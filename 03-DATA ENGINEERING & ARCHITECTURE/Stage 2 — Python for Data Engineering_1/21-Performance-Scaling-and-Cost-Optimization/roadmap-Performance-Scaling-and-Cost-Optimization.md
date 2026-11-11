# Roadmap — Module 2.21: Performance, Scaling, and Cost Optimization

This is the learning roadmap for the twenty-first module of Stage 2,
**Python for Data Engineering**. It tells you **what** to learn about
making data pipelines fast, scalable, and affordable, **in what order**,
**how** to learn each topic, and **how to prove to yourself** that you have
learned it before you move on.

Every earlier module contained a piece of performance work: vectorising
NumPy (2.2), shrinking pandas memory (2.3), lazy plans and streaming in
Polars and DuckDB (2.4), Parquet layout (2.5), indexes and plans (2.6),
concurrency (2.10), Spark tuning (2.14), compaction and clustering (2.15),
and warehouse and storage costs (2.17). This module turns those pieces into
a **discipline**:

1. **Estimate** before you build — how big is the data, how much memory,
   how long, how much money?
2. **Read less** — push filters and column selection as close to the data
   as possible.
3. **Scale out** only when needed, with the right tool (Dask, Ray, Spark).
4. **Speed up the hot path** only where profiling proves it matters.
5. **Measure** every claim with honest benchmarks.
6. **Pay less** by making cost visible and optimising it continuously.

The rule behind all of it: **do not optimise what you have not measured,
and do not scale what you could simply make smaller.**

---

## 1. Module outcome

By the end of this module you will be able to:

- Estimate data sizes, memory footprints, run times, and throughput for a
  workload **before** running it, and check the estimate against reality.
- Audit any pipeline for **predicate pushdown and projection pruning**
  across files, table formats, databases, warehouses, and APIs — and fix
  what blocks it.
- Scale pandas-style and custom Python workloads with **Dask**.
- Use **Ray** and **Ray Data** for distributed Python, ML preprocessing, and
  batch inference.
- Accelerate unavoidable Python hot loops with **Numba** and **Cython** (and
  know the alternatives).
- Design and run **reproducible benchmarks**, detect performance
  regressions in CI, and report results honestly.
- Make compute **cost visible** per pipeline and dataset, and reduce it with
  right-sizing, pricing models, scheduling, and better engine choices.

---

## 2. Prerequisites

This module builds on earlier stages and Modules 2.1–2.20. It does **not**
re-teach them.

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| CPU, caches, RAM, storage, GPUs | Stage 0 — How Computers Work | The physical limits behind every estimate |
| Virtual memory, processes, scheduling | Stage 0 — OS Fundamentals | Memory limits, OOM kills, and CPU sharing |
| Big-O time and space complexity | Stage 1 — Module 1.4 | Estimating how work grows |
| Generators and memory trade-offs | Stage 1 — Module 1.9 | Streaming instead of loading |
| **Profiling and measuring before optimising** | Stage 1 — Module 1.10 | Basic profiling (`cProfile`, `timeit`) is **not** re-taught |
| dtypes, vectorisation, views, memory | Stage 2 — Modules 2.2–2.3 | Memory estimates and vectorised baselines |
| Polars lazy plans, streaming, DuckDB, engine choice | Stage 2 — Module 2.4 | Single-node alternatives to scaling out |
| Parquet internals, statistics, partitioning, compression | Stage 2 — Module 2.5 | The physical basis of pushdown |
| `EXPLAIN` plans, indexes | Stage 2 — Module 2.6 | Database-side pushdown |
| Threads, processes, asyncio, Amdahl's law, free-threading | Stage 2 — Module 2.10 | Parallelism basics **not** re-taught |
| Incremental processing | Stage 2 — Module 2.12 | Processing less data per run |
| Spark partitioning, skew, UDFs, AQE, Spark UI | Stage 2 — Module 2.14 | Spark tuning **not** re-taught; compared with Dask and Ray |
| Table-format metadata pruning, compaction, clustering | Stage 2 — Module 2.15 | Lakehouse pushdown |
| Warehouse pricing, managed Spark, storage classes | Stage 2 — Module 2.17 | Cost models used here |
| Kubernetes resources and autoscaling | Stage 2 — Module 2.18 | Right-sizing containers and clusters |
| Test-data tiers, property tests | Stage 2 — Module 2.19 | Benchmark inputs and correctness of optimised code |
| Metrics, dashboards, cost alerts | Stage 2 — Module 2.20 | Performance and cost observability |

**Tools needed:**

- Python 3.12+ in a `uv` project: `uv add "dask[complete]" "ray[data]"
  numba cython polars duckdb pyarrow pandas psutil` and `uv add --dev
  memray scalene py-spy pyperf pytest-benchmark asv` (check platform
  support for each tool).
- `hyperfine` for benchmarking command-line jobs, and `/usr/bin/time -v`
  (Linux) for peak memory.
- Your platform code, datasets (tiny, small, large tiers from Module 2.19),
  a Spark environment (Module 2.14), and your cloud account with billing
  data and cost tags (Module 2.17).

---

## 3. How the module is organised

The seven topics are grouped into four phases. Work through them **in
order**.

```text
Phase A — Understand and Shrink the Workload        (Basics → Intermediate)
  01 Estimating data size and memory footprint
  02 Predicate pushdown and projection pruning

Phase B — Scale Out Python                          (Intermediate → Advanced)
  03 Parallel DataFrames with Dask
  04 Ray Data overview

Phase C — Speed Up the Hot Path                     (Advanced)
  05 Numba and Cython for hot loops

Phase D — Prove It and Pay Less                     (Advanced)
  06 Benchmarking pipelines
  07 Compute cost optimization

Consolidate
  practice-questions.md
  Module mini-project: a performance and cost review of the platform
```

The optimisation ladder this module follows — always try the cheaper rung
first:

```text
1. Do less work        → incremental processing, read fewer rows and columns (01–02)
2. Use a better engine → vectorised / columnar single-node engines (Module 2.4)
3. Use more cores      → threads, processes (Module 2.10)
4. Use more machines   → Dask, Ray, Spark (03–04, Module 2.14)
5. Compile hot loops   → Numba, Cython (05)
   … and at every rung: measure (06) and price it (07)
```

The dependency chain:

```text
01 ──► 02 ──► 03 ──► 04 ──► 05 ──► 06 ──► 07
size    read   scale    scale    compile   prove    pay
it      less   frames   Python   the loop  it       less
```

Why this order:

- Estimation (01) tells you whether you even have a scaling problem.
- Pushdown (02) is the cheapest, biggest win and must come before scaling
  out — scaling a wasteful scan only makes it more expensive.
- Dask (03) and Ray (04) are the Python-native scale-out options; they are
  compared with Spark from Module 2.14.
- Compiling hot loops (05) is a narrow tool used after profiling.
- Benchmarking (06) formalises the measurement you have been doing
  informally in 01–05; cost optimisation (07) turns performance into money
  and closes the module.

---

## 4. Suggested schedule

About **4 weeks at 8–10 hours per week**.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — estimation and memory · Topic 02 — pushdown and pruning |
| 2 | Topic 03 — Dask · Topic 04 — Ray Data |
| 3 | Topic 05 — Numba and Cython · Topic 06 — benchmarking |
| 4 | Topic 07 — compute cost optimisation · practice questions · mini-project |

---

## 5. How to study every topic (the performance loop)

```text
Read → State the goal (time, memory, cost) → Estimate → Measure the baseline
→ Profile to find the bottleneck → Change one thing → Verify correctness
→ Measure again → Price it → Write it down → Explain aloud
```

1. **Read** the topic file once, fully.
2. **State the goal** as a number: "nightly run under 20 minutes", "peak
   memory under 4 GB", "cost per run under $2".
3. **Estimate** the expected size, time, and cost before running.
4. **Measure the baseline** (wall time, CPU, peak memory, bytes read, cost)
   on representative data.
5. **Profile** to find where time and memory actually go.
6. **Change one thing** at the bottleneck — never several at once.
7. **Verify correctness**: the optimised output must equal the baseline
   (Module 2.19 comparison helpers).
8. **Measure again** with the same method and compare.
9. **Price it**: what does the change save (or cost) per run and per month?
10. **Write down** the result in `module-2.21-notes.md`, including failed
    attempts.
11. **Explain aloud** why the change helped, using profiler and plan
    evidence.

Keep one `perf_lab/` project:

```text
perf_lab/
├── workloads/        # the pipelines and steps under study
├── estimates/        # size, memory, time, and cost estimates (Markdown or notebooks)
├── benchmarks/       # benchmark harness, configs, and result history
├── profiles/         # saved profiler outputs and flame graphs
├── cost/             # billing exports, cost models, and reports
└── tests/            # correctness tests for optimised code
```

---

## 6. Phase A — Understand and Shrink the Workload (Basics → Intermediate)

### Topic 01 — [Estimating data size and memory footprint](01-estimating-data-size-and-memory-footprint.md)

**Why it comes first:** Many "we need a cluster" decisions are wrong
because nobody estimated the data. A five-minute calculation often shows
that the job fits on one machine — or that it never will.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Back-of-the-envelope sizing**: rows × columns × bytes per value, by dtype (Module 2.2) |
| Basics | Size on disk vs in memory: compression and encoding ratios in Parquet (Module 2.5) vs the expanded in-memory size |
| Basics | Measuring actual memory: process resident memory (`psutil`), peak memory (`/usr/bin/time -v`), and engine-reported sizes (`memory_usage`, `estimated_size`, Arrow `nbytes`) |
| Intermediate | **Expansion factors**: CSV to pandas `object` columns, strings as Python objects vs Arrow strings, categorical savings |
| Intermediate | **Peak memory multipliers** of operations: copies, joins (both sides plus output), sorts, group-bys with many groups, pivots, and `toPandas`/`collect` |
| Intermediate | **Memory profiling** beyond Stage 1: `memray` (allocation tracking, flame graphs, native allocations) and `scalene` (CPU, memory, and copy profiling) |
| Intermediate | Containers and memory limits: cgroup limits, the OOM killer, and why a job can be killed without a Python traceback |
| Advanced | **Throughput and latency reference numbers**: memory bandwidth, local SSD, network, and object-storage throughput per connection — and estimating run time from bytes ÷ throughput |
| Advanced | Estimating distributed jobs: bytes per partition, executor memory, shuffle volume (Module 2.14) |
| Advanced | **Capacity planning**: growth rates, peak vs average days, and headroom |
| Advanced | The scaling decision: fits in memory → single node; fits on disk of one machine with streaming → single-node out-of-core (Module 2.4); otherwise → distributed |

**How to learn it**

1. Read the topic file.
2. Before loading five datasets, estimate their on-disk and in-memory sizes;
   then measure and record the error of each estimate.
3. Profile a join-heavy pandas step with `memray` and identify the
   allocation that sets peak memory.

**Hands-on exercise — `estimates/` and `workloads/memory/`**

1. Build a sizing spreadsheet or script: given a schema, row count, and
   compression ratio, estimate disk size, pandas size, Arrow/Polars size,
   and peak memory for a join and a group-by.
2. Validate it against real measurements for three datasets.
3. Profile one memory-hungry pipeline step with `memray` and `scalene`;
   reduce its peak memory by at least 50% using earlier techniques (dtypes,
   streaming, fewer copies) and prove it.
4. Run the step in a container with a memory limit below its old peak and
   show the OOM kill; then show the fixed version succeeding.
5. Estimate the run time of a full-lake scan from S3 using throughput
   numbers; compare with the real run.
6. Write a one-page capacity plan for your platform for the next 12 months.

**Checkpoint — you are ready to move on when you can:**

- [ ] Estimate data size on disk and in memory for any schema.
- [ ] Explain the peak memory of common operations.
- [ ] Profile memory with `memray` or `scalene`.
- [ ] Estimate run time from data volume and throughput.
- [ ] Decide single node vs distributed from estimates.

**Common mistakes:** confusing compressed file size with memory size;
estimating average memory instead of peak; ignoring container limits;
scaling out before estimating.

---

### Topic 02 — [Predicate pushdown and projection pruning](02-predicate-pushdown-and-projection-pruning.md)

**Why here:** The fastest data is data you never read. Pushdown and
pruning are the single biggest performance and cost lever in modern data
platforms — and they break silently.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Projection pruning**: reading only the columns a query needs |
| Basics | **Predicate pushdown**: applying filters as early as possible — ideally inside the storage layer, so rows are never read |
| Basics | **Partition pruning**: skipping whole partitions from partition values |
| Intermediate | The **pushdown stack** end to end: API filters (Module 2.9) → database `WHERE` clauses and JDBC pushdown (Modules 2.6, 2.14) → table-format metadata (manifests and file statistics, Module 2.15) → Parquet row-group statistics, page indexes, and bloom filters (Module 2.5) → in-engine filters |
| Intermediate | **Verifying** pushdown in each engine: Polars `explain()`, DuckDB `EXPLAIN ANALYZE`, Spark `PushedFilters`/`PartitionFilters`, PyArrow dataset filters, warehouse bytes-scanned statistics |
| Intermediate | **What breaks pushdown**: Python UDFs, functions or casts applied to filtered columns, filters on derived columns instead of partition columns, type mismatches, `OR` across columns, and filters applied after a collect |
| Intermediate | **Layout that enables pushdown**: sorting and clustering by filter columns so statistics are selective |
| Advanced | Limit, aggregate, and join pushdown; **dynamic filtering / runtime filters** (e.g. dynamic partition pruning, Module 2.14) |
| Advanced | Late materialisation: reading filter columns first, the rest only for matching rows |
| Advanced | **Scan audits**: measuring bytes scanned vs bytes needed for each production query or job, and finding the worst offenders |
| Advanced | Pushdown and cost: bytes-scanned pricing (Module 2.17) makes pruning a direct cost saving |

**How to learn it**

1. Read the topic file.
2. For one question ("revenue for one country last week"), trace the query
   through every layer of your platform and record what each layer skips.
3. Break pushdown in five different ways and fix each, measuring bytes read.

**Hands-on exercise — `workloads/pushdown/`**

1. Build a **scan audit** script: for your ten most frequent queries or
   jobs, record bytes scanned (from plans, engine metrics, or warehouse
   query history) and bytes in the final result.
2. Fix the three worst offenders (e.g. add partition filters, remove a UDF
   from a filter, avoid casting a partition column, cluster a table by a
   filter column).
3. Demonstrate pushdown at every layer for one query: API filter,
   PostgreSQL `WHERE`, Iceberg manifest pruning, Parquet row-group skipping,
   and column pruning — with evidence from each engine.
4. Show a dynamic partition pruning example in Spark or DuckDB.
5. Compute the cost saving of the fixes under bytes-scanned pricing.

**Checkpoint:**

- [ ] Explain projection pruning, predicate pushdown, and partition pruning.
- [ ] Verify pushdown in Polars, DuckDB, Spark, PyArrow, and a warehouse.
- [ ] Identify and fix what blocks pushdown.
- [ ] Run a scan audit and quantify savings.

**Common mistakes:** `SELECT *`; wrapping partition columns in functions;
filtering after loading data into pandas; assuming pushdown happened
without checking the plan.

---

## 7. Phase B — Scale Out Python (Intermediate → Advanced)

### Topic 03 — [Parallel DataFrames with Dask](03-parallel-dataframes-with-dask.md)

**Why here:** When data or computation outgrows one core or one machine,
Dask scales familiar pandas and NumPy code — and arbitrary Python — without
leaving the Python ecosystem or moving to the JVM.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Dask's collections: **DataFrame** (partitioned pandas), **Array** (chunked NumPy), **Bag**, plus `dask.delayed` and futures for custom work |
| Basics | Lazy task graphs and `.compute()` / `.persist()` |
| Basics | Schedulers: threaded, multiprocessing, and the **distributed** scheduler (`LocalCluster`, `Client`) with its **dashboard** |
| Intermediate | Partitions: choosing partition sizes, `repartition`, and reading Parquet with column selection and filters |
| Intermediate | Dask DataFrame's query optimiser (expression-based planning with projection and predicate pushdown in current versions) — and checking what it did |
| Intermediate | Operations that are cheap (row-wise, per-partition, reductions) vs expensive (**shuffles**: `set_index`, joins on unsorted keys, some group-bys) |
| Intermediate | `dask.delayed` and futures for parallelising custom pipelines (e.g. one task per file, per source, per partition) |
| Advanced | Memory management on workers: spilling, pausing, and avoiding huge partitions; the dashboard's memory and task-stream views |
| Advanced | Deploying Dask: on Kubernetes, on cloud VMs, or managed services — awareness |
| Advanced | Dask vs Spark vs Polars/DuckDB: when each fits (Python-native ecosystems and custom logic vs SQL-heavy ETL vs single-node speed) |
| Advanced | Pitfalls: pandas semantics that do not scale (index-heavy code, row-wise `apply`), too many tiny partitions, and computing the same graph twice |

**How to learn it**

1. Read the topic file.
2. Port a pandas pipeline from Module 2.3 to Dask and watch it run in the
   dashboard.
3. Compare the same workload in pandas, Dask (local cluster), Polars, and
   Spark local mode.

**Hands-on exercise — `workloads/dask/`**

1. Run a daily aggregation over several years of Parquet with Dask
   DataFrame using column selection and filters; confirm pushdown and
   inspect the dashboard.
2. Tune partition sizes and measure the effect.
3. Trigger an expensive shuffle (`set_index` on an unsorted column) and
   compare with an approach that avoids it.
4. Parallelise a per-file custom validation pipeline with `dask.delayed` or
   futures.
5. Benchmark against Polars (single node) and Spark on the same data and
   write a recommendation.

**Checkpoint:**

- [ ] Use Dask DataFrame, Array, delayed, and futures.
- [ ] Run a distributed local cluster and read its dashboard.
- [ ] Choose partition sizes and avoid unnecessary shuffles.
- [ ] Decide between Dask, Spark, and single-node engines.

**Common mistakes:** Dask for data that Polars handles on one machine;
millions of tiny tasks; pandas-style index manipulation at scale; calling
`.compute()` repeatedly on the same graph.

---

### Topic 04 — [Ray Data overview](04-ray-data-overview.md)

**Why here:** Ray is a general distributed Python framework widely used for
ML and AI workloads. **Ray Data** handles large-scale data loading,
preprocessing, and batch inference — the bridge between data engineering
and ML (Module 2.22).

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Ray core: **tasks** (remote functions), **actors** (stateful workers), and the distributed **object store** |
| Basics | Starting Ray locally and the Ray dashboard |
| Basics | **Ray Data** datasets: reading Parquet, CSV, and images; transformations with `map_batches` (batches as pandas, PyArrow, or NumPy) |
| Intermediate | **Streaming execution**: data flows through stages in blocks without materialising everything; back pressure between stages |
| Intermediate | **Resources**: CPUs and GPUs per task or actor, and mixing CPU preprocessing with GPU inference in one pipeline |
| Intermediate | Stateful batch processing with **actor pools** (load a model once per actor, then process many batches) |
| Intermediate | Typical uses: ML preprocessing, **batch inference**, embedding generation (Module 2.22), and feeding training jobs |
| Advanced | Writing outputs (Parquet, lakehouse tables) and integrating with orchestration (Module 2.13) |
| Advanced | Deploying Ray clusters (e.g. on Kubernetes with an operator) and autoscaling — awareness |
| Advanced | Ray Data vs Spark vs Dask: GPU-heavy, Python/ML-heavy workloads vs SQL-style ETL with large joins and aggregations |
| Advanced | Limits: Ray Data is not a SQL engine; heavy relational work usually belongs in Spark, DuckDB, or a warehouse |

**How to learn it**

1. Read the topic file.
2. Run a small Ray program with tasks and an actor; observe scheduling in
   the dashboard.
3. Build a Ray Data pipeline that reads Parquet, transforms batches, and
   writes Parquet; watch streaming execution.

**Hands-on exercise — `workloads/ray/`**

1. Build a Ray Data pipeline that reads product descriptions from Parquet,
   cleans text in CPU batches, computes embeddings with a small model in an
   actor pool (CPU is fine; GPU if available), and writes results to
   Parquet.
2. Tune batch size and actor count; measure throughput and memory.
3. Implement the same pipeline with Spark pandas UDFs (Module 2.14) and
   compare code, throughput, and resource usage.
4. Trigger the pipeline from an orchestrator task with a data interval.
5. Write a decision note: Ray Data, Spark, or Dask for three workloads.

**Checkpoint:**

- [ ] Explain Ray tasks, actors, and the object store.
- [ ] Build streaming Ray Data pipelines with `map_batches`.
- [ ] Use actor pools for model-based batch processing.
- [ ] Choose between Ray, Spark, and Dask.

**Common mistakes:** loading a model inside every batch call instead of per
actor; huge batches that exhaust memory; using Ray Data for join-heavy SQL
work.

---

## 8. Phase C — Speed Up the Hot Path (Advanced)

### Topic 05 — [Numba and Cython for hot loops](05-numba-and-cython-for-hot-loops.md)

**Why here:** Some logic cannot be vectorised: sequential state machines,
custom sessionisation, unusual parsing, complex scoring. When profiling
proves a Python loop is the bottleneck, compiling it can make it 10–100×
faster.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | When to compile: after profiling shows a hot loop, and after trying vectorised NumPy, Polars expressions, or SQL first |
| Basics | **Numba**: `@njit` just-in-time compilation of numeric Python on NumPy arrays; nopython mode; supported types and features |
| Basics | Compile time vs run time; `cache=True` to reuse compiled code |
| Intermediate | Parallel loops with `parallel=True` and `prange`; creating custom ufuncs with `@vectorize` and `@guvectorize` |
| Intermediate | Using Numba with DataFrames: passing column arrays (not DataFrames) into compiled functions; Polars and pandas integration patterns |
| Intermediate | **Cython**: `.pyx` files, static types (`cdef`), typed memoryviews, compiling extensions with a build backend, and the annotation report showing remaining Python interactions |
| Intermediate | Releasing the GIL in compiled code (`nogil`) so threads run in parallel (Module 2.10) |
| Advanced | Correctness: testing compiled functions against the pure-Python reference with property-based tests (Module 2.19) |
| Advanced | Packaging and deployment costs: build toolchains, wheels for several platforms, images (Module 2.18) |
| Advanced | Alternatives: Rust extensions via PyO3 and maturin (including Polars plugins), and Python compilers such as mypyc — awareness |
| Advanced | Using compiled functions inside distributed engines (pandas UDFs, Dask, Ray) |

**How to learn it**

1. Read the topic file.
2. Take a sessionisation or state-machine function over sorted events and
   write it in pure Python, vectorised NumPy/Polars (if possible), Numba,
   and Cython.
3. Profile each and explain the differences.

**Hands-on exercise — `workloads/hot_loops/`**

1. Implement per-user sessionisation over 50 million sorted events in pure
   Python; profile it.
2. Rewrite it with Numba (`@njit`, then `parallel=True` across users) and
   with Cython using typed memoryviews; compare run time including compile
   time.
3. Prove equality with the Python reference using Hypothesis.
4. Use the Numba function inside a Polars pipeline and inside a Spark pandas
   UDF or Dask map; measure end-to-end gains.
5. Write a short decision record: which version to ship and the
   maintenance cost of each.

**Checkpoint:**

- [ ] Decide when compiling is justified.
- [ ] Write Numba functions, including parallel loops.
- [ ] Write a typed Cython extension and read its annotation report.
- [ ] Test compiled code against a reference implementation.
- [ ] Explain the deployment cost of compiled extensions.

**Common mistakes:** compiling before vectorising; passing Python objects
into Numba (falling back to slow modes); measuring the first call including
compilation; shipping unreviewed native code without tests.

---

## 9. Phase D — Prove It and Pay Less (Advanced)

### Topic 06 — [Benchmarking pipelines](06-benchmarking-pipelines.md)

**Why here:** You have measured things throughout this module. This topic
makes measurement **rigorous and repeatable**, so claims like "30% faster"
are true, and performance regressions are caught before they reach
production.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Defining the question and metric: latency, throughput, peak memory, bytes read, or cost per run |
| Basics | Representative inputs: data tiers from Module 2.19; never benchmarking on toy data only |
| Basics | Repetitions, warm-up runs, and reporting medians and percentiles instead of single runs |
| Intermediate | **Cold vs warm caches**: operating-system page cache, engine caches, and remote storage caches — and deciding which reflects production |
| Intermediate | **Controlling noise**: isolated machines or runners, fixed CPU and memory limits, no background workloads, pinned versions |
| Intermediate | Tools: `pyperf` and `pytest-benchmark` for Python functions, `hyperfine` for command-line jobs, sampling profilers (`py-spy`) and `scalene` to explain results, engine UIs and dashboards for distributed runs |
| Intermediate | **Changing one variable at a time** and recording configuration with every result |
| Advanced | **Scalability tests**: strong scaling (same data, more workers) and weak scaling (more data and workers together), compared with Amdahl's law (Module 2.10) |
| Advanced | **Performance regression tracking**: storing results over time (e.g. `asv`-style histories), comparing with baselines and tolerances, and failing CI on significant regressions (on stable runners) |
| Advanced | Statistical care: variance, outliers, and whether a difference is real |
| Advanced | Honest reporting: full configuration, data description, versions, cache state, and limitations — avoiding misleading comparisons (Module 2.4) |

**How to learn it**

1. Read the topic file.
2. Benchmark one pipeline step ten times cold and ten times warm; report
   medians and spread.
3. Change nothing and run it again on another day or machine; observe the
   noise you need to account for.

**Hands-on exercise — `benchmarks/`**

1. Build a **benchmark harness** that runs a named workload on a named data
   tier, repeats it, records wall time, CPU time, peak memory, bytes read,
   configuration, and versions, and appends results to a history file.
2. Benchmark three workloads (a Polars step, a Spark job, a DuckDB query)
   with warm and cold caches.
3. Run a strong- and weak-scaling test for your Dask or Spark workload and
   plot the results against Amdahl's law.
4. Add a CI job (on a stable runner or scheduled job) that runs a small
   benchmark suite and fails when a workload is more than a set percentage
   slower than its baseline.
5. Write a benchmark report for one optimisation from this module,
   including limitations.

**Checkpoint:**

- [ ] Design benchmarks with clear metrics and representative data.
- [ ] Control caches, noise, and variables.
- [ ] Run scalability tests and interpret them.
- [ ] Detect performance regressions automatically.
- [ ] Report results honestly and reproducibly.

**Common mistakes:** single-run numbers; benchmarking on shared noisy CI
runners without accounting for noise; changing several things at once;
reporting only the best run.

---

### Topic 07 — [Compute cost optimization](07-compute-cost-optimization.md)

**Why last:** Performance work ends in money. A platform that is fast but
unaffordable fails as surely as one that is slow. This topic makes cost a
first-class engineering metric and reduces it systematically.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Where data platform money goes: compute (clusters, warehouses, functions), storage (Module 2.17), data transfer, and managed-service fees |
| Basics | **Cost visibility**: tags and labels per pipeline, team, and environment; billing exports; query tagging (Module 2.17) |
| Basics | **Unit economics**: cost per run, per TB processed, per dataset, per dashboard, per consumer |
| Intermediate | **Pricing models**: on-demand vs spot/preemptible vs reserved or committed-use discounts; which workloads suit each (batch and retryable work on spot) |
| Intermediate | **Right-sizing** from utilisation metrics (Module 2.20): CPU, memory, and container requests (Module 2.18) |
| Intermediate | **Idle elimination**: auto-suspend, auto-termination, scale to zero, scheduled shutdown of non-production environments |
| Intermediate | **Choosing the cheapest adequate engine**: a single VM with DuckDB/Polars vs a Spark cluster vs warehouse SQL vs serverless — using the estimates from Topic 01 |
| Intermediate | **Warehouse cost levers**: warehouse size and auto-suspend, clustering and partitioning, incremental models (Module 2.12) instead of full rebuilds, materialisation choices, result caching, and reservations |
| Advanced | Streaming vs micro-batch vs batch cost: always-on compute for latency nobody needs (Modules 2.1, 2.16) |
| Advanced | Hidden costs: retries and backfills, small files and request charges, cross-region transfer, over-retained snapshots, telemetry volume |
| Advanced | Price–performance of hardware: ARM instances, memory-optimised vs compute-optimised, GPUs only where they pay off |
| Advanced | **FinOps practice**: budgets and anomaly alerts (Module 2.20), regular cost reviews, ownership of spend per team, and cost in design reviews |
| Advanced | Sustainability: energy use tracks compute; less waste means lower emissions — awareness |

**How to learn it**

1. Read the topic file.
2. Export your cloud billing data (or build a realistic model of it) and
   attribute every cost line to a pipeline, dataset, or environment.
3. Calculate cost per run for your five most expensive pipelines.

**Hands-on exercise — `cost/`**

1. Build a cost report per pipeline and per dataset from billing exports,
   tags, and warehouse query history; compute unit costs.
2. Identify the top five savings opportunities (e.g. idle clusters, full
   rebuilds that could be incremental, oversized executors, a streaming job
   that could be hourly, unpruned warehouse queries).
3. Implement at least three of them: spot workers for a retryable Spark job,
   auto-suspend and right-sizing for a warehouse, and moving a small Spark
   job to DuckDB/Polars on a container.
4. Measure before and after cost per run and extrapolate the monthly saving.
5. Add budget and cost-anomaly alerts per team.
6. Write a cost-optimisation plan with owners, expected savings, and risks.

**Checkpoint:**

- [ ] Attribute cloud costs to pipelines and datasets.
- [ ] Compute and track unit costs.
- [ ] Choose pricing models and right-size resources.
- [ ] Choose the cheapest engine that meets requirements.
- [ ] Run cost optimisation as an ongoing practice.

**Common mistakes:** untagged resources; optimising tiny costs while a large
idle cluster runs; spot capacity for non-retryable work; cost reviews
without owners; saving money by silently breaking SLAs.

---

## 10. Consolidate — practice questions

When all seven topics are done, open
[`practice-questions.md`](practice-questions.md). For every question:

1. State the goal as numbers (time, memory, cost).
2. Estimate sizes, memory, run time, and cost before touching code.
3. Walk down the optimisation ladder: do less work, better engine, more
   cores, more machines, compile — and justify where you stop.
4. Profile, change one thing at a time, and verify correctness.
5. Benchmark honestly and price the result.
6. Write a short recommendation with trade-offs.

---

## 11. Module mini-project — a performance and cost review of the platform

This is the proof that you have finished the module.

**Scenario:** Your platform (Modules 2.9–2.20) works, but finance reports
that data costs doubled in six months, the nightly run now finishes after
the 07:00 SLA twice a week, and one Spark job is regularly killed for
memory. You are asked to lead a performance and cost review.

Deliver `platform_review/` with:

1. **Baseline** — run metadata, dashboards, and billing data showing
   current run times, peak memory, bytes scanned, and cost per pipeline
   (Module 2.20 metrics plus this module's cost report).
2. **Estimates** — size, memory, and throughput estimates for the four
   heaviest workloads, validated against measurements; a 12-month capacity
   plan.
3. **Scan audit** — bytes scanned vs needed for the top queries and jobs;
   fixes for pushdown blockers and layout, with measured savings.
4. **Memory fix** — the OOM-killed job diagnosed with profilers and fixed,
   proven under a container memory limit.
5. **Scaling choices** — one heavy workload implemented and benchmarked in
   Polars/DuckDB, Dask, and Spark (and Ray Data if it is ML-shaped), with a
   written choice.
6. **Hot path** — one unavoidable loop compiled with Numba or Cython, with
   property-based correctness tests and end-to-end gains measured.
7. **Benchmark harness** — repeatable benchmarks with history and a CI
   regression check.
8. **Cost optimisation** — at least three implemented savings (e.g. spot,
   right-sizing, auto-suspend, incremental instead of full rebuild, engine
   downsizing), with before/after unit costs and projected monthly savings.
9. **Report** — an executive summary (SLA status, cost trend, savings
   achieved), the evidence, an optimisation roadmap with owners, and an ADR
   for each major decision.

**Grading yourself:** the nightly run meets the 07:00 SLA with headroom; no
job is OOM-killed under its configured limits; every performance claim has
a reproducible benchmark behind it; outputs are identical before and after
optimisation; and cost per run falls measurably without breaking any SLA.

---

## 12. Module self-assessment — exit criteria

Only move to Module 2.22 when you can tick every box without looking at your
notes:

- [ ] I can estimate data size, memory, run time, and cost before running.
- [ ] I can profile memory and CPU to find real bottlenecks.
- [ ] I can audit and fix pushdown and pruning across the whole stack.
- [ ] I can scale Python workloads with Dask and Ray Data, and choose them
      over or instead of Spark correctly.
- [ ] I can accelerate hot loops with Numba or Cython and prove
      correctness.
- [ ] I can run rigorous benchmarks and detect regressions.
- [ ] I can make costs visible and reduce them without breaking SLAs.
- [ ] I have finished all practice questions and the mini-project.

---

## 13. Recommended reading and references

| Resource | Relevant topics |
| --- | --- |
| *High Performance Python*, 3rd edition — Micha Gorelick and Ian Ozsvald (O'Reilly) | 01, 05, 06 |
| `memray`, `scalene`, and `py-spy` documentation | 01, 06 |
| Engine documentation on plans and pushdown: Polars, DuckDB, Spark, PyArrow datasets, Iceberg/Delta, and your warehouse | 02 |
| Dask documentation — DataFrame best practices, distributed scheduler, dashboard | 03 |
| Ray documentation — Ray Core and Ray Data (key concepts, performance tips, batch inference) | 04 |
| Numba and Cython documentation (performance tips, parallelism, memoryviews) | 05 |
| `pyperf`, `pytest-benchmark`, `hyperfine`, and airspeed velocity (`asv`) documentation | 06 |
| The FinOps Foundation's FinOps Framework; cloud providers' cost-optimisation guidance | 07 |
| *Cloud FinOps*, 2nd edition — J.R. Storment and Mike Fuller (O'Reilly) | 07 |
| "Latency Numbers Every Programmer Should Know" (and updated versions) | 01 |

---

## 14. Where this module leads

| This module's idea | Where it goes deeper |
| --- | --- |
| Batch inference and embedding pipelines at scale; cost of serving | 2.22 Serving Data for Analytics, ML, and AI |

Performance and cost are two views of the same thing: wasted work. The
habits you build here — estimate first, read less before scaling out,
choose the simplest engine that meets the goal, compile only proven hot
spots, benchmark honestly, and make every dollar attributable — are what
keep a data platform fast and affordable as the data and the organisation
grow.
