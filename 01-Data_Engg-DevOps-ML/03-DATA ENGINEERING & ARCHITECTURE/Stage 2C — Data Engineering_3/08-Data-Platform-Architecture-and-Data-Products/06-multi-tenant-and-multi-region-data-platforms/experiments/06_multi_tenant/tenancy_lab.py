from __future__ import annotations
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TENANT_A = "11111111-1111-1111-1111-111111111111"
TENANT_B = "22222222-2222-2222-2222-222222222222"

@dataclass
class Row:
    tenant_id: str
    event_type: str
    payload: dict[str, Any]

class PolicySimulation:
    """Local policy model only; not a database security boundary."""
    def __init__(self, rows: list[Row]):
        self.rows = rows

    def select(self, tenant_context: str | None) -> list[Row]:
        if not tenant_context:
            return []
        return [row for row in self.rows if row.tenant_id == tenant_context]

    def update(self, tenant_context: str | None, row_tenant_id: str, event_type: str) -> int:
        if not tenant_context:
            return 0
        changed = 0
        for row in self.rows:
            if row.tenant_id == tenant_context and row.tenant_id == row_tenant_id:
                row.event_type = event_type
                changed += 1
        return changed

    def insert(self, tenant_context: str | None, tenant_id: str, event_type: str) -> bool:
        if not tenant_context or tenant_context != tenant_id:
            return False
        self.rows.append(Row(tenant_id, event_type, {}))
        return True

def simulate_quota(requests: dict[str, int], budget: int, per_tenant_cap: int) -> dict[str, dict[str, int]]:
    """Deterministic admission policy; not a performance benchmark."""
    result: dict[str, dict[str, int]] = {}
    remaining = budget
    for tenant, requested in requests.items():
        admitted = min(max(requested, 0), per_tenant_cap, remaining)
        result[tenant] = {"requested": requested, "admitted": admitted, "throttled": max(requested - admitted, 0)}
        remaining -= admitted
    return result

def offboard_tenant(tenant_id: str, inventory: list[dict[str, str]], output_dir: Path) -> dict[str, Any]:
    """Simulates export/deletion state and emits an audit record; does not delete external assets."""
    output_dir.mkdir(parents=True, exist_ok=True)
    scoped = [item for item in inventory if item["tenant_id"] == tenant_id]
    manifest = {
        "tenant_id": tenant_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "assets": sorted(scoped, key=lambda item: (item["asset_type"], item["asset_id"])),
        "export_status": "SIMULATED_EXPORT_MANIFEST_CREATED",
        "deletion_status": "SIMULATED_ASSETS_MARKED_DELETED",
        "limitations": "No external storage, caches, backups, or databases were modified.",
    }
    (output_dir / f"{tenant_id}-export-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    audit = {
        "event": "tenant_offboarding_simulated",
        "tenant_id": tenant_id,
        "actor": "lab_operator",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "asset_count": len(scoped),
        "asset_types": sorted({item["asset_type"] for item in scoped}),
        "result": "SIMULATED",
        "evidence": f"{tenant_id}-export-manifest.json",
    }
    with (output_dir / "audit.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(audit) + "\n")
    return audit
