# Query Performance and Data Locality

**Repository location:** `Stage 2D — Data Architecture/13-Performance-Scalability-and-Cost-Architecture/03-query-performance-and-data-locality.md`  
**Module:** Stage 2D, Module 2D.13 — Performance, Scalability and Cost Architecture  
**Level:** Beginner → Intermediate → Advanced  
**Approach:** Vendor-neutral; calculations and datasets are illustrative, not benchmarks.

---

## 1. Purpose, scope, and learning outcomes

Queries are often slow because they read too much data, move too much data, perform expensive work, wait for shared resources, or combine several of these problems. A useful performance review does not begin with “add an index” or “buy more compute.” It begins by defining the workload, observing the execution, identifying the dominant constraint, and testing a specific hypothesis.

**Data locality** means keeping computation close to the data it needs, or arranging execution and storage so that unnecessary data movement is avoided. It does not mean that all data must live on one machine: distributed systems deliberately move data when the benefits of parallelism outweigh the transfer and coordination cost.

### 1.1 Learning outcomes

By the end of this lesson, you should be able to:

1. Define query-performance objectives using latency percentiles, throughput, freshness, error rate, and workload boundaries.
2. Explain the major stages and operators in a logical query plan and distinguish them from observed physical execution.
3. Calculate scan volume, selectivity, pruning ratios, and approximate scan time while stating the assumptions.
4. Explain how partitioning, clustering, indexing, file layout, and statistics differ and interact.
5. Reason about predicate pushdown, column projection, partition pruning, joins, aggregation, sorting, shuffles, and skew.
6. Identify how remote reads, network transfer, memory pressure, spilling, and parallel execution affect performance.
7. Use runtime evidence to rank bottleneck hypotheses instead of presenting guesses as findings.
8. Explain why reducing scanned bytes may not reduce end-to-end latency when another stage dominates.
9. Design a controlled, repeatable experiment with a baseline, one main variable, success criteria, and regression checks.
10. Produce a workload profile, query-plan review, scan and movement assessment, optimisation proposal, and validation plan.

### 1.2 Scope boundaries

This is a query-performance and data-locality lesson, not a complete course in a specific SQL dialect, database administration, sharding, caching, or cloud cost modelling.

- Topic 01 (`01-capacity-planning-and-growth-forecasting.md`) addresses demand, capacity, growth, headroom, and forecast uncertainty.
- Topic 02 (`02-throughput-latency-concurrency-and-queueing.md`) explains throughput, latency, concurrency, queueing, percentiles, and resource contention.
- This topic investigates why particular queries are slow and what evidence supports an optimisation.
- Topic 04 (`04-scaling-partitioning-sharding-and-hotspots.md`) goes deeper into distribution choices, scaling, sharding, skew, and hotspots.
- Topic 05 treats caching and materialisation; Topic 06 treats cost modelling; Topic 07 treats formal performance testing; Topic 08 integrates evidence into architecture optimisation.

### 1.3 The governing principle

> Read less, move less, compute less — but measure end-to-end behaviour before concluding that a change helped.

The rule is a direction for investigation, not a guarantee. For example, pruning a large scan may save I/O while a distributed join or queue wait remains the dominant part of latency.

---

## 2. Prerequisites and concepts carried forward

### 2.1 Topic 01: capacity planning and growth forecasting

You should already be able to describe workload volume, average and peak demand, growth assumptions, capacity, headroom, and measurable service objectives. These concepts matter because a query that is acceptable at low concurrency may degrade when many similar queries compete for CPU, memory, storage bandwidth, or connections.

Capacity estimates are not latency predictions. A system may have sufficient average capacity yet violate p95 latency during bursts, skewed workloads, or simultaneous batch and interactive processing.

### 2.2 Topic 02: throughput, latency, concurrency, and queueing

Use the distinction between:

- **Service time:** time spent actively processing a request, excluding queue wait according to the chosen measurement boundary.
- **Queue wait:** time waiting for a resource or execution slot.
- **End-to-end latency:** elapsed time from the declared start event to the declared completion event.
- **Throughput:** completed work per unit time.
- **Concurrency:** work in progress, including whatever queued/in-flight work the metric's boundary counts.

For a stable system and consistent boundaries, Little's Law is:

\[
L = \lambda W
\]

where \(L\) is average work in the system, \(\lambda\) is average throughput, and \(W\) is average time in the system. If query latency rises while throughput remains constant, average in-flight work can rise too. That does not by itself identify whether the cause is scan I/O, a shuffle, memory pressure, queueing, or another operator.

Use p50, p95, and p99 where relevant; an average can hide long-running outliers. Compare percentiles only when workload, sampling, time window, and measurement boundary are comparable.

### 2.3 Prerequisites from the wider architecture roadmap

The module roadmap identifies these prerequisites for Topic 03:

- **Seq 2:** throughput, latency, concurrency, queueing, and performance interpretation.
- **P4:** partitioning, indexing, clustering, skew, file layout, and formats.
- **P5:** table formats, compute/storage separation, control-plane concepts, quotas, and multi-team isolation.

You do not need production access or a vendor-specific account. You can learn the reasoning with small synthetic datasets, query-plan examples, arithmetic, and a written experiment design.

---

## 3. Beginner level: what happens when a query runs?

Consider this illustrative request:

> “For the previous seven complete days, calculate net sales by region for product category `Accessories`.”

A conceptual SQL query might be:

```sql
SELECT
    region,
    SUM(net_amount) AS net_sales
FROM sales
WHERE sale_date >= DATE '2026-10-01'
  AND sale_date <  DATE '2026-10-08'
  AND category = 'Accessories'
GROUP BY region;
```

The dates are illustrative and use a half-open interval: the start is included and the end is excluded. The schema assumed here contains `sale_date`, `category`, `region`, and `net_amount`. Real date semantics and supported syntax depend on the engine.

### 3.1 Logical stages

A simplified logical plan is:

```text
Scan sales
  → Filter sale_date range and category
  → Group by region
  → Aggregate SUM(net_amount)
  → Return result
```

A SQL optimizer may push filters closer to the scan, read only required columns, combine operators, or choose a different physical strategy. The diagram describes the requested logic, not a promise about the physical execution.

For a query with a join:

```text
Scan orders ── Filter ─┐
                       ├─ Join ─ Aggregate ─ Sort ─ Return
Scan customers ────────┘
```

### 3.2 Common operators and their possible costs

| Operator or stage | What it does | What can make it expensive | Evidence to inspect |
|---|---|---|---|
| Scan / table read | Reads relevant rows, columns, files, blocks, or index pages | Large read volume, remote I/O, small-file overhead, poor pruning | Bytes read, files/partitions read, rows read, read time |
| Filter | Removes rows that do not satisfy predicates | Filter applied too late, expensive expression, low selectivity | Input/output rows, predicate placement, CPU time |
| Projection | Retains needed columns | Too many columns carried through later stages | Read columns, row width, intermediate bytes |
| Join | Matches rows from two inputs | Large inputs, poor join order, data redistribution, skew, many-to-many expansion | Input cardinalities, join type, shuffle bytes, output rows |
| Aggregate | Computes groups and measures | High group cardinality, large state, shuffle, skew | Input/output rows, number of groups, memory, spill |
| Sort / window | Orders rows or evaluates order-sensitive functions | Large sort input, wide rows, insufficient memory | Rows sorted, sort time, spill, partitioning of window |
| Exchange / shuffle | Redistributes rows among workers | Network transfer, serialization, skew, coordination | Bytes sent/received, task distribution, exchange time |
| Result materialisation | Builds or transfers final output | Large result, client/network bottleneck | Output rows/bytes, fetch time, client timing |
| Queue / resource wait | Waits for compute, memory, slots, locks, or I/O capacity | Concurrent workload, saturation, isolation limits | Queue time, wait events, concurrent load, resource metrics |

A stage may be fast by itself and still be part of a slow query because it produces too much data for the next stage. Always inspect both input and output cardinality.

### 3.3 Logical plan versus physical plan versus runtime evidence

These are different layers of understanding:

1. **Logical plan:** the operations required to answer the query, such as filter, join, and aggregate.
2. **Physical plan:** a proposed implementation, such as sequential scan, index scan, hash join, sort-merge join, broadcast join, repartition, or parallel aggregate.
3. **Runtime profile:** what actually happened for a particular execution: rows, bytes, task durations, waits, spill, skew, and elapsed time.

A plan can suggest a likely cost, but it does not prove the runtime bottleneck. Statistics may be stale; data distributions may be skewed; cache state and concurrency may vary; and runtime optimizers may adapt. A runtime profile is also specific to its workload and environment.

### 3.4 A book-search analogy

- Reading every shelf is like a broad scan.
- Using a suitable index or partition metadata is like locating the relevant shelf first.
- Reading only the required columns is like copying only the pages needed.
- Carrying books across the building is like shuffling data between workers.
- Sorting every book before answering one question is like sorting a large intermediate result unnecessarily.

The analogy helps build intuition but does not replace measurement. Sequential scans can be efficient for large portions of a table; an index can be slower when it causes many random reads.

---

## 4. Terminology and core performance metrics

### 4.1 Query objectives

A useful objective states the workload and measurement boundary. Example:

> For interactive regional-sales queries over the last seven days, p95 end-to-end latency should be at most 2 seconds at 40 concurrent sessions, with an error rate below 0.1%, on the defined dataset and execution environment.

This is an illustrative objective, not a universal target. It is incomplete until “end-to-end” is defined (submit-to-result-ready or submit-to-client-fetch), the data size is specified, and the test conditions are documented.

Useful objective dimensions include:

- p50 / p95 / p99 latency;
- completed queries per second or per minute;
- error and timeout rate;
- data freshness or maximum acceptable staleness;
- workload mix and concurrency;
- dataset size, distribution, and query parameters;
- resource and isolation boundaries.

### 4.2 Metrics: definitions and limits

| Metric | Definition / measurement | What it helps show | What it cannot prove alone |
|---|---|---|---|
| End-to-end latency | Elapsed time between declared start and completion events | User-visible speed | Which stage caused the delay |
| Operator/stage time | Engine-reported time attributed to an operator/stage | Where execution time appears to accrue | That timings are additive; overlapping stages and instrumentation differ |
| Rows scanned/read | Rows visited or emitted by a scan, depending on engine semantics | Scan work and pruning effectiveness | Exact physical I/O bytes or total CPU |
| Rows returned | Rows delivered by the query | Result cardinality | Amount of input work |
| Bytes scanned/read | Engine-defined bytes read, often compressed or physical/logical depending on system | Approximate scan volume and sometimes billing basis | Total network, CPU, decompression, metadata, or client transfer |
| Scan selectivity | Fraction of candidate rows that satisfy a filter, with explicit denominator | How selective the predicate is | Whether the engine can avoid reading the rejected rows |
| Pruning ratio | Fraction of candidate scan units avoided, defined consistently | Layout/filter effectiveness | Runtime improvement if another stage dominates |
| Shuffle bytes | Data transferred during redistribution | Network and exchange cost | Whether the shuffle is the only bottleneck |
| Intermediate rows/bytes | Rows/bytes produced between operators | Expansion and memory pressure risk | Exact resident memory; representation and compression differ |
| Spill bytes | Data written to/read from temporary storage because memory was insufficient for an operation | Memory pressure and spill cost | Whether more memory alone is the best fix |
| Task-duration spread | Distribution of durations across parallel tasks | Skew, stragglers, uneven work | Root cause without per-task input and resource context |
| CPU time / utilisation | Engine or host CPU accounting over a window | Compute demand or saturation evidence | Query-level CPU unless attribution is available |
| Queue / wait time | Time waiting for slots, resources, I/O, locks, or admission | Contention and scheduling delay | Which upstream workload created it without correlation |
| Output bytes | Bytes returned to the client or next stage | Result-transfer and downstream work | Full query scan volume |

Metric names differ by engine. Record the definition used by the platform, not just the label.

### 4.3 Selectivity, pruning, and bytes

Let:

- \(N\) = rows in the candidate input;
- \(N_f\) = rows that satisfy a predicate;
- \(s\) = row selectivity;
- \(B\) = bytes in the relevant candidate scan units.

Then:

\[
s = \frac{N_f}{N}
\]

If 12,000 rows out of 1,000,000 satisfy a filter, \(s = 0.012 = 1.2\%\). The filter is selective, but the engine might still read the full 1,000,000-row input if the storage layout cannot prune data. **Low result selectivity is not the same as low scan volume.**

For a simple scan estimate:

\[
T_{\text{scan}} \approx \frac{B_{\text{read}}}{R_{\text{effective}}}
\]

where \(R_{\text{effective}}\) is the effective read rate under the observed conditions. This is only a rough lower-bound-style estimate for the read component: it ignores setup, metadata, decompression, CPU, network, contention, and overlapping work. It should not be treated as an end-to-end latency prediction.

If a query reads 24 GiB at an illustrative effective rate of 600 MiB/s:

- 24 GiB = 24 × 1,024 = 24,576 MiB.
- Estimated scan transfer time = 24,576 / 600 = 40.96 seconds.

That is an illustrative arithmetic estimate, not a benchmark. Actual scan time can be lower or higher because engines pipeline reads, parallelize work, reuse cache, decompress data, and overlap I/O with compute.

### 4.4 Distinguish three denominators

Never say “the query scans 1%” without defining what the 1% refers to.

- **Predicate selectivity:** qualifying rows / rows presented to the filter.
- **Pruning effectiveness:** scan units skipped / candidate scan units (for example, files or partitions).
- **Scan reduction:** bytes read after the change compared with bytes read before the change.

These can move independently. A 1%-selective predicate may still read 100% of the files; a partition predicate may skip 90% of files but still read many bytes within the remaining partitions.

---

## 5. Worked examples: scan volume, pruning, and query-plan reasoning

All sizes and performance figures in this section are illustrative.

### 5.1 Example A — column projection in a columnar format

Assume a table has 12 columns, each with similar compressed size, and the query needs only 3 columns. If the format and engine can read column chunks independently, a rough column-byte estimate is:

\[
B_{\text{selected}} \approx B_{\text{all}} \times \frac{3}{12}
\]

For an illustrative 120 GiB table, this gives approximately 30 GiB for those columns before accounting for metadata, compression differences, row-group selection, filters, and other overhead.

This is not a guarantee that the query reads exactly 25% of bytes. Column sizes can differ greatly, filters may require additional columns, and file layout may affect which row groups can be skipped. Still, selecting only required columns can reduce bytes read and the width of intermediate data.

Bad pattern:

```sql
SELECT *
FROM sales
WHERE sale_date >= DATE '2026-10-01';
```

Better when only three columns are needed:

```sql
SELECT sale_date, region, net_amount
FROM sales
WHERE sale_date >= DATE '2026-10-01';
```

The second query gives the optimizer an opportunity to avoid reading unneeded columns in a columnar system. It is not necessarily faster on every storage engine or for every small table.

### 5.2 Example B — partition pruning versus row filtering

Assume an event table contains 30 days of data at 2 GiB per day: 60 GiB total. A query needs 3 days.

**Case 1: date partitions are aligned with the filter**

- Candidate data: 60 GiB.
- Three relevant daily partitions: 3 × 2 GiB = 6 GiB.
- If partition pruning works, approximately 6 GiB of data files are candidates for reading, before column projection and file/row-group pruning.
- Candidate scan reduction: \(1 - 6/60 = 0.90\), or 90%.

**Case 2: data is not partitioned or organized to prune by date**

The filter may return the same 3 days of rows, but the engine may have to scan much or all of the 60 GiB to find them.

The row result is logically identical; the physical work differs. Partition pruning depends on the predicate, partition metadata, and the storage layout. A predicate wrapped in a non-prunable expression, type mismatch, or inaccurate metadata may prevent effective pruning in some systems.

### 5.3 Example C — estimate bytes and scan time

Suppose an illustrative query has these observations:

| Measurement | Before layout change | After layout change |
|---|---:|---:|
| Candidate data | 80 GiB | 80 GiB |
| Bytes read | 64 GiB | 8 GiB |
| Effective read rate assumed for estimate | 512 MiB/s | 512 MiB/s |
| Estimated scan component | 128 s | 16 s |

Arithmetic:

- 64 GiB = 65,536 MiB; 65,536 / 512 = 128 s.
- 8 GiB = 8,192 MiB; 8,192 / 512 = 16 s.

The estimate suggests a reduction of 112 seconds in the scan component if the effective rate remains constant. It does **not** prove end-to-end latency will improve by the same amount. The actual query could be dominated by a 180-second join, queue wait, or spill. Measure the complete execution and stage profile before claiming a user-visible improvement.

### 5.4 Example D — fewer scanned bytes, unchanged latency

Illustrative stage timing for one query:

| Component | Before | After pruning |
|---|---:|---:|
| Scan | 20 s | 3 s |
| Shuffle and join | 42 s | 42 s |
| Aggregate and final output | 8 s | 8 s |
| Total if sequential/non-overlapping for this illustration | 70 s | 53 s |

The scan falls by 85%, while total time falls by about 24%. The proportional change is smaller because the scan was not the whole query. In a real distributed plan, stages can overlap, so summing stage times may not equal wall-clock time. Use the engine's critical path or wall-clock timing when available.

### 5.5 Example E — read rows versus returned rows

A query returns 5,000 rows from a billion-row fact table. That result alone says nothing about how much work was required. If the engine scanned the whole table, the result can be small while the scan is large. If an index, partition metadata, or data skipping narrows the candidate set, the engine may inspect a much smaller portion.

Record at least:

- rows/files/partitions considered and actually read;
- bytes read and relevant columns;
- rows entering and leaving filters;
- rows entering and leaving joins/aggregations;
- output rows and bytes;
- elapsed time and resource waits.

### 5.6 Example F — join expansion and cardinality

Suppose `orders` has 1,000,000 rows and `order_items` has 4,000,000 rows. A join on unique `orders.order_id` to many `order_items.order_id` can reasonably produce about 4,000,000 rows before later filters, assuming every item references one existing order and there are no other filtering effects.

But if both sides contain repeated keys, the join can multiply rows. If a key occurs \(a_k\) times on the left and \(b_k\) times on the right, that key contributes \(a_k \times b_k\) joined rows. For a key with 20,000 rows on each side, that is 400,000,000 matched pairs for that key alone.

Before optimizing a join, verify key uniqueness and expected cardinality. A large output can be correct business logic or a data-quality/modeling defect; do not “optimize away” required rows.

---

## 6. Data layout: partitioning, clustering, indexing, files, and statistics

These mechanisms are related, but not interchangeable.

### 6.1 Partitioning

Partitioning divides a table or dataset into explicit subsets, commonly by a date, tenant, region, or another key. It can allow a query to eliminate entire partitions before reading data.

**Helps when:**
- frequent filters align with the partition key;
- each partition has enough data to justify its metadata and file organization;
- the engine can infer relevant partitions from the predicate.

**Can fail or regress when:**
- queries rarely filter by the partition key;
- partition count becomes excessive;
- many tiny partitions/files increase planning and listing overhead;
- one partition becomes disproportionately large or hot;
- writes and updates create operational complexity.

A partition key is not automatically a good partition key simply because the column is frequently used. Consider query patterns, data volume, cardinality, update behavior, and skew.

### 6.2 Clustering / sorting / data organization

Clustering groups nearby values or sorts data by selected columns within a table, partition, file, or storage unit. It can improve locality and data skipping for predicates on those columns, and may improve joins or aggregations in some engines.

**Helps when:** query filters or joins repeatedly use the clustered columns, and data is physically organized enough for the engine to skip units or exploit ordering.

**Costs:** ingestion/rewrite work, maintenance, compaction, sorting CPU, storage rewrite, and possible deterioration as new data arrives. Clustering may be weak if values are randomly distributed, data is small, or filters do not align with the layout.

Clustering is not the same as partitioning: clustering often organizes data within broader units rather than creating a separate top-level partition for every value.

### 6.3 Indexing

An index is an auxiliary structure that helps locate rows or keys without scanning the full base structure. Different index designs have different semantics; a B-tree-like index, bitmap index, inverted index, and zone-map-like metadata should not be treated as equivalent.

**Can help:** selective point lookups, range access, join-key lookup, or ordered retrieval when the index matches the predicate and the engine's access path.

**Can hurt:** broad scans where sequential I/O is more efficient, write-heavy workloads that must maintain indexes, storage growth, cache pressure, index bloat, or plans that perform many random lookups.

Columnar warehouses and object-storage lakehouses may use metadata, file statistics, clustering, bloom filters, or other skipping structures rather than conventional row-store indexes. Do not assume every platform supports the same mechanism.

### 6.4 File layout and file size

In lakehouse/object-storage systems, file layout affects how many objects must be listed/opened, how much metadata must be processed, parallelism, compression, and pruning opportunities.

- **Too many tiny files:** scheduling and metadata overhead, inefficient reads, more open/list operations.
- **Very large files:** may limit parallelism or make selective reads less efficient, depending on format and engine.
- **Well-sized columnar files:** can improve sequential throughput and column projection, but the appropriate size is platform- and workload-dependent.
- **Compaction:** can reduce small-file overhead, but consumes compute, adds I/O, and may contend with ingestion or interactive queries.

There is no universally optimal file size. Measure planning time, file counts, read throughput, parallelism, and workload-specific latency.

### 6.5 Statistics and metadata

Optimizers use statistics such as row counts, column distributions, distinct counts, null fractions, min/max values, and data sizes to estimate cardinality and choose plans. Some systems also maintain per-file or per-partition statistics.

Stale or incomplete statistics can lead to poor join order, wrong join strategy, unnecessary repartitioning, or memory estimates that are too low. Statistics are estimates, not truth; high-cardinality or correlated columns can make estimates difficult.

### 6.6 Predicate pushdown and partition pruning

- **Predicate pushdown:** applying a filter as close to the data source as practical, reducing downstream work and possibly reducing source reads.
- **Partition pruning:** excluding partitions that cannot satisfy a predicate.
- **File/row-group/data skipping:** excluding smaller storage units using metadata or clustering.
- **Column projection:** reading only columns required by the query and its filters/joins.

These are distinct optimizations. A filter may be pushed into a scan without enabling partition pruning. A query can prune partitions but still read unnecessary columns. Validate the actual plan and runtime scan metrics.

### 6.7 Practical predicate discipline

Prefer predicates whose meaning and data types match the stored columns and layout. For example, a direct date range is often easier to reason about for pruning than applying a function to every stored date value.

Potentially less pruning-friendly pattern (engine dependent):

```sql
WHERE EXTRACT(YEAR FROM sale_timestamp) = 2026
```

Direct range pattern:

```sql
WHERE sale_timestamp >= TIMESTAMP '2026-01-01 00:00:00'
  AND sale_timestamp <  TIMESTAMP '2027-01-01 00:00:00'
```

The second form may be easier for an optimizer to translate into range pruning. This is not a universal rule: optimizers may rewrite expressions, and timestamp types/time zones must be handled correctly. Inspect the plan and verify rows/bytes read.

---

## 7. Intermediate level: reading and diagnosing query plans

### 7.1 A repeatable plan-reading sequence

1. **Confirm the exact query and parameters.** Query text, bind values, date range, tenant, and data snapshot can change the plan and result size.
2. **Define the objective and boundary.** For example, client-observed p95 latency at 30 concurrent sessions.
3. **Locate the scan nodes.** Record table, partitions/files, projected columns, filters, estimated rows, actual rows, and bytes.
4. **Compare estimates with actuals.** Large cardinality errors can distort join choices and memory expectations.
5. **Follow rows and bytes through the plan.** Identify expansion, wide intermediates, repeated scans, unnecessary sorts, and large exchanges.
6. **Inspect joins and aggregates.** Record join type, join keys, build/probe inputs where exposed, shuffle/repartition, group cardinality, and skew.
7. **Inspect runtime resource symptoms.** CPU, I/O wait, network, spill, queue wait, task duration, memory pressure, and concurrent workload.
8. **Identify the critical path.** The longest or blocking stage may dominate wall-clock latency; parallel/overlapping stage durations must be interpreted carefully.
9. **Form ranked hypotheses.** Each hypothesis should state supporting evidence, counter-evidence, and the next measurement.
10. **Choose one primary change and validate it.** Keep result correctness and regression checks in the test plan.

### 7.2 Estimates versus actuals

An illustrative plan might report:

| Operator | Estimated rows | Actual rows | Interpretation |
|---|---:|---:|---|
| Filtered orders | 100,000 | 2,400,000 | Filter selectivity was badly estimated or data distribution changed |
| Join output | 150,000 | 3,900,000 | Join cardinality estimate is too low; inspect key multiplicity and filters |
| Aggregate output | 50,000 | 48,000 | Final group count is relatively close despite earlier errors |

A ratio such as `actual_rows / estimated_rows` can help flag estimation error, but very small estimates, adaptive plans, repeated loops, and engine-specific row-count semantics need care. The table alone does not tell you whether stale statistics, correlated predicates, skew, or an incorrect query assumption caused the difference.

### 7.3 Join strategies and when they can help

| Strategy | General idea | Often useful when | Possible failure mode / trade-off |
|---|---|---|---|
| Nested-loop-like join | For each row/key on one side, search the other side | One input is tiny or an indexed lookup is cheap | Can be disastrous for large unindexed inputs |
| Hash join | Build a hash structure for one input, probe it with the other | Equality join; build side fits available memory | Large build side, spill, skew, or extra data movement |
| Sort-merge join | Sort/order inputs by join key, then merge | Inputs are already ordered or sort cost is acceptable | Large sorts and spills if ordering is absent |
| Broadcast join | Copy a small input to multiple workers so a large input can join locally | Small filtered dimension and sufficient memory/network | Broadcast too large, replicated memory pressure, repeated transfer |
| Shuffle/repartition join | Redistribute both sides by join key, then join matching partitions | Large distributed inputs where keys need co-location | Network shuffle, skew, serialization, spill, stragglers |

No strategy is always faster. The correct choice depends on input sizes after filtering, key distribution, available memory, existing ordering, network cost, optimizer statistics, and concurrency. Avoid forcing a strategy before measuring; a hint that helps one data size can regress after growth.

### 7.4 Shuffle, sort, and aggregation

A **shuffle** redistributes rows across workers, often so all rows for a join key or group key meet in the same partition. It may require serialization, network transfer, buffering, and synchronization.

A **sort** orders rows. Sorting may be required by merge joins, window functions, `ORDER BY`, or an engine's chosen plan. If only a small top-N result is needed, an engine may use a more efficient top-N strategy, but this must be verified.

An **aggregation** may have partial/local and final/distributed phases. Local pre-aggregation can reduce the number of rows shuffled when many rows collapse into a small number of groups. It may help less when nearly every row has a distinct group key.

For each exchange, ask:

- How many bytes enter and leave?
- Is the redistribution required by semantics or by the chosen plan?
- Can filtering or projection occur before the exchange?
- Does local aggregation reduce rows enough to justify its CPU/state?
- Are task durations balanced, or is one key/partition dominating?
- Is the exchange spilling to disk or blocked by a slow receiver?

### 7.5 Data skew

Skew means the workload or data is unevenly distributed. For example, one customer may account for 30% of fact rows. A hash repartition by customer ID can send that customer's records to one partition, leaving one task with much more work.

A simple diagnostic measure is:

\[
\text{skew ratio} = \frac{\text{maximum partition load}}{\text{mean partition load}}
\]

Suppose eight partitions have loads `[10, 11, 9, 10, 12, 8, 10, 50]` arbitrary units. Total = 120; mean = 15; maximum = 50; skew ratio = 50/15 ≈ 3.33. One partition has about 3.33 times the mean load.

This ratio is a signal, not a complete diagnosis. The chosen “load” could be rows, bytes, CPU time, or duration; state which. A high duration ratio can also result from remote I/O or scheduling noise, not only key skew.

Possible responses include changing partition keys, pre-aggregating, handling known hot keys separately, salting where semantics permit, or choosing a different join plan. These approaches can add complexity, increase output work, complicate correctness, or make other queries slower. Detailed partitioning and hotspot design is Topic 04.

---

## 8. Advanced level: distributed execution and data locality

### 8.1 What locality means

Data locality describes how close the compute performing an operation is to the data it needs, measured in practical terms such as network hops, transfer volume, latency, cache residency, and remote-storage access. In separated compute/storage architectures, “locality” does not necessarily mean the data is on the same physical machine; it can mean avoiding unnecessary transfers, using efficient sequential reads, caching metadata, or colocating related work where the platform supports it.

Common sources of movement include:

- reading data from remote object storage;
- fetching blocks from a remote storage node;
- shuffling rows across workers for joins or aggregation;
- broadcasting a dimension table to many workers;
- transferring large intermediate results between execution stages;
- returning a large result set to a client or downstream service.

Movement has a cost in bandwidth, serialization/deserialization CPU, memory buffering, latency, and possible contention. The exact cost depends on hardware, network, compression, protocol, and concurrency.

### 8.2 Local compute versus movement

Consider two conceptual plans for joining a large fact table with a small dimension table.

**Plan A — repartition both inputs**
1. Read the fact table.
2. Read the dimension table.
3. Shuffle both by join key.
4. Join partitions.
5. Aggregate.

**Plan B — broadcast the filtered dimension**
1. Filter the dimension to a small set of rows.
2. Broadcast it to workers.
3. Read fact partitions and join locally against the broadcast copy.
4. Aggregate.

Plan B may avoid shuffling the large fact input. It can fail if the filtered dimension is larger than expected, if broadcast copies exceed memory, or if many concurrent queries replicate large structures. Plan A may be preferable for large inputs or when the dimension is not actually small.

The question is not “is broadcast faster?” but “what bytes move in each plan, how many copies are made, what memory is required, and what does the measured critical path show?”

### 8.3 Parallelism and the straggler problem

Parallel execution can shorten elapsed time when work divides well and resources are available. It does not make all workloads scale linearly.

Limits include:

- a serial stage or coordinator bottleneck;
- data skew, so a few tasks run much longer;
- network or storage bandwidth saturation;
- shared CPU/memory pressure;
- scheduling overhead and too many tiny tasks;
- synchronization barriers where all tasks must finish before the next stage;
- a client that cannot consume output fast enough.

A useful approximation for an idealized perfectly divisible workload is:

\[
T_P \approx \frac{T_1}{P}
\]

where \(T_1\) is the serial work time and \(P\) is the number of equal, independent workers. Real execution has serial work, overhead, uneven task sizes, contention, and communication; therefore this is an optimistic bound, not a performance promise.

Amdahl-style reasoning makes the serial fraction visible. If 20% of elapsed work cannot be parallelized and the remaining 80% is made infinitely fast, total speedup cannot exceed \(1/0.2 = 5\) under the simplified model. Use this to avoid expecting more benefit than the workload structure permits.

### 8.4 Memory pressure and spilling

Hash joins, hash aggregates, sorts, and window operators can require substantial working memory. If their working set exceeds memory available to the operator or worker, an engine may spill intermediate data to temporary storage, partition the operation, or reduce concurrency.

Symptoms to correlate:

- spill bytes and spill read/write time;
- operator memory estimates and observed peak memory;
- sudden latency increases as concurrency rises;
- large hash-build input or high-cardinality groups;
- a few tasks with disproportionately high memory use;
- queueing caused by memory limits or execution slots.

More memory may help a spilling query, but is not automatically the best fix. Reduce unnecessary columns and rows, improve join order or selectivity, address skew, or reduce concurrency if the evidence supports those changes. Raising per-query memory can reduce the number of concurrent queries the system can admit.

### 8.5 Remote reads and compute/storage separation

In separated compute/storage designs, compute can scale independently from stored data, but queries still pay for remote reads, metadata operations, and transfer. Performance can be influenced by:

- number of files and metadata operations;
- cache warmth and cache hit behavior;
- remote storage request latency and throughput;
- compression/decompression;
- file size and row-group layout;
- concurrency across tenants;
- data transfer between storage, compute, and client.

Do not infer that remote storage is the bottleneck merely because storage is remote. Look at read time, bytes, request counts, wait metrics, cache state, CPU, and competing workloads. Likewise, high network bytes are not inherently bad if they are required and well parallelized.

### 8.6 Query concurrency and workload interference

The same query can run differently under concurrent load. Many scans may compete for storage bandwidth; memory-heavy joins can reduce admission capacity; large batch jobs can interfere with interactive dashboards; and too many tasks can increase scheduling overhead.

Use Topic 02's queueing concepts. Record query latency by workload class and concurrency, not just a single overall average. Distinguish:

- **Intrinsic work:** scan, compute, shuffle, sort, and result transfer needed for the query.
- **Queueing/contention:** waiting due to shared resources or concurrency controls.
- **Workload interference:** other jobs consume resources or trigger contention.
- **Data-dependent variation:** different parameters, cardinalities, skew, or cache state.

A separate workload pool, concurrency cap, scheduling window, or resource allocation can improve isolation, but may increase cost or slow batch completion. Test with the actual mixed workload and agreed service objectives.

---

## 9. Measurement-driven diagnosis: evidence, hypotheses, and decisions

### 9.1 Use explicit evidence labels

Use the following labels in a review:

- **Observed fact:** directly measured or shown by a captured plan/runtime profile.
- **Calculated result:** derived from stated inputs and a reproducible formula.
- **Hypothesis:** a plausible explanation not yet confirmed.
- **Assumption:** an input accepted temporarily because evidence is unavailable.
- **Recommendation:** a proposed action based on evidence and trade-offs.
- **Unknown / limitation:** a material question not answered by current data.

Example:

- **Fact:** the runtime profile reports 72 GiB read and 110 GiB shuffled.
- **Fact:** p95 latency is 48 seconds under 20 concurrent queries in the recorded run.
- **Hypothesis:** the shuffle is the dominant bottleneck.
- **Needed evidence:** stage critical-path timing, task duration distribution, spill metrics, and a controlled run with a change that reduces shuffle volume.
- **Recommendation:** first test whether earlier filtering and column projection reduce the shuffle input; do not yet claim a specific latency gain.

### 9.2 A bottleneck hypothesis should be falsifiable

A useful hypothesis predicts an observable change.

Weak: “The query is slow because the table is too big.”

Stronger: “The query reads 72 GiB even though it filters to three date partitions. If partition pruning is failing, the runtime scan should show files from dates outside the range. We will inspect the physical scan and compare candidate partitions with actual files read. If the engine already reads only the three relevant partitions, this hypothesis is rejected.”

For each hypothesis, write:

1. Evidence supporting it.
2. Evidence against it or not yet available.
3. Next measurement.
4. Expected result if true.
5. Result that would falsify it.
6. Proposed change only after the measurement plan is clear.

### 9.3 Diagnosis workflow

1. **Reproduce the workload.** Preserve query text, parameters, dataset snapshot, concurrency, and relevant environment.
2. **Set success criteria.** Specify latency percentile, throughput, error rate, correctness, and resource constraints.
3. **Capture a baseline.** Record several runs where possible; note warm/cold cache, background jobs, and variance.
4. **Inspect plan and runtime.** Collect estimates, actual rows, bytes, task distribution, waits, and spill.
5. **Rank bottlenecks.** Separate scan, CPU, shuffle/network, memory/spill, queueing, and result transfer.
6. **Choose the smallest informative intervention.** Prefer a change that tests one principal hypothesis.
7. **Run a controlled comparison.** Keep other variables constant; repeat and report spread, not only the best run.
8. **Check correctness and regressions.** Compare result sets or aggregates, other workload classes, freshness, and write/maintenance cost.
9. **Document the decision.** Include evidence, uncertainty, alternatives, rollback, and follow-up measurements.

### 9.4 What counts as a good baseline?

A baseline should identify:

- query ID/text and parameter class (with sensitive values protected);
- dataset size, snapshot, and key distributions;
- physical plan and optimizer statistics state;
- engine/runtime version and relevant configuration;
- compute shape and resource limits;
- concurrency and workload mix;
- cache state or warm-up procedure;
- elapsed time and latency distribution;
- rows and bytes read, shuffle bytes, spill, output bytes;
- CPU, memory, storage/network, and wait indicators where available;
- correctness checks and measurement timestamp.

A single run is a useful observation, not a stable benchmark. Repeatability matters because cache, scheduling, autoscaling, compaction, and concurrent jobs can change the result.

---

## 10. Controlled experiments and optimisation trade-offs

### 10.1 Experiment design

A sound query-performance experiment includes:

- **Question:** one decision-oriented question.
- **Hypothesis:** a specific cause and predicted observable outcome.
- **Independent variable:** the principal thing changed (for example, partition layout).
- **Controls:** same data snapshot, query semantics, parameter class, resource allocation, concurrency, and measurement method.
- **Dependent metrics:** latency percentiles, bytes read, shuffle, spill, CPU, queue wait, correctness.
- **Success criterion:** a predeclared threshold or statistically/operationally meaningful change.
- **Regression criteria:** correctness, freshness, ingestion duration, storage growth, other query classes, and resource contention.
- **Repeat plan:** number and order of runs, warm/cold-cache policy, and how variance will be summarized.
- **Rollback plan:** how to revert the layout, index, configuration, or query change.

Change one principal variable at a time when possible. If multiple changes are bundled, the result may show that the bundle helped but not which change caused the effect. In some cases a factorial or staged experiment is more efficient, but confounding must still be controlled.

### 10.2 Compare median and tail, not only the fastest run

For each variant, report at least the number of runs, median latency, a spread measure (such as interquartile range), and relevant p95/p99 when the sample size supports those percentiles. Very small samples make tail percentiles unstable. Do not claim a reliable p99 from a handful of executions.

Keep workload and cache conditions comparable. If the new layout is warm in cache while the baseline is cold, the comparison may measure cache differences rather than layout quality.

### 10.3 Optimisation comparison matrix

| Candidate | Possible benefit | Maintenance / regression cost | Evidence needed |
|---|---|---|---|
| Narrow projection | Fewer bytes and narrower intermediates | Usually low, but query may need hidden filter/join columns | Read columns and bytes; compare correctness |
| Push filters earlier | Fewer rows downstream | Depends on semantics; filter may not be movable across all operations | Plan placement, input/output rows |
| Partition pruning | Avoids irrelevant partitions | Partition design and metadata overhead; skew risk | Partitions/files considered vs read, bytes |
| Clustering / sorting | Better locality or data skipping | Rewrite/maintenance cost; may decay as data arrives | Pruning metrics, read volume, write/maintenance impact |
| Index or skipping metadata | Faster selective access | Storage, write/update overhead, build/refresh cost | Access path, lookup/read cost, write impact |
| Broadcast small join input | Avoids shuffling large side | Replicated memory and network cost | Filtered build size, broadcast bytes, peak memory |
| Pre-aggregation | Shrinks rows before shuffle | Extra state/CPU; semantics must be preserved | Input/output rows, groups, result equivalence |
| Compaction | Fewer small files and less metadata overhead | Compute and I/O; contention during rewrite | File counts, planning time, scan throughput |
| Increase memory or compute | May reduce spill or shorten resource-bound work | Higher resource use; concurrency may still bottleneck | Spill, CPU, queue, per-stage timing |
| Separate workload pools / cap concurrency | Reduces interference and protects interactive latency | More idle capacity or slower batch completion | Latency by class, utilization, queueing, throughput |

### 10.4 Maintenance cost is part of performance

An optimization may reduce query time but increase ingestion latency, compaction work, storage footprint, metadata count, or operational risk. Evaluate the whole lifecycle:

- query frequency and criticality;
- read savings per execution;
- number of query patterns benefiting;
- data arrival/update pattern;
- refresh or rewrite cost;
- storage and metadata growth;
- effect on concurrency and other workloads;
- recovery and rollback complexity.

This lesson does not price those costs; Topic 06 covers formal cost models. Here, identify and measure the relevant cost drivers so the later model has sound inputs.

---

## 11. Representative SQL, pseudocode, and reproducible calculations

### 11.1 Illustrative schema

The SQL examples assume these conceptual tables:

```text
sales(
  sale_id, sale_timestamp, sale_date, customer_id,
  product_id, category, region, quantity, net_amount
)

customers(
  customer_id, region, customer_segment
)

products(
  product_id, category, product_name
)
```

Assumptions: `sale_id` identifies a sale row; `customers.customer_id` is unique; `products.product_id` is unique. Real schemas must verify these assumptions. Syntax such as date literals, explain commands, and statistics commands varies across engines.

### 11.2 Filter and project early where semantics permit

```sql
SELECT
    s.region,
    SUM(s.net_amount) AS net_sales
FROM sales AS s
WHERE s.sale_date >= DATE '2026-10-01'
  AND s.sale_date <  DATE '2026-10-08'
  AND s.category = 'Accessories'
GROUP BY s.region;
```

Review questions:

- Does the scan read only needed columns plus filter columns?
- Are date partitions/files outside the range skipped?
- Is the category predicate applied at or near the scan?
- How many rows/bytes reach the aggregation?
- Is the grouping cardinality small or unexpectedly high?

### 11.3 Join only required attributes

Less focused:

```sql
SELECT *
FROM sales AS s
JOIN customers AS c
  ON s.customer_id = c.customer_id
WHERE s.sale_date >= DATE '2026-10-01'
  AND s.sale_date <  DATE '2026-10-08';
```

More focused when only region and net amount are required:

```sql
SELECT
    c.region,
    SUM(s.net_amount) AS net_sales
FROM sales AS s
JOIN customers AS c
  ON s.customer_id = c.customer_id
WHERE s.sale_date >= DATE '2026-10-01'
  AND s.sale_date <  DATE '2026-10-08'
GROUP BY c.region;
```

The focused query reduces the requested output columns and may let the optimizer reduce columns carried through the join. The filter applies to the sales table; the optimizer may choose the physical join order and strategy. Always verify output semantics: if the customer table is not unique by `customer_id`, the join can multiply sales rows and inflate the sum.

### 11.4 Inspect a plan

Many engines support an `EXPLAIN`-style facility; some support an execution profile or an `EXPLAIN ANALYZE`-like command. Use the platform's documentation and avoid running an execution-analysis command on an expensive production query without understanding whether it executes the query.

Generic procedure:

```text
1. Capture the logical/physical plan.
2. If safe, execute on a representative test dataset.
3. Capture actual rows, bytes, operator/stage timings, shuffle, spill and waits.
4. Compare estimated and actual cardinalities.
5. Record which metrics are engine estimates and which are observed runtime values.
```

### 11.5 Python: calculate scan and pruning estimates

The following standard-library Python example is intended to run as-is on Python 3.9 or later. It estimates arithmetic only; it does not simulate a database engine.

```python
import math
from dataclasses import dataclass


def _nonnegative_int(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value < 0:
        raise ValueError(f"{name} must be non-negative")


def _finite_positive_rate(name: str, value: float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric")
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")


@dataclass(frozen=True)
class ScanEstimate:
    candidate_bytes: int
    bytes_read: int
    effective_bytes_per_second: float

    def __post_init__(self) -> None:
        _nonnegative_int("candidate_bytes", self.candidate_bytes)
        _nonnegative_int("bytes_read", self.bytes_read)
        if self.bytes_read > self.candidate_bytes:
            raise ValueError("bytes_read cannot exceed candidate_bytes")
        _finite_positive_rate(
            "effective_bytes_per_second", self.effective_bytes_per_second
        )

    @property
    def scan_reduction_fraction(self) -> float:
        if self.candidate_bytes == 0:
            return 0.0
        return 1.0 - self.bytes_read / self.candidate_bytes

    @property
    def estimated_scan_seconds(self) -> float:
        return self.bytes_read / self.effective_bytes_per_second


def selectivity(rows_matching: int, rows_examined: int) -> float:
    _nonnegative_int("rows_matching", rows_matching)
    _nonnegative_int("rows_examined", rows_examined)
    if rows_matching > rows_examined:
        raise ValueError("matching rows cannot exceed examined rows")
    if rows_examined == 0:
        if rows_matching == 0:
            return 0.0  # Explicit convention for an empty input.
        raise ValueError("matching rows cannot be positive when rows_examined is zero")
    return rows_matching / rows_examined


def estimated_scan_seconds(bytes_read: int, bytes_per_second: float) -> float:
    _nonnegative_int("bytes_read", bytes_read)
    _finite_positive_rate("bytes_per_second", bytes_per_second)
    return bytes_read / bytes_per_second


def test_examples() -> None:
    # 12,000 rows match out of 1,000,000 examined = 1.2%.
    assert abs(selectivity(12_000, 1_000_000) - 0.012) < 1e-12
    assert selectivity(0, 0) == 0.0

    # 60 GiB candidate data, 6 GiB read => 90% scan reduction.
    gib = 1024 ** 3
    estimate = ScanEstimate(
        candidate_bytes=60 * gib,
        bytes_read=6 * gib,
        effective_bytes_per_second=512 * 1024 ** 2,
    )
    assert abs(estimate.scan_reduction_fraction - 0.90) < 1e-12
    assert abs(estimate.estimated_scan_seconds - 12.0) < 1e-12

    # 24 GiB at 600 MiB/s => 40.96 seconds.
    assert abs(
        estimated_scan_seconds(24 * gib, 600 * 1024 ** 2) - 40.96
    ) < 1e-9
    assert estimated_scan_seconds(0, 1.0) == 0.0

    invalid_calls = [
        lambda: selectivity(2, 1),
        lambda: selectivity(-1, 10),
        lambda: selectivity(1, 0),
        lambda: selectivity(True, 10),
        lambda: estimated_scan_seconds(10, 0),
        lambda: estimated_scan_seconds(10, float("nan")),
        lambda: estimated_scan_seconds(10, float("inf")),
        lambda: estimated_scan_seconds(True, 10.0),
        lambda: ScanEstimate(10, 11, 1.0),
        lambda: ScanEstimate(-1, 0, 1.0),
        lambda: ScanEstimate(10, 0, float("nan")),
        lambda: ScanEstimate(10, 0, True),
    ]
    for invalid in invalid_calls:
        try:
            invalid()
        except (TypeError, ValueError):
            pass
        else:
            raise AssertionError("Expected invalid input to raise TypeError or ValueError")


if __name__ == "__main__":
    test_examples()
    print("Selectivity:", selectivity(12_000, 1_000_000))
    print("Scan reduction:", ScanEstimate(
        60 * 1024**3, 6 * 1024**3, 512 * 1024**2
    ).scan_reduction_fraction)
    print("Estimated scan seconds:", estimated_scan_seconds(
        24 * 1024**3, 600 * 1024**2
    ))
    print("All scan-estimate assertions passed.")
```

Expected output:

```text
Selectivity: 0.012
Scan reduction: 0.9
Estimated scan seconds: 40.96
All scan-estimate assertions passed.
```

These outputs verify the formulas and input guards in this small calculation model. They do not validate a database engine's physical scan rate or runtime behavior.

### 11.6 Python: compare end-to-end time with a bottleneck model

This deliberately simplified model assumes non-overlapping stages. Real distributed stages may overlap, so use this for reasoning, not as an engine simulator.

```python
import math


def sequential_total_seconds(stage_seconds: dict[str, float]) -> float:
    """Sum non-overlapping stage durations; not a distributed wall-time model."""
    if not stage_seconds:
        return 0.0
    for name, value in stage_seconds.items():
        if not isinstance(name, str) or not name:
            raise ValueError("stage names must be non-empty strings")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"stage time for {name!r} must be numeric")
        if not math.isfinite(value) or value < 0:
            raise ValueError(f"stage time for {name!r} must be finite and non-negative")
    return sum(stage_seconds.values())


def test_bottleneck_example() -> None:
    before = {"scan": 20.0, "shuffle_join": 42.0, "aggregate": 8.0}
    after = {"scan": 3.0, "shuffle_join": 42.0, "aggregate": 8.0}

    assert sequential_total_seconds(before) == 70.0
    assert sequential_total_seconds(after) == 53.0
    assert sequential_total_seconds({}) == 0.0

    scan_reduction = 1.0 - after["scan"] / before["scan"]
    total_reduction = 1.0 - sequential_total_seconds(after) / sequential_total_seconds(before)
    assert abs(scan_reduction - 0.85) < 1e-12
    assert abs(total_reduction - (17.0 / 70.0)) < 1e-12

    for invalid in [
        lambda: sequential_total_seconds({"scan": -1.0}),
        lambda: sequential_total_seconds({"scan": float("nan")}),
        lambda: sequential_total_seconds({"scan": float("inf")}),
        lambda: sequential_total_seconds({"scan": True}),
    ]:
        try:
            invalid()
        except (TypeError, ValueError):
            pass
        else:
            raise AssertionError("Expected invalid stage duration to fail")


if __name__ == "__main__":
    test_bottleneck_example()
    print("Before total: 70.0 s")
    print("After total: 53.0 s")
    print("Scan reduction: 85.0%")
    print("All bottleneck-model assertions passed.")
```

Expected output:

```text
Before total: 70.0 s
After total: 53.0 s
Scan reduction: 85.0%
All bottleneck-model assertions passed.
```

The example shows why scan reduction does not imply the same percentage reduction in total time. It is not a prediction for overlapping distributed execution.

---

## 12. Practical exercises

Attempt the questions before reading the answer keys. All numerical values are illustrative.

### 12.1 Beginner exercises

**B1 — selectivity.** A table scan examines 2,500,000 rows. A filter returns 50,000 rows. Calculate row selectivity as a percentage. Explain why this does not prove that only 2% of storage bytes were read.

**B2 — column projection.** A columnar dataset is 96 GiB across 8 equally sized columns. A query needs 2 columns. Estimate the selected-column bytes under the equal-size assumption. Name two reasons actual bytes may differ.

**B3 — partition pruning.** A 28-day dataset has 1.5 GiB/day. A query filters to 4 days. Estimate candidate bytes with aligned daily partition pruning and without pruning. Calculate the idealized reduction fraction.

**B4 — metric interpretation.** A query returns 200 rows but reports 90 GiB read. What does this suggest? What does it not prove?

### 12.2 Intermediate exercises

**I1 — scan estimate.** A query reads 18 GiB. Assume effective read throughput is 450 MiB/s. Estimate scan transfer time. List at least four reasons wall-clock query time may differ.

**I2 — plan estimates.** An estimated join output is 100,000 rows; actual output is 5,000,000. Give three possible causes and the evidence you would gather before changing the join strategy.

**I3 — skew.** Six partition loads are `[10, 12, 9, 11, 8, 40]`. Calculate the mean and skew ratio. Explain one caveat about interpreting this ratio.

**I4 — experiment.** A developer claims that clustering by `customer_id` reduced query latency by 50%, based on one run before and one run after. Write a better validation plan with controls, metrics, and regression checks.

**I5 — selectivity vs pruning.** A filter returns 0.5% of rows, but bytes read remain almost unchanged. Explain three plausible reasons and how to distinguish them.

### 12.3 Advanced exercises

**A1 — join locality.** A 2 GiB filtered dimension joins a 2 TiB fact table. Compare broadcast and repartition strategies. Do not declare a winner without discussing memory, network, replication, skew, concurrency, and measured plan evidence.

**A2 — scan reduction with fixed downstream cost.** In a simplified non-overlapping model, scan time is 30 seconds, join/shuffle is 50 seconds, and aggregation is 20 seconds. A change reduces scan time to 6 seconds while the other stages remain unchanged. Calculate the scan reduction and total-time reduction. Explain why this is only an illustrative model.

**A3 — workload interference.** An interactive query's p95 rises from 3 seconds to 15 seconds during a nightly batch job. Its bytes scanned remain similar, but queue wait and spill rise. Produce a ranked hypothesis list and identify the next measurements.

**A4 — maintenance trade-off.** A layout change reduces read bytes for a report used 20 times/day, but the rewrite adds 90 minutes of ingestion/maintenance work each day. Propose the evidence and decision criteria needed before adopting it. Do not invent a cost or claim a universal break-even point.

**A5 — critical path.** A profile shows 25 seconds scan, 50 seconds shuffle, 15 seconds aggregate, and 30 seconds queue wait. Explain why these numbers may not add to wall-clock latency in a distributed engine. State what you would inspect to identify the critical path.

**A6 — workload-level ranking.** Use the following fictional query workload. Calculate the daily query-time proxy (`frequency per day × mean seconds per execution`), rank the patterns, and choose layout or query changes for the top three. State which effects are predictions and how you would validate benefits and side effects.

| Pattern | Executions/day | Mean elapsed seconds/execution |
|---|---:|---:|
| Q1 — dashboard aggregate | 240 | 12 |
| Q2 — customer lookup | 5,000 | 0.2 |
| Q3 — daily revenue report | 40 | 45 |
| Q4 — audit full scan | 4 | 300 |
| Q5 — product search | 2,000 | 0.15 |
| Q6 — batch fact/dimension join | 12 | 180 |
| Q7 — customer 360 report | 80 | 25 |
| Q8 — export job | 3 | 600 |
| Q9 — ingestion validation | 24 | 60 |
| Q10 — metadata query | 1,000 | 0.5 |

Treat this as a prioritisation proxy, not compute cost or a guarantee of elapsed-time savings. Query executions may overlap and stage durations may not be additive.

---

## 13. Exercise answer key and reasoning

### 13.1 Beginner answers

- **B1:** \(50{,}000 / 2{,}500{,}000 = 0.02 = 2\%\). This is row selectivity. If the storage cannot skip rows or blocks, the engine may still read nearly all bytes.
- **B2:** \(96 \times 2/8 = 24\) GiB under the equal-size assumption. Actual columns may have different compressed sizes; filter, join, or partition metadata may require additional columns; and row-group pruning can change bytes read.
- **B3:** Total = \(28 \times 1.5 = 42\) GiB. Four days = \(4 \times 1.5 = 6\) GiB. Idealized reduction = \(1 - 6/42 = 6/7 \approx 85.7\%\). This assumes every day is equally sized and pruning skips all other daily partitions.
- **B4:** The query returns a small result after processing a much larger input, or the engine's bytes-read metric has a broad scope. It does not by itself prove a missing index, bad layout, or inefficient query. Inspect plan, predicate, partition/file counts, selected columns, and downstream operators.

### 13.2 Intermediate answers

- **I1:** 18 GiB = 18,432 MiB; \(18{,}432/450 \approx 40.96\) seconds. Actual time can differ due to parallel reads, overlap with CPU, compression/decompression, cache, metadata, queueing, network, and operator work.
- **I2:** Possible causes include stale statistics, correlated predicates, skew, unexpected duplicate keys/many-to-many relationships, parameter-specific distributions, or filters applied later than expected. Inspect actual input/output rows, key uniqueness and frequency, statistics age, predicate placement, per-task distribution, and runtime spill before choosing a strategy.
- **I3:** Total = 90; mean = 15; max = 40; skew ratio = \(40/15 \approx 2.67\). Caveat: define whether load means rows, bytes, CPU, or duration; a duration imbalance alone does not prove key skew.
- **I4:** Use the same query parameters, dataset snapshot, compute shape, concurrency, and cache policy; collect multiple runs; compare median and spread plus p95 if sample size supports it; inspect bytes read, pruning, shuffle, spill, and CPU; verify result correctness; measure write/maintenance cost and effects on other queries; define success and rollback criteria before testing.
- **I5:** The filter may not map to storage units; data may be randomly distributed; the engine may push the predicate but still need to scan all candidate blocks; a function/type conversion may inhibit pruning; or another required column/operator may dominate. Inspect physical scan, files/partitions read, row-group/file statistics, bytes read, and predicate placement.

### 13.3 Advanced answers

- **A1:** Broadcast can avoid shuffling the large fact side if the 2 GiB dimension remains small after filtering and can be replicated safely across workers. But 2 GiB per worker may be too large under concurrency, and serialization/network costs matter. Repartitioning may incur substantial shuffle but avoid broad replication. Compare actual filtered size, workers, memory headroom, network volume, key skew, spill, plan, and wall-clock profile.
- **A2:** Scan reduction = \(1 - 6/30 = 80\%\). Before total = \(30+50+20=100\) seconds; after = \(6+50+20=76\) seconds. Total reduction = \(24\%\). It assumes sequential non-overlapping stages and unchanged downstream work; a real distributed critical path can overlap.
- **A3:** First hypothesis: shared-resource contention from the batch workload, supported by correlated timing, queue wait, and spill; second: memory pressure from concurrent jobs; third: storage/network saturation if read waits also rise. Measure time-aligned per-class latency, admitted/running queries, CPU/memory, spill bytes, storage/network wait, task skew, and batch stages. A controlled run with the batch moved or throttled can test interference.
- **A4:** Compare report frequency, baseline/after bytes and latency distributions, query importance, ingestion SLOs, rewrite duration/compute, extra storage, effect on other queries, freshness, and operational risk. Decide based on business service objectives and measured lifecycle impact; Topic 06 can translate these quantities into a formal cost comparison.
- **A5:** Stages can overlap, and stage-level timers may count worker time across many tasks rather than elapsed critical-path time. Queue wait may overlap with other work or be measured at a different boundary. Inspect the query timeline/DAG, stage dependencies, task start/end times, per-stage wall-clock duration, waits, and whether metrics are summed across workers or measured as elapsed time.
- **A6:** Daily query-time proxy (executions × mean seconds): Q1 = 2,880 s/day; Q2 = 1,000; Q3 = 1,800; Q4 = 1,200; Q5 = 300; Q6 = 2,160; Q7 = 2,000; Q8 = 1,800; Q9 = 1,440; Q10 = 500. Ranking: Q1, Q6, Q7, then Q3/Q8 (tie), then Q9. Candidate ideas: Q1—test a summary/materialized aggregate or selective layout; Q6—inspect join cardinality, filter/project early, and compare broadcast/repartition with measured filtered size; Q7—test date/key partitioning or clustering only if the predicates and physical layout support pruning. These are hypotheses, not proven wins. Validate repeated before/after runs on the same data and workload, query correctness, bytes read/shuffled, latency distribution, concurrency effects, ingestion/maintenance cost, freshness, and regressions. The proxy is not dollars and can double-count overlapping elapsed time; use engine resource/cost metrics for a formal cost ranking.

---

## 14. Industry-style scenarios and architecture comparisons

The organisations and measurements below are fictional teaching scenarios, not real benchmarks.

### 14.1 Scenario A — a report scans full history

**Symptoms:** A report filters to the latest seven days but reads most of a multi-year fact table. Runtime is 40 minutes.

**Candidate options:**
1. Partition on date and verify pruning.
2. Cluster/sort by date or a frequently paired filter.
3. Create a summary/aggregate table for a repeated report pattern.
4. Keep the current design if the query is rare and the maintenance cost outweighs the benefit.

**Evidence needed:** query frequency, bytes read, date partitions/files considered and read, predicate placement, layout, report freshness, and write/maintenance costs.

**Reasoning:** Date partitioning may be a straightforward first test if queries consistently filter on date and the table is large enough. A summary table may reduce repeated work but introduces refresh logic, freshness constraints, and extra storage. Do not recommend both automatically.

### 14.2 Scenario B — a skewed join has one long-running task

**Symptoms:** Most tasks finish quickly; one task runs 12 times longer. A single customer accounts for a large fraction of rows.

**Candidate options:** validate join cardinality and key frequency; filter/project earlier; pre-aggregate if semantics allow; isolate a hot key; consider salting or an alternative distribution strategy.

**Evidence needed:** per-task rows/bytes/time, key frequency distribution, actual join output, spill, shuffle bytes, and correctness requirements.

**Trade-off:** Salting can spread a hot key but may require replication or a two-stage aggregate and can increase complexity. It is not a safe generic rewrite for every join.

### 14.3 Scenario C — interactive queries slow during batch

**Symptoms:** Interactive p95 and p99 rise during batch processing; scan bytes for each query remain similar.

**Candidate options:** schedule batch away from peak, throttle it, separate workload pools, reserve capacity for interactive work, or optimize the batch's resource-heavy stage.

**Evidence needed:** time-aligned per-class latency, queue wait, CPU, memory, spill, network/storage metrics, concurrency, and service objectives for each class.

**Trade-off:** Isolation protects latency but can leave resources idle or slow batch completion. Scheduling is simpler if a business window exists; separate pools may be justified where latency guarantees are important.

### 14.4 Scenario D — an index helps one query but slows ingestion

**Symptoms:** Selective point lookups improve, while insert/update throughput drops and index storage grows.

**Decision method:** quantify read frequency and criticality, observed lookup latency, write overhead, index size and maintenance, and whether alternative layout/pruning meets the objective. Keep the index only if the workload-level trade-off is acceptable.

**Key lesson:** optimize the workload, not a single query in isolation.

### 14.5 Architecture comparison: one large scan versus maintained layout

| Dimension | Broad scan / simple layout | Pruned or clustered layout |
|---|---|---|
| Read work | May read many irrelevant units | Can skip irrelevant partitions/files/blocks |
| Query latency | Predictable for simple sequential scans; may be large | May improve selective workloads; depends on pruning |
| Ingestion | Often simpler | May require partition routing, sorting, rewrite or compaction |
| Metadata | Usually simpler | May grow with partitions, files, and statistics |
| Skew risk | Depends on execution distribution | Poor partition choice can create hot or oversized units |
| Maintenance | Lower layout maintenance | Periodic maintenance and validation may be required |
| Best evidence | Scan throughput and query distribution | Bytes/files skipped, latency, maintenance cost, regression tests |

No column represents a universal winner. The right choice follows actual query patterns and measured operational constraints.

---

## 15. Common mistakes and troubleshooting

| Mistake | Why it fails | Better approach |
|---|---|---|
| Reporting only average latency | Hides tail behavior and outliers | Use p50/p95/p99 with a stated sample/window |
| Equating few result rows with little work | Large scans can produce tiny results | Compare input rows/bytes with output rows/bytes |
| Assuming low selectivity means low scan bytes | Storage may not skip rejected rows | Inspect pruning and actual bytes read |
| Assuming an index is always faster | Random lookups and index maintenance can cost more than a scan | Compare the actual access path and workload mix |
| Assuming partitioning always helps | Wrong key or too many partitions can add overhead | Test workload alignment, metadata, and skew |
| Treating clustering and partitioning as synonyms | They create different forms of data organization | State which units can be skipped and how |
| Optimizing only the scan | Join, shuffle, queueing, or client transfer may dominate | Identify the critical path and end-to-end effect |
| Reading the plan but ignoring runtime | Estimates can be wrong; resource contention varies | Compare estimates with actual rows, bytes, and waits |
| Treating stage timers as additive wall time | Parallel tasks and stages can overlap | Use timeline/DAG and critical-path interpretation |
| Broadcasting because one input “looks small” | Filtered size or concurrency may make replication expensive | Measure post-filter size, memory, and broadcast bytes |
| Ignoring skew | Average task time hides stragglers | Inspect task-duration and input distributions |
| Adding memory without diagnosing spill | More per-query memory may reduce concurrency | Correlate spill, working set, and queueing |
| Optimizing one query without workload context | Other queries or ingestion may regress | Measure workload-level effects and maintenance costs |
| Comparing one before/after run | Cache, load, and noise confound results | Repeat controlled runs and report variability |
| Changing many things at once | Causal attribution becomes difficult | Change one principal variable or design a controlled multi-factor experiment |
| Calling an estimate a benchmark | A formula is not observed engine behavior | Label assumptions and measure real execution where possible |
| Claiming an optimization is “free” | Layout/index changes add write, storage, or operational cost | Include maintenance, freshness, metadata, and regression risks |
| Using a production `EXPLAIN ANALYZE` blindly | Some commands execute the query and can be expensive | Confirm semantics and test safely on representative data |

### 15.1 Troubleshooting checklist

When a query is slow, answer these in order:

- [ ] Is the latency objective defined, and is the measurement boundary clear?
- [ ] Is the exact query/parameter class and dataset snapshot known?
- [ ] Does the physical plan show expected filters and projected columns?
- [ ] Are partitions/files/row groups actually being skipped?
- [ ] Are estimated and actual cardinalities materially different?
- [ ] Does a join multiply rows unexpectedly?
- [ ] Are shuffle bytes large relative to input and output?
- [ ] Are task times skewed or are there stragglers?
- [ ] Is there spill, memory pressure, or resource waiting?
- [ ] Does the problem correlate with concurrency or other workloads?
- [ ] Is the final result large or slow to transfer?
- [ ] Is the suspected cause supported by a measurement, or is it still a hypothesis?
- [ ] Is the proposed test able to disprove the hypothesis?
- [ ] Are correctness, ingestion, freshness, and other workloads included in regression checks?

---

## 16. Expected deliverables

Produce the following review package for one representative query or workload class.

### 16.1 Deliverable A — query workload and performance-metric profile

Include:

| Field | Required content |
|---|---|
| Workload name / owner | Name or role responsible for the query |
| Business purpose | Decision or product behavior supported |
| Query pattern | Point lookup, range scan, analytical scan, join/aggregate, etc. |
| Frequency and concurrency | Typical and peak rates; simultaneous workloads |
| Data profile | Table sizes, growth, key distributions, skew, freshness |
| Objectives | Latency percentiles, throughput, errors, freshness, correctness |
| Environment | Compute, storage, engine version, resource limits |
| Measurement boundary | Start/end events and included waits/transfers |
| Evidence source | Plan, runtime profile, logs, synthetic calculation, or assumption |
| Unknowns | Missing facts and how to obtain them |

### 16.2 Deliverable B — query-plan analysis

Document:

- logical intent and physical plan summary;
- scan nodes and filters/projection;
- estimated versus actual rows;
- join strategy and input/output cardinality;
- shuffle, sort, aggregation, and intermediate growth;
- spill, skew, resource wait, and task-duration evidence;
- critical-path interpretation;
- facts, hypotheses, assumptions, and unknowns separately.

### 16.3 Deliverable C — scan-volume and data-movement assessment

Calculate or measure:

- candidate table/partition/file volume;
- bytes actually read;
- scan reduction and/or pruning ratio with definitions;
- estimated scan transfer time with explicit throughput assumption;
- shuffle/broadcast/remote-read/output bytes where available;
- intermediate row and byte expansion;
- important limits of the measurements.

### 16.4 Deliverable D — evidence-backed bottleneck hypotheses

For each hypothesis:

| Field | Content |
|---|---|
| Rank | Expected impact and confidence |
| Hypothesis | Specific possible cause |
| Supporting evidence | Observed facts or calculations |
| Counter-evidence / gaps | What weakens or is missing |
| Confirming measurement | Next metric or controlled test |
| Falsification condition | What result would reject it |
| Risk if wrong | Cost or regression risk of acting prematurely |

### 16.5 Deliverable E — optimisation proposal and validation plan

For each candidate change, include expected benefit, evidence basis, assumptions, implementation/maintenance effort, storage and ingestion effects, risks, regression scope, success criteria, rollback plan, and owner. Rank proposals by expected value and confidence, not by fashion.

A recommendation should distinguish:

- **Measured result:** demonstrated in the stated environment.
- **Expected benefit:** a reasoned prediction not yet verified.
- **Open question:** a material uncertainty requiring a test.

---

## 17. Mastery criteria and completion gate

### 17.1 Mastery criteria

You have mastered this topic when you can:

1. Explain query stages and identify which metrics describe scan, movement, compute, waits, and output.
2. Estimate scan time with correct units and explain why it is not an end-to-end latency prediction.
3. Distinguish row selectivity from partition pruning and bytes scanned.
4. Explain partitioning, clustering, indexing, file layout, and statistics without treating them as interchangeable.
5. Read a conceptual plan and identify where estimated and actual cardinalities diverge.
6. Compare join strategies using input size, data movement, memory, and skew.
7. Explain how locality, parallelism, remote reads, spill, and concurrency affect latency.
8. Show why a large scan reduction may yield a smaller end-to-end gain.
9. Form hypotheses that are supported by evidence and can be falsified.
10. Design a controlled experiment with correctness and regression checks.
11. State the trade-offs and maintenance costs of the chosen layout or query change.
12. Explain what the evidence does not prove.

### 17.2 Completion gate

- [ ] Query workload and performance-metric profile completed.
- [ ] Query plan interpreted, with estimates distinguished from runtime observations.
- [ ] Scan-volume and data-movement worksheet completed; units and arithmetic reproduced.
- [ ] At least three bottleneck hypotheses labelled and ranked by evidence.
- [ ] At least two optimisation options compared with benefits, risks, and maintenance costs.
- [ ] A controlled before/after validation plan states controls, metrics, sample/repeat approach, success criteria, correctness checks, and rollback.
- [ ] Beginner, intermediate, and advanced exercises attempted; gaps logged.
- [ ] No performance gain is described as measured unless it was actually measured.
- [ ] Review distinguishes findings, calculations, assumptions, hypotheses, recommendations, and unknowns.

**Readiness statement:** You are ready for Topic 04 when you can explain not only how a query can read and move less data, but also when the remaining constraint requires changing how load and data are distributed.

---

## 18. Transition to Topic 04 — Scaling, partitioning, sharding, and hotspots

Topic 03 focuses on query execution and locality: the data touched, the operators used, the bytes moved, and the resource waits observed. Topic 04 asks a related but different question:

> Once the query and access path are understood, how should data and workload be distributed so that capacity, parallelism, and failure or hotspot behavior remain acceptable as demand grows?

Topic 04 will extend the reasoning to scale-up versus scale-out, partition/shard keys, skew, hot keys, effective capacity, resharding movement, and validation with realistic distributions. Bring forward the query profile, key-frequency evidence, shuffle/task-skew measurements, workload objectives, and the list of unresolved hypotheses from this lesson.

The hand-off is complete when the proposed optimisation is evidence-backed, its trade-offs are explicit, and the remaining distribution problem is clearly separated from a query-plan problem.
