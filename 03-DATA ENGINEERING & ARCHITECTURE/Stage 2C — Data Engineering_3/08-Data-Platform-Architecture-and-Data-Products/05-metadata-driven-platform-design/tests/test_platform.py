import json
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from metadata_platform import (
    GENERATOR_VERSION,
    ROOT,
    PipelineSpec,
    execute_simulation,
    generate_dbt_sources,
    generate_plan,
    governance_policy,
    load_all_specs,
    migrate_v1_to_v3,
    migrate_v2_to_v3,
    render_dbt_model,
    spec_digest,
    write_generated,
)


def test_three_configs_validate_and_have_unique_targets():
    specs = load_all_specs()
    assert len(specs) == 3
    assert len({spec.pipeline_id for spec in specs}) == 3
    assert len({(spec.target.layer, spec.target.dataset) for spec in specs}) == 3


def test_incremental_requires_watermark_and_column():
    raw = yaml.safe_load((ROOT / "configs/customers.yaml").read_text())
    raw["source"]["watermark"] = None
    with pytest.raises(ValidationError, match="requires source.watermark"):
        PipelineSpec.model_validate(raw)
    raw = yaml.safe_load((ROOT / "configs/customers.yaml").read_text())
    raw["source"]["watermark"] = "not_a_column"
    with pytest.raises(ValidationError, match="must appear in source.columns"):
        PipelineSpec.model_validate(raw)


def test_full_mode_rejects_watermark():
    raw = yaml.safe_load((ROOT / "configs/orders.yaml").read_text())
    raw["source"]["watermark"] = "updated_at"
    with pytest.raises(ValidationError, match="full extraction"):
        PipelineSpec.model_validate(raw)


def test_cdc_uses_log_cursor_not_column_watermark():
    raw = yaml.safe_load((ROOT / "configs/orders.yaml").read_text())
    raw["source"]["extraction_mode"] = "cdc"
    raw["source"]["cdc_cursor"] = None
    with pytest.raises(ValidationError, match="requires source.cdc_cursor"):
        PipelineSpec.model_validate(raw)
    raw["source"]["cdc_cursor"] = "lsn"
    raw["source"]["watermark"] = None
    spec = PipelineSpec.model_validate(raw)
    assert spec.source.cdc_cursor == "lsn"


def test_unknown_fields_fail_closed():
    raw = yaml.safe_load((ROOT / "configs/orders.yaml").read_text())
    raw["dangerous_unreviewed_option"] = True
    with pytest.raises(ValidationError, match="Extra inputs"):
        PipelineSpec.model_validate(raw)


def test_sensitive_classification_requires_not_null_for_every_key():
    raw = yaml.safe_load((ROOT / "configs/customers.yaml").read_text())
    raw["source"]["keys"] = ["customer_id", "tenant_id"]
    raw["source"]["columns"].append("tenant_id")
    with pytest.raises(ValidationError, match="tenant_id"):
        PipelineSpec.model_validate(raw)


def test_quality_check_columns_must_exist():
    raw = yaml.safe_load((ROOT / "configs/orders.yaml").read_text())
    raw["quality_checks"][0]["column"] = "missing_column"
    with pytest.raises(ValidationError, match="unknown source columns"):
        PipelineSpec.model_validate(raw)


def test_invalid_cron_ranges_fail():
    raw = yaml.safe_load((ROOT / "configs/orders.yaml").read_text())
    raw["schedule"] = "99 * * * *"
    with pytest.raises(ValidationError, match="invalid cron field"):
        PipelineSpec.model_validate(raw)


def test_governance_driven_by_classification_retention_and_owner():
    specs = {spec.pipeline_id: spec for spec in load_all_specs()}
    conf = governance_policy(specs["crm_customers"])
    pub = governance_policy(specs["erp_product_catalog"])
    assert conf["masking"]["mask_pii"] is True
    assert conf["retention"]["days"] == 365
    assert conf["owner_notifications"]["recipient"] == "crm-data@example.com"
    assert conf["retention"]["enforcement_status"] == "policy_artifact_only"
    assert pub["masking"]["mask_pii"] is False
    assert pub["retention"]["days"] == 1825


def test_generator_outputs_match_fixture_contract_and_include_sources(tmp_path):
    plans = write_generated(output_dir=tmp_path)
    assert len(plans) == 3
    plan = json.loads((tmp_path / "crm_customers.plan.json").read_text())
    sql = (tmp_path / "stg_crm_customers.sql").read_text()
    assert plan["pipeline_id"] == "crm_customers"
    assert plan["generator_version"] == GENERATOR_VERSION
    assert plan["execution"]["checkpoint_key"] == "crm_customers:watermark"
    expected = json.loads((ROOT / "fixtures/expected_crm_plan_contract.json").read_text())
    actual = {
        "pipeline_id": plan["pipeline_id"], "schema_version": plan["schema_version"],
        "target": plan["target"], "schedule": plan["schedule"],
        "classification": plan["governance"]["classification"],
        "mask_pii": plan["governance"]["masking"]["mask_pii"],
        "retention_days": plan["governance"]["retention"]["days"],
        "checkpoint_key": plan["execution"]["checkpoint_key"],
    }
    assert actual == expected
    assert "source('crm', 'customers')" in sql
    assert "customer_id" in sql
    sources = yaml.safe_load((tmp_path / "sources.yml").read_text())
    assert sources["version"] == 2
    assert {source["name"] for source in sources["sources"]} == {"crm", "commerce", "erp"}
    assert (tmp_path / "governance_policies.json").exists()
    manifest = json.loads((tmp_path / "generated_manifest.json").read_text())
    assert manifest["generator_version"] == GENERATOR_VERSION
    assert "sources.yml" in manifest["artifacts"]


def test_generator_supports_new_source_without_hardcoded_column_map(tmp_path):
    raw = yaml.safe_load((ROOT / "configs/customers.yaml").read_text())
    raw["pipeline_id"] = "crm_contacts"
    raw["source"]["object"] = "contacts"
    raw["source"]["columns"] = ["contact_id", "email", "updated_at"]
    raw["source"]["keys"] = ["contact_id"]
    raw["quality_checks"] = [
        {"type": "not_null", "column": "contact_id"},
        {"type": "unique", "column": "contact_id"},
        {"type": "not_null", "column": "updated_at"},
    ]
    raw["target"]["dataset"] = "crm_contacts"
    raw["description"] = "Ingest CRM contact records"
    config_dir = tmp_path / "configs"
    config_dir.mkdir()
    for path in (ROOT / "configs").glob("*.yaml"):
        (config_dir / path.name).write_text(path.read_text())
    (config_dir / "contacts.yaml").write_text(yaml.safe_dump(raw, sort_keys=False))
    output_dir = tmp_path / "out"
    write_generated(config_dir=config_dir, output_dir=output_dir)
    sql = (output_dir / "stg_crm_contacts.sql").read_text()
    assert "contact_id" in sql and "source('crm', 'contacts')" in sql


def test_sql_identifier_injection_rejected():
    spec = load_all_specs()[0]
    with pytest.raises(ValueError, match="unsafe column"):
        render_dbt_model(spec, ["customer_id; drop table users"])


def test_v1_migration_yields_valid_v2_spec():
    raw = yaml.safe_load((ROOT / "fixtures/legacy_customers_v1.yaml").read_text())
    migrated = migrate_v1_to_v3(raw)
    spec = PipelineSpec.model_validate(migrated)
    assert spec.schema_version == "3.0"
    assert spec.source.extraction_mode == "incremental"
    assert spec.source.watermark == "updated_at"
    assert spec.source.columns == ["customer_id", "updated_at"]
    assert {check.type for check in spec.quality_checks} == {"not_null", "unique"}


def test_migration_rejects_invalid_legacy_config_and_missing_fields():
    raw = yaml.safe_load((ROOT / "fixtures/legacy_customers_v1.yaml").read_text())
    raw["watermark_column"] = None
    with pytest.raises(ValueError, match="requires watermark"):
        migrate_v1_to_v3(raw)
    raw = yaml.safe_load((ROOT / "fixtures/legacy_customers_v1.yaml").read_text())
    del raw["primary_key"]
    with pytest.raises(ValueError, match="missing required fields"):
        migrate_v1_to_v3(raw)



def test_v2_to_v3_migration_adds_explicit_schema_metadata():
    raw = yaml.safe_load((ROOT / "configs/customers.yaml").read_text())
    raw["schema_version"] = "2.0"
    for field in ("columns", "dbt_schema", "cdc_cursor"):
        raw["source"].pop(field, None)
    migrated = migrate_v2_to_v3(raw)
    spec = PipelineSpec.model_validate(migrated)
    assert spec.schema_version == "3.0"
    assert spec.source.columns == ["customer_id", "updated_at"]  # inferred subset; human schema enrichment is required
    assert spec.source.dbt_schema == "crm"


def test_migration_rejects_ambiguous_legacy_cdc():
    raw = yaml.safe_load((ROOT / "fixtures/legacy_customers_v1.yaml").read_text())
    raw["mode"] = "cdc"
    with pytest.raises(ValueError, match="manual mapping"):
        migrate_v1_to_v3(raw)


def test_run_history_records_simulation_not_successful_ingestion(tmp_path):
    spec = load_all_specs()[0]
    history = tmp_path / "history.jsonl"
    row = execute_simulation(spec, "test-run-1", history)
    assert row["status"] == "SIMULATED"
    assert row["execution_mode"] == "local_simulation"
    assert row["checkpoint"]["advanced"] is False
    saved = json.loads(history.read_text().splitlines()[0])
    assert saved["run_id"] == "test-run-1"
    assert saved["config_digest"] == row["config_digest"]


def test_simulation_lineage_event_uses_valid_other_event_type():
    from metadata_platform import make_openlineage_event
    spec = load_all_specs()[0]
    row = execute_simulation(spec, "lineage-run", ROOT / "reports" / "test_history.jsonl")
    event = make_openlineage_event(spec, row["run_id"], row["status"], row["started_at"], row["ended_at"])
    assert event["eventType"] == "OTHER"
    assert "simulation only" in event["job"]["facets"]["documentation"]["description"].lower()
    (ROOT / "reports" / "test_history.jsonl").unlink(missing_ok=True)


def test_blank_run_id_rejected(tmp_path):
    with pytest.raises(ValueError, match="run_id must not be blank"):
        execute_simulation(load_all_specs()[0], "  ", tmp_path / "history.jsonl")


def test_deterministic_plans_and_manifest_digests(tmp_path):
    specs = load_all_specs()
    first = write_generated(output_dir=tmp_path / "first")
    second = write_generated(output_dir=tmp_path / "second")
    assert first == second
    manifest_a = json.loads((tmp_path / "first/generated_manifest.json").read_text())
    manifest_b = json.loads((tmp_path / "second/generated_manifest.json").read_text())
    assert manifest_a["artifacts"] == manifest_b["artifacts"]
    assert generate_plan(specs[0])["config_digest"] == spec_digest(specs[0])


def test_exported_json_schema_matches_pydantic_model():
    exported = json.loads((ROOT / "schema/metadata-v3.schema.json").read_text())
    assert exported["properties"]["schema_version"]["const"] == "3.0"
    assert "source" in exported["properties"]
    assert "columns" in exported["$defs"]["SourceSpec"]["properties"]
    assert "dbt_schema" in exported["$defs"]["SourceSpec"]["properties"]
