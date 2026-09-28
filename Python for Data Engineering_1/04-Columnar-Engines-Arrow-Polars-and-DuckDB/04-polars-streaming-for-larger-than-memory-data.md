# Polars Streaming for Larger-than-Memory Data

> **Stage 2 — Python for Data Engineering**  
> **Module 2.4 — Columnar Engines, Arrow, Polars and DuckDB**  
> **Topic 04**

This chapter teaches how a single-node Polars pipeline can process workloads larger than available RAM by executing a compatible lazy query incrementally rather than materializing the entire input at once.

The central engineering idea is:

```text
Lazy execution
=
build and optimize a query plan before execution

Streaming execution
=
execute a compatible plan incrementally in batches/morsels
```

Therefore:

```text
Lazy ≠ automatically streaming
```

A `LazyFrame` can exist without being executed in streaming mode. The query plan still has to be executable by the selected engine, and individual operators can retain substantial state.

---

# 1. Learning Objectives

After completing this chapter, you should be able to:

- explain why datasets larger than RAM create problems
- explain the difference between disk size and execution memory
- explain in-memory processing and out-of-core processing
- explain streaming execution from first principles
- explain batches, chunks, and morsels
- explain bounded working memory without claiming constant memory
- distinguish lazy execution from streaming execution
- run a Polars lazy query with `collect(engine="streaming")`
- use streaming sinks such as `sink_parquet`
- understand `sink_csv`, `sink_ipc`, and `sink_ndjson`
- identify operations that generally stream well
- identify operations that may retain large amounts of state
- reason about group-by state
- reason about join state and the conceptual build side
- reason about global sorting
- reason about some window operations and pivoting
- investigate streaming fallback or memory-heavy plan regions
- redesign a pipeline to reduce rows, columns, and retained state early
- understand partition-wise processing and its semantic risks
- write partitioned output when the installed Polars version supports the required sink API
- reason about batch/chunk sizing
- understand `POLARS_MAX_THREADS`
- understand CPU parallelism versus memory pressure
- measure peak memory on Linux
- benchmark streaming workloads fairly
- compare Polars streaming with pandas manual chunking
- explain chunk-boundary correctness
- understand GPU execution at awareness level
- understand distributed Polars at awareness level
- recognize the practical single-node limit
- complete the required streaming exercises and capstone

The most important question to answer by the end is:

> **How can Polars process a dataset that is larger than available RAM without first materializing the complete input in memory?**

And the deeper production question is:

> **What makes a pipeline streamable, what causes memory growth, how can streaming fall back to other execution, how do I detect that, and how do I redesign the pipeline?**

---

# 2. Prerequisites

This chapter builds on:

- CPU, RAM, and storage concepts
- Python fundamentals
- pandas and pandas chunking
- Arrow columnar memory concepts
- Polars eager API
- Polars expressions and contexts
- Polars Lazy API
- predicate pushdown
- projection pushdown
- basic Parquet concepts

You should already recognize code such as:

```python
import polars as pl

lf = pl.scan_parquet("data/*.parquet")
```

You do not need to re-learn the entire Lazy API here. We will concentrate on what changes when the execution target is a larger-than-memory workload.

---

# 3. Why Data Larger Than RAM Is a Problem

Start with a concrete machine:

```text
Available RAM = 16 GB
Dataset      = 40 GB
```

A naive eager load might look like:

```python
import polars as pl

df = pl.read_parquet("large_dataset.parquet")
```

This does not mean Polars simply needs "40 GB of RAM because the file is 40 GB".

The critical distinction is:

```text
File size on disk
        ≠
Memory required during execution
```

A Parquet file is compressed and encoded for storage. When columns are decoded into an in-memory representation, the memory footprint can be very different from the compressed file size.

During a real query, additional memory can be required for:

- decompressed column data
- intermediate expressions
- aggregation state
- join state
- sorting state
- temporary buffers
- thread-local working memory
- output buffers
- validity/null metadata
- string data and offsets
- allocator overhead
- copies created by transformations
- the final result

For example:

```text
10 GB Parquet on disk
        ↓
possibly much larger decoded columns
        ↓
intermediate state
        ↓
join/group/sort state
        ↓
final result
```

The exact peak depends on data types, compression, cardinality, query structure, the engine, the machine, and the Polars version.

## Why "the file fits on disk" is not enough

Storage and RAM serve different roles:

```text
SSD / object storage
--------------------
large capacity
slower access
persistent

RAM
--------------------
small capacity
fast access
working memory
```

A 100 GB dataset can be perfectly valid on storage while being too large to materialize safely in a 16 GB or 32 GB process.

## Memory pressure is not the same as an immediate out-of-memory error

A process can become unhealthy before the operating system kills it.

Typical progression:

```text
low memory use
    ↓
higher memory use
    ↓
less headroom
    ↓
allocator contention / reclaim / paging pressure
    ↓
very slow execution
    ↓
container OOM / OS OOM / process failure
```

Production data engineering therefore asks:

> **What is the peak working set of this plan, not only how large is the input file?**

---

# 4. In-Memory Processing vs Out-of-Core Processing

## 4.1 In-memory processing

The simplest mental model is:

```text
Dataset
   ↓
Load into RAM
   ↓
Compute
   ↓
Result in RAM
```

For an eager Polars workflow:

```python
import polars as pl

df = pl.read_parquet("events.parquet")

result = (
    df
    .filter(pl.col("status") == "ok")
    .group_by("customer_id")
    .agg(pl.col("amount").sum())
)
```

The input is already materialized as a `DataFrame`.

That is convenient and often fast when the dataset and intermediates fit comfortably in memory.

## 4.2 Out-of-core processing

Out-of-core processing means:

> The workload is designed so that the active working set does not need to contain the entire dataset at once.

Conceptually:

```text
Dataset
   ↓
read part
   ↓
process part
   ↓
update retained state
   ↓
release/reuse working memory
   ↓
read next part
   ↓
continue
```

The key word is **working set**.

---

# 5. Working Set: The Most Useful Mental Model

Keep this distinction in your head:

```text
Total dataset size
        ≠
Working-set size
```

Suppose:

```text
Input dataset = 100 GB
Available RAM = 16 GB
```

A well-designed query may reduce the active data quickly:

```text
100 GB input
    ↓ filter
  8 GB relevant rows
    ↓ projection
  3 GB needed columns
    ↓ aggregation
  retained group state
    ↓
manageable working set
```

This is conceptual, not a memory guarantee.

Actual process memory includes:

- buffers
- operator state
- thread-local data
- metadata
- allocator overhead
- result buffering

A streaming engine helps by avoiding unnecessary whole-input materialization, but it cannot make arbitrary global state disappear.

---

# 6. What Is Streaming Execution?

A beginner-friendly definition:

> **Streaming execution means the engine processes manageable portions of the input through the execution plan incrementally instead of treating the complete input as one giant in-memory object.**

Important terms:

### Batch

A manageable set of rows processed together.

### Chunk

A physically buffered set of rows or column data.

### Morsel

A small unit of work used internally by some query engines for parallel execution.

You can use "batch" as the beginner mental model. The internal implementation can be more sophisticated than a simple Python loop.

### State

Information an operator retains across input batches.

Examples:

```text
filter
→ little retained global state

group_by
→ aggregation state

join
→ match/build/probe state

global sort
→ ordering state
```

## Conceptual execution

```text
Input Dataset
     ↓
 Batch 1 → operators → partial output/state
 Batch 2 → operators → partial output/state
 Batch 3 → operators → partial output/state
 Batch 4 → operators → partial output/state
 ...
```

The important nuance is:

> **Not every operator independently processes one batch and immediately forgets it.**

A stateful operator can keep information from earlier batches.

---

# 7. Memory-Bounded Processing

Suppose:

```text
Dataset      = 100 GB
Available RAM = 16 GB
```

A streaming-compatible query can make this possible by processing the data incrementally.

But do not memorize the incorrect rule:

```text
streaming
=
memory usage exactly one tiny batch
```

That is not how real query engines work.

Memory still depends on:

- batch/chunk size
- number of concurrent tasks
- data types
- number of columns
- aggregation cardinality
- join state
- sorting requirements
- window state
- output buffering
- caches
- engine implementation
- query shape
- resource limits imposed by the container

A better model is:

```text
Peak memory
≈
input working buffers
+ operator state
+ intermediates
+ output buffers
+ runtime overhead
```

The exact formula is not fixed.

---

# 8. Lazy + Streaming Execution Model

This chapter extends the Lazy API concepts from Topic 03.

The full conceptual pipeline is:

```text
Source
  ↓
LazyFrame
  ↓
Expressions
  ↓
Logical plan
  ↓
Optimizer
  ↓
Execution strategy
  ├── in-memory
  └── streaming
        ↓
     batches/morsels
        ↓
     operators
        ↓
     output
```

This leads to two very important statements:

```text
Lazy execution
=
defer execution + build/optimize a plan
```

and:

```text
Streaming execution
=
execute a compatible plan incrementally
```

Therefore:

```text
Lazy ≠ Streaming
```

A `LazyFrame` is a description of work.

Streaming is an execution strategy.

## Why lazy execution helps streaming

The optimizer can often reduce the amount of work before execution.

For example:

```text
100 GB source
    ↓ predicate pushdown
20 GB relevant rows
    ↓ projection pushdown
only 8 columns read
    ↓ streaming execution
incremental processing
```

So:

> **Good streaming starts before execution. Query design determines the amount of work the streaming engine must perform.**

---

# 9. `collect(engine="streaming")`

For current Polars APIs, the explicit form is:

```python
import polars as pl

result = (
    pl.scan_parquet("data/*.parquet")
    .filter(pl.col("amount") > 0)
    .select(["customer_id", "amount"])
    .collect(engine="streaming")
)
```

What happens?

1. `scan_parquet(...)` creates a lazy scan.
2. `.filter(...)` adds a predicate to the plan.
3. `.select(...)` narrows the columns.
4. `.collect(...)` triggers execution.
5. `engine="streaming"` asks Polars to use the streaming engine.

## Why use `collect(engine="streaming")`?

It is useful when:

- the input is larger than RAM
- a compatible query can be executed incrementally
- you still need a final `DataFrame`
- the result itself is small enough to materialize

## A critical limitation

This:

```python
result = lf.collect(engine="streaming")
```

still produces a `DataFrame`.

If the final result is itself 30 GB, you have not solved the result-materialization problem.

The pipeline may stream the input but eventually collect a huge result into RAM.

That is where sinks matter.

## Version awareness

Polars APIs evolve quickly. Use the current documented API for the installed version.

For training and reproducibility, an explicit:

```python
.collect(engine="streaming")
```

is a clear way to communicate intent even when default engine resolution changes across major versions.

Some current Polars documentation for version 2 describes `"auto"` resolving to the streaming engine for lazy queries, while the stable documentation still presents `"auto"` as an environment/configuration-dependent default. For this reason, do not rely on implicit default behavior in benchmark documentation; record the explicit engine choice and installed version.

---

# 10. Streaming Sinks

Consider this pipeline:

```text
huge input
    ↓
streaming execution
    ↓
huge DataFrame in RAM
    ↓
write output
```

For a huge result, the final materialization can defeat the benefit.

A sink changes the shape:

```text
huge input
    ↓
streaming execution
    ↓
incremental output
    ↓
disk/object storage
```

Current Polars APIs include lazy sinks such as:

- `sink_parquet`
- `sink_csv`
- `sink_ipc`
- `sink_ndjson`

These evaluate a lazy query in a streaming-oriented output path so results larger than RAM can be written incrementally.

## Important caveat

A sink does **not** mean:

```text
memory = zero
```

A sink can still require:

- operator state
- output buffers
- compression state
- metadata
- join/group state
- temporary working memory

The benefit is that you avoid requiring the **entire final result** to exist in RAM at once.

---

# 11. `sink_parquet`

A basic pattern is:

```python
import polars as pl

lf = (
    pl.scan_parquet("silver/trips/*.parquet")
    .filter(pl.col("trip_status") == "completed")
    .select([
        "trip_id",
        "trip_date",
        "zone_id",
        "fare",
    ])
)

lf.sink_parquet("gold/completed_trips.parquet")
```

The sink executes the query and writes the result directly to Parquet.

## Why this matters

Without a sink:

```text
query
 ↓
DataFrame in RAM
 ↓
write_parquet
```

With a sink:

```text
query
 ↓
streaming execution
 ↓
Parquet output incrementally
```

## Practical trade-offs

A sink is attractive when:

- the output is large
- the final result does not need immediate in-memory use
- the next stage can consume the persisted data
- you want lower output materialization pressure

A collected `DataFrame` is attractive when:

- the result is small
- the next operation genuinely requires an in-memory frame
- you need interactive inspection

Do not use a sink simply because "sinks are always faster". Measure your workload.

---

# 12. `sink_csv`, `sink_ipc`, and `sink_ndjson`

Current Polars APIs also provide:

```python
lf.sink_csv("out.csv")
lf.sink_ipc("out.arrow")
lf.sink_ndjson("out.ndjson")
```

Conceptually:

```text
LazyFrame
   ↓
streaming execution
   ↓
incremental serialization
   ↓
output file
```

## `sink_csv`

Useful when downstream systems require CSV.

Trade-off:

- CSV is portable
- CSV is text-based
- CSV is usually larger and less typed than Parquet
- CSV can be slower to read and write

## `sink_ipc`

IPC/Arrow output is useful when Arrow-compatible consumers matter.

Trade-off:

- excellent interoperability within the Arrow ecosystem
- less universally used as a lake format than Parquet
- choose based on the surrounding architecture

## `sink_ndjson`

Useful for line-oriented JSON interoperability.

Trade-off:

- readable and operationally convenient
- text serialization is usually less compact than columnar formats
- schema is less strongly encoded than a typed columnar storage format

The correct sink depends on downstream requirements, not only memory.

---

# 13. Which Operations Stream Well?

Treat operation classifications as **engineering tendencies**, not eternal laws.

Exact behavior depends on:

- Polars version
- query shape
- data distribution
- operator implementation
- ordering requirements
- whether the operation can maintain incremental state

## 13.1 Generally streaming-friendly

Often good candidates include:

- file scanning
- filtering
- projection/select
- many column expressions
- many aggregations
- many joins

Why?

Because the engine can often process pieces of input while incrementally applying the operator.

## 13.2 Potentially state-heavy

Examples:

- high-cardinality aggregations
- large joins
- deduplication
- some window calculations
- rolling operations depending on query shape

The input can be processed in batches while the operator retains a growing state.

## 13.3 Often difficult for straightforward streaming

Examples:

- global sorts
- some pivot workloads
- certain global ranking/window workloads
- operations that require substantial knowledge of the complete input

The important lesson is not:

> "This operation is always non-streaming."

The better lesson is:

> "This operation creates a global dependency or large retained state, so investigate its actual execution behavior."

---

# 14. Why Some Operations Need Full Data or Large State

## 14.1 Global sort

Suppose you must globally sort one billion rows by timestamp:

```python
lf.sort("event_time")
```

A naive batch model is insufficient:

```text
Batch 1 sorted
Batch 2 sorted
Batch 3 sorted
```

does not automatically yield one globally sorted result.

For example:

```text
Batch 1 → timestamps 10, 20, 90
Batch 2 → timestamps 15, 30, 40
```

Concatenating sorted batches produces:

```text
10, 20, 90, 15, 30, 40
```

which is not globally sorted.

A global ordering requirement creates a large dependency across the input.

An execution engine may use sophisticated techniques, including buffering, partitioning, or temporary storage in some contexts, but the key engineering point is:

> **Global order is fundamentally harder to maintain incrementally than a row-local filter.**

## 14.2 Pivot

A pivot changes the output schema based on encountered values.

Input:

```text
customer | month | revenue
A        | Jan   | 100
A        | Feb   | 120
B        | Jan   |  90
```

Possible output:

```text
customer | Jan | Feb
A        | 100 | 120
B        |  90 | null
```

The complete output structure depends on the set of pivot values.

This is more globally stateful than a straightforward row filter.

## 14.3 Window functions

Window functions vary significantly.

Potential memory drivers include:

- partition state
- ordering
- frame width
- global versus local dependency
- implementation details

Examples that can be demanding:

```text
global ranking
ordered partitions
large window frames
```

Do not assume every window expression behaves identically.

---

# 15. Streaming Fallbacks

A query can be requested with:

```python
.collect(engine="streaming")
```

while still containing portions of work that are not implemented or suitable for streaming execution.

Conceptually:

```text
streaming-compatible region
        +
non-streaming region
        ↓
execution may use another engine/plan path
```

A fallback is important because a query can still succeed while consuming more memory than you expected.

The production lesson:

> **"It returned successfully" does not prove "the query was memory-efficient."**

## Why fallback surprises matter

Suppose:

```text
Input = 120 GB
RAM   = 32 GB
```

You expect low memory usage because you asked for streaming.

But a state-heavy operator can create a plan region that causes the engine to use a different execution path or retain enough state that memory grows sharply.

You must measure rather than assume.

---

# 16. How to Detect Fallbacks or Unexpected Memory Use

Investigate in this order:

1. inspect the query plan
2. inspect the streaming physical plan where supported
3. enable relevant runtime diagnostics
4. profile the query where supported
5. measure process-level peak memory
6. compare the result with an intentionally simplified plan
7. review the current Polars documentation for the installed version

For example, current Polars documentation describes using the streaming engine explicitly in the physical graph:

```python
lf.show_graph(
    plan_stage="physical",
    engine="streaming",
)
```

Do not assume exact graph markers are identical across versions.

The safe approach is:

```text
plan
 ↓
observe
 ↓
measure
 ↓
change one thing
 ↓
re-measure
```

## Current diagnostic hint

Current Polars API documentation also notes that:

```bash
POLARS_VERBOSE=1
```

can provide information about engine fallback in relevant execution paths.

Treat this as a diagnostic aid, not as a substitute for measuring memory.

---

# 17. Streaming vs Global State

A useful mental split is:

## Stateless or nearly stateless processing

```text
batch
 ↓
process
 ↓
emit/release
```

Example:

```python
lf.filter(pl.col("amount") > 0)
```

The filter evaluates rows without needing a huge global table of prior rows.

## Stateful streaming

```text
Batch 1
   ↓
update retained state
   ↓
Batch 2
   ↓
update retained state
   ↓
Batch 3
   ↓
...
```

Examples:

- group-by aggregation
- joins
- deduplication
- some windows

So:

```text
bounded input batches
≠
bounded total state
```

This is one of the most important concepts in production streaming.

---

# 18. Group-By Memory Behaviour

Consider:

```python
result = (
    lf
    .group_by("customer_id")
    .agg(pl.col("amount").sum())
)
```

The input can arrive batch by batch.

But the engine may need to retain:

```text
customer_id
    →
running aggregate state
```

## Low-cardinality example

```text
10 billion rows
100 unique customers
```

The state might be conceptually similar to:

```text
100 groups
```

That can be far smaller than retaining all 10 billion rows.

## High-cardinality example

```text
10 billion rows
500 million unique customers
```

Now the group-state structure itself can become enormous.

### High-cardinality key

A high-cardinality key has a very large number of distinct values relative to the number of records.

Examples:

- `customer_id` in a small customer table may be moderate
- `event_id` is often nearly unique
- raw UUIDs across billions of events can create huge distinct-key state

Memory can grow because of:

- hash tables
- group keys
- aggregate buffers
- string storage
- validity metadata
- hash-table overhead

## Production question

When reviewing a huge group-by, ask:

> How many distinct groups can exist simultaneously?

That is often more informative than asking only:

> How many input rows are there?

---

# 19. How to Reduce Group-By State

Before a huge group-by:

### Filter early

```python
lf = lf.filter(pl.col("event_date") >= date_cutoff)
```

### Project early

```python
lf = lf.select(["customer_id", "amount"])
```

### Reduce cardinality only when semantically valid

If the business calculation genuinely needs daily customer totals, do not keep event-level granularity after it is no longer required.

### Pre-aggregate where safe

For example:

```text
event-level data
    ↓
daily customer totals
    ↓
much smaller data
```

### Partition work where semantics allow

You might process one month at a time if the required result is month-local.

But do not split a global calculation merely because partitions are convenient.

### Use appropriate data types

A narrow numeric representation can reduce memory relative to wider or unnecessarily expensive representations, but only when the chosen dtype preserves the required range and precision.

---

# 20. Join Memory Behaviour

A join is more complicated than a filter because matching values from one side often need to be remembered while processing the other side.

Conceptually, many join algorithms can be described using:

```text
build side
probe side
```

A simplified mental model:

```text
build side
   ↓
create lookup/match state
   ↓
probe side
   ↓
emit matches
```

Do not assume this is the exact internal implementation in every Polars query. Treat it as the conceptual state model.

## Small dimension + huge fact

Example:

```text
fact = 400 GB
dimension = 20 MB
```

This is often more manageable than two equally huge inputs because the retained lookup state may be comparatively small.

## Huge table + huge table

Example:

```text
left  = 300 GB
right = 250 GB
```

Now join state can become a major resource concern.

The engineering question is:

> Which side or structure must be retained, and how large can it become?

---

# 21. Large Build-Side Join Problem

Consider:

```text
trips        = 400 GB
zone_lookup  = 20 GB
RAM          = 32 GB
```

A 20 GB lookup table is much smaller than 400 GB but still potentially too large once decoded and expanded into join state.

Possible redesign actions:

- keep only required lookup columns
- deduplicate the lookup key
- filter lookup rows to the relevant time/domain
- pre-aggregate lookup data if semantically valid
- use partition-aware processing if the join semantics permit
- consider another architecture if retained state remains too large

Do not claim:

> "Streaming magically solves large joins."

It does not.

Streaming reduces whole-input materialization pressure. It does not eliminate the need to maintain state required by the join algorithm.

---

# 22. Pre-Aggregation Before Join

Compare these conceptual plans.

## Potentially expensive order

```text
Huge fact
   ↓
join
   ↓
group_by
```

versus:

```text
Huge fact
   ↓
filter
   ↓
pre-aggregate
   ↓
smaller dataset
   ↓
join
```

Suppose the downstream question is:

> total revenue per customer per day, enriched with customer segment

If the segment table is one row per customer, you may be able to do:

```text
raw events
   ↓
filter relevant events
   ↓
aggregate to customer-day
   ↓
join customer segment
```

instead of:

```text
raw events
   ↓
join segment
   ↓
aggregate
```

The first design can reduce join input.

## But correctness comes first

Pre-aggregation is safe only when the aggregation preserves everything required by downstream logic.

If the downstream join depends on event-level attributes, collapsing events first can change semantics.

The rule is:

```text
Optimize
   ↓
prove semantic equivalence
   ↓
measure
```

---

# 23. Global Sorts

Sorting is a classic memory-pressure source.

A filter can often behave like:

```text
read batch
 ↓
evaluate predicate
 ↓
emit matching rows
```

A global sort has a very different dependency:

```text
read large input
 ↓
learn ordering relationship across all rows
 ↓
produce globally ordered result
```

Potential resource costs include:

- memory pressure
- ordering state
- temporary working storage depending on execution engine
- additional comparisons
- output reorganization

A simple production warning:

```python
lf.sort("timestamp")
```

can be a radically different memory problem from:

```python
lf.filter(pl.col("timestamp") >= cutoff)
```

The latter can reduce data early. The former may require global coordination.

---

# 24. Window Functions

Window operations should be investigated by **what dependency the window introduces**.

Examples:

- `row_number` over a small partition
- ranking over a huge global ordering
- cumulative calculations within a partition
- large frame windows

Potential memory drivers:

```text
partition size
+
ordering requirements
+
frame width
+
retained state
```

A window operation may be manageable in one shape and expensive in another.

For example:

```text
small partition
+
already suitable ordering
```

may be very different from:

```text
one global partition
+
global ordering
+
large frame
```

Do not classify windows using one blanket rule.

---

# 25. Pivot Operations

Input:

```text
customer | month | revenue
A        | Jan   | 100
A        | Feb   | 120
A        | Mar   | 130
B        | Jan   |  90
```

Pivoted result:

```text
customer | Jan | Feb | Mar
A        | 100 | 120 | 130
B        |  90 | ... | ...
```

The output shape depends on the encountered category values.

That makes pivot more globally dependent than a row-wise projection.

A pivot may be a poor choice in a larger-than-memory pipeline when the pivot domain is large or unpredictable.

A production design often asks:

> Do I really need a wide pivot here, or would a long/tidy representation be easier to process and store?

The answer depends on downstream requirements.

---

# 26. Designing a Streaming-Friendly Pipeline

Use this framework:

```text
1. Filter early
2. Project early
3. Reduce data width
4. Reduce unnecessary rows
5. Pre-aggregate before expensive joins where valid
6. Avoid unnecessary global state
7. Partition work where semantics allow
8. Sink outputs incrementally
9. Measure peak memory
10. Validate correctness after redesign
```

These are design principles, not magic switches.

---

# 27. Filter Early

Suppose:

```text
100 GB input
```

but only the last month matters.

Conceptually:

```text
100 GB
  ↓ filter
10 GB relevant
  ↓
expensive transformations
```

Reducing rows early can reduce:

- CPU
- memory
- join state
- aggregation state
- I/O

This connects directly to predicate pushdown from Topic 03.

A useful question:

> Can I exclude irrelevant records before the first state-heavy operator?

---

# 28. Project Early

Suppose a table has:

```text
100 columns
```

but the pipeline needs:

```text
8 columns
```

Then:

```text
100 columns
    ↓
keep 8
    ↓
stream expensive computation
```

Reducing width lowers the amount of data carried through downstream operators.

Projection pushdown can go one step further by avoiding reading unused columns from storage when the source supports it.

---

# 29. Partition-Wise Processing

Suppose the source is partitioned:

```text
year=2024
year=2025
year=2026
```

If the business logic is partition-local, processing partitions independently can provide:

- bounded working sets
- easier retries
- operational isolation
- incremental processing
- easier backfills

However:

> **Partition-wise processing is not automatically equivalent to one global query.**

Examples where partition boundaries can change semantics:

- global rank
- global sort
- global deduplication
- cross-partition windows
- exact global distinct counts
- cross-partition joins

For example:

```text
Process each month independently
```

does not produce the same answer as:

```text
compute one global top-100 customers
```

unless you use a correct global merge strategy.

---

# 30. Partitioned Output

Partitioned output can create layouts such as:

```text
gold/
├── year=2025/
│   ├── month=01/
│   ├── month=02/
│   └── ...
└── year=2026/
    ├── month=01/
    └── ...
```

This is useful for:

- downstream partition pruning
- incremental processing
- operational isolation
- lake-style data layouts
- smaller files per logical partition

Current Polars APIs include a `PartitionBy` concept for sinks. A version-sensitive pattern is conceptually:

```python
import polars as pl

lf.sink_parquet(
    pl.PartitionBy("./gold/", key="month"),
    mkdir=True,
)
```

**Verify the exact `PartitionBy` signature and supported sink behavior against the installed Polars version before using this in production.**

Do not hard-code a training chapter around an API signature that may evolve.

---

# 31. Batch and Chunk Sizes

There is no universal "perfect streaming batch size".

### Too small

Potential downsides:

- more scheduling overhead
- more metadata handling
- lower throughput
- excessive function/operator invocation

### Too large

Potential downsides:

- larger memory spikes
- lower resource headroom
- less predictable memory use
- fewer opportunities for incremental output

### Balanced

The goal is:

```text
good throughput
+
acceptable memory
+
stable execution
```

## A crucial API distinction

Do not confuse:

```text
execution batch size
```

with:

```text
Parquet row_group_size
```

They are related to physical data movement but are not the same control.

Current Polars APIs also expose `collect_batches(chunk_size=...)` for receiving streaming result chunks. Current documentation marks this functionality as unstable and notes that it can be slower than native sinks. Therefore, use native sinks for production output whenever they fit the architecture rather than building a Python loop around `collect_batches()` merely to imitate a sink.

---

# 32. `POLARS_MAX_THREADS`

An environment-level control commonly used with Polars is:

```bash
POLARS_MAX_THREADS=4 python pipeline.py
```

Conceptually, this limits the number of threads Polars will use.

The important production lesson is:

```text
more threads
≠
always better
```

Higher concurrency can increase:

- simultaneous work
- memory pressure
- allocator activity
- intermediate buffers

In a memory-constrained container, using fewer threads can sometimes improve reliability even when single-run throughput falls.

Always verify the exact behavior against the installed Polars version and your environment.

---

# 33. CPU Parallelism vs Memory Pressure

Think about:

```text
more parallel work
      ↓
more simultaneous operators/buffers
      ↓
potentially higher memory pressure
```

Performance can be limited by different resources:

```text
CPU saturation
I/O saturation
memory saturation
```

If your workload is CPU-bound, more threads might help.

If your workload is already memory-bound:

```text
more threads
   ↓
more concurrent memory activity
   ↓
less headroom
   ↓
OOM risk
```

Production tuning is therefore about resource balance, not maximizing one setting.

---

# 34. Container Memory Limits

A pipeline can work on a desktop and fail inside:

- Docker
- Kubernetes
- CI
- serverless runtimes

because:

```text
Host RAM
    ≠
Container memory limit
```

Example:

```text
Host machine:
64 GB RAM

Container:
8 GB limit
```

A process that appears safe on the host can still be killed inside the container.

Memory-aware testing should therefore happen under realistic constraints.

You do not need a full Kubernetes course here. The important point is:

> Test against the resources the process actually receives.

---

# 35. How to Measure Peak Memory

On Linux, a useful process-level baseline is:

```bash
/usr/bin/time -v python pipeline.py
```

Look for:

- elapsed time
- maximum resident set size
- exit status

`Maximum resident set size` is a useful approximation of peak resident memory at the process level.

But remember:

```text
process RSS
≠
every allocator metric
≠
every library's internal memory accounting
```

Different tools answer different questions.

For example:

- `/usr/bin/time -v` asks about process-level resource usage.
- application-level profiling can expose operator-level runtime behavior.
- container telemetry can show cgroup-level limits/usage.

Use measurements that match the question you are trying to answer.

---

# 36. Benchmarking Larger-than-RAM Workloads

A useful benchmark should capture:

- dataset size
- row count
- schema
- wall time
- peak memory
- CPU/thread configuration
- output size
- correctness

Use multiple sizes:

```text
small
≈ RAM
> RAM
```

For this learning module, the streaming exercise explicitly requires a dataset at least:

```text
2–3× larger than available RAM
```

This does not prove a query is production-safe, but it creates the right pressure to observe the engineering trade-offs.

## Example benchmark matrix

Fill in actual measurements:

| Run | Data Size | Mode | Runtime | Peak RAM | Output Size | Correct? |
|---|---:|---|---:|---:|---:|---|
| A | ___ GB | eager | ___ | ___ | ___ | ___ |
| B | ___ GB | lazy + in-memory | ___ | ___ | ___ | ___ |
| C | ___ GB | lazy + streaming | ___ | ___ | ___ | ___ |
| D | ___ GB | streaming sink | ___ | ___ | ___ | ___ |

Do not pre-populate fake values.

---

# 37. Do Not Fake Benchmark Results

Never invent performance numbers.

Benchmark results depend on:

- CPU
- RAM
- storage device
- filesystem
- operating system
- data distribution
- compression
- Polars version
- thread count
- caching
- container limits
- concurrent workloads

Therefore:

> **Benchmark numbers are machine- and workload-dependent.**

Your chapter may contain executable benchmark code.

It must not pretend to know the output before the learner runs it.

---

# 38. Manual pandas Chunking vs Polars Streaming

Pandas manual chunking often looks like:

```python
import pandas as pd

for chunk in pd.read_csv(
    "large.csv",
    chunksize=100_000,
):
    # transform chunk
    ...
```

The developer manages:

- chunk boundaries
- retained state
- combining partial results
- error recovery logic
- output writing
- correctness of cross-chunk operations

Polars streaming moves more of that execution responsibility into the query engine.

Conceptually:

```text
pandas chunking
=
developer manages chunks/state

Polars streaming
=
query engine manages streaming execution
```

This does **not** mean Polars eliminates state-management concerns.

The engine still has to maintain group state, join state, ordering state, and other operator dependencies.

---

# 39. Chunk-Boundary Correctness

Consider:

```text
Chunk 1:
customer A → $100

Chunk 2:
customer A → $200
```

If you calculate a subtotal separately:

```text
chunk 1 → A = $100
chunk 2 → A = $200
```

you still need:

```text
A = $300
```

to obtain the global result.

This is the core reason streaming aggregation uses retained state.

A correct streaming aggregation is conceptually:

```text
Chunk 1
  ↓
state[A] = 100

Chunk 2
  ↓
state[A] = 100 + 200
```

An incorrect manual chunking implementation might accidentally return:

```text
A = 100
A = 200
```

instead of one global result.

## Cross-boundary examples

Be careful with:

- group-bys
- deduplication
- joins
- global ranks
- windows
- running totals
- top-k
- global sorts

Chunk boundaries should be invisible to the final result when the streaming algorithm is correct.

---

# 40. Pandas Chunking Comparison Experiment

Design an experiment that processes the same source data with:

### A. Pandas chunking

```python
for chunk in pd.read_csv(..., chunksize=...):
    ...
```

### B. Polars streaming

```python
lf = pl.scan_parquet("...")
result = lf.collect(engine="streaming")
```

Or use a sink for a large output.

Measure:

- runtime
- peak memory
- code size/complexity
- correctness
- state-management complexity
- number of explicit intermediate structures
- output behavior

Do not declare one approach universally superior.

The point is to learn the engineering trade-off.

---

# 41. GPU Execution — Awareness Only

Polars can expose a GPU execution option such as:

```python
lf.collect(engine="gpu")
```

This is an awareness topic in this chapter, not a GPU-programming chapter.

## Why GPU execution exists

A GPU has:

- very high parallel arithmetic throughput
- specialized memory hierarchy
- different resource constraints from system RAM

Some workloads can benefit greatly from GPU execution.

## GPU memory is not system RAM

Think:

```text
CPU process
   ↕
system RAM

GPU execution
   ↕
GPU memory
```

A dataset that does not fit in GPU memory is still a problem.

GPU execution does not automatically make arbitrary larger-than-RAM workloads solvable.

## Different constraint, different tool

CPU streaming is often about:

```text
reduce memory pressure
process incrementally
use system RAM + storage
```

GPU execution is often about:

```text
increase parallel compute throughput
use GPU acceleration
```

They can overlap, but they are not interchangeable objectives.

Do not learn CUDA programming here.

---

# 42. Distributed Polars — Awareness Only

Conceptually:

```text
single-node streaming
          vs
distributed execution
```

Distributed execution exists for workloads where:

- one machine is too small
- throughput requirements are too high
- parallelism across machines is valuable
- fault tolerance requirements demand more infrastructure
- operational scale exceeds a single-node design

But:

> Streaming extends what one machine can process. It does not make one machine infinitely scalable.

This chapter does not attempt to teach distributed systems in depth.

---

# 43. Single-Node Limit

A single-node streaming design eventually hits limits in:

- RAM
- local storage
- network bandwidth
- CPU
- retained operator state
- join cardinality
- local I/O throughput
- operational SLA
- reliability requirements
- recovery time

Do not use a universal rule such as:

```text
X TB = Spark
```

There is no exact threshold that applies to every workload.

Instead ask:

```text
Can one machine meet:

- memory requirements?
- throughput requirements?
- latency/SLA?
- storage requirements?
- reliability requirements?
- growth expectations?
```

---

# 44. Practical Architecture Decision

Use this decision framework:

```text
Can the workload fit comfortably in RAM?
        ↓
      Yes
        ↓
eager or lazy depending on requirements

        ↓ No

Can single-node streaming handle it?
        ↓
      Yes
        ↓
Polars streaming

        ↓ No
or retained state is too large
or SLA is too strict
        ↓
consider distributed/cloud-native architecture
```

Architecture choice depends on:

- input size
- operator state
- throughput
- latency
- reliability
- growth
- operational complexity
- cost

---

# 45. Required Hands-On Project — `streaming_aggregations.py`

> **Important file-safety note for this curriculum:** the named script is a learning exercise specification. This chapter does not create that script for you.

The project must use a dataset at least:

```text
2–3× larger than available RAM
```

For example, if your effective process memory limit is 16 GB, target roughly 32–48 GB of input data.

The exact byte size matters less than creating a meaningful larger-than-memory condition.

## Step 1 — Establish the machine baseline

Record:

- available RAM
- CPU cores
- storage type/capacity
- operating system
- container memory limit, if applicable
- Polars version
- thread configuration

Example commands:

```bash
free -h
nproc
df -h
python -c "import polars as pl; print(pl.__version__)"
```

Do not assume the host's RAM is the same as the process's effective memory limit inside a container.

## Step 2 — Baseline non-streaming execution

Where feasible:

```python
result = lf.collect()
```

Measure:

- elapsed time
- peak memory
- success/failure
- output size

If the workload clearly cannot fit, do not repeatedly crash a production system merely to "prove" it. Document the infeasible case and move to the streaming experiment.

## Step 3 — Streaming execution

Run:

```python
result = lf.collect(engine="streaming")
```

or the current equivalent documented by the installed version.

## Step 4 — Daily metrics

Compute:

- daily trip count
- daily revenue
- p95 fare per zone

Example conceptual aggregation:

```python
daily = (
    lf
    .group_by(["trip_date"])
    .agg(
        pl.len().alias("trip_count"),
        pl.col("fare").sum().alias("daily_revenue"),
    )
)
```

For p95 by zone/date, use the current supported Polars aggregation API for your installed version and verify the resulting semantics.

## Step 5 — Peak-memory measurement

Run the workload under:

```bash
/usr/bin/time -v python streaming_aggregations.py
```

Record maximum resident set size.

## Step 6 — Whole-dataset deduplication

Use a composite key such as:

```text
(trip_id, trip_version)
```

or another business-appropriate key.

Explain why global deduplication can require meaningful retained state.

## Step 7 — Compare with pandas chunking

Implement an equivalent chunked pandas approach.

Compare:

- correctness
- peak memory
- runtime
- code complexity
- state handling

## Step 8 — Lookup join

Join trips to a zone lookup dataset.

Explain why:

```text
small lookup
```

and:

```text
large lookup
```

can have very different memory behavior.

## Step 9 — Partitioned Parquet output

Write partitioned Parquet by month where the installed Polars version supports the required `PartitionBy` sink behavior.

Use the current documented API rather than relying on an old signature.

## Step 10 — Intentionally add a non-streaming-friendly operation

Choose one:

- global sort
- pivot
- selected window operation

Do not assume it must fail.

Observe:

- runtime
- peak memory
- success/failure
- plan behavior where inspectable

## Step 11 — Redesign

Restructure the plan to reduce retained state.

Examples:

```text
global sort
```

might become:

```text
sort only within a required partition
```

if the business problem truly permits partition-local ordering.

Or:

```text
join raw events
```

might become:

```text
aggregate events first
join smaller aggregate
```

if semantically valid.

Measure again.

## Step 12 — Record memory versus data size

Use a real measurement table:

| Run | Dataset Size | Mode | Rows | Runtime | Peak Memory | Correct? |
|---|---:|---|---:|---:|---:|---|
| 1 | ___ | eager | ___ | ___ | ___ | ___ |
| 2 | ___ | streaming | ___ | ___ | ___ | ___ |
| 3 | ___ | redesigned streaming | ___ | ___ | ___ | ___ |

The values must come from your environment.

---

# 46. Required Streamability Classification Lab

Classify at least 15 operations into:

```text
A. Generally streaming-friendly

B. Potentially state-heavy

C. Often requires full input or significant global state

D. Version/query dependent — verify experimentally
```

Classify at least these:

1. scan
2. filter
3. select
4. with_columns
5. aggregation
6. join
7. global sort
8. window
9. pivot
10. explode
11. deduplication
12. ranking
13. rolling
14. top-k
15. global distinct

## Example worksheet

| Operation | Initial Classification | Why? | Experiment Needed? |
|---|---|---|---|
| scan | ___ | ___ | ___ |
| filter | ___ | ___ | ___ |
| select | ___ | ___ | ___ |
| with_columns | ___ | ___ | ___ |
| aggregation | ___ | ___ | ___ |
| join | ___ | ___ | ___ |
| global sort | ___ | ___ | ___ |
| window | ___ | ___ | ___ |
| pivot | ___ | ___ | ___ |
| explode | ___ | ___ | ___ |
| deduplication | ___ | ___ | ___ |
| ranking | ___ | ___ | ___ |
| rolling | ___ | ___ | ___ |
| top-k | ___ | ___ | ___ |
| global distinct | ___ | ___ | ___ |

Verify your classification using:

- plans
- execution
- memory measurements
- current documentation

Do not replace investigation with memorization.

---

# 47. Required Memory Investigation Lab

Run five experiments.

## Experiment A — Low-cardinality group-by

Example:

```text
10 billion rows
100 groups
```

Record:

- rows
- unique keys
- peak memory
- runtime
- success/failure
- observations

## Experiment B — High-cardinality group-by

Example:

```text
10 billion rows
many millions of unique groups
```

Record the same values.

## Experiment C — Small lookup join

Use a small dimension table.

## Experiment D — Large join

Use a deliberately larger lookup/build-side candidate.

## Experiment E — Global sort

Sort on a high-entropy column.

## Investigation table

| Experiment | Rows | Unique Keys | Peak Memory | Runtime | Success? | Observation |
|---|---:|---:|---:|---:|---|---|
| Low-cardinality group-by | ___ | ___ | ___ | ___ | ___ | ___ |
| High-cardinality group-by | ___ | ___ | ___ | ___ | ___ | ___ |
| Small lookup join | ___ | ___ | ___ | ___ | ___ | ___ |
| Large join | ___ | ___ | ___ | ___ | ___ | ___ |
| Global sort | ___ | ___ | ___ | ___ | ___ | ___ |

Then answer:

> **Why did memory change?**

The answer should discuss retained operator state, not only "because the data was bigger".

---

# 48. Required Streaming Redesign Lab

Start with this intentionally poor conceptual pipeline:

```text
Large dataset
   ↓
read everything
   ↓
keep unnecessary columns
   ↓
global sort
   ↓
join huge tables
   ↓
group
   ↓
collect full result
```

Redesign toward:

```text
scan
 ↓
filter early
 ↓
project early
 ↓
pre-aggregate where valid
 ↓
careful join
 ↓
streaming execution
 ↓
sink
```

Your redesign review must answer:

1. What rows did you remove earlier?
2. What columns did you remove earlier?
3. What state-heavy operation did you move or eliminate?
4. Did the join input become smaller?
5. Did output materialization become smaller?
6. Did semantics remain identical?
7. What did measurement show?

---

# 49. Required Debugging Scenarios

## Problem 1 — Dataset is 3× RAM and normal `collect()` crashes

### Symptom

```text
process exits or reaches OOM
```

### Root cause

The query asks the in-memory engine to materialize too much working data.

### Diagnosis

- measure peak RAM
- inspect whether the input is being eagerly materialized
- inspect the plan
- compare with streaming

### Corrected design

Use a lazy scan and explicit streaming execution where supported:

```python
lf.collect(engine="streaming")
```

or a sink for a huge output.

### Production lesson

Do not begin a larger-than-memory pipeline with eager full-table loading unless you have proven sufficient headroom.

---

## Problem 2 — Streaming still uses too much memory

### Symptom

`engine="streaming"` still approaches or exceeds the memory limit.

### Root cause

Streaming does not remove operator state.

Likely contributors:

- high-cardinality group-by
- large join state
- sorting
- wide rows
- large output
- high thread concurrency

### Diagnosis

Measure peak memory, inspect the plan, and isolate state-heavy operators.

### Corrected design

Reduce rows/columns early and redesign the state-heavy portion.

### Production lesson

Streaming changes execution granularity; it does not make all algorithms memory-free.

---

## Problem 3 — High-cardinality group-by causes memory growth

### Symptom

Memory steadily rises while input is processed.

### Root cause

Aggregation state grows with the number of distinct keys.

### Diagnosis

Compare unique key counts across test datasets.

### Corrected design

- filter early
- reduce width
- pre-aggregate valid subsets
- partition if semantics permit
- reconsider whether the grouping key is unnecessarily granular

### Production lesson

For stateful operators, cardinality can matter more than raw row count.

---

## Problem 4 — Large join causes memory pressure

### Symptom

Memory spikes around the join.

### Root cause

Join state becomes large.

### Diagnosis

Measure left/right sizes after filtering and projection. Determine which side acts as retained lookup/build state conceptually, without assuming one exact internal implementation.

### Corrected design

- reduce lookup columns
- deduplicate lookup keys
- filter both sides early
- pre-aggregate where valid
- use partition-aware architecture if appropriate

### Production lesson

"Small relative to the fact table" is not the same as "small relative to RAM".

---

## Problem 5 — Global sort causes memory spike

### Symptom

Sort stage dominates memory or runtime.

### Root cause

Global ordering introduces cross-batch dependency.

### Diagnosis

Compare:

```text
filter-only
```

against:

```text
filter + global sort
```

### Corrected design

Ask whether global ordering is really required. If only partition-local order is needed, scope the operation accordingly.

### Production lesson

Question the semantic requirement before optimizing implementation details.

---

## Problem 6 — Pipeline appears lazy but is not efficient in streaming mode

### Symptom

Code contains a `LazyFrame`, but resource usage is unexpectedly high.

### Root cause

Possibilities include:

- later eager conversion
- state-heavy operator
- query fallback
- collecting a huge result
- inefficient source design

### Diagnosis

Inspect the complete plan and runtime, not just the presence of `LazyFrame`.

### Corrected design

Preserve laziness to the boundary and use an appropriate streaming sink.

### Production lesson

"Has a LazyFrame" is not a performance guarantee.

---

## Problem 7 — Sink still creates resource pressure

### Symptom

`sink_parquet` still consumes substantial memory.

### Root cause

The query itself may contain large operator state.

### Diagnosis

Profile/measure the query before and after the sink, and isolate expensive operators.

### Corrected design

Reduce working set and operator state before sinking.

### Production lesson

The sink solves output materialization pressure, not arbitrary operator-state growth.

---

## Problem 8 — Works locally but fails inside Docker

### Symptom

Developer machine succeeds; container gets killed.

### Root cause

Container memory limit is much lower than host RAM.

### Diagnosis

Inspect the actual container memory limit and peak process memory.

### Corrected design

Tune threads, reduce working set, and test under realistic limits.

### Production lesson

Resource limits are part of the runtime environment, not an afterthought.

---

## Problem 9 — Increasing thread count makes memory worse

### Symptom

More threads improve throughput but produce OOM failures.

### Root cause

Higher concurrency creates more simultaneous work and memory pressure.

### Diagnosis

Benchmark with multiple controlled thread counts.

### Corrected design

Select a stable thread level that meets the SLA without exhausting memory headroom.

### Production lesson

A throughput-only benchmark can produce an unreliable production configuration.

---

## Problem 10 — Partition-wise processing changes the result

### Symptom

Per-partition processing returns a different answer than the global query.

### Root cause

The computation required cross-partition state.

### Diagnosis

Identify the global dependency:

- ranking
- global sort
- global dedup
- cross-partition window
- global distinct
- cross-partition join

### Corrected design

Use a correct global merge/state strategy or retain a global execution stage.

### Production lesson

Partitioning is an execution optimization only when it preserves semantics.

---

# 50. Common Mistakes

Avoid these errors:

1. calling `collect()` without streaming on huge inputs
2. collecting a huge output into Python instead of sinking
3. performing global sorts casually on data far larger than RAM
4. assuming lazy automatically means streaming
5. assuming streaming guarantees constant memory
6. ignoring aggregation state
7. ignoring join retained state
8. using too many threads
9. ignoring container limits
10. treating disk size as memory footprint
11. splitting a global operation incorrectly by partition
12. failing to validate correctness after redesign
13. trusting benchmarks without measuring peak memory
14. confusing output row-group size with streaming execution chunk size
15. relying on undocumented or obsolete streaming parameters
16. assuming every `window` or `join` behaves identically across query shapes
17. assuming one successful run proves the architecture is safe under growth

---

# 51. Production Engineering Patterns

A realistic pattern is:

```text
Object Storage
      ↓
Partitioned Parquet
      ↓
scan_parquet()
      ↓
LazyFrame
      ↓
Early filter
      ↓
Early projection
      ↓
Validation
      ↓
Deduplication / aggregation
      ↓
Careful joins
      ↓
Streaming execution
      ↓
sink_parquet()
      ↓
Partitioned Gold Dataset
```

Annotate the memory implications:

```text
Filter
→ reduces rows

Projection
→ reduces width

Aggregation
→ retains group state

Join
→ retains join state

Sort
→ can require global state

Sink
→ avoids full output materialization
```

This is one of the most useful production mental models in this chapter.

---

# 52. Streaming Capacity Planning

Before production, ask:

- How large is the dataset?
- How large are decompressed columns?
- What is the expected output size?
- What is the highest-cardinality group-by?
- How large is the join retained/build-side state?
- Is there a global sort?
- Are there window operations?
- Is there a pivot?
- How much memory is actually available to the process?
- Is the workload containerized?
- How much headroom is required?
- What is the SLA?
- What happens if input doubles?

Production capacity planning should be based on observed workload characteristics, not only file size.

---

# 53. Performance Investigation Workflow

Use:

```text
Measure baseline
      ↓
Inspect plan
      ↓
Identify state-heavy operators
      ↓
Reduce input early
      ↓
Reduce width early
      ↓
Reduce retained state
      ↓
Tune resources
      ↓
Run again
      ↓
Validate correctness
```

The senior-engineering principle is:

> **Optimize based on evidence, not intuition alone.**

---

# 54. Explain-Aloud Exercises

Do not answer these using memorized definitions.

## Exercise A

Explain why 40 GB of Parquet does not necessarily require exactly 40 GB of RAM.

Your answer should mention:

- compression
- decoded columns
- intermediates
- state
- output
- runtime overhead

## Exercise B

Explain lazy execution versus streaming execution.

A strong answer should say:

```text
Lazy = defer/build/optimize
Streaming = execute incrementally
```

## Exercise C

Explain why a high-cardinality group-by can consume significant memory.

## Exercise D

Explain why a huge join can break a streaming design.

## Exercise E

Explain why a global sort is harder to stream.

## Exercise F

Explain why collecting a huge final result defeats some benefits of streaming.

## Exercise G

Explain why more threads can increase memory pressure.

## Exercise H

Explain why partition-wise processing can change global semantics.

## Exercise I

Explain when one machine is no longer sufficient.

---

# 55. Senior Data Engineer Interview Questions

## 55.1 Beginner

### Q1. What is streaming execution?

**Answer:**  
Streaming execution processes a compatible query incrementally in batches or morsels rather than requiring the entire input to be materialized as one in-memory object. It reduces whole-input memory pressure but does not eliminate all operator state.

### Q2. Why can a dataset larger than RAM be difficult to process?

**Answer:**  
Because full materialization requires memory for decoded data plus intermediates, retained state, buffers, and output. Disk size alone is not a reliable estimate of peak execution memory.

### Q3. What is a morsel or batch?

**Answer:**  
It is a manageable unit of input work processed by the execution engine. The exact internal unit and scheduling model depend on the engine implementation.

### Q4. What does `collect(engine="streaming")` do?

**Answer:**  
It triggers lazy-query execution using Polars' streaming engine, which processes compatible query regions in batches to reduce memory pressure and support larger-than-memory workloads.

### Q5. What is a streaming sink?

**Answer:**  
A sink is an output operation that evaluates a lazy query in a streaming-oriented way and writes results incrementally to storage, avoiding the need to materialize the entire output as one `DataFrame`.

---

## 55.2 Intermediate

### Q6. How is streaming different from lazy execution?

**Answer:**  
Lazy execution controls **when and how the query plan is constructed and optimized**. Streaming controls **how execution consumes and produces data**. A lazy query may be executed in-memory or with streaming.

### Q7. Which operators generally stream well?

**Answer:**  
Scans, filters, projections, many expressions, many aggregations, and many joins are often suitable for streaming. Exact behavior is query- and version-dependent.

### Q8. Why can group-by consume large memory?

**Answer:**  
Because the engine can process input incrementally but may need to retain one aggregation state per distinct group. High cardinality can therefore create large hash-table/state memory.

### Q9. Why can joins consume large memory?

**Answer:**  
A join commonly needs lookup/matching state. If the retained side is large after decoding, projection, and filtering, that state can exceed available memory.

### Q10. Why are global sorts difficult?

**Answer:**  
A global sort requires cross-batch knowledge about ordering. Independently sorting batches does not automatically produce one globally ordered output.

### Q11. What is a streaming fallback?

**Answer:**  
It is a situation where a requested streaming execution encounters a query region that cannot be executed through the streaming path as intended, so another execution path may be used. The exact fallback behavior is version-dependent and should be verified.

### Q12. How would you detect unexpected memory usage?

**Answer:**  
Inspect the plan, inspect the streaming physical graph where supported, use runtime diagnostics, profile where supported, measure peak process memory, and isolate state-heavy operations.

---

## 55.3 Advanced

### Q13. How would you design a pipeline for a dataset 3× larger than RAM?

**Answer:**  
Start lazy from storage, reduce rows and columns early, avoid unnecessary global operations, keep state-heavy operators under control, use streaming execution, and sink large outputs. Then benchmark peak memory and runtime under the actual resource limit.

### Q14. How would you diagnose a streaming query that still exceeds memory limits?

**Answer:**  
Determine whether the pressure comes from row/column volume, aggregation cardinality, join state, global ordering, output materialization, concurrency, or container limits. Use plan/profiling/OS measurements and change one architectural factor at a time.

### Q15. How would you reduce aggregation state without changing semantics?

**Answer:**  
Filter irrelevant data early, project only required keys/values, reduce granularity only when the business result permits it, pre-aggregate semantically safe subsets, partition only when global semantics are preserved, and select appropriate dtypes.

### Q16. How would you reason about the build side of a large join?

**Answer:**  
Estimate the retained lookup state after applying filters and projections, not just the raw file size. Check distinct key counts, row width, duplicates, and whether the join relationship can be validated or reduced.

### Q17. When is partition-wise processing safe?

**Answer:**  
When the requested result is partition-local or can be correctly combined from partition-local results. It is unsafe when the calculation requires global ordering, global ranking, global deduplication, cross-partition windows, or another global dependency without a correct merge step.

### Q18. How would you benchmark Polars streaming against pandas chunking fairly?

**Answer:**  
Use the same dataset, same business logic, same hardware, same storage, same environment, comparable output, controlled concurrency, and actual peak-memory measurements. Validate exact result equivalence.

### Q19. How does CPU parallelism affect memory behavior?

**Answer:**  
Higher concurrency can improve throughput but also increase simultaneous working memory. In a memory-bound workload, fewer threads can sometimes improve stability.

### Q20. How would you operate a streaming pipeline inside a memory-constrained container?

**Answer:**  
Measure against the real cgroup/container limit, preserve streaming, reduce working set early, control thread count, avoid collecting huge results, monitor peak RSS, and retain safety headroom for runtime overhead.

### Q21. When would you stop optimizing single-node Polars and consider distributed processing?

**Answer:**  
When a correctly designed single-node pipeline cannot meet memory, throughput, latency, reliability, storage, or operational requirements, especially when retained state itself is too large for one machine.

### Q22. How would you defend that architectural decision in a design review?

**Answer:**  
Present measured data: input size, row count, schema, peak memory, runtime, thread settings, bottleneck operator, growth forecast, SLA, and the cost/complexity of the proposed alternative. The decision should be based on observed constraints rather than technology preference.

---

# 56. Architecture Scenarios

## Scenario 1 — 100 GB Parquet on a 32 GB machine

### Problem

The source is roughly 100 GB.

### Resource bottleneck

Potentially RAM during decoding and operator state.

### Likely solution

Lazy scan + early projection/filter + streaming execution + sink if the output is large.

### Trade-offs

More careful pipeline design; some operations can still retain large state.

### Measurement required

Peak RAM, runtime, input bytes/files touched, correctness.

### Architectural boundary

If state or SLA remains beyond the machine, consider another architecture.

---

## Scenario 2 — High-cardinality aggregation

### Problem

A group-by creates millions or hundreds of millions of distinct keys.

### Resource bottleneck

Aggregation hash/state memory.

### Likely solution

Reduce input early, lower granularity only when semantically valid, pre-aggregate, or partition safely.

### Trade-offs

Possible additional stages and more complex correctness validation.

### Measurement

Distinct-key count and peak memory.

### Boundary

State larger than available headroom may require redesign or distributed execution.

---

## Scenario 3 — 50 GB dimension joined to 500 GB fact

### Problem

The lookup side is not truly small relative to machine memory.

### Resource bottleneck

Join retained/build state.

### Likely solution

Project/filter/deduplicate the dimension; pre-aggregate fact if valid; partition if semantics permit.

### Trade-offs

Possible additional I/O and semantic constraints.

### Measurement

Post-filter dimension size and peak join memory.

### Boundary

If retained state remains too large, another architecture may be required.

---

## Scenario 4 — Fast but exceeds Kubernetes memory limit

### Problem

The host benchmark is fast, but the pod is killed.

### Resource bottleneck

Container memory limit.

### Likely solution

Test under actual memory limits, reduce working set, tune threads.

### Trade-offs

Potentially slower execution.

### Measurement

Peak RSS versus container limit.

### Boundary

Sustained operation needs both throughput and memory safety.

---

## Scenario 5 — More threads improve speed but cause OOM

### Problem

Increasing thread count reduces runtime.

### Resource bottleneck

Memory concurrency.

### Likely solution

Find the lowest thread count that meets SLA with stable memory.

### Trade-offs

Some throughput is sacrificed.

### Measurement

runtime + peak memory per thread setting.

### Boundary

Choose configuration from the Pareto trade-off, not maximum raw speed.

---

## Scenario 6 — Partition-wise redesign changes result

### Problem

Processing monthly partitions separately changes a global result.

### Resource bottleneck

Algorithm requires global state.

### Likely solution

Keep the global stage or implement a correct merge.

### Trade-offs

Less partition locality.

### Measurement

Schema, row count, aggregates, exact values.

### Boundary

Do not force partition locality where semantics require global coordination.

---

## Scenario 7 — Sort dominates memory

### Problem

Global sort causes a sharp memory increase.

### Resource bottleneck

Ordering state.

### Likely solution

Question whether global sorting is necessary; limit order scope if semantically valid.

### Trade-offs

Downstream consumers may need a different contract.

### Measurement

Before/after plan and peak memory.

### Boundary

If global order is non-negotiable, plan for its resource cost.

---

## Scenario 8 — Final result is 30 GB and pipeline calls `collect()`

### Problem

The input streams well but the final result is huge.

### Resource bottleneck

Output materialization.

### Likely solution

Sink to Parquet instead.

### Trade-offs

Downstream consumer must read persisted output.

### Measurement

Peak memory with collect versus sink.

### Boundary

If downstream requires one in-memory object, streaming cannot remove that final memory requirement.

---

## Scenario 9 — Workload doubles every six months

### Problem

Today is safe but growth is rapid.

### Resource bottleneck

Future CPU, storage, and state.

### Likely solution

Benchmark scaling behavior and define capacity thresholds.

### Trade-offs

May require earlier architectural investment.

### Measurement

Runs at multiple dataset sizes.

### Boundary

Establish an explicit migration trigger.

---

## Scenario 10 — Single-node streaming misses SLA

### Problem

Memory is stable but runtime is too slow.

### Resource bottleneck

CPU, I/O, network, or state-heavy operator.

### Likely solution

Profile first; optimize the dominant bottleneck; then evaluate distributed or cloud-native processing if the single node remains insufficient.

### Trade-offs

Higher operational complexity.

### Measurement

Wall time, CPU, I/O, peak memory, operator runtime.

### Boundary

When a correct single-node design cannot meet SLA, changing architecture can be more appropriate than endless micro-tuning.

---

# 57. Benchmarking Requirements

Every performance experiment must:

- use executable code
- measure actual results
- document environment
- document dataset size
- document row count
- document schema
- document Polars version
- document CPU/RAM
- document thread settings
- measure runtime
- measure peak memory
- preserve correctness

Never fabricate benchmark values.

Use this record:

```text
Environment:
OS:
CPU:
RAM:
Container limit:
Polars version:
Threads:

Dataset:
Path/layout:
Format:
Rows:
Logical size:
Approx. disk size:

Pipeline:
Business logic:
Engine:
Output sink:

Measurements:
Runtime:
Peak memory:
Output size:
Correctness checks:
```

The benchmark must keep:

```text
same dataset
+
same business logic
+
same file format
+
same hardware
+
same environment
```

Then measure:

```text
runtime
peak memory
correctness
```

For file-based workloads also consider:

```text
bytes read
files touched
output size
```

---

# 58. Version Awareness

Polars evolves quickly.

Where APIs are version-sensitive:

1. check the installed version when execution is available
2. prefer current stable documented APIs
3. clearly identify version-sensitive behavior
4. never invent parameters
5. do not confidently present obsolete syntax as current

Pay particular attention to:

- streaming engine arguments
- sink APIs
- partitioned sink behavior
- streaming diagnostics
- thread controls
- GPU execution syntax
- distributed APIs
- query plan formatting
- profiling interfaces

## Current API notes used in this chapter

As checked against the current official Polars documentation available during preparation:

- `LazyFrame.collect(..., engine="streaming")` is supported.
- lazy scans such as `scan_parquet`, `scan_csv`, and `scan_ipc` are supported.
- `sink_parquet`, `sink_csv`, `sink_ipc`, and `sink_ndjson` are documented as streaming-oriented sinks.
- `LazyFrame.collect_batches(...)` exists, but is documented as unstable and slower than native sinks.
- `PartitionBy` is documented for partitioned sink output.
- current documentation describes streaming physical-plan visualization via `show_graph(..., plan_stage="physical", engine="streaming")`.
- current documentation notes that unsupported GPU queries can fall back to another engine in relevant contexts.
- engine default resolution has changed across Polars major versions, so explicit engine selection is preferable in reproducible training material.

Always confirm these APIs against the exact version installed in your environment.

---

# 59. Technical Accuracy Requirements

Be precise about:

- file size vs memory footprint
- lazy vs streaming
- batch/morsel execution
- bounded working memory vs constant memory
- streaming-compatible operators
- operator state
- fallback execution
- aggregation state
- join state
- conceptual build-side reasoning
- global sorting
- window state
- pivot behavior
- partition-wise semantics
- sinks
- batch/chunk sizing
- thread counts
- container memory
- benchmarking methodology
- CPU vs GPU constraints
- single-node vs distributed processing

Avoid statements such as:

> "Streaming means the entire pipeline always uses constant memory."

Use this instead:

> **Streaming can reduce peak memory by processing data incrementally, but operators may still retain substantial state.**

The correct engineering question is:

```text
What is the largest working set or retained state
created by this specific plan?
```

---

# 60. Important Correctness Rule

Performance optimization must never silently change business semantics.

Use this sequence:

```text
Optimize
   ↓
Run
   ↓
Compare output
   ↓
Validate
```

At minimum compare:

- schema
- row counts
- aggregates
- values
- sort order where ordering is part of the contract
- sorted output before comparison when output order is unspecified

For floating-point metrics, define appropriate tolerances rather than requiring bit-for-bit equality when numerical representation can differ legitimately.

Memory optimization without correctness validation is dangerous in production data engineering.

---

# 61. Important Mental Model — Working Set

Remember:

```text
Total dataset size
        ≠
Working-set size
```

Example:

```text
100 GB input
   ↓ filter
8 GB relevant rows
   ↓ projection
3 GB needed columns
   ↓ aggregation
retained state
   ↓
manageable working set
```

Actual process memory is still:

```text
working data
+
operator state
+
runtime overhead
+
buffers
+
output activity
```

The goal of a streaming-friendly design is often to keep the active working set manageable.

---

# 62. Required Capstone Exercise with a 2–3× RAM Dataset

This is your final practical assignment for the topic.

## Requirements

1. Check available RAM.
2. Create or find a dataset at least 2–3× RAM.
3. Build an eager baseline where feasible.
4. Build a lazy pipeline.
5. Run a streaming version.
6. Measure peak memory.
7. Add one memory-heavy operation deliberately.
8. Observe the impact.
9. Redesign the pipeline.
10. Compare results.
11. Sink the final result to Parquet.
12. Write a short engineering conclusion.

Use this table:

| Run | Data Size | Mode | Runtime | Peak RAM | Result Correct? |
|---|---:|---|---:|---:|---|
| 1 | ___ | eager | ___ | ___ | ___ |
| 2 | ___ | lazy/in-memory | ___ | ___ | ___ |
| 3 | ___ | streaming | ___ | ___ | ___ |
| 4 | ___ | redesigned streaming | ___ | ___ | ___ |

The values must be generated by your environment.

Do not pre-populate fake benchmark values.

## Final engineering conclusion

Write 5–10 sentences covering:

- what became the memory bottleneck
- which operator caused it
- how filtering/projection affected the working set
- how streaming changed execution behavior
- how correctness was validated
- whether one machine was sufficient
- what would trigger an architectural change

---

# 63. Master Checklist

Use this as your completion checklist.

- [ ] I understand why datasets larger than RAM are difficult.
- [ ] I understand file size vs memory footprint.
- [ ] I understand in-memory vs out-of-core processing.
- [ ] I understand streaming execution.
- [ ] I understand batches/morsels.
- [ ] I understand bounded working memory.
- [ ] I understand lazy vs streaming.
- [ ] I can use streaming execution.
- [ ] I understand streaming sinks.
- [ ] I can use `sink_parquet`.
- [ ] I understand `sink_csv`.
- [ ] I understand `sink_ipc`.
- [ ] I understand `sink_ndjson`.
- [ ] I know which operations generally stream well.
- [ ] I know which operations may require substantial state.
- [ ] I understand streaming fallbacks.
- [ ] I can investigate unexpected memory growth.
- [ ] I understand aggregation-state memory.
- [ ] I understand high-cardinality group-bys.
- [ ] I understand join-state memory.
- [ ] I understand build-side considerations.
- [ ] I understand why global sorts are difficult.
- [ ] I understand why some window operations are memory-heavy.
- [ ] I understand pivot limitations.
- [ ] I can design a streaming-friendly pipeline.
- [ ] I understand filter early.
- [ ] I understand project early.
- [ ] I understand pre-aggregation.
- [ ] I understand partition-wise processing.
- [ ] I understand partitioned output.
- [ ] I understand batch-size trade-offs.
- [ ] I understand `POLARS_MAX_THREADS`.
- [ ] I understand CPU parallelism vs memory pressure.
- [ ] I understand container memory limits.
- [ ] I can measure peak memory.
- [ ] I can benchmark fairly.
- [ ] I understand pandas chunking.
- [ ] I understand chunk-boundary correctness.
- [ ] I understand GPU execution at awareness level.
- [ ] I understand distributed Polars at awareness level.
- [ ] I can reason about single-node limits.
- [ ] I completed the `streaming_aggregations.py` exercise.
- [ ] I completed the streamability classification lab.
- [ ] I completed the memory investigation lab.
- [ ] I completed the streaming redesign lab.
- [ ] I completed the 2–3× RAM capstone.
- [ ] I can explain streaming architecture aloud.

---

# 64. Final Mastery Assessment

## Part A — Fundamentals (15 questions)

### 1.
Why is a 20 GB Parquet file not necessarily a 20 GB RAM workload?

### 2.
Define out-of-core processing.

### 3.
Define streaming execution.

### 4.
What is a batch/morsel?

### 5.
Why is bounded working memory not the same as constant memory?

### 6.
What is a `LazyFrame`?

### 7.
Why is lazy execution different from streaming execution?

### 8.
What does `collect(engine="streaming")` ask Polars to do?

### 9.
Why might a sink be preferable to collecting a huge output?

### 10.
What is aggregation state?

### 11.
What is join retained/build-side state conceptually?

### 12.
Why is a global sort difficult for simple batch-wise streaming?

### 13.
Why can a high-cardinality group-by be expensive?

### 14.
What is a streaming fallback?

### 15.
What is the single-node limit?

---

## Part B — Memory Reasoning (15 questions)

### 1.
RAM = 16 GB. Input = 40 GB. What should you investigate before deciding whether the workload is possible?

### 2.
Why can decompressed columns exceed compressed Parquet size?

### 3.
Why can a 100 GB input produce a smaller working set than 100 GB?

### 4.
How can projection reduce memory pressure?

### 5.
How can filtering reduce join memory?

### 6.
Why does aggregation memory depend on distinct keys?

### 7.
Why can 500 million groups be more dangerous than 10 billion rows with 100 groups?

### 8.
Why can a "20 GB lookup table" still be too large for a 16 GB process?

### 9.
Why can increasing thread count increase memory pressure?

### 10.
Why can collecting a 30 GB result defeat streaming benefits?

### 11.
Why can global ordering create cross-batch dependency?

### 12.
Why can partitioning change semantics?

### 13.
Why should container limits be used in capacity planning?

### 14.
Why is peak memory more useful than file size for resource planning?

### 15.
What does "working set" mean in the context of this chapter?

---

## Part C — Streaming vs Non-Streaming Classification (15 scenarios)

For each scenario classify it as:

```text
A = generally streaming-friendly
B = potentially state-heavy
C = often requires full input/significant global state
D = verify experimentally
```

### 1.
Scan Parquet and select four numeric columns.

### 2.
Filter by date.

### 3.
Compute a local arithmetic expression.

### 4.
Group 10 billion rows into 100 groups.

### 5.
Group 10 billion rows by a nearly unique event ID.

### 6.
Join a 5 GB fact slice with a 10 MB lookup.

### 7.
Join two 300 GB datasets.

### 8.
Globally sort one billion rows.

### 9.
Pivot a table with thousands of dynamic categories.

### 10.
Window function over very large ordered partitions.

### 11.
Explode a list column.

### 12.
Deduplicate globally on a nearly unique key.

### 13.
Rank every row globally by revenue.

### 14.
Compute a bounded local transformation after early filtering.

### 15.
Use a newly introduced operation whose streaming support is unclear.

---

## Part D — Coding (15 tasks)

### Task 1
Write a lazy Parquet scan.

### Task 2
Add an early filter.

### Task 3
Add early projection.

### Task 4
Collect using explicit streaming execution.

### Task 5
Write the result with `sink_parquet`.

### Task 6
Write a sink using CSV.

### Task 7
Write a sink using Arrow IPC.

### Task 8
Write a sink using NDJSON.

### Task 9
Build a daily aggregation.

### Task 10
Build a small lookup join.

### Task 11
Measure a pipeline with `/usr/bin/time -v`.

### Task 12
Run a controlled benchmark at multiple thread counts.

### Task 13
Create a deliberately high-cardinality group-by experiment.

### Task 14
Create a deliberately global-sort experiment.

### Task 15
Build a redesign that filters and projects before a join and then sinks the output.

---

## Part E — Debugging (10 broken pipeline scenarios)

### 1.
The query calls `read_parquet()` on a 200 GB dataset.

### 2.
The query uses `LazyFrame` but ends in `.collect()` on a 50 GB result.

### 3.
Streaming is enabled but memory still grows rapidly.

### 4.
The group-by has hundreds of millions of distinct keys.

### 5.
The join lookup table is 25 GB and RAM is 16 GB.

### 6.
The pipeline globally sorts before grouping.

### 7.
A partition-wise rewrite changes totals.

### 8.
The host succeeds but Docker fails.

### 9.
More threads improve throughput and produce OOM failures.

### 10.
A developer assumes one benchmark result applies to every machine.

---

## Part F — Performance Investigation (10 scenarios)

### 1.
Runtime is high but memory is low.

What does that suggest you investigate?

### 2.
Runtime is low but memory is dangerously high.

What resource trade-off is occurring?

### 3.
Projection from 100 columns to 8 does not reduce memory.

What should you verify?

### 4.
Filtering is present but source I/O remains high.

What should you inspect in the plan?

### 5.
A sink still has high peak memory.

Which operator classes should you investigate?

### 6.
A group-by's memory grows with unique key count.

What state structure is likely growing conceptually?

### 7.
A join spikes memory only after schema changes.

Why might row width or key representation matter?

### 8.
The benchmark is faster after warm-up.

What confounding factor should you control?

### 9.
Two benchmark machines show different peak RAM.

Why is that not evidence of a tool defect by itself?

### 10.
A streaming query finishes successfully but uses almost all container memory.

Is success enough? Explain what you would change in production.

---

## Part G — Production Architecture (10 senior-level scenarios)

### 1.
Design a pipeline for 100 GB input on a 32 GB machine.

### 2.
Design a pipeline for 1 TB input on a 64 GB machine with a high-cardinality global group-by.

### 3.
Design a 400 GB fact + 20 GB lookup join.

### 4.
Design a 500 GB event pipeline whose output is 200 GB.

### 5.
Design a workload running under an 8 GB container limit.

### 6.
Design a pipeline where input doubles every six months.

### 7.
Design a pipeline where global ordering is required.

### 8.
Design a pipeline where monthly partitioned output is desirable.

### 9.
Design a pipeline that must support exact global deduplication.

### 10.
Explain when you would move from single-node streaming to a distributed architecture.

---

# 65. Final Answer Key

## Part A — Fundamentals Answer Key

### 1. 20 GB Parquet vs 20 GB RAM

Parquet is compressed and columnar. Decoding, intermediates, state, buffers, and output can make peak memory substantially different from file size.

### 2. Out-of-core processing

Processing a workload without requiring the entire dataset to reside in RAM at once.

### 3. Streaming

Incremental execution of a compatible query using batches/morsels rather than treating the entire input as one in-memory object.

### 4. Batch/morsel

A manageable unit of work passed through the execution pipeline.

### 5. Bounded vs constant memory

Streaming can keep the input working set bounded, but retained state for joins, groups, windows, sorts, and other operators can still grow.

### 6. LazyFrame

A deferred query plan representing work to be executed later.

### 7. Lazy vs streaming

Lazy describes deferred planning/execution; streaming describes incremental execution.

### 8. `collect(engine="streaming")`

Execute the lazy query using the streaming engine.

### 9. Why sinks matter

They avoid materializing a huge final output into one `DataFrame`.

### 10. Aggregation state

Retained information required to combine rows belonging to the same group across batches.

### 11. Join state

Information retained to match records between the two input sides; conceptually this can involve build/probe state.

### 12. Global sort

Global ordering requires cross-batch knowledge; independently sorted batches are not automatically globally ordered.

### 13. High-cardinality group-by

More distinct keys can mean more retained aggregation/hash state.

### 14. Streaming fallback

A plan region may not be streamable through the requested path and may use another execution path or retain substantial state.

### 15. Single-node limit

The point where one machine cannot meet memory, CPU, storage, throughput, latency, reliability, or SLA requirements.

---

## Part B — Memory Reasoning Answer Key

### 1.
Investigate decoded size, required columns, row count, state-heavy operators, output size, threads, and effective process memory.

### 2.
Parquet stores compressed/encoded representations; execution may decode them into larger in-memory structures.

### 3.
Early filtering/projection can reduce active rows and columns before expensive operators.

### 4.
Projection reduces carried column width and can reduce bytes read when pushdown applies.

### 5.
Filtering before a join reduces the number of rows entering join state.

### 6.
Each distinct group can require retained key and aggregate state.

### 7.
A few groups require small state; hundreds of millions of groups can require enormous hash/state memory.

### 8.
The 20 GB lookup can decode to more than 20 GB and must coexist with process overhead and other state.

### 9.
More threads can increase concurrent work and buffers.

### 10.
The final 30 GB result still requires substantial RAM if collected as one `DataFrame`.

### 11.
A decision about global order depends on records across the whole input.

### 12.
A partition-local calculation may not account for values in other partitions.

### 13.
Because the container can have much less memory than the host.

### 14.
Peak working memory determines OOM risk.

### 15.
The data and state actively required by the query at a given time.

---

## Part C — Classification Answer Key

These are initial engineering classifications, not immutable rules.

| # | Operation | Suggested Classification | Reason |
|---:|---|---|---|
| 1 | Scan + select | A | Natural fit for incremental columnar reading |
| 2 | Filter | A | Often local/stream-friendly |
| 3 | Arithmetic expression | A | Usually row/column local |
| 4 | Group 10B → 100 | B | State exists but cardinality is low |
| 5 | Group 10B → near-unique | B/C | State can approach input cardinality |
| 6 | Small lookup join | A/B | Often manageable, but still stateful |
| 7 | Huge + huge join | B/C | Retained join state can be large |
| 8 | Global sort | C | Strong global ordering dependency |
| 9 | Large dynamic pivot | C/D | Output shape/global category knowledge matters |
| 10 | Large ordered window | B/C/D | Depends on partition/order/frame |
| 11 | Explode | D | Output expansion can dominate; verify workload |
| 12 | Global dedup | B/C | Requires retained global key state |
| 13 | Global rank | B/C | Global ordering/ranking dependency |
| 14 | Local transformation after filter | A | Usually low state |
| 15 | Unknown new operation | D | Must verify current support |

The purpose is to reason, measure, and verify rather than memorize labels.

---

## Part D — Coding Answer Key

### 1. Lazy Parquet scan

```python
import polars as pl

lf = pl.scan_parquet("silver/events/*.parquet")
```

### 2. Early filter

```python
lf = lf.filter(
    pl.col("event_date") >= pl.date(2026, 1, 1)
)
```

### 3. Early projection

```python
lf = lf.select(
    ["event_date", "customer_id", "amount"]
)
```

### 4. Streaming collect

```python
result = lf.collect(engine="streaming")
```

### 5. Parquet sink

```python
lf.sink_parquet("gold/events.parquet")
```

### 6. CSV sink

```python
lf.sink_csv("gold/events.csv")
```

### 7. IPC sink

```python
lf.sink_ipc("gold/events.arrow")
```

### 8. NDJSON sink

```python
lf.sink_ndjson("gold/events.ndjson")
```

### 9. Daily aggregation

```python
daily = (
    lf
    .group_by("event_date")
    .agg(
        pl.len().alias("event_count"),
        pl.col("amount").sum().alias("total_amount"),
    )
)
```

### 10. Small lookup join

```python
lookup = pl.scan_parquet("reference/zones.parquet")

joined = lf.join(
    lookup,
    on="zone_id",
    how="left",
)
```

### 11. Peak memory measurement

```bash
/usr/bin/time -v python pipeline.py
```

### 12. Thread benchmark

Use identical input and business logic, changing only the controlled thread setting:

```bash
POLARS_MAX_THREADS=2 /usr/bin/time -v python pipeline.py
POLARS_MAX_THREADS=4 /usr/bin/time -v python pipeline.py
POLARS_MAX_THREADS=8 /usr/bin/time -v python pipeline.py
```

### 13. High-cardinality experiment

Group by a nearly unique key and compare memory against a low-cardinality key.

### 14. Global sort experiment

Compare:

```python
lf.collect(engine="streaming")
```

with:

```python
lf.sort("event_time").collect(engine="streaming")
```

Then measure peak memory and runtime.

### 15. Redesign before join and sink

```python
import polars as pl

lf = (
    pl.scan_parquet("silver/events/*.parquet")
    .filter(pl.col("event_date") >= pl.date(2026, 1, 1))
    .select(["event_date", "customer_id", "zone_id", "amount"])
)

daily = (
    lf
    .group_by(["event_date", "customer_id", "zone_id"])
    .agg(pl.col("amount").sum().alias("daily_amount"))
)

zone = pl.scan_parquet("reference/zones.parquet").select(
    ["zone_id", "zone_name"]
)

final = daily.join(zone, on="zone_id", how="left")

final.sink_parquet("gold/daily_customer_zone.parquet")
```

The semantic equivalence of this redesign must be validated for the actual business problem.

---

## Part E — Debugging Answer Key

### 1. Eager `read_parquet()`

Use lazy scanning and streaming where compatible.

### 2. Huge final `.collect()`

Replace the final materialization with a sink where downstream requirements allow.

### 3. Streaming still uses too much memory

Find state-heavy operators and measure them.

### 4. Huge group cardinality

Reduce cardinality only when semantically valid, or change the aggregation architecture.

### 5. 25 GB lookup on 16 GB RAM

Reduce and filter the lookup before joining; consider architecture changes if retained state remains too large.

### 6. Global sort before grouping

Question whether the sort is necessary. If order is not part of the business requirement, remove it. If local ordering is enough, narrow the sort scope.

### 7. Partition-wise result changes

Restore the global state requirement or introduce a correct global merge.

### 8. Docker failure

Measure against the container limit.

### 9. More threads cause OOM

Reduce thread concurrency and benchmark the memory/throughput trade-off.

### 10. One benchmark result everywhere

Benchmark results are environment-specific; record hardware, software, dataset, storage, thread count, and correctness.

---

## Part F — Performance Investigation Answer Key

### 1.
Investigate CPU, I/O, expressions, sorting, and slow plan nodes.

### 2.
The query is memory-bound or concurrency-heavy.

### 3.
Check whether projection pushdown is actually reaching the scan and whether another operator dominates memory.

### 4.
Inspect the plan for predicate pushdown and check file/row-group pruning behavior.

### 5.
Investigate group-by, join, sort, window, pivot, dedup, and output materialization.

### 6.
A group-state structure keyed by distinct values is likely growing.

### 7.
Wider rows/keys mean more bytes per retained state entry.

### 8.
Control cache warmth and repeat runs under comparable conditions.

### 9.
Different hardware, storage, versions, data distributions, allocators, and thread settings all affect results.

### 10.
No. A successful run that consumes almost all memory has poor headroom and may fail on slightly larger inputs or ordinary runtime variation.

---

## Part G — Production Architecture Answer Key

### 1. 100 GB on 32 GB

Use lazy Parquet scans, aggressive early filtering/projection, streaming, carefully sized stateful operations, and sink output. Measure peak memory under the 32 GB process limit.

### 2. 1 TB with high-cardinality global group-by

Streaming alone may not be sufficient because retained group state can dominate memory. Evaluate pre-aggregation, partition-local aggregation plus a merge, or a distributed architecture.

### 3. 400 GB fact + 20 GB lookup

Filter/projection on both sides, deduplicate lookup keys, aggregate fact data before the join if valid, and measure retained join state.

### 4. 500 GB input → 200 GB output

Use sink-based output to avoid collecting 200 GB into RAM.

### 5. 8 GB container

Design for the actual 8 GB limit, not host RAM. Limit threads, reduce working set, and leave operational headroom.

### 6. Input doubling every six months

Benchmark at several sizes and define a capacity threshold and migration plan.

### 7. Global ordering required

Accept the cost of the global dependency or use an algorithm designed for global ordering; do not fake a local sort as a global sort.

### 8. Monthly partitioned output

Use a supported partitioned sink design and ensure the partition key matches downstream access patterns.

### 9. Exact global deduplication

Do not split partitions naïvely. You need a correct global key strategy or a partitioning scheme that guarantees each key is localized.

### 10. When to distribute

When one machine cannot satisfy the required memory, throughput, latency, reliability, or growth constraints after correct single-node optimization.

---

# 66. Final "Teach It Back" Exercise

You should now explain the entire topic in your own words.

Do not read the answer key while doing this.

Explain:

1. why normal in-memory execution can fail
2. what out-of-core processing means
3. what streaming does
4. how lazy execution fits into streaming
5. what batches/morsels are
6. why streaming does not mean constant memory
7. why some operators retain state
8. how group-by state grows
9. how join state grows
10. why global sorting is difficult
11. why windows can be state-heavy
12. why pivot can be globally dependent
13. how early filtering reduces work
14. how early projection reduces width
15. why pre-aggregation can reduce downstream state
16. why partition-wise processing can change semantics
17. why sinks matter
18. how to measure peak memory
19. how pandas chunking differs from engine-managed streaming
20. when a single machine stops being sufficient

## Teach-back test

Give yourself this prompt:

> "I have a 100 GB Parquet dataset and 16 GB of available process memory. Explain how I would design and operate a Polars pipeline that computes daily metrics and writes the result safely."

A strong answer should naturally include:

```text
lazy scan
+
early filtering
+
early projection
+
streaming execution
+
state-aware aggregation
+
careful joins
+
sink-based output
+
peak-memory measurement
+
correctness validation
+
growth/capacity planning
```

If you can explain why each item belongs there, you understand the core of this chapter.

---

# 67. Key Mental Models to Remember

## Mental Model 1 — Lazy vs Streaming

```text
Lazy
=
defer + plan + optimize

Streaming
=
execute incrementally
```

---

## Mental Model 2 — File Size vs Memory

```text
disk size
≠
decoded memory
≠
peak execution memory
```

---

## Mental Model 3 — Working Set

```text
100 GB input
does not mean
100 GB working set
```

---

## Mental Model 4 — State

```text
batch size can stay bounded
while operator state grows
```

---

## Mental Model 5 — Optimize Before Execution

```text
filter early
project early
reduce state
then stream
```

---

## Mental Model 6 — Output

```text
streaming + collect
=
final result still needs RAM

streaming + sink
=
large result can remain on storage
```

---

## Mental Model 7 — Correctness

```text
performance optimization
        ↓
semantic equivalence
        ↓
measurement
```

---

## Mental Model 8 — Architecture

```text
single-node streaming
      ↓
extends scale
      ↓
does not remove fundamental limits
```

---

# 68. Production Review Checklist

Before approving a larger-than-memory Polars pipeline, ask:

### Data

- What is the compressed file size?
- What is the approximate decoded size?
- How many rows?
- What is the row width?
- Which partitions will be touched?

### Plan

- Are filters pushed down?
- Are unnecessary columns eliminated early?
- Is there a global sort?
- Is there a pivot?
- Are there large windows?
- Is there a high-cardinality group-by?
- How large is the join state?

### Execution

- Is the query lazy until the execution boundary?
- Is streaming explicitly selected where appropriate?
- Is there any accidental eager materialization?
- Is the output being collected unnecessarily?

### Resources

- How much memory does the process actually have?
- How many threads are used?
- What is the container limit?
- Is there enough headroom?

### Correctness

- Did a redesign change the result?
- Were schemas compared?
- Were counts compared?
- Were aggregates compared?
- Were values compared?
- Was output ordering handled correctly?

### Operations

- Can the pipeline retry partitions?
- Is output idempotent?
- Can downstream systems read the partition layout?
- What happens when data grows 2×?

---

# 69. Transition to Topic 05

You now have the conceptual bridge between:

```text
Polars Lazy API
```

and:

```text
larger-than-memory execution
```

You should understand:

```text
Lazy
  ↓
optimized plan
  ↓
streaming execution
  ↓
bounded input working set
  ↓
operator state
  ↓
sink
```

The next topic can build on this foundation by examining additional production-oriented query execution behavior and performance patterns.

The most important lesson to carry forward is:

> **Streaming is not a magic "large-data mode". It is an execution strategy that works best when the query itself is designed to minimize unnecessary data movement and retained global state.**

---

# Appendix A — Minimal Reference Examples

## A. Basic streaming collect

```python
import polars as pl

lf = (
    pl.scan_parquet("data/events/*.parquet")
    .filter(pl.col("status") == "ok")
    .select(["event_date", "customer_id", "amount"])
)

df = lf.collect(engine="streaming")
```

## B. Streaming sink

```python
import polars as pl

(
    pl.scan_parquet("data/events/*.parquet")
    .filter(pl.col("status") == "ok")
    .select(["event_date", "customer_id", "amount"])
    .sink_parquet("gold/events.parquet")
)
```

## C. Linux peak-memory baseline

```bash
/usr/bin/time -v python pipeline.py
```

## D. Controlled thread test

```bash
POLARS_MAX_THREADS=4 /usr/bin/time -v python pipeline.py
```

Remember to run the same workload under controlled conditions.

---

# Appendix B — Benchmark Template

Copy this template into your study notes manually when conducting the experiment.

```text
Experiment name:
Date:
Polars version:
Python version:
OS:
CPU:
RAM:
Container limit:
Storage:
Filesystem:
POLARS_MAX_THREADS:

Dataset path:
Dataset format:
Partitions:
Rows:
Columns:
Schema:
Input disk size:

Business logic:

Execution mode:
collect(engine="streaming") / sink / other:

Plan notes:
- predicate pushdown:
- projection pushdown:
- partition pruning:
- state-heavy operators:

Runtime:
Peak RSS:
Output size:
Files touched:
Observations:

Correctness:
- schema equal:
- row count equal:
- aggregate totals equal:
- key values equal:
- order requirement handled:

Conclusion:
```

---

# Appendix C — Benchmark Rules

Before comparing two pipelines, confirm:

```text
same dataset
      +
same query semantics
      +
same output contract
      +
same hardware
      +
same storage
      +
same environment
      +
same thread configuration
      +
same correctness standard
```

Then compare:

```text
runtime
peak memory
output size
bytes read
files touched
```

A benchmark without controlled conditions is an observation, not a reliable engineering comparison.

---

# Appendix D — Final One-Page Summary

```text
LARGER THAN RAM
      ↓
Full eager materialization may fail
      ↓
Use lazy scans
      ↓
Optimize the query
      ↓
Filter early
      ↓
Project early
      ↓
Reduce data width/rows
      ↓
Control aggregation/join/sort state
      ↓
Execute compatible regions in streaming mode
      ↓
Avoid collecting huge outputs
      ↓
Sink large results directly to storage
      ↓
Measure peak memory + runtime
      ↓
Validate correctness
      ↓
If one machine still cannot meet requirements
      ↓
Consider another architecture
```

And keep this exact distinction:

```text
Lazy execution
=
defer + plan + optimize

Streaming execution
=
incremental execution in batches/morsels
```

Therefore:

```text
Lazy ≠ automatically streaming
```

And finally:

```text
Same result
≠
Same amount of work
```

A production data engineer learns to ask:

> **What work is the engine really doing, what state is it retaining, how much memory can that state consume, and can I change the query shape without changing the business meaning?**
