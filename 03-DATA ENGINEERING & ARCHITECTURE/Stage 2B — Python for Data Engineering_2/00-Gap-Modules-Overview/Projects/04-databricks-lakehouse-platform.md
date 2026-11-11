# Project Roadmap — Databricks Lakehouse Platform

This is the end-to-end roadmap for **Gap Project 04: Databricks Lakehouse
Platform**, the project for **Gap Module G4 — Databricks Lakehouse Platform
Deep Dive**. It takes you from an empty Databricks workspace to a
**production-grade lakehouse** that ingests files and database changes,
builds governed bronze/silver/gold tables with declarative pipelines,
orchestrates everything with Lakeflow Jobs, serves analysts and business
users, shares data with a partner, hands features to ML — and is deployed
entirely as code with Databricks Asset Bundles, with costs attributed from
system tables.

"Production grade" here means: every job, pipeline, and permission is
defined as code and deployed by CI/CD as a service principal; all data is
governed in Unity Catalog with tested row- and column-level controls; bad
data is handled by explicit expectations; failures alert a human and can be
repaired; tables can be rolled back; costs are visible per pipeline; and
someone else can operate the platform from the documentation.

It is written as a sequence of **milestones**. Each milestone has a goal,
tasks, deliverables, and **acceptance criteria**. Commit and tag the
repository at the end of each milestone (`m0`, `m1`, …).

> **Environment note:** you can complete most milestones on **Databricks
> Free Edition** (serverless-only, with limits). Some account-level features
> (e.g. external locations, some system tables, identity federation for CI,
> Lakeflow Connect sources) may require a cloud trial or company sandbox
> workspace. Where a feature is unavailable, implement the closest
> alternative and document the gap — never skip the concept.

> **Change warning:** Databricks product names, APIs, and limits change
> often (e.g. Lakeflow Declarative Pipelines, Lakeflow Jobs, Git folders,
> compute access modes). Check the current documentation for each
> milestone.

> **Cost warning:** on paid workspaces, prefer serverless compute and small
> SQL warehouses with auto-stop, enforce compute policies and budget
> policies, and delete or pause everything after each session.

---

## 1. Why this project matters

Databricks gives you a lot out of the box — which makes it easy to build a
platform that "works" but is ungoverned, click-configured, expensive, and
impossible to promote between environments. Common real-world problems:

- production jobs running on personal all-purpose clusters as individual
  users;
- tables in the wrong catalog with permissions granted to people instead of
  groups;
- PII visible to every analyst;
- pipelines that fail on one bad record — or silently accept all of them;
- nobody can say which job doubled the bill;
- notebooks as the only copy of production logic;
- no way to reproduce the dev set-up in prod.

This project makes you build the platform the way a mature Databricks team
would.

---

## 2. Project goal and scope

### Goal

Build `shoplite-databricks-lakehouse`, which provides:

1. **Foundations**: groups and service principals, catalogs per
   environment, compute and budget policies, secret scopes, and a bundle-based
   repository with CI/CD.
2. **Unity Catalog governance**: bronze/silver/gold schemas, landing
   volumes, group-based grants, tags, row filters, and column masks.
3. **Ingestion**: **Auto Loader** for clickstream and partner files;
   **Lakeflow Connect** (or a CDC feed) for orders and customers.
4. **A declarative pipeline** (Lakeflow Declarative Pipelines) with
   expectations (warn/drop/fail), automatic CDC with **SCD Type 1 and 2**,
   and gold materialized views.
5. **Orchestration** with **Lakeflow Jobs**: file-arrival and scheduled
   triggers, for-each ingestion, quality and reconciliation tasks,
   conditional publish, alerts, and repair runs — as a service principal.
6. **Analytics**: a serverless SQL warehouse, AI/BI dashboards, SQL alerts,
   certified metrics, and an evaluated **Genie** space.
7. **Sharing**: a partner **Delta Share** without PII.
8. **ML handoff**: a feature table, a point-in-time training set, an MLflow
   model registered in Unity Catalog, and a batch-scoring job.
9. **Delivery**: everything in a **Databricks Asset Bundle** with dev and
   prod targets, deployed by CI/CD.
10. **Operations**: cost per pipeline from **system tables**, performance
    tuning (Photon, liquid clustering, predictive optimization), audit,
    drills, runbook, and hand-over.

### In scope

- Databricks platform features from Gap Module G4, Python and SQL code,
  bundles, CI/CD, and the Databricks CLI (and Terraform for workspace-level
  objects where available).

### Out of scope

- Workspace and cloud network provisioning beyond what your environment
  allows (document it), multi-workspace disaster recovery, and vector
  search/RAG (stretch goals).

---

## 3. Prerequisites and timing

- **Gap Module G4** completed (or in progress, following milestone order),
  plus Stage 2 Modules 2.12–2.20.
- Helpful: Stage 2 Projects 03 (ELT and tests) and 04 (medallion logic) for
  reusable business rules.
- A Databricks workspace (Free Edition, trial, or sandbox) and a GitHub
  repository.

**Estimated effort:** about **3–4 weeks** at 8–10 hours per week.

---

## 4. Requirements and service levels (write them down in M0)

| Requirement | Target |
| --- | --- |
| **Freshness** | Partner files in silver within 30 minutes of arrival; clickstream in silver within 1 hour; orders/customers changes in silver within 1 hour; gold refreshed daily by 07:00 |
| **Correctness** | Silver orders reconcile with the source; gold revenue reconciles with silver; SCD Type 2 integrity holds |
| **Quality** | Expectations: critical rules fail the update, invalid rows dropped and counted, suspicious values warned; quality metrics visible |
| **Governance** | All objects in Unity Catalog; grants only to groups and service principals; PII masked for non-privileged groups; regional row filtering |
| **Security** | No personal access tokens in CI; secrets in secret scopes; production runs as a service principal |
| **Operability** | Every failure alerts with context; failed runs can be repaired; tables can be restored |
| **Cost** | Cost per pipeline and per environment visible daily from system tables; within a set budget |
| **Delivery** | The whole platform deploys to a fresh target from the bundle in one command |

---

## 5. Target architecture

```text
 SOURCES                        INGESTION                     UNITY CATALOG (catalogs: dev_shop, prod_shop)
 ───────                        ─────────                     ───────────────────────────────────────────
 Clickstream JSON ──► volume landing/clicks ──► Auto Loader ──► bronze.clicks          (streaming table)
 Partner CSV      ──► volume landing/partner ─► Auto Loader ──► bronze.partner_*       (streaming tables)
 Orders DB        ──► Lakeflow Connect (CDC) ──────────────────► bronze.orders_cdc, bronze.customers_cdc
                      (or a CDC feed landed as files + Auto Loader)

                    Lakeflow Declarative Pipeline (expectations, automatic CDC)
                    bronze ─► silver.orders (SCD1) · silver.dim_customer (SCD2) · silver.clicks (clean, sessions)
                           ─► gold.daily_revenue · gold.customer_ltv · gold.funnel_daily  (materialized views)

 ORCHESTRATION  Lakeflow Job (file arrival + daily schedule): for-each partner ingest → pipeline update
                → reconciliation SQL → if/else publish/alert → notify    (runs as service principal)
 ANALYTICS      Serverless SQL warehouse · AI/BI dashboard · SQL alerts · certified metrics · Genie space
 SHARING        Delta Share (filtered, PII-free view) → partner (open sharing)
 ML HANDOFF     features.customer_daily · point-in-time training set · MLflow model in UC · batch scoring job
 GOVERNANCE     groups, grants, tags, row filters, column masks, lineage, audit (system tables)
 OPERATIONS     system-table cost dashboard · alerts · Photon · liquid clustering · predictive optimization
 DELIVERY       Databricks Asset Bundle (dev, prod) · GitHub Actions · service principal via OIDC
```

### Key decisions to record as ADRs (M0)

- Declarative pipelines vs hand-written Structured Streaming + `MERGE` jobs
  (Project 04) vs dbt.
- Serverless vs classic compute per workload.
- Lakeflow Jobs vs an external orchestrator (Airflow).
- Lakeflow Connect vs other options for the orders database (a CDC feed from
  Debezium/Kafka as in Project 02, or files).
- Environment isolation: separate workspaces vs separate catalogs in one
  workspace.
- Managed vs external tables and volumes.

---

## 6. Repository structure

```text
shoplite-databricks-lakehouse/
├── README.md
├── databricks.yml                 # bundle: variables, targets (dev, prod)
├── resources/
│   ├── pipelines.yml              # declarative pipeline definitions
│   ├── jobs.yml                   # ingestion/orchestration, maintenance, ML scoring, cost jobs
│   └── other.yml                  # other bundle-managed resources as supported (e.g. dashboards, schemas)
├── src/shoplite/
│   ├── transforms/                # pure PySpark functions (sessionisation, bot rules, hashing)
│   ├── ingest/                    # Auto Loader helpers, partner configs
│   ├── quality/                   # reconciliation and custom checks
│   └── ml/                        # feature building, training set, scoring
├── pipelines/
│   ├── bronze.py / bronze.sql
│   ├── silver.py
│   └── gold.sql
├── sql/
│   ├── governance/                # catalogs, schemas, volumes, grants, tags, filters, masks
│   ├── analytics/                 # dashboard datasets, alerts, metric definitions
│   ├── sharing/                   # shares and recipients
│   └── ops/                       # cost, audit, and table-health queries on system tables
├── infra/                         # Terraform (optional): workspace-level objects, groups, service principals
├── tests/
│   ├── unit/                      # local Spark / pytest
│   └── integration/               # Databricks Connect / bundle-run smoke tests
├── docs/
│   ├── requirements.md  architecture.md  data-model.md  access-matrix.md
│   ├── runbook.md  cost-log.md  performance.md  genie-evaluation.md  incidents/  adr/
└── .github/workflows/             # ci.yml (PR), deploy-dev.yml (merge), deploy-prod.yml (approval)
```

---

## 7. Milestones overview

```text
M0   Framing: requirements, data products, environment, and decisions
M1   Workspace and delivery foundations
M2   Unity Catalog design and governance baseline
M3   Code organisation and local development
M4   Ingestion A — files with Auto Loader
M5   Ingestion B — orders and customers change data
M6   The declarative pipeline: expectations, CDC, and gold
M7   Orchestration with Lakeflow Jobs
M8   Fine-grained governance, audit, and GDPR deletion
M9   Performance: Photon, clustering, and predictive optimization
M10  Analytics: SQL warehouse, dashboards, alerts, metrics, and Genie
M11  Sharing and ML handoff
M12  Asset Bundles and CI/CD across environments
M13  Cost and observability with system tables
M14  Reliability drills and runbook
M15  Documentation, cost report, clean-up, and hand-over
(M16 Optional stretch goals)
```

---

## 8. Milestones

### M0 — Framing: requirements, data products, environment, and decisions

**Goal:** Know what you are building, for whom, where, and why.

**Tasks**

1. Write `docs/requirements.md` with SLAs (Section 4), consumers (finance,
   marketing, analysts, ML team, a partner), and non-goals.
2. Define **data products**: `gold.daily_revenue`, `gold.customer_ltv`,
   `gold.funnel_daily`, `silver.dim_customer` (SCD2), a partner share, and a
   customer feature table — with owners and consumers.
3. Record which Databricks features your environment supports (Free
   Edition, trial, or sandbox) and plan alternatives for missing ones.
4. Estimate cost (DBUs and any cloud infrastructure) and set a budget.
5. Write the ADRs listed in Section 5; draw the architecture.

**Acceptance criteria**

- [ ] SLAs, data products, owners, and feature availability are documented.
- [ ] A budget and cost estimate exist.
- [ ] ADRs cover every major choice.

---

### M1 — Workspace and delivery foundations

**Goal:** Identities, policies, and delivery tooling are in place before any
data lands.

**Tasks**

1. **Identities**: groups `data-engineers`, `analysts-finance`,
   `analysts-marketing`, `analysts-regional`, `ml-engineers`,
   `privacy-officers`; service principals `sp-ci-deploy` and `sp-prod-run`.
   Grant permissions only to groups and service principals.
2. **Compute governance**: compute policies (auto-termination, size limits,
   required tags) and, where available, **serverless budget policies** with
   tags for cost attribution; a small serverless SQL warehouse with
   auto-stop.
3. **Secrets**: a secret scope for source credentials; document who can read
   it.
4. **Repository**: bundle skeleton (`databricks.yml` with `dev` and `prod`
   targets and variables for catalog names), Git folder linked to the
   repository, `pre-commit` (Ruff, SQL linting, secret scanning).
5. **CI authentication**: configure the CI service principal with
   workload identity federation (OIDC) from GitHub where available;
   otherwise use short-lived OAuth credentials for the service principal and
   document the limitation. **No personal access tokens.**
6. Optional: manage groups and service principals with the Databricks
   Terraform provider.

**Acceptance criteria**

- [ ] No permission is granted to an individual user.
- [ ] Compute cannot be created without auto-termination and tags.
- [ ] `databricks bundle validate` passes for both targets in CI.

---

### M2 — Unity Catalog design and governance baseline

**Goal:** A clear, governed namespace for every object in the platform.

**Tasks**

1. Create catalogs `dev_shop` and `prod_shop` (or separate workspaces, per
   ADR) with schemas `bronze`, `silver`, `gold`, `quarantine`, `features`,
   and `ops`.
2. Create **volumes** for landing files (`landing/clicks`,
   `landing/partner`), and — if your environment allows — storage
   credentials and external locations for an external landing bucket.
3. **Grants** by group: engineers manage bronze/silver/gold in dev and read
   prod; `sp-prod-run` writes prod; analysts read gold only; ML engineers
   read silver/gold and manage features.
4. Define **tags** for classification (`pii`, `domain`, `tier`) and plan
   row filters and column masks (implemented in M8).
5. Write `docs/data-model.md` (tables, grain, keys, clustering, retention)
   and `docs/access-matrix.md` (groups × objects × privileges × columns ×
   rows).

**Acceptance criteria**

- [ ] Every planned object has a catalog, schema, owner, and grants.
- [ ] Analysts cannot read bronze or silver.
- [ ] The access matrix is complete and matches the grants.

---

### M3 — Code organisation and local development

**Goal:** Production logic lives in a tested Python package, not in
notebooks.

**Tasks**

1. Create `src/shoplite` with pure PySpark transformations: parsing and
   flattening, deduplication by event id, bot rules, sessionisation (30-
   minute gap), hash keys, and revenue logic.
2. Write **unit tests** with local Spark and small DataFrames (Module 2.19).
3. Run integration checks against remote compute with **Databricks
   Connect** from your IDE.
4. Build the package as a wheel referenced by bundle resources.
5. Keep notebooks only for exploration; document conventions in the README.

**Acceptance criteria**

- [ ] Unit tests run locally in minutes and pass in CI.
- [ ] The same functions run unchanged in pipelines and jobs.

---

### M4 — Ingestion A: files with Auto Loader

**Goal:** Files are ingested exactly once, with schema evolution and no data
loss.

**Tasks**

1. Write a file generator that lands clickstream JSON (with occasional new
   fields and corrupt lines) and partner CSV files (per partner, with late
   and corrected deliveries) into the landing volumes.
2. Ingest with **Auto Loader** into bronze streaming tables (inside the
   declarative pipeline, or as a job — per ADR): schema location, evolution
   mode, **rescued data column**, file metadata columns (path, modification
   time), and `availableNow`-style incremental runs.
3. Configure a **file-arrival trigger** (M7) for partner files.
4. Compare with `COPY INTO` for one partner and document the choice.

**Acceptance criteria**

- [ ] Re-running ingestion adds no duplicates.
- [ ] New fields are captured without failures; corrupt records are kept
      (rescued) and counted, not lost.
- [ ] Every bronze row is traceable to its file.

---

### M5 — Ingestion B: orders and customers change data

**Goal:** Every change to orders and customers reaches bronze as an ordered
change feed.

**Tasks**

1. **Preferred:** configure **Lakeflow Connect** from a supported database
   source available to you, ingesting `orders` and `customers` with change
   data capture into bronze.
2. **Alternative (if unavailable):** generate a CDC feed (Debezium-style JSON
   events with operation, before/after images, and a sequence number — as in
   Stage 2 Project 02) landed as files and ingested with Auto Loader.
3. Record the ordering column (sequence number or commit timestamp), delete
   representation, and schema-change behaviour in the source contract.
4. Reconcile source and bronze counts after a burst of inserts, updates, and
   deletes.

**Acceptance criteria**

- [ ] Inserts, updates, and deletes appear in bronze with an ordering
      column.
- [ ] Source and bronze reconcile.
- [ ] The chosen approach and its trade-offs are documented.

---

### M6 — The declarative pipeline: expectations, CDC, and gold

**Goal:** A single declarative pipeline builds trustworthy silver and gold
tables with explicit data-quality behaviour.

**Tasks**

1. **Silver**:
   - `silver.clicks`: typed, deduplicated, bots flagged, sessionised (reusing
     `src/shoplite`);
   - `silver.partner_shipments`: typed and validated;
   - `silver.orders`: **SCD Type 1** from the CDC feed using the automatic
     CDC API, sequenced by the ordering column, applying deletes;
   - `silver.dim_customer`: **SCD Type 2** from the customers change feed,
     with deletes and out-of-order changes handled.
2. **Expectations** on every silver table:
   - **fail** on contract violations (e.g. missing primary keys, unknown
     currencies in orders);
   - **drop** invalid rows (e.g. negative quantities) and count them;
   - **warn** on suspicious values (e.g. unusually large orders).
3. **Gold materialized views**: `gold.daily_revenue` (point-in-time customer
   segment), `gold.customer_ltv`, `gold.funnel_daily` (excluding bots).
4. Parameterise target catalog and schema per bundle target; run in
   development mode in dev, production mode in prod.
5. Query the **event log** for expectation metrics and lineage; publish a
   quality summary table in `ops`.

**Acceptance criteria**

- [ ] Each expectation action is demonstrated with injected defects.
- [ ] SCD Type 2 integrity holds after out-of-order and delete changes.
- [ ] Gold reconciles with silver; incremental refresh equals a full
      refresh.
- [ ] Quality metrics are queryable from the event log.

---

### M7 — Orchestration with Lakeflow Jobs

**Goal:** The platform runs itself, reacts to data arrival, and recovers
from failures predictably.

**Tasks**

1. Build the main job (as bundle resources):
   - **file-arrival trigger** on partner landing and a **daily schedule**;
   - a **for-each** task ingesting each partner with parameters;
   - a **pipeline update** task;
   - a **SQL reconciliation task** (silver vs source counts, gold vs
     silver totals) writing results to `ops`;
   - an **if/else** task: publish/notify on success, alert and stop on
     failure;
   - retries with backoff, timeouts, and failure/duration notifications.
2. Run production jobs **as `sp-prod-run`** with minimal grants.
3. Add a **backfill** mechanism with job parameters (date range) that
   re-ingests or refreshes safely.
4. Demonstrate a **repair run** after a deliberately failed task.

**Acceptance criteria**

- [ ] A normal day runs end to end without manual steps and meets the gold
      deadline.
- [ ] Failures alert with the failed task and link; repair reruns only what
      is needed.
- [ ] Production runs never execute as an individual user.

---

### M8 — Fine-grained governance, audit, and GDPR deletion

**Goal:** Each persona sees exactly what it should, access is auditable,
and personal data can be deleted everywhere.

**Tasks**

1. Apply **column masks** to PII columns (email, phone) — unmasked only for
   `privacy-officers` — and a **row filter** on regional tables for
   `analysts-regional`.
2. Tag PII columns and verify tags through the information schema.
3. **Access tests**: run queries as (or on behalf of) each group/service
   principal and assert visible rows and masked columns; store results.
4. Verify **lineage** from bronze to gold and dashboards for key columns.
5. **Audit**: system-table queries listing who accessed gold PII tables and
   who changed grants in the last week.
6. **GDPR deletion procedure**: delete the customer at the source (propagates
   through CDC), remove their history rows from `silver.dim_customer` and
   dependent gold tables, delete from bronze and quarantine, **purge deleted
   data files** (e.g. `VACUUM` after the retention window, and purging
   deletion vectors where used), remove the customer from shares and
   features, and verify with scans; write a deletion log.

**Acceptance criteria**

- [ ] Access tests pass for every persona in every interface you use (SQL
      editor, dashboards, Genie).
- [ ] Audit queries answer who accessed PII and who changed grants.
- [ ] The deletion procedure removes the customer from current tables and
      from physical storage after the retention period, with evidence.

---

### M9 — Performance: Photon, clustering, and predictive optimization

**Goal:** Gold queries and pipeline updates are fast and cost-effective —
with evidence.

**Tasks**

1. Build a **benchmark** of five typical gold queries and the daily pipeline
   update; record time, data read, and cost.
2. Apply **liquid clustering** on large silver and gold tables using common
   filter and join columns (or automatic clustering where available).
3. Enable **predictive optimization** on managed tables and verify its
   operations from system tables.
4. Compare Photon vs non-Photon (where selectable) for one workload.
5. Read one query profile and fix its most expensive operator.
6. Record before/after results in `docs/performance.md`.

**Acceptance criteria**

- [ ] Measurable improvement for the benchmark after tuning.
- [ ] Predictive optimization activity is visible.
- [ ] Every change has before/after evidence.

---

### M10 — Analytics: SQL warehouse, dashboards, alerts, metrics, and Genie

**Goal:** Business users get consistent, governed, self-service analytics.

**Tasks**

1. Size the **serverless SQL warehouse** (auto-stop, scaling) from measured
   concurrency.
2. Define **certified metrics** (net revenue, AOV, conversion rate, active
   customers) using the semantic/metric feature available to you (Module
   2.22); document definitions.
3. Build an **AI/BI finance dashboard** and a **marketing funnel dashboard**
   on gold, shared with the right groups.
4. Create **SQL alerts** for gold freshness and for revenue anomalies.
5. Create a **Genie space** over gold with instructions, example SQL, and
   trusted assets; evaluate it on **30 real questions**; record accuracy and
   failures in `docs/genie-evaluation.md`; improve until accuracy meets your
   target.

**Acceptance criteria**

- [ ] Dashboards and Genie use the certified metric definitions.
- [ ] Row filters and masks apply in dashboards and Genie.
- [ ] Freshness alerts fire when gold is stale.
- [ ] Genie accuracy is measured and documented.

---

### M11 — Sharing and ML handoff

**Goal:** Partners and ML teams receive governed data without copies,
leakage, or PII exposure.

**Tasks**

1. **Delta Sharing**: create a partner-specific, PII-free view of shipment
   and order status; add it to a share; create an **open-sharing
   recipient**; read it from Python outside Databricks; share with change
   data feed for incremental reads; audit access; revoke and verify.
2. **Feature table**: `features.customer_daily` (primary key
   `customer_id`, timestamp key `as_of_date`) built by a scheduled job from
   silver/gold.
3. **Point-in-time training set** for churn labels; verify no leakage by
   recomputing a sample by hand.
4. Train a simple model with **MLflow**, logging the training table
   versions, and register it in **Unity Catalog** with an alias.
5. A **batch-scoring job** writing `gold.churn_scores` daily.
6. A handoff document for the ML team (schema, freshness, point-in-time
   rules, owners).

**Acceptance criteria**

- [ ] The partner reads only permitted, PII-free data; revocation works.
- [ ] The training set is reproducible and leak-free.
- [ ] Lineage links source tables, features, model, and scores.

---

### M12 — Asset Bundles and CI/CD across environments

**Goal:** The entire platform deploys from code, through environments, by a
service principal.

**Tasks**

1. Ensure **all** jobs, pipelines, and other supported resources are bundle
   resources; governance SQL runs from a deployment job (idempotently); any
   remaining workspace-level objects are in Terraform or documented.
2. Targets: `dev` in **development mode** (per-user prefixes, paused
   schedules) and `prod` in **production mode** (run as `sp-prod-run`,
   schedules active, guarded settings).
3. CI workflow on pull requests: lint, unit tests, `bundle validate`.
4. CD on merge: deploy to `dev` → run the **integration smoke job** (small
   generated data through ingestion, pipeline, reconciliation, and
   dashboards' datasets) → on approval, deploy to `prod`.
5. **Rollback**: redeploy the previous Git tag; restore affected tables with
   `RESTORE` (time travel) if data was changed.
6. Demonstrate deploying to a **fresh target** from scratch.

**Acceptance criteria**

- [ ] Nothing in prod is created or changed by hand.
- [ ] CI uses no personal tokens; prod deploys require approval.
- [ ] A fresh target is deployed and passes the smoke job.

---

### M13 — Cost and observability with system tables

**Goal:** You can see, explain, and control what the platform costs and how
healthy it is.

**Tasks**

1. Cost queries over **billing system tables** joined with list prices:
   daily cost per tag (pipeline, environment, team) and per job/pipeline.
2. A **cost dashboard** with a spike alert; per-environment budgets.
3. An **operations dashboard**: job and pipeline run outcomes and durations,
   expectation metrics, reconciliation results, freshness of gold tables,
   warehouse usage.
4. Implement at least **two cost optimisations** (e.g. switch a job to
   serverless or smaller compute, tighten warehouse auto-stop, reduce
   pipeline refresh frequency where SLAs allow) and measure savings.
5. Record costs in `docs/cost-log.md`.

**Acceptance criteria**

- [ ] Cost per pipeline per day is visible and explained.
- [ ] Spikes trigger an alert.
- [ ] Two optimisations have measured savings without SLA regressions.

---

### M14 — Reliability drills and runbook

**Goal:** Failures are routine to handle, and the procedures are proven.

**Tasks**

Run each drill, capture evidence (run history, event log, system tables),
fix it, and write a short post-mortem in `docs/incidents/`:

1. A surge of invalid orders → expectations drop/fail as designed.
2. A source schema change (new column) → evolution handled or blocked per
   policy.
3. A bad logic deployment corrupts `gold.daily_revenue` → detect, roll back
   code, `RESTORE` the table, verify.
4. A task fails mid-job → **repair run**.
5. A service principal loses a grant → permission error diagnosed from audit
   and fixed as code.
6. A late partner file → file-arrival trigger and freshness alert behaviour.

Write `docs/runbook.md` covering daily checks, each alert, backfills, repair
runs, restores, GDPR deletions, secret rotation, adding a partner, and
deploying and rolling back.

**Acceptance criteria**

- [ ] Every drill is detected and resolved using the runbook.
- [ ] Table restore and repair runs are proven.
- [ ] Each post-mortem has an implemented prevention.

---

### M15 — Documentation, cost report, clean-up, and hand-over

**Goal:** Someone else can deploy, operate, and extend the platform — and
nothing is left running unnecessarily.

**Tasks**

1. Finalise the **README**: architecture, data products, how to deploy
   (dev/prod), how to run and backfill, how to access data, how to operate.
2. Finalise the **cost report**: estimate vs actual, costs per pipeline and
   environment, optimisations, and projected production cost.
3. **Clean up**: destroy the dev target (`bundle destroy`), stop warehouses,
   remove unused shares and recipients, and confirm no scheduled jobs remain
   in environments you are closing.
4. **Hand-over test**: another person (or a fresh identity) deploys to a new
   target, runs the smoke job, investigates one alert, and performs a
   backfill using only the documentation.
5. **Retrospective**: what Databricks did for you vs your Stage 2 hand-built
   versions (Projects 03 and 04), and how the design would differ on AWS
   native services (Gap Project 03).

**Acceptance criteria**

- [ ] The hand-over test succeeds.
- [ ] The cost report matches system-table data.
- [ ] Clean-up is verified.

---

### M16 — Optional stretch goals

- **Lakehouse Federation:** query the source database in place and compare
  with ingestion.
- **Open-format interoperability:** read gold tables from DuckDB, Spark
  outside Databricks, or another engine via open catalog interfaces or
  Iceberg-compatible metadata (Module 2.15).
- **External orchestration:** trigger the bundle's job from Airflow (Module
  2.13) and compare with native triggers.
- **Clean rooms:** a privacy-safe joint analysis with a simulated partner.
- **Vector search / RAG:** index help-centre articles for a support
  assistant (Module 2.22).
- **Multi-workspace:** separate dev and prod workspaces sharing a metastore,
  with catalog-workspace bindings.

---

## 9. Definition of done

- [ ] Groups, service principals, compute and budget policies, and secret
      scopes are in place; no individual grants.
- [ ] Unity Catalog governs every object; row filters, column masks, and
      tags are applied and tested; audit queries work.
- [ ] Auto Loader and Lakeflow Connect (or the CDC alternative) ingest data
      exactly once.
- [ ] The declarative pipeline enforces expectations and builds SCD1, SCD2,
      and gold tables correctly and incrementally.
- [ ] Lakeflow Jobs orchestrate the platform with triggers, for-each,
      conditions, alerts, repair, and backfills — as a service principal.
- [ ] Analytics: warehouse, dashboards, alerts, certified metrics, and an
      evaluated Genie space.
- [ ] Partner sharing and ML handoff are governed, leak-free, and traceable.
- [ ] Everything deploys from the bundle through CI/CD to dev and prod.
- [ ] Cost per pipeline is visible; optimisations measured.
- [ ] Drills completed; runbook, ADRs, cost report, and retrospective done;
      hand-over test passed; clean-up verified.

---

## 10. Evaluation rubric (self or peer review)

Score each area from 0 to 3. A production-grade project scores **at least 2
in every area** and **3 in Governance, Delivery, and Correctness**.

| Area | What a "3" looks like |
| --- | --- |
| Architecture and decisions | Clear design; ADRs with measured evidence |
| Governance | Environment catalogs, group grants, masks, filters, tags, lineage, audit, tested access |
| Ingestion | Exactly-once Auto Loader and CDC ingestion with evolution and provenance |
| Pipelines and quality | Expectations with correct actions; SCD1/SCD2; incremental equals full refresh |
| Orchestration | Triggers, for-each, conditions, repair, backfills, service principal runs |
| Analytics | Certified metrics used everywhere; dashboards, alerts, evaluated Genie |
| Sharing and ML | Safe shares with revocation; leak-free features; model lineage |
| Delivery | Bundles for everything; OIDC CI/CD; approval-gated prod; fresh-target deploy |
| Cost and performance | Cost per pipeline from system tables; tuning and optimisations with evidence |
| Operations | Drills, runbook, hand-over test, verified clean-up |

---

## 11. Common pitfalls to avoid

- Production jobs on all-purpose clusters or running as your own user.
- Grants to individuals; one catalog for dev and prod.
- Business logic only in notebooks.
- Expectations that fail on minor issues — or no expectations at all.
- SCD Type 2 built without a reliable sequencing column.
- Genie spaces over raw tables with no instructions or evaluation.
- Shares that expose PII or are never revoked.
- Resources created in the UI and missing from the bundle.
- Personal access tokens in CI secrets.
- Assuming a `DELETE` physically removes data before retention and purge
  steps run.
- No tags, so costs cannot be attributed.

---

## 12. Suggested timeline

| Week | Milestones |
| --- | --- |
| 1 | M0 framing · M1 foundations · M2 Unity Catalog · M3 code organisation |
| 2 | M4 Auto Loader · M5 CDC ingestion · M6 declarative pipeline |
| 3 | M7 Lakeflow Jobs · M8 governance and deletion · M9 performance · M10 analytics |
| 4 | M11 sharing and ML · M12 bundles and CI/CD · M13 cost · M14 drills · M15 hand-over |
| Optional | M16 stretch goals |

---

## 13. What to show in a portfolio or interview

Be ready to explain:

1. How Unity Catalog is organised and how row filters, column masks, and
   tags protect PII — and how you tested them.
2. How Auto Loader and the CDC path ingest data exactly once.
3. How expectations decide between warning, dropping, and failing.
4. How SCD Type 2 is produced from a change feed, including out-of-order
   changes and deletes.
5. How Lakeflow Jobs orchestrate, repair, and backfill — and why production
   runs as a service principal.
6. How the platform is deployed from bundles through CI/CD to a fresh
   environment.
7. What each pipeline costs per day and how you reduced it.
8. How a partner receives data via Delta Sharing and how ML teams get
   leak-free features.
9. How a customer's data is deleted — including physical files.

A README with the architecture diagram, a short demo (file lands → pipeline
with expectations → dashboard with masked PII → Genie question → partner
share → repair after a failure → fresh-target deploy), the cost dashboard,
and the ADRs make this a strong Databricks portfolio piece — and a solid
base for the capstone on Databricks.
