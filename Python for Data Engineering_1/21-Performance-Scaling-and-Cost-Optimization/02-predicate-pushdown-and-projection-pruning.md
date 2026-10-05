# Claude Code Task — Build the Learning Module

## ROLE

Act as a **Senior Data Engineer with 10+ years of production industry experience**, specializing in:

- Data Engineering
- Data Platform Engineering
- Query Optimization
- Data Storage Architecture
- Columnar Data Systems
- Lakehouse Architecture
- Database Performance
- Data Warehouse Optimization
- Distributed Data Processing
- Cloud Data Platforms
- Performance Engineering
- Cost Optimization

Your task is to create a complete, production-oriented learning module for:

```text
21-Performance-Scaling-and-Cost-Optimization/
```

Target file:

```text
21-Performance-Scaling-and-Cost-Optimization/02-predicate-pushdown-and-projection-pruning.md
```

---

# 1. SOURCE OF TRUTH — MANDATORY

The authoritative source for this task is the **Module 2.21 — Performance, Scaling, and Cost Optimization** roadmap.

This task is specifically for:

```text
Topic 02 — Predicate Pushdown and Projection Pruning
```

The roadmap defines this topic around the central principle:

> **The fastest data is data you never read.**

The module must teach the learner how to minimize unnecessary data movement and computation by pushing filtering and column selection as close to the storage/source layer as possible.

The roadmap explicitly requires coverage of:

### Basics

- Projection pruning
- Predicate pushdown
- Partition pruning

### Intermediate

- End-to-end pushdown stack:
  - API filters
  - Database `WHERE` clauses
  - JDBC pushdown
  - Table-format metadata
  - Manifest pruning
  - File statistics
  - Parquet row-group statistics
  - Page indexes
  - Bloom filters
  - In-engine filters
- Verifying pushdown using:
  - Polars `explain()`
  - DuckDB `EXPLAIN ANALYZE`
  - Spark `PushedFilters`
  - Spark `PartitionFilters`
  - PyArrow dataset filters
  - Warehouse bytes-scanned statistics
- What breaks pushdown:
  - Python UDFs
  - functions applied to filtered columns
  - casts applied to filtered columns
  - filters on derived columns instead of partition columns
  - type mismatches
  - `OR` conditions across columns
  - filters applied after `collect`
- Data layout that enables pushdown:
  - sorting
  - clustering
  - selective statistics

### Advanced

- Limit pushdown
- Aggregate pushdown
- Join pushdown
- Dynamic filtering
- Runtime filters
- Dynamic partition pruning
- Late materialization
- Scan audits
- Bytes scanned vs bytes actually needed
- Identifying worst-performing scans
- Pushdown as a direct cloud-cost optimization

These concepts must all be taught. Do **not** skip any roadmap concept.

---

# 2. PRIMARY LEARNING OBJECTIVE

Build the learner from:

```text
Beginner
    ↓
Foundational
    ↓
Intermediate
    ↓
Advanced
    ↓
Production Data Engineer
```

By the end of this file, the learner must be able to answer:

> **"How can I make a data pipeline or query read less data, prove that the engine actually skipped the unnecessary data, identify what is preventing pushdown, and quantify the performance and cost improvement?"**

The learner should understand that performance optimization begins with:

```text
Don't read unnecessary rows.
Don't read unnecessary columns.
Don't scan unnecessary files.
Don't transfer unnecessary data.
Don't process unnecessary data.
```

---

# 3. CENTRAL PRINCIPLE

Build the entire module around:

```text
READ LESS
    ↓
PROCESS LESS
    ↓
MOVE LESS DATA
    ↓
USE LESS COMPUTE
    ↓
FINISH FASTER
    ↓
COST LESS
```

Explain why this is generally preferable to immediately:

```text
Add more workers
Add more CPUs
Add more machines
Increase cluster size
```

Connect this topic directly to the Module 2.21 optimization ladder:

```text
1. Do less work
       ↓
2. Use a better engine
       ↓
3. Use more cores
       ↓
4. Use more machines
```

Make clear that **predicate pushdown and projection pruning belong near the cheapest and highest-leverage end of the optimization ladder**.

---

# 4. TEACH FROM FIRST PRINCIPLES

Do not assume the learner already understands query optimization.

Start simply.

Explain:

- What is a query?
- What is a scan?
- What does it mean to read a row?
- What does it mean to read a column?
- What is filtering?
- What is projection?
- What is a predicate?
- What is pushdown?
- What is pruning?
- Why does reading less data make a pipeline faster?
- Why does reading less data reduce memory usage?
- Why can reading less data reduce cloud cost?

Use simple examples first.

For example:

```sql
SELECT customer_id, revenue
FROM sales
WHERE country = 'IN';
```

Explain the difference between:

```text
Read everything
→ filter later
```

and:

```text
Push filter into storage/source
→ read only matching data
```

Then gradually introduce real production systems.

---

# 5. REQUIRED LEARNING PROGRESSION

Structure the module approximately as:

```text
Part 1 — Why Reading Less Data Matters
Part 2 — What Is Projection Pruning?
Part 3 — What Is Predicate Pushdown?
Part 4 — Partition Pruning
Part 5 — The End-to-End Pushdown Stack
Part 6 — Verifying Pushdown
Part 7 — What Breaks Pushdown
Part 8 — Data Layout for Better Pushdown
Part 9 — Limit, Aggregate, and Join Pushdown
Part 10 — Dynamic Filtering and Runtime Filters
Part 11 — Late Materialization
Part 12 — Scan Auditing
Part 13 — Pushdown and Cloud Cost
Part 14 — Cross-Engine Examples
Part 15 — Production Failure Scenarios
Part 16 — Complete End-to-End Case Study
Part 17 — Hands-On Pushdown Laboratory
Part 18 — Production Checklist and Decision Framework
Part 19 — Checkpoint and Self-Assessment
```

You may improve the organization, but **do not remove any required roadmap topic**.

---

# 6. PART 1 — WHY READING LESS DATA MATTERS

Explain the fundamental relationship:

```text
Data scanned
    ↓
I/O
    ↓
Network transfer
    ↓
Decompression
    ↓
CPU processing
    ↓
Memory usage
    ↓
Runtime
    ↓
Cost
```

Explain why unnecessary data reading can affect multiple resources simultaneously.

Use a practical scenario:

```text
Dataset:
10 TB

Query needs:
200 GB
```

Explain why scanning the full 10 TB is wasteful.

Discuss:

- runtime;
- storage I/O;
- network;
- CPU;
- memory;
- warehouse cost;
- cloud object-storage request/read costs where relevant.

Do not invent pricing values.

If using cost numbers, clearly label them as illustrative.

---

# 7. PART 2 — PROJECTION PRUNING

Teach projection pruning from first principles.

## 7.1 What Is Projection?

Explain:

```sql
SELECT customer_id, revenue
```

versus:

```sql
SELECT *
```

Explain that a query may only need a subset of columns.

---

## 7.2 What Is Projection Pruning?

Explain:

> Projection pruning means reading only the columns required by the query or downstream operation.

Use a table:

```text
sales
├── customer_id
├── country
├── product_id
├── timestamp
├── revenue
├── cost
├── device
├── campaign
├── ...
```

If the query needs:

```text
customer_id
revenue
```

the engine should ideally avoid reading all other columns.

---

# 8. COLUMNAR STORAGE CONNECTION

Explain why projection pruning is especially powerful with:

- Parquet;
- columnar table formats;
- analytical databases;
- lakehouses;
- columnar warehouses.

Explain the difference between:

```text
Row-oriented storage
```

and:

```text
Column-oriented storage
```

Do not re-teach the entire Parquet module.

Use the learner's existing Module 2.5 knowledge and explain only what is necessary for this topic.

Explain why columnar storage allows:

```text
Read only needed columns
```

instead of:

```text
Read entire rows
```

---

# 9. CODING EXAMPLE — PROJECTION PRUNING

Provide practical examples using:

- PyArrow;
- Polars;
- DuckDB;
- Spark;
- SQL.

For example, demonstrate the difference between:

```python
pl.scan_parquet("sales/*.parquet").select(
    ["customer_id", "revenue"]
)
```

and:

```python
pl.scan_parquet("sales/*.parquet").select(
    pl.all()
)
```

Explain the logical plan.

Use lazy execution where appropriate.

Do not claim that writing `.select()` automatically proves that physical I/O was reduced.

Teach the learner to **verify the physical plan or execution evidence**.

---

# 10. PART 3 — PREDICATE PUSHDOWN

Teach:

> Predicate pushdown means applying a filter as early as possible, ideally inside the storage or source system, so unnecessary rows are never read.

Start with:

```sql
SELECT *
FROM sales
WHERE country = 'IN';
```

Explain two conceptual execution strategies:

### Strategy A — Filter after reading

```text
Read all rows
    ↓
Transfer all rows
    ↓
Filter
```

### Strategy B — Push filter down

```text
Filter at source/storage
    ↓
Read only relevant rows
    ↓
Process fewer rows
```

Explain why Strategy B is generally preferable.

---

# 11. PREDICATES

Explain what a predicate is.

Cover examples:

```sql
country = 'IN'
```

```sql
revenue > 1000
```

```sql
event_date >= DATE '2026-01-01'
```

Explain:

- simple predicates;
- compound predicates;
- predicates involving functions;
- predicates involving casts.

Use practical examples.

---

# 12. PARTITION PRUNING

This is mandatory.

Explain:

> Partition pruning means avoiding entire partitions that cannot contain matching records.

Example:

```text
sales/
├── event_date=2026-01-01/
├── event_date=2026-01-02/
├── event_date=2026-01-03/
...
```

Query:

```sql
WHERE event_date = '2026-01-03'
```

Explain why the engine may only need:

```text
event_date=2026-01-03/
```

instead of scanning every partition.

---

# 13. PARTITION PRUNING VS PREDICATE PUSHDOWN

Explicitly distinguish:

| Concept | What it skips |
|---|---|
| Projection pruning | Columns |
| Predicate pushdown | Rows/records |
| Partition pruning | Entire partitions |
| File pruning | Files |
| Row-group pruning | Row groups |
| Page pruning | Pages/regions |

Explain how these mechanisms can work together.

---

# 14. PART 5 — THE END-TO-END PUSHDOWN STACK

This is one of the most important sections.

Teach the complete stack from source to execution engine.

Use the roadmap's progression:

```text
API filters
    ↓
Database WHERE / JDBC pushdown
    ↓
Table-format metadata
    ↓
Manifest pruning
    ↓
File statistics
    ↓
Parquet row-group statistics
    ↓
Page indexes / Bloom filters
    ↓
In-engine filtering
```

Explain every layer.

---

# 15. API FILTER PUSHdown

Use examples of APIs where filtering can be applied remotely.

Conceptual example:

```text
Bad:

API
→ download all records
→ filter locally

Better:

API filter
→ API returns matching records
```

Explain why this matters.

Connect it to the previously learned API ingestion concepts.

---

# 16. DATABASE WHERE CLAUSES AND JDBC PUSHDOWN

Explain:

```sql
SELECT ...
FROM remote_table
WHERE event_date >= ...
```

versus:

```text
SELECT *
FROM remote_table
→ transfer everything
→ filter in Python
```

Explain why filtering at the database is generally preferable.

Show a Python/JDBC-style example conceptually.

Where appropriate demonstrate how an engine can push filters into a database.

---

# 17. TABLE-FORMAT METADATA

Explain at a conceptual level:

- table metadata;
- manifests;
- file statistics;
- min/max statistics;
- partition metadata.

Explain how metadata can allow the engine to skip files before reading their contents.

Do not re-teach complete Iceberg/Delta architecture.

Focus specifically on:

```text
metadata
→ file skipping
→ less I/O
```

---

# 18. PARQUET ROW-GROUP STATISTICS

Teach:

- row groups;
- min/max statistics;
- row-group pruning;
- page indexes;
- bloom filters.

Example:

```text
Row group A:
revenue min = 10
revenue max = 100

Query:
WHERE revenue > 1000
```

Explain why the engine can determine that this row group cannot contain matching values.

Use simple diagrams.

---

# 19. BLOOM FILTERS

Explain Bloom filters at the level required for Data Engineering.

Teach:

- probabilistic membership testing;
- possible false positives;
- no false negatives under normal operation;
- why they can help skip irrelevant data;
- why they do not replace exact filtering.

Keep the explanation practical.

---

# 20. PART 6 — VERIFYING PUSHdown

This section must emphasize:

> **Never assume pushdown happened. Prove it.**

Teach how to verify it in each engine specified by the roadmap.

---

# 21. POLARS — `explain()`

Demonstrate:

```python
lf = (
    pl.scan_parquet("sales/*.parquet")
    .filter(pl.col("country") == "IN")
    .select(["customer_id", "revenue"])
)

print(lf.explain())
```

Explain what the learner should look for.

Distinguish:

```text
logical plan
vs
optimized logical plan
vs
physical execution
```

Do not make unsupported claims about exact plan formatting across versions.

Mention that output may vary by Polars version.

---

# 22. DUCKDB — `EXPLAIN ANALYZE`

Demonstrate:

```sql
EXPLAIN ANALYZE
SELECT customer_id, revenue
FROM 'sales/*.parquet'
WHERE country = 'IN';
```

Teach how to inspect:

- scan operator;
- filters;
- projections;
- rows processed;
- execution timing.

Explain why actual execution evidence is more valuable than simply reading SQL.

---

# 23. SPARK — `PushedFilters` AND `PartitionFilters`

Use a practical Spark example.

Explain how to inspect:

```text
PushedFilters
PartitionFilters
```

from the query plan.

Show an example of:

```python
df.explain("formatted")
```

and explain what the learner should inspect.

Do NOT re-teach Spark internals from Module 2.14.

Focus only on pushdown verification.

---

# 24. PYARROW DATASET FILTERS

Demonstrate PyArrow dataset filtering.

Example:

```python
import pyarrow.dataset as ds

dataset = ds.dataset("sales/", format="parquet")

table = dataset.to_table(
    columns=["customer_id", "revenue"],
    filter=ds.field("country") == "IN",
)
```

Explain:

- column selection;
- filters;
- partition filtering;
- physical file/row-group skipping where supported.

Again emphasize verification rather than assumptions.

---

# 25. WAREHOUSE BYTES-SCANNED STATISTICS

Explain how analytical warehouses expose scan metrics.

Teach the learner to inspect:

```text
bytes scanned
bytes processed
partitions scanned
execution time
query plan
```

Use a generic warehouse example if the roadmap does not specify one.

Do not invent provider-specific syntax unless clearly marked as an example.

---

# 26. PART 7 — WHAT BREAKS PUSHDOWN

This section must be extremely practical.

Teach each blocker separately.

---

## 26.1 Python UDFs

Explain why:

```text
storage engine
    ↓
cannot understand arbitrary Python function
```

can prevent pushdown.

Example:

```python
df.filter(my_python_function(df["country"]))
```

Explain the difference between:

```text
engine-understandable expression
```

and:

```text
opaque Python logic
```

---

# 27. FUNCTIONS ON FILTERED COLUMNS

Example:

```sql
WHERE LOWER(country) = 'india'
```

or:

```sql
WHERE DATE(timestamp_column) = ...
```

Explain why wrapping columns in functions can prevent efficient use of:

- indexes;
- partition metadata;
- statistics;
- pruning.

Then show a more pushdown-friendly alternative where appropriate.

Do not claim every database behaves identically.

Explicitly state that exact optimizer behavior is engine-dependent.

---

# 28. CASTS ON FILTERED COLUMNS

Explain examples such as:

```sql
WHERE CAST(event_date AS DATE) = ...
```

and why casts can interfere with partition pruning or index usage depending on the engine and data types.

Show how matching types can help.

---

# 29. FILTERING ON DERIVED COLUMNS

Explain:

```text
partition column:
event_date
```

versus:

```text
derived expression:
year(event_date)
```

Explain why filtering directly on the physical partition key may enable better pruning.

Use practical examples.

---

# 30. TYPE MISMATCHES

Explain why:

```text
integer partition column
vs
string filter value
```

can cause problems depending on the engine.

Teach the learner to keep filter types aligned with storage types.

---

# 31. OR CONDITIONS

Explain why:

```sql
WHERE country = 'IN'
   OR customer_type = 'premium'
```

may be harder to optimize than simpler predicates.

Do NOT claim that `OR` always prevents pushdown.

Teach:

> The optimizer may still push parts of the predicate depending on engine capabilities.

The learner must learn to inspect the actual plan.

---

# 32. FILTERING AFTER `collect()`

This is mandatory.

Show:

```text
Remote/distributed dataset
    ↓
collect()
    ↓
local Python process
    ↓
filter
```

versus:

```text
Filter
    ↓
collect only required rows
```

Explain why filtering after `collect()` defeats the purpose of pushdown.

---

# 33. PUSHdown BLOCKER DEBUGGING WORKFLOW

Create a repeatable debugging framework:

```text
1. Identify the filter
2. Identify the storage/source
3. Inspect the logical plan
4. Inspect the optimized plan
5. Inspect the physical plan
6. Identify whether filters are pushed
7. Check partition/file statistics
8. Check data types
9. Check functions/casts/UDFs
10. Measure bytes scanned
11. Fix one blocker
12. Re-run
13. Compare evidence
```

This should become a key production skill.

---

# 34. PART 8 — DATA LAYOUT THAT ENABLES PUSHdown

Explain why query design alone is not enough.

Physical data layout matters.

Cover:

## Sorting

Explain why sorting by common filter columns can improve selectivity of statistics.

---

## Clustering

Explain clustering and why it can improve file-level/row-group-level skipping.

Connect this to Module 2.15.

Do not re-teach table-format compaction and clustering from scratch.

---

## Selective Statistics

Explain:

```text
good statistics
→ better pruning
→ fewer files/row groups read
```

Discuss:

- min/max;
- partition metadata;
- file statistics;
- bloom filters.

---

# 35. DATA LAYOUT EXAMPLE

Create an example where:

### Poor layout

```text
Files contain random countries.
```

### Better layout

```text
Files are clustered/sorted by country.
```

Show why:

```text
WHERE country = 'IN'
```

can become more selective.

Do not claim perfect clustering automatically guarantees perfect pruning.

---

# 36. PART 9 — LIMIT PUSHdown

Introduce advanced pushdown.

Explain:

```sql
SELECT *
FROM events
WHERE country = 'IN'
LIMIT 100;
```

Discuss when the engine can avoid processing more data than necessary.

Explain that exact behavior depends on:

- source;
- ordering;
- query semantics;
- engine;
- distributed execution.

Do not claim that every `LIMIT` is automatically pushed to storage.

---

# 37. AGGREGATE PUSHdown

Explain the concept:

```sql
SELECT COUNT(*)
FROM sales
WHERE country = 'IN';
```

Discuss how aggregation may sometimes be partially or fully pushed toward the data source.

Explain:

- partial aggregation;
- local aggregation;
- remote aggregation;
- source capabilities.

Keep this conceptual but practical.

---

# 38. JOIN PUSHdown

Explain what join pushdown means in systems where the source/optimizer can perform the join closer to the data.

Discuss:

- database joins;
- JDBC pushdown;
- federated engines;
- distributed joins.

Explain why moving computation closer to the source can reduce data transfer.

Do not imply that every engine can push arbitrary joins.

---

# 39. PART 10 — DYNAMIC FILTERING AND RUNTIME FILTERS

This is a mandatory advanced topic.

Explain:

> A query can sometimes derive filter information at runtime from one side of a join and use it to avoid scanning irrelevant data on the other side.

Use a simple example:

```text
Large fact table
        JOIN
Small dimension table
```

Explain how the small side can provide filtering information.

---

# 40. DYNAMIC PARTITION PRUNING

Use a Spark/lakehouse-style conceptual example.

Explain:

```text
Dimension:
country = selected countries

Fact table:
partitioned by country
```

The engine can potentially determine relevant partitions dynamically.

Explain:

```text
Static pruning
vs
Dynamic pruning
```

Clearly distinguish them.

---

# 41. PART 11 — LATE MATERIALIZATION

Explain:

> Late materialization means delaying retrieval of expensive/full column data until after filtering has narrowed down the relevant records.

Use a conceptual example:

```text
Step 1:
Read cheap filter columns

Step 2:
Identify matching rows

Step 3:
Read expensive payload columns only for matches
```

Explain why this can reduce:

- I/O;
- memory;
- decompression;
- CPU.

Connect this to columnar systems.

---

# 42. PART 12 — SCAN AUDITS

This is a critical production topic.

Teach:

> A scan audit measures how much data a production query/job actually reads compared with how much data it truly needs.

Introduce:

```text
Bytes scanned
vs
Bytes needed
```

Create the concept:

```text
Scan efficiency
=
bytes actually needed / bytes scanned
```

Clearly state that this is a useful analytical metric, not a universal industry-standard metric.

---

# 43. SCAN-AUDIT SCRIPT

Build a practical Python-based scan-audit design.

The audit should capture, where available:

```text
query/job
dataset
date
bytes scanned
bytes returned
columns requested
partitions scanned
runtime
engine
cost estimate
```

Then identify:

```text
Top 10 worst scans
```

Do not require an actual cloud provider account.

Provide a local/mock implementation where necessary.

---

# 44. WORST-OFFENDER ANALYSIS

Teach how to prioritize optimization.

For example:

```text
Query A:
1 TB scanned
10 GB needed

Query B:
100 GB scanned
90 GB needed

Query A should be investigated first.
```

Explain why absolute waste and business frequency both matter.

Teach prioritization using:

```text
scan volume
×
query frequency
×
cost
×
business criticality
```

Present this as a practical prioritization heuristic, not a universal formula.

---

# 45. PART 13 — PUSHdown AND COST

Connect pushdown directly to Module 2.17 cost concepts.

Explain:

```text
Better pruning
→ fewer bytes scanned
→ lower compute/storage processing
→ lower runtime
→ lower cost
```

For bytes-scanned-priced systems:

```text
Cost ∝ bytes scanned
```

where applicable.

Do not claim this pricing model applies universally.

---

# 46. COST-SAVING CASE STUDY

Create an example:

```text
Before:
10 TB scanned per run

After:
1 TB scanned per run
```

Calculate:

```text
90% reduction in scanned data
```

Then explain:

- runtime impact;
- memory impact;
- compute impact;
- cost impact.

If pricing is introduced, clearly label it as illustrative.

---

# 47. CROSS-ENGINE COMPARISON

Create a useful comparison table:

| Engine | Projection | Predicate Pushdown | Partition Pruning | Verification |
|---|---|---|---|---|
| Polars | ... | ... | ... | `explain()` |
| DuckDB | ... | ... | ... | `EXPLAIN ANALYZE` |
| Spark | ... | ... | ... | `PushedFilters`, `PartitionFilters` |
| PyArrow | ... | ... | ... | dataset/filter behavior |
| Warehouse | ... | ... | ... | query plan/bytes scanned |

Do not claim feature parity where it does not exist.

Use the table to teach the learner how to reason across engines.

---

# 48. COMPLETE END-TO-END CASE STUDY

Create a realistic production scenario.

Example style:

```text
A company has a 50 TB customer-events lake.

A daily query needs:
- 3 columns
- 1 day of data
- one country
- a subset of customers
```

Walk through:

```text
1. Initial query
2. Measure bytes scanned
3. Inspect plan
4. Identify unnecessary columns
5. Identify missing partition filter
6. Identify a function blocking pruning
7. Fix projection
8. Fix predicate
9. Improve layout
10. Verify row/file pruning
11. Inspect runtime
12. Calculate scan reduction
13. Calculate cost impact
14. Document the optimization
```

The learner should see the complete workflow.

---

# 49. HANDS-ON LAB

Create a substantial local hands-on project aligned with the roadmap.

The roadmap requires the learner to build a:

> **Scan audit**

for the ten most frequent queries/jobs.

The lab must include:

### Exercise 1 — Build a scan audit

Track:

```text
query/job
bytes scanned
bytes needed/result size
runtime
columns
partitions
```

---

### Exercise 2 — Fix three worst offenders

Examples:

- add partition filters;
- remove a UDF from a filter;
- avoid casting a partition column;
- cluster/sort on a filter column;
- eliminate unnecessary columns.

---

### Exercise 3 — Demonstrate the full pushdown stack

For one query demonstrate:

```text
API filter
→ PostgreSQL WHERE
→ table-format metadata
→ Parquet row-group pruning
→ column pruning
```

Provide evidence from each layer where practical.

---

### Exercise 4 — Dynamic partition pruning

Build a small Spark or DuckDB example where runtime filtering can be demonstrated.

---

### Exercise 5 — Calculate cost savings

Calculate the cost impact of reduced bytes scanned under an explicitly stated illustrative pricing model.

These exercises must follow the roadmap.

---

# 50. FAILURE-INJECTION LABS

Include controlled failure scenarios.

At minimum:

## Failure 1 — `SELECT *`

A query only needs three columns but reads every column.

Learner must identify and fix it.

---

## Failure 2 — Missing partition filter

A query accesses one day but scans an entire partitioned dataset.

---

## Failure 3 — Function blocks pruning

Example:

```sql
WHERE DATE(timestamp_column) = ...
```

Learner must investigate whether the transformation prevents efficient pruning.

---

## Failure 4 — Python UDF

A filter uses an opaque Python function.

Learner must explain why pushdown may be lost.

---

## Failure 5 — Type mismatch

Partition column and filter literal use incompatible representations.

---

## Failure 6 — Filter after collect

The pipeline retrieves a huge dataset and filters only after bringing it into Python.

---

## Failure 7 — Poor physical layout

The logical query is correct, but files contain highly mixed values and statistics are not selective.

Learner must reason about sorting/clustering.

For every failure:

```text
Symptoms
→ Investigation
→ Plan evidence
→ Root cause
→ Fix
→ Verification
→ Prevention
```

---

# 51. CODING REQUIREMENTS

Use realistic examples in:

```text
Python
SQL
Polars
DuckDB
PyArrow
Spark
```

Use shell commands when needed.

Every code example should have:

1. Purpose
2. Code
3. Expected result/behavior
4. Explanation
5. Performance implication
6. Production relevance

Do not add code simply to increase length.

---

# 52. EXPERIMENTAL REQUIREMENT

Whenever possible, teach the learner to compare:

```text
Before
vs
After
```

Record:

```text
rows scanned
columns scanned
files scanned
partitions scanned
bytes scanned
runtime
memory
cost
```

The optimization is not considered complete until the learner can show evidence.

---

# 53. BENCHMARKING MINDSET

This topic comes before Module 2.21's dedicated benchmarking topic.

Therefore, do not fully teach Topic 06 benchmarking.

Instead introduce the minimum measurement discipline:

```text
Baseline
→ Change
→ Measure
→ Compare
```

Explain that rigorous benchmark methodology will be covered later.

---

# 54. PRODUCTION DEBUGGING WORKFLOW

Create a reusable checklist:

```text
1. Define the query goal
2. Identify required rows
3. Identify required columns
4. Inspect physical data layout
5. Inspect partitioning
6. Inspect logical plan
7. Inspect optimized plan
8. Inspect physical plan
9. Verify pushdown
10. Measure bytes scanned
11. Identify blockers
12. Fix one blocker
13. Re-run
14. Compare metrics
15. Calculate cost impact
16. Document the change
```

This checklist should become one of the main takeaways.

---

# 55. COMMON MISTAKES

Create a dedicated section covering:

- `SELECT *`;
- filtering after loading into pandas;
- filtering after `collect()`;
- assuming pushdown happened without checking;
- wrapping partition columns in functions;
- unnecessary casts;
- type mismatches;
- opaque Python UDFs;
- filtering on derived columns;
- poor partitioning;
- poor clustering/sorting;
- ignoring row-group statistics;
- ignoring bytes-scanned metrics;
- optimizing low-volume queries instead of high-volume offenders;
- confusing logical plan with actual physical I/O;
- assuming all engines behave identically;
- claiming a cost reduction without measuring bytes scanned.

---

# 56. PRODUCTION TRADE-OFFS

Explain important trade-offs.

Examples:

### More partitions vs partition explosion

### Sorting/clustering cost vs query savings

### Additional metadata vs metadata maintenance

### Bloom filters vs storage/metadata overhead

### Predicate complexity vs optimizer effectiveness

### Pushdown optimization vs query portability

### Data layout optimization vs ingestion cost

### Aggressive pruning vs workload flexibility

### Query performance vs write performance

Make clear that a pushdown-friendly design must be evaluated against the overall workload.

---

# 57. ARCHITECTURAL DECISION FRAMEWORK

Give the learner a practical framework:

```text
Do I read unnecessary columns?
        ↓
Fix projection

Do I read unnecessary partitions?
        ↓
Fix partition filters

Do I read unnecessary files?
        ↓
Improve partitioning/layout/statistics

Do I read unnecessary row groups?
        ↓
Improve predicates/layout/statistics

Is the filter not pushed?
        ↓
Inspect plan and remove blocker

Is the query still expensive?
        ↓
Inspect joins/aggregations/runtime filtering

Is the scan still huge?
        ↓
Run a scan audit

Is the scan reduction meaningful?
        ↓
Measure performance and cost
```

---

# 58. TESTING REQUIREMENT

Teach how to test that an optimization preserves correctness.

Include examples comparing:

```text
Before optimization
vs
After optimization
```

Validate:

- row counts;
- schema;
- values;
- aggregates;
- null behavior;
- edge cases.

Explain that:

> A query that is faster but returns incorrect data is not an optimization.

---

# 59. CHECKPOINT

At the end, include the roadmap checkpoint:

```text
[ ] Explain projection pruning
[ ] Explain predicate pushdown
[ ] Explain partition pruning
[ ] Verify pushdown in Polars
[ ] Verify pushdown in DuckDB
[ ] Verify pushdown in Spark
[ ] Verify filtering in PyArrow
[ ] Inspect warehouse scan metrics
[ ] Identify pushdown blockers
[ ] Fix pushdown blockers
[ ] Run a scan audit
[ ] Quantify savings
```

These requirements are explicitly defined by the roadmap.

Then add practical self-assessment questions.

---

# 60. ENGINEERING QUESTIONS

At the end include questions such as:

- What is projection pruning?
- What is predicate pushdown?
- What is partition pruning?
- Why is reading fewer columns useful?
- Why is filtering at the source better than filtering in Python?
- How do Parquet statistics help?
- What is a row group?
- How do bloom filters help?
- What can prevent pushdown?
- How do you verify pushdown?
- What is dynamic filtering?
- What is dynamic partition pruning?
- What is late materialization?
- How do you perform a scan audit?
- How does pushdown reduce cloud cost?

These should reinforce understanding and should not replace the module's detailed teaching.

---

# 61. GLOSSARY

Include a concise glossary covering relevant terms:

- projection;
- predicate;
- predicate pushdown;
- projection pruning;
- partition pruning;
- file pruning;
- row-group pruning;
- page index;
- bloom filter;
- statistics;
- min/max statistics;
- manifest;
- runtime filter;
- dynamic filtering;
- dynamic partition pruning;
- late materialization;
- scan;
- bytes scanned;
- bytes returned;
- clustering;
- sorting;
- pushdown blocker;
- physical plan;
- logical plan.

---

# 62. FINAL MENTAL MODEL

End the module with:

```text
QUESTION
"What data do I actually need?"

        ↓

COLUMNS
"What columns do I need?"

        ↓

PARTITIONS
"What partitions can I skip?"

        ↓

FILES
"What files can I skip?"

        ↓

ROW GROUPS
"What row groups can I skip?"

        ↓

ROWS
"What rows can I avoid reading?"

        ↓

PLAN
"Did the engine actually push this down?"

        ↓

MEASURE
"How many bytes did I scan?"

        ↓

COST
"What did that scan cost?"

        ↓

OPTIMIZE
"Can I make the next scan smaller?"
```

The learner must leave the module understanding:

> **The best optimization is often the data you never read.**

---

# 63. ROADMAP COVERAGE AUDIT

Before finalizing the file, internally verify every requirement:

```text
[ ] Projection pruning
[ ] Predicate pushdown
[ ] Partition pruning
[ ] API filters
[ ] Database WHERE pushdown
[ ] JDBC pushdown
[ ] Table-format metadata
[ ] Manifest pruning
[ ] File statistics
[ ] Parquet row-group statistics
[ ] Page indexes
[ ] Bloom filters
[ ] In-engine filtering
[ ] Polars explain()
[ ] DuckDB EXPLAIN ANALYZE
[ ] Spark PushedFilters
[ ] Spark PartitionFilters
[ ] PyArrow dataset filters
[ ] Warehouse bytes-scanned statistics
[ ] Python UDF blocker
[ ] Function-on-column blocker
[ ] Cast blocker
[ ] Derived-column blocker
[ ] Type mismatch blocker
[ ] OR-condition limitations
[ ] Filter-after-collect problem
[ ] Sorting
[ ] Clustering
[ ] Selective statistics
[ ] Limit pushdown
[ ] Aggregate pushdown
[ ] Join pushdown
[ ] Dynamic filtering
[ ] Runtime filters
[ ] Dynamic partition pruning
[ ] Late materialization
[ ] Scan audits
[ ] Bytes scanned vs bytes needed
[ ] Worst-offender analysis
[ ] Pushdown and cloud cost
[ ] Cross-engine reasoning
[ ] Hands-on scan audit
[ ] Three worst-offender fixes
[ ] Full pushdown-stack demonstration
[ ] Dynamic partition pruning exercise
[ ] Cost-saving calculation
[ ] Failure-injection exercises
[ ] Correctness validation
[ ] Production debugging workflow
[ ] Checkpoint
[ ] Glossary
```

If anything is missing, add it before completing the file.

---

# 64. TECHNICAL ACCURACY REQUIREMENT

Be precise.

Do NOT claim:

> "This syntax always causes a full scan."

Instead explain:

> "This transformation can prevent or reduce pushdown depending on the engine, data types, optimizer, and physical layout. Inspect the actual plan and scan metrics."

Similarly:

- do not claim all databases support the same pushdown behavior;
- do not claim all Parquet readers use every available statistic;
- do not claim Bloom filters are always present;
- do not claim `LIMIT` is always pushed to storage;
- do not claim joins are always pushed down;
- do not claim dynamic partition pruning is universally available;
- do not claim clustering guarantees pruning.

Distinguish:

```text
Logical possibility
vs
Optimizer behavior
vs
Physical execution
vs
Measured evidence
```

This distinction is essential for production-level Data Engineering.

---

# 65. VERSION AND ENGINE AWARENESS

Where syntax or optimizer behavior is version-dependent:

- state that behavior can vary by engine/version;
- avoid inventing exact output;
- teach the learner how to inspect the actual plan;
- prefer official engine semantics when known;
- do not fabricate benchmark results.

The objective is to teach **reasoning and verification**, not memorization of one engine's output format.

---

# 66. DO NOT RE-TEACH OTHER MODULES

This is Topic 02 of Module 2.21.

Do NOT fully re-teach:

- Parquet internals from Module 2.5;
- database indexing from Module 2.6;
- Spark architecture from Module 2.14;
- lakehouse table formats from Module 2.15;
- warehouse pricing from Module 2.17;
- rigorous benchmarking from Topic 06;
- cost optimization from Topic 07.

Instead, reference previous knowledge where appropriate and explain only the pieces required to understand pushdown and pruning.

For example:

> "You learned Parquet row groups and statistics in Module 2.5. Here we use them to understand how a query can skip row groups."

This keeps the module focused.

---

# 67. FILE-SCOPE RESTRICTION — ABSOLUTE

You may modify **ONLY**:

```text
21-Performance-Scaling-and-Cost-Optimization/02-predicate-pushdown-and-projection-pruning.md
```

Do NOT modify:

```text
README.md
01-estimating-data-size-and-memory-footprint.md
03-parallel-dataframes-with-dask.md
04-ray-data-overview.md
05-numba-and-cython-for-hot-loops.md
06-benchmarking-pipelines.md
07-compute-cost-optimization.md
practice-questions.md
```

Do NOT:

- create other Markdown files;
- create new folders;
- modify the roadmap;
- modify Topic 01;
- modify Topic 03–07;
- modify practice questions;
- create unrelated artifacts.

If you discover errors or improvements in other files, leave them untouched.

---

# 68. FINAL EXECUTION INSTRUCTIONS

Execute the task in this exact order.

### Step 1

Read and analyze the Module 2.21 roadmap.

### Step 2

Extract every Topic 02 requirement.

### Step 3

Design the complete learning progression from basic → intermediate → advanced.

### Step 4

Write the complete learning module with detailed explanations.

### Step 5

Add practical Python, SQL, Polars, DuckDB, PyArrow, and Spark examples where appropriate.

### Step 6

Add plan-verification examples and explain what evidence the learner should inspect.

### Step 7

Add pushdown-blocker troubleshooting.

### Step 8

Add dynamic filtering, late materialization, scan auditing, and cost analysis.

### Step 9

Add the complete hands-on scan-audit laboratory.

### Step 10

Add failure-injection scenarios.

### Step 11

Add correctness validation and production best practices.

### Step 12

Perform the complete roadmap coverage audit.

### Step 13

Write the final learning module ONLY into:

```text
21-Performance-Scaling-and-Cost-Optimization/02-predicate-pushdown-and-projection-pruning.md
```

### Step 14

Verify that no other file or folder has been modified.

### Step 15

Return only a concise completion summary containing:

- target file updated;
- major concepts covered;
- confirmation that all Topic 02 roadmap requirements were covered;
- confirmation that no other files were modified.

**Do not modify anything outside the target file.**