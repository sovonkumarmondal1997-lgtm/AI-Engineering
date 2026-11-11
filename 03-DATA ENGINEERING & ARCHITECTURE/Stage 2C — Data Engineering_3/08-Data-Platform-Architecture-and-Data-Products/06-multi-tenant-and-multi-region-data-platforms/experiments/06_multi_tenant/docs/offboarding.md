# Tenant offboarding runbook (educational simulation)

1. Validate authorization, tenant ID, scope, and legal holds.
2. Suspend credentials, ingestion, schedules, and writes.
3. Inventory primary tables, staging/marts, object versions, topics, caches, search indexes, feature stores, exports, temporary files, catalogue/lineage, replicas, and backup metadata.
4. Create encrypted export and manifest if required; checksum and audit.
5. Delete primary/derived data; invalidate caches; revoke access and key references.
6. Record backup expiry and restore-time deletion replay; do not claim immediate physical deletion from immutable backups.
7. Remove/tombstone metadata under retention policy; revoke credentials and secrets.
8. Independently verify assets and record exceptions, deadlines, actor, reason, timestamps, and evidence.

`tenancy_lab.offboard_tenant` writes only a simulated manifest/audit JSONL; it does not call external services or delete actual data.
