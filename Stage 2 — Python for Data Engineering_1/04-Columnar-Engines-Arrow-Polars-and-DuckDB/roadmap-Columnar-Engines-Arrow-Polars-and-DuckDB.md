# Roadmap — Module 2.4: Columnar Engines — Arrow, Polars, and DuckDB

This is the learning roadmap for the fourth module of Stage 2, **Python for
Data Engineering**. It tells you **what** to learn about Apache Arrow,
Polars, and DuckDB, **in what order**, **how** to learn each topic, and
**how to prove to yourself** that you have learned it before you move on.

Module 2.3 ended with a warning: pandas is single-threaded for most work,
needs several times the data size in memory, and was not designed around
columnar storage. This module introduces the modern single-node data stack
that removes those limits:

- **Apache Arrow** — a standard columnar in-memory format. It is the common
  language that lets engines exchange data without copying or converting.
- **Polars** — a multi-threaded DataFrame library with an expression API, a
  query optimizer, and a streaming engine for larger-than-memory data.
- **DuckDB** — an in-process analytical SQL database ("SQLite for
  analytics") that queries Parquet, CSV, JSON, Arrow, pandas, and Polars
  directly, locally or on object storage.

For a large share of real pipelines — tens to hundreds of gigabytes on one
machine — these tools replace a Spark cluster at a fraction of the cost and
complexity. Knowing where that line is, and being able to move data between
engines without paying for conversions, is a core senior data engineering
skill.

---

## 1. Module outcome

By the end of this module you will be able to:

- Explain the Arrow memory model: arrays, buffers, validity bitmaps,
  offsets, record batches, tables, and schemas.
- Write Polars transformations with **expressions** in the right
  **context** (`select`, `with_columns`, `filter`, `group_by().agg()`,
  `over()`).
- Use the Polars **lazy API**, read its query plans, and explain predicate,
  projection, and slice pushdown.
- Process datasets larger than RAM with the Polars **streaming engine** and
  sink results straight to files.
- Use DuckDB as an in-process analytical database: persistent files,
  querying DataFrames in place, and its analytics-focused SQL extensions.
- Query local and remote files (Parquet, CSV, JSON; S3-compatible storage)
  with DuckDB, including globs, Hive partitions, and secrets.
- Move data between pandas, Polars, DuckDB, and Arrow with **zero or
  minimal copying**, and know which conversions do copy.
- Choose the right engine for a workload and defend the choice with
  measured benchmarks.

---

## 2. Prerequisites

This module builds on earlier stages and Modules 2.1–2.3. It does **not**
re-teach them.

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| CPU cores, caches, RAM vs storage | Stage 0 — How Computers Work | Columnar engines are fast because they use all cores, SIMD, and cache-friendly layouts |
| Virtual memory, filesystems | Stage 0 — Operating System Fundamentals | Memory mapping, spilling to disk, and out-of-core execution |
| Concurrency vocabulary | Stage 1 — Module 1.9 | Understanding multi-threaded execution and why the GIL does not limit these engines |
| OLTP vs OLAP, lakes and lakehouses | Stage 2 — Module 2.1 | These engines are single-node OLAP engines over lake-style files |
| dtypes, validity masks, views vs copies | Stage 2 — Module 2.2 | Arrow formalises these ideas |
| pandas selection, groupby, joins, reshaping, time series | Stage 2 — Module 2.3 | Every exercise re-implements a pandas pattern; the concepts are not re-taught |
| Basic SQL (`SELECT`, `WHERE`, `GROUP BY`, `JOIN`) | Stage 2 — Module 2.1 exercises (SQLite) | Enough for DuckDB here; Module 2.6 covers SQL in depth |

**Tools needed:**

- Python 3.12+ in a `uv` project: `uv add pyarrow polars duckdb pandas`.
- `pytest` and `polars.testing.assert_frame_equal` for tests.
- Docker (from Stage 0) to run **MinIO** as a local S3-compatible object
  store for Topic 06 — no cloud account needed.
- A realistic dataset: NYC Taxi trip records in Parquet (several years) or
  generated data of 10–50 GB, so larger-than-memory behaviour is real.
- Optional: the DuckDB CLI for interactive SQL.

These libraries release often. Check the version you installed
(`pl.__version__`, `duckdb.__version__`, `pa.__version__`) and read the
current documentation for any API that the topic files mark as new or
changing.

---

## 3. How the module is organised

The eight topics are grouped into four phases. Work through them **in
order**.

```text
Phase A — The Columnar Foundation             (Basics)
  01 Apache Arrow columnar memory model

Phase B — Polars                              (Basics → Advanced)
  02 Polars expressions and contexts
  03 Polars lazy API and query optimization
  04 Polars streaming for larger-than-memory data

Phase C — DuckDB                              (Intermediate → Advanced)
  05 DuckDB in-process analytics
  06 Querying files and object storage with DuckDB

Phase D — Integration and Decisions           (Advanced)
  07 Zero-copy interop between pandas, Polars, DuckDB, and Arrow
  08 Choosing a DataFrame engine

Consolidate
  practice-questions.md
  Module mini-project: one workload, four engines
```

The dependency chain:

```text
01 ──► 02 ──► 03 ──► 04 ──► 05 ──► 06 ──► 07 ──► 08
Arrow   Polars  lazy   out-of-  DuckDB  files &  moving   choosing
format  eager   plans  core     SQL     object   data     with
                                        storage  between  evidence
                                                 engines
```

Why this order:

- Arrow comes first because Polars and DuckDB both use Arrow-style
  columnar memory; once you know the format, both engines make sense.
- Polars before DuckDB: the lazy API teaches query plans and pushdown in a
  DataFrame setting you already know from pandas; DuckDB then shows the
  same ideas in SQL.
- Interop (07) needs all three tools. Choosing an engine (08) needs
  measured experience with all of them.

---

## 4. Suggested schedule

About **4 weeks at 8–10 hours per week**.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — Arrow · Topic 02 — Polars expressions and contexts |
| 2 | Topic 03 — Polars lazy API · Topic 04 — Polars streaming |
| 3 | Topic 05 — DuckDB in-process analytics · Topic 06 — files and object storage |
| 4 | Topic 07 — zero-copy interop · Topic 08 — choosing an engine · practice questions · mini-project |

---

## 5. How to study every topic (the query-engine loop)

```text
Read → Write the pandas version → Write the engine version → Read the plan
→ Assert equal results → Scale up → Measure time, memory, bytes read
→ Break it → Write it down → Explain aloud
```

1. **Read** the topic file once, fully.
2. **Write the pandas version** of the task first (you know pandas from
   Module 2.3) so you have a trusted reference.
3. **Write the engine version** — Arrow compute, Polars, or DuckDB SQL.
4. **Read the plan**: `LazyFrame.explain()` in Polars, `EXPLAIN` /
   `EXPLAIN ANALYZE` in DuckDB. Identify what was pushed down and what was
   not. This is the habit that separates engine users from engine experts.
5. **Assert equal results** on a small input (sort both outputs first —
   these engines do not guarantee row order without `ORDER BY` / `sort`).
6. **Scale up** to millions of rows and multi-gigabyte files.
7. **Measure** wall time, peak memory, and — for file queries — how many
   bytes were actually read.
8. **Break it**: nulls, schema drift between files, a file larger than
   RAM, an unsupported operation in streaming mode.
9. **Write down** what you learned in `module-2.4-notes.md`.
10. **Explain aloud** why the engine version is faster (or why it is not).

Keep a single `columnar_lab/` `uv` project:

```text
columnar_lab/
├── data/               # Parquet/CSV inputs (git-ignored)
├── docker-compose.yml  # MinIO for Topic 06
├── src/columnar_lab/   # one module per topic
├── benchmarks/         # timing scripts and result CSVs
└── tests/
```

---

## 6. Phase A — The Columnar Foundation (Basics)

### Topic 01 — [Apache Arrow columnar memory model](01-apache-arrow-columnar-memory-model.md)

**Why it comes first:** Arrow is the memory format underneath Polars, a
common exchange format for DuckDB, the optional backend for pandas, and the
batch format for Spark's pandas UDFs. Understanding it once explains
performance and interoperability across the whole stack.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What Arrow is (a language-independent **specification** for columnar in-memory data) and what it is not (not a file format like Parquet, not a query engine) |
| Basics | Core objects in `pyarrow`: `Array`, `ChunkedArray`, `RecordBatch`, `Table`, `Schema`, `Field`, `DataType` |
| Basics | Creating tables from Python lists, dicts, NumPy, and pandas; inspecting `schema`, `num_rows`, `nbytes` |
| Intermediate | **Physical layout**: every array is one or more buffers — a validity bitmap (1 bit per value for null), a data buffer, and for variable-length types an offsets buffer |
| Intermediate | Nulls as a first-class concept for **every** type (unlike NumPy integers — Module 2.2) |
| Intermediate | The type system: integers, floats, `decimal128`, `bool`, `date32`, `timestamp` with unit and time zone, `duration`, `string` / `large_string` / `string_view`, `binary` |
| Intermediate | Nested types: `list`, `struct`, `map` — nested data kept columnar |
| Intermediate | Encodings: `dictionary` (like pandas categoricals) and run-end encoding |
| Intermediate | `pyarrow.compute` functions: filtering, arithmetic, string functions, aggregations, `take`, `sort_indices` |
| Advanced | Chunking: why a `Table` column is a `ChunkedArray`, when to `combine_chunks`, and how batch size affects performance |
| Advanced | Immutability, slicing without copying, and memory pools (`pa.total_allocated_bytes()`) |
| Advanced | Arrow IPC: the streaming and file (Feather v2) formats; memory-mapping IPC files for near-instant loads |
| Advanced | Schema metadata; casting with `safe=True` and why unsafe casts truncate silently |
| Advanced | The wider ecosystem (awareness level): Arrow C Data Interface, Arrow Flight (network transport), ADBC (database connectivity returning Arrow) |

**How to learn it**

1. Read the topic file.
2. Build an array of strings with nulls, then inspect its buffers with
   `arr.buffers()`. Draw the validity bitmap, offsets, and data buffer by
   hand for a five-element example.
3. Compare the same column as a Python list, a NumPy `object` array, a
   pandas `object` column, and an Arrow `string` array: memory and time to
   compute string lengths.

**Hands-on exercise — `arrow_basics.py`**

1. Build an orders `Table` with an explicit `Schema`: `order_id: string`,
   `customer_id: int64` (nullable), `amount: decimal128(12, 2)`,
   `created_at: timestamp("us", tz="UTC")`, `tags: list<string>`,
   `address: struct<city: string, zip: string>`.
2. Filter, compute totals, and extract `address.city` with
   `pyarrow.compute` only.
3. Dictionary-encode `country` and measure the memory saving.
4. Write the table to Arrow IPC, then memory-map it back and time the load
   against reading the same data from CSV.
5. Show one unsafe cast that truncates data and how `safe=True` prevents
   it.
6. Test schemas and values with pytest.

**Checkpoint — you are ready to move on when you can:**

- [ ] Explain the three buffers of a nullable string array.
- [ ] Explain the difference between Arrow (in memory) and Parquet (on
      disk).
- [ ] Explain why a `Table` column is a `ChunkedArray`.
- [ ] Represent nested data (lists and structs) in Arrow.
- [ ] Explain why Arrow is a good exchange format between engines.

**Common mistakes:** thinking Arrow is a file format or a database;
creating many tiny chunks; losing time-zone information on timestamps;
unsafe casts in production code.

---

## 7. Phase B — Polars (Basics → Advanced)

### Topic 02 — [Polars expressions and contexts](02-polars-expressions-and-contexts.md)

**Why here:** Polars is the DataFrame library built on Arrow-style memory.
Its expression API is different from pandas, and learning to *think in
expressions* is the key skill.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Polars mental model: no index, strict and explicit dtypes, immutable frames, multi-threaded execution |
| Basics | **Expressions**: `pl.col("x")`, `pl.lit(1)`, arithmetic, comparisons, `alias`, `cast` — an expression describes a computation; a context runs it |
| Basics | **Contexts**: `select` (choose/compute columns), `with_columns` (add/replace columns), `filter` (keep rows), `group_by(...).agg(...)` (aggregate) |
| Basics | Reading and writing: `pl.read_csv`, `pl.read_parquet`, `pl.read_ndjson`, `write_parquet`; explicit `schema=` / `schema_overrides=` |
| Intermediate | Conditional logic: `pl.when().then().otherwise()` |
| Intermediate | Namespaces: `.str`, `.dt`, `.list`, `.struct`, `.cat`, `.name` |
| Intermediate | Column selection with `polars.selectors` (`cs.numeric()`, `cs.starts_with("amt_")`) and multi-column expressions |
| Intermediate | Nulls vs `NaN`: Polars keeps them separate (`is_null` vs `is_nan`) — unlike pandas |
| Intermediate | Dtypes: `Int8`–`Int64`, `UInt*`, `Float32/64`, `Decimal`, `String`, `Categorical`, `Enum` (fixed categories), `Date`, `Datetime(time_unit, time_zone)`, `Duration`, `List`, `Struct` |
| Intermediate | Joins: `how="inner" \| "left" \| "full" \| "semi" \| "anti" \| "cross"`, `validate="1:1" \| "1:m" \| "m:1"` for cardinality checks, and `join_asof` |
| Advanced | **Window expressions** with `.over(...)` — group-wise computations that keep the original rows (the equivalent of pandas `transform` and SQL window functions) |
| Advanced | Reshaping: `pivot`, `unpivot`, `explode`, `implode`; time grouping with `group_by_dynamic` and `rolling` |
| Advanced | Expression parallelism: all expressions in one context run in parallel — why many expressions in one `with_columns` beat many separate calls |
| Advanced | Avoiding Python UDFs (`map_elements`): they run row by row, bypass the optimizer, and hold the GIL; what to use instead |

**How to learn it**

1. Read the topic file.
2. Translate 15 pandas snippets from Module 2.3 into Polars. For each,
   write which context the expression runs in.
3. Rewrite three pandas `groupby(...).transform(...)` calls with `.over()`.

**Hands-on exercise — `polars_orders.py`**

Re-implement your Module 2.3 silver and gold logic in Polars (eager mode):

1. Typed read of raw orders with `schema_overrides`, `Enum` for status,
   `Datetime("us", "UTC")` for timestamps.
2. Latest version per order (`sort` + `unique(keep="last")`, or a window
   expression with `.over("order_id")`).
3. Customer metrics with `group_by().agg()` and each order's share of the
   customer's total with `.over()`.
4. Validated joins to customers and products using `validate="m:1"`;
   `join_asof` for FX conversion.
5. Daily revenue with `group_by_dynamic`.
6. Assert equal results against your pandas pipeline (after sorting) and
   benchmark both.

**Checkpoint:**

- [ ] Explain the difference between an expression and a context.
- [ ] Explain why Polars has no index and what replaces index alignment.
- [ ] Use `.over()` for group-wise calculations.
- [ ] Explain why `map_elements` is slow and name two alternatives.
- [ ] Explain how Polars treats `null` and `NaN` differently.

**Common mistakes:** writing pandas-style row loops; chaining many separate
`with_columns` calls instead of one; using `map_elements` for things the
`.str` or `.dt` namespaces already do; forgetting that output row order is
not guaranteed after `group_by`.

---

### Topic 03 — [Polars lazy API and query optimization](03-polars-lazy-api-and-query-optimization.md)

**Why here:** The eager API runs each step immediately. The lazy API lets
Polars see the whole query and optimize it — the idea behind every serious
query engine, including Spark (Module 2.14) and DuckDB (Topic 05).

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `LazyFrame`: building a query plan without executing it; `df.lazy()` and `collect()` |
| Basics | Scanning sources lazily: `pl.scan_parquet`, `pl.scan_csv`, `pl.scan_ndjson`, `pl.scan_ipc` — including globs of many files |
| Basics | `collect_schema()` to get the output schema without running the query |
| Intermediate | Reading plans: `explain()` (optimized vs unoptimized), `show_graph()` |
| Intermediate | Optimizations: **predicate pushdown** (filter early, at the scan), **projection pushdown** (read only needed columns), **slice pushdown** (`head` stops early), common subplan / subexpression elimination, simplification |
| Intermediate | How pushdown meets file formats: Parquet column pruning and row-group skipping using statistics (Module 2.5 explains the internals) |
| Intermediate | Hive-partitioned datasets with `scan_parquet(..., hive_partitioning=True)` and partition pruning |
| Advanced | `profile()` to see time per plan node; finding the expensive step |
| Advanced | What blocks optimization: Python UDFs, eager conversions in the middle, `collect()` inside loops, operations on the full dataset too early |
| Advanced | `pl.collect_all` for running several queries that share a scan |
| Advanced | Sinks: `sink_parquet`, `sink_csv`, `sink_ipc`, `sink_ndjson` — writing results without materialising them in Python |
| Advanced | Structuring a pipeline as functions that take and return `LazyFrame`s — easy to test, optimized as one plan |

**How to learn it**

1. Read the topic file.
2. For five queries, print the unoptimized and optimized plans and mark
   every change the optimizer made.
3. Write one query that defeats pushdown (a Python UDF before a filter) and
   one that does not, and compare the plans and the bytes read.

**Hands-on exercise — `lazy_pipeline.py`**

On a multi-file Parquet dataset (for example, several years of taxi trips):

1. Build the full silver → gold pipeline from Topic 02 as `LazyFrame`
   functions starting from `scan_parquet`.
2. Show with `explain()` that only the needed columns are read and that
   date filters reach the scan.
3. Measure bytes read and time for: eager `read_parquet` + filter, lazy
   with pushdown, and lazy with a UDF that blocks pushdown.
4. Use `profile()` to find the slowest node and improve it.
5. Write results with `sink_parquet`.
6. Unit-test each `LazyFrame` function on a tiny in-memory frame.

**Checkpoint:**

- [ ] Explain predicate, projection, and slice pushdown.
- [ ] Read an optimized plan and point to where a filter was applied.
- [ ] Explain why calling `collect()` in the middle of a pipeline is
      costly.
- [ ] Name two things that prevent optimization.

**Common mistakes:** using `read_*` instead of `scan_*` for large inputs;
collecting too early; assuming the optimizer can see inside Python
functions.

---

### Topic 04 — [Polars streaming for larger-than-memory data](04-polars-streaming-for-larger-than-memory-data.md)

**Why here:** The lazy API gives Polars the whole plan; the streaming
engine uses it to process data in batches, so the full dataset never needs
to fit in RAM — replacing the manual chunking of Module 2.3.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why in-memory engines fail on big data, and how streaming (processing morsels/batches through the plan) solves it |
| Basics | Running a query on the streaming engine: `collect(engine="streaming")` and streaming sinks (`sink_parquet` and friends) |
| Intermediate | Which operations stream well (scans, filters, projections, most aggregations, many joins) and which need the whole input or large state (some sorts, certain window functions, pivots) |
| Intermediate | Fallbacks: when parts of a plan cannot stream and run in memory instead — how to detect this and redesign the query |
| Intermediate | Memory behaviour of `group_by` with high-cardinality keys, joins with large build sides, and global sorts |
| Intermediate | Partitioned output: writing one file per partition key directly from a sink (check the current API in your version) |
| Advanced | Tuning: batch/chunk sizes, thread count (`POLARS_MAX_THREADS`), and memory limits of your machine or container |
| Advanced | Designing for streaming: filter and project early, pre-aggregate before joins, split one huge query into partition-wise runs |
| Advanced | Comparing with manual chunking in pandas: correctness at chunk boundaries (the engine handles it) and performance |
| Advanced | Awareness: GPU execution (`engine="gpu"`) and distributed Polars — when they exist and what problems they target |

**How to learn it**

1. Read the topic file.
2. Take a query that crashes (or swaps heavily) with in-memory
   `collect()` and make it succeed with streaming. Record peak memory for
   both.
3. Classify 15 operations as "streams well" or "needs full data/state",
   then verify with plans and memory measurements.

**Hands-on exercise — `streaming_aggregations.py`**

Use a dataset at least **2–3× larger than your available RAM** (generate
it if needed):

1. Compute daily trips, revenue, and p95 fare per zone with the streaming
   engine; measure peak memory (e.g. with `/usr/bin/time -v` on Linux).
2. Deduplicate trips on a composite key across the whole dataset and
   compare with the pandas chunked approach from Module 2.3 (correctness
   and effort).
3. Join trips to a zone lookup table and sink the result as partitioned
   Parquet by month.
4. Deliberately add an operation that does not stream well; observe the
   memory spike, then redesign the query.
5. Write a short note: peak memory vs data size for each run.

**Checkpoint:**

- [ ] Explain how streaming execution keeps memory bounded.
- [ ] Run a query on data larger than RAM and prove it with measurements.
- [ ] Name operations that need a lot of memory even in streaming mode.
- [ ] Redesign a query to reduce state (filter early, pre-aggregate).

**Common mistakes:** calling `collect()` without the streaming engine on
huge inputs; collecting the full result into Python instead of sinking to
files; global sorts on data far larger than memory.

---

## 8. Phase C — DuckDB (Intermediate → Advanced)

### Topic 05 — [DuckDB in-process analytics](05-duckdb-in-process-analytics.md)

**Why here:** After seeing optimization in a DataFrame engine, you learn
the same ideas in SQL. DuckDB is the easiest way to run fast analytical SQL
anywhere Python runs — laptops, CI, containers, and serverless functions.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What "in-process" means: no server, the database runs inside your Python process (compare with PostgreSQL — Module 2.7 — and SQLite from Module 2.1) |
| Basics | `duckdb.sql(...)`, `duckdb.connect()` (in-memory) vs `duckdb.connect("warehouse.duckdb")` (persistent file); tables, views, `CREATE TABLE AS SELECT` |
| Basics | Getting results: `.fetchall()`, `.df()` (pandas), `.pl()` (Polars), `.arrow()` (Arrow), `.fetchnumpy()` |
| Basics | Querying Python objects directly by variable name: `SELECT * FROM my_pandas_df` or a Polars frame or Arrow table (replacement scans) |
| Intermediate | Why it is fast: columnar storage, vectorized execution, parallelism across cores, and a cost-based optimizer |
| Intermediate | Analytics-friendly SQL: `GROUP BY ALL`, `SELECT * EXCLUDE (...)` / `REPLACE (...)`, `QUALIFY` for filtering window results, `ASOF JOIN`, `PIVOT` / `UNPIVOT`, FROM-first syntax, list and struct functions |
| Intermediate | The relational (Python) API: `duckdb.sql(...).filter(...).aggregate(...)` — composing queries in Python |
| Intermediate | Parameterised queries with `?` placeholders — never string-formatting values into SQL |
| Advanced | `EXPLAIN` and `EXPLAIN ANALYZE`: reading physical plans and operator timings |
| Advanced | Resource settings: `SET memory_limit`, `SET threads`, `SET temp_directory`; out-of-core execution by spilling to disk |
| Advanced | Transactions and concurrency: ACID within one database file, one writing process at a time, many readers; why DuckDB is not an OLTP database or a shared multi-user server |
| Advanced | Extensions: `INSTALL` / `LOAD` (e.g. `httpfs`, `json`, `delta`, `iceberg`, `spatial`) |
| Advanced | Using DuckDB as a local development warehouse and as a test double for warehouse SQL (dialect differences to watch) |

**How to learn it**

1. Read the topic file.
2. Answer the same ten questions about the orders data three ways: pandas,
   Polars, and DuckDB SQL. Compare readability and speed.
3. Run `EXPLAIN ANALYZE` on your slowest query and identify the most
   expensive operator.

**Hands-on exercise — `duckdb_warehouse.py`**

1. Create a persistent `lab.duckdb` with `raw_orders`, `customers`, and
   `products` loaded from your Module 2.3 bronze Parquet files.
2. Build silver and gold as SQL views/tables: dedupe with `QUALIFY
   row_number() OVER (...) = 1`, joins, `ASOF JOIN` for FX, and a `PIVOT`
   report.
3. Query a Polars frame and a pandas frame directly from SQL and return
   results as Arrow.
4. Set a low `memory_limit` and run a large aggregation to observe
   spilling to `temp_directory`.
5. Show a parameterised query and test it with pytest against an
   in-memory database.

**Checkpoint:**

- [ ] Explain what "in-process" means and its trade-offs.
- [ ] Query a pandas or Polars DataFrame from DuckDB SQL without loading it
      into a table.
- [ ] Use `QUALIFY`, `GROUP BY ALL`, and `ASOF JOIN`.
- [ ] Read an `EXPLAIN ANALYZE` output.
- [ ] Explain why DuckDB is not a replacement for PostgreSQL.

**Common mistakes:** opening the same database file for writing from
several processes; formatting values into SQL strings; pulling huge results
into pandas when the next step could stay in SQL.

---

### Topic 06 — [Querying files and object storage with DuckDB](06-querying-files-and-object-storage-with-duckdb.md)

**Why here:** Much of a data lake is Parquet, CSV, and JSON files on object
storage. DuckDB can query them in place — no loading step, no cluster.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Querying files directly: `SELECT * FROM 'data/*.parquet'`, `read_parquet`, `read_csv`, `read_json` |
| Basics | CSV auto-detection (the sniffer) and when to override it with explicit `columns=`, `types=`, `dateformat=` |
| Intermediate | Multi-file reads: globs, lists of files, `union_by_name=true` for schema drift, `filename=true` to track the source file |
| Intermediate | Hive partitions: `hive_partitioning=true` and partition pruning on `year=2025/month=03/` layouts |
| Intermediate | Parquet pushdown: projection and filter pushdown using row-group statistics; `parquet_metadata()` and `parquet_schema()` for inspection |
| Intermediate | Writing files: `COPY (query) TO 'out.parquet' (FORMAT parquet)`, `PARTITION_BY`, compression options |
| Intermediate | Object storage: the `httpfs` extension, `CREATE SECRET` for S3-compatible credentials (and credential chains for cloud roles), endpoints for MinIO |
| Advanced | How remote reads work: HTTP range requests, reading only footers and needed column chunks — why file layout decides remote query cost |
| Advanced | Reading lakehouse tables with the `delta` and `iceberg` extensions (awareness here; Module 2.15 goes deep) |
| Advanced | Performance on remote data: many small files vs fewer larger files, caching, and network cost |
| Advanced | Secrets hygiene: never hard-coding keys in SQL scripts; scoped, temporary credentials (Stage 0 local secrets hygiene; Module 2.17 covers cloud IAM) |

**How to learn it**

1. Read the topic file.
2. Start MinIO with Docker Compose, upload your Parquet dataset in a Hive
   layout, and query it locally and remotely.
3. For one query, compare total file size with bytes actually read, using
   `EXPLAIN ANALYZE` and MinIO's request logs or metrics.

**Hands-on exercise — `lake_queries.py`**

1. Upload taxi Parquet files to MinIO as
   `s3://lake/trips/year=YYYY/month=MM/`.
2. Configure DuckDB with `CREATE SECRET` for MinIO (credentials from
   environment variables, not the script).
3. Query one month with a filter on partition columns and show only those
   files are read.
4. Read a folder of CSV files whose later files added a column, using
   `union_by_name=true` and `filename=true`.
5. Write a gold aggregate back to MinIO with `COPY ... (FORMAT parquet,
   PARTITION_BY (year, month))`.
6. Compare runtime of the same query on local disk vs MinIO and explain the
   difference.

**Checkpoint:**

- [ ] Query a partitioned Parquet dataset on S3-compatible storage.
- [ ] Explain how partition pruning and row-group statistics reduce data
      read.
- [ ] Handle schema drift across files.
- [ ] Configure credentials without hard-coding them.

**Common mistakes:** trusting CSV auto-detection in production; thousands
of tiny files; secrets committed in SQL files; reading whole remote
datasets because a filter could not be pushed down.

---

## 9. Phase D — Integration and Decisions (Advanced)

### Topic 07 — [Zero-copy interop between pandas, Polars, DuckDB, and Arrow](07-zero-copy-interop-between-pandas-polars-duckdb-and-arrow.md)

**Why here:** Real pipelines mix engines: DuckDB for SQL-heavy steps,
Polars for complex transformations, pandas for a library that only accepts
pandas, Arrow for handing data to another system. The boundaries between
them can cost more than the work itself — or almost nothing.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Conversion functions: `pl.from_arrow`, `df.to_arrow()`, `pl.from_pandas`, `df.to_pandas()`, `pa.Table.from_pandas`, `table.to_pandas()`, DuckDB `.arrow()`, `.pl()`, `.df()` |
| Basics | What **zero-copy** means: sharing the same memory buffers instead of converting values |
| Intermediate | When conversions **copy**: NumPy-backed pandas columns with nulls, pandas `object` strings, different timestamp units or time-zone handling, types without an equivalent, chunk consolidation |
| Intermediate | pandas with Arrow-backed dtypes (`dtype_backend="pyarrow"`, `types_mapper=pd.ArrowDtype`) for cheaper round trips |
| Intermediate | Type-mapping pitfalls: nullable integers, decimals, categoricals/dictionaries/`Enum`, nested lists and structs, time zones |
| Advanced | The Arrow C Data Interface and the **Arrow PyCapsule interface** (`__arrow_c_stream__`) — how libraries exchange data without depending on each other |
| Advanced | Streaming record batches between engines (e.g. DuckDB producing Arrow batches consumed incrementally) instead of materialising everything |
| Advanced | Dataframe-agnostic code with **Narwhals** — writing one function that accepts pandas, Polars, and other frames |
| Advanced | Measuring conversion cost: time and peak memory of each boundary; minimising the number of boundaries in a pipeline |
| Advanced | Beyond one process: Arrow IPC files, Arrow Flight, and ADBC drivers for moving Arrow data to and from databases (awareness) |

**How to learn it**

1. Read the topic file.
2. Build a conversion matrix: for each pair of engines, measure time and
   extra memory on a 10-million-row table with ints, floats, strings, nulls,
   timestamps, and a list column.
3. For each row of the matrix, explain *why* it copied or did not.

**Hands-on exercise — `interop_matrix.py`**

1. Generate a wide, mixed-type Arrow table (including nulls, time zones,
   decimals, and nested columns).
2. Convert it through every path (Arrow → Polars → DuckDB → pandas →
   Arrow, and variants). After every hop, assert the schema and values are
   unchanged — record every place types changed.
3. Measure conversion time and peak memory; save the results as a CSV
   table.
4. Write one function using Narwhals that accepts pandas or Polars and
   returns the same result type, and test it with both.
5. Build a mixed pipeline — DuckDB reads and filters Parquet → Polars
   transforms → a pandas-only library consumes — with the fewest possible
   copies, and document each boundary.

**Checkpoint:**

- [ ] Explain what zero-copy means and give two cases where it is
      impossible.
- [ ] Move data between all four tools and keep types intact.
- [ ] Measure the cost of a conversion.
- [ ] Explain what the Arrow PyCapsule interface is for.

**Common mistakes:** converting back and forth between engines at every
step; losing time zones or decimals silently; `to_pandas()` on a huge
result just to call one function.

---

### Topic 08 — [Choosing a DataFrame engine](08-choosing-a-dataframe-engine.md)

**Why last:** Every earlier topic gave you hands-on evidence. This topic
turns it into a repeatable decision process — the kind of judgment expected
from a senior engineer in a design review.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Strengths and limits of each tool: pandas (ecosystem, familiarity), Polars (fast DataFrame API, streaming), DuckDB (SQL, files, persistence), Arrow (exchange and storage format, not an analysis API) |
| Basics | Decision factors: data size vs RAM, SQL vs DataFrame preference, team skills, library ecosystem requirements, deployment target |
| Intermediate | **Benchmarking properly**: realistic data and queries, warm vs cold cache, repeated runs, same file format, measuring memory as well as time, and avoiding vendor benchmark marketing |
| Intermediate | Standard benchmark ideas (e.g. TPC-H-style queries) and why your own workload matters more |
| Intermediate | Single-node limits: when one machine is enough (often up to hundreds of GB with columnar engines) and when you need distributed engines — Spark (Module 2.14), Dask/Ray (Module 2.21), or a cloud warehouse (Module 2.17) |
| Advanced | Operational factors: memory limits in containers, cold-start time in serverless, concurrency (one writer in DuckDB), reproducibility, and upgrade churn in fast-moving libraries |
| Advanced | Mixing engines deliberately: SQL steps in DuckDB, complex logic in Polars, pandas at the edges — with Arrow as the glue |
| Advanced | Writing an engine decision as an Architecture Decision Record (context, options, measurements, decision, consequences) |
| Advanced | Awareness of other engines in the same space (e.g. DataFusion, chDB, cuDF) and how to evaluate a new one quickly |

**How to learn it**

1. Read the topic file.
2. For five workload descriptions (e.g. "nightly 5 GB CSV → Parquet
   cleanup in a 2 GB container", "ad-hoc analyst SQL on 200 GB of lake
   Parquet", "ML feature prep with scikit-learn", "5 TB daily joins across
   teams", "unit tests for warehouse SQL"), pick an engine and write a
   one-paragraph justification.
3. Challenge each answer: what would change your decision?

**Hands-on exercise — `engine_benchmark/`**

1. Define six realistic queries (filter + aggregate, top-N per group, big
   join, window function, dedupe, time-series resample).
2. Implement each in pandas, Polars (lazy/streaming), and DuckDB.
3. Run each at three data sizes (small, about RAM size, larger than RAM),
   cold and warm, three repetitions each; record time and peak memory.
4. Plot or tabulate the results and write a two-page ADR choosing an engine
   for your team's default single-node pipeline work.

**Checkpoint:**

- [ ] Recommend an engine for a workload and defend it with measurements.
- [ ] Run a fair benchmark and explain its limits.
- [ ] Explain when to move from single-node engines to distributed ones.
- [ ] Write an engine choice as an ADR.

**Common mistakes:** choosing based on a single blog benchmark; comparing
a CSV read in one engine with a Parquet read in another; ignoring team
skills and maintenance cost; reaching for Spark for data that fits on one
machine.

---

## 10. Consolidate — practice questions

When all eight topics are done, open
[`practice-questions.md`](practice-questions.md). For every question:

1. Write the input and output schemas (as Arrow types).
2. Decide the engine first and write one sentence explaining why.
3. Solve it on a tiny input and assert the result (sort before comparing).
4. Read the plan (`explain()` or `EXPLAIN ANALYZE`) and note pushdowns.
5. Run it on a large input and record time, peak memory, and bytes read.
6. If the question involves several engines, count and justify every
   conversion.

---

## 11. Module mini-project — one workload, four engines

This is the proof that you have finished the module.

**Scenario:** Your team wants to replace a slow nightly pandas job and a
small Spark cluster with single-node tools. You must build the new pipeline
and justify the choice.

**Data:** Several years of NYC taxi trips (or generated data at least 2×
your RAM) stored as Hive-partitioned Parquet in MinIO, plus a zone lookup
CSV and a daily fare-rules JSON file.

Build `lake_analytics/`, a `uv` project with:

1. **Ingestion** — land raw CSV/JSON files in MinIO; convert to partitioned
   Parquet with explicit Arrow schemas.
2. **Silver in Polars (lazy + streaming)** — typed, deduplicated,
   validated trips; invalid rows sunk to a quarantine dataset.
3. **Gold in DuckDB** — daily and monthly zone metrics, top-N routes per
   borough with `QUALIFY`, and an `ASOF JOIN` to fare rules; written back to
   MinIO with `COPY ... PARTITION_BY`.
4. **Consumer edge** — one step hands a small result to a pandas-only
   library (e.g. a plotting or reporting library) with minimal copying.
5. **Benchmarks** — the same silver + gold logic in pandas (chunked),
   Polars, and DuckDB at three data sizes; time, peak memory, and bytes
   read.
6. **Decision** — an ADR recommending the default engine(s), with the
   benchmark table, operational risks, and the point at which you would
   move to Spark.
7. **Tests** — pytest tests for every transformation on tiny inputs, schema
   assertions after every engine boundary, and a reconciliation check
   (trip counts and revenue identical across engines).

**Grading yourself:** the pipeline processes a dataset larger than your RAM
without crashing; all engines produce identical gold outputs; every engine
boundary is documented; and your ADR's recommendation follows from your own
measurements.

---

## 12. Module self-assessment — exit criteria

Only move to Module 2.5 when you can tick every box without looking at your
notes:

- [ ] I can explain Arrow's memory layout and type system, including nulls
      and nested types.
- [ ] I can write Polars transformations with expressions, contexts, and
      window expressions.
- [ ] I can read Polars lazy plans and explain pushdown optimizations.
- [ ] I can process larger-than-memory data with Polars streaming.
- [ ] I can use DuckDB as an in-process analytical database, including its
      analytics SQL extensions.
- [ ] I can query partitioned files on S3-compatible storage with DuckDB.
- [ ] I can move data between pandas, Polars, DuckDB, and Arrow with
      minimal copying and no type loss.
- [ ] I can choose an engine and defend the choice with fair benchmarks.
- [ ] I have finished all practice questions and the mini-project.

---

## 13. Recommended reading and references

| Resource | Relevant topics |
| --- | --- |
| Apache Arrow documentation — "Arrow Columnar Format" specification and the PyArrow user guide | 01, 07 |
| Polars user guide — expressions, contexts, lazy API, optimizations, streaming | 02, 03, 04 |
| DuckDB documentation — Python API, "Friendly SQL", data import (Parquet, CSV, JSON), `httpfs` / S3, performance guide | 05, 06 |
| Arrow PyCapsule interface documentation; Narwhals documentation | 07 |
| *DuckDB in Action* — Mark Needham, Michael Hunger, Michael Simons (Manning) | 05, 06 |
| *Designing Data-Intensive Applications* — Martin Kleppmann, chapter on column-oriented storage | 01, 08 |
| Polars and DuckDB official blogs and release notes (both projects change quickly) | All topics |

---

## 14. Where this module leads

| This module's idea | Where it goes deeper |
| --- | --- |
| Pushdown and row-group statistics | 2.5 Data Formats — Parquet internals, compression, partitioning, file sizing |
| DuckDB SQL and window functions | 2.6 SQL for Data Engineers |
| ADBC and Arrow from databases | 2.7 Python Database Connectivity |
| Query plans and optimizers | 2.14 PySpark — Catalyst and adaptive query execution |
| Delta and Iceberg extensions | 2.15 Lakehouse Table Formats |
| Object storage and credentials | 2.17 Cloud Storage and Cloud Data Platforms |
| Engine benchmarks and single-node limits | 2.21 Performance, Scaling, and Cost Optimization |
| Arrow batches for ML and AI | 2.22 Serving Data for Analytics, ML, and AI |

Arrow, Polars, and DuckDB change what one engineer on one machine can do.
The discipline you build here — reading plans, measuring bytes read, and
counting conversions — is exactly the discipline that keeps distributed
Spark and cloud warehouse workloads fast and cheap later in Stage 2.
