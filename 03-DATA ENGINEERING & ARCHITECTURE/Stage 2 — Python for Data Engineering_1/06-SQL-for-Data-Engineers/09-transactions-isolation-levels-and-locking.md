# 09 — Transactions, Isolation Levels, and Locking

> **Stage 2 — Python for Data Engineering**  
> **Module 2.6 — SQL for Data Engineers**  
> **Topic 09 — Transactions, Isolation Levels, and Locking**  
> **Primary environment:** PostgreSQL 16+  
> **Secondary awareness:** DuckDB, cloud warehouses, lakehouse table formats

---

## 1. Learning Objectives

By the end of this chapter you should be able to:

- explain ACID precisely;
- write transactions with `BEGIN`, `COMMIT`, `ROLLBACK`, and `SAVEPOINT`;
- reason about autocommit and transaction boundaries;
- design atomic batch publication;
- explain PostgreSQL `READ UNCOMMITTED`, `READ COMMITTED`, `REPEATABLE READ`, and `SERIALIZABLE`;
- reproduce and diagnose dirty-read reasoning, non-repeatable reads, phantom/read-set changes, lost updates, and write skew;
- explain MVCC and transaction snapshots;
- distinguish visibility, blocking, and locking;
- use `FOR UPDATE`, `FOR SHARE`, `NOWAIT`, and `SKIP LOCKED`;
- build a concurrent work queue;
- understand serialization failures and retry the complete transaction;
- explain table-level and DDL locking;
- distinguish `lock_timeout` from `statement_timeout`;
- diagnose and prevent deadlocks;
- explain long-running transaction effects on cleanup and operational health;
- use staging-then-apply and staging-then-swap patterns;
- use advisory locks for singleton pipeline coordination;
- explain DuckDB single-writer behavior, warehouse differences, and lakehouse optimistic concurrency;
- debug concurrency using session timelines and assertions;
- design production-safe pipeline transaction boundaries around business invariants.

### The professional questions

For any concurrent workflow, ask:

```text
1. What does A see?
2. What does B see?
3. What can A change?
4. What can B change?
5. Does one block the other?
6. Can both commit?
7. If not, which transaction can fail and why?
8. What should the application/pipeline do after failure?
9. What post-condition proves the final state is correct?
```

---

## 2. Why Transactions Matter in Data Engineering

Transactions matter whenever a pipeline, worker, scheduler, application, dashboard, or migration shares database state with another actor.

### Failure 1 — Half-loaded batch

```text
10,000 rows expected
5,000 inserted
process crashes
```

If the publication was independently committed, downstream readers may observe an incomplete state. A better design is to make the intended publication unit atomic.

### Failure 2 — Lost update

```text
counter = 10

Worker A reads 10 → computes 11
Worker B reads 10 → computes 11
A writes 11
B writes 11
```

Logical expectation: `12`. Actual result can be `11`.

### Failure 3 — Duplicate job execution

```text
scheduler A → daily_customer_load
scheduler B → daily_customer_load
```

Two workers can start the same logical job unless the design coordinates them.

### Failure 4 — Blocking schema change

A long-running transaction can hold state/locks while a deployment runs:

```sql
ALTER TABLE subscriptions
ADD COLUMN source_system TEXT;
```

The DDL can wait behind an incompatible lock.

### Failure 5 — Deadlock

```text
A locks row 1
B locks row 2
A waits for row 2
B waits for row 1
```

This is a circular wait.

### Data Engineering perspective

The core problem is not "how do I use `COMMIT`?"

It is:

> **Which state transitions must become visible together, what concurrent actors exist, and what is the smallest control set that preserves the invariant?**

---

## 3. The Core Mental Model

> **A transaction is a logical unit of work whose changes become visible according to transaction semantics and whose final state is either committed or rolled back.**

Success:

```text
BEGIN
  ↓
change state
  ↓
validate
  ↓
COMMIT
```

Failure:

```text
BEGIN
  ↓
change state
  ↓
failure
  ↓
ROLLBACK
```

Concurrency:

```text
Transaction A
       \
        \
         → shared database state
        /
       /
Transaction B
```

### Atomic operation ≠ entire pipeline in one huge transaction

```text
atomic operation
        ≠
entire pipeline must remain inside one huge transaction
```

A strong production pipeline often looks like:

```text
slow extraction / parsing
        ↓
staging
        ↓
validation
        ↓
short publication transaction
        ↓
commit
```

### Connection to previous topics

This topic builds on Topics 01–08: querying, joins, aggregation, CTEs, windows, set operations, DDL/types, and indexing/plan reading. Those are prerequisites, not re-taught here.

The mental chain is:

```text
Data modification
      ↓
transaction
      ↓
concurrency
      ↓
isolation
      ↓
locks / MVCC
      ↓
pipeline correctness
```

---

## 4. What Is a Transaction?

A transaction groups one or more database operations into a logical unit of work. It may contain one statement or many.

```sql
BEGIN;

UPDATE accounts
SET balance = balance - 100
WHERE account_id = 1;

UPDATE accounts
SET balance = balance + 100
WHERE account_id = 2;

COMMIT;
```

Failure path:

```sql
BEGIN;

UPDATE accounts
SET balance = balance - 100
WHERE account_id = 1;

-- validation or another operation fails

ROLLBACK;
```

The transaction gives you a boundary. It does not, by itself, identify every race condition that can occur inside that boundary.

---

## 5. ACID

### Atomicity

All changes in the transaction become part of committed state together, or the uncommitted attempt is rolled back.

### Consistency

A successful commit preserves the constraints and business invariants actually represented or checked by the database workflow.

Examples:

```text
PRIMARY KEY uniqueness
FOREIGN KEY validity
CHECK constraints
business rules explicitly enforced in transaction logic
```

Avoid: "Consistency means the database is always correct." A rule that is nowhere represented cannot be magically enforced by ACID.

### Isolation

Concurrent transactions interact according to the selected isolation semantics. Isolation controls visibility and concurrent interaction; it does not mean all transactions physically run one at a time.

### Durability

After commit, changes become durable according to the database's configured durability guarantees. Do not make an unqualified claim that committed data can never be lost under every failure model.

---

## 6. Atomicity

Suppose a daily batch contains one million records:

```text
daily batch
→ 1,000,000 rows
```

A useful publication design is:

```text
BEGIN
  load/apply
  validate
  COMMIT
```

On failure:

```text
ROLLBACK
```

The key is the publication boundary, not the total runtime of the pipeline.

A partial target can be dangerous because downstream queries may assume that a committed date represents a complete logical state.

---

## 7. Consistency

A transaction is useful only when its committed result satisfies the required invariants.

Examples:

```text
primary key uniqueness
foreign-key validity
amount >= 0
at most one active job run
at least one doctor remains on call
published target matches validated staging population
```

Some of these are easy database constraints. Others require transaction logic, locking, serialization, or a combination.

### Senior rule

State the invariant explicitly before selecting a transaction control technique.

---

## 8. Isolation

Isolation answers:

> **What can concurrent transactions observe, and how can their operations interact?**

Example:

```text
A reads row
B updates row and commits
A reads row again
```

Possible outcomes differ by isolation level. Therefore isolation affects:

```text
visibility
concurrency
anomalies
blocking
failure/retry behavior
```

---

## 9. Durability

Conceptually:

```text
BEGIN
  ↓
changes
  ↓
COMMIT
  ↓
committed state
```

Durability is a system property involving database configuration and the broader failure/recovery architecture. For Data Engineering, this connects to logging, replication, backup, failover, and recovery expectations.

---

## 10. BEGIN

Start an explicit transaction with:

```sql
BEGIN;
```

Subsequent statements belong to that transaction until `COMMIT` or `ROLLBACK`.

Example:

```sql
BEGIN;

INSERT INTO job_runs(job_name, run_date, status)
VALUES ('daily_customer_load', CURRENT_DATE, 'running');

UPDATE pipeline_state
SET last_started_at = CURRENT_TIMESTAMP
WHERE pipeline_name = 'daily_customer_load';

COMMIT;
```

The transaction should reflect a meaningful state transition, not an arbitrary collection of unrelated work.

---

## 11. COMMIT

Use:

```sql
COMMIT;
```

It finalizes the successful transaction. The changes become committed according to the database's transaction and durability semantics, and transaction-specific state/locks are released as applicable.

Mental model:

```text
uncommitted work
      ↓
    COMMIT
      ↓
committed state
```

---

## 12. ROLLBACK

Use:

```sql
ROLLBACK;
```

It discards uncommitted changes in the current transaction.

It is useful for:

- failure recovery;
- validation failures;
- controlled local experiments.

A later rollback does not undo work that was already committed.

---

## 13. Autocommit

Many SQL clients operate in autocommit mode by default. Under autocommit, a statement such as:

```sql
UPDATE orders
SET status = 'paid'
WHERE order_id = 1001;
```

may be committed immediately when successful.

A batch designed as:

```text
1,000,000 row changes
→ 1,000,000 statement-sized transactions
```

can create extra transaction overhead and exposes partial progress on failure.

### Production rule

Know the exact transaction behavior of your driver, ORM, CLI, task runner, and connection configuration.

---

## 14. SAVEPOINT

`SAVEPOINT` creates a partial rollback point inside a transaction.

```sql
BEGIN;

SAVEPOINT before_optional_step;

INSERT INTO audit_events(event_type, detail)
VALUES ('optional', 'temporary work');

ROLLBACK TO SAVEPOINT before_optional_step;

COMMIT;
```

The savepoint does not commit anything and does not create a separate transaction.

---

## 15. Partial Rollback

The workflow is:

```text
BEGIN
 ↓
mandatory changes
 ↓
SAVEPOINT
 ↓
optional changes
 ↓
problem
 ↓
ROLLBACK TO SAVEPOINT
 ↓
continue
 ↓
COMMIT
```

Use partial rollback for genuinely recoverable subsections of one transaction. Do not use it as an excuse to keep locks open while performing unrelated long-running work.

---

## 16. Atomic Batch Loading

A production pattern is:

```text
extract
→ stage
→ validate
→ apply
→ commit
```

Example:

```sql
BEGIN;

INSERT INTO customer_daily(customer_id, event_date, status)
SELECT customer_id, event_date, status
FROM staging_customer_daily
WHERE event_date = DATE '2026-09-28';

-- zero-row assertions here

COMMIT;
```

If validation fails:

```text
ROLLBACK
```

### What should happen outside the transaction?

Often:

```text
network download
file parsing
slow transformation
large external validation
```

can happen before the final target publication transaction.

---

## 17. Two Concurrent Transactions

Use two-session reasoning.

```text
SESSION A                         SESSION B
----------                        ----------
BEGIN;                            BEGIN;
SELECT ...;                       SELECT ...;
UPDATE ...;                       UPDATE ...;
COMMIT;                           COMMIT;
```

For every important step record:

```text
Visible state:
Locks:
Waiting:
Result:
```

The sequence of operations matters. Concurrency is a timeline problem.

---

## 18. Isolation Levels

| Isolation | Core idea | Typical concern |
|---|---|---|
| `READ UNCOMMITTED` | Weakest nominal isolation | Some engines permit dirty reads |
| `READ COMMITTED` | Each statement gets an appropriate committed view | Repeated statements may see newer committed data |
| `REPEATABLE READ` | Stable transaction snapshot for ordinary reads | Concurrent conflicts can cause failures |
| `SERIALIZABLE` | Execution must be equivalent to some serial ordering | Serialization failures and retries |

### PostgreSQL-specific rule

PostgreSQL maps `READ UNCOMMITTED` to behavior equivalent to `READ COMMITTED`; PostgreSQL does not provide ordinary dirty reads through that setting.

Do not treat these exact semantics as universal across databases.

### Decision path

```text
What invariant?
      ↓
What concurrent actors?
      ↓
What anomaly?
      ↓
Can atomic SQL solve it?
      ↓
Can row locking solve it?
      ↓
Do we need stronger isolation?
      ↓
What is the retry/blocking cost?
```

---

## 19. Read Uncommitted

In some database systems, `READ UNCOMMITTED` can allow a dirty read: a transaction sees data another transaction has not committed.

Conceptual dirty-read timeline:

```text
SESSION B
BEGIN
UPDATE balance = 500
(not committed)

SESSION A
SELECT balance
→ 500

SESSION B
ROLLBACK
```

A read a value that never became committed state.

### PostgreSQL

For PostgreSQL, `READ UNCOMMITTED` behaves like `READ COMMITTED`. Do not generalize this to another engine without checking its semantics.

---

## 20. Read Committed

PostgreSQL's default isolation level is `READ COMMITTED`.

At a practical level:

> Each statement sees data committed before that statement's snapshot, subject to PostgreSQL's MVCC and locking behavior.

Two-session example:

```text
SESSION A                         SESSION B
----------                        ----------
BEGIN;                            BEGIN;
SELECT balance; → 100
                                  UPDATE accounts
                                  SET balance = 150
                                  WHERE account_id = 1;
                                  COMMIT;
SELECT balance; → 150
ROLLBACK;
```

The two `SELECT` statements can observe different committed states because they are separate statements.

---

## 21. Repeatable Read

PostgreSQL `REPEATABLE READ` uses a stable transaction-level snapshot for ordinary reads.

```text
SESSION A                         SESSION B
----------                        ----------
BEGIN REPEATABLE READ
SELECT → 100
                                  UPDATE → 150
                                  COMMIT
SELECT → snapshot-consistent value
ROLLBACK
```

The second ordinary read remains consistent with A's transaction snapshot.

Concurrent write conflicts can instead produce a serialization-style transaction failure. Therefore `REPEATABLE READ` is not simply "read the same value forever and every write succeeds."

---

## 22. Serializable

`SERIALIZABLE` aims to make successful concurrent execution equivalent to some serial ordering.

It does **not** mean PostgreSQL literally runs transactions one at a time.

Benefits:

- stronger anomaly protection;
- clearer reasoning for some multi-row invariants.

Costs:

- more transaction aborts under conflict;
- retry requirements;
- potentially more coordination overhead.

Typical pattern:

```text
attempt
→ serialization failure
→ ROLLBACK
→ backoff
→ retry whole transaction
```

---

## 23. Isolation-Anomaly Matrix

| Phenomenon | What it means | PostgreSQL-focused behavior | Typical protection |
|---|---|---|---|
| Dirty read | Read uncommitted data | Not exposed by PostgreSQL `READ UNCOMMITTED` | PostgreSQL MVCC semantics |
| Non-repeatable read | Same row read twice, different committed value | Possible at `READ COMMITTED` | `REPEATABLE READ` or stronger where needed |
| Phantom | Predicate matches a different row set | Can occur in weaker semantics; stronger PostgreSQL levels provide stronger guarantees | Appropriate snapshot/isolation strategy |
| Lost update | One logical update overwrites another | Depends on SQL pattern and isolation/locking | Atomic update, row lock, constraint, or stronger isolation |
| Write skew | Different row writes jointly violate invariant | Possible without sufficient protection | Invariant-aware locking or `SERIALIZABLE` |

Keep the distinction:

```text
SQL-standard terminology
        ↓
database-specific meaning
        ↓
PostgreSQL implementation behavior
```

---

## 24. Dirty Reads

A dirty read is a read of data another transaction has changed but not committed.

PostgreSQL's MVCC behavior means ordinary PostgreSQL reads do not expose another transaction's uncommitted value.

This matters because a pipeline that trusts uncommitted state could base decisions on data that later disappears through rollback.

---

## 25. Non-Repeatable Reads

Two-session example:

```text
SESSION A                         SESSION B
----------                        ----------
BEGIN;
SELECT balance → 100
                                  BEGIN;
                                  UPDATE balance = 150;
                                  COMMIT;
SELECT balance → 150
```

At PostgreSQL `READ COMMITTED`, this is possible because the two statements can use different statement snapshots.

At `REPEATABLE READ`, A's ordinary reads remain aligned with its transaction snapshot.

---

## 26. Phantom Reads

A phantom concerns a predicate result set.

```sql
SELECT COUNT(*)
FROM jobs
WHERE status = 'ready';
```

Suppose A sees 10. B inserts a qualifying row and commits. A repeats the predicate and may see a different result under weaker isolation semantics.

The key senior concept is the **read set**:

```text
single row invariant
    ≠
predicate/set invariant
```

If correctness depends on a condition over many rows, row-by-row locking may be insufficient.

---

## 27. Lost Updates

Initial state:

```text
balance = 100
```

Unsafe application flow:

```text
A reads 100 → computes 110
B reads 100 → computes 120
A writes 110
B writes 120
```

One logical update can be lost.

### Safer pattern 1 — Row lock

```sql
BEGIN;

SELECT balance
FROM accounts
WHERE account_id = 1
FOR UPDATE;

-- compute using the locked current value

UPDATE accounts
SET balance = 120
WHERE account_id = 1;

COMMIT;
```

### Safer pattern 2 — Atomic SQL expression

```sql
UPDATE accounts
SET balance = balance + 10
WHERE account_id = 1;
```

When the business operation is expressible directly, the atomic update can avoid the unsafe application-level read-modify-write gap.

---

## 28. Write Skew

Classic invariant:

```text
At least one doctor must remain on call.
```

Initial state:

```text
Doctor A → on call
Doctor B → on call
```

Two transactions each see two doctors on call and independently turn themselves off.

```text
SESSION A                         SESSION B
----------                        ----------
BEGIN;                            BEGIN;
SELECT COUNT(*) → 2              SELECT COUNT(*) → 2
UPDATE doctor A → off            UPDATE doctor B → off
COMMIT;                           COMMIT;
```

Final state:

```text
0 doctors on call
```

The problem is that the invariant spans multiple rows. Locking one row does not necessarily protect the entire rule.

A suitable `SERIALIZABLE` design can detect the unsafe concurrent outcome and reject one transaction instead.

---

## 29. PostgreSQL Isolation Behavior

PostgreSQL-focused facts to remember:

```text
Default isolation: READ COMMITTED
Dirty reads: not exposed in ordinary PostgreSQL semantics
MVCC: yes
Repeatable Read: transaction-level snapshot for ordinary reads
Serializable: stronger serial-order guarantee with possible failures
Retry: required for retryable serialization/deadlock failures
```

Use PostgreSQL documentation and controlled experiments when exact version-specific behavior matters.

Never carry PostgreSQL assumptions unchanged into another engine.

---

## 30. MVCC

MVCC means **Multi-Version Concurrency Control**.

Conceptual row-version model:

```text
Row version A
    ↓
UPDATE
    ↓
Row version B
```

A reader uses visibility rules to determine which row version belongs in its snapshot, while a writer can create a newer version.

### Production intuition

> Readers and writers can often proceed concurrently without requiring every read to block every write.

Do not say:

> "MVCC means there are no locks."

Locks still matter for writes, explicit row locking, DDL, and other coordination operations.

---

## 31. Transaction Snapshots

A snapshot determines which row versions are visible to a transaction or statement.

```text
T1 begins
   ↓
T1 snapshot
   ↓
T2 updates and commits
   ↓
T1 reads
```

Under `READ COMMITTED`, later statements can acquire a newer statement-level view. Under `REPEATABLE READ`, ordinary reads remain tied to the transaction snapshot.

### Debugging question

If one session can see a row and another cannot, ask about:

```text
commit state
isolation level
snapshot visibility
row version
```

Do not immediately blame locking.

---

## 32. Readers and Writers

Compare:

```text
normal SELECT
```

with:

```text
UPDATE / DELETE
```

A normal `SELECT` is primarily a visibility question. Writes also involve concurrency control around the rows they modify.

Use this four-layer model:

```text
1. Visibility — what version can I see?
2. Locks — what am I holding/requesting?
3. Blocking — who is waiting?
4. Commit — when does the change become committed?
```

Normal readers and writers can often coexist under MVCC, but explicit locks and DDL can still block.

---

## 33. Row Locks

Row locks coordinate conflicting access to specific rows.

Common forms taught here:

```sql
SELECT ... FOR UPDATE;
SELECT ... FOR SHARE;
```

Reason about every lock with:

```text
Who holds the lock?
What lock is requested?
Are the locks compatible?
If not:
    block?
    fail?
    skip?
```

Explicit row locks are normally held until the transaction ends, so transaction duration directly affects lock duration.

---

## 34. SELECT FOR UPDATE

Use `FOR UPDATE` when a transaction must make a decision based on a row and prevent conflicting concurrent work from changing that row before the decision completes.

```sql
BEGIN;

SELECT job_id, payload
FROM jobs
WHERE job_id = 100
FOR UPDATE;

UPDATE jobs
SET status = 'running'
WHERE job_id = 100;

COMMIT;
```

Typical use cases:

- inventory reservation;
- work-item claiming;
- read-modify-write business logic.

Do not use it everywhere. Over-locking can reduce concurrency.

---

## 35. SELECT FOR SHARE

`FOR SHARE` requests a shared row lock.

The important concept is shared locking intent rather than memorizing every compatibility rule.

Example:

```sql
BEGIN;

SELECT customer_id
FROM customers
WHERE customer_id = 100
FOR SHARE;

-- perform logic that needs compatible shared access

COMMIT;
```

Use the actual PostgreSQL lock-compatibility semantics when exact behavior is important, especially around foreign-key-sensitive operations.

---

## 36. NOWAIT

`NOWAIT` turns a lock wait into an immediate failure.

```sql
SELECT job_id
FROM jobs
WHERE job_id = 100
FOR UPDATE NOWAIT;
```

Conceptually:

```text
lock available → acquire
lock unavailable → fail immediately
```

This is useful when the business policy says:

```text
If another worker already owns it, try later or choose another item.
```

---

## 37. SKIP LOCKED

`SKIP LOCKED` skips rows that are currently locked instead of waiting.

```sql
SELECT job_id, payload
FROM jobs
WHERE status = 'ready'
ORDER BY job_id
FOR UPDATE SKIP LOCKED
LIMIT 10;
```

Example:

```text
Worker A claims 1–10
Worker B skips 1–10 and claims 11–20
Worker C claims another unlocked batch
```

### Critical caution

`SKIP LOCKED` changes scheduling semantics. It is correct only when skipped work can safely be processed later.

Do not use it for strict dependency order such as:

```text
invoice 100 must finish before invoice 101
```

if skipping 100 would violate correctness.

---

## 38. Work Queues

A database-backed work queue often has a state machine:

```text
ready
 ↓
claimed
 ↓
running
 ↓
completed
```

Failures may move work to:

```text
failed
 ↓
retryable
 ↓
ready
```

A queue table can be as simple as:

```sql
CREATE TABLE jobs (
    job_id BIGINT PRIMARY KEY,
    payload TEXT NOT NULL,
    status TEXT NOT NULL,
    available_at TIMESTAMP NOT NULL
);
```

The concurrency problem is not merely selecting rows. It is **claiming ownership atomically**.

---

## 39. Concurrent Job Claiming

A production-style claim is:

```text
ready
 ↓
lock + claim
 ↓
running
 ↓
commit
```

Example:

```sql
BEGIN;

WITH next_jobs AS (
    SELECT job_id
    FROM jobs
    WHERE status = 'ready'
      AND available_at <= CURRENT_TIMESTAMP
    ORDER BY job_id
    FOR UPDATE SKIP LOCKED
    LIMIT 10
)
UPDATE jobs AS j
SET status = 'running'
FROM next_jobs
WHERE j.job_id = next_jobs.job_id
RETURNING j.job_id;

COMMIT;
```

Claim and transition should be atomic so another worker cannot see the same job as available after ownership has been assigned.

### Failure semantics

If the claim transaction rolls back, the job remains available. If the claim commits and the worker later crashes, the system needs a recovery strategy such as attempt counts, leases, or requeue rules.

---

## 40. Serialization Failures

Higher isolation can reject a transaction even when the SQL is valid in isolation.

```text
Transaction A
      \
       → conflicting concurrent dependency
      /
Transaction B

        ↓
unsafe / non-serializable interaction
        ↓
one transaction fails
```

A serialization failure is often a **correctness mechanism**: the database refuses to silently accept a schedule that does not satisfy the requested transaction semantics.

The application must classify this error as potentially retryable when the workload is designed for retries.

---

## 41. Transaction Retry Patterns

The safe unit of retry is the whole transaction attempt.

```text
BEGIN
 ↓
read state
 ↓
make decisions
 ↓
write state
 ↓
validate
 ↓
COMMIT
```

Transient failure:

```text
serialization/deadlock failure
 ↓
ROLLBACK
 ↓
backoff
 ↓
BEGIN again
 ↓
repeat entire transaction
```

### Pseudocode

```text
attempt = 0

while attempt < retry_limit:
    attempt += 1
    BEGIN
    try:
        perform all transaction reads
        perform all transaction writes
        validate required invariants
        COMMIT
        return success
    except retryable concurrency failure:
        ROLLBACK
        backoff
        continue
    except permanent failure:
        ROLLBACK
        raise
```

### Why not retry one statement?

Because statements earlier in the transaction may have established the assumptions on which the failed statement depends.

```text
statement 1 read state X
statement 2 changed state
statement 3 failed
```

Rerunning only statement 3 may produce a result based on a different state than the original transaction intended.

### Production retry requirements

Use:

- bounded retry attempts;
- backoff, often with jitter when many workers may retry together;
- clear classification of retryable versus permanent errors;
- idempotent or transactionally safe business operations;
- observability of retry count and final outcome.

---

## 42. Table-Level Locks

PostgreSQL also uses table-level locks. You do not need to memorize every lock mode to reason about most Data Engineering incidents.

Instead ask:

```text
What operation is being performed?
What lock does it require?
What sessions hold conflicting locks?
What sessions are waiting?
```

Table-level locking becomes especially important for:

- DDL;
- schema changes;
- certain maintenance operations;
- operations that need stronger table coordination.

### Operational intuition

```text
long transaction
      ↓
conflicting lock remains active
      ↓
DDL waits
      ↓
lock queue grows
      ↓
latency / deployment risk
```

Do not turn this chapter into a complete PostgreSQL lock-mode reference. The goal is production reasoning.

---

## 43. DDL and Locking

A schema change such as:

```sql
ALTER TABLE subscriptions
ADD COLUMN source_system TEXT;
```

can require strong table-level coordination.

### Two-session example

```text
SESSION A                         SESSION B
----------                        ----------
BEGIN;
SELECT * FROM subscriptions;
-- transaction remains open
                                  BEGIN;
                                  ALTER TABLE subscriptions
                                  ADD COLUMN source_system TEXT;
                                  -- may wait...
```

> **Session B is now waiting...**

Release the long transaction:

```sql
-- SESSION A
COMMIT;
```

Then B can proceed if the remaining conditions permit it.

### Deployment safety

Before running production DDL, consider:

```text
active transactions
lock requirements
expected execution duration
lock_timeout
statement_timeout
rollback / retry strategy
```

Not every `ALTER TABLE` has the same cost or lock behavior. The exact DDL statement matters.

---

## 44. lock_timeout

`lock_timeout` limits how long a statement waits to acquire a lock.

```sql
SET lock_timeout = '2s';
```

A deployment migration can use:

```sql
BEGIN;

SET LOCAL lock_timeout = '2s';

ALTER TABLE subscriptions
ADD COLUMN source_system TEXT;

COMMIT;
```

If the lock cannot be acquired within the configured wait budget, the statement fails.

### Why this matters

A migration system often prefers:

```text
attempt
→ fail fast if blocked
→ alert / reschedule
```

instead of:

```text
wait indefinitely
→ migration process stuck
```

`lock_timeout` is a **failure containment mechanism**, not a substitute for a correct locking design.

---

## 45. statement_timeout

`statement_timeout` limits how long a statement is allowed to run.

```sql
SET statement_timeout = '30s';
```

The key distinction is:

```text
lock_timeout
→ maximum lock-wait time

statement_timeout
→ maximum statement execution time
```

### Two scenarios

#### Scenario A — blocked DDL

```text
ALTER TABLE
   ↓
waiting on lock
   ↓
lock_timeout reached
```

#### Scenario B — expensive query

```text
SELECT ...
   ↓
actively executing
   ↓
statement_timeout reached
```

Both controls can protect production, but they protect different failure modes.

### Practical caution

Set values according to workload and environment. A timeout that is safe for an interactive migration may be too small for a legitimate batch query.

---

## 46. Deadlocks

A deadlock occurs when transactions wait on each other in a cycle.

```text
Transaction A locks row 1
Transaction B locks row 2

A requests row 2
B requests row 1

A ↔ B
```

### Two-session pattern

```text
SESSION A                         SESSION B
----------                        ----------
BEGIN;                            BEGIN;
lock row 1                        lock row 2
request row 2 → wait              request row 1 → wait
```

Neither can make progress without intervention.

### Blocking vs deadlock

```text
Blocking:
A → waits for B

Deadlock:
A → waits for B
B → waits for A
```

Not every long wait is a deadlock.

---

## 47. PostgreSQL Deadlock Detection

PostgreSQL detects deadlock cycles and aborts one of the participating transactions.

```text
deadlock
 ↓
database detects cycle
 ↓
one transaction is aborted
 ↓
application receives an error
 ↓
transaction may need retry
```

The same transaction is not guaranteed to be chosen every time.

### Production response

Capture enough information to reconstruct:

```text
session identity
SQL statement
lock ownership
requested lock
transaction start time
transaction order
```

Then ask:

> Which two (or more) code paths acquire the same resources in different orders?

---

## 48. Preventing Deadlocks

Prevention is better than depending only on timeout or retry.

### Main techniques

1. deterministic lock ordering;
2. small transaction scope;
3. acquire only the locks actually required;
4. avoid slow external work while holding locks;
5. reduce contention where possible;
6. retry transient deadlock victims when the transaction is safe to retry.

### Classic rule

```text
Always lock resource 1
then resource 2
```

not:

```text
A: 1 → 2
B: 2 → 1
```

---

## 49. Consistent Lock Ordering

Suppose two accounts must both be locked for a transfer.

### Dangerous

```text
Transaction A: account 10 → account 20
Transaction B: account 20 → account 10
```

### Better

Normalize the order:

```text
lower account_id first
higher account_id second
```

Both paths become:

```text
10 → 20
```

Now B waits for A if A already owns 10, rather than constructing a cycle.

### Generalize the rule

The ordered resources can be:

```text
rows
tables
partitions
jobs
logical pipeline resources
```

The ordering rule should be documented and applied consistently across code paths.

---

## 50. Small Transactions

> **Keep transactions as short as practical.**

Short does not mean one statement.

A transaction should contain the minimum work necessary for its atomic state transition.

### Why long duration is expensive

Longer transactions can:

- hold locks longer;
- keep snapshots alive longer;
- increase blocking;
- increase rollback scope;
- delay cleanup of old row versions;
- increase contention and serialization conflicts;
- increase operational recovery time.

### Bad

```text
BEGIN
↓
download API data
↓
wait 20 minutes
↓
parse files
↓
call another service
↓
UPDATE
↓
COMMIT
```

### Better

```text
extract
↓
stage
↓
validate
↓
BEGIN
↓
publish
↓
COMMIT
```

---

## 51. Long-Running Transactions

A transaction can be accidentally long-running even when the database work itself is small.

```text
BEGIN
↓
SELECT data
↓
Python processing
↓
HTTP request
↓
application sleep
↓
UPDATE
↓
COMMIT
```

From PostgreSQL's perspective, the transaction remains open throughout the application and network delays.

### Risks

```text
long transaction
├── retained locks
├── long-lived snapshot
├── blocking pressure
├── delayed cleanup
├── more rollback work
└── operational pressure
```

Monitor both:

```text
active long transactions
idle-in-transaction sessions
```

These can be different symptoms with similar operational consequences.

---

## 52. VACUUM Interaction

PostgreSQL's MVCC means updates/deletes can leave older row versions behind until they are no longer needed by active snapshots.

A long-running transaction can keep an old snapshot alive:

```text
long transaction
      ↓
old snapshot remains relevant
      ↓
some old row versions cannot yet be removed safely
      ↓
dead tuples / bloat pressure
```

### Consequences

Potential consequences include:

- dead tuples accumulating;
- table or index bloat pressure;
- storage growth;
- increased vacuum workload;
- worse cache efficiency.

Do not say that one long transaction means `VACUUM` stops entirely. The precise cleanup effect depends on what versions are still visible to active snapshots.

### Investigation questions

```text
Are transactions unusually old?
Are sessions idle in transaction?
Is there a long-lived reporting snapshot?
Is vacuum falling behind?
Is table growth abnormal?
```

---

## 53. Replication Lag

Replication behavior depends on the architecture and workload.

Long or large transactions can complicate replication progress and contribute to lag depending on:

- transaction size;
- commit timing;
- replay cost;
- replication architecture;
- downstream workload.

Do not claim that every long transaction automatically creates replica lag.

### Production monitoring

Where relevant, monitor:

```text
transaction duration
transaction size
replica replay lag
blocked sessions
idle-in-transaction sessions
```

The architectural goal is to reduce avoidable transaction duration and make large publication events intentional.

---

## 54. Staging Tables

Staging separates preparation from publication.

```text
source extract
      ↓
staging table
      ↓
validate
      ↓
apply target
      ↓
short transaction
```

### Why it helps

Slow work such as:

```text
download
parse
type conversion
validation
reconciliation
```

can happen without unnecessarily holding target-table locks.

### Example

```sql
CREATE TEMP TABLE staging_customer_delta (
    customer_id BIGINT,
    status TEXT,
    event_ts TIMESTAMP
);
```

Populate and validate staging first. Then open the target publication transaction.

---

## 55. Staging-Then-Apply Pattern

The pattern is:

```text
slow preparation
      ↓
stage
      ↓
validate
      ↓
BEGIN
      ↓
apply + assertions
      ↓
COMMIT
```

Example:

```sql
BEGIN;

UPDATE customer_current AS t
SET
    status = s.status,
    updated_at = s.event_ts
FROM staging_customer_delta AS s
WHERE t.customer_id = s.customer_id;

INSERT INTO customer_current(customer_id, status, updated_at)
SELECT s.customer_id, s.status, s.event_ts
FROM staging_customer_delta AS s
WHERE NOT EXISTS (
    SELECT 1
    FROM customer_current AS t
    WHERE t.customer_id = s.customer_id
);

-- zero-row assertions

COMMIT;
```

The exact upsert/SCD implementation belongs to Topic 10; this section focuses on the transaction boundary.

### Design objective

Hold target locks only for the part that truly needs to be atomic.

---

## 56. Swap/Refresh Patterns

A full refresh can be conceptualized as:

```text
old_table
new_table
```

Build and validate `new_table` before the reader-facing publication operation.

```text
build new state
→ validate
→ short swap/apply
→ readers see new published state
```

### Benefits

- short critical publication window;
- slow computation occurs outside the critical transaction;
- readers can move from old valid state to new valid state as one publication event.

### Risks

A simple rename is not automatically safe for every schema. Consider:

```text
foreign keys
views
permissions
triggers
sequences
indexes
object dependencies
external references
```

The pattern is architectural, not a universal one-line SQL recipe.

---

## 57. Advisory Locks

PostgreSQL advisory locks let application code coordinate around a logical lock key.

Session-level example:

```sql
SELECT pg_advisory_lock(12345);

-- protected logical work

SELECT pg_advisory_unlock(12345);
```

Transaction-scoped example:

```sql
SELECT pg_advisory_xact_lock(12345);
```

Transaction-scoped advisory locks are automatically released when the transaction ends.

### Critical property

Advisory locks are **cooperative**.

PostgreSQL does not know that:

```text
12345 = daily_customer_load
```

Your applications must agree on the meaning of the key.

### Every advisory-lock design should document

```text
Job name:
Lock key:
Who acquires it:
What happens if already held:
When released:
Invariant protected:
Hard database constraint protecting correctness:
```

---

## 58. Preventing Duplicate Pipeline Runs

Consider:

```text
daily_customer_load
```

Invariant:

```text
At most one logical run is active for a given business date.
```

### Conceptual flow

```text
scheduler A
    ↓
gets lock
    ↓
runs job

scheduler B
    ↓
tries same key
    ↓
fails / waits / skips according to policy
```

A useful non-blocking variant is:

```sql
SELECT pg_try_advisory_lock(12345);
```

The application can then decide what to do if the result is false.

### Key convention

Use a stable mapping such as:

```text
namespace + job_name + business_date
→ deterministic lock key
```

### Important

Advisory locks should complement, not replace, hard database correctness guarantees such as a suitable unique constraint or state invariant.

---

## 59. DuckDB Concurrency

**Engine: DuckDB**

DuckDB provides ACID transactional behavior and, for this chapter's architecture model, has a **single-writer** concurrency model with support for concurrent analytical readers.

### Mental model

```text
many readers
     +
one controlled writer
```

This fits many single-node analytical workflows well, but a PostgreSQL-style architecture with many independent concurrent writers may need redesign.

### Do not say

> "DuckDB has no concurrency."

Instead say:

> "DuckDB supports concurrent analytical work, while write concurrency follows a single-writer model in the workload model used here."

When building a real system, verify the exact version and deployment architecture.

---

## 60. Warehouse Concurrency

Cloud warehouses can use architectures very different from PostgreSQL.

Therefore do not assume:

```text
PostgreSQL lock behavior
→ warehouse behavior
```

Instead investigate:

```text
concurrent write semantics
transaction isolation
DDL behavior
reader/writer interaction
queueing / workload management
retry behavior
```

Different warehouses may rely more heavily on MVCC-like mechanisms, metadata operations, optimistic techniques, workload queues, or service-specific coordination.

### Senior rule

> **Always read the target engine's concurrency model before designing a concurrent pipeline.**

Non-PostgreSQL material here is awareness-level, not a substitute for vendor-specific documentation.

---

## 61. Lakehouse Optimistic Concurrency

Lakehouse table formats can use optimistic concurrency control.

Conceptually:

```text
Writer A reads version N
Writer B reads version N

A prepares changes
B prepares changes

A commits → version N+1

B commits
   ↓
conflict validation
   ↓
accept or reject
```

Contrast:

```text
Traditional database:
locks / MVCC / transaction snapshots

Lakehouse:
optimistic conflict detection / commit validation
```

The learner only needs awareness here. Do not assume row-lock syntax such as `FOR UPDATE` has a direct lakehouse equivalent.

---

## 62. Production Pipeline Patterns

For every concurrency pattern, document:

```text
Problem:
Concurrent actors:
Invariant:
Transaction boundary:
Lock/isolation strategy:
Failure mode:
Retry behavior:
Validation:
```

### Pattern 1 — Atomic batch load

```text
Problem: partial publication
Actors: loader + readers
Invariant: batch is old-valid or new-valid, never half-published
Boundary: final apply + assertions
Strategy: short transaction
Failure: rollback
Retry: retry full transaction when transient
Validation: count/reconciliation + zero-row assertions
```

### Pattern 2 — Concurrent work queue

```text
Problem: duplicate claims
Actors: worker A/B/C
Invariant: one active claim per job
Boundary: claim + status transition
Strategy: FOR UPDATE SKIP LOCKED
Failure: rollback returns uncommitted claim
Retry: requeue/recover abandoned work
Validation: no duplicate active claims
```

### Pattern 3 — Lost-update prevention

Prefer:

```sql
UPDATE counters
SET value = value + 1
WHERE counter_id = 1;
```

when the whole transformation can be expressed atomically.

Use `FOR UPDATE` when the business decision requires multiple reads or calculations based on the current locked state.

### Pattern 4 — Staging then apply

```text
slow extract
→ stage
→ validate
→ BEGIN
→ atomic target publication
→ COMMIT
```

### Pattern 5 — Short table refresh

```text
build replacement state
→ validate
→ short reader-facing publication operation
```

### Pattern 6 — Singleton job

```text
stable advisory lock
+
hard database invariant where applicable
```

### Pattern 7 — Serializable transaction with retry

```text
strong invariant
→ SERIALIZABLE
→ possible serialization failure
→ ROLLBACK
→ backoff
→ retry whole transaction
```

Do not prescribe `SERIALIZABLE` everywhere. It is a tool for a correctness requirement with an operational cost.

---

## 63. Concurrency Debugging Methodology

Use this sequence during an incident.

### 1. Identify transaction boundaries

```text
BEGIN
COMMIT
ROLLBACK
autocommit
idle-in-transaction
```

### 2. Identify sessions

```text
Session A
Session B
Session C
```

### 3. Record what each session read

Include the approximate time and isolation level.

### 4. Record what each session changed

List rows/tables and statements.

### 5. Reconstruct held locks

```text
who holds?
what resource?
```

### 6. Reconstruct requested locks

```text
who requests?
what resource?
```

### 7. Determine isolation

```text
READ COMMITTED
REPEATABLE READ
SERIALIZABLE
```

### 8. Build a timeline

```text
Time →
────────────────────────────────────────────
A: BEGIN
A: SELECT row 1
B: BEGIN
B: UPDATE row 1
B: COMMIT
A: SELECT row 1 again
```

### 9. State the invariant

Examples:

```text
one active job
at least one doctor on call
complete batch publication
no lost increments
```

### 10. Classify the incident

```text
blocking
 deadlock
 serialization failure
 lost update
 write skew
 long transaction
```

### 11. Choose the smallest correct fix

Consider:

```text
atomic SQL
constraint
row lock
lock order
SKIP LOCKED
NOWAIT
timeout
advisory lock
isolation change
```

### 12. Re-test concurrency

A concurrency bug is not fixed merely because the code looks safer. Recreate the overlap.

---

## 64. Assertion Queries

The strongest style for pipeline validation is a **zero-row assertion**.

### No duplicate active jobs

```sql
SELECT job_name
FROM job_runs
WHERE status = 'running'
GROUP BY job_name
HAVING COUNT(*) > 1;
```

Expected: zero rows.

### No orphan payments

```sql
SELECT p.payment_id
FROM payments AS p
LEFT JOIN invoices AS i
    ON i.invoice_id = p.invoice_id
WHERE i.invoice_id IS NULL;
```

Expected: zero rows.

### At least one doctor on call

```sql
SELECT 1
WHERE NOT EXISTS (
    SELECT 1
    FROM doctors
    WHERE on_call = true
);
```

Expected: zero rows.

### No invalid subscription state

Example business invariant:

```text
end_date must be NULL or >= start_date
```

```sql
SELECT subscription_id
FROM subscriptions
WHERE end_date IS NOT NULL
  AND end_date < start_date;
```

Expected: zero rows.

### Atomic load reconciliation

```sql
SELECT
    (SELECT COUNT(*)
     FROM staging_customer_daily
     WHERE event_date = DATE '2026-09-28') AS staged_count,
    (SELECT COUNT(*)
     FROM customer_daily
     WHERE event_date = DATE '2026-09-28') AS target_count;
```

Define the expected relationship explicitly. A count comparison is useful only when the target publication is intended to correspond to that staging population.

### Assertion principle

```text
transaction boundary
       ↓
post-condition check
       ↓
COMMIT only if invariant holds
```

---

## 65. Common Mistakes

Use this pattern when reviewing any concurrency mistake:

```text
mistake
→ broken scenario
→ why
→ corrected approach
→ production lesson
```

### Mistake: unintended autocommit

Broken scenario: every statement commits separately.  
Why: transaction boundaries were assumed rather than configured.  
Corrected approach: explicit `BEGIN`/`COMMIT` around the atomic unit.  
Lesson: know your driver/client transaction mode.

### Mistake: forgetting `COMMIT`

Broken scenario: work appears successful in one session but remains uncommitted.  
Why: the transaction is still open.  
Corrected approach: explicit transaction lifecycle and observability.  
Lesson: open transactions are operational state.

### Mistake: expecting rollback after commit

Broken scenario:

```text
COMMIT
...
ROLLBACK
```

Why: rollback affects the current uncommitted transaction, not already committed work.  
Corrected approach: treat commit as the publication boundary.  
Lesson: choose boundaries deliberately.

### Mistake: huge transaction

Broken scenario: a full-day pipeline runs under one transaction.  
Why: locks, snapshots, rollback scope, and cleanup pressure grow.  
Corrected approach: stage independently and publish in smaller atomic units.  
Lesson: atomic does not mean huge.

### Mistake: external work under lock

Broken scenario:

```text
FOR UPDATE
→ HTTP request
→ wait
→ COMMIT
```

Why: lock hold time now depends on remote latency.  
Corrected approach: move external work outside the critical section.  
Lesson: database locks should not be hostage to network calls.

### Mistake: wrong isolation assumption

Broken scenario: code assumes every `REPEATABLE READ` implementation behaves identically.  
Why: isolation labels are not a substitute for engine semantics.  
Corrected approach: verify PostgreSQL behavior.  
Lesson: implementation matters.

### Mistake: PostgreSQL `READ UNCOMMITTED` dirty-read assumption

Broken scenario: developer expects uncommitted values to be visible.  
Corrected approach: remember PostgreSQL maps that setting to `READ COMMITTED`-style behavior.

### Mistake: MVCC means no locks

Broken scenario: developer removes all explicit concurrency controls.  
Corrected approach: reason separately about snapshots and locks.

### Mistake: locking without an invariant

Broken scenario: every code path uses `FOR UPDATE`, causing unnecessary contention.  
Corrected approach: define what must remain stable and lock only what the decision requires.

### Mistake: unsafe `SKIP LOCKED`

Broken scenario: strict dependency order is silently violated.  
Corrected approach: only skip when any eligible work can safely be processed later.

### Mistake: no retry for transient concurrency failures

Broken scenario: a valid transaction fails once and the pipeline is marked permanently failed.  
Corrected approach: classify and retry the full transaction when safe.

### Mistake: retrying one statement

Broken scenario: statement 4 is rerun after the transaction's assumptions changed.  
Corrected approach: restart from `BEGIN`.

### Mistake: inconsistent lock order

Broken scenario:

```text
A: 1 → 2
B: 2 → 1
```

Corrected approach: deterministic ordering.

### Mistake: long-running transactions / idle in transaction

Broken scenario: a Python process sleeps with a transaction open.  
Corrected approach: close the database transaction before slow external work.

### Mistake: ignoring VACUUM interaction

Corrected approach: monitor transaction age, long-lived snapshots, dead tuples, and bloat symptoms.

### Mistake: ignoring replication implications

Corrected approach: monitor transaction duration/size and actual replica lag in the chosen architecture.

### Mistake: unguarded DDL

Corrected approach: plan schema changes, inspect active transactions, use timeouts where appropriate.

### Mistake: missing `lock_timeout`

Corrected approach: bound lock waits for operational migrations where fail-fast is preferable.

### Mistake: missing `statement_timeout`

Corrected approach: bound runaway query/statement execution according to environment.

### Mistake: treating staging as atomic publication

Corrected approach: make the final apply/publish operation the transaction boundary.

### Mistake: unstable advisory keys

Corrected approach: deterministic, documented lock-key convention.

### Mistake: advisory lock as constraint replacement

Corrected approach: use a database constraint/state invariant for hard correctness where possible.

### Mistake: PostgreSQL assumptions applied to every engine

Corrected approach: read the target engine's concurrency model.

### Mistake: DuckDB assumed to be multi-writer like PostgreSQL

Corrected approach: design around its single-writer model.

### Mistake: warehouse assumed to be PostgreSQL

Corrected approach: verify vendor-specific semantics.

### Mistake: lakehouse assumed to use row locks

Corrected approach: reason about optimistic conflict detection.

### Mistake: no timeline during debugging

Corrected approach: reconstruct every session's actions, visibility, lock, wait, commit, and failure.

---

## 66. Beginner Practice

Each exercise includes objective, setup, task, expected result, solution, and explanation.

### Exercise 1 — `BEGIN` and `COMMIT`

**Objective:** Create one explicit transaction.  
**Setup:**

```sql
CREATE TEMP TABLE demo_accounts(account_id INT PRIMARY KEY, balance INT);
INSERT INTO demo_accounts VALUES (1, 100);
```

**Task:**

```sql
BEGIN;
UPDATE demo_accounts SET balance = 150 WHERE account_id = 1;
COMMIT;
```

**Expected result:** `150`.  
**Solution:** The SQL above.  
**Explanation:** The update became part of the committed transaction.

### Exercise 2 — `ROLLBACK`

**Objective:** Undo uncommitted work.  
**Setup:** Use `demo_accounts` with balance 100.  
**Task:**

```sql
BEGIN;
UPDATE demo_accounts SET balance = 200 WHERE account_id = 1;
ROLLBACK;
```

**Expected result:** `100`.  
**Solution:** Roll back the open transaction.  
**Explanation:** The update was never committed.

### Exercise 3 — ACID mapping

**Objective:** Map scenarios to properties.  
**Setup:**

```text
all-or-nothing batch
foreign-key invariant
concurrent visibility
committed state survives configured failure/recovery model
```

**Task:** Map each to ACID.  
**Expected:**

```text
Atomicity
Consistency
Isolation
Durability
```

**Solution:** The mapping above.  
**Explanation:** Each property describes a different guarantee dimension.

### Exercise 4 — Autocommit

**Objective:** Identify statement-sized commit behavior.  
**Setup:** Assume autocommit is enabled.  
**Task:** Predict the effect of:

```sql
UPDATE orders SET status = 'paid' WHERE order_id = 1;
```

**Expected:** The statement may commit immediately.  
**Solution:** Use explicit `BEGIN` when several statements must commit together.  
**Explanation:** Client configuration determines the transaction boundary.

### Exercise 5 — `SAVEPOINT`

**Objective:** Practice partial rollback.  
**Setup:**

```sql
CREATE TEMP TABLE events(event_id INT PRIMARY KEY, event_type TEXT);
```

**Task:**

```sql
BEGIN;
INSERT INTO events VALUES (1, 'mandatory');
SAVEPOINT before_optional;
INSERT INTO events VALUES (2, 'optional');
ROLLBACK TO SAVEPOINT before_optional;
COMMIT;
```

**Expected:** Only event 1 exists.  
**Solution:** The commands above.  
**Explanation:** The transaction continues after the savepoint rollback.

### Exercise 6 — Transaction boundary

**Objective:** Separate slow preparation from atomic publication.  
**Setup:** A source download takes 20 minutes; final publication takes 10 seconds.  
**Task:** Choose a sensible transaction boundary.  
**Expected:** Download/parse/stage before `BEGIN`; publish inside a short transaction.  
**Solution:**

```text
extract → stage → validate → BEGIN → publish → COMMIT
```

**Explanation:** The atomic unit is publication, not network I/O.

### Exercise 7 — Atomic batch failure

**Objective:** Reason about a crash halfway through a batch.  
**Setup:** 1,000 rows must publish together.  
**Task:** Compare one explicit transaction with independent autocommit statements.  
**Expected:** Explicit transaction can roll back the incomplete publication as a unit.  
**Solution:** Put the target publication in `BEGIN`/`COMMIT`.  
**Explanation:** This matches the all-or-nothing invariant.

### Exercise 8 — Basic two-session visibility

**Objective:** Observe PostgreSQL `READ COMMITTED`.  
**Setup:** `balance = 100`.  
**Task:** A reads; B updates to 150 and commits; A reads again.  
**Expected:** A's second statement can see 150.  
**Solution:** Use the default isolation level.  
**Explanation:** PostgreSQL `READ COMMITTED` uses statement-level snapshots.

### Exercise 9 — Validation gate

**Objective:** Make validation part of publication.  
**Setup:** Staging contains the daily batch.  
**Task:** Define when `COMMIT` is allowed.  
**Expected:** Only after required zero-row assertions succeed.  
**Solution:** `BEGIN` → apply → assertions → `COMMIT`, otherwise `ROLLBACK`.  
**Explanation:** Assertions are post-condition checks for committed state.

### Exercise 10 — State the invariant

**Objective:** Practice requirement-first thinking.  
**Setup:** A job updates a watermark, inserts data, and marks the run complete.  
**Task:** State the invariant.  
**Expected example:** The watermark and run-completion state must never claim a publication that was not committed.  
**Solution:** Any precise invariant is acceptable.  
**Explanation:** The invariant determines the transaction boundary.

---

## 67. Intermediate Practice

### Exercise 1 — `READ COMMITTED`

**Objective:** Reproduce a non-repeatable read.  
**Setup:** Row starts at 100.  
**Task:** A reads; B updates/commits; A reads again.  
**Expected:** Two different observations are possible.  
**Solution:** Use PostgreSQL default isolation.  
**Explanation:** Statement snapshots can differ.

### Exercise 2 — `REPEATABLE READ`

**Objective:** Observe a stable transaction snapshot.  
**Setup:** Same row.  
**Task:** A begins `REPEATABLE READ`; B updates and commits; A reads again.  
**Expected:** A's ordinary read remains consistent with its transaction snapshot.  
**Solution:**

```sql
BEGIN ISOLATION LEVEL REPEATABLE READ;
```

**Explanation:** Snapshot lifetime is transaction-wide for ordinary reads.

### Exercise 3 — PostgreSQL `READ UNCOMMITTED`

**Objective:** Avoid engine-agnostic assumptions.  
**Setup:** B has an uncommitted update.  
**Task:** Determine whether A can see the value under PostgreSQL `READ UNCOMMITTED`.  
**Expected:** No ordinary dirty read; behavior is effectively `READ COMMITTED`.  
**Solution:** Treat the level as PostgreSQL-specific.  
**Explanation:** SQL names do not guarantee identical implementations.

### Exercise 4 — Lost update

**Objective:** Reproduce and fix a read-modify-write race.  
**Setup:** Two workers both read 10.  
**Task:** Have both write 11, then replace the logic with an atomic increment.  
**Expected:** Unsafe version loses an increment; atomic version preserves it.  
**Solution:**

```sql
UPDATE counters SET value = value + 1 WHERE counter_id = 1;
```

**Explanation:** The database computes the transition against the current row state.

### Exercise 5 — `FOR UPDATE`

**Objective:** Observe row-level blocking.  
**Setup:** One target row.  
**Task:** A locks it; B requests `FOR UPDATE`.  
**Expected:** B waits until A ends the transaction.  
**Solution:** Release A with `COMMIT` or `ROLLBACK`.  
**Explanation:** B requested a conflicting row lock.

### Exercise 6 — `FOR SHARE`

**Objective:** Practice shared row-lock reasoning.  
**Setup:** A row referenced by another workflow.  
**Task:** Acquire `FOR SHARE` and reason about a concurrent modification.  
**Expected:** Compatible shared operations can proceed; conflicting operations may wait according to PostgreSQL lock rules.  
**Solution:** Use the actual lock-compatibility behavior rather than relying on lock names.  
**Explanation:** Shared and exclusive intentions are different.

### Exercise 7 — `NOWAIT`

**Objective:** Fail fast on conflict.  
**Setup:** A holds a row lock.  
**Task:** B executes `FOR UPDATE NOWAIT`.  
**Expected:** B fails rather than waiting.  
**Solution:** Use `NOWAIT`.  
**Explanation:** The scheduling policy is "do not wait".

### Exercise 8 — `SKIP LOCKED`

**Objective:** Implement a worker queue.  
**Setup:** A holds jobs 1 and 2.  
**Task:** B selects ready jobs with `FOR UPDATE SKIP LOCKED LIMIT 2`.  
**Expected:** B selects other unlocked jobs.  
**Solution:** Use `SKIP LOCKED`.  
**Explanation:** Locked rows are skipped, not waited on.

### Exercise 9 — Visibility vs blocking

**Objective:** Distinguish concepts.  
**Setup:** One session cannot see a newly committed row; another is waiting for a lock.  
**Task:** Classify the symptoms.  
**Expected:** First is visibility/snapshot; second is lock/blocking.  
**Solution:** Apply the four-layer model.  
**Explanation:** They can happen together but are not the same mechanism.

### Exercise 10 — Timeline reasoning

**Objective:** Build a wait graph.  
**Setup:** A owns row 1, B owns row 2, A requests 2, B requests 1.  
**Task:** Draw the graph.  
**Expected:** `A → B` and `B → A`.  
**Solution:** Circular wait = deadlock.  
**Explanation:** The timeline is the primary diagnostic artifact.

---

## 68. Advanced Practice

### Exercise 1 — Write skew

**Objective:** Demonstrate a multi-row invariant failure.  
**Setup:** Two doctors on call, invariant requires at least one.  
**Task:** Make each transaction disable one doctor.  
**Expected:** Weaker concurrency protection can allow an invalid combined state.  
**Solution:** Use invariant-aware locking/isolation, potentially `SERIALIZABLE`.  
**Explanation:** Each write is locally valid while the combined result is invalid.

### Exercise 2 — Serializable failure

**Objective:** Treat transaction failure as a correctness signal.  
**Setup:** Overlapping serializable transactions.  
**Task:** Cause conflicting dependencies.  
**Expected:** One transaction may receive a serialization error.  
**Solution:** Roll back and retry the whole transaction.  
**Explanation:** PostgreSQL protects the serializable guarantee by rejecting an unsafe schedule.

### Exercise 3 — Whole-transaction retry

**Objective:** Define retry scope.  
**Setup:** Five statements form one transaction; statement 4 fails with a transient concurrency error.  
**Task:** Specify the retry.  
**Expected:** `ROLLBACK` → backoff → replay statements 1–5 in a new transaction.  
**Solution:** Retry the complete unit.  
**Explanation:** Earlier reads may have established assumptions for statement 4.

### Exercise 4 — Deterministic lock order

**Objective:** Remove an avoidable deadlock.  
**Setup:** Workers lock accounts in opposite order.  
**Task:** Normalize order.  
**Expected:** All workers lock lower ID first.  
**Solution:** Sort/derive the resource order before locking.  
**Explanation:** The circular-wait edge is removed.

### Exercise 5 — DDL safety

**Objective:** Bound schema-change waiting.  
**Setup:** A migration can encounter long-running transactions.  
**Task:** Add a lock-wait budget.  
**Expected:**

```sql
SET LOCAL lock_timeout = '2s';
```

**Solution:** Use an environment-appropriate timeout.  
**Explanation:** Fail-fast is preferable to an unbounded migration queue in many deployment windows.

### Exercise 6 — Query timeout

**Objective:** Distinguish timeout purposes.  
**Setup:** A query is expensive but does not wait for locks.  
**Task:** Choose the control.  
**Expected:** `statement_timeout`.  
**Solution:**

```sql
SET statement_timeout = '30s';
```

**Explanation:** The problem is execution duration, not lock acquisition.

### Exercise 7 — Long-transaction diagnosis

**Objective:** Connect transaction age to maintenance.  
**Setup:** A transaction stays open for 90 minutes.  
**Task:** Explain potential effects.  
**Expected:** Retained snapshots/locks, delayed cleanup, bloat pressure, blocking risk.  
**Solution:** Inspect transaction age and active snapshots.  
**Explanation:** MVCC makes transaction lifetime operationally important.

### Exercise 8 — Staging/apply

**Objective:** Shorten target lock duration.  
**Setup:** File processing takes 20 minutes; publication takes 20 seconds.  
**Task:** Design the pipeline.  
**Expected:** Prepare/stage first, then short `BEGIN`/apply/commit.  
**Solution:** Staging-then-apply.  
**Explanation:** Target locks are held for the critical section only.

### Exercise 9 — Advisory-lock key

**Objective:** Design deterministic singleton coordination.  
**Setup:** `daily_customer_load` for one business date.  
**Task:** Define a stable lock-key rule.  
**Expected:** Same logical job/date always maps to the same advisory key.  
**Solution:** Document a namespace + job + date mapping.  
**Explanation:** Cooperative locking depends on participants agreeing on the key.

### Exercise 10 — Cross-engine reasoning

**Objective:** Identify portability risks.  
**Setup:** PostgreSQL queue architecture is moved into a single-node DuckDB analytics application.  
**Task:** Identify the concurrency assumption to revisit.  
**Expected:** Concurrent writer behavior.  
**Solution:** Re-check the single-writer model and redesign worker coordination.  
**Explanation:** Transaction architecture is engine-specific.

---

## 69. Two-Session Concurrency Labs

> **Lab safety:** Run these experiments only against a disposable local PostgreSQL database. Never intentionally deadlock, block, alter production schema, or test destructive transaction behavior against production. Clean up every session when the experiment ends.

For each lab, follow the exact execution order. When a line says **waiting**, do not continue with that session until the releasing step is executed.

### Lab 1 — Non-repeatable read

**Starting data**

```sql
CREATE TABLE lab_accounts(
    account_id INT PRIMARY KEY,
    balance INT NOT NULL
);
INSERT INTO lab_accounts VALUES (1, 100);
```

**Setup:** Ensure A uses `READ COMMITTED`.

**SESSION A**

```sql
BEGIN ISOLATION LEVEL READ COMMITTED;
SELECT balance FROM lab_accounts WHERE account_id = 1;
```

**SESSION B**

```sql
BEGIN;
UPDATE lab_accounts SET balance = 150 WHERE account_id = 1;
COMMIT;
```

**Run order:** A `BEGIN`; A `SELECT`; B `BEGIN`; B `UPDATE`; B `COMMIT`; A second `SELECT`.

**Expected observation:** A can see `100` and then `150`.

**Explanation:** Statement-level snapshots allow the second statement to see B's commit.

---

### Lab 2 — Repeatable-read snapshot

**SESSION A**

```sql
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT balance FROM lab_accounts WHERE account_id = 1;
```

**SESSION B**

```sql
BEGIN;
UPDATE lab_accounts SET balance = 200 WHERE account_id = 1;
COMMIT;
```

**Run order:** A begins/reads; B updates/commits; A reads again.

**Expected observation:** A's ordinary read remains aligned with its transaction snapshot.

**Explanation:** PostgreSQL `REPEATABLE READ` uses a stable transaction snapshot.

---

### Lab 3 — Lost update

**Starting data**

```sql
CREATE TABLE lab_counters(counter_id INT PRIMARY KEY, value INT NOT NULL);
INSERT INTO lab_counters VALUES (1, 0);
```

**SESSION A**

```sql
BEGIN;
SELECT value FROM lab_counters WHERE counter_id = 1;
```

**SESSION B**

```sql
BEGIN;
SELECT value FROM lab_counters WHERE counter_id = 1;
```

**Run order:** A reads 0; B reads 0; application logic computes 1 in each session; A writes 1 and commits; B writes 1 and commits.

**Expected result:** `1` instead of two preserved logical increments.

**Fix:**

```sql
UPDATE lab_counters
SET value = value + 1
WHERE counter_id = 1;
```

or use `FOR UPDATE` around the read-modify-write flow.

---

### Lab 4 — `FOR UPDATE` blocking

**SESSION A**

```sql
BEGIN;
SELECT * FROM lab_counters WHERE counter_id = 1 FOR UPDATE;
```

**SESSION B**

```sql
BEGIN;
SELECT * FROM lab_counters WHERE counter_id = 1 FOR UPDATE;
```

**Run order:** A acquires lock; B requests the same lock.

**Expected:** **Session B is now waiting.**

Release:

```sql
-- SESSION A
COMMIT;
```

**Expected:** B can continue.

**Explanation:** B requested a conflicting row lock.

---

### Lab 5 — `NOWAIT`

**SESSION A**

```sql
BEGIN;
SELECT * FROM lab_counters WHERE counter_id = 1 FOR UPDATE;
```

**SESSION B**

```sql
BEGIN;
SELECT *
FROM lab_counters
WHERE counter_id = 1
FOR UPDATE NOWAIT;
```

**Run order:** A locks first, B requests second.

**Expected:** B fails immediately instead of waiting.

**Explanation:** `NOWAIT` converts a lock wait into an error.

---

### Lab 6 — `SKIP LOCKED`

**Starting data**

```sql
CREATE TABLE lab_jobs(
    job_id INT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'ready'
);
INSERT INTO lab_jobs(job_id) VALUES (1),(2),(3),(4);
```

**SESSION A**

```sql
BEGIN;
SELECT job_id
FROM lab_jobs
WHERE status = 'ready'
ORDER BY job_id
FOR UPDATE
LIMIT 2;
```

A locks 1 and 2.

**SESSION B**

```sql
BEGIN;
SELECT job_id
FROM lab_jobs
WHERE status = 'ready'
ORDER BY job_id
FOR UPDATE SKIP LOCKED
LIMIT 2;
```

**Run order:** A selects first; B selects second.

**Expected:** B gets 3 and 4 without waiting.

**Explanation:** B skips locked qualifying rows.

---

### Lab 7 — Write skew

**Starting data**

```sql
CREATE TABLE lab_doctors(
    doctor_id INT PRIMARY KEY,
    on_call BOOLEAN NOT NULL
);
INSERT INTO lab_doctors VALUES (1,true),(2,true);
```

**SESSION A**

```sql
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT COUNT(*) FROM lab_doctors WHERE on_call;
UPDATE lab_doctors SET on_call = false WHERE doctor_id = 1;
```

**SESSION B**

```sql
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT COUNT(*) FROM lab_doctors WHERE on_call;
UPDATE lab_doctors SET on_call = false WHERE doctor_id = 2;
```

**Run order:** A reads; B reads; A update; B update; A commit; B commit.

**Expected:** The combined outcome can violate the invariant by producing zero on-call doctors.

**Then repeat under `SERIALIZABLE`.** One transaction may be aborted with a serialization failure rather than allowing the unsafe outcome.

---

### Lab 8 — Deadlock

**Starting data**

```sql
CREATE TABLE lab_lock_rows(
    row_id INT PRIMARY KEY,
    payload TEXT
);
INSERT INTO lab_lock_rows VALUES (1,'a'),(2,'b');
```

**SESSION A**

```sql
BEGIN;
SELECT * FROM lab_lock_rows WHERE row_id = 1 FOR UPDATE;
```

**SESSION B**

```sql
BEGIN;
SELECT * FROM lab_lock_rows WHERE row_id = 2 FOR UPDATE;
```

**Next A**

```sql
SELECT * FROM lab_lock_rows WHERE row_id = 2 FOR UPDATE;
```

**Expected:** **Session A is now waiting.**

**Next B**

```sql
SELECT * FROM lab_lock_rows WHERE row_id = 1 FOR UPDATE;
```

**Expected:** PostgreSQL detects the cycle and aborts one transaction.

**Explanation:** `A → B` and `B → A` is a deadlock.

---

### Lab 9 — DDL blocked by long transaction

**SESSION A**

```sql
BEGIN;
SELECT * FROM lab_lock_rows;
```

Leave A open.

**SESSION B**

```sql
BEGIN;
SET LOCAL lock_timeout = '2s';
ALTER TABLE lab_lock_rows ADD COLUMN note TEXT;
COMMIT;
```

**Run order:** A begins; A selects; A remains open; B attempts DDL.

**Expected:** B can wait and then fail due to `lock_timeout`, depending on the exact lock conflict/timing.

Release A:

```sql
ROLLBACK;
```

**Explanation:** DDL may require a conflicting table-level lock.

---

### Lab 10 — Serialization failure and retry

**Setup:** Use the doctor invariant from Lab 7.

**SESSION A**

```sql
BEGIN ISOLATION LEVEL SERIALIZABLE;
SELECT COUNT(*) FROM lab_doctors WHERE on_call;
UPDATE lab_doctors SET on_call = false WHERE doctor_id = 1;
```

**SESSION B**

```sql
BEGIN ISOLATION LEVEL SERIALIZABLE;
SELECT COUNT(*) FROM lab_doctors WHERE on_call;
UPDATE lab_doctors SET on_call = false WHERE doctor_id = 2;
```

**Run order:** Make both transactions overlap, then commit them.

**Expected:** One attempt may receive a serialization failure.

**Required recovery:**

```text
ROLLBACK
→ backoff
→ new BEGIN
→ rerun complete transaction
```

**Explanation:** Retry the transaction, not just the failed statement.

---

## 70. Deadlock Challenges

### Challenge 1 — Two rows, opposite order

**Deadlock graph:**

```text
A owns row 1 → requests row 2 → B
B owns row 2 → requests row 1 → A
```

**SQL:** use the pattern from Lab 8.  
**Expected error:** PostgreSQL aborts one deadlocked transaction.  
**Diagnosis:** inconsistent lock order.  
**Corrected approach:** every worker locks ascending IDs.  
**Production lesson:** deterministic ordering removes a common deadlock class.

### Challenge 2 — Two tables, opposite access order

**Scenario:**

```text
Worker A: customers → subscriptions
Worker B: subscriptions → customers
```

**Deadlock graph:**

```text
A owns customer → waits subscription
B owns subscription → waits customer
```

**SQL:** model each table access inside one transaction.  
**Expected error:** possible deadlock when paths overlap.  
**Diagnosis:** cross-table lock order differs.  
**Corrected approach:** document one order for all code paths.  
**Production lesson:** ordering rules include tables, not just rows.

### Challenge 3 — Fix using ordering

**Scenario:** Workers receive account IDs in arbitrary order.  
**Diagnosis:** arbitrary input creates arbitrary lock order.  
**Corrected:** normalize with `MIN(id)` first, then `MAX(id)`.  
**Production lesson:** normalize concurrency-sensitive resource order before locking.

### Challenge 4 — Fix by reducing scope

**Scenario:** A worker locks a row before making an external API call.  
**Diagnosis:** long lock duration expands the blocking/deadlock window.  
**Corrected:** perform external call before the critical transaction when correctness permits.  
**Production lesson:** lock duration is an architectural variable.

### Challenge 5 — Handle the victim correctly

**Scenario:** A production worker receives a deadlock error.  
**Diagnosis:** one transaction has been chosen as the victim.  
**Corrected approach:** rollback the complete transaction and retry with bounded backoff if the operation is retryable.  
**Production lesson:** deadlock handling belongs in application control flow.

---

## 71. Transaction-Anomaly Challenges

Use this answer template for every challenge:

```text
What did A see?
What did B see?
What changed?
What lock exists?
What isolation level is active?
Could both commit?
If not, why?
```

### Challenge 1 — Dirty-read reasoning

B changes a value but does not commit. A tries to read it.

**Answer:** PostgreSQL does not expose ordinary dirty reads, including when `READ UNCOMMITTED` is requested; PostgreSQL maps that level to `READ COMMITTED` behavior.

**Lesson:** distinguish generic SQL terminology from PostgreSQL behavior.

### Challenge 2 — Non-repeatable read

A reads 100. B updates to 150 and commits. A reads again under `READ COMMITTED`.

**Answer:** A can observe 150 on the second statement.

**Lock:** None is required for the read itself.  
**Reason:** separate statement snapshots.

### Challenge 3 — Repeatable-read snapshot

Repeat Challenge 2 with A in `REPEATABLE READ`.

**Answer:** A's ordinary reads stay aligned with the transaction snapshot.

**Lesson:** a stable snapshot changes visibility behavior, while concurrent writes can still produce transaction failures.

### Challenge 4 — Predicate/read-set change

A checks all jobs where `status = 'ready'`. B inserts a matching job and commits.

**Answer:** This is phantom/read-set reasoning.

**Lesson:** a multi-row invariant is not the same as a single-row invariant.

### Challenge 5 — Lost update

A and B both read 10, then both write 11.

**Answer:** one logical increment is lost.

**Corrected approach:** atomic update or a lock-protected read-modify-write.

### Challenge 6 — Write skew

Two doctors see two on-call doctors and each turns one off.

**Answer:** Each transaction's local decision can be valid while the combined final state violates the invariant. `SERIALIZABLE` can detect the unsafe interaction and cause one transaction to fail.

**Lesson:** identify the full read set and the business invariant.

---

## 72. Production Case Study

### Scenario

A subscription-data pipeline loads daily changes into PostgreSQL.

Tables:

```text
customers
subscriptions
invoices
payments
job_runs
```

The platform has:

- scheduled daily loads;
- multiple workers;
- dashboard/report queries;
- occasional schema changes;
- retries after failure;
- concurrent pipeline execution.

### Incident 1 — Partial publication

The loader crashes halfway through the daily apply.

**Problem:** partial target rows.  
**Invariant:** daily publication is all-or-nothing.  
**Actors:** loader + readers + retry worker.  
**Boundary:** short final apply transaction.  
**Strategy:** staging → validation → `BEGIN` → apply → assertions → `COMMIT`.  
**Failure:** rollback.  
**Validation:** staging/target reconciliation and zero-row assertions.

### Incident 2 — Duplicate job processing

Two workers process the same job.

**Problem:** two claims.  
**Invariant:** one active owner per job.  
**Actors:** multiple workers.  
**Boundary:** claim + state transition.  
**Strategy:** `FOR UPDATE SKIP LOCKED`.  
**Failure:** rollback of uncommitted claim.  
**Retry:** recover abandoned `running` work by policy.  
**Validation:**

```sql
SELECT job_id
FROM job_runs
WHERE status = 'running'
GROUP BY job_id
HAVING COUNT(*) > 1;
```

Expected: zero rows.

### Incident 3 — Lost updates

Two workers overwrite each other's computed state.

**Problem:** read-modify-write race.  
**Invariant:** every logical update is preserved.  
**Strategy:** first try to express the state transition atomically:

```sql
UPDATE subscriptions
SET seats_used = seats_used + 1
WHERE subscription_id = 1001;
```

If multi-step logic is necessary, use `FOR UPDATE` around the relevant row state.

### Incident 4 — Deadlock

```text
Worker A: customer 10 → customer 20
Worker B: customer 20 → customer 10
```

**Problem:** circular wait.  
**Fix:** deterministic ordering, e.g. lower ID first.  
**Retry:** full transaction after rollback if safe.  
**Validation:** rerun the concurrent workload.

### Incident 5 — Blocking `ALTER TABLE`

A reporting transaction is left open while deployment attempts DDL.

**Problem:** DDL waits on a conflicting lock.  
**Fix:** migration policy + `lock_timeout` + observation of long transactions.  
**Example:**

```sql
BEGIN;
SET LOCAL lock_timeout = '2s';
ALTER TABLE subscriptions ADD COLUMN source_system TEXT;
COMMIT;
```

### Incident 6 — Serializable failures

A transaction uses `SERIALIZABLE` because a multi-row invariant is important.

**Problem:** occasional serialization errors.  
**Interpretation:** PostgreSQL rejected an unsafe concurrent schedule.  
**Fix:** rollback and retry the entire transaction with bounded backoff.  
**Trade-off:** stronger correctness semantics create more retryable failures under contention.

### Incident 7 — Cleanup pressure

A worker begins a transaction, performs slow Python processing and external calls, then commits 45 minutes later.

**Problem:** long transaction.  
**Risks:** retained snapshots, longer lock retention, blocking, cleanup pressure, larger rollback scope.  
**Fix:** stage/prep first; keep target publication short.  
**Monitoring:** transaction age, idle-in-transaction sessions, bloat/tuple symptoms, replica lag where relevant.

### Final production design

```text
scheduler
   ↓
advisory singleton lock
   ↓
extract / parse
   ↓
staging
   ↓
validate
   ↓
short transaction
   ├── claim work / apply target state
   ├── required row locks
   ├── assertions
   └── COMMIT
   ↓
release / completion
```

Use:

```text
SKIP LOCKED     → queue claim when work can safely be skipped
row locks       → protected read-modify-write
advisory lock   → singleton coordination
appropriate isolation → actual business invariant
retry           → transient concurrency failures
lock_timeout    → bounded DDL lock waits
statement_timeout → bounded statement execution
```

### Case-study review questions

For the final architecture, state:

```text
Problem:
Invariant:
Concurrent actors:
Transaction boundary:
Isolation level:
Lock strategy:
Expected blocking:
Failure mode:
Retry strategy:
Timeout strategy:
Validation:
```

The strongest answer is not the one with the most locking. It is the one that preserves correctness with the smallest justified concurrency-control surface.

---

## 73. Interview Questions

Use this response structure for every question:

```text
Concise answer:
Deeper engineering explanation:
SQL/example where useful:
Likely follow-up:
Common mistake:
```

### 1. What is a transaction?

**Concise answer:** A logical unit of database work.  
**Deeper explanation:** It defines which changes should commit or roll back together.  
**SQL:** `BEGIN; ... COMMIT;`  
**Follow-up:** Can one statement be a transaction?  
**Mistake:** Treating a transaction as synonymous with an entire workflow.

### 2. Explain ACID.

**Concise:** Atomicity, Consistency, Isolation, Durability.  
**Deeper:** They describe all-or-nothing work, invariant preservation, concurrent interaction, and configured committed-state persistence.  
**SQL:** `BEGIN; ... COMMIT;`  
**Follow-up:** Which property addresses concurrency?  
**Mistake:** "Consistency means the database is always correct."

### 3. Atomicity vs consistency?

**Concise:** Atomicity is the unit of commit/rollback; consistency is the validity of the resulting committed state.  
**Deeper:** A transaction can be atomic without enforcing a business rule not represented in the system.  
**SQL:** `CHECK (...)` is an example of an encoded invariant.  
**Follow-up:** How do you enforce a cross-row rule?  
**Mistake:** Treating the terms as synonyms.

### 4. What does `COMMIT` do?

**Concise:** Finalizes the transaction.  
**Deeper:** Changes become committed according to transaction and durability semantics.  
**SQL:** `COMMIT;`  
**Follow-up:** Can `ROLLBACK` later undo it?  
**Mistake:** Treating commit as a savepoint.

### 5. What does `ROLLBACK` do?

**Concise:** Discards uncommitted transaction work.  
**Deeper:** It is a recovery boundary for a transaction attempt.  
**SQL:** `BEGIN; UPDATE ...; ROLLBACK;`  
**Follow-up:** What about work already committed?  
**Mistake:** Thinking rollback erases committed history.

### 6. What is autocommit?

**Concise:** A mode where statements can commit automatically.  
**Deeper:** Driver/client configuration determines the actual transaction boundaries.  
**SQL:** A standalone `UPDATE` may commit immediately.  
**Follow-up:** Why risky for bulk publication?  
**Mistake:** Assuming multiple statements are automatically grouped.

### 7. What is `SAVEPOINT`?

**Concise:** A partial rollback marker inside a transaction.  
**Deeper:** `ROLLBACK TO SAVEPOINT` retains the outer transaction.  
**SQL:** `SAVEPOINT s; ... ROLLBACK TO SAVEPOINT s;`  
**Follow-up:** Does it commit?  
**Mistake:** Calling it a nested transaction.

### 8. Why are transactions important for data pipelines?

**Concise:** They make critical publication and coordination steps atomic.  
**Deeper:** They control partial failure, worker contention, and state visibility.  
**SQL:** staging followed by short `BEGIN`/apply/`COMMIT`.  
**Follow-up:** Should the whole pipeline be one transaction?  
**Mistake:** Making the transaction enormous.

### 9. What is PostgreSQL `READ COMMITTED`?

**Concise:** PostgreSQL's default level; each statement gets an appropriate committed view.  
**Deeper:** Separate statements can observe commits that happened between them.  
**SQL:** `BEGIN ISOLATION LEVEL READ COMMITTED;`  
**Follow-up:** Can two reads differ?  
**Mistake:** Calling it a transaction-wide snapshot.

### 10. What is PostgreSQL's default isolation level?

**Concise:** `READ COMMITTED`.  
**Deeper:** The default is engine-specific.  
**SQL:** `SHOW transaction_isolation;`  
**Follow-up:** What anomaly can occur at this level?  
**Mistake:** Assuming every engine defaults the same way.

### 11. What is `READ UNCOMMITTED` in PostgreSQL?

**Concise:** It behaves like `READ COMMITTED`.  
**Deeper:** PostgreSQL does not expose ordinary dirty reads through this setting.  
**SQL:** `BEGIN ISOLATION LEVEL READ UNCOMMITTED;`  
**Follow-up:** Is that universal?  
**Mistake:** Importing another database's dirty-read semantics.

### 12. What is `REPEATABLE READ`?

**Concise:** A transaction-level stable snapshot for ordinary reads in PostgreSQL.  
**Deeper:** Concurrent write conflicts can still cause a transaction failure.  
**SQL:** `BEGIN ISOLATION LEVEL REPEATABLE READ;`  
**Follow-up:** What happens on a conflicting update?  
**Mistake:** Assuming every transaction always commits.

### 13. What is `SERIALIZABLE`?

**Concise:** Successful behavior must be equivalent to some serial ordering.  
**Deeper:** Concurrent work can proceed, but unsafe interleavings can be rejected.  
**SQL:** `BEGIN ISOLATION LEVEL SERIALIZABLE;`  
**Follow-up:** Does it physically serialize all sessions?  
**Mistake:** Answering yes.

### 14. What is a dirty read?

**Concise:** Reading uncommitted data from another transaction.  
**Deeper:** The value may later disappear if the writer rolls back.  
**SQL:** Conceptual two-session example.  
**Follow-up:** Does PostgreSQL permit it?  
**Mistake:** Assuming `READ UNCOMMITTED` always does.

### 15. What is a non-repeatable read?

**Concise:** The same transaction reads a row twice and sees different committed values.  
**Deeper:** This is possible under PostgreSQL `READ COMMITTED`.  
**SQL:** A reads; B updates/commits; A reads again.  
**Follow-up:** How does repeatable read change it?  
**Mistake:** Confusing it with a phantom.

### 16. What is a phantom read?

**Concise:** A repeated predicate query sees a different qualifying row set.  
**Deeper:** It is about a read set, not just one row's value.  
**SQL:** `SELECT ... WHERE status = 'ready';`  
**Follow-up:** Why does a business invariant care?  
**Mistake:** Treating it as exactly the same as a non-repeatable read.

### 17. What is a lost update?

**Concise:** One logical update overwrites another concurrent update.  
**Deeper:** Common in application read-modify-write flows.  
**SQL:** `UPDATE ... SET value = value + 1`.  
**Follow-up:** Could `FOR UPDATE` solve it?  
**Mistake:** Assuming transactions automatically prevent it.

### 18. What is write skew?

**Concise:** Different row updates jointly violate a multi-row invariant.  
**Deeper:** Each transaction can be locally valid while the combined state is invalid.  
**SQL:** Two-doctor example.  
**Follow-up:** How can `SERIALIZABLE` help?  
**Mistake:** Treating it as a single-row overwrite.

### 19. Explain MVCC.

**Concise:** Multi-Version Concurrency Control uses multiple row versions and visibility rules.  
**Deeper:** It lets readers and writers often progress concurrently.  
**SQL:** Conceptual row-version timeline.  
**Follow-up:** Does MVCC eliminate locks?  
**Mistake:** Saying yes.

### 20. What is a transaction snapshot?

**Concise:** A snapshot determines which row versions are visible.  
**Deeper:** Snapshot lifetime matters to repeatable reads and cleanup.  
**SQL:** `REPEATABLE READ` example.  
**Follow-up:** How can long transactions affect vacuum?  
**Mistake:** Treating snapshots as only a query feature.

### 21. Why can readers and writers often proceed concurrently?

**Concise:** MVCC lets readers use visible row versions while writes create newer versions.  
**Deeper:** Not every read must wait for every write.  
**SQL:** Normal `SELECT` alongside `UPDATE`.  
**Follow-up:** Can reads ever block?  
**Mistake:** "Readers never block anything."

### 22. Does MVCC eliminate locks?

**Concise:** No.  
**Deeper:** Writes, explicit row locks, DDL, and coordination still involve locks.  
**SQL:** `SELECT ... FOR UPDATE`.  
**Follow-up:** Visibility versus locking?  
**Mistake:** Treating MVCC as a lock-free system.

### 23. What is `SELECT FOR UPDATE`?

**Concise:** Selects rows while requesting update-strength row locks.  
**Deeper:** Useful when decisions depend on a row that must not change concurrently.  
**SQL:** `SELECT ... FOR UPDATE;`  
**Follow-up:** Why not lock every query?  
**Mistake:** Over-locking.

### 24. What is `SELECT FOR SHARE`?

**Concise:** Requests a shared row lock.  
**Deeper:** It communicates shared locking intent and can matter for integrity-sensitive operations.  
**SQL:** `SELECT ... FOR SHARE;`  
**Follow-up:** What conflicts with it?  
**Mistake:** Guessing compatibility from the name alone.

### 25. `NOWAIT` vs `SKIP LOCKED`?

**Concise:** `NOWAIT` fails immediately; `SKIP LOCKED` ignores locked rows.  
**Deeper:** They encode different scheduling policies.  
**SQL:** `FOR UPDATE NOWAIT` vs `FOR UPDATE SKIP LOCKED`.  
**Follow-up:** When is skipping unsafe?  
**Mistake:** Using `SKIP LOCKED` everywhere.

### 26. How would you build a work queue?

**Concise:** Claim eligible rows atomically with row locking and `SKIP LOCKED`.  
**Deeper:** Claim + state transition should be one transaction.  
**SQL:** Section 39 query.  
**Follow-up:** How do you recover abandoned jobs?  
**Mistake:** Forgetting post-crash recovery.

### 27. Why can `SKIP LOCKED` be dangerous?

**Concise:** It can skip work that is not legally or logically safe to skip.  
**Deeper:** It should be used only when another unlocked item can safely be processed first.  
**SQL:** Queue example.  
**Follow-up:** What if jobs have strict sequence?  
**Mistake:** Treating reduced blocking as automatic correctness.

### 28. What is a serialization failure?

**Concise:** The database rejects a transaction that cannot safely satisfy its isolation semantics under the current concurrent schedule.  
**Deeper:** This can be expected under `SERIALIZABLE` or stronger snapshot conflicts.  
**SQL:** `BEGIN ISOLATION LEVEL SERIALIZABLE;`  
**Follow-up:** How do you recover?  
**Mistake:** Treating it as a syntax error.

### 29. How should a Data Engineer retry a serialization failure?

**Concise:** Roll back and retry the whole transaction with bounded backoff.  
**Deeper:** Earlier reads may be part of the failed transaction's dependency graph.  
**SQL:** Conceptual retry loop.  
**Follow-up:** What makes an error permanent instead?  
**Mistake:** Retrying just one statement.

### 30. What is a deadlock?

**Concise:** Circular waiting between transactions.  
**Deeper:** Each participant holds a resource needed by another.  
**SQL:** Two rows, opposite order.  
**Follow-up:** How does PostgreSQL handle it?  
**Mistake:** Calling every wait a deadlock.

### 31. How does PostgreSQL detect deadlocks?

**Concise:** It detects a cycle in lock waits and aborts one participant.  
**Deeper:** Aborting one victim breaks the cycle.  
**SQL:** Two-session deadlock lab.  
**Follow-up:** Is the same victim always chosen?  
**Mistake:** Assuming a fixed victim.

### 32. How do you prevent deadlocks?

**Concise:** Consistent lock ordering, small transactions, minimal locks, and retry of transient victims.  
**Deeper:** Prevention removes cycles; retry handles residual transient conflict.  
**SQL:** Lock IDs ascending.  
**Follow-up:** What if two code paths need different resource sets?  
**Mistake:** Relying only on timeouts.

### 33. Why is lock ordering important?

**Concise:** A common global order prevents cyclic acquisition.  
**Deeper:** All paths acquire resource 1 before resource 2.  
**SQL:** `ORDER BY id` before locking.  
**Follow-up:** Does ordering need to be documented?  
**Mistake:** Assuming query order is accidental and harmless.

### 34. Why should transactions be short?

**Concise:** Short transactions reduce lock retention, snapshot lifetime, blocking, and cleanup pressure.  
**Deeper:** Transaction duration is an operational capacity constraint.  
**SQL:** Staging then apply.  
**Follow-up:** Does short mean one statement?  
**Mistake:** Making the atomic unit too small or too large.

### 35. How can long transactions affect VACUUM?

**Concise:** Long-lived snapshots can prevent some obsolete versions from being safely removed.  
**Deeper:** This can contribute to dead tuples and bloat pressure.  
**SQL:** Inspect old transactions in production observability tooling.  
**Follow-up:** What is idle in transaction?  
**Mistake:** Saying vacuum simply stops everywhere.

### 36. How can long transactions affect replication?

**Concise:** Depending on architecture and workload, long/large transactions can complicate replication progress and contribute to lag.  
**Deeper:** The effect depends on transaction size, commit behavior, replay, and architecture.  
**SQL:** No universal SQL fix; monitor actual lag.  
**Follow-up:** What would you monitor?  
**Mistake:** Claiming every long transaction automatically causes lag.

### 37. What is `lock_timeout`?

**Concise:** A bound on waiting for locks.  
**Deeper:** Useful for migrations and operational fail-fast behavior.  
**SQL:** `SET LOCAL lock_timeout = '2s';`  
**Follow-up:** Difference from `statement_timeout`?  
**Mistake:** Treating it as execution timeout.

### 38. What is `statement_timeout`?

**Concise:** A bound on statement execution time.  
**Deeper:** It protects against runaway statements, not specifically lock waits.  
**SQL:** `SET statement_timeout = '30s';`  
**Follow-up:** When can both apply?  
**Mistake:** Confusing the two timeout domains.

### 39. How can DDL block production?

**Concise:** Some schema changes require strong table coordination and can wait behind active transactions.  
**Deeper:** DDL can participate in the same lock queue as pipeline/reporting work.  
**SQL:** `ALTER TABLE ...`.  
**Follow-up:** How would you fail fast?  
**Mistake:** Deploying DDL without a lock budget.

### 40. What is staging-then-apply?

**Concise:** Prepare and validate data first; publish it in a short transaction.  
**Deeper:** It separates slow preparation from atomic publication.  
**SQL:** `BEGIN` + target apply + assertions + `COMMIT`.  
**Follow-up:** Where does extraction happen?  
**Mistake:** Holding target locks during parsing.

### 41. What is staging-then-swap?

**Concise:** Build a replacement state separately, then perform a short publication operation.  
**Deeper:** It can reduce the reader-facing critical window.  
**SQL:** Exact swap mechanism depends on dependencies.  
**Follow-up:** What dependencies matter?  
**Mistake:** Assuming rename is always safe.

### 42. What is an advisory lock?

**Concise:** A PostgreSQL application-defined lock keyed by an agreed identifier.  
**Deeper:** It is cooperative; participants must use the same key.  
**SQL:** `SELECT pg_advisory_lock(12345);`  
**Follow-up:** Session-scoped versus transaction-scoped?  
**Mistake:** Treating it as a data constraint.

### 43. How prevent two pipeline runs simultaneously?

**Concise:** Use a stable advisory key and a hard database invariant where applicable.  
**Deeper:** Coordination and correctness should be layered.  
**SQL:** `SELECT pg_try_advisory_lock(12345);`  
**Follow-up:** What if lock acquisition fails?  
**Mistake:** Using unstable keys.

### 44. How does DuckDB differ from PostgreSQL?

**Concise:** DuckDB is a single-node analytical database with ACID transactions and a single-writer model in this chapter's architecture context.  
**Deeper:** Multi-writer PostgreSQL worker assumptions may not transfer.  
**SQL:** Verify exact behavior for your DuckDB version.  
**Follow-up:** Are concurrent reads possible?  
**Mistake:** Saying DuckDB has no concurrency.

### 45. How can warehouse concurrency differ?

**Concise:** Warehouses can use different storage, isolation, locking, and execution architectures.  
**Deeper:** Concurrency must be designed from vendor-specific semantics.  
**SQL:** No universal cross-warehouse example.  
**Follow-up:** What do you read first?  
**Mistake:** Porting PostgreSQL locking assumptions.

### 46. What is lakehouse optimistic concurrency?

**Concise:** Writers validate that conflicting table state did not change before commit.  
**Deeper:** Conflict detection occurs around commit/version validation rather than traditional row locks alone.  
**SQL:** Conceptual only.  
**Follow-up:** Why doesn't `FOR UPDATE` map directly?  
**Mistake:** Treating file/table versions as rows.

### 47. How debug a production deadlock?

**Concise:** Reconstruct sessions, resources, lock holders, requested locks, order, and timing.  
**Deeper:** Build a wait graph and identify the common cycle.  
**SQL:** Two-session reproducer plus production lock diagnostics.  
**Follow-up:** What prevention changes would you make?  
**Mistake:** Looking only at one transaction's error.

### 48. How diagnose intermittent serialization failures?

**Concise:** Identify the transaction invariant, concurrent actors, isolation level, frequency, retry behavior, and contention pattern.  
**Deeper:** A serialization error can be expected; the design question is whether the retries and isolation cost are acceptable.  
**SQL:** `BEGIN ISOLATION LEVEL SERIALIZABLE; ... COMMIT;`  
**Follow-up:** Could explicit row locking solve the invariant more simply?  
**Mistake:** Treating every failure as a reason to use lower isolation.

---

## 74. Production Checklist

Before shipping a concurrent database workflow:

- [ ] Transaction boundary explicitly defined.
- [ ] Business invariant explicitly defined.
- [ ] ACID requirements understood.
- [ ] Autocommit behavior known.
- [ ] Failure and rollback behavior understood.
- [ ] `SAVEPOINT` used only where partial rollback is required.
- [ ] Isolation level intentionally selected.
- [ ] PostgreSQL-specific isolation behavior considered.
- [ ] Lost-update risk considered.
- [ ] Write-skew risk considered.
- [ ] MVCC visibility understood.
- [ ] Required row locks explicit.
- [ ] `FOR UPDATE` used only where necessary.
- [ ] `FOR SHARE` intentional.
- [ ] `NOWAIT` used when waiting is undesirable.
- [ ] `SKIP LOCKED` used only when skipping is safe.
- [ ] Queue claim and state transition are atomic.
- [ ] Serialization failures have retry handling.
- [ ] Deadlock retries are considered.
- [ ] Lock order is consistent and documented.
- [ ] Transactions are as short as practical.
- [ ] External network calls are not unnecessarily performed while holding locks.
- [ ] Long-running transactions are monitored.
- [ ] VACUUM/cleanup implications are understood.
- [ ] Replication implications are considered where relevant.
- [ ] DDL locking risk is understood.
- [ ] `lock_timeout` is configured where appropriate.
- [ ] `statement_timeout` is configured where appropriate.
- [ ] Staging is separated from final atomic publication where useful.
- [ ] Advisory-lock keys are stable and documented.
- [ ] Database constraints still provide hard correctness where appropriate.
- [ ] Concurrency tests have been run with multiple sessions.
- [ ] Failure/retry behavior has been tested.
- [ ] Post-transaction assertions validate the final state.

---

## 75. Final Knowledge Check

Do not answer these only from memory. For the practical items, use SQL and explicit two-session reasoning.

### Core concepts

1. Define a transaction.
2. Explain all four ACID properties.
3. Give an example of atomicity protecting a daily batch.
4. Give a database invariant that expresses consistency.
5. Explain how isolation differs from atomicity.
6. Explain durability without claiming impossible hardware guarantees.
7. What does `BEGIN` do?
8. What does `COMMIT` do?
9. What does `ROLLBACK` do?
10. How does autocommit affect transaction boundaries?
11. What is `SAVEPOINT`?
12. Why is atomicity different from "one giant pipeline transaction"?

### Isolation and anomalies

13. What is PostgreSQL's default isolation level?
14. What does PostgreSQL do with `READ UNCOMMITTED`?
15. Define a dirty read.
16. Define a non-repeatable read.
17. Define a phantom/read-set change.
18. Define a lost update.
19. Define write skew.
20. Explain PostgreSQL `REPEATABLE READ`.
21. Explain PostgreSQL `SERIALIZABLE`.
22. Does serializable mean literal one-at-a-time execution?
23. Which anomalies are primarily visibility problems versus state-transition problems?
24. Why can a row-level lock fail to protect a multi-row invariant?

### MVCC and locks

25. Define MVCC.
26. What is a transaction snapshot?
27. Why can readers and writers often proceed concurrently?
28. Why does MVCC not eliminate locks?
29. What does `FOR UPDATE` do?
30. What does `FOR SHARE` do?
31. What does `NOWAIT` do?
32. What does `SKIP LOCKED` do?
33. Why can `SKIP LOCKED` be unsafe?
34. Build a queue claim query.
35. Explain the lifecycle `ready → running → completed`.

### Failures

36. What is a serialization failure?
37. What is a deadlock?
38. How does PostgreSQL respond to a deadlock?
39. Why should a deadlock victim retry the whole transaction?
40. Why is retrying only the failed statement unsafe?
41. What should bounded retry logic contain?

### Operations

42. What is `lock_timeout`?
43. What is `statement_timeout`?
44. Give an example of each.
45. Why are long-running transactions dangerous?
46. How can long transactions interact with VACUUM?
47. How can they contribute to replication problems depending on architecture?
48. How can DDL block production?
49. Why can `lock_timeout` be useful during schema deployment?

### Pipeline architecture

50. Explain staging-then-apply.
51. Explain staging-then-swap.
52. Why should slow external work usually happen outside the final publication transaction?
53. What is an advisory lock?
54. How would you prevent duplicate singleton pipeline execution?
55. Why should a database constraint still provide hard correctness where possible?
56. Explain DuckDB's single-writer model.
57. Why should warehouse concurrency be treated separately from PostgreSQL?
58. What is lakehouse optimistic concurrency?

### Practical two-session tasks

59. Reproduce a non-repeatable read at `READ COMMITTED`.
60. Demonstrate a stable snapshot at `REPEATABLE READ`.
61. Reproduce a lost update and fix it with an atomic update.
62. Reproduce and fix a lost update with `FOR UPDATE`.
63. Demonstrate `NOWAIT`.
64. Demonstrate `SKIP LOCKED`.
65. Demonstrate a write-skew scenario.
66. Demonstrate a deadlock.
67. Demonstrate a DDL lock wait and protect the migration with `lock_timeout`.
68. Demonstrate a serialization failure and the full retry sequence.

### Design task

69. Design the concurrency strategy for a multi-worker daily customer load.
70. Explicitly state the invariant.
71. Identify all concurrent actors.
72. Define the transaction boundary.
73. Select the isolation level and justify it.
74. Select row-lock behavior and justify it.
75. Define failure and retry behavior.
76. Define timeout behavior.
77. Define post-transaction assertions.
78. Explain why you did not simply use `SERIALIZABLE` everywhere.

---

## 76. Checkpoint — Ready for Topic 10?

The learner must be able to demonstrate all five capabilities below.

### 1. Explain ACID and each isolation level

Explain:

```text
Atomicity
Consistency
Isolation
Durability
```

and:

```text
READ UNCOMMITTED
READ COMMITTED
REPEATABLE READ
SERIALIZABLE
```

**Practical demonstration:** Explain a two-session visibility example and state what each session sees.

### 2. Reproduce and prevent a lost update

Reproduce:

```text
A reads 10
B reads 10
A writes 11
B writes 11
```

Then prevent it with either an atomic expression:

```sql
UPDATE counters
SET value = value + 1
WHERE counter_id = 1;
```

or:

```sql
SELECT value
FROM counters
WHERE counter_id = 1
FOR UPDATE;
```

**Practical demonstration:** Run the two-session lab and explain why the safe version preserves both logical updates.

### 3. Explain MVCC in two sentences

A strong answer is:

> PostgreSQL uses multiple row versions and visibility rules so transactions can often read a consistent version while writers create newer versions. This reduces the need for every reader to block every writer, but it does not eliminate locks.

**Practical demonstration:** Explain:

```text
T1 snapshot
T2 commits
T1 reads
```

under both `READ COMMITTED` and `REPEATABLE READ`.

### 4. Use `SKIP LOCKED` for a work queue

Write and explain:

```sql
SELECT job_id
FROM jobs
WHERE status = 'ready'
ORDER BY job_id
FOR UPDATE SKIP LOCKED
LIMIT 10;
```

**Practical demonstration:** Run two worker sessions and show that the second claims another unlocked batch instead of waiting on the first worker's locked rows.

### 5. Explain why long transactions and unguarded DDL are dangerous

Explain:

```text
long transaction
→ long-lived snapshot / lock retention
→ cleanup + blocking pressure
```

and:

```text
unguarded DDL
→ lock conflict
→ migration waits
→ deployment risk
```

**Practical demonstration:** Run the DDL lab using `lock_timeout` and explain the blocking/failure timeline.

---

# Final Senior-Level Mental Model

Use this sequence whenever you design or debug a concurrent data workflow:

```text
Define the invariant
        ↓
Identify concurrent actors
        ↓
Define the atomic state transition
        ↓
Choose transaction boundary
        ↓
Choose isolation
        ↓
Choose the minimum necessary lock strategy
        ↓
Bound waits / statement duration
        ↓
Define retry behavior
        ↓
Validate post-conditions
        ↓
Test with concurrent sessions
        ↓
Monitor in production
```

The durable lesson is:

> **Concurrency correctness is about defining the state transitions that must be atomic, determining what concurrent transactions are allowed to observe or modify, and selecting the minimum controls necessary to preserve those invariants.**

## Final Common-Mistake Summary

Do not rely on autocommit unintentionally. Do not forget transaction boundaries. Do not expect `ROLLBACK` to undo already committed work. Do not make transactions larger than necessary or hold database locks while performing slow external work. Do not guess isolation semantics from names alone. Do not assume PostgreSQL `READ UNCOMMITTED` exposes dirty reads. Do not confuse MVCC with "no locks." Do not use locks without stating the invariant. Do not use `SKIP LOCKED` when work cannot safely be skipped. Do not omit retries for retryable serialization/deadlock failures. Do not retry only a failed statement. Do not acquire resources in inconsistent orders. Do not leave transactions open. Do not ignore VACUUM/cleanup, DDL lock risk, timeouts, or relevant replication effects. Do not create unstable advisory-lock conventions or treat advisory locks as constraints. Do not assume PostgreSQL, DuckDB, warehouses, and lakehouses share concurrency semantics. Do not debug concurrency without a session timeline.

## Code and Experiment Safety

- PostgreSQL 16+ is the primary environment.
- DuckDB is secondary awareness only.
- All multi-session material remains inside this Markdown file.
- Run concurrency experiments locally, never against production.
- For destructive experiments, use explicit transactions and `ROLLBACK` when appropriate.
- Remember that `EXPLAIN ANALYZE` on data-modifying statements actually executes them.
- End experiments deliberately; never leave a session idle in transaction.
- Treat timeline output in this chapter as teaching examples, not as observed production output.

## Topic Boundary

Topic 10 builds on these transaction concepts. This chapter does **not** teach MERGE, upsert, or SCD implementation as standalone topics. Use this chapter to establish the concurrency foundation that Topic 10 will rely on.
