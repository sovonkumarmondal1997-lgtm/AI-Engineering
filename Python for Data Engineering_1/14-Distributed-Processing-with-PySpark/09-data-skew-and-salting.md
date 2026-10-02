# Data Skew and Salting

> **Module:** 14 — Distributed Processing with PySpark  
> **Topic:** 09 — Data Skew and Salting  
> **Level:** Beginner → Production Data Engineer  
> **Prerequisites:** Topics 01–08

## 1. Learning Objectives

By the end of this chapter, you should be able to:

- define data skew in distributed processing;
- distinguish skew from simply having too few partitions;
- explain why uneven data distribution creates straggler tasks;
- identify hot keys;
- recognize NULL and default-key skew;
- recognize time-based skew;
- recognize poor partitioning-column choices;
- detect skew from key-frequency analysis;
- reason using maximum versus median task time;
- recognize shuffle-read imbalance;
- explain skew in joins;
- explain join explosion combined with skew;
- explain skew in aggregations;
- explain skew in window functions;
- explain skew in writes;
- choose first-line mitigations before reaching for salting;
- use NULL/default-key isolation where business semantics allow;
- use pre-aggregation when it is semantically valid;
- understand broadcast as a possible skew mitigation;
- explain AQE skew-join handling conceptually;
- explain what salting is and why it works;
- salt the skewed side of a join;
- replicate the other side across the salt range;
- reason about salt-range selection;
- distinguish random and deterministic salting;
- selectively salt only hot keys;
- isolate hot keys;
- implement two-phase aggregation;
- explain the cost of salting;
- identify when not to salt;
- measure performance before and after a skew mitigation;
- validate correctness after an optimization;
- choose a mitigation based on evidence rather than habit.

The goal is not to memorize the word **salting**.

The goal is to become able to reason:

```text
Observe
  ↓
Measure
  ↓
Identify hot keys
  ↓
Understand the cause
  ↓
Choose the simplest valid mitigation
  ↓
Implement
  ↓
Measure again
  ↓
Validate correctness
  ↓
Compare trade-offs
  ↓
Keep / revert
```

---

## 2. Prerequisites

Topic 09 sits immediately after joins and partitioning:

```text
01 → Distributed computing
02 → SparkSession/configuration/deploy modes
03 → RDDs vs DataFrames
04 → Transformations/actions/lazy evaluation
05 → DataFrame API
06 → Spark SQL
07 → Joins/shuffle/broadcast joins
08 → Partitioning/repartition/coalesce
09 → Data skew and salting
10 → Caching/persistence
11 → UDFs
12 → Catalyst/explain plans
13 → AQE
14 → Data sources/save modes/bucketing
15 → Spark UI/debugging
16 → Testing
```

The conceptual transition is:

```text
JOINS
  ↓
introduce data movement

PARTITIONING
  ↓
controls how work is distributed

SKEW
  ↓
explains what happens when that distribution becomes highly uneven
```

You should already understand:

- driver;
- executors;
- partitions;
- tasks;
- jobs;
- stages;
- transformations and actions;
- lazy evaluation;
- DataFrames;
- Spark SQL;
- joins;
- shuffle;
- broadcast joins;
- `repartition()`;
- `coalesce()`.

This chapter connects those concepts to skew. It does not re-teach Topics 01–08.

---

## 3. Core Mental Model

Build the entire chapter around:

```text
DATA
  ↓
PARTITIONS
  ↓
TASKS
  ↓
PARALLEL EXECUTION
```

Balanced:

```text
Partition 1 → 10 GB
Partition 2 → 10 GB
Partition 3 → 11 GB
Partition 4 → 9 GB
```

Skewed:

```text
Partition 1 → 10 GB
Partition 2 → 9 GB
Partition 3 → 11 GB
Partition 4 → 100 GB
                         ↑
                      straggler
```

Then:

```text
Task 1 → finishes quickly
Task 2 → finishes quickly
Task 3 → finishes quickly
Task 4 → runs for a very long time
```

The production consequence is crucial:

> **A distributed job can be limited by one straggler even while most of the cluster is already idle.**

This is the central problem Topic 09 teaches.

---

## 4. What Is Data Skew?

Data skew means that data or computational work is distributed very unevenly across partitions.

Simple example:

```text
100 rows

Partition A → 25
Partition B → 25
Partition C → 25
Partition D → 25
```

This is reasonably balanced.

Now:

```text
Partition A → 10
Partition B → 10
Partition C → 10
Partition D → 70
```

This is skewed.

The number of partitions has not changed.

The problem is the **distribution of work**.

A useful definition is:

> **Data skew occurs when a relatively small number of partitions, keys, or groups contain disproportionately large amounts of data or computational work compared with the rest.**

Skew is therefore a distribution problem.

---

## 5. Why Skew Matters in Distributed Systems

Distributed systems gain performance from parallelism:

```text
Work
 ↓
P0 P1 P2 P3 P4 P5 P6 P7
 ↓
many tasks
 ↓
parallel execution
```

Skew weakens that benefit:

```text
P0 → small
P1 → small
P2 → small
P3 → huge
P4 → small
P5 → small
```

Most tasks finish.

One task remains.

The job cannot complete until the required work is complete.

This produces a **long tail**.

Conceptually:

```text
Task duration

P0 █
P1 █
P2 ██
P3 █
P4 █████████████████████████████████████
```

The cluster may appear mostly idle while one task continues processing the hot partition.

---

## 6. Balanced vs Skewed Partitions

Balanced:

```text
P0 → 10 GB
P1 → 11 GB
P2 → 9 GB
P3 → 10 GB
```

Skewed:

```text
P0 → 10 GB
P1 → 9 GB
P2 → 11 GB
P3 → 100 GB
```

The second workload can be much slower even though:

```text
partition count = 4
```

in both cases.

This proves:

> **Partition count alone does not tell you whether a workload is balanced.**

You need to reason about the distribution of data and work.

---

## 7. Skew Is Different from Too Few Partitions

This distinction is mandatory.

### Too few partitions

```text
4 partitions

P0 → 4 GB
P1 → 4 GB
P2 → 4 GB
P3 → 4 GB
```

The issue may be insufficient parallelism.

### Skew

```text
4 partitions

P0 → 100 MB
P1 → 100 MB
P2 → 100 MB
P3 → 13 GB
```

The issue is uneven distribution.

Increasing partition count can help a **too-few-partitions** problem.

It does not automatically solve a **hot-key skew** problem.

For example, if the same hot key continues to map to one dominant partition:

```text
Before:

HOT KEY
   ↓
P3

After increasing partition count:

HOT KEY
   ↓
P17
```

The partition number changed.

The concentration problem did not.

This distinction prevents a common production mistake:

> **Do not treat every slow Spark stage as a partition-count problem.**

---

## 8. Key Frequency Creates Skew

Many skew problems begin with uneven key frequency.

Example:

```text
customer_id | rows
------------|-----
101         | 10
102         | 15
103         | 8
104         | 12
999999      | 30,000,000
```

The key:

```text
999999
```

is a **hot key**.

If a shuffle or grouping operation distributes records according to `customer_id`, a huge amount of work can become concentrated around that key.

The key-frequency problem becomes a partition/work problem.

```text
Uneven key frequency
        ↓
Key-based distribution
        ↓
Uneven partition size
        ↓
Uneven task work
        ↓
Straggler
```

---

## 9. Hot Keys

A hot key is a key value that appears disproportionately often and therefore creates disproportionate processing work.

Examples:

- one extremely active customer;
- one popular product;
- one viral event;
- one anonymous-user identifier;
- `"UNKNOWN"`;
- `"N/A"`;
- `0`;
- `-1`;
- a default tenant;
- a system-generated placeholder.

Example:

```text
customer_id

1       → 5 rows
2       → 8 rows
3       → 6 rows
999999  → 30,000,000 rows
```

The hot key is not necessarily "bad data."

It may represent legitimate business activity.

The engineering question is:

> **How can the workload process the hot key without allowing it to dominate one task?**

---

## 10. NULL and Default Keys

NULL or default values can become hot keys.

Examples:

```text
customer_id = NULL
customer_id = "UNKNOWN"
customer_id = 0
customer_id = -1
```

Imagine:

```text
100 million events

NULL customer_id → 40 million
valid customer IDs → 60 million
```

The NULL representation is now a major concentration of work.

### Detect it

```python
from pyspark.sql import functions as F

df.groupBy("customer_id").count().orderBy(
    F.desc("count")
).show(20, truncate=False)
```

You should inspect:

- top key;
- count;
- percentage of total;
- semantic meaning of the key.

Do not automatically replace NULL with a random value.

The correct treatment depends on business semantics.

---

## 11. Time-Based Skew

A partitioning or grouping key can look reasonable and still become skewed because business activity changes over time.

Example:

```text
date        rows
----------  --------
2026-09-01  1M
2026-09-02  1M
2026-09-03  1M
2026-09-04  100M
```

Potential causes:

- Black Friday;
- product launch;
- outage;
- viral event;
- month-end;
- end-of-day batch;
- seasonal traffic;
- promotional campaign.

The key itself is not necessarily poorly designed.

The distribution is simply different from the normal workload.

This is why production partitioning must be based on observed data, not only on schema design.

---

## 12. Bad Partitioning Columns

A poor partitioning column can have:

- very few distinct values;
- highly uneven frequencies;
- one dominant value;
- values that do not match the downstream workload.

For example:

```text
country
```

might have only a small number of values.

But:

> **High cardinality does not automatically mean "best partitioning column."**

A good partitioning choice depends on:

- workload;
- downstream operations;
- key distribution;
- data volume;
- reuse;
- storage requirements.

The right question is:

> "Which distribution produces useful work for this workload?"

not:

> "Which column has the most unique values?"

---

## 13. Straggler Tasks and the Long Tail

A **straggler task** is a task that takes substantially longer than its peers.

Example:

```text
Task | Duration
-----|---------
1    | 12 sec
2    | 13 sec
3    | 11 sec
4    | 14 sec
5    | 58 min
```

Task 5 is suspicious.

The rest of the cluster may have already completed its work.

```text
Most tasks:
████

One task:
████████████████████████████████████████
```

The job waits.

This creates a **long-tail latency** problem.

Skew is one major cause of straggler tasks, although not every straggler is caused by skew. Other causes can include:

- slow I/O;
- executor instability;
- garbage collection;
- hardware variability;
- network problems;
- expensive records;
- data-dependent computation.

Therefore:

> **A straggler is a symptom; skew is one possible cause.**

---

## 14. Symptoms of Data Skew

Common production symptoms include:

- one or a few straggler tasks;
- maximum task time dramatically larger than median;
- maximum shuffle read dramatically larger than typical tasks;
- unusually high spill for one task;
- executor out-of-memory during one task;
- long-tail stage completion;
- most executors becoming idle while one task remains;
- one output partition becoming disproportionately large.

Conceptual Spark UI-style view:

```text
Task | Duration | Shuffle Read
-----|----------|-------------
1    | 12 sec   | 100 MB
2    | 13 sec   | 110 MB
3    | 11 sec   | 95 MB
4    | 14 sec   | 105 MB
5    | 58 min   | 85 GB
```

Task 5 deserves investigation.

Do not diagnose the cause solely from this table.

Use it as a signal to investigate the data distribution.

---

## 15. Max vs Median Reasoning

Compare:

```text
median task time = 15 seconds
maximum task time = 45 minutes
```

That is a strong skew signal.

But there is no universal rule such as:

```text
max / median > X = definitely skew
```

The roadmap explicitly requires that thresholds not be presented as universal.

Use:

```text
max vs median
```

as a diagnostic signal.

Also examine:

- shuffle read;
- shuffle write;
- spill;
- input size;
- output size;
- memory behavior.

A large max/median ratio tells you:

> "Something is uneven."

You still need to determine **why**.

---

## 16. Detecting Skew from Data

Start with key-frequency analysis.

```python
from pyspark.sql import functions as F

key_counts = (
    df.groupBy("customer_id")
      .count()
      .orderBy(F.desc("count"))
)

key_counts.show(20, truncate=False)
```

You are looking for:

```text
customer_id | count
------------|--------
999         | 30,000,000
123         | 5,000,000
456         | 4,500,000
...
```

The top keys may explain why one or more partitions become large.

### Key share

A useful metric is:

```text
key share = key_count / total_row_count
```

For example:

```text
total rows = 100 million
hot key rows = 30 million

share = 30 / 100
      = 30%
```

One key owning approximately 30% of the data deserves investigation.

It does not automatically mean salting is required.

---

## 17. Reusable Skew Detector

A useful educational detector can report:

- total rows;
- distinct key count;
- top N keys;
- count per key;
- percentage share;
- maximum key frequency;
- median key frequency.

Example:

```python
from pyspark.sql import functions as F

def profile_key_skew(df, key_col, top_n=20):
    total_rows = df.count()

    key_counts = (
        df.groupBy(key_col)
          .count()
          .withColumn(
              "share",
              F.col("count") / F.lit(total_rows)
          )
    )

    distinct_keys = key_counts.count()

    top_keys = (
        key_counts
        .orderBy(F.desc("count"))
        .limit(top_n)
    )

    return {
        "total_rows": total_rows,
        "distinct_keys": distinct_keys,
        "top_keys": top_keys,
    }
```

### Production note

The example is educational.

Calling:

```python
df.count()
```

and:

```python
key_counts.count()
```

creates actions.

For a production profiling utility, you would often combine metrics or materialize the relevant summary efficiently rather than repeatedly scanning a huge dataset.

The key rule is:

> **Keep diagnostics distributed and avoid collecting millions of keys to the driver.**

Do not do:

```python
keys = df.select("customer_id").collect()
```

for a huge dataset.

---

## 18. Skew in Joins

Connect this topic to Topic 07.

Consider:

```text
Large fact
customer_id
     |
     v
shuffle
     |
     v
hot customer_id
     |
     v
huge partition
```

Suppose:

```text
Left:
customer_id = A → 10,000,000 rows

Right:
customer_id = A → 5,000,000 rows
```

A join involving the hot key can create enormous work.

There are several cases:

### Skew only on the left

```text
Left:  HOT → huge
Right: HOT → small
```

### Skew only on the right

```text
Left:  HOT → small
Right: HOT → huge
```

### Skew on both

```text
Left:  HOT → huge
Right: HOT → huge
```

The third case can be particularly expensive.

---

## 19. Join Explosion Combined with Skew

Skew and join cardinality can compound each other.

Suppose:

```text
Hot key A

Left  → 1,000,000 rows
Right →   100,000 rows
```

A many-to-many join can produce an enormous number of matching combinations.

Conceptually:

```text
1,000,000 × 100,000
```

potential combinations for that key if every row matches.

This is not merely a partition-size problem.

It is also a **join-cardinality problem**.

Therefore:

> **Before applying a skew optimization, understand whether the join itself has an explosive cardinality pattern.**

A skew fix cannot make an inherently enormous result logically small.

---

## 20. Skew in Aggregations

Consider:

```python
result = (
    df.groupBy("customer_id")
      .agg(
          F.sum("revenue").alias("total_revenue")
      )
)
```

Normal distribution:

```text
key A → 1K rows
key B → 2K rows
key C → 1K rows
key D → 2K rows
```

Skew:

```text
key A → 1K rows
key B → 2K rows
key C → 1K rows
key D → 100M rows
```

The aggregation associated with key D can become disproportionately expensive.

The output may contain only one row for D, but Spark still has to process all of D's input records.

This illustrates an important principle:

> **Small output does not imply small computation.**

---

## 21. Skew in Window Functions

Window operations can create a very large logical group.

Example:

```python
from pyspark.sql import functions as F
from pyspark.sql.window import Window

window = Window.partitionBy("customer_id")

result = df.withColumn(
    "customer_total",
    F.sum("revenue").over(window)
)
```

If one customer owns an enormous number of rows:

```text
customer A → 1,000 rows
customer B → 2,000 rows
customer HOT → 100,000,000 rows
```

the window computation associated with HOT can become problematic.

Potential consequences include:

- large partition processing;
- memory pressure;
- long-running work;
- executor failure;
- long-tail execution.

Do not treat salting as a universal fix for windows.

Window semantics can require exact partition-level relationships.

Potential mitigations include:

- reconsidering the partitioning key;
- isolating pathological groups;
- pre-aggregating where semantically valid;
- changing the computation only when business requirements allow it.

---

## 22. Skew in Writes

Skew can affect writes as well as joins and aggregations.

Potential symptoms:

- one very large output partition;
- one unusually long-running write task;
- one disproportionately large output file;
- one storage partition receiving most of the data;
- poor downstream read behavior.

Distinguish:

```text
execution skew
```

from:

```text
storage/output layout problems
```

A write strategy can create storage imbalance even when an upstream computation was reasonably balanced.

Topic 08 covered partitioning and output-file behavior.

This topic focuses specifically on how **uneven data distribution** can produce write-side problems.

---

## 23. First-Line Skew Fixes

Do not immediately use salting.

A disciplined sequence is:

```text
1. Understand the skew
2. Verify the hot keys
3. Handle NULL/default keys where appropriate
4. Filter irrelevant data if semantically valid
5. Pre-aggregate
6. Broadcast a genuinely small side if appropriate
7. Isolate hot keys
8. Consider AQE
9. Salt when necessary
10. Measure
```

The principle is:

> **Use the simplest correct mitigation that addresses the actual cause.**

Salting is powerful, but it introduces complexity and data replication.

---

## 24. Handling NULL and Default Keys Separately

Suppose:

```text
customer_id = NULL
```

represents unknown customers.

You might separate the workload:

```python
normal = df.filter(
    F.col("customer_id").isNotNull()
)

unknown = df.filter(
    F.col("customer_id").isNull()
)
```

Then:

```text
Main data
    |
    +---- normal keys ------> standard processing
    |
    +---- NULL/default keys -> separate strategy
```

The separate strategy could be:

- a special aggregate;
- a separate output;
- a different join;
- a business-defined fallback.

The important point is semantic correctness.

Do not simply transform:

```text
NULL → random value
```

unless the business meaning supports that transformation.

---

## 25. Pre-Aggregation

If business semantics permit, reduce data before the expensive join.

Raw transactions:

```text
customer_id | amount
```

Pre-aggregate:

```python
summary = (
    transactions
    .groupBy("customer_id")
    .agg(
        F.sum("amount").alias("total_amount")
    )
)
```

Then join:

```python
result = summary.join(
    customer_dimension,
    on="customer_id",
    how="left"
)
```

Instead of:

```text
billions of transaction rows
        ↓
join
```

you may have:

```text
one summary row per customer
        ↓
join
```

This can drastically reduce the data participating in the join.

### When it works

Pre-aggregation is useful when:

- the business logic permits aggregation first;
- row-level detail is not required for the join;
- the downstream operation needs a summary.

### When it does not work

If you need every original row enriched by a dimension:

```text
transaction-level output
```

you cannot simply replace the fact table with one row per customer without changing the result.

Correctness comes first.

---

## 26. Broadcast as a Skew Mitigation

If one side is genuinely small, broadcast can avoid some shuffle-related work.

```python
from pyspark.sql import functions as F

result = fact.join(
    F.broadcast(dim),
    on="customer_id",
    how="left"
)
```

Conceptually:

```text
Small dimension
      ↓
replicated to executors

Large fact
      ↓
processed locally with the dimension
```

Broadcast can therefore be a useful mitigation when a skewed large fact joins to a genuinely small dimension.

### Limitations

Broadcast is not:

> "the universal skew solution."

Potential concerns include:

- the small side may not actually be small enough;
- executor memory constraints;
- data growth over time;
- broadcast overhead;
- inappropriate use on large-large joins.

Measure.

---

## 27. AQE Skew Join Handling

Adaptive Query Execution can use runtime information to mitigate certain skewed shuffle partitions in supported join scenarios.

Conceptually:

Without adaptive skew handling:

```text
Huge partition
      ↓
one huge task
```

With skew handling:

```text
Huge partition
      ↓
split into smaller pieces
      ↓
multiple tasks
```

The key idea is:

> **AQE can detect skewed shuffle partitions at runtime and split oversized partitions for applicable joins.**

Topic 09 introduces this concept.

Topic 13 teaches AQE comprehensively, including:

- AQE architecture;
- runtime statistics;
- adaptive partition coalescing;
- adaptive join changes;
- configuration;
- deeper execution behavior.

Do not turn this chapter into a full AQE tutorial.

---

## 28. What Is Salting?

Salting means adding an artificial value to a skewed key so that one hot key can be distributed across multiple partitioning keys.

Original:

```text
customer_id = 999
```

Salted:

```text
customer_id = 999, salt = 0
customer_id = 999, salt = 1
customer_id = 999, salt = 2
customer_id = 999, salt = 3
```

Instead of:

```text
HOT KEY
   ↓
one dominant partition
```

you create:

```text
HOT KEY
   |
   +-- HOT,0
   +-- HOT,1
   +-- HOT,2
   +-- HOT,3
   +-- ...
```

These composite keys can be distributed across multiple partitions.

Salting therefore changes the distribution key.

---

## 29. Why Salting Works

Without salting:

```text
Key A
Key A
Key A
Key A
Key A
Key A
Key A
   ↓
same key
   ↓
same partitioning destination
```

With salting:

```text
A,0
A,1
A,2
A,3
   ↓
different composite keys
   ↓
multiple partitioning destinations
```

The objective is not to make the logical key different.

The objective is to make the **physical distribution key** more granular.

This can turn:

```text
one huge unit of work
```

into:

```text
multiple smaller units of work
```

The downstream computation then needs to preserve the original business semantics.

---

## 30. Canonical Salted Join

Suppose:

### Fact

```text
customer_id
value
```

### Dimension

```text
customer_id
customer_name
```

The fact table has a hot key.

Create salt on the skewed side:

```python
from pyspark.sql import functions as F

salt_count = 16

fact_salted = fact.withColumn(
    "salt",
    F.floor(F.rand(seed=42) * salt_count)
)
```

Now the fact records for the hot customer can have:

```text
customer_id | salt
------------|-----
999         | 0
999         | 1
999         | 2
999         | 3
...
```

But the dimension table still has:

```text
customer_id = 999
```

There is a problem.

If the join key becomes:

```text
customer_id + salt
```

the dimension side needs matching salt values.

---

## 31. Replicating the Non-Skewed Side

Create salt values:

```python
salt_values = (
    spark.range(salt_count)
         .withColumnRenamed("id", "salt")
)
```

Replicate the dimension:

```python
dimension_salted = (
    dimension
    .crossJoin(salt_values)
)
```

Conceptually:

```text
customer_id | customer_name | salt
------------|---------------|-----
999         | Alice         | 0
999         | Alice         | 1
999         | Alice         | 2
...
999         | Alice         | 15
```

Now join:

```python
result = fact_salted.join(
    dimension_salted,
    on=["customer_id", "salt"],
    how="left"
)
```

The complete flow is:

```text
Fact
  ↓
add salt
  ↓
(customer_id, salt)
  ↓
distributed across multiple keys

Dimension
  ↓
replicate across salt range
  ↓
(customer_id, salt)
  ↓
join
```

The important relational idea is:

> **The side that is not salted must be expanded across the salt values when the salt participates in the join condition.**

---

## 32. Complete Salted Join Example

```python
from pyspark.sql import functions as F

salt_count = 16

fact_salted = (
    fact
    .withColumn(
        "salt",
        F.floor(F.rand(seed=42) * salt_count).cast("int")
    )
)

salt_values = (
    spark.range(salt_count)
         .withColumnRenamed("id", "salt")
         .withColumn("salt", F.col("salt").cast("int"))
)

dimension_salted = (
    dimension
    .crossJoin(salt_values)
)

result = (
    fact_salted
    .join(
        dimension_salted,
        on=["customer_id", "salt"],
        how="left"
    )
)
```

### What happened?

1. A salt column was added to the skewed side.
2. The salt has values in a bounded range.
3. The dimension side was replicated across that range.
4. The join uses both:
   - `customer_id`;
   - `salt`.
5. The hot customer can now participate in multiple partitioning keys.

### What did it cost?

The dimension side was expanded.

That is the trade-off.

---

## 33. Replication Cost

If:

```text
salt_count = 16
```

then the logical dimension representation may expand approximately:

```text
original dimension
×
16
```

before accounting for actual physical compression and execution details.

The consequences can include:

- more rows;
- more data movement;
- more memory;
- more computation;
- larger intermediate datasets;
- more complex execution.

Therefore:

> **Salting is not free.**

It exchanges:

```text
replication + complexity
```

for:

```text
better distribution of hot-key work
```

---

## 34. Choosing the Salt Range

Do not present a universal correct value.

The salt range depends on:

- hot-key frequency;
- number of hot keys;
- available task capacity;
- executor resources;
- size of the replicated side;
- desired work distribution;
- downstream workload.

Too small:

```python
salt_count = 2
```

may not distribute the hot key sufficiently.

Too large:

```python
salt_count = 10_000
```

may replicate the other side unnecessarily.

The correct value is workload-dependent.

The production process is:

```text
Choose candidate range
      ↓
Run
      ↓
Measure
      ↓
Compare
      ↓
Adjust
```

---

## 35. Salt-Range Experiment

Test candidates such as:

```text
2
4
8
16
32
```

only if those values make sense for your workload.

Record:

```text
salt_count
runtime
shuffle read
shuffle write
max task time
median task time
replicated-side size
memory pressure
correctness
```

Do not assume the largest candidate is best.

A larger salt range can:

- reduce individual hot-key partition size;
- increase replication;
- increase data movement;
- increase scheduling work.

This is an optimization trade-off.

---

## 36. Random vs Deterministic Salting

### Random salting

```python
F.floor(
    F.rand(seed=42) * salt_count
)
```

Advantages:

- simple;
- can distribute records for a hot key across salt values;
- deterministic for a fixed seed in a reproducible experiment, subject to Spark execution semantics.

Potential concern:

- the distribution is probabilistic;
- it does not guarantee perfect balance.

### Deterministic salting

For example:

```python
F.pmod(
    F.hash("some_column"),
    F.lit(salt_count)
)
```

Advantages:

- reproducible mapping from the chosen columns;
- useful when stable distribution matters.

Potential concern:

- hash distribution is not guaranteed to be perfectly uniform;
- the chosen input columns affect the distribution.

Neither method guarantees perfect balance.

---

## 37. Deterministic Salt Design

A deterministic salt should be based on information that distributes records within the hot key.

For example:

```python
fact_salted = fact.withColumn(
    "salt",
    F.pmod(
        F.hash("transaction_id"),
        F.lit(salt_count)
    ).cast("int")
)
```

The idea is:

```text
customer_id
+
transaction_id
        ↓
hash
        ↓
salt bucket
```

If `transaction_id` is reasonably distributed, this can spread the hot customer's records.

Do not use:

```python
hash(customer_id)
```

as the salt source for a hot customer.

Every record for the same customer would produce the same hash and therefore the same salt.

That would not solve the concentration.

---

## 38. Salting Only Hot Keys

Salting the entire dataset can be unnecessarily expensive.

A more targeted strategy is:

```text
Hot keys
   ↓
salted processing

Normal keys
   ↓
normal processing
```

This can reduce:

- replication;
- extra columns;
- shuffle;
- intermediate data;
- code complexity.

The basic architecture is:

```text
Input
  |
  +---- Hot keys ------> salted/special strategy
  |
  +---- Normal keys ---> standard strategy
                |
                v
              UNION
```

Selective salting is often more operationally attractive when only a small number of keys cause the problem.

---

## 39. Hot-Key Isolation

Hot-key isolation means processing pathological keys separately.

Workflow:

```text
1. Identify top hot keys.
2. Split them from the normal dataset.
3. Apply a special strategy to them.
4. Process normal keys normally.
5. Union the results.
```

Example:

```text
Input
  |
  +---- Hot keys ------> special strategy
  |
  +---- Normal keys ---> normal join
                         |
                         v
                       UNION
```

The special strategy might be:

- broadcast;
- salting;
- pre-aggregation;
- dedicated aggregation;
- a business-defined exception path.

Why can this be useful?

Because you do not pay the complexity of salting for every row when only a few keys are pathological.

---

## 40. Two-Phase Aggregation

Skewed aggregation can use a two-phase strategy.

Original:

```python
df.groupBy("customer_id").agg(
    F.sum("revenue")
)
```

Problem:

```text
HOT customer
      ↓
huge amount of aggregation work
```

Two-phase approach:

### Phase 1

```text
(customer_id, salt)
        ↓
partial aggregation
```

### Phase 2

```text
(customer_id)
        ↓
combine partial aggregates
```

Example:

```python
partial = (
    df
    .withColumn(
        "salt",
        F.pmod(
            F.hash("transaction_id"),
            F.lit(salt_count)
        ).cast("int")
    )
    .groupBy("customer_id", "salt")
    .agg(
        F.sum("revenue").alias("partial_revenue")
    )
)

final = (
    partial
    .groupBy("customer_id")
    .agg(
        F.sum("partial_revenue").alias("revenue")
    )
)
```

The hot key can now be processed through multiple partial aggregation groups.

---

## 41. Proving Two-Phase Aggregation

Input:

```text
customer_id | revenue
------------|--------
A           | 10
A           | 20
A           | 30
A           | 40
```

After salting:

```text
A,0 → 10
A,1 → 20
A,0 → 30
A,1 → 40
```

Partial aggregation:

```text
A,0 → 40
A,1 → 60
```

Final aggregation:

```text
A → 100
```

The original total is:

```text
10 + 20 + 30 + 40 = 100
```

The final total remains:

```text
40 + 60 = 100
```

This works because summation is decomposable:

```text
sum(all values)
=
sum(partial sums)
```

Do not assume every aggregation can be transformed this way without checking its mathematical and business semantics.

Correctness must be proven.

---

## 42. Window Skew Mitigation

Window skew requires special care.

Potential approaches include:

- reconsidering the partitioning key;
- isolating pathological groups;
- pre-aggregating when semantics allow;
- changing the computation only when business requirements permit.

Do not invent a universal salted-window recipe.

For some windows, exact row relationships within a partition are part of the business meaning.

Therefore:

> **Optimization must not change the window's semantics.**

---

## 43. Write Skew Mitigation

Possible approaches include:

- improving distribution before writing;
- selecting an appropriate partitioning strategy;
- separating exceptional keys;
- avoiding a single massive output partition;
- measuring file sizes and task durations.

Do not automatically use:

```python
coalesce(1)
```

to "fix" a large output.

That can reduce write parallelism and create a bottleneck.

Topic 08 owns the broader partitioning and write-file strategy.

Topic 09 focuses on the **uneven distribution** causing the write problem.

---

## 44. Cost of Salting

Salting can produce benefits:

```text
Reduced skew
    ↓
Better parallelism
    ↓
Shorter straggler tail
```

But it can also produce costs:

```text
More rows
    ↓
More data movement
    ↓
More computation
    ↓
More memory
    ↓
More complexity
```

Potential costs include:

- replicated rows;
- extra shuffle;
- larger intermediate data;
- increased memory pressure;
- more CPU work;
- more complex code;
- more complex debugging;
- more complex correctness validation.

Therefore:

> **Salting is an optimization technique, not a default transformation.**

---

## 45. When Not to Salt

Do not salt when:

- skew is small;
- AQE already handles the issue adequately;
- broadcast solves the problem;
- pre-aggregation solves the problem;
- hot-key isolation is simpler;
- replication cost exceeds the benefit;
- the workload is too small for the complexity to matter;
- correctness would become harder to guarantee than the performance benefit justifies.

The decision should be:

```text
Measure
  ↓
Compare alternatives
  ↓
Choose the simplest correct fix
```

---

## 46. Skew Mitigation Decision Tree

Use this as a reasoning framework:

```text
Is the workload skewed?
        |
       YES
        |
        v
Can the skew be explained?
        |
       YES
        |
        v
Is it NULL/default data?
   /              \
 YES               NO
  |                 |
Handle separately   v
                Is one side small?
                 /          \
               YES          NO
                |            |
           Broadcast         v
                         Can we pre-aggregate?
                           /        \
                         YES        NO
                          |          |
                     Pre-aggregate  v
                               Is AQE sufficient?
                                /          \
                              YES           NO
                               |             |
                              AQE            v
                                       Hot-key isolation
                                             OR
                                           Salting
```

This is not a rigid algorithm.

For example:

- hot-key isolation and salting can coexist;
- AQE can remain enabled while manual mitigation is tested;
- broadcast can be relevant after hot-key analysis;
- data-quality fixes can be more valuable than execution tricks.

---

## 47. Measurement Framework

Measure before and after.

Record:

- wall-clock runtime;
- median task time;
- maximum task time;
- shuffle read;
- shuffle write;
- spill;
- output size;
- memory pressure;
- result correctness.

Comparison table:

```text
Technique | Runtime | Shuffle Read | Max Task | Median Task | Notes
----------|---------|--------------|----------|-------------|------
Baseline  | ...     | ...          | ...      | ...         | ...
AQE       | ...     | ...          | ...      | ...         | ...
Broadcast | ...     | ...          | ...      | ...         | ...
Salting   | ...     | ...          | ...      | ...         | ...
Isolation | ...     | ...          | ...      | ...         | ...
```

Do not invent benchmark values.

Use placeholders until you actually run the experiment.

---

## 48. AQE ON vs OFF Experiment

The roadmap requires controlled experimentation.

### Experiment A

```text
AQE ON
Baseline
```

### Experiment B

```text
AQE OFF
Baseline
```

### Experiment C

```text
AQE ON
+
Salting
```

### Experiment D

```text
AQE OFF
+
Salting
```

### Experiment E

```text
AQE ON
+
Hot-key isolation
```

Record actual measurements.

The purpose is not to prove that:

```text
AQE > salting
```

or:

```text
salting > AQE
```

universally.

The purpose is to understand the workload.

---

## 49. Correctness Validation

Optimization is useless if it changes the answer.

For every skew mitigation, validate:

- row counts;
- aggregate totals;
- join coverage;
- duplicate behavior;
- NULL handling;
- unmatched records;
- key-level totals.

Example:

Before:

```text
customer A total revenue = 1,000
```

After:

```text
customer A total revenue = 1,000
```

The optimization must preserve business correctness.

### Join correctness

Compare:

```text
matched rows
unmatched rows
duplicate rows
key-level counts
```

### Aggregation correctness

Compare:

```text
total revenue
count
distinct keys
key-level aggregates
```

Correctness should be checked before declaring a performance optimization successful.

---

## 50. Salting and Duplication Risks

A common mistake is to replicate the dimension side but fail to include salt in the join condition.

Suppose:

```text
one fact row
```

joins against:

```text
16 replicated dimension rows
```

If the join condition is only:

```text
customer_id
```

the fact row may match all 16 copies.

That creates duplicates.

The correct salted join uses:

```text
customer_id + salt
```

on both sides.

Conceptually:

```text
fact:
A,3

dimension:
A,0
A,1
A,2
A,3
...
A,15
```

The fact row matches only:

```text
A,3
```

when the join includes:

```text
customer_id
AND
salt
```

This is why the salt is part of the physical join key.

---

## 51. Salting and Data Types

Keep the salt type consistent.

For example:

```python
F.floor(
    F.rand(seed=42) * salt_count
).cast("int")
```

and:

```python
spark.range(salt_count).withColumn(
    "salt",
    F.col("id").cast("int")
)
```

Both sides use an integer salt.

Avoid silent type mismatches such as:

```text
left salt  → integer
right salt → string
```

Also distinguish:

```text
original business key
```

from:

```text
composite physical key
```

For example:

```text
customer_id
```

is still the business identifier.

```text
(customer_id, salt)
```

is the temporary distribution/join key.

---

## 52. Production Decision Framework

| Problem | First Investigation | Possible Fix |
|---|---|---|
| NULL/default hot key | key frequency | separate handling |
| Small dimension + skewed fact | dimension size | broadcast |
| Reducible aggregation | business semantics | pre-aggregate |
| AQE-capable skewed join | runtime evidence | AQE |
| Few extreme hot keys | top-key analysis | hot-key isolation |
| Large skewed join | key distribution | salting |
| Skewed aggregation | key distribution | two-phase aggregation |
| Window skew | partition key | redesign/isolate if semantically valid |
| Write skew | output distribution | partition/write strategy |

This is a reasoning framework, not a rigid algorithm.

The correct engineering process is:

```text
Understand
   ↓
Measure
   ↓
Compare options
   ↓
Implement
   ↓
Validate
   ↓
Measure again
```

---

## 53. Measurement-First Engineering

Make this principle explicit:

> **DO NOT OPTIMIZE SKEW WITHOUT MEASURING IT.**

The comparison loop is:

```text
Baseline
   ↓
Change ONE thing
   ↓
Run again
   ↓
Measure
   ↓
Validate correctness
   ↓
Keep / revert
```

Record:

```text
wall time
median task time
maximum task time
shuffle read
shuffle write
spill
output size
memory pressure
correctness
```

This is how a performance investigation becomes engineering rather than guesswork.

---

## 54. Distributed-Processing Study Loop

Apply the module's learning loop specifically to skew:

```text
Read
  ↓
Predict stages/shuffles/partitions
  ↓
Write it
  ↓
Explain the plan
  ↓
Run small
  ↓
Run big
  ↓
Read Spark UI
  ↓
Change ONE thing
  ↓
Measure again
  ↓
Write it down
  ↓
Explain aloud
```

For skew, add:

```text
Identify hot keys
  ↓
Measure key share
  ↓
Compare task distribution
  ↓
Validate correctness
```

---

## 55. Connection to Topic 10 — Caching

Caching can sometimes help repeated expensive computations.

But:

> **Caching does not fix skew itself.**

If the dataset is skewed:

```text
cache(skewed_dataset)
```

does not magically rebalance it.

Topic 10 owns:

- `cache()`;
- `persist()`;
- storage levels;
- reuse decisions.

Topic 09 only establishes the distinction.

---

## 56. Connection to Topic 11 — UDFs

Do not teach UDFs here.

Only recognize that Python UDFs and pandas UDFs can affect execution performance.

Topic 11 owns:

- Python UDFs;
- pandas UDFs;
- built-in functions;
- serialization boundaries;
- UDF performance trade-offs.

Do not use UDFs as a skew solution unless the topic scope explicitly requires them.

---

## 57. Connection to Topic 12 — Catalyst

Later you will inspect how Spark's optimizer represents and chooses execution strategies.

Topic 12 owns:

- logical plans;
- physical plans;
- Catalyst;
- `explain()`.

For Topic 09, the important point is:

> **Skew mitigation is a workload and execution-layout problem that must eventually be understood in the context of Spark's physical plan.**

Do not deeply teach Catalyst here.

---

## 58. Connection to Topic 13 — AQE

Topic 09 introduces:

- why AQE matters;
- what skew-join handling means;
- why runtime information can help.

Topic 13 owns:

- AQE architecture;
- runtime statistics;
- adaptive partition coalescing;
- adaptive join changes;
- configuration;
- deeper behavior.

Remember:

```text
Topic 09
→ AQE skew handling concept

Topic 13
→ AQE comprehensively
```

---

## 59. Connection to Topic 15 — Spark UI

Topic 09 introduces the symptoms you should recognize in the UI:

- task-duration imbalance;
- maximum versus median;
- shuffle-read imbalance;
- spill;
- executor memory problems.

Topic 15 owns detailed Spark UI analysis.

The production progression is:

```text
Topic 09:
Recognize suspicious skew behavior

        ↓

Topic 15:
Investigate the execution in detail
```

---

## 60. Mental Model: Balanced Partitions

```text
P0 → 10 GB
P1 → 11 GB
P2 → 9 GB
P3 → 10 GB
```

The work is reasonably balanced.

This does not mean the partitions are mathematically equal.

It means the distribution is sufficiently balanced for the workload.

---

## 61. Mental Model: Skewed Partitions

```text
P0 → 10 GB
P1 → 9 GB
P2 → 11 GB
P3 → 100 GB
             ↑
          straggler
```

The large partition can dominate stage completion.

---

## 62. Mental Model: Hot Key

```text
Key A → 1,000 rows
Key B → 2,000 rows
Key C → 1,500 rows
Key HOT → 50,000,000 rows
```

If the execution distributes by key, HOT deserves immediate investigation.

---

## 63. Mental Model: Salting

```text
HOT
 |
 +-- HOT,0
 +-- HOT,1
 +-- HOT,2
 +-- HOT,3
 +-- ...
```

The artificial salt creates multiple physical distribution keys.

---

## 64. Mental Model: Hot-Key Isolation

```text
Input
  |
  +---- Hot keys ----> special strategy
  |
  +---- Normal keys --> standard strategy
                           |
                           v
                         UNION
```

This can be simpler than salting the entire dataset.

---

## 65. Mental Model: Two-Phase Aggregation

```text
Raw data
   ↓
(key, salt)
   ↓
Partial aggregation
   ↓
(key)
   ↓
Final aggregation
```

This can distribute work for a hot key while preserving a decomposable aggregate such as `sum`.

---

## 66. Production Engineering Principles

Make these principles explicit:

1. Detect before optimizing.
2. Understand the data distribution.
3. Identify hot keys.
4. Separate data-quality skew from legitimate business skew.
5. Try the simplest correct mitigation first.
6. Do not salt automatically.
7. Do not broadcast blindly.
8. Do not increase executors blindly.
9. Measure every optimization.
10. Validate correctness after every optimization.
11. Compare maximum and median task behavior.
12. Consider shuffle volume.
13. Consider memory pressure.
14. Consider downstream effects.
15. Keep optimization complexity justified by measurable benefit.

---

## 67. Mini Project — Production Data Skew Investigation and Remediation Lab

### Objective

Build a complete investigation around deliberately skewed data.

Required characteristics:

- one key owns approximately 30% of rows;
- five additional keys own approximately another 20%;
- remaining rows are distributed among many keys;
- NULL/default keys are present;
- enough records exist for meaningful experiments.

The project should demonstrate:

```text
Detection
   ↓
Diagnosis
   ↓
First-line fixes
   ↓
AQE
   ↓
Salting
   ↓
Hot-key isolation
   ↓
Two-phase aggregation
   ↓
Measurement
   ↓
Correctness
   ↓
Production decision
```

### Project tasks

1. Create a SparkSession.
2. Generate skewed data.
3. Inspect total row count.
4. Count distinct keys.
5. Calculate top key frequencies.
6. Calculate key share.
7. Identify hot keys.
8. Identify NULL/default-key concentration.
9. Create a baseline join.
10. Create a baseline aggregation.
11. Measure baseline behavior.
12. Apply NULL/default-key handling.
13. Apply pre-aggregation.
14. Apply broadcast where appropriate.
15. Test AQE skew handling.
16. Implement salting.
17. Choose a salt range.
18. Replicate the smaller side.
19. Perform the salted join.
20. Implement hot-key isolation.
21. Implement two-phase aggregation.
22. Compare approaches.
23. Test with AQE ON.
24. Test with AQE OFF where supported and appropriate.
25. Record runtime.
26. Record shuffle metrics where available.
27. Record task-time distribution.
28. Validate output correctness.
29. Explain trade-offs.
30. Write a final engineering decision based on measurements.

---

## 68. Mini Project — Synthetic Dataset

The following is a starting point for deliberately creating skew.

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = (
    SparkSession.builder
    .appName("skew-remediation-lab")
    .master("local[*]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

N = 1_000_000

base = (
    spark.range(N)
    .withColumn(
        "customer_id",
        F.when(
            F.col("id") < N * 0.30,
            F.lit(999999)
        )
        .when(
            F.col("id") < N * 0.50,
            (F.col("id") % 5 + 1).cast("long")
        )
        .otherwise(
            (F.col("id") % 100_000 + 100).cast("long")
        )
    )
    .withColumn(
        "revenue",
        (F.rand(seed=42) * 100).cast("double")
    )
)
```

This is a teaching dataset, not a claim that these exact proportions are ideal for every experiment.

Add some NULL/default records deliberately:

```python
df = (
    base
    .withColumn(
        "customer_id",
        F.when(
            (F.col("id") % 50) == 0,
            F.lit(None).cast("long")
        ).otherwise(F.col("customer_id"))
    )
)
```

Inspect:

```python
df.groupBy("customer_id").count().orderBy(
    F.desc("count")
).show(20, truncate=False)
```

### Important

The exact generated distribution depends on the expression and dataset size.

Verify actual frequencies instead of assuming that the code produced the intended percentages.

---

## 69. Mini Project — Baseline Key Profile

```python
from pyspark.sql import functions as F

total_rows = df.count()

key_counts = (
    df.groupBy("customer_id")
      .count()
      .withColumn(
          "share",
          F.col("count") / F.lit(total_rows)
      )
      .orderBy(F.desc("count"))
)

key_counts.show(20, truncate=False)
```

Questions:

1. Which keys dominate?
2. What percentage does the top key own?
3. How much work is represented by NULL?
4. Are the top five keys unusually large?
5. Is the skew legitimate business behavior or a data-quality issue?

Do not optimize before answering those questions.

---

## 70. Mini Project — Baseline Aggregation

```python
baseline_agg = (
    df.groupBy("customer_id")
      .agg(
          F.sum("revenue").alias("total_revenue"),
          F.count("*").alias("row_count")
      )
)

baseline_agg.count()
```

Record:

```text
runtime:
task distribution:
shuffle behavior:
correctness:
```

Do not invent the values.

---

## 71. Mini Project — Baseline Join

Create a small dimension:

```python
dimension = (
    df.select("customer_id")
      .where(F.col("customer_id").isNotNull())
      .distinct()
      .withColumn(
          "customer_name",
          F.concat(F.lit("customer-"), F.col("customer_id"))
      )
)
```

Then:

```python
baseline_join = df.join(
    dimension,
    on="customer_id",
    how="left"
)
```

Before benchmarking, inspect:

```python
dimension.count()
```

and determine whether it is genuinely small enough for a broadcast experiment.

Do not assume it is.

---

## 72. Mini Project — NULL Handling Experiment

Split:

```python
normal = df.filter(
    F.col("customer_id").isNotNull()
)

unknown = df.filter(
    F.col("customer_id").isNull()
)
```

Process them separately according to a defined business rule.

Then validate:

```text
original row count
=
normal row count + unknown row count
```

This is a correctness check.

---

## 73. Mini Project — Pre-Aggregation Experiment

```python
summary = (
    df.filter(F.col("customer_id").isNotNull())
      .groupBy("customer_id")
      .agg(
          F.sum("revenue").alias("total_revenue")
      )
)
```

Compare a downstream join against the raw transaction join.

Record:

```text
input rows to join
shuffle
runtime
result correctness
```

The purpose is to determine whether reducing the data before the join is semantically valid and operationally useful.

---

## 74. Mini Project — Broadcast Experiment

If the dimension is genuinely small:

```python
broadcast_join = df.join(
    F.broadcast(dimension),
    on="customer_id",
    how="left"
)
```

Compare against baseline.

Record:

```text
runtime
memory behavior
shuffle behavior
correctness
```

Do not assume broadcast wins.

---

## 75. Mini Project — Salting Experiment

```python
from pyspark.sql import functions as F

salt_count = 16

fact_salted = (
    df
    .withColumn(
        "salt",
        F.floor(
            F.rand(seed=42) * salt_count
        ).cast("int")
    )
)

salt_values = (
    spark.range(salt_count)
         .withColumnRenamed("id", "salt")
         .withColumn(
             "salt",
             F.col("salt").cast("int")
         )
)

dimension_salted = (
    dimension
    .crossJoin(salt_values)
)

salted_join = (
    fact_salted
    .join(
        dimension_salted,
        on=["customer_id", "salt"],
        how="left"
    )
)
```

### Important production refinement

This example salts every row.

For a production workload where only a few keys are hot, selective salting may be more appropriate.

Do not treat this as a universal implementation.

---

## 76. Mini Project — Salt Range Experiment

Test a small set of candidate ranges:

```text
2
4
8
16
32
```

For each candidate, record:

```text
salt_count
runtime
shuffle read
shuffle write
max task time
median task time
replicated dimension size
memory pressure
correctness
```

Do not choose the maximum value automatically.

---

## 77. Mini Project — Hot-Key Isolation

First identify hot keys.

For example:

```python
hot_keys = (
    key_counts
    .filter(F.col("share") > F.lit(0.05))
    .select("customer_id")
)
```

The threshold above is an **experiment parameter**, not a universal skew threshold.

Use the actual workload to define what deserves special treatment.

Then conceptually split:

```text
hot
normal
```

and process them differently.

Validate the union:

```text
hot result
+
normal result
=
expected complete result
```

---

## 78. Mini Project — Two-Phase Aggregation

```python
salt_count = 16

partial = (
    df
    .withColumn(
        "salt",
        F.pmod(
            F.hash("id"),
            F.lit(salt_count)
        ).cast("int")
    )
    .groupBy("customer_id", "salt")
    .agg(
        F.sum("revenue").alias("partial_revenue")
    )
)

final = (
    partial
    .groupBy("customer_id")
    .agg(
        F.sum("partial_revenue").alias("total_revenue")
    )
)
```

Validate against the direct aggregation.

For example, compare:

```text
customer_id
total_revenue
```

between the baseline and two-phase results.

---

## 79. Mini Project — AQE Experiment

For an experiment, use Spark configuration appropriate to your Spark version/environment.

Conceptually compare:

```text
AQE ON
```

against:

```text
AQE OFF
```

and record actual results.

Do not assume that AQE will always outperform manual salting.

The point is to understand:

```text
What does Spark solve automatically?
What still requires application-level reasoning?
```

---

## 80. Mini Project — Final Engineering Report

Your final report should contain:

```text
1. Problem
2. Evidence of skew
3. Hot keys
4. Root cause
5. Baseline performance
6. Candidate mitigations
7. AQE result
8. Broadcast result
9. Pre-aggregation result
10. Salting result
11. Hot-key isolation result
12. Two-phase aggregation result
13. Correctness comparison
14. Cost comparison
15. Final decision
16. Why the decision is justified
17. What you would monitor in production
```

The final recommendation must be workload-specific.

Do not write:

> "Salting is the best technique."

Write something like:

> "For this workload, the measured evidence showed that ______ reduced the straggler tail while preserving correctness at an acceptable replication cost."

---

## 81. Hands-On Labs

### Lab 1 — Create a Balanced Dataset

**Objective:** Establish a baseline without skew.

**Setup:**

Create data where key frequencies are approximately balanced.

**Task:** Count key frequencies.

**Expected behavior:** No single key should dominate.

**Hint:** Use a reasonably distributed identifier.

**Verification:** Inspect top-key shares.

**Common mistake:** Assuming balanced partitions simply because key counts look similar.

---

### Lab 2 — Create a Deliberately Skewed Dataset

**Objective:** Create a dataset with one dominant key.

**Task:** Make one key own a large fraction of the rows.

**Expected behavior:** Key-frequency analysis should reveal the hot key.

**Hint:** Use conditional expressions.

**Verification:** Calculate key share.

**Common mistake:** Changing partition count instead of changing key frequency.

---

### Lab 3 — Detect Hot Keys

**Objective:** Identify top keys.

```python
df.groupBy("customer_id").count().orderBy(
    F.desc("count")
).show(20)
```

**Expected behavior:** Hot keys appear at the top.

**Verification:** Explain why a hot key can create skew.

**Common mistake:** Treating every high-frequency key as automatically pathological.

---

### Lab 4 — Detect NULL/Default-Key Skew

**Objective:** Find NULL and placeholder concentrations.

**Task:** Analyze:

```text
NULL
UNKNOWN
0
-1
```

where applicable.

**Expected behavior:** One or more placeholders may dominate.

**Verification:** Calculate their shares.

**Common mistake:** Replacing NULL values without understanding business semantics.

---

### Lab 5 — Create a Skewed Aggregation

**Objective:** Create a groupBy workload with a hot key.

**Task:** Aggregate by `customer_id`.

**Expected behavior:** The hot key creates disproportionate work.

**Hint:** Compare key frequencies before the aggregation.

**Verification:** Explain why the output can be small even when the computation is large.

**Common mistake:** Looking only at output row count.

---

### Lab 6 — Create a Skewed Join

**Objective:** Demonstrate join skew.

**Task:** Create a hot key on the large side and join to another dataset.

**Expected behavior:** One or a few tasks may dominate.

**Verification:** Compare task-time distribution.

**Common mistake:** Calling the problem "too few partitions" without inspecting key distribution.

---

### Lab 7 — Compare Max vs Median

**Objective:** Learn a practical skew signal.

**Task:** Record maximum and median task duration.

**Expected behavior:** A skewed workload may have a very large max/median gap.

**Verification:** Explain why the ratio is a signal, not a universal threshold.

**Common mistake:** Declaring skew from one metric alone.

---

### Lab 8 — Fix NULL/Default-Key Skew

**Objective:** Separate pathological NULL/default records.

**Task:** Process normal and unknown records separately.

**Expected behavior:** The normal path no longer carries the same concentration.

**Verification:** Validate row-count conservation.

**Common mistake:** Dropping the unknown records accidentally.

---

### Lab 9 — Apply Pre-Aggregation

**Objective:** Reduce join input before joining.

**Task:** Aggregate transactions by customer before joining to a dimension.

**Expected behavior:** The join input becomes smaller.

**Verification:** Confirm that the business result is still correct.

**Common mistake:** Pre-aggregating when row-level detail is required.

---

### Lab 10 — Apply Broadcast

**Objective:** Test broadcast as a skew mitigation.

**Task:** Broadcast a genuinely small dimension.

**Expected behavior:** Some shuffle work can be avoided.

**Verification:** Compare runtime and memory behavior.

**Common mistake:** Broadcasting a large dataset.

---

### Lab 11 — Implement Basic Salting

**Objective:** Understand the mechanics of a salted join.

**Task:** Add salt to the skewed side and replicate the other side.

**Expected behavior:** Hot-key records can be distributed across multiple salt values.

**Verification:** Validate join correctness.

**Common mistake:** Replicating the dimension but omitting salt from the join condition.

---

### Lab 12 — Compare Salting and Hot-Key Isolation

**Objective:** Compare two advanced approaches.

**Task:** Implement:

```text
Approach A → salt all relevant rows
Approach B → isolate hot keys
```

**Expected behavior:** Each has different cost characteristics.

**Verification:** Compare runtime, shuffle, replication, and code complexity.

**Common mistake:** Declaring one universally superior.

---

### Lab 13 — Two-Phase Aggregation

**Objective:** Distribute a skewed aggregation.

**Task:** Aggregate by:

```text
(customer_id, salt)
```

then by:

```text
customer_id
```

**Expected behavior:** The hot key's work is split into partial aggregates.

**Verification:** Compare final totals against the direct aggregation.

**Common mistake:** Using an aggregation that is not safely decomposable without checking semantics.

---

### Lab 14 — Full Skew Remediation Experiment

**Objective:** Conduct a production-style comparison.

Compare:

```text
baseline
NULL/default handling
pre-aggregation
broadcast
AQE
salting
hot-key isolation
two-phase aggregation
```

**Expected behavior:** Different techniques have different costs.

**Verification:** Produce a measurement table.

**Common mistake:** Optimizing without a baseline.

---

### Lab 15 — Full Comparison Experiment

**Objective:** Produce a final engineering recommendation.

**Task:** Run AQE ON/OFF experiments and compare candidate salt ranges.

**Expected behavior:** The results should be workload-specific.

**Verification:** Explain the final choice using evidence and correctness.

**Common mistake:** Treating benchmark results as universal Spark rules.

---

## 82. Debugging Exercises

### Scenario 1 — One Task Takes 45 Minutes

**Symptom:** Most tasks finish in seconds; one takes 45 minutes.

**Diagnosis:** Strong signal of a straggler.

**Investigation:**

- compare max and median task time;
- inspect shuffle read;
- inspect input distribution;
- identify top keys.

**Likely cause:** Hot-key skew.

**Fix:** Choose an appropriate mitigation after measuring.

**Validation:** Compare task-time distribution before and after.

---

### Scenario 2 — Huge Shuffle Read on One Task

**Symptom:** One task reads dramatically more shuffle data.

**Diagnosis:** Possible skewed shuffle partition.

**Investigation:** Identify which key frequencies produce the concentration.

**Likely cause:** Hot key.

**Fix:** AQE skew handling, isolation, or salting depending on evidence.

**Validation:** Compare shuffle and task metrics.

---

### Scenario 3 — NULL Represents 40% of Events

**Symptom:** `NULL` dominates key frequency.

**Diagnosis:** NULL/default-key skew.

**Investigation:** Confirm business meaning.

**Likely cause:** Missing customer identity.

**Fix:** Separate processing or business-defined fallback.

**Validation:** Preserve all required records.

---

### Scenario 4 — Broadcast Causes Memory Pressure

**Symptom:** Executor memory pressure increases after adding broadcast.

**Diagnosis:** Broadcast side may not be sufficiently small.

**Investigation:** Measure actual dimension size and executor memory.

**Likely cause:** Blind broadcasting.

**Fix:** Remove broadcast or choose another strategy.

**Validation:** Compare runtime and memory behavior.

---

### Scenario 5 — Salting Makes the Job Slower

**Symptom:** Stragglers decrease but total runtime increases.

**Diagnosis:** Salting may have traded skew cost for replication and extra computation.

**Investigation:**

- replication size;
- shuffle;
- CPU;
- max/median task time.

**Likely cause:** Salting cost exceeds benefit.

**Fix:** Tune salt range or choose isolation/AQE/broadcast.

**Validation:** Compare end-to-end cost.

---

### Scenario 6 — Salt Range Is Too Small

**Symptom:** One salted task remains disproportionately large.

**Diagnosis:** The hot key is still concentrated.

**Investigation:** Compare task distribution across salt values.

**Likely cause:** Insufficient salt range.

**Fix:** Test a larger candidate range.

**Validation:** Measure again.

---

### Scenario 7 — Salt Range Is Too Large

**Symptom:** Runtime increases and the replicated side becomes much larger.

**Diagnosis:** Over-salting.

**Investigation:** Measure replication and shuffle.

**Likely cause:** Salt range exceeds what the workload needs.

**Fix:** Reduce candidate range.

**Validation:** Compare skew reduction against added cost.

---

### Scenario 8 — Salted Join Produces Duplicates

**Symptom:** Output row count is larger than expected.

**Diagnosis:** Join correctness problem.

**Investigation:** Check whether the salt participates in the join condition.

**Likely cause:** Replicated dimension joined only on the original key.

**Fix:**

```text
customer_id + salt
```

must participate in the salted join.

**Validation:** Compare key-level row counts.

---

### Scenario 9 — Two-Phase Aggregation Changes Totals

**Symptom:** Final aggregate differs from baseline.

**Diagnosis:** Correctness failure.

**Investigation:**

- compare key-level totals;
- inspect salt generation;
- inspect partial aggregate;
- check NULL behavior.

**Likely cause:** Incorrect transformation or non-decomposable aggregation semantics.

**Fix:** Correct the aggregation design.

**Validation:** Require equality with the trusted baseline.

---

### Scenario 10 — AQE Improves the Join Automatically

**Symptom:** The join becomes faster after AQE is enabled without application code changes.

**Diagnosis:** Runtime adaptive behavior may be mitigating skew.

**Investigation:** Compare AQE ON/OFF and inspect execution behavior.

**Likely cause:** AQE skew-join handling.

**Fix:** Do not automatically add manual salting.

**Validation:** Determine whether AQE already provides sufficient improvement.

---

### Scenario 11 — More Executors Do Not Help

**Symptom:** Cluster size increases, but the job still waits on one task.

**Diagnosis:** Capacity increased without changing the skewed work unit.

**Investigation:** Identify the dominant key and partition.

**Likely cause:** One hot key remains concentrated.

**Fix:** Address the distribution problem.

**Validation:** Compare the straggler tail.

---

### Scenario 12 — Developer Blames Partition Count

**Symptom:** A team immediately increases partitions.

**Diagnosis:** The root cause has not been established.

**Investigation:** Compare key frequencies and task distribution.

**Likely cause:** Confusion between insufficient partition count and skew.

**Fix:** Diagnose the data distribution first.

**Validation:** Only change partition count if evidence supports it.

---

## 83. Practice Questions

Exactly 40 questions follow: 10 Basic, 10 Moderate, 10 Hard, and 10 Advanced.

### 10 Basic

#### B1. What is data skew?

**Answer:** Data skew is an uneven distribution of data or computational work across partitions.

**Explanation:** Some partitions contain substantially more work than others.

---

#### B2. What is a hot key?

**Answer:** A key value that occurs disproportionately often and creates unusually large processing work.

**Explanation:** A hot key can concentrate data into one or a few partitions.

---

#### B3. What is a straggler task?

**Answer:** A task that takes substantially longer than its peers.

**Explanation:** A straggler can keep a stage running after most other tasks finish.

---

#### B4. How is skew different from too few partitions?

**Answer:** Too few partitions means insufficient work units; skew means work is unevenly distributed among the existing units.

**Explanation:** Increasing partition count does not automatically redistribute a hot key.

---

#### B5. Why can NULL create skew?

**Answer:** A large number of NULL records can behave as a concentrated grouping or join category.

**Explanation:** If many records share the same missing-value representation, one part of the workload can dominate.

---

#### B6. What is a key-frequency analysis?

**Answer:** Counting how many records belong to each key and examining the most frequent keys.

**Example:**

```python
df.groupBy("customer_id").count().orderBy(
    F.desc("count")
)
```

---

#### B7. What does max versus median task time tell you?

**Answer:** A large difference can signal uneven work or stragglers.

**Explanation:** It is a diagnostic signal, not a universal skew threshold.

---

#### B8. Can adding more executors automatically fix skew?

**Answer:** No.

**Explanation:** If one hot key remains concentrated in one dominant task, extra executors do not necessarily split that work.

---

#### B9. What is salting?

**Answer:** Adding an artificial value to a skewed key so that one hot key can be represented by multiple physical distribution keys.

**Explanation:** This can spread work across multiple partitions.

---

#### B10. Does salting always improve performance?

**Answer:** No.

**Explanation:** Salting introduces replication, extra data movement, computation, and complexity.

---

### 10 Moderate

#### M1. How can you calculate a hot-key share?

**Answer:**

```text
key share = key_count / total_row_count
```

**Explanation:** It measures how much of the dataset belongs to a key.

---

#### M2. Why is one key owning 30% of the dataset suspicious?

**Answer:** Because a single key represents a very large fraction of the workload and may create a disproportionately large partition or task.

**Explanation:** The exact threshold for action is workload-dependent.

---

#### M3. How can time-based behavior create skew?

**Answer:** A period such as a product launch or Black Friday can produce far more records than normal periods.

**Explanation:** The same partitioning key can become highly uneven as traffic changes.

---

#### M4. How can a bad partitioning column create skew?

**Answer:** A column with few distinct values or highly uneven frequencies can concentrate data.

**Explanation:** The partitioning strategy follows the data distribution of the selected key.

---

#### M5. How can pre-aggregation reduce skew pressure?

**Answer:** It can reduce the number of rows participating in a downstream join or aggregation.

**Explanation:** This works only when aggregation before the downstream operation preserves required semantics.

---

#### M6. When can broadcast help with skew?

**Answer:** When one join side is genuinely small enough to broadcast safely.

**Explanation:** It can avoid some shuffle of the small side.

---

#### M7. Why does AQE matter for skew?

**Answer:** AQE can use runtime information to identify and split certain skewed shuffle partitions in supported join scenarios.

**Explanation:** Runtime data can reveal skew that was not fully known at planning time.

---

#### M8. Why does a salted join need the other side replicated?

**Answer:** Because the join key becomes a combination such as `(customer_id, salt)`.

**Explanation:** The non-skewed side needs matching rows for the possible salt values.

---

#### M9. Why can hot-key isolation be cheaper than salting everything?

**Answer:** Only pathological keys receive the expensive special treatment.

**Explanation:** Normal keys continue through the standard path.

---

#### M10. Why can a small output still represent a large computation?

**Answer:** Aggregations can consume millions of input rows and produce one output row per key.

**Explanation:** Output size is not a direct measure of processing cost.

---

### 10 Hard

#### H1. Explain why increasing partitions may not fix a hot key.

**Answer:** If the partitioning function continues to map the same hot key to one dominant partition, increasing the number of partitions changes the number of buckets but does not necessarily split the hot key's work.

**Explanation:** The problem is concentration by key, not merely the number of partitions.

---

#### H2. A join has one hot key on both sides. Why is this especially dangerous?

**Answer:** Both sides can contain large numbers of rows for the same key, producing a very large amount of join work and potentially an enormous result.

**Explanation:** Skew and many-to-many cardinality can compound.

---

#### H3. What are the main costs of salting a join?

**Answer:** Extra salt generation, replication of the other side, more rows, more shuffle, more computation, and increased implementation complexity.

**Explanation:** Salting trades distribution imbalance for additional work.

---

#### H4. Why is `salt_count = 10_000` not automatically better than `salt_count = 16`?

**Answer:** A larger range may reduce hot-key concentration further but can massively increase replication and overhead.

**Explanation:** The correct salt range is workload-dependent.

---

#### H5. Compare random and deterministic salting.

**Answer:** Random salting assigns salt probabilistically, while deterministic salting derives the salt from stable input data such as a hash.

**Explanation:** Deterministic approaches can make assignment reproducible, but neither guarantees perfect balance.

---

#### H6. How can two-phase aggregation mitigate skew?

**Answer:** First aggregate by `(key, salt)` and then combine the partial aggregates by `key`.

**Explanation:** The hot key's input work is divided among multiple partial groups.

---

#### H7. Why can a salted join produce duplicates?

**Answer:** If the replicated side is joined only on the original key and not the salt, one fact row can match multiple replicated copies.

**Explanation:** The salt must participate in the physical join condition.

---

#### H8. Why can NULL/default-key isolation be preferable to salting?

**Answer:** If the skew comes from a small number of known exceptional values, a separate business-defined path can solve the concentration without replicating the entire dataset or dimension.

**Explanation:** Simpler mitigation can have lower cost and complexity.

---

#### H9. Why should you compare maximum and median task time?

**Answer:** Their difference reveals whether a small number of tasks are taking disproportionately longer than typical tasks.

**Explanation:** This is a useful skew signal when combined with shuffle and data evidence.

---

#### H10. Why must correctness be validated after salting?

**Answer:** Salting changes the physical join/grouping representation and can introduce duplicate matches or incorrect aggregation if implemented incorrectly.

**Explanation:** Performance improvement is irrelevant if business results change.

---

### 10 Advanced

#### A1. A hot key represents 30% of a fact table and joins to a large dimension. How would you investigate?

**Answer:** Profile key frequency on both sides, measure task and shuffle imbalance, inspect join cardinality, determine whether the dimension can be broadcast, evaluate pre-aggregation or isolation, test AQE, and only then consider selective salting.

**Explanation:** The correct solution depends on data shape and measured cost.

---

#### A2. How would you choose a salt range?

**Answer:** Start from the hot-key volume and available parallelism, then test candidate ranges while measuring task distribution, shuffle, replication cost, memory, runtime, and correctness.

**Explanation:** There is no universal correct salt range.

---

#### A3. When would you choose hot-key isolation over salting?

**Answer:** When a small number of identifiable keys cause the problem and can be handled with a simpler special strategy.

**Explanation:** Selective treatment can avoid paying salting overhead for normal data.

---

#### A4. When can AQE make manual salting unnecessary?

**Answer:** When AQE's supported skew handling sufficiently reduces the skewed join's straggler behavior and the measured result is acceptable.

**Explanation:** Manual salting adds complexity and should not be added without evidence of additional benefit.

---

#### A5. Why can adding executors fail to solve a skewed stage?

**Answer:** More executors add capacity, but they do not necessarily divide a single hot-key task into smaller tasks.

**Explanation:** The bottleneck is the size and concentration of the work unit.

---

#### A6. How would you prove a salting optimization is successful?

**Answer:** Demonstrate preserved correctness and compare baseline versus salted runtime, max/median task time, shuffle volume, spill, memory behavior, and replication cost.

**Explanation:** A shorter straggler tail alone does not prove that end-to-end performance improved.

---

#### A7. A salted join reduces maximum task time but increases total runtime. What might be happening?

**Answer:** The skew was reduced, but the cost of replication, shuffle, or additional computation exceeded the saved straggler time.

**Explanation:** Optimization should be judged on end-to-end workload cost.

---

#### A8. Why can window-function skew be harder to fix with salting?

**Answer:** Window semantics can require all rows for a logical partition to remain related, so arbitrarily splitting the partition can change the computation.

**Explanation:** Correctness constraints can limit distribution-based techniques.

---

#### A9. How would you distinguish legitimate business skew from data-quality skew?

**Answer:** Investigate the meaning and lineage of the hot key. A highly active real customer may be legitimate, while `"UNKNOWN"` or `-1` may indicate missing data.

**Explanation:** The mitigation should address the cause rather than blindly optimizing the symptom.

---

#### A10. Design a production skew-remediation strategy.

**Answer:** Establish a baseline, profile key distribution, identify hot keys and NULL/default concentration, diagnose whether the problem is join/aggregation/window/write related, test the simplest valid mitigation, compare AQE/broadcast/pre-aggregation/isolation/salting as appropriate, validate correctness, measure cost, and monitor the chosen strategy over time.

**Explanation:** Skew remediation is an evidence-driven engineering process, not a single API call.

---

## 84. Interview Questions

### Basic

1. What is data skew?
2. Why is skew a problem in distributed systems?
3. What is a hot key?
4. What is a straggler task?
5. How do you detect skew from data?
6. How do NULL/default keys create skew?
7. Why is max versus median task time useful?
8. Why does adding executors not necessarily solve skew?

### Intermediate

9. How does skew affect a join?
10. How does skew affect aggregation?
11. How does time-based traffic create skew?
12. What makes a partitioning column problematic?
13. When can pre-aggregation help?
14. When can broadcast help?
15. What is AQE skew join handling?
16. How would you investigate a task with huge shuffle read?

### Advanced

17. Explain salting to an engineer who understands SQL but not distributed systems.
18. Why does the skewed side receive the salt?
19. Why must the other side be replicated?
20. How would you choose a salt range?
21. Compare random and deterministic salting.
22. What is hot-key isolation?
23. What is two-phase aggregation?
24. What are the costs of salting?
25. When would you avoid salting?
26. How do you validate correctness after salting?

### Senior Data Engineer

27. Why can a single hot key keep an entire Spark job running after most tasks finish?
28. How would you distinguish partition-count problems from skew problems?
29. How would you diagnose a skewed large-large join?
30. How would you decide between AQE, broadcast, pre-aggregation, hot-key isolation, and salting?
31. How would you make a skew mitigation robust as data volume changes?
32. What metrics would you put into operational monitoring for skew?
33. How would you detect that a previously safe broadcast strategy has become unsafe?
34. How would you prevent a salting optimization from silently changing business results?

### Distributed Systems Architecture

35. Explain the trade-off between replication and parallelism in a salted join.
36. Why is skew a long-tail problem?
37. Why can a workload be skewed even when the average partition size looks acceptable?
38. How would you design a skew-remediation framework for multiple pipelines?
39. How should skew handling interact with AQE?
40. How would you decide whether skew is significant enough to justify application complexity?

---

## 85. Architecture Questions

### Scenario 1 — Hot Customer

A customer represents approximately 30% of a fact table.

The fact joins a large dimension.

Symptoms:

```text
most tasks → seconds
one task   → 45 minutes
```

Questions:

1. How would you prove the hot customer is the cause?
2. What would you inspect on both join sides?
3. Could join explosion be involved?
4. Could broadcast help?
5. Could hot-key isolation help?
6. When would salting become reasonable?
7. What would you measure after the change?

Strong reasoning should begin with evidence rather than immediately selecting salting.

---

### Scenario 2 — NULL Explosion

NULL customer IDs represent approximately 40% of events.

Questions:

1. Is this business-valid or a data-quality issue?
2. How would you isolate the NULL records?
3. What should happen to them semantically?
4. Would salting them be appropriate?
5. How would you validate row conservation?

The key lesson:

> A data-quality problem should not automatically be converted into an execution-optimization problem.

---

### Scenario 3 — Large-Large Join

Both sides are large.

One key is extremely hot on both sides.

Questions:

1. What makes this more difficult than a small-large join?
2. What join-cardinality analysis is required?
3. Can broadcast realistically solve it?
4. Could pre-aggregation help?
5. Could hot-key isolation help?
6. How would salting work?
7. What are the replication costs?
8. What correctness checks are mandatory?

---

### Scenario 4 — Small Dimension

The fact table is huge and skewed.

The dimension is genuinely small.

Questions:

1. Should broadcast be considered?
2. What evidence is required before broadcasting?
3. What memory risks exist?
4. Would AQE still be relevant?
5. Would salting necessarily be justified?

The answer must be evidence-driven.

---

### Scenario 5 — Salted Join Regression

Salting reduces maximum task duration:

```text
45 min → 5 min
```

but total runtime changes:

```text
20 min → 28 min
```

Questions:

1. Did salting solve the skew?
2. Did it improve the end-to-end workload?
3. What additional metrics would you inspect?
4. Is the regression caused by replication?
5. Could a smaller salt range work?
6. Could hot-key isolation be simpler?
7. Could AQE provide sufficient mitigation?

Do not answer with a universal "salting is bad."

The decision depends on the workload and business objective.

---

### Scenario 6 — AQE vs Manual Salting

AQE appears to split skewed partitions successfully.

Questions:

1. Why might manual salting still be unnecessary?
2. What measurements would support keeping AQE alone?
3. When might manual salting still be considered?
4. What complexity does manual salting introduce?
5. How would you compare AQE ON/OFF?
6. What correctness checks would you run?

---

### Scenario 7 — Skewed Aggregation

One customer owns most transactions.

A direct:

```python
groupBy("customer_id")
```

creates one dominant task.

Questions:

1. Could pre-aggregation help?
2. How could two-phase aggregation distribute work?
3. What properties must the aggregate have?
4. How would you validate totals?
5. What would you measure?

---

### Scenario 8 — Window Skew

One tenant owns 80% of all events.

A window partitions by:

```text
tenant_id
```

Questions:

1. Why is this a skew problem?
2. Why might salting change semantics?
3. Could the business computation be redesigned?
4. Could pathological tenants be isolated?
5. What correctness constraints must remain intact?

---

## 86. Common Misconceptions

### Misconception 1 — "More partitions automatically fix skew."

**Why it sounds reasonable:** More partitions usually expose more parallel work.

**Why it is incomplete:** A hot key can remain concentrated in one partitioning destination.

**Correct mental model:** Diagnose key distribution first.

**Production implication:** Avoid blindly increasing partition count.

---

### Misconception 2 — "Adding more executors automatically fixes skew."

**Why it sounds reasonable:** More machines should mean more capacity.

**Why it is incomplete:** One hot task may still contain the dominant work.

**Correct mental model:** Capacity cannot help if the work is not divisible.

**Production implication:** Fix distribution when distribution is the bottleneck.

---

### Misconception 3 — "One hot key means the whole dataset is bad."

**Why it sounds reasonable:** The job is slow because of that key.

**Why it is incomplete:** The rest of the data may be perfectly healthy.

**Correct mental model:** Isolate the pathological portion when appropriate.

**Production implication:** Hot-key isolation can be preferable to globally transforming the dataset.

---

### Misconception 4 — "Broadcast always fixes skew."

**Why it sounds reasonable:** Broadcast avoids shuffle.

**Why it is incomplete:** It requires a sufficiently small side and can create memory pressure.

**Correct mental model:** Broadcast is one candidate mitigation.

**Production implication:** Measure size and memory behavior.

---

### Misconception 5 — "Salting always improves performance."

**Why it sounds reasonable:** It spreads hot-key work.

**Why it is incomplete:** Replication and additional computation can outweigh the benefit.

**Correct mental model:** Salting trades skew for extra work.

**Production implication:** Benchmark before keeping it.

---

### Misconception 6 — "The larger the salt range, the better."

**Why it sounds reasonable:** More salt values mean more distribution.

**Why it is incomplete:** Replication cost also grows.

**Correct mental model:** Find an appropriate range experimentally.

**Production implication:** Optimize the trade-off.

---

### Misconception 7 — "Random salting guarantees perfect balance."

**Why it sounds reasonable:** Randomness spreads records.

**Why it is incomplete:** Random distribution is probabilistic.

**Correct mental model:** Random salting can improve distribution without guaranteeing equality.

**Production implication:** Measure actual task distribution.

---

### Misconception 8 — "Every skewed join should be salted."

**Why it sounds reasonable:** Salting is a known skew technique.

**Why it is incomplete:** AQE, broadcast, pre-aggregation, or isolation may be simpler.

**Correct mental model:** Choose the simplest valid mitigation.

**Production implication:** Avoid unnecessary complexity.

---

### Misconception 9 — "NULL is just another ordinary value."

**Why it sounds reasonable:** It is represented as a value in the schema.

**Why it is incomplete:** A large concentration of NULL records can represent a major missing-data category.

**Correct mental model:** Inspect its frequency and business meaning.

**Production implication:** Data-quality handling may be the right fix.

---

### Misconception 10 — "AQE makes manual skew reasoning unnecessary."

**Why it sounds reasonable:** AQE adapts at runtime.

**Why it is incomplete:** AQE handles supported scenarios and does not eliminate data-model or business-semantic reasoning.

**Correct mental model:** AQE is one layer of mitigation.

**Production implication:** Understand the workload before relying on automation.

---

## 87. Learning Checkpoints

### Checkpoint A — Fundamentals

- Can you explain skew in one sentence?
- Can you distinguish skew from too few partitions?
- Can you explain why one straggler can delay a job?

### Checkpoint B — Detection

- Can you identify a hot key?
- Can you calculate key share?
- Can you compare maximum and median task time?
- Can you interpret shuffle-read imbalance?

### Checkpoint C — First-Line Fixes

- Can you identify NULL/default-key skew?
- Can you explain when pre-aggregation helps?
- Can you explain when broadcast can help?
- Can you explain why more executors may not help?

### Checkpoint D — AQE and Salting

- Can you explain AQE skew handling?
- Can you explain why salting works?
- Can you explain why the other side is replicated?
- Can you explain salt-range trade-offs?

### Checkpoint E — Advanced Strategies

- Can you explain hot-key isolation?
- Can you implement two-phase aggregation?
- Can you explain salting cost?
- Can you identify when not to salt?

### Checkpoint F — Production

- Can you design a measurement plan?
- Can you validate correctness?
- Can you compare AQE, broadcast, pre-aggregation, isolation, and salting?
- Can you make a workload-specific production decision?

---

## 88. Final Knowledge Assessment

### 10 Conceptual Questions

1. Define data skew.
2. Distinguish skew from insufficient partition count.
3. Define a hot key.
4. Explain a straggler task.
5. Explain NULL/default-key skew.
6. Explain max versus median task-time reasoning.
7. Explain join skew.
8. Explain aggregation skew.
9. Explain why salting works.
10. Explain the cost of salting.

### 5 Code-Reading Questions

#### Code 1

```python
df.groupBy("customer_id").count().orderBy(
    F.desc("count")
).show(20)
```

What is this useful for?

**Expected:** Detecting high-frequency keys.

#### Code 2

```python
F.floor(F.rand(seed=42) * 16)
```

What is this doing?

**Expected:** Generating a bounded integer salt value.

#### Code 3

```python
dimension.crossJoin(salt_values)
```

Why is this present in a salted join?

**Expected:** Replicating dimension rows across salt values.

#### Code 4

```python
.groupBy("customer_id", "salt")
```

Why is salt included?

**Expected:** To create multiple partial groups for a hot key.

#### Code 5

```python
.groupBy("customer_id")
.agg(F.sum("partial_revenue"))
```

Why is this second aggregation needed?

**Expected:** To combine the partial results back into the original business key.

### 5 Debugging Problems

1. One task takes 45 minutes.
2. NULL represents 40% of rows.
3. Salting makes the job slower.
4. Salted join creates duplicates.
5. AQE already removes the straggler.

For each, provide:

```text
Symptom
Diagnosis
Investigation
Likely cause
Correction
Validation
```

### 5 Production Architecture Problems

1. Hot customer in a large-large join.
2. NULL/default-key explosion.
3. Small dimension with skewed fact.
4. Salted join regression.
5. AQE versus manual salting.

Passing requires evidence-based reasoning rather than memorized recommendations.

---

## 89. Final Summary

The complete conceptual progression is:

```text
Distributed Data
       ↓
Partitions
       ↓
Uneven Key Frequencies
       ↓
Data Skew
       ↓
Hot Keys
       ↓
Uneven Partitions
       ↓
Straggler Tasks
       ↓
Long-Tail Jobs
       ↓
Detection
       ↓
First-Line Fixes
       ↓
AQE / Broadcast / Pre-Aggregation
       ↓
Hot-Key Isolation
       ↓
Salting
       ↓
Two-Phase Aggregation
       ↓
Measurement
       ↓
Production Decision
```

The central production principle is:

> **The learner must understand the problem before applying the optimization.**

A mature Spark engineer does not begin with:

```python
salt_count = 16
```

A mature Spark engineer begins with:

```text
Why is this job skewed?
```

Then:

```text
Which keys are responsible?
```

Then:

```text
What is the simplest correct mitigation?
```

Then:

```text
Did it actually improve the workload?
```

Then:

```text
Did it preserve correctness?
```

---

## 90. What You Should Be Able to Do Now

You should now be able to:

- define data skew;
- explain balanced versus skewed partitions;
- distinguish skew from too few partitions;
- explain hot keys;
- detect NULL/default-key concentration;
- recognize time-based skew;
- identify problematic partitioning columns;
- recognize straggler tasks;
- reason using max versus median task time;
- inspect shuffle-read imbalance conceptually;
- analyze key frequency;
- calculate key share;
- explain join skew;
- explain join explosion combined with skew;
- explain aggregation skew;
- explain window-function skew;
- explain write skew;
- apply NULL/default-key handling;
- use pre-aggregation where semantically valid;
- consider broadcast when a side is genuinely small;
- explain AQE skew-join handling;
- implement a basic salted join;
- replicate the non-skewed side correctly;
- choose candidate salt ranges experimentally;
- distinguish random and deterministic salting;
- selectively salt hot keys;
- isolate hot keys;
- implement two-phase aggregation;
- explain the cost of salting;
- identify when not to salt;
- validate correctness;
- measure before and after;
- compare alternative strategies;
- make a production decision based on evidence.

---

## 91. Glossary

**Data Skew** — Uneven distribution of data or computational work across partitions.

**Partition Skew** — Uneven data volume or processing work among execution partitions.

**Key Skew** — Uneven frequency of values in a key column.

**Hot Key** — A key value occurring disproportionately often.

**Straggler Task** — A task that takes substantially longer than peer tasks.

**Long Tail** — A small number of slow tasks extending overall job completion time.

**Shuffle** — Redistribution of records between partitions.

**Shuffle Read** — Data read by a task from shuffle output.

**Shuffle Write** — Data written as shuffle output for downstream tasks.

**Key Frequency** — Number of records associated with a key.

**Key Share** — A key's record count divided by total record count.

**NULL Key** — A missing key value that may become a concentrated category.

**Default Key** — A placeholder such as `"UNKNOWN"`, `0`, or `-1`.

**Broadcast** — Replication of a sufficiently small dataset to executors to avoid certain shuffle patterns.

**AQE** — Adaptive Query Execution, Spark's runtime adaptation mechanism.

**AQE Skew Join Handling** — Adaptive handling that can split oversized skewed shuffle partitions in supported join scenarios.

**Salting** — Adding an artificial value to a key to create multiple physical distribution keys.

**Salt** — The artificial value added to a business key.

**Salt Range** — The set or count of salt values used to distribute a hot key.

**Hot-Key Isolation** — Processing pathological hot keys separately from normal keys.

**Pre-Aggregation** — Reducing data through aggregation before a downstream operation.

**Two-Phase Aggregation** — Partial aggregation using a finer key such as `(key, salt)` followed by final aggregation by the original key.

**Window Skew** — Uneven computational or memory burden caused by extremely large logical window partitions.

**Write Skew** — Uneven work or output distribution during data writes.

**Data Distribution** — How records are spread across keys and partitions.

**Partition Balance** — The degree to which partitions contain comparable amounts of useful work.

---

## 92. Technical Accuracy Checklist

Before considering this topic complete, verify:

- [ ] Data skew is defined as uneven data/work distribution.
- [ ] Skew is distinguished from simply having too few partitions.
- [ ] Hot keys are correctly explained.
- [ ] NULL/default keys are discussed.
- [ ] Time-based skew is explained.
- [ ] Poor partitioning columns are discussed.
- [ ] Straggler tasks are explained.
- [ ] Max versus median is presented as a signal, not a universal threshold.
- [ ] Shuffle read/write implications are explained.
- [ ] Join skew is explained.
- [ ] Join explosion is connected to skew.
- [ ] Aggregation skew is explained.
- [ ] Window-function skew is explained.
- [ ] Write skew is explained.
- [ ] Key-frequency detection is included.
- [ ] First-line fixes come before salting.
- [ ] NULL/default-key handling is included.
- [ ] Pre-aggregation is explained with semantic constraints.
- [ ] Broadcast is not presented as universal.
- [ ] AQE skew handling is explained only at the required conceptual depth.
- [ ] Salting is explained.
- [ ] The skewed side is salted.
- [ ] The other side is replicated when necessary.
- [ ] Salt-range trade-offs are explained.
- [ ] Random and deterministic salting are distinguished.
- [ ] Selective salting/hot-key isolation is explained.
- [ ] Two-phase aggregation is explained.
- [ ] Salting costs are clearly explained.
- [ ] When not to salt is covered.
- [ ] Correctness validation is mandatory.
- [ ] Measurement is emphasized.
- [ ] AQE ON/OFF experimentation is included.
- [ ] No fabricated benchmark values are included.
- [ ] No universal salt range is prescribed.
- [ ] No universal skew threshold is prescribed.
- [ ] The mini-project is complete.
- [ ] At least 14 labs are included.
- [ ] At least 10 debugging exercises are included.
- [ ] Exactly 40 practice questions are included.
- [ ] Interview questions are included.
- [ ] Senior architecture scenarios are included.
- [ ] Misconceptions are included.
- [ ] Learning checkpoints are included.
- [ ] Final assessment is included.
- [ ] Glossary is included.
- [ ] Topic 10 caching is only connected, not deeply taught.
- [ ] Topic 11 UDFs are not deeply taught.
- [ ] Topic 12 Catalyst is not deeply taught.
- [ ] Topic 13 AQE is not duplicated in full.
- [ ] Topic 15 Spark UI is not duplicated in full.

---

## 93. Do Not Duplicate Previous Topics

This chapter uses, but does not re-teach in full:

- Spark architecture;
- SparkSession;
- RDDs;
- transformations/actions;
- DataFrame API;
- Spark SQL;
- temporary views;
- joins;
- shuffle fundamentals;
- `repartition()`;
- `coalesce()`.

Use those concepts only as prerequisites and connections.

The distinctive subject of Topic 09 is:

```text
uneven distribution
+
hot keys
+
stragglers
+
skew diagnosis
+
skew mitigation
```

---

## 94. Do Not Prematurely Teach Future Topics

Do not deeply teach:

- complete caching/persistence;
- Python UDFs;
- pandas UDFs;
- Catalyst optimizer;
- full `explain()` analysis;
- complete AQE architecture;
- data sources;
- bucketing;
- complete Spark UI;
- testing.

The only AQE material here should be what is necessary to understand:

> **AQE can automatically mitigate certain skewed join partitions.**

The full AQE topic belongs to:

```text
13-adaptive-query-execution-aqe.md
```

---

## 95. Topic Completion Standard

Do not consider Topic 09 complete until you can explain:

```text
What is skew?
      ↓
Why does skew matter?
      ↓
How does a hot key create skew?
      ↓
How do NULL/default keys create skew?
      ↓
How does time-based behavior create skew?
      ↓
How do poor partitioning columns create skew?
      ↓
How do I detect hot keys?
      ↓
How do I recognize stragglers?
      ↓
How do I use max vs median?
      ↓
How does skew affect joins?
      ↓
How does skew affect aggregations?
      ↓
How does skew affect windows?
      ↓
How does skew affect writes?
      ↓
What are first-line fixes?
      ↓
When can broadcast help?
      ↓
When can pre-aggregation help?
      ↓
What does AQE skew handling do?
      ↓
What is salting?
      ↓
Why does salting work?
      ↓
Why must the other side be replicated?
      ↓
How do I choose a salt range?
      ↓
When should I selectively salt?
      ↓
What is hot-key isolation?
      ↓
What is two-phase aggregation?
      ↓
What does salting cost?
      ↓
When should I NOT salt?
      ↓
How do I validate correctness?
      ↓
How do I measure the optimization?
      ↓
How do I make the production decision?
```

You should also be able to implement and explain:

```python
df.groupBy("customer_id").count()

F.floor(F.rand(seed=42) * salt_count)

dimension.crossJoin(salt_values)

fact_salted.join(
    dimension_salted,
    on=["customer_id", "salt"]
)

df.groupBy(
    "customer_id",
    "salt"
).agg(
    F.sum("revenue")
)

partial.groupBy("customer_id").agg(
    F.sum("partial_revenue")
)
```

The important part is not syntax.

It is understanding the distributed execution problem each transformation addresses.

---

## 96. Final Self-Review

- [ ] Did I teach data skew from absolute basics?
- [ ] Did I explain balanced versus skewed partitions?
- [ ] Did I distinguish skew from too few partitions?
- [ ] Did I explain hot keys?
- [ ] Did I explain NULL/default keys?
- [ ] Did I explain time-based skew?
- [ ] Did I explain poor partitioning columns?
- [ ] Did I explain straggler tasks?
- [ ] Did I explain max versus median?
- [ ] Did I explain shuffle-read imbalance?
- [ ] Did I explain skewed joins?
- [ ] Did I explain join explosion?
- [ ] Did I explain skewed aggregations?
- [ ] Did I explain window-function skew?
- [ ] Did I explain write skew?
- [ ] Did I teach key-frequency detection?
- [ ] Did I teach first-line fixes?
- [ ] Did I explain NULL/default-key handling?
- [ ] Did I explain pre-aggregation?
- [ ] Did I explain broadcast as a mitigation?
- [ ] Did I explain AQE skew join handling?
- [ ] Did I explain salting?
- [ ] Did I explain why salting works?
- [ ] Did I explain salting the skewed side?
- [ ] Did I explain replication of the other side?
- [ ] Did I explain salt-range selection?
- [ ] Did I explain random versus deterministic salting?
- [ ] Did I explain selective salting/hot-key isolation?
- [ ] Did I explain two-phase aggregation?
- [ ] Did I explain salting cost?
- [ ] Did I explain when not to salt?
- [ ] Did I explain correctness validation?
- [ ] Did I explain measurement?
- [ ] Did I include AQE ON/OFF experimentation?
- [ ] Did I include a complete mini-project?
- [ ] Did I include at least 14 labs?
- [ ] Did I include debugging exercises?
- [ ] Did I include exactly 40 practice questions?
- [ ] Did I include interview questions?
- [ ] Did I include architecture scenarios?
- [ ] Did I include misconceptions?
- [ ] Did I include learning checkpoints?
- [ ] Did I include a final assessment?
- [ ] Did I include a glossary?
- [ ] Did I preserve the roadmap's scope?
- [ ] Did I avoid duplicating Topics 01–08?
- [ ] Did I avoid deeply teaching Topics 10–16?

---

## 97. Final Takeaway

The central lesson of Topic 09 is:

> **Distributed data is not necessarily evenly distributed work.**

A production PySpark engineer should be able to see the chain:

```text
Uneven key frequency
        ↓
Hot key
        ↓
Uneven partition
        ↓
Straggler task
        ↓
Long-tail stage
        ↓
Slow job
```

Then reason through the mitigation chain:

```text
Detect
  ↓
Measure
  ↓
Understand cause
  ↓
Handle data-quality skew
  ↓
Pre-aggregate if valid
  ↓
Broadcast if genuinely appropriate
  ↓
Use AQE when it solves the case
  ↓
Isolate hot keys when practical
  ↓
Salt when necessary
  ↓
Use two-phase aggregation for suitable aggregates
  ↓
Measure
  ↓
Validate correctness
  ↓
Keep / revert
```

The professional skill is not knowing that salting exists.

The professional skill is knowing **when the workload actually requires it, how to implement it correctly, what it costs, and how to prove that it helped.**

