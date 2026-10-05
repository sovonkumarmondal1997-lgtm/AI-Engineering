# Module 2.21 — Performance, Scaling, and Cost Optimization
# Practice Questions

## How to Use This Question Bank

This question bank tests the production-oriented concepts taught across Topics 01–07 of Module 2.21. For each question, read the problem first, work through the reasoning, then compare your solution with the explanation and production insight.

The intended optimization mindset is:

> Estimate → Read less → Scale only when needed → Profile the hot path → Compile only when justified → Benchmark honestly → Measure cost → Optimize cost.

The question bank deliberately mixes calculations, code interpretation, debugging, architecture decisions, benchmark analysis, and cost reasoning. Numerical prices and benchmark values are explicitly hypothetical when used.

## Difficulty Model

- **Basic (1–10):** foundational understanding and simple application.
- **Moderate (11–20):** combines multiple concepts and requires diagnosis or selection.
- **Hard (21–30):** multi-step engineering reasoning, trade-offs, and production-style scenarios.
- **Advanced (31–40):** senior-level design reviews involving uncertainty, SLAs, benchmark evidence, architecture, performance, and cost.

# Part I — Basic

## Question 1 — Estimate an In-Memory DataFrame

### Difficulty
Basic

### Topics Covered
- Topic 01 — Estimating Data Size and Memory Footprint

### Problem
A dataset contains 5,000,000 rows and 8 numeric columns. Assume each value occupies 8 bytes in the in-memory representation. Ignoring index and object overhead, estimate the raw memory required.

### How to Think About It
Start with the simple back-of-the-envelope model: rows × columns × bytes per value. This is a first estimate, not a claim about actual peak RSS.

### Solution
Formula:

`memory ≈ rows × columns × bytes/value`

Substitute:

`5,000,000 × 8 × 8 = 320,000,000 bytes`

So the raw estimate is approximately **320 MB** using decimal units, or about **305 MiB** using binary units.

### Explanation
The calculation estimates the storage occupied by the values under the stated fixed-width assumption. Actual process memory can be higher because of indexes, Python objects, temporary allocations, copies, joins, sorts, group-bys, and other execution overhead.

### Production Insight
Use estimation before choosing an execution strategy. A small arithmetic estimate can prevent an unnecessary distributed design and can also reveal when a seemingly reasonable in-memory workload is too close to the machine's memory limit.

## Question 2 — Why Disk Size Is Not RAM Requirement

### Difficulty
Basic

### Topics Covered
- Topic 01 — Disk vs Memory
- Topic 01 — Compression and Encoding

### Problem
A Parquet dataset occupies 40 GB on object storage after compression. An engineer claims that a 40 GB machine is therefore sufficient to process it entirely in memory. Is that conclusion justified?

### How to Think About It
Separate the physical storage representation from the execution representation. Parquet may compress and encode values efficiently on disk, while an engine may materialize decoded columns and temporary structures in memory.

### Solution
No. The conclusion is not justified.

The 40 GB figure is a **compressed/encoded storage size**, not necessarily the memory footprint during processing. The actual workload may require more memory because data is decoded, columns may use different in-memory representations, and operations such as joins, sorts, group-bys, and copies can create temporary memory pressure.

### Explanation
The source module explicitly distinguishes disk size from memory size and emphasizes peak memory rather than only input size. Measurements such as pandas `memory_usage`, Polars `estimated_size`, Arrow `nbytes`, process RSS, and peak-memory tools help replace assumptions with evidence.

### Production Insight
Never size a machine from compressed Parquet bytes alone. Estimate the execution representation, identify memory-expanding operations, and leave headroom for peak rather than average usage.

## Question 3 — Identify the Main Pushdown Opportunity

### Difficulty
Basic

### Topics Covered
- Topic 02 — Predicate Pushdown
- Topic 02 — Projection Pruning
- Topic 02 — Partition Pruning

### Problem
A query reads a Parquet dataset containing 100 columns but needs only `customer_id`, `date`, and `amount`, and it filters to one month. Which two optimizations should you look for first?

### How to Think About It
Ask two questions: which columns must be read, and which files/row groups can be skipped? The first maps to projection pruning; the second maps to predicate/partition pruning.

### Solution
The first opportunities are:

1. **Projection pruning** — read only `customer_id`, `date`, and `amount`.
2. **Predicate/partition pruning** — use the date filter to avoid reading irrelevant partitions and, where available, use file and row-group statistics to skip additional data.

### Explanation
The module's core principle is that the fastest data is data you never read. Reducing the number of columns lowers bytes read and reducing the number of files/row groups lowers scan work. Verification should use the relevant engine plan or scan statistics rather than assuming pruning occurred.

### Production Insight
Pushdown and pruning should normally be considered before adding compute. They improve both performance and cost because fewer bytes need to move through the execution engine.

## Question 4 — Understand Dask Laziness

### Difficulty
Basic

### Topics Covered
- Topic 03 — Parallel DataFrames with Dask
- Dask Lazy Task Graphs

### Problem
Consider:

```python
ddf = dask.dataframe.read_parquet("events/")
filtered = ddf[ddf["country"] == "IN"]
result = filtered[["user_id", "amount"]]
```

Has the complete computation necessarily executed before `result` is created?

### How to Think About It
Identify whether the operations construct a lazy graph or trigger execution. Dask DataFrame operations generally build a task graph; `.compute()` requests the concrete result.

### Solution
No. The code primarily constructs a lazy computation graph. The actual computation is normally triggered by an operation such as `.compute()`, while `.persist()` can materialize and retain intermediate results for reuse.

### Explanation
Dask's lazy task graph allows planning and optimization before execution. Understanding this distinction is essential for reasoning about where work occurs and when the scheduler, workers, memory, and I/O are actually engaged.

### Production Insight
Do not confuse creating a Dask expression with running it. In production debugging, always identify the point at which computation is triggered.

## Question 5 — Choose the Ray Data Batch Primitive

### Difficulty
Basic

### Topics Covered
- Topic 04 — Ray Data
- `map_batches`
- Ray Blocks

### Problem
A Ray Data pipeline needs to apply the same preprocessing function to batches of records rather than one Python object at a time. Which Ray Data operation is the natural fit?

### How to Think About It
Look for the operation designed to apply a transformation to batches. Ray Data uses `map_batches` for batch-oriented processing and can work with pandas, PyArrow, or NumPy batch representations.

### Solution
The natural choice is **`map_batches`**. It applies the transformation to batches and supports batch representations such as pandas, PyArrow, and NumPy depending on the workload.

### Explanation
Batch-oriented execution reduces per-record Python overhead and is especially useful for ML preprocessing, inference, and other transformations that naturally operate on vectors or batches.

### Production Insight
Choose batch size and batch representation based on the workload and resource behavior. A correct primitive is necessary, but production performance still depends on CPU/GPU utilization, memory, and backpressure.

## Question 6 — Decide Whether a Loop Is a Hot Path

### Difficulty
Basic

### Topics Covered
- Topic 05 — Numba and Cython
- Profiling Before Optimization
- Vectorization First

### Problem
A Python function contains a loop over millions of records and profiling shows that this loop consumes most of the CPU time. What should you establish before immediately adding `@njit`?

### How to Think About It
First confirm that the loop is actually the measured hot path and then consider whether a vectorized NumPy, Polars, or SQL implementation can remove the Python loop altogether.

### Solution
You should establish:

1. The loop is a measured CPU hot path.
2. The workload cannot be substantially improved by a simpler vectorized NumPy/Polars/SQL formulation.
3. The behavior is correct and benchmarkable.

Only then should Numba or Cython become serious options.

### Explanation
The module's optimization order is profile first and vectorize first. Compilation is a targeted optimization for justified hot loops, not a universal response to slow Python.

### Production Insight
The senior question is not “Can Numba make this faster?” It is “Do I need to compile this loop at all?”

## Question 7 — Pick the Right Benchmark Metrics

### Difficulty
Basic

### Topics Covered
- Topic 06 — Benchmarking Pipelines

### Problem
A data pipeline is being optimized for production. Name five useful metrics that should be considered instead of reporting only wall-clock runtime.

### How to Think About It
Performance is multidimensional. The source module explicitly calls out latency, throughput, peak memory, bytes read, and cost per run.

### Solution
Five useful metrics are:

- latency/runtime;
- throughput;
- peak memory;
- bytes read;
- cost per run.

### Explanation
Runtime alone can hide a trade-off. An implementation can be faster while reading more data, using much more memory, or costing significantly more. A production benchmark should therefore capture multiple dimensions.

### Production Insight
Benchmark the metrics that map to the real production objective. If the SLA is latency and the budget is strict, a runtime-only benchmark is incomplete.

## Question 8 — Calculate Cost per Run

### Difficulty
Basic

### Topics Covered
- Topic 07 — Compute Cost Optimization
- Cost per Run

### Problem
Assume a hypothetical worker costs **$0.50/hour**. A pipeline uses 4 workers for 30 minutes. Ignore all other costs. What is the hypothetical compute cost per run?

### How to Think About It
Convert 30 minutes to 0.5 hours, multiply worker count by hours, then multiply by hourly price.

### Solution
Compute:

`4 workers × 0.5 hours = 2 worker-hours`

`2 × $0.50 = $1.00`

The hypothetical compute cost is **$1.00 per run**.

### Explanation
This is an intentionally hypothetical pricing model, not a real cloud price. The important skill is translating resource consumption and runtime into unit economics.

### Production Insight
Cost optimization begins with visibility. Once cost per run is known, it can be compared against throughput, SLA, and monthly workload volume.

## Question 9 — Estimate Runtime from Throughput

### Difficulty
Basic

### Topics Covered
- Topic 01 — Throughput Estimation
- Topic 06 — Benchmarking

### Problem
A workload must process 600 GB. A measured pipeline throughput is 50 GB/minute. Ignoring startup and other overhead, estimate the runtime.

### How to Think About It
Use the simple relationship `time ≈ bytes / throughput`. Keep the units consistent.

### Solution
`time = 600 GB / 50 GB/min = 12 minutes`

The estimated runtime is **12 minutes**.

### Explanation
This is a planning estimate, not a guaranteed production runtime. Real systems may experience startup overhead, variable throughput, I/O contention, skew, cache effects, and other bottlenecks.

### Production Insight
Back-of-the-envelope runtime estimates are valuable for capacity planning and SLA reasoning, but should be validated with representative benchmarks.

## Question 10 — Apply the Optimization Ladder

### Difficulty
Basic

### Topics Covered
- Module-wide Optimization Ladder

### Problem
A pipeline is slow. An engineer's first proposal is to add more machines. Give the preferred reasoning sequence from the module before blindly scaling out.

### How to Think About It
Start with reducing the work. Then consider whether a better engine can solve it. Scale cores or machines only when justified by the workload. Compile hot loops only after profiling. Finally benchmark and price the result.

### Solution
A suitable sequence is:

1. **Do less work**
2. **Use a better engine**
3. **Use more cores**
4. **Use more machines**
5. **Compile hot loops**
6. **Measure**
7. **Price**

The exact operational order can involve measurement throughout, but the central principle is to avoid scaling work that could simply be eliminated or reduced.

### Explanation
The module rejects “the data is slow, so add more machines” as the default mindset. Estimation, pushdown, engine selection, profiling, honest benchmarking, and cost analysis should precede unnecessary complexity.

### Production Insight
The simplest adequate architecture is usually preferable. Scaling is a tool, not the first diagnosis.


# Part II — Moderate

## Question 11 — Estimate Peak Memory with an Expansion Factor

### Difficulty
Moderate

### Topics Covered
- Topic 01 — Memory Estimation
- Topic 01 — Peak Memory

### Problem
A pipeline has a 20 GB in-memory input representation. During a join, historical measurements show that peak working memory can reach 2.5× the input representation. Estimate peak working memory and explain why the machine should not be sized exactly to that number.

### How to Think About It
Apply the measured expansion factor, then add operational headroom. Peak memory is more important than average memory for avoiding OOM failures.

### Solution
Estimated peak working memory:

`20 GB × 2.5 = 50 GB`

So the measured-style estimate is **50 GB peak working memory**.

The machine should not be sized to exactly 50 GB because the process also needs room for other allocations and the operating system/container. Production capacity planning should include explicit headroom and consider cgroup/container limits.

### Explanation
Joins can create additional structures and copies, so input size is not equal to peak memory. The module emphasizes expansion factors, peak versus average memory, headroom, and measurement with tools such as RSS and `/usr/bin/time -v`.

### Production Insight
Treat peak memory as a capacity constraint. A pipeline that barely fits under ideal conditions can fail when data shape, concurrency, or temporary allocations change.

## Question 12 — Diagnose a Blocked Predicate Pushdown

### Difficulty
Moderate

### Topics Covered
- Topic 02 — Predicate Pushdown
- Topic 02 — Pushdown Blockers
- Topic 02 — Verification

### Problem
A Parquet query filters on `amount > 100`, but the execution plan shows that far more data is scanned than expected. The filter is expressed through a Python UDF. What is the likely issue, and how would you investigate it?

### How to Think About It
First distinguish the logical filter from whether the storage/engine can understand it early enough to prune data. A Python UDF may block pushdown because the scan layer cannot necessarily reason about arbitrary Python code.

### Solution
Likely root cause: the Python UDF is preventing effective pushdown.

Investigation:

1. Inspect the engine's execution plan.
2. In Polars, inspect `explain()`.
3. In DuckDB, inspect `EXPLAIN ANALYZE`.
4. For Spark, inspect `PushedFilters` and relevant partition filters.
5. Compare bytes scanned with bytes logically needed.
6. Rewrite the predicate using an engine-understandable expression where possible.
7. Re-measure scan volume and runtime.

### Explanation
Pushdown is not proven by writing a filter in application code. It must be verified through execution evidence. Python UDFs, functions or casts on filtered columns, derived columns, type mismatches, and other constructs can block optimization.

### Production Insight
When scan cost is high, treat the plan as evidence. Rewrite the filter only after identifying the actual blocker, then benchmark the resulting scan and cost.

## Question 13 — Choose a Dask Partitioning Strategy

### Difficulty
Moderate

### Topics Covered
- Topic 03 — Dask
- Dask Partitions
- Partition Sizing

### Problem
A Dask workload has 50,000 tiny partitions. The dashboard shows high scheduler overhead and low useful worker throughput. What is the most likely problem and what change should you test?

### How to Think About It
The number of partitions matters because each partition creates task and scheduling overhead. Excessively tiny partitions can make the scheduler spend too much effort coordinating tasks instead of doing useful work.

### Solution
The likely problem is **partition granularity that is too small**.

Test a larger partition size by using `repartition` or by changing the upstream read/layout so fewer, appropriately sized partitions are created. Then benchmark scheduler overhead, throughput, worker memory, and task duration.

### Explanation
Dask can parallelize work, but parallelism has coordination costs. Tiny partitions are an anti-pattern when they create disproportionate scheduler overhead. The right size depends on workload, memory, and cluster characteristics, so it should be measured rather than chosen by a universal number.

### Production Insight
Partition sizing is an engineering parameter. Optimize it against worker memory, task duration, scheduler overhead, and throughput—not simply “more partitions = more parallelism.”

## Question 14 — Diagnose a Dask Shuffle Bottleneck

### Difficulty
Moderate

### Topics Covered
- Topic 03 — Dask
- Shuffles
- `set_index`
- Dashboard Troubleshooting

### Problem
A Dask job performs `set_index()` on a large unsorted dataset. Workers show high memory pressure and spilling, while the task-stream view shows a long shuffle phase. What is the likely bottleneck and what evidence should you inspect next?

### How to Think About It
`set_index()` on unsorted data can require a shuffle. A shuffle moves data between workers and can create substantial memory, network, and coordination pressure.

### Solution
Likely bottleneck: the **shuffle caused by repartitioning the data for the new index**.

Inspect:

- dashboard task-stream behavior;
- worker memory;
- spilling activity;
- partition sizes;
- shuffle-related task duration;
- network/communication behavior where visible;
- whether the index operation is actually necessary.

Then compare an alternative layout or processing strategy and benchmark it.

### Explanation
The dashboard provides evidence rather than merely confirming that “Dask is slow.” High spilling combined with a long shuffle phase points toward a distributed data movement problem and possible memory pressure.

### Production Insight
Avoid expensive shuffles when the workload does not require them. If they are required, size partitions and workers with the shuffle's memory and communication behavior in mind.

## Question 15 — Reason About Ray Data Batch Size

### Difficulty
Moderate

### Topics Covered
- Topic 04 — Ray Data
- `map_batches`
- Batch Size
- CPU/GPU Utilization

### Problem
A Ray Data inference pipeline uses GPUs, but GPU utilization remains low. CPU preprocessing is also visible between inference calls. Name the first two workload parameters you would investigate and explain why.

### How to Think About It
Look for GPU starvation and insufficient work per inference invocation. Batch size and the number of concurrent processing actors/batches are direct controls over how effectively the GPU can be fed.

### Solution
Investigate:

1. **Batch size** — batches that are too small may create excessive invocation overhead and insufficient GPU work.
2. **Actor/concurrency configuration** — too little concurrency can leave GPUs idle while CPU preprocessing occurs.

Also inspect CPU preprocessing time and whether the pipeline is experiencing backpressure or another upstream bottleneck.

### Explanation
Ray Data is designed around batch processing, resource allocation, and streaming execution. GPU utilization depends on the complete pipeline, not merely requesting GPUs. Batch size, actor pools, CPU preprocessing, and throughput must be considered together.

### Production Insight
A GPU allocation is not proof of GPU efficiency. Benchmark throughput and cost per inference while tuning batch size and concurrency.

## Question 16 — Decide Whether Numba Is Justified

### Difficulty
Moderate

### Topics Covered
- Topic 05 — Numba
- Profiling
- Vectorization First

### Problem
A Python loop takes 80% of CPU time. A vectorized NumPy version appears feasible but has not been tested. An engineer proposes Cython immediately. What should happen first?

### How to Think About It
Compilation should not be the first response. Compare the measured hot loop with a simpler vectorized implementation and benchmark it before selecting a compiled path.

### Solution
First:

1. Verify the loop is the measured hot path.
2. Implement the feasible NumPy/vectorized alternative.
3. Benchmark correctness and performance.
4. If the vectorized version is insufficient and the loop remains a justified hot path, evaluate Numba or Cython.
5. Choose the simplest option that meets the target.

### Explanation
The module explicitly places vectorization before compilation. Numba and Cython add build/runtime complexity and should be justified by evidence. The goal is not to maximize compiler usage; it is to remove the bottleneck efficiently.

### Production Insight
Compilation is a last-mile optimization. Prefer an understandable vectorized solution when it meets the performance target.

## Question 17 — Design a Credible Benchmark

### Difficulty
Moderate

### Topics Covered
- Topic 06 — Benchmarking
- Warm-ups
- Repetitions
- Median and Variance

### Problem
Two implementations are being compared. The engineer ran each once on a shared machine and chose the faster result. List four changes that would make the comparison more credible.

### How to Think About It
A single observation is vulnerable to warm-up effects, cache state, background noise, and random variance. Build a controlled experiment rather than comparing two arbitrary runs.

### Solution
Improve the benchmark by:

- using representative data;
- performing warm-ups;
- running multiple repetitions;
- reporting median and relevant percentiles/variance;
- controlling cache state where relevant;
- isolating the runner and pinning versions;
- changing one major variable at a time;
- recording configuration and environment.

At least four of these should be applied; in production benchmarking, use the full methodology appropriate to the workload.

### Explanation
The source emphasizes warm-up, repetitions, median, percentiles, variance, cache state, isolated runners, fixed resources, pinned versions, and honest reporting. A benchmark result without methodology is difficult to trust.

### Production Insight
A benchmark is an experiment. Treat its environment and methodology as part of the result.

## Question 18 — Interpret Strong vs Weak Scaling

### Difficulty
Moderate

### Topics Covered
- Topic 06 — Strong Scaling
- Topic 06 — Weak Scaling
- Amdahl's Law

### Problem
A workload takes 40 minutes on 4 workers and 22 minutes on 8 workers with the same input. Is this a strong-scaling experiment or a weak-scaling experiment?

### How to Think About It
Ask whether the workload stayed constant while resources changed. Strong scaling keeps the workload fixed; weak scaling grows the workload with resources.

### Solution
This is a **strong-scaling** experiment because the same workload is run with 4 and 8 workers.

The speedup is:

`40 / 22 ≈ 1.82×`

Ideal 2× speedup was not achieved, indicating parallel overhead, serial work, contention, or another scaling limit.

### Explanation
Strong scaling asks how much faster a fixed workload becomes as resources increase. Amdahl's law explains why a serial fraction or other non-parallelizable portion limits the maximum speedup.

### Production Insight
Do not equate doubling resources with doubling performance. Measure scaling efficiency and identify the bottleneck limiting additional parallelism.

## Question 19 — Calculate Cost per TB

### Difficulty
Moderate

### Topics Covered
- Topic 07 — Unit Economics
- Cost per TB

### Problem
A hypothetical workload processes 20 TB per month and costs $80/month in compute. What is its hypothetical compute cost per TB?

### How to Think About It
Unit economics divides total relevant cost by the corresponding unit of work.

### Solution
`Cost per TB = $80 / 20 TB = $4/TB`

The hypothetical compute cost is **$4 per TB**.

### Explanation
This metric allows comparison across workloads or configurations even when total monthly volumes differ. It is not a complete economic model because storage, transfer, managed-service fees, and other costs may also matter.

### Production Insight
Track cost per unit of work, not only monthly spend. Unit economics makes optimization decisions more comparable as workload volume changes.

## Question 20 — Choose the Simplest Adequate Engine

### Difficulty
Moderate

### Topics Covered
- Topic 01 — Workload Estimation
- Topic 03 — Dask
- Topic 04 — Ray Data
- Topic 07 — Engine Selection

### Problem
A 30 GB analytical workload fits comfortably on a single machine, primarily consists of columnar filtering and aggregation, and has no GPU or distributed requirement. Which general direction should be evaluated first: Polars/DuckDB on a single node, Dask, Ray Data, or Spark? Explain.

### How to Think About It
Start with workload size and type. If a workload fits comfortably on one machine and has no special distributed or GPU requirement, prefer evaluating a capable single-node engine before adding distributed operational complexity.

### Solution
Evaluate **Polars or DuckDB on a single node first**.

Reasoning:

- the workload fits on one machine;
- filtering and aggregation are natural single-node analytical operations;
- there is no stated GPU requirement;
- there is no stated need for distributed processing;
- Dask, Ray, or Spark would introduce additional distributed coordination and operational complexity without an established need.

The final decision should still be validated with representative benchmarks.

### Explanation
The module's optimization philosophy is to choose the simplest adequate architecture. Distributed systems are valuable when workload characteristics require them, but they are not automatically faster or cheaper for small, manageable workloads.

### Production Insight
Engine selection is an engineering decision driven by workload characteristics, not by the popularity of a framework.


# Part III — Hard

## Question 21 — Optimize a Memory-Heavy Join

### Difficulty
Hard

### Topics Covered
- Topic 01 — Peak Memory
- Topic 02 — Projection Pruning
- Joins
- Capacity Planning

### Problem
A pipeline reads two Parquet datasets and crashes during a join. The raw inputs total 30 GB on disk. Before changing cluster size, design a diagnosis sequence that addresses why 30 GB of input can still cause an OOM.

### How to Think About It
Separate storage size from execution memory. Inspect selected columns, in-memory representation, join expansion, temporary allocations, and peak RSS. Then reduce work before adding resources.

### Solution
A strong diagnosis is:

1. Estimate the in-memory size of each required input rather than using compressed disk size.
2. Apply projection pruning so unused columns are not materialized.
3. Apply predicate/partition pruning where possible.
4. Measure RSS and peak memory during the join.
5. Investigate join cardinality and whether the join creates large intermediate structures.
6. Inspect copies/temporary allocations.
7. Compare measured peak memory with container/cgroup limits and available headroom.
8. Only then decide whether repartitioning, out-of-core processing, or more resources are necessary.

The 30 GB disk figure alone is insufficient to size the execution environment.

### Explanation
Joins are specifically identified as memory-expanding operations. Peak memory can exceed input representation through hash structures, copies, intermediate results, and other execution behavior. Reducing columns and rows before the join can be more effective than immediately increasing machine size.

### Production Insight
An OOM is often an estimation and workload-shape problem before it is a hardware problem. Measure peak memory and reduce the data flowing into the expensive operation.

## Question 22 — Build a Pushdown Scan Audit

### Difficulty
Hard

### Topics Covered
- Topic 02 — Pushdown/Pruning
- Topic 06 — Benchmarking
- Topic 07 — Cost Optimization

### Problem
A warehouse query returns 200 MB but scans 2 TB. Design a practical scan-audit process to determine whether the excess scan is justified or caused by missing pruning/pushdown.

### How to Think About It
Compare logical output size with physical work. Inspect the query plan and storage-level evidence, identify which predicates and projections reached the scan, then quantify bytes scanned and cost before and after a change.

### Solution
Audit steps:

1. Record baseline runtime, bytes scanned, and cost per run.
2. Inspect the execution plan for filter/projection pushdown.
3. Check whether partition pruning occurs.
4. Inspect file/table statistics, manifests, or row-group statistics where applicable.
5. Look for blockers such as Python UDFs, casts/functions on filtered columns, derived-column filters, type mismatches, or filtering after `collect`.
6. Reduce selected columns.
7. Rewrite filters into forms the engine can push down.
8. Re-run the query on representative data.
9. Compare bytes scanned, runtime, and cost.
10. Confirm result correctness.

If the scan remains large, determine whether the physical layout—such as sorting/clustering/partitioning—limits pruning.

### Explanation
The 200 MB result does not imply that only 200 MB needed to be read. The key metric is bytes needed versus bytes scanned. Pushdown is both a performance technique and a cost lever.

### Production Insight
Make scan volume an observable production metric. A recurring scan audit can reveal cost regressions before they become large bills.

## Question 23 — Repair a Dask Memory-Pressure Pattern

### Difficulty
Hard

### Topics Covered
- Topic 01 — Memory Footprint
- Topic 03 — Dask
- Partitions
- Spilling

### Problem
A Dask cluster has workers repeatedly spilling to disk. The dashboard shows a few very large partitions while many other partitions are much smaller. Throughput is poor. Propose a diagnosis and remediation plan.

### How to Think About It
Look for partition imbalance and peak worker memory. Large partitions can exceed useful memory capacity even when average cluster memory looks sufficient. Spilling is evidence of memory pressure, not automatically a reason to add workers.

### Solution
Diagnosis:

1. Inspect the Dask dashboard's worker memory view.
2. Identify which tasks process the oversized partitions.
3. Measure partition sizes and their relationship to worker memory.
4. Check whether a shuffle or repartitioning operation created the imbalance.
5. Determine whether the large partitions are caused by data skew or poor partition sizing.

Remediation:

- repartition the data into more balanced partitions where appropriate;
- reduce columns/rows before expensive operations;
- avoid unnecessary shuffles;
- size workers with realistic peak memory and headroom;
- benchmark the new partition layout;
- verify that spilling decreases without creating excessive scheduler overhead.

### Explanation
Dask worker memory management includes spilling and pausing behavior. More workers do not necessarily solve oversized partitions because a single oversized partition can still exceed the useful memory of the worker handling it.

### Production Insight
Partition-level evidence matters more than aggregate cluster capacity. Fix data distribution and partition sizing before simply increasing the cluster.

## Question 24 — Resolve Low GPU Utilization in Ray Data

### Difficulty
Hard

### Topics Covered
- Topic 04 — Ray Data
- Batch Size
- Actor Pools
- GPU Economics

### Problem
A Ray Data batch-inference job requests 8 GPUs. Benchmark results show low GPU utilization, substantial CPU preprocessing time, and a high cost per inference. Design the first optimization experiment.

### How to Think About It
Treat the GPU as part of an end-to-end pipeline. If CPU preprocessing starves the GPU or batches are too small, adding more GPUs can increase cost without increasing useful throughput.

### Solution
First establish a baseline containing:

- inference throughput;
- GPU utilization;
- CPU utilization;
- batch size;
- actor count/pool configuration;
- preprocessing time;
- cost per inference.

Then run a controlled experiment changing one major variable at a time. Start by testing larger batch sizes where model/memory constraints allow, and adjust actor/concurrency configuration so CPU preprocessing can feed the GPUs continuously. Verify memory safety and measure throughput and cost per inference.

Do not assume that moving from 8 to more GPUs is the solution.

### Explanation
Ray Data supports `map_batches`, CPU/GPU resource allocation, actor pools, and stateful processing. Model loading once per actor can reduce repeated initialization, while batch size and concurrency affect GPU utilization. The correct choice must be benchmarked.

### Production Insight
The goal is useful GPU work per dollar, not maximum allocated GPU count. Optimize the pipeline feeding the accelerator before scaling accelerator count.

## Question 25 — Choose Between Vectorization, Numba, and Cython

### Difficulty
Hard

### Topics Covered
- Topic 05 — Numba and Cython
- Profiling
- NumPy/Polars/SQL
- Benchmarking

### Problem
A sessionization function contains a CPU-heavy Python loop. Profiling confirms the loop is the dominant hot path. A vectorized Polars formulation is possible but would require a moderate rewrite. Numba can compile the existing numerical loop; Cython would require a compiled extension. How should you decide?

### How to Think About It
The decision should compare the simplest alternatives against the measured performance target, correctness, engineering complexity, and deployment implications.

### Solution
Use this sequence:

1. Define the performance target.
2. Prototype the vectorized Polars/SQL/NumPy alternative and benchmark it.
3. If it meets the target, prefer it because it removes the Python loop without compiler/build complexity.
4. If it does not, evaluate Numba if the loop and data types fit its supported execution model.
5. Evaluate Cython if static typing, typed memoryviews, GIL/nogil control, or extension-level behavior provides a justified advantage.
6. Benchmark candidates under the same methodology.
7. Include packaging, wheel/platform compatibility, Docker, correctness, and maintenance in the decision.

The answer is not inherently “Numba” or “Cython”; it is the simplest implementation that meets the measured requirement.

### Explanation
The module positions Numba and Cython as tools for justified hot paths. Numba often offers a direct route for numerical array-oriented loops, while Cython provides lower-level control and compiled-extension patterns. The production choice includes deployment cost, not just runtime.

### Production Insight
A compiler is an architectural dependency. Measure its benefit and account for the long-term build and deployment surface.

## Question 26 — Judge a Claimed 30% Benchmark Improvement

### Difficulty
Hard

### Topics Covered
- Topic 06 — Benchmarking
- Variance
- Outliers
- Statistical Interpretation

### Problem
Two implementations are benchmarked under identical conditions:

| Run | A (s) | B (s) |
|---|---:|---:|
| 1 | 100 | 70 |
| 2 | 80 | 90 |
| 3 | 95 | 75 |
| 4 | 85 | 82 |
| 5 | 110 | 68 |

An engineer claims B is definitively 30% faster. Is that claim supported by this table alone?

### How to Think About It
First compute medians and inspect spread. A single comparison should not be reduced to the fastest observed run. Check whether the distributions overlap and whether additional controlled repetitions are needed.

### Solution
Sort A: `80, 85, 95, 100, 110` → median **95 s**.

Sort B: `68, 70, 75, 82, 90` → median **75 s**.

Median-based speedup:

`95 / 75 ≈ 1.27×`

That is about **21.1% lower runtime** for B relative to A, not a demonstrated 30% speedup.

The table also shows meaningful variance. Therefore the 30% claim is **not supported by this table alone**. More controlled repetitions and an appropriate statistical summary are warranted.

### Explanation
The module requires median/percentile reasoning, variance awareness, and honest reporting. The fastest B run is 68 seconds, but comparing 68 with 110 would be cherry-picking. A credible benchmark reports methodology and distribution, not a favorable pair of runs.

### Production Insight
Do not optimize or announce a win from the best run. Benchmark claims should survive reasonable scrutiny of variance and experimental design.

## Question 27 — Apply Amdahl's Law to Scaling

### Difficulty
Hard

### Topics Covered
- Topic 06 — Amdahl's Law
- Strong Scaling
- Cost Optimization

### Problem
Suppose 25% of a workload is serial and 75% can scale perfectly. What is the maximum theoretical speedup with 8× parallel resources according to Amdahl's law?

### How to Think About It
Use `speedup = 1 / (serial_fraction + parallel_fraction / N)`.

### Solution
With serial fraction `0.25`, parallel fraction `0.75`, and `N = 8`:

`speedup = 1 / (0.25 + 0.75/8)`

`= 1 / (0.25 + 0.09375)`

`= 1 / 0.34375`

`≈ 2.91×`

So the theoretical maximum speedup under the stated assumptions is about **2.91×**, far below 8×.

### Explanation
The serial fraction remains a limiting component even when additional resources are perfect. Real systems can perform worse because of communication, scheduling, synchronization, I/O, and other overheads.

### Production Insight
Before buying more machines, identify the serial fraction and other scaling limits. If the workload cannot scale efficiently, additional resources may increase cost faster than performance.

## Question 28 — Compare Three Scaling Configurations

### Difficulty
Hard

### Topics Covered
- Topic 06 — Benchmark Interpretation
- Topic 07 — Cost Optimization
- SLA
- Strong Scaling

### Problem
The following are illustrative benchmark data:

| Configuration | Runtime | Workers | Cost |
|---|---:|---:|---:|
| A | 40 min | 4 | $4 |
| B | 25 min | 8 | $6 |
| C | 20 min | 16 | $11 |

The production SLA is 30 minutes. Which configurations meet the SLA, which is cheapest among those that meet it, and which is fastest?

### How to Think About It
Separate three questions: SLA feasibility, absolute cost, and runtime. Do not collapse them into a single “best” metric.

### Solution
SLA:

- A: 40 min → **fails**
- B: 25 min → **meets**
- C: 20 min → **meets**

Among SLA-compliant options:

- Cheapest: **B at $6**
- Fastest: **C at 20 minutes**
- B has a lower cost and still meets the SLA.

Therefore, if the requirement is simply to satisfy the stated 30-minute SLA at minimum cost, **B is the preferred configuration**. C is justified only if its additional 5-minute reduction has business value.

### Explanation
This separates performance from cost and SLA. Faster is not automatically better when the SLA is already satisfied. Additional evidence such as variability, reliability, and workload growth may affect the final production decision.

### Production Insight
Optimize for the actual service objective. Once an SLA is met, additional performance should justify its marginal cost.

## Question 29 — Estimate Cost Savings from Reading Less

### Difficulty
Hard

### Topics Covered
- Topic 01 — Data Size
- Topic 02 — Pushdown
- Topic 07 — Cost Optimization

### Problem
A hypothetical warehouse query currently scans 8 TB per run at an assumed cost of $5 per TB. A pushdown/pruning improvement reduces the scan to 1.5 TB. Calculate the old cost, new cost, and savings per run.

### How to Think About It
Use cost per TB as the unit-economics model. Calculate each configuration separately, then subtract.

### Solution
Hypothetical old cost:

`8 TB × $5/TB = $40`

Hypothetical new cost:

`1.5 TB × $5/TB = $7.50`

Savings:

`$40 - $7.50 = $32.50 per run`

Percentage reduction:

`$32.50 / $40 × 100 = 81.25%`

So the hypothetical saving is **$32.50 per run**, or **81.25% of the scan cost**.

### Explanation
The price is explicitly hypothetical. The engineering point is that pushdown/pruning reduces work at the source, so performance and cost can improve together without adding compute.

### Production Insight
When a workload is scan-heavy, reducing bytes read is often a higher-leverage cost optimization than right-sizing compute after the scan has already happened.

## Question 30 — Build an Engine-Selection Decision

### Difficulty
Hard

### Topics Covered
- Topic 01 — Workload Estimation
- Topic 03 — Dask
- Topic 04 — Ray Data
- Topic 07 — Engine Selection

### Problem
You have three workloads:

A. 15 GB interactive SQL-style analytics with filters and aggregations.
B. 2 TB tabular transformation workload that exceeds a single machine's comfortable memory and has conventional dataframe operations.
C. 500 GB ML preprocessing and batch inference that requires GPUs.

Choose the first engine family to evaluate for each from Polars/DuckDB, Dask, Ray Data, or Spark, and justify each choice.

### How to Think About It
Match the architecture to workload shape rather than selecting one framework for everything.

### Solution
A reasonable first evaluation is:

- **A → Polars or DuckDB:** single-node analytical workload that is small enough to fit comfortably and is filter/aggregation oriented.
- **B → Dask or Spark:** the workload exceeds comfortable single-node memory and needs distributed dataframe-style processing. Dask is a natural evaluation for dataframe-oriented Python workflows; Spark is another candidate depending on the broader platform and operational requirements.
- **C → Ray Data:** GPU-backed ML preprocessing and batch inference align strongly with Ray Data's resource-aware batch processing and actor-pool model.

Each choice still requires representative benchmarking, correctness validation, operational assessment, and cost analysis.

### Explanation
The module teaches that engine selection depends on data size, workload type, joins/aggregation, ML preprocessing, GPU requirements, distributed needs, operational complexity, cost, and SLA. There is no universal winner.

### Production Insight
Choose the simplest engine that satisfies the workload's real constraints. A migration or distributed architecture should be justified by evidence, not framework preference.


# Part IV — Advanced

## Question 31 — Design a Production Optimization Plan for a Memory and Scan Incident

### Difficulty
Advanced

### Topics Covered
- Topics 01, 02, 06, 07
- Peak Memory
- Pushdown
- Benchmarking
- Cost

### Problem
A daily pipeline has three symptoms: it scans far more Parquet data than the final result needs, occasionally hits container OOM during a join, and has rising compute cost. The SLA is 25 minutes. Design a prioritized optimization plan.

### How to Think About It
Follow the module-wide ladder. First measure and estimate; then reduce bytes and columns; then address peak memory; only then evaluate engine/scaling changes. Every change must preserve correctness and be benchmarked against the SLA and cost objective.

### Solution
Recommended sequence:

1. Establish a baseline: runtime, bytes read, peak RSS, cost/run, input sizes, and join behavior.
2. Audit projection pruning, predicate pushdown, and partition pruning using execution-plan evidence.
3. Remove unnecessary columns and rows before the join.
4. Estimate the in-memory representations and measure peak memory during the join.
5. Check for copies, join expansion, skew, and other temporary allocations.
6. Compare peak usage against cgroup/container limits and add justified headroom.
7. If the workload still cannot meet the SLA, evaluate the simplest adequate engine/scaling option.
8. Profile remaining CPU hot paths.
9. If a true hot loop remains, evaluate vectorization, then Numba/Cython as justified.
10. Benchmark each major change using representative data, controlled cache conditions, warm-ups, repetitions, and median/percentile reporting.
11. Calculate cost per run and cost per unit of work.
12. Choose the configuration that meets the 25-minute SLA with the best justified cost/performance trade-off.

### Explanation
This plan avoids treating every symptom as a scaling problem. Excessive scan volume can inflate both runtime and cost; peak-memory failures can be reduced by shrinking the workload before the join; and only measured bottlenecks should receive more compute or compilation.

### Production Insight
A senior engineer fixes the workload before fixing the infrastructure. The final recommendation should show evidence for every major architectural change.

## Question 32 — Assess a Dask Cluster with Conflicting Signals

### Difficulty
Advanced

### Topics Covered
- Topics 01, 03, 06
- Dask Dashboard
- Partition Sizing
- Spilling
- Benchmarking

### Problem
A Dask cluster was doubled from 8 to 16 workers. Runtime improved only from 30 to 27 minutes, while cost increased substantially. The dashboard shows many tiny partitions, some oversized partitions spilling, and a long shuffle. What should the next engineering action be?

### How to Think About It
The weak speedup and higher cost suggest the added workers are not addressing the dominant bottlenecks. Use dashboard evidence to fix partitioning and shuffle behavior before another scale-out experiment.

### Solution
Next action:

1. Stop treating worker count as the primary tuning variable.
2. Inspect partition sizes and rebalance the dataset.
3. Reduce excessive tiny partitions to lower scheduler overhead.
4. Investigate oversized partitions causing worker spilling.
5. Analyze the long shuffle and determine whether the operation can be avoided or made cheaper.
6. Reduce data volume/columns before the expensive operation where possible.
7. Re-run a controlled benchmark with the same workload and measured configuration.
8. Compare runtime, peak memory/spilling, throughput, and cost per run.
9. Only after these changes should worker count be revisited.

The 8→16 worker change produced only a 30/27 ≈ **1.11× speedup**, which is poor relative to the resource increase.

### Explanation
The dashboard provides direct evidence that the system is suffering from partition and shuffle issues. More workers cannot automatically fix a badly shaped workload and may amplify cost without proportional useful work.

### Production Insight
Use the Dask dashboard as a diagnostic instrument. Tune data distribution and expensive operations before increasing cluster size.

## Question 33 — Design a Ray GPU Utilization Experiment

### Difficulty
Advanced

### Topics Covered
- Topics 01, 04, 06, 07
- Ray Data
- Batch Size
- Actor Pools
- GPU Economics

### Problem
A Ray Data inference pipeline uses 4 GPUs. Current measurements show 35% GPU utilization, 70% CPU utilization, 200 inferences/s, and a hypothetical cost of $0.004 per inference. The SLA requires at least 250 inferences/s. Design the experiment sequence and explain what evidence would justify adding GPUs.

### How to Think About It
The system is GPU-backed but not GPU-saturated. First determine whether batch size, actor concurrency, model loading, or CPU preprocessing is starving the GPU. The SLA target should drive the decision.

### Solution
Experiment sequence:

1. Record the baseline: 200 inferences/s, 35% GPU utilization, 70% CPU utilization, batch size, actor-pool configuration, and $0.004/inference.
2. Test a larger batch size within model-memory limits.
3. Test actor-pool/concurrency changes to keep GPUs fed.
4. Measure CPU preprocessing and pipeline backpressure.
5. Confirm whether model loading is reused per actor rather than repeatedly performed.
6. For each controlled configuration, measure throughput, GPU utilization, memory safety, and cost per inference.
7. Select the smallest configuration that reliably reaches ≥250 inferences/s.
8. Add GPUs only if the current GPUs remain the limiting resource after batch/concurrency and upstream bottlenecks are addressed.

For example, if a tested configuration reaches 260 inferences/s at the same 4 GPUs, adding GPUs is unnecessary. If all reasonable batch/concurrency configurations plateau below 250 while GPUs are consistently saturated, then adding GPUs becomes evidence-based.

### Explanation
The initial 35% GPU utilization is evidence against blindly adding GPUs. A production experiment must distinguish accelerator starvation from accelerator capacity limits.

### Production Insight
GPU economics is throughput per dollar, not GPU count. The SLA provides the acceptance criterion for the experiment.

## Question 34 — Evaluate a Hot Loop Optimization with Benchmark Evidence

### Difficulty
Advanced

### Topics Covered
- Topics 05, 06, 07
- Profiling
- Numba/Cython
- Benchmarking
- Cost

### Problem
A Python sessionization loop consumes 75% of CPU time. Three implementations are measured after warm-up on representative data:

| Implementation | Median runtime | Peak memory | Cost/run |
|---|---:|---:|---:|
| Python loop | 120 s | 2 GB | $0.80 |
| Vectorized Polars | 55 s | 2.5 GB | $0.80 |
| Numba loop | 48 s | 2.1 GB | $0.82 |

The SLA is 60 s. Which implementation should be preferred initially, and when might Numba still be justified?

### How to Think About It
Compare each option against the SLA and consider whether the additional speed is worth its complexity and cost. Do not optimize for the fastest number alone.

### Solution
The **vectorized Polars implementation** should be preferred initially because:

- it meets the 60-second SLA at 55 seconds;
- it costs $0.80/run, the same as the baseline;
- it avoids the additional compiled-loop complexity represented by the Numba option;
- its peak memory is only modestly higher in the illustrative data.

Numba is still justified if the SLA becomes materially tighter, if future workload growth makes 55 seconds insufficient, or if other evidence shows the compiled loop provides meaningful value that outweighs its additional cost and maintenance/deployment complexity.

The Numba result is faster at 48 seconds, but it does not automatically win because the stated requirement is already satisfied by Polars.

### Explanation
This is an example of the optimization ladder in action: eliminate the Python hot path through a simpler vectorized engine before adding compiler complexity. The numbers are illustrative benchmark data, not universal performance claims.

### Production Insight
A production optimization is successful when it satisfies the requirement at acceptable cost and complexity—not when it achieves the lowest benchmark number.

## Question 35 — Investigate a Benchmark Regression

### Difficulty
Advanced

### Topics Covered
- Topic 06 — Benchmarking
- Cache State
- CI Regression Detection

### Problem
A CI benchmark reports that a pipeline became 12% slower after a code change. The benchmark runner changed at the same time, the OS page-cache state is unknown, and only one run was recorded. What should you conclude, and how should the regression test be redesigned?

### How to Think About It
Separate an observed measurement from a credible regression conclusion. The environment changed and the sample size is one, so the result is not sufficient to attribute the slowdown to the code change.

### Solution
Conclusion: the 12% result is **evidence worth investigating, not proof of a code regression**.

Redesign:

1. Use stable benchmark runners.
2. Pin relevant software versions.
3. Control or record cache state: cold, warm, OS page cache, engine cache, and remote-storage conditions as applicable.
4. Use warm-ups.
5. Run multiple repetitions.
6. Report median and variability/percentiles.
7. Keep the dataset representative and stable.
8. Record configuration and environment.
9. Define a regression tolerance.
10. Compare against a historical baseline in CI.
11. Investigate only after the measurement methodology is sufficiently stable.

### Explanation
Benchmark regression detection is itself an experimental-design problem. If the runner and cache state change simultaneously with the code, attribution becomes ambiguous.

### Production Insight
A trustworthy CI performance signal requires a stable measurement system. Otherwise teams can waste time chasing benchmark noise.

## Question 36 — Choose a Cost-Optimal Configuration Under an SLA

### Difficulty
Advanced

### Topics Covered
- Topics 06, 07
- Benchmarking
- Strong Scaling
- Cost per Run
- SLA

### Problem
A production pipeline has a 20-minute SLA. The following are illustrative benchmark results:

| Config | Runtime | Cost/run | Peak memory |
|---|---:|---:|---:|
| A | 28 min | $3 | 40 GB |
| B | 19 min | $4.50 | 52 GB |
| C | 14 min | $8 | 70 GB |
| D | 18 min | $7 | 90 GB |

The execution environment has a 64 GB memory limit. Which configuration is the strongest default choice, and what additional evidence would you request before finalizing?

### How to Think About It
First eliminate configurations that violate the SLA or memory constraint. Then compare cost among feasible options and identify uncertainty such as variance and reliability.

### Solution
A is infeasible because it misses the 20-minute SLA.

C is infeasible because its 70 GB peak memory exceeds the 64 GB limit.

B and D meet the SLA and memory limit:

- B: 19 min, $4.50, 52 GB
- D: 18 min, $7, 90 GB — although D meets the stated 64 GB limit? No: 90 GB exceeds it, so D is also infeasible.

Therefore **B is the only feasible configuration among the four**.

Before finalizing, request repeated benchmark results, percentile latency, failure/retry behavior, workload representativeness, and confirmation that 52 GB leaves sufficient production headroom.

### Explanation
The strongest configuration is constrained by SLA, memory, reliability, and cost—not raw speed. A configuration that violates a hard resource limit is not a valid optimization candidate.

### Production Insight
Always apply hard constraints before optimizing among candidates. Then optimize the remaining feasible set.

## Question 37 — Evaluate a Spark-to-Dask-or-Ray Migration

### Difficulty
Advanced

### Topics Covered
- Topics 03, 04, 06, 07
- Engine Selection
- Benchmarking
- Cost
- Operational Risk

### Problem
A team wants to replace a stable Spark pipeline with Dask or Ray because engineers prefer Python APIs. The pipeline performs large tabular transformations, joins, and aggregations, has no GPU requirement, and already meets its SLA. What evidence would you require before approving a migration?

### How to Think About It
The burden of proof is on the proposed change. Existing correctness, SLA, and operational stability are valuable constraints. A preference for a different API is not enough to justify migration risk.

### Solution
Require:

1. Workload characterization: data size, growth, joins, aggregations, partition/shuffle behavior, and memory profile.
2. A representative benchmark comparing Spark with Dask and/or Ray Data.
3. Correctness equivalence tests.
4. Strong-scaling and relevant performance measurements.
5. Peak-memory and failure behavior.
6. Operational comparison: deployment, monitoring, debugging, scheduling, and recovery.
7. Cost per run and cost per unit of work.
8. Migration effort and rollback strategy.
9. Evidence that the new system provides a material benefit—performance, cost, maintainability, or capability—that justifies the migration risk.

### Explanation
Dask and Ray are not automatically replacements for Spark. The module explicitly requires workload-based comparison among Dask, Ray, Spark, Polars, and DuckDB, including operational complexity and cost.

### Production Insight
Do not migrate a production platform because a framework is fashionable or more familiar. Migrate when measured benefits outweigh technical and operational risk.

## Question 38 — Integrated Optimization Review

### Difficulty
Advanced

### Topics Covered
- Topics 01–07
- Estimation
- Pushdown
- Engine Selection
- Scaling
- Profiling
- Benchmarking
- Cost

### Problem
A pipeline processes 10 TB/day. It currently scans 10 TB, takes 45 minutes, uses a distributed cluster, and costs a hypothetical $18/run. Profiling shows only 5% of CPU time is spent in a Python loop; the scan reads many unused columns. The SLA is 30 minutes. Outline the complete optimization plan using the module's sequence: Estimate → Read less → Choose engine → Scale → Profile → Benchmark → Price.

### How to Think About It
Do not start with the 5% Python loop because the scan and SLA gap are larger issues. Estimate the workload, reduce unnecessary reads, reassess whether the current distributed architecture is still appropriate, then address remaining measured bottlenecks.

### Solution
Plan:

1. **Estimate:** quantify bytes/day, memory footprint, throughput, peak memory, partition sizes, and current cost/unit.
2. **Read less:** apply projection pruning, predicate pushdown, and partition pruning; audit bytes scanned versus bytes needed.
3. **Choose engine:** reassess whether the reduced workload still requires the current distributed architecture; evaluate a single-node or different engine only if estimates support it.
4. **Scale:** if distributed execution remains necessary, right-size workers/partitions and avoid unnecessary shuffles.
5. **Profile:** reassess CPU, memory, I/O, and the remaining Python loop after scan reduction.
6. **Compile only if justified:** the loop is only 5% of CPU time, so Numba/Cython is unlikely to be the first lever unless later evidence changes.
7. **Benchmark:** use representative data, warm-ups, repetitions, controlled cache conditions, and report runtime, throughput, peak memory, bytes read, and cost.
8. **Price:** compare cost/run and cost/unit before and after.
9. **Decision:** select the simplest configuration that reliably reaches ≤30 minutes with acceptable cost and operational risk.

### Explanation
This follows the central module philosophy. A small CPU hot path should not distract from a 10 TB scan problem. Reducing bytes read can improve both runtime and cost before any compiler or cluster expansion is considered.

### Production Insight
Senior optimization work prioritizes the highest-leverage bottleneck. The final recommendation should be evidence-backed and reversible where practical.

## Question 39 — Decide Whether to Replace Spark with Dask or Ray

### Difficulty
Advanced

### Topics Covered
- Topics 01, 03, 04, 06, 07
- Migration Decision
- Cost/Performance/SLA Trade-off

### Problem
A company runs a 2 TB/day Spark workload with large joins and aggregations. It takes 40 minutes at a hypothetical $10/run. A proposed Dask implementation takes 32 minutes at $9/run, while a proposed Ray Data implementation takes 29 minutes at $14/run. The SLA is 35 minutes. The alternatives have only been tested once on a development environment. Should the migration be approved?

### How to Think About It
Separate technical feasibility from production approval. Dask appears to meet the SLA at lower illustrative cost, but one development benchmark is insufficient evidence for a production migration.

### Solution
Do **not approve immediately**.

Initial interpretation:

- Spark: 40 min → misses SLA, $10/run.
- Dask: 32 min → appears to meet SLA, $9/run.
- Ray: 29 min → appears to meet SLA, but $14/run.

Dask is the most promising candidate from the illustrative numbers, but the evidence is weak because each alternative was tested only once in development.

Before approval:

1. Build representative production-like datasets, including join/aggregation characteristics.
2. Repeat benchmarks with warm-ups, controlled cache state, stable environments, and pinned versions.
3. Measure median/percentiles and variance.
4. Validate correctness.
5. Measure peak memory, shuffle/communication behavior, and failure/retry behavior.
6. Compare cost per run and cost per unit of work.
7. Evaluate operational complexity and monitoring/debugging.
8. Test growth and scaling behavior.
9. Establish rollback criteria.

If repeated production-like testing confirms Dask meets the 35-minute SLA at lower or acceptable cost with acceptable reliability and operational risk, then a migration or controlled pilot can be justified.

### Explanation
The benchmark values are explicitly illustrative. The key decision is that performance and cost alone do not establish production readiness. The migration must survive representative testing and operational review.

### Production Insight
A senior design review distinguishes “promising benchmark” from “production evidence.” Approve a controlled migration only when the evidence covers correctness, SLA, cost, scaling, and operational risk.

## Question 40 — Complete Production Design Review

### Difficulty
Advanced

### Topics Covered
- Topics 01–07
- Data Growth
- Memory Constraints
- Pushdown
- Distributed Processing
- Benchmarking
- Cost
- SLA

### Problem
A production data platform has this situation:

- Current input: 4 TB/day.
- Expected growth: 2× over the next year.
- Current runtime: 50 minutes.
- SLA: 35 minutes.
- Current hypothetical cost: $20/run.
- A scan audit shows 60% of selected columns are unused.
- The largest join produces a peak-memory footprint approximately 2.2× the in-memory input representation.
- The current Dask cluster has both tiny partitions and a small number of oversized partitions.
- A Python loop accounts for 8% of CPU time.
- A benchmark of a larger cluster reduces runtime to 34 minutes but increases cost to $31/run.
- All benchmark values are illustrative.

As the senior Data Engineer, produce a complete recommendation: what should be fixed first, what should not be optimized yet, what evidence should be collected, and how would you decide whether the $31/run configuration is justified?

### How to Think About It
Treat this as a design review. Start with the workload and hard constraints, then apply the optimization ladder. The 8% Python loop is unlikely to be the first lever, and the larger cluster already meets the SLA but at substantially higher cost. The question is whether the same SLA can be met more efficiently after reducing unnecessary work and fixing partition/memory issues.

### Solution
Recommendation:

**1. Establish the baseline and capacity model.**
Measure runtime, throughput, bytes read, peak RSS, partition sizes, shuffle volume, cost/run, and workload growth. Project the 2× growth rather than optimizing only today's 4 TB/day.

**2. Read less first.**
The scan audit already identifies a high-value opportunity: 60% of selected columns are unused. Apply projection pruning and audit predicate/partition pruning as well. Re-measure bytes scanned and runtime.

**3. Fix partition shape and memory behavior.**
Investigate tiny partitions for scheduler overhead and oversized partitions for worker spilling/peak memory. Repartition where justified, reduce data before expensive operations, and ensure worker/container memory has sufficient headroom.

**4. Reassess distributed capacity after workload reduction.**
The $31/run configuration meets the 35-minute SLA at 34 minutes, but it costs 55% more than the current $20/run baseline:

`($31 - $20) / $20 × 100 = 55%`

It should not automatically become the permanent configuration.

**5. Do not prioritize the Python loop yet.**
At 8% of CPU time, it is not an obvious dominant bottleneck. After scan and partition improvements, profile again. If it becomes material, evaluate vectorization/Polars/NumPy/SQL first, then Numba or Cython only if justified.

**6. Re-benchmark correctly.**
Use representative data, include expected growth tiers, warm-ups, repetitions, median/percentiles, controlled cache conditions, stable runners, fixed versions, and one-variable-at-a-time experiments. Record runtime, throughput, peak memory, bytes read, and cost.

**7. Decide using SLA plus unit economics.**
If a lower-cost configuration reaches the 35-minute SLA with acceptable variance, reliability, and headroom, prefer it over $31/run. If the larger configuration remains necessary, calculate the business value of the 16-minute improvement from the original 50 minutes and confirm that the additional cost is justified.

**8. Consider growth explicitly.**
The 2× growth forecast may change the feasible architecture. Test scaling behavior and capacity headroom rather than assuming today's configuration will remain adequate.

The correct final decision is therefore: **do not reject the $31/run configuration, but do not accept it as the default merely because it meets the SLA. First reduce unnecessary scan work, correct partition/memory behavior, then remeasure the minimum-cost configuration that reliably satisfies the SLA under representative and growth-oriented workloads.**

### Explanation
This scenario integrates the complete module philosophy. The existing 34-minute result is useful evidence, but it is not necessarily the optimal architecture. The largest known opportunities are workload reduction and data-distribution problems, while the Python loop is a comparatively small measured fraction of CPU time.

The 55% cost increase is also not inherently bad or good. Cost must be evaluated against the SLA, reliability, workload growth, and unit economics. If a higher-cost configuration is required to protect a business-critical SLA, it may be justified; if the same SLA can be achieved by doing less work and fixing partitioning, paying 55% more would be poor optimization.

### Production Insight
A senior Data Engineer does not optimize a single metric in isolation. The production decision should be based on measured workload shape, correctness, SLA reliability, scaling behavior, cost per unit of work, and expected growth. The objective is the **simplest adequate system at the required performance and cost envelope**.


# Module Coverage Audit

| Learning File | Concepts Tested | Questions |
|---|---|---|
| Topic 01 — Estimating Data Size and Memory Footprint | Rows × columns × bytes, disk vs memory, expansion factors, peak memory, throughput, capacity planning | Q1, Q2, Q9, Q11, Q21, Q23, Q30, Q31, Q38, Q40 |
| Topic 02 — Predicate Pushdown and Projection Pruning | Projection pruning, predicate pushdown, partition pruning, verification, blockers, scan audits, cost impact | Q3, Q12, Q22, Q29, Q31, Q38, Q40 |
| Topic 03 — Parallel DataFrames with Dask | Lazy graphs, partitions, repartitioning, shuffles, dashboard, spilling, memory, engine selection | Q4, Q13, Q14, Q20, Q23, Q30, Q32, Q38, Q39, Q40 |
| Topic 04 — Ray Data Overview | `map_batches`, blocks, batch size, CPU/GPU resources, actor pools, inference, GPU utilization, engine choice | Q5, Q15, Q20, Q24, Q30, Q33, Q39, Q40 |
| Topic 05 — Numba and Cython for Hot Loops | Profiling, vectorization first, `@njit`, Cython decision, compilation justification, deployment complexity | Q6, Q16, Q25, Q34, Q38, Q40 |
| Topic 06 — Benchmarking Pipelines | Metrics, representative data, warm-up, repetitions, median, variance, cache state, strong/weak scaling, Amdahl's law, regression detection | Q7, Q9, Q17, Q18, Q26, Q27, Q28, Q34, Q35, Q36, Q38, Q39, Q40 |
| Topic 07 — Compute Cost Optimization | Cost/run, cost/TB, unit economics, engine selection, GPU economics, SLA/cost trade-offs, right-sizing reasoning | Q8, Q19, Q20, Q24, Q28, Q29, Q30, Q33, Q34, Q36, Q39, Q40 |

## Difficulty and Count Verification

| Difficulty | Questions | Count |
|---|---|---:|
| Basic | Q1–Q10 | 10 |
| Moderate | Q11–Q20 | 10 |
| Hard | Q21–Q30 | 10 |
| Advanced | Q31–Q40 | 10 |
| **Total** | **Q1–Q40** | **40** |

## Question-Type Coverage

The bank includes:

- Numerical and estimation problems
- Code interpretation
- Debugging and diagnosis
- Architecture and engine-selection decisions
- Benchmark interpretation
- Cost and unit-economics calculations
- Production optimization scenarios
- Scaling and Amdahl's law
- SLA and cost/performance trade-offs
- Cross-topic integrated design reviews

## Quality-Control Summary

- Exactly 40 questions
- Exactly 10 Basic, 10 Moderate, 10 Hard, and 10 Advanced
- Every question includes Problem → How to Think About It → Solution → Explanation → Production Insight
- Cross-topic questions are concentrated in Hard and Advanced sections
- Hypothetical benchmark and pricing values are explicitly identified
- No universal performance claims are presented as measured facts
- The question bank remains within Module 2.21 scope

# Final Practice Guidance

Do not optimize by memorizing framework names. For each problem, practice the engineering sequence:

> **Estimate the workload → reduce unnecessary work → choose the simplest adequate engine → scale only when justified → profile the actual hot path → compile only when justified → benchmark honestly → calculate unit economics → make the production decision.**

A strong Module 2.21 answer should explain not only **what** to change, but **why**, **what evidence would justify the change**, **how correctness and SLA would be protected**, and **whether the resulting performance is worth its operational and compute cost**.
