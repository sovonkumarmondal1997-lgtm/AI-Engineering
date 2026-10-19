from __future__ import annotations
import json, re, hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).resolve().parent
SCHEMA_VERSION = "2.0"
CLASSIFICATION_RANK = {"public": 0, "internal": 1, "confidential": 2, "restricted": 3}
ALLOWED_CONNECTORS = {"csv_file", "http_api", "database"}

class SourceSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    system: str = Field(min_length=2, pattern=r"^[a-z][a-z0-9_-]*$")
    object: str = Field(min_length=1, pattern=r"^[a-zA-Z][a-zA-Z0-9_]*$")
    connector: Literal["csv_file", "http_api", "database"]
    connection_ref: str = Field(min_length=3)
    extraction_mode: Literal["full", "incremental", "cdc"]
    keys: list[str] = Field(min_length=1)
    watermark: str | None = None

    @field_validator("keys")
    @classmethod
    def keys_are_unique(cls, v):
        if len(v) != len(set(v)):
            raise ValueError("source.keys must not contain duplicates")
        return v

    @model_validator(mode="after")
    def incremental_requires_watermark(self):
        if self.extraction_mode in {"incremental", "cdc"} and not self.watermark:
            raise ValueError("incremental/cdc extraction requires source.watermark")
        if self.extraction_mode == "full" and self.watermark:
            raise ValueError("full extraction must not define a watermark")
        return self

class TargetSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    layer: Literal["bronze", "silver", "gold"]
    dataset: str = Field(pattern=r"^[a-z][a-z0-9_]*$")

class QualityCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["not_null", "unique", "accepted_values"]
    column: str = Field(min_length=1)
    values: list[str] | None = None

    @model_validator(mode="after")
    def values_match_check_type(self):
        if self.type == "accepted_values" and not self.values:
            raise ValueError("accepted_values check requires a non-empty values list")
        if self.type != "accepted_values" and self.values is not None:
            raise ValueError("values is only valid for accepted_values")
        return self

class PipelineSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["2.0"]
    pipeline_id: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    description: str = Field(min_length=10)
    source: SourceSpec
    target: TargetSpec
    quality_checks: list[QualityCheck] = Field(min_length=1)
    schedule: str = Field(min_length=9)
    owner: str
    classification: Literal["public", "internal", "confidential", "restricted"]
    retention_days: int = Field(gt=0, le=36500)
    tags: list[str] = []
    custom_logic: Literal["normalize_phone_v1", "custom_api_pagination_v1"] | None = None

    @field_validator("schedule")
    @classmethod
    def cron_shape(cls, v):
        # Educational structural check only, not a complete cron parser.
        if len(v.split()) != 5:
            raise ValueError("schedule must contain five cron fields")
        if any(not re.fullmatch(r"[0-9*/?,\\-]+", part) for part in v.split()):
            raise ValueError("schedule contains unsupported cron characters")
        return v

    @field_validator("owner")
    @classmethod
    def owner_must_be_email(cls, v):
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", v):
            raise ValueError("owner must be an email address")
        return v

    @model_validator(mode="after")
    def validate_pipeline_semantics(self):
        if self.source.connector not in ALLOWED_CONNECTORS:
            raise ValueError("unsupported connector")
        if self.source.watermark and self.source.watermark in self.source.keys:
            raise ValueError("watermark must not also be a primary key")
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
    specs = [load_spec(p) for p in sorted(config_dir.glob("*.yaml"))]
    ids = [s.pipeline_id for s in specs]
    if len(ids) != len(set(ids)):
        raise ValueError("pipeline_id values must be unique across the config directory")
    targets = [s.target.dataset for s in specs]
    if len(targets) != len(set(targets)):
        raise ValueError("target.dataset values must be unique across the config directory")
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
        "retention": {"days": spec.retention_days, "action": "expire_or_delete_after_retention"},
        "owner": spec.owner,
        "access_review_required": spec.classification in {"confidential", "restricted"},
    }

def generate_plan(spec: PipelineSpec) -> dict:
    return {
        "pipeline_id": spec.pipeline_id,
        "schema_version": spec.schema_version,
        "config_digest": spec_digest(spec),
        "source": spec.source.model_dump(mode="json"),
        "target": spec.target.model_dump(mode="json"),
        "schedule": spec.schedule,
        "owner": spec.owner,
        "quality_checks": [q.model_dump(mode="json") for q in spec.quality_checks],
        "governance": governance_policy(spec),
        "execution": {
            "mode": "local_simulation",
            "checkpoint_key": f"{spec.pipeline_id}:watermark" if spec.source.watermark else None,
            "retry_policy": {"max_attempts": 3, "backoff": "exponential"},
            "idempotency_key": "pipeline_id + source_window + config_digest",
            "custom_logic": spec.custom_logic,
        },
    }

def render_dbt_model(spec: PipelineSpec, columns: list[str], template_dir: Path | None = None) -> str:
    if not columns:
        raise ValueError("columns must be supplied from a trusted schema or discovery step")
    for col in columns:
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", col):
            raise ValueError(f"unsafe column identifier: {col}")
    env = Environment(
        loader=FileSystemLoader(str(template_dir or ROOT / "templates")),
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=False,
        lstrip_blocks=False,
    )
    # Use a Python renderer for source/target names and only permit validated identifiers.
    # The emitted file is an educational dbt model template; it is not run against a warehouse here.
    template = env.get_template("staging_model.sql.j2")
    # Values intentionally contain dbt Jinja expressions. Jinja renders them as text once;
    # dbt later evaluates those expressions when compiling the generated model.
    source_call = f"{{{{ source('{spec.source.system}', '{spec.source.object}') }}}}"
    dbt_config_line = "{{ config(materialized='view', tags=" + repr(spec.tags) + ") }}"
    return template.render(
        pipeline=spec,
        columns=columns,
        source_call=source_call,
        dbt_config_line=dbt_config_line,
    )


def migrate_v1_to_v2(raw: dict) -> dict:
    """Explicit migration for the documented v1 shape; unknown keys are rejected."""
    if raw.get("schema_version") != "1.0":
        raise ValueError("migrate_v1_to_v2 expects schema_version '1.0'")
    allowed = {
        "schema_version","pipeline_id","source_system","source_object","connector","connection_ref",
        "mode","primary_key","watermark_column","target_layer","target_dataset","owner",
        "classification","retention_days","schedule"
    }
    unknown = set(raw) - allowed
    if unknown:
        raise ValueError(f"unknown v1 fields: {sorted(unknown)}")
    mode = raw["mode"]
    watermark = raw.get("watermark_column")
    if mode in {"incremental","cdc"} and not watermark:
        raise ValueError("v1 incremental/cdc config requires watermark_column")
    if mode == "full" and watermark:
        raise ValueError("v1 full mode cannot carry watermark_column")
    return {
        "schema_version": "2.0",
        "pipeline_id": raw["pipeline_id"],
        "description": f"Migrated from schema 1.0: {raw['pipeline_id']}",
        "source": {
            "system": raw["source_system"],
            "object": raw["source_object"],
            "connector": raw["connector"],
            "connection_ref": raw["connection_ref"],
            "extraction_mode": mode,
            "keys": [raw["primary_key"]],
            "watermark": watermark,
        },
        "target": {"layer": raw["target_layer"], "dataset": raw["target_dataset"]},
        "quality_checks": [
            {"type": "not_null", "column": raw["primary_key"]},
            {"type": "unique", "column": raw["primary_key"]},
        ],
        "schedule": raw["schedule"],
        "owner": raw["owner"],
        "classification": raw["classification"],
        "retention_days": raw["retention_days"],
        "tags": ["migrated"],
        "custom_logic": None,
    }

def make_openlineage_event(spec: PipelineSpec, run_id: str, state: str, started_at: str, ended_at: str | None = None) -> dict:
    """Create an OpenLineage-shaped event payload locally; no event is sent to a backend."""
    event = {
        "eventType": state.upper(),
        "eventTime": ended_at or started_at,
        "run": {"runId": run_id},
        "job": {"namespace": "metadata-platform-lab", "name": spec.pipeline_id},
        "inputs": [{"namespace": spec.source.system, "name": spec.source.object}],
        "outputs": [{"namespace": spec.target.layer, "name": spec.target.dataset}],
        "producer": "https://example.invalid/metadata-platform-lab",
        "schemaURL": "https://openlineage.io/spec/2-0-2/OpenLineage.json",
    }
    return event

def execute_simulation(spec: PipelineSpec, run_id: str, history_path: Path | None = None) -> dict:
    """Simulate a run and append operational history; does not connect to a real source."""
    history_path = history_path or ROOT / "reports/run_history.jsonl"
    now = datetime.now(timezone.utc).isoformat()
    status = "COMPLETE"
    error = None
    try:
        plan = generate_plan(spec)
        # The sample runtime checks configuration and records an execution plan only.
        if not plan["target"]["dataset"]:
            raise RuntimeError("target dataset missing")
    except Exception as exc:
        status, error = "FAIL", str(exc)
    row = {
        "run_id": run_id, "pipeline_id": spec.pipeline_id, "status": status,
        "started_at": now, "ended_at": datetime.now(timezone.utc).isoformat(),
        "config_digest": spec_digest(spec), "error": error,
        "checkpoint": {"key": f"{spec.pipeline_id}:watermark", "value": None} if spec.source.watermark else None,
    }
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with history_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    return row

def write_generated(config_dir: Path | None = None, output_dir: Path | None = None) -> list[dict]:
    config_dir = config_dir or ROOT / "configs"
    output_dir = output_dir or ROOT / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    plans = []
    for spec in load_all_specs(config_dir):
        plan = generate_plan(spec)
        plans.append(plan)
        (output_dir / f"{spec.pipeline_id}.plan.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        # Fixture schema for the demo. Real platforms discover schema from a source/catalogue.
        columns_by_object = {
            "customers": ["customer_id", "email", "full_name", "updated_at"],
            "orders": ["order_id", "customer_id", "amount", "status"],
            "product_catalog": ["sku", "name", "category", "modified_at"],
        }
        sql = render_dbt_model(spec, columns_by_object[spec.source.object])
        (output_dir / f"stg_{spec.target.dataset}.sql").write_text(sql, encoding="utf-8")
    (output_dir / "governance_policies.json").write_text(
        json.dumps([governance_policy(s) for s in load_all_specs(config_dir)], indent=2) + "\n",
        encoding="utf-8",
    )
    return plans
