from pathlib import Path
import json
from tenancy_lab import PolicySimulation, Row, TENANT_A, TENANT_B, simulate_quota, offboard_tenant

root = Path(__file__).parent
policy = PolicySimulation([Row(TENANT_A, "signup", {"id": "a-1"}), Row(TENANT_B, "purchase", {"id": "b-1"})])
print("pool simulation: tenant A visible rows =", len(policy.select(TENANT_A)))
print("pool simulation: tenant B visible rows to A =", len([r for r in policy.select(TENANT_A) if r.tenant_id == TENANT_B]))
print("noisy-neighbour quota =", json.dumps(simulate_quota({"heavy-B": 100, "small-A": 10}, budget=30, per_tenant_cap=20), sort_keys=True))
inventory = [
    {"tenant_id": TENANT_A, "asset_type": "primary_table", "asset_id": "events"},
    {"tenant_id": TENANT_A, "asset_type": "derived_table", "asset_id": "daily_metrics"},
    {"tenant_id": TENANT_A, "asset_type": "cache", "asset_id": "dashboard_cache"},
    {"tenant_id": TENANT_A, "asset_type": "catalogue", "asset_id": "events_asset"},
    {"tenant_id": TENANT_A, "asset_type": "backup_metadata", "asset_id": "snapshot-2026-10-01"},
    {"tenant_id": TENANT_B, "asset_type": "primary_table", "asset_id": "events"},
]
audit = offboard_tenant(TENANT_A, inventory, root / "outputs")
print("offboarding =", json.dumps({"result": audit["result"], "asset_count": audit["asset_count"], "asset_types": audit["asset_types"]}, sort_keys=True))
print("NOTE: local simulation only; no external data was deleted and no regional failover was executed.")
