# Topic 03 — Partitioning, Clustering, and Query Cost Control

> **Audience:** Beginner-to-advanced data engineers working with BigQuery  
> **Module:** Stage 2C — Data Engineering_3 → 04-Google-Cloud-BigQuery-and-GCP-Data-Engineering  
> **Prerequisite:** Topic 02 — BigQuery Architecture, Slots, and Storage  
> **Next:** Topic 04 — BigQuery Loading, Streaming, and External Tables  
> **Lab root:** `experiments/03_partition_cluster/`

## 1. Learning objectives and prerequisites

By the end of this lesson, you should be able to:

- Choose ingestion-time, time-unit-column, or integer-range partitioning from actual query patterns and data-retention requirements.
- Explain partition pruning, clustering, block pruning, and the limits of both.
- Build and compare equivalent unpartitioned, partitioned, and partitioned-plus-clustered event tables.
- Use dry runs, `maximum_bytes_billed`, `require_partition_filter`, partition expiration, and project/user controls as cost guardrails.
- Reduce scanned columns and unnecessary execution work without changing query semantics.
- Evaluate approximate aggregates, result caching, materialized views, BI Engine, search indexes, and vector indexes against a workload.
- Optimize append-only ingestion, `MERGE`, joins, pre-aggregation, cross joins, `QUALIFY`, and window functions.
- Find expensive jobs using `INFORMATION_SCHEMA.JOBS_BY_PROJECT` and investigate concurrency/slot pressure using `JOBS_TIMELINE`.
- Record real measurements without confusing estimates, bytes processed, bytes billed, slot time, latency, or money.

### Prerequisites

You should already be comfortable with:

- GoogleSQL, `WHERE`, joins, grouping, window functions, CTEs, and query plans.
- BigQuery datasets, jobs, slots, storage, native tables, and on-demand versus capacity pricing (Topic 02).
- Cloud IAM and the principle of least privilege.
- The difference between event time and ingestion time, and basic batch/streaming ingestion.

### Scope and evidence rule

This lesson follows Topic 03 of `roadmap-Google-Cloud-BigQuery-and-GCP-Data-Engineering.md`. It builds on Topic 02's execution/storage model and prepares you for Topic 04's batch loads, streaming, and external tables. The SQL examples are templates: replace `YOUR_PROJECT`, `YOUR_DATASET`, and region qualifiers with your own environment. No benchmark values are asserted here. Lab results must be measured in your project.

---

## 2. How BigQuery query costs arise

BigQuery separates storage from compute. Cost and performance depend on the pricing model, the amount and shape of data scanned, the work performed by execution stages, and contention for available compute.

### 2.1 Two major analysis pricing models

| Model | Main cost driver | What optimization means |
|---|---|---|
| On-demand analysis | Billable bytes processed, subject to the applicable pricing and free-tier rules | Reduce bytes billed and avoid unnecessary jobs |
| Capacity-based analysis | Provisioned/assigned capacity and its utilization over time, under the selected edition/reservation model | Improve throughput and slot efficiency; reduce wasted capacity and queueing |

A query that reads fewer bytes is usually beneficial under on-demand pricing. Under capacity pricing, fewer bytes can still reduce latency and free slots for other work, but it does not necessarily lower the fixed capacity charge immediately. Evaluate the cost model that actually applies to your project.

### 2.2 Metrics that must not be conflated

| Metric | Meaning | Where to inspect it | Important caveat |
|---|---|---|---|
| Dry-run estimate | Pre-execution estimate of bytes processed | Query job configuration, console estimate, or client dry run | Estimate only; it does not execute the query and may not predict runtime or every billing detail |
| `total_bytes_processed` | Bytes processed by the query job according to job statistics | `INFORMATION_SCHEMA.JOBS_BY_PROJECT` | Not the same as elapsed time or slot use |
| `total_bytes_billed` | Bytes used for billing calculations in job metadata | `INFORMATION_SCHEMA.JOBS_BY_PROJECT` | Can differ from processed bytes due to billing rules, minimums, cache behavior, and pricing model |
| `total_slot_ms` | Aggregate slot milliseconds consumed by a job | `INFORMATION_SCHEMA.JOBS_BY_PROJECT` | A resource-work metric, not wall-clock milliseconds |
| Execution latency | Elapsed time from job start to end | `start_time`, `end_time`, job details | Can include queueing and coordination; depends on concurrency and system conditions |
| Actual monetary cost | Charge recorded for the relevant billing account/SKU and period | Cloud Billing export and pricing configuration | Job metadata alone is not a final invoice; credits, editions, reservations, currency, and SKU rates matter |

For example, 60,000 slot-milliseconds means an aggregate 60 slot-seconds of work; it does **not** mean the query took 60 seconds. A job can consume many slots concurrently and finish in less wall-clock time, or wait in a queue despite modest work.

### 2.3 A useful mental model

1. **Scan reduction:** partition pruning, block pruning, column projection, and selective predicates reduce input read.
2. **Execution reduction:** pre-aggregation, sensible joins, avoiding row explosion, and efficient windowing reduce CPU, shuffle, and intermediate data.
3. **Reuse:** result cache and materialized views can avoid repeating work when their freshness and semantics meet requirements.
4. **Guardrails:** dry runs, `maximum_bytes_billed`, quotas, labels, reservations, budgets, and billing export prevent surprises and make ownership visible.
5. **Measurement:** compare equivalent queries with the same data, filters, selected columns, cache state, and pricing assumptions.

### 2.4 Simple on-demand estimate (not a quote)

For a rough estimate:

\[
\text{estimated analysis cost} \approx
\frac{\text{billable TiB}}{1\text{ TiB}} \times \text{applicable price per TiB}
\]

Use the current regional/pricing SKU and account terms. Do not hard-code a universal rate into a production cost model. Confirm whether a job is billed on demand or covered by capacity, and use billing export for realized cost.

---

## 3. Partitioning fundamentals and pruning

Partitioning divides a table into independently addressable partitions. BigQuery can eliminate partitions that cannot match a qualifying filter. Partitioning is most useful when common queries filter on a stable date/time or integer-range dimension.

### 3.1 Choose the partitioning type

| Type | Partition expression / pseudocolumn | Good fit | Main trade-off |
|---|---|---|---|
| Ingestion-time | `_PARTITIONTIME` or `_PARTITIONDATE` | Data is append-oriented, ingestion time is the reliable retention/reporting axis, or event-time fields are absent/untrusted | Late-arriving data is placed according to ingestion time, not event time |
| Time-unit column | `DATE` column, or `TIMESTAMP_TRUNC` / `DATETIME_TRUNC` expression | Reports repeatedly filter by business/event date; the timestamp/date is validated and populated | Bad or null timestamps, late data, and queries that omit the partition predicate need handling |
| Integer range | `RANGE_BUCKET(integer_column, GENERATE_ARRAY(start, end, interval))` | Stable integer ranges such as account/customer IDs or numeric buckets with range-filter workloads | Not suited to arbitrary high-cardinality equality lookup; values outside configured bounds go to `__UNPARTITIONED__` |

For event analytics, a common starting point is daily partitioning on `event_date` or `DATE(event_ts)` materialized as a `DATE` column. Choose it only if the majority of important queries include date ranges. If the workload routinely asks for a full history grouped by a non-date key, partitioning alone may not help that query.

### 3.2 Daily time-column partitioning

```sql
CREATE TABLE `YOUR_PROJECT.YOUR_DATASET.events_partitioned`
(
  event_id STRING NOT NULL,
  event_ts TIMESTAMP NOT NULL,
  event_date DATE NOT NULL,
  tenant_id STRING,
  user_id STRING,
  event_name STRING,
  country STRING,
  revenue NUMERIC,
  attributes JSON
)
PARTITION BY event_date
OPTIONS (
  require_partition_filter = TRUE,
  partition_expiration_days = 400,
  description = 'Event data partitioned by event_date; 400-day retention example'
);
```

The `event_date` field must agree with the intended business definition. For a production pipeline, derive or validate it from `event_ts` using a documented time zone convention. UTC is often the simplest storage convention; business-local reporting can derive a separate business date explicitly.

For hourly partitions, use them only when hourly filtering is common and each partition has enough data to justify the extra partition metadata/management overhead. For monthly or yearly partitions, use them only when the typical query granularity and retention policy align with that coarser grain. Smaller partition granularity does not automatically mean better performance.

### 3.3 Ingestion-time partitioning

```sql
CREATE TABLE `YOUR_PROJECT.YOUR_DATASET.events_ingestion_partitioned`
(
  event_id STRING,
  event_ts TIMESTAMP,
  tenant_id STRING,
  event_name STRING,
  revenue NUMERIC
)
PARTITION BY _PARTITIONDATE
OPTIONS (require_partition_filter = TRUE);
```

Filter with the pseudocolumn:

```sql
SELECT event_name, COUNT(*) AS event_count
FROM `YOUR_PROJECT.YOUR_DATASET.events_ingestion_partitioned`
WHERE _PARTITIONDATE >= DATE '2026-10-01'
  AND _PARTITIONDATE <  DATE '2026-10-08'
GROUP BY event_name;
```

Ingestion-time partitioning is useful for arrival-time operations and retention. It is not interchangeable with event-time partitioning. If events can arrive late, a query by event time may scan many ingestion partitions unless the table design and query also use arrival metadata.

### 3.4 Integer-range partitioning

```sql
CREATE TABLE `YOUR_PROJECT.YOUR_DATASET.customer_events_by_id_range`
(
  customer_id INT64,
  event_ts TIMESTAMP,
  event_name STRING,
  revenue NUMERIC
)
PARTITION BY RANGE_BUCKET(customer_id, GENERATE_ARRAY(0, 1000000, 10000));
```

This defines range boundaries from 0 to 1,000,000 with interval 10,000. The end boundary is exclusive. Values outside the configured range are stored in the special `__UNPARTITIONED__` partition. Use integer-range partitioning when query predicates commonly constrain meaningful ranges and the ranges distribute data reasonably; do not choose it solely because a numeric ID exists.

### 3.5 Partition pruning: predicate shape matters

Prefer a direct, type-compatible range predicate on the partitioning column:

```sql
SELECT event_name, COUNT(*) AS event_count
FROM `YOUR_PROJECT.YOUR_DATASET.events_partitioned`
WHERE event_date >= DATE '2026-10-01'
  AND event_date <  DATE '2026-11-01'
GROUP BY event_name;
```

Half-open ranges (`>= start AND < end`) are usually easy to reason about and avoid overlap between adjacent windows.

Avoid wrapping the partitioning column in a function when the expression prevents pruning:

```sql
-- Prefer this form:
WHERE event_date >= DATE '2026-10-01'
  AND event_date < DATE '2026-11-01'

-- Avoid assuming this form prunes identically:
WHERE FORMAT_DATE('%Y-%m', event_date) = '2026-10'
```

BigQuery can optimize some expressions, but do not depend on optimizer inference where a direct predicate is available. Check the dry-run estimate and execution details.

Use `AND` to combine the partition predicate with other filters. A condition such as `partition_date = ... OR country = ...` can prevent pruning because rows in other partitions may still satisfy the `OR`. Predicate order alone is not the key; semantics and optimizer-recognizable expressions are.

### 3.6 `require_partition_filter`

Set `require_partition_filter = TRUE` for shared tables where unrestricted scans are a recurring risk:

```sql
ALTER TABLE `YOUR_PROJECT.YOUR_DATASET.events_partitioned`
SET OPTIONS (require_partition_filter = TRUE);
```

This requires a predicate usable for partition elimination on every query referencing the table, including views/materialized views that reference it. A filter on a non-partition column alone is not enough. This is a useful safety rail, not a substitute for selecting a narrow range: `WHERE event_date >= DATE '2000-01-01'` technically filters partitions but may still scan nearly all history.

A qualifying predicate should reference only the partitioning column, for example:

```sql
WHERE event_date = DATE '2026-10-18'
  AND tenant_id = 'tenant_42'
```

The partition filter does not guarantee the query is cheap; inspect how many partitions remain.

### 3.7 Partition expiration and retention

Set expiration only when it matches legal, product, analytics, and recovery requirements:

```sql
ALTER TABLE `YOUR_PROJECT.YOUR_DATASET.events_partitioned`
SET OPTIONS (partition_expiration_days = 400);
```

- Time-unit partition expiration is measured from the partition boundary; expiration is asynchronous.
- Integer-range partitioned tables do not support partition expiration times.
- A table-level expiration can take precedence over partition expiration.
- Reducing the expiration period can cause older partitions to become eligible for deletion; verify before changing it.
- Retention is a data-lifecycle control, not a backup policy. Confirm downstream consumers, legal holds, replay requirements, and disaster recovery first.

### 3.8 Partition size and too many tiny partitions

There is no single partition size that is optimal for every workload. Partitioning has management overhead and can make sense only when there is sufficient data and queries can prune it. As a rule of thumb, avoid designs that create lots of tiny partitions, especially hourly partitions with little data. Consider daily partitions for normal event volumes, and coarser partitions if most partitions remain very small and queries often scan broad ranges. Validate using `INFORMATION_SCHEMA.PARTITIONS`, storage metrics, query history, and actual query patterns rather than treating a heuristic as a service limit.

---

## 4. Clustering fundamentals and block pruning

Clustering organizes table data into storage blocks according to the values of selected columns. BigQuery can use block metadata to skip blocks that cannot match a filter. Unlike partition pruning, block pruning is not a fixed, user-defined partition boundary, and exact scan savings are not guaranteed before execution.

### 4.1 Current clustering-column rule

For BigQuery clustered tables, you can specify **up to four clustering columns**. Clustering columns must be supported top-level, non-repeated fields of eligible types. The supported set includes common scalar types such as `STRING`, `INT64`, `NUMERIC`, `BOOL`, `DATE`, `DATETIME`, `TIMESTAMP`, and `GEOGRAPHY`; check the current official documentation for the complete supported type list and feature-specific exceptions.

Clustering-column order matters. For a table clustered by `(tenant_id, event_name, user_id)`, data is organized first by `tenant_id`, then `event_name`, then `user_id`. Filters on leading clustering columns generally have the strongest opportunity to prune blocks. Do not assume filtering only on the third column is as effective as filtering on the first.

### 4.2 Choose columns from observed filters

Use query logs to answer:

1. Which columns are filtered most frequently?
2. Which predicates are selective and commonly present together?
3. Is the column type supported for clustering?
4. Is the column stable enough to be useful across many queries?
5. Does the data distribution have enough locality to create skippable blocks?
6. Will clustering maintenance be worth it given update/streaming patterns and query frequency?

Example: if most reports filter by `tenant_id`, then by `event_name`, and then sometimes by `user_id`, a candidate is:

```sql
CLUSTER BY tenant_id, event_name, user_id
```

But if most queries filter on `country` and `event_name`, the candidate should reflect those actual predicates. High cardinality alone is not a sufficient selection rule; choose keys based on filter/aggregation workload and data distribution.

### 4.3 Clustered table example

```sql
CREATE TABLE `YOUR_PROJECT.YOUR_DATASET.events_partitioned_clustered`
(
  event_id STRING NOT NULL,
  event_ts TIMESTAMP NOT NULL,
  event_date DATE NOT NULL,
  tenant_id STRING,
  user_id STRING,
  event_name STRING,
  country STRING,
  revenue NUMERIC,
  attributes JSON
)
PARTITION BY event_date
CLUSTER BY tenant_id, event_name, user_id
OPTIONS (
  require_partition_filter = TRUE,
  partition_expiration_days = 400
);
```

Partitioning narrows the date range; clustering may then prune blocks within the remaining partitions. This combination is often useful for multi-tenant event data where queries filter by date and tenant/event type. It is not automatically the best design if queries rarely filter by date or if clustered fields are seldom filtered.

### 4.4 Automatic reclustering and write patterns

BigQuery can automatically recluster clustered data in the background as data changes. For partitioned tables, reclustering is scoped within partitions. This helps maintain clustering quality over time, but it does not mean every new row is instantly perfectly ordered, nor does it guarantee a fixed reduction in bytes scanned. Append-heavy ingestion, streaming writes, frequent updates, and skew can affect observed pruning.

### 4.5 Clustering decision table

| Workload | Candidate design | Validate |
|---|---|---|
| Daily dashboards filtered by date and tenant | Partition by date, cluster by tenant | Bytes processed/billed and latency for representative dashboard queries |
| Frequent lookup-like filters on a few tenant IDs in large partitions | Partition by date if date is commonly constrained; cluster by tenant ID | Actual block pruning; do not assume BigQuery behaves like a row-store index |
| Full-table scans and global aggregates | Clustering may add little scan reduction | Slot-ms, latency, and total cost before/after |
| Many tiny daily partitions | Consider coarser time partitioning and/or a different design | Partition metadata, storage volume per partition, and query range patterns |
| Updates spread across many old partitions | Revisit ingestion and DML strategy; clustering alone is not the fix | Mutated bytes, job history, and data freshness requirements |

---

## 5. Combined physical table-design strategies

### 5.1 A decision workflow

Use this order rather than choosing physical design from intuition alone.

1. **Classify queries:** list the top 5–10 production queries by frequency, bytes processed/billed, latency, and business importance.
2. **Find the dominant selective filter:** date/time, tenant, account, event type, or a numeric range.
3. **Partition only if pruning is likely:** the partition key should be filtered by important queries and have sensible granularity.
4. **Cluster within the partition:** use up to four supported columns ordered by common filtering patterns.
5. **Account for writes:** event-time backfills, late data, streaming, frequent `MERGE`, and mutation patterns may change maintenance cost.
6. **Set safety rails:** require partition filters, cap bytes billed for ad-hoc workloads, and set quotas where appropriate.
7. **Measure a representative workload:** same data, selected columns, predicates, query semantics, and cache policy.
8. **Review continuously:** data growth and workload drift can make an old physical design suboptimal.

### 5.2 A sample event workload

Assume a hypothetical event table has:

- `event_id STRING`
- `event_ts TIMESTAMP`
- `event_date DATE`
- `tenant_id STRING`
- `user_id STRING`
- `event_name STRING`
- `country STRING`
- `revenue NUMERIC`
- `attributes JSON`

Typical queries:

| Query pattern | Design hypothesis | Reason |
|---|---|---|
| Daily tenant event counts | Partition by `event_date`; cluster by `tenant_id`, `event_name` | Date partition pruning, then tenant/event block pruning |
| One tenant's last 7 days | Same design | Selective date and tenant predicates |
| Full-history top countries | Partitioning may not reduce this query if all dates are needed | Optimize selected columns and aggregate work; test whether clustering helps |
| Event-time retention and late arrivals | Partition on validated event date; track ingestion timestamp separately | Retention follows event time, while ingestion metadata supports late-data diagnosis |
| Queries mostly filter by account ID and never date | Reconsider date partitioning alone; maybe integer range partitioning only if range predicates suit the workload | Partitioning by a column nobody filters gives little pruning |

### 5.3 Partition filter + clustering example

```sql
SELECT
  event_name,
  COUNT(*) AS events,
  COUNT(DISTINCT user_id) AS exact_users
FROM `YOUR_PROJECT.YOUR_DATASET.events_partitioned_clustered`
WHERE event_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
  AND event_date < CURRENT_DATE()
  AND tenant_id = 'tenant_42'
GROUP BY event_name;
```

This uses the date predicate for partition pruning and tenant filter for potential block pruning. `CURRENT_DATE()` makes the query non-deterministic for result-cache purposes; use literal dates when benchmarking or when the business definition calls for a fixed interval. Also note that `COUNT(DISTINCT ...)` can be more expensive than approximate counting; change it only if approximate results satisfy the business requirement.

---

## 6. Query-writing techniques to reduce scanning and execution work

### 6.1 Select only the columns you need

BigQuery is columnar. Under on-demand pricing, selected columns matter because unnecessary columns can increase bytes processed. Avoid `SELECT *` in production queries on wide tables.

```sql
-- Avoid for wide production tables:
SELECT *
FROM `YOUR_PROJECT.YOUR_DATASET.events_partitioned`
WHERE event_date = DATE '2026-10-18';

-- Prefer:
SELECT event_id, event_ts, tenant_id, event_name, revenue
FROM `YOUR_PROJECT.YOUR_DATASET.events_partitioned`
WHERE event_date = DATE '2026-10-18';
```

`SELECT * EXCEPT (...)` can be useful for exploratory analysis, but an explicit column list is usually clearer for durable data contracts.

### 6.2 Filter early where semantics permit

Filter rows before joins, unnests, expensive window calculations, or wide aggregations when the filter does not change the intended result. BigQuery's optimizer can push down predicates in many cases; explicit, simple predicates also make pruning easier to inspect.

```sql
WITH recent_events AS (
  SELECT tenant_id, user_id, event_name, event_ts
  FROM `YOUR_PROJECT.YOUR_DATASET.events_partitioned`
  WHERE event_date >= DATE '2026-10-01'
    AND event_date < DATE '2026-11-01'
    AND tenant_id = 'tenant_42'
)
SELECT event_name, COUNT(*) AS events
FROM recent_events
GROUP BY event_name;
```

A CTE is a readability construct, not a promise that BigQuery materializes or executes it exactly once. Inspect the execution graph if repeated subqueries are expensive.

### 6.3 Why `LIMIT` alone does not reduce bytes billed

```sql
SELECT event_id, event_ts, attributes
FROM `YOUR_PROJECT.YOUR_DATASET.events_partitioned`
WHERE event_date >= DATE '2026-01-01'
LIMIT 100;
```

The engine may still need to scan the relevant columns and partitions to produce qualifying rows. `LIMIT` limits output rows, not the amount of input data read in general. Combine it with selective partition and column filters; use it for output control, not as a cost guarantee.

### 6.4 Approximate aggregation

Use approximate functions only when a probabilistic estimate meets the product's error tolerance:

```sql
SELECT
  event_name,
  APPROX_COUNT_DISTINCT(user_id) AS estimated_unique_users
FROM `YOUR_PROJECT.YOUR_DATASET.events_partitioned`
WHERE event_date >= DATE '2026-10-01'
  AND event_date < DATE '2026-11-01'
GROUP BY event_name;
```

`APPROX_COUNT_DISTINCT`, `APPROX_QUANTILES`, and related functions can reduce the cost of exact aggregation for suitable large datasets, but the actual scan and performance benefit is workload-dependent. They do not eliminate the need to scan input columns, and the output is approximate. Compare accuracy and latency against exact aggregation on a representative sample before adopting it for financial, compliance, or billing calculations.

### 6.5 Avoid row explosion

`UNNEST` and cross joins can multiply rows. If an array has multiple elements per event, unnest only the fields and rows required. Aggregate before joining when it preserves the intended grain.

```sql
-- Risk: a large cartesian product if both sides are large and unrelated.
SELECT *
FROM `YOUR_PROJECT.YOUR_DATASET.events_partitioned` e
CROSS JOIN `YOUR_PROJECT.YOUR_DATASET.large_dimension` d;
```

A cross join is appropriate only when the full product is intended or the input is deliberately tiny. For a true relationship, use the correct join keys. Review row counts before and after each stage and look for sudden multiplication.

### 6.6 Join order, join strategy, and pre-aggregation

BigQuery chooses join strategies, but query shape and input sizes still matter:

- Filter each side to the relevant date/tenant and columns before joining where semantics allow.
- Aggregate a very large fact table to the required grain before joining to a dimension if the aggregation preserves correctness.
- Keep join keys type-compatible and avoid functions on keys where they prevent efficient matching.
- Avoid many-to-many joins unless intended; verify uniqueness assumptions on dimension keys.
- Broadcast joins can be efficient when one input is small; large inputs may require shuffle/hash strategies. Do not force a strategy without evidence.
- Skewed join keys (for example, one `tenant_id` owning a large fraction of rows) can create uneven stage work. Inspect execution details, stage input/output, shuffle, and `JOBS_TIMELINE`.

Example of pre-aggregation:

```sql
WITH tenant_daily AS (
  SELECT event_date, tenant_id, COUNT(*) AS event_count
  FROM `YOUR_PROJECT.YOUR_DATASET.events_partitioned`
  WHERE event_date >= DATE '2026-10-01'
    AND event_date < DATE '2026-11-01'
  GROUP BY event_date, tenant_id
)
SELECT d.segment, SUM(t.event_count) AS event_count
FROM tenant_daily t
JOIN `YOUR_PROJECT.YOUR_DATASET.tenant_dimension` d
  USING (tenant_id)
GROUP BY d.segment;
```

This is valid only if the report needs event counts at segment level and the dimension has the expected one-row-per-tenant grain. If the dimension contains multiple rows per tenant, the join can multiply counts.

### 6.7 `QUALIFY` and window functions

`QUALIFY` filters rows after window-function evaluation. It can simplify top-N-per-group queries, but it does not make the window computation free.

```sql
SELECT tenant_id, event_id, event_ts
FROM `YOUR_PROJECT.YOUR_DATASET.events_partitioned`
WHERE event_date >= DATE '2026-10-01'
  AND event_date < DATE '2026-11-01'
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY tenant_id
  ORDER BY event_ts DESC
) <= 3;
```

To reduce work, restrict the date range and columns before computing the window when business semantics allow. Partitioning the table physically by date is different from `PARTITION BY` inside `OVER (...)`: the former is storage layout; the latter defines analytic window groups.

### 6.8 Dry runs and `maximum_bytes_billed`

A dry run validates the query and estimates bytes processed without running the query. It is ideal for preflight checks, but it does not provide measured latency, slot use, cache behavior, or actual billed cost.

Python client example:

```python
from google.cloud import bigquery

client = bigquery.Client(project="YOUR_PROJECT")
sql = """
SELECT event_name, COUNT(*) AS events
FROM `YOUR_PROJECT.YOUR_DATASET.events_partitioned`
WHERE event_date >= DATE '2026-10-01'
  AND event_date < DATE '2026-11-01'
GROUP BY event_name
"""

job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
job = client.query(sql, job_config=job_config)
print(f"Estimated bytes processed: {job.total_bytes_processed:,}")
```

Use `maximum_bytes_billed` as a hard per-query scan guard for applicable on-demand queries:

```python
from google.cloud import bigquery

client = bigquery.Client(project="YOUR_PROJECT")
job_config = bigquery.QueryJobConfig(
    maximum_bytes_billed=50 * 1024**3,  # 50 GiB; example guardrail
    use_query_cache=False,
    labels={"workload": "ad_hoc", "cost_center": "analytics"},
)
job = client.query(sql, job_config=job_config)
job.result()
print(job.total_bytes_processed, job.total_bytes_billed, job.total_slot_ms)
```

If the estimated bytes to be billed exceed the configured maximum, BigQuery rejects the query rather than running it. A limit that is too low can reject legitimate queries; calibrate it to workload tiers. For clustered tables, pre-execution byte estimates used by this guard can be conservative upper bounds, so a query can be rejected even when its eventual billed bytes might have been lower after block pruning. `maximum_bytes_billed` is not a general cap on reservation consumption, storage charges, or every other possible cost category. Confirm the applicable behavior for your pricing model and query type.

### 6.9 Query labels

Use labels to group jobs by application, team, environment, or cost center. Labels improve analysis; they do not themselves enforce a budget or alter query semantics.

```python
job_config = bigquery.QueryJobConfig(
    labels={
        "team": "growth",
        "environment": "production",
        "workload": "daily_dashboard",
    }
)
```

Label keys and values must follow BigQuery's label restrictions. Standardize them centrally so the billing export and job metadata can be joined consistently.

---

## 7. Materialized views, caching, and acceleration trade-offs

These mechanisms solve different problems. Evaluate them separately.

### 7.1 Result cache

BigQuery may reuse results from an identical query for a limited period (typically up to 24 hours, subject to invalidation and eligibility rules). Cache hits can reduce query latency and analysis charges. The cache is best-effort, not a guaranteed application cache.

Common reasons a query may not use cached results include changed source data, changed query text, non-deterministic functions, wildcard table references, destination-table configuration, and other eligibility limitations. Check `cache_hit` in job metadata. When benchmarking table designs, set `use_query_cache = FALSE` for the measured runs; otherwise the second run may be a cache hit rather than a physical-design improvement.

### 7.2 Materialized views

Materialized views persist precomputed query results and can reduce repeated aggregation work when the query pattern is supported and the optimizer can use the materialized view. They have refresh, storage, and maintenance trade-offs. Incremental refresh support and query rewrite eligibility depend on SQL shape and product rules; do not assume every query can be accelerated.

```sql
CREATE MATERIALIZED VIEW `YOUR_PROJECT.YOUR_DATASET.mv_daily_tenant_events`
AS
SELECT
  event_date,
  tenant_id,
  event_name,
  COUNT(*) AS event_count,
  SUM(revenue) AS revenue_total
FROM `YOUR_PROJECT.YOUR_DATASET.events_source`
GROUP BY event_date, tenant_id, event_name;
```

This example uses the lab's non-partition-filter-enforced source table so the view definition is not blocked by the lab's `require_partition_filter` setting. In production, if the source is partitioned and requires a partition filter, verify whether the materialized-view definition and every consumer query satisfy the requirement; consider a compatible partitioned materialized-view design where supported. Before using this example in production, confirm the base-table and materialized-view restrictions in the current documentation, including partitioning/refresh requirements and supported SQL. Compare repeated aggregation queries before and after, with cache state controlled, and include refresh/maintenance and storage in the cost evaluation.

### 7.3 BI Engine

BI Engine is an in-memory acceleration service for supported BigQuery analytics and BI workloads. It can improve dashboard latency, especially for repeated interactive queries, but it is not a universal replacement for partitioning, clustering, query optimization, or capacity planning. Consider it when latency SLOs and query frequency justify the reservation/capacity cost. Validate dashboard compatibility, cache coverage, concurrency, and actual latency.

### 7.4 Choose the reuse mechanism

| Mechanism | Best fit | Limitations to include in the decision |
|---|---|---|
| Result cache | Repeated identical query, source data unchanged, cache eligible | Best-effort and invalidated; not a correctness or freshness guarantee |
| Materialized view | Repeated supported aggregation/query pattern over stable sources | Refresh/maintenance, storage, supported SQL, query rewrite eligibility |
| BI Engine | Interactive BI latency and concurrency requirements | Capacity cost, supported workload/query behavior, memory/cache coverage |
| Persisted summary table | Custom refresh, complex transformation, or explicit data contract | Pipeline orchestration, freshness, backfill and reconciliation ownership |

---

## 8. DML, `MERGE`, joins, and analytical query optimization

### 8.1 Append-only versus mutation-heavy data

Append-only event data is often operationally simpler and can avoid repeated scans/mutations of historical partitions. If events are immutable, prefer batch appends or load jobs where the ingestion SLA permits. Keep a separate correction/deduplication strategy for late or duplicate events.

For mutable entities, decide whether the use case needs row-level updates or whether a new version/event is more appropriate. Frequent `UPDATE`, `DELETE`, or `MERGE` operations can add processing cost and complexity. Exact DML billing behavior depends on the table type, partitioning, statement, and pricing model; consult current BigQuery DML pricing rules rather than applying a universal formula.

### 8.2 Reduce the scope of `MERGE`

```sql
MERGE `YOUR_PROJECT.YOUR_DATASET.customer_current` AS T
USING (
  SELECT customer_id, updated_at, status
  FROM `YOUR_PROJECT.YOUR_DATASET.customer_staging`
  WHERE DATE(updated_at) >= DATE '2026-10-01'
) AS S
ON T.customer_id = S.customer_id
WHEN MATCHED AND S.updated_at > T.updated_at THEN
  UPDATE SET status = S.status, updated_at = S.updated_at
WHEN NOT MATCHED THEN
  INSERT (customer_id, updated_at, status)
  VALUES (S.customer_id, S.updated_at, S.status);
```

This is an illustrative pattern, not a universal cost-optimized `MERGE`. If the target is partitioned, include target partition constraints when logically safe and supported by the join/update semantics. Filtering only the source does not guarantee the target scan is limited. Avoid adding a target date predicate that would incorrectly turn an existing key into a false non-match and insert duplicates. Test correctness with late-arriving updates and keys whose partition changes.

### 8.3 Deduplicate before merge

If staging can contain multiple rows per key, reduce it to the intended latest record first:

```sql
CREATE OR REPLACE TABLE `YOUR_PROJECT.YOUR_DATASET.customer_staging_deduped` AS
SELECT customer_id, updated_at, status
FROM `YOUR_PROJECT.YOUR_DATASET.customer_staging`
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY customer_id
  ORDER BY updated_at DESC
) = 1;
```

Define tie-breaking behavior if `updated_at` can tie. Use deterministic secondary keys. This can reduce merge input and prevent ambiguous multiple matches, but the deduplication query itself costs compute and should be measured.

### 8.4 Partition-aware ingestion: handoff to Topic 04

Topic 04 covers batch loads, streaming, and external tables. Bring these design questions into ingestion:

- Is the partition key derived from event time or ingestion time?
- How are late-arriving events handled when their event date is old?
- Does the load job write to a narrow date range or append into a broad destination?
- Are duplicate/replayed events possible, and how are they identified?
- Will streaming ingestion temporarily affect cache eligibility or write layout?
- Do external tables provide the needed pruning/metadata behavior, or would a native table be more appropriate for repeated analytics?
- What retention and replay window does the pipeline need?

A good table design must match the data arrival contract. Partitioning on event time is valuable only if event dates are reliable and the pipeline can backfill/correct the appropriate partitions safely.

---

## 9. Cost monitoring, budgets, quotas, and governance

No single control prevents every type of cost. Use defense in depth.

### 9.1 Guardrail stack

| Control | Purpose | Limitation |
|---|---|---|
| `require_partition_filter` | Reject queries that omit a partition-eliminating predicate | A very broad filter can still scan most partitions |
| `maximum_bytes_billed` | Reject applicable on-demand queries exceeding a per-query byte threshold | Not a global budget or a general capacity-cost limit |
| Custom quotas / query limits | Limit usage for a user/project/workload where supported | Limits and availability vary; configure according to current product rules |
| Reservations / assignments | Allocate and isolate capacity across teams/workloads | Reservations manage compute capacity, not an automatic hard currency cap |
| Labels | Attribute jobs to teams/apps/cost centers | Labels are metadata, not enforcement |
| Cloud Billing budget and alerts | Alert owners when spend reaches configured thresholds | A budget alert is not a hard spend cap by itself |
| Billing export | Reconcile actual SKU-level cost and trends | Export is delayed and must be joined to ownership metadata |
| IAM and workload separation | Restrict who can launch expensive jobs and where | Requires ongoing role review and clear ownership |

### 9.2 Establish measurable policy

A useful production policy defines:

- A scan ceiling for interactive analyst queries, with separate tiers for approved batch workloads.
- Mandatory partition filters for large shared partitioned tables.
- Labels for team, environment, workload, and cost center.
- Alerts on daily/monthly spend and unusual increases.
- Review thresholds for repeated high bytes billed, high slot-ms, long runtime, or errors.
- Reservation ownership and isolation where teams have conflicting concurrency/SLO needs.
- An exception process for legitimate full-history jobs, including owner, reason, and expected scan.

Set thresholds from historical distributions and business SLOs, not arbitrary numbers copied from a tutorial.

### 9.3 Billing export versus job metadata

Use `INFORMATION_SCHEMA` to find query behavior and identify candidate jobs. Use Cloud Billing export to reconcile realized costs at billing SKU granularity. They answer different questions: job metadata is excellent for diagnosing scans and slot use; billing export is the authoritative place to analyze the charges recorded on the billing account. A job's `total_bytes_billed` is not by itself a complete invoice calculation.

### 9.4 Quotas and reservations

Custom quotas and limits change over time and differ by feature, region, and organization policy. Verify the current quota names and supported scopes in the Cloud Console and official documentation before rollout. For multi-team workloads, reservation assignments can improve predictability and isolate critical dashboards from ad-hoc analysis, but they do not eliminate queueing if demand exceeds available slots. Use slot usage, runnable units, queueing, and latency data to size reservations.

---

## 10. Advanced workload analysis and tuning

### 10.1 Top 20 expensive query jobs this month

Run this query in the region containing the jobs. Replace `region-us` with the correct region qualifier; the `INFORMATION_SCHEMA` region must match the dataset/job location. Access to project-level job metadata requires appropriate permissions.

```sql
-- Top 20 completed query jobs by billed bytes in the current UTC calendar month.
-- Use the correct region-us / region-eu / region-asia-* qualifier.
SELECT
  creation_time,
  project_id,
  user_email,
  job_id,
  statement_type,
  total_bytes_processed,
  total_bytes_billed,
  total_slot_ms,
  TIMESTAMP_DIFF(end_time, start_time, MILLISECOND) AS elapsed_ms,
  cache_hit,
  reservation_id,
  labels,
  error_result.reason AS error_reason,
  query
FROM `YOUR_PROJECT.region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE creation_time >= TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), MONTH)
  AND creation_time < TIMESTAMP_ADD(
    TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), MONTH), INTERVAL 1 MONTH
  )
  AND job_type = 'QUERY'
  AND state = 'DONE'
  AND (statement_type IS NULL OR statement_type != 'SCRIPT')
  AND query IS NOT NULL
ORDER BY total_bytes_billed DESC NULLS LAST
LIMIT 20;
```

Notes:

- This ranks jobs by `total_bytes_billed`; a separate ranking by `total_slot_ms` finds compute-heavy work that may not be the largest scan.
- `query` can contain sensitive SQL text. Restrict report access and consider hashing/omitting it in shared dashboards.
- The metadata view includes jobs visible to the querying principal under its permissions and retains job history for a limited period (currently up to 180 days). The report is not guaranteed to represent every billing line item. Excluding `SCRIPT` parent rows avoids double-counting totals already represented by child jobs.
- For failed jobs, byte fields may be null or zero; include them for failure analysis separately.
- For on-demand billing estimates, apply the actual SKU/rate and pricing context. For capacity, interpret slot use against reservation costs and utilization.

### 10.2 Expensive queries by slot work

```sql
SELECT
  user_email,
  job_id,
  creation_time,
  total_slot_ms,
  total_bytes_processed,
  total_bytes_billed,
  TIMESTAMP_DIFF(end_time, start_time, MILLISECOND) AS elapsed_ms,
  cache_hit,
  query
FROM `YOUR_PROJECT.region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND job_type = 'QUERY'
  AND state = 'DONE'
  AND (statement_type IS NULL OR statement_type != 'SCRIPT')
  AND total_slot_ms IS NOT NULL
ORDER BY total_slot_ms DESC
LIMIT 20;
```

A high slot-ms job may be compute-heavy, shuffle-heavy, or processing many rows even when bytes billed are modest. Inspect the execution graph, stage input/output, shuffle bytes, skew, and repeated stages. Optimize the stage doing the most work rather than assuming every slow query is a scan problem.

### 10.3 `JOBS_TIMELINE`: concurrency and skew signals

`JOBS_TIMELINE` / `JOBS_TIMELINE_BY_PROJECT` provides time-sliced job metadata, generally one row per job per one-second interval. It can include pending and running states, so do not label every row as completed execution time. The view is partitioned by `job_creation_time`; include a bounded predicate on that column as well as the desired `period_start` window. Use a narrow time range and aggregate to job or minute before analyzing.

```sql
-- Example: per-job slot-ms over the recent hour, considering jobs created in the last day.
-- Widen the job_creation_time window if you need to include older, long-running jobs.
SELECT
  job_id,
  COUNT(*) AS time_slices_observed,
  SUM(period_slot_ms) AS summed_period_slot_ms,
  MAX(period_slot_ms) AS max_period_slot_ms
FROM `YOUR_PROJECT.region-us.INFORMATION_SCHEMA.JOBS_TIMELINE_BY_PROJECT`
WHERE job_creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
  AND job_creation_time < CURRENT_TIMESTAMP()
  AND period_start >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
  AND period_start < CURRENT_TIMESTAMP()
  AND (statement_type IS NULL OR statement_type != 'SCRIPT')
GROUP BY job_id
ORDER BY summed_period_slot_ms DESC
LIMIT 20;
```

Check the current schema and semantics before using timeline metrics for capacity planning. One row represents a time slice; summing time-slice fields is not the same as elapsed latency. `JOBS_TIMELINE` is partitioned on `job_creation_time`, so bound that column to control metadata scanning while independently bounding `period_start` to the time interval of interest. Use `JOBS_BY_PROJECT` for job-level totals and `JOBS_TIMELINE` for time-varying resource pressure. Permission requirements may be more restrictive than ordinary job history.

### 10.4 Inspect partition metadata

```sql
SELECT
  table_name,
  partition_id,
  total_rows,
  total_logical_bytes,
  last_modified_time
FROM `YOUR_PROJECT.YOUR_DATASET.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name IN (
  'events_partitioned',
  'events_partitioned_clustered'
)
ORDER BY table_name, partition_id;
```

Use this to identify tiny/empty partitions, unexpected retention, uneven data volumes, or late data concentrated in particular periods. Metadata views and column availability can evolve; confirm the current schema for the region and dataset.

### 10.5 Search indexes and vector indexes: awareness, not a default fix

**Search indexes** can accelerate supported search predicates, especially search-oriented operations over large string/JSON data. They introduce index storage/maintenance considerations and only help eligible query patterns. They are not a substitute for partitioning when the workload is a date-range analytical scan. Validate supported operators, index coverage, freshness, and cost with the current search-index documentation.

**Vector indexes** support approximate nearest-neighbor search for supported vector workloads. They have build/maintenance, storage, freshness, and recall/latency trade-offs; supported index types and query syntax can change. Use them for embedding similarity retrieval when the retrieval workload justifies them—not as a general-purpose optimization for relational filters or aggregations. Compare recall, latency, index coverage, and total cost against a baseline.

### 10.6 Table snapshots and recovery

A BigQuery table snapshot is a read-only, point-in-time representation of a table, typically storage-efficient when it shares unchanged data with the source. Example:

```sql
CREATE SNAPSHOT TABLE `YOUR_PROJECT.YOUR_DATASET.events_snapshot_20261019`
CLONE `YOUR_PROJECT.YOUR_DATASET.events_partitioned`
OPTIONS (
  expiration_timestamp = TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
);
```

Before using this syntax in production, verify current snapshot limits and options, source/destination location rules, and retention policies. Snapshots can help protect against accidental table changes and support point-in-time recovery within their configured lifecycle. They are **not a complete disaster-recovery strategy**: they do not independently guarantee cross-region recovery, protection from project/account compromise, immutable retention, restoration testing, pipeline/code recovery, or recovery of every related dependency. Define RPO/RTO, cross-region or cross-project needs, access separation, retention, and restore drills.

---

## 11. Hands-on exercises

All labs are designed for a disposable dataset. Use a development project, set a budget alert, label jobs, and delete lab tables when finished. Avoid running the wide scans in a production project.

### 11.1 Lab setup and reproducible sample dataset

**Folder layout**

```text
experiments/
└── 03_partition_cluster/
    ├── README.md
    ├── 01_create_comparison_tables.sql
    ├── 02_run_comparable_queries.sql
    ├── 03_partition_guardrails.sql
    ├── 04_materialized_view.sql
    ├── 05_top20_expensive_queries.sql
    └── results-template.csv
```

Create a dataset in a single location (for example `US`) and keep the source and tables in that same location. A reproducible option is to generate a deterministic sample with a fixed seed outside BigQuery, load it once to a native table, and create the three comparison tables from that same source. This avoids relying on public dataset availability or changes.

For a lightweight SQL-only lab, use a bounded generated sample. The query below creates 100,000 rows deterministically; change the count only after reviewing the estimated work and project guardrails.

```sql
CREATE SCHEMA IF NOT EXISTS `YOUR_PROJECT.bq_cost_lab`
OPTIONS(location = 'US');

CREATE OR REPLACE TABLE `YOUR_PROJECT.bq_cost_lab.events_source` AS
WITH generated AS (
  SELECT
    n,
    TIMESTAMP_ADD(
      TIMESTAMP '2026-01-01 00:00:00+00',
      INTERVAL MOD(n * 37, 365 * 24 * 60) MINUTE
    ) AS event_ts
  FROM UNNEST(GENERATE_ARRAY(1, 100000)) AS n
)
SELECT
  FORMAT('evt-%012d', n) AS event_id,
  event_ts,
  DATE(event_ts) AS event_date,
  FORMAT('tenant-%03d', MOD(n, 100)) AS tenant_id,
  FORMAT('user-%06d', MOD(n * 13, 20000)) AS user_id,
  CASE MOD(n, 5)
    WHEN 0 THEN 'page_view'
    WHEN 1 THEN 'purchase'
    WHEN 2 THEN 'search'
    WHEN 3 THEN 'add_to_cart'
    ELSE 'logout'
  END AS event_name,
  CASE MOD(n, 4)
    WHEN 0 THEN 'US'
    WHEN 1 THEN 'IN'
    WHEN 2 THEN 'GB'
    ELSE 'DE'
  END AS country,
  CAST(MOD(n * 17, 100000) AS NUMERIC) / 100 AS revenue,
  JSON_OBJECT('source', 'lab', 'sequence', n) AS attributes
FROM generated;
```

This synthetic data is for reproducibility, not a realistic benchmark. It has intentionally patterned distributions and does not represent real-world skew, compression, or query performance. Record the exact row count, table size, region, and creation timestamp.

### 11.2 Exercise 1 — Create equivalent physical designs

**Prerequisites:** Complete lab setup; use a disposable project/dataset in one location, with a budget alert and permissions to create tables.

All three tables derive from the same source and schema. The only intended difference is physical design.

```sql
CREATE OR REPLACE TABLE `YOUR_PROJECT.bq_cost_lab.events_unpartitioned` AS
SELECT * FROM `YOUR_PROJECT.bq_cost_lab.events_source`;

CREATE OR REPLACE TABLE `YOUR_PROJECT.bq_cost_lab.events_partitioned`
PARTITION BY event_date AS
SELECT * FROM `YOUR_PROJECT.bq_cost_lab.events_source`;

CREATE OR REPLACE TABLE `YOUR_PROJECT.bq_cost_lab.events_partitioned_clustered`
PARTITION BY event_date
CLUSTER BY tenant_id, event_name, user_id AS
SELECT * FROM `YOUR_PROJECT.bq_cost_lab.events_source`;
```

**Expected observations:** all three tables should contain the same rows and columns; only the latter two have daily partitioning, and the third also has clustering. The small synthetic data can make scan differences negligible. **Validation:** compare `COUNT(*)`, schema, partitioning/clustering metadata, and `INFORMATION_SCHEMA.PARTITIONS`; record table sizes and creation times. If current service rules reject a DDL combination, record the exact error and consult the current DDL documentation rather than silently changing the design. **Cleanup:** use Section 11.9 after completing all exercises; keep the tables until all comparisons are finished.

### 11.3 Exercise 2 — Compare equivalent queries

**Prerequisites:** Exercise 1 completed and row counts/schema verified; access to dry-run estimates and query job metadata.

Run a semantically equivalent query against each table. The unpartitioned table can use the same date predicate even though it has no partition pruning.

```sql
-- Unpartitioned
SELECT event_name, COUNT(*) AS event_count, SUM(revenue) AS revenue_total
FROM `YOUR_PROJECT.bq_cost_lab.events_unpartitioned`
WHERE event_date >= DATE '2026-03-01'
  AND event_date < DATE '2026-04-01'
  AND tenant_id = 'tenant-042'
GROUP BY event_name;

-- Partitioned
SELECT event_name, COUNT(*) AS event_count, SUM(revenue) AS revenue_total
FROM `YOUR_PROJECT.bq_cost_lab.events_partitioned`
WHERE event_date >= DATE '2026-03-01'
  AND event_date < DATE '2026-04-01'
  AND tenant_id = 'tenant-042'
GROUP BY event_name;

-- Partitioned + clustered
SELECT event_name, COUNT(*) AS event_count, SUM(revenue) AS revenue_total
FROM `YOUR_PROJECT.bq_cost_lab.events_partitioned_clustered`
WHERE event_date >= DATE '2026-03-01'
  AND event_date < DATE '2026-04-01'
  AND tenant_id = 'tenant-042'
GROUP BY event_name;
```

For each table:

1. Run a dry run first and record the estimate.
2. Run once with query cache disabled and record job metrics.
3. Do not compare a cache hit against a non-cache hit.
4. Repeat a few times only if the lab budget allows; record variability instead of cherry-picking the fastest run.
5. Inspect the execution graph and bytes processed/billed, slot-ms, and elapsed time.
6. Keep query text, selected columns, filters, location, and result semantics comparable.

Expected qualitative outcome: the partitioned table may process less data if the date predicate prunes partitions. The clustered table may further prune blocks for `tenant_id`, but exact benefit depends on data volume, clustering quality, and optimizer behavior. For a small synthetic table, the measured difference may be negligible or obscured by minimum billing, fixed overhead, or metadata. **Validation:** confirm equivalent results before comparing `total_bytes_processed`, `total_bytes_billed`, `total_slot_ms`, elapsed time, cache status, and execution graph. **Cleanup:** retain tables for Exercises 3–5, then use Section 11.9. **Do not infer a production benefit from this small sample alone.**

### 11.4 Exercise 3 — Test `require_partition_filter`

**Prerequisites:** Exercise 1 completed; permission to alter the lab table and submit query jobs.

```sql
ALTER TABLE `YOUR_PROJECT.bq_cost_lab.events_partitioned`
SET OPTIONS (require_partition_filter = TRUE);
```

Run a query without a date predicate:

```sql
-- Expected to be rejected because there is no qualifying partition filter.
SELECT COUNT(*)
FROM `YOUR_PROJECT.bq_cost_lab.events_partitioned`;
```

Then run with a qualifying predicate:

```sql
SELECT COUNT(*)
FROM `YOUR_PROJECT.bq_cost_lab.events_partitioned`
WHERE event_date = DATE '2026-03-01';
```

Record the error message and success. A filter on `tenant_id` alone should not satisfy the partition-filter requirement. A very broad date range can satisfy the rule but still be expensive. **Validation:** retain the rejected query error and the successful query job ID/metrics. **Cleanup:** no separate cleanup is required; the table option is reset or the table dropped in Section 11.9.

### 11.5 Exercise 4 — Test `maximum_bytes_billed`

**Prerequisites:** Python environment with `google-cloud-bigquery`, Application Default Credentials, permission to create query jobs, and the disposable lab table from Exercise 1.

In Python with `google-cloud-bigquery` installed and Application Default Credentials configured:

```python
from google.cloud import bigquery
from google.api_core.exceptions import BadRequest

client = bigquery.Client(project="YOUR_PROJECT")
sql = """
SELECT event_id, event_ts, attributes
FROM `YOUR_PROJECT.bq_cost_lab.events_unpartitioned`
"""

# Choose a deliberately small threshold only after checking a dry-run estimate.
dry_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
estimate_job = client.query(sql, job_config=dry_config)
estimated = estimate_job.total_bytes_processed or 0
print(f"Estimated bytes processed: {estimated:,}")

guard_config = bigquery.QueryJobConfig(
    maximum_bytes_billed=1,  # Demonstration only; likely rejects a nonempty scan.
    use_query_cache=False,
    labels={"workload": "cost_guardrail_lab"},
)
try:
    client.query(sql, job_config=guard_config).result()
    print("Query succeeded; inspect metadata to determine why the guard was not exceeded.")
except BadRequest as exc:
    print("Query rejected as expected for this test:", exc)
```

The threshold above is intentionally tiny and for a disposable lab only. The exact behavior depends on estimate and billing rules. If the table is empty or the query is cache-eligible, the result may differ; this script disables cache. Record whether the query was rejected, the error text, and the estimate. Do not set a one-byte ceiling for real analyst workloads. **Validation:** save the dry-run estimate, job/error outcome, and query job ID if created; do not treat the estimate as actual billed bytes. **Cleanup:** no persistent object is created by this exercise; Section 11.9 removes the lab table.

### 11.6 Exercise 5 — Materialized view and repeated aggregation

**Prerequisites:** Lab source table exists, materialized-view creation permission is available, and query cache can be disabled through job configuration.

```sql
CREATE MATERIALIZED VIEW `YOUR_PROJECT.bq_cost_lab.mv_daily_tenant_events`
AS
SELECT
  event_date,
  tenant_id,
  event_name,
  COUNT(*) AS event_count,
  SUM(revenue) AS revenue_total
FROM `YOUR_PROJECT.bq_cost_lab.events_source`
GROUP BY event_date, tenant_id, event_name;
```

If creation fails because the query/table does not meet current materialized-view requirements, record the error and adjust only after consulting the current documentation. Do not replace it with a logical view and claim the same acceleration.

Run the same aggregation against the base table to test whether BigQuery can automatically rewrite the eligible query to use the materialized view. Then query the materialized view directly as a control. Use the same date window and disable result caching in the client/job configuration for every measurement; a SQL query alone cannot disable the result cache.

```sql
-- Eligible base-table query: the optimizer may or may not rewrite it.
SELECT event_date, tenant_id, event_name,
       COUNT(*) AS event_count, SUM(revenue) AS revenue_total
FROM `YOUR_PROJECT.bq_cost_lab.events_source`
WHERE event_date >= DATE '2026-03-01'
  AND event_date < DATE '2026-04-01'
GROUP BY event_date, tenant_id, event_name;

-- Direct materialized-view query: control for reading the precomputed result.
SELECT event_date, tenant_id, event_name, event_count, revenue_total
FROM `YOUR_PROJECT.bq_cost_lab.mv_daily_tenant_events`
WHERE event_date >= DATE '2026-03-01'
  AND event_date < DATE '2026-04-01';
```

**Expected observations:** the optimizer may or may not rewrite the base-table query; directly querying the materialized view reads its stored result but does not prove automatic rewrite. No fixed percentage or speedup is promised. **Validation:** compare row counts and aggregate values for the same date window; inspect query plan/job metadata and materialized-view statistics to confirm whether the base-table query was rewritten; check `cache_hit`; include view storage and refresh/maintenance in the trade-off. **Cleanup:** drop the materialized view using Section 11.9 after saving measurements. The view has no guaranteed savings when the workload is ineligible or the optimizer does not use it.

### 11.7 Exercise 6 — Top-20 expensive-query report

**Prerequisites:** Project-level job metadata permissions, the correct region qualifier, and access to query text only where approved. This report reads metadata, not application table data.

Save the query in Section 10.1 as `05_top20_expensive_queries.sql`. Run it in the correct region and time window. For a first test, narrow the window to seven days if the project has a large job history. Sort by `total_bytes_billed`; then produce a second report sorted by `total_slot_ms`.

For each of the top jobs, classify the likely cause:

- Large scan / missing partition filter.
- Wide projection / `SELECT *`.
- High-cardinality or repeated aggregation.
- Join explosion, shuffle, or skew.
- Window function over a broad input.
- Repeated query with cache disabled or source changes.
- Capacity queueing or concurrency.
- Legitimate full-history workload.

Write one specific corrective action and a measurable expected outcome for each of the top five jobs. **Expected observations:** up to 20 visible completed query jobs for the current month, ranked by billed bytes; fewer than 20 may be returned. Capacity-priced jobs' byte fields are diagnostic rather than a direct money calculation. **Validation:** compare the separate slot-ms ranking and reconcile actual charges with Billing export. Check region, permissions, month boundaries, and script-parent exclusion. **Cleanup:** no data tables are created; store or delete the report according to SQL-text sensitivity policy.

### 11.8 Measurement worksheet

Copy this table into `results-template.csv` or a spreadsheet and fill it from actual job metadata. Do not fill it with invented numbers.

| Field | Meaning |
|---|---|
| `run_id` | Unique identifier for this measurement |
| `table_design` | `unpartitioned`, `partitioned`, or `partitioned_clustered` |
| `query_variant` | Stable name/hash of the query |
| `run_timestamp_utc` | Measurement time |
| `region` | BigQuery location |
| `row_count` | Rows in the source/table |
| `table_logical_bytes` | Table storage size from metadata |
| `dry_run_estimated_bytes` | Pre-execution estimate |
| `total_bytes_processed` | Job metadata value |
| `total_bytes_billed` | Job metadata value |
| `total_slot_ms` | Job metadata value |
| `elapsed_ms` | `end_time - start_time` |
| `cache_hit` | Whether result cache was used |
| `reservation_id` | Reservation if present |
| `actual_cost_source` | Billing export SKU/period or `not yet reconciled` |
| `notes` | Query plan, caveats, errors, data changes |

### 11.9 Cleanup

```sql
DROP MATERIALIZED VIEW IF EXISTS `YOUR_PROJECT.bq_cost_lab.mv_daily_tenant_events`;
DROP TABLE IF EXISTS `YOUR_PROJECT.bq_cost_lab.events_unpartitioned`;
DROP TABLE IF EXISTS `YOUR_PROJECT.bq_cost_lab.events_partitioned`;
DROP TABLE IF EXISTS `YOUR_PROJECT.bq_cost_lab.events_partitioned_clustered`;
DROP TABLE IF EXISTS `YOUR_PROJECT.bq_cost_lab.events_source`;
-- Drop the schema only after verifying it contains no other needed objects:
-- DROP SCHEMA `YOUR_PROJECT.bq_cost_lab`;
```

Confirm object names before running cleanup. Use a dedicated lab dataset; never use a broad wildcard delete.

---

## 12. Common anti-patterns and troubleshooting

| Symptom / anti-pattern | Why it fails | Corrective action |
|---|---|---|
| Partitioning on a field no important query filters | Little or no partition pruning | Inspect query history and choose a frequently constrained time/range key |
| Excessive tiny partitions | More metadata/management overhead and little data per partition | Test daily/monthly granularity against actual query ranges and partition sizes |
| `SELECT *` on a wide table | Reads columns that downstream logic does not need | Project explicit columns |
| Believing `LIMIT` caps bytes billed | Output row count does not generally constrain input scan | Use selective filters and dry runs |
| Filtering with `OR` across partition and non-partition predicates | Partitions may not be safely eliminated | Express logically correct filters with a direct partition predicate joined by `AND` when possible |
| Applying a function to the partition key | Can prevent clear partition pruning | Use direct typed range predicates; verify dry run |
| Too many clustering columns or wrong order | Clustering budget is limited; later keys may not help common queries | Use up to four columns based on query predicate frequency/order |
| Assuming clustering guarantees scan savings | Block pruning depends on data distribution, block metadata, and query filters | Measure against equivalent tables |
| Benchmarking with result cache on | Cached run is not a physical-layout comparison | Disable cache and inspect `cache_hit` |
| Treating dry-run estimate as actual billing | Estimate is not execution metadata or invoice cost | Compare job stats and billing export |
| Setting `maximum_bytes_billed` too low | Valid jobs can be rejected | Establish workload tiers and document exceptions |
| Materialized view created but not used | Query may be ineligible for rewrite or not match | Inspect plan/job metadata; check supported SQL and freshness |
| High `total_slot_ms` but low bytes billed | Compute/shuffle/row explosion may dominate | Inspect execution graph, joins, windows, and `JOBS_TIMELINE` |
| Expensive `MERGE` over history | Target scan/mutation may be broader than expected | Use safe partition constraints, dedupe source, and reconsider update model |
| Snapshot treated as complete DR | Does not cover all account/region/dependency failure modes | Define RPO/RTO, cross-region strategy, IAM separation, and restore drills |
| Search/vector index added to every table | Index cost/maintenance without matching workload benefit | Use only for eligible search/ANN workloads; measure recall, latency, and cost |
| Budgets assumed to stop spend | Budget alerts generally notify; they are not hard caps | Combine alerts with quotas, IAM, query limits, and ownership |
| External-table performance assumed equal to native tables | Metadata, source format, and predicate support affect behavior | Test with the intended file format and Topic 04 ingestion design |

---

## 13. Knowledge checks with answers

### Q1. When should you choose ingestion-time rather than event-time partitioning?

**Answer:** When ingestion time is the reliable operational axis—for example, arrival monitoring or retention by ingestion date—or the source lacks a trustworthy event timestamp. If most analytics filter by business/event date, partition on a validated event-date field instead, while separately tracking ingestion time for late-arrival diagnosis.

### Q2. What is the maximum number of clustering columns supported for a BigQuery clustered table?

**Answer:** Up to four, subject to current product rules and supported field types. Order matters; select the leading columns from observed filter patterns, not a generic cardinality-only heuristic.

### Q3. Does `LIMIT 100` guarantee lower bytes billed?

**Answer:** No. It limits output rows, not necessarily the input columns/partitions scanned. Use selective predicates, partition/block pruning, and column projection.

### Q4. What does `require_partition_filter` enforce?

**Answer:** It requires a predicate usable for partition elimination on the partitioning column. It does not guarantee that the remaining range is small or cheap.

### Q5. Why can bytes processed differ from bytes billed?

**Answer:** Billing rules and minimums, query/cache behavior, and the applicable pricing model can affect the relationship. Use job statistics for diagnostics and billing export for realized SKU-level charges.

### Q6. What is the difference between `total_slot_ms` and elapsed time?

**Answer:** `total_slot_ms` aggregates slot use over the job; elapsed time is wall-clock time. Parallel work can consume many slot-milliseconds in less elapsed time, and queueing can increase latency without a proportional increase in work.

### Q7. When is a materialized view worthwhile?

**Answer:** When a repeated supported query/aggregation is used frequently enough that reduced query work outweighs storage, refresh, and maintenance costs. Confirm that the query actually uses the materialized view and compare with cache disabled.

### Q8. Why might clustering not help a full-history query?

**Answer:** If the query needs most rows/blocks, block pruning has little opportunity. Clustering is most useful when selective predicates align with the clustering columns and data locality is meaningful.

### Q9. Why is a source-side filter not enough to guarantee a cheap `MERGE`?

**Answer:** The target table can still require a broad scan to match keys. Target partition pruning must be designed safely so that updates are not missed and duplicate inserts are not introduced.

### Q10. Is a BigQuery table snapshot a complete backup and disaster-recovery solution?

**Answer:** No. It is useful for point-in-time table recovery, but does not by itself guarantee cross-region recovery, protection from account/project compromise, restoration of dependencies, immutable retention, or tested RPO/RTO.

### Q11. What are the first two reports to build when costs rise?

**Answer:** A top-20 job report by `total_bytes_billed` and a separate report by `total_slot_ms`, then inspect execution graphs and timeline data for the high-impact jobs. Reconcile actual money with billing export.

### Q12. What evidence is required before claiming clustering reduced cost?

**Answer:** Equivalent queries on the same data and selected columns, cache disabled/controlled, recorded dry-run estimates and actual job metrics, plus pricing context and multiple runs where practical. Do not infer a result from table DDL alone.

---

## 14. Syllabus checkpoint

Mark each item complete only after you can explain it and, where relevant, demonstrate it in your own project.

- [ ] Explain ingestion-time, date/timestamp-column, and integer-range partitioning.
- [ ] Show partition pruning with a direct filter and identify a non-pruning predicate.
- [ ] Configure `require_partition_filter` and partition expiration safely.
- [ ] Explain dry-run estimates, processed bytes, billed bytes, slot-ms, latency, and actual cost.
- [ ] Create equivalent unpartitioned, partitioned, and partitioned-plus-clustered tables.
- [ ] Explain the four-column clustering limit and justify clustering order from query logs.
- [ ] Explain why small partitions and skew can undermine a design.
- [ ] Reduce scanning with column projection, early filters, and approximate aggregates where acceptable.
- [ ] Explain why `LIMIT` alone is not a cost guardrail.
- [ ] Compare result cache, materialized views, and BI Engine.
- [ ] Explain append-only ingestion, `MERGE`, DML, join order, pre-aggregation, cross joins, skew, `QUALIFY`, and window-function cost.
- [ ] Produce job reports using `JOBS_BY_PROJECT` and investigate time-varying workload behavior using `JOBS_TIMELINE`.
- [ ] Explain quota/limit, reservation, label, billing budget, and billing export roles.
- [ ] Describe search/vector index use cases and table snapshot limitations.
- [ ] Complete the six lab exercises and record real measurements without inventing results.

### Checkpoint standard

You are ready for Topic 04 when you can choose a partition and clustering design for five query patterns, demonstrate query guardrails, explain the cost metrics, and identify at least one measured optimization opportunity. You do not need to prove that every optimization helps every dataset; you do need to show how you tested it.

---

## 15. Summary and transition to Topic 04

The central engineering rule is to design BigQuery tables around measured workloads:

1. Use partitioning when important queries filter on a stable partition key.
2. Use clustering to improve block pruning for common selective filters within the relevant table or partition.
3. Project only necessary columns and reduce rows before expensive joins, windows, and aggregations.
4. Use approximate results only when their error profile meets the product requirement.
5. Evaluate caching, materialized views, and BI Engine separately; verify reuse rather than assuming it.
6. Guardrail ad-hoc queries with dry runs, `maximum_bytes_billed`, partition-filter requirements, quotas, and IAM.
7. Use job metadata to diagnose work and billing export to reconcile money.
8. Measure equivalent queries and record the environment, cache state, data size, and pricing model.

**Transition to Topic 04 — BigQuery Loading, Streaming, and External Tables:** table design and ingestion must be designed together. The next lesson examines batch load jobs, streaming paths, external data, and ingestion guarantees. Carry forward the chosen partition key, late-arrival strategy, retention window, duplicate-handling design, and performance measurement baseline.

---

## 16. Official documentation references

Check these official pages before applying examples to production. Google Cloud features, SQL syntax, metadata schemas, quotas, and pricing can change; this lesson avoids hard-coding a universal price or claiming that a benchmark has run.

1. [Introduction to partitioned tables](https://cloud.google.com/bigquery/docs/partitioned-tables)
2. [Create partitioned tables](https://cloud.google.com/bigquery/docs/creating-partitioned-tables)
3. [Query partitioned tables](https://cloud.google.com/bigquery/docs/querying-partitioned-tables)
4. [Manage partitioned tables, expiration, and partition-filter requirements](https://cloud.google.com/bigquery/docs/managing-partitioned-tables)
5. [Introduction to clustered tables](https://cloud.google.com/bigquery/docs/clustered-tables)
6. [Create clustered tables](https://cloud.google.com/bigquery/docs/creating-clustered-tables)
7. [Querying clustered tables](https://cloud.google.com/bigquery/docs/querying-clustered-tables)
8. [Query pricing and cost controls](https://cloud.google.com/bigquery/pricing)
9. [Estimate query costs](https://cloud.google.com/bigquery/docs/estimate-costs)
10. [Dry runs](https://cloud.google.com/bigquery/docs/running-queries#dry-run)
11. [Query job configuration and `maximum_bytes_billed`](https://cloud.google.com/bigquery/docs/reference/rest/v2/Job#JobConfigurationQuery)
12. [Query performance best practices](https://cloud.google.com/bigquery/docs/best-practices-performance-compute)
13. [Optimize storage and query performance](https://cloud.google.com/bigquery/docs/best-practices-storage)
14. [Cached query results](https://cloud.google.com/bigquery/docs/cached-results)
15. [Materialized views introduction](https://cloud.google.com/bigquery/docs/materialized-views-intro)
16. [BI Engine introduction](https://cloud.google.com/bigquery/docs/bi-engine-intro)
17. [DML statements and cost considerations](https://cloud.google.com/bigquery/docs/data-manipulation-language)
18. [Introduction to `INFORMATION_SCHEMA`](https://cloud.google.com/bigquery/docs/information-schema-intro)
19. [`JOBS_BY_PROJECT` view](https://cloud.google.com/bigquery/docs/information-schema-jobs)
20. [`JOBS_TIMELINE` view](https://cloud.google.com/bigquery/docs/information-schema-jobs-timeline)
21. [Custom quotas](https://cloud.google.com/bigquery/quotas#custom_quotas)
22. [Manage reservations](https://cloud.google.com/bigquery/docs/reservations-intro)
23. [Cloud Billing export to BigQuery](https://cloud.google.com/billing/docs/how-to/export-data-bigquery)
24. [Search indexes](https://cloud.google.com/bigquery/docs/search)
25. [Vector indexes](https://cloud.google.com/bigquery/docs/vector-index)
26. [Table snapshots](https://cloud.google.com/bigquery/docs/table-snapshots-intro)
27. [Create table snapshots](https://cloud.google.com/bigquery/docs/table-snapshots-create)
28. [BigQuery Python client reference](https://cloud.google.com/python/docs/reference/bigquery/latest)

---

## Validation note

This lesson has been statically re-audited against Topic 03 and its roadmap requirements, including code-block structure, metadata-view partition filters, script-job double-counting risks, exercise prerequisites/validation/cleanup, and explicit measurement/execution caveats. The SQL and Python examples are instructional templates and have not been executed against a live BigQuery project as part of this artifact build. Confirm current documentation, IAM permissions, region, project quotas, pricing model, and feature availability before production use. The lab is designed to record measurements; no benchmark results are prefilled or claimed.
