import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from product_lab import (
    ProductDocument,
    compare_schemas,
    evaluate_budget,
    evaluate_snapshot,
    load_spec,
    notify_consumers,
    parse_time,
)

ROOT = Path(__file__).resolve().parents[1]


def test_orders_spec_validates():
    doc = load_spec(ROOT / "specs/orders.yaml")
    assert doc.product.name == "orders"
    assert doc.product.version == "1.2.0"
    assert doc.product.slos.freshness.max_age_minutes == 15


def test_restricted_product_cannot_default_allow():
    raw = json.loads(json.dumps(load_spec(ROOT / "specs/orders.yaml").model_dump()))
    raw["product"]["classification"] = "restricted"
    raw["product"]["access"]["default"] = "allow"
    with pytest.raises(ValidationError):
        ProductDocument.model_validate(raw)


def test_snapshot_freshness_and_completeness():
    spec = load_spec(ROOT / "specs/orders.yaml").product
    snapshot = json.loads((ROOT / "data/orders_snapshot.json").read_text())
    result = evaluate_snapshot(spec, snapshot, parse_time("2026-10-19T09:00:00Z"))
    assert result["latest_event_age_minutes"] == 8.0
    assert result["freshness_sli_pass"] is True
    assert result["completeness_percent"] == 99.7
    assert result["completeness_sli_pass"] is True
    assert result["overall_pass"] is True


def test_stale_snapshot_fails_freshness():
    spec = load_spec(ROOT / "specs/orders.yaml").product
    snapshot = json.loads((ROOT / "data/orders_snapshot.json").read_text())
    result = evaluate_snapshot(spec, snapshot, parse_time("2026-10-19T10:00:00Z"))
    assert result["latest_event_age_minutes"] == 68.0
    assert result["freshness_sli_pass"] is False
    assert result["overall_pass"] is False


def test_error_budget_calculation():
    spec = load_spec(ROOT / "specs/orders.yaml").product
    history = json.loads((ROOT / "data/slo_history.json").read_text())
    result = evaluate_budget(spec, history)
    # 30 days * 24 hourly probes = 720; 1% failure allowance = 7.2 failed probes.
    assert result["expected_probes_per_slo_window"] == 720
    assert result["allowed_failed_probes_per_slo_window"] == 7.2
    assert result["sli_failures_observed"] == 1
    assert result["budget_consumed_percent"] == 13.889
    assert result["error_rate_burn_multiple"] == 10.0


def test_schema_comparison_flags_removed_field():
    result = compare_schemas(ROOT / "data/schema_v1.json", ROOT / "data/schema_v2_breaking.json")
    assert result["breaking"] is True
    assert result["removed_fields"] == ["order_status"]
    assert result["added_fields"] == ["source_system", "status_code"]


def test_notification_is_local_mock(tmp_path):
    result = notify_consumers(
        ROOT / "data/consumer_list.json",
        "Test migration notice",
        tmp_path / "outbox.json",
    )
    assert result["sent"] is False
    assert result["mechanism"] == "local-json-outbox"
    assert len(result["recipients"]) == 3
    assert (tmp_path / "outbox.json").exists()


def test_naive_timestamp_rejected():
    with pytest.raises(ValueError):
        parse_time("2026-10-19T09:00:00")


def test_completeness_error_budget_calculation():
    spec = load_spec(ROOT / "specs/orders.yaml").product
    history = json.loads((ROOT / "data/slo_history.json").read_text())
    result = evaluate_budget(spec, history, "completeness")
    assert result["sli"] == "completeness"
    assert result["sli_failures_observed"] == 0
    assert result["budget_consumed_percent"] == 0.0


def test_future_event_timestamp_fails_freshness():
    spec = load_spec(ROOT / "specs/orders.yaml").product
    snapshot = json.loads((ROOT / "data/orders_snapshot.json").read_text())
    snapshot["latest_event_at"] = "2026-10-19T09:05:00Z"
    result = evaluate_snapshot(spec, snapshot, parse_time("2026-10-19T09:00:00Z"))
    assert result["latest_event_age_minutes"] == -5.0
    assert result["freshness_sli_pass"] is False
