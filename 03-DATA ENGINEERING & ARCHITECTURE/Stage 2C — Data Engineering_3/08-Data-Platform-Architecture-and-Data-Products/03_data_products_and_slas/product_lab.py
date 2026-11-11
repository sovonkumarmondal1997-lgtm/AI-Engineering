from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator


ROOT = Path(__file__).resolve().parent


class Owner(BaseModel):
    model_config = ConfigDict(extra="forbid")
    team: str = Field(min_length=1)
    business_owner: str = Field(min_length=1)
    technical_owner: str = Field(min_length=1)
    support_channel: str = Field(min_length=1)
    escalation: str = Field(min_length=1)


class FieldSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1)
    type: Literal["string", "integer", "number", "boolean", "datetime"]
    nullable: bool
    description: str = Field(min_length=1)
    key: str | None = None


class OutputPort(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["table", "file", "api", "stream", "metric_endpoint"]
    address: str = Field(min_length=1)
    format: str = Field(min_length=1)


class Lineage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sources: list[str] = Field(min_length=1)
    transformation: str = Field(min_length=1)


class AccessRole(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1)
    permissions: list[str] = Field(min_length=1)


class Access(BaseModel):
    model_config = ConfigDict(extra="forbid")
    default: Literal["deny", "allow"]
    roles: list[AccessRole] = Field(min_length=1)
    restricted_fields: list[str]


class FreshnessSLO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    max_age_minutes: int = Field(gt=0)
    target_percent: float = Field(gt=0, le=100)
    window_days: int = Field(gt=0)
    probe_interval_minutes: int = Field(gt=0)


class CompletenessSLO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    min_expected_row_ratio_percent: float = Field(gt=0, le=100)
    target_percent: float = Field(gt=0, le=100)
    window_days: int = Field(gt=0)
    probe_interval_minutes: int = Field(gt=0)


class QualityRules(BaseModel):
    model_config = ConfigDict(extra="forbid")
    max_duplicate_order_ids: int = Field(ge=0)
    max_null_order_ids: int = Field(ge=0)


class SLOs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    freshness: FreshnessSLO
    completeness: CompletenessSLO
    quality: QualityRules


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")
    compatibility_policy: str = Field(min_length=1)
    deprecation_notice_days: int = Field(gt=0)
    support_hours: str = Field(min_length=1)


class ChangelogEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: str = Field(min_length=1)
    date: str = Field(min_length=1)
    change: str = Field(min_length=1)


class Documentation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    catalogue_url: str = Field(min_length=1)
    sample_query: str = Field(min_length=1)
    changelog: list[ChangelogEntry]


class Product(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    name: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    lifecycle_status: Literal["draft", "active", "deprecated", "retired"]
    description: str = Field(min_length=1)
    purpose: str = Field(min_length=1)
    non_goals: list[str]
    owner: Owner
    consumers: list[str] = Field(min_length=1)
    output_port: OutputPort
    schema_fields: list[FieldSpec] = Field(alias="schema", min_length=1)
    lineage: Lineage
    classification: Literal["public", "internal", "confidential", "restricted"]
    retention_days: int = Field(gt=0)
    access: Access
    slos: SLOs
    contract: Contract
    documentation: Documentation

    @model_validator(mode="after")
    def unique_fields_and_keys(self):
        names = [field.name for field in self.schema_fields]
        if len(names) != len(set(names)):
            raise ValueError("schema field names must be unique")
        primary_keys = [field.name for field in self.schema_fields if field.key == "primary"]
        if len(primary_keys) > 1:
            raise ValueError("this lab permits at most one primary key")
        if self.access.default == "allow" and self.classification in {"confidential", "restricted"}:
            raise ValueError("confidential/restricted products cannot use default allow access")
        return self


class ProductDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")
    product: Product


def load_spec(path: Path) -> ProductDocument:
    with path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    return ProductDocument.model_validate(raw)


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"timestamp must include a timezone: {value}")
    return parsed.astimezone(timezone.utc)


def evaluate_snapshot(spec: Product, snapshot: dict, now: datetime) -> dict:
    observed_at = parse_time(snapshot["observed_at"])
    latest_event_at = parse_time(snapshot["latest_event_at"])
    age_minutes = (now - latest_event_at).total_seconds() / 60
    # A future event timestamp is not treated as fresh; it may indicate clock skew or bad source data.
    freshness_ok = 0 <= age_minutes <= spec.slos.freshness.max_age_minutes
    expected = int(snapshot["expected_rows"])
    actual = int(snapshot["actual_rows"])
    if expected <= 0:
        raise ValueError("expected_rows must be positive")
    ratio = actual / expected * 100
    completeness_ok = ratio >= spec.slos.completeness.min_expected_row_ratio_percent
    quality_ok = (
        int(snapshot["duplicate_order_ids"]) <= spec.slos.quality.max_duplicate_order_ids
        and int(snapshot["null_order_ids"]) <= spec.slos.quality.max_null_order_ids
        and int(snapshot.get("invalid_rows", 0)) == 0
    )
    return {
        "observed_at": observed_at.isoformat().replace("+00:00", "Z"),
        "latest_event_age_minutes": round(age_minutes, 2),
        "freshness_sli_pass": freshness_ok,
        "expected_rows": expected,
        "actual_rows": actual,
        "completeness_percent": round(ratio, 3),
        "completeness_sli_pass": completeness_ok,
        "quality_sli_pass": quality_ok,
        "overall_pass": freshness_ok and completeness_ok and quality_ok,
    }


def evaluate_budget(spec: Product, history: dict, sli_name: str = "freshness") -> dict:
    if sli_name not in {"freshness", "completeness"}:
        raise ValueError("sli_name must be freshness or completeness")
    probes = history["probes"]
    if not probes:
        raise ValueError("history must contain at least one probe")
    slo = spec.slos.freshness if sli_name == "freshness" else spec.slos.completeness
    target = slo.target_percent / 100
    allowed_fail_fraction = 1 - target
    failures = sum(not bool(p[f"{sli_name}_ok"]) for p in probes)
    total = len(probes)
    observed_fail_fraction = failures / total
    # Budget consumption uses the configured 30-day target window, not just the sample length.
    expected_probes = (
        slo.window_days * 24 * 60 / slo.probe_interval_minutes
    )
    allowed_failed_probes = expected_probes * allowed_fail_fraction
    consumed_fraction = failures / allowed_failed_probes if allowed_failed_probes else (float("inf") if failures else 0.0)
    error_rate_burn_multiple = (observed_fail_fraction / allowed_fail_fraction) if allowed_fail_fraction else (float("inf") if failures else 0.0)
    return {
        "window_start": history["window_start"],
        "window_end": history["window_end"],
        "probes_observed": total,
        "sli_failures_observed": failures,
        "observed_failure_percent": round(observed_fail_fraction * 100, 3),
        "sli": sli_name,
        "target_percent": slo.target_percent,
        "configured_window_days": slo.window_days,
        "configured_probe_interval_minutes": slo.probe_interval_minutes,
        "expected_probes_per_slo_window": int(expected_probes),
        "allowed_failed_probes_per_slo_window": round(allowed_failed_probes, 3),
        "budget_consumed_percent": round(consumed_fraction * 100, 3),
        "error_rate_burn_multiple": round(error_rate_burn_multiple, 3),
        "warning": "This is a simple cumulative budget-consumption ratio, not a time-normalized burn-rate alert."
    }


def notify_consumers(consumer_file: Path, message: str, out_file: Path) -> dict:
    """Write a deterministic local notification outbox; no email is sent."""
    data = json.loads(consumer_file.read_text(encoding="utf-8"))
    payload = {
        "mechanism": "local-json-outbox",
        "sent": False,
        "reason": "simulation only; no SMTP/API configured",
        "message": message,
        "recipients": data["consumers"],
    }
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def compare_schemas(v1_path: Path, v2_path: Path) -> dict:
    v1 = json.loads(v1_path.read_text(encoding="utf-8"))
    v2 = json.loads(v2_path.read_text(encoding="utf-8"))
    old_fields, new_fields = set(v1["fields"]), set(v2["fields"])
    removed = sorted(old_fields - new_fields)
    added = sorted(new_fields - old_fields)
    # This educational comparator treats field removal/rename as breaking.
    breaking = bool(removed)
    return {
        "old_version": v1["version"],
        "new_version": v2["version"],
        "removed_fields": removed,
        "added_fields": added,
        "breaking": breaking,
        "recommended_action": (
            "publish a parallel major version, migrate consumers, then retire old version after notice period"
            if breaking else "review compatibility and publish additive change"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Educational data-product specification and SLO lab")
    parser.add_argument("--spec", type=Path, default=ROOT / "specs/orders.yaml")
    parser.add_argument("--snapshot", type=Path, default=ROOT / "data/orders_snapshot.json")
    parser.add_argument("--history", type=Path, default=ROOT / "data/slo_history.json")
    parser.add_argument("--now", default="2026-10-19T09:00:00Z", help="UTC/offset-aware timestamp for reproducible evaluation")
    parser.add_argument("--out", type=Path, default=ROOT / "reports")
    args = parser.parse_args()

    try:
        doc = load_spec(args.spec)
    except (ValidationError, yaml.YAMLError, OSError, ValueError) as exc:
        print(f"SPEC_INVALID: {exc}")
        return 2

    now = parse_time(args.now)
    snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
    history = json.loads(args.history.read_text(encoding="utf-8"))
    current = evaluate_snapshot(doc.product, snapshot, now)
    freshness_budget = evaluate_budget(doc.product, history, "freshness")
    completeness_budget = evaluate_budget(doc.product, history, "completeness")
    schema_change = compare_schemas(ROOT / "data/schema_v1.json", ROOT / "data/schema_v2_breaking.json")
    notification = notify_consumers(
        ROOT / "data/consumer_list.json",
        "orders v2.0.0 is planned as a breaking release; migrate by 2027-01-17. See migration guide in the product documentation.",
        args.out / "notification_outbox.json",
    )

    report = {
        "product": doc.product.name,
        "version": doc.product.version,
        "spec_validation": "passed",
        "snapshot_evaluation": current,
        "freshness_error_budget": freshness_budget,
        "completeness_error_budget": completeness_budget,
        "schema_change": schema_change,
        "consumer_notification": {
            "mechanism": notification["mechanism"],
            "sent": notification["sent"],
            "recipient_count": len(notification["recipients"]),
            "outbox_file": str(args.out / "notification_outbox.json"),
        },
        "catalogue_registration": {
            "status": "not_attempted",
            "reason": "No live DataHub/OpenMetadata server or credentials configured; local spec/catalogue metadata only."
        },
    }
    args.out.mkdir(parents=True, exist_ok=True)
    report_path = args.out / "slo_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"\nREPORT_WRITTEN: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
