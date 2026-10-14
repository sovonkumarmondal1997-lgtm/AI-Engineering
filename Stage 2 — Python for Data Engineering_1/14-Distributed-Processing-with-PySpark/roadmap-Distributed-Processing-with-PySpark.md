# Roadmap — Module 2.14: Distributed Processing with PySpark

This is the learning roadmap for the fourteenth module of Stage 2, **Python
for Data Engineering**. It tells you **what** to learn about Apache Spark
with Python, **in what order**, **how** to learn each topic, and **how to
prove to yourself** that you have learned it before you move on.

In Module 2.4 you learned that single-node engines (Polars, DuckDB) handle
a surprising amount of data — and you wrote down the point at which you
would move to a distributed engine. This module is that move. **Apache
Spark** is the most widely used engine for processing data across many
machines, it underpins most lakehouse platforms, and PySpark is a core
skill in a large share of data engineering roles and interviews.

Writing PySpark that *works* is easy — the DataFrame API looks like the
pandas and Polars code you already know. Writing PySpark that works **at
scale** is a different skill: understanding where data moves between
machines (shuffles), how many pieces work is split into (partitions), why
one task takes an hour while the others take a minute (skew), what the
optimizer did to your query (plans), and how to read the Spark UI when a
job is slow or dies with out-of-memory errors. This module teaches both.

---

## 1. Module outcome

By the end of this module you will be able to:

- Explain Spark's architecture: driver, executors, cluster managers, jobs,
  stages, tasks, and partitions.
- Configure a `SparkSession`, size executors, package Python dependencies,
  and submit jobs in client and cluster deploy modes.
- Explain RDDs vs DataFrames and why DataFrames (and Spark SQL) are the
  default.
- Predict jobs, stages, and shuffles from transformations and actions, and
  use lazy evaluation to your advantage.
- Write production transformations with the DataFrame API and Spark SQL,
  including window functions and complex types.
- Choose join strategies, use broadcast joins, and control shuffles.
- Control partitioning in memory and on disk with `repartition`,
  `coalesce`, and `partitionBy`.
- Diagnose and fix **data skew** with AQE, salting, and other techniques.
- Cache and persist data only when it pays off.
- Choose between built-in functions, pandas UDFs, and Python UDFs with
  measured evidence.
- Read Catalyst **explain plans** and use **Adaptive Query Execution**.
- Read and write data sources correctly — schemas, corrupt records, JDBC,
  object storage, save modes, dynamic partition overwrite, and bucketing.
- Debug slow and failing jobs with the **Spark UI**.
- Test PySpark code quickly and reliably.

---

## 2. Prerequisites

This module builds on earlier stages and Modules 2.1–2.13. It does **not**
re-teach them.

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| CPU cores, RAM, disk, network, processes, JVM-style memory basics | Stage 0 — How Computers Work / OS Fundamentals | Executors are processes with cores and memory on networked machines |
| Docker and Docker Compose | Stage 0 — Developer Environment | Running a local Spark cluster and MinIO |
| Pure functions, layered design, pytest fixtures | Stage 1 — Modules 1.7–1.8 | Testable Spark transformations |
| Batch vs streaming, lakehouse architecture | Stage 2 — Module 2.1 | Spark's place in the platform |
| NumPy vectorisation and memory | Stage 2 — Module 2.2 | Pandas UDFs are vectorised NumPy/pandas code |
| pandas `groupby`, joins, windows, chunking | Stage 2 — Module 2.3 | The DataFrame API maps to these ideas |
| Arrow, Polars lazy plans and pushdown, single-node limits | Stage 2 — Module 2.4 | Spark plans and pushdown are the same ideas at cluster scale; Arrow powers pandas UDFs |
| Parquet internals, partitioning, small files, compression | Stage 2 — Module 2.5 | File layout decides Spark read and write performance; **not** re-taught |
| SQL: joins, window functions, fan traps, `EXPLAIN` | Stage 2 — Module 2.6 | Spark SQL semantics are **not** re-taught |
| JDBC-style extraction concepts, bulk loading | Stage 2 — Module 2.7 | Spark's JDBC source |
| Star schemas, grain | Stage 2 — Module 2.8 | Star joins and broadcast of dimensions |
| Concurrency and Amdahl's law | Stage 2 — Module 2.10 | Parallelism and stragglers |
| Pandera and quality checks | Stage 2 — Module 2.11 | Validating Spark DataFrames |
| Idempotent loads, partition overwrite, merges, hash keys, backfills | Stage 2 — Module 2.12 | Patterns applied with Spark; **not** re-taught |
| Orchestration, submitting work to external engines | Stage 2 — Module 2.13 | Spark jobs are launched by an orchestrator |

**Tools needed:**

- **Java 17 or 21** (Spark 4 requires Java 17 or newer).
- Python 3.12+ in a `uv` project: `uv add pyspark pyarrow pandas pytest`
  (Spark 4.x; check that your PySpark, Java, and Python versions are
  supported together).
- **Local mode** (`local[*]`) for most exercises, and a small **standalone
  cluster** in Docker Compose (one master, two or three workers) for
  cluster behaviour.
- MinIO (S3-compatible) with Spark's S3A connector, and PostgreSQL with its
  JDBC driver — both from earlier modules.
- A large dataset: several years of NYC taxi trips, or TPC-H data at scale
  factor 10–50 (DuckDB's `tpch` extension can generate it and export to
  Parquet).

**A note on versions:** Spark 4 changed some defaults and added features
compared with Spark 3 — most notably **ANSI SQL mode is on by default**
(invalid casts and overflows raise errors instead of returning NULL), plus
Spark Connect improvements, a `VARIANT` type, and Python data source and
UDTF APIs. Many tutorials still describe Spark 3. Check behaviour against
the version you run, and learn to recognise Spark 3 code you will maintain.

---

## 3. How the module is organised

The sixteen topics are grouped into five phases. Work through them **in
order**.

```text
Phase A — How Spark Works                           (Basics)
  01 Distributed computing: driver, executors, and cluster managers
  02 SparkSession, configuration, and deploy modes
  03 RDDs vs DataFrames
  04 Transformations, actions, and lazy evaluation

Phase B — Writing Spark Code                        (Basics → Intermediate)
  05 DataFrame API: select, filter, and withColumn
  06 Spark SQL and temporary views

Phase C — Moving Data Across the Cluster            (Intermediate → Advanced)
  07 Joins, shuffle, and broadcast joins
  08 Partitioning: repartition and coalesce
  09 Data skew and salting
  10 Caching and persistence levels

Phase D — Performance Internals                     (Advanced)
  11 Python UDFs vs pandas UDFs vs built-ins
  12 Catalyst optimizer and explain plans
  13 Adaptive Query Execution

Phase E — Production I/O and Operations             (Advanced)
  14 Data sources, save modes, and bucketing
  15 Spark UI and debugging slow jobs
  16 Testing PySpark code

Consolidate
  practice-questions.md
  interview-practice.md
  Module mini-project: a tuned, tested Spark pipeline at scale
```

The dependency chain:

```text
01 ► 02 ► 03 ► 04 ► 05 ► 06 ► 07 ► 08 ► 09 ► 10 ► 11 ► 12 ► 13 ► 14 ► 15 ► 16
arch  config API   lazy  write  SQL   joins parts skew  cache UDFs  plans AQE  I/O  debug test
```

Why this order:

- You must know what a driver, executor, and partition are (01) before
  configuring them (02); the API choice (03) and lazy execution (04)
  explain everything that follows.
- You write code (05–06) before you optimise it.
- Joins (07) introduce shuffles; partitioning (08) controls them; skew (09)
  is what goes wrong with them; caching (10) avoids repeating them.
- UDFs (11) come just before Catalyst (12) because UDFs are the most common
  way to block the optimizer; AQE (13) is the runtime layer on top of
  Catalyst.
- I/O (14), debugging (15), and testing (16) are production concerns that
  use everything above.

---

## 4. Suggested schedule

About **6 weeks at 8–10 hours per week**. This is one of the largest
modules in Stage 2.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — architecture · Topic 02 — SparkSession and deploy modes · Topic 03 — RDDs vs DataFrames |
| 2 | Topic 04 — lazy evaluation · Topic 05 — DataFrame API · Topic 06 — Spark SQL |
| 3 | Topic 07 — joins and shuffles · Topic 08 — partitioning |
| 4 | Topic 09 — skew · Topic 10 — caching · Topic 11 — UDFs |
| 5 | Topic 12 — Catalyst and plans · Topic 13 — AQE · Topic 14 — data sources and save modes |
| 6 | Topic 15 — Spark UI and debugging · Topic 16 — testing · practice · interview practice · mini-project |

---

## 5. How to study every topic (the distributed-processing loop)

```text
Read → Predict (stages, shuffles, partitions) → Write it → Explain the plan
→ Run small (local) → Run big (cluster) → Read the Spark UI
→ Change one thing → Measure again → Write it down → Explain aloud
```

1. **Read** the topic file once, fully.
2. **Predict** how many jobs, stages, and shuffles the code will create,
   and how many partitions each stage will have. This habit is the core
   skill of Spark performance work.
3. **Write it** as a pure function `DataFrame → DataFrame` (the Module 2.12
   structure).
4. **Explain the plan** with `df.explain("formatted")` before running it.
5. **Run small** in local mode on a sample to check correctness against a
   pandas, Polars, or DuckDB reference.
6. **Run big** on the Docker cluster with the full dataset.
7. **Read the Spark UI**: jobs, stages, task-time distribution, shuffle
   read/write, spill, and GC time.
8. **Change one thing** — a join hint, a partition count, a cache, a UDF
   replaced by a built-in.
9. **Measure again** and record wall time, shuffle bytes, spill, and task
   time percentiles in a table.
10. **Write down** what you learned in `module-2.14-notes.md`.
11. **Explain aloud** why the change helped or hurt, using the plan and UI
    as evidence.

Keep one `spark_lab/` project:

```text
spark_lab/
├── docker-compose.yml   # Spark master + workers, MinIO, PostgreSQL
├── conf/                # spark-defaults.conf, log4j settings
├── src/spark_lab/       # transformations (pure functions) and jobs (entry points)
├── jobs/                # spark-submit entry scripts
├── experiments/         # tuning results (CSV) and saved plans
└── tests/
```

---

## 6. Phase A — How Spark Works (Basics)

### Topic 01 — [Distributed computing: driver, executors, and cluster managers](01-distributed-computing-driver-executors-and-cluster-managers.md)

**Why it comes first:** Every Spark behaviour — performance, failures,
memory errors, costs — follows from how work is split across machines.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why distribute: data or compute larger than one machine; horizontal vs vertical scaling; shared-nothing clusters |
| Basics | A short history: MapReduce (disk between every step) → Spark (in-memory, optimised plans) |
| Basics | **Driver** (plans the work, holds the `SparkSession`), **executors** (processes that run tasks and hold data), and **cluster manager** (allocates resources) |
| Basics | **Partitions** as the unit of parallelism; **cores** as task slots; one task processes one partition |
| Intermediate | Execution hierarchy: an **action** creates a **job**; a job splits into **stages** at shuffle boundaries; a stage runs one **task** per partition |
| Intermediate | Cluster managers: local mode, Spark standalone, YARN, and Kubernetes — and managed platforms that hide them (Module 2.17) |
| Intermediate | Data locality: moving computation to data, and why cloud object storage changes that picture |
| Intermediate | Fault tolerance: lost partitions recomputed from **lineage**; task retries; speculative execution for stragglers |
| Advanced | How PySpark works: Python driver code talks to the JVM (Py4J in classic mode); Python worker processes run UDFs; Arrow transfers data between the JVM and Python |
| Advanced | **Spark Connect**: a thin client–server architecture where your Python code sends plans to a remote Spark server — benefits and API differences (for example no RDD API) |
| Advanced | When **not** to use Spark: data that fits comfortably in one machine (Module 2.4), low-latency lookups, small frequent jobs where cluster start-up dominates |

**How to learn it**

1. Read the topic file.
2. Draw a cluster with one driver, three executors of four cores each, and
   a 48-partition dataset; show how tasks are scheduled in waves.
3. Start the Docker standalone cluster and match every container and web UI
   to your drawing.

**Hands-on exercise — `jobs/hello_cluster.py`**

1. Run a word count over a large text dataset in local mode and on the
   standalone cluster.
2. In the Spark UI, find the job, its stages, the number of tasks per
   stage, and which executor ran each task.
3. Kill one worker container mid-job and observe task retries and
   recomputation.
4. Run the same aggregation in DuckDB or Polars on one machine and compare
   times; write down where Spark starts to win on your hardware.

**Checkpoint — you are ready to move on when you can:**

- [ ] Explain driver, executor, cluster manager, partition, and task.
- [ ] Explain jobs, stages, and tasks and where stage boundaries come from.
- [ ] Explain how Spark recovers from a lost executor.
- [ ] Explain how Python code runs in PySpark and what Spark Connect
      changes.
- [ ] Decide when Spark is unnecessary.

**Common mistakes:** thinking the driver processes the data; using Spark
for data DuckDB handles in seconds; ignoring that Python and the JVM are
separate processes.

---

### Topic 02 — [SparkSession, configuration, and deploy modes](02-sparksession-configuration-and-deploy-modes.md)

**Why here:** Before writing transformations, you must be able to start
Spark correctly — with the right resources, dependencies, and settings — in
development and in production.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `SparkSession.builder` with `appName`, `master`, and `config`; `local[*]` for development; `spark.stop()` |
| Basics | Configuration sources and precedence: code, `spark-submit` flags, `spark-defaults.conf`, and environment variables; reading the Environment tab |
| Basics | `spark-submit`: `--master`, `--deploy-mode`, `--conf`, application arguments |
| Intermediate | **Deploy modes**: **client** (driver runs where you submit — good for interactive work) vs **cluster** (driver runs inside the cluster — typical for production) |
| Intermediate | **Resources**: `spark.executor.memory`, `spark.executor.cores`, number of executors, `spark.driver.memory`, memory overhead (important for Python workers), dynamic allocation |
| Intermediate | Key SQL settings: `spark.sql.shuffle.partitions`, `spark.sql.adaptive.enabled`, `spark.sql.session.timeZone` (always UTC for pipelines), `spark.sql.ansi.enabled` |
| Intermediate | **Python dependencies on executors**: `--py-files` (zip of your package), packed virtual environments, or container images (typical on Kubernetes); Java dependencies with `--packages` / `--jars` (e.g. JDBC drivers, S3A) |
| Advanced | **Memory model**: unified memory (execution vs storage), user memory, overhead, and off-heap memory — and which one runs out in which error |
| Advanced | **Executor sizing**: few large vs many small executors; a common starting point of about 4–5 cores per executor; leaving room for the OS and overhead; matching container limits |
| Advanced | Configuration hygiene: environment-specific configs, no secrets in code (credentials via environment or secret stores), recording effective config per run |
| Advanced | Connecting to a remote Spark Connect server (`SparkSession.builder.remote(...)`) and what that means for deployment |

**How to learn it**

1. Read the topic file.
2. Package your `spark_lab` code, submit it to the standalone cluster in
   client and cluster modes, and find the driver logs in each case.
3. Calculate executor settings for a given machine size and verify them in
   the Executors tab.

**Hands-on exercise — `conf/` and `jobs/`**

1. Create `spark-defaults.conf` for local development and for the cluster
   (UTC time zone, adaptive execution on, sensible shuffle partitions).
2. Build a job entry point that takes `--date` and `--env` arguments (the
   run context from Module 2.12) and logs its effective configuration.
3. Ship your Python package to executors with `--py-files` and a UDF that
   imports from it; then try a packed virtual environment.
4. Add the PostgreSQL JDBC driver and S3A connector via `--packages` and
   read from both.
5. Run the same job with three executor sizings and compare time and
   memory usage.

**Checkpoint:**

- [ ] Start Spark locally and submit to a cluster.
- [ ] Explain client vs cluster deploy mode.
- [ ] Size executors and explain memory overhead.
- [ ] Ship Python and Java dependencies to executors.

**Common mistakes:** giving the driver huge memory "to be safe" while
executors starve; forgetting memory overhead for Python; configs scattered
across notebooks; session time zone left as the machine's local zone.

---

### Topic 03 — [RDDs vs DataFrames](03-rdds-vs-dataframes.md)

**Why here:** Spark has two main APIs. Knowing why DataFrames won — and
when RDDs still appear — explains why "Pythonic" low-level code is often
the slowest Spark code.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **RDD**: Resilient Distributed Dataset — an immutable, partitioned collection of Python objects with lineage |
| Basics | RDD operations: `map`, `filter`, `flatMap`, `reduceByKey`, `collect` |
| Basics | **DataFrame**: distributed table with a schema, optimised by Catalyst and executed by Tungsten |
| Intermediate | Why DataFrames are faster from Python: work stays in the JVM in optimised binary format; RDD functions serialise every record to Python and back |
| Intermediate | Schemas: `StructType` / `StructField`, DDL strings (`"id BIGINT, amount DECIMAL(12,2)"`), schema inference and its cost |
| Intermediate | `Row` objects and converting between RDDs and DataFrames |
| Advanced | When you still meet RDDs: legacy code, very low-level partition logic, some libraries — and that the RDD API is unavailable with Spark Connect |
| Advanced | Datasets (typed API in Scala and Java only) — awareness |
| Advanced | The pandas API on Spark (`pyspark.pandas`) — when it helps migrate pandas code and its performance caveats |

**How to learn it**

1. Read the topic file.
2. Implement the same aggregation with RDD operations and with DataFrames;
   compare time, plans, and the Python worker activity.
3. Read a large CSV with schema inference and with an explicit schema;
   compare time.

**Hands-on exercise — `src/spark_lab/rdd_vs_df.py`**

1. Compute revenue per country with RDDs (`map` + `reduceByKey`) and with
   the DataFrame API on 100 million rows; record times.
2. Define explicit schemas for your datasets as both `StructType` and DDL
   strings.
3. Convert a small pandas-based transformation to the pandas API on Spark
   and to the DataFrame API; compare.
4. Write down a rule for your team: when (if ever) RDDs are acceptable.

**Checkpoint:**

- [ ] Explain RDDs and DataFrames and why DataFrames are faster in
      PySpark.
- [ ] Define schemas explicitly.
- [ ] Explain when RDDs still appear and their Spark Connect limitation.

**Common mistakes:** using RDD `map` with Python lambdas for work built-in
functions can do; schema inference on large production inputs.

---

### Topic 04 — [Transformations, actions, and lazy evaluation](04-transformations-actions-and-lazy-evaluation.md)

**Why here:** Spark does nothing until you ask for a result. Understanding
laziness explains surprising run times, repeated work, and driver
crashes.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Transformations** (lazy: `select`, `filter`, `join`, `groupBy`) vs **actions** (trigger execution: `count`, `show`, `collect`, `take`, `write`) |
| Basics | Lazy evaluation builds a plan; an action executes it |
| Basics | **Narrow** transformations (each output partition depends on one input partition — no shuffle) vs **wide** transformations (need data from many partitions — shuffle) |
| Intermediate | Predicting stages: every wide transformation adds a stage boundary; counting jobs from actions |
| Intermediate | **Repeated computation**: two actions on the same DataFrame recompute it twice (unless cached — Topic 10) |
| Intermediate | The dangers of `collect()` and `toPandas()` on large data (driver out-of-memory) and Arrow-accelerated `toPandas()` for small results |
| Intermediate | Debugging with `show()` and `count()` — useful, but each one is a full job |
| Advanced | Lineage and recomputation after failures |
| Advanced | Plan growth from building DataFrames in long Python loops, and why it slows planning |
| Advanced | Laziness and errors: bad code may only fail at the action, far from the line that caused it |

**How to learn it**

1. Read the topic file.
2. For ten short programs, predict the number of jobs, stages, and shuffles
   before running them; check in the Spark UI.
3. Add a `count()` after every step of a pipeline and measure the extra
   time.

**Hands-on exercise — `src/spark_lab/lazy.py`**

1. Build a five-step pipeline and confirm that no job runs until the final
   write.
2. Call `count()` and then `write` on the same DataFrame; show the
   recomputation in the UI.
3. Crash the driver with `collect()` on a large DataFrame (with a small
   driver memory); then return a safe aggregate with `toPandas()` using
   Arrow.
4. Build a DataFrame in a 200-iteration loop of `withColumn` calls and
   measure planning time; rewrite it with one `select` / `withColumns`.

**Checkpoint:**

- [ ] Distinguish transformations from actions.
- [ ] Classify transformations as narrow or wide.
- [ ] Predict jobs and stages from code.
- [ ] Avoid driver crashes from `collect()` and `toPandas()`.

**Common mistakes:** `count()` everywhere for "debugging" in production;
`collect()` on large data; building huge plans in loops; assuming each
line runs when it is written.

---

## 7. Phase B — Writing Spark Code (Basics → Intermediate)

### Topic 05 — [DataFrame API: select, filter, and withColumn](05-dataframe-api-select-filter-and-withcolumn.md)

**Why here:** The DataFrame API is how most PySpark pipelines are written.
It feels like Polars expressions (Module 2.4) and SQL (Module 2.6) — this
topic focuses on Spark-specific behaviour and idioms.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Reading data (`spark.read.parquet`, `.csv`, `.json`) with explicit schemas; `printSchema`, `show`, `limit` |
| Basics | `select`, `filter` / `where`, `withColumn`, `withColumnRenamed`, `drop`, `alias` |
| Basics | Column expressions with `pyspark.sql.functions as F`: `F.col`, `F.lit`, `F.when().otherwise()`, arithmetic and comparisons, `cast` |
| Basics | Aggregation: `groupBy().agg(...)` with `F.sum`, `F.count`, `F.countDistinct`, `F.avg`, `F.max` |
| Intermediate | NULL handling: `isNull`, `coalesce`, `na.fill`, `na.drop` — and NULL semantics matching SQL |
| Intermediate | **ANSI mode** behaviour in Spark 4: invalid casts and arithmetic overflow raise errors; `try_cast` and `try_*` functions when failure should produce NULL |
| Intermediate | Strings, dates, and timestamps: `F.to_timestamp`, `F.date_trunc`, `F.from_utc_timestamp`, and the session time zone |
| Intermediate | **Window functions**: `Window.partitionBy(...).orderBy(...)`, `row_number`, `lag`, `sum` over frames (`rowsBetween`, `rangeBetween`) |
| Intermediate | Deduplication: `dropDuplicates(subset)` vs `row_number()` with explicit ordering (the deterministic version) |
| Intermediate | Adding many columns: `withColumns` (dict) or one `select` instead of long `withColumn` chains |
| Advanced | **Complex types**: arrays, structs, and maps; `F.explode`, `F.from_json` / `F.to_json`, higher-order functions (`F.transform`, `F.filter`, `F.aggregate`) on arrays; the `VARIANT` type for semi-structured data (Spark 4) |
| Advanced | `DataFrame.transform(func)` for readable chaining of pure functions (the Spark equivalent of `pipe`) |
| Advanced | `unionByName(allowMissingColumns=True)` for combining sources with drifting schemas |
| Advanced | Porting a pandas or Polars pipeline to PySpark and verifying identical results |

**How to learn it**

1. Read the topic file.
2. Port your Module 2.12 silver orders transformations to PySpark, one
   pure function per step.
3. Compare every step's output with the Polars or DuckDB version on a
   sample.

**Hands-on exercise — `src/spark_lab/silver_orders.py`**

1. Implement `standardise`, `cast_types` (using `try_cast` and a
   quarantine flag for invalid values), `deduplicate_latest` (with
   `row_number`), and `add_derived_columns` as `DataFrame → DataFrame`
   functions chained with `.transform()`.
2. Parse a JSON string column into a struct with `from_json`, explode line
   items, and compute per-order totals with higher-order functions.
3. Compute each customer's running revenue and days since previous order
   with window functions.
4. Replace a 30-step `withColumn` chain with `withColumns` and compare
   planning time.
5. Verify results against the Module 2.12 output.

**Checkpoint:**

- [ ] Write transformations with `select`, `filter`, `withColumn(s)`, and
      `F` functions.
- [ ] Handle NULLs and ANSI-mode casting safely.
- [ ] Use window functions and complex types.
- [ ] Chain transformations with `DataFrame.transform`.

**Common mistakes:** `dropDuplicates` when "latest" was required;
local-time timestamp parsing; long `withColumn` loops; Python-level logic
where a built-in function exists.

---

### Topic 06 — [Spark SQL and temporary views](06-spark-sql-and-temporary-views.md)

**Why here:** Many Spark pipelines — and most analysts — prefer SQL. Spark
SQL and the DataFrame API compile to the same plans, so you can mix them
freely.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `df.createOrReplaceTempView("orders")` and `spark.sql("SELECT ...")` returning DataFrames |
| Basics | Session-scoped temporary views vs global temporary views |
| Basics | Mixing SQL and the DataFrame API in one pipeline |
| Intermediate | **Parameterised queries** (`spark.sql(query, args={...})` with named markers) instead of string formatting (injection rules from Module 2.7) |
| Intermediate | The **catalog**: databases/schemas, tables, and views (`spark.catalog`); **managed** vs **external** tables |
| Intermediate | Spark SQL features for pipelines: CTEs, window functions, `QUALIFY`-style filtering alternatives, `MERGE` (with table formats — Module 2.15), SQL functions for complex types |
| Advanced | Metastores and catalogs: Hive metastore and modern catalogs (Unity-style, Iceberg REST, Glue — Module 2.15 and 2.17) |
| Advanced | Newer SQL features in recent Spark versions (e.g. SQL pipe syntax) — awareness |
| Advanced | Running dbt on Spark (dbt Spark/Databricks adapters) — connecting to Module 2.12 |
| Advanced | Choosing SQL vs DataFrame API: team skills, testability, dynamic logic, and reuse |

**How to learn it**

1. Read the topic file.
2. Write five queries from Module 2.6 in Spark SQL and in the DataFrame
   API; compare their plans — they should be identical.
3. Create managed and external tables and observe what happens to the
   files when you drop each.

**Hands-on exercise — `src/spark_lab/gold_sql.py`**

1. Register silver DataFrames as temporary views and build
   `gold_daily_revenue` and `gold_top_products_per_country` in Spark SQL.
2. Pass the run date with a parameterised query.
3. Save gold outputs as external tables in a local catalog and query them
   from a new Spark session.
4. Confirm with `explain()` that the SQL and DataFrame versions produce the
   same physical plan.

**Checkpoint:**

- [ ] Use temporary views and parameterised Spark SQL.
- [ ] Explain managed vs external tables and the catalog.
- [ ] Mix SQL and DataFrame code in one pipeline.

**Common mistakes:** f-string SQL; managed tables that delete data on
`DROP`; assuming SQL is slower or faster than the DataFrame API.

---

## 8. Phase C — Moving Data Across the Cluster (Intermediate → Advanced)

### Topic 07 — [Joins, shuffle, and broadcast joins](07-joins-shuffle-and-broadcast-joins.md)

**Why here:** Joins are where distributed processing gets expensive: to
join on a key, matching rows must end up on the same machine. That
movement — the **shuffle** — dominates the cost of most Spark jobs.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Join types in Spark: inner, left, right, full, `left_semi`, `left_anti`, cross |
| Basics | What a **shuffle** is: writing data by key to local disk, then fetching it over the network; stage boundaries and shuffle read/write metrics |
| Basics | **Broadcast hash join**: copying a small table to every executor so the big table does not move |
| Intermediate | Join strategies: broadcast hash join, **sort-merge join** (default for large tables), shuffle hash join, broadcast nested loop join, and Cartesian product — and when Spark picks each |
| Intermediate | `spark.sql.autoBroadcastJoinThreshold`, `F.broadcast(df)`, and join hints (`BROADCAST`, `MERGE`, `SHUFFLE_HASH`) |
| Intermediate | Join correctness at scale: key type mismatches, NULL keys, duplicate column names after joins (aliases), and join explosion (from Module 2.6) |
| Intermediate | Star-schema joins: broadcasting dimensions onto a large fact table (Module 2.8) |
| Advanced | Broadcast limits: driver and executor memory, and why "broadcast everything" fails |
| Advanced | Range and non-equi joins at scale, and techniques to make them tractable (bucketing time ranges) |
| Advanced | Avoiding shuffles altogether: pre-partitioned or bucketed data (Topic 14), and aggregating before joining |
| Advanced | Shuffle internals: shuffle files, spill to disk, external shuffle services, and shuffle fetch failures |

**How to learn it**

1. Read the topic file.
2. Join a 500-million-row fact table to dimension tables of 1,000 rows,
   10 million rows, and 500 million rows; record the chosen strategies and
   shuffle bytes.
3. Force different strategies with hints and compare.

**Hands-on exercise — `src/spark_lab/joins.py`**

1. Enrich trips/orders with small dimensions using broadcast joins; confirm
   in the plan that no shuffle occurs on the fact table.
2. Join two large tables with sort-merge join and read shuffle metrics in
   the UI.
3. Try to broadcast a table that is too large; observe the failure and fix
   it.
4. Reproduce and fix a NULL-key issue, a type-mismatch join (zero matches),
   and an ambiguous-column error.
5. Reduce shuffle size by aggregating before joining; measure.

**Checkpoint:**

- [ ] Explain what a shuffle is and why it is expensive.
- [ ] Explain and choose between join strategies.
- [ ] Use broadcast joins and hints correctly.
- [ ] Reduce shuffles in a join-heavy pipeline.

**Common mistakes:** broadcasting large tables; joining before filtering
or aggregating; ignoring skewed keys (Topic 09); ambiguous columns after
self-joins.

---

### Topic 08 — [Partitioning: repartition and coalesce](08-partitioning-repartition-and-coalesce.md)

**Why here:** Partitions decide parallelism in memory and file counts on
disk. Too few partitions waste the cluster; too many drown it in tiny
tasks and tiny files.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | In-memory partitions (units of parallel work) vs on-disk partitions (directories from `partitionBy`, Module 2.5) |
| Basics | Inspecting partitions: `df.rdd.getNumPartitions()` (classic mode), `F.spark_partition_id()` |
| Basics | Partitions on read: file splitting and `spark.sql.files.maxPartitionBytes` |
| Intermediate | Shuffle partitions: `spark.sql.shuffle.partitions` (default 200) and how adaptive execution adjusts it (Topic 13) |
| Intermediate | **`repartition(n)`** and **`repartition(col)`**: full shuffle to rebalance or co-locate keys; `repartitionByRange` for sorted output |
| Intermediate | **`coalesce(n)`**: merge partitions without a full shuffle — cheap, but it can reduce the parallelism of upstream work |
| Intermediate | Choosing partition counts: a rule of thumb of roughly 100–200 MB per partition and a multiple of total cores |
| Advanced | **Controlling output files**: `repartition` by the same columns as `partitionBy` to get one file per directory; `maxRecordsPerFile`; avoiding the small-files problem (Module 2.5) |
| Advanced | `sortWithinPartitions` before writing to improve Parquet statistics and compression |
| Advanced | Partitioning for downstream joins and aggregations (co-partitioned data) |
| Advanced | The cost of unnecessary repartitions |

**How to learn it**

1. Read the topic file.
2. Write the same dataset partitioned by date with no repartition, with
   `coalesce(1)`, with `repartition(200)`, and with `repartition("date")`;
   count files and measure write time.
3. Measure a heavy aggregation with 8, 200, and 2,000 shuffle partitions.

**Hands-on exercise — `src/spark_lab/partitioning.py`**

1. Build a partition report function showing partition count and row
   counts per partition for any DataFrame.
2. Write taxi trips partitioned by `year/month` with a target of 128–512 MB
   files; justify your repartition strategy.
3. Show `coalesce(1)` making an expensive upstream stage single-threaded,
   and fix it with `repartition`.
4. Sort within partitions by a common filter column and measure the effect
   on downstream DuckDB queries (reusing Module 2.5 inspection).
5. Tune `spark.sql.shuffle.partitions` for your main aggregation and record
   the results.

**Checkpoint:**

- [ ] Explain in-memory vs on-disk partitioning.
- [ ] Choose between `repartition` and `coalesce`.
- [ ] Choose partition counts and shuffle partitions.
- [ ] Control output file counts and sizes.

**Common mistakes:** `coalesce(1)` on big data to get "one file"; default
200 shuffle partitions for everything; `partitionBy` without repartitioning
(thousands of tiny files); repartitioning repeatedly "just in case".

---

### Topic 09 — [Data skew and salting](09-data-skew-and-salting.md)

**Why here:** In real data, some keys are huge — one giant customer, a
default "unknown" country, NULLs. One partition gets most of the data, one
task runs for an hour, and the whole job waits.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What skew is: uneven data across partitions, usually from uneven key frequencies |
| Basics | Symptoms: one or a few straggler tasks, huge max vs median task time and shuffle read in the UI, executor out-of-memory on one task |
| Basics | Detecting skew: key frequency counts (`groupBy(key).count().orderBy(desc)`) |
| Intermediate | Common causes: hot keys, NULL or default keys, time-based keys at peak times, bad partitioning columns |
| Intermediate | First fixes: filter or separately handle NULL/default keys; broadcast the smaller side; pre-aggregate |
| Intermediate | **AQE skew join handling** — automatic splitting of skewed partitions (Topic 13) |
| Advanced | **Salting**: adding a random salt to the skewed side's key and replicating the other side across salts; choosing the salt range |
| Advanced | **Isolating hot keys**: processing the top keys separately (e.g. broadcast) and unioning with the rest |
| Advanced | **Two-phase aggregation** for skewed `groupBy`: aggregate by (key, salt), then by key |
| Advanced | Skew in window functions (one enormous partition) and in writes (one huge output directory) |
| Advanced | The cost of salting: more data movement and complexity — measure before and after |

**How to learn it**

1. Read the topic file.
2. Generate a dataset where 1 key holds 30% of rows and 5 keys hold another
   20%; join and aggregate it and study the task-time distribution.
3. Apply each fix one at a time, with AQE on and off, and record results.

**Hands-on exercise — `src/spark_lab/skew.py`**

1. Build a skew detector that reports the top keys and their share of rows,
   and the max/median task time from a run.
2. Fix a skewed join with salting; then with hot-key isolation; then with
   AQE skew handling only. Compare wall time and shuffle volume.
3. Fix a skewed aggregation with two-phase aggregation.
4. Fix a NULL-key skew by handling NULLs separately.
5. Write a decision guide: which fix for which kind of skew.

**Checkpoint:**

- [ ] Recognise skew in the Spark UI.
- [ ] Detect hot keys from data.
- [ ] Fix skew with AQE, broadcasting, salting, isolation, or two-phase
      aggregation.
- [ ] Measure whether a fix actually helped.

**Common mistakes:** adding executors to fix skew (one task is still slow);
salting without measuring; forgetting NULL keys; salting when AQE already
handles the case.

---

### Topic 10 — [Caching and persistence levels](10-caching-and-persistence-levels.md)

**Why here:** Laziness (Topic 04) means reused DataFrames are recomputed.
Caching avoids that — but misused, it wastes memory and slows jobs down.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `cache()` and `persist(StorageLevel...)`; caching is lazy and happens on the first action |
| Basics | `unpersist()` to free memory |
| Basics | The Storage tab: what is cached, fraction cached, memory and disk used |
| Intermediate | Storage levels: memory only, memory and disk, disk only, serialised and replicated variants; the default for DataFrames |
| Intermediate | **When to cache**: a DataFrame used by several actions or branches, iterative algorithms, expensive results reused in the same job |
| Intermediate | **When not to cache**: used once, cheaper to recompute than to store, or bigger than available memory |
| Advanced | Eviction and memory pressure: cached data competing with execution memory |
| Advanced | **Checkpointing** (`checkpoint`, `localCheckpoint`) to truncate long lineage in iterative jobs |
| Advanced | Caching vs writing intermediate results to Parquet (durable, shareable across jobs and restarts) |
| Advanced | Caching behaviour with Spark Connect and on managed platforms (disk caches) — awareness |

**How to learn it**

1. Read the topic file.
2. Run a pipeline that uses one expensive DataFrame in three outputs with
   and without caching; compare time and memory.
3. Cache something larger than executor memory and observe the Storage and
   Executors tabs.

**Hands-on exercise — `src/spark_lab/caching.py`**

1. Build three gold outputs from one expensive silver join; measure with no
   cache, `cache()`, and `persist(DISK_ONLY)`.
2. Show a cache that is never used again and wastes memory; remove it.
3. Build an iterative computation (e.g. repeated enrichment rounds) and
   use checkpointing to keep the plan small.
4. Compare caching with writing the intermediate to Parquet and reading it
   back.
5. Write a caching checklist for your team.

**Checkpoint:**

- [ ] Explain when caching helps and when it hurts.
- [ ] Choose a storage level.
- [ ] Use checkpointing to truncate lineage.
- [ ] Decide between caching and writing intermediates.

**Common mistakes:** caching everything; never unpersisting; caching
before a filter that would shrink the data; expecting `cache()` to run
immediately.

---

## 9. Phase D — Performance Internals (Advanced)

### Topic 11 — [Python UDFs vs pandas UDFs vs built-ins](11-python-udfs-vs-pandas-udfs-vs-built-ins.md)

**Why here:** Sooner or later you need logic Spark does not provide. How
you write it can change a job's run time by 10× or more.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Built-in functions** first: they run in the JVM, are optimised by Catalyst, and support pushdown |
| Basics | **Python UDFs** (`@F.udf`): row-at-a-time, data serialised to Python workers and back — slow and opaque to the optimizer |
| Basics | Declaring return types; NULL handling inside UDFs |
| Intermediate | **Arrow-optimised Python UDFs** (enabling Arrow for Python UDFs) as a cheaper middle ground |
| Intermediate | **pandas UDFs** (`@F.pandas_udf`): vectorised batches via Arrow — Series → Series, iterator of Series (for expensive per-batch set-up such as loading a model), and Series → scalar (aggregations) |
| Intermediate | Group and map functions: `groupBy().applyInPandas()` (one pandas DataFrame per group — e.g. per-group models) and `mapInPandas()` / `mapInArrow()` (per batch) |
| Advanced | **Python UDTFs** (table functions returning multiple rows) and the Python data source API (Spark 4) — awareness and use cases |
| Advanced | Memory risks: `applyInPandas` with a huge group loads it all into one Python worker |
| Advanced | Why UDFs block optimisation (no predicate pushdown through them, no code generation) and how to limit their impact (filter first, UDF last) |
| Advanced | Packaging UDF dependencies for executors (Topic 02) |
| Advanced | Benchmark discipline: the same logic as built-ins, pandas UDF, Arrow UDF, and plain UDF |

**How to learn it**

1. Read the topic file.
2. Implement one piece of logic four ways and benchmark on 100 million
   rows.
3. Look at the plans of each version and find where the Python evaluation
   appears.

**Hands-on exercise — `src/spark_lab/udfs.py`**

1. Implement a phone-number normaliser as: built-in functions
   (`regexp_replace` etc.), a plain Python UDF, an Arrow-optimised UDF, and
   a pandas UDF; benchmark all four.
2. Use an iterator-of-Series pandas UDF to load a lookup model once per
   batch.
3. Fit a tiny per-country trend model with `applyInPandas`.
4. Show a filter after a UDF that cannot be pushed down; move the filter
   before the UDF and measure.
5. Write a rule for your team on when UDFs are allowed.

**Checkpoint:**

- [ ] Explain why built-ins beat UDFs.
- [ ] Write pandas UDFs of each main type.
- [ ] Use `applyInPandas` and `mapInPandas` appropriately.
- [ ] Limit the optimizer impact of unavoidable UDFs.

**Common mistakes:** Python UDFs for string or date logic Spark already
supports; huge groups in `applyInPandas`; UDFs that import heavy libraries
per row.

---

### Topic 12 — [Catalyst optimizer and explain plans](12-catalyst-optimizer-and-explain-plans.md)

**Why here:** Every DataFrame and SQL query passes through the Catalyst
optimizer. Reading its plans is the most reliable way to know what Spark
will actually do — before spending cluster time finding out.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The planning pipeline: parsed (unresolved) logical plan → analysed logical plan → **optimised logical plan** → physical plans → selected **physical plan** → code generation |
| Basics | `df.explain()` and its modes: `simple`, `extended`, `formatted`, `cost`, `codegen` |
| Intermediate | Reading physical plans: `FileScan` (with `PushedFilters`, `PartitionFilters`, `ReadSchema`), `Filter`, `Project`, `Exchange` (shuffle), `BroadcastExchange`, `SortMergeJoin`, `BroadcastHashJoin`, `HashAggregate` (partial and final), `Sort`, `Window` |
| Intermediate | Optimisation rules you can see: predicate pushdown, projection pruning, constant folding, combining filters, join reordering |
| Intermediate | Pushdown to files: which filters reach Parquet (row-group skipping, Module 2.5) and which cannot (UDFs, some casts) |
| Advanced | **Tungsten** and whole-stage code generation (the `*(n)` markers in plans) |
| Advanced | Cost-based optimisation: table and column statistics (`ANALYZE TABLE ... COMPUTE STATISTICS`) and their effect on join choices |
| Advanced | Recognising plan anti-patterns: extra `Exchange` nodes, repeated scans, missing pushdown, Cartesian products |
| Advanced | Comparing Spark plans with DuckDB and Polars plans (Module 2.4) and PostgreSQL plans (Module 2.6) |

**How to learn it**

1. Read the topic file.
2. For ten queries, predict the physical plan nodes, then read
   `explain("formatted")` and compare.
3. Break pushdown on purpose (UDF in a filter, a cast on a partition
   column) and find the difference in the plan.

**Hands-on exercise — `experiments/plans/`**

1. Save formatted plans for every gold query in your pipeline and annotate
   each `Exchange`, join strategy, and pushed filter.
2. Find a query where a filter is not pushed to the scan; rewrite it so it
   is, and measure bytes read.
3. Compute table statistics and show a join strategy change.
4. Identify and remove an unnecessary shuffle.

**Checkpoint:**

- [ ] Explain Catalyst's planning stages.
- [ ] Read a physical plan and identify shuffles, join strategies, and
      pushdown.
- [ ] Explain whole-stage code generation.
- [ ] Use statistics and rewrites to improve plans.

**Common mistakes:** tuning by trial and error without reading plans;
misreading partial and final aggregates as two separate queries; ignoring
`PushedFilters: []`.

---

### Topic 13 — [Adaptive Query Execution](13-adaptive-query-execution.md)

**Why here:** Catalyst plans before running, using estimates. **Adaptive
Query Execution (AQE)** re-plans *during* the run, using real statistics
from completed stages — fixing many problems automatically.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What AQE is: re-optimising the remaining plan at stage boundaries using runtime shuffle statistics; enabled by default in modern Spark |
| Basics | Recognising AQE in plans (`AdaptiveSparkPlan`, final vs initial plan) and in the SQL tab of the UI |
| Intermediate | **Coalescing post-shuffle partitions**: merging tiny shuffle partitions automatically (advisory partition size) |
| Intermediate | **Switching join strategies at runtime**: converting sort-merge joins to broadcast joins when one side turns out small |
| Intermediate | **Skew join optimisation**: splitting skewed partitions (thresholds and factors) |
| Advanced | **Dynamic partition pruning**: skipping partitions of a fact table based on a filtered dimension at runtime |
| Advanced | Key AQE configuration and when to tune it (advisory partition size, skew thresholds, broadcast thresholds) |
| Advanced | What AQE cannot fix: skew within aggregations and windows, bad file layouts, UDF costs, and poor data models |
| Advanced | Interaction with manual tuning: removing hard-coded shuffle partitions and hints that AQE now handles better |

**How to learn it**

1. Read the topic file.
2. Run your skewed join and your many-small-partitions aggregation with AQE
   on and off; compare plans, task counts, and time.
3. Filter a dimension and join it to a partitioned fact table; observe
   dynamic partition pruning.

**Hands-on exercise — `experiments/aqe/`**

1. Build an experiment matrix (AQE on/off × three workloads: many small
   shuffle partitions, a join where one side becomes small after filtering,
   a skewed join) and record results.
2. Tune advisory partition size for your main job and measure.
3. Demonstrate dynamic partition pruning with a star-schema query on
   partitioned data.
4. Remove manual tuning that AQE makes unnecessary and confirm no
   regression.

**Checkpoint:**

- [ ] Explain what AQE changes at runtime.
- [ ] Identify AQE decisions in plans and the UI.
- [ ] Explain dynamic partition pruning.
- [ ] Explain the limits of AQE.

**Common mistakes:** disabling AQE because an old guide said so; manual
partition counts and hints fighting AQE; expecting AQE to fix data-model
problems.

---

## 10. Phase E — Production I/O and Operations (Advanced)

### Topic 14 — [Data sources, save modes, and bucketing](14-data-sources-save-modes-and-bucketing.md)

**Why here:** Every Spark pipeline begins with a read and ends with a
write. Getting them right decides correctness (no duplicated or lost
data), cost (bytes scanned), and reliability.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `DataFrameReader` and `DataFrameWriter`: `format`, `option`, `schema`, `load`, `save`; Parquet, ORC, JSON, CSV, text, and Avro (via its package) |
| Basics | **Save modes**: `append`, `overwrite`, `ignore`, `errorifexists` — and why `overwrite` can be dangerous |
| Basics | Writing partitioned output with `partitionBy` (layout rules from Module 2.5) |
| Intermediate | **Explicit schemas** on read and handling bad records: `PERMISSIVE` (with a corrupt-record column), `DROPMALFORMED`, `FAILFAST` — connecting to quarantine (Module 2.11) |
| Intermediate | **Dynamic partition overwrite** (`partitionOverwriteMode=dynamic`): replacing only the partitions present in the output — the idempotent partition overwrite from Module 2.12 |
| Intermediate | **JDBC sources**: parallel reads with `partitionColumn`, `lowerBound`, `upperBound`, `numPartitions`, and `fetchsize`; pushdown of filters; batched writes — and protecting the source database (Module 2.7) |
| Intermediate | Object storage with S3A: credentials providers (no keys in code), performance options, and output committers |
| Intermediate | `saveAsTable` vs `save` vs `insertInto`, and the catalog |
| Advanced | **Bucketing**: `bucketBy` + `sortBy` + `saveAsTable` to pre-shuffle data so later joins and aggregations on the bucket key avoid shuffles; limitations (tables only, matching bucket counts, compatibility across engines) |
| Advanced | Why plain file writes are not atomic on object storage (partial outputs after failures, concurrent readers) — the motivation for lakehouse table formats (Module 2.15) |
| Advanced | Custom data sources with the Python data source API (Spark 4) — awareness, e.g. reading from your mock API |
| Advanced | Reading many small files efficiently and compacting outputs (Module 2.5) |

**How to learn it**

1. Read the topic file.
2. Re-run a daily job twice with `append`, `overwrite` (static), and
   dynamic partition overwrite; compare the resulting data.
3. Read a PostgreSQL table with one JDBC partition and with 16; watch the
   source database's connections (Module 2.7) and time.

**Hands-on exercise — `jobs/io_patterns.py`**

1. Read raw CSV/JSON with explicit schemas and `PERMISSIVE` mode; route
   corrupt records to a quarantine path.
2. Write silver with dynamic partition overwrite by date and prove re-runs
   are idempotent.
3. Extract a 50-million-row PostgreSQL table in parallel via JDBC with a
   bounded number of connections; compare with your Module 2.7 extractor.
4. Bucket two large tables on `customer_id` and show a shuffle-free join in
   the plan; compare with the unbucketed version.
5. Read and write MinIO via S3A with credentials from environment
   variables.
6. Kill a write mid-way and inspect what readers see — write down why this
   motivates Module 2.15.

**Checkpoint:**

- [ ] Read with explicit schemas and handle corrupt records.
- [ ] Choose save modes and use dynamic partition overwrite for idempotent
      writes.
- [ ] Read from JDBC in parallel without overloading the source.
- [ ] Explain and use bucketing.
- [ ] Explain the atomicity problem of plain file outputs.

**Common mistakes:** static `overwrite` wiping a whole table on a
single-day rerun; JDBC reads with one partition (or 200 connections);
schema inference in production; credentials in job code.

---

### Topic 15 — [Spark UI and debugging slow jobs](15-spark-ui-and-debugging-slow-jobs.md)

**Why here:** Knowing the theory is not enough; production Spark work is
diagnosis. The Spark UI shows exactly where time and memory went — if you
know how to read it.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Spark UI tabs: **Jobs**, **Stages**, **Storage**, **Environment**, **Executors**, and **SQL / DataFrame** |
| Basics | Finding the slowest job and stage; task summary metrics (min, median, max) |
| Basics | Driver and executor logs; setting log levels |
| Intermediate | Reading stage details: task-time distribution, shuffle read/write, input size, **spill** (memory and disk), GC time |
| Intermediate | The SQL tab: the query plan graph with runtime metrics per operator |
| Intermediate | The **history server** and event logs for finished jobs |
| Intermediate | A **debugging method**: slowest stage → why (skew? spill? too few or too many tasks? big shuffle? UDF?) → one change → measure |
| Advanced | Common failures and their signatures: driver out-of-memory (`collect`, huge broadcasts), executor out-of-memory (skew, large partitions), container killed for exceeding memory overhead (Python workers), shuffle fetch failures, lost executors, serialisation errors |
| Advanced | Long GC pauses, too many small tasks, stragglers and speculative execution |
| Advanced | Collecting metrics programmatically (listeners, REST API, or metrics libraries) for dashboards and regression tracking (Module 2.20) |
| Advanced | Writing a performance investigation report: symptoms, evidence, cause, fix, measured result |

**How to learn it**

1. Read the topic file.
2. For every problem you created in Topics 07–13 (skew, bad partitioning,
   UDFs, missing broadcast, over-caching), find its signature in the UI and
   write it down.
3. Configure the history server so you can study past runs.

**Hands-on exercise — `experiments/debugging/`**

1. Run a deliberately bad job (skewed join, UDF-heavy filter, `coalesce(1)`
   upstream, 2,000 shuffle partitions on small data, unnecessary cache) and
   diagnose each problem only from the Spark UI and logs.
2. Reproduce a driver OOM, an executor OOM, and a memory-overhead container
   kill; document each error message and fix.
3. Fix the job step by step, recording time and resource use after each
   fix.
4. Write a one-page investigation report and a "Spark debugging checklist"
   for your team.

**Checkpoint:**

- [ ] Navigate every Spark UI tab and the history server.
- [ ] Diagnose skew, spill, partitioning problems, and UDF costs from the
      UI.
- [ ] Identify the cause of common memory failures.
- [ ] Follow a repeatable debugging method.

**Common mistakes:** adding memory or executors without diagnosis; looking
only at total job time; ignoring spill and GC metrics; no event logs, so
failed production runs cannot be investigated.

---

### Topic 16 — [Testing PySpark code](16-testing-pyspark-code.md)

**Why last:** Spark code is notoriously hard to test when business logic
is tangled with sessions and I/O. With the structure from Module 2.12 and
the right fixtures, it is fast and reliable.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Testable structure: pure `DataFrame → DataFrame` functions; I/O and session creation in thin job entry points |
| Basics | A **session-scoped pytest fixture** creating a local `SparkSession` (small shuffle partitions, UI off, UTC time zone) |
| Basics | Building small test DataFrames with explicit schemas |
| Intermediate | Comparing results: `pyspark.testing.assertDataFrameEqual` and `assertSchemaEqual` (order-insensitive options, tolerances for floats) |
| Intermediate | Testing edge cases: NULLs, empty DataFrames, duplicates, time-zone boundaries, ANSI-mode errors |
| Intermediate | Testing UDFs directly as Python functions and inside Spark |
| Intermediate | Testing SQL transformations registered as temporary views |
| Advanced | Integration tests: running a whole job against local files or MinIO and checking outputs and quality rules (Pandera's PySpark support from Module 2.11) |
| Advanced | **Plan regression tests**: asserting that key queries still use broadcast joins or pushed filters |
| Advanced | Keeping the suite fast: one session per test run, tiny data, parallel test processes, and Spark Connect for lighter clients |
| Advanced | Property-based testing of transformations (Module 2.19) |

**How to learn it**

1. Read the topic file.
2. Take one of your earlier jobs and refactor it until every transformation
   is testable without I/O.
3. Measure your test suite's run time and cut it in half.

**Hands-on exercise — `tests/`**

1. Create a `spark` session fixture in `conftest.py`.
2. Unit-test every silver and gold transformation with small handwritten
   DataFrames and `assertDataFrameEqual`, including NULL, empty, and
   duplicate cases.
3. Test your UDFs and pandas UDFs.
4. Write a plan regression test asserting the fact-to-dimension join is a
   broadcast join.
5. Write an integration test running the full daily job on a sample
   dataset in MinIO and validating outputs with Pandera.
6. Keep the whole suite under a target run time (for example 2 minutes).

**Checkpoint:**

- [ ] Structure Spark code for testability.
- [ ] Write fast unit tests with a shared session fixture.
- [ ] Compare DataFrames and schemas correctly.
- [ ] Write integration and plan regression tests.

**Common mistakes:** a new `SparkSession` per test; testing only whole jobs
end to end; comparing DataFrames with order-sensitive `collect()`; tests
that depend on 200 default shuffle partitions and run slowly.

---

## 11. Consolidate — practice questions and interview practice

### [`practice-questions.md`](practice-questions.md)

For every question:

1. Estimate data sizes and the cluster needed (or whether Spark is needed
   at all).
2. Predict jobs, stages, shuffles, and join strategies.
3. Write the solution as pure, tested transformations.
4. Read the plan before running; run on the cluster; read the UI.
5. Tune one thing at a time and record the evidence.
6. Verify results against a single-node engine on a sample.

### [`interview-practice.md`](interview-practice.md)

Spark questions appear in most data engineering interviews. Practise
answers out loud, with diagrams, and with a **20-minute timer** for
scenario questions.

Typical concept questions: driver vs executor; job vs stage vs task;
narrow vs wide transformations; transformations vs actions; RDD vs
DataFrame; `repartition` vs `coalesce`; `cache` vs `persist`; broadcast
join and when it fails; sort-merge vs broadcast hash join; what AQE does;
how Catalyst optimises; Python UDF vs pandas UDF; client vs cluster mode;
save modes and dynamic partition overwrite; bucketing.

Typical scenario questions: "one task takes 90% of the job time — what do
you do?", "the job fails with executor out-of-memory", "the job writes
50,000 tiny files", "a nightly job got 3× slower this week", "join a
10 TB table with a 50 MB table", "deduplicate 5 billion events keeping the
latest per key", "design a daily batch pipeline on Spark for a lakehouse",
and "when would you not use Spark?".

---

## 12. Module mini-project — a tuned, tested Spark pipeline at scale

This is the proof that you have finished the module.

**Scenario:** The single-node pipeline from Modules 2.4 and 2.12 must now
process several years of history (tens to hundreds of GB — NYC taxi trips
or TPC-H-style data plus your orders sources) nightly, with backfills,
within a fixed time budget on a small cluster.

Build `spark_pipeline/` with:

1. **Cluster and packaging** — a Docker standalone cluster (or local mode
   with realistic settings), `spark-defaults.conf` per environment, and a
   packaged job submitted with `spark-submit` in cluster mode.
2. **Ingestion** — parallel JDBC extraction from PostgreSQL (bounded
   connections) and raw file reads from MinIO with explicit schemas and
   corrupt-record quarantine.
3. **Silver** — pure DataFrame transformations (types with ANSI-safe
   casts, deterministic deduplication with windows, hash keys from Module
   2.12, complex-type parsing) chained with `.transform()`.
4. **Gold** — Spark SQL and DataFrame aggregations with broadcast
   dimension joins, window functions, and one pandas UDF where no built-in
   exists.
5. **Performance** — a deliberately skewed join fixed with AQE and/or
   salting, partition tuning for output files of 128–512 MB, justified
   caching, bucketed tables for a repeated large join, and annotated plans
   for every gold query.
6. **Writes** — dynamic partition overwrite for idempotent daily runs and
   backfills; a demonstration of the atomicity problem to hand over to
   Module 2.15.
7. **Operations** — history server enabled, a performance investigation
   report with before/after metrics, and a Spark debugging checklist.
8. **Tests** — unit tests for every transformation and UDF, a plan
   regression test, and an integration test on sample data with Pandera
   validation.
9. **Orchestration (optional)** — an Airflow DAG from Module 2.13 that
   submits the job per data interval and runs a backfill.

**Grading yourself:** the nightly run meets its time budget; re-running any
day or backfilling a month produces identical outputs; every tuning
decision is backed by plans and Spark UI evidence; and the test suite runs
in minutes, not hours.

---

## 13. Module self-assessment — exit criteria

Only move to Module 2.15 when you can tick every box without looking at your
notes:

- [ ] I can explain Spark's architecture and execution hierarchy.
- [ ] I can configure, size, package, and submit Spark jobs.
- [ ] I can explain RDDs vs DataFrames and lazy evaluation.
- [ ] I can write production transformations with the DataFrame API and
      Spark SQL.
- [ ] I can control joins, shuffles, and partitioning.
- [ ] I can detect and fix data skew.
- [ ] I can decide when to cache, persist, or checkpoint.
- [ ] I can choose between built-ins, pandas UDFs, and Python UDFs with
      evidence.
- [ ] I can read Catalyst plans and explain what AQE changed.
- [ ] I can read and write data sources idempotently, including JDBC and
      bucketed tables.
- [ ] I can debug slow and failing jobs with the Spark UI.
- [ ] I can test PySpark code quickly and reliably.
- [ ] I have finished the practice questions, interview practice, and the
      mini-project.

---

## 14. Recommended reading and references

| Resource | Relevant topics |
| --- | --- |
| Apache Spark documentation (4.x) — PySpark user guide, SQL/DataFrame guide, performance tuning, configuration, monitoring, Spark Connect, migration guide | All topics |
| PySpark API reference — `pyspark.sql.functions`, pandas UDFs, `pyspark.testing` | 05, 11, 16 |
| *Learning Spark*, 2nd edition — Jules S. Damji, Brooke Wenig, Tathagata Das, Denny Lee (O'Reilly) | 01–14 |
| *Spark: The Definitive Guide* — Bill Chambers and Matei Zaharia (O'Reilly) — older but excellent on fundamentals | 01–10, 14 |
| *High Performance Spark*, 2nd edition — Holden Karau, Adi Polak, Rachel Warren (O'Reilly) | 07–13, 15 |
| Databricks and Apache Spark blog posts on Adaptive Query Execution and Catalyst | 12, 13 |
| *Designing Data-Intensive Applications* — Martin Kleppmann, chapter on batch processing | 01, 04, 07 |

---

## 15. Where this module leads

| This module's idea | Where it goes deeper |
| --- | --- |
| Atomic writes, `MERGE`, time travel, compaction, Z-ordering | 2.15 Lakehouse Table Formats |
| Structured Streaming with the same DataFrame API | 2.16 Streaming and Event-Driven Data |
| Managed Spark platforms (Databricks, EMR, Dataproc) and cloud storage | 2.17 Cloud Storage and Cloud Data Platforms |
| Spark on Kubernetes and container images for jobs | 2.18 Containers, Infrastructure, and CI/CD for Data |
| Property-based and integration testing of Spark jobs | 2.19 Testing Data Pipelines |
| Spark metrics, lineage, and job observability | 2.20 Observability, Lineage, Governance, and Security |
| Dask and Ray as alternatives; compute cost optimisation | 2.21 Performance, Scaling, and Cost Optimization |
| Feature pipelines and embedding generation at scale | 2.22 Serving Data for Analytics, ML, and AI |

Spark rewards engineers who think about **where data moves** rather than
just what the code says. The habits you build here — predict the stages,
read the plan, find the shuffle, look for skew, measure every change, and
keep transformations pure and tested — will make you effective on any
distributed engine you meet next.
