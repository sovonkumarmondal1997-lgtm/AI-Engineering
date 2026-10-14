# Bulk Loading with COPY and executemany

## Learning Objectives

By the end of this topic, you should be able to:

- Explain why row-by-row inserts become inefficient at high row counts.
- Explain the role of network round trips, transaction boundaries, Python overhead, and database work in bulk-loading performance.
- Explain the loading ladder from single-row `INSERT` through transactions, `executemany()`, multi-row `INSERT`, `COPY`, and binary `COPY`.
- Use psycopg 3 `COPY FROM STDIN` and `copy.write_row()`.
- Stream input from a Python iterable without materializing the entire dataset in memory.
- Distinguish row-oriented COPY from text/CSV block writes and binary COPY.
- Move Parquet data into PostgreSQL staging with bounded memory.
- Design a staging → validate → `MERGE`/upsert ingestion workflow.
- Reason about batch size, commit frequency, restartability, and idempotency.
- Understand why one malformed row can fail a COPY operation and how to isolate bad rows.
- Debug NULL-marker, delimiter, quote, timestamp/timezone, UUID, array, JSON, and Decimal/numeric issues.
- Evaluate indexes, constraints, triggers, and `ANALYZE` as part of a large-load plan.
- Integrate pandas, Polars, and ADBC into database-loading workflows.
- Explain the difference between client-side `STDIN`/`STDOUT` COPY and PostgreSQL server-side file COPY.
- Explain how DuckDB can participate in Parquet/PostgreSQL movement without treating it as a universal replacement for PostgreSQL-native loading.
- Benchmark loading methods fairly on the same workload.
- Design an idempotent, restartable, observable bulk-loading pipeline.
- Review a bulk loader in production engineering terms rather than speed slogans.

The central outcome is not “always use COPY.”

It is:

> **Understand why different loading methods behave differently, measure them on the target workload, and design a safe loading architecture.**

---

## Prerequisites

This topic assumes that you already understand:

- DB-API execution
- psycopg 3
- parameterized queries
- transactions
- connection pooling
- SQLAlchemy Core
- SQLAlchemy ORM trade-offs
- Alembic schema migrations
- staging patterns from Module 2.6
- Parquet basics from Module 2.5

Do not re-teach those topics in depth.

Topic 09 is where Python database connectivity becomes high-volume data movement engineering.

The core mental model is:

```text
Input data
    ↓
Reader / generator / Parquet
    ↓
Loading method
    ↓
PostgreSQL staging
    ↓
Validation
    ↓
MERGE / upsert
    ↓
Target table
```

---

# 1. Why Bulk Loading Matters

Loading five rows and loading five million rows may use the same SQL vocabulary, but they do not create the same engineering problem.

For a tiny operation:

```text
Python
  ↓
INSERT
  ↓
PostgreSQL
```

may be perfectly reasonable.

For a large load:

```text
5,000,000 rows
```

the cumulative cost of:

- Python function calls
- serialization
- network traffic
- server parsing
- protocol synchronization
- transaction handling
- index maintenance
- constraint checks
- trigger execution
- WAL generation

can dominate the actual useful work.

So the question changes from:

> “How do I insert this row?”

to:

> “How can I move this dataset through the database boundary with the least unnecessary work while preserving correctness?”

---

# 2. Why Row-by-Row Inserts Are Slow

Consider:

```python
for row in rows:
    cur.execute(
        """
        INSERT INTO orders (id, amount)
        VALUES (%s, %s)
        """,
        row,
    )
```

A conceptual execution path is:

```text
Python row
   ↓
driver execution
   ↓
database interaction
   ↓
PostgreSQL
   ↓
result/progress
   ↓
next row
```

The exact wire behavior depends on the driver and execution mode, so do not assume that every `execute()` causes exactly one network round trip.

The important idea is that repeated small operations create repeated protocol and application overhead.

For one million rows, even a small per-row cost becomes large.

## Where the time can go

```text
Python loop overhead
+
parameter adaptation
+
protocol traffic
+
database execution
+
index maintenance
+
constraint checks
+
WAL
+
commit
```

The database may spend relatively little time doing the actual row insertion compared with all the surrounding overhead.

---

# 3. Autocommit vs One Transaction

A particularly expensive pattern is committing every row:

```text
row 1 → commit
row 2 → commit
row 3 → commit
...
```

Each commit is a durability boundary.

A more efficient conceptual structure is:

```text
many rows
    ↓
one deliberate transaction
    ↓
commit
```

With psycopg:

```python
with conn.transaction():
    for row in rows:
        cur.execute(
            """
            INSERT INTO orders (id, amount)
            VALUES (%s, %s)
            """,
            row,
        )
```

This changes the failure boundary.

### One transaction

```text
all rows
   ↓
failure
   ↓
rollback the transaction
```

### Separate commits

```text
batch 1 committed
batch 2 committed
batch 3 committed
batch 4 fails
```

Now the database contains a partial load.

Neither design is automatically correct for every workload.

The decision depends on:

- required atomicity
- load size
- restartability
- transaction duration
- rollback scope
- WAL pressure
- operational recovery requirements

---

# 4. The Loading Ladder

A useful learning ladder is:

```text
Single INSERT
      ↓
Single transaction
      ↓
executemany()
      ↓
Multi-row INSERT
      ↓
COPY
      ↓
Binary COPY
```

The point is not to memorize a ranking.

The point is to understand which layer of overhead each technique removes or changes.

| Method | Main idea | Main cost/concern |
| --- | --- | --- |
| Single `INSERT` | one row per execution | repeated execution overhead |
| One transaction | many writes under one transaction | larger failure/rollback boundary |
| `executemany()` | repeated parameter sets through one API call | driver-specific execution behavior |
| Multi-row `INSERT` | several rows in one SQL statement | statement/parameter size |
| COPY | PostgreSQL bulk data protocol | data-format and error-handling design |
| Binary COPY | binary representation over COPY | tighter type-format coupling |

Treat the ladder as a reasoning framework, not a universal performance guarantee.

---

# 5. Single INSERT

A parameterized single-row insert:

```python
cur.execute(
    """
    INSERT INTO orders (id, amount)
    VALUES (%s, %s)
    """,
    (1, 100),
)
```

is a good teaching baseline because it shows the database boundary clearly.

You already learned parameterization in earlier topics.

The new lesson is that **correctness and performance are separate questions**.

A single insert may be exactly right when:

- a human-facing operation creates one record
- the row count is tiny
- latency of one operation matters more than throughput
- the code is not performing bulk data movement

The same technique becomes questionable when repeated millions of times.

---

# 6. One Transaction

Now group many inserts into a transaction:

```python
with conn.transaction():
    for row in rows:
        cur.execute(
            """
            INSERT INTO orders (id, amount)
            VALUES (%s, %s)
            """,
            row,
        )
```

You have removed repeated commit boundaries, but you still have repeated execution calls.

Think:

```text
one transaction
+
many execute() calls
```

This is better than:

```text
one transaction per row
```

for many workloads, but the protocol and Python overhead of individual execution still exists.

### Production lesson

Do not stop optimizing merely because you moved from autocommit to one transaction.

---

# 7. `executemany()`

Psycopg supports:

```python
cur.executemany(
    """
    INSERT INTO orders (id, amount)
    VALUES (%s, %s)
    """,
    rows,
)
```

Conceptually:

```text
one SQL template
+
many parameter sets
```

This is preferable to manually building a giant string containing actual values.

The driver can decide how to execute those parameter sets efficiently.

In current psycopg 3, `executemany()` uses pipeline-mode machinery internally, so a caller does not need to wrap a single `executemany()` call in an explicit pipeline block merely to get that behavior. Exact execution behavior remains driver-specific. citeturn744364search0

### What `executemany()` does not mean

It does **not** mean:

```text
“the database sees one magical bulk statement”
```

The concrete protocol and batching behavior depend on the driver implementation.

That is why benchmarking still matters.

---

# 8. `executemany()` vs Manual Loop

| Method | Main idea | Engineering concern |
| --- | --- | --- |
| Loop + `execute()` | repeated individual execution | potentially high Python/protocol overhead |
| `executemany()` | repeated parameterized execution through driver API | driver behavior must be measured |
| Multi-row `INSERT` | several rows in one SQL statement | SQL/parameter payload grows |
| COPY | bulk data protocol | format, validation, failure semantics |

### Bad idea

```python
sql = f"""
INSERT INTO orders (id, amount)
VALUES {some_python_string_with_values}
"""
cur.execute(sql)
```

> ⚠️ INTENTIONALLY UNSAFE TRAINING EXAMPLE

This mixes query construction with data values and creates quoting/injection problems.

Use parameterized APIs or COPY.

---

# 9. Multi-Row INSERT

A multi-row insert can look like:

```sql
INSERT INTO orders (id, amount)
VALUES
    (%s, %s),
    (%s, %s),
    (%s, %s);
```

The database receives multiple rows as one statement.

The potential advantages are:

```text
fewer statement boundaries
+
fewer protocol interactions
```

But the SQL payload becomes larger.

That means you must consider:

- number of parameters
- statement size
- Python construction cost
- memory
- server parsing/processing
- error isolation

---

# 10. When Multi-Row INSERT Becomes Awkward

Imagine constructing a statement containing tens or hundreds of thousands of values.

Even with parameterization, the statement becomes operationally awkward.

Potential problems include:

```text
huge statement
+
many parameters
+
larger Python structures
+
harder failure isolation
```

If one row is malformed, the whole statement can fail.

That is one reason PostgreSQL provides COPY as a dedicated bulk data path.

---

# 11. What Is PostgreSQL COPY?

`COPY` is PostgreSQL's specialized bulk data movement mechanism.

Psycopg 3 exposes PostgreSQL's COPY protocol through `Cursor.copy()`. The current psycopg documentation describes `COPY FROM STDIN` and `COPY TO STDOUT` as the normal client-side pattern, using a `Copy` object as a context manager. citeturn920414search0

Conceptually:

```text
Input data
    ↓
COPY protocol
    ↓
PostgreSQL
```

This is different from:

```text
row
 ↓
INSERT
 ↓
row
 ↓
INSERT
 ↓
row
 ↓
INSERT
```

COPY is designed for continuous bulk transfer.

That changes the economics of the data path.

---

# 12. `COPY FROM STDIN`

The basic psycopg 3 pattern is:

```python
with cur.copy(
    "COPY orders (id, amount) FROM STDIN"
) as copy:
    ...
```

Then:

```python
copy.write_row((1, 100))
copy.write_row((2, 250))
```

A complete example:

```python
import psycopg


def load_orders(conn: psycopg.Connection) -> None:
    rows = [
        (1, 100),
        (2, 250),
        (3, 75),
    ]

    with conn.cursor() as cur:
        with cur.copy(
            "COPY orders (id, amount) FROM STDIN"
        ) as copy:
            for row in rows:
                copy.write_row(row)

    conn.commit()
```

The values are adapted by psycopg as COPY row values. The COPY operation remains subject to normal transaction behavior. citeturn920414search0

### Line-by-line mental model

```text
cur.copy(...)
    ↓
start COPY FROM STDIN

copy.write_row(...)
    ↓
send one logical record through COPY

exit with-block
    ↓
complete COPY operation

commit
    ↓
make transaction durable
```

---

# 13. COPY Row Mode

`write_row()` accepts an iterable of values:

```python
with cur.copy(
    "COPY orders (id, amount, customer_id) FROM STDIN"
) as copy:
    for row in rows:
        copy.write_row(row)
```

This is especially convenient when your source is already represented as Python rows.

Current psycopg documentation notes that Python iterables can be streamed this way and that values use psycopg's normal adaptation machinery. If an exception is raised inside the COPY context, the operation is interrupted and the records inserted so far by that COPY operation are discarded. citeturn920414search0

### Important limitation

Row-by-row `write_row()` is not the same thing as block-level CSV/text loading.

For row mode, do not mix it with COPY options such as:

```text
FORMAT CSV
DELIMITER
NULL
```

when using `write_row()`. For already-formatted text/CSV data, use block writes instead. citeturn920414search0

---

# 14. COPY Write Modes

There are three useful concepts to distinguish.

## Row-oriented writing

```python
copy.write_row(row)
```

You provide Python values.

## Block-oriented writing

```python
copy.write(data)
```

You provide already-formatted COPY payload, such as text or bytes.

## Binary COPY

```sql
COPY orders FROM STDIN (FORMAT BINARY)
```

You transfer binary COPY data.

Psycopg 3 supports both row-level and block-level writing. Current documentation notes that block writes can use `str` in text mode or `bytes` in text/binary modes. citeturn920414search1

### Decision question

Ask:

```text
Do I have Python records?
```

Use row mode.

Ask:

```text
Do I already have correctly formatted COPY data?
```

Block mode may be more appropriate.

Ask:

```text
Do I need binary transfer and can I control PostgreSQL's exact type format?
```

Consider binary COPY.

---

# 15. COPY Text Format

Text COPY represents data in a text-oriented serialization.

The important issues are:

- delimiters
- escaping
- NULL representation
- encoding
- type parsing
- embedded special characters

A text representation might conceptually look like:

```text
1	100	India
2	250	India
3	75	UK
```

The separator is part of the COPY format contract.

Do not invent a parser independently of PostgreSQL's expected format.

---

# 16. COPY CSV Format

CSV is deceptively complicated.

A field can contain:

```text
comma
quote
newline
```

For example:

```text
"London, UK"
```

or:

```text
"Customer said ""hello"""
```

A CSV loader must correctly handle quoting and escaping.

Potential failure modes:

```text
delimiter inside field
quote inside field
newline inside field
incorrect escaping
wrong encoding
wrong NULL marker
```

### Production lesson

A file being called “CSV” does not prove that it satisfies the PostgreSQL COPY CSV contract.

---

# 17. Binary COPY

Binary COPY changes the representation of data.

Conceptually:

```text
Python/application
       ↓
binary COPY payload
       ↓
PostgreSQL
```

Potential advantages include less text formatting/parsing overhead.

Potential cost:

- stricter type compatibility
- more complex debugging
- more careful testing
- stronger dependence on target type representation

Current psycopg documentation warns that PostgreSQL binary COPY is strict about types and does not apply ordinary cast rules in the same forgiving way as text input. For example, a value whose binary type does not exactly match the target PostgreSQL type can be rejected. citeturn920414search0

### Example

```python
with cur.copy(
    "COPY orders (id, amount) FROM STDIN (FORMAT BINARY)"
) as copy:
    for row in rows:
        copy.write_row(row)
```

Use binary COPY deliberately.

Do not choose it merely because “binary sounds faster.”

---

# 18. Generator-Based COPY

You do not need to materialize the entire dataset.

Instead of:

```python
rows = list(source)
```

use:

```python
def rows():
    for item in source:
        yield (
            item.id,
            item.amount,
        )
```

Then:

```python
with cur.copy(
    "COPY orders (id, amount) FROM STDIN"
) as copy:
    for row in rows():
        copy.write_row(row)
```

Conceptually:

```text
source
  ↓
generator
  ↓
COPY
  ↓
PostgreSQL
```

This is one of the most important memory lessons in the module.

---

# 19. Streaming Parquet into COPY

Suppose a Parquet file contains millions of orders.

A production-oriented path is:

```text
Parquet
   ↓
bounded batch reader
   ↓
Arrow/Parquet batch
   ↓
controlled conversion
   ↓
COPY
   ↓
staging table
```

Do not do:

```python
rows = parquet_file.read().to_pylist()
```

for a huge file unless you have intentionally sized memory for the entire dataset.

Instead:

```text
read batch
   ↓
convert batch
   ↓
COPY batch
   ↓
release batch
   ↓
read next batch
```

The objective is bounded memory.

---

# 20. `copy_parquet_to_staging()`

A representative design is:

```python
from collections.abc import Iterable
from pathlib import Path
import psycopg


def copy_parquet_to_staging(
    path: Path,
    table: str,
    connection: psycopg.Connection,
    batches: Iterable[Iterable[tuple]],
) -> int:
    rows_loaded = 0

    with connection.cursor() as cur:
        with cur.copy(
            f"COPY {table} (order_id, customer_id, amount, ordered_at) "
            "FROM STDIN"
        ) as copy:
            for batch in batches:
                for row in batch:
                    copy.write_row(row)
                    rows_loaded += 1

    return rows_loaded
```

The table identifier above is illustrative. In production code, do not insert an untrusted identifier into SQL by string interpolation. Use validated configuration and/or psycopg's SQL composition tools for identifiers.

The important architecture is:

```text
Parquet reader
    ↓
bounded batch
    ↓
Python rows
    ↓
COPY
    ↓
staging
```

### Required properties

- explicit target columns
- bounded memory
- controlled data types
- safe identifiers
- deliberate transaction scope
- useful metrics
- predictable failure behavior

---

# 21. Staging Table Pattern

A high-volume ingestion path often uses:

```text
Source file / source system
          ↓
        COPY
          ↓
     staging table
          ↓
       validate
          ↓
      rejected rows
          ↓
        MERGE
          ↓
      target table
```

Why not always COPY directly into the final table?

Because staging creates a controlled boundary.

You can:

- inspect the incoming data
- validate before mutating the target
- detect duplicates
- quarantine malformed records
- measure the load
- retry the final merge
- make reruns easier to reason about

---

# 22. Staging Table Design

A staging table might contain:

```text
order_id
customer_id
amount
ordered_at
load_id
```

You can also maintain a separate audit record.

Choices include:

### Temporary staging

Useful when data is tightly scoped to one database session/workflow.

### Persistent staging

Useful when operators need to inspect or replay loads.

### Unlogged staging

Potentially useful for transient workloads where the durability/replication trade-offs are acceptable.

There is no universal staging schema.

Choose based on:

- data volume
- replay needs
- transaction model
- cleanup strategy
- concurrency
- durability requirements
- operational tooling

---

# 23. UNLOGGED Staging

PostgreSQL supports `UNLOGGED` tables.

Conceptually:

```sql
CREATE UNLOGGED TABLE staging_orders (
    order_id BIGINT,
    customer_id BIGINT,
    amount NUMERIC,
    ordered_at TIMESTAMPTZ
);
```

An unlogged table reduces some WAL-related overhead, but it changes durability and replication behavior.

Therefore:

```text
faster transient staging
```

may come with:

```text
different crash/recovery/replication semantics
```

Do not use it automatically.

---

# 24. Validate After COPY

A successful COPY means the input was accepted by PostgreSQL's COPY parser/type checks.

It does not prove that the data is semantically valid.

Think:

```text
COPY success
    ≠
business-data success
```

Validation might include:

- row count
- required fields
- valid ranges
- duplicate business keys
- expected timestamps
- valid reference values
- domain rules
- source/target reconciliation

Example:

```sql
SELECT COUNT(*)
FROM staging_orders;
```

Check missing identifiers:

```sql
SELECT COUNT(*)
FROM staging_orders
WHERE order_id IS NULL;
```

Check negative amounts:

```sql
SELECT COUNT(*)
FROM staging_orders
WHERE amount < 0;
```

Check duplicate keys:

```sql
SELECT order_id, COUNT(*)
FROM staging_orders
GROUP BY order_id
HAVING COUNT(*) > 1;
```

---

# 25. MERGE / Upsert Into Target

The core pipeline is:

```text
staging
   ↓
validate
   ↓
MERGE/upsert
   ↓
target
```

The Python boundary can be:

```python
with conn.transaction():
    # 1. load staging
    # 2. validate staging
    # 3. merge into target
    ...
```

Whether all three steps should share one transaction depends on:

- staging size
- target size
- lock behavior
- atomicity requirements
- failure/restart strategy

Do not assume that “one transaction is always safer.”

---

# 26. Full Staging Load

A production-oriented load often becomes:

```text
1. create/prepare staging
2. COPY input
3. validate staging
4. identify/reject invalid records
5. MERGE into target
6. record metrics
7. clean up staging
```

At each stage ask:

```text
What can fail?
What has changed?
Can I retry?
What is visible?
What needs cleanup?
```

That turns a loader into an operational workflow rather than a single SQL call.

---

# 27. Batch Size

Batch size is one of the most important knobs in a bulk loader.

A larger batch can reduce per-batch overhead.

But a larger batch can also increase:

- memory
- transaction duration
- rollback scope
- failure blast radius
- retry cost
- database pressure

Think:

```text
tiny batch
    ↓
low memory / small failure scope
but more overhead

medium batch
    ↓
trade-off

huge batch
    ↓
potentially strong throughput
but large memory/failure/transaction scope
```

Do not copy a batch size from another team's system.

Measure it.

---

# 28. Commit Frequency

Compare:

```text
commit every row
```

```text
commit every batch
```

```text
commit entire load
```

### Commit every row

Pros:

- tiny rollback scope

Cons:

- enormous commit overhead

### Commit every batch

Pros:

- bounded failure scope
- restartability
- controlled transaction size

Cons:

- partial progress must be tracked

### One giant transaction

Pros:

- strong all-or-nothing semantics for the transaction

Cons:

- huge rollback scope
- long transaction
- large resource footprint
- difficult recovery for very large datasets

The right choice depends on the required correctness and operational model.

---

# 29. Restartability

Suppose a 100 GB input fails after 70% has loaded.

Ask:

```text
Can I restart from zero?
```

Sometimes yes.

But for expensive loads, you may prefer:

```text
batch checkpoints
+
deterministic load IDs
+
idempotent target logic
```

A conceptual design:

```text
batch 1 → committed
batch 2 → committed
batch 3 → committed
batch 4 → failed
```

Restart could begin at batch 4 instead of batch 1.

This requires explicit progress tracking.

---

# 30. Idempotent Loading

Idempotency means:

> Repeating the same logical load should not unexpectedly duplicate or corrupt the target.

Bad:

```text
load file
load same file
→ duplicate rows
```

Better:

```text
load file
load same file
→ same intended target state
```

Mechanisms can include:

- stable business keys
- unique constraints
- deterministic `load_id`
- staging tables
- `MERGE`
- upsert semantics
- processed-file records

No single mechanism fits every workload.

---

# 31. Loading the Same File Twice

This is a mandatory production-grade exercise.

### Procedure

1. Load the file.
2. Record target counts and relevant state.
3. Record the load identifier.
4. Load the exact same file again.
5. Compare the resulting target state.

A successful test should prove the second execution is handled as intended.

For example:

```text
First run:
10,000 input rows
10,000 target changes

Second run:
10,000 input rows
0 additional logical changes
```

The exact result depends on your idempotency design.

Do not invent the result before running the test.

---

# 32. Bad Rows

COPY is intentionally strict.

Imagine:

```text
100,000 valid rows
1 malformed row
```

The COPY operation can fail as a whole.

This is useful for correctness because you do not silently accept malformed data.

But operationally it can be inconvenient.

Current psycopg documentation notes that an exception raised within the COPY context interrupts the operation and discards the records inserted so far by that COPY operation. citeturn920414search0

---

# 33. COPY Failure Semantics

Typical failure sources include:

- invalid integer
- numeric overflow
- malformed timestamp
- invalid UUID
- malformed JSON
- incorrect field count
- malformed CSV quoting
- unexpected NULL representation

For example:

```text
2026-09-29T25:12:00Z
```

cannot represent a valid time.

A malformed row can make the entire COPY batch fail.

That makes batch sizing a data-quality control too.

---

# 34. Finding Bad Rows

A useful diagnostic strategy is binary splitting.

```text
large batch
   ↓
COPY fails
   ↓
split batch in half
   ↓
test first half
   ↓
test second half
   ↓
identify failing subset
   ↓
repeat
```

Eventually:

```text
bad subset
   ↓
bad row
```

This resembles binary search.

It is valuable for debugging imports.

It is not necessarily the best steady-state production design.

For recurring supplier/data-quality problems, pre-validation or quarantine-oriented ingestion may be better.

---

# 35. Bad-Row Quarantine

A quarantine structure might look like:

```text
rejected_rows
-------------
load_id
row_number
raw_data
error_reason
created_at
```

The point is to preserve enough evidence for:

- investigation
- reconciliation
- correction
- reprocessing

A useful flow is:

```text
input
  ↓
validation
  ├── valid → load
  └── invalid → quarantine
```

Do not silently discard malformed records.

---

# 36. COPY NULL Markers

NULL handling is a classic source of bugs.

The data may contain:

```text
NULL
```

as a literal string.

Or:

```text
""
```

as an empty string.

Those are not necessarily the same thing.

For a CSV/text contract, explicitly define:

```text
What means NULL?
What means empty string?
What means missing field?
```

For row-mode `write_row()`, psycopg performs value adaptation rather than requiring you to manually encode a NULL marker. For block COPY, you are responsible for producing compatible COPY-formatted data. citeturn920414search0

---

# 37. Delimiters and Quotes

Suppose the data contains:

```text
New York, NY
```

If comma is the delimiter, the field must be encoded correctly.

Suppose the customer name is:

```text
O'Reilly
```

or:

```text
He said "hello"
```

Correct COPY formatting matters.

Potential bugs:

```text
wrong delimiter
wrong quote character
missing escaping
incorrect newline handling
```

### Production lesson

Choose and test one explicit wire format.

Do not “split on comma” and assume you have CSV parsing solved.

---

# 38. Timezones in COPY

Timestamps deserve explicit treatment.

Two PostgreSQL types matter:

```text
timestamp without time zone
timestamp with time zone
```

Your pipeline must decide:

```text
Are timestamps UTC?
Are they local?
Are offsets preserved?
What does source text mean?
```

For production data pipelines, a deliberate UTC convention is often easier to reason about, but the correct design depends on the source's business semantics.

### Example risk

Source:

```text
2026-09-29 10:00:00+05:30
```

If the pipeline drops the offset and writes:

```text
2026-09-29 10:00:00
```

the original instant may be lost.

Do not allow a serializer to silently erase time-zone meaning.

---

# 39. Decimal Precision

Financial and measurement data often require exact decimal semantics.

Python:

```python
from decimal import Decimal

amount = Decimal("123456789.123456")
```

PostgreSQL:

```text
NUMERIC
```

Do not casually convert:

```text
Decimal
  ↓
float
```

because floating-point representation may not preserve the intended decimal value.

A useful contract is:

```text
source decimal
   ↓
Python Decimal
   ↓
PostgreSQL numeric
```

Record:

- precision
- scale
- rounding rules

---

# 40. Data Types During COPY

| Python/data representation | PostgreSQL target | Main concern |
| --- | --- | --- |
| `int` | `integer` / `bigint` | range |
| `Decimal` | `numeric` | precision/scale |
| timezone-aware `datetime` | `timestamptz` | instant/timezone |
| `date` | `date` | format |
| UUID | `uuid` | valid UUID |
| `list` | array | element types |
| dict / JSON text | `jsonb` | valid JSON |
| `None` | `NULL` | missing vs empty |

Binary COPY requires especially careful type compatibility because PostgreSQL is stricter about binary representations. citeturn920414search0

---

# 41. UUID, Array, and JSON Awareness

These types often expose hidden assumptions.

## UUID

Make sure the input is actually a UUID:

```python
from uuid import UUID

value = UUID("9b1deb4d-b5e0-4a18-9f6a-8e7e12b7c123")
```

## Arrays

The Python representation and PostgreSQL element type must agree.

For example:

```text
list[int]
```

should not accidentally become:

```text
list[str]
```

## JSON / JSONB

Validate JSON structure and encoding before load.

Example:

```python
import json

payload = json.dumps(
    {"source": "supplier-a", "version": 3}
)
```

The target database still enforces its own type rules.

---

# 42. Index Strategy

Indexes help reads.

Indexes also add work to writes.

During a large initial load, evaluate:

```text
indexes already present
```

versus:

```text
load data
    ↓
create nonessential indexes
```

Potentially, maintaining many indexes during a huge initial load can add significant work.

But dropping indexes can be dangerous when:

- uniqueness is required
- readers depend on the index
- constraints use the index
- the system cannot tolerate the temporary absence
- rebuilding is expensive
- the target is already serving traffic

So:

> **Do not automatically drop indexes. Measure and reason from workload requirements.**

---

# 43. Deferrable Constraints

Some PostgreSQL constraints can be defined as deferrable.

Conceptually:

```text
immediate validation
```

versus:

```text
deferred validation
```

A deferred constraint can sometimes allow a transaction to temporarily contain an intermediate state and enforce the invariant later in the transaction.

This can be useful for certain bulk-loading workflows.

But:

- not every constraint is deferrable
- deferral affects transaction semantics
- deferred validation can delay error detection

Use it only when the workload needs it.

---

# 44. Triggers During Large Loads

Triggers can execute additional work during inserts or updates.

That may include:

- audit records
- denormalized updates
- validations
- notifications
- derived calculations

Therefore:

```text
COPY throughput
```

can be limited by:

```text
trigger work
```

Disabling triggers can be dangerous and may require privileges or special database behavior.

Do not treat:

```text
DISABLE TRIGGER
```

as a default performance optimization.

Correctness comes first.

---

# 45. `ANALYZE` After Loading

PostgreSQL's query planner relies on statistics.

A large load can materially change the data distribution.

Running:

```sql
ANALYZE orders;
```

can refresh statistics so the planner has better information about the new state.

Do not claim that every query plan must change after `ANALYZE`.

The lesson is:

```text
large data change
    ↓
statistics may no longer represent reality
    ↓
consider ANALYZE
```

---

# 46. Large Initial Load Optimization

Before a large initial load, evaluate:

```text
input format
batch size
transaction strategy
staging table
indexes
constraints
triggers
WAL/storage capacity
target merge strategy
ANALYZE
```

Do not optimize one dimension independently.

For example:

```text
COPY is very fast
```

does not matter if:

```text
MERGE becomes the bottleneck
```

or:

```text
index maintenance dominates
```

A fast transport layer can simply move the bottleneck elsewhere.

---

# 47. pandas Loading

Pandas supports:

```python
df.to_sql(...)
```

and integrates with SQLAlchemy or supported ADBC connections. The current pandas documentation also supports a callable `method` for customizing how rows are inserted. citeturn244743search0

A normal call might be:

```python
df.to_sql(
    "orders",
    engine,
    if_exists="append",
    index=False,
)
```

The important Data Engineering question is:

> What happens underneath?

For large loads, default row-oriented behavior may not match the throughput you need.

Pandas also supports `chunksize` and `method="multi"`/custom methods. citeturn244743search0

---

# 48. Custom pandas COPY Method

The roadmap requires awareness of a custom `to_sql(method=...)` method that uses PostgreSQL COPY.

A representative pattern is:

```python
from collections.abc import Callable, Iterable

import pandas as pd
from psycopg import sql


def copy_method(
    pd_table,
    conn,
    keys: list[str],
    data_iter: Iterable[tuple],
) -> int:
    raw_connection = conn.connection
    table_name = pd_table.name

    columns = sql.SQL(", ").join(
        sql.Identifier(key)
        for key in keys
    )

    copy_sql = sql.SQL(
        "COPY {} ({}) FROM STDIN"
    ).format(
        sql.Identifier(table_name),
        columns,
    )

    count = 0

    with raw_connection.cursor() as cur:
        with cur.copy(copy_sql) as copy:
            for row in data_iter:
                copy.write_row(row)
                count += 1

    return count


df.to_sql(
    "orders",
    engine,
    if_exists="append",
    index=False,
    method=copy_method,
)
```

The exact object exposed through pandas' SQLAlchemy integration depends on the versions and connection type. Treat this as a teaching pattern that should be validated against the exact versions used in your project.

### Why this matters

```text
DataFrame
   ↓
pandas
   ↓
custom SQL/database method
   ↓
COPY
   ↓
PostgreSQL
```

This keeps pandas useful as an analytical edge layer without forcing its default insertion strategy to define your bulk-loading architecture.

---

# 49. Polars Loading

Polars provides:

```python
df.write_database(...)
```

The current stable API accepts either an existing SQLAlchemy/ADBC connection or a URI, and allows choosing an SQLAlchemy or ADBC write engine. citeturn244743search1

Example:

```python
import polars as pl

df = pl.DataFrame(
    {
        "order_id": [1, 2, 3],
        "amount": [100, 200, 300],
    }
)

df.write_database(
    table_name="orders",
    connection="postgresql://user:password@localhost/db",
    if_table_exists="append",
)
```

For production code, do not hard-code credentials in source.

Polars is most useful as the DataFrame transformation boundary.

The database write path still needs independent evaluation.

---

# 50. ADBC / Arrow-Native Ingestion

ADBC provides an Arrow-oriented database connectivity standard.

Conceptually:

```text
Arrow Table
     ↓
ADBC driver
     ↓
PostgreSQL
```

The current ADBC PostgreSQL driver supports bulk ingestion, and its Python DB-API exposes `adbc_ingest()` for ingesting an Arrow `Table`, `RecordBatch`, or `RecordBatchReader`. citeturn353989search0turn353989search1

Install the PostgreSQL driver:

```bash
pip install adbc-driver-postgresql
```

A basic connection is:

```python
import adbc_driver_postgresql.dbapi


uri = "postgresql://user:password@localhost:5432/postgres"

with adbc_driver_postgresql.dbapi.connect(uri) as conn:
    ...
```

---

# 51. ADBC Ingest Example

With PyArrow:

```python
import pyarrow as pa
import adbc_driver_postgresql.dbapi


table = pa.table(
    {
        "order_id": [1, 2, 3],
        "amount": [100.0, 250.0, 75.0],
    }
)

uri = "postgresql://user:password@localhost:5432/postgres"

with adbc_driver_postgresql.dbapi.connect(uri) as conn:
    with conn.cursor() as cur:
        inserted = cur.adbc_ingest(
            "orders",
            table,
            mode="append",
        )

        print(inserted)
```

The ADBC API supports different ingestion modes such as append/create/replace/create-append, depending on the driver. citeturn353989search0

The important data path is:

```text
Arrow data
    ↓
ADBC
    ↓
PostgreSQL
```

not:

```text
Arrow
 ↓
Python list of tuples
 ↓
row loop
```

---

# 52. COPY vs ADBC

Use a workload comparison.

| Dimension | PostgreSQL COPY | ADBC ingestion |
| --- | --- | --- |
| Input representation | Python rows or COPY-formatted blocks | Arrow-native data |
| PostgreSQL-specific control | Strong | More standardized abstraction |
| Arrow interoperability | Requires conversion unless already in Arrow-friendly path | Native design |
| Type handling | PostgreSQL COPY semantics | Arrow ↔ PostgreSQL type mapping |
| Debugging | Direct PostgreSQL COPY model | Additional abstraction layer |
| Ecosystem integration | PostgreSQL-focused | Cross-tool Arrow ecosystem |
| Universal performance winner? | No | No |

Current ADBC PostgreSQL documentation notes that bulk ingestion is supported and that the driver has specific Arrow↔PostgreSQL type mappings. It also notes limitations around some PostgreSQL types, including numeric read-back behavior and some timestamp handling details. citeturn353989search1

The decision should be measured, especially when type conversion dominates.

---

# 53. Server-Side COPY TO/FROM Files

PostgreSQL also supports server-side file paths in COPY.

Conceptually:

```sql
COPY orders TO '/server/path/orders.csv';
```

or:

```sql
COPY orders FROM '/server/path/orders.csv';
```

The critical distinction is:

```text
STDIN / STDOUT
=
client/driver provides or receives data
```

whereas:

```text
server-side file path
=
PostgreSQL server environment accesses the file
```

That means server-side COPY depends on:

- PostgreSQL server filesystem
- PostgreSQL server permissions
- deployment environment
- security policy

For many Python ingestion workflows, `STDIN` is easier because the application controls the stream.

---

# 54. DuckDB PostgreSQL Extension

DuckDB can participate in a Parquet/PostgreSQL data path.

Conceptually:

```text
Parquet
   ↕
DuckDB
   ↕
PostgreSQL
```

This can be useful when DuckDB is already the analytical processing engine around the file.

But it is not automatically a replacement for:

```text
psycopg COPY
```

or:

```text
ADBC
```

The important question is:

```text
Where is the transformation happening?
Where is the bulk transfer happening?
What format crosses each boundary?
```

Choose the path that minimizes unnecessary conversion and operational complexity for the workload.

---

# 55. Warehouse Bulk Loads

Cloud warehouses often expose their own high-throughput loading mechanisms.

Therefore:

```text
PostgreSQL COPY
```

is not the same abstraction as:

```text
generic warehouse load API
```

A platform might use:

```text
Object storage
   ↓
warehouse native bulk load
```

while PostgreSQL may use:

```text
application/object storage
   ↓
COPY FROM STDIN
   ↓
PostgreSQL
```

Do not force PostgreSQL-specific loading mechanics onto a warehouse.

The detailed warehouse architecture belongs elsewhere in the roadmap.

---

# 56. Performance Model

A useful high-level model is:

```text
Total load cost
=
Python processing
+
serialization
+
network transfer
+
protocol overhead
+
database parsing
+
WAL
+
index maintenance
+
constraint checks
+
trigger work
+
commit
```

Different methods optimize different terms.

### Row-by-row

```text
high repeated-call overhead
```

### `executemany()`

```text
reduces some repeated execution overhead
```

### Multi-row INSERT

```text
packs more rows into statements
```

### COPY

```text
uses a purpose-built bulk protocol
```

### Binary COPY

```text
changes the representation itself
```

Do not claim that one technique dominates every part of the cost model.

---

# 57. Network Round-Trip Model

Suppose:

```text
1,000,000 rows
```

A conceptual comparison is:

### Individual execution

```text
row
 ↓
operation
 ↓
response
 ↓
next row
```

### Bulk protocol

```text
many rows
 ↓
continuous/batched transfer
 ↓
PostgreSQL
```

This becomes especially important when client/server latency is meaningful.

Psycopg's pipeline support documentation explains that reducing client/server waiting can matter most for many small operations or higher-latency connections. citeturn744364search0

COPY is not simply “pipeline mode for INSERT.” It is a different protocol path.

---

# 58. Memory Model

Compare:

### Bad

```python
rows = list(source)
load(rows)
```

### Better

```python
for batch in source:
    load(batch)
```

The relevant metric is peak memory:

```text
Peak memory
=
largest set of live objects/buffers
```

Large loads can consume memory in:

- Python objects
- Arrow arrays
- DataFrame batches
- serialization buffers
- COPY buffers
- temporary staging structures

Bounded memory is a design goal, not an afterthought.

---

# 59. Transaction Model for Bulk Loads

Compare:

```text
one giant transaction
```

with:

```text
batch transaction
```

The choice changes:

- atomicity
- rollback scope
- throughput
- restartability
- replication impact
- lock duration
- recovery complexity

A useful decision question is:

> “What is the largest unit of work that I am comfortable repeating or rolling back?”

That often points toward a practical batch boundary.

---

# 60. Staging + MERGE Transaction Strategy

A common architecture is:

```text
COPY
  ↓
staging
  ↓
validation
  ↓
MERGE
  ↓
target
```

You must decide whether:

```text
COPY + validate + MERGE
```

belongs in one transaction or separate phases.

### One transaction

Can provide stronger atomicity.

### Separate phases

Can provide:

- better restartability
- smaller transactions
- easier operational inspection
- smaller failure scope

Neither is universally correct.

---

# 61. Required 1-Million-Row Benchmark

The benchmark must compare the loading ladder on the **same one million logical rows**.

Compare:

1. single inserts
2. one transaction
3. `executemany()`
4. multi-row `INSERT`
5. COPY
6. binary COPY where practical

Use the same:

- PostgreSQL instance
- target table
- schema
- dataset
- machine resources
- Python version
- relevant driver/library versions

Run repeated trials.

Where appropriate, warm up the environment first.

Measure:

- elapsed time
- rows/second
- peak memory
- transaction count
- error count
- connection usage where relevant

Do not fabricate results.

---

# 62. Benchmark Prediction Exercise

Before running the experiment, create predictions.

Example table:

| Method | Predicted throughput | Predicted memory behavior | Predicted bottleneck |
| --- | --- | --- | --- |
| Single INSERT | write your prediction | write your prediction | write your prediction |
| One transaction | write your prediction | write your prediction | write your prediction |
| `executemany()` | write your prediction | write your prediction | write your prediction |
| Multi-row INSERT | write your prediction | write your prediction | write your prediction |
| COPY | write your prediction | write your prediction | write your prediction |
| Binary COPY | write your prediction | write your prediction | write your prediction |

Then run the experiment.

Compare:

```text
Prediction
   ↓
Measurement
   ↓
Explanation of mismatch
```

This is a performance-engineering habit.

---

# 63. Benchmark Result Template

Use this table:

| Method | Rows | Time | Rows/sec | Peak Memory | Transactions | Errors | Notes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Single INSERT | 1,000,000 | measure | measure | measure | measure | measure | |
| One transaction | 1,000,000 | measure | measure | measure | measure | measure | |
| `executemany()` | 1,000,000 | measure | measure | measure | measure | measure | |
| Multi-row INSERT | 1,000,000 | measure | measure | measure | measure | measure | |
| COPY | 1,000,000 | measure | measure | measure | measure | measure | |
| Binary COPY | 1,000,000 | measure | measure | measure | measure | measure | |
| ADBC | 1,000,000 | measure | measure | measure | measure | measure | |

**Do not fill the table with invented numbers.**

---

# 64. Performance Interpretation

Suppose:

```text
COPY is faster
```

That is useful.

But the architecture still needs to answer:

```text
Is the load idempotent?
Can bad rows be isolated?
Is memory bounded?
Can it restart?
Can operations observe it?
```

Suppose:

```text
ADBC is slower in one benchmark
```

Do not conclude:

```text
ADBC is bad
```

Investigate:

- Arrow construction cost
- type conversion
- batch size
- database state
- driver version
- indexes
- target constraints

Performance results are evidence for a workload, not slogans about a tool.

---

# 65. COPY + ANALYZE Experiment

Design an experiment.

### Step 1

Load substantial data.

### Step 2

Run a query whose plan depends on statistics.

### Step 3

Run:

```sql
ANALYZE orders;
```

### Step 4

Compare the planner's statistics/plan where applicable.

The goal is not to force the plan to change.

The goal is to observe when fresh statistics matter.

---

# 66. COPY + Index Strategy Experiment

Compare two controlled scenarios.

### Scenario A

Indexes already exist during the load.

### Scenario B

Nonessential indexes are created after loading.

Measure:

- total load duration
- total index-build duration
- database CPU
- disk activity
- query availability
- resulting target state

Do not remove an index that is required for correctness merely to improve benchmark speed.

---

# 67. COPY + Constraint Strategy

Evaluate:

```text
immediate constraints
```

versus:

```text
deferred constraints
```

where PostgreSQL supports the relevant constraint as deferrable.

Also compare:

```text
COPY directly into constrained target
```

with:

```text
COPY into staging
→ validate
→ merge
```

The key question is:

> Where should correctness be enforced, and at what point?

Do not disable database constraints just to make a benchmark faster.

---

# 68. COPY + Trigger Strategy

Measure whether trigger work materially affects the load.

Ask:

```text
How much of load time is transport?
How much is trigger work?
```

If triggers perform expensive secondary work, COPY cannot eliminate that cost.

Any attempt to change trigger behavior must be:

- explicit
- authorized
- reversible where possible
- validated for correctness

---

# 69. Production Observability

A production loader should expose evidence.

Track:

- rows read
- rows loaded
- rows rejected
- rows/second
- elapsed time
- batch count
- batch failures
- retries
- transaction duration
- connection usage
- memory
- validation duration
- MERGE duration

A useful log event might look like:

```text
load_id=20260929-orders-001
batch=42
rows=50,000
elapsed_ms=8200
rows_per_sec=6097
status=success
```

Do not log secrets.

---

# 70. Load Audit Records

A load audit structure can contain:

```text
load_id
source_file
started_at
finished_at
rows_read
rows_loaded
rows_rejected
status
error_message
```

This supports:

- operations
- reconciliation
- incident investigation
- reruns
- reporting

The exact schema is project-specific.

---

# 71. Load Reconciliation

A simple reconciliation equation can be:

```text
rows_read
=
rows_loaded
+
rows_rejected
```

where that accounting model matches the pipeline design.

Example:

```text
1,000,000 read
999,980 loaded
20 rejected
```

Then:

```text
1,000,000
=
999,980 + 20
```

Reconciliation should be tied to a specific `load_id` and workflow definition.

---

# 72. From a Working Loader to a Production Loader

Think in maturity levels.

## Level 1 — Row-by-row

```text
INSERT per row
```

## Level 2 — One transaction

```text
many writes
→ one transaction
```

## Level 3 — `executemany()`

```text
parameterized repeated execution
```

## Level 4 — COPY

```text
bulk protocol
```

## Level 5 — Bounded memory

```text
batch/generator input
```

## Level 6 — Staging + validation

```text
COPY
→ staging
→ validate
```

## Level 7 — MERGE/idempotency

```text
validated staging
→ controlled target update
```

## Level 8 — Bad-row quarantine

```text
invalid data
→ evidence-preserving quarantine
```

## Level 9 — Benchmark/observability

```text
measure
→ understand
→ monitor
```

## Level 10 — Recovery/restartability

```text
checkpoint
→ retry
→ reconcile
```

Production maturity comes from combining these concerns.

---

# 73. Internal Mechanics: `executemany()`

Given:

```python
cur.executemany(
    """
    INSERT INTO orders (id, amount)
    VALUES (%s, %s)
    """,
    rows,
)
```

Think:

```text
Python iterable
      ↓
psycopg
      ↓
driver execution/pipeline behavior
      ↓
PostgreSQL
```

The standard DB-API concept is:

```text
many parameter sets
```

The concrete optimization is driver-specific.

In psycopg 3, `executemany()` internally uses pipeline mode, but COPY is not available inside pipeline mode. citeturn744364search0

That distinction matters:

```text
executemany()
=
optimized repeated execution

COPY
=
separate bulk protocol
```

---

# 74. Internal Mechanics: COPY

Given:

```python
with cur.copy(
    "COPY orders (id, amount) FROM STDIN"
) as copy:
    for row in rows:
        copy.write_row(row)
```

Think:

```text
Python row
      ↓
psycopg COPY interface
      ↓
COPY protocol
      ↓
PostgreSQL
      ↓
table
```

The driver is not generating an `INSERT` statement for each row.

Instead, the application participates in a database bulk-transfer protocol. citeturn920414search0

This is the central reason COPY belongs higher on the loading ladder.

---

# 75. Internal Mechanics: Staging Pipeline

The end-to-end data path is:

```text
Input
  ↓
batching
  ↓
bulk transport
  ↓
staging
  ↓
validation
  ↓
merge/upsert
  ↓
idempotent target
  ↓
observability
```

For each stage, know:

| Stage | Purpose | Typical failure |
| --- | --- | --- |
| Input | source data | malformed file |
| Batching | bound resources | oversized batch |
| COPY | transport | type/format failure |
| Staging | isolate input | target staging issue |
| Validation | business/data checks | rejected records |
| MERGE | final mutation | constraint/key conflict |
| Idempotency | safe reruns | duplicate logical load |
| Observability | evidence | missing metrics |

---

# 76. Complete Hands-On Lab

All exercises remain inside this document.

## Lab 1 — Single-Row Insert

**Objective**

Create a baseline measurement.

**Setup**

Use a disposable PostgreSQL table.

**Learner prediction**

Predict how many database operations occur.

**Code**

```python
with conn.cursor() as cur:
    cur.execute(
        """
        INSERT INTO orders (id, amount)
        VALUES (%s, %s)
        """,
        (1, 100),
    )

conn.commit()
```

**Expected observation**

One logical insert operation.

**Measurement**

Record elapsed time.

**Debugging**

Inspect exceptions and transaction state.

**Production takeaway**

This is a baseline, not automatically a bulk-loading strategy.

---

## Lab 2 — One Transaction

**Objective**

Measure the effect of commit frequency.

**Code**

```python
with conn.transaction():
    for order_id in range(1, 10_001):
        conn.execute(
            """
            INSERT INTO orders (id, amount)
            VALUES (%s, %s)
            """,
            (order_id, order_id * 10),
        )
```

**Prediction**

Removing per-row commits should reduce commit overhead.

**Measurement**

Record total elapsed time.

---

## Lab 3 — `executemany()`

**Code**

```python
rows = [
    (order_id, order_id * 10)
    for order_id in range(1, 10_001)
]

with conn.cursor() as cur:
    cur.executemany(
        """
        INSERT INTO orders (id, amount)
        VALUES (%s, %s)
        """,
        rows,
    )

conn.commit()
```

**Prediction**

Predict how it compares with the manual loop.

---

## Lab 4 — Multi-Row INSERT

Construct a parameterized multi-row statement for a moderate batch.

Do not interpolate values into the SQL text.

**Measurement**

Compare:

```text
statement construction time
+
database time
```

---

## Lab 5 — COPY Row Mode

```python
with conn.cursor() as cur:
    with cur.copy(
        "COPY orders (id, amount) FROM STDIN"
    ) as copy:
        for order_id in range(1, 10_001):
            copy.write_row(
                (order_id, order_id * 10)
            )

conn.commit()
```

**Prediction**

Predict the main source of savings.

---

## Lab 6 — COPY Text/CSV

Create correctly formatted COPY text data.

Test:

- delimiter handling
- quotes
- NULL
- newline in a field

Use block-level `copy.write()` rather than `write_row()` when you are supplying preformatted COPY data. citeturn920414search0

---

## Lab 7 — Binary COPY

Test:

```sql
COPY orders FROM STDIN (FORMAT BINARY)
```

Verify type compatibility carefully.

Do not use binary mode until the target data types are explicit.

---

## Lab 8 — Generator-Based COPY

Replace:

```python
rows = list(source)
```

with a generator.

Measure peak memory where practical.

---

## Lab 9 — Parquet → Staging

Read Parquet in bounded batches and COPY into:

```text
staging_orders
```

Record:

- batch count
- rows
- duration
- peak memory

---

## Lab 10 — Validation

Validate:

- row counts
- NULL rules
- duplicates
- amount ranges
- timestamp semantics

---

## Lab 11 — MERGE

Merge validated staging data into the target.

Measure the MERGE separately from the COPY.

This shows whether transport or target mutation is the bottleneck.

---

## Lab 12 — Idempotent Rerun

Run the same logical load twice.

Prove that the second execution does not create unintended duplicate target state.

---

## Lab 13 — Bad-Row Quarantine

Introduce a malformed row.

Use batch splitting to identify the failing subset.

Move the invalid record into:

```text
rejected_rows
```

Record the error reason.

---

## Lab 14 — ADBC Ingestion

Load the same logical dataset through ADBC.

Measure the same dimensions used for COPY.

---

## Lab 15 — Benchmark All Methods

Run the one-million-row benchmark.

Do not optimize one method differently unless the benchmark specification explicitly calls for that distinction.

---

## Lab 16 — Index Strategy Experiment

Compare:

```text
indexes already present
```

and:

```text
load
→ build nonessential indexes
```

---

## Lab 17 — Analyze After Load

Run:

```sql
ANALYZE orders;
```

Observe planner statistics/plan behavior where applicable.

---

## Lab 18 — Failure Injection

Test:

- malformed row
- connection failure
- duplicate key
- MERGE failure
- process crash after staging
- repeated file delivery

For each scenario, document:

```text
failure
  ↓
staging state
  ↓
target state
  ↓
recovery action
  ↓
idempotency impact
```

---

# 77. `bulk_loader.py` Exercise

The roadmap requires an exercise equivalent to:

```text
bulk_loader.py
```

Do not create an external file for this document.

Implement the exercise in your local project.

The learner must:

1. Implement every rung of the loading ladder.
2. Measure rows/second.
3. Load one million orders.
4. Stream Parquet into PostgreSQL using COPY.
5. Use staging → validation → MERGE.
6. Keep memory bounded.
7. Find bad rows using batch splitting.
8. Quarantine invalid records.
9. Load the same dataset through ADBC.
10. Compare ADBC with COPY.
11. Rerun the same file twice.
12. Prove the target behaves idempotently.

For every implementation, record:

```text
method
dataset
batch size
transaction strategy
elapsed time
rows/sec
peak memory
errors
recovery behavior
```

---

# 78. Parquet → Staging Exercise

Design:

```python
def copy_parquet_to_staging(
    path,
    staging_table,
    connection,
    batch_size,
):
    ...
```

Requirements:

- bounded-memory reads
- explicit target columns
- predictable type conversion
- COPY
- useful exceptions
- transaction handling
- cleanup strategy
- metrics

The learner should explain:

```text
Why this batch size?
Why this transaction boundary?
Why this conversion?
Why this staging table?
```

---

# 79. Staging → Validate → MERGE Project

Create this architecture:

```text
Parquet
   ↓
COPY
   ↓
staging_orders
   ↓
validation queries
   ↓
rejected_rows
   ↓
MERGE
   ↓
orders
```

For each stage, document:

- input
- output
- failure type
- retryability
- cleanup
- observability

Do not retry data errors indefinitely.

---

# 80. Failure-Injection Lab

## Failure 1 — Malformed CSV row

Expected focus:

```text
COPY format validation
```

## Failure 2 — Invalid timestamp

Expected focus:

```text
type semantics
```

## Failure 3 — Numeric overflow

Expected focus:

```text
numeric range / Decimal contract
```

## Failure 4 — Duplicate business key

Expected focus:

```text
staging validation / MERGE
```

## Failure 5 — Connection lost

Expected focus:

```text
transaction state
retry boundary
```

## Failure 6 — MERGE fails

Expected focus:

```text
target constraint/data correctness
```

## Failure 7 — Crash after staging

Expected focus:

```text
restartability
```

## Failure 8 — Same file twice

Expected focus:

```text
idempotency
```

---

# 81. Debugging Exercises

## Problem 1 — Row-by-row load takes hours

**Observed symptom**

The loader is still running long after the expected window.

**Possible causes**

- repeated execution overhead
- network latency
- database bottleneck
- indexes
- triggers

**Corrective direction**

Measure the loading ladder rather than guessing.

---

## Problem 2 — `executemany()` is slower than expected

**Investigate**

- driver behavior
- batch size
- SQL shape
- index maintenance
- server CPU
- network latency

Do not assume `executemany()` has one fixed performance profile.

---

## Problem 3 — Multi-row INSERT becomes too large

**Investigate**

- statement size
- parameter count
- Python memory
- error isolation

Consider a different loading method.

---

## Problem 4 — COPY fails because of one malformed row

**Investigate**

- failing batch
- input format
- type conversion
- batch-splitting diagnostic

---

## Problem 5 — Timestamp values shifted

**Investigate**

- source timezone
- serialization
- target type
- session timezone
- UTC convention

---

## Problem 6 — Numeric values lose precision

**Investigate**

```text
Decimal
  ↓
float?
```

and compare the final PostgreSQL numeric value.

---

## Problem 7 — Empty strings become NULL

**Investigate**

- COPY NULL marker
- CSV representation
- source data contract

---

## Problem 8 — CSV fields break on commas or quotes

**Investigate**

- delimiter
- quote
- escape semantics
- encoding

---

## Problem 9 — COPY is fast but MERGE is slow

The bottleneck may have moved to:

- target indexes
- target constraints
- conflict detection
- target-side SQL
- table contention

Do not keep optimizing COPY if MERGE dominates.

---

## Problem 10 — Rerunning duplicates data

**Root cause**

No idempotency contract.

**Fix**

Introduce stable keys and controlled merge logic.

---

## Problem 11 — Large load consumes too much memory

**Root cause**

Whole-file materialization.

**Fix**

Use batch readers/generators.

---

## Problem 12 — ADBC differs from COPY

Investigate:

- Arrow conversion
- type mappings
- batch size
- input representation
- database state
- driver version

Do not infer architecture from one benchmark.

---

# 82. Bulk-Loading Anti-Patterns

## Anti-pattern 1 — One INSERT per row in autocommit

Why beginners do it:

```text
simple to write
```

What actually happens:

```text
many commits
```

Production consequence:

```text
poor throughput
```

Correct mental model:

```text
commit is a cost and a correctness boundary
```

---

## Anti-pattern 2 — Giant SQL string with values

Why beginners do it:

```text
looks like fewer statements
```

What actually happens:

```text
unsafe query construction
+
large SQL payload
```

Production consequence:

```text
security and operability problems
```

Correct mental model:

```text
parameterize values
```

---

## Anti-pattern 3 — COPY directly into final tables without validation

Consequence:

```text
bad input
   ↓
final production table
```

Correct mental model:

```text
staging creates a safety boundary
```

---

## Anti-pattern 4 — ORM objects for million-row ingestion

Consequence:

```text
millions of Python objects
+
identity/session overhead
```

Correct mental model:

```text
use a set/bulk-oriented loading path
```

---

## Anti-pattern 5 — Materializing entire Parquet file

Consequence:

```text
peak memory explosion
```

Correct mental model:

```text
bounded batches
```

---

## Anti-pattern 6 — One giant transaction without recovery planning

Consequence:

```text
large rollback
+
large failure scope
```

Correct mental model:

```text
choose a deliberate transaction boundary
```

---

## Anti-pattern 7 — Keeping every index during a huge initial load without measurement

Consequence:

```text
extra write/index work
```

Correct mental model:

```text
measure index strategy
```

---

## Anti-pattern 8 — Disabling triggers/constraints blindly

Consequence:

```text
correctness invariants may disappear
```

Correct mental model:

```text
understand exactly what is being disabled
```

---

## Anti-pattern 9 — Ignoring type/format semantics

Consequence:

```text
silent or hard-to-debug data corruption
```

Correct mental model:

```text
loading is a data-contract problem
```

---

## Anti-pattern 10 — Treating COPY success as business-data success

Consequence:

```text
transport succeeded
but semantics are wrong
```

Correct mental model:

```text
transport validation ≠ business validation
```

---

## Anti-pattern 11 — Retrying malformed data forever

Consequence:

```text
same failure
repeated endlessly
```

Correct mental model:

```text
classify data errors separately from transient infrastructure failures
```

---

## Anti-pattern 12 — Assuming the fastest raw loader is the best architecture

Consequence:

```text
fast transport
but poor recovery/observability/idempotency
```

Correct mental model:

```text
performance is one production requirement among several
```

---

# 83. Bulk-Loading Design Patterns

## Pattern A — Small Load

```text
small dataset
   ↓
executemany()
```

Use when simplicity and moderate throughput are appropriate.

## Pattern B — Larger Batch

```text
larger dataset
   ↓
multi-row INSERT / COPY
```

Choose based on benchmark evidence.

## Pattern C — File Ingestion

```text
Parquet
   ↓
bounded batch reader
   ↓
COPY staging
```

## Pattern D — Safe Target Update

```text
staging
   ↓
validate
   ↓
MERGE/upsert
```

## Pattern E — Bad-Row Workflow

```text
invalid
   ↓
quarantine
```

## Pattern F — Arrow-Native Pipeline

```text
Arrow
   ↓
ADBC
   ↓
PostgreSQL
```

No pattern is universally correct.

---

# 84. COPY vs `executemany()` Decision Framework

# How to Choose a Loading Method

Ask:

1. How many rows?
2. How wide are the rows?
3. Where does the data come from?
4. Is the source already Arrow/Parquet?
5. How much Python conversion is required?
6. What throughput is required?
7. How important is easy debugging?
8. How severe are malformed-row problems?
9. Is bounded memory required?
10. Is staging/validation/MERGE required?
11. How much database capacity is available?
12. What does the benchmark show?

Use this model:

```text
Workload
+
data format
+
database capacity
+
correctness
+
recovery
+
measurement
```

Do not ask:

> “Which tool wins?”

Ask:

> “Which loading path removes unnecessary work while preserving the required operational behavior?”

---

# 85. Bulk-Loading Decision Tree

```text
How much data?
       ↓
small
  → execute / executemany

large
  ↓
structured file?
  → Parquet / Arrow / CSV
       ↓
Need PostgreSQL bulk protocol?
  → COPY

Need Arrow-native integration?
  → evaluate ADBC

Need validation + controlled target mutation?
  → staging → validate → MERGE

Need huge initial load?
  → evaluate indexes / constraints / triggers / transaction strategy

Need exact PostgreSQL-specific behavior?
  → COPY / psycopg path may provide the required control
```

> This is a reasoning framework, not a universal recipe.

---

# 86. Code Review Checklist

# Bulk Loader Code Review Checklist

## Input

- Is the input schema explicit?
- Are types controlled?
- Is the whole dataset materialized unnecessarily?
- Is the source format clearly defined?

## Loading

- Is row-by-row execution being used unnecessarily?
- Is `executemany()` appropriate?
- Is multi-row INSERT appropriate?
- Is COPY appropriate?
- Is binary COPY justified?

## Transactions

- What is the transaction boundary?
- Is rollback scope acceptable?
- Is restartability considered?

## Staging

- Is staging required?
- Are data-quality checks run before final target mutation?
- Can invalid data be quarantined?

## Performance

- Are indexes understood?
- Are constraints understood?
- Are triggers understood?
- Is batch size measured?
- Is `ANALYZE` considered?

## Reliability

- What happens on malformed input?
- What happens on connection failure?
- Can the load be safely retried?

## Idempotency

- What happens if the same file arrives twice?

## Observability

- Are rows read/loaded/rejected tracked?
- Is duration recorded?
- Are batch failures visible?
- Is target merge time visible?

---

# 87. Testing Strategy

Test at multiple levels.

## Correctness

- valid rows
- empty input
- one-row input
- large input
- NULL
- duplicate key
- constraint violation

## Format

- delimiter edge cases
- quote edge cases
- embedded newline
- invalid encoding
- timestamp formats
- timezone offsets
- Decimal precision
- UUID
- array
- JSON

## Reliability

- connection loss
- process crash
- partial load
- retry
- database restart

## Idempotency

- same file once
- same file twice
- same logical load with retry

## Staging

- row-count reconciliation
- validation failure
- quarantine
- MERGE correctness

## Performance

- benchmark methods
- measure memory
- measure throughput
- measure transaction behavior

Representative pytest-style example:

```python
def test_duplicate_file_is_idempotent(database):
    run_load(database, "orders.parquet", load_id="orders-001")
    first_count = read_target_count(database)

    run_load(database, "orders.parquet", load_id="orders-001")
    second_count = read_target_count(database)

    assert second_count == first_count
```

Test the real PostgreSQL behavior for integration tests.

---

# 88. Data Contract Thinking

Bulk loading is not only a performance problem.

It is also a data-contract problem.

Define:

- schema
- types
- nullability
- encoding
- delimiters
- quote rules
- timestamp semantics
- required columns
- uniqueness expectations
- numeric precision

Think:

```text
Source contract
      ↓
loader contract
      ↓
PostgreSQL target contract
```

A fast loader that changes the meaning of the data is a failed loader.

---

# 89. Production Scenarios

## Scenario A — One-Million-Row Nightly Load

Compare:

```text
executemany()
multi-row INSERT
COPY
```

Use the benchmark to make the decision.

---

## Scenario B — Fifty-Million-Row Initial Load

Focus on:

```text
staging
batching
index strategy
constraints
ANALYZE
recovery
```

---

## Scenario C — Parquet Ingestion

Use:

```text
Parquet
→ bounded reader
→ COPY
→ staging
```

---

## Scenario D — Bad Supplier Data

Use:

```text
COPY failure
→ isolate bad batch
→ quarantine
→ continue valid data
```

---

## Scenario E — Duplicate File Delivery

Use:

```text
stable load identity
+
idempotent target logic
```

---

## Scenario F — Financial Data

Use:

```text
Decimal
→ numeric
```

and validate precision.

---

## Scenario G — UTC Timestamps

Make the timezone contract explicit.

---

## Scenario H — Database Restart

Understand which work was:

```text
committed
```

and which work was:

```text
uncommitted
```

Then define the restart boundary.

---

# 90. Production-Oriented Bulk Loader Project

# Production-Oriented Bulk Loader

Assume a Parquet file contains millions of orders.

Requirements:

- secure database connection
- bounded-memory reader
- staging table
- COPY ingestion
- validation
- bad-row quarantine
- MERGE/upsert
- idempotent rerun
- reconciliation
- load audit
- performance measurement

Architecture:

```text
Parquet
   ↓
bounded-memory reader
   ↓
staging_orders
   ↑
COPY
   ↓
validation
   ├── valid
   │     ↓
   │   MERGE
   │     ↓
   │   orders
   │
   └── invalid
         ↓
     rejected_rows
```

Record:

```text
load_id
rows_read
rows_loaded
rows_rejected
duration
batch_count
MERGE duration
validation duration
status
```

The project is not complete until you can explain:

```text
what happens
when the loader fails,
restarts,
and sees the same file again.
```

---

# 91. Failure-Injection Matrix

| Failure | Staging state | Target state | Recovery concern |
| --- | --- | --- | --- |
| malformed row | COPY batch fails | unchanged by failed COPY | isolate bad data |
| invalid timestamp | COPY batch fails | unchanged by failed COPY | fix/route invalid input |
| numeric overflow | COPY batch fails | unchanged by failed COPY | type contract |
| duplicate key in target | staging may succeed | MERGE fails | target correctness |
| connection loss | transaction may roll back | depends on committed state | retry boundary |
| MERGE failure | staging may remain | target partially/fully unchanged depending on transaction | inspect state |
| process crash after staging | staging may remain | target may be unchanged | resume safely |
| duplicate file | staging repeats | should not duplicate logical target state | idempotency |

Never infer the exact state of a failed workflow without inspecting it.

---

# 92. COPY Data Validation Checklist

Before COPY, where practical, validate:

- column count
- expected schema
- encoding
- required values
- timestamp format
- numeric range
- UUID format
- JSON shape
- array element type
- file integrity

But do not remove database constraints.

Think:

```text
pre-validation
+
database constraints
```

rather than:

```text
pre-validation
instead of
database constraints
```

---

# 93. Large Initial Load vs Incremental Load

## Initial load

Often has:

- millions of rows
- little existing target data
- different index strategy
- different transaction model

## Incremental load

Often has:

- smaller batches
- existing target rows
- upsert/merge
- stronger idempotency requirements

Therefore:

```text
initial load architecture
```

and:

```text
incremental load architecture
```

may legitimately differ.

---

# 94. Observability Model

A simple operational model is:

```text
Input
  ↓
rows_read
  ↓
COPY
  ↓
rows_loaded_to_staging
  ↓
validation
  ↓
rows_rejected
  ↓
MERGE
  ↓
target_changes
```

Metrics should let you locate the bottleneck.

If:

```text
COPY = 10 seconds
MERGE = 4 minutes
```

then:

```text
COPY is not the main optimization target.
```

This principle prevents endless micro-optimization of the wrong stage.

---

# 95. Performance Bottleneck Migration

A common journey is:

```text
row-by-row
    ↓
Python/network bottleneck
```

then:

```text
executemany()
    ↓
database/index bottleneck
```

then:

```text
COPY
    ↓
target MERGE bottleneck
```

That is not failure.

It is what happens when you remove one bottleneck and expose the next one.

The correct response is measurement.

---

# 96. Production Hardening Questions

Before shipping a loader, answer:

```text
What is the source format?
What is the target schema?
What is the batch size?
What is the transaction boundary?
What is the throughput target?
What is the memory budget?
What happens on a bad row?
What happens on a connection failure?
What happens on a duplicate file?
Where is staging?
How is data validated?
How is target state reconciled?
How is the load observed?
How can it be restarted?
How can it be rerun safely?
```

---

# 97. Interview Questions

## Basic

1. Why are row-by-row inserts slow?
2. What does `executemany()` do?
3. What is PostgreSQL COPY?
4. What is the difference between INSERT and COPY?
5. Why does one transaction usually reduce overhead?
6. What is a staging table?
7. What is binary COPY?

## Intermediate

1. How does a multi-row INSERT differ from `executemany()`?
2. Why can network round trips matter?
3. Why does batch size matter?
4. Why can COPY be faster?
5. What is `COPY FROM STDIN`?
6. What does `copy.write_row()` do?
7. Why use a generator for COPY input?
8. Why is staging useful?
9. Why can one malformed row fail a COPY batch?
10. What is idempotent loading?
11. Why might `ANALYZE` matter after a large load?

## Advanced

1. How would you design a 50-million-row Parquet → PostgreSQL ingestion pipeline?
2. How would you keep memory bounded?
3. How would you isolate malformed rows?
4. How would you compare COPY with ADBC?
5. What factors affect COPY performance?
6. When might a large initial load justify changing index strategy?
7. What are the risks of disabling triggers?
8. How would you design restartability?
9. How would you prove a load is idempotent?
10. How would you reconcile source rows, rejected rows, staging rows, and target changes?
11. How would you determine whether COPY or MERGE is the bottleneck?

---

# 98. Architecture Questions

1. Design a production Parquet → PostgreSQL ingestion system for 100 million rows.
2. When would you use `executemany()` instead of COPY?
3. How would you choose between COPY and ADBC?
4. How would you design staging tables?
5. How would you handle malformed records without replaying an enormous file unnecessarily?
6. How would you choose batch size?
7. How would you design idempotent loading?
8. How would you keep production queries available during a large load?
9. How would you decide whether indexes should remain during an initial load?
10. How would you monitor a bulk loader?
11. COPY succeeds but MERGE becomes the bottleneck. How would you investigate?
12. The loader is extremely fast but timestamps/Decimal/null semantics are wrong. How would you prevent that?
13. A file is delivered twice. How does your architecture avoid unintended duplicates?
14. A process crashes after staging but before MERGE. How does the next run recover?
15. How would you define the data contract for an external supplier feeding PostgreSQL?

Reason from:

```text
workload
+
data volume
+
input format
+
database capacity
+
correctness
+
data quality
+
restartability
+
observability
```

Do not answer these with “COPY wins.”

---

# 99. Final Checkpoint

Preserve the roadmap checkpoint:

- [ ] Explain the entire loading ladder.
- [ ] Explain why row-by-row inserts are expensive.
- [ ] Demonstrate one-transaction loading.
- [ ] Demonstrate `executemany()`.
- [ ] Demonstrate multi-row INSERT.
- [ ] Demonstrate COPY from Python.
- [ ] Use `copy.write_row()`.
- [ ] Explain text/CSV COPY.
- [ ] Explain binary COPY.
- [ ] Use a generator as input.
- [ ] Stream Parquet into staging.
- [ ] Explain bounded-memory loading.
- [ ] Implement staging → validation → MERGE.
- [ ] Design idempotent loading.
- [ ] Run the same file twice and verify behavior.
- [ ] Explain why one bad row can fail a COPY batch.
- [ ] Use batch splitting to diagnose malformed data.
- [ ] Quarantine rejected rows.
- [ ] Explain NULL markers and delimiter/quote issues.
- [ ] Explain timezone and Decimal issues.
- [ ] Discuss indexes, constraints, triggers, and `ANALYZE`.
- [ ] Explain pandas loading.
- [ ] Explain a custom pandas COPY method.
- [ ] Explain Polars `write_database`.
- [ ] Explain ADBC ingestion.
- [ ] Compare COPY and ADBC.
- [ ] Explain server-side COPY awareness.
- [ ] Explain DuckDB/PostgreSQL movement awareness.
- [ ] Benchmark loading methods on one million rows.
- [ ] Compare prediction with measurement.
- [ ] Explain why no benchmark number should be fabricated.
- [ ] Explain how the target load becomes observable and restartable.

The learner must demonstrate implementation and reasoning, not memorization.

---

# 100. Common Mistakes

### Mistake 1

Assuming `executemany()` is automatically equivalent to COPY.

### Mistake 2

Assuming COPY means every input is automatically valid.

### Mistake 3

Loading directly into final production tables without a validation boundary.

### Mistake 4

Using one huge batch without considering memory or rollback scope.

### Mistake 5

Using one tiny batch without measuring the throughput cost.

### Mistake 6

Dropping indexes without understanding correctness or availability implications.

### Mistake 7

Disabling triggers or constraints just because they add overhead.

### Mistake 8

Treating CSV formatting as trivial.

### Mistake 9

Converting Decimal to float accidentally.

### Mistake 10

Dropping timezone information silently.

### Mistake 11

Materializing an entire Parquet file.

### Mistake 12

Retrying malformed data indefinitely.

### Mistake 13

Assuming ADBC and COPY have identical type semantics.

### Mistake 14

Calling the fastest benchmark “best architecture.”

### Mistake 15

Not making duplicate-file behavior explicit.

---

# 101. Final Mental Model

## The Bulk-Loading Mental Model

```text
Input data
    ↓
Reader / generator
    ↓
Batching
    ↓
Loading method
    ↓
Staging
    ↓
Validation
    ↓
MERGE / upsert
    ↓
Target
```

### Loading methods

```text
Single INSERT
    ↓
Transaction
    ↓
executemany()
    ↓
Multi-row INSERT
    ↓
COPY
    ↓
Binary COPY
```

### Reliability

```text
throughput
+
bounded memory
+
validation
+
idempotency
+
recovery
+
observability
```

### Key distinction

```text
Fast raw loading
        ≠
production-grade ingestion
```

---

# 102. Final Review

## What You Now Understand

You should now understand:

- the loading ladder
- single inserts
- transaction batching
- `executemany()`
- multi-row INSERT
- COPY
- binary COPY
- generators
- Parquet → COPY
- staging
- validation
- MERGE
- batch sizing
- commit frequency
- idempotency
- bad-row handling
- quarantine
- type and format issues
- indexes
- constraints
- triggers
- `ANALYZE`
- pandas
- Polars
- ADBC
- server-side COPY awareness
- DuckDB/PostgreSQL extension awareness
- warehouse bulk-load awareness
- benchmarking
- production observability

## What You Can Implement

You should be able to:

- implement multiple loading methods
- benchmark them
- stream Parquet into PostgreSQL
- use staging
- validate data
- merge into targets
- quarantine malformed records
- keep memory bounded
- make repeated loads idempotent
- compare COPY and ADBC
- design production load workflows

## What You Can Debug

You should be able to investigate:

- slow row-by-row loads
- unexpected `executemany()` behavior
- oversized multi-row statements
- COPY failures
- bad timestamps
- Decimal precision problems
- NULL marker problems
- CSV delimiter/quote failures
- MERGE bottlenecks
- duplicate loads
- excessive memory usage
- partial loads
- connection failures

## What Comes Next

Topic 10 focuses on **server-side cursors and streaming large results from PostgreSQL into Python/Parquet with bounded memory**.

This topic has intentionally focused on moving data **into PostgreSQL**. Do not turn the loader examples above into a full server-side cursor extraction course.

---

# 103. Production Rules to Remember

1. Do not load millions of rows one INSERT at a time without a deliberate reason.
2. Understand the loading ladder.
3. Use transactions deliberately.
4. Use `executemany()` when it fits the workload.
5. Use PostgreSQL COPY when high-volume bulk movement calls for it.
6. Keep input memory bounded.
7. Prefer staging when validation and controlled target mutation are required.
8. Treat COPY success as transport success, not automatically data-quality success.
9. Design bad-row handling deliberately.
10. Respect NULL, CSV, timestamp, UUID, array, JSON, and Decimal semantics.
11. Consider indexes, constraints, triggers, and `ANALYZE`.
12. Make repeated loads idempotent where the workflow requires safe reruns.
13. Measure batch size rather than guessing.
14. Benchmark methods on the same workload.
15. Track rows read, loaded, rejected, duration, and failures.
16. Choose the ingestion method based on workload and operational requirements, not ideology.

---

# 104. Code Quality Requirements

Every production-oriented example in this module should:

- use Python 3.12+
- use psycopg 3 syntax
- use correct PostgreSQL COPY syntax
- use parameterized SQL for values
- avoid hard-coded credentials
- use resource-safe context managers
- use explicit target columns
- make memory considerations visible
- use realistic transaction boundaries
- distinguish training examples from production patterns
- avoid fabricated benchmark results
- avoid unsupported performance claims
- explain database-side effects
- explain data-quality implications

For intentionally poor examples:

```text
⚠️ INTENTIONALLY INEFFICIENT / UNSAFE TRAINING EXAMPLE
```

For recommended patterns:

```text
✅ PRODUCTION-ORIENTED PATTERN
```

---

# 105. Important Scope Boundaries

This topic must stay focused on loading data **into PostgreSQL**.

Do not re-teach in depth:

- transaction engineering
- connection pooling
- SQLAlchemy Core
- SQLAlchemy ORM
- Alembic

Use them as prerequisites.

The next topic is:

```text
10-server-side-cursors-and-streaming-large-results.md
```

Therefore do not teach:

- full server-side cursor implementation
- detailed large-result streaming from PostgreSQL
- extraction-oriented memory architecture
- full PostgreSQL → Python/Parquet extraction pipelines

Parquet is used here as an **input source** for bulk loading.

---

# 106. Final Engineering Mindset

Do not ask:

> “What is the fastest way to INSERT rows?”

Ask:

```text
What is the actual data path?
What is the bottleneck?
What loading method removes unnecessary work?
How do I validate the data?
What happens when one row is bad?
How do I recover?
What happens when the same file arrives twice?
How much database capacity does the load consume?
How do I keep memory bounded?
How do I prove the method works at production scale?
```

The correct production mindset is:

```text
Different loading methods exist
because they optimize different parts
of the data-movement path.
```

A production-grade loader combines:

```text
Throughput
+
bounded memory
+
validation
+
idempotency
+
recovery
+
observability
```

That is the difference between:

```text
fast data insertion
```

and:

```text
production-grade data ingestion
```

The learner should now be able to defend a bulk-loading architecture in:

- production planning
- code review
- architecture review
- performance investigations
- data-quality reviews
- pipeline design
- technical interviews
