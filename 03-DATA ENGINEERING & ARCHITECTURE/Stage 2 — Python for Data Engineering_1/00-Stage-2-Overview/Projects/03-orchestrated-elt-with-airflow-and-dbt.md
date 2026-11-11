# Project Roadmap — Orchestrated ELT with Airflow and dbt

This is the end-to-end roadmap for **Stage 2 Project 03: Orchestrated ELT
with Airflow and dbt**. It takes you from an empty repository to a
**production-grade** analytics platform in which several sources are
extracted and loaded into a warehouse, transformed with **dbt** into tested
dimensional models, and orchestrated end to end by **Apache Airflow** — on
time, every day, with quality gates, backfills, CI/CD, and alerting.

It is written as a sequence of **milestones**. Each milestone has a goal,
tasks, deliverables, and **acceptance criteria** you must meet before moving
on. The acceptance criteria are what make this production grade rather than
"a DAG that ran `dbt run` once".

---

## 1. Why this project matters

The combination of an orchestrator and dbt on top of a warehouse is the
most common analytics architecture in industry today (the "modern data
stack"). It looks simple — load raw data, write `SELECT` statements, run
them on a schedule — but in production it fails in predictable ways:

- dashboards show half-updated numbers because models were published before
  tests ran;
- a late source file silently produces a day of zero revenue;
- a full rebuild takes six hours, so someone adds incremental models without
  handling late data;
- nobody knows which models a change affects, so every pull request rebuilds
  the whole warehouse — or none of it is tested;
- a backfill after a logic fix double-counts a month;
- the 07:00 finance deadline is missed and nobody is alerted until 09:30.

This project makes you build the platform that avoids all of these.

---

## 2. Project goal and scope

### Goal

Build `analytics_platform`, which every day:

1. **Extracts and loads** data from four sources into a `raw` layer of the
   warehouse — incrementally and idempotently (EL).
2. **Transforms** raw data with **dbt** into staging, intermediate, and mart
   models (a star schema with an SCD Type 2 customer dimension), using
   incremental models that handle late data.
3. **Tests** every model and **blocks publication** of any mart that fails
   critical tests (write–audit–publish).
4. Is **orchestrated by Airflow**: data-aware scheduling, retries, pools,
   deadlines, backfills, and alerts.
5. Delivers finance marts by **07:00** every day, with freshness and
   correctness visible to consumers.
6. Is tested, versioned, deployed through CI/CD with dbt "slim CI", observed,
   documented, and operable by someone else.

### In scope

- Source systems with realistic behaviour, EL pipelines, the dbt project
  (models, snapshots, seeds, macros, tests, contracts, docs), Airflow DAGs,
  quality gates, backfills, environments, CI/CD, observability, lineage, and
  operations.

### Out of scope (covered by other Stage 2 projects)

- A deep, hand-built API client and incremental ingestion framework →
  **Project 01** (you may reuse it here as one source).
- Log-based CDC → **Project 02** (you may reuse its silver tables as a
  source).
- Spark and lakehouse gold pipelines → **Project 04**.
- Streaming → **Project 05**.
- A full data-quality and observability platform → **Project 06**.

---

## 3. Prerequisites and when to do this project

**Recommended timing:** after completing **Modules 2.1–2.13**. The
production-hardening milestones (M11–M14) use Modules 2.17–2.20. If you
have not studied those yet, complete the **Core track** now and return for
the **Production track** later.

| Module | What this project uses from it |
| --- | --- |
| 2.1 Foundations | ELT, medallion-style layering, SLAs, consumers |
| 2.6 SQL | CTEs, window functions, `MERGE`, SCD Type 2, assertion queries |
| 2.7 Python DB connectivity | Warehouse connections, bulk loading |
| 2.8 Data modelling | Facts, dimensions, grain, keys, SCD types, bus matrix |
| 2.9 Ingestion patterns | Incremental extraction, watermarks, file drops, dlt |
| 2.11 Validation and quality | Contracts, severity, WAP, reconciliation, freshness |
| 2.12 Pipeline design | Data intervals, idempotency, incremental processing, late data, backfills, hashing, **dbt** |
| 2.13 Orchestration | **Airflow**: DAGs, TaskFlow, mapping, assets, sensors, retries, deadlines, backfills, DAG tests |
| 2.17 Cloud *(production track)* | Cloud warehouse, IAM, query cost |
| 2.18 Delivery *(production track)* | Images, secrets, CI/CD, environments, dbt slim CI |
| 2.19 Testing | dbt unit tests, DAG tests, end-to-end smoke tests |
| 2.20 Observability *(production track)* | Metrics, OpenLineage, catalog, alerts, runbooks |
| 2.22 Serving *(stretch)* | Semantic layer on the marts |

### Tracks

| Track | Milestones | Result |
| --- | --- | --- |
| **Core track** | M0–M10 | A correct, tested, orchestrated ELT platform running locally |
| **Production track** | M11–M14 | Containerised, CI/CD-deployed, observable, and operable platform |

**Estimated effort:** Core track 4–5 weeks; Production track 2 weeks (at
8–10 hours per week).

---

## 4. The scenario

You are the analytics engineer at **ShopLite**. Leadership wants one
trusted warehouse for finance, marketing, and product analytics.

### Sources

| Source | Access | Behaviour that makes it hard |
| --- | --- | --- |
| **Orders database** (PostgreSQL: customers, products, orders, order_items, payments) | SQL extraction by `updated_at` (or Project 02's silver tables) | Late-updated statuses, deletes, customer attribute changes |
| **Commerce API** (refunds and returns) | REST API (or Project 01's package) | Pagination, rate limits, late records |
| **Marketing spend files** (one CSV per channel per day) | SFTP or object-storage drop | Files arrive late, sometimes twice, sometimes corrected |
| **FX rates** | Public-style REST endpoint (mock) | One rate per currency per day; occasional gaps |

### Consumers and their needs

| Consumer | Needs |
| --- | --- |
| Finance | `daily_revenue` (gross, refunds, net; by country and currency, converted to USD) by **07:00**; month-end closing with no silent restatements |
| Marketing | Spend, attributed orders, and return on ad spend (ROAS) by channel and day |
| Product and analysts | Clean star schema: orders, order items, customers (with history), products, dates |

### Service-level agreement (write it down in M0)

- **Timeliness:** finance marts published by **07:00** local time for the
  previous day; others by 09:00.
- **Correctness:** no mart is published unless its critical tests pass;
  daily revenue reconciles with the source database within a documented
  tolerance.
- **Late data:** changes up to **7 days** old are reflected automatically;
  older changes to closed months require an audited restatement.
- **Freshness visibility:** every mart exposes when it was last successfully
  built and for which data date.
- **Availability:** transient failures retry automatically; missing the
  deadline or a failed critical test pages the on-call engineer.

---

## 5. Target architecture

```text
 Sources                         Warehouse (PostgreSQL locally; cloud optional)
 ───────                         ─────────────────────────────────────────────
 Orders DB ──┐                   raw.*          (EL output, append/merge + load metadata)
 Commerce API┤  EL (dlt or        │
 Spend files ┤  custom Python) ──►│ dbt
 FX rates  ──┘                    ▼
                                 staging.*      (1:1 with sources, cleaned, typed)
                                 intermediate.* (joins, business logic)
                                 snapshots.*    (SCD Type 2)
                                 audit.*        (marts built here first)  ── dbt tests ──┐
                                 marts.*        (published star schema + reporting)  ◄────┘ publish on pass

 Airflow 3 (orchestration)
   el_<source> DAGs ──emit assets──► transform DAG (asset-scheduled) ──► publish ──► notify
   sensors for files · pools for sources · retries · deadlines · backfills · alerts

 Around everything: dbt docs · OpenLineage · metrics & alerts · CI/CD with slim CI · runbook
```

### Technology choices (defaults)

| Concern | Default (local) | Production option |
| --- | --- | --- |
| Warehouse | PostgreSQL (`dbt-postgres`) | Snowflake / BigQuery / Redshift (`dbt-<adapter>`) |
| Extract–load | **dlt** pipelines (or your Project 01/02 code) | Same, or managed connectors (Module 2.9) |
| Transformation | **dbt Core** | Same, or managed dbt |
| Orchestration | **Apache Airflow 3** (Docker Compose) | Airflow on Kubernetes (Helm) or managed Airflow |
| dbt execution in Airflow | Isolated environment (separate image or virtualenv) running `dbt build` with selectors | Or a dbt-to-Airflow integration that maps models to tasks (ADR) |
| File drops | SFTP container or MinIO | Cloud object storage |
| Quality | dbt tests, unit tests, contracts, source freshness | + Project 06 platform |
| Lineage | OpenLineage (Airflow provider, dbt integration) + Marquez | Same or catalog |
| CI/CD | GitHub Actions with dbt slim CI | Same, with environments and OIDC |
| Linting | Ruff, SQLFluff (dbt templater) | Same |

Record every decision as an **ADR** in `docs/adr/`, especially: EL tool,
dbt execution strategy in Airflow, incremental strategies, and the
publication (WAP) mechanism.

---

## 6. Repository structure

```text
orchestrated-elt/
├── README.md
├── docker-compose.yml               # airflow, warehouse (postgres), source db, sftp/minio, mock APIs, marquez
├── .env.example
├── docs/
│   ├── requirements.md
│   ├── architecture.md
│   ├── source-contracts/            # one per source
│   ├── bus-matrix.md                # business processes × dimensions
│   ├── adr/
│   └── runbook.md
├── sources/                         # source simulators and data generators (with late data, corrections)
├── el/                              # extract–load pipelines (dlt sources/resources or custom)
│   └── pyproject.toml
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles/                    # profiles.yml per environment (no secrets; env vars)
│   ├── models/
│   │   ├── staging/<source>/        # stg_ models + sources.yml (freshness)
│   │   ├── intermediate/            # int_ models
│   │   └── marts/{core,finance,marketing}/  # dim_, fct_, reporting models + contracts
│   ├── snapshots/                   # SCD Type 2
│   ├── seeds/                       # small reference data (country codes, channel mapping)
│   ├── macros/                      # e.g. surrogate keys, lookback windows, publish helpers
│   ├── tests/                       # singular tests, reconciliation tests
│   └── packages.yml
├── airflow/
│   ├── dags/                        # thin DAG files
│   ├── include/                     # helpers, SQL, dbt runner utilities
│   └── tests/                       # DAG import, structure, policy tests
├── tests/                           # EL unit/integration tests, end-to-end smoke test
└── .github/workflows/               # CI (lint, tests, dbt slim CI, DAG tests), CD
```

---

## 7. Milestones overview

```text
Core track
  M0   Project framing and local platform
  M1   Source systems and source contracts
  M2   Extract–load into the raw layer
  M3   dbt foundations: project, sources, staging
  M4   Dimensional marts: intermediate models, facts, dimensions, snapshots
  M5   Incremental models, late data, and full-refresh strategy
  M6   Testing and contracts in dbt
  M7   Airflow orchestration
  M8   Quality gates and write–audit–publish
  M9   Backfills, reruns, and month-end closing
  M10  Testing the whole platform

Production track
  M11  Packaging, dependency isolation, and secrets
  M12  CI/CD with dbt slim CI and environments
  M13  Observability, lineage, documentation, and alerting
  M14  Operations: runbook, drills, performance, cost, and hand-over
  (M15 Optional stretch goals)
```

Commit and tag at the end of every milestone (`m0`, `m1`, …).

---

## 8. Core track

### M0 — Project framing and local platform

**Goal:** A clear definition of success and a reproducible local platform.

**Tasks**

1. Write `docs/requirements.md` with consumers, questions, the SLA
   (Section 4), and non-goals.
2. Write `docs/bus-matrix.md` (business processes × conformed dimensions —
   Module 2.8): orders, payments, refunds, marketing spend × date, customer,
   product, channel, country, currency.
3. Draw the architecture and data flow in `docs/architecture.md`.
4. Build `docker-compose.yml`: Airflow 3 (with a PostgreSQL metadata
   database), a **separate** PostgreSQL acting as the warehouse, the source
   database, an SFTP server or MinIO, mock APIs, and Marquez (later) — with
   health checks and idempotent set-up services.
5. Set up tooling: `uv`, Ruff, SQLFluff, pytest, `pre-commit` with secret
   scanning.
6. First ADRs: warehouse, EL tool, dbt execution strategy in Airflow.

**Acceptance criteria**

- [ ] The platform starts healthy from a clean clone; the Airflow UI and the
      warehouse are reachable.
- [ ] The SLA has measurable deadlines and tolerances.
- [ ] The bus matrix lists every mart you will build.

---

### M1 — Source systems and source contracts

**Goal:** Realistic, controllable sources and written contracts describing
how each behaves.

**Tasks**

1. Build or reuse source simulators with a seeded generator:
   - orders database with daily inserts, status updates up to 10 days
     later, cancellations, deletes, and customer attribute changes;
   - refunds API with pagination, rate limits, and late records;
   - marketing spend CSV drops per channel per day — some late, some
     re-sent as corrections, one occasionally malformed;
   - FX rates endpoint with occasional missing days.
2. Write a **source contract** per source (Module 2.11): fields and types,
   keys, update and delete behaviour, delivery schedule, lateness, known
   quirks, owner.
3. Measure lateness from the simulators (distribution of `updated_at` vs
   event date) — you will use it to size lookback windows in M5.

**Acceptance criteria**

- [ ] Each source can simulate its failure modes on demand.
- [ ] Every source has a contract with keys and change behaviour.
- [ ] You have a measured lateness distribution for orders and refunds.

---

### M2 — Extract–load into the raw layer

**Goal:** Raw data arrives in the warehouse completely, incrementally, and
idempotently — without transformation.

**Tasks**

1. Build one EL pipeline per source (dlt recommended — Module 2.9; or reuse
   Project 01/02 code):
   - orders database: incremental by `updated_at` with a lookback,
     **merge** into raw tables by primary key; deletes captured (soft-delete
     flag or a periodic key reconciliation);
   - refunds API: incremental with pagination and rate limiting;
   - spend files: detect complete files, register each file (name, size,
     checksum), load with **replace-by-file** semantics so corrected
     re-sends replace earlier versions;
   - FX rates: daily append with idempotent keys.
2. Every raw table carries load metadata: `_loaded_at`, `_load_id`/run id,
   source file or request, and (for files) checksum.
3. Parameterise every pipeline by **data interval** (Module 2.12) so it can
   be run for any past day.
4. Decide raw-layer schema-change behaviour (dlt schema contracts or your
   own checks) and document it.

**Acceptance criteria**

- [ ] Running any EL pipeline twice for the same interval changes nothing.
- [ ] A corrected spend file replaces the earlier version; a duplicate
      delivery is ignored.
- [ ] Late-updated orders within the lookback appear in raw.
- [ ] An unexpected schema change is handled according to the documented
      policy (never silently).

---

### M3 — dbt foundations: project, sources, staging

**Goal:** A clean, conventional dbt project with a staging layer that every
later model builds on.

**Tasks**

1. Initialise the dbt project with profiles per environment (`dev`, `ci`,
   `prod`) using environment variables for credentials (no secrets in
   files).
2. Adopt conventions (Module 2.12): `stg_`, `int_`, `dim_`, `fct_`
   prefixes; one staging model per source table; folder-level
   materialisation defaults (staging as views, marts as tables); SQL style
   enforced by SQLFluff.
3. Declare **sources** with descriptions and **freshness** thresholds per
   source (e.g. spend files: warn after 26 h, error after 30 h).
4. Build **staging models**: rename columns, cast types, standardise time
   zones to UTC, normalise codes, deduplicate raw versions, and expose
   deletion flags — no joins and no business logic.
5. Add **seeds** for small reference data (country codes, channel mapping)
   and packages (e.g. `dbt_utils`).
6. Add basic tests on every staging model's primary key (`unique`,
   `not_null`).

**Acceptance criteria**

- [ ] `dbt build --select staging` passes on a fresh warehouse.
- [ ] Every source has freshness thresholds and descriptions.
- [ ] SQLFluff passes on all models.
- [ ] Every staging model has a documented grain and tested key.

---

### M4 — Dimensional marts: intermediate models, facts, dimensions, snapshots

**Goal:** A trustworthy star schema and reporting marts that answer the
consumers' questions.

**Tasks**

1. Build **intermediate models** for reusable business logic: order
   enrichment (line totals, discounts), FX conversion with point-in-time
   rates (as-of join by date and currency — Module 2.12), refund
   allocation, marketing attribution (a simple, documented last-touch
   rule).
2. Build **dimensions**: `dim_date` (with fiscal calendar), `dim_product`,
   `dim_channel`, `dim_country`, and `dim_customer` from a **dbt snapshot**
   (SCD Type 2, check or timestamp strategy — Module 2.12), including an
   unknown-member row.
3. Build **facts** with explicit grain (Module 2.8): `fct_order_items`
   (transaction), `fct_orders`, `fct_payments`, `fct_refunds`,
   `fct_marketing_spend` (periodic, per channel per day).
4. Build **reporting marts**: `mart_daily_revenue` (gross, refunds, net, in
   local currency and USD, by country), `mart_channel_performance` (spend,
   attributed orders, revenue, ROAS), `mart_customer_ltv`.
5. Generate **surrogate keys** with a consistent macro and document the
   canonicalisation (Module 2.12).
6. Document every model and column (descriptions) and its grain.

**Acceptance criteria**

- [ ] Every fact and dimension has a written grain and a key test.
- [ ] Facts join to dimensions with no orphans (relationships tests) and no
      fan-out (row counts preserved).
- [ ] `mart_daily_revenue` reconciles with a direct SQL query on the source
      database for sample days.
- [ ] Revenue by customer segment can be reported both "as was" and "as is"
      using the SCD Type 2 dimension.

---

### M5 — Incremental models, late data, and full-refresh strategy

**Goal:** Daily builds stay fast as data grows — without ever missing late
changes or double-counting.

**Tasks**

1. Convert large facts (`fct_order_items`, `fct_orders`, `fct_payments`)
   to **incremental** models with `unique_key` and a suitable strategy
   (`merge` or `delete+insert`).
2. Implement a **lookback window** (a project variable, default sized from
   the M1 lateness measurement, e.g. 7 days) so each run reprocesses recent
   days — not only rows newer than the maximum loaded timestamp.
3. Make `mart_daily_revenue` recompute only the affected days (the dates
   touched by changed orders and refunds — Module 2.12 change
   propagation).
4. Configure `on_schema_change` deliberately and document it.
5. Pass the Airflow **data interval** into dbt as variables so a run for a
   given day is deterministic (no `current_date` inside models).
6. Define the **full-refresh** policy: when it is required (logic changes),
   how it is run safely (into a shadow schema, then published — M8/M9),
   and how long it takes.
7. Optionally evaluate dbt's **microbatch** strategy for time-series facts
   and record the result in an ADR.

**Acceptance criteria**

- [ ] After 30 simulated days with late updates, incremental results equal
      a full refresh exactly (automated comparison).
- [ ] Running the same day twice leaves marts unchanged.
- [ ] Incremental daily build time stays roughly flat as history grows
      (measure it).
- [ ] No model references the current date directly.

---

### M6 — Testing and contracts in dbt

**Goal:** Every important assumption is tested, and published marts have
enforced contracts.

**Tasks**

1. **Generic data tests** on every model: keys, `not_null`,
   `accepted_values`, `relationships`, and package tests (e.g. expression or
   recency tests).
2. **Singular tests** for business rules: net revenue = gross − refunds;
   no negative spend; every order has at least one item; SCD Type 2 has
   one current row per customer and no overlapping ranges.
3. **Reconciliation tests**: raw vs staging row counts; total revenue in
   `mart_daily_revenue` vs `fct_orders` per day; spend per channel-day vs
   raw files.
4. **Unit tests** (dbt unit tests) for the trickiest logic: FX as-of
   conversion, refund allocation, attribution, lookback filtering.
5. **Severities and thresholds**: `error` for critical tests on finance
   marts, `warn` for informational ones; `warn_if` / `error_if` for
   tolerated error rates; `store_failures` for investigation.
6. **Model contracts** on published marts (column names, types, and
   constraints), and **versioning** a mart when its contract must change.
7. Tag tests as `critical` or `non_critical` for use by the quality gate
   (M8).

**Acceptance criteria**

- [ ] Every mart has contract enforcement and critical tests.
- [ ] Every business rule in `docs/requirements.md` maps to at least one
      test.
- [ ] Injected defects (duplicate orders, missing FX rate, negative spend,
      broken attribution) each fail the expected test.

---

### M7 — Airflow orchestration

**Goal:** The whole platform runs itself daily with the right
dependencies, triggers, and failure behaviour.

**Tasks**

1. Design DAGs (Module 2.13) and write the design into an ADR:
   - `el_orders_db`, `el_refunds_api`, `el_fx_rates` — scheduled daily
     after midnight; each task calls the EL pipeline with the
     **data interval**; each successful run emits an **asset** update
     (e.g. `raw.orders`);
   - `el_marketing_spend` — waits for the day's files with a **deferrable**
     sensor or trigger, with a deadline;
   - `transform_daily` — **scheduled on assets** (all required raw
     assets updated), runs dbt (M8 publish flow), then emits
     `marts.finance` and `marts.marketing` assets;
   - `reverse_notify` (optional) — informs consumers that marts are ready.
2. Choose and implement the **dbt execution approach** (ADR):
   - `dbt build` with selectors per layer in a few tasks (simple, fast), or
   - one Airflow task per model via an integration (fine-grained retries and
     visibility, more scheduler load).
   Either way, run dbt in an **isolated Python environment** to avoid
   dependency conflicts with Airflow.
3. Configure `retries`, exponential backoff, and `execution_timeout` per
   task; non-retryable failures for contract violations (Module 2.13).
4. Use **pools** to limit concurrent calls to the refunds API and warehouse
   load.
5. Use **dynamic task mapping** for per-channel spend loads.
6. Pass only small references through XComs (run ids, row counts).
7. Store connections and variables in environment variables or a secrets
   backend — never in DAG files.

**Acceptance criteria**

- [ ] A full day runs end to end without manual steps, triggered by time
      and assets.
- [ ] If the spend files are late, the transform waits (not fails) until a
      deadline, then alerts.
- [ ] Killing a worker mid-run results in retries and a correct final
      state.
- [ ] DAG files contain no business logic and parse quickly.

---

### M8 — Quality gates and write–audit–publish

**Goal:** Consumers never see marts that failed critical tests — and always
know how fresh the data is.

**Tasks**

1. Implement **write–audit–publish** (Module 2.11) for marts:
   - **write:** build marts into an `audit` schema (via a dbt target or
     schema override);
   - **audit:** run all tests for the built models; evaluate critical vs
     non-critical failures;
   - **publish:** if critical tests pass, publish atomically (for example,
     swap schemas inside one transaction, or repoint consumer-facing views
     at the audited tables); if they fail, keep the previous published
     version, stop, and alert.
2. Write a `publication_log` table: mart, data date, run id, dbt
   invocation id, test summary, published at.
3. Expose freshness to consumers: a `marts.data_status` view showing, per
   mart, the latest published data date and time.
4. Add a **circuit breaker**: if raw source freshness checks fail, skip the
   transform and alert instead of building marts on stale inputs.
5. Notify consumers when marts are published (or delayed) with a short
   status message.

**Acceptance criteria**

- [ ] An injected critical defect leaves yesterday's published marts
      untouched and triggers an alert.
- [ ] Non-critical failures publish with a warning recorded.
- [ ] Consumers can always see the data date and publication time of each
      mart.
- [ ] Publication is atomic — no consumer query ever sees a mix of old and
      new tables.

---

### M9 — Backfills, reruns, and month-end closing

**Goal:** Reprocessing history is routine, safe, and auditable.

**Tasks**

1. **Rerun a single day** end to end (EL + dbt) from the Airflow UI or CLI
   and prove the result is identical.
2. **Backfill** 90 days of EL with bounded concurrency (pools, max active
   runs) without delaying the daily 07:00 run (Module 2.13).
3. **Logic change rollout:** change the attribution rule, rebuild affected
   marts with a **full refresh into the audit schema**, compare old vs new
   outputs (a data diff report — Module 2.19), then publish.
4. **Month-end closing:** after a cutoff (e.g. business day 3), mark the
   month closed in `publication_log`; changes to a closed month require a
   **restatement** run that records what changed, who approved it, and
   notifies finance (Module 2.12).
5. Write runbook entries for each procedure.

**Acceptance criteria**

- [ ] A 90-day backfill completes while daily runs still meet their
      deadline.
- [ ] A logic change is released with a data diff and no downtime for
      consumers.
- [ ] Late changes to a closed month never change published numbers without
      an audited restatement.

---

### M10 — Testing the whole platform

**Goal:** Confidence that EL, dbt, and Airflow work together — before any
change reaches production.

**Tasks**

1. **EL unit and integration tests** (recorded API responses,
   Testcontainers for PostgreSQL and SFTP/MinIO — Module 2.19).
2. **dbt:** unit tests, data tests, and contract checks run in CI against a
   fresh schema with seeded fixture data.
3. **DAG tests** (Module 2.13): import test, structure tests (quality gate
   between build and publish; publish never directly after build),
   policy tests (owners, retries, timeouts, catch-up setting, no naive
   dates).
4. **End-to-end smoke test**: start the stack, generate two days of source
   data, run the full DAG chain for both days with `airflow dags test` (or
   triggered runs), and assert marts, tests, and `publication_log`.
5. **Regression tests** for every defect found during the project.

**Acceptance criteria**

- [ ] The end-to-end smoke test passes from a clean environment.
- [ ] Removing the audit step, breaking the lookback, or publishing before
      tests each fails a test.
- [ ] No flaky tests across 20 runs.

**At the end of M10 you have completed the Core track.** Tag the repository
`core-complete` and write a retrospective.

---

## 9. Production track

### M11 — Packaging, dependency isolation, and secrets

**Goal:** Reproducible deployments with no dependency conflicts and no
secrets in code.

**Tasks**

1. Build images (Module 2.18): an Airflow image with your DAG helpers and
   providers, and a **separate dbt image** (or virtual environment) pinned
   to your dbt and adapter versions; run dbt tasks in that image (for
   example via a Docker/Kubernetes pod operator) or in an isolated
   environment.
2. Pin all versions with lock files; scan images.
3. Move credentials (warehouse, source database, SFTP, APIs) into an
   Airflow **secrets backend** or Kubernetes secrets fed from a secrets
   manager; dbt reads credentials from environment variables.
4. Use separate warehouse roles for EL, dbt, and analysts with least
   privilege (Modules 2.17, 2.20).

**Acceptance criteria**

- [ ] Upgrading dbt never requires changing the Airflow image, and vice
      versa.
- [ ] No credential appears in Git, images, `profiles.yml`, or logs.
- [ ] Each warehouse role can access only what it needs.

---

### M12 — CI/CD with dbt slim CI and environments

**Goal:** Every change is tested against production-like data in minutes,
and deployments are repeatable.

**Tasks**

1. **CI on pull requests** (Module 2.18):
   - lint (Ruff, SQLFluff), type checks, EL unit tests, DAG tests;
   - **dbt slim CI:** build and test only **modified models and their
     children** (`state:modified+`) in a per-PR schema, **deferring** to the
     production manifest for unchanged parents;
   - contract checks and a data-diff report for modified marts against
     production.
2. Store the production **dbt artefacts** (`manifest.json`, run results)
   after every production run so CI can compare against them.
3. **CD on merge:** build images once, deploy DAGs and the dbt project to
   `dev`, run the end-to-end smoke test, promote the same images to
   `staging` and then `prod` with approval.
4. Drop per-PR schemas automatically when pull requests close.

**Acceptance criteria**

- [ ] A pull request changing one model builds and tests only that model and
      its descendants, in minutes.
- [ ] A breaking change to a mart's contract fails CI.
- [ ] The versions of DAGs, dbt project, and images in production are
      traceable to a commit.

---

### M13 — Observability, lineage, documentation, and alerting

**Goal:** Everyone can see what ran, what it produced, whether it is on
time, and what depends on what.

**Tasks**

1. **Run metrics** (Module 2.20): Airflow task durations and states; parse
   dbt `run_results.json` into a `dbt_model_runs` table (model, duration,
   rows affected, status, test results) and chart slowest models and test
   failures over time.
2. **Lineage:** enable OpenLineage in Airflow and dbt; view end-to-end
   lineage from sources to marts in Marquez or a catalog; use it for impact
   analysis before changes.
3. **Documentation:** publish dbt docs (descriptions, lineage graph, tests)
   as an internal site after each production deployment; link marts to
   owners and glossary terms.
4. **Alerts** with severity, owner, and runbook links:
   - finance marts not published by 07:00 → page (use your Airflow
     version's deadline features plus a freshness check on
     `marts.data_status`);
   - critical test failure blocking publication → page;
   - source freshness error → ticket (page for orders);
   - EL failure after retries → ticket;
   - model run time or warehouse cost spike → ticket.
5. Tag warehouse queries by DAG, task, and dbt model for cost attribution
   (Module 2.17).

**Acceptance criteria**

- [ ] The 07:00 deadline alert fires in a drill where the pipeline is
      delayed.
- [ ] For any mart column, you can show its upstream sources and downstream
      consumers.
- [ ] You can list the five slowest and five most expensive models from
      your own metrics.

---

### M14 — Operations: runbook, drills, performance, cost, and hand-over

**Goal:** Someone else can operate and evolve the platform confidently.

**Tasks**

1. Write `docs/runbook.md`: daily operation, rerunning a day, backfills,
   full refreshes, restatements, handling each alert, adding a new source,
   adding a new mart, rotating credentials, and escalation.
2. Run **drills** and record detection and recovery times:
   - spend files two hours late;
   - a corrupted source file;
   - a critical test failure in `mart_daily_revenue`;
   - the Airflow scheduler down for an hour;
   - the warehouse unavailable during the dbt run;
   - a bad model change reaching staging.
3. **Performance:** find the slowest models, fix them (incremental logic,
   indexes or clustering, materialisation choices, pre-aggregation), and
   show the daily run meets its deadline with headroom (Module 2.21).
4. **Cost** (if on a cloud warehouse): cost per daily run and per mart;
   auto-suspend and sizing; a monthly estimate and budget alert.
5. **Hand-over:** walkthrough for a new engineer, and a final
   retrospective.

**Acceptance criteria**

- [ ] All drills end with correct marts and consumers informed.
- [ ] The daily run finishes with at least 60 minutes of headroom before
      07:00 on your target data volume.
- [ ] Another person can add a new source and mart using only the
      documentation.

---

### M15 — Optional stretch goals

- **Cloud warehouse:** migrate to Snowflake, BigQuery, or Redshift with
  Terraform-managed resources; compare cost and run time.
- **Semantic layer:** define certified metrics (net revenue, ROAS, active
  customers) on the marts (Module 2.22) and serve them to a BI tool.
- **Per-model orchestration:** try a dbt-to-Airflow integration that maps
  models to tasks, or Dagster's dbt assets, and compare with your approach
  (ADR).
- **Data contracts:** manage source and mart contracts in a YAML standard
  and generate tests from them (Module 2.11).
- **BI dashboards:** build finance and marketing dashboards on the marts with
  freshness indicators from `marts.data_status`.
- **Project 01 and 02 integration:** replace simulated sources with the
  outputs of your ingestion and CDC projects.

---

## 10. Definition of done

**Correctness**

- [ ] Marts are correct against the source for sampled days; incremental
      results equal full refreshes; revenue reconciles within tolerance.
- [ ] Late data within the window is applied automatically; closed months
      change only through audited restatements.

**Reliability and timeliness**

- [ ] Daily runs complete without manual steps and meet the 07:00 deadline
      with headroom.
- [ ] Every EL and dbt run is idempotent; reruns and backfills are safe.
- [ ] Consumers never see marts that failed critical tests.

**Engineering**

- [ ] dbt project with conventions, documentation, tests, unit tests, and
      contracts.
- [ ] Thin, tested DAGs with assets, sensors, pools, retries, and deadlines.
- [ ] CI with slim dbt builds, DAG tests, and end-to-end smoke test; CD with
      promotion.
- [ ] Isolated dependencies and no secrets in code.

**Operations and documentation**

- [ ] Metrics, lineage, dbt docs, and actionable alerts.
- [ ] Requirements, bus matrix, source contracts, ADRs, runbook, and
      retrospective complete.

---

## 11. Evaluation rubric (self or peer review)

Score each area from 0 to 3. A production-grade project scores **at least 2
in every area** and **3 in Correctness, Publication safety, and
Timeliness**.

| Area | What a "3" looks like |
| --- | --- |
| Correctness | Reconciled marts; incremental equals full refresh; no fan-out |
| Publication safety | WAP with atomic publish; failed audits never reach consumers |
| Timeliness | Deadline met with headroom; deadline alerts proven in drills |
| Modelling | Clear grain, conformed dimensions, SCD Type 2, documented marts |
| Incremental design | Measured lookback, change propagation, safe full refreshes |
| Testing | Data, unit, contract, reconciliation, DAG, and end-to-end tests |
| Orchestration | Asset-aware, thin DAGs; sensors, pools, retries, backfills |
| Delivery | Slim CI, artefact-based deferral, promotion, dependency isolation |
| Observability | Model-level metrics, lineage, docs site, actionable alerts |
| Documentation | Another engineer can operate and extend the platform |

---

## 12. Common pitfalls to avoid

- Running `dbt run` and `dbt test` separately so failed models are already
  published.
- Using `current_date` or `now()` in models instead of the run's data
  interval.
- Incremental models filtered only by `max(updated_at)` with no lookback.
- Business logic duplicated across marts instead of shared intermediate
  models.
- Installing dbt into the Airflow image and fighting dependency conflicts.
- One giant DAG that runs everything sequentially, or hundreds of tiny
  DAGs with timing-based dependencies.
- Catch-up enabled by accident, launching months of runs.
- CI that rebuilds the whole project on every pull request — or tests
  nothing.
- Credentials in `profiles.yml` or DAG files.
- Silent restatements of closed months.
- Alerts without owners or runbooks.

---

## 13. Suggested timeline

| Week | Milestones |
| --- | --- |
| 1 | M0 framing and platform · M1 sources and contracts |
| 2 | M2 extract–load · M3 dbt foundations |
| 3 | M4 dimensional marts · M5 incremental models and late data |
| 4 | M6 dbt testing and contracts · M7 Airflow orchestration |
| 5 | M8 quality gates and WAP · M9 backfills and closing · M10 platform testing → **Core track complete** |
| 6 | M11 packaging and secrets · M12 CI/CD and slim CI |
| 7 | M13 observability and lineage · M14 operations → **Production track complete** |
| 8 (optional) | M15 stretch goals |

---

## 14. What to show in a portfolio or interview

Be ready to explain:

1. Your layering (raw → staging → intermediate → marts) and why business
   logic lives where it does.
2. The grain of each fact and how you prevented fan-out.
3. How incremental models handle late data, and how you proved they equal a
   full refresh.
4. How write–audit–publish guarantees consumers never see failing marts.
5. How Airflow triggers the transform (assets, sensors) and handles late
   files and deadlines.
6. How you run dbt inside Airflow and why (ADR).
7. How slim CI works with deferral to production artefacts.
8. How backfills, logic changes, and month-end restatements are done
   safely.
9. What your drills revealed and what you changed.

A README with the architecture diagram, the dbt lineage graph, a short demo
(daily run, a blocked publication after an injected defect, a backfill, and
a slim CI run on a pull request), and the runbook will demonstrate that you
can run an analytics platform, not just write SQL models.
