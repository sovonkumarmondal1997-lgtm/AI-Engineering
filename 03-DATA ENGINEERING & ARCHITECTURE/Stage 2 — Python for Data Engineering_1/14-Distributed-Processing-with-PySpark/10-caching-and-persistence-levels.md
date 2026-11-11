# Caching and Persistence Levels

> **Module:** 2.14 — Distributed Processing with PySpark  
> **Phase:** C — Moving Data Across the Cluster  
> **Topic:** 10 — Caching and Persistence Levels  
> **Target environment:** Modern Apache Spark 4.x / PySpark 4.x  
> **Prerequisites:** Topics 01–09

---

## 1. Learning Objectives

By the end of this topic, you should be able to:

- explain what caching means in Spark;
- explain why caching exists;
- connect caching to lazy evaluation and lineage;
- explain why an uncached DataFrame can be recomputed;
- explain what `cache()` does;
- explain what `persist()` does;
- explain why `cache()` is lazy;
- explain when cached data is materialized;
- explain first-action versus later-action behavior;
- use `unpersist()` appropriately;
- explain what happens when cached blocks are evicted;
- explain Spark `StorageLevel`;
- compare memory, disk, serialization, and replication choices;
- explain the modern default DataFrame persistence behavior accurately;
- choose among `MEMORY_ONLY`, `MEMORY_AND_DISK`, `DISK_ONLY`, and relevant variants;
- reason about cache size, partition count, and partition size;
- decide when caching is useful;
- decide when caching is wasteful;
- explain caching before and after filtering;
- explain caching around expensive joins and shuffles;
- explain caching across multiple branches;
- explain caching in iterative workloads;
- investigate cached data with the Spark UI Storage tab;
- use the Executors tab to investigate memory pressure;
- explain eviction and recomputation;
- distinguish caching from checkpointing;
- distinguish `checkpoint()` from `localCheckpoint()`;
- distinguish caching from durable Parquet materialization;
- distinguish persistence from a Python variable or temporary view;
- measure whether persistence actually improved a workload;
- make a production caching decision from evidence rather than habit.

The target skill is not:

```python
df.cache()
```

The target skill is answering:

> **Should this DataFrame be persisted, at what level, for how long, and why?**

---

## 2. Why Caching Exists

Spark transformations are lazy.

Suppose you build an expensive DataFrame:

```python
from pyspark.sql import functions as F

silver = (
    orders
    .join(customers, on="customer_id", how="left")
    .filter(F.col("status") == "completed")
    .groupBy("customer_id")
    .agg(
        F.sum("amount").alias("revenue")
    )
)
```

At this point Spark has a description of a computation.

It has not necessarily processed all the input.

Now imagine:

```python
silver.count()

silver.write.mode("overwrite").parquet("/tmp/revenue")

silver.groupBy("customer_id").count().show()
```

These are separate actions.

Without persistence, Spark may need to execute the upstream lineage again for later actions.

Conceptually:

```text
WITHOUT CACHE

Action 1
   ↓
compute lineage
   ↓
result

Action 2
   ↓
compute lineage again
   ↓
result

Action 3
   ↓
compute lineage again
   ↓
result
```

With persistence:

```text
WITH CACHE

First action
   ↓
compute lineage
   ↓
materialize cached partitions
   ↓
result

Later actions
   ↓
reuse persisted partitions where applicable
   ↓
result
```

Caching therefore addresses a **reuse problem**.

It does not mean:

- every computation becomes faster;
- every shuffle disappears;
- skew disappears;
- data becomes permanently stored;
- the entire dataset is guaranteed to remain in memory.

---

## 3. The Problem: Repeated Computation

Imagine preparing a complicated meal.

If three people need the same prepared ingredients, repeatedly preparing those ingredients from scratch wastes work.

Spark has a similar problem.

Suppose:

```text
raw data
   ↓
filter
   ↓
join
   ↓
large aggregation
   ↓
expensive_df
```

If three downstream outputs all reuse `expensive_df`, recomputing the entire upstream lineage can be wasteful.

The engineering question becomes:

```text
Cost of recomputation
        VS
Cost of storing the result
```

Caching is useful when the storage cost and persistence overhead are justified by the computation saved.

---

## 4. Caching and Lazy Evaluation

This topic directly builds on Topic 04.

### Without persistence

```python
df = expensive_transformation(...)
```

This constructs a lazy DataFrame.

Then:

```python
df.count()
```

triggers execution.

Later:

```python
df.write.parquet(path)
```

may require Spark to execute the upstream computation again if the result was not persisted.

### With persistence

```python
df = expensive_transformation(...)

df.cache()
```

Calling `cache()` does **not** mean:

```text
RUN NOW
```

Instead it means conceptually:

```text
MARK THIS DATAFRAME FOR PERSISTENCE
```

The cached blocks are populated when an action causes the DataFrame to be computed.

```python
df.cache()

# No full computation merely because cache() was called.

df.count()
# First action:
# compute -> materialize partitions -> return result
```

Then:

```python
df.groupBy("customer_id").count().show()
```

can reuse persisted partitions where the execution plan allows it.

### Mental model

```text
Transformation
      ↓
cache()
      ↓
persistence requested
      ↓
still lazy
      ↓
action
      ↓
compute partitions
      ↓
store persisted blocks
      ↓
reuse later
```

---

## 5. `cache()`

The convenient API is:

```python
df.cache()
```

For a DataFrame, this requests persistence using the DataFrame's default persistence level.

Important properties:

- it is lazy;
- it does not immediately execute the DataFrame;
- the first action can still be expensive;
- computed partitions can be retained for later reuse;
- persisted data is not a durable table;
- persisted blocks can be lost or evicted;
- Spark can recompute missing partitions from lineage.

Example:

```python
transformed = (
    orders
    .filter(F.col("status") == "completed")
    .groupBy("customer_id")
    .agg(
        F.sum("amount").alias("revenue")
    )
)

transformed.cache()

# Materializes the cache.
transformed.count()

# Can reuse persisted partitions.
transformed.orderBy(F.desc("revenue")).show(20)
```

### What happens?

```text
cache()
  ↓
mark DataFrame for persistence

first action
  ↓
execute lineage
  ↓
persist computed partitions
  ↓
return action result

later action
  ↓
read persisted partitions where available
```

### What `cache()` does not mean

It does not mean:

```text
permanent storage
```

It does not mean:

```text
all data stays in RAM forever
```

It does not mean:

```text
no future computation is possible
```

It does not mean:

```text
the source data has been modified
```

---

## 6. `persist()`

`persist()` provides explicit control over the storage level.

```python
from pyspark import StorageLevel

df.persist(StorageLevel.MEMORY_AND_DISK)
```

Then materialize:

```python
df.count()
```

And eventually release:

```python
df.unpersist()
```

### Why `persist()` exists

Different workloads have different constraints.

For example:

```text
Dataset fits comfortably in executor memory
        ↓
MEMORY_ONLY may be reasonable
```

or:

```text
Dataset may not fit in memory
        ↓
MEMORY_AND_DISK may be more appropriate
```

or:

```text
Memory is highly constrained
        ↓
DISK_ONLY may be considered
```

### Core comparison

| Operation | Purpose | Storage choice | Execution timing |
|---|---|---|---|
| `cache()` | Convenient persistence | DataFrame default | Lazy |
| `persist(level)` | Controlled persistence | Explicit `StorageLevel` | Lazy |
| `unpersist()` | Release persisted blocks | N/A | Explicit cleanup |

A production engineer chooses the persistence strategy based on workload evidence.

---

## 7. `cache()` vs `persist()`

The key distinction is:

```text
cache()
→ convenient default persistence

persist(level)
→ explicit persistence strategy
```

Example:

```python
df.cache()
```

versus:

```python
df.persist(StorageLevel.DISK_ONLY)
```

Both are lazy.

Both are intended to allow reuse.

The difference is that `persist()` lets you choose the storage behavior.

### Important DataFrame default

For modern Spark DataFrames, the documented default persistence level for `DataFrame.cache()` / default DataFrame persistence is **`MEMORY_AND_DISK_DESER`**.

This is an important version-awareness point.

Older tutorials may state different defaults, especially when discussing older RDD APIs.

Do not transfer an old Spark tutorial's RDD persistence default directly to modern DataFrames.

---

## 8. `StorageLevel`

A `StorageLevel` describes how Spark should retain persisted data.

Think about four dimensions:

```text
1. MEMORY
2. DISK
3. SERIALIZATION
4. REPLICATION
```

### Memory

Can cached blocks be kept in executor memory?

### Disk

Can cached blocks be stored on disk?

### Serialization

Should the persisted representation use a serialized form?

Serialization can reduce storage footprint in some contexts, but introduces encoding/decoding work.

### Replication

Should persisted blocks have additional copies?

Replication can improve resilience or availability of cached blocks, but increases storage and network cost.

---

## 9. Storage Levels in Detail

### 9.1 `MEMORY_ONLY`

Conceptually:

```text
Keep persisted data in memory.
If a partition cannot be kept at the requested level,
Spark can recompute it from lineage when needed.
```

Example:

```python
from pyspark import StorageLevel

df.persist(StorageLevel.MEMORY_ONLY)
df.count()
```

Useful when:

- the persisted dataset fits comfortably;
- reuse is high;
- fast access matters;
- recomputation is acceptable for blocks that are not retained.

Trade-off:

- can consume substantial executor storage;
- partitions that cannot be retained at this level may need recomputation.

---

### 9.2 `MEMORY_AND_DISK`

Conceptually:

```text
Keep persisted blocks in memory when possible.
Use disk when memory is insufficient.
```

Example:

```python
df.persist(StorageLevel.MEMORY_AND_DISK)
df.count()
```

Useful when:

- the dataset may exceed available memory;
- recomputation is expensive;
- disk fallback is preferable to losing the persisted block.

Trade-off:

- disk access is slower than memory;
- storage resources are consumed;
- the first materialization still performs the original computation.

---

### 9.3 `DISK_ONLY`

Conceptually:

```text
Persist data on disk rather than consuming executor memory
for the persisted representation.
```

Example:

```python
df.persist(StorageLevel.DISK_ONLY)
df.count()
```

Useful when:

- memory is constrained;
- recomputation is expensive;
- reuse justifies persistence;
- disk capacity is available.

Trade-off:

- reads from disk are generally slower than memory;
- disk space is consumed;
- the first action still computes the data.

---

### 9.4 Replicated Variants

Examples include:

```python
StorageLevel.MEMORY_ONLY_2
StorageLevel.MEMORY_AND_DISK_2
StorageLevel.DISK_ONLY_2
```

The `_2` concept means persisted blocks are replicated.

Conceptually:

```text
Block A
  ├── copy 1
  └── copy 2
```

Potential benefit:

- another copy may remain available if one executor is lost.

Costs:

- additional storage;
- additional network transfer;
- additional operational overhead.

Replication is not automatically worth the cost.

---

### 9.5 Serialized Variants

Serialization changes the representation used for persistence.

The important engineering trade-off is:

```text
smaller / different storage representation
        VS
encoding / decoding overhead
```

Do not assume:

```text
serialized = always better
```

or:

```text
deserialized = always better
```

The correct choice depends on:

- data representation;
- memory pressure;
- CPU overhead;
- access pattern;
- Spark version;
- API being used.

For Python users, remember that PySpark has additional language/runtime boundaries compared with JVM-only Spark applications.

---

### 9.6 Modern DataFrame Default

For modern DataFrames, use the documented default:

```text
MEMORY_AND_DISK_DESER
```

when explaining `DataFrame.cache()` behavior in current Spark.

Do not confuse this with:

```text
RDD.cache()
```

which has different historical/default semantics.

The important production lesson is:

> **Always reason from the API and Spark version you are actually running, not from a copied tutorial written for an older release.**

---

## 10. Storage-Level Decision Table

| Situation | Possible choice | Reasoning |
|---|---|---|
| Data comfortably fits in memory and is heavily reused | `MEMORY_ONLY` | Fast reuse can justify memory |
| Data may exceed memory and recomputation is expensive | `MEMORY_AND_DISK` | Allows disk fallback |
| Memory is constrained but reuse still matters | `DISK_ONLY` | Avoids retaining the persisted representation in memory |
| Additional persisted redundancy is justified | Replicated level | More copies can improve availability |
| Default DataFrame caching is appropriate | `cache()` | Uses the modern DataFrame default |
| Uncertain whether persistence helps | Benchmark first | Avoid premature optimization |

There is no universally best storage level.

---

## 11. Cache Materialization

Consider:

```python
df = spark.read.parquet("/data/orders")

cached = (
    df.filter(F.col("status") == "completed")
      .select("customer_id", "amount")
)

cached.cache()

print("Cache requested")

cached.count()

print("First action completed")
```

The sequence is:

```text
cached.cache()
      ↓
persistence requested
      ↓
no immediate full computation

cached.count()
      ↓
Spark executes the required lineage
      ↓
partitions are materialized
      ↓
persisted blocks become available
      ↓
count result returned
```

The first action may therefore be approximately as expensive as the uncached computation, plus persistence overhead.

The benefit appears when the result is reused.

```python
cached.count()

cached.groupBy("customer_id").count().show()

cached.groupBy("customer_id").sum("amount").show()
```

The later operations can consume the persisted representation instead of rebuilding the entire upstream lineage.

---

## 12. First Action vs Later Actions

This is a critical benchmark concept.

### First action

```text
read source
  ↓
transform
  ↓
shuffle if required
  ↓
compute
  ↓
persist blocks
  ↓
return action result
```

### Later action

```text
read persisted blocks
  ↓
perform only downstream work required
  ↓
return result
```

Therefore, a benchmark such as:

```python
df.cache()

start = time.perf_counter()
df.count()
first = time.perf_counter() - start

start = time.perf_counter()
df.count()
second = time.perf_counter() - start
```

does not compare two identical situations.

The first action includes materialization.

The second may reuse the persisted data.

Always document whether your measurement is:

- cold;
- first-action;
- warm;
- repeated-action.

---

## 13. Caching and Partitions

Spark caches **computed partitions**, not one giant DataFrame object sitting in a single memory area.

Conceptually:

```text
DataFrame
   |
   +---- Partition 0 → persisted block
   +---- Partition 1 → persisted block
   +---- Partition 2 → persisted block
   +---- Partition 3 → persisted block
```

A useful diagnostic:

```python
print(df.rdd.getNumPartitions())
```

This converts through the RDD interface for inspection. It is useful diagnostically, but normal DataFrame processing does not require converting the DataFrame to an RDD.

### Why partitioning matters

If a dataset has:

```text
many large partitions
```

the persisted representation can require substantial storage.

If it has:

```text
many tiny partitions
```

there may be unnecessary task and block-management overhead.

Topic 08 covers partitioning deeply.

Here the key connection is:

> **Caching stores partition-level results, so partition size and partition distribution influence caching behavior.**

---

## 14. Caching and Repartitioning

Consider:

```python
df = df.repartition(200, "customer_id")
df.cache()
```

The order matters.

The `repartition()` itself is a lazy transformation.

The first action may need to perform the shuffle and then materialize the resulting partitions.

Conceptually:

```text
source
  ↓
shuffle / repartition
  ↓
partitioned DataFrame
  ↓
cache
  ↓
first action
  ↓
persist resulting partitions
```

If the repartitioned result is reused several times, persisting that boundary can sometimes be useful.

But do not add a repartition only because you plan to cache.

Ask:

```text
Does the downstream workload actually benefit from this partitioning?
```

---

## 15. When to Cache

A strong caching candidate often has all or most of these properties:

```text
expensive to compute
        +
reused multiple times
        +
reasonable storage cost
        +
sufficient resources
        +
reuse occurs within the application
```

### Scenario A — Multiple actions

```python
silver.cache()

silver.count()
silver.groupBy("country").count().show()
silver.orderBy(F.desc("revenue")).show()
```

### Scenario B — Multiple branches

```python
silver = expensive_join(...)

silver.cache()

gold_sales = silver.filter(F.col("type") == "sale")
gold_returns = silver.filter(F.col("type") == "return")
gold_customers = silver.select("customer_id").distinct()
```

Without persistence, the expensive upstream work may be repeated for multiple branches.

### Scenario C — Expensive join

```text
large input
   ↓
expensive join
   ↓
reused result
```

If the result is reused substantially, persistence can be useful.

### Scenario D — Iterative processing

An iterative algorithm may reuse intermediate state repeatedly.

Caching can reduce repeated lineage execution.

However, careless caching inside a loop can create memory pressure.

---

## 16. When NOT to Cache

Avoid caching by default.

Common cases:

### Used once

```python
df.filter(...).write.parquet(path)
```

If there is no meaningful reuse, caching may add overhead without providing a benefit.

### Cheap computation

If recomputation is cheaper than persistence, caching may be counterproductive.

### Very large data with low reuse

A huge dataset that is consumed once is often a poor cache candidate.

### Memory pressure

If persistence causes executor pressure, the workload can become slower.

### Cached before a highly selective filter

Compare:

```python
huge_df.cache()

reduced = huge_df.filter(...)
```

with:

```python
reduced = huge_df.filter(...)

reduced.cache()
```

If the expensive upstream work is not reused, caching the huge intermediate can waste storage.

The right boundary depends on:

- reuse;
- computation cost;
- data reduction;
- downstream branches.

### Immediately written once

If the result is written once and never reused in the application, durable materialization or direct execution may be more appropriate.

---

## 17. Cache After Reduction

Consider:

```python
huge_df = spark.read.parquet("/data/events")

huge_df.cache()

reduced = huge_df.filter(
    F.col("event_type") == "purchase"
)
```

This retains the large pre-filter result if persistence materializes it.

Compare:

```python
reduced = huge_df.filter(
    F.col("event_type") == "purchase"
)

reduced.cache()
```

Now the persisted representation is smaller if the filter is highly selective.

But do not turn this into a universal rule.

Sometimes the expensive computation is upstream of the filter and is reused by several branches. In that case, caching earlier can still be correct and useful.

The production question is:

> **Which boundary maximizes useful reuse per unit of storage and recomputation cost?**

---

## 18. Cache Everything Is a Bad Strategy

This is a common anti-pattern:

```python
df1.cache()
df2.cache()
df3.cache()
df4.cache()
df5.cache()
```

Why it is dangerous:

- executor storage is finite;
- cached blocks compete for resources;
- unused caches waste capacity;
- eviction can trigger recomputation;
- memory pressure can hurt execution;
- cache maintenance has overhead;
- more persisted data can make diagnosis harder.

Production principle:

> **Persist only data whose reuse justifies its storage cost.**

---

## 19. Cache Lifecycle

A useful lifecycle model is:

```text
CREATE
  ↓
PERSIST REQUESTED
  ↓
FIRST ACTION
  ↓
MATERIALIZE
  ↓
REUSE
  ↓
POSSIBLE EVICTION
  ↓
POSSIBLE RECOMPUTATION
  ↓
UNPERSIST
```

### State 1 — Not persisted

No cached blocks.

### State 2 — Persistence requested

```python
df.cache()
```

but no action has necessarily materialized the data.

### State 3 — Materialized

An action has computed partitions and Spark has persisted them according to the selected level.

### State 4 — Partially cached

Some partitions may be available while others are not.

### State 5 — Evicted

A cached block can be removed when resources are under pressure.

### State 6 — Recomputed

If the missing block is needed again, Spark can recompute it from lineage.

### State 7 — Unpersisted

```python
df.unpersist()
```

requests release of persisted blocks.

---

## 20. `unpersist()`

Use:

```python
df.unpersist()
```

after the persisted dataset is no longer useful.

Example:

```python
silver.cache()

silver.count()

gold_a = silver.filter(F.col("region") == "APAC")
gold_b = silver.filter(F.col("region") == "EMEA")

gold_a.write.mode("overwrite").parquet("/out/apac")
gold_b.write.mode("overwrite").parquet("/out/emea")

silver.unpersist()
```

### Why it matters

Long-running applications may process many stages or datasets.

Keeping old caches alive can waste storage capacity.

### Blocking behavior

PySpark exposes:

```python
df.unpersist(blocking=False)
```

The default is non-blocking.

If you need the unpersist operation to complete before continuing, use:

```python
df.unpersist(blocking=True)
```

Use blocking cleanup deliberately rather than mechanically.

---

## 21. Memory Pressure

Executor resources are finite.

Conceptually:

```text
Executor
├── execution needs
├── persisted/storage blocks
├── Python/runtime overhead
└── other resource demands
```

The important production relationship is:

```text
More cached data
        ↓
less available resource capacity
        ↓
possible memory pressure
        ↓
possible eviction / spill / GC pressure
        ↓
possible recomputation
        ↓
job may become slower
```

Do not rely on simplistic fixed memory percentages.

Actual memory behavior depends on:

- Spark version;
- execution mode;
- JVM/runtime;
- workload;
- serialization;
- Python process behavior;
- configuration;
- data shape.

The correct diagnostic question is:

> **Did persistence reduce recomputation enough to justify the resource pressure it introduced?**

---

## 22. Eviction and Recomputation

Caching is not permanent storage.

If a persisted partition is unavailable when needed, Spark can use lineage to recompute it.

Conceptually:

```text
Cached partition
      ↓
evicted
      ↓
downstream operation needs it
      ↓
Spark recomputes required lineage
      ↓
partition can be persisted again
```

This means a partially cached DataFrame can behave differently from a fully cached one.

### Important consequence

Do not assume:

```text
cache()
+
one successful count()
=
all partitions permanently resident forever
```

The Storage tab can show how much was actually cached.

---

## 23. Partial Cache

Imagine:

```text
Partition 0 → cached
Partition 1 → cached
Partition 2 → cached
Partition 3 → not cached
```

The next action may reuse three partitions and recompute one.

This can create confusing performance.

A developer might say:

> "But I cached the DataFrame."

The more precise question is:

> **How much of the DataFrame is actually persisted at the moment the action runs?**

Use the Spark UI to investigate.

---

## 24. Spark UI — Storage Tab

The Storage tab is the primary place to inspect persistence.

Look for:

- persisted dataset/RDD information;
- storage level;
- number of partitions;
- cached partitions;
- fraction cached;
- memory used;
- disk used.

A conceptual view:

```text
Dataset
Storage Level: MEMORY_AND_DISK_DESER
Partitions: 200
Cached: 200
Fraction Cached: 100%
Memory Used: ...
Disk Used: ...
```

### Questions to ask

1. Did the cache materialize?
2. How many partitions are cached?
3. Is the fraction cached complete?
4. How much memory is consumed?
5. Is disk being used?
6. Is the dataset actually reused?
7. Did runtime improve?

### 100% cached is not automatically "optimized"

A dataset can be 100% cached and still:

- be unnecessary;
- consume excessive resources;
- be slower overall;
- be poorly partitioned;
- be cached but rarely reused.

Caching is a means, not the objective.

---

## 25. Spark UI — Executors Tab

The Executors tab helps investigate resource behavior.

Caching-related questions include:

- Are executors under memory pressure?
- Is GC behavior changing?
- Are executors failing?
- Is resource usage uneven?
- Is storage pressure associated with slower execution?
- Did adding multiple caches create resource contention?

### Debugging workflow

```text
Slow job
  ↓
Check whether cache was requested
  ↓
Check Storage tab
  ↓
Check cached fraction
  ↓
Check memory/disk use
  ↓
Check Executors tab
  ↓
Inspect pressure/failures/GC where visible
  ↓
Compare against uncached baseline
  ↓
Change persistence strategy
  ↓
Measure again
```

Topic 15 teaches Spark UI debugging comprehensively. Here, focus only on the caching-specific evidence.

---

## 26. Caching and Shuffles

Connect Topics 07–09 to caching.

Example:

```text
large fact
   ↓
join
   ↓
shuffle
   ↓
aggregate
   ↓
expensive DataFrame
   ↓
three downstream uses
```

If the expensive DataFrame is persisted:

```text
first action
   ↓
pay computation + shuffle
   ↓
persist result
   ↓
later actions reuse result
```

This can avoid repeating the expensive upstream work.

But caching does **not**:

- eliminate the original shuffle;
- fix skew;
- automatically repartition data;
- replace AQE;
- make an inefficient query efficient by itself.

Caching is fundamentally a **reuse optimization**.

---

## 27. Caching and Data Skew

Topic 09 taught skew.

A common misconception is:

```python
df.cache()
```

will fix skew.

It will not.

If one partition is much larger:

```text
P0 → 10 MB
P1 → 12 MB
P2 → 11 MB
P3 → 900 MB
```

caching does not rebalance those partitions.

It stores the resulting partitions according to the persistence strategy.

Caching can actually make a poorly balanced result expensive to retain.

Use Topic 09 techniques for skew.

Use caching when the resulting computation is expensive and reused.

---

## 28. Caching and Multiple Branches

This is one of the strongest common use cases.

```python
silver = (
    orders
    .join(customers, "customer_id")
    .filter(F.col("status") == "completed")
)

silver.cache()

gold_revenue = (
    silver
    .groupBy("region")
    .agg(F.sum("amount").alias("revenue"))
)

gold_customers = (
    silver
    .select("customer_id")
    .distinct()
)

gold_products = (
    silver
    .groupBy("product_id")
    .count()
)
```

Conceptually:

```text
                 ┌── gold_revenue
                 │
expensive silver ├── gold_customers
                 │
                 └── gold_products
```

Without persistence, the expensive common upstream work can be repeated.

With persistence:

```text
compute silver once
       ↓
persist
       ↓
reuse across branches
```

This is a classic caching candidate.

---

## 29. Caching and Iterative Workloads

Iterative algorithms repeatedly operate on intermediate data.

Conceptually:

```text
state_0
  ↓
iteration_1
  ↓
iteration_2
  ↓
iteration_3
  ↓
...
```

Caching can avoid rebuilding the same expensive intermediate state repeatedly.

But careless loop caching can become an anti-pattern.

Bad pattern:

```python
current = initial_df

for i in range(10):
    current = expensive_transformation(current)
    current.cache()
    current.count()
```

Now multiple historical DataFrames may remain persisted.

A better pattern is to explicitly manage lifecycle.

For example:

```python
current = initial_df

for i in range(10):
    next_df = expensive_transformation(current)
    next_df.persist(StorageLevel.MEMORY_AND_DISK)

    next_df.count()

    if current is not initial_df:
        current.unpersist()

    current = next_df
```

The exact lifecycle depends on the algorithm, but the principle is:

> **Persist only the state you will reuse, and release state that is no longer needed.**

---

## 30. Long Lineage

Iterative processing can also produce increasingly long lineage:

```text
A → B → C → D → E → F → G → H → ...
```

Caching may reduce repeated execution of materialized data, but it does not fundamentally mean:

```text
lineage has disappeared
```

This distinction leads to checkpointing.

---

## 31. Checkpointing

Checkpointing addresses a different problem.

Core idea:

> **Checkpointing truncates lineage.**

Example:

```text
Before:

A → B → C → D → E → F → G → H
```

After checkpointing:

```text
A → B → C → CHECKPOINT
                    ↓
                    D → E
```

The checkpoint becomes a new materialization boundary.

### Why use checkpointing?

Potential reasons include:

- long iterative lineage;
- complex dependency chains;
- reducing recovery/recomputation depth;
- making iterative workflows more manageable.

Do not describe checkpointing as merely a "stronger cache."

The primary mental model is:

```text
CACHE
→ reuse computed data

CHECKPOINT
→ cut the lineage dependency chain
```

---

## 32. `checkpoint()`

A reliable checkpoint generally requires a configured checkpoint directory.

Example:

```python
spark.sparkContext.setCheckpointDir("/tmp/spark-checkpoints")
```

Then:

```python
checkpointed = df.checkpoint()
```

For DataFrames, `checkpoint()` is eager by default in modern PySpark APIs, but the API supports an `eager` argument.

For explicit behavior:

```python
checkpointed = df.checkpoint(eager=True)
```

The important concept is that the checkpoint creates a materialized boundary that truncates the previous lineage.

### Durability

A reliable checkpoint is intended to provide stronger recovery semantics than a local executor cache.

Use an appropriate durable/shared checkpoint location in a production environment.

Do not treat:

```text
/tmp
```

as automatically suitable for a production distributed system.

---

## 33. `localCheckpoint()`

Example:

```python
local_checkpointed = df.localCheckpoint()
```

Conceptually:

- it also truncates lineage;
- it uses local executor-side storage behavior rather than a durable checkpoint location;
- it is less reliable/durable than a proper checkpoint;
- it can be useful for controlled iterative workloads where full checkpoint durability is unnecessary.

The production distinction is:

```text
checkpoint()
→ stronger durability / recovery semantics

localCheckpoint()
→ faster/local lineage truncation with weaker durability
```

Exact implementation details can vary by Spark version and execution environment, so use the documentation for the Spark release being deployed.

---

## 34. `checkpoint()` vs `localCheckpoint()`

| Property | `checkpoint()` | `localCheckpoint()` |
|---|---|---|
| Main purpose | Truncate lineage | Truncate lineage |
| Storage model | Configured checkpoint location | Local executor-oriented storage |
| Durability | Stronger | Weaker |
| Suitable for critical recovery boundary | Yes, when correctly configured | Generally no |
| Useful in iterative computation | Yes | Yes, when weaker durability is acceptable |
| Failure tolerance | Better | Lower |

The key question is:

> **Can the workload tolerate losing a local checkpoint and recomputing or restarting?**

If not, use a durable checkpoint strategy.

---

## 35. Cache vs Checkpoint

| Concept | Primary purpose | Lineage | Durability | Typical use |
|---|---|---|---|---|
| `cache()` / `persist()` | Reuse computed data | Retained | Not durable across application lifecycle | Repeated reuse |
| `checkpoint()` | Truncate lineage | Truncated at checkpoint | Durable when configured appropriately | Long lineage / iterative processing |
| `localCheckpoint()` | Truncate lineage | Truncated at checkpoint | Weaker | Controlled local iterative workloads |

Mental model:

```text
CACHE
"Keep this result around because I will reuse it."

CHECKPOINT
"Create a new dependency boundary so I do not carry the old lineage forward."
```

These solve related but different problems.

---

## 36. Cache vs Parquet

There are three broad strategies:

```text
1. Recompute
2. Cache/persist
3. Materialize to Parquet
```

### Cache/persist

Advantages:

- convenient;
- fast reuse when data is resident;
- good for repeated work in one application.

Limitations:

- tied to application/executor lifecycle;
- not a durable business artifact;
- can be evicted;
- not automatically reusable by another independent job.

### Parquet

Example:

```python
intermediate.write.mode("overwrite").parquet(
    "/data/intermediate/sales"
)
```

Then:

```python
intermediate = spark.read.parquet(
    "/data/intermediate/sales"
)
```

Advantages:

- durable;
- restart-safe;
- shareable across jobs;
- explicit intermediate artifact.

Costs:

- write I/O;
- read I/O;
- storage cost;
- file-management concerns;
- additional pipeline boundary.

### Decision matrix

| Requirement | Recompute | Cache/Persist | Parquet |
|---|---:|---:|---:|
| Used once | Often appropriate | Usually unnecessary | Usually unnecessary |
| Reused repeatedly in same application | Possible | Strong candidate | Possible |
| Reused across jobs | Poor fit | Poor fit | Strong candidate |
| Must survive application restart | No | No | Yes |
| Very expensive computation | Maybe | Candidate | Candidate |
| Data larger than executor memory | Possible | Consider disk level | Strong candidate |
| Durable intermediate required | No | No | Yes |

Parquet is not automatically faster.

It is a **durable materialization strategy**, not simply a faster cache.

---

## 37. Cache vs Temp Views vs Python Variables

These concepts are different.

### Python variable

```python
cached_df = df
```

This does not materialize data.

It creates another Python reference to the DataFrame object.

### Temporary view

```python
df.createOrReplaceTempView("orders")
```

This creates a SQL name for the DataFrame.

It does not automatically persist the underlying data.

### Cache

```python
df.cache()
```

This requests physical persistence of computed partitions.

### Summary

```text
Python variable
→ reference

Temp view
→ SQL name

Cache/persist
→ physical reuse strategy
```

A temp view can be backed by a cached DataFrame if you explicitly persist that DataFrame, but creating the view alone does not imply caching.

---

## 38. Cache and Lineage

Consider:

```text
raw
 ↓
filter
 ↓
join
 ↓
aggregate
 ↓
cached_df
```

Persistence allows the computed result to be reused.

But lineage remains conceptually important for recovery and recomputation.

If a persisted block disappears:

```text
cached block unavailable
        ↓
lineage
        ↓
recompute
```

This is why cache is different from durable materialization.

---

## 39. Performance Measurement

Do not evaluate caching by intuition.

Measure.

A simple timer:

```python
import time

start = time.perf_counter()

df.count()

elapsed = time.perf_counter() - start

print(f"elapsed={elapsed:.3f}s")
```

For a meaningful experiment, compare:

```text
baseline
   ↓
cache()
   ↓
persist(MEMORY_AND_DISK)
   ↓
persist(DISK_ONLY)
   ↓
Parquet materialization
```

Record actual measurements.

### Measure

- first-action wall-clock time;
- second-action wall-clock time;
- repeated-action time;
- shuffle read/write;
- spill;
- memory usage;
- disk usage;
- task duration;
- cached fraction;
- correctness.

### Benchmark table

| Strategy | First action | Second action | Memory | Disk | Notes |
|---|---:|---:|---:|---:|---|
| No cache | record actual | record actual | record actual | record actual | recomputation |
| `MEMORY_ONLY` | record actual | record actual | record actual | record actual | |
| `MEMORY_AND_DISK` | record actual | record actual | record actual | record actual | |
| `DISK_ONLY` | record actual | record actual | record actual | record actual | |
| Parquet | record actual | record actual | record actual | record actual | durable |

Never invent benchmark numbers.

---

## 40. Benchmarking Correctly

A poor benchmark is:

```python
df.cache()
df.count()

df.count()
```

without documenting:

- whether the cache was warm;
- whether the application was reused;
- whether the source was local or remote;
- whether the cluster was idle;
- whether the dataset was already in an OS/storage cache;
- whether the same action was repeated;
- whether correctness was checked.

A better experimental process is:

```text
1. Establish baseline.
2. Run the workload.
3. Record metrics.
4. Reset/clean state where practical.
5. Add persistence.
6. Materialize.
7. Run the same downstream workload.
8. Record metrics.
9. Compare.
10. Validate correctness.
```

Change one major variable at a time.

---

## 41. Production Decision Framework

Ask:

1. Is this DataFrame reused?
2. How many times?
3. How expensive is recomputation?
4. How large is the DataFrame?
5. How many partitions does it have?
6. How large are those partitions?
7. How much executor storage is available?
8. Is the workload memory-sensitive?
9. Could caching cause eviction?
10. Does the DataFrame contain an expensive shuffle?
11. Is it reused only within this application?
12. Does it need to survive application restart?
13. Does another job need the data?
14. Is lineage becoming too long?
15. Would checkpointing solve the actual problem?
16. Would Parquet be a better durable intermediate?
17. Did measurement prove caching helped?

### Decision tree

```text
Is the result reused?
       /       \
     NO         YES
     |           |
Usually don't   Is recomputation expensive?
cache           /                  \
              NO                    YES
              |                      |
       Usually don't cache     Is memory/storage adequate?
                                  /          \
                                YES           NO
                                 |             |
                          cache/persist     choose level
                                            or durable
                                            materialization
```

Then ask:

```text
Does it need to survive application restart?
        |
       YES
        ↓
Consider durable storage such as Parquet
or an appropriate persistent data artifact.
```

```text
Is lineage too long?
        |
       YES
        ↓
Consider checkpointing.
```

```text
Is it repeatedly reused inside one application?
        |
       YES
        ↓
Consider cache/persist.
```

The answer can be a combination.

For example:

```text
checkpoint
   ↓
cache
   ↓
reuse repeatedly
```

may be appropriate in a specific iterative workload.

---

## 42. Production Scenario A — Five Gold Outputs

A silver DataFrame is produced by:

```text
orders
  ↓
customer join
  ↓
status filter
  ↓
business transformations
  ↓
silver
```

Five gold outputs reuse it.

Questions:

1. Is there meaningful reuse?
2. Is the silver transformation expensive?
3. How large is the silver dataset?
4. Does it fit in the selected persistence level?
5. How much executor storage is available?
6. Is the cache actually materialized?
7. Does the measured runtime improve?

This is a strong caching candidate, but the final decision should still be measured.

---

## 43. Production Scenario B — 500 GB Used Once

A 500 GB DataFrame is created and written once.

Potential reasoning:

```text
reuse = low
storage requirement = huge
benefit from cache = low
```

Blindly caching is usually difficult to justify.

A direct write or durable intermediate strategy may be more appropriate depending on the pipeline.

Do not answer solely from the number 500 GB.

The correct decision also depends on:

- partitioning;
- cluster resources;
- downstream reuse;
- recomputation cost;
- pipeline architecture.

---

## 44. Production Scenario C — Reused Data but Limited Memory

A dataset is repeatedly reused but cannot comfortably fit in executor memory.

Possible choices:

- `MEMORY_AND_DISK`;
- `DISK_ONLY`;
- durable Parquet materialization;
- redesign the reuse boundary;
- reduce data before persistence.

Measure each relevant option.

Do not assume:

```text
MEMORY_ONLY
```

is correct simply because memory access is fast.

---

## 45. Production Scenario D — Multiple Independent Jobs

A team wants to cache a DataFrame today and reuse it tomorrow from a separate Spark application.

Cache is usually the wrong abstraction for that requirement.

Why?

```text
cache/persist
→ application-level execution optimization

Parquet/table
→ durable data artifact
```

Use durable materialization when the data must survive application lifecycle boundaries.

---

## 46. Production Scenario E — Iterative Enrichment

Suppose:

```text
iteration 1
  ↓
iteration 2
  ↓
iteration 3
  ↓
...
```

The lineage becomes increasingly complex.

Possible tools:

```text
cache/persist
+
checkpoint
```

The decision depends on the problem:

- cache helps repeated reuse;
- checkpoint truncates lineage.

Do not use cache as a substitute for lineage management.

---

## 47. Spark Connect and Managed-Platform Awareness

Modern Spark deployments can include Spark Connect and managed platforms with platform-specific caching or disk-cache features.

The important awareness point is:

> **Do not assume that every "cache" you encounter has identical lifecycle, durability, or physical behavior across all deployment products.**

For this module:

- learn standard Spark `cache()` / `persist()` semantics;
- understand that managed platforms may provide additional storage/cache layers;
- verify platform-specific behavior before designing around it;
- do not treat a platform disk cache as equivalent to a durable business table.

Spark Connect can also change where client and server responsibilities live.

The production principle remains:

> **Know which layer is providing the persistence and what its lifecycle guarantees are.**

---

## 48. Hands-On Coding Examples

### Example 1 — No Caching

```python
from pyspark.sql import functions as F

orders = spark.read.parquet("/data/orders")

completed = (
    orders
    .filter(F.col("status") == "completed")
    .select("customer_id", "amount")
)

completed.count()
completed.groupBy("customer_id").count().show()
```

**What it does:** Builds and uses a transformed DataFrame twice.

**What to observe:** Without persistence, the upstream work may be repeated for separate actions.

**Production lesson:** Reuse does not automatically imply caching; measure the recomputation cost.

---

### Example 2 — `cache()`

```python
completed = (
    orders
    .filter(F.col("status") == "completed")
    .select("customer_id", "amount")
)

completed.cache()

completed.count()
completed.groupBy("customer_id").count().show()
```

**What to observe:** The first action materializes persisted blocks; later work can reuse them.

**Mistake to avoid:** Assuming `cache()` itself executes the DataFrame.

---

### Example 3 — `MEMORY_ONLY`

```python
from pyspark import StorageLevel

completed.persist(StorageLevel.MEMORY_ONLY)

completed.count()
```

**What it demonstrates:** Explicit persistence with a chosen storage level.

**Mistake to avoid:** Assuming all partitions will necessarily remain resident under arbitrary memory pressure.

---

### Example 4 — `MEMORY_AND_DISK`

```python
completed.persist(StorageLevel.MEMORY_AND_DISK)

completed.count()
```

**What it demonstrates:** A persistence strategy that can use disk when memory is insufficient.

**Mistake to avoid:** Assuming disk fallback makes the data as fast as memory.

---

### Example 5 — `DISK_ONLY`

```python
completed.persist(StorageLevel.DISK_ONLY)

completed.count()
```

**What it demonstrates:** Persistence without retaining the persisted representation in executor memory.

**Mistake to avoid:** Expecting memory-like read performance.

---

### Example 6 — `unpersist()`

```python
completed.cache()
completed.count()

# downstream work
completed.groupBy("customer_id").count().show()

completed.unpersist()
```

**What it demonstrates:** Explicit lifecycle management.

**Mistake to avoid:** Keeping every historical cache alive in a long-running application.

---

### Example 7 — Multiple Branches

```python
silver = (
    orders
    .join(customers, "customer_id")
    .filter(F.col("status") == "completed")
)

silver.cache()

gold_revenue = (
    silver
    .groupBy("region")
    .agg(F.sum("amount").alias("revenue"))
)

gold_customers = (
    silver
    .select("customer_id")
    .distinct()
)

gold_products = (
    silver
    .groupBy("product_id")
    .count()
)
```

**What it demonstrates:** One expensive common input reused by multiple branches.

**Mistake to avoid:** Caching a common branch that is not actually expensive or reused.

---

### Example 8 — Cache After Reduction

```python
events = spark.read.parquet("/data/events")

purchases = (
    events
    .filter(F.col("event_type") == "purchase")
    .select("user_id", "product_id", "event_ts")
)

purchases.cache()
purchases.count()
```

**What it demonstrates:** Persisting a potentially smaller downstream representation.

**Mistake to avoid:** Assuming the reduced dataset is always the correct cache boundary. Reuse and computation cost determine the best boundary.

---

### Example 9 — Checkpoint

```python
spark.sparkContext.setCheckpointDir(
    "/data/checkpoints/spark-app"
)

checkpointed = df.checkpoint(eager=True)

checkpointed.count()
```

**What it demonstrates:** Creating a checkpoint boundary.

**Mistake to avoid:** Treating checkpoint as simply another cache.

---

### Example 10 — Local Checkpoint

```python
local_checkpointed = df.localCheckpoint(eager=True)

local_checkpointed.count()
```

**What it demonstrates:** Local lineage truncation with weaker durability.

**Mistake to avoid:** Using it where durable recovery is a requirement.

---

### Example 11 — Cache vs Parquet

```python
intermediate = expensive_transformation()

intermediate.cache()
intermediate.count()
```

versus:

```python
intermediate = expensive_transformation()

intermediate.write.mode("overwrite").parquet(
    "/data/intermediate/customer_summary"
)

reloaded = spark.read.parquet(
    "/data/intermediate/customer_summary"
)
```

**What it demonstrates:** Application-local persistence versus durable materialization.

---

### Example 12 — Runtime Measurement

```python
import time

start = time.perf_counter()
df.count()
elapsed = time.perf_counter() - start

print(f"elapsed={elapsed:.3f}s")
```

Run the same workload under controlled conditions.

**Mistake to avoid:** Comparing a cold first action with a warm cached action and calling the difference a complete cache benchmark.

---

### Example 13 — Inspect Partitions

```python
print(
    "partitions:",
    df.rdd.getNumPartitions()
)
```

**What it demonstrates:** Partition count can help interpret cache size and task behavior.

**Mistake to avoid:** Converting DataFrames to RDDs unnecessarily in production just to inspect a basic property repeatedly.

---

### Example 14 — Explicit Persistence Status

```python
print(
    "storage level:",
    df.storageLevel
)
```

Use this as a quick programmatic check of the DataFrame's persistence setting.

Then use the Spark UI to inspect what has actually been materialized.

---

## 49. Hands-On Labs

### Lab 1 — Three Outputs From One Expensive Silver DataFrame

Build:

- one expensive silver join;
- three gold outputs.

Run:

1. without cache;
2. with `cache()`;
3. with `persist(DISK_ONLY)`.

Measure:

- wall-clock time;
- shuffle behavior;
- memory;
- disk usage.

Record actual results.

Do not fabricate numbers.

---

### Lab 2 — Cache That Should Not Exist

Create a DataFrame that:

- is expensive enough to be interesting;
- is used only once.

Compare:

```text
cached
vs
uncached
```

Observe:

- storage usage;
- first-action time;
- overall runtime.

Remove the cache.

Write down why the cache was unnecessary.

---

### Lab 3 — Cache After Reduction

Compare:

```python
huge_df.cache()

filtered = huge_df.filter(
    F.col("event_type") == "purchase"
)
```

against:

```python
filtered = huge_df.filter(
    F.col("event_type") == "purchase"
)

filtered.cache()
```

Measure:

- cached data size;
- reuse;
- runtime;
- memory pressure.

Explain when the second strategy may be better.

---

### Lab 4 — Storage Levels

Run the same reusable workload with:

```text
MEMORY_ONLY
MEMORY_AND_DISK
DISK_ONLY
```

Record:

```text
first action
second action
memory
disk
runtime
```

Do not declare a winner without measurements.

---

### Lab 5 — Cache Eviction / Memory Pressure

Create a sufficiently large dataset to create meaningful storage pressure without intentionally crashing the environment.

Observe:

- Storage tab;
- Executors tab;
- cached fraction;
- memory usage;
- disk usage;
- task behavior;
- recomputation if visible.

Explain what changed.

---

### Lab 6 — Checkpointing

Create an iterative transformation.

Compare:

```text
normal lineage
cache
checkpoint
```

Study:

- lineage behavior;
- materialization;
- runtime;
- recovery implications.

Explain which problem each technique addresses.

---

### Lab 7 — Cache vs Parquet

Compare:

```text
persisted intermediate
```

against:

```text
Parquet intermediate
```

Discuss:

- speed;
- durability;
- sharing;
- restart behavior;
- storage cost;
- operational complexity.

---

### Lab 8 — Multiple Branches

Create one expensive DataFrame and at least three downstream branches.

Run:

```text
without persistence
with cache
```

Measure the repeated upstream work.

Explain whether the reuse justified the cache.

---

### Lab 9 — `unpersist()` Lifecycle

Build a long-running sequence with two reusable intermediates.

Persist the first.

Use it.

Unpersist it.

Persist the second.

Observe the Storage tab.

Explain why lifecycle management matters.

---

### Lab 10 — First Action vs Warm Action

Measure:

```text
first action after cache()
second action
third action
```

Explain:

- materialization cost;
- warm reuse;
- possible eviction.

---

### Lab 11 — Iterative Workload

Implement several enrichment iterations.

Experiment with:

```text
cache every iteration
cache current state only
checkpoint periodically
```

Measure resource behavior.

Do not retain every historical DataFrame indefinitely.

---

### Lab 12 — Production Decision Lab

Given several datasets, decide:

```text
recompute
cache
MEMORY_ONLY
MEMORY_AND_DISK
DISK_ONLY
checkpoint
Parquet
```

For every choice justify:

- reuse;
- cost;
- size;
- memory;
- durability;
- lifecycle;
- measurement plan.

---

## 50. Debugging Exercises

### Scenario 1 — `cache()` Was Called, but the First Action Is Still Slow

**Symptom:** Developer expects `cache()` to make the first action immediately fast.

**Likely cause:** The first action is materializing the cache.

**Investigation:**

- compare first and second actions;
- inspect Storage tab;
- verify cached fraction.

**Fix:** Explain lazy materialization and benchmark subsequent reuse.

**Do not:** Conclude that caching failed simply because the first action was expensive.

---

### Scenario 2 — Caching Made the Second Action Slower

**Symptom:** The cached version is slower overall.

**Likely causes:**

- persistence overhead;
- memory pressure;
- poor cache boundary;
- insufficient reuse;
- storage-level mismatch.

**Investigation:**

- compare baseline;
- inspect memory;
- inspect disk;
- inspect cached fraction;
- inspect task time.

**Fix:** Remove or change persistence if evidence does not justify it.

---

### Scenario 3 — Storage Tab Shows Only 60% Cached

**Symptom:** Only part of the dataset is cached.

**Likely causes:**

- insufficient memory;
- eviction;
- incomplete materialization;
- executor loss.

**Investigation:**

- check number of partitions;
- check memory/disk;
- inspect Executors;
- rerun the action.

**Fix:** Choose an appropriate storage level or redesign the cache boundary.

---

### Scenario 4 — Executor Memory Pressure After Several Caches

**Symptom:** Multiple DataFrames have been persisted.

**Likely cause:** Too much cached state competing for finite resources.

**Fix:**

- unpersist unused datasets;
- reduce cache count;
- reduce data before persistence;
- choose another storage level.

**Do not:** Add caches simply because a DataFrame is reused once.

---

### Scenario 5 — Cached DataFrame Is Never Reused

**Symptom:** A DataFrame was cached and then immediately written once.

**Diagnosis:** Persistence may have added unnecessary overhead.

**Fix:** Remove the cache and compare.

---

### Scenario 6 — Raw Dataset Cached Before Filtering

**Symptom:** A huge raw dataset consumes storage.

**Investigation:** Determine whether the raw dataset is reused independently.

**Fix:** Consider caching a reduced downstream result if that is the actual reusable boundary.

**Caveat:** Do not move the cache blindly; measure the computational cost of rebuilding the upstream portion.

---

### Scenario 7 — Developer Expects Cache to Survive Application Restart

**Symptom:** A new application cannot find yesterday's cached DataFrame.

**Diagnosis:** Cache is not a durable cross-application data artifact.

**Fix:** Materialize to durable storage such as Parquet when cross-job reuse is required.

---

### Scenario 8 — Developer Uses Cache to Fix Skew

**Symptom:** One task remains much slower than others.

**Diagnosis:** Cache does not rebalance partitions.

**Fix:** Use Topic 09 skew diagnosis and mitigation techniques.

---

### Scenario 9 — Long Iterative Pipeline Still Has Huge Lineage

**Symptom:** Developer cached every iteration but lineage remains complex.

**Diagnosis:** Cache and lineage truncation are different concepts.

**Fix:** Evaluate checkpointing.

---

### Scenario 10 — Intermediate Data Must Be Reused by Multiple Jobs

**Symptom:** Several independent applications need the same intermediate.

**Diagnosis:** Application-local cache is the wrong lifecycle.

**Fix:** Consider durable Parquet/table materialization.

---

### Scenario 11 — `MEMORY_ONLY` Causes Repeated Recomputation

**Symptom:** A reused dataset is not fully retained.

**Diagnosis:** The selected storage level cannot keep all required persisted blocks resident under the available resources.

**Fix:** Test `MEMORY_AND_DISK` or another appropriate strategy.

---

### Scenario 12 — `DISK_ONLY` Uses Too Much Time

**Symptom:** Persistence exists, but later actions remain slow.

**Diagnosis:** Disk-backed reuse can be slower than memory.

**Fix:** Determine whether the speed trade-off is acceptable or whether a different level or durable materialization is better.

---

## 51. Production Scenarios

### Scenario A — Silver Reused Five Times

A silver DataFrame feeds five gold outputs.

Ask:

- Is the upstream work expensive?
- How large is silver?
- Does it fit the chosen persistence level?
- How much storage is available?
- Does measured runtime improve?

Potential answer:

> Strong caching candidate, subject to measurement and resource capacity.

---

### Scenario B — 500 GB Dataset Used Once

Ask:

- Is it actually reused?
- Is recomputation likely?
- Does caching provide measurable benefit?

Potential reasoning:

> Low reuse weakens the case for caching, especially when the persisted representation is very large.

---

### Scenario C — 50 GB Reused Repeatedly With Limited Memory

Possible candidates:

```text
MEMORY_AND_DISK
DISK_ONLY
Parquet
```

The decision depends on:

- reuse frequency;
- memory;
- disk;
- runtime;
- durability requirements.

---

### Scenario D — Separate Daily Jobs Need the Same Result

Cache is not the correct cross-application persistence boundary.

Consider:

```text
Parquet / table / durable data artifact
```

---

### Scenario E — Long Iterative Enrichment

Potential combination:

```text
checkpoint
+
cache
```

if:

- lineage must be truncated;
- the checkpoint boundary is reused repeatedly.

Do not use the combination automatically.

---

## 52. Common Mistakes and Misconceptions

### 1. "cache() immediately executes the DataFrame."

**Correct model:** `cache()` is lazy. An action materializes the persisted data.

### 2. "cache() means permanent storage."

**Correct model:** Cache is application-level persistence, not a durable business artifact.

### 3. "cache() removes shuffles."

**Correct model:** It can prevent repeated upstream computation after materialization, but it does not remove the original shuffle.

### 4. "cache() fixes skew."

**Correct model:** Cache stores the resulting partitions; it does not rebalance skew.

### 5. "cache() always makes jobs faster."

**Correct model:** Persistence adds storage and materialization cost and can create resource pressure.

### 6. "MEMORY_ONLY is always best."

**Correct model:** Storage level depends on data size, reuse, resources, and workload.

### 7. "MEMORY_AND_DISK means everything stays in memory."

**Correct model:** It allows persisted blocks to use disk when memory is insufficient.

### 8. "Every cached partition remains forever."

**Correct model:** Cached blocks can be evicted or lost and recomputed.

### 9. "`unpersist()` deletes the source data."

**Correct model:** It releases persisted blocks; it does not delete the source dataset.

### 10. "Checkpoint is just another cache."

**Correct model:** Checkpointing primarily truncates lineage.

### 11. "`localCheckpoint()` is as durable as `checkpoint()`."

**Correct model:** Local checkpointing has weaker durability/recovery properties.

### 12. "Python variable assignment materializes data."

**Correct model:** Assignment creates a reference to a DataFrame object.

### 13. "A temp view automatically caches data."

**Correct model:** A temp view provides a SQL name; persistence must be requested separately.

### 14. "More cached DataFrames always means better performance."

**Correct model:** Unused caches waste finite resources.

### 15. "100% cached means the job is optimized."

**Correct model:** Complete caching does not prove that caching was useful.

### 16. "The first action after cache should be fast."

**Correct model:** The first action can include the full computation and cache materialization.

### 17. "Cache survives application restart."

**Correct model:** Use durable storage when data must survive the application lifecycle.

### 18. "A cache is equivalent to Parquet."

**Correct model:** Cache is a runtime reuse mechanism; Parquet is durable materialization.

### 19. "Checkpoint always makes the job faster."

**Correct model:** Checkpointing adds I/O and should solve a lineage/recovery problem that justifies its cost.

### 20. "Caching is a substitute for query optimization."

**Correct model:** Fix expensive transformations, skew, partitioning, and execution strategy where appropriate. Cache is one reuse optimization.

---

## 53. Practice Questions

Exactly 40 questions: 10 Basic, 10 Moderate, 10 Hard, 10 Advanced.

### Basic — 1–10

#### B1. What problem does caching solve?

**Answer:** It can prevent repeated computation of an expensive intermediate result that is reused.

**Reasoning:** Spark is lazy and can recompute lineage for separate actions unless the result is persisted.

---

#### B2. Is `cache()` eager?

**Answer:** No.

**Reasoning:** `cache()` marks the DataFrame for persistence; an action is needed to compute and populate persisted blocks.

---

#### B3. What is the first action after `cache()` responsible for?

**Answer:** It computes the required lineage and materializes persisted partitions as part of execution.

---

#### B4. What does `unpersist()` do?

**Answer:** It requests release of persisted blocks for the DataFrame.

---

#### B5. What is a `StorageLevel`?

**Answer:** A specification describing how Spark should persist data, including memory/disk use, serialization behavior, and replication.

---

#### B6. What is the main purpose of `MEMORY_AND_DISK`?

**Answer:** To retain persisted blocks in memory when possible and use disk when memory is insufficient.

---

#### B7. Does a Python variable automatically cache a DataFrame?

**Answer:** No.

---

#### B8. Does a temporary view automatically cache a DataFrame?

**Answer:** No.

---

#### B9. What is the primary purpose of checkpointing?

**Answer:** To truncate lineage.

---

#### B10. When is Parquet preferable to cache?

**Answer:** When the intermediate must be durable, restart-safe, or shared across independent jobs.

---

### Moderate — 11–20

#### M11. Why can the first action after `cache()` still be slow?

**Answer:** It may perform the full upstream computation while materializing persisted partitions.

---

#### M12. Why can caching a DataFrame used once be wasteful?

**Answer:** The persistence overhead may not be recovered through reuse.

---

#### M13. Why can caching a large raw DataFrame before filtering be inefficient?

**Answer:** The persisted representation may be much larger than a reduced downstream result that would have been sufficient for reuse.

---

#### M14. Why might `MEMORY_AND_DISK` be preferable to `MEMORY_ONLY`?

**Answer:** When the dataset may not fit comfortably in memory and recomputation is expensive.

---

#### M15. What does a partially cached DataFrame mean?

**Answer:** Some partitions are persisted while others are unavailable or not currently cached.

---

#### M16. Why can an evicted partition be recomputed?

**Answer:** Spark retains lineage information that can be used to reconstruct missing partitions.

---

#### M17. How does caching interact with a shuffle?

**Answer:** It can avoid repeating an already-computed shuffle-producing lineage when the shuffled result is persisted and reused, but it does not remove the original shuffle.

---

#### M18. Why is a DataFrame with multiple downstream branches a good cache candidate?

**Answer:** A common expensive upstream result can be computed once and reused across branches.

---

#### M19. What is the difference between cache and checkpoint?

**Answer:** Cache/persist is primarily for reuse; checkpointing is primarily for truncating lineage.

---

#### M20. Why is a temp view not equivalent to cache?

**Answer:** A temp view provides SQL naming/access; cache requests physical persistence of computed data.

---

### Hard — 21–30

#### H21. A DataFrame is reused three times but caching makes total runtime worse. Give three possible explanations.

**Answer:** The dataset may be too large, persistence may create memory pressure, or recomputation may be cheaper than the chosen persistence strategy.

---

#### H22. Why might 100% cache coverage still be a bad design?

**Answer:** The cached result may be unnecessary, rarely reused, or consuming resources that would be better allocated to execution.

---

#### H23. Why can `DISK_ONLY` be useful?

**Answer:** It can preserve reusable results without retaining their persisted representation in executor memory, at the cost of slower disk-backed access.

---

#### H24. Why can `_2` storage levels be expensive?

**Answer:** Replication creates additional copies, increasing storage and network cost.

---

#### H25. Why does checkpointing help long iterative lineage?

**Answer:** It creates a materialization boundary and truncates the previous dependency chain.

---

#### H26. Why might `localCheckpoint()` be inappropriate for a critical recovery boundary?

**Answer:** It has weaker durability/reliability characteristics than a properly configured durable checkpoint.

---

#### H27. How would you compare cache and Parquet for a reusable intermediate?

**Answer:** Compare reuse frequency, lifecycle, durability, storage cost, write/read I/O, memory pressure, and whether multiple jobs need the data.

---

#### H28. What would you inspect if the Storage tab shows only 60% cached?

**Answer:** Partition count, resource pressure, eviction, materialization completeness, executor status, and persistence level.

---

#### H29. Why can caching and skew coexist?

**Answer:** Caching preserves computed partitions but does not rebalance uneven work.

---

#### H30. Why should cache placement be treated as a design decision?

**Answer:** The placement determines the amount of data stored, the amount of recomputation avoided, and which downstream branches can reuse the result.

---

### Advanced — 31–40

#### A31. Design a persistence strategy for a silver DataFrame used by five gold branches.

**Answer:** Establish a baseline, measure silver computation cost and size, persist the common boundary if reuse justifies it, select a storage level based on resource capacity, materialize deliberately, monitor the Storage/Executors tabs, and unpersist when the branches finish.

---

#### A32. A cached dataset is fully materialized but total job time increased. How would you prove whether caching caused the regression?

**Answer:** Compare controlled baseline and persisted runs, including first-action cost, later actions, memory, disk, shuffle, spill, task time, and correctness. Inspect whether the cache caused resource contention.

---

#### A33. When would you combine checkpointing and caching?

**Answer:** In a workload where lineage must be truncated and the resulting checkpointed state is also reused repeatedly.

---

#### A34. How would you choose between `MEMORY_AND_DISK` and `DISK_ONLY`?

**Answer:** Measure whether retaining the persisted representation in memory materially improves reuse enough to justify memory consumption. If memory pressure is harmful and disk reuse is adequate, `DISK_ONLY` may be preferable.

---

#### A35. Why is cache not a cross-job data-sharing mechanism?

**Answer:** Persistence is tied to the application's runtime/executor lifecycle rather than serving as a durable shared data artifact.

---

#### A36. How would you investigate a cache that appears to be ignored?

**Answer:** Verify the DataFrame is actually persisted, run an action to materialize it, inspect Storage-tab state, check whether later operations reference the same persisted DataFrame, and inspect resource pressure/eviction.

---

#### A37. How can partitioning affect cache efficiency?

**Answer:** Cached data is stored partition by partition, so partition size and distribution influence storage requirements, task behavior, and the likelihood of uneven resource pressure.

---

#### A38. What evidence would justify replacing cache with Parquet?

**Answer:** Cross-job reuse, restart durability requirements, insufficient runtime storage resources, operational need for an explicit intermediate artifact, or measurements showing durable materialization is a better lifecycle boundary.

---

#### A39. What evidence would justify removing a cache?

**Answer:** Low reuse, low recomputation cost, significant storage/memory overhead, eviction/recomputation, or measured runtime regression.

---

#### A40. What is the most important production question before adding `cache()`?

**Answer:** **What repeated computation am I avoiding, and is that saving worth the storage/resource cost?**

---

## 54. Interview Practice

Exactly 40 interview questions are provided below.

### Basic — 1–10

#### I1. What is Spark caching?

**Answer guidance:** Explain it as runtime persistence of computed partitions for reuse.

#### I2. Why does Spark need caching?

**Answer guidance:** Lazy evaluation means reusable lineage can be recomputed for separate actions.

#### I3. Is `cache()` lazy?

**Answer guidance:** Yes. An action materializes persisted data.

#### I4. What is `persist()`?

**Answer guidance:** Explicit persistence with a chosen storage level.

#### I5. What is `unpersist()`?

**Answer guidance:** Requests release of persisted blocks.

#### I6. What is `StorageLevel`?

**Answer guidance:** It defines persistence characteristics such as memory, disk, serialization, and replication.

#### I7. What is the modern DataFrame default persistence level?

**Answer guidance:** Modern DataFrame caching uses `MEMORY_AND_DISK_DESER`; do not confuse it with historical RDD defaults.

#### I8. Does caching make data durable?

**Answer guidance:** No. Use durable storage when lifecycle guarantees are required.

#### I9. What is checkpointing?

**Answer guidance:** A mechanism for truncating lineage by materializing a checkpoint boundary.

#### I10. What is the difference between cache and checkpoint?

**Answer guidance:** Cache is primarily for reuse; checkpoint is primarily for lineage truncation.

---

### Moderate — 11–20

#### I11. What happens during the first action after `cache()`?

**Answer guidance:** The upstream computation executes and persisted blocks are materialized as part of that execution.

#### I12. Why can the first cached action still be expensive?

**Answer guidance:** It includes the initial computation and persistence cost.

#### I13. When should you cache a DataFrame?

**Answer guidance:** When expensive computation is reused sufficiently and resource cost is justified.

#### I14. When should you not cache?

**Answer guidance:** One-time use, cheap computation, low reuse, large storage footprint, or resource pressure.

#### I15. Explain `MEMORY_ONLY` versus `MEMORY_AND_DISK`.

**Answer guidance:** Memory-only prioritizes memory retention; memory-and-disk allows disk fallback for persisted blocks.

#### I16. Why use `DISK_ONLY`?

**Answer guidance:** To persist reusable results while minimizing persisted representation in executor memory.

#### I17. What are replicated storage levels?

**Answer guidance:** They maintain additional copies at additional storage/network cost.

#### I18. What is cache eviction?

**Answer guidance:** Persisted blocks can be removed when resources are constrained; missing blocks can later be recomputed.

#### I19. What is a partially cached dataset?

**Answer guidance:** Some partitions are persisted while others are not currently available in the cache.

#### I20. How do you inspect cached data?

**Answer guidance:** Use the Spark UI Storage tab and correlate with Executors/resource behavior.

---

### Hard — 21–30

#### I21. Why can caching slow a job down?

**Answer guidance:** Materialization and storage overhead, memory pressure, disk I/O, eviction, and insufficient reuse can outweigh saved computation.

#### I22. Why is caching after filtering sometimes better?

**Answer guidance:** It may reduce the persisted data volume, but only if the filtered result is the correct reusable boundary.

#### I23. Why might caching before filtering still be correct?

**Answer guidance:** If the expensive upstream computation is shared by multiple downstream branches, caching earlier can maximize reuse.

#### I24. Does caching remove shuffle?

**Answer guidance:** No. It can prevent repeated execution of a shuffle-producing lineage after the result is persisted.

#### I25. Does caching fix skew?

**Answer guidance:** No. It does not rebalance partitions.

#### I26. Why can an evicted partition be recomputed?

**Answer guidance:** Spark retains lineage needed to reconstruct the partition.

#### I27. Why does checkpointing differ from cache?

**Answer guidance:** Checkpointing changes the lineage boundary; caching retains reusable computed partitions.

#### I28. What is `localCheckpoint()`?

**Answer guidance:** A local, less durable lineage-truncation mechanism.

#### I29. Why is Parquet useful as an intermediate?

**Answer guidance:** It creates a durable, shareable artifact that can survive application restart and be consumed by independent jobs.

#### I30. How would you benchmark caching?

**Answer guidance:** Compare controlled baseline and persisted runs, distinguish first versus warm actions, and inspect runtime/resource/correctness metrics.

---

### Advanced — 31–40

#### I31. How would you decide between cache and Parquet?

**Answer guidance:** Evaluate application lifecycle, reuse scope, durability, size, resource availability, I/O cost, and measured performance.

#### I32. How would you diagnose a cache that only reaches 60% coverage?

**Answer guidance:** Investigate partition count, memory pressure, eviction, executor state, storage level, and materialization.

#### I33. How does caching interact with executor memory?

**Answer guidance:** Persisted blocks consume storage resources and can compete with execution needs, creating pressure and potentially eviction/recomputation.

#### I34. How would you manage caches in a long-running application?

**Answer guidance:** Persist selectively, monitor usage, unpersist obsolete datasets, and avoid accumulating historical caches.

#### I35. How would you cache an iterative workload?

**Answer guidance:** Persist only the current reusable state, materialize deliberately, unpersist obsolete state, and evaluate checkpointing for lineage control.

#### I36. When would you combine checkpoint and cache?

**Answer guidance:** When lineage truncation and repeated reuse are both actual requirements.

#### I37. Why can a 100% cached dataset still be a performance problem?

**Answer guidance:** Complete caching does not establish that storage cost was justified or that downstream execution is efficient.

#### I38. What production metrics matter when evaluating caching?

**Answer guidance:** Wall time, first/warm action time, shuffle, spill, memory/disk usage, cached fraction, task behavior, executor health, and correctness.

#### I39. How would you explain a cache regression to a production team?

**Answer guidance:** Show baseline versus persisted measurements, identify resource contention or low reuse, and recommend removing/changing persistence based on evidence.

#### I40. What is your production caching philosophy?

**Answer guidance:** Persist deliberately, measure reuse, choose the least costly adequate storage level, observe the runtime system, and remove persistence that does not provide measurable value.

---

## 55. Architecture Scenarios

At least six production architecture scenarios are required.

### Architecture 1 — Large Medallion Pipeline

Design caching for:

```text
Bronze
  ↓
Silver
  ↓
Gold A
Gold B
Gold C
Gold D
Gold E
```

Questions:

1. Which layer is the likely reuse boundary?
2. What makes a silver DataFrame a cache candidate?
3. What metrics must be collected?
4. How should the persistence level be selected?
5. When should it be unpersisted?
6. When would Parquet be preferable?

A strong design should explicitly separate:

```text
runtime reuse
```

from:

```text
durable data architecture
```

---

### Architecture 2 — Reused Silver Layer

A silver DataFrame is reused by five downstream transformations.

Evaluate:

```text
no persistence
cache()
MEMORY_AND_DISK
DISK_ONLY
Parquet
```

Justify the decision using:

- computation cost;
- reuse frequency;
- data size;
- executor storage;
- disk capacity;
- lifecycle;
- durability;
- measurements.

---

### Architecture 3 — Iterative Spark Workload

An enrichment algorithm executes 20 iterations.

Design a strategy for:

- current-state persistence;
- old-state cleanup;
- checkpoint frequency;
- lineage control;
- failure recovery.

Explain why:

```text
cache everything
```

is not a valid architecture.

---

### Architecture 4 — Cache vs Checkpoint vs Parquet

A team reports:

> "Our pipeline is slow because the lineage is enormous, and the same intermediate is reused by several jobs."

Evaluate:

```text
cache
checkpoint
localCheckpoint
Parquet
```

A strong answer should recognize that the requirements may need more than one mechanism:

```text
checkpoint
+
cache
```

within one application, plus:

```text
Parquet
```

for cross-job durability.

---

### Architecture 5 — Production Cache Regression

A pipeline was changed to add five caches.

After deployment:

- memory pressure increased;
- executor failures increased;
- total runtime worsened.

Design an investigation.

Required evidence:

- cached datasets;
- cached fraction;
- memory/disk usage;
- executor behavior;
- reuse counts;
- wall time;
- shuffle;
- spill;
- task distribution.

The expected architecture response is not:

> "Use more memory."

It is:

> **Determine whether each cache creates enough saved computation to justify its resource cost.**

---

### Architecture 6 — Long-Running Spark Application

A long-running application processes multiple datasets throughout its lifetime.

Design a cache lifecycle.

Include:

```text
persist
  ↓
materialize
  ↓
reuse
  ↓
unpersist
```

Discuss:

- cache ownership;
- cleanup;
- memory pressure;
- monitoring;
- accidental cache accumulation;
- executor loss;
- recomputation.

---

### Architecture 7 — Cross-Job Intermediate

Five independent jobs require the same expensive intermediate.

Should all five jobs depend on runtime cache?

Explain:

```text
cache
vs
Parquet/table
```

The durable artifact is generally the stronger architectural abstraction when cross-job lifecycle is required.

---

### Architecture 8 — Memory-Constrained Cluster

A frequently reused dataset is too large for comfortable memory retention.

Compare:

```text
MEMORY_AND_DISK
DISK_ONLY
Parquet
```

Your answer must discuss:

- reuse frequency;
- memory pressure;
- disk I/O;
- durability;
- restart behavior;
- actual measurements.

---

## 56. Study Loop

Use the Module 2.14 study loop:

```text
READ
  ↓
PREDICT
  ↓
WRITE IT
  ↓
EXPLAIN THE PLAN
  ↓
RUN SMALL
  ↓
RUN BIG
  ↓
READ SPARK UI
  ↓
CHANGE ONE THING
  ↓
MEASURE AGAIN
  ↓
WRITE IT DOWN
  ↓
EXPLAIN ALOUD
```

Apply it specifically to caching:

1. Predict whether a second action recomputes.
2. Run without persistence.
3. Inspect the execution.
4. Add `cache()`.
5. Run the first action.
6. Inspect Storage.
7. Run the second action.
8. Compare metrics.
9. Try another storage level.
10. Explain why the result changed.

---

## 57. Learning Checkpoints

### Beginner Checkpoint

- [ ] Explain why caching exists.
- [ ] Explain lazy materialization.
- [ ] Use `cache()`.
- [ ] Use `persist()`.
- [ ] Use `unpersist()`.

### Intermediate Checkpoint

- [ ] Explain `StorageLevel`.
- [ ] Compare `MEMORY_ONLY`, `MEMORY_AND_DISK`, and `DISK_ONLY`.
- [ ] Decide when to cache.
- [ ] Decide when not to cache.
- [ ] Explain caching after filtering.
- [ ] Read basic Storage-tab information.
- [ ] Explain memory pressure.

### Advanced Checkpoint

- [ ] Explain eviction and recomputation.
- [ ] Diagnose caching problems using Spark UI.
- [ ] Explain caching around shuffles.
- [ ] Explain iterative caching.
- [ ] Use `checkpoint()` appropriately.
- [ ] Explain `localCheckpoint()`.
- [ ] Distinguish cache from checkpoint.
- [ ] Distinguish cache from durable Parquet.
- [ ] Design a production caching strategy.
- [ ] Support the strategy with measurements.

---

## 58. Final Assessment

### Part A — Conceptual: 10 Questions

1. Why does Spark recompute a DataFrame?
2. What does `cache()` actually do?
3. Why is `cache()` lazy?
4. What is `StorageLevel`?
5. Compare `MEMORY_ONLY` and `MEMORY_AND_DISK`.
6. What is eviction?
7. What does `unpersist()` do?
8. What is checkpointing?
9. Why is Parquet different from cache?
10. Why is caching not a solution for skew?

**Passing standard:** Explain the execution model, not just API names.

---

### Part B — Code: 10 Questions

#### C1

```python
df.cache()
```

What happens immediately?

**Expected:** Persistence is requested; full computation is not automatically triggered.

#### C2

```python
df.cache()
df.count()
```

What happens on `count()`?

**Expected:** Required lineage executes and persisted partitions are materialized.

#### C3

```python
df.persist(StorageLevel.DISK_ONLY)
```

What changes?

**Expected:** The persistence strategy is explicitly disk-oriented.

#### C4

```python
df.unpersist()
```

What does it release?

**Expected:** Persisted blocks for that DataFrame, not source data.

#### C5

```python
df.createOrReplaceTempView("x")
```

Does this cache `df`?

**Expected:** No.

#### C6

```python
x = df
```

Does this cache `df`?

**Expected:** No.

#### C7

```python
df.checkpoint()
```

What is the main purpose?

**Expected:** Truncate lineage through a checkpoint boundary.

#### C8

```python
df.localCheckpoint()
```

What is the key caveat?

**Expected:** Weaker durability/recovery characteristics.

#### C9

```python
filtered = df.filter(...)
filtered.cache()
```

Why might this be better than caching `df`?

**Expected:** The filtered result may be smaller and more appropriate for reuse.

#### C10

```python
df.cache()
df.count()
df.count()
```

Why can the second count differ from the first?

**Expected:** The first action may materialize persistence; the second can reuse it.

---

### Part C — Debugging: 5 Scenarios

1. Only 60% of the cache is materialized.
2. Caching increased executor memory pressure.
3. A cached DataFrame is never reused.
4. A developer expects cache to survive application restart.
5. An iterative pipeline still has huge lineage after caching.

For each, explain:

```text
Symptom
→ Diagnosis
→ Evidence
→ Correction
→ Validation
```

---

### Part D — Performance: 5 Scenarios

1. `MEMORY_ONLY` is faster but causes pressure.
2. `MEMORY_AND_DISK` is slower but stable.
3. `DISK_ONLY` saves memory but increases read time.
4. Parquet adds I/O but enables cross-job reuse.
5. Cache reduces repeated work but total runtime increases.

For each, select a strategy only after discussing:

- reuse;
- storage;
- memory;
- durability;
- measured cost.

---

### Part E — Architecture: 5 Scenarios

1. Five gold branches share one expensive silver result.
2. Multiple jobs need the same intermediate.
3. An iterative pipeline has long lineage.
4. A long-running application accumulates many caches.
5. A production cache change causes executor failures.

Passing requires a defensible production decision with evidence.

---

## 59. Glossary

**Cache** — A runtime persistence mechanism used to retain computed data for reuse.

**Persist** — Explicitly request persistence with a chosen storage level.

**StorageLevel** — A specification describing how persisted data is stored.

**MEMORY_ONLY** — Persist using memory-oriented storage without disk fallback at the requested level.

**MEMORY_AND_DISK** — Persist using memory when possible and disk when needed.

**DISK_ONLY** — Persist using disk rather than retaining the persisted representation in memory.

**Serialization** — Encoding data into a representation suitable for storage or transfer.

**Replication** — Keeping additional copies of persisted blocks.

**Materialization** — The act of executing the lazy computation and producing concrete partitions.

**Lazy Evaluation** — Deferring execution until an action requires results.

**Lineage** — The dependency history Spark can use to reconstruct partitions.

**Partition** — A distributed unit of data and parallel work.

**Cached Block** — A persisted partition/result stored according to a persistence strategy.

**Eviction** — Removal of persisted data from available cache/storage resources.

**Storage Memory** — Resources used for persisted/cached data and related storage functions.

**Execution Memory** — Resources used during active computation, such as aggregation and shuffle operations.

**Recomputation** — Re-executing lineage to reconstruct a missing partition.

**`unpersist()`** — Requests release of persisted blocks.

**Checkpoint** — A materialized boundary that truncates lineage.

**`localCheckpoint()`** — Local lineage truncation with weaker durability characteristics.

**Durable Checkpoint** — A checkpoint written to a suitable persistent/shared checkpoint location.

**Parquet Materialization** — Writing an intermediate DataFrame as a durable Parquet dataset.

**Storage Tab** — Spark UI area used to inspect persisted data.

**Executors Tab** — Spark UI area used to inspect executor resource and task behavior.

**Warm Action** — An action performed after relevant persisted data has already been materialized.

**Cold Action** — An action performed before the relevant persisted data is available.

---

## 60. Summary

The complete mental model is:

```text
LAZY EVALUATION
      ↓
REUSED DATAFRAME
      ↓
WITHOUT PERSISTENCE
      ↓
RECOMPUTATION
      ↓
WASTED COMPUTE
      ↓
CACHE / PERSIST
      ↓
MATERIALIZE
      ↓
REUSE PERSISTED PARTITIONS
```

Then add resource reality:

```text
PERSIST
  ↓
STORAGE COST
  ↓
MEMORY / DISK PRESSURE
  ↓
POSSIBLE EVICTION
  ↓
POSSIBLE RECOMPUTATION
```

And distinguish the three major strategies:

```text
RECOMPUTE
→ no storage cost, but repeated compute

CACHE / PERSIST
→ fast runtime reuse within an application,
  but not durable

CHECKPOINT
→ truncate lineage

PARQUET
→ durable, shareable materialization
```

The production decision is:

```text
Is the result reused?
        ↓
How expensive is recomputation?
        ↓
How large is the result?
        ↓
How much resource capacity exists?
        ↓
What persistence level fits?
        ↓
Does it need durability?
        ↓
Would checkpointing solve a lineage problem?
        ↓
MEASURE
        ↓
VALIDATE
        ↓
KEEP / CHANGE / REMOVE
```

---

## 61. Topic Completion Standard

Do not consider Topic 10 complete until you can explain, without notes:

```text
Why does caching exist?
        ↓
How does lazy evaluation create recomputation?
        ↓
What does cache() do?
        ↓
Why is cache() lazy?
        ↓
What does persist() add?
        ↓
What is StorageLevel?
        ↓
How do memory, disk, serialization and replication differ?
        ↓
What is the modern DataFrame default?
        ↓
When is the cache materialized?
        ↓
How do cached partitions relate to partitions?
        ↓
When should I cache?
        ↓
When should I not cache?
        ↓
What happens under memory pressure?
        ↓
What is eviction?
        ↓
Why can Spark recompute an evicted partition?
        ↓
How do I use unpersist()?
        ↓
How do I inspect the Storage tab?
        ↓
How do I investigate Executors?
        ↓
How does cache interact with shuffle?
        ↓
How does cache interact with skew?
        ↓
How does cache help multiple branches?
        ↓
How does cache help iterative workloads?
        ↓
Why might checkpointing be necessary?
        ↓
What is the difference between checkpoint() and localCheckpoint()?
        ↓
What is the difference between cache and checkpoint?
        ↓
What is the difference between cache and Parquet?
        ↓
What is the difference between cache and a temp view?
        ↓
What is the difference between cache and a Python variable?
        ↓
How do I benchmark caching?
        ↓
How do I make the production decision?
```

The final professional skill is:

> **Do not ask "Can I cache this?" Ask "What repeated computation will persistence eliminate, what will it cost, what lifecycle do I need, and what evidence proves the decision is worthwhile?"**

---

## 62. Final Self-Review

- [ ] `cache()` is explained.
- [ ] `persist()` is explained.
- [ ] `unpersist()` is explained.
- [ ] Caching is clearly lazy.
- [ ] StorageLevel is deeply explained.
- [ ] `MEMORY_ONLY` is covered.
- [ ] `MEMORY_AND_DISK` is covered.
- [ ] `DISK_ONLY` is covered.
- [ ] Serialization variants are explained.
- [ ] Replication variants are explained.
- [ ] Modern DataFrame default behavior is addressed.
- [ ] Materialization is explained.
- [ ] Cache lifecycle is explained.
- [ ] When to cache is explained.
- [ ] When not to cache is explained.
- [ ] Memory pressure is explained.
- [ ] Eviction is explained.
- [ ] Recomputation is explained.
- [ ] Storage tab is covered.
- [ ] Executors tab caching investigation is covered.
- [ ] Caching and partitions are connected.
- [ ] Caching and shuffles are connected.
- [ ] Caching and skew are distinguished.
- [ ] Iterative workloads are covered.
- [ ] `checkpoint()` is covered.
- [ ] `localCheckpoint()` is covered.
- [ ] Cache vs checkpoint is covered.
- [ ] Cache vs Parquet is covered.
- [ ] Temp view vs cache is covered.
- [ ] Python variable vs cache is covered.
- [ ] Performance measurement is covered.
- [ ] No benchmark numbers are fabricated.
- [ ] At least 7 substantial coding examples exist.
- [ ] The required caching lab is included.
- [ ] At least 10 debugging exercises exist.
- [ ] Exactly 40 practice questions exist.
- [ ] Exactly 40 interview questions exist.
- [ ] At least 6 architecture scenarios exist.
- [ ] At least 15 misconceptions exist.
- [ ] Learning checkpoints exist.
- [ ] Final assessment exists.
- [ ] Glossary exists.
- [ ] Beginner → intermediate → advanced progression is clear.
- [ ] Spark 4.x awareness is maintained.
- [ ] Later topics are connected without being deeply duplicated.
- [ ] No benchmark result is invented.
- [ ] No unrelated file is modified.

---

## 63. Final Takeaway

Caching is not a performance button.

It is a resource-allocation decision.

The mature Spark engineer thinks in this sequence:

```text
COMPUTATION
    ↓
REUSE
    ↓
COST OF RECOMPUTATION
    ↓
COST OF STORAGE
    ↓
RESOURCE PRESSURE
    ↓
PERSISTENCE LEVEL
    ↓
MATERIALIZATION
    ↓
OBSERVABILITY
    ↓
MEASUREMENT
    ↓
CORRECTNESS
    ↓
PRODUCTION DECISION
```

The most important distinction is:

```text
CACHE / PERSIST
→ reuse computed data

CHECKPOINT
→ truncate lineage

PARQUET / DURABLE DATASET
→ preserve an intermediate beyond the application lifecycle
```

A production-quality decision is therefore not:

```python
df.cache()
```

It is:

```text
I know what is being recomputed.
I know how often it is reused.
I know how much storage it requires.
I know what resource pressure it creates.
I know whether durability is required.
I measured the before/after behavior.
I validated correctness.
I can explain why this persistence strategy is justified.
```

That is the level of reasoning expected from a production Data Engineer working with PySpark.
