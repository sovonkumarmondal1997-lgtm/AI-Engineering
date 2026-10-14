# DB-API (PEP 249): Connections and Cursors

> **Module:** Stage 2 — Python for Data Engineering  
> **Module 2.7:** Python Database Connectivity  
> **Topic:** 01 — DB-API (PEP 249): connections and cursors  
> **Level:** Beginner → Intermediate → Advanced foundation

## Learning Objectives

By the end of this topic, you should be able to:

- Explain the database-access stack:

  ```text
  Your Python application
          ↓
      DB-API interface
          ↓
     Database driver
          ↓
  Database/network protocol
          ↓
    Database server
  ```

- Explain what **PEP 249 / DB-API 2.0** standardizes and what it deliberately leaves to individual drivers.
- Explain the difference between a **connection** and a **cursor**.
- Use `connect()`, `cursor()`, `execute()`, `executemany()`, `fetchone()`, `fetchmany()`, `fetchall()`, `commit()`, `rollback()`, and `close()` with `sqlite3`.
- Explain what happens conceptually when Python executes SQL through a driver.
- Use `cursor.description`, `rowcount`, and `arraysize` appropriately while understanding their limitations.
- Recognize the five DB-API parameter styles: `qmark`, `numeric`, `named`, `format`, and `pyformat`.
- Explain the standard DB-API exception hierarchy and catch meaningful exception classes.
- Explain implicit transaction behavior at a foundation level.
- Explain why database-driver context-manager behavior must be checked in the driver's documentation.
- Explain the DB-API `threadsafety` levels and why a connection should not automatically be assumed safe for arbitrary concurrent use.
- Write simple driver-agnostic helpers such as a bounded `iter_rows()` generator.
- Explain why DB-API is a common programming contract, not a promise that all databases behave identically.
- Compare `sqlite3` and DuckDB at the DB-API/foundation level without turning the comparison into a product ranking.

## Prerequisites

This topic is part of Module 2.7 — Python Database Connectivity. It assumes you already have the earlier skills identified by the module roadmap:

| Earlier skill | Where it was learned | Why it matters here |
|---|---|---|
| Exceptions and useful errors | Stage 1 — Module 1.3 | Database failures need meaningful handling. |
| Environment configuration and validation | Stage 1 — Module 1.5 | Real drivers need configuration outside source code. |
| Mocking and test doubles | Stage 1 — Module 1.7 | Database boundaries eventually need isolated tests. |
| Protocols and layered design | Stage 1 — Module 1.8 | DB-API is itself an abstraction boundary. |
| Context managers, iterators, generators | Stage 1 — Module 1.9 | Database resources need explicit lifecycle management. |
| Configuration, logging, idempotency | Stage 1 — Module 1.10 | Database code must be operationally safe. |
| pandas database I/O basics | Stage 2 — Module 2.3 | This topic explains the lower-level ideas underneath database I/O. |
| Arrow/ADBC awareness and Parquet | Stage 2 — Modules 2.4–2.5 | Later database-transfer topics build on these concepts. |
| SQL, transactions, locking, `MERGE`, SCD concepts | Stage 2 — Module 2.6 | SQL itself is not re-taught here. |

This topic intentionally **does not** teach PostgreSQL/psycopg details, SQL injection, production transaction engineering, connection pooling, SQLAlchemy, Alembic, PostgreSQL `COPY`, or large-result server-side streaming in depth. Those belong to Topics 02–10 of this module.

---

## Why This Topic Matters

A Python program does not talk directly to a database engine simply because you wrote a SQL string.

There is a boundary between your application and the database. At that boundary, several responsibilities are separated:

- Your application decides **what work it wants done**.
- A database driver translates your Python-level calls into the database-specific protocol and exposes results back to Python.
- The database server parses and executes the SQL, applies its own transaction and concurrency rules, reads or changes data, and produces results.
- DB-API gives Python code a **common interface** for many drivers so that concepts such as connections, cursors, execution, fetching, and exceptions have a familiar shape.

This boundary is one of the most important foundations in Data Engineering. Later you will use Python to:

- extract database tables into files,
- load files into staging tables,
- maintain pipeline metadata,
- update watermarks,
- run quality checks,
- orchestrate warehouse loads,
- and move large amounts of data between systems.

A data engineer who understands the boundary can reason about unfamiliar database drivers instead of memorizing isolated APIs.

---

# 1. The Python → Database Architecture

## 1.1 The five-layer mental model

Start with this model:

```text
┌───────────────────────────────┐
│ Your Python application       │
│ business / pipeline logic     │
└───────────────┬───────────────┘
                │ Python method calls
                ▼
┌───────────────────────────────┐
│ DB-API interface              │
│ common Python database model  │
└───────────────┬───────────────┘
                │ implemented by
                ▼
┌───────────────────────────────┐
│ Database driver               │
│ e.g. sqlite3 / psycopg / ...  │
└───────────────┬───────────────┘
                │ database protocol
                ▼
┌───────────────────────────────┐
│ Database server / engine      │
│ SQL parser + executor + data  │
└───────────────────────────────┘
```

The simplified roadmap picture can also be written as:

```text
Your Python application
        ↓
    DB-API interface
        ↓
   Database driver
        ↓
Database/network protocol
        ↓
  Database server
```

### What does the application do?

The application decides the operation it needs:

```python
cursor.execute("SELECT id, name FROM customers WHERE country = ?", ("IN",))
```

The Python application is not responsible for implementing the database protocol itself. It asks the driver to execute an operation.

### What is DB-API?

DB-API is a standard interface specification for Python database access. It defines common concepts and behaviors so Python code can interact with different drivers in a recognizable way.

It does **not** contain a database server. It is not SQLite, PostgreSQL, DuckDB, MySQL, or Oracle.

Think of DB-API as a **contract**:

> “A Python database driver should expose a familiar set of objects, methods, attributes, parameters, and exception categories.”

The actual implementation is provided by a driver.

### What does a driver do?

A driver is the concrete software that knows how to communicate with a particular database system.

Conceptually, a driver may need to:

1. establish a database connection;
2. authenticate or negotiate access;
3. encode your SQL and parameters into the database's protocol;
4. send the request over the appropriate transport;
5. receive responses from the server;
6. decode result data into Python objects;
7. map database failures into Python exception classes.

The exact mechanics differ by driver and database.

### Why is the server separate?

The server owns the actual database state and executes database operations.

For a server-based database, the server may manage:

- data files,
- indexes,
- locks,
- transactions,
- query execution,
- connection/session state,
- concurrency,
- permissions,
- and resource management.

SQLite is useful as a learning example because the database engine is embedded in the process and the database is usually a local file. Even there, your Python program still interacts through a driver-level API.

### Why is DB-API an abstraction?

An abstraction hides details that application code does not need to repeat everywhere.

Instead of learning five completely unrelated APIs, a Python developer can learn the common DB-API concepts first:

```text
connect
  ↓
connection
  ↓
cursor
  ↓
execute
  ↓
fetch
```

Later, when you meet another driver, you ask:

- How does this driver connect?
- What parameter style does it use?
- What exceptions does it expose?
- How does it handle transactions?
- Which additional capabilities does it provide?

That is a much stronger approach than memorizing one library.

---

## 1.2 End-to-end execution flow

Consider:

```python
cursor.execute(
    "SELECT id, name FROM users WHERE id = ?",
    (42,),
)
row = cursor.fetchone()
```

Conceptually:

```text
Python calls cursor.execute(...)
        ↓
Driver receives SQL + parameter value
        ↓
Driver prepares the database-specific request
        ↓
Driver communicates with the database
        ↓
Database parses and executes the statement
        ↓
Database produces a result
        ↓
Driver receives the result
        ↓
Cursor exposes the result through DB-API methods
        ↓
Python calls fetchone()
        ↓
One result row becomes a Python object
```

### What Python controls

Your Python code controls things such as:

- when to connect;
- what statement to request;
- what parameter values to pass;
- when to fetch rows;
- when to commit or roll back where applicable;
- when to release objects/resources.

### What the driver controls

The driver controls database-specific communication details and implementation choices. Examples include how SQL and parameters are encoded, how result messages are decoded, and what capabilities are exposed beyond the common DB-API contract.

### What the database controls

The database controls the actual execution semantics. It decides how a statement is parsed, planned, executed, locked, and applied according to that database engine's rules.

This distinction is important:

> Calling a Python method does not mean Python itself is executing SQL. Python is requesting database work through a driver.

---

# 2. What Is PEP 249 / DB-API?

## 2.1 PEP 249 in plain language

**PEP 249** is the Python Database API Specification v2.0, commonly called **DB-API 2.0**.

It specifies a standard interface for Python database modules.

Its purpose is not to make databases identical. Its purpose is to make their Python interfaces similar enough that common ideas transfer.

For example, a DB-API-style module commonly gives you concepts like:

```python
connection = module.connect(...)
cursor = connection.cursor()
cursor.execute(...)
rows = cursor.fetchall()
connection.commit()
connection.close()
```

A particular driver may add much more. The common interface is the foundation.

## 2.2 Standardized interface vs implementation

It helps to separate three things:

| Layer | Meaning |
|---|---|
| Standardized interface | The common DB-API contract. |
| Driver implementation | The concrete Python module that implements the contract. |
| Database-specific capabilities | Features that exist because the target database/driver has them. |

For example:

```text
PEP 249 / DB-API
       ↓
common concepts: connection, cursor, execute, fetch
       ↓
Concrete driver
       ↓
database-specific protocol/features
```

A driver can follow DB-API and still expose extra features that another driver does not.

## 2.3 Examples

The roadmap uses three useful examples:

- `sqlite3` — Python's standard-library SQLite interface;
- `psycopg` — a PostgreSQL Python driver;
- DuckDB's Python API — an embedded analytical database API that supports DB-API-style usage.

The important lesson is **not** that these APIs are identical.

The important lesson is that once you understand the common concepts, the differences become easier to reason about.

## 2.4 What “DB-API 2.0” does not mean

It does not mean:

> “Every Python database library accepts exactly the same arguments and behaves exactly the same way.”

Instead, it means there is a common specification for important concepts.

Driver documentation still matters.

---

# 3. Connection Objects

## 3.1 What is a connection?

A **connection object** represents Python's active interaction with a database through a driver.

Simple definition:

> **Connection = the object that represents and manages an active database interaction/session resource.**

The exact implementation differs between embedded and server-based databases, but conceptually a connection gives your Python program a context in which it can execute database operations.

## 3.2 Why does a connection exist?

Database interaction needs state and resources.

Depending on the database and driver, a connection may be associated with:

- authentication state,
- transaction state,
- session settings,
- server-side resources,
- network resources,
- database handles,
- and one or more cursors.

That is why a connection is more than “just a network socket.”

For a server database there may be a network connection underneath it, but the connection object also represents higher-level database/session state.

## 3.3 Creating a connection

With SQLite:

```python
import sqlite3

conn = sqlite3.connect("example.db")
```

What happens conceptually:

1. Python imports the `sqlite3` module.
2. `sqlite3.connect()` creates a connection object.
3. The driver opens or creates the database resource.
4. The returned `conn` object becomes your handle for database interaction.

## 3.4 Common connection operations

The core DB-API connection operations in this topic are:

```text
connect()
cursor()
commit()
rollback()
close()
```

### `connect()`

Creates a connection to the database.

Conceptual model:

```text
Python
  │
  └── connect(...)
        │
        ▼
    Driver setup
        │
        ▼
 Database connection/session
```

### `cursor()`

Creates a cursor associated with the connection.

```python
cursor = conn.cursor()
```

A connection can typically have multiple cursor objects associated with it. The exact concurrency and lifecycle rules depend on the driver.

### `commit()`

Commits the current transaction where transaction behavior supports this operation.

At this stage you only need the foundation:

> `commit()` tells the database/driver to make the current transaction's successful changes durable/visible according to the database's transaction semantics.

Detailed transaction design belongs to Topic 04.

### `rollback()`

Rolls back the current transaction where supported.

Again, Topic 04 covers the deeper engineering decisions.

### `close()`

Releases the connection resource.

After a connection is closed, further use is generally invalid and should raise a driver-specific database exception.

## 3.5 First runnable example

```python
import sqlite3

conn = sqlite3.connect("example.db")

try:
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    print(cursor.fetchone())
finally:
    conn.close()
```

### Line-by-line explanation

```python
import sqlite3
```

Loads the standard-library SQLite driver.

```python
conn = sqlite3.connect("example.db")
```

Creates a connection to a file-backed SQLite database.

`try:`

Starts a resource-management boundary. If something fails, the `finally` block still runs.

```python
cursor = conn.cursor()
```

Creates a cursor associated with the connection.

```python
cursor.execute("SELECT 1")
```

Asks the driver to execute the statement.

```python
print(cursor.fetchone())
```

Retrieves one result row.

`finally:` with `conn.close()`

Releases the connection even if the query raises an exception.

## 3.6 What if connection creation fails?

The call can fail before `conn` exists:

```python
conn = sqlite3.connect("some/path/database.db")
```

For example, a filesystem permission problem can prevent the database from being opened.

That means cleanup code must only operate on resources that were successfully created.

One safe pattern is to use the connection's context-management behavior where appropriate, while still understanding exactly what the context manager controls. We return to this in Section 13.

## 3.7 What if code crashes before `close()`?

If your program exits, operating-system cleanup may eventually release resources. But production code should not depend on process termination to clean up database resources.

In long-running workers, services, or multi-step pipeline processes, an unclosed connection can remain alive and consume database resources.

Production rule:

> **Acquire database resources deliberately and release them deterministically.**

---

# 4. Cursor Objects

## 4.1 What is a cursor?

Simple definition:

> **Cursor = an object used by Python code to execute a database statement and work with the rows/results associated with that statement.**

A cursor is normally obtained from a connection:

```python
conn = sqlite3.connect("example.db")
cursor = conn.cursor()
```

Conceptually:

```text
Connection
    │
    ├── Cursor A
    ├── Cursor B
    └── Cursor C
```

The connection is the broader database interaction resource. A cursor provides the statement/result interface used by Python code.

## 4.2 Why do cursors exist?

Database operations have two broad stages:

1. execute an operation;
2. work with the result, if one exists.

The cursor gives Python an object through which those operations can be expressed.

For example:

```python
cursor.execute("SELECT id, name FROM users")
row = cursor.fetchone()
```

The cursor is the object that remembers the result context needed by subsequent fetch calls.

## 4.3 Cursor lifecycle

A simple lifecycle is:

```text
create cursor
     ↓
execute statement
     ↓
inspect metadata / fetch results
     ↓
finish work
     ↓
close cursor
```

For small programs, explicit cursor closure is often simplest:

```python
cursor = conn.cursor()
try:
    cursor.execute("SELECT 1")
    print(cursor.fetchone())
finally:
    cursor.close()
    conn.close()
```

Drivers may also support context-manager syntax for cursors. Always verify the driver's documented behavior.

## 4.4 Cursor vs database-side server cursor

These terms are easy to confuse.

A **DB-API cursor** is a Python-level interface object.

A **server-side cursor** is a database/driver mechanism that can keep a result set associated with the server and transfer rows incrementally rather than materializing the entire result on the client at once.

They are related concepts but are not automatically equivalent.

This matters because:

```python
rows = cursor.fetchmany(100)
```

does not, by itself, prove that the database driver never buffered a larger result internally.

The DB-API interface tells you how Python asks for rows. It does not, by itself, prescribe a universal result-buffering architecture.

Detailed server-side cursor behavior belongs to Topic 10.

---

# 5. `execute()`

## 5.1 What is `execute()`?

The cursor method:

```python
cursor.execute(...)
```

asks the driver to execute one database operation.

For a result-producing statement, such as `SELECT`, the cursor becomes associated with a result that Python can subsequently fetch.

For a statement that does not return rows, such as an `INSERT`, there may be no row set to fetch.

## 5.2 CREATE TABLE

```python
import sqlite3

conn = sqlite3.connect("example.db")
try:
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
        """
    )
    conn.commit()
finally:
    conn.close()
```

Conceptually:

```text
Python cursor.execute()
        ↓
SQLite driver
        ↓
SQLite engine
        ↓
Parse CREATE TABLE
        ↓
Create/verify table structure
```

There are no result rows to fetch from this statement.

## 5.3 INSERT

```python
cursor.execute(
    "INSERT INTO users (name) VALUES (?)",
    ("Asha",),
)
```

The cursor sends the request to the driver with the SQL statement and its parameter value.

## 5.4 SELECT

```python
cursor.execute("SELECT id, name FROM users")
row = cursor.fetchone()
```

The key distinction is:

```text
execute()     → ask the driver/database to perform the operation
fetchone()    → retrieve one row from the result interface
```

`execute()` does not necessarily mean:

> “Load every row into a Python list immediately.”

The actual result-buffering behavior is driver- and database-specific.

## 5.5 UPDATE and DELETE

```python
cursor.execute(
    "UPDATE users SET name = ? WHERE id = ?",
    ("Asha Singh", 1),
)

cursor.execute(
    "DELETE FROM users WHERE id = ?",
    (2,),
)
```

Again, the database performs the operation. Python receives status information and exceptions through the driver.

---

# 6. `executemany()`

## 6.1 What problem does it solve?

Suppose you want to perform the same kind of operation for many parameter sets:

```python
rows = [
    ("Asha",),
    ("Rahul",),
    ("Mira",),
]
```

With repeated `execute()` calls, you might write:

```python
for row in rows:
    cursor.execute(
        "INSERT INTO users (name) VALUES (?)",
        row,
    )
```

DB-API also provides:

```python
cursor.executemany(
    "INSERT INTO users (name) VALUES (?)",
    rows,
)
```

The purpose is to express a repeated parameterized operation through one DB-API call.

## 6.2 `execute()` vs `executemany()`

| Method | Main idea |
|---|---|
| `execute()` | Execute one operation/statement with one parameter set. |
| `executemany()` | Apply one operation pattern to multiple parameter sets. |

The exact performance characteristics are **driver-specific**.

Do not assume:

> `executemany()` = one database round trip per row

and do not assume:

> `executemany()` = a high-performance bulk loader in every driver.

A driver may batch work internally, pipeline requests, prepare statements, or use another implementation strategy.

## 6.3 Small SQLite example

```python
import sqlite3

conn = sqlite3.connect("example.db")
try:
    cursor = conn.cursor()

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS products ("
        "id INTEGER PRIMARY KEY, "
        "name TEXT NOT NULL"
        ")"
    )

    products = [
        ("Keyboard",),
        ("Mouse",),
        ("Monitor",),
    ]

    cursor.executemany(
        "INSERT INTO products (name) VALUES (?)",
        products,
    )

    conn.commit()
finally:
    conn.close()
```

The important conceptual flow is:

```text
one SQL operation pattern
        +
multiple parameter sets
        ↓
executemany()
        ↓
driver-specific implementation
        ↓
database operations
```

Large-scale PostgreSQL bulk-loading techniques such as `COPY` belong to Topic 09. `executemany()` is one rung on the loading ladder, not the complete bulk-loading story.

---

# 7. Fetching Results

The three required DB-API fetching methods are:

```text
fetchone()
fetchmany()
fetchall()
```

## 7.1 `fetchone()`

Definition:

> Return the next available row, or `None` when no row is available.

Example:

```python
cursor.execute("SELECT id, name FROM users ORDER BY id")

row = cursor.fetchone()
print(row)
```

If the result is:

```text
(1, "Asha")
(2, "Rahul")
```

then the first call might produce:

```python
(1, "Asha")
```

and the next call:

```python
(2, "Rahul")
```

After the result is exhausted, `fetchone()` returns `None` according to the DB-API contract.

## 7.2 `fetchmany()`

Definition:

> Return the next batch of available rows, up to the requested size.

Example:

```python
rows = cursor.fetchmany(100)
```

If fewer than 100 rows remain, the returned sequence may contain fewer rows. If no rows remain, it is an empty sequence.

This makes it useful for application-level batching:

```python
while True:
    rows = cursor.fetchmany(100)
    if not rows:
        break

    for row in rows:
        process(row)
```

The key point:

> `fetchmany()` lets your application process rows in bounded batches, but it does not by itself guarantee that the driver never buffered more data internally.

## 7.3 `fetchall()`

Definition:

> Return all remaining result rows as a sequence.

Example:

```python
rows = cursor.fetchall()
```

For small datasets, this is convenient.

For a large result, it can be dangerous:

```text
Database result
      ↓
Driver/client buffering (implementation-specific)
      ↓
fetchall()
      ↓
large Python collection
      ↓
high memory usage
```

Imagine a query returns 20 million rows. A Python list containing millions of row objects can consume a large amount of memory.

The problem is not merely the database size. It is the size and shape of the Python representation created by your application.

## 7.4 Empty, one-row, and multi-row cases

### Empty result

```python
cursor.execute("SELECT id FROM users WHERE id = -1")

print(cursor.fetchone())
# None

print(cursor.fetchall())
# []
```

### One row

```python
cursor.execute("SELECT id FROM users WHERE id = 1")

row = cursor.fetchone()
print(row)
```

### Multiple rows

```python
cursor.execute("SELECT id FROM users ORDER BY id")

for row in cursor.fetchall():
    print(row)
```

For a large result, prefer a batching pattern:

```python
while True:
    rows = cursor.fetchmany(100)
    if not rows:
        break

    for row in rows:
        print(row)
```

## 7.5 Memory reasoning

Consider this:

```python
rows = cursor.fetchall()
```

Your application has chosen an **all-at-once materialization strategy** from its API perspective.

Now compare:

```python
while True:
    rows = cursor.fetchmany(1000)
    if not rows:
        break

    process_batch(rows)
```

The second pattern provides a bounded batch size to application logic.

However, do not overstate the guarantee:

```text
Application batching ≠ guaranteed server streaming
```

The driver may still buffer data. Truly large-result streaming requires driver/database mechanisms such as server-side cursors or bulk extraction interfaces. Those are intentionally left for Topic 10.

---

# 8. Cursor Metadata

The roadmap requires these cursor attributes:

```text
description
rowcount
arraysize
```

## 8.1 `cursor.description`

### What is it?

`description` provides metadata about the result columns of an executed query.

The DB-API specification represents each column description as a sequence containing information such as its name and type-related metadata.

For application code that only needs column names, the first item is commonly used:

```python
columns = [column[0] for column in cursor.description]
```

### Why does it exist?

It lets code inspect result structure without hard-coding the column names separately.

This is particularly useful for generic data-extraction helpers.

### Practical example

```python
import sqlite3

conn = sqlite3.connect("example.db")
try:
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name FROM users ORDER BY id"
    )

    print(cursor.description)

    columns = [column[0] for column in cursor.description]
    print(columns)

    rows = cursor.fetchall()
    rows_as_dicts = [
        dict(zip(columns, row))
        for row in rows
    ]

    print(rows_as_dicts)
finally:
    conn.close()
```

If the result columns are `id` and `name`, the helper can produce:

```python
[
    {"id": 1, "name": "Asha"},
    {"id": 2, "name": "Rahul"},
]
```

### Line-by-line reasoning

```python
columns = [column[0] for column in cursor.description]
```

Reads the column name from each description item.

```python
rows = cursor.fetchall()
```

Gets all remaining rows. This is acceptable for a small learning dataset but should not automatically be used for a large production extract.

```python
dict(zip(columns, row))
```

Pairs each column name with the corresponding value in the row.

### Reusable helper

```python
from collections.abc import Sequence
from typing import Any


def rows_to_dicts(
    description: Sequence[Sequence[Any]],
    rows: Sequence[Sequence[Any]],
) -> list[dict[str, Any]]:
    """Convert row tuples into dictionaries using DB-API metadata."""
    columns = [column[0] for column in description]
    return [dict(zip(columns, row)) for row in rows]
```

This helper is reasonably portable because it assumes only the common structure of `description` and iterable row values.

It is still not a guarantee that every driver returns exactly the same Python row type or metadata details.

## 8.2 `cursor.rowcount`

`rowcount` reports information about the number of rows affected by or associated with the most recent operation, subject to the DB-API rules and driver limitations.

For an `UPDATE`, you may see a useful count:

```python
cursor.execute(
    "UPDATE users SET name = ? WHERE id = ?",
    ("Asha Singh", 1),
)

print(cursor.rowcount)
```

But you should not assume that `rowcount` always gives a precise count for every `SELECT` across every driver.

DB-API allows situations where the number is not determinable and indicates that with `-1`.

Production rule:

> Treat `rowcount` as driver/database operation metadata, not as a universal substitute for an explicit `COUNT(*)` query or a measured data-validation strategy.

## 8.3 `cursor.arraysize`

`arraysize` is a cursor attribute used as a default batch size for operations such as `fetchmany()` when a size is not supplied.

Example:

```python
cursor.arraysize = 100
rows = cursor.fetchmany()
```

Conceptually:

```python
cursor.fetchmany()
```

means roughly:

```python
cursor.fetchmany(cursor.arraysize)
```

when the method is called without an explicit size.

The DB-API specification defines a default value and gives this attribute meaning, but driver implementation details can still matter for performance.

For clarity, production code often makes the desired batch size explicit:

```python
rows = cursor.fetchmany(1000)
```

That makes intent obvious and avoids hidden dependence on a driver's default.

## 8.4 Metadata limitations

Always distinguish:

```text
DB-API-level metadata
        vs
Driver-specific metadata details
        vs
Database-specific type semantics
```

A portable helper should use the common contract and isolate database-specific extensions elsewhere.

---

# 9. `sqlite3`: Our First DB-API Driver

## 9.1 Why SQLite is ideal for learning

SQLite is useful for this topic because:

- it is available through Python's standard library;
- no separate database server is required for basic exercises;
- a database can be stored in a local file;
- the examples are easy to reproduce;
- it exposes the core DB-API workflow clearly.

That makes it a zero-setup learning environment.

It is not a claim that SQLite behaves exactly like PostgreSQL or another production database system.

## 9.2 One coherent example

We will build a tiny customer database.

```python
import sqlite3

DB_PATH = "dbapi_lab.db"


conn = sqlite3.connect(DB_PATH)

try:
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            country TEXT NOT NULL
        )
        """
    )

    cursor.executemany(
        "INSERT OR IGNORE INTO customers (id, name, country) VALUES (?, ?, ?)",
        [
            (1, "Asha", "IN"),
            (2, "Rahul", "IN"),
            (3, "Mina", "SG"),
        ],
    )

    conn.commit()

    cursor.execute(
        "SELECT id, name, country FROM customers ORDER BY id"
    )

    print("Description:")
    print(cursor.description)

    print("One row:")
    print(cursor.fetchone())

    print("Next batch:")
    print(cursor.fetchmany(2))

finally:
    conn.close()
```

### What this teaches

The program follows the fundamental sequence:

```text
connect
  ↓
cursor
  ↓
execute
  ↓
fetch
  ↓
commit
  ↓
close
```

The details become more important as the workload grows, but this sequence is the foundation.

---

## 9.3 A cleaner context-managed SQLite example

SQLite's connection can be used as a context manager:

```python
import sqlite3

with sqlite3.connect("dbapi_context.db") as conn:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS numbers (value INTEGER)"
    )
    conn.execute("INSERT INTO numbers (value) VALUES (?)", (1,))
```

The important subtlety is that the connection context manager controls transaction behavior. It does **not** mean that the connection object is automatically closed just because the `with` block ended.

Therefore, this is still a valid explicit pattern:

```python
conn = sqlite3.connect("dbapi_context.db")
try:
    with conn:
        conn.execute(
            "INSERT INTO numbers (value) VALUES (?)",
            (2,),
        )
finally:
    conn.close()
```

The exact context-manager behavior of other drivers may differ. Never transfer assumptions from SQLite to another driver without checking its documentation.

---

# 10. DB-API Parameter Styles

## 10.1 What is parameter binding?

Parameter binding means that variable values are supplied separately from the SQL command structure.

Conceptually:

```text
SQL command structure
       +
parameter values
       ↓
driver/database execution
```

For example:

```python
cursor.execute(
    "SELECT * FROM users WHERE id = ?",
    (user_id,),
)
```

The parameter is not written into the SQL string by Python string formatting.

This topic only establishes the DB-API parameter concept. SQL injection and the full security implications are covered in Topic 03.

## 10.2 Why are parameter styles needed?

Different drivers historically use different placeholder syntaxes.

PEP 249 defines a `paramstyle` concept so code can identify which parameter notation a driver expects.

The five standard styles are:

```text
qmark      ?
numeric    :1
named      :name
format     %s
pyformat   %(name)s
```

## 10.3 Comparison table

| Style | Example placeholder | Typical example |
|---|---|---|
| `qmark` | `?` | `sqlite3` |
| `numeric` | `:1` | DB-API-style drivers that support it |
| `named` | `:name` | Drivers that support it |
| `format` | `%s` | `psycopg` |
| `pyformat` | `%(name)s` | `psycopg` |

**Important:** this table is about the DB-API parameter styles, not a statement that every driver supports every style.

A driver chooses the parameter style or styles it supports.

## 10.4 `qmark` example

SQLite commonly uses `qmark`:

```python
user_id = 42

cursor.execute(
    "SELECT * FROM users WHERE id = ?",
    (user_id,),
)
```

The SQL text contains a placeholder:

```text
SELECT * FROM users WHERE id = ?
```

and the parameter is passed separately:

```python
(user_id,)
```

## 10.5 Why you must learn the driver's style

This will fail when used with a driver that expects another style:

```python
cursor.execute(
    "SELECT * FROM users WHERE id = ?",
    (user_id,),
)
```

if that driver expects `%s`, for example.

The correct approach is not to guess. Read the driver's documentation or inspect its DB-API parameter style information where appropriate.

## 10.6 Foundational rule

> **Parameter style is part of the driver contract. Use the placeholder syntax that the driver expects.**

Topic 03 will turn this foundation into a full discussion of safe parameterization, identifiers, and SQL injection.

---

# 11. DB-API Exception Hierarchy

## 11.1 Why exceptions are categorized

Database failures are not all equivalent.

A duplicate key is different from a network failure. A malformed SQL statement is different from invalid data. A driver interface failure is different from an operational database outage.

DB-API defines a standard hierarchy so application code can reason about categories of errors.

The required hierarchy is:

```text
Error
├── InterfaceError
├── DatabaseError
│   ├── DataError
│   ├── OperationalError
│   ├── IntegrityError
│   ├── InternalError
│   ├── ProgrammingError
│   └── NotSupportedError
```

## 11.2 `Error`

`Error` is the common base class for DB-API exceptions.

It allows code to catch a database-related failure broadly when that is genuinely what the application wants.

## 11.3 `InterfaceError`

Represents problems related to the database interface rather than normal database operation.

Examples can include failures in the way the driver interface is used or connection-level interface problems, depending on the driver.

## 11.4 `DatabaseError`

A base class for errors associated with database processing.

Its subclasses provide more specific categories.

## 11.5 `DataError`

Used for problems with processed data, such as invalid values or values outside allowed ranges, depending on the driver/database.

Examples conceptually include:

- numeric overflow;
- invalid data format;
- value outside a database type's supported range.

## 11.6 `OperationalError`

Used for operational problems such as connection failures, database availability problems, or other situations where the operation cannot be completed because of external conditions.

An operational problem can sometimes be transient, but that does not mean every `OperationalError` should automatically be retried. The exact failure must be understood.

## 11.7 `IntegrityError`

Used for violations of database integrity constraints.

Examples include:

- duplicate primary key;
- uniqueness constraint violation;
- foreign-key violation;
- another integrity rule enforced by the database.

Example in SQLite:

```python
import sqlite3

conn = sqlite3.connect(":memory:")
try:
    conn.execute(
        "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL)"
    )
    conn.execute("INSERT INTO users (id, name) VALUES (?, ?)", (1, "Asha"))

    try:
        conn.execute(
            "INSERT INTO users (id, name) VALUES (?, ?)",
            (1, "Rahul"),
        )
    except sqlite3.IntegrityError as exc:
        print(f"Integrity failure: {exc}")
finally:
    conn.close()
```

The important idea is the type of failure, not the exact text of the message.

## 11.8 `InternalError`

Represents internal database/driver processing problems. These are generally not ordinary application-input failures.

The exact cases depend on the driver and database.

## 11.9 `ProgrammingError`

Commonly associated with programming mistakes such as:

- malformed SQL passed by the application;
- invalid parameter count;
- using a closed database object;
- another misuse of the API.

Example:

```python
import sqlite3

conn = sqlite3.connect(":memory:")
try:
    try:
        conn.execute("SELEC invalid_sql")
    except sqlite3.ProgrammingError as exc:
        print(f"Programming error: {exc}")
finally:
    conn.close()
```

Exact exception classification for a malformed statement can vary by driver, so always verify the concrete driver's exceptions.

## 11.10 `NotSupportedError`

Used when a requested operation is not supported by the driver/database combination.

This is useful when an API exists conceptually but the current driver does not implement a requested capability.

## 11.11 Why `except Exception: pass` is dangerous

Bad pattern:

```python
try:
    cursor.execute("...")
except Exception:
    pass
```

This can hide the actual failure and allow the pipeline to continue as though nothing happened.

Better:

```python
try:
    cursor.execute("...")
except sqlite3.IntegrityError as exc:
    print(f"Data integrity problem: {exc}")
except sqlite3.OperationalError as exc:
    print(f"Operational problem: {exc}")
```

The correct exception handling strategy depends on the application.

## 11.12 Which errors might be retry candidates?

At foundation level:

| Failure category | Typical retry posture |
|---|---|
| Transient operational/connectivity problem | Sometimes a retry candidate after diagnosis. |
| Serialization/deadlock-style concurrency failure | Often retryable in a correctly designed transaction; covered deeply in Topic 04. |
| Integrity constraint violation | Usually not something to blindly retry. |
| Programming/syntax error | Fix the code; retrying unchanged code is not useful. |
| Unsupported operation | Change the implementation/driver; retrying unchanged code does not solve it. |

This is deliberately a foundation, not a complete retry strategy. Topic 04 covers transaction retries in detail.

---

# 12. Implicit Transactions

## 12.1 What is a transaction?

A transaction groups database operations into a unit with defined commit/rollback behavior.

At this point, the key question is:

> **What happens when Python does not explicitly write `BEGIN`?**

DB-API drivers and databases can use transaction behavior in which a transaction begins implicitly when an operation requiring transaction control occurs.

The details vary by driver/database configuration, so do not assume one driver's transaction rules are universal.

## 12.2 The important lifecycle

A simplified mental model is:

```text
Connection created
      ↓
first transaction-relevant statement
      ↓
transaction becomes active
      ↓
commit() OR rollback()
      ↓
transaction ends
```

## 12.3 Why it matters

A beginner may write:

```python
conn = sqlite3.connect("example.db")
conn.execute(
    "INSERT INTO users (name) VALUES (?)",
    ("Asha",),
)
# program continues...
```

and assume:

> “The row is permanently stored because the statement ran successfully.”

That conclusion is unsafe. Transaction behavior matters.

## 12.4 Two-connection visibility demonstration

Use a file-backed SQLite database so two connections refer to the same database.

```python
import sqlite3

DB_PATH = "transaction_visibility.db"

setup = sqlite3.connect(DB_PATH)
try:
    setup.execute("DROP TABLE IF EXISTS users")
    setup.execute(
        "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL)"
    )
    setup.commit()
finally:
    setup.close()

conn_a = sqlite3.connect(DB_PATH, isolation_level="DEFERRED")
conn_b = sqlite3.connect(DB_PATH, isolation_level="DEFERRED")

try:
    conn_a.execute(
        "INSERT INTO users (name) VALUES (?)",
        ("Asha",),
    )

    row_before_commit = conn_b.execute(
        "SELECT id, name FROM users ORDER BY id"
    ).fetchall()

    print("Connection B before A commits:", row_before_commit)

    conn_a.commit()

    row_after_commit = conn_b.execute(
        "SELECT id, name FROM users ORDER BY id"
    ).fetchall()

    print("Connection B after A commits:", row_after_commit)
finally:
    conn_a.close()
    conn_b.close()
```

### What should you predict?

Before running:

1. Connection A inserts a row.
2. Connection A does not commit.
3. Connection B reads the table.
4. Connection B should not see A's uncommitted change under the usual transaction visibility rules.
5. Connection A commits.
6. Connection B can then observe the committed row.

### What is the engineering lesson?

The SQL statement and the transaction containing that statement are separate concepts:

```text
execute INSERT
    ≠
commit transaction
```

This distinction becomes critical in pipelines that perform multiple writes.

## 12.5 What happens if you forget `commit()`?

The exact outcome depends on the driver and how the connection is closed, but the safe mental model is:

> **Do not rely on process termination or connection teardown to mean “my work is committed.”**

Make transaction boundaries explicit and understand the specific driver behavior.

## 12.6 Scope boundary

This topic only establishes the transaction foundation.

Topic 04 goes deeper into:

- explicit transaction blocks;
- savepoints;
- isolation levels;
- autocommit;
- failed-transaction state;
- retrying serialization failures/deadlocks;
- idle-in-transaction sessions;
- idempotency and unknown commit outcomes.

---

# 13. Context Managers and Resource Lifecycle

## 13.1 Why use a context manager?

Python's `with` statement creates a structured lifecycle boundary.

Conceptually:

```text
enter resource scope
      ↓
use resource
      ↓
leave scope
      ↓
perform defined cleanup/transaction action
```

This is helpful for database code because connections and cursors are resources that should have predictable lifecycles.

## 13.2 The important warning

A context manager does **not** universally mean:

> “The database connection is closed at the end of the `with` block.”

Different database drivers can define different context-manager behavior.

SQLite is a good example because the connection context manager controls transaction behavior but does not itself close the connection.

## 13.3 SQLite demonstration

```python
import sqlite3

conn = sqlite3.connect("context_demo.db")

with conn:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY)"
    )
    conn.execute("INSERT INTO events (id) VALUES (?)", (1,))

# The connection can still be used here.
print(conn.execute("SELECT COUNT(*) FROM events").fetchone())

conn.close()
```

The key lesson is:

```text
with conn:
    transaction behavior
        ≠
    automatic universal connection closure
```

## 13.4 Why driver documentation matters

Suppose Driver A uses:

```python
with connect(...) as conn:
    ...
```

to close the connection on exit, while Driver B uses the context manager primarily for transaction handling.

If your code assumes Driver B behaves like Driver A, you may create leaks or unexpected lifecycle behavior.

Production rule:

> **Use context managers deliberately, but always verify what the specific driver promises `__enter__` and `__exit__` will do.**

## 13.5 Cursor context managers

Some drivers provide:

```python
with conn.cursor() as cursor:
    cursor.execute(...)
```

If supported, this can provide a clean cursor lifecycle.

Again, the exact cleanup semantics belong to the driver's implementation.

---

# 14. Thread Safety

## 14.1 Why thread safety matters

Data Engineering programs sometimes use multiple threads for concurrent work.

That immediately raises an important question:

> Can multiple threads safely use the same database module, connection, or cursor?

The answer is not “yes” or “no” for all DB-API drivers. PEP 249 gives a standardized `threadsafety` attribute to communicate the driver's supported level.

## 14.2 DB-API thread-safety levels

PEP 249 defines four levels:

| `threadsafety` | Meaning |
|---:|---|
| `0` | Threads may not share the module. |
| `1` | Threads may share the module, but not connections. |
| `2` | Threads may share the module and connections, but not cursors. |
| `3` | Threads may share the module, connections, and cursors. |

The important point is that `threadsafety` describes what the driver claims it supports under the DB-API contract. It does not automatically mean concurrent access is a good architectural choice.

## 14.3 Inspecting the value

```python
import sqlite3

print("sqlite3 threadsafety:", sqlite3.threadsafety)
```

Do not hard-code assumptions from memory. Inspect the driver and read its documentation for concurrency details.

## 14.4 Driver supports threads ≠ share one connection everywhere

This distinction is critical.

There are at least three different questions:

```text
Can Python create threads?
        ↓
Can the driver be used in a threaded process?
        ↓
Can this exact connection/cursor be shared safely?
```

They are not the same question.

## 14.5 Why sharing a cursor is especially risky

A cursor represents state associated with database operations and result handling.

If two threads unexpectedly operate on the same cursor at the same time, the logical sequence of operations becomes difficult to reason about.

For example:

```text
Thread A: execute query A
Thread B: execute query B
Thread A: fetch row
```

Which result does Thread A expect?

This is exactly the kind of ambiguity resource ownership rules are intended to prevent.

## 14.6 Production mental model

Prefer explicit ownership:

```text
worker
  ↓
its database resource
```

rather than:

```text
many workers
      ↓
shared mutable connection/cursor
```

The exact architecture depends on the driver and workload. Connection pooling, multiprocessing rules, and async database access are covered later in the module.

---

# 15. Building Driver-Agnostic Helpers

One of the most useful outcomes of learning DB-API is that you can build small abstractions around the common contract.

The goal is not to pretend all databases are identical.

The goal is to remove repetitive boilerplate where the contract genuinely is common.

## 15.1 A row iterator using `fetchmany()`

The roadmap requires:

```python
iter_rows(cursor, batch_size)
```

implemented as a generator.

A clean implementation is:

```python
from collections.abc import Iterator
from typing import Any


def iter_rows(cursor: Any, batch_size: int) -> Iterator[Any]:
    """Yield rows from a DB-API cursor in bounded application batches."""
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero")

    while True:
        rows = cursor.fetchmany(batch_size)
        if not rows:
            break

        yield from rows
```

## 15.2 Why a generator?

A generator does not construct a full list of every row in advance.

Instead:

```text
fetch batch
   ↓
yield rows
   ↓
consumer processes them
   ↓
fetch next batch
```

This keeps the application-side processing pattern bounded by the chosen batch size rather than requiring one giant Python list.

Again, this does not automatically turn the driver into a server-side streaming implementation.

## 15.3 Validate the helper

### Empty result

```python
cursor.execute("SELECT id FROM users WHERE 1 = 0")

for row in iter_rows(cursor, 100):
    print(row)
```

The loop should produce zero rows.

### One row

```python
cursor.execute("SELECT id FROM users WHERE id = ?", (1,))

for row in iter_rows(cursor, 100):
    print(row)
```

Exactly one row should be yielded when one matches.

### Many rows

```python
cursor.execute("SELECT id FROM users ORDER BY id")

for row in iter_rows(cursor, 2):
    print(row)
```

The generator fetches up to two rows per application batch.

## 15.4 Dictionary-row helper

A generic helper can use `cursor.description`:

```python
from collections.abc import Iterator
from typing import Any


def iter_dict_rows(cursor: Any, batch_size: int) -> Iterator[dict[str, Any]]:
    """Yield result rows as dictionaries using DB-API column metadata."""
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero")

    description = cursor.description
    if description is None:
        raise ValueError("cursor has no result-column metadata")

    columns = [column[0] for column in description]

    while True:
        rows = cursor.fetchmany(batch_size)
        if not rows:
            break

        for row in rows:
            yield dict(zip(columns, row))
```

This abstraction works because it depends on a common DB-API shape:

```text
cursor.description
cursor.fetchmany()
row is iterable
```

## 15.5 What makes a helper portable?

A helper is more portable when it uses only common concepts:

```python
cursor.fetchmany(batch_size)
cursor.description
```

It becomes less portable when it relies on database-specific extensions:

```python
cursor.some_vendor_only_method(...)
```

The correct boundary is often:

```text
common application logic
        ↓
small portable abstraction
        ↓
driver-specific adapter where necessary
```

## 15.6 Don't fake portability

Bad abstraction:

> “Every database supports this exactly the same way, so I will hide all differences.”

Better abstraction:

> “I will standardize the common operations, and I will make database-specific capabilities explicit where they matter.”

That mindset becomes increasingly important as your systems grow.

---

# 16. What DB-API Does Not Standardize

DB-API is intentionally useful but limited.

## 16.1 No universal connection-string standard

DB-API does not define one universal connection-string grammar that all database drivers must support.

You may encounter:

```text
postgresql://...
sqlite:///...
other-driver-specific forms
```

but these belong to driver/tool ecosystems, not a single universal DB-API connection-string standard.

## 16.2 No universal connection-pooling standard

PEP 249 does not standardize a universal pooling API.

Connection pooling is an operational feature layered above basic DB-API connection semantics.

Topic 05 covers:

- psycopg pools;
- SQLAlchemy pool behavior;
- PgBouncer;
- pool sizing;
- concurrency and connection limits.

## 16.3 No universal bulk-loading standard

The DB-API does not define one universal high-performance bulk-load interface.

A database may provide a specialized bulk path such as PostgreSQL `COPY`.

Topic 09 covers this in detail.

## 16.4 No universal async interface

DB-API 2.0 is not a universal async database API.

Drivers may expose asynchronous interfaces independently.

Async database programming is addressed later in Module 2.10.

## 16.5 Vendor-specific capabilities remain

A PostgreSQL driver may expose PostgreSQL-specific features. Another database driver may expose completely different features.

That is expected.

The standard contract gives you a common floor, not a common ceiling.

A useful metaphor is:

```text
                    Vendor-specific features
               ┌──────────────────────────────┐
               │                              │
        ┌──────┴──────┐                ┌──────┴──────┐
        │ Driver A    │                │ Driver B    │
        │ extensions  │                │ extensions  │
        └──────┬──────┘                └──────┬──────┘
               │                              │
               └──────── DB-API common ───────┘
```

## 16.6 Why higher-level tools exist

Because DB-API intentionally stops at a common low-level interface, higher-level tools can add capabilities such as:

- richer SQL construction;
- metadata modeling;
- pooling configuration;
- dialect abstraction;
- ORM behavior;
- other application-oriented database tooling.

For example:

```text
DB-API drivers
      ↓
SQLAlchemy / higher-level database tooling
```

You will learn SQLAlchemy Core and ORM in Topics 06–07.

Another ecosystem, ADBC, focuses on Arrow-native data interchange and database connectivity. It solves a different interoperability problem and is covered later in this module.

The key lesson is:

> **Multiple layers exist because no single abstraction is optimized for every database-access problem.**

---

# 17. `sqlite3` vs DuckDB: Same Contract, Different Implementations

The roadmap explicitly asks you to compare the same five operations in `sqlite3` and DuckDB.

The purpose is to demonstrate transfer of concepts, not to rank the products.

## 17.1 Five common operations

We will compare:

1. connect;
2. create table;
3. insert;
4. execute a query;
5. fetch results.

## 17.2 Comparison table

| Operation | `sqlite3` | DuckDB Python API | DB-API lesson |
|---|---|---|---|
| Connect | `sqlite3.connect(...)` | `duckdb.connect(...)` | Both expose a connection concept. |
| Create table | Execute SQL through a connection/cursor | Execute SQL through a connection/cursor | SQL/database capabilities remain database-specific. |
| Insert | DB-API parameterized statement | DB-API-style parameterized statement | Parameter styles/capabilities must be checked per driver. |
| Query | `execute(...)` then fetch | `execute(...)` then fetch | Common execution/fetching model transfers. |
| Fetch | `fetchone()`, `fetchmany()`, `fetchall()` | Same common-style methods | Common DB-API concepts make unfamiliar drivers easier to learn. |

## 17.3 `sqlite3` example

```python
import sqlite3

conn = sqlite3.connect(":memory:")
try:
    cursor = conn.cursor()

    cursor.execute(
        "CREATE TABLE users (id INTEGER, name TEXT)"
    )

    cursor.execute(
        "INSERT INTO users (id, name) VALUES (?, ?)",
        (1, "Asha"),
    )

    cursor.execute("SELECT id, name FROM users")
    print(cursor.fetchone())
finally:
    conn.close()
```

## 17.4 DuckDB example

If DuckDB is installed, a comparable example is:

```python
import duckdb

conn = duckdb.connect()
try:
    cursor = conn.cursor()

    cursor.execute(
        "CREATE TABLE users (id INTEGER, name VARCHAR)"
    )

    cursor.execute(
        "INSERT INTO users (id, name) VALUES (?, ?)",
        (1, "Asha"),
    )

    cursor.execute("SELECT id, name FROM users")
    print(cursor.fetchone())
finally:
    conn.close()
```

The exact return types and supported features can differ by implementation and version, so treat this as a conceptual comparison rather than a promise that every capability matches exactly.

## 17.5 What is standardized?

The transferable concepts include:

```text
connect
cursor
execute
fetchone
fetchmany
fetchall
close
```

The implementation-specific parts may include:

- extra methods;
- supported parameter syntax;
- row representation details;
- transaction semantics;
- supported SQL dialect;
- database-specific types;
- performance characteristics;
- additional analytical features.

That is exactly why DB-API is useful: it gives you a starting structure without pretending that databases are the same product.

---

# 18. What Happens Internally?

This section builds the internal mental model required for production reasoning.

Consider:

```python
conn = ...
cursor = conn.cursor()
cursor.execute(...)
rows = cursor.fetchmany(100)
conn.commit()
conn.close()
```

We will separate **guaranteed contract**, **typical behavior**, and **implementation-specific details**.

## 18.1 Step 1 — Python creates or receives a connection object

```python
conn = ...
```

At the Python level, `conn` is an object implemented by the database driver.

Internally, the object may contain references to lower-level resources, state, configuration, buffers, or native resources.

PEP 249 does not specify the internal memory layout of a driver object.

## 18.2 Step 2 — a cursor object is created

```python
cursor = conn.cursor()
```

The driver creates a cursor object associated with the connection.

The exact relationship between Python cursor state and any database-side cursor state is implementation-specific.

## 18.3 Step 3 — Python calls `execute()`

```python
cursor.execute("SELECT ...")
```

At the conceptual level:

```text
Python method call
      ↓
driver receives statement request
      ↓
driver encodes request for target database
      ↓
database receives request
```

The database then processes the operation according to its own execution engine.

## 18.4 Step 4 — database execution

The database may perform work such as:

```text
parse SQL
  ↓
validate objects/types
  ↓
plan/prepare as applicable
  ↓
read data / apply changes
  ↓
produce result/status
```

The exact steps depend on the database.

## 18.5 Step 5 — result handling

For a `SELECT`, the driver obtains information about the result and exposes it through cursor methods.

The crucial point is that PEP 249 does not mandate one exact client-buffering implementation.

A driver may buffer data in ways that are invisible to your Python code.

## 18.6 Step 6 — Python fetches rows

```python
rows = cursor.fetchmany(100)
```

The DB-API interface asks for the next batch of rows.

At the Python level, your program receives Python row objects.

Depending on the driver, creating those objects can itself consume significant memory and CPU for very large datasets.

## 18.7 Step 7 — transaction completion

```python
conn.commit()
```

If the operation is inside a transaction, the driver requests a commit.

The database then applies the commit according to its own transaction semantics.

The exact transaction lifecycle is intentionally explored more deeply in Topic 04.

## 18.8 Step 8 — resource cleanup

```python
conn.close()
```

The driver releases the connection resource.

For a server-based database, that may involve closing the network session and releasing server-side resources associated with the connection.

For an embedded database such as SQLite, it includes releasing the driver's/database handle and associated resources.

## 18.9 Three levels of truth

When reading a driver implementation or documentation, classify statements as:

### Level A — DB-API contract

Examples:

- connection/cursor concepts;
- fetch methods;
- parameter-style concept;
- exception hierarchy;
- threadsafety attribute semantics.

### Level B — typical driver behavior

Examples:

- how results are buffered;
- how Python objects are allocated;
- when a transaction is implicitly started.

These are common patterns but require driver-specific confirmation.

### Level C — database-specific behavior

Examples:

- PostgreSQL session semantics;
- PostgreSQL-specific cursor features;
- SQLite locking behavior;
- DuckDB-specific analytical extensions.

An experienced data engineer does not confuse these levels.

---

# 19. Real Data Engineering Use Cases

DB-API knowledge appears in many production systems even when the final application uses higher-level tooling.

## 19.1 ETL/ELT extraction

A pipeline may execute:

```python
cursor.execute("SELECT ...")
```

and then fetch data in batches for transformation or writing to Parquet.

The important engineering questions become:

- What is the connection lifecycle?
- How large is each batch?
- What does the driver buffer?
- What happens if the query fails?
- What happens if the network/database disappears?

Later Topic 10 addresses large-result streaming.

## 19.2 Staging-table loads

A pipeline may insert rows into a staging table before validation and merge logic.

At the DB-API level, this means understanding:

```text
connection
  ↓
transaction
  ↓
execute / executemany / bulk path
```

Topic 09 handles high-performance bulk loading.

## 19.3 Pipeline metadata tables

A pipeline may record:

- run status;
- start/end timestamps;
- row counts;
- watermarks;
- errors;
- quality-check outcomes.

These often involve small, transactional database operations where ordinary DB-API usage is perfectly appropriate.

## 19.4 Audit tables

An audit record may be written after a processing step:

```python
cursor.execute(
    "INSERT INTO pipeline_audit (...) VALUES (...)"
)
```

The application must know whether that write committed and how to handle failure.

## 19.5 Watermarks

A pipeline may read the last processed value:

```python
cursor.execute(
    "SELECT last_value FROM watermarks WHERE pipeline_name = ?",
    (pipeline_name,),
)
```

Then fetch it:

```python
watermark = cursor.fetchone()
```

The query itself may be simple. The production behavior depends on correct transaction and concurrency design, addressed later in the module.

## 19.6 Data-quality result storage

A pipeline may store validation outcomes:

```text
rule_name
rows_checked
rows_failed
status
run_id
```

Again, the DB-API mental model applies even if the implementation later uses SQLAlchemy Core or another abstraction.

## 19.7 Operational database reads

A data pipeline may need to read a source database without disrupting it.

Understanding connection and cursor behavior helps you reason about:

- query lifetime;
- result size;
- resource usage;
- error handling;
- transaction state.

## 19.8 Warehouse loads

Later in this module you will compare multiple loading mechanisms.

The DB-API foundation lets you understand where a higher-performance loading technique sits relative to ordinary execution calls.

---

# 20. Hands-On Lab

The roadmap requires a `dbapi_basics.py` exercise. Because this module file must remain self-contained and no additional artifact is created here, the exercise is specified and demonstrated entirely in this Markdown file.

## Lab Goal

Build enough practical fluency that you can write a small DB-API program without copying the API from a tutorial.

You will use only:

```python
import sqlite3
```

No external dependency is required.

## 20.1 Before you run anything: predict

For each lab step, answer these questions before executing the code:

1. What Python object is created?
2. What does the driver receive?
3. What SQL reaches the database engine?
4. Does a transaction begin?
5. Is there a result set?
6. How many rows should be available?
7. Where are rows represented once Python fetches them?
8. What happens if `commit()` is omitted?
9. What happens if the cursor is closed?
10. What exception should appear for each intentional failure?

The goal is not speed. The goal is to learn to predict database behavior before observing it.

---

## 20.2 Lab Part A — Create a table

### Goal

Create a table using `sqlite3`.

### Starter code

```python
import sqlite3

conn = sqlite3.connect(":memory:")

try:
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
        """
    )

    print("Table created")
finally:
    conn.close()
```

### Predict

- What is `conn`?
- What is `cursor`?
- Is the `CREATE TABLE` statement a row-producing query?
- Should `fetchone()` be used after this statement?

### Expected observation

You should see:

```text
Table created
```

There is no meaningful result row to fetch from the DDL operation.

### Likely mistake

Trying to treat every SQL statement as if it produces rows.

Correct mental model:

```text
SELECT → usually result rows
INSERT/UPDATE/DELETE/DDL → generally status/change, not a row result
```

---

## 20.3 Lab Part B — Insert rows with parameters

### Goal

Use the `qmark` DB-API parameter style supported by SQLite.

### Starter code

```python
import sqlite3

conn = sqlite3.connect(":memory:")

try:
    cursor = conn.cursor()

    cursor.execute(
        "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL)"
    )

    cursor.execute(
        "INSERT INTO users (id, name) VALUES (?, ?)",
        (1, "Asha"),
    )

    cursor.execute(
        "INSERT INTO users (id, name) VALUES (?, ?)",
        (2, "Rahul"),
    )

    conn.commit()
    print("Inserted rows")
finally:
    conn.close()
```

### Predict

What are the two separate pieces?

```text
SQL structure:
INSERT INTO users (id, name) VALUES (?, ?)

Values:
(1, "Asha")
```

### Expected observation

Two rows should be committed.

### Production lesson

Parameter binding is a core DB-API concept. Topic 03 develops the security implications in depth.

---

## 20.4 Lab Part C — `fetchone()`

### Goal

Fetch one row.

```python
cursor.execute(
    "SELECT id, name FROM users ORDER BY id"
)

row = cursor.fetchone()
print(row)
```

Expected shape:

```text
(1, 'Asha')
```

Then:

```python
row = cursor.fetchone()
print(row)
```

Expected shape:

```text
(2, 'Rahul')
```

A further call after the result is exhausted should return `None`.

---

## 20.5 Lab Part D — `fetchmany(100)`

### Goal

Practice application-side batching.

```python
cursor.execute(
    "SELECT id, name FROM users ORDER BY id"
)

rows = cursor.fetchmany(100)
print(rows)
```

Because only a small number of rows exist, you should get all remaining rows even though the requested batch size is 100.

Remember:

> `fetchmany(100)` means “give me up to 100 available rows,” not “the database contains exactly 100 rows.”

---

## 20.6 Lab Part E — `fetchall()`

### Goal

See the convenience of `fetchall()` and understand the scaling risk.

```python
cursor.execute(
    "SELECT id, name FROM users ORDER BY id"
)

rows = cursor.fetchall()
print(rows)
```

For two rows, this is perfectly reasonable.

Now imagine the result contains:

```text
5 million rows
10 million rows
50 million rows
```

The same syntax would request the remaining rows as one application-level collection.

That is why `fetchall()` should be a deliberate choice, not a reflex.

---

## 20.7 Lab Part F — `cursor.description`

### Goal

Inspect result metadata and produce dictionary rows.

```python
cursor.execute(
    "SELECT id, name FROM users ORDER BY id"
)

columns = [column[0] for column in cursor.description]
print(columns)

rows = cursor.fetchall()
rows_as_dicts = [
    dict(zip(columns, row))
    for row in rows
]

print(rows_as_dicts)
```

Expected column names:

```python
['id', 'name']
```

Expected conceptual result:

```python
[
    {'id': 1, 'name': 'Asha'},
    {'id': 2, 'name': 'Rahul'},
]
```

---

## 20.8 Lab Part G — Trigger `IntegrityError`

### Goal

Create a duplicate primary key.

```python
try:
    cursor.execute(
        "INSERT INTO users (id, name) VALUES (?, ?)",
        (1, "Duplicate"),
    )
except sqlite3.IntegrityError as exc:
    print("Caught expected integrity error:", exc)
```

### Predict

The database should reject the row because `id = 1` already exists.

### Expected reasoning

```text
Duplicate primary key
        ↓
database constraint violation
        ↓
DB-API integrity category
        ↓
specific driver exception
```

---

## 20.9 Lab Part H — Trigger `ProgrammingError`

### Goal

Deliberately send invalid SQL or misuse the API, then catch the driver-specific exception.

```python
try:
    cursor.execute("SELEC id FROM users")
except sqlite3.ProgrammingError as exc:
    print("Caught programming error:", exc)
```

Important caveat: the exact exception classification for a particular invalid statement can vary between drivers. The exercise teaches classification using SQLite; production code must use the actual driver's documented exception classes.

---

## 20.10 Lab Part I — Uncommitted visibility

Use two connections to the same file.

```python
import sqlite3

DB_PATH = "dbapi_visibility.db"

setup = sqlite3.connect(DB_PATH)
try:
    setup.execute("DROP TABLE IF EXISTS users")
    setup.execute(
        "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL)"
    )
    setup.commit()
finally:
    setup.close()

conn_a = sqlite3.connect(DB_PATH, isolation_level="DEFERRED")
conn_b = sqlite3.connect(DB_PATH, isolation_level="DEFERRED")

try:
    conn_a.execute(
        "INSERT INTO users (id, name) VALUES (?, ?)",
        (1, "Asha"),
    )

    print("B before A commits:")
    print(conn_b.execute("SELECT * FROM users").fetchall())

    conn_a.commit()

    print("B after A commits:")
    print(conn_b.execute("SELECT * FROM users").fetchall())
finally:
    conn_a.close()
    conn_b.close()
```

### Expected observation

Before `conn_a.commit()`, `conn_b` should not see the uncommitted row under the normal isolation behavior used here.

After commit, `conn_b` should see it.

### Production lesson

Always understand whether your code has an active transaction. Do not assume that “execute succeeded” means “another connection can now see the change.”

---

## 20.11 Lab Part J — Implement `iter_rows()`

### Goal

Create a generator that fetches in batches without calling `fetchall()`.

```python
from collections.abc import Iterator
from typing import Any


def iter_rows(cursor: Any, batch_size: int) -> Iterator[Any]:
    """Yield rows in application-sized batches."""
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero")

    while True:
        rows = cursor.fetchmany(batch_size)
        if not rows:
            return
        yield from rows
```

### Test with empty table

```python
cursor.execute("SELECT id, name FROM users WHERE 1 = 0")

print(list(iter_rows(cursor, 100)))
```

Expected:

```python
[]
```

### Test with one row

```python
cursor.execute(
    "SELECT id, name FROM users WHERE id = ?",
    (1,),
)

print(list(iter_rows(cursor, 100)))
```

Expected: one row.

### Test with many rows

```python
cursor.execute(
    "SELECT id, name FROM users ORDER BY id"
)

for row in iter_rows(cursor, 2):
    print(row)
```

### Predict before running

If there are seven result rows and `batch_size=2`, the application-level fetch pattern should conceptually be:

```text
2 rows
2 rows
2 rows
1 row
empty → stop
```

---

# 21. Debugging Exercises

Database bugs are often boundary bugs: Python thinks one thing happened while the database or driver did something else.

Use the following debugging workflow:

```text
Observe the Python state
        ↓
Observe the database-facing operation
        ↓
Check transaction/resource state
        ↓
Identify the exact exception
        ↓
Reduce to the smallest failing example
        ↓
Fix the lifecycle/contract violation
```

## Failure 1 — Connection forgotten or leaked

### Problematic code

```python
def load_users():
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM users")
    return cursor.fetchall()
```

### Why it is dangerous

The returned rows do not make the connection lifecycle obvious. In a long-running process, repeated calls can keep resources alive longer than intended.

### Corrected version

```python
def load_users():
    conn = sqlite3.connect("app.db")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM users")
        return cursor.fetchall()
    finally:
        conn.close()
```

### Production lesson

Resource lifetime should be visible in the function that owns the resource unless a broader lifecycle is intentional.

---

## Failure 2 — `fetchall()` on a huge result

### Problematic code

```python
cursor.execute("SELECT * FROM huge_table")
rows = cursor.fetchall()
process(rows)
```

### Why it becomes dangerous

The entire remaining application-visible result is materialized into one Python collection.

### Corrected application-level pattern

```python
cursor.execute("SELECT * FROM huge_table")

while True:
    rows = cursor.fetchmany(1000)
    if not rows:
        break

    process(rows)
```

### Production lesson

Batch application processing reduces peak memory pressure, but the driver may still buffer results internally. For truly large extraction workloads, use mechanisms designed for streaming; that belongs to Topic 10.

---

## Failure 3 — `commit()` forgotten

### Problematic code

```python
conn.execute(
    "INSERT INTO users (name) VALUES (?)",
    ("Asha",),
)

# No commit.
```

### Why it is dangerous

The write may remain inside an open/uncommitted transaction and may not be visible as expected to another connection.

### Corrected foundation-level version

```python
conn.execute(
    "INSERT INTO users (name) VALUES (?)",
    ("Asha",),
)
conn.commit()
```

### Production lesson

Know the transaction state of your connection even when your code does not explicitly issue `BEGIN`.

---

## Failure 4 — Wrong parameter style

### Problematic code

```python
cursor.execute(
    "SELECT * FROM users WHERE id = %s",
    (user_id,),
)
```

This is not correct for a driver expecting `qmark` such as the SQLite example.

### Corrected SQLite version

```python
cursor.execute(
    "SELECT * FROM users WHERE id = ?",
    (user_id,),
)
```

### Production lesson

Parameter syntax belongs to the driver contract. Never assume all DB-API drivers accept the same placeholder syntax.

---

## Failure 5 — Using a closed cursor

### Problematic code

```python
cursor.close()

cursor.execute("SELECT 1")
```

### Why it fails

The cursor lifecycle has ended.

### Corrected version

Create a new cursor when the old one is intentionally closed:

```python
cursor = conn.cursor()
try:
    cursor.execute("SELECT 1")
    print(cursor.fetchone())
finally:
    cursor.close()
```

### Production lesson

Object lifetime is part of correctness, not merely cleanup.

---

## Failure 6 — Catching `Exception` and hiding the failure

### Problematic code

```python
try:
    cursor.execute("...")
except Exception:
    pass
```

### Why it fails operationally

The real problem disappears from logs and control flow.

### Corrected foundation-level approach

```python
try:
    cursor.execute("...")
except sqlite3.IntegrityError as exc:
    print(f"Data integrity problem: {exc}")
except sqlite3.OperationalError as exc:
    print(f"Operational database problem: {exc}")
```

### Production lesson

Specific exceptions communicate intent and enable appropriate handling.

---

## Failure 7 — Assuming `with connection:` always closes the connection

### Problematic assumption

```python
with sqlite3.connect("app.db") as conn:
    conn.execute("...")

# Assumed: conn is always closed.
```

### What actually matters

SQLite's connection context manager controls transaction behavior; it does not itself provide a universal promise that the connection is closed at block exit.

### Correct lifecycle

```python
conn = sqlite3.connect("app.db")
try:
    with conn:
        conn.execute("...")
finally:
    conn.close()
```

### Production lesson

Context-manager semantics are driver-specific.

---

## Failure 8 — Sharing a connection across threads without understanding the driver

### Problematic design

```python
shared_conn = sqlite3.connect("app.db")

# Many worker threads use shared_conn simultaneously.
```

### Why it is dangerous

Thread safety depends on driver guarantees and connection configuration. A driver may allow module sharing while restricting connection or cursor sharing.

### Correct reasoning

First inspect:

```python
print(sqlite3.threadsafety)
```

Then read the driver's concurrency documentation and design explicit ownership of connections/cursors.

### Production lesson

Never use “Python threads work” as evidence that a database connection or cursor is safe for arbitrary concurrent access.

---

# 22. Common Mistakes

The following mistakes are especially important because they reveal an incorrect mental model.

| What beginners think | What actually matters | Production consequence | Correct mental model |
|---|---|---|---|
| “The INSERT succeeded, so it is committed.” | Statement execution and transaction commit are separate concerns. | Data visibility/persistence can be wrong. | Know transaction state. |
| “`with` always closes the connection.” | Context-manager semantics differ by driver. | Leaked resources. | Read the driver contract. |
| “Catch `Exception` so the pipeline never crashes.” | Broad catches can hide root causes. | Silent data loss or corrupted pipeline state. | Catch meaningful exceptions and handle deliberately. |
| “`fetchmany()` means streaming.” | The API controls application fetch size, not all driver buffering behavior. | Memory may still spike on large results. | Distinguish batching from true streaming. |
| “Every database uses `?`.” | Parameter styles differ. | Query failures. | Learn the driver's `paramstyle`. |
| “DB-API makes all databases the same.” | It standardizes common concepts, not every database behavior. | Incorrect assumptions when switching drivers. | Contract ≠ identical implementation. |
| “Threads are safe, so one cursor can be shared.” | Thread safety has explicit levels and driver rules. | Race conditions or failures. | Understand resource ownership and `threadsafety`. |
| “Connections are cheap, so leave them open.” | Connections consume resources and may carry transaction/session state. | Resource exhaustion and harder operations. | Treat connections as valuable resources. |
| “`fetchall()` is the easiest default.” | Large results can produce huge Python objects. | Memory pressure or OOM. | Fetch in controlled batches and choose the right extraction mechanism. |

---

# 23. Interview and Architecture Questions

The goal is to answer these in engineering terms, not by reciting definitions.

## Basic

### 1. What is DB-API?

Explain DB-API as a standard Python database access interface and distinguish it from a specific database engine.

### 2. What is a connection?

Explain it as the active database interaction/session resource managed by the driver.

### 3. What is a cursor?

Explain it as the statement execution and result-handling interface associated with a connection.

### 4. What is the difference between `fetchone()` and `fetchall()`?

Discuss result consumption and memory implications.

### 5. What does `cursor.description` contain?

Explain its role in exposing metadata about result columns.

## Intermediate

### 6. Why does DB-API define parameter styles?

Explain interoperability across historical driver conventions.

### 7. What is `executemany()`?

Explain repeated parameterized operations and why performance is driver-specific.

### 8. Why can `fetchall()` be dangerous?

Explain how a large result becomes a large Python collection and can create memory pressure.

### 9. What is the difference between `Error`, `DatabaseError`, and `IntegrityError`?

Explain the exception hierarchy and why specificity matters.

### 10. Why do context-manager semantics differ between drivers?

Explain that the standard interface does not force every driver to implement identical resource semantics.

### 11. Why might `commit()` be required even when Python never calls `BEGIN`?

Explain implicit transaction behavior.

## Advanced

### 12. What does PEP 249 standardize and what does it not standardize?

Give examples of both common concepts and intentionally unspecified features.

### 13. Why can a DB-API-compatible driver still behave differently from another?

Separate common API contract from database/driver implementation details.

### 14. Why is a cursor not simply equivalent to a server-side cursor?

Distinguish the Python-level DB-API object from an optional database/driver mechanism for server-held result state.

### 15. What does `threadsafety` actually tell you?

Explain levels 0–3 and why application architecture still matters.

### 16. Why does DB-API not provide a universal pooling API?

Explain that pooling is an operational layer outside the narrow database-access contract.

### 17. How would you design a driver-agnostic row iterator?

Explain why `fetchmany()` + a generator is a reasonable abstraction and why it does not guarantee server-side streaming.

### 18. What parts of database access should be standardized by an application abstraction layer?

Discuss common behavior such as row iteration and error boundaries while keeping database-specific capabilities explicit.

### 19. A team changes from SQLite to PostgreSQL. Which assumptions can you carry forward, and which must you re-check?

A strong answer should mention DB-API concepts that transfer and driver/database-specific behavior such as parameter syntax, type adaptation, transaction semantics, error subclasses, concurrency rules, and performance characteristics.

### 20. A query returns 50 million rows. Is `fetchmany(1000)` automatically safe?

A strong answer must say no: it bounds application-level batches but does not itself prove that the driver does not buffer a much larger result. Server-side streaming is a separate concern.

---

# 24. Checkpoint

Do not move on because the definitions look familiar. Complete these from memory.

## Roadmap-aligned checkpoint

- [ ] Explain the roles of a connection and a cursor.
- [ ] Name the five DB-API parameter styles.
- [ ] Map at least three common failures to DB-API exception classes.
- [ ] Explain why `fetchall()` on a large table is dangerous.

## Additional practical checks

- [ ] Write a simple SQLite DB-API program from memory.
- [ ] Use `fetchmany()` correctly.
- [ ] Build dictionary rows from `cursor.description`.
- [ ] Explain implicit transaction behavior.
- [ ] Explain why DB-API knowledge transfers between drivers.
- [ ] Explain at least three things DB-API does not standardize.
- [ ] Explain the difference between standard behavior and driver-specific behavior.
- [ ] Explain the four DB-API `threadsafety` levels.
- [ ] Implement `iter_rows(cursor, batch_size)` without using `fetchall()`.
- [ ] Explain why a DB-API cursor and a server-side cursor are not automatically the same thing.

## Self-test

Answer these without looking back:

1. Your Python process creates a connection. Which layer actually knows the target database protocol?
2. What object normally comes from `connection.cursor()`?
3. Why can two drivers both be DB-API-compatible while using different placeholder syntax?
4. What should `fetchone()` return when there are no rows left?
5. What risk appears when `fetchall()` is called on a huge result?
6. What does `cursor.description` enable?
7. What is the purpose of `rowcount`?
8. What is `arraysize` for?
9. What is the difference between `IntegrityError` and `ProgrammingError`?
10. Why should you not assume a connection context manager closes the connection?
11. What does `threadsafety=1` mean?
12. What does DB-API not standardize about connection pooling?
13. Why can `fetchmany()` be memory-safer at the application level without guaranteeing true streaming?
14. Why is `commit()` a separate concept from `execute()`?
15. What is the most important mental model for moving from one database driver to another?

### Suggested pass condition

You should be able to answer all 15 questions in your own words and implement the core SQLite lab without looking at the examples.

---

# 25. Final Review

## The core flow

```text
Python application
       ↓
DB-API interface
       ↓
Database driver
       ↓
Database/network protocol
       ↓
Database server
```

## The core object relationship

```text
Connection
    ↓
Cursor
    ↓
execute()
    ↓
result/status
    ↓
fetchone()/fetchmany()/fetchall()
```

## The core transaction foundation

```text
transaction-relevant statement
          ↓
    active transaction
          ↓
      commit()
          OR
      rollback()
```

## The core error model

```text
DB-API Error
    ↓
more specific exception category
    ↓
application decides what to do
```

Do not automatically retry every database error and do not automatically swallow every database error.

## The core memory model

```text
fetchall()
    ↓
all remaining result rows
    ↓
large Python collection
```

versus:

```text
fetchmany(batch_size)
    ↓
bounded application batch
    ↓
process
    ↓
next batch
```

But remember:

```text
application batching
        ≠
server-side streaming
```

## The core portability model

```text
DB-API = common interface
Driver  = concrete implementation
Database = engine with its own semantics/capabilities
```

---

# 26. Production Rules to Remember

## Rules I should remember

1. **Know what layer you are working with.**
2. **Treat connections as valuable resources.**
3. **Treat cursors as scoped database-operation interfaces.**
4. **Do not assume all database drivers behave identically.**
5. **Understand the parameter style of the driver you use.**
6. **Do not blindly use `fetchall()` for large datasets.**
7. **Understand transaction behavior even when it is implicit.**
8. **Catch meaningful database exceptions.**
9. **Do not hide database failures.**
10. **Know what PEP 249 guarantees and what it leaves to drivers.**
11. **Separate application-level batching from true server-side streaming.**
12. **Do not confuse a DB-API cursor with a database server-side cursor.**
13. **Make resource ownership and lifecycle visible in production code.**
14. **Treat thread-safety as a driver contract that must be understood, not guessed.**
15. **Use abstraction to capture common behavior, not to erase meaningful database differences.**

---

## Most Important Mental Model

```text
DB-API gives you a common interface.
The driver implements that interface.
The database still has its own behavior and capabilities.
```

Or, in one sentence:

> **Learn DB-API once so that each new database driver becomes a new implementation to investigate, not a completely new mental model to memorize.**

---

# Preparing for Topic 02

You should now be comfortable with:

```text
DB-API concept
      ↓
Driver concept
      ↓
Connection
      ↓
Cursor
      ↓
Execute
      ↓
Fetch
      ↓
Parameters
      ↓
Exceptions
      ↓
Transactions
      ↓
Resource lifecycle
      ↓
Driver-specific differences
```

The next topic, `02-postgresql-from-python-with-psycopg.md`, will take this abstract foundation and apply it to PostgreSQL with `psycopg`.

It will go deeper into PostgreSQL-specific connection configuration, row factories, type adaptation, time zones, timeouts, PostgreSQL-specific error classes, parameter binding details, pipeline mode, and other driver-specific capabilities.

That separation is intentional:

```text
Topic 01
Common DB-API mental model
        ↓
Topic 02
Concrete PostgreSQL + psycopg implementation
```

---

# Quick Reference Cheat Sheet

| Concept | What to remember |
|---|---|
| Connection | Database interaction/session resource. |
| Cursor | Statement execution/result handling interface associated with a connection. |
| `connect()` | Create/open a connection. |
| `cursor()` | Create a cursor from a connection. |
| `execute()` | Execute one database operation. |
| `executemany()` | Execute a repeated parameterized operation over multiple parameter sets. |
| `fetchone()` | Fetch one next row; returns `None` when exhausted. |
| `fetchmany()` | Fetch up to a requested number of rows. |
| `fetchall()` | Fetch all remaining rows; can create large Python memory usage. |
| `description` | Result-column metadata. |
| `rowcount` | Operation row-count information, subject to driver/database limitations. |
| `arraysize` | Default fetch batch size used by `fetchmany()` when size is omitted. |
| `commit()` | Complete the current transaction. |
| `rollback()` | Undo the current transaction's uncommitted work where supported. |
| `close()` | Release a database resource. |
| `paramstyle` | DB-API parameter placeholder convention used by a driver. |
| `IntegrityError` | Integrity/constraint-related database failure. |
| `OperationalError` | Operational/database availability type of failure. |
| `ProgrammingError` | Common category for API misuse or invalid SQL/programming problems. |
| `threadsafety` | DB-API indicator describing what database module/connection/cursor sharing is supported across threads. |
| DB-API | Common Python database access contract. |
| Driver | Concrete implementation of the database-access interface. |
| Server-side cursor | Optional driver/database mechanism; not automatically the same as a Python DB-API cursor. |

---

## Final Principle

A production Data Engineer should be able to look at database code and ask:

```text
What Python object owns this resource?
What driver is underneath it?
What does the DB-API contract guarantee here?
What is driver-specific?
What does the database actually do?
What is the transaction state?
How many rows are moving?
Where are those rows held?
What happens if this fails?
Who is responsible for cleanup?
```

Those questions are more valuable than memorizing method names in isolation.

Once this mental model becomes automatic, PostgreSQL drivers, analytical database drivers, warehouse connectors, and higher-level database tools become much easier to understand because you can always locate them within the same underlying architecture.
