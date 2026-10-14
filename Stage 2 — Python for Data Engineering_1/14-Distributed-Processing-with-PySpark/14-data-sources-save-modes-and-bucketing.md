# Data Sources, Save Modes, and Bucketing in PySpark

> **Module:** 2.14 — Distributed Processing with PySpark  
> **Phase:** E — Production I/O and Operations  
> **Topic:** 14 — Data Sources, Save Modes, and Bucketing  
> **Engineering focus:** correctness → reliability → performance → operational safety

Every Spark pipeline begins with a read and ends with a write. Production quality depends on much more than knowing the `spark.read` and `df.write` APIs. The engineer must understand schemas, malformed input, save semantics, partition layout, database load, object-storage behavior, catalog metadata, bucketing, small files, retries, and failure visibility.

The central production pipeline is:

```text
SOURCE
  ↓
READ
  ↓
SCHEMA
  ↓
VALIDATION
  ↓
TRANSFORMATION
  ↓
PARTITIONING
  ↓
WRITE
  ↓
STORAGE LAYOUT
  ↓
RELIABILITY
  ↓
DOWNSTREAM READ PERFORMANCE
```

This chapter teaches that complete path from first principles to production engineering.


## 1. Learning Objectives

By the end of this topic, you should be able to:

- Explain `DataFrameReader` and `DataFrameWriter`.
- Use `format`, `option`, `schema`, `load`, `save`, and convenience APIs.
- Read and write Parquet, ORC, JSON, CSV, text, and Avro.
- Choose explicit schemas for production inputs.
- Explain schema inference risks.
- Handle malformed records with `PERMISSIVE`, corrupt-record capture, `DROPMALFORMED`, and `FAILFAST`.
- Design quarantine flows for bad input.
- Explain `append`, `overwrite`, `ignore`, and `errorifexists`.
- Explain why overwrite is a destructive operation.
- Write partitioned data with `partitionBy`.
- Distinguish static and dynamic partition overwrite.
- Design idempotent partition replacement.
- Read PostgreSQL through JDBC.
- Parallelize JDBC reads using `partitionColumn`, `lowerBound`, `upperBound`, and `numPartitions`.
- Explain why JDBC bounds are partitioning inputs, not simply a `WHERE` filter.
- Use `fetchsize` thoughtfully.
- Understand JDBC filter pushdown and batched writes.
- Protect a production source database from excessive Spark concurrency.
- Explain S3A/object-storage access and credential-provider patterns.
- Explain output committers conceptually.
- Distinguish `save`, `saveAsTable`, and `insertInto`.
- Explain the Spark catalog and physical files versus table metadata.
- Explain bucketing, `bucketBy`, and `sortBy`.
- Explain conditions under which bucketed joins/aggregations may reduce shuffle.
- Explain bucket-count compatibility and cross-engine limitations.
- Diagnose the small-file problem and design compaction.
- Explain object-store atomicity limitations and why lakehouse table formats exist.
- Understand Spark 4 Python Data Source API awareness-level concepts without relying on unverified signatures.
- Design, debug, measure, and document production I/O patterns.

## 2. Why Spark I/O Matters in Production

A production Spark pipeline can be computationally correct and still be operationally wrong.

Examples:

- A CSV schema is inferred incorrectly and numeric values become strings.
- A retry appends the same day's data twice.
- Static overwrite removes partitions that should have remained untouched.
- A JDBC extraction launches hundreds of database connections and overloads PostgreSQL.
- A job succeeds but creates millions of tiny files.
- A plain object-store write fails halfway through and leaves output that a concurrent reader can observe.
- A bucketed table is assumed to eliminate shuffle, but the actual plan still contains an `Exchange`.
- A credential is committed to Git because a developer placed it in a Spark option.

Production I/O therefore has four dimensions:

| Dimension | Core question |
|---|---|
| Correctness | Did we read and write the intended data? |
| Reliability | What happens during retries, failures, and concurrency? |
| Performance | How many bytes, files, connections, and requests are involved? |
| Operability | Can engineers observe, debug, replay, and recover the pipeline? |

The correct mental model is not:

```text
read file → transform → write file
```

It is:

```text
external system
    ↓
controlled ingestion
    ↓
explicit contract
    ↓
validation/quarantine
    ↓
distributed transformation
    ↓
intentional physical layout
    ↓
safe write semantics
    ↓
observable downstream dataset
```

## 3. Mental Model: Spark Read → Transform → Write

A DataFrame represents a distributed dataset and its logical schema. Reading does not necessarily mean Spark immediately loads every byte into executor memory.

A simplified model is:

```text
spark.read
    ↓
DataFrameReader
    ↓
logical description of the source
    ↓
query planning
    ↓
tasks read source partitions
    ↓
DataFrame
```

Similarly:

```text
DataFrame
    ↓
DataFrameWriter
    ↓
planned write
    ↓
executor tasks
    ↓
output files / table data
```

Spark is lazy. A read transformation usually contributes to a plan; actual I/O occurs when an action requires execution.

This matters because:

- projection can reduce columns read,
- predicates can sometimes be pushed to the source,
- partition pruning can reduce storage partitions,
- the final number of output partitions influences output file count,
- write mode affects existing data,
- commit behavior affects what becomes visible.

A production engineer therefore asks:

1. What source is being accessed?
2. What schema is being enforced?
3. What filters and columns can be pushed?
4. How is input partitioned?
5. How many tasks/connections are created?
6. What files/tables are written?
7. What happens on retry or failure?
8. What will downstream readers see?

## 4. DataFrameReader Fundamentals

`DataFrameReader` is exposed through `spark.read`.

Mental model:

```text
SparkSession
    ↓
spark.read
    ↓
DataFrameReader
    ↓
format()
    ↓
option()
    ↓
schema()
    ↓
load()
    ↓
DataFrame
```

Example:

```python
df = (
    spark.read
        .format("parquet")
        .load("data/input")
)
```

### What each call means

- `format("parquet")`: selects the source implementation.
- `option(...)`: supplies source-specific or generic options.
- `schema(...)`: supplies the expected schema instead of relying entirely on inference.
- `load(...)`: identifies the source path/table/query according to the source.
- The returned object is a DataFrame.

Convenience APIs are often clearer:

```python
spark.read.parquet("data/input")
spark.read.csv("data/input.csv")
spark.read.json("data/input.json")
spark.read.text("data/input.txt")
```

Use the generic form when:

- multiple options are required,
- the format is selected dynamically,
- you want a consistent configuration pattern,
- you are building reusable ingestion code.

### Important internal idea

`DataFrameReader` describes how the source should be read. Spark later plans how executor tasks perform that read.

It is therefore not equivalent to:

```python
open("file")
```

in ordinary Python.

## 5. DataFrameWriter Fundamentals

`DataFrameWriter` is exposed from a DataFrame through `df.write`.

Mental model:

```text
DataFrame
    ↓
DataFrameWriter
    ↓
format()
    ↓
option()
    ↓
mode()
    ↓
partitionBy()
    ↓
save()
```

Example:

```python
(
    df.write
      .format("parquet")
      .mode("append")
      .save("data/output")
)
```

Spark generally writes multiple output files because the DataFrame is distributed.

If a DataFrame has many partitions, multiple executor tasks can write output concurrently:

```text
DataFrame
   |
   +-- partition 1 → part file
   +-- partition 2 → part file
   +-- partition 3 → part file
   +-- ...
```

Therefore:

> One DataFrame does not imply one output file.

The output file count is influenced by:

- input/output partitioning,
- repartitioning/coalescing,
- partitioned storage layout,
- task execution,
- file format and writer behavior.

Do not use `coalesce(1)` as a generic production solution to "make one file." It can create a single-task bottleneck and poor scalability.

## 6. `format`, `option`, `schema`, `load`, and `save`

### `format`

Selects the data source:

```python
spark.read.format("parquet")
spark.read.format("csv")
spark.read.format("jdbc")
```

### `option`

Configures source/sink behavior:

```python
(
    spark.read
        .format("csv")
        .option("header", "true")
        .option("delimiter", ",")
)
```

### `schema`

Supplies a known schema:

```python
reader = spark.read.schema(schema)
```

### `load`

Loads a source:

```python
df = reader.load(path)
```

### `save`

Writes a DataFrame:

```python
df.write.format("parquet").save(path)
```

These methods are building blocks. Production code should avoid scattering source-specific magic values throughout a pipeline. Configuration should be explicit, validated, and observable.

## 7. Parquet

Parquet is a columnar storage format widely used for analytics.

### Why columnar storage matters

If a query needs:

```text
customer_id
amount
```

but the dataset contains 80 columns, a columnar format can avoid reading irrelevant columns when the engine and storage path support projection pruning.

Important characteristics:

- columnar organization,
- embedded schema,
- compression,
- statistics useful for filtering,
- nested-data support,
- strong Spark interoperability.

Example:

```python
df = spark.read.parquet("s3a://lake/silver/orders")
df.write.mode("append").parquet("s3a://lake/gold/orders")
```

### Production strengths

Parquet is a strong general-purpose choice for:

- analytical datasets,
- Spark pipelines,
- column pruning,
- predicate pushdown,
- partitioned data lakes.

It is not a transaction protocol. A directory of Parquet files does not automatically provide database-like atomic table semantics.

## 8. ORC

ORC is also a columnar analytics format.

Conceptually it provides:

- columnar organization,
- compression,
- schema,
- statistics,
- predicate-related optimization opportunities.

Example:

```python
df = spark.read.orc("data/orders")
df.write.mode("overwrite").orc("data/orders_orc")
```

ORC and Parquet are both legitimate analytical formats. The appropriate choice depends on:

- ecosystem compatibility,
- existing platform standards,
- engine support,
- storage conventions,
- workload characteristics.

Do not claim that one format is universally faster.

## 9. JSON

JSON is useful when input is semi-structured or naturally represented as nested objects.

Example:

```python
df = (
    spark.read
        .option("multiLine", "true")
        .json("data/events.json")
)
```

JSON is convenient but generally has greater parsing and storage overhead than a compact columnar representation for repeated analytical processing.

Use JSON commonly for:

- raw API responses,
- semi-structured ingestion,
- external-system interchange,
- early landing zones.

A common production pattern is:

```text
JSON/API
  ↓
raw
  ↓
validated schema
  ↓
Parquet/columnar silver
```

Do not assume that raw JSON should remain the primary format for every downstream analytical workload.

## 10. CSV

CSV is common because it is simple and interoperable, but it has many ambiguities:

- delimiter,
- header presence,
- quoting,
- escaping,
- null representation,
- whitespace,
- embedded delimiters,
- malformed rows,
- type inference.

Example:

```python
df = (
    spark.read
        .option("header", "true")
        .option("inferSchema", "false")
        .csv("data/input.csv")
)
```

For production, prefer an explicit schema:

```python
df = (
    spark.read
        .schema(schema)
        .option("header", "true")
        .csv("data/input.csv")
)
```

CSV is often appropriate at ingestion boundaries, but it is usually less attractive as a long-lived analytical storage format than a columnar format such as Parquet.

## 11. Text

Text input is useful when each record is fundamentally a line or when the source has not yet been parsed.

Example:

```python
lines = spark.read.text("data/raw.log")
```

The resulting DataFrame commonly contains a string column named `value`.

Text is useful for:

- logs,
- raw line-oriented files,
- custom parsing,
- initial landing.

It does not provide the schema and columnar benefits of analytical formats.

A typical pipeline is:

```text
raw text
  ↓
parse
  ↓
validated structured DataFrame
  ↓
columnar storage
```

## 12. Avro

Avro is a row-oriented serialization format with schema support and is commonly used in event/data interchange systems.

In Spark, Avro support may require the appropriate Spark package/module for the installed distribution and version.

Conceptually:

```python
df = spark.read.format("avro").load("data/events")
df.write.format("avro").save("data/events_out")
```

Verify availability and package requirements against the installed Spark distribution.

### Avro versus Parquet

| Concern | Avro | Parquet |
|---|---|---|
| Organization | Row-oriented | Columnar |
| Typical strength | Serialization/interchange | Analytics |
| Schema | Yes | Yes |
| Column pruning | Not its primary strength | Strong |
| Common event use | Strong | Possible but less interchange-oriented |
| Analytical scans | Usually less ideal | Strong |

Neither format is universally superior; the data flow determines the choice.

## 13. Choosing a Data Format

| Format | Typical role | Strengths | Common cautions |
|---|---|---|---|
| Parquet | Analytics/storage | Columnar, compression, pruning | File/table reliability still matters |
| ORC | Analytics/storage | Columnar, compression | Ecosystem conventions |
| JSON | Raw/semi-structured | Flexible, human-readable | Parsing/storage overhead |
| CSV | Interchange/raw | Very portable | Ambiguous schema/escaping |
| Text | Raw/log ingestion | Simple | Requires parsing |
| Avro | Event/interchange | Schema-aware row serialization | Package/ecosystem requirements |

A production architecture may intentionally use several:

```text
API/CSV/JSON
     ↓
Raw
     ↓
Validation
     ↓
Parquet/ORC
     ↓
Analytics
```

Do not select a format solely because it is familiar.

## 14. Schema Inference vs Explicit Schema

Schema inference is convenient:

```python
df = (
    spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .csv(path)
)
```

But inference can be problematic when:

- files contain inconsistent values,
- the sample does not represent future data,
- a column changes from integer-like to string-like,
- nullability differs,
- vendor files drift,
- inference costs additional work.

Explicit schema makes the contract visible:

```python
df = (
    spark.read
        .schema(schema)
        .option("header", "true")
        .csv(path)
)
```

### Production principle

For important production interfaces:

> Prefer an explicit, reviewed schema or an explicit schema contract.

Inference can still be appropriate for exploration and controlled internal workflows.

## 15. Explicit Schemas in PySpark

Example:

```python
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    DoubleType,
)

schema = StructType([
    StructField("customer_id", StringType(), True),
    StructField("age", IntegerType(), True),
    StructField("amount", DoubleType(), True),
])

df = (
    spark.read
        .schema(schema)
        .option("header", "true")
        .csv("data/input.csv")
)
```

### Why the schema matters

It defines:

- column names,
- data types,
- nullability expectations.

Nested schemas can be explicit too:

```python
from pyspark.sql.types import ArrayType, MapType

nested_schema = StructType([
    StructField(
        "customer",
        StructType([
            StructField("id", StringType(), True),
            StructField("segment", StringType(), True),
        ]),
        True,
    ),
    StructField(
        "tags",
        ArrayType(StringType()),
        True,
    ),
])
```

Schema is not merely documentation. It affects parsing, downstream expressions, validation, and correctness.

## 16. Malformed Records and Bad Data

Malformed records happen at system boundaries.

Examples:

- `"abc"` where an integer is expected,
- invalid quoting in CSV,
- truncated JSON,
- invalid date representation,
- unexpected field structure.

The dangerous response is:

```text
bad row → silently disappear
```

A production pipeline needs an explicit policy:

```text
valid record → main dataset

invalid record → quarantine
                  or
                fail
                  or
            intentionally drop
```

The correct policy depends on the business contract.

The important engineering question is:

> Can the pipeline explain what happened to every rejected record?

## 17. PERMISSIVE

`PERMISSIVE` is designed to allow parsing to continue while capturing malformed information according to the source's supported corrupt-record behavior.

Conceptually:

```text
input
 ↓
parser
 ├── valid → typed columns
 └── malformed → corrupt-record representation
```

A production pattern should make the corrupt record observable.

For example, a CSV ingestion can configure a corrupt-record column where supported:

```python
df = (
    spark.read
        .schema(schema)
        .option("header", "true")
        .option("mode", "PERMISSIVE")
        .option("columnNameOfCorruptRecord", "_corrupt_record")
        .csv(path)
)
```

Verify exact behavior for the installed Spark version and format.

The key idea is not the option string. It is:

> **Preserve evidence of malformed input instead of silently losing it.**

## 18. Corrupt-Record Columns

A corrupt-record column provides a place to retain the raw malformed representation when the data source supports that mechanism.

Example:

```python
bad = df.filter(F.col("_corrupt_record").isNotNull())
good = df.filter(F.col("_corrupt_record").isNull())
```

Then:

```text
good
  ↓
main pipeline

bad
  ↓
quarantine
```

Preserve useful metadata where possible:

- ingestion timestamp,
- source file,
- batch/run ID,
- source system,
- error category,
- raw record.

A corrupt-record column should not become an excuse to accept arbitrary schema drift. It is an observability and recovery mechanism.

## 19. DROPMALFORMED

`DROPMALFORMED` intentionally drops malformed records for formats/options that support the mode.

Example:

```python
df = (
    spark.read
        .schema(schema)
        .option("mode", "DROPMALFORMED")
        .csv(path)
)
```

### Risk

If 1,000 records disappear and the pipeline reports success, the pipeline may be operationally incorrect.

Therefore, use dropping only when:

- the business policy explicitly allows it,
- the loss is measurable,
- the pipeline emits appropriate metrics/logs,
- investigation is possible.

A silent drop is not a quality strategy.

## 20. FAILFAST

`FAILFAST` tells the reader to fail when malformed input is encountered where supported.

Example:

```python
df = (
    spark.read
        .schema(schema)
        .option("mode", "FAILFAST")
        .csv(path)
)
```

Fail-fast is valuable when:

- the source contract is strict,
- malformed data must block publication,
- partial success would be worse than failure.

It can be inappropriate when:

- a small number of bad records should be quarantined,
- the business requires best-effort ingestion,
- the pipeline has a controlled error lane.

The correct policy is driven by the data contract.

## 21. Quarantine Patterns

A robust ingestion design can use:

```text
Raw Input
   ↓
Parse
   ├──────── valid ───────→ validated dataset
   │
   └──────── invalid ─────→ quarantine
                              ↓
                         investigation
                              ↓
                         remediation
```

A quarantine record should ideally preserve:

- raw payload,
- source path/file,
- ingestion timestamp,
- batch/run identifier,
- error classification,
- parser/schema version.

Connect this to Module 2.11: data validation, contracts, and quality. This chapter focuses on I/O behavior; the validation framework itself belongs to that earlier module.

## 22. Save Modes

Spark commonly exposes four save modes:

```text
append
overwrite
ignore
errorifexists
```

| Mode | If target exists | Typical use | Main risk |
|---|---|---|---|
| `append` | Add output | Incremental/event-style writes | Duplicates on retry |
| `overwrite` | Replace according to sink semantics | Deliberate replacement | Destructive scope |
| `ignore` | Do nothing | Write-if-absent patterns | Hides stale/existing state |
| `errorifexists` | Fail | Safety guard | Requires explicit lifecycle |

Save mode is a correctness decision, not merely an API preference.

## 23. APPEND

Example:

```python
df.write.mode("append").parquet(path)
```

Append is useful for genuinely additive workloads.

But consider:

```text
10:00 job writes day=2026-10-01
10:05 job fails after output
10:10 retry writes same day again
```

If the retry appends the same logical records, duplicates can result.

Therefore:

> Append is not automatically idempotent.

For partitioned batch processing, replacing the affected partition can be safer when the pipeline is designed around deterministic recomputation.

## 24. OVERWRITE

Example:

```python
df.write.mode("overwrite").parquet(path)
```

Overwrite is powerful and potentially destructive.

Risks include:

- replacing more data than intended,
- wiping unrelated partitions,
- exposing partial output depending on storage/committer behavior,
- concurrent readers observing unexpected states,
- failed jobs leaving operational recovery work.

Actual behavior depends on:

- data source,
- filesystem/object store,
- partition-overwrite configuration,
- committer,
- Spark version,
- table API.

Never reduce the rule to "overwrite deletes the old files." Production behavior is more nuanced.

Use overwrite only when its scope is explicit and tested.

## 25. IGNORE

Example:

```python
df.write.mode("ignore").parquet(path)
```

If the target already exists, Spark can skip the write according to the sink's semantics.

This can be useful for:

- initialization,
- write-if-absent workflows,
- immutable artifacts.

But it can hide an operational problem:

```text
Expected today's dataset
        ↓
Target already exists
        ↓
Write skipped
        ↓
Pipeline reports success
```

The existence of a target does not prove its contents are correct.

## 26. ERRORIFEXISTS

Example:

```python
df.write.mode("errorifexists").parquet(path)
```

Failing when the target already exists can be safer for workflows where replacement must be explicit.

Use it when:

- duplicate output should be considered an error,
- lifecycle is managed elsewhere,
- accidental replacement must be prevented.

`errorifexists` and `ignore` express different operational philosophies:

```text
ignore      → existing state is acceptable
errorifexists → existing state is exceptional
```

## 27. Why OVERWRITE Can Be Dangerous

Consider:

```text
sales/
  date=2026-09-28/
  date=2026-09-29/
  date=2026-09-30/
```

A daily job should replace only:

```text
date=2026-09-30
```

A careless full overwrite can replace the entire target.

Production questions:

1. What is the intended replacement scope?
2. Is the write partition-scoped?
3. What happens if the job fails halfway?
4. What happens if a reader is active?
5. What happens on retry?
6. What happens if two jobs overlap?

This is why dynamic partition overwrite and transactional table formats matter.

## 28. Partitioned Output with `partitionBy`

Example:

```python
(
    df.write
      .mode("append")
      .partitionBy("event_date")
      .parquet("data/events")
)
```

Conceptual layout:

```text
data/events/
  event_date=2026-09-30/
  event_date=2026-10-01/
  event_date=2026-10-02/
```

Partitioning can support partition pruning:

```text
query asks for event_date = 2026-10-01
                  ↓
read only relevant storage partitions
```

But partitioning has a cost.

A high-cardinality partition column can create:

- many directories,
- many small files,
- expensive listings,
- fragmented data.

Good partition columns usually have meaningful filtering value and manageable cardinality.

## 29. Static Partition Overwrite

Partition overwrite behavior must be understood carefully.

In a static-style overwrite, the partition specification/scope is interpreted before the write, and depending on the API and configuration, an overwrite can affect a broader target scope than the records produced by the current DataFrame.

The key risk is:

```text
intended:
replace one partition

actual:
replace a larger table/partition scope
```

Never assume the scope from the word "partition" alone.

Test the exact API, Spark version, catalog, data source, and `partitionOverwriteMode` behavior used in your application.

## 30. Dynamic Partition Overwrite

Dynamic partition overwrite is designed for partitioned writes where only partitions represented by the incoming data should be replaced.

A commonly used setting is:

```python
spark.conf.set(
    "spark.sql.sources.partitionOverwriteMode",
    "dynamic",
)
```

Then:

```python
(
    daily_df.write
        .mode("overwrite")
        .partitionBy("event_date")
        .parquet(path)
)
```

Suppose the target contains:

```text
date=2026-09-28
date=2026-09-29
date=2026-09-30
```

and the DataFrame contains only:

```text
date=2026-09-30
```

The intended dynamic behavior is to replace the output partition represented by the incoming data while leaving unrelated partitions untouched.

### Important limitation

Dynamic partition overwrite does **not** automatically make the entire pipeline idempotent.

You still need:

- deterministic source extraction,
- deterministic transformations,
- correct partition keys,
- controlled retries,
- correct handling of concurrent writers,
- validation,
- appropriate table/write semantics.

Verify exact behavior for your Spark version and sink.

## 31. Idempotent Partition Writes

An idempotent daily load aims for:

```text
Run day=2026-10-01
        ↓
logical result R

Run same day again
        ↓
logical result R
```

A common design is:

```text
read source for target partition
        ↓
deterministic transform
        ↓
replace target partition
```

rather than:

```text
append every retry
```

### Example

```python
spark.conf.set(
    "spark.sql.sources.partitionOverwriteMode",
    "dynamic",
)

(
    daily_result
        .write
        .mode("overwrite")
        .partitionBy("event_date")
        .parquet(output_path)
)
```

Test idempotency explicitly:

```text
first run
↓
record counts

second run
↓
record counts

compare:
- row count
- keys
- aggregates
- partition contents
```

Connect this to Module 2.12 transformation/pipeline design and Module 2.13 orchestration/retries.

## 32. JDBC Data Sources

JDBC is a production boundary between Spark and a database.

Mental model:

```text
Spark executors
      ↓
JDBC connections
      ↓
PostgreSQL
```

The database is not a passive file. It is a live system with:

- CPU,
- memory,
- storage,
- locks,
- connection limits,
- query concurrency,
- operational users.

A Spark job can therefore harm the source database if parallelism is uncontrolled.

A basic read:

```python
jdbc_url = "jdbc:postgresql://db.example.internal:5432/analytics"

df = (
    spark.read
        .format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", "public.orders")
        .option("user", "${DB_USER}")
        .option("password", "${DB_PASSWORD}")
        .option("driver", "org.postgresql.Driver")
        .load()
)
```

Use a secret-management or environment mechanism in real deployments. Do not place real credentials in source code.

## 33. JDBC Parallel Reads

A single JDBC partition can create a bottleneck:

```text
Spark
  ↓
one connection
  ↓
PostgreSQL
```

Parallel JDBC reads can create:

```text
Executor 1 → connection → DB
Executor 2 → connection → DB
Executor 3 → connection → DB
...
```

The relevant options include:

- `partitionColumn`
- `lowerBound`
- `upperBound`
- `numPartitions`

Example:

```python
df = (
    spark.read
        .format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", "public.orders")
        .option("user", db_user)
        .option("password", db_password)
        .option("driver", "org.postgresql.Driver")
        .option("partitionColumn", "order_id")
        .option("lowerBound", "1")
        .option("upperBound", "50000000")
        .option("numPartitions", "16")
        .load()
)
```

The important production principle is:

> Spark parallelism becomes database concurrency.

Sixteen partitions can mean substantially more simultaneous source work than one partition.

## 34. JDBC Partitioning Parameters

### `partitionColumn`

Identifies a column Spark can use to divide the JDBC read.

### `lowerBound` and `upperBound`

These help define the partitioning range.

**Critical point:** they should not be misunderstood as a simple filter guaranteeing that only values between the two bounds are read.

They are used to construct parallel read partitions according to Spark's JDBC behavior.

### `numPartitions`

Controls the maximum partitioning parallelism used for the JDBC read and therefore can influence connection concurrency.

### Small numerical example

Suppose:

```text
partitionColumn = order_id
lowerBound = 1
upperBound = 1,000
numPartitions = 4
```

Conceptually Spark can divide the numeric range into several partitions. The exact predicate construction and handling of boundary/out-of-range values are Spark JDBC implementation details; verify the installed version.

### Production warning

If the database can safely support only a few concurrent reads, do not choose `numPartitions=100` simply because Spark has 100 executor slots.

## 35. JDBC Filter Pushdown

A filter can sometimes be pushed to the database:

```text
Spark filter
    ↓
Can source execute it?
    ↓
Database applies predicate
    ↓
Less data transferred to Spark
```

Example:

```python
orders = (
    spark.read
        .format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", "public.orders")
        .option("user", db_user)
        .option("password", db_password)
        .load()
)

recent = orders.filter(F.col("order_date") >= F.lit("2026-10-01"))
```

When pushdown is possible, the database can do work closer to the data.

Benefits can include:

- less network transfer,
- less Spark-side processing,
- less executor input.

Pushdown is not guaranteed for every expression. It depends on:

- JDBC source,
- database capabilities,
- expression,
- query shape,
- Spark version.

Connect this to Topic 12's predicate-pushdown concepts without re-teaching Catalyst.

## 36. JDBC Fetch Size

`fetchsize` influences how rows are fetched from the database through JDBC.

Example:

```python
df = (
    spark.read
        .format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", "public.orders")
        .option("fetchsize", "10000")
        .load()
)
```

Conceptually it affects the trade-off among:

- round trips,
- driver/database buffering,
- network efficiency,
- memory consumption.

There is no universal best value.

A safe tuning process is:

```text
baseline
→ measure
→ change fetch size
→ measure
→ inspect source DB
→ validate memory/network behavior
```

## 37. JDBC Batched Writes

A JDBC write can be parallelized by DataFrame partitions.

Example:

```python
(
    df.write
      .format("jdbc")
      .option("url", jdbc_url)
      .option("dbtable", "public.fact_orders")
      .option("user", db_user)
      .option("password", db_password)
      .option("driver", "org.postgresql.Driver")
      .option("batchsize", "1000")
      .mode("append")
      .save()
)
```

Production concerns:

- batch size,
- number of Spark partitions,
- number of database connections,
- transaction behavior,
- unique constraints,
- retries,
- duplicate writes,
- database locks,
- target indexes.

A failed Spark task may be retried. Therefore, JDBC writes must be designed with retry semantics in mind.

## 38. Protecting the Source Database

Spark parallelism is not free when the source is a database.

Consider:

```text
Spark executors
      ↓
100 JDBC connections
      ↓
PostgreSQL
```

The database may experience:

- CPU pressure,
- I/O pressure,
- lock contention,
- connection exhaustion,
- cache pressure,
- query queueing,
- network saturation.

### Protection strategies

- Bound `numPartitions`.
- Use source-appropriate indexes.
- Prefer incremental extraction.
- Use watermarks where appropriate.
- Extract during controlled windows.
- Use read replicas where architecture permits.
- Monitor source CPU/I/O/connections.
- Avoid full-table extraction when unnecessary.
- Coordinate with database owners.
- Measure before increasing concurrency.

The correct question is:

> "How much parallelism can the source safely sustain?"

not:

> "How much parallelism can Spark generate?"

## 39. Object Storage and S3A

Conceptual path:

```text
Spark
  ↓
S3A connector
  ↓
Object storage
```

S3A is Spark/Hadoop's S3-compatible filesystem connector path.

Object storage differs from a traditional local filesystem in important ways:

- network-based access,
- object-oriented semantics,
- request-oriented operations,
- different consistency/visibility considerations depending on system,
- different commit strategies,
- different performance characteristics.

For Spark I/O, think about:

- file size,
- request count,
- listing,
- parallelism,
- serialization/compression,
- commit/finalization behavior.

Do not turn this topic into a complete AWS course. The focus is Spark I/O engineering.

## 40. S3A Credentials and Credential Providers

Never put secrets directly into source code:

```python
# BAD
access_key = "real-secret"
secret_key = "real-secret"
```

Instead use:

- environment-based credentials where appropriate,
- workload/instance identity,
- IAM-style roles,
- secret managers,
- credential providers supported by the deployment.

Principles:

1. Never commit credentials to Git.
2. Use least privilege.
3. Avoid printing secrets in logs.
4. Prefer workload identity over long-lived static keys.
5. Rotate credentials through the organization's secret-management process.
6. Separate development and production permissions.

S3A configuration is deployment-specific. Verify supported credential-provider behavior against the Hadoop/Spark distribution you are running.

## 41. S3A Performance Considerations

Important factors include:

### Network throughput

Executors depend on network access to object storage.

### Request overhead

Millions of small files can generate large request overhead.

### File sizes

Very tiny files are inefficient for analytical scans.

### Multipart upload

Large writes may use multipart upload mechanisms supported by the storage connector.

### Listing

Large object prefixes can make listing/metadata operations expensive.

### Compression

Compression reduces bytes transferred/stored but adds CPU work.

### Parallelism

Too little parallelism underutilizes the cluster; too much can create request pressure.

There are no universal performance numbers. Measure in your environment.

## 42. Output Committers

An output committer coordinates task output and finalization.

Conceptually:

```text
Task attempt
    ↓
writes candidate output
    ↓
task success
    ↓
commit/finalization
    ↓
output becomes visible according to the environment
```

Why is this necessary?

Because tasks can:

- fail,
- retry,
- run speculatively,
- produce temporary/candidate output.

The system must distinguish successful task output from failed attempts.

Object storage can require different commit strategies than a traditional filesystem.

Do not assume all storage systems use identical commit semantics.

The correct production question is:

> "What does this Spark version + connector + storage system guarantee about output visibility and commit behavior?"

## 43. `save` vs `saveAsTable` vs `insertInto`

| API | Primary abstraction | Typical concern |
|---|---|---|
| `save()` | File-oriented sink | Path and file layout |
| `saveAsTable()` | Table/catalog-oriented sink | Table metadata and lifecycle |
| `insertInto()` | Existing table insertion | Existing schema/partition/table semantics |

### `save()`

```python
df.write.mode("append").parquet(path)
```

File-oriented.

### `saveAsTable()`

```python
(
    df.write
      .format("parquet")
      .mode("overwrite")
      .saveAsTable("analytics.orders")
)
```

Creates/writes through a catalog table abstraction according to the environment.

### `insertInto()`

```python
df.write.insertInto("analytics.orders")
```

This targets an existing table and therefore depends strongly on the table's metadata/schema/partitioning semantics.

Do not assume all three APIs have identical schema matching, overwrite, or catalog behavior. Verify the actual table and Spark version.

## 44. Spark Catalog Fundamentals

A catalog connects logical table names to metadata and underlying data.

Conceptual model:

```text
Catalog
  ↓
Namespace/database
  ↓
Table
  ↓
Metadata
  ↓
Underlying data
```

A physical directory:

```text
s3a://lake/orders/
```

is not the same concept as a logical table:

```text
analytics.orders
```

The catalog can describe:

- table name,
- schema,
- location,
- partitioning,
- provider,
- metadata.

A data engineer needs to understand both:

```text
physical storage
```

and:

```text
logical table metadata
```

This chapter does not deep-dive into lakehouse catalog systems; that belongs to later modules.

## 45. Bucketing Fundamentals

Bucketing deliberately organizes table rows into a fixed number of buckets based on one or more keys.

Mental model:

```text
Input data
    ↓
bucket key
    ↓
hash/partition into fixed buckets
    ↓
optional sorting within buckets
    ↓
persist as table
```

Why do this?

Because repeated workloads may repeatedly join or aggregate on the same key.

If two compatible tables have matching bucket organization, Spark may be able to avoid or reduce some future shuffle work.

Bucketing is therefore a **physical design choice**.

It is not merely another filtering mechanism.

## 46. `bucketBy`

Example:

```python
(
    df.write
      .bucketBy(16, "customer_id")
      .sortBy("customer_id")
      .saveAsTable("analytics.bucketed_customers")
)
```

Conceptually:

- `16` = bucket count,
- `customer_id` = bucket key,
- `sortBy` = ordering inside buckets,
- `saveAsTable` = table-oriented persistence.

Important:

> Verify the actual behavior for your Spark version, catalog, provider, and storage configuration.

Do not assume this code has identical physical behavior across every Spark environment.

## 47. `sortBy`

`sortBy` can order records within buckets:

```python
(
    df.write
      .bucketBy(16, "customer_id")
      .sortBy("customer_id")
      .saveAsTable("analytics.bucketed_customers")
)
```

Bucketing and sorting solve different problems:

```text
Bucketing → which bucket receives the row
Sorting   → order of rows within a bucket
```

Sorting can help downstream processing that benefits from ordered data, but it adds write-time work.

## 48. Bucketed Tables with `saveAsTable`

Bucketing is traditionally associated with table-oriented writes.

A production design should document:

- bucket count,
- bucket key,
- sorting columns,
- table provider,
- catalog,
- Spark version,
- intended consumers.

Do not treat a bucketed table as a self-documenting optimization.

The physical contract must be understood by future maintainers.

## 49. How Bucketing Can Reduce Future Shuffle

Suppose two large tables are both bucketed compatibly on:

```text
customer_id
```

A future join:

```python
a.join(b, "customer_id")
```

may be able to exploit that existing physical organization.

Conceptually:

```text
Unbucketed:

A ──shuffle──┐
             ├── join
B ──shuffle──┘
```

Potentially compatible bucketed layout:

```text
A bucket 0 ─┐
B bucket 0 ─┤
A bucket 1 ─┼─ join by matching buckets
B bucket 1 ─┤
...
```

But do not promise a shuffle-free join.

The actual plan depends on:

- matching bucket keys,
- compatible bucket counts,
- table metadata,
- join expression,
- optimizer behavior,
- Spark version,
- statistics,
- other plan requirements.

Always verify:

```python
joined.explain("formatted")
```

## 50. Bucketing and Aggregations

Bucketing can also be useful for repeated aggregations on the bucket key.

Conceptually:

```text
bucketed table
      ↓
groupBy(customer_id)
      ↓
existing distribution may reduce redistribution
```

But again:

> Do not guarantee a shuffle-free aggregation.

The optimizer may still introduce an `Exchange` for correctness or other physical reasons.

Use the plan as evidence:

```python
(
    bucketed_df
      .groupBy("customer_id")
      .count()
      .explain("formatted")
)
```

## 51. Bucket Count and Compatibility

Bucket count is part of the physical contract.

Too few buckets can mean:

- large buckets,
- insufficient parallelism,
- less granular work distribution.

Too many buckets can mean:

- many files,
- metadata overhead,
- small files,
- maintenance cost.

For compatible bucketed joins, matching bucket metadata matters.

A table with:

```text
16 buckets
```

and another with:

```text
32 buckets
```

should not be assumed to have equivalent physical organization.

The appropriate bucket count depends on:

- data volume,
- key distribution,
- cluster size,
- query patterns,
- downstream joins,
- storage layout.

## 52. Limitations of Bucketing

Major limitations include:

- It is a physical design choice with maintenance cost.
- Compatibility matters.
- Cross-engine support is not universal.
- Bucket counts can become poorly matched to future workloads.
- It does not solve arbitrary skew.
- It does not replace partition pruning.
- It does not automatically improve every query.
- It may not be respected in every context.
- It is not equivalent to partitioning.
- Actual plan behavior must be verified.

Bucketing should be adopted because repeated workloads justify the physical organization—not because it sounds advanced.

## 53. Bucketing vs Partitioning

| Dimension | Partitioning | Bucketing |
|---|---|---|
| Physical organization | Directory/storage partitions | Fixed buckets |
| Typical purpose | Partition pruning | Join/aggregation optimization |
| Cardinality | Usually relatively low | Explicit fixed bucket count |
| Filtering | Strong use case | Not primary purpose |
| Join optimization | Indirect | Potentially strong |
| Storage layout | Partition directories | Bucketed table files/metadata |
| Main design question | Which partitions should be skipped? | Which keys should share physical distribution? |

They can be combined where appropriate:

```text
partition by event_date
bucket by customer_id
```

But every physical-layout dimension increases operational complexity. Use it intentionally.

## 54. Small-File Problem

Spark can create too many files because of:

- too many input/output partitions,
- tiny input partitions,
- frequent incremental writes,
- high-cardinality `partitionBy`,
- repeated append jobs,
- excessive bucket counts.

Example:

```text
one day
  ↓
50,000 tiny files
```

Downstream consequences:

- metadata/listing overhead,
- many file-open operations,
- more tasks,
- object-store request overhead,
- inefficient scans,
- higher scheduling overhead.

The small-file problem is often a **write-layout problem**, not a compute problem.

## 55. Output Compaction

Compaction reduces many small files into fewer appropriately sized files.

Conceptually:

```text
many small files
       ↓
read
       ↓
repartition/coalesce intentionally
       ↓
write fewer files
```

Example:

```python
(
    spark.read.parquet(input_path)
      .repartition(64)
      .write
      .mode("overwrite")
      .parquet(compacted_path)
)
```

The number `64` is an experiment, not a universal recommendation.

Avoid:

```python
df.coalesce(1)
```

as a generic compaction strategy.

It can force work through one partition and become a bottleneck.

Compaction should consider:

- target file size,
- partition boundaries,
- workload,
- cluster capacity,
- storage request overhead,
- future query patterns.

## 56. Object-Store Atomicity Limitations

A directory of object-store files is not automatically equivalent to a transactional database table.

Failure scenarios can include:

```text
Task 1 writes output
Task 2 writes output
Task 3 fails
Job fails
```

A reader may encounter state that is not the logical dataset the application intended, depending on the storage and commit protocol.

Other concerns:

- concurrent readers,
- concurrent writers,
- retries,
- partial outputs,
- stale metadata,
- failed cleanup.

The distinction is:

```text
object storage
    ≠
transactional table protocol
```

Object storage is excellent durable storage. Transactional semantics require additional metadata and commit layers.

## 57. Why Lakehouse Table Formats Exist

Plain files eventually raise requirements such as:

- atomic commits,
- snapshot isolation,
- concurrent readers,
- concurrent writers,
- schema evolution,
- deletes/updates,
- reliable table metadata.

This motivates lakehouse table formats.

Conceptually:

```text
Plain files
    ↓
reliability limitations
    ↓
metadata + transaction requirements
    ↓
lakehouse table format
```

This chapter intentionally does not deep-dive into Delta, Iceberg, or Hudi. That belongs to the next module.

The important lesson is:

> A file format answers how data is encoded; a table format can additionally define how a dataset is managed as a reliable table.

## 58. Spark 4 Python Data Source API

Modern Spark releases include Python-facing data-source capabilities.

At an awareness level, understand that a custom Python data source can provide a way to integrate Python-defined source logic with Spark's data-source architecture.

Potential conceptual use case:

```text
Mock API
   ↓
custom Python data-source logic
   ↓
Spark DataFrame
   ↓
distributed transformation
```

Use cases may include:

- controlled mock sources,
- specialized integrations,
- custom ingestion prototypes.

### Version warning

Python Data Source APIs are version-sensitive.

Do not copy an API signature from an old tutorial without checking:

```python
print(spark.version)
```

Verify the exact API, interfaces, capabilities, and packaging requirements against the installed Spark version and official documentation.

This chapter deliberately keeps this topic at awareness level rather than pretending to be a complete custom-data-source course.

## 59. Production I/O Design Patterns

### Pattern A — Raw landing

```text
external source
    ↓
raw immutable-ish landing
    ↓
validation
    ↓
quarantine
    ↓
validated data
```

### Pattern B — Idempotent daily partition

```text
source for day
    ↓
deterministic transformation
    ↓
replace only target partition
```

### Pattern C — Database extraction

```text
PostgreSQL
    ↓
bounded JDBC concurrency
    ↓
Spark
    ↓
partitioned Parquet
```

### Pattern D — Small-file control

```text
incremental data
    ↓
controlled output partitioning
    ↓
periodic compaction
    ↓
healthy file layout
```

### Pattern E — Repeated large joins

```text
stable workload
    ↓
evaluate bucketing
    ↓
write compatible tables
    ↓
verify physical plan
```

### Pattern F — Strong transactional requirement

```text
plain files
    ↓
identify reliability limitation
    ↓
adopt appropriate table format
```

The correct pattern depends on the workload and failure model.

## 60. Hands-On Labs

Each lab follows:

```text
Read
↓
Understand
↓
Predict
↓
Write PySpark
↓
Run small
↓
Inspect output/schema/plan
↓
Introduce failure
↓
Debug
↓
Measure
↓
Compare
↓
Document
↓
Explain aloud
```

### Lab 1 — Parquet Read/Write

**Objective:** Read and write a Parquet dataset.

**Setup:**

```python
df = spark.range(1000)

path = "/tmp/io_lab_parquet"

df.write.mode("overwrite").parquet(path)
loaded = spark.read.parquet(path)

print(loaded.schema)
print(loaded.count())
```

**Inspect:** schema, output files, partitions, plan.

**Production lesson:** file writes are distributed and create multiple files.

### Lab 2 — CSV with Explicit Schema

Build a CSV dataset and read it using a `StructType`.

Record differences between inference and explicit schema.

### Lab 3 — Nested JSON

Create/read nested JSON and inspect:

```python
df.printSchema()
```

Compare JSON convenience with downstream columnar storage.

### Lab 4 — Malformed Records

Create valid and malformed CSV records.

Test:

- `PERMISSIVE`,
- corrupt-record capture,
- `DROPMALFORMED`,
- `FAILFAST`.

Document which records reach the main output and which reach quarantine.

### Lab 5 — Save-Mode Comparison

Run the same daily dataset multiple times with:

```text
append
overwrite
ignore
errorifexists
```

Record row counts and target contents after each run.

### Lab 6 — Partitioned Output

Write:

```python
df.write.partitionBy("event_date").parquet(path)
```

Inspect the directory layout and query a single date.

### Lab 7 — Dynamic Partition Overwrite

Create three date partitions. Rewrite only one partition using dynamic overwrite.

Run twice and verify logical idempotency.

### Lab 8 — Idempotent Daily Load

Implement:

```text
source day
→ transform
→ target partition replacement
```

Run it twice and compare keys/aggregates.

### Lab 9 — JDBC Basic Read

Read PostgreSQL using JDBC with credentials supplied outside source code.

Inspect the resulting plan.

### Lab 10 — JDBC 1 vs 16

Run a controlled comparison using:

```text
numPartitions = 1
numPartitions = 16
```

Record:

- runtime,
- source connections,
- source CPU/I/O,
- Spark tasks,
- network.

Do not assume 16 is better.

### Lab 11 — JDBC Filter Pushdown

Read a large table, apply a selective filter, and inspect whether the source can execute the predicate.

### Lab 12 — JDBC Batched Write

Write a controlled DataFrame to PostgreSQL.

Experiment with partition count and batch size while monitoring the database.

### Lab 13 — S3A/MinIO

Using the provided local MinIO environment, configure S3A access without hard-coded credentials.

Read/write a small Parquet dataset.

### Lab 14 — `save` vs `saveAsTable`

Write the same logical data as:

- file output,
- catalog table.

Inspect the difference between path and metadata.

### Lab 15 — Bucketed Table

Create a bucketed table:

```python
(
    df.write
      .bucketBy(16, "customer_id")
      .sortBy("customer_id")
      .saveAsTable("lab_bucketed_customers")
)
```

Verify actual behavior in your Spark environment.

### Lab 16 — Bucketed Join

Create two compatible bucketed tables and join them.

Inspect:

```python
joined.explain("formatted")
```

Do not assume the shuffle disappears; prove it.

### Lab 17 — Small-File Generation

Intentionally create many small output files.

Measure:

- file count,
- scan behavior,
- task count.

### Lab 18 — Compaction

Compact the small files using an intentional partition count.

Compare before/after layout and scan behavior.

### Lab 19 — Output Failure Simulation

Interrupt a write in a controlled local/test environment.

Inspect output and document what a reader might observe.

### Lab 20 — Plan Inspection

For all major I/O experiments, capture:

```python
df.explain("formatted")
```

and, when useful:

```python
df.explain("extended")
```

Record:

- scans,
- filters,
- partition filters,
- exchanges,
- joins,
- bucket-related behavior.

## 61. Debugging Exercises

### Exercise 1 — CSV Schema Inferred Incorrectly

**Symptom:** `customer_id` became an integer in one batch and string-like in another.

**Investigation:** inspect schema and source values.

**Fix:** define an explicit schema and enforce the contract.

**Prevention:** schema validation and drift monitoring.

### Exercise 2 — Malformed Rows Disappear

**Symptom:** source has 1,000,000 rows; output has fewer with no error.

**Investigation:** inspect reader mode and corrupt-record handling.

**Fix:** use intentional quarantine/failure policy.

**Prevention:** rejected-record metrics.

### Exercise 3 — Append Duplicates After Retry

**Symptom:** daily partition contains duplicates after a retry.

**Investigation:** inspect run IDs and write mode.

**Fix:** deterministic partition replacement or another idempotent strategy.

**Prevention:** retry-safe design.

### Exercise 4 — Overwrite Removes Unrelated Partitions

**Symptom:** historical dates disappeared.

**Investigation:** inspect write mode and partition-overwrite configuration.

**Fix:** scope the replacement correctly.

**Prevention:** automated partition-preservation tests.

### Exercise 5 — Dynamic Overwrite Replaces Wrong Partitions

**Symptom:** more partitions changed than expected.

**Investigation:** inspect distinct partition values in the output DataFrame and configuration.

**Fix:** validate the output partition set before writing.

**Prevention:** pre-write assertions.

### Exercise 6 — JDBC Overloads PostgreSQL

**Symptom:** source DB CPU and connections spike.

**Investigation:** inspect `numPartitions`, concurrent jobs, and database metrics.

**Fix:** reduce/bound concurrency, improve extraction strategy.

**Prevention:** source capacity budget.

### Exercise 7 — JDBC 16 Partitions Slower Than One

**Symptom:** higher parallelism increases runtime.

**Investigation:** source contention, indexes, connection overhead, network, query plan.

**Fix:** choose concurrency based on measured source capacity.

**Prevention:** repeatable extraction benchmarks.

### Exercise 8 — JDBC Pushdown Missing

**Symptom:** Spark reads far more data than expected.

**Investigation:** inspect source query behavior and supported expressions.

**Fix:** reshape filter if appropriate and verify database/source support.

**Prevention:** plan/source-query inspection.

### Exercise 9 — Credentials in Code

**Symptom:** access key appears in a repository.

**Investigation:** assume exposure and follow incident/rotation procedures.

**Fix:** move to supported credential-provider/identity mechanisms.

**Prevention:** secret scanning and least privilege.

### Exercise 10 — Millions of Small Files

**Symptom:** output scan is slow despite modest total data volume.

**Investigation:** file count, partition cardinality, task count.

**Fix:** correct output partitioning and compact.

**Prevention:** file-count monitoring.

### Exercise 11 — Bucketed Join Still Shuffles

**Symptom:** `Exchange` remains in the plan.

**Investigation:** bucket keys/counts, table metadata, join expression, optimizer behavior.

**Fix:** determine whether the physical contract is actually compatible.

**Prevention:** plan verification after table creation.

### Exercise 12 — Poor Compaction

**Symptom:** compaction creates either one huge file or thousands of tiny files.

**Investigation:** partition count and data volume.

**Fix:** choose a measured target parallelism/file size.

**Prevention:** monitor file-size distribution.

### Exercise 13 — Concurrent Reader Sees Incomplete Output

**Symptom:** reader observes unexpected intermediate files/state.

**Investigation:** storage system and committer semantics.

**Fix:** use appropriate commit/table semantics.

**Prevention:** transactional table format when required.

### Exercise 14 — `insertInto` Schema Assumption

**Symptom:** data lands in the wrong columns or fails due to table expectations.

**Investigation:** inspect target table schema/partition metadata and write semantics.

**Fix:** align the DataFrame/table contract explicitly.

**Prevention:** schema assertions and integration tests.

## 62. Production Scenarios

### Scenario 1 — Daily Sales Ingestion

**Business context:** daily sales arrive from PostgreSQL.

**Problem:** the job must be rerunnable.

**Design considerations:** bounded JDBC concurrency, explicit schema, deterministic transformations, partitioned Parquet, dynamic partition overwrite.

**Validation:** run the same day twice and compare logical output.

### Scenario 2 — Retry Creates Duplicates

**Context:** orchestration retries after executor failure.

**Problem:** append duplicates data.

**Investigation:** run ID, write mode, partition contents.

**Solution options:** deterministic replacement, staging, transactional table format.

**Trade-off:** replacement is safer for deterministic partitions but depends on correct partition scope.

### Scenario 3 — Monthly Backfill

**Context:** one month of historical data must be recomputed.

**Problem:** avoid destroying unrelated months.

**Design:** partition-scoped processing and carefully tested overwrite semantics.

**Validation:** snapshot partition inventory before/after.

### Scenario 4 — PostgreSQL Extraction

**Context:** 50-million-row source.

**Problem:** extraction takes too long.

**Options:** JDBC parallel reads, incremental extraction, indexes, read replica.

**Constraint:** database capacity.

**Validation:** compare one versus controlled parallelism while monitoring PostgreSQL.

### Scenario 5 — Database Overload

**Context:** Spark extraction causes production DB latency.

**Root cause:** Spark concurrency exceeds source capacity.

**Solution:** reduce partitions, schedule extraction, use replicas, incremental extraction.

**Trade-off:** lower Spark parallelism may increase elapsed time but protect the source.

### Scenario 6 — S3 Millions of Small Files

**Context:** hourly ingestion creates thousands of files.

**Problem:** downstream scans slow down.

**Solution:** control output partitioning and compact.

**Validation:** file-count and file-size distributions.

### Scenario 7 — Repeated Customer Joins

**Context:** two large stable datasets repeatedly join on `customer_id`.

**Option:** evaluate compatible bucketing.

**Validation:** inspect actual plans and benchmark representative joins.

**Caution:** bucketing is a physical design commitment and has maintenance cost.

### Scenario 8 — Failed Object-Store Write

**Context:** job fails during output.

**Problem:** concurrent readers must not consume incomplete logical data.

**Investigation:** connector/committer behavior.

**Solution options:** stronger commit/table semantics.

### Scenario 9 — Vendor Corrupt CSV

**Context:** vendor sends malformed records.

**Policy options:** fail-fast, quarantine, or intentional dropping with metrics.

**Decision:** business data contract.

### Scenario 10 — Migration Toward Lakehouse Tables

**Context:** plain Parquet has growing concurrency and reliability requirements.

**Trigger:** atomicity, snapshots, schema evolution, concurrent writes.

**Next step:** evaluate an appropriate table format in Topic 15.

## 63. Common Misconceptions

1. **"Append is automatically idempotent."**  
   Append can duplicate data on retry. Idempotency requires a deterministic replacement/deduplication strategy.

2. **"Overwrite is always safe."**  
   Overwrite is potentially destructive and its scope depends on the API/configuration/storage semantics.

3. **"More JDBC partitions are always faster."**  
   More connections can overload the source database.

4. **"`lowerBound`/`upperBound` are simple filters."**  
   They are inputs to JDBC partitioning behavior, not a promise that only those values are read.

5. **"`partitionBy` makes every query faster."**  
   It helps queries that can prune useful partitions; it can hurt through high cardinality and small files.

6. **"Every column should be a partition column."**  
   High-cardinality partitioning can create unusable storage layouts.

7. **"Bucketing is the same as partitioning."**  
   They create different physical organizations for different optimization goals.

8. **"Bucketing always removes shuffle."**  
   The actual plan may still require an exchange.

9. **"More buckets are always better."**  
   Too many buckets can create excessive files and metadata.

10. **"Bucketing works identically across all engines."**  
    Cross-engine support and semantics are not universal.

11. **"S3 is a filesystem."**  
    Object storage has different operational semantics from a traditional filesystem.

12. **"Putting AWS keys in code is acceptable."**  
    Credentials belong in supported identity/secret mechanisms.

13. **"`saveAsTable` and `save` are the same."**  
    One is table/catalog-oriented; the other is file-oriented.

14. **"`insertInto` always matches columns by name."**  
    Existing table semantics must be understood and verified; do not assume identical behavior to a name-based schema merge.

15. **"A successful Spark job guarantees atomic table visibility."**  
    Plain file writes do not automatically provide transactional table semantics.

16. **"`coalesce(1)` is the correct way to compact."**  
    It can create a single-task bottleneck.

17. **"CSV is as reliable as Parquet for analytics."**  
    CSV has more ambiguity and parsing overhead and lacks the same columnar characteristics.

18. **"Schema inference is always safe."**  
    Inference can be unstable or expensive at production boundaries.

19. **"`DROPMALFORMED` is harmless."**  
    Dropped records can silently create correctness gaps.

20. **"`FAILFAST` is always better."**  
    Failure policy depends on the data contract and operational requirements.

21. **"Dynamic partition overwrite makes the whole pipeline idempotent."**  
    It only addresses part of the write behavior.

22. **"Object storage provides database transactions automatically."**  
    Transactional table semantics require additional mechanisms.

23. **"Committers are irrelevant."**  
    Commit behavior influences how task output becomes final output.

24. **"A bucketed table automatically produces a shuffle-free join."**  
    Compatibility and optimizer behavior must be verified.

25. **"Lakehouse formats are just another file format."**  
    They address table-level metadata and transactional/reliability semantics beyond encoding.

26. **"A table name is the same thing as a directory."**  
    Catalog metadata and physical storage are distinct concepts.

27. **"If the write succeeded, the data must be correct."**  
    Successful execution is not proof of semantic correctness.

28. **"JDBC is just another file source."**  
    A database is a live shared system with resource limits and concurrency concerns.

## 64. Practice Questions

### Basic — 1–10

1. What is `DataFrameReader`, and how is it accessed in PySpark?
2. What is the difference between `load()` and `save()`?
3. Name the four common Spark save modes.
4. Why is Parquet commonly used for analytical storage?
5. Why are explicit schemas valuable in production ingestion?
6. What does `partitionBy()` do conceptually?
7. What problem does a corrupt-record column solve?
8. What is JDBC?
9. What is the purpose of a Spark catalog?
10. What is bucketing?

### Moderate — 11–20

11. Explain why `append` can produce duplicates after a retry.
12. Compare `PERMISSIVE`, `DROPMALFORMED`, and `FAILFAST`.
13. Explain static versus dynamic partition overwrite.
14. Explain why high-cardinality `partitionBy` can create a small-file problem.
15. Explain `partitionColumn`, `lowerBound`, `upperBound`, and `numPartitions` in a JDBC read.
16. Why can 16 JDBC partitions be slower than one?
17. What is filter pushdown in JDBC?
18. Compare `save()`, `saveAsTable()`, and `insertInto()`.
19. Explain the difference between partitioning and bucketing.
20. Why must a bucketed join be verified with the physical plan?

### Hard — 21–30

21. Design a retry-safe daily partitioned Parquet load.
22. A CSV source changes a numeric column to a string in one batch. How would you diagnose and prevent the problem?
23. A PostgreSQL source becomes overloaded when Spark extracts data. Build an investigation and remediation plan.
24. Explain why JDBC `lowerBound`/`upperBound` should not be treated as simple filters.
25. Design a quarantine strategy for malformed vendor CSV files.
26. A job overwrites all historical partitions when only today's partition should change. What would you inspect?
27. Two large tables repeatedly join on `customer_id`. When would you investigate bucketing?
28. A bucketed join still contains an `Exchange`. List possible causes.
29. A successful object-store write leaves unexpected intermediate files after failure. Explain how you would investigate.
30. Design a compaction strategy that avoids both millions of small files and a single-task bottleneck.

### Advanced — 31–40

31. Design a PostgreSQL → Spark → S3/Parquet architecture that protects the source database.
32. Explain how save mode, partition overwrite, retry semantics, and idempotency interact.
33. A daily pipeline has 100 partitions and 10 million rows per day. Explain how you would choose a partitioning strategy without assuming a universal file size.
34. Design an experiment comparing one and 16 JDBC partitions while controlling for database load and Spark variability.
35. Explain how bucketing can reduce future shuffle and why it still cannot be assumed to eliminate `Exchange`.
36. Explain the operational difference between a directory of Parquet files and a transactional table format.
37. Design a migration plan from plain Parquet to a table format when concurrent readers and atomic commits become requirements.
38. A Spark job has excellent compute utilization but downstream scans are slow. Explain how file count and layout could be responsible.
39. Design a production I/O standard covering schema, bad records, save modes, JDBC, object storage, file layout, and observability.
40. Given a failed production write, explain how you would reason from business correctness backward through Spark execution, commit behavior, storage layout, and downstream visibility.

## 65. Interview Questions

### Basic — 1–10

1. What is `DataFrameReader`?
2. What is `DataFrameWriter`?
3. What is Parquet?
4. Why would you use an explicit schema?
5. What are Spark save modes?
6. What is `partitionBy()`?
7. What is JDBC?
8. What is S3A?
9. What is a Spark catalog?
10. What is bucketing?

### Moderate — 11–20

11. Why is overwrite dangerous?
12. How does dynamic partition overwrite help daily pipelines?
13. How would you handle malformed records?
14. Why can `append` create duplicate data?
15. How do you parallelize a JDBC read?
16. What does `fetchsize` influence?
17. How do you protect a PostgreSQL source from Spark?
18. What is the difference between `saveAsTable` and `save`?
19. What is an output committer?
20. What is the small-file problem?

### Hard — 21–30

21. A Spark job is creating too many JDBC connections. How do you diagnose it?
22. Why might increasing JDBC `numPartitions` make a pipeline worse?
23. How would you prove that dynamic partition overwrite is replacing only intended partitions?
24. How would you design malformed-record quarantine?
25. When would you use bucketing instead of only partitioning?
26. Why might a bucketed join still shuffle?
27. How would you investigate an S3A write that leaves unexpected output after failure?
28. What metrics would you monitor for small-file problems?
29. Why is `coalesce(1)` usually a poor production compaction strategy?
30. How do object-store semantics affect Spark output reliability?

### Advanced — 31–40

31. Design a production PostgreSQL-to-S3 Spark ingestion architecture and defend its JDBC parallelism.
32. How would you make a daily partition pipeline safe to retry?
33. A source schema is unstable. How would you balance explicit contracts with controlled schema evolution?
34. Explain how catalog metadata changes the meaning of a physical data directory.
35. How would you evaluate whether bucketing is worth its write and maintenance cost?
36. A team claims that bucketed tables eliminate shuffle. How would you challenge and test the claim?
37. How would you design output semantics for concurrent readers during Spark failures?
38. How would you decide whether plain Parquet is sufficient or a transactional table format is required?
39. How would you audit a Spark I/O platform for credential, database-load, file-layout, and retry risks?
40. Describe how you would establish an organization-wide Spark I/O standard without assuming that one configuration fits every workload.

## 66. Architecture Questions

### Scenario 1 — PostgreSQL → S3 Daily Pipeline

**Requirements:** daily incremental extraction, analytics-ready Parquet, retries.

**Constraints:** PostgreSQL is production-critical.

**Design:** bounded JDBC parallelism, incremental predicate, explicit schema, partitioned output, idempotent partition replacement.

**Failure modes:** source outage, Spark retry, duplicate output, partial write.

**Validation:** row counts, business keys, partition inventory, source DB metrics.

### Scenario 2 — Retry Creates Duplicates

**Requirements:** retry-safe daily job.

**Options:** deterministic partition replacement, staging/deduplication, transactional table format.

**Trade-off:** complexity versus correctness guarantees.

### Scenario 3 — Millions of Tiny Files

**Requirements:** preserve incremental ingestion.

**Options:** controlled output partitioning, periodic compaction, table-format optimization later.

**Validation:** file count and file-size distribution.

### Scenario 4 — PostgreSQL Overload

**Requirements:** reduce extraction time without harming source.

**Options:** bounded concurrency, indexing, read replica, incremental extraction.

**Decision process:** source capacity first, Spark speed second.

### Scenario 5 — Safe Daily Replacement

**Requirements:** replace only one date partition.

**Options:** dynamic partition overwrite or transactional table semantics.

**Validation:** assert expected output partition set before write.

### Scenario 6 — Repeated Large Customer Joins

**Requirements:** stable repeated joins on the same key.

**Option:** evaluate compatible bucketing.

**Validation:** actual plan, repeated workload benchmark, write/storage cost.

### Scenario 7 — Concurrent Reader Consistency

**Requirements:** readers must not observe invalid intermediate table state.

**Problem:** plain files do not automatically provide transaction semantics.

**Decision:** evaluate table format/commit architecture.

### Scenario 8 — Transactional Requirement

**Requirements:** atomic commits, snapshots, concurrent writers.

**Conclusion:** plain file output may no longer be sufficient; evaluate lakehouse table formats in the next module.

### Scenario 9 — Vendor Bad Data

**Requirements:** preserve valid data while investigating malformed records.

**Design:** permissive parsing + quarantine + metrics.

### Scenario 10 — Bucketed Analytics Platform

**Requirements:** repeated large joins/aggregations.

**Decision process:** determine whether workload stability justifies bucket maintenance.

**Validation:** actual plan and representative workload measurements.

## 67. Production Checklist

### Read correctness

- [ ] Source format explicitly identified.
- [ ] Explicit schema used where appropriate.
- [ ] Schema drift policy documented.
- [ ] Malformed-record policy documented.
- [ ] Quarantine path/strategy defined.
- [ ] Rejected-record metrics available.

### Save correctness

- [ ] Save mode deliberately selected.
- [ ] Overwrite scope understood.
- [ ] Partition overwrite behavior tested.
- [ ] Retry behavior tested.
- [ ] Idempotency demonstrated.

### JDBC

- [ ] Source capacity documented.
- [ ] `numPartitions` bounded.
- [ ] `partitionColumn` appropriate.
- [ ] Bounds understood.
- [ ] Fetch size tested.
- [ ] Pushdown verified where relevant.
- [ ] Database monitoring enabled.
- [ ] Credentials not in code.

### Object storage

- [ ] S3A configuration uses supported credential-provider mechanisms.
- [ ] No static secrets in Git.
- [ ] File count monitored.
- [ ] File-size distribution monitored.
- [ ] Commit behavior understood.
- [ ] Failure visibility tested.

### Tables/catalog

- [ ] Physical path and logical table understood.
- [ ] `save`, `saveAsTable`, and `insertInto` semantics documented.
- [ ] Table schema validated.
- [ ] Partition metadata validated.

### Bucketing

- [ ] Workload justifies bucketing.
- [ ] Bucket key is stable.
- [ ] Bucket count is intentional.
- [ ] Compatibility requirements documented.
- [ ] Actual physical plans verified.
- [ ] Cross-engine assumptions documented.

### Reliability

- [ ] Retry tested.
- [ ] Partial failure tested.
- [ ] Concurrent-reader behavior tested.
- [ ] Recovery procedure documented.

### Security

- [ ] Secrets externalized.
- [ ] Least privilege applied.
- [ ] Logs do not expose credentials.
- [ ] Encryption requirements understood.

## 68. Learning Checkpoints

### Checkpoint 1 — Data Sources

You can:

- Explain `DataFrameReader`.
- Explain `DataFrameWriter`.
- Read/write common formats.
- Choose explicit schemas.

### Checkpoint 2 — Reliability

You can:

- Explain save modes.
- Explain overwrite risks.
- Handle malformed records.
- Design quarantine.

### Checkpoint 3 — Partitioned Writes

You can:

- Explain `partitionBy`.
- Explain static overwrite.
- Explain dynamic overwrite.
- Design an idempotent partition load.

### Checkpoint 4 — JDBC

You can:

- Read PostgreSQL.
- Parallelize reads.
- Explain JDBC partitioning.
- Protect the source DB.

### Checkpoint 5 — Object Storage

You can:

- Explain S3A.
- Use credential-provider concepts.
- Explain committers.
- Explain small-file risks.

### Checkpoint 6 — Bucketing

You can:

- Explain `bucketBy`.
- Explain `sortBy`.
- Explain bucketed joins.
- Explain bucket limitations.

### Checkpoint 7 — Production I/O

You can:

- Design a reliable Spark I/O architecture.
- Identify failure modes.
- Explain when plain files are insufficient.

## 69. Final Assessment

## Part A — Theory

Answer without notes:

1. Explain the complete Spark I/O lifecycle.
2. Compare Parquet, ORC, JSON, CSV, text, and Avro.
3. Explain explicit schema versus inference.
4. Compare all four save modes.
5. Explain static versus dynamic partition overwrite.
6. Explain JDBC parallel reads.
7. Explain S3A credential-provider principles.
8. Explain `save`, `saveAsTable`, and `insertInto`.
9. Explain bucketing and its limitations.
10. Explain object-store atomicity limitations.

## Part B — Code

Write working code for:

1. Explicit-schema CSV ingestion.
2. Malformed-record handling.
3. Partitioned Parquet write.
4. Dynamic partition overwrite.
5. JDBC parallel read.
6. Bucketed table.

The code should:

- avoid hard-coded credentials,
- document assumptions,
- inspect schemas,
- inspect plans where relevant.

## Part C — Debugging

A production pipeline has all of these symptoms:

- duplicates after retry,
- malformed rows disappearing,
- PostgreSQL connection spikes,
- millions of small files,
- bucketed join still shuffling.

Diagnose each issue using:

```text
symptom
→ evidence
→ root-cause hypotheses
→ controlled experiment
→ fix
→ prevention
```

## Part D — Architecture

Design:

```text
PostgreSQL
    ↓
Spark
    ↓
S3/MinIO
    ↓
Partitioned Parquet
    ↓
Analytics
```

Then answer:

> How would the architecture change if strong transactional table semantics, concurrent readers, concurrent writers, and atomic commits became mandatory?

The expected direction is to evaluate a lakehouse table format rather than pretending plain file output provides database-like transactions.

## 70. Glossary

**DataFrameReader** — Spark API used to describe how a DataFrame should be read from a data source.

**DataFrameWriter** — Spark API used to describe how a DataFrame should be written.

**Data source** — System or format from which Spark reads data.

**Data sink** — Destination to which Spark writes data.

**Parquet** — Columnar storage format commonly used for analytics.

**ORC** — Columnar storage format used for analytical workloads.

**JSON** — Semi-structured text representation commonly used for interchange and raw ingestion.

**CSV** — Delimited text format with potential ambiguity around schema, quoting, and malformed records.

**Text** — Line-oriented raw input representation.

**Avro** — Schema-aware row-oriented serialization format.

**Schema** — Structure describing columns, data types, and nullability.

**Schema inference** — Deriving a schema from input data.

**Explicit schema** — Schema supplied by the application.

**Corrupt record** — Input record that cannot be parsed according to the expected schema/format.

**PERMISSIVE** — Parsing mode that allows supported malformed input to be represented rather than immediately failing.

**DROPMALFORMED** — Parsing mode that discards malformed records where supported.

**FAILFAST** — Parsing mode that fails when malformed input is encountered where supported.

**Quarantine** — Controlled storage/location for rejected or malformed records.

**Append** — Write mode that adds output to an existing target.

**Overwrite** — Write mode that replaces output according to the sink/configuration semantics.

**Ignore** — Write mode that can skip an existing target.

**ErrorIfExists** — Write mode that fails when the target already exists.

**Partitioning** — Organizing data into distinct physical partitions to support parallelism and/or pruning.

**PartitionBy** — Writer API used to organize output using partition columns.

**Dynamic partition overwrite** — Overwrite behavior where partitions represented by the incoming output are replaced rather than blindly replacing unrelated partitions, subject to Spark/sink semantics.

**Idempotency** — Property that repeating the same logical operation produces the same logical result.

**JDBC** — Java Database Connectivity interface used to connect Spark with relational databases.

**PartitionColumn** — JDBC column used to divide a source read into parallel partitions.

**FetchSize** — JDBC fetch configuration influencing how rows are retrieved from the database.

**Pushdown** — Executing supported filtering/projection work closer to the data source.

**S3A** — Hadoop/Spark connector path used for S3-compatible object storage.

**Credential provider** — Mechanism that supplies credentials to a connector without embedding secrets directly in application code.

**Output committer** — Mechanism coordinating task output and finalization/commit behavior.

**Catalog** — Metadata system through which Spark can resolve logical databases/namespaces/tables.

**`save`** — File-oriented DataFrame write operation.

**`saveAsTable`** — Table/catalog-oriented DataFrame write operation.

**`insertInto`** — Operation that inserts into an existing catalog table.

**Bucketing** — Fixed physical organization of table data by one or more bucket keys.

**`bucketBy`** — Writer operation specifying bucket count and bucket columns for a bucketed table.

**`sortBy`** — Writer operation specifying sorting within buckets.

**Bucket count** — Number of buckets in a bucketed table's physical organization.

**Small-file problem** — Performance/operational problem caused by excessive numbers of tiny files.

**Compaction** — Rewriting many small files into fewer appropriately sized files.

**Object storage** — Storage system organized around objects rather than traditional filesystem blocks/directories.

**Atomicity** — Property that a logical operation becomes visible as an all-or-nothing unit.

**Lakehouse table format** — Table-management layer that adds capabilities such as transactional commits, snapshots, schema evolution, and table metadata on top of data files.

## 71. Cross-Module Connections

### Module 2.5 — Data Formats, Compression and File Layout

Connect:

- Parquet,
- file size,
- compression,
- partitioning,
- small files,
- compaction.

Do not re-teach Module 2.5; use it to reason about I/O layout.

### Module 2.7 — Python Database Connectivity

Connect:

- JDBC,
- connections,
- fetching,
- transactions,
- source protection.

### Module 2.8 — Data Modelling for Analytics

Connect:

- star schemas,
- fact/dimension layout,
- repeated join keys,
- bucketing decisions.

### Module 2.11 — Data Validation, Contracts and Quality

Connect:

- bad records,
- quarantine,
- schema enforcement.

### Module 2.12 — Transformation Patterns and Pipeline Design

Connect:

- idempotency,
- partition overwrite,
- incremental processing.

### Module 2.13 — Orchestration

Connect:

- retries,
- backfills,
- partition-level execution.

### Topics 07–13

Connect:

- joins,
- shuffle,
- partitioning,
- skew,
- AQE,
- Catalyst,
- explain plans.

The purpose here is integration, not re-teaching previous chapters.

## 72. Forward Connection to Lakehouse Table Formats

This topic naturally leads to the next module:

```text
Plain files
    ↓
file-based reliability limitations
    ↓
metadata + transaction requirements
    ↓
lakehouse table formats
```

You should now understand why a directory of Parquet files is not necessarily a reliable table abstraction for workloads requiring:

- atomic commits,
- snapshots,
- concurrent writers,
- concurrent readers,
- schema evolution,
- deletes/updates.

Topic 15 will build on this motivation.

## 73. Plan Inspection

For performance-related examples, use:

```python
df.explain("formatted")
```

and where useful:

```python
df.explain("extended")
```

Inspect:

- file scans,
- filters,
- partition filters,
- exchanges,
- joins,
- bucket-related behavior,
- shuffle,
- stage boundaries.

Plan output can vary with:

- Spark version,
- catalog,
- data source,
- statistics,
- configuration.

Never fabricate exact plan output in documentation.

## 74. Spark 4 Version Awareness

Start experiments with:

```python
print(spark.version)
```

Rules:

- Prefer APIs applicable to the installed version.
- Verify configuration names.
- Verify Python Data Source API signatures.
- Do not blindly copy Spark 3 tutorials.
- Flag version-sensitive behavior.
- Treat the installed Spark runtime as the authority for experiments.

When behavior differs by release, explicitly say:

> **Verify against the installed Spark version.**

## 75. No Fabricated Benchmarks

Never claim:

```text
16 JDBC partitions are 5× faster.
Parquet is exactly X% faster than CSV.
Bucketing eliminates Y% of shuffle.
```

unless the number was generated by an actual controlled experiment.

Instead document:

- workload,
- Spark version,
- cluster,
- source system,
- configuration,
- measurement procedure,
- repeated results,
- interpretation.

Production engineering is evidence-driven.

## 76. Security

Spark I/O security focuses on the boundary between the processing engine and external systems.

### Database credentials

Use:

- environment/secret mechanisms,
- managed identities,
- secret managers,
- deployment-specific credential providers.

### S3/object storage

Prefer:

- workload/instance identity,
- role-based access,
- short-lived credentials,
- least privilege.

### Secrets

Never:

- commit secrets to Git,
- print credentials in logs,
- place secrets in notebook cells that become shared artifacts,
- embed long-lived access keys in source.

### Encryption

Understand:

- encryption in transit,
- encryption at rest,
- database TLS,
- object-storage encryption requirements.

This is an I/O-focused security treatment, not a complete security course.

## 77. Performance Engineering

### Read performance

Focus on:

- column pruning,
- predicate pushdown,
- partition pruning,
- file format,
- file count,
- file size.

### JDBC performance

Focus on:

- bounded parallel reads,
- fetch size,
- pushdown,
- source database capacity,
- network,
- indexing.

### Write performance

Focus on:

- partition count,
- file sizes,
- compression,
- small files,
- object-store request overhead.

### Bucketing

Evaluate:

- repeated joins,
- repeated aggregations,
- compatible bucket metadata,
- actual plan behavior.

### Measurement discipline

Record:

```text
Spark version
dataset
cluster
storage
configuration
runtime
task count
file count
file-size distribution
source DB load
shuffle metrics where relevant
```

Never optimize solely from intuition.

## 78. Reliability Engineering

A successful Spark job is not automatically a correct pipeline.

Reliability requires:

- idempotency,
- retry safety,
- intentional save modes,
- correct partition overwrite,
- partial-failure handling,
- concurrent-reader reasoning,
- concurrent-writer reasoning,
- source-failure handling,
- target-failure handling,
- corrupt-input policy,
- schema-drift policy,
- database-capacity protection.

A useful design test is:

> **What happens if the job fails at every possible point?**

Then ask:

> **What will a retry do?**

Then:

> **What will a concurrent reader observe?**

This is the mindset that separates production I/O engineering from API memorization.

## 79. Production I/O Decision Framework

When selecting an I/O design, use this sequence:

### 1. Define correctness

What records must exist after success?

### 2. Define retry semantics

What happens if the job runs twice?

### 3. Define failure visibility

What happens to malformed input and partial output?

### 4. Define source capacity

How much load can the source safely accept?

### 5. Define storage layout

What partition/file organization supports downstream queries?

### 6. Define reliability requirements

Do you need only files, or table-level transactional semantics?

### 7. Define performance evidence

Which measurements prove the design works?

### 8. Define operational controls

What will alert engineers when behavior changes?

This sequence should be used before tuning individual Spark options.

## 80. Learning Loop

Use the roadmap learning loop:

```text
READ
↓
UNDERSTAND
↓
PREDICT
↓
WRITE PYSPARK CODE
↓
RUN SMALL
↓
INSPECT OUTPUT
↓
INSPECT SCHEMA
↓
INSPECT PLAN
↓
INTRODUCE FAILURE
↓
DEBUG
↓
MEASURE
↓
COMPARE
↓
DOCUMENT
↓
EXPLAIN ALOUD
↓
APPLY TO PRODUCTION SCENARIO
```

Repeat the loop for:

- formats,
- schemas,
- save modes,
- partition overwrite,
- JDBC,
- object storage,
- catalogs,
- bucketing,
- compaction.

## 81. Final Quality Control

Before considering this topic complete:

- [x] DataFrameReader covered.
- [x] DataFrameWriter covered.
- [x] `format` covered.
- [x] `option` covered.
- [x] `schema` covered.
- [x] `load` covered.
- [x] `save` covered.
- [x] Parquet covered.
- [x] ORC covered.
- [x] JSON covered.
- [x] CSV covered.
- [x] Text covered.
- [x] Avro covered.
- [x] All four save modes covered.
- [x] Overwrite risks covered.
- [x] `partitionBy` covered.
- [x] Explicit schemas covered.
- [x] `PERMISSIVE` covered.
- [x] Corrupt-record handling covered.
- [x] `DROPMALFORMED` covered.
- [x] `FAILFAST` covered.
- [x] Quarantine covered.
- [x] Dynamic partition overwrite covered.
- [x] Idempotent partition writes covered.
- [x] JDBC covered.
- [x] JDBC parallel reads covered.
- [x] `partitionColumn` covered.
- [x] `lowerBound` covered.
- [x] `upperBound` covered.
- [x] `numPartitions` covered.
- [x] `fetchsize` covered.
- [x] Filter pushdown covered.
- [x] Batched JDBC writes covered.
- [x] Source database protection covered.
- [x] S3A covered.
- [x] Credential providers covered.
- [x] S3A performance covered.
- [x] Output committers covered.
- [x] `saveAsTable` covered.
- [x] `insertInto` covered.
- [x] Catalog covered.
- [x] Bucketing covered.
- [x] `bucketBy` covered.
- [x] `sortBy` covered.
- [x] Bucketed joins covered.
- [x] Bucketed aggregations covered.
- [x] Bucket count covered.
- [x] Bucketing limitations covered.
- [x] Cross-engine compatibility limitations covered.
- [x] Small-file problem covered.
- [x] Compaction covered.
- [x] Object-storage atomicity limitations covered.
- [x] Lakehouse motivation covered.
- [x] Spark 4 Python Data Source API awareness covered.
- [x] `jobs/io_patterns.py` exercise designed but not modified.
- [x] Save-mode experiment included.
- [x] JDBC 1-vs-16 experiment included.
- [x] Hands-on labs included.
- [x] Debugging exercises included.
- [x] Production scenarios included.
- [x] Exactly 40 practice questions included.
- [x] Exactly 40 interview questions included.
- [x] Architecture scenarios included.
- [x] At least 25 misconceptions included.
- [x] Performance engineering included.
- [x] Reliability included.
- [x] Security included.
- [x] Cross-module connections included.
- [x] Forward connection to lakehouse table formats included.
- [x] Production checklist included.
- [x] Learning checkpoints included.
- [x] Final assessment included.
- [x] Glossary included.
- [x] No fabricated benchmark numbers.
- [x] No fabricated Spark plan output.
- [x] No fabricated Spark 4 API signatures.
- [x] Version-sensitive behavior identified.
- [x] Beginner → Intermediate → Advanced → Production progression is clear.
