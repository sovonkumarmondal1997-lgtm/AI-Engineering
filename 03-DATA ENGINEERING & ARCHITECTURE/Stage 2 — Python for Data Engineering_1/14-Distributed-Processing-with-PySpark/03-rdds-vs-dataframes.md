# Module 2.14 — Distributed Processing with PySpark

# Topic 03 — RDDs vs DataFrames

## Learning Objectives

By the end of this chapter, you should be able to:

1. Explain what an RDD is.
2. Explain what a DataFrame is.
3. Explain why Spark provides multiple data abstractions.
4. Understand distributed collections and partitions.
5. Explain RDD immutability and lineage.
6. Create and manipulate RDDs with PySpark.
7. Create DataFrames with PySpark.
8. Explain schema, rows, columns, and structured data.
9. Distinguish lower-level distributed object processing from structured processing.
10. Explain why DataFrames provide Spark with more information for optimization.
11. Explain the Python/JVM implications of PySpark RDD operations.
12. Compare RDD and DataFrame implementations of the same problem.
13. Convert between RDDs and DataFrames when there is a clear reason.
14. Explain why `collect()` can be dangerous.
15. Identify legitimate RDD use cases.
16. Identify common production workloads that naturally fit DataFrames.
17. Make a production-oriented abstraction choice without relying on simplistic performance claims.

---

## 1. Why Does Spark Need Data Abstractions?

Suppose you have a small Python collection:

```python
numbers = [1, 2, 3, 4, 5]
```

A single Python process can work with it directly.

Now imagine that the dataset contains several terabytes of records. It cannot fit comfortably into the memory of one machine, and one CPU cannot process it in an acceptable amount of time.

The problem becomes:

```text
Local data
    ↓
Too much data for one machine
    ↓
Data must be distributed
    ↓
Multiple machines process different pieces
    ↓
Spark needs an abstraction for that distributed data
```

An abstraction is a model that gives you a useful way to work with something without requiring you to manually manage every physical detail.

Spark historically provided the **RDD**, or Resilient Distributed Dataset, as a fundamental distributed collection abstraction.

For structured data processing, Spark provides the **DataFrame**, a higher-level abstraction representing distributed data organized into named columns with a schema.

A useful progression is:

```text
Python collection
        ↓
Data too large for one machine
        ↓
Distributed collection
        ↓
RDD
        ↓
Structured distributed data
        ↓
DataFrame
```

The important distinction is:

```text
data
```

versus:

```text
an abstraction used to process data
```

An RDD or DataFrame is not the data itself in the everyday physical-storage sense. It is a Spark abstraction that describes how distributed data can be represented and processed.

---

# 2. Connection to the Previous Topics

Topic 01 introduced the basic distributed execution model:

```text
Driver
   ↓
Executors
   ↓
Tasks
   ↓
Partitions
```

Topic 02 introduced `SparkSession`, configuration, local execution, deployment modes, and `spark-submit`.

A simple application can begin with:

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("RDDDataFrameDemo")
    .getOrCreate()
)
```

The important point for this chapter is that both RDDs and DataFrames ultimately participate in Spark's distributed execution model.

Conceptually:

```text
RDD / DataFrame
       ↓
   partitions
       ↓
     tasks
       ↓
   executors
```

This chapter does not repeat the full driver/executor or deployment discussion. Instead, it focuses on the data abstractions themselves.

---

# 3. What Is an RDD?

**RDD** stands for:

> **Resilient Distributed Dataset**

Each word communicates an important design property.

## 3.1 Resilient

Resilient means that Spark can recover from certain failures by using information about how an RDD was derived.

The important concepts are:

- lineage
- partition dependencies
- recomputation
- fault tolerance

If a partition is lost because an executor fails, Spark can often recompute that partition from the RDD's lineage rather than requiring the entire application to start again from scratch.

This is one reason RDDs are called resilient.

---

## 3.2 Distributed

An RDD is not necessarily held on one machine.

It is logically one distributed collection that is divided into partitions.

```text
RDD
 |
 +---- Partition 1
 |
 +---- Partition 2
 |
 +---- Partition 3
 |
 +---- Partition 4
```

Different partitions can be processed in parallel.

Conceptually:

```text
1 partition
     ↓
1 task
```

This connects directly to the distributed execution model introduced in Topic 01.

---

## 3.3 Dataset

Dataset means that an RDD represents a collection of records or objects.

Those records can be simple values:

```python
1
2
3
4
```

or more complex Python objects:

```python
("Alice", 30)
("Bob", 25)
```

or dictionaries and other application-level representations.

The RDD abstraction does not require a tabular schema with named columns.

---

# 4. RDD Mental Model

A useful mental model is:

```text
RDD
 |
 +---- Partition 1
 |
 +---- Partition 2
 |
 +---- Partition 3
 |
 +---- Partition 4
```

Logically:

```text
one distributed collection
```

Physically:

```text
many partitions
```

Those partitions provide the units over which Spark can schedule work.

Do not confuse the logical RDD with one physical file or one physical machine.

An RDD is a distributed computational abstraction.

---

# 5. RDD Immutability

RDDs are **immutable**.

Immutable means that an existing RDD is not changed in place by a transformation.

Instead, a transformation produces another RDD.

For example:

```python
rdd2 = rdd1.map(lambda x: x * 2)
```

The conceptual model is:

```text
RDD 1
  |
  | map
  v
RDD 2
```

Another transformation can create another RDD:

```text
RDD 1
  |
  | map
  v
RDD 2
  |
  | filter
  v
RDD 3
```

Immutability helps Spark reason about:

- lineage
- dependencies
- recomputation
- reproducibility

It also makes the programming model easier to reason about because transformations describe new distributed datasets rather than mutating an existing dataset in place.

---

# 6. RDD Lineage

Lineage is the history of transformations needed to produce an RDD.

For example:

```text
Input
  ↓
RDD 1
  ↓ map
RDD 2
  ↓ filter
RDD 3
```

The lineage captures the dependency relationship between these logical datasets.

If a partition of `RDD 3` is lost, Spark can use the dependency information to determine how to recompute it from earlier data.

This is a key part of Spark's fault-tolerance model.

The important mental model is:

```text
RDD
 ↓
transformation history
 ↓
dependency information
 ↓
possible recomputation
```

The complete execution behavior of transformations and actions is covered in the next topic. Here, lineage is introduced as a fundamental RDD property.

---

# 7. Creating RDDs

## 7.1 Creating an RDD with `parallelize()`

For small demonstration or test data:

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("RDDDemo")
    .getOrCreate()
)

numbers = [1, 2, 3, 4, 5]

rdd = spark.sparkContext.parallelize(numbers)
```

Here:

- `spark.sparkContext` accesses the underlying Spark context.
- `parallelize()` creates an RDD from a local collection.
- Spark distributes the collection into partitions.

### Important production warning

The original Python collection exists on the driver before `parallelize()` is called.

Therefore:

```python
huge_local_python_collection
        ↓
driver memory
        ↓
parallelize()
```

is not a general production ingestion strategy for large datasets.

`parallelize()` is especially useful for:

- small examples
- unit tests
- demonstrations
- controlled local experiments

---

## 7.2 Creating an RDD from Text Data

Spark can also create an RDD from a file-based source:

```python
lines = spark.sparkContext.textFile("path/to/file.txt")
```

The important conceptual distinction is:

```text
parallelize()
    ↓
starts with a driver-side collection
```

whereas:

```text
textFile()
    ↓
reads distributed/file-backed input
```

The exact partitioning and physical behavior depends on the source and Spark's input processing.

Do not treat `textFile()` as merely a different spelling of `parallelize()`.

---

# 8. Basic RDD Operations

RDD APIs include operations such as:

```python
map()
filter()
flatMap()
reduce()
collect()
count()
take()
```

The purpose here is to establish the RDD abstraction. Detailed treatment of transformations, actions, and lazy evaluation belongs to Topic 04.

---

## 8.1 `map()`

`map()` applies a function to each record.

```python
numbers = [1, 2, 3, 4, 5]

rdd = spark.sparkContext.parallelize(numbers)

doubled = rdd.map(lambda x: x * 2)

print(doubled.collect())
```

Expected demonstration output:

```text
[2, 4, 6, 8, 10]
```

Conceptually:

```text
1 → 2
2 → 4
3 → 6
4 → 8
5 → 10
```

Distributed interpretation:

```text
Partition A → process its records
Partition B → process its records
Partition C → process its records
```

The transformation operates across the records in the distributed collection.

---

## 8.2 `filter()`

`filter()` keeps records that satisfy a condition.

```python
numbers = [1, 2, 3, 4, 5]

rdd = spark.sparkContext.parallelize(numbers)

even_numbers = rdd.filter(lambda x: x % 2 == 0)

print(even_numbers.collect())
```

Expected demonstration output:

```text
[2, 4]
```

---

## 8.3 `flatMap()`

`flatMap()` can produce zero, one, or many output records for each input record.

A classic example is splitting lines into words:

```python
lines = spark.sparkContext.parallelize([
    "spark is distributed",
    "spark processes data"
])

words = lines.flatMap(lambda line: line.split())

print(words.collect())
```

Possible output:

```text
["spark", "is", "distributed", "spark", "processes", "data"]
```

Conceptually:

```text
line
 ↓
many words
```

---

## 8.4 `reduce()`

`reduce()` combines records using a function.

```python
numbers = spark.sparkContext.parallelize([1, 2, 3, 4])

total = numbers.reduce(lambda a, b: a + b)

print(total)
```

Output:

```text
10
```

The operation represents distributed aggregation, although the exact execution mechanics and stage behavior are intentionally deferred to Topic 04 and later shuffle material.

---

## 8.5 `count()`

```python
count = rdd.count()
```

This returns the number of records.

---

## 8.6 `take()`

For a small sample:

```python
sample = rdd.take(5)
```

`take()` is often safer for inspection than collecting an entire large dataset.

---

## 8.7 `collect()` — Use With Care

```python
records = rdd.collect()
```

`collect()` returns all records to the driver.

That means:

```text
Distributed data
      ↓
Driver
      ↓
Driver memory
```

For a small demonstration dataset, this can be fine.

For a large production dataset, it can cause a driver out-of-memory failure.

A good mental rule is:

> `collect()` is a data movement operation to the driver, not merely a display operation.

---

# 9. Pair RDDs

An RDD can contain key-value pairs.

For example:

```python
pairs = spark.sparkContext.parallelize([
    ("apple", 1),
    ("banana", 1),
    ("apple", 1)
])
```

This is commonly called a **pair RDD**.

Pair RDD operations include:

```python
reduceByKey()
groupByKey()
mapValues()
```

For example:

```python
counts = pairs.reduceByKey(lambda a, b: a + b)

print(counts.collect())
```

Conceptually, the result contains:

```text
apple  → 2
banana → 1
```

The important point at this stage is that key-based operations may require records with the same key to be brought together across partitions.

That can involve distributed data movement.

The detailed mechanics of shuffle, partitioning, broadcast joins, and performance tuning are covered later in the module. Do not treat this introductory discussion as the full shuffle chapter.

---

# 10. What Is a DataFrame?

A Spark **DataFrame** is:

> A distributed collection of data organized into named columns with a schema.

The key ideas are:

```text
Distributed
Structured
Rows
Columns
Schema
```

A DataFrame has a table-like logical representation.

For example:

```text
+-------+-----+-------+
| name  | age | city  |
+-------+-----+-------+
| Alice | 30  | Delhi |
| Bob   | 25  | Pune  |
+-------+-----+-------+
```

This is conceptually similar to a SQL table.

However, a Spark DataFrame is not simply a local database table.

It represents structured distributed data that Spark can process across partitions and executors.

---

# 11. DataFrame Mental Model

A useful model is:

```text
DataFrame
    ↓
Distributed partitions
    ↓
Structured execution
```

The table-like interface is logical.

The underlying processing remains distributed.

For example:

```text
DataFrame
 |
 +---- Partition 1
 |
 +---- Partition 2
 |
 +---- Partition 3
 |
 +---- Partition 4
```

The learner should therefore avoid this misconception:

> "A DataFrame is not distributed because it looks like a table."

The table-like abstraction hides much of the distributed implementation detail from application code.

---

# 12. DataFrame Schema

A DataFrame contains structural information about its columns.

For example:

```python
df.printSchema()
```

might produce:

```text
root
 |-- name: string
 |-- age: long
 |-- city: string
```

A schema describes information such as:

- column names
- data types
- nullability
- nested structure where applicable

Schema information matters because it provides Spark and the developer with more information about the data.

It improves:

- validation
- correctness
- readability
- interoperability with SQL
- opportunities for execution optimization

A schema also communicates the intended shape of the dataset to other engineers.

---

# 13. Creating DataFrames

A simple DataFrame can be created from local data:

```python
data = [
    ("Alice", 30),
    ("Bob", 25),
]

df = spark.createDataFrame(
    data,
    ["name", "age"],
)

df.show()
```

Conceptually:

```text
Python records
      ↓
DataFrame
      ↓
named columns + schema
```

For production data processing, DataFrames are also commonly created by reading structured data:

```python
df = spark.read.parquet("data/")
```

The detailed DataFrame reader/writer API and data-source behavior are covered later.

---

# 14. RDD vs DataFrame: The Core Difference

At the highest level:

```text
RDD
 ↓
Lower-level distributed collection of records/objects
```

while:

```text
DataFrame
 ↓
Higher-level structured distributed data
 ↓
Named columns + schema
```

A foundational comparison:

| Dimension | RDD | DataFrame |
|---|---|---|
| Abstraction | Lower-level distributed collection | Higher-level structured data |
| Schema | No required schema | Schema-aware |
| API style | Functional/object-oriented | Relational/column-oriented |
| Optimization information | Less structural information available | More structural information available |
| SQL integration | Limited | Native Spark SQL integration |
| Python interaction | Python record/object processing can be prominent | Spark-native expressions can avoid unnecessary Python-level execution |
| Serialization concerns | More exposed for arbitrary Python objects | Spark has more opportunities to use optimized internal representations |
| Typical use | Specialized or lower-level distributed logic | Structured ETL, analytics, SQL, and data processing |

The table is only a summary. Each dimension needs to be understood rather than memorized.

---

# 15. Why Spark Has Multiple Abstractions

A single abstraction cannot naturally express every kind of distributed computation.

Consider two workloads.

### Workload A

```text
Read Parquet
    ↓
Filter rows
    ↓
Select columns
    ↓
Calculate expressions
    ↓
Aggregate
    ↓
Write result
```

This is naturally structured.

### Workload B

```text
Create custom distributed objects
    ↓
Apply specialized object-level algorithm
    ↓
Manipulate arbitrary application structures
```

This may not map naturally to relational operations.

Spark's multiple abstractions allow engineers to work at different levels of abstraction.

The engineering question is not:

> "Which abstraction is universally superior?"

Instead:

> "Which abstraction naturally expresses this workload while giving Spark and the engineering team the information they need?"

---

# 16. RDD Objects vs Structured Data

An RDD can contain arbitrary records or objects.

For example:

```python
rdd = spark.sparkContext.parallelize([
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
])
```

Conceptually, Spark sees a distributed collection whose records are Python-level objects.

A DataFrame instead exposes structured information:

```text
name: string
age: long
```

Do not describe a DataFrame as simply:

> "an RDD with column names."

That is an oversimplification.

A DataFrame provides a distinct structured abstraction that Spark can reason about using relational semantics and structured execution planning.

---

# 17. Why DataFrames Can Provide More Optimization Opportunities

A common but incomplete statement is:

> "DataFrames are faster because they are optimized."

That does not explain the important part.

The deeper reasoning is:

```text
Schema
   ↓
Structured expressions
   ↓
Logical representation
   ↓
Optimization opportunities
   ↓
Efficient physical execution
```

When Spark knows that an operation is structured, it can potentially reason about:

- which columns are required
- which filters can be pushed toward data sources
- which expressions can be simplified
- which operations can be rearranged or combined
- which physical execution strategy is appropriate

This is where concepts such as **Catalyst**, **Tungsten**, code generation, and optimized internal representations become relevant.

At this stage, only the conceptual relationship matters.

Later topics provide the detailed optimizer and execution-plan material.

---

# 18. Catalyst: Introductory View

**Catalyst** is Spark SQL's query optimization framework.

At a high level:

```text
DataFrame / SQL operation
        ↓
Logical representation
        ↓
Analysis
        ↓
Optimization
        ↓
Physical planning
        ↓
Execution
```

The important Topic 03 idea is:

> A DataFrame gives Spark structured information that can participate in this planning and optimization process.

RDD transformations expose less relational structure to the optimizer.

The complete Catalyst and `explain()` discussion belongs to Topic 12.

---

# 19. Tungsten and Efficient Execution: Introductory View

Spark's execution engine includes techniques for efficient memory management, binary representations, code generation, and CPU-efficient processing.

These concepts are often discussed under the broader **Tungsten** execution work.

The important distinction is:

```text
RDD:
arbitrary record/object processing can expose more
serialization and Python-object overhead
```

versus:

```text
DataFrame:
structured operations give Spark more opportunities to
use optimized internal execution
```

This is not a promise that every DataFrame operation will outperform every RDD implementation.

Performance remains workload-dependent.

---

# 20. Python/JVM Considerations in PySpark

This is particularly important when reasoning about PySpark.

A simplified architecture is:

```text
PySpark application
        |
        v
Python process
        |
        v
Spark JVM
        |
        v
Distributed execution
```

Spark itself is JVM-based.

PySpark provides Python APIs over Spark.

When an RDD transformation contains Python logic such as:

```python
rdd.map(lambda x: x * 2)
```

the computation involves Python-level execution and therefore can involve communication and serialization between the Python runtime and Spark's JVM-side execution environment.

The exact mechanics depend on the operation and execution path, but the key engineering idea is:

> Arbitrary Python object processing gives Spark less opportunity to execute the computation entirely through Spark-native structured execution.

---

# 21. RDD Serialization

When Python objects cross execution boundaries, serialization and deserialization can become important.

Conceptually:

```text
Python object
     ↓
serialization
     ↓
communication
     ↓
Python/JVM or worker boundary
     ↓
deserialization
```

The costs can include:

- CPU overhead
- memory overhead
- network transfer
- object materialization

Arbitrary Python objects are also harder for Spark's structured optimizer to reason about than expressions over known structured columns.

This does not mean that every RDD operation is automatically slow. It means the abstraction exposes different optimization opportunities and runtime costs.

---

# 22. DataFrame Built-In Expressions

DataFrames can express transformations using Spark-native expressions.

For example:

```python
from pyspark.sql import functions as F

result = df.select(
    F.col("name"),
    (F.col("age") + 1).alias("next_age"),
)
```

The conceptual flow is:

```text
Python API call
      ↓
Spark expression
      ↓
Structured execution plan
      ↓
Spark execution engine
```

Compare that with:

```python
rdd.map(lambda row: row["age"] + 1)
```

The latter directly expresses Python-level record processing.

The DataFrame expression tells Spark more about the operation itself.

The later UDF chapter explores what happens when logic cannot be expressed through Spark-native built-ins.

---

# 23. Same Problem, Two Approaches

Suppose the requirement is:

> Find customers older than 30.

Assume an RDD contains dictionary-like records.

### RDD

```python
rdd_result = rdd.filter(
    lambda row: row["age"] > 30
)
```

### DataFrame

```python
from pyspark.sql import functions as F

df_result = df.filter(
    F.col("age") > 30
)
```

Both can represent the same business requirement.

But the abstractions communicate different information.

### RDD approach

The application provides a Python function over records.

### DataFrame approach

The application provides a structured column expression.

This difference affects:

- readability
- schema awareness
- optimizer visibility
- Python execution
- maintainability

It does not mean that every DataFrame implementation is automatically faster.

---

# 24. Word Count: RDD Style

Word count is a classic RDD example.

```python
words = (
    lines
    .flatMap(lambda line: line.split())
    .map(lambda word: (word, 1))
    .reduceByKey(lambda a, b: a + b)
)
```

The processing model is explicit:

```text
lines
  ↓
split lines
  ↓
individual words
  ↓
(word, 1)
  ↓
combine values by key
```

This example demonstrates why RDDs are powerful: they allow direct record-level transformations.

It also demonstrates why RDD code can become lower-level: the developer explicitly defines record manipulation.

---

# 25. Word Count: Structured Style

A DataFrame approach can represent the same problem using structured operations.

A simplified example is:

```python
from pyspark.sql import functions as F

word_counts = (
    lines_df
    .select(F.explode(F.split(F.col("value"), r"\s+")).alias("word"))
    .groupBy("word")
    .count()
)
```

The important lesson is not the exact syntax.

The conceptual difference is:

```text
RDD:
explicit record/object transformations
```

versus:

```text
DataFrame:
structured column expressions and relational operations
```

The DataFrame representation gives Spark more structural information about the computation.

---

# 26. RDD Advantages

RDDs can be useful when the workload genuinely benefits from lower-level distributed collection semantics.

Examples include:

- highly custom record-level transformations
- irregular or unstructured data
- algorithms that naturally operate on distributed objects
- legacy Spark applications
- specialized low-level distributed processing
- cases where the DataFrame abstraction does not express the required logic conveniently

The key word is **genuinely**.

Choosing an RDD simply because it feels familiar is different from choosing it because the workload actually requires its abstraction.

---

# 27. RDD Disadvantages

RDDs generally require the developer to manage more details at the application level.

Common trade-offs include:

- lower-level API
- less structural information
- fewer optimizer opportunities
- more visible serialization concerns
- potentially more Python overhead in PySpark
- harder-to-maintain pipelines
- less natural SQL integration
- greater responsibility on the developer

For structured Data Engineering workloads, these trade-offs can make an RDD implementation unnecessarily complex.

---

# 28. DataFrame Advantages

DataFrames provide:

- schema
- named columns
- SQL integration
- higher-level APIs
- structured expressions
- more optimizer visibility
- optimization opportunities
- readability
- maintainability
- interoperability with Spark SQL
- a natural abstraction for structured ETL and analytics

These are especially useful when the workload looks like:

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

---

# 29. DataFrame Limitations

DataFrames are not the natural abstraction for every algorithm.

Potential limitations include:

- less direct control over individual Python objects
- awkward expression of some arbitrary algorithms
- object-oriented custom logic may not map naturally
- specialized distributed algorithms may fit a lower-level abstraction better
- some debugging situations require a strong understanding of Spark's execution model

Therefore:

```text
higher-level
```

does not mean:

```text
universally appropriate
```

---

# 30. When Should You Use RDDs?

Use a deliberate decision process.

```text
Is the data structured?
        |
       YES
        ↓
Can Spark SQL/DataFrame APIs express the logic?
        |
       YES
        |
        └──→ Prefer the DataFrame abstraction
        |
       NO
        ↓
Is low-level distributed object processing genuinely required?
        |
       YES
        |
        └──→ Consider an RDD
```

This is not an absolute rule.

The important engineering principle is:

> RDD should be a deliberate abstraction choice rather than the automatic starting point for modern structured Data Engineering.

---

# 31. When Should You Use DataFrames?

DataFrames naturally fit workloads such as:

- ETL
- analytics
- filtering
- aggregations
- joins
- structured transformations
- Parquet processing
- lakehouse pipelines
- SQL-heavy workloads
- data-quality transformations
- batch data processing

The reason is structural alignment.

If the business requirement is naturally expressed in terms of:

```text
rows
columns
filters
expressions
aggregations
```

then the DataFrame abstraction communicates that intent directly.

---

# 32. RDD to DataFrame Conversion

RDDs can be converted to DataFrames when a structured representation becomes useful.

For suitable row-shaped data:

```python
df = rdd.toDF(["name", "age"])
```

Conceptually:

```text
RDD records
    ↓
introduce column structure
    ↓
DataFrame
    ↓
schema-aware processing
```

Conversion can be useful when:

- legacy RDD processing produces structured records
- downstream processing is naturally relational
- you want SQL/DataFrame APIs
- you want Spark to have more structural information

A conversion should have a reason.

Repeatedly switching between abstractions can make a pipeline harder to understand.

---

# 33. Explicit Schema During Conversion

For production-quality data, an explicit schema can be preferable to relying on inference.

For example:

```python
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    LongType,
)

schema = StructType([
    StructField("name", StringType(), True),
    StructField("age", LongType(), True),
])

df = spark.createDataFrame(
    [
        ("Alice", 30),
        ("Bob", 25),
    ],
    schema=schema,
)
```

The important idea is that a schema is an explicit contract about the structure of the DataFrame.

Detailed schema design and DataFrame APIs are covered in later topics.

---

# 34. DataFrame to RDD Conversion

A DataFrame can be exposed as an RDD:

```python
rdd = df.rdd
```

The resulting RDD contains Spark `Row` objects.

For example:

```python
rows_rdd = df.rdd

print(rows_rdd.take(2))
```

A conceptual result could look like:

```text
[Row(name='Alice', age=30),
 Row(name='Bob', age=25)]
```

This can be useful when a genuinely lower-level RDD operation is required.

However, repeatedly doing:

```text
DataFrame
   ↓
RDD
   ↓
DataFrame
   ↓
RDD
```

without a clear reason can reduce clarity and may introduce unnecessary conversion or Python-level processing.

---

# 35. The `collect()` Warning

These two operations both move all records to the driver:

```python
rdd.collect()
```

and:

```python
df.collect()
```

The danger is the same:

```text
Distributed dataset
       ↓
all records
       ↓
driver memory
```

Suppose a DataFrame contains 500 GB of data.

Calling:

```python
df.collect()
```

does not mean "show me a few records."

It requests the complete result at the driver.

That can overwhelm driver memory.

For inspection, use bounded operations such as:

```python
df.show(20)
```

or:

```python
df.take(20)
```

The exact safe method depends on the goal, but the principle is:

> Never assume that a distributed dataset can safely be materialized on the driver.

---

# 36. RDD and DataFrame Partitions

Both RDDs and DataFrames participate in partitioned distributed processing.

Conceptually:

```text
RDD / DataFrame
       |
       +---- Partition 1
       +---- Partition 2
       +---- Partition 3
       +---- Partition 4
```

Partitions are important because they provide units of parallel processing.

The distinction is:

```text
logical abstraction
        vs
physical partitioning
```

An RDD is a distributed collection abstraction.

A DataFrame is a structured distributed-data abstraction.

Both ultimately have distributed execution involving partitions.

Detailed partition sizing, `repartition()`, `coalesce()`, file sizing, and partition-aware performance belong to Topic 08.

---

# 37. RDD and DataFrame Lineage

RDD lineage can be visualized as:

```text
RDD 1
  ↓ map
RDD 2
  ↓ filter
RDD 3
```

A DataFrame pipeline can be viewed conceptually as:

```text
Input
  ↓
DataFrame transformations
  ↓
Structured execution representation
```

Both abstractions support lazy distributed computation.

The important distinction is that DataFrames provide structured information that can participate in Spark SQL's planning and optimization framework.

Do not interpret this as:

> "RDDs have no execution plan."

Spark still executes RDD transformations through its distributed execution engine.

The difference is in the amount and kind of structural information available for optimization.

---

# 38. Immutability Comparison

Both abstractions follow a transformation-oriented programming model.

RDD:

```python
rdd2 = rdd1.filter(lambda x: x > 10)
```

DataFrame:

```python
df2 = df1.filter(F.col("value") > 10)
```

Neither operation means:

```text
modify rdd1 in place
modify df1 in place
```

Instead:

```text
original
   ↓
transformation
   ↓
new logical result
```

This supports reasoning about pipelines and makes transformations composable.

---

# 39. Practical Project Example

Consider a production pipeline processing customer transactions stored in Parquet.

The requirements are:

```text
Read transaction data
      ↓
Filter invalid records
      ↓
Select required columns
      ↓
Calculate transaction value
      ↓
Aggregate by customer
      ↓
Write result
```

## RDD-style thinking

An RDD implementation could explicitly manipulate records:

```python
valid = transactions_rdd.filter(
    lambda row: row["amount"] >= 0
)

enriched = valid.map(
    lambda row: {
        "customer_id": row["customer_id"],
        "value": row["quantity"] * row["unit_price"],
    }
)
```

This is flexible, but the developer is expressing record-level logic in Python.

## DataFrame-style thinking

The same requirements naturally map to structured expressions:

```python
from pyspark.sql import functions as F

result = (
    transactions_df
    .filter(F.col("amount") >= 0)
    .select(
        "customer_id",
        "quantity",
        "unit_price",
    )
    .withColumn(
        "value",
        F.col("quantity") * F.col("unit_price"),
    )
    .groupBy("customer_id")
    .agg(
        F.sum("value").alias("total_value")
    )
)
```

The DataFrame version communicates:

```text
structured columns
        ↓
structured expressions
        ↓
structured aggregation
```

This is a natural fit for the workload.

The example is intentionally not a complete performance-tuning exercise. Joins, shuffle tuning, skew, caching, and other optimization topics come later.

---

# 40. Performance Reasoning

Avoid this statement:

> "DataFrames are always faster."

A more technically useful statement is:

> DataFrames provide Spark with structural information that can enable more optimization than arbitrary RDD transformations, especially when using Spark-native expressions.

Performance depends on factors including:

- workload
- data format
- Python execution
- serialization
- optimizer visibility
- built-in functions
- cluster resources
- data volume
- operation type

Therefore distinguish:

```text
potential optimization advantage
```

from:

```text
guaranteed performance
```

A poorly designed DataFrame pipeline can still perform badly.

A carefully designed RDD computation can be appropriate and effective for its intended workload.

Production engineering requires measurement rather than slogans.

---

# 41. Common Misconceptions

## Misconception 1: "RDD and DataFrame are completely different distributed systems."

### Correction

They are different Spark data abstractions within the same distributed Spark platform.

Both participate in Spark's distributed execution architecture.

---

## Misconception 2: "A DataFrame is just an RDD with column names."

### Correction

A DataFrame is a structured abstraction with schema and relational semantics. Its structure provides Spark with information that can participate in SQL planning and optimization.

---

## Misconception 3: "RDDs are deprecated and cannot be used."

### Correction

RDDs remain a valid Spark abstraction and can be appropriate for specialized lower-level processing and legacy applications.

The decision should depend on the workload.

---

## Misconception 4: "DataFrames are always faster."

### Correction

DataFrames can provide more optimization opportunities, but actual performance depends on workload, implementation, data source, execution strategy, resources, and other factors.

---

## Misconception 5: "DataFrames are not distributed."

### Correction

A DataFrame is distributed data organized into a structured logical representation. Its records can be processed across partitions and executors.

---

## Misconception 6: "`collect()` just displays the data."

### Correction

`collect()` materializes all returned records at the driver.

For large datasets, this can cause driver-memory exhaustion.

---

## Misconception 7: "Every Python transformation runs inside the Spark JVM."

### Correction

PySpark provides Python APIs, and arbitrary Python logic can execute in Python worker processes. Python/JVM and serialization boundaries can therefore matter.

---

## Misconception 8: "A DataFrame schema means the data is stored on one machine."

### Correction

Schema describes structure. It says nothing about the data being local to one machine.

A DataFrame can represent data distributed across many partitions and executors.

---

# 42. Hands-On Labs

## Lab 1 — Create an RDD

Create:

```python
rdd = spark.sparkContext.parallelize(
    [1, 2, 3, 4, 5]
)
```

Perform:

- `map`
- `filter`
- `count`
- `take`

Questions:

1. What does the RDD represent?
2. What are its records?
3. Why can the records be processed in parallel?

---

## Lab 2 — Create a DataFrame

Create:

```python
data = [
    ("Alice", 30),
    ("Bob", 25),
]

df = spark.createDataFrame(
    data,
    ["name", "age"],
)
```

Inspect:

```python
df.show()
df.printSchema()
```

Questions:

1. What are the columns?
2. What are the data types?
3. Why does the schema matter?

---

## Lab 3 — Same Problem with Both APIs

Filter records where age is greater than 30.

RDD:

```python
rdd_result = rdd.filter(
    lambda row: row["age"] > 30
)
```

DataFrame:

```python
df_result = df.filter(
    F.col("age") > 30
)
```

Compare:

- code readability
- structure
- optimizer visibility
- Python execution
- maintainability

---

## Lab 4 — RDD Word Count

Implement:

```text
flatMap
    ↓
map
    ↓
reduceByKey
```

Explain what each stage of the logical computation represents.

Do not optimize it yet.

---

## Lab 5 — Structured Word Count

Implement a DataFrame-based word count.

Compare the abstractions rather than only comparing line counts.

Answer:

> What information does the DataFrame representation communicate that the RDD representation does not?

---

## Lab 6 — RDD to DataFrame

Create structured RDD records and convert them:

```python
df = rdd.toDF(["name", "age"])
```

Inspect:

```python
df.printSchema()
```

Explain what structure has been introduced.

---

## Lab 7 — DataFrame to RDD

Convert:

```python
rdd = df.rdd
```

Inspect:

```python
rdd.take(5)
```

Explain the resulting `Row` representation.

Then answer:

> Why might you convert a DataFrame to an RDD?

---

## Lab 8 — Partition Awareness

Inspect the number of partitions using an appropriate API.

For an RDD:

```python
rdd.getNumPartitions()
```

Explain:

- what a partition is
- why partitions matter
- how partitions relate to tasks

Do not introduce advanced repartitioning techniques yet.

---

# 43. Predict → Run → Observe → Explain

Use the learning loop:

```text
Predict
   ↓
Run
   ↓
Observe
   ↓
Explain
   ↓
Compare RDD vs DataFrame
   ↓
Change one thing
   ↓
Run again
   ↓
Measure
```

For example, before running:

```python
df.filter(F.col("age") > 30)
```

predict:

- what records should remain
- what the resulting schema should be
- whether the original DataFrame changes

Then run it.

Finally explain *why* the result occurred.

The objective is not to memorize outputs.

The objective is to build a mental model of Spark's abstractions.

---

# 44. Production Decision Framework

Use the following questions.

| Question | RDD | DataFrame |
|---|---|---|
| Structured tabular data? | Possible | Natural fit |
| Schema-aware processing? | Manual | Native |
| SQL integration? | Limited | Strong |
| Arbitrary Python object logic? | Stronger fit | Less natural |
| Optimizer visibility? | Limited | Stronger |
| Typical ETL workload? | Possible | Natural fit |
| Specialized low-level algorithms? | Can fit | Depends on abstraction |

### Structured tabular data

If the workload is fundamentally rows and columns, DataFrames naturally communicate that structure.

### Schema-aware processing

DataFrames provide schema as a first-class concept.

RDD records can have structure by convention, but the RDD abstraction does not require a schema.

### SQL integration

DataFrames integrate naturally with Spark SQL.

### Arbitrary Python object logic

RDDs can represent arbitrary objects, making them useful for certain specialized computations.

### Optimizer visibility

DataFrames expose structured expressions and relational semantics that provide more information for Spark SQL's planning and optimization framework.

### Typical ETL

Structured ETL naturally maps to DataFrame operations.

### Specialized algorithms

The appropriate abstraction depends on the algorithm. Some lower-level distributed computations may fit RDD semantics more naturally.

---

# 45. Real-World Scenarios

## Scenario 1 — Structured Parquet ETL

A company processes Parquet customer data:

```text
filter
select
aggregate
write
```

Ask:

> Which abstraction naturally represents this workload, and why?

A strong answer should discuss:

- schema
- structured expressions
- maintainability
- optimizer visibility
- SQL/DataFrame interoperability

Do not justify the decision with only "DataFrames are faster."

---

## Scenario 2 — Custom Distributed Object Processing

A custom algorithm requires complex object-level distributed processing that does not naturally map to relational operations.

Ask:

> Why might an RDD be considered?

The reasoning should focus on abstraction fit rather than a blanket preference for RDDs.

---

## Scenario 3 — Legacy RDD Application

A team has an old Spark application written entirely with RDDs.

Ask:

> Should the team automatically rewrite everything?

No automatic answer follows from the abstraction alone.

Consider:

- business value
- correctness
- operational stability
- test coverage
- maintainability
- whether the workload is structured
- whether migration would provide meaningful benefits
- migration risk

A migration should have a technical reason.

---

## Scenario 4 — Unnecessary DataFrame-to-RDD Conversion

A developer converts a large DataFrame to an RDD only to perform a simple filter.

Discuss:

- loss of structured intent
- potential Python-level processing
- maintainability
- unnecessary abstraction switching
- whether the filter could be expressed with a DataFrame built-in

---

## Scenario 5 — Huge `collect()`

A developer writes:

```python
df.rdd.collect()
```

for a huge dataset.

Explain the execution risk.

The problem is not that the syntax is invalid.

The problem is:

```text
distributed result
       ↓
all records
       ↓
driver memory
```

This can cause driver-side memory exhaustion.

---

# 46. Migrating RDD Code to DataFrames

Consider:

```python
rdd.filter(
    lambda x: x["age"] > 30
)
```

A structurally equivalent DataFrame operation can be:

```python
df.filter(
    F.col("age") > 30
)
```

The DataFrame version can provide:

- clearer schema-aware intent
- relational semantics
- stronger optimizer visibility
- easier integration with SQL
- maintainable structured code

But do not assume every RDD operation has a trivial one-to-one DataFrame replacement.

Some algorithms genuinely require lower-level logic.

Migration is therefore an engineering exercise, not a mechanical syntax conversion.

---

# 47. Advanced Conceptual Comparison

## Abstraction Level

RDDs expose a lower-level distributed collection model.

DataFrames expose a higher-level structured data model.

## Schema

RDDs do not require a schema.

DataFrames are schema-aware.

## Type and Structure Information

RDDs can contain arbitrary objects.

DataFrames expose named columns and data types.

## Execution Optimization

RDD transformations expose less relational structure to Spark's SQL optimizer.

DataFrame expressions provide more structure that can be analyzed and optimized.

## Python Interaction

RDD transformations commonly expose Python-level record processing.

DataFrame built-in expressions can represent operations as Spark-native expressions.

## Serialization

Arbitrary Python objects can increase serialization concerns.

Structured execution can use more optimized internal representations.

## SQL Integration

RDDs have limited direct SQL integration.

DataFrames are a core Spark SQL abstraction.

## Fault Tolerance

Both participate in Spark's distributed fault-tolerance model.

RDD lineage is an explicit and foundational concept.

DataFrame computations are also represented through Spark's execution planning and distributed runtime.

## Lineage

RDDs have transformation lineage.

DataFrame pipelines also form a chain of logical transformations and execution planning.

## Partitioning

Both ultimately participate in partition-based distributed execution.

## Usability

RDDs provide lower-level control.

DataFrames provide a higher-level API aligned with structured processing.

## Maintainability

Structured workloads are often easier to communicate and maintain with DataFrames because the schema and relational intent are explicit.

## Production Use Cases

RDDs are useful for specialized or legacy lower-level distributed processing.

DataFrames naturally fit structured ETL, analytics, and SQL-oriented workloads.

---

# 48. What This Chapter Does Not Cover in Depth

This chapter establishes the abstraction boundary.

It does **not** deeply teach:

- transformations and actions as a standalone topic
- lazy evaluation in depth
- the complete DataFrame API
- Spark SQL in depth
- joins
- shuffle optimization
- broadcast joins
- repartition
- coalesce
- data skew
- salting
- caching
- persistence
- UDF performance
- Catalyst internals
- Adaptive Query Execution
- Spark UI
- advanced data sources
- advanced testing

Those topics belong to later files in Module 2.14.

They may be referenced briefly when needed to explain RDD/DataFrame differences.

---

# 49. Interview Preparation

## Basic

### 1. What is an RDD?

**Model answer:**  
An RDD, or Resilient Distributed Dataset, is an immutable distributed collection of records that Spark can process in parallel across partitions. Its lineage enables fault-tolerant recomputation of lost partitions.

### 2. Why is an RDD called resilient?

**Model answer:**  
Because Spark can use lineage and partition dependencies to recompute lost partitions after certain failures rather than requiring the complete dataset computation to restart.

### 3. What does distributed mean in RDD?

**Model answer:**  
The logical collection is divided into partitions that can be processed in parallel across executors.

### 4. What is a DataFrame?

**Model answer:**  
A Spark DataFrame is a distributed collection of data organized into named columns with a schema. It provides a higher-level structured abstraction that integrates with Spark SQL.

### 5. What is the main conceptual difference between an RDD and a DataFrame?

**Model answer:**  
An RDD is a lower-level distributed collection abstraction, while a DataFrame is a higher-level schema-aware structured-data abstraction.

---

## Intermediate

### 6. Why do DataFrames provide more optimization opportunities?

**Model answer:**  
DataFrames expose schema and structured expressions, giving Spark SQL's planning and optimization framework more information about the computation than arbitrary record-level Python functions provide.

### 7. Why can Python RDD operations have additional overhead?

**Model answer:**  
RDD transformations that execute arbitrary Python logic can involve Python worker execution and serialization/deserialization across Python/JVM-related boundaries. This can add CPU and memory overhead.

### 8. When might an RDD still be appropriate?

**Model answer:**  
For specialized lower-level distributed algorithms, arbitrary object-oriented processing, irregular data, or legacy applications where the RDD abstraction genuinely fits the workload.

### 9. Why is structured ETL naturally suited to DataFrames?

**Model answer:**  
Structured ETL is usually expressed as filters, projections, expressions, aggregations, and other relational operations. DataFrames represent these concepts directly and provide Spark with schema and structured execution information.

### 10. What does `df.rdd` do?

**Model answer:**  
It exposes the DataFrame as an RDD of Spark `Row` objects, allowing lower-level RDD processing when there is a legitimate reason to use it.

---

## Advanced

### 11. What happens conceptually when converting RDD → DataFrame?

**Model answer:**  
The records are represented through a structured DataFrame abstraction and associated schema. Spark can then reason about the data using structured column semantics and SQL/DataFrame planning.

### 12. Why can converting DataFrame → RDD change the engineering characteristics of a pipeline?

**Model answer:**  
It moves the code from a structured, schema-aware abstraction to a lower-level record-oriented abstraction. This can reduce structured optimizer visibility and can introduce more Python-level object processing.

### 13. Are RDDs unoptimized?

**Model answer:**  
No. Spark still executes RDD transformations through its distributed execution engine. The important distinction is that arbitrary RDD transformations expose less relational structure for Spark SQL's optimizer to analyze.

### 14. Are DataFrames always faster?

**Model answer:**  
No. DataFrames provide more optimization opportunities for structured workloads, but actual performance depends on the workload, implementation, data source, execution strategy, resources, and other factors.

---

## Production and Architecture

### 15. You inherit an RDD-based ETL pipeline. What do you investigate before migrating it?

**Model answer:**  
Investigate the workload shape, data structure, correctness, tests, operational behavior, performance bottlenecks, maintenance cost, and whether the logic can naturally be expressed with DataFrame/Spark SQL APIs. Migration should be justified by engineering value.

### 16. A DataFrame is converted to RDD to apply a simple filter. What would you question?

**Model answer:**  
I would ask why the filter cannot be expressed using a DataFrame built-in expression. If it can, the conversion may be unnecessary and can reduce structured execution advantages and clarity.

### 17. Why is `df.rdd.collect()` dangerous?

**Model answer:**  
Because it requests all DataFrame records through the RDD and brings them to the driver. For sufficiently large results, driver memory can be exhausted.

### 18. How would you explain the choice of DataFrame to an architecture review?

**Model answer:**  
I would justify it using workload structure, schema, relational semantics, maintainability, SQL interoperability, Python/JVM considerations, and optimization opportunities rather than claiming that DataFrames are universally faster.

---

# 50. Practice Questions

## Basic — 10 Questions

1. What does RDD stand for?
2. What does "distributed" mean in an RDD?
3. What does "resilient" mean?
4. What is a partition?
5. What does immutable mean?
6. What is RDD lineage?
7. What is a DataFrame?
8. What is a schema?
9. What is the difference between a row and a column?
10. Why is a Spark DataFrame still distributed even though it looks like a table?

---

## Moderate — 10 Questions

1. Explain the difference between `parallelize()` and `textFile()`.
2. What does `map()` do to an RDD?
3. What is a pair RDD?
4. Why might `reduceByKey()` require data movement?
5. How does a DataFrame represent structure?
6. Why does schema information matter?
7. Why can DataFrames provide more optimization opportunities?
8. What does `df.rdd` return conceptually?
9. Why should repeated RDD/DataFrame conversions be questioned?
10. Why is `collect()` different from simply displaying a small sample?

---

## Hard — 10 Questions

1. Explain why arbitrary Python RDD transformations can have serialization overhead.
2. Explain why DataFrame built-in expressions can provide Spark with more optimization information.
3. Why is "DataFrames are optimized RDDs" an inaccurate description?
4. Why are RDDs still useful even though DataFrames are commonly used for structured processing?
5. What engineering factors should influence an RDD-to-DataFrame migration?
6. How do schema and relational semantics affect maintainability?
7. Why can a DataFrame filter be structurally different from an RDD `filter(lambda ...)` even when they produce the same records?
8. Explain the difference between logical abstraction and physical partitioning.
9. Why does converting a DataFrame to an RDD potentially change Python execution characteristics?
10. Why should performance claims be tested against the actual workload?

---

## Advanced — 10 Questions

1. Explain the relationship among schema, structured expressions, logical planning, and optimization opportunities.
2. Compare RDD lineage with the structured execution representation of a DataFrame.
3. Explain how Python object processing can affect distributed execution.
4. Design a decision framework for choosing RDD vs DataFrame.
5. A 2 TB Parquet pipeline uses RDDs for filtering, projection, and aggregation. What would you investigate before recommending a migration?
6. A custom distributed algorithm manipulates complex Python objects that do not map naturally to relational operations. What factors would support considering RDDs?
7. Explain why DataFrame adoption should not be justified by the phrase "DataFrames are always faster."
8. Explain how `collect()` can turn a distributed computation into a driver-memory problem.
9. Explain the engineering risks of repeatedly switching between DataFrame and RDD representations.
10. Explain the production principle of choosing the highest-level Spark abstraction that naturally expresses the workload while preserving exceptions for genuinely specialized processing.

---

# 51. Final Architecture Exercise

## Scenario A — Structured Lakehouse Pipeline

A Data Engineering team receives large Parquet datasets containing structured customer and transaction records.

The pipeline performs:

```text
Read Parquet
    ↓
Filter invalid records
    ↓
Select required columns
    ↓
Derived calculations
    ↓
Aggregation
    ↓
Write to lakehouse
```

### Task

Decide whether the core processing should naturally be expressed with RDDs or DataFrames.

Justify the decision using:

- data structure
- schema
- optimizer visibility
- maintainability
- Python execution
- performance opportunities
- production complexity

### Reference reasoning

The workload is highly structured and naturally expresses relational operations over named columns. A DataFrame representation communicates that structure directly and provides Spark with more information for structured planning and optimization.

The reasoning should not be:

> "DataFrames are always faster."

A stronger explanation is:

> The DataFrame abstraction naturally represents the workload and exposes schema and structured expressions that can provide Spark with more optimization opportunities while improving maintainability and SQL interoperability.

---

## Scenario B — Specialized Object Processing

A research team develops a distributed algorithm that manipulates complex application objects and does not naturally map to relational operations.

### Task

Explain why an RDD may be considered.

### Reference reasoning

An RDD can represent arbitrary distributed records or objects and provides lower-level transformation semantics. If the algorithm genuinely requires this abstraction and cannot naturally be expressed through structured Spark APIs, an RDD may be a reasonable choice.

Again, the decision should be based on workload fit rather than an assumption that one abstraction always wins.

---

# 52. Knowledge Checkpoint

Before moving to Topic 04, explain these concepts without looking at the chapter.

## RDD

- What is an RDD?
- Why is it resilient?
- Why is it distributed?
- What is a dataset in this context?
- What is immutability?
- What is lineage?
- What is a partition?

## DataFrame

- What is a DataFrame?
- What is a schema?
- What are rows and columns?
- Why does structure matter?
- Why can a DataFrame participate in SQL planning?

## Comparison

- RDD vs DataFrame
- schema differences
- abstraction-level differences
- Python execution differences
- serialization implications
- optimizer visibility
- SQL integration
- maintainability

## Production

- When would you naturally use a DataFrame?
- When might an RDD be appropriate?
- Why should RDDs not automatically be treated as obsolete?
- Why should DataFrames not automatically be assumed to be faster?
- Why is unnecessary conversion between abstractions undesirable?
- Why is `collect()` dangerous for large results?

If you cannot explain these ideas in your own words, review this chapter before moving forward.

---

# 53. Final Summary

The fundamental distinction is:

```text
RDD
 ↓
Lower-level distributed collection
 ↓
Record/object-oriented distributed processing
```

versus:

```text
DataFrame
 ↓
Higher-level structured distributed data
 ↓
Schema + named columns + relational abstraction
 ↓
More information available for structured optimization
```

An RDD provides:

- distributed records
- partitions
- immutability
- lineage
- lower-level transformation control

A DataFrame provides:

- distributed structured data
- schema
- named columns
- Spark SQL integration
- structured expressions
- more opportunities for Spark to optimize structured workloads

The Python/JVM distinction is also important.

Arbitrary Python RDD operations can expose Python object and serialization overhead.

DataFrame built-in expressions can allow Spark to represent operations as Spark-native structured expressions rather than arbitrary Python record-processing functions.

The production principle is:

> Choose the highest-level Spark abstraction that naturally expresses the workload, while understanding the lower-level abstraction well enough to reason about legacy systems, specialized algorithms, and Spark internals.

This is a decision principle, not an absolute rule.

The objective is engineering judgment.

---

# 54. Glossary

## RDD

Resilient Distributed Dataset: Spark's lower-level immutable distributed collection abstraction.

## Resilient

Able to recover from certain failures through lineage-based recomputation.

## Distributed Dataset

A logical collection whose records are distributed across partitions for parallel processing.

## Partition

A unit of distributed data processing that can be assigned to a task.

## Lineage

The dependency history describing how a distributed dataset was derived.

## Immutable

Not modified in place by transformations; transformations produce new logical results.

## Transformation

An operation that describes a new distributed dataset from an existing one. Detailed execution behavior is covered in Topic 04.

## Action

An operation that requests a result from a distributed computation. Detailed behavior is covered in Topic 04.

## Pair RDD

An RDD whose records are key-value pairs, enabling key-oriented operations.

## DataFrame

A distributed collection of structured data organized into named columns with a schema.

## Schema

The structural description of DataFrame columns, including names and data types.

## Row

A logical record in structured DataFrame data. When exposed through `df.rdd`, rows are represented as Spark `Row` objects.

## Column

A named field in a DataFrame.

## Structured Data

Data whose organization and types are explicitly represented, such as named columns with a schema.

## Serialization

Converting an in-memory object into a representation suitable for transfer or storage.

## Deserialization

Reconstructing an object from its serialized representation.

## Python Worker

A Python process used by Spark for execution of Python-side operations.

## JVM

Java Virtual Machine. Apache Spark's core runtime is JVM-based.

## SparkContext

A lower-level Spark application entry point associated with distributed execution. In modern PySpark applications, it is normally accessed through `SparkSession`.

## SparkSession

The main entry point for modern PySpark DataFrame and Spark SQL work.

## Catalyst Optimizer

Spark SQL's framework for analyzing and optimizing structured query plans. This is introductory in this chapter and covered in depth later.

## Logical Plan

A representation of what a structured computation should accomplish, independent of the final physical execution strategy. This is introduced conceptually here.

## Driver

The process coordinating the Spark application.

## Executor

A process on a worker node that executes Spark tasks.

## Task

A unit of Spark work operating on a partition.

## Distributed Collection

A logical collection whose data is divided across partitions and processed in a distributed environment.

---

# 55. Topic Completion Standard

You should consider Topic 03 complete only when you can do all of the following:

- Explain RDD from first principles.
- Explain why RDDs are resilient.
- Explain why RDDs are distributed.
- Explain RDD immutability.
- Explain RDD lineage.
- Create an RDD in PySpark.
- Use basic RDD operations.
- Explain pair RDDs at a foundational level.
- Explain DataFrames from first principles.
- Explain schema, rows, and columns.
- Create and inspect a DataFrame.
- Explain why structured information matters.
- Explain the RDD/DataFrame abstraction difference.
- Explain Python/JVM and serialization considerations.
- Explain why DataFrames can provide more optimization opportunities.
- Convert between RDDs and DataFrames with a clear reason.
- Explain why `collect()` can be dangerous.
- Identify legitimate RDD use cases.
- Identify common DataFrame workloads.
- Compare the same problem using both abstractions.
- Defend an abstraction choice in a production architecture discussion.
- Explain why "DataFrames are always faster" is an inadequate engineering argument.

If you can do these things, you have the conceptual foundation required for Topic 04: **Transformations, Actions, and Lazy Evaluation**.
