# Incremental Processing and Backfills

> **Stage 2 — Python for Data Engineering**  
> **Module 2.12 — Transformation Patterns and Pipeline Design**  
> **Topic 03 — Incremental Processing and Backfills**

---

## 1. Learning Objectives

By the end of this chapter, you should be able to:

- explain full rebuilds versus incremental transformations;
- explain what “incremental” actually means;
- implement partition-based incremental processing;
- implement watermark-based processing;
- use upstream `_loaded_at` as a transformation-side change signal;
- distinguish event time, business time, load time, and execution time;
- identify affected downstream partitions rather than merely processing the execution date;
- propagate changes through a dependency graph;
- design incremental aggregations;
- distinguish additive and non-additive aggregates;
- design safe historical backfills;
- bound backfill parallelism;
- protect normal production workloads from backfills;
- use shadow/blue-green backfill targets;
- reason about atomic cutover and rollback;
- track transformation logic versions;
- estimate backfill cost and runtime;
- recover safely from failed partitions;
- prove incremental output is equivalent to a full rebuild;
- debug missed changes, incorrect partitions, resource exhaustion, and concurrency problems;
- explain incremental/backfill architecture at senior Data Engineer level.

The central progression is:

```text
Full rebuild
    ↓
Incremental processing
    ↓
Affected-data identification
    ↓
Dependency-aware recomputation
    ↓
Backfills
    ↓
Safe backfills
    ↓
Shadow validation
    ↓
Atomic cutover
    ↓
Production operations
```

The central principle is:

> **Incremental processing reduces unnecessary computation, but it introduces state and dependency complexity. The goal is not merely to process less data; it is to process the minimum necessary data while preserving the correctness guarantees of a full rebuild.**

---

# 2. Prerequisites

This topic depends on Topics 01 and 02.

You should already understand:

- deterministic pipeline structure;
- `RunContext`;
- logical dates and data intervals;
- pure transformations;
- step contracts;
- partition-scoped processing;
- append and overwrite;
- merge/upsert;
- deduplication;
- idempotent loads;
- version-aware updates.

A useful mental connection is:

```text
Topic 01
How should transformation code be structured?
        ↓
Topic 02
How should each run load data safely?
        ↓
Topic 03
What data actually needs to be processed again?
```

We will briefly reinforce prerequisites when needed, but this chapter focuses on **incremental computation and historical recomputation**.

---

# 3. Why Incremental Processing Exists

Imagine a pipeline with:

```text
10 TB of historical source data
```

Suppose only:

```text
10 GB
```

changed since yesterday.

A full rebuild processes:

```text
10 TB
```

even though only:

```text
10 GB
```

is relevant to the new result.

That creates unnecessary:

- CPU consumption;
- memory consumption;
- storage I/O;
- database reads;
- network transfer;
- warehouse compute;
- runtime;
- operational exposure.

Incremental processing attempts to exploit the difference:

```text
10 TB historical data
+
10 GB changed data
        ↓
identify affected outputs
        ↓
process only affected data
```

But there is a trade-off.

Full rebuild:

```text
simple
+
expensive
```

Incremental:

```text
cheaper
+
more state/dependency complexity
```

Therefore:

> **Incremental processing is a correctness problem as much as a performance problem.**

---

# 4. Full Rebuild vs Incremental Processing

## 4.1 Full rebuild

The conceptual flow is:

```text
Read all historical data
        ↓
Transform all historical data
        ↓
Write complete target
```

Example:

```text
10 TB source
    ↓
10 TB transformation
    ↓
10 TB target
```

### Advantages

- simple reasoning;
- fewer incremental state rules;
- easy to reproduce;
- naturally incorporates historical corrections;
- easier to compare against a clean reference;
- fewer dependency-specific edge cases.

### Disadvantages

- expensive at scale;
- longer runtime;
- higher I/O;
- larger failure surface;
- more resource consumption;
- can compete with production workloads.

A full rebuild can still be the correct production choice for small or easily recomputable datasets.

---

## 4.2 Incremental processing

The conceptual flow is:

```text
Existing target
      +
changed input
      ↓
identify affected output
      ↓
recompute affected output
      ↓
update target
```

Example:

```text
10 TB historical dataset
+
10 GB changed data
        ↓
identify affected partitions
        ↓
process affected partitions
        ↓
retain unaffected partitions
```

### Advantages

- lower compute;
- lower I/O;
- shorter normal-run runtime;
- better scalability.

### Costs

- more state;
- more dependency reasoning;
- more complex failure recovery;
- risk of silently missing changed data;
- more difficult historical correctness;
- more complicated backfills.

---

# 5. What Does “Incremental” Actually Mean?

Incremental processing does **not** have one universal implementation.

It can mean:

```text
process new partitions
```

or:

```text
process changed partitions
```

or:

```text
process rows after a watermark
```

or:

```text
process changed entities
```

or:

```text
process a lookback window
```

or:

```text
recompute affected aggregate groups
```

or:

```text
propagate changed upstream partitions to downstream partitions
```

or:

```text
reprocess a historical range during a backfill
```

A dangerous beginner definition is:

```sql
WHERE order_date = CURRENT_DATE - 1
```

That is only correct when the business contract guarantees that yesterday's output can only depend on yesterday's input.

Real systems often violate that assumption.

---

# 6. Execution Date vs Affected Data Date

This distinction is fundamental.

Suppose:

```text
Execution date = 2025-03-05
```

but an order with:

```text
order_date = 2025-03-01
_loaded_at = 2025-03-05
```

arrives today.

If daily revenue is partitioned by:

```text
order_date
```

the affected partition is:

```text
2025-03-01
```

not:

```text
2025-03-05
```

Therefore:

```text
execution date
```

answers:

> When did the pipeline run?

while:

```text
affected data date
```

answers:

> Which output needs to change because of this input?

These are not interchangeable.

---

# 7. Partition-Based Incremental Processing

A partition is a logical subset of a dataset.

For example:

```text
orders/
    date=2025-03-01/
    date=2025-03-02/
    date=2025-03-03/
```

The partition key is:

```text
date
```

A partition-scoped transformation can process one interval at a time.

Conceptually:

```python
def process_partition(run_date):
    bronze = read_bronze(run_date)
    silver = transform(bronze)
    write_partition(silver, run_date)
```

The important property is:

```text
one input interval
        ↓
one deterministic output interval
```

This makes retry and replacement easier.

---

# 8. Partition-Scoped Processing

Suppose:

```text
2025-03-10
```

needs recomputation.

A partition-oriented pipeline can:

```text
read source data for 2025-03-10
        ↓
transform
        ↓
validate
        ↓
overwrite output partition 2025-03-10
```

Unrelated partitions remain untouched.

This is powerful because the unit of computation is also the unit of replacement.

A useful design is:

```text
dataset
+
partition
+
logic version
```

as a processing identity.

---

# 9. Why “Yesterday Only” Fails

Suppose the pipeline runs on:

```text
2025-03-05
```

and processes:

```text
order_date = 2025-03-04
```

Later, a corrected order arrives:

```text
order_date = 2025-03-01
_loaded_at = 2025-03-05
```

If the transformation only processes:

```text
order_date = 2025-03-04
```

the corrected order is ignored.

The result is stale.

Correct incremental processing must determine:

```text
which target output is affected?
```

rather than assuming:

```text
execution date = affected date
```

---

# 10. Watermark-Based Incremental Processing

A watermark represents progress through an ordered source attribute.

A common field is:

```text
_loaded_at
```

Example:

```text
_loaded_at
---------------------
2025-03-01 10:00:00
2025-03-01 11:00:00
2025-03-01 12:00:00
```

Suppose the previous watermark is:

```text
2025-03-01 11:00:00
```

The next processing interval might be:

```sql
WHERE _loaded_at > :previous_watermark
  AND _loaded_at <= :new_watermark
```

If:

```text
previous = 11:00
new      = 12:00
```

then the interval is:

```text
(11:00, 12:00]
```

This means:

```text
11:00 excluded
12:00 included
```

The exact convention must be explicit.

---

# 11. Watermark Boundary Design

A watermark implementation must define:

- lower-bound inclusivity;
- upper-bound inclusivity;
- timestamp precision;
- timezone;
- clock semantics;
- duplicate boundary records;
- retry behavior;
- late commits;
- null watermark behavior.

A robust convention is often:

```text
(previous_watermark, current_watermark]
```

because it avoids processing the exact same boundary value twice.

But even this is not enough if the source can produce multiple records with identical timestamps and the timestamp is not a unique ordering field.

In that situation, a compound cursor may be safer:

```text
(timestamp, unique_id)
```

The general rule is:

> **A watermark must have clearly defined ordering semantics, not merely a timestamp column.**

---

# 12. Watermark vs Partition Incremental

These solve related but different problems.

| Pattern | Main unit |
|---|---|
| Partition incremental | Data partition |
| Watermark incremental | Source progress |
| Entity incremental | Changed business entities |
| Dependency incremental | Affected downstream outputs |

A pipeline may combine them:

```text
Use _loaded_at watermark
        ↓
find changed source rows
        ↓
extract their business dates
        ↓
recompute affected partitions
```

This is often more powerful than choosing one technique exclusively.

---

# 13. Upstream `_loaded_at`

Suppose silver contains:

```text
order_id
order_date
_loaded_at
amount
```

Example:

```text
order_id | order_date  | _loaded_at
---------+-------------+---------------------
101      | 2025-03-01  | 2025-03-01 10:00
102      | 2025-03-01  | 2025-03-05 09:00
```

Order 102 belongs to:

```text
order_date = 2025-03-01
```

but was loaded on:

```text
2025-03-05
```

A downstream transformation can use `_loaded_at` to detect that the source row changed recently.

But `_loaded_at` does **not** mean:

```text
business event happened at _loaded_at
```

It means:

```text
the transformation system received or persisted the row at _loaded_at
```

This distinction is essential.

---

# 14. Event Time vs Load Time

Consider:

```text
event_time = 2025-03-01 08:00
_loaded_at  = 2025-03-05 10:00
```

Event time tells you:

```text
when the business event occurred
```

Load time tells you:

```text
when the pipeline saw/persisted it
```

For incremental detection:

```text
_loaded_at
```

may be useful.

For business partitioning:

```text
event_time
```

or:

```text
order_date
```

may be the correct attribute.

Do not use one timestamp for every semantic purpose.

---

# 15. Determining What Needs to Be Recomputed

The core question is:

> **What changed, and which outputs depend on that change?**

Consider four cases.

## Case A — New data for today's partition

```text
changed input → 2025-03-10
```

Recompute:

```text
2025-03-10
```

## Case B — Historical correction

```text
changed input → order_date=2025-03-01
```

Recompute:

```text
2025-03-01
```

even if execution is:

```text
2025-03-10
```

## Case C — Dimension change

A customer classification changes.

Potentially affected:

```text
many historical fact partitions
```

## Case D — Reference mapping change

A product category mapping changes.

Potentially:

```text
all historical records containing that product
```

The correct affected set is a dependency question.

---

# 16. Dependency-Aware Incremental Processing

Consider:

```text
bronze_orders
      ↓
silver_orders
      ↓
daily_revenue
      ↓
monthly_revenue
```

Suppose:

```text
silver_orders / date=2025-03-10
```

changes.

At minimum:

```text
daily_revenue / date=2025-03-10
```

is affected.

If monthly revenue is derived from daily revenue:

```text
monthly_revenue / month=2025-03
```

is also affected.

Therefore:

```text
changed upstream data
        ↓
affected direct outputs
        ↓
affected downstream outputs
```

This is change propagation.

---

# 17. Change Propagation

Suppose:

```text
orders
  ↓
daily_order_metrics
  ↓
weekly_metrics
  ↓
monthly_metrics
```

An order from:

```text
Monday
```

is corrected on:

```text
Friday
```

The affected outputs may be:

```text
Monday daily partition
        ↓
week containing Monday
        ↓
month containing Monday
```

The execution date is Friday.

The business impact date is Monday.

The downstream dependency graph determines the affected outputs.

---

# 18. Change Propagation Table

A useful planning table is:

| Changed object | Affected output | Reason |
|---|---|---|
| One order | Its order-date daily revenue | Order contributes to that date |
| One order | Its monthly revenue | Daily/monthly aggregation depends on order |
| Customer dimension | Customer-level aggregates | Customer attributes are inputs |
| Product mapping | Product/category aggregates | Classification changes |
| Reference FX rate | Converted revenue | Currency conversion changes |
| Historical source correction | Corresponding historical partition | Existing result becomes stale |

The important design question is:

> **Can we derive the affected output set deterministically from the changed input?**

If yes, incremental processing can often be made both efficient and explainable.

---

# 19. Incremental Aggregations

Aggregations require more reasoning than row-level transformations.

Suppose:

```text
orders
↓
SUM(amount)
```

Existing daily revenue:

```text
$1,000
```

A historical order changes:

```text
$100 → $150
```

The correct revenue becomes:

```text
$1,050
```

A naive incremental pipeline that only processes new orders may never discover the correction.

Therefore aggregate incrementality requires understanding:

```text
which groups changed
```

and:

```text
how changed rows alter group state
```

---

# 20. Additive Aggregations

Examples:

```text
SUM(revenue)
COUNT(order_id)
```

These are often easier to maintain incrementally.

For example:

```text
old sum = 1,000
new order = 100
```

Then:

```text
new sum = 1,100
```

For updates, however, you may need the old and new values:

```text
old amount = 100
new amount = 150
```

Then:

```text
new total
=
old total
- old amount
+ new amount
```

That requires sufficient state.

---

# 21. Average Is Not Simply Additive

Average is:

```text
AVG = SUM / COUNT
```

Therefore storing only:

```text
average
```

is insufficient for exact incremental maintenance.

Instead retain:

```text
sum
count
```

Then:

```text
average = sum / count
```

Example:

```text
sum = 300
count = 3
average = 100
```

Add a value:

```text
60
```

New state:

```text
sum = 360
count = 4
average = 90
```

The important lesson is:

> **Some non-additive metrics become incrementally maintainable if sufficient underlying state is stored.**

---

# 22. Count Distinct

Consider:

```text
COUNT(DISTINCT customer_id)
```

Suppose yesterday:

```text
customers = {A, B, C}
```

Today:

```text
customers = {B, C, D}
```

You cannot safely calculate:

```text
3 + 3 = 6
```

because B and C overlap.

The correct distinct set is:

```text
{A, B, C, D}
```

with count:

```text
4
```

Exact incremental distinct counting may require:

- maintaining sets;
- maintaining reusable state;
- recomputing affected groups;
- or using suitable sketches for approximate counting.

---

# 23. Median and Percentiles

Median is even less naturally additive.

Suppose:

```text
Day A values = [1, 2, 100]
median = 2
```

and:

```text
Day B values = [3, 4, 5]
median = 4
```

You cannot calculate the combined median as:

```text
(2 + 4) / 2
```

The combined values are:

```text
[1, 2, 3, 4, 5, 100]
```

Median:

```text
3.5
```

Therefore non-additive aggregates may require:

- recomputing affected groups;
- maintaining specialized state;
- approximate sketches;
- or full/partition rebuilds.

Do not force every metric into a naive incremental formula.

---

# 24. Incremental Strategies by Data Shape

| Data shape | Possible strategy |
|---|---|
| Append-only events | Process new partitions |
| Mutable entities | Process changed entities |
| Partitioned facts | Recompute affected partitions |
| Daily aggregates | Recompute affected groups/partitions |
| Slowly changing dimensions | Process changed entities and propagate impact |
| Small reference tables | Full refresh may be simpler |
| Large historical transformations | Partitioned incremental processing |

The choice depends on:

```text
volume
change frequency
dependency structure
correctness requirements
compute cost
operational complexity
```

---

# 25. Backfills

A **backfill** is a deliberate historical reprocessing operation.

Example:

```text
2024-01-01
     ↓
2025-01-01
```

is intentionally recomputed.

Backfills are not evidence that the pipeline failed.

They are normal operations in mature data platforms.

They are required whenever historical outputs need to reflect:

- corrected source data;
- corrected business logic;
- new fields;
- new sources;
- improved transformation logic;
- historical enrichment;
- repaired historical partitions.

---

# 26. Why Backfills Are Necessary

Imagine a bug in revenue logic:

```python
revenue = quantity * unit_price
```

was incorrectly implemented as:

```python
revenue = quantity + unit_price
```

A new version fixes the logic.

Running the corrected pipeline only for tomorrow does not repair:

```text
last year
```

The historical target is still wrong.

A backfill applies the corrected logic to the required historical range.

---

# 27. Types of Backfills

## 27.1 Bug-fix backfill

A historical transformation contained a defect.

```text
logic v1 → incorrect
logic v2 → corrected
```

Affected partitions need v2.

## 27.2 Logic-change backfill

Business rules changed.

Example:

```text
old revenue definition
→
new revenue definition
```

## 27.3 Schema backfill

A new column must be populated historically.

## 27.4 Source-data correction

The source corrected historical records.

## 27.5 New-source backfill

A new source becomes available and should populate historical periods.

## 27.6 Targeted backfill

Only selected partitions or entities are affected.

## 27.7 Full historical backfill

The entire historical range is recomputed.

The correct type depends on the scope of the change.

---

# 28. A Backfill Is a Production Deployment

A useful mental model is:

```text
Backfill
=
production computation
+
historical scope
```

Therefore a backfill needs:

```text
range definition
+
logic version
+
resource controls
+
validation
+
failure recovery
+
safe cutover
```

Do not treat a backfill as:

```text
"just run the script again for two years."
```

---

# 29. Safe Backfill Lifecycle

A production-safe lifecycle is:

```text
Plan
  ↓
Estimate
  ↓
Run shadow computation
  ↓
Validate
  ↓
Compare
  ↓
Cut over
  ↓
Monitor
  ↓
Retain rollback path
```

Before execution, define:

```text
start
end
input assumptions
logic version
target
parallelism
validation rules
rollback plan
```

---

# 30. Backfill Range Definition

A range should be explicit.

Prefer:

```text
start = 2024-01-01
end   = 2024-12-31
```

over:

```text
"last year"
```

Why?

Because reproducibility requires a precise interval.

Also define whether the end is:

```text
inclusive
```

or:

```text
exclusive
```

A common convention is:

```text
[start, end)
```

meaning:

```text
start included
end excluded
```

For example:

```text
[2025-01-01, 2025-02-01)
```

means the entire month of January.

---

# 31. Backfill Configuration

A conceptual backfill command is:

```bash
backfill \
  --pipeline orders_gold \
  --start 2024-01-01 \
  --end 2025-01-01 \
  --parallelism 4
```

The command should make the important operational inputs explicit.

A production implementation may additionally require:

```text
--logic-version
--target
--dry-run
--max-partitions
--resource-class
```

The exact CLI belongs to the surrounding pipeline framework; the key lesson is that backfill scope should not be hidden.

---

# 32. Bounded Parallelism

Suppose a backfill contains:

```text
10,000 partitions
```

A naive implementation might launch:

```text
10,000 workers
```

That can exhaust:

- CPU;
- memory;
- database connections;
- warehouse concurrency;
- storage bandwidth;
- network capacity.

Instead use bounded parallelism:

```text
10,000 partitions
        ↓
4 workers
```

or:

```text
10,000 partitions
        ↓
8 workers
```

The correct value depends on the workload.

---

# 33. Why More Workers Can Be Slower

Suppose one partition is I/O-heavy.

With:

```text
4 workers
```

the system may have sufficient storage bandwidth.

With:

```text
100 workers
```

all workers compete for the same bottleneck.

You can get:

```text
more contention
+
more queueing
+
more database pressure
+
more retries
=
longer total runtime
```

Therefore:

> **Bounded parallelism is a resource-management decision, not merely a concurrency setting.**

---

# 34. Python Example: Bounded Backfill Workers

A simple standard-library implementation:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta


def date_range(start: date, end: date):
    current = start

    while current < end:
        yield current
        current += timedelta(days=1)


def process_partition(partition_date: date) -> str:
    # Real code would read, transform, validate,
    # and atomically write this partition.
    return f"completed {partition_date}"


def run_backfill(
    start: date,
    end: date,
    max_workers: int = 4,
) -> list[str]:
    partitions = list(date_range(start, end))
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(process_partition, partition)
            for partition in partitions
        ]

        for future in as_completed(futures):
            results.append(future.result())

    return results
```

The important property is:

```text
max_workers = 4
```

not:

```text
one worker per partition
```

For CPU-heavy transformations, process-based or engine-native parallelism may be more appropriate. The correct execution model depends on the workload.

---

# 35. Resource Isolation

Backfills can accidentally starve normal production workloads.

Imagine:

```text
Production:
4 database connections

Backfill:
100 workers
```

If every backfill worker consumes a connection, normal production work may fail.

The system should distinguish:

```text
NORMAL PRODUCTION
        +
BACKFILL
```

Possible controls include:

- separate worker pools;
- separate queues;
- concurrency limits;
- lower-priority scheduling;
- database workload management;
- warehouse resource groups;
- separate compute;
- scheduled backfill windows.

---

# 36. Production and Backfill Coexistence

A useful conceptual design is:

```text
                 Scheduler
                    │
          ┌─────────┴─────────┐
          ↓                   ↓
   Production queue       Backfill queue
          ↓                   ↓
   normal workers        bounded workers
          ↓                   ↓
          └─────────┬─────────┘
                    ↓
               Data platform
```

The backfill must not be allowed to consume every available resource simply because historical work is large.

---

# 37. Shadow / Blue-Green Backfills

Instead of immediately replacing production data:

```text
production_gold
```

build:

```text
shadow_gold
```

using the new logic.

Conceptually:

```text
Historical source
       ↓
new transformation
       ↓
shadow_gold
```

Then compare:

```text
production_gold
       vs
shadow_gold
```

Only after validation should the new result become production.

---

# 38. Shadow Validation

Compare at several levels.

## Row counts

```text
production = 100,000,000
shadow     = 100,000,000
```

Equal counts are useful but insufficient.

## Key coverage

Compare:

```text
set(production.keys())
set(shadow.keys())
```

## Aggregates

Compare:

```text
SUM(revenue)
COUNT(order_id)
```

by relevant partitions.

## Null rates

Compare important columns.

## Hashes

For deterministic rows, calculate stable fingerprints.

## Business invariants

Examples:

```text
revenue >= 0
order_id unique
customer_id valid
```

The goal is not simply:

```text
same row count
```

but:

```text
same intended business result
```

---

# 39. Blue-Green Cutover

A conceptual blue-green arrangement is:

```text
Current:
gold_v1

New:
gold_v2
```

After validation:

```text
gold_v1
    ↓
cutover
    ↓
gold_v2 becomes current
```

Consumers should not observe a partially completed historical rebuild.

The exact implementation may use:

- atomic table swap;
- transactional rename;
- a view pointing to a versioned table;
- metadata-controlled table selection.

The storage technology determines which mechanism is available.

---

# 40. Atomic Swap and Cutover

Partial replacement is dangerous.

Imagine:

```text
100 historical partitions
```

and only:

```text
60
```

have been rebuilt.

If consumers read the same production target during the operation, they may see:

```text
60 partitions → new logic
40 partitions → old logic
```

That is a mixed-version dataset.

A safer approach is:

```text
build complete shadow target
        ↓
validate
        ↓
atomic cutover
```

Then the production target moves from one coherent state to another.

---

# 41. Rollback

A safe cutover should retain a rollback path when practical.

Example:

```text
gold_v1
gold_v2
```

After switching to:

```text
gold_v2
```

keep:

```text
gold_v1
```

long enough to verify production behavior.

If a serious defect is discovered:

```text
gold_v2
  ↓
rollback
  ↓
gold_v1
```

Rollback policy depends on storage and retention constraints, but it should be considered before cutover, not after an incident.

---

# 42. Versioned Logic Per Partition

Historical outputs may have been produced using:

```text
logic_version = 1
```

A corrected transformation may produce:

```text
logic_version = 2
```

A useful partition ledger is:

| dataset | partition | logic_version | status |
|---|---|---:|---|
| orders_gold | 2025-03-01 | 1 | complete |
| orders_gold | 2025-03-02 | 2 | complete |
| orders_gold | 2025-03-03 | 1 | complete |

Now you can ask:

> Which partitions were produced with logic version 1?

The answer can drive a targeted backfill.

---

# 43. Why Logic Versioning Matters

Logic versioning helps with:

### Reproducibility

You know which code semantics produced the output.

### Debugging

If a consumer reports a problem:

```text
partition = 2025-03-01
logic_version = 1
```

you have useful historical context.

### Auditing

You can explain when and why historical data changed.

### Targeted backfills

You can identify:

```text
all partitions where logic_version < 2
```

### Migration planning

You can measure progress:

```text
version 1 = 2,000 partitions
version 2 = 8,000 partitions
```

---

# 44. Logic Version Is Not Necessarily a Git Commit

A Git commit hash can be useful, but a transformation logic version is an operational data concept.

You may track:

```text
transform_version = 7
```

and separately retain:

```text
git_sha = abc123...
```

The important question is:

> **Can I identify the transformation semantics that produced this partition?**

---

# 45. Full-Refresh Escape Hatch

Incremental processing should not become dogma.

Sometimes:

```text
full rebuild
```

is safer.

Consider a full refresh when:

- the dataset is small;
- compute is cheap;
- the dependency graph is extremely complex;
- a massive logic change invalidates incremental assumptions;
- historical data is severely corrupted;
- the incremental implementation is harder to validate than a full rebuild.

A useful principle is:

> **Use incremental processing when it provides meaningful savings without creating unacceptable correctness complexity.**

---

# 46. Incremental vs Full Refresh Decision

Ask:

```text
How much data changes?
How much does the target cost to rebuild?
How complex are dependencies?
Can affected data be identified exactly?
Can incremental output be validated against a full rebuild?
How expensive is a full rebuild?
How frequently does logic change?
What is the correctness risk?
```

A simple decision table:

| Situation | Likely choice |
|---|---|
| Small table | Full refresh |
| Huge table, tiny changes | Incremental |
| Exact affected partitions known | Incremental |
| Complex global dependency | Consider full refresh |
| Historical corruption everywhere | Full refresh |
| Cheap compute, strict simplicity | Full refresh |
| Stable partitioned transformation | Incremental |

These are design heuristics, not absolute rules.

---

# 47. Backfill Cost and Time Estimation

A useful first-order estimate is:

```text
estimated time
≈
partitions × time per partition ÷ parallelism
```

Example:

```text
1,000 partitions
2 minutes/partition
10 workers
```

Estimate:

```text
1,000 × 2 / 10
=
200 minutes
≈ 3 hours 20 minutes
```

This is an estimate, not a physical law.

---

# 48. Backfill Overhead

Real systems add:

- worker startup;
- task scheduling;
- storage I/O;
- database contention;
- partition skew;
- retries;
- validation;
- commit time;
- metadata updates;
- failed partitions;
- resource throttling.

Therefore:

```text
estimated time
```

should be validated with representative benchmarks.

---

# 49. Better Backfill Estimation

A practical workflow:

```text
1. Select representative partitions.
2. Measure p50 processing time.
3. Measure p95/p99 processing time.
4. Estimate total work.
5. Apply realistic parallelism.
6. Add operational overhead.
7. Run a small pilot.
8. Re-estimate.
```

Do not use the fastest partition as the only benchmark.

Partition size skew can make a large backfill take much longer than:

```text
N × average
```

would suggest.

---

# 50. Idempotency During Backfills

Backfill partitions must be retryable.

Suppose:

```text
partition 2025-03-01
```

fails halfway through.

A safe design should allow:

```text
retry partition
```

without producing:

```text
duplicate output
```

or:

```text
mixed old/new files
```

This is why Topic 02's idempotent load patterns matter here.

A partition backfill should have:

```text
deterministic input
+
deterministic transformation
+
safe replacement
```

---

# 51. Determinism During Backfills

A historical transformation should not silently depend on:

```python
datetime.now()
```

or:

```python
random.random()
```

For example:

```python
def transform(df):
    df["processed_at"] = datetime.now()
    return df
```

Repeated backfills can produce different results.

Instead, pass the run context explicitly:

```python
def transform(df, run_context):
    processed_at = run_context.logical_time
    ...
```

The exact output contract depends on the pipeline, but the transformation should not accidentally depend on wall-clock execution time.

---

# 52. Backfill Failure and Recovery

Real failures include:

- worker crash;
- machine failure;
- out-of-memory;
- database timeout;
- storage failure;
- network failure;
- partial partition completion;
- duplicate execution;
- concurrent backfill;
- collision with normal production work.

For each failure, ask:

```text
What happened?
        ↓
What data may be affected?
        ↓
How do we detect it?
        ↓
How do we recover?
        ↓
How do we prevent corruption?
```

This turns recovery into a design property rather than an emergency improvisation.

---

# 53. Failed Partition Example

Suppose:

```text
100 partitions
```

are being rebuilt.

Partition:

```text
2025-04-17
```

fails.

Do not automatically mark the entire backfill successful.

Track:

```text
partition
status
attempts
logic_version
started_at
completed_at
error
```

Example:

| partition | status | attempts |
|---|---|---:|
| 2025-04-15 | complete | 1 |
| 2025-04-16 | complete | 1 |
| 2025-04-17 | failed | 2 |
| 2025-04-18 | complete | 1 |

The failed partition can then be retried independently.

---

# 54. Detecting Partial Completion

A dangerous state is:

```text
partition marked complete
```

when output was not durably written.

A safer sequence is:

```text
process
 ↓
write output
 ↓
validate output
 ↓
commit durable completion state
```

The metadata should only say:

```text
complete
```

after the output meets the defined durability/correctness contract.

This connects directly to the checkpoint and state concepts taught later in Topic 08.

---

# 55. Concurrent Backfills

Two workers may accidentally process:

```text
2025-04-17
```

at the same time.

Possible consequences:

- conflicting writes;
- wasted compute;
- inconsistent metadata;
- race conditions;
- last-writer-wins corruption.

Possible controls include:

```text
partition lock
lease
advisory lock
orchestrator concurrency policy
```

The exact mechanism depends on the storage/orchestration system.

The invariant should be:

> **At most one incompatible writer owns a production partition at a time.**

---

# 56. Incremental vs Full-Rebuild Equivalence

This is one of the strongest correctness tests in this topic.

For the same:

```text
input data
+
transformation logic version
```

we want:

```text
incremental result
=
full rebuild result
```

This does not mean the physical execution must be identical.

It means the semantic output should be equivalent.

---

# 57. Equivalence Example

Suppose we have:

```text
30 days of orders
```

Run A:

```text
full rebuild
```

Run B:

```text
day 1 incremental
day 2 incremental
...
day 30 incremental
```

Compare:

```text
row counts
primary keys
aggregates
stable row hashes
null rates
business invariants
```

If they differ, the incremental algorithm has a correctness problem or the comparison contract is incomplete.

---

# 58. Polars Reconciliation Example

A simple key-level reconciliation:

```python
import polars as pl


def compare_outputs(
    full: pl.DataFrame,
    incremental: pl.DataFrame,
) -> None:
    full_sorted = full.sort("order_id")
    incremental_sorted = incremental.sort("order_id")

    if full_sorted.shape != incremental_sorted.shape:
        raise AssertionError(
            f"Shape mismatch: "
            f"{full_sorted.shape} != {incremental_sorted.shape}"
        )

    if full_sorted.to_dicts() != incremental_sorted.to_dicts():
        raise AssertionError(
            "Incremental output differs from full rebuild."
        )
```

For production-scale data, avoid pulling enormous datasets into Python merely to compare them.

Use engine-native reconciliation where appropriate.

---

# 59. DuckDB Reconciliation Example

Suppose:

```text
full_rebuild
incremental_result
```

have the same schema.

A useful comparison is:

```sql
SELECT
    COUNT(*) AS row_count
FROM full_rebuild

EXCEPT

SELECT
    COUNT(*) AS row_count
FROM incremental_result;
```

For a more meaningful comparison, compare keys and values.

For example:

```sql
SELECT *
FROM full_rebuild

EXCEPT

SELECT *
FROM incremental_result;
```

and the reverse:

```sql
SELECT *
FROM incremental_result

EXCEPT

SELECT *
FROM full_rebuild;
```

Both should return zero rows under the comparison's null/type semantics.

---

# 60. Hash-Based Equivalence

For wide rows, stable row fingerprints can make comparisons easier.

Conceptually:

```text
canonical row
      ↓
stable serialization
      ↓
hash
```

Then compare:

```text
key
+
row_hash
```

This connects to Topic 05, where deterministic hashing is taught in depth.

Do not use arbitrary serialization that changes column order or null representation between implementations.

---

# 61. Practical Production Implementation

The following simplified project uses:

```text
bronze_orders
    ↓
silver_orders
    ↓
orders_gold
```

Input columns:

```text
order_id
customer_id
order_date
_loaded_at
amount
status
```

Goal:

```text
daily order revenue
```

Target grain:

```text
one row per order_date + customer_id
```

The implementation will demonstrate:

1. full rebuild;
2. partition incremental;
3. historical correction;
4. affected-partition detection;
5. recomputation;
6. backfill;
7. bounded parallelism;
8. failure/retry;
9. logic version;
10. shadow validation.

---

# 62. Sample Orders Data

```python
from datetime import date, datetime, timedelta

import polars as pl


orders = pl.DataFrame(
    {
        "order_id": [1, 2, 3, 4, 5, 6],
        "customer_id": ["A", "A", "B", "B", "C", "C"],
        "order_date": [
            date(2025, 3, 1),
            date(2025, 3, 1),
            date(2025, 3, 2),
            date(2025, 3, 2),
            date(2025, 3, 3),
            date(2025, 3, 3),
        ],
        "_loaded_at": [
            datetime(2025, 3, 1, 10),
            datetime(2025, 3, 1, 11),
            datetime(2025, 3, 2, 10),
            datetime(2025, 3, 2, 11),
            datetime(2025, 3, 3, 10),
            datetime(2025, 3, 3, 11),
        ],
        "amount": [100.0, 50.0, 75.0, 25.0, 200.0, 80.0],
        "status": [
            "paid",
            "paid",
            "paid",
            "cancelled",
            "paid",
            "paid",
        ],
    }
)
```

---

# 63. Full Rebuild

A simple reference implementation:

```python
def full_rebuild(orders: pl.DataFrame) -> pl.DataFrame:
    return (
        orders
        .filter(pl.col("status") == "paid")
        .group_by(["order_date", "customer_id"])
        .agg(
            pl.col("amount").sum().alias("revenue"),
            pl.len().alias("order_count"),
        )
        .sort(["order_date", "customer_id"])
    )
```

This processes every source row.

It is simple and useful as a correctness reference.

---

# 64. Partition-Based Gold Transformation

A partition transformation can be:

```python
def build_daily_partition(
    orders: pl.DataFrame,
    partition_date: date,
) -> pl.DataFrame:
    return (
        orders
        .filter(
            (pl.col("order_date") == partition_date)
            & (pl.col("status") == "paid")
        )
        .group_by(["order_date", "customer_id"])
        .agg(
            pl.col("amount").sum().alias("revenue"),
            pl.len().alias("order_count"),
        )
        .sort(["order_date", "customer_id"])
    )
```

Now the transformation has a clear contract:

```text
input:
orders for one logical date

output:
gold partition for that date
```

---

# 65. Detecting Affected Partitions

Suppose new silver rows were loaded since the previous watermark.

```python
def affected_dates(
    changed_silver: pl.DataFrame,
) -> list[date]:
    return (
        changed_silver
        .select("order_date")
        .unique()
        .sort("order_date")
        .to_series()
        .to_list()
    )
```

If changed rows contain:

```text
2025-03-01
2025-03-01
2025-03-07
```

the affected set is:

```text
2025-03-01
2025-03-07
```

not:

```text
today only
```

---

# 66. Incremental Processing Flow

```python
def run_incremental(
    silver: pl.DataFrame,
    changed_rows: pl.DataFrame,
) -> dict[date, pl.DataFrame]:
    dates = affected_dates(changed_rows)

    outputs = {}

    for partition_date in dates:
        outputs[partition_date] = build_daily_partition(
            silver,
            partition_date,
        )

    return outputs
```

The simplified design assumes `silver` represents the authoritative current source state.

A real pipeline would read only the relevant source scope rather than passing the entire dataset into every partition transformation.

---

# 67. Historical Correction

Suppose order 2 changes:

```text
amount = 50
```

to:

```text
amount = 80
```

and the order remains:

```text
order_date = 2025-03-01
```

The execution date may be:

```text
2025-03-05
```

But the affected partition is:

```text
2025-03-01
```

Therefore:

```text
changed silver row
       ↓
order_date = 2025-03-01
       ↓
recompute gold 2025-03-01
```

This is the essence of dependency-aware incremental processing.

---

# 68. Full-Rebuild Comparison

```python
full = full_rebuild(orders)

affected = orders.filter(
    pl.col("order_date").is_in(
        [date(2025, 3, 1)]
    )
)

incremental_partition = build_daily_partition(
    orders,
    date(2025, 3, 1),
)
```

A production test would compare:

```text
full partition for 2025-03-01
```

against:

```text
incremental partition for 2025-03-01
```

They should be semantically equal.

---

# 69. Backfill Range

A backfill can identify partitions:

```python
def backfill_dates(
    start: date,
    end: date,
) -> list[date]:
    result = []
    current = start

    while current < end:
        result.append(current)
        current += timedelta(days=1)

    return result
```

Example:

```python
dates = backfill_dates(
    date(2025, 3, 1),
    date(2025, 4, 1),
)
```

This produces:

```text
2025-03-01
...
2025-03-31
```

The half-open interval:

```text
[start, end)
```

makes range boundaries explicit.

---

# 70. Backfill Worker

```python
def process_backfill_partition(
    orders: pl.DataFrame,
    partition_date: date,
    logic_version: int,
) -> dict:
    result = build_daily_partition(
        orders,
        partition_date,
    )

    return {
        "partition": partition_date,
        "logic_version": logic_version,
        "row_count": result.height,
        "status": "complete",
    }
```

In a real pipeline, the worker would also:

```text
write shadow output
validate
commit metadata
```

The example focuses on the control flow.

---

# 71. Backfill With Bounded Workers

```python
from concurrent.futures import ThreadPoolExecutor, as_completed


def run_parallel_backfill(
    orders: pl.DataFrame,
    start: date,
    end: date,
    logic_version: int,
    max_workers: int = 4,
) -> list[dict]:
    partitions = backfill_dates(start, end)
    results = []

    with ThreadPoolExecutor(
        max_workers=max_workers
    ) as executor:
        futures = {
            executor.submit(
                process_backfill_partition,
                orders,
                partition,
                logic_version,
            ): partition
            for partition in partitions
        }

        for future in as_completed(futures):
            results.append(future.result())

    return results
```

The bounded worker count protects resources.

A production implementation must additionally handle:

- retries;
- failure recording;
- cancellation;
- locks;
- durable output;
- validation;
- progress state.

---

# 72. Simulated Worker Failure

A teaching example:

```python
def process_backfill_partition(
    orders: pl.DataFrame,
    partition_date: date,
    logic_version: int,
) -> dict:
    if partition_date == date(2025, 3, 17):
        raise RuntimeError(
            "Simulated worker failure"
        )

    result = build_daily_partition(
        orders,
        partition_date,
    )

    return {
        "partition": partition_date,
        "logic_version": logic_version,
        "row_count": result.height,
        "status": "complete",
    }
```

The correct operational response is not:

```text
rerun everything blindly
```

Instead:

```text
identify failed partition
        ↓
verify incomplete output
        ↓
retry partition
        ↓
validate
        ↓
mark complete
```

---

# 73. Logic Version Tracking

Add:

```python
LOGIC_VERSION = 2
```

and record:

```python
metadata = {
    "dataset": "orders_gold",
    "partition": partition_date,
    "logic_version": LOGIC_VERSION,
    "status": "complete",
}
```

Now historical state can answer:

```text
Which logic generated this partition?
```

A future change can identify partitions where:

```text
logic_version < 2
```

and create a targeted backfill.

---

# 74. Shadow Backfill

Conceptually:

```python
shadow_result = build_daily_partition(
    orders,
    date(2025, 3, 1),
)

production_result = existing_gold.filter(
    pl.col("order_date") == date(2025, 3, 1)
)
```

Then validate:

```text
row count
keys
revenue
order count
null rates
business invariants
```

Only after validation should the new partition replace the production partition.

For a multi-partition migration, a shadow table is often safer than replacing partitions one at a time.

---

# 75. Atomic Cutover Model

For a larger backfill:

```text
production_gold_v1
        │
        │ consumers
        ↓

shadow_gold_v2
        ↑
        │
historical backfill
```

After validation:

```text
consumer view
      ↓
points from v1
      ↓
atomic switch
      ↓
points from v2
```

This prevents consumers from observing a half-rebuilt dataset.

---

# 76. Testing: Full Rebuild Equals Incremental

Test 1:

```text
full rebuild
```

versus:

```text
incremental processing
```

Expected:

```text
semantic equality
```

The comparison should cover:

```text
row count
primary keys
values
aggregates
hashes
null rates
business invariants
```

---

# 77. Testing: Incremental Twice

Test 2:

```text
run incremental
run incremental again
```

Expected:

```text
same final target
```

This is the incremental equivalent of Topic 02's idempotency test.

A pipeline that produces different output when rerun with the same logical input is not production-safe.

---

# 78. Testing: Backfill Historical Range

Test 3:

```text
backfill 2025-03-01 → 2025-03-31
```

Then compare against:

```text
full rebuild for the same range
```

Expected:

```text
equivalent output
```

---

# 79. Testing: Failed Partition Retry

Test 4:

```text
partition A → success
partition B → simulated failure
partition C → success
```

Then:

```text
retry B
```

Expected:

```text
A complete
B complete
C complete
```

and:

```text
no duplicate or corrupt B output
```

---

# 80. Testing: Historical Change Propagation

Test 5:

1. Build historical gold.
2. Change an old silver record.
3. Detect its affected business date.
4. Recompute only the affected partition.
5. Compare that partition with a full rebuild.
6. Confirm unrelated partitions did not change.

This proves that the incremental dependency logic is scoped correctly.

---

# 81. Testing: Logic Version

Test 6:

```text
version 1 → historical partitions
version 2 → backfilled partitions
```

Verify metadata records the correct version.

Then query:

```text
all partitions with logic_version = 1
```

to identify remaining migration work.

---

# 82. Testing: Shadow Result

Test 7:

```text
production target
       vs
shadow target
```

Verify:

```text
keys
row counts
aggregates
hashes
null rates
business invariants
```

Only permit cutover when required validation succeeds.

---

# 83. Testing: Concurrent Backfill Protection

Test 8:

Start two attempts for:

```text
same dataset
same partition
```

Expected:

```text
one owner
one successful effect
```

or an explicit safe coordination mechanism.

The exact mechanism may be:

```text
database advisory lock
lease
orchestrator concurrency policy
```

---

# 84. Pipeline Success vs Data Correctness

These are different statements.

```text
Pipeline succeeded
```

means:

```text
the process completed without an unhandled execution error
```

It does **not** necessarily mean:

```text
the data is correct
```

A successful incremental pipeline can still:

- miss a historical update;
- recompute the wrong partition;
- use the wrong logic version;
- omit a dependency;
- produce an incorrect aggregate.

Therefore production pipelines require:

```text
execution success
+
data correctness validation
```

---

# 85. Debugging: Historical Changes Are Missed

## Symptoms

A historical order changed, but the gold table did not.

## Likely causes

- pipeline processes only execution date;
- `_loaded_at` not tracked;
- affected partition not derived;
- downstream dependency not propagated;
- change detection query has an incorrect watermark.

## Debugging steps

1. Find the changed silver row.
2. Inspect `order_date`.
3. Inspect `_loaded_at`.
4. Check the previous/current watermark.
5. Determine whether the row entered the change set.
6. Determine whether its `order_date` entered affected partitions.
7. Check whether the gold partition was recomputed.

## Prevention

Make affected-partition derivation explicit and test historical corrections.

---

# 86. Debugging: Wrong Partition Overwritten

## Symptoms

A backfill for:

```text
2025-03-01
```

changed:

```text
2025-03-02
```

## Likely causes

- execution date used instead of logical partition;
- timezone conversion;
- inclusive/exclusive range bug;
- partition path generated incorrectly.

## Debugging

Log:

```text
requested interval
logical partition
output path
```

Then verify the mapping.

## Prevention

Make partition identity an explicit function:

```python
def output_partition(run_date: date) -> str:
    return f"date={run_date.isoformat()}"
```

Test boundary dates.

---

# 87. Debugging: Incremental Differs From Full Rebuild

## Symptoms

```text
incremental != full rebuild
```

## Likely causes

- missed changed input;
- wrong affected partition set;
- aggregation state incomplete;
- inconsistent filtering;
- nondeterministic transformation;
- different null semantics;
- different version logic.

## Debugging strategy

Start with:

```text
key-level diff
```

then:

```text
partition-level diff
```

then:

```text
input diff
```

then:

```text
transformation logic
```

Do not immediately rewrite the whole pipeline.

---

# 88. Debugging: Backfill Consumes All Connections

## Symptoms

Normal production jobs begin timing out.

## Cause

Backfill concurrency is too high.

Example:

```text
100 workers
100 database connections
```

## Fix

Use:

```text
bounded workers
+
connection pool limits
+
resource isolation
```

A backfill should not consume all resources simply because it has a large historical range.

---

# 89. Debugging: Concurrent Partition Processing

## Symptoms

Two workers write:

```text
same partition
```

at the same time.

## Risks

- race condition;
- conflicting output;
- inconsistent metadata;
- unnecessary compute.

## Fix

Use an ownership mechanism:

```text
lock
lease
orchestrator concurrency
```

and ensure the output operation is idempotent.

---

# 90. Debugging: Failed Partition Marked Complete

## Symptoms

Metadata says:

```text
status = complete
```

but the output is missing or invalid.

## Cause

Completion state was committed before durable output.

## Correct sequence

```text
compute
 ↓
write
 ↓
validate
 ↓
commit completion metadata
```

Not:

```text
mark complete
 ↓
write
```

---

# 91. Debugging: Logic Changed but History Did Not

## Symptoms

New partitions use:

```text
logic_version = 2
```

old partitions remain:

```text
logic_version = 1
```

but no backfill was scheduled.

## Fix

Use logic-version metadata to identify:

```text
partitions where logic_version < 2
```

Then plan the historical rebuild.

---

# 92. Debugging: Backfill Is Slower Than Estimated

## Symptoms

Estimate:

```text
3 hours
```

Actual:

```text
9 hours
```

## Likely causes

- partition size skew;
- I/O bottleneck;
- database contention;
- too many workers;
- retries;
- startup overhead;
- validation overhead;
- poor target layout.

## Debugging

Measure:

```text
partition runtime distribution
CPU
memory
I/O
database latency
worker utilization
retry count
```

Then adjust based on evidence.

---

# 93. Production Design Patterns

## Pattern 1 — Partition recomputation

```text
changed input
 ↓
affected partition
 ↓
recompute
 ↓
overwrite
```

Good for deterministic partitioned facts and aggregates.

## Pattern 2 — Watermark + affected partitions

```text
_loaded_at watermark
        ↓
changed source rows
        ↓
distinct business dates
        ↓
recompute affected partitions
```

Useful when load time identifies changed records while business date determines target partition.

## Pattern 3 — Entity-driven recomputation

```text
changed customer IDs
        ↓
find affected facts
        ↓
recompute customer aggregates
```

Useful for customer-centric outputs.

## Pattern 4 — Shadow backfill

```text
production target
       +
shadow target
       ↓
compare
       ↓
cutover
```

Useful for high-risk historical changes.

## Pattern 5 — Version-driven migration

```text
logic_version < current
        ↓
backfill
        ↓
logic_version = current
```

Useful for controlled logic migrations.

---

# 94. Anti-Patterns

| Anti-pattern | Why it fails | Better approach |
|---|---|---|
| Always full rebuild | Wasteful at scale | Increment where justified |
| Increment only by execution date | Misses historical changes | Track affected data |
| Unlimited backfill concurrency | Resource exhaustion | Bounded concurrency |
| Backfill directly into production | Partial corruption risk | Shadow/isolated target |
| No logic version | Cannot explain historical output | Track transformation version |
| No reconciliation | Incorrect data can appear successful | Compare with reference/full rebuild |
| No retry-safe design | Failures can corrupt output | Idempotent partition processing |
| No concurrency control | Duplicate/conflicting work | Locks/leases |
| Incremental processing everywhere | Complexity without benefit | Use full refresh when appropriate |
| Treat `_loaded_at` as event time | Incorrect business partitioning | Separate load and business time |
| Process only new rows for aggregates | Misses changed historical groups | Recompute affected groups |
| Estimate from one fast partition | Underestimates runtime | Use representative benchmarks |
| Mark complete before durable output | False success | Commit completion after output validation |
| Mix old and new logic during cutover | Consumers see inconsistent history | Shadow + atomic cutover |

---

# 95. Hands-On Project

## Project: `orders_gold`

Build:

```text
bronze_orders
      ↓
silver_orders
      ↓
orders_gold
```

Target:

```text
gold_daily_revenue
```

Grain:

```text
one row per order_date + customer_id
```

Required capabilities:

```text
full rebuild
partition incremental
watermark-based change detection
affected-partition propagation
historical correction
backfill
bounded parallelism
failure/retry
logic version
shadow validation
safe cutover
```

---

# 96. Project Part A — Full Rebuild

Create a clean reference implementation.

Requirements:

```text
read all silver data
filter valid paid orders
group by order_date/customer_id
calculate revenue and order_count
write complete gold result
```

The full rebuild becomes the correctness oracle for later incremental processing.

---

# 97. Project Part B — Incremental Processing

Implement:

```text
changed silver rows
       ↓
affected order dates
       ↓
recompute only those gold partitions
```

Do not simply process:

```text
execution date
```

The affected partition must come from source data.

---

# 98. Project Part C — Customer Lifetime

Build:

```text
gold_customer_lifetime
```

where:

```text
customer_id
```

is the logical group.

If an historical order changes:

```text
customer_id = A
```

the affected customer must be identified and recomputed.

This demonstrates entity-driven incremental processing.

---

# 99. Project Part D — Backfill Command

Design:

```bash
backfill \
  --pipeline orders_gold \
  --start 2024-01-01 \
  --end 2025-01-01 \
  --parallelism 4
```

Required behavior:

```text
parse range
 ↓
generate partitions
 ↓
estimate work
 ↓
run bounded workers
 ↓
validate
 ↓
record status
```

---

# 100. Project Part E — Logic Version

Record:

```text
transform_version
```

for every output partition.

Example:

```text
orders_gold
2025-03-01
logic_version=2
```

Change the revenue logic.

Then query the metadata to determine which partitions require backfill.

---

# 101. Project Part F — Shadow Backfill

Build:

```text
orders_gold_current
orders_gold_shadow
```

Run the new logic into:

```text
orders_gold_shadow
```

Then compare:

```text
keys
row counts
revenue
order counts
hashes
null rates
business invariants
```

Do not cut over if required validation fails.

---

# 102. Project Part G — Simulated Failure

Inject a failure for a chosen partition:

```python
if partition_date == failure_date:
    raise RuntimeError("simulated failure")
```

Verify:

```text
failed partition
```

is not marked complete.

Retry it.

Verify:

```text
complete
```

and:

```text
no duplicate output
```

---

# 103. Project Part H — Equivalence Proof

Finally compare:

```text
incremental result
```

with:

```text
full rebuild
```

for:

```text
60 simulated days
```

containing:

- new records;
- historical corrections;
- repeated runs;
- failed partitions;
- logic changes.

The target should remain semantically equivalent for the same logic version.

---

# 104. Progressive Exercises — Beginner

## Exercise 1 — Convert Full Rebuild to Partition Processing

Take:

```text
process all dates
```

and change it to:

```text
process one requested date
```

### Solution guidance

Introduce:

```python
partition_date
```

as an explicit transformation input.

---

## Exercise 2 — Process One Changed Partition

Given:

```text
changed order_date = 2025-03-07
```

recompute only:

```text
2025-03-07
```

### Key insight

The changed date, not the execution date, determines the output.

---

## Exercise 3 — Add a Watermark

Given:

```text
previous_watermark = 10:00
new_watermark = 11:00
```

read:

```sql
_loaded_at > 10:00
AND _loaded_at <= 11:00
```

### Key insight

Boundary semantics must be explicit.

---

## Exercise 4 — Execution Date vs Affected Date

Explain why:

```text
execution = 2025-03-10
order_date = 2025-03-01
```

can require:

```text
recompute 2025-03-01
```

### Expected reasoning

`_loaded_at` identifies when the change entered the transformation system; `order_date` identifies the business partition affected.

---

# 105. Progressive Exercises — Intermediate

## Exercise 5 — Dependency-Aware Recompute

Given:

```text
silver_orders
 ↓
daily_revenue
 ↓
monthly_revenue
```

a March 10 daily partition changes.

Identify affected:

```text
daily partition
monthly partition
```

### Solution

```text
daily_revenue / 2025-03-10
monthly_revenue / 2025-03
```

---

## Exercise 6 — Incremental Aggregation

An order changes:

```text
100 → 150
```

Existing aggregate:

```text
1,000
```

Calculate the new aggregate.

### Solution

```text
1,000 - 100 + 150
= 1,050
```

This requires knowledge of the previous contribution.

---

## Exercise 7 — Additive vs Non-Additive

Classify:

```text
SUM
COUNT
AVG
COUNT DISTINCT
MEDIAN
```

### Solution

```text
SUM              → additive
COUNT            → additive
AVG              → derived from sum/count
COUNT DISTINCT   → non-trivially additive
MEDIAN           → non-additive
```

---

## Exercise 8 — Historical Backfill

Design a backfill for:

```text
2024-01-01
→
2024-12-31
```

after a revenue bug.

### Required answer

Include:

```text
range
logic version
resource limit
validation
shadow target
cutover
rollback
```

---

## Exercise 9 — Bounded Parallelism

Choose a strategy for:

```text
500 partitions
```

with:

```text
4 workers
```

### Expected reasoning

Process partitions through a bounded worker pool instead of creating 500 concurrent workers.

---

# 106. Progressive Exercises — Advanced

## Exercise 10 — Shadow Backfill

Design:

```text
production_gold
shadow_gold
```

and a validation process.

### Required checks

```text
row counts
keys
aggregates
hashes
null rates
business invariants
```

---

## Exercise 11 — Logic-Version Tracking

Design metadata:

```text
dataset
partition
logic_version
status
```

### Goal

Identify:

```text
all partitions with logic_version < current_version
```

---

## Exercise 12 — Failure and Retry

Simulate:

```text
partition A → success
partition B → failure
partition C → success
```

Retry B only.

### Required invariant

A, B, and C must each have exactly one valid completed output.

---

## Exercise 13 — Incremental vs Full Rebuild

Run:

```text
30-day full rebuild
```

and:

```text
30 daily incremental runs
```

Compare outputs.

### Required checks

```text
keys
values
aggregates
row counts
nulls
business invariants
```

---

## Exercise 14 — Atomic Cutover

Design a conceptual cutover from:

```text
gold_v1
```

to:

```text
gold_v2
```

without exposing a mixed-version dataset.

### Expected solution

Build and validate `gold_v2` independently, then switch consumers atomically using a supported table/view/version mechanism.

---

## Exercise 15 — Resource Isolation

Design a system where:

```text
production = high priority
backfill = bounded lower priority
```

### Expected solution

Use separate queues/worker pools and explicit concurrency/resource limits.

---

# 107. Expert Exercises

## Exercise 16 — Two-Year Backfill

Design a two-year backfill while production remains online.

Include:

```text
partitioning
parallelism
resource isolation
shadow target
validation
cutover
rollback
observability
```

---

## Exercise 17 — Mutable Customer Dataset

Design incremental processing for:

```text
customer profile changes
```

where historical customer aggregates depend on current customer classification.

Explain how customer changes propagate to affected downstream outputs.

---

## Exercise 18 — Dependency-Aware Backfill Framework

Design a framework that accepts:

```text
dataset
start
end
logic_version
```

and automatically determines:

```text
affected partitions
dependencies
execution order
resource limits
validation
```

---

## Exercise 19 — 5,000-Partition Failure

Thirty percent of a:

```text
5,000-partition
```

backfill fails.

Design recovery without rerunning successful partitions unnecessarily.

### Expected reasoning

Use durable partition state:

```text
complete
failed
pending
running
```

and retry only failed/incomplete work after validating output ownership.

---

## Exercise 20 — When Not to Use Incremental

Give three scenarios where full refresh is safer.

### Good answers

Examples:

- small target;
- extremely complex dependency graph;
- widespread historical corruption;
- major transformation rewrite;
- cheap compute where simplicity is more valuable than incremental complexity.

The important reasoning is:

> **Incremental processing is an optimization only when its correctness complexity is acceptable.**

---

# 108. Production Design Scenario

Consider:

```text
Raw Orders
    ↓
Bronze
    ↓
Silver
    ↓
Daily Orders
    ↓
Daily Revenue
    ↓
Monthly Revenue
```

Environment:

```text
2 years of data
500 GB
daily ingestion
occasional late records
mutable orders
business logic changes
monthly reporting
production must remain online
```

---

# 109. Scenario Design — Incremental Strategy

Use:

```text
silver _loaded_at
        ↓
identify changed orders
        ↓
derive affected order_date partitions
        ↓
recompute daily orders/revenue
        ↓
propagate to monthly revenue
```

Do not rely only on:

```text
today's date
```

---

# 110. Scenario Design — Aggregation Strategy

Daily revenue:

```text
recompute affected daily partitions
```

Monthly revenue:

```text
recompute affected months
```

because a corrected daily result changes the monthly aggregate.

If monthly revenue depends only on daily revenue, you do not necessarily need to rescan all raw orders for the month.

---

# 111. Scenario Design — Backfill Strategy

For a major logic change:

```text
build new logic version
        ↓
estimate two-year workload
        ↓
run representative pilot
        ↓
bounded parallel backfill
        ↓
shadow target
        ↓
validate
        ↓
atomic cutover
```

Production workloads remain isolated.

---

# 112. Scenario Design — Validation

Validate:

```text
row counts
primary keys
daily revenue
monthly revenue
null rates
business invariants
logic version
```

Compare representative ranges against:

```text
full rebuild
```

before trusting the incremental framework at scale.

---

# 113. Scenario Design — Recovery

Every partition should have a durable state:

```text
pending
running
complete
failed
```

A failed partition is retryable.

A successful partition is not recomputed unless:

```text
logic version changed
input changed
explicit rebuild requested
```

This avoids unnecessary work.

---

# 114. Senior Data Engineer Reasoning

An experienced engineer asks:

```text
What changed?
      ↓
Which data is affected?
      ↓
Which downstream outputs depend on it?
      ↓
What can be recomputed safely?
      ↓
Can the computation be idempotent?
      ↓
Can the result be validated?
      ↓
Can the operation be retried?
      ↓
Can production workload remain safe?
      ↓
Should this be incremental or full refresh?
```

The key insight is:

> **Incremental processing is fundamentally a dependency and correctness problem, not merely a performance optimization.**

---

# 115. Senior Decision Framework

Before implementing incremental processing, write:

```text
Source:
__________

Changed-data signal:
__________

Target grain:
__________

Affected output:
__________

Dependency:
__________

Recompute unit:
__________

Load strategy:
__________

Idempotency mechanism:
__________

Validation:
__________

Failure recovery:
__________

Logic version:
__________

Resource limit:
__________
```

If these answers are unclear, the incremental design is not yet mature.

---

# 116. Interview Questions — Basic

## 1. What is incremental processing?

**Expected answer:** Processing only the data or outputs that changed instead of rebuilding the complete historical target.

**Key concepts:** changed data, affected outputs, compute savings.

**Senior insight:** Incremental processing trades compute savings for state and dependency complexity.

---

## 2. What is a full rebuild?

**Expected answer:** Reading and transforming the complete logical input range to produce the complete target.

**Key concepts:** simplicity, correctness, cost.

**Senior insight:** Full rebuilds remain valuable as correctness references and escape hatches.

---

## 3. Why does incremental processing exist?

**Expected answer:** To avoid repeatedly processing unchanged historical data.

**Key concepts:** scale, I/O, runtime.

**Senior insight:** The optimization is worthwhile only when correctness can be preserved.

---

## 4. What is a partition?

**Expected answer:** A logical subset of data identified by a partition key such as date.

**Key concepts:** partition key, interval.

**Senior insight:** A good partitioning scheme can make incremental recomputation bounded.

---

## 5. What is a watermark?

**Expected answer:** A marker representing progress through an ordered source attribute.

**Key concepts:** lower bound, upper bound, cursor.

**Senior insight:** Watermark semantics must define boundaries and ordering precisely.

---

## 6. What is `_loaded_at`?

**Expected answer:** A timestamp representing when a record was loaded or persisted by an upstream system.

**Key concepts:** load time.

**Senior insight:** It is useful for detecting changed data but should not automatically be treated as event time.

---

## 7. What is a backfill?

**Expected answer:** Deliberate historical reprocessing over a specified range or affected set.

**Key concepts:** historical recomputation.

**Senior insight:** Backfills are normal production operations.

---

## 8. Why do backfills happen?

**Expected answer:** Bugs, logic changes, schema changes, source corrections, new sources, and historical enrichment.

**Key concepts:** logic version, history.

**Senior insight:** Historical data is part of the product and must be maintainable.

---

## 9. Why use bounded concurrency?

**Expected answer:** To prevent backfills from exhausting CPU, memory, connections, storage, or warehouse capacity.

**Key concepts:** resource control.

**Senior insight:** More workers can make a bottlenecked workload slower.

---

## 10. What is a shadow target?

**Expected answer:** A separate target where new logic is executed and validated before production cutover.

**Key concepts:** isolation, validation.

**Senior insight:** Shadow processing separates computation from production visibility.

---

# 117. Interview Questions — Moderate

## 11. Why is “process yesterday” not a complete incremental strategy?

**Expected answer:** Historical changes can arrive later and affect older business partitions.

**Key concepts:** affected date, load date.

**Senior insight:** Incremental logic should derive affected outputs from changed inputs.

---

## 12. What is the difference between event time and load time?

**Expected answer:** Event time describes when the business event occurred; load time describes when the pipeline received/persisted it.

**Key concepts:** temporal semantics.

**Senior insight:** Different timestamps serve different contracts.

---

## 13. How do you use `_loaded_at` for downstream processing?

**Expected answer:** Use it to identify recently changed upstream rows, then derive affected business partitions or entities.

**Key concepts:** watermark, change propagation.

**Senior insight:** `_loaded_at` is a change signal, not automatically the target partition key.

---

## 14. What is change propagation?

**Expected answer:** Determining which downstream outputs must be recomputed because upstream data changed.

**Key concepts:** dependencies, affected set.

**Senior insight:** It is the heart of dependency-aware incremental processing.

---

## 15. Why is average not directly additive?

**Expected answer:** An average alone does not retain enough information. Exact maintenance requires sufficient state such as sum and count.

**Key concepts:** derived aggregate.

**Senior insight:** Store the right intermediate state when incremental computation matters.

---

## 16. Why is count distinct difficult to increment?

**Expected answer:** New groups can overlap with previously seen entities.

**Key concepts:** set state, overlap.

**Senior insight:** Exact and approximate distinct counting have different state/cost trade-offs.

---

## 17. Why can a backfill affect production workload?

**Expected answer:** It can consume shared CPU, memory, storage bandwidth, database connections, or warehouse concurrency.

**Key concepts:** isolation.

**Senior insight:** Backfills must be treated as first-class production workloads.

---

## 18. Why use a shadow table?

**Expected answer:** To compute and validate new historical results without exposing partially rebuilt data to consumers.

**Key concepts:** blue-green, validation.

**Senior insight:** It separates correctness verification from production visibility.

---

## 19. Why track logic version per partition?

**Expected answer:** To identify which transformation semantics produced each output and determine what needs rebuilding after logic changes.

**Key concepts:** reproducibility, migration.

**Senior insight:** Data lineage includes transformation semantics, not just source lineage.

---

## 20. When is full refresh preferable?

**Expected answer:** When the dataset is small, compute is cheap, dependencies are complex, or incremental correctness is harder to guarantee.

**Key concepts:** simplicity vs optimization.

**Senior insight:** Incremental processing is not a goal by itself.

---

# 118. Interview Questions — Hard

## 21. Design incremental daily revenue.

**Expected answer:** Detect changed silver rows, derive affected order dates, recompute those daily partitions, validate, and replace them idempotently.

**Key concepts:** affected partitions, overwrite.

**Senior insight:** Do not confuse ingestion date with order date.

---

## 22. An order from last week changes today. What should happen?

**Expected answer:** The order's business date partition and all dependent aggregates must be identified and recomputed.

**Key concepts:** change propagation.

**Senior insight:** The execution date is irrelevant to the affected partition.

---

## 23. How would you backfill two years safely?

**Expected answer:** Define range and logic version, estimate workload, pilot, use bounded parallelism, isolate resources, build shadow output, validate, atomically cut over, and retain rollback.

**Key concepts:** production backfill.

**Senior insight:** A backfill is a historical deployment.

---

## 24. How would you prove incremental processing is correct?

**Expected answer:** Compare incremental output with a full rebuild under the same input and logic version, using keys, values, aggregates, hashes, and invariants.

**Key concepts:** equivalence.

**Senior insight:** Execution success is not correctness.

---

## 25. How do you recover from a failed partition?

**Expected answer:** Record partition state, identify incomplete output, retry only the failed partition, and validate before marking it complete.

**Key concepts:** retry, state.

**Senior insight:** Partition-level idempotency makes large backfills recoverable.

---

## 26. How do you prevent two workers from processing the same partition?

**Expected answer:** Use orchestration concurrency controls, leases, or database advisory locks.

**Key concepts:** ownership.

**Senior insight:** Correctness and resource efficiency both benefit from explicit ownership.

---

## 27. Why might a backfill be slower with more workers?

**Expected answer:** Shared resources become saturated and contention increases.

**Key concepts:** bottlenecks, bounded parallelism.

**Senior insight:** Benchmark the resource bottleneck instead of assuming linear scaling.

---

## 28. How do you migrate logic from v1 to v2?

**Expected answer:** Record logic versions, identify v1 partitions, compute v2 in shadow, reconcile, then cut over safely.

**Key concepts:** logic migration.

**Senior insight:** Version metadata turns an opaque historical migration into a measurable process.

---

## 29. How would you handle a new historical source?

**Expected answer:** Define how the source changes the target contract, backfill the affected range in isolation, validate against expected results, then cut over.

**Key concepts:** source expansion.

**Senior insight:** New-source backfills can affect more downstream data than the source's own partitions suggest.

---

## 30. How do you protect production from a large backfill?

**Expected answer:** Separate worker pools/queues, bound concurrency, limit connections, schedule appropriately, and monitor shared resource usage.

**Key concepts:** workload isolation.

**Senior insight:** A backfill is a competing workload unless explicitly isolated.

---

# 119. Interview Questions — Advanced

## 31. Design incremental processing for 5 TB/day.

**Expected answer:** Establish source change semantics, partition by appropriate business/logical boundaries, use watermarks to detect changed data, derive affected outputs, enforce idempotent partition writes, validate incrementals against full rebuilds, and monitor cost.

**Key concepts:** scale, correctness.

**Senior insight:** The architecture starts with change semantics, not worker count.

---

## 32. Design a two-year backfill while production remains online.

**Expected answer:** Use a versioned shadow target, bounded workers, resource isolation, partition state, validation, and atomic cutover.

**Key concepts:** blue-green, isolation.

**Senior insight:** Avoid exposing mixed-version output.

---

## 33. Design dependency-aware recomputation.

**Expected answer:** Represent dataset dependencies and map changed upstream entities/partitions to affected downstream partitions, then process dependencies in topological order.

**Key concepts:** DAG, propagation.

**Senior insight:** Incremental state should represent affected outputs, not only source changes.

---

## 34. Design a safe logic migration.

**Expected answer:** Assign a new logic version, identify stale partitions, compute shadow outputs, compare against expected/reference results, then cut over.

**Key concepts:** versioning.

**Senior insight:** Logic version is part of the target's operational metadata.

---

## 35. Recover after 30% of a backfill fails.

**Expected answer:** Query durable partition state, isolate failed/incomplete partitions, verify completed outputs, retry failures with bounded concurrency, and rerun reconciliation.

**Key concepts:** resumability.

**Senior insight:** Do not blindly restart all work if completed partitions are trusted and version-compatible.

---

## 36. Design incremental daily and monthly aggregates.

**Expected answer:** Recompute changed daily partitions and propagate affected months from changed daily outputs.

**Key concepts:** dependency propagation.

**Senior insight:** Downstream aggregate scope is determined by dependency, not source ingestion interval alone.

---

## 37. Design deterministic historical recomputation.

**Expected answer:** Pin input semantics and transformation logic version, use deterministic transformations, explicit intervals, stable ordering, idempotent outputs, and reproducible reference checks.

**Key concepts:** determinism.

**Senior insight:** Historical reproducibility is an architectural property.

---

## 38. Design shadow backfill and atomic cutover.

**Expected answer:** Compute the full target in a separate versioned target, validate comprehensively, switch consumers atomically, and preserve rollback.

**Key concepts:** blue-green.

**Senior insight:** The consumer should see a coherent version, not a moving rebuild.

---

## 39. Design resource isolation.

**Expected answer:** Give production and backfill workloads separate concurrency/resource controls and ensure backfills have bounded access to shared services.

**Key concepts:** workload management.

**Senior insight:** Resource isolation is part of data correctness because resource exhaustion can cause cascading failures.

---

## 40. Design a framework that chooses incremental vs full refresh.

**Expected answer:** Evaluate target size, change rate, affected-set determinability, dependency complexity, historical correctness risk, compute cost, and validation ability.

**Key concepts:** strategy selection.

**Senior insight:** The framework should optimize for correctness-adjusted cost, not minimum processed rows.

---

# 120. Architecture Questions

## 1. Design an incremental pipeline for 5 TB/day.

### Reference solution

```text
source
 ↓
watermark/change detection
 ↓
changed entities
 ↓
affected partitions
 ↓
deterministic transformations
 ↓
partition overwrite/merge
 ↓
validation
 ↓
metrics
```

Key decisions:

- use a reliable change signal;
- derive affected outputs;
- avoid full target scans;
- use bounded resources;
- reconcile with periodic full rebuilds.

---

## 2. Design a two-year backfill while production remains online.

### Reference solution

```text
production target v1
        +
shadow target v2
        ↑
bounded backfill workers
        ↑
historical source
```

Add:

```text
logic version
partition ledger
resource isolation
validation
atomic cutover
rollback
```

---

## 3. Design a dependency-aware recomputation framework.

### Reference solution

Represent:

```text
dataset
partition/entity
dependencies
```

Then:

```text
changed source
      ↓
affected direct outputs
      ↓
propagate through DAG
      ↓
topological execution
```

Each output must have a deterministic recomputation contract.

---

## 4. Design a safe logic migration.

### Reference solution

```text
logic v1
   ↓
identify v1 partitions
   ↓
logic v2 shadow backfill
   ↓
validate
   ↓
cutover
```

Record:

```text
logic_version
run_id
partition
status
```

---

## 5. Recover after 30% of a backfill fails.

### Reference solution

```text
partition ledger
       ↓
find failed/pending
       ↓
verify completed outputs
       ↓
retry failures
       ↓
validate
       ↓
complete migration
```

Do not discard trusted successful work without a correctness reason.

---

## 6. Design incremental daily and monthly aggregates.

### Reference solution

```text
changed orders
      ↓
affected days
      ↓
daily revenue
      ↓
affected months
      ↓
monthly revenue
```

Daily and monthly output scopes should be explicit.

---

## 7. Design deterministic historical recomputation.

### Reference solution

Pin:

```text
input interval
logic version
source semantics
configuration
timezone
ordering
```

Avoid hidden runtime-dependent values.

---

## 8. Design shadow backfill and atomic cutover.

### Reference solution

```text
current target
new shadow target
      ↓
reconcile
      ↓
atomic consumer switch
```

Retain old target for rollback where practical.

---

## 9. Design resource isolation between production and backfills.

### Reference solution

```text
production workers
backfill workers
```

with independent:

```text
concurrency
connection limits
priority
scheduling
resource classes
```

---

## 10. Design a framework that decides incremental vs full refresh.

### Reference solution

Evaluate:

```text
change volume
target size
dependency complexity
affected-set certainty
compute cost
validation cost
failure risk
```

Then choose the simpler strategy that meets correctness and performance requirements.

---

# 121. Production Checklist

## Incremental Correctness

```text
[ ] Affected data is explicitly identified.
[ ] Execution date is not confused with affected data date.
[ ] Partition boundaries are deterministic.
[ ] Watermark semantics are defined.
[ ] Lower/upper boundary behavior is defined.
[ ] Timezone semantics are defined.
[ ] Dependencies are understood.
[ ] Affected downstream outputs can be derived.
[ ] Incremental output can be reconciled with a full rebuild.
```

## Backfill Safety

```text
[ ] Backfill range is explicit.
[ ] Range boundary semantics are explicit.
[ ] Logic version is known.
[ ] Input assumptions are known.
[ ] Cost is estimated.
[ ] Runtime is estimated.
[ ] Concurrency is bounded.
[ ] Resources are isolated.
[ ] Shadow target exists where appropriate.
[ ] Validation is completed.
[ ] Cutover is safe.
[ ] Rollback exists.
```

## Reliability

```text
[ ] Partitions are retryable.
[ ] Processing is idempotent.
[ ] Transformations are deterministic.
[ ] Failures are observable.
[ ] Concurrent runs are controlled.
[ ] Partial completion is detectable.
[ ] Completion metadata is committed only after durable output.
```

## Operations

```text
[ ] Normal production workloads are protected.
[ ] Progress is observable.
[ ] Partition runtime is measured.
[ ] Resource utilization is measured.
[ ] Failed partitions can be isolated.
[ ] Stale logic versions can be identified.
[ ] Backfill status can be audited.
[ ] Representative benchmarks exist.
```

---

# 122. Final Mental Model

## Incremental Processing

```text
Incremental Processing
=
Process only what changed
+
Understand dependencies
+
Recompute affected outputs
+
Preserve correctness
```

This means:

```text
Do not ask only:
"What arrived today?"

Ask:
"What changed?"
        ↓
"Which outputs depend on it?"
        ↓
"What must be recomputed?"
```

## Safe Backfill

```text
Safe Backfill
=
Historical recomputation
+
Bounded resources
+
Deterministic logic
+
Idempotent execution
+
Validation
+
Safe cutover
+
Recovery
```

A mature Data Engineer does not optimize blindly for:

```text
minimum rows processed
```

The real objective is:

```text
minimum necessary computation
+
full correctness guarantees
```

The goal is not to process less data at any cost.

> **The goal is to process the minimum necessary data while preserving the same correctness guarantees as a full rebuild.**

---

# 123. Exit Criteria

You are ready to move to Topic 04 when you can independently:

```text
[ ] Explain full rebuild vs incremental processing.
[ ] Explain partition-based incremental processing.
[ ] Explain watermark-based processing.
[ ] Distinguish event time from load time.
[ ] Use upstream _loaded_at appropriately.
[ ] Identify affected partitions.
[ ] Distinguish execution date from affected data date.
[ ] Propagate changes through dependencies.
[ ] Design incremental aggregates.
[ ] Distinguish additive and non-additive aggregation problems.
[ ] Design targeted and full historical backfills.
[ ] Bound backfill concurrency.
[ ] Protect normal production workloads.
[ ] Design shadow/blue-green backfills.
[ ] Reason about atomic cutover.
[ ] Define rollback.
[ ] Track transformation logic versions.
[ ] Decide when full refresh is safer.
[ ] Estimate backfill runtime and cost.
[ ] Build retry-safe backfills.
[ ] Prove incremental/full-rebuild equivalence.
[ ] Debug missed historical changes.
[ ] Debug wrong partition selection.
[ ] Debug resource exhaustion.
[ ] Debug concurrent backfill execution.
[ ] Explain the architecture in a senior Data Engineer interview.
```

---

# 124. Final Principle

> **Incremental processing is not simply “processing yesterday.” It is the disciplined identification of changed inputs, propagation of those changes to exactly the outputs they affect, deterministic recomputation of those outputs, and validation that the result remains equivalent to a correct full rebuild. Backfills extend the same discipline to historical ranges and must be treated as controlled production operations with bounded resources, explicit logic versions, safe isolation, validation, cutover, and recovery.**
