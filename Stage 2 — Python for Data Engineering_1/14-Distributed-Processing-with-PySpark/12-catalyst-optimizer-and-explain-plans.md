# Catalyst Optimizer and Explain Plans

> **Module 2.14 — Distributed Processing with PySpark · Phase D — Performance Internals · Topic 12**

## 1. Learning Objectives

By the end of this topic, you should be able to:

- explain what Catalyst is and why Spark needs an optimizer;
- explain why DataFrame and SQL code is not executed exactly as written;
- trace Spark code through unresolved logical, analyzed logical, optimized logical, physical planning, selected physical execution, and code generation;
- use `df.explain()` with `simple`, `extended`, `formatted`, `cost`, and `codegen`;
- read physical-plan trees and identify `FileScan`, `Filter`, `Project`, `Exchange`, `BroadcastExchange`, `SortMergeJoin`, `BroadcastHashJoin`, `HashAggregate`, `Sort`, and `Window`;
- distinguish `PushedFilters`, `PartitionFilters`, and `ReadSchema`;
- explain predicate pushdown, partition pruning, projection pruning, constant folding, filter combination, and join reordering;
- explain Parquet pushdown and why some expressions cannot be pushed down;
- explain how Python UDFs affect optimizer visibility;
- explain whole-stage code generation and `*(n)` markers at a high level;
- explain Tungsten at the level required for production data engineering;
- explain cost-based optimization, table statistics, column statistics, and `ANALYZE TABLE ... COMPUTE STATISTICS`;
- explain how statistics can influence join strategy;
- recognize unnecessary exchanges, repeated scans, missing pushdown, Cartesian products, excessive reads, and unexpected join strategies;
- compare Spark planning with DuckDB, Polars, and PostgreSQL at a conceptual level;
- predict plans before running queries;
- rewrite queries based on plan evidence;
- measure whether a rewrite actually improved the workload;
- prepare for Topic 13, Adaptive Query Execution, without confusing planning-time optimization with runtime re-optimization.

## 2. Why Query Optimization Matters

A Spark program is a description of a computation. It is not a promise that Spark will execute every source-code statement in source order.

For example:

```python
result = (
    orders
    .filter("country = 'IN'")
    .select("customer_id", "amount")
    .groupBy("customer_id")
    .sum("amount")
)
```

The source code describes the intended computation. Spark can analyze the complete computation and choose a physical strategy.

The professional workflow is therefore:

```text
WRITE QUERY
    ↓
PREDICT PLAN
    ↓
EXPLAIN PLAN
    ↓
READ PLAN
    ↓
IDENTIFY BOTTLENECK
    ↓
REWRITE / TUNE
    ↓
EXPLAIN AGAIN
    ↓
RUN
    ↓
MEASURE
    ↓
COMPARE
```

The key habit is:

> **Read the plan before guessing.**

Do not start performance tuning with "add more executors." First determine what Spark believes it needs to do.

## 3. What Is Catalyst?

Catalyst is Spark SQL's query-planning and optimization framework.

At a practical level, Catalyst takes a structured representation of a DataFrame or SQL computation and transforms it through planning stages before execution.

Think of it as the bridge between:

```text
Spark SQL / DataFrame API
        ↓
query representation
        ↓
analysis
        ↓
logical optimization
        ↓
physical planning
        ↓
selected physical plan
        ↓
execution
```

Catalyst matters because Spark has more information about a structured expression than it would have about arbitrary imperative code.

That information allows Spark to reason about operations such as:

- filters;
- projections;
- joins;
- aggregations;
- expressions;
- grouping;
- sorting;
- windows;
- scans.

Do not think of Catalyst as a single optimization rule. It is a framework containing analysis, transformation, optimization, and planning machinery.

The exact set and ordering of rules is Spark-version-sensitive. This topic focuses on the reasoning patterns you need as a Data Engineer rather than memorizing internal rule names.

## 4. Why Spark Needs an Optimizer

Without optimization, a declarative query could be executed in a much less efficient form than necessary.

Consider:

```python
df.filter(F.col("country") == "IN").select("customer_id")
```

The user cares about the result.

Spark can reason about:

- whether filtering can happen before unnecessary work;
- which columns are actually needed;
- whether the filter can reach the storage layer;
- whether a constant expression can be simplified;
- how joins and aggregations should be implemented.

This is the central distinction:

```text
What the user asked for
        ≠
The exact sequence of operations Spark must execute
```

The optimizer attempts to preserve semantics while improving the execution strategy.

Optimization is not a guarantee of faster execution. It creates opportunities for better execution. The workload, statistics, data source, configuration, and runtime conditions still matter.

## 5. From PySpark Code to Execution

A useful end-to-end mental model is:

```text
Python DataFrame / SQL code
        ↓
Parsed / constructed representation
        ↓
Unresolved logical plan
        ↓
Analysis
        ↓
Analyzed logical plan
        ↓
Logical optimization
        ↓
Optimized logical plan
        ↓
Physical planning
        ↓
Candidate physical plans
        ↓
Selected physical plan
        ↓
Code generation / execution mechanisms
        ↓
Tasks on executors
```

This is the journey you should learn to inspect.

The source code is the starting point.

The physical plan is the operational blueprint.

Actual runtime behavior is still influenced by execution-time information and runtime mechanisms, including AQE, which is the subject of Topic 13.

## 6. Catalyst Planning Pipeline

The planning pipeline can be summarized as:

```text
Unresolved Logical Plan
        ↓
Analysis
        ↓
Analyzed Logical Plan
        ↓
Optimized Logical Plan
        ↓
Physical Planning
        ↓
Selected Physical Plan
        ↓
Code Generation / Execution
```

Each stage answers a different question.

| Stage | Core question |
|---|---|
| Unresolved logical plan | What operations did the query request, before names/types are fully resolved? |
| Analysis | What do the referenced columns, tables, functions, and types mean? |
| Analyzed logical plan | What is the resolved relational computation? |
| Optimization | Can the logical computation be rewritten into an equivalent, more efficient form? |
| Physical planning | Which executable operator strategies can implement the logical computation? |
| Selected physical plan | Which physical strategy was selected from available alternatives? |
| Execution/code generation | How will the selected operators execute on the cluster? |

Do not confuse logical optimization with physical execution.

Do not confuse Catalyst's planning-time work with AQE's runtime re-optimization.

## 7. Unresolved Logical Plans

An unresolved logical plan represents the requested computation before all references have been fully resolved.

For example:

```sql
SELECT customer_id, SUM(amount)
FROM orders
GROUP BY customer_id
```

At this stage Spark still needs to resolve things such as:

- which relation `orders` refers to;
- which attributes correspond to `customer_id` and `amount`;
- data types;
- function resolution;
- grouping semantics.

The unresolved representation is useful because it separates **what was requested** from **how it will execute**.

### Important mental model

```text
SQL / DataFrame intent
        ↓
unresolved logical structure
        ↓
analysis
```

You generally do not need to manipulate unresolved plans directly as a normal Data Engineer. You need to understand where they fit in the pipeline.

## 8. Analysis

Analysis resolves the meaning of the logical plan.

Conceptually, Spark answers:

- Does this column exist?
- Which relation owns this attribute?
- Is the reference ambiguous?
- What is the data type?
- Is this function valid?
- Is the expression type-compatible?
- Does the grouping expression make sense?

A failure such as:

```text
cannot resolve ...
```

is an analysis problem, not a physical-performance problem.

### Debugging principle

Classify the failure before changing configuration.

```text
Analysis error
    ↓
inspect names / schema / types / functions

Performance problem
    ↓
inspect logical and physical plan / runtime evidence
```

This classification prevents wasted tuning effort.

## 9. Analyzed Logical Plans

An analyzed logical plan has resolved attributes and expressions.

The plan now represents the relational computation with names and types resolved.

A simplified conceptual example:

```text
Aggregate
  grouping = customer_id
  aggregate = sum(amount)
        |
     Filter
     country = 'IN'
        |
      Scan orders
```

This is still a logical description.

It does not yet tell you exactly whether Spark will:

- broadcast a join;
- sort;
- shuffle;
- use a particular scan strategy;
- use a particular aggregation implementation.

Those questions belong to physical planning.

## 10. Optimized Logical Plans

The optimizer can rewrite the analyzed logical plan while preserving semantics.

Examples include:

- predicate pushdown;
- projection pruning;
- constant folding;
- combining compatible filters;
- join reordering when applicable;
- eliminating redundant operations;
- other optimizer rules supported by the Spark version.

Example:

```text
Before:

Project(customer_id, amount)
  |
Filter(country = 'IN')
  |
Scan(all columns)


After logical optimization:

Project(customer_id, amount)
  |
Filter(country = 'IN')
  |
Scan(only required columns)
```

The exact optimized plan depends on the query, data source, configuration, statistics, and Spark version.

Do not memorize one expected plan as universal truth.

## 11. Predicate Pushdown

Predicate pushdown means moving a filter as close to the data source as safely possible.

Suppose:

```python
df.filter(F.col("country") == "IN")
```

If the source supports the predicate, Spark may be able to communicate that condition to the scan.

Conceptually:

```text
Without useful pushdown:

Storage
  ↓
read many rows
  ↓
Spark Filter
  ↓
remaining rows


With pushdown:

Storage
  ↓
source-aware filtering
  ↓
fewer rows enter Spark
```

Benefits can include:

- fewer records read;
- less I/O;
- less CPU;
- less downstream data processing.

### Important qualification

Not every filter is pushable.

Pushdown depends on:

- data source;
- expression;
- data type;
- function;
- connector capability;
- Spark version.

An empty `PushedFilters` list is a signal to investigate, not automatically a bug.

## 12. Parquet Pushdown and Partition Pruning

Parquet and other file-based sources can expose different forms of filtering behavior.

Two concepts must be kept separate:

### Predicate pushdown

A filter may be communicated to the data source or file reader.

### Partition pruning

Spark may avoid entire directory/table partitions based on partition-column predicates.

These are not the same thing.

A physical scan can contain information such as:

```text
PartitionFilters: [...]
PushedFilters: [...]
ReadSchema: struct<...>
```

Read them independently.

### Parquet and row-group behavior

Parquet can use file metadata and supported filtering mechanisms to avoid unnecessary data at lower levels, subject to the exact expression and implementation.

Do not claim that every filter becomes row-group skipping.

### Cast example

A predicate such as:

```python
df.filter(F.col("event_date") == F.lit("2026-01-01"))
```

may behave differently from a predicate that transforms the partition column:

```python
df.filter(F.to_date(F.col("event_timestamp")) == F.lit("2026-01-01"))
```

Whether pruning/pushdown occurs depends on schema, source, expression, and optimizer capabilities.

The lesson is to inspect the plan rather than assume.

## 13. Projection Pruning

Projection pruning means Spark avoids carrying or reading columns that are not needed.

Suppose a table has:

```text
100 columns
```

but the query needs:

```text
customer_id
amount
country
```

A good scan should avoid unnecessary columns when the source and plan permit it.

Look for:

```text
ReadSchema
```

in the physical plan.

### Why it matters

Unnecessary columns increase:

- I/O;
- memory;
- serialization;
- network movement;
- CPU work.

### Practical habit

Write:

```python
df.select("customer_id", "amount", "country")
```

when those are the only columns needed.

Do not assume Spark can always eliminate every unnecessary column across arbitrary custom functions. Custom expressions can change visibility and requirements.

## 14. Constant Folding

Constant folding evaluates expressions whose values can be determined without reading row data.

For example:

```python
F.lit(10) + F.lit(20)
```

does not need to be recomputed for every row.

Conceptually:

```text
10 + 20
  ↓
30
```

The optimizer can simplify constant expressions before runtime.

This is a small example of a larger principle:

> Spark can often perform work once during planning instead of repeatedly during row processing.

Do not expect every expression to be folded. The expression must be deterministic and safely reducible under Spark's semantics.

## 15. Filter Combination

Multiple filters can sometimes be combined into a more compact logical representation.

For example:

```python
df.filter(F.col("country") == "IN")   .filter(F.col("amount") > 100)
```

can conceptually become:

```text
Filter:
country = 'IN' AND amount > 100
```

This does not mean every source-code rewrite produces an identical visible physical plan.

The important skill is recognizing that the optimizer can reason about equivalent filter predicates rather than blindly preserving the exact DataFrame-call sequence.

## 16. Join Reordering

For multi-table queries, join order can materially affect intermediate data size and execution cost.

Suppose:

```text
A JOIN B JOIN C
```

The optimizer may have opportunities to choose an alternative order when the required semantics and available information permit it.

Join planning can depend on:

- estimated row counts;
- relation sizes;
- join predicates;
- statistics;
- available join strategies;
- configuration;
- optimizer rules.

Do not say:

> "Catalyst always finds the globally optimal join order."

It does not.

The correct mental model is:

> Spark uses available rules and cost information to find a suitable plan within the supported search space.

## 17. Physical Planning

Physical planning translates a logical computation into executable operator strategies.

A logical join such as:

```text
A JOIN B ON A.id = B.id
```

could have different physical implementations.

Examples include:

```text
SortMergeJoin
BroadcastHashJoin
```

depending on the query, statistics, configuration, hints, and available strategies.

Similarly, a logical aggregation can become physical aggregation operators.

The physical plan is therefore where the abstract computation becomes an operational strategy.

## 18. FileScan

A scan is where Spark obtains data from a source.

For file-based data, you may see a scan operator with information about:

- files or relations;
- pushed filters;
- partition filters;
- read schema.

A conceptual example:

```text
FileScan parquet [...]
  PartitionFilters: [...]
  PushedFilters: [...]
  ReadSchema: struct<customer_id:bigint,amount:double>
```

Do not fabricate exact plan output for a specific Spark version.

Your target skill is to recognize the fields and ask:

```text
Where is the data coming from?
How much is being filtered at the source?
Which columns are being read?
Are partitions being pruned?
```

## 19. Filter

A `Filter` operator applies a predicate to rows.

Example:

```python
df.filter(F.col("amount") > 100)
```

A filter appearing in the physical plan does not automatically mean that the storage layer failed to filter.

You may see both:

```text
FileScan
  PushedFilters: [...]
      |
    Filter
```

The scan may apply a source-supported portion while Spark still applies the complete predicate after reading the data.

Always inspect both the scan metadata and the surrounding operators.

## 20. Project

A `Project` operator represents selection and expression computation.

Example:

```python
df.select(
    "customer_id",
    (F.col("amount") * 1.18).alias("gross_amount")
)
```

A project can:

- select columns;
- rename columns;
- compute expressions.

Projection pruning concerns which columns need to travel through the plan and which columns need to be read.

Do not confuse a `Project` operator with physical file-column pruning. The two are related but occur at different conceptual levels.

## 21. Exchange

`Exchange` is one of the most important physical-plan operators to recognize.

Conceptually, it represents a redistribution boundary.

Examples include data redistribution needed for:

- joins;
- aggregations;
- repartitioning;
- ordering requirements.

A shuffle often appears around:

```text
Exchange
```

### Is Exchange always bad?

No.

Some distributed algorithms require data movement.

The correct question is:

> **Why does this Exchange exist, and is it necessary for the requested computation?**

### Investigation questions

- What operator requires the redistribution?
- Is the data being repartitioned unnecessarily?
- Could a better join strategy avoid a large shuffle?
- Is a grouping requiring a shuffle?
- Did an earlier transformation introduce an extra redistribution?

An Exchange is evidence to investigate, not a universal error.

## 22. BroadcastExchange

`BroadcastExchange` represents preparation of a relation for broadcast to relevant executors.

A conceptual join plan can look like:

```text
BroadcastExchange
        |
small relation
        |
BroadcastHashJoin
        |
large relation
```

Broadcast can avoid a full shuffle of the large relation when the strategy is appropriate.

But:

- broadcast is not always better;
- memory matters;
- statistics may be inaccurate;
- configuration matters;
- hints do not make an oversized relation safe.

Always inspect why Spark selected the strategy and verify runtime behavior.

## 23. SortMergeJoin

`SortMergeJoin` is a distributed join strategy commonly used for large equi-joins.

Conceptually:

```text
left
  ↓
shuffle / partition
  ↓
sort
  ↓
       SortMergeJoin
  ↑
sort
  ↑
shuffle / partition
  ↑
right
```

The exact physical tree depends on the query and Spark version.

A SortMergeJoin is not inherently a performance failure.

It may be appropriate when:

- both relations are large;
- broadcasting is unsuitable;
- the join keys support the required strategy.

The engineering question is whether the selected strategy is appropriate for the actual data.

## 24. BroadcastHashJoin

`BroadcastHashJoin` can be appropriate when one side of a join is small enough to broadcast safely.

Conceptually:

```text
small side
   ↓
BroadcastExchange
   ↓
BroadcastHashJoin ← large side
```

Potential advantage:

- avoid shuffling the large side for the join.

Potential risks:

- broadcasting too much data;
- memory pressure;
- incorrect assumptions about relation size;
- stale statistics.

Do not claim that BroadcastHashJoin is always faster than SortMergeJoin.

## 25. HashAggregate

`HashAggregate` represents hash-based aggregation execution where the selected physical strategy supports it.

A grouped aggregation may show:

```text
HashAggregate
    ↑
HashAggregate
    ↑
Exchange
```

The two aggregation operators are often a partial/final pattern.

### Partial aggregation

Combines values locally before redistribution where possible.

### Final aggregation

Combines the redistributed partial results.

This can reduce the amount of data that must cross the shuffle boundary.

Do not interpret the two operators as two separate queries.

## 26. Partial and Final Aggregation

A common aggregation pattern is:

```text
Scan
  ↓
Partial Aggregate
  ↓
Exchange
  ↓
Final Aggregate
```

Why?

Suppose many rows on one executor contribute to the same group.

Local partial aggregation can reduce:

```text
many input rows
```

into:

```text
fewer intermediate aggregate states
```

before the Exchange.

This is an important distributed-computation pattern.

When reading a plan, ask:

> Is Spark aggregating locally before shuffling?

Do not assume that every aggregation will have exactly this visible shape.

## 27. Sort

`Sort` represents an ordering requirement.

Sorting can be expensive because it can involve:

- CPU work;
- memory;
- spill;
- redistribution when global ordering requires it.

Sorts may appear for:

- explicit ordering;
- join strategies;
- window operations;
- other physical requirements.

A `Sort` is not automatically unnecessary.

Ask:

- Why is the sort required?
- Is it local or part of a broader distributed requirement?
- Can the upstream plan already provide the required ordering?
- Is the query requesting an expensive global ordering?

## 28. Window

Window functions operate over ordered or partitioned row sets.

Example:

```python
from pyspark.sql.window import Window

w = Window.partitionBy("customer_id").orderBy("event_timestamp")

result = df.withColumn(
    "running_amount",
    F.sum("amount").over(w)
)
```

When reading a plan containing a window operation, consider:

- partitioning requirements;
- sorting requirements;
- data movement;
- cardinality;
- memory and spill behavior.

Window operations can be expensive because the physical execution may require data to be partitioned and ordered appropriately.

## 29. Explain Modes

PySpark provides several explain modes. The exact formatting can vary by Spark version.

### `simple`

```python
df.explain("simple")
```

Useful for a concise physical-plan view.

### `extended`

```python
df.explain("extended")
```

Useful for seeing multiple planning stages, including parsed, analyzed, optimized, and physical representations.

### `formatted`

```python
df.explain("formatted")
```

Useful for structured physical-plan inspection.

### `cost`

```python
df.explain("cost")
```

Useful when you need plan information together with cost/statistics information that Spark has available.

### `codegen`

```python
df.explain("codegen")
```

Useful for inspecting generated-code information for supported portions of the plan.

### Important rule

Do not treat one mode as universally "best."

Use the mode that answers the question you are investigating.

## 30. Reading `explain("formatted")`

For production plan reading, `formatted` is often a useful starting point because it separates operators and their attributes more clearly.

Use this workflow:

```python
df.explain("formatted")
```

Then annotate:

1. scan;
2. `ReadSchema`;
3. `PartitionFilters`;
4. `PushedFilters`;
5. projections;
6. filters;
7. every `Exchange`;
8. join strategy;
9. aggregation stages;
10. sorts;
11. windows;
12. Python execution;
13. final output.

### Plan annotation framework

Use:

```text
OPERATOR:
WHY IT EXISTS:
INPUT DATA:
DATA MOVEMENT:
EXPECTED CARDINALITY:
MEMORY RISK:
OPTIMIZATION OPPORTUNITY:
RUNTIME EVIDENCE:
```

The goal is not to memorize plan text. It is to reconstruct the dataflow.

## 31. UDFs and Optimizer Visibility

Topic 11 established that Python UDFs can reduce Spark's visibility into custom computation.

This matters here because the plan can expose a Python evaluation boundary instead of a native expression tree.

Compare conceptually:

```text
Built-in expression
    ↓
Spark-native expression
    ↓
optimizer can reason about expression semantics
```

with:

```text
Python UDF
    ↓
custom Python boundary
    ↓
less semantic visibility into the implementation
```

Potential consequences include reduced opportunities for:

- predicate pushdown through the custom computation;
- expression simplification;
- code generation across the boundary;
- other expression-level optimizations.

Do not say that a UDF disables all Catalyst optimization. Surrounding parts of the query can still be optimized.

This is the bridge from Topic 11 to this topic.

## 32. Whole-Stage Code Generation

Whole-stage code generation allows Spark to combine compatible operators into generated JVM code.

A physical plan may contain markers such as:

```text
*(1)
*(2)
*(3)
```

At a high level, the marker indicates participation in a code-generated execution stage.

Conceptually:

```text
multiple compatible operators
        ↓
generated JVM code
        ↓
less interpretation / fewer intermediate objects
        ↓
CPU-efficient execution
```

Do not treat `*(n)` as a guarantee of identical execution behavior across Spark versions.

Use it as a clue that code generation is involved.

### Why it matters

For supported native Spark operations, code generation can reduce overhead associated with interpreting each operator independently.

A Python UDF creates a boundary that is not simply fused into the same JVM-generated expression code.

## 33. Tungsten

Tungsten refers to Spark's execution-engine work focused on efficient use of CPU and memory.

At the roadmap-required level, connect Tungsten with:

- compact/binary-oriented data representations;
- memory efficiency;
- CPU efficiency;
- efficient execution;
- whole-stage code generation.

Do not describe Tungsten as a separate optimizer.

A useful distinction is:

```text
Catalyst
→ query analysis / logical optimization / physical planning

Tungsten-related execution work
→ efficient physical execution and resource utilization
```

These are related parts of Spark's overall execution architecture, not interchangeable names.

## 34. Cost-Based Optimization

Rule-based optimization applies transformations based on known semantic patterns.

Cost-based optimization (CBO) uses available statistics to help choose among alternatives.

Conceptually:

```text
Rule-based reasoning
        +
available statistics
        ↓
better-informed planning choices
```

Potential inputs include:

- estimated row counts;
- relation sizes;
- distinct counts;
- null information;
- min/max;
- column statistics;
- other available metadata.

CBO is only as useful as the information available to it.

Do not assume:

- every table has statistics;
- every statistic is current;
- every data source exposes the same metadata;
- a cost estimate is a runtime measurement.

## 35. Table and Column Statistics

Statistics help Spark estimate the shape of data.

Possible information includes:

- table/row-count estimates;
- relation size;
- distinct counts;
- null counts;
- min/max;
- average or maximum length where applicable;
- other column-level information supported by the environment.

### `ANALYZE TABLE`

A commonly used command is:

```sql
ANALYZE TABLE orders COMPUTE STATISTICS;
```

Column statistics can be requested using syntax appropriate to the supported Spark/catalog environment.

Always verify the exact command and catalog capabilities for the Spark version and table provider in use.

### Why stale statistics matter

Suppose a table used to be small but is now much larger.

If planning information still suggests the old size, a join strategy chosen from stale estimates may be unsuitable.

Statistics are inputs to planning, not guarantees of runtime truth.

## 36. Statistics and Join Strategies

Consider a join:

```text
fact JOIN dimension
```

If Spark estimates that `dimension` is small enough and the relevant conditions are satisfied, a broadcast-based strategy may become attractive.

Conceptually:

```text
Large + small
    ↓
BroadcastHashJoin
```

If both sides are large or broadcasting is unsuitable:

```text
Large + large
    ↓
SortMergeJoin
```

The actual choice can depend on:

- estimates;
- statistics;
- broadcast configuration;
- join predicates;
- hints;
- available strategies;
- Spark version.

### Catalyst vs AQE

Keep the distinction clear:

```text
Catalyst / planning
→ uses information available before execution

AQE
→ can re-optimize during execution using runtime statistics
```

Topic 13 teaches AQE deeply. Do not duplicate it here.

## 37. Plan Anti-Patterns

### Anti-pattern 1 — Extra Exchange

Multiple Exchanges may indicate unnecessary redistribution.

Investigate why each exists before removing anything.

### Anti-pattern 2 — Repeated Scans

The same large source is scanned repeatedly.

Possible causes include:

- separate branches;
- repeated actions;
- query structure;
- missing reuse;
- intentionally repeated reads.

Investigate before recommending caching.

### Anti-pattern 3 — Missing Pushdown

Example:

```text
PushedFilters: []
```

when you expected source filtering.

Treat this as a diagnostic signal.

### Anti-pattern 4 — Cartesian Product

Recognize:

```text
CartesianProduct
```

A missing join condition can accidentally create a Cartesian product.

### Anti-pattern 5 — Huge Sort

Large sorting requirements can create substantial CPU, memory, and spill costs.

### Anti-pattern 6 — Unexpected Join Strategy

A `SortMergeJoin` may deserve investigation when a dimension appears small enough for broadcast.

Do not force a broadcast without verifying data size, statistics, configuration, and memory safety.

### Anti-pattern 7 — Python UDF Barrier

A Python UDF may appear where a Spark-native expression would provide greater optimizer visibility.

### Anti-pattern 8 — Excessive Data Read

A large `ReadSchema` or absent pruning can indicate that too much data is being read.

The correct response is plan investigation, not automatic configuration changes.

## 38. Comparing Spark, DuckDB, Polars, and PostgreSQL Plans

The learner has already encountered query engines outside Spark. Compare planning concepts rather than re-teaching those systems.

| Engine | Planning concept | Optimizer | Physical execution |
|---|---|---|---|
| Spark | logical/physical plans | Catalyst | distributed |
| DuckDB | logical/physical planning | optimizer | vectorized local/embedded execution |
| Polars | lazy logical plan | query optimizer | vectorized/local or streaming execution depending on mode |
| PostgreSQL | planner/executor plan | cost-based planner | database execution |

### Spark

```text
DataFrame / SQL
    ↓
Catalyst
    ↓
logical + physical planning
    ↓
distributed execution
```

### DuckDB

```text
SQL / relational API
    ↓
planning / optimization
    ↓
vectorized local execution
```

### Polars

```text
lazy query
    ↓
optimized logical plan
    ↓
physical execution
```

### PostgreSQL

```text
SQL
    ↓
planner / optimizer
    ↓
execution plan
    ↓
executor
```

The transferable skill is:

> **Understand what the engine plans to do before assuming what it will do.**

## 39. Plan-Driven Debugging

Use:

```text
SYMPTOM
  ↓
READ PLAN
  ↓
IDENTIFY OPERATOR
  ↓
IDENTIFY DATA MOVEMENT
  ↓
IDENTIFY DATA VOLUME
  ↓
FORM HYPOTHESIS
  ↓
CHANGE ONE THING
  ↓
READ PLAN AGAIN
  ↓
RUN
  ↓
MEASURE
```

Suppose:

> "The job became 3× slower."

Do not immediately say:

> "Increase executors."

Instead investigate:

- Did the plan change?
- Did the join strategy change?
- Did pushdown disappear?
- Did an Exchange appear?
- Did an Exchange multiply?
- Did statistics change?
- Did partition pruning disappear?
- Did a UDF get introduced?
- Did `ReadSchema` expand?
- Did the data volume change?

### Plan problem vs data problem

A plan can be appropriate while the data changed dramatically.

Conversely, the data can remain stable while a query rewrite changes the plan.

Separate:

```text
plan evidence
+
data characteristics
+
runtime evidence
```

before deciding what to fix.

## 40. Hands-On Labs

> These are exercise specifications only. The roadmap requires work under `experiments/plans/`, but this document does not create or modify that directory.

### Lab 1 — Ten Query Plan Prediction Set

Choose ten representative queries.

For each:

1. write the query;
2. predict major operators;
3. predict pushdown;
4. predict whether an Exchange is required;
5. predict the join strategy;
6. run `explain("formatted")`;
7. compare prediction with reality;
8. explain every difference.

### Lab 2 — Filter + Select

Use:

```python
df.filter(F.col("country") == "IN").select(
    "customer_id",
    "amount",
)
```

Predict:

- scan;
- filters;
- read schema;
- project.

Then inspect the plan.

### Lab 3 — Filter + Aggregation

Build:

```python
(
    df.filter(F.col("country") == "IN")
      .groupBy("customer_id")
      .agg(F.sum("amount").alias("total_amount"))
)
```

Identify:

- partial aggregation;
- Exchange;
- final aggregation.

### Lab 4 — Small Dimension Join

Join a large fact relation to a deliberately small dimension.

Inspect whether the selected plan uses a broadcast strategy.

Do not assume the result; verify it.

### Lab 5 — Two Large Tables

Join two large relations.

Identify:

- Exchange;
- sorting requirements;
- join strategy;
- input schemas.

### Lab 6 — Window Function

Create a customer running-total window.

Identify:

- partitioning;
- ordering;
- sort;
- window operator.

### Lab 7 — UDF Filter

Compare:

```python
df.filter(normalize_udf(F.col("phone")) == "123")
```

with a native equivalent where available.

Inspect the plan and identify the Python boundary.

### Lab 8 — Partitioned Parquet Filter

Write partitioned test data.

Filter on the partition column.

Inspect:

```text
PartitionFilters
PushedFilters
ReadSchema
```

Explain the difference.

### Lab 9 — Multiple Filters

Build several chained filters.

Inspect whether the logical plan represents them as a combined predicate.

### Lab 10 — Multi-Table Join

Join three relations.

Predict join order and strategies.

Compare with the optimized and physical plans.

### Lab 11 — Pushdown-Breaking Experiment

Implement a native filter and a UDF-based filter.

Compare the scan metadata.

Record measured bytes read rather than inventing a number.

### Lab 12 — Cast on Partition Column

Create a safe partition-column example where a cast changes pruning/pushdown behavior.

Compare plans.

### Lab 13 — Projection Pruning

Compare:

```python
df.select("*")
```

with:

```python
df.select("customer_id", "amount")
```

Inspect `ReadSchema`.

### Lab 14 — Statistics and Join Strategy

Create a controlled dataset.

Collect appropriate statistics where supported.

Compare the plan before and after statistics become available.

Record the actual result.

### Lab 15 — Extra Exchange Investigation

Find a query with multiple Exchanges.

For each Exchange, answer:

- Why is it there?
- Which operator requires it?
- Is it semantically necessary?
- Can the query be rewritten?
- Did the rewrite actually reduce runtime?

---

## 41. Plan Reading Exercises

For every exercise:

```text
PREDICT FIRST
    ↓
RUN EXPLAIN
    ↓
READ PLAN
    ↓
COMPARE
    ↓
EXPLAIN DIFFERENCES
```

### Exercise 1 — Filter + Select

```python
q = df.filter(F.col("country") == "IN").select(
    "customer_id",
    "amount",
)
q.explain("formatted")
```

**Questions**

- What is the scan?
- What is `ReadSchema` expected to contain?
- Where should filtering appear?
- What pushdown evidence should you inspect?

**Answer guidance:** Expect a scan and filter/project structure, but verify exact output for your Spark version and source.

### Exercise 2 — Filter + Aggregation

```python
q = (
    df.filter(F.col("country") == "IN")
      .groupBy("customer_id")
      .agg(F.sum("amount").alias("total"))
)
q.explain("formatted")
```

**Questions**

- Is there an Exchange?
- Is there partial aggregation?
- Where does the final aggregation occur?

**Answer guidance:** Grouping commonly requires redistribution unless the input already satisfies the required partitioning; inspect the actual plan.

### Exercise 3 — Small Dimension Join

```python
q = fact.join(dim, "customer_id")
q.explain("formatted")
```

**Questions**

- Which relation is smaller?
- Is a BroadcastExchange present?
- Which join strategy was selected?
- Are statistics available?

**Answer guidance:** Do not assume broadcast. Verify size estimates, configuration, and the actual plan.

### Exercise 4 — Two Large Tables

```python
q = left.join(right, "customer_id")
q.explain("formatted")
```

**Questions**

- Where are Exchanges?
- Are sorts present?
- Is SortMergeJoin selected?

**Answer guidance:** A large equi-join can use SortMergeJoin, but the exact plan is data/configuration/version-dependent.

### Exercise 5 — Window

```python
w = Window.partitionBy("customer_id").orderBy("event_timestamp")

q = df.withColumn(
    "running_amount",
    F.sum("amount").over(w),
)
q.explain("formatted")
```

**Questions**

- What partitioning is required?
- What ordering is required?
- Is a sort visible?

**Answer guidance:** Window execution commonly requires the input to satisfy partition/order requirements.

### Exercise 6 — UDF Filter

```python
q = df.filter(normalize_phone(F.col("phone")) == "123456")
q.explain("formatted")
```

**Questions**

- Where does Python execution appear?
- Can the phone normalization be pushed into the storage scan?
- What native alternative might exist?

**Answer guidance:** A Python UDF is opaque to the storage layer compared with a supported native predicate.

### Exercise 7 — Partitioned Parquet

```python
q = (
    spark.read.parquet("/data/events")
    .filter(F.col("country") == "IN")
)
q.explain("formatted")
```

**Questions**

- Where should `PartitionFilters` appear?
- What is the difference from `PushedFilters`?
- What does `ReadSchema` tell you?

**Answer guidance:** Partition pruning concerns file/directory partitions; pushed filters concern predicates communicated to the scan.

### Exercise 8 — Multiple Filters

```python
q = (
    df.filter(F.col("country") == "IN")
      .filter(F.col("amount") > 100)
      .filter(F.col("status") == "PAID")
)
q.explain("extended")
```

**Questions**

- How does the optimized logical plan represent the predicates?
- Can the predicates be combined?
- Which parts may reach storage?

**Answer guidance:** Predicate combination is distinct from storage pushdown.

### Exercise 9 — Projection Pruning

```python
q = df.select("customer_id", "amount")
q.explain("formatted")
```

**Questions**

- What is the ReadSchema?
- Are unrelated columns still required?
- What happens if a custom Python function consumes the entire row?

**Answer guidance:** The latter can increase required columns depending on the expression and API.

### Exercise 10 — Multi-Table Join

```python
q = (
    orders
    .join(customers, "customer_id")
    .join(products, "product_id")
)
q.explain("formatted")
```

**Questions**

- What is the join order?
- What are the join strategies?
- Where are Exchanges?
- What statistics could influence planning?

**Answer guidance:** Explain the actual plan instead of assuming the source-code join order is the physical order.

---

## 42. Break Pushdown on Purpose

### Experiment A — UDF in Filter

Compare:

```python
native = df.filter(
    F.regexp_replace("phone", "[^0-9]", "") == "123456"
)
```

with:

```python
udf_version = df.filter(
    normalize_phone(F.col("phone")) == "123456"
)
```

Inspect:

```python
native.explain("formatted")
udf_version.explain("formatted")
```

Questions:

- Which version gives Spark more semantic information?
- What happens near the scan?
- Can the custom Python operation be communicated to the file source?
- What data-reduction opportunities are lost?

### Experiment B — Cast on a Partition Column

Create a partitioned dataset with a simple typed partition column.

Compare:

```python
df.filter(F.col("country") == "IN")
```

with a deliberately transformed/cast partition predicate.

Inspect `PartitionFilters`.

Do not assume that every cast prevents pruning. The purpose is to learn to verify.

### Experiment C — Select Many Columns

Compare:

```python
df.select("*")
```

with:

```python
df.select("customer_id", "amount")
```

Inspect `ReadSchema`.

Measure actual bytes read where your environment exposes the metric.

---

## 43. Performance Measurement

Use an evidence table:

| Metric | Before | After |
|---|---:|---:|
| Runtime | measured | measured |
| Bytes read | measured | measured |
| Shuffle read | measured | measured |
| Shuffle write | measured | measured |
| Peak memory | measured | measured |
| Task duration | measured | measured |

Never fabricate these values.

### Measurement protocol

1. Verify correctness.
2. Use the same dataset.
3. Use the same Spark configuration.
4. Use comparable partitioning.
5. Use the same action.
6. Warm up where appropriate.
7. Run more than once when appropriate.
8. Record variability.
9. Compare plans.
10. Compare runtime evidence.
11. Explain why the plan changed.
12. Decide whether the change is worth keeping.

### Plan improvement vs runtime improvement

A plan can look cleaner without producing a measurable runtime improvement.

Conversely, a plan difference that looks small can matter substantially at scale.

Therefore:

```text
Plan evidence
+
Runtime evidence
=
Production conclusion
```

---

## 44. Production Plan Review Checklist

Before deploying a major Spark query:

- [ ] Read `explain("formatted")`.
- [ ] Identify all major scans.
- [ ] Check `ReadSchema`.
- [ ] Check `PartitionFilters`.
- [ ] Check `PushedFilters`.
- [ ] Identify every `Exchange`.
- [ ] Determine why each Exchange exists.
- [ ] Identify join strategies.
- [ ] Verify expected broadcast behavior where appropriate.
- [ ] Check for accidental Cartesian products.
- [ ] Check partial/final aggregation.
- [ ] Check expensive sorts.
- [ ] Check window operations.
- [ ] Look for repeated scans.
- [ ] Look for Python UDF execution.
- [ ] Check statistics when CBO matters.
- [ ] Compare the plan against expected behavior.
- [ ] Run representative workload tests.
- [ ] Record runtime evidence.
- [ ] Document any intentional anti-patterns.

### Plan annotation framework

For every important operator, record:

```text
Operator:
Purpose:
Input:
Output:
Data movement:
Estimated size:
Statistics:
Memory implication:
Why it exists:
Could it be removed?
Could it be reduced?
Runtime evidence:
```

This turns plan reading into an auditable engineering process.

## 45. Common Misconceptions

### 1. "Spark executes DataFrame lines exactly in order."

**Correct mental model:** DataFrame calls build a computation that Spark can analyze and optimize before execution.

### 2. "The physical plan is the same as the logical plan."

**Correct mental model:** The logical plan describes relational intent; the physical plan describes executable strategies.

### 3. "`explain()` executes the full query."

**Correct mental model:** Explain is primarily a planning/introspection operation. Do not use it as a substitute for a real workload action.

### 4. "`formatted` is always the only useful explain mode."

**Correct mental model:** Different modes answer different questions.

### 5. "Every filter is automatically pushed to storage."

**Correct mental model:** Pushdown depends on the source and expression.

### 6. "`PushedFilters` means partition pruning."

**Correct mental model:** `PushedFilters` and `PartitionFilters` describe different mechanisms.

### 7. "`PartitionFilters` and `PushedFilters` mean the same thing."

**Correct mental model:** Partition pruning can avoid entire partitions; pushed filters communicate supported predicates to the scan.

### 8. "`Exchange` always means a bug."

**Correct mental model:** Distributed joins, aggregations, and other operations can legitimately require redistribution.

### 9. "Every Exchange means the entire dataset is shuffled."

**Correct mental model:** Interpret the specific exchange and its dataflow rather than assuming the largest possible movement.

### 10. "`BroadcastHashJoin` is always better."

**Correct mental model:** Broadcast is appropriate only when the data size, memory, configuration, and workload make it suitable.

### 11. "`SortMergeJoin` is always slower."

**Correct mental model:** It can be an appropriate large-scale join strategy.

### 12. "`HashAggregate` means only one aggregation happens."

**Correct mental model:** A physical plan can contain partial and final aggregation operators.

### 13. "Partial and final aggregates mean two separate queries."

**Correct mental model:** They are execution stages for one logical aggregation.

### 14. "A plan with fewer lines is always faster."

**Correct mental model:** Plan readability and line count are not performance metrics.

### 15. "If Catalyst optimized it, performance is guaranteed."

**Correct mental model:** Optimization creates better opportunities; runtime depends on actual data and execution conditions.

### 16. "Statistics are always accurate."

**Correct mental model:** Statistics can be missing, stale, incomplete, or unsuitable for a particular data source.

### 17. "`ANALYZE TABLE` fixes every join problem."

**Correct mental model:** Statistics improve planning information but do not guarantee a specific strategy or runtime result.

### 18. "UDFs always completely disable Catalyst."

**Correct mental model:** UDFs reduce visibility into the custom computation; surrounding parts of the plan can still be optimized.

### 19. "Code generation means Spark never interprets anything."

**Correct mental model:** Code generation applies to supported portions of execution and is not a universal statement about the entire application.

### 20. "Tungsten is the same thing as Catalyst."

**Correct mental model:** Catalyst focuses on query planning/optimization; Tungsten-related work concerns efficient execution.

### 21. "AQE and Catalyst are the same thing."

**Correct mental model:** Catalyst plans before execution; AQE can re-optimize during execution using runtime information.

### 22. "A better-looking plan always means a faster job."

**Correct mental model:** Validate with representative runtime measurements.

---

## 46. Practice Questions

Exactly **40** questions: 10 Basic, 10 Moderate, 10 Hard, 10 Advanced.

### 46.1 Basic — 10 Questions

1. What problem does Catalyst solve?
2. What is a logical plan?
3. What is an unresolved logical plan?
4. What happens during analysis?
5. What is an optimized logical plan?
6. What is a physical plan?
7. What does `df.explain("formatted")` help you inspect?
8. What is an `Exchange`?
9. What is the difference between `PushedFilters` and `PartitionFilters`?
10. Why should you read a plan before tuning a Spark job?

### 46.2 Moderate — 10 Questions

11. Explain the difference between logical optimization and physical planning.
12. What does a `FileScan` tell you about data access?
13. Why is `ReadSchema` important?
14. What is projection pruning?
15. What is predicate pushdown?
16. Why can a Python UDF reduce optimizer visibility?
17. What is the purpose of a partial aggregation?
18. When might Spark choose `BroadcastHashJoin`?
19. Why can a window operation require sorting?
20. When would you use `extended` instead of `simple` explain output?

### 46.3 Hard — 10 Questions

21. A query reads 100 columns but only returns 4. What plan evidence would you inspect?
22. A filter appears in the plan but `PushedFilters` is empty. What possibilities would you investigate?
23. A query suddenly contains an additional `Exchange`. How would you determine whether it is necessary?
24. Why can stale statistics influence join planning?
25. Explain how a UDF can affect pushdown without making the entire query unoptimizable.
26. A three-table join performs poorly. Which plan operators and statistics would you inspect?
27. How would you distinguish partition pruning from predicate pushdown in a Parquet plan?
28. What does a partial/final aggregation pattern tell you about distributed execution?
29. Why can a physical plan change even when SQL text is unchanged?
30. Why is a plan comparison insufficient without runtime measurement?

### 46.4 Advanced — 10 Questions

31. Design a plan-review method for a five-billion-row fact pipeline.
32. A broadcast join becomes a sort-merge join after a table grows. Explain the planning factors that could cause the change.
33. Design an investigation for a 10× increase in bytes read.
34. How would you prove that a rewrite improved a plan rather than merely changed its appearance?
35. Design a statistics strategy for a production Spark data platform.
36. A query has repeated scans of the same large source. Design a root-cause investigation before recommending caching.
37. Design a plan-driven debugging workflow that separates logical, physical, and runtime problems.
38. Compare Spark planning with DuckDB, Polars, and PostgreSQL without reducing the comparison to "all are optimizers."
39. Design a production policy for reviewing `Exchange`, join, scan, pushdown, and UDF operators.
40. Explain how Catalyst planning prepares the system for AQE without replacing AQE.

---

## 47. Interview Practice

Exactly **40** interview questions: 10 Basic, 10 Moderate, 10 Hard, 10 Advanced.

### 47.1 Basic — 10 Questions

1. What is Catalyst?
   - **Answer guidance:** Spark SQL's query analysis, optimization, and physical-planning framework.

2. Why doesn't Spark simply execute DataFrame statements in source order?
   - **Answer guidance:** DataFrame/SQL APIs describe a declarative computation that Spark can analyze and optimize before execution.

3. What is an unresolved logical plan?
   - **Answer guidance:** A logical representation before references such as attributes, relations, functions, and types are fully resolved.

4. What is analysis?
   - **Answer guidance:** Resolving names, relations, types, functions, and expression semantics.

5. What is an optimized logical plan?
   - **Answer guidance:** A semantically equivalent logical representation after optimizer transformations.

6. What is a physical plan?
   - **Answer guidance:** An executable strategy using concrete physical operators.

7. What does `explain("formatted")` provide?
   - **Answer guidance:** A structured view of physical-plan operators and their attributes, subject to Spark version.

8. What is an Exchange?
   - **Answer guidance:** A redistribution boundary used when downstream execution requires data to be repartitioned or otherwise exchanged.

9. What is predicate pushdown?
   - **Answer guidance:** Communicating supported filter conditions closer to the data source.

10. What is `ReadSchema`?
    - **Answer guidance:** The schema/columns that the scan plans to read.

### 47.2 Moderate — 10 Questions

11. Explain the Catalyst planning pipeline.
    - **Answer guidance:** Unresolved logical → analysis → analyzed logical → optimized logical → physical planning → selected physical plan → execution/code generation.

12. What is projection pruning?
    - **Answer guidance:** Eliminating unnecessary columns from the computation and, where supported, from the scan.

13. What is constant folding?
    - **Answer guidance:** Evaluating safe constant expressions during planning instead of repeatedly at runtime.

14. Why can filters be combined?
    - **Answer guidance:** Spark can represent logically compatible predicates together and optimize the resulting expression.

15. Why does join order matter?
    - **Answer guidance:** Intermediate data size and available strategies can change substantially depending on join order.

16. What is `BroadcastExchange`?
    - **Answer guidance:** Preparation of a relation for broadcast execution.

17. Why can `SortMergeJoin` be appropriate?
    - **Answer guidance:** It can handle large distributed equi-joins without requiring a small side to fit a broadcast strategy.

18. What are partial and final aggregations?
    - **Answer guidance:** Local aggregation can reduce data before redistribution; final aggregation combines the redistributed partial results.

19. What are `PushedFilters`?
    - **Answer guidance:** Predicates communicated to the scan/source when supported.

20. What are `PartitionFilters`?
    - **Answer guidance:** Predicates used for partition pruning, distinct from generic source predicate pushdown.

### 47.3 Hard — 10 Questions

21. Why can a Python UDF reduce optimizer visibility?
    - **Answer guidance:** Spark cannot generally inspect arbitrary Python implementation semantics the way it can inspect native expressions.

22. How would you investigate `PushedFilters: []`?
    - **Answer guidance:** Check the source, predicate shape, data types, casts/functions, connector support, and Spark version before calling it a defect.

23. How would you diagnose an unexpected SortMergeJoin?
    - **Answer guidance:** Inspect estimates, statistics, relation sizes, broadcast configuration, join predicates, hints, and actual data.

24. Why can stale statistics produce a poor physical plan?
    - **Answer guidance:** Planning decisions are based partly on estimated sizes/cardinalities; stale estimates can misrepresent the current workload.

25. Explain whole-stage code generation.
    - **Answer guidance:** Compatible physical operators can be combined into generated JVM code, reducing some interpretation/intermediate-object overhead.

26. What is the relationship between Catalyst and Tungsten?
    - **Answer guidance:** Catalyst focuses on query planning/optimization; Tungsten-related execution work focuses on efficient CPU/memory execution.

27. How would you determine whether an Exchange is unnecessary?
    - **Answer guidance:** Identify the downstream requirement, inspect partitioning/distribution needs, test a semantically equivalent rewrite, compare plan and runtime.

28. How do you distinguish a plan problem from a data problem?
    - **Answer guidance:** Compare plan structure, input size/distribution, statistics, and runtime metrics across the same and changed datasets.

29. Why can a query plan change without changing SQL text?
    - **Answer guidance:** Statistics, configuration, Spark version, source metadata, catalog state, hints, and other planning inputs can change.

30. Why must plan analysis be combined with runtime measurement?
    - **Answer guidance:** A plan is a prediction/strategy; actual workload characteristics determine realized performance.

### 47.4 Advanced — 10 Questions

31. Design a production plan-review process.
    - **Answer guidance:** Standardize formatted-plan review, annotate scans/filters/exchanges/joins/aggregates, validate statistics, benchmark representative data, and record decisions.

32. How would you design a statistics strategy for a large Spark platform?
    - **Answer guidance:** Identify important tables/columns, establish refresh rules, monitor staleness, understand catalog/source limitations, and validate planning impact.

33. A query reads 10× more data than yesterday. Walk through your investigation.
    - **Answer guidance:** Compare plans, ReadSchema, partition filters, pushed filters, source/table changes, statistics, partition layout, and actual data volume.

34. A query contains five Exchanges. How do you determine whether that is a problem?
    - **Answer guidance:** Map each Exchange to the operator requirement; distinguish necessary redistribution from avoidable repartitioning.

35. How would you evaluate a join rewrite?
    - **Answer guidance:** Compare logical intent, physical join strategy, Exchanges/sorts, statistics, runtime, and correctness.

36. How would you explain CBO to an engineering team without promising perfect plans?
    - **Answer guidance:** CBO uses available estimates to make better-informed choices; missing or stale statistics and runtime reality still limit accuracy.

37. Why can a UDF be a plan anti-pattern even when its runtime function is simple?
    - **Answer guidance:** It can hide semantics from Spark and prevent opportunities available to native expressions.

38. How would you build a cross-engine plan-reading skill?
    - **Answer guidance:** Compare the common lifecycle—logical representation, optimization, physical strategy, execution—while respecting each engine's architecture.

39. How should Topic 12 prepare an engineer for AQE?
    - **Answer guidance:** Teach what Catalyst plans before execution and how to read those decisions; Topic 13 then explains runtime re-optimization using observed statistics.

40. What does "production-level plan literacy" mean?
    - **Answer guidance:** The ability to predict, inspect, explain, challenge, rewrite, benchmark, and document Spark execution plans using evidence.

---

## 48. Architecture Scenarios

### Scenario 1 — Nightly Job Suddenly Reads 10× More Data

Investigate:

- `ReadSchema`;
- `PartitionFilters`;
- `PushedFilters`;
- partition layout;
- source data growth;
- plan changes;
- statistics.

Do not immediately increase cluster size.

### Scenario 2 — Join Changes from Broadcast to Sort-Merge

Investigate:

- estimated relation sizes;
- current table statistics;
- broadcast configuration;
- actual data size;
- join predicates;
- hints;
- Spark version/configuration.

Record whether the change is expected.

### Scenario 3 — Query Contains Multiple Exchanges

Annotate every Exchange:

```text
Exchange #1 → why?
Exchange #2 → why?
Exchange #3 → why?
```

Determine which are required by joins, aggregation, repartitioning, ordering, or other distribution requirements.

### Scenario 4 — Gold Aggregation Has Huge Shuffle Volume

Inspect:

- partial aggregation;
- Exchange;
- group cardinality;
- input volume;
- unnecessary columns;
- upstream filters;
- skew.

Do not assume the aggregation operator itself is the root cause.

### Scenario 5 — Filter Is Not Pushed into Parquet

Investigate:

- predicate expression;
- casts/functions;
- source capability;
- partition filters;
- pushed filters;
- Spark version.

Rewrite only when semantics remain correct.

### Scenario 6 — UDF Prevents Efficient Scan Filtering

Compare:

```text
native predicate
vs
Python UDF predicate
```

Inspect plan differences and estimate how much data enters the UDF.

### Scenario 7 — Stale Statistics Cause Poor Join Planning

Design:

- statistics collection;
- refresh policy;
- monitoring;
- validation;
- rollback/rewrite strategy.

### Scenario 8 — Standard Production Plan Review

Create an organizational process requiring:

1. formatted plan;
2. scan annotation;
3. filter/pushdown review;
4. Exchange review;
5. join strategy review;
6. aggregation review;
7. UDF review;
8. statistics review;
9. representative benchmark;
10. documented approval.

### Scenario 9 — Repeated Large Scan

Determine whether repeated scans are caused by:

- query branches;
- repeated actions;
- separate jobs;
- missing reuse;
- intentionally independent reads.

Only after diagnosis should caching or another reuse strategy be considered.

### Scenario 10 — Accidental Cartesian Product

A query suddenly contains:

```text
CartesianProduct
```

Investigate:

- join conditions;
- aliases;
- column names;
- accidental cross join;
- data cardinality.

Treat the issue as a correctness and performance risk.

---

## 49. Learning Checkpoints

### Checkpoint 1 — Planning Pipeline

Can you explain:

```text
unresolved
→ analyzed
→ optimized
→ physical
→ selected physical
→ execution
```

without mixing the stages?

### Checkpoint 2 — Explain Modes

Can you choose between:

```python
simple
extended
formatted
cost
codegen
```

based on the question you are trying to answer?

### Checkpoint 3 — Physical Operators

Can you identify:

```text
FileScan
Filter
Project
Exchange
BroadcastExchange
SortMergeJoin
BroadcastHashJoin
HashAggregate
Sort
Window
```

from a physical plan?

### Checkpoint 4 — Scan Efficiency

Can you explain:

```text
PartitionFilters
PushedFilters
ReadSchema
```

without confusing them?

### Checkpoint 5 — Optimization

Can you recognize:

- predicate pushdown;
- projection pruning;
- constant folding;
- filter combination;
- join reordering?

### Checkpoint 6 — Advanced Execution

Can you explain:

- whole-stage code generation;
- `*(n)` markers;
- Tungsten;
- CBO;
- statistics?

### Checkpoint 7 — Performance Engineering

Can you:

- predict a plan;
- inspect the plan;
- identify an anti-pattern;
- rewrite the query;
- re-read the plan;
- measure the workload;
- explain whether the rewrite helped?

---

## 50. Final Assessment

### Part A — Explain the Pipeline

Without notes, explain:

```text
PySpark code
→ unresolved logical plan
→ analysis
→ analyzed logical plan
→ optimized logical plan
→ physical planning
→ selected physical plan
→ execution/code generation
```

### Part B — Plan Reading

Given an actual plan from your environment, identify:

- scan;
- filters;
- projections;
- Exchanges;
- join strategy;
- aggregation;
- sorting;
- window;
- pushdown;
- partition pruning;
- schema being read.

### Part C — Optimization

Given a slow query:

1. predict the cause;
2. inspect the plan;
3. identify one change;
4. rewrite;
5. inspect the new plan;
6. benchmark;
7. document the result.

### Part D — Statistics

Demonstrate:

- why statistics matter;
- how to inspect available statistics;
- how `ANALYZE TABLE ... COMPUTE STATISTICS` fits into the workflow where supported;
- how a join strategy can be affected;
- why statistics are not guarantees.

### Part E — Anti-Patterns

Diagnose:

1. extra Exchange;
2. repeated scan;
3. missing pushdown;
4. Cartesian product;
5. excessive sort;
6. unexpected join;
7. Python UDF barrier;
8. excessive data read.

### Part F — Cross-Engine Reasoning

Explain the common planning idea across:

- Spark;
- DuckDB;
- Polars;
- PostgreSQL.

Do not claim the engines use identical optimizer implementations.

---

## 51. Production Questions

Before approving a major Spark query, ask:

### Data Access

- Where is the data coming from?
- How much data is being read?
- Is `ReadSchema` minimal?
- Are partition filters present where expected?
- Are pushed filters present where supported?

### Data Movement

- Where are the Exchanges?
- Why does each Exchange exist?
- Is any redistribution unnecessary?
- Is a Cartesian product present?

### Joins

- What join strategy was selected?
- Why?
- What statistics influenced it?
- Is broadcasting safe?
- Are the join keys correct?

### Aggregation

- Is there partial aggregation?
- Where is the shuffle?
- Are there unnecessary columns before aggregation?

### Ordering

- Why is a sort required?
- Is a window operation responsible?
- Is the ordering requirement necessary?

### Custom Code

- Is there a Python UDF?
- Could a built-in replace it?
- Does it reduce optimizer visibility?
- How much data enters Python?

### Statistics

- Are statistics available?
- Are they current?
- Are they relevant to the decision?

### Verification

- Did the plan change as intended?
- Did runtime improve?
- Did bytes read improve?
- Did shuffle improve?
- Did memory behavior improve?

---

## 52. Spark 4.x Version Awareness

This roadmap targets:

- Java 17 or 21;
- Python 3.12+;
- PySpark 4.x.

Spark plan output is version-sensitive.

Therefore:

- do not blindly copy Spark 2.x or Spark 3.x plan screenshots;
- do not assume exact operator names or formatting are immutable;
- verify the behavior in the learner's installed Spark version;
- treat examples in this document as conceptual unless actual output was produced in the learner's environment.

The important skill is interpreting the meaning of plan information, not memorizing a particular formatting layout.

---

## 53. Technical Accuracy Rules

Keep these rules active whenever reading a plan:

- Do not guarantee a specific physical plan.
- Do not assume every filter is pushed down.
- Do not confuse partition pruning with predicate pushdown.
- Do not confuse `PushedFilters` with `PartitionFilters`.
- Do not say `Exchange` is always bad.
- Do not say every Exchange means the entire dataset is shuffled.
- Do not say `BroadcastHashJoin` is always better.
- Do not say `SortMergeJoin` is always slower.
- Do not say statistics are always complete or accurate.
- Do not say `ANALYZE TABLE` fixes every join problem.
- Do not say UDFs completely disable Catalyst.
- Do not say code generation guarantees identical runtime behavior.
- Do not treat Tungsten as the optimizer.
- Do not treat AQE as the same thing as Catalyst.
- Do not fabricate plan output.
- Do not fabricate performance numbers.
- Do not infer runtime performance solely from plan appearance.

If behavior depends on:

- Spark version;
- data source;
- configuration;
- statistics;
- dataset size;
- AQE;
- hints;

state that dependency clearly.

---

## 54. Connection to Topic 13 — Adaptive Query Execution

Catalyst plans using information available during planning.

AQE adds a runtime layer:

```text
Catalyst planning
        ↓
initial physical plan
        ↓
execution stages
        ↓
runtime statistics
        ↓
AQE can re-optimize remaining work
```

Keep the distinction:

> **Catalyst is primarily planning-time optimization.**

> **AQE is runtime re-optimization based on observed execution information.**

This topic prepares you to read the initial plan.

Topic 13 will teach how Spark can change execution decisions after runtime statistics become available.

---

## 55. Final Self-Review

- [ ] Catalyst is explained from beginner to advanced.
- [ ] Why Catalyst exists is explained.
- [ ] Complete planning pipeline is explained.
- [ ] Unresolved logical plan is explained.
- [ ] Analysis is explained.
- [ ] Analyzed logical plan is explained.
- [ ] Optimized logical plan is explained.
- [ ] Physical planning is explained.
- [ ] Physical plan selection is explained.
- [ ] Code generation is introduced.
- [ ] `simple` is covered.
- [ ] `extended` is covered.
- [ ] `formatted` is covered.
- [ ] `cost` is covered.
- [ ] `codegen` is covered.
- [ ] `FileScan` is covered.
- [ ] `Filter` is covered.
- [ ] `Project` is covered.
- [ ] `Exchange` is covered.
- [ ] `BroadcastExchange` is covered.
- [ ] `SortMergeJoin` is covered.
- [ ] `BroadcastHashJoin` is covered.
- [ ] `HashAggregate` is covered.
- [ ] Partial/final aggregation is covered.
- [ ] `Sort` is covered.
- [ ] `Window` is covered.
- [ ] Predicate pushdown is covered.
- [ ] `PartitionFilters` are covered.
- [ ] `PushedFilters` are covered.
- [ ] `ReadSchema` is covered.
- [ ] Parquet pushdown is covered.
- [ ] Projection pruning is covered.
- [ ] Constant folding is covered.
- [ ] Filter combination is covered.
- [ ] Join reordering is covered.
- [ ] UDF optimizer impact is covered.
- [ ] Whole-stage code generation is covered.
- [ ] Tungsten is covered.
- [ ] Cost-based optimization is covered.
- [ ] Table statistics are covered.
- [ ] Column statistics are covered.
- [ ] `ANALYZE TABLE` is covered.
- [ ] Statistics and join strategy are covered.
- [ ] Plan anti-patterns are covered.
- [ ] Extra Exchange is covered.
- [ ] Repeated scans are covered.
- [ ] Missing pushdown is covered.
- [ ] Cartesian products are covered.
- [ ] Unexpected join strategies are covered.
- [ ] Excessive data reads are covered.
- [ ] Spark vs DuckDB is covered.
- [ ] Spark vs Polars is covered.
- [ ] Spark vs PostgreSQL is covered.
- [ ] At least 10 plan-reading exercises exist.
- [ ] Pushdown-breaking experiments exist.
- [ ] Performance measurement is included.
- [ ] Plan-driven debugging is included.
- [ ] At least 20 misconceptions exist.
- [ ] Exactly 40 practice questions exist.
- [ ] Exactly 40 interview questions exist.
- [ ] At least 8 architecture scenarios exist.
- [ ] Production plan-review checklist exists.
- [ ] Plan annotation framework exists.
- [ ] Learning checkpoints exist.
- [ ] Final assessment exists.
- [ ] Glossary exists.
- [ ] Spark 4 awareness is maintained.
- [ ] No fabricated plan outputs exist.
- [ ] No fabricated benchmark numbers exist.
- [ ] Topic 13 AQE is prepared for but not duplicated.
- [ ] No unrelated topic is deeply duplicated.

---

## 56. Glossary

**Catalyst** — Spark SQL's framework for analysis, optimization, and physical planning.

**Logical plan** — A relational description of what computation is required.

**Unresolved logical plan** — Logical representation before references and expressions are fully resolved.

**Analysis** — Resolution of relations, attributes, functions, types, and expression semantics.

**Analyzed logical plan** — Logical plan after analysis has resolved its references.

**Optimized logical plan** — Semantically equivalent logical plan after optimization rules are applied.

**Physical plan** — An executable representation using physical operator strategies.

**Physical planning** — Selection of executable strategies for a logical computation.

**FileScan** — Physical scan operation that reads data from a source.

**Filter** — Operator that applies a predicate to rows.

**Project** — Operator that selects or computes output expressions.

**Exchange** — Physical redistribution boundary.

**BroadcastExchange** — Preparation of a relation for broadcast execution.

**SortMergeJoin** — Distributed join strategy involving partitioning and sorting of join inputs.

**BroadcastHashJoin** — Join strategy that broadcasts one side and uses hash-based matching.

**HashAggregate** — Physical aggregation operator using hash-based aggregation.

**Partial aggregation** — Local aggregation before redistribution.

**Final aggregation** — Aggregation that combines redistributed partial results.

**Sort** — Physical ordering operation.

**Window** — Physical execution of window-function requirements.

**Predicate pushdown** — Sending supported filtering predicates closer to the data source.

**Partition pruning** — Avoiding entire table/file partitions using partition predicates.

**Projection pruning** — Eliminating unnecessary columns.

**PushedFilters** — Predicates communicated to a data source/scan when supported.

**PartitionFilters** — Predicates used for partition pruning.

**ReadSchema** — Columns/types the scan plans to read.

**Constant folding** — Evaluating safely reducible constant expressions during planning.

**Join reordering** — Changing join order when semantics and planning information permit it.

**Whole-stage code generation** — Combining compatible physical operators into generated JVM execution code.

**Tungsten** — Spark execution-engine work emphasizing efficient memory and CPU use.

**CBO** — Cost-Based Optimization using available statistics to inform planning decisions.

**Table statistics** — Metadata describing relation size/cardinality and related information.

**Column statistics** — Column-level metadata such as distinct counts, null counts, and supported distribution information.

**`ANALYZE TABLE`** — SQL command used to compute statistics where supported.

**Plan anti-pattern** — A suspicious plan characteristic that warrants investigation.

**AQE** — Adaptive Query Execution; runtime re-optimization using observed execution statistics.

---

## 57. Summary

The most important lesson of Topic 12 is:

> **Spark code is not the final execution strategy. The plan is the bridge between intent and execution.**

Develop the following habit:

```text
Spark code
   ↓
Predict
   ↓
Explain
   ↓
Read
   ↓
Identify data movement
   ↓
Identify data volume
   ↓
Identify operator strategy
   ↓
Rewrite
   ↓
Explain again
   ↓
Run
   ↓
Measure
```

When you see a Spark performance problem, ask:

```text
Where is the data coming from?

How much data is being read?

Are filters being pushed?

Are partitions being pruned?

Are unnecessary columns being read?

Where are the Exchanges?

Why is Spark redistributing data?

What join strategy did Spark select?

Why did Spark select it?

Are statistics available?

Is the aggregation partial and final?

Is there an unnecessary sort?

Is a UDF reducing optimizer visibility?

Is there a Cartesian product?

Are repeated scans occurring?

Can I improve the query rather than blindly increasing cluster resources?

Did the plan actually improve after the rewrite?

Did runtime measurements confirm the improvement?
```

That is plan-driven Spark performance engineering.

---

## 58. Topic Completion Standard

Do not consider this topic complete because you can run:

```python
df.explain()
```

You are ready to move forward only when you can:

1. explain Catalyst;
2. trace the planning pipeline;
3. distinguish unresolved, analyzed, optimized, and physical plans;
4. use all required explain modes;
5. read a formatted physical plan;
6. identify scans and read schemas;
7. distinguish partition pruning from predicate pushdown;
8. identify Exchanges and explain why they exist;
9. identify broadcast and sort-merge joins;
10. recognize partial/final aggregation;
11. identify sorts and windows;
12. explain projection pruning;
13. explain constant folding;
14. explain filter combination;
15. explain join reordering;
16. explain UDF optimizer visibility;
17. explain whole-stage code generation;
18. explain Tungsten at the required level;
19. explain CBO and statistics;
20. recognize common plan anti-patterns;
21. compare Spark planning conceptually with DuckDB, Polars, and PostgreSQL;
22. predict plans before running queries;
23. rewrite a query based on plan evidence;
24. verify the rewrite with a new plan;
25. measure actual runtime impact;
26. explain why the plan changed;
27. prepare for AQE without confusing it with Catalyst.

> **Final professional standard:** You should be able to look at a Spark physical plan and ask, with evidence, **"What is Spark actually going to do?"**
