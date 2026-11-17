# Module 2.14 — Distributed Processing with PySpark

# Topic 04 — Transformations, Actions and Lazy Evaluation

## Learning Objectives

By the end of this chapter, you should be able to:

1. Define a Spark transformation.
2. Define a Spark action.
3. Distinguish transformations from actions.
4. Explain narrow dependencies.
5. Explain wide dependencies at a conceptual level.
6. Explain lazy evaluation.
7. Explain why Spark uses lazy evaluation.
8. Explain lineage and recomputation.
9. Explain how an action triggers execution.
10. Explain the relationship between jobs, stages, tasks, and partitions.
11. Identify where shuffle boundaries can occur.
12. Predict whether a PySpark statement describes computation or triggers execution.
13. Identify actions that can move data to the driver.
14. Explain why repeated actions can cause repeated computation.
15. Explain how transformation chains are constructed.
16. Reason about execution timing correctly.
17. Debug common mistakes caused by misunderstanding Spark's lazy execution model.
18. Apply these concepts to production Data Engineering pipelines.

---

# 1. The Fundamental Question: When Does Spark Actually Do the Work?

Consider:

```python
df2 = df.filter(...)
df3 = df2.select(...)
df4 = df3.withColumn(...)
```

A beginner may think:

```text
filter executes
    ↓
select executes
    ↓
withColumn executes
```

That is not the right mental model.

Spark transformations are generally **lazy**.

The important question is:

> When does Spark actually execute the distributed computation?

Now add:

```python
df4.show()
```

The mental model becomes:

```text
Input
  ↓
Transformation
  ↓
Transformation
  ↓
Transformation
  ↓
Computation has been described
  ↓
Action
  ↓
Spark executes the required distributed work
```

This distinction is foundational.

A Spark program contains two different ideas:

```text
WHAT THE PROGRAM DESCRIBES
```

and:

```text
WHEN SPARK ACTUALLY EXECUTES THE DISTRIBUTED COMPUTATION
```

Understanding that separation is one of the most important steps from beginner-level PySpark usage to production Spark engineering.

---

# 2. Connection to Previous Topics

The previous topics established the architecture required to understand this chapter.

## Topic 01 introduced

- driver
- executors
- cluster managers
- partitions
- tasks
- jobs
- stages
- lineage
- fault tolerance

## Topic 02 introduced

- `SparkSession`
- Spark configuration
- local execution
- cluster execution
- deployment modes
- `spark-submit`

## Topic 03 introduced

- RDDs
- DataFrames
- schema
- distributed collections
- structured distributed data
- RDD vs DataFrame abstractions

This chapter connects those ideas.

The execution hierarchy to keep in mind is:

```text
Transformation chain
        ↓
      Action
        ↓
       Job
        ↓
      Stages
        ↓
       Tasks
        ↓
    Partitions
        ↓
    Executors
```

The exact physical execution plan can be more complicated than this simplified model, but this hierarchy is an essential mental model.

---

# 3. What Is a Transformation?

A **transformation** describes a new dataset derived from an existing dataset.

Examples include:

```python
rdd2 = rdd1.map(...)
```

and:

```python
df2 = df1.filter(...)
```

Conceptually:

```text
RDD 1
  ↓
map
  ↓
RDD 2
```

or:

```text
DataFrame 1
  ↓
filter
  ↓
DataFrame 2
```

A transformation generally:

- describes computation
- produces another logical dataset
- does not immediately execute the distributed computation
- contributes to lineage or a structured computation representation
- can be chained with other transformations
- is eventually evaluated when an action requires a result

The word **describes** is important.

When you write:

```python
df2 = df.filter(F.col("age") > 30)
```

you have described a computation.

You have not necessarily processed every row in the source dataset at that moment.

---

# 4. Why Do Transformations Exist?

Spark needs a way to express distributed computations as composable steps.

Instead of manually telling every executor:

```text
Read partition 1
Read partition 2
Read partition 3
...
```

the developer describes the desired data transformation.

For example:

```python
result = (
    df
    .filter(F.col("age") > 30)
    .select("name", "age")
)
```

This communicates the logical requirement:

```text
Start with df
   ↓
keep rows where age > 30
   ↓
keep only name and age
```

Spark can then determine how to execute the required computation.

This is one of the major advantages of a distributed data-processing framework: application code describes the computation at a higher level while Spark handles distributed execution.

---

# 5. Transformation Mental Model

Think of a transformation as adding another step to a computation graph.

```text
Input
  |
  v
filter
  |
  v
select
  |
  v
withColumn
```

The graph can be thought of as a description of the required computation.

At this point:

```text
No final result requested
```

Therefore, Spark does not need to perform the full distributed computation simply because the transformations were written.

When an action is eventually requested:

```text
withColumn
    ↓
action
    ↓
execution
```

the required computation becomes executable.

---

# 6. Real-World Analogy: A Recipe

Consider preparing a meal.

You might define:

```text
Wash vegetables
    ↓
Cut vegetables
    ↓
Add seasoning
    ↓
Cook
```

Writing down the steps does not cook the food.

The recipe describes the work.

Only when cooking begins does the actual work happen.

A simplified analogy is:

```text
Transformations = recipe steps
Action          = request to produce the meal
Lazy evaluation = defer the actual cooking until the result is required
```

This is only an analogy.

Spark does not literally maintain a recipe card in the same way a person does. The useful lesson is the separation between **describing computation** and **executing computation**.

---

# 7. RDD Transformations

RDDs provide a lower-level transformation API.

Common examples include:

```python
map()
filter()
flatMap()
distinct()
union()
```

For example:

```python
numbers = spark.sparkContext.parallelize(
    [1, 2, 3, 4, 5]
)

doubled = numbers.map(
    lambda x: x * 2
)
```

The result:

```python
doubled
```

is another RDD representing the transformed dataset.

The transformation itself does not mean:

```text
all five values have already been processed
```

Instead:

```text
numbers
   ↓
map(x → x * 2)
   ↓
doubled
```

has been established as a computation relationship.

---

# 8. RDD `filter()`

Example:

```python
numbers = spark.sparkContext.parallelize(
    [1, 2, 3, 4, 5]
)

even_numbers = numbers.filter(
    lambda x: x % 2 == 0
)
```

Conceptually:

```text
1 → removed
2 → kept
3 → removed
4 → kept
5 → removed
```

But the complete distributed computation does not have to happen when `filter()` is called.

To request the result:

```python
result = even_numbers.collect()
```

Now an action is present.

The execution model is:

```text
parallelize
    ↓
filter
    ↓
collect
    ↓
execution
```

---

# 9. RDD `flatMap()`

`flatMap()` can produce multiple output records from one input record.

Example:

```python
lines = spark.sparkContext.parallelize([
    "spark is distributed",
    "spark processes data",
])

words = lines.flatMap(
    lambda line: line.split()
)
```

Conceptually:

```text
"spark is distributed"
        ↓
"spark", "is", "distributed"

"spark processes data"
        ↓
"spark", "processes", "data"
```

Again:

```python
words
```

represents the transformed RDD.

To request results:

```python
words.take(10)
```

The action causes Spark to perform the necessary computation.

---

# 10. RDD `distinct()`

Example:

```python
numbers = spark.sparkContext.parallelize(
    [1, 2, 2, 3, 3, 3]
)

unique_numbers = numbers.distinct()
```

`distinct()` is a transformation.

It describes the requirement:

```text
remove duplicate values
```

Because duplicate values can exist in different partitions, this type of operation can require data redistribution.

That makes it useful for introducing the idea of a **wide dependency**.

The detailed mechanics of shuffle optimization come later.

---

# 11. RDD `union()`

Example:

```python
rdd1 = spark.sparkContext.parallelize([1, 2, 3])
rdd2 = spark.sparkContext.parallelize([4, 5, 6])

combined = rdd1.union(rdd2)
```

The transformation creates a logical combination:

```text
RDD 1 ─┐
       ├──→ combined RDD
RDD 2 ─┘
```

Again, no final result is required until an action is requested.

---

# 12. DataFrame Transformations

DataFrames also use transformations.

Common examples include:

```python
filter()
select()
withColumn()
drop()
orderBy()
groupBy()
```

For example:

```python
from pyspark.sql import functions as F

filtered = df.filter(
    F.col("age") > 30
)
```

Then:

```python
selected = filtered.select(
    "name",
    "age",
)
```

Then:

```python
result = selected.withColumn(
    "age_next_year",
    F.col("age") + 1,
)
```

Conceptually:

```text
df
 ↓
filter
 ↓
select
 ↓
withColumn
 ↓
result
```

The complete distributed computation is not necessarily performed at each transformation call.

---

# 13. `select()` as a Transformation

Example:

```python
selected = df.select(
    "name",
    "age",
)
```

This describes a projection of the dataset.

Conceptually:

```text
Input columns
    ↓
name
age
    ↓
Output DataFrame
```

The important Topic 04 lesson is not the full `select()` API.

It is:

> `select()` describes a new structured result; it does not require the complete result to be materialized immediately.

---

# 14. `withColumn()` as a Transformation

Example:

```python
result = df.withColumn(
    "age_next_year",
    F.col("age") + 1,
)
```

This creates a new DataFrame representation containing the derived column.

Conceptually:

```text
Existing DataFrame
       ↓
derive expression
       ↓
New logical DataFrame
```

The operation participates in the transformation chain.

---

# 15. `groupBy()` and the Transformation Model

A grouped aggregation is also part of the computation description.

For example:

```python
grouped = (
    df
    .groupBy("city")
    .count()
)
```

The important point is:

```python
grouped
```

represents a requested computation.

The final distributed work is triggered by an action such as:

```python
grouped.show()
```

The actual physical execution may involve redistribution and shuffle. That distinction is explored more deeply in later shuffle topics.

---

# 16. Transformation Categories

Two important dependency categories are:

```text
Narrow transformations
```

and:

```text
Wide transformations
```

This classification helps explain:

- partition dependencies
- parallel execution
- shuffle
- stage boundaries

The goal here is to understand the execution model.

This is not yet the detailed shuffle-optimization chapter.

---

# 17. Narrow Transformations

A **narrow dependency** is a dependency where a child partition can generally be computed from a small or local set of parent partitions without requiring a full redistribution of the data.

Typical examples include:

```python
map()
filter()
flatMap()
```

Conceptually:

```text
Parent Partition 1 → Child Partition 1
Parent Partition 2 → Child Partition 2
Parent Partition 3 → Child Partition 3
```

A task processing one output partition can generally read the relevant parent partition data without requiring all partitions to exchange records.

This is why narrow dependencies are useful for efficient pipeline composition.

---

# 18. Why Narrow Dependencies Matter

Suppose:

```text
Partition 1
Partition 2
Partition 3
Partition 4
```

are processed independently.

A transformation such as a filter can conceptually behave like:

```text
Partition 1 → filtered Partition 1
Partition 2 → filtered Partition 2
Partition 3 → filtered Partition 3
Partition 4 → filtered Partition 4
```

There is no requirement to gather all matching records into one global location simply to perform the filter.

That allows Spark to preserve a high degree of partition-local processing.

Do not interpret this as:

> "Narrow transformations are always free."

They still consume CPU, memory, and potentially I/O.

The important distinction is that they do not inherently require a full redistribution of records.

---

# 19. Wide Transformations

A **wide dependency** occurs when a child partition may depend on data from multiple parent partitions.

Conceptually:

```text
Partition 1 ─┐
Partition 2 ─┼──→ redistribution → new partitions
Partition 3 ─┤
Partition 4 ─┘
```

This redistribution is commonly called a **shuffle**.

Examples that can require wide dependencies include:

```python
reduceByKey()
groupByKey()
distinct()
```

and structured operations such as some:

- aggregations
- joins
- repartitioning operations

The exact physical behavior depends on the operation and execution plan.

---

# 20. Why Wide Dependencies Can Create Stage Boundaries

Consider:

```text
Stage 1
Partition 1 ─┐
Partition 2 ─┼──→ Shuffle
Partition 3 ─┤
Partition 4 ─┘
                 ↓
              Stage 2
```

A shuffle can separate portions of a Spark job into different stages because the downstream computation depends on redistributed data.

The important conceptual chain is:

```text
Wide dependency
      ↓
Potential shuffle
      ↓
Redistribution
      ↓
Stage boundary
```

This is not a claim that every operation has exactly one shuffle or exactly two stages.

Spark's actual execution plan determines the details.

---

# 21. Narrow vs Wide Dependencies

| Narrow dependency | Wide dependency |
|---|---|
| Child partition depends on a limited/local set of parent partitions | Child partitions may depend on multiple parent partitions |
| Usually avoids full redistribution | May require redistribution |
| Can often remain within a stage | Can introduce a shuffle boundary |
| Often simpler data movement pattern | Often more network and disk activity |
| Examples: `map`, `filter` | Examples: `reduceByKey`, `groupByKey`, some aggregations/joins |

Do not reduce the distinction to:

```text
narrow = fast
wide = slow
```

That is too simplistic.

A narrow operation can still be expensive.

A wide operation may be necessary and correctly designed.

The key distinction is the dependency and data-movement pattern.

---

# 22. What Is an Action?

An **action** is an operation that requests a result or an output operation and therefore causes Spark to execute the computation required to produce that result.

Examples include:

### RDD

```python
collect()
count()
first()
take()
reduce()
saveAsTextFile()
```

### DataFrame

```python
show()
count()
collect()
first()
take()
write...
```

The important conceptual difference is:

```text
Transformation
    ↓
describes computation
```

versus:

```text
Action
    ↓
requests computation/result
```

---

# 23. Why Do Actions Exist?

Spark needs a point at which the application says:

> I now need a result.

Until that point, Spark can continue building the computation description.

For example:

```python
result = (
    df
    .filter(F.col("age") > 30)
    .select("name")
)
```

The program has defined a result.

But:

```python
result.show()
```

requests that result.

This causes Spark to execute the necessary distributed work.

---

# 24. Common RDD Actions

## `count()`

```python
number_of_records = rdd.count()
```

Requests the number of records.

The result is a single value.

---

## `first()`

```python
record = rdd.first()
```

Requests the first record.

The result is returned to the driver.

---

## `take(n)`

```python
records = rdd.take(10)
```

Requests a bounded number of records.

This is useful for inspection because the requested result is intentionally limited.

---

## `collect()`

```python
records = rdd.collect()
```

Requests all records and returns them to the driver.

This can be dangerous for large datasets.

---

## `reduce()`

```python
total = rdd.reduce(lambda a, b: a + b)
```

Requests an aggregate result.

---

## `saveAsTextFile()`

```python
rdd.saveAsTextFile("output/")
```

Requests computation that produces external output.

The operation has an external side effect and therefore should be treated as a production output operation, not simply as a display function.

---

# 25. Common DataFrame Actions

## `show()`

```python
df.show()
```

Requests rows for display.

This is commonly used for development and inspection.

---

## `count()`

```python
count = df.count()
```

Requests a record count.

---

## `first()`

```python
row = df.first()
```

Requests one result row.

---

## `take(n)`

```python
rows = df.take(10)
```

Requests a bounded set of rows.

---

## `collect()`

```python
rows = df.collect()
```

Requests all selected rows back to the driver.

This can be unsafe for large results.

---

## `write`

For example:

```python
df.write.parquet("output/")
```

The write operation requests the distributed computation necessary to produce the output.

The exact write semantics depend on the data source, save mode, partitioning, and other configuration. Those details belong to later topics.

---

# 26. Transformation vs Action

| Transformation | Action |
|---|---|
| Describes computation | Requests a result/output |
| Generally lazy | Triggers required execution |
| Produces another logical dataset | Produces a result or external side effect |
| Builds dependencies/lineage or structured computation | Causes Spark to execute the required computation |
| Examples: `map`, `filter`, `select` | Examples: `count`, `show`, `collect`, `write` |

The distinction is foundational.

For example:

```python
filtered = df.filter(F.col("age") > 30)
```

is a transformation.

Then:

```python
filtered.count()
```

is an action.

The complete conceptual flow is:

```text
filter
  ↓
count
  ↓
execution
```

---

# 27. What Is Lazy Evaluation?

Spark uses **lazy evaluation**.

A precise definition is:

> Spark generally does not execute the distributed computation represented by transformations immediately. Instead, it records the computation and executes the required work when an action requests a result.

For example:

```python
df2 = df.filter(
    F.col("age") > 30
)

df3 = df2.select(
    "name"
)

df4 = df3.withColumn(
    "name_length",
    F.length("name")
)
```

The conceptual state is:

```text
filter
   ↓
select
   ↓
withColumn
   ↓
computation described
```

Then:

```python
df4.show()
```

causes:

```text
Action
   ↓
required execution
```

---

# 28. Lazy Evaluation Does Not Mean "Spark Does Nothing"

This is an important technical distinction.

Do not interpret lazy evaluation as:

> Spark does absolutely nothing when a transformation is called.

A better statement is:

> Spark constructs and tracks the computation representation rather than immediately executing the full distributed data processing.

There can still be ordinary application-side work involved in constructing DataFrame/RDD objects, expressions, metadata, and other representations.

The important thing being deferred is the **distributed data processing**.

So distinguish:

```text
Building a computation representation
```

from:

```text
Executing the distributed computation over the dataset
```

---

# 29. Why Does Spark Use Lazy Evaluation?

Lazy evaluation provides several important benefits.

## 29.1 Avoid unnecessary computation

Suppose:

```python
df2 = df.filter(...)
df3 = df2.select(...)
```

but `df3` is never used.

There is no reason for Spark to process the entire dataset merely because those transformations were defined.

---

## 29.2 Build a complete computation chain

Spark can see the sequence of required operations before executing the final result.

Conceptually:

```text
filter
   ↓
select
   ↓
derive
   ↓
aggregate
   ↓
action
```

---

## 29.3 Enable planning and optimization

Structured DataFrame operations can be analyzed before execution.

This creates opportunities for Spark's structured execution framework to reason about the computation.

The detailed Catalyst discussion belongs to Topic 12.

---

## 29.4 Avoid unnecessary intermediate materialization

If every transformation executed immediately and produced a fully materialized intermediate dataset, complex pipelines could generate unnecessary I/O and storage overhead.

Lazy execution allows Spark to execute the required computation as a planned pipeline instead of automatically materializing every logical intermediate result.

---

## 29.5 Support lineage-based recovery

Spark maintains dependency information that can be used to recompute lost data.

Lazy evaluation and lineage are related concepts, but they are not identical.

Lineage describes dependencies.

Lazy evaluation describes when the distributed computation is executed.

---

# 30. Lineage

A transformation chain creates dependency information.

For example:

```text
Input
  ↓
filter
  ↓
map
  ↓
select
  ↓
aggregate
  ↓
action
```

The important idea is:

```text
derived result
     ↓
depends on
     ↓
previous computation
```

Lineage helps Spark understand how derived distributed data relates to earlier data.

If an executor loses a partition, Spark can use dependency information to determine how the required data can be recomputed.

Do not confuse:

```text
lineage
```

with:

```text
already materialized data
```

A lineage relationship can exist even when the intermediate data has not been materialized as a stored dataset.

---

# 31. Transformation Chaining

Transformation chaining is one of the most common PySpark programming styles.

For example:

```python
from pyspark.sql import functions as F

result = (
    df
    .filter(F.col("age") > 30)
    .select("name", "age")
    .withColumn(
        "age_next_year",
        F.col("age") + 1,
    )
)
```

Conceptually:

```text
df
 ↓
filter
 ↓
select
 ↓
withColumn
 ↓
result
```

At this point, an action has not necessarily been called.

Then:

```python
result.show()
```

requests execution.

This is why a transformation chain should be thought of as a **computation description**.

---

# 32. A Complete DataFrame Lazy-Evaluation Example

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = (
    SparkSession.builder
    .appName("LazyEvaluationDemo")
    .getOrCreate()
)

df = spark.createDataFrame(
    [
        ("Alice", 30),
        ("Bob", 25),
        ("Charlie", 40),
    ],
    ["name", "age"],
)

filtered = df.filter(
    F.col("age") > 30
)

selected = filtered.select(
    "name"
)

selected.show()

spark.stop()
```

Let's trace it.

### Step 1 — Create SparkSession

```python
spark = ...
```

This establishes the application entry point.

### Step 2 — Create the DataFrame

```python
df = spark.createDataFrame(...)
```

A small local example is used here for demonstration.

### Step 3 — Define a filter

```python
filtered = df.filter(...)
```

This is a transformation.

### Step 4 — Define a projection

```python
selected = filtered.select("name")
```

This is another transformation.

### Step 5 — Call `show()`

```python
selected.show()
```

This is an action.

### Step 6 — Spark executes the required computation

Conceptually:

```text
df
 ↓
filter age > 30
 ↓
select name
 ↓
show
 ↓
execution
```

The important lesson is not the syntax.

The lesson is:

> Transformations build the computation; the action requests its result.

---

# 33. RDD Lazy-Evaluation Example

Consider:

```python
numbers = spark.sparkContext.parallelize(
    [1, 2, 3, 4, 5]
)

doubled = numbers.map(
    lambda x: x * 2
)

filtered = doubled.filter(
    lambda x: x > 5
)

result = filtered.collect()
```

Trace it:

```text
parallelize
    ↓
map
    ↓
filter
    ↓
collect
```

The transformations are:

```python
map(...)
filter(...)
```

The action is:

```python
collect()
```

The distributed computation required to produce the result is triggered by the action.

---

# 34. "Nothing Happens" Experiment

Consider:

```python
filtered = df.filter(
    F.col("age") > 30
)

selected = filtered.select(
    "name"
)
```

There is no action.

The important observation is:

```text
No result has been requested.
```

Spark has constructed the logical computation representation rather than executing the full distributed computation.

This is a useful experiment for beginners.

Now add:

```python
selected.show()
```

An action has been introduced.

The execution requirement changes.

---

# 35. Action Experiment

Consider:

```python
selected.count()
```

The action requests a count.

Then:

```python
selected.show()
```

requests rows for display.

These are separate action requests.

This leads to a critical production concept:

> Multiple actions on the same unpersisted computation can cause Spark to perform overlapping work more than once.

Caching and persistence are covered later in Topic 10. Here, understand the problem rather than the solution.

---

# 36. Multiple Actions

Consider:

```python
filtered = df.filter(
    F.col("age") > 30
)

filtered.count()
filtered.show()
```

A common beginner assumption is:

> "Spark already calculated `filtered` for `count()`, so `show()` automatically reuses that result."

That should not be assumed.

Without persistence, Spark may need to recompute the required upstream work for another action.

Conceptually:

```text
filtered
   ↓
count()
   ↓
execution

filtered
   ↓
show()
   ↓
another execution request
```

The exact execution behavior depends on the computation and Spark's execution mechanisms, but the production concern is real:

> Repeated actions can cause repeated computation when intermediate results are not persisted.

---

# 37. Why Multiple Actions Matter in Production

Suppose a pipeline contains an expensive transformation:

```python
expensive = (
    df
    .filter(...)
    .select(...)
    .withColumn(...)
    .groupBy(...)
)
```

Then the application performs:

```python
expensive.count()
expensive.show()
expensive.write.parquet(...)
```

There are three action/output requests.

If the expensive upstream computation is not persisted and each action requires it, the application may repeat substantial work.

The correct response is not:

> "Always cache everything."

That would be another dangerous oversimplification.

The caching decision belongs to Topic 10.

The lesson here is:

> Understand the execution consequences of every action.

---

# 38. Actions Are Not All the Same

Actions differ in what they request.

## `count()`

```python
df.count()
```

Requests a count.

The final result is small:

```text
one integer
```

The underlying distributed processing may still involve the entire relevant dataset.

---

## `first()`

```python
df.first()
```

Requests one row.

The result returned to the driver is small.

---

## `take(10)`

```python
df.take(10)
```

Requests a bounded number of rows.

This is useful for inspection.

---

## `show()`

```python
df.show()
```

Requests a limited representation for display.

It should not be interpreted as equivalent to collecting the entire DataFrame.

---

## `collect()`

```python
df.collect()
```

Requests all selected rows to be returned to the driver.

This can be dangerous.

---

## `write`

```python
df.write.parquet("output/")
```

Requests execution that produces external output.

The result is not returned as a large Python object to the driver.

---

# 39. `collect()` and Driver Memory

This deserves special attention.

Consider:

```python
df.collect()
```

Conceptually:

```text
Distributed dataset
       ↓
Executors process data
       ↓
Results move to driver
       ↓
Driver memory
```

If the result is very large, the driver can run out of memory.

The problem becomes especially dangerous when developers think:

```python
collect()
```

means:

```text
"show me the data"
```

It does not mean that.

It means:

> Return the complete result to the driver.

---

# 40. `collect()` vs `take()`

Compare:

```python
df.take(10)
```

with:

```python
df.collect()
```

The conceptual difference is:

```text
take(10)
    ↓
bounded result
```

versus:

```text
collect()
    ↓
all results
```

For development inspection, a bounded operation is usually more appropriate.

Examples include:

```python
df.show(10)
```

or:

```python
df.take(10)
```

Do not use `collect()` casually on large production datasets.

---

# 41. `show()` vs `collect()`

| Operation | Purpose | Driver implication |
|---|---|---|
| `show()` | Display a limited number of rows | Intended for inspection |
| `collect()` | Return all selected rows | Potentially dangerous |
| `take(n)` | Return a bounded number of rows | Bounded result |
| `count()` | Return a count | Small final result |

The underlying distributed computation can still be substantial for `count()` or `show()`.

The size of the final driver result is not the same thing as the amount of distributed work.

This is an important distinction.

---

# 42. Action Results vs Distributed Work

Consider:

```python
df.count()
```

The result is one integer.

That does **not** mean Spark only processed one record.

Conceptually:

```text
Many distributed records
       ↓
distributed counting
       ↓
partial results
       ↓
final count
       ↓
one integer
```

The final result is small, but the computation can involve a large dataset.

Similarly:

```python
df.show()
```

may display only a few rows while still requiring Spark to access and process enough data to satisfy the operation.

Never infer the amount of distributed work solely from the size of the final result.

---

# 43. Job Creation

An action causes Spark to submit the computation required for that action as a **job**.

The conceptual relationship is:

```text
Transformation chain
       ↓
Action
       ↓
Job
```

For example:

```python
result = (
    df
    .filter(F.col("age") > 30)
    .select("name")
)

result.count()
```

The `count()` action causes Spark to execute the computation required to produce the count.

The job is then broken into stages and tasks according to its dependency structure and execution plan.

---

# 44. Jobs, Stages, Tasks and Partitions

The core hierarchy is:

```text
Action
  ↓
Job
  ↓
Stages
  ↓
Tasks
  ↓
Partitions
```

## Action

Requests a result or output.

## Job

Represents the computation required by an action.

## Stage

Represents a portion of a job separated by relevant dependency boundaries.

## Task

Represents work on a partition within a stage.

## Partition

Represents a unit of distributed data processing.

This connects the current chapter directly to Topic 01.

---

# 45. Example: Tracing a Pipeline

Consider:

```python
result = (
    df
    .filter(F.col("age") > 30)
    .select("name", "age")
)

result.count()
```

Conceptually:

```text
filter
  ↓
select
  ↓
count
  ↓
Job
  ↓
Stages
  ↓
Tasks
  ↓
Partitions
```

If the operations can be executed through narrow dependencies, Spark may be able to process them within a continuous stage.

If a wide dependency is introduced, a shuffle boundary can separate portions of the computation.

The exact stage structure must not be guessed without considering the actual execution plan.

---

# 46. Shuffle Boundaries

Suppose:

```text
Stage 1
Partition 1 ─┐
Partition 2 ─┼──→ Shuffle
Partition 3 ─┤
Partition 4 ─┘
                 ↓
              Stage 2
```

The shuffle represents redistribution of records.

This can involve:

- network transfer
- disk I/O
- serialization
- partitioning
- additional coordination

Because downstream computation depends on redistributed data, a shuffle can create a stage boundary.

The exact mechanics of shuffle and its optimization are taught later.

---

# 47. Why Shuffle Is Relevant to Lazy Evaluation

Lazy evaluation allows Spark to build the computation before execution.

Consider:

```python
result = (
    df
    .filter(...)
    .groupBy(...)
    .count()
)
```

The application has described a pipeline.

When an action is requested:

```python
result.show()
```

Spark must determine how to execute the required computation.

If the computation contains a dependency that requires redistribution, Spark's execution will reflect that dependency.

Conceptually:

```text
Transformations
      ↓
dependency structure
      ↓
Action
      ↓
Job
      ↓
stage boundaries
      ↓
distributed execution
```

This is why understanding lazy evaluation is necessary before studying shuffle optimization.

---

# 48. Transformation vs Stage

A common beginner mistake is:

> "Every transformation creates a stage."

That is incorrect.

Transformations describe computation.

Stages are execution units formed according to dependency boundaries and Spark's execution planning.

For example:

```text
filter
   ↓
map
   ↓
select
```

may form one continuous stage under an appropriate execution path.

A wide dependency can introduce a boundary:

```text
filter
   ↓
map
   ↓
shuffle
   ↓
aggregate
```

which can lead to multiple stages.

Do not equate:

```text
one transformation = one stage
```

---

# 49. Action vs Stage

Another misconception is:

> "Every action creates exactly one stage."

That is also incorrect.

An action can trigger a job containing multiple stages.

For example:

```text
Action
  ↓
Job
  ↓
Stage 1
  ↓
Shuffle
  ↓
Stage 2
  ↓
Stage 3
```

The number of stages depends on the computation and execution plan.

The correct mental model is:

```text
Action
   ↓
Job
   ↓
one or more stages
```

---

# 50. Wide vs Narrow: Not Fast vs Slow

It is tempting to memorize:

```text
narrow = fast
wide = slow
```

Do not do that.

A narrow transformation can still be expensive because it may:

- scan a large dataset
- perform CPU-intensive calculations
- invoke expensive Python logic
- read substantial input

A wide transformation can be necessary and correctly designed.

The useful distinction is:

```text
How do parent and child partitions depend on each other?
```

That question leads to better execution reasoning than simply asking whether an operation is "fast."

---

# 51. Lazy Evaluation and Optimization

A useful conceptual model is:

```text
Multiple transformations
        ↓
Logical computation
        ↓
Spark can reason about required work
        ↓
Execution planning
        ↓
Action
        ↓
Distributed execution
```

For DataFrames, structured APIs provide additional information that Spark SQL can use during planning and optimization.

For RDDs, Spark uses dependency and lineage information to construct distributed execution.

The complete Catalyst optimizer discussion belongs to Topic 12.

The important Topic 04 lesson is:

> Lazy evaluation creates the opportunity for Spark to see the computation before executing the requested result.

---

# 52. Transformation Order

Consider:

```python
df.filter(...)
   .select(...)
```

versus:

```python
df.select(...)
   .filter(...)
```

Both may represent logically equivalent computations when the selected columns preserve the columns needed by the filter.

However, do not assume that the written order directly determines the final physical execution order.

For structured DataFrames, Spark can analyze the logical computation and apply appropriate optimizations.

The engineering principles are:

- write logically correct transformations
- preserve required columns
- understand the semantics
- allow Spark's optimizer to reason about structured operations
- measure actual execution behavior when performance matters

Do not manually rearrange code solely because you assume one textual ordering is faster.

---

# 53. Action-Driven Execution

A very useful production question is:

> **What action ultimately requires this data?**

Consider:

```python
df1 = source_df

df2 = df1.filter(
    F.col("amount") > 0
)

df3 = df2.select(
    "customer_id",
    "amount",
)

df4 = df3.groupBy(
    "customer_id"
)
```

Ask:

> What causes Spark to execute this pipeline?

The answer is not:

```text
filter()
```

or:

```text
select()
```

The answer is an action or output request such as:

```python
df4.count()
```

or:

```python
df4.write.parquet("output/")
```

This mental model should become automatic.

---

# 54. "Nothing Happens" vs "Something Happens"

A more accurate mental model is:

```text
Transformation call
    ↓
Spark constructs computation representation
    ↓
No full distributed execution yet
```

Then:

```text
Action
    ↓
Spark schedules required distributed work
    ↓
Executors process partitions
    ↓
Result/output produced
```

This avoids two opposite misconceptions:

### Incorrect idea A

> "Every transformation executes immediately."

### Incorrect idea B

> "Transformations do absolutely nothing."

The correct concept lies between them.

---

# 55. Measuring Execution Time Correctly

Consider:

```python
import time

start = time.time()

df2 = df.filter(
    F.col("age") > 30
)

end = time.time()

print(end - start)
```

This does **not** measure the time required to process the distributed dataset.

It mainly measures application-side construction of the transformation.

A more meaningful basic experiment is:

```python
import time

start = time.time()

df2 = df.filter(
    F.col("age") > 30
)

df2.count()

end = time.time()

print(f"Elapsed time: {end - start:.3f} seconds")
```

Now an action is included.

The measurement still includes more than pure executor computation—such as scheduling and communication—but it represents actual execution much more meaningfully.

---

# 56. Why Timing Only a Transformation Is Misleading

Suppose:

```python
start = time.time()

filtered = df.filter(
    F.col("amount") > 0
)

print(time.time() - start)
```

You might observe:

```text
0.001 seconds
```

and conclude:

> "The filter processed a billion rows in one millisecond."

That conclusion is wrong.

The transformation did not necessarily execute the distributed data processing at that point.

You measured the construction of the computation representation, not the complete distributed execution.

This is a common benchmarking mistake.

---

# 57. Production Pipeline Mental Model

A typical batch pipeline can be viewed as:

```text
Read
 ↓
Transform
 ↓
Transform
 ↓
Transform
 ↓
Validate
 ↓
Write
```

Most intermediate operations are transformations.

The final output operation is an action-like execution trigger.

For example:

```python
cleaned = (
    raw_df
    .filter(F.col("amount") >= 0)
    .select(
        "customer_id",
        "amount",
    )
)

cleaned.write.parquet(
    "output/"
)
```

Conceptually:

```text
read
 ↓
filter
 ↓
select
 ↓
write
 ↓
execution
```

The write request causes Spark to execute the necessary distributed computation.

---

# 58. Real-World ETL Example

Suppose a company receives transaction data.

Requirements:

```text
Raw transactions
      ↓
Filter invalid records
      ↓
Select required columns
      ↓
Calculate derived value
      ↓
Aggregate
      ↓
Write output
```

A simplified DataFrame pipeline might be:

```python
from pyspark.sql import functions as F

result = (
    transactions_df
    .filter(F.col("quantity") > 0)
    .select(
        "customer_id",
        "quantity",
        "unit_price",
    )
    .withColumn(
        "transaction_value",
        F.col("quantity") * F.col("unit_price"),
    )
    .groupBy("customer_id")
    .agg(
        F.sum("transaction_value").alias("total_value")
    )
)

result.write.parquet(
    "output/customer_totals/"
)
```

Identify the concepts:

### Transformations

```text
filter
select
withColumn
groupBy
agg
```

### Final execution request

```text
write
```

The transformations describe the pipeline.

The write request causes Spark to execute the required computation.

The exact physical plan and shuffle behavior depend on the data and execution plan.

---

# 59. Side Effects and Actions

Transformations are intended to describe data computation.

Actions can produce:

- returned results
- displayed results
- external output
- external side effects

Examples:

```python
show()
collect()
write...
```

This distinction matters in production because output operations are not merely observations.

For example:

```python
df.write.parquet("output/")
```

can create external data.

Repeatedly executing an output action can therefore have consequences beyond CPU usage.

The exact behavior depends on the data source, save mode, and output semantics, which are covered later.

---

# 60. Common Beginner Mistakes

## Mistake 1 — Thinking transformations execute immediately

Incorrect:

```text
filter() → full distributed execution
select() → full distributed execution
```

Correct:

```text
transformations → computation description
action → execution request
```

---

## Mistake 2 — Thinking actions are only display functions

Actions include more than:

```python
show()
```

They also include:

```python
count()
collect()
first()
take()
reduce()
write...
```

---

## Mistake 3 — Calling `collect()` on huge datasets

Incorrect:

```python
df.collect()
```

without considering result size.

Correct reasoning:

```text
Will all results fit safely in driver memory?
```

---

## Mistake 4 — Measuring only transformation construction

Incorrect:

```python
start = time.time()
df2 = df.filter(...)
end = time.time()
```

and interpreting the result as full distributed processing time.

---

## Mistake 5 — Forgetting multiple actions

Example:

```python
df.count()
df.show()
df.write.parquet(...)
```

These are multiple execution requests.

Do not automatically assume Spark computed the upstream data once and retained it for all three.

---

## Mistake 6 — Confusing transformations with stages

A transformation is a logical computation operation.

A stage is an execution unit.

They are not the same concept.

---

## Mistake 7 — Assuming every transformation causes a shuffle

Many common transformations are narrow.

Shuffle occurs when the dependency structure requires data redistribution.

---

## Mistake 8 — Assuming every action sends all data to the driver

For example:

```python
count()
```

returns a small count result.

```python
collect()
```

returns all selected records.

Actions have different result semantics.

---

## Mistake 9 — Assuming lazy evaluation means no planning

Spark can construct and track computation representations before execution.

Lazy evaluation does not mean Spark waits until the action to understand that a computation exists.

---

## Mistake 10 — Assuming every transformation permanently materializes an intermediate dataset

A transformation generally defines a derived computation.

It does not automatically mean:

```text
write intermediate dataset to disk
```

---

## Mistake 11 — Treating `show()` and `collect()` as equivalent

They have different result semantics and driver-memory implications.

---

# 61. Transformations vs Actions vs Jobs vs Stages vs Tasks

This hierarchy should become part of your mental model.

| Concept | Meaning |
|---|---|
| Transformation | Describes how to derive another dataset |
| Action | Requests a result or output and triggers required execution |
| Job | Computation associated with an action |
| Stage | Portion of a job separated by relevant dependency boundaries |
| Task | Work performed for one partition within a stage |
| Partition | Unit of distributed data processing |

The relationship is:

```text
Transformation chain
       ↓
Action
       ↓
Job
       ↓
Stages
       ↓
Tasks
       ↓
Partitions
```

For example:

```text
filter
  ↓
select
  ↓
groupBy
  ↓
count
  ↓
Job
  ↓
Stage(s)
  ↓
Task(s)
  ↓
Partition(s)
```

The exact number of stages and tasks depends on the actual execution plan and partitioning.

---

# 62. A More Detailed Mental Model

Consider:

```python
result = (
    df
    .filter(F.col("amount") > 0)
    .select("customer_id", "amount")
    .groupBy("customer_id")
    .sum("amount")
)

result.show()
```

A conceptual trace is:

```text
Python program
      ↓
DataFrame transformations
      ↓
logical computation representation
      ↓
show() action
      ↓
Spark job
      ↓
execution stages
      ↓
tasks
      ↓
partitions
      ↓
executors
      ↓
result
```

If the grouping requires redistribution, a shuffle may create a stage boundary.

Do not assume exact physical details without examining the execution plan.

---

# 63. Practical Debugging Scenario 1 — "My Filter Is Instant"

Developer:

```python
start = time.time()

filtered = df.filter(
    F.col("age") > 30
)

print(time.time() - start)
```

They report:

> "The filter is extremely fast."

### Diagnosis

The developer measured transformation construction, not necessarily distributed execution.

### Better experiment

```python
start = time.time()

filtered = df.filter(
    F.col("age") > 30
)

filtered.count()

print(time.time() - start)
```

Now the experiment includes an action.

---

# 64. Practical Debugging Scenario 2 — "Adding Count Made It Slow"

Developer writes:

```python
filtered = df.filter(
    F.col("age") > 30
)
```

and sees almost no delay.

Then:

```python
filtered.count()
```

takes several minutes.

### Explanation

The transformation was lazy.

The action caused Spark to execute the required distributed computation.

The delay was not necessarily introduced by `count()` as an intrinsically expensive operation.

Instead, `count()` exposed the execution cost that had been deferred.

---

# 65. Practical Debugging Scenario 3 — Repeated Actions

Code:

```python
filtered = df.filter(
    F.col("age") > 30
)

filtered.count()
filtered.show()
```

### Engineering question

Could the filter be evaluated more than once?

Yes, unless intermediate computation is reused through appropriate persistence or other execution mechanisms.

Do not immediately solve every such problem by caching.

First establish:

1. whether recomputation exists
2. whether it matters
3. whether the upstream computation is expensive
4. whether reuse justifies persistence

Detailed persistence decisions belong to Topic 10.

---

# 66. Practical Debugging Scenario 4 — Driver OOM

Code:

```python
df.collect()
```

Dataset:

```text
billions of rows
```

### Diagnosis

The application requests all selected rows at the driver.

The architecture becomes:

```text
Executors
    ↓
huge result
    ↓
Driver
    ↓
driver memory exhaustion
```

The correct question is not:

> "How do I make collect faster?"

It is:

> "Why am I moving the complete distributed result to the driver?"

---

# 67. Practical Debugging Scenario 5 — No Action

Code:

```python
df2 = df.filter(...)
df3 = df2.select(...)
df4 = df3.withColumn(...)
```

Then the program ends.

### What happened?

The program constructed the computation representation.

It did not request a final distributed result or output.

This is one reason a PySpark script can appear to "run instantly" even though the pipeline appears to contain many transformations.

---

# 68. Practical Debugging Scenario 6 — Wide Dependency

Suppose:

```python
pairs = spark.sparkContext.parallelize([
    ("A", 1),
    ("B", 1),
    ("A", 1),
])

result = pairs.reduceByKey(
    lambda a, b: a + b
)

result.collect()
```

The important reasoning is:

```text
reduceByKey
     ↓
same-key values may need to meet
     ↓
data redistribution may be required
     ↓
shuffle boundary
     ↓
collect action
```

Do not attempt to predict an exact stage count from this simplified code without considering the actual execution environment and plan.

---

# 69. Hands-On Lab 1 — Identify Transformations and Actions

Given:

```python
result = (
    df
    .filter(F.col("age") > 30)
    .select("name")
)

result.count()
```

Identify:

- transformations
- action
- point where execution is requested

Expected reasoning:

```text
filter  → transformation
select  → transformation
count   → action
```

---

# 70. Hands-On Lab 2 — RDD Lazy Evaluation

Create:

```python
rdd = spark.sparkContext.parallelize(
    [1, 2, 3, 4, 5]
)

rdd2 = rdd.map(
    lambda x: x * 2
)

rdd3 = rdd2.filter(
    lambda x: x > 5
)
```

Then:

```python
rdd3.collect()
```

Explain:

1. What transformations were defined?
2. What was the action?
3. When was the distributed computation requested?
4. What result should be produced?

---

# 71. Hands-On Lab 3 — DataFrame Lazy Evaluation

Create:

```python
df2 = df.filter(
    F.col("age") > 30
)

df3 = df2.select(
    "name"
)

df4 = df3.withColumn(
    "name_length",
    F.length("name")
)
```

Then:

```python
df4.show()
```

Explain the execution sequence conceptually.

---

# 72. Hands-On Lab 4 — Multiple Actions

Run:

```python
filtered = df.filter(
    F.col("age") > 30
)

filtered.count()
filtered.show()
```

Answer:

1. How many action requests are there?
2. Why might upstream work be repeated?
3. What later topic will address reuse of expensive intermediate data?

Expected final answer for question 3:

> Topic 10 — Caching and Persistence.

---

# 73. Hands-On Lab 5 — `collect()` vs `take()`

Compare:

```python
df.take(5)
```

and:

```python
df.collect()
```

Answer:

1. Which one requests a bounded result?
2. Which one requests all results?
3. Which one creates a greater driver-memory risk?
4. Why should `collect()` be treated carefully in production?

---

# 74. Hands-On Lab 6 — Narrow Transformation

Build:

```python
rdd2 = (
    rdd
    .map(lambda x: x * 2)
    .filter(lambda x: x > 10)
)
```

Then trigger:

```python
rdd2.count()
```

Explain:

```text
map
 ↓
filter
 ↓
count
```

and why these operations can form a narrow dependency chain.

Do not claim that this guarantees one exact physical stage in every possible execution environment.

---

# 75. Hands-On Lab 7 — Wide Transformation

Use:

```python
pairs = spark.sparkContext.parallelize([
    ("apple", 1),
    ("banana", 1),
    ("apple", 1),
])

counts = pairs.reduceByKey(
    lambda a, b: a + b
)

counts.collect()
```

Explain:

```text
reduceByKey
    ↓
same-key records may need redistribution
    ↓
shuffle
    ↓
collect action
```

The goal is conceptual reasoning, not detailed shuffle tuning.

---

# 76. Hands-On Lab 8 — Job Reasoning

Given:

```python
result = (
    df
    .filter(F.col("amount") > 0)
    .select("customer_id", "amount")
)

result.count()
```

Predict:

1. How many action requests?
2. What causes execution?
3. What is the job?
4. What does a task operate on?
5. What could create a stage boundary?

Then explain your reasoning.

Do not require an exact stage count if the execution details are not guaranteed by the example.

---

# 77. Predict → Run → Observe → Explain

Use the Module 2.14 learning loop:

```text
Predict
   ↓
Write the transformation chain
   ↓
Predict whether execution occurs
   ↓
Add an action
   ↓
Run
   ↓
Observe
   ↓
Explain jobs/stages/tasks conceptually
   ↓
Change one thing
   ↓
Run again
   ↓
Compare
```

For example, before running:

```python
df2 = df.filter(F.col("age") > 30)
```

predict:

```text
Will the entire dataset be processed immediately?
```

Then add:

```python
df2.count()
```

and predict again.

The purpose is to develop execution reasoning rather than memorize definitions.

---

# 78. Timing Experiment

Use:

```python
import time

start = time.time()

filtered = df.filter(
    F.col("age") > 30
)

end = time.time()

print(
    f"Transformation construction: "
    f"{end - start:.3f}s"
)
```

Then compare:

```python
start = time.time()

filtered = df.filter(
    F.col("age") > 30
)

filtered.count()

end = time.time()

print(
    f"Transformation + action: "
    f"{end - start:.3f}s"
)
```

Discuss:

- what each measurement captures
- why the first number does not represent complete distributed processing
- why the second number is more meaningful for basic execution timing
- why neither is a complete production benchmarking methodology

---

# 79. Production Scenario 1 — Unexpected Runtime

A developer says:

> "My 20-step pipeline runs in milliseconds."

The code contains only transformations:

```python
df1 = df.filter(...)
df2 = df1.select(...)
df3 = df2.withColumn(...)
# ...
df20 = df19.select(...)
```

### Diagnosis

No action or output operation has been shown.

The developer may be measuring only construction of the computation representation.

### Engineering response

Identify the action that ultimately consumes the result.

---

# 80. Production Scenario 2 — Repeated Computation

A pipeline contains:

```python
df2 = expensive_transformation(df)

df2.count()
df2.show()
df2.write.parquet("output/")
```

### Questions

1. How many action/output requests are present?
2. Could upstream computation repeat?
3. What information is needed before deciding whether persistence is justified?

### Reference reasoning

There are three result/output requests.

Without reuse mechanisms, Spark may need to perform upstream work again for later requests.

Before introducing persistence, measure the cost and reuse pattern.

---

# 81. Production Scenario 3 — Driver OOM

A developer executes:

```python
huge_df.collect()
```

on a multi-terabyte dataset.

### Diagnosis

The complete result is requested at the driver.

### Correct engineering reasoning

The problem is architectural:

```text
distributed dataset
        ↓
all records
        ↓
driver
```

A bounded inspection operation or distributed downstream processing is usually more appropriate depending on the requirement.

---

# 82. Production Scenario 4 — Stage Boundary

A pipeline contains an operation requiring records from different partitions to be redistributed.

### Reasoning

A wide dependency can require:

```text
partitioned input
     ↓
shuffle
     ↓
redistributed data
```

The shuffle can introduce a stage boundary.

Do not claim:

> "Every aggregation always creates exactly one shuffle."

The actual execution plan determines the physical behavior.

---

# 83. Production Scenario 5 — No Action

A developer builds a large transformation chain and the program exits.

### Question

Why did the program complete quickly?

### Answer

Because no final action/output request required the distributed computation to execute.

This is a direct consequence of lazy evaluation.

---

# 84. Advanced Reasoning: Lazy Graph Construction

A useful abstraction is:

```text
Transformations
      ↓
Dependency / computation representation
      ↓
Action
      ↓
Execution planning
      ↓
Distributed execution
```

For RDDs, lineage and partition dependencies are central to this representation.

For DataFrames, structured expressions and logical planning provide additional information.

This is the bridge from basic PySpark programming to advanced Spark execution analysis.

---

# 85. Advanced Reasoning: Fault Tolerance

Suppose a partition being processed by an executor is lost.

Spark can use the dependency information associated with the computation to determine how the lost data can be recomputed.

Conceptually:

```text
Original data
    ↓
Transformation A
    ↓
Transformation B
    ↓
Lost partition
    ↓
Recompute required dependency chain
```

This is why lineage matters.

Lazy evaluation and lineage are related, but do not confuse them:

```text
Lazy evaluation
= when distributed computation is executed

Lineage
= dependency history used to reason about derived data
```

---

# 86. Advanced Reasoning: Multiple Actions

Consider:

```python
result = (
    df
    .filter(...)
    .select(...)
    .groupBy(...)
)
```

Then:

```python
result.count()
result.show()
result.write.parquet(...)
```

A production engineer should immediately ask:

```text
How expensive is the upstream computation?

How many times is it being requested?

Is the result reused?

Would persistence be justified?

Is the output operation idempotent and correctly configured?

Are we accidentally moving data to the driver?
```

This is the beginning of execution-aware pipeline design.

---

# 87. Advanced Reasoning: Execution Is Not Textual Order

Consider:

```python
df.filter(...)
  .select(...)
  .withColumn(...)
```

The code is written in a sequence.

That does not mean Spark blindly executes each operation exactly as written and materializes its output before moving to the next.

Instead, Spark builds a representation of the required computation and determines an appropriate execution strategy.

For structured DataFrames, later optimizer topics explain this in much greater depth.

---

# 88. What You Should Be Able to Predict

Given:

```python
result = (
    df
    .filter(F.col("amount") > 0)
    .select("customer_id", "amount")
)
```

you should be able to say:

```text
No action yet.
```

Given:

```python
result.count()
```

you should say:

```text
An action has requested a result.
Spark must execute the required computation.
```

Given:

```python
result.collect()
```

you should say:

```text
The action requests all result rows at the driver.
```

Given:

```python
result.write.parquet("output/")
```

you should say:

```text
An output action requests distributed execution and writes the result.
```

Given:

```python
rdd.reduceByKey(...)
```

you should recognize:

```text
This is a transformation that may involve a wide dependency and shuffle.
```

That ability to predict execution behavior is the real learning objective.

---

# 89. Do Not Duplicate Later Topics

This chapter establishes the execution model only.

It does **not** deeply teach:

- complete DataFrame API reference
- Spark SQL
- join algorithms
- broadcast joins
- detailed shuffle optimization
- repartition
- coalesce
- data skew
- salting
- caching
- persistence
- Python UDFs
- pandas UDFs
- Catalyst internals
- Adaptive Query Execution
- data sources
- bucketing
- Spark UI
- advanced testing

Those subjects belong to later Module 2.14 files.

They may be referenced when needed to explain the concepts here.

---

# 90. Interview Preparation

## Basic

### 1. What is a Spark transformation?

**Model answer:**  
A transformation describes a new dataset derived from an existing dataset. It is generally evaluated lazily and becomes part of the computation dependency chain.

### 2. What is a Spark action?

**Model answer:**  
An action requests a result or output operation and causes Spark to execute the distributed computation required to produce that result.

### 3. What is lazy evaluation?

**Model answer:**  
Lazy evaluation means Spark generally delays distributed computation represented by transformations until an action requires a result.

### 4. Give three transformations.

**Model answer:**  
Examples include `map`, `filter`, `flatMap`, `select`, and `withColumn`.

### 5. Give three actions.

**Model answer:**  
Examples include `count`, `show`, `collect`, `first`, `take`, and output operations such as `write`.

### 6. What is lineage?

**Model answer:**  
Lineage is the dependency history describing how derived distributed data was produced from earlier data. It supports fault-tolerant recomputation.

---

## Moderate

### 7. What is a narrow dependency?

**Model answer:**  
A narrow dependency is one where a child partition can generally be computed from a limited or local set of parent partitions without requiring full redistribution.

### 8. What is a wide dependency?

**Model answer:**  
A wide dependency occurs when a child partition may depend on data from multiple parent partitions, commonly requiring redistribution or shuffle.

### 9. What causes a Spark job to execute?

**Model answer:**  
An action or output request causes Spark to execute the computation required to produce the requested result.

### 10. What is the relationship between a job, stage, and task?

**Model answer:**  
An action can trigger a job. A job can contain multiple stages separated by relevant dependency boundaries. Each stage is executed through tasks operating on partitions.

### 11. Does every transformation create a stage?

**Model answer:**  
No. Transformations describe computation. Stages are execution units determined by dependency boundaries and the execution plan.

### 12. Does every action create exactly one stage?

**Model answer:**  
No. An action can trigger a job containing multiple stages.

---

## Hard

### 13. Why does Spark use lazy evaluation?

**Model answer:**  
Lazy evaluation avoids unnecessary computation, allows Spark to construct the required computation chain, reduces unnecessary intermediate materialization, and creates opportunities for planning and optimization.

### 14. Why can multiple actions cause repeated computation?

**Model answer:**  
Each action is a separate request for a result. If upstream intermediate data is not persisted and must be recomputed for the later action, Spark may repeat substantial work.

### 15. Why is `collect()` dangerous?

**Model answer:**  
`collect()` requests all selected records at the driver. If the result is too large, driver memory can be exhausted.

### 16. How should you benchmark a transformation?

**Model answer:**  
Include an action in the timing measurement. Timing only the transformation call generally measures construction of the computation representation rather than distributed processing.

### 17. Why can a shuffle create a stage boundary?

**Model answer:**  
A shuffle redistributes data between partitions. Downstream computation depends on the redistributed data, so Spark can separate the pre-shuffle and post-shuffle work into different stages.

### 18. Is every wide transformation slow?

**Model answer:**  
Not necessarily. Wide dependencies can introduce redistribution and additional cost, but actual performance depends on data volume, partitioning, cluster resources, execution plan, and workload.

---

## Advanced

### 19. Explain lazy evaluation and lineage together.

**Model answer:**  
Lazy evaluation controls when distributed computation is executed, while lineage describes dependencies among derived datasets. Spark can defer execution while retaining enough dependency information to execute and, where needed, recompute data.

### 20. A developer says `df.filter(...)` took 0.001 seconds on a huge table. What do you say?

**Model answer:**  
That timing likely measured transformation construction rather than full distributed execution because no action was shown. Add an action such as `count()` for a basic execution-time experiment.

### 21. How would you reason about a pipeline with `count()`, `show()`, and `write()`?

**Model answer:**  
Treat them as separate action/output requests. Investigate whether expensive upstream work is repeated, whether persistence is justified, and whether the output semantics are safe.

### 22. Why should exact stage counts not be guessed from source code alone?

**Model answer:**  
Stage structure depends on dependency relationships and Spark's physical execution planning. Source code alone does not always determine the exact final stage structure.

---

## Production and Architecture

### 23. How would you debug a pipeline that appears to execute instantly but produces no output?

**Model answer:**  
Check whether the code contains any action or output operation. A transformation-only pipeline can finish quickly because the distributed computation has not been requested.

### 24. A 500 GB pipeline calls `collect()`. What is your first concern?

**Model answer:**  
The complete result is being requested at the driver, creating a potential driver-memory failure. I would first question why the full distributed result needs to be materialized at the driver.

### 25. How would you explain lazy evaluation to a production team?

**Model answer:**  
Transformations describe the computation, while actions request its result. Spark can defer distributed execution until the result is needed, allowing it to reason about the computation before executing it.

### 26. What questions should a production engineer ask when seeing multiple actions?

**Model answer:**  
How expensive is the upstream computation? Is the result reused? Could the computation be repeated? Is persistence justified? Are any actions moving data to the driver? Are output side effects safe?

---

# 91. Practice Questions

## Basic — 10 Questions

1. What is a transformation?
2. What is an action?
3. What does lazy evaluation mean?
4. Give three examples of RDD transformations.
5. Give three examples of DataFrame transformations.
6. Give three examples of Spark actions.
7. What is lineage?
8. What is a partition?
9. Why is `collect()` potentially dangerous?
10. What operation normally causes Spark to execute a transformation chain?

---

## Moderate — 10 Questions

1. Explain the difference between a narrow and wide dependency.
2. Why can `reduceByKey()` require a shuffle?
3. What is a Spark job?
4. What is a stage?
5. What is a task?
6. How are jobs, stages, tasks, and partitions related?
7. Why does a wide dependency potentially create a stage boundary?
8. Why does `show()` not have the same driver-memory behavior as `collect()`?
9. Why can two actions on the same DataFrame cause repeated work?
10. Why does measuring only `df.filter(...)` not measure full distributed execution?

---

## Hard — 10 Questions

1. Explain why Spark does not execute every transformation immediately.
2. Explain why lazy evaluation can reduce unnecessary work.
3. Explain how lineage supports fault tolerance.
4. Why is "narrow means fast and wide means slow" an inadequate model?
5. Explain how a shuffle changes the dependency structure between partitions.
6. Why can an action with a tiny result still require substantial distributed computation?
7. Why should exact stage counts not be inferred casually from source code?
8. Explain why `df.count()` can be expensive even though it returns one integer.
9. Explain the difference between constructing a computation and executing a computation.
10. Explain why multiple actions should be considered during production pipeline design.

---

## Advanced — 10 Questions

1. Trace the execution model from a transformation chain through an action to executor work.
2. Explain how lazy evaluation, lineage, and dependency structure interact.
3. A pipeline has ten transformations and three actions. What production questions should you ask?
4. Why can a transformation-only script complete quickly even when the source dataset is huge?
5. How would you design a safe inspection workflow for a multi-terabyte DataFrame?
6. Explain how a wide dependency can influence stage structure.
7. Why is transformation timing different from execution timing?
8. How would you diagnose unexpected repeated computation?
9. Explain why the final result size does not necessarily indicate the amount of distributed work.
10. Explain the production principle: "What action ultimately requires this data?"

---

# 92. Final Architecture Exercise

## Scenario

A Data Engineering team processes **500 GB of transaction data**.

The pipeline performs:

```text
Read transaction data
        ↓
Filter invalid rows
        ↓
Select required columns
        ↓
Calculate derived metrics
        ↓
Aggregate by customer
        ↓
Write result to a lakehouse
```

### Task 1 — Identify Transformations

Identify the operations that describe computation.

Expected reasoning:

```text
filter
select
derived calculation
aggregate
```

These describe the desired computation.

### Task 2 — Identify the Final Action

The final write operation requests output:

```text
write
```

This causes Spark to execute the required computation.

### Task 3 — Explain Lazy Evaluation

Before the write request, Spark can construct the computation representation.

Conceptually:

```text
read
 ↓
filter
 ↓
select
 ↓
derive
 ↓
aggregate
 ↓
write
```

The distributed processing required to produce the output is triggered by the output request.

### Task 4 — Where Might a Shuffle Occur?

The customer aggregation may require records for the same customer to be brought together.

That can require redistribution:

```text
Partitions
   ↓
shuffle
   ↓
customer-based aggregation
```

Do not assume an exact number of shuffle operations or stages without examining the actual physical execution.

### Task 5 — What Causes a Job to Execute?

The output action:

```text
write
```

requests the result.

Conceptually:

```text
write
 ↓
job
```

### Task 6 — How Are Stages Conceptually Formed?

A portion of the computation that can be executed without crossing a relevant dependency boundary can belong to one stage.

A shuffle can create a boundary:

```text
Stage 1
   ↓
shuffle
   ↓
Stage 2
```

The exact stage structure is execution-plan dependent.

### Task 7 — What Does a Task Operate On?

A task performs work associated with one partition within a stage.

Conceptually:

```text
Stage
  ↓
Task 1 → Partition 1
Task 2 → Partition 2
Task 3 → Partition 3
...
```

### Task 8 — What Happens If There Are Multiple Actions?

If the pipeline instead performs:

```python
result.count()
result.show()
result.write.parquet(...)
```

there are multiple action/output requests.

Without appropriate reuse mechanisms, upstream work may be repeated.

### Task 9 — What Happens If the Developer Calls `collect()`?

The developer requests all selected results at the driver.

For a huge dataset, this can cause driver-memory exhaustion.

---

# 93. Reference Architecture Reasoning

A strong production explanation would be:

> The pipeline is represented as a chain of lazy transformations. Spark does not need to perform the complete distributed computation merely because those transformations are defined. The final output action requests execution, causing Spark to create a job and execute the required stages through tasks operating on partitions. If the customer aggregation requires records from different partitions to meet, a shuffle can introduce a stage boundary. Multiple actions may cause repeated upstream computation when intermediate results are not persisted. A full `collect()` would be inappropriate for a large result because it moves the result to the driver.

This is the execution model you should carry into the rest of Module 2.14.

---

# 94. Knowledge Checkpoint

Before moving to Topic 05, explain the following without looking at your notes.

## Transformations

- What is a transformation?
- Why does Spark use transformations?
- Give three RDD transformation examples.
- Give three DataFrame transformation examples.
- What is a narrow dependency?
- What is a wide dependency?

## Actions

- What is an action?
- Give three action examples.
- Why does an action trigger execution?
- Why are actions not all equivalent?
- Why is `collect()` dangerous?

## Lazy Evaluation

- What does lazy evaluation mean?
- Why does Spark use lazy evaluation?
- What is the difference between constructing a computation and executing it?
- Why can lazy evaluation reduce unnecessary computation?
- How does lazy evaluation relate to planning?

## Execution

- What is a job?
- What is a stage?
- What is a task?
- What is a partition?
- What can create a stage boundary?
- Why should exact stage counts not be guessed casually?

## Production

- Why can multiple actions cause repeated work?
- How should transformation timing be measured?
- Why is `count()` potentially expensive despite returning one integer?
- Why is `collect()` dangerous on large data?
- What action ultimately requires your pipeline's data?

If you cannot explain these ideas in your own words, review the relevant sections before advancing.

---

# 95. Final Mental Model

Keep this model available whenever you write PySpark:

```text
Transformation
      ↓
Build computation
      ↓
Lazy
      ↓
More transformations
      ↓
Action
      ↓
Job
      ↓
Stages
      ↓
Tasks
      ↓
Partitions
      ↓
Executors
      ↓
Distributed execution
```

The core principle is:

> **Transformations describe the work. Actions request the result. Lazy evaluation allows Spark to delay distributed execution until the result is actually required.**

Then add the dependency model:

```text
Narrow dependency
      ↓
local/limited partition dependency
```

versus:

```text
Wide dependency
      ↓
redistribution may be required
      ↓
shuffle
      ↓
possible stage boundary
```

And finally the production model:

```text
Transformation chain
      ↓
What action requires it?
      ↓
How much work will execute?
      ↓
Could there be a shuffle?
      ↓
Could work be repeated?
      ↓
Could data move to the driver?
      ↓
How does it behave at production scale?
```

This execution-aware mindset is more important than memorizing individual API names.

---

# 96. Glossary

## Transformation

An operation that describes a new dataset derived from an existing dataset.

## Action

An operation that requests a result or output and triggers the required distributed computation.

## Lazy Evaluation

The model in which Spark delays execution of distributed transformations until an action requires a result.

## Eager Evaluation

A programming model in which an operation performs its computation immediately when invoked. Spark transformations generally do not use this model.

## Lineage

The dependency history describing how derived distributed data was produced.

## RDD

Resilient Distributed Dataset, Spark's lower-level distributed collection abstraction.

## DataFrame

Spark's higher-level structured distributed-data abstraction with named columns and schema.

## Partition

A unit of distributed data processing.

## Dependency

A relationship describing how one stage or dataset depends on upstream partitions or computation.

## Narrow Dependency

A dependency where a child partition can generally be computed from a limited/local set of parent partitions without requiring full redistribution.

## Wide Dependency

A dependency where a child partition may depend on data from multiple parent partitions, commonly requiring redistribution.

## Shuffle

Redistribution of data across partitions, often involving network and disk I/O.

## Job

A unit of Spark computation associated with an action.

## Stage

A portion of a job separated by relevant dependency boundaries.

## Task

A unit of work performed for one partition within a stage.

## Driver

The process coordinating the Spark application.

## Executor

A process that runs Spark tasks.

## Distributed Execution

Processing data across multiple partitions and potentially multiple executor processes or machines.

## Materialization

The point at which a computation's data is actually produced rather than merely represented as a pending computation.

## Recomputation

Re-executing required upstream computation to reconstruct lost or otherwise unpersisted derived data.

---

# 97. Production Engineering Mindset

Throughout future Spark work, ask these questions:

```text
What transformation am I defining?

What action ultimately requires this data?

When will the distributed computation actually execute?

How many action requests does my application make?

Could this action bring data to the driver?

Where might a shuffle occur?

What dependencies exist between partitions?

Could repeated actions cause repeated computation?

Am I measuring actual execution time?

How does lineage support recovery?

What happens if an executor fails?

How does this pipeline behave at production scale?
```

These questions turn PySpark from an API-learning exercise into distributed-systems engineering.

---

# 98. Topic Completion Standard

You should consider Topic 04 complete only when you can:

- define transformations
- define actions
- distinguish transformations from actions
- explain lazy evaluation
- explain why Spark uses lazy evaluation
- explain lineage
- explain narrow dependencies
- explain wide dependencies
- explain shuffle boundaries conceptually
- trace action → job → stages → tasks → partitions
- identify when distributed execution is requested
- identify dangerous `collect()` usage
- explain repeated action behavior
- measure execution rather than merely transformation construction
- reason about a production pipeline from its action backward
- explain why exact stage counts depend on execution details
- explain why not every transformation creates a stage
- explain why not every action sends all data to the driver
- debug common lazy-evaluation misconceptions
- describe these concepts clearly without relying on memorized definitions

---

# 99. Final Summary

Spark's execution model can be reduced to one foundational idea:

```text
Transformations
    ↓
Describe computation
    ↓
Lazy evaluation
    ↓
Action
    ↓
Trigger required execution
    ↓
Job
    ↓
Stages
    ↓
Tasks
    ↓
Partitions
    ↓
Executors
```

Transformations such as:

```python
map()
filter()
select()
withColumn()
```

describe computation.

Actions such as:

```python
count()
show()
take()
collect()
write()
```

request a result or output.

Lazy evaluation allows Spark to defer distributed execution until that result is required.

Lineage and dependency relationships allow Spark to reason about how derived data depends on upstream data.

Narrow dependencies generally preserve local or limited partition relationships.

Wide dependencies may require redistribution and shuffle, which can create stage boundaries.

Multiple actions can cause repeated upstream computation when intermediate results are not persisted.

`collect()` can turn a distributed computation into a driver-memory problem.

The production engineer therefore does not merely ask:

> "What PySpark function should I call?"

Instead, ask:

> **"What computation am I describing, what action ultimately requires it, and how will Spark execute that computation across partitions, tasks, stages, and executors?"**

That mental model is the foundation for the next topics in Module 2.14, including the DataFrame API, Spark SQL, joins and shuffle behavior, partitioning, skew, caching, optimization, and Spark UI debugging.
