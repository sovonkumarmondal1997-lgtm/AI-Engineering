# Transaction Control from Python

## Learning Objectives

By the end of this module, you should be able to:

- Explain a database transaction as a deliberate unit of work.
- Explain when a psycopg 3 transaction starts and ends.
- Use `commit()` and `rollback()` correctly.
- Use `conn.transaction()` to create explicit transaction boundaries.
- Explain PostgreSQL's default transaction behavior from Python.
- Use autocommit deliberately rather than globally.
- Use nested transaction contexts as savepoints.
- Recover from a failed transaction state.
- Configure transaction isolation from Python.
- Use read-only transaction/session settings as a safety guardrail.
- Detect and diagnose `idle in transaction`.
- Use `idle_in_transaction_session_timeout` as a protective control.
- Keep transactions short and avoid external I/O inside open transactions.
- Distinguish retryable transient failures from permanent failures.
- Retry the **whole transaction** rather than only a failed statement.
- Use backoff for transaction retries.
- Reproduce and reason about serialization failures.
- Understand deadlocks and `DeadlockDetected`.
- Reason about unknown commit outcomes.
- Design idempotent database operations so retries are safe.
- Record pipeline execution status independently from the main transaction.
- Explain why two ordinary transactions across two databases do not provide simple atomicity.
- Understand two-phase commit at an awareness level.
- Review transaction code from both the Python side and PostgreSQL side.
- Defend transaction-boundary decisions in code reviews and architecture discussions.

---

## Prerequisites

You should already have completed:

- `01-db-api-pep-249-connections-and-cursors.md`
- `02-postgresql-from-python-with-psycopg.md`
- `03-parameterized-queries-and-sql-injection.md`

Topic 01 established DB-API transaction basics.

Topic 02 established psycopg 3 connectivity and PostgreSQL session behavior.

Topic 03 established safe query construction.

Module 2.6 taught transactions at the SQL level.

This topic teaches what transaction control looks like when **Python and psycopg own the database interaction lifecycle**.

> **Scope boundary:** connection pooling belongs to Topic 05. SQLAlchemy, Alembic, bulk loading, and large-result streaming belong to later topics. They may be referenced, but their implementation details are intentionally deferred.

---

# Why Transaction Control Matters

A transaction is not just an SQL feature.

It is an **application boundary**.

In a Data Engineering pipeline, Python often coordinates several database operations:

```text
read state
    ↓
validate
    ↓
write metadata
    ↓
update target
    ↓
record result
```

The engineer must decide:

> Which of these actions must succeed or fail together?

That is a transaction-boundary decision.

The difference between correct SQL and correct transaction engineering is important.

This SQL can be perfectly valid:

```sql
UPDATE orders
SET status = 'processed'
WHERE id = 123;
```

but the surrounding Python can still be operationally wrong if it:

- starts a transaction;
- calls an external API;
- sleeps for several minutes;
- performs expensive Python processing;
- forgets to commit or roll back.

A database transaction can therefore be **logically correct but operationally badly scoped**.

The central production mental model is:

```text
Transaction boundaries
+
Failure boundaries
+
Retry boundaries
+
Consistency boundaries
```

---

# 1. What Is a Transaction?

A transaction is a unit of database work that PostgreSQL treats as one logical unit for transaction semantics.

At the simplest level:

```text
START
  ↓
operations
  ↓
COMMIT
```

or:

```text
START
  ↓
operations
  ↓
ERROR
  ↓
ROLLBACK
```

## 1.1 Why does a transaction exist?

Imagine moving money:

```text
decrease account A
increase account B
```

If the first operation succeeds but the second never happens, the database could be left in an incorrect state.

A transaction provides a boundary where the intended work can be treated atomically:

```text
both succeed
    or
the transaction is rolled back
```

The full theory of atomicity, isolation, visibility, and locking was introduced in the earlier SQL curriculum.

Here, the focus is:

> **How does Python control that transaction through psycopg?**

---

# 2. The Python ↔ PostgreSQL Transaction Model

Think in both directions:

```text
Python process
      ↕
psycopg
      ↕
PostgreSQL session
      ↕
transaction state
      ↕
database changes / locks / visibility
```

A Python call such as:

```python
conn.commit()
```

is not simply:

> "save the Python object."

It means:

> **Complete the current database transaction according to PostgreSQL transaction semantics.**

Similarly:

```python
conn.rollback()
```

does not mean:

> "undo everything this Python program has ever done."

It means:

> **Abort the current transaction and discard the transaction's uncommitted database changes.**

This distinction is foundational.

---

# 3. psycopg Default Transaction Behavior

With psycopg 3, a connection normally operates with transaction behavior where the first database statement starts transaction activity.

Consider:

```python
with psycopg.connect(...) as conn:
    conn.execute(
        "INSERT INTO pipeline_events (event_id) VALUES (%s)",
        (1,),
    )
    conn.execute(
        "INSERT INTO pipeline_events (event_id) VALUES (%s)",
        (2,),
    )
    conn.commit()
```

Conceptually:

```text
connection established
        ↓
first statement
        ↓
transaction becomes active
        ↓
second statement
        ↓
commit
        ↓
transaction completes
```

The application did not have to write:

```sql
BEGIN;
```

explicitly for transaction activity to matter.

## 3.1 Why is this surprising?

A beginner might see:

```python
conn.execute("SELECT ...")
```

and think:

> "It's only a SELECT. Why should I care about transaction state?"

But PostgreSQL sessions can have transaction state even when application code did not explicitly type `BEGIN`.

That matters for:

- snapshot/visibility;
- locks;
- cleanup;
- vacuum;
- DDL;
- connection lifecycle.

## 3.2 Production rule

> Never assume transaction state is inactive merely because your Python code did not explicitly call `BEGIN`.

---

# 4. `commit()`

The basic API is:

```python
conn.commit()
```

## 4.1 What does commit mean?

It completes the current transaction and makes the transaction's successful changes durable according to PostgreSQL's commit semantics.

A useful mental model is:

```text
transaction
    ↓
all required operations succeeded
    ↓
COMMIT
    ↓
transaction complete
```

## 4.2 Simple example

```python
import psycopg

with psycopg.connect(...) as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS demo_items (
            id integer PRIMARY KEY,
            name text NOT NULL
        )
        """
    )

    conn.execute(
        "INSERT INTO demo_items (id, name) VALUES (%s, %s)",
        (1, "alpha"),
    )

    conn.commit()
```

The commit boundary is explicit.

## 4.3 Commit too often

Consider:

```python
for row in rows:
    conn.execute(
        "INSERT INTO demo_items (id, name) VALUES (%s, %s)",
        (row.id, row.name),
    )
    conn.commit()
```

This creates many transaction boundaries.

At a conceptual level:

```text
insert 1 → commit
insert 2 → commit
insert 3 → commit
...
```

The cost is not merely syntax.

Frequent commits can increase:

- commit overhead;
- network coordination;
- transaction management overhead;
- partial-progress complexity.

For a multi-step logical unit, a single deliberate transaction is often easier to reason about.

## 4.4 Commit too late

The opposite problem is:

```python
conn.execute(...)
slow_python_work()
call_external_api()
sleep()
more_database_work()
conn.commit()
```

Now the transaction remains open while Python is doing unrelated work.

That increases operational risk.

The correct question is:

> **What work truly belongs inside this transaction?**

---

# 5. `rollback()`

The basic API is:

```python
conn.rollback()
```

Rollback aborts the current transaction.

## 5.1 What rollback undoes

Changes made during the current uncommitted transaction are discarded according to PostgreSQL transaction semantics.

For example:

```python
conn.execute(
    "INSERT INTO demo_items (id, name) VALUES (%s, %s)",
    (1, "alpha"),
)

conn.rollback()
```

The uncommitted insert does not remain as a committed database change.

## 5.2 What rollback does not mean

Rollback is not:

```text
delete this row
```

It is:

```text
abort the current transaction
```

That distinction becomes very important when a transaction contains many operations.

## 5.3 Explicit exception handling

A classic pattern is:

```python
try:
    conn.execute(...)
    conn.execute(...)
    conn.commit()
except Exception:
    conn.rollback()
    raise
```

The `raise` matters.

It preserves the original failure rather than hiding it.

However, when possible, psycopg's transaction context manager can make the boundary clearer and harder to misuse.

---

# 6. `conn.transaction()`

This is the preferred explicit transaction-boundary pattern for many psycopg programs.

```python
with conn.transaction():
    conn.execute(...)
    conn.execute(...)
```

Conceptually:

```text
enter transaction block
        ↓
run database operations
        ↓
success → commit
failure → rollback
```

## 6.1 Simple example

```python
import psycopg

with psycopg.connect(...) as conn:
    with conn.transaction():
        conn.execute(
            """
            INSERT INTO pipeline_events (event_id)
            VALUES (%s)
            """,
            (1,),
        )

        conn.execute(
            """
            INSERT INTO pipeline_events (event_id)
            VALUES (%s)
            """,
            (2,),
        )
```

The two writes are intentionally grouped.

## 6.2 Failure behavior

```python
try:
    with psycopg.connect(...) as conn:
        with conn.transaction():
            conn.execute(
                "INSERT INTO pipeline_events (event_id) VALUES (%s)",
                (1,),
            )

            raise RuntimeError("simulated failure")
except RuntimeError:
    print("Transaction was rolled back")
```

The context manager creates a clear failure boundary.

## 6.3 Why this is useful

The code directly expresses:

```text
these operations are one unit
```

That is better than scattering:

```python
commit()
rollback()
```

through unrelated functions without a clear boundary.

---

# 7. Transaction Boundaries

A transaction boundary answers:

> **Exactly which database operations must succeed or fail together?**

## 7.1 Good boundary

Suppose a pipeline is performing a small atomic state change:

```text
BEGIN
  ↓
update state
  ↓
insert audit row
  ↓
COMMIT
```

If either operation fails, neither should be committed.

## 7.2 Bad boundary

A dangerous transaction might look like:

```text
BEGIN
  ↓
database work
  ↓
call HTTP API
  ↓
sleep 30 seconds
  ↓
read a large file
  ↓
perform expensive Python transformation
  ↓
more database work
  ↓
COMMIT
```

The database transaction now depends on unrelated external activity.

## 7.3 Why external I/O inside a transaction is risky

The longer the transaction stays open, the more likely it is to:

- retain a snapshot;
- hold locks longer;
- contend with concurrent work;
- delay cleanup;
- encounter additional failures;
- become visible as `idle in transaction`.

A strong rule is:

> **Do not call an external API, read a large file, or sleep inside an open transaction unless that is a deliberate and justified design requirement.**

---

# 8. Autocommit

psycopg can be configured with:

```python
conn = psycopg.connect(
    ...,
    autocommit=True,
)
```

## 8.1 What changes?

In normal transaction mode:

```text
statement A
statement B
statement C
       ↓
commit
```

In autocommit mode, statements are committed individually in the normal case:

```text
statement A → commit
statement B → commit
statement C → commit
```

There is no automatic multi-statement atomic unit around all three.

## 8.2 Why does autocommit exist?

Some PostgreSQL commands cannot run inside a normal transaction block or are commonly used in a mode where autocommit is appropriate.

Examples include:

- `CREATE DATABASE`;
- `VACUUM`;
- some maintenance commands.

The exact command restrictions are PostgreSQL-specific.

## 8.3 Example

```python
import psycopg

with psycopg.connect(..., autocommit=True) as conn:
    conn.execute("VACUUM")
```

The exact PostgreSQL version, command, and environment still matter.

## 8.4 Why not enable autocommit everywhere?

Because multi-step pipeline operations often need atomicity.

Suppose:

```python
conn.execute("UPDATE A ...")
conn.execute("UPDATE B ...")
```

Under autocommit:

```text
UPDATE A → committed
UPDATE B → fails
```

Now A remains changed.

Under a deliberate transaction:

```text
UPDATE A
UPDATE B
    ↓
if B fails
    ↓
rollback
```

The choice depends on the semantics of the work.

---

# 9. Normal Transaction Mode vs Autocommit

| Aspect | Normal transaction mode | Autocommit |
|---|---|---|
| Multiple statements as one atomic unit | Yes | No, in the normal autocommit pattern |
| Explicit transaction boundary | Yes | Each statement is completed independently |
| Useful for multi-step pipeline logic | Often | Often not |
| Useful for commands with transaction restrictions | Sometimes restricted | Often appropriate |
| Risk of unintended long transaction | Exists | Reduced |
| Requires deliberate transaction design | Yes | Still required for multi-step atomic workflows |

There is no universal "always normal" or "always autocommit" rule.

The correct decision comes from the command and consistency requirement.

---

# 10. Savepoints and Nested Transactions

Now suppose you have 100 logical batches.

```text
batch 1
batch 2
...
batch 100
```

Batch 37 fails.

You might want:

```text
batches 1–36 → keep
batch 37 → reject
batches 38–100 → keep
```

rather than rolling everything back.

That is where a **savepoint** is useful.

A savepoint creates an intermediate recovery boundary inside an outer transaction.

---

# 11. Nested `conn.transaction()` as Savepoint Behavior

psycopg supports nested transaction blocks.

Conceptually:

```python
with conn.transaction():
    # outer transaction

    ...

    with conn.transaction():
        # nested transaction / savepoint
        ...
```

The outer block represents the main transaction.

The nested block can be treated as a savepoint boundary.

Conceptually:

```text
OUTER TRANSACTION
      ↓
batch 1
      ↓
SAVEPOINT
      ↓
batch 2
      ↓
ERROR
      ↓
ROLLBACK TO SAVEPOINT
      ↓
OUTER TRANSACTION CONTINUES
      ↓
COMMIT
```

The exact API semantics should follow psycopg 3 documentation for the version in use, but the important mental model is:

> **A nested transaction block can give one part of the work a smaller rollback boundary without aborting the outer transaction.**

---

# 12. Savepoint Lab — 100 Batches

The roadmap requires a 100-batch exercise where batch 37 is deliberately bad.

> ⚠️ **INTENTIONALLY FAILING TRANSACTION EXAMPLE**
>
> Use only a disposable local Docker PostgreSQL database.

## 12.1 Example tables

```sql
CREATE TABLE IF NOT EXISTS batch_items (
    item_id integer PRIMARY KEY,
    batch_id integer NOT NULL,
    payload text NOT NULL
);

CREATE TABLE IF NOT EXISTS rejected_batches (
    batch_id integer PRIMARY KEY,
    reason text NOT NULL,
    rejected_at timestamptz NOT NULL DEFAULT now()
);
```

## 12.2 Code

```python
import psycopg


def load_batches(conn, batches: list[list[tuple[int, int, str]]]) -> None:
    with conn.transaction():
        for batch_number, batch in enumerate(batches, start=1):
            try:
                with conn.transaction():
                    for item_id, batch_id, payload in batch:
                        conn.execute(
                            """
                            INSERT INTO batch_items (
                                item_id,
                                batch_id,
                                payload
                            )
                            VALUES (%s, %s, %s)
                            """,
                            (item_id, batch_id, payload),
                        )

                    if batch_number == 37:
                        raise ValueError(
                            "Simulated failure in batch 37"
                        )

            except ValueError as exc:
                conn.execute(
                    """
                    INSERT INTO rejected_batches (
                        batch_id,
                        reason
                    )
                    VALUES (%s, %s)
                    ON CONFLICT (batch_id)
                    DO UPDATE SET reason = EXCLUDED.reason
                    """,
                    (batch_number, str(exc)),
                )
```

## 12.3 What happens?

The outer block represents the larger transaction.

Each nested block acts as a smaller failure boundary.

At batch 37:

```text
inner work
    ↓
exception
    ↓
inner rollback
    ↓
batch 37 changes disappear
    ↓
rejected_batches records rejection
    ↓
outer transaction continues
```

## 12.4 Critical design question

Should every pipeline always do this?

No.

Savepoints have cost and complexity.

Consider:

- transaction duration;
- number of batches;
- savepoint frequency;
- rejected data volume;
- lock duration;
- recovery strategy.

A savepoint is appropriate when you intentionally want **partial recovery inside a larger atomic unit**.

---

# 13. Failed-Transaction State

This is one of the most important PostgreSQL behaviors to understand.

Suppose:

```python
conn.execute("some statement that fails")
```

inside a transaction.

After a PostgreSQL statement error, the transaction can be left in an **aborted/failed state**.

Conceptually:

```text
ACTIVE TRANSACTION
        ↓
SQL ERROR
        ↓
FAILED / ABORTED TRANSACTION
        ↓
ROLLBACK
        ↓
CLEAN STATE
```

## 13.1 The common surprise

A beginner might write:

```python
try:
    conn.execute("bad SQL")
except Exception:
    print("Something failed")

conn.execute("SELECT 1")
```

The second statement may fail because the connection's transaction is still in the failed state.

## 13.2 Recovery

```python
try:
    conn.execute("bad SQL")
except Exception:
    conn.rollback()

row = conn.execute("SELECT 1").fetchone()
print(row)
```

Rollback returns the transaction to a clean state where new work can begin.

## 13.3 Why this matters in production

If a worker catches an error but forgets to roll back, it may keep using a connection that cannot successfully execute subsequent statements.

The resulting symptoms can look confusing:

```text
the SQL itself looks valid
but every statement keeps failing
```

The root cause is transaction state.

---

# 14. Failed State vs Savepoint Recovery

These are different boundaries.

## Without savepoint

```text
transaction
   ↓
error
   ↓
whole transaction must be rolled back
```

## With savepoint

```text
outer transaction
   ↓
savepoint
   ↓
error
   ↓
rollback to savepoint
   ↓
outer transaction continues
```

The design question is:

> Which unit should fail together?

That is transaction engineering.

---

# 15. Isolation Levels from Python

The earlier SQL curriculum covered transaction-isolation theory.

Here, focus on how Python/psycopg controls it.

Common PostgreSQL isolation levels include:

```text
READ COMMITTED
REPEATABLE READ
SERIALIZABLE
```

The stronger the consistency requirements, the more concurrency behavior can change.

## 15.1 Why configure isolation from Python?

Because the application may need to express:

```text
this transaction requires this consistency level
```

rather than relying blindly on a default.

## 15.2 Practical principle

Isolation is an application decision.

It affects:

- visibility;
- concurrency;
- serialization conflicts;
- retry requirements.

In particular:

```text
SERIALIZABLE
    ↓
stronger consistency guarantees
    ↓
possible serialization failures
    ↓
application may need retries
```

That is why transaction isolation and retry logic cannot be designed independently.

## 15.3 Configuring a transaction

psycopg provides transaction-control APIs through connection and transaction settings.

An example using a transaction-level isolation setting:

```python
from psycopg import IsolationLevel

with conn.transaction(
    isolation_level=IsolationLevel.SERIALIZABLE,
):
    conn.execute(...)
```

The exact API should follow the psycopg 3 version in use.

The important mental model is:

> Python expresses the transaction requirement; PostgreSQL enforces the isolation semantics.

---

# 16. Read-Only Transactions

A read-only transaction tells PostgreSQL that the transaction is not intended to perform writes.

The concept is:

```text
read work
    ↓
READ ONLY
```

This can be a valuable guardrail for extraction jobs.

## 16.1 Why use it?

A read-only mode can help catch accidental writes.

For example, an extraction process might be intended to:

```text
SELECT only
```

and should not accidentally run:

```text
UPDATE
DELETE
```

## 16.2 Conceptual example

```python
from psycopg import transaction

with conn.transaction(
    isolation_level=transaction.IsolationLevel.READ_COMMITTED,
    read_only=True,
):
    rows = conn.execute(
        "SELECT id, name FROM customers"
    ).fetchmany(100)
```

The exact API shape can vary by psycopg version; consult the installed psycopg 3 documentation when implementing this in the lab.

The key principle is:

> **Read-only is a guardrail, not merely a performance feature.**

---

# 17. `idle in transaction`

This is one of the most important production concepts in the module.

Consider:

```python
with psycopg.connect(...) as conn:
    conn.execute("SELECT count(*) FROM orders")
    time.sleep(60)
```

A transaction may have started when the statement executed.

Then Python stops sending SQL.

PostgreSQL can report:

```text
idle in transaction
```

## 17.1 What does that mean?

It means:

```text
transaction started
      ↓
no SQL currently executing
      ↓
transaction is still open
```

The session is idle.

The transaction is not.

## 17.2 Why is this dangerous?

An open transaction may keep:

- a transaction snapshot;
- resources associated with the transaction;
- locks where applicable.

Long-running transactions can also interfere with cleanup and DDL behavior.

The exact consequences depend on the workload and isolation semantics.

## 17.3 Observe it

From another session:

```sql
SELECT
    pid,
    application_name,
    state,
    xact_start,
    query
FROM pg_stat_activity
WHERE application_name = 'topic-04-idle-demo';
```

You may see:

```text
state = idle in transaction
```

That is a concrete database-side signal that your Python code has left a transaction open.

---

# 18. Why `idle in transaction` Can Hurt the Database

Imagine:

```text
Transaction A
  ↓
starts
  ↓
Python waits 10 minutes
  ↓
transaction still open
```

Meanwhile other database activity continues.

Potential consequences include:

- old snapshots remaining relevant;
- cleanup being delayed;
- blocking interactions with DDL or locks;
- greater resource retention;
- difficult operational diagnosis.

The exact behavior depends on PostgreSQL version, query pattern, isolation level, and concurrent activity.

The production lesson is simple:

> **Do not keep transactions open while waiting on unrelated work.**

---

# 19. `idle_in_transaction_session_timeout`

PostgreSQL provides:

```text
idle_in_transaction_session_timeout
```

This setting protects the server against sessions that remain idle inside transactions for too long.

Conceptually:

```text
transaction open
      ↓
Python goes idle
      ↓
timeout threshold reached
      ↓
PostgreSQL terminates the session
```

## 19.1 Why use it?

It is a safety net.

For a pipeline role, a bounded value can prevent accidental transaction leaks from lasting indefinitely.

## 19.2 Example

A session can set:

```sql
SET idle_in_transaction_session_timeout = '30s';
```

From psycopg:

```python
with psycopg.connect(
    ...,
    options="-c idle_in_transaction_session_timeout=30000",
) as conn:
    ...
```

A server-side role configuration can also establish policy.

## 19.3 Safety net, not design

Do not think:

> "We have a timeout, so long transactions are fine."

A timeout only limits the worst case.

The better architecture is:

```text
short transaction
+
explicit boundary
+
timeout safety net
```

---

# 20. Keep Transactions Short

The production rule is:

> **Short and deliberate transactions are easier to reason about, recover, and operate.**

Why?

```text
Shorter transaction
      ↓
smaller failure domain
      ↓
shorter lock duration
      ↓
less contention
      ↓
less operational risk
```

## 20.1 Anti-pattern

```python
with conn.transaction():
    read_file()
    call_api()
    time.sleep(30)
    transform_data()
    write_database()
```

This is usually the wrong boundary.

## 20.2 Better shape

```text
read / fetch external data
        ↓
validate / transform
        ↓
prepare database work
        ↓
open transaction
        ↓
small set of database operations
        ↓
COMMIT
```

The transaction contains the database consistency boundary, not every step of the workflow.

---

# 21. Retryable vs Non-Retryable Errors

Not every database failure deserves a retry.

This is an essential production distinction.

## 21.1 Typical retry candidates

The roadmap calls out:

- serialization failures;
- deadlocks;
- some transient connection failures.

These are often **transient**.

A later attempt may succeed even when the application code is unchanged.

## 21.2 Typical non-retryable failures

Examples:

- integrity/constraint violations;
- syntax errors;
- programming errors.

A retry usually repeats the same invalid operation.

## 21.3 Classification table

| Failure | Typical cause | Retry? | Reason |
|---|---|---|---|
| Serialization failure | concurrency conflict | Often yes | A fresh transaction can succeed |
| Deadlock | conflicting concurrent locks | Often yes | A new attempt may avoid the cycle |
| Unique violation | duplicate/invalid data | Usually no | Same input normally fails again |
| Syntax error | invalid SQL | No | Retrying does not fix code |
| Programming error | application bug | No | Code must change |
| Some connection failures | transient connectivity issue | Sometimes | Depends on operation semantics |

The exact retry decision always depends on application semantics.

---

# 22. Why Retry the Whole Transaction?

Suppose the transaction is:

```text
A
B
C
```

and C fails because of serialization conflict.

A tempting but incorrect model is:

```text
A
B
C fails
 ↓
retry C only
```

Why can this be wrong?

Because A and B were observed/executed under the transaction's original snapshot and concurrency conditions.

A fresh transaction is a new consistency context.

The correct model is:

```text
BEGIN
  ↓
A
  ↓
B
  ↓
C
  ↓
serialization failure
  ↓
ROLLBACK
  ↓
BEGIN new transaction
  ↓
A
  ↓
B
  ↓
C
  ↓
COMMIT
```

The entire logical transaction must be re-evaluated.

That is the production rule:

> **Retry the transaction, not merely the failed statement.**

---

# 23. Retry With Backoff

Immediate retries can create a retry storm.

For example:

```text
worker A fails
worker B fails
worker C fails
all retry immediately
↓
same contention repeats
```

Backoff spaces out attempts.

A simple exponential schedule might be:

```text
attempt 1 → 100 ms
attempt 2 → 200 ms
attempt 3 → 400 ms
attempt 4 → 800 ms
```

Real systems often add jitter so many workers do not retry at exactly the same time.

## 23.1 Self-contained retry helper

This is intentionally small so the transaction boundary stays visible.

```python
import random
import time
from collections.abc import Callable
from typing import TypeVar

import psycopg


T = TypeVar("T")


RETRYABLE_ERRORS = (
    psycopg.errors.SerializationFailure,
    psycopg.errors.DeadlockDetected,
)


def run_transaction_with_retry(
    conn: psycopg.Connection,
    operation: Callable[[], T],
    *,
    max_attempts: int = 5,
    base_delay_seconds: float = 0.1,
) -> T:
    last_error: Exception | None = None

    for attempt in range(max_attempts):
        try:
            with conn.transaction():
                return operation()

        except RETRYABLE_ERRORS as exc:
            last_error = exc

            if attempt == max_attempts - 1:
                raise

            delay = base_delay_seconds * (2**attempt)
            delay *= random.uniform(0.5, 1.5)

            time.sleep(delay)

    assert last_error is not None
    raise last_error
```

The most important part is not the backoff formula.

It is this:

```python
with conn.transaction():
    return operation()
```

Each attempt creates a fresh transaction boundary.

## 23.2 What should not be retried?

Do not turn this into:

```python
except Exception:
    retry()
```

That would retry:

- syntax mistakes;
- bad data;
- programming bugs;
- many permanent failures.

Retryability is a classification decision.

---

# 24. Serialization Failure Lab

The roadmap requires reproducing a serialization failure with two concurrent Python processes using `SERIALIZABLE`.

> ⚠️ **LOCAL TRAINING LAB**
>
> Run this only against the module's own Docker PostgreSQL environment.

## 24.1 The idea

Two transactions read related data and then attempt conflicting updates.

Conceptually:

```text
Process A                     Process B

BEGIN SERIALIZABLE            BEGIN SERIALIZABLE
       ↓                             ↓
     READ                          READ
       ↓                             ↓
    UPDATE                        UPDATE
       ↓                             ↓
   COMMIT ✅                   COMMIT → conflict
```

PostgreSQL may abort one transaction with a serialization failure.

## 24.2 Why?

`SERIALIZABLE` aims to provide behavior equivalent to a serial execution ordering.

If concurrent work cannot be safely serialized, PostgreSQL can choose to abort a transaction rather than return an invalid result.

## 24.3 What the Python layer sees

psycopg can raise:

```python
psycopg.errors.SerializationFailure
```

The recovery is:

```text
rollback
↓
backoff
↓
new transaction
↓
re-run all transaction operations
```

## 24.4 Lab design

Create a simple table:

```sql
CREATE TABLE IF NOT EXISTS inventory (
    id integer PRIMARY KEY,
    quantity integer NOT NULL
);

INSERT INTO inventory (id, quantity)
VALUES (1, 100)
ON CONFLICT (id) DO NOTHING;
```

Then have two local Python processes use `SERIALIZABLE` transactions and intentionally coordinate their reads/updates to create a conflict.

The goal is to observe:

```text
PostgreSQL concurrency conflict
        ↓
SerializationFailure
        ↓
Python catches it
        ↓
transaction is rolled back
        ↓
fresh transaction retries
```

Do not treat the exact timing of the lab as guaranteed on every run. Concurrency is timing-sensitive.

---

# 25. Deadlocks

A deadlock occurs when transactions wait for each other in a cycle.

Example:

```text
Transaction A holds lock X
Transaction B holds lock Y

A waits for Y
B waits for X

      ↓
cycle
```

PostgreSQL detects the deadlock and aborts one transaction.

psycopg can surface:

```python
psycopg.errors.DeadlockDetected
```

## 25.1 Why can it be retryable?

The deadlock itself is a transient concurrency condition.

A new transaction can sometimes succeed because the conflicting lock order no longer occurs.

## 25.2 Why retry the whole transaction?

Because the aborted transaction's state is no longer valid.

The safe pattern is:

```text
transaction
  ↓
deadlock
  ↓
rollback
  ↓
new transaction
  ↓
re-run complete logical work
```

## 25.3 Small controlled example

> ⚠️ **INTENTIONALLY FAILING CONCURRENCY EXAMPLE**
>
> Use only the local training database.

Two sessions can deliberately acquire resources in opposite order:

```text
Session A:
lock row 1
then request row 2

Session B:
lock row 2
then request row 1
```

PostgreSQL detects the cycle.

The educational goal is to understand:

```text
deadlock → database aborts one transaction → Python must handle the transaction failure
```

Module 2.6 contains deeper locking theory.

---

# 26. Unknown Commit Outcome

This is an advanced concept that every production data engineer should understand.

Imagine:

```text
Python transaction
      ↓
COMMIT request
      ↓
PostgreSQL may commit
      ↓
network failure
      ↓
Python loses connection
```

Now ask:

> Did PostgreSQL commit?

The client may not know.

The state is:

```text
COMMIT outcome
    ↓
UNKNOWN
```

## 26.1 Why is this difficult?

The problem is not simply:

```text
commit succeeded
```

or:

```text
commit failed
```

The client has lost the communication needed to determine the result.

PostgreSQL may have committed before the network failure became visible to Python.

## 26.2 Never assume

Do not write recovery code like:

```python
except ConnectionError:
    # Assume commit did not happen.
    retry()
```

That assumption can create duplicate side effects.

The right question is:

> **If I re-execute this operation, is it safe?**

That leads directly to idempotency.

---

# 27. Idempotent Loads

An operation is idempotent when repeating the same logical operation produces the same intended final state.

This is especially valuable when commit outcome is uncertain.

## 27.1 Non-idempotent design

Suppose:

```text
INSERT new event
```

is blindly repeated.

Possible result:

```text
run 1 → row inserted
run 2 → duplicate row
```

## 27.2 Idempotent design

A pipeline can instead use a stable logical key and a deterministic final state.

Conceptually:

```text
logical record key
      ↓
same input reprocessed
      ↓
same intended target state
```

The exact SQL pattern depends on the workload.

The important idea is:

> **Make retries safe at the level of the business operation, not just the network call.**

---

# 28. Unknown Commit + Idempotency

The relationship is:

```text
unknown commit outcome
        +
safe re-execution
        ↓
recoverable workflow
```

Suppose a load logically means:

```text
customer_id = 123
status = "processed"
```

If a retry simply creates another independent side effect, recovery is dangerous.

If the operation is designed around a stable identity and deterministic state, retrying can converge on the same result.

This is one reason idempotency is central to pipeline reliability.

---

# 29. Pipeline Runs and Audit Transactions

The roadmap requires a `pipeline_runs` table whose status updates occur in short, separate transactions.

A conceptual schema:

```sql
CREATE TABLE pipeline_runs (
    run_id UUID PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    finished_at TIMESTAMPTZ,
    rows_in BIGINT,
    rows_out BIGINT,
    error_message TEXT
);
```

## 29.1 Why not put the audit row in the main transaction?

Suppose:

```text
main transaction
    ↓
load data
    ↓
FAIL
    ↓
ROLLBACK
```

If the pipeline status was written inside that same transaction, the status update may also roll back.

The system could then lose evidence that the run failed.

Instead:

```text
Transaction 1
    insert status=running
    COMMIT

Main work
    ↓
success/failure

Transaction 2
    update status
    COMMIT
```

This is a valuable control-plane pattern.

---

# 30. Pipeline Run Context Manager

A small Python abstraction can make the lifecycle explicit.

```python
from contextlib import contextmanager
from datetime import datetime, timezone
from uuid import UUID


@contextmanager
def pipeline_run(
    conn,
    *,
    run_id: UUID,
    pipeline_name: str,
):
    started_at = datetime.now(timezone.utc)

    # Short independent transaction for audit start.
    with conn.transaction():
        conn.execute(
            """
            INSERT INTO pipeline_runs (
                run_id,
                pipeline_name,
                status,
                started_at
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                run_id,
                pipeline_name,
                "running",
                started_at,
            ),
        )

    try:
        yield

    except Exception as exc:
        finished_at = datetime.now(timezone.utc)

        # Separate transaction so failure status can survive
        # rollback of the main unit of work.
        with conn.transaction():
            conn.execute(
                """
                UPDATE pipeline_runs
                SET status = %s,
                    finished_at = %s,
                    error_message = %s
                WHERE run_id = %s
                """,
                (
                    "failed",
                    finished_at,
                    str(exc),
                    run_id,
                ),
            )

        raise

    else:
        finished_at = datetime.now(timezone.utc)

        with conn.transaction():
            conn.execute(
                """
                UPDATE pipeline_runs
                SET status = %s,
                    finished_at = %s
                WHERE run_id = %s
                """,
                (
                    "succeeded",
                    finished_at,
                    run_id,
                ),
            )
```

## 30.1 Important limitation

This does not create perfect distributed transaction guarantees.

For example, Python itself could crash between:

```text
main work completes
```

and:

```text
audit status updated
```

Production systems therefore often add stronger operational controls such as reconciliation and recovery logic.

The pattern is still valuable because it prevents the main transaction rollback from automatically erasing the run history.

---

# 31. Transactions Across Two Databases

This is another important boundary.

Imagine:

```text
Source PostgreSQL
      ↓
Python
      ↓
Warehouse PostgreSQL
```

You might think:

```python
source.commit()
warehouse.commit()
```

is one logical transaction.

It is not.

## 31.1 Failure timeline

```text
Source transaction
    ↓
COMMIT ✅

Warehouse transaction
    ↓
COMMIT ❌
```

Now the two systems disagree.

Or:

```text
Source COMMIT fails
Warehouse COMMIT succeeds
```

The same problem exists in the opposite direction.

Two ordinary database connections do not automatically provide one atomic transaction across both systems.

---

# 32. Two-Phase Commit — Awareness

A distributed transaction protocol can coordinate participants through a prepare phase and commit phase.

Conceptually:

```text
BEGIN
  ↓
prepare
  ↓
all participants ready?
  ↓
commit
```

This is often called **two-phase commit (2PC)**.

For this module, awareness is enough.

The important point is:

> Cross-database atomicity is a distributed systems problem, not something solved by simply calling `commit()` twice.

---

# 33. Why Data Pipelines Often Prefer Idempotency and Checkpoints

In many data systems, a more practical design is:

```text
small checkpointed steps
+
idempotent re-execution
+
watermarks
+
reconciliation
+
recovery logic
```

rather than:

```text
one gigantic distributed transaction
```

Why?

Because pipelines commonly involve:

- multiple databases;
- object storage;
- files;
- APIs;
- message systems;
- external services.

Trying to force every component into one atomic transaction can be complex or impossible.

A checkpointed pipeline instead says:

```text
step 1 complete
   ↓
checkpoint
   ↓
step 2 complete
   ↓
checkpoint
   ↓
recover from last known safe point
```

The full patterns belong to later pipeline-design modules.

Here, the key lesson is the transaction boundary.

---

# 34. Transaction State Machine

A useful advanced mental model is:

```text
CONNECTED
    ↓
NO ACTIVE TRANSACTION
    ↓
FIRST STATEMENT
    ↓
ACTIVE TRANSACTION
    ├────────────────────┐
    ↓                    ↓
 COMMIT                ERROR
    ↓                    ↓
 CLEAN              FAILED TRANSACTION
                         ↓
                      ROLLBACK
                         ↓
                       CLEAN
```

With a savepoint:

```text
ACTIVE TRANSACTION
       ↓
    SAVEPOINT
       ↓
      WORK
       ↓
     ERROR
       ↓
ROLLBACK TO SAVEPOINT
       ↓
OUTER TRANSACTION CONTINUES
```

With a retry:

```text
BEGIN
  ↓
WORK
  ↓
SERIALIZATION FAILURE
  ↓
ROLLBACK
  ↓
BACKOFF
  ↓
BEGIN AGAIN
  ↓
WORK AGAIN
  ↓
COMMIT
```

With an uncertain commit:

```text
WORK
  ↓
COMMIT SENT
  ↓
NETWORK FAILURE
  ↓
CLIENT CANNOT DETERMINE OUTCOME
  ↓
RECOVERY MUST ACCOUNT FOR POSSIBLE SUCCESS
```

These diagrams are more important than memorizing isolated API calls.

---

# 35. Python Side vs PostgreSQL Side

For:

```python
with conn.transaction():
    conn.execute(...)
    conn.execute(...)
```

use this mental table:

| Python side | PostgreSQL-side interpretation |
|---|---|
| `conn.transaction()` | Deliberate transaction boundary |
| `execute()` | SQL statement is executed |
| Python exception | Application failure may cause rollback |
| successful block exit | Transaction is committed |
| exception block exit | Transaction is rolled back |
| `rollback()` | Current transaction is aborted |
| `commit()` | Current transaction is completed |
| nested transaction context | Savepoint-style recovery boundary |

This is a conceptual mapping.

Do not assume every internal PostgreSQL protocol message is one-to-one with a Python method call.

---

# 36. Complete Transaction Lab Progression

Work through these labs in order.

## Lab 1 — Explicit commit

### Objective

Understand visibility and commit.

### Task

Insert a row from connection A.

Do not commit.

Use connection B to check whether the expected committed state is visible.

Then commit and check again.

### Predict

Before running:

```text
What does connection B see?
```

### Production lesson

Transaction completion affects visibility.

---

## Lab 2 — Rollback

### Objective

Understand transaction cancellation.

### Task

Perform a write, then deliberately raise an exception and roll back.

### Predict

Should the database retain the write?

### Production lesson

Rollback aborts current uncommitted work.

---

## Lab 3 — Transaction context

### Objective

Make the boundary explicit.

Use:

```python
with conn.transaction():
    ...
```

### Production lesson

Scope is visible in the code.

---

## Lab 4 — Autocommit

### Objective

Understand statement-by-statement completion.

Run a command that is appropriate/required in autocommit mode in the local PostgreSQL environment.

### Production lesson

Autocommit is a deliberate mode, not a universal default.

---

## Lab 5 — Failed transaction state

### Objective

See the aborted state.

### Task

1. Start a transaction.
2. Trigger a statement error.
3. Attempt another statement without rollback.
4. Observe the resulting failure.
5. Call `rollback()`.
6. Repeat the statement.

### Production lesson

After transaction failure, recovery requires transaction-state awareness.

---

## Lab 6 — Savepoint

### Objective

Recover from one bad unit without discarding the entire outer transaction.

### Task

Use nested transaction blocks around batches.

### Production lesson

A savepoint defines a smaller rollback boundary.

---

## Lab 7 — Idle transaction

### Objective

See transaction state in PostgreSQL.

### Task

Start transaction activity, then sleep.

From a second connection, query:

```sql
SELECT
    pid,
    application_name,
    state,
    xact_start
FROM pg_stat_activity
WHERE application_name = 'topic-04-idle-demo';
```

### Production lesson

A Python program can appear idle while its database transaction remains active.

---

## Lab 8 — Serializable retry

### Objective

Reproduce a serialization failure.

### Task

Use two local Python processes at `SERIALIZABLE`.

### Production lesson

A transient concurrency error can require a whole-transaction retry.

---

## Lab 9 — Deadlock retry

### Objective

Observe `DeadlockDetected`.

### Task

Coordinate two local sessions so they acquire locks in conflicting order.

### Production lesson

Retry the transaction after the database aborts it.

---

## Lab 10 — Unknown commit outcome

### Objective

Reason about an ambiguous commit.

### Task

Design a thought experiment:

```text
COMMIT sent
↓
network breaks
↓
client is disconnected
```

Ask:

> Can the client prove whether PostgreSQL committed?

Then design the recovery strategy around idempotency.

### Production lesson

Unknown outcomes require safe re-execution or verification.

---

# 37. Hands-On Exercise — `transactions.py`

The roadmap specifies a complete transaction exercise equivalent to `transactions.py`.

Because no additional files should be created by this document, use the existing lab project and implement the exercise there.

## Requirements

Your implementation must demonstrate:

1. 100 logical batches.
2. Batch 37 intentionally fails.
3. Each batch has a savepoint.
4. Only batch 37 is rolled back.
5. The rejected batch is recorded.
6. Successful batches remain committed.
7. Failed-transaction state is reproduced.
8. A serialization failure is reproduced using concurrent local processes.
9. The whole transaction is retried.
10. Non-retryable errors are not retried.
11. A `pipeline_run` context manager is implemented.
12. `idle_in_transaction_session_timeout` is configured.
13. A stuck transaction can be demonstrated and terminated safely.

## Learner workflow

Before running each section:

```text
PREDICT
    ↓
RUN
    ↓
OBSERVE
    ↓
EXPLAIN
```

Write down:

- transaction state;
- expected SQL;
- expected exception;
- expected commit/rollback result;
- PostgreSQL session state.

---

# 38. Debugging Section

## Problem 1 — Forgot to commit

### Symptoms

Another connection does not see the expected committed change.

### Root cause

The transaction was never completed.

### Database state

```text
ACTIVE TRANSACTION
```

### Fix

Use:

```python
conn.commit()
```

or a transaction context manager.

### Production lesson

Always know the commit boundary.

---

## Problem 2 — Connection is stuck in failed transaction state

### Symptoms

Every subsequent SQL statement fails even though the SQL itself is valid.

### Root cause

A previous statement error left the transaction aborted.

### Fix

```python
conn.rollback()
```

### Production lesson

Exception handling must include transaction-state recovery.

---

## Problem 3 — Transaction stays open while Python sleeps

### Symptoms

```text
idle in transaction
```

appears in `pg_stat_activity`.

### Root cause

The application began transaction activity and then performed slow work without completing the transaction.

### Fix

Move slow Python/external work outside the database transaction.

### Production lesson

Transaction scope should match database consistency scope.

---

## Problem 4 — Retry only failed statement

### Symptoms

Serialization failures produce inconsistent or logically incorrect retries.

### Root cause

The failed statement was retried in the wrong transaction context.

### Fix

Rollback and rerun the complete logical transaction.

### Production lesson

Retry boundaries must align with transaction boundaries.

---

## Problem 5 — Infinite retry of a unique violation

### Symptoms

The worker repeatedly fails with the same duplicate-key error.

### Root cause

A permanent data/logic error is being treated as transient.

### Fix

Classify the exception.

### Production lesson

Retry policy must be selective.

---

## Problem 6 — Commit lost connection

### Symptoms

Python receives a connectivity error around commit.

### Root cause

The client cannot determine exactly when the network failed relative to server-side commit processing.

### Fix

Design operation recovery around safe re-execution or verification.

### Production lesson

Commit uncertainty is a real failure mode.

---

## Problem 7 — Pipeline status disappears on rollback

### Symptoms

The pipeline failed, but there is no durable `failed` run record.

### Root cause

The run-status update was inside the transaction that rolled back.

### Fix

Use separate short audit transactions.

### Production lesson

Observability state can require its own transaction boundary.

---

## Problem 8 — Two database commits diverge

### Symptoms

Source and warehouse show different states.

### Root cause

Two independent transactions were committed separately.

### Fix

Use checkpointed/idempotent workflow design or a deliberate distributed transaction protocol where justified.

### Production lesson

Two `commit()` calls are not one atomic commit.

---

# 39. Transaction Anti-Patterns

## Anti-pattern 1 — One transaction around an entire pipeline

### Why beginners do it

"Then everything succeeds or fails together."

### What actually happens

The transaction can stay open through:

- extraction;
- transformation;
- network calls;
- waits;
- large Python operations.

### Production impact

Long snapshots, locks, contention, and difficult recovery.

### Correct mental model

Use smaller transaction boundaries around actual database consistency requirements.

---

## Anti-pattern 2 — HTTP requests inside database transactions

### Why beginners do it

"The API call is part of the business operation."

### What actually happens

The database transaction waits for an external system whose latency and reliability are not controlled by PostgreSQL.

### Production impact

Long-running transactions.

### Correct mental model

Separate external I/O from database transaction scope unless a carefully designed coordination protocol is required.

---

## Anti-pattern 3 — Sleeping inside transactions

### Beginner behavior

```python
with conn.transaction():
    conn.execute(...)
    time.sleep(30)
```

### Production impact

The session may become:

```text
idle in transaction
```

### Correct mental model

Sleep outside the transaction whenever possible.

---

## Anti-pattern 4 — Retrying every exception

### Why beginners do it

"It makes the pipeline resilient."

### What actually happens

Permanent bugs repeat.

### Production impact

Retry storms and wasted resources.

### Correct mental model

Retry only errors that are plausibly transient and whose operation semantics allow safe retry.

---

## Anti-pattern 5 — Retrying only the failed statement

### What actually happens

The transaction's previous reads and writes belong to the old transaction context.

### Correct mental model

Retry the whole transaction.

---

## Anti-pattern 6 — Never rolling back after a failure

### What actually happens

The connection can remain in an aborted transaction state.

### Production impact

Subsequent operations fail.

### Correct mental model

Recover transaction state before continuing.

---

## Anti-pattern 7 — Using autocommit for multi-step atomic work

### What actually happens

Each statement is completed independently.

### Production impact

Partial success.

### Correct mental model

Use an explicit transaction when multiple operations must succeed/fail together.

---

## Anti-pattern 8 — Assuming commit failure means "nothing happened"

### What actually happens

The outcome can be unknown.

### Production impact

Blind retries can duplicate effects.

### Correct mental model

Design for ambiguous outcomes.

---

## Anti-pattern 9 — Main and audit state in one transaction

### What actually happens

A rollback can erase the evidence of the failure.

### Correct mental model

Use independent short transactions for operational audit state.

---

## Anti-pattern 10 — Two-database consistency via two ordinary commits

### What actually happens

The first can commit while the second fails.

### Production impact

Cross-system inconsistency.

### Correct mental model

Use idempotent/checkpointed workflows or an intentional distributed transaction mechanism.

---

# 40. Transaction Design Patterns

## Pattern A — Single atomic operation

```text
BEGIN
  ↓
operation
  ↓
COMMIT
```

Use when one logical operation must be atomic.

---

## Pattern B — Multiple operations must succeed together

```text
BEGIN
  ↓
A
  ↓
B
  ↓
C
  ↓
COMMIT
```

If C fails:

```text
ROLLBACK
```

---

## Pattern C — Partial failure with savepoints

```text
BEGIN
  ↓
batch A
  ↓
SAVEPOINT
  ↓
batch B
  ↓
failure
  ↓
ROLLBACK TO SAVEPOINT
  ↓
continue
  ↓
COMMIT
```

Use when only one sub-unit should fail.

---

## Pattern D — Retryable transaction

```text
BEGIN
  ↓
work
  ↓
COMMIT

if transient conflict:
  ↓
ROLLBACK
  ↓
BACKOFF
  ↓
BEGIN AGAIN
```

The complete work runs again.

---

## Pattern E — Audited pipeline run

```text
START RUN
   ↓
COMMIT

MAIN WORK
   ↓
SUCCESS / FAILURE
   ↓
UPDATE RUN STATUS
   ↓
COMMIT
```

The audit lifecycle is independent.

---

## Pattern F — Multi-database workflow

```text
step
  ↓
checkpoint
  ↓
next step
  ↓
checkpoint
  ↓
recovery
```

Prefer idempotent boundaries where practical.

---

# 41. Performance and Operability

Transaction engineering affects performance even when SQL itself is unchanged.

## 41.1 Transaction duration

Long transactions can increase resource retention and contention.

## 41.2 Lock duration

Locks acquired by work inside a transaction can remain relevant until the transaction completes, depending on the operation.

Shorter transactions often reduce contention.

## 41.3 Commit frequency

Too many commits increase transaction overhead.

Too few commits can create huge, long-lived transactions.

The right frequency is workload-dependent.

## 41.4 Savepoint overhead

Savepoints provide recovery granularity but add complexity and some database work.

Use them deliberately.

## 41.5 Retry amplification

Suppose 100 workers all collide and retry immediately.

You can turn:

```text
one concurrency problem
```

into:

```text
many repeated concurrency problems
```

Backoff and jitter help reduce synchronized retries.

## 41.6 Operational indicators

Useful transaction-health signals include:

- transaction duration;
- number of `idle in transaction` sessions;
- long-running transactions;
- serialization-failure counts;
- deadlock counts;
- rollback counts;
- retry counts;
- transaction age.

The exact monitoring stack comes later in the roadmap.

---

# 42. Production Data Engineering Scenarios

## Scenario 1 — Watermark update

Imagine a pipeline reads up to:

```text
updated_at = T
```

and then wants to advance the watermark.

A key question is:

> At what point is the watermark safe to commit?

If the watermark is committed before the associated data changes are durable, a failure can cause data to be skipped.

A safer design aligns:

```text
data state
+
checkpoint state
```

with an appropriate transaction boundary.

The detailed incremental-ingestion pattern belongs to Module 2.9.

The transaction lesson is:

> **Do not advance a checkpoint before the work it represents is safely completed.**

---

## Scenario 2 — Staging validation

A pipeline may conceptually perform:

```text
load staging
      ↓
validate
      ↓
apply final state
      ↓
commit
```

The exact implementation depends on the loading technique.

The transaction decision is:

> Which changes need atomic visibility?

Do not keep an entire extraction process inside the same transaction merely because the final database update is transactional.

---

## Scenario 3 — Pipeline metadata

A pipeline wants:

```text
running
↓
succeeded
```

or:

```text
running
↓
failed
```

The status should remain observable even when the main transaction fails.

That is why the metadata transaction can be separate.

---

## Scenario 4 — Concurrent workers

Multiple workers update related state.

Under strict isolation, one worker may receive:

```python
psycopg.errors.SerializationFailure
```

The correct response may be:

```text
rollback
↓
backoff
↓
whole-transaction retry
```

not:

```text
retry only the final statement
```

---

## Scenario 5 — Deadlock between loaders

Worker A and Worker B acquire locks in different orders.

PostgreSQL detects a deadlock.

One transaction gets:

```python
psycopg.errors.DeadlockDetected
```

The transaction should be restarted according to a bounded retry policy.

---

## Scenario 6 — Source + warehouse

A workflow writes:

```text
source database
+
warehouse database
```

Two independent commits cannot provide simple atomicity.

Use:

```text
idempotent steps
+
checkpoints
+
recovery
```

where appropriate.

---

# 43. Testing Strategy

Transaction correctness should be tested deliberately.

Tests should cover:

- successful commit;
- rollback on exception;
- failed-transaction state;
- savepoint recovery;
- autocommit behavior;
- read-only enforcement;
- serialization failure;
- deadlock retry;
- non-retryable error not being retried;
- whole-transaction retry;
- pipeline-run status persistence;
- connection loss around commit;
- no unexpected open transaction after completion.

No separate test file is required by this document; the examples below are inline exercises.

## 43.1 Commit test

```python
def test_transaction_commits(conn):
    with conn.transaction():
        conn.execute(
            "INSERT INTO demo_items (id, name) VALUES (%s, %s)",
            (101, "committed"),
        )

    row = conn.execute(
        "SELECT name FROM demo_items WHERE id = %s",
        (101,),
    ).fetchone()

    assert row[0] == "committed"
```

## 43.2 Rollback test

```python
import pytest


def test_exception_rolls_back(conn):
    with pytest.raises(RuntimeError):
        with conn.transaction():
            conn.execute(
                """
                INSERT INTO demo_items (id, name)
                VALUES (%s, %s)
                """,
                (102, "rolled-back"),
            )
            raise RuntimeError("stop")

    row = conn.execute(
        "SELECT name FROM demo_items WHERE id = %s",
        (102,),
    ).fetchone()

    assert row is None
```

## 43.3 Non-retryable error test

A retry helper should not catch all exceptions.

Test that a known permanent exception propagates without consuming retry attempts.

The exact implementation depends on the retry helper being tested.

## 43.4 Savepoint test

Create one valid batch and one invalid batch.

Verify:

```text
valid batch remains
invalid batch disappears
rejection record exists
outer transaction completes
```

## 43.5 `idle in transaction` test

The test must inspect `pg_stat_activity` and verify that a deliberately idle session transitions to the expected state.

The lab is inherently timing-sensitive.

---

# 44. Learning Checkpoint A — Basics

You should now be able to explain:

- transaction;
- commit;
- rollback;
- transaction boundary.

Without looking at the examples, explain:

```text
START
  ↓
work
  ↓
COMMIT

or

START
  ↓
work
  ↓
ERROR
  ↓
ROLLBACK
```

Then explain how Python expresses the same boundary.

---

# 45. Learning Checkpoint B — Failure

You should now be able to explain:

- failed transaction state;
- rollback;
- savepoint.

Given:

```python
conn.execute("bad operation")
conn.execute("SELECT 1")
```

you should immediately ask:

> Has the transaction been rolled back?

If not, explain why the second statement may fail.

Then compare with:

```python
with conn.transaction():
    ...
```

and nested savepoint behavior.

---

# 46. Learning Checkpoint C — Production

You should now be able to explain:

- `idle in transaction`;
- short transaction design;
- timeout protection;
- retry classification.

Given:

```text
worker
↓
begins transaction
↓
calls API
↓
waits 45 seconds
↓
returns to database
```

identify the transaction-design problem.

---

# 47. Learning Checkpoint D — Advanced

You should now be able to explain:

- unknown commit outcome;
- idempotency;
- separate audit transactions;
- two-database atomicity limitations.

The key chain is:

```text
commit uncertainty
    ↓
possible success
    ↓
safe retry required
    ↓
idempotent operation
```

---

# 48. Python Transaction Code Review Checklist

Before approving Python transaction code, ask:

- Where does the transaction begin?
- Where does it end?
- Is the boundary intentional?
- Which operations must succeed/fail together?
- Can slow Python work happen while the transaction is open?
- Can external APIs be called while the transaction is open?
- Can the code sleep while the transaction is open?
- Is commit explicit or context-managed?
- What happens on an exception?
- Is rollback guaranteed?
- Can the connection enter a failed transaction state?
- Are savepoints used where partial recovery is actually required?
- Which exceptions are retryable?
- Does retry restart the entire transaction?
- Is backoff used?
- Is the operation idempotent?
- What happens if commit outcome is unknown?
- Are audit records independently durable?
- Is autocommit being used deliberately?
- Could this code become `idle in transaction`?
- What happens under concurrent workers?
- What evidence would `pg_stat_activity` show?

---

# 49. From Working Transaction Code to Production Transaction Code

## Version 1 — Naive

```python
conn.execute(...)
conn.execute(...)
```

No explicit boundary is visible.

Questions remain:

```text
When does the transaction end?
What if the second operation fails?
```

## Version 2 — Explicit transaction

```python
with conn.transaction():
    conn.execute(...)
    conn.execute(...)
```

Now the atomic unit is visible.

## Version 3 — Bounded scope

Prepare data before opening the transaction:

```text
fetch / validate / transform
        ↓
open short transaction
        ↓
database changes
        ↓
commit
```

## Version 4 — Savepoints

Introduce smaller rollback boundaries only where required.

## Version 5 — Retryable transaction

```text
serialization failure
      ↓
rollback
      ↓
backoff
      ↓
whole-transaction retry
```

## Version 6 — Idempotent transaction

Make repeated logical execution safe.

## Version 7 — Audited execution

Separate:

```text
main transaction
```

from:

```text
pipeline run metadata transactions
```

This progression is a useful engineering maturity model.

---

# 50. Unknown Commit + Idempotency Example

Suppose a pipeline is processing:

```text
customer_id = 123
```

and intends to establish:

```text
processed = true
```

## 50.1 Non-idempotent design

```text
INSERT event
```

If the client loses the connection after COMMIT might have succeeded, retrying can produce:

```text
duplicate event
```

## 50.2 Idempotent design

Use a stable logical identity so reprocessing converges on the same intended state.

For example, the operation can be modeled around:

```text
customer_id = 123
logical event = "processed"
```

The exact SQL mechanism is workload-specific.

The essential property is:

```text
same logical input
+
repeat execution
=
same intended final state
```

That makes an unknown commit outcome manageable.

---

# 51. Transaction State Timeline Exercises

## Timeline A — Normal

```text
CONNECT
  ↓
FIRST SQL
  ↓
TRANSACTION ACTIVE
  ↓
MORE SQL
  ↓
COMMIT
  ↓
CLEAN
```

Question:

> Which Python call creates the application's explicit boundary?

Answer:

```python
with conn.transaction():
```

or an equivalent explicit commit/rollback design.

---

## Timeline B — Failure

```text
TRANSACTION ACTIVE
  ↓
SQL ERROR
  ↓
FAILED TRANSACTION
  ↓
ROLLBACK
  ↓
CLEAN
```

Question:

> What happens if rollback is forgotten?

The connection can remain unusable for subsequent transaction work.

---

## Timeline C — Savepoint

```text
OUTER TRANSACTION
      ↓
SAVEPOINT
      ↓
WORK
      ↓
ERROR
      ↓
ROLLBACK TO SAVEPOINT
      ↓
CONTINUE
      ↓
COMMIT
```

Question:

> What is smaller here: the transaction boundary or the recovery boundary?

The savepoint creates a smaller recovery boundary inside the outer transaction.

---

## Timeline D — Retry

```text
BEGIN
  ↓
WORK
  ↓
SERIALIZATION FAILURE
  ↓
ROLLBACK
  ↓
BACKOFF
  ↓
BEGIN AGAIN
  ↓
WORK AGAIN
  ↓
COMMIT
```

Question:

> Why is A run again?

Because the new transaction has a new concurrency/visibility context.

---

## Timeline E — Unknown commit

```text
WORK
  ↓
COMMIT SENT
  ↓
NETWORK FAILURE
  ↓
CLIENT DOES NOT KNOW OUTCOME
  ↓
SAFE RE-EXECUTION / VERIFICATION
```

Question:

> Why is idempotency valuable?

Because retrying is no longer inherently dangerous.

---

# 52. Production Rules to Remember

## Rules I should remember

1. **Know exactly where every transaction begins and ends.**
2. **Keep transactions short.**
3. **Do not perform slow Python work inside an open transaction unless deliberately required.**
4. **Avoid external API calls inside database transactions.**
5. **Roll back after transaction failures.**
6. **Use savepoints when only part of a unit should fail.**
7. **Use autocommit deliberately, not automatically.**
8. **Retry serialization failures and deadlocks deliberately.**
9. **Retry the whole transaction, not only the failed statement.**
10. **Do not blindly retry permanent errors.**
11. **Treat commit uncertainty as a real failure mode.**
12. **Design idempotent operations.**
13. **Keep pipeline audit records independent from main work where failure visibility matters.**
14. **Do not assume two databases can be updated atomically with two ordinary commits.**
15. **Observe transaction state through PostgreSQL, not only Python logs.**
16. **Use timeouts as safety nets, not as substitutes for correct transaction design.**

---

# 53. Final Mental Model

## The Transaction Mental Model

```text
A transaction is a deliberate boundary around database work.

Inside the boundary:
    operations that must succeed/fail together

At the boundary:
    COMMIT or ROLLBACK

On transient concurrency failure:
    ROLLBACK
    RETRY THE WHOLE TRANSACTION

On uncertain commit outcome:
    outcome may be unknown
    design for safe re-execution or verification

For pipeline observability:
    record run state in separate short transactions
```

The compact production model is:

```text
Short transactions.
Clear boundaries.
Rollback on failure.
Retry only what is safely retryable.
Retry the whole transaction.
Design for unknown commit outcomes.
Make operations idempotent.
```

---

# 54. Final Review

## What You Now Understand

You should now understand:

- transaction lifecycle;
- psycopg default transaction behavior;
- `commit()`;
- `rollback()`;
- `conn.transaction()`;
- transaction boundaries;
- autocommit;
- savepoints;
- nested transaction contexts;
- failed transaction state;
- isolation-level configuration;
- read-only mode;
- `idle in transaction`;
- `idle_in_transaction_session_timeout`;
- short transaction design;
- retry classification;
- whole-transaction retry;
- exponential backoff and jitter;
- serialization failures;
- deadlocks;
- unknown commit outcomes;
- idempotency;
- pipeline-run audit transactions;
- cross-database transaction limitations;
- two-phase commit awareness.

## What You Can Implement

You should now be able to:

- build deliberate transaction boundaries;
- use psycopg transaction contexts;
- use savepoints;
- recover from failed transaction state;
- configure isolation and read-only behavior;
- implement bounded retries;
- retry an entire transaction;
- detect idle transactions;
- design idempotent operations;
- record pipeline run status;
- reason about two-database workflows.

## What You Can Debug

You should be able to diagnose:

```text
forgotten commit
failed transaction state
idle in transaction
overly long transaction scope
incorrect retry behavior
serialization failures
deadlocks
unknown commit outcomes
missing audit status
cross-database divergence
```

The debugging method is:

```text
Observed behavior
      ↓
Root cause
      ↓
Database state
      ↓
Transaction boundary
      ↓
Recovery strategy
      ↓
Production lesson
```

## What Comes Next

Next:

`05-connection-pooling.md`

That topic introduces shared/reused connections and connection pools under concurrent workloads.

Do not prematurely apply pooling concepts to solve transaction-boundary problems.

A pool manages **connection reuse**.

A transaction manages **database work boundaries**.

They are related, but they are not the same abstraction.

---

# 55. Final Roadmap Checkpoint

Do not move to Topic 05 until you can complete every roadmap requirement:

- [ ] Use `conn.transaction()` correctly.
- [ ] Use savepoints from Python.
- [ ] Explain and detect `idle in transaction`.
- [ ] Use `pg_stat_activity` to inspect transaction state.
- [ ] Configure `idle_in_transaction_session_timeout`.
- [ ] Keep transactions short.
- [ ] Explain why external I/O should normally be outside open transactions.
- [ ] Decide which database errors are retryable.
- [ ] Distinguish serialization failures and deadlocks from permanent errors.
- [ ] Retry the whole transaction rather than only the failed statement.
- [ ] Implement bounded backoff.
- [ ] Reproduce a serialization failure in local PostgreSQL.
- [ ] Reproduce a deadlock in local PostgreSQL.
- [ ] Explain the unknown commit outcome problem.
- [ ] Explain why idempotent loads matter.
- [ ] Implement the pipeline-run audit pattern.
- [ ] Explain why audit status may need separate transactions.
- [ ] Explain why two ordinary database commits do not provide simple cross-database atomicity.
- [ ] Explain two-phase commit at awareness level.
- [ ] Explain explicit commit/rollback behavior.
- [ ] Explain autocommit and when it is appropriate.
- [ ] Explain isolation and read-only configuration.
- [ ] Explain the transaction state machine.
- [ ] Complete the `transactions.py` exercise requirements.
- [ ] Complete the debugging exercises.
- [ ] Complete the code-review checklist exercise.
- [ ] Defend transaction-boundary decisions in engineering terms.

The checkpoint is behavioral.

You should be able to **design, run, observe, debug, and explain** transaction behavior rather than simply recite API names.

---

# 56. Final One-Page Cheat Sheet

```text
TRANSACTION
    = deliberate boundary around database work

COMMIT
    = complete current transaction

ROLLBACK
    = abort current transaction

conn.transaction()
    = explicit transaction scope

AUTOCOMMIT
    = statements complete independently in normal usage

SAVEPOINT
    = smaller rollback boundary inside an outer transaction

FAILED TRANSACTION
    = statement error can leave transaction aborted
      → rollback before continuing

ISOLATION
    = controls transaction concurrency/visibility semantics

READ ONLY
    = guardrail against writes

idle in transaction
    = transaction open while session is not executing SQL

idle_in_transaction_session_timeout
    = server-side safety net

RETRYABLE
    = often transient concurrency failures

NON-RETRYABLE
    = usually permanent data/code problems

WHOLE-TRANSACTION RETRY
    = rollback + backoff + rerun all logical steps

UNKNOWN COMMIT OUTCOME
    = client cannot always know whether server committed

IDEMPOTENCY
    = repeated logical execution reaches the same intended final state

PIPELINE AUDIT
    = status writes can use separate short transactions

TWO DATABASES
    = two ordinary commits are not one atomic transaction
```

The central engineering idea is:

```text
Transaction boundaries
      ↓
Failure boundaries
      ↓
Retry boundaries
      ↓
Consistency boundaries
```

When those four boundaries are deliberately designed, Python database code becomes much easier to reason about and much safer to operate in production.
