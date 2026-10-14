# Project Roadmap — CDC Replication from PostgreSQL to the Lakehouse

This is the end-to-end roadmap for **Stage 2 Project 02: CDC Replication
from PostgreSQL to the Lakehouse**. It takes you from an empty repository
to a **production-grade** change-data-capture (CDC) pipeline that streams
every insert, update, and delete from an operational PostgreSQL database
through Kafka into open lakehouse tables — continuously, correctly, and
without harming the source database.

It is written as a sequence of **milestones**. Each milestone has a goal,
the tasks to complete, the deliverables to produce, and **acceptance
criteria** you must meet before moving on. The acceptance criteria are what
make this production grade rather than "a demo that replicated a few rows".

---

## 1. Why this project matters

Almost every company's most important data lives in operational databases:
orders, customers, payments, inventory. Analytics, ML, and other services
need that data — but querying the production database directly is slow,
risky, and misses history. Nightly full dumps are expensive and stale;
timestamp-based incremental extraction misses deletes and intermediate
changes (Module 2.9).

**Log-based CDC** solves this: it reads the database's own transaction log
and publishes every change as an event. Done well, it gives the business a
near-real-time, complete, historical copy of its operational data in the
lakehouse. Done badly, it fills the production database's disk with
retained WAL, silently drops deletes, breaks on the first schema change,
and produces a lake copy that nobody can prove is correct.

This project makes you solve all of those problems end to end.

---

## 2. Project goal and scope

### Goal

Build `cdc_lakehouse`, a continuously running system that:

1. Captures every change from selected PostgreSQL tables with **Debezium**
   via logical decoding, starting with a consistent **initial snapshot**.
2. Publishes change events to **Kafka** with schemas managed in a **schema
   registry**.
3. Appends every raw change event to a **bronze change-log table** in the
   lakehouse (Apache Iceberg by default).
4. Maintains **silver mirror tables** that equal the source tables' current
   state — including deletes — using ordered, idempotent `MERGE`s.
5. Maintains **history (SCD Type 2) tables** built from the change log.
6. Handles **schema evolution**, re-snapshots, and new tables safely.
7. **Reconciles** the lakehouse against the source and measures end-to-end
   latency.
8. **Maintains** the tables (compaction, snapshot expiry, orphan cleanup)
   and honours **erasure** requests across every copy.
9. Is monitored, alerting, deployed through CI/CD, and operable by someone
   else.

### In scope

- The source database and a realistic workload generator, Debezium on Kafka
  Connect, Kafka topics and schemas, Spark Structured Streaming jobs,
  Iceberg tables with a catalog, reconciliation, maintenance, privacy
  handling, testing, deployment, monitoring, and operations.

### Out of scope (covered by other Stage 2 projects)

- API ingestion → **Project 01**.
- dbt marts and batch ELT orchestration → **Project 03**.
- Gold-layer batch analytics with PySpark and Delta → **Project 04**.
- Real-time windowed analytics and alerts → **Project 05**.
- The full data-quality and observability platform → **Project 06**.

---

## 3. Prerequisites and when to do this project

**Recommended timing:** after completing **Modules 2.1–2.16**. The
production-hardening milestones (M12–M15) use Modules 2.13 and 2.17–2.20.
If you have not studied those yet, complete the **Core track** now and
return for the **Production track** later.

| Module | What this project uses from it |
| --- | --- |
| 2.1 Foundations | Medallion layers, latency and freshness SLAs |
| 2.5 Data formats | Avro, Parquet, partitioning, small files |
| 2.6 SQL | Transactions, `MERGE`, SCD Type 2, window-function dedupe, `EXCEPT` comparisons |
| 2.7 Python DB connectivity | psycopg, workload generation, reconciliation queries |
| 2.8 Data modelling | Grain, keys, SCD types, event data |
| 2.9 Ingestion patterns | **CDC concepts**, logical decoding, replication slots, snapshot handoff |
| 2.10 Concurrency | Workload generator, bounded parallel reconciliation |
| 2.11 Validation and quality | Contracts, schema compatibility, dead-letter handling, reconciliation |
| 2.12 Pipeline design | Idempotency, version guards, hashing, state |
| 2.14 PySpark | DataFrames, partitioning, Spark UI |
| 2.15 Lakehouse table formats | Iceberg (or Delta) internals, `MERGE`, time travel, maintenance, catalogs, physical deletion |
| 2.16 Streaming | Kafka, consumers, delivery semantics, schema registry, Structured Streaming, **Debezium**, lag |
| 2.13 Orchestration *(production track)* | Scheduled maintenance and reconciliation |
| 2.17 Cloud *(production track)* | Object storage, IAM, managed Kafka and catalogs |
| 2.18 Delivery *(production track)* | Images, Compose/Kubernetes, CI/CD, secrets |
| 2.19 Testing | Integration, property, and end-to-end tests |
| 2.20 Observability and governance *(production track)* | Metrics, alerts, runbooks, PII, erasure |

### Tracks

| Track | Milestones | Result |
| --- | --- | --- |
| **Core track** | M0–M11 | A correct, tested CDC pipeline from PostgreSQL to Iceberg running locally |
| **Production track** | M12–M15 | Deployed, monitored, alerting, operable, and resilient to infrastructure failures |

**Estimated effort:** Core track 4–5 weeks; Production track 2–3 weeks (at
8–10 hours per week).

**Hardware note:** the full local stack (PostgreSQL, Kafka, Kafka Connect,
schema registry, Spark, MinIO, catalog, monitoring) needs roughly 12–16 GB
of RAM. Use Compose profiles to run only what each milestone needs, or run
the heavier pieces on a small cloud VM.

---

## 4. The scenario

You are a data engineer at **ShopLite**. Its order-management service runs
on PostgreSQL. Analytics, finance, and the ML team need a complete,
near-real-time, historical copy of these tables in the lakehouse:

| Table | Rows (simulated) | Behaviour that makes it hard |
| --- | --- | --- |
| `customers` | ~1 M | Frequent profile updates; GDPR deletions |
| `addresses` | ~1.5 M | Many-to-one with customers; deletes when customers remove addresses |
| `products` | ~50 K | Price updates; archived products; occasional schema changes |
| `orders` | ~20 M | High insert rate; status changes for days; cancellations |
| `order_items` | ~60 M | Inserted with orders in the same transaction; composite key |
| `payments` | ~20 M | Updates arrive seconds after orders; refunds |
| `inventory` | ~50 K | Very hot rows updated constantly (many changes per key) |
| `outbox_events` *(stretch)* | append-only | Domain events published via the outbox pattern |

### Service-level agreement (write it down in M0)

- **Latency:** a committed source change is visible in silver mirror tables
  within **5 minutes at p95**.
- **Completeness and correctness:** at every reconciliation point, silver
  tables equal the source tables at the same log position (row counts,
  keys, and checksums), including deletes.
- **History:** every change to `customers`, `products`, and `orders` is
  available in history tables with its commit time.
- **Source safety:** retained WAL for the CDC replication slot never
  exceeds an agreed threshold (for example 10 GB); CDC never takes locks
  that block the application.
- **Privacy:** an erasure request removes a customer's personal data from
  every lakehouse copy (including history and old snapshots) within 7 days.
- **Availability:** failures recover automatically where possible; sustained
  lag or a stopped connector pages the on-call engineer.

---

## 5. Target architecture

```text
┌──────────────────────────────┐
│ PostgreSQL (order service)   │  wal_level=logical · publication · replica identity
│  tables + workload generator │  CDC role (least privilege) · heartbeat table
└──────────────┬───────────────┘
               │ logical decoding (pgoutput) via replication slot
               ▼
┌──────────────────────────────┐      ┌───────────────────────┐
│ Kafka Connect + Debezium     │─────►│ Schema registry        │
│  snapshot · streaming ·      │      │ (Avro, compatibility)  │
│  heartbeats · signals        │      └───────────────────────┘
└──────────────┬───────────────┘
               │ one topic per table (keys = primary keys)
               ▼
┌──────────────────────────────┐
│ Kafka (KRaft)                │  retention sized for replay · DLQ topics
└──────────────┬───────────────┘
               │ Spark Structured Streaming (checkpoints)
               ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Lakehouse on object storage (MinIO / S3) · Iceberg REST catalog       │
│                                                                      │
│  bronze.cdc_<table>      append-only change log (+ Kafka offsets)    │
│  silver.<table>          current-state mirror (MERGE: upsert/delete) │
│  silver.<table>_history  SCD Type 2 history from the change log      │
└──────────────────────────────────────────────────────────────────────┘
               │
   reconciliation · table maintenance · erasure · metrics · alerts
               │
     orchestrator (Airflow) for scheduled jobs · readers: Spark, DuckDB, PyIceberg
```

### Technology choices (defaults)

| Concern | Default (local) | Production option |
| --- | --- | --- |
| Source | PostgreSQL 16+ in Docker | Managed PostgreSQL (with logical replication enabled) |
| CDC | Debezium PostgreSQL connector on Kafka Connect, `pgoutput` plugin | Same, or a managed CDC connector |
| Broker | Apache Kafka 4.x (KRaft), 3 brokers | Managed Kafka |
| Schemas | Avro with a schema registry | Same |
| Processing | Spark Structured Streaming (PySpark) | Managed Spark (Module 2.17) |
| Table format | Apache Iceberg | Delta Lake (stretch goal) |
| Catalog | Iceberg REST catalog (e.g. Apache Polaris) | Managed catalog |
| Storage | MinIO | S3 / GCS / ADLS |
| Scheduling | Airflow (maintenance, reconciliation) | Same |
| Readers | DuckDB, PyIceberg, Spark | + warehouse or query engine |
| Monitoring | Prometheus, Grafana, Alertmanager | Same or managed |
| Delivery | Docker Compose; optionally kind/k3d | Kubernetes, Terraform, GitHub Actions |

Record every decision and its alternatives as an **ADR** in `docs/adr/`
(for example: Iceberg vs Delta, Avro vs Protobuf, one topic per table,
bronze design, how deletes are represented in silver).

---

## 6. Repository structure

```text
cdc-postgres-to-lakehouse/
├── README.md
├── pyproject.toml / uv.lock
├── docker-compose.yml               # profiles: source, kafka, connect, spark, lake, monitoring, airflow
├── .env.example
├── docs/
│   ├── requirements.md              # scope, consumers, SLA
│   ├── architecture.md
│   ├── source-contract.md           # tables, keys, change semantics, schema-change policy
│   ├── data-model.md                # bronze / silver / history tables, grain, keys
│   ├── adr/
│   └── runbook.md
├── source/
│   ├── migrations/                  # source schema (Alembic or SQL) and evolutions
│   ├── cdc_setup.sql                # publication, CDC role, heartbeat table, replica identity
│   └── workload/                    # workload generator (inserts, updates, deletes, bursts)
├── connect/
│   ├── connectors/                  # Debezium connector configs as code (JSON/YAML per env)
│   └── deploy.py                    # idempotent create/update/validate via the Connect REST API
├── src/cdc_lakehouse/
│   ├── config.py
│   ├── streaming/                   # bronze and silver Structured Streaming jobs
│   ├── merge/                       # dedupe, ordering, MERGE builders, SCD2 builder
│   ├── schema/                      # schema-evolution handling
│   ├── reconcile/                   # source vs lake comparisons, latency probes
│   ├── maintenance/                 # compaction, expiry, orphan cleanup
│   ├── privacy/                     # erasure pipeline
│   ├── observability/
│   └── cli.py
├── dags/                            # Airflow DAGs for maintenance, reconciliation, erasure
├── tests/
│   ├── unit/  property/  integration/  e2e/
│   └── fixtures/                    # recorded Debezium events
└── .github/workflows/
```

---

## 7. Milestones overview

```text
Core track
  M0   Project framing and local platform
  M1   Source database, CDC configuration, and workload generator
  M2   Debezium on Kafka Connect: snapshot and streaming
  M3   Event contracts and the schema registry
  M4   Bronze: an append-only change log in Iceberg
  M5   Silver: a correct current-state mirror with MERGE
  M6   History: SCD Type 2 from the change log
  M7   Snapshots, re-snapshots, new tables, and backfills
  M8   Schema evolution end to end
  M9   Reconciliation and latency measurement
  M10  Table maintenance and erasure
  M11  Testing to production standard

Production track
  M12  Packaging, configuration as code, and secrets
  M13  CI/CD and safe upgrades of streaming jobs
  M14  Observability and alerting
  M15  Operations: runbook, chaos drills, performance, cost, hand-over
  (M16 Optional stretch goals)
```

Commit and tag at the end of every milestone (`m0`, `m1`, …).

---

## 8. Core track

### M0 — Project framing and local platform

**Goal:** Know exactly what you are building and how success is measured,
and have a reproducible local platform.

**Tasks**

1. Write `docs/requirements.md`: consumers (analytics, finance, ML), the
   tables they need, the SLA from Section 4, and non-goals.
2. Draw the architecture in `docs/architecture.md`, including every
   component, topic, and table, and where state lives (replication slot,
   Connect offsets, Spark checkpoints, table snapshots).
3. Set up the repository: `uv`, Ruff, type checker, pytest, `pre-commit`
   with secret scanning.
4. Write `docker-compose.yml` with **profiles**, health checks, named
   volumes, and idempotent set-up services (bucket, catalog namespaces,
   Kafka topics where not auto-created).
5. Write the first ADRs: table format, catalog, serialisation format, and
   processing engine.

**Acceptance criteria**

- [ ] The stack starts healthy from a clean clone, profile by profile.
- [ ] The SLA has measurable numbers for latency, correctness, source
      safety, and privacy.
- [ ] The architecture document names every place where pipeline state is
      stored.

---

### M1 — Source database, CDC configuration, and workload generator

**Goal:** A realistic source database that is correctly configured for
logical replication, and a workload that exercises every hard case.

**Tasks**

1. Create the source schema (Section 4) with primary keys on every table,
   realistic types (`NUMERIC` money, `TIMESTAMPTZ`, `JSONB` metadata,
   enums), foreign keys, and indexes.
2. Configure logical replication: `wal_level = logical`, sensible
   `max_replication_slots` and `max_wal_senders`, and a
   `max_slot_wal_keep_size` safety limit (and understand what happens when
   it is reached).
3. Create a **publication** for the replicated tables and a dedicated
   **CDC role** with only the privileges logical replication and
   snapshots need (least privilege — Module 2.17).
4. Decide **replica identity** per table (default primary key vs `FULL`)
   and document the effect on `before` images for updates and deletes.
5. Create a **heartbeat table** that Debezium can update so that quiet
   periods still advance the slot (M2).
6. Build a **workload generator** (Python, psycopg, asyncio — Modules 2.7,
   2.10) with configurable rates and scenarios:
   - steady inserts, updates, and deletes across all tables;
   - multi-table transactions (an order with its items and payment);
   - hot keys (inventory rows updated many times per second);
   - bursts (10× traffic for 5 minutes);
   - long-running transactions;
   - GDPR-style customer deletions cascading to addresses;
   - bulk updates (a price change on 20% of products).
7. Write `docs/source-contract.md`: tables, keys, change semantics, which
   columns contain personal data, and the schema-change policy agreed with
   the "application team".

**Acceptance criteria**

- [ ] Every replicated table has a primary key and a documented replica
      identity.
- [ ] The CDC role cannot write to application tables.
- [ ] The workload generator is reproducible from a seed and can run each
      scenario on demand.
- [ ] You can explain what `max_slot_wal_keep_size` protects against and
      what it costs.

---

### M2 — Debezium on Kafka Connect: snapshot and streaming

**Goal:** Every committed change in the source reliably becomes an event in
Kafka, starting from a consistent snapshot.

**Tasks**

1. Run Kafka (KRaft, 3 brokers), the schema registry, and Kafka Connect
   with the Debezium PostgreSQL connector.
2. Write the connector configuration **as code** (`connect/connectors/`)
   and a `deploy.py` that validates and creates/updates it idempotently
   through the Connect REST API.
3. Configure the connector deliberately and document every setting:
   `pgoutput` plugin, publication and slot names, table include list,
   **snapshot mode** for the initial load, **heartbeat** interval and
   heartbeat table, **tombstones on delete**, decimal and time precision
   handling, topic naming, key and value converters (Avro + registry).
4. Design topics: one per table, partitions sized for throughput, keys =
   primary keys (so all changes of a row stay ordered in one partition),
   replication factor 3, and **retention long enough to rebuild silver**
   from Kafka after an outage (document the number).
5. Run the initial snapshot, then start the workload; inspect raw events
   and map every field of the **change event envelope** (`before`,
   `after`, `op`, `source.lsn`, `source.txId`, `ts_ms`) to what you learned
   in Modules 2.9 and 2.16.
6. Restart the connector, stop it for 30 minutes under load, and restart
   again; observe offsets and slot behaviour.

**Deliverables:** running CDC, connector config as code, topic design ADR.

**Acceptance criteria**

- [ ] After the snapshot, the number of snapshot (`op = r`) events per
      table equals the source row count.
- [ ] Inserts, updates, and deletes (with tombstones) all appear with
      correct keys and ordering per key.
- [ ] Stopping and restarting the connector loses no changes.
- [ ] During a quiet period, heartbeats keep the replication slot
      advancing (WAL retention stays low).

---

### M3 — Event contracts and the schema registry

**Goal:** Change events are typed, versioned contracts; incompatible
changes are caught before they break the pipeline.

**Tasks**

1. Inspect the Avro schemas Debezium registers for each table's key and
   value; document how PostgreSQL types map to Avro and then to Iceberg
   (decimals, timestamps with time zone, JSONB, enums, arrays).
2. Set **compatibility modes** per subject (Module 2.11) and document why.
3. Define the **schema-change policy** with the application team (in the
   source contract): which changes are allowed freely (add nullable
   column), which need notice (type widening), and which require a
   migration plan (rename, drop, type change).
4. Configure a **dead-letter** path for records the downstream jobs cannot
   deserialise or process (Module 2.16), with alerting.
5. Add a CI check (used in M13) that fails when a source migration would
   produce an incompatible schema.

**Acceptance criteria**

- [ ] Every table's type mapping from PostgreSQL to Iceberg is documented
      and tested.
- [ ] An incompatible schema change is rejected or routed to the
      dead-letter path with a clear alert — never silently corrupts data.

---

### M4 — Bronze: an append-only change log in Iceberg

**Goal:** Every change event is stored durably and unchanged in the
lakehouse, so silver and history tables can always be rebuilt without
re-reading the source.

**Tasks**

1. Design `bronze.cdc_<table>` (one per table) or a unified change-log
   table (document the choice): columns for the flattened `before` and
   `after` images (or structs), `op`, source metadata (`lsn`, `tx_id`,
   commit timestamp), Kafka metadata (`topic`, `partition`, `offset`,
   timestamp), and ingestion time.
2. Partition by ingestion or commit date (hidden partitioning —
   Module 2.15); choose a sort order that helps reprocessing.
3. Write a **Spark Structured Streaming** job reading all CDC topics with
   Avro deserialisation via the schema registry, writing to bronze with a
   **checkpoint location** per query.
4. Make bronze writes **idempotent**: after a restart, no event is written
   twice (checkpoint-based exactly-once with a deduplication guard on
   `(topic, partition, offset)`, or `foreachBatch` with a batch-id guard —
   document the approach).
5. Choose a **trigger** interval that meets the latency SLA without
   creating tiny files; plan compaction for M10.
6. Build a `rebuild-silver --from-bronze` command skeleton (used in M5–M6).

**Acceptance criteria**

- [ ] Killing the bronze job at random 20 times produces no missing and no
      duplicate `(topic, partition, offset)` rows.
- [ ] Every event in Kafka within retention is present in bronze.
- [ ] Bronze is readable from DuckDB or PyIceberg as well as Spark.

---

### M5 — Silver: a correct current-state mirror with MERGE

**Goal:** For every replicated table, `silver.<table>` equals the source
table's current state — including updates and deletes — at all times after
processing catches up.

**Tasks**

1. Write the silver job with `foreachBatch` (Module 2.16) reading either
   from Kafka directly or incrementally from bronze (document the choice;
   reading from bronze makes rebuilds and replays simpler).
2. Within each micro-batch, **deduplicate per primary key**, keeping the
   **latest change by log position** (`lsn`, then event order within the
   transaction) — never by processing time.
3. **MERGE** into `silver.<table>`:
   - `op = c/r/u` → insert or update with the `after` image;
   - `op = d` → delete (or soft-delete with `_deleted_at` — decide and
     document per consumer need);
   - apply a **version guard**: never overwrite a row with a change whose
     log position is older than the stored `_source_lsn`.
4. Store metadata columns: `_source_lsn`, `_source_commit_ts`,
   `_op`, `_ingested_at`, `_batch_id`.
5. Make the `MERGE` **idempotent** so replaying a batch or a whole period
   produces identical tables.
6. Handle **composite keys** (`order_items`) and very hot keys
   (`inventory`) efficiently (dedupe before merge; restrict merge targets
   with partition/cluster predicates — Module 2.15).
7. Implement `rebuild-silver` from bronze for a table, into a **shadow
   table**, with an atomic swap after validation.

**Acceptance criteria**

- [ ] After the workload stops and processing catches up, every silver
      table equals its source table exactly (verified in M9).
- [ ] Replaying the last 24 hours of bronze into silver changes nothing.
- [ ] Out-of-order or duplicated events never produce a stale row.
- [ ] Deletes in the source are reflected in silver.
- [ ] A full rebuild from bronze into a shadow table equals the live silver
      table.

---

### M6 — History: SCD Type 2 from the change log

**Goal:** Analysts and ML can ask "what did this customer, product, or
order look like at time T?".

**Tasks**

1. Build `silver.<table>_history` for `customers`, `products`, and
   `orders`: one row per version with `valid_from` (commit timestamp),
   `valid_to`, `is_current`, `_source_lsn`, and a `_hash_diff` of tracked
   columns (Module 2.12).
2. Create a new version only when tracked attributes change (ignore
   changes to technical columns you have decided not to track).
3. Close the current version on delete (and mark it deleted).
4. Handle several changes to the same key **within one micro-batch** in
   log order, producing all intermediate versions.
5. Handle late or replayed events idempotently (the same change never
   produces two versions).
6. Write assertion queries: exactly one current row per key; no overlapping
   or gapped validity ranges; history ordered by log position.

**Acceptance criteria**

- [ ] For a sample of keys, the full sequence of versions matches the
      sequence of committed changes in the source (verified by the workload
      generator's own log).
- [ ] All SCD Type 2 integrity assertions pass after chaos tests.
- [ ] A point-in-time query reproduces the source state at a chosen past
      time for a sample of rows.

---

### M7 — Snapshots, re-snapshots, new tables, and backfills

**Goal:** You can add tables, recover from lost state, and re-baseline
without downtime or data loss.

**Tasks**

1. Document the **snapshot-to-streaming handoff**: how Debezium guarantees
   no gap and no double-apply between the initial snapshot and streaming,
   and how your silver merge tolerates overlap (version guard).
2. **Add a new table** (for example `shipments`) to an already running
   pipeline using Debezium **incremental snapshots** (signals) without
   re-snapshotting everything.
3. Simulate **lost pipeline state** (deleted Spark checkpoint or lost
   Connect offsets) and write the recovery procedure: re-snapshot a table
   (or rebuild silver from bronze), then reconcile.
4. Simulate a **dropped or invalidated replication slot** (for example after
   exceeding `max_slot_wal_keep_size`) and recover with a re-snapshot,
   documenting the data risk and the reconciliation afterwards.
5. Write runbook entries for each case.

**Acceptance criteria**

- [ ] A new table is added while the pipeline runs, and its silver table
      reconciles with the source.
- [ ] Each state-loss scenario is recovered with a documented procedure and
      ends with successful reconciliation.

---

### M8 — Schema evolution end to end

**Goal:** Source schema changes flow through the pipeline safely — or are
stopped with a clear alert — according to the agreed policy.

**Tasks**

1. For each change type, run it on the source under load and observe the
   whole path (Debezium → registry → bronze → silver → history):
   - add a nullable column;
   - add a column with a default;
   - widen a type (`INTEGER` → `BIGINT`, `NUMERIC(10,2)` → `NUMERIC(12,2)`);
   - drop a column;
   - rename a column;
   - change a type incompatibly (`TEXT` → `INTEGER`).
2. Implement handling in the Spark jobs: automatic Iceberg schema evolution
   for allowed changes (add, widen), explicit failure with an alert for
   disallowed changes, and a documented migration procedure
   (expand-and-contract — Modules 2.7 and 2.11) for renames and drops.
3. Ensure history tables keep old columns for past versions.
4. Update the source contract and ADRs with the final policy.

**Acceptance criteria**

- [ ] Allowed changes appear in silver without restarts or data loss.
- [ ] Disallowed changes stop processing for the affected table only, alert,
      and leave existing data intact.
- [ ] A rename is completed with an expand-and-contract migration and no
      consumer breakage.

---

### M9 — Reconciliation and latency measurement

**Goal:** Prove the lakehouse equals the source, and prove the latency
SLA — continuously, not once.

**Tasks**

1. **Consistent comparison point:** capture the source state and its log
   position together (for example, a `REPEATABLE READ` transaction that
   reads `pg_current_wal_lsn()` and the table data), then wait until silver
   has processed past that position.
2. Compare per table: row counts, key sets (missing and extra keys), and
   **checksums** of canonicalised rows (per partition or key range —
   Modules 2.11 and 2.12); drill down to mismatched keys.
3. Run reconciliation on a schedule (for example hourly for counts, daily
   for full checksums) and store results in `meta.reconciliation`.
4. **Latency probes:** the workload generator writes marker rows with their
   commit time; a probe measures when each marker appears in silver; publish
   p50/p95/p99 end-to-end latency.
5. Break down latency by stage: commit → Kafka (Debezium), Kafka → bronze,
   bronze → silver.

**Acceptance criteria**

- [ ] Reconciliation passes for every table after sustained workload with
      bursts, hot keys, and deletes.
- [ ] Injected faults — a skipped micro-batch, a duplicate batch, an
      ignored delete, a corrupted row — are each detected and located to
      the exact keys.
- [ ] p95 end-to-end latency meets the SLA, with a per-stage breakdown.

---

### M10 — Table maintenance and erasure

**Goal:** Tables stay fast and affordable indefinitely, and personal data
can be removed from every copy on request.

**Tasks**

1. **Maintenance plan** per table (Module 2.15): compaction of small files
   from frequent commits, sort or clustering for common queries, **snapshot
   expiry**, **orphan file removal**, and manifest rewrites — with
   schedules and retention periods justified in an ADR.
2. Implement maintenance as Airflow DAGs (Module 2.13) that avoid or
   handle conflicts with the streaming writers.
3. Produce a **table health report**: file counts and sizes, snapshot
   counts, delete files, and storage per table.
4. **Erasure pipeline** (Module 2.20) for a customer:
   - the application deletes the customer in PostgreSQL → CDC deletes the
     silver row automatically;
   - history tables: remove or pseudonymise the customer's versions;
   - bronze change log: rewrite affected files to remove or pseudonymise
     the customer's events;
   - expire snapshots and remove old files so no copy remains in storage;
   - Kafka: rely on retention (and document the maximum time data may
     remain) or tombstones on compacted topics;
   - produce a **deletion certificate** with verification scans.

**Acceptance criteria**

- [ ] After a week of simulated load, file counts and query times stay
      within targets thanks to maintenance.
- [ ] Maintenance never corrupts tables or breaks streaming writers.
- [ ] After an erasure request and the maintenance cycle, a scan of every
      data file finds no trace of the customer's personal data; the
      certificate lists every location processed.

---

### M11 — Testing to production standard

**Goal:** A test suite that catches CDC-specific bugs quickly and reliably.

**Tasks**

1. **Unit tests** with recorded Debezium events: envelope parsing, type
   mapping, deduplication by log position, merge-plan building, SCD Type 2
   version building, hash canonicalisation.
2. **Property tests** (Hypothesis — Module 2.19): for any random sequence
   of inserts, updates, and deletes (with duplicates and re-deliveries),
   applying the change log produces the same table as applying the
   operations directly to a dictionary model; history has valid ranges;
   shuffling delivery across keys (not within a key) does not change the
   result.
3. **Integration tests** (Testcontainers or Compose): connector deployment,
   snapshot and streaming, bronze idempotency after restarts, silver
   `MERGE` with deletes, schema evolution cases.
4. **End-to-end smoke test**: start the minimal stack, run a short workload
   with deletes and a schema change, wait for catch-up with polling (never
   fixed sleeps), and run reconciliation.
5. **Regression tests** for every bug found during the project.

**Acceptance criteria**

- [ ] Re-introducing any of these bugs fails a test: ordering by processing
      time instead of log position, missing version guard, ignored
      tombstones, non-idempotent bronze writes, SCD overlaps, dropped
      columns breaking history.
- [ ] The end-to-end test ends with successful reconciliation.
- [ ] No flaky tests across 20 runs.

**At the end of M11 you have completed the Core track.** Tag the repository
`core-complete` and write a retrospective.

---

## 9. Production track

### M12 — Packaging, configuration as code, and secrets

**Goal:** Every component is reproducible, configured per environment, and
free of hard-coded credentials.

**Tasks**

1. Build container images for the Spark jobs and tools (non-root,
   `uv`-based, scanned — Module 2.18); use official images for Kafka,
   Connect with Debezium, and the catalog, pinned by version.
2. Keep **all configuration as code**: connector configs per environment,
   topic definitions, Spark job settings, table maintenance policies, and
   alert rules.
3. Move secrets (database CDC password, catalog and storage credentials,
   registry credentials) to a secrets manager or Kubernetes external
   secrets, delivered at runtime (Module 2.18); Kafka Connect should read
   them through a config provider rather than plain-text connector JSON.
4. Optionally deploy to a local Kubernetes cluster: Kafka and Connect via an
   operator or Helm, Spark jobs via Spark on Kubernetes, with resource
   requests and limits.
5. Enforce **TLS** for Kafka, the registry, PostgreSQL, and object storage
   in non-local environments (Module 2.20).

**Acceptance criteria**

- [ ] A new environment can be created from code alone.
- [ ] No credential appears in Git, images, connector JSON, or logs.

---

### M13 — CI/CD and safe upgrades of streaming jobs

**Goal:** Changes to connectors, schemas, and streaming jobs are tested and
deployed without losing state or data.

**Tasks**

1. **CI on pull requests:** lint, types, unit and property tests,
   integration tests, connector-config validation, source-migration schema
   compatibility checks (M3), image build and scan.
2. **CD:** deploy connector config changes through the Connect REST API
   idempotently; deploy streaming jobs by building an immutable image,
   stopping the running query gracefully, and starting the new version from
   the **same checkpoint**.
3. Document which changes are **checkpoint-compatible** in Structured
   Streaming and which require a new checkpoint plus a controlled replay
   from bronze or Kafka (Module 2.16).
4. Promote through `dev` → `staging` → `prod` with an end-to-end smoke test
   and reconciliation as gates (Module 2.18).
5. Write and rehearse the **rollback** procedure for a bad job version and
   for a bad connector change.

**Acceptance criteria**

- [ ] A job upgrade under continuous load loses and duplicates nothing
      (reconciliation passes afterwards).
- [ ] A checkpoint-incompatible change is deployed via a documented replay
      procedure.
- [ ] Rollback of the job and of the connector config each take one
      documented action.

---

### M14 — Observability and alerting

**Goal:** Every link in the chain is visible, and problems are detected
before the SLA is breached or the source database is endangered.

**Tasks**

1. Collect metrics (Module 2.20) for:
   - **source:** replication slot lag and **retained WAL bytes**, slot
     active status, long-running transactions;
   - **Debezium/Connect:** connector and task status, snapshot progress,
     events per second, time since last event, errors;
   - **Kafka:** consumer lag per topic and partition, under-replicated
     partitions;
   - **Spark:** input rate vs processing rate, batch duration, state and
     checkpoint health;
   - **tables:** freshness (max `_source_commit_ts`), file and snapshot
     counts;
   - **correctness:** reconciliation results and end-to-end latency
     percentiles.
2. Build dashboards: an end-to-end CDC overview and one per table.
3. Define alerts with severity, owner, and runbook links, for example:
   - retained WAL above a warning threshold → ticket; above a critical
     threshold → page (source database at risk);
   - connector or task `FAILED` → page;
   - p95 latency above SLA for 15 minutes → page;
   - consumer lag growing for 30 minutes → ticket;
   - reconciliation mismatch → ticket (page for finance tables);
   - dead-letter records present → ticket.
4. Ensure no personal data appears in logs, metrics, or alert payloads.

**Acceptance criteria**

- [ ] Every chaos scenario in M15 triggers the expected alert.
- [ ] From the dashboard alone you can answer: "Is CDC healthy? How far
      behind are we? Is the source database at risk? Is the lake correct?"

---

### M15 — Operations: runbook, chaos drills, performance, cost, and hand-over

**Goal:** Someone else can run this system confidently, and it survives
realistic infrastructure failures.

**Tasks**

1. Write `docs/runbook.md`: architecture summary; start, stop, and upgrade
   procedures; adding a table; re-snapshotting; rebuilding silver from
   bronze; handling each alert; rotating credentials; running an erasure
   request; contacts and escalation.
2. Run **chaos drills** and record timings and outcomes:
   - kill a Kafka broker; kill the Connect worker; kill the Spark driver;
   - stop the pipeline for 2 hours under load, then recover;
   - a long-running transaction on the source during streaming;
   - a traffic burst of 10× for 30 minutes;
   - an incompatible schema change;
   - a PostgreSQL restart and (if you set up a replica) a **failover** —
     and what happens to the logical replication slot (investigate
     failover-safe slot options in recent PostgreSQL versions and document
     your approach).
   Every drill must end with successful reconciliation.
3. **Performance:** measure throughput per stage, find the bottleneck
   (Debezium, Kafka partitions, Spark micro-batch, `MERGE` cost), and tune
   within the SLA (partitions, trigger interval, merge predicates,
   clustering — Modules 2.14, 2.15, 2.21).
4. **Cost** (if in the cloud): estimate always-on costs (brokers, Connect,
   Spark), storage growth of bronze and history, and compare with a
   micro-batch alternative (for example `availableNow` every 15 minutes) —
   write a recommendation (Modules 2.16, 2.21).
5. **Hand-over:** a walkthrough for a new engineer and a final
   retrospective.

**Acceptance criteria**

- [ ] All chaos drills end with reconciliation passing and no manual data
      fixes.
- [ ] Retained WAL never exceeded the critical threshold during drills (or,
      if it did, the alert fired and the runbook resolved it).
- [ ] Another person can add a table and handle an alert using only the
      runbook.
- [ ] Throughput limits and costs are documented with evidence.

---

### M16 — Optional stretch goals

- **Delta Lake variant:** implement silver in Delta Lake as well, with
  liquid clustering and change data feed, and compare with Iceberg.
- **Outbox events:** publish domain events through the Debezium outbox
  event router and land them in a separate event table.
- **Flink CDC comparison:** reimplement one table's pipeline with Flink SQL
  and CDC connectors, and compare latency and operations.
- **Multi-engine access:** query silver through the catalog from a SQL
  engine or warehouse, and apply row- and column-level access controls
  (Module 2.20).
- **Cloud deployment:** managed PostgreSQL, managed Kafka, object storage,
  and a managed catalog, created with Terraform.
- **Lineage:** emit OpenLineage events from the Spark jobs.
- **Downstream incremental consumers:** read Iceberg incremental changes to
  update a gold aggregate without full rebuilds.

---

## 10. Definition of done

**Correctness**

- [ ] Silver mirrors equal the source at every reconciliation point,
      including deletes, after workloads with bursts, hot keys, and schema
      changes.
- [ ] History tables contain every change in order with valid SCD Type 2
      ranges.
- [ ] Bronze contains every event exactly once.

**Reliability and source safety**

- [ ] Restarts, crashes, outages, and upgrades lose and duplicate nothing.
- [ ] Retained WAL stays below the agreed threshold, with alerts and a
      runbook for the edge cases.
- [ ] Re-snapshots, new tables, and rebuilds follow documented procedures.

**Governance and security**

- [ ] Schema changes follow the agreed policy and are checked in CI.
- [ ] Erasure requests are completed and proven across all lakehouse copies.
- [ ] Least-privilege CDC role, TLS, and no secrets in code or configuration.

**Engineering and operations**

- [ ] Layered tests, including property and end-to-end tests, with no
      flakiness.
- [ ] Configuration and infrastructure as code; CI/CD with safe upgrades
      and rollback.
- [ ] Dashboards and alerts across source, CDC, Kafka, Spark, tables, and
      correctness.
- [ ] Complete documentation: requirements, source contract, architecture,
      data model, ADRs, runbook, retrospective.

---

## 11. Evaluation rubric (self or peer review)

Score each area from 0 to 3. A production-grade project scores **at least 2
in every area** and **3 in Correctness, Source safety, and Reliability**.

| Area | What a "3" looks like |
| --- | --- |
| Correctness | Continuous reconciliation at consistent log positions; faults located to keys |
| Source safety | Least-privilege CDC, heartbeats, WAL limits, slot monitoring and runbooks |
| Reliability | Exactly-once effects through restarts, upgrades, and chaos drills |
| Ordering and idempotency | Dedupe and version guards by log position; replay-safe merges |
| History | Correct SCD Type 2 from the change log, including intra-batch changes |
| Schema evolution | Policy agreed, enforced in CI, handled at runtime without corruption |
| Lakehouse operations | Maintenance plan implemented; healthy files and snapshots over time |
| Privacy | Provable erasure across bronze, silver, history, snapshots, and Kafka retention |
| Observability | End-to-end metrics, SLA dashboards, actionable alerts |
| Delivery and documentation | Config as code, CI/CD, safe job upgrades, runbook usable by others |

---

## 12. Common pitfalls to avoid

- Tables without primary keys (updates and deletes cannot be applied
  correctly).
- Leaving a replication slot unconsumed until the source disk fills.
- No heartbeats, so quiet databases retain WAL indefinitely.
- Ordering changes by Kafka timestamp or processing time instead of log
  position.
- Ignoring tombstones and delete events, leaving deleted rows in silver.
- `MERGE`ing a micro-batch that contains several changes per key without
  deduplication.
- Deleting Spark checkpoints or Connect offsets to "fix" a problem.
- Kafka retention too short to rebuild after an outage.
- Believing a `DELETE` in silver satisfies an erasure request while bronze,
  history, and old snapshots still hold the data.
- Letting streaming commits create thousands of tiny files with no
  compaction.
- Secrets in plain-text connector configuration.
- Declaring success without a reconciliation at a consistent log position.

---

## 13. Suggested timeline

| Week | Milestones |
| --- | --- |
| 1 | M0 framing and platform · M1 source, CDC configuration, workload |
| 2 | M2 Debezium and Kafka · M3 contracts and registry |
| 3 | M4 bronze change log · M5 silver mirror |
| 4 | M6 history · M7 snapshots and recovery · M8 schema evolution |
| 5 | M9 reconciliation and latency · M10 maintenance and erasure · M11 testing → **Core track complete** |
| 6 | M12 packaging and secrets · M13 CI/CD and safe upgrades |
| 7 | M14 observability · M15 operations and chaos drills → **Production track complete** |
| 8 (optional) | M16 stretch goals |

---

## 14. What to show in a portfolio or interview

Be ready to explain:

1. Why log-based CDC instead of timestamp-based extraction, and what it
   costs the source database.
2. How the snapshot-to-streaming handoff avoids gaps and duplicates.
3. How you guarantee correct ordering and idempotency (log position,
   version guards, replay-safe merges).
4. How deletes and tombstones flow from PostgreSQL to silver and history.
5. How you protect the source (heartbeats, WAL limits, slot monitoring) and
   what you do when a slot is lost.
6. How you prove correctness (consistent-point reconciliation) and measure
   latency.
7. How a schema change travels through the pipeline, and what your policy
   blocks.
8. How an erasure request is honoured across bronze, silver, history,
   snapshots, and Kafka.
9. What your chaos drills showed, and what you changed because of them.

A README with an architecture diagram, a short demo (workload running,
a connector killed and recovered, a schema change handled, reconciliation
passing), and the runbook will show that you can run CDC in production —
not just set it up.
