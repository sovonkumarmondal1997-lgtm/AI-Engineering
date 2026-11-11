# Multi-Tenant and Multi-Region Data Platforms
## Stage 2C — Data Engineering_3 · Module 2C.8 · Topic 06

> **Architectural thesis:** multi-tenancy is a resource-sharing and trust-boundary decision; multi-region design is a placement, legal-boundary, consistency, and recovery decision. Neither is solved by adding `tenant_id` to a table or deploying a second region.

## 1. Learning objectives

By the end of this lesson, you should be able to:

- Choose silo, pool, or bridge/hybrid tenancy against isolation, cost, customisation, operations, and scale.
- Trace trusted tenant identity through ingestion, events, tables, partitions, topics, logs, lineage, authorization, and query execution.
- Explain why a tenant column is not an access-control boundary and demonstrate PostgreSQL row-level security (RLS).
- Design noisy-neighbour controls, per-tenant service tiers, usage attribution, showback, and chargeback.
- Distinguish regions from availability zones and design placement around latency, locality, and residency constraints.
- Compare active-passive, active-active, and regional-hub/global-aggregation patterns.
- Define measurable RPO/RTO targets and distinguish targets from observed drill results.
- Design tenant onboarding, export, migration, offboarding, and deletion with auditable evidence.
- Run the lab and identify what must be tested against a real PostgreSQL deployment.

## 2. Prerequisites and terminology

Expected background: SQL and relational modelling, IAM, batch/stream processing, partitioning, orchestration, catalogues/lineage, data quality, and basic cloud-region concepts.

| Term | Meaning |
|---|---|
| Tenant | Customer, business unit, or consumer whose data, policies, usage, and lifecycle must be governed. |
| Tenant context | Trusted identity established by authentication and authorization. Never trust an arbitrary client-supplied tenant header alone. |
| Silo / pool / bridge | Separate stack / shared stack / mixed placement. |
| RLS | Database row-level security that filters or constrains rows according to policy. |
| Noisy neighbour | A tenant whose workload consumes shared capacity and degrades another tenant's service. |
| Region / availability zone (AZ) | Geographic deployment area / isolated failure domain within a region. AZs are not a substitute for regional DR. |
| Residency / sovereignty | Where data is stored or processed / applicable legal authority and control. |
| RPO / RTO | Recovery Point Objective: maximum tolerable data-loss window. Recovery Time Objective: maximum tolerable service-restoration time. |
| Showback / chargeback | Report cost / allocate or bill costs to a tenant or cost centre. |
| SLO / SLA | Measured service objective / contractual service commitment, often with remedies. |

## 3. Multi-tenancy fundamentals

A multi-tenant platform serves multiple customers on shared control plane, software, infrastructure, or operational workflows. Sharing can reduce unit cost and simplify upgrades, but it creates isolation and fairness obligations.

Requirements to make explicit:

1. **Isolation:** one tenant must not read, change, infer, or delete another tenant's data or state.
2. **Performance:** a burst from one tenant must not exhaust shared capacity.
3. **Security:** identity, authorization, encryption, secrets, audit, and administrative access must be designed together.
4. **Governance:** retention, residency, export, deletion, and legal hold can differ by tenant.
5. **Economics:** fixed infrastructure, variable consumption, support, and compliance costs need attribution.
6. **Operations:** onboarding, upgrades, incidents, migrations, and recovery must work across thousands of tenants.
7. **Customisation:** enterprise customers may require dedicated keys, private networking, dedicated compute, longer retention, or stronger recovery commitments.
8. **Scalability:** control-plane metadata, partition counts, connection pools, catalogues, and automation must scale with tenant count.

Tenant is a security and lifecycle boundary, but not necessarily the same as database, workspace, legal entity, billing account, or region. Model these separately when their cardinalities differ.

## 4. Silo, pool, and hybrid tenancy

| Dimension | Silo | Pool | Bridge / hybrid |
|---|---|---|---|
| Data plane | Dedicated stack/database/account or cluster | Shared tables and compute with tenant-aware controls | Shared baseline plus dedicated resources for selected tenants |
| Isolation blast radius | Usually smaller if IAM/network/admin paths are separate | Larger; policy mistakes can affect many tenants | Depends on shared components and escape routes |
| Cost | Highest fixed cost | Lowest unit cost at scale | Intermediate; premium tenants pay for dedicated capacity |
| Operations | Many deployments, upgrades, and backups | Shared platform, stronger guardrails required | More placement states and migrations |
| Noisy neighbours | Easier to bound with dedicated capacity | Requires quotas and fair scheduling | Dedicated resources for hot or premium tenants |
| Customisation | High | Constrained to common product | Tiered |
| Fit | Regulated/high-value enterprise or bespoke workload | Many small tenants with common needs | Most mature B2B SaaS portfolios |

**Decision rule:** pool by default only when the platform can enforce tenant-aware authorization and fairness. Use silo when isolation, residency, contractual commitments, or workload profile justify the operating cost. Use hybrid when requirements vary materially by tenant class.

A silo is not automatically secure: shared administrators, backups, CI/CD credentials, control-plane APIs, or cross-account roles can still cross the boundary. A pool is not automatically insecure: well-enforced policies, narrowly scoped roles, tests, and monitoring can make it appropriate.

## 5. Tenant identity and isolation

Use an immutable internal `tenant_id` (opaque UUID or stable identifier) and a separate mapping from external account IDs. Resolve identity from a verified token/session and server-side membership. Reject missing, unknown, suspended, or mismatched tenant context before data operations.

Propagate tenant context through:

- **Events and ingestion:** validate identity in the envelope at ingestion.
- **Tables:** carry `tenant_id` through raw, staging, intermediate, marts, aggregates, and deletion manifests; use tenant-aware keys and constraints.
- **Partitions and object paths:** partitioning can improve pruning/deletion, but is not authorization. Avoid tiny partitions for thousands of small tenants.
- **Topics and streams:** include tenant identity in envelopes/keys and enforce producer/consumer authorization. Kafka quotas constrain resources, not confidentiality.
- **Logs, traces, metadata, lineage:** attach controlled tenant attributes; redact payloads/secrets. Metadata may itself be sensitive.
- **Access policies/query execution:** derive database context from trusted server-side identity, bind parameters, and enforce policy at storage/compute boundaries.

Isolation mechanisms include separate cloud accounts/projects, databases, schemas, shared tables with RLS, per-tenant keys, tenant-aware partitions, per-tenant warehouses/queues, network policies, scoped secrets, and tenant-aware cache/idempotency keys.

**Why `tenant_id` is not enough:** `WHERE tenant_id = :tenant_id` is an application convention easily omitted in new queries, joins, views, BI tools, or jobs. Use trusted identity, database-enforced policy, least privilege, negative tests, and monitoring.

## 6. Security boundaries and testing

### PostgreSQL RLS example: bind the policy to a database-authenticated principal

**Threat-model warning:** a policy based only on `current_setting('app.tenant_id')` is useful against accidentally omitted filters, but a shared database login that can execute arbitrary SQL can usually set that custom parameter to another tenant's value. It is not, by itself, a boundary against SQL injection or a malicious holder of that shared credential. Do not describe that pattern as preventing a caller from spoofing tenant identity.

The companion lab demonstrates a stronger, explicit model: each tenant connects using a tenant-specific database login, and RLS maps the unforgeable `session_user` value to the tenant. This increases role/credential lifecycle overhead; for large deployments, use a reviewed identity-aware database proxy or a cryptographically verified context design rather than trusting a client-settable GUC. Never expose tenant database credentials to end users.

Illustrative bootstrap (the lab uses local-only credentials; replace them in real deployments):

```sql
CREATE ROLE tenant_a_runtime LOGIN PASSWORD 'tenant_a_local_only'
  NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS;
CREATE ROLE tenant_b_runtime LOGIN PASSWORD 'tenant_b_local_only'
  NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS;

-- Assume app is owned by a privileged migration role and tenant roles already exist.
CREATE ROLE tenant_policy_owner NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS;
GRANT USAGE, CREATE ON SCHEMA app TO tenant_policy_owner;
CREATE TABLE app.tenant_principals (
  db_role name PRIMARY KEY,
  tenant_id uuid NOT NULL UNIQUE
);
ALTER TABLE app.tenant_principals OWNER TO tenant_policy_owner;
INSERT INTO app.tenant_principals VALUES
  ('tenant_a_runtime', '11111111-1111-1111-1111-111111111111'),
  ('tenant_b_runtime', '22222222-2222-2222-2222-222222222222');
REVOKE ALL ON app.tenant_principals FROM PUBLIC;

CREATE FUNCTION app.current_tenant_id() RETURNS uuid
LANGUAGE sql STABLE SECURITY DEFINER
SET search_path = pg_catalog, app
AS $$
  SELECT tenant_id FROM app.tenant_principals WHERE db_role = session_user
$$;
ALTER FUNCTION app.current_tenant_id() OWNER TO tenant_policy_owner;
REVOKE ALL ON FUNCTION app.current_tenant_id() FROM PUBLIC;
REVOKE CREATE ON SCHEMA app FROM tenant_policy_owner;
GRANT EXECUTE ON FUNCTION app.current_tenant_id() TO tenant_a_runtime, tenant_b_runtime;

CREATE TABLE app.events (
  event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL,
  event_type text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE app.events ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.events FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON app.events
  USING (tenant_id = app.current_tenant_id())
  WITH CHECK (tenant_id = app.current_tenant_id());
GRANT USAGE ON SCHEMA app TO tenant_a_runtime, tenant_b_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON app.events TO tenant_a_runtime, tenant_b_runtime;
```

`session_user` remains the authenticated login identity inside the security-definer function; callers cannot change it with `SET ROLE` or a custom GUC. The function has a fixed `search_path`, its owner is non-login and non-superuser, and the mapping table is not writable by tenant roles. Review these properties during deployment. Superusers and `BYPASSRLS` roles remain privileged; table owners can bypass ordinary RLS unless forced and constrained. Test read, insert, update, delete, joins, views, exports, missing/unmapped identity, and attempted spoofing. Security-definer functions and privileged jobs require separate review.

Security checklist:

- [ ] Canonical identity is authenticated, immutable, and propagated.
- [ ] Runtime role is not owner, superuser, or `BYPASSRLS`.
- [ ] RLS is enabled and forced; `USING` and `WITH CHECK` are reviewed.
- [ ] BI, scheduled jobs, support tools, exports, and async paths are tested.
- [ ] Connection pools preserve the authenticated tenant principal; a connection is never reused across tenants without a verified identity switch and reset test.
- [ ] Logs/lineage avoid secrets and unnecessary payloads.
- [ ] Key rotation, break-glass access, and admin access are audited.
- [ ] CI tests run against a production-like database configuration.

## 7. Noisy-neighbour controls

One tenant may run a large scan, burst messages, monopolise concurrency, or generate expensive transformations. Apply layered controls:

1. **Admission control:** request rate, concurrent queries, bytes scanned, queue depth, job budget.
2. **Fair scheduling:** weighted queues, concurrency caps, workload classes, reserved capacity.
3. **Resource isolation:** separate warehouses/queues for heavy tenants, query timeouts, memory limits, scaling boundaries.
4. **Backpressure:** reject, defer, or slow noncritical work before shared services fail.
5. **Workload design:** pruning, incremental models, pre-aggregation, tenant-aware caches, limits on ad hoc query complexity.
6. **SLO monitoring:** latency/errors by tenant and tier, plus saturation metrics.
7. **Abuse controls:** budgets, alerts, throttling, escalation.

Examples of distinct control planes:

- **Snowflake warehouses:** separate compute/scaling boundaries can isolate compute consumption; they do not grant data permissions.
- **BigQuery reservations:** assignments shape compute availability; IAM/dataset policy still governs access.
- **Kafka quotas:** constrain client throughput/request use; they do not authorize tenant records within a shared topic.

The lab uses a deterministic token-budget scheduler. It demonstrates policy, not database CPU isolation or a cloud benchmark. Production measurement should include queue wait, p95/p99 latency, throttled requests, and resource saturation.

## 8. Cost attribution and tenant lifecycle

Track usage at `(tenant_id, region, service, workload_class, day)` where possible: bytes scanned, compute seconds/credits, storage GB-days, egress, events, task runtime, concurrency, support hours. Separate directly measured usage from allocated shared fixed cost. Reconcile telemetry with provider billing.

- **Showback:** usage/cost reports without invoicing.
- **Chargeback:** allocation to contract, invoice, cost centre, or budget.
- **Service tiers:** specify concurrency, throughput, retention, support, and recovery objectives. Don't imply equal SLOs when capacity differs.
- Define SLOs by both region and tenant tier; a region-wide aggregate can hide a failing tenant or workload. Track availability, p95/p99 latency, errors, queue lag, and recovery status with region/tier labels, while avoiding uncontrolled metric cardinality.
- Avoid high-cardinality metric explosions; retain detailed per-tenant usage in logs/warehouse tables.

**Onboarding:** create registry entry → assign region/tier → provision resources → create identity/key references → apply policies → set quotas → canary-test → record owner/config/audit.

**Export:** authorize request → scope and cutoff → encrypted export/manifest → checksums and object versions → approved delivery → receipt/expiry verification → audit.

**Offboarding:** suspend writes/credentials → inventory all assets → export if required → delete primary data → delete derived tables/materialized views/features/search indexes/caches/object versions/stream retention/temp files → track backup expiry and restore-time deletion replay → remove/tombstone catalogue/lineage under policy → revoke keys → verify → audit.

Immutable backups may not permit immediate physical deletion without affecting other tenants. Define retention windows, legal holds, restore-time deletion replay, and what “complete” means. Never claim completion while replicas, caches, backups, or derived assets remain unaccounted for.

## 9. Regions and data residency

A **region** is a geographic deployment area. An **availability zone** is an isolated failure domain within a region; multi-AZ resilience does not equal regional DR.

Placement must consider latency, locality, contracts, applicable law, processing location, support access, telemetry, backups, keys, logs, egress, service availability, and capacity. The control plane's metadata may itself be sensitive.

GDPR and other laws may impose obligations for personal data, transfers, safeguards, processors, and data-subject rights. “Stored in EU” alone does not establish compliance, and a US copy is not universally permitted or forbidden in every case. Legal/privacy owners must map categories, purposes, transfers, contracts, and retention. This is architecture education, not legal advice or a compliance guarantee.

Maintain a tenant placement registry such as `tenant_id → home_region, residency_class, tier, endpoints, key references, allowed processing regions`. Resolve placement before reads/writes and fail closed if placement is missing or inconsistent.

Use regional catalogues for detailed assets, schema, lineage, and operations when metadata is residency-sensitive. A global catalogue may store only minimal non-sensitive indexes or opaque references. Treat query logs and lineage as potentially regulated data.

Global analytics options:
- **Federated queries:** compute in region and return results; coordinator/logs/cache/results still need review.
- **Regional aggregation:** compute metrics locally and export approved aggregates.
- **Privacy-preserving rollups:** minimum cohort sizes, suppression, rounding, differential privacy where justified, and release review.
- **Global data products:** define dimensions/grain/freshness and assess re-identification risk. Small-cell counts can reveal individuals even without direct identifiers.

## 10. Multi-region architecture patterns

**Active-passive:** one region serves writes; recovery region receives replication or backups. Simpler write ownership, but promotion/routing/validation take time and replication lag can imply data loss.

**Active-active:** both regions serve traffic. Use when latency/availability justifies complexity. Define entity ownership, conflict resolution, idempotency, clock assumptions, and network-partition behavior. It does not magically provide globally serializable transactions.

**Regional hubs with global aggregation:** each residency region owns raw data and regional products; global layer receives approved aggregates/minimal metadata. Strong default where raw data must remain local, but aggregates can still be sensitive.

Recommended case-study default: regional hubs with region-local tenant pools and active-passive recovery **within each approved residency boundary**. EU tenant data and DR copies remain in the approved EU boundary; US tenant data and copies remain in the approved US boundary. Global operations receive minimal opaque health/cost signals and approved aggregates only. Do not fail an EU tenant to the US unless a documented legal, contractual, and privacy review permits it.

```mermaid
flowchart TB
  U[Customers / API clients] --> G[Global edge: identity, tenant lookup, routing]
  G -->|EU tenant| EU[EU regional hub]
  G -->|US tenant| US[US regional hub]
  subgraph EUB[EU approved residency boundary]
    EU --> EUP[EU pooled data plane: RLS and quotas]
    EU --> EUS[EU enterprise silo stacks]
    EUP --> EUD[(EU warehouse / object store)]
    EUS --> EUD
    EUD --> EUDR[(EU DR replica / backup)]
    EUM[EU regional catalogue and lineage]
  end
  subgraph USB[US approved residency boundary]
    US --> USP[US pooled data plane: RLS and quotas]
    US --> USS[US enterprise silo stacks]
    USP --> USD[(US warehouse / object store)]
    USS --> USD
    USD --> USDR[(US DR replica / backup)]
    USM[US regional catalogue and lineage]
  end
  EUD --> EA[Approved EU regional aggregate]
  USD --> UA[Approved US regional aggregate]
  EA --> GA[Global aggregate service]
  UA --> GA
  EUM --> EM[Minimal global metadata index]
  USM --> EM
```

This is a logical diagram, not a deployed system. Global edge telemetry must not become a covert data plane. If identity metadata itself contains regulated personal data, regionalise or minimise it.

## 11. Replication, consistency, and conflict handling

Replication does not guarantee zero lag, identical cross-system ordering, legal permission to transfer, or application consistency.

| System | Mechanisms | Questions |
|---|---|---|
| Object storage | Versioning, replication rules, inventory, checksums, lifecycle | Which prefixes/versions replicate? Are destinations allowed? What happens to deletes, object lock, and legal holds? |
| Kafka | MirrorMaker 2 or Cluster Linking; topic/ACL/config handling | Are offsets, consumer groups, schemas, ACLs, configs covered? How are duplicate/replayed events handled? |
| Warehouse | Provider-specific replication/failover groups | Which objects are included? What is lag visibility? Who can promote/fail back? |
| Relational DB | Streaming replicas, managed cross-region replicas, backup/restore | Is replica read-only? What durability is acknowledged? How is old primary fenced? |

- **Asynchronous replication:** lower write latency, but nonzero RPO is possible.
- **Synchronous cross-region replication:** may reduce acknowledged-write loss under defined assumptions, but adds latency and can reduce write availability when remote link/region fails.
- **Single writer per tenant/entity:** simpler conflicts; failover must fence old writers.
- **Active-active writes:** define deterministic conflict rules (application merge, version vectors, conflict queue, or last-writer-wins with caveats). Clock-based last-writer-wins can lose updates.
- **At-least-once event replication:** consumers must be idempotent; use stable event IDs and deduplication.
- **Schema/policy replication:** schema registry, catalogue, ACL, and key references must be recovered too.

Every replicated asset needs owner, source/destination, policy basis, lag SLO, delete behavior, and tested recovery procedure. If residency forbids cross-region copies, use in-boundary backups/AZ redundancy or another explicitly approved geography—never a hidden exception.

## 12. Disaster recovery, RPO, and RTO

- **RPO** is the maximum acceptable age of data lost after a disruptive event. An RPO of five minutes means the design target bounds lost business data to that window for the specified failure scenario and measurement method.
- **RTO** is the maximum acceptable elapsed time from declared disruption to restoration of the defined service level. A VM starting is not service recovery; include routing, auth, correctness, backlog, and consumer validation.

Illustrative planning targets—not universal recommendations and not measured by this lab:

| Tier | Illustrative RPO | Illustrative RTO | Design implication |
|---|---:|---:|---|
| Small shared tenants | ≤ 15 min | ≤ 4 h | Async replication/backups may be acceptable if tested and contractually disclosed. |
| Enterprise analytics | ≤ 5 min | ≤ 60 min | Higher-frequency replication, reserved recovery capacity, automation, stronger validation. |
| Critical ingestion/control plane | ≤ 1 min | ≤ 30 min | Requires separate cost/availability analysis; no assumption these targets are achieved. |

Measure from drills. RPO uses the gap between last durable business event before failure and recovered point. RTO runs from documented incident trigger to validated service restoration. Record timestamps, data gaps, stale reads, queue lag, failed dependencies, and manual steps. A target is not evidence.

Recovery sequence:
1. Detect/declare incident; identify affected region and tenants.
2. Freeze or fence writes to avoid dual-primary/split-brain.
3. Check replication lag, last durable offsets, backup integrity, and residency.
4. Select approved promotion/restore point.
5. Promote and route only within permitted placement.
6. Validate IAM, RLS, keys, catalogue, schema, quotas, and critical queries.
7. Reconcile events/derived tables; deduplicate replays and verify counts/checksums.
8. Drain backlog, observe SLOs, communicate impact.
9. Preserve evidence and record actual RPO/RTO.
10. Fail back only after clean resynchronisation, fencing, and validation.

Run drills for region loss, control-plane outage, key-service failure, accidental deletion, bad schema deployment, and replication-link loss. A successful backup job alone does not prove recoverability.

**Compliance evidence (SOC 2 / ISO/IEC 27001):** treat these as control frameworks, not automatic certifications conferred by an architecture. Maintain evidence for access provisioning/reviews and revocation, privileged/break-glass access, change approvals, key lifecycle, security monitoring, incident response, supplier controls, retention/deletion exceptions, backup restoration, recovery drills, and tenant-specific SLO reporting. Map controls to the organisation's actual scope, auditor/certification requirements, and statement of applicability; do not claim compliance merely because a control is described here.

## 13. Hands-on implementation and tests

The companion project is `experiments/06_multi_tenant/`. It contains:
- PostgreSQL pooled-tenancy DDL with forced RLS and tenant-specific authenticated database roles.
- Integration tests for cross-tenant reads, updates, inserts, and attempted tenant-context spoofing.
- Local Python policy simulation when PostgreSQL/Docker is unavailable.
- Silo-style schema-per-tenant SQL example.
- Deterministic noisy-neighbour quota simulation.
- Offboarding inventory/export-manifest/audit simulation.
- Regional architecture and failover checklist.

### Run local simulation

```bash
cd experiments/06_multi_tenant
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
pytest -q
python run_lab.py
```

Expected without both `TEST_DATABASE_URL_A` and `TEST_DATABASE_URL_B`: five local tests pass and two PostgreSQL integration tests skip. Pytest version may alter summary formatting. Local tests validate the simulation and SQL artefact presence—not runtime PostgreSQL RLS.

### Run PostgreSQL integration tests

Requires Docker Compose and a Docker daemon:

```bash
docker compose up -d --wait
# Linux/macOS: configure two distinct tenant logins
export TEST_DATABASE_URL_A='postgresql://tenant_a_runtime:tenant_a_local_only@localhost:55432/tenant_lab'
export TEST_DATABASE_URL_B='postgresql://tenant_b_runtime:tenant_b_local_only@localhost:55432/tenant_lab'
# PowerShell equivalents:
# $env:TEST_DATABASE_URL_A = "postgresql://tenant_a_runtime:tenant_a_local_only@localhost:55432/tenant_lab"
# $env:TEST_DATABASE_URL_B = "postgresql://tenant_b_runtime:tenant_b_local_only@localhost:55432/tenant_lab"
python -m pip install -e ".[test]"
python -m pytest -q
docker compose down -v
```

The integration tests connect as distinct tenant logins, not the table owner. Tenant A must see only A, must not read/update/delete B, must not insert a B-owned row, and must not gain B access by setting `app.tenant_id`. A passing run validates this lab configuration only—not production isolation or a penetration test.

Assumptions/limits:
- Compose credentials are lab-only and per-tenant login is an illustrative isolation model, not a universal recommendation for 5,000 tenants.
- A privileged bootstrap role creates objects/grants; tenant roles are separate and have no membership in each other.
- RLS does not protect against superusers, `BYPASSRLS` roles, malicious privileged functions, compromised tenant credentials, or data paths outside the policy boundary.
- Offboarding writes a simulated manifest and audit event; it does not delete real cloud versions, managed backups, external caches, or SaaS assets.
- No cloud region is provisioned; the diagram is not a failover test.

## 14. Worked SaaS architecture case study

### Assumptions

- 5,000 small tenants use a common analytics product and similar security requirements.
- 20 enterprise tenants require stronger contractual isolation, support, custom retention, and predictable capacity; some need dedicated keys/private connectivity.
- EU and US customers have separate approved residency classes; raw tenant-level records do not cross boundaries by default.
- Each tenant has one home region for primary writes. DR remains within its approved boundary unless an explicit legal/contractual exception is approved.
- For the case study, target the small pooled cohort at RPO ≤ 15 minutes / RTO ≤ 4 hours and the enterprise cohort at RPO ≤ 5 minutes / RTO ≤ 60 minutes, subject to costed design and timed drills. These are objectives, not measured results.
- The two-region phrase means one primary plus an approved recovery location per residency class; it does not mean EU data may fail over to the US or vice versa. If only one in-jurisdiction region is available, the architecture must state that regional-loss recovery is unavailable or obtain an approved alternate geography.
- Separate EU and US regional stacks can be operated.

### Tenancy choice

**5,000 small tenants: pooled tenancy per region.** Shared services and storage/compute, RLS, canonical tenant context, quotas, per-tenant usage records, and regional placement. Partition for workload and operational efficiency, not necessarily one physical partition per tenant. Add dedicated queue/warehouse capacity when measured consumption breaches tier thresholds.

**20 enterprise tenants: bridge model with siloed data plane where contract/risk requires it.** Dedicated database/schema/account or full stack according to threat model; reserved compute, per-tenant keys/private connectivity where required. Keep a shared control plane only if its metadata/admin access is acceptable; isolate it when necessary.

| Dimension | Small pooled cohort | Enterprise silo/hybrid cohort |
|---|---|---|
| Cost | Low marginal cost | Higher fixed and operating cost |
| Isolation | RLS, least privilege, tests | Resource/account/credential separation plus policy controls |
| Workload | Quotas and fair scheduling | Reserved/dedicated compute, stronger SLOs |
| Access | Standard roles/policy templates | Tenant-specific IAM/network/key requirements |
| Operations | Automated onboarding/shared upgrades | Fleet automation and controlled version skew |
| Migration | Tenant-aware copy and cutover | Provision, snapshot/CDC, reconcile, route switch |

### Migration between pool and silo

1. Confirm target region/tenancy policy and approve data movement.
2. Provision target schema, RLS/roles, grants, retention, quotas, monitoring, and keys.
3. Copy a consistent snapshot, then capture changes with CDC or a short write freeze.
4. Reconcile counts, checksums, keys, aggregates, and policy behavior.
5. Run shadow reads and compare results.
6. Switch versioned tenant routing with rollback.
7. Fence old writes; validate new SLOs; retire old data under retention policy.
8. Update catalogue, lineage, billing, support runbooks, and DR plans.

Separate a hot tenant when measured saturation/SLO breaches persist or contract requires it—not just because it is large. Migration complexity is state consistency, dependencies, cutover, and rollback, not creating a schema.

### Two-region design

- Tenant registry maps tenant to EU or US; gateway routes authenticated requests to the home region.
- Each region has independent data plane, object storage, warehouse, keys, quotas, regional catalogue/lineage, observability, and recovery environment.
- Primary and DR copies remain inside the approved boundary.
- Only approved aggregates and minimal opaque health/cost signals flow globally.
- Global aggregation rejects raw rows, applies cohort thresholds, and reviews re-identification risk.
- Failover is fenced and audited. Never silently route EU tenants to US.
- Validate RPO/RTO with drills covering IAM, keys, routing, ingestion backlog, derived tables, and query success.

## 15. Failover and offboarding checklists

### Failover/recovery drill

- [ ] Define scenario, blast radius, success criteria, observers, rollback.
- [ ] Confirm replication topology and legal/residency boundary.
- [ ] Record baseline and last durable source offsets.
- [ ] Trigger controlled failure and timestamp incident start.
- [ ] Fence old writers; verify no split-brain.
- [ ] Confirm replica lag and backup integrity.
- [ ] Promote/restore only within approved boundary.
- [ ] Validate routing, authentication, keys, RLS, schema, catalogue, quotas.
- [ ] Reconcile counts, checksums, event IDs, derived tables, backlog.
- [ ] Run tenant smoke tests and measure SLOs.
- [ ] Record actual RPO/RTO, data gap, stale reads, manual steps, failures.
- [ ] Fail back only after controlled resynchronisation and validation.
- [ ] Assign remediation owners/dates and repeat after fixes.

### Offboarding

- [ ] Verify authorized request, tenant ID, scope, legal holds.
- [ ] Suspend credentials, ingestion, schedules, and writes.
- [ ] Inventory raw/staging/marts, object versions, topics, caches, search, features, exports, temp data, catalogue/lineage, replicas, backup metadata.
- [ ] Create encrypted export manifest if required.
- [ ] Delete primary/derived data; invalidate caches; revoke access.
- [ ] Track replica and backup expiry; define restore-time deletion replay.
- [ ] Remove/tombstone metadata under retention policy.
- [ ] Revoke keys/secrets and grants.
- [ ] Independently verify deletion and record exceptions/deadlines.
- [ ] Emit access-controlled audit record with actor, reason, timestamps, inventory version, outcome, evidence.

## 16. Common mistakes and misconceptions

- **“Tenant ID is enough.”** It is data, not policy.
- **“Schema-per-tenant equals silo.”** Schemas can share roles, compute, database failure domain, and admins.
- **“RLS protects against DB admins.”** Superusers and bypass roles remain privileged.
- **“Multi-AZ means multi-region.”** AZs are generally within one region.
- **“Replication means zero data loss.”** Async replication has lag.
- **“Active-active is always more available.”** Conflicts, quorum dependencies, and split-brain risks add failure modes.
- **“The catalogue is only metadata.”** Names, query text, lineage, and IDs may be sensitive.
- **“Delete the tenant row and done.”** Derived assets, caches, streams, backups, and exports matter.
- **“Backup succeeded, so DR works.”** Restore and application validation are required.
- **“EU region means compliance.”** Legal, contract, access, transfer, backup, and process controls still matter.
- **“Dedicated compute means data isolation.”** Compute isolation is not authorization.
- **“RPO/RTO targets are achieved by design.”** Demonstrate them in timed drills.

## 17. Practice questions with answers

**Q1. Why isn't a tenant column sufficient?**  
It does not force every query, join, view, export, or job to filter correctly. Use trusted context, database-enforced policy, least privilege, and negative tests.

**Q2. When is silo justified?**  
When isolation, residency, contractual SLOs, customisation, workload, or blast-radius needs outweigh fixed and operational cost.

**Q3. RPO vs RTO?**  
RPO bounds tolerable data loss measured in time; RTO bounds time to restore the defined service level.

**Q4. What does Kafka quota solve—and not solve?**  
It constrains client resource usage/throughput, not which tenant's records a consumer may read.

**Q5. How can global analytics respect residency?**  
Compute approved aggregates locally, export reviewed rollups, minimise global metadata, assess re-identification risk, and govern result/log/cache paths.

**Q6. Hardest part of pool-to-silo migration?**  
Consistent state transfer, CDC, policy parity, dependencies, cutover/rollback, and retiring old copies.

**Q7. What proves DR target?**  
Timestamped drill with defined incident start, validated restoration, measured data gap, and documented results—not a config or vendor claim.

**Q8. What must offboarding cover?**  
Authorization/legal hold, export, primary/derived data, caches, feature/search stores, streams, replicas, backups, metadata, credentials/keys, restore-time deletion, audit.

## 18. Completion checklist

- [ ] I can defend silo/pool/hybrid against explicit requirements.
- [ ] I can trace identity through events, storage, streams, logs, lineage, and query execution.
- [ ] I understand RLS role/ownership assumptions and can run integration tests.
- [ ] I can design noisy-neighbour controls and per-tenant cost attribution.
- [ ] I can map data, metadata, backups, and support access to residency.
- [ ] I can compare active-passive, active-active, and regional aggregation.
- [ ] I can define and measure RPO/RTO in a drill.
- [ ] I can migrate tenancy with reconciliation and rollback.
- [ ] I can offboard with a complete inventory and audit trail.
- [ ] I have met the roadmap checkpoint: choose a model, enforce/test isolation, control noisy neighbours, design residency/RPO/RTO.

## 19. Primary references and further reading

Official/primary documentation; verify current versions and regional availability before implementation.

1. PostgreSQL — Row Security Policies: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
2. PostgreSQL — `CREATE POLICY`: https://www.postgresql.org/docs/current/sql-createpolicy.html
3. PostgreSQL — `SET` / configuration parameters: https://www.postgresql.org/docs/current/sql-set.html
4. Snowflake — Virtual warehouses: https://docs.snowflake.com/en/user-guide/warehouses
5. Google Cloud — BigQuery reservations: https://cloud.google.com/bigquery/docs/reservations-intro
6. Apache Kafka — Quotas: https://kafka.apache.org/documentation/#design_quotas
7. Apache Kafka — MirrorMaker 2: https://kafka.apache.org/documentation/#georeplication
8. Confluent — Cluster Linking: https://docs.confluent.io/cloud/current/multi-cloud/cluster-linking/index.html
9. AWS — S3 replication: https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication.html
10. AWS — RDS cross-Region read replicas: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.XRgn.html
11. Google Cloud — BigQuery data replication: https://cloud.google.com/bigquery/docs/data-replication
12. GDPR — Regulation (EU) 2016/679, official text: https://eur-lex.europa.eu/eli/reg/2016/679/oj
13. European Commission — International data transfers: https://commission.europa.eu/law/law-topic/data-protection/international-dimension-data-protection_en
14. AICPA — SOC for Service Organizations: https://www.aicpa-cima.com/resources/landing/system-and-organization-controls-soc-suite-of-services
15. ISO — ISO/IEC 27001: https://www.iso.org/standard/27001
16. OpenLineage — Specification: https://openlineage.io/docs/spec/

### Roadmap alignment

This follows Topic 06 of `roadmap-Data-Platform-Architecture-and-Data-Products.md`: tenancy choices, identity propagation, regions/residency, isolation, noisy neighbours, lifecycle, cost attribution, replication/DR, global analytics, tenant-aware metadata/lineage, compliance evidence, and pool/silo migration. It includes the prescribed `experiments/06_multi_tenant/` exercise, the 5,000-small/20-enterprise case, EU/US design, checkpoints, and common mistakes. `Roadmap_ptree.md` locates the target under `Stage 2C — Data Engineering_3/08-Data-Platform-Architecture-and-Data-Products/`.
