import json, shutil
from pathlib import Path
import pytest
import yaml
from pydantic import ValidationError
from metadata_platform import ROOT, PipelineSpec, load_spec, load_all_specs, generate_plan, governance_policy, render_dbt_model, migrate_v1_to_v2, execute_simulation, write_generated

def test_three_configs_validate_and_have_unique_targets():
    specs = load_all_specs()
    assert len(specs) == 3
    assert len({s.pipeline_id for s in specs}) == 3
    assert len({s.target.dataset for s in specs}) == 3

def test_incremental_requires_watermark():
    raw = yaml.safe_load((ROOT/"configs/customers.yaml").read_text())
    raw["source"]["watermark"] = None
    with pytest.raises(ValidationError, match="watermark"):
        PipelineSpec.model_validate(raw)

def test_full_mode_rejects_watermark():
    raw = yaml.safe_load((ROOT/"configs/orders.yaml").read_text())
    raw["source"]["watermark"] = "updated_at"
    with pytest.raises(ValidationError, match="full extraction"):
        PipelineSpec.model_validate(raw)

def test_unknown_fields_fail_closed():
    raw = yaml.safe_load((ROOT/"configs/orders.yaml").read_text())
    raw["dangerous_unreviewed_option"] = True
    with pytest.raises(ValidationError, match="Extra inputs"):
        PipelineSpec.model_validate(raw)

def test_sensitive_classification_requires_key_quality_check():
    raw = yaml.safe_load((ROOT/"configs/customers.yaml").read_text())
    raw["quality_checks"] = [{"type":"unique","column":"customer_id"}]
    with pytest.raises(ValidationError, match="not_null"):
        PipelineSpec.model_validate(raw)

def test_governance_driven_by_classification_and_retention():
    specs = {s.pipeline_id:s for s in load_all_specs()}
    conf = governance_policy(specs["crm_customers"])
    pub = governance_policy(specs["erp_product_catalog"])
    assert conf["masking"]["mask_pii"] is True
    assert conf["retention"]["days"] == 365
    assert pub["masking"]["mask_pii"] is False
    assert pub["retention"]["days"] == 1825

def test_generator_outputs_match_fixture_contract(tmp_path):
    plans = write_generated(output_dir=tmp_path)
    assert len(plans) == 3
    plan = json.loads((tmp_path/"crm_customers.plan.json").read_text())
    sql = (tmp_path/"stg_crm_customers.sql").read_text()
    assert plan["pipeline_id"] == "crm_customers"
    assert plan["execution"]["checkpoint_key"] == "crm_customers:watermark"
    expected = json.loads((ROOT/"fixtures/expected_crm_plan_contract.json").read_text())
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
    assert (tmp_path/"governance_policies.json").exists()

def test_sql_identifier_injection_rejected():
    spec = load_all_specs()[0]
    with pytest.raises(ValueError, match="unsafe column"):
        render_dbt_model(spec, ["customer_id; drop table users"])

def test_v1_migration_yields_valid_v2_spec():
    raw = yaml.safe_load((ROOT/"fixtures/legacy_customers_v1.yaml").read_text())
    migrated = migrate_v1_to_v2(raw)
    spec = PipelineSpec.model_validate(migrated)
    assert spec.schema_version == "2.0"
    assert spec.source.extraction_mode == "incremental"
    assert spec.source.watermark == "updated_at"
    assert {q.type for q in spec.quality_checks} == {"not_null", "unique"}

def test_migration_rejects_invalid_legacy_config():
    raw = yaml.safe_load((ROOT/"fixtures/legacy_customers_v1.yaml").read_text())
    raw["watermark_column"] = None
    with pytest.raises(ValueError, match="requires watermark"):
        migrate_v1_to_v2(raw)

def test_run_history_and_lineage_payload_are_structured(tmp_path):
    spec = load_all_specs()[0]
    history = tmp_path/"history.jsonl"
    row = execute_simulation(spec, "test-run-1", history)
    assert row["status"] == "COMPLETE"
    saved = json.loads(history.read_text().splitlines()[0])
    assert saved["run_id"] == "test-run-1"
    assert saved["config_digest"] == row["config_digest"]


def test_exported_json_schema_matches_pydantic_model():
    exported = json.loads((ROOT/"schema/metadata-v2.schema.json").read_text())
    assert exported["properties"]["schema_version"]["const"] == "2.0"
    assert "source" in exported["properties"]

def test_restricted_config_requires_not_null_for_every_composite_key():
    raw = yaml.safe_load((ROOT/"configs/customers.yaml").read_text())
    raw["source"]["keys"] = ["customer_id", "tenant_id"]
    with pytest.raises(ValidationError, match="tenant_id"):
        PipelineSpec.model_validate(raw)
