# Spark UI and Debugging Slow Jobs

> **Module 2.14 — Distributed Processing with PySpark | Topic 15**
>
> Production principle: **Do not tune Spark by guessing. Diagnose first. Change one thing. Measure again.**

---

## 1. Learning Objectives

By the end of this topic, you should be able to:

- Navigate the Spark UI and understand what each major tab is for.
- Find the slowest job, stage, and task pattern.
- Interpret task minimum, median, maximum, distribution, shuffle, spill, and GC metrics.
- Connect Spark UI evidence to SQL/DataFrame physical plans.
- Read driver and executor logs and use appropriate log levels.
- Use event logs and the Spark History Server for completed applications.
- Diagnose skew, spill, excessive or insufficient parallelism, large shuffles, expensive UDFs, and over-caching.
- Distinguish driver OOM, executor OOM, memory-overhead/container failures, shuffle fetch failures, lost executors, and serialization failures.
- Recognize stragglers and understand when speculative execution helps or does not.
- Build a repeatable evidence-based debugging workflow.
- Collect Spark metrics programmatically at an appropriate advanced-awareness level.
- Track performance regressions and write a production performance investigation report.

### The core outcome

A slow Spark job is a **symptom**, not a root cause.

The professional debugging path is:

```text
Slow Job
   ↓
Find Slow Stage
   ↓
Find Abnormal Task Distribution
   ↓
Inspect Metrics
   ↓
Inspect SQL Plan
   ↓
Inspect Logs
   ↓
Form Root-Cause Hypothesis
   ↓
Change One Thing
   ↓
Re-run
   ↓
Measure
   ↓
Validate Correctness
   ↓
Document
```

---

## 2. Why Spark Debugging Matters

Distributed systems fail and slow down for different reasons at different layers.

A statement such as:

> "The Spark job took 45 minutes."

does not identify the problem.

You need to determine:

- Which job was slow?
- Which stage consumed the time?
- Were tasks balanced?
- Was one partition much larger than the others?
- How much input was processed?
- How much data was shuffled?
- Was data spilled to memory or disk?
- Was GC consuming significant task time?
- Did a Python UDF add expensive execution?
- Did executors fail or disappear?
- Did the driver perform an unsafe operation such as `collect()`?
- Did a physical-plan operator perform substantially more work than expected?

A production engineer therefore works from **evidence** rather than configuration folklore.

### A useful rule

> **Do not ask "what configuration should I change?" until you have evidence about what is actually wrong.**

Random tuning creates:

- configuration complexity,
- infrastructure cost,
- hidden technical debt,
- false confidence,
- difficult incident diagnosis.

---

## 3. The Spark Debugging Mental Model

The central loop for this topic is:

```text
SYMPTOM
  ↓
EVIDENCE
  ↓
SPARK UI
  ↓
STAGE
  ↓
TASK METRICS
  ↓
EXECUTION PLAN
  ↓
ROOT-CAUSE HYPOTHESIS
  ↓
ONE CHANGE
  ↓
RE-RUN
  ↓
MEASURE
  ↓
VALIDATE
  ↓
DOCUMENT
```

### Evidence hierarchy

Prefer evidence in roughly this order:

1. Application/job duration and failure state.
2. Stage duration and task distribution.
3. Shuffle, spill, input/output, and GC metrics.
4. SQL/DataFrame runtime operator metrics.
5. Physical plan.
6. Driver/executor logs.
7. Cluster/infrastructure evidence.
8. Configuration evidence from the actual running application.

This is not a rigid rule. A failure can require logs before a stage can finish. The point is to avoid changing settings before understanding the symptom.

### Hypothesis quality

A useful hypothesis is testable.

Weak:

> "Spark needs more memory."

Stronger:

> "The aggregation stage has a small number of very large partitions, producing long task tails and disk spill; reducing partition concentration or changing the aggregation strategy should reduce maximum task time and spill."

The second hypothesis predicts observable changes.

---

## 4. Spark Application Execution Recap

You already learned driver, executors, jobs, stages, tasks, partitions, shuffle, DataFrames, SQL, Catalyst, and AQE.

For debugging, keep this compact model:

```text
Application
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
Executor execution
```

A wide dependency can introduce an `Exchange` and therefore a shuffle boundary. That boundary often becomes a useful debugging landmark.

Do not treat every slow stage as independently meaningful. A stage can be slow because of work produced by earlier design choices.

---

## 5. Starting and Accessing the Spark UI

The Spark UI is normally available while an application is active. The exact address and exposed tabs can vary with deployment mode, Spark version, cluster manager, and platform.

### Local development

A simple PySpark application:

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = (
    SparkSession.builder
    .appName("spark-ui-debugging")
    .master("local[*]")
    .getOrCreate()
)

df = spark.range(0, 5_000_000)

result = (
    df.withColumn("bucket", F.col("id") % 100)
      .groupBy("bucket")
      .count()
)

result.show()

spark.stop()
```

While the application is active, inspect the Spark UI exposed by the running Spark application/environment rather than assuming a universal port.

### Useful checks

```python
print(spark.version)
print(spark.sparkContext.uiWebUrl)
```

`uiWebUrl` can be `None` depending on the context and environment. In managed platforms, the platform may expose the UI through its own interface.

### Deployment contexts

The debugging concepts remain the same across:

- local mode,
- Spark Standalone,
- YARN,
- Kubernetes,
- managed Spark platforms.

What changes is how you access logs, executors, event logs, infrastructure metrics, and the history service.

---

## 6. Spark UI Overview

The Spark UI answers different questions at different levels.

| Tab | Main question |
|---|---|
| Jobs | What jobs ran and how long did they take? |
| Stages | Which execution stage is slow? |
| Storage | What is cached or persisted? |
| Environment | What configuration/environment is active? |
| Executors | What are executors doing and failing on? |
| SQL / DataFrame | Which operators consumed time/resources? |

Exact labels and details are version-sensitive.

### Jobs → Stages → Tasks

Think of the UI as a drill-down:

```text
Application
   ↓
Jobs
   ↓
Stages
   ↓
Tasks
   ↓
Task metrics / executor evidence
```

### UI versus logs

The UI is excellent for answering:

- what happened,
- where it happened,
- how long it took,
- how work was distributed.

Logs are often required to answer:

- why an executor disappeared,
- why a Python worker failed,
- which exception occurred,
- why a container was killed.

A strong investigation uses both.

---

## 7. Jobs Tab

The Jobs tab is the first place to identify **which job is actually slow**.

Typical information includes:

- Job ID,
- description,
- submission time,
- duration,
- stages,
- active jobs,
- completed jobs,
- failed jobs.

### Action → Job → Stages

A DataFrame operation is lazy until an action requires execution.

For example:

```python
df.filter("amount > 100").count()
```

The `count()` action can create a Spark job.

The application may execute many actions:

```python
df.count()
df.groupBy("country").count().show()
df.write.mode("overwrite").parquet("/some/path")
```

Therefore:

> Application runtime is not necessarily the duration of one DataFrame action.

### First question

Ask:

> **Which job is actually slow?**

Do not immediately optimize the last operation you wrote in Python.

---

## 8. Stages Tab

A stage is an execution region separated by dependency boundaries, particularly shuffle boundaries.

You already know the theory. Here, use it diagnostically.

Look for:

- stage duration,
- number of tasks,
- input,
- output,
- shuffle read,
- shuffle write,
- failed tasks,
- task-duration distribution.

### Slowest stage first

The longest stage is often the best place to begin.

It is **not automatically the root cause**.

For example:

```text
Stage 0: 20 s
Stage 1: 2 min
Stage 2: 50 min
```

Stage 2 deserves investigation first. But Stage 2 may be slow because Stage 1 produced pathological partitioning, or because its join strategy generated excessive shuffle.

---

## 9. Task Metrics

Task-level statistics are often more informative than stage duration alone.

Common summary values include:

- minimum,
- median,
- maximum.

Illustrative example:

```text
Task times:

2s
2s
3s
3s
4s
5s
90s
```

The median is close to the normal workload, while the maximum is dramatically larger.

This can indicate a **straggler**.

Possible explanations include:

- data skew,
- unusually large partition,
- slow executor/node,
- external I/O,
- GC,
- resource contention.

One metric does not prove the cause.

### Minimum task time

A low minimum means at least one task completed quickly. It does not prove the stage is healthy.

### Median task time

The median is useful as a representation of a typical task because it is less affected by a small number of extreme tasks.

### Maximum task time

A large maximum relative to the median is a strong signal for further investigation.

A useful diagnostic quantity is:

```text
max task time / median task time
```

This ratio is a clue, not a universal threshold.

---

## 10. Task-Time Distribution

A balanced workload might resemble:

```text
10s
11s
10s
12s
11s
```

A long-tail workload might resemble:

```text
10s
11s
12s
11s
140s
```

Look for:

- median,
- maximum,
- long tail,
- quantiles when available,
- concentration of slow tasks.

### What a long tail can mean

A long tail may result from:

- skew,
- large partitions,
- slow nodes,
- GC,
- I/O,
- contention,
- transient infrastructure problems.

Do not immediately label it "skew."

Ask whether the slow task is processing more data, experiencing more spill, spending more time in GC, or running on an unhealthy executor.

---

## 11. Reading a Stage in Detail

A productive stage investigation asks:

### Workload

- How much input?
- How much output?
- How many tasks?
- How much shuffle?

### Distribution

- What is min/median/max task time?
- Is there a long tail?
- Are only a few tasks slow?
- Are all tasks slow?

### Resource behavior

- Is there spill?
- Is GC high?
- Are executors failing?
- Is memory pressure visible?

### Operator behavior

- What operators produced this stage?
- Is there an `Exchange`?
- Is there a join?
- Is there an aggregation?
- Is there a sort?
- Is Python execution involved?

This turns a stage page into an investigation rather than a dashboard-reading exercise.

---

## 12. Shuffle Read

**Shuffle read** represents data fetched by tasks from shuffle output.

It commonly appears after operations such as:

- joins,
- aggregations,
- repartitioning,
- sorting,
- other operations that require redistribution.

Large shuffle read can mean substantial network/data movement.

But:

> **Large shuffle is not automatically bad.**

Interpret it relative to:

- input size,
- expected operation,
- partitioning,
- workload shape,
- runtime,
- output requirements.

A large join over a large dataset may legitimately require significant shuffle.

### Diagnostic questions

```text
Is shuffle large?
        ↓
Was a shuffle expected?
        ↓
Is the shuffle disproportionately large?
        ↓
Is task distribution balanced?
        ↓
Is there skew?
        ↓
Could a different join strategy reduce movement?
```

---

## 13. Shuffle Write

Shuffle write is data written for downstream stages to consume.

It is strongly associated with operations that redistribute data.

A physical plan such as:

```text
Exchange
   ↓
SortMergeJoin
```

should make you expect shuffle activity.

Use shuffle write/read together with stage duration and task distribution.

### A useful pattern

```text
Large Shuffle Write
+
Large Shuffle Read
+
Long Stage
+
High Network Activity
```

is evidence for a network/data-movement-heavy stage.

It is not sufficient by itself to prove the query design is wrong.

---

## 14. Input and Output Metrics

Input size tells you how much data a stage reads from an external source or upstream representation.

Output tells you how much data is produced.

Use these metrics to establish scale.

### Why scale matters

Suppose two jobs both have a 10-minute stage:

```text
Job A: 50 MB input
Job B: 2 TB input
```

The same duration means something very different.

Always normalize performance discussions against workload volume.

### Questions

- Did input volume grow?
- Did output explode?
- Did filtering become less selective?
- Did a join multiply rows?
- Did a file layout change create more work?

Performance regression is often a workload change rather than an engine defect.

---

## 15. Memory Spill

Spill occurs when an execution operator cannot keep all required intermediate state in memory.

Conceptually:

```text
Working Data
     ↓
Memory available?
     ↓
Yes → Continue
No  → Spill
```

Memory spill is not automatically a failure.

It becomes important when it is associated with:

- long task times,
- large partitions,
- memory pressure,
- disk spill,
- high GC.

Common contributors:

- large aggregations,
- large joins,
- large sorts,
- skew,
- too-large partitions.

### Diagnostic chain

```text
Spill
 +
Partition size
 +
Task time
 +
GC
 +
Executor memory
```

should be examined together.

---

## 16. Disk Spill

Disk spill generally introduces more expensive I/O than keeping working state in memory.

A useful conceptual model:

```text
Operator working set
       ↓
Memory capacity exceeded
       ↓
Intermediate state spilled
       ↓
Disk I/O
       ↓
Additional execution time
```

Disk spill can occur in otherwise valid Spark workloads. The question is whether the amount and associated runtime are acceptable.

### Do not jump to

> "Increase executor memory."

First ask:

- Is partitioning pathological?
- Is there skew?
- Is the aggregation too broad?
- Is the join producing too much intermediate state?
- Is there unnecessary caching?
- Is the input layout causing inefficient work?

---

## 17. Garbage Collection Time

GC is JVM garbage collection.

High executor GC can indicate significant object/memory-management pressure.

Distinguish:

### High GC

The JVM spends substantial time reclaiming memory.

### High compute time

Tasks spend time executing useful computation.

### High shuffle time

Tasks spend time moving/processing redistributed data.

These can overlap.

High GC alone does not prove that adding memory is the correct solution.

Investigate:

- object-heavy execution,
- cache pressure,
- large partitions,
- data representation,
- memory configuration,
- workload shape.

---

## 18. Storage Tab

The Storage tab helps diagnose persistence.

Look for:

- cached RDDs/DataFrames,
- storage level,
- memory usage,
- disk usage,
- partition count,
- cached data.

Connect this to Topic 10.

### Over-caching signature

Potential evidence:

```text
Large cached dataset
+
Executor memory pressure
+
GC
+
Evictions
+
Little actual reuse
```

This suggests caching may be contributing to the problem.

Caching is a performance tool, not a default requirement.

### Questions

- Is the cached dataset reused?
- Is the persisted representation appropriate?
- Is cache occupying memory needed by execution?
- Can the cache be removed?
- Was it unpersisted when no longer needed?

---

## 19. Environment Tab

The Environment tab is an evidence source.

Use it to verify what the application actually received.

Depending on Spark version/deployment, it can expose information about:

- Spark configuration,
- JVM/environment,
- classpath-related information,
- runtime settings.

### Important principle

> **Do not assume the configuration you intended to set is the configuration the application actually received.**

If someone says:

> "We set shuffle partitions to 400."

verify the actual application environment.

---

## 20. Executors Tab

The Executors tab helps investigate executor behavior.

Look for:

- driver,
- active executors,
- dead executors,
- task activity,
- memory,
- disk,
- GC,
- failures.

### Signs of executor imbalance

Possible evidence:

```text
Executor A: many long-running tasks
Executor B: mostly idle
Executor C: failed
```

Investigate whether this reflects:

- skew,
- scheduling,
- data locality,
- executor health,
- dynamic allocation,
- resource availability.

### Correlation path

```text
UI
 ↓
Executor
 ↓
Task
 ↓
Log
```

The UI tells you which executor/task deserves inspection; the log can reveal the actual exception.

---

## 21. SQL / DataFrame Tab

The SQL tab is a core debugging tool for both SQL and DataFrame workloads.

Mental model:

```text
DataFrame / SQL
      ↓
Catalyst
      ↓
Physical Plan
      ↓
SQL UI
      ↓
Runtime Metrics
```

Trace operators such as:

```text
FileScan
   ↓
Filter
   ↓
Exchange
   ↓
Join
   ↓
Aggregate
```

### Operator questions

For each operator ask:

- How much input did it process?
- How much output did it produce?
- Did it trigger data movement?
- How long did it run?
- Did it create an unexpectedly large result?
- Does its behavior match the physical plan?

---

## 22. SQL Runtime Metrics

The central question is:

> **Where did the time go?**

Relevant metrics can include:

- input rows,
- output rows,
- data size,
- duration,
- shuffle,
- partition information,
- version-dependent operator metrics.

### Example reasoning

Suppose a `Filter` receives a very large number of rows and emits nearly all of them.

That may suggest:

- the predicate is not selective,
- filtering happens later than expected,
- the input volume is larger than assumed.

Suppose an `Exchange` moves a very large amount of data.

Investigate:

- join,
- aggregation,
- repartition,
- partitioning,
- skew,
- AQE behavior.

The SQL tab provides evidence; it does not automatically explain the root cause.

---

## 23. Connecting UI Metrics to Physical Plans

This is one of the most important professional skills.

```text
Code
 ↓
Explain Plan
 ↓
Spark UI
 ↓
Runtime Metrics
 ↓
Root Cause
```

Illustrative plan:

```text
Exchange
   ↓
SortMergeJoin
```

Suppose the UI then shows:

- large shuffle,
- long stage,
- large task variance.

A reasonable hypothesis is:

> The join is expensive because substantial data is being redistributed and one or more partitions may be disproportionately expensive.

Now inspect:

- task distribution,
- shuffle distribution,
- join keys,
- input sizes,
- skew evidence,
- AQE behavior.

Do not conclude "the join is bad" from the operator name alone.

---

## 24. Driver Logs

Driver logs reveal driver-side behavior such as:

- application startup,
- configuration,
- planning,
- job failures,
- serialization failures,
- driver memory errors,
- exceptions.

### Practical search strategy

Search for:

```text
ERROR
Exception
OutOfMemoryError
Caused by:
Task failed
ExecutorLostFailure
FetchFailed
Serialization
PythonException
```

Use timestamps and job/stage/task identifiers to correlate log events with UI events.

### Driver-side failures

A driver failure can terminate the entire application even when executors are healthy.

---

## 25. Executor Logs

Executor logs are different because they expose executor/task-side failures.

Look for:

- task exceptions,
- executor OOM,
- Python worker errors,
- serialization problems,
- shuffle errors,
- JVM errors,
- evidence surrounding lost executors.

### Correlation example

```text
Failed Stage
   ↓
Failed Task
   ↓
Executor ID
   ↓
Executor Log
   ↓
Exception / Failure Cause
```

Do not treat "executor lost" as a root cause. It is a symptom that requires further evidence.

---

## 26. Spark Log Levels

Common logging levels are:

- `ERROR`
- `WARN`
- `INFO`
- `DEBUG`

### When to increase detail

Use higher detail temporarily when:

- reproducing a difficult failure,
- tracing a subsystem,
- investigating configuration,
- isolating an exception.

Avoid:

> "Set DEBUG everywhere in production forever."

Higher verbosity can create:

- log volume,
- operational noise,
- storage cost,
- additional overhead,
- harder incident review.

Use targeted, temporary diagnostic logging when possible.

---

## 27. Spark History Server

The History Server provides a way to inspect completed applications using retained event logs.

Conceptually:

```text
Running Application
      ↓
Event Logs
      ↓
History Server
      ↓
Past Application UI
```

This matters because production incidents are often discovered after an application has already finished.

### Why it matters

A team can use historical application evidence for:

- post-mortem analysis,
- regression investigation,
- failed-job analysis,
- before/after comparison,
- performance baselines.

Do not assume a fixed event-log directory or deployment environment. Those are platform and configuration dependent.

---

## 28. Event Logs

Event logs capture application execution events conceptually including:

- application lifecycle events,
- job events,
- stage events,
- task events,
- configuration-related information,
- execution history.

They allow the History Server to reconstruct useful application UI information after the application finishes.

Without retained event logs, a completed production failure may leave much less evidence for later analysis.

---

## 29. A Systematic Debugging Workflow

Use this exact core workflow.

### Step 1 — Confirm the symptom

Define:

- what is slow,
- how slow it is,
- when the regression started,
- what baseline is expected.

### Step 2 — Identify the slow job

Use the Jobs tab.

### Step 3 — Identify the slowest stage

Use the Stages tab.

### Step 4 — Inspect task distribution

Check min/median/max and long tails.

### Step 5 — Inspect shuffle

Check shuffle read/write and whether the amount is expected.

### Step 6 — Inspect spill

Look for memory and disk spill.

### Step 7 — Inspect GC

Determine whether GC is materially contributing.

### Step 8 — Inspect SQL operator metrics

Find operators doing unexpected amounts of work.

### Step 9 — Inspect logs

Use driver and executor logs for failure/root-cause evidence.

### Step 10 — Form a hypothesis

Write one testable explanation.

### Step 11 — Change ONE thing

Do not simultaneously alter:

- partition count,
- executor memory,
- join hints,
- cache behavior,
- UDF implementation,
- AQE settings.

Otherwise you lose causal clarity.

### Step 12 — Re-run

Use comparable input and environment.

### Step 13 — Measure

Compare runtime and relevant metrics.

### Step 14 — Validate correctness

Performance improvement is not success if output changed incorrectly.

### Step 15 — Document

Record evidence, change, result, and remaining risk.

---

## 30. Diagnosing Data Skew

Topic 09 already taught skew and salting. Here the objective is recognizing skew in evidence.

Illustrative example:

```text
Median task: 8 sec
Maximum task: 410 sec
```

Investigate:

1. task/partition distribution,
2. shuffle distribution,
3. join or aggregation,
4. hot keys if available,
5. executor logs,
6. partition sizes.

### Typical signature

```text
Most tasks: normal
One/few tasks: dramatically slower
```

This is evidence of a long tail.

It is not automatic proof of skew.

A slow task could also reflect:

- a slow node,
- GC,
- I/O,
- resource contention,
- unusual partition contents.

---

## 31. Diagnosing Spill

Potential signature:

- significant memory spill,
- significant disk spill,
- long task times,
- memory pressure,
- large partitions.

Possible causes:

- large aggregation,
- large sort,
- large join,
- skew,
- too-large partitions,
- insufficient resources,
- poor query design.

### Diagnostic sequence

```text
Spill
 ↓
Which operator?
 ↓
Which stage?
 ↓
Which partitions?
 ↓
Is skew present?
 ↓
Is partition size appropriate?
 ↓
Is the operation producing excessive intermediate state?
```

"Add more memory" is not the first diagnostic step.

---

## 32. Diagnosing Too Many Tasks

Signs can include:

- very high task count,
- very small task durations,
- substantial scheduling overhead,
- many tiny input files,
- excessive shuffle partitions.

Investigate:

- file layout,
- input partitioning,
- `spark.sql.shuffle.partitions`,
- AQE behavior,
- whether the workload is too small for the chosen parallelism.

Too many tasks can make a small workload slower because scheduling and task startup overhead becomes significant.

---

## 33. Diagnosing Too Few Tasks

Signs can include:

- low parallelism,
- few tasks,
- long task durations,
- underutilized executors,
- large partitions.

Possible causes:

- too few partitions,
- `coalesce()` used too aggressively,
- poor input partitioning,
- data layout.

Connect this to Topic 08.

The correct response is not automatically "increase partitions." First establish whether the existing tasks are large enough to justify additional parallelism.

---

## 34. Diagnosing Large Shuffles

Potential signature:

```text
High shuffle read/write
+
Long network-heavy stage
+
Expensive join/aggregation
```

Investigate:

- join strategy,
- partitioning,
- data volume,
- skew,
- AQE,
- broadcast opportunity,
- unnecessary repartitioning.

### Example

If a join has:

```text
Large left input
Large right input
Exchange
SortMergeJoin
Large shuffle
```

you may investigate whether:

- one side is actually small enough to broadcast safely,
- filters can reduce inputs before the join,
- the join keys are skewed,
- partitioning can be improved.

Do not apply a broadcast blindly. A large broadcast can create memory pressure and failures.

---

## 35. Diagnosing UDF Bottlenecks

Topic 11 covered UDF trade-offs. Here, diagnose them.

Python UDFs can introduce expensive Python execution and reduce the optimizer's visibility into the computation.

Potential evidence:

- Python execution operators,
- increased execution time,
- high CPU,
- less optimization opportunity.

### Debugging workflow

1. Identify the Python UDF.
2. Measure the affected workload.
3. Replace it with a built-in expression where possible.
4. Re-run comparable input.
5. Compare runtime and relevant metrics.
6. Validate output equivalence.

The UI alone does not prove the UDF is the only cause.

---

## 36. Diagnosing Over-Caching

Potential evidence:

- large Storage tab usage,
- executor memory pressure,
- elevated GC,
- eviction/recomputation,
- cached datasets with little reuse.

Ask:

```text
Is this dataset reused?
        ↓
Yes → Is the storage level appropriate?
No  → Why is it cached?
```

Cache should be justified by a workload pattern, not habit.

---

## 37. Driver OutOfMemoryError

A driver OOM commonly looks like:

```text
java.lang.OutOfMemoryError
```

Potential causes include:

- `collect()`,
- `toPandas()`,
- huge driver-side objects,
- huge broadcast variables,
- excessive metadata,
- driver-side loops.

### Unsafe pattern

```python
rows = df.collect()
```

`collect()` transfers all rows to the driver.

### Safer patterns, with limits

```python
df.limit(100).collect()
```

```python
df.take(100)
```

```python
df.sample(False, 0.001).limit(1000).collect()
```

Other safer designs include:

- aggregate before collecting,
- write results from executors,
- inspect bounded samples.

None of these is automatically safe for arbitrary sizes.

### Driver OOM diagnosis

Use:

```text
Driver log
+
Application failure
+
Code path
+
Data volume
```

Do not "add executors" to solve a driver-memory problem. Executors do not increase driver heap.

---

## 38. Huge Broadcast Risks

Broadcast joins can avoid a large shuffle when a suitable relation is small enough.

But a broadcast is not free.

Potential risks:

- large executor memory consumption,
- serialization/deserialization overhead,
- executor OOM,
- network distribution cost,
- unstable execution if the broadcast grows unexpectedly.

### Diagnostic rule

If broadcast is suspected:

- inspect the physical plan,
- inspect input size,
- inspect executor memory,
- inspect task/runtime behavior,
- verify the broadcast relation is actually appropriate.

A broadcast hint communicates intent; it does not magically make an oversized relation safe.

---

## 39. Executor OutOfMemoryError

Potential causes:

- huge partitions,
- data skew,
- large joins,
- large aggregations,
- cache pressure,
- excessive object creation,
- Python worker memory.

Use multiple evidence sources:

```text
UI
+
Executor Log
+
Task Distribution
+
Partition Size
```

### Example reasoning

If one task has:

- dramatically larger duration,
- large spill,
- high GC,
- and an executor OOM,

investigate partition size and skew before changing global memory settings.

---

## 40. Memory Overhead and Python Workers

A PySpark executor is not just JVM heap.

Conceptually distinguish:

```text
Executor JVM Heap
        +
Memory Overhead / Non-Heap Resources
        +
Python Worker Processes
        +
Native / Off-Heap Usage
        =
Container Memory Demand
```

A job can therefore fail even when the JVM heap does not look completely full.

Potential contributors:

- Python worker processes,
- native libraries,
- off-heap memory,
- container limits,
- executor overhead allocation.

Exact behavior depends on Spark version and cluster manager.

Do not memorize universal memory values. Verify the actual deployment's memory model and limits.

---

## 41. Shuffle Fetch Failures

A downstream task may need shuffle data produced by an upstream stage.

A shuffle fetch failure means the downstream task could not retrieve required shuffle data.

Potential causes:

- lost executor,
- network problem,
- missing/corrupted shuffle data,
- executor failure,
- resource pressure,
- infrastructure instability.

### Investigation

1. Identify the failed stage.
2. Identify failed task(s).
3. Inspect executor logs.
4. Inspect shuffle metrics.
5. Check lost-executor events.
6. Check cluster/infrastructure evidence.

Do not conclude:

> "Fetch failed = network problem."

The failure may be downstream evidence of an earlier executor failure.

---

## 42. Lost Executors

"Executor lost" means Spark lost an executor process/resource.

Possible causes include:

- OOM,
- container kill,
- node failure,
- network issue,
- external infrastructure problem.

It is a **symptom**, not a complete diagnosis.

Ask:

```text
Why was it lost?
 ↓
OOM?
Container?
Node?
Network?
Application error?
Infrastructure?
```

Use the executor log and platform-level diagnostics where available.

---

## 43. Serialization Errors

Serialization is required when data or functions cross process boundaries.

Common PySpark problems include:

- non-serializable objects in closures,
- driver-only objects captured by worker code,
- large captured variables,
- Python serialization failures.

### Bad design concept

```python
connection = create_driver_only_connection()

def transform(row):
    # Captures a driver-only connection.
    return connection.do_something(row)
```

The worker may need to serialize the function and its closure.

A better design separates worker-safe computation from driver-only resources.

### Rule

Do not capture unnecessary objects in functions sent to executors.

---

## 44. Long GC Pauses

High GC can create:

- slow tasks,
- long executor pauses,
- reduced throughput,
- apparent stragglers.

Investigate:

- object creation,
- cache pressure,
- large partitions,
- memory configuration,
- representation of intermediate data.

Do not simply increase memory.

More memory can help some workloads and worsen others by changing object lifetime, cache behavior, or resource utilization.

---

## 45. Stragglers

A **straggler** is a task that takes substantially longer than most peer tasks.

Potential causes:

- skew,
- slow node,
- GC,
- I/O,
- resource contention,
- unusually large partition.

### Differentiating causes

| Evidence | Possible explanation |
|---|---|
| Slow task also processes much more data | Skew/large partition |
| Slow task has high GC | Memory pressure |
| Slow task is on one unhealthy executor | Node/executor issue |
| Slow task shows external I/O delay | I/O bottleneck |
| Similar data sizes but one executor consistently slow | Resource/infrastructure issue |

Use multiple signals.

---

## 46. Speculative Execution

Speculative execution can launch another attempt for a task that appears unusually slow compared with peers.

Conceptually:

```text
Normal task attempt
       ↓
Detected as unusually slow
       ↓
Backup attempt
       ↓
First successful result wins
```

It can help when the root cause is a slow node or transient executor problem.

It cannot reliably solve data skew.

If the task is slow because it has dramatically more data, running the same work again elsewhere does not remove the excess work.

### Trade-off

Speculation consumes additional resources.

Therefore:

> Speculation is a mitigation for certain stragglers, not a substitute for fixing pathological partitioning.

---

## 47. Programmatic Spark Metrics

Manual UI inspection does not scale to hundreds of production jobs.

A platform team may need to collect:

- runtime,
- stage metrics,
- task distribution,
- shuffle,
- spill,
- failures,
- resource usage.

Possible mechanisms include:

- Spark REST API,
- Spark listeners,
- Spark metrics systems/libraries,
- event-log processing.

This topic introduces the architecture rather than becoming a complete observability course.

A useful conceptual pipeline is:

```text
Spark Application
      ↓
Spark UI / Event Stream / REST
      ↓
Metrics
      ↓
Monitoring System
      ↓
Dashboard / Regression Detection
```

This connects forward to Module 2.20, where observability, lineage, governance, and security are treated more deeply.

---

## 48. Spark Listeners and REST API

### Spark listeners

A Spark listener consumes Spark application events.

A data platform team can use listener-based approaches for:

- job lifecycle events,
- stage lifecycle,
- task events,
- automated metrics collection,
- custom performance analysis.

Implementation details are deployment/version dependent.

### REST API

Spark exposes programmatic application information through interfaces associated with the Spark UI/history ecosystem.

Potential uses include:

- application metadata,
- job metadata,
- stage metrics,
- automated monitoring,
- regression analysis.

Do not hard-code REST endpoints from memory. Exact endpoints and availability can vary by Spark version and environment. Verify them against the installed version.

### Version check

```python
print(spark.version)
```

---

## 49. Performance Regression Tracking

A job that was fast last week can become slow this week.

Possible reasons:

- data growth,
- distribution changes,
- schema changes,
- code changes,
- Spark upgrade,
- configuration changes,
- infrastructure changes.

Track at least:

- runtime,
- input volume,
- shuffle,
- spill,
- task distribution,
- failure rate,
- resource utilization.

### Baseline thinking

A baseline should answer:

> "What does normal look like for this workload?"

A useful baseline is contextualized by:

- input size,
- date/window,
- schema,
- code version,
- Spark version,
- relevant configuration,
- cluster shape.

Runtime alone is not enough.

---

## 50. Deliberately Slow Spark Jobs

The best way to learn debugging is to create controlled failures.

**Important:** actual metrics are environment-dependent. The examples below are deliberately illustrative. Run them only on synthetic/safe datasets.

### Slow Job 1 — Skewed Join

#### Setup

Create a hot key on one side:

```python
from pyspark.sql import functions as F

left = (
    spark.range(0, 2_000_000)
    .withColumn(
        "key",
        F.when(F.col("id") < 1_800_000, F.lit(1))
         .otherwise(F.col("id"))
    )
)

right = (
    spark.range(0, 100_000)
    .withColumn("key", F.col("id") + 1)
)

bad = left.join(right, "key")
bad.count()
```

#### Expected symptom

Potential long-tail task distribution.

#### Investigation task

Use:

- Stages tab,
- task min/median/max,
- shuffle metrics,
- SQL tab,
- physical plan.

#### Root cause

Potentially concentrated work around a hot join key.

#### Fix

Investigate filtering, pre-aggregation, broadcast suitability, or skew-aware techniques from Topic 09.

#### Re-run

Compare task distribution and shuffle behavior.

---

### Slow Job 2 — UDF-Heavy Filter

```python
from pyspark.sql import functions as F
from pyspark.sql.types import BooleanType
import time

@F.udf(returnType=BooleanType())
def expensive_predicate(x):
    if x is None:
        return False
    total = 0
    for i in range(500):
        total += (x * i) % 97
    return total % 2 == 0

df = spark.range(0, 500_000)

bad = df.filter(expensive_predicate("id"))
bad.count()
```

#### Investigate

- SQL tab,
- Python execution operators,
- stage duration,
- CPU behavior.

#### Fix

Replace with a built-in expression when semantically possible.

---

### Slow Job 3 — `coalesce(1)` Upstream

```python
df = spark.range(0, 5_000_000)

bad = (
    df.repartition(100)
      .coalesce(1)
      .filter("id % 2 = 0")
)

bad.count()
```

Investigate task count and parallelism.

The point is not that `coalesce(1)` is always wrong; it is that forcing one partition can create a serial bottleneck when used upstream of substantial work.

---

### Slow Job 4 — 2,000 Shuffle Partitions on Tiny Data

```python
small = spark.range(0, 10_000)

bad = (
    small.repartition(2_000)
         .groupBy((F.col("id") % 10).alias("bucket"))
         .count()
)

bad.count()
```

Investigate:

- number of tasks,
- task duration,
- scheduling overhead,
- AQE behavior.

Do not assume a specific runtime.

---

### Slow Job 5 — Unnecessary Cache

```python
df = spark.range(0, 2_000_000)

unused = df.withColumn("x", F.col("id") * 2).cache()

# The dataset is not reused meaningfully.
result = df.filter("id < 10_000").count()
print(result)
```

Investigate the Storage tab and executor memory behavior.

The exact evidence depends on whether and when the cached DataFrame is materialized.

---

### Slow Job 6 — Large Driver `collect()`

Use a bounded synthetic dataset and do not intentionally exhaust a production driver:

```python
df = spark.range(0, 1_000_000)

rows = df.collect()
print(len(rows))
```

Investigate:

- driver memory,
- driver logs,
- application behavior.

For a real OOM experiment, scale gradually in an isolated environment.

---

### Slow Job 7 — Large Shuffle

```python
left = spark.range(0, 2_000_000).withColumn("k", F.col("id") % 500_000)
right = spark.range(0, 2_000_000).withColumn("k", F.col("id") % 500_000)

result = left.join(right, "k")
result.count()
```

Investigate:

- `Exchange`,
- shuffle read/write,
- join strategy,
- task distribution.

---

### Slow Job 8 — Memory-Heavy Aggregation

```python
df = (
    spark.range(0, 5_000_000)
    .withColumn("group_key", F.col("id") % 2_000_000)
)

result = df.groupBy("group_key").count()
result.count()
```

Use an isolated environment and observe:

- stage metrics,
- spill,
- GC,
- partition behavior.

The actual amount of spill depends on the Spark version, environment, and resources.

---

## 51. Hands-On Debugging Labs

The following labs are designed for `experiments/debugging/`. The specification requires that directory but does not require this Markdown task to modify it.

### Lab 1 — Navigate the Jobs Tab

**Objective:** identify the slowest completed/active job.

**Setup:** run several DataFrame actions.

**Code:**

```python
df = spark.range(0, 1_000_000)

df.count()
df.groupBy((F.col("id") % 10).alias("bucket")).count().show()
```

**Inspect:** Jobs tab.

**Expected evidence:** multiple jobs with different descriptions/durations.

**Questions:**
- Which action produced each job?
- Which job is longest?

**Diagnosis:** establish the actual slow job before changing code.

**Validation:** repeat with comparable input.

**Production lesson:** application duration alone is insufficient.

---

### Lab 2 — Navigate the Stages Tab

**Objective:** identify the longest stage.

**Inspect:**
- stage duration,
- task count,
- shuffle,
- input/output.

**Production lesson:** stage-level evidence narrows the investigation.

---

### Lab 3 — Task Min/Median/Max

**Objective:** detect a long tail.

Use the skewed join example.

**Inspect:**
- min,
- median,
- max.

**Question:** Is one task dramatically slower?

**Production lesson:** task distribution is often more informative than average runtime.

---

### Lab 4 — Diagnose a Skewed Join

Run the deliberately skewed join.

**Inspect:**
- SQL plan,
- Exchange,
- join operator,
- task distribution,
- shuffle.

**Diagnosis:** form a skew hypothesis.

**Fix:** use a justified strategy from Topic 09.

**Validation:** compare distribution and correctness.

---

### Lab 5 — Diagnose Spill

Create a memory-heavy aggregation in an isolated environment.

**Inspect:**
- memory spill,
- disk spill,
- GC,
- task duration.

**Question:** Which operator is producing the working set?

**Production lesson:** identify the workload shape before increasing memory.

---

### Lab 6 — Too Many Tasks

Run the small-data/2,000-partition example.

**Inspect:**
- task count,
- task duration,
- scheduling behavior.

**Production lesson:** parallelism has overhead.

---

### Lab 7 — Too Few Tasks

Run the `coalesce(1)` example.

**Inspect:**
- number of tasks,
- executor utilization,
- task duration.

**Production lesson:** reducing partitions can reduce parallelism.

---

### Lab 8 — Large Shuffle

Run the join with many keys.

**Inspect:**
- Exchange,
- shuffle read/write,
- stage duration,
- task distribution.

**Production lesson:** large shuffle is evidence to investigate, not proof of a defect.

---

### Lab 9 — UDF Bottleneck

Run the UDF example.

**Inspect:**
- SQL tab,
- Python execution,
- task duration.

**Fix:** replace with built-ins if equivalent.

**Validation:** compare output and metrics.

---

### Lab 10 — Unnecessary Cache

Cache a dataset that is not reused.

**Inspect:**
- Storage tab,
- memory,
- GC,
- eviction behavior.

**Production lesson:** cache only when reuse justifies the resource cost.

---

### Lab 11 — Driver OOM Investigation

Use a gradually scaled synthetic `collect()` experiment.

**Inspect:**
- driver log,
- driver memory,
- application failure.

**Safety:** never perform uncontrolled OOM experiments in production.

---

### Lab 12 — Executor OOM Investigation

Use synthetic skew/large-partition data in a small isolated cluster.

**Inspect:**
- failed task,
- executor log,
- stage,
- memory metrics.

**Production lesson:** executor OOM often requires partition/workload investigation.

---

### Lab 13 — Shuffle Fetch Failure Investigation

Use a controlled environment capable of reproducing executor loss or shuffle-data unavailability.

**Inspect:**
- failed stage,
- failed task,
- executor logs,
- lost-executor evidence.

**Production lesson:** a fetch failure can be downstream evidence of an earlier executor failure.

---

### Lab 14 — History Server

Enable event logging according to the installed Spark environment.

**Inspect:**
- completed application,
- jobs,
- stages,
- SQL,
- executor information where retained.

**Production lesson:** event logs turn transient runtime evidence into historical evidence.

---

### Lab 15 — Event Log Analysis

Inspect a completed application's retained event history.

**Objective:** identify:
- slow stage,
- task distribution,
- shuffle,
- failures.

**Production lesson:** historical analysis enables post-mortems.

---

### Lab 16 — Performance Investigation Report

Use a deliberately slow job.

Produce:

- symptom,
- baseline,
- evidence,
- root-cause hypothesis,
- one change,
- before/after,
- correctness validation.

---

### Lab 17 — Before/After Optimization

Run a workload, record baseline, make one evidence-based change, and repeat.

Use:

| Metric | Baseline | Change | After | Interpretation |
|---|---:|---|---:|---|
| Runtime | | | | |
| Input | | | | |
| Shuffle Read | | | | |
| Shuffle Write | | | | |
| Spill Memory | | | | |
| Spill Disk | | | | |
| GC Time | | | | |
| Task Median | | | | |
| Task Max | | | | |
| Executor Failures | | | | |

Do not fabricate the numbers.

---

### Lab 18 — Programmatic Metrics

At awareness level, investigate how the Spark UI/history ecosystem can expose application and stage information programmatically.

Tasks:

- identify the installed Spark version,
- identify the environment's available interface,
- collect a small set of application/stage metadata,
- store it for comparison.

Do not assume a fixed REST endpoint across versions.

---

### Lab 19 — Team Debugging Checklist

Turn the production checklist in this chapter into a team runbook.

Include:

- symptom,
- baseline,
- slow job,
- slow stage,
- task distribution,
- shuffle,
- spill,
- GC,
- SQL,
- logs,
- hypothesis,
- change,
- measurement,
- correctness,
- documentation.

---

## 52. Debugging Exercises

Work through these without looking at the diagnosis first.

### Basic

#### Exercise 1

**Scenario:** one job is 3× longer than the others.

**UI evidence:** Jobs tab shows a single unusually long completed job.

**Task:** identify the next two UI locations you should inspect.

**Possibilities:** Stages, SQL.

**Diagnosis:** drill into the job's stages and identify the slowest stage.

**Fix:** none yet; diagnosis precedes tuning.

**Validation:** establish baseline metrics.

---

#### Exercise 2

**Scenario:** a stage has tasks between 4 and 7 seconds.

**Task:** decide whether this alone indicates skew.

**Diagnosis:** no. The distribution is relatively compact; inspect other evidence.

---

#### Exercise 3

**Scenario:** task median is 10 seconds and max is 150 seconds.

**Task:** list at least four possible causes.

**Diagnosis:** skew, large partition, slow executor/node, GC, I/O, or resource contention.

---

#### Exercise 4

**Scenario:** a stage has high shuffle read.

**Task:** explain why high shuffle is not sufficient to declare the job bad.

**Diagnosis:** compare shuffle to input size, operation, expected data movement, partitioning, and runtime.

---

### Moderate

#### Exercise 5

**Scenario:** large disk spill accompanies long aggregation tasks.

**Task:** investigate before changing memory.

**Diagnosis:** inspect aggregation shape, partition sizes, skew, cache pressure, and executor memory.

---

#### Exercise 6

**Scenario:** 2,000 tiny tasks execute against a small dataset.

**Task:** identify likely overhead.

**Diagnosis:** task scheduling and management overhead may dominate useful computation.

---

#### Exercise 7

**Scenario:** `coalesce(1)` is immediately before an expensive transformation.

**Task:** explain the risk.

**Diagnosis:** downstream work may be constrained to a single partition.

---

#### Exercise 8

**Scenario:** Storage tab contains a large cached dataset and executors show high GC.

**Task:** formulate a hypothesis.

**Diagnosis:** cache may be consuming memory needed for execution; verify reuse before removing it.

---

### Hard

#### Exercise 9

**Scenario:** a join has one task 30× slower than the median. Shuffle is also high.

**Task:** identify evidence needed to distinguish skew from a slow node.

**Correct diagnosis path:** compare partition/data sizes, executor identity, GC, logs, and task attempts.

---

#### Exercise 10

**Scenario:** executor disappears and downstream tasks report fetch failures.

**Task:** determine whether the fetch failure is necessarily the root cause.

**Diagnosis:** no. The lost executor may have caused the missing shuffle data.

---

#### Exercise 11

**Scenario:** JVM heap appears healthy but the container is killed.

**Task:** identify the missing resource dimension.

**Diagnosis:** investigate memory overhead, Python workers, native/off-heap usage, and container limits.

---

#### Exercise 12

**Scenario:** a Python UDF appears in the SQL execution path and runtime increased after deployment.

**Task:** design a controlled comparison.

**Diagnosis:** replace with a semantically equivalent built-in if possible and compare metrics.

---

### Advanced

#### Exercise 13

**Scenario:** AQE is enabled, but one stage still has an extreme long tail.

**Task:** explain why AQE being enabled does not eliminate the need for diagnosis.

**Diagnosis:** AQE can adapt some runtime decisions, but it does not make every skew, partition, UDF, I/O, or infrastructure problem disappear.

---

#### Exercise 14

**Scenario:** runtime increased 70% after a Spark upgrade.

**Task:** design a regression investigation.

**Correct path:**
- establish baseline,
- compare workload,
- compare plan,
- compare configuration,
- inspect SQL/runtime metrics,
- isolate version-related behavior,
- validate with controlled runs.

---

#### Exercise 15

**Scenario:** hundreds of jobs need centralized performance monitoring.

**Task:** design a lightweight metrics architecture.

**Diagnosis:** UI-only inspection does not scale; use event/log/API/listener-based collection and a monitoring store/dashboard.

---

## 53. Production Failure Scenarios

### Scenario 1 — One Task Takes 20× Longer

**Symptom:** most tasks complete normally; one task dominates stage duration.

**Evidence:** high max/median ratio.

**UI investigation:** task distribution, shuffle, input size.

**Log investigation:** executor hosting the slow task.

**Root-cause candidates:** skew, large partition, GC, slow executor.

**Hypothesis:** concentrated partition data.

**Fix:** investigate and apply an appropriate partition/skew strategy.

**Validation:** task distribution becomes less pathological without changing correctness.

**Preventive action:** monitor task-tail metrics.

---

### Scenario 2 — Huge Shuffle Stage

**Symptom:** shuffle-heavy stage dominates runtime.

**Evidence:** high shuffle read/write and long duration.

**UI:** inspect Exchange/join/aggregation.

**Logs:** investigate failures if present.

**Candidates:** expected large join, unnecessary repartition, skew, poor filtering.

**Validation:** compare shuffle and runtime after one targeted change.

---

### Scenario 3 — Large Disk Spill

**Symptom:** large disk spill and long tasks.

**Evidence:** spill + task duration + memory pressure.

**Candidates:** aggregation, sort, join, skew, large partitions.

**Fix:** address the workload/partition issue before indiscriminate memory increases.

---

### Scenario 4 — High Executor GC

**Symptom:** high GC time.

**Evidence:** executor metrics and logs.

**Candidates:** cache pressure, object-heavy workload, large partitions, memory pressure.

**Validation:** confirm GC and runtime change together.

---

### Scenario 5 — Driver OOM

**Symptom:** driver crashes.

**Evidence:** driver log contains OOM; code contains `collect()` or large driver-side operation.

**Root cause candidate:** driver-side materialization.

**Fix:** aggregate, sample, limit, or write distributed results instead.

---

### Scenario 6 — Executor OOM

**Symptom:** task/executor failure.

**Evidence:** executor log + task distribution.

**Candidates:** skew, huge partition, large join, aggregation, cache, Python worker.

**Fix:** address the evidence-supported cause.

---

### Scenario 7 — Python Worker/Container Memory Kill

**Symptom:** container killed despite apparently non-exhausted JVM heap.

**Evidence:** executor/container logs.

**Candidates:** Python worker, native memory, overhead, off-heap.

**Validation:** monitor container memory and worker behavior.

---

### Scenario 8 — Shuffle Fetch Failure

**Symptom:** downstream task cannot fetch shuffle data.

**Evidence:** failed stage and executor history.

**Candidates:** lost executor, missing shuffle data, network/resource problem.

**Fix:** determine upstream failure before changing shuffle configuration.

---

### Scenario 9 — Lost Executors

**Symptom:** executors disappear.

**Evidence:** Executors tab + executor logs.

**Candidates:** OOM, container kill, node/network failure.

**Validation:** reproduce or correlate with infrastructure evidence.

---

### Scenario 10 — Serialization Failure

**Symptom:** task fails while executing Python function.

**Evidence:** executor log identifies serialization error.

**Candidates:** non-serializable closure/object.

**Fix:** remove driver-only state from worker closure.

---

### Scenario 11 — Thousands of Tiny Tasks

**Symptom:** very high task count with tiny task durations.

**Candidates:** tiny files, excessive shuffle partitions.

**Investigation:** file layout + shuffle configuration + AQE.

**Fix:** change the specific source of excessive parallelism.

---

### Scenario 12 — Regression After Data Growth

**Symptom:** previously fast job slows after input doubles.

**Evidence:** input volume and runtime increased.

**Candidates:** changed distribution, partition sizing, skew, join behavior.

**Validation:** compare metrics normalized by input volume.

---

### Scenario 13 — AQE Enabled but Still Slow

**Symptom:** AQE is ON but job remains slow.

**Candidates:** skew, UDF, I/O, driver work, bad source layout, unavoidable data movement, resource limits.

**Fix:** diagnose actual evidence rather than disabling AQE or changing unrelated settings.

---

### Scenario 14 — Cache Causes Pressure

**Symptom:** Storage usage and GC increase.

**Candidates:** unnecessary cache or inappropriate persistence level.

**Fix:** remove or change persistence only after verifying reuse.

---

### Scenario 15 — UDF Regression

**Symptom:** deployment introduces Python UDF and runtime increases.

**Investigation:** compare plan/operator metrics and output correctness.

**Fix:** replace with built-in expression where possible.

---

## 54. Common Misconceptions

1. **"The longest job is always the root cause."**  
   The longest job is the symptom to investigate.

2. **"The slowest stage is always the root cause."**  
   It is usually a good starting point, not proof of causality.

3. **"High shuffle automatically means a bad job."**  
   Large workloads can legitimately require large data movement.

4. **"Any spill means the job is broken."**  
   Spill can occur in valid workloads; its magnitude and performance impact matter.

5. **"High GC automatically means more memory is required."**  
   GC is evidence of memory-management pressure, not a universal prescription.

6. **"More executors always make a job faster."**  
   Parallelism can be limited by partitions, skew, I/O, serialization, or coordination overhead.

7. **"More partitions always make a job faster."**  
   Excessive partitions can add scheduling overhead.

8. **"One slow task always means skew."**  
   Slow nodes, I/O, GC, and contention can produce stragglers.

9. **"Executor lost means Spark is broken."**  
   Executor loss can originate from application, resource, node, or infrastructure causes.

10. **"Shuffle fetch failure always means a network problem."**  
    It can result from lost executors or unavailable shuffle data.

11. **"Driver OOM means the cluster needs more executors."**  
    Executors do not increase driver heap.

12. **"`collect()` is safe for moderate-looking DataFrames."**  
    Driver memory depends on actual serialized data and overhead.

13. **"AQE automatically fixes everything."**  
    AQE adapts selected runtime decisions; it does not eliminate all bottlenecks.

14. **"The SQL tab is only for SQL queries."**  
    DataFrame operations can appear there as SQL/DataFrame executions.

15. **"The Jobs tab tells you exactly why the job is slow."**  
    It identifies jobs; deeper diagnosis requires stages, tasks, SQL, and logs.

16. **"The Spark UI is enough without logs."**  
    Many failures require executor/driver logs.

17. **"History Server is only useful for failed jobs."**  
    Historical performance analysis is also valuable for successful jobs.

18. **"Event logs are unnecessary."**  
    They preserve evidence for completed applications.

19. **"Speculation fixes skew."**  
    Duplicate execution does not remove extra data processed by a skewed partition.

20. **"Caching always improves performance."**  
    Cache consumes resources and can cause pressure.

21. **"UDFs are always slower."**  
    They often have overhead, but diagnosis should be measurement-based.

22. **"High CPU always means CPU is the bottleneck."**  
    High CPU can coexist with other bottlenecks.

23. **"High memory always means memory is the bottleneck."**  
    High memory usage may be normal for the workload.

24. **"A large shuffle is always avoidable."**  
    Some distributed operations inherently require redistribution.

25. **"One metric is enough to diagnose Spark performance."**  
    Root-cause analysis requires correlated evidence.

26. **"Increasing configuration values is debugging."**  
    Configuration changes are experiments only when tied to a hypothesis and measured.

27. **"A broadcast hint guarantees a safe broadcast."**  
    Broadcast size and executor memory still matter.

28. **"A slow executor proves the node is unhealthy."**  
    The task may simply have more work.

---

## 55. Practice Questions

Exactly **40** scenario-based practice questions follow.

### Basic — 1–10

1. A Spark application has five completed jobs. How would you identify which job to investigate first?
2. A job contains four stages. Which UI evidence would you use to identify the slowest stage?
3. A stage reports minimum task time of 2 seconds, median of 4 seconds, and maximum of 90 seconds. What should you investigate next?
4. A stage has high shuffle read. What additional evidence would you inspect before deciding whether the shuffle is problematic?
5. A stage has disk spill. Does this alone prove the job is incorrectly configured? Explain.
6. What is the purpose of the Storage tab during a performance investigation?
7. What is the purpose of the Environment tab when validating configuration?
8. How would you distinguish information found in driver logs from information found in executor logs?
9. Why can the History Server be useful after an application has already completed?
10. What does `spark.version` tell you during a version-sensitive UI investigation?

### Moderate — 11–20

11. A stage has a median task duration of 8 seconds and maximum of 410 seconds. Design the next five diagnostic steps.
12. A workload has high shuffle write and high shuffle read. Explain how you would determine whether the shuffle is expected.
13. A stage has large disk spill and long task durations. What evidence would help distinguish skew from a generally undersized execution environment?
14. A workload has 2,000 tiny tasks over a small input. What symptoms would indicate scheduling overhead?
15. A workload has only one task after `coalesce(1)`. When could that be a problem?
16. The SQL tab shows an `Exchange` followed by a `SortMergeJoin`. What runtime evidence would you inspect to understand its cost?
17. A Python UDF appears in a slow query. How would you test whether replacing it with a built-in expression improves performance?
18. The Storage tab shows a large cache while executors show high GC. How would you investigate whether caching is causal?
19. A downstream stage reports a shuffle fetch failure after an executor disappeared. Explain the likely investigation path.
20. A completed production application must be analyzed two hours after it finished. What evidence sources should be available?

### Hard — 21–30

21. One task is 30× slower than its peers, but its executor shows no obvious failure. Design an investigation that distinguishes skew from a slow node.
22. A join produces a large shuffle and one task has a very large input partition. What evidence would support a skew hypothesis?
23. A stage spills heavily even though task durations are relatively balanced. What possible explanations should be considered?
24. A job becomes slower after input volume doubles. How would you determine whether the regression is simply proportional to workload growth or caused by changed data distribution?
25. A driver OOM occurs after a code change that added `collect()`. What evidence would you record before redesigning the operation?
26. JVM heap looks acceptable, but the container is killed. What additional memory dimensions would you investigate in PySpark?
27. AQE is enabled, but a workload still has a large long tail. What possibilities remain?
28. A performance change reduces runtime but increases executor failures. How should the change be evaluated?
29. A Spark upgrade changes the SQL physical plan. How would you structure a controlled regression investigation?
30. A production team wants automated detection of slow stages across hundreds of applications. What data should be collected and what architecture would you use?

### Advanced — 31–40

31. Design an evidence-based investigation for a job that normally takes 20 minutes but occasionally takes 2 hours.
32. A daily pipeline starts failing with executor OOM after data volume doubles. Develop a hypothesis tree using UI, task, SQL, and log evidence.
33. A skewed join has one task 25× slower than the median. Explain how you would determine whether salting, broadcast, pre-aggregation, or partition changes are justified.
34. A stage has high GC, high disk spill, and a large cache. Design an experiment that changes only one causal factor at a time.
35. A shuffle fetch failure occurs intermittently on a large production job. Explain how you would distinguish application-level causes from infrastructure instability.
36. A UDF deployment causes a runtime regression. Design a before/after experiment that proves or disproves the UDF as the primary contributor.
37. Build a performance regression baseline that remains meaningful when daily input volume changes.
38. Design a metrics pipeline that detects stage-level performance regressions without relying on manual UI inspection.
39. Write the evidence you would require before recommending a global change to executor memory for a production workload.
40. Design a complete performance investigation from symptom through root-cause hypothesis, one change, measurement, correctness validation, and final report.

---

## 56. Interview Questions

Exactly **40** interview questions follow.

### Basic — 1–10

1. What is the Spark UI and why is it important for production debugging?
2. What is the difference between the Jobs and Stages tabs?
3. What do minimum, median, and maximum task times tell you?
4. What is shuffle read?
5. What is shuffle write?
6. What is spill?
7. What is the purpose of the Executors tab?
8. What is the difference between driver and executor logs?
9. What is the Spark History Server?
10. Why are Spark event logs important?

### Moderate — 11–20

11. How would you debug a slow Spark job?
12. What does a very high maximum task time relative to the median indicate?
13. How do you identify skew from Spark UI evidence?
14. What does high spill indicate?
15. How do you distinguish a driver OOM from an executor OOM?
16. How do you use the SQL tab during performance debugging?
17. How would you investigate an expensive `Exchange`?
18. How would you diagnose over-caching?
19. How would you investigate a shuffle fetch failure?
20. How does the History Server help with production incidents?

### Hard — 21–30

21. One task takes 20× longer than all others. What would you investigate before declaring skew?
22. What evidence would distinguish a slow executor from a large partition?
23. Why can high GC time slow a Spark job?
24. Why is "increase executor memory" not an adequate first response to spill?
25. What are common causes of Python-worker memory pressure?
26. Why can a shuffle fetch failure be a consequence rather than the original failure?
27. When can speculative execution help, and when can it fail to solve the problem?
28. How would you investigate a performance regression after a Spark upgrade?
29. How do you connect an `explain("formatted")` plan to Spark UI runtime evidence?
30. How would you investigate a job that is slow despite AQE being enabled?

### Advanced — 31–40

31. Design a complete evidence-based workflow for a production Spark performance incident.
32. How would you distinguish skew, GC, I/O, and infrastructure failure when all appear as stragglers?
33. A workload has high shuffle, high spill, and low executor utilization. What hypotheses would you prioritize and why?
34. How would you prove that a Python UDF is materially contributing to a production regression?
35. How would you diagnose a container memory kill when JVM heap metrics look normal?
36. How would you automate performance regression detection for hundreds of Spark jobs?
37. What should a production Spark performance investigation report contain?
38. How would you design event-log retention and analysis for post-mortem debugging?
39. How would you change your debugging strategy when the same workload alternates between fast and very slow runs?
40. How would you prevent random Spark tuning from becoming configuration debt?

---

## 57. Architecture Questions

### Architecture Scenario 1 — Intermittent 20-Minute vs 2-Hour Runtime

**System context:** daily production Spark pipeline.

**Symptoms:** most runs finish normally; some runs take dramatically longer.

**Evidence:** task-duration long tail on slow runs.

**Investigation strategy:**
- compare input/distribution,
- compare task distribution,
- compare shuffle,
- compare SQL plan/runtime metrics,
- inspect executor logs.

**Candidate causes:** skew, infrastructure, data growth, changed partitioning.

**Design choices:** targeted partition/skew mitigation or infrastructure remediation.

**Trade-offs:** additional shuffle or complexity may be introduced.

**Validation:** compare comparable runs.

**Prevention:** monitor task-tail and workload-distribution metrics.

---

### Architecture Scenario 2 — Executor OOM After Data Doubles

**Context:** daily aggregation.

**Symptoms:** executor OOM begins after growth.

**Evidence:** large partitions and increased spill.

**Investigation:** task distribution, partition size, SQL plan, cache, executor logs.

**Candidates:** partition sizing, skew, larger intermediate state.

**Long-term prevention:** workload-aware partitioning and regression tracking.

---

### Architecture Scenario 3 — One Join Task Takes 30× Longer

**Context:** large fact-to-dimension join.

**Symptoms:** one task dominates.

**Evidence:** long tail and shuffle.

**Investigation:** join keys, partition sizes, hot keys, broadcast suitability.

**Trade-offs:** salting can increase data volume; broadcast can increase executor memory.

**Validation:** output equivalence and task distribution.

---

### Architecture Scenario 4 — Huge Disk Spill

**Context:** large aggregation.

**Symptoms:** disk spill dominates stage.

**Evidence:** spill + memory pressure.

**Investigation:** operator, partition size, cache, skew.

**Design choices:** pre-aggregation, partition strategy, query redesign, resource change only when justified.

---

### Architecture Scenario 5 — Repeated Executor Disappearance

**Context:** production cluster.

**Symptoms:** executors repeatedly disappear and downstream stages fail.

**Investigation:** executor logs, container events, node health, network, memory.

**Trade-offs:** application and infrastructure changes may have different operational ownership.

**Prevention:** centralized failure metrics and infrastructure monitoring.

---

### Architecture Scenario 6 — Driver Crash

**Context:** large DataFrame processing.

**Symptoms:** driver OOM.

**Evidence:** driver log and code path.

**Candidate:** unbounded `collect()`/`toPandas()`.

**Design:** distributed write or aggregate before collecting.

**Validation:** bound driver-side result size.

---

### Architecture Scenario 7 — Regression After Spark Upgrade

**Context:** same code and workload.

**Symptoms:** runtime changes after upgrade.

**Investigation:**
- compare Spark version,
- physical plan,
- configuration,
- AQE behavior,
- SQL runtime metrics,
- task distribution.

**Trade-off:** rollback versus adapting workload/configuration must be based on evidence and compatibility requirements.

---

### Architecture Scenario 8 — Centralized Monitoring for Hundreds of Jobs

**Context:** many production pipelines.

**Requirement:** detect regressions automatically.

**Architecture:**

```text
Spark Applications
      ↓
Event Logs / REST / Listeners
      ↓
Metrics Extraction
      ↓
Metrics Store
      ↓
Dashboard + Alerting
      ↓
Performance Investigation
```

**Track:**
- runtime,
- input,
- shuffle,
- spill,
- task distributions,
- failures,
- resource utilization.

**Long-term prevention:** define workload-specific baselines rather than one global runtime threshold.

---

## 58. Performance Investigation Report

Use this as a reusable template.

# Spark Performance Investigation

## 1. Summary

What happened?

## 2. Symptom

What became slow or failed?

## 3. Impact

Who or what was affected?

## 4. Workload

Describe:

- input volume,
- partitions,
- key distribution,
- output,
- execution environment.

## 5. Baseline

Record normal performance.

## 6. Evidence

List UI, plan, log, and infrastructure evidence.

## 7. Slowest Stage

Record stage ID, duration, task count, and relevant metrics.

## 8. Task Distribution

Record min/median/max and long-tail observations.

## 9. Shuffle Analysis

Record shuffle read/write and interpretation.

## 10. Spill Analysis

Record memory/disk spill and interpretation.

## 11. GC Analysis

Record relevant GC evidence.

## 12. SQL Plan Analysis

Record relevant operators such as:

- FileScan,
- Filter,
- Exchange,
- Join,
- Aggregate,
- Sort,
- Window.

## 13. Logs

Include relevant driver/executor evidence.

## 14. Root-Cause Hypothesis

Write a falsifiable explanation.

## 15. Change Made

Record exactly one material change for the experiment.

## 16. Before vs After

Use:

| Metric | Baseline | Change | After | Interpretation |
|---|---:|---|---:|---|
| Runtime | | | | |
| Input | | | | |
| Shuffle Read | | | | |
| Shuffle Write | | | | |
| Spill Memory | | | | |
| Spill Disk | | | | |
| GC Time | | | | |
| Task Median | | | | |
| Task Max | | | | |
| Executor Failures | | | | |

## 17. Correctness Validation

Explain how output correctness was verified.

## 18. Resource Impact

Did CPU, memory, network, or storage requirements change?

## 19. Remaining Risks

What is still uncertain?

## 20. Recommendation

State the evidence-supported next action.

---

## 59. Production Debugging Checklist

### 1. Confirm

- [ ] What is slow?
- [ ] Since when?
- [ ] Compared with what baseline?

### 2. Jobs

- [ ] Identify slow job.

### 3. Stages

- [ ] Identify slow stage.

### 4. Tasks

- [ ] Check min.
- [ ] Check median.
- [ ] Check max.
- [ ] Look for long tail.

### 5. Data

- [ ] Input size.
- [ ] Output size.
- [ ] Partition count.
- [ ] Distribution/skew.

### 6. Shuffle

- [ ] Shuffle read.
- [ ] Shuffle write.
- [ ] Expected versus unexpected movement.

### 7. Memory

- [ ] Memory spill.
- [ ] Disk spill.
- [ ] GC.
- [ ] Cache.

### 8. SQL

- [ ] Physical plan.
- [ ] Runtime operator metrics.
- [ ] Exchange/join/aggregation behavior.

### 9. Logs

- [ ] Driver.
- [ ] Executor.
- [ ] Failed task.
- [ ] Exception.

### 10. Infrastructure

- [ ] Executor loss.
- [ ] Network.
- [ ] Container.
- [ ] Resource pressure.

### 11. Hypothesis

- [ ] Write down likely cause.
- [ ] Identify evidence supporting it.
- [ ] Identify evidence that could disprove it.

### 12. Change

- [ ] Make one material change.

### 13. Measure

- [ ] Compare against baseline.

### 14. Validate

- [ ] Verify correctness.
- [ ] Verify resource impact.

### 15. Document

- [ ] Complete investigation report.
- [ ] Record preventive action.

---

## 60. Learning Checkpoints

### Checkpoint 1 — UI Fundamentals

You can:

- navigate major tabs,
- identify jobs and stages,
- find the slowest stage.

### Checkpoint 2 — Metrics

You can:

- interpret min/median/max,
- read shuffle,
- read spill,
- read GC.

### Checkpoint 3 — Plan + UI

You can:

- connect physical plan to UI,
- identify expensive operators,
- explain runtime behavior.

### Checkpoint 4 — Failure Diagnosis

You can:

- distinguish driver OOM from executor OOM,
- investigate shuffle failures,
- investigate executor loss,
- investigate memory-overhead failures.

### Checkpoint 5 — Production Debugging

You can:

- diagnose a slow job,
- form a hypothesis,
- make one change,
- measure,
- validate correctness,
- write an investigation report.

---

## 61. Final Assessment

### Part A — Theory

Explain:

- Spark UI,
- Jobs,
- Stages,
- Tasks,
- shuffle,
- spill,
- GC,
- SQL/DataFrame tab,
- driver/executor logs,
- History Server,
- event logs.

### Part B — Diagnosis

Take an intentionally slow workload.

You must:

1. Identify the slowest stage.
2. Identify task distribution.
3. Inspect shuffle.
4. Inspect spill.
5. Inspect SQL plan.
6. Inspect logs.
7. Form a hypothesis.
8. Apply one fix.
9. Measure.
10. Validate correctness.

### Part C — Failure Analysis

Diagnose:

- driver OOM,
- executor OOM,
- shuffle fetch failure,
- lost executor.

For each, identify:

- symptom,
- evidence,
- likely root causes,
- investigation path,
- corrective action.

### Part D — Production Report

Produce:

- summary,
- evidence,
- root cause,
- fix,
- before/after metrics,
- correctness validation,
- prevention.

### Passing standard

Do not pass based only on memorized definitions.

You should be able to open a Spark UI and explain:

> "This is the symptom, this is the evidence, this is my hypothesis, this is the one change I will test, and this is how I will measure whether it worked."

---

## 62. Glossary

**Spark UI** — Web interface for inspecting Spark application execution, jobs, stages, tasks, SQL executions, storage, executors, and environment information.

**Application** — A Spark program running as a distributed application.

**Job** — A unit of execution typically triggered by an action.

**Stage** — A set of tasks separated from other execution regions by dependency boundaries such as shuffle boundaries.

**Task** — The unit of work executed against a partition.

**Executor** — A process that performs tasks for a Spark application.

**Driver** — The process coordinating the Spark application and scheduling work.

**Shuffle** — Redistribution of data across partitions/executors.

**Shuffle read** — Data fetched by downstream tasks from shuffle output.

**Shuffle write** — Intermediate shuffle data written for downstream consumption.

**Spill** — Moving intermediate execution state out of memory because available execution memory is insufficient.

**Memory spill** — Spill involving execution memory management before/around disk-backed storage.

**Disk spill** — Intermediate state written to disk.

**GC** — JVM garbage collection.

**Straggler** — A task that takes substantially longer than its peers.

**Speculative execution** — Running an additional attempt for a task believed to be unusually slow.

**SQL tab** — Spark UI area showing SQL/DataFrame execution information and runtime metrics.

**Physical plan** — The execution-oriented plan selected by Spark for a query.

**Runtime metric** — Measurement collected while an operator/stage/task executes.

**Event log** — Persisted record of application execution events used for historical analysis.

**History Server** — Service that presents retained Spark event-log information for completed applications.

**Driver log** — Log output from the application driver.

**Executor log** — Log output from executor processes.

**OutOfMemoryError** — JVM memory failure indicating an allocation could not be satisfied by the relevant JVM memory area.

**Memory overhead** — Memory associated with executor/driver resources outside the main JVM heap, with exact behavior depending on Spark and cluster manager.

**Python worker** — Python process used to execute Python-side Spark workload components.

**Shuffle fetch failure** — Failure to retrieve required shuffle data.

**Lost executor** — An executor process/resource that Spark can no longer use.

**Serialization** — Conversion of an object/function into a form that can be transferred or stored.

**Spark listener** — Event-driven mechanism for receiving Spark application execution events.

**REST API** — Programmatic HTTP interface associated with Spark application/UI information; exact endpoints are version/environment dependent.

**Performance regression** — A measurable deterioration relative to a defined baseline.

**Baseline** — Reference performance and workload state against which a new run is compared.

**Root cause** — The underlying condition responsible for the observed failure or performance problem.

**Hypothesis** — A testable explanation for observed evidence.

---

## 63. Cross-Connections to Previous Topics

This topic is intentionally diagnostic rather than a re-teaching of earlier modules.

### Topic 04 — Transformations, Actions, Jobs, Stages

Use the execution chain:

```text
Transformation
→ Action
→ Job
→ Stages
→ Tasks
```

The UI lets you observe the execution that the earlier theory predicted.

### Topic 07 — Joins, Shuffle, Broadcast

Use:

- join strategy,
- shuffle read/write,
- broadcast evidence,
- task distribution.

### Topic 08 — Repartition, Coalesce, Partition Count

Use:

- number of tasks,
- partition sizes,
- under/over-parallelism,
- task duration.

### Topic 09 — Skew and Salting

Use:

- long-tail tasks,
- uneven partition work,
- shuffle distribution.

### Topic 10 — Caching

Use:

- Storage tab,
- memory,
- GC,
- eviction,
- reuse.

### Topic 11 — Python UDFs

Use:

- Python execution operators,
- CPU/runtime evidence,
- controlled replacement experiments.

### Topic 12 — Catalyst and Explain Plans

Use:

- physical plan,
- Exchange,
- scans,
- joins,
- aggregates,
- runtime operator metrics.

### Topic 13 — AQE

Use:

- runtime-adapted behavior,
- initial versus final plan,
- skew handling,
- partition coalescing.

### Topic 14 — Data Sources and Bucketing

Use:

- input size,
- file layout,
- small-file symptoms,
- JDBC behavior,
- bucket-related execution evidence.

### Forward connection — Topic 16 Testing PySpark Code

Testability reduces debugging time.

Pure transformations are easier to isolate and diagnose than code that combines:

- I/O,
- transformations,
- side effects,
- external dependencies.

Separating I/O from transformation logic also improves reliability and makes controlled performance experiments easier.

---

## 64. No Random Tuning

Make this rule operational:

```text
OBSERVE
   ↓
HYPOTHESIZE
   ↓
TEST
   ↓
MEASURE
```

Not:

```text
SLOW
 ↓
CHANGE FIVE SETTINGS
 ↓
HOPE
```

Random tuning creates:

- configuration complexity,
- hidden technical debt,
- higher infrastructure cost,
- false confidence,
- harder production debugging.

A configuration change is an engineering experiment when:

1. the hypothesis is explicit,
2. one material variable is changed,
3. the workload is comparable,
4. metrics are collected,
5. correctness is checked.

---

## 65. No Fabricated Metrics

All numbers in this chapter are illustrative unless explicitly produced by the learner's environment.

Do **not** invent:

- runtime,
- shuffle sizes,
- task counts,
- spill values,
- GC times,
- memory usage,
- Spark UI output.

Use labels such as:

> **Illustrative example**

or:

> **Example output — may vary by environment**

Actual benchmarks must come from the learner's run.

---

## 66. Spark Version Awareness

Spark UI details and metrics can vary between versions and distributions.

Therefore:

- verify UI labels against the installed Spark version,
- do not assume identical metrics across platforms,
- do not fabricate REST endpoints,
- verify configuration behavior,
- verify History Server deployment details.

Check:

```python
print(spark.version)
```

The conceptual debugging method remains stable:

```text
Evidence
→
Hypothesis
→
Controlled change
→
Measurement
```

---

## 67. Production Debugging Mindset

A senior data engineer does not start with:

> "What configuration should I change?"

Start with:

> **"What does the evidence show?"**

Then:

> **"What is the most likely root cause?"**

Then:

> **"What is the smallest change that tests my hypothesis?"**

Then:

> **"Did the metrics improve?"**

Finally:

> **"Did correctness remain intact?"**

This mindset turns Spark debugging from trial-and-error into engineering.

---

## 68. Final Self-Review

Before considering Topic 15 complete, verify:

- [ ] Spark UI overview is understood.
- [ ] Jobs tab is understood.
- [ ] Stages tab is understood.
- [ ] Storage tab is understood.
- [ ] Environment tab is understood.
- [ ] Executors tab is understood.
- [ ] SQL/DataFrame tab is understood.
- [ ] Slowest job diagnosis is understood.
- [ ] Slowest stage diagnosis is understood.
- [ ] Task min/median/max is understood.
- [ ] Task distribution is understood.
- [ ] Shuffle read/write are understood.
- [ ] Input/output scale is considered.
- [ ] Memory/disk spill is understood.
- [ ] GC is understood.
- [ ] Driver logs are understood.
- [ ] Executor logs are understood.
- [ ] Log levels are understood.
- [ ] SQL runtime metrics are understood.
- [ ] History Server is understood.
- [ ] Event logs are understood.
- [ ] Systematic debugging workflow can be followed.
- [ ] Skew can be diagnosed from evidence.
- [ ] Spill can be diagnosed from evidence.
- [ ] Too-few/too-many-task conditions can be diagnosed.
- [ ] Large shuffle can be investigated.
- [ ] UDF bottlenecks can be tested.
- [ ] Over-caching can be investigated.
- [ ] Driver OOM can be distinguished from executor OOM.
- [ ] `collect()` risk is understood.
- [ ] Broadcast memory risk is understood.
- [ ] Memory overhead/Python worker behavior is understood.
- [ ] Shuffle fetch failures can be investigated.
- [ ] Lost executors can be investigated.
- [ ] Serialization failures can be investigated.
- [ ] Long GC pauses can be investigated.
- [ ] Stragglers are understood.
- [ ] Speculative execution is understood.
- [ ] Programmatic metrics collection is understood at an advanced-awareness level.
- [ ] Spark listeners are understood conceptually.
- [ ] REST API use is understood conceptually and version-aware.
- [ ] Performance regression tracking is understood.
- [ ] Performance investigation reporting is understood.
- [ ] At least 15 hands-on labs are completed.
- [ ] At least 15 debugging exercises are completed.
- [ ] At least 12 production scenarios are analyzed.
- [ ] Exactly 40 practice questions are completed.
- [ ] Exactly 40 interview questions are completed.
- [ ] At least 8 architecture scenarios are completed.
- [ ] At least 25 misconceptions are corrected.
- [ ] Production debugging checklist is understood.
- [ ] Performance comparison template is understood.
- [ ] Learning checkpoints are passed.
- [ ] Final assessment is completed.
- [ ] No fabricated benchmark is treated as real evidence.

---

## 69. Final Takeaway

Spark performance engineering is not primarily a configuration exercise.

It is an evidence-and-hypothesis discipline.

When a Spark job is slow:

```text
Do not guess.
   ↓
Find the job.
   ↓
Find the stage.
   ↓
Inspect task distribution.
   ↓
Inspect shuffle.
   ↓
Inspect spill.
   ↓
Inspect GC.
   ↓
Inspect SQL operators.
   ↓
Inspect logs.
   ↓
Form one hypothesis.
   ↓
Make one change.
   ↓
Re-run.
   ↓
Measure.
   ↓
Validate correctness.
   ↓
Document.
```

The goal is not merely to make Spark faster.

The goal is to be able to explain, with evidence:

> **what was slow, where it was slow, why it was slow, what changed, what the metrics proved, what they did not prove, and whether the fix preserved correctness.**
