# PostgreSQL from Python with psycopg

## Learning Objectives

By the end of this module, you should be able to:

- Install and verify **psycopg 3**.
- Explain where psycopg sits between Python and PostgreSQL.
- Connect to PostgreSQL with a connection string or keyword arguments.
- Load connection settings from environment variables without hard-coding credentials.
- Use psycopg 3 connection and cursor context managers correctly.
- Understand psycopg row factories, including `dict_row`, `namedtuple_row`, and `class_row`.
- Explain Python ↔ PostgreSQL type adaptation and round-trip values safely.
- Use timezone-aware UTC datetimes with PostgreSQL `timestamptz`.
- Configure `connect_timeout`, `application_name`, `sslmode`, and `statement_timeout`.
- Observe PostgreSQL sessions through `pg_stat_activity`.
- Recognize and classify important PostgreSQL-specific psycopg exceptions.
- Explain SQLSTATE and why it is useful for machine-readable error handling.
- Explain server-side versus client-side parameter binding.
- Understand prepared statements and their interaction with connection poolers.
- Understand psycopg pipeline mode, text/binary transfer, and custom type adaptation at an advanced level.
- Explain `LISTEN` / `NOTIFY` and recognize `AsyncConnection`.
- Recognize common psycopg2 legacy patterns while keeping psycopg 3 as the primary API.
- Build a production-oriented PostgreSQL connection factory.

## Prerequisites

You should complete:

`01-db-api-pep-249-connections-and-cursors.md`

Topic 01 taught the DB-API contract: connections, cursors, execution, fetching, parameter styles, exception categories, implicit transactions, and resource lifecycle.

This topic teaches how that contract is implemented for **PostgreSQL through psycopg 3**.

The module assumes a PostgreSQL 16+ Docker environment from Module 2.7. The examples use Python 3.12+.

> **Scope boundary:** parameterized-query security belongs primarily to Topic 03, detailed transaction engineering belongs to Topic 04, connection pooling to Topic 05, SQLAlchemy to Topics 06–07, Alembic to Topic 08, bulk loading with `COPY` to Topic 09, and large-result streaming to Topic 10. Those subjects are only referenced here when needed to understand psycopg's role.

---

# Why This Topic Matters

Python is often the orchestration layer of a data pipeline, but PostgreSQL is the system that owns the data and executes the SQL.

That means a real data engineer constantly crosses this boundary:

```text
Python application
      ↓
DB-API concepts
      ↓
psycopg 3 driver
      ↓
PostgreSQL protocol
      ↓
PostgreSQL server
      ↓
Storage + query execution
```

A Python program does not directly "run SQL inside Python."

Instead, Python asks a **driver** to communicate with PostgreSQL. The driver turns Python-level operations into protocol messages PostgreSQL understands, receives the server's responses, and adapts database values into Python objects.

This matters because many production failures occur at the boundary:

- the wrong host or credentials are used;
- a connection hangs for too long;
- a timestamp is sent without timezone information;
- a database error is reduced to a meaningless generic exception;
- a long-running statement has no timeout;
- a service cannot be identified in `pg_stat_activity`;
- Python code assumes a row is a dictionary when the driver returned a tuple;
- a feature works with psycopg 2 but behaves differently with psycopg 3.

The goal of this module is therefore not memorizing psycopg method names.

The goal is to build a mental model that lets you understand unfamiliar PostgreSQL client code later.

---

# 1. The Python → PostgreSQL Architecture

## 1.1 The layers

Think in layers:

```text
Your Python application
        ↓
DB-API interface
        ↓
psycopg 3 driver
        ↓
PostgreSQL wire/network protocol
        ↓
PostgreSQL server
        ↓
Storage / query execution
```

Each layer has a different responsibility.

### Python application

Your code decides:

- which database operation to perform;
- what connection settings to use;
- which SQL statement to send;
- which Python values to supply;
- what to do with returned rows;
- how to handle failures.

Python does **not** implement the PostgreSQL protocol itself.

### DB-API interface

The DB-API defines common Python database concepts such as:

- connections;
- cursors;
- `execute()`;
- `fetchone()`;
- `fetchmany()`;
- `fetchall()`;
- database-related exceptions.

It is a contract.

### psycopg 3

psycopg is the concrete PostgreSQL driver.

It knows how to talk to PostgreSQL and exposes PostgreSQL-specific capabilities while presenting a Python API based on DB-API concepts.

### PostgreSQL protocol

The driver and server communicate using PostgreSQL's wire protocol.

The details are handled by psycopg and PostgreSQL rather than by normal application code.

### PostgreSQL server

PostgreSQL is the database system that:

- authenticates the connection;
- parses SQL;
- plans and executes statements;
- reads and writes data;
- enforces constraints;
- manages transactions and sessions;
- returns results and errors.

## 1.2 What happens during a query?

Suppose Python executes:

```python
result = conn.execute(
    "SELECT id, total FROM orders WHERE id = %s",
    (order_id,),
)
```

Conceptually:

```text
Python
  ↓
conn.execute(...)
  ↓
psycopg receives SQL + Python parameter
  ↓
psycopg prepares protocol messages / parameter representation
  ↓
PostgreSQL receives the request
  ↓
PostgreSQL parses / plans / executes
  ↓
PostgreSQL produces result rows
  ↓
psycopg receives database values
  ↓
psycopg adapts values into Python objects
  ↓
Python receives a result/cursor-like object
  ↓
fetchone()/fetchmany()/fetchall()
```

The important mental model is:

> **Python asks. psycopg translates and communicates. PostgreSQL executes. psycopg translates results back.**

## 1.3 Who controls what?

| Concern | Python application | psycopg | PostgreSQL |
|---|---:|---:|---:|
| Which query to request | Yes | No | No |
| Connection configuration | Yes | Interprets it | Applies server rules |
| PostgreSQL wire protocol | No | Yes | Yes |
| SQL execution | Requests it | Communicates it | Yes |
| Python ↔ PostgreSQL type adaptation | Chooses Python values | Yes | Defines database types |
| Query planning | No | No | Yes |
| Constraints | No | No | Yes |
| Session settings | Requests/configures | Transmits | Stores/applies |
| Row representation in Python | Often chooses | Helps implement | No |
| Connection cleanup | Requests/closes | Implements protocol/resource handling | Releases server-side session/resources |

The table is deliberately simplified. Real behavior depends on the driver and PostgreSQL.

---

# 2. What Is PEP 249 / DB-API?

## 2.1 PEP 249 in plain language

**PEP 249** defines the Python Database API Specification 2.0.

In simple terms:

> PEP 249 defines a common shape for Python programs that talk to relational databases.

That common shape includes concepts such as:

```python
connect(...)
connection.cursor()
cursor.execute(...)
cursor.fetchone()
connection.commit()
connection.rollback()
connection.close()
```

A driver can implement that contract for a specific database.

For example:

```text
sqlite3  ──┐
psycopg  ──┼──> DB-API concepts
DuckDB   ──┘
```

The implementations are not identical.

## 2.2 Why have a standard?

Without a common interface, every Python database integration could invent completely unrelated concepts.

A common contract means that after learning:

```python
connection
cursor
execute
fetch
commit
rollback
```

you already recognize the major shape of another database driver.

That dramatically lowers the learning cost of new systems.

## 2.3 Standardized interface vs implementation

There are three different ideas:

### Standardized interface

Examples:

- connections;
- cursors;
- execution;
- fetching;
- common exception hierarchy;
- parameter-style metadata.

### Driver implementation

psycopg decides how those concepts work for PostgreSQL.

SQLite's `sqlite3` decides how they work for SQLite.

DuckDB's Python integration decides how they work for DuckDB.

### Database-specific capabilities

PostgreSQL has capabilities that the common DB-API contract does not fully describe.

Examples include:

- PostgreSQL-specific SQL;
- SQLSTATE details;
- PostgreSQL `LISTEN` / `NOTIFY`;
- PostgreSQL-specific type adapters;
- PostgreSQL protocol features.

So:

> **DB-API gives you a common programming model. It does not turn PostgreSQL, SQLite, and DuckDB into the same database.**

---

# 3. Installing psycopg 3

## 3.1 Install it in the project

For this module's `uv` project:

```bash
uv add "psycopg[binary]"
```

The package name is `psycopg`.

The `[binary]` extra asks for the binary distribution that makes installation easier in many development environments.

For this learning module, that avoids unnecessary native-build complexity.

## 3.2 Import psycopg

```python
import psycopg
```

A minimal verification program:

```python
import psycopg

print(psycopg.__version__)
```

Run it inside the project environment:

```bash
uv run python your_script.py
```

The important engineering habit is:

> Verify which Python environment and package version your program is actually using.

A surprisingly common debugging problem is installing a package into one environment and running code in another.

## 3.3 Installation mental model

```text
uv project
   ↓
psycopg package
   ↓
Python import
   ↓
psycopg 3 API
   ↓
PostgreSQL
```

---

# 4. Your First PostgreSQL Connection

## 4.1 The smallest connection example

```python
import psycopg

conn = psycopg.connect(
    "postgresql://user:password@localhost:5432/mydb"
)

conn.close()
```

The code means:

1. import psycopg;
2. ask psycopg to connect;
3. PostgreSQL connection details are provided;
4. receive a connection object;
5. close the connection.

## 4.2 Understanding the connection string

This part:

```text
postgresql://user:password@localhost:5432/mydb
```

contains:

| Part | Meaning |
|---|---|
| `postgresql://` | connection URI scheme |
| `user` | PostgreSQL username |
| `password` | password |
| `localhost` | PostgreSQL host |
| `5432` | PostgreSQL TCP port |
| `mydb` | database name |

Do not confuse a URI with the DB-API standard.

The DB-API does **not** require one universal connection-string syntax.

psycopg supports PostgreSQL-style connection information, including URI-like forms.

## 4.3 Keyword-argument style

You can also write:

```python
import psycopg

conn = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="mydb",
    user="app_user",
    password="development-only-secret",
)

conn.close()
```

This can be easier to read and configure programmatically.

## 4.4 URI versus keyword arguments

Neither form is universally "better."

URI form is convenient when:

- a platform already provides a connection URI;
- connection settings are passed as one string.

Keyword arguments are convenient when:

- settings are assembled from structured configuration;
- you want to validate fields separately;
- connection options need to be explicit.

Both ultimately provide psycopg with connection information.

## 4.5 What happens if connection fails?

This:

```python
conn = psycopg.connect(...)
```

does not guarantee a connection.

Possible problems include:

- PostgreSQL is not running;
- hostname cannot be resolved;
- port is wrong;
- credentials are wrong;
- database does not exist;
- TLS requirements are incompatible;
- connection timeout expires.

A production program should not assume that database connectivity always works.

---

# 5. Secure Environment-Based Configuration

## 5.1 Why configuration belongs outside source code

This is unsafe for production code:

```python
conn = psycopg.connect(
    "postgresql://etl_user:super-secret-password@db.internal:5432/warehouse"
)
```

The password is now part of the source code.

Source code can appear in:

- Git repositories;
- pull requests;
- CI logs;
- code-review tools;
- copied snippets;
- backup systems.

Instead, configuration should be supplied externally.

## 5.2 Common PostgreSQL environment variables

A common environment-based setup is:

```text
PGHOST
PGPORT
PGDATABASE
PGUSER
PGPASSWORD
```

For example, a local shell might provide:

```bash
export PGHOST=localhost
export PGPORT=5432
export PGDATABASE=warehouse
export PGUSER=etl_user
export PGPASSWORD='local-development-secret'
```

The exact production secret mechanism can be more sophisticated.

The principle remains:

> **Code defines behavior. Environment or a secret system supplies environment-specific credentials and settings.**

## 5.3 `.pgpass`

PostgreSQL also supports a `.pgpass` mechanism for storing connection passwords outside application source code.

Conceptually:

```text
host:port:database:user:password
```

On systems where `.pgpass` is used, permissions and file handling matter.

Do not treat `.pgpass` as a reason to print or commit credentials.

## 5.4 A small settings loader

Keep the settings logic explicit.

```python
from dataclasses import dataclass
import os


@dataclass(frozen=True)
class PostgresSettings:
    host: str
    port: int
    dbname: str
    user: str
    password: str


def load_settings() -> PostgresSettings:
    required = {
        "PGHOST": os.getenv("PGHOST"),
        "PGPORT": os.getenv("PGPORT"),
        "PGDATABASE": os.getenv("PGDATABASE"),
        "PGUSER": os.getenv("PGUSER"),
        "PGPASSWORD": os.getenv("PGPASSWORD"),
    }

    missing = [name for name, value in required.items() if not value]

    if missing:
        raise RuntimeError(
            f"Missing PostgreSQL settings: {', '.join(missing)}"
        )

    return PostgresSettings(
        host=required["PGHOST"],
        port=int(required["PGPORT"]),
        dbname=required["PGDATABASE"],
        user=required["PGUSER"],
        password=required["PGPASSWORD"],
    )
```

Notice what this example does **not** do:

```python
print(settings.password)
```

or:

```python
logger.info("Connecting with password=%s", settings.password)
```

Credentials are operationally sensitive.

## 5.5 Better mental model

```text
Source code
   +
Environment / secret provider
   ↓
Connection settings
   ↓
psycopg.connect(...)
```

Later modules can introduce richer secret-management systems, but the basic rule starts here.

---

# 6. Connection Context Managers

## 6.1 Why `with psycopg.connect(...)` matters

The explicit pattern:

```python
conn = psycopg.connect(...)

try:
    ...
finally:
    conn.close()
```

works, but psycopg 3 provides a connection context manager.

```python
with psycopg.connect(...) as conn:
    ...
```

For psycopg 3, the roadmap's intended behavior is:

- commit on successful context exit;
- roll back on exception;
- close the connection.

That is extremely useful because the lifecycle is tied to a Python block.

## 6.2 Successful operation

```python
import psycopg

with psycopg.connect(
    "postgresql://app_user@localhost:5432/mydb"
) as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS demo (
            id integer PRIMARY KEY,
            name text NOT NULL
        )
        """
    )
```

Conceptually:

```text
enter with-block
    ↓
connection is usable
    ↓
SQL executes
    ↓
block exits successfully
    ↓
psycopg commits
    ↓
connection closes
```

## 6.3 Failure path

```python
import psycopg

try:
    with psycopg.connect(
        "postgresql://app_user@localhost:5432/mydb"
    ) as conn:
        conn.execute(
            "INSERT INTO demo (id, name) VALUES (1, 'Alice')"
        )

        raise RuntimeError("something failed")
except RuntimeError:
    print("Python handled the failure")
```

Conceptually:

```text
enter
  ↓
statement executes
  ↓
Python exception
  ↓
context manager sees exception
  ↓
rollback
  ↓
connection closes
  ↓
exception continues outward
```

The important point is that the context manager controls resource and transaction behavior according to psycopg 3's documented semantics.

## 6.4 Do not generalize blindly

Topic 01 already showed an important warning:

> Context-manager behavior can differ between DB-API drivers.

For example, a context manager may manage transaction behavior without meaning that the connection is closed.

Therefore:

> **Always understand the specific driver's lifecycle semantics.**

---

# 7. Cursor Context Managers

## 7.1 The explicit cursor form

A cursor is a DB-API object used to execute database operations and work with returned results.

With psycopg:

```python
with psycopg.connect(...) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM customers")
        row = cur.fetchone()
```

There are two scopes:

```text
connection scope
└── cursor scope
    └── SQL operation
```

The cursor is narrower in responsibility than the connection.

## 7.2 Connection versus cursor

Think of it this way:

```text
Connection
    = relationship/session with PostgreSQL

Cursor
    = interface for executing a statement and consuming its result
```

A single connection can create more than one cursor over its lifetime.

The exact concurrency and cursor semantics remain driver-specific.

## 7.3 Cursor lifecycle

A typical sequence is:

```text
connection opened
     ↓
cursor created
     ↓
statement executed
     ↓
result consumed
     ↓
cursor closed
     ↓
connection remains usable
     ↓
connection closed
```

The key idea is scope.

Do not keep a cursor alive longer than necessary merely because the connection remains open.

---

# 8. `conn.execute()` Shortcut

psycopg 3 supports a convenience form:

```python
with psycopg.connect(...) as conn:
    result = conn.execute(
        "SELECT id, name FROM customers"
    )
    row = result.fetchone()
```

This is useful for short, simple operations.

## 8.1 Why does this exist?

Because many operations do not need you to manually write:

```python
with conn.cursor() as cur:
    cur.execute(...)
```

every time.

The shortcut keeps concise code readable.

## 8.2 What it does not mean

Do not conclude:

> "There is no cursor concept anymore."

The cursor/result machinery is still conceptually important.

The shortcut is an API convenience.

Use an explicit cursor when it makes the lifecycle or code structure clearer.

---

# 9. Row Factories

A normal result can be represented as tuples.

For example:

```python
(101, "Alice")
```

That is compact, but application code becomes less self-describing:

```python
row[0]
row[1]
```

psycopg provides **row factories**.

A row factory controls how returned rows are represented in Python.

## 9.1 `dict_row`

```python
from psycopg.rows import dict_row
import psycopg

with psycopg.connect(
    "postgresql://app_user@localhost:5432/mydb",
    row_factory=dict_row,
) as conn:
    rows = conn.execute(
        "SELECT id, name FROM customers ORDER BY id"
    ).fetchall()

print(rows)
```

The rows are conceptually:

```python
[
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
]
```

Now code can be explicit:

```python
for row in rows:
    print(row["name"])
```

instead of:

```python
for row in rows:
    print(row[1])
```

## 9.2 When `dict_row` helps

It is especially readable for:

- metadata queries;
- dynamic column sets;
- ad hoc pipeline logic;
- APIs that naturally use named fields.

Trade-off:

- dictionary-style rows carry more structure than plain tuples.

For high-volume processing, row representation can affect memory and CPU.

## 9.3 `namedtuple_row`

```python
from psycopg.rows import namedtuple_row
import psycopg

with psycopg.connect(
    "postgresql://app_user@localhost:5432/mydb",
    row_factory=namedtuple_row,
) as conn:
    row = conn.execute(
        "SELECT id, name FROM customers WHERE id = %s",
        (1,),
    ).fetchone()

print(row.id)
print(row.name)
```

This keeps named field access while behaving like a tuple-like structure.

A useful mental model:

```text
tuple       → row[0]
namedtuple  → row.id
dict        → row["id"]
```

## 9.4 `class_row(MyDataclass)`

For strongly structured pipeline code, a dataclass can be useful.

```python
from dataclasses import dataclass

from psycopg.rows import class_row
import psycopg


@dataclass(frozen=True)
class Order:
    id: int
    customer_id: int
    total: float


with psycopg.connect(
    "postgresql://app_user@localhost:5432/mydb",
    row_factory=class_row(Order),
) as conn:
    order = conn.execute(
        """
        SELECT id, customer_id, total
        FROM orders
        WHERE id = %s
        """,
        (101,),
    ).fetchone()

print(order)
print(order.id)
```

The row is mapped into an `Order` instance.

## 9.5 Choosing a row representation

There is no universal winner.

| Row style | Strength | Trade-off |
|---|---|---|
| Tuple/default | Compact, simple | Positional access is less expressive |
| `dict_row` | Very readable named access | More Python object overhead |
| `namedtuple_row` | Named + tuple-like | Less flexible than a dict |
| `class_row` | Domain-oriented objects | More modeling overhead |

Production rule:

> Choose row representation based on readability, volume, downstream interfaces, and memory requirements.

---

# 10. Python ↔ PostgreSQL Type Adaptation

## 10.1 What is type adaptation?

Type adaptation is the process by which psycopg translates values across the Python/PostgreSQL boundary.

Conceptually:

```text
Python object
    ↓
psycopg adapter
    ↓
PostgreSQL value
```

and:

```text
PostgreSQL value
    ↓
psycopg loader
    ↓
Python object
```

For example:

```text
Python int
    ↕
PostgreSQL integer
```

The important distinction is:

> SQL text is not the same thing as a Python object.

Psycopg has to represent Python values in a form PostgreSQL understands and convert PostgreSQL result values back into useful Python objects.

---

# 11. Integer Mapping

A core mapping is:

```text
Python int
    ↕
PostgreSQL integer / bigint
```

Example:

```python
import psycopg

with psycopg.connect(...) as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS numbers (
            value bigint
        )
        """
    )

    value = 9_000_000
    conn.execute(
        "INSERT INTO numbers (value) VALUES (%s)",
        (value,),
    )
```

When PostgreSQL returns the value, psycopg can produce a Python integer.

## 11.1 Range still matters

Python integers are flexible, but PostgreSQL integer types have defined ranges.

For example:

```text
integer → 32-bit signed range
bigint  → 64-bit signed range
```

So "Python supports this integer" does not mean "PostgreSQL can store this integer in every integer column."

A production engineer thinks about the **database schema** and not only the Python type.

---

# 12. `Decimal` ↔ `numeric`

A common mapping is:

```text
Python Decimal
      ↕
PostgreSQL numeric
```

Use `Decimal` when exact decimal representation matters.

```python
from decimal import Decimal

import psycopg

amount = Decimal("1234.56")

with psycopg.connect(...) as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS payments (
            id integer PRIMARY KEY,
            amount numeric(12, 2)
        )
        """
    )

    conn.execute(
        "INSERT INTO payments (id, amount) VALUES (%s, %s)",
        (1, amount),
    )

    row = conn.execute(
        "SELECT amount FROM payments WHERE id = %s",
        (1,),
    ).fetchone()

print(row)
```

For financial values, exact decimal semantics are usually preferable to relying on binary floating-point.

The important engineering model is:

```text
money-like value
    ↓
Decimal
    ↓
numeric(precision, scale)
```

The database schema still defines the final allowed precision and scale.

---

# 13. Timezone-Aware Datetimes and `timestamptz`

This is one of the most important production concepts in the module.

## 13.1 Naive versus aware datetime

A naive datetime:

```python
from datetime import datetime

value = datetime(2026, 9, 29, 10, 30)
```

does not carry timezone information.

An aware UTC datetime:

```python
from datetime import datetime, timezone

value = datetime.now(timezone.utc)
```

does.

For production pipeline timestamps, prefer the aware UTC form.

## 13.2 PostgreSQL `timestamptz`

A common mapping is:

```text
timezone-aware Python datetime
              ↕
PostgreSQL timestamptz
```

The PostgreSQL type name `timestamptz` is often misunderstood.

It is better to think:

> `timestamptz` represents an absolute point in time, with PostgreSQL using timezone information when interpreting or displaying timestamp values.

It does not mean PostgreSQL stores a timezone label such as `"Asia/Kolkata"` with every timestamp.

## 13.3 Why UTC?

Suppose one service runs in India and another in the United States.

Local time representations become ambiguous when systems exchange timestamps.

A consistent convention is:

```text
Application timestamps
        ↓
timezone-aware
        ↓
UTC
        ↓
database
```

Then convert for human presentation at the edges.

## 13.4 Round-trip example

```python
from datetime import datetime, timezone

import psycopg

created_at = datetime.now(timezone.utc)

with psycopg.connect(...) as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id integer PRIMARY KEY,
            created_at timestamptz NOT NULL
        )
        """
    )

    conn.execute(
        "INSERT INTO events (id, created_at) VALUES (%s, %s)",
        (1, created_at),
    )

    row = conn.execute(
        "SELECT created_at FROM events WHERE id = %s",
        (1,),
    ).fetchone()

    returned = row[0]

print(returned)
print(returned.tzinfo)
```

The exact textual display can depend on session settings, but the returned Python value should be treated as timezone-aware.

## 13.5 Production warning

Do not casually mix:

```python
datetime.now()
```

with:

```python
datetime.now(timezone.utc)
```

in the same pipeline.

A timestamp without timezone semantics creates ambiguity that can become a data-quality problem.

---

# 14. `date` ↔ PostgreSQL `date`

A Python `date` represents a calendar date without a time-of-day.

```python
from datetime import date

business_date = date(2026, 9, 29)
```

PostgreSQL has:

```sql
date
```

A simple round trip:

```python
from datetime import date

import psycopg

business_date = date(2026, 9, 29)

with psycopg.connect(...) as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_metrics (
            day date
        )
        """
    )

    conn.execute(
        "INSERT INTO daily_metrics (day) VALUES (%s)",
        (business_date,),
    )

    row = conn.execute(
        "SELECT day FROM daily_metrics"
    ).fetchone()

print(row[0])
```

Do not replace a date with a datetime merely because Python supports both.

Use the type that matches the data's meaning.

---

# 15. UUID ↔ PostgreSQL `uuid`

Python's standard library provides UUID objects:

```python
from uuid import UUID, uuid4

customer_id = uuid4()
print(customer_id)
```

PostgreSQL provides:

```sql
uuid
```

Round-trip example:

```python
from uuid import uuid4

import psycopg

customer_id = uuid4()

with psycopg.connect(...) as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS customers_uuid (
            id uuid PRIMARY KEY
        )
        """
    )

    conn.execute(
        "INSERT INTO customers_uuid (id) VALUES (%s)",
        (customer_id,),
    )

    row = conn.execute(
        "SELECT id FROM customers_uuid WHERE id = %s",
        (customer_id,),
    ).fetchone()

print(type(row[0]))
print(row[0])
```

The goal is not merely that the value "looks right."

A type-aware application should preserve the semantic type.

---

# 16. Python Lists ↔ PostgreSQL Arrays

psycopg can adapt Python lists to PostgreSQL array values when the target database column is an array.

Conceptually:

```text
Python list
    ↕
PostgreSQL array
```

Example schema:

```sql
CREATE TABLE IF NOT EXISTS tagged_items (
    id integer PRIMARY KEY,
    tags text[]
)
```

Python:

```python
tags = ["python", "postgresql", "etl"]

with psycopg.connect(...) as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tagged_items (
            id integer PRIMARY KEY,
            tags text[]
        )
        """
    )

    conn.execute(
        "INSERT INTO tagged_items (id, tags) VALUES (%s, %s)",
        (1, tags),
    )

    row = conn.execute(
        "SELECT tags FROM tagged_items WHERE id = %s",
        (1,),
    ).fetchone()

print(row[0])
```

## 16.1 Array is not JSON

These are different database types:

```text
text[]      → PostgreSQL array
jsonb       → JSON document/value
```

Both can represent lists, but they have different database semantics.

The schema must match the application's intent.

---

# 17. `Jsonb(...)` ↔ PostgreSQL `jsonb`

psycopg provides explicit JSON adaptation helpers.

```python
from psycopg.types.json import Jsonb
```

A Python dictionary:

```python
payload = {
    "source": "billing",
    "attempt": 2,
    "tags": ["retry", "important"],
}
```

can be adapted for a `jsonb` column:

```python
from psycopg.types.json import Jsonb
import psycopg

payload = {
    "source": "billing",
    "attempt": 2,
    "tags": ["retry", "important"],
}

with psycopg.connect(...) as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_events (
            id integer PRIMARY KEY,
            payload jsonb NOT NULL
        )
        """
    )

    conn.execute(
        "INSERT INTO audit_events (id, payload) VALUES (%s, %s)",
        (1, Jsonb(payload)),
    )

    row = conn.execute(
        "SELECT payload FROM audit_events WHERE id = %s",
        (1,),
    ).fetchone()

print(row[0])
```

The conceptual transformation is:

```text
Python dict
    ↓
JSON serialization/adaptation
    ↓
PostgreSQL jsonb
```

Use a relational column when a value is fundamentally relational and queryable as a stable attribute.

Use JSONB when a semi-structured document is a deliberate part of the data model.

This section is about connectivity and type adaptation, not advanced PostgreSQL JSON querying.

---

# 18. `None` ↔ SQL `NULL`

A simple mapping is:

```text
Python None
    ↕
SQL NULL
```

Example:

```python
import psycopg

with psycopg.connect(...) as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS optional_values (
            id integer PRIMARY KEY,
            note text
        )
        """
    )

    conn.execute(
        "INSERT INTO optional_values (id, note) VALUES (%s, %s)",
        (1, None),
    )

    row = conn.execute(
        "SELECT note FROM optional_values WHERE id = %s",
        (1,),
    ).fetchone()

print(row[0] is None)
```

Remember:

```text
None != ""
None != "NULL"
None != []
```

`NULL` has database semantics of "unknown/missing/not present," depending on the model.

Application logic must respect column nullability and SQL's three-valued logic where relevant.

---

# 19. Type Round-Trip Lab

The roadmap requires you to round-trip all important Python types through PostgreSQL.

This lab should be treated as a prediction exercise.

## 19.1 Before you run it

Predict:

- what Python object is sent for each field;
- what PostgreSQL type receives it;
- what Python type should come back;
- where a mismatch could happen.

## 19.2 Example

```python
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

import psycopg
from psycopg.types.json import Jsonb


def round_trip_values() -> None:
    source = {
        "integer_value": 123,
        "decimal_value": Decimal("19.95"),
        "timestamp_value": datetime.now(timezone.utc),
        "date_value": date(2026, 9, 29),
        "uuid_value": uuid4(),
        "tags": ["etl", "postgres"],
        "payload": {"source": "pipeline", "attempt": 1},
        "nullable_value": None,
    }

    with psycopg.connect(...) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS type_round_trip (
                id integer PRIMARY KEY,
                integer_value bigint,
                decimal_value numeric(12, 2),
                timestamp_value timestamptz,
                date_value date,
                uuid_value uuid,
                tags text[],
                payload jsonb,
                nullable_value text
            )
            """
        )

        conn.execute(
            """
            INSERT INTO type_round_trip (
                id,
                integer_value,
                decimal_value,
                timestamp_value,
                date_value,
                uuid_value,
                tags,
                payload,
                nullable_value
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                integer_value = EXCLUDED.integer_value,
                decimal_value = EXCLUDED.decimal_value,
                timestamp_value = EXCLUDED.timestamp_value,
                date_value = EXCLUDED.date_value,
                uuid_value = EXCLUDED.uuid_value,
                tags = EXCLUDED.tags,
                payload = EXCLUDED.payload,
                nullable_value = EXCLUDED.nullable_value
            """,
            (
                1,
                source["integer_value"],
                source["decimal_value"],
                source["timestamp_value"],
                source["date_value"],
                source["uuid_value"],
                source["tags"],
                Jsonb(source["payload"]),
                source["nullable_value"],
            ),
        )

        row = conn.execute(
            """
            SELECT
                integer_value,
                decimal_value,
                timestamp_value,
                date_value,
                uuid_value,
                tags,
                payload,
                nullable_value
            FROM type_round_trip
            WHERE id = %s
            """,
            (1,),
        ).fetchone()

    print(row)


if __name__ == "__main__":
    round_trip_values()
```

## 19.3 What to verify

Do not only compare string representations.

Check types:

```python
assert isinstance(row[0], int)
assert isinstance(row[1], Decimal)
assert row[2].tzinfo is not None
assert isinstance(row[3], date)
assert isinstance(row[4], type(source["uuid_value"]))
assert isinstance(row[5], list)
assert isinstance(row[6], dict)
assert row[7] is None
```

A production engineer asks:

> Did the value come back with the correct **meaning and type**, not merely the expected text?

---

# 20. Session Timezone

## 20.1 What is a session timezone?

Each PostgreSQL connection represents a database session.

The session can have settings, including a timezone.

You can inspect it:

```sql
SHOW TimeZone;
```

From psycopg:

```python
with psycopg.connect(...) as conn:
    row = conn.execute("SHOW TimeZone").fetchone()
    print(row[0])
```

## 20.2 Why can sessions differ?

Two connections can have different settings.

Conceptually:

```text
Python process A → PostgreSQL session A → TimeZone A
Python process B → PostgreSQL session B → TimeZone B
```

This is one reason application-level timezone policy should be explicit.

## 20.3 Practical policy

For pipeline timestamps:

```text
store/communicate:
    timezone-aware UTC

display to humans:
    convert as needed
```

Do not depend on whichever local timezone happens to be configured on a development laptop.

---

# 21. Connection Options

A production PostgreSQL connection is more than:

```python
host
port
user
password
```

Operational settings matter.

## 21.1 `connect_timeout`

`connect_timeout` controls how long the connection attempt is allowed to wait.

Example:

```python
import psycopg

conn = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="warehouse",
    user="app_user",
    password="development-only-secret",
    connect_timeout=5,
)
```

The idea is:

```text
connect attempt
      ↓
server responds → connect
or
timeout reached → fail
```

Without a sensible connection-timeout policy, an unavailable network path can consume time waiting for a connection.

## 21.2 `application_name`

A very valuable operational setting:

```python
with psycopg.connect(
    ...,
    application_name="orders_etl",
) as conn:
    ...
```

The name can appear in `pg_stat_activity`.

That allows database operators to answer:

> Which application or pipeline owns this PostgreSQL session?

In production, observability is far easier when jobs identify themselves.

## 21.3 `sslmode`

PostgreSQL connections can use SSL/TLS.

`sslmode` controls how psycopg should handle encrypted connections.

At a practical level:

```text
Python
  ↓
encrypted network connection
  ↓
PostgreSQL
```

Encryption matters because credentials and data travel across a network.

The exact appropriate `sslmode` depends on the deployment.

Do not copy insecure local-development settings into production merely because they work in Docker.

The correct question is:

> What security guarantee does this environment require?

## 21.4 `statement_timeout`

A connection can succeed while an individual query runs too long.

That is a different failure mode.

```text
Connection timeout
    =
Can I establish the database connection?

Statement timeout
    =
How long may a database statement execute?
```

A psycopg connection can be configured with PostgreSQL options.

For example:

```python
with psycopg.connect(
    ...,
    options="-c statement_timeout=5000",
) as conn:
    conn.execute("SELECT pg_sleep(10)")
```

This asks PostgreSQL to cancel the statement after about 5 seconds.

The exact behavior and exception type are PostgreSQL/psycopg specific.

A reliable data pipeline generally needs a timeout policy rather than infinite waiting.

---

# 22. Observing PostgreSQL from Python

One of the strongest engineering habits in this module is:

> **Do not observe only Python. Observe what PostgreSQL sees.**

## 22.1 `pg_stat_activity`

PostgreSQL exposes session information through `pg_stat_activity`.

A simple query:

```sql
SELECT
    pid,
    application_name,
    state,
    query
FROM pg_stat_activity
WHERE application_name = 'orders_etl';
```

## 22.2 Practical exercise

### Step 1 — Open a connection

```python
import time
import psycopg

with psycopg.connect(
    ...,
    application_name="orders_etl",
) as conn:
    print("Connected. Inspect pg_stat_activity now.")
    time.sleep(15)
```

### Step 2 — From another PostgreSQL session

Run:

```sql
SELECT
    pid,
    application_name,
    state,
    query
FROM pg_stat_activity
WHERE application_name = 'orders_etl';
```

### Step 3 — Interpret the result

You should be able to identify:

- the session PID;
- the application name;
- its current state;
- the current or recent query information.

This teaches an important production habit:

```text
Python logs tell you what your process thinks happened.

PostgreSQL metadata tells you what the database session actually looks like.
```

---

# 23. Psycopg-Specific Exceptions

Topic 01 introduced the DB-API exception hierarchy.

psycopg adds PostgreSQL-specific exception classes that contain more precise information.

Required examples include:

- `UniqueViolation`
- `SerializationFailure`
- `DeadlockDetected`
- `QueryCanceled`

## 23.1 `UniqueViolation`

Suppose a unique key already exists.

Conceptually:

```text
INSERT duplicate key
       ↓
PostgreSQL detects constraint violation
       ↓
PostgreSQL returns an error
       ↓
psycopg raises UniqueViolation
```

Example:

```python
import psycopg

try:
    with psycopg.connect(...) as conn:
        conn.execute(
            "INSERT INTO customers (id, name) VALUES (%s, %s)",
            (1, "Alice"),
        )
except psycopg.errors.UniqueViolation as exc:
    print("Duplicate key:", exc)
```

The important lesson is classification.

A duplicate-key error is not the same kind of failure as a broken network connection.

## 23.2 `SerializationFailure`

A serialization failure occurs when PostgreSQL cannot safely serialize concurrent transactions under a strict isolation level.

At this topic's awareness level:

```text
concurrent transactions
       ↓
PostgreSQL detects serialization conflict
       ↓
SerializationFailure
```

It can be a candidate for a retry.

Detailed transaction-retry architecture belongs to Topic 04.

## 23.3 `DeadlockDetected`

A deadlock can occur when concurrent transactions wait on each other in a cycle.

Conceptually:

```text
Transaction A holds lock X
Transaction B holds lock Y

A waits for Y
B waits for X

      ↓
deadlock cycle

      ↓
PostgreSQL aborts one participant
      ↓
DeadlockDetected
```

This can also be a candidate for retry, depending on the operation.

Again, the complete retry policy is deliberately deferred to Topic 04.

## 23.4 `QueryCanceled`

A statement can be canceled, including because of a PostgreSQL `statement_timeout`.

Example:

```python
import psycopg

try:
    with psycopg.connect(
        ...,
        options="-c statement_timeout=2000",
    ) as conn:
        conn.execute("SELECT pg_sleep(10)")
except psycopg.errors.QueryCanceled as exc:
    print("The statement was canceled:", exc)
```

This is different from:

```text
could not connect
```

The connection may have existed successfully; the statement itself was canceled.

## 23.5 What should be logged?

Useful operational details often include:

- exception class;
- SQLSTATE where appropriate;
- safe statement/context identifiers;
- pipeline/job name;
- application name;
- timing;
- correlation/run identifier.

Avoid logging:

- passwords;
- secret connection URIs;
- sensitive row contents.

---

# 24. SQLSTATE

## 24.1 What is SQLSTATE?

**SQLSTATE** is a standardized machine-readable error/status code system used by PostgreSQL.

A human-readable message can change in wording.

A code gives applications a stable classification signal.

## 24.2 Why does that matter?

For program logic:

```text
human message
    ↓
good for reading

SQLSTATE / exception class
    ↓
better for machine classification
```

psycopg exposes SQLSTATE information on exceptions.

Conceptually:

```python
try:
    ...
except psycopg.Error as exc:
    print("SQLSTATE:", exc.sqlstate)
```

For production handling, a specific exception class is often the clearest expression:

```python
except psycopg.errors.UniqueViolation:
    ...
```

rather than converting every error into:

```python
except Exception:
    ...
```

## 24.3 Exception class versus SQLSTATE

Think of the relationship as:

```text
PostgreSQL error
    ↓
SQLSTATE
    ↓
psycopg exception classification
```

The exception class gives Python code an expressive API.

SQLSTATE provides a precise machine-readable database classification.

Neither eliminates the need to understand the actual database operation.

---

# 25. Server-Side vs Client-Side Parameter Binding

This is an advanced section.

Topic 03 will teach SQL injection deeply.

Here, the goal is to understand the communication model.

## 25.1 Server-side binding concept

Normal psycopg parameterized execution separates SQL structure from parameter values.

Conceptually:

```text
SQL structure
    +
parameter values
    ↓
driver/protocol
    ↓
PostgreSQL
```

Example:

```python
row = conn.execute(
    """
    SELECT id, total
    FROM orders
    WHERE id = %s
    """,
    (order_id,),
).fetchone()
```

The application does not manually construct a SQL string by inserting `order_id` text into it.

## 25.2 Client-side binding

psycopg also provides a `ClientCursor`:

```python
from psycopg import ClientCursor
```

Conceptually, client-side binding means the parameter interpolation/quoting work happens on the client side rather than following the normal server-side parameter-binding model.

The exact details matter because some PostgreSQL statements or client integrations care about whether binding occurs on the client or server.

## 25.3 Why does this distinction exist?

Different workloads and integrations can have different needs.

A normal psycopg cursor is designed to work naturally with PostgreSQL's parameterized protocol.

`ClientCursor` exists for cases where client-side adaptation/binding behavior is useful or required.

The important engineering lesson is:

> **The phrase "parameterized query" describes application intent; the exact wire-level mechanism depends on the driver/API being used.**

## 25.4 What remains important?

Regardless of binding mode:

- use the driver's documented parameter APIs;
- do not hand-quote values;
- do not confuse SQL identifiers with values;
- understand the next topic's security rules.

Do not turn this section into the complete SQL injection lesson.

---

# 26. Prepared Statements

## 26.1 What is a prepared statement?

A prepared statement allows a database session to prepare a statement for repeated execution.

Conceptually:

```text
prepare statement
       ↓
execute many times
       ↓
reuse prepared form
```

Potential benefit:

```text
less repeated parse/prepare work
```

This matters most when a statement is executed repeatedly.

## 26.2 Why not always prepare everything?

Because preparation itself has costs and trade-offs.

Possible concerns include:

- statement lifetime;
- per-session state;
- workload patterns;
- planning behavior;
- pooler compatibility.

The right question is not:

> "Are prepared statements good?"

It is:

> "Does this workload benefit from preparation enough to justify the added behavior?"

## 26.3 Automatic preparation in psycopg

psycopg can automatically prepare frequently repeated statements.

The exact threshold/settings are driver behavior, not a PEP 249 guarantee.

For a high-throughput service this can be valuable.

For a deployment that sits behind certain connection poolers, it can require additional compatibility analysis.

## 26.4 Prepared statements and poolers

This is an important architectural interaction.

A prepared statement can be session-specific.

But transaction- or statement-level pooling can move work between backend sessions.

Conceptually:

```text
Application
    ↓
Pooler
    ↓
PostgreSQL session A
or
PostgreSQL session B
```

If your application assumes session-local prepared state while a pooler changes the backend session, compatibility problems can appear.

Do not solve that here.

Topic 05 covers pooling and PgBouncer in depth.

For now, remember:

> **Session state and connection pooling are coupled architectural concerns.**

---

# 27. Pipeline Mode

## 27.1 The problem: network round trips

Suppose your application sends three independent operations:

```text
Query 1 → wait → response
Query 2 → wait → response
Query 3 → wait → response
```

The waiting can dominate when operations are small and network latency is significant.

## 27.2 Pipeline concept

psycopg pipeline mode allows multiple operations to be sent in a pipeline so that the client does not have to wait for each round trip before submitting later operations.

Conceptually:

```text
Without pipeline:

Q1 → response → Q2 → response → Q3 → response


With pipeline:

Q1 ─┐
Q2 ─┼──> server
Q3 ─┘
       ↓
responses processed
```

## 27.3 Small example

```python
import psycopg

with psycopg.connect(...) as conn:
    with conn.pipeline():
        conn.execute("SELECT 1")
        conn.execute("SELECT 2")
        conn.execute("SELECT 3")
```

The exact behavior available to the application around result consumption should follow psycopg's API documentation for the version in use.

## 27.4 When can it help?

Pipeline mode is worth evaluating when:

- many operations are small;
- network round trips are expensive;
- operations can be issued without waiting for each result;
- ordering/dependency constraints allow pipelining.

## 27.5 When can it fail to help?

If:

- one query dominates execution time;
- operations are inherently dependent;
- server execution is the bottleneck;
- the workload is already efficiently batched.

Therefore:

> **Pipeline mode is a performance tool, not a universal acceleration switch.**

Measure it.

---

# 28. Binary vs Text Transfer

PostgreSQL's protocol can represent certain values in text or binary form.

At a high level:

```text
Text transfer
    ↓
textual representation
    ↓
parse/convert

Binary transfer
    ↓
binary representation
    ↓
decode/convert
```

Binary transfer can reduce some parsing or serialization work for some types and workloads.

But do not make a blanket claim such as:

> "Binary is always faster."

The effect depends on:

- data types;
- volume;
- conversion costs;
- driver behavior;
- server behavior;
- downstream Python processing.

The production lesson is:

> Understand the representation costs, then measure the workload.

---

# 29. Custom Type Adapters

Standard database types are not the only types you may encounter.

PostgreSQL supports concepts such as:

- enums;
- domains;
- custom types.

psycopg has an adaptation system that can be extended.

## 29.1 Why custom adapters exist

Suppose a PostgreSQL enum represents:

```text
pending
running
succeeded
failed
```

Your Python application may want a corresponding Python enum.

The adaptation problem becomes:

```text
Python enum
    ↕
PostgreSQL enum
```

Similarly:

```text
Python value
    ↕
PostgreSQL domain
```

## 29.2 Direction matters

There are two directions:

### Dumping / adapting

```text
Python
   ↓
PostgreSQL representation
```

### Loading

```text
PostgreSQL representation
   ↓
Python object
```

A custom integration must consider both directions if round-trip semantics are required.

## 29.3 Awareness-level example

Suppose you define:

```python
from enum import Enum


class PipelineStatus(str, Enum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
```

A production adapter can be configured so this maps naturally to a corresponding PostgreSQL enum.

The exact registration mechanism is version/API specific and should be implemented against the psycopg 3 adaptation documentation rather than invented from memory.

For this module, the important mechanism is:

> **psycopg's adaptation layer is extensible when standard Python ↔ PostgreSQL mappings are not enough.**

Do not become an expert adapter author in this topic.

---

# 30. `LISTEN` / `NOTIFY`

PostgreSQL can send asynchronous notifications through channels.

The conceptual flow is:

```text
Producer
   ↓
NOTIFY channel
   ↓
PostgreSQL
   ↓
LISTEN client
   ↓
Python application
```

## 30.1 Why use it?

It can be useful when a Python process needs lightweight notifications triggered by database activity.

Examples include:

- waking a worker;
- notifying an internal process that metadata changed;
- triggering a cache refresh;
- coordinating small control-plane events.

## 30.2 Conceptual example

One session can issue:

```sql
NOTIFY pipeline_events, 'run-completed';
```

Another session can:

```sql
LISTEN pipeline_events;
```

psycopg exposes PostgreSQL notification mechanisms to Python.

A minimal conceptual example:

```python
import psycopg

with psycopg.connect(...) as conn:
    conn.execute("LISTEN pipeline_events")

    # Notification consumption depends on the surrounding
    # application loop and psycopg notification API.
```

The important architectural boundary is:

> PostgreSQL notifications are lightweight database notifications, not a replacement for a durable event-streaming platform.

Do not turn this into Kafka or streaming architecture.

---

# 31. Async Connection Awareness

psycopg 3 also exposes an asynchronous connection API:

```python
psycopg.AsyncConnection
```

The motivation is straightforward.

Synchronous code:

```text
call database
    ↓
wait
    ↓
continue
```

Async code can allow other work while I/O is waiting:

```text
start database I/O
    ↓
yield control
    ↓
perform other async work
    ↓
resume when database I/O is ready
```

This matters in I/O-heavy services.

But async introduces:

- coroutine semantics;
- event-loop integration;
- different resource-management patterns;
- concurrency coordination.

Detailed async patterns are intentionally deferred to:

**Module 2.10 — Concurrency and Parallelism in Practice**

At this stage, you only need to recognize:

```python
from psycopg import AsyncConnection
```

and understand why it exists.

---

# 32. psycopg 3 vs psycopg 2 in Real Codebases

psycopg 3 is the focus of this module.

psycopg 2 still appears in legacy systems.

A production engineer should understand old code before changing it.

## 32.1 Modern focus

```text
psycopg 3
    ↓
current learning target
```

## 32.2 Legacy awareness

```text
psycopg 2
    ↓
existing production/legacy code you may encounter
```

Relevant legacy patterns include:

- context-manager behavior differences;
- `extras.execute_values`;
- `copy_expert`;
- older imports and APIs.

For example, a legacy codebase may contain:

```python
from psycopg2 import extras

extras.execute_values(...)
```

or:

```python
cursor.copy_expert(...)
```

The existence of these APIs is useful context when reading historical pipeline code.

Do not automatically rewrite an entire system just because psycopg 3 is newer.

Migration questions include:

- compatibility;
- dependency graph;
- test coverage;
- deployment constraints;
- operational risk;
- behavior differences.

The correct production attitude is:

> Understand the existing system first. Change it deliberately.

---

# 33. Production Connection Factory

A data platform often benefits from one centralized connection-creation function.

The goal is not to build a giant framework.

The goal is to make important connection settings consistent.

## 33.1 Configuration model

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class PostgresSettings:
    host: str
    port: int
    dbname: str
    user: str
    password: str
    application_name: str
    connect_timeout: int
    statement_timeout_ms: int
```

## 33.2 Connection factory

```python
import psycopg


def get_connection(settings: PostgresSettings) -> psycopg.Connection:
    return psycopg.connect(
        host=settings.host,
        port=settings.port,
        dbname=settings.dbname,
        user=settings.user,
        password=settings.password,
        application_name=settings.application_name,
        connect_timeout=settings.connect_timeout,
        options=f"-c statement_timeout={settings.statement_timeout_ms}",
    )
```

This function creates one predictable connection policy.

## 33.3 Why centralize it?

Without a central policy, different pipelines may accidentally use:

```text
Job A → timeout 5s
Job B → no timeout
Job C → timeout 30m
Job D → no application_name
Job E → different timezone assumptions
```

Centralization reduces accidental divergence.

## 33.4 Production use

```python
settings = load_settings()

with get_connection(settings) as conn:
    row = conn.execute(
        "SELECT count(*) FROM orders"
    ).fetchone()

print(row[0])
```

The data operation remains separate from connection configuration.

## 33.5 What this abstraction intentionally does not include

Not here:

- a connection pool;
- retry decorators;
- transaction orchestration framework;
- SQLAlchemy;
- bulk-loading APIs.

Those belong to later topics.

---

# 34. Production Data Engineering Scenarios

## Scenario 1 — Pipeline metadata

A Python pipeline writes a small row describing a run:

```text
pipeline_name
status
started_at
finished_at
rows_in
rows_out
```

psycopg matters because:

- timestamps need correct types;
- connections need predictable lifecycle;
- errors need useful classification;
- application name helps operations teams identify the job.

This is a control-plane operation with database integration requirements.

## Scenario 2 — Operational extraction

A pipeline reads customer orders.

A production-oriented client should consider:

```text
secure configuration
      ↓
application_name
      ↓
connect_timeout
      ↓
statement_timeout
      ↓
appropriate row representation
      ↓
correct type handling
```

Large-result server-side streaming is intentionally deferred to Topic 10.

## Scenario 3 — Constraint violation

Suppose an insert violates a unique key.

PostgreSQL produces a constraint error.

psycopg exposes:

```python
psycopg.errors.UniqueViolation
```

The Python program can now classify the event precisely.

## Scenario 4 — Long-running query

A pipeline may issue a query that runs too long.

The engineering controls are complementary:

```text
application_name
    ↓
identify who is running

statement_timeout
    ↓
limit runaway execution

pg_stat_activity
    ↓
observe database-side state
```

This combination is much more operationally useful than simply writing:

```python
print("query started")
```

## Scenario 5 — Legacy application

You open an old repository and see:

```python
import psycopg2
from psycopg2 import extras
```

Do not immediately conclude that the system is wrong.

First determine:

- what APIs it uses;
- what tests cover;
- whether deployment depends on old behavior;
- whether migration to psycopg 3 changes semantics.

Production engineering includes maintaining systems, not only writing greenfield code.

---

# 35. Debugging Lab

## Debugging Problem 1 — Wrong connection configuration

### Problem

```python
import psycopg

conn = psycopg.connect(
    host="localhost",
    port=5433,
    dbname="warehouse",
    user="etl",
)
```

The PostgreSQL server is actually listening on `5432`.

### Why it fails

The Python code is asking the driver to connect to the wrong endpoint.

### Better diagnostic thinking

Check:

```text
host
port
database
user
server availability
TLS requirements
```

Do not immediately rewrite application logic.

### Production lesson

Connection failures are often configuration failures.

---

## Debugging Problem 2 — Password accidentally logged

### Problem

```python
print(
    f"Connecting to {settings.host}"
    f" as {settings.user}"
    f" with password={settings.password}"
)
```

### Why it is dangerous

Logs often have broader access and longer retention than source code.

### Corrected form

```python
print(
    f"Connecting to {settings.host}"
    f" as {settings.user}"
)
```

### Production lesson

> Observability must not become secret exposure.

---

## Debugging Problem 3 — Naive datetime

### Problem

```python
from datetime import datetime

created_at = datetime.now()
```

### Why it is risky

The value has no timezone information.

### Corrected form

```python
from datetime import datetime, timezone

created_at = datetime.now(timezone.utc)
```

### Production lesson

Make the application's timestamp convention explicit.

---

## Debugging Problem 4 — Wrong row representation

### Problem

```python
row = conn.execute(
    "SELECT id, name FROM customers LIMIT 1"
).fetchone()

print(row["name"])
```

The connection did not use `dict_row`.

### Why it fails

The default row may be tuple-like rather than dictionary-like.

### Corrected form

```python
from psycopg.rows import dict_row

with psycopg.connect(..., row_factory=dict_row) as conn:
    row = conn.execute(
        "SELECT id, name FROM customers LIMIT 1"
    ).fetchone()

print(row["name"])
```

### Alternative

Use positional access if that representation is intentional:

```python
print(row[1])
```

### Production lesson

Know your row representation instead of guessing.

---

## Debugging Problem 5 — Duplicate key

### Problem

```python
import psycopg

try:
    with psycopg.connect(...) as conn:
        conn.execute(
            "INSERT INTO customers (id, name) VALUES (%s, %s)",
            (1, "Alice"),
        )
except psycopg.errors.UniqueViolation as exc:
    print("Unique violation:", exc)
```

### Diagnostic reasoning

Ask:

1. Which constraint failed?
2. What SQL operation was running?
3. Is the data duplicate?
4. Is the pipeline logic supposed to be idempotent?
5. Is this expected data rejection or an unexpected pipeline bug?

### Production lesson

A precise exception gives more control than a generic failure.

---

## Debugging Problem 6 — Statement timeout

### Problem

```python
import psycopg

try:
    with psycopg.connect(
        ...,
        options="-c statement_timeout=2000",
    ) as conn:
        conn.execute("SELECT pg_sleep(10)")
except psycopg.errors.QueryCanceled as exc:
    print("Timed out:", exc)
```

### Diagnostic question

Ask:

```text
Did the connection fail?
or
Did the database statement get canceled?
```

Here, the statement was canceled.

### Production lesson

Connection timeout and statement timeout solve different problems.

---

## Debugging Problem 7 — Prepared statements behind a pooler

### Situation

A system works directly against PostgreSQL.

It starts producing errors after introducing a connection pooler with transaction-level pooling.

### Possible cause

Prepared state is associated with a PostgreSQL session.

A pooler can move application work between backend sessions.

### Correct response

Do not immediately disable random features.

First investigate:

```text
prepared statement behavior
pooling mode
session affinity
driver configuration
```

Detailed pooler behavior belongs to Topic 05.

---

# 36. Hands-On Exercise — `pg_client.py`

The roadmap requires a `pg_client.py` exercise.

No additional file is created by this document. The specification below is the exercise to implement in the module's existing lab environment.

## Objective

Build a small PostgreSQL client layer that proves you can:

- configure connections securely;
- identify sessions;
- use row factories;
- round-trip common Python values;
- handle PostgreSQL-specific exceptions;
- configure timeouts.

## Prerequisites

You need:

- Python 3.12+;
- psycopg 3;
- Docker PostgreSQL;
- a working database/user;
- environment-based connection settings.

## Starter design

Implement:

```python
def get_connection(settings):
    ...
```

The function should:

- read settings from the environment/settings object;
- configure `application_name`;
- configure `connect_timeout`;
- configure `statement_timeout`;
- never log the password;
- return a psycopg connection.

## Starter example

```python
from dataclasses import dataclass
import os

import psycopg


@dataclass(frozen=True)
class Settings:
    host: str
    port: int
    dbname: str
    user: str
    password: str
    application_name: str
    connect_timeout: int
    statement_timeout_ms: int


def load_settings() -> Settings:
    return Settings(
        host=os.environ["PGHOST"],
        port=int(os.environ["PGPORT"]),
        dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        application_name="module-2-7-topic-02",
        connect_timeout=5,
        statement_timeout_ms=5000,
    )


def get_connection(settings: Settings) -> psycopg.Connection:
    return psycopg.connect(
        host=settings.host,
        port=settings.port,
        dbname=settings.dbname,
        user=settings.user,
        password=settings.password,
        application_name=settings.application_name,
        connect_timeout=settings.connect_timeout,
        options=f"-c statement_timeout={settings.statement_timeout_ms}",
    )
```

### What you should predict before running

Predict:

1. Which Python object `get_connection()` returns.
2. Which database session PostgreSQL creates.
3. Where the `application_name` should appear.
4. How long a deliberately slow statement should be allowed to run.
5. Which error class should appear after a timeout.

---

## Exercise A — `dict_row`

Modify the connection or query so that:

```python
row = conn.execute(
    "SELECT id, name FROM orders LIMIT 1"
).fetchone()
```

returns a dictionary-like row.

Then access:

```python
row["id"]
row["name"]
```

### Expected result

The field names should be available directly.

### Production lesson

Named access can reduce ambiguity in operational metadata and small query results.

---

## Exercise B — Dataclass rows

Create:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    id: int
    customer_id: int
    total: float
```

Use:

```python
from psycopg.rows import class_row
```

and configure:

```python
row_factory=class_row(Order)
```

Then query one order.

### Predict first

What Python type should the result be?

Expected answer:

```text
Order
```

### Production lesson

Dataclass rows can be useful when the query result has a stable domain shape.

---

## Exercise C — Type round trip

Round-trip values containing:

```text
Decimal
UTC datetime
UUID
list
Jsonb
```

Then read them back.

Verify the returned objects and compare them to the originals.

### Predict first

For each field, write:

```text
Python input type
→ PostgreSQL column type
→ Python returned type
```

For example:

```text
Decimal
→ numeric
→ Decimal
```

---

## Exercise D — Statement timeout

Run:

```python
conn.execute("SELECT pg_sleep(10)")
```

with a short `statement_timeout`.

Catch:

```python
psycopg.errors.QueryCanceled
```

### Expected reasoning

```text
connection succeeded
        ↓
statement started
        ↓
timeout threshold reached
        ↓
PostgreSQL cancels statement
        ↓
psycopg surfaces QueryCanceled
```

---

## Exercise E — Duplicate key

Insert the same primary key twice.

Catch:

```python
psycopg.errors.UniqueViolation
```

### Predict first

Is this:

- a connectivity problem;
- a timeout;
- a syntax error;
- a constraint violation?

Expected category:

```text
constraint violation
```

---

## Exercise F — Docker PostgreSQL

Run all of the exercises against the PostgreSQL container established for Module 2.7.

Do not replace PostgreSQL with SQLite for the psycopg exercises.

---

# 37. Observability Exercise

The objective is:

> **Do not only observe Python. Observe what PostgreSQL sees.**

## Step 1 — Python

```python
import time
import psycopg

with psycopg.connect(
    ...,
    application_name="topic-02-observability",
) as conn:
    conn.execute("SELECT 1")

    print("Inspecting pg_stat_activity...")
    time.sleep(15)
```

## Step 2 — PostgreSQL

From another PostgreSQL session:

```sql
SELECT
    pid,
    application_name,
    state,
    query
FROM pg_stat_activity
WHERE application_name = 'topic-02-observability';
```

## Step 3 — Explain

You should be able to explain:

- which session is yours;
- what application created it;
- what state it is in;
- what query information is visible.

### Expected reasoning

```text
Python process
    ↓
psycopg connection
    ↓
PostgreSQL backend session
    ↓
pg_stat_activity
```

### Production lesson

A database engineer operates both sides of the boundary:

```text
application-side evidence
+
database-side evidence
```

---

# 38. Predict → Run → Observe → Explain

Use the module's database-boundary learning loop.

For important examples, stop before running the code and answer:

### Question 1

What Python object is created?

### Question 2

What does psycopg receive?

### Question 3

What does PostgreSQL receive?

### Question 4

Does a transaction begin implicitly?

### Question 5

What Python type should come back?

### Question 6

Which exception should appear if the operation fails?

### Question 7

What should `pg_stat_activity` show?

### Question 8

What resource is released when the context manager exits?

This exercise is more valuable than memorizing:

```python
psycopg.connect(...)
```

because production debugging is mostly about understanding state transitions.

---

# 39. Production Hardening: From Working Code to Production Code

## Version 1 — Naive

```python
conn = psycopg.connect(...)
```

This proves almost nothing about operational quality.

Questions remain:

- Which credentials?
- Which environment?
- Which timeout?
- Who owns the connection?
- How is failure classified?
- How is the session identified?

## Version 2 — Configured

```python
conn = psycopg.connect(
    ...,
    connect_timeout=5,
    application_name="orders_pipeline",
)
```

Now:

- connection attempts are bounded;
- the session is identifiable.

## Version 3 — Production-oriented

```python
from dataclasses import dataclass
import os

import psycopg


@dataclass(frozen=True)
class Settings:
    host: str
    port: int
    dbname: str
    user: str
    password: str
    application_name: str
    connect_timeout: int
    statement_timeout_ms: int


def load_settings() -> Settings:
    required = {
        name: os.getenv(name)
        for name in (
            "PGHOST",
            "PGPORT",
            "PGDATABASE",
            "PGUSER",
            "PGPASSWORD",
        )
    }

    missing = [key for key, value in required.items() if not value]

    if missing:
        raise RuntimeError(
            "Missing PostgreSQL configuration: "
            + ", ".join(missing)
        )

    return Settings(
        host=required["PGHOST"],
        port=int(required["PGPORT"]),
        dbname=required["PGDATABASE"],
        user=required["PGUSER"],
        password=required["PGPASSWORD"],
        application_name="orders_pipeline",
        connect_timeout=5,
        statement_timeout_ms=30_000,
    )


def get_connection(settings: Settings) -> psycopg.Connection:
    return psycopg.connect(
        host=settings.host,
        port=settings.port,
        dbname=settings.dbname,
        user=settings.user,
        password=settings.password,
        application_name=settings.application_name,
        connect_timeout=settings.connect_timeout,
        options=f"-c statement_timeout={settings.statement_timeout_ms}",
    )
```

### What changed?

```text
Version 1
    ↓
just connect

Version 2
    ↓
timeouts + observability

Version 3
    ↓
external configuration
+ validation
+ timeout policy
+ resource lifecycle
+ safe credential handling
+ consistent session identity
```

That is the difference between "code that connects" and a reusable production client foundation.

---

# 40. What Actually Happens When psycopg Executes a Query?

Consider:

```python
from datetime import datetime, timezone

import psycopg

order_id = 101

with psycopg.connect(...) as conn:
    result = conn.execute(
        "SELECT id, total FROM orders WHERE id = %s",
        (order_id,),
    )

    row = result.fetchone()
```

Walk it carefully.

## Step 1 — Python requests a connection

```python
psycopg.connect(...)
```

Python calls the psycopg API.

## Step 2 — psycopg establishes PostgreSQL communication

The driver handles PostgreSQL connection details.

## Step 3 — PostgreSQL session is established

The server creates the database-side session/backend associated with the connection.

Session settings such as:

```text
application_name
TimeZone
statement_timeout
```

can now matter.

## Step 4 — Python calls `execute()`

The application supplies:

```text
SQL
+
parameter tuple
```

## Step 5 — psycopg processes the request

The driver handles parameter/type adaptation and PostgreSQL protocol communication.

The exact wire behavior depends on the psycopg API being used.

## Step 6 — PostgreSQL executes the statement

PostgreSQL:

- parses SQL;
- plans the statement;
- accesses data;
- produces result rows.

## Step 7 — Data returns

The server sends result information and values back to the driver.

## Step 8 — psycopg adapts returned values

For example:

```text
PostgreSQL integer
      ↓
Python int

PostgreSQL numeric
      ↓
Python Decimal

PostgreSQL timestamptz
      ↓
timezone-aware Python datetime
```

## Step 9 — Python consumes the row

```python
row = result.fetchone()
```

The application now has the row representation selected by the driver/row factory.

## Step 10 — Context exit

```python
with psycopg.connect(...) as conn:
```

exits.

Under psycopg 3's context-manager behavior:

- successful work is committed;
- exceptions trigger rollback;
- the connection is closed.

### Three levels of certainty

When reasoning about internals, distinguish:

#### DB-API contract

Examples:

- connection/cursor concepts;
- execution;
- fetching;
- transaction methods.

#### Typical psycopg behavior

Examples:

- psycopg 3 row factories;
- PostgreSQL-specific exception classes;
- context-manager semantics;
- type adaptation.

#### PostgreSQL-specific behavior

Examples:

- SQLSTATE;
- `pg_stat_activity`;
- `statement_timeout`;
- `LISTEN` / `NOTIFY`;
- PostgreSQL data types.

A good engineer never says:

> "DB-API guarantees this."

when the behavior actually comes from psycopg or PostgreSQL.

---

# 41. Performance Thinking

Performance begins with understanding where time can go.

For database access, major contributors include:

```text
connection establishment
        +
network round trips
        +
server execution
        +
serialization / adaptation
        +
result materialization
        +
Python processing
```

This creates several useful questions.

## 41.1 Network round trips

A workload with hundreds of tiny independent operations may spend substantial time waiting on communication.

This explains why pipeline mode can sometimes help.

## 41.2 Connection establishment

Opening a new connection has setup cost.

That becomes more important as concurrency grows.

Connection pooling is covered later in Topic 05.

## 41.3 Serialization and adaptation

Values cross an interface boundary.

Conceptually:

```text
Python object
    ↓
adapt
    ↓
network/protocol
    ↓
PostgreSQL value
```

and back again.

Large numbers of objects can make conversion work significant.

## 41.4 Text vs binary

Different representations can have different conversion costs.

But the correct engineering practice is:

> Measure the workload rather than relying on a generic statement that binary is faster.

## 41.5 Prepared statements

Repeated statements may benefit from preparation.

But preparation changes state and interacts with pooling.

Again:

> optimize after understanding the workload.

## 41.6 Result materialization

This is especially important in Python.

A database result becomes Python objects.

For large outputs, object creation and memory usage can become substantial.

Topic 10 covers large-result streaming in depth.

For this topic, the lesson is only:

> **Retrieving database data always has an application-side representation cost.**

---

# 42. Interview Questions

## Basic

### 1. What is psycopg?

**Expected reasoning:** psycopg is a Python PostgreSQL driver that provides a Python-facing interface to PostgreSQL.

### 2. Why does Python need a PostgreSQL driver?

**Expected reasoning:** Python needs software that understands how to communicate with PostgreSQL's protocol and adapt values/results.

### 3. What does `psycopg.connect()` return?

**Expected reasoning:** a psycopg connection object representing the application's connection/session with PostgreSQL.

### 4. What is a row factory?

**Expected reasoning:** a mechanism that controls how returned database rows are represented as Python objects.

### 5. Why use `dict_row`?

**Expected reasoning:** for readable named-field access such as `row["name"]`.

## Intermediate

### 6. How does psycopg adapt Python values to PostgreSQL types?

**Expected reasoning:** psycopg has adapters/loaders that translate Python objects into PostgreSQL representations and database values back into Python objects.

### 7. Why should pipelines prefer UTC-aware timestamps?

**Expected reasoning:** to avoid ambiguous local-time semantics and establish a consistent absolute-time convention across systems.

### 8. What is SQLSTATE?

**Expected reasoning:** a machine-readable PostgreSQL status/error classification code.

### 9. What is the difference between `connect_timeout` and `statement_timeout`?

**Expected reasoning:** connection timeout limits establishing the connection; statement timeout limits statement execution.

### 10. What is `application_name`?

**Expected reasoning:** a session identifier that helps operators identify which application or job owns a PostgreSQL connection.

### 11. Why is `UniqueViolation` more useful than a generic exception?

**Expected reasoning:** it classifies a specific database failure, allowing more precise diagnosis and behavior.

### 12. What is `Jsonb`?

**Expected reasoning:** psycopg's JSONB adaptation helper for sending Python JSON-compatible values to PostgreSQL `jsonb`.

### 13. How do Python lists map to PostgreSQL arrays?

**Expected reasoning:** psycopg can adapt Python lists to compatible PostgreSQL array types, assuming the database schema matches.

## Advanced

### 14. What is server-side parameter binding?

**Expected reasoning:** a communication model where SQL structure and parameter values are represented separately for PostgreSQL protocol processing.

### 15. What is client-side binding?

**Expected reasoning:** a mode where the client performs the relevant binding/interpolation work before sending the resulting statement representation.

### 16. What are prepared statements?

**Expected reasoning:** prepared database statements that can be reused for repeated execution.

### 17. Why can prepared statements cause trouble behind some poolers?

**Expected reasoning:** prepared state can be session-specific while transaction/statement pooling can move work between backend sessions.

### 18. What is pipeline mode?

**Expected reasoning:** a psycopg feature that can reduce waiting caused by sequential network round trips for suitable independent operations.

### 19. Why can binary transfer matter?

**Expected reasoning:** binary representations can reduce parsing/conversion overhead for some types and workloads.

### 20. What is a custom type adapter?

**Expected reasoning:** an extension to psycopg's adaptation layer for translating application-specific Python values and PostgreSQL custom types.

### 21. When would `LISTEN` / `NOTIFY` be useful?

**Expected reasoning:** for lightweight database-originated notifications where a Python process needs to react to a database event.

### 22. What does `AsyncConnection` change?

**Expected reasoning:** it enables asynchronous database I/O, which can improve concurrency for suitable I/O-bound applications but introduces event-loop and async-programming complexity.

### 23. What differences might you encounter when maintaining psycopg2 code?

**Expected reasoning:** legacy APIs, context-manager behavior, old helper functions such as `extras.execute_values` and `copy_expert`, and other interface changes.

---

# 43. Architecture Questions

These questions require engineering reasoning rather than API recall.

## 1. How would you design a reusable PostgreSQL client layer for multiple pipelines?

Think about:

```text
configuration
+
connection creation
+
observability
+
error classification
+
resource lifecycle
```

Keep database operations separate from configuration policy.

## 2. Which connection settings would you standardize across pipeline jobs?

Potential categories include:

- connection timeout;
- statement timeout;
- application name;
- TLS policy;
- timezone policy.

The correct values should be derived from workload and operational requirements.

## 3. How would you prevent credentials from leaking through logs?

Design the logging boundary so secrets are never interpolated into logs.

Also consider:

- connection URI sanitization;
- exception message handling;
- structured logging fields;
- CI/CD output.

## 4. How would you identify which Python job owns a PostgreSQL session?

Use a deliberate `application_name` convention and inspect:

```sql
pg_stat_activity
```

Do not rely only on PID guessing.

## 5. How would you classify PostgreSQL-specific exceptions?

Use specific psycopg exception classes first where practical, and SQLSTATE when machine-readable classification is useful.

Avoid:

```python
except Exception:
    pass
```

## 6. Why might one pipeline use `dict_row` while another uses dataclasses?

The decision can depend on:

- query shape stability;
- readability;
- domain modeling;
- memory overhead;
- downstream interface expectations.

## 7. What would you do when Python and PostgreSQL disagree about data types?

Investigate:

```text
Python type
↓
psycopg adapter
↓
PostgreSQL column type
↓
PostgreSQL constraints/range
↓
returned Python type
```

Do not patch the symptom before identifying the boundary mismatch.

## 8. When would pipeline mode be worth evaluating?

When many small independent operations are dominated by network round trips.

Benchmark before standardizing it.

## 9. What risks exist when prepared statements meet connection poolers?

Session-local state can conflict with pooler behavior that changes backend session assignment.

Understand the pooling mode before relying on session-specific state.

## 10. Which psycopg2 patterns would make you cautious when reviewing legacy data-engineering code?

Look for:

- old helper APIs;
- context-manager assumptions;
- parameter handling;
- bulk-operation helpers;
- connection lifecycle;
- code that assumes psycopg2-specific behavior.

The correct approach is analysis before migration.

---

# 44. Checkpoint

Do not move on until you can perform these tasks without relying on copied examples.

## Roadmap checkpoint

- [ ] Connect securely using environment-based configuration.
- [ ] Use row factories to return dictionaries or dataclasses.
- [ ] Explain how Python datetimes map to `timestamptz`.
- [ ] Set a statement timeout and handle the error it raises.
- [ ] Explain server-side versus client-side parameter binding.

## Practical checkpoint

- [ ] Round-trip `int`, `Decimal`, UTC `datetime`, `date`, `UUID`, list, `Jsonb`, and `None`.
- [ ] Configure `application_name`.
- [ ] Find your connection in `pg_stat_activity`.
- [ ] Catch `UniqueViolation`.
- [ ] Explain SQLSTATE.
- [ ] Explain prepared statements.
- [ ] Explain pipeline mode.
- [ ] Explain why psycopg 3 and psycopg 2 code can differ.
- [ ] Explain which advanced features are intentionally deferred to later topics.

## Behavioral self-test

Without looking at your notes, explain this chain:

```text
Python
  ↓
DB-API concepts
  ↓
psycopg 3
  ↓
PostgreSQL protocol
  ↓
PostgreSQL session
  ↓
SQL execution
  ↓
result
  ↓
psycopg adaptation
  ↓
Python objects
```

Then explain one failure path:

```text
Python execute()
      ↓
PostgreSQL constraint violation
      ↓
SQLSTATE
      ↓
psycopg exception
      ↓
application handling
```

If you can explain both chains clearly, you understand the core boundary.

---

# 45. Common Mistakes

## Mistake 1 — Naive datetimes

### Beginner belief

"A Python datetime is a timestamp."

### What actually happens

A naive datetime has no timezone information.

### Production consequence

Systems in different timezones can interpret the same local-looking value differently.

### Correct mental model

```text
pipeline timestamp
    ↓
timezone-aware
    ↓
UTC
```

---

## Mistake 2 — Credentials in code

### Beginner belief

"It is convenient to put the password in the connection string."

### What actually happens

The credential becomes part of source code.

### Production consequence

Secret leakage risk.

### Correct mental model

```text
code → behavior
environment/secret provider → credentials
```

---

## Mistake 3 — Credentials in logs

### Beginner belief

"Logging the complete connection settings helps debugging."

### What actually happens

A password or secret can enter operational systems.

### Production consequence

A debugging log becomes a security incident.

### Correct mental model

Log identity and safe metadata, not credentials.

---

## Mistake 4 — No timeouts

### Beginner belief

"The database will eventually return."

### What actually happens

A network or query can remain stuck much longer than expected.

### Production consequence

Workers block, schedules slip, resources remain occupied, and failures become harder to isolate.

### Correct mental model

Use an explicit timeout policy appropriate to the workload.

---

## Mistake 5 — Relying on psycopg2-era behavior

### Beginner belief

"psycopg is psycopg."

### What actually happens

psycopg 3 and psycopg 2 have meaningful API and behavior differences.

### Production consequence

Legacy assumptions can produce incorrect code during maintenance or migration.

### Correct mental model

Treat psycopg 2 as legacy compatibility context and psycopg 3 as the current learning target.

---

## Mistake 6 — Assuming every PostgreSQL error should be retried

### Beginner belief

"If the query fails, retry it."

### What actually happens

Some errors indicate transient concurrency conditions; others indicate bad data, bad SQL, or violated constraints.

### Production consequence

Blind retries can amplify failures or repeatedly perform invalid work.

### Correct mental model

Classify the failure first. Detailed retry engineering belongs in Topic 04.

---

## Mistake 7 — Treating every Python datetime as production-safe

### Beginner belief

`datetime` always means an unambiguous point in time.

### What actually happens

Naive and timezone-aware datetimes have different semantics.

### Production consequence

Timestamp inconsistencies.

### Correct mental model

Define a UTC-aware pipeline timestamp policy.

---

## Mistake 8 — Ignoring `application_name`

### Beginner belief

"It is just metadata."

### What actually happens

A database operator may have no quick way to identify which pipeline owns a session.

### Production consequence

Slower incident diagnosis.

### Correct mental model

Connection identity is part of observability.

---

## Mistake 9 — Ignoring SQLSTATE

### Beginner belief

"The exception message is enough."

### What actually happens

Human text is less stable for machine classification.

### Production consequence

Less precise operational handling.

### Correct mental model

Use specific exception classes and SQLSTATE where they add value.

---

## Mistake 10 — Assuming prepared statements are always beneficial

### Beginner belief

"Prepared is always faster."

### What actually happens

Preparation has costs and introduces session-state behavior.

### Production consequence

Unnecessary complexity or pooler compatibility problems.

### Correct mental model

Use preparation deliberately for workloads that benefit from it.

---

## Mistake 11 — Assuming pipeline mode always improves performance

### Beginner belief

"Fewer round trips means everything is faster."

### What actually happens

Server execution, dependencies, and client processing may dominate.

### Production consequence

Complexity without measurable benefit.

### Correct mental model

Benchmark the actual workload.

---

## Mistake 12 — Confusing connection timeout with query timeout

### Beginner belief

"A timeout is a timeout."

### What actually happens

One applies while establishing a connection; the other limits statement execution.

### Production consequence

The wrong control is used for the failure being observed.

### Correct mental model

```text
connect_timeout
    → can I establish the connection?

statement_timeout
    → how long may this statement execute?
```

---

## Mistake 13 — Confusing JSONB with PostgreSQL arrays

### Beginner belief

"A list is a list."

### What actually happens

PostgreSQL `text[]` and `jsonb` are different database types.

### Production consequence

Schema mismatches and incorrect application behavior.

### Correct mental model

Choose the database type that matches the data model.

---

## Mistake 14 — Assuming context-manager behavior is identical across drivers

### Beginner belief

"`with connection:` always closes the connection."

### What actually happens

DB-API drivers can define different context-manager semantics.

### Production consequence

Leaked resources or surprising lifecycle behavior.

### Correct mental model

Read the driver's documentation.

---

# 46. Final Review

## What you now know

You should now understand that psycopg is not "the database."

It is the PostgreSQL driver sitting at the boundary:

```text
Python application
      ↓
DB-API concepts
      ↓
psycopg 3
      ↓
PostgreSQL protocol
      ↓
PostgreSQL
```

You should understand:

- connections;
- cursors;
- connection context managers;
- row factories;
- Python ↔ PostgreSQL adaptation;
- timezone-aware timestamps;
- session settings;
- timeouts;
- PostgreSQL-specific exceptions;
- SQLSTATE;
- advanced binding concepts;
- prepared statements;
- pipeline mode;
- binary/text transfer;
- custom adapters;
- `LISTEN` / `NOTIFY`;
- async awareness;
- psycopg2 legacy differences.

## What you should be able to implement

You should be able to build a small PostgreSQL client that:

```text
loads secure configuration
        ↓
creates a psycopg connection
        ↓
sets application_name
        ↓
sets timeout policy
        ↓
executes SQL
        ↓
returns appropriate row structures
        ↓
handles specific database errors
        ↓
closes resources correctly
```

## What you should be able to debug

You should be able to investigate:

- incorrect connection settings;
- leaked connections;
- missing timeout policies;
- wrong row representations;
- naive timestamps;
- type adaptation mismatches;
- duplicate-key errors;
- statement cancellation;
- PostgreSQL session visibility;
- psycopg2 versus psycopg3 assumptions.

## What you should be able to explain in an interview

You should be able to explain:

```text
what DB-API is
what psycopg adds
how a connection works
how a cursor works
how type adaptation works
how errors become Python exceptions
how SQLSTATE helps classification
how PostgreSQL sessions are observed
why timeouts matter
why prepared statements interact with pooling
```

## What comes next

Next:

`03-parameterized-queries-and-sql-injection.md`

That topic takes the parameter-handling foundation established here and examines safe value binding, dynamic identifiers, allowlists, and SQL injection in depth.

---

# 47. Production Rules to Remember

## Rules I should remember

1. **Know what layer you are working with.**

   Python, DB-API, psycopg, PostgreSQL protocol, and PostgreSQL server have different responsibilities.

2. **Treat database connections as valuable resources.**

   Create them deliberately and close them predictably.

3. **Treat cursors as scoped database-operation interfaces.**

   Do not keep them alive without a reason.

4. **Do not assume all drivers behave identically.**

   DB-API standardization is not identical implementation.

5. **Understand the parameter style and binding behavior of the driver you use.**

6. **Use timezone-aware UTC datetimes for pipeline timestamps.**

7. **Configure connection and statement timeouts deliberately.**

8. **Use `application_name` so database operators can identify your job.**

9. **Catch meaningful PostgreSQL exceptions rather than hiding failures.**

10. **Know what PEP 249 guarantees and what psycopg/PostgreSQL add beyond it.**

11. **Do not assume advanced performance features are automatically beneficial.**

12. **Observe the database side, not only the Python side.**

The durable mental model is:

```text
DB-API gives you a common interface.
The driver implements that interface.
The database still has its own behavior and capabilities.
```

That distinction is the foundation for everything that follows in Python database engineering.
