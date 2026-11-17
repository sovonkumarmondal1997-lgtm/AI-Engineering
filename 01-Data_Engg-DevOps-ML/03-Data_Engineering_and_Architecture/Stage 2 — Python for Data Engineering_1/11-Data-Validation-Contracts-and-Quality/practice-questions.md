# Practice Questions — Reconciliation and Row-Count Audits

> **Module:** Python for Data Engineering — Data Validation, Contracts, and Quality  
> **Topic:** 09 — Reconciliation and Row-Count Audits  
> **Purpose:** Practice reconciliation from fundamentals through production-grade Data Engineering scenarios.  
> **Structure:** 40 questions — 10 Basic, 10 Moderate, 10 Hard, 10 Advanced.

---

# 1. Basic Questions

## Question 1 — What Is Reconciliation?

In your own words, explain what data reconciliation means in a Data Engineering pipeline.

Your answer should identify:

- the two or more data boundaries being compared;
- what is being compared;
- why the comparison exists;
- what action can result from a mismatch.

---

## Question 2 — Row-Count Audit

A source table contains 50,000 rows and the target table contains 49,850 rows.

Answer:

1. What is the row-count difference?
2. Which side has fewer rows?
3. Does this prove that 150 records are missing?
4. What additional check would you perform to identify the specific records?

---

## Question 3 — Equal Counts, Different Data

The source contains:

```text
A
B
C
D
```

The target contains:

```text
A
B
C
X
```

Both datasets contain four rows.

Answer:

1. Would a row-count audit pass?
2. Is the data actually reconciled?
3. Which source record is missing?
4. Which target record is unexpected?
5. What type of reconciliation detects this problem?

---

## Question 4 — Count Difference

Given:

```text
source_count = 1,000
target_count = 950
```

Calculate:

1. absolute difference;
2. signed difference using `target - source`;
3. percentage difference relative to the source.

Write the formula before calculating the result.

---

## Question 5 — Python Count Reconciliation

Write a Python function:

```python
reconcile_counts(source_count, target_count)
```

that returns `True` only when the two counts are exactly equal.

The function should reject negative counts.

---

## Question 6 — Missing Records

The source IDs are:

```python
{"A", "B", "C", "D", "E"}
```

The target IDs are:

```python
{"A", "B", "C", "E"}
```

Using Python sets, determine:

1. the missing IDs;
2. the unexpected target IDs;
3. the number of missing records.

---

## Question 7 — Unexpected Records

The source contains:

```text
101
102
103
104
```

The target contains:

```text
101
102
103
104
105
106
```

Answer:

1. What are the unexpected records?
2. What is the count difference?
3. Which reconciliation technique should identify the unexpected records?

---

## Question 8 — Validation vs Reconciliation

Explain the difference between:

```text
validation
```

and:

```text
reconciliation
```

Give one practical Data Engineering example for each.

---

## Question 9 — Audit Evidence

A reconciliation job reports:

```text
FAIL
```

but stores no source count, target count, run ID, timestamp, or rule information.

Explain why this is insufficient for a production Data Engineering system.

List at least five pieces of evidence that should be retained.

---

## Question 10 — Transformation-Aware Reconciliation

A pipeline intentionally removes cancelled orders.

The source contains:

```text
100,000 rows
```

The target contains:

```text
92,000 rows
```

Should a production reconciliation automatically fail because the counts differ?

Explain why or why not.

---

# 2. Moderate Questions

## Question 11 — Percentage Tolerance

A pipeline has:

```text
source_count = 1,000,000
target_count = 999,000
```

The documented tolerance is `0.2%`.

Determine whether the count reconciliation passes.

Show:

1. absolute difference;
2. percentage difference;
3. comparison with the tolerance.

---

## Question 12 — Zero Baseline

Consider these three cases:

```text
0 → 0
0 → 10
10 → 0
```

For each case:

1. calculate or describe the percentage difference;
2. explain why a naive percentage formula can fail;
3. propose a sensible production classification.

---

## Question 13 — SQL Missing-Key Query

Write SQL that returns records present in:

```text
source.orders
```

but missing from:

```text
target.orders
```

using `order_id` as the reconciliation key.

Explain why the query is an anti-join.

---

## Question 14 — SQL Unexpected-Key Query

Write SQL that returns records present in:

```text
target.orders
```

but not in:

```text
source.orders
```

using `order_id`.

Explain how this differs from the previous question.

---

## Question 15 — Duplicate Detection

A target table contains:

```text
order_id
---------
A
B
B
C
D
D
D
```

Write SQL that identifies duplicate `order_id` values and reports their occurrence counts.

Then explain why duplicate detection is necessary even when source and target row counts are equal.

---

## Question 16 — Aggregate Reconciliation

The source reports:

```text
row_count = 100,000
total_amount = 5,000,000
```

The target reports:

```text
row_count = 100,000
total_amount = 4,950,000
```

Answer:

1. Which check passes?
2. Which check fails?
3. Why is the aggregate mismatch important?
4. Give two possible causes.

---

## Question 17 — Partition Reconciliation

Global counts are:

```text
source = 1,000,000
target = 1,000,000
```

Daily counts are:

```text
Date         Source       Target
2026-09-28   300,000      300,000
2026-09-29   350,000      400,000
2026-09-30   350,000      300,000
```

Answer:

1. Does the global count expose a problem?
2. Which partitions differ?
3. What could have happened?
4. Why is partition-level reconciliation valuable?

---

## Question 18 — pandas Reconciliation

Given:

```python
import pandas as pd

source = pd.DataFrame({
    "order_id": ["A", "B", "C", "D"]
})

target = pd.DataFrame({
    "order_id": ["A", "B", "C", "E"]
})
```

Write pandas code using:

```python
merge(..., how="outer", indicator=True)
```

to identify:

- source-only records;
- target-only records;
- records present on both sides.

---

## Question 19 — Audit Table Design

Design a minimal SQL table for reconciliation audits.

Include at least:

- `run_id`
- dataset name
- source count
- target count
- difference
- status
- timestamp

Then explain the purpose of each field.

---

## Question 20 — Late-Arriving Data

At 10:00:

```text
source = 1,000,000
target = 980,000
```

At 11:30:

```text
source = 1,000,000
target = 1,000,000
```

The pipeline has a documented two-hour reconciliation grace period.

Answer:

1. Should the 10:00 mismatch immediately be classified as permanent data loss?
2. What state should the reconciliation have?
3. What should happen after the grace period?
4. Why are event time, ingestion time, and processing time important?

---

# 3. Hard Questions

## Question 21 — Equal Counts With Substitution

Source:

```text
order_id | amount
---------+-------
A        | 100
B        | 200
C        | 300
D        | 400
```

Target:

```text
order_id | amount
---------+-------
A        | 100
B        | 200
C        | 999
D        | 400
```

The row counts and key sets match.

Design a reconciliation strategy that detects the corrupted amount.

Your answer should include at least two possible techniques.

---

## Question 22 — Equal Counts With Duplicate and Missing Record

Source:

```text
A
B
C
D
```

Target:

```text
A
B
C
C
```

Both contain four rows.

Determine:

1. whether count reconciliation passes;
2. whether key-set reconciliation passes;
3. what duplicate check reveals;
4. which source record is missing;
5. why multiple reconciliation layers are required.

---

## Question 23 — Canonical Row Hash

Design a deterministic SHA-256 row-hashing function for:

```text
order_id
amount
status
```

Your design must define:

- field order;
- NULL representation;
- string normalization;
- monetary formatting;
- encoding.

Explain why canonicalization matters before hashing.

---

## Question 24 — Batch Hash

You have these deterministic row hashes:

```text
hash_A
hash_B
hash_C
hash_D
```

Design a batch-level hashing strategy that is insensitive to row ordering.

Explain why simply concatenating rows in arbitrary arrival order can create false mismatches.

---

## Question 25 — Snapshot Consistency

A source database is continuously receiving new orders.

At 12:00:

```text
source query begins
```

At 12:02:

```text
500 new orders arrive
```

The target was loaded from a source snapshot taken at 11:59.

A reconciliation compares the current source count with the target count.

Explain why this may produce a false failure.

Design a better reconciliation approach.

---

## Question 26 — API Pagination Failure

An API reports:

```text
total_records = 100,000
```

Your extraction process receives:

```text
pages_requested = 1,000
pages_received = 990
records_received = 99,000
```

Answer:

1. What is the immediate evidence?
2. What failure mode does this suggest?
3. Which audit fields should be retained?
4. What recovery action would you consider?
5. How could the pipeline prevent silent page loss?

---

## Question 27 — Replay Duplication

A pipeline processes:

```text
batch_id = batch-2026-09-30-001
```

The target load fails after writing 70% of the data.

The orchestrator retries the entire batch.

The target now contains duplicate records.

Explain:

1. why the retry was unsafe;
2. how batch identity helps;
3. how idempotent writes could prevent the problem;
4. how reconciliation should detect the duplicate effects.

---

## Question 28 — Aggregation Reconciliation

Source data contains 10 million order-line records.

The target contains one row per:

```text
order_date + region
```

There are only 20,000 target rows.

Design reconciliation checks that are appropriate for this transformation.

Explain why comparing raw row counts is not appropriate.

---

## Question 29 — Incremental Reconciliation

A 5 TB table is partitioned by event date.

A daily pipeline processes only the previous day's partition.

Design an incremental reconciliation strategy.

Your answer should address:

- partition scope;
- source measurement;
- target measurement;
- key checks;
- aggregates;
- late-arriving records;
- audit history;
- recovery.

---

## Question 30 — Failure Diagnosis

A reconciliation reports:

```text
source_count = 10,000,000
target_count = 9,999,500
```

You discover:

```text
missing_keys = 0
unexpected_keys = 0
duplicate_keys = 0
```

But:

```text
source_amount = 500,000,000
target_amount = 499,700,000
```

Explain what this combination of evidence tells you.

List at least four possible causes and the next diagnostic checks you would perform.

---

# 4. Advanced Questions

## Question 31 — Design a Production Reconciliation Architecture

Design a reconciliation architecture for:

```text
API
 ↓
raw object storage
 ↓
staging tables
 ↓
curated warehouse
 ↓
analytics data product
```

The system processes 2 TB per day.

Your design must include:

- source audit;
- target audit;
- run IDs;
- batch IDs;
- row counts;
- partition checks;
- key checks;
- aggregate checks;
- audit storage;
- observability;
- alerting;
- recovery;
- idempotency.

Explain which checks should be cheap and which should be reserved for suspicious scopes.

---

## Question 32 — Billion-Row Reconciliation

You must reconcile a 1-billion-row dataset every day.

A full source-to-target join takes six hours and consumes significant compute.

Design a more scalable strategy.

Discuss:

- partition pruning;
- incremental reconciliation;
- metadata;
- precomputed aggregates;
- key-range reconciliation;
- sampling;
- hashes;
- targeted deep comparison;
- full reconciliation frequency.

Explain the trade-offs.

---

## Question 33 — Streaming Reconciliation

Design reconciliation for a streaming system:

```text
producer
   ↓
event stream
   ↓
consumer
   ↓
warehouse
```

Events contain stable event IDs.

The producer emits:

```text
1,000,000 events/hour
```

The consumer may temporarily lag.

Your design must distinguish:

```text
temporary lag
```

from:

```text
permanent data loss
```

Discuss:

- offsets;
- committed offsets;
- event IDs;
- windows;
- watermarks;
- late events;
- duplicate events;
- finalization;
- alerting.

---

## Question 34 — Transformation-Aware Quality Contract

Design a reconciliation contract for:

```text
raw orders
   ↓
remove cancelled orders
   ↓
deduplicate order_id
   ↓
aggregate by date and region
   ↓
daily revenue table
```

The source has:

```text
10,000,000 rows
```

The final table has:

```text
50,000 rows
```

Define what should be reconciled at each stage.

Your answer should avoid the incorrect assumption that every stage must have the same row count.

---

## Question 35 — Financial Reconciliation

Design a production reconciliation system for payments.

Requirements:

- no silent monetary loss;
- duplicate transactions must be detected;
- refunds and reversals exist;
- multiple currencies exist;
- late transactions exist;
- source and target are not queried at exactly the same instant.

Define:

1. identifiers;
2. monetary arithmetic;
3. snapshot strategy;
4. aggregate checks;
5. transaction-level checks;
6. tolerance rules;
7. late-data policy;
8. recovery process;
9. audit evidence;
10. alert severity.

---

## Question 36 — Reconciliation Audit Schema

Design a production-grade audit table that supports historical analysis.

Include fields for:

- pipeline;
- dataset;
- source system;
- target system;
- run ID;
- batch ID;
- source snapshot;
- target snapshot;
- partition;
- source metrics;
- target metrics;
- differences;
- rule version;
- status;
- severity;
- timestamps;
- remediation state.

Explain how your schema supports incident investigation.

---

## Question 37 — Defect Injection Test Plan

Design a defect-injection test suite for a reconciliation engine.

You must intentionally introduce:

1. missing records;
2. unexpected records;
3. duplicates;
4. equal-count substitutions;
5. wrong partitions;
6. aggregate corruption;
7. API page loss;
8. duplicate batch replay;
9. late-arriving records;
10. legitimate filtering.

For each defect, specify:

- injected defect;
- expected detection layer;
- expected result;
- recovery strategy.

---

## Question 38 — Debug a Production Incident

A critical pipeline reports:

```text
RECONCILIATION FAILED

source_count = 50,000,000
target_count = 49,998,000
difference = -2,000
```

Initial investigation shows:

```text
global count mismatch = 2,000
```

Further analysis shows:

```text
2026-09-30 partition:
source = 10,000,000
target = 9,998,000
```

All other partitions match.

The affected partition contains late-arriving events.

Design the complete debugging workflow.

Your answer should cover:

- verification of the reconciliation query;
- snapshot validation;
- partition analysis;
- late-data investigation;
- watermark/grace period;
- key comparison;
- recovery;
- final reconciliation;
- audit closure.

---

## Question 39 — Design a Layered Reconciliation Strategy

Create a layered strategy for a high-risk dataset.

Your layers should progress from cheapest to most expensive.

For example:

```text
Layer 1
?
 ↓
Layer 2
?
 ↓
Layer 3
?
 ↓
Layer 4
?
 ↓
Layer 5
?
```

Define:

1. what each layer checks;
2. why it exists;
3. when it should run;
4. what failure triggers the next layer;
5. how the final result is classified.

Explain how this design controls compute cost without sacrificing important assurance.

---

## Question 40 — End-to-End Production Design Challenge

You are responsible for a production pipeline:

```text
External API
    ↓
Python extraction
    ↓
JSON landing
    ↓
Parquet raw layer
    ↓
staging database
    ↓
curated warehouse
    ↓
analytics data product
```

The source provides:

```text
API total count
pagination tokens
batch ID
updated_at
stable record ID
```

The business considers the dataset critical.

The system experiences:

- late-arriving records;
- API retries;
- occasional duplicate pages;
- schema evolution;
- partial file arrival;
- warehouse load retries;
- transformations that filter and aggregate records.

Design a complete production reconciliation system.

Your answer must cover:

### A. Source-side evidence

What should be captured from the API?

### B. Landing reconciliation

How do you reconcile API responses against landed records?

### C. File reconciliation

How do you verify files and partitions?

### D. Database reconciliation

How do you reconcile staging against raw data?

### E. Transformation reconciliation

How do you validate filters, deduplication, and aggregation?

### F. Warehouse reconciliation

What row, key, partition, and aggregate checks are required?

### G. Late data

How do you distinguish provisional from final reconciliation?

### H. Idempotency

How do you prevent retries from creating duplicate effects?

### I. Audit trail

What evidence should remain permanently?

### J. Observability

What metrics and alerts should be emitted?

### K. Recovery

What happens when a reconciliation fails?

### L. Scale

How would your design change if the dataset grows from:

```text
10 million records/day
```

to:

```text
1 billion records/day
```

### M. Testing

How would you prove that the reconciliation system itself is correct?

---

# 5. Practical Coding Exercises

## Coding Exercise 1 — Exact Count Reconciliation

Implement:

```python
def reconcile_counts(source_count: int, target_count: int) -> bool:
    ...
```

Requirements:

- reject negative counts;
- return `True` for exact equality;
- return `False` otherwise.

---

## Coding Exercise 2 — Percentage Difference

Implement:

```python
def percentage_difference(source: int, target: int) -> float:
    ...
```

Requirements:

- handle `source == 0`;
- reject negative counts;
- return a percentage;
- document the zero-baseline policy.

---

## Coding Exercise 3 — Absolute Tolerance

Implement:

```python
def within_absolute_tolerance(
    source: int,
    target: int,
    tolerance: int,
) -> bool:
    ...
```

Test:

```text
1000 vs 998, tolerance 5 → PASS
1000 vs 990, tolerance 5 → FAIL
```

---

## Coding Exercise 4 — Relative Tolerance

Implement a relative-tolerance reconciliation function.

Test:

```text
source = 1,000,000
target = 999,000
tolerance = 0.2%
```

Determine whether the result passes.

---

## Coding Exercise 5 — Missing and Unexpected Keys

Given two Python lists of IDs:

```python
source_ids = [...]
target_ids = [...]
```

return:

```python
missing_ids
unexpected_ids
```

Also detect duplicate IDs on either side.

---

## Coding Exercise 6 — pandas Full Reconciliation

Using pandas:

```python
source = pd.DataFrame(...)
target = pd.DataFrame(...)
```

produce a reconciliation DataFrame containing:

```text
order_id
reconciliation_status
```

where status is one of:

```text
source_only
target_only
both
```

---

## Coding Exercise 7 — Aggregate Reconciliation

Implement a function that compares:

```text
row count
total quantity
total amount
distinct customers
```

between source and target.

Return a structured result containing:

```text
metric
source_value
target_value
difference
status
```

---

## Coding Exercise 8 — Deterministic Row Hash

Implement a SHA-256 hash for:

```text
order_id
amount
status
```

Define explicit canonicalization rules.

Then prove that logically equivalent normalized inputs generate the same hash.

---

## Coding Exercise 9 — Partition Reconciliation

Given:

```python
source_counts = {
    "2026-09-28": 1000,
    "2026-09-29": 1200,
    "2026-09-30": 1100,
}

target_counts = {
    "2026-09-28": 1000,
    "2026-09-29": 1190,
    "2026-09-30": 1100,
}
```

produce a partition-level reconciliation report.

---

## Coding Exercise 10 — Audit Record

Create a Python dataclass representing a reconciliation audit result.

Include:

```text
run_id
dataset
source_count
target_count
difference
difference_pct
status
checked_at
```

Then serialize the result to JSON.

---

# 6. SQL Exercises

## SQL Exercise 1 — Count Comparison

Write one SQL statement that returns:

```text
source_count
target_count
difference
```

for two tables.

---

## SQL Exercise 2 — Missing Keys

Return source records missing from target.

---

## SQL Exercise 3 — Unexpected Keys

Return target records missing from source.

---

## SQL Exercise 4 — Duplicate Keys

Return all duplicate business keys and their occurrence counts.

---

## SQL Exercise 5 — Aggregate Comparison

Return:

```text
COUNT(*)
SUM(amount)
COUNT(DISTINCT customer_id)
MIN(order_timestamp)
MAX(order_timestamp)
```

for a dataset.

---

## SQL Exercise 6 — Partition Comparison

Compare source and target counts by:

```text
order_date
```

and return only mismatching partitions.

---

## SQL Exercise 7 — Field-Level Comparison

Join source and target by `order_id` and identify records where:

```text
amount
```

differs.

Handle NULLs correctly.

---

## SQL Exercise 8 — Reconciliation Status

Write SQL that classifies a count comparison as:

```text
PASS
WARNING
FAIL
```

using a documented percentage tolerance.

---

## SQL Exercise 9 — Audit Insert

Write an `INSERT` statement that records a reconciliation result in an audit table.

---

## SQL Exercise 10 — Historical Failure Analysis

Given a reconciliation audit table, write SQL to determine:

1. datasets with the most failures;
2. average difference percentage;
3. latest failure per dataset;
4. number of unresolved failures.

---

# 7. Debugging Exercises

## Debugging Exercise 1

A reconciliation reports:

```text
source = 100,000
target = 99,999
```

but the engineer claims the data is complete.

What evidence would you request before accepting that conclusion?

---

## Debugging Exercise 2

Global counts match, but a dashboard shows revenue is lower than expected.

What reconciliation layers would you run next?

---

## Debugging Exercise 3

Counts differ only during the first 30 minutes after ingestion.

What timing-related causes should you investigate?

---

## Debugging Exercise 4

A reconciliation suddenly reports 20% more target rows.

What duplicate/replay causes should you investigate?

---

## Debugging Exercise 5

A full outer join produces millions of rows even though each table has one million records.

What could be wrong with the join key or data grain?

---

## Debugging Exercise 6

A hash comparison fails even though users claim the values are equivalent.

What canonicalization issues could cause the mismatch?

---

## Debugging Exercise 7

A partition-level check fails but global counts pass.

Explain how this can happen.

---

## Debugging Exercise 8

An API extraction has:

```text
API total = 500,000
received = 500,000
```

but downstream data has only 450,000 rows.

List the next five checks you would perform.

---

## Debugging Exercise 9

A replayed batch passes count reconciliation but creates duplicate business records.

Which controls are missing?

---

## Debugging Exercise 10

A reconciliation fails every Monday but passes Tuesday through Sunday.

Design an investigation plan that looks for systematic causes rather than repeatedly increasing the tolerance.

---

# 8. Review and Self-Assessment

Before considering this practice set complete, you should be able to answer the following without notes:

- Why are row counts useful?
- Why are row counts insufficient?
- How do you identify missing records?
- How do you identify unexpected records?
- How do you detect duplicates?
- Why are stable keys important?
- How do you reconcile aggregates?
- Why does partition-level reconciliation matter?
- What is deterministic hashing?
- Why is canonicalization necessary?
- What belongs in an audit table?
- How do absolute and relative tolerances differ?
- Why can a zero source count be special?
- How do late-arriving records affect reconciliation?
- What is a watermark?
- How do retries create duplicate effects?
- What does idempotency mean?
- What is incremental reconciliation?
- How does CDC support reconciliation?
- How should transformations affect expected row counts?
- How do you reconcile aggregated datasets?
- How do you reconcile APIs?
- How do you reconcile files?
- How do you reconcile databases?
- How do you reconcile streaming systems?
- How do you control reconciliation cost at scale?
- What should happen after a reconciliation failure?
- Why should audit history be retained?
- How do you prove that the reconciliation system itself works?

---

# 9. Final Challenge

Without looking at the earlier sections, design a reconciliation solution for this pipeline:

```text
PostgreSQL source
      ↓
Python extraction
      ↓
Parquet raw layer
      ↓
Python/Pandas transformation
      ↓
PostgreSQL staging
      ↓
Warehouse
```

The source contains:

```text
100 million records/day
```

The pipeline:

- filters invalid records;
- quarantines malformed records;
- deduplicates by business key;
- aggregates some datasets;
- receives late-arriving updates;
- retries failed loads;
- partitions data by event date.

Your design must answer:

1. What do you measure at the source?
2. What do you measure after extraction?
3. How do you reconcile files?
4. How do you reconcile staging?
5. How do you reconcile transformed data?
6. How do you account for quarantined records?
7. How do you account for deduplicated records?
8. How do you reconcile aggregated datasets?
9. How do you handle late-arriving records?
10. How do you detect duplicate replays?
11. How do you choose tolerances?
12. What belongs in the audit table?
13. What metrics do you expose?
14. What alerts do you create?
15. What blocks publication?
16. What recovery actions are available?
17. How do you make the system idempotent?
18. How do you scale reconciliation without scanning everything?
19. How do you test the system with injected defects?
20. How do you prove the final published data is trustworthy?

---

# 10. Expected Learning Outcome

After completing these exercises, you should be able to move beyond:

```text
"COUNT(*) matches."
```

and reason in terms of:

```text
source evidence
    ↓
expected transformation
    ↓
target evidence
    ↓
count reconciliation
    ↓
partition reconciliation
    ↓
key reconciliation
    ↓
duplicate detection
    ↓
aggregate reconciliation
    ↓
hash/field reconciliation
    ↓
timing and watermark semantics
    ↓
audit evidence
    ↓
decision
    ↓
recovery
```

The goal is not merely to detect that two datasets differ.

The goal is to determine:

> **What should have happened, what actually happened, whether the difference is expected, how confident we are in the result, and what the production system should do next.**
