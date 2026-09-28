# Polars Lazy API and Query Optimization

> **Stage 2 — Python for Data Engineering · Module 2.4 · Topic 03**
>
> A complete, beginner-friendly, production-oriented chapter on Polars lazy execution, query plans, optimizer behaviour, pushdown, pruning, profiling, optimization blockers, and evidence-based performance engineering.

---

# 1. Learning Objectives

By the end of this chapter, you should be able to:

- Explain eager versus lazy execution.
- Explain what a `LazyFrame` represents.
- Use `df.lazy()` and `collect()`.
- Lazily scan Parquet, CSV, NDJSON, and Arrow IPC sources.
- Scan multiple files with globs.
- Inspect a lazy result schema with `collect_schema()`.
- Explain logical plans and physical execution plans.
- Use `explain()` and understand optimized versus unoptimized plans.
- Understand `show_graph()` as a visual plan-inspection tool.
- Explain scan, projection, filter, join, aggregation, sort, and sink nodes.
- Explain predicate, projection, and slice pushdown.
- Explain common subplan elimination, common subexpression elimination, and simplification.
- Explain how lazy planning interacts with Parquet column pruning and row-group skipping.
- Explain Hive-style partitioning and partition pruning.
- Measure bytes read when tooling makes it observable.
- Use `profile()` or the current version-equivalent profiling API.
- Find the dominant runtime bottleneck.
- Identify Python UDFs, early `collect()`, eager conversions, and premature full-dataset operations as possible optimization blockers.
- Understand `pl.collect_all()`.
- Understand and use lazy sinks such as `sink_parquet()`.
- Structure reusable `LazyFrame -> LazyFrame` transformations.
- Unit-test those transformations on tiny in-memory inputs.
- Build the required `lazy_pipeline.py` exercise.
- Prove pushdown with plans and measurements instead of assumptions.
- Distinguish lazy execution from streaming execution.
- Make production-oriented optimization decisions using evidence.

---

# 2. Prerequisites

This chapter builds on:

- Python fundamentals.
- pandas concepts.
- Eager Polars.
- Polars expressions and contexts.
- Apache Arrow fundamentals.
- Basic Parquet concepts.
- Basic Data Engineering pipeline thinking.

The previous topic introduced:

```text
DataFrame
Expression
select()
with_columns()
filter()
group_by().agg()
joins
dtypes
```

This chapter changes the question from:

> "How do I express this transformation?"

to:

> "How can the engine see and optimize the entire transformation before it executes?"

---

# 3. Why Lazy Execution Exists

Imagine a dataset:

```text
10 billion rows
100 columns
```

The business request is:

> Calculate January revenue by customer using only `customer_id`, `amount`, and `created_at`.

A straightforward eager workflow might conceptually do:

```text
Read everything
    ↓
Load many columns
    ↓
Transform
    ↓
Filter to January
    ↓
Keep 3 columns
    ↓
Aggregate
```

A smarter execution strategy may be able to do:

```text
Understand complete query
    ↓
Identify required columns
    ↓
Identify useful filters
    ↓
Prune partitions
    ↓
Skip irrelevant row groups where possible
    ↓
Read less data
    ↓
Filter
    ↓
Aggregate
```

The key problem is:

> You cannot optimize the entire workload well if you execute every statement before seeing the later statements.

Lazy execution lets Polars delay execution and build a larger view of the requested computation.

---

# 4. The Core Mental Model

## Eager

```text
Python statement
      ↓
execute immediately
      ↓
concrete result
```

Example:

```python
import polars as pl

df = pl.DataFrame(
    {
        "customer_id": [1, 2, 3],
        "amount": [100, 200, 300],
    }
)

result = df.filter(
    pl.col("amount") > 100
)
```

After `filter()`, `result` is a concrete DataFrame.

## Lazy

```text
Python expressions
      ↓
build logical query plan
      ↓
optimizer rewrites plan
      ↓
execution strategy
      ↓
execute
      ↓
result
```

Example:

```python
lf = (
    df.lazy()
      .filter(pl.col("amount") > 100)
      .select(["customer_id", "amount"])
)

result = lf.collect()
```

The main idea is:

> **Lazy execution is valuable because Polars can see more of the workload before doing the work.**

This may allow the engine to reduce:

- columns read,
- rows processed,
- repeated computation,
- intermediate materialization,
- source I/O.

It does not guarantee that every query becomes faster.

---

# 5. Eager vs Lazy — Side by Side

| Aspect | Eager | Lazy |
|---|---|---|
| Main object | `DataFrame` | `LazyFrame` |
| Execution | Immediate | Deferred |
| Intermediate result | Materialized | Can remain planned |
| Optimizer visibility | Smaller scope | Larger scope |
| Query-plan inspection | Limited | Central |
| Best fit | Small/simple/debugging tasks | Larger analytical pipelines |
| Final materialization | Already concrete | `collect()` or a sink |

A useful rule:

> Use eager execution when immediate materialized data is what you need. Use lazy execution when whole-query planning can reduce meaningful work.

---

# 6. The Recipe Analogy

Think of lazy execution as reading the entire recipe before cooking.

```text
Recipe
=
query

Ingredients
=
source data/columns

Steps
=
expressions

Kitchen
=
execution engine

Optimization
=
finding unnecessary work before cooking
```

In actual Polars terms:

```text
lazy transformations
      ↓
query plan
      ↓
optimizer
      ↓
execution
```

The analogy is only useful because the engine is actually building and optimizing a representation of the computation.

---

# 7. What Is a `LazyFrame`?

A `LazyFrame` represents a pending computation.

Example:

```python
import polars as pl

df = pl.DataFrame(
    {
        "customer_id": [1, 2, 3],
        "amount": [100, 200, 300],
    }
)

lf = df.lazy()

print(type(df))
print(type(lf))
```

Conceptually:

```text
DataFrame
→ concrete data

LazyFrame
→ description of work to obtain data
```

The exact transformation chain can keep growing:

```python
lf = (
    df.lazy()
      .filter(pl.col("amount") > 100)
      .with_columns(
          (pl.col("amount") * 1.18)
          .alias("gross_amount")
      )
      .select(
          ["customer_id", "gross_amount"]
      )
)
```

No full final result has been requested yet.

---

# 8. `collect()`

`collect()` triggers execution and materializes the lazy result.

```python
result = (
    df.lazy()
      .filter(pl.col("amount") > 100)
      .select(["customer_id", "amount"])
      .collect()
)
```

Think:

```text
LazyFrame
   ↓
plan
   ↓
optimization
   ↓
execution
   ↓
DataFrame
```

This is the main execution lifecycle for the chapter.

---

# 9. Why `collect()` Too Early Can Be Expensive

Bad pattern:

```python
lf = pl.scan_parquet("orders/*.parquet")

lf = lf.filter(
    pl.col("created_at") >= "2026-01-01"
)

df = lf.collect()

df = df.filter(
    pl.col("created_at") < "2026-02-01"
)

df = df.select(
    ["customer_id", "amount"]
)
```

The first `collect()` forced materialization before the later operations were known to the optimizer.

Better:

```python
lf = (
    pl.scan_parquet("orders/*.parquet")
      .filter(
          pl.col("created_at") >= "2026-01-01"
      )
      .filter(
          pl.col("created_at") < "2026-02-01"
      )
      .select(
          ["customer_id", "amount"]
      )
)

result = lf.collect()
```

Now the full pipeline is visible.

### Important nuance

Early materialization is not universally wrong.

It can be justified when:

- an intermediate result is intentionally persisted,
- a downstream library requires materialized data,
- a checkpoint is part of the design,
- a debugging boundary is deliberate,
- independent reuse justifies materialization.

The production rule is:

> **Materialize deliberately, not accidentally.**

---

# 10. Lazy Scanning

Compare:

```python
df = pl.read_parquet("orders.parquet")
```

with:

```python
lf = pl.scan_parquet("orders.parquet")
```

The first is an eager read.

The second creates a lazy scan node.

You can then write:

```python
lf = (
    pl.scan_parquet("orders.parquet")
      .filter(pl.col("amount") > 1000)
      .select(["customer_id", "amount"])
)
```

The source remains inside the pending plan.

---

# 11. Required Lazy Scan APIs

## `scan_parquet`

```python
lf = pl.scan_parquet(
    "data/orders.parquet"
)
```

Especially important because Parquet is columnar and can expose metadata that helps selective reading.

## `scan_csv`

```python
lf = pl.scan_csv(
    "data/orders.csv"
)
```

CSV is row-oriented text and generally provides different optimization opportunities from Parquet.

## `scan_ndjson`

```python
lf = pl.scan_ndjson(
    "data/orders.ndjson"
)
```

Useful for newline-delimited JSON.

## `scan_ipc`

```python
lf = pl.scan_ipc(
    "data/orders.arrow"
)
```

Useful for Arrow IPC inputs where supported by the installed version.

### Version awareness

Polars changes quickly. Always verify the exact API signature and supported options against the version installed in your `uv` environment.

---

# 12. Multi-File Lazy Scanning

Data Engineering systems frequently store data across many files:

```text
orders/
├── 2026-01.parquet
├── 2026-02.parquet
├── 2026-03.parquet
└── ...
```

A glob can create one logical lazy input:

```python
lf = pl.scan_parquet(
    "orders/*.parquet"
)
```

For partitioned data:

```text
orders/
├── year=2025/
│   ├── month=01/
│   └── month=02/
└── year=2026/
    ├── month=01/
    └── month=02/
```

you can scan a broader pattern and use Hive-style partitioning when supported.

---

# 13. What Can Go Wrong With Multi-File Scanning?

Files can drift.

For example:

```text
file A:
amount = Float64

file B:
amount = String
```

A robust pipeline should not blindly assume all files have identical schemas.

Questions to ask:

```text
Are schemas compatible?
Are new columns expected?
Should schema drift fail?
Should columns be aligned?
What is the contract?
```

Keep this topic focused on lazy planning; detailed schema-evolution strategy belongs elsewhere in the Data Engineering roadmap.

---

# 14. `collect_schema()`

Use:

```python
schema = lf.collect_schema()
print(schema)
```

This is useful because it asks:

> What schema will this query produce?

without requiring you to materialize the entire result.

Possible uses:

- schema validation,
- debugging,
- contract checks,
- pipeline development,
- confirming output dtypes.

The important distinction is:

```text
collect_schema()
→ inspect structure

collect()
→ materialize data
```

---

# 15. Example: Schema Before Data

Suppose:

```python
lf = (
    pl.scan_parquet("orders/*.parquet")
      .with_columns(
          (pl.col("amount") * 1.18)
          .alias("gross_amount")
      )
      .select(
          ["customer_id", "gross_amount"]
      )
)
```

You can inspect:

```python
print(lf.collect_schema())
```

before loading all rows.

This is especially helpful when debugging a pipeline over large datasets.

---

# 16. Query Plans

A query plan is a representation of the operations required to produce a result.

For:

```python
lf = (
    pl.scan_parquet("orders/*.parquet")
      .filter(pl.col("amount") > 1000)
      .select(["customer_id", "amount"])
)
```

a simple conceptual plan is:

```text
Scan
  ↓
Filter
  ↓
Projection
```

The exact final plan is the optimizer's job.

Do not confuse this conceptual view with exact plan text.

---

# 17. Logical Plan

A logical plan answers:

> **What operations are needed?**

For example:

```text
scan source
filter rows
select columns
aggregate
```

It is about the requested computation and dependencies.

---

# 18. Physical Execution Plan

A physical execution plan answers:

> **How will the engine execute the logical computation?**

It is closer to implementation:

```text
source scan strategy
join implementation
aggregation execution
sort
materialization/sink
```

You do not need to become a database optimizer researcher in this topic.

You do need to understand:

```text
logical intent
→ optimizer rewrites
→ executable strategy
```

---

# 19. `explain()`

The primary plan inspection tool is:

```python
print(lf.explain())
```

Use it to ask:

```text
What work is planned?
Where is the scan?
Where is the filter?
Which columns are required?
Did the optimizer move operations?
```

When your installed version supports distinct optimized/unoptimized plan views, inspect both.

Do not depend on exact plan formatting because it can change across versions.

---

# 20. Unoptimized vs Optimized Plan

Consider:

```python
lf = (
    pl.scan_parquet("orders/*.parquet")
      .filter(
          pl.col("amount") > 1000
      )
      .select(
          ["customer_id", "amount"]
      )
)
```

Conceptually the initial plan is:

```text
Scan
 ↓
Filter
 ↓
Projection
```

An optimized plan may conceptually behave more like:

```text
Scan
  ├── required columns only
  └── supported predicate pushed toward source
       ↓
remaining execution
```

The important question is not:

> "Does the optimized plan look prettier?"

It is:

> **Does the optimized plan represent less physical work while preserving the same result?**

---

# 21. `show_graph()`

Where supported:

```python
lf.show_graph()
```

can show the query plan visually.

A complex plan can be easier to reason about as:

```text
        Scan
          │
       Filter
          │
      ┌───┴───┐
      │       │
    Join   Lookup
      │       │
      └───┬───┘
          │
      Aggregate
          │
         Sink
```

The exact UI/rendering is version- and environment-dependent.

Learn the graph structure, not one exact screenshot.

---

# 22. Common Plan Operators

## Scan

Reads from a source.

Potential costs:

- I/O,
- parsing,
- decompression,
- file discovery.

## Projection

Chooses required columns.

Potential benefit:

- less data carried forward.

## Filter

Removes rows according to predicates.

Potential benefit:

- fewer rows enter downstream work.

## Join

Combines inputs by keys.

Potential costs:

- memory,
- hashing,
- sorting,
- large intermediate results.

## Aggregation

Summarizes grouped data.

Potential costs:

- grouping state,
- high-cardinality keys.

## Sort

Orders rows.

Potential cost:

- global data movement and memory.

## Sink

Writes the final or intermediate result.

Potential benefit:

- avoids unnecessary full-result materialization.

---

# 23. Predicate Pushdown

A predicate is a condition such as:

```python
pl.col("amount") > 1000
```

Predicate pushdown means:

> Move a compatible filtering operation closer to the source.

Conceptually:

```text
Without useful pushdown

Scan everything
    ↓
Filter
```

versus:

```text
With pushdown

Source / scan
    ↓
apply compatible filter as early as possible
    ↓
continue
```

The objective is to reduce unnecessary:

- rows read,
- rows parsed,
- rows carried,
- downstream CPU,
- memory.

---

# 24. Predicate Pushdown Is Conditional

Never memorize:

> "Polars always pushes filters into the file."

A correct statement is:

> Polars can push compatible predicates toward a source when the optimizer and source reader can safely use them.

Limitations can come from:

- source capability,
- predicate shape,
- data type semantics,
- derived columns,
- unsupported operations,
- Python UDFs,
- query dependencies.

---

# 25. Predicate Pushdown Example

```python
lf = (
    pl.scan_parquet("orders/*.parquet")
      .filter(
          pl.col("created_at") >= "2026-01-01"
      )
)
```

Ask:

```text
Can the source use this predicate?
Is the predicate on a physical/source column?
Can partitions be pruned?
Can Parquet metadata help?
```

Do not assume the answer.

Inspect the plan and measure.

---

# 26. Projection Pushdown

Projection means:

> Which columns are required?

Example:

```python
lf = (
    pl.scan_parquet("orders/*.parquet")
      .select(
          ["customer_id", "amount"]
      )
)
```

Suppose the file contains:

```text
100 columns
```

and the query needs only:

```text
customer_id
amount
```

An efficient reader can potentially avoid reading the other 98 columns.

---

# 27. Why Projection Pushdown Matters

Reducing columns can lower:

- I/O,
- decompression,
- memory,
- CPU,
- object-storage transfer.

This is especially powerful with columnar formats.

A good mental model:

```text
100-column source
       ↓
dependency analysis
       ↓
2-column requirement
       ↓
read only required columns where supported
```

---

# 28. Projection Dependencies

Projection pushdown is not merely:

> Read only the columns visible in `select()`.

Consider:

```python
gross =
    amount * tax_rate
```

If your final query selects:

```text
customer_id
gross
```

the source may need:

```text
customer_id
amount
tax_rate
```

The optimizer must trace dependencies backward.

This is why reading plans is more useful than memorizing rules.

---

# 29. Slice Pushdown

A slice limits the result.

For example:

```python
lf.head(100)
```

asks for only part of the result.

Potentially:

```text
process everything
    ↓
take 100
```

can be reduced to something closer to:

```text
avoid work for rows that cannot reach the first 100
```

when query semantics and source capabilities permit it.

---

# 30. Slice Pushdown and Global Operations

Consider:

```python
lf = (
    pl.scan_parquet("orders/*.parquet")
      .sort("amount", descending=True)
      .head(100)
)
```

You cannot assume that the engine can read only the first 100 physical source rows.

To find the true top 100, the engine may need substantially more input.

Therefore:

> Slice pushdown depends on the operators before it.

---

# 31. Common Subplan Elimination

Suppose:

```text
Query A
  ↓
Scan orders

Query B
  ↓
Scan orders
```

Both may share common work.

A coordinated optimizer can potentially reuse a common portion.

Conceptually:

```text
          shared work
             │
        ┌────┴────┐
        ▼         ▼
      Query A   Query B
```

This is particularly relevant when several lazy queries depend on the same expensive source or computation.

---

# 32. Common Subexpression Elimination

This operates at a smaller level.

Suppose a complex expression appears multiple times:

```text
amount * exchange_rate
```

If the optimizer can safely identify identical shared computation, it may avoid recalculating it.

The principle is:

```text
compute shared expression
        ↓
reuse result
```

Do not assume elimination always happens. Query shape and optimizer implementation matter.

---

# 33. Simplification

Optimizers can also simplify plans and expressions.

Conceptual examples:

```text
x + 0
```

or:

```text
compute field
then immediately discard it
```

may expose unnecessary work.

Optimization is therefore broader than:

```text
push filter
```

It can include:

```text
remove
rewrite
simplify
reuse
push
prune
```

while preserving semantics.

---

# 34. Pushdown Meets Parquet

Parquet is an especially important source for this topic.

A Parquet dataset can expose:

- columnar storage,
- row groups,
- statistics,
- file-level metadata.

A lazy query can provide:

```text
required columns
+
compatible predicates
```

to the reader.

Conceptually:

```text
Lazy query
    ↓
Optimizer
    ↓
required columns + filter information
    ↓
Parquet reader
    ↓
column pruning
    ↓
row-group skipping where safe
```

This is the bridge from query planning to file-layout efficiency.

---

# 35. Parquet Column Pruning

Suppose a file has:

```text
A B C D E F G H
```

but the query requires:

```text
B D
```

A columnar reader can potentially avoid loading:

```text
A C E F G H
```

This is the storage-side manifestation of projection pushdown.

The benefit comes from the combination of:

```text
lazy planning
+
columnar storage
+
source-level support
```

---

# 36. Parquet Row-Group Skipping

Parquet stores data in row groups.

A row group can have statistics such as conceptual:

```text
row group 1:
amount min=0 max=50

row group 2:
amount min=51 max=100

row group 3:
amount min=101 max=200
```

For:

```text
amount > 100
```

the first two groups cannot satisfy the predicate.

The reader may therefore skip them.

This is called row-group skipping.

The actual result depends on the available statistics, predicate semantics, and reader implementation.

---

# 37. Hive-Style Partitioning

A common lake layout is:

```text
lake/
├── year=2025/
│   ├── month=01/
│   └── month=02/
└── year=2026/
    ├── month=01/
    └── month=02/
```

The directory names themselves contain partition values.

This is Hive-style partitioning.

---

# 38. `hive_partitioning=True`

Where supported:

```python
lf = pl.scan_parquet(
    "lake/orders/**/*.parquet",
    hive_partitioning=True,
)
```

This tells the scan to interpret Hive-style directory values.

Then a query such as:

```python
lf = lf.filter(
    (pl.col("year") == 2026)
    & (pl.col("month") == 1)
)
```

may allow partition pruning.

---

# 39. Partition Pruning

Partition pruning answers:

> Which partitions can be eliminated before reading their contents?

Conceptually:

```text
Query:
year=2026 AND month=1
```

Dataset:

```text
year=2025/
year=2026/month=01/
year=2026/month=02/
```

Potential candidate:

```text
year=2026/month=01/
```

This is an earlier level of elimination than reading rows inside files.

---

# 40. Partition Pruning vs Row-Group Skipping

| Mechanism | Level | Evidence used |
|---|---|---|
| Partition pruning | Dataset layout | Partition values in path/layout |
| Row-group skipping | Inside Parquet files | Row-group statistics |
| Projection pushdown | Columns | Dependency analysis |
| Predicate pushdown | Rows/filter logic | Predicate + source capability |

A useful hierarchy:

```text
dataset
  ↓
partition pruning
  ↓
eligible files
  ↓
row-group skipping
  ↓
required columns
  ↓
row-level processing
```

These mechanisms can work together.

---

# 41. Bytes Read

Runtime alone is not sufficient.

For file workloads, useful measurements include:

```text
dataset size
files touched
bytes read
runtime
peak memory
```

A query may be faster because it reads less data.

That is stronger evidence than simply observing a lower runtime once.

---

# 42. Measuring Bytes Carefully

"Bytes read" can mean different things in different tools.

Possible quantities include:

- compressed file bytes,
- decompressed bytes,
- network transfer,
- bytes returned by an object store,
- bytes requested by range reads,
- application-level I/O.

Always ask:

> **What exactly is this metric measuring?**

Do not compare unrelated metrics as if they were identical.

---

# 43. `profile()`

Use:

```python
result = lf.profile()
```

where supported by your installed version.

Profiling is different from plan inspection.

```text
explain()
→ planned work

profile()
→ observed runtime
```

A profile can help identify the operator that actually consumes execution time.

---

# 44. Finding the Slowest Node

Suppose a plan contains:

```text
Scan
  ↓
Filter
  ↓
Join
  ↓
Group By
  ↓
Sort
```

The profile may reveal that one operator dominates runtime.

The workflow becomes:

```text
profile
  ↓
find dominant cost
  ↓
understand cause
  ↓
change design
  ↓
measure again
```

Do not optimize every node equally.

---

# 45. I/O vs CPU vs Memory Bottlenecks

## I/O-heavy

Possible signs:

- large bytes read,
- long scan time,
- remote storage,
- many files.

Investigate:

```text
partition pruning
projection
predicate pushdown
row-group skipping
file layout
```

## CPU-heavy

Possible signs:

- source read is acceptable,
- compute node dominates.

Investigate:

```text
UDFs
joins
sorting
strings
complex expressions
```

## Memory-heavy

Possible signs:

- large intermediate states,
- giant joins,
- global sorting,
- repeated materialization.

Investigate:

```text
projection
filtering
join cardinality
collect()
sink
```

---

# 46. Optimization Blockers

The required blockers are:

1. Python UDFs.
2. Eager conversions in a lazy pipeline.
3. `collect()` inside loops.
4. Full-dataset operations too early.

The common theme:

> **They can prevent the engine from seeing or safely reducing work across the whole pipeline.**

---

# 47. Python UDFs

Example:

```python
lf = (
    pl.scan_parquet("orders/*.parquet")
      .with_columns(
          pl.col("amount")
            .map_elements(
                lambda x: x * 1.18,
                return_dtype=pl.Float64,
            )
            .alias("gross_amount")
      )
      .filter(
          pl.col("status") == "PAID"
      )
)
```

The optimizer understands native operations much better than an arbitrary Python function.

Compare:

```python
pl.col("amount") * 1.18
```

with:

```python
pl.col("amount").map_elements(...)
```

The first exposes a native expression tree.

The second creates a Python callback boundary.

---

# 48. Why UDFs Can Reduce Optimization Opportunities

A Python UDF can introduce:

- Python interpreter overhead,
- callback-per-element work,
- reduced optimizer visibility,
- GIL-related constraints for Python code,
- reduced opportunity for native execution.

This does not mean UDFs are forbidden.

Use them when the logic genuinely cannot be expressed natively.

A strong rule:

```text
Native expression exists?
→ use it.

No native expression exists?
→ isolate UDF, benchmark it, document it.
```

---

# 49. Deliberately Blocking Pushdown

Native version:

```python
native = (
    pl.scan_parquet("orders/*.parquet")
      .filter(
          pl.col("amount") > 100
      )
      .select(
          ["customer_id", "amount"]
      )
)
```

UDF variant:

```python
blocked = (
    pl.scan_parquet("orders/*.parquet")
      .with_columns(
          pl.col("amount")
            .map_elements(
                lambda x: x,
                return_dtype=pl.Float64,
            )
            .alias("amount")
      )
      .filter(
          pl.col("amount") > 100
      )
      .select(
          ["customer_id", "amount"]
      )
)
```

The exact optimizer response depends on the operation and Polars version.

Your job is to inspect both plans and measure them.

---

# 50. Eager Conversions in the Middle

Bad structure:

```text
LazyFrame
   ↓
collect()
   ↓
pandas/DataFrame operation
   ↓
lazy again
   ↓
collect()
```

This introduces a hard boundary.

Better when possible:

```text
LazyFrame
   ↓
native transformation
   ↓
native transformation
   ↓
collect/sink
```

The optimizer can then see more of the computation as one plan.

---

# 51. `collect()` Inside Loops

Potentially problematic:

```python
for customer_id in customer_ids:
    result = (
        pl.scan_parquet("orders/*.parquet")
          .filter(
              pl.col("customer_id") == customer_id
          )
          .collect()
    )
```

This can repeatedly:

- scan,
- plan,
- execute,
- materialize.

Investigate whether the task can instead be expressed as:

```text
one query
grouped query
or coordinated lazy queries
```

The rule is not "never use loops."

The rule is:

> **Repeated execution of a large source can be a serious performance smell.**

---

# 52. Full-Dataset Operations Too Early

Suppose:

```python
lf = (
    pl.scan_parquet("orders/*.parquet")
      .sort("created_at")
      .filter(
          pl.col("status") == "PAID"
      )
)
```

If sorting before filtering is not required for correctness, then:

```python
lf = (
    pl.scan_parquet("orders/*.parquet")
      .filter(
          pl.col("status") == "PAID"
      )
      .sort("created_at")
)
```

may do less sorting work.

The principle is:

> **Reduce the input to expensive operators when semantics permit.**

---

# 53. `pl.collect_all`

If you have multiple lazy queries:

```python
query_a = (
    pl.scan_parquet("orders/*.parquet")
      .filter(pl.col("status") == "PAID")
)

query_b = (
    pl.scan_parquet("orders/*.parquet")
      .filter(pl.col("status") == "CANCELLED")
)
```

coordinated collection with:

```python
pl.collect_all([query_a, query_b])
```

may allow shared work to be reused where the optimizer identifies it.

Do not assume every pair of queries benefits.

The potential benefit depends on common scans and plan structure.

---

# 54. Lazy Sinks

Large output:

```python
result = lf.collect()
result.write_parquet("gold.parquet")
```

This requires a full materialized DataFrame first.

For large outputs, a sink can instead represent:

```text
lazy plan
   ↓
execute
   ↓
write directly
```

This can reduce peak materialization memory.

---

# 55. `sink_parquet`

Conceptual example:

```python
(
    pl.scan_parquet("orders/*.parquet")
      .filter(
          pl.col("status") == "PAID"
      )
      .select(
          ["customer_id", "amount"]
      )
      .sink_parquet(
          "gold/paid_orders.parquet"
      )
)
```

Check the exact current signature in your installed version.

---

# 56. Other Sinks

The roadmap also requires awareness of:

```text
sink_csv
sink_ipc
sink_ndjson
```

Conceptual examples:

```python
lf.sink_csv("output.csv")
```

```python
lf.sink_ipc("output.arrow")
```

```python
lf.sink_ndjson("output.ndjson")
```

The exact APIs can be version-sensitive.

Use sinks when the goal is to materialize to a file and a complete in-memory DataFrame is unnecessary.

---

# 57. `collect()` vs Sink

A useful decision rule:

```text
Need the result as a Python DataFrame?
→ collect()

Need a large output file?
→ sink
```

The decision depends on:

- output size,
- memory,
- downstream consumers,
- need for Python-level inspection.

---

# 58. `LazyFrame → LazyFrame` Functions

A strong production pattern is:

```python
def clean_orders(
    lf: pl.LazyFrame,
) -> pl.LazyFrame:
    return (
        lf
        .filter(
            pl.col("amount") >= 0
        )
        .select(
            [
                "order_id",
                "customer_id",
                "amount",
                "created_at",
            ]
        )
    )
```

Then:

```python
def enrich_orders(
    lf: pl.LazyFrame,
) -> pl.LazyFrame:
    return lf.with_columns(
        (
            pl.col("amount") * 1.18
        ).alias("gross_amount")
    )
```

Compose:

```python
lf = pl.scan_parquet(
    "orders/*.parquet"
)

lf = clean_orders(lf)
lf = enrich_orders(lf)

result = lf.collect()
```

---

# 59. Why `LazyFrame → LazyFrame` Design Works Well

It gives you:

- testability,
- composability,
- optimizer visibility,
- separation of business stages,
- reusable transformations,
- easier maintenance.

A transformation function should generally not call `collect()` unless materialization is explicitly part of that function's contract.

---

# 60. Unit Testing Lazy Transformations

Test with tiny inputs.

```python
import polars as pl
from polars.testing import assert_frame_equal


def filter_paid(
    lf: pl.LazyFrame,
) -> pl.LazyFrame:
    return lf.filter(
        pl.col("status") == "PAID"
    )


def test_filter_paid():
    source = pl.DataFrame(
        {
            "order_id": ["O1", "O2"],
            "status": ["PAID", "CANCELLED"],
        }
    )

    actual = filter_paid(
        source.lazy()
    ).collect()

    expected = pl.DataFrame(
        {
            "order_id": ["O1"],
            "status": ["PAID"],
        }
    )

    assert_frame_equal(
        actual,
        expected,
    )
```

The production design is:

```text
function remains lazy
test controls materialization
```

---

# 61. Testing Correctness vs Testing Optimization

A correctness test asks:

```text
Did I get the right result?
```

A plan inspection asks:

```text
Did the query have the structure I expected?
```

A benchmark asks:

```text
Did that structure actually reduce cost?
```

Therefore:

```text
Correctness
+
Plan inspection
+
Performance measurement
```

is stronger than any one alone.

---

# 62. Why Exact Plan String Assertions Are Brittle

Plan text can change across versions.

Avoid tests such as:

```python
assert lf.explain() == "exact giant string"
```

unless a version-pinned system intentionally requires that contract.

Better:

- inspect plans during development,
- test data semantics with unit tests,
- benchmark critical workloads,
- use lightweight plan assertions only when the project accepts version coupling.

---

# 63. Mandatory Project — `lazy_pipeline.py`

Use a realistic multi-file Parquet dataset such as NYC Taxi data.

Goal:

```text
raw Parquet
    ↓
silver transformations
    ↓
gold transformations
    ↓
Parquet output
```

The project must prove:

```text
optimization
+
correctness
+
measurement
```

---

# 64. Project Architecture

Conceptual structure:

```text
lazy_pipeline/
├── data/
├── src/
│   └── lazy_pipeline.py
├── tests/
└── benchmarks/
```

This section describes architecture only.

The current chapter must not create those additional files.

---

# 65. Project Step 1 — Scan

Start with:

```python
lf = pl.scan_parquet(
    "data/taxi/**/*.parquet",
    hive_partitioning=True,
)
```

Do not start with:

```python
pl.read_parquet(...)
```

The exercise is intentionally about lazy planning.

---

# 66. Project Step 2 — Silver Functions

Use functions such as:

```python
def clean_trips(
    lf: pl.LazyFrame,
) -> pl.LazyFrame:
    ...
```

Possible conceptual flow:

```text
scan
 ↓
typed columns
 ↓
filter invalid rows
 ↓
select required columns
 ↓
deduplicate
 ↓
derive fields
```

Every function should accept and return a `LazyFrame`.

---

# 67. Project Step 3 — Gold Functions

Build metrics such as:

```text
daily trips
daily revenue
zone metrics
```

Example:

```python
gold = (
    silver
    .group_by("zone_id")
    .agg(
        pl.len().alias("trip_count"),
        pl.col("fare_amount")
          .sum()
          .alias("revenue"),
    )
)
```

Keep the pipeline lazy.

---

# 68. Project Step 4 — Explain the Plan

Run:

```python
print(gold.explain())
```

Identify:

```text
scan
filter
projection
join
aggregation
sort
sink
```

For every major node ask:

```text
What does it do?
Why is it needed?
Can less data reach it?
Can it move earlier?
```

---

# 69. Project Step 5 — Prove Projection Pushdown

Create a query that requires only a small set of columns.

For example:

```python
lf = (
    pl.scan_parquet("data/taxi/**/*.parquet")
      .select(
          [
              "PULocationID",
              "fare_amount",
              "pickup_datetime",
          ]
      )
)
```

Inspect the optimized plan.

Then measure I/O when the environment allows it.

Your proof should be based on evidence, not assumptions.

---

# 70. Project Step 6 — Prove Predicate Pushdown

Add a selective date filter:

```python
lf = (
    pl.scan_parquet("data/taxi/**/*.parquet")
      .filter(
          pl.col("pickup_datetime")
          .is_between(
              "2026-01-01",
              "2026-01-31",
          )
      )
)
```

Then inspect:

```python
print(lf.explain())
```

Investigate:

```text
filter placement
partition pruning
row-group skipping
bytes read
```

The actual amount of pruning depends on the physical dataset.

---

# 71. Project Step 7 — Compare Eager vs Lazy

### Eager

```python
df = pl.read_parquet(
    "data/taxi/**/*.parquet"
)

result = (
    df
    .filter(
        pl.col("fare_amount") > 20
    )
    .select(
        ["PULocationID", "fare_amount"]
    )
)
```

### Lazy

```python
result = (
    pl.scan_parquet(
        "data/taxi/**/*.parquet"
    )
    .filter(
        pl.col("fare_amount") > 20
    )
    .select(
        ["PULocationID", "fare_amount"]
    )
    .collect()
)
```

Use the same:

```text
dataset
query
file format
environment
```

---

# 72. Project Step 8 — Block Pushdown With a UDF

Build a native version:

```python
native = (
    pl.scan_parquet(PATH)
      .filter(
          pl.col("fare_amount") > 20
      )
      .select(
          ["PULocationID", "fare_amount"]
      )
)
```

Create an equivalent UDF-based version.

Then compare:

```python
print(native.explain())
print(blocked.explain())
```

and measure:

```text
runtime
peak memory
bytes read where measurable
```

The exact plan output is version-sensitive.

---

# 73. Project Step 9 — Profile

Use the installed API:

```python
profile_result = (
    native
    .profile()
)
```

or the current equivalent.

Identify:

```text
most expensive plan node
```

Then write:

```text
Observed bottleneck:
Why it is expensive:
What I changed:
What happened after:
```

---

# 74. Project Step 10 — Improve

Do not change ten things at once.

Use:

```text
baseline
  ↓
one hypothesis
  ↓
one important change
  ↓
measure
```

Example hypothesis:

> "The join is receiving unnecessary columns."

Change:

```text
project earlier
```

Then measure:

```text
runtime
memory
bytes read
```

---

# 75. Project Step 11 — Sink

If the Gold output is large:

```python
gold.sink_parquet(
    "data/gold/taxi_metrics.parquet"
)
```

rather than:

```python
df = gold.collect()
df.write_parquet(...)
```

when Python does not need the full DataFrame.

---

# 76. Project Step 12 — Unit Test

Each transformation function should accept a tiny DataFrame converted to lazy form:

```python
source.lazy()
```

Then:

```python
result = clean_trips(
    source.lazy()
).collect()
```

Compare against expected output.

Test:

- normal rows,
- empty input,
- nulls,
- duplicates,
- boundary timestamps.

---

# 77. Required Pushdown Experiment

## Experiment A — Native

```text
scan_parquet
      ↓
filter
      ↓
select
```

## Experiment B — UDF

```text
scan_parquet
      ↓
Python UDF
      ↓
filter
      ↓
select
```

For each:

```text
inspect plan
measure runtime
measure bytes read if possible
compare results
```

The lesson:

> **Optimizer-friendly code gives the engine more information about what can be moved or eliminated.**

---

# 78. Required Eager vs Lazy Experiment

Keep constant:

```text
same dataset
same Parquet files
same columns
same predicates
same hardware
same Polars version
```

Measure:

```text
wall time
peak memory
bytes read when measurable
```

Report:

```text
baseline
measurement
interpretation
limitations
```

Never write:

> "Lazy is universally faster."

---

# 79. Benchmark Skeleton

```python
from time import perf_counter

import polars as pl


PATH = "data/taxi/**/*.parquet"


def benchmark(label, fn, repeats=3):
    fn()

    times = []

    for _ in range(repeats):
        start = perf_counter()
        fn()
        times.append(
            perf_counter() - start
        )

    average = sum(times) / len(times)

    print(
        f"{label}: "
        f"avg={average:.6f}s"
    )


def eager_query():
    return (
        pl.read_parquet(PATH)
          .filter(
              pl.col("fare_amount") > 20
          )
          .select(
              ["PULocationID", "fare_amount"]
          )
    )


def lazy_query():
    return (
        pl.scan_parquet(PATH)
          .filter(
              pl.col("fare_amount") > 20
          )
          .select(
              ["PULocationID", "fare_amount"]
          )
          .collect()
    )


benchmark(
    "eager",
    eager_query,
)

benchmark(
    "lazy",
    lazy_query,
)
```

This code generates the measurements.

Do not hard-code expected performance numbers.

---

# 80. Fair Benchmark Requirements

Record:

```text
dataset size
row count
file count
schema
file format
CPU
RAM
Python version
Polars version
cache state where relevant
repetitions
warm-up
```

Avoid comparing:

```text
CSV + pandas
```

with:

```text
Parquet + Polars
```

and attributing all differences to lazy execution.

A fair comparison controls important variables.

---

# 81. Cache Effects

Repeated file reads can be affected by OS and storage caches.

Therefore document:

```text
warm
vs
cold
```

conditions where meaningful.

A benchmark run after previous reads may measure:

```text
cache performance
```

rather than:

```text
storage performance
```

Neither is "wrong"; they answer different questions.

---

# 82. Query-Plan Reading Exercises

For each exercise:

1. Predict the simple logical plan.
2. Inspect the actual plan.
3. Identify possible optimization.
4. Explain the optimization.
5. State what measurement could prove it.

---

## Exercise 1

```python
pl.scan_parquet(PATH)
```

Expected concept:

```text
Scan
```

---

## Exercise 2

```python
pl.scan_parquet(PATH).select(
    ["id", "amount"]
)
```

Expected opportunity:

```text
Projection pushdown
```

---

## Exercise 3

```python
pl.scan_parquet(PATH).filter(
    pl.col("amount") > 100
)
```

Expected opportunity:

```text
Predicate pushdown
```

---

## Exercise 4

```python
(
    pl.scan_parquet(PATH)
      .filter(pl.col("amount") > 100)
      .select(["id", "amount"])
)
```

Expected opportunities:

```text
predicate
+
projection
```

---

## Exercise 5

```python
(
    pl.scan_parquet(PATH)
      .head(100)
)
```

Investigate:

```text
slice pushdown
```

but do not assume only 100 physical rows are read.

---

## Exercise 6

```python
(
    pl.scan_parquet(PATH)
      .sort("amount")
      .head(100)
)
```

Explain why sorting can require substantially more data.

---

## Exercise 7

Two lazy queries share the same source.

Investigate:

```text
common subplan elimination
collect_all
```

---

## Exercise 8

A complex expression is repeated.

Investigate:

```text
common subexpression elimination
```

---

## Exercise 9

A `collect()` appears halfway through a pipeline.

Explain the materialization boundary.

---

## Exercise 10

A Python UDF occurs before a selective predicate.

Explain why this may reduce optimization opportunities.

---

# 83. Debugging Lab

## Problem 1 — `read_parquet()` Used for a Large Pipeline

### Symptom

The pipeline loads the full dataset immediately.

### Likely cause

Eager source ingestion.

### Diagnosis

Inspect the first source call.

### Better approach

Use:

```python
pl.scan_parquet(...)
```

when lazy planning is appropriate.

### Production lesson

The execution model starts at the source.

---

## Problem 2 — `collect()` Too Early

### Symptom

A pipeline has several DataFrame materialization boundaries.

### Cause

Intermediate eager operations.

### Diagnosis

Search for:

```python
.collect()
```

### Fix

Keep compatible transformations inside the LazyFrame.

### Lesson

Preserve plan visibility.

---

## Problem 3 — `collect()` in a Loop

### Symptom

The same large source is processed repeatedly.

### Cause

Per-item materialization.

### Fix

Investigate one consolidated query or coordinated lazy queries.

### Lesson

Repeated execution can dominate simple transformation cost.

---

## Problem 4 — Python UDF Before Filter

### Symptom

A selective filter does not seem to reduce source work as expected.

### Cause

Opaque Python computation before the predicate.

### Fix

Use a native expression if possible.

### Lesson

Native expressions expose semantics.

---

## Problem 5 — Too Many Columns Read

### Symptom

The final result uses 5 columns but source I/O is much larger than expected.

### Diagnosis

Inspect the optimized plan and dependencies.

### Fix

Narrow projections and remove unnecessary derived columns.

---

## Problem 6 — Filter Applied Too Late

### Symptom

An expensive operation processes far more rows than necessary.

### Fix

Move compatible filtering earlier.

### Lesson

Reduce data before expensive operators where semantics permit.

---

## Problem 7 — Partitions Are Not Pruned

### Symptom

A partitioned dataset still touches many directories.

### Diagnosis

Check:

```text
partition layout
hive_partitioning
predicate columns
data types
```

### Fix

Align query predicates with partition semantics.

---

## Problem 8 — Unexpectedly High Bytes Read

### Investigate

```text
projection
predicate
partition pruning
row-group statistics
file count
file layout
cache state
measurement definition
```

---

## Problem 9 — Profiling Shows an Unexpected Bottleneck

### Symptom

You expected scan time to dominate, but a join does.

### Fix

Follow the measured bottleneck.

### Lesson

Your intuition is a hypothesis, not evidence.

---

## Problem 10 — Giant Result Collected

### Symptom

The process runs out of memory while writing a large result.

### Fix

Consider:

```text
sink_parquet
```

or an appropriate output sink.

### Lesson

Do not materialize a large result if no downstream Python code needs it.

---

# 84. Common Mistakes

Avoid:

- using `read_*` instead of `scan_*` when large lazy inputs are appropriate,
- collecting too early,
- assuming the optimizer can inspect arbitrary Python functions,
- optimizing without measuring,
- assuming every filter is pushed to storage,
- assuming pushdown means no bytes are read,
- ignoring file layout,
- ignoring partitions,
- collecting large output unnecessarily,
- running repeated `collect()` calls inside loops,
- treating exact plan strings as version-stable APIs,
- assuming a lazy plan is automatically a streaming plan.

---

# 85. Plan vs Result

Memorize:

```text
same result
    ≠
same execution cost
```

Example:

```text
Query A:
read 1 TB
return 1 GB

Query B:
read 200 GB
return same 1 GB
```

The business result may be identical.

The operational cost is not.

This is why query-plan literacy matters.

---

# 86. Plan vs Profile

Memorize:

```text
explain()
→ What does the plan say?

profile()
→ What took time when it ran?
```

Use:

```text
plan
+
profile
+
I/O
```

for serious optimization.

---

# 87. Lazy vs Streaming

This distinction prepares you for Topic 04.

## Lazy execution

```text
defer execution
+
plan
+
optimize
```

## Streaming

```text
execute the plan in bounded batches/morsels
```

Therefore:

```text
Lazy ≠ Streaming
```

A LazyFrame can be optimized without automatically becoming a streaming execution.

Topic 04 will build on the lazy plan and explain larger-than-RAM execution.

---

# 88. Production Architecture

A realistic design is:

```text
Object Storage
      ↓
Partitioned Parquet
      ↓
scan_parquet()
      ↓
LazyFrame
      ↓
typed transformations
      ↓
filters
      ↓
projection
      ↓
joins
      ↓
aggregations
      ↓
optimizer
      ↓
execution
      ↓
sink_parquet()
      ↓
Gold Dataset
```

The performance outcome depends on all of these layers:

```text
query
+
engine
+
file format
+
file layout
+
storage
+
network
+
hardware
```

---

# 89. Production Optimization Questions

When reviewing a LazyFrame pipeline, ask:

## Source

- Is the source lazy?
- Is the file format suitable for selective reading?
- Is the data partitioned?

## Columns

- Which columns are actually required?
- What dependency columns are needed to compute derived fields?

## Rows

- Which filters are selective?
- Can they move closer to the source?
- Can partitions be pruned?

## Expensive operators

- Is a join receiving unnecessary rows?
- Is a sort necessary?
- Is aggregation receiving unnecessary columns?

## Materialization

- Why is `collect()` here?
- Could a sink be used?
- Is any large intermediate result being materialized unnecessarily?

## Python

- Are there UDFs?
- Can they be rewritten natively?

## Evidence

- What does `explain()` show?
- What does `profile()` show?
- What do I/O measurements show?

---

# 90. Three High-Value Rules

## Read Less

Use:

```text
projection pushdown
predicate pushdown
partition pruning
row-group skipping
```

when supported.

## Do Less

Use:

```text
early filtering
narrow projections
native expressions
avoid repeated computation
avoid unnecessary sorting
avoid repeated scans
```

## Materialize Less

Use:

```text
late collect()
sinks
LazyFrame composition
```

when appropriate.

---

# 91. Performance Trade-Offs

An optimization can improve one resource and worsen another.

Example:

```text
runtime ↓
memory ↑
```

That may or may not be acceptable.

A senior Data Engineer considers:

```text
runtime
+
memory
+
cost
+
concurrency
+
reliability
+
maintainability
```

The correct optimization is the one that fits the production constraints.

---

# 92. Production Scenario — 1 TB Daily Lake Query

Requirement:

```text
query one day from partitioned Parquet
```

Investigate:

```text
partition columns
required columns
selectivity
row-group statistics
file count
remote/local storage
```

Do not begin by rewriting the code blindly.

---

# 93. Production Scenario — Slow Remote Query

If the dataset is on remote object storage, unnecessary reads can mean:

```text
more storage I/O
+
more network transfer
+
higher latency
```

Investigate:

```text
partition pruning
projection
predicate pushdown
file count
cache
```

Cloud billing must be evaluated separately from technical byte counts.

---

# 94. Production Scenario — Large Join

If a join dominates profiling:

```text
inspect cardinality
inspect input widths
inspect input row counts
inspect duplicate keys
inspect pre-join filtering
inspect pre-join projection
```

Reducing the input before the join can be more valuable than micro-optimizing the join itself.

---

# 95. Production Scenario — Large Final Output

If the output is hundreds of GB:

```text
Do I actually need a Python DataFrame?
```

If the answer is no:

```text
lazy plan
   ↓
sink
```

may be a better design.

---

# 96. Version Awareness

Check:

```python
import polars as pl

print(pl.__version__)
```

Verify current documentation for:

- `scan_parquet`,
- `scan_csv`,
- `scan_ndjson`,
- `scan_ipc`,
- `collect_schema`,
- `explain`,
- `show_graph`,
- `profile`,
- `collect_all`,
- sink APIs.

Plan text and optimizer behaviour can change.

Do not hard-code version-specific behaviour into learning notes as universal truth.

---

# 97. Query Optimization as a Discipline

Do not ask:

> "What code looks faster?"

Ask:

> **What work is actually being done?**

Then:

```text
Inspect
  ↓
Measure
  ↓
Find bottleneck
  ↓
Hypothesize
  ↓
Change
  ↓
Measure again
  ↓
Validate correctness
```

This is the core optimization loop.

---

# 98. Query Optimization Report Template

Use this for your own lab:

```markdown
## Workload

Dataset:
Rows:
Files:
Format:

## Baseline

Runtime:
Peak memory:
Bytes read:

## Plan

Main nodes:
Pushdowns:
Pruning:

## Bottleneck

Observed node:
Why it costs:

## Hypothesis

What unnecessary work exists?

## Change

What was modified?

## Result

Runtime:
Peak memory:
Bytes read:

## Correctness

How was equality proven?

## Limitations

What does this experiment not prove?
```

This is a useful professional habit.

---

# 99. Why Your Own Workload Matters

Generic benchmarks may measure:

```text
simple aggregation
```

while your production workload contains:

```text
joins
strings
timestamps
nested values
wide schemas
remote storage
```

The performance relationship can change.

Therefore:

> Use benchmark literature to form hypotheses, but use representative workload measurements to make engineering decisions.

---

# 100. Important Technical Boundaries

Do not overstate:

### Predicate pushdown

It is conditional.

### Projection pushdown

It includes dependency analysis, not only final visible columns.

### Slice pushdown

It may be limited by upstream operations.

### Partition pruning

It depends on matching partition semantics.

### Row-group skipping

It depends on available metadata/statistics.

### UDF blocking

Exact plan changes depend on the function and version.

### `collect_all`

Shared work is workload-dependent.

### Sinks

They reduce materialization in appropriate scenarios; they do not make every pipeline bounded-memory automatically.

---

# 101. Senior Engineer Mental Model

When you see:

```python
lf = (
    pl.scan_parquet(...)
      .filter(...)
      .select(...)
      .join(...)
      .group_by(...)
      .agg(...)
)
```

do not think:

> "This is just a chain of methods."

Think:

```text
SOURCE
  ↓
What columns are needed?
  ↓
What rows are needed?
  ↓
What partitions are needed?
  ↓
What row groups are needed?
  ↓
What work can be reused?
  ↓
What work is opaque?
  ↓
What expensive operators remain?
  ↓
How should the result be materialized?
```

That is query-engine literacy.

---

# 102. Transition to Topic 04

The module progression is:

```text
Topic 02
How to express transformations
        ↓
Topic 03
How to see and optimize the whole transformation
        ↓
Topic 04
How to execute the optimized plan on data larger than RAM
```

Topic 04 builds on:

- `LazyFrame`,
- query plans,
- pushdown,
- sinks.

The next question is:

> How can a good plan execute without requiring the complete input to fit into RAM?

That is the streaming problem.


---

# 103. Required Hands-On Project — Full Specification

The module roadmap's core exercise is a multi-file Parquet pipeline in a realistic Data Engineering setting.

A suitable dataset is:

```text
NYC Taxi trip records
```

or another realistic dataset with several files.

The project should be large enough that you can observe meaningful differences between:

```text
eager reading
lazy reading
optimizer-friendly code
optimization-blocked code
```

Do not fabricate dataset measurements.

---

## 103.1 Project Goal

Build:

```text
Multi-file Parquet
        ↓
Silver LazyFrame transformations
        ↓
Gold LazyFrame transformations
        ↓
Parquet output
```

Then prove:

```text
what the optimizer changed
+
how much work was reduced
+
whether the result stayed correct
```

---

## 103.2 Project Structure

Conceptual structure:

```text
lazy_pipeline/
├── data/
├── src/
│   └── lazy_pipeline.py
├── tests/
└── benchmarks/
```

This is an architecture description only. Do not create those additional files as part of this chapter-generation task.

---

## 103.3 Step 1 — Source Scan

Start with:

```python
import polars as pl

lf = pl.scan_parquet(
    "data/taxi/**/*.parquet",
    hive_partitioning=True,
)
```

Questions:

```text
What source is represented?
What columns exist?
Are partitions encoded in paths?
Can the source be pruned?
```

Do not call `collect()` yet.

---

## 103.4 Step 2 — Inspect Schema

```python
print(lf.collect_schema())
```

Record:

```text
column names
dtypes
partition-derived columns if applicable
```

This creates an early schema checkpoint without requiring the full result.

---

## 103.5 Step 3 — Build Silver Functions

Create functions conceptually like:

```python
def clean_trips(
    lf: pl.LazyFrame,
) -> pl.LazyFrame:
    return (
        lf
        .filter(
            pl.col("fare_amount") >= 0
        )
        .select(
            [
                "pickup_datetime",
                "PULocationID",
                "fare_amount",
                "trip_distance",
            ]
        )
    )
```

Your actual columns depend on the dataset.

The design rule remains:

```text
LazyFrame in
    ↓
native transformations
    ↓
LazyFrame out
```

---

## 103.6 Step 4 — Build Gold Logic

For example:

```python
def build_gold(
    lf: pl.LazyFrame,
) -> pl.LazyFrame:
    return (
        lf
        .group_by("PULocationID")
        .agg(
            pl.len().alias("trip_count"),
            pl.col("fare_amount")
              .sum()
              .alias("revenue"),
        )
    )
```

The Gold stage should remain lazy.

---

## 103.7 Step 5 — Inspect the Plan

```python
print(gold.explain())
```

Annotate it manually:

```text
Source:
__________

Filter:
__________

Projection:
__________

Join:
__________

Aggregate:
__________

Sort:
__________
```

Then ask:

```text
Which operations are before the expensive operations?
Which columns are needed?
Which rows can be eliminated?
What can be pushed toward the source?
```

---

# 104. Pushdown Experiment — Projection

Create a wide source with many columns.

Example:

```python
lf = (
    pl.scan_parquet("data/taxi/**/*.parquet")
      .select(
          [
              "PULocationID",
              "fare_amount",
              "pickup_datetime",
          ]
      )
)
```

The experiment:

```text
source contains many columns
        ↓
query requires only 3
        ↓
inspect plan
        ↓
measure source I/O when possible
```

### Record

```text
Available columns:
Required columns:
Observed plan:
Measured bytes:
Runtime:
Peak memory:
```

### Question

Did the engine have enough information to avoid reading unnecessary columns?

---

# 105. Pushdown Experiment — Predicate

Use a selective predicate:

```python
lf = (
    pl.scan_parquet("data/taxi/**/*.parquet")
      .filter(
          pl.col("pickup_datetime")
          .is_between(
              "2026-01-01",
              "2026-01-31",
          )
      )
)
```

Inspect:

```python
print(lf.explain())
```

Then determine:

```text
Does the filter reach the scan?
Are partitions pruned?
Can row groups be skipped?
How much data is actually read?
```

Do not claim a result before measurement.

---

# 106. Deliberately Blocking Optimization With a Python UDF

Create:

```python
blocked = (
    pl.scan_parquet("data/taxi/**/*.parquet")
      .with_columns(
          pl.col("fare_amount")
            .map_elements(
                lambda x: x,
                return_dtype=pl.Float64,
            )
            .alias("fare_amount_copy")
      )
      .filter(
          pl.col("fare_amount_copy") > 20
      )
)
```

Compare against:

```python
native = (
    pl.scan_parquet("data/taxi/**/*.parquet")
      .filter(
          pl.col("fare_amount") > 20
      )
)
```

Inspect:

```python
print(native.explain())
print(blocked.explain())
```

Then benchmark.

The exact optimizer behaviour is version-sensitive. The purpose is to test how an opaque Python transformation can affect optimization opportunities.

---

# 107. Eager vs Lazy Benchmark

## Eager

```python
def eager_query():
    df = pl.read_parquet(
        "data/taxi/**/*.parquet"
    )

    return (
        df
        .filter(
            pl.col("fare_amount") > 20
        )
        .select(
            [
                "PULocationID",
                "fare_amount",
            ]
        )
    )
```

## Lazy

```python
def lazy_query():
    return (
        pl.scan_parquet(
            "data/taxi/**/*.parquet"
        )
        .filter(
            pl.col("fare_amount") > 20
        )
        .select(
            [
                "PULocationID",
                "fare_amount",
            ]
        )
        .collect()
    )
```

Benchmark both under the same conditions.

---

# 108. Benchmarking Code

```python
from time import perf_counter

import polars as pl


PATH = "data/taxi/**/*.parquet"


def benchmark(
    label: str,
    fn,
    repeats: int = 3,
) -> list[float]:
    # Warm-up
    fn()

    times: list[float] = []

    for _ in range(repeats):
        start = perf_counter()
        fn()
        elapsed = perf_counter() - start
        times.append(elapsed)

    average = sum(times) / len(times)

    print(
        f"{label}: "
        f"average={average:.6f}s"
    )

    return times


def eager_query():
    return (
        pl.read_parquet(PATH)
        .filter(
            pl.col("fare_amount") > 20
        )
        .select(
            [
                "PULocationID",
                "fare_amount",
            ]
        )
    )


def lazy_query():
    return (
        pl.scan_parquet(PATH)
        .filter(
            pl.col("fare_amount") > 20
        )
        .select(
            [
                "PULocationID",
                "fare_amount",
            ]
        )
        .collect()
    )


eager_times = benchmark(
    "eager",
    eager_query,
)

lazy_times = benchmark(
    "lazy",
    lazy_query,
)
```

The code produces actual values.

Do not write fixed expected timing numbers into your notes.

---

# 109. Benchmark Record

For every serious run record:

```text
Date:
Machine:
CPU:
RAM:
OS:
Python:
Polars:
Dataset:
Rows:
Files:
Columns:
File format:
Cache condition:
Repetitions:
Eager times:
Lazy times:
Peak memory:
Bytes read:
```

Then write:

```text
Observation:
Possible mechanism:
Evidence:
Limitation:
```

---

# 110. Cold vs Warm Effects

Repeated reads can be affected by:

- operating-system file cache,
- storage cache,
- filesystem cache,
- one-time initialization.

Therefore distinguish, where meaningful:

```text
cold-ish run
warm run
```

Do not pretend that one repeated measurement represents every deployment.

---

# 111. Profiling Exercise

Build a moderately complex query:

```python
lf = (
    pl.scan_parquet(PATH)
      .filter(...)
      .select(...)
      .join(...)
      .group_by(...)
      .agg(...)
)
```

Then profile using the installed API:

```python
profiled = lf.profile()
```

or the current equivalent in your version.

Find the most expensive stage.

Write:

```text
Bottleneck:
Possible cause:
Evidence:
Optimization hypothesis:
Change:
After-measurement:
```

---

# 112. What if the Scan Is the Bottleneck?

Investigate:

```text
How many files?
How many partitions?
How many columns?
How many bytes?
Local or remote?
Can projection improve?
Can predicate pushdown improve?
Can partition pruning improve?
Can row-group skipping improve?
```

Do not immediately rewrite the transformation code.

---

# 113. What if the Join Is the Bottleneck?

Investigate:

```text
left row count
right row count
selected columns
join key
key uniqueness
expected cardinality
duplicate keys
pre-join filtering
```

Ask:

> Can I make both join inputs smaller before performing the join?

---

# 114. What if the Sort Is the Bottleneck?

Investigate:

```text
Is global order required?
Can rows be filtered before sorting?
Can columns be reduced?
Does the downstream result really require a global sort?
```

Do not remove required sorting just to make a query faster.

---

# 115. What if a UDF Is the Bottleneck?

Ask:

```text
Is there a native expression?
Is there a namespace operation?
Can the logic be decomposed into expressions?
Is the custom Python logic truly unavoidable?
```

If unavoidable:

```text
isolate
benchmark
document
monitor
```

---

# 116. Sink Experiment

Compare:

```python
result = (
    lf
    .collect()
)

result.write_parquet(
    "gold.parquet"
)
```

with a sink-based design when supported:

```python
lf.sink_parquet(
    "gold.parquet"
)
```

The question is not:

> "Is sink always faster?"

It is:

> Does avoiding full result materialization reduce memory pressure and fit the workload better?

---

# 117. `collect_all()` Experiment

Create several related queries:

```python
paid = (
    pl.scan_parquet(PATH)
      .filter(
          pl.col("status") == "PAID"
      )
)

cancelled = (
    pl.scan_parquet(PATH)
      .filter(
          pl.col("status") == "CANCELLED"
      )
)
```

Compare:

```text
collect paid separately
collect cancelled separately
```

against coordinated collection with the current `pl.collect_all(...)` API.

Record actual:

```text
runtime
source reads
memory
```

Do not assume shared execution occurs without inspecting/benchmarking.

---

# 118. File Layout Investigation

Create two conceptual datasets:

### Dataset A

```text
poorly organized files
```

### Dataset B

```text
Hive-partitioned Parquet
```

Then query:

```text
one year
one month
```

Investigate:

```text
files considered
files read
bytes read
runtime
```

This experiment demonstrates why optimization is partly a storage-layout problem.

---

# 119. Production Incident Exercise

Scenario:

> A nightly pipeline that normally finishes in 20 minutes now takes 90 minutes. The query result is still correct.

Investigate in this order:

```text
1. Did data volume change?
2. Did file count change?
3. Did partitioning change?
4. Did schema width change?
5. Did bytes read change?
6. Did the plan change?
7. Did a UDF or conversion get added?
8. Did a join grow unexpectedly?
9. Did a sort become dominant?
10. What changed in the data or dependency versions?
```

This is a realistic incident-response mindset.

---

# 120. Production Monitoring Ideas

For important lazy pipelines, useful operational signals can include:

```text
run duration
rows processed
output rows
input files
bytes read
peak memory
failed partitions
schema changes
dependency version
```

The exact metrics depend on your platform.

The principle is:

> Performance regressions should be observable, not discovered only after an SLA miss.

---

# 121. Senior Data Engineer Design Review

Suppose a design review proposes:

```text
Every stage calls collect()
```

Ask:

```text
Why?
What is the materialization contract?
Could the whole plan remain lazy?
What memory does each boundary require?
Which pushdown opportunities disappear?
```

Suppose someone proposes:

```text
Everything in one giant function
```

Ask:

```text
Can we split transformations into testable LazyFrame → LazyFrame functions?
```

Suppose someone proposes:

```text
map_elements for all custom logic
```

Ask:

```text
Which rules already have native expressions?
```

---

# 122. Senior Optimization Review Questions

Use these questions in interviews and code reviews:

```text
What is the source?
What is the grain?
What columns are required?
What rows are required?
What predicates are selective?
Which partitions are relevant?
Can row groups be skipped?
What is the join cardinality?
What is the most expensive node?
Where is data materialized?
Is a sink possible?
Where are Python boundaries?
How was the optimization measured?
How was correctness verified?
```

---

# 123. Practice Problems — Basic

## B1

Create an eager DataFrame and convert it to a LazyFrame.

## B2

Write a lazy filter.

## B3

Write a lazy projection.

## B4

Call `collect()` and identify the materialization point.

## B5

Use `scan_parquet()`.

## B6

Use `scan_csv()`.

## B7

Use `collect_schema()`.

## B8

Use `explain()`.

## B9

Explain predicate pushdown.

## B10

Explain projection pushdown.

---

# 124. Practice Problems — Basic Answer Key

### B1

```python
lf = df.lazy()
```

### B2

```python
lf.filter(
    pl.col("amount") > 100
)
```

### B3

```python
lf.select(
    ["customer_id", "amount"]
)
```

### B4

The `collect()` call triggers materialization.

### B5

```python
pl.scan_parquet("data/*.parquet")
```

### B6

```python
pl.scan_csv("data/*.csv")
```

### B7

```python
lf.collect_schema()
```

### B8

```python
lf.explain()
```

### B9

Move a compatible predicate closer to the source to reduce unnecessary row work.

### B10

Reduce the required column set as early as semantics and source support allow.

---

# 125. Practice Problems — Moderate

## M1

Why can early `collect()` reduce optimizer visibility?

## M2

Give an example where `head(100)` cannot simply cause the source to read 100 rows.

## M3

Explain common subplan elimination.

## M4

Explain common subexpression elimination.

## M5

Explain plan simplification.

## M6

Explain Hive-style partitioning.

## M7

Explain partition pruning.

## M8

Explain Parquet row-group skipping.

## M9

Explain why `collect_schema()` is useful during development.

## M10

Explain why sinks can reduce materialization.

---

# 126. Practice Problems — Moderate Answer Key

### M1

It creates a concrete result before downstream operations are known to the same plan.

### M2

A global sort followed by `head(100)` may need much more than 100 source rows to find the correct top 100.

### M3

Reuse of shared portions of multiple lazy plans when the optimizer can safely identify common work.

### M4

Reuse of repeated expressions inside a plan where safe.

### M5

Rewriting/removing redundant work while preserving semantics.

### M6

A directory layout such as:

```text
year=2026/month=01/
```

where path values represent partition fields.

### M7

Eliminating partitions that cannot satisfy predicates.

### M8

Using Parquet statistics to skip row groups that cannot satisfy a predicate.

### M9

It exposes expected output structure without full data materialization.

### M10

They can write a large result directly from the execution pipeline instead of collecting a huge DataFrame first.

---

# 127. Practice Problems — Hard

## H1

A 50-column dataset returns only 4 columns. What do you investigate?

## H2

A highly selective filter exists but all partitions are scanned. List likely causes.

## H3

A UDF occurs before a filter. What experiment would you run?

## H4

A join consumes 70% of runtime. What should you investigate?

## H5

A loop calls `collect()` once for each customer. What alternatives should you investigate?

## H6

Runtime improves but bytes read stay flat. What could explain this?

## H7

Bytes read decrease but runtime barely changes. What could explain this?

## H8

A `collect()` was introduced as a debugging step and remains in production. What should you review?

## H9

A selector or dynamic transformation starts including a newly added column. Why can this happen?

## H10

How do you prove an optimized query remains correct?

---

# 128. Practice Problems — Hard Answer Key

### H1

Inspect:

```text
projection pushdown
column dependencies
computed fields
joins
filters
```

and measure source I/O.

### H2

Possible causes:

- partition values are not recognized,
- predicate uses non-partition columns,
- layout does not match the filter,
- many partitions genuinely qualify,
- source statistics are insufficient,
- measurement includes cached or other I/O.

### H3

Compare:

```text
native expression
vs
UDF
```

Inspect plans and measure runtime/I/O.

### H4

Inspect:

```text
input sizes
key uniqueness
cardinality
selected columns
pre-join filters
```

### H5

Investigate one consolidated query, a grouped query, or coordinated lazy collection.

### H6

The bottleneck may have moved to CPU, join, aggregation, or another stage.

### H7

I/O may not be the dominant cost, or the reduced I/O may be small relative to total work.

### H8

Determine whether the boundary is still required. Remove it if it is not part of the intended architecture.

### H9

Dynamic selection follows rules, not a fixed column list.

### H10

Use:

```text
deterministic result comparison
schema checks
row-count/reconciliation checks
business invariants
```

---

# 129. Practice Problems — Advanced

## A1

Design a lazy query over 1 TB partitioned Parquet where only one week and five columns are needed.

## A2

Design a projection-pushdown proof experiment.

## A3

Design a predicate-pushdown proof experiment.

## A4

Design a UDF blocker experiment.

## A5

Design a benchmark separating I/O cost from CPU cost.

## A6

Design a `LazyFrame → LazyFrame` architecture for a silver-to-gold pipeline.

## A7

Explain when `collect_all()` can help.

## A8

Design a profiling investigation for a sort bottleneck.

## A9

Design a profiling investigation for a join bottleneck.

## A10

Create an architecture-review checklist for a production lazy pipeline.

---

# 130. Practice Problems — Advanced Answer Key

### A1

```text
scan partitioned Parquet
→ filter partition/date
→ project required columns
→ transformations
→ aggregate
→ sink
```

Measure plan and I/O.

### A2

Use the same dataset and query with narrow vs broad required projections. Inspect the optimized plan and measure read volume.

### A3

Use a selective predicate and compare a native expression with a version that reduces pushdown visibility.

### A4

Use equivalent native and Python-UDF transformations. Compare plan, runtime, memory, and I/O.

### A5

Measure:

```text
bytes read
scan time
compute-node profile
total runtime
```

### A6

Keep transformation functions pure:

```python
def stage(lf: pl.LazyFrame) -> pl.LazyFrame:
    return ...
```

and materialize only at orchestration/output boundaries.

### A7

When multiple lazy queries have shared work and coordinated collection allows the engine to reuse some of it.

### A8

Determine whether filtering/projection can reduce the sort input. Confirm whether global sorting is required.

### A9

Inspect cardinality, key distribution, input widths, and pre-join reduction.

### A10

Review:

```text
source
schema
partitions
projection
predicates
plan
pushdowns
joins
materialization
profiling
I/O
memory
correctness
versioning
```

---

# 131. Interview Preparation — Beginner

## Question 1 — What is lazy execution?

Lazy execution defers execution of a query until a materializing action occurs, allowing the engine to plan and optimize a larger set of transformations together.

## Question 2 — What is a LazyFrame?

A `LazyFrame` is a pending DataFrame computation rather than a fully materialized result.

## Question 3 — What does `collect()` do?

It executes the lazy plan and materializes the result as a concrete DataFrame.

## Question 4 — Why use `scan_parquet()`?

It keeps the source inside a lazy plan, allowing downstream transformations to participate in planning and optimization.

## Question 5 — What is a query plan?

A representation of the operations and dependencies needed to produce a result.

---

# 132. Interview Preparation — Intermediate

## Question 6 — What is predicate pushdown?

Moving a compatible filtering operation toward the source so unnecessary rows can potentially be avoided earlier.

## Question 7 — What is projection pushdown?

Reducing the columns that need to be read or carried through the pipeline based on downstream dependencies.

## Question 8 — What is slice pushdown?

Moving a limit/slice earlier when that can safely reduce work.

## Question 9 — What is partition pruning?

Eliminating irrelevant partitions using partition metadata.

## Question 10 — What is row-group skipping?

Using Parquet row-group statistics to skip groups that cannot contain matching data.

## Question 11 — What does `collect_schema()` do?

It determines the lazy result schema without requiring full result materialization.

## Question 12 — Why is Parquet important for lazy optimization?

Because its columnar structure and metadata can support selective reading and row-group skipping.

---

# 133. Interview Preparation — Advanced

## Question 13 — Why can an optimizer make the query faster without changing its output?

Because different execution strategies can be semantically equivalent while doing less I/O, CPU work, memory movement, or redundant computation.

## Question 14 — What makes a query optimizer-friendly?

Native expressions, visible dependencies, preserved lazy execution, source-compatible predicates, narrow projections, and limited opaque Python boundaries.

## Question 15 — Why can Python UDFs interfere with optimization?

The optimizer can reason about native expression structure more effectively than arbitrary Python callback semantics.

## Question 16 — Why is early `collect()` often a problem?

It materializes an intermediate state before downstream operations can be optimized together.

## Question 17 — How would you prove projection pushdown?

Inspect the optimized plan and measure the source bytes/files/columns actually read where instrumentation permits.

## Question 18 — How would you investigate high bytes read?

Check:

```text
partition pruning
projection
predicate pushdown
row-group skipping
file count
file layout
cache
```

## Question 19 — When can `collect_all()` help?

When several lazy queries contain common work that can potentially be shared during coordinated execution.

## Question 20 — Why use a sink?

To write a large result without unnecessarily materializing the entire result as a Python DataFrame.

## Question 21 — How do you structure reusable lazy transformations?

Use functions that accept a `LazyFrame` and return a transformed `LazyFrame`, leaving materialization to the orchestration boundary.

## Question 22 — How do you distinguish CPU and I/O bottlenecks?

Use profiling together with source/I/O measurements. A scan-dominated query suggests source costs; compute-dominated profiles suggest transformations, joins, sorts, or UDFs.

---

# 134. Senior Architecture Questions

## Question 23

A query scans 2 TB but returns 5 GB. What is your first optimization question?

> Can the query read less than 2 TB?

Then inspect:

```text
partition pruning
projection pushdown
predicate pushdown
row-group skipping
```

## Question 24

A team wants to add `collect()` after every pipeline step for "debugging."

What should you say?

Materialization can be valuable during debugging, but it should not automatically become production architecture. Keep a debug mode or targeted checks rather than destroying the global lazy plan.

## Question 25

A Python UDF is required for a business rule.

What is the correct design response?

Use it only where needed, isolate it, benchmark it, document why a native alternative is unavailable, and monitor its cost.

## Question 26

A design claims:

> "All Parquet filters are pushed to storage."

What is wrong with that statement?

Pushdown depends on predicate semantics, optimizer capabilities, file-reader capabilities, metadata, and source layout.

## Question 27

A team optimized runtime by changing the query and accidentally changed duplicate-row behaviour.

What failed?

Correctness was not treated as a non-negotiable constraint.

---

# 135. Explain-Aloud Exercises

## Exercise A — `scan_parquet`

Explain:

```python
lf = pl.scan_parquet(
    "orders/*.parquet"
)
```

before `collect()`.

Your answer should include:

```text
lazy source
pending computation
query plan
no final DataFrame yet
```

---

## Exercise B — Predicate Pushdown

Explain:

```python
.filter(
    pl.col("amount") > 1000
)
```

without claiming that every matching row is read directly from storage.

---

## Exercise C — Projection Pushdown

Explain:

```text
100 columns
→ query needs 5
```

and what the optimizer is trying to accomplish.

---

## Exercise D — Partition vs Row Group

Explain:

```text
partition pruning
```

and:

```text
row-group skipping
```

as different levels of elimination.

---

## Exercise E — `collect()` in Loops

Explain why:

```python
for item in items:
    lf.collect()
```

can repeatedly execute expensive work.

---

## Exercise F — UDF

Explain why:

```python
map_elements(...)
```

may be less optimizer-friendly than:

```python
pl.col(...)
```

based native expressions.

---

## Exercise G — `explain()` vs `profile()`

Explain:

```text
plan prediction
vs
runtime evidence
```

---

## Exercise H — Sink

Explain why:

```text
large LazyFrame
→ sink_parquet
```

can be better than:

```text
large LazyFrame
→ collect
→ write
```

when Python does not need the full DataFrame.

---

# 136. Debugging Drill — Complete Cases

For each case, answer:

```text
Symptom
Cause
Inspection
Fix
Production lesson
```

### Case 1

All 100 columns are read.

### Case 2

All year partitions are scanned despite a year predicate.

### Case 3

A selective filter provides no apparent source reduction after adding a UDF.

### Case 4

A pipeline has three `collect()` calls.

### Case 5

A 200 GB result causes an out-of-memory error during output.

### Case 6

`profile()` shows a sort dominates.

### Case 7

`profile()` shows a join dominates.

### Case 8

Runtime improves but source I/O does not.

### Case 9

A benchmark improves only after warm-up.

### Case 10

A plan changes after a Polars upgrade.

---

# 137. Debugging Drill — Answer Key

### Case 1

Inspect projection dependencies and source scan.

### Case 2

Inspect Hive partition recognition, layout, and predicate alignment.

### Case 3

Compare against native expression and inspect optimized plan.

### Case 4

Review whether each materialization is intentional and whether stages can remain one plan.

### Case 5

Use a sink when a full in-memory result is unnecessary.

### Case 6

Reduce the sort input or question whether global sort is necessary.

### Case 7

Inspect input size, key cardinality, duplicates, projection, and pre-join filtering.

### Case 8

Optimization probably affected CPU or execution efficiency rather than source I/O.

### Case 9

Document warm/cold state; cache effects are real.

### Case 10

Re-verify version-sensitive plan formatting and optimizer behaviour through current documentation and new measurements.

---

# 138. Final Mastery Assessment

Do not use the answer key until you have attempted every section.

---

## Part A — Fundamental Concepts

Answer all 15.

1. Explain eager vs lazy execution.
2. What is a `LazyFrame`?
3. Why does `collect()` execute the plan?
4. Why can lazy execution improve performance?
5. Why does lazy execution not guarantee faster results?
6. What is a query plan?
7. What is a logical plan?
8. What is a physical execution plan?
9. What is `collect_schema()`?
10. What does `explain()` tell you?
11. What does `profile()` tell you?
12. What is predicate pushdown?
13. What is projection pushdown?
14. What is partition pruning?
15. What is row-group skipping?

---

# 139. Part A — Answer Key

1. Eager executes immediately; lazy defers materialization and allows a larger plan to be optimized first.
2. A pending query computation.
3. It is a materializing operation that requests the result.
4. The optimizer can potentially eliminate unnecessary work.
5. Some workloads have little optimization opportunity or are dominated by unavoidable operations.
6. A representation of required operations and dependencies.
7. A representation of what must be computed.
8. A more concrete strategy for how the computation will execute.
9. The expected result schema without full data materialization.
10. It exposes the query plan and is used to inspect optimization.
11. It reports runtime information useful for locating bottlenecks.
12. Moving compatible filtering closer to the source.
13. Reducing required columns.
14. Removing irrelevant partitions using their partition metadata.
15. Skipping Parquet row groups based on metadata/statistics when predicates permit.

---

# 140. Part B — Query Plan Interpretation

For each, state:

```text
optimization
evidence
limitation
```

### B1

```python
pl.scan_parquet(PATH).select(
    ["id", "amount"]
)
```

### B2

```python
pl.scan_parquet(PATH).filter(
    pl.col("amount") > 100
)
```

### B3

```python
(
    pl.scan_parquet(PATH)
      .filter(pl.col("amount") > 100)
      .select(["id", "amount"])
)
```

### B4

```python
pl.scan_parquet(PATH).head(100)
```

### B5

```python
(
    pl.scan_parquet(PATH)
      .sort("amount", descending=True)
      .head(100)
)
```

### B6

```python
(
    pl.scan_parquet(PATH)
      .with_columns(
          (pl.col("amount") * 1.18)
          .alias("gross")
      )
      .filter(
          pl.col("status") == "PAID"
      )
)
```

### B7

Two queries use the same source.

### B8

A derived expression appears repeatedly.

### B9

An intermediate `collect()` occurs.

### B10

A filter matches Hive partition fields.

### B11

A Python UDF appears before a selective filter.

### B12

Final output contains four columns but source reads many more.

### B13

Final result is 500 GB.

### B14

A join dominates profile time.

### B15

Bytes read remain constant but runtime falls.

---

# 141. Part B — Answer Key

### B1

Projection pushdown. Inspect scan requirements and I/O.

### B2

Predicate pushdown. Inspect predicate placement and source I/O.

### B3

Both.

### B4

Potential slice pushdown, but the source may still require more work.

### B5

The global sort can require substantial input before the correct top 100 is known.

### B6

The status filter may be movable before the derived expression because it does not depend on `gross`.

### B7

Investigate common subplan elimination and coordinated collection.

### B8

Investigate common subexpression elimination.

### B9

The plan is split by materialization.

### B10

Investigate partition pruning.

### B11

Investigate reduced optimizer visibility and compare against a native expression.

### B12

Inspect projection dependencies.

### B13

Consider a sink.

### B14

Investigate join inputs, cardinality, duplicates, projection, and filtering.

### B15

The improvement likely came from CPU/execution efficiency rather than reduced source I/O.

---

# 142. Part C — Coding Assessment

Implement:

1. `scan_source(path) -> LazyFrame`.
2. `filter_valid_rows(lf) -> LazyFrame`.
3. `select_required_columns(lf) -> LazyFrame`.
4. `build_silver(lf) -> LazyFrame`.
5. `build_gold(lf) -> LazyFrame`.
6. `collect_schema`.
7. `explain`.
8. `profile`.
9. `sink_parquet`.
10. a unit test.
11. an eager baseline.
12. a lazy baseline.
13. a UDF baseline.
14. a fair benchmark.
15. an optimization report.

---

# 143. Part C — Reference Patterns

### 1. Source

```python
def scan_source(path: str) -> pl.LazyFrame:
    return pl.scan_parquet(path)
```

### 2. Filter

```python
def filter_valid_rows(
    lf: pl.LazyFrame,
) -> pl.LazyFrame:
    return lf.filter(
        pl.col("amount") >= 0
    )
```

### 3. Projection

```python
def select_required_columns(
    lf: pl.LazyFrame,
) -> pl.LazyFrame:
    return lf.select(
        [
            "customer_id",
            "amount",
        ]
    )
```

### 4. Silver

Compose typed filters, projections, deduplication, and derived fields while remaining lazy.

### 5. Gold

Use grouped aggregations while remaining lazy.

### 6. Schema

```python
lf.collect_schema()
```

### 7. Plan

```python
lf.explain()
```

### 8. Profile

Use the current profiling API supported by the installed version.

### 9. Sink

```python
lf.sink_parquet(
    "output.parquet"
)
```

### 10. Unit test

Pass a tiny in-memory DataFrame as:

```python
source.lazy()
```

then collect inside the test.

---

# 144. Part D — Optimization Debugging Assessment

Diagnose these ten failures:

1. Lazy source replaced by eager read.
2. Early materialization.
3. `collect()` in loop.
4. UDF before filter.
5. Wide projection.
6. Late filtering.
7. Partitions not pruned.
8. Unexpected bytes read.
9. Profile bottleneck.
10. Huge result collected.

For each write:

```text
Symptom
Cause
How to inspect
Correction
Evidence after correction
Production lesson
```

---

# 145. Part D — Model Answers

### 1. Eager source

Change:

```python
pl.read_parquet(...)
```

to an appropriate:

```python
pl.scan_parquet(...)
```

when global lazy planning is beneficial.

### 2. Early materialization

Move downstream compatible work into the same LazyFrame.

### 3. Loop collection

Investigate one query or coordinated lazy collection.

### 4. UDF

Replace with native expression if possible.

### 5. Wide projection

Trace dependencies and select only required columns.

### 6. Late filtering

Move compatible filters earlier.

### 7. Partition pruning

Check path layout, `hive_partitioning`, predicate fields, and actual files touched.

### 8. Bytes read

Inspect source layout, projections, predicates, pruning, statistics, and measurement semantics.

### 9. Profile bottleneck

Optimize the dominant cost rather than a minor node.

### 10. Huge result

Use a sink when materialization is unnecessary.

---

# 146. Part E — Production Architecture Assessment

Answer as if you are defending a production design.

### E1

A 1 TB partitioned Parquet dataset is queried for one day.

### E2

A team claims lazy execution makes the pipeline fast.

### E3

The plan shows a filter, but storage I/O stays high.

### E4

A Python UDF is necessary for one complex business rule.

### E5

The final output is 300 GB.

### E6

A join dominates profiling.

### E7

A sort dominates profiling.

### E8

A benchmark differs dramatically between machines.

### E9

A Polars upgrade changes plan formatting.

### E10

How would you present an optimization change to a design review?

---

# 147. Part E — Answer Key

### E1

Investigate partition pruning, projection, predicate pushdown, file count, and row-group skipping.

### E2

Correct the statement: lazy execution creates optimization opportunities; it does not guarantee fast execution.

### E3

Investigate whether the filter can actually be pushed, whether the partitioning matches it, and whether file statistics can help.

### E4

Isolate, document, benchmark, and monitor it.

### E5

Prefer a sink when Python does not need the whole materialized result.

### E6

Check cardinality, duplicates, row/column width, and upstream reduction.

### E7

Determine whether the sort is required and reduce its input if possible.

### E8

Check hardware, storage, cache, data shape, library version, and concurrency.

### E9

Re-check version-sensitive plan output and compare semantic optimizations rather than exact strings.

### E10

Show:

```text
problem
baseline
plan
profile
measurement
hypothesis
change
new evidence
correctness
trade-offs
limitations
```

---

# 148. Final Production Engineering Checklist

Use this before releasing a large LazyFrame pipeline.

## Source

```text
[ ] lazy source
[ ] correct file format
[ ] partition layout understood
[ ] schema known
[ ] file count known
```

## Query

```text
[ ] intended grain documented
[ ] required columns known
[ ] selective predicates identified
[ ] joins understood
[ ] sorts justified
```

## Optimizer

```text
[ ] explain() inspected
[ ] projection opportunity checked
[ ] predicate opportunity checked
[ ] slice opportunity checked
[ ] partition pruning checked
[ ] row-group skipping considered
[ ] repeated work considered
```

## Python boundaries

```text
[ ] UDFs reviewed
[ ] eager conversions reviewed
[ ] collect() reviewed
[ ] loops reviewed
```

## Execution

```text
[ ] profile() inspected
[ ] dominant bottleneck identified
[ ] bytes read measured if possible
[ ] peak memory measured if important
```

## Output

```text
[ ] collect only when required
[ ] sink considered for large output
```

## Correctness

```text
[ ] output schema tested
[ ] row counts reconciled
[ ] business metrics validated
[ ] edge cases tested
```

---

# 149. Final Mastery Checklist

- [ ] I understand eager vs lazy execution.
- [ ] I understand what a `LazyFrame` represents.
- [ ] I know when execution occurs.
- [ ] I understand `df.lazy()`.
- [ ] I understand `collect()`.
- [ ] I can use `scan_parquet()`.
- [ ] I can use `scan_csv()`.
- [ ] I can use `scan_ndjson()`.
- [ ] I understand `scan_ipc()`.
- [ ] I can scan multiple files.
- [ ] I understand globs.
- [ ] I can use `collect_schema()`.
- [ ] I understand logical plans.
- [ ] I understand physical execution plans.
- [ ] I can use `explain()`.
- [ ] I can compare optimized and unoptimized plans.
- [ ] I understand `show_graph()`.
- [ ] I can recognize scan nodes.
- [ ] I can recognize projection nodes.
- [ ] I can recognize filter nodes.
- [ ] I can recognize join nodes.
- [ ] I can recognize aggregation nodes.
- [ ] I can recognize sort nodes.
- [ ] I can recognize sink nodes.
- [ ] I understand predicate pushdown.
- [ ] I understand projection pushdown.
- [ ] I understand slice pushdown.
- [ ] I understand common subplan elimination.
- [ ] I understand common subexpression elimination.
- [ ] I understand simplification.
- [ ] I understand Parquet column pruning.
- [ ] I understand Parquet row-group skipping.
- [ ] I understand Hive-style partitioning.
- [ ] I understand `hive_partitioning=True`.
- [ ] I understand partition pruning.
- [ ] I can distinguish partition pruning from row-group skipping.
- [ ] I can measure bytes read where possible.
- [ ] I know why bytes read is useful.
- [ ] I can use `profile()`.
- [ ] I can identify the slowest plan node.
- [ ] I can distinguish I/O, CPU, and memory bottlenecks.
- [ ] I understand Python UDF optimization barriers.
- [ ] I understand eager conversions inside lazy pipelines.
- [ ] I understand `collect()` inside loops.
- [ ] I understand premature full-dataset operations.
- [ ] I understand `pl.collect_all()`.
- [ ] I understand lazy sinks.
- [ ] I can use `sink_parquet()`.
- [ ] I understand `sink_csv()`.
- [ ] I understand `sink_ipc()`.
- [ ] I understand `sink_ndjson()`.
- [ ] I can structure `LazyFrame → LazyFrame` functions.
- [ ] I can unit-test lazy transformations.
- [ ] I understand plan vs result.
- [ ] I understand explain vs profile.
- [ ] I understand lazy vs streaming.
- [ ] I completed the lazy pipeline project.
- [ ] I completed the pushdown experiments.
- [ ] I completed the UDF blocker experiment.
- [ ] I benchmarked eager vs lazy fairly.
- [ ] I completed the profiling investigation.
- [ ] I completed the debugging exercises.
- [ ] I completed the practice problems.
- [ ] I completed the final mastery assessment.
- [ ] I can defend an optimization with measurements.

---

# 150. Final Mastery Challenge

Without looking at notes, explain this:

```python
lf = (
    pl.scan_parquet(
        "lake/orders/**/*.parquet",
        hive_partitioning=True,
    )
    .filter(
        (pl.col("year") == 2026)
        & (pl.col("month") == 1)
    )
    .select(
        [
            "customer_id",
            "amount",
        ]
    )
    .group_by("customer_id")
    .agg(
        pl.col("amount")
          .sum()
          .alias("revenue")
    )
)
```

Your explanation must cover:

```text
1. source
2. lazy execution
3. partition pruning
4. predicate pushdown
5. projection pushdown
6. grouping
7. aggregation
8. plan
9. collect vs sink
10. how to prove optimization
```

A strong explanation will say:

```text
The source is represented lazily.

The year/month predicate may allow partition pruning
because those values are represented in the Hive-style
dataset layout.

The query needs only customer_id and amount for the
final aggregation, so projection analysis can reduce
the physical columns required.

The group_by().agg() reduces the data to one row per
customer.

The complete transformation remains visible to the
optimizer until an execution operation such as collect()
or an appropriate sink.

I would verify the plan with explain(), inspect runtime
with profile(), and measure source I/O/bytes read where
possible. Then I would validate that the output remains
correct.
```

---

# 151. Final Mental Model

You should now be able to picture a Polars lazy pipeline like this:

```text
                         LAZY POLARS
                              │
                              ▼
                       LazyFrame
                              │
                              ▼
                       Logical Plan
                              │
                    ┌─────────┴─────────┐
                    │                   │
                 rewrite              prune
                    │                   │
                    └─────────┬─────────┘
                              ▼
                     Optimized Plan
                              │
             ┌────────────────┼─────────────────┐
             ▼                ▼                 ▼
       predicate          projection         slice
       pushdown            pushdown          pushdown
             │                │                 │
             └────────────────┼─────────────────┘
                              ▼
                     source/file pruning
                              │
               ┌──────────────┴─────────────┐
               ▼                            ▼
        partition pruning           row-group skipping
               │                            │
               └──────────────┬─────────────┘
                              ▼
                         execution
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
                 collect              sink
                    │                   │
                    ▼                   ▼
               DataFrame               File
```

The key questions are:

```text
What data is required?
What data can be eliminated?
What work can move earlier?
What work can be reused?
What work is opaque?
Where is the bottleneck?
Where is data materialized?
How do I prove the optimization?
```

---

# 152. Transition to Topic 04

The module sequence now becomes:

```text
Topic 01
Arrow columnar memory
        ↓
Topic 02
Polars expressions and contexts
        ↓
Topic 03
Polars lazy API and query optimization
        ↓
Topic 04
Polars streaming for larger-than-memory data
```

The transition is:

```text
Topic 02
"I can express the transformation."

Topic 03
"I can keep the transformation as a plan and optimize it."

Topic 04
"I can execute an optimized plan using bounded-memory
streaming for datasets larger than RAM."
```

Topic 04 will build directly on:

```text
LazyFrame
query plan
pushdown
sinks
```

Do not try to solve the entire streaming problem in this chapter.

---

# 153. Final Production Reflection

Answer these in writing before moving to Topic 04.

### Reflection 1

Why is lazy execution useful even when the query result is small?

### Reflection 2

What does the optimizer need to know to perform projection pushdown?

### Reflection 3

Why can a query plan be more useful than the final result when troubleshooting performance?

### Reflection 4

Why does data layout matter to query optimization?

### Reflection 5

Why are Python UDFs an important design consideration?

### Reflection 6

Why can early `collect()` change the performance characteristics of the same logical transformation?

### Reflection 7

Why are bytes read, runtime, and peak memory all useful measurements?

### Reflection 8

Why is partition pruning different from row-group skipping?

### Reflection 9

When is a sink preferable to `collect()`?

### Reflection 10

What evidence would convince you that a production optimization is real?

---

# 154. Topic 03 Exit Criteria

Only move to Topic 04 when you can demonstrate all of the following without looking at notes:

```text
[ ] Explain eager vs lazy execution.
[ ] Explain LazyFrame.
[ ] Explain df.lazy().
[ ] Explain collect().
[ ] Explain lazy source scanning.
[ ] Use scan_parquet().
[ ] Use scan_csv().
[ ] Use scan_ndjson().
[ ] Understand scan_ipc().
[ ] Scan multiple files.
[ ] Explain collect_schema().
[ ] Read a query plan.
[ ] Use explain().
[ ] Compare optimized/unoptimized plans.
[ ] Explain show_graph().
[ ] Identify plan operators.
[ ] Explain predicate pushdown.
[ ] Explain projection pushdown.
[ ] Explain slice pushdown.
[ ] Explain common subplan elimination.
[ ] Explain common subexpression elimination.
[ ] Explain simplification.
[ ] Explain Parquet column pruning.
[ ] Explain Parquet row-group skipping.
[ ] Explain Hive partitioning.
[ ] Use hive_partitioning=True.
[ ] Explain partition pruning.
[ ] Distinguish partition pruning and row-group skipping.
[ ] Measure bytes read where possible.
[ ] Use profile().
[ ] Identify a bottleneck.
[ ] Distinguish I/O, CPU, and memory bottlenecks.
[ ] Explain Python UDF barriers.
[ ] Explain early eager conversion.
[ ] Explain collect() inside loops.
[ ] Explain premature full-dataset operations.
[ ] Understand collect_all().
[ ] Understand lazy sinks.
[ ] Understand sink_parquet().
[ ] Understand sink_csv().
[ ] Understand sink_ipc().
[ ] Understand sink_ndjson().
[ ] Build LazyFrame → LazyFrame functions.
[ ] Unit-test those functions.
[ ] Complete lazy_pipeline.py.
[ ] Complete projection pushdown experiment.
[ ] Complete predicate pushdown experiment.
[ ] Complete UDF blocker experiment.
[ ] Complete eager vs lazy benchmark.
[ ] Complete profiling experiment.
[ ] Complete plan reading exercises.
[ ] Complete debugging exercises.
[ ] Complete practice problems.
[ ] Complete mastery assessment.
[ ] Explain lazy vs streaming.
[ ] Defend an optimization using evidence.
```

---

# 155. Final Senior Data Engineer Takeaway

The most important change in thinking is:

```text
Beginner mindset:

"My code returns the correct rows."

Senior mindset:

"I know what work the code causes.

I know what the optimizer can remove.

I know what the storage layer can prune.

I know where materialization occurs.

I know which operator dominates runtime.

And I can prove the improvement with measurements
without changing the result."
```

That is the core skill this chapter is designed to build.

---
