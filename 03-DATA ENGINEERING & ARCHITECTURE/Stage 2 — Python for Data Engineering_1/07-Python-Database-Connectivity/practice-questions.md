
# Module 2.7 Practice Questions — Python Database Connectivity

## How to Use These Questions

This is the final 40-question practice set for Module 2.7 — Python Database Connectivity.

Work through the questions in order. The difficulty increases from foundational database-boundary reasoning to production-oriented design.

For each question:

1. Read the **Problem** without looking ahead.
2. Write down what Python sends, what PostgreSQL receives, and what the database/driver state should be.
3. Attempt the implementation or reasoning yourself.
4. Compare your work with the **Solution**.
5. Use **How to solve it** to identify the reasoning process you should be able to reproduce without memorizing the answer.
6. Pay attention to **Common mistake** because most production database failures come from incorrect assumptions about state, transactions, resource lifetime, or data movement.

When a question asks you to measure performance, do not invent results. Run the benchmark in the controlled PostgreSQL environment used for Module 2.7 and record the actual values.

## Difficulty Progression

| Part | Questions | What it tests |
|---|---:|---|
| Basic | Q1–Q10 | Fundamentals, small implementations, terminology applied to code |
| Moderate | Q11–Q20 | Debugging and combining two or more concepts |
| Hard | Q21–Q30 | Multi-concept production reasoning, implementation, and trade-offs |
| Advanced | Q31–Q40 | Architecture, failure recovery, correctness, performance engineering, and operational decisions |

---

# Part 1 — Basic

## Q1. Connection, Cursor, and a Parameterized Query

**Difficulty:** Basic

**Problem**

Write a small psycopg 3 example that:

1. Opens a PostgreSQL connection.
2. Creates a cursor with a context manager.
3. Executes a parameterized query that finds orders for a given customer id.
4. Fetches the first row.
5. Closes resources safely.

Then explain the responsibility of the connection versus the cursor.

**What you need to do**

Use a placeholder for the value. Do not build SQL with an f-string.

**Solution**

A connection represents the PostgreSQL session and gives Python access to transaction control. A cursor is used to execute SQL and consume the result.

```python
import psycopg

dsn = "postgresql://app_user@localhost:5432/appdb"

customer_id = 42

with psycopg.connect(dsn) as conn:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, amount
            FROM orders
            WHERE customer_id = %s
            ORDER BY id
            LIMIT 1
            """,
            (customer_id,),
        )
        row = cur.fetchone()

print(row)
```

**How to solve it**

1. Open one connection.
2. Create a cursor inside that connection.
3. Put the SQL structure in the SQL string.
4. Pass `customer_id` separately as a parameter.
5. Fetch exactly the result you need.
6. Let the context managers close resources safely.

**Why this works**

The driver keeps SQL structure separate from data values. The connection owns the session/transaction context, while the cursor handles execution and result consumption.

**Common mistake**

Using:

```python
cur.execute(f"SELECT * FROM orders WHERE customer_id = {customer_id}")
```

The value is being inserted into the SQL string instead of being passed as a bound parameter.

---

## Q2. Recognizing the DB-API Fetching Options

**Difficulty:** Basic

**Problem**

You have a cursor with a result set. Explain the practical difference among:

```python
fetchone()
fetchmany(1000)
fetchall()
```

Then identify which one is potentially dangerous for a very large result.

**What you need to do**

Explain the memory implication rather than only defining the methods.

**Solution**

- `fetchone()` consumes one row.
- `fetchmany(1000)` consumes up to 1,000 rows.
- `fetchall()` requests all remaining rows.

For a very large result, `fetchall()` is potentially dangerous because it can materialize a huge number of Python row objects at once.

```python
row = cur.fetchone()
batch = cur.fetchmany(1000)
all_rows = cur.fetchall()
```

The important engineering distinction is that the application consuming rows in batches does not by itself prove that the database result was streamed from the server.

**How to solve it**

1. Start with the API contract: each method controls how the application consumes rows.
2. Ask how many rows exist in memory at once.
3. Separate that question from how the driver obtains the result from PostgreSQL.
4. For truly large extraction, investigate server-side cursors or another streaming path.

**Why this works**

It avoids confusing application-level batching with database-side streaming.

**Common mistake**

Thinking `fetchmany()` automatically guarantees bounded memory for the whole driver/result path.

---

## Q3. Psycopg Type Adaptation

**Difficulty:** Basic

**Problem**

You need to insert an order containing:

- a `Decimal` amount,
- a timezone-aware `datetime`,
- a `UUID`,
- an optional JSON-like value represented with `Jsonb`.

Write a small parameterized insert and identify the PostgreSQL types involved.

**Solution**

```python
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

import psycopg
from psycopg.types.json import Jsonb

order_id = UUID("550e8400-e29b-41d4-a716-446655440000")
amount = Decimal("199.95")
created_at = datetime.now(timezone.utc)
payload = {"source": "batch"}

with psycopg.connect(
    "postgresql://app_user@localhost:5432/appdb"
) as conn:
    conn.execute(
        """
        INSERT INTO orders (
            id,
            amount,
            created_at,
            payload
        )
        VALUES (%s, %s, %s, %s)
        """,
        (order_id, amount, created_at, Jsonb(payload)),
    )
```

Typical PostgreSQL types are:

- `Decimal` → a numeric/decimal-compatible column.
- timezone-aware `datetime` → `timestamptz`.
- `UUID` → `uuid`.
- `Jsonb(...)` → `jsonb`.

**How to solve it**

1. Identify the Python value.
2. Identify the intended PostgreSQL type.
3. Let psycopg adapt the value rather than converting it into SQL text manually.
4. Keep timezone semantics explicit for timestamps.

**Why this works**

Psycopg performs Python-to-PostgreSQL type adaptation instead of forcing the application to hand-build literal SQL.

**Common mistake**

Converting values to strings just because PostgreSQL also accepts textual input. That can introduce precision, timezone, or formatting mistakes.

---

## Q4. Commit or Rollback on Success and Failure

**Difficulty:** Basic

**Problem**

Write a transaction block that inserts an order and a corresponding audit row. Both operations must succeed together. If either raises an exception, neither change should remain committed.

**Solution**

```python
import psycopg

with psycopg.connect(
    "postgresql://app_user@localhost:5432/appdb"
) as conn:
    with conn.transaction():
        conn.execute(
            """
            INSERT INTO orders (id, customer_id, amount)
            VALUES (%s, %s, %s)
            """,
            (1001, 42, 50),
        )

        conn.execute(
            """
            INSERT INTO pipeline_runs (run_id, status)
            VALUES (%s, %s)
            """,
            ("run-1001", "recorded"),
        )
```

The transaction context commits on normal exit and rolls back when an exception escapes the block.

**How to solve it**

1. Identify the operations that must be atomic.
2. Put them inside one transaction boundary.
3. Do not insert an API call, sleep, or long file operation inside that boundary.
4. Let exception handling cause rollback.

**Why this works**

The application expresses the business unit of work explicitly.

**Common mistake**

Opening a transaction, doing unrelated slow work, and only then committing. Long transactions can hold locks and snapshots longer than necessary.

---

## Q5. Pool Borrow and Return

**Difficulty:** Basic

**Problem**

You have a `psycopg_pool.ConnectionPool`. Show how a worker should borrow one connection for a short database operation and return it safely.

**Solution**

```python
from psycopg_pool import ConnectionPool

pool = ConnectionPool(
    "postgresql://app_user@localhost:5432/appdb",
    min_size=1,
    max_size=5,
)

with pool.connection() as conn:
    row = conn.execute(
        "SELECT count(*) FROM orders"
    ).fetchone()

print(row)
pool.close()
```

**How to solve it**

1. Create the pool once for the process.
2. Borrow a connection with `pool.connection()`.
3. Perform the short database operation.
4. Exit the context manager so the connection returns to the pool.
5. Close the pool when the process shuts down.

**Why this works**

The connection is a reusable resource. Pooling removes repeated connection-creation overhead and controls the number of concurrent database connections.

**Common mistake**

Keeping a borrowed connection while doing unrelated Python work. That can cause pool exhaustion.

---

## Q6. Build a Simple SQLAlchemy Core Query

**Difficulty:** Basic

**Problem**

Use SQLAlchemy Core to select customer ids and total order amount for customers whose total exceeds a parameterized threshold.

**Solution**

```python
from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql+psycopg://app_user@localhost:5432/appdb"
)

with engine.connect() as conn:
    rows = conn.execute(
        text(
            """
            SELECT customer_id, SUM(amount) AS total_amount
            FROM orders
            GROUP BY customer_id
            HAVING SUM(amount) > :minimum
            """
        ),
        {"minimum": 1000},
    ).all()

print(rows)
```

**How to solve it**

1. Create the engine once.
2. Open a connection.
3. Use `text()` for raw SQL when that is the chosen Core style.
4. Bind the threshold as a parameter.
5. Consume the result using an appropriate result method.

**Why this works**

SQLAlchemy Core provides an abstraction around connection management and SQL execution while still exposing SQL concepts.

**Common mistake**

Creating a new engine for every query. The engine owns connection-pooling behavior, so it is normally a process-level object rather than a per-query object.

---

## Q7. Identify an ORM N+1 Pattern

**Difficulty:** Basic

**Problem**

You load 100 pipelines and then loop over them, accessing `pipeline.runs` for each pipeline. Explain why this can generate far more SQL queries than expected.

**Solution**

The relationship may be lazily loaded. The first query loads the 100 pipelines, and then each access to `pipeline.runs` can trigger another query. That can produce roughly one query for the parent collection plus one query per parent.

The fix is to choose an explicit eager-loading strategy such as `selectinload()` when the workload calls for it.

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

stmt = (
    select(Pipeline)
    .options(selectinload(Pipeline.runs))
)

pipelines = session.scalars(stmt).all()
```

**How to solve it**

1. Count the logical parent query.
2. Inspect relationship access in the loop.
3. Ask whether every access can trigger SQL.
4. Use SQL logging to verify the real query count.
5. Choose an eager-loading strategy and re-measure.

**Why this works**

The database work becomes more deliberate rather than accidentally being driven by object access.

**Common mistake**

Assuming a relationship attribute is just an in-memory Python list because it is written with attribute syntax.

---

## Q8. Alembic Migration Lifecycle

**Difficulty:** Basic

**Problem**

You create a new Alembic migration adding a `currency` column. Name the basic commands you would use to:

1. Create the revision.
2. Apply all pending migrations.
3. See the current database revision.
4. See migration history.
5. Roll back one revision.

**Solution**

```bash
alembic revision -m "add currency to orders"
alembic upgrade head
alembic current
alembic history
alembic downgrade -1
```

The migration script becomes the versioned record of the schema change.

**How to solve it**

1. Create a revision.
2. Put the intended schema operation in the revision.
3. Apply it with `upgrade`.
4. Inspect state with `current` and history with `history`.
5. Use `downgrade` only when the migration's reverse operation is understood and safe.

**Why this works**

Schema evolution becomes versioned and repeatable instead of being an undocumented manual change.

**Common mistake**

Trusting autogenerate or editing a migration that has already been applied in production without understanding the consequences.

---

## Q9. PostgreSQL COPY from Python

**Difficulty:** Basic

**Problem**

You need to load a sequence of order rows into a PostgreSQL table using psycopg 3 `COPY ... FROM STDIN`. Write the core loop using `copy.write_row()`.

**Solution**

```python
import psycopg

rows = [
    (1, 42, 10.50),
    (2, 43, 25.00),
    (3, 44, 90.00),
]

with psycopg.connect(
    "postgresql://app_user@localhost:5432/appdb"
) as conn:
    with conn.cursor() as cur:
        with cur.copy(
            """
            COPY orders (id, customer_id, amount)
            FROM STDIN
            """
        ) as copy:
            for row in rows:
                copy.write_row(row)
```

**How to solve it**

1. Choose the target columns explicitly.
2. Start a COPY-from-STDIN operation.
3. Feed rows to the COPY stream.
4. Keep the data values separate from the SQL command itself.
5. Let the context close the COPY operation correctly.

**Why this works**

COPY is a PostgreSQL bulk-data protocol designed for high-volume movement rather than one application SQL statement per row.

**Common mistake**

Treating COPY as a magic validation layer. COPY transport success does not automatically mean the source data meets every business rule.

---

## Q10. Named Cursor vs Client-Side Cursor

**Difficulty:** Basic

**Problem**

A table contains 20 million rows. Explain why this pattern is risky:

```python
cur.execute("SELECT * FROM orders")
rows = cur.fetchall()
```

Then show the basic idea for a server-side/named cursor.

**Solution**

The first pattern can materialize a very large result in the client and create a severe Python-memory spike.

A named cursor provides a server-side cursor path:

```python
with psycopg.connect(
    "postgresql://app_user@localhost:5432/appdb"
) as conn:
    with conn.cursor(name="extract") as cur:
        cur.execute(
            """
            SELECT id, customer_id, amount
            FROM orders
            """
        )

        while True:
            batch = cur.fetchmany(10_000)
            if not batch:
                break
            process(batch)
```

**How to solve it**

1. Identify the size of the result.
2. Reject `fetchall()` when it is unnecessary.
3. Use a named cursor when database-side cursor behavior is appropriate.
4. Consume bounded batches.
5. Measure memory and throughput rather than guessing.

**Why this works**

The goal is controlled result transfer so application memory is governed primarily by the active batch and processing buffers rather than by total source rows.

**Common mistake**

Assuming `fetchmany()` on every cursor means the entire result was never buffered by the driver.

---

# Part 2 — Moderate

## Q11. Safely Building a Dynamic ORDER BY

**Difficulty:** Moderate

**Problem**

A reporting function accepts:

```python
order_by = "amount"
direction = "desc"
```

Both values come from configuration. Explain why they cannot simply be passed as ordinary query parameters, and show a safe approach using an allowlist and `psycopg.sql`.

**Solution**

Ordinary value placeholders protect data values, not SQL identifiers or SQL keywords. A column name and sort direction are part of SQL structure.

```python
from psycopg import sql

ALLOWED_COLUMNS = {
    "id": sql.Identifier("id"),
    "amount": sql.Identifier("amount"),
    "created_at": sql.Identifier("created_at"),
}

ALLOWED_DIRECTIONS = {
    "asc": sql.SQL("ASC"),
    "desc": sql.SQL("DESC"),
}

def build_ordered_query(order_by: str, direction: str):
    try:
        column = ALLOWED_COLUMNS[order_by]
        sort = ALLOWED_DIRECTIONS[direction.lower()]
    except KeyError as exc:
        raise ValueError("Unsupported ordering option") from exc

    return sql.SQL(
        "SELECT id, amount, created_at FROM orders "
        "ORDER BY {} {}"
    ).format(column, sort)
```

**How to solve it**

1. Decide whether each input is data or SQL structure.
2. Use parameters for data values.
3. Use an allowlist for permitted structural choices.
4. Use `Identifier` for identifiers.
5. Reject anything outside the approved choices.

**Why this works**

The query builder never treats arbitrary input as raw SQL syntax.

**Common mistake**

Seeing that a value parameter cannot represent a table/column name and then falling back to string formatting.

---

## Q12. Recovering a Failed Transaction

**Difficulty:** Moderate

**Problem**

This code fails on the first insert with a unique-key error, then tries another query:

```python
conn.execute(
    "INSERT INTO orders (id) VALUES (%s)",
    (10,),
)

try:
    conn.execute(
        "INSERT INTO orders (id) VALUES (%s)",
        (11,),
    )
except Exception:
    pass

conn.execute("SELECT count(*) FROM orders")
```

Explain why the final query can fail and how to recover.

**Solution**

In PostgreSQL, once a statement error aborts the current transaction, later statements in that transaction cannot proceed normally until the transaction is rolled back.

The basic recovery is:

```python
try:
    conn.execute(
        "INSERT INTO orders (id) VALUES (%s)",
        (10,),
    )
except Exception:
    conn.rollback()

row = conn.execute(
    "SELECT count(*) FROM orders"
).fetchone()
```

For batch-level fault isolation, a savepoint/nested transaction is often more appropriate than rolling back the entire outer transaction.

**How to solve it**

1. Identify whether a transaction is already open.
2. Assume a database error may have changed transaction state.
3. Roll back before attempting unrelated work.
4. Use savepoints when only a nested unit should fail.

**Why this works**

The Python exception and the PostgreSQL transaction state are related but not identical. Recovering the Python exception without recovering transaction state leaves the connection unusable for subsequent statements.

**Common mistake**

Catching the exception and continuing without `rollback()`.

---

## Q13. Understanding PostgreSQL Types and Time Zones

**Difficulty:** Moderate

**Problem**

A pipeline receives UTC-aware Python datetimes but stores them in PostgreSQL. Explain what you should check if different engineers report different timestamp values when reading the same rows.

Include:

- `timestamptz`,
- Python timezone-aware `datetime`,
- session timezone,
- UTC handling.

**Solution**

The first check is whether the column is `timestamptz` and whether the application is consistently using timezone-aware datetimes.

A production-safe approach is to choose a clear UTC convention and make the session/application behavior explicit.

```python
from datetime import datetime, timezone

created_at = datetime.now(timezone.utc)

with psycopg.connect(
    "postgresql://app_user@localhost:5432/appdb"
) as conn:
    conn.execute("SET TIME ZONE 'UTC'")
    conn.execute(
        """
        INSERT INTO events (event_time)
        VALUES (%s)
        """,
        (created_at,),
    )
```

**How to solve it**

1. Inspect the PostgreSQL column type.
2. Inspect the Python value's `tzinfo`.
3. Check the session timezone.
4. Compare values using the chosen UTC convention.
5. Test round-tripping from Python → PostgreSQL → Python.

**Why this works**

Time correctness depends on the combination of column semantics, driver adaptation, and session configuration.

**Common mistake**

Using naive datetimes while assuming they represent UTC automatically.

---

## Q14. Pool Sizing With 32 Workers

**Difficulty:** Moderate

**Problem**

A process has 32 worker threads, but the PostgreSQL instance has a strict connection budget. Each worker does a short query followed by CPU work.

Explain why `max_size=32` is not automatically required, and identify the factors you would use to choose a smaller pool.

**Solution**

Pool size should be driven by actual concurrent database demand and the database's connection budget, not simply by the number of Python workers.

Relevant factors include:

- how many workers can be waiting on the database simultaneously,
- query duration,
- PostgreSQL `max_connections`,
- connections needed by other services,
- number of processes, not just threads,
- whether PgBouncer or another external pooler exists,
- observed pool wait time and throughput.

A process might deliberately use a pool smaller than its worker count so excess workers wait briefly for a connection instead of creating 32 PostgreSQL sessions.

**How to solve it**

1. Count processes.
2. Estimate or measure peak simultaneous DB usage.
3. Reserve connection headroom for other workloads.
4. Start from a constrained pool.
5. Benchmark throughput and wait time.
6. Observe PostgreSQL with `pg_stat_activity`.

**Why this works**

Connections consume server resources. A larger pool can increase concurrency without improving useful throughput.

**Common mistake**

Treating “workers = pool size” as a universal formula.

---

## Q15. SQLAlchemy Core vs ORM for a Data-Engineering Operation

**Difficulty:** Moderate

**Problem**

You need to perform a set-based update affecting 500,000 rows. A teammate proposes loading all rows as ORM objects, changing them one by one, and committing.

Explain the main concerns and give a more suitable SQLAlchemy approach.

**Solution**

For a set-based data operation, materializing hundreds of thousands of ORM objects introduces object creation, identity-map tracking, and unit-of-work overhead.

A Core statement is more aligned with the operation:

```python
from sqlalchemy import update

stmt = (
    update(orders)
    .where(orders.c.status == "pending")
    .values(status="processed")
)

with engine.begin() as conn:
    conn.execute(stmt)
```

**How to solve it**

1. Classify the operation: object-centric or set-based?
2. Identify whether Python needs one object per row.
3. Prefer a database-side set operation when row-by-row object behavior is unnecessary.
4. Measure the difference when performance matters.

**Why this works**

The ORM is useful for tracked object state and operational metadata. Large set-based transformations often benefit from Core or database-native operations.

**Common mistake**

Selecting ORM simply because the codebase already uses ORM elsewhere.

---

## Q16. Alembic Autogenerate and a Column Rename

**Difficulty:** Moderate

**Problem**

You rename:

```text
customer_name
→
full_name
```

Autogenerate produces a drop-and-add style migration. Explain the danger and what you should do before applying it.

**Solution**

A drop-and-add interpretation can destroy existing values because Alembic cannot always infer that the operation is a rename.

The migration should be reviewed and corrected manually so the database performs a rename operation rather than dropping the old column and adding a new empty one.

For example:

```python
from alembic import op

op.alter_column(
    "customers",
    "customer_name",
    new_column_name="full_name",
)
```

**How to solve it**

1. Compare the intended schema change with the generated migration.
2. Ask whether data should survive.
3. Treat a rename as a semantic operation, not just a structural diff.
4. Edit the migration before applying it.
5. Test against a copy containing representative data.

**Why this works**

Autogenerate compares schemas; it does not always know the business meaning of a change.

**Common mistake**

Applying generated migrations without reading them.

---

## Q17. COPY Into Staging Before MERGE

**Difficulty:** Moderate

**Problem**

You receive a large Parquet file containing customer updates. You need to validate the incoming data before modifying the production target table.

Describe the staging flow and show the high-level SQL/Python sequence.

**Solution**

The production-oriented pattern is:

```text
Parquet
  ↓
COPY into staging
  ↓
validate staging
  ↓
MERGE / upsert target
  ↓
cleanup staging
```

Example sequence:

```python
with conn.transaction():
    copy_parquet_into_staging(conn, path="customers.parquet")

    invalid = conn.execute(
        """
        SELECT count(*)
        FROM staging_customers
        WHERE customer_id IS NULL
        """
    ).fetchone()[0]

    if invalid:
        raise ValueError("Validation failed")

    conn.execute(
        """
        MERGE INTO customers AS target
        USING staging_customers AS source
        ON target.customer_id = source.customer_id
        WHEN MATCHED THEN
            UPDATE SET name = source.name
        WHEN NOT MATCHED THEN
            INSERT (customer_id, name)
            VALUES (source.customer_id, source.name)
        """
    )
```

**How to solve it**

1. Separate transport from business validation.
2. Load into staging.
3. Validate in PostgreSQL.
4. Change the target only after validation succeeds.
5. Keep the target mutation controlled and repeatable.

**Why this works**

The staging boundary prevents unvalidated bulk transport from directly becoming production state.

**Common mistake**

Loading directly into the final table and discovering bad rows only after partial target mutation.

---

## Q18. Idempotency and Safe Reruns

**Difficulty:** Moderate

**Problem**

A batch job may be retried after a timeout. The input file contains order updates identified by `order_id`. Design one way to make repeated execution safe.

**Solution**

A common approach is to load into staging and then use a deterministic upsert/MERGE keyed by `order_id`.

The target operation must produce the same final state when the same input is applied again.

Conceptually:

```text
same input
   ↓
same staging content
   ↓
same deterministic merge
   ↓
same target state
```

**How to solve it**

1. Identify the business key.
2. Define what “same input twice” should mean.
3. Ensure the target has an appropriate uniqueness constraint.
4. Use an idempotent merge/upsert pattern.
5. Test the exact same file twice and compare target state.

**Why this works**

Idempotency reduces the risk of duplicating data when failure recovery cannot know exactly how much work already committed.

**Common mistake**

Assuming “the job failed” means “nothing committed.”

---

## Q19. `fetchmany()` But Memory Still Grows

**Difficulty:** Moderate

**Problem**

A developer writes:

```python
cur.execute("SELECT * FROM orders")

while True:
    batch = cur.fetchmany(10_000)
    if not batch:
        break
    process(batch)
```

The process still uses unexpectedly high memory.

Explain what assumption may be wrong and what you should test.

**Solution**

The likely incorrect assumption is that `fetchmany()` proves database-side streaming.

With a normal client-side cursor/result path, the driver may already have received or buffered a substantial portion of the result before the application consumes batches.

The next test is to compare:

```text
client-side cursor + fetchmany
vs
named/server-side cursor + fetchmany
```

and measure peak memory.

**How to solve it**

1. Keep the query identical.
2. Measure process memory.
3. Replace the cursor with a named/server-side cursor.
4. Keep the batch size constant.
5. Compare memory, elapsed time, and connection/transaction duration.

**Why this works**

It isolates buffering behavior from the application batching loop.

**Common mistake**

Defining “streaming” solely by the existence of `fetchmany()`.

---

## Q20. COPY Data Type Failure

**Difficulty:** Moderate

**Problem**

A CSV COPY load fails. Investigation shows that:

- one row contains a literal `NULL`,
- one timestamp has an unexpected timezone representation,
- a decimal field has an unexpected textual format.

Explain what you would inspect before retrying.

**Solution**

Inspect the COPY format contract:

1. What marker represents SQL `NULL`?
2. What delimiter, quote, and escape rules are active?
3. Are timestamp values compatible with the target type and expected timezone semantics?
4. Are decimals represented without accidental formatting or precision loss?
5. Are data types aligned between the source representation and PostgreSQL columns?

For complex or high-risk data, typed row-oriented COPY, an Arrow/ADBC path, or a stronger staging/validation boundary may be easier to control than ad hoc CSV serialization.

**How to solve it**

1. Read the exact COPY format configuration.
2. Inspect representative bad rows.
3. Compare source representation to target PostgreSQL types.
4. Validate with a small controlled load.
5. Re-run the larger batch only after the format contract is correct.

**Why this works**

Bulk protocols move data efficiently, but the format contract still has to be correct.

**Common mistake**

Treating a COPY failure as a generic performance problem instead of first inspecting data-format semantics.

---

# Part 3 — Hard

## Q21. Retry the Whole Transaction After Serialization Failure

**Difficulty:** Hard

**Problem**

At `SERIALIZABLE` isolation, a transaction sometimes fails with a serialization error. A developer retries only the final SQL statement that failed.

Explain why this is insufficient and design the correct retry unit.

**Solution**

A serialization failure can invalidate the transaction's assumptions as a whole. Retrying only one statement is not equivalent to re-running the transaction from a clean state.

The retry unit should be the entire transaction:

```python
import time
from psycopg.errors import SerializationFailure

def run_transaction(conn):
    with conn.transaction():
        conn.execute("SELECT ...")
        conn.execute("UPDATE ...")
        conn.execute("INSERT ...")

def run_with_retry(conn, attempts=3):
    for attempt in range(attempts):
        try:
            run_transaction(conn)
            return
        except SerializationFailure:
            conn.rollback()
            if attempt == attempts - 1:
                raise
            time.sleep(0.5 * (2 ** attempt))
```

**How to solve it**

1. Identify the transaction boundary.
2. Classify serialization failure as a potentially retryable transaction failure.
3. Roll back the failed transaction.
4. Re-run the entire unit of work.
5. Use bounded retries and backoff.
6. Re-run only if the operation is safe under the retry design.

**Why this works**

The database's serializable result is a property of the transaction as a whole.

**Common mistake**

Retrying an individual statement while keeping the rest of the old transaction context.

---

## Q22. Connection Pool Capacity Across Processes

**Difficulty:** Hard

**Problem**

You deploy four worker processes. Each process has a pool configured:

```text
min_size = 2
max_size = 8
```

PostgreSQL has limited connection capacity, and another application also uses the same database.

Compute the maximum connections this deployment could request from PostgreSQL and explain why the calculation must be done across processes.

**Solution**

The theoretical maximum from the four application processes is:

```text
4 processes × 8 connections
= 32 possible PostgreSQL connections
```

The `min_size` of 2 means the pools can maintain a smaller baseline, but `max_size` determines the upper bound each process can reach.

The real connection budget must also account for:

- PostgreSQL's own capacity,
- other applications,
- administrative connections,
- monitoring,
- migrations,
- background jobs,
- external poolers.

**How to solve it**

1. Treat each process as an independent pool owner.
2. Multiply process count by per-process maximum.
3. Add other consumers.
4. Compare the resulting upper bound with the database connection budget.
5. Leave operational headroom.

**Why this works**

Pools are local resources. A “max 8” pool in four processes does not mean 8 total database connections.

**Common mistake**

Looking at one process in isolation.

---

## Q23. Dynamic Filters With SQLAlchemy Core

**Difficulty:** Hard

**Problem**

Build a SQLAlchemy Core query for `orders` with optional filters:

- country list,
- minimum amount,
- start date,
- end date.

None of the filters is guaranteed to be present.

You must not build the SQL with string concatenation or f-strings.

**Solution**

Build expressions incrementally:

```python
from sqlalchemy import select

conditions = []

if countries:
    conditions.append(orders.c.country.in_(countries))

if minimum_amount is not None:
    conditions.append(orders.c.amount >= minimum_amount)

if start_date is not None:
    conditions.append(orders.c.created_at >= start_date)

if end_date is not None:
    conditions.append(orders.c.created_at < end_date)

stmt = select(
    orders.c.id,
    orders.c.customer_id,
    orders.c.amount,
)

if conditions:
    stmt = stmt.where(*conditions)
```

**How to solve it**

1. Treat filter choices as structure that your application controls.
2. Construct SQL expression objects rather than SQL strings.
3. Add only the predicates actually requested.
4. Let SQLAlchemy bind the underlying values.

**Why this works**

It keeps query composition structured and parameterized.

**Common mistake**

Constructing:

```python
where_sql = f"country = '{country}'"
```

and mixing data values with SQL syntax.

---

## Q24. ORM N+1: Diagnose, Fix, Measure

**Difficulty:** Hard

**Problem**

A pipeline admin page lists 5,000 pipelines and then displays each pipeline's latest runs. The page suddenly becomes slow.

Explain how you would determine whether N+1 is the problem and compare `selectinload` and `joinedload`.

**Solution**

First enable SQL logging and count statements. If the code loads pipelines and then accesses `pipeline.runs` repeatedly, lazy loading can produce many additional queries.

A `selectinload()` approach can batch related objects into separate SELECT statements:

```python
stmt = (
    select(Pipeline)
    .options(selectinload(Pipeline.runs))
)

pipelines = session.scalars(stmt).all()
```

`joinedload()` can load related data through a join, but the shape of the relationship and result set matters. A joined strategy can produce repeated parent data in the SQL result and must be evaluated for the specific query.

**How to solve it**

1. Measure the number of SQL statements before the change.
2. Inspect relationship loading behavior.
3. Apply `selectinload` or `joinedload`.
4. Measure statement count, runtime, and result volume.
5. Keep the strategy that fits the actual query shape and operational need.

**Why this works**

ORM performance should be treated as a measured query-plan/data-shape problem, not as a framework ideology question.

**Common mistake**

Fixing N+1 without checking how much data the eager-loading strategy actually transfers.

---

## Q25. Safe Migration for a 10-Million-Row Table

**Difficulty:** Hard

**Problem**

You need to add a `currency` column to a 10-million-row `orders` table and eventually make it `NOT NULL`.

Design a migration sequence that minimizes production risk.

**Solution**

Use an expand-and-contract style sequence:

```text
1. Add nullable currency column
2. Deploy code that can write/read the new column safely
3. Backfill in batches
4. Validate completeness
5. Enforce NOT NULL when safe
6. Remove temporary compatibility logic later if needed
```

For large-table migrations, also consider:

- `lock_timeout`,
- the duration of each migration step,
- whether any index should be created concurrently,
- keeping large data backfills separate from the schema change transaction.

**How to solve it**

1. Separate structural change from bulk data movement.
2. Make the first schema change compatible with existing rows.
3. Backfill in controlled chunks.
4. Validate before tightening constraints.
5. Only then enforce the final invariant.

**Why this works**

A large-table schema operation and a 10-million-row data update have different failure and locking characteristics.

**Common mistake**

Adding a non-null column with a full-table rewrite/backfill as one blocking deployment step without measuring its production impact.

---

## Q26. Isolating a Bad COPY Row

**Difficulty:** Hard

**Problem**

A large COPY batch fails because one or more rows are invalid. PostgreSQL reports COPY failure, and you do not know which rows are bad.

Design a controlled debugging method that finds the bad data without abandoning the entire dataset.

**Solution**

A practical diagnostic approach is batch splitting:

```text
large batch
   ↓
split into two smaller batches
   ↓
which half fails?
   ↓
split the failing half
   ↓
repeat
   ↓
isolate bad row(s)
```

Then:

1. Preserve the bad input.
2. Record the reason it failed.
3. Quarantine the bad row(s) or corrected representation.
4. Load the valid rows.
5. Record reconciliation and rejection metrics.

**How to solve it**

1. Treat the whole COPY failure as a transport failure for that batch.
2. Do not assume only one row is bad.
3. Narrow the failing input using controlled partitioning.
4. Quarantine rather than silently dropping data.
5. Measure accepted and rejected records.

**Why this works**

Batch splitting turns an opaque bulk failure into a reproducible diagnostic problem.

**Common mistake**

Skipping the entire source file after the first COPY error.

---

## Q27. Named Cursor to Parquet With Bounded Memory

**Difficulty:** Hard

**Problem**

Implement the core of:

```python
extract_table_to_parquet(
    conn,
    query,
    path,
    batch_size,
)
```

Requirements:

- named cursor,
- bounded batch size,
- explicit Arrow schema,
- `ParquetWriter`,
- temporary path,
- atomic final rename,
- row-count tracking.

**Solution**

A production-oriented sketch is:

```python
from pathlib import Path
import os

import pyarrow as pa
import pyarrow.parquet as pq
from psycopg.rows import tuple_row

def extract_table_to_parquet(conn, query, path, batch_size, schema):
    final_path = Path(path)
    temp_path = final_path.with_suffix(final_path.suffix + ".tmp")
    rows_written = 0
    writer = None

    try:
        with conn.cursor(
            name="extract",
            row_factory=tuple_row,
        ) as cur:
            cur.itersize = batch_size
            cur.execute(query)

            while True:
                rows = cur.fetchmany(batch_size)
                if not rows:
                    break

                batch_table = pa.Table.from_pylist(
                    [dict(zip(schema.names, row)) for row in rows],
                    schema=schema,
                )

                if writer is None:
                    writer = pq.ParquetWriter(
                        temp_path,
                        schema,
                    )

                writer.write_table(batch_table)
                rows_written += len(rows)

        if writer is not None:
            writer.close()
            writer = None

        # Final validation belongs before publication.
        os.replace(temp_path, final_path)

        return rows_written

    except Exception:
        if writer is not None:
            writer.close()
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass
        raise
```

For real production code, you would also validate the final file and reconcile the row count with a source count taken over the same logical data boundary.

**How to solve it**

1. Create the temporary output path.
2. Open the named cursor.
3. Fetch one bounded batch.
4. Convert only that batch to Arrow.
5. Write that batch to `ParquetWriter`.
6. Repeat until exhaustion.
7. Close the writer.
8. Validate.
9. Atomically rename the temporary file.

**Why this works**

The active Python batch is bounded by `batch_size`; total source row count does not need to become one giant Python list.

**Common mistake**

Writing directly to `orders.parquet` and assuming the existence of the file means extraction completed.

---

## Q28. Keyset Pagination Checkpoint

**Difficulty:** Hard

**Problem**

An extraction must be restartable. Rows are ordered by `(updated_at, id)` and each batch contains 10,000 rows.

Write the conceptual SQL for the next batch after a checkpoint.

**Solution**

```sql
SELECT id, updated_at, amount
FROM orders
WHERE (updated_at, id) > (%s, %s)
ORDER BY updated_at, id
LIMIT %s;
```

The checkpoint contains the last successfully written key:

```text
last_updated_at
last_id
```

After a successful batch:

```text
write batch
   ↓
confirm output success
   ↓
persist checkpoint for last row
```

**How to solve it**

1. Use a deterministic ordering.
2. Use a composite key when the timestamp alone is not unique.
3. Save the key of the final row from the successfully completed batch.
4. Resume with a strict `>` predicate.
5. Verify uniqueness/stability assumptions for the ordering key.

**Why this works**

Keyset pagination describes a resume position by data key rather than by a fragile numeric offset.

**Common mistake**

Ordering only by `updated_at` when many rows can share the same timestamp.

---

## Q29. Design a Fair 20-Million-Row Benchmark

**Difficulty:** Hard

**Problem**

Design a benchmark comparing:

- client-side cursor,
- named cursor,
- `COPY TO STDOUT`,
- ADBC Arrow extraction.

Your benchmark must compare methods fairly.

**Solution**

Control these variables:

```text
same table
same columns
same filter
same PostgreSQL instance
same machine/container
same Python version
same relevant driver versions
same output target
same data
```

Measure:

- elapsed time,
- peak Python memory,
- rows/sec,
- output size,
- connection duration,
- query duration where practical.

Repeat runs and document whether caches were warm or cold.

Do not mix result formats without explaining how that affects the comparison. Do not fabricate numbers.

**How to solve it**

1. Define one workload.
2. Define one correctness check.
3. Implement each extraction method for that exact workload.
4. Measure memory and time independently.
5. Repeat runs.
6. Compare measured results to your predictions.

**Why this works**

A benchmark is evidence only when the workload and measurement method are controlled.

**Common mistake**

Using a different query or output format for each method and then calling the results directly comparable.

---

## Q30. Primary vs Read Replica for a Heavy Extract

**Difficulty:** Hard

**Problem**

A nightly export scans a large table for several hours. The primary also handles user writes.

Compare running the export on the primary versus a read replica. Include:

- freshness,
- replica lag,
- resource isolation,
- long-running reads,
- operational risk.

**Solution**

**Primary**

- can provide the freshest source state,
- but the extraction competes for database resources with production writes and queries.

**Read replica**

- can move much of the read workload away from the primary,
- but extracted data may be behind the primary because of replication lag,
- and the replica itself has finite CPU, I/O, memory, and connection capacity.

Neither choice is universal. The correct design depends on the required freshness, consistency, workload size, and source capacity.

**How to solve it**

1. Define the freshness requirement.
2. Measure expected extract duration.
3. Check replica lag behavior.
4. Evaluate source workload impact.
5. Run a representative load test where possible.
6. Document the operational trade-off.

**Why this works**

Source protection is part of extraction correctness in production.

**Common mistake**

Assuming a read replica makes the extraction free or invisible to the platform.

---

# Part 4 — Advanced

## Q31. Unknown Commit Outcome After Connection Loss

**Difficulty:** Advanced

**Problem**

A transaction updates a warehouse target. The application loses the network connection during `COMMIT`. The client cannot determine whether the commit reached PostgreSQL.

The job is allowed to retry.

Design the operation so that a retry does not corrupt the target.

**Solution**

Treat commit outcome as potentially unknown. Do not assume the first transaction definitely rolled back.

The practical design is to make the operation idempotent:

```text
input batch
   ↓
deterministic key
   ↓
upsert / MERGE
   ↓
safe repeated application
```

For example, use a stable business key and deterministic values:

```sql
MERGE INTO orders AS target
USING staging_orders AS source
ON target.order_id = source.order_id
WHEN MATCHED THEN
    UPDATE SET amount = source.amount,
                   status = source.status
WHEN NOT MATCHED THEN
    INSERT (order_id, amount, status)
    VALUES (source.order_id, source.amount, source.status);
```

**How to solve it**

1. Recognize that network failure during COMMIT creates uncertainty.
2. Avoid relying on “retry means clean slate.”
3. Use an idempotent write model.
4. Re-run the whole intended operation.
5. Reconcile the final target state.

**Why this works**

Idempotency is a practical way to survive ambiguous commit outcomes.

**Common mistake**

Blindly re-inserting rows and assuming an uncertain commit must have rolled back.

---

## Q32. Transaction-Pooling PgBouncer and Session State

**Difficulty:** Advanced

**Problem**

An application works correctly when it connects directly to PostgreSQL, but behavior changes after placing PgBouncer in transaction-pooling mode.

The application relies on:

- session-level `SET`,
- prepared statements,
- `LISTEN`,
- advisory locks held across transactions.

Explain why those features require special attention.

**Solution**

Transaction pooling can move a transaction from one PostgreSQL server connection to another over time. Features whose semantics depend on staying on the same server session can therefore become incompatible or require configuration/design changes.

Examples from the module include:

- session state,
- some prepared-statement setups,
- `LISTEN`,
- advisory locks held across transactions.

**How to solve it**

1. Identify whether the feature is transaction-scoped or session-scoped.
2. Check what pooling mode is being used.
3. Verify whether the application expects server-session affinity.
4. Test the behavior through the actual pooler mode.
5. Redesign or choose a compatible pooling mode when required.

**Why this works**

Application pooling and external poolers change the lifecycle relationship between application activity and physical PostgreSQL sessions.

**Common mistake**

Treating all pooling modes as interchangeable.

---

## Q33. Production Migration With Expand-and-Contract

**Difficulty:** Advanced

**Problem**

A production system has a `customer_name` column used by existing readers. You want to replace it with a new `display_name` column while avoiding a breaking deployment.

Design the migration/deployment sequence.

**Solution**

A safe expand-and-contract sequence is:

```text
1. Add display_name as nullable
2. Deploy code that can read either representation
3. Dual-write display_name for new changes
4. Backfill old rows in batches
5. Validate display_name completeness
6. Switch readers to display_name
7. Remove old-field dependencies
8. Later remove customer_name
```

The exact sequence depends on application compatibility requirements, but the key is that each deployed step remains compatible with the surrounding versions.

**How to solve it**

1. Add the new structure first.
2. Make old and new application versions coexist temporarily.
3. Backfill separately from the schema change.
4. Switch readers only after validation.
5. Remove the old structure only after dependencies are gone.

**Why this works**

The database and application evolve in compatible increments rather than requiring a single atomic cutover.

**Common mistake**

Renaming or dropping the old column immediately because the new schema is logically equivalent.

---

## Q34. Recovering a 20-Million-Row Extract After a Network Failure

**Difficulty:** Advanced

**Problem**

A nightly extract:

- processes a 20-million-row `orders` table,
- writes Parquet,
- fails after approximately 8 million rows,
- leaves a partial `.parquet` file,
- loses the database connection.

The next run must not publish duplicate or incomplete output.

Design the recovery architecture.

**Solution**

Use a restartable, checkpointed design:

```text
keyset pagination
      ↓
bounded batch
      ↓
write batch
      ↓
checkpoint last successful key
      ↓
repeat
```

Use a temporary output path:

```text
orders.parquet.tmp
```

and only publish:

```text
orders.parquet
```

after completion and validation.

A robust sequence is:

```text
start/resume
   ↓
read checkpoint
   ↓
extract next batch
   ↓
write batch successfully
   ↓
persist checkpoint
   ↓
repeat
   ↓
close writer
   ↓
reconcile source/output
   ↓
validate Parquet
   ↓
atomic rename
```

**How to solve it**

1. Discard or isolate the incomplete final-path output.
2. Resume from the last confirmed checkpoint.
3. Ensure checkpoint advancement happens after output success.
4. Continue until all rows are processed.
5. Compare source/output keys or another correctness proof.
6. Publish only after final validation.

**Why this works**

The checkpoint represents completed output work, not merely attempted work.

**Common mistake**

Saving the checkpoint before writing the corresponding batch.

---

## Q35. Three Related Tables From One Consistent Snapshot

**Difficulty:** Advanced

**Problem**

You must export:

- `customers`,
- `orders`,
- `payments`

so that downstream processing sees a mutually compatible point in time.

Design the PostgreSQL transaction strategy.

**Solution**

Use one `REPEATABLE READ` transaction when the consistency requirement and workload permit it:

```text
BEGIN
  ↓
REPEATABLE READ snapshot
  ↓
extract customers
  ↓
extract orders
  ↓
extract payments
  ↓
COMMIT
```

Each extraction observes the same logical snapshot established for the transaction.

The operational cost is that the transaction/snapshot may remain open for a long time. That can affect cleanup/vacuum behavior and source resources, so the design must be evaluated before production deployment.

**How to solve it**

1. Determine whether cross-table point-in-time consistency is actually required.
2. Start one transaction with the required isolation level.
3. Run the three extracts inside it.
4. Measure transaction duration.
5. Monitor PostgreSQL state during the extract.
6. Reconcile each output before publication.

**Why this works**

All three tables are read from a compatible logical snapshot instead of independent snapshots taken at different times.

**Common mistake**

Running three separate transactions and calling the result “one snapshot.”

---

## Q36. Resumable Extraction: Proving No Missing or Duplicate Rows

**Difficulty:** Advanced

**Problem**

A keyset-based extraction uses `(updated_at, id)` and checkpoints after every successful batch. The process is killed and restarted twice.

Explain how you would prove that the final output has no missing rows and no duplicates.

**Solution**

Do not rely on row count alone.

Use multiple signals:

```text
source key set
      vs
output key set
```

and verify:

- number of output rows,
- uniqueness of output business/primary keys,
- continuity of checkpoint progression,
- coverage of the intended extraction boundary,
- absence of duplicate keys,
- source/output key comparison where practical.

For example, if the extraction's logical target is the set of rows satisfying a fixed predicate, compare key sets or hashes over those keys between the source snapshot/boundary and output.

**How to solve it**

1. Define the exact extraction boundary.
2. Define the key that uniquely identifies a row.
3. Verify output-key uniqueness.
4. Compare source and output counts.
5. Compare source and output key sets when feasible.
6. Inspect checkpoint transitions.

**Why this works**

A missing row and an extra duplicate can cancel numerically. Row count alone cannot prove correctness.

**Common mistake**

Checking only:

```text
source_count == output_count
```

and declaring success.

---

## Q37. Choosing ORM, Core, COPY, or Named Cursor for Four Workloads

**Difficulty:** Advanced

**Problem**

You have four independent jobs:

1. Update 200 pipeline metadata rows.
2. Load 5 million orders into PostgreSQL.
3. Extract 30 million orders into Parquet with per-row Python transformation.
4. Run a large set-based SQL transformation inside PostgreSQL.

Design a Module 2.7 technique selection for each job and justify the reasoning.

**Solution**

| Workload | Plausible technique | Reasoning |
|---|---|---|
| Pipeline metadata | SQLAlchemy ORM | Small operational/object-oriented records fit the Session/Unit of Work model |
| 5M-row load | COPY or another measured bulk path | High-volume input rewards bulk transport and minimizes per-row overhead |
| 30M-row extract with Python transformation | Named/server-side cursor or another measured streaming path | Need bounded memory and direct row-oriented processing |
| Large set-based SQL transformation | SQLAlchemy Core or direct SQL | The database can perform the set operation without materializing every row as ORM objects |

These are workload-specific choices, not universal rankings.

**How to solve it**

1. Characterize each workload.
2. Ask whether the job is object-centric, bulk transport, streaming extraction, or set-based SQL.
3. Choose the smallest abstraction that preserves correctness and operational requirements.
4. Benchmark when multiple candidates remain plausible.

**Why this works**

Module 2.7 teaches that database-access methods solve different problems.

**Common mistake**

Standardizing every database operation on one abstraction regardless of workload.

---

## Q38. ADBC, Arrow, COPY, and Row-Based Extraction

**Difficulty:** Advanced

**Problem**

A platform team wants one extraction path for both:

- row-level Python processing,
- Arrow-native processing into Parquet.

Compare named cursors, `COPY TO STDOUT`, and ADBC/Arrow extraction. Include the representation moving across the boundary and the major trade-offs.

**Solution**

A useful comparison is:

| Dimension | Named cursor | COPY TO STDOUT | ADBC / Arrow |
|---|---|---|---|
| Main representation | Driver row objects | COPY stream | Arrow RecordBatch/Table |
| Row-level Python logic | Direct | Less direct depending on format | Possible through Arrow conversion |
| Bulk file movement | Good | Natural fit | Natural fit |
| Arrow interoperability | Requires conversion | Requires conversion depending on path | Native-oriented |
| PostgreSQL-specific control | Strong | Strong | Driver dependent |
| Restartability | Additional design required | Additional design required | Additional design required |
| Performance | Workload-dependent | Workload-dependent | Workload-dependent |

The correct choice depends on where transformation occurs, output format, and measured performance.

**How to solve it**

1. Ask what representation the next stage wants.
2. Ask whether Python needs ordinary row objects.
3. Identify conversion boundaries.
4. Measure time and memory on the actual workload.

**Why this works**

Arrow-native movement may reduce conversion boundaries, but that does not imply automatic speedups for every workload.

**Common mistake**

Assuming the most modern-looking interface must be fastest.

---

## Q39. Advanced psycopg Capability Assessment

**Difficulty:** Advanced

**Problem**

A legacy codebase uses psycopg2. A new platform is adopting psycopg 3 and wants to understand several advanced capabilities without turning this into a full async or messaging module.

Explain the production significance of:

- prepared statements,
- pipeline mode,
- binary vs text transfer,
- custom adapters,
- `LISTEN` / `NOTIFY`,
- `AsyncConnection`,
- psycopg2 compatibility concerns.

**Solution**

These features are related to the driver boundary but solve different problems:

- **Prepared statements:** can reduce repeated parse/plan overhead for suitable workloads, but introduce lifecycle/pooler compatibility considerations.
- **Pipeline mode:** allows multiple operations to reduce network round trips; it changes how command/result flow is handled and requires careful transaction/error reasoning.
- **Binary vs text transfer:** changes representation and type/serialization behavior across the driver boundary.
- **Custom adapters:** allow advanced control when built-in Python/PostgreSQL type adaptation is insufficient.
- **LISTEN / NOTIFY:** provides PostgreSQL session-level notification behavior; pooling mode can matter because session affinity matters.
- **AsyncConnection:** provides asynchronous driver APIs for asyncio applications; detailed async design is outside this module.
- **psycopg2:** is a legacy interface still encountered in production; migration planning must account for API differences rather than assuming psycopg 3 is a drop-in textual rename.

**How to solve it**

1. Classify each feature by the problem it solves.
2. Identify whether it changes connection/session behavior.
3. Check compatibility with pools or poolers.
4. Verify actual driver-version documentation before adopting advanced features.

**Why this works**

A senior engineer evaluates advanced driver features in the context of workload, lifecycle, compatibility, and operational behavior.

**Common mistake**

Enabling every advanced driver feature without defining the actual bottleneck or compatibility requirement.

---

## Q40. Design the Production PostgreSQL → Parquet → Warehouse Sync

**Difficulty:** Advanced

**Problem**

Design a production-oriented Module 2.7 pipeline with these requirements:

- PostgreSQL source,
- tens of millions of rows,
- extract to Parquet,
- bounded Python memory,
- resumability after failure,
- validation before publication,
- read replica available,
- warehouse load after extraction,
- audit metadata,
- safe retries.

Your design must use only concepts taught in Module 2.7.

**Solution**

A coherent design is:

```text
PostgreSQL primary
      ↓
read replica when freshness/lag requirements allow
      ↓
bounded extraction
      ↓
named cursor / COPY / ADBC selected by workload benchmark
      ↓
Arrow batches where useful
      ↓
ParquetWriter
      ↓
temporary output
      ↓
row-count + key reconciliation
      ↓
atomic publication
      ↓
warehouse staging/load path
      ↓
target merge/upsert
      ↓
audit record
```

The decision logic should be explicit:

### Source protection

Use a read replica when its lag and resource profile are acceptable for the freshness requirement.

### Extraction

For row-oriented Python transformation, a named cursor is a natural candidate. For bulk stream movement, COPY TO STDOUT is a candidate. For Arrow-first processing, ADBC is a candidate. Benchmark alternatives instead of assuming one universal winner.

### Resumability

For recurring or failure-sensitive extracts, use keyset pagination such as `(updated_at, id)` with a checkpoint saved after the corresponding output batch has succeeded.

### Output safety

Never treat a partially written final filename as success. Write to a temporary path, validate, then atomically rename.

### Correctness

Use:

```text
row count
+
key-level reconciliation
+
checkpoint continuity
+
file validation
```

A consistent snapshot may be required when several related tables must represent the same point in time.

### Reliability

Retry at the correct unit:

- retry the whole transaction after retryable transaction failures,
- make target operations idempotent,
- treat unknown commit outcomes as potentially ambiguous,
- reconcile after recovery.

### Observability

Record at least:

```text
extract_id
table_name
started_at
finished_at
rows_expected
rows_written
status
last_checkpoint
output_path
error_message
```

Measure:

```text
rows/sec
elapsed time
peak memory
query duration
connection duration
output bytes
retry count
```

**How to solve it**

1. Characterize the extraction workload.
2. Choose primary vs replica based on freshness and source protection.
3. Choose the extraction mechanism based on row processing, bulk output, or Arrow interoperability.
4. Define a bounded-memory batch boundary.
5. Define the checkpoint semantics before implementation.
6. Design temporary output and atomic publication.
7. Define reconciliation and correctness proofs.
8. Define retry/idempotency behavior.
9. Add audit and operational metrics.
10. Benchmark the final candidate design on representative data.

**Why this works**

A production extraction is not simply “read rows in chunks.” It is:

```text
source execution
+
controlled transfer
+
bounded memory
+
correctness
+
recovery
+
safe publication
+
observability
```

The design uses the Module 2.7 concepts as one coherent database-access system.

**Common mistake**

Optimizing only rows/sec while ignoring source impact, correctness, restartability, and incomplete output.

---

# Final Module Review

Use the 40 questions as a final Module 2.7 assessment.

Before considering the module complete, you should be able to explain and implement the full progression:

```text
DB-API
   ↓
psycopg
   ↓
parameterized queries
   ↓
transactions
   ↓
pooling
   ↓
SQLAlchemy Core
   ↓
SQLAlchemy ORM
   ↓
Alembic
   ↓
bulk loading
   ↓
large-result streaming
```

## Final Self-Check

- [ ] I can explain connection vs cursor and the DB-API contract.
- [ ] I can use psycopg 3 safely and understand Python/PostgreSQL type adaptation.
- [ ] I can prevent SQL injection for values and safely compose dynamic identifiers.
- [ ] I can reason about transaction state, savepoints, isolation, retries, and idempotency.
- [ ] I can size and monitor a connection pool across processes.
- [ ] I can explain PgBouncer pooling-mode trade-offs.
- [ ] I can use SQLAlchemy Core without forgetting what the database is doing.
- [ ] I can recognize when ORM is useful and when object materialization becomes a liability.
- [ ] I can diagnose N+1 and measure the effect of eager loading.
- [ ] I can create and safely review Alembic migrations.
- [ ] I can design large-table migrations around lock risk and staged rollout.
- [ ] I can use COPY and staging for high-volume loads.
- [ ] I can make bulk loads idempotent and observable.
- [ ] I can diagnose bad COPY data and quarantine failures.
- [ ] I can distinguish `fetchmany()` from true server-side streaming.
- [ ] I can use named cursors for bounded-memory extraction.
- [ ] I can stream extraction into Parquet using explicit Arrow schemas.
- [ ] I can design atomic output publication.
- [ ] I can make large extraction resumable with keyset checkpoints.
- [ ] I can reason about consistent snapshots and long-running reads.
- [ ] I can compare named cursor, COPY TO STDOUT, and ADBC/Arrow paths.
- [ ] I can design fair benchmarks without inventing results.
- [ ] I can design a production database-access workflow with correctness, recovery, observability, and source protection.

# Topic Coverage Map

| Topic | Covered by |
|---|---|
| Topic 01 — DB-API / PEP 249 | Q1, Q2, Q4, Q10, Q12 |
| Topic 02 — PostgreSQL with psycopg | Q3, Q9, Q13, Q21, Q39 |
| Topic 03 — Parameterized Queries / SQL Injection | Q1, Q11, Q17, Q23, Q39 |
| Topic 04 — Transaction Control | Q4, Q12, Q21, Q31, Q35 |
| Topic 05 — Connection Pooling | Q5, Q14, Q22, Q32, Q39 |
| Topic 06 — SQLAlchemy Core | Q6, Q15, Q23, Q37, Q40 |
| Topic 07 — SQLAlchemy ORM | Q7, Q15, Q24, Q37 |
| Topic 08 — Alembic | Q8, Q16, Q25, Q33, Q37 |
| Topic 09 — Bulk Loading | Q9, Q17, Q18, Q20, Q26, Q37, Q40 |
| Topic 10 — Server-Side Cursors / Streaming | Q2, Q10, Q19, Q27, Q28, Q29, Q30, Q34, Q35, Q36, Q38, Q40 |

## Final Practice Principle

The point of this question set is not to memorize one database-access tool as universally best.

For each production scenario, reason through:

```text
Workload
   ↓
Correctness requirements
   ↓
Database/driver behavior
   ↓
Resource limits
   ↓
Failure modes
   ↓
Recovery strategy
   ↓
Measurement
   ↓
Production design
```

A strong Module 2.7 result is the ability to explain not only **what code to write**, but also:

- what Python is doing,
- what the driver is doing,
- what PostgreSQL is doing,
- what happens on failure,
- how memory behaves,
- how connections are consumed,
- how correctness is proven,
- and how the system behaves when the workload becomes large.
