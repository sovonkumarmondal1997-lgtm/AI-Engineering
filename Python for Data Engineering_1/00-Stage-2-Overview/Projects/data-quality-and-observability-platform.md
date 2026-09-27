# Project Roadmap — Data Quality and Observability Platform

This is the end-to-end roadmap for **Stage 2 Project 06: Data Quality and
Observability Platform**. It takes you from an empty repository to a
**production-grade** internal platform that watches a whole data estate —
warehouse tables, lakehouse tables, files, and Kafka topics — and answers
four questions continuously:

1. **Is the data correct?** (contracts, checks, reconciliation)
2. **Is it on time and behaving normally?** (freshness, volume, schema, and
   distribution monitors)
3. **If something is wrong, what is affected and who must act?** (lineage,
   impact analysis, alert routing, incidents)
4. **Can bad data be stopped before consumers see it?** (quality gates and
   circuit breakers for pipelines)

It is written as a sequence of **milestones**. Each milestone has a goal,
tasks, deliverables, and **acceptance criteria** you must meet before moving
on. The acceptance criteria are what make this production grade rather than
"a script that runs a few `COUNT(*)` queries".

---

## 1. Why this project matters

In every earlier project you added checks to *one* pipeline. In real
companies there are hundreds of pipelines owned by many teams, and data
problems rarely stay where they start: a late partner file makes a silver
table stale, which makes a gold table wrong, which makes a dashboard, an ML
model, and a finance report wrong. Without a platform:

- every team writes its own ad-hoc checks, differently;
- alerts arrive from five tools for one incident — or not at all;
- nobody knows which downstream tables and consumers are affected;
- bad data is published because pipelines have no way to ask "is this safe?";
- incidents are discovered by consumers, not engineers;
- nobody can say whether data quality is getting better or worse.

A data quality and observability platform turns quality from a per-pipeline
afterthought into a shared, self-service capability. Building one teaches
you to think like a platform engineer for data.

---

## 2. Project goal and scope

### Goal

Build `dq_platform`, a set of services and libraries that:

1. Holds a **registry** of datasets with owners, tiers, SLOs, and
   **contracts as code**.
2. **Executes checks** (schema, validity, uniqueness, integrity, freshness,
   volume, reconciliation, custom SQL) against several storage systems,
   incrementally per partition, on schedules and on data-update events.
3. **Profiles** datasets into a **metrics history** and runs **anomaly
   monitors** for freshness, volume, schema drift, and distribution drift.
4. Exposes a **gate API** that pipelines call before publishing
   (write–audit–publish and circuit breakers).
5. Collects **lineage** and provides **impact analysis** and root-cause
   hints.
6. **Routes alerts** to owners, groups related alerts into **incidents**,
   and informs data consumers.
7. Publishes **scorecards**, dashboards, and catalog quality status.
8. Is itself tested, deployed, secured, monitored, and easy to adopt.

### In scope

- The platform services, a realistic monitored data estate with an incident
  injector, integrations with Airflow, dbt, Spark, Kafka, and a catalog,
  and platform operations.

### Out of scope

- Building the data pipelines themselves (reuse **Projects 01–05**, or the
  simulated estate built in M1).
- A commercial-grade UI: use Grafana, the catalog UI, and an API instead of
  building a web front end (a simple UI is a stretch goal).

---

## 3. Prerequisites and when to do this project

**Recommended timing:** after completing **Modules 2.1–2.20** (it relies
heavily on Modules 2.11, 2.13, 2.19, and 2.20). It works best after you have
built at least two of Projects 01–05, so you have real pipelines to observe.

| Module | What this project uses from it |
| --- | --- |
| 2.1 Foundations | SLAs, dataset tiers, data as a product |
| 2.4 Columnar engines | DuckDB and Arrow for fast checks over files and lake tables |
| 2.6 SQL | Assertion queries, `EXCEPT`, window functions, pushdown-friendly checks |
| 2.7 Python DB connectivity | Connection pools, SQLAlchemy, read-only roles, Alembic |
| 2.8 Data modelling | Grain, keys, referential integrity |
| 2.9 Ingestion | Freshness and source contracts |
| 2.10 Concurrency | Running many checks in parallel with bounded concurrency |
| 2.11 Validation and quality | **Everything**: dimensions, Pydantic, Pandera, GX, Soda, contracts, schema evolution, quarantine, WAP, anomaly checks, reconciliation |
| 2.12 Pipeline design | Config-driven engines, state, idempotency |
| 2.13 Orchestration | Airflow integration, gates, sensors, assets |
| 2.15 Lakehouse table formats | Reading Delta/Iceberg metadata for cheap checks |
| 2.16 Streaming | Kafka lag, DLQ rates, streaming checks |
| 2.17 Cloud | Warehouse query cost, IAM |
| 2.18 Delivery | Images, CI/CD, secrets, environments |
| 2.19 Testing | Testing the platform itself, including with injected defects |
| 2.20 Observability and governance | **Everything**: metrics, OpenTelemetry, alerting and on-call, OpenLineage, catalogs, PII, incident response |
| 2.21 Performance and cost | Cost of checks, pushdown, sampling |
| 2.22 Serving | FastAPI for the gate and platform APIs |

### Tracks

| Track | Milestones | Result |
| --- | --- | --- |
| **Core track** | M0–M11 | A working, tested platform observing a realistic estate, detecting and routing injected incidents |
| **Production track** | M12–M14 | Secure, self-service, reliable platform that other teams can adopt |

**Estimated effort:** Core track 5–6 weeks; Production track 2–3 weeks (at
8–10 hours per week).

---

## 4. The scenario

You are the first engineer on ShopLite's new **Data Reliability** team.
Last quarter:

- a partner file arrived with amounts in cents, inflating revenue for two
  days before finance noticed;
- a source renamed a column and a silver table silently filled with NULLs;
- a streaming consumer fell behind for six hours without anyone knowing;
- a duplicated batch doubled order counts in the marketing dashboard;
- three teams each got alerts about the same broken upstream table, and
  none of them owned it.

Leadership asks for a platform that every data team can use.

### Monitored data estate

| System | Datasets (examples) |
| --- | --- |
| PostgreSQL warehouse | `raw.*`, `staging.*`, `marts.daily_revenue`, `marts.channel_performance` (Project 03) |
| Lakehouse (Delta/Iceberg on MinIO) | `bronze.events`, `silver.orders`, `silver.dim_customer`, `gold.daily_kpis` (Projects 02 and 04) |
| Files | Partner landing files with control totals |
| Kafka | `clean.orders`, `alerts.risk`, DLQ topics, consumer groups (Project 05) |
| Pipelines | Airflow DAGs, dbt runs, Spark jobs emitting run and lineage events |

### Platform service-level objectives (write them down in M0)

- **Detection:** critical incidents on tier-1 datasets are detected within
  **15 minutes** of the bad data landing (or of a freshness deadline being
  missed).
- **Precision:** fewer than **10%** of paging alerts are false positives
  (measured weekly).
- **Gates:** gate decisions are returned in under **1 second** at p95, and
  the gate service is available **99.9%** of the time during pipeline
  windows (with a documented fail-open or fail-closed policy per tier).
- **Coverage:** 100% of tier-1 datasets have contracts, owners, freshness
  SLOs, and critical checks.
- **Onboarding:** a team can onboard a new dataset in **under 30 minutes**
  with a pull request.
- **Cost:** quality checks consume less than an agreed share of warehouse
  and compute cost (e.g. 5%).

---

## 5. Target architecture

```text
                       ┌─────────────────────────────────────────────┐
  contracts/ (YAML) ──►│ Registry & contracts service                 │◄── CI validation
  owners, tiers, SLOs  │  datasets · owners · tiers · SLOs · checks   │
                       └───────────────┬─────────────────────────────┘
                                       │
   Pipelines (Airflow, dbt, Spark,     ▼
   Kafka jobs) ── run & lineage ──► Event intake ──► Scheduler / trigger (schedule + on-update)
   events (OpenLineage)                │                         │
                                       ▼                         ▼
                              Lineage store (Marquez)    Check runner (bounded parallel)
                                       │                   adapters: SQL · DuckDB (files, Delta, Iceberg)
                                       │                             · Spark (large) · Kafka (lag, DLQ, samples)
                                       │                   optional backends: Soda / Great Expectations / Pandera
                                       │                         │
                                       │                         ▼
                                       │               Results & metrics store (PostgreSQL)
                                       │                check_results · metric_history · schema_snapshots
                                       │                         │
                                       │                         ▼
                                       │               Monitors (freshness · volume · schema · distribution)
                                       │                         │
                                       ▼                         ▼
                          Impact analysis ◄──────── Incident manager ──► Alert routing (owners, tiers)
                                                         │                  → Alertmanager / chat / email
  Pipelines ── "may I publish?" ──► Gate API (FastAPI) ◄──┘                → consumer status page
                                                         │
                               Catalog sync (OpenMetadata / DataHub) · Grafana scorecards & SLO dashboards
                               Meta-monitoring: the platform monitors itself
```

### Technology choices (defaults)

| Concern | Default | Notes |
| --- | --- | --- |
| Language and services | Python, FastAPI, Pydantic | Module 2.22 |
| Platform database | PostgreSQL with Alembic migrations | Registry, results, metrics, incidents |
| Contracts | YAML inspired by open data-contract standards, validated with Pydantic | Module 2.11 |
| Check execution | Own check library generating SQL; DuckDB for Parquet/Delta/Iceberg; Spark for very large tables | Optional Soda/GX backends behind the same interface (ADR) |
| Scheduling | Airflow (scheduled runs and on-asset-update triggers) | Or the platform's own scheduler |
| Lineage | OpenLineage (Airflow provider, Spark, dbt) → Marquez | Module 2.20 |
| Catalog | OpenMetadata or DataHub | One of them |
| Alerting | Prometheus Alertmanager or your own notifier with routing | Module 2.20 |
| Dashboards | Grafana | Scorecards and SLOs |
| Telemetry | Prometheus metrics, OpenTelemetry traces, structured logs | For the platform itself |
| Delivery | Docker, Compose or Kubernetes, GitHub Actions | Module 2.18 |

Record decisions as **ADRs**: build vs buy for checks, contract format,
anomaly methods, gate fail-open/fail-closed policy, and alert grouping
strategy.

---

## 6. Repository structure

```text
dq-platform/
├── README.md
├── pyproject.toml / uv.lock
├── docker-compose.yml               # platform services + monitored estate + marquez + catalog + monitoring
├── docs/
│   ├── requirements.md              # stakeholders, SLOs, tiers, non-goals
│   ├── architecture.md
│   ├── contract-spec.md             # the YAML contract format
│   ├── check-library.md             # every check type, parameters, SQL semantics
│   ├── monitors.md                  # anomaly methods, tuning, evaluation results
│   ├── adr/
│   ├── onboarding.md                # how a team onboards a dataset
│   └── runbook.md
├── contracts/                       # one YAML per dataset (owners, tier, schema, checks, SLOs)
├── estate/                          # the monitored estate simulator and incident injector
├── src/dq_platform/
│   ├── registry/                    # dataset registry, contract parsing and validation
│   ├── checks/                      # check definitions → SQL / DataFrame operations
│   ├── adapters/                    # postgres, duckdb (files, delta, iceberg), spark, kafka
│   ├── runner/                      # scheduling, triggering, bounded execution, results writing
│   ├── profiling/                   # metrics collection, sketches, schema snapshots
│   ├── monitors/                    # freshness, volume, schema, distribution detectors
│   ├── gates/                       # gate API and decision logic
│   ├── lineage/                     # OpenLineage intake, impact analysis
│   ├── incidents/                   # grouping, lifecycle, routing, notifications
│   ├── catalog_sync/                # push status to the catalog
│   ├── reporting/                   # scorecards, weekly reports
│   └── observability/               # platform self-monitoring
├── integrations/
│   ├── airflow/                     # gate operator/sensor, callbacks, asset triggers
│   ├── dbt/                         # ingest dbt run_results and test results
│   └── spark/                       # helper to call gates and emit metrics from jobs
├── migrations/
├── dashboards/                      # Grafana dashboards as code
├── tests/
│   ├── unit/  property/  integration/  e2e/
│   └── incidents/                   # labelled incident scenarios for detection evaluation
└── .github/workflows/
```

---

## 7. Milestones overview

```text
Core track
  M0   Project framing: stakeholders, tiers, and platform SLOs
  M1   The monitored estate and the incident injector
  M2   Metadata model and registry
  M3   Contracts and checks as code
  M4   The check execution engine
  M5   Profiling, metrics history, and schema drift
  M6   Anomaly monitors and their evaluation
  M7   Quality gates and circuit breakers
  M8   Lineage and impact analysis
  M9   Alerting, incident grouping, and consumer communication
  M10  Catalog integration, scorecards, and reporting
  M11  Testing the platform

Production track
  M12  Packaging, deployment, security, and privacy
  M13  CI/CD and self-service onboarding
  M14  Platform reliability, scale, cost, operations, and adoption
  (M15 Optional stretch goals)
```

Commit and tag at the end of every milestone (`m0`, `m1`, …).

---

## 8. Core track

### M0 — Project framing: stakeholders, tiers, and platform SLOs

**Goal:** Know who the platform serves, what "good" means, and how the
platform itself will be judged.

**Tasks**

1. Interview-style exercise: write short personas for a data producer, a
   pipeline owner, a data consumer (analyst, finance), and an on-call
   engineer; list what each needs from the platform.
2. Define **dataset tiers** (e.g. tier 1 = finance and executive data, tier
   2 = team data, tier 3 = exploratory) with required checks, freshness
   SLOs, alert severity, and gate policy per tier (Module 2.1).
3. Write the platform SLOs from Section 4 in `docs/requirements.md`, plus
   non-goals.
4. Draw the architecture (Section 5) and write ADRs for build vs buy of
   check execution, the contract format, and the gate failure policy.
5. Set up the repository, `uv`, Ruff, type checking, pytest, `pre-commit`,
   and the Compose stack skeleton.

**Acceptance criteria**

- [ ] Tiers and their obligations are written in one table.
- [ ] Platform SLOs are measurable (detection time, precision, gate latency,
      coverage, onboarding time, cost).
- [ ] The build-vs-buy ADR states what you build, what you reuse, and why.

---

### M1 — The monitored estate and the incident injector

**Goal:** A realistic set of datasets and pipelines to observe — and a way to
create every kind of data incident on demand, with known ground truth.

**Tasks**

1. **Reuse** outputs of Projects 01–05 where available, or build a compact
   simulated estate:
   - PostgreSQL warehouse schemas (`raw`, `staging`, `marts`);
   - lakehouse tables (Delta or Iceberg on MinIO) for bronze, silver, gold;
   - a partner-file landing zone with trailer control totals;
   - Kafka topics with a consumer group and a DLQ;
   - a small set of Airflow DAGs (and optionally a dbt project and a Spark
     job) that update these datasets daily and hourly, emitting OpenLineage
     events.
2. Generate **several months of normal history** with realistic
   seasonality (weekday/weekend, month-end, holidays, promotions) so
   monitors have baselines.
3. Build an **incident injector** that can create, on a chosen dataset and
   time, each incident type with a recorded ground-truth label:
   - late or missing data (freshness);
   - volume drop or spike;
   - duplicate batch;
   - null-rate spike in a column;
   - schema change (renamed, dropped, retyped column);
   - distribution shift (e.g. amounts ×100 — the "cents" incident);
   - referential integrity break (orphan keys);
   - source-vs-target mismatch (reconciliation);
   - Kafka consumer lag growth and DLQ surge;
   - personal data appearing in a column that should not contain it.
4. Store ground-truth labels for later evaluation of detection (M6, M11).

**Acceptance criteria**

- [ ] The estate runs daily/hourly updates end to end and emits lineage
      events.
- [ ] Every incident type can be injected with one command and is labelled.
- [ ] At least 90 days of normal history exist for baselines.

---

### M2 — Metadata model and registry

**Goal:** One authoritative place describing every monitored dataset and
every result the platform produces.

**Tasks**

1. Design the platform database (with Alembic migrations):
   - `datasets` (id, system, location, domain, owner team, tier, grain,
     keys, partitioning, SLOs, status);
   - `contracts` and `contract_versions`;
   - `checks` (generated from contracts: type, parameters, severity,
     schedule/trigger, scope);
   - `check_runs` and `check_results` (run id, dataset, partition, check,
     observed value, threshold, status, sample reference, duration, cost
     estimate);
   - `metric_history` (dataset, partition, metric, value, time);
   - `schema_snapshots`;
   - `incidents`, `incident_events`, `alerts`;
   - `gate_decisions` and `gate_overrides`.
2. Build a **registry API** (FastAPI, read-only for most callers) to list
   datasets, owners, contracts, latest status, and SLO compliance.
3. Decide retention for results and metrics (and aggregation of old data).

**Acceptance criteria**

- [ ] Every table has documented grain and keys; migrations run up and down.
- [ ] The registry API returns any dataset's owner, tier, SLOs, contract
      version, and latest status in under 200 ms.

---

### M3 — Contracts and checks as code

**Goal:** Teams describe expectations declaratively; the platform turns them
into executable checks. Invalid contracts never reach production.

**Tasks**

1. Write the **contract specification** (`docs/contract-spec.md`), inspired
   by open data-contract standards (Module 2.11): dataset identity, owner,
   tier, description, schema (columns, types, nullability, keys), semantics
   (units, allowed values), freshness SLO, volume expectations, quality
   checks with severities, partitioning for incremental checks, consumers,
   and version.
2. Implement **Pydantic models** for the specification; validate every
   contract file in CI with clear errors.
3. Implement the **check library** (`docs/check-library.md`), each check
   with defined semantics, SQL/DataFrame implementation, and parameters:
   - schema: expected columns and types, no unexpected columns;
   - validity: not null, accepted values, ranges, regex patterns;
   - uniqueness: single and composite keys;
   - integrity: foreign keys to another dataset (no orphans);
   - freshness: latest event or load timestamp vs SLO;
   - volume: row count within bounds per partition;
   - reconciliation: counts and sums vs a source or control totals;
   - custom SQL: returns zero rows when passing (Module 2.6);
   - streaming: consumer lag, DLQ rate, schema id changes.
4. Implement **severity and thresholds** (warn/error/critical; allowed
   failure rate) and link each check to its dataset tier.
5. Write contracts for **every tier-1 dataset** in the estate and for at
   least half of the rest.

**Acceptance criteria**

- [ ] Contracts for all tier-1 datasets exist and pass validation in CI.
- [ ] Every check type has unit tests of its semantics, including NULL
      handling and empty partitions.
- [ ] An invalid contract (unknown check, wrong type, missing owner) fails
      CI with a clear message.

---

### M4 — The check execution engine

**Goal:** Run thousands of checks correctly, cheaply, and quickly across
different storage systems — scheduled or triggered by data updates.

**Tasks**

1. Define an **adapter interface** (connect, run a query or DataFrame
   operation, get table metadata, estimate cost) and implement adapters for:
   - PostgreSQL / warehouse via SQLAlchemy or psycopg (read-only role —
     Module 2.7);
   - DuckDB for Parquet files and Delta/Iceberg tables on object storage;
   - Spark for very large tables (optional);
   - Kafka (consumer lag and DLQ metrics via the admin API, and sampled
     message validation against schemas).
2. **Compile** checks into efficient queries: combine many checks on one
   table into one scan where possible; always filter to the **partition**
   being validated (incremental checks — Modules 2.12, 2.21); use table
   metadata (row counts, file statistics, Delta/Iceberg metadata) before
   full scans.
3. Implement **triggers**: scheduled runs (e.g. hourly, daily) and
   **on-update** runs when a lineage or asset event says a dataset
   partition changed (Module 2.13).
4. Run checks with **bounded concurrency** per system (Module 2.10) and
   timeouts; never overload a source.
5. Write results **idempotently** (re-running the same check for the same
   partition updates, not duplicates, the result).
6. Store **failure samples** safely: store row keys and a small number of
   masked example values — never raw personal data (Module 2.20).
7. Optionally implement **Soda or Great Expectations backends** behind the
   same interface and compare (ADR).

**Acceptance criteria**

- [ ] All contract checks run across all systems for a day's partitions
      within a set time budget.
- [ ] Checks triggered by a dataset update complete within 5 minutes of the
      update event.
- [ ] Re-running checks produces no duplicate results.
- [ ] Failure samples contain no raw personal data.
- [ ] Every injected incident detectable by a rule (duplicates, nulls,
      orphans, reconciliation, schema) is caught by the right check.

---

### M5 — Profiling, metrics history, and schema drift

**Goal:** Collect the measurements that let the platform notice problems no
one wrote a rule for.

**Tasks**

1. Build a **profiler** that, per dataset partition, records: row count,
   null rate and distinct count per column (approximate distinct counts with
   sketches for large tables), numeric min/max/mean/percentiles, top
   category shares, string length stats, and latest timestamps.
2. Store profiles in `metric_history` efficiently; profile incrementally
   (only new or changed partitions).
3. Record **schema snapshots** on every run and detect **schema drift**
   (added, removed, renamed-looking, retyped columns), classified with the
   compatibility rules from Module 2.11.
4. Use cheap sources first: table metadata, file statistics, Delta/Iceberg
   metadata, and warehouse information schema; fall back to scans only when
   needed.
5. Measure profiling cost and duration per dataset.

**Acceptance criteria**

- [ ] 90 days of history are profiled for every monitored dataset.
- [ ] Schema drift is detected and classified within one run of the change.
- [ ] Profiling stays within its cost budget (from M0).

---

### M6 — Anomaly monitors and their evaluation

**Goal:** Detect the unknown unknowns — with measured precision and recall,
not guesswork.

**Tasks**

1. Implement monitors (Modules 2.11, 2.20):
   - **freshness:** latest data vs SLO deadline, and "no update when one was
     expected" based on the dataset's update pattern;
   - **volume:** row count vs a **seasonal baseline** (same weekday, rolling
     median and median absolute deviation, holiday calendar);
   - **null rate and distinct count** changes;
   - **distribution drift:** numeric shifts (e.g. KS test, population
     stability index), category share shifts (e.g. chi-square), and simple
     ratio checks for unit errors (×100, ×1,000);
   - **schema drift** from M5;
   - **streaming:** lag growth rate and projected time to breach retention;
     DLQ rate spikes.
2. Account for **practical vs statistical significance** on large datasets
   (minimum effect sizes).
3. **Evaluate** monitors against the labelled incident scenarios from M1:
   precision, recall, and detection delay per monitor and per incident type;
   record results in `docs/monitors.md`.
4. **Tune** thresholds and seasonality until you meet the platform's
   precision target, and document every choice.
5. Add a **feedback loop**: owners can mark an alert as a false positive or
   expected change (e.g. a promotion), which adjusts baselines or silences
   with an expiry and an audit record.

**Acceptance criteria**

- [ ] All injected incidents in the labelled set are detected (by a check
      or a monitor) within the detection SLO.
- [ ] Paging-level false positives on 90 days of clean history stay below
      the precision target.
- [ ] The "cents" incident (amounts ×100) and the renamed-column incident
      are both detected before the affected data is published (with gates —
      M7).
- [ ] Feedback changes are audited and expire.

---

### M7 — Quality gates and circuit breakers

**Goal:** Pipelines can ask the platform whether it is safe to publish — and
bad data is stopped automatically.

**Tasks**

1. Build the **gate API**:
   `POST /gates/evaluate` with dataset, partition, run id, and (optionally)
   the staging location to check; the platform runs or looks up the required
   checks and monitors for the dataset's tier and returns `pass`, `warn`, or
   `fail` with reasons and links.
2. Define **policies per tier**: which failures block publication, and the
   **fail-open vs fail-closed** behaviour when the platform itself is
   unavailable (e.g. tier 1 fail-closed, tier 3 fail-open) — documented in
   an ADR.
3. Build **integrations**:
   - an Airflow operator or deferrable sensor that calls the gate and fails
     or branches the DAG (Module 2.13);
   - a Python helper for Spark and other jobs;
   - an ingestion hook for dbt results (parse `run_results.json` and test
     results into the platform).
4. Implement **circuit breakers**: when an upstream dataset is failing,
   downstream pipelines are paused (or their gates fail) automatically, with
   a clear reason.
5. Implement an **override workflow**: an authorised person can override a
   failed gate with a reason; overrides are time-limited and audited.
6. Wire gates into the estate's **write–audit–publish** flows (Module 2.11).

**Acceptance criteria**

- [ ] Injected incidents on tier-1 datasets are blocked at the gate; the
      previous published version stays visible to consumers.
- [ ] Gate decisions return in under 1 second at p95 for pre-computed
      results.
- [ ] Downstream pipelines pause automatically when an upstream tier-1
      dataset fails.
- [ ] Every override is recorded with who, why, and until when.

---

### M8 — Lineage and impact analysis

**Goal:** For any problem, know instantly what is affected downstream, who
must be told, and which upstream issue probably caused it.

**Tasks**

1. Collect **OpenLineage** events from Airflow, Spark, and dbt into Marquez;
   emit custom events from estate scripts with the Python client (Module
   2.20); enforce consistent dataset naming shared with the registry.
2. Build an **impact analysis** service: given a dataset (and optionally a
   column), return all downstream datasets, their owners and tiers, known
   consumers (dashboards, models), and whether each has already consumed the
   bad partition.
3. Build **root-cause hints**: given a failing dataset, list upstream
   datasets with recent failures, schema changes, late updates, or unusual
   metrics — ranked by recency and lineage distance.
4. Show lineage and impact in incident notifications (M9) and the catalog
   (M10).
5. Detect **lineage gaps** (datasets in the registry without lineage events)
   and report them.

**Acceptance criteria**

- [ ] For each injected incident, the impacted downstream datasets and
      owners are listed correctly.
- [ ] For downstream symptoms (e.g. a wrong gold table), the root-cause
      hints rank the injected upstream cause first in most scenarios
      (measure it).
- [ ] Lineage gaps are reported with the responsible owner.

---

### M9 — Alerting, incident grouping, and consumer communication

**Goal:** The right people learn about the right problem once, with enough
context to act — and consumers are told what they can trust.

**Tasks**

1. Implement **alert routing** by dataset owner, domain, and tier (Module
   2.20): page for tier-1 critical failures, ticket for tier-2, digest for
   tier-3.
2. Implement **incident grouping**: failures that share an upstream cause
   (via lineage and timing) are grouped into one incident; downstream
   alerts are **suppressed** or attached to the upstream incident instead of
   paging every team.
3. Implement the **incident lifecycle**: `open` → `acknowledged` →
   `mitigated` → `resolved`, with timestamps, assignee, impact list, and
   links to checks, lineage, runbooks, and dashboards.
4. Send **notifications** (chat/email/webhook) with context: what failed,
   since when, impact, suspected cause, runbook, and a link to the incident.
5. Build a **data status page** (or catalog banner) that tells consumers
   which datasets are currently degraded and since when.
6. Track **MTTD and MTTR** per incident, and provide a **post-mortem
   template** pre-filled from the incident timeline (Module 2.20).

**Acceptance criteria**

- [ ] An injected upstream failure affecting five downstream datasets
      produces **one** incident and one page to the upstream owner, with the
      downstream owners informed but not paged.
- [ ] Every notification contains owner, impact, suspected cause, and a
      runbook link.
- [ ] Consumers can see the status of any dataset without asking an
      engineer.
- [ ] MTTD and MTTR are recorded for every incident.

---

### M10 — Catalog integration, scorecards, and reporting

**Goal:** Quality and reliability are visible to everyone and improve over
time.

**Tasks**

1. **Catalog sync:** push quality status, last successful check, freshness,
   contract version, owners, and incident banners to OpenMetadata or DataHub
   for every dataset (Module 2.20).
2. **Grafana dashboards as code:**
   - dataset health (checks, monitors, freshness, recent incidents);
   - domain and team **scorecards** (pass rates by quality dimension,
     SLO compliance, coverage of contracts and checks);
   - platform SLOs (detection time, precision, gate latency, cost of checks);
   - error budgets for dataset freshness SLOs.
3. A weekly **quality report** generated automatically: incidents, SLO
   compliance, top noisy checks, coverage gaps, and trends.
4. Show **coverage**: datasets without owners, contracts, or tier-required
   checks.

**Acceptance criteria**

- [ ] Any dataset's quality status is visible in the catalog.
- [ ] Scorecards show trends per team and domain over the simulated months.
- [ ] The weekly report is generated without manual work and highlights
      coverage gaps.

---

### M11 — Testing the platform

**Goal:** The platform that others trust must itself be trustworthy.

**Tasks**

1. **Unit tests:** contract validation, check compilation to SQL (golden
   SQL snapshots), check semantics, monitor statistics, grouping logic,
   routing rules, gate policies.
2. **Property tests** (Module 2.19): uniqueness checks agree with a Python
   reference on random data; volume monitors produce no alerts on synthetic
   seasonal series without anomalies and detect injected spikes above a
   minimum size; incident grouping is order-independent.
3. **Integration tests** with Testcontainers: adapters against PostgreSQL,
   DuckDB over MinIO Parquet/Delta/Iceberg, and Kafka; gate API with Airflow
   integration; lineage intake from real OpenLineage events.
4. **End-to-end scenario tests:** for each labelled incident type — inject,
   run the estate, assert detection within SLO, gate blocking, a single
   grouped incident, correct routing, catalog and status updates, and
   resolution after the fix.
5. **Regression tests** for every missed detection or false alarm found
   during tuning.

**Acceptance criteria**

- [ ] Every incident type has an automated end-to-end scenario test that
      passes.
- [ ] Removing incident grouping, the fail-closed policy, or partition
      filtering fails a test.
- [ ] No flaky tests across 20 runs.

**At the end of M11 you have completed the Core track.** Tag the repository
`core-complete` and write a retrospective.

---

## 9. Production track

### M12 — Packaging, deployment, security, and privacy

**Goal:** A secure platform that can safely connect to every data system in
the company.

**Tasks**

1. Build images for the platform services (registry/gate API, runner,
   monitors, incident manager, catalog sync) and deploy them with Compose or
   Kubernetes (Module 2.18), with health checks and resource limits.
2. Use **read-only, least-privilege** roles into every monitored system;
   separate credentials per system and environment; secrets from a secrets
   manager (Modules 2.17, 2.18).
3. Protect the platform API with authentication and authorisation (teams can
   manage only their own contracts, silences, and overrides).
4. **Privacy:** never store raw personal data in results or samples; mask
   samples; add a PII detector for columns (Module 2.20) that raises a
   contract violation when personal data appears where it is not declared.
5. Enforce TLS for all connections outside local development.

**Acceptance criteria**

- [ ] The platform cannot write to any monitored system.
- [ ] A team cannot override gates or silence alerts for another team's
      datasets.
- [ ] A scan of the platform database finds no raw personal data.

---

### M13 — CI/CD and self-service onboarding

**Goal:** Teams onboard and evolve their datasets through pull requests, and
platform changes ship safely.

**Tasks**

1. **Contract pull-request pipeline:** validate contracts, detect breaking
   contract changes (Module 2.11), **dry-run** new or changed checks against
   the dataset in a staging environment and show results and estimated cost
   in the pull request.
2. **Platform CI/CD:** lint, types, unit, property, integration, and
   scenario tests; image build and scan; deploy to `dev` → `staging` →
   `prod` with the scenario suite as a gate; database migrations in order.
3. **Onboarding guide** (`docs/onboarding.md`) and a template contract; a
   command that scaffolds a contract from an existing table's schema and
   profile (to be reviewed and tightened by the owner).
4. Measure onboarding time with someone unfamiliar with the platform.

**Acceptance criteria**

- [ ] A new dataset is onboarded in under 30 minutes via one pull request,
      with dry-run results visible before merge.
- [ ] A contract change that would break consumers fails CI with an
      explanation.
- [ ] Platform deployments are promoted with the scenario tests as a gate.

---

### M14 — Platform reliability, scale, cost, operations, and adoption

**Goal:** The platform is reliable, affordable, operable, and actually
used.

**Tasks**

1. **Meta-monitoring:** monitor the platform itself — missed check
   schedules, runner backlog, check duration trends, gate API errors and
   latency, lineage intake delays — and add a **dead man's switch** alert
   that fires if the platform stops reporting.
2. **Scale test:** simulate 1,000 datasets and 20,000 checks; measure
   runtime, database size, and cost; optimise (batching checks per table,
   metadata-first checks, sampling for tier-3, result aggregation).
3. **Cost of quality:** tag every query the platform runs; report cost per
   dataset and per check; keep total cost within the M0 budget (Module
   2.21).
4. **Runbook** (`docs/runbook.md`): platform outage (and what fail-open and
   fail-closed mean for pipelines), backlog recovery, re-running checks for a
   period, bulk silencing during planned maintenance, restoring from backup,
   rotating credentials.
5. **Drills:** gate service down during a tier-1 pipeline run; platform
   database unavailable; a flood of incidents after a large upstream outage;
   a bad platform release producing false alarms (rollback).
6. **Adoption metrics:** datasets onboarded, coverage by tier, active users,
   alert precision trend, MTTD/MTTR trend; a short plan to increase adoption.
7. **Hand-over:** walkthrough and final retrospective.

**Acceptance criteria**

- [ ] The dead man's switch fires when the platform is stopped.
- [ ] The scale test meets its runtime and cost targets.
- [ ] All drills end with pipelines behaving according to the documented
      policies and no silent data incidents.
- [ ] Adoption and reliability metrics are reported on a dashboard.

---

### M15 — Optional stretch goals

- **Simple web UI** for dataset health, incidents, and overrides.
- **Advanced anomaly detection:** forecasting-based baselines or
  multivariate detectors; compare precision and recall with your
  statistical monitors.
- **Producer-side contracts:** run contract checks in producer teams' CI
  (for example on schema migrations in the source database of Project 02).
- **Streaming data quality:** validate samples of Kafka events in real time
  and quarantine bad events (Project 05 integration).
- **AI-assisted summaries:** generate incident summaries from structured
  incident data, lineage, and check results — always with links to evidence
  and never as the sole source of truth.
- **Standard compliance:** export contracts to an open data-contract format
  and test round-trips.

---

## 10. Definition of done

**Detection and prevention**

- [ ] Every labelled incident type is detected within the detection SLO.
- [ ] Tier-1 incidents are blocked at gates before consumers see them.
- [ ] Monitors meet the precision target on clean history.

**Response**

- [ ] Related failures become one incident, routed to the upstream owner
      with impact, suspected cause, and runbook.
- [ ] Consumers can see dataset status; MTTD and MTTR are measured.

**Coverage and adoption**

- [ ] 100% of tier-1 datasets have contracts, owners, SLOs, and critical
      checks.
- [ ] Onboarding a dataset takes under 30 minutes via pull request.

**Platform quality**

- [ ] Tested with unit, property, integration, and scenario tests.
- [ ] Secure (read-only access, authorisation, no personal data stored).
- [ ] Reliable (meta-monitoring, dead man's switch, documented fail-open or
      fail-closed policies), scalable, and within its cost budget.
- [ ] Documentation complete: requirements, contract spec, check library,
      monitors evaluation, ADRs, onboarding guide, runbook, retrospective.

---

## 11. Evaluation rubric (self or peer review)

Score each area from 0 to 3. A production-grade project scores **at least 2
in every area** and **3 in Detection, Prevention, and Incident handling**.

| Area | What a "3" looks like |
| --- | --- |
| Detection | Every incident type detected within SLO, measured against ground truth |
| Precision | Measured false-positive rate below target; feedback loop working |
| Prevention | Gates and circuit breakers block tier-1 incidents; policies documented |
| Incident handling | Lineage-aware grouping, correct routing, consumer communication, MTTD/MTTR |
| Contracts and checks | Clear spec, CI validation, efficient incremental execution across systems |
| Lineage | Consistent naming, impact analysis, useful root-cause hints, gap reporting |
| Visibility | Catalog status, scorecards, SLO dashboards, weekly reports |
| Platform engineering | Tests, security, privacy, CI/CD, meta-monitoring |
| Scale and cost | Scale test passed; cost of quality measured and within budget |
| Adoption | Self-service onboarding, documentation, and adoption metrics |

---

## 12. Common pitfalls to avoid

- Hundreds of low-value checks and no owners — noise instead of signal.
- Static thresholds on seasonal data.
- Full-table scans for every check instead of partition-scoped and
  metadata-first checks.
- Storing failing rows with personal data in the results database.
- Alerting every downstream team for one upstream problem.
- Gates with no defined behaviour when the platform itself is down.
- Monitors that are never evaluated against real or labelled incidents.
- Contracts edited in a UI with no review or history.
- A platform nobody monitors — and that fails silently.
- Measuring success by number of checks rather than incidents prevented,
  detection time, and precision.

---

## 13. Suggested timeline

| Week | Milestones |
| --- | --- |
| 1 | M0 framing · M1 monitored estate and incident injector |
| 2 | M2 metadata model and registry · M3 contracts and checks as code |
| 3 | M4 check execution engine · M5 profiling and schema drift |
| 4 | M6 anomaly monitors and evaluation · M7 gates and circuit breakers |
| 5 | M8 lineage and impact · M9 alerting and incidents |
| 6 | M10 catalog, scorecards, reporting · M11 testing → **Core track complete** |
| 7 | M12 deployment, security, privacy · M13 CI/CD and onboarding |
| 8 | M14 reliability, scale, cost, operations → **Production track complete** |
| 9 (optional) | M15 stretch goals |

---

## 14. What to show in a portfolio or interview

Be ready to explain:

1. How tiers drive checks, alert severity, and gate policies.
2. Your contract specification and how contracts become efficient checks.
3. How monitors handle seasonality, and your measured precision and recall.
4. How gates and circuit breakers stopped the "cents" and renamed-column
   incidents before publication.
5. How lineage turns many alerts into one incident with the right owner.
6. How you kept checks cheap at scale and measured the cost of quality.
7. How you protected personal data inside a quality platform.
8. How the platform monitors itself and what happens when it is down.
9. How teams onboard themselves, and how you measured adoption.

A README with the architecture diagram, a short demo (inject an incident →
detection → blocked gate → one grouped incident with impact → fix →
resolution → post-mortem), the monitors evaluation table, and the onboarding
guide shows that you can build data reliability as a platform — not just
write checks for one pipeline.
