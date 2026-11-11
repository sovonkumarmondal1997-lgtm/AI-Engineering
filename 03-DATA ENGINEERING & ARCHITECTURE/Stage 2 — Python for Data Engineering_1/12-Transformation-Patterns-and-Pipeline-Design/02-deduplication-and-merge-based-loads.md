# Deduplication and Merge-Based Loads

> **Stage 2 — Python for Data Engineering**  
> **Module 2.12 — Transformation Patterns and Pipeline Design**  
> **Topic 02 — Deduplication and Merge-Based Loads**

## 1. Learning Objectives

By the end of this chapter you should be able to:

- explain why duplicates are normal in production pipelines;
- distinguish exact duplicates, business-key duplicates, and record versions;
- define target grain and business key;
- choose append, partition overwrite, merge/upsert, delete + insert, or full refresh with swap;
- deduplicate within an incoming batch and reconcile against a target;
- select the winning version deterministically;
- handle deletes and tombstones;
- implement merge behavior with Python/Polars and DuckDB;
- implement a database `MERGE`;
- protect newer state from stale out-of-order updates;
- prove idempotency after retries and partial failures;
- reason about target-side merge performance;
- use partition predicates, clustering/data organization, and batching;
- understand bounded deduplication windows;
- test correctness against a clean reference result;
- debug incorrect deduplication and merge behavior.

The progression is:

```text
Basic Concepts
→ Practical Deduplication
→ Load Strategies
→ Deterministic Version Selection
→ Merge / Upsert
→ Idempotency
→ Out-of-Order Data
→ Performance
→ Production Design
```

Topic 01 established readers, writers, pure transformations, deterministic transformations, RunContext, data intervals, partition scope, and testability. Topic 02 applies those foundations to the harder problem:

> **How do we keep a target correct when the same logical data can arrive more than once, in different versions, or in the wrong order?**

---

# 2. Why Duplicates Exist

Duplicates are not necessarily evidence of a broken source. They commonly arise from normal production delivery semantics.

## 2.1 At-least-once delivery

A system may prefer:

```text
deliver again
```

over:

```text
lose the record
```

Therefore a consumer may receive:

```text
event 101
event 101
```

The target must tolerate replay.

## 2.2 Retries

Consider:

```text
read batch
  ↓
transform
  ↓
write target
  ↓
process crashes before success is recorded
```

The orchestrator may retry the entire batch.

A naive append can produce:

```text
101
102
103
101
102
103
```

## 2.3 Overlapping extraction windows

Two runs might use:

```text
Run A: 10:00 → 11:00
Run B: 10:30 → 11:30
```

The interval `10:30 → 11:00` is delivered twice.

Overlap may be intentional and useful. The transformation must therefore tolerate repeated records.

## 2.4 Webhook redelivery

A payment provider may resend the same event if acknowledgement was delayed:

```text
event_id = abc123
event_id = abc123
```

The consumer should treat delivery as replayable.

## 2.5 CDC replay

CDC may produce several states:

```text
customer 42 → pending
customer 42 → paid
```

A replay can deliver either state again. A current-state target must understand both identity and version.

## 2.6 Multiple sources

CRM, billing, and support systems can describe the same business entity.

Deduplication therefore requires a business identity definition.

## 2.7 Partial pipeline failures

A pipeline can write some rows and then fail:

```text
100,000 rows
↓
60,000 durable
↓
crash
```

A retry may contain all 100,000 rows.

The load strategy must make that retry safe.

## 2.8 Reruns and historical processing

A historical interval may intentionally be processed more than once.

Therefore:

```text
same logical input
+
same target
```

is normal production behavior.

---

# 3. Types of Duplicates

## 3.1 Exact duplicates

```text
order_id | status | amount
---------+--------+-------
101      | paid   | 50
101      | paid   | 50
```

Every relevant field is identical.

## 3.2 Business-key duplicates

```text
order_id | status  | amount
---------+---------+-------
101      | pending | 50
101      | paid    | 50
```

The rows differ, but both represent the same logical order.

## 3.3 Different versions

```text
order_id | status  | version
---------+---------+--------
101      | pending | 10
101      | paid    | 11
```

These are different source states, not necessarily duplicate historical events.

If the target is current order state, version 11 may be the only desired row.

If the target is event history, both rows may be required.

> **Deduplication is determined by target grain and business semantics, not by row equality alone.**

---

# 4. Business Key and Target Grain

Before writing deduplication code, answer:

> **What does one target row represent?**

Examples:

```text
one row per order
one row per customer
one row per order line
one row per payment event
one row per customer-day
```

Then define the business key.

Examples:

```text
order → order_id
customer → customer_id
order line → order_id + line_number
customer-day → customer_id + event_date
```

A deduplication rule without a defined grain is incomplete.

## Business key vs physical row

A physical row is a storage representation.

A business key identifies a logical entity.

This is why:

```python
df.unique()
```

can be technically valid but semantically wrong.

It removes identical rows. It does not determine which version of an entity should survive.

---

# 5. The Core Deduplication Question

Correct deduplication is not:

```text
"remove duplicate rows"
```

It is:

```text
Define the grain
        ↓
Define the business key
        ↓
Understand source delivery semantics
        ↓
Identify versions
        ↓
Choose the winning version deterministically
```

Only then should implementation begin.

---

# 6. Load Strategies

The five roadmap strategies are:

```text
1. Append
2. Partition overwrite
3. Merge / upsert
4. Delete + insert
5. Full refresh with swap
```

There is no universal winner. Selection depends on:

- data mutability;
- target grain;
- partitioning;
- duplicate behavior;
- delete semantics;
- target size;
- retry behavior;
- version semantics;
- performance requirements.

---

# 7. Append

Append means:

```text
incoming batch
      ↓
INSERT
      ↓
target
```

Simple implementation:

```python
def append_batch(
    target: pl.DataFrame,
    batch: pl.DataFrame,
) -> pl.DataFrame:
    return pl.concat([target, batch])
```

Append is a natural candidate for immutable event history:

```text
click events
audit events
immutable payment events
```

It becomes dangerous for mutable entities:

```text
order 101 pending
order 101 paid
```

or replayed batches:

```text
batch A
batch A retry
```

Use append only when the target semantics make repeated records acceptable or when explicit deduplication is part of the design.

---

# 8. Partition Overwrite

Partition overwrite replaces a bounded target partition.

Example:

```text
silver/orders/date=2026-09-30
```

Conceptually:

```text
existing partition
       ↓
replace
       ↓
new partition
```

This is useful for:

- daily aggregates;
- corrected partitions;
- deterministic partition-scoped transformations;
- bounded rebuilds.

If:

```text
input partition X
```

always produces:

```text
output partition X
```

then rerunning the same transformation can naturally converge to the same final partition.

Physical atomic replacement is platform-specific and was covered earlier; this topic focuses on the load strategy.

---

# 9. Merge / Upsert

A merge reconciles incoming records with existing target state.

```text
                 incoming
                    │
                    ▼
               MATCH ON KEY
               /                    matched       not matched
             │               │
       update/delete        insert
```

Example:

```text
target:
101 | pending | v10

incoming:
101 | paid    | v11
102 | paid    | v1
```

After merge:

```text
101 | paid | v11
102 | paid | v1
```

Merge is a natural candidate for mutable entities such as:

```text
customer profiles
product catalogues
current order state
account state
```

---

# 10. Delete + Insert

The pattern is:

```text
DELETE affected rows
+
INSERT corrected rows
```

It can be useful when:

- the affected scope is bounded;
- a partition can be rebuilt;
- the corrected dataset is small enough;
- row-by-row merge semantics are unnecessary.

The main operational question is atomicity.

If delete and insert are separate effects, a failure between them can temporarily or permanently leave an incomplete target unless the surrounding system provides suitable transaction/replacement semantics.

---

# 11. Full Refresh With Swap

The conceptual pattern is:

```text
Build new table
       ↓
Validate
       ↓
Swap into place
```

A full refresh can be attractive when:

- the table is small;
- the result is easily recomputable;
- correctness is easier to establish through replacement;
- rollback is important.

Costs include:

- extra compute;
- extra storage;
- longer rebuilds;
- platform-specific swap complexity.

For very large targets with small changes, full refresh may be unnecessarily expensive.

---

# 12. Choosing a Load Strategy

| Data shape | Candidate strategy | Reasoning |
|---|---|---|
| Immutable events | Append + explicit dedupe if required | History is additive |
| Partitioned aggregates | Partition overwrite | A bounded partition can be rebuilt |
| Mutable entities | Merge/upsert | Current state changes |
| Small tables | Full refresh with swap | Simplicity can dominate |
| Corrected bounded region | Delete + insert / overwrite | Replace known scope |
| CDC current-state table | Merge + version guard | Updates and deletes matter |

Before choosing, ask:

```text
What is the grain?
Is the source immutable or mutable?
Are duplicates expected?
Can deletes occur?
Is the target partitioned?
Is the table small enough for refresh?
Does the source provide a reliable version?
What happens on retry?
What happens after partial failure?
```

---

# 13. Batch Deduplication vs Target Deduplication

These are separate problems.

## Within-batch deduplication

```text
incoming batch
      ↓
deduplicate
      ↓
load
```

Example:

```text
101 | pending | v10
101 | paid    | v11
```

may become:

```text
101 | paid | v11
```

## Against-target deduplication

Suppose:

```text
target:
101 | pending | v10

incoming:
101 | paid | v11
```

The incoming batch may be internally unique, but the target still needs reconciliation.

## Why both are needed

A production flow commonly looks like:

```text
batch dedupe
      ↓
version selection
      ↓
target reconciliation
```

Only doing one of these can leave correctness gaps.

---

# 14. Choosing the Winning Version

The roadmap's preferred hierarchy is:

```text
1. sequence number / log position
2. source updated_at
3. load time as last resort
```

## 14.1 Sequence or log position

Example:

```text
order_id | sequence
101      | 104
101      | 105
```

Version 105 wins.

This is especially strong when the source explicitly guarantees ordering semantics.

## 14.2 Source `updated_at`

Example:

```text
order_id | updated_at
101      | 10:05
101      | 10:12
```

10:12 wins if the source timestamp is reliable and represents the state change.

## 14.3 Load time

Suppose:

```text
v12 arrives at 10:00
v11 arrives at 10:05
```

Selecting by load time incorrectly chooses v11.

Load time describes:

```text
when the consumer received the record
```

not necessarily:

```text
which source state is newer
```

Therefore it is a last resort.

---

# 15. Deterministic Tie-Breakers

Suppose:

```text
order_id | updated_at
101      | 10:00:00
101      | 10:00:00
```

A timestamp alone does not define a unique winner.

Use a deterministic secondary field:

```text
updated_at DESC,
event_id DESC
```

Example:

```text
order_id | updated_at | event_id
101      | 10:00:00   | A100
101      | 10:00:00   | A101
```

Winner:

```text
A101
```

Never rely on arbitrary physical row order.

Deterministic selection is required for:

- reproducible reruns;
- consistent backfills;
- reliable debugging;
- idempotency;
- reference-result comparison.

---

# 16. Exact Deduplication With Polars

For truly exact duplicates:

```python
import polars as pl

df = pl.DataFrame(
    {
        "order_id": [101, 101, 102],
        "status": ["paid", "paid", "pending"],
        "amount": [50.0, 50.0, 25.0],
    }
)

deduped = df.unique()
```

This is appropriate only when entire-row equality defines duplication.

It does not solve versioned business-key duplicates.

---

# 17. Business-Key Deduplication With Polars

Example:

```python
df = pl.DataFrame(
    {
        "order_id": [101, 101, 102],
        "status": ["pending", "paid", "pending"],
        "sequence": [10, 11, 1],
    }
)
```

Select the highest sequence per order:

```python
deduped = (
    df
    .sort(
        ["order_id", "sequence"],
        descending=[False, True],
    )
    .group_by("order_id", maintain_order=True)
    .first()
)
```

The important rule is:

```text
business key
+
version ordering
```

not the API call itself.

---

# 18. Deterministic Polars Deduplication

Suppose versions tie:

```python
df = pl.DataFrame(
    {
        "order_id": [101, 101, 101],
        "status": ["paid", "shipped", "cancelled"],
        "sequence": [11, 11, 11],
        "event_id": ["A1", "A2", "A3"],
    }
)
```

Define:

```text
order_id ASC
sequence DESC
event_id DESC
```

Then:

```python
deduped = (
    df
    .sort(
        ["order_id", "sequence", "event_id"],
        descending=[False, True, True],
    )
    .group_by("order_id", maintain_order=True)
    .first()
)
```

The same input produces the same winner.

---

# 19. DuckDB / SQL Deduplication

SQL window functions express deterministic version selection clearly:

```sql
SELECT
    order_id,
    status,
    amount,
    sequence,
    event_id
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY order_id
            ORDER BY
                sequence DESC,
                event_id DESC
        ) AS rn
    FROM incoming_orders
)
WHERE rn = 1;
```

The logic is:

```text
PARTITION BY business key
        ↓
ORDER BY version
        ↓
ROW_NUMBER = 1
```

This is semantically different from:

```sql
SELECT DISTINCT ...
```

because the window function explicitly defines which version wins.

---

# 20. Python-Engine Merge Using Anti-Join + Union

A Python engine can simulate merge behavior:

```text
target
+
incoming winners
↓
identify target keys being replaced
↓
anti-join those target rows away
↓
union surviving target rows + incoming rows
```

Example:

```python
def merge_current_state(
    target: pl.DataFrame,
    incoming: pl.DataFrame,
) -> pl.DataFrame:
    incoming_keys = incoming.select("order_id").unique()

    remaining_target = target.join(
        incoming_keys,
        on="order_id",
        how="anti",
    )

    return pl.concat(
        [remaining_target, incoming],
        how="vertical_relaxed",
    )
```

This assumes `incoming` already contains exactly one correct winner per key.

For a large target, do not automatically load the whole target into Python memory. Use DuckDB or a database/warehouse when that is the appropriate execution engine.

---

# 21. Version-Aware Python Merge

A simple current-state implementation can reconcile target and incoming versions:

```python
def select_latest(
    df: pl.DataFrame,
) -> pl.DataFrame:
    return (
        df
        .sort(
            ["order_id", "sequence", "event_id"],
            descending=[False, True, True],
        )
        .group_by("order_id", maintain_order=True)
        .first()
    )


def merge_current_state(
    target: pl.DataFrame,
    incoming: pl.DataFrame,
) -> pl.DataFrame:
    candidates = pl.concat(
        [
            select_latest(target),
            select_latest(incoming),
        ],
        how="vertical_relaxed",
    )

    return select_latest(candidates)
```

Logical contract:

```text
target + incoming
      ↓
one row per business key
      ↓
highest valid version wins
```

This is a teaching implementation. Large production targets should use an execution engine capable of bounded target access.

---

# 22. Database `MERGE`

A PostgreSQL-style merge can be expressed as:

```sql
MERGE INTO silver_orders AS target
USING staged_orders AS source
ON target.order_id = source.order_id

WHEN MATCHED
     AND source.sequence > target.sequence
     AND source.is_deleted = TRUE
THEN DELETE

WHEN MATCHED
     AND source.sequence > target.sequence
THEN UPDATE SET
    status = source.status,
    amount = source.amount,
    sequence = source.sequence,
    event_id = source.event_id

WHEN NOT MATCHED
     AND source.is_deleted = FALSE
THEN INSERT (
    order_id,
    status,
    amount,
    sequence,
    event_id
)
VALUES (
    source.order_id,
    source.status,
    source.amount,
    source.sequence,
    source.event_id
);
```

The key ideas are:

```text
match key
version guard
delete
update
insert
```

The exact supported syntax should be verified against the database version in use.

---

# 23. Staging Before Merge

A production database load often follows:

```text
source
  ↓
staging
  ↓
deduplicate
  ↓
validate
  ↓
MERGE
  ↓
target
```

Staging gives you a controlled place to:

- inspect incoming rows;
- count duplicates;
- select winning versions;
- validate schema;
- identify deletes;
- measure batch size;
- then mutate the target.

This preserves Topic 01's architecture:

```text
read
 ↓
transform
 ↓
validate
 ↓
load
```

---

# 24. Delete and Tombstone Handling

A delete may arrive as:

```text
order_id | is_deleted
101      | true
```

A target needs an explicit contract.

## Hard delete

```text
101 exists
    ↓
tombstone
    ↓
101 removed
```

SQL:

```sql
WHEN MATCHED
     AND source.is_deleted = TRUE
THEN DELETE
```

## Soft delete

Keep the row:

```text
order_id | status | is_deleted
101      | paid   | true
```

Soft delete may be appropriate when auditability or downstream history matters.

The key rule is:

> **A delete is data too, and its version must be ordered like an update.**

An old delete must not remove newer state.

---

# 25. Idempotency

A load is idempotent when repeatedly applying the same input produces the same final target state.

Conceptually:

```text
Load(B)
Load(B)
```

should have the same final state as:

```text
Load(B)
```

A state formulation is:

```text
L(L(T, B), B) = L(T, B)
```

where:

- `T` is the initial target;
- `B` is the input batch.

Idempotency is a state property, not simply a label attached to a function.

---

# 26. Why Idempotency Matters

Retries happen because of:

- worker crashes;
- network failures;
- database timeouts;
- orchestration failures;
- process termination;
- partial output;
- infrastructure problems.

Therefore:

```text
retry
```

must be treated as a normal condition.

If a retry creates duplicates or stale state, the pipeline is unsafe.

---

# 27. Idempotency Proof

Use this procedure:

1. Start with target `T0`.
2. Apply batch `B`.
3. Capture `T1`.
4. Apply `B` again.
5. Capture `T2`.
6. Verify:

```text
T1 == T2
```

Compare according to the target's semantic contract:

- same business keys;
- same values;
- same versions;
- same delete state.

A stronger test also simulates partial failure.

---

# 28. Partial Failure and Retry

Consider:

```text
incoming batch
      ↓
write 60%
      ↓
CRASH
```

Then retry the complete batch.

## Append

Potential result:

```text
first 60% duplicated
```

unless deduplication is explicitly implemented.

## Partition overwrite

If replacement is safe and atomic, retrying can rebuild the same partition.

## Merge

A transactional, version-aware merge can converge to the correct state after retry.

## Full refresh with swap

If the new table is built separately, a failure before the swap can leave the old target intact.

The load strategy therefore determines recovery behavior.

---

# 29. Out-of-Order Updates

Suppose events arrive:

```text
v10
v12
v11
v13
```

Without protection:

```text
v10 → target v10
v12 → target v12
v11 → target v11  ❌
v13 → target v13
```

Now consider:

```text
v10
v12
v13
v11
```

Without a version guard:

```text
v13 → target v13
v11 → target v11  ❌
```

The target becomes stale.

---

# 30. Version Guards

The merge should compare versions:

```sql
WHEN MATCHED
AND source.version > target.version
THEN UPDATE
```

If:

```text
target = v13
incoming = v11
```

then:

```text
11 > 13
```

is false.

The older event cannot overwrite newer state.

This protects current-state targets from stale delivery.

---

# 31. Out-of-Order Example

Process:

```text
v10
v12
v11
v13
```

| Event | Comparison | Target |
|---|---|---|
| v10 | no target | v10 |
| v12 | 12 > 10 | v12 |
| v11 | 11 > 12 = false | v12 |
| v13 | 13 > 12 | v13 |

Final:

```text
v13
```

Now process:

```text
v13
v11
```

The second event is rejected by the version guard.

Final:

```text
v13
```

---

# 32. Version Tie Handling

If:

```text
target.version = 12
incoming.version = 12
```

then:

```sql
source.version > target.version
```

rejects the incoming row.

That is appropriate if equal versions represent the same logical state.

If equal versions can conflict, define a deterministic secondary ordering:

```text
version DESC,
event_id DESC
```

Never allow physical row order to choose business state.

---

# 33. Merge Performance

A merge reconciles:

```text
incoming source
+
target
```

The incoming batch may be small while the target is enormous.

Example:

```text
incoming = 10,000 rows
target   = 5,000,000,000 rows
```

A whole-table merge can become increasingly expensive.

As the target grows:

```text
target size ↑
      ↓
data inspected ↑
      ↓
merge duration ↑
      ↓
cost ↑
```

The production question becomes:

> **How much target data must be inspected to reconcile this batch?**

---

# 34. Partition Pruning

Suppose the target is partitioned by:

```text
order_date
```

and today's input contains:

```text
order_date = 2026-09-30
```

An unrestricted merge may inspect all historical partitions.

A scoped merge can conceptually restrict target work to:

```text
target.order_date = 2026-09-30
```

The idea is:

```text
incoming scope
      ↓
derive relevant target scope
      ↓
prune unrelated partitions
```

Partition predicates can dramatically reduce merge work.

The exact syntax depends on the execution engine.

---

# 35. Clustering and Data Organization

Target data can also be organized around frequently used merge keys.

Possible mechanisms include:

- clustering;
- indexing;
- sorted storage;
- locality-aware file organization;
- partitioning.

These are not interchangeable.

For example:

```text
partition by order_date
cluster/index by order_id
```

may help when:

- date bounds identify the relevant partition;
- order IDs identify rows within that partition.

The general principle is:

> **Organize target data so the engine can locate relevant rows without inspecting unnecessary data.**

---

# 36. Batching

Large merge workloads may be divided into smaller batches.

Benefits:

- lower memory use;
- shorter transactions;
- shorter lock duration;
- easier recovery;
- smaller retry units.

Costs:

- more transaction overhead;
- possible lower throughput if batches are too small;
- more orchestration complexity.

The goal is not the smallest possible batch.

The goal is an appropriate balance among:

```text
memory
throughput
transaction size
lock duration
failure recovery
```

---

# 37. Deduplication Windows

Some batch systems cannot remember every key forever.

A deduplication window might be:

```text
remember seen keys for 7 days
```

Question:

> What happens when a duplicate arrives on day 10?

If the system no longer remembers the key, it may treat the record as new.

Therefore:

> **A deduplication window is a correctness assumption.**

Choose it based on observed delivery behavior and business requirements.

Streaming systems are outside this chapter; Module 2.16 covers streaming in depth.

---

# 38. Eight-Dataset Strategy Exercise

For each dataset, identify grain, mutability, duplicate behavior, strategy, and reasoning.

| Dataset | Grain / characteristics | Candidate strategy | Reason |
|---|---|---|---|
| Click events | One immutable event | Append + dedupe if needed | Event history is additive |
| Orders with status updates | One current order | Merge + version guard | Mutable state |
| Customer profiles | One customer | Merge/upsert | Mutable entity |
| Daily FX rates | One currency pair/day | Partition overwrite | Daily partition is recomputable |
| Product catalogue | One product | Merge/upsert | Mutable entity |
| CDC stream | One current entity | Merge + version guard + deletes | Replay/out-of-order/delete semantics |
| Webhook payments | One payment event or state | Append or merge depending on target grain | Event history vs current state |
| Daily aggregates | One entity/day | Partition overwrite | Bounded recomputation |

The table gives candidate strategies, not universal answers. The target contract determines the final decision.

---

# 39. Three-Run Comparison

Initial target:

```text
empty
```

Input:

```text
101 | paid
102 | paid
```

## Append

Run 1:

```text
101 | paid
102 | paid
```

Run 2 retry:

```text
101 | paid
102 | paid
101 | paid
102 | paid
```

Append is not idempotent by itself.

## Partition overwrite

Run 1:

```text
date=X
101 | paid
102 | paid
```

Run 2 rebuilds the same partition:

```text
date=X
101 | paid
102 | paid
```

The final state remains equivalent if replacement is safe and deterministic.

## Merge

Run 1:

```text
101 | paid
102 | paid
```

Run 2 matches the same keys and leaves the target in the same logical state.

A correctly designed merge is idempotent.

---

# 40. Complete Orders CDC Hands-On Project

## Scenario

You have 30 days of silver orders.

The CDC source:

- redelivers approximately 3% of events;
- contains updates;
- contains deletes;
- can deliver records out of order;
- provides a source sequence number;
- can replay the same batch.

Target grain:

```text
one current row per order
```

Required flow:

```text
CDC
 ↓
batch dedupe
 ↓
winning version
 ↓
delete handling
 ↓
staging
 ↓
merge with version guard
 ↓
current-state target
```

---

# 41. Example CDC Input

```text
order_id | status    | amount | sequence | event_id | is_deleted
---------+-----------+--------+----------+----------+-----------
101      | pending   | 50.00  | 10       | e10      | false
101      | paid      | 50.00  | 11       | e11      | false
101      | pending   | 50.00  | 10       | e10      | false
102      | paid      | 25.00  | 20       | e20      | false
102      | cancelled | 25.00  | 21       | e21      | true
```

For order 101:

```text
v10
v11
v10 duplicate
```

Winner:

```text
v11
```

For order 102:

```text
v20 active
v21 delete
```

Winner:

```text
v21 delete
```

---

# 42. Reference Dataset / Correctness Oracle

Build a simple reference implementation that processes source events in sequence order.

```python
def reference_state(events):
    state = {}

    for row in events:
        key = row["order_id"]
        current = state.get(key)

        if (
            current is None
            or row["sequence"] > current["sequence"]
            or (
                row["sequence"] == current["sequence"]
                and row["event_id"] > current["event_id"]
            )
        ):
            state[key] = row

    return state
```

The production pipeline should match the reference's logical result.

This is a correctness oracle:

```text
production-style implementation
             ↓
          compare
             ↑
clean reference implementation
```

The reference can prioritize clarity over performance.

---

# 43. Python Implementation

A simple version-selection step:

```python
def latest_events(
    df: pl.DataFrame,
) -> pl.DataFrame:
    return (
        df
        .sort(
            ["order_id", "sequence", "event_id"],
            descending=[False, True, True],
        )
        .group_by("order_id", maintain_order=True)
        .first()
    )
```

A teaching merge:

```python
def merge_orders(
    target: pl.DataFrame,
    incoming: pl.DataFrame,
) -> pl.DataFrame:
    incoming = latest_events(incoming)

    candidates = pl.concat(
        [target, incoming],
        how="vertical_relaxed",
    )

    return latest_events(candidates)
```

A production implementation should also apply explicit delete semantics and avoid loading an enormous target into Python memory when the target size makes that inappropriate.

---

# 44. Python Delete Handling

Separate tombstones:

```python
active = incoming.filter(
    ~pl.col("is_deleted")
)

deleted_keys = (
    incoming
    .filter(pl.col("is_deleted"))
    .select("order_id")
    .unique()
)
```

Remove deleted target keys:

```python
remaining = target.join(
    deleted_keys,
    on="order_id",
    how="anti",
)
```

Then merge active records.

However, deletion must also obey version ordering.

An older delete must not remove newer active state.

---

# 45. PostgreSQL Merge for Orders

A staging table can be merged:

```sql
MERGE INTO silver_orders AS target
USING staged_orders AS source
ON target.order_id = source.order_id

WHEN MATCHED
     AND source.sequence > target.sequence
     AND source.is_deleted = TRUE
THEN DELETE

WHEN MATCHED
     AND source.sequence > target.sequence
     AND source.is_deleted = FALSE
THEN UPDATE SET
    status = source.status,
    amount = source.amount,
    sequence = source.sequence,
    event_id = source.event_id

WHEN NOT MATCHED
     AND source.is_deleted = FALSE
THEN INSERT (
    order_id,
    status,
    amount,
    sequence,
    event_id
)
VALUES (
    source.order_id,
    source.status,
    source.amount,
    source.sequence,
    source.event_id
);
```

The incoming staging data should already have one deterministic winner per business key.

---

# 46. Double-Run Test

Run:

```text
load(batch)
```

then:

```text
load(batch)
```

Compare:

```text
target_after_first
target_after_second
```

Require semantic equality.

Then compare against the reference:

```text
pipeline_result == reference_result
```

This tests both:

```text
idempotency
correctness
```

---

# 47. Simulated Crash Test

Simulate:

```text
batch
 ↓
partial processing
 ↓
CRASH
 ↓
retry
```

Requirement:

```text
final target after crash + retry
=
clean target from complete run
```

If it differs, investigate:

- non-idempotent writes;
- incorrect transaction boundaries;
- duplicate target rows;
- stale updates;
- incorrect delete handling;
- incomplete partial-output cleanup;
- incorrect version selection.

---

# 48. Testing and Correctness

At minimum test:

| Scenario | Invariant |
|---|---|
| Exact duplicate | One logical record remains |
| Business-key duplicate | One winner per key |
| Version selection | Highest valid version wins |
| Tie | Same winner every run |
| Delete | Correct delete/soft-delete state |
| Out-of-order update | Older version cannot overwrite newer |
| Retry | Same final target state |
| Partial failure | Retry converges to clean result |
| Empty input | Valid target remains |
| Duplicate-only input | No unintended changes |
| Large target | Target-side work is appropriately bounded |

---

# 49. Common Buggy Implementation: `unique()`

Bad:

```python
df.unique()
```

Why it fails:

```text
101 | pending | v10
101 | paid    | v11
```

are not exact duplicates.

If the target needs one current row, `unique()` alone does not define the winner.

Fix:

```text
business key
+
version ordering
+
tie-breaker
```

---

# 50. Common Bug: Latest by Load Time

Bad:

```sql
ORDER BY loaded_at DESC
```

when a reliable source sequence exists.

Example:

```text
v12 arrives at 10:00
v11 arrives at 10:05
```

Load time chooses v11 incorrectly.

Fix:

```text
source sequence
```

or a reliable source `updated_at`.

---

# 51. Common Bug: No Version Guard

Bad:

```sql
WHEN MATCHED
THEN UPDATE
```

Any incoming row can overwrite the target.

Fix:

```sql
WHEN MATCHED
AND source.sequence > target.sequence
THEN UPDATE
```

---

# 52. Common Bug: Append Mutable Entities

Bad:

```python
target = pl.concat([target, incoming])
```

for a current-state customer target.

Result:

```text
customer 42 | old address
customer 42 | new address
```

Fix:

```text
merge/upsert
```

or use an intentionally historical model.

---

# 53. Common Bug: No Deterministic Tie-Breaker

Bad:

```sql
ROW_NUMBER() OVER (
    PARTITION BY order_id
    ORDER BY updated_at DESC
)
```

when timestamps can tie.

Fix:

```sql
ROW_NUMBER() OVER (
    PARTITION BY order_id
    ORDER BY
        updated_at DESC,
        event_id DESC
)
```

---

# 54. Common Bug: Only Batch Deduplication

Incoming:

```text
101 | v11
```

Target:

```text
101 | v12
```

The batch is internally unique, but the target is newer.

A blind update can regress state.

Fix:

```text
target reconciliation
+
version guard
```

---

# 55. Common Bug: Whole-Table Merge

Incoming:

```text
10,000 rows
```

Target:

```text
5 billion rows
```

Scanning the whole target is usually wasteful.

Investigate:

```text
partition predicates
clustering/indexing/data organization
incoming scope
batching
```

Measure the result.

---

# 56. Observability

Useful load metrics:

- input row count;
- duplicate row count;
- unique key count;
- inserted rows;
- updated rows;
- deleted rows;
- rejected rows;
- version conflicts;
- merge duration;
- target rows affected.

## Why they matter

A sudden duplicate count can reveal replay or upstream delivery problems.

A sudden version-conflict spike can indicate stale or replayed records.

Unexpectedly high target rows affected can indicate a bad match condition.

Merge duration should be compared with:

```text
input size
target size
partitions touched
```

This topic focuses on merge correctness metrics rather than full observability, lineage, or governance.

---

# 57. Senior Data Engineer Reasoning

Before writing code, ask:

```text
What is the grain?
What is the business key?
Is the source immutable or mutable?
What defines the latest version?
Can updates arrive out of order?
Can deletes occur?
Can the same batch be replayed?
What happens on partial failure?
What is the target size?
Can the target be partition-pruned?
How will idempotency be proven?
```

These questions come first because implementation cannot repair an undefined data contract.

---

# 58. Production Architecture

```text
Bronze / CDC / Source
        ↓
       Read
        ↓
    Normalize
        ↓
Batch Deduplication
        ↓
 Version Selection
        ↓
 Quality Validation
        ↓
      Staging
        ↓
MERGE / Overwrite / Append
        ↓
      Target
        ↓
 Reconciliation
```

Responsibilities:

| Stage | Responsibility |
|---|---|
| Read | Obtain source data |
| Normalize | Standardize representation |
| Batch dedupe | Remove incoming ambiguity |
| Version selection | Determine winner |
| Validation | Enforce known contracts |
| Staging | Provide controlled load boundary |
| Merge/load | Apply target state |
| Reconciliation | Verify expected result |

This architecture extends Topic 01 rather than replacing it.

---

# 59. Architecture Exercise 1 — Mutable Customer CDC

## Problem

A customer target receives:

```text
customer_id
name
email
status
sequence
is_deleted
```

through CDC.

Events can be replayed and arrive out of order.

## Reasoning

Target grain:

```text
one row per customer
```

Business key:

```text
customer_id
```

Version:

```text
sequence
```

Candidate strategy:

```text
merge + version guard + delete handling
```

## Model architecture

```text
CDC
 ↓
batch dedupe
 ↓
latest sequence per customer
 ↓
validation
 ↓
staging
 ↓
MERGE
 ↓
customer target
```

---

# 60. Architecture Exercise 2 — Daily Orders With 3% Duplicates

## Problem

A daily batch contains 3% duplicate events.

The target is partitioned by order date.

## Reasoning

Ask:

```text
Does the target represent events?
Does it represent current state?
Can the complete daily result be recomputed?
```

If the target is a deterministic daily aggregate:

```text
partition overwrite
```

may be natural.

If it is mutable current state across many dates:

```text
merge
```

may be more appropriate.

The target contract decides.

---

# 61. Architecture Exercise 3 — Out-of-Order Merge

## Problem

Target:

```text
order 101 → v13
```

Incoming:

```text
order 101 → v11
```

## Model solution

Do not update.

```text
11 > 13
```

is false.

The version guard preserves v13.

---

# 62. Architecture Exercise 4 — Crash After Partial Writes

## Problem

A large batch partially affects the target and then the worker crashes.

## Reasoning

Ask:

```text
What is durable?
Can the operation be replayed?
Is the write transactional?
Can the target identify already-applied state?
```

## Model solution

Use an idempotent load design:

- transactional merge where supported;
- atomic partition replacement where appropriate;
- version-aware reconciliation;
- controlled staging;
- explicit crash/retry testing.

---

# 63. Architecture Exercise 5 — Rapidly Growing Target

## Problem

Target grows:

```text
100M → 1B → 5B rows
```

Incoming batch remains:

```text
10M rows/day
```

## Reasoning

An unrestricted merge may increasingly scan unrelated target data.

Investigate:

```text
partition predicates
clustering/indexing/data organization
batch size
incoming scope
```

Measure:

```text
rows scanned
partitions scanned
merge duration
rows affected
```

Then verify correctness has not changed.

---

# 64. Mini Implementation Exercises

## Exercise 1 — Exact duplicate removal

Input:

```text
101 | paid
101 | paid
102 | pending
```

Solution:

```python
deduped = df.unique()
```

Use this only when exact equality defines duplication.

## Exercise 2 — Business-key deduplication

Input:

```text
101 | pending | 10
101 | paid    | 11
```

Solution:

```python
result = (
    df
    .sort(
        ["order_id", "sequence"],
        descending=[False, True],
    )
    .group_by("order_id")
    .first()
)
```

## Exercise 3 — Latest version

Use source `updated_at`:

```python
result = (
    df
    .sort(
        ["order_id", "updated_at"],
        descending=[False, True],
    )
    .group_by("order_id")
    .first()
)
```

Document why the timestamp is trusted.

## Exercise 4 — Deterministic tie-breaking

```python
result = (
    df
    .sort(
        ["order_id", "updated_at", "event_id"],
        descending=[False, True, True],
    )
    .group_by("order_id")
    .first()
)
```

## Exercise 5 — Tombstone handling

Use an anti-join for deleted keys, then merge active rows. Apply version guards to the deletion itself.

## Exercise 6 — Python merge

Concatenate target and incoming winners and select the deterministic winner per key. For huge targets, push the work into an analytical/database engine.

## Exercise 7 — SQL merge

```sql
MERGE INTO target AS t
USING source AS s
ON t.order_id = s.order_id
WHEN MATCHED
     AND s.sequence > t.sequence
THEN UPDATE SET
    status = s.status,
    sequence = s.sequence
WHEN NOT MATCHED
THEN INSERT (
    order_id,
    status,
    sequence
)
VALUES (
    s.order_id,
    s.status,
    s.sequence
);
```

## Exercise 8 — Version guard

Target:

```text
101 | v13
```

Incoming:

```text
101 | v11
```

Expected:

```text
target remains v13
```

## Exercise 9 — Idempotency proof

Run a batch twice and compare final target state. Then repeat after a simulated partial failure.

## Exercise 10 — Performance optimization

A merge scans the entire target.

Investigate:

```text
partition predicates
clustering/indexing/data organization
batch size
incoming scope
```

Measure before and after.

---

# 65. Trade-offs

| Strategy | Simplicity | Mutable data | Retry safety | Typical use |
|---|---|---|---|---|
| Append | High | Weak unless history is intended | Low without dedupe | Immutable events |
| Partition overwrite | High for bounded partitions | Good within partition | Often strong | Daily aggregates |
| Merge | Moderate | Strong | Strong when designed correctly | Mutable entities |
| Delete + insert | Moderate | Good for bounded regions | Depends on atomicity | Corrected partitions |
| Full refresh + swap | Conceptually simple | Strong | Strong when swap is safe | Small/rebuildable tables |

Do not turn this into a universal ranking.

Selection depends on:

```text
data semantics
+
target size
+
failure behavior
+
performance
+
operational requirements
```

---

# 66. Debugging Workflow

Use this sequence:

```text
1. Identify target grain
2. Identify business key
3. Inspect duplicate records
4. Determine source version semantics
5. Check tie-breaking
6. Inspect incoming vs target
7. Check merge condition
8. Check delete handling
9. Check version guard
10. Re-run against a known reference
11. Measure target-side work
```

## Step 1 — Grain

Write:

```text
One row represents ______.
```

## Step 2 — Business key

Write:

```text
Business key = ______.
```

## Step 3 — Duplicate inspection

Group incoming records by the key.

## Step 4 — Version semantics

Determine whether the source provides:

```text
sequence
log position
updated_at
```

## Step 5 — Tie-breaking

Check whether versions can tie.

## Step 6 — Incoming vs target

Compare:

```text
incoming.version
target.version
```

## Step 7 — Merge condition

Verify the match key.

## Step 8 — Delete handling

Verify tombstones follow the same version rules.

## Step 9 — Version guard

Verify older data cannot regress state.

## Step 10 — Reference

Compare with an independently written reference.

## Step 11 — Performance

Inspect target-side scanning and rows affected.

---

# 67. Production Checklist

```text
[ ] Target grain is explicitly defined
[ ] Business key is explicitly defined
[ ] Duplicate sources are understood
[ ] Exact vs business-key duplicates are distinguished
[ ] Version semantics are documented
[ ] Winning version is deterministic
[ ] Tie-breaking is deterministic
[ ] Deletes/tombstones are handled
[ ] Correct load strategy is selected
[ ] Batch deduplication is implemented
[ ] Target-side conflicts are handled
[ ] Out-of-order updates are protected
[ ] Merge is idempotent
[ ] Partial failure behavior is understood
[ ] Retry behavior is tested
[ ] Reference output exists
[ ] Results reconcile with reference
[ ] Target-side work is bounded
[ ] Partition pruning is used where appropriate
[ ] Merge performance is measured
[ ] Operational metrics are available
```

---

# 68. Interview Questions

## Basic

### What is deduplication?

**Model answer:** Deduplication is the process of resolving multiple records that represent the same logical target entity or event according to an explicit grain and identity rule.

### Why do duplicates happen?

**Model answer:** Common causes include at-least-once delivery, retries, overlapping extraction windows, webhook redelivery, CDC replay, partial failures, reruns, and multiple sources.

### What is a business key?

**Model answer:** A business key identifies a logical business entity at the target grain, such as `order_id` for one row per order.

### What is an upsert?

**Model answer:** An upsert inserts a record when its key is absent and updates an existing record when its key is already present, subject to the target's version and business rules.

## Intermediate

### When would you use append instead of merge?

**Model answer:** Append is natural for immutable event history when each row is intended to remain a separate event. Mutable current-state entities usually require reconciliation rather than blind append.

### Why is batch deduplication different from target deduplication?

**Model answer:** Batch deduplication resolves conflicts among incoming records. Target reconciliation determines how incoming records interact with already-persisted state. Both may be required.

### Why is source sequence better than load time?

**Model answer:** Source sequence represents source-side ordering or version semantics, while load time represents when the consumer happened to receive the record. Delayed older records can therefore arrive after newer ones.

## Hard

### How do you make a merge idempotent?

**Model answer:** Define a stable business key, select one deterministic incoming winner per key, compare versions against target state, handle deletes explicitly, and ensure repeated application leaves the same final target state.

### How do you handle out-of-order CDC records?

**Model answer:** Use a reliable source version or log position and guard updates/deletes so an incoming version is applied only when it is newer than the target version.

### How do you process deletes?

**Model answer:** Represent them as explicit tombstones or delete events and apply a version-aware hard-delete or soft-delete policy according to the target contract.

## Advanced / Senior

### Design an idempotent load for a mutable orders table.

**Model answer:** Define `order_id` as the business key, stage incoming events, select one deterministic winner per order, apply a version guard, handle tombstones, merge into the target, and test repeated execution and crash/retry against a reference result.

### How would you safely replay a failed merge?

**Model answer:** Determine what effects became durable, then replay the entire logical batch through an idempotent merge or transactional boundary. Never assume that an orchestrator retry alone guarantees correctness.

### How would you optimize a merge against a 5-billion-row target?

**Model answer:** First establish the correctness contract. Then restrict target-side work using partition predicates and suitable data organization, consider clustering/indexing where supported, batch appropriately, and measure rows scanned, partitions touched, duration, and rows affected.

### How would you prove correctness after a two-year historical reload?

**Model answer:** Use deterministic transformations and version selection, build a trusted reference for representative partitions, reconcile keys/counts/versions/deletes, rerun selected intervals, and verify that repeated execution produces the same logical state.

---

# 69. Final Review Questions

Before moving to Topic 03, answer these without looking:

1. Why are duplicates normal in production Data Engineering?
2. What is the difference between an exact duplicate and a business-key duplicate?
3. Why can two different rows represent versions of the same entity?
4. What is the target grain of a current-state orders table?
5. What is its business key?
6. When is append appropriate?
7. When is partition overwrite appropriate?
8. When is merge appropriate?
9. When can delete + insert be useful?
10. When can full refresh with swap be attractive?
11. Why is batch deduplication different from target reconciliation?
12. Why is source sequence better than load time?
13. Why is deterministic tie-breaking required?
14. How should deletes and tombstones be handled?
15. What makes a merge idempotent?
16. How would you prove idempotency after partial failure?
17. How does a version guard prevent stale updates?
18. Why do whole-table merges become expensive?
19. How does partition pruning reduce merge work?
20. What are the trade-offs of batching?
21. What is a deduplication window?
22. How would you design a 3%-duplicate CDC orders load?
23. How would you test a crash followed by retry?
24. How would you compare Python merge behavior with PostgreSQL `MERGE`?
25. What questions should a senior engineer ask before implementation?

---

# 70. Scope Boundary

This chapter focuses on:

```text
Deduplication
Merge-Based Loads
Version Selection
Delete Handling
Idempotency
Out-of-Order Protection
Merge Performance
```

Later Module 2.12 topics cover:

```text
Incremental processing and backfills
Late-arriving data and reprocessing windows
Hashing
Reference-data enrichment
Metadata/config-driven pipelines
Checkpoints and resumability
dbt
Streaming
```

Those topics may depend on the patterns here, but they are intentionally not taught in depth in this chapter.

---

# 71. Final Mental Model

Correct deduplication is not:

```text
"remove duplicate rows"
```

It is:

```text
Define the grain
        ↓
Define the business key
        ↓
Understand source delivery semantics
        ↓
Identify versions
        ↓
Choose the winning version deterministically
        ↓
Choose the correct load strategy
        ↓
Handle deletes
        ↓
Protect against stale updates
        ↓
Make the load idempotent
        ↓
Prove correctness
        ↓
Measure performance
```

The senior-level habit is to reason about correctness before implementation.

If you cannot answer:

```text
What is the grain?
What is the key?
Which version wins?
What happens on retry?
What happens if data arrives out of order?
What happens on delete?
What happens after partial failure?
How much target data must be scanned?
```

then the merge is not yet fully designed.

---

# 72. Exit Criteria

```text
[ ] I can explain why duplicates occur in production pipelines.
[ ] I can distinguish exact, business-key, and version duplicates.
[ ] I can identify the correct business key.
[ ] I can choose among append, overwrite, merge, delete+insert, and full refresh.
[ ] I can deduplicate within a batch.
[ ] I can reason about target-side duplicates.
[ ] I can select the correct winning version.
[ ] I can implement deterministic tie-breaking.
[ ] I can handle deletes and tombstones.
[ ] I can implement a merge using Python/Polars/DuckDB.
[ ] I can implement a database MERGE.
[ ] I can protect against out-of-order updates.
[ ] I can prove idempotency.
[ ] I can reason about partial failure and retry.
[ ] I can optimize target-side merge work.
[ ] I can explain partition pruning and batching.
[ ] I can design tests for correctness.
[ ] I can debug incorrect deduplication.
[ ] I can explain the design in a senior Data Engineering interview.
[ ] I can design a production-safe deduplication and merge pipeline.
```

---

# 73. One-Sentence Principle

> **Production deduplication is not about deleting repeated rows; it is about defining logical identity, selecting the correct version deterministically, applying the right load strategy, protecting against stale updates, and proving that retries converge to the same correct target state.**
