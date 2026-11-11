# Project Roadmap — Lakehouse Medallion Pipeline with PySpark and Delta Lake

This is the end-to-end roadmap for **Stage 2 Project 04: Lakehouse
Medallion Pipeline with PySpark and Delta Lake**. It takes you from an empty
repository to a **production-grade** batch lakehouse that ingests large,
messy raw files into **bronze**, turns them into clean, conformed,
deduplicated **silver** tables, and publishes business-ready **gold**
tables — using **PySpark** at scale and **Delta Lake** for reliable,
versioned tables.

It is written as a sequence of **milestones**. Each milestone has a goal,
tasks, deliverables, and **acceptance criteria** you must meet before moving
on. The acceptance criteria are what make this production grade rather than
"a Spark notebook that ran on a sample".

---

## 1. Why this project matters

Medallion (bronze → silver → gold) pipelines on Spark and Delta Lake are the
backbone of many modern data platforms. They are also where data volume
turns small mistakes into large incidents:

- raw files with a few corrupt lines crash the whole job — or are silently
  dropped;
- duplicated events inflate conversion rates;
- a rerun of one day overwrites the whole table;
- one "hot" product or bot user makes one task run for an hour;
- thousands of tiny files make every query slow;
- a bad deployment corrupts gold tables, and nobody can roll back;
- storage grows forever, and deleted customers are still in old files.

This project makes you build a medallion lakehouse that is correct at
scale, fast, recoverable, and cheap to run.

---

## 2. Project goal and scope

### Goal

Build `medallion_lakehouse`, a daily batch platform that:

1. **Ingests** new raw files incrementally into **bronze Delta tables**,
   keeping every record (including corrupt ones) with full provenance.
2. Builds **silver** tables: typed, validated, deduplicated, conformed, with
   late data handled, sessionised clickstream, and SCD Type 2 dimensions
   maintained with Delta `MERGE`.
3. Builds **gold** tables: facts, daily KPIs, funnels, product performance,
   and a customer feature table — incrementally and idempotently.
4. Enforces **quality gates** and **write–audit–publish** so bad data never
   reaches gold consumers, with **time travel** for rollback.
5. Is **tuned** for scale (partitioning, skew, joins, file layout) with
   measured evidence.
6. Is **maintained** (compaction, clustering, vacuum, retention) and honours
   **erasure** requests across all layers.
7. Is orchestrated, tested, deployed through CI/CD, observed, and operable.

### In scope

- Large synthetic sources, landing zone, bronze/silver/gold Delta tables,
  PySpark jobs, Delta features (`MERGE`, constraints, schema evolution,
  change data feed, time travel, restore, clustering, `OPTIMIZE`,
  `VACUUM`), quality, performance tuning, maintenance, privacy, testing,
  orchestration, deployment, and operations.

### Out of scope (covered by other Stage 2 projects)

- API ingestion → **Project 01**.
- Log-based CDC and streaming merges into Iceberg → **Project 02**.
- Warehouse ELT with dbt → **Project 03**.
- Real-time streaming analytics → **Project 05**.
- The full data-quality and observability platform → **Project 06**.

---

## 3. Prerequisites and when to do this project

**Recommended timing:** after completing **Modules 2.1–2.15**. The
production-hardening milestones (M11–M14) use Modules 2.13 and 2.17–2.21.
If you have not studied those yet, complete the **Core track** now and
return for the **Production track** later.

| Module | What this project uses from it |
| --- | --- |
| 2.1 Foundations | Medallion layers, lakehouse architecture, SLAs |
| 2.5 Data formats | JSON Lines, CSV, Parquet, nested data, partitioning, small files, compression |
| 2.6 SQL | Window functions, dedupe patterns, `MERGE`, SCD Type 2 |
| 2.8 Data modelling | Grain, facts and dimensions, OBT, event and clickstream modelling, point-in-time features |
| 2.11 Validation and quality | Quality dimensions, quarantine, thresholds, WAP, reconciliation |
| 2.12 Pipeline design | Data intervals, idempotent loads, incremental processing, late data, hashing, state |
| 2.14 PySpark | **Everything**: DataFrames, SQL, joins, partitioning, skew, caching, UDFs, plans, AQE, I/O, Spark UI, testing |
| 2.15 Lakehouse table formats | **Delta Lake**: transaction log, `MERGE`, time travel, restore, clustering, `OPTIMIZE`, `VACUUM`, catalogs |
| 2.13 Orchestration *(production track)* | Airflow DAGs, backfills, maintenance scheduling |
| 2.17 Cloud *(production track)* | Object storage, IAM, managed Spark |
| 2.18 Delivery *(production track)* | Images, secrets, CI/CD, environments |
| 2.19 Testing | PySpark unit, property, integration, and smoke tests |
| 2.20 Observability and governance *(production track)* | Metrics, lineage, alerts, PII, erasure |
| 2.21 Performance and cost *(production track)* | Estimation, pushdown, benchmarking, compute cost |

### Tracks

| Track | Milestones | Result |
| --- | --- | --- |
| **Core track** | M0–M10 | A correct, tuned, tested medallion lakehouse running on a local Spark cluster |
| **Production track** | M11–M14 | Orchestrated, deployed through CI/CD, observable, and operable at scale |

**Estimated effort:** Core track 4–5 weeks; Production track 2–3 weeks (at
8–10 hours per week).

**Hardware note:** generate data in **size tiers** (tiny for tests, small
for development, large for performance work). The large tier should be at
least a few times bigger than your machine's RAM (for example 50–200 GB)
so that performance problems are real. Use a small cloud VM or managed Spark
for the large tier if your laptop cannot hold it.

---

## 4. The scenario

You are a data engineer at **ShopLite**. The analytics, marketing, and ML
teams need a lakehouse built from the company's high-volume raw data.

### Sources (landed as files in object storage)

| Source | Format and volume | Behaviour that makes it hard |
| --- | --- | --- |
| **Clickstream events** | Gzipped JSON Lines, hourly files; the largest source (hundreds of millions of events in the large tier) | Nested properties, duplicates from client retries, events arriving up to 5 days late, bot traffic, a few corrupt lines, new fields appearing |
| **Order exports** | Daily Parquet exports from the order system (full changed rows) | The same order appears in several exports as its status changes; cancellations |
| **Product catalogue** | Daily JSON snapshot with nested attributes and category arrays | Price and category changes; archived products; schema drift |
| **Customer profiles** | Daily CSV snapshot | Attribute changes (segment, country), GDPR deletions, messy strings |
| **Inventory snapshots** | Daily Parquet per warehouse | Very large on some days; one warehouse holds most stock (skew) |
| **Logistics partner files** | CSV with header/trailer records, sometimes re-sent | Control totals in trailers; corrected re-sends |

### Consumers and their needs

| Consumer | Gold tables |
| --- | --- |
| Management and analytics | `gold.daily_kpis` (sessions, orders, revenue, conversion rate, average order value by day, country, channel) |
| Marketing and product | `gold.funnel_daily` (view → add-to-cart → checkout → purchase), `gold.product_performance` |
| Operations | `gold.inventory_health` (stock, sell-through, days of cover) |
| BI tool | `gold.orders_obt` (one wide, denormalised table per order line) |
| ML team | `gold.customer_features_daily` (point-in-time-correct features per customer per day) |

### Service-level agreement (write it down in M0)

- **Timeliness:** gold tables for day *D* are published by **06:00** on day
  *D+1*.
- **Correctness:** gold tables are published only after quality gates pass;
  gold revenue reconciles with order exports; incremental results equal a
  full rebuild.
- **Late data:** events up to **5 days** late are reflected automatically in
  silver and gold.
- **Recoverability:** any gold table can be rolled back to its previous
  published version within **15 minutes**.
- **Privacy:** an erasure request removes a customer's personal data from
  all layers, including old table versions, within **7 days**.
- **Cost:** a documented target cost (or compute-hours) per daily run.

---

## 5. Target architecture

```text
 Object storage (MinIO locally / S3 in the cloud)
 ────────────────────────────────────────────────
 landing/<source>/...  (raw files as delivered — never modified)
        │  incremental file discovery (Structured Streaming availableNow + checkpoint)
        ▼
 bronze.*   Delta · append-only · raw columns + _rescued/_corrupt data · provenance metadata
        │  PySpark batch per data interval (with lookback)
        ▼
 silver.*   Delta · typed · validated · deduplicated · conformed · SCD2 dimensions (MERGE)
            quarantine.*  (invalid records with reasons)
        │  incremental via change data feed / affected-date recomputation
        ▼
 gold_staging.*  →  quality gates  →  gold.*  (publish; time travel for rollback)

 Catalog (Hive metastore or open-source Unity Catalog) · readers: Spark, DuckDB, Polars, BI
 Orchestration: Airflow (daily layers, backfills, maintenance) · Spark cluster (standalone / Kubernetes / managed)
 Around everything: run metadata · Spark metrics & history server · lineage · alerts · CI/CD · runbook
```

### Technology choices (defaults)

| Concern | Default (local) | Production option |
| --- | --- | --- |
| Compute | PySpark 4.x, standalone cluster in Docker (or `local[*]` for tests) | Spark on Kubernetes or managed Spark (Module 2.17) |
| Table format | **Delta Lake** (version compatible with your Spark version) | Same; optional Iceberg compatibility (UniForm) |
| Storage | MinIO (S3A) | S3 / GCS / ADLS |
| Catalog | Hive-compatible metastore or open-source Unity Catalog | Managed catalog |
| Orchestration | Airflow 3 | Same or managed Airflow |
| Quality | PySpark checks (and/or Pandera for PySpark) + Delta constraints | + Project 06 platform |
| Lineage | OpenLineage Spark integration + Marquez | Same or catalog |
| Readers | Spark SQL, DuckDB `delta` extension, Polars `scan_delta`, delta-rs | + BI tool |
| CI/CD | GitHub Actions | Same with environments |

Record decisions as **ADRs** in `docs/adr/`: partitioning vs liquid
clustering per table, incremental strategy per layer, WAP mechanism,
retention periods, and cluster sizing.

---

## 6. Repository structure

```text
medallion-lakehouse/
├── README.md
├── pyproject.toml / uv.lock
├── docker-compose.yml             # spark master/workers, minio, metastore/catalog, airflow, history server, marquez
├── conf/                          # spark-defaults per environment, log4j
├── docs/
│   ├── requirements.md
│   ├── architecture.md
│   ├── source-contracts/
│   ├── data-model.md              # every table: layer, grain, keys, partitioning/clustering, retention
│   ├── sizing.md                  # data-size, memory, and runtime estimates
│   ├── adr/
│   └── runbook.md
├── generator/                     # synthetic source data at tiny/small/large tiers (seeded)
├── src/medallion/
│   ├── context.py                 # run context: env, data interval, run id
│   ├── io/                        # readers, Delta writers, table registry
│   ├── bronze/                    # ingestion jobs per source
│   ├── silver/                    # cleaning, dedupe, conformance, sessionisation, SCD2
│   ├── gold/                      # facts, KPIs, funnel, product, inventory, features, OBT
│   ├── quality/                   # checks, quarantine, gates, reconciliation
│   ├── publish/                   # write–audit–publish, rollback
│   ├── maintenance/               # optimize, clustering, vacuum, erasure
│   └── jobs/                      # spark-submit entry points
├── dags/                          # Airflow DAGs
├── tests/
│   ├── unit/  property/  integration/  e2e/  plans/
│   └── fixtures/
└── .github/workflows/
```

---

## 7. Milestones overview

```text
Core track
  M0   Project framing, sizing, and local platform
  M1   Source data at scale and source contracts
  M2   Bronze: incremental, lossless ingestion
  M3   Delta table design and the catalog
  M4   Silver: clean, deduplicated, conformed, historised
  M5   Gold: facts, aggregates, features, and OBT
  M6   Idempotency, late data, and incremental correctness
  M7   Quality gates, write–audit–publish, and rollback
  M8   Performance tuning at scale
  M9   Table maintenance, retention, and erasure
  M10  Testing to production standard

Production track
  M11  Orchestration and backfills
  M12  Packaging, deployment, and security
  M13  CI/CD and environments
  M14  Observability, operations, drills, and cost
  (M15 Optional stretch goals)
```

Commit and tag at the end of every milestone (`m0`, `m1`, …).

---

## 8. Core track

### M0 — Project framing, sizing, and local platform

**Goal:** Know what you are building, how big it is, and have a platform
that can run it.

**Tasks**

1. Write `docs/requirements.md`: consumers, gold tables, SLA (Section 4),
   and non-goals.
2. **Estimate** (Module 2.21) in `docs/sizing.md`: daily and total raw
   volume per source, compressed vs in-memory size, expected bronze/silver/
   gold sizes, shuffle volume of the biggest joins, executor memory, and
   runtime per layer. You will compare these estimates with reality in M8.
3. Draw the architecture and data flow (Section 5).
4. Build `docker-compose.yml` with profiles: Spark master and workers,
   MinIO, a catalog/metastore, Spark history server, Airflow, and Marquez
   (later). Configure Spark with Delta and S3A, UTC session time zone, and
   adaptive query execution enabled.
5. Set up `uv`, Ruff, pytest, `pre-commit` with secret scanning, and a
   `spark` pytest fixture (Module 2.14).
6. Write the first ADRs: Delta and catalog versions, cluster sizing.

**Acceptance criteria**

- [ ] A trivial Delta table can be created, written, and read through the
      catalog on MinIO from the cluster.
- [ ] Sizing estimates exist for every source and layer.
- [ ] The SLA has measurable deadlines, tolerances, and a cost target.

---

### M1 — Source data at scale and source contracts

**Goal:** Realistic, large, reproducible raw data with every defect the
pipeline must handle.

**Tasks**

1. Build a **seeded generator** (Modules 2.2 and 2.19) producing the
   sources in Section 4 at **tiny**, **small**, and **large** tiers, with
   configurable:
   - duplicate events, late events (up to 5 days), bot sessions;
   - corrupt JSON lines, malformed CSV rows, and a new field appearing
     mid-history;
   - order status changes across several daily exports;
   - customer attribute changes and deletions;
   - a heavily skewed product and warehouse distribution;
   - logistics files with trailer control totals and corrected re-sends.
2. Write files to `landing/<source>/<date>/...` exactly as a real system
   would (hourly clickstream files, daily snapshots).
3. Write a **source contract** per source: format, schema, keys, delivery
   schedule, lateness, change and delete behaviour, and quirks.
4. Measure the lateness distribution of clickstream events.

**Acceptance criteria**

- [ ] Each tier regenerates identically from its seed.
- [ ] Every defect type can be switched on and its rate configured.
- [ ] Every source has a contract; the large tier exceeds your RAM several
      times.

---

### M2 — Bronze: incremental, lossless ingestion

**Goal:** Every delivered record lands in bronze exactly once, with
provenance — and nothing is lost, not even corrupt records.

**Tasks**

1. Implement **incremental file discovery** per source: Spark Structured
   Streaming with a file source and `trigger(availableNow=True)` plus a
   checkpoint (processes only new files, then stops — Module 2.16), or a
   file registry (Module 2.9). Record the choice in an ADR.
2. Read with **explicit schemas** (never inference in production) and
   `PERMISSIVE` mode capturing malformed records in a corrupt-record column
   (Module 2.14); keep fields not in the schema in a rescued-data JSON
   column.
3. Add provenance columns: source file path (from the file metadata column),
   file modification time, `_ingested_at`, `_run_id`, and a record hash.
4. Append to `bronze.<source>` Delta tables partitioned or clustered by
   ingestion date.
5. For logistics files, validate trailer **control totals** and reject
   (quarantine) files whose totals do not match; handle corrected re-sends
   by file version.
6. Make re-runs safe: re-running ingestion for already processed files must
   add nothing.

**Acceptance criteria**

- [ ] Bronze row counts equal the number of lines in landed files (including
      corrupt ones, which are flagged, not dropped).
- [ ] Re-running ingestion adds zero rows; a killed run resumes without
      duplicates or gaps.
- [ ] A new field in clickstream appears in the rescued-data column without
      breaking ingestion.
- [ ] Every bronze row is traceable to its exact source file.

---

### M3 — Delta table design and the catalog

**Goal:** Every table is deliberately designed — grain, keys, layout,
constraints, evolution, and retention — and registered in the catalog.

**Tasks**

1. Write `docs/data-model.md` with, for every bronze, silver, quarantine,
   and gold table: layer, grain, keys, columns and types, partitioning **or**
   liquid clustering keys (and why), constraints, retention, and owner.
2. Create schemas/namespaces `bronze`, `silver`, `quarantine`,
   `gold_staging`, and `gold` in the catalog; create tables with DDL (not
   implicit creation) including:
   - `NOT NULL` and `CHECK` constraints on silver and gold (Module 2.15);
   - generated columns where useful (for example a date from a timestamp);
   - table properties for change data feed on silver tables, and
     deletion vectors where appropriate (check reader compatibility).
3. Define the **schema-evolution policy** per layer: bronze tolerant
   (rescued data), silver and gold strict (explicit migrations only).
4. Add a small **table registry** in code so jobs refer to tables by logical
   name, not by path.

**Acceptance criteria**

- [ ] Every table has a documented grain, key, and layout choice.
- [ ] Writing a row that violates a constraint fails.
- [ ] An unexpected column cannot silently enter silver or gold.
- [ ] Tables are readable through the catalog from Spark and by path from
      DuckDB or delta-rs.

---

### M4 — Silver: clean, deduplicated, conformed, historised

**Goal:** Silver tables are the trustworthy, reusable single version of
each entity and event.

**Tasks**

1. Structure silver logic as **pure DataFrame → DataFrame functions**
   chained with `DataFrame.transform` (Modules 2.12, 2.14), with I/O only at
   the edges.
2. **Clickstream** (`silver.events`):
   - parse and flatten nested properties; cast types with ANSI-safe
     functions (`try_cast`); convert all times to UTC;
   - **deduplicate** by `event_id` within a bounded window (keep the first
     occurrence);
   - flag **bots** with documented rules;
   - route invalid events (missing ids, impossible timestamps) to
     `quarantine.events` with reasons.
3. **Sessions** (`silver.sessions`): sessionise events per user with a
   30-minute inactivity rule using window functions; compute session start,
   end, duration, pages, entry channel.
4. **Orders** (`silver.orders`, `silver.order_items`): merge daily exports
   with `MERGE`, keeping the **latest version** per order by the source's
   update timestamp with a version guard; apply cancellations.
5. **Dimensions** (`silver.dim_customer`, `silver.dim_product`): **SCD Type
   2** with hash diffs (Module 2.12) using Delta `MERGE`, one transaction
   per load; customer deletions handled per the privacy policy (M9).
6. **Inventory** and **logistics**: typed, deduplicated, reconciled with
   control totals.
7. Record per run: rows in, rows out, quarantined, deduplicated — and check
   conservation (`in = out + quarantined + removed duplicates`).

**Acceptance criteria**

- [ ] No duplicate `event_id`, order id, or current dimension row in silver.
- [ ] SCD Type 2 integrity holds (one current row per key, no overlaps).
- [ ] Conservation checks pass for every table and run.
- [ ] Sessions match a reference implementation (e.g. DuckDB SQL) on the
      small tier.

---

### M5 — Gold: facts, aggregates, features, and OBT

**Goal:** Business-ready tables with clear grain, correct joins, and fast
queries.

**Tasks**

1. Build `gold.fct_order_items` (grain: one row per order line) joined to
   SCD Type 2 dimensions **point-in-time** (the version valid at order
   time) with broadcast joins for small dimensions.
2. Build `gold.daily_kpis`, `gold.funnel_daily` (step conversion rates,
   excluding bots), `gold.product_performance`, and
   `gold.inventory_health`.
3. Build `gold.orders_obt`: a wide denormalised table for BI, clustered by
   the most common filters.
4. Build `gold.customer_features_daily`: point-in-time-correct features per
   customer per day (e.g. orders in the last 30 days, days since last
   session, average basket) with no future leakage (Modules 2.8, 2.22).
5. Document grain, definitions, and owners for every gold table; define
   metrics consistently (e.g. conversion rate = purchasing sessions ÷ all
   non-bot sessions).

**Acceptance criteria**

- [ ] Row counts of facts equal silver line counts (no fan-out).
- [ ] Gold revenue per day equals the sum of silver order lines and
      reconciles with order exports.
- [ ] Features for a sample of customers and dates are recomputed
      independently and match, proving no leakage.

---

### M6 — Idempotency, late data, and incremental correctness

**Goal:** Daily runs process only what changed, handle late data, and are
safe to repeat — with proof.

**Tasks**

1. Give every job a **run context** with the data interval; no `now()` in
   transformations.
2. **Silver incremental:** process new bronze rows (by ingestion date or
   via change data feed) plus a **lookback window** sized from the measured
   lateness (e.g. 5 days) for event-time tables.
3. **Gold incremental:** determine the set of **affected event dates** from
   silver changes (change data feed), recompute only those dates, and write
   them with a predicate-scoped overwrite (`replaceWhere`) or dynamic
   partition overwrite (Modules 2.12, 2.14, 2.15).
4. Make `MERGE`-based tables idempotent (deduplicated sources, version
   guards) and use Delta **idempotent write** options (application
   transaction ids) where appropriate for retried writes.
5. Build a **full-rebuild job** for every gold table into a shadow table,
   and an automated **comparison** between incremental and full-rebuild
   results.

**Acceptance criteria**

- [ ] Running any day twice leaves every table unchanged (compare table
      hashes or versions' contents).
- [ ] Events arriving 1–5 days late update the right silver and gold dates
      automatically.
- [ ] After 30 simulated days, incremental gold equals a full rebuild
      exactly.
- [ ] Rerunning one day never touches other days' data.

---

### M7 — Quality gates, write–audit–publish, and rollback

**Goal:** Gold consumers never see bad data, and any mistake can be undone
in minutes.

**Tasks**

1. Implement **quality checks** (Module 2.11) per layer: uniqueness,
   not-null, accepted values, ranges, referential integrity, freshness,
   volume anomalies versus same-weekday history, and reconciliation with
   sources (orders revenue, logistics control totals).
2. Implement **quarantine thresholds**: continue with warnings below a
   threshold; fail the run above it.
3. Implement **write–audit–publish** for gold:
   - **write** new results to `gold_staging` tables (or a shallow clone of
     the gold table);
   - **audit** with the checks above;
   - **publish** atomically into `gold` (for example a `MERGE` or
     `replaceWhere` from staging, or swapping in the audited version) and
     record the published Delta version in a `publication_log`.
4. Implement **rollback**: a command that restores a gold table to the
   previous published version with Delta `RESTORE` (time travel — Module
   2.15) and logs the action.
5. Expose freshness to consumers: a `gold.data_status` table with the
   latest published data date and version per gold table.

**Acceptance criteria**

- [ ] An injected defect (duplicated day, missing country, negative prices)
      blocks publication and alerts; the previous gold version remains
      visible.
- [ ] A rollback of any gold table completes within 15 minutes, verified by
      a drill.
- [ ] Every published gold version is recorded with its run id and check
      results.

---

### M8 — Performance tuning at scale

**Goal:** The large tier runs within the SLA and cost target — with every
improvement proven by evidence.

**Tasks**

1. Run the full pipeline on the **large tier** and record a **baseline**:
   wall time per job, shuffle bytes, spill, task-time distribution, peak
   executor memory, files written, and cost or compute-hours (Modules 2.14,
   2.21). Compare with your M0 estimates.
2. Diagnose with the **Spark UI**, plans (`explain("formatted")`), and the
   history server; fix one bottleneck at a time, for example:
   - **skew:** hot products and the dominant warehouse — AQE skew handling,
     salting, or isolating hot keys;
   - **joins:** broadcast small dimensions; avoid unnecessary shuffles;
   - **partitions:** right-size shuffle partitions and output files;
   - **UDFs:** replace Python UDFs with built-ins or pandas UDFs;
   - **pushdown:** make sure date filters reach the scan (partition
     pruning, data skipping, clustering — Module 2.21);
   - **caching:** cache only reused intermediate results.
3. Choose **layouts**: partitioning for very large, date-filtered tables vs
   **liquid clustering** (or Z-ordering) for multi-column filters; target
   file sizes; measure query time for typical gold queries.
4. Write a **tuning report**: before/after metrics, plans, and the reason
   for each change.
5. Add **plan regression tests** (Module 2.14) for key joins (e.g. assert a
   broadcast join) and filters (assert pushed filters).

**Acceptance criteria**

- [ ] The large-tier daily run meets the 06:00 deadline with headroom on
      your cluster (document its size).
- [ ] No task takes more than a set multiple of the median (skew fixed).
- [ ] Gold query times for five typical queries improved measurably after
      layout changes.
- [ ] Every tuning decision is backed by before/after evidence.

---

### M9 — Table maintenance, retention, and erasure

**Goal:** Tables stay fast and affordable indefinitely, and personal data
can be removed everywhere.

**Tasks**

1. Write a **maintenance policy** per table (Module 2.15): `OPTIMIZE`
   (compaction) frequency, clustering, `VACUUM` retention, log retention,
   and — for tables using deletion vectors — how deleted rows are
   physically purged.
2. Build a **table health report**: number and size distribution of files,
   versions, storage per table, and time since last optimisation.
3. Justify retention: time-travel needs for rollback (M7) and audits vs
   storage cost vs erasure deadlines.
4. Implement an **erasure pipeline** (Module 2.20) for a customer:
   - identify all rows across bronze, silver, quarantine, and gold (using
     keys and lineage);
   - delete or pseudonymise them with Delta `DELETE`/`MERGE`;
   - purge deletion vectors and run `VACUUM` after the retention window so
     old files are removed;
   - verify by scanning all remaining data files and table versions;
   - record a deletion certificate.
5. Keep raw **landing** files under lifecycle rules (Module 2.17) consistent
   with the erasure policy (or restrict and document why they are kept).

**Acceptance criteria**

- [ ] After weeks of simulated runs, file counts and query times remain
      within targets because of maintenance.
- [ ] `VACUUM` never breaks rollback within the agreed window.
- [ ] After an erasure request and the maintenance cycle, no file or
      readable version contains the customer's personal data.

---

### M10 — Testing to production standard

**Goal:** Fast, reliable tests that catch the bugs that matter in a
medallion pipeline.

**Tasks**

1. **Unit tests** for every pure transformation with tiny DataFrames and
   `assertDataFrameEqual` (Module 2.14): parsing, dedupe, bot rules,
   sessionisation (including sessions crossing midnight and time zones),
   SCD Type 2, point-in-time joins, KPI definitions.
2. **Property tests** (Module 2.19): deduplication is idempotent and
   order-independent; sessionisation over chunked input equals whole
   input; incremental gold equals a full rebuild for random late-arrival
   patterns.
3. **Integration tests** against local Spark with MinIO and the catalog:
   bronze ingestion with corrupt lines and new fields, Delta `MERGE`s,
   `replaceWhere` overwrites, constraints, WAP, and `RESTORE`.
4. **Plan tests** (M8) and **contract tests** on gold schemas.
5. **End-to-end smoke test** on the tiny tier: two days of data through all
   layers with late events and a defect, asserting published gold,
   quarantine contents, and publication logs.

**Acceptance criteria**

- [ ] Re-introducing any of these bugs fails a test: dedupe by the wrong
      key, sessions in local time, future leakage in features, fan-out in
      the fact, whole-table overwrite on rerun, publishing before audit.
- [ ] The unit suite runs in a few minutes with a shared Spark session.
- [ ] No flaky tests across 20 runs.

**At the end of M10 you have completed the Core track.** Tag the repository
`core-complete` and write a retrospective.

---

## 9. Production track

### M11 — Orchestration and backfills

**Goal:** The lakehouse runs itself daily, recovers from routine failures,
and backfills safely.

**Tasks**

1. Write Airflow DAGs (Module 2.13):
   - `bronze_ingest` — per source, triggered on schedule (and by file
     arrival where useful), emitting bronze **assets**;
   - `silver_build` — scheduled on bronze assets, one task per silver table
     group, passing the data interval;
   - `gold_publish` — scheduled on silver assets: write → audit → publish,
     with branching on gate results and alerts;
   - `lakehouse_maintenance` — nightly/weekly `OPTIMIZE`, clustering,
     `VACUUM`, health report, and erasure processing.
2. Submit Spark jobs with the appropriate operator (spark-submit to your
   cluster, Kubernetes, or a managed service), passing the run context as
   arguments.
3. Use **pools** so backfills and maintenance cannot starve the daily run;
   set retries, timeouts, and non-retryable failures for contract
   violations.
4. Implement **backfills**: rerun a date range of silver and gold with
   bounded parallelism; a logic-change backfill into shadow tables with a
   data diff before publishing.

**Acceptance criteria**

- [ ] A normal day runs end to end without manual steps and meets the
      deadline.
- [ ] A 60-day backfill completes without delaying the daily run.
- [ ] Maintenance never conflicts destructively with daily writes.

---

### M12 — Packaging, deployment, and security

**Goal:** Reproducible, secure deployments of the Spark jobs and their
dependencies.

**Tasks**

1. Package the `medallion` Python package and build a **Spark job image**
   (Module 2.18) with pinned PySpark, Delta, S3A, and Python dependencies;
   scan it.
2. Keep Spark configuration per environment (`dev`, `staging`, `prod`) in
   code; size executors from M8 evidence.
3. Use **least-privilege** identities per layer (Module 2.17): ingestion
   can write only bronze; silver jobs read bronze and write silver; gold
   jobs read silver and write gold; analysts read gold only.
4. Deliver credentials through a secrets manager or workload identity —
   never in `spark-defaults.conf` or code.
5. Optionally run on Kubernetes (Spark on Kubernetes or an operator) or a
   managed Spark service (Module 2.17).

**Acceptance criteria**

- [ ] A job denied access outside its layer fails with a permission error.
- [ ] No credential appears in images, configuration files, or logs.
- [ ] The same image runs in every environment with configuration changes
      only.

---

### M13 — CI/CD and environments

**Goal:** Every change is tested and deployed safely, with realistic
validation before production.

**Tasks**

1. **CI on pull requests:** lint, types, unit, property, plan, and
   integration tests; image build and scan; DAG tests.
2. **Data validation for changes:** run changed jobs on the small tier in
   an ephemeral environment (or against **shallow clones** of production
   tables — Module 2.18) and produce a data diff of affected gold tables.
3. **CD on merge:** build the image once, deploy to `dev`, run the
   end-to-end smoke test, promote the same image to `staging` (large-tier
   run against the SLA) and then `prod` with approval.
4. Document and rehearse rollback of a bad release: redeploy the previous
   image and `RESTORE` affected gold tables.

**Acceptance criteria**

- [ ] A change that alters gold numbers shows a data diff in the pull
      request before merge.
- [ ] Production runs a known image version traceable to a commit.
- [ ] A bad release is rolled back — code and data — within the documented
      time.

---

### M14 — Observability, operations, drills, and cost

**Goal:** You can see, explain, and control the platform's health, speed,
and cost — and someone else can run it.

**Tasks**

1. **Observability** (Module 2.20): run metadata per job (rows per layer,
   quarantine rates, durations, Delta versions written), Spark event logs
   and history server, OpenLineage lineage from Spark, dashboards for
   freshness, runtime trends, table health, and quality results.
2. **Alerts** with owners and runbooks: gold not published by 06:00, gate
   failure, quarantine rate above threshold, runtime regression, table
   health degradation, erasure deadline at risk.
3. **Runbook** (`docs/runbook.md`): daily operations, rerun a day,
   backfill, rollback, handle skewed or oversized days, recover from failed
   maintenance, process erasure requests, add a new source.
4. **Drills:** executor out-of-memory on an unusually large day; a surge of
   corrupt files; a skewed day (a viral product); concurrent writers
   conflicting on a table; a bad deploy followed by rollback; storage
   unavailability mid-write. Every drill ends with correct gold tables.
5. **Cost:** cost or compute-hours per daily run and per table; optimise
   (right-sized executors, spot/preemptible workers for retryable jobs,
   fewer full rebuilds, smarter maintenance schedules) and record savings
   (Module 2.21).

**Acceptance criteria**

- [ ] Every drill is detected by an alert and resolved with the runbook.
- [ ] Cost per run is known and within the target.
- [ ] Another person can run a backfill and a rollback using only the
      documentation.

---

### M15 — Optional stretch goals

- **Interoperability:** enable Delta UniForm (or write an Iceberg copy) and
  read gold tables from an Iceberg-compatible engine; compare with Project
  02.
- **Governance:** use open-source Unity Catalog (or your catalog) for
  table-level permissions and column masking on personal data (Module
  2.20).
- **Managed Spark:** run the large tier on a managed platform and compare
  runtime and cost with your local cluster (Module 2.17).
- **Single-node comparison:** implement one gold table with Polars or DuckDB
  over the Delta tables and compare with Spark (Module 2.4).
- **Streaming bronze:** switch clickstream ingestion from `availableNow`
  batches to a continuous stream and discuss the cost/latency trade-off.
- **Semantic layer or features serving:** expose gold metrics through a
  semantic layer, or publish customer features to a feature store (Module
  2.22).

---

## 10. Definition of done

**Correctness**

- [ ] Bronze is lossless and traceable; silver is deduplicated and
      conformed; gold reconciles with sources.
- [ ] Incremental results equal full rebuilds; late data is applied
      automatically.
- [ ] Features are point-in-time correct.

**Reliability and recoverability**

- [ ] Every job is idempotent and interval-scoped; reruns and backfills are
      safe.
- [ ] Consumers never see gold that failed quality gates; rollback is
      proven within 15 minutes.

**Performance, maintenance, and cost**

- [ ] The large tier meets the SLA with evidence-backed tuning.
- [ ] Maintenance keeps file counts, query times, and storage within
      targets.
- [ ] Cost per run is measured and within target.

**Governance and security**

- [ ] Least-privilege access per layer; no secrets in code or config.
- [ ] Erasure proven across layers and table versions.

**Engineering and documentation**

- [ ] Layered tests including plan and end-to-end tests; CI/CD with data
      diffs and promotion.
- [ ] Orchestration with assets, gates, backfills, and maintenance.
- [ ] Requirements, sizing, data model, ADRs, tuning report, runbook, and
      retrospective complete.

---

## 11. Evaluation rubric (self or peer review)

Score each area from 0 to 3. A production-grade project scores **at least 2
in every area** and **3 in Correctness, Recoverability, and Performance**.

| Area | What a "3" looks like |
| --- | --- |
| Correctness | Lossless bronze, clean silver, reconciled gold, incremental = full rebuild |
| Recoverability | WAP with audited publishes; rollback drills within target |
| Performance | SLA met on the large tier; skew, joins, partitions, and layout tuned with evidence |
| Delta mastery | Constraints, `MERGE`, CDF, `replaceWhere`, time travel, clustering, maintenance used deliberately |
| Data modelling | Clear grain, SCD Type 2, point-in-time joins, no fan-out, leak-free features |
| Quality | Checks, thresholds, quarantine, conservation, and reconciliation per layer |
| Maintenance and privacy | Health stays stable over time; erasure provable across versions |
| Testing | Unit, property, integration, plan, and end-to-end tests without flakiness |
| Delivery and operations | Orchestrated, CI/CD with data diffs, alerts, runbook, drills |
| Cost awareness | Measured cost per run, optimisations with recorded savings |

---

## 12. Common pitfalls to avoid

- Inferring schemas from raw files in production.
- Dropping corrupt records instead of capturing and quarantining them.
- Deduplicating on all columns instead of the business key.
- Sessionising in local time or across unsorted data.
- Joining facts to the **current** dimension row instead of the version
  valid at event time.
- Static `overwrite` of whole tables on a single-day rerun.
- Incremental gold built only from "new" rows, ignoring updates and late
  events.
- Python UDFs in hot paths; broadcasting large tables; ignoring skew.
- `coalesce(1)` to "get one file", or thousands of tiny files per run.
- `VACUUM` with a retention shorter than your rollback window.
- Believing a `DELETE` alone completes an erasure request.
- Tuning by guesswork without the Spark UI and plans.

---

## 13. Suggested timeline

| Week | Milestones |
| --- | --- |
| 1 | M0 framing, sizing, platform · M1 source data and contracts |
| 2 | M2 bronze ingestion · M3 Delta table design |
| 3 | M4 silver |
| 4 | M5 gold · M6 idempotency and incremental correctness |
| 5 | M7 quality gates and WAP · M8 performance tuning · M9 maintenance and erasure · M10 testing → **Core track complete** |
| 6 | M11 orchestration and backfills · M12 packaging and security |
| 7 | M13 CI/CD · M14 observability, drills, and cost → **Production track complete** |
| 8 (optional) | M15 stretch goals |

---

## 14. What to show in a portfolio or interview

Be ready to explain:

1. What belongs in bronze, silver, and gold — and why bronze is lossless.
2. How incremental file discovery and provenance make ingestion safe to
   rerun.
3. How you deduplicated events, sessionised clickstream, and maintained
   SCD Type 2 dimensions with `MERGE`.
4. How gold is updated incrementally for late data, and how you proved it
   equals a full rebuild.
5. How write–audit–publish and `RESTORE` protect consumers.
6. Your biggest performance win, with Spark UI and plan evidence.
7. Your partitioning vs clustering decisions and maintenance policy.
8. How an erasure request is completed across layers and old versions.
9. The cost per daily run and how you reduced it.

A README with the architecture diagram, the table catalogue, a short demo
(a day's run, a blocked publication after an injected defect, a rollback, a
backfill), the tuning report, and the runbook shows you can operate a
lakehouse at scale — not just write Spark code.
