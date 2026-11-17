from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ROOT = Path(__file__).resolve().parent
SCHEMA_VERSION = "3.0"
GENERATOR_VERSION = "0.2.0"
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
ALLOWED_CONNECTORS = {"csv_file", "http_api", "database"}


def _valid_cron_field(field: str, minimum: int, maximum: int) -> bool:
    """Validate a five-field numeric cron component, including lists/ranges/steps."""
    if field == "*":
        return True
    for item in field.split(","):
        if not item:
            return False
        base, slash, step_text = item.partition("/")
        if slash:
            if not step_text.isdigit() or int(step_text) < 1:
                return False
        if base == "*":
            continue
        if "-" in base:
            parts = base.split("-")
            if len(parts) != 2 or not all(p.isdigit() for p in parts):
                return False
            start, end = map(int, parts)
            if start < minimum or end > maximum or start > end:
                return False
        else:
            if not base.isdigit() or not minimum <= int(base) <= maximum:
                return False
    return True


def validate_cron(value: str) -> str:
    fields = value.split()
    ranges = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 7)]
    if len(fields) != 5:
        raise ValueError("schedule must contain five cron fields")
    for field, (minimum, maximum) in zip(fields, ranges):
        if not _valid_cron_field(field, minimum, maximum):
            raise ValueError(f"invalid cron field {field!r}; expected values in {minimum}..{maximum}")
    return value


class SourceSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    system: str = Field(min_length=2, pattern=r"^[a-z][a-z0-9_-]*$")
    object: str = Field(min_length=1, pattern=r"^[a-zA-Z][a-zA-Z0-9_]*$")
    connector: Literal["csv_file", "http_api", "database"]
    connection_ref: str = Field(min_length=3, pattern=r"^[A-Za-z0-9_.:-]+$")
    extraction_mode: Literal["full", "incremental", "cdc"]
    keys: list[str] = Field(min_length=1)
    columns: list[str] = Field(min_length=1)
    dbt_schema: str = Field(min_length=1, pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    watermark: str | None = None
    cdc_cursor: str | None = None

    @field_validator("keys", "columns")
    @classmethod
    def valid_unique_identifiers(cls, values: list[str]) -> list[str]:
        if any(not isinstance(v, str) or not IDENTIFIER_RE.fullmatch(v) for v in values):
            raise ValueError("keys/columns must contain safe SQL identifiers")
        if len(values) != len(set(values)):
            raise ValueError("source keys/columns must not contain duplicates")
        return values

    @field_validator("watermark", "cdc_cursor")
    @classmethod
    def validate_cursor_name(cls, value: str | None) -> str | None:
        if value is not None and not IDENTIFIER_RE.fullmatch(value):
            raise ValueError("watermark/cdc_cursor must be a safe identifier")
        return value

    @model_validator(mode="after")
    def validate_extraction_cursor(self):
        if not set(self.keys).issubset(self.columns):
            raise ValueError("every source key must appear in source.columns")
        if self.extraction_mode == "incremental":
            if not self.watermark:
                raise ValueError("incremental extraction requires source.watermark")
            if self.watermark not in self.columns:
                raise ValueError("incremental watermark must appear in source.columns")
            if self.cdc_cursor:
                raise ValueError("incremental extraction must not define source.cdc_cursor")
        elif self.extraction_mode == "cdc":
            if not self.cdc_cursor:
                raise ValueError("CDC extraction requires source.cdc_cursor (for example an LSN/offset field)")
            if self.watermark:
                raise ValueError("CDC uses a log cursor, not a column watermark; omit source.watermark")
        else:
            if self.watermark or self.cdc_cursor:
                raise ValueError("full extraction must not define a watermark or CDC cursor")
        return self


class TargetSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    layer: Literal["bronze", "silver", "gold"]
    dataset: str = Field(pattern=r"^[a-z][a-z0-9_]*$")


class QualityCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["not_null", "unique", "accepted_values"]
    column: str = Field(min_length=1, pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    values: list[str] | None = None

    @model_validator(mode="after")
    def values_match_check_type(self):
        if self.type == "accepted_values" and not self.values:
            raise ValueError("accepted_values check requires a non-empty values list")
        if self.type != "accepted_values" and self.values is not None:
            raise ValueError("values is only valid for accepted_values")
        if self.values is not None and len(self.values) != len(set(self.values)):
            raise ValueError("accepted_values must not contain duplicates")
        return self


class PipelineSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["3.0"]
    pipeline_id: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    description: str = Field(min_length=10)
    source: SourceSpec
    target: TargetSpec
    quality_checks: list[QualityCheck] = Field(min_length=1)
    schedule: str
    owner: str
    classification: Literal["public", "internal", "confidential", "restricted"]
    retention_days: int = Field(gt=0, le=36500)
    tags: list[str] = Field(default_factory=list)
    custom_logic: Literal["normalize_phone_v1", "custom_api_pagination_v1"] | None = None

    @field_validator("schedule")
    @classmethod
    def cron_shape(cls, value: str) -> str:
        return validate_cron(value)

    @field_validator("owner")
    @classmethod
    def owner_must_be_email(cls, value: str) -> str:
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            raise ValueError("owner must be an email address")
        return value

    @field_validator("tags")
    @classmethod
    def tags_must_be_unique(cls, values: list[str]) -> list[str]:
        if any(not tag.strip() for tag in values):
            raise ValueError("tags must not contain blank values")
        if len(values) != len(set(values)):
            raise ValueError("tags must not contain duplicates")
        return values

    @model_validator(mode="after")
    def validate_pipeline_semantics(self):
        if self.source.connector not in ALLOWED_CONNECTORS:
            raise ValueError("unsupported connector")
        columns = set(self.source.columns)
        unknown_check_columns = {check.column for check in self.quality_checks} - columns
        if unknown_check_columns:
            raise ValueError(f"quality checks reference unknown source columns: {sorted(unknown_check_columns)}")
        if self.classification in {"confidential", "restricted"}:
            checked_keys = {q.column for q in self.quality_checks if q.type == "not_null"}
            missing_key_checks = set(self.source.keys) - checked_keys
            if missing_key_checks:
                raise ValueError(
                    "confidential/restricted pipelines require not_null checks for every key; "
                    f"missing: {sorted(missing_key_checks)}"
                )
        return self


def load_spec(path: Path) -> PipelineSpec:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: YAML root must be a mapping")
    return PipelineSpec.model_validate(raw)


def load_all_specs(config_dir: Path | None = None) -> list[PipelineSpec]:
    config_dir = config_dir or ROOT / "configs"
    specs = [load_spec(path) for path in sorted(config_dir.glob("*.yaml"))]
    if not specs:
        raise ValueError(f"no YAML pipeline definitions found in {config_dir}")
    ids = [spec.pipeline_id for spec in specs]
    if len(ids) != len(set(ids)):
        raise ValueError("pipeline_id values must be unique across the config directory")
    targets = [(spec.target.layer, spec.target.dataset) for spec in specs]
    if len(targets) != len(set(targets)):
        raise ValueError("target layer/dataset pairs must be unique across the config directory")
    return specs


def spec_digest(spec: PipelineSpec) -> str:
    payload = json.dumps(spec.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def governance_policy(spec: PipelineSpec) -> dict:
    masking = {
        "public": {"mask_pii": False, "policy": "no_default_masking"},
        "internal": {"mask_pii": False, "policy": "internal_access_controls"},
        "confidential": {"mask_pii": True, "policy": "mask_email_phone_in_nonprod"},
        "restricted": {"mask_pii": True, "policy": "mask_all_direct_identifiers_nonprod"},
    }[spec.classification]
    return {
        "pipeline_id": spec.pipeline_id,
        "classification": spec.classification,
        "masking": masking,
        "retention": {
            "days": spec.retention_days,
            "action": "expire_or_delete_after_retention",
            "enforcement_status": "policy_artifact_only",
        },
        "owner": spec.owner,
        "owner_notifications": {"on_failure": True, "on_quality_failure": True, "recipient": spec.owner},
        "access_review_required": spec.classification in {"confidential", "restricted"},
        "enforcement_status": "policy_artifact_only",
    }


def generate_plan(spec: PipelineSpec) -> dict:
    return {
        "pipeline_id": spec.pipeline_id,
        "schema_version": spec.schema_version,
        "generator_version": GENERATOR_VERSION,
        "config_digest": spec_digest(spec),
        "source": spec.source.model_dump(mode="json"),
        "target": spec.target.model_dump(mode="json"),
        "schedule": spec.schedule,
        "owner": spec.owner,
        "quality_checks": [check.model_dump(mode="json") for check in spec.quality_checks],
        "governance": governance_policy(spec),
        "execution": {
            "mode": "local_simulation",
            "checkpoint_key": f"{spec.pipeline_id}:watermark" if spec.source.watermark else (
                f"{spec.pipeline_id}:cdc_cursor" if spec.source.cdc_cursor else None
            ),
            "retry_policy": {"max_attempts": 3, "backoff": "exponential"},
            "idempotency_key": "pipeline_id + source_window + config_digest",
            "custom_logic_requested": spec.custom_logic,
            "custom_logic_executed": False,
        },
    }


def render_dbt_model(spec: PipelineSpec, columns: list[str] | None = None, template_dir: Path | None = None) -> str:
    selected_columns = columns if columns is not None else spec.source.columns
    if not selected_columns:
        raise ValueError("columns must be supplied from trusted metadata or schema discovery")
    if any(not IDENTIFIER_RE.fullmatch(column) for column in selected_columns):
        raise ValueError("unsafe column identifier in source.columns")
    if len(selected_columns) != len(set(selected_columns)):
        raise ValueError("dbt model columns must be unique")
    env = Environment(
        loader=FileSystemLoader(str(template_dir or ROOT / "templates")),
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=False,
        lstrip_blocks=False,
    )
    template = env.get_template("staging_model.sql.j2")
    source_call = f"{{{{ source('{spec.source.system}', '{spec.source.object}') }}}}"
    dbt_config_line = "{{ config(materialized='view', tags=" + repr(spec.tags) + ") }}"
    return template.render(
        pipeline=spec,
        columns=selected_columns,
        source_call=source_call,
        dbt_config_line=dbt_config_line,
    )


def generate_dbt_sources(specs: list[PipelineSpec]) -> str:
    """Generate dbt source declarations matching each generated source() call."""
    grouped: dict[str, dict[str, object]] = {}
    for spec in specs:
        source_name = spec.source.system
        entry = grouped.setdefault(source_name, {"name": source_name, "schema": spec.source.dbt_schema, "tables": []})
        if entry["schema"] != spec.source.dbt_schema:
            raise ValueError(f"source system {source_name!r} maps to multiple dbt schemas")
        tables = entry["tables"]
        assert isinstance(tables, list)
        if not any(table["name"] == spec.source.object for table in tables):
            tables.append({"name": spec.source.object, "description": f"Landing relation for {spec.pipeline_id}"})
    payload = {"version": 2, "sources": list(grouped.values())}
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)


def migrate_v1_to_v3(raw: dict) -> dict:
    """Migrate the documented flat v1 format; legacy column metadata needs review."""
    if not isinstance(raw, dict):
        raise ValueError("v1 config must be a mapping")
    if raw.get("schema_version") != "1.0":
        raise ValueError("migrate_v1_to_v3 expects schema_version '1.0'")
    allowed = {
        "schema_version", "pipeline_id", "source_system", "source_object", "connector", "connection_ref",
        "mode", "primary_key", "watermark_column", "target_layer", "target_dataset", "owner",
        "classification", "retention_days", "schedule", "columns", "dbt_schema",
    }
    unknown = set(raw) - allowed
    if unknown:
        raise ValueError(f"unknown v1 fields: {sorted(unknown)}")
    required = allowed - {"watermark_column", "columns", "dbt_schema"}
    missing = required - set(raw)
    if missing:
        raise ValueError(f"v1 config missing required fields: {sorted(missing)}")
    mode = raw["mode"]
    watermark = raw.get("watermark_column")
    if mode == "cdc":
        raise ValueError("CDC migration requires manual mapping from source log position to source.cdc_cursor")
    if mode not in {"full", "incremental"}:
        raise ValueError(f"unsupported v1 extraction mode: {mode!r}")
    if mode == "incremental" and not watermark:
        raise ValueError("v1 incremental config requires watermark_column")
    if mode == "full" and watermark:
        raise ValueError("v1 full mode cannot carry watermark_column")
    primary_key = raw["primary_key"]
    columns = raw.get("columns") or list(dict.fromkeys([primary_key] + ([watermark] if watermark else [])))
    migrated = {
        "schema_version": SCHEMA_VERSION,
        "pipeline_id": raw["pipeline_id"],
        "description": f"Migrated from schema 1.0: {raw['pipeline_id']}",
        "source": {
            "system": raw["source_system"],
            "object": raw["source_object"],
            "connector": raw["connector"],
            "connection_ref": raw["connection_ref"],
            "extraction_mode": mode,
            "keys": [primary_key],
            "columns": columns,
            "dbt_schema": raw.get("dbt_schema", raw["source_system"]),
            "watermark": watermark,
            "cdc_cursor": None,
        },
        "target": {"layer": raw["target_layer"], "dataset": raw["target_dataset"]},
        "quality_checks": [
            {"type": "not_null", "column": primary_key},
            {"type": "unique", "column": primary_key},
        ],
        "schedule": raw["schedule"],
        "owner": raw["owner"],
        "classification": raw["classification"],
        "retention_days": raw["retention_days"],
        "tags": ["migrated"],
        "custom_logic": None,
    }
    # Fail during migration rather than returning a malformed configuration.
    PipelineSpec.model_validate(migrated)
    return migrated



def migrate_v2_to_v3(raw: dict) -> dict:
    """Migrate a draft v2 config by adding explicit column and dbt-schema metadata."""
    if not isinstance(raw, dict):
        raise ValueError("v2 config must be a mapping")
    if raw.get("schema_version") != "2.0":
        raise ValueError("migrate_v2_to_v3 expects schema_version '2.0'")
    allowed = {
        "schema_version", "pipeline_id", "description", "source", "target", "quality_checks",
        "schedule", "owner", "classification", "retention_days", "tags", "custom_logic",
    }
    unknown = set(raw) - allowed
    if unknown:
        raise ValueError(f"unknown v2 fields: {sorted(unknown)}")
    required = allowed - {"tags", "custom_logic"}
    missing = required - set(raw)
    if missing:
        raise ValueError(f"v2 config missing required fields: {sorted(missing)}")
    source = raw["source"]
    if not isinstance(source, dict):
        raise ValueError("v2 source must be a mapping")
    mode = source.get("extraction_mode")
    if mode == "cdc" and source.get("watermark") and not source.get("cdc_cursor"):
        raise ValueError("v2 CDC migration requires manual mapping from watermark to source.cdc_cursor")
    keys = source.get("keys") or []
    checks = raw.get("quality_checks") or []
    inferred = list(dict.fromkeys(
        list(keys)
        + [check["column"] for check in checks if isinstance(check, dict) and isinstance(check.get("column"), str)]
        + ([source["watermark"]] if source.get("watermark") else [])
    ))
    migrated = dict(raw)
    migrated["schema_version"] = SCHEMA_VERSION
    migrated_source = dict(source)
    migrated_source.setdefault("columns", inferred)
    migrated_source.setdefault("dbt_schema", source.get("system", ""))
    migrated_source.setdefault("cdc_cursor", None)
    migrated["source"] = migrated_source
    PipelineSpec.model_validate(migrated)
    return migrated


def make_openlineage_event(
    spec: PipelineSpec, run_id: str, state: str, started_at: str, ended_at: str | None = None
) -> dict:
    """Create a local OpenLineage-shaped event; no event is sent to a backend."""
    allowed_states = {"START", "RUNNING", "COMPLETE", "ABORT", "FAIL", "OTHER"}
    normalized_state = state.upper()
    event_type = "OTHER" if normalized_state == "SIMULATED" else normalized_state
    if event_type not in allowed_states:
        raise ValueError(f"unsupported OpenLineage event state: {state!r}")
    if not run_id.strip():
        raise ValueError("run_id must not be blank")
    event = {
        "eventType": event_type,
        "eventTime": ended_at or started_at,
        "run": {"runId": run_id},
        "job": {
            "namespace": "urn:metadata-platform-lab:job",
            "name": spec.pipeline_id,
            "facets": {"documentation": {"description": "Local simulation only; no data-plane execution occurred."}},
        },
        "inputs": [{"namespace": f"urn:metadata-platform-lab:source:{spec.source.system}", "name": spec.source.object}],
        "outputs": [{"namespace": f"urn:metadata-platform-lab:target:{spec.target.layer}", "name": spec.target.dataset}],
        "producer": "https://example.invalid/metadata-platform-lab",
        "schemaURL": "https://openlineage.io/spec/2-0-2/OpenLineage.json",
    }
    return event


def execute_simulation(spec: PipelineSpec, run_id: str, history_path: Path | None = None) -> dict:
    """Record a local plan simulation, not a successful ingestion run."""
    if not run_id.strip():
        raise ValueError("run_id must not be blank")
    history_path = history_path or ROOT / "reports/run_history.jsonl"
    now = datetime.now(timezone.utc).isoformat()
    status = "SIMULATED"
    error = None
    try:
        plan = generate_plan(spec)
        if not plan["target"]["dataset"]:
            raise RuntimeError("target dataset missing")
    except Exception as exc:
        status, error = "SIMULATION_FAILED", str(exc)
    row = {
        "run_id": run_id,
        "pipeline_id": spec.pipeline_id,
        "status": status,
        "execution_mode": "local_simulation",
        "started_at": now,
        "ended_at": datetime.now(timezone.utc).isoformat(),
        "config_digest": spec_digest(spec),
        "generator_version": GENERATOR_VERSION,
        "error": error,
        "checkpoint": {
            "key": f"{spec.pipeline_id}:watermark" if spec.source.watermark else f"{spec.pipeline_id}:cdc_cursor",
            "value": None,
            "advanced": False,
        } if (spec.source.watermark or spec.source.cdc_cursor) else None,
    }
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with history_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(row) + "\n")
    return row


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_generated(config_dir: Path | None = None, output_dir: Path | None = None) -> list[dict]:
    config_dir = config_dir or ROOT / "configs"
    output_dir = output_dir or ROOT / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    specs = load_all_specs(config_dir)
    plans: list[dict] = []
    generated_paths: list[Path] = []
    for spec in specs:
        plan = generate_plan(spec)
        plans.append(plan)
        plan_path = output_dir / f"{spec.pipeline_id}.plan.json"
        plan_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        generated_paths.append(plan_path)
        sql_path = output_dir / f"stg_{spec.target.dataset}.sql"
        sql_path.write_text(render_dbt_model(spec), encoding="utf-8")
        generated_paths.append(sql_path)

    sources_path = output_dir / "sources.yml"
    sources_path.write_text(generate_dbt_sources(specs), encoding="utf-8")
    generated_paths.append(sources_path)
    policy_path = output_dir / "governance_policies.json"
    policy_path.write_text(json.dumps([governance_policy(spec) for spec in specs], indent=2) + "\n", encoding="utf-8")
    generated_paths.append(policy_path)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "artifacts": {path.name: _sha256_file(path) for path in sorted(generated_paths)},
    }
    manifest_path = output_dir / "generated_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return plans
