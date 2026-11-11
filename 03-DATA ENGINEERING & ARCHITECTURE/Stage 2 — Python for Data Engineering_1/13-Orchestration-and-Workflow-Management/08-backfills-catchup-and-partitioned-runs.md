# Backfills, Catch-up, and Partitioned Runs

> **Apache Airflow 3.x — Production Data Engineering**

A production pipeline is not complete unless it can safely process the past.

This chapter teaches historical execution from first principles through production operations: **data intervals → catch-up → backfill → rerun/clearing → partitioned processing → idempotency → load control → late data → logic-change backfills → shadow processing → safe replacement → downstream invalidation → asset partitions → testing and observability**.

---

## 1. Learning Objectives

By the end of this chapter you should be able to:

- explain scheduled execution, catch-up, backfill, rerun, clearing, reprocessing, partitioned execution, logic-change processing, full rebuilds, shadow processing, and downstream invalidation;
- reason about data intervals and logical time rather than wall-clock time;
- configure and operate historical workloads safely in Airflow 3.x;
- distinguish scheduler-driven recovery from deliberate historical processing;
- design partition-aware, deterministic, idempotent pipelines;
- bound backfill concurrency and protect daily production;
- handle late-arriving data;
- perform controlled logic-change backfills;
- validate corrected historical output before replacing trusted data;
- reason about downstream invalidation and selective recomputation;
- understand asset partitions conceptually;
- test historical processing, failure recovery, load, and idempotency;
- design 30-day, 90-day, 180-day, and very large backfills.

### Core learning loop

For every concept:

**Concept → Why it exists → Mental model → Internal mechanics → Example → Failure scenario → Debugging → Production pattern → Trade-offs → Testing → Architecture**

---

## 2. Prerequisites

This chapter assumes familiarity with:

- DAGs and dependencies;
- schedules;
- Operators and TaskFlow;
- Connections, Variables, Hooks, and XCom;
- sensors and deferrable operators;
- retries and failure callbacks.

Those topics are referenced only where they affect historical execution.

The central assumption is that transformation logic can be made **interval-scoped**:

```text
run
 ↓
data interval
 ↓
read interval
 ↓
transform interval
 ↓
write partition
 ↓
validate partition
```

---

# 3. Why Historical Processing Matters

Normal processing handles today's expected interval. Production systems also need to recover or intentionally recompute the past.

Historical work is required because of:

- missed schedules;
- scheduler downtime;
- newly deployed pipelines;
- late-arriving data;
- corrected source data;
- bug fixes;
- transformation changes;
- schema changes;
- data-quality failures;
- downstream corrections;
- new historical reporting requirements.

A mature pipeline therefore needs two capabilities:

```text
NORMAL
today → today's interval → today's output

HISTORICAL
past interval → same interval-aware logic → corrected output
```

The goal is not merely to execute old code. The goal is to produce the **correct historical result without corrupting current production**.

---

# 4. Data Intervals and Logical Time

## 4.1 Data interval

A scheduled daily run represents a data period:

```text
2026-10-01 00:00
        ↓
2026-10-02 00:00
```

The interval is:

```text
[2026-10-01 00:00, 2026-10-02 00:00)
```

The end boundary is excluded.

This half-open convention prevents overlap:

```text
[Oct 1, Oct 2)
[Oct 2, Oct 3)
```

## 4.2 Important time concepts

| Concept | Meaning |
|---|---|
| Interval start | beginning of the data period |
| Interval end | exclusive end boundary |
| Logical date | logical representation associated with the scheduled run |
| Run | one orchestration execution |
| Task instance | one task execution in a run |
| Execution time | physical time computation actually occurs |
| Data time | time period the computation is responsible for |

A run can execute on Oct 2 at 08:00 while processing:

```text
Oct 1 → Oct 2
```

Therefore:

> **Execution time is not the same thing as data time.**

## 4.3 Why this matters for backfills

If code uses:

```python
datetime.now()
```

to decide which data to process, a historical run can accidentally process today's data.

Prefer interval context:

```text
interval_start
interval_end
```

and use those boundaries for source filtering and output partitioning.

Example:

```sql
SELECT *
FROM source.orders
WHERE event_time >= :interval_start
  AND event_time <  :interval_end;
```

---

# 5. Normal Scheduled Processing

A daily workflow can be visualized as:

```text
Day 1 → interval 1 → run
Day 2 → interval 2 → run
Day 3 → interval 3 → run
```

The pipeline should identify its interval from orchestration context.

A robust task behaves conceptually like:

```text
run interval
    ↓
[interval_start, interval_end)
    ↓
query source
    ↓
transform
    ↓
write partition
    ↓
validate
```

This connects directly to interval-scoped transformations in Module 2.12.

Do not rebuild transformation logic around the current clock simply because the task is being executed now.

---

# 6. What Is Catch-up?

**Catch-up** allows scheduled workflows to process eligible intervals that were missed since the configured starting point.

Example:

```text
Expected:
Mon → Tue → Wed → Thu

Scheduler unavailable:
Mon
Tue

Scheduler returns:
Wed

Catch-up:
Mon → Tue → Wed
```

Catch-up is primarily **schedule recovery**.

It exists so a scheduler outage or delayed activation does not automatically create permanent historical gaps.

Catch-up is not the same as deliberately correcting an already-successful interval.

---

# 7. Catch-up Configuration

Airflow DAG configuration includes the concept:

```python
catchup=False
```

versus:

```python
catchup=True
```

Neither is universally correct.

### `catchup=False`

Conceptually:

```text
DAG becomes active
      ↓
do not automatically create the whole historical schedule backlog
      ↓
focus on current/future scheduling
```

This may be appropriate when historical processing is intentionally controlled separately.

### `catchup=True`

Conceptually:

```text
configured start
      ↓
historical scheduled intervals
      ↓
eligible intervals
      ↓
scheduler-managed execution
```

This may be appropriate when every scheduled interval represents required processing.

### Production question

Do not ask:

> Should every DAG use `catchup=True`?

Ask:

> What should happen to historical scheduled intervals when this workflow starts or resumes?

---

# 8. Catch-up Failure Scenarios

Catch-up interacts with:

- retries;
- dependencies;
- concurrency;
- source availability;
- task failures.

## Scheduler downtime

Historical intervals may become eligible after the scheduler returns.

## DAG paused

A paused DAG may intentionally stop normal scheduling. When resumed, the resulting historical workload depends on the DAG's scheduling configuration.

## Late deployment

If a DAG has an old starting point and historical scheduling is enabled, activating it can produce a large workload.

## Failed task

Catch-up does not replace failure recovery. A failed interval may need a retry, rerun, or deliberate reprocessing.

## Missing upstream data

The interval may exist while source data does not. That is a **data-availability** problem rather than a missed schedule.

---

# 9. What Is a Backfill?

A **backfill** is deliberate processing of historical intervals over a selected time range.

Example:

```text
2026-01-01 → 2026-03-31

Jan 1
Jan 2
Jan 3
...
Mar 31
```

Typical reasons:

- new historical pipeline onboarding;
- corrected source data;
- logic bugs;
- historical reconstruction;
- known quality failures;
- new reporting requirements.

The defining property is deliberate historical scope.

---

# 10. Catch-up vs Backfill vs Rerun vs Rebuild

| Concept | Trigger | Scope | Purpose |
|---|---|---|---|
| Catch-up | scheduler | missed eligible intervals | recover schedule |
| Backfill | deliberate operator/control action | selected historical range | process past data |
| Rerun | recovery action | one or more intervals | correct/recover execution |
| Clear | execution-state action | selected task instances | make selected work eligible again |
| Reprocessing | deliberate recomputation | selected historical data | regenerate/correct results |
| Full rebuild | reconstruction | broad dataset/range | regenerate the dataset |

Example:

```text
Only Apr 12 failed
→ targeted rerun

Apr 1–Apr 30 source data corrected
→ selected backfill/reprocessing

Entire dataset untrusted
→ consider full rebuild
```

---

# 11. Airflow 3.x Scheduler-Managed Backfills

Airflow 3.x is the primary version for this chapter.

The current model emphasizes **scheduler-managed backfills**:

```text
operator selects historical scope
        ↓
backfill work is represented
        ↓
scheduler manages eligible execution
        ↓
tasks run with interval context
        ↓
operators monitor progress
```

Important operational concerns:

- historical interval selection;
- concurrency;
- interaction with normal scheduled runs;
- monitoring;
- operational control;
- reprocessing behavior.

### Legacy Airflow 2.x reference

Older Airflow 2.x material commonly teaches CLI-oriented backfill workflows.

That behavior may be useful for historical understanding, but it is **legacy/reference context here**, not the primary Airflow 3.x workflow.

Always verify version-sensitive commands and APIs against the exact Airflow 3.x release deployed by your organization.

---

# 12. Backfill Parameters

A safe backfill must define:

- selected DAG;
- start date/time;
- end date/time;
- exact interval boundaries;
- concurrency;
- reprocessing behavior;
- ordering;
- task selection where applicable.

Prefer:

```text
[2026-01-01 00:00, 2026-04-01 00:00)
```

over:

```text
"January through March"
```

A useful operational record is:

```text
DAG: orders_daily
Start: 2026-01-01T00:00:00Z
End: 2026-04-01T00:00:00Z
Expected intervals: 90
Historical concurrency: 4
Reprocessing policy: failed-only
Daily production protected: yes
Owner: data-platform
```

Precise boundaries make the operation auditable and repeatable.

---

# 13. Backfill Reprocessing Behavior

Suppose:

```text
90-day backfill

30 successful
5 failed
55 never processed
```

Conceptual policies include:

| Policy | Successful | Failed | Never processed |
|---|---:|---:|---:|
| Skip successful | skip | rerun | run |
| Failed-only recovery | skip | rerun | depends on original objective |
| Rerun all | rerun | rerun | run |

These are intent models. Exact Airflow 3.x semantics should be checked against the deployed release.

Use:

- successful-skip behavior when trusted output should remain;
- failed-only recovery when only failures require correction;
- all-interval reprocessing when historical output must be regenerated, such as a logic change.

---

# 14. Clearing and Reprocessing

Consider:

```text
extract → transform → quality → publish
```

If `transform` is incorrect for one interval:

```text
clear selected transform task instance
        ↓
rerun
        ↓
downstream consequences
```

Clearing is useful for selected task-instance recovery.

It becomes dangerous when applied indiscriminately.

Do not assume:

```text
clear everything
```

is equivalent to:

```text
safe historical correction
```

Broad clearing can trigger:

- source reads;
- duplicate writes;
- warehouse load;
- downstream recomputation;
- long historical workloads.

### Clear versus backfill

```text
Clear
→ execution-state recovery for selected task instances

Backfill
→ deliberate historical interval processing
```

---

# 15. Partitioned Runs

A **partitioned run** processes one well-defined slice of data.

Examples:

```text
date=2026-10-01
date=2026-10-02
date=2026-10-03
```

or:

```text
hour=10
hour=11
hour=12
```

Partitioning provides a unit of:

- processing;
- isolation;
- validation;
- rerunning;
- parallelism.

A 90-day operation becomes:

```text
90 daily partitions
```

rather than one opaque workload.

---

# 16. Partition Boundaries

Common granularities:

- daily;
- hourly;
- monthly;
- custom interval.

Daily:

```text
[2026-10-01 00:00, 2026-10-02 00:00)
```

Hourly:

```text
[2026-10-01 10:00, 2026-10-01 11:00)
```

Partition definitions must avoid:

- overlap;
- gaps;
- ambiguous timestamps;
- timezone inconsistency.

Use one canonical boundary convention throughout the pipeline.

---

# 17. Partitioned Run Context

Useful interval context includes:

```text
interval_start
interval_end
partition_id
run_id
```

Example:

```text
interval_start = 2026-10-01T00:00:00+00:00
interval_end   = 2026-10-02T00:00:00+00:00
partition_id   = 2026-10-01
```

Use the context to:

### Query

```sql
WHERE event_time >= :interval_start
  AND event_time < :interval_end
```

### Write

```text
orders/date=2026-10-01/
```

### Validate

```text
expected partition = 2026-10-01
```

### Log

```text
processing_partition=2026-10-01
```

---

# 18. Deterministic Historical Processing

The same interval should produce the same logical output when inputs and code are unchanged.

```text
interval
  ↓
deterministic transformation
  ↓
partition output
```

Avoid making business scope depend on:

- current clock;
- random values;
- unstable ordering;
- mutable external state.

Determinism improves:

- reruns;
- backfills;
- debugging;
- reproducibility;
- audits.

---

# 19. Idempotency During Backfills

Historical work is often repeated.

Dangerous:

```text
INSERT
INSERT
INSERT
```

A repeated run can create:

- duplicates;
- double counting;
- duplicate files;
- inconsistent warehouse state.

Safer patterns include:

- partition overwrite;
- `MERGE`/upsert;
- unique constraints where appropriate;
- deterministic object paths;
- atomic/controlled replacement;
- write → audit → publish.

Example:

```text
orders/date=2026-10-01/
```

is a stable logical destination.

A rerun should replace or reconcile the same logical partition rather than create another copy.

### Idempotency test

Run:

```text
interval A
interval A again
```

Then verify:

```text
same row count
same keys
same business metrics
no duplicate state
```

---

# 20. Backfill Load Control

Historical workloads can overwhelm:

- source databases;
- workers;
- object storage;
- warehouses;
- APIs;
- downstream systems.

Controls include:

- maximum active runs;
- pools;
- concurrency;
- task-level parallelism;
- ordering;
- batching;
- resource limits.

The production objective is:

> **Complete historical work safely while protecting current production.**

---

# 21. Concurrent Backfills and Daily Runs

Example:

```text
Daily:
2026-10-01

Backfill:
2026-04-01 → 2026-09-30
```

If historical work consumes all resources:

```text
backfill
  ↓
workers saturated
  ↓
daily pipeline delayed
```

A safer model is:

```text
Historical workload
       ↓
bounded historical capacity
       ↓
resource controls
       ↑
       │
Daily production
       ↓
protected capacity
```

Possible mechanisms:

- pools;
- priority;
- bounded concurrency;
- separate execution capacity where justified;
- staged batches.

Do not assume separate infrastructure is always necessary; choose controls based on workload and deployment architecture.

---

# 22. 90-Day Backfill Lab

## Scenario

`orders_daily` must process **90 days** while daily processing continues.

Requirements:

- maximum 4 concurrent historical runs;
- daily runs continue;
- source systems are protected;
- successful/failed intervals are tracked;
- only failures are rerun;
- processing is idempotent.

## Design

```text
90 historical intervals
        ↓
bounded concurrency = 4
        ↓
partition processing
        ↓
validation
        ↓
success / failure ledger
```

If one interval fails:

```text
identify failed partition
        ↓
diagnose
        ↓
fix
        ↓
rerun selected interval
        ↓
validate
```

Do not rerun all 90 intervals automatically.

---

# 23. Backfill Ordering

Possible strategies:

### Oldest-first

```text
Jan → Feb → Mar → Apr
```

Useful when historical dependencies build sequentially.

### Newest-first

```text
Apr → Mar → Feb → Jan
```

Useful when recent business data has higher operational value.

### Dependency-aware

Order work according to upstream/downstream constraints.

### Resource-aware

Consider partition size, source load, and destination capacity.

### Mixed strategy

Protect daily production while processing history in controlled batches.

There is no universally correct ordering.

---

# 24. Huge Backfills

A workload may grow from:

```text
90 days
→ 1 year
→ 5 years
→ billions of rows
```

The engineering problem then includes:

- runtime;
- cost;
- source load;
- warehouse load;
- parallelism;
- partitioning;
- batching;
- monitoring;
- restartability.

### Why "increase concurrency" is dangerous

More concurrency may improve throughput but also increase:

```text
source load
warehouse load
contention
network pressure
failures
cost
```

Use:

```text
pilot
 ↓
measure
 ↓
bounded concurrency
 ↓
batch
 ↓
monitor
 ↓
validate
```

Never claim an exact throughput or completion time without measurement from the target environment.

---

# 25. Backfill Observability

Operators need visibility into:

- intervals completed;
- intervals failed;
- active runs;
- backlog;
- processing rate;
- average interval duration;
- task duration;
- source load;
- destination load;
- output validation;
- downstream impact;
- estimated completion.

Example:

```text
Backfill: orders_daily
Range: 90 days

Completed: 61
Failed:     2
Running:    4
Remaining: 23

Validation failures: 1
Daily production: healthy
```

A backfill that cannot be observed cannot be safely controlled.

---

# 26. Logic-Change Backfills

Suppose:

```text
old:
revenue = quantity * old_price

new:
revenue = quantity * corrected_price
```

and the bug affected:

```text
last 180 days
```

This is different from recovering a failed task.

You are intentionally changing historical results.

You must reason about:

- logic version;
- affected intervals;
- downstream datasets;
- dependencies;
- validation;
- replacement;
- rollback.

Do not blindly overwrite trusted production data.

---

# 27. Shadow Tables

A safer pattern is:

```text
Existing gold
    │
    ├── remains available
    │
New corrected processing
    ↓
shadow_gold
    ↓
compare
    ↓
validate
    ↓
controlled replacement
```

Benefits:

- isolation;
- validation;
- rollback opportunity;
- smaller blast radius.

Limitations:

- additional storage;
- additional compute;
- comparison effort;
- replacement coordination.

Shadow processing is especially valuable when the correction can materially change historical business results.

---

# 28. Safe Replacement / Table Swap Concept

A database-specific atomic swap cannot be assumed to work identically everywhere.

The general production pattern is:

```text
shadow/staging output
       ↓
validation
       ↓
controlled or atomic replacement
       ↓
downstream visibility
       ↓
rollback capability
```

Before replacement, answer:

```text
What is trusted today?
What will become trusted?
What validation proves the new output?
How is rollback performed?
Which downstream datasets must be recomputed?
```

---

# 29. Downstream Invalidation

Example:

```text
orders_silver
     ↓
revenue_gold
     ↓
dashboard
```

If `orders_silver` changes historically:

```text
orders_silver corrected
     ↓
revenue_gold may be stale
     ↓
dashboard may be stale
```

The process is:

```text
upstream correction
       ↓
dependency analysis
       ↓
affected intervals
       ↓
selective downstream recomputation
       ↓
validation
```

A historical correction is therefore a **dependency-graph problem**, not merely a write operation.

---

# 30. Logic-Change Backfill Lab

Scenario:

```text
Revenue logic changed.
Affected range = 180 days.
```

Required workflow:

```text
identify affected partitions
        ↓
new logic
        ↓
shadow output
        ↓
old/new comparison
        ↓
quality validation
        ↓
controlled replacement
        ↓
downstream invalidation
        ↓
downstream recomputation
        ↓
audit
```

Compare:

- row counts;
- keys;
- aggregates;
- business metrics;
- nulls;
- duplicates;
- partition completeness.

Expected differences are not automatically failures. Validate that they are consistent with the intended logic correction.

---

# 31. Late-Arriving Data

Example:

```text
Oct 1 partition
      ↓
source data missing
      ↓
Oct 2 source data arrives
      ↓
Oct 1 is incomplete
      ↓
reprocess Oct 1
```

Late data is different from catch-up:

```text
Catch-up:
the scheduled interval was missed

Late data:
the interval existed, but required source data arrived later

Backfill:
an operator deliberately processes historical intervals
```

Late-data correction should be:

- interval-specific;
- idempotent;
- validated;
- assessed for downstream impact.

---

# 32. Asset Partitions

A partitioned data asset can be represented conceptually as:

```text
orders_daily
├── 2026-10-01
├── 2026-10-02
├── 2026-10-03
└── ...
```

Important concepts:

- partitioned assets;
- daily partition keys;
- historical materialization;
- partition backfills;
- asset-level visibility.

The key relationship is:

```text
partitioned asset
      ↓
selected historical partitions
      ↓
materialization / backfill
```

This chapter focuses on the partition concept and orchestration relationship rather than turning this into the Dagster topic.

---

# 33. Testing Backfills

## Unit testing

Test interval calculations and partition paths.

```python
def partition_path(interval_start):
    return f"orders/date={interval_start:%Y-%m-%d}/"
```

## Integration testing

Process one historical interval end-to-end.

## Multi-interval testing

Run several adjacent partitions and verify:

- no overlap;
- no gaps;
- correct boundaries.

## Idempotency testing

Run the same interval twice.

Expected:

```text
same logical result
no duplicate state
```

## Failure testing

Fail one historical interval and verify that it can be isolated and rerun.

## Backfill load testing

Simulate multiple concurrent intervals and observe resource behavior.

## Logic-change testing

Compare old/new outputs and validate expected differences.

---

# 34. Backfill Validation

A successful task is not proof of correct historical data.

Validate:

- row counts;
- partitions;
- date ranges;
- duplicates;
- nulls;
- business metrics;
- reconciliation;
- downstream consistency.

Conceptual flow:

```text
Backfill
   ↓
validation
   ↓
publish
```

Use Module 2.11 controls such as reconciliation and quality gates without re-teaching the entire data-quality module.

---

# 35. Failure Injection Lab

Inject:

1. one interval fails;
2. source unavailable;
3. duplicate output;
4. partial write;
5. malformed historical data;
6. logic error;
7. resource exhaustion;
8. daily run competes with backfill;
9. backfill task times out;
10. corrected output differs unexpectedly from production.

For each scenario document:

```text
Expected failure
      ↓
Detection
      ↓
Recovery
      ↓
Rerun strategy
      ↓
Validation
```

Example: source unavailable.

```text
source outage
   ↓
historical interval fails
   ↓
detect dependency failure
   ↓
do not corrupt output
   ↓
restore source
   ↓
rerun interval
   ↓
validate
```

---

# 36. Production Backfill Decision Tree

```text
Need historical processing?
        |
       Yes
        ↓
Why?
 ┌──────────────┬──────────────┬──────────────┐
 │              │              │              │
Missed run    Late data    Logic change    New history
 │              │              │              │
Catch-up      Rerun       Shadow/backfill   Backfill
                               │
                               ↓
                         validate/replace
```

Then ask:

```text
Is output idempotent?
How many intervals?
Can daily production be protected?
Does downstream data need recomputation?
Does logic change?
Which partitions are affected?
What validation is required?
How can the operation be stopped safely?
```

---

# 37. Production Backfill Patterns

## Pattern 1 — Failed interval recovery

```text
daily run
 ↓
failure
 ↓
fix
 ↓
rerun interval
 ↓
validate
```

## Pattern 2 — Historical source correction

```text
source corrected
 ↓
selected partitions
 ↓
backfill
 ↓
validate
```

## Pattern 3 — Logic correction

```text
new code
 ↓
shadow historical output
 ↓
validate
 ↓
controlled replacement
 ↓
recompute downstream
```

## Pattern 4 — Large historical migration

```text
years of data
 ↓
batch by partitions
 ↓
controlled concurrency
 ↓
monitor
 ↓
validate
```

---

# 38. Trade-offs

| Decision | Benefit | Cost/Risk |
|---|---|---|
| Catch-up | automatic schedule recovery | unexpected backlog |
| Deliberate backfill | explicit control | operational complexity |
| High concurrency | potentially faster | higher resource pressure |
| Low concurrency | safer load | longer completion |
| Full rebuild | simple conceptual reconstruction | expensive/disruptive |
| Selective reprocessing | smaller blast radius | dependency analysis |
| Shadow processing | safer validation | extra compute/storage |

---

# 39. End-to-End `orders_daily` Backfill Lab

Architecture:

```text
Source
 ↓
Bronze
 ↓
Silver
 ↓
Gold
 ↓
Quality
 ↓
Publish
```

Scenario:

> The pipeline missed 90 days.

Requirements:

- historical intervals processed;
- maximum 4 concurrent backfill runs;
- daily processing continues;
- failed intervals rerun selectively;
- every partition validated;
- idempotency preserved;
- progress observable.

### Expected design

```text
90 intervals
    ↓
bounded historical concurrency
    ↓
interval-scoped processing
    ↓
partition validation
    ↓
success/failure tracking
    ↓
targeted recovery
```

---

# 40. 180-Day Backfill Lab

Scenario:

```text
180-day historical range
+
normal daily processing
```

Requirements:

- bounded concurrency;
- partition-aware processing;
- monitoring;
- validation;
- failure recovery;
- no unnecessary full rebuild.

To prevent the backfill from delaying a critical daily 07:00 workload:

```text
historical workload
      ↓
limited capacity
      ↓
production protected
```

Monitor:

- daily task duration;
- source load;
- warehouse load;
- active historical runs;
- backlog.

If production degrades, throttle or pause historical work.

---

# 41. Code Review Exercises

## Bad example 1 — Unlimited concurrency

**Problem:** 365 days are launched with unlimited concurrency.

**Impact:** source and warehouse overload, worker contention, production starvation.

**Correction:** bounded concurrency and monitored batches.

## Bad example 2 — Current wall-clock time

```python
partition = datetime.now().date()
```

**Problem:** historical execution can process the wrong partition.

**Correction:** use interval context.

## Bad example 3 — Repeated append

```sql
INSERT INTO revenue_daily
SELECT ...
```

with no duplicate protection.

**Problem:** reruns can double count.

**Correction:** partition replacement, merge/upsert, unique constraints, or equivalent idempotent design.

## Bad example 4 — Rebuild everything

**Problem:** one changed partition causes unnecessary downstream work.

**Correction:** identify affected partitions and dependencies.

## Bad example 5 — Direct production overwrite

**Problem:** unvalidated logic-change output becomes trusted immediately.

**Correction:** shadow → compare → validate → replace.

## Bad example 6 — Historical work starves daily production

**Problem:** full capacity is consumed by backfill.

**Correction:** resource isolation/bounding and production protection.

## Bad example 7 — Task success means data correctness

**Problem:** successful execution can still produce wrong output.

**Correction:** interval-level validation.

## Bad example 8 — Ignore downstream invalidation

**Problem:** corrected upstream data leaves dependent outputs stale.

**Correction:** dependency analysis and selective recomputation.

---

# 42. Debugging Historical Runs

Use this workflow:

```text
Identify interval
      ↓
Inspect run state
      ↓
Inspect task state
      ↓
Check interval inputs
      ↓
Check source availability
      ↓
Check output partition
      ↓
Check duplicates/partial writes
      ↓
Check downstream impact
      ↓
Rerun safely
      ↓
Validate
```

The exact interval comes first because historical failures can differ by:

- source availability;
- data volume;
- schema;
- late data;
- business conditions.

---

# 43. Backfill Cost and Resource Management

Never invent exact costs or guaranteed durations.

Reason about:

- compute;
- storage;
- source-system load;
- warehouse load;
- network bandwidth;
- concurrency;
- opportunity cost to normal production.

Before a large operation:

```text
estimate
 ↓
pilot
 ↓
measure
 ↓
set controls
 ↓
scale gradually
```

A historical operation is production work and should be planned accordingly.

---

# 44. Backfill Safety Checklist

Before starting:

- [ ] exact interval range defined;
- [ ] source availability confirmed;
- [ ] partition boundaries confirmed;
- [ ] idempotency verified;
- [ ] workload estimated;
- [ ] concurrency configured;
- [ ] critical daily runs protected;
- [ ] validation defined;
- [ ] rollback/recovery defined;
- [ ] monitoring defined;
- [ ] stop conditions defined;
- [ ] owner defined;
- [ ] reason documented.

---

# 45. Production Observability Checklist

Monitor:

- active intervals;
- completed intervals;
- failed intervals;
- backlog;
- processing rate;
- concurrency;
- source load;
- destination load;
- task duration;
- retry count;
- validation failures;
- downstream impact;
- estimated completion.

A backfill should be operationally visible from start to completion.

---

# 46. Architecture Exercises

### 1. How would you backfill 30 days safely?

Expected reasoning:

1. define exact intervals;
2. verify interval-aware processing;
3. verify idempotency;
4. bound concurrency;
5. protect daily production;
6. validate partitions;
7. monitor;
8. rerun only failures.

### 2. How would you backfill 180 days while daily production continues?

Protect production capacity, batch history, bound concurrency, monitor source/destination load, and keep interval-level recovery possible.

### 3. How would you rerun only failed intervals?

Identify the failed interval set, diagnose, fix, rerun only that set, and validate.

### 4. How would you process late-arriving data?

Identify the affected interval, verify the late source data, reprocess idempotently, validate, and assess downstream effects.

### 5. How would you handle a six-month logic bug?

Identify affected partitions, version the corrected logic, shadow-process history, compare, validate, replace safely, and recompute downstream.

### 6. How would you protect a critical 07:00 workload?

Reserve/protect production capacity, bound historical concurrency, use pools/priorities where appropriate, and monitor daily execution health.

### 7. How would you choose selective reprocessing versus full rebuild?

Consider affected scope, trust in unaffected outputs, dependency certainty, cost, risk, and operational feasibility.

### 8. How would you handle downstream invalidation?

Trace dependencies from corrected upstream partitions, identify affected downstream partitions, selectively recompute, and validate.

### 9. How would you design shadow processing?

Keep trusted production live, generate corrected output separately, compare, validate, then perform controlled replacement.

### 10. How would you backfill billions of rows?

Partition and batch the workload, pilot, bound concurrency, protect production, monitor, validate, and make progress independently restartable.

---

# 47. Interview Questions

## 47.1 Basic — 10

### 1. What is a data interval?

**Answer:** The defined period of source data that a run is responsible for processing, such as `[Oct 1, Oct 2)` for a daily interval.

### 2. What is catch-up?

**Answer:** Processing of eligible scheduled intervals that were missed, according to the workflow's scheduling configuration.

### 3. What is a backfill?

**Answer:** Deliberate processing of historical intervals over a selected range.

### 4. Catch-up versus backfill?

**Answer:** Catch-up primarily recovers missed scheduling; backfill is deliberate historical processing.

### 5. Why are partitions useful?

**Answer:** They create independently addressable units for processing, validation, parallelism, and reruns.

### 6. Why use interval context?

**Answer:** To ensure the task processes the assigned historical data period rather than current wall-clock data.

### 7. What is idempotency?

**Answer:** Repeating the same interval does not create incorrect additional state such as duplicates or double counting.

### 8. Why is unlimited concurrency dangerous?

**Answer:** It can overload sources, warehouses, workers, and downstream systems and starve normal production.

### 9. What is a shadow table?

**Answer:** An isolated destination used to build and validate corrected output before replacing trusted production data.

### 10. What is downstream invalidation?

**Answer:** The need to reconsider or recompute dependent datasets after an upstream historical correction.

## 47.2 Moderate — 10

### 11. Why are half-open intervals useful?

**Answer:** Adjacent intervals meet at one boundary without overlapping or leaving a gap.

### 12. What is the risk of catch-up with an old start date?

**Answer:** A large historical backlog can become eligible and create unexpected resource demand.

### 13. What is clearing?

**Answer:** Clearing changes selected task-instance state so the work can become eligible for execution again.

### 14. When should failed intervals be rerun instead of all intervals?

**Answer:** When successful outputs remain trusted and only failures need correction.

### 15. Why is wall-clock time dangerous?

**Answer:** A historical run can accidentally read or write today's data instead of its assigned interval.

### 16. How do you protect daily production?

**Answer:** Bound historical concurrency and use pools, priorities, batching, or separate capacity as appropriate.

### 17. Why is task success insufficient?

**Answer:** Execution success does not prove data correctness; output still needs validation.

### 18. What should be compared during a logic-change backfill?

**Answer:** Rows, keys, aggregates, business metrics, partition completeness, and expected differences.

### 19. Why use shadow output?

**Answer:** It isolates corrected computation and allows validation before production replacement.

### 20. Why does late data cause historical reruns?

**Answer:** The original interval may have been processed before all required source data arrived.

## 47.3 Hard — 10

### 21. Design a 90-day backfill while daily processing continues.

**Answer:** Use interval-scoped partitions, bounded historical concurrency, protected production capacity, per-partition validation, an explicit success/failure ledger, and idempotent writes.

### 22. What if orchestration is retry-safe but storage is not?

**Answer:** Repeated task execution can still duplicate or corrupt storage. Idempotency must cover the complete write path.

### 23. How would you correct 14 historical source partitions?

**Answer:** Isolate affected partitions, verify source completeness, reprocess with safe writes, validate, and assess downstream dependencies.

### 24. Why is logic-change processing different from failure recovery?

**Answer:** Failure recovery attempts to achieve the originally intended result; logic-change processing intentionally changes historical results and therefore requires stronger comparison, validation, replacement, and downstream planning.

### 25. Why avoid direct production overwrite during a six-month correction?

**Answer:** An incorrect result can immediately replace trusted data and make containment and rollback harder.

### 26. Oldest-first or newest-first?

**Answer:** Choose based on dependencies, business value, freshness, resource constraints, and operational risk. Neither is universally correct.

### 27. What if backfill degrades the daily pipeline?

**Answer:** Treat degradation as a throttle/stop signal, reduce historical concurrency, protect production capacity, and resume only after resource conditions are safe.

### 28. Why is downstream invalidation a graph problem?

**Answer:** An upstream change can affect multiple dependent datasets and partitions, requiring dependency tracing to determine recomputation scope.

### 29. How do you test idempotency?

**Answer:** Run the same interval twice and verify equivalent logical output, no duplicate keys, and stable business metrics.

### 30. How do you design a restartable billion-row backfill?

**Answer:** Partition and batch it, track progress, use idempotent writes, bound concurrency, validate completed batches, and restart failed batches independently.

## 47.4 Advanced — 10

### 31. Design a six-month revenue correction while gold remains available.

**Answer:** Keep trusted gold live, build a shadow correction, compare and validate, identify downstream dependencies, perform controlled replacement, recompute affected downstream partitions, and preserve rollback/audit evidence.

### 32. How do you prevent a backfill from overwhelming a source database?

**Answer:** Estimate demand, bound concurrency, batch work, use resource controls, monitor source load, throttle when necessary, and protect critical source operations.

### 33. How do you distinguish scheduling gaps from data-availability gaps?

**Answer:** A scheduling gap means the interval execution was missed; a data-availability gap means the interval existed but source data arrived later.

### 34. How do you make a logic-change backfill auditable?

**Answer:** Record affected intervals, old/new logic versions, code identity, validation results, replacement details, downstream recomputation, owner, and rollback information.

### 35. When is full rebuild safer?

**Answer:** When affected scope cannot be isolated reliably, dependencies are uncertain, existing outputs cannot be trusted, or reconstruction is simpler and safer.

### 36. How do variable partition sizes affect concurrency?

**Answer:** One partition may consume much more resources than another, so concurrency should consider actual workload size rather than merely counting partitions.

### 37. How does determinism help rollback?

**Answer:** Deterministic processing makes historical output reproducible and easier to compare, verify, and restore.

### 38. How do you handle late data crossing a logic-version boundary?

**Answer:** Track both affected interval and logic version, process with the intended corrected version, validate, and recompute downstream dependencies.

### 39. How do you prove a backfill did not starve production?

**Answer:** Monitor production duration, queueing, resource utilization, source/destination load, and freshness expectations throughout the operation.

### 40. Design an operating model for repeated historical corrections.

**Answer:** Standardize interval selection, partitioning, idempotent writes, bounded concurrency, validation, dependency analysis, shadow processing for logic changes, controlled replacement, observability, auditability, and rollback.

---

# 48. Practical Exercises

## Beginner

1. Explain data intervals.
2. Create a daily partition.
3. Explain catch-up using a scheduler outage.
4. Configure and reason about catch-up.
5. Identify historical intervals.

## Intermediate

1. Design a 7-day backfill.
2. Rerun failed intervals.
3. Test idempotency.
4. Use partition-specific paths.
5. Protect daily processing.

## Advanced

1. Design a 90-day backfill.
2. Control concurrency.
3. Handle late data.
4. Perform selective reprocessing.
5. Reason about downstream invalidation.

## Expert / Production

1. Design a 180-day logic-change backfill.
2. Use shadow outputs.
3. Compare old/new results.
4. Validate.
5. Safely replace production output.
6. Recompute affected downstream partitions.
7. Maintain daily freshness expectations.

---

# 49. Final Practical Challenge

A company has:

```text
5 source systems
      ↓
Bronze
      ↓
Silver
      ↓
Quality
      ↓
Gold Revenue
      ↓
Analytics
```

Problems:

1. The pipeline missed 14 days because of an outage.
2. One source delivered data late for 7 days.
3. A transformation bug affected the last 180 days.
4. Normal daily processing must continue.
5. Gold revenue must remain available during correction.

Design:

- catch-up strategy;
- backfill strategy;
- partition strategy;
- concurrency limits;
- idempotency;
- late-data correction;
- logic-change backfill;
- shadow output;
- validation;
- replacement;
- downstream invalidation;
- observability;
- rollback.

### Expected architecture

```text
                         ┌──────────────────┐
                         │ Daily production │
                         │ protected        │
                         └────────┬─────────┘
                                  │
Sources → Bronze → Silver → Gold → Analytics
                 ↑       ↑
                 │       │
          historical   corrected
          partitions   shadow path
                 │       │
                 └──→ validation
                         ↓
                  controlled replace
                         ↓
                  downstream rebuild
```

### Expected reasoning

**Phase 1:** recover the missed intervals using the appropriate catch-up/backfill mechanism.

**Phase 2:** isolate the seven late-data partitions and reprocess them idempotently.

**Phase 3:** process the 180-day logic correction in shadow storage.

**Phase 4:** compare and validate old/new results.

**Phase 5:** replace corrected output safely.

**Phase 6:** invalidate/recompute affected downstream partitions.

**Phase 7:** maintain observability and rollback capability throughout.

---

# 50. Relationship to Other Module 2.13 Topics

## Topic 01

DAGs, dependencies, and scheduling provide the foundation for identifying historical scheduled intervals.

## Topic 04

TaskFlow and DAG execution provide the implementation mechanism for interval-aware tasks.

## Topic 06

Sensors and deferrable operators may be involved when historical source data is not yet available.

## Topic 07

Retries, timeouts, deadlines, and failure callbacks operate inside historical task execution. They do not replace the historical-scope decision.

This chapter intentionally does not duplicate those topics.

---

# 51. Relationship to Module 2.11

Historical processing should use validation controls such as:

```text
Backfill
 ↓
row-count checks
 ↓
reconciliation
 ↓
quality gate
 ↓
publish
```

Relevant dimensions include:

- row counts;
- reconciliation;
- freshness;
- bad records;
- partition completeness.

The purpose here is to show where validation fits in historical orchestration, not to re-teach Module 2.11.

---

# 52. Relationship to Module 2.12

Backfills depend on:

- interval-scoped transformations;
- deterministic processing;
- idempotency;
- partition awareness;
- safe reruns;
- state management.

Conceptually:

```text
correct transformation design
          ↓
correct historical orchestration
          ↓
safe reprocessing
```

Orchestration cannot compensate for non-idempotent transformation logic.

---

# 53. Learning Checkpoints

Ask after each major section:

- What interval is this run processing?
- Is this catch-up or deliberate backfill?
- Is this rerun or full rebuild?
- Is the output idempotent?
- What happens if the interval runs twice?
- Can the backfill overload the source?
- How will daily production be protected?
- What happens to downstream data?
- Does a logic change require shadow processing?
- Which partitions are affected?
- What validation is required?
- How can the operation be stopped safely?

These questions test reasoning, not memorization.

---

# 54. Code Quality Requirements

Examples in this chapter should:

- target Airflow 3.x;
- use realistic APIs;
- avoid invented syntax;
- be interval-aware;
- avoid inappropriate hard-coded dates;
- demonstrate safe partition handling;
- demonstrate idempotent patterns;
- explain important code;
- include error-handling considerations.

When an API is version-sensitive, verify it against the deployed Airflow 3.x release.

---

# 55. No Fabricated Performance or Cost Claims

Do not invent:

- exact throughput;
- exact backfill duration;
- exact infrastructure capacity;
- exact cost;
- guaranteed completion time.

Use measurements from the target environment for production planning.

---

# 56. Common Mistakes Checklist

- [ ] confusing catch-up with backfill;
- [ ] using wall-clock time instead of data intervals;
- [ ] unclear partition boundaries;
- [ ] overlapping partitions;
- [ ] missing partitions;
- [ ] non-idempotent historical writes;
- [ ] unlimited backfill concurrency;
- [ ] starving daily production;
- [ ] blindly rerunning everything;
- [ ] clearing too much;
- [ ] ignoring downstream invalidation;
- [ ] directly overwriting production during logic changes;
- [ ] no validation;
- [ ] no rollback strategy;
- [ ] ignoring late-arriving data;
- [ ] assuming task success means data correctness;
- [ ] treating huge backfills like ordinary daily runs.

---

# 57. Final Knowledge Checklist

You should be able to answer **YES**:

- [ ] Can I explain data intervals?
- [ ] Can I explain catch-up?
- [ ] Can I explain backfill?
- [ ] Can I distinguish catch-up, backfill, rerun, and rebuild?
- [ ] Can I explain Airflow 3.x scheduler-managed backfills?
- [ ] Can I explain clearing?
- [ ] Can I design partitioned runs?
- [ ] Can I pass interval context into processing logic?
- [ ] Can I make historical processing idempotent?
- [ ] Can I control backfill concurrency?
- [ ] Can I protect normal daily workloads?
- [ ] Can I design a 90-day backfill?
- [ ] Can I design a 180-day backfill?
- [ ] Can I handle late-arriving data?
- [ ] Can I perform a logic-change backfill?
- [ ] Can I use shadow processing?
- [ ] Can I safely replace corrected output?
- [ ] Can I identify downstream invalidation?
- [ ] Can I reason about asset partitions?
- [ ] Can I test historical processing?
- [ ] Can I observe a running backfill?
- [ ] Can I design safe recovery?
- [ ] Can I reason about cost and resource impact?

---

# 58. Final Mental Model

```text
historical need
      ↓
identify exact interval(s)
      ↓
why?
 ┌────┼───────────┬─────────────┐
 ↓    ↓           ↓             ↓
miss  late data   logic change  new history
 ↓    ↓           ↓             ↓
catch rerun       shadow         backfill
-up               processing
                  ↓
               compare
                  ↓
               validate
                  ↓
             replacement
                  ↓
          downstream impact
                  ↓
             recomputation
```

The production principles are:

1. **Process by data interval, not wall-clock accident.**
2. **Know why historical processing is happening.**
3. **Make partition boundaries explicit.**
4. **Make repeated execution safe.**
5. **Bound historical workload.**
6. **Protect normal production.**
7. **Treat late data as historical correction.**
8. **Treat logic changes as controlled historical migrations.**
9. **Validate before replacing trusted data.**
10. **Trace downstream consequences.**
11. **Make historical progress observable.**
12. **Keep rollback and auditability in the design.**

---

## Source Alignment

This chapter follows the supplied Topic 08 specification as the authoritative scope, terminology, ordering, production principles, hands-on requirements, and scope boundary. fileciteturn25file0L73-L99

The required progression and Topic 08 scope are based on the supplied specification, including historical processing, catch-up, backfills, partitioned runs, load control, logic-change processing, asset partitions, testing, failure injection, architecture exercises, and interview preparation. fileciteturn25file0L124-L168

The chapter treats Airflow 3.x as primary and older Airflow 2.x CLI behavior only as legacy/reference context, as required by the supplied specification. fileciteturn25file0L105-L120
