# Micro-Partitions, Clustering, and Pruning

**Roadmap location:** `Stage 2C — Data Engineering_3/03-Snowflake-Deep-Dive/03-micro-partitions-clustering-and-pruning.md`  
**Module:** Snowflake Deep Dive — Phase B: Storage Internals and Loading  
**Prerequisites:** Topic 01 — Snowflake architecture, storage, compute, and services; Topic 02 — virtual warehouses, sizing, scaling, billing, and Query Profile  
**Hands-on lab:** `experiments/03_micro_partitions/`

---

## Learning objectives

By the end of this lesson, you should be able to:

1. Explain how Snowflake automatically stores table data in immutable, compressed, columnar micro-partitions.
2. Explain how partition metadata allows Snowflake to prune data before scanning it.
3. Predict why a date-range predicate may prune well on date-ordered data but poorly on randomly ordered data.
4. Read partitions-scanned-versus-total metrics in Query Profile and distinguish them from elapsed time and bytes scanned.
5. Interpret clustering depth, overlap, and the output of `SYSTEM$CLUSTERING_INFORMATION`.
6. Choose and justify clustering-key columns, expressions, and ordering from real query patterns.
7. Evaluate automatic clustering, ingestion-time sorting, DML effects, and their compute/storage costs.
8. Decide when Search Optimization Service or a materialized view may be more appropriate than a clustering key.
9. Explain how native Snowflake tables differ from external tables and Apache Iceberg tables in their pruning and maintenance models.
10. Complete the lab, capture actual observations, and make a cost-aware recommendation without assuming a performance gain in advance.

## Prerequisites and learning order

- **Topic 01:** Know the separation between Snowflake storage, virtual warehouses, and serverless services. Micro-partitions are a storage organization; a warehouse executes queries against them.
- **Topic 02:** Know how to select a warehouse, inspect Query Profile, and interpret credits and elapsed time. A query becoming faster does not by itself prove that clustering is cost-effective.
- **This topic:** Understand storage layout and pruning before moving to Topic 04 (stages, `COPY INTO`, and Snowpipe). The way data arrives can influence its initial physical organization.

Use the roadmap as the syllabus. This lesson adds implementation detail and cautions needed to run the specified lab safely; it does not assume that any experiment has already been executed.

---

# Part 1 — Beginner: Micro-partitions and pruning

## 1. What is a micro-partition?

Snowflake automatically divides the rows of a standard native table into storage units called **micro-partitions**. The roadmap describes them as immutable, compressed, columnar units of approximately **50–500 MB of uncompressed data**. Treat that range as an approximate teaching reference, not as a target size that users configure or a promise about every partition.

Key properties:

- **Automatic:** Snowflake creates and manages micro-partitions as data is loaded or changed. You do not manually create them, choose their exact boundaries, or maintain a traditional index for them.
- **Immutable storage units:** A change does not mean Snowflake edits a micro-partition in place like a mutable row page. Changed data can result in new micro-partitions and old versions being retained according to data-retention rules.
- **Columnar:** Values are stored and processed by column, allowing Snowflake to avoid reading unneeded columns for many queries.
- **Compressed:** Snowflake compresses column data. Similar values grouped together can improve compression as well as pruning.
- **Metadata-bearing:** Snowflake maintains metadata such as value ranges and counts that helps the optimizer decide which micro-partitions may contain qualifying rows.

### Why this matters in production

A query that returns 500 rows from a multi-terabyte table does not necessarily need to scan every micro-partition. If metadata proves that most partitions cannot contain those rows, Snowflake can skip them. The practical goal is to reduce unnecessary data scanning while preserving correctness.

### What micro-partitions are not

They are not user-managed partitions with a DDL boundary you define for every range; they are not B-tree indexes; and they are not a guarantee that every predicate will eliminate large amounts of data. A query can still scan many partitions if their metadata overlaps the predicate, if the filter is not selective, or if the query expression prevents useful pruning.

## 2. Metadata: what Snowflake can know without scanning all rows

Micro-partition metadata can include, among other information:

- Minimum and maximum values for columns, where applicable.
- Counts and other column statistics.
- Information used to identify partitions that cannot match a predicate.

Imagine the following simplified metadata. Each box represents a micro-partition, not a user-created partition key.

| Micro-partition | Minimum `EVENT_DATE` | Maximum `EVENT_DATE` | Rows (illustrative) |
|---|---|---|---:|
| MP-01 | 2025-01-01 | 2025-01-07 | 1,000,000 |
| MP-02 | 2025-01-08 | 2025-01-14 | 1,000,000 |
| MP-03 | 2025-01-15 | 2025-01-21 | 1,000,000 |
| MP-04 | 2025-01-22 | 2025-01-28 | 1,000,000 |
| MP-05 | 2025-01-29 | 2025-02-04 | 1,000,000 |

These values are illustrative. Real partition sizes, row counts, and date ranges depend on the data and load process.

## 3. Partition pruning: step by step

**Partition pruning** means excluding micro-partitions that cannot contain rows satisfying a query predicate. Snowflake uses partition metadata during query planning/execution to avoid scanning data that cannot match. Pruning is an optimization; the `WHERE` predicate still determines the correct result.

### Predicate A — narrow date range

```sql
SELECT COUNT(*)
FROM ANALYTICS.EVENTS
WHERE EVENT_DATE >= '2025-01-10'::DATE
  AND EVENT_DATE <  '2025-01-13'::DATE;
```

Step by step:

1. Snowflake examines the date predicate and partition metadata.
2. MP-01 ends on January 7, so it cannot contain a qualifying row and can be pruned.
3. MP-02 spans January 8–14 and may contain qualifying rows, so it must be considered.
4. MP-03 spans January 15–21, so it cannot match the range ending before January 13 and can be pruned.
5. MP-04 and MP-05 are also outside the range and can be pruned.
6. Snowflake scans the candidate partition(s) and applies the predicate to rows.

This example assumes the displayed metadata and simplified date boundaries. It is not a claim that a real query will scan exactly one partition.

### Predicate B — date range across two partition ranges

```sql
SELECT EVENT_TYPE, COUNT(*)
FROM ANALYTICS.EVENTS
WHERE EVENT_DATE >= '2025-01-12'::DATE
  AND EVENT_DATE <  '2025-01-20'::DATE
GROUP BY EVENT_TYPE;
```

MP-02 and MP-03 may contain matching dates. The other listed partitions can be excluded if their metadata establishes that they do not overlap the requested range. The aggregation still has to process the qualifying rows in the remaining partitions.

### Predicate C — a value present in every partition's min/max range

```sql
SELECT COUNT(*)
FROM ANALYTICS.EVENTS
WHERE CUSTOMER_ID = 424242;
```

If `CUSTOMER_ID` values are mixed throughout the table and every partition's minimum/maximum range includes `424242`, min/max metadata alone may not eliminate many partitions. The value might exist in a partition—or it might not; the range does not prove existence. This is one reason a selective point lookup can benefit from Search Optimization Service when its supported predicates and economics fit.

### Predicate D — a function on a filtered column

Compare a direct range predicate:

```sql
SELECT COUNT(*)
FROM ANALYTICS.EVENTS
WHERE EVENT_DATE >= '2025-01-01'::DATE
  AND EVENT_DATE <  '2025-02-01'::DATE;
```

with a function-based predicate:

```sql
SELECT COUNT(*)
FROM ANALYTICS.EVENTS
WHERE DATE_TRUNC('MONTH', EVENT_DATE) = '2025-01-01'::DATE;
```

The optimizer can sometimes derive equivalent constraints from expressions, but do not assume every function/cast form prunes as well as a direct, type-compatible range. When practical, express date filters as half-open ranges (`>= start AND < end`) and confirm the actual plan in Query Profile. Do not rewrite a predicate solely on folklore; compare semantically equivalent queries on representative data.

## 4. Natural ordering and load order

Snowflake automatically creates micro-partitions, but **the order in which rows arrive can influence how values are grouped into them**. When a table is loaded in date order, adjacent micro-partitions may cover adjacent date ranges. A narrow date filter can then skip most partitions. If rows from all dates are mixed randomly, each micro-partition may contain a broad range of dates, making more partitions candidates for the same filter.

### Well-ordered example

```text
EVENT_DATE increases from left to right

MP-01          MP-02          MP-03          MP-04
Jan 01–07  |   Jan 08–14  |   Jan 15–21  |   Jan 22–28
[min,max]      [min,max]      [min,max]      [min,max]

Filter Jan 10–12  -> MP-02 is a likely candidate; other ranges can be skipped.
```

### Randomly mixed example

```text
EVENT_DATE values are mixed across partitions

MP-01          MP-02          MP-03          MP-04
Jan–Apr    |   Jan–Apr    |   Jan–Apr    |   Jan–Apr
[min,max]      [min,max]      [min,max]      [min,max]

Filter Jan 10–12  -> every partition's range may overlap the filter.
```

The diagram describes a common pattern, not a guarantee. Actual pruning depends on metadata and data distribution. A well-ordered table can still prune poorly for a predicate on a different column; a randomized table can sometimes prune adequately for some filters.

### Production relevance and trade-off

Ordering data at ingestion can improve natural clustering without a continuing clustering-key maintenance service. However, a global sort of a large input can require substantial warehouse compute, memory, and spill. If loads arrive incrementally or late, new rows may overlap old ranges. Compare the one-time or recurring cost of ordering at load time with automatic clustering maintenance and the resulting query workload.

## 5. Why ordinary micro-partition pruning does not need traditional indexes

In many traditional relational systems, an index is a separately maintained access structure that maps keys to rows or pages. For standard native Snowflake tables, Snowflake automatically maintains micro-partition metadata and uses it to prune partitions. Users do not create a conventional B-tree index for ordinary filtering on a native table.

This does **not** mean all lookups are automatically fast. If metadata ranges overlap heavily, a predicate is not selective, or a lookup pattern needs more precise access paths than partition metadata provides, Snowflake may still scan many partitions. Specialized storage services—such as Search Optimization Service—serve different query patterns and have their own maintenance and credit costs.

---

# Part 2 — Intermediate: Clustering and its measurement

## 6. What clustering means

For this lesson, clustering means the degree to which rows with similar values for selected columns are grouped into the same or nearby micro-partitions. A **clustering key** is a set of columns or supported expressions that Snowflake uses as the target organization for a large table. Defining a key does not instantly rearrange every existing row; Snowflake may need background reclustering to improve the existing layout.

A good key aligns with the predicates and ordering used by a meaningful share of production queries. It should not be chosen merely because a column is a primary identifier, appears in a schema, or has a high number of distinct values.

### Well-clustered illustration

For a key `EVENT_DATE`, each partition covers a relatively compact range:

```text
Date value  ───────────────────────────────────────────────────────►

MP-A: [Jan 01 ───── Jan 07]
MP-B:                 [Jan 08 ───── Jan 14]
MP-C:                                  [Jan 15 ───── Jan 21]
MP-D:                                                   [Jan 22 ───── Jan 28]

Ranges have little overlap. A date filter can often eliminate partitions
whose ranges do not intersect the predicate.
```

### Overlapping illustration

```text
Date value  ───────────────────────────────────────────────────────►

MP-A: [Jan 01 ─────────────────────────────── Jan 28]
MP-B:       [Jan 03 ───────────────────────── Jan 27]
MP-C: [Jan 01 ─────────────────────── Jan 24]
MP-D:            [Jan 06 ───────────────────────────── Jan 31]

Many ranges overlap. A narrow date predicate may leave many partitions
as candidates, even if relatively few rows match.
```

These are conceptual min/max ranges. Real micro-partitions contain many values, and clustering is multidimensional when a key has more than one expression.

## 7. Clustering depth and overlap

- **Overlap** describes how much the value ranges of micro-partitions overlap for the selected clustering dimensions.
- **Clustering depth** summarizes overlap depth across micro-partitions for the selected columns or expressions. For a populated table, `SYSTEM$CLUSTERING_DEPTH` returns an average depth of at least 1; lower depth generally indicates better clustering for the specified dimensions.
- **Average overlap** and **average depth** are useful diagnostics, not a direct prediction of query latency or cost. They do not prove that a key benefits the actual workload.

Do not interpret a depth number as “that many times slower,” as a pruning percentage, or as a target that every table must reach. The appropriate result depends on table size, data distribution, filter selectivity, query frequency, DML rate, and the cost of maintaining the layout. The `SYSTEM$CLUSTERING_INFORMATION` output can include `cluster_by_keys`, `version` (`CLASSIC` or `OPTIMA`), `total_partition_count`, `average_overlaps`, `average_depth`, and `notes`; `total_constant_partition_count` and `partition_depth_histogram` are not available for Optima Clustering. If a table has more than two million micro-partitions, the function's results are based on a subset and `total_partition_count` is capped at two million. Fields may differ by clustering implementation; consult current documentation and inspect the returned JSON.

## 8. Inspect clustering with `SYSTEM$CLUSTERING_INFORMATION`

The function can evaluate the defined key or specified columns/expressions. If a table has no explicit clustering key, supply the columns/expressions to evaluate.

```sql
-- If EVENTS has a defined clustering key, inspect that key:
SELECT SYSTEM$CLUSTERING_INFORMATION('ANALYTICS.EVENTS');

-- Evaluate a candidate key before defining it:
SELECT SYSTEM$CLUSTERING_INFORMATION(
  'ANALYTICS.EVENTS',
  '(EVENT_DATE)'
);

-- Compare a second candidate on the same table:
SELECT SYSTEM$CLUSTERING_INFORMATION(
  'ANALYTICS.EVENTS',
  '(EVENT_TYPE, EVENT_DATE)'
);
```

Use fully qualified names and correct quoting/casing for your environment. The second argument is a string describing the column list or expressions, not a SQL array. Run the function before and after a clustering change, then compare the output over time. For a candidate key, the reported depth describes that candidate's current layout; it does not mean the table is already physically reclustered for that candidate.

### Interpreting the output

| Output field (where returned) | What it tells you | What it does not tell you |
|---|---|---|
| `cluster_by_keys` | The key defined on the table, or dimensions being evaluated | Whether the key is useful for every query |
| `version` | Automatic Clustering implementation (`CLASSIC` or `OPTIMA`) | A performance score or a cost value |
| `notes` | Implementation-generated guidance or warnings, when present | A substitute for Query Profile or workload evidence |
| `total_partition_count` | Number of micro-partitions represented in the analysis; results are subset-based and capped at 2 million when the table exceeds that size | Query runtime or bytes scanned |
| `total_constant_partition_count` | Partitions considered constant for the selected clustering dimensions, when supported | A universal target or guaranteed pruning rate |
| `average_overlaps` | Average number of overlapping partitions under the function's definition | A direct multiplier for latency |
| `average_depth` | Average overlap depth; lower is generally better for the evaluated dimensions | Proof that the chosen key is worth its maintenance cost |
| `partition_depth_histogram` | Distribution of partitions across overlap-depth buckets, when supported | A substitute for Query Profile and workload benchmarking |

**Caution:** the output schema and some fields differ for Optima Clustering. Treat the returned JSON as the source of truth for the account's current behavior, and use current Snowflake documentation for interpretation.

## 9. Choosing a clustering key

Start with observed query patterns, not the table schema alone.

1. Collect the most frequent and most expensive queries against the table.
2. Identify columns repeatedly used in selective `WHERE` predicates, joins, or sorting.
3. Estimate selectivity: does the query usually need a small portion of the table?
4. Check value distribution and cardinality. The roadmap emphasizes low-to-medium cardinality as a useful starting point. In practice, cardinality alone is not a rule: extremely low-cardinality columns can provide weak discrimination, while a high-cardinality timestamp or identifier can be useful in a suitable access pattern. Test rather than applying a blanket threshold.
5. Consider whether the same key helps a substantial fraction of the workload.
6. Evaluate candidate clustering information, then test representative queries before and after a physical layout change.
7. Estimate maintenance credits and storage implications against expected query savings.

### Key order and expressions

A clustering key can contain multiple columns or expressions. The dimensions and their order matter to the clustering strategy and to how useful the organization is for particular predicates. Prefer the simplest key that matches the workload. Do not add columns merely to “cover everything”: more complex keys can increase maintenance and may dilute the benefit for the common filters.

Example for a table mostly queried by event date, with occasional filtering by tenant:

```sql
-- Candidate only: evaluate with actual query history before applying.
ALTER TABLE ANALYTICS.EVENTS CLUSTER BY (TO_DATE(EVENT_TS), TENANT_ID);
```

`TO_DATE(EVENT_TS)` can be useful when most queries filter by calendar date rather than the exact timestamp. Confirm the expression is supported for clustering in your table and Snowflake implementation, especially for an already populated table. Do not copy this example blindly: if queries are mainly tenant point lookups or if the table is small, a different design—or no clustering key—may be better.

### Common selection failures

- **A unique ID chosen automatically:** high cardinality does not itself mean good pruning. A point lookup may be a Search Optimization candidate.
- **A boolean or tiny-category column alone:** if almost every partition contains both values, metadata cannot exclude many partitions.
- **A key no important query filters on:** the table may become well-clustered on an irrelevant dimension.
- **Too many expressions:** additional dimensions can raise maintenance cost and complicate the interpretation of results.
- **A key chosen from a single query:** optimize the workload, not one isolated query, unless that query is business-critical enough to justify the cost.

## 10. Automatic clustering and background reclustering

When a clustering key is defined on a standard table, Snowflake can use **Automatic Clustering** to maintain the organization as data changes. It is a background service; you do not provide a virtual warehouse for its work. Snowflake evaluates whether reclustering is useful and, when it is, reorganizes affected data into new micro-partitions.

Important operational detail for the current date of this lesson: Snowflake documentation states that newly clustered tables use **Optima Clustering** beginning September 1, 2026, while tables already clustered remain on **Clustering Classic**. These implementations have different cost models. Check which version applies to the table and use the matching documentation and account usage data; do not assume all accounts or existing tables have identical billing behavior.

### Credit and storage implications

- **Clustering Classic:** maintenance consumes serverless compute credits; rates and usage depend on the actual operations and current service consumption schedule.
- **Optima Clustering:** Snowflake's current documentation describes ingestion-based billing as `GB ingested × 0.007 credits per GB × overlap factor`. The overlap factor is between 0 and 1 and reflects the proportion of ingested data that requires active clustering; naturally well-clustered arriving data can have a lower factor. Treat this as the documented model at the time this lesson was prepared, not a timeless price guarantee: verify current service-consumption documentation and the table's clustering version before budgeting.
- **Storage churn:** reclustering creates new micro-partitions and marks affected old micro-partitions as deleted. Retention for Time Travel and Fail-safe can mean old data remains stored for a period, so storage usage may temporarily increase.
- **DML interaction:** inserts, updates, deletes, merges, and loads can alter clustering. Frequent small changes to a large clustered table may create continuing maintenance work.
- **No instant guarantee:** defining a key is not proof that all existing data has already been reorganized or that every query will become faster.

To inspect recent maintenance usage where available:

```sql
-- Account Usage history is generally delayed; permissions are required.
SELECT
    TO_DATE(START_TIME) AS USAGE_DATE,
    DATABASE_NAME,
    SCHEMA_NAME,
    TABLE_NAME,
    VERSION,
    SUM(CREDITS_USED) AS CREDITS_USED
FROM SNOWFLAKE.ACCOUNT_USAGE.AUTOMATIC_CLUSTERING_HISTORY
WHERE START_TIME >= DATEADD(day, -30, CURRENT_TIMESTAMP())
GROUP BY 1, 2, 3, 4, 5
ORDER BY USAGE_DATE DESC, CREDITS_USED DESC;
```

The documented `SNOWFLAKE.ACCOUNT_USAGE.AUTOMATIC_CLUSTERING_HISTORY` view includes `START_TIME`, `CREDITS_USED`, `TABLE_NAME`, `DATABASE_NAME`, `SCHEMA_NAME`, and `VERSION`; the example uses those documented columns. Data latency can be up to three hours. A missing recent row is not proof that maintenance was free. Use `VERSION` to distinguish `OPTIMA` from `CLASSIC`, and do not infer Optima costs from old Clustering Classic patterns.

Before enabling clustering on a large existing table, evaluate the current estimate function where supported and available, such as `SYSTEM$ESTIMATE_AUTOMATIC_CLUSTERING_COSTS`, and establish a baseline. Estimates are not guarantees. Start with one representative table and monitor both query performance and maintenance costs.

### Suspending or removing a key

Snowflake supports suspending/resuming automatic reclustering on clustered tables in relevant implementations, and dropping a key prevents future clustering-key maintenance. Use the current command syntax for the table and clustering implementation; do not suspend/resume as a casual toggle without understanding catch-up behavior and cost. For Optima Clustering, Snowflake documents that suspending stops billing for newly ingested data, but resuming can incur catch-up cost for data ingested while suspended. If the intent is to stop future clustering permanently, dropping the key is a different and more durable choice.

---

# Part 3 — Advanced: Production design and alternatives

## 11. When is clustering worth evaluating?

The roadmap gives **tables larger than approximately 1 TB with selective filters** as a guideline. This is a heuristic, not a minimum requirement, a guarantee, or a vendor rule. Current Snowflake guidance often discusses tables with multiple terabytes and many micro-partitions as strong candidates. Use size to prioritize investigation—not as an automatic instruction to add a key.

Clustering is most worth evaluating when several conditions hold:

- The table is large enough that avoiding scans can matter.
- A significant portion of workload queries filter or sort on a common set of columns.
- Those queries are selective enough that skipping partitions is valuable.
- The table is queried often relative to how often it changes.
- The expected reduction in query compute/latency outweighs reclustering, storage, and operational costs.
- Representative benchmarks show a repeatable benefit after controlling for cache, warehouse size, concurrency, and query changes.

It is often not worth clustering when the table is small, queries already finish quickly, predicates are not selective, workloads use many unrelated filter patterns, or DML churn causes high maintenance cost. A low average depth alone is not a business case.

## 12. Sort at ingestion or rely on automatic clustering?

| Situation | First option to test | Why | Main trade-off |
|---|---|---|---|
| Large batch arrives once and can be ordered by a dominant date/key | Sort/order during the load or CTAS | Data can arrive naturally grouped, potentially reducing later maintenance | Sorting itself consumes compute and can spill; late-arriving data can overlap ranges |
| Append-only data arrives in date order and queries filter on that date | Preserve natural order; measure before adding a key | Existing layout may already prune well | New batches and corrections can gradually change overlap |
| Continuous/incremental data causes important partitions to overlap | Automatic clustering on a justified key | Background maintenance can restore useful organization | Serverless credits and possible storage churn |
| Table is small or query filters vary widely | No clustering key initially | Simpler and cheaper until evidence supports change | Some queries may scan more data than an optimized layout would |
| Workload is dominated by selective equality lookups on IDs | Test Search Optimization Service | Built for needle-in-a-haystack access patterns | Access-path build/maintenance and ongoing service cost |
| Repeated expensive aggregate/projection query on one base table | Evaluate a materialized view | Precomputed result can avoid repeating work | Storage plus automatic maintenance cost; definition restrictions |
| Complex transformation pipeline with target freshness/refresh requirements | Evaluate dynamic tables | Declarative transformation and managed refresh behavior | Refresh compute and storage; not a direct drop-in replacement for every materialized view |

Do not use `ORDER BY` in a query as a promise of permanent physical clustering unless the load operation and observed layout support the conclusion. For large tables, a sort can itself be costly. Compare end-to-end cost: sort/load cost plus recurring query cost versus automatic-clustering maintenance plus recurring query cost.

## 13. How `MERGE`, `UPDATE`, and other DML affect organization

Micro-partitions are immutable storage units. DML against a native table can cause affected data to be represented in new micro-partitions rather than modifying old storage in place. As `INSERT`, `UPDATE`, `DELETE`, `MERGE`, and `COPY` operations add or change rows, the resulting data distribution can overlap existing key ranges and degrade clustering for the chosen dimensions.

This is why the same key can look well-clustered after a bulk load and less well-clustered after months of incremental changes. It does not mean every DML statement destroys clustering or that every DML statement triggers immediate reclustering. Snowflake evaluates the table and may maintain it automatically when applicable.

Production practices:

- Batch changes when the application can tolerate it; many tiny DML operations can be more expensive to maintain than fewer larger batches.
- Monitor both the workload and clustering maintenance after large `MERGE`/`UPDATE` jobs.
- Avoid clustering keys that do not serve important queries just because the table is frequently modified.
- Include Time Travel/Failsafe storage behavior in cost analysis when reclustering creates substantial data turnover.
- Do not treat a high depth reading alone as a command to force more maintenance; validate the query benefit first.

## 14. Search Optimization Service (SOS)

**Search Optimization Service** builds and maintains a search access path for supported predicates. It is designed for highly selective searches—especially point lookups expected to return a small number of rows—where partition min/max metadata may leave too many partitions as candidates.

Examples include:

```sql
-- Enable equality search optimization for a frequently queried identifier.
ALTER TABLE ANALYTICS.EVENTS
  ADD SEARCH OPTIMIZATION ON EQUALITY(REQUEST_ID);

-- A selective point lookup that may benefit when SOS is ready and supported.
SELECT EVENT_TS, EVENT_TYPE, PAYLOAD
FROM ANALYTICS.EVENTS
WHERE REQUEST_ID = 'req-8f31a2';
```

For a semi-structured `VARIANT` column, support must be enabled for the relevant column or element as appropriate. Confirm the path expression and supported predicate in the current docs before running. Example:

```sql
ALTER TABLE ANALYTICS.EVENTS
  ADD SEARCH OPTIMIZATION ON EQUALITY(PAYLOAD:user.id);

SELECT EVENT_TS, PAYLOAD
FROM ANALYTICS.EVENTS
WHERE PAYLOAD:user.id = 'user-12345';
```

The syntax and supported predicate types should be checked against the current Snowflake documentation and data types in use. Search optimization is an Enterprise Edition (or higher) feature. It is not automatically a replacement for clustering: its persistent access paths require build and maintenance resources, and adding it to a very large table can cause a temporary increase in credit consumption while access paths are built. Prefer enabling it only for columns/predicates with a demonstrated workload need rather than indiscriminately on every column.

### Clustering versus SOS

| Workload pattern | Clustering | Search Optimization |
|---|---|---|
| Broad range scan by date over a huge table | Often worth evaluating | Usually not the first choice for a broad range |
| Selective equality lookup by an ID returning few rows | May help if the ID is a useful clustering dimension, but may still leave many candidate partitions | Often a stronger candidate if supported and selective |
| Frequent filters over a common range dimension | Natural or maintained clustering can reduce scanned partitions | Depends on supported predicate and selectivity; compare empirically |
| Selective point lookup into a supported `VARIANT` path | A key on supported expressions may not be the simplest or best fit | Can support specified semi-structured equality/substring patterns subject to documented limitations |
| Queries return a large fraction of the table | Pruning benefit may be limited | Usually poor economics for a non-selective lookup strategy |

SOS is not a user-managed traditional index, and its presence does not guarantee a specific latency improvement. Confirm that the service is built, that the query predicate is supported, and that Query Profile/workload measurements show the intended effect.

## 15. Materialized views and dynamic tables

These features materialize results, but they solve different needs from clustering and from each other.

### Materialized views

A materialized view stores a precomputed result derived from a `SELECT` over a single base table, subject to Snowflake's definition restrictions. It can help when the same expensive aggregation, projection, or selective query is run frequently. It incurs storage and automatic background maintenance compute when the base table changes. DML and reclustering on the base table can contribute to materialized-view maintenance work.

Illustrative pattern:

```sql
-- Example only; confirm the expression and restrictions for your account.
CREATE MATERIALIZED VIEW ANALYTICS.DAILY_EVENT_COUNTS AS
SELECT EVENT_DATE, EVENT_TYPE, COUNT(*) AS EVENT_COUNT
FROM ANALYTICS.EVENTS
GROUP BY EVENT_DATE, EVENT_TYPE;
```

Do not assume every query can use a materialized view or that every aggregation is allowed by materialized-view restrictions. Check current documentation before creating one. Monitor maintenance usage (for example, materialized-view refresh history) and storage as well as query runtime.

### Dynamic tables

A dynamic table materializes the result of a defined query and uses managed refresh according to its target lag and refresh behavior. It is commonly used to define and maintain transformation pipelines declaratively. Its refresh compute and storage are costs that must be evaluated against the pipeline's freshness and maintenance requirements.

### Comparison

| Design | Primary purpose | Maintenance model | Cost and limitation to remember |
|---|---|---|---|
| Clustering key | Organize base-table micro-partitions for scan/pruning patterns | Automatic clustering/reclustering where enabled | Maintenance credits and potential storage churn; helps queries aligned to the key |
| Search Optimization | Accelerate supported selective searches | Background build and maintenance of access paths | Enterprise feature; access-path build and maintenance cost |
| Materialized view | Reuse precomputed result for repeated supported query patterns | Automatic background maintenance | Extra storage and serverless maintenance; definition restrictions, generally single base table |
| Dynamic table | Maintain a declared transformation result with managed refresh | Refresh according to target lag/refresh strategy | Refresh compute and storage; freshness and pipeline semantics matter |

These options are not mutually exclusive, but stacking them can compound maintenance costs. Add one optimization at a time and measure its incremental value. A dynamic table is not simply a materialized view with a different name, and neither is a universal substitute for clustering.

## 16. Native tables versus external tables versus Iceberg tables

Do not apply native-table assumptions to every object that Snowflake can query.

### Standard native Snowflake tables

- Snowflake manages storage and automatically creates micro-partitions with metadata.
- Query pruning can use native micro-partition metadata.
- Clustering keys and Automatic Clustering are available subject to supported table type and implementation.
- DML and reclustering can produce new micro-partitions and retention/storage effects.

### External tables

- The data remains in external cloud storage; Snowflake stores metadata about files and exposes the data for querying.
- Pruning is materially different: partition columns and file-level metadata can exclude files/partitions. When a file is selected, Snowflake generally scans relevant data within that file; non-partition filters may be applied after file pruning.
- External tables are read-only for DML. Do not assume native micro-partition clustering keys or Automatic Clustering can be applied to the external data.
- Partitioned paths and refreshed external-table metadata are important to performance and correctness. External-table queries may be slower than native tables; materialized views or loading into native tables may be options for repeated workloads.

### Apache Iceberg tables

- Iceberg tables use Apache Iceberg metadata (including snapshots, manifests, and file/partition metadata) to identify files and relevant data. The exact metadata-management and write model depends on whether the table is Snowflake-managed or externally managed and on supported features.
- Iceberg pruning is not the same as the native Snowflake micro-partition/clustering-key model. Do not assume `SYSTEM$CLUSTERING_INFORMATION` and Automatic Clustering work as they do for standard native tables; consult current feature support for the specific Iceberg table type.
- Partition transforms and file layout influence pruning. External engines may write files and evolve partition specifications, subject to Snowflake's supported Iceberg behavior.
- Iceberg can be useful for open-format interoperability, but query performance depends on file size, partitioning, metadata, engine, and data organization. It is not automatically faster or slower than native tables in every workload.

### Decision table

| Table type | Main pruning metadata/layout | Can you apply native-table clustering-key assumptions? | Operational focus |
|---|---|---|---|
| Standard native Snowflake table | Micro-partition metadata and optional clustering key | Yes, subject to supported features | Query Profile, clustering information, DML and clustering costs |
| External table | External file metadata and defined partition columns/path layout | No; data is external and external tables are read-only | File sizing/layout, partition-column design, metadata refresh, external I/O |
| Iceberg table | Iceberg snapshots/manifests and file/partition metadata; exact support depends on management mode | Do not assume so; verify supported Iceberg features | Partition transforms, file layout, metadata/catalog management, engine compatibility |

---

# Part 4 — Query Profile and performance validation

## 17. Read “partitions scanned / total”

Run a representative query, open its Query Profile in Snowsight, and inspect the table scan operator. Record the **partitions scanned** and **total partitions** reported for that scan, along with bytes scanned, elapsed time, cache state, and relevant operator details. The exact labels can vary with the interface/version.

For example, if a profile reports 120 partitions scanned out of 1,200 total, then 1,080 partitions were not scanned by that operator. This arithmetic is a description of the observed profile—not a claim that the query became 90% faster or that credits fell by 90%. Query execution includes other operators, warehouse behavior, caching, concurrency, and result size.

### Query Profile exercise

1. Run a narrow date-range query against the date-ordered table.
2. Save its query ID and open Query Profile.
3. Record partitions scanned/total, bytes scanned, execution time, and any spill or queueing indicators.
4. Run the equivalent predicate against the randomized table.
5. Repeat each query enough times to understand variability, while separating cold-cache and warm-cache runs.
6. Compare the profiles. If partition counts are similar, investigate whether the physical order differed as expected, whether the query actually filtered on the candidate key, and whether the dataset is large enough for the difference to be visible.
7. Compare a selective filter on a non-clustered column.
8. Do not compare runs on different warehouses or under different concurrency and then attribute all changes to clustering.

### Before-and-after analysis template

| Metric | Baseline | Candidate change | Difference | Notes / evidence |
|---|---:|---:|---:|---|
| Partitions scanned | Record actual | Record actual | Calculate | Query Profile, same table/query shape |
| Total partitions | Record actual | Record actual | Calculate | Check whether table layout/size changed |
| Bytes scanned | Record actual | Record actual | Calculate | Also note selected columns and compression |
| Execution time | Record actual | Record actual | Calculate | Repeat runs; identify cache state |
| Queueing / spill | Record actual | Record actual | Describe | Warehouse and concurrency may affect this |
| Warehouse credits | Record actual or estimate | Record actual or estimate | Calculate | Include warehouse runtime and minimum billing behavior |
| Automatic clustering credits | Record actual | Record actual | Calculate | Account Usage can lag; identify clustering version |
| Storage impact | Record actual | Record actual | Describe | Include Time Travel/Failsafe effects where relevant |

**Measured observation** means a value you actually recorded from your Snowflake account. **Expected behavior** means a hypothesis—for example, “date-ordered data should prune better for a narrow date filter.” Never present a hypothesis as a benchmark result.

## 18. A defensible performance comparison

A sound experiment changes one relevant factor at a time.

- Keep SQL text, selected columns, filters, result cardinality, warehouse size, and concurrency as consistent as practical.
- Use the same source rows in both layouts. A different dataset is not a controlled comparison.
- Control or record result-cache and warehouse-cache conditions. Do not compare a warm cached run with a cold run and attribute the difference to clustering.
- Record query IDs, timestamps, and Query Profile screenshots or exported notes.
- Compare multiple runs and use medians or ranges rather than selecting the best run.
- Include load/sort cost and reclustering maintenance in the economic evaluation—not just query time.
- Avoid running a large lab in a production account without approval, budget limits, and cleanup procedures.

### Illustrative, not measured, example

Suppose a representative query scans 900 partitions before a layout change and 180 afterwards. That is an observed reduction of 80% in partitions scanned **only if those numbers are actual measurements**. It does not imply an 80% reduction in latency, credits, or total work. For this lesson, no such benchmark has been run; learners must fill the table with their own observations.

---

# Part 5 — Hands-on lab: `experiments/03_micro_partitions/`

## 19. Lab goal and safety

Follow the roadmap experiment sequence: generate 100 million rows ordered by date, measure date-range pruning, randomize the load order, evaluate a clustering key with `SYSTEM$CLUSTERING_INFORMATION`, track maintenance credits, test a non-clustered filter, and decide whether the key was worth its cost.

This lab can be compute- and storage-intensive. **100 million rows is the roadmap target, not a requirement to incur uncontrolled cost.** Run it in a dedicated sandbox database/schema, use a warehouse with a known size and auto-suspend policy, and set a budget/credit guardrail appropriate to your account. Do not run the full version in production without explicit approval.

### Privileges and prerequisites

You need:

- A dedicated, disposable database/schema namespace for this run, with permission to create and drop tables. Use a unique schema name (for example, `LAB_SCHEMA_MP_20261019`) and stop if it already exists.
- Usage on the selected warehouse, database, and schema. Use a dedicated or explicitly approved warehouse that is already configured with appropriate auto-suspend/auto-resume settings. **Do not alter a shared warehouse for this lab.**
- Permission to run the clustering information function and query the relevant query history.
- Additional privileges such as `OWNERSHIP` on the table and schema-level `ADD SEARCH OPTIMIZATION` if you optionally test SOS; do not perform that optional operation unless authorized.
- Access to account usage/history views may require elevated monitoring privileges. If unavailable, record that cost data could not be observed rather than assuming zero cost.

**Collision safety:** the lab DDL intentionally uses `CREATE` rather than `CREATE OR REPLACE` for objects it creates. If a create statement reports that an object already exists, stop and choose a new lab schema/name; do not continue and do not run cleanup against objects you did not create.

### Dataset size choices

| Scale | When to use it | Limitations |
|---|---|---|
| 1 million rows | First syntax check and low-cost trial | May be too small for a stable, obvious layout difference |
| 10 million rows | Moderate experiment where 100M is not feasible | Still may not reproduce multi-terabyte production behavior |
| 100 million rows | Roadmap target for a stronger comparison | Can consume substantial compute, sorting, storage, and maintenance credits |

Choose one scale and write it in your lab notes. A smaller dataset is acceptable if the result is described as a scaled-down experiment and the conclusions are appropriately limited. Do not infer production-scale cost from row count alone; row width, compression, warehouse size, concurrency, and data distribution all matter.

## 20. Create the lab schema and source dataset

Replace `LAB_DB.LAB_SCHEMA` with a sandbox location you control. Choose the row count deliberately; the following example uses 1 million rows so it is safer as a first run. Change `ROWCOUNT` only after you understand the expected cost.

```sql
-- LAB_DB must already exist. Choose a unique schema name before running.
CREATE SCHEMA LAB_DB.LAB_SCHEMA;

-- Select a dedicated/pre-approved warehouse that is already configured safely.
-- Replace LAB_WH with that warehouse; do not change a shared warehouse's settings.
USE WAREHOUSE LAB_WH;

CREATE TABLE LAB_DB.LAB_SCHEMA.EVENTS_SOURCE AS
SELECT
    SEQ4() AS EVENT_ID,
    DATEADD(
        day,
        UNIFORM(0, 1095, RANDOM(42)),
        '2022-01-01'::DATE
    ) AS EVENT_DATE,
    UNIFORM(1, 1000000, RANDOM(7)) AS CUSTOMER_ID,
    CASE UNIFORM(1, 5, RANDOM(11))
      WHEN 1 THEN 'view'
      WHEN 2 THEN 'click'
      WHEN 3 THEN 'purchase'
      WHEN 4 THEN 'login'
      ELSE 'other'
    END AS EVENT_TYPE,
    'payload-' || UNIFORM(1, 100000, RANDOM(19))::VARCHAR AS PAYLOAD_TOKEN
FROM TABLE(GENERATOR(ROWCOUNT => 1000000));

SELECT COUNT(*) AS ROWS_CREATED
FROM LAB_DB.LAB_SCHEMA.EVENTS_SOURCE;
```

**Before scaling:** verify the exact row count. `GENERATOR(ROWCOUNT => ...)` is a compile-time row-count argument; choose the number before executing. The example columns are intentionally simple and do not mimic every production data shape. `SEQ4()` is used as an identifier for the experiment; do not rely on sequence values as gap-free business identifiers. Random distributions and generated values are illustrative. If your account's SQL parser or supported function behavior differs, test with a smaller row count and adjust according to current Snowflake SQL documentation.

For 100 million rows, change the generator row count to `100000000` and execute only when you have approved the cost and time. If the lab uses a 10M scale, record it explicitly. Do not run multiple 100M CTAS operations concurrently.

## 21. Create date-ordered and randomized variants

Create both variants from the same source rows so the comparison is about organization rather than different records.

```sql
-- Variant A: ask the load operation to emit rows in date order.
CREATE TABLE LAB_DB.LAB_SCHEMA.EVENTS_ORDERED AS
SELECT EVENT_ID, EVENT_DATE, CUSTOMER_ID, EVENT_TYPE, PAYLOAD_TOKEN
FROM LAB_DB.LAB_SCHEMA.EVENTS_SOURCE
ORDER BY EVENT_DATE, EVENT_ID;

-- Variant B: deterministic hash ordering approximates a mixed load order.
CREATE TABLE LAB_DB.LAB_SCHEMA.EVENTS_RANDOMIZED AS
SELECT EVENT_ID, EVENT_DATE, CUSTOMER_ID, EVENT_TYPE, PAYLOAD_TOKEN
FROM LAB_DB.LAB_SCHEMA.EVENTS_SOURCE
ORDER BY HASH(EVENT_ID);
```

The `ORDER BY` clauses express the intended output order for CTAS, but do not treat them as a guarantee of exact physical partition boundaries or perfect clustering. The observed layout is what matters. Sorting can be expensive and can spill; check Query Profile for the CTAS statements too. For a large dataset, run these operations sequentially and retain only the variants needed for the experiment.

Check row counts and a basic summary:

```sql
SELECT 'SOURCE' AS TABLE_NAME, COUNT(*) AS ROWS
FROM LAB_DB.LAB_SCHEMA.EVENTS_SOURCE
UNION ALL
SELECT 'ORDERED', COUNT(*) FROM LAB_DB.LAB_SCHEMA.EVENTS_ORDERED
UNION ALL
SELECT 'RANDOMIZED', COUNT(*) FROM LAB_DB.LAB_SCHEMA.EVENTS_RANDOMIZED;

SELECT MIN(EVENT_DATE), MAX(EVENT_DATE), COUNT(DISTINCT EVENT_TYPE)
FROM LAB_DB.LAB_SCHEMA.EVENTS_ORDERED;
```

The row counts should match. If they do not, stop and investigate before comparing performance.

## 22. Baseline date-range queries

Run equivalent queries on each variant. Use a selective date range and then a broader range. Do not add a clustering key yet.

```sql
-- Ordered table: narrow range
SELECT EVENT_TYPE, COUNT(*) AS EVENT_COUNT
FROM LAB_DB.LAB_SCHEMA.EVENTS_ORDERED
WHERE EVENT_DATE >= '2023-04-01'::DATE
  AND EVENT_DATE <  '2023-04-08'::DATE
GROUP BY EVENT_TYPE;

-- Randomized table: same predicate
SELECT EVENT_TYPE, COUNT(*) AS EVENT_COUNT
FROM LAB_DB.LAB_SCHEMA.EVENTS_RANDOMIZED
WHERE EVENT_DATE >= '2023-04-01'::DATE
  AND EVENT_DATE <  '2023-04-08'::DATE
GROUP BY EVENT_TYPE;

-- Repeat with a broader range, for example one quarter.
SELECT COUNT(*)
FROM LAB_DB.LAB_SCHEMA.EVENTS_ORDERED
WHERE EVENT_DATE >= '2023-04-01'::DATE
  AND EVENT_DATE <  '2023-07-01'::DATE;
```

For each query:

1. Record the query ID.
2. Open Query Profile.
3. Record partitions scanned and total, bytes scanned, execution time, and cache/warehouse conditions.
4. Capture the exact predicate and table name in your notes.
5. Repeat under comparable conditions.

**Expected behavior, not a guaranteed result:** the ordered variant will often have narrower date ranges per micro-partition and better pruning for date filters. The randomized variant will often have more overlap. If this pattern does not appear, check the actual table size, whether the CTAS layout was preserved, the date distribution, and Query Profile. Never invent or fill in expected partition counts.

## 23. Inspect clustering information before changing the table

```sql
SELECT SYSTEM$CLUSTERING_INFORMATION(
  'LAB_DB.LAB_SCHEMA.EVENTS_ORDERED',
  '(EVENT_DATE)'
);

SELECT SYSTEM$CLUSTERING_INFORMATION(
  'LAB_DB.LAB_SCHEMA.EVENTS_RANDOMIZED',
  '(EVENT_DATE)'
);
```

Save the complete returned JSON and record the table scale, query ID if available, and observation time. Compare `average_depth`, `average_overlaps`, partition counts, and histogram fields where returned. A candidate-key measurement is diagnostic; it does not apply the key to the table.

## 24. Add a clustering key to a separate test variant

Do not overwrite your baseline tables. Use a separate variant so the before/after comparison remains available.

```sql
CREATE TABLE LAB_DB.LAB_SCHEMA.EVENTS_CLUSTER_TEST AS
SELECT EVENT_ID, EVENT_DATE, CUSTOMER_ID, EVENT_TYPE, PAYLOAD_TOKEN
FROM LAB_DB.LAB_SCHEMA.EVENTS_RANDOMIZED;

ALTER TABLE LAB_DB.LAB_SCHEMA.EVENTS_CLUSTER_TEST
  CLUSTER BY (EVENT_DATE);
```

Defining the key does not mean all rows have already been reclustered. Allow background maintenance to run as appropriate, then re-check:

```sql
SELECT SYSTEM$CLUSTERING_INFORMATION(
  'LAB_DB.LAB_SCHEMA.EVENTS_CLUSTER_TEST'
);

SELECT SYSTEM$CLUSTERING_INFORMATION(
  'LAB_DB.LAB_SCHEMA.EVENTS_CLUSTER_TEST',
  '(EVENT_DATE)'
);
```

Run the same date-range queries and compare profiles. Do not force an arbitrary wait time or claim a completed reclustering state based only on elapsed time. Record when you measured and whether the clustering information changed. On small tables, Snowflake may decide that reclustering is not useful; that is a valid observation.

## 25. Track clustering cost

Where permissions and account history permit, inspect the current account's automatic clustering history:

```sql
SELECT
    TO_DATE(START_TIME) AS USAGE_DATE,
    DATABASE_NAME,
    SCHEMA_NAME,
    TABLE_NAME,
    VERSION,
    SUM(CREDITS_USED) AS CREDITS_USED
FROM SNOWFLAKE.ACCOUNT_USAGE.AUTOMATIC_CLUSTERING_HISTORY
WHERE START_TIME >= DATEADD(day, -14, CURRENT_TIMESTAMP())
  AND DATABASE_NAME = 'LAB_DB'
  AND SCHEMA_NAME = 'LAB_SCHEMA'
GROUP BY 1, 2, 3, 4, 5
ORDER BY USAGE_DATE DESC, CREDITS_USED DESC;
```

Check the view schema first if the query errors. Account Usage data can be delayed and current Optima Clustering may expose a different history/cost model than Clustering Classic. Record one of the following accurately:

- Actual credits observed and the period covered.
- No matching history rows were visible yet (not equivalent to zero cost).
- Cost could not be observed due to privileges or view availability.

Where supported, evaluate `SYSTEM$ESTIMATE_AUTOMATIC_CLUSTERING_COSTS` before enabling or changing a key on a large table. Verify its current signature and output in official documentation; estimates are not actual billing.

## 26. Test a frequently filtered non-clustered column

`CUSTOMER_ID` is deliberately not in the `EVENT_DATE` clustering key. Test a selective customer lookup on each table:

```sql
SELECT EVENT_DATE, EVENT_TYPE, PAYLOAD_TOKEN
FROM LAB_DB.LAB_SCHEMA.EVENTS_CLUSTER_TEST
WHERE CUSTOMER_ID = 424242;
```

Compare with the same predicate on the ordered and randomized baselines. Because `CUSTOMER_ID` values are distributed independently of date, a date key may not improve this query. That is an expected hypothesis, not a guaranteed outcome. Record partitions scanned/total and bytes scanned. If the workload truly consists of highly selective customer-ID point lookups, evaluate Search Optimization Service in a separate authorized experiment rather than adding `CUSTOMER_ID` to the clustering key without evidence.

Optional, only with the necessary privileges and after estimating cost:

```sql
-- Optional; may build access paths and consume credits.
ALTER TABLE LAB_DB.LAB_SCHEMA.EVENTS_CLUSTER_TEST
  ADD SEARCH OPTIMIZATION ON EQUALITY(CUSTOMER_ID);
```

After the service has built the access path, repeat the query and compare Query Profile and latency. A small lab may not show a material improvement, and enabling SOS solely to see whether it works can cost more than the learning value. Do not enable it on the 100M-row variant unless the cost has been approved.

## 27. Decide whether the key was worth its cost

Use this decision record. Complete it with your own measurements; do not replace missing values with guesses.

| Question | Evidence to collect | Decision implication |
|---|---|---|
| Did date pruning improve? | Same predicate, comparable Query Profiles | If no meaningful change, do not claim a clustering benefit |
| Did latency improve consistently? | Repeated runs, cache/warehouse conditions | A single fast run is insufficient |
| Did bytes scanned or partitions scanned fall? | Query Profile | Confirms scan reduction more directly than latency alone |
| Did the table have enough micro-partitions to benefit? | Total partition count and table size | Small tables often do not justify maintenance |
| What did clustering maintenance cost? | Actual history/estimate, version, period | Include credits in the total cost comparison |
| Did a non-clustered filter benefit? | Profile for `CUSTOMER_ID` predicate | If not, the date key may not help that workload |
| How often does the table change? | DML/load cadence | Frequent DML can increase maintenance needs |
| Does ingestion-time ordering suffice? | Ordered vs randomized baseline | If natural order meets the need, a key may be unnecessary |
| Is there a better specialized option? | Point-lookup selectivity, supported SOS predicates, repeated aggregates | Evaluate SOS or materialization only when their use case and cost fit |

**Recommended conclusion format:** “For dataset scale ___, query pattern ___, and observation period ___, the key [did/did not/could not be shown to] improve ___ by the measured amount ___. Maintenance cost was ___. The result [does/does not] justify a production trial because ___. Limitations are ___.”

## 28. Lab cleanup

The tables can consume storage until dropped and retention behavior completes. Remove only objects successfully created by this run, and only after confirming the database/schema and object names belong exclusively to this lab. If any initial `CREATE` failed because of a name collision, do not run these drops against that pre-existing object. Drop tables first; drop the schema only if this run created it and it contains no other work. The warehouse is assumed to be pre-existing and is not dropped or modified.

```sql
DROP TABLE IF EXISTS LAB_DB.LAB_SCHEMA.EVENTS_CLUSTER_TEST;
DROP TABLE IF EXISTS LAB_DB.LAB_SCHEMA.EVENTS_RANDOMIZED;
DROP TABLE IF EXISTS LAB_DB.LAB_SCHEMA.EVENTS_ORDERED;
DROP TABLE IF EXISTS LAB_DB.LAB_SCHEMA.EVENTS_SOURCE;

-- Optional, only if this run created the schema and it is empty afterward:
-- DROP SCHEMA LAB_DB.LAB_SCHEMA;
```

Do not drop the schema or warehouse if they are shared by other labs or users. Verify the lab object's names before cleanup. Dropping a table does not necessarily mean every retained historical micro-partition disappears immediately because Time Travel and Fail-safe retention can apply.

---

# Part 6 — Production operations and troubleshooting

## 29. Production checklist

Before adding a clustering key:

- [ ] Identify the top query patterns and confirm they filter or sort on the proposed dimensions.
- [ ] Record a baseline from Query Profile and query history.
- [ ] Check table size, micro-partition count, selectivity, and current clustering information.
- [ ] Evaluate whether natural ingestion order already supports pruning.
- [ ] Consider sort-at-load cost, automatic clustering version, and DML cadence.
- [ ] Estimate and then monitor maintenance credits using the relevant current cost model.
- [ ] Include storage churn and retention in the cost review.
- [ ] Change one table/key at a time and retain a rollback plan.
- [ ] Recheck the workload after the change; do not use depth alone as the success metric.

## 30. Troubleshooting guide

| Symptom | Possible causes | What to check next |
|---|---|---|
| Date query scans most partitions | Data is randomized; ranges overlap; predicate is broad; query uses a different dimension | Inspect min/max behavior via clustering information, predicate shape, and Query Profile |
| Depth is low but query is not faster | Query already scans little data; bottleneck is compute, joins, sorting, queueing, or output; caching differs | Inspect the full Query Profile, warehouse state, and repeated runs |
| Depth is high but clustering cost is not justified | Table/query volume is low; filters are not selective; the key does not match workload | Reassess query history and total cost before further maintenance |
| New key does not immediately change results | Existing rows may not have been reclustered yet; table is too small to benefit; maintenance not triggered | Monitor clustering information and maintenance history; avoid assuming an exact completion time |
| DML causes maintenance to rise | Updates/merges/inserts overlap existing key ranges; changes are frequent or scattered | Review DML cadence, batch where possible, compare query savings with maintenance cost |
| `SYSTEM$CLUSTERING_INFORMATION` errors | Incorrect identifier/quoting, missing argument for an unclustered table, unsupported expression, privilege issue | Check fully qualified name, string argument syntax, function docs, and role privileges |
| History query returns no rows | Account Usage delay, no activity yet, wrong object filter, missing privileges, different clustering implementation | Check view schema, wider time window, correct database/schema, and current cost model |
| Date clustering does not help customer ID lookup | Key aligns to date, not customer ID; min/max ranges still overlap for customer ID | Test supported SOS for selective equality lookups; benchmark before enabling |
| SOS shows no benefit | Access path not ready, predicate unsupported, filter not selective, table too small, profile not comparable | Check service status, supported predicates, query profile, and cost before proceeding |
| External-table query scans too much | File layout/partition columns poorly designed; metadata stale; many files selected | Inspect external partition columns, file paths, refresh state, and file sizing |
| Iceberg behavior differs from native table | Iceberg metadata and feature support differ; management mode or partition transforms differ | Inspect Iceberg metadata/layout and verify support for the exact table configuration |

## 31. Common mistakes to avoid

1. **Clustering small tables by default.** The potential savings may be negligible relative to maintenance and complexity.
2. **Treating 1 TB as a hard threshold.** It is a roadmap heuristic; workload evidence is decisive.
3. **Clustering on a very high-cardinality column without a workload reason.** Cardinality alone is not a selection rule; point lookups may call for SOS.
4. **Assuming a clustering key is an index.** It changes the target data organization and has maintenance costs; it does not guarantee a point lookup touches one partition.
5. **Assuming `ORDER BY` guarantees perfect physical layout.** Inspect the resulting layout and Query Profile.
6. **Ignoring `MERGE`/`UPDATE`/`DELETE` effects.** DML can change the organization and increase background work.
7. **Comparing only elapsed time.** Include partitions scanned, bytes scanned, credits, queueing, spill, caching, and maintenance.
8. **Assuming a lower clustering depth guarantees faster queries.** Depth is a layout diagnostic, not a workload outcome.
9. **Assuming no cost because a history query is empty.** Permissions, latency, filters, and implementation can explain missing rows.
10. **Ignoring materialized-view maintenance.** Base-table DML and reclustering can create extra work for dependent views.
11. **Applying native-table assumptions to external and Iceberg tables.** Their pruning metadata and maintenance models differ.
12. **Enabling SOS across every column.** Start with selective, supported predicates and an approved cost case.
13. **Treating expected lab behavior as measured data.** Only values captured from the learner's own account are measurements.

---

# Part 7 — Practice questions with answers

### 1. What is a Snowflake micro-partition?

**Answer:** An automatically created, immutable, compressed, columnar storage unit. The roadmap gives an approximate size of 50–500 MB uncompressed. Snowflake maintains metadata that helps identify which partitions may contain matching rows.

### 2. How does partition pruning work?

**Answer:** Snowflake compares query predicates with micro-partition metadata. If metadata proves a partition cannot contain a matching row, the partition can be skipped. Candidate partitions still need to be scanned and filtered.

### 3. Why can date-ordered loads improve date pruning?

**Answer:** Adjacent partitions may cover narrower, more localized date ranges. A date predicate can exclude partitions whose ranges do not intersect the predicate. This is an expected tendency, not a guarantee.

### 4. What is clustering depth?

**Answer:** A summary of overlap depth for the selected clustering dimensions. Lower depth generally indicates better clustering for those dimensions, but does not directly predict query latency or cost.

### 5. What does `SYSTEM$CLUSTERING_INFORMATION` do?

**Answer:** It returns clustering diagnostics for a table's defined key or a specified set of columns/expressions. For an unclustered table, supply the candidate dimensions. Use the output to compare layout, not as a substitute for query benchmarking.

### 6. Is a high-cardinality column always a good clustering key?

**Answer:** No. The key must match important query patterns and support useful partition exclusion. High cardinality alone is not enough; a selective point lookup may be better suited to Search Optimization Service.

### 7. When is clustering worth evaluating?

**Answer:** Commonly on very large tables with selective, recurring queries aligned to a small number of dimensions, especially when the table is queried much more often than it is changed. The roadmap's approximately 1 TB guideline is a heuristic, not a rule.

### 8. What costs should be counted when clustering a table?

**Answer:** Query costs before/after, automatic-clustering maintenance under the applicable implementation, possible storage churn and retention, ingestion/sort costs, and operational overhead. Do not compare query runtime alone.

### 9. Why can `MERGE` and `UPDATE` affect clustering?

**Answer:** DML changes data distribution and may result in new micro-partitions whose ranges overlap existing partitions. Snowflake can then determine that background reclustering is beneficial. Not every DML statement causes immediate reclustering.

### 10. When should Search Optimization Service be considered?

**Answer:** For supported, highly selective lookup patterns expected to return few rows, including some equality/`IN` predicates and specified semi-structured searches. It has feature requirements and build/maintenance costs.

### 11. How are materialized views different from dynamic tables?

**Answer:** Materialized views precompute results for supported repeated query patterns over a base table and maintain those results automatically. Dynamic tables define materialized transformation results with managed refresh and target-lag semantics. Both incur storage/compute and are not interchangeable in every use case.

### 12. Why should external-table pruning not be described as native micro-partition pruning?

**Answer:** External tables query files outside Snowflake and use external-table metadata, including file paths and declared partition columns, to prune files. Native micro-partition storage and clustering-key maintenance do not apply in the same way.

### 13. What is different about Iceberg pruning?

**Answer:** Iceberg relies on Iceberg snapshots/manifests and file/partition metadata. Its behavior and supported operations depend on table management mode and feature support. Do not assume native Snowflake clustering-key features apply identically.

### 14. If partitions scanned decrease by 80%, did query cost decrease by 80%?

**Answer:** Not necessarily. Query operators, warehouse time, cache, result size, queueing, and service maintenance all contribute to cost and latency. The 80% figure describes only the measured partition-count reduction if it came from actual profile values.

### 15. What evidence should justify keeping a clustering key?

**Answer:** Repeatable improvement for representative queries, reduced unnecessary scanning or other measured workload benefit, and total query savings that justify maintenance credits, storage impact, and operational cost.

---

# Roadmap checkpoint

Use this checklist to confirm the Topic 03 outcomes:

- [ ] Explain micro-partitions and pruning.
- [ ] Read and interpret clustering information.
- [ ] Choose clustering keys and justify the cost.
- [ ] Explain why DML can disturb clustering.
- [ ] Predict pruning for three filter shapes on date-ordered data.
- [ ] Draw overlapping versus well-clustered micro-partitions.
- [ ] Compare ordered and randomized layouts using actual Query Profile data.
- [ ] Evaluate a non-clustered filter and distinguish clustering from Search Optimization.
- [ ] Explain the differences between native, external, and Iceberg table pruning.
- [ ] Distinguish measured results from expected behavior and document the limits of the experiment.

**You are ready for Topic 04 — Stages, `COPY INTO`, and Snowpipe when you can explain how ingestion order influences initial data organization and how to validate pruning and maintenance cost using evidence rather than assumptions.**

---

# References

Use current official documentation because feature support, clustering implementation, and cost models can evolve.

1. [Micro-partitions and data clustering](https://docs.snowflake.com/en/user-guide/tables-clustering-micropartitions)
2. [Clustering keys and clustered tables](https://docs.snowflake.com/en/user-guide/tables-clustering-keys)
3. [`SYSTEM$CLUSTERING_INFORMATION`](https://docs.snowflake.com/en/sql-reference/functions/system_clustering_information)
4. [`SYSTEM$CLUSTERING_DEPTH`](https://docs.snowflake.com/en/sql-reference/functions/system_clustering_depth)
5. [Automatic Clustering](https://docs.snowflake.com/en/user-guide/tables-auto-reclustering)
6. [Automatic Clustering history view](https://docs.snowflake.com/en/sql-reference/account-usage/automatic_clustering_history)
7. [`SYSTEM$ESTIMATE_AUTOMATIC_CLUSTERING_COSTS`](https://docs.snowflake.com/en/sql-reference/functions/system_estimate_automatic_clustering_costs)
8. [Optimizing storage for performance](https://docs.snowflake.com/en/user-guide/performance-query-storage)
9. [Search Optimization Service — point lookup queries](https://docs.snowflake.com/en/user-guide/search-optimization/point-lookup-queries)
10. [Search optimization for semi-structured data](https://docs.snowflake.com/en/user-guide/search-optimization/semi-structured-queries)
11. [Working with materialized views](https://docs.snowflake.com/en/user-guide/views-materialized)
12. [Views, materialized views, and dynamic tables](https://docs.snowflake.com/en/user-guide/overview-view-mview-dts)
13. [Introduction to external tables](https://docs.snowflake.com/en/user-guide/tables-external-intro)
14. [Iceberg table metadata and retention](https://docs.snowflake.com/en/user-guide/tables-iceberg-metadata)

