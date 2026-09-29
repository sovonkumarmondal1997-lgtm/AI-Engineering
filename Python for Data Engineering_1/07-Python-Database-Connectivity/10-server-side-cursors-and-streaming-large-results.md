# Server-Side Cursors and Streaming Large Results

## Learning Objectives

By the end of this module, you should be able to:

- explain why `fetchall()` is risky for very large PostgreSQL results;
- distinguish client-side buffering, application-level batching, and database-side streaming;
- implement a psycopg 3 named/server-side cursor with bounded application memory;
- explain `itersize`, `fetchmany()`, transaction lifetime, and `withhold=True`;
- use SQLAlchemy 2.x streaming options deliberately;
- explain why pandas `read_sql(..., chunksize=...)` is not itself a proof of database-side streaming;
- use `COPY (query) TO STDOUT` for bulk serialized extraction;
- stream large results into CSV and Parquet;
- write Parquet incrementally with `ParquetWriter` and an explicit Arrow schema;
- monitor long-running reads with `pg_stat_activity`;
- use statement timeouts and evaluate read-replica placement;
- design keyset-based resumability using `(updated_at, id)` where appropriate;
- explain why `OFFSET` is not a reliable restart position for changing data;
- extract related tables from a consistent `REPEATABLE READ` snapshot;
- understand ADBC and Arrow-native record-batch extraction;
- recover safely from network/process failures;
- publish output only after validation and reconciliation;
- benchmark time, peak memory, rows/sec, and output size fairly;
- defend an extraction architecture using workload, correctness, source-impact, and operational evidence.

The central outcome is:

> The objective is not merely to “read rows in chunks.” The objective is to move a very large database result through a bounded-memory, restartable, observable, correctness-preserving pipeline.

## Prerequisites

This is Topic 10, the final topic of Module 2.7 — Python Database Connectivity. It assumes completion of:

- Topic 01 — DB-API (PEP 249): connections and cursors
- Topic 02 — PostgreSQL from Python with psycopg
- Topic 03 — Parameterized Queries and SQL Injection
- Topic 04 — Transaction Control from Python
- Topic 05 — Connection Pooling
- Topic 06 — SQLAlchemy Core: Engine and Metadata
- Topic 07 — SQLAlchemy ORM: When to Use and Avoid
- Topic 08 — Schema Migrations with Alembic
- Topic 09 — Bulk Loading with COPY and executemany

You should already understand:

- Python context managers and iterators;
- psycopg 3 connection/cursor usage;
- transactions and isolation;
- SQLAlchemy 2.x Core;
- PostgreSQL `COPY`;
- Arrow/Parquet and `ParquetWriter`;
- keyset-pagination concepts.

Do not re-teach those topics in depth.

> Topic 09 taught moving large amounts of data **into** PostgreSQL. Topic 10 teaches the opposite direction: extracting large PostgreSQL results **out of** the database while keeping Python memory bounded.

---

## Why Large Extraction Is a Data Engineering Problem

The dangerous starting point is familiar:

```python
rows = cursor.fetchall()
```

For a result containing 1 million, 10 million, or 20 million rows, this can create a large client-side memory footprint. The actual amount depends on column types, row width, driver representation, Python object overhead, and conversion buffers. There is no universal “X bytes per row” multiplier that is safe to memorize.

A production extraction must reason about:

```text
result buffering
+
cursor type
+
transaction lifetime
+
batch size
+
memory
+
database snapshot
+
query duration
+
network failures
+
resume strategy
+
output atomicity
+
reconciliation
```

The mental shift is:

```text
small query
→ “How do I fetch it?”

large extraction
→ “Where does every part of the result live,
   how long does it live there,
   and what happens if something fails?”
```

The extractor crosses three boundaries:

1. **PostgreSQL execution** — query work, snapshots, server resources.
2. **Driver/application transfer** — buffering and row representation.
3. **Output publication** — temporary state, validation, checkpointing, and final visibility.

---

## The Core Mental Model

```text
Large source table
      ↓
database-side execution
      ↓
controlled result transfer
      ↓
bounded Python batches
      ↓
Parquet / CSV output
      ↓
validation + reconciliation
      ↓
atomic completion
```

Keep this model visible while learning every mechanism below.

## 1. The Naive Extraction Pattern

```python
import psycopg

with psycopg.connect() as conn:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, updated_at, amount
            FROM orders
            ORDER BY id
        """)
        rows = cur.fetchall()

        for row in rows:
            process(row)
```

⚠️ **INTENTIONALLY INEFFICIENT / DANGEROUS TRAINING EXAMPLE**

The problem is the complete result collection:

```text
SELECT huge result
    ↓
client-side result handling
    ↓
large result representation
    ↓
Python list + row objects
    ↓
processing
```

A safer architecture changes the transfer pattern:

```text
SELECT
    ↓
controlled retrieval
    ↓
batch
    ↓
process/write
    ↓
release batch
    ↓
next batch
```

## 2. Client-Side Cursors

A normal psycopg cursor created with:

```python
cur = conn.cursor()
```

uses the ordinary client-side result path.

The important concept is not that “PostgreSQL always sends every byte before `execute()` returns” — internal behavior depends on the driver and protocol. The production-safe lesson is more precise:

> A normal/client-side cursor is not the mechanism to rely on when you need a guarantee that a huge result will remain server-side and be transferred only in controlled portions.

Psycopg documents server-side cursors as a distinct cursor type for partial retrieval of large datasets. This is why cursor choice is architectural.

Think:

```text
client-side cursor
=
normal result path
```

versus:

```text
server-side cursor
=
server-managed result state
+
controlled FETCH operations
```

## 3. Why `fetchmany()` Does Not Automatically Solve the Problem

This looks memory-safe:

```python
cur.execute("SELECT id, amount FROM orders")

while True:
    batch = cur.fetchmany(10_000)
    if not batch:
        break

    process(batch)
```

But the application only controls how many rows it consumes from the cursor at a time. It has not proved that the underlying client-side result path did not already buffer a large amount of the result.

Therefore:

```text
fetchmany()
≠
guaranteed server-side streaming
```

This distinction is foundational:

```text
application-level batching
=
how much the application processes together
```

versus:

```text
database-side streaming
=
how the result is retained/transferred between
PostgreSQL and the client
```

A useful experiment is:

```text
normal cursor + fetchmany()
vs
named cursor + fetchmany()
```

and then measure peak process memory. The purpose is to verify the actual stack, not memorize a claim.

## 4. Server-Side / Named Cursors

Psycopg creates a server-side cursor when the cursor has a name:

```python
with conn.cursor(name="extract") as cur:
    cur.execute("""
        SELECT id, updated_at, amount
        FROM orders
        ORDER BY id
    """)

    for row in cur:
        process(row)
```

For explicit batches:

```python
with conn.cursor(name="extract") as cur:
    cur.execute("""
        SELECT id, updated_at, amount
        FROM orders
        ORDER BY id
    """)

    while True:
        batch = cur.fetchmany(10_000)
        if not batch:
            break
        process(batch)
```

Conceptually:

```text
Python
  ↓
named cursor
  ↓
PostgreSQL server-side cursor state
  ↓
FETCH N
  ↓
Python receives N rows
  ↓
process
  ↓
FETCH N
  ↓
...
```

A named cursor reduces Python-side result materialization because the server-side cursor can retrieve portions rather than exposing one giant client-side result.

It does **not** mean “zero memory anywhere.” PostgreSQL still has to maintain cursor/query state and may consume server resources.

## 5. Named Cursor Internal Model

A useful ownership model is:

```text
Python owns:
    current batch
    transformed batch
    output buffers
    application state

PostgreSQL owns:
    cursor state
    execution state
    server-side resources needed by the query
```

Do not teach:

> “The complete result is always stored in server RAM.”

That is too strong. Sorts, hashes, plans, temporary relations, and cursor execution can use different resources depending on the query.

The reliable distinction is:

```text
client-side cursor
→ normal client result path

named/server-side cursor
→ PostgreSQL-side cursor state
→ partial FETCH operations
→ bounded client transfer
```

This is the behavior that matters to extraction design.

## 6. Bounded Memory

Define bounded memory as:

> Peak application memory should remain approximately stable as source table size increases, assuming fixed batch size and comparable row width.

For example:

```text
1M rows
10M rows
100M rows

source size ↑↑↑

fixed batch size
       ↓
active Python batch ≈ fixed
       ↓
peak application memory remains controlled
```

This is not a mathematical guarantee of perfectly constant memory.

Actual usage can vary with:

- batch size;
- row width;
- Python objects;
- Arrow/native allocations;
- temporary conversion buffers;
- Parquet compression/writer buffers;
- unusually large individual values.

This defeats bounded memory:

```python
all_batches = []

while batch := cur.fetchmany(10_000):
    all_batches.append(batch)
```

Even if each batch is small, retaining every batch makes total memory grow with source size.

## 7. Iterating Named Cursors

Named cursors can be iterated directly:

```python
from psycopg.rows import dict_row

with psycopg.connect(conninfo) as conn:
    with conn.cursor(
        name="extract",
        row_factory=dict_row,
    ) as cur:
        cur.execute("""
            SELECT id, updated_at, amount
            FROM orders
            ORDER BY updated_at, id
        """)

        for row in cur:
            process(row)
```

If the downstream operation naturally works on batches, explicit fetching is clearer:

```python
with conn.cursor(name="extract", row_factory=dict_row) as cur:
    cur.execute("""
        SELECT id, updated_at, amount
        FROM orders
        ORDER BY updated_at, id
    """)

    while batch := cur.fetchmany(10_000):
        process_batch(batch)
```

Batch-oriented processing is useful for:

- Arrow conversion;
- Parquet row groups;
- progress metrics;
- checkpoint boundaries;
- controlled transformations.

Always close the named cursor. Server-side cursor cleanup releases server-associated resources.

## 8. `itersize`

`itersize` controls how many records psycopg retrieves in a batch when iterating over a server-side cursor with:

```python
for row in cur:
    ...
```

Example:

```python
with conn.cursor(name="extract") as cur:
    cur.itersize = 5_000
    cur.execute("""
        SELECT id, amount
        FROM orders
        ORDER BY id
    """)

    for row in cur:
        process(row)
```

The distinction is:

```text
iteration
→ itersize controls internal retrieval batch
```

while:

```python
cur.fetchmany(5_000)
```

explicitly requests a fetch size.

Changing `itersize` changes a trade-off among:

```text
fewer round trips
vs
larger per-fetch memory
vs
larger processing bursts
```

Do not treat any single value as universally optimal. The correct value is workload-dependent.

## 9. Batch Size Trade-Offs

The basic trade-off is:

```text
tiny batch
→ lower active-batch memory
→ more fetch calls / round trips
→ more coordination overhead

large batch
→ fewer fetch calls
→ more network/protocol amortization
→ larger memory bursts
→ larger conversion/write bursts
```

Batch size also affects:

- Python object creation;
- Arrow conversion;
- Parquet row-group size;
- disk write behavior;
- logging frequency;
- checkpoint granularity.

A useful measurement table is:

| Batch size | Peak memory | Fetch time | Conversion time | Write time | Rows/sec |
| --- | ---: | ---: | ---: | ---: | ---: |
| measured | measured | measured | measured | measured | measured |
| measured | measured | measured | measured | measured | measured |
| measured | measured | measured | measured | measured | measured |

Do not put an invented “recommended” value in production code. Measure against the actual row width and memory budget.

## 10. Named Cursors and Transactions

Ordinary named cursors are normally tied to transaction lifetime.

The lifecycle is:

```text
BEGIN
  ↓
DECLARE / open cursor
  ↓
FETCH batches
  ↓
process
  ↓
COMMIT / ROLLBACK
  ↓
cursor lifecycle ends
```

Use a deliberate transaction boundary:

```python
with psycopg.connect(conninfo) as conn:
    with conn.cursor(name="extract") as cur:
        cur.execute("""
            SELECT id, amount
            FROM orders
            ORDER BY id
        """)

        while batch := cur.fetchmany(10_000):
            process(batch)
```

The important production consequence is:

> The extraction may keep a transaction and its snapshot alive for the duration of the cursor.

This is why a four-hour cursor is not merely a four-hour Python loop. It can be a four-hour database transaction.

## 11. `withhold=True`

`withhold=True` creates a named cursor that can survive a successful commit:

```python
with conn.cursor(
    name="extract",
    withhold=True,
) as cur:
    ...
```

Conceptually:

```text
WITHOUT HOLD
transaction
    ↓
cursor
    ↓
COMMIT
    ↓
cursor ends

WITH HOLD
transaction
    ↓
cursor
    ↓
COMMIT
    ↓
cursor may remain usable
```

The feature exists for a specific lifecycle requirement:

> “I need the server-side cursor to remain usable after commit.”

It is not a generic “better streaming” switch.

Use it only when the longer cursor/resource lifetime is intentional.

## 12. Long-Running Reads

A long-running read can keep an old snapshot alive.

PostgreSQL MVCC uses snapshots to determine row visibility. If a transaction remains open while an extractor slowly processes rows, older row versions may remain relevant to that snapshot for longer.

The accurate production concern is:

```text
long-running transaction
→ old snapshot remains relevant
→ cleanup of versions visible to that snapshot may be delayed
→ source database maintenance/resource pressure can increase
```

Do not simplify this to:

> “Any long query blocks VACUUM.”

The actual effect depends on transaction/snapshot state and what row versions VACUUM is trying to remove.

Monitor the source, especially:

- transaction age;
- `xact_start`;
- `query_start`;
- `backend_xmin` when relevant;
- wait events;
- table growth/cleanup pressure.

## 13. Observing Long-Running Extractions

Identify the extractor with `application_name` and inspect it:

```sql
SELECT
    pid,
    application_name,
    state,
    xact_start,
    query_start,
    wait_event_type,
    wait_event,
    query
FROM pg_stat_activity
WHERE application_name = 'large_extract';
```

Useful interpretations:

| Field | What to investigate |
| --- | --- |
| `state` | `active`, `idle`, or `idle in transaction` |
| `xact_start` | How old is the transaction? |
| `query_start` | How long has the current/last query been running? |
| `wait_event_type` | Is the server waiting? |
| `wait_event` | What category of wait is occurring? |

Useful operational questions:

```text
Is the database still executing?
Is the extractor stuck in Python?
Is the connection idle in transaction?
Has the transaction become unusually old?
Is the process still advancing rows?
```

Use a stable application name:

```text
large_extract
```

and keep per-run identifiers in structured logs.

## 14. Extraction Roles and Statement Timeouts

A dedicated extraction role/session should use a deliberate statement-timeout policy.

Conceptual connection configuration:

```python
with psycopg.connect(
    conninfo,
    options=(
        "-c application_name=large_extract "
        "-c statement_timeout=1800000"
    ),
) as conn:
    run_extract(conn)
```

Or use a transaction-local setting:

```python
with conn.transaction():
    conn.execute("SET LOCAL statement_timeout = '30min'")
    run_extract(conn)
```

A timeout is a safety control:

```text
unbounded server operation
→
controlled failure boundary
```

Do not confuse:

```text
statement_timeout
```

with:

```text
entire extraction job timeout
```

A large extraction can consist of multiple database operations. The application may also need an overall wall-clock deadline.

Too aggressive:

```text
healthy large extraction
→ timeout
→ unnecessary restart
```

Too permissive:

```text
pathological query
→ source resources consumed for too long
```

Choose from measured query behavior and source protection requirements.

## 15. Read Replicas

A read replica can move some heavy extraction reads away from the primary:

```text
Primary
   ↓ replication
Read replica
   ↓
large extraction
```

Potential benefits:

- less direct contention on the primary;
- isolated read capacity;
- a natural place for some analytical reads.

Important limitations:

- replication lag;
- older snapshots/data;
- replica CPU/I/O limits;
- hot-standby query/recovery conflicts;
- failover/switchover behavior.

A replica can protect the primary from some direct extraction load, but it does not make the workload free.

Use:

```text
primary
→ freshness
→ shared source capacity

replica
→ some read isolation
→ possible staleness
```

The correct choice depends on freshness and source-impact requirements.

## 16. SQLAlchemy Streaming

SQLAlchemy 2.x exposes streaming behavior through execution options:

```python
stmt = select(
    orders.c.id,
    orders.c.updated_at,
    orders.c.amount,
)

with engine.connect() as conn:
    result = (
        conn.execution_options(
            stream_results=True,
        )
        .execute(stmt)
    )

    for row in result:
        process(row)
```

A fixed buffer can be expressed with:

```python
with engine.connect() as conn:
    result = (
        conn.execution_options(
            stream_results=True,
            yield_per=10_000,
        )
        .execute(stmt)
    )

    for row in result:
        process(row)
```

The stack is:

```text
SQLAlchemy
    ↓
dialect
    ↓
DBAPI driver
    ↓
PostgreSQL
```

`stream_results=True` requests a streaming/server-side result strategy where the backend supports it.

The abstraction does not erase backend/driver differences. Always verify the actual database/driver path.

## 17. `yield_per`

`yield_per` provides a fixed-size buffering strategy for result consumption.

Example:

```python
with engine.connect() as conn:
    result = (
        conn.execution_options(
            yield_per=10_000,
        )
        .execute(stmt)
    )

    for row in result:
        process(row)
```

For batch-oriented consumption:

```python
with engine.connect() as conn:
    result = (
        conn.execution_options(
            yield_per=10_000,
        )
        .execute(stmt)
    )

    for partition in result.partitions():
        process_partition(partition)
```

A crucial anti-pattern is:

```python
result = conn.execution_options(
    yield_per=10_000
).execute(stmt)

rows = result.all()
```

Calling `.all()` asks for the result as a whole and can defeat the intended bounded consumption pattern.

In ORM work, `yield_per` also controls object construction and has compatibility constraints with some eager-loading strategies. Large extraction often does not need ORM identity/relationship machinery.

## 18. SQLAlchemy Streaming Internal Model

Use this model:

```text
SQLAlchemy
    ↓
stream_results / yield_per
    ↓
dialect
    ↓
driver result strategy
    ↓
server-side cursor if supported
    ↓
PostgreSQL
```

Therefore code review must ask:

- Which backend?
- Which driver?
- Does that dialect use server-side cursors?
- Is the result consumed incrementally?
- Is application code retaining old rows?
- Is ORM object creation adding memory pressure?

Streaming is a property of the end-to-end result path, not merely the presence of an execution option.

## 19. pandas `read_sql(..., chunksize=...)`

Pandas supports:

```python
for chunk in pd.read_sql(
    query,
    engine,
    chunksize=10_000,
):
    process(chunk)
```

This provides chunked DataFrame consumption.

The critical caveat is:

> `chunksize` does not, by itself, guarantee database-side streaming.

The stack remains:

```text
pandas
  ↓
SQLAlchemy
  ↓
driver
  ↓
PostgreSQL
```

If a lower layer buffers a large result, pandas can still experience high memory usage.

The correct mental model is:

```text
chunksize
=
pandas/DataFrame chunking
```

not automatically:

```text
chunksize
=
server-side streaming
```

For strict memory requirements, configure the lower-level streaming path deliberately and measure it.

## 20. pandas Streaming Experiment

Run three cases against the same query.

### Case A — ordinary read

```python
df = pd.read_sql(
    query,
    engine,
)
consume(df)
```

### Case B — pandas chunks

```python
for df in pd.read_sql(
    query,
    engine,
    chunksize=10_000,
):
    consume(df)
```

### Case C — streaming configured underneath

```python
with engine.connect().execution_options(
    yield_per=10_000,
) as conn:
    for df in pd.read_sql(
        query,
        conn,
        chunksize=10_000,
    ):
        consume(df)
```

Measure:

```text
elapsed time
peak Python memory
process RSS where available
rows processed
```

The experiment should answer:

```text
Did DataFrame chunking reduce memory?
Did the driver stream?
Was DataFrame construction the bottleneck?
Did yield_per change observed behavior?
```

Use measurements, not assumptions.

## 21. COPY TO STDOUT

PostgreSQL supports copying a query result:

```sql
COPY (
    SELECT id, updated_at, amount
    FROM orders
    ORDER BY id
)
TO STDOUT
WITH (FORMAT CSV, HEADER TRUE);
```

Psycopg exposes COPY through:

```python
with conn.cursor() as cur:
    with cur.copy("""
        COPY (
            SELECT id, updated_at, amount
            FROM orders
        ) TO STDOUT
        WITH (FORMAT CSV, HEADER TRUE)
    """) as copy:
        for block in copy:
            output.write(block)
```

This is a bulk serialized transfer path.

Conceptually:

```text
query
 ↓
COPY protocol
 ↓
PostgreSQL serializes result
 ↓
psycopg receives stream blocks
 ↓
file / downstream processing
```

It can reduce normal row-object materialization because the output is transferred in COPY representation.

Do not claim it is always faster than a named cursor. If Python must transform each row, the named-cursor path may be easier to work with. Benchmark the complete pipeline.

## 22. COPY TO STDOUT vs Named Cursor

| Dimension | Named Cursor | COPY TO STDOUT |
| --- | --- | --- |
| Data representation | Driver-adapted rows | COPY-serialized stream |
| Python row objects | Yes, per fetched batch | Can be reduced |
| Row-level transformation | Direct | Less direct |
| Bulk file output | Good fit | Strong fit |
| Restartability | Additional design | Additional design |
| PostgreSQL-specific control | Strong | Strong |
| Performance | Workload-dependent | Workload-dependent |

The table is descriptive, not a ranking.

Ask:

```text
Do I need Python to inspect/transform rows?
or
Do I mainly need high-volume serialized movement?
```

That is often the first architecture fork.

## 23. Streaming to CSV

A direct CSV path can stream COPY bytes into a temporary file:

```python
from pathlib import Path
import os

def copy_query_to_csv(conn, copy_sql: str, path: Path) -> None:
    temp = path.with_name(path.name + ".tmp")

    try:
        with temp.open("wb") as output:
            with conn.cursor() as cur:
                with cur.copy(copy_sql) as copy:
                    for block in copy:
                        output.write(block)

            output.flush()
            os.fsync(output.fileno())

        os.replace(temp, path)

    except Exception:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass
        raise
```

The `copy_sql` must be trusted/approved SQL. Do not interpolate untrusted input into a `COPY` query.

Important CSV semantics include:

- encoding;
- delimiter;
- quote and escape behavior;
- embedded newlines;
- NULL representation;
- header handling.

For direct movement, keeping PostgreSQL's COPY serialization intact avoids an unnecessary parse-and-reserialize step.

## 24. Streaming to Parquet

The canonical architecture is:

```text
PostgreSQL
    ↓
named cursor / COPY / ADBC
    ↓
bounded batch
    ↓
Arrow arrays/table
    ↓
ParquetWriter
    ↓
temporary file
    ↓
validation
    ↓
atomic publication
```

Parquet is a natural analytical destination because it supports typed, columnar storage and can carry an explicit schema.

A streaming writer should never do:

```python
all_rows = cursor.fetchall()
table = pa.Table.from_pylist(all_rows)
pq.write_table(table, path)
```

Instead:

```text
one batch
→ Arrow conversion
→ write one row group/batch
→ release references
→ next batch
```

This keeps memory associated with active batches rather than the total result.

## 25. Explicit Arrow Schema

Use an explicit Arrow schema:

```python
import pyarrow as pa

schema = pa.schema([
    pa.field("id", pa.int64(), nullable=False),
    pa.field(
        "updated_at",
        pa.timestamp("us", tz="UTC"),
        nullable=False,
    ),
    pa.field(
        "amount",
        pa.decimal128(18, 2),
        nullable=True,
    ),
])
```

Then:

```python
table = pa.Table.from_pylist(
    batch,
    schema=schema,
)
```

The schema matters because it provides:

- stable types across batches;
- a defined representation for timestamps;
- deliberate Decimal precision/scale;
- predictable downstream contracts;
- valid schema even for an empty result.

Without an explicit schema, inference can depend on which values happen to appear in the batch.

## 26. Named Cursor → ParquetWriter

A focused implementation:

```python
from __future__ import annotations

import os
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from psycopg.rows import dict_row


def extract_table_to_parquet(
    conn,
    query: str,
    path: Path,
    batch_size: int,
    arrow_schema: pa.Schema,
) -> int:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")

    path = Path(path)
    temp_path = path.with_name(path.name + ".tmp")

    writer = None
    rows_written = 0

    try:
        with conn.cursor(
            name="extract",
            row_factory=dict_row,
        ) as cur:
            cur.itersize = batch_size
            cur.execute(query)

            writer = pq.ParquetWriter(
                temp_path,
                arrow_schema,
            )

            while True:
                batch = cur.fetchmany(batch_size)
                if not batch:
                    break

                arrow_batch = pa.Table.from_pylist(
                    batch,
                    schema=arrow_schema,
                )
                writer.write_table(arrow_batch)
                rows_written += len(batch)

            writer.close()
            writer = None

        with temp_path.open("ab") as f:
            f.flush()
            os.fsync(f.fileno())

        # Validate before publishing in a real implementation.
        os.replace(temp_path, path)

        return rows_written

    except Exception:
        if writer is not None:
            try:
                writer.close()
            except Exception:
                pass

        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass

        raise
```

The important components are:

```text
named cursor
+
fixed batch
+
explicit schema
+
ParquetWriter
+
temporary path
+
cleanup
+
atomic publication
```

This is a production-oriented teaching pattern, not a complete reusable library. Source count reconciliation, structured logging, query timeout, and safe run metadata should be layered around it.

## 27. Atomic Output Files

Writing directly to:

```text
orders.parquet
```

is risky.

A crash can leave a file that exists but is incomplete.

Use:

```text
orders.parquet.tmp
      ↓
complete extraction
      ↓
close writer
      ↓
validate
      ↓
atomic rename
      ↓
orders.parquet
```

For a same-filesystem local file, `os.replace()` provides atomic replacement semantics.

The memorable rule is:

> The final filename is a success/publication signal.

A temp file means:

```text
work in progress
```

A published final path means:

```text
the output passed the publication prerequisites
```

For object storage, rename semantics differ. The same invariant is implemented with temporary objects/prefixes plus an explicit completion/manifest state.

## 28. Partial File Detection

Never infer extraction success from:

```text
file exists
```

Use multiple signals:

- temp-file convention;
- successful writer finalization;
- schema validation;
- file readability;
- expected row count;
- source reconciliation;
- key-level checks where feasible;
- successful publication transition.

For Parquet, a correctly closed writer finalizes the file structure/footer. A crash before finalization should make the temp state ineligible for publication.

A good lifecycle is:

```text
temp exists
→ work not published

temp closed + validated
→ candidate result

final path published
→ consumer-visible result
```

## 29. Row-Count Reconciliation

For a simple extract:

```sql
SELECT COUNT(*)
FROM orders;
```

Compare with:

```text
source_count
=
extracted_count
```

For filtered extraction, use the same filter semantics:

```sql
SELECT COUNT(*)
FROM orders
WHERE updated_at >= %s;
```

The count is only meaningful if it represents the same logical data boundary as the extraction.

For production, record:

```text
rows_expected
rows_written
```

and emit a mismatch as a failure unless the workload has an explicitly documented reason for approximate reconciliation.

Counts are important evidence, but not a complete proof.

## 30. Extract Query vs Count Query

Two correct queries can produce different results when the source changes:

```text
T0: extract SELECT
T1: source changes
T2: COUNT(*)
```

A count mismatch may therefore reflect different snapshots rather than an extraction bug.

For strong point-in-time reconciliation:

```text
BEGIN REPEATABLE READ
    ↓
snapshot S1
    ↓
extract
    ↓
COUNT(*) from S1
    ↓
COMMIT
```

For incremental designs, an equivalent logical boundary can be created using a watermark:

```text
source rows <= watermark
```

The key principle is:

> Reconciliation is only meaningful when source and output are compared against the same defined data boundary.

## 31. Resumable Extraction

Ask:

> What happens when a 4-hour extraction fails at 87%?

Restarting from zero is expensive. Restarting from an ambiguous position can silently lose data.

A resumable extractor records a checkpoint:

```text
last_updated_at
last_id
rows_extracted
checkpoint_time
status
```

The core sequence is:

```text
read batch
  ↓
write batch safely
  ↓
persist checkpoint
```

The checkpoint means:

> “The output is known to contain all source rows through this logical position.”

That is a stronger contract than:

```text
rows_seen = 12,000,000
```

## 32. Keyset Pagination

Use a stable composite ordering key where appropriate:

```sql
SELECT
    id,
    updated_at,
    amount
FROM orders
WHERE (updated_at, id) > (%s, %s)
ORDER BY updated_at, id
LIMIT %s;
```

The checkpoint is:

```text
(last_updated_at, last_id)
```

The extractor then makes progress:

```text
checkpoint N
    ↓
rows > checkpoint N
    ↓
write batch
    ↓
checkpoint N+1
```

The key must have deterministic ordering semantics.

Why two columns?

```text
updated_at
=
business/change ordering

id
=
tie-breaker
```

This is not universal. Mutable ordering columns, deletes, updates, and late changes can require additional data-boundary design.

## 33. Why Not OFFSET Pagination?

Consider:

```sql
SELECT ...
FROM orders
ORDER BY updated_at, id
LIMIT 10000
OFFSET 5000000;
```

`OFFSET` means:

> Skip the first 5,000,000 rows in the result as currently ordered.

It does not mean:

> Resume after the last row I successfully wrote.

If rows are inserted or deleted before the offset, the position can shift:

```text
batch 1
   ↓
source changes
   ↓
batch 2 using old offset
   ↓
position has moved
   ↓
rows can be repeated or skipped
```

Keyset pagination instead says:

```text
resume after known key
```

This is tied to data values rather than current row position.

## 34. Keyset Checkpoint Design

A simple checkpoint structure:

```text
last_updated_at
last_id
rows_extracted
updated_at
status
```

The safe order is:

```text
1. read checkpoint
2. query next batch
3. write batch
4. ensure output boundary is safe
5. persist checkpoint
6. continue
```

Never:

```text
checkpoint
  ↓
write batch
```

because a crash between the two operations can permanently skip data on restart.

Checkpoint values should be monotonic under the chosen ordering:

```text
checkpoint 1
   <
checkpoint 2
   <
checkpoint 3
```

If the control store supports atomic updates, use them to avoid conflicting writers.

## 35. Resumable Extraction Example

```python
def extract_incrementally(
    conn,
    last_updated_at,
    last_id,
    batch_size,
    upper_watermark,
):
    while True:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, updated_at, amount
                FROM orders
                WHERE updated_at <= %s
                  AND (updated_at, id) > (%s, %s)
                ORDER BY updated_at, id
                LIMIT %s
                """,
                (
                    upper_watermark,
                    last_updated_at,
                    last_id,
                    batch_size,
                ),
            )
            batch = cur.fetchall()

        if not batch:
            return

        write_batch_safely(batch)

        last_updated_at = batch[-1][1]
        last_id = batch[-1][0]

        persist_checkpoint(
            last_updated_at=last_updated_at,
            last_id=last_id,
        )
```

A useful improvement is to make the upper watermark part of the run contract. That prevents rows that change after the run begins from silently moving the run's goalpost.

The full architecture is:

```text
watermark
=
dataset boundary

checkpoint
=
progress inside that boundary
```

## 36. Resume Correctness

The required proof is:

```text
no missing rows
+
no duplicate rows
```

For a small controlled test:

```python
assert source_ids == output_ids
```

For a large dataset, do not blindly build a Python `set` containing every key. Possible scalable validation patterns include:

- database-side joins;
- sorted key streams;
- partitioned reconciliation;
- hashes/aggregates over deterministic partitions;
- duplicate-count checks.

A strong proof combines:

```text
row count
+
key-level evidence
+
checkpoint monotonicity
+
output validation
```

A count match alone is insufficient because:

```text
one missing row
+
one duplicate row
=
same count
```

## 37. Consistent Snapshots

For related-table extraction, ask:

> How do I guarantee the files represent a compatible point in time?

A `REPEATABLE READ` transaction provides a stable snapshot for the transaction's reads:

```text
BEGIN REPEATABLE READ
      ↓
snapshot S1
      ↓
customers
      ↓
orders
      ↓
payments
      ↓
COMMIT
```

Conceptually:

```python
with psycopg.connect(conninfo) as conn:
    with conn.transaction():
        conn.execute(
            "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ"
        )

        extract_table(conn, customers_query, customers_tmp)
        extract_table(conn, orders_query, orders_tmp)
        extract_table(conn, payments_query, payments_tmp)
```

This is a consistency tool, not a free optimization. The longer the transaction stays open, the longer its snapshot remains relevant.

## 38. Per-Table vs Shared Snapshot

### Separate extraction transactions

```text
A at S1
B at S2
C at S3
```

Pros:

- shorter transaction lifetimes;
- independent failures;
- potentially easier operational control.

Risk:

```text
A and B may describe different committed states
```

### Shared snapshot

```text
A ─┐
B ─┼→ S1
C ─┘
```

Pros:

- compatible point-in-time relationship.

Costs:

- longer transaction;
- longer snapshot lifetime;
- more source impact;
- more complex coordinated publication.

The decision is driven by the downstream correctness requirement.

## 39. ADBC / Arrow-Native Extraction

ADBC exposes Arrow-oriented result APIs.

Conceptually:

```text
PostgreSQL
    ↓
ADBC PostgreSQL driver
    ↓
Arrow RecordBatch / RecordBatchReader
    ↓
Parquet
```

Two concepts must be distinguished:

```python
cursor.fetch_arrow_table()
```

can represent the complete result as one Arrow Table.

For a huge result, that can still be a large memory operation.

A record-batch reader is more appropriate for streaming:

```python
cursor.execute("""
    SELECT id, updated_at, amount
    FROM orders
""")

reader = cursor.fetch_record_batch()

for batch in reader:
    write_arrow_batch(batch)
```

ADBC is attractive when Arrow is already the natural representation. The advantage is reduced conversion between row-oriented Python objects and columnar Arrow structures.

Do not assume ADBC is automatically faster. Driver settings, PostgreSQL execution, network, Arrow conversion, and Parquet writing still matter.

## 40. ADBC vs Named Cursor vs COPY

| Dimension | Named Cursor | COPY TO STDOUT | ADBC |
| --- | --- | --- | --- |
| Row-oriented processing | Strong fit | Less direct | Moderate / batch-oriented |
| Bulk file extraction | Good | Strong fit | Strong fit |
| Arrow interoperability | Convert rows to Arrow | Depends on output path | Native-oriented |
| Python row-object creation | Per batch | Reduced | Often reduced |
| Restartability | Additional design | Additional design | Additional design |
| Driver-specific behavior | Psycopg | Psycopg/PostgreSQL | ADBC driver-dependent |
| Performance | Workload-dependent | Workload-dependent | Workload-dependent |

Use the comparison to identify experiments, not winners.

## 41. Network Failure Mid-Stream

Imagine:

```text
10M rows
   ↓
6M written
   ↓
network failure
```

Potential states:

```text
database
→ cursor/transaction interrupted

Python
→ connection failed

temp file
→ partial

checkpoint
→ may still point to the prior safe batch

final output
→ must remain unpublished
```

Recovery should begin from the last known-good state.

For a single full-snapshot Parquet file:

```text
failure
→ discard incomplete temp
→ restart extraction
```

For a keyset design:

```text
failure
→ discard/reject partial current batch
→ resume after last valid checkpoint
```

The key is never to treat “bytes probably made it” as a durable correctness boundary.

## 42. Temporary Files + Atomic Finalization

Reusable pattern:

```text
write temp
   ↓
flush / close
   ↓
validate
   ↓
atomic publication
```

The output state machine is:

```text
working
   ↓
completed
   ↓
validated
   ↓
published
```

For local files:

```python
os.replace(temp_path, final_path)
```

Use the same filesystem when local atomic replacement semantics are required.

For multi-file extracts, use a logical publication marker/manifest so consumers know whether the complete set is available.

## 43. Extraction Failure State Machine

```text
START
  ↓
RUNNING
  ↓
WRITING TEMP
  ├──── failure ───→ FAILED / CLEANUP
  ↓
COMPLETED
  ↓
VALIDATED
  ↓
ATOMIC RENAME / COMMIT
  ↓
PUBLISHED
```

State meanings:

- **START** — validate configuration and destination.
- **RUNNING** — database work is active.
- **WRITING TEMP** — output is intentionally invisible to consumers.
- **FAILED / CLEANUP** — remove or quarantine unsafe temporary state.
- **COMPLETED** — extraction read all intended source rows.
- **VALIDATED** — schema, count, and required correctness checks passed.
- **PUBLISHED** — final output became consumer-visible.

Do not collapse “query finished” and “published successfully” into one status.

## 44. Empty / One Row / Large Table

### Empty table

Expected:

```text
0 rows
valid schema
valid output
```

Explicit schema is essential because there are no values from which to infer types.

### One row

Expected:

```text
one batch
one output row
valid schema
```

### Large table

Expected:

```text
many batches
controlled memory
correct count
valid output
```

These three cases expose different bugs:

- empty-batch assumptions;
- missing schema on zero rows;
- last-batch handling;
- incorrect row counts;
- checkpoint bugs.

## 45. 20-Million-Row Benchmark

Compare:

```text
A. client-side cursor
B. named cursor
C. COPY TO STDOUT
D. ADBC Arrow extraction
```

Measure:

```text
elapsed time
peak Python memory
process RSS where practical
rows/sec
output size
CPU where practical
connection duration
query duration
```

Do not fabricate results.

The benchmark answers:

```text
What happened on this machine,
with this query,
against this PostgreSQL instance,
using these library versions?
```

It does not prove a universal ranking.

## 46. Benchmark Predictions

Before running the test, predict:

| Question | Prediction |
| --- | --- |
| Which methods create Python row objects? | |
| Which methods should reduce client-side buffering? | |
| Where might serialization dominate? | |
| Where might network throughput dominate? | |
| Which method's natural output is serialized bytes? | |
| Which method's natural output is Arrow batches? | |

Then compare:

```text
prediction
vs
measurement
```

A surprising result is useful because it tells you which layer of your mental model was incomplete.

## 47. Fair Benchmark Rules

Keep constant:

- PostgreSQL instance;
- table/data;
- selected columns;
- filters;
- machine/container;
- Python version;
- driver versions;
- output target;
- filesystem/storage;
- warm-up procedure where appropriate.

Do not compare:

```text
method A → 3 narrow columns → Parquet
method B → 20 wide columns → CSV
```

and call it a transport benchmark.

Record:

```text
query
row count
columns
versions
batch size
output format
hardware/container limits
run timestamp
```

## 48. Peak Memory Measurement

Python's `tracemalloc` measures Python allocation activity:

```python
import tracemalloc

tracemalloc.start()

run_extraction()

current, peak = tracemalloc.get_traced_memory()
print("current:", current)
print("peak:", peak)

tracemalloc.stop()
```

On Linux/WSL, process-level RSS can also be observed with the standard library:

```python
import resource

usage = resource.getrusage(resource.RUSAGE_SELF)
print("max RSS:", usage.ru_maxrss)
```

Interpret them differently:

```text
tracemalloc
→ Python allocations

RSS
→ process memory footprint
```

Arrow/native buffers and native database-driver allocations may not appear as expected in `tracemalloc`.

No single memory number is a perfect accounting of every native byte.

## 49. Time Measurement

Use:

```python
from time import perf_counter

started = perf_counter()
run_extraction()
elapsed = perf_counter() - started
print(f"elapsed={elapsed:.3f}s")
```

For repeated experiments:

```text
warm up where appropriate
→ repeat
→ record every run
→ summarize consistently
```

Rows/sec:

```text
rows/sec
=
successfully extracted rows
/
elapsed seconds
```

Always define what “elapsed” includes.

## 50. Streaming-to-Parquet Benchmark

Compare:

```text
A:
named cursor
→ Python rows
→ Arrow
→ ParquetWriter

B:
COPY TO STDOUT
→ conversion/output path

C:
ADBC RecordBatchReader
→ Parquet
```

Measure:

- time;
- peak memory;
- output size;
- connection duration;
- CPU where practical.

Break timing into stages if possible:

```text
database
+
network
+
conversion
+
serialization
+
disk
```

The slowest stage is the target for optimization.

## 51. Client-Side Cursor Memory Experiment

⚠️ **INTENTIONALLY INEFFICIENT / DANGEROUS TRAINING EXAMPLE**

```python
with conn.cursor() as cur:
    cur.execute("""
        SELECT id, amount
        FROM large_orders
    """)
    rows = cur.fetchall()

    for row in rows:
        process(row)
```

Measure:

```text
peak memory
elapsed time
```

Then compare:

```python
with conn.cursor(name="extract") as cur:
    cur.execute("""
        SELECT id, amount
        FROM large_orders
        ORDER BY id
    """)

    while batch := cur.fetchmany(10_000):
        process(batch)
```

The key question is:

> What changed in the database-to-client result path?

## 52. SQLAlchemy Streaming Experiment

Compare:

```text
ordinary execution
stream_results=True
yield_per
```

Example:

```python
stmt = select(
    orders.c.id,
    orders.c.amount,
)

with engine.connect() as conn:
    result = conn.execute(stmt)
    consume(result)
```

Then:

```python
with engine.connect() as conn:
    result = conn.execution_options(
        stream_results=True,
    ).execute(stmt)
    consume(result)
```

And:

```python
with engine.connect() as conn:
    result = conn.execution_options(
        yield_per=10_000,
    ).execute(stmt)
    consume(result)
```

Measure memory and runtime.

Explain unexpected results through the stack:

```text
SQLAlchemy
→ dialect
→ driver
→ PostgreSQL
```

## 53. pandas Experiment

Compare:

```text
read_sql()
read_sql(chunksize=...)
read_sql(chunksize=...) + lower-level streaming configuration
```

Measure:

```text
peak memory
runtime
rows/sec
```

Do not conclude that `chunksize` proves streaming.

A result such as:

```text
chunksize memory still high
```

is a useful diagnostic signal, not a contradiction of the pandas API.

## 54. Complete Production-Oriented Extractor

A strong extractor combines:

```text
named cursor
+
bounded batches
+
explicit Arrow schema
+
ParquetWriter
+
temporary output
+
row count
+
structured logging
+
failure cleanup
+
validation
+
source reconciliation
+
atomic publication
```

Representative structure:

```python
def extract_table_to_parquet(
    conn,
    query,
    path,
    batch_size,
    arrow_schema,
):
    # validate arguments
    # set explicit cursor/batch behavior
    # write to temp path
    # process batches
    # track rows
    # close/finalize writer
    # validate output
    # reconcile with source boundary
    # publish atomically
    # clean up on failure
    ...
```

Production logging should capture:

```text
extract_id
table
rows_total
batch_rows
elapsed
output_bytes
```

Never log:

```text
password
full DSN containing secret
authentication token
```

## 55. Three Related Tables from One Snapshot

Exercise:

```text
customers
orders
payments
```

Goal:

```text
all outputs represent a compatible point in time
```

One possible sequence:

```text
BEGIN REPEATABLE READ
    ↓
source snapshot S1
    ↓
customers → temp
orders    → temp
payments  → temp
    ↓
validate
    ↓
reconcile
    ↓
commit/close source transaction
    ↓
publish output set
```

The source transaction is not the same transaction as the filesystem publication.

That difference matters.

A robust design makes the publication state separately observable:

```text
database extraction successful
+
outputs validated
+
publication successful
=
run published
```

## 56. Extraction from Primary vs Replica

Use this comparison:

| Aspect | Primary | Read replica |
| --- | --- | --- |
| Freshness | Primary committed state | Potentially behind primary |
| Read isolation | Shares primary resources | Separates some read load |
| Lag risk | None from replication | Yes |
| Recovery conflicts | Normal primary behavior | Hot-standby conflicts possible |
| Operational use | Fresh extracts | Heavy/offloaded reads where acceptable |

A replica is appropriate only when its freshness and capacity satisfy the workload.

## 57. Query Design for Extraction

Extraction SQL should be deliberate:

```sql
SELECT
    id,
    updated_at,
    amount
FROM orders
WHERE updated_at >= $1
ORDER BY updated_at, id;
```

Prefer:

- required columns only;
- explicit filters;
- deterministic ordering when resumability requires it;
- no unnecessary joins;
- explicit source-impact awareness.

Do not turn this module into a full SQL tuning course. The relevant point is:

> A sophisticated transfer mechanism cannot compensate for a poorly scoped extraction query.

## 58. Extraction Query + Ordering

Ordering is part of correctness.

This:

```sql
ORDER BY updated_at
```

may be ambiguous when many rows share the same timestamp.

This is stronger:

```sql
ORDER BY updated_at, id
```

because `id` acts as a tie-breaker.

Checkpoint:

```text
updated_at = 2026-09-29 12:00:00+00
id = 100
```

Next condition:

```sql
WHERE (updated_at, id) > (%s, %s)
```

The ordering key itself must be stable enough for the workload.

## 59. Watermark vs Extraction Checkpoint

A watermark is:

```text
business/data-change boundary
```

Example:

```text
updated_at <= 2026-09-29 12:00:00+00
```

A checkpoint is:

```text
progress position within the run
```

Example:

```text
last_updated_at = 2026-09-29 11:59:58+00
last_id = 900001
```

Together:

```text
watermark
→ defines the dataset to process

checkpoint
→ defines how far through that dataset the run has completed
```

Do not automatically treat them as the same value.

## 60. Complete Resumable Extraction Case Study

Scenario:

```text
20M-row orders table
extract killed after 12M rows
```

Suppose the last checkpoint is:

```text
updated_at = 2026-09-29 10:42:18.553001+00
id = 12345678
```

Recovery:

```text
1. read checkpoint
2. reopen connection
3. select rows strictly after checkpoint
4. write next batch
5. advance checkpoint after safe output
6. continue
7. reconcile source/output
8. publish only validated output
```

The absence of duplicates depends on:

```text
strictly greater than
+
deterministic ordering
+
correct checkpoint
```

The absence of missing rows depends on:

```text
complete output before checkpoint
+
stable key/data boundary
```

## 61. Failure-Injection Lab

Inject these failures.

### Failure 1 — Process killed midway

Expected recovery:

```text
discard unsafe partial state
→ resume from last valid checkpoint
```

### Failure 2 — Database connection lost

Expected recovery:

```text
current transaction/cursor ends
→ reconnect
→ resume from safe boundary
```

### Failure 3 — Parquet write fails

Expected recovery:

```text
temp is invalid
→ do not publish
→ clean or quarantine
```

### Failure 4 — Disk fills

Expected recovery:

```text
stop safely
→ free capacity
→ clean unsafe output
→ resume/restart
```

### Failure 5 — Source changes without a snapshot boundary

Expected recovery:

```text
investigate data-boundary mismatch
→ do not blindly blame the extractor
```

### Failure 6 — Checkpoint written before output

Expected consequence:

```text
restart can skip rows
```

### Failure 7 — Rename before validation

Expected consequence:

```text
consumer can observe invalid output
```

For each failure record:

```text
Failure
↓
inconsistent state
↓
correct ordering
↓
recovery
↓
prevention
```

## 62. Checkpoint Ordering

The rule is:

```text
write batch
   ↓
ensure output state is safe
   ↓
persist checkpoint
```

Never:

```text
checkpoint
   ↓
write batch
```

Otherwise:

```text
checkpoint says batch N exists
process dies
batch N missing
restart after N
missing data
```

One nuance matters: a single Parquet file is not necessarily an independently recoverable batch store. If mid-run resume must preserve prior batches, consider output fragments with explicit commit boundaries.

## 63. Output Publication Ordering

Use:

```text
extract
 ↓
close writer
 ↓
reconcile
 ↓
validate
 ↓
publish atomically
```

Never:

```text
publish
 ↓
validate
```

Publication is a logical state transition, not the same thing as writing bytes.

For multiple related files:

```text
all temp outputs ready
+
all validations passed
→
publish set / manifest
```

## 64. Extraction Audit Metadata

A conceptual record:

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

Useful operational extensions:

```text
batch_size
peak_memory
rows_per_second
query_hash
schema_version
source_endpoint
```

Do not store secrets.

The audit record should make it possible to answer:

```text
Did it run?
How many rows were expected?
How many were written?
Where is the output?
Where did it fail?
How far did it progress?
```

## 65. Production Observability

Track:

- rows extracted;
- rows/sec;
- current batch;
- peak memory;
- elapsed time;
- checkpoint position;
- retry count;
- query duration;
- connection state;
- output bytes;
- failure/rejection status.

Use the metrics to distinguish:

```text
slow source
vs
slow network
vs
slow Python conversion
vs
slow Parquet
vs
slow disk
```

Example structured message:

```text
extract batch complete
extract_id=abc123
table=orders
batch_rows=10000
rows_total=420000
elapsed_s=...
```

Do not put secrets in logs.

## 66. Extraction Bottleneck Diagnosis

Use:

```text
Extraction is slow
      ↓
Is PostgreSQL slow?
      ↓
Is network throughput limiting?
      ↓
Is Python conversion slow?
      ↓
Is Parquet writing slow?
      ↓
Is disk I/O limiting?
      ↓
Is batch size poorly tuned?
```

Measure each layer.

Example:

```text
database query time = 80s
client elapsed      = 220s
```

The missing 140 seconds must be in:

```text
network
conversion
serialization
disk
coordination
```

This is why end-to-end timing is more informative than timing only `cursor.execute()`.

## 67. Server-Side Cursor vs Keyset Pagination

These mechanisms solve different problems.

### Server-side cursor

```text
one long-running logical query
→ FETCH batch
→ FETCH batch
→ ...
```

### Keyset pagination

```text
small query
→ checkpoint
→ small query
→ checkpoint
→ ...
```

Compare:

| Dimension | Server-side cursor | Keyset pagination |
| --- | --- | --- |
| Natural consistency | Strong within one transaction | Requires explicit boundary design |
| Restartability | Additional design | Natural checkpoint boundary |
| Transaction lifetime | Potentially long | Can be shorter |
| Query count | Fewer logical queries | More queries |
| Key requirements | Lower | Requires stable ordering key |
| Changing-source semantics | Snapshot can simplify | Must be explicitly defined |

Neither is universally better.

## 68. When to Use a Server-Side Cursor

A named cursor is a natural fit when:

- one stable query is sufficient;
- sequential full extraction is desired;
- bounded client memory is required;
- a consistent snapshot is valuable;
- the source can tolerate the transaction duration.

Example:

```text
nightly full snapshot
→ one query
→ named cursor
→ Parquet
→ validation
→ publication
```

Before selecting it, ask:

```text
What is the maximum expected duration?
Can the source tolerate that snapshot?
What happens if the network dies?
Can output recovery be made safe?
```

## 69. When Keyset Pagination May Be Preferable

Keyset may be preferable when:

- restartability is critical;
- long transactions are undesirable;
- a stable ordering key exists;
- the source is naturally incremental;
- checkpoints are first-class requirements.

Example:

```text
batch 1
→ output
→ checkpoint

batch 2
→ output
→ checkpoint
```

The trade-off is greater application coordination and more explicit source-data semantics.

## 70. Streaming vs Incremental Extraction

Remember:

```text
Streaming
=
control memory per read
```

```text
Incremental extraction
=
control how much source data the run processes
```

Example:

```text
50M-row full snapshot
→ streamed in 10K batches
```

is memory-bounded but still a 50M-row run.

Incremental extraction:

```text
only 200K changed rows
```

reduces source work itself.

These mechanisms can be combined.

## 71. Production Design Patterns

### Pattern A — Full snapshot export

```text
REPEATABLE READ
 ↓
named cursor
 ↓
Parquet
 ↓
reconcile
 ↓
publish
```

### Pattern B — Large one-time serialized export

```text
COPY TO STDOUT
 ↓
temporary file
 ↓
validate
 ↓
publish
```

### Pattern C — Restartable incremental export

```text
keyset
 ↓
batch output
 ↓
checkpoint
```

### Pattern D — Multi-table consistent export

```text
one transaction/snapshot
 ↓
multiple tables
 ↓
validate all
 ↓
publish set
```

### Pattern E — Arrow-native export

```text
ADBC
 ↓
Arrow batches
 ↓
Parquet
```

Use the pattern that satisfies the workload rather than following a universal recipe.

## 72. Internal Mechanics: Client-Side Result Flow

```text
SELECT
 ↓
driver/client result path
 ↓
buffering/materialization
 ↓
fetchmany()
 ↓
Python
```

The important question is:

> Where are later rows before the application asks for them?

If the driver has already buffered them on the client, the application's batch size is not the database-to-client memory bound.

## 73. Internal Mechanics: Named Cursor Flow

```text
SELECT
 ↓
named cursor / server-side state
 ↓
FETCH batch
 ↓
Python process
 ↓
next FETCH
 ↓
...
```

This creates a controlled client-transfer boundary.

Server resources remain involved, so transaction/cursor lifecycle still matters.

## 74. Internal Mechanics: COPY TO STDOUT

```text
SELECT query
 ↓
COPY protocol
 ↓
PostgreSQL serialized stream
 ↓
psycopg receives blocks
 ↓
file / processing
```

The representation itself is different from Python row objects.

This is why COPY can be an attractive path for direct file movement.

## 75. Internal Mechanics: ADBC

```text
PostgreSQL
 ↓
ADBC driver
 ↓
Arrow RecordBatch
 ↓
Parquet / DataFrame
```

The key advantage is fewer row-to-columnar conversion boundaries.

But:

```text
Arrow Table
=
possibly whole-result materialization

RecordBatchReader
=
streaming-oriented representation
```

Use the right API for the memory requirement.

## 76. Complete Hands-On Lab

Complete these progressively:

1. `fetchall()` baseline.
2. `fetchmany()` application batching.
3. named/server-side cursor.
4. `itersize`.
5. `withhold=True`.
6. SQLAlchemy streaming.
7. pandas `chunksize`.
8. COPY TO STDOUT.
9. named cursor → ParquetWriter.
10. explicit Arrow schema.
11. temporary output.
12. row-count reconciliation.
13. keyset resumability.
14. kill-and-resume.
15. multi-table consistent snapshot.
16. ADBC Arrow extraction.
17. 20-million-row benchmark.

For each lab record:

```text
Objective
Setup
Prediction
Code
Observation
Measurement
Debugging
Production takeaway
```

## 77. `extractor.py` Exercise

Implement:

```python
extract_table_to_parquet(
    conn,
    query,
    path,
    batch_size,
)
```

Requirements:

1. Named cursor.
2. Bounded memory.
3. Stable batch size.
4. `ParquetWriter`.
5. Explicit Arrow schema.
6. Temporary output.
7. Atomic rename.
8. Row-count tracking.
9. Source count reconciliation.
10. Meaningful logging.
11. Failure cleanup.
12. Empty-table support.
13. One-row support.
14. Large-table support.

Then implement conceptual variants for:

```text
COPY TO STDOUT
ADBC RecordBatch
```

and compare:

```text
speed
memory
output
transformation flexibility
recovery
```

## 78. Resumability Exercise

Build an extractor using:

```text
(updated_at, id)
```

Procedure:

```text
1. Seed a deterministic dataset.
2. Record expected keys.
3. Extract batch 1.
4. Write output.
5. Save checkpoint.
6. Repeat for several batches.
7. Kill the process.
8. Restart from checkpoint.
9. Complete the extraction.
10. Compare source/output keys.
11. Compare counts.
12. Publish only after validation.
```

Then deliberately reverse steps 4 and 5 and demonstrate the skipped-data failure.

## 79. Consistent-Snapshot Exercise

Extract:

```text
customers
orders
payments
```

Requirements:

- one `REPEATABLE READ` transaction;
- one logical snapshot;
- separate temporary outputs;
- row counts;
- final validation;
- coordinated publication.

During the exercise, observe `pg_stat_activity` and answer:

```text
How old is the transaction?
How long is the snapshot open?
What is the operational cost?
```

## 80. 20-Million-Row Benchmark Exercise

Use one 20M-row table and equivalent result columns.

Run:

```text
client-side cursor
named cursor
COPY TO STDOUT
ADBC
```

Keep constant:

```text
data
query
machine
PostgreSQL environment
Python environment
output target
```

Measure:

```text
time
peak memory
rows/sec
output size
connection duration
```

Do not use fabricated values.

## 81. Debugging Exercises

### Problem 1 — Memory still grows with `fetchmany()`

Likely cause: client-side buffering.

### Problem 2 — Named cursor fails outside transaction

Cause: cursor lifecycle/transaction mismatch.

### Problem 3 — Cursor disappears after commit

Cause: ordinary cursor is not held across commit; evaluate `withhold=True`.

### Problem 4 — Extraction causes cleanup pressure

Cause candidate: long-running snapshot.

### Problem 5 — Extraction times out

Distinguish server `statement_timeout` from application/network deadlines.

### Problem 6 — Parquet file exists but is incomplete

Likely cause: final-path writes before validation.

### Problem 7 — Resume creates duplicates

Check:

```text
checkpoint
>
vs
>=
ordering key
checkpoint timing
```

### Problem 8 — Resume misses rows

Check:

```text
checkpoint-before-output bug
mutable key
watermark boundary
```

### Problem 9 — Row counts differ

Check snapshot/data boundary and filter semantics.

### Problem 10 — OFFSET resume skips data

Changing source positions can shift offsets.

### Problem 11 — pandas chunksize still has high memory

Inspect lower-level result buffering.

### Problem 12 — COPY is fast but Python is slow

Transport is not the bottleneck; measure processing.

### Problem 13 — ADBC memory differs from tracemalloc

Native Arrow allocations may not appear in Python allocation measurements.

### Problem 14 — Read replica returns older data

Inspect replica lag and freshness requirements.

For every bug use:

```text
Observed symptom
↓
Root cause
↓
Python state
↓
Database state
↓
Recovery
↓
Prevention
```

## 82. Extraction Anti-Patterns

### 1. `fetchall()` on a huge table

```text
simple
→ potentially unbounded client memory
```

### 2. `fetchmany()` assumed to be streaming

```text
application batching
≠
database-side streaming
```

### 3. One giant transaction

```text
consistency
→ potentially long snapshot/resource lifetime
```

### 4. No timeout

```text
runaway extraction
→ uncontrolled source impact
```

### 5. Primary-only extraction without impact analysis

```text
read workload
→ CPU/I/O/cache/connection competition
```

### 6. OFFSET restart

```text
row position
→ unstable on changing data
```

### 7. Direct final-file writing

```text
crash
→ ambiguous output
```

### 8. Checkpoint before output

```text
crash
→ skipped data on restart
```

### 9. Publish before validation

```text
consumer sees incorrect data
```

### 10. Row count as sole proof

```text
missing + duplicate
→ same count
```

### 11. pandas chunksize as proof of streaming

```text
pandas chunking
≠
driver/server streaming guarantee
```

### 12. COPY assumed universally fastest

Bulk serialization and row-level transformation are different workloads.

### 13. ADBC assumed automatically faster

Arrow representation does not erase database/network/serialization costs.

### 14. Ignoring snapshot impact

Long-lived snapshots can affect database cleanup.

## 83. Extraction Decision Framework

# How to Choose an Extraction Strategy

Ask:

1. How large is the result?
2. Is bounded memory required?
3. Is the extraction one-time or recurring?
4. Must it be restartable?
5. Is a consistent snapshot required?
6. Is row-by-row Python processing required?
7. Is raw bulk file movement the primary goal?
8. Is Arrow the natural intermediate representation?
9. How long can the source query safely run?
10. Is a read replica available?
11. What statement timeout is acceptable?
12. What output format is required?
13. How will completion be proven?
14. What does measurement show?

A neutral decision skeleton:

```text
bounded memory?
  ↓ yes
Need Python row transformations?
  ↓
named cursor / streaming path

No row-level transformation?
  ↓
bulk serialized output?
  ↓
evaluate COPY

Arrow already natural?
  ↓
evaluate ADBC record batches
```

Then evaluate two independent correctness axes:

```text
restartability
consistency
```

## 84. Named Cursor vs COPY vs ADBC Decision Table

| Dimension | Named Cursor | COPY TO STDOUT | ADBC |
| --- | --- | --- | --- |
| Row-level Python processing | Strong | Less direct | Arrow-batch oriented |
| Bounded-memory extraction | Yes with correct use | Stream-oriented | Yes with batch reader |
| Bulk file output | Good | Strong fit | Strong fit |
| Arrow integration | Conversion required | Path-dependent | Native-oriented |
| Python object creation | Per batch | Reduced | Can be reduced |
| Restartability | Additional design | Additional design | Additional design |
| Performance | Workload-dependent | Workload-dependent | Workload-dependent |

Benchmark the complete path that includes output and processing.

## 85. Extraction vs Source Protection

A successful extract is not fully successful if it destabilizes the source.

Evaluate:

```text
query duration
+
transaction duration
+
snapshot lifetime
+
CPU
+
I/O
+
connection occupancy
+
replica lag
```

Source-protection controls include:

- statement timeout;
- dedicated extraction identity;
- `application_name`;
- read replica where appropriate;
- bounded extraction concurrency;
- deliberate batch size;
- narrow queries;
- scheduling outside critical source windows.

## 86. Primary vs Replica Decision Framework

### Primary

Consider when:

- freshness is mandatory;
- source capacity is adequate;
- extraction impact is acceptable.

### Replica

Consider when:

- lag is acceptable;
- read isolation is useful;
- replica capacity is sufficient;
- hot-standby behavior is understood.

Always assess:

```text
freshness
lag
capacity
query duration
recovery conflicts
```

## 87. Consistency vs Recovery Trade-Off

### Long consistent snapshot

```text
strong point-in-time view
+
potentially long transaction
```

### Shorter keyset batches

```text
better restart boundaries
+
more application complexity
+
changing-source semantics
```

The right design starts from the correctness requirement.

## 88. Extraction Correctness Proofs

# How to Prove the Extract Is Complete

Use:

```text
row count
+
key comparison
+
checkpoint continuity
+
output validation
+
snapshot/data-boundary evidence
```

The evidence means:

```text
count
→ quantity

keys
→ identity

checkpoint
→ progress

schema/file checks
→ output structure

snapshot/watermark
→ source boundary
```

No single signal is enough for every workload.

## 89. Output Validation

Validate:

- schema;
- columns;
- expected types;
- row count;
- file readability;
- Parquet footer/metadata;
- publication state.

Representative inspection:

```python
import pyarrow.parquet as pq

pf = pq.ParquetFile(path)
assert pf.schema_arrow == expected_schema
```

For huge files, avoid reading the entire file only to validate it. Prefer metadata and batch-aware validation where possible.

## 90. Complete Production Extraction Pipeline

```text
PostgreSQL
   ↓
read/replica
   ↓
bounded extraction mechanism
   ↓
Arrow batches
   ↓
ParquetWriter
   ↓
temporary output
   ↓
row-count/key reconciliation
   ↓
atomic publication
   ↓
audit record
```

Failure boundaries:

```text
source
→ query/timeout failure

transfer
→ cursor/network failure

conversion
→ schema/type failure

output
→ disk/write failure

validation
→ mismatch

publication
→ final visibility failure
```

Each boundary should have a recovery path.

## 91. Internal End-to-End Query Flow

```python
with conn.cursor(name="extract") as cur:
    cur.execute("""
        SELECT id, updated_at, amount
        FROM orders
        ORDER BY updated_at, id
    """)

    while batch := cur.fetchmany(10_000):
        process(batch)
```

The conceptual layers are:

```text
1. Python opens connection.
2. Transaction/session begins.
3. Named cursor is created.
4. PostgreSQL executes query.
5. Server-side cursor state is maintained.
6. Python requests batches.
7. Driver adapts values.
8. Arrow/output consumes the batch.
9. Progress/checkpoint state advances.
10. Final validation occurs.
11. Temporary file is published.
12. Resources close.
```

Not every query uses the same physical server resources. Keep implementation claims at the documented behavioral level.

## 92. Why Memory Can Stay Bounded

```text
source rows ↑↑↑
      ↓
batch size fixed
      ↓
active batch ≈ fixed
      ↓
Python peak memory stays controlled
```

Exceptions:

```text
very wide rows
large values
Arrow/native buffers
writer buffers
accidental retention
```

Therefore:

> Bounded means controlled and approximately stable under the intended workload assumptions.

A fixed row count is not enough if each row can itself be enormous.

## 93. Complete Resume Timeline

```text
Batch 1
  ↓
write output
  ↓
checkpoint 1

Batch 2
  ↓
write output
  ↓
checkpoint 2

Batch 3
  ↓
write output
  ↓
checkpoint 3

PROCESS KILLED

Restart
  ↓
read checkpoint 3
  ↓
start after checkpoint 3
  ↓
continue Batch 4
```

The critical invariant:

```text
checkpoint N
=
all output through N is safely recoverable
```

## 94. Complete Snapshot Timeline

```text
BEGIN REPEATABLE READ
        ↓
Snapshot S1
        ↓
customers from S1
        ↓
orders from S1
        ↓
payments from S1
        ↓
COMMIT
```

This gives compatible point-in-time reads across the tables, at the cost of keeping the transaction/snapshot active.

## 95. Complete Failure Recovery Model

```text
RUNNING
  ↓
batch extraction
  ↓
write temp
  ↓
checkpoint
  ↓
...
  ↓
FAILURE
  ↓
cleanup unsafe state
  ↓
restart from last valid checkpoint
  ↓
complete
  ↓
reconcile
  ↓
publish atomically
```

Every state transition needs an invariant.

## 96. Testing Strategy

Test:

- empty result;
- one row;
- multiple rows;
- large table;
- client-side result behavior;
- named cursor;
- `fetchmany()`;
- `itersize`;
- `withhold=True`;
- transaction behavior;
- statement timeout;
- replica behavior where available;
- SQLAlchemy streaming;
- pandas chunksize;
- COPY TO STDOUT;
- Parquet writing;
- explicit Arrow schema;
- temporary output;
- atomic publication;
- row-count reconciliation;
- key reconciliation;
- checkpoint correctness;
- process kill/resume;
- connection failure;
- disk failure;
- consistent snapshot;
- ADBC.

Representative inline pytest:

```python
def test_empty_extract_preserves_schema(tmp_path, conn):
    output = tmp_path / "empty.parquet"

    rows = extract_table_to_parquet(
        conn=conn,
        query="""
            SELECT id, updated_at, amount
            FROM orders
            WHERE false
        """,
        path=output,
        batch_size=10_000,
        arrow_schema=expected_schema,
    )

    assert rows == 0
    assert output.exists()
```

## 97. Data Integrity Test Matrix

| Test | Expected result |
| --- | --- |
| Empty table | Valid empty output with schema |
| One row | Exactly one output row |
| Large table | Approximately bounded memory |
| Kill mid-extract | Resume succeeds |
| Duplicate checkpoint attempt | No duplicate final rows |
| Missing checkpoint update | Restart is safe |
| Source changes outside snapshot | Behavior is explicit |
| Same extract rerun | Controlled output |
| Corrupt/incomplete temp file | Not published |
| Connection failure | Safe retry/restart |
| Disk failure | Temp state not published |
| Replica lag | Freshness policy is respected |

## 98. Code Review Checklist

# Large Extraction Code Review Checklist

### Memory

- Does the code call `fetchall()` on a large result?
- Does `fetchmany()` operate on a streaming/server-side result path?
- Are prior batches released?
- Is batch size explicit and measured?

### Database

- Is transaction lifetime deliberate?
- Is a long snapshot required?
- Is `statement_timeout` configured?
- Is `application_name` set?
- Is primary/replica placement intentional?

### Correctness

- Is ordering deterministic?
- Is the checkpoint written after output?
- Is the data boundary explicit?
- Is count reconciliation based on the same boundary?
- Is key-level validation used where appropriate?

### Output

- Is there a temp path?
- Is `ParquetWriter` closed?
- Is schema explicit?
- Is publication atomic/logically atomic?
- Is validation performed before publication?

### Operations

- Are progress metrics present?
- Can operators find the session in `pg_stat_activity`?
- Are secrets absent from logs?
- Is the failure state recoverable?

## 99. Production Hardening

Think in stages.

### Level 1 — Working

```text
SELECT
→ process
→ write
```

### Level 2 — Memory controlled

```text
named cursor
→ bounded batches
```

### Level 3 — Operationally safer

```text
timeout
+
monitoring
+
temp output
+
validation
```

### Level 4 — Recoverable

```text
keyset
+
checkpoint
+
kill/resume testing
```

### Level 5 — Correctness-proven

```text
data boundary
+
count
+
key evidence
+
schema validation
```

### Level 6 — Evidence-driven

```text
benchmark
+
source-impact measurement
+
documented decision
```

## 100. Interview Questions

1. Why can `fetchall()` be dangerous for very large results?
2. What is a named/server-side cursor?
3. Why is `fetchmany()` not itself proof of streaming?
4. What does `itersize` influence?
5. Why do named cursors have transaction-lifetime implications?
6. What does `withhold=True` change?
7. What risks come from long-running reads?
8. Why might a read replica help?
9. What does `stream_results=True` request?
10. What does `yield_per` do?
11. Why doesn't pandas `chunksize` guarantee database-side streaming?
12. What is `COPY (query) TO STDOUT`?
13. How do you stream to Parquet?
14. Why use an explicit Arrow schema?
15. Why write to a temporary path?
16. Why can extract and count disagree?
17. Why is OFFSET a poor restart position?
18. How does `(updated_at, id)` support resumability?
19. What makes a checkpoint valid?
20. How do you prove no rows are missing or duplicated?
21. Why use `REPEATABLE READ` for related tables?
22. What's the difference between `fetch_arrow_table()` and a record-batch reader?
23. What happens when the network dies halfway through?
24. Which metrics should a production extractor expose?
25. How would you benchmark four extraction methods fairly?

## 101. Architecture Questions

1. Design PostgreSQL → Parquet extraction for 20 million rows with bounded memory.
2. Compare named cursor, COPY TO STDOUT, and ADBC using explicit workload assumptions.
3. A four-hour extraction holds an old transaction snapshot. What risks do you investigate?
4. How would you reduce extraction impact on the primary?
5. How would you ensure a killed process never skips data?
6. How would you prove completeness?
7. How would you extract customers/orders/payments from one point in time?
8. Why might pandas chunksize still show high memory?
9. COPY is faster but row transformation is harder. How do you decide?
10. How do you publish multiple outputs atomically/logically atomically?
11. How do you prevent checkpoint/output ordering bugs?
12. How would you benchmark fairly?

Reason from:

```text
data volume
+
memory
+
source impact
+
consistency
+
restartability
+
output format
+
performance
+
operability
```

## 102. Decision Framework

# How to Design a Production Extraction

Ask, in order:

1. What is the result size?
2. Must Python memory remain bounded?
3. Is row-by-row transformation required?
4. Is raw bulk movement the goal?
5. Is restartability required?
6. Is a consistent snapshot required?
7. Can the source tolerate the read duration?
8. Is a read replica available?
9. What output format is required?
10. What mechanism provides the needed performance?
11. How will correctness be proved?
12. How will failure be recovered?
13. What does the benchmark show?

This is a process, not a universal “best method.”

## 103. Extraction Anti-Failure Rules

Never assume:

```text
chunksize = streaming
```

Correct principle:

```text
chunksize = pandas chunk consumption
```

Never assume:

```text
fetchmany = streaming
```

Correct principle:

```text
fetchmany = application fetch size
```

Never assume:

```text
file exists = success
```

Correct principle:

```text
published file = validated result
```

Never assume:

```text
count matches = exact contents
```

Correct principle:

```text
count + key/progress/output evidence
```

Never assume:

```text
fastest benchmark = best architecture
```

Correct principle:

```text
performance
+
correctness
+
recovery
+
source protection
+
operability
```

## 104. Common Mistakes

Preserve these roadmap-required mistakes:

- `fetchall()` or `read_sql()` without an appropriate streaming path on large tables;
- extracting from the primary during peak hours without impact analysis;
- leaving partial output after a crash;
- using `OFFSET` as a restart position while data changes.

Also avoid:

- treating `fetchmany()` as guaranteed server-side streaming;
- ignoring named-cursor transaction requirements;
- using `withhold=True` without understanding resource lifetime;
- keeping snapshots open unnecessarily;
- setting timeouts too aggressively;
- having no timeout;
- writing checkpoints before output is safely established;
- validating after publication;
- using only row counts as correctness proof;
- ignoring replica lag;
- measuring only Python memory;
- choosing huge batches without measurement;
- choosing tiny batches without measurement;
- selecting unnecessary columns;
- mixing consistency and restartability requirements without explicitly choosing the trade-off.

## 105. Final Mental Model

# The Large-Extraction Mental Model

```text
The source is large.

Therefore:
    control result transfer,
    control application memory,
    control transaction lifetime,
    control output publication,
    control restart state,
    control source impact.
```

Remember:

```text
Client-side cursor
=
normal result handling path

Named cursor
=
server-side result state + controlled batch retrieval

COPY TO STDOUT
=
bulk serialized extraction path

ADBC
=
Arrow-native extraction path

Keyset pagination
=
restartability

REPEATABLE READ
=
cross-table snapshot consistency

Temporary files + atomic publication
=
safe visibility

Reconciliation
=
evidence of correctness
```

And:

```text
Streaming
≠
Incremental extraction
```

Streaming controls memory per read.

Incremental extraction controls how much source data a run processes.

Finally:

```text
Fast extraction
≠
safe extraction
```

A production extractor needs:

```text
performance
+
bounded memory
+
correctness
+
restartability
+
source protection
+
observability
```

## 106. Final Review

# Final Review

### What You Now Understand

You now understand:

- client-side vs server-side cursors;
- named cursors;
- `fetchmany()`;
- `itersize`;
- `withhold=True`;
- bounded memory;
- long-running snapshots;
- read replicas;
- statement timeouts;
- SQLAlchemy streaming;
- `yield_per`;
- pandas chunksize caveat;
- COPY TO STDOUT;
- CSV/Parquet streaming;
- explicit Arrow schemas;
- row reconciliation;
- keyset pagination;
- checkpoints;
- consistent snapshots;
- ADBC;
- network failure handling;
- atomic publication;
- observability;
- benchmarking.

### What You Can Implement

You should be able to:

- extract tables larger than RAM;
- use named cursors;
- write Parquet incrementally;
- implement keyset resumability;
- survive process failures;
- reconcile source/output;
- extract related tables consistently;
- compare COPY and ADBC;
- benchmark memory/time;
- protect the source;
- publish output atomically.

### What You Can Debug

You should be able to diagnose:

```text
memory growth
cursor/transaction problems
timeouts
long snapshots
replica lag
partial output
checkpoint bugs
missing/duplicate rows
pandas buffering
COPY bottlenecks
ADBC/native memory
```

### What You Can Defend in Production Reviews

You should be able to explain decisions about:

```text
cursor type
batch size
snapshot
replica
timeout
checkpoint
output publication
reconciliation
benchmark evidence
```

As the final topic of Module 2.7, you have now covered the Python ↔ database boundary:

```text
DB-API
  ↓
psycopg
  ↓
safe queries
  ↓
transactions
  ↓
pooling
  ↓
SQLAlchemy Core
  ↓
ORM
  ↓
migrations
  ↓
bulk loading
  ↓
large-result extraction
```

The next module is:

**Module 2.8 — Data Modelling for Analytics**

This module does not teach data modelling. It gives you the connectivity foundation needed to reason about keys, grain, and warehouse structures next.

## 107. Production Rules to Remember

1. Never assume `fetchall()` is safe for large tables.
2. `fetchmany()` alone does not guarantee database-side streaming.
3. Use named/server-side cursors when the workload needs controlled result transfer.
4. Understand named-cursor transaction lifetime.
5. Treat `withhold=True` as a deliberate lifecycle choice.
6. Keep extraction memory bounded.
7. Measure batch size.
8. Protect the source database from uncontrolled long-running reads.
9. Use statement timeouts deliberately.
10. Consider read replicas for heavy extraction workloads.
11. Use COPY TO STDOUT when its data-transfer characteristics fit the workload.
12. Consider ADBC when Arrow-native transfer is valuable.
13. Write output to temporary paths first.
14. Publish final files atomically.
15. Persist checkpoints only after the corresponding output state is safely established.
16. Use keyset pagination when resumability is required on changing data.
17. Use consistent snapshots when cross-table consistency is required.
18. Row counts alone do not prove completeness.
19. Benchmark time and memory rather than relying on tool reputation.
20. Choose the extraction architecture from workload, correctness, source impact, and operational requirements.

---

# Final Engineering Mindset

Do not ask only:

> “How do I fetch 20 million rows?”

Ask:

```text
How will rows move from PostgreSQL to the destination?
Where will they be buffered?
How much memory can Python use?
How long will the database snapshot remain open?
What happens if the connection dies at 80%?
How will I resume?
How will I prove no rows are missing?
How will I prevent duplicate output?
How will I publish only a complete result?
How will I protect the source database?
What does measurement show?
```

> **Large-result extraction is not simply a loop over rows. It is a controlled data-movement system with memory, consistency, recovery, source-protection, and observability requirements.**

---

# API Verification Notes

Verify installed library versions in your own environment before production deployment.

- Psycopg 3 cursor types: https://www.psycopg.org/psycopg3/docs/advanced/cursors.html
- Psycopg 3 cursor API: https://www.psycopg.org/psycopg3/docs/api/cursors.html
- Psycopg 3 transactions: https://www.psycopg.org/psycopg3/docs/basic/transactions.html
- SQLAlchemy 2.x connections and streaming: https://docs.sqlalchemy.org/en/20/core/connections.html
- SQLAlchemy ORM large-result handling: https://docs.sqlalchemy.org/en/20/orm/queryguide/api.html
- pandas `read_sql`: https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html
- Apache Arrow ADBC Python documentation: https://arrow.apache.org/adbc/current/python/
- PostgreSQL `COPY`: https://www.postgresql.org/docs/current/sql-copy.html
- PostgreSQL monitoring: https://www.postgresql.org/docs/current/monitoring-stats.html
- PostgreSQL transaction isolation: https://www.postgresql.org/docs/current/transaction-iso.html
- PostgreSQL client timeout settings: https://www.postgresql.org/docs/current/runtime-config-client.html
