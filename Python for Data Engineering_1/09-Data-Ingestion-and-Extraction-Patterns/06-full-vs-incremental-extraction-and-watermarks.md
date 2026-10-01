# Full vs Incremental Extraction and Watermarks

> **Module:** Data Ingestion and Extraction Patterns  
> **Topic:** Full vs Incremental Extraction and Watermarks  
> **Audience:** Complete beginner progressing toward production-ready Data Engineer  
> **Python:** 3.12+  
> **Scope:** Extraction strategy, state, correctness, recovery, backfills, reconciliation, and production design

Extraction is not finished when a source returns HTTP 200 or a SQL query succeeds. A production pipeline must also answer a harder question:

> **What data should I extract on this run, and how can I prove that I did not miss or corrupt anything?**

The two foundational strategies are **full extraction** and **incremental extraction**. Full extraction asks the source for the complete current state. Incremental extraction asks for the changes since a previously known point.

The important engineering decision is not “incremental is better” or “full is better.” The right strategy depends on **volume, change rate, delete behavior, source capabilities, watermark reliability, freshness requirements, cost, and operational complexity**.

This chapter develops that reasoning from first principles and then turns it into a production-oriented design.

---

# 1. Learning Objectives

By the end of this chapter, you should be able to:

- Explain full extraction.
- Explain incremental extraction.
- Explain watermarks and high-water marks.
- Choose a reasonable watermark column or progress marker.
- Design durable extraction state.
- Distinguish append-only extraction from changed-record extraction.
- Understand downstream append and upsert semantics.
- Use `MERGE`/upsert concepts for changed records.
- Analyze inclusive and exclusive extraction boundaries.
- Handle identical timestamps.
- Design a lookback window.
- Explain late commits and long-running transactions.
- Explain clock-skew risks.
- Account for timestamp precision.
- Advance state only after durable landing/commit.
- Make reruns safe through idempotency and deduplication.
- Explain why timestamp-based extraction cannot naturally see hard deletes.
- Design soft-delete handling or periodic full-key reconciliation.
- Understand when CDC should be evaluated for delete/change capture.
- Design historical backfills.
- Make backfills idempotent.
- Define first-run and empty-window behavior.
- Compare full, incremental, and hybrid strategies.
- Connect extraction design to freshness SLAs.
- Instrument extraction runs with useful metadata.
- Debug missed records, duplicates, stale deletes, and state errors.
- Reason about crash recovery.
- Defend an extraction strategy during a production architecture review.

---

# 2. Prerequisites

This topic assumes you already have a basic understanding of:

- HTTP/API extraction.
- API pagination.
- Retries.
- Idempotency.
- SQL basics.
- Database extraction.
- `MERGE`/upsert concepts.
- Metadata/state tables.
- Bronze/raw landing.
- Freshness SLAs.

These topics were covered earlier in the learning sequence. They are only briefly revisited here when they are necessary to reason about extraction state.

---

# 3. The Core Question: What Should We Extract?

Imagine a customer table:

```text
id | name  | updated_at
---|-------|-------------------
1  | Alice | 2026-09-01 10:00
2  | Bob   | 2026-09-01 10:05
3  | Carol | 2026-09-01 10:10
```

Suppose the pipeline runs every hour.

A beginner might ask:

> “How do I query the customers?”

A production Data Engineer asks:

> “Which customers need to be extracted during this run, and what evidence tells me that the boundary is safe?”

There are two fundamental choices.

```text
FULL EXTRACTION
"Give me the complete current state."

INCREMENTAL EXTRACTION
"Give me what changed since my previous known state."
```

The second strategy introduces **state**.

That state is commonly represented by a watermark.

```text
WATERMARK
"The source-side value representing how far I have
safely extracted."
```

A watermark is not magic. It does not automatically guarantee completeness.

A watermark is safe only when:

- the source field is reliable;
- its update semantics are understood;
- boundaries are handled correctly;
- late data is accounted for;
- state advances after durable landing/commit;
- duplicates can be handled safely;
- deletes are addressed separately when necessary.

The central mental model for this chapter is:

```text
Source characteristics
       ↓
Volume
       ↓
Change rate
       ↓
Delete behavior
       ↓
Source capabilities
       ↓
Freshness requirement
       ↓
Watermark reliability
       ↓
Extraction strategy
       ↓
State management
       ↓
Completeness validation
       ↓
Idempotency
       ↓
Backfill / recovery strategy
```

---

# 4. Full Extraction

## 4.1 Simple Explanation

Full extraction reads the complete current dataset on every run.

Conceptually:

```python
rows = extract_all_customers()
```

SQL:

```sql
SELECT *
FROM customers;
```

The source is not asked “what changed since the last run?” It is asked:

> “What is the complete state right now?”

## 4.2 Real-World Analogy

Imagine counting all books in a library every evening.

You do not need to remember yesterday's count. You walk through the entire library and count every book again.

That is simple and easy to verify, but expensive for a very large library.

## 4.3 Advantages

Full extraction can provide:

- Simple implementation.
- Simple recovery.
- Easy reconciliation.
- Natural detection of hard deletes when the complete source state is available.
- A straightforward first run.
- A complete snapshot that can serve as an audit point.

## 4.4 Disadvantages

Full extraction can cause:

- Repeated source reads.
- Higher source load.
- Higher network transfer.
- Higher processing cost.
- Longer runtimes.
- Higher storage churn.
- Poor scalability for very large datasets.

## 4.5 When Full Extraction Is Reasonable

Full extraction can be a sound engineering choice for:

- Small reference tables.
- Low-cost APIs.
- Configuration/reference data.
- Daily snapshots.
- Low-change datasets.
- Sources without reliable change tracking.
- Workloads where simplicity and reconciliation are more valuable than incremental complexity.

“Small enough to extract fully” is not a universal row-count threshold.

It is a business and operational decision.

A 50-million-row table might be reasonable to extract fully in one environment and completely unreasonable in another.

---

# 5. Incremental Extraction

## 5.1 Simple Explanation

Incremental extraction retrieves records that are new or changed since the previous extraction state.

For a timestamp watermark:

```sql
SELECT *
FROM customers
WHERE updated_at > :watermark;
```

Instead of repeatedly reading the complete table, the extractor reads the relevant change window.

This can reduce:

- Source load.
- Network transfer.
- Processing.
- Runtime.
- Freshness latency.
- Cost.

But the simplicity of the query hides a difficult problem:

> **How do we know that the watermark and its boundary are correct?**

That is where production engineering begins.

---

# 6. Full vs Incremental Example

Suppose:

```text
Run 1
------
1 Alice
2 Bob
3 Carol
```

Before Run 2:

```text
4 David added
2 Bob updated
```

A full extraction returns:

```text
Run 2:
1
2
3
4
```

An incremental extraction might return:

```text
Run 2:
2
4
```

The downstream system must understand what those records mean.

For an append-only dataset:

```text
new record → append
```

For a mutable entity table:

```text
changed record
      ↓
   upsert
      ↓
target current state
```

Incremental extraction therefore has two separate questions:

1. **Which source records should be extracted?**
2. **What should the target do with those records?**

Do not confuse extraction semantics with target-write semantics.

---

# 7. Two Main Incremental Patterns

## 7.1 Pattern A — Append-Only Incremental Extraction

Examples:

- Events.
- Logs.
- Immutable transactions.
- Audit records.

If records never change after creation, the extractor can often use a creation timestamp or sequence:

```sql
SELECT *
FROM events
WHERE created_at > :watermark;
```

The target operation may simply be:

```text
new rows → append
```

### Failure Scenario

If the source is assumed to be append-only but records can actually be edited, an append-only target can silently accumulate stale versions.

### Production Rule

Verify the source's immutability guarantee. Do not infer it from table names or application behavior.

## 7.2 Pattern B — Changed-Record Incremental Extraction

Examples:

- Customers.
- Orders.
- Products.

The source returns records that changed:

```text
changed rows
     ↓
upsert / MERGE
     ↓
target state
```

For example:

```sql
MERGE INTO target_customers AS target
USING staged_customers AS source
ON target.id = source.id
WHEN MATCHED THEN
    UPDATE SET
        name = source.name,
        updated_at = source.updated_at
WHEN NOT MATCHED THEN
    INSERT (id, name, updated_at)
    VALUES (source.id, source.name, source.updated_at);
```

> **Dialect note:** `MERGE` syntax varies across PostgreSQL versions, DuckDB, warehouses, and other databases. Treat the example as a conceptual SQL pattern unless adapted to your target dialect.

---

# 8. Watermarks

A watermark is a progress marker representing how far an extractor has **safely processed** the source according to its extraction rule.

Examples include:

```text
updated_at
created_at
id
sequence_number
LSN
cursor
```

This chapter focuses primarily on timestamp- and ID-based extraction.

The basic lifecycle is:

```text
Source
  ↓
Extract records
  ↓
Land data
  ↓
Validate / commit
  ↓
Advance watermark
```

Notice what is deliberately absent:

```text
Extract
  ↓
Advance watermark
  ↓
Maybe write data
```

That ordering is unsafe.

---

# 9. High-Water Mark

Suppose the state store contains:

```text
watermark = 2026-09-01T10:00:00Z
```

The intended meaning is:

> The pipeline has safely processed data up to this point according to the extraction rule and state semantics.

This is a **state statement**, not merely a query parameter.

A useful way to think about it is:

```text
watermark = committed progress
```

not:

```text
watermark = last value the extractor happened to observe
```

That distinction becomes critical during failures.

---

# 10. Watermark State Table

A simple state table might be:

```sql
CREATE TABLE watermarks (
    pipeline_name TEXT PRIMARY KEY,
    watermark_value TIMESTAMP,
    updated_at TIMESTAMP NOT NULL
);
```

### Column meanings

| Column | Purpose |
|---|---|
| `pipeline_name` | Identifies the extraction state |
| `watermark_value` | Last safely committed progress value |
| `updated_at` | Records when state itself was updated |

In a production system, state often contains more information, for example:

```text
pipeline_name
source_name
watermark_type
watermark_value
watermark_id
last_run_id
updated_at
status
```

A composite watermark may require multiple state fields.

---

# 11. Why State Must Exist Outside the Extractor Process

### BAD EXAMPLE

```python
# BAD EXAMPLE
watermark = "2026-09-01T10:00:00Z"
```

This variable disappears when the process exits.

A crash can erase the extractor's knowledge of progress.

A production pipeline needs durable state:

```text
Extractor
   ↓
Metadata database / durable state store
   ↓
watermark
```

The exact state store can vary. The important property is durability and controlled update semantics.

---

# 12. Choosing a Watermark Column

A good watermark should ideally be:

- Reliably updated when relevant data changes.
- Available in source queries.
- Efficiently filterable.
- Indexed where appropriate.
- Sufficiently ordered or monotonic.
- Precise enough for the source's change rate.
- Stable.
- Governed by an understood contract.

Common candidates:

```text
updated_at
created_at
id
sequence
version
```

But these are not automatically safe.

### `created_at`

Useful for append-only data.

Usually insufficient for mutable records because an update may not change `created_at`.

### `updated_at`

Potentially useful for mutable records.

But only if the source reliably updates it for every relevant change.

### ID

Useful when IDs are generated monotonically and the dataset is append-only.

An ID is generally not a substitute for change tracking when existing records can be modified.

### Sequence / Version

Often strong progress markers when the source explicitly guarantees ordering.

The source contract matters more than the column name.

---

# 13. Why `updated_at` Is Not Automatically Safe

Suppose:

```text
Customer 1
updated_at = 10:00

Customer 2
updated_at = 10:05
```

Later:

```text
Customer 3 changes
but updated_at remains 09:50
```

If the extractor has already advanced beyond 09:50, the changed Customer 3 can be missed indefinitely.

The key lesson:

> **A watermark column is only as reliable as the source system's guarantee about it.**

Before production use, determine:

- Who writes the field?
- Is it updated for every mutation?
- Is it generated by the database or application?
- Is it transaction commit time or application event time?
- What precision does it have?
- What timezone does it use?
- Can old timestamps be written?
- Can updates occur without changing it?

---

# 14. Indexed Watermarks

A reliable watermark can still be operationally expensive if the source cannot filter on it efficiently.

For a relational database:

```sql
CREATE INDEX idx_customers_updated_at
ON customers(updated_at);
```

Conceptually:

```text
Without useful index
→ source may scan a huge table

With useful index
→ source may locate changed rows efficiently
```

An index improves query performance.

It does **not** make an unreliable watermark reliable.

Those are separate concerns:

```text
Correctness:
Is the watermark complete and trustworthy?

Performance:
Can the source find the rows efficiently?
```

---

# 15. Monotonicity

A progress marker is easier to reason about when it is monotonic or sufficiently ordered.

Example:

```text
10
20
30
40
```

Progress moves forward.

A problematic pattern might be:

```text
10
30
20
40
```

This does not necessarily make extraction impossible, but it means a simple “last observed value” may not represent a safe boundary.

Possible progress markers include:

- Monotonically increasing sequences.
- Commit positions.
- Carefully governed timestamps.
- Composite `(timestamp, id)` positions.

Always verify source guarantees.

---

# 16. Inclusive vs Exclusive Boundaries

Compare:

```sql
WHERE updated_at > :watermark
```

with:

```sql
WHERE updated_at >= :watermark
```

Suppose:

```text
watermark = 10:00:00
```

Records:

```text
A → 09:59:59
B → 10:00:00
C → 10:00:00
D → 10:00:01
```

### Exclusive boundary

```sql
WHERE updated_at > '10:00:00'
```

Returns:

```text
D
```

It excludes B and C.

### Inclusive boundary

```sql
WHERE updated_at >= '10:00:00'
```

Returns:

```text
B
C
D
```

It may intentionally re-read records already processed.

That can be safe when the downstream is idempotent.

### The core trade-off

```text
>
↓
less overlap
greater boundary-loss risk

>=
↓
more overlap
greater duplicate-processing risk
```

Neither operator is universally correct.

The correct choice depends on:

- How state is defined.
- Timestamp precision.
- Source guarantees.
- Whether the target can deduplicate.
- Whether a lookback is used.
- Whether a composite progress marker is used.

---

# 17. Identical Timestamps

Suppose:

```text
A → 10:00:00
B → 10:00:00
C → 10:00:00
```

If the watermark is only:

```text
10:00:00
```

then a naïve next query can struggle to distinguish which records were actually processed.

Strategies include:

- Overlap/lookback.
- `(timestamp, id)` composite progress.
- Deduplication.
- Source sequence/version.
- Higher timestamp precision.

### Composite example

```sql
WHERE
    updated_at > :timestamp
OR (
    updated_at = :timestamp
    AND id > :id
)
ORDER BY updated_at, id;
```

This requires an ordering contract and suitable query/index support.

It is not universally correct merely because it looks precise.

---

# 18. The Lookback Window

A common production pattern is:

```text
previous watermark
       ↓
move backward by safety interval
       ↓
re-read overlap
       ↓
deduplicate
       ↓
validate
       ↓
advance state
```

Example:

```text
watermark = 10:00
lookback = 30 minutes

effective extraction start = 09:30
```

The extractor intentionally re-reads some records.

This protects against:

- Late commits.
- Clock skew.
- Transaction delays.
- Timestamp precision problems.
- API timestamp truncation.

Lookback is a **correctness mechanism** only when paired with safe duplicate handling.

---

# 19. Late Commit Problem

Consider this timeline:

```text
09:59 — transaction starts
10:00 — extractor runs
10:01 — extractor advances watermark
10:05 — transaction commits
```

Suppose the record's relevant timestamp is not visible to the extractor until commit.

A naïve extraction that moves directly from 10:00 onward may miss the record.

A lookback can cause the next run to revisit the earlier window:

```text
next run
effective start = 09:30
```

The late record can then be discovered.

This works only if the target can safely process overlap.

---

# 20. Clock Skew

Different systems may have different clocks:

```text
Application server clock
        ≠
Database server clock
        ≠
Extractor clock
```

For example, the extractor may calculate a cutoff using its local clock while the source assigns timestamps using another clock.

UTC normalization helps prevent timezone confusion, but:

> **UTC does not magically eliminate clock skew.**

The stronger design is to use source-generated progress markers where possible and to treat timestamp semantics as part of the source contract.

---

# 21. Long-Running Transactions

A source transaction may behave like:

```text
transaction starts
       ↓
long processing
       ↓
commit later
```

The extractor may run during the transaction and therefore observe a database state that does not yet contain the final committed record.

Again, a safety window can help:

```text
previous watermark
       ↓
lookback
       ↓
re-read potentially late records
```

But lookback is not a substitute for understanding source transaction semantics.

---

# 22. Safe Watermark Advancement

This is one of the most important rules in incremental extraction.

## WRONG

```text
extract
   ↓
advance watermark
   ↓
write data
```

Suppose the process crashes after the state update:

```text
watermark says "done"
data says "not saved"
```

The next run may skip those records permanently.

## RIGHT

```text
extract
   ↓
land data durably
   ↓
validate
   ↓
commit data
   ↓
advance watermark
```

The watermark should represent **committed progress**, not attempted progress.

---

# 23. Crash-Recovery Timeline

Consider:

```text
Run starts
   ↓
Read watermark
   ↓
Extract
   ↓
Land records
   ↓
CRASH
```

If the watermark was not advanced, the next run can re-read the same range.

That is safe when the pipeline is idempotent:

```text
same input
    +
same processing
    ↓
same target state
```

This is one reason overlap and reprocessing are often preferable to attempting fragile exactly-once behavior across independent systems.

---

# 24. Atomicity Between Data and State

The system wants these two operations to behave consistently:

```text
Data write
+
Watermark update
```

If the target and metadata state live in the same transactional database, they may be committed together:

```text
BEGIN
  write target
  update watermark
COMMIT
```

But many pipelines look more like:

```text
Source database
       ↓
Object storage
       ↓
Target warehouse
       ↓
Metadata database
```

These systems generally do not share one distributed transaction.

Realistic patterns include:

- Same-database transaction where possible.
- Staging + commit.
- Durable raw landing before state advancement.
- Metadata state tied to immutable run IDs.
- Idempotent reprocessing.
- Explicit recovery logic.

Do not pretend that one universal transaction can atomically span arbitrary source, object-storage, warehouse, and metadata systems.

---

# 25. Deduplication

Lookback intentionally creates overlap.

Example:

```text
Run 1:
10:00 → 10:30

Run 2:
10:15 → 11:00
```

The range:

```text
10:15 → 10:30
```

can appear twice.

This is expected.

Deduplication can use a stable source primary key:

```text
primary key
```

or, when historical versions matter:

```text
(id, updated_at)
```

The correct deduplication key depends on the target model.

For a current-state customer table:

```text
id
```

may be the target identity.

For versioned history:

```text
(id, updated_at)
```

may distinguish versions.

Do not deduplicate blindly on every field. Define the identity of a record first.

---

# 26. Deletes — The Major Limitation

Consider:

```text
Source:
1 Alice
2 Bob
3 Carol
```

Then Bob is hard-deleted:

```text
Source:
1 Alice
3 Carol
```

A timestamp query such as:

```sql
SELECT *
FROM customers
WHERE updated_at > :watermark;
```

cannot naturally return Bob.

Why?

Because Bob no longer exists to be returned.

The key principle is:

> **Timestamp-based incremental extraction observes surviving rows, not disappeared rows.**

This is one of the most important limitations of ordinary watermark extraction.

---

# 27. Delete Handling Strategies

## Strategy 1 — Soft Deletes

The source keeps a record and marks it:

```text
deleted_at
is_deleted
```

Then the incremental filter can capture the change.

Example:

```sql
SELECT *
FROM customers
WHERE updated_at > :watermark;
```

A target can then apply:

```text
is_deleted = true
```

## Strategy 2 — Periodic Full-Key Reconciliation

Compare source keys with target keys:

```text
source IDs
    vs
target IDs
```

If a target-only ID is no longer present in the source, it may represent a delete.

## Strategy 3 — CDC

Change Data Capture can expose delete events directly.

CDC is introduced here only because it solves an important limitation of timestamp-based extraction. Detailed PostgreSQL WAL, logical decoding, replication slots, publications, snapshots, and streaming belong to the dedicated CDC topic.

---

# 28. Full-Key Reconciliation

Suppose:

```text
Source:
1
2
3
```

Target:

```text
1
2
3
4
```

Then:

```text
target-only ID = 4
```

This is evidence that ID 4 may have been deleted from the source.

Conceptually:

```sql
SELECT id FROM target
EXCEPT
SELECT id FROM source;
```

> **Dialect note:** `EXCEPT` availability and syntax are database-specific, but the set-difference idea is broadly applicable.

At scale, full-key reconciliation may itself be expensive.

Possible controls include:

- Running less frequently.
- Partitioning the reconciliation.
- Comparing key hashes or summaries.
- Reconciling by date or business partition where appropriate.
- Using source APIs that provide totals or snapshots.
- Evaluating CDC when delete correctness is critical.

---

# 29. Backfills

A backfill means re-extracting historical data for a defined period or range.

Typical reasons:

- A pipeline bug was fixed.
- The source was temporarily unavailable.
- Records were missed.
- A schema issue was corrected.
- Historical source data was corrected.
- A new downstream dataset requires historical population.

Example:

```text
2026-01-01 → 2026-01-31
```

A backfill is an extraction operation, not merely a rerun button.

It needs:

- Defined boundaries.
- Bounded windows.
- Idempotent landing.
- Progress tracking.
- Validation.
- Recovery behavior.

---

# 30. Backfill Windows

Instead of extracting an entire month in one huge request:

```text
2026-01-01 → 2026-01-31
```

break it into windows:

```text
01–02
02–03
03–04
...
30–31
31–Feb 1
```

Smaller windows can provide:

- Bounded memory.
- Easier retries.
- Reduced source pressure.
- Easier monitoring.
- Easier recovery.
- More precise failure isolation.

Window size should be derived from source behavior and operational limits, not copied from an arbitrary “best practice.”

---

# 31. Idempotent Backfills

Running:

```text
January backfill
```

twice should not create unintended duplicates.

Possible strategies include:

- Deterministic partition replacement.
- Primary-key upsert.
- `MERGE`.
- Stable run/window identifiers.
- Deduplication.
- Write-to-staging then commit.

The desired property is:

```text
same historical input
        +
same processing
        ↓
same intended target state
```

---

# 32. Implementing a Backfill Function

A simplified Python design:

```python
from collections.abc import Iterator
from datetime import datetime, timedelta


def generate_windows(
    start: datetime,
    end: datetime,
    *,
    window: timedelta = timedelta(days=1),
) -> Iterator[tuple[datetime, datetime]]:
    if end <= start:
        return

    current = start
    while current < end:
        next_boundary = min(current + window, end)
        yield current, next_boundary
        current = next_boundary


def backfill(
    start: datetime,
    end: datetime,
    *,
    window: timedelta = timedelta(days=1),
) -> None:
    for window_start, window_end in generate_windows(
        start,
        end,
        window=window,
    ):
        # 1. Extract source data for this historical window.
        # 2. Land the raw result durably.
        # 3. Validate the landing.
        # 4. Apply idempotent target logic.
        # 5. Record progress and metrics.
        # 6. Retry only the failed window when appropriate.
        print(window_start, window_end)
```

The important architecture is not the loop itself:

```text
window
  ↓
extract
  ↓
land
  ↓
validate
  ↓
commit
  ↓
record progress
```

---

# 33. First-Ever Run

What happens when there is no watermark?

This must be explicit.

Possible strategies:

```text
No watermark
   ↓
Full extraction
```

or:

```text
No watermark
   ↓
Configured initial historical window
```

or:

```text
No watermark
   ↓
Source-defined starting cursor/sequence
```

Do not silently invent a first-run boundary.

The initial extraction policy should be documented as part of the pipeline's operational contract.

---

# 34. Empty Windows

Suppose the source has no changes:

```text
No records changed today.
```

An empty result is not necessarily an error.

The pipeline should distinguish:

```text
0 records returned
```

from:

```text
request/query failed
```

Whether the watermark advances during an empty window depends on the source semantics and how the next boundary is defined.

For example, if the watermark represents a source-observed cutoff rather than the maximum record timestamp, an empty successful extraction may still advance state.

The rule must be explicit.

---

# 35. Time Zones

Timestamps should generally be normalized to UTC for cross-system comparison:

```text
2026-09-01T10:00:00Z
```

Local timestamps introduce problems such as:

- Daylight-saving transitions.
- Ambiguous local times.
- Different source/application time zones.
- Extractor-local time assumptions.
- Inconsistent comparisons.

A good production contract states:

```text
timezone = UTC
precision = milliseconds
```

or whatever the actual source guarantees.

If the source emits local timestamps, normalize them only when the source timezone semantics are known.

---

# 36. Timestamp Precision

Precision can be:

```text
seconds
milliseconds
microseconds
nanoseconds
```

Suppose the source stores:

```text
10:00:00.123456
```

but the API filter accepts only:

```text
10:00:00
```

Multiple records can share the same externally visible filter value.

This can create gaps if boundaries are too precise for the API's actual semantics.

A lookback and deduplication strategy can compensate for coarse filtering when source behavior permits it.

---

# 37. APIs That Truncate Filters

Suppose an API accepts:

```text
updated_since=10:00:00
```

but internally has:

```text
10:00:00.100
10:00:00.500
10:00:00.900
```

If the next request starts at:

```text
10:00:01
```

those records may be skipped depending on the API's filter semantics.

A safer pattern can be:

```text
previous progress
      ↓
subtract safety interval
      ↓
API updated_since
      ↓
deduplicate
```

The exact safety interval must come from source behavior and freshness/cost requirements.

---

# 38. Choosing Between Full and Incremental

Use a workload-based decision framework.

| Factor | Question |
|---|---|
| Volume | How much data exists? |
| Change rate | How much changes per run? |
| Delete behavior | Can deletes be observed? |
| Watermark quality | Is there a reliable change marker? |
| Source capability | Can the source filter efficiently? |
| Indexing | Can the source execute incremental queries efficiently? |
| Freshness | How quickly must data arrive? |
| Cost | What is the extraction cost? |
| Complexity | Can the team operate the strategy safely? |

### Volume

Large data volumes increase the cost of repeatedly extracting unchanged records.

### Change Rate

A tiny change rate can make incremental extraction attractive when the source supports it reliably.

### Delete Behavior

If hard deletes matter and no delete signal exists, incremental extraction needs reconciliation or another mechanism.

### Watermark Quality

If no reliable progress marker exists, a full snapshot may be simpler and safer.

### Source Capability

A source may advertise `updated_since` but implement it inefficiently or with surprising timestamp semantics.

### Freshness

A strict freshness SLA can influence how often the source must be queried and how much overlap is acceptable.

### Cost

Consider source load, network, compute, storage, and operational cost.

### Complexity

An incremental design can reduce data movement while increasing correctness and operational complexity.

---

# 39. Five Source Decision Exercise

For each scenario, decide and justify:

- Full vs incremental.
- Watermark.
- Delete handling.
- Backfill approach.
- Reconciliation.
- Freshness.
- Operational complexity.

Do not choose based on a slogan. Write down the evidence.

## Source 1 — Small Reference Table

```text
Approximately a few thousand rows.
Changes are rare.
No reliable updated timestamp.
```

Questions:

1. What strategy would you consider?
2. Why?
3. What happens when a row is deleted?
4. What does recovery look like?

## Source 2 — 500-Million-Row Orders Table

```text
Very large table.
A small percentage changes daily.
Reliable updated_at exists.
updated_at is indexed.
```

Questions:

1. Why might incremental extraction be operationally attractive?
2. What must be verified before trusting `updated_at`?
3. How would you handle overlap?
4. How would you detect deletes?

## Source 3 — Append-Only Event Log

```text
Events are immutable.
A sequence number increases for every event.
```

Questions:

1. What progress marker is available?
2. Does an update-record problem exist?
3. What does the target write pattern look like?

## Source 4 — SaaS Contacts API With No Delete Signal

```text
The API supports updated_since.
Contacts can be edited.
Hard deletes are not exposed.
```

Questions:

1. What watermark would you investigate?
2. Why is incremental extraction insufficient for deletes?
3. What reconciliation could supplement it?
4. What alternative source capability would you evaluate?

## Source 5 — Daily File Drop

```text
A partner publishes one daily file.
Each file represents the full current state.
```

Questions:

1. Is “incremental” automatically necessary?
2. How would you detect a missing file?
3. How could full snapshots support delete detection?
4. How would historical backfills work?

---

# 40. Hybrid Strategies

A hybrid design can combine:

```text
Frequent incremental extraction
+
Periodic full reconciliation
```

Example:

```text
Every 15 minutes → incremental
Every Sunday     → full-key reconciliation
```

This can balance:

- Efficient daily movement.
- Completeness checks.
- Delete detection.
- Operational risk.
- Freshness requirements.

The exact frequency must come from:

- Source behavior.
- Delete tolerance.
- Business SLA.
- Source load limits.
- Recovery requirements.

---

# 41. Full vs Incremental Trade-Off Matrix

| Dimension | Full | Incremental |
|---|---|---|
| Complexity | Usually simpler | Requires state and boundary design |
| Source load | Repeatedly reads full state | Usually reads a smaller change set |
| Network | Higher for large unchanged datasets | Usually lower |
| Deletes | Naturally visible in complete snapshots | Not visible through ordinary timestamp filtering |
| Recovery | Straightforward to rerun | Requires careful state/idempotency design |
| State | Minimal or none for extraction progress | Durable state is central |
| Backfills | Often simple snapshot re-extraction | Requires historical windows and careful state handling |
| Scale | Can become expensive at large volume | Often useful when change volume is much smaller than total volume |
| Freshness | Depends on snapshot runtime/frequency | Can support frequent small runs when source allows it |
| Correctness risks | Primarily operational cost/availability | Boundary, late data, duplicate, delete, and state risks |

There is no universal winner.

The decision depends on workload characteristics.

---

# 42. Production Implementation

A simplified extractor:

```python
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Protocol


class SourceClient(Protocol):
    def extract(
        self,
        *,
        start: datetime,
        end: datetime | None = None,
    ) -> list[dict[str, Any]]:
        ...


class StateStore(Protocol):
    def get_watermark(self) -> datetime | None:
        ...

    def save_watermark(self, watermark: datetime) -> None:
        ...


class LandingStore(Protocol):
    def write(self, records: list[dict[str, Any]], *, run_id: str) -> None:
        ...


@dataclass(frozen=True)
class ExtractionResult:
    extracted: int
    landed: int
    watermark_before: datetime | None
    watermark_after: datetime | None


def extract_incremental(
    source_client: SourceClient,
    state_store: StateStore,
    landing_store: LandingStore,
    *,
    lookback: timedelta,
    run_id: str,
    extraction_end: datetime,
) -> ExtractionResult:
    watermark_before = state_store.get_watermark()

    if watermark_before is None:
        # First-run behavior must be explicit.
        extraction_start = datetime.min.replace(tzinfo=extraction_end.tzinfo)
    else:
        extraction_start = watermark_before - lookback

    records = source_client.extract(
        start=extraction_start,
        end=extraction_end,
    )

    # In production, deduplicate using a source-defined identity/version key.
    deduplicated = deduplicate_records(records)

    # Durable landing must succeed before state advances.
    landing_store.write(deduplicated, run_id=run_id)

    validate_landing(deduplicated)

    next_watermark = determine_safe_watermark(
        records=deduplicated,
        extraction_end=extraction_end,
    )

    # Advance state only after the data is durably landed and validated.
    state_store.save_watermark(next_watermark)

    return ExtractionResult(
        extracted=len(records),
        landed=len(deduplicated),
        watermark_before=watermark_before,
        watermark_after=next_watermark,
    )
```

The example uses intentionally small interfaces so that each responsibility is visible.

The core sequence is:

1. Read watermark.
2. Apply lookback.
3. Extract.
4. Land raw data.
5. Deduplicate.
6. Validate.
7. Determine safe progress.
8. Commit/persist data.
9. Advance state.

The placeholder functions represent domain-specific logic:

```python
def deduplicate_records(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    ...


def validate_landing(records: list[dict[str, Any]]) -> None:
    ...


def determine_safe_watermark(
    *,
    records: list[dict[str, Any]],
    extraction_end: datetime,
) -> datetime:
    ...
```

In a real implementation, these functions must have explicit contracts. Do not hide boundary semantics behind vague helper functions.

---

# 43. Mock API Design

The hands-on laboratory below uses a mock API entirely inside this Markdown file.

Conceptual endpoint:

```text
GET /customers?updated_since=...
```

The mock source should be able to simulate:

- Normal updates.
- Late commits.
- Hard deletes.
- Identical timestamps.
- Empty windows.

A compact in-memory model can be:

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Customer:
    id: int
    name: str
    updated_at: datetime


class MockCustomersAPI:
    def __init__(self, customers: list[Customer]) -> None:
        self.customers = customers

    def get_customers(
        self,
        *,
        updated_since: datetime | None,
    ) -> list[Customer]:
        if updated_since is None:
            return list(self.customers)

        return [
            customer
            for customer in self.customers
            if customer.updated_at > updated_since
        ]

    def delete_customer(self, customer_id: int) -> None:
        self.customers = [
            customer
            for customer in self.customers
            if customer.id != customer_id
        ]

    def update_customer(
        self,
        customer_id: int,
        *,
        name: str,
        updated_at: datetime,
    ) -> None:
        for customer in self.customers:
            if customer.id == customer_id:
                customer.name = name
                customer.updated_at = updated_at
                return

        raise KeyError(customer_id)
```

For the laboratory, deliberately manipulate the model to create late commits and identical timestamps.

---

# 44. Required Hands-On Exercise

The roadmap names the exercise `incremental_extractor.py`.

**Do not create that file.**

Keep the implementation inside this Markdown chapter.

The exercise must demonstrate:

1. Store an `updated_at` watermark.
2. Extract incrementally.
3. Land raw pages as JSON Lines.
4. Partition by run date.
5. Inject late commits.
6. Demonstrate missed records.
7. Fix the problem with lookback.
8. Deduplicate by `(id, updated_at)`.
9. Inject hard deletes.
10. Demonstrate the delete problem.
11. Implement weekly full-key reconciliation.
12. Emit delete markers.
13. Implement `backfill(start, end, window="1d")`.
14. Crash after landing but before watermark update.
15. Re-run successfully.
16. Test identical timestamps.
17. Test empty windows.
18. Test first-ever execution.

## 44.1 In-Memory State and Landing

```python
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


@dataclass(frozen=True)
class CustomerRecord:
    id: int
    name: str
    updated_at: datetime


class InMemoryState:
    def __init__(self) -> None:
        self.watermark: datetime | None = None

    def get(self) -> datetime | None:
        return self.watermark

    def set(self, value: datetime) -> None:
        self.watermark = value


class JsonlLanding:
    def __init__(self, root: Path) -> None:
        self.root = root

    def write(
        self,
        records: list[CustomerRecord],
        *,
        run_date: str,
        run_id: str,
    ) -> Path:
        destination = (
            self.root
            / f"run_date={run_date}"
            / f"run_id={run_id}.jsonl"
        )
        destination.parent.mkdir(parents=True, exist_ok=True)

        with destination.open("w", encoding="utf-8") as handle:
            for record in records:
                payload = asdict(record)
                payload["updated_at"] = record.updated_at.isoformat()
                handle.write(json.dumps(payload) + "\n")

        return destination
```

This demonstrates the required JSON Lines landing and run-date partitioning concept.

## 44.2 Deduplication by `(id, updated_at)`

```python
def deduplicate_by_id_and_timestamp(
    records: list[CustomerRecord],
) -> list[CustomerRecord]:
    seen: set[tuple[int, datetime]] = set()
    result: list[CustomerRecord] = []

    for record in records:
        key = (record.id, record.updated_at)

        if key in seen:
            continue

        seen.add(key)
        result.append(record)

    return result
```

This is appropriate only when `(id, updated_at)` represents the desired version identity.

If two legitimate versions can share both values, a stronger source sequence/version is required.

---

# 45. Demonstrating a Missed Late Commit

Assume:

```text
Run 1 watermark = 10:00
```

The extractor uses:

```sql
WHERE updated_at > '10:00'
```

Now a source transaction commits late:

```text
09:59 transaction starts
10:00 extractor passes boundary
10:05 transaction commits
```

If the resulting source record carries a timestamp earlier than the extractor's next boundary, a naïve extractor can miss it.

### Failure experiment

1. Start with watermark `10:00`.
2. Run extraction.
3. Insert a record with a source timestamp that falls before the next boundary.
4. Run the next extraction without lookback.
5. Confirm that the record is absent.
6. Add a 30-minute lookback.
7. Run again.
8. Confirm that the record is recovered.
9. Deduplicate the overlap.

The exercise demonstrates why “last timestamp” is not enough reasoning.

---

# 46. Demonstrating Hard Deletes

Start with:

```text
1 Alice
2 Bob
3 Carol
```

Delete Bob:

```text
1 Alice
3 Carol
```

Run:

```sql
SELECT *
FROM customers
WHERE updated_at > :watermark;
```

No deletion record is returned.

The laboratory should then perform a key reconciliation:

```text
Source keys:
1, 3

Target keys:
1, 2, 3

Target-only:
2
```

Emit a delete marker conceptually:

```json
{"id": 2, "operation": "DELETE"}
```

The delete marker is a target-processing event, not evidence that the original timestamp query discovered Bob.

---

# 47. Backfill Implementation

A simple extraction-oriented backfill skeleton:

```python
from collections.abc import Callable, Iterator
from datetime import datetime, timedelta


def windows(
    start: datetime,
    end: datetime,
    *,
    step: timedelta,
) -> Iterator[tuple[datetime, datetime]]:
    current = start

    while current < end:
        boundary = min(current + step, end)
        yield current, boundary
        current = boundary


def backfill(
    start: datetime,
    end: datetime,
    *,
    window: timedelta = timedelta(days=1),
    extract_window: Callable[
        [datetime, datetime],
        list[CustomerRecord],
    ],
) -> None:
    for window_start, window_end in windows(
        start,
        end,
        step=window,
    ):
        records = extract_window(window_start, window_end)

        # Production pattern:
        # 1. Assign a deterministic window/run identity.
        # 2. Land the raw records.
        # 3. Validate the landing.
        # 4. Apply idempotent target logic.
        # 5. Record the completed window.
        # 6. Retry only failed windows.
        print(
            f"backfill {window_start.isoformat()} "
            f"to {window_end.isoformat()}: {len(records)} records"
        )
```

---

# 48. Crash-Recovery Exercise

Inject a failure after landing but before watermark update:

```python
def run_with_failure_injection() -> None:
    records = extract_records()

    land_records(records)

    # Simulate process failure here.
    raise RuntimeError("Injected crash before watermark update")

    update_watermark()
```

After restart:

```text
watermark still points to previous committed progress
        ↓
same overlap is extracted again
        ↓
landing/target operation is idempotent
        ↓
watermark advances only after successful commit
```

The key observation is:

> A crash should create reprocessing, not silent data loss.

---

# 49. Boundary Testing

Use records such as:

```text
customers
---------
id | name  | updated_at
1  | Alice | 10:00:00
2  | Bob   | 10:05:00
3  | Carol | 10:05:00
4  | Dave  | 10:10:00
```

Test:

```text
watermark = 10:05:00
```

Then compare:

```sql
updated_at > :watermark
```

and:

```sql
updated_at >= :watermark
```

Expected reasoning:

```text
>
→ Dave only

>=
→ Bob, Carol, Dave
```

Then ask:

> If Bob and Carol were already landed, how does the pipeline safely handle them appearing again?

Expected answer:

```text
Idempotency + deduplication / upsert
```

---

# 50. Empty-Window Test

Set the watermark beyond all source records:

```text
watermark = 23:00
```

Then extract.

Expected:

```text
records_returned = 0
```

The run should not automatically be marked failed.

Observability should distinguish:

```text
successful empty window
```

from:

```text
source query failure
```

---

# 51. First-Ever Execution Test

Start with:

```text
watermark = None
```

The code should follow the documented initial strategy.

For example:

```text
None
 ↓
initial full extraction
 ↓
durable landing
 ↓
validation
 ↓
state initialization
```

or:

```text
None
 ↓
configured historical window
 ↓
durable landing
 ↓
state initialization
```

Do not silently default to an arbitrary timestamp.

---

# 52. Failure Injection Lab

## Failure 1 — Watermark Advanced Before Data Write

```text
extract
 ↓
advance watermark
 ↓
CRASH
 ↓
data never written
```

Result:

```text
state says complete
data is incomplete
```

**Fix:** advance state only after durable landing/commit.

---

## Failure 2 — Strict `>` Boundary Loses Records

```text
watermark = 10:00:00
record = 10:00:00
query = > 10:00:00
```

Result:

```text
record excluded
```

**Fix:** Define boundary semantics explicitly; use overlap or composite progress where appropriate.

---

## Failure 3 — No Lookback Loses Late Commit

```text
transaction starts
 ↓
extractor passes boundary
 ↓
transaction commits later
```

**Fix:** Use a source-appropriate lookback or stronger source progress marker.

---

## Failure 4 — Lookback Without Deduplication Creates Duplicates

```text
Run 1 → 10:00–10:30
Run 2 → 10:15–11:00
```

The overlap can be processed twice.

**Fix:** Idempotent target writes and appropriate deduplication.

---

## Failure 5 — Hard Delete Is Missed

```text
Bob exists
 ↓
Bob is deleted
 ↓
timestamp query returns no Bob
```

**Fix:** Soft delete, full-key reconciliation, CDC, or another source-supported deletion mechanism.

---

## Failure 6 — Timestamp Precision Mismatch

```text
source = 10:00:00.500
API filter precision = seconds
```

**Fix:** Understand filter precision and use a safety overlap when necessary.

---

## Failure 7 — Source Clock Differs From Extractor Clock

```text
source clock = 10:00
extractor clock = 10:02
```

**Fix:** Prefer source-defined progress markers and document timezone/clock semantics.

---

## Failure 8 — Backfill Overlaps Normal Incremental Run

```text
normal run
   ↓
backfill same period
   ↓
normal run again
```

**Fix:** Make historical processing idempotent and separate backfill progress from normal watermark semantics where necessary.

---

# 53. Debugging Methodology

When an incremental pipeline appears to have missed or duplicated data, do not immediately rewrite the query.

Use this process:

```text
1. Identify last committed watermark
2. Identify actual source records
3. Calculate extraction window
4. Inspect boundary condition
5. Check late-arriving records
6. Check duplicates
7. Check deletes
8. Check state advancement timing
9. Compare source and target counts
10. Reconstruct the timeline
```

## Realistic Debugging Example

Suppose a customer with ID 42 is missing.

### Step 1 — Inspect state

```text
watermark_before = 10:00:00
watermark_after  = 10:30:00
```

### Step 2 — Inspect extraction window

```text
10:00 → 10:30
```

### Step 3 — Inspect source

The source shows:

```text
id = 42
updated_at = 10:04:00
```

### Step 4 — Inspect landing

No ID 42 exists.

### Step 5 — Inspect query boundary

```sql
WHERE updated_at > '10:00:00'
AND updated_at < '10:30:00'
```

That should include 42.

### Step 6 — Inspect pagination / source behavior

If this was an API, the record may have been omitted by pagination, filtering, or an API consistency issue.

### Step 7 — Inspect state timing

If the raw landing failed but state advanced, the state is the root cause.

The debugging lesson is:

> Reconstruct the source-to-state timeline before changing extraction logic.

---

# 54. Completeness Proof

A successful process exit does not prove that extraction was complete.

Useful evidence includes:

- Source counts.
- Target counts.
- Watermark before/after.
- Overlap reconciliation.
- Checksums where appropriate.
- Periodic full-key reconciliation.
- Source API totals.
- Audit metadata.
- Known source sequence ranges.

The goal is to establish evidence for:

```text
Did the pipeline process the intended source range?
```

not merely:

```text
Did the process finish without an exception?
```

---

# 55. Idempotency

The extractor must tolerate:

```text
same page extracted twice
same window extracted twice
job restarted
backfill repeated
lookback overlap
```

Desired behavior:

```text
same input
   +
same processing
   ↓
same target state
```

This is what makes crash recovery practical.

Idempotency can be implemented through:

- Primary-key upsert.
- `MERGE`.
- Deterministic partition replacement.
- Stable event IDs.
- Deduplication keys.
- Immutable raw landing plus deterministic downstream processing.

---

# 56. Observability

A production incremental pipeline should measure at least:

- Records requested.
- Records returned.
- Records landed.
- Duplicates detected.
- Deletes detected.
- Watermark before.
- Watermark after.
- Extraction window.
- Duration.
- Freshness.
- Retries.
- Failures.

A useful run record might look like:

```text
run_id                  = run-20261001-001
watermark_before       = 2026-09-30T10:00:00Z
window_start            = 2026-09-30T09:30:00Z
window_end              = 2026-10-01T10:00:00Z
records_extracted       = 18,420
duplicates_removed      = 420
records_landed          = 18,000
deletes_detected        = 17
watermark_after         = 2026-10-01T10:00:00Z
duration_seconds        = 91
status                  = SUCCESS
```

---

# 57. Production Metadata Example

A conceptual metadata table:

| Field | Purpose |
|---|---|
| `pipeline_name` | Identifies the pipeline |
| `run_id` | Identifies this execution |
| `started_at` | Run start time |
| `completed_at` | Run completion time |
| `watermark_before` | Previous committed progress |
| `watermark_after` | New committed progress |
| `window_start` | Actual extraction start |
| `window_end` | Actual extraction end |
| `records_extracted` | Records returned by source |
| `records_landed` | Records durably landed |
| `duplicates_removed` | Overlap eliminated |
| `deletes_detected` | Deletes identified through reconciliation/signals |
| `status` | Success/failure state |

This metadata makes incidents reconstructable.

---

# 58. Architecture Diagram

```text
                 ┌──────────────────┐
                 │ Source System    │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Extraction Query │
                 │ updated_at > WM  │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Raw Landing      │
                 │ immutable payload│
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Validation       │
                 │ Deduplication    │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Target           │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Watermark State  │
                 └──────────────────┘
```

The ordering matters.

The state should reflect successful committed progress.

---

# 59. Production Architecture — Advanced

A robust architecture can look like:

```text
Source
  │
  ├── incremental filter
  ├── lookback window
  │
  ▼
Extractor
  │
  ├── checkpoint/progress
  ├── metrics
  └── retries
  │
  ▼
Bronze / Raw Landing
  │
  ├── immutable payload
  ├── run_id
  ├── extracted_at
  └── source metadata
  │
  ▼
Validation / Deduplication
  │
  ▼
Target
  │
  ▼
State Store
```

### Responsibility boundaries

**Source**
- Defines actual data semantics.
- Provides filter capability.
- Provides timestamps/sequence/version semantics.

**Extractor**
- Calculates extraction windows.
- Calls source.
- Records run metadata.
- Handles transient failures according to the broader ingestion design.

**Raw landing**
- Preserves evidence of what was received.
- Supports replay and debugging.

**Validation/deduplication**
- Checks payload correctness.
- Removes intentional overlap.
- Enforces source identity/version rules.

**Target**
- Applies append/upsert/delete semantics.

**State store**
- Records committed extraction progress.

---

# 60. Architecture Trade-Offs

## Larger Lookback

Pros:

- More likely to catch late records.
- More tolerant of timestamp uncertainty.

Cons:

- More duplicate processing.
- More source load.
- More network traffic.
- More downstream work.

## Smaller Lookback

Pros:

- Cheaper.
- Faster.
- Less overlap.

Cons:

- Greater risk of missing late data.

## Frequent Full Reconciliation

Pros:

- Stronger delete detection.
- Faster discovery of divergence.

Cons:

- More source and compute cost.

## Infrequent Reconciliation

Pros:

- Lower operational cost.

Cons:

- Deletes can remain stale longer.

Do not choose arbitrary values merely because they are common elsewhere.

Derive the strategy from:

```text
source behavior
+
freshness SLA
+
change rate
+
cost
+
acceptable recovery window
```

---

# 61. Watermark as a Contract

Treat the watermark strategy as part of the source contract.

Document:

```text
watermark column
update guarantees
timestamp precision
timezone
late-arrival behavior
delete behavior
indexing
boundary semantics
retention
```

Before production deployment, ask the source owner:

> “What guarantee does this field actually provide?”

For example:

```text
updated_at:
- generated by database trigger
- UTC
- microsecond precision
- changes on every insert/update
- not changed by hard delete
- indexed
```

This is much stronger than simply writing:

```text
watermark = updated_at
```

---

# 62. Composite Watermarks

When timestamps alone are insufficient, a composite position can provide more precise ordering:

```text
(updated_at, id)
```

Conceptual query:

```sql
WHERE
    updated_at > :timestamp
OR (
    updated_at = :timestamp
    AND id > :id
)
ORDER BY updated_at, id;
```

This helps distinguish multiple records sharing the same timestamp.

However, it requires:

- A stable secondary ordering key.
- Correct source ordering.
- Appropriate indexes.
- Well-defined state semantics.
- An understanding of updates to existing IDs.

It is not automatically correct for every source.

---

# 63. Watermark State Machine

A useful conceptual state machine is:

```text
INITIAL
   ↓
RUNNING
   ↓
LANDED
   ↓
VALIDATED
   ↓
COMMITTED
   ↓
WATERMARK ADVANCED
```

The watermark should represent:

```text
COMMITTED
```

not:

```text
RUNNING
```

and not:

```text
ATTEMPTED
```

This distinction is essential for recovery.

---

# 64. Advanced Scenario — Crash at Every Stage

| Crash point | State that should remain | Rerun expectation |
|---|---|---|
| Before extraction | Previous committed state | Start normally |
| During extraction | Previous committed state | Re-extract |
| After extraction | Previous committed state | Reprocess extracted range |
| During landing | Previous committed state | Retry landing safely |
| After landing | Previous committed state until commit | Reconcile/idempotently reuse landing |
| During validation | Previous committed state | Revalidate |
| After target write | Depends on transaction/commit design | Idempotent rerun must converge |
| Before watermark update | Previous committed state | Re-read overlap |
| After watermark update | New state must correspond to durable committed data | If not, this is a correctness incident |

The most dangerous case is:

```text
watermark advanced
+
data not durably committed
```

That is why state advancement belongs after durable progress.

---

# 65. Common Mistakes

Avoid:

- Using full extraction for huge datasets without justification.
- Using incremental extraction without a reliable watermark.
- Advancing the watermark before durable landing.
- Using strict `>` without boundary analysis.
- Ignoring identical timestamps.
- Ignoring late commits.
- Using no lookback when source semantics require one.
- Using lookback without deduplication.
- Assuming `updated_at` is always reliable.
- Forgetting deletes.
- Having no reconciliation strategy.
- Having no first-run behavior.
- Having no backfill strategy.
- Using local-time watermarks without explicit semantics.
- Ignoring timestamp precision.
- Storing state only in process memory.
- Mixing backfill and normal incremental state carelessly.
- Assuming successful execution means complete extraction.

---

# 66. Knowledge Check

Do these questions before reading the answer key.

## Basic — Questions

1. What is full extraction?
2. What is incremental extraction?
3. What is a watermark?
4. What is a high-water mark?
5. Why can full extraction be useful for small reference data?
6. What is append-only data?
7. What is a changed-record incremental pattern?
8. Why might changed records require an upsert?
9. Why should watermark state be durable?
10. Give two examples of possible watermark fields.

## Intermediate — Questions

1. Why can `>` lose records?
2. Why can `>=` create duplicate processing?
3. What problem do identical timestamps create?
4. What is a lookback window?
5. Why does lookback need deduplication?
6. What is a late commit?
7. Why can clock skew affect timestamp extraction?
8. Why does an index help incremental extraction?
9. Why should the watermark advance after durable landing?
10. What should happen when a pipeline crashes before watermark advancement?

## Advanced — Questions

1. Why can timestamp extraction miss hard deletes?
2. What is full-key reconciliation?
3. When might CDC be evaluated?
4. What makes a backfill idempotent?
5. What is a composite watermark?
6. Why does timestamp precision matter?
7. What should a source watermark contract document?
8. How can a hybrid strategy combine incremental extraction and reconciliation?
9. How would you prove extraction completeness?
10. How does a freshness SLA influence extraction design?

---

# 67. Knowledge Check — Answer Key

## Basic Answers

1. **Full extraction** reads the complete current source state on a run.
2. **Incremental extraction** reads new or changed records relative to previously committed progress.
3. A **watermark** is a source-side progress marker used to define what has safely been extracted.
4. A **high-water mark** is the latest committed progress position under the pipeline's extraction semantics.
5. Small reference data may be cheap enough that the simplicity and natural reconciliation benefits outweigh incremental complexity.
6. Append-only data is data that is not changed after creation.
7. A changed-record pattern extracts records that have been modified since prior progress.
8. The target may already contain the record, so the new version needs to replace/update it rather than merely append another current-state row.
9. Process-local state disappears on crashes/restarts; durable state survives.
10. Examples include `updated_at`, `created_at`, sequence numbers, IDs under suitable guarantees, versions, and source cursors.

## Intermediate Answers

1. `>` excludes records exactly equal to the watermark.
2. `>=` reprocesses the boundary and therefore requires safe idempotency/deduplication.
3. Multiple records can share the same timestamp, so timestamp alone may not uniquely identify progress.
4. A lookback moves the effective extraction start backward to intentionally re-read a safety overlap.
5. Overlap creates repeated records by design.
6. A late commit is data that becomes committed/visible after the extractor has already passed the relevant boundary.
7. Different clocks can cause timestamps and extraction cutoffs to be inconsistent.
8. An index can allow the source to find changed rows efficiently rather than scanning a large dataset.
9. Otherwise a crash can leave the state saying data was processed when it was not.
10. Keep the previous committed state and safely reprocess the range on restart.

## Advanced Answers

1. A hard-deleted row no longer exists for `updated_at > watermark` to return.
2. Full-key reconciliation compares source and target keys to identify target-only records that may represent deletes.
3. CDC is useful when reliable change events, including deletes, are required and the source provides appropriate CDC capabilities.
4. Repeating the same backfill produces the same intended target state rather than additional unintended duplicates.
5. A composite watermark uses multiple ordered fields, such as `(updated_at, id)`, to distinguish records sharing the same timestamp.
6. If the source stores more precision than the extraction interface exposes, boundary filters can omit records.
7. Field semantics, update guarantees, precision, timezone, late-arrival behavior, delete behavior, indexing, boundary semantics, and retention.
8. Frequent incremental runs can provide freshness while periodic reconciliation can provide stronger completeness/delete detection.
9. Use source/target counts, watermark evidence, overlap reconciliation, source totals, checksums where appropriate, key reconciliation, and audit metadata.
10. A stricter SLA may require more frequent extraction, efficient source filtering, bounded overlap, and faster recovery.

---

# 68. Interview Questions

These questions are intended to test production reasoning rather than memorized definitions.

1. When would you choose full extraction over incremental?
2. What makes a watermark reliable?
3. Why is `updated_at` dangerous?
4. How do you handle late-arriving records?
5. What happens if the pipeline crashes after landing but before updating the watermark?
6. How do you detect deletes?
7. How would you design a backfill?
8. Why can `>=` create duplicates?
9. Why can `>` create data loss?
10. How do you handle identical timestamps?
11. What is a lookback window?
12. How do you select its size?
13. How do time zones affect incremental extraction?
14. How does timestamp precision affect correctness?
15. How would you design incremental extraction for 500 million rows?
16. How would you prove completeness?
17. How would you design reconciliation?
18. What would you put in an ingestion metadata table?
19. What is the difference between attempted progress and committed progress?
20. Why is a durable raw landing useful during incremental extraction failures?

A strong interview answer should include:

```text
source semantics
+
failure modes
+
state
+
boundaries
+
idempotency
+
observability
+
recovery
```

---

# 69. Senior-Level Design Exercise

## Scenario

A SaaS API contains:

```text
200 million customer records
0.5% change daily
updated_since is supported
timestamps have millisecond precision
records can arrive up to 20 minutes late
hard deletes are not exposed
business freshness requirement: < 30 minutes
```

Design:

- Extraction strategy.
- Watermark.
- Lookback.
- Deduplication.
- Delete handling.
- State management.
- Backfill strategy.
- Reconciliation schedule.
- Completeness checks.
- Observability.
- Failure recovery.

### Stop Here and Design It Yourself

Before reading the reference solution, write your architecture.

Consider:

```text
What does the API guarantee?
How large is each extraction window?
What does the watermark actually mean?
What happens if the process crashes?
How are deletes discovered?
How do you prove completeness?
```

## Reference Solution

A reasonable design could be:

```text
Incremental API extraction
        ↓
source-defined updated_since
        ↓
bounded safety lookback
        ↓
raw immutable landing
        ↓
deduplication/upsert
        ↓
validation
        ↓
committed state advancement
        ↓
periodic key reconciliation
```

### Watermark

Investigate the API's `updated_since` semantics and use the most reliable source-generated change timestamp available.

Do not assume the API's timestamp is complete until its update semantics are verified.

### Lookback

Because records can arrive up to 20 minutes late, the extraction window needs a safety margin informed by that behavior and operational variability.

Do not choose a number simply because it is a common industry value.

### Deduplication

The overlap means records can be returned repeatedly.

Use a stable customer identity plus an appropriate source version/timestamp rule.

### Deletes

The API does not expose hard deletes.

Therefore timestamp-based extraction alone cannot guarantee delete completeness.

Evaluate:

- Periodic full-key reconciliation.
- Soft-delete fields if the API has one that was overlooked.
- Another source endpoint.
- CDC or source export capabilities if available.

### State

Persist state durably.

A run should conceptually be:

```text
read previous committed state
        ↓
calculate effective extraction window
        ↓
extract
        ↓
land
        ↓
validate
        ↓
commit target
        ↓
advance state
```

### Backfills

Use bounded historical windows:

```text
day or smaller window
```

depending on API volume and operational limits.

Make each window idempotent.

### Reconciliation

Because hard deletes are not exposed, schedule reconciliation frequently enough to satisfy the business's acceptable stale-delete tolerance.

The schedule is a design decision derived from:

```text
business requirement
+
source load
+
dataset size
+
reconciliation cost
```

### Completeness

Track:

```text
records requested
records returned
records landed
duplicates
watermark before
watermark after
window start/end
run duration
API totals where available
reconciliation results
```

### Failure Recovery

If the process crashes before state advancement:

```text
previous watermark remains
        ↓
overlap is re-extracted
        ↓
idempotent processing prevents corruption
```

This design deliberately accepts some duplicate work in exchange for safer recovery.

---

# 70. Five Production Design Scenarios

For each scenario, document:

```text
Strategy
Watermark
Boundary
Delete handling
Backfill
Failure recovery
Freshness
Operational complexity
```

## Scenario 1 — 5,000-Row Reference Table

Facts:

```text
5,000 rows
low change rate
no reliable change marker
```

Reasoning should consider:

- Whether full extraction is cheap.
- Whether a snapshot naturally detects deletes.
- Whether incremental complexity is justified.

## Scenario 2 — 500-Million-Row Transactional Table

Facts:

```text
500 million rows
small daily change rate
reliable indexed change marker
```

Reasoning should consider:

- Source indexing.
- Change rate.
- Query performance.
- Lookback.
- Target upsert semantics.
- Reconciliation.

## Scenario 3 — Append-Only Event Stream

Facts:

```text
immutable events
monotonic sequence
```

Reasoning should consider:

- Sequence-based progress.
- Append-only target semantics.
- Crash recovery.
- Duplicate event handling.

## Scenario 4 — SaaS API Without Delete Events

Facts:

```text
mutable records
updated_since supported
no delete event
```

Reasoning should consider:

- Incremental updates.
- Lookback.
- Deduplication.
- Full-key reconciliation.
- Alternative source capabilities.

## Scenario 5 — Daily Partner File

Facts:

```text
one file per day
each file represents current full state
```

Reasoning should consider:

- Snapshot semantics.
- File completeness.
- Missing-file detection.
- Delete detection.
- Historical reprocessing.

---

# 71. Production Checklist

## Strategy

- [ ] Full vs incremental decision documented.
- [ ] Volume understood.
- [ ] Change rate understood.
- [ ] Freshness SLA understood.
- [ ] Operational complexity accepted.

## Watermark

- [ ] Watermark field/progress marker documented.
- [ ] Update semantics verified.
- [ ] Indexed where appropriate.
- [ ] Precision verified.
- [ ] Timezone verified.
- [ ] Ordering/monotonicity assumptions verified.

## Boundaries

- [ ] Inclusive/exclusive semantics documented.
- [ ] Identical timestamps handled.
- [ ] Lookback configured based on source behavior.
- [ ] Deduplication implemented.
- [ ] Composite progress evaluated where needed.

## Deletes

- [ ] Delete behavior understood.
- [ ] Soft-delete signal checked.
- [ ] Reconciliation strategy defined.
- [ ] CDC evaluated when appropriate.
- [ ] Delete freshness requirement defined.

## Reliability

- [ ] State stored durably.
- [ ] State advances only after durable landing/commit.
- [ ] Crash recovery tested.
- [ ] Reruns are idempotent.
- [ ] First-ever behavior is explicit.
- [ ] Empty-window behavior is explicit.

## Backfills

- [ ] Historical extraction supported.
- [ ] Windows bounded.
- [ ] Backfills idempotent.
- [ ] Backfill state is separated from normal incremental semantics where necessary.
- [ ] Normal incremental processing is protected from backfill overlap.

## Observability

- [ ] Watermark before/after.
- [ ] Window start/end.
- [ ] Records extracted.
- [ ] Records landed.
- [ ] Duplicates.
- [ ] Deletes.
- [ ] Freshness.
- [ ] Duration.
- [ ] Failures/retries.
- [ ] Run ID.
- [ ] Reconciliation results.

---

# 72. Final Mental Model

```text
                  EXTRACTION STRATEGY
                         │
           ┌─────────────┴─────────────┐
           │                           │
         FULL                    INCREMENTAL
           │                           │
     complete snapshot            state required
                                       │
                                       ▼
                                   WATERMARK
                                       │
                         ┌─────────────┼─────────────┐
                         │             │             │
                      boundary      lookback       deletes
                         │             │             │
                         ▼             ▼             ▼
                    deduplication   late data   reconciliation
                         │             │             │
                         └─────────────┼─────────────┘
                                       ▼
                                   safe state
                                       │
                                       ▼
                                    backfills
```

The key principle is:

> **The goal of incremental extraction is not merely to read fewer rows. The goal is to reduce extraction cost while preserving completeness, correctness, recoverability, and freshness.**

The deeper mental model is:

```text
Full extraction
= complete current state

Incremental extraction
= changed/new data + durable progress state

Watermark
= committed source-side progress

Lookback
= intentional overlap for safety

Deduplication
= makes overlap safe

Reconciliation
= detects divergence that ordinary incremental filtering cannot see

Backfill
= controlled historical extraction

Idempotency
= makes retries and crashes recoverable

Observability
= provides evidence of what happened

Completeness
= must be demonstrated, not assumed
```

---

# 73. Exit Criteria

Do not consider this topic complete until you can independently:

- [ ] Explain full extraction.
- [ ] Explain incremental extraction.
- [ ] Explain watermarks.
- [ ] Explain high-water marks.
- [ ] Choose a watermark column/progress marker.
- [ ] Explain why `updated_at` can be unsafe.
- [ ] Implement incremental filtering.
- [ ] Explain indexed watermark fields.
- [ ] Explain monotonicity.
- [ ] Handle inclusive/exclusive boundaries.
- [ ] Handle identical timestamps.
- [ ] Implement a lookback window.
- [ ] Deduplicate overlapping windows.
- [ ] Explain late commits.
- [ ] Explain clock skew.
- [ ] Explain timestamp precision problems.
- [ ] Explain API filter truncation.
- [ ] Advance state only after durable landing/commit.
- [ ] Recover from crashes.
- [ ] Explain why timestamp extraction misses hard deletes.
- [ ] Implement or design delete reconciliation.
- [ ] Design idempotent backfills.
- [ ] Explain first-run behavior.
- [ ] Explain empty-window behavior.
- [ ] Explain hybrid strategies.
- [ ] Compare full and incremental extraction.
- [ ] Select an extraction strategy based on workload characteristics.
- [ ] Propose completeness evidence.
- [ ] Define production observability.
- [ ] Defend the decision in a production architecture review.

---

# 74. Completion Summary

You started with:

```text
"What is full extraction?"
```

Then progressed through:

```text
"What is incremental extraction?"
        ↓
"What is a watermark?"
        ↓
"How do I select one?"
        ↓
"How do I handle boundaries?"
        ↓
"What happens when data arrives late?"
        ↓
"How do I handle duplicates?"
        ↓
"What about deletes?"
        ↓
"How do I backfill?"
        ↓
"What happens when the pipeline crashes?"
        ↓
"How do I prove completeness?"
        ↓
"How do I choose an extraction strategy in production?"
```

The final production perspective is:

```text
Extraction strategy
        +
source contract
        +
durable state
        +
safe boundaries
        +
lookback
        +
deduplication
        +
delete strategy
        +
idempotent recovery
        +
backfills
        +
reconciliation
        +
observability
        =
production-grade extraction
```

There is no universal rule that incremental extraction is always better, and there is no rule that full extraction is always bad.

The correct strategy is the one that satisfies the actual workload's requirements for:

```text
correctness
+
completeness
+
freshness
+
cost
+
recoverability
+
operational simplicity
```

