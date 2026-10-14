# Roadmap — Module 2C.7: Real-Time OLAP and Query Engines

This is the learning roadmap for the seventh module of Stage 2C, **Data
Engineering_3**. It tells you **what** to learn about real-time OLAP
databases and distributed query engines, **in what order**, **how** to
learn each topic, and **how to prove to yourself** that you have learned it
before you move on.

A warehouse such as Snowflake or BigQuery answers analytical questions in
seconds, which is fine for analysts. But some products need analytics in
**tens of milliseconds**, at **thousands of queries per second**, on data
that is **seconds old**: user-facing dashboards ("your sales today"),
observability tools, ad-tech reporting, fraud monitoring, product
analytics. Warehouses are the wrong tool for these. A different class of
engines — **ClickHouse, Apache Druid, Apache Pinot, StarRocks, Apache
Doris** — exists for exactly this.

A second class of engines — **Trino and Presto** — does not store data at
all. It queries data **where it already lives** (lake, warehouse,
databases) with federated SQL.

This module teaches how both classes work, what makes them fast, and how
to choose between them and the warehouse you already know.

---

## 1. Module outcome

By the end of this module you will be able to:

- Explain why general warehouses struggle with user-facing, low-latency
  analytics and what real-time OLAP engines change.
- Model and tune **ClickHouse** tables: MergeTree engines, sorting keys,
  partitions, projections, and materialised views.
- Explain the architectures of **Druid** and **Pinot** (segments, roll-up,
  indexes, real-time vs historical nodes) and ingest from Kafka.
- Run federated queries with **Trino/Presto** across a lake and databases,
  and tune connectors and joins.
- Compare **StarRocks and Doris** with ClickHouse and Trino.
- Use **materialised views and pre-aggregation** to cut latency and cost.
- **Choose** an engine for a low-latency dashboard workload with a
  justified trade-off analysis.

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| SQL, window functions, EXPLAIN | Stage 2 — Module 2.6 | Everything here is SQL |
| Columnar storage, Parquet, compression, partitioning | Stage 2 — Module 2.5 | OLAP engines are columnar |
| DuckDB / vectorised execution | Stage 2 — Module 2.4 | Same ideas at cluster scale |
| Dimensional modelling, OBT | Stage 2 — Module 2.8 | Wide tables work well in OLAP |
| Kafka and streaming concepts | Stage 2 — Module 2.16 | Real-time ingestion |
| Lakehouse formats, catalogs, Hive metastore | Stage 2 — Module 2.15; Module 2C.2 | Trino reads Iceberg/Delta/Hive |
| Warehouses | Modules 2C.3–2C.5 | The baseline to compare against |
| Docker Compose | Stage 2B — Module 2B.1 | Running engines locally |
| Caching and serving | Stage 2 — Module 2.22 | Where these engines sit in the stack |

**Tools needed:**

- Docker Compose with: **ClickHouse**, **Trino** (with a Hive/Iceberg
  catalog and MinIO), **Kafka**, and optionally **Apache Pinot or Druid**
  and **StarRocks** (these are heavier — run one at a time).
- Python 3.12+ in a `uv` project: `uv add clickhouse-connect trino pinotdb
  kafka-python confluent-kafka pandas pytest`.
- A data generator for events (e.g., web events: user, page, country,
  device, revenue, timestamp) that can produce 100 million rows.

**A note on versions:** these projects move quickly (ClickHouse
releases monthly; Trino releases weekly; Druid and Pinot have major
architecture updates). Check behaviour against the version you run.

---

## 3. How the module is organised

The six topics are grouped into two phases. Work through them **in
order**.

```text
Phase A — Real-Time OLAP and Query Engines           (Intermediate → Advanced)
  01 ClickHouse architecture and MergeTree
  02 Apache Druid and Apache Pinot overview
  03 Trino and Presto: federated queries
  04 StarRocks and Doris overview

Phase B — Speed and Selection                        (Advanced)
  05 Materialised views and pre-aggregation
  06 Choosing an OLAP engine for low-latency dashboards

Consolidate
  Module mini-project: a real-time product analytics backend
```

The dependency chain:

```text
01 ► 02 ► 03 ► 04 ► 05 ► 06
one   stream query  newer  make   pick
deep  native  lakes MPP    it     one
engine engines in   engines fast
              place
```

Why this order:

- ClickHouse (01) teaches columnar OLAP internals in depth, which
  transfer to every other engine.
- Druid and Pinot (02) add pre-aggregation, real-time segments, and
  indexing ideas designed for streams.
- Trino (03) is the contrast: no storage, just compute and connectors.
- StarRocks and Doris (04) show the newer generation that blends both
  worlds.
- Pre-aggregation (05) applies to all engines; selection (06) pulls the
  decision together.

---

## 4. Suggested schedule

About **4 weeks at 8 hours per week**.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — ClickHouse |
| 2 | Topic 02 — Druid and Pinot · Topic 03 — Trino |
| 3 | Topic 04 — StarRocks/Doris · Topic 05 — materialised views and pre-aggregation |
| 4 | Topic 06 — choosing an engine · mini-project |

---

## 5. How to study every topic (the OLAP benchmark loop)

```text
Read → Predict what is fast and slow → Load the same dataset → Run the
same queries → Measure latency and concurrency → Inspect the plan and
storage → Change one design choice → Re-measure → Write it down
→ Explain aloud
```

1. **Read** the topic file once, fully.
2. **Predict** which queries will be fast and why (sort key, index,
   pre-aggregation).
3. **Load** the *same* 100M-row event dataset into each engine.
4. **Run the same 10 queries** (filters, group-bys, top-N, distinct counts,
   time series, joins).
5. **Measure** p50/p95 latency and throughput under concurrency (e.g., 1,
   10, 100 clients).
6. **Inspect** query plans, parts/segments, index usage, and compression.
7. **Change one choice** (sorting key, partitioning, index, roll-up).
8. **Re-measure** and record the effect.
9. **Write it down** in `module-2c7-notes.md`.
10. **Explain aloud** why the engine behaved as it did.

Keep one `olap_lab/` project:

```text
olap_lab/
├── docker-compose.yml   # ClickHouse, Trino + MinIO + Hive/Iceberg catalog, Kafka, (Pinot/StarRocks)
├── generator/           # event generator (batch + Kafka)
├── sql/                 # DDL and the benchmark query set per engine
├── bench/               # concurrency/latency harness in Python
├── results/             # CSVs and charts
└── tests/
```

---

## 6. Phase A — Real-Time OLAP Engines (Intermediate → Advanced)

### Topic 01 — [ClickHouse architecture and MergeTree](01-clickhouse-architecture-and-mergetree.md)

**Why it comes first:** ClickHouse is the most widely adopted open-source
real-time OLAP database. Its MergeTree design teaches the core ideas —
sorted columnar storage, sparse indexes, and background merges — in the
clearest form.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What ClickHouse is: columnar, vectorised, massively parallel OLAP; typical use cases (logs, events, product analytics) |
| Basics | Running it; `clickhouse-client`, the HTTP interface, and the Python `clickhouse-connect` library |
| Basics | Data types (including `LowCardinality`, `DateTime64`, `Nullable`, arrays, `Map`, `Tuple`, JSON); creating tables |
| Basics | Inserting data: batch inserts, formats (CSV, JSONEachRow, Parquet), and why many tiny inserts are bad |
| Intermediate | The **MergeTree** family: how data is stored as sorted, immutable **parts** and merged in the background |
| Intermediate | **`ORDER BY` (sorting key) vs `PRIMARY KEY`**: the sparse primary index (granules of ~8,192 rows) and why the sorting key is the most important design decision |
| Intermediate | **Partitioning** (`PARTITION BY`, usually by month/day): purpose (data lifecycle, not speed) and the too-many-parts trap |
| Intermediate | Compression codecs (`LZ4`, `ZSTD`, `Delta`, `DoubleDelta`, `Gorilla`), column ordering, and `LowCardinality` |
| Intermediate | **Skipping indexes** (minmax, set, bloom filter) and when they help; **projections** |
| Intermediate | Engine variants: `ReplacingMergeTree` (dedup by key), `SummingMergeTree`, `AggregatingMergeTree`, `CollapsingMergeTree`; why dedup is eventual and `FINAL` is costly |
| Intermediate | **Materialised views** as insert-time triggers and `AggregateFunction` states (`-State`/`-Merge`) |
| Advanced | Updates and deletes: lightweight deletes, mutations (`ALTER ... UPDATE/DELETE`), and designing for append-only |
| Advanced | Distributed ClickHouse: shards and replicas, `Distributed` tables, `ReplicatedMergeTree`, ClickHouse Keeper |
| Advanced | Ingestion from Kafka (Kafka table engine, ClickPipes, Kafka Connect) and from object storage (`s3` function, `S3Queue`) |
| Advanced | Query performance: `EXPLAIN`, `system.query_log`, `system.parts`, `system.part_log`, memory limits, and join behaviour (joins are weaker than in warehouses) |
| Advanced | Operations: monitoring parts and merges, TTL for data lifecycle, tiered storage, backups, and ClickHouse Cloud vs self-managed |
| Advanced | ClickHouse vs warehouses: where it wins and where it loses (joins, updates, concurrency control) |

**How to learn it**

1. Read the topic file.
2. Draw how 10 inserts become 10 parts and then merge into 1.
3. For the events table, propose a sorting key from the typical filters
   and justify the column order.

**Hands-on exercise — `experiments/01_clickhouse/`**

1. Create an `events` table with a poor sorting key (random order) and
   load 100M rows; run 10 queries and record latency.
2. Recreate with a good `ORDER BY (tenant, event_date, user_id)`; compare
   rows read and latency (`EXPLAIN indexes = 1`).
3. Insert in many small batches vs large batches; watch `system.parts`
   and "too many parts".
4. Build a `SummingMergeTree` or `AggregatingMergeTree` target fed by a
   materialised view; compare dashboard query time.
5. Use `ReplacingMergeTree` for deduplication; show duplicates before
   merge and the cost of `FINAL`.
6. Consume a Kafka topic into ClickHouse and measure end-to-end freshness.

**Checkpoint — you are ready to move on when you can:**

- [ ] Explain parts, merges, granules, and the sparse index.
- [ ] Choose a sorting key and partitioning scheme.
- [ ] Use materialised views for pre-aggregation.
- [ ] Explain why dedup and updates are different here.
- [ ] Ingest from Kafka and files with the right batching.

**Common mistakes:** partitioning too finely; a sorting key chosen
without looking at queries; row-by-row inserts; expecting mutable-row
semantics like Postgres; heavy multi-table joins as the main pattern.

---

### Topic 02 — [Apache Druid and Apache Pinot overview](02-apache-druid-and-apache-pinot-overview.md)

**Why here:** Druid and Pinot are purpose-built for user-facing analytics
on streams. Their architectures — segments, real-time ingestion, and rich
indexing — show a different set of design choices from ClickHouse.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The problem space: sub-second analytics on streaming + historical data with high concurrency (LinkedIn "Who viewed your profile", Uber, Netflix, ad-tech) |
| Basics | Time-partitioned **segments** as the unit of storage, distribution, and querying |
| Basics | Data model: a time column, dimensions, and metrics; schemas for Druid datasources and Pinot tables |
| Intermediate | **Druid architecture**: Coordinator, Overlord, Broker, Historical, MiddleManager/Indexer, Router; deep storage (S3/HDFS) and metadata store; real-time vs historical tiers |
| Intermediate | **Druid ingestion**: Kafka/Kinesis supervisors, batch ingestion, **roll-up** at ingest time (pre-aggregation), and query granularity |
| Intermediate | **Pinot architecture**: Controller, Broker, Server, Minion; real-time vs offline tables; hybrid tables; Helix/ZooKeeper |
| Intermediate | **Pinot indexes**: sorted, inverted, range, bitmap, text, JSON, and the **star-tree index** for pre-aggregation |
| Intermediate | Querying: Druid SQL and native JSON; Pinot's SQL (single-stage and multi-stage query engine) |
| Advanced | Upserts in Pinot (partial upserts, primary-key semantics) and update handling in Druid (reingestion, compaction) |
| Advanced | Segment sizing, compaction, retention rules, and tiering; replication and fault tolerance |
| Advanced | Joins and subqueries: strengths and limits in each engine |
| Advanced | Operations: scaling brokers/servers, monitoring ingestion lag, and cost of running always-on clusters |
| Advanced | Managed options (Imply, StarTree) and when a managed service beats self-hosting |
| Advanced | Druid vs Pinot vs ClickHouse in practice: ingest-time roll-up vs index-based pruning vs raw-speed scans |

**How to learn it**

1. Read the topic file.
2. Draw the Pinot (or Druid) request path from broker → servers →
   segments.
3. For an ad-impressions stream, decide what to roll up and what to keep
   raw, and what you lose by rolling up.

**Hands-on exercise — `experiments/02_druid_pinot/`**

1. Start Pinot (or Druid) with Docker; define a schema and a real-time
   table consuming from your Kafka topic.
2. Query live data and observe freshness while the generator runs.
3. Add inverted, range, and star-tree indexes (Pinot) or enable roll-up
   (Druid); compare latency for dashboard queries.
4. Run a concurrency test of 100 clients and compare against ClickHouse.
5. Stop a server/historical node and observe query behaviour.

**Checkpoint:**

- [ ] Explain segments and the real-time/historical split.
- [ ] Explain roll-up (Druid) and star-tree (Pinot).
- [ ] Ingest from Kafka into either engine.
- [ ] Compare the two with ClickHouse on architecture and operations.

**Common mistakes:** rolling up away detail you later need; too many tiny
segments; underestimating operational complexity of multi-component
clusters; using these engines for ad hoc join-heavy analytics.

---

## 7. Phase B — Query Engines Over Data in Place (Intermediate → Advanced)

### Topic 03 — [Trino and Presto: federated queries](03-trino-and-presto-federated-queries.md)

**Why here:** Trino stores nothing. It is a distributed SQL engine that
queries lakes, warehouses, and databases in place — the engine behind
Starburst, Athena (Presto-based), and many data-mesh platforms.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What Trino is (and what Presto/PrestoDB is); the origin at Facebook and the 2019–2020 fork into PrestoDB and Trino |
| Basics | Architecture: **coordinator**, **workers**, stages, tasks, splits, and exchanges; MPP in memory with pipelined execution |
| Basics | Catalogs, schemas, tables; connecting with the CLI, JDBC, and the Python `trino` client |
| Intermediate | **Connectors**: Hive, Iceberg, Delta Lake, PostgreSQL/MySQL, Kafka, MongoDB, Elasticsearch, BigQuery, Snowflake; one query across several |
| Intermediate | Querying Parquet/ORC on object storage with the Hive/Iceberg connector and a metastore; partition pruning |
| Intermediate | **Federated joins** (lake ⋈ database) and the cost of moving data; predicate/projection/aggregation **pushdown** |
| Intermediate | `EXPLAIN` and `EXPLAIN ANALYZE`; join distribution (broadcast vs partitioned); statistics and the cost-based optimiser (`ANALYZE`) |
| Intermediate | Writing: `CREATE TABLE AS`, `INSERT`, and Iceberg `MERGE`; table maintenance (`optimize`, `expire_snapshots`) |
| Advanced | Memory management, spilling, query limits, resource groups, and multi-tenant isolation |
| Advanced | Fault-tolerant execution (FTE) for long ETL queries; autoscaling workers on Kubernetes |
| Advanced | Security: authentication (LDAP, OAuth2, Kerberos), access control (file-based, Ranger, OPA), and row/column filters |
| Advanced | Performance tuning: file sizes, table statistics, dynamic filtering, and caching (Alluxio, filesystem cache) |
| Advanced | Trino vs Spark SQL vs Athena vs warehouses for interactive vs ETL work; Trino as a data-virtualisation layer in a mesh (links to Module 2C.8) |

**How to learn it**

1. Read the topic file.
2. Draw a query joining an Iceberg table on MinIO with a PostgreSQL table;
   mark where data moves and what is pushed down.
3. List what Trino is good at and what it is not.

**Hands-on exercise — `experiments/03_trino/`**

1. Start Trino with Iceberg (MinIO + REST/Hive catalog) and PostgreSQL
   catalogs.
2. Query Iceberg tables with partition filters; compare `EXPLAIN
   ANALYZE` input rows with and without pruning.
3. Write a federated join and inspect pushdown in the plan; change the
   join so more is pushed down.
4. Run `ANALYZE` and watch the optimiser change a join distribution.
5. Create resource groups and prove isolation between "dashboard" and
   "etl" users.
6. Run the same query on Trino and DuckDB; compare for small and large
   data.

**Checkpoint:**

- [ ] Explain coordinator, workers, connectors, and catalogs.
- [ ] Write and tune a federated query.
- [ ] Read `EXPLAIN ANALYZE` and spot pushdown.
- [ ] Explain when Trino is not the right tool.

**Common mistakes:** no table statistics; huge cross-database joins with
no filter pushdown; treating Trino as a low-latency serving layer;
ignoring small files in the lake.

---

### Topic 04 — [StarRocks and Doris overview](04-starrocks-and-doris-overview.md)

**Why here:** StarRocks and Apache Doris are newer MPP OLAP engines that
combine fast columnar storage with strong SQL (joins, updates) and lake
access. They are increasingly chosen as ClickHouse or Trino alternatives.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Where they fit: real-time analytics with strong **join** performance, high concurrency, and MySQL-protocol compatibility |
| Basics | Architecture: Frontend (FE: metadata, planning) and Backend (BE) nodes — plus compute nodes (CN) in StarRocks' shared-data mode |
| Basics | Connecting with any MySQL client; basic DDL and loading |
| Intermediate | Table models: duplicate, aggregate, unique/primary key (real-time upserts), and updates; sort keys and prefix indexes |
| Intermediate | Distribution: partitions and buckets; colocation for joins; bitmap and bloom filter indexes |
| Intermediate | Loading: Stream Load, Routine Load from Kafka, Broker/Spark/Flink connectors, and CDC pipelines |
| Intermediate | **Materialised views**: synchronous and asynchronous, with query rewrite (automatic use by the optimiser) |
| Advanced | Querying the lake: external catalogs for Hive, Iceberg, Delta, Hudi — a Trino-like use with local caching |
| Advanced | Shared-data (storage–compute separation) architecture vs shared-nothing; elasticity and cost |
| Advanced | Cost-based optimiser, runtime filters, vectorised execution and CBO strengths on multi-table joins |
| Advanced | Comparison: StarRocks/Doris vs ClickHouse (joins, updates, ops), vs Trino (storage, latency), vs Druid/Pinot (semantics, indexing) |
| Advanced | Ecosystem and managed services (CelerData, VeloDB), community maturity, and risk assessment |

**How to learn it**

1. Read the topic file.
2. Take a star-schema dashboard query (fact + 3 dimensions) and predict
   its behaviour on ClickHouse vs StarRocks.
3. Decide when "joins done well" is the deciding factor.

**Hands-on exercise — `experiments/04_starrocks_doris/`**

1. Start StarRocks (or Doris) with Docker; create a primary key table and
   a duplicate-key table.
2. Load via Routine Load from Kafka; test an upsert and read your write.
3. Run a 4-table star join and compare with ClickHouse's time.
4. Create an asynchronous materialised view and verify automatic query
   rewrite.
5. Query an Iceberg table through an external catalog and compare with
   Trino.

**Checkpoint:**

- [ ] Explain FE/BE architecture and table models.
- [ ] Use primary-key tables for upserts.
- [ ] Use materialised views with automatic rewrite.
- [ ] Place them accurately in the engine landscape.

**Common mistakes:** choosing based on benchmarks alone; ignoring
operational maturity and community support; mapping tables to the wrong
model (duplicate vs primary key).

---

## 8. Phase C — Speed and Selection (Advanced)

### Topic 05 — [Materialized views and pre-aggregation](05-materialized-views-and-pre-aggregation.md)

**Why here:** the fastest query is one that has been computed already.
Pre-aggregation is the universal lever across every engine, but it must be
designed carefully.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why pre-aggregate: dashboard queries repeat the same group-bys; trade storage and write cost for read speed |
| Basics | Materialised view vs view vs summary table vs cache; refresh models (on-insert, scheduled, incremental, full) |
| Basics | Common aggregates: counts, sums, min/max — and why averages and distinct counts need special state |
| Intermediate | **Rollup / cube / aggregate tables**: choosing dimensions and time grain; the cardinality explosion problem |
| Intermediate | Mergeable aggregates: `AggregateFunction` states (ClickHouse), HyperLogLog, t-digest and theta sketches (links to Module 2C.9) |
| Intermediate | Engine-specific forms: ClickHouse MVs and projections; Druid roll-up; Pinot star-tree; StarRocks async MVs with rewrite; Snowflake dynamic tables (Module 2C.3); BigQuery materialised views (Module 2C.4); Trino MVs on Iceberg |
| Intermediate | Late and updated data: how corrections propagate (or don't) into aggregates |
| Advanced | Designing **a tiered aggregate pyramid**: raw → minute → hour → day, with retention at each level |
| Advanced | Query routing and rewrite: automatic (optimizer) vs manual (application chooses the table) |
| Advanced | Correctness: reconciling aggregates with raw data; drift detection; backfills when logic changes |
| Advanced | Cost model: write amplification, storage growth, and refresh compute vs query savings |
| Advanced | Caching layers (Redis, result caches, CDN) vs pre-aggregation: when each is right (links to Module 2.22 Topic 02) |

**How to learn it**

1. Read the topic file.
2. List the 10 dashboard queries and group them by dimension set to find
   the minimum number of aggregates that serve them all.
3. Estimate row counts for each aggregate level.

**Hands-on exercise — `experiments/05_preaggregation/`**

1. Pick the three slowest dashboard queries from your benchmark.
2. Build minute and hour roll-ups using ClickHouse MVs, and an
   equivalent in one other engine.
3. Use `uniqState`/`uniqMerge` (or HLL) so distinct counts roll up
   correctly; show the error vs exact.
4. Insert late and corrected events; show how aggregates change (or fail
   to).
5. Write a reconciliation query comparing aggregate totals to raw data.
6. Measure storage, write overhead, and query speedup.

**Checkpoint:**

- [ ] Choose aggregates from query patterns.
- [ ] Roll up non-additive measures correctly.
- [ ] Handle late data and backfills in aggregates.
- [ ] Reconcile aggregates with raw data.

**Common mistakes:** pre-aggregating on high-cardinality dimensions;
averaging averages; no reconciliation; forgetting how updates affect
aggregates.

---

### Topic 06 — [Choosing an OLAP engine for low-latency dashboards](06-choosing-an-olap-engine-for-low-latency-dashboards.md)

**Why it comes last:** choosing an engine is a senior skill. It requires
all of the above plus a method that is fair, repeatable, and honest about
trade-offs.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The decision dimensions: latency (p50/p99), concurrency (QPS), freshness, data volume, query shapes, update patterns, team skills, cost |
| Basics | Workload classes: internal BI, embedded/user-facing analytics, observability/log analytics, ad hoc exploration, lakehouse virtualisation |
| Basics | Quick map: warehouse (BI, ad hoc, ELT), ClickHouse (fast scans, logs, events), Druid/Pinot (high-QPS user-facing on streams), StarRocks/Doris (joins + real-time), Trino (federation, lake queries), DuckDB (single-node), Postgres (small data) |
| Intermediate | Designing a **fair benchmark**: representative data, real query mix, warm/cold cache, concurrency, and recording hardware and cost |
| Intermediate | Reading public benchmarks (ClickBench, SSB, TPC-H/DS) critically; vendor claims vs your workload |
| Intermediate | Total cost of ownership: compute, storage, ingestion, ops effort, managed-service fees, and egress |
| Intermediate | Freshness vs latency trade-offs and the architecture needed (streaming ingestion, pre-aggregation, caching) |
| Advanced | Hybrid architectures: warehouse/lakehouse as the source of truth + an OLAP serving layer for hot dashboards; reverse ETL; semantic layer in front |
| Advanced | Operational risk: maturity, community, hiring, managed offerings, upgrade pain, multi-tenant isolation, and failure modes |
| Advanced | Migration and exit costs; avoiding lock-in with open formats (Iceberg) and standard SQL |
| Advanced | Writing a decision record (ADR) that a skeptical CTO can accept (links to Module 2C.8) |
| Advanced | Case studies: product analytics, observability, ad-tech reporting, fintech risk dashboards |

**How to learn it**

1. Read the topic file.
2. Write a requirements sheet for three scenarios (internal exec
   dashboard, customer-facing usage dashboard, log analytics).
3. For each, pick an engine and write down what would make you wrong.

**Hands-on exercise — `experiments/06_choosing_engine/`**

1. Run your 10-query benchmark at 1, 10, and 100 concurrent clients on
   ClickHouse, a lake engine (Trino), and one of Pinot/Druid/StarRocks.
2. Add a warehouse (DuckDB as a stand-in, or a trial warehouse) as the
   baseline.
3. Record latency percentiles, throughput, load time, storage size, and a
   cost estimate per month.
4. Write a decision record with the matrix, the winner for each scenario,
   risks, and a migration/exit plan.

**Checkpoint:**

- [ ] Define workload requirements precisely.
- [ ] Design a fair benchmark.
- [ ] Compare engines on total cost, not just speed.
- [ ] Write a defensible architecture decision record.

**Common mistakes:** choosing the trendiest engine; benchmarking with a
cold cache or unrealistic queries; ignoring operational burden; treating a
serving layer as the system of record.

---

## 9. Module mini-project — a real-time product analytics backend

**Goal:** serve a customer-facing dashboard with sub-second latency on
fresh data.

**Requirements**

1. A generator produces 100M+ events plus a Kafka stream (late and
   duplicate events included).
2. The lakehouse holds raw history (Iceberg on MinIO) and is queryable
   through Trino.
3. A real-time engine (ClickHouse, or Pinot/StarRocks) ingests the same
   stream with pre-aggregated tables for the dashboard.
4. A small API (FastAPI, Module 2.22) serves five dashboard endpoints from
   the OLAP engine with caching.
5. A benchmark report with p50/p95 latency at 1/10/100 concurrent users and
   freshness measured end to end.
6. A reconciliation job comparing OLAP aggregates with lakehouse truth.
7. A decision record explaining the engine choice and when you would
   switch.

**Done when** dashboard queries answer in under a second at 100
concurrent users, new events appear within seconds, aggregates reconcile
with raw data, and your record explains every trade-off.

---

## 10. Module self-assessment — exit criteria

You have completed this module when you can do all of the following
**without notes**:

- [ ] Explain why warehouses are not ideal for user-facing analytics.
- [ ] Design ClickHouse tables with correct sorting keys, partitions, and
      materialised views.
- [ ] Explain Druid and Pinot architectures, roll-up, and star-tree
      indexes.
- [ ] Write and tune federated queries in Trino.
- [ ] Place StarRocks/Doris relative to the other engines.
- [ ] Pre-aggregate correctly, including non-additive measures.
- [ ] Choose an engine with a fair benchmark and a written decision.

---

## 11. Recommended reading and references

- ClickHouse documentation and the ClickHouse "MergeTree" and "sparse
  primary index" guides; the ClickBench project.
- Apache Druid, Apache Pinot, StarRocks, and Apache Doris documentation.
- *Trino: The Definitive Guide* — Matt Fuller et al.
- Papers and talks: Druid paper, Pinot papers (LinkedIn), Presto paper.
- *Designing Data-Intensive Applications* — Kleppmann (storage engines and
  OLAP chapters).

---

## 12. Where this module leads

- **Module 2C.8** uses these engines as building blocks in platform
  architecture, data products, and build-vs-buy decisions.
- **Module 2C.9** covers sketches (HyperLogLog) and dashboards that run on
  these engines.
- **Module 2C.10** covers the feature and training data paths that sit
  next to serving analytics.
