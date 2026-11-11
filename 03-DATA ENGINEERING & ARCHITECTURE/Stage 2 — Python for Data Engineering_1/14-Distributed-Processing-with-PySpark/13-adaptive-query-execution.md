# Adaptive Query Execution in Apache Spark

> **Module:** `14-Distributed-Processing-with-PySpark/`  
> **Topic:** 13 — Adaptive Query Execution (AQE)  
> **Position:** After Topic 12 — Catalyst Optimizer and Explain Plans; before Topics 14–16.

## 1. Learning Objectives

By completing this chapter, you should be able to explain AQE from first principles and use it as a production performance-engineering tool. You will learn to:

- explain why a pre-execution plan can be suboptimal;
- distinguish Catalyst's pre-execution optimization from AQE's runtime adaptation;
- explain runtime statistics, stage boundaries, and adaptive re-planning;
- recognize `AdaptiveSparkPlan`, `isFinalPlan=false`, and `isFinalPlan=true` when exposed by the installed Spark version;
- explain post-shuffle partition coalescing and advisory partition size;
- explain runtime join-strategy switching, including sort-merge to broadcast conversion;
- explain AQE skew-join optimization and its thresholds/factors;
- explain dynamic partition pruning in star-schema workloads;
- inspect and tune AQE configuration without cargo-cult changes;
- understand the continuing role of `repartition()`, `coalesce()`, and join hints;
- identify problems AQE cannot solve;
- compare AQE ON/OFF with controlled experiments;
- correlate code → plan → stage → task → metrics → AQE decision;
- diagnose production performance issues and communicate architecture trade-offs.

## 2. Prerequisites and Mental Model

This chapter assumes the learner has completed the preceding topics on joins/shuffle, partitioning, skew, caching, UDFs, and Catalyst/explain plans. The central progression is:

```text
Catalyst planning
      ↓
Initial physical plan
      ↓
Spark executes a stage
      ↓
Actual runtime statistics become available
      ↓
AQE evaluates the remaining execution
      ↓
Plan can be adapted where supported
      ↓
Remaining stages execute
```

The key sentence to remember is:

> **Catalyst makes decisions before execution using estimates and known information; AQE can make better decisions during execution because Spark now has actual runtime statistics.**

AQE is not an isolated feature and does not replace Catalyst. It is the runtime adaptation layer built on Spark's execution/planning machinery.

## 3. Why Adaptive Query Execution Exists

A query planner must make decisions before it can observe every intermediate result. It can use schema, query structure, catalog information, statistics, and configuration, but estimates can differ from reality.

Imagine a filtered dimension relation:

```text
Before execution:
  estimated size = large
  ↓
  initial join = SortMergeJoin

During execution:
  filter actually leaves a very small relation
  ↓
  AQE sees runtime size
  ↓
  BroadcastHashJoin may now be viable
```

The important distinction is timing:

```text
Static:
Estimate → Plan → Execute

Adaptive:
Estimate → Initial Plan → Execute Stage → Observe → Re-optimize → Continue
```

AQE exists because runtime information can be materially better than a pre-execution estimate for some decisions.

## 4. The Problem with Static Query Planning

Static planning is necessary; it is not inherently wrong. Its limitation is incomplete information.

Common causes of estimation error include:

- missing or stale statistics;
- unknown filter selectivity;
- changing data distributions;
- intermediate results much larger or smaller than expected;
- skewed partitions;
- workload variability.

A senior engineer does not ask whether the planner was "wrong" in isolation. The useful question is: **what information was available when the decision was made, and what additional information became available later?**

## 5. Catalyst vs Adaptive Query Execution

| Dimension | Catalyst | AQE |
|---|---|---|
| Main timing | Primarily before execution | During execution |
| Information | Query structure, metadata, available statistics/estimates | Runtime statistics plus the existing plan |
| Main purpose | Analyze, optimize, and select execution strategies | Adapt remaining execution using observed runtime behavior |
| Examples | Predicate pushdown, projection pruning, join planning | Post-shuffle coalescing, runtime join adaptation, skew-join handling |
| Relationship | Planning foundation | Runtime adaptation layer |

A useful analogy is route planning: Catalyst selects a route before departure using known information; AQE is like changing the remaining route after observing actual traffic. The analogy is only conceptual—the technical implementation remains part of Spark's adaptive execution framework.

## 6. What AQE Actually Does

AQE can execute part of a physical plan, collect runtime information, and use it to adapt supported portions of the remaining plan. Important capabilities include:

1. post-shuffle partition coalescing;
2. runtime join-strategy adaptation;
3. skew-join optimization;
4. runtime-aware partition pruning behavior in supported query shapes.

AQE does **not** mean Spark can change anything at any time. Completed work remains completed, and adaptation is constrained by execution boundaries and supported physical operators.

## 7. AQE Execution Lifecycle

A simplified lifecycle is:

```text
1. Query submitted
2. Catalyst analyzes query
3. Optimized logical plan produced
4. Initial physical plan produced
5. Adaptive execution starts
6. Initial stage executes
7. Shuffle/stage runtime statistics become available
8. AQE evaluates the remaining plan
9. Supported decisions are re-optimized
10. Remaining stages execute
11. More runtime information can become available
12. Further adaptation may occur
13. Final execution completes
```

### Why stage boundaries matter

AQE needs actual information. A completed stage can expose facts about the data it produced. That information is useful when there is still downstream work whose strategy can change.

```text
Stage A
  ↓
Materialized output + runtime statistics
  ↓
AQE decision point
  ↓
Adapted remaining plan
  ↓
Stage B
```

AQE therefore operates with Spark's stage-oriented execution model; it is not a mechanism for retroactively changing arbitrary completed computation.

## 8. Runtime Statistics

Runtime statistics are observations produced by execution. Depending on the operator and Spark version, useful information can include:

- rows produced;
- actual intermediate relation size;
- shuffle data size;
- shuffle partition sizes;
- partition-size distribution;
- skew characteristics.

### Estimated versus actual

| | Estimated | Actual |
|---|---|---|
| Timing | Before execution | After relevant execution has occurred |
| Source | Statistics, metadata, planner estimates | Runtime execution |
| Use | Initial plan | Adaptive decisions |
| Reliability | Depends on statistic quality | Observed for completed work |

Example:

```text
Estimated filtered relation: large
Actual filtered relation:    small
```

The actual result can create an opportunity for a different downstream strategy. It does not guarantee that Spark will choose that strategy.

## 9. Stage Boundaries and Re-optimization

AQE is useful at points where runtime information has become available and there is still work remaining.

A practical reasoning sequence is:

1. What stage has completed?
2. What statistics did it expose?
3. Which downstream operators depend on that result?
4. Which of those operators can still be adapted?
5. What configuration, hints, and resource constraints apply?

This is more useful than memorizing AQE configuration names.

## 10. Recognizing AQE in Plans

Start every experiment by recording the runtime version:

```python
print("Spark version:", spark.version)
```

Inspect a DataFrame:

```python
df.explain("formatted")
```

After execution, inspect again where the environment exposes adaptive state:

```python
df.count()
df.explain("formatted")
```

An adaptive plan can expose `AdaptiveSparkPlan`. Some plan representations also expose `isFinalPlan=false` before completion and `isFinalPlan=true` after the adaptive execution reaches its final state.

**Do not treat one printed plan as universal.** Plan formatting and visible operators vary by Spark version, query, and execution context. Use the installed runtime as the authority.

## 11. AdaptiveSparkPlan

`AdaptiveSparkPlan` is a plan representation associated with adaptive execution. Conceptually it says that Spark is managing the query through a framework that can observe runtime information and adapt supported remaining execution.

When you see it, ask:

- Is AQE enabled?
- Where are the exchanges/stage boundaries?
- Which intermediate result can provide runtime information?
- Did the final plan differ?
- Were partitions coalesced?
- Did a join strategy change?
- Was skew handled?

`AdaptiveSparkPlan` by itself is not proof of a performance improvement.

## 12. Initial Plan vs Final Plan

The initial plan is the strategy Spark starts with. The final adaptive plan is the state reached after relevant runtime decisions.

Conceptually:

```text
Initial:
AdaptiveSparkPlan
    SortMergeJoin

Final:
AdaptiveSparkPlan
    BroadcastHashJoin
```

That is only a representative structure. Another query may retain `SortMergeJoin`, or change partitioning without changing the join.

Therefore:

> AQE enabled + unchanged final plan is not automatically a failure.

The correct investigation compares runtime evidence with the decisions that were available.

## 13. Post-Shuffle Partition Coalescing

A shuffle may create many partitions. If the actual workload is small, many partitions can be tiny.

For example:

```text
10,000 shuffle partitions
        ↓
Most contain very little data
        ↓
10,000 downstream tasks
```

Potential costs include:

- scheduler overhead;
- task startup overhead;
- inefficient executor utilization;
- excessive tiny-task execution.

AQE can coalesce compatible post-shuffle partitions so downstream work uses fewer, larger partitions.

```text
Before:
P1 P2 P3 P4 P5 P6 P7 P8

After:
P1+P2+P3 | P4+P5 | P6+P7+P8
```

This is different from application-level `coalesce()`: AQE uses runtime shuffle information to make an adaptive downstream decision.

### Trade-off

Too-small partitions increase overhead. Too-large partitions can reduce parallelism, increase memory pressure, and create long-tail tasks. AQE attempts to find a practical balance using runtime information.

## 14. Advisory Partition Size

The key configuration concept is:

```text
spark.sql.adaptive.advisoryPartitionSizeInBytes
```

It is an advisory target used by adaptive partition-sizing decisions. It does not guarantee that every partition will have exactly that size.

Conceptually:

```text
small advisory target
→ more/finer downstream partitions may remain

large advisory target
→ fewer/larger downstream partitions may be produced
```

If too small, tiny-task overhead may remain. If too large, tasks can become unnecessarily large or reduce useful parallelism.

There is no universally correct value because row width, compression, operator cost, cluster resources, and data distribution differ.

### Experiment

```python
spark.conf.set(
    "spark.sql.adaptive.advisoryPartitionSizeInBytes",
    str(64 * 1024 * 1024),
)
```

The value above is an **experiment setting**, not a universal recommendation. Measure task count, task sizes, stage duration, spill, shuffle metrics, and long-tail behavior.

## 15. Runtime Join Strategy Switching

A join strategy that looks appropriate before execution may become less appropriate after a relation is filtered.

```text
Initial estimate
    ↓
SortMergeJoin
    ↓
Filter stage executes
    ↓
Actual relation is small
    ↓
AQE evaluates remaining join
    ↓
BroadcastHashJoin may become viable
```

The word **may** matters. Runtime switching depends on actual statistics, thresholds, join type, hints, resources, and Spark version.

## 16. Sort-Merge Join to Broadcast Join

A sort-merge join is useful for large equi-joins where broadcasting is not safely attractive. It can require shuffle and sorting.

A broadcast hash join can avoid a large shuffle of the broadcast side when one side is safely small.

Example:

```python
from pyspark.sql import functions as F

fact = (
    spark.range(0, 5_000_000)
    .withColumn("customer_id", (F.col("id") % 500_000).cast("long"))
)

dim = (
    spark.range(0, 500_000)
    .withColumnRenamed("id", "customer_id")
    .withColumn(
        "status",
        F.when((F.col("customer_id") % 100) == 0, "ACTIVE")
         .otherwise("INACTIVE")
    )
)

filtered_dim = dim.filter(F.col("status") == "ACTIVE")
joined = fact.join(filtered_dim, "customer_id", "inner")

joined.explain("formatted")
joined.count()
joined.explain("formatted")
```

Inspect the actual initial/final plan, broadcast exchange, join operator, shuffle metrics, and task distribution. Do not claim a particular output is guaranteed across Spark versions.

### Trade-offs

**Broadcast:** potentially less shuffle, but requires executor memory and is unsafe if the relation is unexpectedly large.

**Sort-merge:** handles large relations well, but can require shuffle and sorting.

AQE does not mean "always choose broadcast."

## 17. AQE and Broadcast Thresholds

A relevant configuration is:

```text
spark.sql.autoBroadcastJoinThreshold
```

Inspect the effective value rather than assuming a universal default:

```python
print(spark.version)
print(spark.conf.get("spark.sql.autoBroadcastJoinThreshold"))
```

Static planning can use known/estimated size information. Adaptive execution can use actual runtime size where the supported AQE decision applies.

Increasing the threshold expands the set of relations that may be considered for broadcast. That can increase executor memory pressure. Measure before and after; do not increase it merely because a join is slow.

## 18. Skew Join Optimization

Topic 09 established the mechanics of skew and salting. Here the focus is how AQE reacts to skewed **join partitions**.

A simplified distribution:

```text
Partition 1: 10 MB
Partition 2: 12 MB
Partition 3: 11 MB
Partition 4: 900 MB  ← skew
```

One long task can delay the stage after most peer tasks finish.

For supported skewed joins, AQE can conceptually:

1. identify unusually large shuffle partitions;
2. split skewed partitions into smaller pieces;
3. replicate the corresponding partition from the other side where required;
4. run smaller pieces in parallel;
5. combine results correctly.

## 19. Skew Thresholds and Factors

Important configuration concepts include:

```text
spark.sql.adaptive.skewJoin.enabled
spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes
spark.sql.adaptive.skewJoin.skewedPartitionFactor
```

Verify names and semantics against the installed Spark version.

| Setting | Concept | Too aggressive | Too conservative | Validation |
|---|---|---|---|---|
| `...skewJoin.enabled` | Enables supported adaptive skew-join handling | Extra adaptive work | Skew opportunity missed | Compare task distribution |
| `...ThresholdInBytes` | Absolute size criterion | More candidates | Large skew may qualify less often | Inspect partition sizes |
| `...Factor` | Relative size criterion | More candidates | Some relative outliers missed | Compare distribution |

Do not memorize magic values. Tune only after inspecting partition distributions and measuring the result.

## 20. AQE and Data Skew

AQE can help with skewed join partitions, but it does not automatically solve:

- skewed aggregations;
- skewed windows;
- hot business keys;
- poor key design;
- huge data explosions;
- bad storage layout;
- poor modeling.

Manual options can include:

- salting;
- pre-aggregation;
- selective broadcast;
- improved partitioning;
- data-model changes.

The diagnostic distinction is important:

```text
Skewed join partition → AQE skew handling may help
Skewed GROUP BY       → redesign/pre-aggregation/salting may be required
```

## 21. Dynamic Partition Pruning

Partition pruning avoids reading storage partitions that cannot contribute to a result.

Static example:

```sql
WHERE sale_date = '2026-01-03'
```

If the table is partitioned by `sale_date`, Spark can identify the relevant partition before reading data.

Dynamic partition pruning (DPP) derives pruning information from another relation in the query, commonly a filtered dimension in a star-schema query.

```text
dim_customer
     ↓ filter
allowed customer information
     ↓
     JOIN
     ↓
fact_sales partitioned storage
     ↓
prune irrelevant partitions when applicable
```

DPP is a distinct Spark SQL optimization. Do not equate DPP with AQE. They can complement one another in runtime-aware workloads.

Effectiveness depends on partition layout, query shape, filter selectivity, data-source support, statistics, and Spark version.

## 22. Dynamic Partition Pruning with Star Schemas

Consider:

```text
fact_sales(customer_id, sale_date, amount)
dim_customer(customer_id, segment)
```

A query might be:

```python
filtered_customers = dim_customer.filter(
    F.col("segment") == "enterprise"
)

result = (
    fact_sales
    .join(filtered_customers, "customer_id", "inner")
    .groupBy("sale_date")
    .agg(F.sum("amount").alias("revenue"))
)
```

The relevant engineering questions are:

- Is the fact table partitioned by a useful column?
- Can the filtered dimension provide useful pruning information?
- Is the filter selective enough to matter?
- Does the plan expose partition-filter evidence?
- Does the data source support the required behavior?

Inspect rather than assume.

## 23. Dynamic Partition Pruning PySpark Lab

Create a small star-schema workload:

```python
from pyspark.sql import functions as F

fact_sales = (
    spark.range(0, 2_000_000)
    .withColumn("customer_id", (F.col("id") % 50_000).cast("long"))
    .withColumn(
        "sale_date",
        F.date_add(F.lit("2026-01-01"), (F.col("id") % 30).cast("int"))
    )
    .withColumn("amount", (F.col("id") % 1000).cast("double"))
    .select("customer_id", "sale_date", "amount")
)

dim_customer = (
    spark.range(0, 50_000)
    .withColumnRenamed("id", "customer_id")
    .withColumn(
        "segment",
        F.when((F.col("customer_id") % 100) == 0, "enterprise")
         .otherwise("consumer")
    )
)

fact_path = "/tmp/aqe_fact_sales"
(
    fact_sales.write
    .mode("overwrite")
    .partitionBy("sale_date")
    .parquet(fact_path)
)

fact = spark.read.parquet(fact_path)
enterprise = dim_customer.filter(F.col("segment") == "enterprise")

query = fact.join(enterprise, "customer_id", "inner")
query.explain("formatted")
query.count()
```

Inspect scan nodes, partition filters, exchanges, adaptive state, and runtime behavior. Then create a comparison query that cannot use the same pruning opportunity and explain the difference.

## 24. AQE Configuration

Start with:

```python
print("Spark version:", spark.version)
```

Then inspect relevant configuration defensively:

```python
keys = [
    "spark.sql.adaptive.enabled",
    "spark.sql.adaptive.coalescePartitions.enabled",
    "spark.sql.adaptive.advisoryPartitionSizeInBytes",
    "spark.sql.adaptive.localShuffleReader.enabled",
    "spark.sql.adaptive.skewJoin.enabled",
    "spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes",
    "spark.sql.adaptive.skewJoin.skewedPartitionFactor",
    "spark.sql.autoBroadcastJoinThreshold",
    "spark.sql.optimizer.dynamicPartitionPruning.enabled",
]

for key in keys:
    try:
        print(key, "=", spark.conf.get(key))
    except Exception as exc:
        print(key, "= unavailable:", type(exc).__name__)
```

AQE can be enabled/disabled for a controlled experiment:

```python
spark.conf.set("spark.sql.adaptive.enabled", "true")
# or
spark.conf.set("spark.sql.adaptive.enabled", "false")
```

Configuration behavior is version-sensitive. Inspect the effective runtime value instead of copying defaults from an old tutorial.

## 25. Important AQE Configuration Parameters

| Configuration | Conceptual role | Change only when | Main risk |
|---|---|---|---|
| `spark.sql.adaptive.enabled` | Enables adaptive execution | Testing/production policy requires it | Losing adaptive behavior |
| `spark.sql.adaptive.coalescePartitions.enabled` | Adaptive post-shuffle coalescing | Tiny downstream partitions are evidenced | Over-large tasks in an unsuitable workload |
| `spark.sql.adaptive.advisoryPartitionSizeInBytes` | Advisory target for adaptive partition sizing | Task-size distribution suggests a mismatch | Too-small/too-large tasks |
| `spark.sql.adaptive.localShuffleReader.enabled` | Adaptive local shuffle reading where applicable | Plan/UI evidence supports it | Version/workload-specific behavior |
| `spark.sql.adaptive.skewJoin.enabled` | Supported skew-join adaptation | Join skew is evidenced | Extra work/complexity |
| `spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes` | Absolute skew criterion | Partition distribution supports a change | Missed or over-detected skew |
| `spark.sql.adaptive.skewJoin.skewedPartitionFactor` | Relative skew criterion | Distribution supports a change | Misclassification |
| `spark.sql.autoBroadcastJoinThreshold` | Broadcast eligibility criterion | Join evidence supports testing it | Executor memory pressure |
| DPP configuration | Dynamic partition-pruning behavior | Partitioned star-schema workload supports it | Overhead/no benefit |

Defaults are intentionally not stated as universal. Verify the installed Spark release.

## 26. AQE Configuration Tuning Strategy

Use this workflow:

```text
Baseline
  ↓
Inspect plan
  ↓
Inspect Spark UI
  ↓
Identify bottleneck
  ↓
Form hypothesis
  ↓
Change one setting
  ↓
Run same workload
  ↓
Measure
  ↓
Compare
  ↓
Keep or revert
```

Do not tune because a setting exists. "More tuning" is not synonymous with better performance.

## 27. AQE and Manual Partition Tuning

AQE can reduce the need for rigid `spark.sql.shuffle.partitions` tuning, but it does not make manual partitioning obsolete.

Manual partitioning still matters for:

- input/output layout;
- storage partitioning;
- known downstream requirements;
- locality;
- file layout;
- stable business partitioning;
- application-specific join preparation.

`repartition()` is an application transformation. AQE post-shuffle coalescing is runtime adaptation. They operate at different layers.

## 28. AQE and Join Hints

Broadcast hints can be expressed in PySpark:

```python
joined = fact.join(
    F.broadcast(dim),
    on="customer_id",
    how="inner",
)
```

Or SQL:

```sql
SELECT /*+ BROADCAST(dim) */ ...
FROM fact
JOIN dim ON fact.customer_id = dim.customer_id
```

A hint is not a magic performance button. A hard-coded hint can constrain strategy choices and can become unsafe as data changes.

Do not claim AQE always overrides hints. Hint semantics and interactions are version-sensitive; verify the installed Spark version and inspect the actual plan.

## 29. What AQE Cannot Fix

AQE is not a universal optimizer for all system problems. It cannot automatically repair:

1. skewed aggregations;
2. skewed windows;
3. bad file layouts;
4. excessive small files;
5. poor data modeling;
6. bad partitioning strategy;
7. expensive Python UDFs;
8. inefficient Python code;
9. unnecessary scans;
10. excessive columns;
11. poor schema design;
12. huge join explosions;
13. Cartesian products;
14. incorrect join conditions;
15. excessive network traffic caused by application design;
16. external-system bottlenecks;
17. slow object storage;
18. JDBC bottlenecks;
19. driver-side bottlenecks;
20. bad application architecture.

The correct response is to fix the underlying bottleneck rather than trying another AQE setting.

## 30. AQE Limitations and Trade-offs

AQE requires runtime information and therefore has decision overhead. Some information becomes available only after work has already happened. Some completed work cannot be changed. Not every workload contains enough uncertainty for AQE to materially help.

Data layout, application architecture, resource sizing, statistics, and query design remain important.

The two questions that should guide investigation are:

> **What information does Spark have at this point?**

> **What decision can still be changed?**

## 31. AQE ON vs AQE OFF Experiments

Run the same workload with AQE disabled and enabled.

```python
import time
from pyspark.sql import functions as F

def run_case(spark, enabled):
    spark.conf.set("spark.sql.adaptive.enabled", str(enabled).lower())

    df = (
        spark.range(0, 2_000_000)
        .withColumn("key", F.col("id") % 100_000)
    )
    result = df.groupBy("key").count()
    result.explain("formatted")

    start = time.perf_counter()
    result.count()
    return time.perf_counter() - start

print("AQE OFF:", run_case(spark, False))
print("AQE ON :", run_case(spark, True))
```

Measure:

- runtime;
- task count;
- stage duration;
- shuffle read/write;
- partition count;
- task-duration distribution;
- join strategy where relevant;
- initial/final plan;
- resource behavior.

Do not fabricate results. Hardware, storage, JVM, Python, Spark version, cluster resources, and data distribution all affect outcomes.

## 32. Required Experiment Matrix

Use this table and fill it from actual experiments:

| Workload | AQE | Data characteristics | Initial plan | Final plan | Join strategy | Partitions | Tasks | Shuffle read | Shuffle write | Runtime | Bottleneck | Interpretation |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---|---|
| Many small shuffle partitions | OFF | | | | N/A | | | | | | | |
| Many small shuffle partitions | ON | | | | N/A | | | | | | | |
| Small-after-filter join | OFF | | | | | | | | | | | |
| Small-after-filter join | ON | | | | | | | | | | | |
| Skewed join | OFF | | | | | | | | | | | |
| Skewed join | ON | | | | | | | | | | | |

The table is intentionally measurement-driven rather than filled with invented benchmark numbers.

## 33. Tune Advisory Partition Size Experiment

Change only:

```python
spark.sql.adaptive.advisoryPartitionSizeInBytes
```

For each setting record:

- resulting partition count;
- task count;
- task-size distribution;
- runtime;
- shuffle behavior;
- spill;
- long-tail behavior;
- executor memory behavior.

Do not optimize only for wall-clock time. A configuration that appears faster in one run can increase memory pressure or reduce stability.

## 34. Dynamic Partition Pruning Experiment

Perform these steps:

1. Build a partitioned fact table.
2. Build a dimension table.
3. Filter the dimension.
4. Join it to the fact.
5. Inspect the plan.
6. Inspect partition-filter behavior.
7. Run the query.
8. Compare with a query where pruning cannot meaningfully occur.
9. Explain the difference.

Connect the result to data modeling, star schemas, partitioning, predicate pushdown, Catalyst, AQE, and Spark SQL.

## 35. Manual-Tuning-Removal Experiment

1. Capture an existing manually tuned baseline.
2. Enable AQE.
3. Identify one hard-coded assumption that may no longer be necessary.
4. Remove only that assumption.
5. Run the same workload.
6. Compare runtime and resource metrics.
7. Validate correctness.
8. Keep or revert based on evidence.

The principle is:

> **Reduce unnecessary hard-coded assumptions when the engine can make a better decision using actual data.**

## 36. Spark UI and AQE

Depending on Spark version/deployment, inspect the SQL/query-execution view for:

- adaptive execution evidence;
- initial/final plan information where exposed;
- stages;
- tasks;
- shuffle read/write;
- task-duration distribution;
- skew;
- join strategy.

UI details are version-sensitive. Verify the actual installed environment.

Correlate:

```text
Code
 ↓
Plan
 ↓
Stage
 ↓
Task
 ↓
Metrics
 ↓
AQE decision
```

## 37. Production Troubleshooting Workflow

Problem: **"Spark join is slow."**

Do not immediately increase partitions.

Use:

1. reproduce if possible;
2. capture plan;
3. identify join strategy;
4. inspect exchanges;
5. inspect partition sizes;
6. inspect skew;
7. check AQE state;
8. compare initial/final plans;
9. inspect task-duration distribution;
10. check broadcast behavior;
11. check shuffle volume;
12. check input/storage characteristics;
13. form a hypothesis;
14. change one thing;
15. measure;
16. validate correctness;
17. document the result.

### Scenario: AQE-enabled job still slow

Possible causes include scan cost, storage, UDFs, join explosion, unsupported skew, JDBC, or driver bottlenecks. AQE may simply not be the dominant lever.

### Scenario: Broadcast does not occur

Check actual relation size, threshold, join type, hints, statistics, final plan, and memory/resource conditions.

### Scenario: One task is much slower

Inspect partition-size distribution, skew, spills, storage, and operator cost before changing partition counts.

# 38. Hands-On Labs

## Lab 1 — Identify AQE

Print Spark version, inspect AQE configuration, explain a query, execute it, and inspect the adaptive plan state.

## Lab 2 — AQE ON/OFF

Run the same query under both settings. Record plans, tasks, shuffle metrics, and runtime.

## Lab 3 — Many Tiny Shuffle Partitions

Create a small dataset with a deliberately high shuffle partition count. Compare with AQE coalescing.

## Lab 4 — Advisory Partition Size

Test several experimental advisory sizes. Record partition counts, task sizes, stage duration, spill, and long-tail behavior.

## Lab 5 — Runtime Join Switching

Create a dimension that becomes small after filtering. Inspect initial/final plan and join strategy.

## Lab 6 — Broadcast Safety

Test a higher broadcast threshold carefully. Observe memory/resource consequences rather than optimizing for the join alone.

## Lab 7 — Skewed Join

Create a hot key and compare task distribution with AQE skew handling enabled/disabled.

## Lab 8 — Skew Threshold Experiment

Change one skew-related setting at a time and measure partition/task distribution.

## Lab 9 — Dynamic Partition Pruning

Build a partitioned fact and filtered dimension. Inspect scan and partition-filter evidence.

## Lab 10 — Manual Tuning Removal

Remove one potentially obsolete hard-coded partition setting and validate the result.

## Lab 11 — AQE and Join Hints

Compare no hint versus broadcast hint under AQE and inspect actual final behavior.

## Lab 12 — Plan-Driven Debugging

Take a slow query and document plan, exchanges, join strategy, skew, partition distribution, and AQE state before changing anything.

## Lab 13 — Repeated Performance Trials

Run the same workload repeatedly and analyze variability before drawing conclusions.

## Lab 14 — DPP Comparison

Compare a query with a useful partition-pruning opportunity against one without it.

## Lab 15 — End-to-End AQE Investigation

Follow the full loop: read → predict → code → explain → run → AQE ON/OFF → UI → change one variable → measure → explain → document → present.

# 39. Debugging Exercises

## Exercise 1 — AQE disabled accidentally

**Scenario / symptom:** The query is expected to adapt but the effective setting is false.

**Learner task:** Determine whether AQE is the actual bottleneck or merely part of the execution context.

**Investigation steps:**
1. Record `spark.version` and relevant effective configuration.
2. Capture the initial/final plan where available.
3. Inspect stages, tasks, shuffle, partition-size distribution, and long-tail behavior.
4. Form one hypothesis before changing anything.
5. Change one variable and rerun the same workload.

**Expected reasoning / corrective approach:** Verify Spark version and effective configuration, capture the plan, then run a controlled ON/OFF comparison.

**Production rule:** Do not accept a configuration change until the evidence explains the observed symptom and correctness has been revalidated.

## Exercise 2 — Too many tiny shuffle partitions

**Scenario / symptom:** Thousands of very short downstream tasks appear.

**Learner task:** Determine whether AQE is the actual bottleneck or merely part of the execution context.

**Investigation steps:**
1. Record `spark.version` and relevant effective configuration.
2. Capture the initial/final plan where available.
3. Inspect stages, tasks, shuffle, partition-size distribution, and long-tail behavior.
4. Form one hypothesis before changing anything.
5. Change one variable and rerun the same workload.

**Expected reasoning / corrective approach:** Inspect shuffle volume, partition sizes, task count, and adaptive coalescing before changing the global partition count.

**Production rule:** Do not accept a configuration change until the evidence explains the observed symptom and correctness has been revalidated.

## Exercise 3 — Coalescing not behaving as expected

**Scenario / symptom:** Task count remains higher than expected.

**Learner task:** Determine whether AQE is the actual bottleneck or merely part of the execution context.

**Investigation steps:**
1. Record `spark.version` and relevant effective configuration.
2. Capture the initial/final plan where available.
3. Inspect stages, tasks, shuffle, partition-size distribution, and long-tail behavior.
4. Form one hypothesis before changing anything.
5. Change one variable and rerun the same workload.

**Expected reasoning / corrective approach:** Check effective AQE settings, actual shuffle partition sizes, stage boundaries, query shape, and Spark version.

**Production rule:** Do not accept a configuration change until the evidence explains the observed symptom and correctness has been revalidated.

## Exercise 4 — Broadcast not occurring

**Scenario / symptom:** An engineer believes the filtered side is small, but the plan is non-broadcast.

**Learner task:** Determine whether AQE is the actual bottleneck or merely part of the execution context.

**Investigation steps:**
1. Record `spark.version` and relevant effective configuration.
2. Capture the initial/final plan where available.
3. Inspect stages, tasks, shuffle, partition-size distribution, and long-tail behavior.
4. Form one hypothesis before changing anything.
5. Change one variable and rerun the same workload.

**Expected reasoning / corrective approach:** Inspect actual size, threshold, join type, hints, statistics, and final plan instead of assuming size from row count.

**Production rule:** Do not accept a configuration change until the evidence explains the observed symptom and correctness has been revalidated.

## Exercise 5 — Broadcast memory pressure

**Scenario / symptom:** Executors experience memory pressure after a broadcast strategy appears.

**Learner task:** Determine whether AQE is the actual bottleneck or merely part of the execution context.

**Investigation steps:**
1. Record `spark.version` and relevant effective configuration.
2. Capture the initial/final plan where available.
3. Inspect stages, tasks, shuffle, partition-size distribution, and long-tail behavior.
4. Form one hypothesis before changing anything.
5. Change one variable and rerun the same workload.

**Expected reasoning / corrective approach:** Inspect broadcast size, executor metrics, final plan, threshold, and hints; test a safer non-broadcast strategy.

**Production rule:** Do not accept a configuration change until the evidence explains the observed symptom and correctness has been revalidated.

## Exercise 6 — Skewed join remains slow

**Scenario / symptom:** One or a few tasks remain long-tail outliers.

**Learner task:** Determine whether AQE is the actual bottleneck or merely part of the execution context.

**Investigation steps:**
1. Record `spark.version` and relevant effective configuration.
2. Capture the initial/final plan where available.
3. Inspect stages, tasks, shuffle, partition-size distribution, and long-tail behavior.
4. Form one hypothesis before changing anything.
5. Change one variable and rerun the same workload.

**Expected reasoning / corrective approach:** Inspect partition sizes and skew settings and determine whether the skew is in a supported join pattern.

**Production rule:** Do not accept a configuration change until the evidence explains the observed symptom and correctness has been revalidated.

## Exercise 7 — Aggregation skew

**Scenario / symptom:** One grouping key dominates execution.

**Learner task:** Determine whether AQE is the actual bottleneck or merely part of the execution context.

**Investigation steps:**
1. Record `spark.version` and relevant effective configuration.
2. Capture the initial/final plan where available.
3. Inspect stages, tasks, shuffle, partition-size distribution, and long-tail behavior.
4. Form one hypothesis before changing anything.
5. Change one variable and rerun the same workload.

**Expected reasoning / corrective approach:** Explain why skew-join optimization does not directly solve aggregation skew; consider pre-aggregation, salting, or key redesign.

**Production rule:** Do not accept a configuration change until the evidence explains the observed symptom and correctness has been revalidated.

## Exercise 8 — Dynamic partition pruning not visible

**Scenario / symptom:** A star-schema query scans more data than expected.

**Learner task:** Determine whether AQE is the actual bottleneck or merely part of the execution context.

**Investigation steps:**
1. Record `spark.version` and relevant effective configuration.
2. Capture the initial/final plan where available.
3. Inspect stages, tasks, shuffle, partition-size distribution, and long-tail behavior.
4. Form one hypothesis before changing anything.
5. Change one variable and rerun the same workload.

**Expected reasoning / corrective approach:** Inspect fact partitioning, join/filter relationship, scan partition filters, configuration, data source, and Spark version.

**Production rule:** Do not accept a configuration change until the evidence explains the observed symptom and correctness has been revalidated.

## Exercise 9 — Excessive manual tuning

**Scenario / symptom:** A job contains many historical partition settings.

**Learner task:** Determine whether AQE is the actual bottleneck or merely part of the execution context.

**Investigation steps:**
1. Record `spark.version` and relevant effective configuration.
2. Capture the initial/final plan where available.
3. Inspect stages, tasks, shuffle, partition-size distribution, and long-tail behavior.
4. Form one hypothesis before changing anything.
5. Change one variable and rerun the same workload.

**Expected reasoning / corrective approach:** Inventory each setting, preserve a baseline, remove one unjustified assumption, and validate.

**Production rule:** Do not accept a configuration change until the evidence explains the observed symptom and correctness has been revalidated.

## Exercise 10 — Bad join condition

**Scenario / symptom:** Join output is unexpectedly huge.

**Learner task:** Determine whether AQE is the actual bottleneck or merely part of the execution context.

**Investigation steps:**
1. Record `spark.version` and relevant effective configuration.
2. Capture the initial/final plan where available.
3. Inspect stages, tasks, shuffle, partition-size distribution, and long-tail behavior.
4. Form one hypothesis before changing anything.
5. Change one variable and rerun the same workload.

**Expected reasoning / corrective approach:** Check join keys, duplicates, cardinality, null behavior, accidental many-to-many relationships, and cross joins.

**Production rule:** Do not accept a configuration change until the evidence explains the observed symptom and correctness has been revalidated.

## Exercise 11 — Final plan unchanged

**Scenario / symptom:** Initial and final adaptive plans look equivalent.

**Learner task:** Determine whether AQE is the actual bottleneck or merely part of the execution context.

**Investigation steps:**
1. Record `spark.version` and relevant effective configuration.
2. Capture the initial/final plan where available.
3. Inspect stages, tasks, shuffle, partition-size distribution, and long-tail behavior.
4. Form one hypothesis before changing anything.
5. Change one variable and rerun the same workload.

**Expected reasoning / corrective approach:** Explain that AQE can retain the initial strategy when runtime evidence does not justify a change.

**Production rule:** Do not accept a configuration change until the evidence explains the observed symptom and correctness has been revalidated.

## Exercise 12 — UDF blamed on AQE

**Scenario / symptom:** A query with a Python UDF is slow and the team suspects AQE.

**Learner task:** Determine whether AQE is the actual bottleneck or merely part of the execution context.

**Investigation steps:**
1. Record `spark.version` and relevant effective configuration.
2. Capture the initial/final plan where available.
3. Inspect stages, tasks, shuffle, partition-size distribution, and long-tail behavior.
4. Form one hypothesis before changing anything.
5. Change one variable and rerun the same workload.

**Expected reasoning / corrective approach:** Compare native-expression and UDF versions and inspect the execution boundary and task behavior.

**Production rule:** Do not accept a configuration change until the evidence explains the observed symptom and correctness has been revalidated.

# 40. Production Scenarios

## Scenario 1 — Large fact/dimension join with unknown selectivity

**Scenario:** The filtered dimension varies from large to very small across runs.

**Evidence to inspect:** Initial/final plans, runtime relation size, broadcast exchange, shuffle metrics.

**Candidate investigation/solution:** AQE may switch the remaining join strategy when actual size supports it.

**Trade-offs:** Broadcast memory and workload variability must be validated.

**Validation strategy:** Re-run the same representative workload, compare correctness and multi-dimensional performance metrics, and document the decision. Do not infer a universal rule from one experiment.

## Scenario 2 — Thousands of tiny shuffle partitions

**Scenario:** A stage has many short tasks and low work per task.

**Evidence to inspect:** Shuffle size, task count, task duration, adaptive coalescing.

**Candidate investigation/solution:** Test post-shuffle coalescing and advisory partition size.

**Trade-offs:** Too-large coalesced tasks can reduce parallelism.

**Validation strategy:** Re-run the same representative workload, compare correctness and multi-dimensional performance metrics, and document the decision. Do not infer a universal rule from one experiment.

## Scenario 3 — Hot join key

**Scenario:** One partition/task dominates the stage.

**Evidence to inspect:** Partition-size and task-duration distributions, join plan.

**Candidate investigation/solution:** AQE skew join if applicable; otherwise salting/pre-aggregation/modeling.

**Trade-offs:** Replication and extra work must be weighed.

**Validation strategy:** Re-run the same representative workload, compare correctness and multi-dimensional performance metrics, and document the decision. Do not infer a universal rule from one experiment.

## Scenario 4 — Star schema with partitioned fact

**Scenario:** A selective dimension filter accompanies a large partitioned fact.

**Evidence to inspect:** Scan, partition filters, join, input bytes, DPP evidence.

**Candidate investigation/solution:** Validate dynamic partition pruning and storage layout.

**Trade-offs:** Weak selectivity or poor layout may limit benefit.

**Validation strategy:** Re-run the same representative workload, compare correctness and multi-dimensional performance metrics, and document the decision. Do not infer a universal rule from one experiment.

## Scenario 5 — AQE-enabled job still slow

**Scenario:** AQE is on but end-to-end runtime remains high.

**Evidence to inspect:** Plan/UI/metrics and input/storage behavior.

**Candidate investigation/solution:** Investigate whether scan, UDF, data explosion, storage, JDBC, or driver work dominates.

**Trade-offs:** AQE may not be the right lever.

**Validation strategy:** Re-run the same representative workload, compare correctness and multi-dimensional performance metrics, and document the decision. Do not infer a universal rule from one experiment.

## Scenario 6 — Broadcast causes executor pressure

**Scenario:** An adaptive or hinted broadcast relation consumes substantial memory.

**Evidence to inspect:** Final plan, broadcast size, executor memory/spill.

**Candidate investigation/solution:** Improve filtering/projection, remove unsafe hint, adjust threshold, or use non-broadcast strategy.

**Trade-offs:** Less broadcast may mean more shuffle.

**Validation strategy:** Re-run the same representative workload, compare correctness and multi-dimensional performance metrics, and document the decision. Do not infer a universal rule from one experiment.

## Scenario 7 — Manual shuffle tuning became obsolete

**Scenario:** A job contains historical hard-coded partition settings.

**Evidence to inspect:** Current AQE behavior and representative workload measurements.

**Candidate investigation/solution:** Remove one unnecessary assumption at a time.

**Trade-offs:** Validate no regression before rollout.

**Validation strategy:** Re-run the same representative workload, compare correctness and multi-dimensional performance metrics, and document the decision. Do not infer a universal rule from one experiment.

## Scenario 8 — AQE ON/OFF regression

**Scenario:** AQE-enabled workload becomes slower after a Spark upgrade.

**Evidence to inspect:** Spark version, initial/final plans, configuration, repeated metrics.

**Candidate investigation/solution:** Identify which adaptive decision changed and why.

**Trade-offs:** Do not generalize from one workload or one run.

**Validation strategy:** Re-run the same representative workload, compare correctness and multi-dimensional performance metrics, and document the decision. Do not infer a universal rule from one experiment.

## Scenario 9 — DPP with poor partition layout

**Scenario:** DPP is conceptually applicable but scan cost remains high.

**Evidence to inspect:** Storage partition layout and actual input bytes.

**Candidate investigation/solution:** Improve physical layout rather than relying only on runtime pruning.

**Trade-offs:** Storage redesign has operational cost.

**Validation strategy:** Re-run the same representative workload, compare correctness and multi-dimensional performance metrics, and document the decision. Do not infer a universal rule from one experiment.

## Scenario 10 — Overuse of hints

**Scenario:** Every join has a hard-coded hint.

**Evidence to inspect:** Hint inventory, actual plans, memory/task metrics.

**Candidate investigation/solution:** Remove unjustified hints experimentally.

**Trade-offs:** Hints can constrain optimizer flexibility.

**Validation strategy:** Re-run the same representative workload, compare correctness and multi-dimensional performance metrics, and document the decision. Do not infer a universal rule from one experiment.

# 41. Common Misconceptions

## 1. AQE replaces Catalyst

**Correction:** AQE works with Spark's planning/optimization machinery; it does not replace Catalyst.

## 2. AQE automatically fixes every skew problem

**Correction:** Supported skewed joins can benefit, while aggregation/window skew may require other techniques.

## 3. AQE means I never need repartition()

**Correction:** Manual partitioning remains relevant for execution and storage requirements.

## 4. AQE always makes queries faster

**Correction:** Benefits depend on workload, uncertainty, configuration, resources, and overhead.

## 5. AQE always broadcasts small tables

**Correction:** Join type, thresholds, hints, memory, statistics, and version behavior matter.

## 6. AQE eliminates all shuffle tuning

**Correction:** It can reduce some rigid tuning but does not eliminate partition and layout engineering.

## 7. AQE fixes bad data models

**Correction:** Modeling problems require modeling changes.

## 8. AQE fixes Python UDF performance

**Correction:** AQE does not turn Python execution into native Spark execution.

## 9. The final plan must differ from the initial plan

**Correction:** AQE may legitimately keep the original strategy.

## 10. More partitions always means better performance

**Correction:** More tasks can increase scheduler and task overhead.

## 11. Broadcast is always faster

**Correction:** Broadcast can be unsafe or unnecessary for larger relations.

## 12. DPP is the same as ordinary partition pruning

**Correction:** DPP derives pruning information dynamically from query relationships.

## 13. AQE can change anything at any time

**Correction:** Adaptation is constrained by runtime information, execution boundaries, and supported strategies.

## 14. Spark configuration defaults are universal

**Correction:** Defaults and behavior must be verified against the installed Spark version.

## 15. A configuration name is enough to tune Spark

**Correction:** A setting must be tied to a measured workload problem and validated.

## 16. One benchmark run proves a setting is better

**Correction:** Performance is variable; use repeated representative trials.

## 17. AdaptiveSparkPlan proves performance improved

**Correction:** It indicates adaptive execution, not an outcome.

## 18. Larger advisory partition size is always better

**Correction:** It can reduce task count while increasing task size and memory pressure.

## 19. DPP appearing means the query is optimized

**Correction:** Pruning can exist while another bottleneck dominates.

## 20. AQE makes storage layout irrelevant

**Correction:** Input/file/partition layout can dominate scan performance.

## 21. Join hints are harmless

**Correction:** Hints can constrain strategy and create memory risk.

## 22. AQE eliminates the need for statistics

**Correction:** Pre-execution statistics remain important for initial planning.

## 23. Runtime statistics are omniscient

**Correction:** They describe observed completed work, not future execution.

## 24. AQE should be tuned before inspecting the plan

**Correction:** Plan/UI evidence should precede hypothesis-driven tuning.

## 25. If AQE does not fix a problem, Spark is broken

**Correction:** Many bottlenecks are outside AQE's scope.

# 42. Practice Questions

Exactly 40 questions are provided: 10 Basic, 10 Moderate, 10 Hard, and 10 Advanced.

## Basic — 1–10

1. What problem does AQE solve?
2. Explain static versus adaptive planning.
3. How does AQE relate to Catalyst?
4. What are runtime statistics?
5. Why do stage boundaries matter?
6. What does `AdaptiveSparkPlan` indicate?
7. What is a post-shuffle partition?
8. Why can tiny shuffle partitions be inefficient?
9. What is advisory partition size?
10. Why does AQE not guarantee faster queries?

## Moderate — 11–20

11. How can filtering cause AQE to reconsider a join?
12. Why can sort-merge be a reasonable initial strategy even if broadcast later becomes viable?
13. What evidence would show post-shuffle coalescing?
14. Contrast estimated and actual relation size.
15. Why can increasing the broadcast threshold be dangerous?
16. What does AQE skew-join optimization attempt to do?
17. Distinguish an absolute skew threshold from a relative skew factor.
18. Why does skew-join handling not automatically solve aggregation skew?
19. Explain DPP using a fact/dimension example.
20. Why change one AQE setting at a time?

## Hard — 21–30

21. A join begins as sort-merge and ends as broadcast. Explain the likely sequence.
22. Design an experiment for 20,000 tiny shuffle partitions.
23. AQE is enabled but the final plan is unchanged. Give plausible explanations.
24. Design an advisory partition-size experiment.
25. A skewed join remains slow after AQE. Build an investigation tree.
26. Why can a broadcast hint be dangerous?
27. Compare static partition pruning and DPP.
28. Why cannot AQE retroactively change a completed stage?
29. Design an AQE ON/OFF experiment and list metrics.
30. How does AQE change the role of `spark.sql.shuffle.partitions`?

## Advanced — 31–40

31. Why can AQE be valuable for workloads with variable selectivity?
32. Design a matrix for tiny-partition, small-after-filter, and skewed-join workloads.
33. How would you evaluate an adaptive broadcast that reduces shuffle but increases memory pressure?
34. Design a production troubleshooting workflow for a slow AQE-enabled join.
35. Explain the relationship among DPP, partitioned storage, Catalyst, and AQE.
36. How would you evaluate whether an old join hint should remain?
37. Why are “more partitions” and “higher broadcast threshold” examples of cargo-cult tuning risk?
38. Design a version-controlled experiment that isolates AQE from storage and cluster variability.
39. How do you distinguish an AQE limitation from a data-model limitation?
40. Give a senior-engineer explanation connecting runtime statistics, stage boundaries, coalescing, join adaptation, skew, DPP, and troubleshooting.

# 43. Interview Questions

Exactly 40 questions are provided: 10 Basic, 10 Moderate, 10 Hard, and 10 Advanced.

## Basic — 1–10

1. What is AQE?
2. Why was AQE introduced?
3. How is AQE different from Catalyst?
4. What are runtime statistics?
5. What is `AdaptiveSparkPlan`?
6. What is an initial adaptive plan?
7. What is post-shuffle partition coalescing?
8. What is advisory partition size?
9. What is skew-join optimization?
10. What is DPP?

## Moderate — 11–20

11. Why can static planning be suboptimal?
12. How does AQE obtain runtime information?
13. Why are shuffle boundaries important?
14. Explain sort-merge to broadcast adaptation.
15. What are broadcast risks?
16. How would you inspect adaptive coalescing?
17. How do skew threshold and skew factor differ?
18. When will AQE not solve skew?
19. How would you inspect an AQE plan?
20. How would you safely change an AQE setting?

## Hard — 21–30

21. A query is slow although AQE is enabled. How do you investigate?
22. Why might AQE retain the initial join strategy?
23. How do you distinguish partitioning from skew?
24. How do you determine whether broadcast is safe?
25. How do you evaluate advisory partition-size changes?
26. How does AQE change manual shuffle tuning?
27. How do join hints interact with adaptive planning?
28. Why is DPP relevant to star schemas?
29. What Spark UI evidence would you inspect?
30. How would you prove an AQE change improved performance?

## Advanced — 31–40

31. Explain AQE as a runtime control loop.
32. How would you isolate AQE's contribution from storage and cluster variability?
33. How would you design execution for highly variable intermediate relation sizes?
34. Adaptive broadcast causes memory pressure. What do you inspect and change?
35. Skewed join improves but aggregation skew remains. Why and what next?
36. Explain Catalyst's initial planning and AQE's runtime re-optimization together.
37. How would you decide whether to remove an old tuning setting?
38. How would you audit dozens of AQE-related production settings?
39. How would you explain AQE's role and limits to an architecture review board?
40. Describe a complete AQE-related production incident investigation, including evidence, hypothesis, experiment, validation, and rollback criteria.

# 44. Architecture Questions

For every scenario, provide: scenario, symptoms, evidence, candidate explanations, investigation, solutions, trade-offs, and validation.

## Scenario 1 — Variable-selectivity fact/dimension join
A large fact joins a dimension whose filter selectivity varies dramatically. Determine whether AQE runtime join adaptation is useful and how you would validate broadcast safety.

## Scenario 2 — Tiny shuffle partitions
A stage creates thousands of tiny shuffle partitions. Determine whether adaptive coalescing can reduce downstream task overhead and how you would measure the trade-off.

## Scenario 3 — Hot join key
One join key creates a long-tail task. Determine whether AQE skew-join handling applies and when salting or pre-aggregation is required.

## Scenario 4 — Star-schema fact table
A filtered dimension joins a partitioned fact table. Determine whether DPP can reduce irrelevant reads and whether the physical layout supports it.

## Scenario 5 — AQE-enabled job still slow
AQE is enabled but end-to-end performance remains poor. Separate AQE issues from scan, UDF, storage, JDBC, driver, or modeling bottlenecks.

## Scenario 6 — Broadcast memory pressure
Adaptive execution chooses broadcast and executors show memory pressure. Decide whether to change threshold, filtering/projection, hints, or strategy after inspecting evidence.

## Scenario 7 — Historical manual tuning
A job contains years of hard-coded shuffle settings. Design a safe removal and validation process.

## Scenario 8 — AQE regression after upgrade
AQE ON becomes slower after a Spark upgrade. Compare Spark version, configuration, initial/final plans, and repeated metrics before changing anything.

## Scenario 9 — DPP with poor storage layout
DPP is conceptually applicable but scan cost remains high. Determine whether the real problem is physical data layout.

## Scenario 10 — Hint-heavy application
Every join has a hard-coded hint. Design an evidence-based hint audit and rollback strategy.

# 45. Production Checklist

## Before Running

- [ ] Spark version verified.
- [ ] AQE configuration inspected.
- [ ] Dataset characteristics understood.
- [ ] Partitioning understood.
- [ ] Join strategy understood.

## During Investigation

- [ ] Initial plan captured.
- [ ] Final plan captured.
- [ ] AQE state checked.
- [ ] Shuffle metrics inspected.
- [ ] Partition sizes inspected.
- [ ] Task distribution inspected.
- [ ] Skew inspected.

## During Tuning

- [ ] One variable changed at a time.
- [ ] Hypothesis documented.
- [ ] Baseline preserved.
- [ ] Runtime measured.
- [ ] Resource usage measured.
- [ ] Correctness validated.

## Before Production

- [ ] AQE behavior validated on representative data.
- [ ] Configuration documented.
- [ ] No unnecessary hints.
- [ ] No unnecessary hard-coded tuning.
- [ ] Failure modes understood.
- [ ] Spark-version behavior verified.

# 46. Performance Measurement Principles

Measure more than wall-clock time:

- task count;
- stage duration;
- shuffle read/write;
- input/output size;
- partition-size distribution;
- executor memory behavior;
- spill;
- long-tail tasks.

Repeat experiments because results can vary with warm-up, dataset, storage, cluster load, and runtime environment. One run is not enough evidence.

A useful record is:

```text
Spark version:
JVM:
Python:
AQE setting:
Shuffle partitions:
Advisory size:
Dataset:
Dataset size:
Cluster:
Storage:
Run:
Runtime:
Shuffle read:
Shuffle write:
Tasks:
Long-tail observations:
Plan change:
Conclusion:
```

# 47. Cross-Connections with Previous Topics

### Topic 07 — Joins, Shuffle, Broadcast
AQE builds on join strategy and data movement. Runtime relation size can change the join decision.

### Topic 08 — Partitioning
AQE builds on shuffle partitions, repartitioning, coalescing, and task parallelism.

### Topic 09 — Data Skew
AQE can adapt supported skewed joins, while salting/pre-aggregation remain necessary for other skew patterns.

### Topic 10 — Caching/Persistence
Caching affects repeated computation and runtime behavior but does not replace adaptive execution.

### Topic 11 — UDFs
Python UDFs can be expensive execution boundaries. AQE cannot transform them into native expressions.

### Topic 12 — Catalyst/Explain Plans
Topic 12 explains the initial planning pipeline. Topic 13 adds runtime feedback:

```text
Catalyst → Initial Physical Plan → Runtime Statistics → AQE → Adapted Remaining Plan
```

Also connect AQE to data modeling, star schemas, partitioned storage, Parquet, Spark UI, and performance engineering without re-teaching those topics.

# 48. Forward Connection to Topics 14–16

### Topic 14 — Data Sources, Save Modes, Bucketing
AQE decisions depend on the characteristics of data entering and leaving the query. Storage layout remains important.

### Topic 15 — Spark UI and Debugging Slow Jobs
The plan/metric reasoning learned here becomes the foundation for deeper Spark UI diagnosis.

### Topic 16 — Testing PySpark Code
AQE experiments should be reproducible and correctness-checked; performance changes must not silently alter results.

# 49. Spark Version Awareness

The roadmap uses modern Spark and warns that many online tutorials target older Spark releases. Therefore:

- verify `spark.version`;
- prefer APIs/configuration supported by the installed release;
- flag version-sensitive behavior;
- do not invent configuration names;
- do not invent defaults;
- do not fabricate plan output;
- do not fabricate Spark UI output;
- do not fabricate benchmark numbers.

```python
print(spark.version)
```

Use the installed runtime as the authority for an experiment.

# 50. No Fabricated Benchmarks

Never state a percentage improvement unless the learner actually measured it. Instead:

> Measure the runtime before and after the change.

Results depend on dataset size/distribution, hardware, Spark version, JVM, storage, cluster resources, and configuration.

# 51. Simple → Advanced Progression

### Level 1 — Foundation
AQE purpose, static vs adaptive planning, Catalyst vs AQE.

### Level 2 — Execution Mechanics
Stage boundaries, runtime statistics, `AdaptiveSparkPlan`, initial/final plans.

### Level 3 — Core Features
Post-shuffle coalescing, advisory partition size, runtime join switching, broadcast, skew-join optimization.

### Level 4 — Advanced AQE
DPP, configuration, hints, manual tuning.

### Level 5 — Production Engineering
Debugging, AQE ON/OFF, Spark UI, measurement, limitations, architecture decisions.

### Level 6 — Mastery
Practice, debugging, interviews, architecture, production checklist, final assessment.

# 52. Learning Checkpoints

## Checkpoint 1 — AQE Fundamentals

You should explain AQE in one paragraph, explain why static planning can be insufficient, and distinguish Catalyst from AQE.

## Checkpoint 2 — Runtime Adaptation

You should explain runtime statistics, stage boundaries, `AdaptiveSparkPlan`, and initial/final plans.

## Checkpoint 3 — Core Features

You should explain coalescing, advisory size, runtime join switching, and skew-join optimization.

## Checkpoint 4 — Advanced AQE

You should explain DPP, configuration, hint interaction, and AQE limitations.

## Checkpoint 5 — Production

You should diagnose a slow AQE-enabled query, read initial/final plan evidence, and test a performance hypothesis.

# 53. Final Assessment

## Theory Assessment

Without the chapter, explain:

1. AQE from memory.
2. Catalyst versus AQE.
3. Runtime statistics.
4. Stage boundaries.
5. `AdaptiveSparkPlan`.
6. Initial versus final plans.
7. Partition coalescing.
8. Advisory partition size.
9. Runtime join switching.
10. Sort-merge → broadcast adaptation.
11. Skew-join optimization.
12. Skew thresholds/factors.
13. Dynamic partition pruning.
14. AQE configuration strategy.
15. Manual tuning interaction.
16. AQE limitations.

## Hands-On Assessment

Build a small reproducible lab that:

1. generates configurable synthetic data;
2. creates a shuffle-heavy workload;
3. creates a small-after-filter join;
4. creates a skewed join;
5. creates partitioned fact data;
6. runs AQE OFF and ON;
7. captures initial/final plan evidence;
8. records tasks and shuffle metrics;
9. tests advisory partition size;
10. investigates DPP;
11. writes a production-style conclusion.

A passing answer explains **why** the plan changed or did not change, what evidence proves the result, and what trade-offs were introduced.

# 54. Required Study Loop

```text
READ
↓
UNDERSTAND THE CONCEPT
↓
PREDICT WHAT SPARK WILL DO
↓
WRITE THE PYSPARK CODE
↓
EXPLAIN THE PLAN
↓
RUN A SMALL DATASET
↓
COMPARE AQE ON/OFF
↓
READ SPARK UI
↓
CHANGE ONE VARIABLE
↓
MEASURE AGAIN
↓
EXPLAIN WHY THE RESULT CHANGED
↓
DOCUMENT THE FINDING
↓
EXPLAIN IT ALOUD
↓
APPLY IT TO A PRODUCTION SCENARIO
```

# 55. Glossary

**Adaptive Query Execution (AQE)** — Runtime execution framework that uses observed information to adapt supported remaining query execution.

**Catalyst** — Spark SQL's analysis and optimization framework.

**Runtime statistics** — Observed execution information such as intermediate sizes and shuffle partition characteristics.

**Stage boundary** — A boundary between execution regions, commonly associated with shuffle/materialized output.

**Shuffle** — Redistribution of data across partitions.

**Shuffle partition** — A partition of shuffle output consumed by downstream work.

**Post-shuffle partition** — A downstream-consumable partition representing shuffle output.

**Advisory partition size** — A target used by adaptive partition sizing/coalescing decisions.

**Coalescing** — Combining multiple smaller partitions into fewer larger partitions.

**Broadcast join** — Join strategy that distributes one side to executors rather than performing the same shuffle on that side.

**Sort-merge join** — Large-scale equi-join strategy based on partitioning/shuffle and sorting.

**Skew** — Uneven distribution where some keys or partitions contain substantially more data.

**Skewed partition** — An unusually large partition relative to its peers.

**Skew factor** — Relative criterion used in skew detection.

**Skew threshold** — Absolute size criterion used in skew detection.

**Dynamic partition pruning** — Runtime/query-derived filtering that can avoid reading irrelevant storage partitions in supported shapes.

**Partition pruning** — Avoiding reads of irrelevant storage partitions.

**AdaptiveSparkPlan** — Plan representation associated with adaptive execution.

**Initial plan** — Physical strategy used at the beginning of execution.

**Final plan** — Adaptive plan state reached after relevant runtime decisions.

**Exchange** — Physical redistribution of data between partitions.

**Executor** — Spark worker process executing tasks and holding data.

**Task** — Unit of Spark execution over a partition.

**Long-tail task** — An unusually slow task that delays completion of peer work.

# 56. Topic Completion Standard

Before moving to Topic 14, verify that you can:

- [ ] explain AQE from first principles;
- [ ] distinguish Catalyst and AQE;
- [ ] explain runtime statistics and stage boundaries;
- [ ] recognize `AdaptiveSparkPlan`;
- [ ] explain initial/final plans;
- [ ] explain post-shuffle partition coalescing;
- [ ] explain advisory partition size;
- [ ] explain runtime join switching;
- [ ] explain sort-merge → broadcast adaptation;
- [ ] explain skew-join optimization and its thresholds/factors;
- [ ] distinguish join skew from aggregation/window skew;
- [ ] explain and test DPP;
- [ ] inspect AQE configuration;
- [ ] tune from evidence rather than guesswork;
- [ ] explain manual partition and hint interactions;
- [ ] explain what AQE cannot fix;
- [ ] run AQE ON/OFF experiments;
- [ ] interpret Spark UI evidence;
- [ ] complete the debugging exercises;
- [ ] answer the practice and interview questions;
- [ ] solve architecture scenarios;
- [ ] complete the final theory and hands-on assessments.

## Final Takeaway

> **Static planning uses what Spark knows before execution. AQE uses what Spark learns during execution to make better decisions about work that has not yet been completed.**

The production-engineering question is therefore not simply:

> "Which AQE setting should I change?"

It is:

> **"What did the initial plan assume, what actually happened at runtime, what decision can still change, and what evidence will prove that the change helped?"**
