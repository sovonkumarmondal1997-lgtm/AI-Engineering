# Project Roadmap — AWS Serverless Lakehouse

This is the end-to-end roadmap for **Gap Project 03: AWS Serverless
Lakehouse**, the project for **Gap Module G3 — AWS Data Engineering Deep
Dive**. It takes you from an empty AWS account to a **production-grade
lakehouse on AWS** that ingests files, database changes, and click events;
transforms them into governed Iceberg tables; serves analysts through
Athena and Redshift Serverless; and is secured, observed, cost-controlled,
tested, deployed through CI/CD, recoverable, and torn down cleanly.

"Production grade" here means: every resource is created as code; every
workload runs with least privilege and encrypted, private data paths; bad
data is blocked before publication; failures alert a human; access is
fine-grained and tested; costs are attributed per pipeline and stay within
budget; the platform can be rolled back and rebuilt; and someone else can
operate it from the documentation.

It is written as a sequence of **milestones**. Each milestone has a goal,
tasks, deliverables, and **acceptance criteria**. Commit and tag the
repository at the end of each milestone (`m0`, `m1`, …).

> **Cost warning:** some services in this project bill by the hour
> (Redshift Serverless base capacity while in use, DMS, interface VPC
> endpoints, NAT gateways if you add one, RDS). Set a project budget with
> alerts before M1, prefer on-demand and serverless options, keep resource
> sizes minimal, **destroy dev resources at the end of every session**, and
> verify teardown. Always check current pricing and free-tier terms.

> **Change warning:** AWS service names, features, and limits change often.
> Confirm details in the current documentation before implementing each
> milestone.

---

## 1. Why this project matters

A serverless lakehouse is one of the most common AWS data architectures:
S3 for storage, Glue for catalog and ETL, Athena for SQL, Lake Formation for
governance, Kinesis/Firehose for streams, DMS for replication, and Step
Functions for orchestration. The individual services are easy to try; the
**integration** is what employers pay for:

- data landing in the wrong place with the wrong permissions;
- crawlers creating surprise tables;
- Athena bills exploding from unpartitioned raw data;
- analysts seeing PII because permissions were set in two places;
- a Glue job silently reprocessing everything;
- no alert when a DMS task stops;
- costs nobody can attribute — and resources left running after the demo.

This project makes you build the whole platform end to end with the
discipline of a production team.

---

## 2. Project goal and scope

### Goal

Build `shoplite-aws-lakehouse`, which provides:

1. **Foundations**: account safety, Terraform state, environments, tagging,
   budgets, and CI/CD with OIDC.
2. **Storage and catalog**: encrypted buckets, Iceberg tables (in S3 Tables
   or general-purpose buckets), and a Glue Data Catalog defined as code.
3. **Three ingestion paths**:
   - **partner files** → S3 events → Step Functions validation → bronze;
   - **orders database** (RDS PostgreSQL) → **DMS** CDC → S3 → merged into
     Iceberg silver;
   - **click events** → **Kinesis** → **Firehose** → bronze.
4. **Transformations**: Glue Spark jobs bronze → silver → gold with **Glue
   Data Quality** gates and an SCD Type 2 customer dimension; one heavy job
   compared on **EMR Serverless**.
5. **Orchestration**: Step Functions with EventBridge schedules and events,
   retries, alerts, and backfills.
6. **Serving**: Athena workgroups with scan limits and **Redshift
   Serverless** for BI-style queries.
7. **Governance and security**: Lake Formation with LF-Tags, row filters,
   and PII column restrictions; KMS; private networking with VPC endpoints;
   Secrets Manager; CloudTrail audit; a GDPR deletion procedure.
8. **Operations**: CloudWatch dashboards and alarms, cost per pipeline,
   table maintenance, runbook, incident drills, and rollback/rebuild drills.
9. **Evidence**: architecture diagram, ADRs, cost report, and a verified
   teardown.

### In scope

- All AWS resources in Terraform (or OpenTofu), Python for jobs and tools,
  SQL for Athena and Redshift, GitHub Actions for CI/CD.

### Out of scope

- A BI tool build-out (optional stretch goal), multi-region disaster
  recovery, and MSK/Managed Flink (stretch goals).

---

## 3. Prerequisites and timing

- **Gap Module G3** completed (or in progress, following the milestone
  order), plus Stage 2 Modules 2.9–2.20.
- Helpful: Stage 2 Projects 02 (CDC) and 04 (medallion) for logic you can
  reuse.
- An AWS account used only for learning, with MFA and single sign-on or
  assumed roles.

**Estimated effort:** about **3–4 weeks** at 8–10 hours per week (spread
across short, torn-down sessions to control cost).

---

## 4. Requirements and service levels (write them down in M0)

| Requirement | Target |
| --- | --- |
| **Freshness** | Partner files in silver within 30 minutes of arrival; orders changes in silver within 1 hour (DMS + hourly merge); click events in bronze within 10 minutes; gold published daily by 07:00 (UTC or your chosen zone) |
| **Correctness** | Silver orders reconcile with the source database; gold revenue reconciles with silver; no duplicate keys in silver/gold |
| **Quality** | Critical Data Quality rules block gold publication; failing rows quarantined |
| **Security** | Least-privilege roles per workload; customer-managed KMS keys for silver/gold; private data paths via VPC endpoints; no long-lived keys |
| **Governance** | Analysts see only permitted rows and columns in Athena and Redshift Spectrum; access audited |
| **Operability** | Every failure triggers an alert with context; one dashboard shows platform health |
| **Cost** | A total project budget (e.g. a small fixed monthly amount you choose) and cost per pipeline visible from tags |
| **Recoverability** | Gold tables can be rolled back to a previous snapshot in minutes; the dev environment can be destroyed and recreated from code |

---

## 5. Target architecture

```text
 SOURCES                      INGESTION                              LAKEHOUSE (S3 + Iceberg + Glue Catalog)
 ───────                      ─────────                              ───────────────────────────────────────
 Partner (S3 upload) ──► landing/ ─EventBridge─► Step Functions ──► bronze.partner_* (Iceberg)
                                                (validate, quarantine,
                                                 register, load)
 RDS PostgreSQL ────► DMS (full load + CDC) ──► s3://…/dms/ ──► Glue merge job ──► silver.orders, silver.customers
 (orders service)
 Click producer ───► Kinesis Data Streams ───► Data Firehose ──► bronze.click_events (Iceberg or partitioned Parquet)

                                   Glue Spark jobs + Glue Data Quality (EMR Serverless for one heavy job)
                                   bronze ─► silver (typed, deduped, SCD2) ─► gold (facts, aggregates)

 ORCHESTRATION   Step Functions (daily + hourly) · EventBridge rules & Scheduler · SNS alerts
 SERVING         Athena workgroups (analytics, etl) · Redshift Serverless (gold via COPY or Spectrum)
 GOVERNANCE      Lake Formation (LF-Tags, row filters, column restrictions) · CloudTrail data events on gold
 SECURITY        KMS keys per layer · private subnets + S3 gateway endpoint + required interface endpoints · Secrets Manager
 OPERATIONS      CloudWatch dashboard & alarms · cost allocation tags & budgets · table maintenance · runbook
 DELIVERY        Terraform (dev, prod) · GitHub Actions with OIDC · tests · teardown script
```

### Key decisions to record as ADRs (M0)

- Iceberg in **S3 Tables** vs in **general-purpose buckets** (managed
  maintenance vs control and portability).
- **Step Functions** vs MWAA for orchestration.
- **DMS** vs zero-ETL vs self-managed Debezium for the orders database.
- **Kinesis + Firehose** vs MSK for click events.
- **Athena-only** vs Athena + **Redshift Serverless** for serving.
- Environment strategy: separate AWS accounts vs one account with
  separate prefixes, catalogs, and state.

---

## 6. Repository structure

```text
shoplite-aws-lakehouse/
├── README.md
├── infra/
│   ├── bootstrap/                 # state bucket, OIDC provider, CI roles (applied once)
│   ├── modules/                   # storage, catalog, kms, network, lakeformation, ingestion, glue, stepfunctions, redshift, observability, budgets
│   └── envs/
│       ├── dev/                   # dev configuration (small sizes, teardown-friendly)
│       └── prod/                  # prod configuration (approval-gated)
├── src/
│   ├── glue_jobs/                 # bronze→silver→gold, DMS merge, maintenance
│   ├── lambdas/                   # file validation, quarantine, alert formatting
│   ├── producers/                 # click-event producer, orders workload generator
│   └── common/                    # shared transformation functions (pure, testable)
├── statemachines/                 # Step Functions definitions (ASL JSON/YAML)
├── sql/
│   ├── athena/                    # DDL, views, maintenance, audit queries
│   └── redshift/                  # schema, COPY/MERGE, WLM, data sharing
├── dq/                            # Glue Data Quality rulesets (DQDL)
├── tests/
│   ├── unit/                      # pytest, moto
│   ├── glue_local/                # tests run in the Glue local container
│   └── e2e/                       # smoke tests against dev
├── scripts/
│   ├── teardown.sh                # destroy + verification of no billable leftovers
│   └── cost_report.py             # cost per pipeline from billing data
├── docs/
│   ├── requirements.md  architecture.md  data-model.md  access-matrix.md
│   ├── runbook.md  cost-log.md  incidents/  adr/
└── .github/workflows/             # ci.yml (PR), deploy-dev.yml (merge), deploy-prod.yml (approval)
```

---

## 7. Milestones overview

```text
M0   Framing: requirements, data products, budget, and decisions
M1   Account and delivery foundations
M2   Storage and catalog
M3   Security and network baseline
M4   Ingestion A — partner files
M5   Ingestion B — orders database CDC with DMS
M6   Ingestion C — click events with Kinesis and Firehose
M7   Transformations and data quality with Glue
M8   Orchestration, reruns, and backfills
M9   Serving: Athena and Redshift Serverless
M10  Governance: Lake Formation, audit, and GDPR deletion
M11  Observability, maintenance, and cost
M12  Testing and CI/CD across environments
M13  Reliability: rollback, rebuild, and incident drills
M14  Documentation, cost report, teardown, and hand-over
(M15 Optional stretch goals)
```

---

## 8. Milestones

### M0 — Framing: requirements, data products, budget, and decisions

**Goal:** Know what you are building, for whom, at what cost, and why each
service was chosen.

**Tasks**

1. Write `docs/requirements.md` with the SLAs from Section 4, consumers
   (finance, marketing, analysts), and non-goals.
2. Define **data products**: `gold.daily_revenue`, `gold.customer_ltv`,
   `gold.funnel_daily`, `gold.dim_customer` (SCD2), with owners and
   consumers.
3. Choose a **region** (service availability, price, latency) and write a
   **cost estimate** per milestone and per month (Topic 01 of G3, Module
   2.21).
4. Write the ADRs listed in Section 5.
5. Draw the architecture in `docs/architecture.md`.

**Acceptance criteria**

- [ ] SLAs, data products, and owners are written.
- [ ] A cost estimate exists and fits your budget.
- [ ] Every major service choice has an ADR with alternatives.

---

### M1 — Account and delivery foundations

**Goal:** A safe account and a delivery pipeline before any data resource
exists.

**Tasks**

1. Account safety: MFA on the root user, root not used, single sign-on or
   assumed roles for yourself, **AWS Budgets** with email alerts (e.g. at
   50%, 80%, 100%), and **cost allocation tags** activated (`project`,
   `environment`, `pipeline`, `owner`).
2. `infra/bootstrap`: an S3 bucket for Terraform state (versioned,
   encrypted, with state locking), and a **GitHub OIDC identity provider**
   with CI roles (plan role for pull requests, apply role for deploys).
3. Environment layout: `dev` and `prod` with separate state and naming (or
   separate accounts, per your ADR).
4. Default tags on every resource via the Terraform provider.
5. `scripts/teardown.sh`: destroy the dev environment and **verify** no
   tagged billable resources remain (e.g. by querying tagged resources and
   listing known hourly-billed services).
6. A first CI workflow: `terraform fmt`, `validate`, a linter, a security
   scanner, and `plan` on pull requests using OIDC (no stored keys).

**Acceptance criteria**

- [ ] No long-lived access keys exist for you or CI.
- [ ] Budgets alert by email; tags appear on all resources.
- [ ] A pull request shows a Terraform plan; teardown verifies a clean
      account.

---

### M2 — Storage and catalog

**Goal:** Well-structured, encrypted storage and a catalog defined entirely
as code.

**Tasks**

1. Buckets (via a storage module): `landing`, `lake` (bronze/silver/gold
   prefixes, or a table bucket for S3 Tables), `quarantine`,
   `athena-results`, `logs` — all with **blocked public access**,
   **versioning** where needed, **default encryption** (KMS keys from M3),
   **TLS-only bucket policies**, and **lifecycle rules** (expire temp and
   Athena results; expire noncurrent versions on landing after N days).
2. Glue **databases** `bronze`, `silver`, `gold`, `quarantine`; Iceberg
   table definitions for core tables created as code (or through
   Terraform-run DDL), with explicit schemas and partition specs.
3. **Partition projection** for any raw, non-Iceberg tables (e.g. landing
   JSON by date).
4. Access points for `ingestion` (write landing) and `analytics` (read gold
   via Lake Formation later).
5. Document the data model in `docs/data-model.md` (tables, grain, keys,
   partitioning, retention).

**Acceptance criteria**

- [ ] No bucket is public; non-TLS requests are denied.
- [ ] All tables exist from code with explicit schemas; no crawlers on
      contracted datasets.
- [ ] Lifecycle rules keep temporary storage from growing.

---

### M3 — Security and network baseline

**Goal:** Every workload has its own least-privilege identity, data is
encrypted with controlled keys, and processing traffic stays private.

**Tasks**

1. **KMS**: customer-managed keys for `silver` and `gold` (and optionally
   `bronze`), with key policies naming only the roles that need them; S3
   Bucket Keys enabled.
2. **IAM roles** per workload: partner validator, DMS, Firehose, each Glue
   job family, Step Functions, Redshift, Athena ETL, and analyst personas —
   documented in `docs/access-matrix.md`.
3. **Network**: a VPC with private subnets for Glue connections, DMS, and
   RDS; an **S3 gateway endpoint**; only the **interface endpoints**
   genuinely needed (e.g. Glue, STS, Secrets Manager, CloudWatch Logs) —
   and a cost note for each; no NAT gateway unless justified in an ADR.
4. **Secrets Manager** for the RDS credentials (with rotation configured
   where practical).
5. Bucket policies restricting the gold prefix to requests via your VPC
   endpoint or specific roles, as per your design.

**Acceptance criteria**

- [ ] Each role can do only its documented actions (spot-check with access
      tests and the IAM policy simulator).
- [ ] Glue jobs and DMS run in private subnets without a NAT gateway (or
      with a justified one).
- [ ] Decrypting gold data fails for roles not in the key policy.

---

### M4 — Ingestion A: partner files

**Goal:** Partner files are validated, deduplicated, and loaded — or
quarantined with a reason — automatically.

**Tasks**

1. Partners upload CSV files plus a manifest (row count, checksum) to
   `landing/partner/<partner>/<date>/` (simulate with a script).
2. An **EventBridge** rule on object creation (manifest arrival) starts a
   **Step Functions** workflow:
   - validate the manifest and file (Lambda or Glue Python shell):
     checksum, row count, schema, required columns;
   - check the **file registry** (DynamoDB or an Iceberg table) to ensure
     each file version is processed once;
   - on failure: move to `quarantine/` with a reason and alert;
   - on success: start a Glue job loading into `bronze.partner_shipments`
     (Iceberg, with provenance columns).
3. Make the workflow **idempotent** (same object and ETag → no-op) and
   handle corrected re-sends per the partner contract.

**Acceptance criteria**

- [ ] A valid file reaches bronze within the SLA; duplicates are ignored.
- [ ] Invalid files are quarantined with a reason and an alert.
- [ ] Re-sent corrected files replace earlier versions per the contract.

---

### M5 — Ingestion B: orders database CDC with DMS

**Goal:** Every insert, update, and delete in the orders database reaches
silver correctly.

**Tasks**

1. Create a small **RDS PostgreSQL** instance in private subnets with
   logical replication enabled and a least-privilege replication user
   (secret in Secrets Manager); run a workload generator (inserts, updates,
   deletes) from Stage 2 Project 02 or G3 Topic 11.
2. Configure **DMS** (Serverless or a small replication instance): full
   load + CDC to S3 in Parquet with operation and commit-timestamp columns;
   table mappings; validation enabled.
3. Build a **Glue merge job** (hourly) that reads new DMS files,
   deduplicates by key using the commit order, and `MERGE`s into Iceberg
   `silver.orders` and `silver.customers`, applying deletes (Module 2.15).
4. Reconcile row counts and key sets between RDS and silver (Module 2.11).
5. Monitor DMS task status and latency, and the source replication slot.

**Acceptance criteria**

- [ ] After workload bursts, silver equals the source at reconciliation
      time, including deletes.
- [ ] Re-running a merge for the same files changes nothing.
- [ ] A stopped DMS task triggers an alert (M11).

---

### M6 — Ingestion C: click events with Kinesis and Firehose

**Goal:** Click events stream into the lake reliably, partitioned and
queryable within minutes.

**Tasks**

1. Create an **on-demand Kinesis** data stream; write a Python producer
   sending click events with `PutRecords`, retrying only failed records,
   keyed to avoid hot shards.
2. Create a **Firehose** stream from Kinesis to the lake:
   - either to an **Iceberg table** (`bronze.click_events`), or to
     partitioned Parquet using **dynamic partitioning** by event date and
     **format conversion** with a Glue schema;
   - buffering tuned to avoid tiny files;
   - an error output prefix and encryption with your KMS key.
3. Query click events in Athena within the freshness SLA.
4. Monitor iterator age and delivery errors (M11).

**Acceptance criteria**

- [ ] Events appear in bronze within 10 minutes.
- [ ] Output files are reasonably sized and partitioned.
- [ ] Failed records are retried or captured, never silently lost.

---

### M7 — Transformations and data quality with Glue

**Goal:** Silver and gold tables are correct, incremental, idempotent, and
never published with critical quality failures.

**Tasks**

1. Put transformation logic in `src/common/` as **pure functions** tested
   locally, used by Glue job entry points.
2. Glue Spark jobs:
   - `bronze_to_silver_clicks`: parse, dedupe by event id, sessionise, flag
     bots;
   - `silver_dim_customer_scd2`: SCD Type 2 with hash diffs from
     `silver.customers` changes;
   - `silver_to_gold`: `fct_orders` with point-in-time customer versions,
     `gold.daily_revenue`, `gold.customer_ltv`, `gold.funnel_daily` —
     recomputing only affected dates (Module 2.12).
3. **Glue Data Quality** rulesets per table (completeness, uniqueness,
   ranges, referential integrity, freshness); **critical** rules fail the
   job before publication; failing rows written to `quarantine/`.
4. **Write–audit–publish** for gold: write results to staging tables (or an
   Iceberg branch where your engines support it), run quality checks, then
   publish with `MERGE`/overwrite of affected partitions.
5. Use **job parameters** for the data interval; no "now" inside logic;
   rerunning a day gives identical results.
6. Run the heaviest job (e.g. a full rebuild of `fct_orders`) on **EMR
   Serverless** as well and compare time and cost with Glue (G3 Topic 09).

**Acceptance criteria**

- [ ] Rerunning any job for the same interval changes nothing.
- [ ] An injected defect (e.g. amounts ×100, duplicate orders) is blocked
      from gold and alerted.
- [ ] SCD Type 2 integrity checks pass; gold reconciles with silver.
- [ ] A Glue vs EMR Serverless comparison is documented.

---

### M8 — Orchestration, reruns, and backfills

**Goal:** Pipelines run themselves on schedules and events, recover from
transient failures, and can reprocess history safely.

**Tasks**

1. **Step Functions** state machines:
   - `hourly`: DMS merge → silver clicks → quality checks;
   - `daily`: SCD2 → gold build (write) → quality (audit) → publish →
     notify; with `Choice` states on quality results;
   - native "run job and wait" integrations for Glue and Athena, retries
     with backoff, and catchers routing failures to an SNS alert with
     context.
2. **EventBridge Scheduler** for hourly and daily runs; a **date
   parameter** for reruns.
3. A **backfill** state machine using a **Map** state over a date range
   with bounded concurrency, not interfering with daily runs.
4. Prevent overlapping runs (execution-name conventions or checks).

**Acceptance criteria**

- [ ] Daily gold is published by the SLA deadline without manual steps.
- [ ] A transient Glue failure is retried automatically; a permanent failure
      alerts once with context.
- [ ] A 30-day backfill completes with correct results.

---

### M9 — Serving: Athena and Redshift Serverless

**Goal:** Analysts get fast, cheap, controlled access to gold data.

**Tasks**

1. **Athena workgroups**: `analytics` (enforced result location and
   encryption, per-query scan limit) and `etl`; saved queries and views for
   common questions.
2. Measure bytes scanned for ten typical queries; improve layout
   (partitioning, sorting/compaction) where needed.
3. **Redshift Serverless** with a low base capacity and a maximum capacity
   limit: load gold facts and dimensions with `COPY` (or query via
   **Spectrum** through the Glue Catalog); design distribution and sort keys
   for the star schema; add workload-management rules.
4. Compare cost and performance of the same dashboards-style queries in
   Athena and Redshift; write a serving recommendation.

**Acceptance criteria**

- [ ] Analysts cannot run queries above the scan limit.
- [ ] Typical queries run within agreed times and costs.
- [ ] The Athena vs Redshift recommendation is backed by measurements.

---

### M10 — Governance: Lake Formation, audit, and GDPR deletion

**Goal:** Fine-grained, tested, auditable access — and a proven way to
delete a person's data.

**Tasks**

1. Move catalog permissions to **Lake Formation** deliberately (review
   default permissions and hybrid access).
2. **LF-Tags** (`domain`, `layer`, `classification`) on databases, tables,
   and PII columns; grants by tag to personas: data engineer, finance
   analyst, marketing analyst.
3. A **row filter** so a regional analyst sees only their region; PII
   columns hidden from marketing.
4. **Access tests** (automated): run queries as each persona role and
   assert visible rows and columns.
5. **CloudTrail data events** for the gold prefix; Athena queries over the
   trail answering "who accessed PII last week?".
6. **GDPR deletion procedure**: delete a customer in the source database
   (flows via DMS), delete from Iceberg silver/gold with `DELETE`, **expire
   snapshots** and **remove orphan files** (or rely on S3 Tables
   maintenance), delete from quarantine and landing, and expire **noncurrent
   S3 object versions**; verify with a scan; record a deletion log.

**Acceptance criteria**

- [ ] Each persona sees exactly the permitted rows and columns (tests pass).
- [ ] Access to gold is auditable from CloudTrail.
- [ ] A deleted customer's data is provably gone from all current and
      historical storage after the procedure.

---

### M11 — Observability, maintenance, and cost

**Goal:** You know the platform's health and cost at a glance, and tables
stay fast and cheap.

**Tasks**

1. **CloudWatch alarms** (routed to SNS/email/chat): Glue job failures (via
   EventBridge job-state events), Step Functions failed executions, Data
   Quality failures, Kinesis iterator age, Firehose delivery errors, DMS
   task failures and latency, Redshift query queue time, Athena workgroup
   scanned bytes.
2. A **CloudWatch dashboard** for the platform and three **Logs Insights**
   queries for incident investigation.
3. **Table maintenance**: scheduled Iceberg compaction and snapshot expiry
   (Athena `OPTIMIZE`/`VACUUM`, Glue/EMR jobs, or S3 Tables automatic
   maintenance) with retention aligned to rollback needs.
4. **Cost**: cost per pipeline and environment from tags (Cost Explorer or
   billing exports queried with Athena via `scripts/cost_report.py`);
   budgets per environment; a monthly cost log comparing estimate vs
   actual.
5. Identify and implement at least **two cost optimisations** (e.g. Glue
   Flex for non-urgent jobs, smaller Redshift max capacity, removing an
   unused interface endpoint, better Firehose buffering).

**Acceptance criteria**

- [ ] Every failure type from M4–M9 triggers an alarm.
- [ ] Table health (files, snapshots) stays within targets.
- [ ] Cost per pipeline is reported and within budget; two optimisations
      show measured savings.

---

### M12 — Testing and CI/CD across environments

**Goal:** Changes are tested automatically and promoted safely from dev to
prod.

**Tasks**

1. **Unit tests**: transformation functions (pytest, small DataFrames),
   Lambda handlers, and boto3 code with **moto**.
2. **Glue local tests**: run Glue job entry points in the Glue local
   development container against sample data.
3. **Infrastructure checks**: `fmt`, `validate`, linting, and a security
   scanner on every pull request; plan output posted to the pull request.
4. **Deployment**: merge → apply `dev` → upload job scripts and state
   machines → run an **end-to-end smoke test** (drop a partner file, produce
   click events, run the daily workflow, assert gold rows and quality
   results) → promote to `prod` after manual approval.
5. **Rollback**: redeploy the previous version of jobs and state machines;
   restore data with Iceberg time travel (M13).

**Acceptance criteria**

- [ ] A failing unit test or security finding blocks the merge.
- [ ] The end-to-end smoke test passes in dev before prod deployment.
- [ ] Prod deployments require approval and use OIDC roles only.

---

### M13 — Reliability: rollback, rebuild, and incident drills

**Goal:** Mistakes and failures are recoverable within minutes — and you
have practised it.

**Tasks**

1. **Data rollback drill**: publish a bad gold version on purpose; detect
   it; roll back the Iceberg table to the previous snapshot; verify; record
   time taken.
2. **Rebuild drill**: destroy the dev environment and rebuild from code
   (infrastructure, jobs, catalog); reload sample data; run the smoke test;
   record time taken and gaps.
3. **Incident drills** (each with a timeline from CloudWatch/CloudTrail and
   a short post-mortem in `docs/incidents/`):
   - a malformed partner file burst;
   - a schema change in the source database (new column) flowing through
     DMS;
   - a stopped DMS task;
   - Kinesis throttling from a hot key;
   - a Glue job role losing a permission;
   - a KMS key policy change blocking reads.
4. Update the runbook and alarms with every lesson.

**Acceptance criteria**

- [ ] Gold rollback completes in minutes and is verified.
- [ ] The dev environment rebuilds from code with a documented time.
- [ ] Every drill has a timeline, a fix, and an implemented prevention.

---

### M14 — Documentation, cost report, teardown, and hand-over

**Goal:** Someone else can understand, operate, and pay for the platform —
and you leave nothing running.

**Tasks**

1. Finalise the **README**: architecture diagram, data products, how to
   deploy, how to run and backfill, how to access data, how to tear down.
2. Finalise the **runbook**: daily checks, each alarm and its response,
   backfills, rollbacks, GDPR deletions, credential rotation, and teardown.
3. Write the **cost report**: estimate vs actual per milestone and per
   pipeline, the biggest cost drivers, optimisations, and a projected
   monthly cost at production scale.
4. Run the **teardown** and verify: no tagged resources, no hourly-billed
   services remaining, budgets at zero growth for the next days.
5. **Hand-over test**: another person (or a fresh role) deploys dev, runs
   the smoke test, handles one alarm, and tears down using only the docs.
6. Write a **retrospective**: what you would change, and how the design
   would differ on Databricks (G4) or with MSK/zero-ETL.

**Acceptance criteria**

- [ ] The hand-over test succeeds.
- [ ] The cost report is complete and matches billing data.
- [ ] Teardown is verified — nothing billable remains.

---

### M15 — Optional stretch goals

- **S3 Tables vs general-purpose Iceberg:** implement both for one table and
  compare maintenance effort and cost.
- **Zero-ETL:** replace DMS for one table with a zero-ETL integration where
  available, and compare.
- **MSK and Managed Flink:** a real-time aggregation path for click events.
- **Business catalog:** publish gold data products in SageMaker Unified
  Studio / DataZone and approve a subscription (G3 Topic 14).
- **Multi-account:** split ingestion, lake, and analytics into separate
  accounts with cross-account Lake Formation sharing.
- **Dashboards:** a small BI dashboard on Athena or Redshift.

---

## 9. Definition of done

- [ ] Everything — infrastructure, jobs, state machines, catalog,
      permissions — is created from code in dev and prod.
- [ ] Three ingestion paths meet their freshness SLAs.
- [ ] Silver and gold are correct, reconciled, idempotent, and protected by
      quality gates.
- [ ] Orchestration handles schedules, events, retries, alerts, and
      backfills.
- [ ] Analysts are served through controlled Athena workgroups and Redshift
      Serverless.
- [ ] Lake Formation permissions are fine-grained, tag-based, tested, and
      audited; GDPR deletion is proven.
- [ ] KMS, private networking, Secrets Manager, and least-privilege roles
      throughout.
- [ ] Alarms, dashboard, table maintenance, and cost per pipeline in place;
      within budget.
- [ ] CI/CD with OIDC, unit and end-to-end tests, and approval-gated prod.
- [ ] Rollback, rebuild, and incident drills completed.
- [ ] README, ADRs, runbook, cost report, retrospective; teardown verified.

---

## 10. Evaluation rubric (self or peer review)

Score each area from 0 to 3. A production-grade project scores **at least 2
in every area** and **3 in Security, Correctness, and Cost control**.

| Area | What a "3" looks like |
| --- | --- |
| Architecture and decisions | Clear diagram; ADRs for every major choice with measured evidence |
| Infrastructure as code | 100% Terraform, environments, OIDC, verified teardown |
| Ingestion | Three paths meeting SLAs; idempotent; failures quarantined and alerted |
| Correctness | Reconciliation, SCD2 integrity, idempotent reruns, WAP |
| Data quality | Glue Data Quality gates with critical/non-critical rules and quarantine |
| Security | Least privilege, KMS per layer, private paths, secrets managed, no static keys |
| Governance | LF-Tags, row/column controls, access tests, CloudTrail audit, proven deletion |
| Operations | Alarms for every failure mode, dashboard, maintenance, drills |
| Cost control | Estimates, tags, budgets, per-pipeline costs, measured optimisations |
| Delivery | CI with tests and scans, e2e smoke test, approval-gated prod, rollback |
| Documentation | Hand-over test passed from docs alone |

---

## 11. Common pitfalls to avoid

- Creating resources in the console and never capturing them in code.
- Long-lived access keys for yourself or CI.
- Crawlers on production prefixes creating surprise tables.
- Athena queries on raw JSON/CSV without partitions or scan limits.
- Permissions granted both in IAM and Lake Formation, so tests pass for the
  wrong reason.
- Forgetting KMS permissions in job roles (mysterious access-denied errors).
- A NAT gateway (or interface endpoints) left running between sessions.
- Not expiring S3 noncurrent versions and Iceberg snapshots — so "deleted"
  data remains.
- Glue job bookmarks treated as the only incremental state without
  reconciliation.
- Declaring the project finished without a verified teardown.

---

## 12. Suggested timeline

| Week | Milestones |
| --- | --- |
| 1 | M0 framing · M1 foundations · M2 storage and catalog · M3 security and network |
| 2 | M4 partner files · M5 DMS CDC · M6 Kinesis and Firehose |
| 3 | M7 Glue transformations and quality · M8 orchestration · M9 serving |
| 4 | M10 governance · M11 observability and cost · M12 CI/CD · M13 drills · M14 docs and teardown |
| Optional | M15 stretch goals |

Work in short sessions and tear down dev resources after each one; recreate
them from code at the start of the next session (this also proves your
infrastructure code).

---

## 13. What to show in a portfolio or interview

Be ready to explain:

1. The architecture and why each AWS service was chosen over alternatives.
2. How partner files, database changes, and click events are ingested
   reliably and idempotently.
3. How Glue jobs stay incremental, idempotent, and quality-gated.
4. How Lake Formation enforces row and column security, and how you tested
   it.
5. How data is encrypted and kept on private network paths.
6. How you would detect and respond to a stopped DMS task or a bad gold
   publication.
7. What the platform costs per pipeline, and how you reduced it.
8. How a customer's data is deleted everywhere — including old versions.
9. How the whole platform is deployed, promoted, rolled back, and torn down
   from code.

A README with the architecture diagram, a short demo (partner file →
quality gate → gold → analyst query with row-level security → rollback →
teardown), the cost report, and the ADRs make this a strong AWS data
engineering portfolio piece — and a solid base for the capstone on AWS.
