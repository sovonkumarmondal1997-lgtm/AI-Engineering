# Materialized Views and Pre-Aggregation

> **Module:** Stage 2C — Data Engineering_3 / 07-Real-Time-OLAP-and-Query-Engines  
> **Lesson:** `05-materialized-views-and-pre-aggregation.md`  
> **Level:** Beginner → advanced data engineering  
> **Scope:** Aggregate design, correctness, refresh behavior, engine-specific mechanisms, and a reproducible lab.

## 1. Learning objectives and prerequisites

By the end of this lesson, you should be able to:

- Explain why repeated dashboard `GROUP BY` queries are candidates for pre-aggregation.
- Distinguish a logical view, a materialized view, a summary table, and a cache.
- Choose an appropriate refresh model and state the freshness guarantee it provides.
- Combine counts, sums, minima, maxima, averages, and distinct counts without changing their meaning.
- Design rollups by dimensions and time grain while estimating cardinality and storage.
- Use ClickHouse aggregate states (`AggregateFunction`, `-State`, `-Merge`) and explain the roles of HyperLogLog, t-digest, and Theta sketches.
- Compare ClickHouse materialized views and projections with Druid roll-up, Pinot star-tree, StarRocks asynchronous materialized views, Snowflake dynamic tables, BigQuery materialized views, and Trino materialized views on Iceberg.
- Explain the effect of late arrivals, duplicate events, corrections, deletes, and transformation changes.
- Reconcile precomputed results with canonical raw data and plan a safe backfill.
- Measure query latency, ingestion overhead, storage, and refresh cost without assuming a speedup in advance.

### Prerequisites

You should be comfortable with SQL `GROUP BY`, joins, timestamps, `EXPLAIN`, dimensional modeling, columnar storage, ClickHouse MergeTree basics, and the general role of Trino and lakehouse tables. Familiarity with approximate aggregates from Module 2C.9 and caching/serving from Module 2.22 is useful. This lesson references those topics but does not replace them.

### Vocabulary used throughout

We use UTC timestamps and half-open time windows: `start <= event_time AND event_time < end`. A “minute bucket” begins at a UTC minute boundary; an “hour bucket” begins at a UTC hour boundary. A **canonical event** is the accepted current representation of an event after deduplication/correction policy. A **raw event log** may contain duplicate deliveries and correction history, so it is not automatically the same thing as canonical current state.

---

## 2. Purpose and mental model of pre-aggregation

### 2.1 Why it exists

Imagine a product analytics dashboard with 30 panels. Several panels repeatedly ask for the same facts:

```sql
SELECT
    toStartOfHour(event_time) AS hour_utc,
    country,
    count() AS events,
    sum(revenue) AS revenue
FROM events
WHERE event_time >= now() - INTERVAL 7 DAY
GROUP BY hour_utc, country;
```

Another panel groups by hour and device; a third groups by country and page; a fourth asks for unique users per hour. Without pre-aggregation, the engine repeatedly scans event rows, applies filters, groups them, and computes measures. Columnar storage and indexes can make those queries efficient, but the computation is still repeated.

Pre-aggregation moves part of that work to ingestion or refresh time. Instead of storing only millions of events, the system also stores reusable grouped results such as `(hour_utc, country) → event_count, revenue_sum`. Dashboard queries then scan fewer rows and merge smaller aggregates.

The trade-off is not “free speed.” Pre-aggregation exchanges some combination of:

- **Read work:** fewer rows scanned and fewer groups computed per dashboard request.
- **Storage:** extra aggregate rows and sometimes larger intermediate states.
- **Write work:** each input may update one or more aggregate structures.
- **Refresh work:** scheduled/incremental refreshes consume compute and can lag.
- **Correctness complexity:** corrections, deletes, deduplication, and logic changes may require compensation or rebuilding.
- **Flexibility:** a rollup cannot answer dimensions or detail that were discarded.

Use it when query patterns are repetitive and predictable, the data reduction is meaningful, and the required freshness/correction semantics can be maintained. Keep raw/canonical detail when users need arbitrary drill-downs, auditability, or future metrics.

### 2.2 A useful mental model

```text
Canonical events
    │
    ├── raw/detail queries ────────────────────────────────┐
    │                                                     │
    ├── minute aggregate: minute + selected dimensions    │
    │        │                                            │
    │        └── hour/day rollups or independent MVs      │
    │                                                     ▼
    └── reconciliation and backfill                 Dashboard/API
```

A rollup is a **lossy projection of the event set**. It retains only selected dimensions and aggregate information. If the rollup keeps `(hour, country, device)` but discards `page`, it cannot later answer “top pages by country and hour” exactly unless that information is retained elsewhere.

### 2.3 Refresh models

| Model | How it works | Freshness and trade-off | Typical fit |
|---|---|---|---|
| On-insert / ingest-time | Each insert or ingest batch updates derived state | Low lag; adds work to ingestion; behavior is source- and engine-specific | Append-heavy events with stable transformation logic |
| Incremental refresh | Process only changes since a prior refresh or maintain deltas | Efficient when changes and query operators are supported; correctness depends on change tracking and supported semantics | Continuously changing warehouse/lakehouse tables |
| Scheduled refresh | Recompute or incrementally refresh at a configured cadence | Bounded but nonzero staleness; predictable compute window | Dashboards with a few minutes of acceptable lag |
| Full refresh | Re-run the defining query and replace/rebuild the result | Simple conceptual correctness, potentially expensive and slow | Small summaries, logic changes, unsupported incremental operations |
| Manual refresh | Operator/job explicitly invokes refresh | Freshness depends on orchestration and success monitoring | Controlled backfills, experiments, low-frequency data |

These terms describe broad models, not a universal SQL contract. For example, a ClickHouse incremental materialized view is triggered by inserts into its source table; it is not a generic “keep this query synchronized with all future UPDATE and DELETE operations” abstraction. A Snowflake dynamic table has its own refresh modes and target-lag behavior. Trino's materialized-view definition and refresh are connector-dependent.

---

## 3. View, materialized view, summary table, and cache

| Mechanism | Stores result rows? | Who maintains it? | Can it be used transparently? | Main risk |
|---|---:|---|---|---|
| Ordinary/logical view | Usually no | Query runs when read | Query names the view; optimizer may inline it | Repeats underlying work |
| Materialized view (MV) | Yes, or connector-managed physical result | Engine refresh/maintenance mechanism | Sometimes; optimizer rewrite is not universal | Staleness, unsupported rewrites, correction semantics |
| Summary/aggregate table | Yes | ETL/job/application/SQL pipeline | Usually only if query/application routes to it, unless optimizer recognizes it | Orchestration and reconciliation burden |
| Result cache | Cached query output | Engine cache policy | Often transparent for matching queries | Invalidation, cache key, and freshness behavior |
| Redis/application cache | Key-value response or precomputed response | Application or cache policy | Application explicitly reads it | Invalidation, duplicate business logic, hot keys |
| CDN cache | HTTP response near clients | HTTP cache headers and purge policy | Transparent at HTTP layer | Stale responses and personalization/security leakage |

An MV is a stored result with a query definition and some maintenance mechanism. A summary table is a stored result without necessarily having native MV metadata or automatic optimizer integration. A cache reuses a prior result; it does not necessarily maintain an analytically useful set of rollup dimensions. A cache key might be a full SQL string plus parameters, whereas an aggregate table deliberately supports a family of queries.

**Decision rule:** use an aggregate structure to reduce repeated computation across related queries; use a cache when repeated requests are identical or nearly identical and a cache hit is likely. They can coexist.

---

## 4. Aggregate semantics and correctness

The most important design decision is not the table engine; it is whether the stored state is sufficient to produce the requested metric correctly at a coarser grain.

### 4.1 Which aggregates combine directly?

Suppose one hour is composed of minute groups \(i\).

| Measure | Store at the lower grain | Combine into a higher grain | Caveat |
|---|---|---|---|
| Event count | `count` | `sum(minute_count)` | Only if each canonical event contributes once |
| Revenue | `sum(revenue)` | `sum(minute_revenue)` | Corrections/refunds must be represented consistently |
| Minimum | `min(value)` | `min(minute_min)` | A deletion of the minimum may require recomputation |
| Maximum | `max(value)` | `max(minute_max)` | A deletion of the maximum may require recomputation |
| Average | `sum(value)` and `count(value)` | `sum(sum_value) / sum(non_null_count)` | Do not average the averages without weights |
| Exact distinct users | Exact set or equivalent exact state | Union sets, then count | Sets can be large; summing per-minute distinct counts is wrong |
| Approximate distinct users | Mergeable sketch state | Merge sketches, then estimate | Approximate; compatibility/precision matters |
| Percentile/quantile | Mergeable distribution sketch/state | Merge state and finalize | Averaging percentiles is not valid |

SQL `COUNT(column)` ignores `NULL`; `COUNT(*)` counts rows. If a metric is “number of events,” use a row count or a non-null event identifier with a documented null policy. If it is “number of users,” do not label `count()` as users.

### 4.2 Why average-of-averages fails

Minute A has 2 purchases with amounts 10 and 20: average = 15. Minute B has 8 purchases averaging 100: total = 800. The combined average is:

\[
\frac{10 + 20 + 800}{2 + 8} = \frac{830}{10} = 83
\]

Averaging the two minute averages gives `(15 + 100) / 2 = 57.5`, which is wrong because the minutes have different counts.

Store `sum_amount` and `count_amount`, then calculate `sum(sum_amount) / sum(count_amount)`. If null amounts are possible, the count must be `count(amount)`, not `count(*)`. For weighted averages, retain both numerator and denominator in the same way.

### 4.3 Distinct counts are non-additive

If users `{A, B}` appear in minute 1 and `{B, C}` appear in minute 2, the minute-level distinct counts are 2 and 2, but the hourly distinct count is 3, not 4. Therefore:

```sql
-- Incorrect for an hourly distinct-user count:
SELECT hour_utc, sum(minute_unique_users)
FROM minute_rollup
GROUP BY hour_utc;
```

Correct options include:

1. Recompute `COUNT(DISTINCT user_id)` from canonical raw events for the requested hour.
2. Retain exact user sets and union them at query time, if supported and affordable.
3. Store mergeable approximate distinct states, merge them, and accept/document approximation.
4. Store exact counts for a fixed, small set of groups when the cardinality and correction requirements justify the cost.

The same issue applies to “unique buyers,” “unique sessions,” and many funnel measures. Do not sum distinct counts across time buckets or dimensions unless disjointness is guaranteed by the data model.

### 4.4 Intermediate state versus final result

An **intermediate state** is a mergeable representation that can be combined with other states. A **final result** is the scalar answer after merging/finalization. A scalar such as `42 unique users` is generally not enough to derive the exact or approximate unique count of a larger interval. The state contains the information required for the merge.

ClickHouse examples below use `AggregateFunction` columns to persist intermediate states and `...Merge` functions to finalize them.

---

## 5. Rollups, cubes, dimensions, and time grain

### 5.1 Rollup and cube

A **rollup** is a family of summaries at coarser grains, for example minute → hour → day. It can also refer to grouping sets that aggregate across dimensions. A **data cube** represents combinations of dimensions, such as `(country, device, page)`, `(country, device)`, `(country, page)`, and `(country)`. A full cube can grow rapidly.

If dimensions have cardinalities `country=20`, `device=6`, `page=50,000`, and `plan=5`, the theoretical full cross-product is:

\[
20 \times 6 \times 50{,}000 \times 5 = 30{,}000{,}000
\]

That is the upper bound if every combination exists for a single time bucket. Real data is usually sparse, but high-cardinality combinations can still produce huge tables. Avoid building every possible cube just because the database can.

### 5.2 Choosing time grain

| Grain | Strength | Cost/limitation | Common use |
|---|---|---|---|
| Raw event | Arbitrary drill-down, full detail | Largest scans and storage | Audits, detailed funnels, corrections |
| Minute | Near-real-time time series | Many rows over long retention | Live dashboards and anomaly views |
| Hour | Smaller, useful for multi-day trends | Cannot answer minute-level questions alone | 7–90 day dashboards |
| Day | Compact long-term history | Hides intraday peaks | Long-term reporting |

Time grain is not a substitute for dimensions. A minute rollup grouped by `country, device` cannot answer page-level breakdowns. Always specify both the time grain and retained dimensions.

### 5.3 Ten-query dimension-selection exercise

This is a **sample workload**, not a claim about your actual benchmark. Assume all ten queries need event count and revenue; query 6 also needs unique users. A dimension set can serve a query when it contains every dimension needed by that query, and its time grain is at least as fine as the requested output grain.

| ID | Dashboard question | Time grain | Required dimensions |
|---|---|---|---|
| Q1 | Events/revenue by hour | Hour | — |
| Q2 | Events/revenue by hour and country | Hour | `country` |
| Q3 | Events/revenue by hour and device | Hour | `device` |
| Q4 | Events/revenue by hour, country, device | Hour | `country, device` |
| Q5 | Events/revenue by hour and page | Hour | `page` |
| Q6 | Unique users by hour and country | Hour | `country` plus distinct state |
| Q7 | Events/revenue by day and country | Day | `country` |
| Q8 | Events/revenue by hour, country, plan | Hour | `country, plan` |
| Q9 | Events/revenue by hour and plan | Hour | `plan` |
| Q10 | Events/revenue by minute and country | Minute | `country` |

A reasonable minimal candidate set for this workload is:

- `minute_country`: serves Q10 directly and can roll up to hour/day country metrics (Q2, Q7) for additive measures.
- `hour_device_country`: serves Q4 and can roll up to Q2 and Q3 for additive measures.
- `hour_page`: serves Q5.
- `hour_country_plan`: serves Q8 and can roll up to Q2 and Q9 for additive measures.
- `hour_country_users_state`: serves Q6 using mergeable distinct state. This can potentially share a physical table with `minute_country` only if that table retains the required user state at minute grain and the storage/refresh cost is acceptable.

The final bullet is a deliberate design decision: sharing a table can reduce table count, but adding a large sketch to every group increases storage and ingestion work. A minimal number of tables is not necessarily a minimal total cost. Validate this candidate set against actual SQL, filters, SLA, and correction semantics. If Q1 is frequent enough, it may be worth a dedicated hour-level total instead of aggregating country groups every time.

### 5.4 Estimate row counts before creating tables

Use:

\[
\text{rows} \approx \text{number of time buckets} \times \text{observed groups per bucket}
\]

For an illustrative 30-day period:

- Minute buckets: `30 × 24 × 60 = 43,200`
- Hour buckets: `30 × 24 = 720`
- Day buckets: `30`

Suppose observed groups per bucket are measured as: 12 countries, 4 devices, 40 country-device combinations, 8,000 pages, and 30 country-plan combinations. Then approximate rows are:

| Aggregate | Estimate | Approximate rows |
|---|---:|---:|
| Minute + country | `43,200 × 12` | 518,400 |
| Hour + country/device | `720 × 40` | 28,800 |
| Hour + page | `720 × 8,000` | 5,760,000 |
| Hour + country/plan | `720 × 30` | 21,600 |
| Hour + country distinct-user sketch | `720 × 12` | 8,640 sketch-bearing rows |

These are planning estimates based on stated assumptions, not benchmark results. They assume every listed combination appears in every bucket; actual observed row counts may be lower. Page rollup dominates row count in this example. Compression, sort order, null handling, sketch size, and engine metadata affect bytes per row, so measure actual storage rather than inventing a universal bytes-per-row value.

---

## 6. Mergeable aggregates and sketches

This section is deliberately a practical overview. For algorithm details, see Module 2C.9.

### 6.1 ClickHouse `AggregateFunction`, `-State`, `-Merge`

ClickHouse aggregate functions can return an intermediate state using `...State`. A column declared as `AggregateFunction(function, argument_types...)` stores that state. A query combines states using the corresponding `...Merge` function.

A state is not the final answer and should not be treated as a normal numeric scalar. The exact type returned by `uniqState` and its serialization are engine-managed. Keep state production and merge functions compatible.

For example:

```sql
-- State creation:
uniqState(user_id)

-- Merge states and return a final estimate:
uniqMerge(users_state)

-- For sum:
sumState(revenue)
sumMerge(revenue_state)
```

Use `sumState`/`sumMerge` and `uniqState`/`uniqMerge` as matching pairs. Do not call `sum()` on serialized aggregate-state bytes, and do not sum finalized distinct estimates.

### 6.2 HyperLogLog (HLL)

HLL is a mergeable sketch for approximate cardinality. Each input contributes to a compact state; states can be merged, then finalized to an estimate. It is useful when exact distinct counting is too costly and the business can accept a measured approximation. Precision/state size and estimator behavior depend on implementation. Do not quote a fixed error rate without specifying the implementation, precision, and validation results.

### 6.3 t-digest

t-digest is a mergeable summary for quantile/percentile estimation, often useful for latency distributions such as p50/p95/p99. It retains a compact representation of the distribution rather than every sample. Quantiles are approximate; accuracy depends on implementation, compression settings, and data distribution. Do not average p95 values from separate buckets to obtain a global p95. Merge distribution states if the engine supports it, or recompute from detail.

### 6.4 Theta sketches

Theta sketches support approximate set operations and cardinality estimation, including union and (in supported implementations) intersection/difference. They can be useful when the question involves overlap, such as “users who viewed product A and product B.” Availability and SQL/API syntax depend on the engine/library. Treat the state as an implementation-specific binary/sketch value, not as a count.

### 6.5 Exact versus approximate

| Requirement | Preferred approach | Main trade-off |
|---|---|---|
| Financial reconciliation, billing, legal counts | Exact aggregation over canonical data or validated exact state | Higher CPU/storage; correction semantics must be correct |
| Exploratory distinct users over large windows | Approximate mergeable sketch, after measuring error | Small result error accepted for lower resource use |
| Tail latency percentiles over huge event streams | Mergeable quantile sketch | Approximate quantiles; configuration and distribution matter |
| User overlap/cohort intersections | Theta or other set sketch if supported | Approximate set operations and implementation-specific semantics |

To compare approximation with exact count, calculate both from the same canonical dataset and report absolute error and relative error:

\[
\text{absolute error} = |\text{estimate} - \text{exact}|
\]

\[
\text{relative error} = \frac{|\text{estimate} - \text{exact}|}{\text{exact}}
\]

If exact is zero, relative error is undefined; report absolute error and label the denominator case. Do not fabricate a measured error or promise that an implementation always stays within a chosen threshold.

---

## 7. Engine-specific implementations and trade-offs

These systems do **not** implement one identical abstraction. Check the version, connector, supported SQL operators, refresh policy, and optimizer plan for the deployment you actually run.

### 7.1 ClickHouse materialized views

A ClickHouse incremental materialized view is generally an insert-trigger-like transformation: inserts into the source table feed the view query, and output is inserted into the target table (or an implicit target if configured). It is excellent for append-oriented event ingestion and aggregate-state targets.

Key implications:

- A late event **inserted as a new row** can update its historical bucket because the view processes the inserted row. “Late” does not automatically mean “missed.”
- An `ALTER TABLE ... UPDATE/DELETE`, mutation, partition drop, or correction to already-ingested data does not behave like a universal recomputation of all MV output. Design an explicit correction/rebuild path.
- If duplicate deliveries are inserted twice, the MV can count them twice unless idempotency/deduplication is handled before aggregation or by a safe compensation strategy.
- `AggregatingMergeTree` stores aggregate states; query with `...Merge` and group by the full target grain. Background merges are not a reason to skip correct query-time merging.
- A view that writes to a separate target does not make that target a canonical source of truth. Keep raw/canonical data for audit and reconciliation.

A basic aggregate target can use `AggregatingMergeTree`:

```sql
CREATE TABLE events_minute
(
    minute_utc DateTime('UTC'),
    country LowCardinality(String),
    device LowCardinality(String),
    event_count_state AggregateFunction(count),
    revenue_state AggregateFunction(sum, Decimal(18, 2)),
    users_state AggregateFunction(uniq, UInt64)
)
ENGINE = AggregatingMergeTree
ORDER BY (minute_utc, country, device);

CREATE MATERIALIZED VIEW events_to_minute
TO events_minute
AS
SELECT
    toStartOfMinute(event_time) AS minute_utc,
    country,
    device,
    countState() AS event_count_state,
    sumState(revenue) AS revenue_state,
    uniqState(user_id) AS users_state
FROM events_raw
GROUP BY minute_utc, country, device;
```

Query the stored states like this:

```sql
SELECT
    toStartOfHour(minute_utc) AS hour_utc,
    country,
    countMerge(event_count_state) AS events,
    sumMerge(revenue_state) AS revenue,
    uniqMerge(users_state) AS approximate_unique_users
FROM events_minute
WHERE minute_utc >= toDateTime('2026-01-01 00:00:00', 'UTC')
  AND minute_utc <  toDateTime('2026-01-02 00:00:00', 'UTC')
GROUP BY hour_utc, country;
```

`uniqMerge(users_state)` merges all selected states within each `(hour_utc, country)` group and produces one estimate. It must not be wrapped in `sum()` or pre-finalized at minute level. Likewise, `countMerge` and `sumMerge` merge their respective stored states across all matching rows in the output group; do not nest them inside another aggregate.


For a real production schema, validate aggregate-state grouping and function types against the ClickHouse version in use. Often the simpler and safer design is to build a separate hour target directly from `events_raw`, or to store state columns and aggregate them directly at the target grain. Do not build a multi-level pipeline until you have tested the state-merging plan.

### 7.2 ClickHouse projections

A projection is an alternate physical representation within a table, such as a different sort order or a pre-aggregated representation. It can improve pruning/access patterns without requiring the application to name a separate summary table. The optimizer may select a projection when it is semantically applicable, but selection is not guaranteed for every query. Verify with `EXPLAIN` and system metadata.

Choose a projection when the access pattern maps to a different useful ordering or supported pre-aggregation and the storage/write cost is justified. Choose an MV when you need a distinct derived dataset, explicit aggregate-state logic, or a different lifecycle. Projection support and optimizer behavior vary by ClickHouse version and projection type.

### 7.3 Apache Druid roll-up

Druid can combine rows at ingestion time when their dimensions and timestamp are identical after the configured query-granularity truncation. `segmentGranularity` controls time chunk/segment partitioning; `queryGranularity` controls timestamp truncation for roll-up. Roll-up can reduce row count and storage substantially, but discards event-level detail. It is not equivalent to a generic SQL MV refreshed after arbitrary updates.

Use roll-up when the expected query dimensions and metrics are known at ingestion. Late events may be ingested into historical time intervals depending on ingestion/task and segment-replacement/compaction workflow; this is not the same as a ClickHouse insert-trigger MV. For corrections or deduplication, understand Druid's ingestion, reindexing, and compaction model for the deployed version.

### 7.4 Apache Pinot star-tree

Pinot's star-tree index precomputes aggregate combinations over selected dimensions and metrics to accelerate compatible aggregation queries. It is an index-based optimization inside Pinot segments, not a user-managed general-purpose SQL summary table. The star-tree configuration determines dimensions, split behavior, and aggregations; only compatible query patterns benefit.

Use it for repeated, high-QPS aggregation patterns with a known schema. More dimensions increase index construction/storage cost. It does not preserve arbitrary event detail that was excluded from the index, and support/behavior depends on Pinot version and query engine. Inspect the query plan and measure with/without the index.

### 7.5 StarRocks asynchronous materialized views

StarRocks asynchronous MVs store precomputed query results and can support multi-table joins, aggregations, refresh schedules/manual refresh, partition-aware refresh, and transparent query rewrite for supported query shapes. Synchronous rollup-style MVs are a different feature with narrower operators and synchronous load-time maintenance.

The optimizer uses an MV only when the query is compatible and freshness/consistency policy permits it. A successful `CREATE MATERIALIZED VIEW` does not prove that a later dashboard query used it. Inspect explain plans and MV refresh/task metadata. For native tables, StarRocks can enforce consistency checks; external-catalog sources have different visibility into source changes and may not provide the same strong consistency guarantees.

Illustrative syntax (verify exact properties and supported query shape for the StarRocks version):

```sql
CREATE MATERIALIZED VIEW mv_hour_country
DISTRIBUTED BY HASH(country) BUCKETS 8
REFRESH SCHEDULE EVERY (INTERVAL 5 MINUTE)
AS
SELECT
    date_trunc('hour', event_time) AS hour_utc,
    country,
    count(*) AS events,
    sum(revenue) AS revenue
FROM events
GROUP BY date_trunc('hour', event_time), country;
```

This is an illustration of an asynchronous MV, not a promise that every StarRocks release accepts every distribution/refresh clause exactly as written. Validate DDL against the deployed version and then prove rewrite using `EXPLAIN`.

### 7.6 Snowflake dynamic tables

A dynamic table defines a query whose results Snowflake refreshes toward a target lag. Refresh can use incremental, full, auto, or adaptive modes depending on the supported definition and release. Target lag is a freshness target, not a hard real-time guarantee. Some updates or bulk operations can trigger reinitialization/full work; incremental refresh is available only for supported query patterns.

Illustrative pattern:

```sql
CREATE OR REPLACE DYNAMIC TABLE analytics.hour_country
    TARGET_LAG = '5 minutes'
    WAREHOUSE = analytics_wh
    REFRESH_MODE = INCREMENTAL
AS
SELECT
    DATE_TRUNC('hour', event_time) AS hour_utc,
    country,
    COUNT(*) AS events,
    SUM(revenue) AS revenue
FROM analytics.events
GROUP BY 1, 2;
```

Check the refresh mode actually used, refresh history, lag, and warehouse consumption. Do not assume “dynamic table” means on-insert synchronous maintenance or zero refresh cost.

### 7.7 BigQuery materialized views

BigQuery incremental materialized views support a restricted SQL/function subset and can incrementally maintain results for supported changes. Smart tuning can rewrite eligible queries to use an MV. When changes or query shapes invalidate incremental use, BigQuery may read base-table changes or fall back to base data; non-incremental MVs support broader definitions but require full refresh and do not receive the same smart-tuning behavior.

Illustrative aggregate:

```sql
CREATE MATERIALIZED VIEW `project_id.analytics.mv_hour_country`
AS
SELECT
  TIMESTAMP_TRUNC(event_time, HOUR, 'UTC') AS hour_utc,
  country,
  COUNT(*) AS events,
  SUM(revenue) AS revenue
FROM `project_id.analytics.events`
GROUP BY hour_utc, country;
```

Verify supported SQL, query rewrite, bytes processed, refresh history, and any staleness settings in the current BigQuery documentation. Do not assume every delete/update pattern is incrementally maintained without cost or restrictions.

### 7.8 Trino materialized views on Iceberg

Trino has SQL for creating and refreshing materialized views, but **the connector determines where and how results are stored and which properties/operations are supported**. The Trino Iceberg connector documents materialized-view creation with properties such as storage partitioning; refresh is explicit unless a separate orchestration policy invokes it. Refresh may be incremental or full depending on definition and snapshot history. Do not assume a query against base tables is automatically rewritten to use this MV: reference the MV directly unless the exact Trino release and connector documentation plus `EXPLAIN` prove otherwise. This differs from ClickHouse's insert-trigger MV and Snowflake's managed dynamic-table refresh.

Illustrative Trino SQL (run with an Iceberg catalog and a supported Trino version):

```sql
CREATE MATERIALIZED VIEW iceberg.analytics.mv_hour_country
WITH (partitioning = ARRAY['country'])
AS
SELECT
    date_trunc('hour', event_time) AS hour_utc,
    country,
    count(*) AS events,
    sum(revenue) AS revenue
FROM iceberg.analytics.events
GROUP BY 1, 2;

REFRESH MATERIALIZED VIEW iceberg.analytics.mv_hour_country;
```

After base-table changes, schedule/execute refresh and monitor its completion. Validate connector support, storage format, permissions, refresh semantics, stale-view behavior, and optimizer rewrite for the exact connector/version. Do not treat Trino as a native always-on aggregate store or assume all connectors implement the same MV lifecycle.

### 7.9 Summary comparison

| Mechanism | Where aggregation occurs | Refresh/maintenance | Transparent rewrite? | Corrections and late data |
|---|---|---|---|---|
| ClickHouse incremental MV | On source inserts | Insert-trigger-like; target stores rows/states | Not a general optimizer rewrite requirement | Late inserts flow through; source mutations/deletes and duplicates require explicit design |
| ClickHouse projection | Physical alternate representation | Engine-maintained with base table | Optimizer may select it | Depends on projection type and engine maintenance; verify version/plan |
| Druid roll-up | Ingestion | Ingestion/segment workflow | Query reads rolled-up datasource; not generic MV rewrite | Late data and corrections follow ingestion/reindex/compaction workflow |
| Pinot star-tree | Segment/index build | Segment/index lifecycle | Compatible queries can use index | Index is not a universal correction/rewrite mechanism |
| StarRocks async MV | MV storage | Async, scheduled, or manual refresh | Yes for supported query shapes and freshness rules | Native/external source consistency differs; verify refresh and rewrite |
| Snowflake dynamic table | Managed derived table | Target-lag refresh, incremental/full/adaptive modes | Queries can read the table; not equivalent to every MV rewrite | Depends on refresh support; some changes can trigger reinitialization |
| BigQuery MV | Managed precomputed data | Background/incremental when supported; fallback/refresh behavior varies | Smart tuning for eligible incremental MVs | Engine can compensate for some base changes; unsupported changes may invalidate incremental path |
| Trino MV + Iceberg | Connector-managed Iceberg storage table | Explicit refresh; incremental or full depending on definition/history | Do not assume base-query rewrite; query the MV explicitly unless verified | Refresh after source changes; freshness is checked against source snapshots |

---

## 8. Late data, duplicates, corrections, reconciliation, and backfills

### 8.1 Separate four cases

1. **Late new event:** event time is old, but the event is newly inserted and valid.
2. **Duplicate delivery:** the same logical event is inserted more than once.
3. **Correction:** a previously accepted event's timestamp, dimensions, or measures change.
4. **Deletion/retraction:** an event is no longer valid and must stop contributing.

They are different data operations and should not share one vague “late data” policy.

### 8.2 Why insert-triggered aggregates can drift

Suppose event `E1` was inserted with revenue 10, so the MV adds 10 to a minute bucket. Later, a correction says its revenue is 12. If the corrected row is simply inserted as another row, an insert-trigger MV may add 12, leaving total 22. If the source row is updated to 12, the aggregate target is not automatically guaranteed to subtract 10 and add 12. The correct net contribution is 12.

Likewise, a duplicate event can add its contribution twice. For distinct sketches, even a “subtract old event” approach is generally not available: many sketches are not invertible in the way a sum is. This is why correction policy must be designed before relying on aggregate states.

### 8.3 Reliable patterns

**Pattern A — append-only, immutable events.** Each event is unique and corrections are represented as new compensating facts (for example, a refund is a negative revenue fact). This works well for additive metrics when the business semantics truly are additive. It does not automatically solve distinct-user correction or a correction that changes the event's grouping dimensions.

**Pattern B — canonicalize before aggregation.** Deduplicate by stable event ID and apply version/correction rules in a canonical table or upstream pipeline. Aggregate only accepted canonical records. Be careful: a ReplacingMergeTree-like engine may resolve versions during merges, but an MV fed by each insert can still have already counted every version. Deduplicating source reads is not the same as undoing old MV contributions.

**Pattern C — rebuild affected buckets.** Identify the old and new bucket(s), recompute them from canonical data, and replace/rebuild those partitions or rows in a controlled process. This is often the clearest strategy for corrected distinct counts or changed dimensions.

**Pattern D — delta/compensation ledger.** Emit a negative old contribution and positive new contribution for additive metrics. This requires a reliable old value and exactly-once/idempotent processing. It does not work generically for non-invertible sketches.

For every path, define an idempotency key, correction/version ordering, maximum late-arrival horizon, and a recovery procedure after partial failure.

### 8.4 Reconciliation

Reconcile aggregates against canonical raw data at the same time range, filter conditions, dimensions, null rules, and event acceptance policy. Compare row counts and additive measures first; compare distinct metrics separately using exact results or a documented approximation tolerance.

A ClickHouse example for a simple count/revenue minute aggregate. `FULL OUTER JOIN` unmatched-side detection below relies on nullable join columns, so the query sets `join_use_nulls = 1` (or implement missing-group checks with explicit anti-joins):

```sql
WITH
raw AS
(
    SELECT
        toStartOfMinute(event_time) AS minute_utc,
        country,
        count() AS events,
        sum(revenue) AS revenue
    FROM events_canonical
    WHERE event_time >= toDateTime('2026-01-01 00:00:00', 'UTC')
      AND event_time <  toDateTime('2026-01-02 00:00:00', 'UTC')
    GROUP BY minute_utc, country
),
agg AS
(
    SELECT
        minute_utc,
        country,
        countMerge(event_count_state) AS events,
        sumMerge(revenue_state) AS revenue
    FROM events_minute
    WHERE minute_utc >= toDateTime('2026-01-01 00:00:00', 'UTC')
      AND minute_utc <  toDateTime('2026-01-02 00:00:00', 'UTC')
    GROUP BY minute_utc, country
)
SELECT
    coalesce(raw.minute_utc, agg.minute_utc) AS minute_utc,
    coalesce(raw.country, agg.country) AS country,
    raw.events AS raw_events,
    agg.events AS aggregate_events,
    raw.revenue AS raw_revenue,
    agg.revenue AS aggregate_revenue
FROM raw
FULL OUTER JOIN agg
    ON raw.minute_utc = agg.minute_utc
   AND raw.country = agg.country
WHERE raw.events != agg.events
   OR agg.events IS NULL
   OR raw.events IS NULL
   OR abs(raw.revenue - agg.revenue) > 0.01
SETTINGS join_use_nulls = 1;
```

This is a reconciliation template; validate syntax and `join_use_nulls` behavior in your deployment. The important logic is a full comparison so that missing aggregate groups and unexpected extra aggregate groups are not hidden by an inner join. Adapt aggregate-state expressions to the exact target schema. If the target uses ordinary scalar columns rather than aggregate states, do not use `countMerge`/`sumMerge`.

Reconciliation checks should include:
- Row/group coverage: missing and unexpected groups.
- Exact additive totals: event count, revenue, quantity.
- Min/max where deletions/corrections could remove an extreme.
- Distinct counts: exact canonical calculation versus estimate and relative/absolute error.
- Freshness: source watermark versus last successful refresh/ingestion time.
- Version/logic: aggregation definition version and backfill status.

### 8.5 Drift detection and backfills

When transformation logic changes, existing aggregate rows do not magically adopt the new logic. Version the transformation definition. A safe backfill plan is:

1. Freeze or capture a consistent source boundary/watermark.
2. Build the new aggregate into a shadow table or new partition set.
3. Reconcile it against canonical data over a representative interval.
4. Compare old and new outputs, including edge cases and distinct/quantile measures.
5. Atomically switch the serving view/table or use a controlled cutover.
6. Monitor freshness and query plans after the switch.
7. Retain a rollback path until correctness is proven.

For late arrivals, choose a reprocessing horizon based on observed lateness and business rules. “Recompute the last day” is not safe if corrections can arrive after a week; the horizon must be grounded in source behavior and SLA.

---

## 9. Tiered aggregate architecture and cost modeling

### 9.1 Aggregate pyramid

```text
Raw/canonical event retention:      30–180 days (example only)
        │
        ├── Minute aggregates:      3–14 days
        │       │
        │       └── Hour aggregates: 30–180 days
        │                │
        │                └── Day aggregates: 1–5 years
        │
        └── Reconciliation, audit, and rebuild path
```

The durations above are illustrative, not recommendations for every system. Retention depends on compliance, product needs, correction horizons, cost, and whether raw data is archived elsewhere. Do not delete raw data until the organization has accepted the loss of drill-down and has a tested rebuild/reconciliation strategy.

A tiered design can use direct raw-to-hour and raw-to-day MVs instead of chaining minute → hour → day. Direct derivation avoids cascading-state complexity and can simplify correction/rebuild logic, but it can repeat source work. A chained pyramid can save repeated raw scans but requires careful mergeability, refresh ordering, and recovery after missed or duplicated upstream batches. Benchmark both when scale warrants it.

### 9.2 Manual routing versus optimizer rewrite

- **Manual routing:** application/query layer chooses `events_minute`, `events_hour`, or raw data based on requested time range and dimensions. This is explicit and predictable but duplicates logic and can route incorrectly.
- **Optimizer-driven rewrite:** the engine decides whether an MV/projection/index can answer the original query. This reduces application changes but depends on supported query patterns, statistics, freshness, and engine version.
- **Hybrid:** expose stable semantic views and verify plans; use explicit aggregate tables for queries where automatic rewrite is not available.

Never assume that because an MV exists, the optimizer used it. Confirm using `EXPLAIN`, query logs, bytes scanned, and engine-specific MV statistics.

### 9.3 A simple break-even model

Let:

- \(Q\) = dashboard queries per day,
- \(C_r\) = average compute cost per raw query,
- \(C_a\) = average compute cost per aggregate-backed query,
- \(C_m\) = daily maintenance/refresh compute cost,
- \(C_s\) = daily storage cost of aggregate tables,
- \(C_w\) = extra daily ingestion/write cost caused by maintaining aggregates.

Approximate net daily benefit:

\[
\text{net benefit} = Q(C_r - C_a) - C_m - C_s - C_w
\]

This is a decision aid, not a billing formula. Include concurrency, p95/p99 latency, freshness, failure/recovery labor, and opportunity cost in a real decision. An aggregate can improve latency while increasing total cost; it may still be justified for an SLA.

### 9.4 Measure rather than invent

Record before/after values on the same data, hardware, filters, query results, and concurrency. For latency, calculate `speedup = baseline_latency / aggregate_latency` and `latency_reduction_pct = 100 × (baseline_latency - aggregate_latency) / baseline_latency`; use the same percentile on both sides and report the raw measurements too. If the baseline latency is zero or invalid, the ratio is undefined. Measure:

- p50/p95/p99 query latency and throughput.
- Rows read, bytes read, CPU, memory, and spill where available.
- Ingestion throughput and end-to-end freshness.
- MV refresh duration, lag, failure rate, and compute usage.
- Table/partition bytes, row count, compression, and sketch state size.
- Reconciliation differences and recovery time after correction/backfill.

Use warm-up runs and multiple measured iterations; report medians and spread. Avoid comparing a warm cached baseline against a cold aggregate query or changing the data volume between tests.

### 9.5 Caches versus pre-aggregation

| Workload | Better first candidate | Why |
|---|---|---|
| Same exact query repeats with same parameters | Result cache | Avoids repeated identical work with minimal modeling |
| Same dashboard grouping with different time ranges/filters | Aggregate table/MV | Reuses aggregate state across a family of queries |
| User-specific response by key with strict low latency | Redis/application cache | Fast key-value lookup; requires explicit invalidation/freshness policy |
| Public/static HTTP response | CDN | Caches at edge; appropriate only when authorization/personalization semantics permit |
| Ad hoc questions with unknown dimensions | Raw columnar table and query optimization | Precomputing every possible grouping is wasteful |
| Predictable high-QPS aggregates with tight SLA | MV/rollup/index, possibly plus cache | Materialize reusable computation and cache exact hot responses if useful |

A CDN or Redis cache does not replace a governed aggregate model. Conversely, pre-aggregation does not eliminate the benefit of caching a hot, identical response.

---

## 10. Hands-on experiments — `experiments/05_preaggregation/`

The roadmap lab is organized around three slow queries, minute/hour rollups, an equivalent strategy in a second engine, distinct-count correctness, late/corrected events, reconciliation, and before/after measurements.

### 10.1 Lab structure

Create:

```text
experiments/05_preaggregation/
├── README.md
├── clickhouse/
│   ├── 01_schema.sql
│   ├── 02_seed_data.sql
│   ├── 03_rollups.sql
│   ├── 04_queries.sql
│   └── 05_reconciliation.sql
├── trino-iceberg/
│   └── 01_hour_country_mv.sql
├── bench/
│   ├── query-set.md
│   └── results.csv
└── notes.md
```

This is a suggested lab file layout inside the roadmap's `experiments/05_preaggregation/`; the lesson itself does not create or run those repository files.

### 10.2 Step 1 — Create a reproducible ClickHouse dataset

The following is a small deterministic smoke dataset. It is intentionally small for correctness checks; scale the generator later for performance tests. Run in a clean ClickHouse database. Create `events_raw` now, but **defer the `INSERT` block and baseline checks until after Step 10.4 has created both materialized views**. That ordering ensures the insert-trigger views receive the seed rows.

```sql
CREATE TABLE events_raw
(
    event_id UInt64,
    ingest_seq UInt64, -- strictly increasing ingestion/version sequence for this lab
    event_time DateTime('UTC'),
    user_id UInt64,
    country LowCardinality(String),
    device LowCardinality(String),
    page LowCardinality(String),
    plan LowCardinality(String),
    revenue Decimal(18, 2)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, country, device, event_id);

INSERT INTO events_raw VALUES
(1, 1, '2026-01-01 10:00:05', 101, 'IN', 'mobile', '/home', 'free',  0.00),
(2, 2, '2026-01-01 10:00:20', 102, 'IN', 'desktop','/pricing','pro', 10.00),
(3, 3, '2026-01-01 10:01:10', 101, 'IN', 'mobile', '/pricing','free', 0.00),
(4, 4, '2026-01-01 10:02:05', 103, 'US', 'mobile', '/home', 'pro', 20.00),
(5, 5, '2026-01-01 10:02:30', 104, 'US', 'desktop','/home', 'free', 0.00),
(6, 6, '2026-01-01 10:03:15', 102, 'IN', 'desktop','/checkout','pro', 5.00),
(7, 7, '2026-01-01 10:03:45', 105, 'IN', 'mobile', '/home', 'free', 0.00),
(8, 8, '2026-01-01 10:04:05', 101, 'IN', 'mobile', '/checkout','free', 0.00),
(9, 9, '2026-01-01 10:04:40', 106, 'US', 'desktop','/pricing','pro', 15.00),
(10,10,'2026-01-01 10:05:10', 103, 'US', 'mobile', '/checkout','pro', 5.00);
```

`events_raw` is the append-only lab input. The table does not itself enforce uniqueness of `event_id`. In production, deduplicate or canonicalize before using these rows as truth.

Baseline correctness checks:

```sql
SELECT count() AS event_rows, sum(revenue) AS revenue
FROM events_raw;

SELECT
    uniqExact(user_id) AS exact_unique_users,
    uniq(user_id) AS approximate_unique_users
FROM events_raw;
```

For this sample, there are 10 rows, total revenue is 55.00, and the exact distinct user count is 6. The approximate function may equal 6 on a tiny set, but that is not evidence of its error rate on production data.

### 10.3 Step 2 — Select three slow dashboard queries

If you have a benchmark, choose the three slowest by p95 latency and record the query IDs, filters, time range, and result checksum. If you do not yet have a benchmark, use this clearly labeled sample workload:

**Q-A: Hourly event/revenue trend**

```sql
SELECT
    toStartOfHour(event_time) AS hour_utc,
    count() AS events,
    sum(revenue) AS revenue
FROM events_raw
WHERE event_time >= toDateTime('2026-01-01 00:00:00', 'UTC')
  AND event_time <  toDateTime('2026-01-02 00:00:00', 'UTC')
GROUP BY hour_utc
ORDER BY hour_utc;
```

**Q-B: Hourly country/device breakdown**

```sql
SELECT
    toStartOfHour(event_time) AS hour_utc,
    country,
    device,
    count() AS events,
    sum(revenue) AS revenue
FROM events_raw
WHERE event_time >= toDateTime('2026-01-01 00:00:00', 'UTC')
  AND event_time <  toDateTime('2026-01-02 00:00:00', 'UTC')
GROUP BY hour_utc, country, device
ORDER BY hour_utc, country, device;
```

**Q-C: Hourly distinct users by country**

```sql
SELECT
    toStartOfHour(event_time) AS hour_utc,
    country,
    uniqExact(user_id) AS exact_unique_users
FROM events_raw
WHERE event_time >= toDateTime('2026-01-01 00:00:00', 'UTC')
  AND event_time <  toDateTime('2026-01-02 00:00:00', 'UTC')
GROUP BY hour_utc, country
ORDER BY hour_utc, country;
```

These query examples are defined here for planning; execute them after the seed `INSERT` in Step 10.2 has run (the MVs must first be created in Step 10.4). Run each query several times, capture p50/p95, rows/bytes read, and query plan. Do not label the sample queries “slowest” unless measurements show that they are.

### 10.4 Step 3 — Build minute and hour aggregate-state targets

Use independent raw-to-minute and raw-to-hour MVs for the first lab. This makes the source of each result easy to reason about and avoids depending on cascaded MV refresh ordering.

```sql
CREATE TABLE events_minute
(
    minute_utc DateTime('UTC'),
    country LowCardinality(String),
    device LowCardinality(String),
    event_count_state AggregateFunction(count),
    revenue_state AggregateFunction(sum, Decimal(18, 2)),
    users_state AggregateFunction(uniq, UInt64)
)
ENGINE = AggregatingMergeTree
ORDER BY (minute_utc, country, device);

CREATE MATERIALIZED VIEW events_to_minute
TO events_minute
AS
SELECT
    toStartOfMinute(event_time) AS minute_utc,
    country,
    device,
    countState() AS event_count_state,
    sumState(revenue) AS revenue_state,
    uniqState(user_id) AS users_state
FROM events_raw
GROUP BY minute_utc, country, device;

CREATE TABLE events_hour
(
    hour_utc DateTime('UTC'),
    country LowCardinality(String),
    device LowCardinality(String),
    event_count_state AggregateFunction(count),
    revenue_state AggregateFunction(sum, Decimal(18, 2)),
    users_state AggregateFunction(uniq, UInt64)
)
ENGINE = AggregatingMergeTree
ORDER BY (hour_utc, country, device);

CREATE MATERIALIZED VIEW events_to_hour
TO events_hour
AS
SELECT
    toStartOfHour(event_time) AS hour_utc,
    country,
    device,
    countState() AS event_count_state,
    sumState(revenue) AS revenue_state,
    uniqState(user_id) AS users_state
FROM events_raw
GROUP BY hour_utc, country, device;
```

Create the targets and views **before** inserting the seed rows so the MVs receive those inserts. If you create them after loading the source, existing data is not retroactively processed; backfill the targets explicitly from `events_raw`. If your test database already contains data, use a clean database or run a controlled backfill instead of assuming the MV will populate history.

Queries over aggregate states:

```sql
-- Q-A: hour-level total. The hour table retains country/device groups;
-- countMerge/sumMerge combine those groups into one hour result.
SELECT
    hour_utc,
    countMerge(event_count_state) AS events,
    sumMerge(revenue_state) AS revenue
FROM events_hour
WHERE hour_utc >= toDateTime('2026-01-01 00:00:00', 'UTC')
  AND hour_utc <  toDateTime('2026-01-02 00:00:00', 'UTC')
GROUP BY hour_utc
ORDER BY hour_utc;

-- Q-B: same grain as the raw country/device query.
SELECT
    hour_utc, country, device,
    countMerge(event_count_state) AS events,
    sumMerge(revenue_state) AS revenue
FROM events_hour
WHERE hour_utc >= toDateTime('2026-01-01 00:00:00', 'UTC')
  AND hour_utc <  toDateTime('2026-01-02 00:00:00', 'UTC')
GROUP BY hour_utc, country, device
ORDER BY hour_utc, country, device;

-- Minute counts/revenue:
SELECT
    minute_utc, country, device,
    countMerge(event_count_state) AS events,
    sumMerge(revenue_state) AS revenue
FROM events_minute
GROUP BY minute_utc, country, device
ORDER BY minute_utc, country, device;

-- Hourly distinct users by country. Merge states across devices before finalizing.
SELECT
    hour_utc,
    country,
    uniqMerge(users_state) AS approximate_unique_users
FROM events_hour
GROUP BY hour_utc, country
ORDER BY hour_utc, country;
```

Compare the stored estimate to the exact baseline from the same raw population before injecting late/duplicate/corrected rows:

```sql
WITH
exact AS
(
    SELECT
        toStartOfHour(event_time) AS hour_utc,
        country,
        uniqExact(user_id) AS exact_users
    FROM events_raw
    GROUP BY hour_utc, country
),
approx AS
(
    SELECT
        hour_utc,
        country,
        uniqMerge(users_state) AS estimated_users
    FROM events_hour
    GROUP BY hour_utc, country
)
SELECT
    exact.hour_utc,
    exact.country,
    exact.exact_users,
    approx.estimated_users,
    abs(toFloat64(approx.estimated_users) - toFloat64(exact.exact_users)) AS absolute_error,
    if(
        exact.exact_users = 0,
        CAST(NULL AS Nullable(Float64)),
        abs(toFloat64(approx.estimated_users) - toFloat64(exact.exact_users))
            / toFloat64(exact.exact_users)
    ) AS relative_error
FROM exact
INNER JOIN approx USING (hour_utc, country)
ORDER BY hour_utc, country;
```

This query computes error from observed results; it does not assert a particular value or guaranteed bound. Run it against the same canonical population on both sides when testing corrections. The MV's `uniq` state is approximate; if the business requires exact distinct users, use an exact strategy or an explicitly supported exact state and measure its cost.

### 10.5 Step 4 — Equivalent strategy with Trino + Iceberg (static alternative if unavailable)

Use the same logical dimensions and additive measures in an Iceberg catalog configured for your Trino version:

```sql
CREATE MATERIALIZED VIEW iceberg.analytics.mv_hour_country_device
WITH (partitioning = ARRAY['country'])
AS
SELECT
    date_trunc('hour', event_time) AS hour_utc,
    country,
    device,
    count(*) AS events,
    sum(revenue) AS revenue
FROM iceberg.analytics.events
GROUP BY 1, 2, 3;

REFRESH MATERIALIZED VIEW iceberg.analytics.mv_hour_country_device;
```

Then query the materialized view directly and compare the same result with Q-B. Run `REFRESH MATERIALIZED VIEW` after loading or changing the Iceberg source. Confirm that the catalog/connector supports the syntax and properties for your exact Trino release; if not, use a scheduled CTAS/`INSERT OVERWRITE`-style summary-table pipeline on Iceberg and record that this is a managed summary table rather than a native connector MV.

This lab is intentionally explicit about refresh: Trino/Iceberg is not assumed to refresh synchronously on each source insert.

### 10.6 Step 5 — Insert a late event

A valid late event has an event time earlier than the current watermark but is a new logical event. Insert one with an older event time:

```sql
INSERT INTO events_raw VALUES
(11, 11, '2026-01-01 10:01:30', 107, 'IN', 'mobile', '/home', 'free', 0.00);
```

Because the ClickHouse MV is insert-triggered, this newly inserted row should contribute to its historical minute/hour bucket. Query raw and aggregate outputs again. Expected effect: row count increases by one; total revenue stays 55.00; exact distinct users rises from 6 to 7. Verify rather than assume the runtime behavior.

### 10.7 Step 6 — Duplicate delivery and correction test

Insert a duplicate delivery using the same logical `event_id` but a later ingestion sequence:

```sql
INSERT INTO events_raw VALUES
(11, 12, '2026-01-01 10:01:30', 107, 'IN', 'mobile', '/home', 'free', 0.00);
```

This lab input table has no uniqueness constraint, so the raw log now contains a duplicate delivery. The raw table has 12 rows, revenue remains 55.00, and exact distinct users remain 7. The insert-trigger MVs count 12 deliveries, so their event count is intentionally too high for canonical-event reporting.

Now correct event 2: revenue changes from 10.00 to 12.00 and its page changes. The `ingest_seq` is the lab's deterministic version order; production systems should use a source sequence/version with a defined tie policy. Append the correction as a new version:

```sql
INSERT INTO events_raw VALUES
(2, 13, '2026-01-01 10:00:20', 102, 'IN', 'desktop', '/pricing-v2', 'pro', 12.00);
```

The insert-trigger MVs have counted all raw deliveries and versions, so their output is intentionally wrong for canonical-current-state reporting. Build the canonical view by selecting the latest complete row per event ID (the tuple is selected as a unit so fields cannot come from different versions):

```sql
CREATE VIEW events_canonical AS
SELECT
    event_id,
    tupleElement(latest, 1) AS event_time,
    tupleElement(latest, 2) AS user_id,
    tupleElement(latest, 3) AS country,
    tupleElement(latest, 4) AS device,
    tupleElement(latest, 5) AS page,
    tupleElement(latest, 6) AS plan,
    tupleElement(latest, 7) AS revenue
FROM
(
    SELECT
        event_id,
        argMax(tuple(event_time, user_id, country, device, page, plan, revenue), ingest_seq) AS latest
    FROM events_raw
    GROUP BY event_id
);
```

The lab sequence is unique, so `argMax(..., ingest_seq)` has no ties. In production, resolve equal versions explicitly and represent tombstones/deletions in canonicalization logic. After the late event, duplicate, and correction, canonical current state contains 11 events, total revenue is 57.00, and exact unique users remain 7. The raw append-only log contains 13 rows and revenue 67.00 because it includes both duplicate delivery and the superseded event version.

For a controlled rebuild, create separate corrected targets (do not overwrite live targets while insert-trigger MVs are still writing to them):

```sql
CREATE TABLE events_minute_rebuilt AS events_minute;
CREATE TABLE events_hour_rebuilt AS events_hour;

INSERT INTO events_minute_rebuilt
SELECT
    toStartOfMinute(event_time), country, device,
    countState(), sumState(revenue), uniqState(user_id)
FROM events_canonical
GROUP BY toStartOfMinute(event_time), country, device;

INSERT INTO events_hour_rebuilt
SELECT
    toStartOfHour(event_time), country, device,
    countState(), sumState(revenue), uniqState(user_id)
FROM events_canonical
GROUP BY toStartOfHour(event_time), country, device;
```

Validate `CREATE TABLE ... AS` behavior and column compatibility in your ClickHouse release; if the cloned table definition does not preserve the desired engine/order, create each table explicitly with the same columns and `ENGINE = AggregatingMergeTree ORDER BY (...)`. Reconcile the rebuilt targets against `events_canonical`, changing the aggregate CTE's source table to `events_minute_rebuilt`. For distinct states, rebuild affected groups rather than assuming a sketch can subtract a corrected user's prior contribution. This demonstrates both naive drift and a canonical rebuild path.
### 10.8 Step 7 — Reconciliation query

For additive measures, compare raw canonical data with the aggregate table at identical grain and interval. Use the query in Section 8.4, adapting it to your canonical table and target schema. The full comparison must expose:
- aggregate groups absent from raw data,
- raw groups absent from aggregate data,
- count differences,
- revenue differences beyond an agreed decimal tolerance.

Run it before and after the late event. After the duplicate/correction scenario, compare `events_canonical` with the rebuilt target by changing the `agg` CTE from `events_minute` to `events_minute_rebuilt`; the original insert-trigger target is expected to disagree until rebuilt. Store mismatched-group count and maximum absolute revenue difference in `notes.md`.

### 10.9 Step 8 — Measure storage, write overhead, and latency

Use the same source dataset and query parameters for baseline and aggregate-backed runs. Report query speedup only from measured latency ratios, never from the existence of an MV. Include at least:
- Baseline and post-MV p50/p95/p99 latency (several iterations; separate warm-up).
- Rows and bytes read.
- Ingestion throughput/latency with MVs disabled versus enabled, or a comparable controlled A/B load test.
- `system.parts` bytes for raw and aggregate tables; aggregate row counts.
- MV refresh time/lag for engines with scheduled refresh.
- Exact versus approximate distinct result and error.
- Reconciliation mismatch count after every correction scenario.

Example ClickHouse storage inspection:

```sql
SELECT
    table,
    sum(rows) AS rows,
    formatReadableSize(sum(bytes_on_disk)) AS bytes_on_disk
FROM system.parts
WHERE active
  AND database = currentDatabase()
  AND table IN ('events_raw', 'events_minute', 'events_hour')
GROUP BY table
ORDER BY table;
```

Use query logs and `EXPLAIN` to establish whether the aggregate path was actually used. The lab has no built-in performance claim: the output is your measured result. Do not infer speedup from a tiny 10-row dataset; scale a generated dataset for meaningful benchmarking.

### 10.10 Results template

Fill this with observed values—do not copy invented numbers into it.

| Metric | Raw baseline | Pre-aggregated | Notes |
|---|---:|---:|---|
| Q-A p50 / p95 | | | Same data, parameters, cache conditions |
| Q-B p50 / p95 | | | Confirm query uses aggregate |
| Q-C exact p50 / p95 | | | Exact raw distinct baseline |
| Q-C sketch p50 / p95 | | | Include absolute/relative error |
| Rows/bytes read | | | Per query |
| Ingest rows/sec | | | MVs add work; control other variables |
| Raw + aggregate storage | | | Include all state columns |
| Refresh lag/duration | | | For scheduled/connector-managed path |
| Reconciliation mismatches | | | Must be zero for exact additive metrics after backfill |

---

## 11. Troubleshooting and common mistakes

| Symptom or mistake | Why it happens | Corrective action |
|---|---|---|
| Hourly distinct users are too high | Summed minute distinct counts or finalized counts | Merge distinct states at the hourly grouping level or recompute exact distincts |
| Average differs from source query | Average-of-averages or wrong denominator | Store sum and non-null count; divide after combining |
| Late events do not appear | Target not refreshed, MV created after source load, wrong source table, or engine-specific ingestion path | Verify trigger/refresh semantics, source watermark, and backfill process |
| Corrections double count | Corrected version inserted as a new additive event | Canonicalize by ID/version; rebuild affected groups or use safe compensating deltas |
| Duplicate events inflate counts/revenue | Schema contains event ID but no idempotency enforcement | Deduplicate before aggregation; test duplicate delivery explicitly |
| Query ignores MV | Query grain/filter/aggregation not compatible, freshness rule fails, or optimizer does not support rewrite | Inspect `EXPLAIN`, engine logs, MV eligibility, and refresh state |
| MV is stale after source update | Engine does not maintain that update type incrementally | Follow engine-specific invalidation/rebuild behavior; do not assume universal propagation |
| Storage explodes | High-cardinality dimension combinations or sketches retained at too fine a grain | Reduce dimensions, choose coarser grain, measure state size, retain detail separately |
| Ingestion slows unexpectedly | Multiple MVs, large state computation, excessive small inserts, or refresh contention | Batch inserts, profile each MV, simplify state, schedule expensive refreshes |
| Backfill creates duplicates | Backfill overlaps live ingestion or target is appended instead of replaced | Establish a watermark, build shadow target, reconcile, then switch atomically |
| Results differ by timezone | Mixed UTC/local bucketing or daylight-saving boundaries | Standardize timestamp type and timezone; use half-open windows |
| Percentiles are averaged across buckets | Quantiles are non-additive | Merge compatible quantile states or compute from detailed data |
| MV exists but is not a net win | Maintenance/storage costs exceed saved query work | Use the workload break-even model and remove unused aggregates |

### Common mistakes to avoid

- Pre-aggregating on every high-cardinality dimension.
- Treating distinct counts, averages, and percentiles as additive.
- Assuming all materialized views update on every source mutation.
- Treating ClickHouse insert-trigger MVs as automatically correction-safe.
- Assuming optimizer rewrite in every engine.
- Choosing dimensions from intuition rather than a representative ten-query workload.
- Deleting raw data before reconciliation/backfill is tested.
- Claiming latency or storage improvements without controlled measurements.
- Comparing engine features without recording engine version, connector, refresh settings, and query plan.
- Calling a scheduled summary table a native MV when the engine/connector does not provide native MV semantics.

---

## 12. Checkpoints and self-assessment

### Checkpoint A — fundamentals

- [ ] Explain why repeated dashboard group-bys may benefit from pre-aggregation.
- [ ] Distinguish logical views, MVs, summary tables, and caches.
- [ ] Describe on-insert, incremental, scheduled, full, and manual refresh.
- [ ] State the freshness and correction guarantees of the chosen mechanism.

### Checkpoint B — aggregate semantics

- [ ] Combine counts, sums, minima, and maxima correctly.
- [ ] Explain why averaging averages is wrong when group sizes differ.
- [ ] Explain why distinct counts cannot generally be summed across groups.
- [ ] Distinguish aggregate states from finalized scalar results.
- [ ] Explain approximate error and when exactness is required.

### Checkpoint C — design

- [ ] Produce a dimension set for ten dashboard queries and justify the minimal candidate aggregates.
- [ ] Estimate raw/minute/hour/day row counts from bucket count and observed groups.
- [ ] Identify the high-cardinality combinations likely to dominate storage.
- [ ] Explain when to use a rollup, cube, MV, projection, star-tree index, or cache.

### Checkpoint D — correctness and operations

- [ ] Demonstrate a late insert reaching an insert-trigger aggregate.
- [ ] Demonstrate duplicate/correction drift under naive ingestion.
- [ ] Reconcile aggregate totals with canonical raw data.
- [ ] Describe a safe backfill with watermark, shadow target, validation, and cutover.
- [ ] Measure latency, ingestion overhead, storage, and refresh lag without fabricating results.

### Final review questions

1. Why is `sum(minute_unique_users)` generally not the hourly unique-user count?
2. What state should an aggregate table retain to roll up an average?
3. Why can a ClickHouse MV fail to reflect a source-table mutation even though the raw table now looks correct?
4. What is the difference between a Druid ingestion roll-up and a StarRocks asynchronous MV?
5. Why is Trino MV behavior a connector/version question?
6. Which workload would benefit more from Redis caching than from a new aggregate table?
7. What evidence proves that a dashboard query actually used an MV or projection?
8. What should happen when a transformation changes the definition of revenue?

**Ready-to-advance criterion:** you can answer the questions and show a reproducible experiment where additive aggregates reconcile exactly, approximate distinct counts are compared with exact counts, correction behavior is documented, and the measured cost/latency trade-off is supported by collected results.

---

## 13. References

The following official documentation is the source of engine-specific behavior. Documentation is version-sensitive; confirm the version deployed in your lab.

### ClickHouse
- Incremental materialized views: https://clickhouse.com/docs/materialized-view/incremental-materialized-view
- Aggregate functions and aggregate states: https://clickhouse.com/docs/sql-reference/aggregate-functions
- `AggregatingMergeTree`: https://clickhouse.com/docs/engines/table-engines/mergetree-family/aggregatingmergetree
- Projections: https://clickhouse.com/docs/data-modeling/projections

### Apache Druid
- Ingestion specification and `granularitySpec`: https://druid.apache.org/docs/latest/ingestion/ingestion-spec/
- Data roll-up: https://druid.apache.org/docs/latest/ingestion/rollup/

### Apache Pinot
- Star-tree index: https://docs.pinot.apache.org/basics/indexing/star-tree-index

### StarRocks
- Asynchronous materialized views: https://docs.starrocks.io/docs/using_starrocks/async_mv/Materialized_view/
- Query rewrite: https://docs.starrocks.io/docs/using_starrocks/async_mv/
- Refresh materialized view: https://docs.starrocks.io/docs/sql-reference/sql-statements/materialized_view/REFRESH_MATERIALIZED_VIEW/

### Snowflake
- Dynamic-table refresh modes: https://docs.snowflake.com/en/user-guide/dynamic-tables/refresh-modes
- Dynamic tables: https://docs.snowflake.com/en/user-guide/dynamic-tables/overview

### BigQuery
- Materialized-view introduction: https://cloud.google.com/bigquery/docs/materialized-views-intro
- Create materialized views and supported SQL: https://cloud.google.com/bigquery/docs/materialized-views-create
- Manage and refresh materialized views: https://cloud.google.com/bigquery/docs/materialized-views-manage

### Trino / Iceberg
- Trino `CREATE MATERIALIZED VIEW`: https://trino.io/docs/current/sql/create-materialized-view.html
- Trino `REFRESH MATERIALIZED VIEW`: https://trino.io/docs/current/sql/refresh-materialized-view.html
- Iceberg connector: https://trino.io/docs/current/connector/iceberg.html

### Related roadmap modules
- Module 2C.9 — approximate algorithms and sketches: use it for deeper HLL, t-digest, and Theta-sketch mechanics.
- Module 2.22 Topic 02 — caching and serving: use it for deeper cache policy and invalidation design.

---

## Verification note

This lesson has been statically reviewed for syllabus coverage, SQL consistency, aggregation semantics, and explicit engine-specific caveats. The lab SQL is reproducible guidance, but no live ClickHouse, Trino/Iceberg, Druid, Pinot, StarRocks, Snowflake, or BigQuery cluster was available for execution in this authoring session. No runtime test, benchmark, latency improvement, storage reduction, or approximation-error result is claimed. Run the experiments on your target versions and retain the outputs as evidence.
