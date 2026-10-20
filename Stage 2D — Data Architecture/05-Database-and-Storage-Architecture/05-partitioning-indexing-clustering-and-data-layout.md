# Partitioning, Indexing, Clustering and Data Layout

> **Stage:** 2D — Data Architecture  
> **Module:** 05 — Database and Storage Architecture  
> **Topic:** 5 of 7  
> **Scope:** Vendor-neutral architectural reasoning. This lesson designs and validates logical data layout; it does not prescribe a product-specific physical implementation.

---

## 1. Learning objectives

By the end of this lesson, you should be able to:

1. Explain **partitioning**, **indexing**, **clustering**, **sorting**, **pruning**, **selectivity**, **cardinality**, **skew**, **hotspot**, and **data layout** in precise terms.
2. Distinguish logical partitioning from physical storage organization, and explain why the terms and available controls vary among database engines, storage engines, file formats, and table formats.
3. Start from query patterns and workload evidence rather than choosing a layout technique first.
4. Select candidate partition keys and granularity while considering pruning, cardinality, partition/file counts, metadata overhead, skew, small files, write amplification, and maintenance.
5. Explain when an index is useful, what it costs, and why an index that benefits one query may hurt ingestion or other workloads.
6. Explain how clustering and sorting improve locality and data skipping, and why neither is interchangeable with partitioning or indexing.
7. Calculate average partition size, approximate file counts, and a skew ratio from stated assumptions.
8. Design a query-traceable layout for analytical transaction history and an operational ledger, including a deliberately rejected option.
9. Define a repeatable validation experiment with a representative query set, baseline, candidate layout, measurements, and pass/fail criteria.
10. Account for the total cost of a layout: read performance, write throughput, storage, maintenance jobs, operational risk, and workload drift.

**Core rule:** every proposed layout element must name the query pattern it is intended to improve, the assumption that makes it relevant, and the measurement that would confirm or reject its value.

---

## 2. Why the topic matters in real-world data architecture

Two systems can hold the same records and use similar compute capacity yet behave very differently. The difference may be how the data are organized and how much irrelevant data a query must inspect.

Imagine a filing room containing five years of transaction records. If files are grouped by date, a request for last Tuesday's records can ignore most of the room. If files are randomly mixed, the same request may require checking many more folders. An index is more like a directory that points toward particular records. Clustering is like placing similar records close together within the folders. These are related ideas, but they solve different problems.

At production scale, layout affects more than read latency:

- **Read cost:** how many partitions, files, pages, or records must be inspected.
- **Write cost:** how much work is required to route incoming records, update indexes, maintain ordering, or rewrite data.
- **Concurrency:** whether many writers contend for the same partition, index structure, or physical region.
- **Storage:** how much space the data and supporting structures consume.
- **Operations:** compaction, reclustering, index rebuilds, statistics refreshes, and partition maintenance.
- **Reliability:** whether maintenance can keep up with ingestion and whether failures leave a backlog.
- **Adaptability:** whether the design still fits after query patterns, data volume, or distributions change.

A layout is an architectural choice because it creates long-lived assumptions about access patterns, data distribution, maintenance capacity, and acceptable cost. It is not a one-time trick to make a benchmark query faster.

### 2.1 The concepts in one table

| Concept | Precise working definition | Primary question it answers |
|---|---|---|
| **Data layout** | The logical and physical organization of data and the metadata used to find and read it | How is data arranged for this workload? |
| **Partitioning** | Dividing a dataset into separately identifiable subsets using a key, range, hash, or other rule | Which subsets can be excluded before reading? |
| **Sharding** | Distributing data across separate nodes, instances, or independently managed storage units; the routing and failure boundaries depend on the system | How is data distributed across serving/storage units, and where is each key routed? |
| **Indexing** | Maintaining an auxiliary access structure that helps locate matching records or pages | Can the system find matching rows without scanning all candidate data? |
| **Clustering** | Organizing records or storage units so related values are physically close or grouped | Can locality and data-skipping metadata reduce work? |
| **Sorting** | Ordering records by one or more keys within a defined scope | Can ordered access, range processing, or data skipping become cheaper? |
| **Pruning** | Skipping partitions, files, row groups, pages, or index branches that cannot match a query | What data can safely be avoided? |
| **Selectivity** | The fraction of candidate rows that satisfy a predicate; lower fractions are more selective | How many rows remain after a filter? |
| **Cardinality** | The number of distinct values in a column or key, or the number of resulting groups/partitions depending on context | How many distinct values or units will this choice create? |
| **Skew** | Uneven distribution of data or work across keys, partitions, workers, or storage units | Is one unit much larger or busier than the others? |
| **Hotspot** | A key, partition, node, or storage region receiving disproportionate traffic or writes | Where is contention or overload concentrated? |

**Terminology caution:** database products do not all use *partition*, *cluster*, *sort*, or *index* in exactly the same way. In analytical file/table systems, partitioning may mean directory- or metadata-level grouping and clustering may mean periodic file reorganization. In a relational database, partitioning may be implemented inside one logical table and an index may be a B-tree, hash, bitmap, or another structure. A design must name the actual mechanism once the implementation is selected.

### 2.2 Logical partitioning versus physical organization

- **Logical partitioning** describes how records are assigned to named subsets, for example `event_date = 2026-10-19`. A query with a compatible date predicate may be able to eliminate unrelated subsets.
- **Physical organization** describes how data are actually placed inside those subsets: file boundaries, row ordering, pages, blocks, row groups, indexes, and statistics.
- **Logical table metadata** may describe the partitioning or clustering strategy, but the implementation determines which optimizations are available and whether the data currently satisfy the intended layout.

A partition definition does not guarantee that every partition is a single file, a single node, or a balanced amount of work. Likewise, sorting records does not necessarily create independent partitions, and an index is not the same thing as a partition.

**Partitioning versus sharding:** partitioning describes how a dataset is divided into subsets; sharding specifically emphasizes distributing subsets across distinct serving or storage units. Some systems use the terms differently or implement partitioning across nodes, so confirm the product's semantics. Do not assume that a logical partition is a shard, that each partition resides on one node, or that adding partitions automatically spreads load. A sharding proposal must also account for routing, cross-shard queries/joins, rebalancing, availability, and hotspot behavior.

### 2.3 Why query patterns come first

A layout should follow the workload, not the other way around. Before suggesting a key or index, record:

- filter predicates: equality, `IN`, ranges, and combinations;
- join keys and expected join sizes;
- grouping and aggregation columns;
- ordering and pagination requirements;
- query frequency and concurrency;
- data volume, growth, ingestion rate, and peak rate;
- freshness, latency, and correctness targets;
- updates, deletes, late-arriving records, and correction patterns;
- retention and access constraints;
- read/write trade-offs and operational capacity.

A date partition may be excellent for daily reports and weak for a customer lookup spanning all dates. An index may help a selective point lookup and contribute little to a query that reads most of a table. A cluster order may help one range predicate but be less useful for another column. These are testable hypotheses, not universal rules.

---

## 3. Prerequisite knowledge

This topic assumes that you have completed Topics 1–4 of this module.

| Prerequisite | What you should already know | How it is used here |
|---|---|---|
| Topic 1 — OLTP and OLAP separation | Transactional versus analytical workloads, latency and throughput differences | Decide whether a layout belongs in an operational store, analytical store, or both |
| Topic 2 — Database and specialized-store selection | Workload-first selection, access patterns, transactions, data models, scaling | Avoid using layout optimization to compensate for an unsuitable store |
| Topic 3 — Object storage and file formats | Object storage behavior, row/column-oriented formats, compression, small files, compaction | Estimate file counts and understand how layout is represented in files |
| Topic 4 — Warehouse, lakehouse, and table formats | Storage versus table-management layer, catalogs, snapshots, metadata, engine capabilities | Determine which layout controls the selected table system actually supports |
| 2D.2 Topic 3 — Volume, velocity, variety and growth | Volume and peak-load estimation | Quantify partition size, growth, and load imbalance |
| 2D.4 Topic 4 — Facts, dimensions and grain | What one row represents; facts, dimensions, and granularity | Avoid designing layout before defining the data grain |

### 3.1 A prerequisite check

For a transaction-history table, you should be able to answer:

1. What does one row represent: one authorization attempt, one posted ledger entry, or one transaction lifecycle?
2. Which queries are common, and what predicates do they use?
3. Which store and table-management capabilities are available?
4. Is the data append-only, corrected in place, or subject to updates and deletes?
5. What volume and retention assumptions are being used?

If the row grain, access patterns, or storage capabilities are unknown, the layout recommendation is premature. Record the gap and resolve it before treating the design as final.

---

## 4. Beginner-level learning sequence

### 4.1 Partitioning: divide the data into useful subsets

**What it is:** partitioning assigns records to separately identifiable subsets using a rule such as a date range, a key value, or a hash bucket.

**How it works:** if a query predicate is compatible with the partition rule and the engine can reason about it, the engine can exclude partitions that cannot contain qualifying rows. This is **partition pruning**.

Example query pattern:

```sql
-- Illustrative SQL; assumes event_date is a typed date column.
SELECT COUNT(*) AS transaction_count
FROM transaction_history
WHERE event_date >= DATE '2026-10-01'
  AND event_date <  DATE '2026-10-08';
```

If the table is partitioned by `event_date` at daily granularity and the predicate is usable by the engine, partitions outside the seven-day range may be skipped. This is an expected mechanism, not a measured performance result. Actual pruning depends on the system, table metadata, predicate form, statistics, and layout.

**When to consider it**
- Queries repeatedly filter by a stable date or another bounded key.
- The dataset is large enough that skipping subsets is valuable.
- The chosen key and granularity yield manageable subset sizes and counts.
- Ingestion and maintenance can route data into those subsets reliably.

**When not to use it**
- The table is small enough that a simpler layout is sufficient.
- The key has very high cardinality and would create too many tiny subsets.
- Common queries rarely filter on the proposed key.
- The distribution is highly skewed and no mitigation or alternative layout is justified.

**Costs and risks**
- More partitions create more metadata and planning work.
- Small partitions can generate small files and increase scheduling overhead.
- Inserts, late arrivals, and corrections may touch many partitions.
- A key such as `customer_id` can create millions of logical subsets if used directly.
- A time key can concentrate current writes in the newest partition or partition range.

**How to validate:** compare the baseline and candidate with the same representative queries; inspect partitions/files read and bytes scanned where available; confirm result correctness; measure write and maintenance overhead.

#### Partitioning terminology

- **Partition key:** the value or expression used to assign records to a partition.
- **Partition granularity:** how broad each partition is, such as month, day, or hour.
- **Partition cardinality:** the number of distinct partition values/units expected over the relevant data horizon.
- **Partition pruning:** excluding partitions that cannot satisfy the query.
- **Partition imbalance:** material differences in partition sizes or work.

### 4.2 Indexing: create an additional path to the data

**What it is:** an index is an auxiliary structure that helps a system locate rows, pages, or data ranges without inspecting every candidate record.

An index might map a customer identifier to record locations or organize key values in a searchable tree. The exact structure and behavior depend on the engine. Some analytical engines use different forms of indexes or data-skipping metadata; some scans rely mainly on partition metadata, file statistics, and columnar layout rather than conventional row indexes.

**When to consider it**
- Queries repeatedly perform selective point lookups or narrow ranges.
- The selected store supports an index suitable for the access pattern.
- The read benefit is worth index storage and write/maintenance cost.
- The index can be kept consistent with writes and corrections.

**When not to use it**
- Queries read a large fraction of the table.
- The store or query engine does not use the proposed index.
- The column has low selectivity for the relevant predicates.
- Write volume is high and index maintenance threatens ingestion targets.
- The index duplicates an existing access path without demonstrated benefit.

**Costs and risks**
- Additional storage and metadata.
- Work to update the index on inserts, updates, and deletes.
- Rebuild, statistics, and repair operations.
- Potential contention or write amplification.
- Indexes can become stale or less useful as data distribution changes.

**How to validate:** capture query plans or index usage where available, compare latency and reads for the target query, measure ingestion throughput and maintenance duration, and test representative writes as well as reads.

### 4.3 Clustering and sorting: keep related values close

**Clustering** groups related records or storage units physically, while **sorting** establishes an order by one or more columns within a scope. Depending on the engine, these can be related features but are not synonymous. Sorting by `merchant_id` may place similar merchant values near each other; clustering may reorganize files or blocks to improve locality and data skipping.

For a file-based analytical table, an engine may use minimum/maximum values or other statistics for each file or row group. If values are organized by a commonly filtered column, the engine may skip units whose recorded value range cannot match the predicate. Whether this works depends on the file format, metadata, table management, and query engine.

**When to consider it**
- Queries filter or join repeatedly on columns that are not a good partition key.
- The data are large enough that locality can reduce the amount scanned.
- There is an operational way to maintain the order as data arrive or change.
- The expected benefit applies to a meaningful portion of the workload.

**When not to use it**
- The table is small or queries already read most rows.
- Writes are frequent and maintaining order would be too expensive.
- The clustering key has little relationship to common predicates.
- The engine cannot exploit the resulting layout or statistics.

**Costs and risks**
- Reorganization/compaction consumes compute and I/O.
- New data can degrade the intended order until maintenance runs.
- Multiple access patterns may compete for the same physical organization.
- Reclustering can rewrite data and increase temporary storage or write amplification.

**How to validate:** inspect file/row-group statistics and scan metrics where available, compare bytes and units read for named predicates, measure maintenance cost, and retest after a realistic ingestion cycle.

### 4.4 Do not confuse the techniques

| Technique | What it can skip or improve | Typical scope | Key cost |
|---|---|---|---|
| Partitioning | Whole partitions that cannot match | Logical subsets of a table or dataset | Partition count, routing, metadata, imbalance |
| Indexing | Candidate rows/pages/locations that cannot match | Depends on index and store | Extra structure, write overhead, rebuilds |
| Clustering | Data units with poor locality or nonmatching statistics | Often files, row groups, blocks, or storage regions | Reorganization and maintenance |
| Sorting | Ordered access and locality within a scope | A table, partition, file, or block depending on system | Sorting/rewrite cost; order can degrade |
| Pruning | The act of excluding irrelevant units | Partitions, files, row groups, pages, index branches | Requires usable predicates and trustworthy metadata |

A single architecture may use more than one technique. The question is not “Which technique is best?” but “What is the least costly combination that meets the important workload requirements?”

### 4.5 Selectivity and cardinality

**Selectivity** describes how much of the candidate data satisfies a predicate. If a filter matches 10,000 rows out of 10,000,000 rows, the row-level selectivity is:

\[
\text{selectivity}=\frac{10{,}000}{10{,}000{,}000}=0.001=0.1\%
\]

This is a selective filter at the row level. It does not guarantee that only 0.1% of bytes will be read: if matching rows are scattered across many files/pages and no useful access path exists, the engine may still inspect a large amount of data.

**Cardinality** is context-sensitive:
- column cardinality: number of distinct values;
- partition cardinality: number of distinct partition values or units;
- grouping cardinality: number of output groups.

A high-cardinality customer identifier may be useful for selective lookup but disastrous as a direct partition key if it creates millions of tiny partitions. A low-cardinality status column may not prune enough data by itself, although it may still be useful in combination with another technique.

### 4.6 Beginner exercise: match query patterns to techniques

For each query below, name a likely candidate technique and one limitation. Do not assume the candidate must be implemented.

| Query pattern | Candidate to investigate | Why it may help | Limitation to state |
|---|---|---|---|
| Last 7 days of transactions | Date partitioning | May exclude older partitions | Little benefit for all-history queries |
| Find one transaction by unique ID | Index or native key access path | May locate a narrow record set | Depends on store and index support |
| Aggregate by day over 5 years | Date layout plus scan-efficient file organization | Data is scanned broadly but can be grouped by date | Partitioning may not reduce much if all dates are read |
| Find one merchant across 3 years | Merchant-oriented index, clustering, or alternate access path | Date-only partitioning may read many date partitions | A merchant index or second layout has costs |
| Filter by a low-selectivity status | Test combined predicate/layout; perhaps no new structure | Status alone may match most rows | Index/partition may add cost without pruning |
| Sort results by transaction time | Existing order, index, or engine sort | May reduce sorting work if order can be exploited | Global ordering may still require merge/sort |
| Join two large tables on customer ID | Compatible distribution/partitioning or clustering where supported | May reduce data movement or improve locality | Benefits depend on engine, join strategy, and skew |
| Ingest current events continuously | Layout that spreads writes safely | May reduce write contention | Time-based partition can still concentrate writes |

**Ability to demonstrate:** explain why a technique might help and give at least one case where it would not.

---

## 5. Intermediate-level learning sequence

### 5.1 Step 1 — Build a query-pattern register

Before choosing a key, document the important queries. The following is a template; fill it with observed or explicitly assumed workload evidence.

| ID | Query purpose | Predicates / join keys | Data horizon | Frequency / concurrency | Latency target | Approximate rows or bytes read | Business importance |
|---|---|---|---|---|---|---|---|
| Q1 | Recent transaction monitoring | `event_date` range | Last 24 hours | High / many concurrent readers | Stated by product owner | Estimate from sampled data | High |
| Q2 | Customer transaction history | `customer_id`, date range | 90 days | Medium | Stated by product owner | Estimate | High |
| Q3 | Merchant risk review | `merchant_id`, date range | 3 years | Daily / analyst concurrency | Stated by risk team | Estimate | High |
| Q4 | Daily finance reconciliation | `event_date`, account or ledger key | Daily | Batch window | Must finish by agreed deadline | Estimate | Critical |
| Q5 | Full-history regulatory analysis | Date and risk attributes | 5 years | Periodic | Batch window | Large scan | High |
| Q6 | Operational ledger lookup | Unique entry ID or account key | Current state/history required | High / concurrent reads and writes | Strict operational target | Narrow lookup expected | Critical |

Use workload logs, query plans, stakeholder interviews, representative samples, or explicit assumptions. Do not disguise guesses as measured facts. Record the date and owner of the workload evidence.

For each query, include:
- equality and range predicates;
- join and grouping columns;
- ordering and pagination;
- data horizon and result size;
- frequency and concurrent users/workers;
- read and write rate;
- freshness and latency target;
- whether the query is interactive, scheduled, or batch;
- current bottleneck evidence, if known.

### 5.2 Step 2 — Establish the baseline

A baseline is the current behavior against which the candidate will be compared. Capture:
- query result correctness and row counts;
- p50 and p95 latency for repeated runs where latency matters;
- bytes scanned, partitions/files/pages read, and rows processed where exposed;
- CPU, memory, spill, and data movement where relevant;
- ingestion throughput and write latency;
- maintenance duration and failure rate;
- storage used by indexes, extra copies, metadata, and temporary rewrite data;
- concurrency and queueing behavior.

Do not invent a baseline. If no implementation exists, label the initial estimates as hypotheses and use a prototype or representative benchmark dataset to establish measurements.

### 5.3 Step 3 — Choose candidate partition keys and granularity

A useful partition key often appears in frequent filters and produces subsets large enough to avoid excessive small units, but no universal partition size or cardinality is correct for all systems.

For a first estimate:

```text
partition_count ≈ number of distinct partition values in the retained horizon
average_partition_size ≈ total retained data size / partition_count
```

These formulas assume the data are distributed uniformly across partition values. Real distributions are often uneven, so average size must be accompanied by a skew check.

#### Worked example: daily versus hourly partitions

**Illustrative assumptions:**
- Retained dataset size: 5 TB (decimal units: 1 TB = 1,000 GB).
- Retention horizon: 5 years.
- Approximate daily partition count: 1,825 days.
- Approximate hourly partition count: 43,800 hours.
- Data distribution is treated as uniform for this first estimate only.

**Daily layout**

\[
\text{average size}=\frac{5{,}000\text{ GB}}{1{,}825}
\approx 2.74\text{ GB per daily partition}
\]

**Hourly layout**

\[
\text{average size}=\frac{5{,}000{,}000\text{ MB}}{43{,}800}
\approx 114.16\text{ MB per hourly partition}
\]

Interpretation:
- Daily partitioning gives roughly 1,825 partition units with an average of 2.74 GB each under the stated assumptions.
- Hourly partitioning gives roughly 43,800 partition units with an average of 114 MB each.
- Hourly partitioning may make sense if hourly pruning is important and the system handles that many partitions well; otherwise it may create excess metadata and many small data units.
- Neither result is a universal target. Actual data distribution, compression, file sizing, engine planning overhead, concurrency, and query mix must be measured.

#### File-count estimate

For a partitioned file-based table, an initial estimate may be:

\[
\text{files per partition}\approx
\frac{\text{partition size}}{\text{target file size}}
\]

Assume, illustratively, a target data-file size of 256 MB using decimal units.

For the daily average:

\[
\frac{2{,}740\text{ MB}}{256\text{ MB/file}}
\approx 10.7\text{ files per daily partition}
\]

The average ratio is about 10.70 target-sized files per daily partition. Two different planning estimates are useful, and they should not be confused:

- **Aggregate-volume estimate:** using the unrounded ratio across the full dataset gives about 19,531 target-file equivalents:

  \[
  1{,}825\times 10.702\approx 19{,}531\text{ target-file equivalents}
  \]

- **Per-partition ceiling estimate:** if each of the 1,825 daily partitions is independently packed into whole files no larger than about 256 MB, a simple ceiling calculation gives `ceil(10.702) = 11` files per average partition, or `1,825 × 11 = 20,075` files. This is a conservative arithmetic scenario, not a guarantee about writer output; files may be smaller, multiple writers may create extra files, and actual partitions are not equal-sized.

These estimates differ because rounding each partition separately is not the same as dividing aggregate bytes by target file size. Actual writers create whole files; compression, skew, concurrent writers, late data, and compaction alter the result. Treat the target size as an assumption for planning, not a universal rule or command to pad files.

For the hourly average:

\[
\frac{114.16\text{ MB}}{256\text{ MB/file}}
\approx 0.45
\]

A fractional result does **not** mean a physical file can be fractional. It indicates the average hourly partition is smaller than the target file size. If every nonempty hour produces at least one file, the layout may have at least about 43,800 hourly files across the five-year horizon, many smaller than the target. Whether this is acceptable depends on the table system, metadata handling, and workload.

### 5.4 Step 4 — Estimate selectivity and expected pruning

Partition pruning is most useful when predicates allow the engine to exclude whole partitions. For example:
- a date-range query can often prune a date-partitioned table;
- a query by customer ID alone may still touch many date partitions;
- a query that wraps a partition column in a transformation may or may not be recognized as a compatible range, depending on the engine and expression;
- a predicate that does not reference the partition key may not prune partitions at all.

Do not assume that a logically equivalent predicate produces the same physical plan. Inspect the plan or scan metrics if the engine exposes them.

For a rough partition-level estimate, define:

\[
\text{partition fraction read}=
\frac{\text{partitions expected to be scanned}}
{\text{total partitions}}
\]

If a seven-day query over five years of daily partitions reads seven of 1,825 partitions, the idealized fraction is:

\[
\frac{7}{1{,}825}\approx0.00384=0.384\%
\]

This is a count of partitions, not a guaranteed percentage of bytes scanned. If recent days contain much more data than older days, or the query needs other data units, the byte fraction can differ substantially.

### 5.5 Step 5 — Decide whether an index is justified

Evaluate an index as a workload-specific investment.

| Question | Evidence to collect |
|---|---|
| Is the predicate selective? | Estimated or observed fraction of rows matching |
| Is it frequent or business-critical? | Query frequency, concurrency, and impact |
| Does the engine use this index type? | Documented capability and actual plan/usage evidence |
| What is the read benefit? | Latency, rows/pages visited, bytes read, or other relevant metrics |
| What is the write cost? | Insert/update throughput and latency with/without the index |
| What is the storage cost? | Index bytes, backups/replicas if relevant, and rebuild space |
| What maintenance is needed? | Rebuild, statistics refresh, repair, monitoring, owner |
| Does it hurt other queries? | Representative workload mix, not only the target query |

A low-selectivity index is not automatically useless; a composite index or specialized index may still help in some implementations. Conversely, a high-selectivity column does not guarantee that an index will help if the query engine cannot exploit it or the query reads a large portion of the underlying data.

### 5.6 Step 6 — Evaluate clustering/sorting for locality

Clustering or sorting may be a candidate when a frequently used predicate is not a good partition key. It can improve data skipping when the physical organization makes the relevant values localized and the engine has useful metadata.

A conceptual comparison:

| Design | Example | Likely benefit | Cost or limitation |
|---|---|---|---|
| Partition by date | `event_date` day partitions | Date-range pruning | Queries by merchant across all dates may touch many partitions |
| Cluster/sort within date by merchant | Related merchant values grouped within each date | May skip files/row groups for a merchant predicate within date ranges | Requires supported ordering/statistics and maintenance |
| Index on merchant ID | Auxiliary path to merchant records | May accelerate selective merchant lookups in a compatible store | Extra storage and write maintenance; may not suit broad analytical scans |
| Second curated copy by merchant | Separate layout optimized for merchant history | Different access pattern gets its own layout | Duplicate storage, refresh/consistency, retention, and operational cost |

These are alternatives to test, not assumptions that every table should have all four.

### 5.7 Step 7 — Account for writes and maintenance

Read optimization can impose a recurring tax. Include:
- index maintenance on each insert, update, or delete;
- partition-routing and late-arriving-data behavior;
- compaction and file-count management;
- reclustering/sorting or rewrite jobs;
- statistics refresh and metadata maintenance;
- rebuild time and extra temporary storage;
- write amplification (more data written than the logical change alone);
- locks, commit conflicts, or hotspots where relevant;
- operational monitoring and ownership.

For an index that improves one report but slows nightly ingestion, compare the report's business value against the ingestion delay, downstream lateness, storage, and maintenance. Do not decide from one query's latency alone.

### 5.8 Repeatable layout design method

Use this method for each candidate layout:

1. **Baseline workload:** list top query shapes, writes, data volume, concurrency, and targets.
2. **Candidate layout:** propose partition keys/granularity, indexes, clustering/sort order, and table/file organization.
3. **Estimate cardinality and skew:** count expected partitions and distinct values; calculate average and maximum/mean where possible.
4. **Estimate file/partition counts:** use explicit units and assumptions; identify small-file or metadata risks.
5. **Predict pruning:** name which query predicates should exclude which partitions/files/pages and what cannot be skipped.
6. **Compare total costs:** read performance, write overhead, storage, maintenance, concurrency, and operational burden.
7. **Validate with representative tests:** baseline and candidate, same data and query parameters, repeated runs, correctness checks.
8. **Apply pass/fail criteria:** keep the change only if its benefit exceeds its costs and it meets the agreed workload objectives.
9. **Revise:** adjust key, granularity, cluster order, or index; retest the full representative workload.
10. **Monitor drift:** define what metrics and thresholds trigger a review.

### 5.9 Intermediate practice task

For a table with five years of transaction history, propose:
- one date-based partition candidate;
- one alternative for merchant queries across all dates;
- one index candidate for an operational lookup, if supported;
- a way to measure whether clustering helps;
- the write and maintenance costs to include;
- a workload change that would cause you to revisit the design.

Your answer is incomplete if it only lists techniques without connecting them to query patterns and assumptions.

---

## 6. Advanced-level learning sequence

### 6.1 Skew and hotspots: averages can hide the bottleneck

**Skew** means data or work is unevenly distributed. A mean partition size can look healthy even when one partition is many times larger or receives a disproportionate share of writes. That largest unit may dominate elapsed time or cause one worker to become a bottleneck.

A simple size-skew ratio is:

\[
\text{skew ratio}=
\frac{\text{largest partition size}}
{\text{mean partition size}}
\]

This is a diagnostic indicator, not a universal pass/fail threshold. Workload skew may be more important than byte-size skew: one partition may contain smaller records but receive most concurrent updates.

#### Worked skew worksheet

**Illustrative assumptions:**
- Total data across the relevant partitions: 12,000 GB.
- Number of partitions: 100.
- Largest partition: 960 GB.
- The remaining 99 partitions together contain the remaining data.
- GB values are decimal.

**Step 1 — Mean size**

\[
\text{mean}=\frac{12{,}000\text{ GB}}{100}
=120\text{ GB per partition}
\]

**Step 2 — Size of the other partitions on average**

\[
\frac{12{,}000-960\text{ GB}}{99}
=\frac{11{,}040\text{ GB}}{99}
\approx111.52\text{ GB}
\]

The other 99 partitions average about 111.52 GB, while one partition is 960 GB.

**Step 3 — Skew ratio**

\[
\text{skew ratio}=\frac{960\text{ GB}}{120\text{ GB}}=8
\]

The largest partition is eight times the overall mean size. That is a clear signal to investigate the distribution, but it does not by itself prove a performance problem. Validate with per-partition processing time, bytes, row counts, concurrency, and failure/retry metrics.

| Worksheet field | Value |
|---|---:|
| Total data | 12,000 GB |
| Partition count | 100 |
| Mean partition size | 120 GB |
| Largest partition size | 960 GB |
| Mean of other 99 partitions | 111.52 GB (approx.) |
| Skew ratio | 8.0 |
| Follow-up evidence needed | Per-partition work/time, key distribution, concurrent writes, scan metrics |

**Interpretation:** a single very large partition can become the long pole in parallel processing. If it is also a write hotspot, it can cause contention or increase retries. The remedy depends on the cause: an uneven business key, a current-time concentration, or a physical-layout problem are different conditions.

#### Workload/partition-load skew worksheet

Size skew and workload skew are related but not identical. A partition can be small in bytes yet receive most writes or consume disproportionate CPU. Measure the work unit that matches the bottleneck (for example writes/hour, rows processed, CPU time, or elapsed processing time).

**Illustrative load example:** assume 100 partitions receive 1,000,000 writes per hour in total, and the busiest partition receives 80,000 writes per hour.

\[
\text{mean writes/hour} = \frac{1{,}000{,}000}{100} = 10{,}000
\]

\[
\text{write-load skew ratio} = \frac{80{,}000}{10{,}000} = 8
\]

The busiest partition receives eight times the mean write load. The other 99 partitions together receive 920,000 writes/hour, or about 9,292.9 writes/hour each on average. This is illustrative arithmetic, not a benchmark or a universal threshold. Confirm whether this concentration creates contention, latency, retries, or queueing before choosing a mitigation.

| Load worksheet field | Illustrative value |
|---|---:|
| Total writes per hour | 1,000,000 |
| Partition count | 100 |
| Mean writes per partition per hour | 10,000 |
| Maximum writes in one partition per hour | 80,000 |
| Mean across the other 99 partitions | 9,292.9 (approx.) |
| Write-load skew ratio (max / overall mean) | 8.0 |
| Required follow-up | Per-partition latency, contention, retries, queueing, and key distribution |

### 6.2 Common sources of skew

1. **Large customers or merchants:** a few keys represent a large share of records.
2. **Monotonically increasing keys:** new writes accumulate at one end or in one active region of an index or partition structure.
3. **Current-time concentration:** most new events land in the newest time partition.
4. **Uneven event activity:** weekends, campaigns, month-end, or settlement periods create unequal partitions.
5. **Join skew:** a small number of keys produce enormous join groups.
6. **Null/default values:** missing keys collapse into one partition or one join group.
7. **Poor hash distribution:** a chosen hash/bucket strategy does not distribute the actual key population as expected.

### 6.3 Mitigation choices and what they give up

| Mitigation | How it may help | Trade-off or limitation | Validate with |
|---|---|---|---|
| Composite key | Adds another dimension to divide a large group | More complex predicates and routing; may fragment related data | Distribution and query patterns |
| Hash/bucket partitioning | Spreads a key population across buckets | Can weaken range pruning and require the same hash logic for routing | Bucket balance, pruning, join/write behavior |
| Salting a hot key | Splits one logical hot key into several physical values | Reads/aggregations may need to combine salts; routing becomes more complex | Hot-key throughput and correctness |
| Sub-partition or split oversized groups | Breaks large subsets into smaller units | More metadata and more complex maintenance | Largest-unit size and total planning overhead |
| Adaptive splitting/rebalancing | Responds to changing distribution | Depends on platform support and operational behavior | Split/rebalance stability and overhead |
| Separate access-optimized copy | Gives a major query pattern its own layout | Extra storage, refresh lag, consistency and retention obligations | End-to-end value versus duplication cost |
| Change query strategy or pre-aggregate | Reduces work for repeated aggregates | May add refresh logic and freshness constraints | Query cost, freshness, correctness |

Do not select a mitigation just because it is familiar. For example, hashing a customer key can distribute load but may undermine a range query by customer identifier or date. Salting may solve a write hotspot but require downstream aggregation to combine salted values.

### 6.4 High cardinality and granularity trade-offs

Partition granularity affects both pruning and operational complexity.

- **Too coarse:** queries read more irrelevant data, and partitions may become large units for maintenance or concurrent work.
- **Too fine:** partition and metadata counts rise, small files become more likely, and planning/listing overhead may dominate.
- **High-cardinality key:** can create an excessive number of partitions, even if it is selective for lookups.
- **Low-cardinality key:** may produce too few partitions to prune effectively or distribute work.
- **Skewed key:** can create one or a few oversized partitions even when the average size seems reasonable.

There is no universal ideal partition size or number. The right granularity depends on the engine, table format, query plan behavior, data distribution, file sizing, workload, and operational constraints. Treat size guidelines as hypotheses to test, not hard laws.

### 6.5 Competing access patterns

One physical layout rarely optimizes every workload. Suppose most reports filter by date, while a critical risk investigation searches a merchant across all dates.

Possible responses:
1. Keep date as the primary partition key and accept that merchant searches may scan many partitions if they remain within target.
2. Cluster or sort within date by merchant if supported and if it improves skipping.
3. Add a secondary index in a store that supports and benefits from it.
4. Maintain a second curated table or materialized view for merchant-oriented queries.
5. Revisit whether both query families belong in the same store or need different serving paths.

Each alternative adds a cost. A second copy adds storage, refresh, reconciliation, retention, and governance requirements. An index adds write and maintenance overhead. A more complex layout adds operational failure modes. A design should optimize the overall workload, not only the most visible report.

### 6.6 Quantify a proposed layout before implementation

At minimum, calculate:
- retained volume and growth;
- number of distinct partition values over the retention horizon;
- average and maximum partition size, not only the mean;
- approximate file count using the expected file size;
- percentage of queries expected to benefit;
- number of files/partitions expected to be touched by common filters;
- index storage and write-maintenance estimates where applicable;
- expected compaction/reclustering frequency and duration;
- cost of any duplicate access-optimized copy.

Keep assumptions explicit. For example, “all dates have equal volume” is a simplifying assumption, not a fact. If the assumption is likely false, use a range or sample actual distribution.

### 6.7 Validation experiment design

A defensible validation plan includes the following.

#### A. Representative query set

Choose queries by business importance, frequency, concurrency, and distinct access pattern. Include:
- date-range queries;
- customer or merchant lookups;
- join-heavy queries;
- aggregations and order-by queries;
- a broad scan that may not benefit from pruning;
- concurrent reads/writes;
- late-arriving records or corrections where relevant.

Do not validate only the query the proposed layout was designed to improve. A change can improve one query and degrade the rest of the workload.

#### B. Controlled comparison

- Use the same data snapshot or equivalent dataset.
- Keep query parameters, result correctness, and concurrency conditions comparable.
- Separate cold-cache and warm-cache results if cache state materially affects the workload; do not mix them silently.
- Repeat runs enough to understand variability.
- Record engine version, configuration, data volume, and candidate layout.
- Avoid treating a tiny synthetic dataset as representative of production-scale metadata or skew.

#### C. Measurements

| Dimension | Metric examples | Why it matters |
|---|---|---|
| Read latency | p50 and p95 latency; elapsed time for scheduled jobs | Typical and tail behavior |
| Read work | Bytes scanned, files/partitions/pages read, rows processed | Whether pruning or indexing reduced work |
| Compute | CPU, memory, spill, data movement if exposed | Whether less I/O shifted cost elsewhere |
| Write impact | Ingestion throughput, write latency, backlog, retries | Read gains must not break freshness or write targets |
| Maintenance | Compaction/recluster duration, index rebuild time, failed jobs | Recurring operational tax |
| Storage | Table, index, metadata, temporary rewrite, and duplicate-copy size | Full cost, not only data bytes |
| Correctness | Row counts, aggregates, duplicates, missing/extra records | A faster incorrect query is a failed design |
| Operations | Alerts, failure recovery, owner effort, runbook steps | Production readiness |

#### D. Define pass/fail criteria before testing

Examples of criteria structure—not universal numeric targets:
- Q1 p95 latency must meet the owner-approved target under agreed concurrency.
- Bytes scanned for Q1 should fall by a pre-agreed amount if scan reduction is the stated hypothesis.
- Nightly ingestion must complete inside its existing or revised agreed window.
- No result differences may occur outside explicitly approved semantic changes.
- Maintenance must fit within an agreed compute budget and operational window.
- Total storage and operating cost must remain within the approved range.

Set actual thresholds with stakeholders before running the test. Do not invent a percentage improvement or claim the layout passed without measurement.

#### E. Decide and document

Keep the candidate only if:
1. correctness is preserved;
2. the important workload objectives are met;
3. the improvement is repeatable;
4. write and maintenance costs are acceptable;
5. the complexity has an owner and runbook;
6. the evidence is strong enough for the decision.

If the result is inconclusive, record it as inconclusive. Improve the dataset, query coverage, or measurement rather than promoting a hypothesis into a fact.

### 6.8 Workload drift and review triggers

A layout can become wrong as the business changes. Review it when:
- a new high-volume query pattern appears;
- date-only reports become merchant/customer investigations;
- data grows much faster than expected;
- new tenants or merchants create skew;
- ingestion becomes more frequent;
- write throughput falls or backlogs rise;
- bytes scanned or p95 latency increases without corresponding growth;
- maintenance jobs run longer or fail more often;
- the engine, file format, table format, or query strategy changes;
- retention changes alter partition counts or data distribution.

Record an owner, a monitoring signal, and a threshold or decision rule for each important review trigger.

### 6.9 Advanced exercise

Take a proposed layout that partitions by `customer_id` and is estimated to create millions of tiny partitions. Diagnose:
- why the key's cardinality is dangerous for this layout;
- whether customer lookups are frequent and selective enough to justify an index or another access path;
- whether a coarser partition key plus clustering could address the dominant analytical queries;
- how skew would be measured;
- how the alternative would be validated;
- which costs or query patterns might get worse.

Then take an index that appears to improve one report but increases nightly ingestion time by 40% in a measured test. Decide whether to retain, redesign, or remove it only after evaluating business criticality, ingestion deadline, workload mix, and total cost. The 40% figure in this scenario is illustrative, not a general index overhead.

---

## 7. Industry-application exercises

The following case is fictional and is used only to practice architecture reasoning.

### 7.1 Northbridge Bank: scope and assumptions

Northbridge Bank maintains:
- a **transaction-history analytical table** used for recent activity, customer history, merchant risk analysis, reconciliation, and broad regulatory analysis;
- an **operational ledger table** used for exact lookups and frequent writes, with correctness and latency requirements defined by the ledger owner.

**Illustrative assumptions for the analytical history:**
- retained data: 5 TB decimal;
- retention horizon: 5 years;
- daily transaction monitoring is common;
- customer-history queries filter by `customer_id` and a bounded date range;
- merchant risk queries filter by `merchant_id` across multiple years;
- daily reconciliation uses a date range plus account or ledger attributes;
- full-history regulatory analysis is occasional and reads a broad portion of the data;
- actual query frequencies, latency targets, distributions, and costs must be obtained from Northbridge stakeholders or measurements.

These assumptions do not establish production requirements or performance results.

### 7.2 Query-to-layout proposal

| Layout element | Query pattern it is intended to improve | Assumption | Expected mechanism | Cost / risk | Validation evidence |
|---|---|---|---|---|---|
| Daily partitioning on `event_date` for analytical history | Q1 recent activity; Q4 daily reconciliation | Those queries commonly filter by event date and data volume is large enough to justify partitioning | Exclude date partitions outside the requested range | Many partitions over long retention; late data and metadata overhead | Partitions/files read, bytes scanned, p50/p95 latency, ingestion routing |
| Cluster/sort within each date by `merchant_id`, if supported | Q3 merchant risk over selected dates | Merchant predicates are frequent and data organization can improve file/row-group skipping | Improve locality and statistics within date partitions | Reorganization cost; may not help queries with different predicates | Scan metrics and query plans for merchant queries; reclustering duration |
| Candidate index or alternate lookup path for `customer_id`, if the selected store supports it | Q2 customer history | Customer queries are frequent and selective enough to justify the structure | Narrow the candidate records or data ranges | Write overhead, index storage, potential limited benefit for broad history | Query plan/use, latency, write throughput, index storage |
| Existing unique-key access path on operational ledger entry ID, where supported | Q6 exact ledger lookup | Operational lookup is latency-sensitive and keyed by a unique identifier | Direct or indexed lookup | Must preserve transaction semantics and write performance; implementation-specific | Correctness, latency percentiles, concurrent read/write behavior |
| No extra index for broad regulatory scan unless evidence supports one | Q5 full-history analysis | Q5 reads a broad fraction of data | Broad scan is likely dominated by scan-efficient layout and compute | Extra index may add cost without reducing broad scan work | Bytes scanned, plan, overall query and write workload |

**Traceability rule:** each row states the query pattern. If no high-value query needs the proposed element, remove it from the proposal or mark it as an experiment rather than a committed design.

### 7.3 Skew and cardinality worksheet for Northbridge

The 5 TB / daily partition calculation in Section 5.3 is only an average estimate. Northbridge should measure actual daily volume and compare:
- largest and smallest daily partitions;
- mean and median daily size;
- the busiest hour and write concentration;
- largest merchant/customer record counts;
- null/default key frequency;
- rows and bytes processed per partition during reconciliation and risk jobs.

Use the Section 6.1 skew worksheet as a model. Do not infer that Northbridge has a skew ratio of 8; that value was illustrative only. Calculate the ratio from its own measured or explicitly estimated distribution.

### 7.4 Rejected design: partition directly by customer ID

**Proposal rejected:** create one physical partition per `customer_id` for the full analytical history.

**Why it is rejected as the initial design:**
- Customer ID may have very high cardinality, producing a very large number of small partitions.
- Partition metadata and file/listing/planning overhead may grow substantially.
- It does not naturally optimize daily monitoring or full-history date-range queries.
- Unequal customer activity can create skew.
- The design assumes customer lookups dominate the workload, but the stated workload includes date-based reconciliation and merchant risk queries.
- A candidate index or a date-oriented partition plus clustering may be simpler and more balanced, depending on measured capabilities.

This is not a universal prohibition against customer-based partitioning. It is rejected for this illustrative workload because its cardinality and query mix do not justify the complexity without stronger evidence.

### 7.5 Compare candidate strategies

| Candidate | Fit to stated workload | Benefits | Main costs and risks | Decision status |
|---|---|---|---|---|
| A. No special partitioning; simple table/file layout | Baseline for small or low-volume data, or when the engine manages layout adequately | Simplest operations and fewer layout assumptions | May scan more data as volume grows; must still measure baseline | Keep as baseline; could be sufficient if targets are met |
| B. Daily date partitions only | Recent activity and daily reconciliation | Clear date pruning; understandable maintenance boundaries | Merchant/customer queries may scan many date partitions; partition and file counts grow with retention | Primary candidate to test |
| C. Daily date partitions plus merchant clustering/sorting | Date-oriented queries and merchant risk within date ranges | May reduce file/row-group reads for merchant predicates | Reorganization and maintenance; engine may not exploit it; competing keys | Candidate only if merchant query evidence supports it |
| D. Customer-ID partitions plus several indexes | Customer lookups | May appear attractive for one access pattern | High partition cardinality, metadata/small-unit risk, index write overhead, poor fit for other query patterns | Reject initially; reconsider only with contrary workload evidence |
| E. Separate merchant-optimized analytical copy | Merchant risk searches across long history | Independent layout for a critical access pattern | Extra storage, refresh lag, reconciliation, retention and governance work | Consider only if Q3 cannot meet its target in the primary layout |
| F. Operational ledger uses its own suitable access path, separate from analytical history | Exact operational lookups and concurrent writes | Keeps operational access design aligned to transactional correctness and latency | Additional integration/replication if analytics needs a copy | Validate against Topic 1 separation decision and operational requirements |

### 7.6 Decision method and validation criteria

Before selecting a candidate, Northbridge must establish:
1. query frequency, concurrency, and business importance;
2. actual data volume and date/customer/merchant distribution;
3. available capabilities of the selected database/table format/engine;
4. latency, freshness, ingestion, and batch-window targets;
5. index, clustering, compaction, and metadata maintenance costs;
6. retention and access constraints.

**Example validation plan (criteria placeholders):**
- Run the representative query set on the baseline and each candidate.
- Record result correctness, p50/p95 latency, bytes scanned, partitions/files read, and compute metrics where available.
- Measure ingestion throughput, write latency, and late-data behavior.
- Measure maintenance time, storage overhead, and failed/retried maintenance jobs.
- Agree a pass/fail threshold with each workload owner before testing.
- Keep a more complex candidate only if it meets the target and its incremental benefit justifies its recurring cost.

No performance result is claimed here; these are the measurements Northbridge would need to collect.

### 7.7 Operational ledger versus analytical history

Do not copy the analytical partitioning design to the operational ledger automatically. First establish the ledger's access model and transaction requirements. A transactional store may favor a unique key or a supported index, while an analytical table may favor date pruning and scan locality. The same word, such as *partitioning*, can describe different implementation details in those systems.

If the ledger is replicated to analytical storage, the analytical layout must account for data freshness, corrections, and the fact that the analytical copy is not necessarily the authoritative record. Layout does not resolve replication or consistency requirements; those belong to Topic 6.

### 7.8 Exercise deliverables

Produce:
1. a query-pattern register with at least six queries;
2. a layout proposal for analytical history and a separate operational-ledger proposal;
3. a table mapping every proposed partition, index, and cluster/sort element to a query ID;
4. a cardinality, file-count, and skew worksheet with units and assumptions;
5. a rejected-alternative rationale;
6. a validation experiment with baseline, candidate, representative tests, metrics, and pass/fail criteria;
7. a maintenance register with task, owner, cadence/trigger, failure signal, and recovery action.

---

## 8. Practical scenarios and case-based reasoning

### Scenario 1 — Millions of tiny customer partitions

A team partitions an analytical table directly by customer ID. The table contains millions of customers and many customers have very little data.

**Reasoning path**
1. Count distinct customer IDs and estimate the resulting partition count.
2. Measure the size distribution, not only the average.
3. Determine whether queries filter by customer alone or also by date.
4. Compare a coarser date partition with clustering, indexing, or a separate access path for the dominant customer query.
5. Include metadata/planning, small-file, write-routing, and maintenance costs.
6. Validate with the representative query set.

**Answer guidance:** do not automatically choose another key without evidence. The initial design has a high-cardinality risk and should be compared with a simpler baseline.

### Scenario 2 — An index improves one report but slows nightly loads

An index is measured to improve a critical report but increases nightly load duration by 40% in the illustrative scenario.

**Reasoning path**
1. Verify the report improvement across repeated runs and under realistic concurrency.
2. Determine whether nightly loads still meet their business deadline and freshness target.
3. Measure index storage, update overhead, rebuild needs, and any effects on other queries.
4. Consider whether a different index, clustering, materialized result, or query rewrite would give a better total trade-off.
5. Decide using agreed business value and pass/fail criteria.

**Answer guidance:** the 40% is not a universal index cost. If the load misses a critical deadline, the index may be unacceptable even if the report is faster. If the load still meets its target and the report is critical, the index may remain justified.

### Scenario 3 — New merchant query across all dates

The table is partitioned by date. The business adds a high-priority merchant investigation that scans three years.

**Reasoning path**
1. Check whether the merchant predicate can prune anything beyond date partitions.
2. Measure how many date partitions and files are read and how much data is scanned.
3. Test merchant clustering/sorting or a suitable index if supported.
4. Compare the cost of a separate merchant-oriented copy with the query's frequency and urgency.
5. Revisit the layout only if the new workload changes the total trade-off.

**Answer guidance:** date partitioning is not automatically wrong; it serves the date-oriented queries. The new query is evidence that the workload may now need another access path.

### Scenario 4 — Average partition size looks healthy, but jobs run slowly

The mean partition size is 120 GB, but one partition is 960 GB.

**Reasoning path**
1. Calculate the size skew ratio: 960 GB / 120 GB = 8.
2. Check row count, processing time, concurrent writes, and key distribution for the large partition.
3. Determine whether the issue is data skew, a hot key, a time-based write concentration, or uneven file organization.
4. Evaluate a mitigation and its impact on pruning and query complexity.
5. Compare per-partition work and end-to-end job duration before and after.

**Answer guidance:** the average conceals a large outlier. The ratio identifies an investigation target; it does not alone establish the right fix.

### Scenario 5 — A date filter scans more data than expected

A query filters the intended date range but scans nearly all files.

**Reasoning path**
1. Inspect the query plan and partition/file pruning metrics if available.
2. Confirm the predicate uses the intended column and data type.
3. Check whether the table metadata and actual layout agree.
4. Verify whether the query engine can use the partition expression and file statistics.
5. Check if the filter is selective at the row level but matches values scattered throughout all files.
6. Re-test with a semantically equivalent predicate supported by the engine.

**Answer guidance:** do not assume a date partition guarantees pruning. Metadata, predicate form, data distribution, and engine behavior all matter.

### Scenario 6 — A layout was fast last year but is slow now

Query patterns and data volume have changed, and maintenance jobs now run longer.

**Reasoning path**
1. Compare current query distribution with the assumptions in the original design.
2. Recalculate partition cardinality, average/maximum size, and file count.
3. Review index usage and write cost.
4. Check compaction/reclustering backlog and statistics freshness.
5. Re-run the baseline/candidate experiment with current data.
6. Update the decision record and monitoring triggers.

**Answer guidance:** layout is a workload-dependent decision, not a permanent property. Revisit it when evidence changes.

### Scenario 7 — Should every column get an index?

A team proposes indexing every filterable column to avoid future slow queries.

**Answer guidance:** reject blanket indexing. For each index, identify a frequent or important query, expected selectivity, engine support, write cost, storage, and validation. Some queries may benefit from clustering, partition pruning, query rewriting, or no additional structure. An index without a demonstrated workload benefit is an unproven recurring cost.

### Scenario 8 — Query latency improves but total cost rises

A candidate reduces a report's p95 latency but requires frequent full-table reclustering and a duplicate data copy.

**Answer guidance:** evaluate the full workload and total cost. Include compute and storage for maintenance, refresh/consistency, failure recovery, and operational ownership. Keep the design only if the business value of the latency improvement justifies those costs and the remaining targets are met.

---

## 9. Expected outputs and deliverables

Complete and retain these artifacts as part of the learning exercise.

### 9.1 Query-pattern list

At least ten representative queries for a realistic project, or six for the Northbridge exercise, with:
- predicates, join keys, grouping, and ordering;
- frequency and concurrency;
- data horizon and estimated result/data scanned;
- target latency or completion deadline;
- write/update behavior and freshness constraints;
- source of evidence and confidence level.

### 9.2 Layout design

For each table or dataset, document:
- data grain and volume;
- candidate partition key and granularity;
- candidate index and supported access pattern;
- cluster/sort keys and intended locality;
- expected pruning behavior;
- known limitations and queries that may not benefit;
- engine/table-format capabilities that must be verified;
- data retention and update patterns that affect layout.

Every element must map to a query ID and an assumption.

### 9.3 Cardinality and skew worksheet

Include:
- total data volume and units;
- partition horizon and count;
- average partition size;
- maximum and median size if known;
- distinct-key counts;
- skew ratio and its interpretation;
- estimated file count using a stated target file size;
- assumptions about uniformity, compression, and file-writing behavior.

### 9.4 Validation experiment plan

Include:
- baseline and candidate descriptions;
- representative query set;
- data volume and engine/configuration;
- repeat/run conditions;
- correctness checks;
- read and write metrics;
- p50/p95 latency where relevant;
- maintenance and storage costs;
- pass/fail criteria fixed before testing;
- decision rule and owner.

### 9.5 Maintenance register

| Task | Why it exists | Trigger/cadence | Owner | Failure signal | Recovery/response |
|---|---|---|---|---|---|
| Index maintenance/rebuild | Keep access path usable and consistent | Engine- and workload-specific | Named data/store owner | Increased latency, stale statistics, failed rebuild | Diagnose, rebuild/repair, retest |
| Compaction | Control small files and improve scan organization | Based on file-count/layout evidence | Data platform/table owner | File count growth, scan overhead, backlog | Compact safely and validate results |
| Reclustering/sorting | Restore locality as new data arrive | Based on observed degradation | Table owner | Rising bytes scanned or reduced skipping | Reorganize, measure before/after |
| Partition maintenance | Keep partition metadata and routing correct | On new period/key or retention event | Data owner | Missing, duplicate, or unexpected partitions | Repair metadata/data routing |
| Statistics refresh | Help planning decisions where supported | Engine-specific or data-change trigger | Database/platform owner | Poor plans or stale estimates | Refresh and compare plans |
| Workload review | Detect drift from design assumptions | Scheduled review and metric triggers | Architecture/workload owner | Targets missed or query mix changes | Rebuild workload register and revisit layout |

The table is a template. Assign actual owners, triggers, and recovery steps in the real project; do not leave them implicit.

### 9.6 Decision record

For each significant layout decision, record:
- problem and workload evidence;
- constraints and assumptions;
- options considered;
- selected option and why;
- rejected alternatives and evidence;
- read/write/maintenance trade-offs;
- test results or explicit unvalidated hypotheses;
- owner, monitoring signals, and revisit triggers.

---

## 10. Common mistakes and misconceptions

1. **Treating partitioning, indexing, and clustering as interchangeable.** They operate at different levels and have different costs.
2. **Choosing a partition key without query evidence.** A key should serve important predicates and manageable cardinality.
3. **Partitioning directly by a high-cardinality identifier.** This can create millions of tiny units and substantial metadata overhead.
4. **Choosing the finest possible granularity.** More pruning is not free; planning, metadata, file counts, and maintenance may rise.
5. **Choosing a coarse layout without checking query horizons.** Queries may read much more data than necessary.
6. **Assuming partitioning helps every query.** A query that does not constrain the partition key may still touch many partitions.
7. **Assuming an index always speeds reads.** It may be unused, low-selectivity, or irrelevant to broad scans.
8. **Indexing every column.** Every additional structure needs storage, write maintenance, and operational attention.
9. **Ignoring write amplification.** Inserts, updates, deletes, index maintenance, sorting, and compaction can increase total writes.
10. **Ignoring clustering degradation.** New data may not follow the intended order; the benefit may disappear without maintenance.
11. **Using only averages.** Large partitions, hot keys, or uneven write rates can dominate elapsed time.
12. **Confusing size skew with workload skew.** Equal bytes do not guarantee equal CPU, I/O, or contention.
13. **Assuming a fractional file-count estimate is a physical file count.** A value below one means the average partition is smaller than the target; actual nonempty partitions still need physical representation.
14. **Ignoring the small-file problem.** Excessive files can increase planning, metadata, open/close, and scheduling overhead.
15. **Optimizing one query and declaring success.** The change may degrade ingestion, joins, broad scans, or other queries.
16. **Ignoring workload drift.** Data distribution and access patterns change; old assumptions need review.
17. **Confusing expected with measured improvement.** A design hypothesis is not a benchmark result.
18. **Claiming a universal ideal partition size or index strategy.** The right choice depends on engine, data, query shape, and operational limits.
19. **Ignoring engine and table-format capability differences.** A conceptual layout cannot be assumed to be supported identically across systems.
20. **Failing to assign maintenance ownership.** A layout that depends on unowned maintenance is not operationally complete.

---

## 11. Mastery criteria

You have mastered this topic when you can provide evidence that you can:

- [ ] Explain the distinct roles of partitioning, indexing, clustering, sorting, and pruning.
- [ ] Explain selectivity, cardinality, skew, and hotspot without conflating their meanings.
- [ ] Build a workload register before proposing a layout.
- [ ] Choose a candidate partition key and granularity with explicit query-pattern evidence.
- [ ] Calculate average partition size and approximate file counts with correct units.
- [ ] Calculate and interpret a skew ratio and explain why the mean can hide a bottleneck.
- [ ] State which queries are expected to benefit from every layout element and which are not.
- [ ] Explain index storage/write costs and clustering/compaction maintenance.
- [ ] Compare a simple baseline with a more complex layout and justify any additional copy or structure.
- [ ] Define a validation experiment using representative queries, correctness checks, read/write metrics, maintenance cost, and pre-agreed pass/fail criteria.
- [ ] Distinguish expected benefits from measured results.
- [ ] Identify workload drift signals and define when the architecture should be reviewed.

**Mastery standard:** the recommendation must be reproducible from the documented workload assumptions, calculations, and validation plan. Confidence or familiarity with a technique is not sufficient evidence.

---

## 12. Completion gate

Do not mark Topic 5 complete until every item below is satisfied.

- [ ] **Query evidence:** the query-pattern list contains the important filters, joins, aggregations, ordering, frequency, concurrency, and target behavior.
- [ ] **Traceability:** every proposed partition, index, cluster, or sort element is linked to a named query pattern and stated assumption.
- [ ] **Cardinality and size:** partition count, average size, and estimated file count include formulas, units, assumptions, and reproducible arithmetic.
- [ ] **Skew:** the skew worksheet compares the mean and largest partition, computes the ratio correctly, and states what additional measurements are needed.
- [ ] **Trade-offs:** the design includes write overhead, storage, maintenance, metadata/small-file risks, and queries that may get worse.
- [ ] **Alternative rejected:** at least one alternative is rejected with workload-based reasons rather than preference alone.
- [ ] **Validation plan:** baseline, representative query set, correctness checks, metrics, repeated tests, and pass/fail criteria are defined.
- [ ] **No invented results:** any untested benefit is marked as a hypothesis; no performance outcome is claimed without evidence.
- [ ] **Maintenance ownership:** recurring tasks have an owner, trigger/cadence, failure signal, and recovery approach.
- [ ] **Practice questions:** answer and correct the Topic 5 practice questions; revisit incorrect answers and attempt them again.

### Final self-test

1. Why can date partitioning help a last-seven-days query but not necessarily a customer-only query?
2. Why is a highly selective predicate not proof that an index will help?
3. How can clustering reduce bytes scanned without reducing the number of logical date partitions?
4. What does a skew ratio of 8 mean, and what does it *not* prove?
5. Why can a partition's average size be acceptable while the physical file count is still problematic?
6. What measurements would you use to decide whether an index that improves one report but slows ingestion should remain?
7. Which assumptions would cause you to revisit a date-partitioned layout when merchant queries become more important?
8. Why must pass/fail criteria be agreed before the candidate test?
9. What additional cost appears when a second layout-optimized copy is introduced?
10. What signals would tell you that the layout no longer fits the workload?

A strong answer names the mechanism, states the assumptions, explains the trade-off, and identifies evidence that could disprove the recommendation.

---

**Topic boundary:** this lesson defines and validates logical layout choices. Detailed replication and transaction guarantees belong to Topic 6; full retention, archival, and storage-tier policy belongs to Topic 7. Their constraints must still be considered when they materially affect layout, but they are not substitutes for the Topic 5 workload-to-layout method.
