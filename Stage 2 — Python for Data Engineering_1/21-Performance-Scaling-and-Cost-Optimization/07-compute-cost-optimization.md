# 07 — Compute Cost Optimization

> **Stage 2 → Module 2.21 — Performance, Scaling, and Cost Optimization**  
> **Phase D — Prove It and Pay Less**  
> **Level: Advanced**

## 1. Why Compute Cost Optimization Matters

Compute cost optimization is the engineering discipline of reducing the resources and money required to process data while preserving correctness, reliability, scalability, and required SLAs.

The module philosophy is:

> **Estimate → Read less → Scale only when needed → Profile → Benchmark → Price**

The central optimization ladder is:

```text
Do less work
    ↓
Use a better engine
    ↓
Use more cores
    ↓
Use more machines
    ↓
Compile the hot loop
```

The first principle is:

> **Do not optimize what you have not measured.**

And the economic version is:

> **The cheapest optimization is often avoiding unnecessary work altogether.**

A production Data Engineer should not begin with:

> “Which cloud instance is cheapest?”

Instead ask:

> **“Why does this workload consume these resources, what does each unit of work cost, and what is the cheapest configuration that still meets the business requirement?”**

This topic is the economic conclusion of the performance-engineering work covered throughout Module 2.21.

---

# 2. What Does Compute Cost Actually Mean?

Compute cost is broader than an hourly instance price.

A data workload can create cost through:

- CPU consumption
- memory allocation
- worker/node consumption
- execution time
- cluster runtime
- serverless compute
- container compute
- managed-service compute
- idle compute
- over-provisioned compute
- under-utilized compute
- retry cost
- failed-job cost
- inefficient algorithms
- excessive data movement
- unnecessary scans
- poor partitioning
- bad parallelism

A useful conceptual relationship is:

```text
runtime × resource consumption × resource price
```

However, real cloud billing can be more complicated because actual bills may also involve:

- storage,
- network transfer,
- managed-service charges,
- billing granularity,
- resource-specific pricing,
- minimum charges,
- committed-use arrangements,
- discounts,
- interruptions,
- retries,
- ancillary services.

Therefore a simple cost model is an engineering approximation, not automatically an exact cloud bill.

## Important distinction

> **A slow pipeline is not automatically an expensive pipeline, and a fast pipeline is not automatically a cheap pipeline.**

For example:

```text
Configuration A:
8 workers × 20 minutes

Configuration B:
4 workers × 35 minutes
```

A may finish sooner, but whether it is cheaper depends on the actual resource pricing and billing model.

The engineering objective is therefore not:

```text
minimum runtime
```

or:

```text
minimum hourly price
```

but:

```text
required business outcome
+
required SLA
+
correctness
+
reliability
+
lowest justified cost
```

---

# 3. Cost Optimization Mental Model

Start with the workload:

```text
Data Volume
    ↓
Bytes Read
    ↓
CPU / Memory / Network Work
    ↓
Resources Required
    ↓
Execution Time
    ↓
Infrastructure Consumption
    ↓
Cloud / Platform Cost
```

Engineers can intervene at several points:

```text
Reduce Data
     ↓
Reduce Work
     ↓
Improve Query / Execution Plan
     ↓
Improve Parallelism
     ↓
Choose Appropriate Engine
     ↓
Right-size Resources
     ↓
Scale Dynamically
     ↓
Reduce Idle Time
     ↓
Benchmark
     ↓
Measure Cost
```

This ordering matters.

If you can eliminate 90% of unnecessary work, buying a larger cluster to execute that unnecessary work faster is usually the wrong first move.

---

# 4. Cost Optimization vs Performance Optimization

These disciplines overlap but are not identical.

| Discipline | Primary question |
|---|---|
| Performance optimization | How can this workload execute faster or process more work? |
| Compute optimization | How can resources be used more efficiently? |
| Cost optimization | How can the workload satisfy its requirements at lower cost? |
| Resource optimization | What resource allocation is appropriate? |
| Capacity planning | What resources will be needed as workload changes? |

These objectives can conflict.

Suppose:

```text
Configuration A:
8 workers × 20 minutes

Configuration B:
4 workers × 35 minutes
```

A is faster.

B may use less compute.

If the workload has a strict SLA, A may be the correct choice even if it costs more.

Spending more can be justified when it:

- meets an SLA,
- reduces operational risk,
- reduces failure probability,
- enables required throughput,
- reduces downstream delays.

Therefore:

> **Optimize for the required business objective, not simply the lowest raw compute bill.**

---

# 5. Cost Metrics

Track both absolute cost and unit economics.

Important metrics include:

- total cost per run
- cost per successful run
- cost per GB processed
- cost per TB processed
- cost per million records
- cost per pipeline
- cost per day
- cost per month
- cost per dataset
- cost per customer/workload where relevant
- CPU utilization
- memory utilization
- compute utilization
- execution time
- throughput
- bytes read
- bytes written
- shuffle volume
- network transfer
- retry count
- failed-job cost

## Why unit economics matter

Consider:

```text
Monthly compute cost = $10,000
```

This alone says little.

Compare:

```text
System A:
$10,000 for 10 TB

System B:
$10,000 for 100 TB
```

System B has substantially better processing economics.

Useful unit metrics include:

```text
$/GB
$/TB
$/million rows
$/successful pipeline run
$/feature generated
$/embedding generated
$/training dataset processed
```

The exact unit should match the business workload.

---

# 6. Build a Simple Cost Model

Start with a deliberately simple **hypothetical example**.

```text
workers = 8
cost_per_worker_hour = $0.50
runtime = 30 minutes
```

Compute cost:

```text
8 × $0.50 × 0.5 hours
= $2.00
```

This is an educational approximation.

## Python calculator

```python
def estimate_compute_cost(
    workers: int,
    worker_hourly_cost: float,
    runtime_hours: float,
) -> float:
    return workers * worker_hourly_cost * runtime_hours


cost = estimate_compute_cost(
    workers=8,
    worker_hourly_cost=0.50,
    runtime_hours=0.5,
)

print(f"Estimated compute cost: ${cost:.2f}")
```

## Extended model

```python
def estimate_total_cost(
    *,
    workers: int,
    worker_hourly_cost: float,
    runtime_hours: float,
    driver_hourly_cost: float = 0.0,
    storage_cost: float = 0.0,
    network_cost: float = 0.0,
    retry_cost: float = 0.0,
    idle_cost: float = 0.0,
) -> float:
    worker_cost = workers * worker_hourly_cost * runtime_hours
    driver_cost = driver_hourly_cost * runtime_hours

    return (
        worker_cost
        + driver_cost
        + storage_cost
        + network_cost
        + retry_cost
        + idle_cost
    )
```

## Cost per unit

```python
def cost_per_gb(total_cost: float, gb_processed: float) -> float:
    if gb_processed <= 0:
        raise ValueError("gb_processed must be positive")
    return total_cost / gb_processed


def cost_per_tb(total_cost: float, tb_processed: float) -> float:
    if tb_processed <= 0:
        raise ValueError("tb_processed must be positive")
    return total_cost / tb_processed


def cost_per_million_records(
    total_cost: float,
    records: int,
) -> float:
    if records <= 0:
        raise ValueError("records must be positive")
    return total_cost / (records / 1_000_000)
```

## Monthly and annual projection

```python
def monthly_cost(
    cost_per_run: float,
    runs_per_day: int,
    days_per_month: int = 30,
) -> float:
    return cost_per_run * runs_per_day * days_per_month


def annualized_cost(
    cost_per_run: float,
    runs_per_day: int,
    days_per_year: int = 365,
) -> float:
    return cost_per_run * runs_per_day * days_per_year
```

Use these models to reason about economics. Replace assumptions with actual billing and usage data before making financial decisions.

---

# 7. Establish a Cost Baseline

Optimization without a baseline is guesswork.

Before changing anything, record:

- dataset size
- rows
- bytes
- runtime
- CPU usage
- memory usage
- workers
- worker size
- engine
- configuration
- bytes read
- bytes written
- shuffle volume
- retries
- cost
- SLA
- correctness

Use:

| Metric | Baseline |
|---|---:|
| Data processed | ... |
| Runtime | ... |
| Workers | ... |
| Peak memory | ... |
| CPU utilization | ... |
| Bytes read | ... |
| Shuffle | ... |
| Cost/run | ... |
| Cost/TB | ... |
| SLA | ... |
| Correctness | Pass/Fail |

Every later optimization should be compared against this baseline.

---

# 8. Connect Cost Optimization to Module 2.21

## Topic 01 — Estimating Data Size and Memory Footprint

Estimation helps prevent over-provisioning.

It informs:

- memory requirements,
- worker sizing,
- partition sizing,
- capacity planning.

A good estimate can stop an engineer from selecting a resource configuration based purely on fear of OOM.

## Topic 02 — Predicate Pushdown and Projection Pruning

Reading less can reduce:

- I/O,
- CPU,
- memory,
- runtime,
- potentially compute cost.

The chain is:

```text
Read fewer rows/columns
        ↓
Less data movement
        ↓
Less processing
        ↓
Less resource consumption
        ↓
Potentially lower cost
```

Measure the actual effect.

## Topic 03 — Dask

Cost depends on:

- worker sizing,
- parallelism,
- scheduler overhead,
- cluster utilization,
- scaling behavior.

## Topic 04 — Ray Data

Cost depends on:

- actor count,
- batch size,
- CPU/GPU allocation,
- distributed execution,
- GPU utilization.

## Topic 05 — Numba and Cython

Reducing CPU time can reduce compute consumption when CPU work is material.

Compilation should still follow the optimization ladder:

```text
Profile
→ identify hot loop
→ try simpler optimizations
→ benchmark
→ compile only when justified
```

## Topic 06 — Benchmarking

Benchmarking provides the evidence required to evaluate:

- performance impact,
- cost impact,
- regression,
- resource efficiency,
- fair configuration comparisons.

Topic 07 is therefore the economic conclusion of the performance-engineering process.

---

# 9. Do Less Work First

The first cost optimization is workload reduction.

Prefer:

- filtering earlier,
- reading fewer columns,
- reading fewer files,
- incremental processing,
- avoiding unnecessary recomputation,
- caching only useful intermediate results,
- eliminating redundant transformations,
- avoiding duplicate jobs,
- reducing unnecessary joins,
- reducing unnecessary shuffles,
- efficient formats,
- partition pruning,
- query pruning.

## Example — DuckDB

```python
import duckdb

result = duckdb.sql(
    """
    SELECT customer_id, amount
    FROM 'sales/*.parquet'
    WHERE country = 'IN'
    """
)
```

If the data is appropriately organized and the engine can exploit its metadata and statistics, this logical query may avoid processing irrelevant data.

Do not claim a specific percentage saving without measurement.

## Example — Polars

```python
import polars as pl

result = (
    pl.scan_parquet("sales/*.parquet")
    .filter(pl.col("country") == "IN")
    .select(["customer_id", "amount"])
    .group_by("customer_id")
    .agg(pl.col("amount").sum())
    .collect()
)
```

The lazy execution model can allow the engine to optimize the scan and projection.

Again, measure the actual effect.

---

# 10. Compute vs Data Scan Cost

Unnecessary scanning creates multiple forms of waste:

```text
More bytes read
    ↓
More I/O
    ↓
More CPU
    ↓
More memory pressure
    ↓
Longer runtime
    ↓
More resource consumption
    ↓
Potentially higher cost
```

Important techniques include:

- column pruning,
- predicate pushdown,
- partition pruning,
- Parquet statistics,
- appropriate file sizing,
- small-file mitigation,
- compression,
- efficient columnar formats.

## Small-file problem

Many tiny files can create:

- metadata overhead,
- scheduling overhead,
- connection overhead,
- inefficient reads.

Do not interpret this as “always make files as large as possible.” The right file layout depends on:

- engine,
- storage system,
- workload,
- partitioning,
- concurrency.

Benchmark the resulting workload.

---

# 11. Right-Sizing

Right-sizing means choosing resource capacity appropriate to the actual workload.

Think in terms of:

```text
Too large
Too small
Right-sized
```

## Too large

Possible symptoms:

- low CPU utilization,
- low memory utilization,
- idle workers,
- high cost,
- little performance benefit.

## Too small

Possible symptoms:

- OOM,
- excessive spilling,
- long runtime,
- queueing,
- repeated failures,
- SLA violations.

## Right-sized

A right-sized system has enough capacity to:

- complete reliably,
- meet the SLA,
- tolerate expected variability,
- avoid unnecessary idle capacity.

“Bigger machine = faster” is not universally true.

A workload may instead be:

- CPU-bound,
- memory-bound,
- I/O-bound,
- network-bound,
- shuffle-bound,
- scheduler-bound.

Profiling identifies the actual constraint.

---

# 12. Resource Utilization

Track:

- CPU utilization,
- memory utilization,
- worker utilization,
- GPU utilization,
- cluster utilization,
- idle workers,
- executor idle time.

Distinguish:

```text
Allocated capacity
        vs
Actually used capacity
```

For example:

```text
Allocated:
16 workers

Average active:
3 workers
```

This can indicate significant waste if sustained and if the spare capacity is not required for burst handling or SLA protection.

Low utilization is not automatically waste. Interpret it alongside:

- workload variability,
- peak demand,
- failure tolerance,
- scaling latency,
- SLA requirements.

---

# 13. Scaling Strategies and Cost

## Vertical scaling

```text
Bigger machine
```

Potential advantages:

- more CPU,
- more memory,
- fewer nodes,
- simpler coordination.

Potential costs:

- over-provisioning,
- expensive nodes,
- diminishing returns,
- hardware constraints.

## Horizontal scaling

```text
More machines
```

Potential advantages:

- distributed capacity,
- parallel execution,
- larger aggregate memory.

Additional costs can include:

- network traffic,
- coordination,
- shuffle,
- scheduling,
- serialization.

## Elastic scaling

```text
Scale up/down based on workload
```

Important parameters include:

- minimum workers,
- maximum workers,
- scale-up latency,
- scale-down latency,
- workload variability,
- burst behavior.

Autoscaling can increase cost if configured poorly.

Examples:

- minimum capacity too high,
- scale-up triggers too aggressively,
- scale-down is too slow,
- workload finishes before scaling can amortize its startup cost,
- resource churn is excessive.

---

# 14. Batching and Resource Efficiency

Batch size affects:

- CPU utilization,
- memory,
- network,
- scheduling overhead,
- throughput,
- cost.

Conceptually:

```text
Very small batches
    ↓
More overhead

Very large batches
    ↓
More memory pressure
```

A useful operating point balances:

```text
throughput
+
memory
+
latency
+
resource cost
```

Apply this reasoning to:

- Ray Data,
- Spark,
- Dask,
- API ingestion,
- batch inference.

Example:

```text
batch_size = 32
→ low memory
→ more scheduling overhead

batch_size = 4096
→ potentially higher throughput
→ higher memory pressure

batch_size = 1024
→ potentially balanced
```

These are illustrative relationships, not measured results.

---

# 15. Parallelism and Cost

More parallelism does not automatically mean lower cost.

Too little parallelism can create:

```text
Low utilization
+
long runtime
```

Too much can create:

```text
Scheduling overhead
+
small tasks
+
coordination
+
contention
```

Connect parallelism to:

- Dask partitions,
- Spark partitions,
- Ray blocks,
- CPU cores.

The objective is:

> **Effective parallelism, not maximum parallelism.**

The correct level is found through measurement.

---

# 16. Spark Cost Optimization

Production Spark cost optimization should consider:

- executor count,
- executor cores,
- executor memory,
- driver sizing,
- partition sizing,
- shuffle reduction,
- broadcast joins,
- Adaptive Query Execution,
- caching,
- unnecessary actions,
- data scans,
- file sizing,
- small-file mitigation,
- dynamic allocation,
- autoscaling.

## 16.1 Avoid unnecessary scans

Use:

- predicate pushdown,
- projection pruning,
- partition pruning,
- efficient file layouts.

## 16.2 Reduce shuffle

Shuffle can create:

- network traffic,
- disk I/O,
- serialization,
- memory pressure,
- longer runtime.

Investigate joins, aggregations, partitioning, and skew.

## 16.3 Broadcast joins

When the smaller dataset is genuinely small enough:

```python
from pyspark.sql import functions as F

result = large_df.join(
    F.broadcast(small_df),
    on="customer_id",
    how="left",
)
```

Do not broadcast arbitrary datasets merely because broadcast joins can be faster. Memory constraints matter.

## 16.4 Avoid unnecessary actions

A debugging action can become production waste:

```python
df.count()
df.write.parquet(output_path)
```

If `count()` is not required by the business logic, it may represent an unnecessary additional computation.

## 16.5 Caching

Caching is valuable when a result is reused enough to justify its resource consumption.

It can be wasteful when:

- the result is used once,
- memory is constrained,
- recomputation is cheap.

## 16.6 Dynamic allocation

Dynamic resource allocation can reduce idle capacity, but scaling behavior and startup overhead must be benchmarked.

---

# 17. Dask Cost Optimization

Important cost dimensions include:

- worker count,
- worker memory,
- partition size,
- scheduler overhead,
- spilling,
- persistence,
- task graph size,
- unnecessary materialization,
- cluster idle time.

## Partition sizing

Very small partitions can create scheduling overhead.

Very large partitions can create:

- memory pressure,
- spilling,
- slow individual tasks.

The appropriate partition size depends on workload characteristics.

## Spilling

Spilling can prevent memory failure but may increase I/O and runtime.

Therefore:

```text
More memory
    ↓
Potentially less spill I/O
```

but:

```text
More memory
    ↓
Potentially higher infrastructure cost
```

Benchmark the trade-off.

## Persistence

Persist when reuse is high enough to justify the memory/resource cost.

Avoid persistence when:

- results are used once,
- memory is constrained,
- recomputation is inexpensive.

---

# 18. Ray Data Cost Optimization

Important dimensions include:

- CPU allocation,
- GPU allocation,
- actor count,
- actor-pool sizing,
- batch size,
- resource utilization,
- object-store memory,
- data locality,
- scaling.

## Actor count

Too few actors can under-utilize resources.

Too many can cause:

- scheduling overhead,
- contention,
- unnecessary resource reservation.

## Batch size

Batch size affects:

- throughput,
- memory,
- serialization,
- GPU utilization.

## GPU utilization

A GPU that spends much of its time waiting for CPU preprocessing can be extremely expensive.

The better optimization may be:

```text
Improve CPU preprocessing
        ↓
Improve batching
        ↓
Increase GPU utilization
        ↓
Increase useful records/GPU-second
```

---

# 19. GPU Cost Optimization

GPU economics should be measured in useful work per unit cost.

**Hypothetical example:**

```text
CPU:
1,000 records/sec

GPU:
10,000 records/sec
```

The GPU is 10× faster in this example.

But the correct comparison is not simply:

```text
CPU hourly price
vs
GPU hourly price
```

Instead evaluate:

```text
cost per million records
```

Important factors include:

- CPU vs GPU workload suitability,
- GPU utilization,
- GPU memory,
- batching,
- inference throughput,
- idle GPU time,
- CPU preprocessing,
- GPU starvation.

Moving a workload to GPUs does not automatically reduce cost.

Never invent actual cloud GPU prices.

---

# 20. Serverless vs Cluster Compute

Compare conceptually:

- serverless compute,
- fixed clusters,
- autoscaling clusters,
- containers,
- Kubernetes,
- managed Spark,
- warehouse compute.

| Factor | Serverless | Fixed/Managed Cluster |
|---|---|---|
| Idle capacity | Often lower | Can be significant |
| Startup latency | Can matter | Can be amortized |
| Operational burden | Usually lower | Often higher |
| Resource control | Service-dependent | Usually greater |
| Bursty workloads | Often attractive | Requires scaling |
| Long-running workloads | Depends on service | Often suitable |
| Predictability | Service-dependent | Often easier to control |

Choose based on:

- workload frequency,
- duration,
- startup latency,
- idle capacity,
- operational overhead,
- predictability,
- scaling requirements.

---

# 21. Spot / Preemptible Compute

Spot or preemptible resources can reduce compute cost while introducing interruption risk.

Important concepts:

- interruption,
- checkpointing,
- retryability,
- fault tolerance.

Good candidates include:

- batch transformations,
- backfills,
- recomputable workloads,
- large non-urgent processing.

Poor candidates may include workloads where interruption violates:

- SLA,
- correctness,
- recovery guarantees,
- operational requirements.

The real economic comparison should include expected interruption and retry behavior.

Do not fabricate provider-specific prices.

---

# 22. Scheduling for Cost

Scheduling can be a cost optimization strategy.

Compare conceptually:

```text
Every 5 minutes
vs
Every hour
vs
Event-driven
```

Possible strategies:

- avoid unnecessary frequency,
- event-driven execution,
- incremental processing,
- batching small workloads,
- off-peak execution where economically relevant,
- dependency-aware execution,
- avoiding duplicate runs.

But:

> **Cost optimization must not violate freshness SLAs.**

If a workload must refresh within ten minutes, moving it to hourly execution is not an optimization.

---

# 23. Retry and Failure Cost

Failures can multiply compute cost:

```text
Job
 ↓
Failure
 ↓
Retry
 ↓
Repeated compute
 ↓
Higher cost
```

Important failure modes:

- transient failures,
- bad data,
- OOM,
- shuffle failures,
- executor failures,
- retry storms.

Track:

```text
retry_count
+
failed_attempt_cost
+
successful_run_cost
=
actual workload economics
```

Reliability engineering is therefore part of cost optimization.

A system that is 10% cheaper per successful first attempt but fails frequently may be more expensive overall.

---

# 24. Idle Compute

Look for:

- idle clusters,
- idle executors,
- idle Kubernetes pods,
- development environments,
- abandoned clusters,
- forgotten notebooks,
- long-running services.

Useful controls include:

- automatic shutdown,
- TTL,
- autoscaling,
- scheduled shutdown,
- resource quotas,
- environment policies,
- monitoring.

Development environments can create significant waste because they are often created for experimentation and then forgotten.

---

# 25. Kubernetes Resource Economics

At a conceptual production level, understand:

- CPU requests,
- CPU limits,
- memory requests,
- memory limits,
- pod utilization,
- cluster utilization,
- bin packing,
- autoscaling,
- Cluster Autoscaler,
- Horizontal Pod Autoscaler,
- resource over-provisioning.

The economic chain is:

```text
Resource request
      ↓
Scheduler placement
      ↓
Cluster capacity
      ↓
Node utilization
      ↓
Infrastructure consumption
```

Incorrect resource requests can lead to inefficient placement and low cluster utilization.

This section is not a Kubernetes course. Its purpose is to understand how resource configuration affects compute economics.

---

# 26. Cloud Billing and Cost Allocation

A production platform should connect:

```text
Pipeline
   ↓
Infrastructure
   ↓
Resource
   ↓
Billing
```

Cost attribution can use:

- project/account,
- environment,
- team,
- workload,
- service,
- tags,
- labels,
- cost centers,
- chargeback,
- showback.

Poor tagging makes optimization difficult because the organization cannot reliably answer:

> “Which pipeline, workload, or team generated this spend?”

Engineering teams should be able to connect workload identity to infrastructure consumption.

---

# 27. Cost per Unit of Work

Unit economics should be first-class metrics.

Examples:

```text
$/GB
$/TB
$/million rows
$/successful pipeline run
$/feature generated
$/embedding generated
$/training dataset processed
```

For example:

```text
$10,000/month
```

is not enough.

Compare:

```text
System A:
$10,000 / 10 TB

System B:
$10,000 / 100 TB
```

System B has much better processing economics.

As workloads grow, cost/unit can expose efficiency degradation even when total cost remains within budget.

---

# 28. Performance-Cost Frontier

Think in terms of a:

> **Performance vs Cost frontier**

Example:

```text
Configuration A
cheap but slow

Configuration B
moderate cost / moderate speed

Configuration C
expensive but extremely fast
```

Evaluate:

- SLA,
- throughput,
- cost,
- reliability,
- business value.

The goal is the:

> **Best feasible point**

rather than automatically selecting the cheapest configuration.

---

# 29. Engine Selection for Cost

Engine choice is an economic decision.

| Workload | Candidate |
|---|---|
| SQL analytics | DuckDB / warehouse / Spark |
| Large distributed joins | Spark |
| Python parallel DataFrames | Dask |
| ML-heavy batch processing | Ray Data |
| Single-machine analytics | Polars / DuckDB |
| Numeric hot loop | NumPy / Numba |
| Small workload | Avoid distributed infrastructure |

The key principle is:

> **Do not use a distributed system when a single machine can solve the workload efficiently.**

Distributed infrastructure introduces:

- scheduling,
- networking,
- serialization,
- coordination,
- operational complexity.

For small workloads these costs can dominate the useful computation.

---

# 30. When Not to Optimize

Optimization has an engineering cost.

Optimization may be unnecessary when:

- the workload already meets the SLA,
- cost is negligible,
- optimization complexity exceeds expected savings,
- the workload runs rarely,
- engineering time costs more than compute savings,
- operational risk becomes unacceptable.

Use:

```text
Expected savings
vs
Engineering effort
vs
Operational risk
```

A technically possible optimization is not automatically a worthwhile optimization.

---

# 31. Optimization ROI

**Hypothetical example:**

```text
Current monthly compute cost = $20,000
Expected reduction = 20%
```

Then:

```text
Estimated monthly savings = $4,000
```

But also consider:

- annual savings,
- engineering effort,
- migration cost,
- maintenance cost,
- operational risk.

## Python calculator

```python
def optimization_roi(
    *,
    monthly_cost: float,
    expected_reduction: float,
    engineering_cost: float,
    months: int = 12,
) -> dict:
    monthly_savings = monthly_cost * expected_reduction
    total_savings = monthly_savings * months
    net_benefit = total_savings - engineering_cost

    return {
        "monthly_savings": monthly_savings,
        "total_savings": total_savings,
        "engineering_cost": engineering_cost,
        "net_benefit": net_benefit,
    }


result = optimization_roi(
    monthly_cost=20_000,
    expected_reduction=0.20,
    engineering_cost=10_000,
)

print(result)
```

The values above are hypothetical and must not be presented as actual cloud economics.

---

# 32. Complete Cost Optimization Experiment

The optimization workflow should be:

```text
1. Choose a representative workload.
2. Establish a baseline.
3. Measure runtime.
4. Measure resource utilization.
5. Estimate/record cost.
6. Identify the bottleneck.
7. Make one optimization.
8. Re-run the benchmark.
9. Verify correctness.
10. Measure cost again.
11. Compare runtime.
12. Compare resource usage.
13. Compare cost.
14. Compare cost/unit.
15. Validate SLA.
16. Document the result.
```

Required table:

| Configuration | Runtime | Resources | Cost | Cost/GB | SLA |
|---|---:|---:|---:|---:|---|
| Baseline | | | | | |
| Optimization 1 | | | | | |
| Optimization 2 | | | | | |

Do not fabricate values.

---

# 33. Cost Optimization Decision Tree

Use the workload constraint to choose the optimization.

```text
Is the workload processing unnecessary data?
        ↓
      YES
        ↓
Reduce data scanned
        ↓
Benchmark again

      NO
        ↓
Is the workload CPU-bound?
        ↓
      YES
        ↓
Optimize algorithm / vectorize / compile
        ↓
Benchmark again

      NO
        ↓
Is it memory-bound?
        ↓
      YES
        ↓
Reduce memory footprint / right-size
        ↓
Benchmark again

      NO
        ↓
Is it I/O-bound?
        ↓
      YES
        ↓
Optimize storage access / format / partitioning
```

Extend the diagnosis for:

- network-bound workloads,
- shuffle-bound workloads,
- scheduler-bound workloads,
- under-utilized clusters,
- excessive worker count,
- idle resources,
- inefficient engine selection.

Never optimize the wrong bottleneck.

---

# 34. Production Case Study

## Scenario

A production data platform processes large Parquet datasets every day using a distributed engine.

Initial symptoms:

- runtime is high,
- workers are frequently under-utilized,
- large amounts of data are scanned,
- shuffle volume is high,
- occasional retries occur,
- monthly compute cost is increasing.

The objective is:

> **Reduce workload cost while preserving correctness, reliability, and the required SLA.**

## Step 1 — Measure baseline

Capture:

```text
data size
runtime
workers
CPU
memory
bytes read
shuffle
retries
cost
SLA
```

## Step 2 — Estimate workload

Determine whether resource allocation is consistent with the workload.

## Step 3 — Inspect bytes read

Ask:

```text
How much data is scanned?
How much data is actually required?
```

## Step 4 — Apply predicate pushdown/projection pruning

Reduce unnecessary reads.

## Step 5 — Inspect partitioning

Look for:

- inefficient partitions,
- small files,
- poor pruning,
- skew.

## Step 6 — Analyze shuffle

Investigate joins and aggregations.

## Step 7 — Review parallelism

Check:

```text
workers
partitions
tasks
cores
```

## Step 8 — Right-size workers

Benchmark alternatives.

## Step 9 — Evaluate autoscaling

Determine whether elasticity reduces idle capacity without introducing excessive churn.

## Step 10 — Benchmark configurations

Measure:

```text
runtime
resource usage
cost
cost/TB
```

## Step 11 — Validate SLA and correctness

A cheaper configuration that violates the SLA is not acceptable.

## Step 12 — Document recommendation

Produce:

```text
Baseline
→ Bottleneck
→ Optimization
→ Measurement
→ Cost impact
→ Performance impact
→ SLA impact
→ Recommendation
```

---

# 35. Hands-on Project — Production Data Pipeline Compute Cost Optimization Review

Build a practical cost review.

## Part A — Baseline

Record:

- data size,
- runtime,
- workers,
- CPU,
- memory,
- bytes read,
- shuffle,
- retries,
- cost.

## Part B — Workload Reduction

Optimize:

- filtering,
- column selection,
- incremental processing,
- file scanning.

## Part C — Resource Optimization

Test:

- worker count,
- worker size,
- partition count,
- batch size.

## Part D — Engine Evaluation

Compare at least two suitable engines where practical.

Examples:

```text
Polars
vs
DuckDB
```

or:

```text
Spark
vs
Dask
```

Choose based on workload size and characteristics.

## Part E — Benchmark

Measure:

- runtime,
- throughput,
- peak memory,
- bytes read,
- cost,
- cost/unit.

## Part F — Final Recommendation

Produce:

```text
Baseline
→ Optimization
→ Measurement
→ Cost impact
→ Performance impact
→ SLA impact
→ Final recommendation
```

---

# 36. Failure Injection

## Failure 1 — Massive over-provisioning

```text
Symptoms
→ high resource allocation
→ low CPU utilization
→ high cost
```

Diagnose:

- actual workload demand,
- peak requirements,
- SLA requirements.

Corrective action:

- benchmark smaller configurations.

Verification:

- SLA,
- correctness,
- cost,
- failure behavior.

## Failure 2 — Low CPU utilization

Possible causes:

- I/O bottleneck,
- network bottleneck,
- scheduler overhead,
- excessive parallelism,
- skew.

Do not automatically reduce CPU resources without identifying the constraint.

## Failure 3 — Ten times more data scanned than necessary

Inspect:

- projections,
- predicates,
- partitions,
- file layout.

Measure bytes read before and after the change.

## Failure 4 — Autoscaling churn

Symptoms:

- frequent scale-up,
- frequent scale-down,
- little useful performance improvement.

Investigate:

- thresholds,
- startup latency,
- workload duration,
- scaling policy.

## Failure 5 — GPU allocated but mostly idle

Investigate:

- CPU preprocessing,
- batch size,
- serialization,
- data feeding.

## Failure 6 — Retry-driven cost growth

Inspect:

- failed attempts,
- retry count,
- failure cause.

Fix the reliability issue instead of treating repeated computation as normal.

## Failure 7 — Cheaper configuration violates SLA

The correct action is not simply to accept the cheaper configuration.

Re-evaluate:

```text
cost
+
runtime
+
reliability
+
SLA
```

Select the lowest-cost configuration that still satisfies the required service.

---

# 37. Production Checklist

## Before optimization

- [ ] Workload defined
- [ ] SLA defined
- [ ] Baseline captured
- [ ] Dataset representative
- [ ] Runtime measured
- [ ] Resource usage measured
- [ ] Cost measured/estimated
- [ ] Correctness verified

## During optimization

- [ ] Bottleneck identified
- [ ] One major variable changed at a time
- [ ] Correctness preserved
- [ ] Benchmark repeated
- [ ] Resource utilization checked
- [ ] Cost/unit calculated
- [ ] Failure behavior considered

## Before production

- [ ] SLA validated
- [ ] Failure behavior validated
- [ ] Autoscaling reviewed
- [ ] Idle resource controls configured
- [ ] Cost monitoring configured
- [ ] Alerts configured
- [ ] Ownership established
- [ ] Optimization documented
- [ ] Baseline retained

---

# 38. Common Cost Optimization Mistakes

| Mistake | Why it is wrong | Better approach |
|---|---|---|
| Optimize before measuring | No evidence of the actual problem | Establish a baseline |
| Focus only on hourly price | Runtime and resource consumption matter | Compare total cost/run |
| Ignore runtime | Cheap hourly resources may run much longer | Measure time and cost together |
| Ignore utilization | Allocated resources may sit idle | Compare allocation with actual use |
| Ignore data volume | Unnecessary scanning creates waste | Track bytes processed |
| Over-provision | Pays for unused capacity | Benchmark right-sizing |
| Under-provision | Can cause failures and SLA violations | Optimize within reliability constraints |
| Use too many workers | Coordination may dominate | Benchmark scaling |
| Use too few workers | Runtime may become unnecessarily long | Find useful parallelism |
| Use distributed infrastructure unnecessarily | Pays distributed overhead | Consider single-machine engines |
| Scan unnecessary data | Wastes I/O and compute | Push down filters/projections |
| Excessive shuffle | Increases network and disk work | Review joins and partitioning |
| Poor partitioning | Creates scheduling or memory overhead | Benchmark partition layout |
| Excessive retries | Repeats paid computation | Fix reliability issues |
| Idle clusters | Resources generate no useful work | Apply shutdown/TTL/autoscaling |
| Poor autoscaling | Causes churn or excess capacity | Tune using workload evidence |
| Poor GPU utilization | Expensive accelerators sit idle | Improve batching and feeding |
| Ignore engineering cost | Savings may not justify effort | Calculate ROI |
| Ignore reliability | Cheap failures can be expensive | Include successful-run economics |
| Ignore SLA | Lower cost can break the service | Treat SLA as a constraint |
| Optimize irrelevant workloads | Engineering time is wasted | Prioritize material cost drivers |
| Report only best-case results | Hides variation | Use repeated benchmarks |
| Track only total bill | Hides efficiency changes | Track cost/unit |
| Change without benchmarking | Cannot prove improvement | Measure before and after |
| Ignore correctness | Faster output may be wrong | Make correctness an acceptance gate |

---

# 39. Coding Requirements

Use practical Python examples for:

- compute cost calculation,
- cost per GB/TB,
- monthly cost projection,
- ROI calculation,
- baseline comparison,
- optimization comparison,
- simple benchmark-result analysis.

Relevant Data Engineering tools include:

- Polars,
- DuckDB,
- PyArrow,
- pandas,
- Dask,
- Ray,
- PySpark.

For every important optimization, answer:

```text
What changed?
Why should it help?
What metric should improve?
How do we verify it?
What could make it worse?
```

Example:

```text
What changed?
Reduced the columns read from Parquet.

Why should it help?
Less data must be loaded and processed.

Expected metrics:
bytes read ↓
memory ↓
runtime ↓
potential cost ↓

Verification:
run the same benchmark before and after.

What could make it worse?
If the workload already reads very little data,
the improvement may be negligible.
```

---

# 40. No Fabricated Performance or Cost Claims

Never write:

> “This optimization will reduce cost by 40%.”

unless that number comes from actual benchmark and cost measurements.

Prefer:

> “This may reduce cost because fewer bytes are processed; measure the before/after result.”

Use hypothetical numbers only when explicitly labeled:

> **Hypothetical example**

Never fabricate:

- cloud pricing,
- benchmark results,
- percentage improvements,
- throughput,
- memory savings,
- cost savings.

A defensible claim has:

```text
Expected mechanism
+
Measured evidence
=
Defensible claim
```

---

# 41. Interview Preparation

## Beginner

### What is compute cost?

The economic cost associated with the resources consumed to execute a workload.

### What is right-sizing?

Selecting resource capacity appropriate to workload requirements rather than systematically over- or under-provisioning.

### What is utilization?

The proportion of allocated resources that are actually used.

### Why is runtime alone insufficient?

Because cost depends on both execution time and the resources consumed during that time.

## Intermediate

### How would you reduce the cost of a Spark job?

Establish a baseline, identify the bottleneck, reduce unnecessary data processing, optimize joins/shuffles, review partitioning and caching, right-size resources, benchmark alternatives, and validate SLA and correctness.

### How does partitioning affect cost?

Poor partitioning can increase scanning, scheduling, shuffle, or memory overhead. Effective partitioning can reduce unnecessary work and improve resource utilization.

### How does autoscaling affect cost?

Autoscaling can reduce idle capacity for variable workloads, but excessive minimum capacity, scaling churn, startup latency, or slow scale-down can increase cost.

### How would you calculate cost per TB?

```text
cost per TB =
total workload cost / TB processed
```

## Advanced

### How would you optimize a CPU-bound distributed workload?

Measure CPU utilization, identify the hot path, reduce unnecessary work, improve algorithms or vectorization, consider compilation when justified, and benchmark resource configurations.

### How do you determine whether scaling out is economically justified?

Measure the marginal performance benefit against the marginal resource cost.

```text
additional cost
vs
additional useful throughput / SLA benefit
```

### How would you compare two cluster configurations?

Hold workload and correctness criteria constant, benchmark both, record runtime and resource usage, calculate cost and cost/unit, and evaluate SLA and reliability.

### How do retries affect cost?

Every retry can repeat some or all of the original computation, multiplying compute consumption.

## Senior / Production

### Design a cost optimization strategy for a large Data Platform.

Start with workload attribution and baselines. Prioritize material cost drivers. Reduce unnecessary processing, optimize execution plans, right-size resources, improve utilization, apply elasticity where appropriate, control idle resources, reduce retries, and establish continuous performance/cost monitoring.

### How would you build cost attribution by pipeline/team?

Connect:

```text
Pipeline
→ workload identity
→ infrastructure resource
→ billing record
→ team/cost center
```

Use consistent tags/labels and ownership metadata.

### How would you optimize a workload while maintaining an SLA?

Treat the SLA as a hard constraint and compare configurations on:

```text
cost
+
runtime
+
reliability
+
correctness
```

Select the lowest-cost configuration that satisfies the requirements.

### How would you identify hidden compute waste?

Look for:

- idle clusters,
- low utilization,
- excessive minimum capacity,
- retries,
- unnecessary scans,
- repeated computation,
- excessive parallelism,
- autoscaling churn,
- poor GPU utilization,
- unused development environments.

### How would you establish continuous performance/cost regression detection?

Combine:

```text
baseline
+
benchmark
+
resource metrics
+
cost/unit
+
historical tracking
+
tolerances
+
alerts
```

---

# 42. Final Checkpoint

The learner should be able to answer:

1. What actually causes compute cost?
2. How do you establish a cost baseline?
3. Why should you reduce work before adding infrastructure?
4. How does data volume affect compute?
5. How do CPU and memory utilization affect cost?
6. What is right-sizing?
7. How does autoscaling affect cost?
8. Why can more workers sometimes increase cost without proportional benefit?
9. How do retries increase cost?
10. How do you calculate cost per TB?
11. How do you compare two configurations economically?
12. When should you use a distributed engine?
13. When should you avoid distributed infrastructure?
14. How do GPU utilization and batching affect cost?
15. How do you balance cost against SLA?
16. How do you evaluate optimization ROI?
17. How do you prove that an optimization actually saved money?

Demonstrate the concepts with code and reasoning:

```text
Choose workload
    ↓
Measure baseline
    ↓
Identify bottleneck
    ↓
Change one thing
    ↓
Benchmark
    ↓
Measure resources
    ↓
Calculate cost
    ↓
Validate correctness
    ↓
Validate SLA
    ↓
Compare cost/unit
    ↓
Make recommendation
```

---

# 43. Roadmap Coverage Audit

The roadmap-required topic is **Compute Cost Optimization**. Supporting production knowledge is included where it directly enables the roadmap objective.

| Roadmap Concept | Covered? | Section |
|---|---|---|
| Workload estimation | Yes | 7, 8, 9 |
| Resource sizing | Yes | 11–13 |
| Performance measurement | Yes | 7, 32 |
| Benchmarking | Yes | 6, 32 |
| Engine selection | Yes | 29 |
| Scaling | Yes | 13 |
| Cost measurement | Yes | 5–7 |
| Cost/unit economics | Yes | 5, 27 |
| Production decision-making | Yes | 28, 30–32 |
| CPU cost | Yes | 2, 5, 11 |
| Memory cost | Yes | 2, 11 |
| Worker/node cost | Yes | 2, 13 |
| Execution-time cost | Yes | 2, 4 |
| Idle compute | Yes | 24 |
| Over-provisioning | Yes | 11, 40 |
| Under-provisioning | Yes | 11, 40 |
| Retry cost | Yes | 23, 40 |
| Data-movement cost | Yes | 9, 10, 15 |
| Unnecessary scans | Yes | 9, 10 |
| Poor partitioning | Yes | 10, 16, 17 |
| Bad parallelism | Yes | 14, 15 |
| Right-sizing | Yes | 11 |
| Utilization | Yes | 12 |
| Vertical scaling | Yes | 13 |
| Horizontal scaling | Yes | 13 |
| Elastic scaling | Yes | 13 |
| Batching | Yes | 14 |
| Spark cost optimization | Yes | 16 |
| Dask cost optimization | Yes | 17 |
| Ray Data cost optimization | Yes | 18 |
| GPU cost optimization | Yes | 19 |
| Serverless vs cluster | Yes | 20 |
| Spot/preemptible compute | Yes | 21 |
| Scheduling for cost | Yes | 22 |
| Kubernetes resource economics | Yes | 25 |
| Cloud cost allocation | Yes | 26 |
| Performance-cost frontier | Yes | 28 |
| Optimization ROI | Yes | 31 |
| Production case study | Yes | 34 |
| Hands-on project | Yes | 35 |
| Failure injection | Yes | 36 |
| Coding requirements | Yes | 39 |
| No fabricated cost/performance claims | Yes | 40 |
| Common mistakes | Yes | 40 |
| Production checklist | Yes | 37 |
| Interview preparation | Yes | 41 |
| Final checkpoint | Yes | 42 |

---

# 44. Final Production Mental Model

A senior Data Engineer should think about compute economics as an engineering loop:

```text
                 BUSINESS / SLA REQUIREMENT
                           ↓
                     DEFINE WORKLOAD
                           ↓
                    ESTIMATE THE WORK
                           ↓
                    MEASURE BASELINE
                           ↓
                    FIND THE BOTTLENECK
                           ↓
                     DO LESS WORK
                           ↓
                  CHOOSE BETTER ENGINE
                           ↓
                    RIGHT-SIZE RESOURCES
                           ↓
                    SCALE WHEN NEEDED
                           ↓
                     CONTROL IDLE TIME
                           ↓
                      BENCHMARK
                           ↓
                      MEASURE COST
                           ↓
                    COST PER UNIT
                           ↓
                     VALIDATE SLA
                           ↓
                   VALIDATE CORRECTNESS
                           ↓
                      CALCULATE ROI
                           ↓
                   PRODUCTION DECISION
```

The most important principles are:

> **Do less work before buying more compute.**

> **Measure performance before claiming an optimization.**

> **Measure cost per unit, not only the monthly bill.**

> **More resources do not automatically mean better economics.**

> **The cheapest configuration is not necessarily the best production configuration.**

> **A faster workload is valuable only when its additional resource cost is justified.**

> **A cheaper workload is not successful if it violates correctness, reliability, or SLA requirements.**

The goal is not simply to spend less.

The goal is to deliver the required business outcome with the **lowest justified total resource cost and acceptable operational risk**.

That is production-level compute cost optimization.
