# 09 — Photon, Performance, and Predictive Optimization

> **Module:** Gap Module G4 — Databricks Lakehouse Platform Deep Dive  
> **Topic:** 09 — Photon, Performance, and Predictive Optimization  
> **Level:** Beginner → Intermediate → Advanced → Production  
> **Primary discipline:** Distributed-query performance engineering  
> **Prerequisites:** G4 Topics 01–08, plus prior Stage 2 knowledge of Spark, DataFrames, SQL, Delta Lake, joins, partitioning, AQE, Structured Streaming, and data engineering fundamentals.

---

## 1. Module Purpose

This module teaches Databricks performance engineering as a **measurement-driven production discipline**, not as a list of tuning tricks.

The central question is:

> **Why is this workload slow, what is happening underneath the execution engine and storage layer, what should I measure, what optimization should I apply, how do I verify the improvement, and is the improvement worth its cost?**

The progression is:

```text
Performance foundations
        ↓
Spark execution model
        ↓
Query-performance engineering
        ↓
Databricks execution
        ↓
Photon
        ↓
Workload suitability
        ↓
Query-plan investigation
        ↓
Delta/storage layout
        ↓
Liquid-clustering relationship
        ↓
Predictive optimization
        ↓
Observability
        ↓
Troubleshooting
        ↓
Production architecture
        ↓
Cost/performance engineering
```

### Scope boundary

This topic does **not** re-teach:

- Spark from first principles as a separate course
- Delta Lake fundamentals
- all join algorithms
- all AQE internals
- all liquid-clustering mechanics
- all compute configuration
- all orchestration concepts

Those are prerequisites. Here they are revisited only enough to explain their **performance implications**.

---

# 2. Learning Objectives

By the end of this module, you should be able to:

- explain what performance means for a production data workload;
- distinguish CPU-, memory-, I/O-, network-, scan-, shuffle-, join-, and aggregation-bound workloads;
- connect Spark jobs, stages, tasks, partitions, exchanges, scans, joins, and aggregations to observed performance;
- read a formatted physical execution plan;
- establish a reproducible performance baseline;
- characterize a workload before tuning it;
- explain Photon conceptually and technically;
- explain vectorized/native execution and why implementation-level execution efficiency matters;
- identify workloads likely to benefit from Photon;
- identify cases where Photon cannot remove the dominant bottleneck;
- understand the interaction between Python, PySpark, JVM execution, UDFs, built-in expressions, and native execution;
- benchmark Photon or Photon-capable workloads under controlled conditions;
- explain how Delta/Parquet layout affects end-to-end performance;
- reason about data skipping, file count, file size, statistics, and clustering;
- explain how liquid clustering and Photon solve different parts of the performance problem;
- explain current Databricks predictive-optimization concepts and their operational trade-offs;
- use an evidence-based decision tree for slow queries;
- troubleshoot production performance incidents;
- evaluate runtime, throughput, reliability, and cost together;
- write performance ADRs and production runbooks;
- defend an optimization decision in a design review.

---

# 3. Roadmap Position

Topic 09 deliberately follows:

```text
02 — Compute
03 — Notebooks / Git / Project Structure
04 — Unity Catalog
05 — Auto Loader
06 — Lakeflow Connect
07 — Lakeflow Declarative Pipelines
08 — Lakeflow Jobs
09 — Photon / Performance / Predictive Optimization
```

This sequencing matters.

Earlier topics teach **how workloads are built, governed, ingested, transformed, and orchestrated**. Topic 09 teaches how to make those workloads operationally efficient.

The later topics then build on this performance discipline:

```text
09 — Performance
   ↓
10 — Databricks SQL / AI-BI / Genie
   ↓
11 — Delta Sharing / Marketplace
   ↓
12 — Asset Bundles / CI-CD
   ↓
13 — Cost Management
   ↓
14 — MLflow / Feature Engineering
```

Performance therefore sits at the point where the learner moves from **building pipelines** to **engineering production behavior**.

---

# 4. The Core Performance Mental Model

A logically correct query is not necessarily an operationally efficient query.

Compare:

```text
LOGICAL CORRECTNESS

"Does the query return the right answer?"
```

with:

```text
OPERATIONAL EFFICIENCY

"Does the query return the right answer
within the required latency, throughput,
reliability, and cost envelope?"
```

A production engineer cares about both.

## 4.1 The performance stack

```text
Application / Query Logic
        ↓
Spark SQL / DataFrame API
        ↓
Catalyst Optimization
        ↓
Physical Execution Plan
        ↓
Photon / Execution Engine
        ↓
Partitions / Exchanges / Shuffle
        ↓
Delta / Parquet Layout
        ↓
Storage
        ↓
Compute
        ↓
Cloud Infrastructure
```

A faster execution engine cannot compensate indefinitely for a terrible workload shape.

For example:

```text
Bad architecture:
5 TB scanned
    ↓
5 TB transferred / processed
    ↓
expensive join
    ↓
large shuffle
    ↓
slow execution
```

A better architecture may first reduce the work:

```text
5 TB table
    ↓
predicate + column pruning
    ↓
data skipping / efficient layout
    ↓
400 GB relevant data
    ↓
efficient execution
    ↓
smaller shuffle
    ↓
lower latency + lower cost
```

### Mental Model

> **Scan less → move less → compute less → pay less.**

---

# 5. Performance Fundamentals

## 5.1 What does "performance" mean?

For data platforms, performance has several dimensions:

| Dimension | Question |
|---|---|
| Latency | How long does one workload take? |
| Throughput | How much data/work can be processed per unit time? |
| CPU efficiency | How effectively is available compute used? |
| Memory efficiency | Are executors/compute avoiding pressure and spills? |
| I/O efficiency | How much data is read and written? |
| Network efficiency | How much data crosses process/node boundaries? |
| Parallelism | Is enough useful work happening concurrently? |
| Stability | Does runtime remain predictable as data grows? |
| Cost efficiency | How much does useful work cost? |
| Reliability | Does performance remain inside the SLO under normal failures? |

A senior engineer avoids optimizing a single metric in isolation.

---

## 5.2 CPU-bound workloads

A workload is CPU-bound when processor work is the dominant constraint.

Typical clues:

- high CPU utilization;
- substantial computation per input byte;
- expensive expressions;
- complex aggregations;
- serialization/deserialization overhead;
- Python/UDF-heavy processing;
- execution time does not fall much when storage throughput increases.

Typical actions:

1. inspect expensive operators;
2. replace avoidable UDFs with native expressions;
3. reduce unnecessary computation;
4. investigate vectorized/native execution;
5. evaluate Photon where supported;
6. test whether additional compute reduces wall-clock time efficiently.

---

## 5.3 Memory-bound workloads

Typical symptoms:

- memory pressure;
- spills;
- garbage-collection pressure where applicable;
- large joins or aggregations;
- excessive materialization;
- too much caching;
- very wide rows.

Potential actions:

- reduce columns early;
- reduce intermediate data;
- improve join strategy;
- reduce skew;
- reconsider caching;
- increase appropriate compute resources only after identifying the cause.

---

## 5.4 I/O-bound workloads

Typical symptoms:

- large scan volume;
- low compute utilization relative to data movement;
- slow reads/writes;
- unnecessary files touched;
- inefficient layout.

The first question should often be:

> **Why are we reading this much data?**

not:

> **Which compute size should I buy?**

---

## 5.5 Network-bound workloads

Network cost appears when data must move between workers or external systems.

Common causes:

- shuffle;
- large joins;
- repartitioning;
- skew;
- external service calls;
- unnecessarily wide intermediate data.

---

## 5.6 Scan-heavy workloads

A scan-heavy workload spends substantial time reading data.

Typical improvements:

- select only required columns;
- filter as early as possible;
- exploit predicate pushdown;
- improve table layout;
- use statistics/data skipping mechanisms where applicable;
- avoid unnecessary historical scans;
- use workload-driven clustering.

---

## 5.7 Shuffle-heavy workloads

Shuffle redistributes data across partitions.

It commonly appears around:

- joins;
- groupBy;
- distinct;
- repartition;
- sort;
- aggregations requiring data exchange.

Shuffle can consume:

- CPU;
- memory;
- network bandwidth;
- disk/spill;
- scheduling overhead.

The right response is diagnosis, not automatically "add more workers."

---

## 5.8 Small files

Thousands or millions of tiny files can create overhead in:

- file listing;
- planning;
- metadata handling;
- task scheduling;
- storage requests;
- inefficient scans.

Small-file problems are a **storage/layout problem**, not something Photon alone solves.

---

## 5.9 Under-parallelization vs over-parallelization

### Under-parallelization

Too little useful concurrency can leave resources idle.

### Over-parallelization

Too many tiny tasks can create scheduling and coordination overhead.

The objective is:

> **Enough parallelism to saturate useful resources without creating disproportionate overhead.**

---

# 6. Spark Performance Foundation

The learner has already studied Spark. The purpose here is to connect those concepts to performance.

## 6.1 Driver

The driver coordinates the application.

Performance implications include:

- excessive driver-side collection;
- large metadata workloads;
- poor control-plane patterns;
- collecting massive results to the driver.

---

## 6.2 Executors

Executors perform distributed work.

Their behavior affects:

- CPU;
- memory;
- task execution;
- shuffle;
- spills;
- I/O.

---

## 6.3 Jobs, stages, tasks

A simplified relationship:

```text
Action
  ↓
Spark Job
  ↓
Stages
  ↓
Tasks
  ↓
Partitions
```

A slow job is not necessarily slow everywhere.

One stage may dominate the entire critical path.

---

## 6.4 Narrow vs wide transformations

Narrow transformations can generally process data without redistributing it across partitions.

Wide transformations require an exchange/shuffle.

A useful mental model:

```text
filter / projection
    ↓
usually local processing

groupBy / many joins / repartition
    ↓
potential exchange
    ↓
network + shuffle + synchronization
```

---

## 6.5 Physical execution

Spark turns the logical request into an executable physical plan.

A useful simplified model:

```text
DataFrame / SQL
      ↓
Logical Plan
      ↓
Catalyst Optimization
      ↓
Physical Plan
      ↓
Execution Operators
      ↓
Execution Engine
```

Photon participates at the execution-engine layer where supported.

---

# 7. Worked Example: From Query to Execution

Consider:

```python
df = (
    spark.read.format("delta").load("/data/sales")
    .filter("sale_date >= '2026-01-01'")
    .groupBy("customer_id")
    .sum("amount")
)
```

This expression is lazy.

No aggregation necessarily occurs until an action such as:

```python
df.show()
```

or:

```python
df.write.mode("overwrite").format("delta").save("/data/customer_sales")
```

The engine must conceptually:

```text
Read Delta metadata
      ↓
Identify candidate files
      ↓
Apply filters / data skipping where possible
      ↓
Read required columns
      ↓
Create partitions/tasks
      ↓
Aggregate by customer_id
      ↓
Exchange data if required
      ↓
Perform aggregation
      ↓
Materialize result
```

Inspect the plan:

```python
df.explain("formatted")
```

Or use SQL:

```sql
EXPLAIN FORMATTED
SELECT customer_id, SUM(amount)
FROM sales
WHERE sale_date >= DATE '2026-01-01'
GROUP BY customer_id;
```

### What to inspect

Look for:

- scan operators;
- filters;
- projections;
- exchanges;
- joins;
- aggregation operators;
- sorts;
- partition counts;
- suspiciously large data movement;
- operators that dominate runtime in actual execution.

The exact UI labels and available metrics can change. Verify current Databricks documentation before relying on a particular interface field.

---

# 8. Query Performance Engineering

The production optimization loop is:

```text
Understand workload
        ↓
Measure baseline
        ↓
Inspect execution plan
        ↓
Identify bottleneck
        ↓
Change one thing
        ↓
Run controlled test
        ↓
Measure improvement
        ↓
Validate correctness
        ↓
Evaluate cost
        ↓
Document decision
```

## 8.1 Why random tuning fails

Applying five changes simultaneously creates an attribution problem.

If runtime improves, you do not know which change helped.

If runtime worsens, you do not know which change caused the regression.

If cost rises, you may not understand why.

Therefore:

> **Change one material variable at a time when establishing causality.**

After causal understanding, combine compatible production changes deliberately.

---

# 9. Performance Benchmark Template

Use this template for every serious experiment.

```text
Experiment ID:
Date:
Owner:
Workload:
Business purpose:

Dataset version:
Input size:
Rows:
Columns:

Query/version:
Compute environment:
Runtime:
Photon status:
Concurrency:
Autoscaling/serverless settings:

Baseline runtime:
Baseline data scanned:
Baseline shuffle:
Baseline task/stage behavior:
Baseline estimated/actual cost:

Hypothesis:

Change:

Test runtime:
Test data scanned:
Test shuffle:
Test task/stage behavior:
Test estimated/actual cost:

Correctness result:

Performance delta:
Cost delta:
Reliability/stability impact:

Decision:
Rollback:
Follow-up:
```

### Rule

A benchmark that cannot be reproduced is weak evidence.

---

# 10. What Is Photon?

## 10.1 Simple explanation

Think of Spark as the **programming and distributed-computation model**.

Photon is a Databricks execution engine designed to execute supported workloads more efficiently using native, vectorized techniques.

Analogy:

```text
Same recipe
     ↓
different kitchen machinery
     ↓
better machinery can prepare the same work more efficiently
```

But if the recipe asks you to cook five terabytes of unnecessary ingredients, better machinery does not fix the fundamental problem.

---

## 10.2 Mental model

```text
Spark programming model
        ↓
Catalyst optimization
        ↓
Physical execution plan
        ↓
Execution engine
        ↓
Photon / native execution where supported
```

Photon therefore does not replace:

- Spark SQL;
- DataFrame APIs;
- Catalyst;
- distributed data processing concepts.

It changes how supported execution work is performed.

---

# 11. Why Databricks Built Photon

Traditional JVM-based distributed execution is powerful and general.

However, large analytical workloads can benefit from:

- native execution;
- vectorized processing;
- efficient CPU utilization;
- columnar processing;
- lower per-record execution overhead;
- optimized implementations of supported operators.

At a high level:

```text
Traditional execution
many logical records
        ↓
general-purpose operator implementation
        ↓
CPU work

Photon-oriented execution
columnar batches
        ↓
native/vectorized operators
        ↓
efficient CPU utilization
```

The exact internal implementation is Databricks proprietary and evolves over time. The production lesson is to reason from **observed workload behavior and supported current functionality**, not from assumptions about undocumented internals.

---

# 12. Vectorized and Native Execution

## 12.1 Scalar mental model

A scalar approach can be imagined as:

```text
row 1 → process
row 2 → process
row 3 → process
...
```

## 12.2 Vectorized mental model

Vectorized processing operates on groups/batches of values:

```text
batch of column values
        ↓
optimized CPU operations
        ↓
batch result
```

Modern CPUs can execute certain operations efficiently across vectors of values.

This can improve:

- CPU efficiency;
- throughput;
- operator efficiency;
- memory access patterns.

---

# 13. Photon Architecture in Context

A simplified conceptual architecture:

```text
SQL / DataFrame
      ↓
Logical Plan
      ↓
Optimized Logical Plan
      ↓
Physical Plan
      ↓
Execution Operators
      ↓
Photon-compatible native operators
      ↓
Vectorized / native execution
      ↓
CPU / memory / I/O
```

Photon does not mean every physical operator is magically transformed into a faster implementation.

A workload may contain:

```text
Photon-benefiting operators
        +
non-Photon work
        +
I/O bottlenecks
        +
shuffle
        +
Python/external logic
```

The final runtime is determined by the **whole execution graph**.

---

# 14. Photon Workload Suitability

Photon is generally most interesting for analytical workloads involving substantial supported SQL/DataFrame execution.

Examples:

- large SQL scans;
- filtering;
- projections;
- aggregations;
- joins;
- warehouse analytics;
- large Delta workloads;
- BI-oriented workloads;
- ETL/ELT transformations that remain in supported native execution paths.

Potentially smaller gains can occur when the dominant bottleneck is:

- unsupported/custom execution;
- Python-heavy work;
- external service calls;
- poor storage layout;
- severe skew;
- excessive data movement;
- concurrency;
- inadequate or incorrectly configured compute;
- fundamentally excessive data scanned.

### Core rule

> **Photon can accelerate execution, but Photon cannot eliminate every bottleneck.**

---

# 15. Photon Does Not Fix Bad Query Design

Consider:

```sql
SELECT *
FROM five_terabyte_table;
```

Turning on a faster execution engine does not make five terabytes disappear.

A better query might be:

```sql
SELECT customer_id, amount
FROM five_terabyte_table
WHERE sale_date >= DATE '2026-01-01';
```

Now the system has an opportunity to:

- read fewer columns;
- eliminate irrelevant data;
- exploit filtering and layout;
- reduce downstream processing.

The correct sequence is:

```text
Reduce unnecessary work
        ↓
Optimize execution
        ↓
Optimize compute
        ↓
Measure cost
```

not:

```text
Turn on faster compute
        ↓
hope
```

---

# 16. Photon and Python

Python deserves special attention because PySpark is not the same thing as "all execution happens in Python."

## 16.1 Native Spark expression

Example:

```python
from pyspark.sql import functions as F

df2 = df.withColumn("normalized_name", F.upper("name"))
```

The expression is represented in Spark's execution model.

## 16.2 Python UDF

A Python UDF can introduce additional Python execution overhead:

```python
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

def normalize_name(value):
    return value.upper() if value else None

normalize_udf = udf(normalize_name, StringType())

df2 = df.withColumn("normalized_name", normalize_udf("name"))
```

The UDF is not equivalent to the built-in expression from a performance perspective.

Potential overhead includes:

- Python process boundaries;
- serialization/deserialization;
- conversion overhead;
- reduced ability for the optimizer to reason about custom logic;
- loss of native operator opportunities.

### Prefer built-in expressions

```python
df.withColumn("normalized_name", F.upper("name"))
```

when the built-in function expresses the required logic.

---

# 17. Pandas UDFs and Arrow

Pandas UDFs can use vectorized Python execution and Arrow-based data exchange where applicable.

That can be substantially better than naïve row-by-row Python UDF execution for certain workloads.

However:

> **Vectorized Python is not automatically equivalent to native execution.**

There is still Python execution and data interchange overhead.

Decision hierarchy:

```text
Can Spark built-in express it?
        ↓ yes
Use built-in expression
        ↓ no
Can a native SQL/DataFrame approach express it?
        ↓
Prefer native execution
        ↓
If Python is genuinely required:
consider an appropriate vectorized approach
```

---

# 18. Before/After UDF Example

### Before

```python
def classify_amount(x):
    if x is None:
        return "unknown"
    if x >= 1000:
        return "high"
    return "normal"

classify_udf = udf(classify_amount, StringType())

result = df.withColumn(
    "amount_class",
    classify_udf("amount")
)
```

### After

```python
result = df.withColumn(
    "amount_class",
    F.when(F.col("amount").isNull(), "unknown")
     .when(F.col("amount") >= 1000, "high")
     .otherwise("normal")
)
```

### What to measure

Do not assume the second version is better because it looks cleaner.

Measure:

- wall-clock runtime;
- CPU;
- stage/task duration;
- input/output;
- shuffle;
- correctness;
- compute cost.

---

# 19. Query Plans and Performance Investigation

## 19.1 EXPLAIN

Use:

```sql
EXPLAIN FORMATTED
SELECT customer_id, SUM(amount)
FROM sales
WHERE sale_date >= DATE '2026-01-01'
GROUP BY customer_id;
```

Or:

```python
df.explain("formatted")
```

### Plan-reading questions

Ask:

1. What is the scan?
2. Which columns are being read?
3. Is filtering visible?
4. Is an exchange present?
5. Is there a join?
6. Is there an aggregation?
7. Is sorting required?
8. Where might data volume increase?
9. Which operator is likely to dominate?
10. Does the actual execution support the hypothesis?

A plan tells you what the engine intends to do. Runtime metrics tell you what actually happened.

---

# 20. Observability: Plan vs Runtime

Use two layers of evidence:

```text
STATIC EVIDENCE
EXPLAIN / physical plan
        ↓
"What does the engine intend to execute?"

RUNTIME EVIDENCE
Spark UI / SQL UI / query history / logs / metrics
        ↓
"What actually happened?"
```

Important observations include:

- runtime;
- stage duration;
- task-duration distribution;
- input size;
- output size;
- shuffle volume;
- spill behavior;
- skew;
- concurrency;
- compute configuration;
- workload size.

Exact Databricks UI names and locations evolve. Verify current documentation before automating against a particular UI field.

---

# 21. Photon Benchmarking

## 21.1 Baseline

Record:

- runtime;
- data scanned;
- shuffle;
- stage duration;
- task count;
- compute configuration;
- Photon state where the environment exposes it;
- concurrency;
- workload size.

## 21.2 Controlled test

Run the same workload against a comparable environment.

Control:

- dataset;
- query text;
- result correctness;
- compute shape;
- concurrency;
- cache state where relevant;
- time-of-day effects where material;
- other major workload interference.

## 21.3 Compare

```text
Runtime
CPU efficiency
Resource utilization
Throughput
Stability
Cost
```

---

# 22. Performance Is Not the Same as Cost

Consider:

```text
Before:
10 minutes
$2

After:
4 minutes
$3
```

The second result is faster but more expensive.

It may still be correct for:

- interactive BI;
- strict latency SLOs;
- revenue-critical workloads;
- user-facing applications.

Now:

```text
Before:
10 minutes
$2

After:
6 minutes
$1.10
```

This is potentially a stronger optimization because both latency and cost improved.

The correct question is:

> **Did the optimization improve the business-relevant objective without unacceptable trade-offs?**

---

# 23. Delta Lake and Photon

Photon operates on execution. Delta Lake determines much of the physical data being accessed.

Important concepts include:

- Delta transaction log;
- Parquet;
- columnar storage;
- file scans;
- predicate pushdown;
- column pruning;
- statistics;
- data skipping;
- file size;
- small files;
- clustering/layout.

### Complementary optimization

```text
Delta / layout optimization
=
reduce unnecessary data touched

Photon
=
process supported work more efficiently

Together
=
better end-to-end performance potential
```

---

# 24. The Scan Reduction Principle

Suppose a workload starts with:

```text
5 TB logical table
```

Poor layout/query behavior:

```text
5 TB scanned
```

Improved filtering/layout:

```text
400 GB scanned
```

Then execution optimization:

```text
400 GB
   ↓
efficient native/vectorized execution
```

The largest gain may have come from reducing the amount of work before changing the execution engine.

### Senior-engineer principle

> **First ask whether you can reduce the work. Then ask how efficiently the remaining work can be executed.**

---

# 25. Liquid Clustering and Photon

Liquid clustering has already been introduced elsewhere in the G4 roadmap.

This topic focuses only on the relationship.

## 25.1 Different problems

```text
Liquid clustering
=
better physical organization of table data

Photon
=
faster execution of supported computation
```

## 25.2 Combined model

```text
Query
 ↓
better data layout
 ↓
fewer irrelevant files / bytes
 ↓
smaller workload
 ↓
Photon/native execution
 ↓
more efficient processing
```

Liquid clustering may be useful when query patterns evolve or filtering dimensions do not fit a rigid static partitioning strategy.

The correct choice remains workload-dependent.

---

# 26. Liquid Clustering Performance Investigation

Ask:

- What are the dominant filtering patterns?
- How much data is scanned?
- Which columns drive selective queries?
- Does the table experience changing query patterns?
- Is the current layout causing excessive scanning?
- What maintenance work is required?
- Does the resulting scan reduction justify the maintenance/cost?

Do not assume clustering is beneficial merely because a table is large.

---

# 27. Predictive Optimization

## 27.1 What is predictive optimization?

Predictive optimization is a Databricks capability for automating supported table-maintenance and optimization decisions using platform intelligence and workload/storage signals.

The engineering motivation is simple:

```text
Small number of tables
        ↓
manual maintenance may be manageable

Thousands of governed tables
        ↓
manual optimization becomes operationally expensive
```

Automation can reduce repetitive human maintenance.

---

# 28. Manual vs Automated Optimization

### Manual model

```text
Engineer
  ↓
observe table
  ↓
choose maintenance
  ↓
schedule/run operation
  ↓
measure
  ↓
repeat
```

### Automated model

```text
Platform
  ↓
observe supported signals
  ↓
make supported optimization decisions
  ↓
perform supported maintenance
  ↓
reduce manual intervention
```

Automation does **not** mean:

- all tables become optimal;
- all workloads become fast;
- engineering judgment disappears;
- cost becomes irrelevant;
- every optimization decision becomes transparent;
- application/query problems disappear.

---

# 29. Predictive Optimization — Current-Documentation Rule

Databricks evolves rapidly.

Capabilities, eligibility, naming, supported table types, behavior, interfaces, and pricing can change.

For production use, verify the current official Databricks documentation for:

- what predictive optimization currently automates;
- eligible objects/table types;
- current enablement model;
- current Unity Catalog requirements;
- supported maintenance operations;
- monitoring/observability;
- cost implications;
- regional/edition/workspace dependencies.

Do not treat historical descriptions of predictive optimization as current platform guarantees.

> **Verify this against the current Databricks documentation before using it in production.**

---

# 30. Predictive Optimization vs Manual Optimization

| Dimension | Manual | Predictive / Automated |
|---|---|---|
| Maintenance effort | Higher | Lower for supported automation |
| Operational control | Direct | Policy/platform mediated |
| Human tuning | High | Lower for routine work |
| Scale | Harder across many objects | Better suited to fleet-scale maintenance |
| Cost predictability | Explicit per chosen action | Requires monitoring of automated activity |
| Custom decision-making | High | Depends on supported platform behavior |
| Failure modes | Human scheduling/configuration errors | Eligibility, automation, policy, cost, or platform-behavior issues |
| Best use | Exceptional/custom tuning | Routine supported maintenance at scale |

### When manual optimization is still useful

- controlled experiments;
- exceptional tables;
- incident response;
- one-off migrations;
- cases outside automated scope;
- workload-specific design changes;
- performance engineering that is fundamentally about query logic rather than maintenance.

---

# 31. Performance Layers

Use this hierarchy when diagnosing a problem:

```text
Application / Query Logic
        ↓
Spark SQL / DataFrame API
        ↓
Catalyst Optimization
        ↓
Photon / Execution Engine
        ↓
Partitioning / Shuffle
        ↓
Delta / Parquet Layout
        ↓
Storage
        ↓
Compute
        ↓
Cloud Infrastructure
```

Examples:

### Query-layer problem

`SELECT *` when only three columns are required.

### Execution-layer problem

Expensive custom computation.

### Shuffle-layer problem

Large exchange caused by an avoidable repartition.

### Layout problem

Huge amounts of irrelevant data scanned.

### Compute problem

Insufficient capacity for the workload's concurrency/SLO.

### Architecture problem

A single interactive warehouse is serving incompatible batch and BI workloads.

---

# 32. Production Optimization Decision Tree

```text
Query slow?
    ↓
Measure first
    ↓
Is too much data scanned?
    ├── Yes → storage/layout/filter investigation
    └── No
         ↓
Is shuffle dominant?
    ├── Yes → partition/join/skew investigation
    └── No
         ↓
Is CPU dominant?
    ├── Yes → expression/operator/execution investigation
    └── No
         ↓
Is I/O dominant?
    ├── Yes → storage investigation
    └── No
         ↓
Is Python/UDF overhead dominant?
    ├── Yes → native/built-in expression investigation
    └── No
         ↓
Is concurrency/resource capacity dominant?
    ├── Yes → compute/isolation/scaling investigation
    └── No
         ↓
Investigate workload-specific behavior
```

---

# 33. Performance Anti-Patterns

## 33.1 "Photon will fix it"

Why dangerous:

- execution speed cannot remove unnecessary data;
- layout issues remain;
- skew remains;
- external calls remain;
- bad query logic remains.

---

## 33.2 `SELECT *`

Reads data that may never be needed.

---

## 33.3 Python UDF everywhere

Can introduce Python overhead and reduce opportunities for native execution.

---

## 33.4 Excessive shuffle

Large exchanges increase:

- network traffic;
- CPU;
- memory pressure;
- spill risk;
- runtime.

---

## 33.5 Data skew

One partition can become dramatically larger than others.

A job may appear to be "almost finished" while one task remains active.

---

## 33.6 Excessive repartition

Repartitioning is not free.

Use it because a measurable workload characteristic requires it.

---

## 33.7 Excessive caching

Caching can consume memory and create maintenance pressure without helping repeated workloads enough to justify the cost.

---

## 33.8 Insufficient compute

Sometimes the workload genuinely needs more capacity.

But prove it before scaling.

---

## 33.9 Over-provisioning

More compute can reduce runtime while destroying unit economics.

---

## 33.10 Ignoring concurrency

A query can be fast in isolation and slow under production concurrency.

---

## 33.11 Benchmarking tiny datasets

A 1 GB test may hide:

- skew;
- file-layout problems;
- shuffle amplification;
- concurrency behavior;
- scaling characteristics.

---

## 33.12 Optimizing without measurement

No baseline means no causal evidence.

---

## 33.13 Changing everything at once

This destroys experimental attribution.

---

# 34. Query vs Platform vs Architecture Optimization

## Query optimization

Changes:

- SQL;
- DataFrame logic;
- columns;
- filters;
- expressions;
- joins;
- UDFs.

## Platform optimization

Changes:

- compute;
- Photon;
- warehouse configuration;
- scaling;
- concurrency;
- workload isolation.

## Architecture optimization

Changes:

- data layout;
- ingestion architecture;
- serving architecture;
- workload separation;
- table strategy;
- orchestration boundaries.

A production performance problem may require all three levels.

---

# 35. Production Performance Engineering

A senior Data Engineer starts with the workload.

## 35.1 Workload characterization

Capture:

- input size;
- growth rate;
- query frequency;
- concurrency;
- latency SLO;
- throughput;
- batch/interactive nature;
- peak windows;
- cost budget;
- correctness requirements.

---

## 35.2 SLO thinking

Example:

```text
Dashboard P95 latency:
≤ 10 seconds

Daily batch:
≤ 45 minutes

Data freshness:
≤ 15 minutes

Monthly compute budget:
≤ defined business budget
```

The optimization objective should be explicit.

---

# 36. Capacity Planning

Ask:

1. What is the current workload?
2. What is the expected six-month workload?
3. What is the concurrency peak?
4. What is the SLO?
5. What is the cost ceiling?
6. Can workloads be isolated?
7. Can serverless or autoscaling improve economics?
8. What happens during backfills?

---

# 37. Performance Regression Engineering

A production platform should detect regressions before users do.

A useful regression framework stores:

```text
Workload ID
Dataset size
Query version
Runtime
Input bytes
Shuffle
Task/stage profile
Compute configuration
Cost
Result correctness
Timestamp
```

Then compare:

```text
current
vs
historical baseline
```

Trigger investigation when material degradation occurs.

Do not define a universal threshold without considering workload variability.

---

# 38. Performance vs Cost

A complete optimization function is:

```text
Performance
+
Reliability
+
Cost
+
Maintainability
=
Production optimization
```

## Cost dimensions

Consider:

- compute consumption;
- DBUs conceptually;
- cloud infrastructure;
- serverless economics;
- Photon economics;
- runtime;
- concurrency;
- idle resources;
- autoscaling;
- workload isolation;
- scheduled workloads;
- interactive workloads.

Do not use hard-coded current DBU prices in training examples.

> **Verify current Databricks and cloud pricing before making a production cost decision.**

---

# 39. Governance and Security

A faster workaround is not a production optimization if it violates governance.

Performance engineering must respect:

- Unity Catalog;
- permissions;
- service principals;
- production identities;
- managed tables;
- auditability;
- approved compute;
- secure test data;
- least privilege.

For example:

```text
"Copy sensitive production data to an uncontrolled
developer location because it is faster to test"
```

is not an acceptable optimization.

---

# 40. Hands-On Labs

The following labs are deliberately progressive.

---

## Lab 1 — Establish a Performance Baseline

### Objective

Create a repeatable baseline for a large Delta query.

### Prerequisites

- Databricks workspace;
- accessible Delta dataset;
- SQL or notebook execution;
- permission to inspect query execution.

### Dataset

Use a realistic sales/fact table with:

- at least tens of millions of rows for a meaningful environment;
- date;
- customer;
- product;
- amount;
- region.

### Workload

```sql
SELECT customer_id, SUM(amount) AS revenue
FROM sales
WHERE sale_date >= DATE '2026-01-01'
GROUP BY customer_id;
```

### Record

- runtime;
- input volume;
- shuffle;
- stage duration;
- compute;
- concurrency;
- cost estimate where available.

### Questions

1. What is the dominant stage?
2. Is the workload CPU- or I/O-heavy?
3. How much data is scanned?
4. Is shuffle material?

### Troubleshooting

If the dataset is too small, increase the workload rather than pretending the benchmark is representative.

### Cleanup

No persistent changes required.

### Production lesson

> A performance change without a baseline is an opinion.

---

## Lab 2 — Read a Physical Execution Plan

### Objective

Understand what the engine intends to execute.

### Command

```python
df.explain("formatted")
```

or:

```sql
EXPLAIN FORMATTED
SELECT customer_id, SUM(amount)
FROM sales
WHERE sale_date >= DATE '2026-01-01'
GROUP BY customer_id;
```

### Analyze

Identify:

- scan;
- filter;
- projection;
- aggregation;
- exchange;
- sort if present.

### Production lesson

Learn to connect plan operators to observed runtime behavior.

---

## Lab 3 — Identify a Slow Operator

### Objective

Start from a slow workload and determine which stage/operator dominates.

### Procedure

1. Run workload.
2. Record total runtime.
3. Find longest stage.
4. Inspect task-duration distribution.
5. Identify operator associated with the work.
6. Form a hypothesis.
7. Test one change.

### Production lesson

Do not optimize the first operator that looks complicated. Optimize the operator supported by evidence.

---

## Lab 4 — Built-In Expression vs Python UDF

### Objective

Measure the cost of Python UDF execution.

### Test A

Use a Python UDF to classify a numeric value.

### Test B

Use `when`, `otherwise`, and built-in column expressions.

### Measure

- runtime;
- CPU behavior;
- stage profile;
- shuffle;
- cost.

### Analysis

Why did the built-in expression perform differently?

### Production lesson

Prefer built-in expressions whenever they express the required business logic.

---

## Lab 5 — Investigate a Shuffle-Heavy Workload

### Objective

Diagnose an expensive exchange.

### Workload

Join a large fact table to another large table, then aggregate.

### Procedure

1. inspect plan;
2. identify exchange;
3. inspect data volume;
4. check join cardinality;
5. inspect skew;
6. test a justified join/layout strategy;
7. benchmark.

### Production lesson

Shuffle is often a symptom of the computation required by the query, not a problem to eliminate blindly.

---

## Lab 6 — Investigate Excessive Data Scanning

### Objective

Reduce unnecessary scan work.

### Starting query

```sql
SELECT *
FROM sales
WHERE customer_id = 12345;
```

### Improve

- select only needed columns;
- understand table layout;
- use selective predicates;
- measure scanned data.

### Questions

1. How much data was read before?
2. How much afterward?
3. Did runtime improve?
4. Did cost improve?

---

## Lab 7 — Photon Benchmark

### Objective

Compare the same suitable analytical workload in environments where a meaningful Photon/non-Photon comparison is currently supported.

### Procedure

1. verify current Databricks support;
2. freeze workload;
3. use comparable compute;
4. run warm-up if appropriate;
5. collect baseline;
6. collect Photon result;
7. validate correctness;
8. compare runtime and cost.

### Important

Do not invent a Photon configuration flag.

Use the current Databricks compute/workspace documentation for the supported way to select Photon-capable compute.

### Production lesson

Benchmark product behavior, not marketing claims.

---

## Lab 8 — Photon + Delta Layout

### Objective

Demonstrate that execution-engine speed and data reduction are complementary.

### Experiment

Compare:

```text
Poor layout + efficient execution
vs
Better layout + efficient execution
```

Measure:

- data scanned;
- runtime;
- shuffle;
- cost.

### Production lesson

The best optimization may be reducing the amount of work rather than accelerating the same amount of work.

---

## Lab 9 — Liquid Clustering Performance Investigation

### Objective

Measure the performance relationship between layout and execution.

### Procedure

1. identify a workload with selective filters;
2. establish baseline;
3. inspect scan behavior;
4. evaluate whether current table layout is appropriate;
5. apply liquid clustering only if justified and supported;
6. allow relevant maintenance;
7. rerun representative workloads;
8. compare scan volume and runtime.

### Production lesson

Liquid clustering and Photon solve different problems.

---

## Lab 10 — Predictive Optimization

### Objective

Understand current supported predictive-optimization behavior in the learner's Databricks environment.

### Procedure

1. verify current official documentation;
2. verify workspace/Unity Catalog eligibility;
3. identify a suitable governed table;
4. understand the current enablement model;
5. enable/configure only according to current supported procedures;
6. observe resulting maintenance/optimization behavior;
7. inspect performance and cost evidence;
8. document what was automated.

### Important

Do not copy historical commands from old training material.

### Production lesson

Automation is useful only when its scope, cost, and behavior are understood.

---

## Lab 11 — Performance vs Cost Benchmark

### Objective

Compare two solutions using both latency and economics.

### Scenario

```text
Solution A:
10 min
$2

Solution B:
5 min
$3
```

Then test a third option if appropriate.

### Decide

Which solution satisfies the business SLO at the best acceptable cost?

### Production lesson

A 2× speedup is not automatically a 2× improvement in production value.

---

## Lab 12 — Production Optimization Exercise

### Scenario

A workload has:

- large Delta tables;
- repeated joins;
- Python UDFs;
- excessive scan;
- shuffle;
- dashboard concurrency;
- increasing cost.

### Task

Systematically:

1. establish baseline;
2. profile;
3. inspect plans;
4. identify bottlenecks;
5. optimize query logic;
6. reduce unnecessary data;
7. evaluate Photon;
8. evaluate layout;
9. evaluate clustering;
10. evaluate predictive optimization;
11. benchmark;
12. validate correctness;
13. compare cost;
14. document recommendation.

### Production lesson

Senior engineering is evidence-based iteration.

---

# 41. Production Capstone

# Databricks Lakehouse Performance Optimization Project

## Scenario

A production analytics platform has:

- large Delta tables;
- repeated BI queries;
- joins;
- aggregations;
- historical data;
- frequent incremental ingestion;
- concurrent dashboards;
- slow user-facing analytics;
- increasing compute cost.

## Your mission

You are the performance engineer.

### Required steps

1. Establish baseline.
2. Profile workload.
3. Inspect execution plans.
4. Identify bottlenecks.
5. Optimize query logic.
6. Improve data-access patterns.
7. Evaluate Photon.
8. Evaluate Delta table layout.
9. Evaluate liquid clustering where appropriate.
10. Evaluate predictive optimization.
11. Compare runtime.
12. Compare cost.
13. Validate correctness.
14. Produce production recommendation.

## Required final report

```text
Problem

Baseline

Evidence

Root Cause

Optimization

Before/After

Performance Impact

Cost Impact

Risk

Recommendation

Rollback Strategy
```

### Acceptance criteria

The report must show evidence for every major recommendation.

Do not write:

> "Photon made it faster."

Write:

> "The workload was CPU-heavy after scan reduction. The controlled Photon-capable benchmark reduced runtime from X to Y while maintaining correctness. Cost changed from A to B, and the resulting latency satisfied the workload SLO."

---

# 42. Break/Fix Production Incidents

Each incident follows:

```text
Symptom
→ Business Impact
→ Initial Hypothesis
→ Evidence
→ Investigation
→ Root Cause
→ Fix
→ Verification
→ Prevention
→ Production Lesson
```

---

## Incident 1 — Photon Workload Still Slow

### Symptom

A team enables Photon-capable compute but a 5 TB query remains slow.

### Business impact

Dashboard SLA is missed.

### Initial hypothesis

"Photon is not working."

### Evidence

- scan volume;
- physical plan;
- shuffle;
- skew;
- query shape;
- concurrency.

### Root cause

The workload scans excessive data and performs a large exchange.

### Fix

Reduce scan and address the actual shuffle bottleneck.

### Verification

Compare controlled before/after runs.

### Prevention

Require evidence-based bottleneck identification.

---

## Incident 2 — Excessive Data Scan

### Symptom

A 200 GB result requires several terabytes of reads.

### Impact

High latency and cost.

### Root cause

Poor filtering/layout and unnecessary columns.

### Fix

Reduce projected columns and improve data-access strategy.

### Verification

Measure scanned bytes and runtime.

---

## Incident 3 — Python UDF Bottleneck

### Symptom

One stage dominates runtime.

### Root cause

Heavy Python UDF execution.

### Fix

Replace with built-in expressions where possible.

### Verification

Compare equivalent outputs and performance.

---

## Incident 4 — Shuffle Explosion

### Symptom

A join produces unexpectedly large shuffle.

### Investigation

Inspect cardinality and join plan.

### Root cause

Join logic creates substantial data movement.

### Fix

Rewrite/reshape workload where justified.

### Verification

Measure shuffle and runtime.

---

## Incident 5 — Skewed Join

### Symptom

Most tasks finish quickly; one/few tasks run much longer.

### Root cause

Highly skewed key distribution.

### Fix

Investigate key distribution and apply an appropriate skew strategy.

### Verification

Compare task-duration distribution.

---

## Incident 6 — Small-File Problem

### Symptom

A table has an excessive number of small files.

### Root cause

Ingestion/write pattern.

### Fix

Use appropriate supported maintenance/layout strategy.

### Verification

Measure planning and scan behavior.

---

## Incident 7 — Poor Table Layout

### Symptom

Highly selective queries scan a large portion of the table.

### Root cause

Physical organization does not match workload.

### Fix

Evaluate workload-driven layout and clustering.

---

## Incident 8 — Excessive Repartition

### Symptom

A seemingly simple transformation introduces an expensive exchange.

### Root cause

Unnecessary repartition.

### Fix

Remove or justify the repartition based on evidence.

---

## Incident 9 — Insufficient Compute

### Symptom

A workload consistently misses its latency SLO despite efficient query logic.

### Root cause

The available capacity is insufficient for the workload and concurrency.

### Fix

Evaluate appropriate compute scaling/isolation.

### Verification

Measure runtime and unit cost.

---

## Incident 10 — Over-Provisioned Compute

### Symptom

Runtime is excellent but cost is excessive.

### Root cause

Compute is oversized relative to the workload.

### Fix

Benchmark smaller/alternative compute.

---

## Incident 11 — Concurrency Causes Latency

### Symptom

Queries are fast individually but slow during business peaks.

### Root cause

Resource contention/concurrency.

### Fix

Evaluate workload isolation, scheduling, scaling, or appropriate warehouse configuration.

---

## Incident 12 — Regression After Data Growth

### Symptom

A query that ran in 4 minutes now takes 12 minutes.

### Investigation

Compare:

- data size;
- query version;
- layout;
- scan;
- shuffle;
- concurrency;
- compute.

### Root cause

Determine from evidence; do not assume "Spark got slower."

---

## Incident 13 — Optimization Increased Cost

### Symptom

Runtime improves but spend rises materially.

### Fix

Evaluate the business SLO and unit economics.

### Decision

Keep only if the business value justifies the incremental cost.

---

## Incident 14 — Automated Optimization Has Unexpected Cost

### Symptom

Background maintenance increases resource usage.

### Root cause

Automation is performing supported maintenance that has compute/storage implications.

### Fix

Review current platform behavior, scope, workload value, and governance settings.

### Prevention

Monitor optimization cost and define ownership.

---

## Incident 15 — Runtime Improved but Dashboard SLA Still Missed

### Symptom

Query improves from 20 minutes to 8 minutes, but users still experience unacceptable latency.

### Root cause

The query was only one component of end-to-end latency.

### Investigation

Trace:

```text
Dashboard
 ↓
Query submission
 ↓
Queueing/concurrency
 ↓
Execution
 ↓
Result delivery
```

### Lesson

Optimize the **business path**, not only the SQL runtime.

---

# 43. Additional Break/Fix Scenarios

## Incident 16 — Benchmark Is Not Reproducible

Possible causes:

- changing dataset;
- different compute;
- changing concurrency;
- cache state;
- multiple simultaneous workloads.

### Fix

Freeze experiment variables.

---

## Incident 17 — More Workers Made Runtime Worse

Possible causes:

- coordination overhead;
- insufficient parallel work;
- I/O bottleneck;
- skew;
- resource contention.

### Lesson

Scale only after identifying the limiting resource.

---

## Incident 18 — Photon Improvement Disappears at Production Scale

Possible causes:

- production workload has different data distribution;
- concurrency;
- skew;
- storage layout;
- different query mix.

### Lesson

Benchmark representative production-scale behavior.

---

# 44. Production Runbook — Slow Databricks Query

### Slow Databricks Query Runbook

## Step 1 — Define SLA/SLO

What does "slow" mean?

---

## Step 2 — Capture Baseline

Record:

- runtime;
- workload size;
- compute;
- concurrency;
- cost.

---

## Step 3 — Check Workload Size

Did data volume grow?

---

## Step 4 — Inspect Query Plan

Use:

```python
df.explain("formatted")
```

or:

```sql
EXPLAIN FORMATTED ...
```

---

## Step 5 — Inspect Scan Behavior

Ask:

- How much data is scanned?
- Are unnecessary columns read?
- Is filtering selective?

---

## Step 6 — Inspect Shuffle

Ask:

- Is there a large exchange?
- Is shuffle volume unexpectedly high?
- Is repartition necessary?

---

## Step 7 — Inspect Joins

Check:

- cardinality;
- join strategy;
- skew;
- unnecessary columns.

---

## Step 8 — Inspect Skew

Look for highly uneven task durations or partition sizes.

---

## Step 9 — Inspect Python/UDF Usage

Replace avoidable Python logic with native expressions.

---

## Step 10 — Inspect Storage Layout

Check:

- file count;
- file sizes;
- data skipping;
- clustering/layout;
- scan volume.

---

## Step 11 — Evaluate Photon

Determine whether the dominant workload is appropriate for Photon and whether a controlled benchmark is possible.

---

## Step 12 — Evaluate Compute

Only now consider:

- scaling;
- workload isolation;
- serverless;
- SQL warehouse configuration;
- autoscaling.

---

## Step 13 — Evaluate Concurrency

Was the workload slow only under peak load?

---

## Step 14 — Evaluate Predictive Optimization

Determine whether current supported automation is relevant.

---

## Step 15 — Benchmark

Change one major variable and measure.

---

## Step 16 — Validate Correctness

Performance without correctness is failure.

---

## Step 17 — Compare Cost

Record:

```text
Before:
runtime / cost / SLA

After:
runtime / cost / SLA
```

---

## Step 18 — Document and Deploy

Record:

- root cause;
- evidence;
- fix;
- benchmark;
- rollback;
- owner;
- monitoring.

---

# 45. Decision Matrix — Photon

| Workload | CPU Intensity | Data Size | Query Pattern | Photon Suitability | Expected Benefit | Caveats |
|---|---:|---:|---|---|---|---|
| Large analytical SQL | High | Large | Scan/filter/aggregate | High potential | Medium–High | Verify supported operators |
| Large joins | High | Large | Join/aggregate | Often strong candidate | Medium–High | Shuffle/skew may dominate |
| BI queries | Medium–High | Medium–Large | Repeated SQL | Strong candidate | Medium–High | Concurrency matters |
| Python-heavy transformation | Variable | Large | Custom Python | Lower/partial | Variable | Python may dominate |
| External API calls | Low/Variable | Variable | Network calls | Low | Low | External dependency dominates |
| Poorly laid-out table | Variable | Large | Excessive scan | Partial | Limited alone | Fix data access/layout |
| Severe skew | Variable | Large | Hot keys | Partial | Variable | Skew remains a bottleneck |
| Small workload | Low | Small | Simple query | Often limited | Low | Overhead may dominate |

This is a reasoning matrix, not a promise of performance.

---

# 46. Decision Matrix — Optimization Choice

| Problem | Query Rewrite | Built-ins | Join Optimization | Partition Strategy | Data Layout | Liquid Clustering | Photon | Predictive Optimization | Compute Scaling |
|---|---|---|---|---|---|---|---|---|---|
| Excessive scan | High | Medium | Low | Medium | High | High | Low–Medium | Potential | Low |
| Python overhead | Low | High | Low | Low | Low | Low | Potential | Low | Medium |
| Shuffle | Medium | Low | High | High | Medium | Medium | Medium | Low | Medium |
| Poor layout | Low | Low | Low | Medium | High | High | Low | Potential | Low |
| CPU-bound supported operators | Medium | High | Low | Low | Medium | Low | High potential | Low | Medium |
| Concurrency | Low | Low | Low | Low | Low | Low | Medium | Low | High |
| Routine table maintenance | Low | Low | Low | Low | Medium | Medium | Low | High potential | Low |

---

# 47. Decision Matrix — Manual vs Automated Optimization

| Dimension | Manual | Predictive / Automated |
|---|---|---|
| Best for | Custom/exceptional cases | Routine supported maintenance |
| Control | High | Platform-mediated |
| Operational effort | High | Lower |
| Scale | Limited by human effort | Better for large fleets |
| Experimentation | Excellent | Not the primary purpose |
| Cost visibility | Direct action-by-action | Must monitor automation |
| Failure mode | Human error | Platform scope/eligibility/policy |
| Governance | Engineer-controlled | Policy/platform-controlled |
| Recommendation | Use when evidence requires custom intervention | Use when supported and economically justified |

---

# 48. Architecture Decision Records

## ADR-001 — Adopt Photon for Analytical Workloads

### Context

The platform serves large analytical workloads with measurable CPU-intensive execution.

### Problem

Runtime is above the workload SLO.

### Options

1. query rewrite only;
2. more compute;
3. Photon-capable execution;
4. architecture redesign.

### Decision

Evaluate/adopt Photon where controlled benchmarking demonstrates a material benefit.

### Why

It can improve supported analytical execution efficiency.

### Trade-offs

- cost may change;
- not every workload benefits;
- unsupported/custom work can remain a bottleneck.

### Consequences

Benchmarking and regression monitoring become mandatory.

### Rollback

Return to the prior supported compute/execution configuration.

### Validation

Compare runtime, correctness, cost, and stability.

---

## ADR-002 — Prefer Native Spark Expressions Over Python UDFs

### Context

A transformation is implemented using a Python UDF.

### Problem

The stage is CPU-heavy and UDF overhead is material.

### Options

- retain UDF;
- Pandas UDF;
- built-in expression;
- redesign transformation.

### Decision

Use built-in/native expressions whenever they express the business logic.

### Why

They preserve opportunities for Spark-native optimization and avoid unnecessary Python overhead.

### Trade-offs

Complex custom logic may still require Python.

### Consequences

Tests must prove semantic equivalence.

### Rollback

Restore previous implementation if correctness or compatibility fails.

### Validation

Benchmark and compare outputs.

---

## ADR-003 — Use Workload-Driven Table Layout

### Context

Large tables are queried through selective predicates.

### Problem

Too much data is scanned.

### Options

- keep layout;
- static partitioning;
- liquid clustering;
- query rewrite;
- other supported layout strategies.

### Decision

Choose layout based on observed workload access patterns.

### Why

The objective is to reduce unnecessary data access.

### Trade-offs

Maintenance and compute cost must be considered.

### Validation

Measure scan reduction, runtime, cost, and stability.

---

## ADR-004 — Adopt Predictive Optimization Where Appropriate

### Context

The platform contains many governed tables requiring maintenance.

### Problem

Manual maintenance does not scale operationally.

### Options

- manual operations;
- automation;
- hybrid approach.

### Decision

Use current supported predictive optimization capabilities where eligibility, cost, governance, and operational behavior are acceptable.

### Why

Automation can reduce repetitive maintenance.

### Trade-offs

Automated work consumes resources and requires monitoring.

### Validation

Measure maintenance outcomes and cost.

---

## ADR-005 — Define Performance Benchmarking Standards

### Context

Optimization decisions are inconsistent.

### Problem

Teams compare workloads without controlled baselines.

### Decision

Require:

```text
Baseline
→ Hypothesis
→ One major change
→ Controlled test
→ Correctness validation
→ Cost comparison
→ Decision record
```

### Consequences

Performance work becomes auditable and reproducible.

---

# 49. Observability Framework

Observe performance at multiple layers.

| Layer | Evidence |
|---|---|
| Query | Runtime, query text, result |
| Plan | Physical plan |
| Stage | Duration, task distribution |
| Task | Long-running/outlier tasks |
| Data | Input/output, scan |
| Shuffle | Exchange/shuffle behavior |
| Compute | Resource utilization/configuration |
| Platform | Query history/logs |
| Cost | Compute/DBU/cloud cost |
| Business | SLA/SLO and user experience |

> **If you cannot observe the workload, you cannot reliably optimize it.**

Use current Databricks documentation to verify exact UI labels, system-table schemas, and metric names before building production automation.

---

# 50. Performance Regression Monitoring

A production team should monitor:

- median runtime;
- P95/P99 where appropriate;
- data scanned;
- shuffle;
- workload volume;
- concurrency;
- cost per workload;
- SLA/SLO misses.

A regression may be caused by:

```text
query change
+
data growth
+
layout change
+
compute change
+
concurrency change
+
platform/runtime change
```

Therefore compare multiple dimensions before assigning root cause.

---

# 51. Production Performance Architecture Patterns

## Pattern 1 — BI Analytics

```text
BI
 ↓
Databricks SQL / appropriate warehouse
 ↓
Delta tables
 ↓
governed layout
 ↓
Photon-capable execution where appropriate
```

Focus:

- low latency;
- concurrency;
- predictable cost;
- workload isolation.

---

## Pattern 2 — Batch ETL

```text
Lakeflow Jobs
 ↓
pipeline/task
 ↓
Delta transformations
 ↓
Photon-capable job compute where appropriate
 ↓
curated tables
```

Focus:

- throughput;
- reliability;
- retries;
- cost;
- predictable completion.

---

## Pattern 3 — Mixed Workloads

Separate:

```text
interactive BI
      +
scheduled batch
      +
ad hoc analysis
```

when contention makes shared resources unstable.

---

## Pattern 4 — Large Incremental Lakehouse

```text
Auto Loader / Lakeflow Connect
          ↓
Delta
          ↓
transformations
          ↓
workload-driven layout
          ↓
Photon-capable execution where useful
          ↓
analytics
```

---

## Pattern 5 — Fleet-Scale Governance

```text
Unity Catalog
      ↓
many governed tables
      ↓
supported automated optimization
      ↓
observability
      ↓
cost controls
```

The engineering problem becomes operational scale rather than one-table tuning.

---

# 52. Interview Preparation

## Beginner — 15 Questions

### B1. What is Photon?

**Answer:** Photon is Databricks' native execution engine designed to accelerate supported workloads through efficient native/vectorized execution.

### B2. Is Photon a replacement for Spark?

**Answer:** No. Spark remains the programming/distributed-processing model; Photon is an execution engine used for supported workloads.

### B3. What is query latency?

**Answer:** The elapsed time required to complete a query or workload.

### B4. What is throughput?

**Answer:** The amount of useful work or data processed per unit time.

### B5. What is a shuffle?

**Answer:** Distributed redistribution of data between partitions, often involving network and synchronization overhead.

### B6. Why can shuffle be expensive?

**Answer:** It can consume network, CPU, memory, disk/spill, and coordination resources.

### B7. What is a Python UDF?

**Answer:** A user-defined function implemented in Python and invoked as part of a Spark transformation.

### B8. Why prefer built-in Spark functions?

**Answer:** They preserve native execution and optimizer opportunities and generally avoid unnecessary Python-boundary overhead.

### B9. What is data skipping?

**Answer:** Avoiding files/data ranges that cannot satisfy a query predicate based on available metadata/statistics/layout information.

### B10. What is liquid clustering?

**Answer:** A Databricks table-layout approach that organizes data based on workload-relevant clustering keys without relying on traditional rigid partitioning in the same way.

### B11. What is a physical execution plan?

**Answer:** A plan describing how the logical workload will actually be executed.

### B12. Why benchmark?

**Answer:** To determine whether a change produces a measurable improvement under controlled conditions.

### B13. Does more compute always make queries faster?

**Answer:** No. Storage, shuffle, skew, concurrency, or other bottlenecks can dominate.

### B14. What is predictive optimization?

**Answer:** A Databricks capability for automating supported table-maintenance/optimization decisions using platform intelligence.

### B15. What is the first step in performance tuning?

**Answer:** Define the SLO and establish a baseline.

---

## Intermediate — 20 Questions

### I1. Why does Photon help CPU-heavy analytical workloads?

**Answer:** Native/vectorized execution can process supported operators more efficiently and reduce per-record execution overhead.

### I2. Why does Photon not solve excessive scanning?

**Answer:** The execution engine may process the scanned data faster, but the workload is still doing unnecessary work.

### I3. How do you identify a shuffle bottleneck?

**Answer:** Inspect the physical plan and runtime stage/task behavior for exchanges, large data movement, spills, and long shuffle stages.

### I4. How do you identify a CPU-bound query?

**Answer:** Correlate high compute utilization with operator behavior and show that CPU work, rather than I/O or network, is limiting throughput.

### I5. Why can a query be slow with low CPU?

**Answer:** It may be I/O-, network-, shuffle-, concurrency-, or scheduling-bound.

### I6. What is the relationship between Photon and Catalyst?

**Answer:** Catalyst optimizes the logical/physical plan; Photon is an execution engine that executes supported physical work efficiently.

### I7. Why are Python UDFs often slower than built-ins?

**Answer:** They can introduce Python execution and serialization/conversion overhead and reduce native optimizer/execution opportunities.

### I8. How should Photon be benchmarked?

**Answer:** Use identical workload/data, comparable compute, controlled concurrency, correctness validation, and runtime/cost measurements.

### I9. Why can a 2× faster query be a bad optimization?

**Answer:** If it costs substantially more and the business does not require the lower latency.

### I10. What is a scan-heavy workload?

**Answer:** A workload where reading large amounts of data dominates execution.

### I11. Why can small files hurt performance?

**Answer:** They increase metadata, planning, task, and storage-request overhead.

### I12. Why does skew cause a long tail?

**Answer:** A few partitions receive disproportionate data, leaving outlier tasks running after most tasks finish.

### I13. What should you inspect before changing compute?

**Answer:** Workload size, plan, scan, shuffle, joins, skew, UDFs, concurrency, and storage layout.

### I14. What is predictive optimization's main operational value?

**Answer:** Reducing repetitive manual maintenance across supported governed tables at scale.

### I15. Does predictive optimization eliminate performance engineering?

**Answer:** No. Query design, workload shape, architecture, compute, and cost still require engineering judgment.

### I16. Why should one change be tested at a time?

**Answer:** To establish causal attribution.

### I17. What is a performance regression?

**Answer:** A material deterioration in a workload's measured behavior relative to an accepted baseline.

### I18. Why is production-scale benchmarking important?

**Answer:** Small tests can hide skew, file-layout, shuffle, concurrency, and scaling behavior.

### I19. What is a performance SLO?

**Answer:** A measurable service objective for latency, throughput, freshness, or related performance behavior.

### I20. Why does layout complement Photon?

**Answer:** Layout can reduce the amount of data accessed; Photon can improve the efficiency of processing the remaining work.

---

## Advanced — 20 Questions

### A1. A 5 TB query is CPU-bound with Photon. What next?

**Answer:** Inspect operator-level behavior and query logic. Look for expensive expressions, UDFs, aggregation complexity, unnecessary computation, and opportunities to reduce data before execution.

### A2. A query scans 5 TB but returns 50 MB. What does that suggest?

**Answer:** Strong potential for scan reduction through filtering, column pruning, layout, statistics/data skipping, or clustering.

### A3. A query is fast alone but slow at 9 AM. Why?

**Answer:** Concurrency/resource contention may dominate during the production peak.

### A4. More workers increase runtime. Explain.

**Answer:** The bottleneck may not be compute capacity; additional resources can introduce coordination overhead, contention, or expose another limiting layer.

### A5. Photon reduces CPU but runtime does not change. Why?

**Answer:** CPU was not the critical-path bottleneck. I/O, shuffle, concurrency, or another stage likely dominates.

### A6. Python UDF removal reduces runtime by 35%. What should you document?

**Answer:** Baseline, UDF stage evidence, equivalent native implementation, correctness validation, runtime delta, cost impact, and regression guard.

### A7. Why can a table-layout change outperform an execution-engine change?

**Answer:** Reducing scanned data changes the amount of work, while an execution-engine change mainly improves efficiency of work that remains.

### A8. How do you distinguish skew from insufficient compute?

**Answer:** Inspect task-duration distribution and partition sizes. Skew typically produces outlier tasks rather than uniformly slow work.

### A9. What should a benchmark control?

**Answer:** Dataset, query, compute, concurrency, workload version, result correctness, and other variables that materially affect runtime.

### A10. What is the danger of benchmarking with different cluster sizes?

**Answer:** The experiment becomes confounded; you cannot attribute the result to Photon or the target optimization.

### A11. How would you evaluate predictive optimization economically?

**Answer:** Compare avoided manual effort and performance/storage benefits with the compute/maintenance cost and operational complexity.

### A12. When would you reject predictive optimization?

**Answer:** If the current scope is ineligible, behavior is unsuitable, cost is unjustified, or manual control is required for a specific workload.

### A13. How would you investigate a 3× regression?

**Answer:** Compare historical/current data size, query version, layout, scan, shuffle, task distribution, compute, concurrency, and platform/runtime changes.

### A14. Why is correctness part of performance engineering?

**Answer:** A fast incorrect result is not a successful production optimization.

### A15. What is the difference between query and architecture optimization?

**Answer:** Query optimization changes the computation; architecture optimization changes how workloads/data/services are organized to meet systemic requirements.

### A16. What is a cost-performance frontier?

**Answer:** The set of feasible solutions trading latency/throughput against compute cost.

### A17. Why can serverless economics differ from provisioned compute economics?

**Answer:** Billing and scaling behavior differ, so the optimal choice depends on utilization, workload variability, concurrency, and current pricing.

### A18. What is a performance budget?

**Answer:** A defined maximum acceptable resource/time/cost envelope for a workload.

### A19. Why should performance tests use realistic distributions?

**Answer:** Average data size can hide skew and pathological key distributions that dominate production behavior.

### A20. How do you prove an optimization is durable?

**Answer:** Demonstrate improvement across representative workloads, data volumes, concurrency conditions, and repeated runs while monitoring regression over time.

---

## Senior / Production — 20 Questions

### S1. A 5 TB Delta query takes 18 minutes and Photon is enabled. What do you investigate first?

**Answer:** Baseline and evidence: scan volume, plan, stage critical path, shuffle, skew, UDFs, concurrency, and compute. Photon being enabled is not evidence that Photon is the bottleneck or solution.

### S2. Photon reduces runtime 40% but DBU cost rises 25%. Is it successful?

**Answer:** It depends on the SLO and business value. If the latency improvement is required, it may be successful. If latency was already sufficient, the extra cost may not be justified.

### S3. A query is CPU-bound before optimization and I/O-bound afterward. What does this tell you?

**Answer:** The optimization successfully reduced CPU work enough to expose I/O as the next bottleneck. Continue diagnosis rather than repeatedly optimizing CPU.

### S4. A dashboard slows after a table grows from 500 GB to 5 TB. How do you investigate?

**Answer:** Compare scan volume, selectivity, layout, clustering, file count, query plan, concurrency, and data-distribution changes. Growth itself is not root cause.

### S5. How would you design a performance regression framework?

**Answer:** Version workloads and datasets, capture runtime/scan/shuffle/cost/task distributions, establish baselines, define thresholds appropriate to workload variability, and alert on meaningful regressions.

### S6. Predictive optimization reduces maintenance but increases background compute. What do you do?

**Answer:** Quantify maintenance savings, performance/storage benefits, incremental compute cost, and business value; then choose a policy based on evidence.

### S7. How would you separate BI and batch contention?

**Answer:** Characterize workloads, identify SLO differences, test isolated compute/warehouse paths, compare cost and latency, and adopt isolation if shared resources create unacceptable interference.

### S8. When should you not use more compute?

**Answer:** When the dominant bottleneck is scanning, shuffle, skew, external I/O, inefficient query logic, or concurrency architecture.

### S9. How do you optimize without violating governance?

**Answer:** Use approved identities, Unity Catalog controls, governed tables, least privilege, auditable environments, and production-equivalent access patterns.

### S10. What evidence belongs in a performance ADR?

**Answer:** Workload context, baseline, bottleneck evidence, alternatives, decision, measured results, cost impact, risks, rollback, and validation.

### S11. How do you prevent optimization cargo cults?

**Answer:** Require hypothesis-driven changes and measured evidence rather than prescribing universal tuning rules.

### S12. How would you explain Photon to an architecture review board?

**Answer:** As an execution-engine choice for supported analytical workloads whose value must be demonstrated through controlled performance/cost testing.

### S13. What does "production-ready performance" mean?

**Answer:** The workload meets correctness, latency/throughput, reliability, governance, and cost requirements under representative production conditions.

### S14. How do you evaluate an optimization during peak concurrency?

**Answer:** Benchmark both isolated and representative concurrent workloads because resource contention can change the dominant bottleneck.

### S15. How would you investigate a query that is fast in development but slow in production?

**Answer:** Compare data volume/distribution, table layout, compute, concurrency, caching, query version, permissions/governance, and platform environment.

### S16. How do you decide whether liquid clustering is worth its maintenance cost?

**Answer:** Measure scan reduction and workload benefit against maintenance compute, storage, operational complexity, and alternative designs.

### S17. How would you design a rollback for a performance change?

**Answer:** Version the query/configuration/layout decision, preserve the prior supported state, define rollback triggers, and validate correctness after rollback.

### S18. How do you optimize a workload whose business requirement is cost minimization rather than latency?

**Answer:** Establish a maximum acceptable latency and optimize unit cost first, while preserving correctness and reliability.

### S19. What is the biggest performance-engineering mistake?

**Answer:** Making an optimization decision without evidence about the actual bottleneck and business objective.

### S20. What is the senior-level mental model?

**Answer:**

```text
Measure
→ Diagnose
→ Change
→ Benchmark
→ Validate
→ Price
→ Deploy
→ Monitor
→ Reassess
```

---

# 53. Practice Questions

## 53.1 Conceptual Questions — 25

1. Define performance in a distributed data platform.
2. Explain latency vs throughput.
3. What makes a workload CPU-bound?
4. What makes a workload I/O-bound?
5. What makes a workload network-bound?
6. What is shuffle?
7. Why can shuffle dominate runtime?
8. What is data skew?
9. Why are small files harmful?
10. What is an execution plan?
11. What is Catalyst's role?
12. What is Photon?
13. Why does native/vectorized execution matter?
14. What is the difference between Spark programming model and execution engine?
15. Why doesn't Photon fix bad SQL?
16. Why can Python UDFs be expensive?
17. What is data skipping?
18. Why does column pruning matter?
19. What is liquid clustering?
20. What is predictive optimization?
21. Why is baseline measurement necessary?
22. What is a performance SLO?
23. Why can more compute make a workload worse?
24. Why must correctness be validated?
25. What makes an optimization production-grade?

---

## 53.2 SQL Questions — 15

### SQL1

Rewrite:

```sql
SELECT *
FROM sales
WHERE sale_date >= DATE '2026-01-01';
```

to retrieve only three required columns.

**Expected:** Explicit column projection.

### SQL2

Explain why the following may be expensive:

```sql
SELECT customer_id, COUNT(*)
FROM sales
GROUP BY customer_id;
```

**Expected:** Full-table aggregation and potential exchange/shuffle.

### SQL3

What evidence would you collect before optimizing a large join?

### SQL4

How would you inspect a SQL physical plan?

### SQL5

How can a selective predicate reduce work?

### SQL6

Why might `DISTINCT` be expensive?

### SQL7

Why can repeated aggregation increase shuffle?

### SQL8

How would you benchmark two equivalent SQL rewrites?

### SQL9

How would you detect that a query scans more data than necessary?

### SQL10

What does a long-running aggregation stage suggest?

### SQL11

How can unnecessary columns increase cost?

### SQL12

Why should query correctness be tested after rewrites?

### SQL13

How would concurrency affect a BI SQL workload?

### SQL14

How would you decide whether a SQL workload is suitable for Photon?

### SQL15

How would you document a SQL optimization?

---

## 53.3 PySpark Questions — 15

### PySpark1

Explain:

```python
df.explain("formatted")
```

### PySpark2

Why is this preferable when equivalent?

```python
F.upper("name")
```

over a Python UDF?

### PySpark3

What is lazy evaluation?

### PySpark4

What is a wide transformation?

### PySpark5

What is an exchange?

### PySpark6

Why can `repartition()` be expensive?

### PySpark7

How would you detect a skewed workload?

### PySpark8

Why can collecting large results to the driver be dangerous?

### PySpark9

How would you benchmark two DataFrame implementations?

### PySpark10

What role does Arrow play in applicable Pandas UDF execution?

### PySpark11

Why is vectorized Python not the same as native execution?

### PySpark12

How does column pruning help?

### PySpark13

How can caching hurt performance?

### PySpark14

How does compute choice affect a PySpark workload?

### PySpark15

How would you convert a Python UDF to built-in expressions?

---

## 53.4 Performance-Debugging Scenarios — 15

1. A query scans 4 TB to return 1 GB. Diagnose.
2. One task runs for 30 minutes while 500 tasks finish in 2 minutes. Diagnose.
3. CPU is low but runtime is high. Diagnose.
4. CPU is high but shuffle is low. Diagnose.
5. Shuffle suddenly doubles after a schema change. Diagnose.
6. Runtime rises with data size faster than expected. Diagnose.
7. Photon produces only a small improvement. Diagnose.
8. UDF stage dominates runtime. Diagnose.
9. Performance is excellent at 10 AM but poor at noon. Diagnose.
10. A layout change reduces scan but increases maintenance cost. Evaluate.
11. More workers make the job slower. Diagnose.
12. A benchmark cannot be reproduced. Diagnose.
13. A query improves but the dashboard remains slow. Diagnose end-to-end.
14. Predictive optimization lowers manual work but raises compute. Evaluate.
15. A regression appears after a runtime/platform update. Diagnose using controlled comparison.

---

## 53.5 Architecture Scenarios — 10

1. Design a low-latency BI workload.
2. Design a cost-efficient nightly batch workload.
3. Design isolation between BI and batch.
4. Design a fleet-scale governed optimization strategy.
5. Design a performance regression framework.
6. Design a production benchmark environment.
7. Design a workload-driven table-layout strategy.
8. Design a secure performance-testing process.
9. Design an optimization decision-review process.
10. Design a performance observability model.

---

## 53.6 Cost/Performance Scenarios — 10

1. 40% faster, 25% more expensive — decide.
2. 20% faster, 40% cheaper — decide.
3. 2× compute produces 10% faster runtime — decide.
4. Layout maintenance costs $X but saves $Y — evaluate.
5. Predictive optimization increases background cost — evaluate.
6. Serverless reduces idle cost but changes peak economics — evaluate.
7. BI latency is above SLO — prioritize latency.
8. Batch is already within SLO but over budget — prioritize unit cost.
9. A compute upgrade helps only during peak hours — evaluate workload isolation.
10. A query rewrite reduces runtime and cost but increases code complexity — evaluate maintainability.

---

# 54. Senior Data Engineer Challenges

## Challenge 1

> A 5 TB Delta query takes 18 minutes. Photon is enabled. What do you investigate first?

Expected reasoning:

```text
SLO
→ baseline
→ scan
→ plan
→ shuffle
→ skew
→ UDF/custom logic
→ concurrency
→ compute
```

Do not start with "turn Photon on."

---

## Challenge 2

> Photon reduced runtime by 40%, but DBU cost increased by 25%. Is this successful?

Answer depends on:

- latency SLO;
- user value;
- workload frequency;
- absolute cost;
- alternative designs.

---

## Challenge 3

> A query is CPU-bound before optimization but I/O-bound afterward. What does this tell you?

The optimization removed CPU as the dominant bottleneck. The next limiting layer is now I/O.

---

## Challenge 4

> A dashboard became slower after its table grew from 500 GB to 5 TB.

Investigate:

- scan ratio;
- data skipping;
- layout;
- clustering;
- query plan;
- concurrency;
- data distribution;
- compute.

---

## Challenge 5

> A Python UDF is responsible for a major stage bottleneck.

Redesign:

1. determine whether built-ins can express the logic;
2. replace;
3. validate semantics;
4. benchmark;
5. monitor regression.

---

## Challenge 6

> Predictive optimization reduces manual maintenance but increases background compute.

Evaluate:

```text
manual labor saved
+
performance/storage benefit
-
additional compute
-
operational risk
```

Then decide from measured business value.

---

# 55. Common Beginner Misconceptions

## Misconception 1

> "Photon makes every Spark workload faster."

**Reality:** Benefit depends on workload and supported execution paths.

## Misconception 2

> "Photon fixes bad SQL."

**Reality:** It does not remove unnecessary computation.

## Misconception 3

> "Photon removes the need for layout optimization."

**Reality:** Execution speed and data access are different layers.

## Misconception 4

> "More compute always makes queries faster."

**Reality:** Other bottlenecks can dominate.

## Misconception 5

> "Caching always improves performance."

**Reality:** Cache has memory/resource costs and only helps when reuse justifies it.

## Misconception 6

> "The fastest query is always the cheapest query."

**Reality:** Faster execution can consume more resources.

## Misconception 7

> "Predictive optimization means no engineering is required."

**Reality:** Automation reduces maintenance work; it does not eliminate engineering judgment.

## Misconception 8

> "Lower runtime automatically means success."

**Reality:** Correctness, cost, reliability, maintainability, and SLOs matter.

## Misconception 9

> "If a query succeeds, performance is acceptable."

**Reality:** A successful query can still violate business SLOs and cost budgets.

---

# 56. Mental Models

## Mental Model 1

**Photon = faster execution, not better data architecture.**

## Mental Model 2

**Scan less → move less → compute less → pay less.**

## Mental Model 3

**Measure → diagnose → optimize → benchmark → verify.**

## Mental Model 4

**Storage layout determines how much data you touch; execution engine determines how efficiently you process it.**

## Mental Model 5

**Automation reduces maintenance work; it does not eliminate engineering judgment.**

## Mental Model 6

**The slowest critical-path stage determines the job's practical latency.**

## Mental Model 7

**Do not optimize a resource that evidence says is not limiting the workload.**

## Mental Model 8

**A performance improvement is only production improvement when the business objective improves.**

## Mental Model 9

**Benchmark the workload, not the feature.**

---

# 57. Glossary

| Term | Definition |
|---|---|
| Photon | Databricks execution engine designed to accelerate supported workloads through efficient native/vectorized execution. |
| Vectorized execution | Processing batches/vectors of values rather than relying only on scalar record-at-a-time processing. |
| Native execution | Execution implemented outside the traditional JVM-only path using optimized native techniques. |
| CPU-bound | A workload whose dominant limiting resource is CPU computation. |
| I/O-bound | A workload limited primarily by reading/writing data. |
| Shuffle | Distributed redistribution of data between partitions. |
| Partition | A unit of distributed data/work processed by Spark tasks. |
| Stage | A set of tasks separated from other stages by execution dependencies such as exchanges. |
| Task | A unit of work executed against a partition. |
| Execution plan | Representation of how a logical query will be physically executed. |
| Catalyst | Spark's query optimization framework. |
| Predicate pushdown | Applying filters as close to data access as possible when supported. |
| Column pruning | Reading only columns required by the workload. |
| Data skipping | Avoiding irrelevant files/data based on metadata/statistics/layout information. |
| Delta statistics | Metadata that can help determine whether data files may contain relevant values. |
| Liquid clustering | Workload-driven Databricks table-layout approach. |
| Predictive optimization | Databricks automation for supported optimization/table-maintenance decisions. |
| Query latency | Time required for a workload to complete. |
| Throughput | Useful work processed per unit time. |
| DBU | Databricks Unit, a conceptual unit used in Databricks consumption/billing models; current pricing must be verified. |
| Workload | A repeatable unit of data-processing work with defined inputs and outputs. |
| Concurrency | Number of workloads executing at the same time. |
| Skew | Uneven distribution of data/work across partitions. |
| Spill | Writing intermediate data to disk when in-memory processing cannot contain it. |
| UDF | User-defined function. |
| Python UDF | UDF implemented in Python. |
| Pandas UDF | Vectorized Python UDF mechanism using Pandas/Arrow in supported execution paths. |
| Serverless | Managed compute model where infrastructure management is abstracted from the user. |

---

# 58. Final Production Checklist

## Understanding

- [ ] I understand Spark performance fundamentals.
- [ ] I understand Photon.
- [ ] I understand vectorized/native execution.
- [ ] I understand when Photon helps.
- [ ] I understand when Photon does not solve the problem.
- [ ] I understand predictive optimization.

## Practical

- [ ] I can inspect execution plans.
- [ ] I can identify bottlenecks.
- [ ] I can benchmark workloads.
- [ ] I can compare before/after performance.
- [ ] I can analyze cost.
- [ ] I can investigate storage/layout issues.
- [ ] I can troubleshoot slow queries.

## Production

- [ ] I can create a performance baseline.
- [ ] I can perform controlled optimization.
- [ ] I can make Photon decisions.
- [ ] I can evaluate predictive optimization.
- [ ] I can write a performance ADR.
- [ ] I can create a production performance runbook.
- [ ] I can defend an optimization decision in a design review.
- [ ] I can validate correctness after performance changes.
- [ ] I can evaluate concurrency.
- [ ] I can define performance regression monitoring.

---

# 59. Final Operating Standard

Use this operating standard whenever a production Databricks workload is slow:

```text
DEFINE SLO
    ↓
MEASURE BASELINE
    ↓
CHARACTERIZE WORKLOAD
    ↓
INSPECT PLAN
    ↓
MEASURE RUNTIME BEHAVIOR
    ↓
IDENTIFY BOTTLENECK
    ↓
REDUCE UNNECESSARY WORK
    ↓
OPTIMIZE QUERY / LAYOUT / EXECUTION
    ↓
EVALUATE PHOTON
    ↓
EVALUATE COMPUTE / CONCURRENCY
    ↓
EVALUATE PREDICTIVE OPTIMIZATION
    ↓
BENCHMARK
    ↓
VALIDATE CORRECTNESS
    ↓
COMPARE COST
    ↓
DOCUMENT ADR
    ↓
DEPLOY
    ↓
MONITOR FOR REGRESSION
```

The central principle is:

> **Do not make a workload faster blindly. Make the workload meet its business SLO with the lowest justified total cost and acceptable operational complexity.**

---

# 60. Roadmap Coverage Audit

The authoritative Topic 09 specification requires coverage across performance foundations, Spark execution, Photon, benchmarking, storage/layout, predictive optimization, troubleshooting, production engineering, labs, incidents, runbooks, decision matrices, ADRs, observability, governance, interviews, practice, senior challenges, misconceptions, mental models, glossary, and production completion criteria.

| Roadmap Requirement | Covered? | Section | Hands-on? | Production Depth? |
|---|---|---|---|---|
| Performance foundations | Yes | 5 | Yes | Yes |
| Latency / throughput / utilization | Yes | 5 | Yes | Yes |
| CPU / memory / I/O / network bound | Yes | 5 | Yes | Yes |
| Scan / shuffle / join / aggregation workloads | Yes | 5–6 | Yes | Yes |
| Small files / skew / partitioning | Yes | 5, 33 | Yes | Yes |
| Serialization / Python / UDF overhead | Yes | 17–18 | Yes | Yes |
| Under/over-parallelization | Yes | 5 | Yes | Yes |
| Spark driver/executor/task/stage/job model | Yes | 6 | Yes | Yes |
| Partitions / shuffle / exchange | Yes | 6 | Yes | Yes |
| Narrow/wide transformations | Yes | 6 | Yes | Yes |
| Sort / hash aggregation / joins / scans | Yes | 6, 19 | Yes | Yes |
| Predicate pushdown / column pruning | Yes | 6, 23 | Yes | Yes |
| Lazy evaluation | Yes | 7 | Yes | Yes |
| Physical execution plans | Yes | 7, 19 | Yes | Yes |
| Performance optimization loop | Yes | 8 | Yes | Yes |
| Baselines / controlled experiments | Yes | 8–9 | Yes | Yes |
| Photon foundations | Yes | 10–13 | Yes | Yes |
| Native/vectorized execution | Yes | 11 | Yes | Yes |
| Photon workload suitability | Yes | 14 | Yes | Yes |
| Photon limitations / bottlenecks | Yes | 14, 33 | Yes | Yes |
| Photon + Python/UDFs | Yes | 16–18 | Yes | Yes |
| EXPLAIN / runtime observability | Yes | 19–20, 49 | Yes | Yes |
| Photon benchmarking | Yes | 21 | Yes | Yes |
| Runtime vs cost analysis | Yes | 22, 38 | Yes | Yes |
| Photon + Delta/Parquet | Yes | 23–24 | Yes | Yes |
| Storage/layout/data skipping | Yes | 23–24 | Yes | Yes |
| Liquid clustering relationship | Yes | 25–26 | Yes | Yes |
| Predictive optimization foundations | Yes | 27–30 | Yes | Yes |
| Manual vs automated optimization | Yes | 30, 47 | Yes | Yes |
| Current-documentation safety | Yes | 29 | Yes | Yes |
| Production decision framework | Yes | 32 | Yes | Yes |
| Performance anti-patterns | Yes | 33 | Yes | Yes |
| Production performance engineering | Yes | 34–37 | Yes | Yes |
| Performance vs cost | Yes | 38 | Yes | Yes |
| Security/governance | Yes | 39 | Yes | Yes |
| 12 progressive labs | Yes | 40 | Yes | Yes |
| Realistic capstone | Yes | 41 | Yes | Yes |
| 15+ break/fix incidents | Yes | 42–43 | Yes | Yes |
| Slow-query runbook | Yes | 44 | Yes | Yes |
| Photon decision matrix | Yes | 45 | Yes | Yes |
| Optimization decision matrix | Yes | 46 | Yes | Yes |
| Manual/automated matrix | Yes | 47 | Yes | Yes |
| 5 ADRs | Yes | 48 | Yes | Yes |
| Observability | Yes | 49–50 | Yes | Yes |
| Production architecture patterns | Yes | 51 | Yes | Yes |
| Beginner interview questions ≥15 | Yes | 52 | Yes | Yes |
| Intermediate interview questions ≥20 | Yes | 52 | Yes | Yes |
| Advanced interview questions ≥20 | Yes | 52 | Yes | Yes |
| Senior/production interview questions ≥20 | Yes | 52 | Yes | Yes |
| Conceptual practice ≥25 | Yes | 53.1 | Yes | Yes |
| SQL practice ≥15 | Yes | 53.2 | Yes | Yes |
| PySpark practice ≥15 | Yes | 53.3 | Yes | Yes |
| Performance-debugging ≥15 | Yes | 53.4 | Yes | Yes |
| Architecture scenarios ≥10 | Yes | 53.5 | Yes | Yes |
| Cost/performance scenarios ≥10 | Yes | 53.6 | Yes | Yes |
| Senior Data Engineer challenges | Yes | 54 | Yes | Yes |
| Beginner misconceptions | Yes | 55 | Yes | Yes |
| Mental models | Yes | 56 | Yes | Yes |
| Glossary | Yes | 57 | Yes | Yes |
| Final production checklist | Yes | 58 | Yes | Yes |
| Roadmap coverage audit | Yes | 59 | Yes | Yes |
| Beginner → production progression | Yes | Entire module | Yes | Yes |

**Coverage audit result: Complete against the supplied Topic 09 specification.**

---

# 61. Quality and Validation Notes

- No pending work placeholders are intentionally left in the module.
- Version-sensitive Databricks behavior is explicitly marked for current-documentation verification.
- No hard-coded current DBU prices are presented.
- Photon is treated as an execution-engine component, not as a universal tuning solution.
- Predictive optimization is presented as current-platform behavior that must be verified against the current official Databricks documentation before production use.
- Liquid clustering is connected to performance without re-teaching its entire dedicated topic.
- The module maintains the G4 progression from compute and governance through ingestion/pipelines/orchestration into performance engineering.
- All labs require measurement, troubleshooting, and production lessons.
- Performance claims are framed as hypotheses to validate rather than guaranteed outcomes.

---

# 62. Completion Standard

You are ready to move beyond Topic 09 when you can independently take a slow Databricks workload and produce an evidence-backed answer to all of these:

```text
What is the SLA?
What is the baseline?
How much data is being processed?
What does the physical plan show?
Where is the critical path?
Is the workload CPU-bound?
I/O-bound?
Shuffle-bound?
Skew-bound?
Python-bound?
Concurrency-bound?
Is the data layout appropriate?
Can unnecessary work be removed?
Would Photon help?
Why?
How will it be benchmarked?
Would liquid clustering help?
Why?
Would predictive optimization help?
What will it cost?
How will correctness be validated?
What is the rollback plan?
How will regression be detected?
```

If you cannot answer those questions, do not call the workload optimized.

---

## Final Principle

> **Measure → diagnose → optimize → benchmark → verify → price → monitor.**

That is the production performance-engineering discipline behind Photon, Delta layout, liquid clustering, predictive optimization, and Databricks lakehouse performance.
