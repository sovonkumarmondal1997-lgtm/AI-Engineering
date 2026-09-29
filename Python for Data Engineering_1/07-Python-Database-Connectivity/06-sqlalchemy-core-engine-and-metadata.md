# SQLAlchemy Core: Engine and Metadata


## Learning Objectives

After completing this topic, you should be able to:

- Explain why SQLAlchemy Core exists without treating it as a replacement for SQL or the database.
- Distinguish Engine, Connection, Dialect, Driver, Pool, and Database.
- Create and deliberately reuse an Engine with `create_engine()`.
- Explain `engine.connect()` versus `engine.begin()`.
- Execute textual SQL safely with `text()` and bound parameters.
- Choose among `.all()`, `.first()`, `.one()`, `.scalar()`, and `.mappings()`.
- Define `MetaData`, `Table`, and `Column` objects.
- Use `metadata.create_all()` appropriately in controlled environments.
- Reflect existing schemas with `Table(..., autoload_with=engine)` and `inspect(engine)`.
- Compose SQL using `select()`, `where()`, `join()`, `group_by()`, `func.*`, `insert()`, `update()`, and `delete()`.
- Build dynamic filters and configurable columns without unsafe string construction.
- Execute batches and understand SQLAlchemy 2.x `insertmanyvalues` conceptually.
- Configure Engine pooling with `pool_size`, `max_overflow`, `pool_pre_ping`, `pool_recycle`, and `NullPool`.
- Express PostgreSQL `ON CONFLICT DO UPDATE` using the PostgreSQL dialect.
- Inspect generated SQL and parameters and use `literal_binds` for debugging only.
- Compile the same Core expression for PostgreSQL and SQLite.
- Integrate an Engine with pandas and Polars.
- Decide when Core adds enough value over raw psycopg to justify its abstraction.
- Explain where database-specific behavior remains necessary.

## Prerequisites

Topics 01–05 are assumed knowledge:

| Earlier topic | Foundation used here |
| --- | --- |
| DB-API / PEP 249 | connection and cursor mental model |
| psycopg | PostgreSQL driver layer |
| Parameterized queries | bound values rather than string interpolation |
| Transactions | commit/rollback and atomic work |
| Connection pooling | connection reuse, limits, and lifecycle |

The important bridge is:

```text
psycopg Connection
        ↓
SQLAlchemy Connection

psycopg transaction handling
        ↓
SQLAlchemy begin()/transaction contexts

driver parameter binding
        ↓
SQLAlchemy bound parameters
```

Do not re-teach SQL injection, transaction engineering, or pooling engineering here. Use those earlier topics as foundations.

This topic prepares you for SQLAlchemy ORM in Topic 07. It does not teach ORM internals, Alembic migrations, PostgreSQL `COPY`, or large-result streaming.

## Why SQLAlchemy Core Exists

Direct psycopg code is often perfectly reasonable:

```python
conn.execute(
    "SELECT id, name FROM customers WHERE country = %s",
    (country,),
)
```

The difficulty increases as a codebase needs:

- reusable SQL construction,
- dynamic filters,
- metadata-aware code,
- multiple database backends,
- connection/transaction conventions,
- database-specific extensions,
- and integrations with common Python database tooling.

Without structure, applications tend to accumulate:

```text
SQL strings
+
parameter dictionaries
+
ad-hoc schema knowledge
+
driver utilities
+
one-off query builders
```

SQLAlchemy Core gives those concerns a common object model:

```text
Engine
Connection
MetaData
Table
Column
Expressions
Dialect
Result
```

The important engineering point is not that Core makes SQL disappear. It makes SQL **composable as Python objects**.

```text
Core
  ↓
compose + compile + execute

Database
  ↓
parse + plan + execute
```

Core is therefore a database toolkit, not a database replacement.

## 1. SQLAlchemy Core Architecture

Keep this architecture visible:

```text
Python application
        ↓
SQLAlchemy Core
        ↓
Engine
        ↓
Dialect
        ↓
Driver
        ↓
PostgreSQL / SQLite / another database
```

A more complete execution path is:

```text
Python expression
        ↓
SQLAlchemy expression tree
        ↓
Engine
        ↓
Dialect compilation
        ↓
SQL + bound parameters
        ↓
Driver
        ↓
Database
        ↓
driver result
        ↓
SQLAlchemy Result
        ↓
Python
```

### Engine

The Engine is the reusable entry point for database connectivity. It coordinates the dialect and pool and provides Connections.

### Dialect

The Dialect knows how SQLAlchemy should represent and execute database-specific behavior.

### Driver

The Driver is the concrete Python DB-API implementation. In this module it is psycopg 3.

### Connection

The Connection is the active SQLAlchemy database interaction context.

### Database

The database is still the system that executes SQL and enforces database semantics.

### Memorize the distinctions

```text
Engine   ≠ Connection
Dialect  ≠ Driver
Engine   ≠ Database
Core     ≠ Database
```

The abstraction is useful precisely because you understand what sits below it.

## 2. Engine

Create an Engine:

```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg://user:password@localhost:5432/app"
)
```

The URL is conceptually:

```text
postgresql + psycopg://user:password@host:port/database
```

So:

```text
postgresql = SQLAlchemy database dialect
psycopg    = database driver
```

The Engine should normally be created once and reused.

Preferred lifecycle:

```text
process starts
    ↓
create Engine
    ↓
many Connection contexts
    ↓
process shuts down
```

Avoid:

```python
def query_database():
    engine = create_engine(...)
    ...
```

That treats a long-lived connectivity abstraction as if it were a one-shot connection.

An Engine is also not an open database connection by itself. Think of it as the home base from which Connections are obtained.

## 3. `create_engine()`

A production-friendly configuration starts from external configuration:

```python
import os

from sqlalchemy import create_engine

engine = create_engine(
    os.environ["DATABASE_URL"],
)
```

Never commit real credentials to source control.

A typical local URL has this shape:

```text
postgresql+psycopg://<user>:<password>@localhost:5432/<database>
```

### `echo=True`

For local learning:

```python
engine = create_engine(
    os.environ["DATABASE_URL"],
    echo=True,
)
```

This can help you observe SQLAlchemy's engine activity. Treat SQL logging carefully in production because statements and parameter values may expose sensitive data or create excessive log volume.

### Engine configuration

```python
engine = create_engine(
    database_url,
    pool_size=5,
    max_overflow=5,
    pool_pre_ping=True,
)
```

The URL identifies the database/dialect/driver. Keyword arguments configure Engine behavior.

### First connectivity test

```python
from sqlalchemy import text

with engine.connect() as conn:
    value = conn.execute(text("SELECT 1")).scalar_one()
    print(value)
```

If this works, you have crossed:

```text
configuration
 → Engine
 → Dialect
 → psycopg
 → PostgreSQL
```

## 4. Engine vs Connection

| Concept | Meaning |
| --- | --- |
| Engine | reusable connectivity entry point with dialect/pool configuration |
| Connection | active database interaction context |
| Dialect | backend-specific SQL and DB behavior |
| Driver | concrete Python database implementation |
| Pool | manager of reusable physical connections |
| Database | actual server/database executing operations |

This:

```python
engine = create_engine(database_url)
```

does **not** mean:

```text
one permanent PostgreSQL connection is now active
```

This:

```python
with engine.connect() as conn:
    ...
```

creates a Connection context.

The Connection is the object through which Core statements are executed.

A useful lifecycle model is:

```text
Engine
  ↓
Connection
  ↓
execute
  ↓
close Connection
  ↓
release underlying DB resource
```

### Production lesson

Do not keep Connections open across unrelated units of work simply because the Engine exists.

## 5. `engine.connect()`

Use:

```python
with engine.connect() as conn:
    result = conn.execute(
        text("SELECT current_database()")
    )
    print(result.scalar())
```

The context manager establishes a deliberate connection lifetime.

Conceptually:

```text
engine.connect()
      ↓
Connection context
      ↓
database work
      ↓
context exit
      ↓
Connection closes
```

When a pooled Engine is used, the underlying DB-API resource can be returned to the pool rather than discarded.

### Connection and transaction behavior

Do not oversimplify:

```text
connect() = no transaction
```

SQLAlchemy 2.x supports explicit transaction contexts but also has an autobegin model. A statement can cause transaction state to begin implicitly; explicit `begin()` is useful for declaring the intended transaction boundary.

For example:

```python
with engine.connect() as conn:
    conn.execute(text("SELECT 1"))
    conn.commit()
```

is a valid explicit commit-as-you-go style.

For atomic work, the next section is usually clearer.

## 6. `engine.begin()`

Use `engine.begin()` when the business operation has an explicit transaction scope:

```python
with engine.begin() as conn:
    conn.execute(
        text(
            "UPDATE customers "
            "SET active = false "
            "WHERE id = :id"
        ),
        {"id": 42},
    )

    conn.execute(
        text(
            "INSERT INTO pipeline_runs(name, status) "
            "VALUES (:name, :status)"
        ),
        {
            "name": "customer_deactivation",
            "status": "complete",
        },
    )
```

Conceptually:

```text
engine.begin()
    ↓
Connection
    ↓
transaction context
    ↓
statements
    ↓
normal exit → commit
exception   → rollback
```

This maps cleanly to the transaction knowledge from Topic 04.

### Why data engineers use it

A pipeline may need to update several control records atomically:

```text
insert run
update watermark
mark operation complete
```

When those changes represent one unit of work:

```python
with engine.begin() as conn:
    ...
```

makes the intended atomic boundary visible.

## 7. `connect()` vs `begin()`

| Pattern | Meaning | Typical use |
| --- | --- | --- |
| `engine.connect()` | Connection context | reads or deliberate transaction control |
| `engine.begin()` | Connection + transaction context | atomic multi-statement work |

Read:

```python
with engine.connect() as conn:
    rows = conn.execute(
        text("SELECT id, name FROM customers")
    ).all()
```

Atomic write group:

```python
with engine.begin() as conn:
    conn.execute(insert_a)
    conn.execute(insert_b)
```

The important nuance is that `connect()` is not synonymous with "no transaction." SQLAlchemy supports commit-as-you-go through a Connection, and its `begin()` context gives an explicit transaction scope.

Use the API that communicates intent.

## 8. Raw SQL with `text()`

When you already have SQL, Core provides `text()`:

```python
from sqlalchemy import text

stmt = text("""
    SELECT id, name
    FROM customers
    WHERE country = :country
""")
```

Execute with bound values:

```python
with engine.connect() as conn:
    result = conn.execute(
        stmt,
        {"country": "IN"},
    )
```

### Why `text()` exists

It turns textual SQL into a SQLAlchemy statement object that participates in the Core execution system.

It does not make unsafe SQL construction safe.

### Unsafe construction

```python
# ⚠️ INTENTIONALLY BROKEN TRAINING EXAMPLE
stmt = text(
    f"SELECT id, name FROM customers "
    f"WHERE country = '{country}'"
)
```

`text()` receives an already-interpolated string. Any unsafe construction occurred before SQLAlchemy saw it.

Correct:

```python
stmt = text(
    "SELECT id, name FROM customers "
    "WHERE country = :country"
)

with engine.connect() as conn:
    result = conn.execute(
        stmt,
        {"country": country},
    )
```

The security lesson comes from Topic 03:

```text
SQL structure
+
bound values
```

## 9. Bound Parameters

Use:

```python
stmt = text(
    "SELECT * FROM orders "
    "WHERE amount > :minimum"
)
```

and:

```python
result = conn.execute(
    stmt,
    {"minimum": 1000},
)
```

Separate:

```text
SQL structure:
    amount > :minimum

value:
    1000
```

The driver/dialect layer handles the parameter representation expected by the backend.

### Values versus identifiers

This is valid:

```python
text("WHERE country = :country")
```

This is not a valid identifier-substitution strategy:

```python
# ⚠️ NOT A SAFE IDENTIFIER PARAMETER PATTERN
text("SELECT * FROM :table_name")
```

Table names and column names are SQL identifiers. Handle dynamic identifiers through validated allow-lists and known metadata objects, not value binding.

### Connection to Topic 03

The mental model remains:

```text
trusted SQL structure
+
untrusted values
→
bound parameters
```

## 10. SQLAlchemy Result Objects

Executing a statement returns a SQLAlchemy `Result`:

```python
with engine.connect() as conn:
    result = conn.execute(
        text("SELECT id, name FROM customers")
    )

    rows = result.all()
```

Common methods required for this topic:

```python
result.all()
result.first()
result.one()
result.scalar()
result.mappings()
```

### `.all()`

```python
rows = result.all()
```

Materializes all remaining result rows into a Python collection.

Use it when the expected result size is appropriate for memory.

This topic does not teach large-result streaming; that is intentionally deferred to Topic 10.

### `.first()`

```python
row = result.first()
```

Returns the first available row or `None` when there is no row.

Use it when "zero or one row needed from this result" is the function contract.

Do not confuse `.first()` with adding SQL `LIMIT 1`. If the database itself should stop after one row, put that requirement in the statement.

### `.one()`

```python
row = result.one()
```

Requires exactly one result row. It raises when there is no row or more than one row.

This is valuable when uniqueness is a business/database invariant.

### `.scalar()`

```python
value = result.scalar()
```

Extracts the first column of the first result row and closes the result.

Example:

```python
with engine.connect() as conn:
    count = conn.execute(
        text("SELECT count(*) FROM customers")
    ).scalar()
```

### `.mappings()`

```python
rows = result.mappings().all()

for row in rows:
    print(row["id"], row["name"])
```

This presents rows as mapping-style objects.

### Result lifecycle

A result is consumable. Think:

```text
execute
   ↓
Result
   ↓
consume rows/scalars/mappings
   ↓
result is exhausted or closed
```

Do not write code that consumes a Result once and then expects the same rows to magically be available again.

## 11. `one()`, `first()`, and `scalar()`

Choose a method that matches your expected cardinality.

| Method | Meaning |
| --- | --- |
| `first()` | give me the first available row or `None` |
| `one()` | exactly one row is expected |
| `scalar()` | give me the first column of the first row |

### Unique lookup

```python
stmt = (
    select(customers)
    .where(customers.c.id == 42)
)

with engine.connect() as conn:
    customer = conn.execute(stmt).one()
```

### Optional lookup

```python
with engine.connect() as conn:
    customer = conn.execute(stmt).first()
```

### Aggregate

```python
stmt = select(func.count()).select_from(customers)

with engine.connect() as conn:
    count = conn.execute(stmt).scalar()
```

### Why the choice matters

A result API can communicate correctness expectations.

If the database constraint says:

```text
customer id is unique
```

then `.one()` makes that assumption visible.

If a result can legitimately be absent:

```text
optional configuration row
```

then `.first()` or `.one_or_none()` may better describe the behavior.

The required methods are not interchangeable aliases; each expresses a different contract.

## 12. MetaData

Database metadata describes database structures.

In Core:

```python
from sqlalchemy import MetaData

metadata = MetaData()
```

Treat `MetaData` as a Python container/catalog of schema constructs.

```text
MetaData
   ├── customers
   ├── orders
   ├── pipeline_runs
   └── ...
```

A single `MetaData` object can contain many `Table` objects.

### Why this helps

Without structured metadata, query code may repeatedly use:

```text
table name strings
column name strings
```

With Core:

```text
MetaData
    ↓
Table
    ↓
Column
    ↓
Expression
```

The same `Column` object can then be used in:

```python
select(...)
where(...)
join(...)
group_by(...)
order_by(...)
update(...)
delete(...)
```

### Critical distinction

```text
MetaData
=
Python representation

database schema
=
actual database state
```

They are related but not identical.

If the database schema changes independently, your Python metadata can become stale.

That is why reflection exists.

And it is why production schema evolution belongs to migration tooling rather than `create_all()`.

## 13. Table

Define a table:

```python
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
)

metadata = MetaData()

customers = Table(
    "customers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(200), nullable=False),
    Column("country", String(2), nullable=False),
)
```

The `Table` object is Python metadata.

It is not the database table itself.

### What each argument means

```text
"customers"
    ↓
database table name

metadata
    ↓
owning MetaData collection

Column(...)
    ↓
column definitions
```

### Why `Table` matters to Core

Now you can write:

```python
stmt = select(customers.c.id, customers.c.name)
```

instead of manually maintaining:

```sql
SELECT id, name FROM customers
```

You still produce SQL. You simply have a structured representation that SQLAlchemy can inspect and compile.

## 14. Column

A `Column` describes a column in a Core table definition.

```python
Column(
    "country",
    String(2),
    nullable=False,
)
```

Relevant concepts include:

- name,
- type,
- nullability,
- primary key,
- foreign-key relationships,
- server/default awareness.

Example:

```python
from sqlalchemy import ForeignKey, Numeric

orders = Table(
    "orders",
    metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "customer_id",
        ForeignKey("customers.id"),
        nullable=False,
    ),
    Column("amount", Numeric(12, 2), nullable=False),
)
```

The resulting columns participate directly in expressions:

```python
orders.c.amount >= 1000
orders.c.customer_id == customers.c.id
```

That is the bridge:

```text
Column
   ↓
expression
   ↓
SQL
```

### A useful habit

When you see:

```python
orders.c.amount
```

read it mentally as:

> "the SQL column `orders.amount` represented as a Python Core object."

## 15. Database Types vs SQLAlchemy Types

Generic SQLAlchemy types include:

```python
Integer
String
Numeric
Date
DateTime
Boolean
JSON
```

They are abstraction objects, not promises of identical storage semantics across databases.

Conceptually:

```text
SQLAlchemy Integer
      ↓
dialect
      ↓
backend-specific type rendering/handling
```

For example:

```python
Column("amount", Numeric(12, 2))
```

expresses an exact decimal type concept.

But databases still differ in:

- type implementations,
- casts,
- functions/operators,
- indexing,
- storage behavior,
- DDL,
- constraints.

PostgreSQL-specific types can be used when required.

### Production principle

Use generic types when they communicate the actual requirement and remain useful across supported backends.

Use dialect-specific types when the workload genuinely requires vendor semantics.

Do not claim one-to-one portability where none exists.

## 16. `metadata.create_all()`

Controlled schema creation:

```python
metadata.create_all(engine)
```

A full local/test setup might be:

```python
metadata = MetaData()

customers = Table(
    "customers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(200), nullable=False),
)

metadata.create_all(engine)
```

### Good uses

- disposable local development,
- learning labs,
- simple test databases,
- controlled initialization of small environments.

### Not a production migration system

`create_all()` is not a replacement for a migration history.

Production schema changes can require:

```text
additive changes
backfills
index creation strategy
locking analysis
rollback planning
version history
deployment coordination
```

Topic 08 is where Alembic is taught.

Do not teach or implement Alembic here.

## 17. Reflection

What if a table already exists?

```python
from sqlalchemy import MetaData, Table

metadata = MetaData()

orders = Table(
    "orders",
    metadata,
    autoload_with=engine,
)
```

If the schema must be explicit:

```python
orders = Table(
    "orders",
    metadata,
    schema="public",
    autoload_with=engine,
)
```

Conceptually:

```text
existing database schema
       ↓
metadata queries
       ↓
SQLAlchemy reflection
       ↓
Table / Column / constraints
```

Reflection is useful for:

- existing databases,
- metadata exploration,
- generic data tooling,
- migration preparation,
- schema-aware repositories.

Reflection depends on:

- database connectivity,
- database permissions,
- the dialect,
- object existence,
- and what the database exposes through metadata.

### Reflection is not magic

It does not mean:

```text
database
=
fully reproduced Python object graph
```

It means:

```text
discoverable database metadata
→
Python representation
```

That distinction matters when copying schemas or generating tools around databases you did not design.

## 18. `inspect(engine)`

Use `inspect()` for schema information:

```python
from sqlalchemy import inspect

inspector = inspect(engine)

print(inspector.get_table_names())
```

Inspect columns:

```python
for column in inspector.get_columns("customers"):
    print(
        column["name"],
        column["type"],
        column["nullable"],
        column.get("default"),
    )
```

Inspect keys:

```python
print(
    inspector.get_pk_constraint("customers")
)

print(
    inspector.get_foreign_keys("orders")
)
```

### Unknown database workflow

```text
inspect(engine)
    ↓
tables
    ↓
columns
    ↓
primary keys
    ↓
foreign keys
    ↓
reflect a table
    ↓
use Core expressions
```

This is a practical Data Engineering workflow when you inherit an existing database.

### Production security note

Metadata inspection is still database access.

Do not expose arbitrary schema discovery to untrusted callers merely because the API looks read-only.

## 19. Reflecting Existing Tables

Complete exercise:

```python
from sqlalchemy import MetaData, Table, inspect

inspector = inspect(engine)

for name in inspector.get_table_names():
    print(name)

metadata = MetaData()

orders = Table(
    "orders",
    metadata,
    autoload_with=engine,
)

print("Table:", orders.name)

for column in orders.columns:
    print(
        column.name,
        column.type,
        "nullable=", column.nullable,
        "primary_key=", column.primary_key,
    )
```

Use the reflected table:

```python
stmt = (
    select(
        orders.c.id,
        orders.c.amount,
    )
    .limit(10)
)

with engine.connect() as conn:
    rows = conn.execute(stmt).all()
```

### Learner prediction

Before running the code, predict:

1. Which database metadata must be queried.
2. Which columns should be discovered.
3. Which keys should appear.
4. What SQL the final `select()` should compile into.

Then compare prediction with observation.

### Reflection failure checklist

```text
wrong database
wrong schema
wrong table name
permissions
connection problem
identifier quoting/case
object does not exist
database-specific object behavior
```

## 20. SQL Expression Language

The SQL Expression Language is the center of Core.

Start with:

```python
from sqlalchemy import select

stmt = select(customers)
```

SQLAlchemy is building Python expression objects. It is not executing Python code as SQL.

Use this model:

```text
Python expression
       ↓
SQLAlchemy expression tree
       ↓
dialect compilation
       ↓
SQL + bound parameters
       ↓
driver
       ↓
database
```

For example:

```python
stmt = (
    select(
        customers.c.id,
        customers.c.name,
    )
    .where(customers.c.country == "IN")
)
```

The expression:

```python
customers.c.country == "IN"
```

represents a SQL predicate.

The value `"IN"` is treated as a value to be bound.

### Why this matters

The expression language gives you composition without forcing you to assemble SQL syntax manually.

You can start with:

```python
stmt = select(customers)
```

then add:

```python
stmt = stmt.where(...)
```

then:

```python
stmt = stmt.join(...)
```

then:

```python
stmt = stmt.group_by(...)
```

This becomes especially useful when pipeline configuration changes the query shape.

## 21. `select()`

Select a complete table:

```python
stmt = select(customers)
```

Select specific columns:

```python
stmt = select(
    customers.c.id,
    customers.c.name,
)
```

The `.c` collection exposes columns:

```python
customers.c.id
customers.c.name
customers.c.country
```

Execute:

```python
with engine.connect() as conn:
    rows = conn.execute(stmt).all()
```

### Why the expression object matters

A `Select` can be passed to other APIs, inspected, compiled for a dialect, and extended with further expressions.

Compare:

```python
# SQL text representation
text("SELECT id, name FROM customers")
```

with:

```python
# structured representation
select(
    customers.c.id,
    customers.c.name,
)
```

Neither is inherently "more correct." The structured form becomes more valuable as composition requirements grow.

## 22. `where()`

Simple condition:

```python
stmt = (
    select(customers)
    .where(customers.c.country == "IN")
)
```

The important mental transformation is:

```text
Column object
+
Python comparison
        ↓
SQL expression
```

Do not build the same filter through string interpolation.

Bad:

```python
# ⚠️ INTENTIONALLY BROKEN TRAINING EXAMPLE
stmt = text(
    f"SELECT * FROM customers "
    f"WHERE country = '{country}'"
)
```

Correct:

```python
stmt = select(customers).where(
    customers.c.country == country
)
```

### SQL is still generated

Conceptually:

```sql
SELECT customers.id, customers.name, customers.country
FROM customers
WHERE customers.country = <bound parameter>
```

The exact parameter placeholder depends on the dialect/driver.

## 23. Multiple Conditions

Chain `where()` calls:

```python
stmt = (
    select(customers)
    .where(customers.c.country == "IN")
    .where(customers.c.active.is_(True))
)
```

Or use boolean expression helpers:

```python
from sqlalchemy import and_, not_, or_
```

### `and_()`

```python
stmt = select(customers).where(
    and_(
        customers.c.country == "IN",
        customers.c.active.is_(True),
    )
)
```

### `or_()`

```python
stmt = select(customers).where(
    or_(
        customers.c.country == "IN",
        customers.c.country == "US",
    )
)
```

### `not_()`

```python
stmt = select(customers).where(
    not_(customers.c.active.is_(True))
)
```

Do not use Python `and`/`or` to combine SQLAlchemy expressions:

```python
# ⚠️ INTENTIONALLY BROKEN TRAINING EXAMPLE
condition = (
    customers.c.country == "IN"
    and customers.c.active.is_(True)
)
```

Python attempts truth-value evaluation rather than building SQL boolean logic.

Use SQLAlchemy expression operators instead.

## 24. Dynamic Optional Filters

This is one of the highest-value Core patterns for data engineering.

Suppose a pipeline supports:

- country list,
- start date,
- end date,
- minimum amount.

Build conditions in Python:

```python
def build_order_query(
    orders,
    countries: list[str] | None = None,
    start_date=None,
    end_date=None,
    min_amount=None,
):
    conditions = []

    if countries:
        conditions.append(
            orders.c.country.in_(countries)
        )

    if start_date is not None:
        conditions.append(
            orders.c.created_at >= start_date
        )

    if end_date is not None:
        conditions.append(
            orders.c.created_at < end_date
        )

    if min_amount is not None:
        conditions.append(
            orders.c.amount >= min_amount
        )

    stmt = select(
        orders.c.id,
        orders.c.customer_id,
        orders.c.country,
        orders.c.amount,
        orders.c.created_at,
    )

    if conditions:
        stmt = stmt.where(*conditions)

    return stmt
```

### Why this works

```text
configuration
    ↓
validated Python values
    ↓
Column expressions
    ↓
Core statement
    ↓
dialect compilation
    ↓
bound SQL
```

### What this avoids

```text
SQL string templates
+
conditional concatenation
+
manual comma/AND management
```

### Production lesson

Dynamic SQL does not have to mean dynamic SQL **strings**.

Use an expression system.

## 25. JOIN

Suppose:

```text
orders.customer_id → customers.id
```

Core:

```python
stmt = (
    select(
        customers.c.id.label("customer_id"),
        customers.c.name,
        orders.c.id.label("order_id"),
        orders.c.amount,
    )
    .join(
        orders,
        orders.c.customer_id == customers.c.id,
    )
)
```

Conceptually the database receives something like:

```sql
SELECT
    customers.id AS customer_id,
    customers.name,
    orders.id AS order_id,
    orders.amount
FROM customers
JOIN orders
    ON orders.customer_id = customers.id
```

The exact identifier quoting is dialect-dependent.

### Join debugging questions

Before execution, ask:

- What is the left table?
- What is the right table?
- What predicate connects them?
- Can the predicate multiply rows?
- Are duplicate column names labeled where needed?

Core can make a join easier to compose. It cannot make an incorrect join logically correct.

## 26. GROUP BY

Example:

```python
stmt = (
    select(
        orders.c.customer_id,
        func.sum(orders.c.amount).label("total_amount"),
    )
    .group_by(orders.c.customer_id)
)
```

Conceptual SQL:

```sql
SELECT
    customer_id,
    SUM(amount) AS total_amount
FROM orders
GROUP BY customer_id
```

Add filtering:

```python
stmt = (
    select(
        orders.c.customer_id,
        func.sum(orders.c.amount).label("total_amount"),
    )
    .where(orders.c.created_at >= start_date)
    .group_by(orders.c.customer_id)
)
```

The SQL semantics are the same ones you learned in Module 2.6. Core changes how you construct those semantics.

## 27. `func.*`

Use:

```python
from sqlalchemy import func
```

Examples:

```python
func.count()
func.sum(orders.c.amount)
func.avg(orders.c.amount)
```

Grouped analytical query:

```python
stmt = (
    select(
        orders.c.country,
        func.count().label("order_count"),
        func.sum(orders.c.amount).label("revenue"),
        func.avg(orders.c.amount).label("avg_order_value"),
    )
    .group_by(orders.c.country)
)
```

Conceptually:

```text
func.sum(column)
      ↓
SQL function expression
      ↓
dialect compilation
      ↓
SUM(column)
```

### Portability warning

Common functions may compile on several databases, but function availability and semantics can differ.

Do not assume:

```python
func.some_postgres_function(...)
```

will be portable to SQLite.

## 28. INSERT

Build:

```python
from sqlalchemy import insert

stmt = insert(customers).values(
    id=42,
    name="Alice",
    country="IN",
)
```

Execute in a transaction:

```python
with engine.begin() as conn:
    conn.execute(stmt)
```

The important separation is:

```text
construct statement
        ↓
inspect/test if needed
        ↓
execute inside chosen transaction scope
```

### Returning generated values

On supported backends:

```python
stmt = (
    insert(customers)
    .values(
        name="Alice",
        country="IN",
    )
    .returning(customers.c.id)
)

with engine.begin() as conn:
    customer_id = conn.execute(stmt).scalar_one()
```

Whether `RETURNING` works and how it is rendered depends on the backend/dialect.

## 29. UPDATE

Build:

```python
from sqlalchemy import update

stmt = (
    update(customers)
    .where(customers.c.id == 42)
    .values(country="IN")
)
```

Execute:

```python
with engine.begin() as conn:
    result = conn.execute(stmt)
```

Potentially inspect the affected-row count:

```python
print(result.rowcount)
```

### The important safety rule

Core will happily execute:

```python
update(customers).values(country="IN")
```

which targets every row.

A structured API does not remove the need to verify your predicates.

For a destructive or broad update, tests should assert expected scope.

## 30. DELETE

Build:

```python
from sqlalchemy import delete

stmt = (
    delete(customers)
    .where(customers.c.id == 42)
)
```

Execute:

```python
with engine.begin() as conn:
    conn.execute(stmt)
```

### Dangerous version

```python
# ⚠️ INTENTIONALLY BROKEN TRAINING EXAMPLE
stmt = delete(customers)

with engine.begin() as conn:
    conn.execute(stmt)
```

This targets every row.

The production mental model is:

```text
SQLAlchemy prevents accidental string construction problems
but does not prove SQL intent is correct.
```

Use tests and review for data-destroying operations.

## 31. Batch Execution

The roadmap requires:

```python
conn.execute(
    insert(table),
    list_of_dicts,
)
```

Example:

```python
rows = [
    {"id": 1, "name": "Alice", "country": "IN"},
    {"id": 2, "name": "Bob", "country": "US"},
    {"id": 3, "name": "Carol", "country": "GB"},
]

with engine.begin() as conn:
    conn.execute(
        insert(customers),
        rows,
    )
```

### What is being passed?

One statement:

```python
insert(customers)
```

Many parameter dictionaries:

```text
row 1
row 2
row 3
...
```

SQLAlchemy's execution system and the selected dialect/driver determine how this is sent to the database.

### Why this is useful

It is a straightforward pattern for moderate batch writes.

### What it is not

Do not teach yourself:

```text
Core batch execution
=
PostgreSQL COPY
```

They are different mechanisms.

Topic 09 covers database-native bulk loading.

### Measure

For an actual workload measure:

```text
elapsed seconds
rows inserted
rows/second
transaction duration
memory
database load
```

Never copy a benchmark number from someone else's machine into your own design document.

## 32. `insertmanyvalues`

SQLAlchemy 2.x has an internal batching strategy called `insertmanyvalues` for qualifying INSERT operations.

The useful high-level model is:

```text
one Core INSERT structure
+
many parameter sets
        ↓
SQLAlchemy batching strategy
        ↓
dialect/driver
        ↓
database
```

The exact SQL shape is not guaranteed to be one giant statement in every case.

Factors include:

- SQLAlchemy version,
- dialect,
- driver,
- statement shape,
- backend support,
- insert mode,
- page/batch configuration.

### Why batching can help

It can reduce overhead associated with repeated statement execution and round trips.

### Why performance is still a question

The database still has to:

- parse/process the operation,
- check constraints,
- update indexes,
- write WAL where applicable,
- and maintain transactional state.

The right batch size is empirical.

Do a small benchmark in your own environment before standardizing a value.

## 33. SQLAlchemy Engine Pooling

The SQLAlchemy Engine normally coordinates a pool.

This connects directly to Topic 05:

```text
Topic 05
psycopg_pool.ConnectionPool
        ↓
driver-level pooling

Topic 06
SQLAlchemy Engine
        ↓
SQLAlchemy pool
        ↓
driver
```

A Connection context borrows a usable database resource from the Engine's pool when required.

```text
Engine
  ↓
Pool
  ↓
DBAPI connection
  ↓
SQLAlchemy Connection
  ↓
psycopg
  ↓
PostgreSQL
```

### Why this is important

The abstraction changed; the resource did not.

PostgreSQL still has:

- finite connection capacity,
- session resources,
- authentication cost,
- server-side memory,
- and connection limits.

Do not make this mistake:

> "Because SQLAlchemy has a pool, I no longer need to reason about connections."

You still do.

### Engine pool versus driver pool

You may have seen:

```python
from psycopg_pool import ConnectionPool
```

in Topic 05.

That is a driver-level pool.

SQLAlchemy's Engine manages its own pool abstraction.

Do not casually stack both without understanding why.

## 34. Engine Pool Options

### `pool_size`

```python
engine = create_engine(
    database_url,
    pool_size=5,
)
```

Think of this as the persistent base pool size for the Engine.

### `max_overflow`

```python
engine = create_engine(
    database_url,
    pool_size=5,
    max_overflow=10,
)
```

Conceptually, an Engine can reach:

```text
base pool = 5
overflow  = 10
potential simultaneous connection use = 15
```

That is not a guarantee that 15 connections are always open.

It is a capacity setting.

And it is not the entire application's connection count if other libraries/processes create connections separately.

### `pool_pre_ping`

```python
engine = create_engine(
    database_url,
    pool_pre_ping=True,
)
```

This helps detect stale/disconnected pooled connections at checkout.

Think:

```text
borrow connection
       ↓
health check
       ↓
usable?
   yes → execute
   no  → recycle/reconnect according to pool/dialect behavior
```

It adds an operational check and therefore should be understood as a reliability/performance trade-off.

### `pool_recycle`

```python
engine = create_engine(
    database_url,
    pool_recycle=1800,
)
```

This allows connections older than the configured age to be recycled rather than retained indefinitely.

It can be useful when:

- load balancers,
- proxies,
- firewalls,
- database policies,
- or infrastructure timeouts

make very old connections undesirable.

It is not a substitute for connection health handling.

### `NullPool`

```python
from sqlalchemy.pool import NullPool

engine = create_engine(
    database_url,
    poolclass=NullPool,
)
```

`NullPool` means SQLAlchemy does not keep a reusable connection pool for the Engine.

This may make sense when:

- an external pooler owns the lifecycle,
- the workload is intentionally short-lived,
- connection reuse provides little value,
- or deployment architecture requires no local pool.

It also means connection reuse benefits are intentionally sacrificed.

### Pooling is an architecture decision

Ask:

```text
Who owns connection pooling?
SQLAlchemy?
driver?
PgBouncer?
managed database proxy?
```

Then avoid accidentally creating multiple independent pools that multiply connection pressure.

## 35. PostgreSQL Dialect

The PostgreSQL dialect sits between Core expressions and the driver:

```text
Core expression
       ↓
PostgreSQL dialect
       ↓
psycopg 3
       ↓
PostgreSQL
```

The dialect handles database-specific syntax and behavior such as:

- identifier quoting,
- PostgreSQL data types,
- PostgreSQL-specific SQL constructs,
- parameter/driver integration,
- and dialect-specific compilation.

### Generic Core example

```python
stmt = select(customers).where(
    customers.c.country == "IN"
)
```

This is expressed using generic Core constructs.

### PostgreSQL-specific example

```python
from sqlalchemy.dialects.postgresql import insert
```

That import explicitly selects PostgreSQL-specific behavior.

This is not automatically a problem.

It becomes a problem only when the code claims or requires portability that the construct cannot provide.

## 36. PostgreSQL Upsert

PostgreSQL supports:

```sql
INSERT ...
ON CONFLICT ...
DO UPDATE ...
```

SQLAlchemy Core exposes this through the PostgreSQL dialect:

```python
from sqlalchemy.dialects.postgresql import insert
```

Example:

```python
stmt = insert(customers).values(
    id=42,
    name="Alice",
    country="IN",
)

stmt = stmt.on_conflict_do_update(
    index_elements=[customers.c.id],
    set_={
        "name": stmt.excluded.name,
        "country": stmt.excluded.country,
    },
)
```

Execute:

```python
with engine.begin() as conn:
    conn.execute(stmt)
```

### Understand `excluded`

PostgreSQL's `excluded` represents the row proposed by the failed INSERT.

Therefore:

```python
stmt.excluded.name
```

means:

> the incoming `name` value that was part of the INSERT.

### Full function

```python
def upsert_customer(
    conn,
    customer: dict[str, object],
) -> None:
    stmt = insert(customers).values(customer)

    stmt = stmt.on_conflict_do_update(
        index_elements=[customers.c.id],
        set_={
            "name": stmt.excluded.name,
            "country": stmt.excluded.country,
        },
    )

    conn.execute(stmt)
```

### Batch upsert

```python
rows = [
    {
        "id": 1,
        "name": "Alice",
        "country": "IN",
    },
    {
        "id": 2,
        "name": "Bob",
        "country": "US",
    },
]

stmt = insert(customers)

stmt = stmt.on_conflict_do_update(
    index_elements=[customers.c.id],
    set_={
        "name": stmt.excluded.name,
        "country": stmt.excluded.country,
    },
)

with engine.begin() as conn:
    conn.execute(stmt, rows)
```

### Production warning

The PostgreSQL-specific upsert path is intentionally vendor-specific.

Do not assume the same statement can be used unchanged on SQLite or another database.

Also, do not assume every `on_conflict_do_update()` batch uses the same insert batching strategy as a simple generic INSERT. Measure the actual path.

## 37. Portable vs Dialect-Specific SQL

A useful classification:

### More portable

```text
select()
where()
join()
group_by()
common INSERT/UPDATE/DELETE
common generic types
```

### Less portable

```text
PostgreSQL ON CONFLICT
PostgreSQL-only functions/operators
PostgreSQL-specific types
COPY
vendor-specific DDL
vendor-specific locking
database extensions
```

Memorize:

> **SQLAlchemy improves portability. It does not guarantee portability.**

### Why the distinction matters

A Core expression can have:

```text
same logical intent
+
different compiled SQL
+
different database capabilities
+
different execution semantics
```

Portability is therefore an engineering requirement to test.

Not a property to assume.

### Decision questions

Before designing for portability:

1. Do we actually support multiple databases?
2. Which database features are required?
3. Which features have dialect-specific implementations?
4. Can vendor-specific code be isolated?
5. Will CI execute important queries against each supported backend?
6. Does abstraction reduce enough complexity to justify itself?

## 38. Dynamic SQL with Expressions

Configuration-driven pipelines frequently need dynamic query shapes.

Suppose:

```python
config = {
    "countries": ["IN", "US"],
    "start_date": start_date,
    "min_amount": 1000,
}
```

Do not do:

```python
# ⚠️ INTENTIONALLY BROKEN TRAINING EXAMPLE
sql = (
    "SELECT * FROM orders "
    f"WHERE amount >= {config['min_amount']}"
)
```

Instead:

```python
conditions = []

if config["countries"]:
    conditions.append(
        orders.c.country.in_(config["countries"])
    )

if config["start_date"] is not None:
    conditions.append(
        orders.c.created_at >= config["start_date"]
    )

if config["min_amount"] is not None:
    conditions.append(
        orders.c.amount >= config["min_amount"]
    )

stmt = select(orders)

if conditions:
    stmt = stmt.where(*conditions)
```

The architecture is:

```text
configuration
     ↓
validated data structures
     ↓
SQLAlchemy expressions
     ↓
Core statement
     ↓
compiled SQL
```

### What is safer here?

The user/config data becomes expression values.

It does not become SQL syntax.

### More composability

You can add another condition without rewriting the whole query:

```python
if active_only:
    conditions.append(
        orders.c.status == "active"
    )
```

Then reuse the same builder.

This is one of Core's highest-value features for data engineering pipelines.

## 39. Safe Dynamic Columns

Column selection is an identifier problem.

Suppose configuration contains:

```python
requested_columns = [
    "customer_id",
    "name",
    "country",
]
```

Create an allow-list:

```python
AVAILABLE_COLUMNS = {
    "customer_id": customers.c.id,
    "name": customers.c.name,
    "country": customers.c.country,
}
```

Validate:

```python
selected_columns = []

for name in requested_columns:
    if name not in AVAILABLE_COLUMNS:
        raise ValueError(
            f"Unsupported column: {name!r}"
        )

    selected_columns.append(
        AVAILABLE_COLUMNS[name]
    )
```

Build:

```python
stmt = select(*selected_columns)
```

### Why not string formatting?

Because:

```text
configuration string
    ↓
validated allow-list
    ↓
known Column object
```

is fundamentally safer than:

```text
configuration string
    ↓
SQL text fragment
```

### General rule

> Dynamic identifiers are a validation/design problem, not a parameter-binding problem.

Parameter binding is for values.

Use structured metadata for identifiers.

## 40. Generated SQL

Core statements are Python objects.

Inspect the generic representation:

```python
print(stmt)
```

For a dialect-aware representation:

```python
from sqlalchemy.dialects import postgresql

compiled = stmt.compile(
    dialect=postgresql.dialect()
)

print(compiled)
print(compiled.params)
```

### Why inspect it?

Generated SQL inspection can reveal:

- missing predicates,
- wrong join conditions,
- unexpected selected columns,
- wrong grouping,
- unexpected dialect behavior,
- and query shapes you did not intend.

### What it cannot tell you

Printed SQL does not prove:

- the execution plan,
- index usage,
- lock behavior,
- disk I/O,
- actual runtime,
- database CPU,
- or result cardinality.

Those require database-side observation and execution measurement.

Use:

```text
generated SQL
+
database plan/timing
```

for serious diagnosis.

## 41. `literal_binds`

Debugging example:

```python
debug_sql = stmt.compile(
    dialect=postgresql.dialect(),
    compile_kwargs={
        "literal_binds": True,
    },
)

print(debug_sql)
```

This can show a human-readable statement with values rendered into the debug representation.

### Why useful

It can make a statement easier to inspect and discuss.

### Why debugging only

Normal execution should still use:

```python
conn.execute(stmt)
```

with values represented as bound parameters.

Do not construct production execution around:

```python
str(debug_sql)
```

and then send that string back to the database.

Remember:

```text
debugging representation
        ≠
production execution mechanism
```

## 42. SQL Generation Exercise

Rewrite five representative queries from your Module 2.6 work.

The exact five SQL statements are not present in this Topic 06 specification, so use your actual Module 2.6 statements. The patterns below are representative only.

### 1. Select

```python
stmt = select(
    customers.c.id,
    customers.c.name,
)
```

### 2. Filter

```python
stmt = (
    select(customers)
    .where(customers.c.country == country)
)
```

### 3. Join

```python
stmt = (
    select(
        customers.c.name,
        orders.c.amount,
    )
    .join(
        orders,
        orders.c.customer_id == customers.c.id,
    )
)
```

### 4. Aggregation

```python
stmt = (
    select(
        orders.c.customer_id,
        func.sum(orders.c.amount).label("total_amount"),
    )
    .group_by(orders.c.customer_id)
)
```

### 5. Update/upsert

```python
stmt = (
    update(customers)
    .where(customers.c.id == customer_id)
    .values(country=country)
)
```

or the PostgreSQL-specific upsert:

```python
stmt = insert(customers).values(
    id=customer_id,
    name=name,
    country=country,
)

stmt = stmt.on_conflict_do_update(
    index_elements=[customers.c.id],
    set_={
        "name": stmt.excluded.name,
        "country": stmt.excluded.country,
    },
)
```

For every query:

1. Build the Core expression.
2. Print it.
3. Compile it for PostgreSQL.
4. Inspect parameters.
5. Execute it against PostgreSQL.
6. Compare its result with the original SQL.
7. Explain portability.

## 43. PostgreSQL vs SQLite Compilation

Use the same generic statement:

```python
stmt = (
    select(
        customers.c.id,
        customers.c.name,
    )
    .where(customers.c.country == country)
)
```

PostgreSQL:

```python
from sqlalchemy.dialects import postgresql

pg = stmt.compile(
    dialect=postgresql.dialect()
)

print(pg)
print(pg.params)
```

SQLite:

```python
from sqlalchemy.dialects import sqlite

sq = stmt.compile(
    dialect=sqlite.dialect()
)

print(sq)
print(sq.params)
```

### What stays the same?

The logical expression:

```text
SELECT id, name
WHERE country = value
```

### What can change?

- parameter marker style,
- quoting,
- type rendering,
- backend-specific syntax.

### Now test a PostgreSQL-specific expression

```python
from sqlalchemy.dialects.postgresql import insert

pg_upsert = insert(customers).values(
    id=42,
    name="Alice",
    country="IN",
).on_conflict_do_update(
    index_elements=[customers.c.id],
    set_={
        "name": "Alice",
        "country": "IN",
    },
)
```

The import itself communicates the portability boundary.

### Exercise conclusion

Write:

```text
Generic Core improves portability.

Dialect-specific Core makes vendor capabilities accessible.

Neither gives identical database semantics.
```

## 44. Reflection and Schema Copy Exercise

Reflection can be combined with `to_metadata()` for a controlled structure-copy exercise.

Source:

```python
from sqlalchemy import MetaData, Table

source_metadata = MetaData()

source_table = Table(
    "orders",
    source_metadata,
    autoload_with=source_engine,
)
```

Target metadata:

```python
target_metadata = MetaData()

source_table.to_metadata(
    target_metadata
)
```

Create the target structure:

```python
target_metadata.create_all(
    target_engine
)
```

Verify:

```python
target_inspector = inspect(target_engine)

print(
    target_inspector.get_columns("orders")
)

print(
    target_inspector.get_pk_constraint("orders")
)

print(
    target_inspector.get_foreign_keys("orders")
)
```

### What this demonstrates

```text
source database
    ↓
reflection
    ↓
Python metadata
    ↓
new metadata collection
    ↓
DDL generation
    ↓
target database
```

### What this does not prove

It does not prove the databases are operationally identical.

Separate handling may still be necessary for:

- grants and permissions,
- extensions,
- triggers,
- functions,
- policies,
- special indexes,
- partitioning,
- sequences/ownership,
- vendor-specific objects,
- or deployment configuration.

Do not mistake metadata copying for backup/restore.

## 45. pandas Integration

Pandas supports SQLAlchemy Engines and Connections as database connectivity inputs for SQL reads and writes.

Read a Core statement:

```python
import pandas as pd

stmt = select(
    customers.c.id,
    customers.c.name,
    customers.c.country,
)

df = pd.read_sql(
    stmt,
    engine,
)
```

Write a DataFrame:

```python
df.to_sql(
    "customer_snapshot",
    engine,
    if_exists="append",
    index=False,
)
```

### Architecture boundary

```text
pandas DataFrame
       ↓
SQLAlchemy Engine / Connection
       ↓
Dialect
       ↓
Driver
       ↓
Database
```

### When this is convenient

- small or moderate control-table exports,
- notebook analysis,
- application/reporting integration,
- simple DataFrame-to-table operations.

### When to stop assuming convenience equals efficiency

For large data movement, inspect:

```text
row volume
row width
transaction size
driver behavior
round trips
database write cost
memory
```

`to_sql()` does not automatically turn a DataFrame write into the optimal bulk-loading method.

Topic 09 covers database-native bulk loading.

### Ownership reminder

When your application owns the Engine, it also owns its lifecycle. Do not create a disposable Engine for each DataFrame operation.

## 46. Polars Integration

Polars provides database I/O functions that can work with SQLAlchemy connectivity.

Read:

```python
import polars as pl

stmt = select(
    customers.c.id,
    customers.c.name,
)

df = pl.read_database(
    query=stmt,
    connection=engine,
)
```

Write:

```python
rows_written = df.write_database(
    table_name="customer_snapshot",
    connection=engine,
    if_table_exists="append",
)
```

### Responsibility split

```text
SQLAlchemy
  ↓
database connection
SQL construction
dialect handling
transaction/resource boundary

Polars
  ↓
DataFrame representation
columnar transformations
DataFrame-side analysis
```

### Important current-API detail

Polars supports SQLAlchemy connections/selectables for database reads, and current versions also expose separate SQLAlchemy and ADBC write paths.

Do not assume:

```text
Polars database I/O
=
always SQLAlchemy
```

or:

```text
SQLAlchemy
=
always the fastest DataFrame transfer path
```

Measure the actual integration.

### Data engineering boundary

A common pattern is:

```text
database query
    ↓
SQLAlchemy Core
    ↓
Polars DataFrame
    ↓
columnar transformation
```

That is a complementary use of two abstractions rather than a competition between them.

## 47. SQLAlchemy Core in Data Engineering

Core is especially useful around operational database boundaries.

### Workload A — Pipeline metadata

Use:

```python
insert(pipeline_runs)
update(pipeline_runs)
select(pipeline_runs)
```

for:

- run tracking,
- status,
- watermarks,
- row counts,
- data-quality metadata.

### Workload B — Dynamic extraction

A pipeline may construct:

```text
high-water mark
+
country filter
+
date range
+
source system filter
```

Core expressions keep the values bound while allowing query structure to change.

### Workload C — Control-table lookup

```text
dataset configuration
watermark
feature flag
job state
```

These are usually small operational tables and are a natural match for explicit Core queries.

### Workload D — Moderate staging writes

Use Core batch execution where the volume and latency requirements fit.

### Workload E — PostgreSQL-specific upsert

Use:

```python
sqlalchemy.dialects.postgresql.insert
```

when PostgreSQL `ON CONFLICT` is a deliberate requirement.

### Why Core is useful to data engineers

Data engineering frequently requires both:

```text
SQL-level control
+
Python-level composition
```

Core sits directly at that boundary.

It avoids forcing every database operation into an object-relational model.

## 48. Core vs Raw psycopg

Compare:

| Requirement | Raw psycopg | SQLAlchemy Core |
| --- | --- | --- |
| Direct driver control | strong | less direct |
| SQL composition | manual | expression-based |
| Metadata objects | manual | `MetaData` / `Table` / `Column` |
| Portability | limited by handwritten SQL | stronger for generic constructs |
| PostgreSQL-specific work | very direct | possible through dialect/driver |
| Query inspection | SQL is already explicit | compile expression objects |
| Connection abstraction | driver-level | Engine/Connection |
| DataFrame integration | possible | common connectable boundary |

### Raw psycopg can be the better fit when

```text
SQL is already simple and stable
+
PostgreSQL-only behavior is required
+
driver-specific control matters
+
another abstraction would add little value
```

### Core can be the better fit when

```text
query composition is complex
+
metadata is reused
+
dynamic filters are common
+
multiple backends are supported/tested
+
a repository abstraction benefits from Core objects
```

### Do not make a technology choice by prestige

A mature engineer can use both.

Example:

```text
Core repository
     +
small raw-psycopg escape hatch
```

can be reasonable when the escape hatch is deliberate and isolated.

## 49. When Core Is a Good Fit

Core tends to fit well when you need:

### Composable SQL

Many query variants share the same base tables and expressions.

### Metadata-driven pipelines

The program needs structured descriptions of tables and columns.

### Repository/data-access layers

You want database operations encapsulated in functions while keeping SQL semantics visible.

### Moderate database operations

Control tables and ordinary CRUD workloads often fit naturally.

### Multiple database backends

Generic expressions can reduce duplicate SQL where actual portability is required.

### SQL-level control without ORM behavior

You prefer:

```text
tables
columns
expressions
transactions
results
```

rather than an object graph.

The decision question is:

> What complexity does Core remove, and what complexity does it add?

That question is more useful than "Is Core good?"

## 50. When Core Is Not Enough

### Database-specific features

A dialect-specific API or carefully reviewed raw SQL may be clearer.

### Specialized bulk loading

Large loads may require database-native tools such as PostgreSQL `COPY`.

Topic 09.

### Large result extraction

Bounded-memory result handling introduces another set of design considerations.

Topic 10.

### Schema migration

Runtime table operations are different from schema migration history.

Topic 08.

### Object-domain modeling

Application code may benefit from ORM mapping.

Topic 07.

### General rule

```text
Core is one layer of the database toolkit.
```

Do not make it the answer to every database problem.

## 51. Portability Limits

Portability is a requirement, not a side effect.

```text
portable Python API
        ≠
identical database semantics
```

Potential differences include:

- SQL syntax,
- types,
- functions,
- upserts,
- locking,
- DDL,
- indexes,
- extensions,
- transaction behavior,
- and performance.

### Example: generic type

```python
Column("amount", Numeric(12, 2))
```

is an abstraction.

The actual backend remains responsible for storage and behavior.

### Example: PostgreSQL upsert

```python
from sqlalchemy.dialects.postgresql import insert
```

creates explicit vendor coupling.

### Example: COPY

```text
PostgreSQL-specific
```

and therefore belongs outside a claim of pure backend neutrality.

### Portability decision framework

Ask:

1. Do we really need more than one database?
2. Which features must remain portable?
3. Which features are intentionally vendor-specific?
4. Can vendor-specific code be isolated?
5. Will the supported backends be tested?
6. What is the cost of maintaining two dialect paths?

Memorize:

> **SQLAlchemy improves portability. It does not guarantee portability.**

## 52. Internal Query Flow

Walk through:

```python
stmt = (
    select(
        customers.c.id,
        customers.c.name,
    )
    .where(customers.c.country == "IN")
)

with engine.connect() as conn:
    result = conn.execute(stmt)
```

### Stage 1 — Expression construction

`select(...)` and the comparison create SQLAlchemy expression objects.

### Stage 2 — Expression structure

Conceptually:

```text
SELECT
  id
  name
FROM customers
WHERE country = <bound value>
```

### Stage 3 — Dialect compilation

The target dialect determines backend-compatible SQL syntax.

### Stage 4 — Binding

The value `"IN"` is associated with the expression as data.

### Stage 5 — Driver

The Engine works through psycopg for PostgreSQL.

### Stage 6 — Database

PostgreSQL executes the statement.

### Stage 7 — Result

The database response travels back through the driver into SQLAlchemy's Result abstraction.

```text
Python expression
      ↓
SQLAlchemy expression tree
      ↓
Dialect
      ↓
SQL + bound values
      ↓
Driver
      ↓
PostgreSQL
      ↓
driver result
      ↓
SQLAlchemy Result
      ↓
Python
```

Do not depend on private implementation classes. The flow above is conceptual and stable enough to guide engineering reasoning.

## 53. Internal Engine + Pool Flow

Use:

```python
with engine.connect() as conn:
    ...
```

Think:

```text
Engine
  ↓
Pool
  ↓
physical DB connection
  ↓
SQLAlchemy Connection
  ↓
psycopg
  ↓
PostgreSQL
```

### Borrow/return model

```text
borrow
  ↓
use
  ↓
close Connection context
  ↓
release underlying resource
```

The same resource principles from Topic 05 still apply.

### Process ownership

Do not treat an Engine pool as a safe cross-process shared object.

A process boundary is an ownership boundary.

This matters when applications use:

- multiprocessing,
- worker processes,
- pre-fork servers,
- `os.fork()`.

The safe pattern is to initialize process-local database resources according to the process architecture.

## 54. Reflection Internals

Reflection is effectively a reverse-description workflow.

Hand-defined:

```text
Python metadata
    ↓
DDL generation
    ↓
database
```

Reflected:

```text
database
    ↓
metadata queries
    ↓
SQLAlchemy
    ↓
Python metadata
```

Conceptually:

```text
inspect(engine)
      ↓
schema information
      ↓
Table / Column / constraint objects
```

This is useful when the database is the system you discover rather than the schema you authored.

### Reflection limitations

The Python representation may not capture every behavior associated with:

- triggers,
- permissions,
- extensions,
- policies,
- generated functions,
- unusual indexes,
- partitioning details,
- operational configuration,
- vendor-specific objects.

Therefore:

```text
reflected metadata
=
discovered model of schema objects

not:

complete database backup
```

## 55. Dialect Compilation

Take:

```python
stmt = (
    select(customers.c.id)
    .where(customers.c.country == country)
)
```

Compile PostgreSQL:

```python
from sqlalchemy.dialects import postgresql

pg_stmt = stmt.compile(
    dialect=postgresql.dialect()
)

print(pg_stmt)
print(pg_stmt.params)
```

Compile SQLite:

```python
from sqlalchemy.dialects import sqlite

sqlite_stmt = stmt.compile(
    dialect=sqlite.dialect()
)

print(sqlite_stmt)
print(sqlite_stmt.params)
```

The logical intent remains:

```text
SELECT customer id
WHERE country equals value
```

The database-facing representation can change.

### Why this matters

Dialect compilation is where database differences become visible without executing the statement.

But compilation is not proof of runtime compatibility.

The final test is:

```text
compile
+
execute
+
verify results
```

## 56. Complete Hands-On Lab

The labs should be completed in the shared `db_lab` project already established for Module 2.7.

### Lab 1 — Create an Engine

**Objective:** connect to PostgreSQL through SQLAlchemy.

```python
import os
from sqlalchemy import create_engine

engine = create_engine(
    os.environ["DATABASE_URL"],
)
```

**Learner prediction**

Explain:

```text
postgresql = dialect
psycopg = driver
Engine = connectivity entry point
```

**Code**

```python
from sqlalchemy import text

with engine.connect() as conn:
    print(
        conn.execute(
            text("SELECT 1")
        ).scalar_one()
    )
```

**Expected result**

The query returns `1`.

**Debugging**

Check:

```text
DATABASE_URL
PostgreSQL container
port
credentials
psycopg installation
```

**Production takeaway**

Create the Engine once and reuse it.

---

### Lab 2 — `text()` and Bound Parameters

**Objective:** execute safe raw SQL.

```python
stmt = text("""
    SELECT id, name
    FROM customers
    WHERE country = :country
""")

with engine.connect() as conn:
    result = conn.execute(
        stmt,
        {"country": "IN"},
    )

    for row in result:
        print(row)
```

**Prediction**

Write the SQL structure and parameters separately.

**Debugging**

Print:

```python
print(stmt)
```

**Production takeaway**

Never construct value-bearing SQL with f-strings.

---

### Lab 3 — `engine.begin()`

**Objective:** make multi-statement work atomic.

```python
with engine.begin() as conn:
    conn.execute(
        text(
            "UPDATE customers "
            "SET country = :country "
            "WHERE id = :id"
        ),
        {
            "country": "IN",
            "id": 42,
        },
    )

    conn.execute(
        text(
            "INSERT INTO pipeline_runs(name, status) "
            "VALUES (:name, :status)"
        ),
        {
            "name": "core-lab",
            "status": "success",
        },
    )
```

**Failure experiment**

Raise an exception after the first statement:

```python
with engine.begin() as conn:
    conn.execute(first_statement)
    raise RuntimeError("force rollback")
```

Then verify the first statement did not commit.

**Production takeaway**

Transaction scope should match unit-of-work intent.

---

### Lab 4 — Results

Practice:

```python
result.all()
result.first()
result.one()
result.scalar()
result.mappings().all()
```

Example:

```python
with engine.connect() as conn:
    rows = conn.execute(
        select(customers)
    ).all()

    first_row = conn.execute(
        select(customers).order_by(customers.c.id)
    ).first()

    maybe_one = conn.execute(
        select(customers)
        .where(customers.c.id == 42)
    ).first()

    count = conn.execute(
        select(func.count()).select_from(customers)
    ).scalar()

    mappings = conn.execute(
        select(customers)
    ).mappings().all()
```

For each, write down the returned shape before checking it.

**Production takeaway**

Result method choice communicates your function contract.

---

### Lab 5 — Define Metadata

Create:

```text
customers
orders
pipeline_runs
```

Use one shared `MetaData`.

```python
metadata = MetaData()

customers = Table(
    "customers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(200), nullable=False),
    Column("country", String(2), nullable=False),
)
```

Then define the related tables.

Run:

```python
metadata.create_all(engine)
```

only in your controlled lab environment.

**Production takeaway**

`create_all()` is useful setup tooling, not a schema migration strategy.

---

### Lab 6 — Reflection

```python
inspector = inspect(engine)

print(inspector.get_table_names())

reflected = MetaData()

orders_reflected = Table(
    "orders",
    reflected,
    autoload_with=engine,
)

for column in orders_reflected.columns:
    print(
        column.name,
        column.type,
        column.nullable,
        column.primary_key,
    )
```

**Production takeaway**

You can build tools against schemas your code did not originally define.

---

### Lab 7 — Expression Language

Build:

```python
stmt = select(
    customers.c.id,
    customers.c.name,
).where(
    customers.c.country == "IN"
)
```

Print it.

Compile it.

Execute it.

Compare it with the SQL you predict.

---

### Lab 8 — Dynamic Filters

Implement:

```python
def build_order_query(
    countries=None,
    start_date=None,
    end_date=None,
    min_amount=None,
):
    ...
```

Required constraints:

```text
no string formatting
no SQL fragments assembled from configuration
all values bound
optional conditions composable
```

Test all combinations.

---

### Lab 9 — Batch Insert

Generate 10,000 test rows:

```python
rows = [
    {
        "name": f"customer-{i}",
        "country": "IN",
    }
    for i in range(10_000)
]
```

Execute:

```python
with engine.begin() as conn:
    conn.execute(
        insert(customers),
        rows,
    )
```

Measure:

```text
elapsed seconds
row count
rows/second
transaction duration
memory usage
```

Do not fabricate the results.

---

### Lab 10 — PostgreSQL Upsert

```python
stmt = insert(customers)

stmt = stmt.on_conflict_do_update(
    index_elements=[customers.c.id],
    set_={
        "name": stmt.excluded.name,
        "country": stmt.excluded.country,
    },
)
```

Execute a deliberately repeated dataset and verify:

```text
first run → inserts
second run → conflicts then updates
```

---

### Lab 11 — Generated SQL

For one statement:

```python
print(stmt)

compiled = stmt.compile(
    dialect=postgresql.dialect()
)

print(compiled)
print(compiled.params)
```

Then use `literal_binds` only to create debugging output.

---

### Lab 12 — pandas / Polars

Read the same logical dataset through:

```python
pd.read_sql(...)
```

and:

```python
pl.read_database(...)
```

Observe differences in:

```text
result type
memory behavior
workflow ergonomics
```

Do not declare one universally better.

## 57. `core_repository.py` Exercise

The roadmap specifically asks for a repository exercise. Because this module must not create another file, implement the exercise inside your existing lab project separately; this document contains the complete specification and representative implementation.

### Required objects

Define one shared `MetaData` containing:

```text
customers
orders
pipeline_runs
```

### Required repository capabilities

1. Build a dynamic `select()`.
2. Join customers and orders.
3. Support optional:
   - country list,
   - date range,
   - minimum amount.
4. Use no string formatting for SQL construction.
5. Upsert 10,000 customer rows using PostgreSQL `on_conflict_do_update()`.
6. Reflect an unknown table.
7. Copy its structure to another database.
8. Test repository functions against PostgreSQL.
9. Run at least one generic function against SQLite.
10. Document portability limits.

### Representative repository

```python
from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    Column,
    create_engine,
    insert,
    select,
)
from sqlalchemy.dialects.postgresql import insert as pg_insert


metadata = MetaData()

customers = Table(
    "customers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(200), nullable=False),
    Column("country", String(2), nullable=False),
)

orders = Table(
    "orders",
    metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "customer_id",
        ForeignKey("customers.id"),
        nullable=False,
    ),
    Column("country", String(2), nullable=False),
    Column("amount", Numeric(12, 2), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

pipeline_runs = Table(
    "pipeline_runs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(200), nullable=False),
    Column("status", String(50), nullable=False),
)


def build_order_query(
    countries: Sequence[str] | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    min_amount: Decimal | None = None,
):
    conditions = []

    if countries:
        conditions.append(
            orders.c.country.in_(countries)
        )

    if start_date is not None:
        conditions.append(
            orders.c.created_at >= start_date
        )

    if end_date is not None:
        conditions.append(
            orders.c.created_at < end_date
        )

    if min_amount is not None:
        conditions.append(
            orders.c.amount >= min_amount
        )

    stmt = (
        select(
            orders.c.id,
            orders.c.customer_id,
            customers.c.name,
            orders.c.amount,
            orders.c.created_at,
        )
        .join(
            customers,
            customers.c.id == orders.c.customer_id,
        )
        .order_by(orders.c.created_at.desc())
    )

    if conditions:
        stmt = stmt.where(*conditions)

    return stmt


def upsert_customers(
    engine,
    rows: list[dict[str, object]],
) -> None:
    stmt = pg_insert(customers)

    stmt = stmt.on_conflict_do_update(
        index_elements=[customers.c.id],
        set_={
            "name": stmt.excluded.name,
            "country": stmt.excluded.country,
        },
    )

    with engine.begin() as conn:
        conn.execute(stmt, rows)
```

### Learner prediction

Before running each function, predict:

```text
tables referenced
join relationship
filters applied
transaction boundary
database-specific features
result shape
```

### Generated SQL

Compile important statements:

```python
compiled = stmt.compile(
    dialect=postgresql.dialect()
)

print(compiled)
print(compiled.params)
```

### Debugging sequence

```text
unexpected result
    ↓
inspect statement
    ↓
compile PostgreSQL SQL
    ↓
inspect params
    ↓
run small 3-row reproduction
    ↓
compare with handwritten SQL
    ↓
check database state
```

### Production lesson

The repository is not meant to hide SQL knowledge. It should give SQL a maintainable Python home.

## 58. Generated SQL Lab

### Step 1 — Define

```python
stmt = (
    select(
        customers.c.id,
        customers.c.name,
    )
    .where(customers.c.country == "IN")
)
```

### Step 2 — Print

```python
print(stmt)
```

### Step 3 — PostgreSQL compilation

```python
pg = stmt.compile(
    dialect=postgresql.dialect()
)

print(pg)
```

### Step 4 — Parameters

```python
print(pg.params)
```

### Step 5 — SQLite compilation

```python
sq = stmt.compile(
    dialect=sqlite.dialect()
)

print(sq)
print(sq.params)
```

### Step 6 — Debug representation

```python
debug_sql = stmt.compile(
    dialect=postgresql.dialect(),
    compile_kwargs={"literal_binds": True},
)

print(debug_sql)
```

### Step 7 — Normal execution

```python
with engine.connect() as conn:
    result = conn.execute(stmt)
```

Do not replace normal execution with a string generated by `literal_binds`.

### Questions

Answer:

1. What did SQLAlchemy represent as an expression object?
2. What values were bound?
3. What changed between PostgreSQL and SQLite?
4. Which differences are syntax only?
5. Which differences could indicate real capability/semantic differences?

## 59. Reflection Exercise

Perform all of these steps:

```python
inspector = inspect(engine)
```

1. List tables.
2. Inspect columns.
3. Inspect primary keys.
4. Inspect foreign keys.
5. Reflect the table.
6. Query through the reflected `Table`.

Example:

```python
tables = inspector.get_table_names()

for table_name in tables:
    print(table_name)

columns = inspector.get_columns("orders")

for column in columns:
    print(column)
```

Then:

```python
metadata = MetaData()

orders = Table(
    "orders",
    metadata,
    autoload_with=engine,
)
```

Query:

```python
stmt = select(
    orders.c.id
).limit(10)

with engine.connect() as conn:
    print(conn.execute(stmt).all())
```

### Reflection questions

Explain:

- What database information did SQLAlchemy need?
- Which pieces became Python objects?
- Which database features are still outside the reflected model?
- What permissions were required?

## 60. Database-Agnostic Query Exercise

Build this generic query:

```python
stmt = (
    select(
        customers.c.id,
        customers.c.name,
    )
    .where(customers.c.country == country)
)
```

Compile for:

```text
PostgreSQL
SQLite
```

Then execute against both where the schema and behavior permit.

### Record

```text
logical intent:
generated PostgreSQL SQL:
generated SQLite SQL:
parameter representation:
result:
differences:
```

Now add PostgreSQL-specific upsert behavior.

Write a short explanation:

```text
This repository function is PostgreSQL-specific because...
```

The exercise is successful only when you can explain why one expression is portable enough for the test while another deliberately is not.

## 61. Production Design Patterns

### Pattern A — Shared Engine

```text
Application process
        ↓
one Engine
        ↓
short-lived Connections
        ↓
database
```

### Pattern B — Repository Layer

```text
pipeline/service
        ↓
repository function
        ↓
SQLAlchemy Core
        ↓
Engine
        ↓
database
```

### Pattern C — Metadata-driven query builder

```text
validated configuration
        ↓
known Table/Column objects
        ↓
Core expressions
        ↓
compiled SQL
```

### Pattern D — PostgreSQL-specific operation

```text
generic repository
        ↓
explicit PostgreSQL boundary
        ↓
dialect-specific Core
```

### Pattern E — DataFrame boundary

```text
database
    ↓
SQLAlchemy Engine
    ↓
pandas / Polars
```

None of these is universally correct.

Choose based on the workload and the responsibility each layer should own.

## 62. Core vs ORM Preview

Topic 07 will introduce:

```text
ORM
 ↓
Python mapped objects
 ↓
Session
 ↓
identity map
 ↓
unit of work
```

This topic uses:

```text
Core
 ↓
Table
 ↓
Column
 ↓
Expression
 ↓
Connection
 ↓
Result
```

Do not teach ORM concepts here.

The distinction is enough:

```text
Core = SQL/database toolkit
ORM  = object-relational mapping layer
```

## 63. Core vs Alembic Preview

Runtime operations:

```text
Core
=
queries + writes + metadata + execution
```

Schema lifecycle:

```text
Alembic
=
migration management
```

Do not teach migration implementation here.

`metadata.create_all()` is suitable for controlled setup, not a substitute for migration history.

## 64. Core vs COPY Preview

General Core batch execution:

```python
conn.execute(
    insert(table),
    rows,
)
```

Database-native bulk movement:

```text
PostgreSQL COPY
```

Core provides a general SQL execution abstraction.

`COPY` is a specialized data-loading mechanism.

Topic 09 teaches the details.

## 65. Performance Thinking

Observed runtime can contain:

```text
Python code
+
SQLAlchemy expression construction
+
SQL compilation
+
driver work
+
network
+
database execution
+
result conversion
```

Therefore never assume:

```text
SQLAlchemy overhead
=
dominant cost
```

and never assume:

```text
SQLAlchemy overhead
=
irrelevant
```

Measure.

### Example measurement

```python
from time import perf_counter

start = perf_counter()

with engine.connect() as conn:
    rows = conn.execute(stmt).all()

elapsed = perf_counter() - start

print("seconds:", elapsed)
print("rows:", len(rows))
```

For more useful analysis, separate:

```text
statement construction
execution
result materialization
```

### Data volume matters

A query returning:

```text
10 rows
```

and the same query returning:

```text
10 million rows
```

have different performance risks.

This topic does not teach streaming large results, but you should already recognize when `.all()` is an inappropriate materialization strategy.

### Network matters

A fast database cannot eliminate a slow or distant network.

For repeated tiny queries:

```text
round-trip cost
```

may matter more than expression construction.

### Batch size matters

For inserts:

```text
too small
    ↓
many trips

too large
    ↓
large transactions / more memory / other limits
```

Measure before standardizing.

## 66. Debugging Exercises

Use:

```text
Observed symptom
      ↓
Root cause
      ↓
What SQLAlchemy is doing
      ↓
Database-side consequence
      ↓
Correct fix
      ↓
Production lesson
```

### Problem 1 — Engine created inside every function

**Observed**

Many functions independently call `create_engine()`.

**Root cause**

Engine lifecycle does not match process lifecycle.

**Fix**

Create a shared Engine and reuse it.

**Lesson**

```text
Engine = long-lived
Connection = short-lived
```

### Problem 2 — `text()` plus f-string

**Observed**

```python
text(f"SELECT ... {value}")
```

**Root cause**

Unsafe SQL construction happens before `text()`.

**Fix**

```python
text("SELECT ... :value")
```

plus bound parameters.

### Problem 3 — `connect()` instead of atomic `begin()`

**Observed**

A multi-step write has incorrect transaction scope.

**Fix**

```python
with engine.begin() as conn:
    ...
```

when the operations are one atomic unit.

### Problem 4 — Reflection fails

Check:

```text
schema
table
permissions
database
connection
identifier
```

### Problem 5 — Dynamic filters are strings

Replace:

```python
sql += ...
```

with expression objects.

### Problem 6 — PostgreSQL upsert fails on another backend

Root cause:

```text
dialect-specific feature
```

Fix:

```text
isolate PostgreSQL path
or
design/test an explicit backend-specific implementation
```

### Problem 7 — Generated SQL differs

Check:

```text
dialect
parameter style
quoting
expression compilation
```

### Problem 8 — Batch insert is slow

Investigate:

```text
batch size
transaction boundary
indexes
constraints
network
database time
driver behavior
```

Do not jump directly to "SQLAlchemy is slow."

### Problem 9 — Pool behavior seems different from Topic 05

Check which pool you are observing:

```text
SQLAlchemy Engine pool
vs
psycopg_pool.ConnectionPool
```

### Problem 10 — Reflected schema is not identical

Remember:

```text
metadata representation
≠
complete database behavior
```

Check indexes, triggers, permissions, extensions, policies, and vendor-specific objects.

## 67. Testing Strategy

Test the database boundary, not just Python helper functions.

### Engine connectivity

```python
def test_engine_connectivity(engine):
    with engine.connect() as conn:
        value = conn.execute(
            text("SELECT 1")
        ).scalar_one()

    assert value == 1
```

### Transaction commit

```python
def test_commit(engine, customers):
    with engine.begin() as conn:
        conn.execute(
            insert(customers).values(
                id=500,
                name="Alice",
                country="IN",
            )
        )

    with engine.connect() as conn:
        row = conn.execute(
            select(customers)
            .where(customers.c.id == 500)
        ).one()

    assert row.id == 500
```

### Transaction rollback

```python
import pytest

def test_rollback(engine, customers):
    with pytest.raises(RuntimeError):
        with engine.begin() as conn:
            conn.execute(
                insert(customers).values(
                    id=501,
                    name="Bob",
                    country="US",
                )
            )
            raise RuntimeError("intentional failure")

    with engine.connect() as conn:
        row = conn.execute(
            select(customers)
            .where(customers.c.id == 501)
        ).first()

    assert row is None
```

### Bound-parameter testing

Test values containing:

```text
quotes
unicode
empty strings
long strings
numbers at boundaries
dates
```

The goal is to verify that data remains data.

### Metadata testing

Assert:

```python
assert customers.c.id.primary_key
assert not customers.c.name.nullable
```

### Reflection testing

```python
def test_reflection(engine):
    metadata = MetaData()

    table = Table(
        "customers",
        metadata,
        autoload_with=engine,
    )

    assert "id" in table.c
```

### Dynamic-query testing

Cover:

```text
no filters
country only
date only
minimum amount only
all filters
empty list
unexpected values
```

### PostgreSQL upsert testing

Use a real PostgreSQL integration test for:

```text
insert
repeat same key
update incoming values
verify final state
```

Do not substitute a mock for the core database semantics.

### SQLite portability testing

Test generic constructs on SQLite.

Test PostgreSQL-specific constructs separately against PostgreSQL.

### Generated SQL testing

Prefer semantic assertions:

```python
compiled = stmt.compile(
    dialect=postgresql.dialect()
)

assert "SELECT" in str(compiled)
```

Avoid fragile whitespace-sensitive assertions unless the exact SQL text is the intentional contract.

### Pool testing

Test observable behavior rather than private pool implementation details.

## 68. Code Review Checklist

# SQLAlchemy Core Code Review Checklist

### Lifecycle

- Is the Engine created at the correct application/process boundary?
- Is the Engine reused?
- Are Connection contexts scoped?
- Is Connection ownership clear?

### Transactions

- Is `connect()` versus `begin()` intentional?
- Does transaction scope match business atomicity?
- Can an exception leave a partial unit of work?

### Security

- Are values bound?
- Is any SQL constructed with string interpolation?
- Are dynamic identifiers validated?
- Are secrets absent from logs and source?

### Metadata

- Is `MetaData` organized intentionally?
- Are `Table` and `Column` objects reused?
- Is reflection being used for a clear purpose?
- Is reflected metadata being mistaken for a full schema copy?

### Query correctness

- Are joins correct?
- Are predicates correct?
- Are destructive operations constrained?
- Do result methods match the expected cardinality?

### Performance

- Is batch size measured?
- Are round trips understood?
- Is `.all()` safe for the expected result size?
- Is database execution time distinguished from Python/SQLAlchemy overhead?

### Portability

- Are dialect-specific imports obvious?
- Are backend assumptions documented?
- Are supported backends tested?
- Is portability actually a requirement?

### Pooling

- Are `pool_size` and `max_overflow` understood?
- Is stale connection handling intentional?
- Is `NullPool` being used for an architectural reason?
- Is another pool already in front of this Engine?

### Observability

- Can important SQL be inspected?
- Is SQL logging safe?
- Can database-side behavior be observed separately?

### Scope

- Is Core solving a real problem?
- Is an ORM being introduced prematurely?
- Is migration logic being mixed into runtime query code?
- Is specialized bulk loading being reimplemented unnecessarily?

## 69. Production Hardening

# From Working SQLAlchemy Core Code to Production Core Code

### Level 1 — Raw `text()`

```python
stmt = text(
    "SELECT id FROM customers "
    "WHERE country = :country"
)
```

This is already safer than string interpolation.

### Level 2 — Bound parameters

```python
conn.execute(
    stmt,
    {"country": country},
)
```

### Level 3 — Shared Engine

```python
engine = create_engine(
    database_url,
    pool_pre_ping=True,
)
```

Create once at the intended process boundary.

### Level 4 — Explicit transaction boundary

```python
with engine.begin() as conn:
    ...
```

Use for atomic multi-statement work.

### Level 5 — Metadata

Use:

```text
MetaData
Table
Column
```

when structured schema objects add value.

### Level 6 — Expression-based dynamic SQL

Move from:

```text
SQL string construction
```

to:

```text
validated configuration
      ↓
SQLAlchemy expressions
```

### Level 7 — Explicit dialect-specific functionality

If PostgreSQL behavior is required:

```python
from sqlalchemy.dialects.postgresql import insert
```

Keep the vendor boundary visible.

### Level 8 — SQL inspection

For important statements:

```python
compiled = stmt.compile(
    dialect=postgresql.dialect()
)

print(compiled)
print(compiled.params)
```

### Level 9 — Real integration tests

Verify:

```text
PostgreSQL execution
transactions
reflection
upserts
dynamic queries
```

### Level 10 — Production operations

Add:

- environment/secret management,
- safe logging,
- bounded pools,
- connection health handling,
- timeouts where appropriate,
- database-side monitoring,
- performance measurement,
- clear exception handling,
- tested deployment configuration.

The abstraction does not replace operational engineering.

## 70. Interview Questions

Answer these by explaining the consequence, not just the definition.

### Basic

1. What is SQLAlchemy?
2. What is SQLAlchemy Core?
3. What is an Engine?
4. What is a Connection?
5. What is a Dialect?
6. What is a Driver?
7. What is a Pool?
8. What is `MetaData`?
9. What is a `Table`?
10. What is a `Column`?
11. Why is an Engine normally reused?

### Intermediate

12. What is the difference between `engine.connect()` and `engine.begin()`?
13. What does `text()` do?
14. What are bound parameters?
15. Why is `text(f"...")` still unsafe when the f-string contains untrusted data?
16. What does reflection mean?
17. What does `inspect(engine)` do?
18. What is the SQL Expression Language?
19. What is a SQLAlchemy `Result`?
20. When should `.one()` be used?
21. When should `.first()` be used?
22. What does `.mappings()` provide?
23. What does `.scalar()` return?
24. What is `insertmanyvalues` conceptually?
25. How does Engine pooling relate to driver-level pooling?

### Advanced

26. How does a Core expression become PostgreSQL-specific SQL?
27. What is the role of the dialect?
28. Why does SQLAlchemy not guarantee database portability?
29. How would you construct optional filters safely?
30. How would you validate configurable column names?
31. How would you implement a PostgreSQL upsert with Core?
32. How would you decide between raw psycopg and Core?
33. What is `literal_binds`?
34. Why should `literal_binds` not be your normal execution mechanism?
35. Why can generated SQL differ across dialects?
36. Why can reflection fail to reproduce complete database behavior?
37. How would you isolate PostgreSQL-specific code?
38. How would you test a portability claim?
39. How would you diagnose whether SQLAlchemy or PostgreSQL is the performance bottleneck?
40. When would `NullPool` be a sensible deliberate choice?

### Reasoning exercise

Explain this complete function:

```python
def find_customer(engine, customer_id: int):
    stmt = (
        select(customers)
        .where(customers.c.id == customer_id)
    )

    with engine.connect() as conn:
        return conn.execute(stmt).one_or_none()
```

Cover:

```text
Engine lifetime
Connection lifetime
SQL expression
bound value
dialect compilation
driver
database
result cardinality
connection release
```

## 71. Architecture Questions

Use this decision frame:

```text
workload
+
database features
+
portability requirements
+
operational constraints
+
team maintainability
+
performance measurements
```

### 1. Repository architecture

Design a repository layer for several pipelines.

Explain:

```text
Engine ownership
Connection scope
Transaction ownership
Metadata organization
Repository functions
Dialect-specific boundaries
Testing
```

### 2. Raw psycopg or Core?

Reason about:

- query complexity,
- composition,
- driver-specific requirements,
- portability,
- clarity,
- maintainability,
- measured performance.

Do not provide a universal winner.

### 3. Metadata-driven query builder

Allow configuration to select:

```text
columns
filters
date ranges
aggregations
```

without allowing arbitrary SQL.

A sound design:

```text
validate configuration
        ↓
allow-list identifiers
        ↓
Column objects
        ↓
expressions
        ↓
compiled SQL
```

### 4. PostgreSQL-specific operations

You need `ON CONFLICT`.

Explain where the vendor-specific code belongs.

Discuss:

```text
isolated function/module
explicit PostgreSQL tests
documented portability boundary
```

### 5. Transaction boundary

Suppose a repository has:

```python
create_run()
write_rows()
update_watermark()
```

Should each function create its own transaction?

Not automatically.

Decide which layer knows the business atomicity.

A higher layer may intentionally own:

```python
with engine.begin() as conn:
    create_run(conn)
    write_rows(conn)
    update_watermark(conn)
```

The repository methods can then operate on the same Connection.

### 6. Unexpected SQL

A query is logically correct in Python but slow.

Investigate:

```text
Core statement
      ↓
compiled SQL
      ↓
database query plan/timing
      ↓
index/selectivity
      ↓
network/driver overhead
      ↓
Python result construction
```

### 7. Portability

Prove support rather than assuming it.

```text
compile
+
execute
+
assert results
+
backend-specific integration tests
```

### 8. Reflection-based schema copy

Explain:

```text
inspect
→ reflect
→ to_metadata
→ create
→ verify
```

Then list the objects not guaranteed to be reproduced completely.

### 9. Multiple connection pools

Your application already uses a psycopg-level pool and now introduces SQLAlchemy.

Explain why two independent pools may multiply connection pressure and why pool ownership should be clear.

### 10. Is Core adding complexity?

Give an example where raw psycopg is clearer and an example where Core's expression model significantly reduces complexity.

The senior-level answer is not "always use Core." It is:

> Use the abstraction deliberately and be able to explain why.

## 72. Checkpoints

### Roadmap checkpoint

You must be able to:

```text
[ ] Explain Engine, Connection, and Dialect
[ ] Explain connect() vs begin()
[ ] Build parameterized dynamic queries
[ ] Reflect an existing schema
[ ] Write a PostgreSQL upsert
```

### Implementation checkpoint

Demonstrate:

```text
[ ] create_engine()
[ ] Engine reuse
[ ] text()
[ ] bound parameters
[ ] Result methods
[ ] MetaData
[ ] Table
[ ] Column
[ ] metadata.create_all()
[ ] inspect(engine)
[ ] Table(..., autoload_with=engine)
[ ] select()
[ ] where()
[ ] join()
[ ] group_by()
[ ] func.*
[ ] insert()
[ ] update()
[ ] delete()
[ ] batch execution
[ ] insertmanyvalues concept
[ ] pool_size
[ ] max_overflow
[ ] pool_pre_ping
[ ] pool_recycle
[ ] NullPool
[ ] PostgreSQL on_conflict_do_update()
[ ] PostgreSQL compilation
[ ] SQLite compilation
[ ] dynamic filters
[ ] safe dynamic columns
[ ] pandas integration
[ ] Polars integration
```

### Explanation checkpoint

Without notes, explain:

```text
Application
    ↓
Core
    ↓
Engine
    ↓
Dialect
    ↓
Driver
    ↓
Database
```

and:

```text
MetaData
    ↓
Table
    ↓
Column
    ↓
Expression
    ↓
Compilation
    ↓
Execution
    ↓
Result
```

### Production checkpoint

Explain in your own words:

1. Why the Engine is normally reused.
2. Why dynamic SQL should use expressions rather than string construction.
3. Why reflection is not full schema replication.
4. Why PostgreSQL-specific features create vendor coupling.
5. Why performance must be measured rather than assumed.

## 73. Common Mistakes

### Mistake 1 — Creating an Engine per query

**Beginner belief**

> "I need a connection, so I call `create_engine()` here."

**Reality**

The Engine is a reusable connectivity boundary.

**Consequence**

Unnecessary resource setup and ineffective lifecycle/pooling.

**Mental model**

```text
one Engine
many Connection contexts
```

### Mistake 2 — Using `text()` with f-strings

**Beginner belief**

> "`text()` makes the string safe."

**Reality**

Unsafe string construction already happened.

**Mental model**

```python
text("... :value")
```

plus:

```python
{"value": value}
```

### Mistake 3 — Assuming generated SQL is portable

**Reality**

Dialects and databases differ.

**Mental model**

```text
Core improves portability
but portability must be tested.
```

### Mistake 4 — Confusing Engine and Connection

Engine is the reusable entry point.

Connection is the active database interaction context.

### Mistake 5 — Confusing Dialect and Driver

`postgresql` is the database dialect.

`psycopg` is the driver.

### Mistake 6 — Using the wrong transaction context

If several statements are one atomic operation, make the transaction boundary explicit.

### Mistake 7 — Treating MetaData as the actual database schema

Python metadata can become stale.

### Mistake 8 — Assuming reflection sees every database feature

Reflection discovers metadata through supported inspection mechanisms; it is not a backup system.

### Mistake 9 — Hiding PostgreSQL dependencies

A PostgreSQL-specific import is useful information. Do not disguise it.

### Mistake 10 — Using `literal_binds` as normal execution

It is a debugging representation.

### Mistake 11 — Building dynamic filters as strings

Use expression objects.

### Mistake 12 — Allowing arbitrary dynamic columns

Use a validated allow-list.

### Mistake 13 — Treating batch execution as COPY

They solve different workload problems.

### Mistake 14 — Assuming pandas/Polars integration is automatically efficient at huge volume

Measure the real path.

### Mistake 15 — Over-abstracting

Sometimes the raw driver is clearer.

## 74. Final Mental Model

# The SQLAlchemy Core Mental Model

```text
Engine
=
database connectivity + dialect + pool configuration

Connection
=
active database interaction context

Dialect
=
database-specific SQL and behavior knowledge

Driver
=
concrete Python database implementation

Pool
=
manager of reusable physical connections

MetaData
=
Python representation of schema objects

Table / Column
=
composable schema objects

Expression
=
Python representation of SQL logic

Compilation
=
expression → database-specific SQL

Result
=
SQLAlchemy representation of returned database data
```

Full flow:

```text
Application
      ↓
SQLAlchemy Core
      ↓
Engine
      ↓
Connection
      ↓
Expression
      ↓
Dialect compilation
      ↓
Driver
      ↓
Database
      ↓
Driver result
      ↓
SQLAlchemy Result
      ↓
Application
```

Metadata flow:

```text
MetaData
   ├── Table
   │    ├── Column
   │    ├── Column
   │    └── ...
   ├── Table
   └── Table
```

The key statement:

```text
Core does not replace SQL.

Core helps you build, compose, execute,
inspect, and reuse SQL in Python.
```

## 75. Final Review

### What You Now Understand

You should understand:

- Engine
- Connection
- Dialect
- Driver
- Pool integration
- `connect()` versus `begin()`
- `text()` and bound parameters
- Result objects and common access methods
- `MetaData`
- `Table`
- `Column`
- SQLAlchemy types
- `metadata.create_all()`
- reflection
- `inspect(engine)`
- SQL Expression Language
- `select()`
- `where()`
- joins
- groupings
- `func.*`
- INSERT
- UPDATE
- DELETE
- batch execution
- `insertmanyvalues`
- PostgreSQL upserts
- generated SQL
- `literal_binds`
- PostgreSQL vs SQLite compilation
- pandas/Polars integration
- portability boundaries
- performance measurement
- testing
- repository design
- production hardening

### What You Can Implement

You should now be able to:

```text
build an Engine
      ↓
reuse it
      ↓
open Connection contexts
      ↓
use explicit transaction scopes
      ↓
execute bound SQL
      ↓
define metadata
      ↓
reflect existing schemas
      ↓
compose dynamic SQL
      ↓
execute batches
      ↓
perform PostgreSQL upserts
      ↓
inspect generated SQL
      ↓
integrate DataFrame tools
```

### What You Can Debug

You should be able to diagnose:

```text
Engine lifecycle mistakes
unsafe SQL construction
wrong transaction scope
reflection failures
dynamic query bugs
dialect incompatibility
unexpected generated SQL
batch performance problems
pooling confusion
incomplete metadata replication
```

### What Comes Next

Topic 07 introduces SQLAlchemy ORM and explains when object-relational mapping helps and when it is inappropriate for Data Engineering workloads.

Do not re-teach ORM here.

The next topic adds a different abstraction:

```text
ORM
   ↓
Python mapped objects
   ↓
Session
   ↓
Unit of Work
   ↓
Identity Map
```

You should enter Topic 07 with the Core model already stable.

## 76. Production Rules to Remember

1. Reuse the Engine; do not create one per query.
2. Treat Engine, Connection, Dialect, Driver, and Pool as different concepts.
3. Use `connect()` and `begin()` deliberately.
4. Parameterize values.
5. Use expressions instead of string-building dynamic SQL.
6. Treat dynamic identifiers as a validation/design problem.
7. Use `MetaData`, `Table`, and `Column` deliberately.
8. Reflection is useful but is not complete schema replication.
9. Inspect generated SQL when correctness or performance matters.
10. `literal_binds` is for debugging, not normal execution.
11. PostgreSQL-specific features create vendor coupling.
12. SQLAlchemy improves portability but does not guarantee it.
13. Core batch execution is not the same as database-native bulk loading.
14. Measure abstraction overhead when performance matters.
15. Choose the abstraction level based on workload and requirements.
16. Keep transaction ownership explicit.
17. Test important database behavior against the actual database.
18. Do not mistake API convenience for database correctness.
19. Make vendor-specific boundaries visible.
20. Know what the abstraction is hiding.

## Quick Self-Test

Without looking back, answer these from memory.

### A. Explain the stack

```text
Application
    ↓
Core
    ↓
Engine
    ↓
Dialect
    ↓
Driver
    ↓
Database
```

For each layer, state its responsibility.

### B. Explain the transaction choice

```text
engine.connect()
```

versus:

```text
engine.begin()
```

Give one example where each is intentional.

### C. Explain dynamic query construction

```text
configuration
    ↓
validation
    ↓
Column / expression objects
    ↓
Core statement
    ↓
dialect compilation
    ↓
bound execution
```

Explain why this is safer than assembling strings.

### D. Explain portability

Give one:

```text
generic Core construct
```

and one:

```text
PostgreSQL-specific construct
```

Then explain what engineering consequence follows.

### E. Explain reflection

Answer:

> What does reflection give me, and what does it not guarantee?

### F. Explain Engine pooling

Answer:

> Where does the physical database connection live in the architecture, and what happens when a SQLAlchemy Connection context ends?

If you can explain these flows and implement the labs, you have moved beyond memorizing SQLAlchemy API names and into database-boundary reasoning.

## Documentation Alignment

This module uses SQLAlchemy 2.x-style Core APIs and psycopg 3 for PostgreSQL examples. Exact behavior can vary with the installed SQLAlchemy, driver, PostgreSQL, pandas, and Polars versions, so verify version-sensitive details against the documentation and versions pinned by your project.
