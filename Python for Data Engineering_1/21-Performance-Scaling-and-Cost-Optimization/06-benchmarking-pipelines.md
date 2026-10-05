# 06 — Benchmarking Pipelines

> **Phase D — Prove It and Pay Less**  
> **Module 2.21: Performance, Scaling, and Cost Optimization**  
> **Level: Advanced**

## 1. Module Overview

> **Benchmarking is the disciplined process of measuring a workload under controlled conditions so that performance claims can be reproduced and compared.**

A production Data Engineer should be able to answer:

> **“Is this pipeline actually faster, by how much, under what conditions, and can we prove that the improvement is real and repeatable?”**

Benchmarking is therefore much more than putting a timer around a function. A serious benchmark defines a question, selects representative data, controls the environment, performs repeated measurements, validates correctness, analyzes variation, records configuration, compares against a baseline, and explains the limitations of the conclusion.

The core philosophy is:

```text
Do not optimize what you have not measured.
```

The engineering loop is:

```text
Measure
  ↓
Understand
  ↓
Change one thing
  ↓
Measure again
  ↓
Verify correctness
  ↓
Compare
  ↓
Decide
  ↓
Record
```

A benchmark is evidence, not a stopwatch reading.

### What this module teaches

This module formalizes the measurement work performed throughout Topics 01–05. You will learn how to benchmark:

- Python workloads
- Polars
- DuckDB
- Apache Spark
- Dask or Spark distributed scaling
- memory and I/O behavior
- cold and warm cache behavior
- strong and weak scaling
- performance regressions
- CI performance checks

You will also learn how to construct a reusable benchmark harness and produce a professional benchmark report.

---

## 2. What Is Benchmarking?

Benchmarking answers a comparative engineering question under controlled conditions.

A useful distinction is:

| Activity | Main Question |
|---|---|
| Timing | How long did this run take? |
| Benchmarking | How does this implementation perform under controlled conditions? |
| Profiling | Where is the time/memory going? |
| Monitoring | What is happening in production over time? |

All four are complementary.

For example:

```text
Benchmark
   ↓
Implementation B is 18% slower
   ↓
Profile
   ↓
Most additional time is in serialization
   ↓
Optimize
   ↓
Benchmark again
   ↓
Regression disappears
```

A simple timing statement such as:

```python
start = time.time()
run_pipeline()
print(time.time() - start)
```

can be useful for debugging, but by itself it does not establish a production-grade performance claim.

It does not tell you:

- whether the first run was unusually slow,
- whether the cache was cold or warm,
- whether the machine was busy,
- whether the data was representative,
- whether the result was correct,
- whether the difference is larger than normal measurement noise,
- whether the software versions were identical,
- whether another resource allocation was used,
- whether the observed result repeats.

---

# 3. Benchmarking vs Profiling vs Monitoring

Think of the disciplines as answering different questions.

### Timing

A single elapsed-time measurement:

```text
How long did this execution take?
```

### Benchmarking

A controlled experiment:

```text
How does implementation A compare with implementation B
for this workload, dataset, environment, and cache condition?
```

### Profiling

A diagnostic investigation:

```text
Where is the execution time or memory going?
```

### Monitoring

A production observation system:

```text
How is this workload behaving over hours, days, and releases?
```

A strong workflow often looks like:

```text
Benchmark
    ↓
Find a meaningful difference
    ↓
Profile
    ↓
Understand the cause
    ↓
Change one thing
    ↓
Benchmark again
    ↓
Track the result over time
```

---

# 4. Define the Benchmark Question

Every benchmark must begin with a question.

Bad:

> “Let's benchmark this.”

Good:

> “Does enabling Parquet projection pruning reduce runtime and bytes read for the daily customer aggregation?”

Another good question:

> “Does increasing Spark workers from 4 to 8 reduce runtime enough to justify the additional compute?”

Another:

> “Does the Numba implementation reduce end-to-end pipeline latency compared with the Python implementation?”

The experiment should be expressed as:

```text
Question
   ↓
Metric
   ↓
Input
   ↓
Environment
   ↓
Experiment
   ↓
Result
```

## 4.1 Hypothesis-driven benchmarking

Write a hypothesis before measuring.

Example:

```text
Hypothesis:
Increasing workers from 4 to 8 will reduce runtime.

Independent variable:
worker count

Dependent variable:
runtime

Controlled variables:
dataset, implementation, software versions,
hardware class, cache condition

Expected outcome:
runtime decreases, but not necessarily by 2×
```

This prevents the benchmark from becoming a search for a favorable number.

---

# 5. Choose the Correct Metric

Different workloads require different metrics.

## 5.1 Latency

Latency is the time required to complete one operation or run.

Example:

```text
Pipeline completes in 82 seconds.
```

Latency is useful for:

- one-off jobs,
- SLA measurement,
- interactive queries,
- end-to-end pipeline completion.

## 5.2 Throughput

Throughput is work completed per unit time.

Examples:

```text
rows/sec
GB/min
files/min
events/sec
```

For data processing, throughput is often more informative than raw latency.

For example:

```text
Pipeline A:
100 GB in 100 seconds

Pipeline B:
100 GB in 80 seconds
```

Latency says B is faster.

Throughput makes the comparison explicit:

```text
A = 1.0 GB/sec
B = 1.25 GB/sec
```

## 5.3 Peak memory

Peak memory matters because average memory can hide OOM risk.

A pipeline can have:

```text
Average memory: 4 GB
Peak memory:    15 GB
```

The peak value may determine whether the workload succeeds on a 16 GB machine.

## 5.4 Bytes read

Bytes read are especially important for:

- Parquet,
- object storage,
- warehouses,
- query engines.

An optimization that reduces data read may improve both runtime and cost.

## 5.5 Cost per run

Cost connects performance to infrastructure economics.

Conceptually:

```text
runtime
+
resource consumption
+
pricing model
=
cost
```

Cost optimization is covered in depth by Topic 07; this module establishes the measurements needed to support those calculations.

---

# 6. Representative Inputs

Benchmark data must resemble the workload you are trying to make decisions about.

A tiny dataset can produce behavior completely different from a production-scale dataset:

```text
Tiny dataset
    ↓
fits entirely in memory
    ↓
little I/O
    ↓
little scheduling overhead

Production dataset
    ↓
large scans
    ↓
partitioning
    ↓
shuffle
    ↓
memory pressure
    ↓
distributed execution
```

Record at least:

- row count,
- file count,
- file sizes,
- partitioning,
- key cardinality,
- skew,
- null rates,
- data types,
- compression,
- cache state.

## 6.1 Data tiers

Use the data tiers established earlier in the roadmap:

| Tier | Purpose |
|---|---|
| Tiny | Correctness and debugging |
| Small | Development and integration |
| Large | Performance benchmarking |

Do not use toy data as the only evidence for a production performance claim.

---

# 7. Warm-up Runs

The first execution can differ substantially from subsequent executions.

Potential initialization effects include:

- Python imports,
- JIT compilation,
- query compilation,
- filesystem metadata access,
- OS page-cache population,
- engine initialization,
- connection establishment,
- distributed worker startup.

Conceptually:

```text
Cold run
   ↓
Initialization overhead
   ↓
Warm run
   ↓
Steady-state behavior
```

## 7.1 Should the warm-up be excluded?

Not always.

If production experiences a cold start for every job, startup cost belongs in the benchmark.

If production keeps a process or session alive and repeatedly executes workloads, steady-state behavior may be the relevant measurement.

Therefore document:

```text
Warm-up policy:
- included in end-to-end measurement
- excluded from steady-state measurement
- both measured
```

Never blindly discard the first run.

---

# 8. Repetitions

One run is insufficient for a serious benchmark.

Bad:

```text
Run once → 10.2 sec
```

Better:

```text
10.1
10.0
10.2
9.9
10.4
10.0
10.1
9.8
10.2
10.0
```

Repeated measurements expose variation.

Consider:

- warm-up count,
- number of measured repetitions,
- sample stability,
- variance,
- outliers,
- benchmark duration.

The core exercise in this module explicitly uses **ten cold and ten warm runs**. This is the required learning exercise, not a universal law that every production benchmark must always use exactly ten observations.

The number of repetitions should ultimately depend on:

- workload duration,
- measurement noise,
- required confidence,
- infrastructure cost,
- importance of the decision.

---

# 9. Median and Percentiles

Useful summary statistics include:

- minimum,
- maximum,
- mean,
- median,
- p50,
- p90,
- p95,
- p99.

For a small dataset:

```text
9.9
10.0
10.1
10.2
10.3
10.4
14.9
```

the extreme 14.9-second observation pulls the mean upward, while the median remains representative of the central observations.

## 9.1 Why not report only the minimum?

The minimum is often the most favorable run.

It may represent unusually favorable:

- CPU scheduling,
- cache state,
- I/O conditions,
- background workload,
- network conditions.

Reporting only the best run is therefore misleading.

## 9.2 Why use percentiles?

Percentiles describe the distribution.

For example:

```text
p50 = typical central behavior
p95 = slower tail
p99 = very slow tail
```

For batch pipelines, median and spread may be more informative than a single best result.

---

# 10. Variance and Outliers

Benchmark environments contain noise.

Potential sources include:

- CPU scheduling,
- background processes,
- disk contention,
- network congestion,
- cloud noisy neighbors,
- garbage collection,
- cache state,
- autoscaling,
- distributed scheduling.

At a conceptual level understand:

- variance,
- standard deviation,
- interquartile range,
- outliers.

The goal is not to become a statistician. The goal is to answer:

> **“Is the difference between A and B likely meaningful?”**

A 1% improvement in an environment with ±5% normal variation is weak evidence.

A consistent 10% improvement in an environment with less than 1% variation is much stronger evidence.

---

# 11. Statistical Noise

A benchmark result is an observation, not automatically a fact about the underlying system.

Suppose:

```text
Implementation A:
median = 100 sec

Implementation B:
median = 99 sec
```

A 1% difference may be meaningless if repeated runs vary by several percent.

Conversely:

```text
Implementation A:
median = 100 sec

Implementation B:
median = 90 sec
```

is more compelling if the observed variation is consistently small.

Use:

```text
sample size
+
distribution
+
spread
+
effect size
+
experimental controls
```

to judge the strength of the result.

Do not pretend that a simplistic threshold can establish statistical significance in every environment.

---

# 12. Cold vs Warm Caches

Cache state can materially change benchmark conclusions.

## 12.1 Cold

Conceptually:

```text
Data is not resident in the relevant cache.
```

The workload may pay more:

- storage latency,
- metadata access,
- filesystem reads,
- network transfer,
- initialization.

## 12.2 Warm

Conceptually:

```text
Data or metadata may already be cached.
```

The workload may execute faster because prior activity has populated relevant caches.

Neither state is universally correct.

---

# 13. OS Page Cache

The operating system can cache filesystem data in memory.

A second scan may therefore behave differently from the first.

This means:

```text
First read
→ storage/filesystem access
→ page cache populated

Second read
→ potentially more data served from memory
```

The benchmark must document whether the measured run is intended to represent:

- cold-like behavior,
- warm behavior,
- mixed behavior.

Do not infer a universal cache behavior across all environments.

---

# 14. Engine Caches

Execution engines can have their own caching and reuse behavior.

Examples include:

- query-plan caches,
- data caches,
- runtime caches.

Distributed engines may also reuse sessions, executors, metadata, or other runtime state.

When benchmarking Spark, for example, distinguish:

```text
Cold end-to-end job
```

from:

```text
Warm/reused session
```

if both matter to the production workload.

---

# 15. Remote Storage Caches

Remote storage and network layers can introduce caching behavior outside the process.

The benchmark should therefore record:

```text
Cache state:
Cold / Warm / Mixed / Unknown
```

Do not claim a specific cloud provider's cache behavior unless it has been established by the benchmark environment or authoritative documentation.

The important engineering rule is:

> **Document what you know, and label what you do not know.**

---

# 16. Choosing the Production-Representative Cache State

Neither cold nor warm is universally “correct.”

### Nightly batch

Cold-like behavior may be representative if the job normally starts after a long idle period.

### Interactive dashboard

Warm behavior may be more representative if users repeatedly query related data.

### Reused service/session

Warm behavior may matter because the same process repeatedly accesses the same data.

The benchmark report must explicitly state the chosen condition and why it represents production.

---

# 17. Controlling Benchmark Noise

Control, where practical:

- CPU,
- memory,
- machine type,
- process count,
- thread count,
- background processes,
- data location,
- network conditions,
- software versions.

Preferred environments include:

- isolated machines,
- dedicated CI runners,
- controlled environments,
- scheduled benchmark infrastructure.

Perfect isolation is not always possible.

When it is not possible, record the limitation.

Example:

```text
Limitation:
Benchmark executed on a shared CI runner.
Other workloads may have affected CPU scheduling.
Results should therefore be interpreted as directional.
```

That is more credible than pretending the environment was perfectly controlled.

---

# 18. Fixed CPU and Memory Limits

Resource allocation must be comparable.

Consider:

```text
Benchmark A:
8 CPUs / 32 GB

Benchmark B:
4 CPUs / 16 GB
```

A direct runtime comparison does not isolate implementation performance because the resource budget changed.

Conceptually, containers can provide controlled limits:

```text
CPU limit:    4 CPUs
Memory limit: 16 GB
```

The objective is experimental control, not learning Kubernetes.

---

# 19. Pinned Versions

Benchmark results depend on software and hardware.

Record, where applicable:

```text
Python
Polars
DuckDB
Spark
Dask
Ray
NumPy
pandas
PyArrow
OS
CPU
RAM
```

Also record:

- compiler versions where relevant,
- CPU architecture,
- relevant engine configuration.

Dependency upgrades can change:

- execution plans,
- vectorization,
- serialization,
- memory behavior,
- scheduler behavior,
- algorithm implementations.

Therefore a benchmark history without version information is difficult to interpret.

---

# 20. One Variable at a Time

Controlled experimentation means changing one material variable at a time.

Bad:

```text
Upgrade Polars
+
change data format
+
increase CPU
+
change query
```

and then conclude:

> “The Polars upgrade made it faster.”

Correct:

```text
Baseline
   ↓
Change ONE variable
   ↓
Benchmark
   ↓
Compare
   ↓
Next variable
```

There are situations where intentionally changing multiple factors is appropriate, but that becomes a different experiment and must be described as such.

---

# 21. Benchmark Configuration Recording

Every result must contain enough information to reproduce or understand it.

At minimum record:

```text
benchmark name
workload
dataset
dataset size
input path
cache state
implementation/version
hardware
CPU
memory
worker count
thread count
software versions
configuration parameters
timestamp
run duration
throughput
peak memory
bytes read
result correctness status
```

A JSON-style result can look like:

```json
{
  "benchmark": "customer_aggregation",
  "dataset": "large",
  "cache_state": "warm",
  "workers": 4,
  "threads": 8,
  "runtime_seconds": 12.4,
  "throughput_rows_per_sec": 812345,
  "peak_memory_mb": 2048
}
```

The exact schema may grow as the project becomes more sophisticated.

---

# 22. Benchmark Result Schema

A production-oriented history record should include enough dimensions to distinguish comparable experiments.

Example:

```json
{
  "timestamp": "2026-01-01T12:00:00Z",
  "commit": "abc123",
  "benchmark": "customer_aggregation",
  "engine": "polars",
  "dataset": "large",
  "dataset_rows": 100000000,
  "cache_state": "warm",
  "warmups": 3,
  "repetitions": 10,
  "runtime_seconds_median": 82.1,
  "runtime_seconds_p95": 84.7,
  "throughput_rows_per_sec": 1218000,
  "peak_memory_mb": 4210,
  "bytes_read": 18700000000,
  "workers": 1,
  "threads": 8,
  "correct": true
}
```

Treat this as a schema example, not measured data.

---

# 23. `pyperf`

`pyperf` is appropriate for rigorous repeated Python benchmarks.

It supports concepts such as:

- repeated Python benchmarks,
- warm-ups,
- process isolation,
- stable measurements,
- statistical output.

A simple conceptual example:

```python
import pyperf

def workload():
    total = 0
    for value in range(1_000_000):
        total += value * value
    return total

runner = pyperf.Runner()
runner.bench_func("workload", workload)
```

Use `pyperf` when the unit being benchmarked is a Python-level operation or function.

It is not sufficient by itself to explain a distributed Spark or Ray pipeline. Distributed benchmarks need engine-level evidence and controlled infrastructure.

---

# 24. `pytest-benchmark`

`pytest-benchmark` integrates performance measurements into pytest-based test suites.

Conceptually:

```python
def test_transformation_speed(benchmark):
    result = benchmark(run_transformation)
    assert result is not None
```

Useful cases include:

- Python functions,
- regression tests,
- integration with an existing pytest suite.

The benchmark result can then be compared with previous benchmark history.

Remember:

```text
Correctness test
+
Performance benchmark
```

are complementary. A benchmark must not replace correctness validation.

---

# 25. `hyperfine`

`hyperfine` is useful for command-line workloads.

Example:

```bash
hyperfine 'python pipeline.py --input data/'
```

It is useful for:

- multiple runs,
- warm-up,
- shell-level measurement,
- comparing commands.

For example:

```bash
hyperfine \
  'python pipeline_v1.py --input data/' \
  'python pipeline_v2.py --input data/'
```

The command-line level is valuable for end-to-end executables where internal Python timing would omit startup, process initialization, or other relevant costs.

---

# 26. `py-spy` and `scalene`

Benchmarking tells you:

> **What is faster?**

Profiling can help explain:

> **Why is it faster?**

The workflow is:

```text
Benchmark
   ↓
Difference observed
   ↓
Profile
   ↓
Identify cause
   ↓
Optimize
   ↓
Benchmark again
```

Introduce:

- `py-spy`
- `scalene`

at the appropriate diagnostic level.

Do not use profiling output as a substitute for the benchmark itself. A profile explains execution behavior; a benchmark establishes the comparative performance claim.

---

# 27. Engine UIs and Dashboards

Distributed systems require engine-level evidence.

## Spark

Inspect:

- Spark UI,
- stage/task behavior,
- shuffle,
- execution time.

## Dask

Inspect:

- dashboard,
- task stream,
- worker behavior.

## Ray

Inspect:

- dashboard,
- tasks and actors,
- resource utilization.

Wall-clock time alone may hide:

- skew,
- worker imbalance,
- shuffle overhead,
- scheduler overhead,
- spilling,
- serialization,
- resource starvation.

Use engine dashboards to explain the observed benchmark result.

---

# 28. Building a Benchmark Harness

The central hands-on engineering task is to build a reusable benchmark harness.

The harness should:

- run a named workload,
- run against a named data tier,
- repeat execution,
- record wall time,
- record CPU time,
- record peak memory,
- record bytes read where available,
- record configuration,
- record versions,
- append results to a history file.

A conceptual project structure is:

```text
benchmarks/
├── harness/
├── workloads/
├── datasets/
├── results/
├── reports/
└── configs/
```

Do not create this directory as part of this learning file. It is the design the learner should implement in the hands-on project.

---

# 29. Benchmark Harness Architecture

A robust harness follows:

```text
Benchmark Configuration
        ↓
Load Dataset Definition
        ↓
Prepare Environment
        ↓
Warm-up
        ↓
Run N repetitions
        ↓
Collect Metrics
        ↓
Validate Correctness
        ↓
Aggregate Statistics
        ↓
Store Result
        ↓
Compare Baseline
        ↓
Generate Report
```

### Benchmark configuration

Defines:

- workload,
- data tier,
- engine,
- cache policy,
- worker count,
- thread count,
- repetition count.

### Dataset definition

Defines the exact input and its expected characteristics.

### Environment preparation

Ensures resource and software assumptions are known.

### Warm-up

Separates initialization from steady-state measurement when appropriate.

### Measurement

Collects:

- wall time,
- CPU time,
- memory,
- bytes read,
- correctness.

### Aggregation

Calculates:

- median,
- percentiles,
- spread,
- speedup,
- efficiency where applicable.

### Storage

Appends results to historical records.

### Comparison

Compares the new result against an accepted baseline.

### Reporting

Turns measurements into an interpretable engineering conclusion.

---

# 30. Measuring Wall Time

For Python elapsed-time measurements, prefer:

```python
import time

start = time.perf_counter()

run_pipeline()

elapsed = time.perf_counter() - start
print(f"{elapsed:.3f}s")
```

`time.perf_counter()` is designed for measuring elapsed time using a high-resolution monotonic clock.

A reusable measurement function can be:

```python
import time

def measure_wall_time(fn):
    start = time.perf_counter()
    result = fn()
    elapsed = time.perf_counter() - start
    return result, elapsed
```

For end-to-end benchmarks, ensure the measured region includes exactly what the benchmark question intends to measure.

---

# 31. Measuring CPU Time

Wall time and CPU time answer different questions.

```text
Wall time
=
elapsed real-world time

CPU time
=
time spent consuming CPU
```

Example:

```text
Wall = 100 seconds
CPU  = 40 seconds
```

This may suggest that the process spent substantial time waiting or that work was distributed across resources in a way that makes the relationship between CPU and wall time non-trivial.

Possible contributors include:

- I/O,
- waiting,
- concurrency,
- scheduling.

Do not infer a bottleneck from one metric alone.

---

# 32. Measuring Peak Memory

Practical approaches include:

- process RSS,
- `/usr/bin/time -v` on Linux,
- `psutil`,
- profiler-based approaches.

For example, `psutil` can expose process memory information:

```python
import os
import psutil

process = psutil.Process(os.getpid())
rss_bytes = process.memory_info().rss
print(rss_bytes)
```

This sample is a point-in-time observation. A true peak requires observing memory over the workload or using a mechanism that records maximum resident memory.

On Linux:

```bash
/usr/bin/time -v python pipeline.py
```

can provide maximum resident-set information.

Remember:

```text
Average memory ≠ peak memory
```

Peak memory is particularly important for OOM risk.

---

# 33. Measuring Bytes Read

There is no universal bytes-read API that applies identically to every engine.

Use evidence appropriate to the workload:

- filesystem-level measurements,
- Parquet scan information,
- warehouse statistics,
- engine metrics,
- query plans where relevant.

For example, a query engine may expose scan metrics while a local filesystem workload may require OS/filesystem-level evidence.

The correct method depends on the engine.

Never invent a bytes-read value merely because it would make a benchmark table look complete.

---

# 34. Correctness During Benchmarking

Performance numbers are useless if the optimized pipeline produces incorrect results.

Whenever practical:

```text
Baseline output
      ↓
Optimized output
      ↓
Compare
      ↓
Benchmark result accepted
```

Useful checks include:

- row counts,
- schemas,
- checksums/hashes,
- DataFrame equality,
- numeric tolerances.

For numeric calculations, exact equality may be inappropriate when floating-point arithmetic is involved. Use domain-appropriate tolerances.

The benchmark should record:

```text
correct = true
```

or an equivalent explicit correctness status.

---

# 35. Polars Benchmark

The roadmap explicitly requires benchmarking a Polars step.

Use a representative transformation such as:

```text
Parquet
   ↓
filter
   ↓
select
   ↓
group
   ↓
aggregate
```

Measure:

- cold execution,
- warm execution,
- repeated runs,
- runtime,
- throughput,
- memory,
- bytes read where available.

Do not fabricate results.

The learner should execute the benchmark and record the measured values.

Example workload shape:

```python
import polars as pl

result = (
    pl.scan_parquet("data/large/*.parquet")
    .filter(pl.col("status") == "active")
    .select(["customer_id", "amount"])
    .group_by("customer_id")
    .agg(pl.col("amount").sum())
    .collect()
)
```

The exact workload must be representative of the chosen data tier.

---

# 36. DuckDB Benchmark

Build a comparable DuckDB workload using the same logical computation and same data.

Conceptually:

```sql
SELECT
    customer_id,
    SUM(amount) AS total_amount
FROM read_parquet('data/large/*.parquet')
WHERE status = 'active'
GROUP BY customer_id;
```

Measure:

- cold behavior,
- warm behavior,
- repeated runtime,
- throughput where useful,
- relevant memory and scan metrics.

The comparison must remain logically equivalent.

---

# 37. Spark Benchmark

Build the same logical transformation in Spark.

Account for:

- startup overhead,
- session initialization,
- executor startup,
- caching,
- distributed scheduling.

Distinguish:

```text
cold end-to-end job
```

from:

```text
warm/reused session
```

when relevant.

Do not compare Spark against Polars or DuckDB without documenting:

- startup assumptions,
- environment,
- resource allocation,
- cache state.

---

# 38. Fair Cross-Engine Comparison

A fair comparison controls:

```text
Same data
Same logical computation
Same correctness criteria
Comparable hardware
Comparable resource allocation
Documented cache state
Documented startup assumptions
Pinned versions
```

A benchmark can be technically reproducible and still be unfair.

For example, comparing:

```text
Polars:
8 CPU / 32 GB

Spark:
2 CPU / 8 GB
```

does not establish that one engine is intrinsically faster.

Similarly:

```text
Spark cold startup
vs
Polars warm process
```

may answer a useful operational question, but it must not be presented as an apples-to-apples steady-state comparison.

---

# 39. Strong Scaling

Strong scaling means:

> **Keep the problem size fixed and increase the amount of compute.**

Example:

```text
Same 1 TB dataset

4 workers  → 100 min
8 workers  → ?
16 workers → ?
32 workers → ?
```

Do not invent the missing values.

Measure them experimentally.

The core formula is:

```text
speedup = T1 / Tp
```

where:

- `T1` is the reference runtime,
- `Tp` is the runtime using `p` workers.

Parallel efficiency is:

```text
parallel efficiency = speedup / p
```

where appropriate.

Perfect scaling would imply that doubling workers halves runtime. Real systems usually experience diminishing returns.

---

# 40. Weak Scaling

Weak scaling means:

> **Increase workload size as resources increase.**

Example:

```text
4 workers  → 100 GB
8 workers  → 200 GB
16 workers → 400 GB
32 workers → 800 GB
```

The question is:

> **Can the system maintain similar runtime as both workload and resources scale?**

Strong scaling asks:

```text
How fast can we process the same problem?
```

Weak scaling asks:

```text
Can we handle a proportionally larger problem without increasing runtime substantially?
```

Both reveal different properties of a distributed architecture.

---

# 41. Amdahl's Law

Amdahl's law explains why adding workers eventually stops producing proportional speedup.

The conceptual formula is:

```text
Speedup(N) = 1 / (S + (1-S)/N)
```

where:

- `S` = serial fraction,
- `N` = number of parallel workers.

Suppose:

```text
10% serial
90% parallel
```

Even if the parallel portion scales very well, the serial portion remains a limiting factor.

The engineering intuition is more important than the derivation:

```text
More workers
    ↓
More parallel capacity
    ↓
But serial work remains
    ↓
Plus communication/scheduling overhead
    ↓
Eventually additional workers help less
```

Unlimited workers do not produce unlimited speedup.

---

# 42. Distributed Scaling Benchmark

Use Dask or Spark for the hands-on scaling experiment.

Benchmark, where practical:

```text
1 worker
2 workers
4 workers
8 workers
```

Measure:

- runtime,
- speedup,
- efficiency,
- resource usage.

Do not fabricate final values.

Plot or describe the expected shape after running the experiment.

Then explain the observed result using:

- Amdahl's law,
- scheduling overhead,
- I/O,
- communication,
- shuffle,
- skew,
- resource saturation.

---

# 43. Performance Regression Tracking

A performance regression occurs when a new version becomes materially slower or more resource-intensive than an accepted baseline.

Example:

```text
Pipeline v1 → 120 sec
Pipeline v2 → 128 sec
```

Do not automatically declare this a regression.

First examine:

```text
baseline
+
tolerance
+
noise
+
repeated measurements
+
statistical evidence
```

The decision must distinguish real degradation from ordinary benchmark variation.

---

# 44. Baselines and Tolerances

A baseline is an accepted reference result.

Example:

```text
Baseline median = 100 sec
Allowed regression = 10%
Threshold = 110 sec
```

The 10% value is only an example.

Real tolerances should be informed by:

- historical variance,
- business SLA,
- measurement noise,
- workload importance.

A latency-sensitive production path may require a tighter tolerance than a low-priority batch process.

---

# 45. CI Performance Testing

Conceptually:

```text
Pull Request
     ↓
Benchmark suite
     ↓
Compare with baseline
     ↓
Regression detected?
     ├── NO → Pass
     └── YES → Fail / alert
```

Prefer:

- dedicated runners,
- stable machine type,
- fixed CPU/memory,
- pinned dependencies,
- controlled datasets.

Large performance suites do not necessarily belong on every pull request.

A stable scheduled benchmark job can be preferable when:

- workloads are expensive,
- infrastructure is difficult to provision,
- measurements are noisy,
- the objective is long-term trend detection.

---

# 46. CI Failure Logic

A robust CI decision should look like:

```text
Run benchmark
   ↓
Collect repeated samples
   ↓
Compute summary statistics
   ↓
Compare with baseline
   ↓
Estimate whether difference exceeds tolerance/noise
   ↓
Significant regression?
   ├── YES → Fail CI
   └── NO  → Pass
```

Do not make a single noisy measurement capable of failing production CI.

The failure rule should be deterministic enough to operate reliably while still accounting for measurement variation.

---

# 47. Benchmark History

Store results over time.

A useful history record includes:

```text
date
commit
benchmark
dataset
runtime
throughput
memory
workers
versions
environment
```

Historical trends can reveal:

```text
runtime increasing gradually
memory increasing
throughput declining
```

These changes can expose regressions that code review misses.

A benchmark history also helps answer:

> “When did this workload become slower?”

---

# 48. Statistical Regression Decisions

Consider:

- sample size,
- variance,
- outliers,
- median,
- percentiles,
- effect size,
- repeated experiments.

Example:

> A 1% difference may be meaningless if benchmark noise is ±5%.

Another:

> A 10% difference may be meaningful if variance is consistently below 1%.

The goal is not to create an artificial mathematical certainty. The goal is to make a defensible engineering decision from repeated evidence.

---

# 49. Honest Reporting

Every benchmark report must document:

```text
Question
Dataset
Data size
Hardware
CPU
RAM
Workers
Threads
Software versions
Cache state
Benchmark repetitions
Warm-ups
Metric
Median
Percentiles
Variance/spread
Result
Correctness
Limitations
```

Use language such as:

> “This result was measured on…”

rather than presenting one environment's result as universally true.

A professional report should make limitations visible rather than hiding them.

---

# 50. Common Benchmarking Mistakes

## Mistake 1 — Single-run numbers

**Symptom**

```text
A = 100 sec
B = 90 sec
```

**Why it is wrong**

The difference may be noise.

**Better approach**

Use warm-ups, repeated measurements, and distribution-aware summaries.

---

## Mistake 2 — Shared noisy CI runners

**Symptom**

Benchmark results vary unpredictably between runs.

**Why it is wrong**

Other workloads can influence CPU, memory, disk, or network behavior.

**Better approach**

Use stable runners where possible and explicitly record the limitation otherwise.

---

## Mistake 3 — Changing several things at once

**Symptom**

Engine version, query, data format, and CPU allocation all change together.

**Why it is wrong**

The causal effect cannot be isolated.

**Better approach**

Change one variable at a time unless the experiment intentionally tests a combined change.

---

## Mistake 4 — Reporting only the best run

**Symptom**

Only the fastest observation is shown.

**Why it is wrong**

It hides normal variation.

**Better approach**

Report median and relevant percentiles.

---

## Mistake 5 — Toy data

**Symptom**

A pipeline is declared faster based on a tiny dataset.

**Why it is wrong**

The benchmark may never exercise production bottlenecks.

**Better approach**

Use representative large data.

---

## Mistake 6 — Ignoring cache state

**Symptom**

Cold and warm runs are mixed together.

**Why it is wrong**

Cache state changes execution behavior.

**Better approach**

Label and control the cache condition.

---

## Mistake 7 — Ignoring startup cost

**Symptom**

Only the internal query execution is measured for a workload whose production SLA includes startup.

**Why it is wrong**

The benchmark does not match the operational question.

**Better approach**

Measure the production-relevant boundary.

---

## Mistake 8 — Ignoring correctness

**Symptom**

The faster result is accepted without checking output.

**Why it is wrong**

A wrong answer is not an optimization.

**Better approach**

Compare outputs before accepting the performance result.

---

## Mistake 9 — Changing hardware

**Symptom**

Implementation A and B run on different resource budgets.

**Why it is wrong**

The hardware change becomes a confounding variable.

**Better approach**

Keep resource allocation comparable and record it.

---

## Mistake 10 — Changing data distributions

**Symptom**

Different versions are tested on different skew, cardinality, or null distributions.

**Why it is wrong**

The workload itself changed.

**Better approach**

Keep benchmark input identity controlled.

---

## Mistake 11 — Failing to pin versions

**Symptom**

The engine or dependencies changed between experiments.

**Why it is wrong**

A version change can cause the observed performance difference.

**Better approach**

Record and pin versions.

---

## Mistake 12 — Ignoring distributed scheduler overhead

**Symptom**

Only task computation is considered.

**Why it is wrong**

Distributed execution also pays scheduling, communication, and coordination costs.

**Better approach**

Use end-to-end timing plus engine dashboards.

---

## Mistake 13 — Comparing different resource budgets

**Symptom**

One implementation gets more CPUs or memory.

**Why it is wrong**

The comparison is not fair.

**Better approach**

Use comparable resource allocations.

---

## Mistake 14 — Hiding failed experiments

**Symptom**

Only successful experiments appear in the report.

**Why it is wrong**

The evidence becomes selectively presented.

**Better approach**

Document important failed experiments and explain what they taught you.

---

## Mistake 15 — Reporting only averages

**Symptom**

One mean value represents the entire benchmark.

**Why it is wrong**

Outliers and spread disappear.

**Better approach**

Use median and percentiles alongside appropriate spread information.

---

## Mistake 16 — Optimizing the benchmark instead of the workload

**Symptom**

The measurement harness becomes extremely fast, but the production pipeline does not improve.

**Why it is wrong**

The benchmark boundary does not represent the real workload.

**Better approach**

Keep the benchmark aligned with the production question.

---

# 51. Full Hands-on Project

The required project lives conceptually under:

```text
benchmarks/
```

Do not create the directory as part of this Markdown artifact. Design and implement it as a separate learner project.

The project must contain a benchmark harness capable of:

1. Selecting a named workload.
2. Selecting a named data tier.
3. Running warm-up iterations.
4. Running repeated benchmark iterations.
5. Measuring wall time.
6. Measuring CPU time.
7. Measuring peak memory.
8. Capturing bytes read where available.
9. Capturing environment configuration.
10. Capturing software versions.
11. Verifying correctness.
12. Writing results to a history file.
13. Comparing against a baseline.
14. Generating a benchmark report.

---

# 52. Required Three-Engine Project

Benchmark three engines against the same logical workload.

## Workload 1 — Polars

Use a realistic Parquet transformation.

## Workload 2 — DuckDB

Implement the same logical transformation.

## Workload 3 — Spark

Implement the same logical transformation.

Use:

```text
same input data
same logical result
same correctness requirements
```

Run:

```text
cold
warm
repeated
```

Record:

- runtime,
- throughput where appropriate,
- memory,
- bytes read where available,
- correctness,
- configuration.

Do not fabricate results.

---

# 53. Required Scalability Project

Use Dask or Spark.

Run, where practical:

```text
1 worker
2 workers
4 workers
8 workers
```

Perform both:

### Strong scaling

Same dataset, more workers.

### Weak scaling

More data as workers increase.

Record:

```text
workers
dataset_size
runtime
speedup
efficiency
peak_memory
```

Then explain the result using:

- Amdahl's law,
- observed bottlenecks,
- scheduling,
- communication,
- I/O,
- skew where applicable.

---

# 54. Required CI Project

Design a CI benchmark workflow:

```text
Run small benchmark suite
        ↓
Compare against baseline
        ↓
Check tolerance
        ↓
Detect regression
        ↓
Fail if materially slower
```

Use a stable runner or scheduled benchmark job.

Explain why large benchmarks on every pull request may be inappropriate.

A practical strategy is:

```text
PR CI
  → small, stable, cheap checks

Scheduled benchmark
  → larger, longer, more comprehensive suite

Historical report
  → trend analysis
```

---

# 55. Professional Benchmark Report

Create:

```markdown
# Benchmark Report

## 1. Executive Summary

## 2. Benchmark Question

## 3. Dataset

## 4. Hardware

## 5. Software Versions

## 6. Methodology

## 7. Cache Conditions

## 8. Workloads

## 9. Results

## 10. Variance / Distribution

## 11. Scaling Results

## 12. Regression Comparison

## 13. Correctness Verification

## 14. Interpretation

## 15. Limitations

## 16. Recommendation
```

### 1. Executive Summary

State the decision and most important evidence.

### 2. Benchmark Question

State exactly what was tested.

### 3. Dataset

Document:

- source,
- size,
- rows,
- files,
- distribution characteristics.

### 4. Hardware

Document:

- CPU,
- RAM,
- worker count,
- thread count.

### 5. Software Versions

Record relevant versions.

### 6. Methodology

Explain:

- warm-ups,
- repetitions,
- metrics,
- controls.

### 7. Cache Conditions

State cold, warm, mixed, or unknown.

### 8. Workloads

Describe the exact computation.

### 9. Results

Present the measurements.

### 10. Variance / Distribution

Show median, percentiles, and spread.

### 11. Scaling Results

Show worker count, runtime, speedup, and efficiency.

### 12. Regression Comparison

Compare against the accepted baseline.

### 13. Correctness Verification

Show how outputs were validated.

### 14. Interpretation

Explain what the results mean.

### 15. Limitations

State what the benchmark cannot establish.

### 16. Recommendation

Make the production decision.

---

# 56. Required Results Tables

Use a table such as:

| Benchmark | Engine | Dataset | Cache | Runs | Median | P95 | Throughput | Peak Memory | Correct? |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| | | | | | | | | | |

Scaling:

| Workers | Dataset | Runtime | Speedup | Efficiency |
|---:|---:|---:|---:|---:|
| | | | | |

Do not populate these templates with fabricated numbers.

---

# 57. Experiment Design Template

For every experiment record:

```text
Hypothesis
Independent variable
Dependent variable
Controlled variables
Dataset
Environment
Procedure
Expected outcome
Actual result
Conclusion
```

Example:

```text
Hypothesis:
Increasing workers from 4 to 8 will reduce runtime.

Independent variable:
worker count

Dependent variable:
runtime

Controls:
dataset, code, versions, hardware class

Result:
measured experimentally
```

This turns benchmarking into controlled engineering experimentation.

---

# 58. Debugging Unexpected Benchmark Results

When a benchmark result is unexpected:

```text
1. Verify correctness
2. Check dataset identity
3. Check software versions
4. Check hardware
5. Check resource limits
6. Check cache state
7. Check warm-up
8. Check repetitions
9. Check background load
10. Profile
11. Inspect engine dashboard
12. Repeat experiment
```

Do not immediately conclude:

> “The engine is slower.”

The result may instead be caused by:

- different data,
- cache state,
- startup cost,
- resource limits,
- skew,
- scheduling,
- software versions,
- noisy infrastructure.

---

# 59. Production Decision Framework

The key decision is:

> **Is this performance difference real enough to justify shipping the optimization?**

Evaluate:

```text
Performance gain
+
Statistical confidence / stability
+
Correctness
+
Operational complexity
+
Maintenance cost
+
Infrastructure cost
+
SLA impact
=
Production decision
```

The fastest implementation is not automatically the best production implementation.

For example:

```text
Option A:
10% faster
simple
stable
low maintenance

Option B:
15% faster
complex
fragile
high operational cost
```

The engineering decision may reasonably favor A.

Benchmarking provides evidence; engineering judgment turns evidence into a production decision.

---

# 60. Final Checkpoint

The learner should be able to explain without notes:

```text
Benchmark question
      ↓
Metric
      ↓
Representative data
      ↓
Controlled environment
      ↓
Warm-up
      ↓
Repeated runs
      ↓
Median / percentiles
      ↓
Variance / noise
      ↓
Cold vs warm
      ↓
One variable
      ↓
Result history
      ↓
Scaling experiment
      ↓
Regression detection
      ↓
CI automation
      ↓
Honest report
      ↓
Production decision
```

The learner should also be able to:

- build a benchmark harness,
- benchmark Polars,
- benchmark DuckDB,
- benchmark Spark,
- perform strong scaling,
- perform weak scaling,
- calculate speedup,
- calculate efficiency,
- interpret Amdahl's law,
- detect a regression,
- explain benchmark limitations.

---

# 61. Interview Preparation

## Beginner

### 1. What is benchmarking?

Benchmarking is controlled measurement used to compare workload performance and support reproducible engineering decisions.

### 2. Why is one timing measurement insufficient?

Because one observation cannot distinguish the actual effect from environmental and measurement noise.

### 3. What is latency?

Elapsed time required to complete an operation or workload.

### 4. What is throughput?

Amount of work completed per unit time.

### 5. What is a warm-up?

An initial execution used to absorb initialization effects before measuring steady-state behavior when that matches the benchmark objective.

### 6. What is a cold cache?

A condition in which the relevant data or metadata is not already resident in the relevant cache.

---

## Intermediate

### 7. Why use median instead of minimum?

The minimum tends to represent an unusually favorable run. The median is more representative of the central observations.

### 8. What is p95?

The value below which approximately 95% of observations fall.

### 9. Why benchmark on representative data?

Because production behavior depends on data size, distribution, file layout, skew, cardinality, compression, and other workload characteristics.

### 10. What causes benchmark noise?

CPU scheduling, background processes, disk contention, network variation, cache state, garbage collection, distributed scheduling, and other environmental effects.

### 11. Why pin software versions?

Because dependency and engine upgrades can change performance independently of the code change being evaluated.

### 12. What is strong scaling?

Holding the problem size fixed while increasing compute resources.

### 13. What is weak scaling?

Increasing workload size proportionally with compute resources and examining whether runtime remains approximately stable.

### 14. What is the difference between profiling and benchmarking?

Benchmarking establishes comparative performance; profiling helps explain where execution time or memory is being spent.

---

## Advanced

### 15. How would you design a benchmark for Spark vs Polars?

Use the same input data and logical computation, comparable resource allocations, pinned versions, documented cache conditions, equivalent correctness checks, repeated runs, and explicit startup assumptions. Report both end-to-end and relevant steady-state measurements where appropriate.

### 16. How would you make CI performance tests reliable?

Use stable runners, fixed resource limits, pinned dependencies, controlled datasets, repeated measurements, baselines, tolerances, and decision logic that accounts for normal benchmark noise.

### 17. How would you detect a 5% regression?

Compare repeated observations with a baseline and determine whether the observed change exceeds historical variation and the workload's agreed tolerance. Do not fail CI based on a single observation.

### 18. When is a 5% regression meaningful?

When it is materially larger than normal benchmark variation and matters to the workload's SLA, cost, or capacity.

### 19. How would you benchmark cold vs warm cache behavior?

Run explicitly separated cold and warm experiments, document the cache condition, repeat each condition, and report them separately.

### 20. How would you design a strong-scaling experiment?

Keep the dataset and workload fixed, vary worker count, measure runtime, calculate speedup and efficiency, and inspect distributed-engine behavior.

### 21. How would you design a weak-scaling experiment?

Increase the workload proportionally as worker count increases, then evaluate whether runtime remains approximately stable.

### 22. How does Amdahl's law affect worker scaling?

The serial fraction limits maximum speedup, while communication and scheduling overhead further reduce practical scaling.

### 23. How would you distinguish a real regression from noisy CI?

Repeat the benchmark, inspect distribution and variance, compare with historical behavior, check environment changes, and determine whether the effect exceeds the accepted tolerance.

### 24. What belongs in a professional benchmark report?

The question, dataset, hardware, software versions, methodology, cache conditions, workloads, results, distributions, scaling results, regression comparison, correctness validation, interpretation, limitations, and recommendation.

---

# 62. Final Roadmap Coverage Checklist

Before considering the module complete:

```text
[ ] Benchmark question
[ ] Latency
[ ] Throughput
[ ] Peak memory
[ ] Bytes read
[ ] Cost per run
[ ] Representative inputs
[ ] Module 2.19 data tiers
[ ] Warm-up
[ ] Repetitions
[ ] Median
[ ] Percentiles
[ ] Variance
[ ] Outliers
[ ] Statistical noise
[ ] Cold cache
[ ] Warm cache
[ ] OS page cache
[ ] Engine cache
[ ] Remote storage cache
[ ] Production cache-state decision
[ ] Isolated machines/runners
[ ] Fixed CPU
[ ] Fixed memory
[ ] Background workload control
[ ] Pinned versions
[ ] One variable at a time
[ ] Configuration recording
[ ] pyperf
[ ] pytest-benchmark
[ ] hyperfine
[ ] py-spy
[ ] scalene
[ ] Engine UIs
[ ] Benchmark harness
[ ] Benchmark history
[ ] Strong scaling
[ ] Weak scaling
[ ] Amdahl's law
[ ] Performance regression tracking
[ ] Baselines
[ ] Tolerances
[ ] CI regression checks
[ ] Stable runners / scheduled benchmarks
[ ] Statistical interpretation
[ ] Honest reporting
[ ] Polars benchmark
[ ] DuckDB benchmark
[ ] Spark benchmark
[ ] Dask/Spark scaling benchmark
[ ] Correctness validation
[ ] Full benchmark report
[ ] Production decision
```

---

# 63. Roadmap Coverage Audit

| Roadmap Requirement | Covered? | Section |
|---|---|---|
| Define benchmark question | Yes | 4 |
| Latency | Yes | 5 |
| Throughput | Yes | 5 |
| Peak memory | Yes | 5, 32 |
| Bytes read | Yes | 5, 33 |
| Cost per run | Yes | 5 |
| Representative inputs | Yes | 6 |
| Repetitions | Yes | 8 |
| Warm-ups | Yes | 7 |
| Median | Yes | 9 |
| Percentiles | Yes | 9 |
| Cold vs warm caches | Yes | 12–16 |
| OS page cache | Yes | 13 |
| Engine caches | Yes | 14 |
| Remote storage caches | Yes | 15 |
| Noise control | Yes | 17 |
| Fixed resources | Yes | 18 |
| Pinned versions | Yes | 19 |
| One variable at a time | Yes | 20 |
| `pyperf` | Yes | 23 |
| `pytest-benchmark` | Yes | 24 |
| `hyperfine` | Yes | 25 |
| `py-spy` | Yes | 26 |
| `scalene` | Yes | 26 |
| Engine dashboards | Yes | 27 |
| Strong scaling | Yes | 39 |
| Weak scaling | Yes | 40 |
| Amdahl's law | Yes | 41 |
| Regression tracking | Yes | 43 |
| Baselines | Yes | 44 |
| Tolerances | Yes | 44 |
| CI regression detection | Yes | 45–46 |
| Statistical care | Yes | 10, 49 |
| Honest reporting | Yes | 49 |
| Benchmark harness | Yes | 28–30 |
| Polars workload | Yes | 36 |
| DuckDB workload | Yes | 37 |
| Spark workload | Yes | 38 |
| Scaling experiment | Yes | 42, 53 |
| Benchmark report | Yes | 55–56 |

---

# 64. Production Decision Standard

A senior Data Engineer should be able to defend a performance claim to a Senior Engineer, Staff Engineer, architect, or engineering manager.

The final mental model is:

```text
                     BUSINESS / SLA QUESTION
                             ↓
                        WHAT TO MEASURE
                             ↓
                     REPRESENTATIVE DATA
                             ↓
                    CONTROLLED ENVIRONMENT
                             ↓
                          WARM-UP
                             ↓
                     REPEATED MEASUREMENTS
                             ↓
                   MEDIAN / PERCENTILES
                             ↓
                     VARIANCE / NOISE
                             ↓
                      COLD / WARM STATE
                             ↓
                   ONE VARIABLE AT A TIME
                             ↓
                      FAIR COMPARISON
                             ↓
                     SCALABILITY TEST
                             ↓
                     REGRESSION TRACKING
                             ↓
                          CI CHECK
                             ↓
                     HONEST REPORTING
                             ↓
                     PRODUCTION DECISION
```

The learner should leave this module understanding:

> **A benchmark is evidence, not a stopwatch reading.**

A defensible benchmark makes clear:

1. what question was asked,
2. what was measured,
3. what data was used,
4. what environment was used,
5. how the measurements were repeated,
6. how variation was handled,
7. whether the result was correct,
8. whether the result scales,
9. whether it regresses,
10. and whether the measured improvement is worth shipping.

That is the standard required for production performance engineering.
