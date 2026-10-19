import json
from pathlib import Path
from tenancy_lab import PolicySimulation, Row, TENANT_A, TENANT_B, simulate_quota, offboard_tenant

def test_policy_simulation_is_tenant_scoped():
    policy = PolicySimulation([Row(TENANT_A, "a", {}), Row(TENANT_B, "b", {})])
    assert [row.event_type for row in policy.select(TENANT_A)] == ["a"]
    assert policy.select(None) == []
    assert policy.update(TENANT_A, TENANT_B, "tampered") == 0
    assert policy.insert(TENANT_A, TENANT_B, "spoofed") is False

def test_quota_caps_heavy_tenant_and_preserves_budget():
    result = simulate_quota({"heavy": 100, "small": 10}, budget=30, per_tenant_cap=20)
    assert result["heavy"] == {"requested": 100, "admitted": 20, "throttled": 80}
    assert result["small"]["admitted"] == 10
    assert sum(x["admitted"] for x in result.values()) <= 30

def test_offboarding_inventory_and_audit(tmp_path):
    inventory = [
        {"tenant_id": TENANT_A, "asset_type": "primary_table", "asset_id": "events"},
        {"tenant_id": TENANT_A, "asset_type": "cache", "asset_id": "cache"},
        {"tenant_id": TENANT_B, "asset_type": "primary_table", "asset_id": "events"},
    ]
    audit = offboard_tenant(TENANT_A, inventory, tmp_path)
    manifest = json.loads((tmp_path / f"{TENANT_A}-export-manifest.json").read_text())
    assert audit["asset_count"] == 2
    assert {x["asset_id"] for x in manifest["assets"]} == {"events", "cache"}
    assert manifest["deletion_status"].startswith("SIMULATED")
    assert "No external" in manifest["limitations"]
    line = json.loads((tmp_path / "audit.jsonl").read_text().splitlines()[0])
    assert line["tenant_id"] == TENANT_A and line["result"] == "SIMULATED"

def test_sql_has_forced_rls_and_both_policy_clauses():
    sql = (Path(__file__).parents[1] / "postgres" / "bootstrap.sql").read_text().lower()
    assert "enable row level security" in sql
    assert "force row level security" in sql
    assert "using (" in sql and "with check (" in sql
    assert "nobypassrls" in sql


def test_rls_policy_uses_authenticated_session_identity_not_client_guc():
    sql = (Path(__file__).parents[1] / "postgres" / "bootstrap.sql").read_text().lower()
    assert "where db_role = session_user" in sql
    assert "security definer" in sql
    assert "revoke create on schema app from tenant_policy_owner" in sql
    assert "current_setting('app.tenant_id'" not in sql
    assert "tenant_a_runtime" in sql and "tenant_b_runtime" in sql
