# Late-Arriving Data and Reprocessing Windows

> **Production Data Engineering topic**
>
> Late-arriving data is not merely an ingestion problem. It is a **data correctness + temporal reasoning + incremental processing + reprocessing strategy** problem.
>
> The production goal is not to eliminate late data. The goal is to build transformations that remain correct when data arrives after the period to which it belongs.

---

## 1. Learning Objectives

By the end of this chapter, you should be able to:

- distinguish **event time**, **load/arrival time**, and **processing time**;
- calculate and measure data lateness;
- explain why late facts occur and how they affect historical aggregates;
- measure lateness distributions and use p50/p95/p99 as decision inputs;
- choose a defensible reprocessing/lookback window;
- understand the cost-versus-correctness trade-off of different windows;
- compare event-date and load-date partitioning;
- reprocess affected partitions idempotently;
- define an explicit policy for data arriving outside the normal window;
- handle late-arriving dimensions with inferred/placeholder members;
- re-key historical facts when the real dimension arrives;
- reason about point-in-time dimension correctness;
- distinguish ordinary late-data correction from controlled historical restatement;
- understand valid time versus transaction/knowledge time;
- understand batch watermarks and allowed-lateness concepts;
- design observability around lateness and reprocessing;
- test incremental results against a full rebuild;
- debug production failures involving late facts, dimensions, partitions, and historical reporting.

The core reasoning chain is:

```text
event time
    vs
load / arrival time
    ↓
lateness
    ↓
lookback window
    ↓
affected partitions
    ↓
reprocessing
    ↓
late dimensions
    ↓
historical correction / restatement
```

A key principle is:

> **"Process yesterday's data" is not sufficient for many real-world systems.**

---

## 2. Prerequisites

This chapter assumes you already understand:

- deterministic pipeline structure;
- `RunContext`;
- logical data intervals;
- pure transformations;
- partition-scoped processing;
- deduplication;
- merge/upsert;
- idempotent loading;
- incremental processing;
- backfills.

The dependency chain is:

```text
01 Structuring ETL
      ↓
02 Deduplication and Merge Loads
      ↓
03 Incremental Processing and Backfills
      ↓
04 Late-Arriving Data and Reprocessing Windows
      ↓
05 Hashing
      ↓
06 Lookups and Enrichment
      ↓
...
```

The important connection to the previous topics is:

```text
incremental processing
        +
idempotent loading
        +
temporal reasoning
        =
safe late-data correction
```

---

## 3. Why Late-Arriving Data Exists

Consider an order:

```text
Event time:
2025-03-01 10:15
```

But the source system sends it to the data platform on:

```text
Arrival time:
2025-03-04 08:30
```

Therefore:

```text
event_time = 2025-03-01
loaded_at  = 2025-03-04
```

The order belongs to March 1 from a business/event-time perspective even though the data arrived on March 4.

```text
Mar 1                 Mar 2       Mar 3       Mar 4
  |----------------------|------------|------------|
  Event happens                                      |
                                                   Arrival
```

If the March 1 transformation ran only once, the March 1 result may be incomplete.

### Common causes

Late arrival is normal in production. Causes include:

- network outages;
- source-system downtime;
- delayed batch exports;
- retries and redelivery;
- API delays;
- CDC lag;
- mobile devices being offline;
- clock differences;
- manual corrections;
- source backlogs;
- delayed file delivery;
- upstream database maintenance;
- replication lag;
- event buffering.

### Practical analogy

Imagine a school attendance report.

A student was present on Monday, but the teacher's attendance device did not synchronize until Thursday.

The student was **present Monday**. Thursday is merely when the reporting system **learned about it**.

A good data pipeline preserves both facts.

---

## 4. Event Time vs Load Time

### Event time

**Event time** is when the real-world event occurred.

Examples:

- order created;
- payment completed;
- click occurred;
- sensor measurement taken;
- shipment delivered.

### Load / arrival time

**Load time** is when the data platform received or loaded the record.

### Processing time

**Processing time** is when a transformation actually ran over the record.

| Concept | Meaning | Example |
|---|---|---|
| `event_time` | When the event happened | `2025-03-01 10:15` |
| `loaded_at` | When the platform received it | `2025-03-04 08:30` |
| `processing_time` | When transformation ran | `2025-03-04 09:00` |

These timestamps answer different questions.

```text
What happened?
    event_time

When did our platform receive it?
    loaded_at

When did our transformation process it?
    processing_time
```

### Why the distinction matters

Suppose a daily revenue pipeline says:

```python
WHERE loaded_at::date = '2025-03-04'
```

That selects records **received on March 4**, not necessarily sales that **occurred on March 4**.

If an order happened March 1 and arrived March 4, a load-date-only transformation can assign it to the wrong business day.

A robust pipeline generally preserves both:

```text
event_time
loaded_at
```

and uses each according to its purpose.

---

## 5. What Is Data Lateness?

A simple definition is:

```text
lateness = arrival_time - event_time
```

For example:

```text
event_time   = Mar 1 10:00
arrival_time = Mar 3 10:00

lateness = 48 hours
```

Real systems usually have a distribution:

```text
Record A → 5 minutes late
Record B → 2 hours late
Record C → 1 day late
Record D → 7 days late
Record E → 45 days late
```

Therefore:

> **Lateness is usually a distribution, not one fixed value.**

### Unit and timezone considerations

Before measuring lateness:

1. use timezone-aware timestamps where appropriate;
2. standardize the comparison timezone;
3. understand timestamp precision;
4. define whether arrival means source creation, ingestion, or durable raw-layer receipt;
5. avoid mixing seconds, milliseconds, and microseconds accidentally.

For a UTC-normalized batch:

```python
lateness = loaded_at - event_time
```

A negative value can be an important signal rather than something to silently discard. It may indicate clock skew, timestamp semantics that differ from expectations, or malformed source data.

---

## 6. Measuring Lateness

A production pipeline should measure at least:

- count;
- minimum;
- maximum;
- median;
- p95;
- p99;
- percentage beyond the configured lookback window.

A conceptual Python calculation:

```python
import numpy as np

lateness_hours = np.array([
    0.08,
    0.17,
    0.33,
    0.50,
    1.0,
    2.0,
    4.0,
    8.0,
    24.0,
    72.0,
])

print("median:", np.percentile(lateness_hours, 50))
print("p95:", np.percentile(lateness_hours, 95))
print("p99:", np.percentile(lateness_hours, 99))
```

The exact values are illustrative. The important idea is to measure the actual production distribution.

### Production measurement model

```text
raw event
   │
   ├── event_time
   └── loaded_at
          │
          ▼
loaded_at - event_time
          │
          ▼
lateness distribution
          │
     ┌────┼────┐
     ▼    ▼    ▼
   p50   p95   p99
```

### Important distinction

A metric such as p99 is not a guarantee.

If:

```text
p99 = 3 days
```

that means approximately 99% of observations are at or below that threshold in the measured population and period, subject to the percentile definition and sample quality.

It does **not** mean:

```text
No record can ever arrive after 3 days.
```

That distinction is fundamental to production design.

---

## 7. Late Facts

A **late fact** is a fact whose event time belongs to an earlier business period than its arrival time.

Example:

```text
order_id | event_date | loaded_at
---------+------------+-------------------
1001     | 2025-03-01 | 2025-03-04 08:30
```

The fact:

- belongs to March 1;
- was learned on March 4;
- may require March 1 aggregates to be recomputed.

Potentially affected outputs include:

```text
daily revenue
daily order count
customer metrics
product metrics
monthly aggregates
```

### Why a late fact matters

Suppose March 1 originally contains:

```text
100 orders
$20,000 revenue
```

A late order arrives on March 4:

```text
$250
```

The correct March 1 result becomes:

```text
101 orders
$20,250 revenue
```

If the pipeline only processes March 4, March 1 remains stale.

### Fact correction principle

The correction should target the **business partition affected by the event**, not merely the partition on which the record happened to arrive.

---

## 8. Reprocessing Windows / Lookback Windows

A **reprocessing window**, also called a **lookback window**, means that each new run intentionally reprocesses a recent historical range instead of processing only the newest partition.

Example:

```text
lookback = 3 days
```

On March 10, the pipeline may process:

```text
March 7
March 8
March 9
March 10
```

instead of:

```text
March 10
```

Conceptually:

```text
               run date
                  ↓
Mar 7   Mar 8   Mar 9   Mar 10
 |-------|-------|-------|
       reprocessing window
```

### Python configuration

```python
from datetime import date, timedelta

run_date = date(2025, 3, 10)
lookback_days = 3

start_date = run_date - timedelta(days=lookback_days)

print(start_date)
print(run_date)
```

This example treats the window as four calendar dates inclusive of the run date.

Always define your boundary semantics explicitly. Another implementation might define `lookback_days=3` as the three dates before the current date.

### Why it works

Suppose an event for March 8 arrives on March 10.

If March 8 is inside the window:

```text
March 8
   ↓
reprocessed
   ↓
late event included
   ↓
March 8 output corrected
```

### Why idempotency matters

Reprocessing means deliberately running the same logical partition more than once.

Therefore the output operation must be safe:

```text
same inputs
+
same logic version
+
same partition
        ↓
same correct output
```

Partition overwrite, deterministic merge/upsert, or another proven idempotent strategy is usually preferable to blindly appending another copy.

---

## 9. Choosing the Lookback Window

Choosing a window should be a **measurement problem**, not a guess.

Consider:

- lateness distribution;
- business tolerance for incomplete historical results;
- freshness SLA;
- compute cost;
- storage cost;
- downstream impact;
- source behavior;
- frequency of historical corrections;
- reporting deadlines.

The basic trade-off is:

```text
small window
    ↓
lower compute
    +
higher risk of missing late data

large window
    ↓
higher compute
    +
better late-data coverage
```

The largest possible window is not automatically better.

### A useful decision question

Ask:

> "How much historical data must we reconsider on every run to satisfy the business correctness requirement at an acceptable cost?"

That is more useful than asking:

> "What lookback number do other teams use?"

### Example

Suppose measurements show:

```text
p95 = 18 hours
p99 = 3 days
```

A 3-day normal lookback might be reasonable **if**:

- the sample is representative;
- the business can tolerate exceptional records outside three days;
- the compute cost is acceptable;
- an explicit outside-window policy exists.

It is not automatically correct merely because p99 is three days.

---

## 10. Lateness Percentiles: p95 and p99

Percentiles are useful because average lateness can hide a long tail.

Consider:

```text
5 min
10 min
20 min
30 min
1 hr
2 hr
4 hr
8 hr
1 day
3 days
```

The:

- **median / p50** describes the middle of the distribution;
- **p95** is a high-tail threshold;
- **p99** is an even further high-tail threshold.

### Operational interpretation

If:

```text
p95 = 18 hours
p99 = 3 days
```

then the distribution has a meaningful tail.

A design might use:

```text
normal lookback ≈ 3 days
```

if that aligns with correctness and cost requirements.

But p95/p99 is an **input to the decision, not an automatic answer**.

### Why p99 is not a maximum

Suppose 10,000 records are observed.

A p99 near 3 days says roughly that the 99th percentile boundary is around three days. There may still be records at:

```text
5 days
14 days
45 days
```

Those outliers are exactly why an outside-window policy is necessary.

### Better operational design

Use percentiles together with:

```text
p50
p95
p99
max
outside-window rate
business impact
```

A stable p99 with a rapidly growing maximum can signal an emerging tail problem.

---

## 11. Cost vs Correctness Trade-Off

Illustrative trade-offs:

| Lookback | Compute | Late-data coverage | Operational complexity |
|---|---:|---:|---:|
| 0 days | Low | Low | Low |
| 1 day | Low | Moderate | Moderate |
| 3 days | Moderate | High | Moderate |
| 7 days | Higher | Higher | Moderate |
| 30 days | High | Very high | High |

These are **illustrative**, not universal measurements.

The production principle is:

> **Choose the smallest window that satisfies the required correctness and business tolerance, based on measured lateness and known correction behavior.**

### Cost is not only CPU

A larger window can increase:

- scanned data;
- database I/O;
- object-store reads;
- shuffle volume;
- downstream table writes;
- lock duration;
- validation time;
- pipeline runtime;
- opportunity cost for other workloads.

### Correctness is not binary

A business may accept:

```text
99.9% corrected automatically
+
0.1% routed through controlled exceptions
```

rather than paying the cost of continuously rebuilding a very large history.

The correct design depends on the business requirement.

---

## 12. Event-Date vs Load-Date Partitioning

Two common layouts are:

### Event-date partitioning

```text
event_date=2025-03-01
```

### Load-date partitioning

```text
loaded_date=2025-03-04
```

Consider an event:

```text
event_time = 2025-03-01 10:00
loaded_at  = 2025-03-04 08:30
```

With event-date partitioning, the record belongs in:

```text
event_date=2025-03-01
```

With load-date partitioning, it belongs in:

```text
loaded_date=2025-03-04
```

### Event-date partitioning

**Advantages**

- aligns naturally with event-time analytics;
- makes event-date reprocessing straightforward;
- historical business periods are grouped together.

**Disadvantages**

- late records may require writes to old partitions;
- ingestion may touch many historical partitions;
- operational workflows must support historical mutation safely.

### Load-date partitioning

**Advantages**

- aligns with arrival/ingestion operations;
- newly received data is physically grouped by arrival;
- useful for operational ingestion auditing.

**Disadvantages**

- event-date analytics may require broader scans or secondary filtering;
- late records for one business day are spread across multiple load-date partitions;
- reprocessing by event date may be more expensive or complex.

### There is no universal winner

Partitioning should reflect:

- dominant query patterns;
- incremental processing strategy;
- reprocessing behavior;
- storage layout;
- cost;
- retention;
- late-data characteristics.

A common architecture may retain raw data organized by load/arrival characteristics while building analytical layers around event/business date. The correct choice depends on the layer and workload.

---

## 13. Processing Data Inside the Reprocessing Window

A typical run:

```text
Run on Mar 10
      ↓
Lookback = 3 days
      ↓
Read Mar 7–10
      ↓
Include newly arrived late records
      ↓
Transform
      ↓
Recompute affected partitions
      ↓
Overwrite/merge safely
```

### Important subtlety: the whole window may be read, but not every partition must always be rewritten

There are two common approaches:

1. recompute all partitions in the window;
2. identify affected partitions and recompute only those.

The first is simpler. The second can reduce cost when dependency tracking is reliable.

### Partition selection

For an event-date model:

```python
affected_dates = sorted(
    events["event_time"].dt.date().unique()
)
```

Conceptually:

```text
arrival date
    ↓
inspect event dates
    ↓
identify affected partitions
    ↓
recompute those partitions
```

### Safe write

A simplified partition replacement pattern:

```python
def process_partition(events, partition_date):
    partition_events = events.filter(
        events["event_date"] == partition_date
    )

    result = build_daily_metric(partition_events)

    write_partition_atomically(
        result,
        partition_date=partition_date,
    )
```

The actual storage implementation varies, but the important property is that rerunning a partition replaces or deterministically merges its logical result rather than blindly appending duplicates.

---

## 14. Data Arriving Beyond the Reprocessing Window

Suppose:

```text
lookback = 3 days
```

but a March 1 event arrives on March 15.

That event is:

```text
14 days late
```

and outside the normal window.

The pipeline needs an explicit policy.

### Strategy A — Reject

Use only when the business rules genuinely permit rejection.

A rejection should be observable and auditable. It should not mean silently dropping data.

### Strategy B — Park / quarantine

Store late records separately:

```text
outside_window
      ↓
quarantine
      ↓
review / targeted action
```

This is useful when automatic mutation of historical outputs is undesirable.

### Strategy C — Manual / targeted backfill

Identify affected partitions:

```text
March 1
March 2
...
```

and recompute them through a controlled backfill process.

### Strategy D — Expand the normal window

If outside-window events become systematic, the current window may no longer match source behavior.

This is a configuration/operational decision, not an emergency workaround.

### Strategy E — Restatement process

For financially or operationally significant historical correction, use a controlled restatement workflow.

### Decision table

| Situation | Possible response |
|---|---|
| Within normal window | Automatic reprocessing |
| Rare, low-impact outside window | Quarantine or targeted backfill |
| Repeated outside-window arrivals | Reassess lookback and source contract |
| Closed financial/reporting period | Controlled restatement |
| Material historical correction | Audited correction workflow |

---

## 15. Strategies for Extremely Late Data

Consider:

```text
7-day late
30-day late
6-month late
2-year late
```

Do not use one universal policy.

Consider:

- business importance;
- data contract;
- freshness SLA;
- financial reporting requirements;
- audit requirements;
- historical correction policy;
- downstream dependencies;
- cost of recomputation.

### A useful classification

```text
Normal late
    ↓
inside automated window

Exceptional late
    ↓
outside window
    ↓
controlled exception

Historical correction
    ↓
materially changes published results
    ↓
restatement workflow
```

Do not assume every late record should trigger a full historical rebuild.

---

## 16. Late-Arriving Dimensions

A **fact** records an event or measurable business activity.

Examples:

```text
order
payment
click
shipment
```

A **dimension** describes entities:

```text
customer
product
store
```

Now consider:

```text
Order event:
2025-03-01

Customer dimension:
arrives 2025-03-03
```

The fact exists before the corresponding dimension member is available.

### Why this matters

A fact table might need:

```text
customer_key
```

but the correct dimension row does not yet exist.

If the pipeline simply fails, the order may disappear from downstream analytics.

If it invents a permanent fake customer, historical integrity can be damaged.

This is why inferred/placeholder members are useful.

---

## 17. Inferred / Placeholder Members

An **inferred member** is a temporary dimension record created when a fact arrives before complete dimension information is available.

For example:

```text
customer_key = -1
```

or another explicitly reserved unknown key.

Before the real dimension arrives:

```text
order_id | customer_key
---------+-------------
1001     | -1
```

Later, after the real customer arrives:

```text
customer_id = 5821
```

the fact can be corrected:

```text
order_id | customer_key
---------+-------------
1001     | 5821
```

### Why inferred members exist

They can:

- preserve referential integrity;
- prevent facts from being lost;
- allow downstream pipelines to continue;
- make missing dimensional information visible.

### Risks

An inferred member should not become a permanent garbage bucket.

Track:

- number of inferred members;
- age of inferred members;
- percentage of facts referencing them;
- unresolved members;
- reconciliation failures.

### Example dimension

```text
customer_key | customer_id | status
-------------+-------------+----------------
-1           | NULL        | inferred
5821         | C-9001      | active
```

The special key should be explicit and documented.

---

## 18. Re-Keying Historical Facts

The workflow is:

```text
fact
  ↓
temporary/inferred dimension key
  ↓
real dimension arrives
  ↓
resolve real key
  ↓
update affected facts
  ↓
recompute dependent aggregates
```

### SQL example

Suppose:

```sql
UPDATE fact_orders f
SET customer_key = d.customer_key
FROM dim_customer d
WHERE f.customer_id = d.customer_id
  AND f.customer_key = -1;
```

This is illustrative. A production implementation should include:

- uniqueness constraints;
- correct effective-date logic where applicable;
- bounded affected rows;
- audit columns;
- idempotency;
- reconciliation.

### Python/Polars-style reasoning

```python
corrected = facts.join(
    customers.select(["customer_id", "customer_key"]),
    on="customer_id",
    how="left",
)

corrected = corrected.with_columns(
    pl.coalesce(
        [pl.col("customer_key_right"), pl.col("customer_key")]
    ).alias("customer_key")
)
```

The exact expression can vary by Polars version and schema naming. The important operation is a deterministic reconciliation from business identifier to dimension key.

### Downstream impact

Re-keying may change:

- customer aggregates;
- product/customer attribution;
- segmentation;
- lifetime metrics;
- monthly reporting.

Therefore dimension correction is not merely a lookup operation. It can be a transformation dependency problem.

---

## 19. Point-in-Time Dimension Correctness

A late dimension is not always solved by choosing the dimension row that exists **today**.

Consider a customer whose country changes:

```text
Mar 1  → India
Mar 10 → Singapore
```

An order occurs:

```text
Mar 5
```

If you process that order on March 20 and join it to the customer's current row, you may incorrectly label the March 5 order as Singapore.

For a Type 2-style history:

```text
customer_key | valid_from | valid_to | country
-------------+------------+----------+---------
5821         | Mar 1      | Mar 10   | India
5821         | Mar 10     | NULL     | Singapore
```

The March 5 order should resolve to:

```text
country = India
```

because that version was valid at event time.

### Simplified point-in-time SQL

```sql
SELECT
    f.order_id,
    d.customer_key,
    d.country
FROM fact_orders AS f
JOIN dim_customer AS d
  ON f.customer_id = d.customer_id
 AND f.event_time >= d.valid_from
 AND (
        f.event_time < d.valid_to
        OR d.valid_to IS NULL
     );
```

The exact boundary convention must be consistent across the model.

### Senior-level lesson

> **A historical fact should normally be enriched according to the dimension state relevant to the fact's business time, not merely the current dimension state.**

---

## 20. Closing Books and Historical Corrections

Some periods become operationally or financially **closed**.

Examples include:

- month-end accounting;
- payroll;
- financial reporting;
- regulatory reporting.

After a period is closed, late data may not simply mutate the published result silently.

A controlled system may require:

- a correction workflow;
- audit records;
- approval;
- versioned reporting;
- downstream notification;
- reconciliation.

This is a Data Engineering system-design issue, not legal advice.

### Why "just rerun the partition" may be wrong

For an open daily metric:

```text
March 10
```

automatic reprocessing may be normal.

For a published closed month:

```text
March financial report
```

changing the output without tracking the change can create an audit and reproducibility problem.

The data platform should therefore distinguish:

```text
ordinary operational correction
```

from:

```text
controlled historical restatement
```

---

## 21. Restatements

A **restatement** means deliberately changing previously published historical results because corrected or newly available information changes the result.

Example:

```text
Published March revenue:
$10.0M
```

Later:

```text
Corrected March revenue:
$10.3M
```

The engineering workflow may include:

```text
late/corrected data
       ↓
impact assessment
       ↓
historical recomputation
       ↓
validation
       ↓
approval/control point
       ↓
new published version
       ↓
audit trail
       ↓
downstream notification
```

### Restatement versus ordinary late-data handling

| Ordinary late data | Restatement |
|---|---|
| Usually within normal correction window | Usually historical/closed |
| Automated | Controlled |
| Routine | Exceptional or materially significant |
| Often invisible to consumers | May require notification |
| Idempotent partition replacement | Versioned/audited correction |

These are not absolute rules, but they are useful production distinctions.

### Restatement requirements

Consider:

- business approval;
- auditability;
- versioning;
- reproducibility;
- downstream notification;
- historical reporting consistency;
- rollback strategy.

---

## 22. Bitemporal Thinking

Bitemporal reasoning becomes useful when one timestamp is not enough to reconstruct history.

Two important temporal dimensions are:

### Valid time

When a fact is true in the real/business world.

### Transaction / knowledge time

When the system knew about or recorded that fact.

Example:

```text
valid_time:
March 1

knowledge_time:
March 4
```

The event may have been true on March 1 while the data platform did not know about it until March 4.

### Why this matters

Bitemporal thinking helps with:

- historical reconstruction;
- audit;
- late corrections;
- regulatory systems;
- reproducibility.

Do not overcomplicate the concept initially.

Think:

```text
What was true?
    valid time

When did we know it?
    knowledge time
```

---

## 23. Valid Time vs Transaction / Knowledge Time

| Dimension | Question |
|---|---|
| Valid time | When was this fact true? |
| Knowledge / transaction time | When did our system know or record it? |

Example:

```text
A customer address was actually changed on March 1.

The company received the correction on March 5.

A report generated on March 3 may legitimately show
the old information.

A report generated after March 5 may show the correction.
```

This distinction explains why two reports produced at different knowledge times can legitimately differ even when both are historically correct for their information state.

### Simple bitemporal representation

```text
customer_id | valid_from | valid_to | known_from | known_to | value
------------+------------+----------+------------+----------+------
C1          | Mar 1      | NULL     | Mar 5      | NULL     | new address
```

A production design may use different columns and structures. The key is preserving the two questions separately.

---

## 24. Batch Watermarks and Allowed Lateness

A **watermark** generally represents progress through some time dimension in processing.

**Allowed lateness** describes how long the system is willing to reconsider data that appears after an expected boundary.

Terminology varies between batch and streaming systems, so use the terms carefully.

A useful conceptual model for batch processing is:

```text
Current processing point
        ↓
Lookback / allowed-lateness window
        ↓
Historical data reconsidered
```

For example:

```text
watermark = Mar 10
lookback  = 3 days
```

The system may reconsider:

```text
Mar 7–Mar 10
```

### Important distinction

A watermark is not automatically the same thing as a reprocessing window.

Think of:

```text
watermark
= how far processing has progressed

lookback / allowed lateness
= how much history we intentionally reconsider
```

A system can track source progress while still reopening a controlled historical range.

---

## 25. Designing a Production Reprocessing Strategy

A production architecture can be modeled as:

```text
                  ┌──────────────────────┐
                  │     Source Events    │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Bronze / Raw Layer   │
                  └──────────┬───────────┘
                             │
                     event_time │ loaded_at
                             ▼
                  ┌──────────────────────┐
                  │ Lateness Measurement │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Incremental Pipeline │
                  │ + Lookback Window    │
                  └──────────┬───────────┘
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
             Normal Data          Late Data
                    │                 │
                    │          within window
                    │                 │
                    │             Reprocess
                    │                 │
                    └────────┬────────┘
                             ▼
                    Corrected Output
                             │
                             ▼
                  Outside-window policy
                             │
                   ┌─────────┴─────────┐
                   ▼                   ▼
              Quarantine          Backfill /
                                  Restatement
```

### Component responsibilities

**Raw layer**

Preserve the original event and arrival metadata.

**Lateness measurement**

Continuously measure:

```text
loaded_at - event_time
```

**Incremental pipeline**

Process the current interval plus the configured lookback.

**Idempotent output**

Make repeated partition processing safe.

**Outside-window policy**

Do not let extreme lateness become an undefined edge case.

**Historical correction**

Provide a deliberate path for materially important historical changes.

---

# 26. Hands-On Implementation

We will build a realistic `daily_active_users` example.

## 26.1 Scenario

Input events contain:

```text
user_id
event_time
_loaded_at
event_type
```

We will generate at least 14 days of event-time data and deliberately introduce late arrivals.

Example:

```text
event_time = 2025-03-01 10:00
_loaded_at = 2025-03-04 09:00
```

The event belongs to March 1 but was loaded March 4.

---

## 26.2 Step 1 — Generate Event Data

The following is an illustrative local lab.

```python
from datetime import datetime, timedelta, timezone
import random

random.seed(7)

start = datetime(2025, 3, 1, tzinfo=timezone.utc)

events = []

for i in range(14 * 20):
    event_time = start + timedelta(
        minutes=random.randint(0, 14 * 24 * 60 - 1)
    )

    # Most records arrive quickly, but some are deliberately late.
    delay_hours = random.choice(
        [0.1, 0.5, 1, 2, 6, 24, 48, 72]
    )

    loaded_at = event_time + timedelta(hours=delay_hours)

    events.append(
        {
            "user_id": random.randint(1, 50),
            "event_time": event_time,
            "_loaded_at": loaded_at,
            "event_type": "active",
        }
    )

# Inject an intentionally very late record.
events.append(
    {
        "user_id": 999,
        "event_time": datetime(2025, 3, 1, 10, tzinfo=timezone.utc),
        "_loaded_at": datetime(2025, 3, 15, 9, tzinfo=timezone.utc),
        "event_type": "active",
    }
)
```

### What this teaches

We have deliberately separated:

```text
when the user acted
```

from:

```text
when the pipeline learned about the action
```

That separation is the foundation of the rest of the exercise.

---

## 26.3 Step 2 — Build the Naive Current-Day Pipeline

A naive design might filter only records loaded on the current date:

```python
from datetime import date

def naive_daily_events(events, run_date: date):
    return [
        event
        for event in events
        if event["_loaded_at"].date() == run_date
    ]
```

This is easy to understand, but it answers:

> "What arrived today?"

not:

> "What events belong to the business date we need to report?"

If a March 1 event arrives March 4, a March 1 result will not automatically be revisited.

---

## 26.4 Step 3 — Demonstrate the Error

Suppose March 1 initially has:

```text
42 active users
```

Then a late event arrives on March 4 for a user who was not previously counted.

The correct March 1 result might become:

```text
43 active users
```

But a current-day-only pipeline can leave March 1 at:

```text
42
```

This is a correctness failure caused by a temporal assumption.

---

## 26.5 Step 4 — Implement a Configurable Lookback

```python
from datetime import date, timedelta

def dates_to_process(
    run_date: date,
    lookback_days: int,
):
    start_date = run_date - timedelta(days=lookback_days)

    current = start_date
    dates = []

    while current <= run_date:
        dates.append(current)
        current += timedelta(days=1)

    return dates
```

Example:

```python
print(dates_to_process(date(2025, 3, 10), 3))
```

Conceptually:

```text
2025-03-07
2025-03-08
2025-03-09
2025-03-10
```

---

## 26.6 Step 5 — Measure Lateness

### Polars

```python
import polars as pl

df = pl.DataFrame(events)

df = df.with_columns(
    (
        pl.col("_loaded_at") - pl.col("event_time")
    ).alias("lateness")
)

summary = df.select(
    [
        pl.len().alias("record_count"),
        pl.col("lateness").min().alias("min_lateness"),
        pl.col("lateness").median().alias("median_lateness"),
        pl.col("lateness").quantile(0.95).alias("p95_lateness"),
        pl.col("lateness").quantile(0.99).alias("p99_lateness"),
        pl.col("lateness").max().alias("max_lateness"),
    ]
)

print(summary)
```

This code assumes a Polars version supporting the shown temporal expressions. For production code, pin and test the exact Polars version used by the project.

### Important metric

Also calculate the percentage beyond the current window.

```python
lookback = timedelta(days=3)

outside_window = df.filter(
    pl.col("lateness") > lookback
)

outside_rate = outside_window.height / max(df.height, 1)

print("outside-window rate:", outside_rate)
```

This is often more operationally useful than looking only at p99.

---

## 26.7 Step 6 — Calculate p95 and p99 with NumPy

```python
import numpy as np

lateness_hours = np.array(
    [
        value.total_seconds() / 3600
        for value in df["lateness"].to_list()
    ]
)

p95 = np.percentile(lateness_hours, 95)
p99 = np.percentile(lateness_hours, 99)

print("p95 hours:", p95)
print("p99 hours:", p99)
```

Interpretation:

```text
p95 = high-tail behavior
p99 = farther-tail behavior
```

Neither is a maximum.

---

## 26.8 Step 7 — Choose a Window

Suppose the measured production behavior is:

```text
median = 2 hours
p95    = 18 hours
p99    = 3 days
max    = 14 days
```

A possible design is:

```text
normal lookback = 3 days
```

with:

```text
> 3 days
    ↓
outside-window policy
```

That policy might be:

```text
quarantine
+
targeted backfill
+
restatement for closed material periods
```

The decision must also account for business tolerance and compute cost.

---

## 26.9 Step 8 — Reprocess the Affected Date Range

For an event-date analytical model:

```python
def event_dates_in_window(
    df: pl.DataFrame,
    run_date,
    lookback_days: int,
):
    start_date = run_date - timedelta(days=lookback_days)

    return (
        df
        .filter(
            pl.col("event_time").dt.date().is_between(
                start_date,
                run_date,
                closed="both",
            )
        )
        .with_columns(
            pl.col("event_time").dt.date().alias("event_date")
        )
    )
```

Then compute the daily active-user metric:

```python
def daily_active_users(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df
        .filter(pl.col("event_type") == "active")
        .group_by("event_date")
        .agg(
            pl.col("user_id").n_unique().alias("daily_active_users")
        )
        .sort("event_date")
    )
```

The resulting partitions can be replaced using an idempotent write strategy.

---

## 26.10 Step 9 — Compare with a Full Rebuild

A full rebuild is the reference implementation.

```python
def full_rebuild(df: pl.DataFrame) -> pl.DataFrame:
    prepared = df.with_columns(
        pl.col("event_time").dt.date().alias("event_date")
    )

    return daily_active_users(prepared)
```

The incremental result for a sufficiently wide window should match the corresponding full-rebuild result.

A reconciliation pattern:

```python
def compare_incremental_to_full(
    incremental: pl.DataFrame,
    full: pl.DataFrame,
) -> pl.DataFrame:
    return (
        incremental
        .join(
            full,
            on="event_date",
            how="full",
            suffix="_full",
        )
        .with_columns(
            (
                pl.col("daily_active_users")
                ==
                pl.col("daily_active_users_full")
            ).alias("matches")
        )
    )
```

For production, normalize nulls and schemas explicitly before comparing.

### Core invariant

```text
incremental result
=
full rebuild result
```

for the historical range whose late data has been fully considered.

---

## 26.11 Step 10 — Introduce Outside-Window Data

Our intentionally injected record:

```text
event_time = Mar 1
_loaded_at = Mar 15
```

is far outside a 3-day lookback when the run is March 15.

If March 1 is no longer inside the normal automatic window, the record must enter the explicit exception process.

Example:

```python
def classify_late_record(
    event_time,
    loaded_at,
    lookback: timedelta,
):
    lateness = loaded_at - event_time

    if lateness <= lookback:
        return "within_window"

    return "outside_window"
```

A real system would classify the record using the pipeline's run context and current processing boundary, not only the record's timestamps.

---

## 26.12 Step 11 — Implement an Outside-Window Policy

A simple local policy:

```python
def outside_window_action(lateness: timedelta) -> str:
    if lateness <= timedelta(days=3):
        return "automatic_reprocessing"

    if lateness <= timedelta(days=30):
        return "targeted_backfill"

    return "historical_review"
```

This is intentionally illustrative.

A production policy should usually be driven by:

- dataset configuration;
- business criticality;
- period state;
- data contract;
- owner;
- reporting impact.

Do not hide such policy in arbitrary code branches.

---

## 26.13 Step 12 — Add Late Customer Dimension Data

Suppose the event arrives first:

```text
order_id | customer_id | event_time
---------+-------------+-----------
1001     | C-9001      | Mar 1
```

but the customer dimension arrives later.

Before the dimension arrives:

```text
customer_key = -1
```

After arrival:

```text
customer_id = C-9001
customer_key = 5821
```

The fact can be reconciled.

---

## 26.14 Step 13 — Use an Inferred Member

A simple dimension table:

```sql
CREATE TABLE dim_customer (
    customer_key BIGINT PRIMARY KEY,
    customer_id VARCHAR UNIQUE,
    customer_name VARCHAR,
    member_status VARCHAR NOT NULL
);
```

Create an inferred member:

```sql
INSERT INTO dim_customer (
    customer_key,
    customer_id,
    customer_name,
    member_status
)
VALUES (
    -1,
    NULL,
    'Unknown / Inferred Customer',
    'inferred'
);
```

The fact can temporarily point to:

```text
customer_key = -1
```

The key point is that the fact remains present and referentially valid.

---

## 26.15 Step 14 — Correct the Fact

After the dimension arrives:

```sql
UPDATE fact_orders AS f
SET customer_key = d.customer_key
FROM dim_customer AS d
WHERE f.customer_id = d.customer_id
  AND f.customer_key = -1;
```

A production implementation must also handle:

- duplicate customer identifiers;
- effective dates;
- multiple inferred rows;
- audit columns;
- concurrent updates;
- downstream aggregate recomputation.

### Reconciliation invariant

After correction:

```text
facts_with_real_customer_key
+
intentionally_unknown_facts
=
all eligible facts
```

and the number of unresolved inferred members should be explainable.

---

## 26.16 Step 15 — Simulate a Month-Close Restatement

Suppose:

```text
March revenue originally published = $10.0M
```

A six-month-old source correction changes March revenue to:

```text
$10.3M
```

Do not silently overwrite a closed report.

Instead:

```text
correction received
       ↓
identify affected March outputs
       ↓
recompute in controlled environment
       ↓
validate against source/reconciliation
       ↓
record old and new values
       ↓
apply controlled publication/cutover
       ↓
record audit metadata
```

Useful metadata includes:

```text
restatement_id
affected_period
old_value
new_value
logic_version
source_correction_reference
execution_run_id
applied_at
```

The exact control process depends on the organization.

---

# 27. Required Code Patterns by Tool

## 27.1 Python

Use Python for:

- run-date/window calculations;
- classification;
- control flow;
- test fixtures;
- orchestration boundaries.

```python
from datetime import date, timedelta

def processing_range(
    run_date: date,
    lookback_days: int,
):
    return (
        run_date - timedelta(days=lookback_days),
        run_date,
    )
```

Keep business transformation functions deterministic.

Avoid:

```python
datetime.now()
```

inside a transformation.

Prefer:

```python
def transform(df, run_date):
    ...
```

where the run context supplies the logical time.

---

## 27.2 Polars

Polars is useful for local, columnar transformation work.

```python
import polars as pl

result = (
    df
    .with_columns(
        pl.col("event_time").dt.date().alias("event_date"),
        (
            pl.col("_loaded_at") - pl.col("event_time")
        ).alias("lateness"),
    )
    .group_by("event_date")
    .agg(
        pl.col("user_id").n_unique().alias("dau")
    )
    .sort("event_date")
)
```

This makes the temporal fields visible rather than hiding them in an implicit ingestion convention.

---

## 27.3 DuckDB

DuckDB is useful for SQL-based local analytical validation.

```sql
SELECT
    CAST(event_time AS DATE) AS event_date,
    COUNT(DISTINCT user_id) AS daily_active_users
FROM events
GROUP BY 1
ORDER BY 1;
```

Lateness:

```sql
SELECT
    quantile_cont(
        date_diff('second', event_time, _loaded_at),
        0.95
    ) AS p95_lateness_seconds,
    quantile_cont(
        date_diff('second', event_time, _loaded_at),
        0.99
    ) AS p99_lateness_seconds
FROM events;
```

SQL percentile and date-difference syntax varies across engines. The conceptual operation is:

```text
arrival timestamp - event timestamp
        ↓
numeric lateness
        ↓
percentile
```

Always verify syntax against the actual production engine.

---

## 27.4 SQL

SQL is useful for:

- partition recomputation;
- aggregation;
- dimension joins;
- reconciliation;
- targeted correction.

Example:

```sql
SELECT
    CAST(event_time AS DATE) AS event_date,
    COUNT(DISTINCT user_id) AS dau
FROM silver_events
WHERE event_time >= TIMESTAMP '2025-03-07 00:00:00'
  AND event_time <  TIMESTAMP '2025-03-11 00:00:00'
GROUP BY 1
ORDER BY 1;
```

This uses a half-open interval:

```text
[start, end)
```

which avoids ambiguity at midnight boundaries.

---

# 28. Testing Late Data

A serious test strategy must deliberately create temporal failures.

## Test 1 — On-time event

Input:

```text
event_time = Mar 10
loaded_at  = Mar 10
```

**Invariant:** event is processed normally.

---

## Test 2 — One-day late event

Input:

```text
event_time = Mar 9
loaded_at  = Mar 10
```

**Invariant:** event affects March 9 when March 9 is inside the configured reprocessing policy.

---

## Test 3 — Three-day late event inside configured window

If:

```text
lookback = 3 days
```

then a three-day-late event should be classified consistently according to the documented boundary.

**Invariant:** boundary semantics are explicit and deterministic.

---

## Test 4 — Late event outside configured window

Input:

```text
event_time = Mar 1
loaded_at  = Mar 10
lookback   = 3 days
```

**Invariant:** record is not silently lost; it follows the outside-window policy.

---

## Test 5 — Duplicate late event

Send the same late event twice.

**Invariant:**

```text
one logical event
=
one contribution to the result
```

This depends on the deduplication strategy established in Topic 02.

---

## Test 6 — Multiple late versions for the same business key

Provide:

```text
version 1
version 2
```

in out-of-order arrival.

**Invariant:** the correct version-selection rule is applied consistently.

This connects directly to deterministic merge/version logic from the previous topic.

---

## Test 7 — Late dimension member

Fact arrives before dimension.

**Invariant:** fact remains representable, and the inferred member can later be reconciled.

---

## Test 8 — Historical dimension change

A customer changes attributes after the original event.

**Invariant:** historical facts resolve to the correct dimension version according to the business's temporal semantics.

---

## Test 9 — Restatement

Recompute a closed historical period after a source correction.

**Invariant:** old and new results are traceable and the correction is explicitly controlled.

---

## Test 10 — Incremental result equals full rebuild

For the same input history:

```text
incremental
vs
full rebuild
```

**Invariant:**

```text
same logical output
```

for the tested historical range.

---

## Test 11 — Reprocessing twice

Run the same lookback twice.

**Invariant:**

```text
output_after_run_1
=
output_after_run_2
```

No duplicate contribution should appear.

---

## Test 12 — Deterministic late-data processing

Run the same input, configuration, run interval, and logic version multiple times.

**Invariant:**

```text
same inputs
+
same logic
+
same interval
=
same output
```

---

# 29. Debugging Late-Data Problems

## Scenario 1 — Daily revenue is lower than the source system

### Symptoms

Warehouse revenue is consistently below the source.

### Likely causes

- late events;
- current-day-only processing;
- source/warehouse timing mismatch;
- timezone error;
- deduplication mistake.

### Investigation

Check:

```sql
SELECT
    COUNT(*) AS late_count
FROM raw_orders
WHERE _loaded_at > event_time + INTERVAL '3 days';
```

Then compare event-time distributions and load-time distributions.

### Incorrect solution

Increase the window blindly to 90 days.

### Correct solution

Measure lateness, quantify impact, choose a justified window, and define an outside-window policy.

### Prevention

Monitor:

```text
p95
p99
outside-window count
reconciliation gap
```

---

## Scenario 2 — A late event arrives but does not affect the historical partition

### Symptoms

Raw data contains the event, but the business partition remains unchanged.

### Likely causes

- pipeline filters by `_loaded_at` instead of `event_time`;
- partition selection uses current date only;
- event date extraction is wrong;
- timezone conversion shifts the date.

### Investigation

Trace:

```text
raw record
→ event date
→ selected partitions
→ transformation input
→ output partition
```

### Correct solution

Select affected business partitions using event time and the documented reprocessing policy.

---

## Scenario 3 — Lookback window is too small

### Symptoms

A growing percentage of corrections arrive outside the normal window.

### Investigation

Trend:

```text
outside_window_rate
p95
p99
max
```

over time.

### Correct solution

Determine whether source behavior changed. If so:

- update the source contract if possible;
- reassess the normal window;
- retain an exception path for outliers.

---

## Scenario 4 — Lookback window is too large

### Symptoms

Runtime and compute cost increase sharply.

### Investigation

Measure:

```text
partitions scanned
partitions rewritten
bytes read
bytes written
runtime
```

### Incorrect solution

Reduce the window until the job is fast, without checking correctness.

### Correct solution

Optimize affected-partition selection, partition pruning, incremental aggregation, and controlled exception handling while preserving the correctness requirement.

---

## Scenario 5 — Customer dimension arrives after facts

### Symptoms

Facts contain `customer_key=-1` for too long.

### Investigation

Measure:

```text
inferred_member_count
inferred_member_age
unresolved_customer_count
```

### Correct solution

Implement reconciliation when the dimension arrives and alert on unresolved inferred members beyond the expected SLA.

---

## Scenario 6 — Historical facts use the wrong dimension version

### Symptoms

A March 5 order is labeled with a customer attribute that became valid March 10.

### Investigation

Check:

- dimension validity boundaries;
- event timestamp;
- join conditions;
- timezone;
- inclusive/exclusive boundary semantics.

### Incorrect solution

Join every fact to the customer's current row.

### Correct solution

Use point-in-time logic appropriate to the dimension's temporal model.

---

## Scenario 7 — A closed month silently changes

### Symptoms

A previously published month changes without an explicit correction event.

### Investigation

Trace:

```text
late record
→ selected partition
→ reprocessing job
→ output write
→ publication state
```

### Correct solution

Separate normal automatic correction from controlled restatement for closed periods.

---

## Scenario 8 — Late data is repeatedly reprocessed

### Symptoms

The same historical partitions are recomputed unnecessarily.

### Likely causes

- window too wide;
- no affected-partition tracking;
- no state;
- repeated retries without idempotent checkpoints;
- source repeatedly redelivering the same records.

### Prevention

Track:

```text
run_id
partition
logic_version
last_processed_at
affected_by_late_data
```

and retain the ability to deliberately rerun when needed.

---

# 30. Production Anti-Patterns

| Anti-pattern | Why it fails | Better approach |
|---|---|---|
| Process only today's partition | Misses late data | Use measured lookback/reprocessing |
| Use load time as event time | Incorrect business dates | Preserve both timestamps |
| Arbitrary 7-day window | No evidence | Measure lateness distribution |
| Infinite lookback | Excessive compute | Controlled window + exception policy |
| Ignore late dimensions | Broken enrichment | Inferred members + reconciliation |
| Silently modify closed periods | Audit/reporting problems | Controlled restatement |
| No outside-window policy | Unhandled edge cases | Quarantine/backfill/restatement |
| Use current dimension value for historical facts | Temporal correctness error | Point-in-time logic |
| Reprocess without idempotency | Duplicate/corrupt output | Idempotent partition processing |
| Treat p99 as guaranteed maximum | Outliers still exist | Explicit extreme-lateness policy |
| Mix event-time and load-time filters | Inconsistent results | Define time semantics per step |
| Hide timezone conversion | Date shifts | Standardize and document timezone semantics |
| Recompute everything forever | Cost grows without bound | Affected partitions + controlled backfills |
| Silently discard extreme late records | Data loss | Quarantine and observable exception path |
| Put lookback logic in business SQL everywhere | Difficult to change consistently | Centralize run/window policy |
| Use "latest" dimension rows implicitly | Historical drift | Explicit point-in-time semantics |
| Change a closed period through a routine job | Publication state is unclear | Separate correction and publication workflows |

---

# 31. Production Observability

At minimum, monitor:

- lateness median;
- p95 lateness;
- p99 lateness;
- count of late records;
- count outside the window;
- affected partitions;
- reprocessing volume;
- reprocessing runtime;
- late-dimension count;
- inferred-member count;
- restatement count;
- reconciliation failures;
- failed reprocessing jobs.

Example metrics:

```text
late_records_total
late_records_outside_window_total
lateness_p95_seconds
lateness_p99_seconds
reprocessed_partitions_total
reprocessing_runtime_seconds
inferred_dimension_members_total
```

### Why these metrics matter

A lookback window can become stale as source behavior changes.

For example:

```text
Month 1:
p99 = 2 days

Month 6:
p99 = 6 days
```

A 3-day window that was once reasonable may now systematically miss data.

Similarly:

```text
reprocessing_runtime_seconds ↑
reprocessed_partitions_total ↑
```

can indicate that the normal window has become operationally expensive.

### Useful dashboard dimensions

Break metrics down by:

- dataset;
- source;
- region;
- event type;
- producer;
- date;
- pipeline version.

This can reveal that one source is causing most late arrivals while the rest of the platform remains healthy.

---

# 32. Production Design Checklist

## Time semantics

- [ ] Event time defined.
- [ ] Load time defined.
- [ ] Processing time understood.
- [ ] Time zones standardized.
- [ ] Timestamp precision understood.
- [ ] Boundary semantics documented.

## Lateness

- [ ] Lateness measured.
- [ ] p95 measured.
- [ ] p99 measured.
- [ ] Maximum observed lateness monitored.
- [ ] Outside-window rate monitored.
- [ ] Negative or invalid lateness investigated.

## Reprocessing

- [ ] Lookback window explicitly defined.
- [ ] Window based on measured behavior.
- [ ] Partition strategy supports reprocessing.
- [ ] Reprocessing is idempotent.
- [ ] Reconciliation exists.
- [ ] Incremental output can be compared with a full rebuild.
- [ ] Logic version is identifiable.

## Late dimensions

- [ ] Unknown/inferred member strategy exists.
- [ ] Re-keying is supported.
- [ ] Historical dimension versioning is understood.
- [ ] Point-in-time semantics are explicit.
- [ ] Unresolved inferred members are observable.

## Historical correction

- [ ] Closed-period behavior defined.
- [ ] Restatement process defined.
- [ ] Audit trail exists.
- [ ] Rollback/versioning considered.
- [ ] Downstream publication behavior is defined.
- [ ] Material corrections are distinguishable from routine processing.

---

# 33. Hands-On Exercises

## Beginner

### Exercise 1 — Event time vs load time

Given:

```text
event_time = 2025-03-01 10:15
loaded_at  = 2025-03-04 08:30
```

Calculate the lateness and explain which business date the event belongs to.

**Solution guidance:** subtract event time from arrival time and preserve March 1 as the event date.

---

### Exercise 2 — Calculate lateness

Given:

```text
event_time = 12:00
arrival     = 15:30
```

Calculate:

```text
3 hours 30 minutes
```

Then explain why the record may need a historical correction.

---

### Exercise 3 — Identify a late fact

Given:

```text
order_id | event_date | loaded_at
1001     | Mar 1      | Mar 4
1002     | Mar 4      | Mar 4
```

Identify the late fact.

**Solution:** `1001`.

---

### Exercise 4 — Build a one-day lookback

Implement a function that returns:

```text
run_date - 1 day
through
run_date
```

Use an explicit inclusive/exclusive convention.

---

### Exercise 5 — Build a three-day lookback

Implement:

```python
dates_to_process(run_date, lookback_days=3)
```

and test its boundaries.

---

## Intermediate

### Exercise 6 — Calculate p95 and p99

Given a list of lateness durations:

```python
lateness_hours = [
    0.1, 0.2, 0.5, 1, 2, 3, 5,
    8, 12, 18, 24, 36, 48, 72
]
```

Calculate p95 and p99.

**Key lesson:** percentile values describe distribution thresholds, not guaranteed maxima.

---

### Exercise 7 — Choose a lookback window

Observed behavior:

```text
p50 = 2 hours
p95 = 20 hours
p99 = 4 days
max = 12 days
```

Design a normal window and an outside-window policy.

**Solution guidance:** a four-day window could be considered, but justify it using business tolerance and cost. Do not treat p99 as a guarantee.

---

### Exercise 8 — Event-date partition reprocessing

Build a function that takes:

```text
run_date
lookback_days
```

and returns the event dates that must be recomputed.

Then prove that a late event for an older date is included.

---

### Exercise 9 — Detect outside-window records

For:

```text
lookback = 3 days
```

classify records as:

```text
within_window
outside_window
```

Then calculate the outside-window rate.

---

### Exercise 10 — Compare event-date and load-date partitioning

For:

```text
event_time = Mar 1
loaded_at = Mar 4
```

show the physical partition under each strategy and explain the operational implications.

---

## Advanced

### Exercise 11 — Late-dimension handling

Design a customer dimension process where facts can arrive before customer metadata.

Include:

- inferred member;
- later reconciliation;
- metrics for unresolved inferred members.

---

### Exercise 12 — Implement inferred members

Create a reserved unknown customer key and write SQL that temporarily assigns facts to it.

Then write SQL that corrects the facts after the customer arrives.

---

### Exercise 13 — Re-key facts

Given a fact table with temporary customer keys, re-key affected rows using the real customer identifier.

Add an audit column indicating the correction run.

---

### Exercise 14 — Historical restatement

Build a small March revenue table, then introduce a late correction after March is considered closed.

Implement a controlled restatement record containing:

```text
restatement_id
period
old_value
new_value
logic_version
run_id
applied_at
```

---

### Exercise 15 — Incremental vs full-rebuild reconciliation

Implement both:

```text
incremental with lookback
full rebuild
```

and compare their outputs over a historical test range.

Your goal is to prove:

```text
incremental == full rebuild
```

for the supported correctness window.

---

## Expert

### Exercise 16 — Global event platform

Design late-data handling for a global event platform with:

- multiple time zones;
- clock skew;
- intermittent mobile connectivity;
- regional outages;
- high event volume.

Explain event-time normalization, lateness measurement, lookback, outside-window handling, and historical correction.

---

### Exercise 17 — Dynamic lookback strategy

Design a system that uses observed lateness trends to recommend changes to the normal window.

Constraints:

- changes must be reviewed;
- p99 cannot be treated as a guaranteed maximum;
- compute cost must remain bounded.

---

### Exercise 18 — Late-dimension correction system

Design a system where:

```text
facts can arrive days before dimensions
```

and explain:

- inferred members;
- reconciliation;
- re-keying;
- point-in-time correctness;
- downstream aggregate recomputation.

---

### Exercise 19 — Closed-period restatement workflow

Design a workflow for a closed monthly reporting period.

Include:

- detection;
- impact analysis;
- recomputation;
- validation;
- approval/control point;
- publication;
- audit trail;
- downstream notification.

---

### Exercise 20 — Bitemporal history

Design a bitemporal model that can answer:

1. What was true on March 1?
2. What did the system believe on March 3?
3. What did the system learn on March 5?
4. What is the corrected current interpretation?

Provide table design and example queries.

---

# 34. Senior Data Engineer Reasoning

Senior engineers do not start by asking:

> "How many days should the window be?"

They start with the temporal facts.

Use this decision flow:

```text
When did the event happen?
        ↓
When did we receive it?
        ↓
How late is it?
        ↓
Is it inside the normal window?
        ↓
Which partitions are affected?
        ↓
Which downstream outputs depend on them?
        ↓
Can we safely reprocess them?
        ↓
If outside the window, what policy applies?
        ↓
Does this affect a closed/reporting period?
        ↓
Is this a normal correction or a restatement?
```

### The senior reasoning pattern

A junior design might say:

> "Let's use a seven-day window."

A senior design says:

> "Let's measure lateness, understand the business tolerance, identify the affected partitions, estimate the cost of different windows, define an outside-window path, and verify incremental output against a full rebuild."

That difference is important.

### Core principle

> **Late-arriving data is fundamentally a temporal correctness problem.**

---

# 35. Interview Questions

## Basic — 10 Questions

### 1. What is event time?

**Expected answer:** The time at which the real-world event occurred.

**Explanation:** It represents business/event semantics rather than ingestion timing.

**Key concepts:** event time, business time.

**Senior-level insight:** Event time should not be inferred from arrival time when the source provides a reliable event timestamp.

---

### 2. What is load time?

**Expected answer:** The time at which the data platform received or loaded the record.

**Explanation:** It tells us when the system learned about the data.

**Key concepts:** arrival, ingestion.

**Senior-level insight:** Load time is valuable for operational auditing and lateness measurement even when event time drives analytics.

---

### 3. What is data lateness?

**Expected answer:**

```text
arrival time - event time
```

**Explanation:** It measures how long after the event the platform received the record.

**Key concepts:** temporal difference.

**Senior-level insight:** Lateness should be treated as a distribution.

---

### 4. What is a late fact?

**Expected answer:** A fact whose event time belongs to an earlier period than its arrival time.

**Explanation:** A March 1 order arriving March 4 is a late fact.

**Key concepts:** facts, event time, arrival time.

**Senior-level insight:** Late facts can invalidate already-produced aggregates.

---

### 5. What is a lookback window?

**Expected answer:** A historical range intentionally reconsidered during an incremental run.

**Explanation:** A three-day lookback can process the current day plus recent historical dates.

**Key concepts:** reprocessing, incremental.

**Senior-level insight:** The window must be idempotent and justified by measured lateness.

---

### 6. Why not process only today's partition?

**Expected answer:** Because late records may belong to older event dates.

**Explanation:** Current-day-only processing can leave historical outputs incomplete.

**Key concepts:** late data.

**Senior-level insight:** Processing boundaries should follow business/event semantics.

---

### 7. What is p95 lateness?

**Expected answer:** A percentile describing a high point in the observed lateness distribution.

**Explanation:** Roughly 95% of observations are at or below that threshold under the chosen percentile definition.

**Key concepts:** percentile.

**Senior-level insight:** p95 is a decision input, not a correctness guarantee.

---

### 8. What is p99 lateness?

**Expected answer:** A farther-tail percentile of lateness.

**Explanation:** It captures more extreme behavior than p95.

**Key concepts:** long tail.

**Senior-level insight:** Records can still arrive after p99.

---

### 9. What is an inferred dimension member?

**Expected answer:** A temporary dimension row used when a fact arrives before complete dimension information.

**Explanation:** It lets the fact remain represented rather than being dropped.

**Key concepts:** referential integrity.

**Senior-level insight:** Inferred members need reconciliation and monitoring.

---

### 10. What is a restatement?

**Expected answer:** A controlled change to previously published historical results because corrected information changes the result.

**Explanation:** It differs from routine late-data handling.

**Key concepts:** historical correction, audit.

**Senior-level insight:** Restatements should be explicit, traceable, and reproducible.

---

## Moderate — 10 Questions

### 11. Why is load time insufficient for daily business reporting?

**Expected answer:** Load time describes when the platform received the record, not when the event occurred.

**Explanation:** Late events would be assigned to the wrong business period.

**Key concepts:** event time vs load time.

**Senior-level insight:** Preserve both timestamps and use each intentionally.

---

### 12. How would you choose a three-day lookback?

**Expected answer:** Measure lateness and determine that three days provides acceptable coverage at acceptable cost, while defining an outside-window policy.

**Explanation:** A window should be evidence-driven.

**Key concepts:** p95/p99, business tolerance.

**Senior-level insight:** There is no universal correct window.

---

### 13. Why can average lateness be misleading?

**Expected answer:** A small number of very late records can create a long tail that the average hides.

**Explanation:** Percentiles reveal tail behavior.

**Key concepts:** distribution, p95, p99.

**Senior-level insight:** Monitor tail behavior over time.

---

### 14. What happens when data arrives beyond the normal window?

**Expected answer:** It should follow an explicit policy such as quarantine, targeted backfill, expanded window, or controlled restatement.

**Explanation:** It should never become an undefined edge case.

**Key concepts:** exception handling.

**Senior-level insight:** Outside-window rates can reveal source-contract changes.

---

### 15. Compare event-date and load-date partitioning.

**Expected answer:** Event-date groups records by business occurrence; load-date groups them by arrival.

**Explanation:** Each has different query and reprocessing implications.

**Key concepts:** storage layout.

**Senior-level insight:** Partitioning is workload-dependent.

---

### 16. Why are inferred members useful?

**Expected answer:** They preserve fact representation and referential integrity before the dimension arrives.

**Explanation:** Later reconciliation can replace the temporary relationship.

**Key concepts:** late dimensions.

**Senior-level insight:** Track unresolved inferred members as an operational metric.

---

### 17. Why can current dimension values be wrong for historical facts?

**Expected answer:** Dimension attributes may change over time.

**Explanation:** A historical event should generally use the dimension state appropriate to its event time.

**Key concepts:** SCD2, point-in-time.

**Senior-level insight:** Late arrival increases the chance that temporal joins are exercised after dimension history has changed.

---

### 18. Why is idempotency important for reprocessing?

**Expected answer:** The same historical partition may be processed repeatedly.

**Explanation:** Repeated processing must not duplicate or corrupt results.

**Key concepts:** retries, reruns.

**Senior-level insight:** Exactly-once effects often come from at-least-once execution plus idempotent writes.

---

### 19. Why should closed periods be treated differently?

**Expected answer:** A silent change to a published period can break auditability and reproducibility.

**Explanation:** Controlled corrections make the change explicit.

**Key concepts:** publication state, restatement.

**Senior-level insight:** Data state and publication state are related but distinct concerns.

---

### 20. What does p99 not tell you?

**Expected answer:** It does not provide a guaranteed maximum lateness.

**Explanation:** Outliers can still exceed p99.

**Key concepts:** tail distribution.

**Senior-level insight:** Always define an explicit extreme-lateness path.

---

## Hard — 10 Questions

### 21. Design a daily pipeline with a three-day lookback.

**Expected answer:** Preserve event/load timestamps, measure lateness, read the current interval plus three days, recompute affected partitions idempotently, monitor outside-window records, and compare correctness against a full rebuild.

**Explanation:** The design combines incremental processing with temporal correction.

**Key concepts:** lookback, idempotency.

**Senior-level insight:** A window without an exception policy is incomplete.

---

### 22. What if p99 suddenly changes from two days to six days?

**Expected answer:** Investigate source behavior, segment the distribution, quantify outside-window impact, and decide whether to change the window or improve the source contract.

**Explanation:** This may be a source regression or a genuine behavior change.

**Key concepts:** observability, operational feedback.

**Senior-level insight:** Treat lateness metrics as part of pipeline health.

---

### 23. How do you prevent a late event from being permanently missed?

**Expected answer:** Use a sufficiently justified lookback plus an outside-window mechanism.

**Explanation:** No finite normal window can guarantee against arbitrary lateness.

**Key concepts:** exception path.

**Senior-level insight:** Correctness is achieved through normal automation plus controlled exceptions.

---

### 24. A customer dimension arrives two days after facts. What do you do?

**Expected answer:** Allow an inferred member, then reconcile and re-key the affected facts when the dimension arrives.

**Explanation:** This preserves continuity.

**Key concepts:** inferred members.

**Senior-level insight:** Re-keying can require downstream aggregate recomputation.

---

### 25. How would you prove an incremental pipeline is correct?

**Expected answer:** Compare its output to a deterministic full rebuild across historical test intervals containing on-time, late, duplicate, and boundary cases.

**Explanation:** The full rebuild acts as a reference.

**Key concepts:** reconciliation.

**Senior-level insight:** Test the incremental algorithm, not just individual SQL expressions.

---

### 26. Why might a seven-day window still be wrong?

**Expected answer:** The actual lateness distribution may exceed seven days or business requirements may require a different correction behavior.

**Explanation:** Seven days is an arbitrary number unless justified.

**Key concepts:** evidence-driven design.

**Senior-level insight:** Window size is a business/engineering decision.

---

### 27. How would you detect a timezone-related late-data bug?

**Expected answer:** Compare raw timestamps, normalized timestamps, event-date derivation, and boundary cases around midnight.

**Explanation:** Timezone conversion can shift event dates.

**Key concepts:** temporal normalization.

**Senior-level insight:** Test events around timezone and daylight-saving boundaries where applicable.

---

### 28. What should happen when a closed month receives a late material correction?

**Expected answer:** Route it through a controlled restatement process rather than silently mutating the published result.

**Explanation:** The correction must be auditable and reproducible.

**Key concepts:** restatement.

**Senior-level insight:** Separate computation from publication control.

---

### 29. Explain valid time and knowledge time.

**Expected answer:** Valid time says when the fact was true; knowledge time says when the system knew/recorded it.

**Explanation:** Both are needed for some historical reconstruction problems.

**Key concepts:** bitemporal thinking.

**Senior-level insight:** Different report dates can legitimately expose different knowledge states.

---

### 30. How does a watermark relate to a lookback window?

**Expected answer:** A watermark can represent processing progress, while the lookback determines how much historical data is reconsidered.

**Explanation:** They solve related but distinct problems.

**Key concepts:** batch watermarks, allowed lateness.

**Senior-level insight:** Do not conflate processing progress with historical correction policy.

---

## Advanced — 10 Questions

### 31. Design late-data handling for 500 million events per day.

**Expected answer:** Preserve raw event/load times, measure lateness at scale, use partition pruning and a bounded lookback, reprocess only affected partitions where safe, and route extreme lateness to controlled backfills/restatements.

**Explanation:** The design must bound compute while maintaining correctness.

**Key concepts:** scale, cost, temporal correctness.

**Senior-level insight:** The architecture needs both automatic and exception paths.

---

### 32. How would you choose between p95 and p99 for a lookback?

**Expected answer:** Neither should be chosen automatically. Evaluate business tolerance, cost, correction impact, and the tail beyond each percentile.

**Explanation:** Percentiles describe observed distributions.

**Key concepts:** decision framework.

**Senior-level insight:** A lower percentile may be acceptable when exceptions are cheap and well-controlled; a higher percentile may be warranted for critical correctness.

---

### 33. Design an outside-window exception system.

**Expected answer:** Detect records outside the normal window, persist them in an observable exception dataset, identify affected outputs, classify business impact, and route to targeted backfill or restatement.

**Explanation:** Exceptional lateness needs deterministic handling.

**Key concepts:** exception architecture.

**Senior-level insight:** Exception handling should be part of the normal design, not an emergency script.

---

### 34. How would you safely re-key historical facts?

**Expected answer:** Identify affected facts, resolve the correct dimension version, apply an idempotent update/merge, audit the change, and recompute dependent aggregates.

**Explanation:** Re-keying changes dimensional attribution.

**Key concepts:** inferred members, PIT correctness.

**Senior-level insight:** The impact graph matters as much as the fact update.

---

### 35. Design a dynamic lookback system.

**Expected answer:** Monitor lateness distributions, outside-window rates, and cost; generate a proposed configuration change; validate it; and apply controlled configuration updates.

**Explanation:** Source behavior can evolve.

**Key concepts:** adaptive operations.

**Senior-level insight:** Automation should recommend or apply bounded changes without turning p99 into an absolute guarantee.

---

### 36. How would you support historical reproducibility?

**Expected answer:** Store event time, knowledge/transaction time where required, logic version, run ID, source references, and output version.

**Explanation:** Reproducibility requires knowing both the data state and transformation state.

**Key concepts:** bitemporal, versioning.

**Senior-level insight:** "Current table contents" alone are often insufficient for audit-grade reconstruction.

---

### 37. How would you design late-data handling for multiple regions?

**Expected answer:** Normalize timestamps, retain source-region metadata, account for clock skew and ingestion delays, and define region-aware monitoring.

**Explanation:** Different regions can have different latency distributions.

**Key concepts:** global systems.

**Senior-level insight:** Aggregate p99 can hide a problematic region.

---

### 38. How would you prevent a restatement from corrupting current reporting?

**Expected answer:** Recompute in isolation, validate, publish through a controlled cutover/versioning mechanism, and retain the previous result for rollback/audit.

**Explanation:** Computation and publication should be separable.

**Key concepts:** safe historical correction.

**Senior-level insight:** Shadow computation reduces risk.

---

### 39. What is the relationship between late data and downstream dependencies?

**Expected answer:** A late fact can affect not only its immediate partition but every downstream aggregate or model derived from it.

**Explanation:** Reprocessing scope must follow dependency propagation.

**Key concepts:** DAG impact.

**Senior-level insight:** "Affected partition" should be defined at the correct layer, not only at the raw table.

---

### 40. What is the strongest correctness test for a lookback pipeline?

**Expected answer:** Demonstrate that incremental processing with the documented lookback and exception handling produces the same logical result as a full deterministic rebuild for the supported range, including late and duplicate cases.

**Explanation:** This tests the algorithm rather than only the implementation.

**Key concepts:** equivalence testing.

**Senior-level insight:** Reconciliation against a full rebuild is one of the most powerful validation techniques for incremental transformations.

---

# 36. Architecture Questions

## Architecture 1 — 99% within 24 hours, 1% up to 7 days

Design a daily pipeline where:

```text
99% ≤ 24 hours
rare events ≤ 7 days
```

### Reference solution

Use:

```text
event_time + loaded_at
        ↓
lateness metrics
        ↓
normal lookback selected from measurements
        ↓
automatic reprocessing
        ↓
outside-window exception path
```

If the business can tolerate rare exceptions, the normal window need not necessarily be seven days. The architecture should make the trade-off explicit.

---

## Architecture 2 — Late events affect monthly revenue

Requirements:

- daily reporting;
- monthly reporting;
- historical late facts.

### Reference solution

Use:

- event-date partitions;
- bounded daily lookback;
- monthly aggregation derived from corrected daily facts;
- explicit month-close state;
- controlled restatement for post-close material corrections.

---

## Architecture 3 — Reprocessing framework for 500 GB/day

### Reference solution

Design for:

- partition pruning;
- bounded lookback;
- affected-partition discovery;
- parallel processing with resource limits;
- idempotent writes;
- checkpointing;
- reconciliation;
- cost monitoring.

Do not default to rebuilding all historical data.

---

## Architecture 4 — Late-dimension strategy

### Reference solution

```text
fact arrives
    ↓
lookup dimension
    ↓
missing?
    ↓ yes
inferred member
    ↓
dimension arrives
    ↓
re-key facts
    ↓
recompute dependent outputs
```

Add observability for unresolved members.

---

## Architecture 5 — Inferred-member workflow

### Reference solution

Define:

- reserved inferred key;
- business identifier;
- reconciliation job;
- maximum unresolved age;
- correction audit;
- downstream refresh behavior.

---

## Architecture 6 — Closed-month correction workflow

### Reference solution

```text
late correction
    ↓
impact analysis
    ↓
historical recomputation
    ↓
validation
    ↓
controlled publication
    ↓
audit record
    ↓
consumer notification
```

Keep the previous published version available according to the organization's retention and governance requirements.

---

## Architecture 7 — Bitemporal event history

### Reference solution

Represent:

```text
valid_from / valid_to
known_from / known_to
```

or equivalent temporal fields.

The model should answer both:

```text
What was true at time T?
```

and:

```text
What did the system know at time T?
```

---

## Architecture 8 — Outside-window exception process

### Reference solution

Create a durable exception dataset containing:

```text
record identifier
event time
arrival time
lateness
dataset
affected partition
classification
status
owner
resolution run
```

Then route:

```text
low impact → review
targeted historical impact → backfill
closed/material impact → restatement
```

---

## Architecture 9 — Observability for lateness

### Reference solution

Dashboard:

```text
p50
p95
p99
max
outside-window count/rate
reprocessed partitions
reprocessing runtime
inferred members
restatements
reconciliation failures
```

Slice by source and dataset.

---

## Architecture 10 — Prove incremental equals full rebuild

### Reference solution

For selected historical test ranges:

1. build deterministic full result;
2. start from an earlier incremental state;
3. inject late events;
4. run lookback processing;
5. compare outputs;
6. repeat;
7. test duplicates;
8. test outside-window exceptions;
9. record mismatches.

The acceptance invariant is:

```text
incremental logical result
=
full rebuild logical result
```

for the range and correction policy the system claims to support.

---

# 37. Production Case Study

Consider:

```text
Mobile App
   ↓
Event API
   ↓
Raw Events
   ↓
Silver Events
   ↓
Daily Active Users
   ↓
Monthly Analytics
```

Requirements:

- 500 million events/day;
- 95% arrive within 2 hours;
- 99% arrive within 24 hours;
- rare events arrive up to 14 days late;
- customer dimension may arrive later;
- monthly reporting exists;
- production must remain available.

## Design the event-time strategy

Preserve:

```text
event_time
_loaded_at
processing_time
```

Normalize timestamp semantics and define business-date derivation explicitly.

---

## Design lateness metrics

Measure:

```text
p50
p95
p99
max
outside-normal-window rate
```

Also segment by:

```text
region
source version
event type
```

because a global percentile can hide localized failures.

---

## Design the lookback window

The requirements say:

```text
95% ≤ 2 hours
99% ≤ 24 hours
rare ≤ 14 days
```

A normal window could be selected somewhere around the high-confidence operational range, but the exact number must account for:

- cost;
- freshness;
- downstream tolerance;
- source behavior;
- correction frequency.

A 24-hour window is one possible baseline to evaluate; it is not automatically correct.

Then define:

```text
outside normal window
        ↓
targeted correction
```

for rare events.

---

## Design outside-window handling

For events arriving after the normal window:

```text
record
  ↓
exception dataset
  ↓
impact analysis
  ↓
affected event dates
  ↓
targeted historical recomputation
```

For closed monthly reporting:

```text
material impact
  ↓
restatement workflow
```

---

## Design late-dimension handling

```text
event
 ↓
customer lookup
 ↓
missing
 ↓
inferred member
 ↓
dimension arrives
 ↓
reconciliation
 ↓
re-key
 ↓
dependent aggregates
```

Point-in-time dimension logic must be applied where customer attributes are time-varying.

---

## Design production availability

Do not make the online or normal daily path wait for rare historical corrections.

Use:

```text
normal incremental path
        +
asynchronous historical correction path
```

This separates:

```text
fresh daily processing
```

from:

```text
exceptional historical repair
```

---

## Design observability

At minimum:

```text
late_records_total
late_records_outside_window_total
lateness_p95_seconds
lateness_p99_seconds
reprocessed_partitions_total
reprocessing_runtime_seconds
inferred_dimension_members_total
restatement_count
reconciliation_failures_total
```

Alert on meaningful changes rather than every individual late event.

---

## Design correctness validation

Continuously or periodically compare:

```text
incremental results
vs
full-rebuild reference
```

on selected historical ranges.

Test:

- on-time data;
- late data;
- duplicate late data;
- boundary lateness;
- outside-window data;
- late dimensions;
- historical dimension changes;
- restatements.

---

# 38. A Complete Senior-Level Reference Architecture

A robust design can be summarized as:

```text
                         ┌──────────────────────┐
                         │     Source Events    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Immutable Bronze   │
                         │ event_time, loaded_at│
                         └──────────┬───────────┘
                                    │
                           ┌────────┴────────┐
                           ▼                 ▼
                  Lateness Metrics      Raw Quality
                           │                 │
                           └────────┬────────┘
                                    ▼
                         ┌──────────────────────┐
                         │ Incremental Planner  │
                         │ RunContext + Window  │
                         └──────────┬───────────┘
                                    │
                          ┌─────────┴──────────┐
                          ▼                    ▼
                 In-window records      Outside-window
                          │                    │
                          ▼                    ▼
                 Reprocess affected       Exception
                   event partitions        dataset
                          │                    │
                          ▼                    ▼
                    Silver outputs      Backfill / review
                          │                    │
                          └─────────┬──────────┘
                                    ▼
                         ┌──────────────────────┐
                         │  Dimension Enrichment│
                         │  PIT / Inferred Keys │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  Gold Aggregations   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Publication / Report │
                         └──────────┬───────────┘
                                    │
                         closed period?
                              ┌─────┴─────┐
                              │           │
                             no          yes
                              │           │
                         normal flow   restatement
                                          │
                                          ▼
                                   version + audit
```

### Design properties

The architecture should provide:

1. explicit time semantics;
2. measured lateness;
3. bounded automatic reprocessing;
4. idempotent output;
5. explicit outside-window handling;
6. late-dimension reconciliation;
7. point-in-time correctness;
8. controlled historical correction;
9. observability;
10. reconciliation against a deterministic reference.

---

# 39. Final Mental Model

Keep these three formulas in mind.

### Late data

```text
Late Data
=
Event happened earlier
+
System learned later
```

### Production handling

```text
Production Handling
=
Measure lateness
+
Choose a justified lookback
+
Reprocess affected partitions
+
Handle late dimensions
+
Define an outside-window policy
+
Control historical corrections
```

### Historical correctness

```text
Historical Correctness
=
Valid Time
+
Knowledge Time
+
Deterministic Reprocessing
+
Auditable Restatement
```

The most important idea is:

> **The goal is not to eliminate late data. The goal is to design a pipeline that remains correct when late data inevitably occurs.**

---

# 40. Exit Criteria

Before moving to the next topic, you should be able to independently:

- [ ] explain event time vs load time;
- [ ] explain processing time;
- [ ] calculate data lateness;
- [ ] explain why late facts occur;
- [ ] measure lateness distributions;
- [ ] calculate p95/p99;
- [ ] explain why p99 is not a maximum;
- [ ] choose a defensible reprocessing window;
- [ ] explain cost vs correctness;
- [ ] explain event-date vs load-date partitioning;
- [ ] reprocess affected partitions;
- [ ] explain why idempotency is required;
- [ ] handle data beyond the normal window;
- [ ] design quarantine/backfill strategies;
- [ ] handle late-arriving dimensions;
- [ ] use inferred members;
- [ ] re-key historical facts;
- [ ] reason about point-in-time dimension correctness;
- [ ] explain closed periods;
- [ ] design controlled restatements;
- [ ] explain valid time vs knowledge time;
- [ ] understand batch watermarks and allowed lateness;
- [ ] design production observability;
- [ ] test late-data edge cases;
- [ ] debug temporal correctness failures;
- [ ] prove incremental correctness against a full rebuild;
- [ ] explain the architecture in a senior Data Engineering interview.

---

# 41. Final Quality-Control Checklist

Use this before considering the topic complete.

### Conceptual coverage

- [x] Beginner-friendly intuition.
- [x] Event time and load time clearly distinguished.
- [x] Processing time explained.
- [x] Lateness mathematically defined.
- [x] Late facts explained.
- [x] Lookback/reprocessing windows explained.
- [x] Lookback selection treated as evidence-driven.
- [x] p95 and p99 explained.
- [x] Cost vs correctness explained.
- [x] Event-date vs load-date partitioning covered.
- [x] Outside-window policy covered.
- [x] Late-arriving dimensions covered.
- [x] Inferred members covered.
- [x] Re-keying covered.
- [x] Point-in-time correctness introduced.
- [x] Closing books covered.
- [x] Restatements covered.
- [x] Bitemporal thinking covered.
- [x] Valid time vs knowledge/transaction time covered.
- [x] Batch watermarks and allowed lateness covered.

### Implementation coverage

- [x] Python examples.
- [x] Polars examples.
- [x] DuckDB examples.
- [x] SQL examples.
- [x] Lateness calculations.
- [x] Percentile calculations.
- [x] Partition processing.
- [x] Dimension lookup.
- [x] Re-keying.
- [x] Reprocessing.
- [x] Reconciliation.

### Engineering coverage

- [x] Realistic hands-on project.
- [x] Late-data edge-case tests.
- [x] Debugging scenarios.
- [x] Production anti-patterns.
- [x] Observability.
- [x] Progressive exercises.
- [x] Basic/Moderate/Hard/Advanced interview questions.
- [x] Architecture questions.
- [x] Production case study.
- [x] Final mental model.
- [x] Exit criteria.

### Scope discipline

This chapter stays focused on:

```text
late data
+
temporal correctness
+
reprocessing windows
+
late dimensions
+
historical correction
```

It builds on earlier incremental/idempotent processing concepts rather than replacing them.

---

# 42. File-Safety and Study-Scope Note

This chapter is designed as a **self-contained learning artifact** for:

```text
12-Transformation-Patterns-and-Pipeline-Design/
04-late-arriving-data-and-reprocessing-windows.md
```

It does not require helper files, notebooks, generated configuration, or project-side scripts to understand the concepts.

The intended learning progression is:

```text
Basic Time Concepts
        ↓
Event Time vs Load Time
        ↓
Lateness
        ↓
Late Facts
        ↓
Lookback Windows
        ↓
p95 / p99
        ↓
Reprocessing
        ↓
Late Dimensions
        ↓
Historical Corrections
        ↓
Restatements
        ↓
Bitemporal Thinking
        ↓
Production Architecture
        ↓
Testing
        ↓
Debugging
        ↓
Senior-Level Design
```

The central production habit to carry into the next topic is:

> **Whenever a pipeline processes time-dependent data, explicitly ask when the event happened, when the system learned about it, which outputs are affected, how far history is automatically reconsidered, and what happens when the data arrives later than that policy allows.**
