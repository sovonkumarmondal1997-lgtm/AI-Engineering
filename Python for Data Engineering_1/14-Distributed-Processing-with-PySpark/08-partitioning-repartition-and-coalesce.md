# Partitioning, Repartition and Coalesce

> **Module:** 14 — Distributed Processing with PySpark  
> **Topic:** 08 — Partitioning, `repartition()` and `coalesce()`  
> **Level:** Beginner → Production Data Engineer  
> **Prerequisites:** Topics 01–07 of this module

## 1. Learning Objectives

By the end of this chapter, you should be able to:

- explain what a Spark partition is in precise but simple language;
- explain why Spark partitions distributed data;
- connect **partition → task → executor → available task slots**;
- reason about partition count and parallelism without assuming that more partitions are always faster;
- inspect the number of partitions in a DataFrame;
- distinguish partition count from partition size;
- explain too few versus too many partitions;
- explain how input layout, transformations, shuffles, joins, aggregations, and configuration influence partitioning;
- explain what `repartition()` does and why it commonly introduces a shuffle;
- use `repartition(n)`, `repartition(column)`, and `repartition(n, column...)`;
- explain what `coalesce()` does and why it is primarily useful for reducing partitions;
- choose between `repartition()` and `coalesce()` based on the workload rather than habit;
- reason about partitioning around joins and aggregations;
- distinguish **execution partitioning** from **storage/table partitioning**;
- distinguish `repartition()` from `DataFrameWriter.partitionBy()`;
- understand hash and range partitioning conceptually;
- reason about output-file count and the small-file problem;
- estimate average partition size as a diagnostic mental model;
- design controlled partition experiments;
- diagnose partition-related performance problems;
- explain why partition tuning is workload-dependent;
- identify when later topics such as skew, AQE, Catalyst, caching, and Spark UI become relevant.

---

## 2. Prerequisites

This topic assumes that you already understand:

1. **Driver, executors, and cluster managers** — Topic 01.
2. **SparkSession and deployment configuration** — Topic 02.
3. **RDDs versus DataFrames** — Topic 03.
4. **Transformations, actions, lazy evaluation, jobs, stages, tasks, and shuffle boundaries** — Topic 04.
5. **DataFrame transformations** such as `select`, `filter`, and `withColumn` — Topic 05.
6. **Spark SQL and temporary views** — Topic 06.
7. **Joins, shuffle, and broadcast joins** — Topic 07.

The dependency chain is:

```text
Distributed Computing
        ↓
SparkSession / Configuration / Deploy Modes
        ↓
RDDs vs DataFrames
        ↓
Transformations / Actions / Lazy Evaluation
        ↓
DataFrame API
        ↓
Spark SQL
        ↓
Joins / Shuffle / Broadcast
        ↓
Partitioning / repartition / coalesce   ← YOU ARE HERE
        ↓
Data Skew / Salting
        ↓
Caching / Persistence
        ↓
UDFs
        ↓
Catalyst / Explain
        ↓
AQE
        ↓
Data Sources / Writes / Bucketing
        ↓
Spark UI / Debugging
        ↓
Testing
```

The goal here is **not** to memorize two APIs. The goal is to build a distributed-computing mental model and then use the APIs to deliberately influence data layout.

---

## 3. What Is a Partition?

A Spark partition is a **chunk of a distributed dataset that Spark can process as a unit of parallel work**.

A useful first mental model is:

```text
Dataset
   |
   +---- Partition 0
   +---- Partition 1
   +---- Partition 2
   +---- Partition 3
```

Instead of one giant dataset being processed by one worker operation at a time, Spark can divide the work.

For example:

```text
100 GB dataset

        ↓

P0   P1   P2   P3   P4   P5   P6   P7
```

Each partition contains some portion of the dataset.

### What a partition is not

A partition is **not**:

- a physical machine;
- an executor;
- a CPU core;
- a file in every situation;
- a table partition directory;
- a guarantee of equal data volume;
- a guarantee that all partitions execute simultaneously.

A partition is a **logical unit of distributed data processing** that participates in Spark's physical execution.

### The basic execution relationship

For a typical stage:

```text
Partition
    ↓
  Task
    ↓
Executor
    ↓
CPU / memory / local resources
```

A task generally processes one partition for a stage.

That simple relationship is foundational for understanding partition tuning.

---

## 4. Why Spark Uses Partitions

Spark is designed to process datasets that may be much larger than one machine's memory or compute capacity.

Partitions let Spark divide work across a cluster.

Imagine a 1 TB dataset.

Without distributed partitioning, you could conceptually have:

```text
1 TB
 ↓
one processing unit
```

With distributed execution:

```text
1 TB
 ↓
+--------+--------+--------+--------+
|   P0   |   P1   |   P2   |   P3   |
+--------+--------+--------+--------+
|   P4   |   P5   |   P6   |   P7   |
+--------+--------+--------+--------+
```

Different tasks can process different partitions concurrently when cluster capacity allows.

Partitions therefore influence:

- parallelism;
- task count;
- task duration;
- memory pressure;
- CPU utilization;
- network movement;
- shuffle behavior;
- output-file count;
- downstream read behavior.

The critical lesson is:

> **Partitioning is a distributed execution mechanism, not merely a row-count setting.**

---

## 5. Partition as a Unit of Parallelism

Suppose a stage has:

```text
4 partitions
```

and the cluster can currently run approximately:

```text
2 tasks concurrently
```

A simplified execution picture is:

```text
Wave 1:
Task(P0)  Task(P1)

Wave 2:
Task(P2)  Task(P3)
```

Now suppose there are 8 partitions and approximately 4 available task slots:

```text
Wave 1:
P0 P1 P2 P3

Wave 2:
P4 P5 P6 P7
```

This does **not** mean Spark uses a simplistic one-task-per-core permanent mapping. Scheduling, locality, executor capacity, speculative execution, resource profiles, and other runtime behavior can affect actual execution.

The useful mental model is:

> **More partitions can expose more units of work, but useful parallelism is bounded by available resources and the workload.**

This immediately explains why too few partitions can underutilize a cluster.

---

## 6. Partitions, Tasks, Executors and Cores

Consider:

```text
Cluster
├── Executor A
│   ├── task slot
│   ├── task slot
│   ├── task slot
│   └── task slot
├── Executor B
│   ├── task slot
│   ├── task slot
│   ├── task slot
│   └── task slot
├── Executor C
│   ├── task slot
│   ├── task slot
│   ├── task slot
│   └── task slot
└── Executor D
    ├── task slot
    ├── task slot
    ├── task slot
    └── task slot
```

Conceptually there may be about 16 concurrently usable task slots.

If a stage has only four partitions:

```text
P0 P1 P2 P3
```

there may not be enough independent work to keep all available capacity busy for that stage.

If a stage has an extremely large number of tiny partitions, the opposite problem can occur:

```text
P0 P1 P2 P3 ... P999999
```

Now the scheduler has an enormous number of small units of work.

The correct question is therefore not:

> "How many partitions should every DataFrame have?"

It is:

> "For this workload, how much useful parallel work should Spark expose, and how much data should each task process?"

---

## 7. Understanding Partition Count

Partition count is simply the number of partitions in a distributed dataset at a particular point in the execution lineage.

For example:

```text
Partition count = 8
```

means the dataset currently has eight partitions.

It does **not** mean:

```text
8 machines
8 executors
8 cores
8 files
8 GB
```

Those are different concepts.

Partition count matters because it affects the number of tasks generated for relevant stages.

### Too few partitions

Potential consequences:

- insufficient parallelism;
- large tasks;
- long-running tasks;
- poor resource utilization;
- higher memory pressure per task;
- potentially larger spill behavior.

### Too many partitions

Potential consequences:

- scheduling overhead;
- many tiny tasks;
- task startup overhead;
- excessive metadata;
- tiny output files when writing;
- inefficient work granularity.

The correct partition count is therefore **workload-dependent**.

---

## 8. Inspecting Partitions

For learning and diagnostics, you can inspect the number of partitions of a DataFrame through its underlying RDD:

```python
num_partitions = df.rdd.getNumPartitions()

print(f"Partitions: {num_partitions}")
```

This is useful for understanding the physical data layout.

It does **not** mean that normal DataFrame processing should be rewritten as RDD processing.

For ordinary production transformations, continue using DataFrame/Spark SQL APIs.

### Important distinction

This:

```python
df.rdd.getNumPartitions()
```

is an inspection technique.

It is not a recommendation to convert the entire application to:

```python
df.rdd
```

The DataFrame API remains the preferred structured-data abstraction for the workloads covered by this module.

---

## 9. Creating DataFrames and Observing Partitions

A small educational example:

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("partition-basics")
    .master("local[*]")
    .getOrCreate()
)

df = spark.range(0, 1_000_000)

print("Partitions:", df.rdd.getNumPartitions())
```

The exact partition count depends on how the DataFrame is created and the Spark environment.

Do not build your mental model around a hard-coded number from one local machine.

### Better learning habit

Whenever you experiment:

```python
print("Partition count:", df.rdd.getNumPartitions())
```

then record what happened.

Do not assume that the same number will appear on a different cluster or for a different source.

---

## 10. `getNumPartitions()`

The method:

```python
df.rdd.getNumPartitions()
```

answers:

> "How many partitions does this RDD representation currently expose?"

For a DataFrame, it is useful as a practical educational diagnostic.

Example:

```python
before = df.rdd.getNumPartitions()

df2 = df.repartition(20)

after = df2.rdd.getNumPartitions()

print("Before:", before)
print("After:", after)
```

Remember that `repartition()` is lazy. Creating `df2` does not mean the data has already been physically shuffled.

The partition metadata and the eventual execution are related but should not be confused.

---

## 11. How Spark Determines Partitions

Partition counts can come from several sources.

Conceptually consider:

```text
Data source
    +
Existing partitioning
    +
File layout
    +
Transformations
    +
Shuffle operations
    +
Spark configuration
    +
Join / aggregation behavior
        ↓
Current execution partitioning
```

There is no single universal setting that controls every partition in every situation.

Relevant influences include:

- how the input source is split;
- existing RDD/DataFrame partitioning;
- file sizes and file layout;
- operations that preserve partition relationships;
- shuffle operations;
- join and aggregation execution;
- explicit `repartition()` / `coalesce()`;
- Spark configuration.

### `spark.sql.shuffle.partitions`

A particularly important configuration is:

```python
spark.conf.get("spark.sql.shuffle.partitions")
```

This configuration relates to the number of partitions used by relevant shuffle operations for Spark SQL/DataFrame workloads.

It is **not**:

> "the number of partitions in every DataFrame."

That distinction is critical.

---

## 12. Shuffle Partitions

Connect this topic to Topic 07:

```text
Existing partitions
        |
        v
      Shuffle
        |
        v
Shuffle output partitions
```

A shuffle redistributes records according to the requirements of the downstream operation.

For example, a grouping operation:

```python
df.groupBy("customer_id").count()
```

may require records with the same grouping key to be brought together.

Conceptually:

```text
Before:

P0 → customer A, B, C
P1 → customer B, D
P2 → customer A, D

             |
             | shuffle by customer_id
             v

P0' → all records for selected hash buckets
P1' → all records for selected hash buckets
...
```

The number of shuffle partitions is influenced by Spark configuration and execution decisions.

Do not confuse:

```text
current DataFrame partition count
```

with:

```text
configured shuffle partition count
```

They are related concepts, not interchangeable labels.

---

## 13. Partition Size

Partition count alone is not enough.

Suppose two datasets both have:

```text
100 partitions
```

Dataset A:

```text
10 GB / 100 partitions
≈ 100 MB average
```

Dataset B:

```text
1 TB / 100 partitions
≈ 10 GB average
```

The partition counts are identical, but the processing characteristics can be radically different.

A useful rough mental model is:

```text
Average partition size
≈
Total data volume / partition count
```

For example:

```text
100 GB
÷
100 partitions
≈
1 GB average
```

This is only an approximation.

Actual partition sizes can differ because of:

- key distribution;
- source file layout;
- filtering;
- row width;
- compression;
- shuffle behavior;
- partitioning strategy;
- skew.

Therefore:

> **Partition count is not a substitute for understanding partition size.**

---

## 14. Too Few Partitions

Imagine:

```text
1 TB dataset
4 partitions
```

Conceptually:

```text
P0 → very large
P1 → very large
P2 → very large
P3 → very large
```

If a cluster has many available task slots, only four independent tasks are available for that stage.

Potential consequences:

### 14.1 Poor parallelism

The cluster may have capacity that the workload cannot use.

### 14.2 Large tasks

Each task may process a very large amount of data.

### 14.3 Memory pressure

Larger tasks can increase pressure on executor memory and intermediate data structures.

### 14.4 Long-running tasks

A stage may take as long as its slowest substantial task, depending on the workload.

### 14.5 Underutilization

You can have an expensive cluster with resources sitting idle while a small number of tasks do large amounts of work.

---

## 15. Too Many Partitions

Now imagine:

```text
1 GB dataset
100,000 partitions
```

This may create:

```text
very small tasks
very small tasks
very small tasks
...
```

Potential problems:

- scheduling overhead;
- task startup overhead;
- excessive task metadata;
- poor work granularity;
- many output files;
- downstream metadata overhead.

The key principle is:

> **More partitions does not automatically mean more performance.**

A partition should represent a useful unit of work.

---

## 16. `repartition()`

The DataFrame API provides:

```python
df.repartition(...)
```

A repartition operation creates a new DataFrame with a changed partitioning arrangement.

For example:

```python
df2 = df.repartition(20)
```

Conceptually:

```text
Existing layout
      |
      v
repartition(20)
      |
      v
New layout with 20 partitions
```

Important properties:

- it returns a new DataFrame;
- transformations are lazy;
- it can change both count and distribution;
- it commonly requires redistribution/shuffle;
- it should be used deliberately.

### Why is it expensive?

If records must move between executors:

```text
Existing partitions
       |
       v
Data redistribution
       |
       +--> network transfer
       +--> serialization
       +--> memory
       +--> possible disk spill
       |
       v
New partitions
```

That cost can be justified when the resulting layout materially improves the downstream workload.

It is wasteful when introduced without a reason.

---

## 17. `repartition(n)`

Basic syntax:

```python
df2 = df.repartition(100)
```

This requests a DataFrame with 100 partitions.

Example:

```python
before = df.rdd.getNumPartitions()

df2 = df.repartition(100)

after = df2.rdd.getNumPartitions()

print("Before:", before)
print("After:", after)
```

The important conceptual point is:

```text
repartition(100)
```

is not:

```text
"make the cluster use 100 CPUs"
```

It means:

> "Create a new partitioning arrangement with 100 partitions."

Whether that is beneficial depends on the cluster and workload.

---

## 18. Repartition to Increase Partitions

Example:

```python
df2 = df.repartition(100)
```

Increasing partitions can be useful when:

- the current dataset has too few partitions;
- tasks are excessively large;
- available cluster capacity is underutilized;
- downstream processing benefits from finer work units;
- output parallelism needs deliberate adjustment.

But increasing partitions can introduce:

- shuffle;
- network movement;
- serialization;
- scheduler overhead;
- additional task overhead.

Therefore:

```text
Need more useful parallel work?
        ↓
Consider repartition
        ↓
Measure
```

Do not use:

```python
df.repartition(10_000)
```

simply because 10,000 sounds "highly parallel."

---

## 19. Repartition to Decrease Partitions

You can also write:

```python
df2 = df.repartition(10)
```

even if the original DataFrame had more partitions.

This is different from `coalesce()`.

A reduction using `repartition()` can still involve a shuffle:

```text
Many existing partitions
        |
        v
   repartition(10)
        |
        v
Redistribute records
        |
        v
10 target partitions
```

This can be useful when you specifically want a more globally redistributed layout.

For example, if the current partition distribution is poor, simply reducing partition count without redistribution may leave uneven work.

---

## 20. Repartition by Column

PySpark supports:

```python
df.repartition("customer_id")
```

and:

```python
df.repartition(50, "customer_id")
```

The second form says conceptually:

```text
Target partition count = 50
Partition using customer_id
```

This is useful when a downstream workload is organized around a key.

Conceptually:

```text
customer_id
     |
     v
Partitioning function
     |
     +----> P0
     +----> P1
     +----> P2
     +----> P3
```

Records are assigned according to a partitioning function.

For a hash-oriented distribution, related keys are directed toward corresponding partition destinations.

### Important caveat

Do not conclude:

> "If I repartition by the join key, every future join is automatically shuffle-free."

That is too strong.

Actual execution depends on:

- both sides' distribution;
- join strategy;
- upstream transformations;
- optimizer decisions;
- runtime statistics;
- other execution details.

This topic builds the foundation; later topics will go deeper into optimization.

---

## 21. Repartition by Multiple Columns

Example:

```python
df2 = df.repartition(
    50,
    "country",
    "customer_id"
)
```

Conceptually, the partitioning function considers the combination of:

```text
(country, customer_id)
```

This can be useful when the workload naturally groups around a compound key.

However, the choice has trade-offs.

Consider:

```text
country
+
customer_id
```

The combined key may have high cardinality and a different distribution from either individual column.

Do not choose multiple partitioning keys automatically.

Ask:

1. What downstream operation needs this layout?
2. How are the keys distributed?
3. Will the layout actually reduce useful data movement?
4. What is the cost of creating it?

---

## 22. Repartitioning and Shuffle

Why can `repartition()` be expensive?

Suppose:

```text
P0 P1 P2 P3
```

becomes:

```text
P0' P1' P2' P3' P4'
```

Records may need to move between worker processes:

```text
P0 ----\
P1 -----\ 
P2 ------> shuffle --> P0' P1' P2' P3' P4'
P3 -----/
```

The operation can involve:

- serialization;
- network I/O;
- memory buffering;
- disk spill;
- shuffle bookkeeping;
- downstream task scheduling.

This is why repartitioning should have a workload-driven reason.

---

## 23. `coalesce()`

The DataFrame API also provides:

```python
df.coalesce(n)
```

Its primary practical purpose is to **reduce the number of partitions without a full redistribution in the typical reduction case**.

Example:

```python
df2 = df.coalesce(10)
```

Conceptually:

```text
Before:

P0 P1 P2 P3 P4 P5 P6 P7

             |
             | coalesce(4)
             v

After:

P0'   P1'   P2'   P3'
```

A simplified mental model:

```text
P0 + P1  → P0'
P2 + P3  → P1'
P4 + P5  → P2'
P6 + P7  → P3'
```

This is deliberately simplified. Actual physical behavior can depend on the lineage and execution plan.

The key idea is:

> **Coalesce can reduce partition count while avoiding a full global redistribution.**

---

## 24. `coalesce(n)`

Example:

```python
df2 = df.coalesce(10)
```

If the DataFrame already has many partitions, this can be useful before writing a relatively small output dataset.

For example:

```python
df.coalesce(10).write.parquet(output_path)
```

But there is an important trade-off:

> Coalesce does not perform the same global balancing work as repartition.

Therefore, if the input partitions are uneven, coalescing them can preserve or worsen uneven work distribution.

---

## 25. Coalesce and Data Movement

A simplified view:

```text
Existing:

P0 P1 P2 P3 P4 P5

   |  |  |  |  |  |
   +--+  +--+  +--+
     ↓     ↓     ↓
    P0'   P1'   P2'
```

The important difference from a full repartition is that Spark can combine existing partition groups without globally redistributing every record.

This can make a reduction cheaper.

However:

```text
Cheaper movement
      ≠
Perfectly balanced partitions
```

If the original partitions contain very different amounts of data, the resulting coalesced partitions can also be uneven.

---

## 26. Repartition vs Coalesce

| Feature | `repartition()` | `coalesce()` |
|---|---|---|
| Changes partition count | Yes | Yes, primarily downward |
| Can increase partitions | Yes | Not the intended mechanism |
| Can decrease partitions | Yes | Yes |
| Redistributes data | Yes | Limited for typical reduction |
| Full shuffle | Typically yes | Typically avoided for reduction |
| Can rebalance distribution | Yes | Limited |
| Typical use | Controlled redistribution | Reduce partitions |
| Relative cost for reduction | Potentially higher | Usually lower |
| Useful before a write | Sometimes | Often for controlled reduction |
| Best question to ask | "Do I need redistribution?" | "Can I safely combine existing partitions?" |

Do not memorize the table without understanding the reason.

### The decision rule

Use:

```python
repartition(...)
```

when you need controlled redistribution or need to increase partitions.

Use:

```python
coalesce(...)
```

primarily when you want to reduce partitions and do not need a full rebalance.

---

## 27. Increasing Partitions

If you need more partitions, the practical tool is:

```python
df.repartition(100)
```

not:

```python
df.coalesce(100)
```

The purpose of `coalesce()` is not to serve as the general mechanism for increasing partition count.

A useful API rule:

```text
Need controlled increase?
        ↓
   repartition()
```

---

## 28. Decreasing Partitions

There are two main choices.

### Option A — `repartition()`

```python
df.repartition(20)
```

Potential benefit:

- global redistribution;
- potentially better balance.

Potential cost:

- shuffle;
- network movement;
- serialization;
- execution overhead.

### Option B — `coalesce()`

```python
df.coalesce(20)
```

Potential benefit:

- generally less movement for reduction;
- often useful before a write.

Potential cost:

- less ability to rebalance;
- resulting partitions may be uneven.

So the question is not simply:

> "Which API is faster?"

It is:

> "Do I need redistribution, or do I only need fewer partitions?"

---

## 29. Partitioning Before and After Joins

Topic 07 introduced joins and shuffle.

Partitioning matters because joins often require records with the same key to be brought together.

Conceptually:

```text
Orders
customer_id
    |
    | distribution
    v
P0 P1 P2 P3

Customers
customer_id
    |
    | distribution
    v
P0 P1 P2 P3
```

If the relevant data is already organized compatibly, some downstream data movement may be reduced.

But do not manually repartition both sides of every join.

For example, this is not automatically a best practice:

```python
left = left.repartition("customer_id")
right = right.repartition("customer_id")

joined = left.join(right, "customer_id")
```

Those repartitions themselves can be expensive.

A production engineer asks:

1. What is the current partitioning?
2. Is a shuffle already required?
3. Is the join small-side broadcastable?
4. Is the data reused later?
5. Is the repartition cost amortized?
6. What does measurement show?

Later topics cover optimizer and AQE behavior in more depth.

---

## 30. Partitioning and Aggregations

Consider:

```python
result = (
    df.groupBy("customer_id")
      .count()
)
```

Grouping by `customer_id` can require records to be redistributed according to that grouping key.

Conceptually:

```text
Input partitions
      |
      v
Shuffle by customer_id
      |
      v
Shuffle partitions
      |
      v
Aggregation
```

This is why partitioning is central to distributed aggregation.

But again:

> Do not assume that manually calling `repartition("customer_id")` before every aggregation is automatically beneficial.

If the aggregation itself requires a shuffle, an extra repartition may simply add another expensive operation.

---

## 31. Partitioning and Output Files

Partition count can affect output-file count.

A simplified model is:

```text
Spark partitions
       |
       v
write tasks
       |
       v
output files
```

Therefore:

```text
many partitions
      ↓
many write tasks
      ↓
potentially many output files
```

For example:

```python
df.coalesce(10).write.mode("overwrite").parquet(output_path)
```

can be used when reducing output parallelism is appropriate.

Or:

```python
df.repartition(10).write.mode("overwrite").parquet(output_path)
```

can be used when controlled redistribution is also desired.

These are **not equivalent in cost or distribution**.

### Important qualification

The exact number and layout of output files depend on the file format and write behavior. Do not treat:

```text
number of Spark partitions == guaranteed number of output files
```

as an absolute rule.

The useful production relationship is:

> **Execution partition count strongly influences the number of concurrent write tasks and therefore can influence output-file count.**

---

## 32. Small Files

The small-file problem occurs when a dataset is represented by a very large number of tiny files.

Potential consequences include:

- metadata overhead;
- slower directory/object listing;
- more storage requests;
- inefficient downstream scans;
- more task scheduling;
- operational complexity.

For example:

```text
10 GB output

Option A:
20 reasonably sized files

Option B:
100,000 tiny files
```

Both can contain the same logical data, but their operational characteristics can be very different.

Partition count is one factor contributing to output-file count.

Do not solve the small-file problem blindly with:

```python
df.coalesce(1)
```

Creating one giant file can replace one problem with another:

- reduced write parallelism;
- a potentially huge task;
- a bottleneck;
- poor downstream parallelism.

The correct target depends on the workload and storage system.

---

## 33. Choosing a Partition Count

There is no universal correct partition count.

Instead, reason through:

```text
Total data
    ↓
Approximate partition size
    ↓
Available task capacity
    ↓
Workload characteristics
    ↓
Shuffle requirements
    ↓
Output requirements
    ↓
Measured result
```

Ask:

1. How much data is being processed?
2. How many partitions currently exist?
3. How large are they approximately?
4. How many task slots are available?
5. Are tasks too large?
6. Are tasks too tiny?
7. Is a shuffle involved?
8. Is the data balanced?
9. Are there joins or aggregations?
10. Are we writing output?
11. Are output files too numerous?
12. Can the change be measured?

---

## 34. Partitioning by Key

Partitioning by key means that a partitioning function uses one or more columns to determine partition destinations.

Example:

```python
df.repartition("customer_id")
```

Conceptually:

```text
customer_id
     |
     v
Partitioning function
     |
     +---- P0
     +---- P1
     +---- P2
     +---- P3
```

The purpose is often to organize records around a key used by downstream processing.

Typical workloads include:

- joins;
- groupBy aggregations;
- key-oriented transformations.

### Important caveat

Partitioning by key does not guarantee uniform distribution.

For example:

```text
customer_id = 1
appears 900 million times

customer_id = 2
appears 10 times
```

A key-based partitioning strategy can still produce uneven work.

This is the conceptual bridge to Topic 09 on data skew.

---

## 35. Hash Partitioning Concept

Hash partitioning uses a hash-like function to map keys to partition destinations.

Conceptually:

```text
customer_id
     |
     v
  hash(key)
     |
     v
partition selection
```

A simplified conceptual formula is:

```text
partition_id = hash(key) mod N
```

where `N` is the number of target partitions.

This is a mental model, not a statement that every Spark implementation should be reduced to that exact formula.

### Why hash partitioning is useful

It can distribute many distinct keys across partitions.

For example:

```text
customer A → P2
customer B → P0
customer C → P3
customer D → P1
```

The objective is generally useful distribution.

### Why it is not perfect

Hash partitioning does not guarantee equal data volume.

If one key is extremely frequent, the partition receiving that key can become much larger.

That is data skew, which Topic 09 covers in depth.

---

## 36. Range Partitioning Concept

Range partitioning divides a domain into ranges.

Conceptually:

```text
P0 → customer_id 1–1000
P1 → customer_id 1001–2000
P2 → customer_id 2001–3000
```

Range partitioning can be useful for workloads involving:

- ordered data;
- range-oriented queries;
- ordered processing.

A range-based strategy can preserve useful ordering relationships better than an arbitrary hash distribution.

But range boundaries must be chosen intelligently.

If the data distribution is highly uneven, one range can still contain much more data than another.

---

## 37. Hash vs Range Partitioning

| Characteristic | Hash partitioning | Range partitioning |
|---|---|---|
| Distribution mechanism | Hash/key-based | Value ranges |
| Key locality | Same key maps consistently | Values in same range colocated |
| Ordering | Does not inherently preserve useful key order | Can preserve range ordering |
| Common use | Joins and aggregations | Range-oriented / ordered workloads |
| Balance | Depends on key/data distribution | Depends on range boundaries |
| Main risk | Hot keys / skew | Uneven ranges |
| Mental model | "Which bucket?" | "Which interval?" |

You do not need to memorize low-level implementation details at this stage.

You do need to understand that different partitioning strategies organize distributed work differently.

---

## 38. Partitioning Trade-offs

Partitioning decisions influence multiple resources at once.

```text
Partitioning Decision
        |
        +---- Parallelism
        |
        +---- Task Overhead
        |
        +---- Shuffle Cost
        |
        +---- Network
        |
        +---- Memory
        |
        +---- Disk Spill
        |
        +---- Output Files
        |
        +---- Downstream Read Performance
```

For example, increasing partitions can:

```text
increase useful parallelism
```

while also:

```text
increase task count
increase scheduling overhead
increase output-file count
```

Decreasing partitions can:

```text
reduce task count
reduce file count
```

while also:

```text
reduce parallelism
increase task size
```

This is why partition tuning is an optimization problem rather than a fixed rule.

---

## 39. Common Partitioning Mistakes

### Mistake 1 — Using `repartition()` everywhere

Bad pattern:

```python
df = df.repartition(100)
df = df.filter(...)
df = df.repartition(100)
df = df.join(...)
df = df.repartition(100)
```

Why problematic:

- repeated redistribution can be expensive;
- the requested partitioning may not be needed;
- each repartition adds complexity.

Correct approach:

- identify a concrete downstream reason;
- measure;
- retain only partition changes that provide value.

Production consequence:

> unnecessary shuffle can dominate the job.

---

### Mistake 2 — Assuming more partitions always means faster jobs

Bad assumption:

```text
100 partitions < 10,000 partitions
therefore 10,000 must be faster
```

Why wrong:

- tasks can become too small;
- scheduling overhead increases;
- output files can explode.

Correct approach:

- measure workload-specific results.

---

### Mistake 3 — Using `coalesce()` when redistribution is required

If partitions are badly unbalanced:

```python
df.coalesce(10)
```

may reduce the count without solving the underlying distribution problem.

Correct approach:

```python
df.repartition(10)
```

when a global redistribution is actually needed.

---

### Mistake 4 — Using `repartition()` only to reduce output files

This may introduce an expensive shuffle.

If the current distribution is already acceptable and the primary requirement is fewer output tasks, consider:

```python
df.coalesce(target)
```

and measure.

---

### Mistake 5 — Confusing execution and storage partitioning

These are different:

```python
df.repartition("country")
```

versus:

```python
df.write.partitionBy("country").parquet(path)
```

The first affects execution partitioning.

The second affects storage directory layout for supported writers.

---

### Mistake 6 — Ignoring executor/task capacity

If the cluster can run about 64 tasks concurrently and the stage has only four partitions, available capacity may be underused.

---

### Mistake 7 — Ignoring partition size

A count such as:

```text
100 partitions
```

does not tell you whether each partition contains 1 MB, 100 MB, or 10 GB.

---

### Mistake 8 — Assuming average size equals actual size

A dataset can average:

```text
1 GB/partition
```

while actual sizes look like:

```text
100 MB
200 MB
300 MB
...
50 GB
```

That is a distribution problem.

---

### Mistake 9 — Manually repartitioning both sides of every join

You can pay two shuffle costs before the join even does its own work.

Correct approach:

- understand the join;
- inspect current layout;
- consider broadcast;
- consider reuse;
- measure.

---

### Mistake 10 — Ignoring small-file consequences

A partition strategy that is acceptable for computation can still produce operationally poor storage output.

---

## 40. Debugging Partition Problems

A disciplined debugging workflow is:

```text
Observe
   ↓
Measure
   ↓
Form a hypothesis
   ↓
Change one thing
   ↓
Run the same workload
   ↓
Compare
   ↓
Keep or revert
```

### First diagnostic

```python
print("Partitions:", df.rdd.getNumPartitions())
```

### Then inspect the workload

Ask:

- How much data is being processed?
- What is the row width?
- Is there a shuffle?
- Is the workload a join?
- Is it an aggregation?
- Is the data being written?
- How many tasks are created?
- Are tasks tiny or large?
- Is distribution uneven?

### Controlled partition diagnostic

For educational investigation:

```python
def count_rows_per_partition(iterator):
    count = 0
    for _ in iterator:
        count += 1
    yield count

partition_counts = (
    df.rdd
      .mapPartitions(count_rows_per_partition)
      .collect()
)

print(partition_counts)
```

This gives one count per partition.

**Warning:** the `collect()` above collects only the small diagnostic result—the number of rows per partition—not the original dataset.

Do not do this:

```python
def inspect_partition(iterator):
    rows = list(iterator)
    yield len(rows)
```

on arbitrarily large production partitions. Materializing an entire partition into a Python list can create avoidable Python memory pressure.

If you use partition-level diagnostics, stream through the iterator and emit small summaries.

### Where to look next

Detailed task/stage/shuffle visualization belongs to Topic 15, Spark UI and debugging.

---

## 41. Production Partitioning Patterns

### Pattern A — Increase parallelism deliberately

When a workload has too few large tasks:

```python
df2 = df.repartition(target_partitions)
```

Then measure:

- runtime;
- task duration;
- executor utilization;
- shuffle cost.

---

### Pattern B — Reduce partitions before a controlled write

If a dataset is already reasonably distributed:

```python
df.coalesce(target_files).write.parquet(output_path)
```

This can reduce write-task count without requiring a full redistribution.

---

### Pattern C — Redistribute by a downstream key

When there is a concrete key-oriented workload:

```python
df2 = df.repartition("customer_id")
```

Use this only when the resulting organization has a measurable downstream benefit.

---

### Pattern D — Use a target count plus key

```python
df2 = df.repartition(
    100,
    "customer_id"
)
```

This provides controlled key-based distribution.

Again, it does not guarantee perfect balance.

---

### Pattern E — Avoid gratuitous repartitioning

If the workload is already performing well:

```python
df2 = df
```

may be the best partitioning decision.

No API call is required simply because partitioning is important.

---

## 42. Mini Project — Partition Tuning Lab

Build a small but production-oriented experiment using a synthetic transaction dataset.

### Dataset columns

```text
transaction_id
customer_id
product_id
country
transaction_date
quantity
unit_price
revenue
```

### Project objectives

You will:

1. Create a SparkSession.
2. Generate or load data.
3. Inspect the schema.
4. Inspect the current partition count.
5. Run a baseline transformation.
6. Measure baseline runtime.
7. Test several partition counts.
8. Compare the same workload across configurations.
9. Repartition by a key.
10. Demonstrate `coalesce()`.
11. Compare `repartition()` and `coalesce()`.
12. Write output.
13. Compare output-file counts.
14. Explain small-file implications.
15. Demonstrate execution partitioning versus storage partitioning.
16. Record actual observations.
17. Explain why no universal optimal partition count exists.

### Complete executable project

```python
from pathlib import Path
from time import perf_counter

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = (
    SparkSession.builder
    .appName("partition-tuning-lab")
    .master("local[*]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

data = [
    (1, 101, 1001, "India", "2026-01-01", 2, 100.0),
    (2, 102, 1002, "USA", "2026-01-02", 1, 250.0),
    (3, 101, 1003, "India", "2026-01-03", 5, 80.0),
    (4, 103, 1004, "UK", "2026-01-04", 3, 120.0),
    (5, 104, 1005, "USA", "2026-01-05", 4, 90.0),
]

columns = [
    "transaction_id",
    "customer_id",
    "product_id",
    "country",
    "transaction_date",
    "quantity",
    "unit_price",
]

df = spark.createDataFrame(data, columns)

df = df.withColumn(
    "revenue",
    F.col("quantity") * F.col("unit_price")
)

print("Schema:")
df.printSchema()

print("Initial partitions:", df.rdd.getNumPartitions())


def benchmark(label, dataframe):
    start = perf_counter()

    result = (
        dataframe
        .groupBy("country")
        .agg(
            F.sum("revenue").alias("total_revenue"),
            F.count("*").alias("transaction_count"),
        )
    )

    result.collect()

    elapsed = perf_counter() - start

    print(f"{label}: {elapsed:.4f} seconds")
    print(f"{label} partitions: {dataframe.rdd.getNumPartitions()}")

    return result


baseline = benchmark("baseline", df)

repartitioned_10 = df.repartition(10)
benchmark("repartition_10", repartitioned_10)

repartitioned_50 = df.repartition(50)
benchmark("repartition_50", repartitioned_50)

repartitioned_100 = df.repartition(100)
benchmark("repartition_100", repartitioned_100)

by_customer = df.repartition(10, "customer_id")
print(
    "By-customer partitions:",
    by_customer.rdd.getNumPartitions()
)

coalesced = repartitioned_50.coalesce(10)

print(
    "Before coalesce:",
    repartitioned_50.rdd.getNumPartitions()
)

print(
    "After coalesce:",
    coalesced.rdd.getNumPartitions()
)

output_dir = Path("partition_lab_output")

coalesced.write.mode("overwrite").parquet(
    str(output_dir / "coalesced")
)

repartitioned_10.write.mode("overwrite").parquet(
    str(output_dir / "repartitioned")
)

spark.stop()
```

### Important benchmark rule

The example intentionally does **not** provide fake timing numbers.

Run it in your environment and record:

```text
configuration
dataset size
partition count
runtime
task count
output file count
observations
```

A production benchmark is meaningful only when the workload and environment are real enough to represent the decision being made.

### Suggested experiment matrix

```text
Baseline
   |
   +--> 10 partitions
   |
   +--> 50 partitions
   |
   +--> 100 partitions
   |
   +--> key-based partitioning
   |
   +--> coalesce
```

For each run, record:

| Experiment | Partition count | Runtime | Output files | Notes |
|---|---:|---:|---:|---|
| Baseline | actual | record | record | baseline |
| Repartition 10 | 10 | record | record | record |
| Repartition 50 | 50 | record | record | record |
| Repartition 100 | 100 | record | record | record |
| Key-based | actual | record | record | record |
| Coalesce | target | record | record | record |

Never invent benchmark results.

---

## 43. Hands-On Labs

### Lab 1 — Inspect Current Partition Count

**Objective:** Learn to observe partition count.

**Setup:**

```python
df = spark.range(0, 1_000_000)
```

**Task:**

```python
print(df.rdd.getNumPartitions())
```

**Expected behavior:** You will observe a partition count determined by the local Spark environment and DataFrame construction.

**Hint:** Do not assume the count will be identical on another machine.

**Verification:** Explain why the result is not equal to the number of executors.

**Common mistake:** Assuming partition count is fixed globally.

---

### Lab 2 — Connect Partitions to Tasks

**Objective:** Connect partition count to stage work.

**Task:**

Create a DataFrame with multiple partitions and run:

```python
df.groupBy((F.col("id") % 10).alias("bucket")).count().collect()
```

Observe conceptually that a stage can create tasks associated with partitions.

**Expected behavior:** The action triggers execution.

**Hint:** Revisit Topic 04's jobs/stages/tasks model.

**Verification:** Explain why partitions expose units of work.

**Common mistake:** Saying one partition equals one executor.

---

### Lab 3 — Use `repartition(n)`

**Objective:** Change partition count.

```python
df2 = df.repartition(20)

print("Before:", df.rdd.getNumPartitions())
print("After:", df2.rdd.getNumPartitions())
```

**Expected behavior:** `df2` has the requested target partition count.

**Hint:** Creating `df2` is lazy.

**Verification:** Explain why data movement is not performed merely because the Python statement executed.

**Common mistake:** Treating a transformation as an immediate distributed job.

---

### Lab 4 — Increase Partition Count

**Objective:** Test whether additional parallelism helps.

Run the same workload using:

```python
df.repartition(10)
df.repartition(50)
df.repartition(100)
```

**Expected behavior:** Runtime will depend on workload and environment.

**Hint:** Record actual measurements.

**Verification:** Explain why 100 is not automatically better than 10.

**Common mistake:** Selecting the largest number without benchmarking.

---

### Lab 5 — Decrease Partition Count with `repartition()`

**Objective:** Understand that decreasing with `repartition()` can still shuffle.

Start with:

```python
df_many = df.repartition(100)
df_fewer = df_many.repartition(10)
```

**Expected behavior:** The second repartition requests a new layout and can redistribute data.

**Verification:** Explain the difference between "fewer partitions" and "fewer partitions without global redistribution."

**Common mistake:** Assuming all reductions are equivalent to `coalesce()`.

---

### Lab 6 — Use `coalesce()`

**Objective:** Reduce partitions with limited redistribution.

```python
df_many = df.repartition(100)
df_fewer = df_many.coalesce(10)

print(df_many.rdd.getNumPartitions())
print(df_fewer.rdd.getNumPartitions())
```

**Expected behavior:** The partition count is reduced.

**Hint:** Think "combine existing partitions."

**Verification:** Explain why coalesce can be cheaper than repartition for a reduction.

**Common mistake:** Assuming it perfectly balances the result.

---

### Lab 7 — Compare `repartition()` and `coalesce()`

**Objective:** Understand cost and distribution differences.

Compare:

```python
df.repartition(10)
```

with:

```python
df.coalesce(10)
```

using the same downstream action.

**Expected behavior:** The performance profile may differ.

**Hint:** Both return ten partitions, but they do not necessarily create the same physical data movement.

**Verification:** Explain why equal partition counts do not imply equal execution cost.

**Common mistake:** Comparing only final partition count.

---

### Lab 8 — Repartition by a Column

**Objective:** Understand key-based partitioning.

```python
df2 = df.repartition("customer_id")
```

Then inspect:

```python
print(df2.rdd.getNumPartitions())
```

**Expected behavior:** Spark uses a key-based partitioning strategy.

**Verification:** Explain why this can matter for later key-oriented operations.

**Common mistake:** Claiming every future join will be shuffle-free.

---

### Lab 9 — Repartition by Multiple Columns

**Objective:** Understand compound partitioning keys.

```python
df2 = df.repartition(
    20,
    "country",
    "customer_id"
)
```

**Expected behavior:** The target partitioning considers the combined key.

**Verification:** Explain when a compound key might be useful.

**Common mistake:** Adding many columns without a downstream reason.

---

### Lab 10 — Observe Output File Counts

**Objective:** Connect execution partitions to writes.

```python
output = "partition_output"

df.repartition(20).write.mode("overwrite").parquet(
    output + "/repartitioned"
)

df.repartition(20).coalesce(5).write.mode("overwrite").parquet(
    output + "/coalesced"
)
```

Inspect the generated files in your environment.

**Expected behavior:** The two workflows can produce different execution behavior and file layouts.

**Verification:** Explain why file count is influenced by partitioning but is not a universal one-to-one law.

**Common mistake:** Assuming every partition always maps to exactly one output file in every write scenario.

---

### Lab 11 — Execution Partitioning vs Storage Partitioning

**Objective:** Separate two commonly confused concepts.

Compare:

```python
df.repartition("country")
```

with:

```python
df.write.partitionBy("country").parquet(output_path)
```

**Expected behavior:** The first controls execution partitioning; the second controls supported output directory layout.

**Verification:** Explain why the APIs have similar words but different purposes.

**Common mistake:** Treating `partitionBy()` as a replacement for `repartition()`.

---

### Lab 12 — Partition-Tuning Experiment

**Objective:** Make a measured partition decision.

Test:

```text
baseline
10 partitions
50 partitions
100 partitions
key-based partitioning
coalesce
```

Record:

- runtime;
- partition count;
- task count;
- output file count;
- observations.

**Expected behavior:** Results will vary.

**Verification:** Write a one-paragraph conclusion that explains the best choice for your actual experiment without presenting it as a universal rule.

**Common mistake:** Choosing a configuration based on intuition alone.

---

## 44. Debugging Exercises

### Scenario 1 — Dataset Has Too Few Partitions

**Symptom:** A large dataset runs with only a few long-running tasks.

**Diagnosis:** Partition count may be too low for available cluster parallelism.

**Likely cause:** Input layout or upstream processing produced insufficient partitions.

**Corrective action:** Investigate and test a controlled `repartition()`.

**Explanation:** More useful partitions may expose additional parallel work, but the correct target must be measured.

---

### Scenario 2 — Excessive Number of Partitions

**Symptom:** A small dataset produces an enormous number of tiny tasks.

**Diagnosis:** Work granularity may be too fine.

**Likely cause:** Excessive partition count.

**Corrective action:** Test a lower partition count and compare runtime.

**Explanation:** Scheduling overhead can outweigh the benefit of additional parallelism.

---

### Scenario 3 — `repartition()` Makes the Job Slower

**Symptom:** A developer adds:

```python
df = df.repartition(500)
```

and runtime increases.

**Diagnosis:** The repartition itself may have introduced a costly shuffle without enough downstream benefit.

**Likely cause:** The original layout was already adequate.

**Corrective action:** Remove the repartition or test a more appropriate strategy.

**Explanation:** Redistribution has a cost.

---

### Scenario 4 — `coalesce()` Creates Uneven Work

**Symptom:** After:

```python
df2 = df.coalesce(10)
```

some tasks process substantially more data than others.

**Diagnosis:** Coalesce reduced partitions without globally balancing the records.

**Likely cause:** Uneven input partition sizes.

**Corrective action:** If balancing is necessary, investigate `repartition()` and measure.

**Explanation:** Coalesce is designed for cheaper reduction, not full global rebalancing.

---

### Scenario 5 — Too Many Small Output Files

**Symptom:** A modest dataset produces tens of thousands of files.

**Diagnosis:** Excessive output parallelism is a likely contributor.

**Likely cause:** High partition count at write time.

**Corrective action:** Investigate whether controlled reduction with `coalesce()` is appropriate.

**Explanation:** Reducing write tasks can reduce file count, but creating one file is not automatically desirable.

---

### Scenario 6 — `partitionBy()` Confused with `repartition()`

**Symptom:** A developer expects:

```python
df.write.partitionBy("country")
```

to change the DataFrame's execution partition count.

**Diagnosis:** Two different concepts were conflated.

**Likely cause:** Similar terminology.

**Corrective action:** Explain execution partitioning versus storage partitioning.

**Explanation:** `repartition()` affects execution data layout; `partitionBy()` affects output directory organization for supported writers.

---

### Scenario 7 — `spark.sql.shuffle.partitions` Misunderstood

**Symptom:** A developer changes:

```python
spark.conf.set(
    "spark.sql.shuffle.partitions",
    1000
)
```

and expects every DataFrame to have 1,000 partitions.

**Diagnosis:** The configuration is being treated as a universal partition-count setting.

**Likely cause:** Confusing shuffle partitioning with general execution partitioning.

**Corrective action:** Explain where shuffle partition configuration applies and inspect the actual DataFrame partition count separately.

**Explanation:** Input partitions, non-shuffle transformations, explicit repartitioning, and other mechanisms have their own behavior.

---

### Scenario 8 — Both Join Inputs Are Manually Repartitioned

**Symptom:** A join becomes slower after:

```python
left = left.repartition("customer_id")
right = right.repartition("customer_id")
```

**Diagnosis:** The manual repartitions may have introduced unnecessary shuffle.

**Likely cause:** Partitioning was changed without establishing a measurable benefit.

**Corrective action:** Compare against the original plan/workload and investigate the actual join requirements.

**Explanation:** Partitioning should support a concrete execution need.

---

### Scenario 9 — Reasonable Partition Count, Uneven Task Sizes

**Symptom:** There are 100 partitions, but one or two tasks are dramatically larger.

**Diagnosis:** Partition count is not the same as data balance.

**Likely cause:** Uneven key or data distribution.

**Corrective action:** Measure partition-level distribution and investigate data skew.

**Explanation:** Topic 09 will cover skew and salting in depth.

---

### Scenario 10 — Increasing Partitions Does Not Improve Runtime

**Symptom:** Changing from 50 to 200 partitions has little or negative effect.

**Diagnosis:** The workload may not be parallelism-limited.

**Likely causes:**

- I/O bottleneck;
- shuffle bottleneck;
- CPU characteristics;
- task overhead;
- already adequate parallelism;
- skew.

**Corrective action:** Measure the actual bottleneck before changing partition count again.

**Explanation:** Partition count is only one variable in distributed performance.

---

## 45. Practice Questions

Exactly **40** questions are provided below: 10 Basic, 10 Moderate, 10 Hard, and 10 Advanced.

### 10 Basic

#### B1. What is a Spark partition?

**Answer:** A partition is a chunk of a distributed dataset that Spark can process as a unit of parallel work.

**Why:** Spark uses partitions to divide distributed data into executable work units.

---

#### B2. What is the relationship between a partition and a task?

**Answer:** For a typical stage, one task processes one partition.

**Why:** The partition supplies the data unit and the task is the execution unit created to process it.

---

#### B3. Does one partition equal one executor?

**Answer:** No.

**Why:** An executor can process many tasks over time and may process multiple partitions concurrently according to its available task capacity.

---

#### B4. What does partition count represent?

**Answer:** The number of partitions in a dataset at a particular point in its execution lineage.

**Why:** It describes data-processing units, not machines, cores, or files.

---

#### B5. How can you inspect a DataFrame's partition count for learning or diagnostics?

**Answer:**

```python
df.rdd.getNumPartitions()
```

**Why:** It exposes the partition count of the underlying RDD representation.

---

#### B6. What is `repartition(20)` intended to do?

**Answer:** It creates a new DataFrame with a target partitioning arrangement of 20 partitions.

**Why:** Repartitioning can redistribute data to create the requested layout.

---

#### B7. What is `coalesce(10)` primarily used for?

**Answer:** Reducing the number of partitions, typically with less data movement than a full repartition.

**Why:** Coalesce can combine existing partitions without globally redistributing every record.

---

#### B8. Why can too few partitions be a problem?

**Answer:** They can limit parallelism and create large, long-running tasks.

**Why:** The cluster may have more task capacity than the stage has independent work units.

---

#### B9. Why can too many partitions be a problem?

**Answer:** They can create excessive scheduling and task overhead and can contribute to too many output files.

**Why:** More partitions create more work units, which are not free.

---

#### B10. Is more partitioning always faster?

**Answer:** No.

**Why:** The useful partition count depends on data volume, task size, cluster capacity, shuffle behavior, and workload.

---

### 10 Moderate

#### M1. What is the difference between `repartition(10)` and `coalesce(10)`?

**Answer:** Both can reduce a partition count, but `repartition()` generally redistributes data and can perform a shuffle, while `coalesce()` primarily combines existing partitions without a full redistribution.

**Why:** The choice depends on whether global rebalancing is required.

---

#### M2. Why can `repartition()` be expensive?

**Answer:** It can require records to move between workers, causing network transfer, serialization, memory use, and possible spill.

**Why:** Redistribution is a distributed operation.

---

#### M3. What does `spark.sql.shuffle.partitions` control?

**Answer:** It provides a partition-count setting for relevant SQL/DataFrame shuffle operations.

**Why:** It is specifically related to shuffle partitioning and is not a universal DataFrame partition-count setting.

---

#### M4. If a DataFrame has 100 partitions, does that mean it has 100 equally sized partitions?

**Answer:** No.

**Why:** Data distribution can be uneven due to source layout, keys, filters, and skew.

---

#### M5. What is a useful first approximation for average partition size?

**Answer:**

```text
average partition size
≈
total data volume / partition count
```

**Why:** It provides a rough mental model, but actual partition sizes can vary significantly.

---

#### M6. Why might `coalesce()` be useful before writing output?

**Answer:** It can reduce the number of write tasks and therefore can reduce output-file count without requiring a full redistribution.

**Why:** It is often cheaper when the existing distribution is already acceptable.

---

#### M7. What is the risk of using `coalesce()` on uneven partitions?

**Answer:** The resulting partitions can remain uneven or become more uneven.

**Why:** Coalesce does not perform the same global balancing as repartition.

---

#### M8. What does `df.repartition("customer_id")` communicate?

**Answer:** It requests key-based repartitioning using `customer_id`.

**Why:** A key-oriented layout can be useful for downstream operations involving that key.

---

#### M9. Why should you not manually repartition both sides of every join?

**Answer:** The repartitions themselves can introduce expensive shuffles without providing enough downstream benefit.

**Why:** Partitioning changes should be justified by the actual workload.

---

#### M10. Why can excessive partitions cause too many output files?

**Answer:** More execution partitions can create more concurrent write tasks, which can contribute to more output files.

**Why:** File count is influenced by the number of tasks writing the output.

---

### 10 Hard

#### H1. A cluster has many available task slots, but a 2 TB dataset has only four partitions. What is the conceptual problem?

**Answer:** The stage may expose insufficient parallel work to use the available task capacity, while each task may process a very large amount of data.

**Reasoning:** Partition count is limiting the number of independent work units.

---

#### H2. A 10 GB dataset produces 50,000 tiny output files. What should you investigate first?

**Answer:** Investigate the partition count at write time and why the workload is producing so many write tasks.

**Reasoning:** Excessive execution partitions can contribute to small-file problems, but the exact writer behavior and workload must also be inspected.

---

#### H3. Why can `repartition(10)` be more expensive than `coalesce(10)`?

**Answer:** `repartition(10)` can globally redistribute records, whereas `coalesce(10)` can reduce partitions by combining existing partition groups without a full shuffle.

**Reasoning:** Global redistribution costs network, serialization, and potentially spill resources.

---

#### H4. Explain the difference between `repartition("country")` and `write.partitionBy("country")`.

**Answer:** `repartition("country")` changes execution partitioning; `write.partitionBy("country")` controls storage directory layout for supported output formats.

**Reasoning:** Similar terminology describes two different layers.

---

#### H5. Why can a key-based partitioning strategy still create an oversized partition?

**Answer:** A key can be extremely frequent.

**Reasoning:** Hashing distributes keys, but it does not guarantee that the number of records associated with each key is balanced. This is a data-skew problem.

---

#### H6. When might `repartition()` be preferable to `coalesce()` for decreasing partitions?

**Answer:** When the current partitions are poorly balanced and the workload benefits from a global redistribution.

**Reasoning:** Coalesce prioritizes reduced movement, while repartition provides stronger control over redistribution.

---

#### H7. A developer changes `spark.sql.shuffle.partitions` from 200 to 2,000. Why might an unrelated DataFrame's partition count remain unchanged?

**Answer:** The setting relates to relevant shuffle partitioning; it does not universally overwrite every existing DataFrame partition count.

**Reasoning:** Input partitions, explicit repartitioning, non-shuffle transformations, and other mechanisms have separate effects.

---

#### H8. Why does partition count interact with executor cores?

**Answer:** Partitions create units of work that can become tasks, while executor capacity limits how many tasks can run concurrently.

**Reasoning:** If there are too few partitions, capacity can be underused; if there are excessively many tiny partitions, scheduling overhead can become significant.

---

#### H9. Why might increasing partition count fail to improve a job?

**Answer:** The job may be bottlenecked by I/O, shuffle, skew, CPU characteristics, network, or task overhead rather than insufficient parallelism.

**Reasoning:** Partition count is only one performance variable.

---

#### H10. Why is `total data / partition count` only a rough partition-size estimate?

**Answer:** It assumes an even distribution that may not exist.

**Reasoning:** Actual sizes depend on row width, input layout, filtering, key distribution, shuffle behavior, and skew.

---

### 10 Advanced

#### A1. Design a partitioning investigation for a large production pipeline.

**Answer:** Start with baseline measurements, inspect current partition count and approximate distribution, understand task capacity, identify shuffles, measure task duration and output files, test controlled alternatives, and compare the same workload before and after each change.

**Reasoning:** Partitioning decisions should be evidence-based rather than driven by a universal formula.

---

#### A2. A team adds `repartition(1000)` after every major DataFrame transformation. How would you evaluate the design?

**Answer:** Identify which repartitions solve a real downstream requirement, measure their shuffle cost, remove unnecessary changes, and retain only partitioning decisions that improve measurable workload behavior.

**Reasoning:** Repeated repartitioning can create multiple expensive data redistributions.

---

#### A3. A join becomes slower after both sides are manually repartitioned on the join key. What hypotheses should you test?

**Answer:**

1. The original join strategy was already efficient.
2. The manual repartitions introduced unnecessary shuffles.
3. The data is skewed.
4. The datasets have different sizes and broadcast may be relevant.
5. The repartition benefit is not amortized by downstream reuse.

**Reasoning:** There is no universal rule that pre-repartitioning a join is beneficial.

---

#### A4. How would you design an experiment to choose between 50 and 500 partitions?

**Answer:** Keep the dataset, transformation, action, cluster configuration, and input conditions constant. Run the same workload for both configurations, record runtime, task count, task duration, resource behavior, shuffle behavior, and output-file count, then compare repeated runs.

**Reasoning:** Only controlled comparisons can support a workload-specific tuning decision.

---

#### A5. Explain why execution partitioning and storage partitioning must be considered separately in architecture.

**Answer:** Execution partitioning controls how Spark distributes processing work, while storage partitioning controls how output data is organized in storage directories for supported formats.

**Reasoning:** A design can have efficient execution but poor storage layout, or efficient storage organization but poor execution behavior.

---

#### A6. A dataset has 1,000 partitions but only 2 GB of data. What questions should you ask before reducing them?

**Answer:** Ask about task overhead, output-file count, downstream reuse, current runtime, whether those partitions originate from a required shuffle, and whether reducing them changes task granularity beneficially.

**Reasoning:** Even an apparently excessive count must be evaluated in context.

---

#### A7. A dataset has 20 partitions and a cluster with 200 task slots. Is the partition count definitely wrong?

**Answer:** No.

**Reasoning:** The workload may be small, may not require more parallelism, or may be constrained by another bottleneck. The observation should trigger investigation, not an automatic repartition.

---

#### A8. Why can coalescing partitions improve file management while harming compute parallelism?

**Answer:** Fewer partitions can reduce write-task and file count, but they also expose fewer independent units of work and can create larger tasks.

**Reasoning:** Storage efficiency and compute parallelism are different objectives.

---

#### A9. What should a production engineer document after changing partition strategy?

**Answer:** Document the workload, data volume, original partitioning, target partitioning, reason for the change, cluster capacity, benchmark methodology, measured results, output-file behavior, and any assumptions about data distribution.

**Reasoning:** Partition tuning is operational knowledge that can become invalid as data volume and workload change.

---

#### A10. Explain why there is no universal "optimal partition size" or partition count in this chapter.

**Answer:** The appropriate granularity depends on data volume, row width, workload, cluster resources, shuffle characteristics, storage behavior, data distribution, and Spark version/configuration.

**Reasoning:** A value that works for one workload can be too large or too small for another.

---

## 46. Interview Questions

### Basic

#### 1. What is a Spark partition?

A partition is a distributed chunk of data that can be processed as a unit of parallel work.

#### 2. Why does Spark use partitions?

To divide distributed data into manageable units that can be processed concurrently across available resources.

#### 3. What is the relationship between partitions and tasks?

A typical stage creates one task per partition.

#### 4. What is `repartition()`?

A DataFrame transformation that creates a new partitioning arrangement and can redistribute data.

#### 5. What is `coalesce()`?

A DataFrame transformation primarily used to reduce partition count with less data movement than a full repartition in the typical reduction case.

---

### Intermediate

#### 6. What is the difference between `repartition()` and `coalesce()`?

`repartition()` provides controlled redistribution and is suitable for increasing or decreasing partitions; `coalesce()` is primarily for reducing partitions while avoiding a full shuffle.

#### 7. Why can repartition cause a shuffle?

Because records may need to move across executors to satisfy the new partitioning arrangement.

#### 8. Why is coalesce generally cheaper when reducing partitions?

Because it can combine existing partitions without globally redistributing every record.

#### 9. What is `spark.sql.shuffle.partitions`?

A configuration related to the number of partitions used for relevant Spark SQL/DataFrame shuffle operations.

#### 10. Why can too many partitions hurt performance?

Because task scheduling and coordination overhead can become significant, and writes may produce excessive files.

---

### Advanced

#### 11. How would you choose a partition count?

Start with data volume, current partition size/distribution, cluster task capacity, workload shape, shuffle requirements, and output requirements. Benchmark candidate configurations.

#### 12. How does partitioning affect joins?

Join execution can require data redistribution by join key. A compatible distribution can matter, but manual repartitioning is not automatically beneficial.

#### 13. How does partitioning affect aggregations?

Group-based aggregations often redistribute records by grouping key, making shuffle partitioning an important execution concept.

#### 14. How does partitioning affect output files?

More write partitions can result in more write tasks and can contribute to more output files. Excessive files can create a small-file problem.

#### 15. What is the difference between execution partitioning and storage partitioning?

Execution partitioning organizes Spark's distributed processing work; storage partitioning organizes data in storage directory layout.

#### 16. What is hash partitioning?

A conceptual strategy that uses a hash of a key to select a partition destination.

#### 17. What is range partitioning?

A strategy that organizes values into ranges and assigns ranges to partitions.

---

### Architecture

#### 18. A 2 TB pipeline runs with very few partitions. How would you approach it?

Measure current partition count, task sizes, cluster capacity, and workload characteristics. Test controlled repartitioning and compare actual runtime/resource behavior.

#### 19. A pipeline creates hundreds of thousands of files. What would you investigate?

Partition count at write time, writer behavior, dataset size, whether partitions are too small, and whether controlled coalescing is appropriate.

#### 20. A team uses `coalesce(1)` everywhere to simplify output.

What is the concern?

It can eliminate write parallelism, create a very large single task/file, and become a bottleneck. The right output-file strategy is workload-dependent.

#### 21. When would you deliberately use `repartition(column)`?

When a downstream workload benefits from key-based distribution and the cost of creating that distribution is justified.

#### 22. When would you deliberately use `coalesce(n)`?

When reducing partition count is the objective and a full redistribution is unnecessary.

#### 23. Why is "more partitions" not a sufficient performance strategy?

Because partitioning also affects task overhead, shuffle cost, network movement, memory, output files, and data distribution.

---

## 47. Architecture Questions

### Architecture Scenario 1 — Large Dataset, Low Parallelism

A 2 TB dataset runs on a cluster with many available task slots, but only a small number of partitions are visible for a major stage.

**Questions:**

1. What is the likely conceptual problem?
2. What measurements would you collect?
3. Would you immediately call `repartition()`?
4. What alternatives should be considered?
5. How would you validate the change?

**Expected reasoning:**

The first hypothesis is insufficient work parallelism. Measure partition count, task duration, data volume, and cluster capacity. Test a controlled repartition only after establishing that parallelism is the bottleneck.

---

### Architecture Scenario 2 — Too Many Output Files

A 10 GB dataset produces tens of thousands of output files.

**Questions:**

1. What could cause this?
2. How can partition count contribute?
3. Would `coalesce()` be a candidate?
4. Why might `coalesce(1)` be a poor production solution?
5. What measurements should be collected?

**Expected reasoning:**

High write parallelism can contribute to excessive files. Controlled reduction may help, but the target should balance file management with write and downstream read performance.

---

### Architecture Scenario 3 — Misunderstood Shuffle Configuration

A developer sets:

```python
spark.conf.set(
    "spark.sql.shuffle.partitions",
    1000
)
```

and expects every DataFrame to have 1,000 partitions.

**Questions:**

1. What is wrong with the assumption?
2. What does the setting actually relate to?
3. How would you inspect the current DataFrame partition count?
4. What other mechanisms can affect partitioning?

**Expected reasoning:**

The setting concerns relevant shuffle partitioning, not all partitions in all DataFrames.

---

### Architecture Scenario 4 — Repartition Replaced with Coalesce

A developer changes:

```python
df.repartition(10)
```

to:

```python
df.coalesce(10)
```

and observes a different performance profile.

**Questions:**

1. Why can the behavior differ?
2. What does repartition pay for?
3. What does coalesce avoid?
4. What distribution trade-off is introduced?

**Expected reasoning:**

Repartition can globally redistribute records; coalesce can reduce partitions by combining existing partition groups. Therefore cost and balance can differ.

---

### Architecture Scenario 5 — Slower Join After Manual Partitioning

A join becomes slower after both inputs are repartitioned by the join key.

**Questions:**

1. What new costs were introduced?
2. Was the repartition necessary?
3. Could broadcast have been relevant?
4. Could skew be involved?
5. What evidence should be collected?

**Expected reasoning:**

Investigate whether the repartitions added unnecessary shuffles, whether data sizes suggest a different join strategy, and whether uneven key distribution is involved.

---

## 48. Common Misconceptions

### Misconception 1 — "One partition equals one machine."

**Correction:** Partitions are logical data-processing units. Many partitions can be processed across executors, and an executor can process many partitions over time.

### Misconception 2 — "One partition equals one executor."

**Correction:** An executor can process multiple tasks and therefore multiple partitions across the lifetime of an application.

### Misconception 3 — "More partitions always means more performance."

**Correction:** More partitions can increase useful parallelism but can also increase scheduling overhead and file counts.

### Misconception 4 — "`spark.sql.shuffle.partitions` controls every partition count."

**Correction:** It relates to relevant shuffle partitioning, not every DataFrame's partition count.

### Misconception 5 — "`repartition()` is always bad because it shuffles."

**Correction:** Shuffle is expensive, but deliberate redistribution can be worthwhile when it solves a real workload problem.

### Misconception 6 — "`coalesce()` is always faster."

**Correction:** It can be cheaper for reducing partitions, but it may preserve uneven distribution and is not a universal optimization.

### Misconception 7 — "`coalesce()` is the right tool for increasing partitions."

**Correction:** Use `repartition()` for controlled increases.

### Misconception 8 — "Execution partitioning and storage partitioning are the same."

**Correction:** They operate at different layers and solve different problems.

### Misconception 9 — "100 partitions means approximately equal data."

**Correction:** Partition count does not guarantee balance.

### Misconception 10 — "Manually repartitioning before every join is good practice."

**Correction:** It can introduce unnecessary shuffle and should be justified by measurement and workload requirements.

---

## 49. Learning Checkpoints

Use active recall after each major section.

### Checkpoint A — Foundations

1. What is a partition?
2. Why does Spark need partitions?
3. What is the relationship between a partition and a task?
4. How does executor capacity affect useful parallelism?
5. Why is a partition not a machine?

### Checkpoint B — Partition Count

1. What does partition count mean?
2. What can happen with too few partitions?
3. What can happen with too many?
4. Why is partition count alone insufficient?
5. How can you inspect partition count?

### Checkpoint C — Repartition

1. What does `repartition(n)` do?
2. Why can it cause shuffle?
3. What does `repartition("key")` mean?
4. Why might repartitioning be useful before a downstream workload?
5. Why can it also make a workload slower?

### Checkpoint D — Coalesce

1. What problem does `coalesce()` solve?
2. Why can it be cheaper?
3. What distribution trade-off can it introduce?
4. Why is it not the general tool for increasing partitions?
5. When is coalesce useful before a write?

### Checkpoint E — Production

1. What is execution partitioning?
2. What is storage partitioning?
3. What is the small-file problem?
4. Why is there no universal partition count?
5. What should you measure before and after partition tuning?

---

## 50. Final Knowledge Assessment

### Conceptual Assessment — 10 Questions

1. Define a Spark partition.
2. Explain partition → task → executor.
3. Explain too few partitions.
4. Explain too many partitions.
5. Explain partition size.
6. Explain `repartition()`.
7. Explain `coalesce()`.
8. Explain shuffle partitioning.
9. Distinguish execution and storage partitioning.
10. Explain why partition tuning is workload-dependent.

**Passing standard:** You should be able to answer without relying on memorized API descriptions.

---

### Coding Assessment — 5 Tasks

#### Task 1

Create a DataFrame and print its current partition count.

#### Task 2

Create a new DataFrame with 50 partitions using `repartition()`.

#### Task 3

Reduce those partitions using `coalesce()` and explain the expected difference in data movement.

#### Task 4

Repartition by:

```text
customer_id
```

and explain why a downstream key-oriented workload might benefit.

#### Task 5

Write two outputs using different partition strategies and compare output-file behavior.

**Passing standard:** Your code should be readable, executable, and accompanied by an explanation of the execution implications.

---

### Debugging Assessment — 5 Scenarios

1. A large job has too few partitions.
2. A small job has tens of thousands of tasks.
3. Repartition makes a job slower.
4. Coalesce creates uneven work.
5. Output contains too many tiny files.

For each scenario provide:

```text
Symptom
Diagnosis
Likely cause
Corrective action
Why
```

---

### Architecture Assessment — 5 Production Problems

1. Design a partition strategy for a multi-terabyte transformation.
2. Reduce output files without unnecessarily destroying write parallelism.
3. Diagnose a job that remains slow after increasing partition count.
4. Evaluate a proposed manual repartition-before-every-join pattern.
5. Design an experiment to compare two candidate partition counts.

**Passing standard:** You must explain the reasoning and trade-offs rather than give a single unexplained number.

---

## 51. Forward Connection to Data Skew

The next topic is:

```text
09-data-skew-and-salting.md
```

Partition count alone does not guarantee balanced work.

For example:

```text
Partition 1 → 1 GB
Partition 2 → 1 GB
Partition 3 → 1 GB
Partition 4 → 100 GB
```

There are four partitions, but the workload is highly uneven.

This is **data skew**.

Topic 09 will cover:

- skew;
- hot keys;
- skewed partitions;
- salting;
- skew mitigation.

Do not try to solve every imbalance problem by simply increasing partition count.

---

## 52. Forward Connection to Caching

Partition layout can matter when data is persisted or reused.

However, caching and persistence are owned by Topic 10:

- `cache()`;
- `persist()`;
- storage levels;
- repeated computation.

The key connection is simply:

> A persisted dataset still has a partitioned execution layout, and that layout can influence subsequent work.

Do not turn partitioning into a caching lesson here.

---

## 53. Forward Connection to Catalyst

Spark's optimizer and physical planning machinery can influence how partitioning and exchanges appear in execution.

Topic 12 owns:

- logical plans;
- physical plans;
- Catalyst;
- `explain()`.

For this topic, it is enough to understand that explicit partitioning requests participate in a larger execution system.

Do not assume an API call gives you complete control over every physical detail.

---

## 54. Forward Connection to AQE

Adaptive Query Execution is covered in Topic 13.

AQE can make runtime decisions involving partitioning and exchange behavior based on observed statistics.

Topic 13 owns:

- Adaptive Query Execution;
- dynamic partition coalescing;
- runtime statistics;
- adaptive join decisions.

For now, remember:

> Static partition choices are not necessarily the final runtime behavior in every Spark execution.

---

## 55. Forward Connection to Spark UI

Topic 15 will teach detailed Spark UI diagnosis.

There you will learn to observe:

- number of tasks;
- task duration;
- shuffle read;
- shuffle write;
- skewed tasks;
- stage behavior.

For this chapter, use measurement conceptually and understand what you would look for.

Do not attempt to diagnose every partition problem from partition count alone.

---

## 56. Production Partitioning Principles

Memorize these as decision principles, not as a fixed formula:

1. Understand the workload first.
2. Inspect existing partitioning.
3. Understand available parallelism.
4. Avoid unnecessary shuffle.
5. Avoid excessive task counts.
6. Avoid oversized partitions.
7. Consider data distribution.
8. Consider downstream joins and aggregations.
9. Consider output-file count.
10. Measure before and after changes.
11. Do not hard-code arbitrary partition counts without understanding the workload.
12. Revisit partition choices as data volume changes.

The most important principle is:

> **Do not repartition because "more partitions sounds faster."**

---

## 57. Performance Experimentation

A useful controlled experiment is:

### Experiment A

```python
df_a = df.repartition(10)
```

### Experiment B

```python
df_b = df.repartition(50)
```

### Experiment C

```python
df_c = df.repartition(200)
```

Run the **same workload** for all three.

Record:

- runtime;
- task count;
- approximate task duration;
- resource behavior;
- output-file count;
- stability.

Do not fabricate benchmark numbers.

### Why repeated runs matter

Distributed workloads can vary because of:

- cluster contention;
- caching effects;
- input variability;
- scheduling;
- JVM/Python startup;
- storage variability.

A serious benchmark should therefore use a repeatable methodology rather than one casual run.

---

## 58. Production Decision Framework

Before changing partitioning, ask:

```text
1. How much data?
       ↓
2. Current partition count?
       ↓
3. Approximate partition size?
       ↓
4. Available task capacity?
       ↓
5. Shuffle involved?
       ↓
6. Distribution balanced?
       ↓
7. Increase or decrease?
       ↓
8. Need redistribution?
       ↓
9. Writing output?
       ↓
10. File-count requirement?
       ↓
11. What is the measurable hypothesis?
       ↓
12. Run controlled experiment
       ↓
13. Keep only if evidence supports it
```

This is much stronger than:

```python
df.repartition(500)
```

because "500 sounds good."

---

## 59. Mental Model Diagrams

### Partition Basics

```text
Dataset
  |
  +-- P0
  +-- P1
  +-- P2
  +-- P3
```

### Partition → Task → Executor

```text
Partition
    ↓
  Task
    ↓
Executor
```

### Multiple Tasks

```text
P0 → Task 0 ──┐
P1 → Task 1 ──┼──> Executor resources
P2 → Task 2 ──┤
P3 → Task 3 ──┘
```

### Repartition

```text
P0 P1 P2 P3
 \  |  |  /
  \ |  | /
   Shuffle
      |
      v
P0' P1' P2' P3' P4'
```

### Coalesce

```text
P0 P1 P2 P3 P4 P5
 |  |  |  |  |  |
 +--+  +--+  +--+
   ↓     ↓     ↓
  P0'   P1'   P2'
```

### Execution Partitioning vs Storage Partitioning

```text
Execution:

DataFrame
   ↓
Spark Partitions
   ↓
Tasks
   ↓
Executors
```

```text
Storage:

DataFrame
   ↓
partitionBy("country")
   ↓
country=India/
country=USA/
country=UK/
```

These are related but distinct layers.

---

## 60. What You Should Be Able to Do Now

After completing this topic, you should be able to:

- define a Spark partition;
- explain why partitions exist;
- explain partition → task → executor;
- reason about parallelism;
- inspect partition count;
- distinguish partition count from partition size;
- explain too few partitions;
- explain too many partitions;
- explain shuffle partitions;
- explain `spark.sql.shuffle.partitions`;
- use `repartition(n)`;
- use `repartition(column)`;
- use `repartition(n, columns...)`;
- use `coalesce(n)` appropriately;
- explain why repartition can shuffle;
- explain why coalesce can be cheaper for reduction;
- distinguish execution partitioning from storage partitioning;
- distinguish `repartition()` from `partitionBy()`;
- explain hash partitioning conceptually;
- explain range partitioning conceptually;
- reason about joins and aggregations;
- reason about output files;
- identify the small-file problem;
- design a partition experiment;
- diagnose common partitioning mistakes;
- explain why no universal partition count exists;
- identify when to investigate skew, AQE, Catalyst, caching, or Spark UI.

---

## 61. Summary

The conceptual progression for this topic is:

```text
Distributed Dataset
        ↓
Partitions
        ↓
Tasks
        ↓
Parallelism
        ↓
Partition Count
        ↓
Partition Size
        ↓
Shuffle
        ↓
repartition()
        ↓
coalesce()
        ↓
Partitioning by Key
        ↓
Execution vs Storage Partitioning
        ↓
Performance + Output Files
        ↓
Production Partition Strategy
```

The most important ideas are:

### 1. Partitions are work units

A partition is a distributed chunk of data that can become a task's input.

### 2. Partition count affects parallelism

Too few partitions can leave resources underutilized.

Too many can create excessive overhead.

### 3. Partition size matters

Two datasets with the same partition count can have radically different processing characteristics.

### 4. Repartition means redistribution

`repartition()` is the tool to use when controlled redistribution is needed.

That redistribution commonly introduces a shuffle.

### 5. Coalesce means cheaper reduction

`coalesce()` is primarily useful for reducing partition count when full redistribution is unnecessary.

### 6. Execution partitioning and storage partitioning are different

```python
df.repartition("country")
```

and:

```python
df.write.partitionBy("country")
```

solve different problems.

### 7. Partitioning affects storage as well as computation

Execution partitioning can influence output-file count and therefore the small-file problem.

### 8. Partitioning is workload-dependent

There is no universal magic number.

### 9. Measure

The production loop is:

```text
Hypothesis
   ↓
Measure baseline
   ↓
Change one variable
   ↓
Measure again
   ↓
Compare
   ↓
Keep or revert
```

### 10. Partition count does not guarantee balance

This leads directly to the next topic:

```text
09-data-skew-and-salting.md
```

A dataset can have a perfectly reasonable number of partitions and still have severely uneven work.

---

## 62. Glossary

**Partition** — A distributed chunk of data processed as a unit of work.

**Task** — A unit of execution that generally processes one partition for a stage.

**Executor** — A Spark worker process that executes tasks and holds data/intermediate state.

**Core / Task Slot** — A unit of executor capacity that can participate in concurrent task execution.

**Parallelism** — The amount of independent work that can execute concurrently.

**Partition Count** — Number of partitions in a dataset at a given point in its lineage.

**Partition Size** — Amount of data represented by a partition.

**Shuffle** — Redistribution of records across partitions, often involving network transfer.

**Shuffle Partition** — A partition produced as part of a shuffle stage.

**`repartition()`** — DataFrame transformation used to request a new partitioning arrangement, typically with redistribution.

**`coalesce()`** — DataFrame transformation primarily used to reduce partition count without a full redistribution in the typical reduction case.

**Hash Partitioning** — A conceptual partitioning strategy that maps keys to partitions using a hash-like function.

**Range Partitioning** — A strategy that divides values into ranges and assigns ranges to partitions.

**Execution Partitioning** — The partitioning used by Spark to organize distributed computation.

**Storage Partitioning** — Organization of output data into storage directories or table partitions based on partition columns.

**`partitionBy()`** — DataFrameWriter API used to organize supported output formats by partition columns.

**Data Locality** — The relationship between where data is located and where computation executes.

**Task Scheduling** — The process of assigning executable tasks to available cluster resources.

**Small File Problem** — Operational and performance issues caused by producing very many small output files.

**Data Skew** — Uneven distribution of records or workload across partitions.

**`spark.sql.shuffle.partitions`** — Spark SQL configuration affecting the number of partitions used by relevant shuffle operations.

---

## 63. Topic Completion Standard

Do not consider this topic complete until you can explain, without notes:

```text
What is a partition?
        ↓
Why does Spark need partitions?
        ↓
How does a partition become a task?
        ↓
How does executor capacity limit parallelism?
        ↓
What happens when there are too few partitions?
        ↓
What happens when there are too many?
        ↓
Why does partition size matter?
        ↓
What does repartition do?
        ↓
Why can repartition shuffle?
        ↓
What does coalesce do?
        ↓
Why can coalesce be cheaper?
        ↓
When should you use each?
        ↓
How does partitioning affect joins?
        ↓
How does partitioning affect aggregations?
        ↓
How does partitioning affect output files?
        ↓
What is the small-file problem?
        ↓
What is execution partitioning?
        ↓
What is storage partitioning?
        ↓
Why is there no universal partition count?
        ↓
How would you measure a partitioning decision?
```

You should also be able to implement:

```python
df.repartition(100)
df.repartition("customer_id")
df.repartition(100, "customer_id")
df.coalesce(10)
```

and explain **why** each one exists rather than merely knowing its syntax.

---

## 64. Final Self-Review Checklist

- [x] Partition taught from absolute basics.
- [x] Why partitions exist explained.
- [x] Partition → task relationship explained.
- [x] Task → executor relationship explained.
- [x] Partition count separated from machine/executor count.
- [x] Too few partitions explained.
- [x] Too many partitions explained.
- [x] Partition size distinguished from partition count.
- [x] `getNumPartitions()` included.
- [x] `spark.sql.shuffle.partitions` explained without treating it as universal.
- [x] Shuffle partitions explained.
- [x] `repartition()` explained.
- [x] `repartition(n)` explained.
- [x] Repartition by column explained.
- [x] Multiple-column repartition explained.
- [x] Repartition/shuffle relationship explained.
- [x] `coalesce()` explained.
- [x] Why coalesce can be cheaper explained.
- [x] Repartition versus coalesce compared.
- [x] Output-file implications explained.
- [x] Small-file problem explained.
- [x] Execution partitioning versus storage partitioning explained.
- [x] `partitionBy()` distinguished from `repartition()`.
- [x] Hash partitioning explained conceptually.
- [x] Range partitioning explained conceptually.
- [x] Partitioning around joins explained.
- [x] Partitioning around aggregations explained.
- [x] Production trade-offs explained.
- [x] Complete mini-project included.
- [x] At least 12 hands-on labs included.
- [x] 10 debugging scenarios included.
- [x] Exactly 40 practice questions included.
- [x] Interview questions included.
- [x] Architecture exercises included.
- [x] Misconceptions included.
- [x] Learning checkpoints included.
- [x] Final knowledge assessment included.
- [x] Glossary included.
- [x] Forward connection to skew included without deeply teaching salting.
- [x] Forward connection to caching included without deeply teaching persistence.
- [x] Forward connection to Catalyst included without deeply teaching optimizer internals.
- [x] Forward connection to AQE included without deeply teaching AQE.
- [x] Forward connection to Spark UI included without duplicating Topic 15.
- [x] No fabricated benchmark numbers included.
- [x] Partition tuning presented as workload-dependent.


## Production Partitioning Worksheet

Use this worksheet whenever you are considering a partitioning change.

### Workload

```text
Pipeline / job:
Input source:
Approximate input volume:
Expected output volume:
Primary operation:
Join keys:
Aggregation keys:
Write format:
```

### Current state

```text
Current partition count:
Approximate average partition size:
Observed task count:
Observed task duration:
Shuffle involved?:
Output file count:
Known distribution/skew issue?:
```

### Cluster capacity

```text
Executors:
Executor cores / task capacity:
Memory characteristics:
Concurrent task capacity:
```

### Proposed change

```text
Change:
Reason:
Expected benefit:
Expected cost:
```

### Measurement

```text
Baseline runtime:
Candidate runtime:
Baseline task count:
Candidate task count:
Baseline output files:
Candidate output files:
Other observations:
```

### Decision

```text
Keep change?:
Evidence:
Assumptions:
Follow-up investigation:
```

The final decision should be explainable in one sentence:

> "We changed partitioning from ______ to ______ because ______, and the measured effect was ______ under workload ______."

That is the level of reasoning expected in production Data Engineering.

