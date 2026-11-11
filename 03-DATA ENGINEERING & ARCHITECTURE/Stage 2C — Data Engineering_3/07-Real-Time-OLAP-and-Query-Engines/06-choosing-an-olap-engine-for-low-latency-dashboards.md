# Choosing an OLAP Engine for Low-Latency Dashboards

> **Module:** Stage 2C — Data Engineering_3 / `07-Real-Time-OLAP-and-Query-Engines/`  
> **Lesson:** `06-choosing-an-olap-engine-for-low-latency-dashboards.md`  
> **Level:** Intermediate → advanced  
> **Purpose:** Select an engine from workload evidence, not popularity or a single benchmark score.

## 1. Learning objectives and prerequisites

By the end of this lesson, you should be able to:

- Turn business needs into measurable service-level objectives (SLOs), workload requirements, and hard acceptance gates.
- Distinguish query latency, throughput, concurrency, data freshness, and end-to-end response time.
- Classify workloads and create a shortlist across warehouses, ClickHouse, Druid, Pinot, StarRocks/Doris, Trino, DuckDB, and PostgreSQL.
- Design a fair ten-query benchmark with cold/warm cache runs and concurrency levels 1, 10, and 100.
- Interpret p50/p95/p99, QPS, load time, freshness, storage, and cost without overstating what the measurements prove.
- Read ClickBench, SSB, TPC-H, and TPC-DS critically.
- Estimate total cost of ownership (TCO), including operations, streaming, refreshes, egress, and exit costs.
- Decide when a serving layer, pre-aggregation, caching, a semantic layer, or a hybrid architecture is justified.
- Produce a defensible architecture decision record (ADR) with evidence, alternatives, risks, mitigations, and reconsideration criteria.

### Prerequisites

This lesson builds on the earlier lessons in Module 2C.7:

1. ClickHouse architecture and MergeTree, sorting keys, projections, materialized views, and query plans.
2. Druid and Pinot segments, streaming ingestion, roll-up, and star-tree indexes.
3. Trino/Presto architecture, connectors, pushdown, join distribution, and Iceberg.
4. StarRocks/Doris table models, joins, and asynchronous materialized views.
5. Materialized views and pre-aggregation, including non-additive metrics and correction handling.

Also useful: SQL and `EXPLAIN`, dimensional modeling, Kafka, lakehouse formats, Docker Compose, benchmarking basics, caching/serving, and warehouse cost models. This lesson integrates those ideas rather than teaching each engine from scratch.

### Project-tree placement and dependencies

The project tree places this file at:

```text
Stage 2C — Data Engineering_3/
└── 07-Real-Time-OLAP-and-Query-Engines/
    ├── 01-clickhouse-architecture-and-mergetree.md
    ├── 02-apache-druid-and-apache-pinot-overview.md
    ├── 03-trino-and-presto-federated-queries.md
    ├── 04-starrocks-and-doris-overview.md
    ├── 05-materialized-views-and-pre-aggregation.md
    └── 06-choosing-an-olap-engine-for-low-latency-dashboards.md
```

The roadmap's shared benchmark workspace is `olap_lab/`; this lesson's decision experiment belongs under `experiments/06_choosing_engine/`.

---

## 2. A repeatable engine-selection framework

Engine selection is a constrained decision, not a popularity contest. First define the workload and the non-negotiable requirements. Then shortlist engines, form hypotheses, benchmark fairly, inspect plans, estimate TCO, and record the decision.

```text
Define workload + SLOs
        ↓
Separate hard gates from preferences
        ↓
Shortlist engines by workload class
        ↓
Write hypotheses and benchmark plan
        ↓
Run same data + same query mix + controlled resources
        ↓
Inspect plans, latency, throughput, freshness, storage, cost
        ↓
Reject candidates that fail hard gates
        ↓
Compare remaining trade-offs and operating burden
        ↓
Choose architecture; record rejected alternatives
        ↓
Set monitoring, migration, exit, and reconsideration triggers
```

### 2.1 Hard acceptance gates versus weighted preferences

A hard gate is mandatory. A candidate that fails it should not win because it scores well on other dimensions. Examples:

- p99 query latency must be at or below 300 ms at 100 concurrent clients.
- 95% of accepted events must be queryable within 5 seconds.
- Corrected records must become visible within 2 minutes.
- The system must meet a defined availability and recovery objective.
- Sensitive data must meet access-control and residency requirements.
- Monthly run cost must remain under an approved budget.

Weighted preferences help rank candidates **only after** hard gates are met. Examples include team familiarity, query flexibility, ecosystem fit, or lower migration effort.

### 2.2 Define the workload before choosing the engine

Document the following:

| Dimension | Questions to answer | Evidence |
|---|---|---|
| Query latency | What are p50/p95/p99 targets? Are these database-only or API end-to-end? | Request traces and query logs |
| Throughput | How many completed queries per second are required at peak? | Traffic forecast/load tests |
| Concurrency | How many in-flight queries and active users? What is the arrival pattern? | Production metrics |
| Freshness | How old may the newest accepted event be when visible? | Source timestamp and query visibility timestamp |
| Volume | Current rows/bytes, daily ingest, retention, growth, cardinality | Data profiling and forecasts |
| Query mix | Filters, group-bys, top-N, distincts, time series, joins, scans | Representative query log |
| Mutability | Append-only, duplicate deliveries, upserts, deletes, corrections, late events | Source contract and correction policy |
| Availability | Required uptime, replicas, RPO/RTO, regional needs | Service requirements |
| Tenancy | Shared or isolated customers? Per-tenant quotas? Noisy-neighbor tolerance? | Product/security requirements |
| Governance | RBAC, row/column security, audit, lineage, retention | Compliance/security review |
| Team capability | Who operates it? What is the on-call experience? | Skills and staffing plan |
| Cost | Compute, storage, ingest, egress, operations, managed service, migration | Comparable monthly model |

**Why one latency number is insufficient:** one fast query at concurrency 1 says little about p99 under 100 clients, tail behavior during ingestion, freshness, failure recovery, or monthly cost. A design can have low p50 but terrible p99 due to queueing, compaction, memory pressure, or skew. It can return queries quickly while serving stale data.

---

## 3. Latency, throughput, concurrency, and freshness

### 3.1 Definitions

- **Query latency:** elapsed time for one query from a defined start point to its completion. Specify whether client/network time is included.
- **p50:** median query latency; half of measured queries complete at or below this value.
- **p95:** 95% of measured queries complete at or below this value.
- **p99:** 99% of measured queries complete at or below this value. It needs enough samples to be meaningful; with a tiny sample, p99 is unstable.
- **Throughput / QPS:** completed queries per second over a defined interval. State whether failures/timeouts are excluded and how mixed query weights are counted.
- **Concurrency:** number of queries in flight at a moment, or the number of clients generating requests. These are not identical: a client may wait between requests.
- **Ingestion freshness:** age of the newest eligible source event that is query-visible.
- **End-to-end response time:** from the user's action through application/API, cache, database, network, serialization, and rendering to the user-visible response.

Freshness can be measured per event as:

\[
\text{visibility delay} = t_{\text{query-visible}} - t_{\text{event-created}}
\]

If the producer timestamp is untrusted, also record ingestion-received time. Report p50/p95/p99 freshness delay and the source watermark, not only a mean.

A typical end-to-end budget can be allocated as:

\[
T_{\text{response}} =
T_{\text{client/network}} +
T_{\text{API}} +
T_{\text{cache}} +
T_{\text{database}} +
T_{\text{serialization/render}}
\]

A cache hit may make the database invisible in the response path, but it can also return stale data. Measure cache hit rate and freshness alongside latency.

### 3.2 Example of an SLO sheet

The values below are **illustrative requirements**, not benchmark results.

| Requirement | Illustrative target | Type |
|---|---:|---|
| Database query p95 | ≤ 150 ms | Hard gate |
| Database query p99 | ≤ 400 ms | Hard gate |
| End-to-end API p95 | ≤ 250 ms | Hard gate |
| Event visibility delay p95 | ≤ 5 seconds | Hard gate |
| Peak concurrent clients | 100 | Test condition |
| Sustained throughput | ≥ 500 completed queries/s at stated mix | Hard gate |
| Corrected-event propagation | ≤ 2 minutes | Hard gate |
| Monthly platform cost | ≤ $8,000 | Hard gate |
| Team's on-call readiness | Runbook + trained primary/secondary | Hard gate |

Do not use the example targets without confirming that they reflect the product's user experience and business risk. A fraud dashboard and a monthly executive report have very different freshness and availability needs.

---

## 4. Workload classification

The engine categories in the roadmap are useful starting hypotheses. They are not rules that override workload evidence.

### 4.1 Workload classes

| Workload | Typical shape | Initial shortlist | What could change the recommendation? |
|---|---|---|---|
| Internal BI / executive dashboard | Scheduled refresh, joins, broad dimensions, many analysts, minute-level freshness often acceptable | Warehouse; StarRocks/Doris if real-time or high concurrency dominates | Strong real-time SLA, heavy event scans, existing warehouse economics, or very complex joins |
| Embedded/customer-facing analytics | Many tenants, parameterized filters, predictable group-bys, high QPS, tight tail latency | Pinot, Druid, ClickHouse, StarRocks/Doris | Join-heavy queries favor StarRocks/Doris; unusual arbitrary queries may favor warehouse or Trino; tenancy and security can disqualify an otherwise fast engine |
| Product analytics | Event scans, cohorts, time series, distinct users, event freshness | ClickHouse, Pinot, Druid; StarRocks/Doris if join-heavy | Corrections, exact distincts, high dimensionality, and team experience may alter the choice |
| Observability/log analytics | High ingest, time filtering, high-cardinality labels, retention/TTL, text search varies | ClickHouse; Druid/Pinot for suitable metric dimensions; specialized observability stack if search requirements dominate | Need for full-text search, traces correlation, alerting ecosystem, or strict ingest durability |
| Ad-tech reporting | Impression/click events, dimensions, high concurrency, deduplication, late attribution | ClickHouse, Druid, Pinot, StarRocks/Doris | Strong multi-table joins and correction/upsert patterns may favor StarRocks/Doris; sketch semantics and audit requirements matter |
| Fintech risk dashboards | Fresh events, low-latency risk slices, strict correctness/audit, corrections | ClickHouse or StarRocks/Doris; Pinot/Druid if query shape fits | Exactness, transactional boundaries, explainability, and regulatory audit may require canonical warehouse/operational source alongside serving layer |
| Ad hoc exploration | Unpredictable queries, joins, evolving questions | Warehouse; Trino over lake/warehouse; DuckDB for local analysis | Data volume, concurrency, source locality, and governance |
| Lakehouse query federation | Data remains in Iceberg/other catalogs and databases; connector pushdown important | Trino | If low-latency serving and predictable query patterns become dominant, materialize a serving layer |
| Single-node analysis | Local Parquet/CSV, exploratory SQL, modest scale | DuckDB | Multi-user concurrency, high availability, continuously streaming ingestion, or data larger than practical local resources |
| Small operational dataset | Point lookups, transactions, constraints, modest reporting | PostgreSQL | Large scan-heavy analytics may require columnar/OLAP serving; don't use PostgreSQL as a high-scale OLAP engine just because SQL is familiar |

### 4.2 Decision tree

```text
Is the primary need transactional writes/point lookups?
  ├─ Yes → PostgreSQL or another OLTP database; add analytics separately if needed.
  └─ No
      Is data already in a lake/warehouse and federation the main need?
        ├─ Yes → Trino or warehouse-native query path; test pushdown and concurrency.
        └─ No
            Is this a single-user/local analytical workflow?
              ├─ Yes → DuckDB is a strong baseline.
              └─ No
                  Are dashboard queries predictable, very high-QPS, and stream-fresh?
                    ├─ Yes → Evaluate ClickHouse, Druid, Pinot, StarRocks/Doris.
                    └─ No → Warehouse is a strong default for BI/ad hoc/ELT.
```

For the real-time branch, narrow further by query shape:

- **Fast scans, event/log analytics, flexible aggregations:** include ClickHouse.
- **Streaming-oriented, high-QPS analytics with stable dimensional queries:** include Druid and/or Pinot.
- **Frequent multi-table joins and real-time updates:** include StarRocks and/or Doris.
- **Data should remain in place and queries are federated:** include Trino, but do not assume it is the best serving layer for strict sub-second QPS.
- **Warehouse already meets the SLO at acceptable cost:** keeping it is a valid and often preferable outcome.

### 4.3 Engine landscape: hypotheses, not guarantees

| Engine/category | Strong initial hypothesis | Main trade-offs to investigate |
|---|---|---|
| General-purpose warehouse (e.g., Snowflake/BigQuery) | BI, ad hoc SQL, ELT, governed analytics, elastic managed compute | Interactive tail latency at high concurrency, refresh/freshness, per-query/slot costs, workload isolation |
| ClickHouse | High-volume scans, logs/events, fast aggregation, columnar workloads | Operational model, joins/update semantics, ingestion and correction design, cluster sizing |
| Apache Druid | Streaming-oriented time-series/dimensional analytics with ingestion-time roll-up | Roll-up information loss, segment lifecycle, ingestion/reindex/compaction operations, join/query constraints |
| Apache Pinot | User-facing, high-concurrency analytics on fresh event data with suitable indexes | Segment/index design, mutable/upsert semantics, cluster complexity, supported query patterns |
| StarRocks / Apache Doris | Real-time OLAP with SQL and strong multi-table joins | Refresh/rewrite eligibility, data model, ingestion/update behavior, cluster operations and version-specific features |
| Trino | Federated SQL over lakehouse, warehouses, and databases | Data movement, connector pushdown, file layout/statistics, concurrency and interactive latency |
| DuckDB | Single-node local analysis and reproducible data exploration | Multi-user service requirements, availability, shared state, dataset size and operational serving |
| PostgreSQL | Small operational data with transactions and point access | Scan-heavy aggregation at scale, write/read contention, index/storage amplification |
| Hybrid warehouse + serving OLAP | Warehouse/lake as canonical history; serving store for hot dashboard patterns | Duplicate data, consistency/reconciliation, pipeline failures, additional operations and cost |

No row is a universal winner. Validate the exact release, managed offering, connector, feature limits, and team capability. Open-source availability does not mean zero operating cost.

---

## 5. Requirements sheets for three baseline scenarios

The roadmap requires requirements sheets for an internal executive dashboard, a customer-facing usage dashboard, and log analytics. Start with these templates and replace every illustrative assumption with actual product requirements.

### 5.1 Internal executive dashboard

| Field | Initial requirement sheet |
|---|---|
| Users / traffic | 50–300 internal users; mostly business-hour usage (illustrative) |
| Queries | 10–30 known dashboard queries; joins, group-bys, top-N, period comparisons |
| Freshness | 5–15 minutes may be acceptable (must confirm) |
| Latency | p95 1–3 seconds may be acceptable for complex BI (must confirm) |
| Data | Curated dimensional facts, daily/hourly rollups, governed metrics |
| Corrections | Warehouse ELT and controlled backfills |
| Shortlist | Existing warehouse first; StarRocks/Doris or ClickHouse if SLO/concurrency evidence justifies serving layer |
| Acceptance evidence | Query mix meets latency at expected concurrency; freshness and monthly cost meet target; semantic definitions match |
| Risks | Dashboard proliferation, inconsistent metric definitions, warehouse contention |
| Reconsider if | Freshness falls to seconds, QPS grows substantially, or a serving layer demonstrably reduces total cost while meeting correctness needs |

### 5.2 Customer-facing usage dashboard

| Field | Initial requirement sheet |
|---|---|
| Users / traffic | Multi-tenant application; traffic can spike with customer activity |
| Queries | Tenant-scoped filters, time series, breakdowns, top-N, distinct usage metrics |
| Freshness | Seconds to a minute depending on product promise |
| Latency | p95/p99 API budget must be explicit; database is only one part |
| Data | Event stream plus canonical lake/warehouse history |
| Corrections | Duplicate/late events, account changes, reprocessing, tenant deletion |
| Shortlist | ClickHouse, Pinot, Druid, StarRocks/Doris; test warehouse as baseline if it might meet requirements |
| Acceptance evidence | p95/p99 at 1/10/100 clients, freshness distribution, tenant isolation, correctness and cost |
| Risks | Noisy neighbors, stale cache, authorization bugs, duplicated metrics, backfill drift |
| Reconsider if | Joins dominate, dimensions become unpredictable, or tenant-specific isolation cannot be achieved economically |

### 5.3 Log analytics

| Field | Initial requirement sheet |
|---|---|
| Users / traffic | Engineers and automated dashboards; bursts during incidents |
| Queries | Recent-time filters, service/host filters, group-bys, top-N errors, time series, possibly text search |
| Freshness | Seconds or less for operational signals (confirm) |
| Latency | Fast incident queries, with p95/p99 targets under concurrent load |
| Data | High ingest volume, high-cardinality labels, retention tiers |
| Corrections | Late arrival, duplicate delivery, retention/deletion requirements |
| Shortlist | ClickHouse; Druid/Pinot for dimensional workloads; compare specialized stack if full-text/trace workflow is central |
| Acceptance evidence | Ingest rate, freshness under burst, query latency, compression/storage, retention cost, failure recovery |
| Risks | Cardinality explosion, index bloat, ingest backpressure, expensive long-range scans |
| Reconsider if | Text search, trace correlation, alerting integrations, or operational UX dominate simple OLAP aggregation |

---

## 6. Fair benchmark design

A benchmark should test the workload the product actually has, not whichever query makes a favorite engine look fast. The same logical data and query semantics are required; the physical layout can be engine-appropriate, but every optimization must be documented.

### 6.1 Representative data

Use a representative data generator or a sanitized production sample. Capture:

- Total rows and compressed/uncompressed bytes.
- Rows per second and burst profile.
- Event-time distribution and out-of-order/late-event rate.
- Duplicate rate and correction/upsert rate.
- Cardinality of tenant, user, country, device, page, service, status, and other dimensions.
- Null/missing values, skew, hot keys, and long-tail tenants.
- Retention and partition/time distribution.
- Data types, timestamp timezone, decimal precision, and exactness requirements.

A uniform synthetic generator often hides skew and hot tenants. A dataset with no duplicates or late events cannot evaluate correction behavior. A tiny dataset can validate SQL semantics but cannot establish scale performance.

### 6.2 Ten-query standard workload

Use one logical query set across candidates. Adapt syntax to each engine while preserving semantics, result columns, filters, and data interval. The following query shapes are a **benchmark template**; replace field names with your schema and verify exact result equivalence.

| ID | Query shape | What it tests |
|---|---|---|
| Q1 | Filtered event count over a short time window | Time pruning and scan efficiency |
| Q2 | Filtered sum/revenue by hour | Time-series aggregation |
| Q3 | Group by country and device | Dimensional aggregation |
| Q4 | Top 20 pages/services by event count | Grouping, ordering, top-N |
| Q5 | Exact distinct users/sessions | Non-additive aggregate correctness and cost |
| Q6 | Approximate distinct users using supported sketch | Accuracy/cost trade-off versus Q5 |
| Q7 | Error/status distribution by 5-minute bucket | Time-series rollup and cardinality |
| Q8 | Join facts to a small dimension table | Join planning and broadcast/locality |
| Q9 | Join two substantial tables with filters | Multi-table join performance and shuffle/data movement |
| Q10 | Long-range query over 30–90 days with a selective filter | Retention layout, pruning, storage scan |

Use a documented parameter set for each query: time window, tenant distribution, selectivity, output size, and whether results are cached. A benchmark that compares exact distincts in one engine to approximate distincts in another is not a fair comparison.

### 6.3 Same semantics, engine-appropriate physical design

For each candidate:

1. Load the same logical records and preserve the same filters and timestamp semantics.
2. Use the engine's recommended table/partition/sort/index design for the stated workload.
3. Document all pre-aggregation, indexes, projections, star-tree settings, caches, and refresh policies.
4. Run a raw/unoptimized baseline where practical, then the production-like tuned design.
5. Compare result checksums or exact output equivalence for exact metrics.
6. Record approximation error separately for approximate metrics.
7. Explain whether the candidate is storing data, querying in place, or serving a precomputed copy.

**Fairness does not mean identical DDL.** ClickHouse MergeTree ordering, Pinot star-tree, Druid roll-up, and warehouse clustering are different mechanisms. Fairness means comparable data, semantics, resource budgets, query mix, freshness requirements, and transparent disclosure of each engine's design.

### 6.4 Cold cache and warm cache

Run separate trials:

- **Cold/first-run:** define what “cold” means. Clearing OS caches may be unsafe or impossible in managed environments; restarting an engine is not necessarily equivalent to clearing every cache. Record the actual procedure.
- **Warm/repeated:** execute a warm-up phase, then measure steady-state requests. Record whether result cache, page cache, compiled plans, or application cache is enabled.
- **Cache-disabled (if supported):** useful for isolating engine work, but not necessarily representative of production.
- **Production-like cache:** use the expected dashboard request distribution and cache policy.

Do not compare one engine's cold run to another engine's warm run. Report both if both matter.

### 6.5 Concurrency and arrival model

The required concurrency levels are 1, 10, and 100 clients. At each level:

- Use the same query mix and request pacing.
- Distinguish closed-loop clients (wait for response before next request) from open-loop load (requests arrive at a target rate). Closed-loop tests can hide queueing/overload because request rate drops as latency increases.
- Ramp up, allow warm-up, then measure a fixed steady-state window.
- Include realistic bursts and long-running query mix.
- Record timeouts, errors, retries, and cancellations; do not report latency only for successful fast requests.
- Test ingestion concurrently with queries for streaming workloads.
- Keep resource limits and cluster shape documented.
- Use the same steady-state duration, ramp-up, and arrival schedule for each candidate; repeat runs and report offered load, completed QPS, errors, and timeouts together. If the engine cannot sustain the offered rate, do not reduce the load silently and compare the resulting lower-rate latency as though it were equivalent.

### 6.6 Latency sample size and percentile reporting

For each query class and concurrency setting, record count of successful queries, failures, p50, p95, and p99 where sample size supports it. p99 from a few dozen samples is not stable enough for a strong claim. Capture the histogram or raw per-query latency values when possible.

Do not average percentiles across queries. Report per-query or per-class percentiles, and if a single overall metric is needed, define the weighting by production query frequency. As a practical planning rule, collect at least 10,000 observations per query class × concurrency × cache condition before treating p99 as a stable empirical estimate; that yields only about 100 observations in the slowest 1%, so use more samples when tail-risk confidence matters. This is guidance, not a guarantee of statistical confidence. Preserve raw observations and report the sample count. Run at least three independent trials, randomize or interleave candidate order where practical, and report run-to-run variability; do not select only the best run.

### 6.7 Hardware and configuration manifest

Record this for every run:

```text
Run ID:
Date/time and region:
Engine and exact version:
Connector/driver version:
Deployment mode: local / self-managed cluster / managed service
Node count and per-node CPU/RAM:
Storage type and capacity:
Network/zone/region:
Resource limits and workload groups:
Dataset rows/bytes and generator seed:
Table schema, partition/sort/index design:
Materialized views / rollups / projections:
Ingestion rate and concurrent load:
Query-set revision and parameters:
Cache state and warm-up procedure:
Concurrency and arrival model:
Measurement duration and sample counts:
Background tasks (merges, compaction, refresh, optimize):
Failure/retry policy:
Cost basis and billing assumptions:
```

### 6.8 Load time, storage, and freshness

- **Load time:** record source-to-queryable time, not only bulk insert duration. Include index building, compaction, segment publication, MV refresh, and catch-up.
- **Storage:** include base data, indexes, replicas, aggregate tables, metadata, temporary/staging data, and any source copy needed by the serving layer.
- **Freshness:** produce events with known timestamps, then measure when queries can see them. Report p50/p95/p99 delay and lag during peak ingest.
- **Ingestion overhead:** compare ingest throughput and CPU with and without serving indexes/pre-aggregation where possible.
- **Recovery:** test restart, consumer lag catch-up, failed refresh, and backfill behavior at least for finalists. Repeat important runs and report median plus run-to-run spread; randomize candidate order where practical to reduce time-of-day and thermal/resource drift.

### 6.9 Controlled experiment versus production

A controlled benchmark gives comparative evidence under the tested conditions. It does not prove production behavior when workload distribution, network, tenancy, failure, growth, or operations differ. Run a canary or limited production trial before a high-risk migration when possible. Clearly label all results as one of:

- Measured in this controlled environment.
- Measured in a production-like staging environment.
- Published third-party result.
- Vendor-reported claim.
- Hypothesis / untested assumption.

---

## 7. Benchmark execution plan

### 7.1 Candidate set required by the roadmap

The full comparison includes:

- ClickHouse.
- Trino over Iceberg/lake data.
- At least one of Druid, Pinot, or StarRocks where feasible.
- DuckDB or a warehouse trial as baseline.

For a practical first pass, use ClickHouse + Trino/Iceberg + DuckDB, then add Pinot or StarRocks for the user-facing/real-time candidate. Druid can be substituted when ingestion-time roll-up and time-oriented dimensional queries are central. DuckDB is a useful single-node SQL/semantics baseline, not a proxy for the availability, concurrency, operational model, or pricing of a managed distributed warehouse; run an actual warehouse trial when those properties are part of the decision. Do not run all heavy clusters simultaneously on a small workstation.

### 7.2 Smoke test before 100 million rows

Begin with a 100,000–1,000,000 row dataset, 2–4 representative queries, and one engine at a time. This checks schema mappings, SQL equivalence, connector correctness, and lab scripts—not performance at scale.

Suggested staged progression:

| Stage | Data size | Engines | Goal |
|---|---:|---|---|
| 0: SQL smoke test | 10k–100k rows | DuckDB + ClickHouse | Validate semantics and query outputs |
| 1: Local comparison | 1M rows | DuckDB + ClickHouse; Trino if resources allow | Validate harness and basic measurement |
| 2: Multi-engine | 5M–20M rows | ClickHouse + Trino + one of Pinot/Druid/StarRocks | Find major plan/data-layout issues |
| 3: Scale test | 100M+ rows | Selected finalists, preferably isolated runs | Measure realistic load, query, and storage behavior |
| 4: Failure/freshness test | Based on chosen scale | Finalists | Concurrent ingestion, late data, node/task failure, catch-up |

Resource requirements depend on schema, compression, index choices, replicas, and concurrency. A laptop may run the smoke test but be unsuitable for a meaningful 100M-row comparison across several distributed engines. Estimate disk for multiple copies plus indexes/temporary data; use one heavy engine at a time and stop containers between runs. Never claim that a laptop benchmark predicts production cluster capacity.

### 7.3 Shared workspace

Use the roadmap's `olap_lab/` layout and add the decision experiment:

```text
olap_lab/
├── docker-compose.yml
├── generator/
├── sql/
│   ├── common/
│   ├── clickhouse/
│   ├── trino/
│   ├── duckdb/
│   └── candidate-engine/
├── bench/
│   ├── run_queries.py
│   ├── workload.yaml
│   └── summarize_results.py
├── results/
│   ├── raw/
│   ├── summary.csv
│   └── notes.md
├── experiments/
│   └── 06_choosing_engine/
│       ├── requirements.md
│       ├── benchmark-plan.md
│       ├── comparison-matrix.csv
│       ├── cost-model.csv
│       └── adr.md
└── tests/
    ├── test_query_equivalence.py
    └── test_result_checksums.py
```

The SQL harness should store each query in a canonical logical form plus an engine-specific implementation when syntax differs. Test result equivalence before benchmarking.

### 7.4 Example result schema

Use one row per engine × query × concurrency × cache condition × run:

```csv
run_id,engine,version,query_id,concurrency,cache_mode,iterations,successes,errors,p50_ms,p95_ms,p99_ms,completed_qps,load_seconds,storage_gib,freshness_p95_seconds,ingest_rows_per_second,monthly_cost_estimate,notes
```

Leave measurements blank until observed. Do not insert guessed numbers to make the table appear complete.

### 7.5 How to compute and compare metrics

If \(N\) successful queries complete over \(T\) seconds:

\[
QPS = \frac{N_{\text{successful}}}{T_{\text{measurement}}}
\]

Also report offered request rate and failure rate. If 1,000 requests were offered and 850 completed successfully, reporting only successful QPS hides overload. Define:

\[
\text{failure rate} = \frac{\text{failed or timed-out requests}}{\text{offered requests}}
\]

State how retries are counted. Prefer counting each offered logical request once in the failure-rate denominator and separately reporting attempt-level retries; otherwise retries can inflate offered load or hide user-visible failures. Measure QPS over a stated steady-state interval, not the entire run if it includes warm-up.

For a query latency improvement:

\[
\text{latency reduction} = \frac{L_{\text{baseline}} - L_{\text{candidate}}}{L_{\text{baseline}}}\times100\%
\]

Only compare like-for-like percentiles, query semantics, cache conditions, and concurrency. A 40% p50 improvement does not establish a p99 improvement or an end-to-end response improvement.

For a measured candidate, summarize by query and load level. Do not combine Q1 and Q9 with equal weight unless production traffic gives them equal weight.

### 7.6 Inspect plans and bottlenecks

For each finalist:

- Read the plan (`EXPLAIN`, and runtime analysis where available).
- Confirm predicate and projection pushdown for Trino.
- Inspect rows/bytes read and partition/segment pruning.
- Inspect ClickHouse sorting key/projection/MV usage.
- Inspect Druid roll-up and segment/query granularity assumptions.
- Inspect Pinot indexes/star-tree eligibility.
- Inspect StarRocks/Doris join distribution, MV rewrite, and refresh state.
- Record spill, memory pressure, queueing, compaction, ingestion lag, and background refresh.
- Repeat after changing one physical design choice.

A benchmark is most useful when it explains *why* a candidate performed as measured, not only which number was smallest.

---

## 8. Public benchmark interpretation

Public benchmarks can inform hypotheses and help detect poor configurations. They cannot choose an engine for your product without workload-specific validation.

### 8.1 ClickBench

ClickBench is a public analytical benchmark centered on a dataset and query set representative of click/event analytics. It can help compare analytical scan/aggregation behavior when data, query semantics, configurations, and measurement procedures are aligned. It does not automatically represent multi-tenant API QPS, correction handling, streaming freshness, join-heavy workloads, or your cost model.

Use it to ask: “Can this engine execute a common event-analytics workload competitively?” Do not infer: “This engine will meet my p99 at 100 clients with Kafka ingest and a 30-day retention policy.”

### 8.2 Star Schema Benchmark (SSB)

SSB uses a star-schema analytical workload and is useful for studying dimensional-model query performance, scans, joins, and aggregations. Results depend on scale factor, data layout, compression, and query implementation. It is more informative for dimensional analytical queries than for a personalized high-QPS serving API unless adapted to that workload.

### 8.3 TPC-H

TPC-H is a decision-support benchmark with business-oriented ad hoc queries and data. It can illuminate scan, join, aggregation, and optimizer behavior. TPC-H results are not a direct forecast of event-serving latency, streaming freshness, or multi-tenant QPS. Use official current specifications and distinguish audited results from non-compliant experiments.

### 8.4 TPC-DS

TPC-DS has a broader and more complex decision-support query workload, including varied query shapes. It can test warehouse/optimizer breadth and complex analytical SQL. It does not, by itself, measure event ingestion freshness, dashboard request distributions, or operational burden.

The TPC publishes versioned specifications and rules for consistent/fair benchmark reporting. Use its current specification when running a TPC benchmark, and do not label a subset or modified run as an official TPC result.

### 8.5 Why public results disagree

Benchmark rankings may change because of:

- Hardware, CPU generation, RAM, storage, network, and cloud region.
- Engine version, settings, table layout, sort/partition keys, indexes, and materialized views.
- Dataset scale, skew, cardinality, compression, and query semantics.
- Cold versus warm caches and result-cache behavior.
- Single-query latency versus concurrent throughput.
- Ingestion running or paused, background merges/compaction, and refresh tasks.
- Whether all costs, replicas, and storage are included.
- Whether queries are semantically equivalent and whether results are exact.
- Vendor tuning expertise and whether the workload matches the product's sweet spot.

Use published numbers as evidence about the tested setup, not as a substitute for your benchmark.

---

## 9. Total cost of ownership (TCO)

A fast engine can be the wrong choice if the workload does not need that speed or if the required cluster and expertise cost more than the benefit. TCO includes more than a node price.

### 9.1 Cost categories

| Category | Include |
|---|---|
| Compute | Query nodes, ingestion nodes, coordinators, control plane, warehouse credits/slots, idle capacity, autoscaling headroom |
| Storage | Base data, replicas, indexes, projections, rollups, metadata, backups, snapshots, staging |
| Ingestion and transformation | Kafka/stream processing, connectors, batch pipelines, schema evolution, deduplication, CDC, retries |
| Refresh/pre-aggregation | MV refresh compute, incremental maintenance, rollup/index construction, rebuild/backfill |
| Availability | Replicas, multi-zone/regional deployment, standby capacity, disaster recovery |
| Managed service | Service fees, support tier, control plane, minimum spend, network charges |
| Operations | On-call staffing, upgrades, capacity planning, tuning, incident response, security patching |
| Observability | Metrics, logs, traces, alerting, query audit and cost monitoring |
| Data movement | Egress, cross-region traffic, lake-to-serving copies, repeated reads from external sources |
| Migration/exit | SQL rewrites, schema conversion, re-ingestion, parallel run, validation, rollback, vendor-specific dependencies |
| Risk reserve | Growth, peak traffic, price changes, unexpected compaction/refresh, support needs |

### 9.2 Monthly cost model

A recurring monthly model is:

\[
\begin{aligned}
C_{\text{month, recurring}} ={}& C_{\text{compute}} + C_{\text{storage}} + C_{\text{ingest}} + C_{\text{network}} \\
&+ C_{\text{managed}} + C_{\text{ops}} + C_{\text{refresh}} + C_{\text{backup}} + C_{\text{observability}} \\
C_{\text{month, evaluated}} ={}& C_{\text{month, recurring}} + \frac{C_{\text{one-time migration/backfill}}}{H}
\end{aligned}
\]

For a self-managed system, operational labor is a real cost even when it does not appear on a cloud invoice. Use loaded staff cost or person-hours × internal rate consistently. Avoid double-counting operations already included in a managed-service price. In the evaluated monthly cost, amortize one-time migration/backfill costs over an explicitly chosen comparison horizon H (in months), and report the unamortized one-time amount separately. Do not mix a one-time cost with recurring monthly charges without labeling the horizon. Include observability explicitly unless it is already included in another line item.

**Illustrative arithmetic only:** suppose candidate A has $2,400/month compute, $600 storage, $500 ingestion/network, $1,000 managed/support, $1,500 operations, $300 refresh compute, $100 backup, and $200 observability. Its modeled recurring total is:

\[
2{,}400 + 600 + 500 + 1{,}000 + 1{,}500 + 300 + 100 + 200 = \$6{,}600/\text{month}
\]

This is not a quote or observed cost. It assumes the line items are mutually exclusive and does not yet include amortized migration/backfill cost; add that term for the evaluated monthly comparison. Replace every component with measured usage, vendor quotes, and documented staffing assumptions. For a self-managed alternative, include the cost of reliable on-call coverage and failure recovery rather than assigning operations a value of zero.

### 9.3 Compare cost per useful workload

Useful normalized metrics can include:

- Monthly cost at required SLO and traffic.
- Cost per million successful queries at the required latency/freshness, calculated as `evaluated monthly cost / (successful queries in the same month / 1,000,000)`. Count only requests that meet the required latency and correctness gates in the numerator's workload denominator; state how retries are treated.
- Cost per TB retained (including replicas/indexes/backups).
- Cost per million ingested events.
- Operations hours per month.
- Cost of a full historical backfill.
- Cost during peak versus average demand.

A low cost per query is meaningless if the engine fails the freshness or correctness gate. Compare cost only among candidates that meet mandatory requirements.

### 9.4 Hybrid architecture cost

A hybrid serving layer can reduce dashboard latency but adds:

- A second copy of data.
- Streaming/batch pipeline and retry logic.
- Reconciliation and backfill jobs.
- Schema and metric-definition governance across systems.
- Additional monitoring, on-call, access control, and disaster recovery.
- Egress or cross-zone transfer.
- A migration path for both serving data and application queries.

The hybrid architecture is justified when measurable SLO, scale, isolation, or cost requirements cannot be met adequately by a simpler architecture.

---

## 10. Freshness, serving layers, caching, and semantic architecture

### 10.1 Three different data times

Do not conflate:

1. **Source event time:** when the business event occurred.
2. **Ingestion/processing time:** when the pipeline received and processed it.
3. **Query-visible time:** when the selected engine can return it to a query.

For streaming data, the end-to-end freshness delay includes producer buffering, network, Kafka retention/consumer lag, transformation, index/segment publication, MV refresh, and cache invalidation. Measure visibility at the serving endpoint, not just Kafka consumer lag.

### 10.2 Freshness versus latency

A batch warehouse may be inexpensive and fast enough for a dashboard refreshed every 15 minutes. A real-time serving engine may be necessary for seconds-old data. But streaming ingestion can compete with query resources and create backpressure; a faster query engine does not automatically create fresher data.

Define both:
- Query SLO: e.g., p95 database latency ≤ 150 ms.
- Freshness SLO: e.g., p95 event visibility delay ≤ 5 seconds.

A candidate must meet both at the expected concurrent ingest and query load.

### 10.3 Canonical source of truth plus serving layer

A common hybrid design is:

```text
Applications / event producers
          │
          ▼
      Kafka / CDC
          │
          ├──────────────► Raw lakehouse (e.g., Iceberg) / warehouse
          │                         │
          │                         ├── historical truth, audit, backfills
          │                         └── ad hoc SQL via Trino/warehouse
          │
          ▼
   Stream processing / canonicalization
          │
          ▼
 OLAP serving store (ClickHouse / Pinot / Druid / StarRocks/Doris)
          │
          ▼
 API + authorization + semantic/metric layer + optional cache
          │
          ▼
       Dashboard
```

The lakehouse/warehouse can retain canonical history while the OLAP store is optimized for hot query patterns. This separation is useful only if ownership is clear: which system defines current truth, how corrections propagate, how aggregates are reconciled, and how serving data is rebuilt.

### 10.4 Pre-aggregation and materialized views

Pre-aggregation is useful when a known query family repeatedly computes the same group-bys. It can reduce rows scanned and work per request, but adds storage, ingestion/refresh compute, and correction complexity. Use the prior lesson to verify aggregate semantics, state merging, late-event handling, and reconciliation.

Do not roll up away dimensions that the dashboard may need later. Do not assume a distinct count can be summed. Do not assume all engines automatically rewrite a query to use an MV. Confirm the plan and freshness behavior.

### 10.5 Cache versus aggregate store

| Mechanism | Best use | Main concern |
|---|---|---|
| Database result cache | Repeated identical queries | Cache key, invalidation, freshness, cache hit ratio |
| Redis/application cache | Hot key-value responses or per-tenant results | Invalidation, authorization, hot keys, duplicated business logic |
| CDN | Public/shared HTTP responses | Stale content and leakage of personalized data |
| Materialized view/aggregate table | Many related queries sharing an aggregate | Refresh, storage, correction semantics, query rewrite |
| Serving OLAP engine | Fresh, low-latency analytical query family | Duplicate data, operations, reconciliation |

Cache correctness must include tenant and authorization context. A cache hit that returns one tenant's result to another tenant is a security failure, not a performance issue.

### 10.6 Semantic layer

A semantic layer defines shared metrics and dimensions—e.g., “active user,” “net revenue,” “conversion”—independently of each dashboard. It reduces the risk of the warehouse and serving layer implementing different metric logic. It can live in BI tooling, a semantic service, or governed query models; the exact product is secondary to consistent definitions and tests.

Define:
- Metric formula and grain.
- Allowed dimensions and filters.
- Timezone/calendar policy.
- Null, duplicate, refund, and late-data policy.
- Exact versus approximate distinct behavior.
- Freshness expectation and owner.

### 10.7 Reverse ETL

Reverse ETL is relevant when curated analytical data must be sent from the warehouse/lakehouse to operational systems such as CRM, support, or customer-success tools. It is not a substitute for a low-latency OLAP serving store. Use it when the output is an operational attribute or action, not when the product needs interactive multidimensional analytics. Account for propagation delay, retries, idempotency, and stale downstream fields.

### 10.8 When not to build a hybrid

Avoid a separate serving layer when:
- The warehouse already meets latency/freshness/cost SLOs.
- Query volume is low and caching solves the repeated-request problem.
- The workload is exploratory and dimensions change frequently.
- The team cannot operate another distributed system safely.
- Correction and reconciliation requirements cannot be implemented reliably.
- The business value of the latency improvement is lower than duplicated storage and operations cost.

---

## 11. Operational and strategic risks

### 11.1 Maturity, community, hiring, managed options

Evaluate product maturity in terms of release stability, upgrade guidance, incident history, documentation quality, issue response, security fixes, and the ability to hire/retain operators. A large community is useful but does not guarantee a fit for your workload. A smaller product may still be appropriate if the managed service, support contract, and team expertise reduce risk.

Compare self-managed and managed options on the same SLO:
- Who handles node failure, upgrades, backups, scaling, and patching?
- Are support response times contractual?
- Can you inspect query plans and control configuration?
- Are there limits on storage, concurrency, connectors, or query features?
- What happens to cost during backfills and bursts?

### 11.2 Multi-tenant isolation

For customer-facing analytics, ask:

- Can resource groups/workload groups isolate tenants or query classes?
- Can one large tenant saturate memory, CPU, storage bandwidth, or ingestion?
- Are quotas and per-tenant observability available?
- Can authorization filters be enforced centrally?
- Do caches include tenant and policy context?
- Can noisy tenants be throttled without impacting all customers?
- Does a tenant deletion propagate to raw, serving, aggregate, cache, and backup layers?

A single throughput figure at 100 identical clients does not establish isolation. Test a skewed scenario where one tenant issues expensive queries while many smaller tenants issue normal dashboard traffic.

### 11.3 Upgrade and failure modes

Document how the system behaves during:
- Node or availability-zone failure.
- Kafka backlog or source outage.
- Disk exhaustion or memory pressure.
- Background merge/compaction/index rebuild.
- MV refresh failure or stale materialized data.
- Schema evolution and incompatible type changes.
- Network partition between query engine and object storage.
- Failed backfill or duplicate replay.
- Certificate/credential rotation and permission changes.

Run a small failure drill for finalists. Recovery time and the operator's ability to diagnose a failure are part of suitability.

### 11.4 Lock-in, Iceberg, and standard SQL

Open table formats such as Iceberg can make the **data layer** more portable by separating table metadata/data from a single query engine. Standard SQL helps, but does not guarantee portability:

- SQL functions, timestamp semantics, approximate aggregates, MV behavior, update semantics, and optimizer features differ.
- Indexes, projections, star-tree indexes, rollups, and physical layouts are engine-specific.
- Managed services can use proprietary metadata, APIs, security, streaming integrations, and billing models.
- Migration may require re-ingestion, query rewrites, dual running, result reconciliation, and retraining.

A practical exit plan should preserve raw/canonical data in open formats where feasible, version SQL and schemas, automate query equivalence tests, export configuration, and estimate the time/cost of rebuilding serving structures elsewhere.

### 11.5 Avoid novelty bias

Do not select the newest engine because it is fashionable. Prefer the simplest architecture that meets the hard requirements with acceptable TCO and a credible operations plan. A well-understood warehouse can beat a specialized OLAP store when the workload is moderate and freshness requirements are relaxed.

---

## 12. Worked case studies

The recommendations below are **conditional hypotheses** based on stated assumptions, not measured winners. The correct next step is to validate each against the benchmark and acceptance criteria. The roadmap requires four case-study domains (product analytics, observability, ad-tech reporting, and fintech risk); the three requirement sheets above remain the required initial planning deliverables.

### 12.1 Case study A — product analytics

**Workload assumptions**

- Hundreds of millions of events per day, with growth forecast documented.
- Dashboard queries include event counts, time series, country/device/page breakdowns, cohorts, and distinct users.
- New events should appear within seconds.
- A customer-facing API has high concurrency and strict p95/p99 targets.
- Late and duplicate events occur; raw history is needed for audits and backfills.

**Candidates**

- ClickHouse: strong initial candidate for event scans and aggregations.
- Pinot or Druid: strong candidates if stable dimensional queries, high QPS, and streaming freshness dominate.
- StarRocks/Doris: include if multi-table joins and mutable analytical tables dominate.
- Warehouse + cache: baseline to prove whether specialized serving is actually necessary.
- Trino: useful for historical lakehouse exploration, not assumed to be the serving layer for the tightest SLO.

**Initial architecture hypothesis**

Kafka → canonicalization/deduplication → raw Iceberg/warehouse history plus ClickHouse serving tables with measured rollups → API/semantic layer → optional tenant-safe cache. Trino serves cross-source historical analysis.

**Acceptance criteria (illustrative)**

- Query p95/p99 at concurrency 1/10/100 meet API budget.
- p95 visibility delay meets seconds-level freshness SLO under peak ingest.
- Exact additive metrics reconcile; distinct metrics use documented exact/approximate semantics.
- Duplicate/correction replay is idempotent or triggers bounded rebuild.
- Monthly TCO remains below the approved ceiling.
- Tenant isolation, access controls, and backfill recovery pass tests.

**Risks**

- Duplicate/correction drift in insert-trigger aggregates.
- High-cardinality dimensions inflate storage.
- Serving/lake metrics diverge.
- Hot tenants or queries cause p99 regressions.
- Cache invalidation hides fresh data.

**What would change the decision?**

If query patterns are highly dimensional and predictable at very high QPS, Pinot/Druid may outperform the simpler ClickHouse design for the actual workload. If joins become dominant, StarRocks/Doris may be preferable. If the warehouse meets SLO at lower total cost, avoid the extra serving layer.

### 12.2 Case study B — observability and log analytics

**Workload assumptions**

- High-volume append-heavy logs/events, service and host dimensions, time filters, top-N errors, and time series.
- Retention has hot/warm/cold tiers.
- During incidents, query concurrency and burstiness rise sharply.
- Some workloads need text search or trace correlation beyond aggregate SQL.

**Candidates**

- ClickHouse for scan-heavy event/log analytics.
- Druid/Pinot for dimensional metric dashboards with streaming ingestion and stable query patterns.
- Existing specialized observability platform if text search, tracing UX, alerting, and integrations dominate.
- Warehouse/Trino for historical investigations, not assumed to replace the operational hot path.

**Initial architecture hypothesis**

Stream logs to canonical object storage and a ClickHouse hot serving tier; use retention/TTL and tiered storage. Keep raw history for investigation/replay. If full-text search and traces are first-class requirements, benchmark the existing observability stack rather than choosing only from the OLAP list.

**Acceptance criteria**

- Ingest rate sustained during burst without unbounded backlog.
- p95 freshness remains within operational target.
- p99 query latency meets incident-response budget at 1/10/100 clients.
- Storage per retained day and compression measured.
- Cardinality stress test and long-range query measured.
- Failure/recovery and retention deletion tested.

**Risks**

- Label cardinality explosion and index/storage growth.
- Ingestion competes with query resources.
- Compaction/merge activity creates latency spikes.
- Long retention increases scan cost.
- Text search requirements are underestimated.

**What would change the decision?**

If the key queries are rollup-oriented and time-dimensional, Druid deserves a focused benchmark. If the workload is mostly pre-defined high-QPS dimensional metrics, Pinot is also plausible. If full-text and tracing operations dominate, a specialized platform may be more suitable than forcing an OLAP engine to serve every function.

### 12.3 Case study C — ad-tech reporting

**Workload assumptions**

- Impression, click, conversion, and attribution events.
- High cardinality across campaign, advertiser, placement, device, region, and time.
- Late conversions and deduplication are common.
- Dashboards require high concurrency and aggregation over large time windows.
- Billing/reconciliation metrics may require exactness.

**Candidates**

- ClickHouse for fast scans and flexible aggregation.
- Druid/Pinot for predictable high-QPS dimensional dashboards.
- StarRocks/Doris if campaign, advertiser, and dimension joins are frequent.
- Warehouse/lakehouse for canonical attribution history, audit, and backfills.

**Initial architecture hypothesis**

Keep canonical immutable event history and attribution results in a governed warehouse/lakehouse; serve hot dashboard queries from a selected OLAP engine. Build only the aggregates justified by the ten-query workload. Recompute affected attribution windows when late conversions alter earlier results.

**Acceptance criteria**

- Exact billing/revenue metrics reconcile to canonical attribution output.
- Late conversions propagate within a defined correction SLA.
- Distinct users/clicks are not summed incorrectly across buckets.
- p95/p99 and QPS targets are met under ingest plus query load.
- Reprocessing a window is idempotent and does not double count.
- Cost model includes stream processing, serving storage, refresh, and historical backfill.

**Risks**

- Approximate metrics accidentally used for billing.
- Late attribution causes stale rollups.
- High-cardinality dimensions create storage blowup.
- Serving metrics drift from audited reporting.
- Query speed is optimized at the expense of correctness.

**What would change the decision?**

Join-heavy reporting may favor StarRocks/Doris. A highly stable dimension/query model and very high QPS may favor Druid/Pinot. If most reports are scheduled and freshness is relaxed, a warehouse alone may be sufficient.

### 12.4 Case study D — fintech risk dashboards

**Workload assumptions**

- Near-real-time event and risk slices, strict auditability, sensitive access controls, and corrections.
- Some metrics may be decision-critical and require exact values.
- The serving dashboard is not necessarily the transactional decision system itself.

**Candidates**

- ClickHouse or StarRocks/Doris for a low-latency analytical serving layer, subject to correctness and security tests.
- Pinot/Druid only if query patterns and mutation semantics fit.
- Warehouse/lakehouse as governed historical record.
- PostgreSQL or another OLTP system for transactional risk state where appropriate; do not use an OLAP database as a transactional system by assumption.

**Initial architecture hypothesis**

Keep canonical decisions/events and audit history in the governed source-of-truth platform; serve analytical dashboards from a separately monitored OLAP layer. Separate exact decision-critical metrics from approximate exploratory metrics. Include access-control and deletion propagation tests.

**Acceptance criteria**

- Exact measures reconcile to canonical records.
- p99 and freshness targets meet risk-operations SLO.
- Row-level/tenant-level access control is enforced and audited.
- Corrections, retries, and replays do not silently double count.
- Recovery and rollback are demonstrated.

**Risks**

- Treating an eventually consistent aggregate as a transactional truth.
- Approximation leaking into a regulated metric.
- Cross-tenant or cross-role data exposure through caches.
- Unclear audit lineage or incomplete deletion handling.

**What would change the decision?**

If the workload becomes transactional, move that part to an OLTP system. If complex joins dominate, test StarRocks/Doris. If the risk dashboard is low-volume and the warehouse already meets the SLA, avoid a separate serving engine.

---

## 13. Scoring model: use only after hard gates

A score can make trade-offs explicit, but weights are subjective and must not conceal a failed hard requirement.

### 13.1 Example scoring rubric

First mark each hard gate as pass/fail. Only candidates that pass all mandatory gates are eligible for scoring.

Example preference weights (illustrative):
- Latency/throughput: 30%
- Freshness: 15%
- TCO: 20%
- Query capability: 10%
- Operations/team fit: 15%
- Portability/exit: 10%

Score each criterion from 1 (poor) to 5 (excellent), based on benchmark evidence and documented judgment. To map the full 1–5 scale onto 0–1, normalize as `(score - 1) / 4`; a score of 1 contributes zero and a score of 5 contributes the full criterion weight.

\[
\text{weighted score} = \sum_i w_i \times \frac{s_i - 1}{4}
\]

where weights \(w_i\) sum to 1 and \(s_i\) is the 1–5 score. Scores must be based on measured evidence or explicitly labeled qualitative judgment; mark untested criteria as unknown rather than silently imputing a midpoint. If any hard gate fails or is unknown, do not use the weighted score to declare a winner.

**Illustrative arithmetic:** candidate X scores 4/5 for latency and the latency weight is 0.30. Under the stated 0–1 normalization, the contribution is `0.30 × (4 - 1)/4 = 0.225`. This is arithmetic only, not an engine result. Repeat for each criterion and sum. Do not assign a score based on vendor claims when the required benchmark has not been run; label it “hypothesis” or “unknown.”

A transparent decision can also be a qualitative trade-off instead of a numeric score. If scoring creates false precision, use a pass/fail gate table and written rationale.

### 13.2 Blank candidate matrix

| Candidate | Hard gates pass? | p95/p99 at 1/10/100 | Freshness p95/p99 | Throughput/errors | Load time | Storage | Monthly TCO | Ops fit | Main risk |
|---|---|---|---|---|---|---|---|---|---|
| Warehouse | | | | | | | | | |
| ClickHouse | | | | | | | | | |
| Druid | | | | | | | | | |
| Pinot | | | | | | | | | |
| StarRocks/Doris | | | | | | | | | |
| Trino/Iceberg | | | | | | | | | |
| DuckDB baseline | | | | | | | | | |

Use “not measured” rather than filling blank cells with estimates. If a candidate was excluded before benchmarking, record the reason and the requirement it failed.

---

## 14. Architecture Decision Record (ADR)

An ADR captures why a decision was made, the evidence and assumptions behind it, and what would make the team revisit it. It should be understandable to a skeptical reviewer who did not attend the design meeting.

### 14.1 ADR template

```markdown
# ADR-NNN: Select an OLAP serving architecture

- Status: Proposed / Accepted / Superseded
- Date:
- Owners:
- Reviewers:

## Context and business problem
What dashboard/product problem are we solving? What is the cost of not solving it?

## Workload and SLOs
- Query mix and data volume/growth:
- p50/p95/p99 latency:
- QPS/concurrency:
- Freshness:
- Correctness/exactness:
- Availability, RPO/RTO, tenancy/security:
- Budget:

## Hard acceptance gates
List each gate, how it is measured, and pass/fail evidence.

## Candidates considered
Include the warehouse, ClickHouse, Druid/Pinot, StarRocks/Doris, Trino, DuckDB, or PostgreSQL only where relevant.

## Hypotheses
For each candidate, state what you expect to be strong/weak and why.

## Benchmark methodology
Dataset, query set, cache conditions, concurrency, hardware, versions, run count, load profile, and limitations.

## Evidence
Link raw results, query plans, storage measurements, freshness results, and cost model.
Clearly separate measured values from assumptions.

## Decision
Chosen engine/architecture and why it passes the hard gates.

## Alternatives rejected
Why each was rejected and what trade-off would justify reconsidering it.

## Consequences
Benefits, costs, operational responsibilities, and limitations.

## Risks and mitigations
Include ingestion, freshness, correction, isolation, availability, security, and vendor risks.

## Cost assumptions
Monthly compute, storage, ingestion, managed fees, egress, staffing, refresh, backup, and migration.

## Migration and exit plan
Data formats, query portability, backfill, validation, parallel run, rollback, and estimated exit effort.

## Reconsideration triggers
Specify measurable triggers such as p99 SLO breach, freshness breach, cost threshold, growth, join mix change, or operational incidents.
```

### 14.2 Completed example ADR (hypothetical)

This ADR is **illustrative and intentionally conditional**. It is not based on a benchmark run in this authoring session.

# ADR-006: Customer-facing product analytics serving layer

- **Status:** Proposed pending benchmark
- **Context:** Product analytics queries are generated by customer-facing dashboard interactions. The existing warehouse is the canonical historical source but may not meet the proposed seconds-level freshness and tail-latency targets under peak concurrency.
- **Workload:** Event counts, time series, country/device/page breakdowns, top-N, distinct users, and selected dimension joins. Late and duplicate events occur.
- **Illustrative hard gates:** database p95 ≤ 150 ms and p99 ≤ 400 ms at 100 clients; event visibility p95 ≤ 5 seconds during peak ingest; exact additive measures reconcile; corrections are handled within 2 minutes; monthly TCO ≤ approved budget.
- **Candidates:** warehouse, ClickHouse, Pinot, Druid, StarRocks/Doris, Trino/Iceberg, DuckDB baseline.
- **Hypothesis:** ClickHouse is the first serving candidate because the query mix is event-scan and aggregation heavy. Pinot/Druid are included if high-QPS dimensional query patterns dominate. StarRocks/Doris are included if multi-table joins are more common than the initial workload suggests. Trino remains the lake federation path rather than the assumed hot serving engine. DuckDB validates query semantics on a small dataset.
- **Evidence:** No production benchmark has been run for this example. The decision is not accepted until the ten-query workload, concurrency tests, freshness, correction/reconciliation, and TCO matrix are completed.
- **Decision:** Provisionally evaluate ClickHouse as the primary serving candidate while retaining the warehouse/lakehouse as source of truth. Do not migrate production traffic until it passes every hard gate. If it fails, compare the measured evidence with Pinot/Druid/StarRocks/Doris and the warehouse baseline.
- **Alternatives rejected for initial serving role:** Trino is not assumed to satisfy strict high-QPS low-latency serving over remote lake data without proof; DuckDB is a baseline rather than a multi-tenant HA serving architecture; warehouse-only remains viable if it passes all gates at lower TCO.
- **Consequences:** A second data copy and reconciliation/backfill pipeline are required. The team owns serving-schema evolution, ingestion lag, correction handling, capacity, access control, and cache invalidation.
- **Risks and mitigations:** Duplicate/correction drift → canonicalization and rebuild path; noisy tenants → resource isolation and per-tenant monitoring; stale data → freshness SLO and lag alert; cost growth → monthly usage review and retention policy; lock-in → preserve canonical data in open formats and test export/rebuild.
- **Migration/exit:** Keep canonical raw history in Iceberg/warehouse, version SQL and schemas, automate result checksums, run parallel traffic before cutover, retain rollback path, and periodically estimate rebuild effort for an alternate engine.
- **Reconsider if:** p99 breaches for two consecutive review windows, p95 freshness exceeds 5 seconds during normal peak, monthly cost exceeds the approved ceiling by 20%, join-heavy queries become more than half the workload, or operations cannot meet recovery objectives.

**Important:** this example is a decision process, not a recommendation to deploy ClickHouse without testing. The actual decision follows measured results.

---

## 15. Hands-on lab — `experiments/06_choosing_engine/`

### 15.1 Deliverables

Complete the following artifacts:

```text
experiments/06_choosing_engine/
├── requirements.md
├── benchmark-plan.md
├── query-set.md
├── comparison-matrix.csv
├── cost-model.csv
├── adr.md
├── results/
│   ├── raw/
│   └── summary.csv
└── notes.md
```

### 15.2 Step 1 — Requirements

Write three requirements sheets:
1. Internal executive dashboard.
2. Customer-facing usage dashboard.
3. Log analytics.

For each, specify the data size/growth, ten-query mix, p50/p95/p99 targets, concurrency, QPS, freshness, corrections, retention, availability, security, monthly budget, and team skill constraints. Mark each requirement hard or preferred.

### 15.3 Step 2 — Hypotheses

Before running tests, write one hypothesis per candidate. Example:

- ClickHouse: expected to do well on scan/aggregation queries; validate joins, correction path, and concurrency under ingest.
- Trino/Iceberg: expected to work well for federation and historical queries; validate pushdown, file layout, data movement, and tail latency.
- Pinot or Druid: expected to suit streaming dimensional queries; validate actual query mix, indexing/roll-up costs, and operational burden.
- StarRocks/Doris: expected to be competitive for join-heavy real-time OLAP; validate join plans, refresh/update semantics, and cost.
- DuckDB: expected to be a convenient single-node baseline; not assumed to satisfy multi-tenant availability or 100-client service requirements.
- Warehouse: expected to be strong for BI/ELT and ad hoc SQL; validate interactive SLO and cost.

### 15.4 Step 3 — Dataset and seed

Use the same generated event records across candidates. The logical schema can include:

```text
event_id, event_time_utc, ingest_time_utc, tenant_id, user_id,
event_name, country, device, page, service, status_code, revenue,
dimension_id, correction_version
```

Keep the event generator seed fixed for reproducibility. Generate:
- Common and rare tenants (skew).
- High and low cardinality dimensions.
- Duplicate deliveries and late events.
- Null/unknown dimension values.
- A known correction rate.
- A stable time distribution and retention range.

Use the same canonical data for query equivalence. If an engine cannot implement the same update semantics directly, document the alternate pipeline and include its cost and freshness in the comparison.

### 15.5 Step 4 — Smoke-test procedure

1. Start DuckDB and ClickHouse; add Trino only after the first two return equivalent results.
2. Load 10k–100k rows and execute Q1–Q4 plus Q5 exact distinct.
3. Compare result rows/checksums and verify timezone/null semantics.
4. Add one late event, one duplicate, and one corrected record; document behavior.
5. Run a small concurrency test to validate the harness only.
6. Record all missing capabilities and errors.
7. Scale only after the SQL and data mappings are correct.

The smoke test is not evidence of 100M-row performance. Do not publish a speed ranking from it.

### 15.6 Step 5 — Full ten-query benchmark

For each candidate that remains feasible:

1. Load the same logical dataset; record load-to-queryable time.
2. Configure an engine-appropriate physical layout and document it.
3. Verify query result equivalence.
4. Run cold/first-run and warm-cache conditions separately.
5. Test 1, 10, and 100 clients with the same query mix and arrival model.
6. Run query load concurrently with ingestion for real-time candidates.
7. Capture p50/p95/p99, throughput, error rate, freshness, storage, and background work.
8. Inspect query plans and note pushdown, pruning, indexes, joins, and pre-aggregation.
9. Repeat with one physical design change at a time.
10. Estimate monthly cost at expected average and peak traffic.
11. Record missing measurements rather than substituting guesses.

If the local environment cannot support all engines, report a partial benchmark. A defensible partial comparison is better than a fabricated full matrix.

### 15.7 Step 6 — Cost model

Create a row per candidate and include:

```text
monthly_query_compute
monthly_ingestion_compute
monthly_refresh_or_rollup_compute
monthly_storage_and_replicas
monthly_streaming_infrastructure
monthly_network_and_egress
monthly_managed_service_and_support
monthly_operations_person_hours
monthly_backup_and_monitoring
one_time_migration_cost
one_time_exit_or_rebuild_estimate
```

Document source of every price, utilization assumption, region, currency, and whether taxes/support are included. For hypothetical values, label them illustrative. Use vendor quotes/current pricing calculators for final estimates; do not treat a local Docker run as a managed-service price estimate.

### 15.8 Step 7 — Decision and ADR

1. Reject any candidate that fails a hard gate.
2. For remaining candidates, compare query classes, freshness, operations, TCO, security, and portability.
3. Use a weighted score only if the weights have been agreed and the evidence supports the scores.
4. Complete an ADR for each of the three workload requirements, or explicitly state where one architecture serves more than one.
5. Record rejected alternatives and what would make you wrong.
6. Define a canary/parallel-run plan, reconciliation checks, rollback, and exit strategy.
7. Set reconsideration triggers and an owner/review date.

### 15.9 Results template

| Engine | Version/config | Dataset rows | Load-to-queryable | QPS at 1/10/100 | p50/p95/p99 by query | Errors/timeouts | Freshness p95/p99 | Storage | Monthly TCO | Hard gates | Notes |
|---|---|---:|---:|---|---|---|---|---:|---:|---|---|
| ClickHouse | Not run | | | | | | | | | | |
| Trino/Iceberg | Not run | | | | | | | | | | |
| Pinot/Druid/StarRocks | Not run | | | | | | | | | | |
| DuckDB or warehouse | Not run | | | | | | | | | | |

The starter status “Not run” is intentional. Replace it only with measured evidence from your environment.

---

## 16. Troubleshooting and common mistakes

| Mistake | Why it misleads | Better practice |
|---|---|---|
| Choosing the trendiest engine | Novelty is not workload fit | Require evidence against SLOs and operations constraints |
| Using one query or one latency number | Hides query diversity, tail latency, concurrency, and freshness | Ten-query mix, percentiles, errors, concurrency, freshness |
| Benchmarking with unrealistic data | Uniform or tiny data hides skew, cardinality, and volume issues | Profile production-like distribution and scale progressively |
| Comparing cold cache with warm cache | Invalidates latency comparison | Define and run both conditions consistently |
| Ignoring ingestion during query tests | Misses resource contention and freshness regressions | Run concurrent ingestion and query workload for finalists |
| Treating 100 clients as 100 QPS | Request pacing and latency affect throughput | Specify arrival model, offered rate, in-flight concurrency, completed QPS |
| Reporting p99 from too few samples | Tail estimate is unstable | Report sample count and avoid unsupported percentile claims |
| Comparing exact and approximate answers | Changes the work being measured | Match exactness; report approximation error separately |
| Ignoring data corrections | Serving data can drift silently | Test duplicates, late data, updates/deletes, replay and reconciliation |
| Ignoring background maintenance | Merges/compaction/refresh affect latency | Record background tasks and measure under realistic conditions |
| Ignoring team/operations | A fast engine can become unreliable or expensive | Include on-call, upgrades, failure drills, support, and runbooks |
| Treating serving OLAP as source of truth | Serving copies may be delayed or corrected differently | Define canonical source, reconciliation, rebuild, and audit lineage |
| Assuming Iceberg/SQL means no lock-in | Engine-specific indexes, MVs, functions, and semantics remain | Preserve canonical data, automate portability tests, budget migration |
| Treating a vendor benchmark as a promise | Test setup may not resemble production | Reproduce workload and conditions; label vendor claims |
| Using weighted score to hide a failed gate | A high score can mask unacceptable SLO failure | Hard gates first; weighted preferences second |
| Omitting exit cost | Lock-in can become expensive during migration | Test export/rebuild and document exit strategy |

---

## 17. Final checkpoint

You are ready to complete Module 2C.7 when you can do the following without relying on a vendor ranking:

- [ ] Define a workload and write explicit SLOs for p50/p95/p99, QPS, concurrency, freshness, and correctness.
- [ ] Distinguish database latency from end-to-end response time and ingestion freshness.
- [ ] Classify internal BI, customer-facing analytics, observability, ad hoc, lakehouse federation, single-node, and operational workloads.
- [ ] Explain the initial roles of warehouse, ClickHouse, Druid, Pinot, StarRocks/Doris, Trino, DuckDB, and PostgreSQL.
- [ ] Design ten representative queries with matching semantics across candidates.
- [ ] Explain cold/warm cache tests and concurrency at 1/10/100.
- [ ] Record hardware, versions, settings, load time, storage, throughput, freshness, errors, and cost.
- [ ] Explain what ClickBench, SSB, TPC-H, and TPC-DS do—and do not—prove.
- [ ] Build a monthly TCO model that includes ingestion, refresh, operations, egress, backup, and migration/exit.
- [ ] Explain when a warehouse + OLAP serving layer + cache is justified and when it is unnecessary.
- [ ] Complete requirements sheets for the three roadmap workloads and write “what would make this wrong” for each recommendation.
- [ ] Produce an ADR with hard gates, evidence, alternatives, risks, mitigations, cost assumptions, migration/exit, and reconsideration triggers.
- [ ] State clearly which results were measured, which were published, and which remain hypotheses.

**Common mistakes to remember:** choosing the trendiest engine; benchmarking with cold cache or unrealistic queries; ignoring operational burden; and treating a serving layer as the system of record.

---

## 18. References

Use official/current documentation for version-sensitive behavior and record the version used in your benchmark.

### Project roadmap and related lessons
- `roadmap-Real-Time-OLAP-and-Query-Engines.md` — Topic 06 and the shared `olap_lab/` workflow.
- `01-clickhouse-architecture-and-mergetree.md`
- `02-apache-druid-and-apache-pinot-overview.md`
- `03-trino-and-presto-federated-queries.md`
- `04-starrocks-and-doris-overview.md`
- `05-materialized-views-and-pre-aggregation.md`
- Module 2C.8 — architecture/data-platform decisions and ADR context.
- Module 2.22 Topic 02 — caching and serving.

### Public benchmark references
- ClickBench: https://benchmark.clickhouse.com/
- Star Schema Benchmark background: https://www.cs.umb.edu/~poneil/StarSchemaB.PDF
- TPC current specifications (including TPC-H and TPC-DS): https://www.tpc.org/tpc_documents_current_versions/current_specifications5.asp

### Engine documentation
- ClickHouse documentation: https://clickhouse.com/docs
- Apache Druid documentation: https://druid.apache.org/docs/latest/
- Apache Pinot documentation: https://docs.pinot.apache.org/
- StarRocks documentation: https://docs.starrocks.io/
- Apache Doris documentation: https://doris.apache.org/docs/
- Trino documentation: https://trino.io/docs/current/
- DuckDB documentation: https://duckdb.org/docs/
- PostgreSQL documentation: https://www.postgresql.org/docs/
- Snowflake documentation: https://docs.snowflake.com/
- BigQuery documentation: https://cloud.google.com/bigquery/docs

Specific references consulted for this lesson:
- Apache Pinot introduction and user-facing analytics: https://docs.pinot.apache.org/
- StarRocks materialized-view query rewrite documentation: https://docs.starrocks.io/docs/using_starrocks/async_mv/Materialized_view/
- Trino `CREATE MATERIALIZED VIEW` and refresh semantics: https://trino.io/docs/current/sql/create-materialized-view.html
- TPC current benchmark specifications: https://www.tpc.org/tpc_documents_current_versions/current_specifications5.asp

---

## Verification note

This document has been statically reviewed against the project tree, the Topic 06 roadmap, the required workload classes, benchmark requirements, TCO dimensions, case studies, ADR fields, and checkpoint/common-mistake list. The formulas and illustrative scoring arithmetic were checked for internal consistency. No ClickHouse, Trino, Pinot, Druid, StarRocks/Doris, DuckDB, or warehouse benchmark was executed in this authoring session; no latency, QPS, freshness, storage, or monthly-cost measurement is claimed. The sample requirements, costs, and ADR are explicitly illustrative. Run the lab against your exact engine versions and preserve raw results before making a production decision.
