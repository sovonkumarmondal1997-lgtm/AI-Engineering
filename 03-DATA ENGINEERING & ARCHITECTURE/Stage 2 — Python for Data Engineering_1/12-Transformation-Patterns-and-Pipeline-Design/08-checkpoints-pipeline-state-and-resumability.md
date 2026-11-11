# Checkpoints, Pipeline State, and Resumability

> **Stage 2 — Python for Data Engineering**  
> **Module 2.12 — Transformation Patterns and Pipeline Design**  
> **Topic 08 — Checkpoints, Pipeline State, and Resumability**

This chapter teaches how production data pipelines maintain durable state, recover from failures, resume safely, and achieve **exactly-once EFFECTS** through idempotent processing.

The learning progression is:

```text
concept
→ why it exists
→ internal mechanics
→ simple example
→ realistic example
→ implementation
→ failure scenarios
→ debugging
→ production design
→ trade-offs
→ exercises
→ interview questions
→ architecture reasoning
```

The central recovery invariant is:

```text
Execute work
    ↓
Produce durable output
    ↓
Validate output
    ↓
Commit checkpoint/state
    ↓
Continue
```

Therefore:

> **state says COMPLETE ⇒ durable output exists and satisfies the required validation.**

## 1. Learning Objectives

By the end of this chapter you should be able to:

- define pipeline state, progress, durability, checkpoint, resume, restart, retry, recovery, and failure;
- distinguish pipeline state from business data and logs;
- design run-level, step-level, partition-level, source-progress, and dependency/invalidation state;
- choose checkpoint granularity and durable state storage;
- explain why checkpoint state must be committed only after durable output;
- build a durable partition ledger;
- implement safe resume/restart/retry behavior;
- connect checkpoints with idempotent effects;
- explain exactly-once execution versus exactly-once effects;
- use advisory locks to prevent conflicting concurrent runs;
- detect stale partitions and invalidate them safely;
- use logic, code, schema, and configuration versions;
- repair inconsistent operational state without destroying audit history;
- separate orchestrator state from pipeline/data correctness state;
- perform state/output reconciliation;
- chaos-test recovery with repeated failure injection;
- design an operational state CLI and observability model;
- defend resumability decisions in production architecture interviews.


## 2. Prerequisites

This topic builds directly on earlier Module 2.12 topics:

- deterministic transformations;
- deduplication and merge-based loads;
- incremental processing;
- backfills;
- late-arriving data and reprocessing windows;
- deterministic hashing;
- safe lookups and enrichment;
- metadata- and configuration-driven pipelines.

The dependency chain is:

```text
01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09
```

A useful distinction is:

```text
Idempotency:
"What happens if the same work runs again?"

Checkpointing:
"How does the system know what is safely complete?"
```

Reliable recovery needs both.


## 3. What Is Pipeline State?

Imagine processing 1,000 files. You finish 700 and the worker crashes.

The recovery system needs to answer:

> Which 700 are safely complete, and which 300 still require work?

A temporary variable such as `processed = 700` disappears when the process disappears.

**Pipeline state** is durable operational information that lets the system reconstruct processing progress and validity.

### Key terms

| Term | Meaning |
|---|---|
| State | Durable information about processing condition/progress |
| Progress | How far execution has advanced |
| Durable | Survives process/worker failure |
| Checkpoint | Durable marker representing safely completed work |
| Resume | Continue from a safely committed point |
| Restart | Execute the affected work again |
| Retry | Make another attempt |
| Recovery | Return the pipeline to a correct operational state |
| Failure | Execution stops or produces an unusable/incomplete result |

### State versus a log

A log might contain:

```text
processed partition 2026-01-03
```

A checkpoint record can contain:

```text
dataset=orders
partition=2026-01-03
status=completed
row_count=1284312
logic_version=v7
run_id=run-123
completed_at=...
```

A log describes an event.

State represents a machine-readable assertion that recovery logic can query.

### State versus business data

```text
BUSINESS DATA
-------------
order_id
customer_id
amount
order_date

PIPELINE STATE
--------------
dataset
partition
run_id
status
row_count
logic_version
configuration_version
timestamps
error
```

Business data describes what happened in the business.

Pipeline state describes what the processing system has safely accomplished.

Good state should be:

- durable;
- queryable;
- auditable;
- consistent;
- recoverable;
- protected from accidental corruption.


## 4. Why Production Pipelines Need Durable State

A small script can process a dataset from beginning to end without persistent state.

A production pipeline may process:

- millions or billions of records;
- hundreds or thousands of partitions;
- multiple workers;
- retries;
- worker crashes;
- late data;
- historical backfills;
- changing transformation logic;
- multiple concurrent triggers.

Without durable state, a failure can force the system to rediscover progress.

For example:

```text
30 daily partitions

failure on partition 29
        ↓
without partition state
        ↓
rebuild all 30

with partition state
        ↓
partitions 1–28 = completed
partition 29 = failed
partition 30 = pending
        ↓
retry 29
process 30
```

Durable state reduces unnecessary recomputation and makes recovery explicit.

But state alone does not make retries safe.

If a retry appends the same records again, duplicates can still occur.

Therefore:

> **Durable state tells you what work is believed complete; idempotent effects make repeated work safe.**


## 5. Pipeline State — What Should Be Persisted?

Production state commonly includes:

| State | Example | Why it matters |
|---|---|---|
| Watermark | `2026-10-02T18:00Z` | Source progress |
| Source cursor | `offset=938221` | CDC/event progress |
| Processed-file registry | `file-123.parquet` | File-level recovery |
| Processed-object registry | `s3://.../part-001` | Object-level recovery |
| Partition status | `completed` | Partition recovery |
| Step status | `validate=completed` | Multi-step recovery |
| Run status | `failed` | Run-level operations |
| Row count | `1284312` | Reconciliation |
| Output location | `silver/orders/date=...` | Durable-effect identification |
| Fingerprint/checksum | hash | Optional output verification |
| Logic version | `v7` | Rebuild decisions |
| Configuration version | `config-42` | Reproducibility |
| Schema version | `orders-v5` | Contract context |
| Timestamps | `started_at` | Operational timing |
| Error status | error message/code | Diagnosis |
| Retry count | `3` | Reliability signals |
| Run ID | `run-123` | Ownership/audit |
| Dataset ID | `orders` | Scope |
| Partition ID | `2026-01-03` | Work unit |
| Dependency info | upstream partitions | Invalidation |

State should not become an arbitrary dumping ground. Persist information that supports correctness, recovery, observability, or auditability.


## 6. Types of Pipeline State

### A. Run-level state

A run record describes one execution:

```text
run_id
pipeline_name
logical_start
logical_end
environment
status
started_at
completed_at
configuration_version
```

### B. Step-level state

A multi-step pipeline can record:

```text
extract      → completed
transform    → completed
validate     → completed
load         → running
```

### C. Partition-level state

The partition is often the most useful recovery unit:

```text
dataset
partition
status
row_count
logic_version
run_id
started_at
completed_at
updated_at
error_message
```

### D. Source-progress state

Examples:

```text
watermark
offset
cursor
file/object identifier
```

### E. Dependency/invalidation state

A previously completed output can become stale:

```text
upstream correction
      ↓
silver partition affected
      ↓
gold partition affected
```

State therefore describes both **progress** and, when designed appropriately, **validity**.


## 7. Checkpoints — Fundamentals to Advanced

A checkpoint is a durable marker representing safely completed work.

### Checkpoint granularity

Common levels:

- file;
- batch;
- step;
- partition;
- run.

### Fine-grained checkpoints

Advantages:

- precise recovery;
- less recomputation.

Costs:

- more metadata;
- more writes;
- more state-management complexity.

### Coarse-grained checkpoints

Advantages:

- simpler;
- less metadata;
- fewer state writes.

Costs:

- more recomputation after failure.

### Example

Suppose one daily partition takes six hours.

A daily checkpoint may be too coarse if the pipeline can safely divide work into smaller independent units.

But if each partition takes only 30 seconds, file-level checkpoints may add more operational complexity than they save.

Choose granularity from:

```text
work duration
failure probability
recompute cost
state-store capacity
correctness requirements
operational complexity
```

There is no universal checkpoint frequency.


## 8. Resume vs Restart

### Resume

Resume means:

> Continue from the last safely committed point.

### Restart

Restart means:

> Run the affected work again.

### Retry

Retry is another attempt after failure.

### Recompute

Recompute intentionally rebuilds the result.

### Invalidate and rebuild

Used when a previously completed result is no longer trustworthy or current.

Example:

```text
A = completed
B = completed
C = failed
D = pending
E = pending
```

A safe recovery might retry C and process D/E.

But a checkpoint must not be trusted blindly.

If output for A is missing despite `completed`, the system must reconcile the state/output mismatch before skipping A.

The correct recovery unit is a design choice. Idempotent partition processing often makes restart simpler and safer than extremely fine-grained checkpointing.


## 9. Durable State Locations

### Metadata database

A relational metadata database such as PostgreSQL is useful for:

- partition ledgers;
- run records;
- status queries;
- transactional updates;
- constraints;
- indexes;
- advisory locks.

### Object storage

Useful for:

- manifests;
- immutable state artifacts;
- large metadata objects;
- durable markers.

Trade-offs include less convenient transactional updates and operational queries.

### Durable metadata tables

A database or analytical platform can host state tables when SQL access and durable storage are already available.

### Orchestrator-managed state

An orchestrator can track:

- task status;
- dependencies;
- retries;
- scheduling.

That is useful, but it should not automatically become the sole source of truth for data correctness.

### Pipeline-owned state

Pipeline state may contain:

- watermarks;
- processed partitions;
- output validity;
- logic versions;
- data-specific checkpoints.

### Why memory is insufficient

This:

```python
completed_partitions = {
    "2026-01-01",
    "2026-01-02",
}
```


is lost when the worker exits.

Memory is execution state.

It is not durable pipeline state.

### Comparison

| Location | Durability | Queryability | Concurrency | Typical use |
|---|---|---|---|---|
| Metadata DB | High | High | Strong | Ledger/run state |
| Object storage | High | Medium | Depends on design | Durable artifacts |
| Metadata table | High | High | Good | Operational state |
| Orchestrator | High | High | Strong | Task execution |
| In-memory | None after failure | Local | Local | Temporary execution |


## 10. Checkpoint Commit Order — Critical Concept

The unsafe sequence is:

```text
1. Process partition
2. Mark checkpoint COMPLETE
3. Write output
4. Crash
```

The ledger says:

```text
COMPLETE
```

but output does not exist or is incomplete.

A later run may skip the partition.

### Safer sequence

```text
1. Start partition
2. Process partition
3. Write durable output
4. Validate output
5. Commit checkpoint
6. Mark partition complete
```

The invariant is:

```text
COMPLETE
    ⇒
durable output exists
    AND
required validation passed
```

### Safe Python structure

```python
def process_partition(partition, context, ledger):
    ledger.mark_running(
        dataset=context.dataset,
        partition=partition,
        run_id=context.run_id,
    )

    rows = transform_partition(partition, context)

    write_durable_output(
        dataset=context.dataset,
        partition=partition,
        rows=rows,
    )

    validate_output(
        dataset=context.dataset,
        partition=partition,
    )

    ledger.mark_completed(
        dataset=context.dataset,
        partition=partition,
        run_id=context.run_id,
        row_count=len(rows),
        logic_version=context.logic_version,
    )
```


If the worker crashes after output but before checkpoint, the next attempt must safely handle the existing output. That is the key handoff between checkpointing and idempotency.


## 11. Idempotency + Checkpoints

Checkpointing alone does not guarantee correctness.

Consider:

```text
attempt 1 → write output → crash
attempt 2 → write output again
```

If the second write appends identical records, duplicates occur.

The repeated operation must therefore be safe through:

- partition overwrite;
- merge/upsert;
- deterministic deduplication;
- another explicitly idempotent effect.

The core relationship is:

```text
At-least-once execution
        +
Idempotent effects
        =
Exactly-once EFFECTS
```

This does not mean the function physically executed exactly once.

### Exactly-once execution

```text
the processing operation runs once
```

### Exactly-once effects

```text
multiple attempts may occur,
but the externally visible final effect is correct once
```

Example:

```text
run 1 → overwrite partition P → crash after output
run 2 → overwrite partition P → complete
```

The transformation ran twice.

The final partition can still contain exactly the intended result.

Checkpointing answers:

> What do we believe is complete?

Idempotency answers:

> What happens if we need to do it again?


## 12. Partition Ledger

A partition ledger is a durable operational record of processing progress.

### Conceptual schema

```sql
CREATE TABLE partition_ledger (
    dataset TEXT NOT NULL,
    partition_key TEXT NOT NULL,
    status TEXT NOT NULL,
    row_count BIGINT,
    logic_version TEXT,
    run_id TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    updated_at TIMESTAMP,
    error_message TEXT,
    PRIMARY KEY (dataset, partition_key)
);
```


### Column meanings

| Column | Meaning |
|---|---|
| `dataset` | Dataset identity |
| `partition_key` | Recovery unit |
| `status` | Current state |
| `row_count` | Reconciliation signal |
| `logic_version` | Transformation version |
| `run_id` | Execution that owns/created state |
| `started_at` | Start time |
| `completed_at` | Completion time |
| `updated_at` | Last state mutation |
| `error_message` | Diagnostic information |

### Useful statuses

```text
pending
running
completed
failed
stale
invalidated
```

The ledger is an operational record. The target output remains the business-data result.

### State transition

```text
pending
  ↓
running
  ↓
completed

running
  ↓
failed
  ↓
retry
  ↓
running
  ↓
completed

completed
  ↓
stale
  ↓
running
  ↓
completed
```


## 13. Hands-On Implementation

The practical learning example uses a daily orders transformation.

```text
source orders
     ↓
extract
     ↓
transform
     ↓
daily partition
     ↓
durable output
     ↓
validation
     ↓
partition ledger
```

Example partitions:

```text
orders/
    2026-01-01
    2026-01-02
    2026-01-03
    2026-01-04
    2026-01-05
```

### Run context

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RunContext:
    run_id: str
    dataset: str
    logical_start: str
    logical_end: str
    environment: str
    configuration_version: str
    logic_version: str
```


### Partition state

```python
from dataclasses import dataclass
from enum import Enum


class Status(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STALE = "stale"
    INVALIDATED = "invalidated"


@dataclass
class PartitionState:
    dataset: str
    partition: str
    status: Status
    row_count: int | None = None
    logic_version: str | None = None
    run_id: str | None = None
    error_message: str | None = None
```


This model is educational and in-memory. Production state must be persisted durably.

### First execution

```text
all partitions = pending
```

The worker:

```text
mark running
→ transform
→ write durable output
→ validate
→ mark completed
```

### Second execution

The planner sees:

```text
completed
```

and skips those partitions only after checking the completion invariant.

### Failed partition

```text
A = completed
B = completed
C = failed
D = pending
```

Recovery:

```text
retry C
process D
```

### Partial failure

If the worker crashes after writing C but before checkpointing C, the next execution must reconcile or safely overwrite C.

That is why partition writes must be idempotent.


## 14. Run Ledger / Run State

Run state describes the overall execution.

### Conceptual schema

```sql
CREATE TABLE pipeline_runs (
    run_id TEXT PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    logical_start TIMESTAMP NOT NULL,
    logical_end TIMESTAMP NOT NULL,
    environment TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    configuration_version TEXT NOT NULL
);
```


One run may contain:

```text
RUN run-123
 ├── partition A → completed
 ├── partition B → completed
 ├── partition C → failed
 ├── partition D → pending
 └── partition E → pending
```

The run can be `failed` while A and B remain safely completed.

This is why run state should not replace partition state.


## 15. Failure and Recovery Scenarios

### Scenario 1 — Crash before output

```text
transform
  ↓
worker dies
  ↓
no durable output
no completion checkpoint
```

Recovery: retry.

### Scenario 2 — Crash after output but before checkpoint

```text
output exists
checkpoint incomplete
```

Recovery:

```text
inspect/reconcile output
→ retry idempotently OR adopt valid output
→ validate
→ checkpoint
```

### Scenario 3 — Checkpoint says complete but output is corrupted

This violates the completion invariant.

Recovery:

```text
detect mismatch
→ invalidate
→ rebuild
→ validate
→ complete
```

### Scenario 4 — Worker killed during transformation

No durable effect should be assumed. Retry the partition.

### Scenario 5 — Partial run

Some partitions complete while others fail. The ledger identifies remaining work.

### Scenario 6 — Repeated retry

Run the same partition many times.

The final result should converge to the same correct output.

### Scenario 7 — Concurrent runs

Two workers see `pending` simultaneously.

Without coordination, both may write.

Use:

```text
advisory lock
+
idempotent effect
```


## 16. Advisory Locks

### Why locks exist

Two pipeline instances can both observe:

```text
partition = pending
```

and both start work.

Possible outcomes:

- duplicate computation;
- conflicting writes;
- inconsistent ledger updates;
- unnecessary load.

### PostgreSQL advisory lock

A deterministic resource key can be:

```text
orders:2026-01-03
```

Blocking acquisition:

```sql
SELECT pg_advisory_lock(
    hashtext('orders:2026-01-03')
);
```


Non-blocking acquisition:

```sql
SELECT pg_try_advisory_lock(
    hashtext('orders:2026-01-03')
);
```


Unlock:

```sql
SELECT pg_advisory_unlock(
    hashtext('orders:2026-01-03')
);
```


### Python concept

```python
def try_acquire_partition_lock(conn, dataset, partition):
    resource = f"{dataset}:{partition}"

    row = conn.execute(
        "SELECT pg_try_advisory_lock(hashtext(%s));",
        (resource,),
    ).fetchone()

    return bool(row[0])
```


### Lock sequence

```text
derive deterministic resource identity
        ↓
acquire lock
        ↓
verify ownership
        ↓
process idempotently
        ↓
durable output
        ↓
validation
        ↓
checkpoint
        ↓
release lock
```

Locks reduce concurrent conflicts.

They do not eliminate the need for idempotency because workers can still fail and be retried.


## 17. Stale Partitions

A completed partition can become stale when the inputs or logic that produced it change.

Examples:

- upstream correction;
- late-arriving data;
- changed transformation logic;
- changed reference data;
- schema evolution;
- bug fix;
- business-rule change.

Flow:

```text
upstream change
      ↓
affected-partition detection
      ↓
mark stale
      ↓
reprocess
      ↓
validate
      ↓
completed
```

### Example

```text
partition = 2026-01-03
status = completed
logic_version = v4
```

A bug is fixed and current logic becomes v5.

The partition may need:

```text
completed → stale → reprocess → completed(v5)
```

### Late data

A record arriving on January 10 may change January 3.

The state model therefore needs to support targeted reprocessing.

### Reference-data changes

A product mapping or FX rate change can make historical enrichment stale.

### Schema/business-rule changes

These may require broader invalidation depending on their effect.

Staleness is a validity problem, not necessarily a worker-failure problem.


## 18. Logic Versioning

Record the transformation logic version that produced an output.

Example:

| Partition | Logic | Status |
|---|---|---|
| 2026-01-01 | v1 | completed |
| 2026-01-02 | v1 | completed |
| 2026-01-03 | v2 | completed |

Also distinguish:

- logic version;
- code version;
- schema version;
- configuration version.

### Why the distinction matters

A code deployment can contain changes unrelated to a particular transformation.

A configuration change can alter behavior without changing code.

A schema version can change without changing transformation logic.

A useful operational record is:

```text
dataset=orders
partition=2026-01-03
logic_version=v12
code_version=git:abc123
schema_version=orders-v5
configuration_version=config-2026-10-02
status=completed
```


This improves:

- reproducibility;
- incident investigation;
- targeted backfills;
- auditability.


## 19. State Invalidation

Invalidation explicitly says:

> This previously recorded result should no longer be trusted as current.

Prefer:

```text
completed
    ↓
invalidated
    ↓
reprocessing
    ↓
completed
```

or:

```text
completed
    ↓
stale
    ↓
reprocessing
    ↓
completed
```

over blindly deleting the old record.

### Why deletion is dangerous

It can remove evidence of:

- previous result;
- previous run;
- previous logic version;
- reason for rebuild;
- operator action.

### Targeted invalidation

```sql
UPDATE partition_ledger
SET
    status = 'stale',
    error_message = 'Upstream correction requires rebuild',
    updated_at = CURRENT_TIMESTAMP
WHERE dataset = 'orders'
  AND partition_key BETWEEN '2026-01-01' AND '2026-01-07';
```


The processing planner can then select stale partitions for controlled reprocessing.


## 20. State Repair

Operational state can become inconsistent.

Examples:

- incorrect checkpoint;
- manually interrupted run;
- orphaned `running` partition;
- corrupted metadata;
- missing output;
- output exists but state says failed;
- state says completed but output is missing.

### Repair principles

State repair should be:

- deliberate;
- auditable;
- validated;
- minimally scoped;
- reversible where possible.

### Orphaned RUNNING state

```text
status = running
updated_at = many hours ago
worker = absent
```

Do not immediately mark it completed.

Instead:

1. verify worker/run is gone;
2. inspect output;
3. inspect lock state;
4. determine whether output is valid;
5. transition state to a recoverable status;
6. retry safely.

### Output exists but state says FAILED

Inspect and validate the output.

If valid, decide whether the output can be safely adopted into state or whether a deterministic rebuild is simpler.

### State says COMPLETE but output is missing

Treat this as a correctness incident:

```text
detect mismatch
→ invalidate
→ rebuild
→ validate
→ complete
```

Manual repairs should produce an audit trail.


## 21. Orchestrator vs Pipeline State

### Orchestrator state

Usually describes:

- scheduling;
- task dependencies;
- retries;
- task status;
- task timing.

### Pipeline/data state

Usually describes:

- processed partition;
- watermark;
- output validity;
- logic version;
- row count;
- data-specific checkpoint.

The orchestrator may say:

```text
task transform_orders = SUCCESS
```

while the pipeline state says:

```text
orders / 2026-01-03
status = completed
row_count = 1284312
logic_version = v7
output_validated = true
```

The first is execution control.

The second is data correctness evidence.

A useful boundary is:

```text
Orchestrator
    ↓
WHEN and WHAT to run

Pipeline state
    ↓
WHAT DATA WORK is safely complete
```

Do not automatically create two competing authoritative sources for the same fact.

Define ownership explicitly.


## 22. Exactly-Once Effects

Exactly-once effects are a system property.

Suppose:

```text
process(P) → output(P)
```

The process may execute:

```text
P
P
P
```

but the final durable result should be:

```text
correct output(P)
```

Mechanisms include:

- partition overwrite;
- merge/upsert;
- deterministic transformation;
- idempotent writes;
- transactional commit where appropriate;
- checkpoint after durable validated output.

### Partition overwrite

```text
run 1 → overwrite P
run 2 → overwrite P
run 3 → overwrite P
```

If the transformation is deterministic, repeated attempts converge.

### Merge

A deterministic key allows a merge to update the same business record instead of appending another copy.

### Critical distinction

```text
exactly-once execution
```

is about how many times code executes.

```text
exactly-once effects
```

is about the final externally visible state.

Production data engineering generally relies on the latter because failures make execution-count guarantees difficult.

### Formula

```text
At-least-once execution
+
Idempotent effects
+
Durable output
+
Correct checkpoint ordering
=
Exactly-once EFFECTS
```


## 23. Chaos Testing

A resumable pipeline should be tested under failures at operation boundaries.

Inject failures:

- before transformation;
- during transformation;
- after transformation;
- after output;
- before checkpoint;
- during retry;
- during concurrent processing.

### 100 randomized failure scenarios

A practical test can repeat 100 scenarios:

```python
for scenario in range(100):
    seed = scenario

    try:
        run_pipeline_with_failure_injection(
            seed=seed,
            failure_points=random_failure_points(seed),
        )
    except SimulatedFailure:
        pass

    recover_until_terminal_state()

    assert_outputs_are_correct()
    assert_checkpoint_invariant()
    assert_no_duplicate_business_records()
    assert_ledger_matches_outputs()
```


### Useful invariants

- no missing completed output;
- no duplicate business records;
- completion state only follows valid durable output;
- completed partitions remain reproducible;
- retries converge;
- ledger and output remain consistent.

Chaos testing is valuable because checkpoint bugs often live in the small interval between two otherwise-correct operations.


## 24. State CLI

A simple operational CLI can expose state and controlled recovery.

Examples:

```text
pipeline state
pipeline state --dataset orders
pipeline state --partition 2026-01-03
pipeline retry --partition 2026-01-03
pipeline invalidate --partition 2026-01-03
pipeline rebuild --partition 2026-01-03
```


### `pipeline state`

Show current state.

### `pipeline state --dataset orders`

Show all partitions and their statuses.

### `pipeline state --partition ...`

Show detailed:

- run ID;
- versions;
- timestamps;
- row count;
- error;
- output information.

### `pipeline retry`

Should:

1. validate eligibility;
2. acquire a lock;
3. process idempotently;
4. validate output;
5. commit state.

### `pipeline invalidate`

Should explicitly record why the state is no longer valid.

### `pipeline rebuild`

Should mean intentional recomputation, not simply another retry.

State tooling turns recovery from an ad hoc database-editing exercise into a controlled operational workflow.


## 25. Observability

At minimum observe:

- current run;
- active partitions;
- completed partitions;
- failed partitions;
- stale partitions;
- invalidated partitions;
- retry counts;
- processing duration;
- row counts;
- checkpoint age;
- state/output mismatches;
- orphaned running partitions.

### Failed partitions

```sql
SELECT dataset, partition_key, run_id, error_message
FROM partition_ledger
WHERE status = 'failed'
ORDER BY updated_at DESC;
```


### Stale partitions

```sql
SELECT dataset, partition_key, logic_version, updated_at
FROM partition_ledger
WHERE status = 'stale'
ORDER BY updated_at;
```


### Orphaned running partitions

```sql
SELECT dataset, partition_key, run_id, started_at, updated_at
FROM partition_ledger
WHERE status = 'running'
  AND updated_at < CURRENT_TIMESTAMP - INTERVAL '2 hours';
```


The two-hour threshold is illustrative. Production thresholds should be based on observed workload duration.

A particularly valuable correctness metric is:

```text
state/output mismatch count
```


## 26. Production Architecture

A production architecture can be modeled as:

```text
                 Scheduler / Orchestrator
                           |
                           v
                      Run Manager
                           |
                           v
                    Partition Planner
                           |
                 +---------+---------+
                 |                   |
                 v                   v
              Worker A           Worker B
                 |                   |
                 +---------+---------+
                           |
                           v
                    Durable Outputs
                           |
                           v
                    Validation Layer
                           |
                           v
                    State / Ledger DB
                           |
                           v
                     Observability
```

### Scheduler / Orchestrator

Controls when execution starts and manages task dependencies.

### Run Manager

Creates run IDs and records logical interval, environment, and versions.

### Partition Planner

Reads durable state and determines which partitions need work.

### Workers

Execute transformations, write durable outputs, validate them, and commit state.

### Durable outputs

May be:

- Parquet partitions;
- database tables;
- warehouse partitions.

### Validation layer

Checks:

- schema;
- row count;
- uniqueness;
- reconciliation;
- business rules.

### State / ledger database

Stores:

- run state;
- partition state;
- versions;
- errors;
- timestamps.

### Observability

Surfaces:

- progress;
- failures;
- stale state;
- state/output mismatches;
- recovery activity.

### Recovery flow

```text
worker crash
   ↓
state remains non-complete
   ↓
planner reads state
   ↓
recovery candidate selected
   ↓
lock acquired
   ↓
idempotent processing
   ↓
durable output
   ↓
validation
   ↓
checkpoint
```


## 27. Production Trade-Offs

### Checkpoint frequency

Fine-grained:

```text
more precision
more metadata
more state writes
```

Coarse-grained:

```text
less metadata
simpler
more recomputation
```

### State-store choice

A relational metadata store gives strong query and concurrency semantics but becomes another production dependency.

Object storage scales well for durable artifacts but is less convenient for highly concurrent transactional state.

### Metadata volume

File-level state can become enormous. Partition-level state is often a more practical abstraction for transformation pipelines.

### Locking

Locks reduce duplicate concurrent work but create contention and require careful lifecycle handling.

### Recompute versus checkpoint

Sometimes recomputation is cheaper and safer than implementing a highly granular checkpoint.

### Auditability

More history improves incident response but increases metadata volume.

The right decision depends on:

```text
failure probability
work duration
recompute cost
state volume
concurrency
correctness requirements
operational complexity
audit requirements
```


## 28. Anti-Patterns

### 1. In-memory checkpoint only

**Problem:** disappears on worker failure.

**Safer:** durable metadata.

### 2. Checkpoint before output

**Problem:** false completion.

**Safer:** output → validation → checkpoint.

### 3. Trusting `completed` without validation

**Problem:** state/output mismatch can cause skipped work.

**Safer:** completion invariant and reconciliation.

### 4. No idempotency

**Problem:** retry creates duplicate effects.

**Safer:** overwrite, merge, or deterministic deduplication.

### 5. Global mutable state

**Problem:** hidden context is hard to reproduce and disappears on failure.

**Safer:** explicit run context and durable state.

### 6. One giant checkpoint

**Problem:** one failure forces excessive recomputation.

**Safer:** appropriate step/partition granularity.

### 7. No partition-level state

**Problem:** large workloads cannot recover precisely.

**Safer:** partition ledger.

### 8. Ignoring concurrent runs

**Problem:** duplicate/conflicting work.

**Safer:** deterministic lock plus idempotency.

### 9. Deleting state to fix problems

**Problem:** destroys audit history.

**Safer:** invalidate and rebuild.

### 10. Mixing business data with operational metadata

**Problem:** unclear semantics and governance.

**Safer:** separate state store.

### 11. No logic version

**Problem:** historical output becomes difficult to explain.

**Safer:** record logic version.

### 12. No stale-state handling

**Problem:** old output remains trusted.

**Safer:** stale/invalidation lifecycle.

### 13. Treating orchestrator success as data correctness

**Problem:** task success does not prove valid output.

**Safer:** pipeline/data state and validation.

### 14. Manual state changes without audit

**Problem:** operators cannot reconstruct what happened.

**Safer:** audited repair commands.

### 15. No recovery testing

**Problem:** checkpoint bugs appear only during incidents.

**Safer:** failure injection and chaos testing.


## 29. Debugging

Use:

```text
SYMPTOM
→ POSSIBLE CAUSES
→ INVESTIGATION
→ FIX
→ PREVENTION
```

### Pipeline says completed but output is missing

**Causes:** early checkpoint, deleted output, metadata corruption.

**Investigation:** inspect ledger history, run ID, output location, versions, timestamps.

**Fix:** invalidate and rebuild.

**Prevention:** enforce checkpoint ordering.

### Partition remains running forever

**Causes:** worker crash, lost heartbeat, unreleased lock.

**Investigation:** inspect worker/run/lock and `updated_at`.

**Fix:** prove ownership is gone, reconcile output, transition to recoverable state.

### Retry creates duplicate rows

**Cause:** non-idempotent write.

**Fix:** overwrite/merge/deduplicate.

### Two runs process the same partition

**Cause:** race condition.

**Fix:** advisory lock.

### Stale data remains after upstream correction

**Cause:** no dependency-aware invalidation.

**Fix:** mark affected partitions stale and reprocess.

### Checkpoint advances too early

**Cause:** state commit occurs before durable output.

**Fix:** reorder operations.

### State and output disagree

**Cause:** partial failure.

**Investigation:** compare ledger, output metadata, and run history.

**Fix:** adopt only validated output or rebuild.

### Recovery skips required work

**Cause:** false completion.

**Fix:** reconcile state against durable output before skipping.


## 30. Mini Case Study — Daily Orders Transformation Pipeline

A production pipeline processes millions of orders into daily partitions.

Requirements:

- daily partitions;
- incremental processing;
- retries;
- worker crashes;
- late-arriving records;
- transformation changes;
- concurrent triggers.

### What state should be stored?

At minimum:

```text
run_id
dataset
partition
status
row_count
logic_version
configuration_version
schema_version
timestamps
error
```

### What is the checkpoint?

The durable completion state for a partition after valid output has been produced and validated.

### What is the partition key?

Assume:

```text
order_date
```

### When is the checkpoint committed?

After:

```text
durable output
→ validation
→ state commit
```

### What happens after a crash?

Read durable state and reconcile ambiguous partitions.

### How are duplicate retries handled?

Use idempotent overwrite/merge/deduplication.

### How are stale partitions detected?

Use:

- upstream changes;
- late-data windows;
- logic versions;
- reference-data versions.

### How are logic changes handled?

Create a new logic version and reprocess the affected historical scope.

### How are concurrent runs prevented?

Acquire a partition-level advisory lock.

### How are exactly-once effects demonstrated?

Run the same partition repeatedly, inject failures at boundaries, compare final output with a clean rebuild, and verify no duplicates or missing records.


## 31. Practice Exercises

### Basic — 1

Define pipeline state.

**Goal:** distinguish durable operational knowledge from temporary variables.

### Basic — 2

Explain checkpoint versus log.

**Goal:** explain machine-readable recovery state.

### Basic — 3

Design a run-level state record.

### Basic — 4

Design a partition-level state record.

### Basic — 5

Explain resume versus restart with ten partitions.

### Basic — 6

Compare three durable state locations.

### Basic — 7

Explain why memory is insufficient.

### Basic — 8

Draw safe checkpoint commit ordering.

### Basic — 9

Explain exactly-once execution versus effects.

### Basic — 10

List five state fields useful during incident debugging.

### Moderate — 11

Implement an in-memory partition state machine.

### Moderate — 12

Create the partition ledger SQL schema.

### Moderate — 13

Implement skip-completed logic with output validation.

### Moderate — 14

Simulate failure before output.

### Moderate — 15

Simulate failure after output but before checkpoint.

### Moderate — 16

Create a deterministic lock identity.

### Moderate — 17

Query failed partitions.

### Moderate — 18

Query stale partitions.

### Moderate — 19

Detect orphaned running partitions.

### Moderate — 20

Design a state/retry/invalidate/rebuild CLI.

### Hard — 21

Implement a five-partition resumable pipeline.

### Hard — 22

Inject failure after output and prove convergence.

### Hard — 23

Compare overwrite and append retry behavior.

### Hard — 24

Introduce a new logic version and identify rebuild candidates.

### Hard — 25

Introduce late data and mark an existing partition stale.

### Hard — 26

Simulate two concurrent workers and protect the partition with an advisory lock.

### Hard — 27

Build a ledger/output reconciliation report.

### Hard — 28

Implement audited invalidation.

### Hard — 29

Design orphaned-running repair.

### Hard — 30

Run 100 randomized failure scenarios and verify invariants.

### Advanced — 31

Design a resumable billion-row partitioned pipeline.

### Advanced — 32

Design a state store for 100,000 partitions.

### Advanced — 33

Design concurrency control for duplicate scheduler triggers.

### Advanced — 34

Design stale invalidation across A → B → C.

### Advanced — 35

Design a logic migration from v5 to v6.

### Advanced — 36

Design state repair while preserving audit history.

### Advanced — 37

Define authoritative ownership between orchestrator state and pipeline state.

### Advanced — 38

Design failure injection at every checkpoint boundary.

### Advanced — 39

Design an authorized, auditable state CLI.

### Advanced — 40

Present and defend a complete resumable transformation architecture.


### Basic — Question 1

**Question:** What is a checkpoint?

**Expected answer:** A durable marker representing safely completed work.

**Explanation:** It is stronger than a log because recovery logic can rely on its semantics.

**Key concepts:** durable state; recovery

**Senior-level insight:** A checkpoint needs a correctness invariant.


### Basic — Question 2

**Question:** Why must pipeline state be durable?

**Expected answer:** Because workers can fail and temporary memory disappears.

**Explanation:** Recovery requires information that survives process failure.

**Key concepts:** durability; recovery

**Senior-level insight:** State is the pipeline's durable memory.


### Basic — Question 3

**Question:** What is resume versus restart?

**Expected answer:** Resume continues from a safe boundary; restart repeats the affected work.

**Explanation:** Both can be correct depending on checkpoint granularity and idempotency.

**Key concepts:** resume; restart

**Senior-level insight:** Restarting an idempotent partition is often simpler than fine-grained internal recovery.


### Basic — Question 4

**Question:** Why commit checkpoint state after output?

**Expected answer:** To prevent state from claiming completion when output does not exist.

**Explanation:** The order protects the completion invariant.

**Key concepts:** commit ordering

**Senior-level insight:** State must describe reality, not intention.


### Basic — Question 5

**Question:** What is exactly-once execution?

**Expected answer:** A guarantee that the operation physically executes exactly once.

**Explanation:** This is distinct from exactly-once effects.

**Key concepts:** execution semantics

**Senior-level insight:** Execution-count guarantees are difficult under failure.


### Basic — Question 6

**Question:** What are exactly-once effects?

**Expected answer:** Repeated attempts converge to one correct externally visible result.

**Explanation:** At-least-once execution plus idempotent effects can provide this property.

**Key concepts:** idempotency; effects

**Senior-level insight:** The final effect matters more than invocation count.


### Basic — Question 7

**Question:** What is a partition ledger?

**Expected answer:** Durable metadata describing processing state for dataset partitions.

**Explanation:** It enables precise recovery and operational inspection.

**Key concepts:** partition state; ledger

**Senior-level insight:** Keep operational state separate from business data.


### Basic — Question 8

**Question:** Why record logic versions?

**Expected answer:** To identify which transformation behavior produced an output.

**Explanation:** Logic changes can make previous outputs stale.

**Key concepts:** versioning; backfills

**Senior-level insight:** Code version and logic version are related but not identical.


### Basic — Question 9

**Question:** What is an advisory lock?

**Expected answer:** A database coordination mechanism for an application-defined resource.

**Explanation:** It can prevent concurrent runs from processing the same partition.

**Key concepts:** concurrency; locking

**Senior-level insight:** Locks complement, not replace, idempotency.


### Basic — Question 10

**Question:** What is a stale partition?

**Expected answer:** A completed partition whose result is no longer current or trustworthy.

**Explanation:** It may become stale after upstream, reference-data, or logic changes.

**Key concepts:** staleness; invalidation

**Senior-level insight:** Stale and failed describe different operational conditions.


### Moderate — Question 11

**Question:** How would you design a partition ledger?

**Expected answer:** Use dataset/partition identity, status, run ID, row count, versions, timestamps, and error context.

**Explanation:** Those fields support recovery, reconciliation, and auditability.

**Key concepts:** ledger design

**Senior-level insight:** Only persist fields that answer operational questions.


### Moderate — Question 12

**Question:** Why is a log insufficient for recovery?

**Expected answer:** Logs are event records; recovery needs structured durable state.

**Explanation:** Free-form messages are not a safe correctness interface.

**Key concepts:** logs versus state

**Senior-level insight:** State should be machine-queryable.


### Moderate — Question 13

**Question:** What happens after a crash between output and checkpoint?

**Expected answer:** Output may exist while state is incomplete, so recovery must reconcile or retry idempotently.

**Explanation:** The retry cannot blindly append the same effect.

**Key concepts:** partial failure; idempotency

**Senior-level insight:** This is a fundamental failure window.


### Moderate — Question 14

**Question:** How do you prevent duplicate concurrent processing?

**Expected answer:** Use a deterministic lock and idempotent writes.

**Explanation:** The lock prevents concurrent ownership while idempotency protects retries.

**Key concepts:** locking; idempotency

**Senior-level insight:** Assume duplicate triggers can happen.


### Moderate — Question 15

**Question:** Why is completed status not sufficient?

**Expected answer:** State can disagree with output after partial failure or corruption.

**Explanation:** Completion should imply validated durable output.

**Key concepts:** reconciliation

**Senior-level insight:** Completion is an invariant, not merely a string.


### Moderate — Question 16

**Question:** What should happen after a transformation bug is fixed?

**Expected answer:** Mark affected partitions stale/invalidate them and rebuild under the new logic version.

**Explanation:** Only affected historical scope should be reprocessed where possible.

**Key concepts:** logic version; backfill

**Senior-level insight:** Targeted rebuilds control cost.


### Moderate — Question 17

**Question:** Why separate run and partition state?

**Expected answer:** A run can fail while many partitions succeed.

**Explanation:** Partition state enables precise recovery.

**Key concepts:** run state; partition state

**Senior-level insight:** Aggregate failure must not erase granular progress.


### Moderate — Question 18

**Question:** What belongs in orchestrator state?

**Expected answer:** Scheduling, dependencies, retries, and task execution status.

**Explanation:** These are execution-control concerns.

**Key concepts:** orchestration

**Senior-level insight:** Task success is not automatically data correctness.


### Moderate — Question 19

**Question:** What belongs in pipeline/data state?

**Expected answer:** Watermarks, processed partitions, output validity, versions, and data-specific checkpoints.

**Explanation:** These describe data-processing correctness.

**Key concepts:** pipeline state

**Senior-level insight:** Define one authoritative source for each fact.


### Moderate — Question 20

**Question:** How do you repair an orphaned running partition?

**Expected answer:** Verify the worker is gone, inspect output and locks, transition state to a recoverable condition, then retry safely.

**Explanation:** Never mark it complete just because the worker disappeared.

**Key concepts:** repair; recovery

**Senior-level insight:** Repair must be auditable.


### Hard — Question 21

**Question:** Design exactly-once effects for a daily partition.

**Expected answer:** Use deterministic processing, idempotent overwrite/merge, validation, and checkpoint-after-output.

**Explanation:** Repeated execution must converge to the same result.

**Key concepts:** exactly-once effects

**Senior-level insight:** Prove the property with failure scenarios.


### Hard — Question 22

**Question:** How would you recover after a crash between output and checkpoint?

**Expected answer:** Validate existing output and either adopt it safely or rerun idempotently.

**Explanation:** The ambiguous state is resolved through reconciliation.

**Key concepts:** reconciliation

**Senior-level insight:** Avoid blind state mutation.


### Hard — Question 23

**Question:** How would you design state for 100,000 partitions?

**Expected answer:** Use a durable indexed state store, efficient status queries, bounded metadata growth, and concurrency control.

**Explanation:** State itself needs production capacity planning.

**Key concepts:** scale; metadata

**Senior-level insight:** Checkpoint granularity is a scaling decision.


### Hard — Question 24

**Question:** How do advisory locks interact with retries?

**Expected answer:** Each retry acquires the same deterministic resource lock before processing.

**Explanation:** This prevents concurrent ownership of the same work.

**Key concepts:** locks; retries

**Senior-level insight:** Lock identity should match the protected resource.


### Hard — Question 25

**Question:** How would you invalidate downstream state after an upstream change?

**Expected answer:** Use dependencies to identify affected partitions, mark them stale, and reprocess them.

**Explanation:** Invalidation propagates through data dependencies.

**Key concepts:** lineage; invalidation

**Senior-level insight:** Impact analysis should follow data grain.


### Hard — Question 26

**Question:** Why record configuration version as well as logic version?

**Expected answer:** Configuration can alter behavior without changing application code.

**Explanation:** Reproducibility needs the execution inputs that affect semantics.

**Key concepts:** configuration; reproducibility

**Senior-level insight:** Version the effective execution contract.


### Hard — Question 27

**Question:** How would you detect state/output mismatches?

**Expected answer:** Periodically reconcile ledger records with output metadata and validity checks.

**Explanation:** This catches false completion and orphaned output.

**Key concepts:** reconciliation

**Senior-level insight:** Reconciliation is a control, not merely debugging.


### Hard — Question 28

**Question:** What are trade-offs of fine-grained checkpoints?

**Expected answer:** More recovery precision but more metadata and state-write overhead.

**Explanation:** Checkpointing is an economic design choice.

**Key concepts:** granularity; overhead

**Senior-level insight:** Optimize recovery economics, not checkpoint count.


### Hard — Question 29

**Question:** Why can a partition be stale without being failed?

**Expected answer:** Processing succeeded, but relevant inputs or logic changed later.

**Explanation:** Failure describes execution; staleness describes validity.

**Key concepts:** stale versus failed

**Senior-level insight:** Validity needs its own lifecycle.


### Hard — Question 30

**Question:** How would you chaos-test checkpoint correctness?

**Expected answer:** Inject failures at state-transition boundaries, retry, and verify output/ledger invariants.

**Explanation:** Boundary failures reveal recovery bugs.

**Key concepts:** chaos; invariants

**Senior-level insight:** Success-only tests cannot prove resumability.


### Advanced — Question 31

**Question:** Design a billion-row resumable pipeline.

**Expected answer:** Use partitioning, durable partition state, bounded workers, idempotent outputs, validation, locks, and recovery.

**Explanation:** The recovery unit should avoid rebuilding unrelated data.

**Key concepts:** scale; recovery

**Senior-level insight:** Align processing and recovery units.


### Advanced — Question 32

**Question:** Design a state store for 100,000 partitions.

**Expected answer:** Use a durable relational metadata store with composite identity, status indexes, retention/history strategy, and controlled concurrent updates.

**Explanation:** State is itself a production system.

**Key concepts:** state-store architecture

**Senior-level insight:** Capacity-plan metadata as carefully as data.


### Advanced — Question 33

**Question:** Design concurrency control for multiple triggers.

**Expected answer:** Assign run IDs, plan partition work, acquire deterministic locks, use idempotent effects, and reconcile after crashes.

**Explanation:** Locks and idempotency solve different failure modes.

**Key concepts:** concurrency

**Senior-level insight:** Assume duplicate scheduling events.


### Advanced — Question 34

**Question:** Design stale invalidation for A → B → C.

**Expected answer:** Identify changed A partitions, map affected B partitions, then propagate impact to C using dependency and grain metadata.

**Explanation:** Invalidation is not necessarily one-to-one.

**Key concepts:** lineage; invalidation

**Senior-level insight:** Precise invalidation requires dependency metadata.


### Advanced — Question 35

**Question:** How would you migrate logic from v5 to v6?

**Expected answer:** Identify scope, rebuild idempotently under v6, validate, compare, and record new version state while preserving history.

**Explanation:** A logic migration is a controlled data change.

**Key concepts:** logic migration

**Senior-level insight:** Deployment and historical rebuild are related but distinct.


### Advanced — Question 36

**Question:** How would you repair corrupted state without losing audit history?

**Expected answer:** Record invalidation/repair events, preserve history, rebuild affected partitions, and record the new run/version.

**Explanation:** Deleting state removes evidence.

**Key concepts:** repair; auditability

**Senior-level insight:** Operational history is evidence.


### Advanced — Question 37

**Question:** Should the orchestrator or pipeline own partition correctness?

**Expected answer:** Pipeline/data state should own data correctness; the orchestrator should own scheduling/task execution.

**Explanation:** Task success does not prove valid data output.

**Key concepts:** separation of concerns

**Senior-level insight:** Define authoritative ownership.


### Advanced — Question 38

**Question:** How would you prove a resumable pipeline is safe?

**Expected answer:** Define invariants, inject failures, retry repeatedly, compare with clean rebuilds, and reconcile ledger/output.

**Explanation:** Recovery correctness requires behavioral evidence.

**Key concepts:** invariants; chaos

**Senior-level insight:** Resumability is demonstrated, not asserted.


### Advanced — Question 39

**Question:** What happens if state says COMPLETE but output is missing?

**Expected answer:** Treat it as an invariant violation, invalidate it, investigate, and rebuild.

**Explanation:** Do not continue trusting false completion.

**Key concepts:** completion invariant

**Senior-level insight:** State must describe reality.


### Advanced — Question 40

**Question:** What is the most important checkpoint-design principle?

**Expected answer:** Never commit completion before durable validated output exists.

**Explanation:** This prevents false progress from becoming data loss.

**Key concepts:** commit ordering

**Senior-level insight:** The checkpoint is durable proof, not prediction.


## 32. Architecture Questions

### Architecture 1 — Design a resumable batch-processing system

**Requirements**

- millions of records;
- partitioned processing;
- worker failures;
- retries;
- multiple triggers.

**Assumptions**

Partitions are the recovery unit and effects can be made idempotent.

**State model**

```text
run ledger
partition ledger
logic/configuration/schema versions
```

**Failure model**

Failure can occur before output, after output, or before checkpoint.

**Architecture**

```text
orchestrator
→ run manager
→ partition planner
→ workers
→ durable output
→ validation
→ ledger
```

**Invariant**

```text
completed ⇒ durable validated output
```

**Recovery**

Reconcile ambiguous partitions and retry idempotently.

**Trade-off**

More state gives more recovery precision but increases metadata operations.

### Architecture 2 — Checkpointing for a partitioned lakehouse

Use partition-level state, durable output locations, validation, and atomic/idempotent partition replacement where supported.

### Architecture 3 — State store for 100,000 partitions

Use a durable relational state store with composite identity, status indexes, efficient pending/failed/stale queries, history/retention, and concurrency control.

### Architecture 4 — Worker-crash recovery

Track `running` state and timestamps/ownership. Detect orphaned work, reconcile output, and retry safely. Never promote orphaned `running` directly to `completed`.

### Architecture 5 — Concurrent triggers

Use deterministic partition-level locks plus idempotent writes. Assume duplicate scheduler events.

### Architecture 6 — Stale-partition invalidation

Track dependencies and logic/reference versions. Propagate invalidation to affected downstream partitions, then rebuild and validate.

### Architecture 7 — State repair with audit history

Use explicit `invalidated`/`stale` transitions or an audit history. Preserve the original state and record repair intent.

### Architecture 8 — Exactly-once effects

Combine at-least-once execution with deterministic transformations, idempotent durable effects, validation, and checkpoint-after-output.


## 33. Testing Strategy

Testing must cover more than the happy path.

### Unit tests

Test:

- legal state transitions;
- illegal transitions;
- checkpoint ordering;
- idempotency;
- version decisions;
- stale-state logic.

### Integration tests

Test:

- durable state database;
- durable output;
- retry behavior;
- lock behavior;
- reconciliation.

### Failure tests

Inject:

- crash before transformation;
- crash during transformation;
- crash after output;
- crash before checkpoint;
- concurrent execution.

### Reconciliation tests

Compare:

```text
ledger
vs
output
```

and:

```text
expected partitions
vs
actual partitions
```

### Chaos tests

Run many randomized failures and verify convergence.

| Test type | What it proves |
|---|---|
| Unit | State logic |
| Integration | Durable-system interaction |
| Failure | Boundary recovery |
| Reconciliation | State/output consistency |
| Chaos | Repeated-failure robustness |


## 34. Study Loop

Follow this exact progression:

### 1. Read

Understand state, checkpoints, ledger, idempotency, and recovery.

### 2. Define the run contract

Specify:

```text
inputs
outputs
partition grain
logical interval
state fields
completion invariant
```

### 3. Build

Implement:

```text
process
→ output
→ validate
→ checkpoint
```

### 4. Run twice

Prove repeated execution does not corrupt output.

### 5. Run for the past

Process historical partitions and inspect state.

### 6. Break it

Kill the worker at:

```text
before transform
during transform
after output
before checkpoint
```

### 7. Verify invariants

Prove:

```text
completed
⇒ durable valid output
```

### 8. Change logic and rebuild

Increase `logic_version` and identify partitions requiring reprocessing.

### 9. Write it down

Document the state model, failure model, recovery behavior, invariants, and repair procedures.

### 10. Explain aloud

Explain why checkpointing and idempotency solve different problems.


## 35. Mental Models

> **Checkpoint = durable proof of completed work.**

> **State must describe reality, not intention.**

> **Never advance state before the effect is durable.**

> **At-least-once execution + idempotent effects = exactly-once effects.**

> **Recovery is only safe when retry is safe.**

> **Completed does not mean correct unless the completion invariant is enforced.**

> **Locks prevent conflicting concurrency; idempotency makes retries safe.**

> **A stale result is not necessarily a failed result.**

> **Operational state is evidence about how the system processed data.**

> **The recovery unit should match the processing unit whenever practical.**


## 36. Common Beginner Confusions

| Confusion | Correct distinction |
|---|---|
| Checkpoint vs log | Checkpoint is recovery state; log is an event record |
| Checkpoint vs cache | Checkpoint supports correctness/recovery; cache supports performance |
| State vs business data | State describes processing; business data describes domain events |
| Run state vs partition state | Run summarizes execution; partition tracks work unit |
| Resume vs restart | Resume continues from safe point; restart repeats work |
| Retry vs reprocess | Retry repeats failed work; reprocess intentionally rebuilds |
| Idempotency vs checkpointing | Checkpoint tracks completion; idempotency makes repeats safe |
| Exactly-once execution vs effects | Execution count versus final external state |
| Orchestrator vs pipeline state | Scheduling/task state versus data correctness state |
| Stale vs failed | Validity change versus execution failure |
| Invalidated vs deleted | Explicitly unusable versus removed |
| Logic version vs data version | Transformation behavior versus input/reference version |


## 37. State CLI and Operational Procedures

A state CLI should expose controlled operations rather than encourage arbitrary SQL editing.

### Inspection

```text
pipeline state
pipeline state --dataset orders
pipeline state --partition 2026-01-03
```

### Retry

```text
pipeline retry --partition 2026-01-03
```

Expected behavior:

```text
validate eligibility
→ acquire lock
→ execute idempotently
→ validate
→ checkpoint
```

### Invalidate

```text
pipeline invalidate --partition 2026-01-03
```

Should require a reason and record the operator/action.

### Rebuild

```text
pipeline rebuild --partition 2026-01-03
```

Should explicitly represent intentional recomputation.

Operational state changes should be:

- authorized;
- audited;
- minimally scoped;
- observable.


## 38. Production Review Questions

Before approving a resumable pipeline, ask:

1. What is the recovery unit?
2. Where does durable state live?
3. What exactly does `completed` mean?
4. Can output exist without state?
5. Can state exist without output?
6. What happens if the worker dies after output?
7. What happens if it dies before output?
8. What happens if it dies before checkpoint?
9. Are writes idempotent?
10. Can two runs process the same partition?
11. How is concurrency prevented?
12. How are stale partitions identified?
13. How are logic changes represented?
14. How are state repairs audited?
15. What is the authoritative source for data correctness?
16. How is state/output reconciliation performed?
17. How is chaos testing performed?
18. How does a billion-row backfill recover?
19. What happens when the state store is unavailable?
20. Can the team explain the recovery path without reading implementation details?


## 39. Production Checklist

### State model

- [ ] Pipeline state is explicitly defined
- [ ] Run state is defined
- [ ] Step state is defined where needed
- [ ] Partition state is defined
- [ ] Source progress is defined
- [ ] Dependency/invalidation state is defined

### Durability

- [ ] State survives worker failure
- [ ] State is queryable
- [ ] State is auditable
- [ ] State is protected
- [ ] State store has backup/recovery

### Checkpoint correctness

- [ ] Output is durable before completion
- [ ] Output is validated before completion
- [ ] Completion invariant is documented
- [ ] Ambiguous output/state cases are handled

### Idempotency

- [ ] Partition effects are idempotent
- [ ] Retries are safe
- [ ] Duplicate triggers are safe
- [ ] Final effects converge

### Concurrency

- [ ] Work ownership is explicit
- [ ] Advisory/other locks are appropriate
- [ ] Lock scope is understood
- [ ] Lock failure is handled

### Staleness

- [ ] Logic versions are recorded
- [ ] Configuration versions are recorded
- [ ] Schema versions are recorded
- [ ] Stale partitions can be identified
- [ ] Invalidations are auditable

### Recovery

- [ ] Resume behavior is defined
- [ ] Restart behavior is defined
- [ ] State repair is controlled
- [ ] Orphaned work is detectable
- [ ] State/output reconciliation exists

### Testing

- [ ] Unit tests
- [ ] Integration tests
- [ ] Failure injection
- [ ] Reconciliation tests
- [ ] Chaos tests
- [ ] 100-scenario failure test

### Operations

- [ ] State CLI exists
- [ ] Retry is controlled
- [ ] Invalidate is controlled
- [ ] Rebuild is controlled
- [ ] Observability exists
- [ ] Alerts exist for state/output mismatches


## 40. Exit Criteria

You are ready to move forward when you can independently:

- define pipeline state;
- explain durable state;
- distinguish state from logs;
- design run-level state;
- design step-level state;
- design partition-level state;
- design source-progress state;
- choose checkpoint granularity;
- choose a durable state location;
- explain why in-memory progress is insufficient;
- enforce output → validation → checkpoint ordering;
- explain the completion invariant;
- make processing idempotent;
- explain exactly-once effects;
- design a partition ledger;
- implement resume/retry behavior;
- prevent conflicting concurrent runs;
- use advisory locks appropriately;
- detect stale partitions;
- use logic versions;
- invalidate state safely;
- repair inconsistent state;
- distinguish orchestrator state from pipeline state;
- reconcile state with outputs;
- run failure injection and chaos tests;
- design an operational state CLI;
- observe and debug recovery;
- design a production resumability architecture;
- explain the trade-offs;
- defend the design in an interview.

### Final mental model

```text
Execute work
    ↓
Produce durable output
    ↓
Validate output
    ↓
Commit checkpoint/state
    ↓
Continue
```

When failure occurs:

```text
Failure
  ↓
Read durable state
  ↓
Identify safe completed work
  ↓
Reconcile ambiguous work
  ↓
Acquire lock
  ↓
Retry idempotently
  ↓
Durable output
  ↓
Validation
  ↓
Checkpoint
```

When logic or input data changes:

```text
Change detected
  ↓
Identify affected partitions
  ↓
Mark stale / invalidated
  ↓
Reprocess
  ↓
Validate
  ↓
Record new version
  ↓
Completed
```

The most important principle is:

> **A checkpoint is not merely a record that a worker reached a line of code. It is durable operational evidence that a defined unit of work produced the required valid effect.**

Reliable resumability comes from:

```text
durable state
+
correct checkpoint ordering
+
idempotent effects
+
explicit concurrency control
+
tested recovery behavior
```
