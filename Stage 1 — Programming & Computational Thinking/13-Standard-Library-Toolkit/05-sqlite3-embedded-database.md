# SQLite with Python's `sqlite3`: Embedded Databases for Reliable Data Pipelines

> **Target:** Python 3.12+ · **Scope:** the Python standard-library `sqlite3` module and SQLite as an embedded database.  
> **Prerequisites:** basic SQL, Python functions and exceptions, `pathlib`, file handling, `pytest`, logging, and the earlier lessons on safe writes and idempotency.

## Learning objectives

By the end of this lesson, you should be able to:

- Explain when SQLite is a good fit and when a client-server database is preferable.
- Create file-backed and in-memory databases; use cursors and parameterized CRUD operations.
- Design tables with constraints, foreign keys, indexes, and useful row representations.
- Understand connection context managers, transaction boundaries, rollback, and Python 3.12 transaction controls.
- Use upserts, CTEs, window functions, and optional JSON support without assuming every SQLite build is identical.
- Diagnose lock contention and select appropriate WAL, timeout, and threading settings.
- Back up a database, open it read-only, migrate its schema, and use custom SQL functions safely.
- Build an idempotent batch-ingestion pattern and test it against isolated temporary databases.

## 1. Prerequisites and roadmap placement

This is Lesson 05 in **Stage 1 — Programming & Computational Thinking → Module 13 — Standard Library Toolkit**. The module roadmap places it after iteration/operator tools, file and archive operations, and safe subprocess use, and before hashing, configuration, networking, and runtime utilities.

Relevant earlier skills:

| Prior skill | Why it matters here |
|---|---|
| SQL basics | Tables, predicates, joins, constraints, and query plans are SQL concepts, not Python APIs. |
| `pathlib` and file operations | File-backed databases have paths and need sensible directory/permission handling. |
| Exceptions and context managers | Transactions need explicit success/failure behavior and reliable cleanup. |
| Safe writes and idempotency | A pipeline must tolerate retries without duplicating durable effects. |
| `pytest` and `tmp_path` | Tests should use isolated, disposable database files. |
| Logging and configuration | Diagnostics must be useful without logging secrets or sensitive data. |

The focus is **embedded SQLite**. This lesson is not a general database course and does not teach PostgreSQL administration; the later client-server database material builds on these fundamentals.

## 2. Database fundamentals

### What SQLite is

SQLite is a relational database engine embedded in the application process. A Python program calls the SQLite library directly; there is no separate database server to install or administer. A database is commonly stored in one file, although journal/WAL sidecar files may also appear while connections are active.

**Good fits:** local job state, deduplication keys, a small catalog, offline tools, test fixtures, local caches, desktop applications, and single-host data pipelines.

**Poor fits:** workloads requiring many simultaneous writers, coordinated writes across multiple hosts over a network filesystem, centralized access control, or a database service shared by many independently deployed applications. SQLite permits multiple readers but only one writer at a time for a database file. A client-server engine is often a better fit when write concurrency or remote access is a core requirement.

### Connect to a database

```python
from contextlib import closing
from pathlib import Path
import sqlite3

# In-memory database: useful for examples and isolated tests.
with closing(sqlite3.connect(":memory:")) as con:
    with con:  # transaction boundary; closing() handles connection lifetime
        con.execute("CREATE TABLE sample (id INTEGER PRIMARY KEY, label TEXT NOT NULL)")
        con.execute("INSERT INTO sample(label) VALUES (?)", ("demo",))
    print(con.execute("SELECT label FROM sample").fetchone())
# Output: ('demo',)

# File-backed database: parent directory should already exist or be created intentionally.
db_path = Path("state") / "pipeline.sqlite3"
db_path.parent.mkdir(parents=True, exist_ok=True)
con = sqlite3.connect(db_path, timeout=5.0)
try:
    con.execute("CREATE TABLE IF NOT EXISTS heartbeat (name TEXT PRIMARY KEY)")
    con.commit()
finally:
    con.close()
```

`sqlite3.connect()` creates a database file if the path does not exist and the parent directory is available. `timeout` controls how long SQLite waits for a lock before raising `OperationalError`; it is not a general query execution timeout. Always close long-lived connections deliberately.

### A connection context manager does not close the connection

`with con:` manages a transaction: on normal exit it commits an open transaction; when an exception escapes it rolls back an open transaction. It **does not close** `con`. Use `contextlib.closing(con)` or an explicit `try/finally` if you want automatic closure.

```python
from contextlib import closing
import sqlite3

with closing(sqlite3.connect(":memory:")) as con:
    with con:
        con.execute("CREATE TABLE t (value INTEGER)")
        con.execute("INSERT INTO t VALUES (?)", (7,))
    print(con.execute("SELECT value FROM t").fetchone())
# The outer closing() closes the connection.
# Output: (7,)
```

A context manager does not magically make a sequence of separate statements atomic unless those statements are inside the same transaction boundary. For example, do not commit each row in a batch if all-or-nothing batch semantics are required.

## 3. Beginner operations: CRUD and parameterized SQL

### Create, insert, query, update, and delete

`execute()` runs one SQL statement. `executemany()` reuses a statement for a sequence of parameter sets. `fetchone()` returns one row or `None`; `fetchall()` materializes all remaining rows; iterating the cursor retrieves rows incrementally.

```python
import sqlite3

con = sqlite3.connect(":memory:")
try:
    con.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1))
        )
    """)
    con.executemany(
        "INSERT INTO users(email, active) VALUES (?, ?)",
        [("ada@example.test", 1), ("lin@example.test", 0)],
    )
    con.commit()

    row = con.execute(
        "SELECT id, email, active FROM users WHERE email = ?",
        ("ada@example.test",),
    ).fetchone()
    print(row)
    # Output: (1, 'ada@example.test', 1)

    con.execute("UPDATE users SET active = ? WHERE email = ?", (0, "ada@example.test"))
    con.execute("DELETE FROM users WHERE email = ?", ("lin@example.test",))
    con.commit()
    print(list(con.execute("SELECT email, active FROM users ORDER BY id")))
    # Output: [('ada@example.test', 0)]
finally:
    con.close()
```

### Parameterize values; never interpolate untrusted values into SQL

The `?` placeholder represents a **value**, not SQL syntax. The parameter sequence must match the number of placeholders.

```python
import sqlite3

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT NOT NULL)")
con.execute("INSERT INTO users(email) VALUES (?)", ("real@example.test",))
email = "x' OR 1=1 --"
row = con.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
print(row)
# Output: None — the payload is a value, not SQL syntax.
con.close()
```

The unusual input is treated as data, not executable SQL. Avoid `f"SELECT ... WHERE email = '{email}'"`: string interpolation can turn user input into SQL syntax. Parameterization is both safer and usually clearer.

**Identifiers are different.** You cannot bind a table or column name with `?`. For dynamic identifiers, choose from a fixed allow-list and quote the selected identifier correctly; do not accept arbitrary SQL fragments from callers.

```python
import sqlite3

ALLOWED_SORT_COLUMNS = {"email", "active"}

def list_users(con: sqlite3.Connection, sort_by: str) -> list[tuple]:
    if sort_by not in ALLOWED_SORT_COLUMNS:
        raise ValueError("unsupported sort column")
    # Identifier is selected from a fixed allow-list; values remain parameterized.
    return list(con.execute(f'SELECT email, active FROM users ORDER BY "{sort_by}"'))

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE users (email TEXT, active INTEGER)")
con.executemany("INSERT INTO users VALUES (?, ?)", [("b@example.test", 1), ("a@example.test", 0)])
print(list_users(con, "email"))
# Output: [('a@example.test', 0), ('b@example.test', 1)]
try:
    list_users(con, "email; DROP TABLE users")
except ValueError:
    print("rejected")
    # Output: rejected
con.close()
```

The f-string above is safe only because `sort_by` must exactly match a known identifier from the allow-list. Never generalize this pattern to untrusted SQL fragments.

### Cursor iteration versus `fetchall()`

- Use `fetchone()` when you need one row.
- Use `fetchall()` when the result is known to be small and materializing it is useful.
- Iterate the cursor for potentially large result sets to avoid creating a second in-memory copy of every row.

`executemany()` is a convenient statement-reuse API, not a promise of one network round trip or a specific speedup. For SQLite, putting a batch inside one transaction is often much more important than committing each row.

## 4. Transactions and failure semantics

A transaction groups related changes so they commit together or roll back together. This matters when writing an output row and its deduplication/checkpoint record: if one succeeds and the other fails, the pipeline can become inconsistent.

```python
import sqlite3

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE accounts (name TEXT PRIMARY KEY, balance INTEGER NOT NULL CHECK (balance >= 0))")
con.commit()
try:
    with con:
        con.execute("INSERT INTO accounts VALUES (?, ?)", ("team-a", 100))
        con.execute("INSERT INTO accounts VALUES (?, ?)", ("team-b", -5))  # CHECK fails
except sqlite3.IntegrityError as exc:
    print(type(exc).__name__)
    # Output: IntegrityError

print(con.execute("SELECT name FROM accounts").fetchall())
# Output: [] — the first insert was rolled back too.
con.close()
```

The exception must escape the `with con:` block for its transaction to roll back. If code catches and suppresses the exception *inside* the block, the context manager may see a normal exit and commit earlier successful statements. Catch errors outside the transaction when all-or-nothing behavior is desired.

### Python 3.12 transaction configuration

Python 3.12 added the `Connection.autocommit` attribute and parameter. Do not confuse this Python setting with SQLite's low-level autocommit state.

- `autocommit=sqlite3.LEGACY_TRANSACTION_CONTROL` preserves the historical behavior governed by `isolation_level` (the default in Python 3.12+ unless changed by a future default).
- `autocommit=False` requests PEP 249-style transaction control: Python keeps a transaction open and uses `BEGIN DEFERRED` after commits/rollbacks.
- `autocommit=True` uses SQLite autocommit mode; Python's `commit()` and `rollback()` methods have no effect in that mode. Explicit SQL transaction statements can still be used when appropriate.
- `isolation_level` affects transaction behavior only in legacy transaction-control mode. It is ignored when `autocommit` is not `LEGACY_TRANSACTION_CONTROL`.
- The connection context manager does not itself start a transaction. It commits or rolls back a transaction that is open when the block exits; with `autocommit=True` it has no effect. Under `autocommit=False`, Python keeps a transaction open and opens a new one after commit/rollback, so examples that issue their own `BEGIN IMMEDIATE` need to account for that mode.

For a teaching example, the default connection and `with con:` are often sufficient. For production code, select a transaction mode explicitly when its semantics matter and test it against the Python versions you support.

### `BEGIN IMMEDIATE`

A deferred transaction may read first and only later discover it cannot upgrade to a write transaction. `BEGIN IMMEDIATE` requests a write transaction at the start, surfacing contention earlier. It can reduce surprise in short read-modify-write units, but it also reserves the single writer slot sooner. Do not hold it while doing network calls or lengthy computation.

```python
import sqlite3

con = sqlite3.connect("pipeline.sqlite3", timeout=2.0)
try:
    con.execute("CREATE TABLE IF NOT EXISTS counters (name TEXT PRIMARY KEY, value INTEGER NOT NULL)")
    con.execute("INSERT INTO counters(name, value) VALUES (?, 0) ON CONFLICT(name) DO NOTHING", ("processed",))
    con.commit()
    con.execute("BEGIN IMMEDIATE")
    con.execute("UPDATE counters SET value = value + 1 WHERE name = ?", ("processed",))
    con.commit()
    print(con.execute("SELECT value FROM counters WHERE name = ?", ("processed",)).fetchone())
finally:
    if con.in_transaction:
        con.rollback()
    con.close()
# Output on the first run: (1,); later runs increment the existing value.
```

Do not run `BEGIN IMMEDIATE` inside an already active transaction; SQLite will report that a transaction is already active. This example commits initialization separately, then uses a short explicit write transaction.

## 5. Row factories, dynamic typing, and schema design

### `sqlite3.Row` and custom row factories

```python
import sqlite3

con = sqlite3.connect(":memory:")
con.row_factory = sqlite3.Row
con.execute("CREATE TABLE jobs (job_id INTEGER PRIMARY KEY, status TEXT NOT NULL)")
con.execute("INSERT INTO jobs(status) VALUES (?)", ("ready",))
row = con.execute("SELECT job_id, status FROM jobs").fetchone()
print(row["status"], row["job_id"])
# Output: ready 1
con.close()
```

Set `row_factory` before creating cursors whose rows should use it. `sqlite3.Row` supports both index and case-insensitive name access with low overhead. A custom factory can convert rows into dataclasses or domain objects, but avoid creating complicated hidden conversion logic in a factory if it makes queries harder to debug.

```python
import sqlite3

def dict_factory(cursor: sqlite3.Cursor, row: tuple) -> dict[str, object]:
    return {column[0]: row[index] for index, column in enumerate(cursor.description)}

con = sqlite3.connect(":memory:")
con.row_factory = dict_factory  # applies to cursors created after this assignment
con.execute("CREATE TABLE sample (code TEXT, quantity INTEGER)")
con.execute("INSERT INTO sample VALUES (?, ?)", ("X-1", 3))
print(con.execute("SELECT code, quantity FROM sample").fetchone())
# Output: {'code': 'X-1', 'quantity': 3}
con.close()
```

### SQLite type affinity and `STRICT` tables

SQLite uses dynamic typing: the storage class belongs to the value, and column declarations generally establish affinity rather than enforcing a rigid type system. A column declared `INTEGER` can still accept values that do not behave like a strict integer in ordinary tables.

`STRICT` tables, available in SQLite **3.37.0+**, add stricter type enforcement for a limited set of declared type names (`INT`, `INTEGER`, `REAL`, `TEXT`, `BLOB`, `ANY`). They are useful when malformed types must be rejected, but they do not replace business validation or constraints.

```sql
CREATE TABLE measurements (
    measurement_id INTEGER PRIMARY KEY,
    sensor TEXT NOT NULL,
    reading REAL NOT NULL CHECK (reading >= 0)
) STRICT;
```

Check `sqlite3.sqlite_version_info` when depending on a SQLite feature. The Python version does not uniquely determine the linked SQLite library version.

### Adapters, converters, and timestamps

SQLite natively stores `NULL`, `INTEGER`, `REAL`, `TEXT`, and `BLOB`. Python's `sqlite3` can adapt custom Python values into SQLite-supported values and convert selected SQLite values back to Python objects. Converters are opt-in through `detect_types` and declared type names or column-name annotations.

```python
from datetime import datetime, timezone
import sqlite3

# Prefer explicit, portable timestamp representations.
now = datetime.now(timezone.utc)
iso_text = now.isoformat()
epoch_seconds = now.timestamp()
print(iso_text.endswith("+00:00"), isinstance(epoch_seconds, float))
# Output: True True

# Example of a custom adapter/converter for a small domain type.
class Point:
    def __init__(self, x: int, y: int) -> None:
        self.x, self.y = x, y

sqlite3.register_adapter(Point, lambda p: f"{p.x},{p.y}")
def convert_point(raw: bytes) -> Point:
    x_text, y_text = raw.decode("ascii").split(",")
    return Point(int(x_text), int(y_text))
sqlite3.register_converter("POINT", convert_point)

con = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
con.execute("CREATE TABLE points (value POINT)")
con.execute("INSERT INTO points VALUES (?)", (Point(2, 5),))
point = con.execute("SELECT value FROM points").fetchone()[0]
print((point.x, point.y))
# Output: (2, 5)
con.close()
```

The adapter/converter registries shown are process-global. Use unique declared type names and avoid registering conflicting conversions in reusable libraries. The example uses ASCII-safe text for clarity; for production types, define validation and a stable serialization format.

For timestamps, choose one convention and document it: ISO 8601 UTC text (for example, `2026-10-17T00:00:00+00:00`) is readable and sortable when formatted consistently; UTC epoch values are compact numeric instants. Avoid naive datetimes when timezone meaning matters. Python's historical default SQLite date/time adapters and converters are deprecated as of Python 3.12; explicit representations are recommended.

### Constraints and foreign keys

Use constraints to make invalid states difficult to store:

- `PRIMARY KEY`: identifies a row.
- `UNIQUE`: rejects duplicate values (subject to SQLite's NULL semantics).
- `NOT NULL`: disallows missing values.
- `CHECK`: validates a row-level condition.
- `FOREIGN KEY`: enforces a relationship when enabled.

SQLite foreign-key enforcement must be enabled for each connection unless configured otherwise by the build. Set it before beginning a transaction:

```python
import sqlite3

con = sqlite3.connect(":memory:")
con.execute("PRAGMA foreign_keys = ON")
assert con.execute("PRAGMA foreign_keys").fetchone()[0] == 1
con.executescript("""
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE
);
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    amount_cents INTEGER NOT NULL CHECK (amount_cents >= 0)
);
""")
con.execute("INSERT INTO customers(email) VALUES (?)", ("buyer@example.test",))
con.execute("INSERT INTO orders(customer_id, amount_cents) VALUES (?, ?)", (1, 500))
con.commit()
try:
    con.execute("INSERT INTO orders(customer_id, amount_cents) VALUES (?, ?)", (999, 500))
except sqlite3.IntegrityError:
    print("foreign key rejected")
    # Output: foreign key rejected
con.close()
```

A foreign-key pragma issued inside a transaction does not change enforcement. Put connection setup in one tested connection factory so every connection receives the same settings.

## 6. Upserts, deduplication, indexes, and SQL features

### Upserts

`INSERT ... ON CONFLICT ... DO UPDATE` performs an insert or updates the conflicting row. This UPSERT syntax requires SQLite **3.24.0+**. The special `excluded` name refers to the candidate row that would have been inserted. Check `sqlite3.sqlite_version_info` if you deploy to environments with older system SQLite libraries.

```python
import sqlite3

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE prices (sku TEXT PRIMARY KEY, cents INTEGER NOT NULL CHECK(cents >= 0))")
statement = """
INSERT INTO prices(sku, cents) VALUES (?, ?)
ON CONFLICT(sku) DO UPDATE SET cents = excluded.cents
"""
con.execute(statement, ("SKU-1", 250))
con.execute(statement, ("SKU-1", 275))
print(con.execute("SELECT sku, cents FROM prices").fetchall())
# Output: [('SKU-1', 275)]
con.close()
```

`INSERT OR IGNORE` suppresses certain constraint violations, including uniqueness conflicts. It can be useful for `seen_ids`, but it may also hide invalid data rejected by other constraints. Prefer a targeted `ON CONFLICT(key) DO NOTHING` when the intent is specifically to ignore duplicate keys.

```python
import sqlite3

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE seen_ids (event_id TEXT PRIMARY KEY)")
con.execute("INSERT OR IGNORE INTO seen_ids(event_id) VALUES (?)", ("evt-1",))
con.execute("INSERT OR IGNORE INTO seen_ids(event_id) VALUES (?)", ("evt-1",))
print(con.execute("SELECT COUNT(*) FROM seen_ids").fetchone())
# Output: (1,)
con.close()
```

Use this broad form only when suppressing all applicable ignored constraint failures is acceptable. The targeted `ON CONFLICT(event_id) DO NOTHING` form better documents that only a duplicate event ID is expected.

### Indexes and query plans

An index can speed up filters, joins, and ordering, at the cost of storage and extra work on inserts/updates/deletes. Index columns that match real query patterns; do not index every column by default.

```sql
CREATE INDEX idx_events_created_at ON events(created_at);
```

Inspect a query plan using `EXPLAIN QUERY PLAN`:

```python
import sqlite3

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE prices (sku TEXT PRIMARY KEY, cents INTEGER NOT NULL)")
con.execute("INSERT INTO prices VALUES (?, ?)", ("SKU-1", 250))
plan = con.execute(
    "EXPLAIN QUERY PLAN SELECT sku FROM prices WHERE sku = ?", ("SKU-1",)
).fetchall()
print(bool(plan))
# Output: True
con.close()
```

The exact plan text and numeric details can vary by SQLite version and schema statistics. Tests should not usually assert the full output string. Use representative data and measurements to decide whether an index helps.

### CTEs, window functions, and JSON functions

Common table expressions (CTEs; available since SQLite 3.8.3) give a query a named intermediate result. Window functions (available in SQLite 3.25.0+) compute values across related rows without collapsing each group into one row. They are useful for ranking, rolling comparisons, and latest-record selection.

```sql
WITH ranked AS (
    SELECT customer_id, order_id, amount_cents,
           ROW_NUMBER() OVER (
               PARTITION BY customer_id
               ORDER BY order_id DESC
           ) AS rn
    FROM orders
)
SELECT customer_id, order_id, amount_cents
FROM ranked
WHERE rn = 1;
```

SQLite supports window functions in modern versions; verify the linked SQLite version for your minimum runtime. JSON functions such as `json_extract()` are available in modern SQLite builds (JSON support is built in by default from SQLite 3.38.0, but builds can differ and JSON may be omitted at compile time).

```python
import sqlite3

con = sqlite3.connect(":memory:")
try:
    value = con.execute("SELECT json_extract(?, '$.status')", ('{"status":"ok"}',)).fetchone()[0]
except sqlite3.OperationalError as exc:
    raise RuntimeError("this SQLite build lacks the required JSON function") from exc
finally:
    con.close()
print(value)
# Output when JSON support is available: ok
```

Avoid making optional SQL features implicit assumptions in reusable code; check capability at startup or handle the specific missing-feature error.

## 7. Performance and maintenance

### Batch inserts and prepared-statement reuse

Group many related inserts in one transaction. SQLite's Python wrapper caches prepared statements by default, and `executemany()` is convenient for repeated parameter sets. Performance depends on data, disk, indexes, durability settings, and transaction size; no universal multiplier is guaranteed.

```python
import sqlite3

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE inventory (name TEXT PRIMARY KEY, quantity INTEGER NOT NULL)")
rows = [(f"item-{i}", i) for i in range(1_000)]
with con:
    con.executemany("INSERT INTO inventory(name, quantity) VALUES (?, ?)", rows)
print(con.execute("SELECT COUNT(*) FROM inventory").fetchone())
# Output: (1000,)
con.close()
```

For very large batches, choose a bounded batch size to balance throughput, lock duration, memory, and rollback cost. Create indexes required by correctness first; consider delaying nonessential secondary indexes until bulk loading finishes, then measure.

### `ANALYZE` and `VACUUM`

- `ANALYZE` gathers statistics that can help the query planner choose indexes.
- `VACUUM` rebuilds the database file and can reclaim free pages, but it may need extra disk space and can be expensive. It should not be run blindly after every delete.

Run maintenance based on measured need and operational windows, not as a reflex.

### Backups and read-only connections

Use SQLite's backup API for a consistent database copy while the source connection is in use. A raw file copy of an active database can miss WAL content or capture an inconsistent set of files.

```python
from contextlib import closing
from pathlib import Path
import sqlite3

source_path = Path("pipeline.sqlite3")
backup_path = Path("pipeline-backup.sqlite3")
with closing(sqlite3.connect(source_path)) as source:
    with source:
        with closing(sqlite3.connect(backup_path)) as destination:
            source.backup(destination)

# Read-only URI connection. `uri=True` is required.
uri = f"file:{backup_path.resolve().as_posix()}?mode=ro"
with closing(sqlite3.connect(uri, uri=True)) as readonly:
    print(readonly.execute("PRAGMA query_only").fetchone())
# Output: (0,) — mode=ro makes the database read-only; query_only is a separate pragma.
```

`mode=ro` prevents writes through this connection. If a path contains URI-reserved characters, construct/quote the URI path carefully rather than concatenating arbitrary user input. A read-only connection is useful for reports and inspection jobs.

## 8. Concurrency, WAL, and lock handling

### WAL and pragmas

`PRAGMA journal_mode=WAL` usually lets readers continue reading a stable snapshot while a writer appends changes to the write-ahead log. It does **not** enable multiple simultaneous writers. WAL is generally intended for connections on the same host; it is not a solution for multi-host access over arbitrary network filesystems.

- `busy_timeout` controls how long SQLite waits for a lock before returning `SQLITE_BUSY`/`database is locked` in common cases.
- `synchronous` controls durability/performance trade-offs. `FULL` generally provides stronger durability than `NORMAL` in WAL mode, while the exact guarantee depends on filesystem and hardware honoring sync requests. Do not weaken it without understanding the loss window.

```python
import sqlite3

con = sqlite3.connect("pipeline.sqlite3", timeout=3.0)
try:
    mode = con.execute("PRAGMA journal_mode=WAL").fetchone()[0]
    con.execute("PRAGMA busy_timeout = 3000")
    con.execute("PRAGMA synchronous = FULL")
    print(mode.lower())  # Typically: wal
finally:
    con.close()
```

Configure connection-level pragmas for every connection where required. `journal_mode=WAL` is persistent for the database; `busy_timeout`, `foreign_keys`, and `synchronous` have connection-specific considerations. Validate the returned mode rather than assuming a pragma always succeeded.

### Connection per thread

By default, `sqlite3.connect()` sets `check_same_thread=True`: using a connection from another thread raises `ProgrammingError`. Create one connection per worker thread when practical. Setting `check_same_thread=False` disables that guard; it does **not** serialize access or make concurrent use of one connection automatically safe. If sharing is unavoidable, coordinate access and transaction boundaries with a lock and understand the SQLite library's threading mode.

### Bounded lock retries

Do not retry every `OperationalError` forever. A retry policy should be bounded, limited to a known transient lock condition, and should retry the **whole transaction** if the transaction was rolled back or cannot continue. Avoid retrying non-idempotent external side effects inside the same function.

```python
import random
import sqlite3
import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")

def _is_transient_lock_error(exc: sqlite3.OperationalError) -> bool:
    # Python 3.11+ exposes SQLite result codes. Extended result codes retain
    # the primary result in the low byte (for example, SQLITE_BUSY_SNAPSHOT).
    code = getattr(exc, "sqlite_errorcode", None)
    if code is not None:
        primary_code = code & 0xFF
        return primary_code in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED)
    # Fallback for older Python versions without sqlite_errorcode.
    message = str(exc).lower()
    return "locked" in message or "busy" in message

def retry_locked(operation: Callable[[], T], *, attempts: int = 4) -> T:
    if isinstance(attempts, bool) or not isinstance(attempts, int) or attempts < 1:
        raise ValueError("attempts must be a positive integer")
    for attempt in range(attempts):
        try:
            return operation()
        except sqlite3.OperationalError as exc:
            if not _is_transient_lock_error(exc):
                raise
            if attempt == attempts - 1:
                raise
            time.sleep(min(0.05 * (2 ** attempt), 0.5) + random.uniform(0, 0.02))
    raise AssertionError("unreachable")
```

This illustrative retry is deliberately bounded. In production, prefer checking SQLite error codes where supported by your Python/SQLite versions rather than matching localized error strings. `operation` must create a fresh, correctly scoped transaction or connection on each attempt; do not retry a partially applied transaction blindly.

### Demonstrating the single-writer constraint

```python
import sqlite3
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as directory:
    db = Path(directory) / "locks.db"
    first = sqlite3.connect(db, timeout=0.05)
    second = sqlite3.connect(db, timeout=0.05)
    first.execute("CREATE TABLE counter (value INTEGER)")
    first.commit()
    try:
        first.execute("BEGIN IMMEDIATE")  # first connection reserves writer slot
        try:
            second.execute("INSERT INTO counter VALUES (1)")
        except sqlite3.OperationalError as exc:
            print("second writer blocked:", "locked" in str(exc).lower() or "busy" in str(exc).lower())
            # Output: second writer blocked: True (on a normal local SQLite build)
        finally:
            first.rollback()
    finally:
        first.close()
        second.close()
```

The test uses a short timeout to make contention visible. Timing and exact exception text are platform/build dependent, so production diagnostics should use error codes when available. Do not hide lock contention by making the timeout extremely large without observing lock duration.

## 9. Schema migrations with `PRAGMA user_version`

`user_version` is an application-controlled integer stored in the database header. It is a lightweight migration marker, not a full migration framework. Apply migrations transactionally and make each migration's expected starting version explicit.

The following minimal example uses a connection in legacy transaction-control mode (the Python 3.12 default; specify `autocommit=sqlite3.LEGACY_TRANSACTION_CONTROL` explicitly if you need to pin the mode as defaults evolve) or `autocommit=True` with no active transaction. It refuses to run inside an existing transaction, acquires the writer slot before reading/updating schema state, and uses explicit SQL `COMMIT`/`ROLLBACK` so it also works with `autocommit=True`. Do not pass a connection configured with `autocommit=False` to this specific helper: that mode deliberately keeps a transaction open.

```python
import sqlite3

MIGRATIONS = {
    1: "CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)",
}

def migrate(con: sqlite3.Connection) -> None:
    if con.in_transaction:
        raise RuntimeError("migrate() requires a connection with no active transaction")
    con.execute("BEGIN IMMEDIATE")
    try:
        version = con.execute("PRAGMA user_version").fetchone()[0]
        latest = max(MIGRATIONS, default=0)
        if version > latest:
            raise RuntimeError(
                f"database schema version {version} is newer than this program"
            )
        if version < 1:
            con.execute(MIGRATIONS[1])
            con.execute("PRAGMA user_version = 1")
        con.execute("COMMIT")
    except BaseException:
        if con.in_transaction:
            con.execute("ROLLBACK")
        raise
```

For more than a few migrations, use explicit ordered migration functions, check the expected version before each step, test upgrades from every supported starting version, and document destructive changes. Avoid `executescript()` inside a transaction you expect it to preserve: its behavior can implicitly commit a pending transaction under legacy transaction control. Each migration should be tested against the transaction modes your application supports.

## 10. Custom SQL functions, aggregates, and collations

`create_function()` exposes a Python callable to SQL; `create_aggregate()` defines a class with `step()` and `finalize()`; `create_collation()` supplies text comparison rules. They can make domain-specific queries expressive, but Python callbacks execute inside database operations and can become performance bottlenecks.

```python
import sqlite3

con = sqlite3.connect(":memory:")
con.create_function("normalize_code", 1, lambda value: value.strip().upper() if value is not None else None, deterministic=True)
print(con.execute("SELECT normalize_code(?)", (" ab-12 ",)).fetchone()[0])
# Output: AB-12
con.close()
```

Only mark a function `deterministic=True` if equal inputs always produce equal outputs and it has no observable side effects. Custom functions are registered per connection. Avoid callbacks that perform I/O, mutate external state, or depend on ambient time when queries should be reproducible.

Aggregates and collations are also connection-level registrations. An aggregate class implements `step()` for each row and `finalize()` for the final result. A collation returns a negative integer, zero, or a positive integer to compare two strings. Keep callbacks deterministic and fast because SQLite invokes them while executing SQL.

```python
import sqlite3

class Span:
    def __init__(self):
        self.low = None
        self.high = None

    def step(self, value):
        if value is not None:
            self.low = value if self.low is None else min(self.low, value)
            self.high = value if self.high is None else max(self.high, value)

    def finalize(self):
        return None if self.low is None else self.high - self.low

con = sqlite3.connect(":memory:")
con.create_aggregate("span", 1, Span)
con.execute("CREATE TABLE samples (value INTEGER)")
con.executemany("INSERT INTO samples VALUES (?)", [(4,), (9,), (6,)])
print(con.execute("SELECT span(value) FROM samples").fetchone()[0])
# Output: 5

def unicode_nocase(left: str, right: str) -> int:
    a, b = left.casefold(), right.casefold()
    return (a > b) - (a < b)

con.create_collation("UNICODE_NOCASE", unicode_nocase)
con.execute("CREATE TABLE labels (value TEXT)")
con.executemany("INSERT INTO labels VALUES (?)", [("beta",), ("Alpha",), ("ALPHA",)])
print([row[0] for row in con.execute("SELECT value FROM labels ORDER BY value COLLATE UNICODE_NOCASE, value")])
# Output: ['ALPHA', 'Alpha', 'beta']
con.close()
```

A custom collation's ordering must be stable for the lifetime of indexes that use it. If the comparison implementation changes, rebuild affected indexes; otherwise their stored ordering may no longer match the callback.

## 11. Practical implementation: idempotent batch pipeline

A reliable ingestion transaction must store the deduplication marker and the durable output together. If the transaction fails, both should roll back. This mini-project accepts deterministic event records, validates them, stores each event once, and records processed IDs.

### Schema and application code

```python
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, TypedDict

class Event(TypedDict):
    event_id: str
    source: str
    amount_cents: int

SCHEMA = """
CREATE TABLE IF NOT EXISTS sources (
    source TEXT PRIMARY KEY,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
) STRICT;
CREATE TABLE IF NOT EXISTS seen_ids (
    event_id TEXT PRIMARY KEY,
    processed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
) STRICT;
CREATE TABLE IF NOT EXISTS event_totals (
    event_id TEXT PRIMARY KEY REFERENCES seen_ids(event_id),
    source TEXT NOT NULL REFERENCES sources(source),
    amount_cents INTEGER NOT NULL CHECK (amount_cents >= 0)
) STRICT;
"""

def connect_database(path: str | Path) -> sqlite3.Connection:
    # Pin the transaction mode relied on by process_batch() and this lesson.
    con = sqlite3.connect(
        path,
        timeout=5.0,
        autocommit=sqlite3.LEGACY_TRANSACTION_CONTROL,
    )
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    if con.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
        con.close()
        raise RuntimeError("SQLite foreign-key enforcement is unavailable")
    return con

def initialize_database(con: sqlite3.Connection) -> None:
    # executescript() can commit a pending transaction before running its script.
    # Refuse to take ownership of a caller's transaction.
    if con.in_transaction:
        raise RuntimeError("initialize_database() requires no active transaction")
    # Make the DDL transaction explicit instead of assuming `with con:` wraps it.
    try:
        con.executescript("BEGIN IMMEDIATE;\n" + SCHEMA + "\nCOMMIT;")
    except Exception:
        if con.in_transaction:
            con.rollback()
        raise

def validate_event(event: Event) -> None:
    if not isinstance(event["event_id"], str) or not event["event_id"].strip():
        raise ValueError("event_id must be a non-empty string")
    if not isinstance(event["source"], str) or not event["source"].strip():
        raise ValueError("source must be a non-empty string")
    # bool is a subclass of int, but is not an acceptable monetary amount here.
    if isinstance(event["amount_cents"], bool) or not isinstance(event["amount_cents"], int):
        raise ValueError("amount_cents must be an integer")
    if event["amount_cents"] < 0:
        raise ValueError("amount_cents must be >= 0")

def process_batch(con: sqlite3.Connection, events: Iterable[Event]) -> int:
    """Insert each event once; return the number of newly processed event IDs.

    The connection must use legacy transaction control and have no transaction
    already open; this function owns the transaction it commits or rolls back.
    The input iterable is consumed inside the transaction. Keep batches bounded so
    validation/iteration does not hold a writer lock for an unbounded duration.
    """
    if con.autocommit != sqlite3.LEGACY_TRANSACTION_CONTROL:
        raise RuntimeError("process_batch() requires LEGACY_TRANSACTION_CONTROL")
    if con.in_transaction:
        raise RuntimeError("process_batch() requires no active transaction")
    inserted = 0
    with con:
        for event in events:
            validate_event(event)
            marker = con.execute(
                "INSERT INTO seen_ids(event_id) VALUES (?) ON CONFLICT(event_id) DO NOTHING",
                (event["event_id"],),
            )
            if marker.rowcount == 0:
                existing = con.execute(
                    "SELECT source, amount_cents FROM event_totals WHERE event_id = ?",
                    (event["event_id"],),
                ).fetchone()
                if existing is None:
                    raise RuntimeError("checkpoint exists without its output row")
                if (existing["source"], existing["amount_cents"]) != (
                    event["source"], event["amount_cents"]
                ):
                    raise ValueError("event_id was already processed with a different payload")
                continue  # identical event already committed with its output
            con.execute("INSERT INTO sources(source) VALUES (?) ON CONFLICT(source) DO NOTHING", (event["source"],))
            con.execute(
                "INSERT INTO event_totals(event_id, source, amount_cents) VALUES (?, ?, ?)",
                (event["event_id"], event["source"], event["amount_cents"]),
            )
            inserted += 1
    return inserted

def get_total(con: sqlite3.Connection) -> int:
    row = con.execute("SELECT COALESCE(SUM(amount_cents), 0) AS total FROM event_totals").fetchone()
    return int(row["total"])
```

**Important transaction note:** `executescript()` can commit a pending transaction before running its script under legacy transaction control. Here `initialize_database()` is intended for schema setup, not mixed into an application transaction. For more elaborate migrations, use explicit migration transaction logic and verify behavior under the selected `autocommit` mode.

### Example run

```python
from tempfile import TemporaryDirectory
from pathlib import Path

sample_events: list[Event] = [
    {"event_id": "evt-1", "source": "batch-A", "amount_cents": 125},
    {"event_id": "evt-2", "source": "batch-A", "amount_cents": 300},
    {"event_id": "evt-1", "source": "batch-A", "amount_cents": 125},  # duplicate
]
with TemporaryDirectory() as directory:
    con = connect_database(Path(directory) / "events.sqlite3")
    try:
        initialize_database(con)
        print(process_batch(con, sample_events))
        print(process_batch(con, sample_events))
        print(get_total(con))
        # Output:
        # 2
        # 0
        # 425
    finally:
        con.close()
```

This provides **database-level idempotency** for the output represented by `event_totals`: identical repeated event IDs are skipped, while the same ID with a different source/amount is rejected rather than silently discarding a conflicting payload. If a checkpoint exists without its output row, processing also fails loudly. The marker and output are in one transaction. This does not make unrelated external side effects (sending email, calling an API, writing another database) atomic; use an outbox or another coordinated design when a transaction must trigger external work.

### Operational considerations

- Keep batches bounded. A generator that blocks on network I/O while inside `with con:` can hold a write transaction too long; fetch/validate a bounded batch before opening the write transaction when appropriate.
- The schema uses `STRICT`, so it requires SQLite 3.37.0+. If older linked SQLite versions are supported, provide a non-STRICT schema and explicit validation.
- `CURRENT_TIMESTAMP` is UTC text in SQLite's default format, but it has second precision. If higher precision or application-specific clock semantics matter, supply a consistent timestamp explicitly.
- `sources` is inserted in the same transaction as marker and output. If any later insert fails, all changes for the event/batch roll back.
- `connect_database()` pins `LEGACY_TRANSACTION_CONTROL`; `process_batch()` rejects other `autocommit` modes and already-open transactions. `initialize_database()` rejects an already-open transaction because `executescript()` can implicitly commit pending work. These guards prevent helpers from unexpectedly taking ownership of a caller's pending work. If your application needs `autocommit=False`, redesign the helpers around that transaction policy rather than mixing modes.

## 12. Tests with `pytest` and `tmp_path`

Tests should use a new database file per test, not a shared developer database. This suite exercises duplicate handling, rollback, invalid data, foreign keys, and repeated batch execution.

Save the application implementation from Section 11 in `pipeline_store.py`, then save this as `test_pipeline_store.py` in the same directory:

```python
import sqlite3
import pytest

from pipeline_store import connect_database, initialize_database, process_batch, get_total

@pytest.fixture
def db(tmp_path):
    con = connect_database(tmp_path / "test.sqlite3")
    initialize_database(con)
    try:
        yield con
    finally:
        con.close()

def event(event_id="e-1", source="s-1", amount_cents=100):
    return {"event_id": event_id, "source": source, "amount_cents": amount_cents}

def test_batch_is_idempotent(db):
    records = [event(), event("e-2", amount_cents=50)]
    assert process_batch(db, records) == 2
    assert process_batch(db, records) == 0
    assert get_total(db) == 150

def test_duplicate_in_same_batch_is_skipped(db):
    assert process_batch(db, [event(), event()]) == 1
    assert db.execute("SELECT COUNT(*) FROM event_totals").fetchone()[0] == 1

def test_conflicting_duplicate_payload_is_rejected(db):
    assert process_batch(db, [event()]) == 1
    with pytest.raises(ValueError, match="different payload"):
        process_batch(db, [event(source="changed-source")])
    assert get_total(db) == 100
    assert db.execute("SELECT COUNT(*) FROM event_totals").fetchone()[0] == 1

def test_process_batch_does_not_commit_callers_transaction(db):
    db.execute("INSERT INTO sources(source) VALUES (?)", ("caller-owned",))
    with pytest.raises(RuntimeError, match="no active transaction"):
        process_batch(db, [event()])
    assert db.execute("SELECT COUNT(*) FROM sources WHERE source = ?", ("caller-owned",)).fetchone()[0] == 1
    db.rollback()
    assert db.execute("SELECT COUNT(*) FROM sources WHERE source = ?", ("caller-owned",)).fetchone()[0] == 0

def test_process_batch_rejects_autocommit_true(tmp_path):
    con = sqlite3.connect(tmp_path / "autocommit.sqlite3", autocommit=True)
    try:
        con.execute("PRAGMA foreign_keys = ON")
        initialize_database(con)
        with pytest.raises(RuntimeError, match="LEGACY_TRANSACTION_CONTROL"):
            process_batch(con, [event()])
        assert con.execute("SELECT COUNT(*) FROM seen_ids").fetchone()[0] == 0
    finally:
        con.close()

def test_invalid_record_rolls_back_whole_batch(db):
    records = [event("valid"), event("invalid", amount_cents=-1)]
    with pytest.raises(ValueError):
        process_batch(db, records)
    assert db.execute("SELECT COUNT(*) FROM seen_ids").fetchone()[0] == 0
    assert db.execute("SELECT COUNT(*) FROM sources").fetchone()[0] == 0

def test_foreign_key_is_enabled(db):
    with pytest.raises(sqlite3.IntegrityError):
        with db:
            db.execute(
                "INSERT INTO event_totals(event_id, source, amount_cents) VALUES (?, ?, ?)",
                ("missing-marker", "missing-source", 10),
            )

def test_bool_is_not_accepted_as_money(db):
    with pytest.raises(ValueError):
        process_batch(db, [event(amount_cents=True)])

def test_constraint_failure_rolls_back(db):
    with pytest.raises(sqlite3.IntegrityError):
        with db:
            db.execute("INSERT INTO sources(source) VALUES (?)", ("temporary",))
            db.execute(
                "INSERT INTO event_totals(event_id, source, amount_cents) VALUES (?, ?, ?)",
                ("orphan", "temporary", -1),
            )
    assert db.execute("SELECT COUNT(*) FROM sources WHERE source = ?", ("temporary",)).fetchone()[0] == 0

@pytest.mark.parametrize("bad_id", ["", "   ", None])
def test_event_id_must_be_nonempty_text(db, bad_id):
    with pytest.raises((ValueError, TypeError, KeyError)):
        process_batch(db, [event(event_id=bad_id)])
```

Run:

```bash
python -m pytest -q
```

Expected summary for this test file: **12 passed** (the parameterized test contributes three cases). The exact pytest output format varies by version.

### What the rollback tests prove

The suite tests application validation failure, conflicting duplicate payloads, caller-owned transaction protection, and a database constraint failure after an earlier write in the same transaction. In rollback cases the earlier write is absent afterward, demonstrating rollback of the complete unit of work. The test fixture uses a new file-backed database per test, which exercises real connection and foreign-key behavior rather than sharing a global in-memory connection.

## 13. Common mistakes and debugging

| Mistake | Why it fails | Better practice |
|---|---|---|
| Building SQL with f-strings for values | SQL injection or quoting errors | Bind values with `?`. |
| Assuming `with con:` closes the connection | Connection remains open | Explicit `close()` or `contextlib.closing()`. |
| Forgetting `commit()` outside a transaction context | Changes may be rolled back when connection closes | Define transaction boundaries deliberately. |
| Catching an error inside `with con:` and suppressing it | Earlier statements may still commit | Let the error escape or explicitly roll back. |
| Assuming foreign keys are enabled | Invalid relationships may be stored | Set and verify `PRAGMA foreign_keys=ON` per connection. |
| Retrying every `OperationalError` forever | Hides real bugs and creates unbounded delay | Retry only transient lock failures with a bounded policy. |
| Using WAL to expect multiple writers | WAL improves reader/writer coexistence, not writer parallelism | Shorten write transactions or choose a client-server DB. |
| Sharing one connection across threads casually | Operations can interleave or violate transaction assumptions | Use connection-per-thread or explicit synchronization. |
| Committing each row | High overhead and partial batches | Batch inserts in a transaction when semantics permit. |
| Assuming `STRICT` guarantees domain correctness | It enforces storage types, not all business rules | Use `CHECK`, foreign keys, and application validation. |
| Treating `INSERT OR IGNORE` as harmless | It can suppress more than duplicate-key conflicts | Prefer targeted `ON CONFLICT(key) DO NOTHING`. |
| Copying a live database file as a backup | WAL or transaction state may be omitted | Use `Connection.backup()`. |

## 14. Hands-on exercises

1. **CRUD:** Add a `status` column and implement parameterized create/read/update/delete functions.
2. **Constraints:** Add a unique external reference and test duplicate rejection.
3. **Upsert:** Store the latest observation for each `(device_id, observed_at)` key.
4. **Query plan:** Create 50,000 deterministic rows, compare a filter before/after an index, and inspect `EXPLAIN QUERY PLAN`. Do not assert that timing always improves on every machine.
5. **Migration:** Introduce schema version 2 and write a migration test starting from version 1.
6. **Read-only mode:** Open the database with `mode=ro` and assert that a write fails.
7. **Locking:** Hold `BEGIN IMMEDIATE` on one connection and observe a second connection's bounded wait/failure.
8. **Backup:** Back up a database, reopen the backup, and verify row counts and constraints.
9. **Custom function:** Register a deterministic normalization function and test `NULL` handling.
10. **Idempotency:** Process the same batch three times and prove that the output count and total do not change after the first run.

## 15. Self-check questions with explained answers

### 1. Why does `with con:` not close a connection?

It is a transaction context manager. It commits an open transaction on normal exit and rolls back on an escaping exception; connection lifetime is separate. Use explicit closure or `closing()`.

### 2. Why are `?` placeholders safer than f-strings?

SQLite binds each value as data. F-strings merge data into SQL syntax, which can change the statement's meaning. Placeholders do not bind identifiers, so dynamic identifiers need an allow-list.

### 3. What does WAL change, and what does it not change?

WAL generally lets readers continue on a snapshot while a writer appends to the WAL. It does not permit multiple simultaneous writers and is not a general multi-host network-filesystem solution.

### 4. Why use `ON CONFLICT ... DO NOTHING` for a checkpoint?

The primary key is the durable uniqueness guard. A repeated event does not create a second marker, and the application only writes output for a newly inserted marker. Marker and output must be in the same transaction.

### 5. Why is `INSERT OR IGNORE` sometimes too broad?

It may suppress constraint violations beyond the one duplicate key the application intended to ignore. A targeted conflict clause communicates the intended condition more precisely.

### 6. Why is a database backup API preferable to copying the `.sqlite3` file?

An active database may have WAL/journal state outside the main file. `Connection.backup()` uses SQLite's backup mechanism to produce a consistent copy.

### 7. When should SQLite be replaced with a client-server database?

When many writers need concurrent progress, multiple hosts need coordinated access, centralized administration/authorization is required, or the workload outgrows a single local database file.

### 8. What makes the example pipeline idempotent?

`seen_ids.event_id` is a primary key, and the output write occurs only if the marker insert created a new row. The marker and output share a transaction, so a failed batch does not leave a marker without its corresponding output.

### 9. Does `STRICT` replace validation?

No. It narrows accepted storage types but does not express every business invariant. Use SQL constraints and application validation together.

### 10. Why should lock retries be bounded?

A lock may be transient, but it can also signal a long transaction or architectural contention. Bounded retries prevent infinite waits and preserve observability. Retry the complete transaction only when it is safe to do so.

## 16. Final mastery checklist

- [ ] I can explain when SQLite is an appropriate embedded database.
- [ ] I can connect to `:memory:` and file-backed databases and close connections reliably.
- [ ] I use parameterized SQL for every value and allow-lists for dynamic identifiers.
- [ ] I understand `execute`, `executemany`, cursor iteration, and fetch methods.
- [ ] I can explain why `with con:` manages transactions but does not close the connection.
- [ ] I can design constraints and explicitly enable foreign keys.
- [ ] I can use row factories, adapters/converters, `STRICT` tables, and documented timestamp formats.
- [ ] I can implement targeted upserts and distinguish them from broad `OR IGNORE` behavior.
- [ ] I can inspect query plans and measure indexing decisions.
- [ ] I understand `autocommit`, `isolation_level`, and when `BEGIN IMMEDIATE` helps.
- [ ] I can configure WAL and busy timeouts without claiming SQLite supports multiple writers.
- [ ] I can explain thread ownership and why disabling `check_same_thread` is not a concurrency strategy.
- [ ] I can apply schema migrations and back up databases using the SQLite API.
- [ ] I can build and test an idempotent checkpoint pipeline that rejects conflicting payloads for an already-seen ID and does not commit a caller-owned transaction.
- [ ] I know when SQLite's single-writer and single-host model is no longer a good fit.

## 17. Quick reference

| Need | API or pattern | Notes |
|---|---|---|
| Connect | `sqlite3.connect(path)` | File-backed database; creates file when possible. |
| In-memory test DB | `sqlite3.connect(":memory:")` | Private to that connection. |
| Parameterized statement | `con.execute(sql, params)` | Bind values, not identifiers. |
| Batch statements | `con.executemany(sql, rows)` | Use a transaction for related changes. |
| Transaction scope | `with con:` | Commits/rolls back; does not close. |
| Dict-like rows | `con.row_factory = sqlite3.Row` | Set before creating cursors. |
| Foreign keys | `PRAGMA foreign_keys = ON` | Configure and verify each connection. |
| Upsert | `ON CONFLICT (...) DO UPDATE` | Requires an appropriate unique constraint. |
| Ignore duplicate key | `ON CONFLICT(key) DO NOTHING` | Narrower intent than broad `OR IGNORE`. |
| Schema version | `PRAGMA user_version` | Application-managed migration marker. |
| WAL | `PRAGMA journal_mode=WAL` | Readers coexist better with writer; still one writer. |
| Lock wait | `timeout=` or `PRAGMA busy_timeout` | Use bounded retries for transient contention. |
| Backup | `Connection.backup()` | Prefer over raw copy of a live database file. |
| Read-only URI | `file:path?mode=ro`, `uri=True` | Handle URI escaping carefully. |
| Query plan | `EXPLAIN QUERY PLAN ...` | Output details vary by SQLite version. |
| Feature detection | `sqlite3.sqlite_version_info` | Python version alone does not identify SQLite features. |

**Rule of thumb:** Keep SQL values parameterized, enforce invariants in the schema, keep transactions short, and make checkpoint state atomic with the output it protects.
