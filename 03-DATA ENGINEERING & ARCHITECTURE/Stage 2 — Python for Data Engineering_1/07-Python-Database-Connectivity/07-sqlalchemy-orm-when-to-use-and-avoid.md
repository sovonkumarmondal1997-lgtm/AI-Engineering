# SQLAlchemy ORM: When to Use and Avoid

> **Central principle:** ORM is a useful abstraction when object-level behavior reduces complexity. For data-movement and set-based workloads, measure the cost before accepting object-relational overhead.

## Learning Objectives

By the end of this module, you should be able to:

- Explain what an ORM is and why object-relational mapping exists.
- Explain the difference between the relational model and the Python object model.
- Build SQLAlchemy 2.x ORM models using `DeclarativeBase`, `Mapped[...]`, and `mapped_column()`.
- Explain the roles of the `Engine`, `Session`, and ORM mapping.
- Create and scope Sessions deliberately using `Session` and `sessionmaker`.
- Explain what `session.add()`, `flush()`, `commit()`, and `rollback()` each do.
- Explain the Unit of Work pattern and how a Session coordinates changes.
- Explain the Identity Map and its benefits and costs.
- Recognize transient, pending, persistent, deleted, and detached object states.
- Model one-to-many relationships and understand relationship loading.
- Explain lazy loading and recognize the N+1 query problem.
- Detect N+1 behavior through SQL logging, query counts, and code inspection.
- Use `selectinload()` and `joinedload()` deliberately based on relationship shape.
- Explain Session lifetime, `expire_on_commit`, and detached objects.
- Identify Data Engineering workloads where ORM can reduce complexity.
- Identify bulk, extract, and set-based workloads where object materialization may add unnecessary cost.
- Use SQLAlchemy 2.x ORM bulk execution and understand its limits.
- Combine ORM and Core intentionally in one architecture.
- Keep persistence models separate from external validation/serialization models.
- Design a fair benchmark comparing ORM object insertion, ORM bulk execution, Core, and later database-native bulk loading.
- Write an evidence-based team ORM usage policy.
- Defend an ORM decision in code review, production planning, architecture discussions, and interviews.

### The decision skill this module teaches

You are not learning a slogan such as “always use ORM” or “never use ORM.” You are learning a decision process:

```text
Workload
   ↓
Data volume
   ↓
Access pattern
   ↓
Relationship complexity
   ↓
Transaction scope
   ↓
Object-level behavior required?
   ↓
Set-based/data-movement workload?
   ↓
What abstraction reduces complexity?
   ↓
What overhead does it introduce?
   ↓
What do measurements show?
   ↓
What should the team standardize?
```

## Prerequisites

This topic assumes you have already completed Topics 01–06:

- DB-API (PEP 249)
- PostgreSQL with psycopg 3
- parameterized queries and SQL injection prevention
- transactions
- connection pooling
- SQLAlchemy Core: Engine, Connection, MetaData, Table, Column, expressions, reflection, generated SQL, and portability

Do not re-learn those topics here. Use them as foundations.

> Topic 06 taught SQLAlchemy Core, where Python works directly with SQL expressions and table metadata. Topic 07 introduces a different abstraction: mapping database rows and relationships to Python objects.

---

# Why ORM Exists

Start with a practical question:

> Why would a Python program want a database row to behave like a Python object?

A relational database naturally gives you:

```text
customers
+----+-------+---------+
| id | name  | country |
+----+-------+---------+
|  1 | Alice | India   |
|  2 | Bob   | Japan   |
+----+-------+---------+
```

A Python application often wants to work with:

```python
customer.name
customer.country
customer.orders
```

Without an ORM, application code often has to repeatedly perform some combination of:

```text
SQL
  ↓
rows/tuples/mappings
  ↓
manual conversion
  ↓
Python objects
```

An ORM automates much of this mapping.

The important word is **mapping**.

An ORM does not replace the relational database. It creates a layer that maps relational structures to an object-oriented representation.

## What problem does ORM solve?

For an object-oriented application or tool, ORM can reduce repetitive work around:

- mapping columns to attributes
- constructing and tracking related objects
- coordinating changes across related objects
- maintaining object identity within a unit of work
- translating object changes into SQL statements
- loading relationships according to declared strategies

The value is therefore not “less SQL” by itself.

The value is that a consistent object-level abstraction can reduce application complexity for certain workloads.

## What ORM does not remove

```text
ORM does not remove SQL.
ORM does not remove PostgreSQL.
ORM does not remove transactions.
ORM does not remove indexes.
ORM does not remove query planning.
ORM does not remove network round trips.
ORM does not remove database constraints.
```

This matters because the database still executes SQL and remains responsible for relational integrity and set processing.

---

# 1. Relational Model vs Object Model

## Relational world

The database works with concepts such as:

- tables
- rows
- columns
- primary keys
- foreign keys
- joins
- sets
- SQL statements

Example:

```text
Customer table

id | name  | country
---+-------+--------
1  | Alice | India
```

## Object world

Python applications work with:

- classes
- objects
- attributes
- references
- object identity
- methods

Example:

```python
class Customer:
    name: str
    country: str
```

The ORM maps these two worlds:

```text
Database

Table → Row → Column
  ↓      ↓      ↓
       mapping
  ↓      ↓      ↓
Class → Object → Attribute

Python
```

## Why relationships need machinery

A database relationship may look like:

```text
customers.id
      ↑
      |
orders.customer_id
```

An application may want:

```python
customer.orders
```

The ORM has to know that `customer.orders` corresponds to a database relationship and decide when and how to load those rows.

That is why ORM is more than a row-to-object converter. It includes mapping configuration and runtime state management.

---

# 2. SQLAlchemy 2.0 ORM Style

SQLAlchemy 2.x uses modern Python typing-aware ORM APIs.

The basic mapping starts with `DeclarativeBase`.

```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

Then mapped classes can inherit from `Base`.

```python
from sqlalchemy.orm import Mapped, mapped_column


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    country: Mapped[str]
```

This is the primary style used throughout this module.

## Why the 2.x style matters

The model declaration communicates several things together:

```text
Python class
   +
Python type annotations
   +
SQLAlchemy mapping instructions
   ↓
ORM mapping
```

The Python type annotation is useful to the Python type system and to SQLAlchemy's mapping configuration, but it is not a complete description of every database behavior. Constraints, indexes, server-side defaults, permissions, triggers, extensions, and database-specific features still exist at the database layer.

> **Production rule:** Treat ORM model declarations as one representation of persistence structure, not as proof that the Python class contains the complete database schema contract.

---

# 3. `DeclarativeBase`

## What is `DeclarativeBase`?

`DeclarativeBase` is the base class used to build a declarative ORM model hierarchy.

```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

When `Customer(Base)` is declared, SQLAlchemy can register the class as an ORM mapping.

## Why it exists

It gives your mapped classes a common declarative foundation.

Conceptually:

```text
Base
 ├── Customer
 ├── Order
 ├── Pipeline
 ├── PipelineRun
 └── Watermark
```

## What it does not mean

`Base` is not a database connection.

`Base` is not a database.

`Base` does not automatically create tables merely because Python classes exist.

Table creation is a separate operation and should be treated separately from production schema migration management.

---

# 4. `Mapped[...]` and `mapped_column()`

## `Mapped[...]`

`Mapped[...]` declares an ORM-mapped attribute.

```python
id: Mapped[int]
name: Mapped[str]
```

The generic parameter describes the expected Python-side value type.

For an optional value:

```python
from typing import Optional

notes: Mapped[Optional[str]]
```

Modern Python can also use the union form:

```python
notes: Mapped[str | None]
```

## `mapped_column()`

`mapped_column()` provides column-level configuration.

```python
id: Mapped[int] = mapped_column(primary_key=True)
```

Common configuration includes:

- primary key behavior
- explicit SQLAlchemy type information
- nullability expectations
- defaults and server defaults
- foreign-key configuration
- indexing/uniqueness where appropriate

Example:

```python
email: Mapped[str] = mapped_column(unique=True, index=True)
```

Use explicit types when the inferred type is not sufficient or when the database representation requires a deliberate choice.

## Database type vs Python type

Keep the mental model:

```text
Python type annotation
        ↓
SQLAlchemy mapping configuration
        ↓
SQL column type
        ↓
PostgreSQL type
```

The mapping is a bridge, not a claim that the two type systems are identical.

---

# 5. Modeling Pipeline Metadata

This module uses pipeline metadata as a reference workload because it illustrates a common Data Engineering scenario where ORM can be useful.

Typical metadata tables include:

```text
Pipeline
PipelineRun
Watermark
```

These records are usually small compared with fact/event datasets.

Operations might be:

```text
start_run()
finish_run()
get_watermark()
set_watermark()
```

This is an object-oriented control workload:

```text
small records
   ↓
transactional operations
   ↓
object relationships
   ↓
ORM can reduce application mapping code
```

A representative model set:

```python
from __future__ import annotations

from datetime import datetime
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Pipeline(Base):
    __tablename__ = "pipelines"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    config_json: Mapped[str] = mapped_column(Text)

    runs: Mapped[list["PipelineRun"]] = relationship(
        back_populates="pipeline",
        cascade="all, delete-orphan",
    )


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    pipeline_id: Mapped[int] = mapped_column(ForeignKey("pipelines.id"))
    status: Mapped[str] = mapped_column(String(30))
    started_at: Mapped[datetime]
    finished_at: Mapped[datetime | None]
    rows_in: Mapped[int] = mapped_column(default=0)
    rows_out: Mapped[int] = mapped_column(default=0)
    error_message: Mapped[str | None] = mapped_column(Text)

    pipeline: Mapped[Pipeline] = relationship(back_populates="runs")
```

The exact model shape should be driven by your real metadata contract. This example exists to teach the ORM mechanics.

---

# 6. Engine and Session

Topic 06 established the Engine.

The ORM adds a Session above it.

```text
Application
    ↓
Session
    ↓
Engine
    ↓
Connection / pool
    ↓
Dialect / driver
    ↓
PostgreSQL
```

The important distinction is:

```text
Engine
= connectivity and database-engine configuration

Session
= ORM work coordination and object state management

Connection
= active database interaction context

Transaction
= database unit of atomic work

ORM object
= Python representation of a mapped database entity
```

## A Session is not a connection

A Session may obtain and release database connections as needed. It coordinates work; it is not simply a permanently checked-out PostgreSQL connection.

## A Session is not identical to a transaction

A Session can manage transaction state, but the concepts are different.

Use this mental model:

```text
Session
  ↓
coordinates ORM work
  ↓
uses connections when database access is required
  ↓
participates in transactions
```

This distinction is essential when reasoning about concurrency, pooling, errors, and lifecycle.

---

# 7. `Session`

The simplest explicit Session pattern is:

```python
from sqlalchemy.orm import Session


with Session(engine) as session:
    customer = session.get(Customer, 1)
    print(customer)
```

The context manager gives the Session a deliberate lifecycle.

Conceptually:

```text
create Session
     ↓
perform ORM work
     ↓
commit or rollback as required
     ↓
close Session
```

## Why use a deliberate scope?

A bounded Session makes it easier to reason about:

- object state
- transaction boundaries
- failure isolation
- relationship loading
- identity-map size
- connection usage

A Session that remains alive across unrelated workloads makes all of these harder to understand.

---

# 8. `sessionmaker`

`sessionmaker` is a factory for creating Sessions with consistent configuration.

```python
from sqlalchemy.orm import sessionmaker


SessionFactory = sessionmaker(bind=engine)
```

Then:

```python
with SessionFactory() as session:
    customer = session.get(Customer, 1)
```

The factory does not mean “one Session for the whole application.”

It means:

```text
one configured factory
        ↓
many deliberately scoped Session instances
```

This separation is useful because session configuration is centralized while session lifetime remains bounded.

## Common mistake

```python
GLOBAL_SESSION = SessionFactory()
```

Do not turn `sessionmaker` into a reason to share one Session across unrelated operations.

> **Production lesson:** A Session factory is reusable configuration. A Session instance is runtime state.

---

# 9. Querying

SQLAlchemy 2.x ORM querying uses Core-style statements executed through the Session.

```python
from sqlalchemy import select


stmt = select(Customer)

with SessionFactory() as session:
    customers = session.scalars(stmt).all()
```

This is a major architectural connection between Topics 06 and 07:

```text
Topic 06
Core expression
    ↓
Topic 07
ORM entity result
```

A filter:

```python
stmt = select(Customer).where(Customer.country == "India")
```

Execution:

```python
with SessionFactory() as session:
    customers = session.scalars(stmt).all()
```

The database still receives SQL.

The ORM adds mapping and object management around the result.

## `session.get()`

For primary-key lookup:

```python
with SessionFactory() as session:
    customer = session.get(Customer, 1)
```

`Session.get()` has special identity-map semantics: SQLAlchemy can consult the Session's current identity state before issuing a new database query.

This is one reason Identity Map matters.

---

# 10. Adding Objects

Create a Python object:

```python
customer = Customer(
    name="Alice",
    country="India",
)
```

Then add it to the Session:

```python
session.add(customer)
```

The critical distinction is:

```text
Customer(...)
    ↓
Python object exists

session.add(customer)
    ↓
object becomes tracked by Session

flush
    ↓
INSERT can be emitted

commit
    ↓
transaction completes
```

`session.add()` is therefore not the same thing as “INSERT has already been sent to PostgreSQL.”

---

# 11. Flush

`flush()` synchronizes pending ORM changes with the database within the current transaction.

```python
customer = Customer(name="Alice", country="India")
session.add(customer)
session.flush()
```

After a successful flush, database-side effects such as an INSERT have been issued, but the surrounding transaction may still be active.

## Why flush exists

Suppose you create one object and then need database-generated state before creating another object.

A flush can make the first object's database identity available to subsequent work without committing the whole transaction.

Conceptually:

```text
add()
  ↓
pending state
  ↓
flush()
  ↓
SQL sent to database
  ↓
transaction still active
```

## Flush vs commit

| Operation | Meaning |
|---|---|
| `session.add()` | Track an object in the Session |
| `session.flush()` | Synchronize pending ORM changes with the database |
| `session.commit()` | Flush pending changes, then commit the transaction |
| `session.rollback()` | Roll back the current transaction and reset appropriate Session state |

> **Production rule:** Never use “flush” and “commit” as synonyms.

---

# 12. Commit

```python
session.commit()
```

For ORM work, `commit()` is a transaction boundary. SQLAlchemy flushes pending changes before committing.

Example:

```python
with SessionFactory() as session:
    customer = Customer(name="Alice", country="India")
    session.add(customer)
    session.commit()
```

A simplified mental model is:

```text
pending changes
      ↓
flush
      ↓
transaction commit
      ↓
changes become committed database state
```

Do not treat commit as a Python-object operation only. It is a database transaction operation with Session-state consequences.

---

# 13. Rollback

When a database operation fails, the transaction may need to be rolled back before the Session can continue meaningful transactional work.

```python
with SessionFactory() as session:
    try:
        customer = Customer(name="Alice", country="India")
        session.add(customer)
        session.commit()
    except Exception:
        session.rollback()
        raise
```

For a context-managed transaction, an explicit `session.begin()` block can make transaction intent clearer:

```python
with SessionFactory() as session:
    with session.begin():
        session.add(Customer(name="Alice", country="India"))
```

Successful exit commits; an exception causes rollback.

The exact failure handling belongs to transaction engineering from Topic 04. Here, focus on how ORM Session state interacts with that transaction lifecycle.

---

# 14. Unit of Work

## The problem

Imagine changing multiple related objects:

```python
customer.name = "Alice Updated"
order.amount = 250
new_order = Order(...)
session.add(new_order)
```

You want those changes treated as one logical unit of work.

The Unit of Work pattern is the Session's ability to keep track of object changes and coordinate their synchronization with the database.

Conceptually:

```text
Python object changes
        ↓
Session tracks state
        ↓
Unit of Work determines required SQL
        ↓
flush
        ↓
SQL statements
        ↓
transaction
        ↓
commit
```

## What the Unit of Work gives you

It helps coordinate changes such as:

- new objects
- modified objects
- deleted objects
- relationships between objects

The ORM can determine an appropriate sequence of SQL operations based on mapped state and relationships.

It does not mean one object always equals one SQL statement. SQLAlchemy has batching and statement-generation behavior that can combine or optimize operations depending on the mappings, dialect, and execution path.

## Why this can be valuable

For small operational workflows, the ability to express:

```python
pipeline.status = "running"
run.status = "started"
session.add(run)
session.commit()
```

can be much easier to maintain than manually synchronizing every individual SQL statement and mapping every returned row.

> **Production lesson:** Unit of Work is valuable when coordinating object-level changes is part of the problem. It is less valuable when the problem is simply moving or transforming very large sets of rows.

---

# 15. Identity Map

## Definition

Within the scope of a Session, SQLAlchemy maintains an identity map: a given database identity is represented by one current ORM object instance within that Session.

Consider:

```python
with SessionFactory() as session:
    a = session.get(Customer, 1)
    b = session.get(Customer, 1)

    assert a is b
```

The same primary-key identity is normally associated with the same Python object within that Session.

## Why identity matters

Without identity tracking, one Session could accidentally hold multiple Python objects that claim to represent the same database row but contain conflicting in-memory state.

The identity map helps maintain a coherent object view within a unit of work.

## Identity Map benefits

- consistency of object identity inside the Session
- useful coordination of relationships
- change tracking against one object instance
- efficient primary-key identity lookup in appropriate cases

## Identity Map costs

Identity tracking is not free.

The Session may need to maintain references and object state for entities it has loaded or created.

For a small control table this may be negligible.

For a huge extraction that materializes millions of ORM entities, the object and bookkeeping overhead becomes an engineering concern.

This is one of the key reasons to measure ORM behavior instead of making ideological performance claims.

---

# 16. Session Object States

An ORM object moves through states during its lifetime.

## Transient

A newly created Python object that is not yet associated with a Session.

```python
customer = Customer(name="Alice", country="India")
```

Conceptually:

```text
Python object
   ↓
transient
```

## Pending

After:

```python
session.add(customer)
```

the object is associated with the Session and pending persistence.

```text
transient
   ↓ add()
pending
```

## Persistent

After the object participates in ORM persistence and is associated with an active Session, it is in the persistent state.

```text
pending
   ↓ flush
persistent
```

## Deleted

An existing object can be marked for deletion:

```python
session.delete(customer)
```

The deletion participates in the Unit of Work and current transaction.

## Detached

When the object is no longer associated with the Session, it can be detached.

A common path is:

```text
persistent
   ↓
Session closes
   ↓
detached
```

Detached objects can still hold already-loaded data, but they cannot freely perform operations that require an active Session.

---

# 17. Relationships

A relationship maps object navigation to a database relationship.

Example:

```python
class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    orders: Mapped[list["Order"]] = relationship(
        back_populates="customer"
    )


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id")
    )
    amount: Mapped[float]

    customer: Mapped[Customer] = relationship(
        back_populates="orders"
    )
```

The database relationship is:

```text
customers.id
      ↑
      |
orders.customer_id
```

The object relationship becomes:

```python
customer.orders
order.customer
```

## Why relationships are powerful

They let application code reason in domain terms.

Instead of manually writing a join for every object navigation operation, the mapping describes how entities relate.

But relationship navigation also introduces a major performance responsibility: **when does the related data get loaded?**

---

# 18. Relationship Loading

There are two broad ideas to understand first:

```text
Lazy loading
Eager loading
```

## Lazy loading

The related collection is loaded when the application accesses it.

Conceptually:

```python
pipeline = session.get(Pipeline, 1)

# Later...
runs = pipeline.runs
```

The attribute access may cause another SQL query if the relationship is not already loaded.

This is convenient, but convenience can hide database work.

## Eager loading

The application tells SQLAlchemy to load related data as part of the overall query strategy.

Two important strategies are:

- `selectinload()`
- `joinedload()`

Both are eager-loading strategies, but they shape database work differently.

> **Production lesson:** Relationship loading strategy is not merely an API preference. It is a database-performance decision.

---

# 19. Lazy Loading and the N+1 Query Problem

Consider:

```python
pipelines = session.scalars(
    select(Pipeline)
).all()

for pipeline in pipelines:
    print(pipeline.runs)
```

Suppose lazy loading is used for `Pipeline.runs`.

A possible pattern is:

```text
1 query → load pipelines
N queries → load each pipeline's runs
-------------------------------
1 + N queries
```

With 100 pipelines, that pattern could mean:

```text
1 + 100 = 101 queries
```

The exact number depends on the query and relationship configuration, but the architectural problem is real: code that looks like one Python loop can translate into many database round trips.

## Why N+1 is dangerous

Each round trip can involve:

- network latency
- connection usage
- SQL parsing/planning work
- database CPU
- result construction

A query that works well for 10 entities can become problematic at 10,000 entities.

## Key mental model

```text
Python loop
    ↓
attribute access
    ↓
possibly SQL
    ↓
possibly one round trip per parent
```

That is why ORM code requires database observation, not only Python-code inspection.

---

# 20. Detecting N+1

## Method 1: SQL logging

For a local learning environment, enable SQLAlchemy engine logging:

```python
from sqlalchemy import create_engine

engine = create_engine(
    database_url,
    echo=True,
)
```

Then inspect the statements generated while the loop runs.

Do not use verbose SQL logging blindly in production. Logging can create sensitive-data exposure, volume, and performance costs.

## Method 2: Count queries in a test

A test can attach an event listener and count SQL executions.

Representative example:

```python
from sqlalchemy import event
from sqlalchemy.engine import Engine


def count_selects(engine: Engine):
    statements: list[str] = []

    def after_execute(
        conn,
        cursor,
        statement,
        parameters,
        context,
        executemany,
    ) -> None:
        if statement.lstrip().upper().startswith("SELECT"):
            statements.append(statement)

    event.listen(engine, "after_cursor_execute", after_execute)
    return statements, after_execute
```

For a real test, remember to remove the listener after the assertion.

## Method 3: Code inspection

Look for patterns such as:

```python
for parent in parents:
    print(parent.children)
```

The key question is:

> Could this attribute access issue a query repeatedly?

## Method 4: Database-side observation

Use PostgreSQL activity monitoring and application logs to understand the actual workload.

> **Production rule:** The best N+1 diagnosis combines code inspection with observed SQL behavior.

---

# 21. `selectinload`

`selectinload()` is an eager-loading strategy that generally coordinates related loading using additional SELECT statements and primary-key based matching.

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload


stmt = (
    select(Pipeline)
    .options(selectinload(Pipeline.runs))
)

with SessionFactory() as session:
    pipelines = session.scalars(stmt).all()
```

Conceptually:

```text
query parents
      +
coordinated query for related rows
```

This can eliminate the pattern where every parent causes its own relationship SELECT.

It does not guarantee a fixed number of SQL statements for every possible relationship shape or query. The important lesson is that loading is coordinated rather than being left to repeated per-object lazy access.

## When to investigate `selectinload`

Consider it when:

- a collection relationship is needed for many parents
- individual lazy loads would create excessive round trips
- loading related rows separately is acceptable for the workload
- the related collection is large enough that joining it directly could create unnecessary row multiplication

These are workload considerations, not absolute rules.

---

# 22. `joinedload`

`joinedload()` eager-loads a relationship through a JOIN strategy.

Example for a many-to-one relationship:

```python
from sqlalchemy import select
from sqlalchemy.orm import joinedload


stmt = (
    select(Order)
    .options(joinedload(Order.customer))
)

with SessionFactory() as session:
    orders = session.scalars(stmt).all()
```

A critical point is that joined eager loading can multiply SQL rows when the relationship is a collection.

For example:

```text
1 customer
100 orders
```

A joined representation can contain 100 SQL rows carrying repeated customer columns.

## Collection example

```python
stmt = (
    select(Customer)
    .options(joinedload(Customer.orders))
)

with SessionFactory() as session:
    customers = session.scalars(stmt).unique().all()
```

When a collection is joined eagerly, SQLAlchemy requires `unique()` before materializing ORM entities from the result because the SQL result can contain duplicate parent identities across rows.

This is a critical practical detail.

---

# 23. `selectinload` vs `joinedload`

| Strategy | General idea | Important trade-off |
|---|---|---|
| Lazy loading | Load relationship when accessed | Convenient, but can create N+1 |
| `selectinload` | Additional coordinated SELECT(s) | Avoids per-parent relationship queries; still performs extra database work |
| `joinedload` | Load through a JOIN | Can increase SQL row multiplicity, especially for collections |

## For collection relationships

Suppose a pipeline has many runs.

```text
Pipeline
   ↓
100 runs
```

A joined query can repeat Pipeline columns on many SQL rows.

`selectinload` instead keeps parent and child retrieval as separate coordinated operations.

The right choice depends on:

- relationship cardinality
- expected parent count
- expected child count
- row width
- database execution plan
- network transfer
- result materialization cost

## For many-to-one relationships

Suppose every Order has one Customer.

A joined load may be attractive because the related entity is singular and the row multiplication effect is much smaller.

Again, inspect the actual query and workload.

> **Decision rule:** Choose a loading strategy based on relationship shape and measured query behavior, not on the name of the API.

---

# 24. Session Lifecycle

The Session lifecycle should be explicit.

```python
with SessionFactory() as session:
    ...
```

A deliberate unit of work commonly looks like:

```text
create Session
    ↓
load/change objects
    ↓
flush as needed
    ↓
commit on success
or
rollback on failure
    ↓
close Session
```

## Why long-lived Sessions are problematic

A very long-lived Session can accumulate:

- ORM objects
- identity-map state
- expired/persistent state transitions
- transaction context
- application-specific assumptions about freshness

It can also blur the meaning of “what operation is this Session representing?”

## What not to do

```python
# ⚠️ INTENTIONALLY PROBLEMATIC TRAINING EXAMPLE

global_session = SessionFactory()
```

Then:

```python
global_session.add(...)
global_session.execute(...)
# unrelated pipeline A
# unrelated pipeline B
# unrelated admin operation
```

This mixes unrelated state and makes failures difficult to isolate.

## Better mental model

```text
SessionFactory
     ↓
create a Session
     ↓
one deliberate unit of work
     ↓
close it
```

The exact boundary depends on the application architecture, but it should be deliberate rather than accidental.

---

# 25. One Session per Unit of Work

“One Session per unit of work” is an architectural principle, not a framework-specific dependency-injection recipe.

A unit of work might be:

- one pipeline metadata update
- one control-table transaction
- one internal administrative operation
- one application request
- one bounded batch of logically related changes

For example:

```python
def finish_run(
    session: Session,
    run: PipelineRun,
    rows_out: int,
) -> None:
    run.status = "success"
    run.rows_out = rows_out
    run.finished_at = datetime.now(timezone.utc)
    session.commit()
```

The broader architecture may create the Session and pass it into repository/service functions.

The key is that the Session lifetime is explicit.

> **Production lesson:** Session scope should match a meaningful unit of work, not the lifetime of the process by default.

---

# 26. `expire_on_commit`

SQLAlchemy Sessions normally expire ORM objects on commit so that subsequent attribute access can refresh state for a later transaction.

Conceptually:

```text
commit
  ↓
ORM state expires
  ↓
next relevant access may refresh from database
```

You can configure a Session factory:

```python
SessionFactory = sessionmaker(
    bind=engine,
    expire_on_commit=False,
)
```

## Why expiration exists

After a commit, the database is the source of truth. Other transactions may have changed data, triggers may have run, or server-side values may have changed.

Expiration helps prevent the application from treating an old in-memory view as permanently authoritative.

## When disabling expiration can be useful

Sometimes the application intentionally wants returned objects to remain directly usable after the transaction, especially in controlled metadata or API boundaries.

But disabling expiration everywhere can create stale-data surprises.

## Decision checklist

Ask:

- Will the object be used after commit?
- Is stale state acceptable?
- Will the object be detached shortly after commit?
- Are server-generated values important?
- Does another operation need to observe fresh database state?

Do not treat `expire_on_commit=False` as a universal improvement.

---

# 27. Detached Objects

A detached ORM object is no longer associated with an active Session.

Example:

```python
with SessionFactory() as session:
    customer = session.get(Customer, 1)

# Session has closed here.
```

The `customer` object may still contain data already loaded into memory.

But relationship access that requires a database query cannot proceed without a Session.

For example:

```python
# ⚠️ INTENTIONALLY PROBLEMATIC TRAINING EXAMPLE

with SessionFactory() as session:
    customer = session.get(Customer, 1)

print(customer.orders)
```

If `orders` was not already loaded, SQLAlchemy may need the Session to issue a SELECT. With no active Session, relationship loading can fail with a detached-instance error.

## Better approaches

Choose deliberately among:

1. Load what the boundary needs before closing the Session.
2. Keep the object inside the Session scope while relationship access is needed.
3. Return a purpose-built data structure at the boundary instead of leaking ORM objects.

Example:

```python
with SessionFactory() as session:
    stmt = (
        select(Customer)
        .options(selectinload(Customer.orders))
        .where(Customer.id == 1)
    )
    customer = session.scalars(stmt).one()

# Relationship is already loaded before Session closes.
print(customer.orders)
```

The exact data boundary should be designed intentionally.

---

# 28. Session Lifecycle Failure Cases

## Failure 1 — Using an object after Session close

**Observed behavior:** attribute access works for some fields but relationship access fails.

**Root cause:** some attributes were already loaded; other attributes required database access.

**ORM behavior:** the detached instance cannot perform the required lazy load.

**Database effect:** no query can be issued because there is no active Session connection context for the lazy load.

**Correct design:** load required data before detachment or convert the data into a boundary-specific structure.

**Production lesson:** “The object exists” does not mean “the object can still access the database.”

## Failure 2 — Lazy loading relationships inside loops

**Observed behavior:** application performs far more SELECTs than expected.

**Root cause:** each parent access can trigger another query.

**ORM behavior:** lazy loading is doing exactly what was configured.

**Database effect:** many round trips.

**Correct design:** select an eager-loading strategy appropriate for the relationship and access pattern.

**Production lesson:** convenient attribute access can hide I/O.

## Failure 3 — One Session for a huge batch

**Observed behavior:** memory grows as the batch runs.

**Root cause:** the Session may retain many objects and associated state.

**ORM behavior:** identity tracking and object lifecycle management accumulate state.

**Database effect:** the transaction may also remain open longer than intended.

**Correct design:** use bounded work units and consider a lower-level/set-based path for large operations.

**Production lesson:** object-oriented convenience has resource implications.

## Failure 4 — Reusing a Session across unrelated operations

**Observed behavior:** stale state, confusing transaction behavior, unexpected object identity.

**Root cause:** multiple logical workflows share one stateful Session.

**Correct design:** define clear Session boundaries.

**Production lesson:** runtime state should have a meaningful owner.

---

# 29. Where ORM Fits in Data Engineering

ORM can be useful when the workload is object-centric and relatively small.

## Pipeline metadata

Examples:

- Pipeline
- PipelineRun
- Watermark
- DataQualityResult
- JobConfiguration

These often have:

- modest row counts per operation
- rich relationships
- transactional updates
- lifecycle transitions
- clear object identity

Example:

```text
start pipeline
     ↓
create PipelineRun object
     ↓
update status
     ↓
attach metadata
     ↓
commit
```

The object model can make the application code straightforward.

## Internal admin tools

Suppose an internal tool manages:

```text
pipelines
owners
schedules
run policies
```

Users may work with individual entities and relationships rather than moving millions of rows.

In such a workload, ORM mapping may reduce repetitive translation code.

## Small operational APIs

An API that manages a modest number of operational entities can benefit from:

```text
HTTP request
   ↓
validated input
   ↓
ORM model
   ↓
transaction
   ↓
database
```

This can be a reasonable architecture when the domain object model is actually useful.

## Important qualification

None of these cases proves ORM must be used.

They merely make ORM worth evaluating because the abstraction aligns with the workload.

---

# 30. Where ORM Should Generally Be Avoided as the Default Abstraction

The key workloads to investigate carefully are:

- bulk loads
- large extracts
- set-based transformations
- high-volume staging operations

The reason is not that ORM is “bad.”

The reason is that ORM adds object-level work that may not contribute to the business requirement.

---

# 31. ORM for Bulk Loads — Why It Can Hurt

Consider:

```python
# ⚠️ INTENTIONALLY SLOW-AT-SCALE TRAINING SHAPE

for row in million_rows:
    session.add(
        Order(
            customer_id=row.customer_id,
            amount=row.amount,
        )
    )

session.commit()
```

This path asks Python and SQLAlchemy to handle each logical record as an ORM object.

Potential overhead includes:

- Python object allocation
- attribute instrumentation
- identity tracking
- Session bookkeeping
- relationship/cascade processing where configured
- flush management
- Python-level iteration
- database round trips or statement execution overhead

At small scale, these costs may be acceptable.

At very large scale, they can dominate the workload.

> **Important:** Do not claim a fixed slowdown factor without measurement. The size of the penalty depends on schema, SQLAlchemy version, driver, PostgreSQL version, indexes, transaction strategy, hardware, and implementation.

---

# 32. ORM for Large Extracts — Why It Can Hurt

Consider:

```python
orders = session.scalars(
    select(Order)
).all()
```

This asks the ORM to materialize database rows into Python ORM objects.

For millions of rows, you should explicitly investigate:

- object allocation
- identity-map state
- relationship state
- Python memory use
- CPU for materialization
- garbage collection pressure
- lifetime of the Session

The database may be capable of producing the rows efficiently, but turning every row into a rich Python object can add a large amount of work that an analytical pipeline does not need.

For an extraction workload, the requirement may actually be:

```text
Database rows
   ↓
tabular representation
   ↓
Parquet / DataFrame / another system
```

not:

```text
Database rows
   ↓
ORM object graph
   ↓
Python business logic
```

Large-result streaming is covered later in Topic 10. This topic only establishes why ORM object materialization must be treated as a workload decision.

---

# 33. ORM for Set-Based Transformations

Suppose the requirement is:

> Update all active orders from one status to another when they meet a condition.

A database-native set operation is conceptually:

```text
Database
   ↓
set-based UPDATE
   ↓
Database
```

The ORM-object alternative would be:

```text
Database rows
   ↓
ORM objects
   ↓
Python loop
   ↓
object changes
   ↓
flush
   ↓
database
```

The second path introduces Python work even though the business operation is naturally set-based.

The principle is:

```text
Use objects when object behavior is useful.
Use database sets when the operation is fundamentally a set operation.
```

SQLAlchemy's ORM can execute SQL expressions directly, so “using the ORM” does not require materializing every affected row as an object. This distinction becomes important in bulk operations.

---

# 34. ORM Bulk Operations

SQLAlchemy 2.x supports ORM-enabled DML through `Session.execute()`.

Example:

```python
from sqlalchemy import insert

rows = [
    {"name": "Alice", "country": "India"},
    {"name": "Bob", "country": "Japan"},
    {"name": "Carol", "country": "Germany"},
]

with SessionFactory() as session:
    session.execute(insert(Customer), rows)
    session.commit()
```

This is different from:

```python
for row in rows:
    session.add(Customer(**row))
```

The bulk form can avoid creating one ORM object per input row.

## Why this matters

You can still use an ORM-mapped class as the target while using a more SQL-oriented execution path.

This creates a useful middle layer:

```text
ORM mapping
    ↓
SQL-oriented bulk execution
    ↓
database
```

## What it does not solve

Bulk ORM execution does not magically provide all object-oriented behavior.

Depending on the operation, you may not get the same behavior as creating and tracking ordinary ORM objects, including differences around:

- in-memory object identity
- object lifecycle callbacks/expectations
- relationship population
- per-instance state tracking
- how Session state is synchronized with the database

The exact semantics depend on the DML operation and execution mode.

> **Production rule:** Choose bulk ORM execution when you explicitly want SQL-oriented row operations while retaining ORM mapping context. Do not assume it is behaviorally identical to `session.add()` on ORM objects.

## Modern vs legacy bulk APIs

SQLAlchemy 2.x documentation marks older methods such as `bulk_insert_mappings()` as legacy and directs new code toward modern ORM-enabled DML patterns.

Primary teaching in this module therefore uses:

```python
session.execute(insert(Customer), rows)
```

rather than legacy bulk helper methods.

---

# 35. ORM Object Insert vs ORM Bulk vs Core vs COPY

This comparison is about abstraction and workload, not ranking.

| Technique | Main abstraction | What it gives you | Typical reason to investigate it |
|---|---|---|---|
| ORM objects | Python object lifecycle | identity, relationships, Unit of Work, object state | object-centric operational workflows |
| ORM bulk execution | SQL-oriented DML through ORM | mapping context without one object per row | larger batches when object materialization is unnecessary |
| Core | SQL/database toolkit | composable SQL and direct statement control | set-based operations, dynamic SQL, data-access layers |
| PostgreSQL `COPY` | database-native bulk movement | specialized high-throughput loading path | very large ingestion workloads |

`COPY` is a later-topic boundary in this curriculum. Do not treat this section as a COPY implementation lesson.

The architectural question is:

> Which abstraction solves the real problem with acceptable cost and complexity?

---

# 36. Identity Map and Large Data

The Identity Map is a useful object-management mechanism when object identity matters.

Imagine loading:

```text
1,000,000 database rows
        ↓
1,000,000 ORM objects
```

The application may now have a large amount of Python state to manage.

A useful conceptual model is:

```text
Rows
 ↓
ORM object allocation
 ↓
attribute instrumentation
 ↓
identity tracking
 ↓
Session state
 ↓
memory and CPU
```

For a metadata system with a few hundred rows, the same machinery may be exactly what simplifies the application.

For a 1-million-row analytical extract, much of that machinery may be incidental to the requirement.

This is the central workload-fit lesson.

---

# 37. Mixing ORM and Core

ORM and Core are not mutually exclusive.

A mature codebase can deliberately use both.

```text
Application
   ├── ORM → metadata/domain operations
   │
   └── Core → set-based/batch/database operations
             ↓
          same Engine
```

Example:

```text
ORM
 ├── Pipeline
 ├── PipelineRun
 └── Watermark

Core
 ├── analytical aggregation
 ├── batch staging DML
 └── dynamic extraction SQL
```

This is often more expressive than forcing every database operation through one abstraction.

## Why mixing can be healthy

ORM and Core solve different problems:

```text
ORM
= object-level modeling and lifecycle

Core
= SQL/data-access composition
```

A pipeline control plane might benefit from ORM while its data plane uses Core and database-native bulk tools.

---

# 38. Shared `MetaData`

SQLAlchemy ORM mappings and Core table structures participate in the same broader SQLAlchemy metadata system.

Conceptually:

```text
Declarative ORM classes
        +
Core Table objects
        ↓
shared metadata model
```

A declarative class contributes table metadata that Core expressions can also work with.

For example, an ORM model:

```python
class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
```

corresponds to table metadata that can be used through SQLAlchemy constructs.

The important lesson is that ORM and Core are layers of the same SQLAlchemy ecosystem, not separate universes.

## Example of mixed execution

```python
from sqlalchemy import update

stmt = (
    update(Customer)
    .where(Customer.country == "India")
    .values(country="IN")
)

with SessionFactory() as session:
    session.execute(stmt)
    session.commit()
```

This is ORM-enabled SQL expression execution without first loading every matching Customer into Python.

---

# 39. Mixed Workload Example

Imagine a pipeline platform.

## ORM handles

```text
Pipeline
PipelineRun
Watermark
DataQualityResult
```

Operations:

```text
create run
update status
record failure
read watermark
update watermark
```

## Core handles

```text
set-based update
batch staging operations
reporting query
configuration-driven extraction
```

## Database-native methods handle later

```text
very large bulk movement
```

The architecture becomes:

```text
                    PostgreSQL
                        ↑
            ┌───────────┴───────────┐
            │                       │
          ORM                      Core
            │                       │
     metadata/domain          set-based/data access
            │                       │
            └──────── Engine ───────┘
```

This composition should be explicit and documented rather than accidental.

---

# 40. Pipeline Metadata ORM Example

A practical control-plane model can use:

```text
Pipeline
PipelineRun
Watermark
```

## Pipeline

```python
class Pipeline(Base):
    __tablename__ = "pipelines"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    config_json: Mapped[str]
```

## PipelineRun

```python
class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    pipeline_id: Mapped[int] = mapped_column(
        ForeignKey("pipelines.id")
    )
    status: Mapped[str]
    started_at: Mapped[datetime]
    finished_at: Mapped[datetime | None]
    rows_in: Mapped[int] = mapped_column(default=0)
    rows_out: Mapped[int] = mapped_column(default=0)
    error_message: Mapped[str | None]

    pipeline: Mapped[Pipeline] = relationship(
        back_populates="runs"
    )
```

## Watermark

```python
class Watermark(Base):
    __tablename__ = "watermarks"

    id: Mapped[int] = mapped_column(primary_key=True)
    pipeline_name: Mapped[str] = mapped_column(unique=True)
    last_processed_value: Mapped[str]
```

## `start_run()`

```python
from datetime import datetime, timezone


def start_run(session: Session, pipeline_id: int) -> PipelineRun:
    run = PipelineRun(
        pipeline_id=pipeline_id,
        status="running",
        started_at=datetime.now(timezone.utc),
        finished_at=None,
        rows_in=0,
        rows_out=0,
    )
    session.add(run)
    session.flush()
    return run
```

Why flush?

Because the caller may need database-generated identity before continuing within the same transaction.

## `finish_run()`

```python
def finish_run(
    session: Session,
    run: PipelineRun,
    *,
    rows_in: int,
    rows_out: int,
) -> None:
    run.status = "success"
    run.rows_in = rows_in
    run.rows_out = rows_out
    run.finished_at = datetime.now(timezone.utc)
    session.commit()
```

## `get_watermark()`

```python
def get_watermark(
    session: Session,
    pipeline_name: str,
) -> Watermark | None:
    stmt = select(Watermark).where(
        Watermark.pipeline_name == pipeline_name
    )
    return session.scalars(stmt).first()
```

## `set_watermark()`

For a small metadata table, ORM object manipulation is straightforward:

```python
def set_watermark(
    session: Session,
    pipeline_name: str,
    last_processed_value: str,
) -> None:
    watermark = get_watermark(session, pipeline_name)

    if watermark is None:
        watermark = Watermark(
            pipeline_name=pipeline_name,
            last_processed_value=last_processed_value,
        )
        session.add(watermark)
    else:
        watermark.last_processed_value = last_processed_value

    session.commit()
```

For concurrency-sensitive control metadata, the transaction and database constraints must still be designed carefully. The ORM does not replace database locking or uniqueness requirements.

---

# 41. ORM Usage Policy

A team should not standardize “ORM everywhere.”

A better policy is workload-based.

## ORM may be preferred when

- the workload operates on relatively small metadata/control tables
- object relationships materially reduce code complexity
- individual entities are the unit of work
- Unit of Work behavior is useful
- object identity is useful to the application

## Core may be preferred when

- the operation is strongly set-based
- exact SQL control matters
- dynamic SQL composition is important
- large batches are involved
- object materialization is unnecessary

## Database-native bulk paths should be evaluated when

- very large row movement dominates
- PostgreSQL-specific bulk capabilities are central to throughput
- Python object construction is not part of the requirement

## Architecture review required when

- millions of ORM objects may be created
- ORM is used for bulk ingestion
- relationships are lazily loaded inside loops
- Session lifetime is unclear
- query count is unknown for high-volume paths
- performance claims are based on intuition rather than measurement

The policy should be validated against real workloads.

---

# 42. ORM vs Pydantic Models

An ORM model and an external validation model have different primary responsibilities.

```text
ORM model
=
persistence mapping

Pydantic model
=
validation / serialization boundary
```

A common architecture is:

```text
External API payload
        ↓
Pydantic validation model
        ↓
application logic
        ↓
SQLAlchemy ORM model
        ↓
database
```

## Why separate the classes?

External input and database persistence evolve for different reasons.

The API may accept:

```json
{
  "country": "India",
  "name": "Alice"
}
```

The database model may additionally contain:

```text
id
created_at
updated_at
internal flags
foreign keys
```

Combining these responsibilities can create unwanted coupling between:

- external API contracts
- validation rules
- database persistence details
- security boundaries
- serialization behavior

The lesson is separation of responsibilities, not “never reuse any types.”

Pydantic is only introduced at awareness level here; detailed validation design belongs elsewhere in the curriculum.

---

# 43. Internal Mechanics: Object to SQL

Consider:

```python
customer = Customer(
    name="Alice",
    country="India",
)

session.add(customer)
session.flush()
```

Conceptually:

```text
Python object
      ↓
ORM instrumentation/state tracking
      ↓
Session tracks pending object
      ↓
Unit of Work determines database operation
      ↓
SQL INSERT generated
      ↓
SQLAlchemy Engine
      ↓
dialect / driver
      ↓
PostgreSQL
```

The important point is that PostgreSQL never sees a “Customer object.”

It sees SQL and parameters.

The ORM is the mapping and coordination layer.

## What SQL might look like?

Conceptually:

```sql
INSERT INTO customers (name, country)
VALUES (%(name)s, %(country)s)
```

The exact placeholder syntax depends on the dialect and driver. Do not use a copied SQL string as a contract for every backend.

---

# 44. Internal Mechanics: Relationship Loading

Consider:

```python
pipeline.runs
```

Conceptually, attribute access can lead to:

```text
Python attribute access
        ↓
SQLAlchemy checks relationship state
        ↓
Is related data already loaded?
        ↓
Yes → return in-memory objects
        |
        No
        ↓
relationship loading strategy
        ↓
possibly issue SELECT
        ↓
PostgreSQL
        ↓
rows returned
        ↓
ORM maps rows to objects
        ↓
Identity Map tracks instances
        ↓
relationship collection available
```

Eager loading changes the timing and shape of this work.

The key production lesson is that object attribute access can have database side effects when lazy loading is enabled.

---

# 45. Internal Mechanics: Identity Map

Use:

```python
a = session.get(Customer, 1)
b = session.get(Customer, 1)

assert a is b
```

The conceptual sequence is:

```text
request Customer id=1
        ↓
Session checks identity state
        ↓
object already represented?
        ↓
return current instance
```

This creates consistent identity within the Session.

At scale, however:

```text
many rows
  ↓
many ORM objects
  ↓
identity tracking
  ↓
large Session state
```

That does not automatically make ORM unusable. It means that object materialization and Session lifetime become performance and memory variables that should be measured.

---

# 46. Internal Mechanics: Flush vs Commit

Keep this model memorized:

```text
session.add()
      ↓
pending object
      ↓
session.flush()
      ↓
database transaction synchronized
      ↓
transaction still active
      ↓
session.commit()
      ↓
transaction completed
```

The critical distinction is:

```text
flush ≠ commit
```

A flush can be necessary to obtain database-generated information or to synchronize state before another query.

A commit completes the transaction.

Do not use flush as a durability guarantee.

---

# 47. Performance Thinking

ORM overhead can come from multiple sources.

## Python-side costs

- object creation
- attribute instrumentation
- identity tracking
- relationship collections
- Session bookkeeping
- Python loops

## Database-side costs

- SQL execution
- indexes
- locks
- query plans
- transaction overhead

## Boundary costs

- network round trips
- parameter adaptation
- result materialization
- driver work

A useful mental model is:

```text
ORM abstraction cost
+
Python object cost
+
network/database cost
=
observed workload cost
```

Therefore:

> ORM performance is a workload property, not a philosophical property.

## What to measure

At minimum for a meaningful comparison:

- elapsed time
- rows per second
- peak memory where practical
- number of SQL statements
- transaction strategy
- batch size
- database CPU where observable

A slow ORM benchmark does not prove all ORM workloads are slow.

A fast ORM benchmark does not prove ORM is the best abstraction for every workload.

---

# 48. Memory Thinking

Compare two representations of the same data.

## Tabular result

```text
row values
row values
row values
```

## ORM object graph

```text
Customer object
  ↓
attributes
  ↓
relationship collection
  ↓
Order objects
  ↓
Session identity state
```

The object representation can involve significantly more Python-managed state than a compact tabular representation.

For a small metadata workload, this can be a useful trade.

For a 20-million-row extraction, the same object model may add memory and CPU that the pipeline does not need.

This is why “large data” should trigger a representation question:

> Do I need domain objects, or do I need efficient tabular movement?

---

# 49. Database Set Operations

The database is optimized for set-based operations.

Suppose you need to update many rows matching one condition.

The conceptual operation is:

```text
Database
  ↓
set-based UPDATE
  ↓
Database
```

An object-heavy alternative is:

```text
Database
  ↓
ORM objects
  ↓
Python loop
  ↓
object changes
  ↓
flush
  ↓
Database
```

The second approach may be useful when individual object behavior matters.

The first approach is often simpler when the requirement is purely set-based.

SQLAlchemy ORM supports executing SQL expression constructs directly, so the choice is not binary.

Example:

```python
from sqlalchemy import update

stmt = (
    update(Order)
    .where(Order.amount < 0)
    .values(amount=0)
)

with SessionFactory() as session:
    session.execute(stmt)
    session.commit()
```

No loop over individual `Order` objects is required for the operation above.

The database remains responsible for the set operation.

---

# 50. DataFrame and Analytical Boundary

ORM is generally not the natural abstraction for:

- DataFrame ingestion
- analytical extraction
- Parquet movement
- very large set processing

For those workloads, investigate:

```text
SQLAlchemy Core
pandas
Polars
database-native bulk paths
```

The boundary can look like:

```text
PostgreSQL
    ↓
SQLAlchemy / database access
    ↓
pandas or Polars
    ↓
DataFrame / analytical processing
```

The point is not that ORM can never appear in an analytical system.

The point is that object materialization should be justified by the workload.

---

# 51. N+1 Case Study

## Scenario

A platform has 500 pipelines. Each pipeline has recent run records.

Naive code:

```python
pipelines = session.scalars(
    select(Pipeline)
).all()

for pipeline in pipelines:
    recent_runs = pipeline.runs[:5]
    print(pipeline.name, recent_runs)
```

If `pipeline.runs` is lazily loaded, the code may perform one query for the pipelines plus additional queries for relationships.

The exact number depends on configuration and what is already loaded, so measure it rather than assuming a fixed count.

## Diagnosis

1. Turn on SQL logging in a local environment.
2. Execute the loop.
3. Count relationship SELECTs.
4. Inspect whether they repeat the same pattern.
5. Replace lazy loading with a deliberate eager-loading strategy.
6. Count again.

## Example fix

```python
stmt = (
    select(Pipeline)
    .options(selectinload(Pipeline.runs))
)

pipelines = session.scalars(stmt).all()
```

Then inspect the generated SQL and the size of the returned relationship sets.

## Engineering lesson

The issue is not “ORM.”

The issue is hidden database work caused by an access pattern that did not match the workload.

---

# 52. `joinedload` Case Study

Suppose:

```text
1 Customer
100 Orders
```

A joined eager-load shape can produce 100 SQL rows because the customer columns are repeated alongside each order.

Conceptually:

```text
Customer columns + Order 1
Customer columns + Order 2
Customer columns + Order 3
...
Customer columns + Order 100
```

This can increase:

- transferred row width
- SQL result size
- duplicate parent data
- ORM result-processing work

The alternative may be `selectinload`, which retrieves the parents and related collection through coordinated SELECT operations.

The decision should consider actual relationship cardinality and query plan.

## A many-to-one example

For:

```text
1 Order → 1 Customer
```

`joinedload(Order.customer)` may be attractive because the join does not create the same collection-style multiplication.

Again, inspect the actual workload.

---

# 53. Session Longevity Case Study

## Bad shape

```python
# ⚠️ INTENTIONALLY BROKEN TRAINING EXAMPLE

global_session = SessionFactory()

while True:
    process_pipeline_a(global_session)
    process_pipeline_b(global_session)
    process_pipeline_c(global_session)
```

Potential problems include:

- identity-map growth
- stale in-memory state
- transaction leakage
- unclear ownership
- poor failure isolation
- difficult debugging

## Better shape

✅ **PRODUCTION-ORIENTED PATTERN**

```python
def process_pipeline(engine, pipeline_id: int) -> None:
    with SessionFactory(bind=engine) as session:
        run_pipeline_metadata_work(session, pipeline_id)
        session.commit()
```

The exact transaction boundary belongs to your application design, but the stateful Session should have a meaningful owner.

## Production lesson

Do not solve Session-lifecycle problems by creating a global state container.

Define a lifecycle and enforce it.

---

# 54. Detached Object Case Study

Problem:

```python
with SessionFactory() as session:
    customer = session.get(Customer, 1)

# Session is closed.
print(customer.orders)
```

Why it can fail:

```text
customer.orders
      ↓
relationship not loaded
      ↓
needs SQL
      ↓
needs active Session
      ↓
Session no longer available
```

A deliberate eager-loading approach:

```python
with SessionFactory() as session:
    stmt = (
        select(Customer)
        .options(selectinload(Customer.orders))
        .where(Customer.id == 1)
    )
    customer = session.scalars(stmt).one()

print(customer.orders)
```

The deeper lesson is that object lifetime and database-access lifetime are related.

---

# 55. Complete Hands-On Lab

The following lab is intentionally progressive. Do not skip the prediction step.

Every lab follows:

```text
Objective
   ↓
Setup
   ↓
Predict what Python and PostgreSQL will do
   ↓
Run code
   ↓
Inspect result / SQL
   ↓
Debug failure cases
   ↓
Write the production takeaway
```

## Lab 1 — Define ORM Models

### Objective

Create `Customer` and `Order` models using modern SQLAlchemy 2.x style.

### Setup

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    orders: Mapped[list["Order"]] = relationship(
        back_populates="customer"
    )


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id")
    )
    amount: Mapped[float]

    customer: Mapped[Customer] = relationship(
        back_populates="orders"
    )
```

### Learner prediction

Before creating tables, answer:

1. Which database tables are represented?
2. Which column is the primary key?
3. Where is the foreign key?
4. Is a SQL connection used merely by importing this module?

### Expected observation

The classes define mappings. They do not by themselves execute SQL.

### Debugging

Check names, typing, foreign-key target, and relationship `back_populates` pairs.

### Production takeaway

Model declarations are metadata and mapping configuration, not runtime database activity.

---

## Lab 2 — Create a Session

### Objective

Use a Session with an existing Engine.

```python
from sqlalchemy.orm import Session

with Session(engine) as session:
    customer = session.get(Customer, 1)
    print(customer)
```

### Learner prediction

Ask:

- Is Session the same thing as a PostgreSQL connection?
- When does the database need to be contacted?
- What happens when the context exits?

### Production takeaway

Keep Session creation and closure explicit.

---

## Lab 3 — Add and Commit

### Objective

Create and persist one object.

```python
with SessionFactory() as session:
    customer = Customer(name="Alice")
    session.add(customer)
    session.commit()
    print(customer.id)
```

### Prediction

Before running, write the likely lifecycle:

```text
construct object
→ add
→ flush during commit
→ INSERT
→ commit
```

### Debugging

Try removing `commit()` and observe what another independent Session sees.

### Production takeaway

Object state and committed database state are different concepts.

---

## Lab 4 — Flush vs Commit

### Objective

Observe the difference.

```python
with SessionFactory() as session:
    customer = Customer(name="Bob")
    session.add(customer)
    session.flush()

    print(customer.id)

    # Transaction is still active.
    session.commit()
```

### Learner prediction

Answer before running:

- Could a generated primary key become available after flush?
- Has the transaction necessarily committed after flush?

### Production takeaway

Flush synchronizes; commit completes the transaction.

---

## Lab 5 — Unit of Work

### Objective

Change multiple related objects and commit them together.

```python
with SessionFactory() as session:
    customer = session.get(Customer, 1)
    order = Order(customer=customer, amount=250.0)

    customer.name = "Alice Updated"
    session.add(order)

    session.commit()
```

### Learner prediction

Identify all changes that the Session must coordinate.

### Debugging

Introduce a constraint violation and observe rollback behavior.

### Production takeaway

Unit of Work is most valuable when object-level changes form one logical transaction.

---

## Lab 6 — Identity Map

### Objective

Observe object identity.

```python
with SessionFactory() as session:
    first = session.get(Customer, 1)
    second = session.get(Customer, 1)

    print(first is second)
```

### Expected observation

For the same identity in the same Session, the two lookups normally return the same ORM instance.

### Production takeaway

Identity Map is a Session-scoped object-consistency mechanism, not a global cache.

---

## Lab 7 — Relationships

### Objective

Create `Customer → Orders`.

```python
with SessionFactory() as session:
    customer = Customer(name="Carol")
    customer.orders = [
        Order(amount=100.0),
        Order(amount=200.0),
    ]

    session.add(customer)
    session.commit()
```

### Learner prediction

Explain the relationship between the Python object graph and the database foreign key.

### Production takeaway

ORM relationships express object navigation over relational foreign keys.

---

## Lab 8 — N+1

### Objective

Deliberately trigger lazy relationship loads.

```python
with SessionFactory() as session:
    customers = session.scalars(select(Customer)).all()

    for customer in customers:
        print(customer.orders)
```

Enable local SQL logging and count the queries.

### Prediction

Explain whether you expect one SELECT or potentially many SELECTs.

### Debugging

Look for repeated statements differing primarily by parent identity.

### Production takeaway

Attribute access can trigger I/O. ORM code must be reasoned about as database code.

---

## Lab 9 — `selectinload`

### Objective

Replace the N+1 pattern with coordinated eager loading.

```python
stmt = (
    select(Customer)
    .options(selectinload(Customer.orders))
)

with SessionFactory() as session:
    customers = session.scalars(stmt).all()

    for customer in customers:
        print(customer.orders)
```

### Measure

Count SQL statements before and after.

Do not assume an absolute count before observing the generated SQL.

### Production takeaway

Eager loading should be selected based on relationship access and query behavior.

---

## Lab 10 — `joinedload`

### Objective

Compare joined eager loading.

```python
stmt = (
    select(Order)
    .options(joinedload(Order.customer))
)

with SessionFactory() as session:
    orders = session.scalars(stmt).all()
```

Then investigate a collection:

```python
stmt = (
    select(Customer)
    .options(joinedload(Customer.orders))
)

with SessionFactory() as session:
    customers = session.scalars(stmt).unique().all()
```

### Prediction

Explain what row multiplication could occur for a collection relationship.

### Production takeaway

Know when `unique()` is required and why joined collections can enlarge the SQL result.

---

## Lab 11 — Session Lifecycle

### Objective

Understand detached objects.

```python
with SessionFactory() as session:
    customer = session.get(Customer, 1)

# Session is closed.
print(customer.name)
```

Then test a not-yet-loaded relationship.

### Debugging

If relationship access fails, identify whether the object is detached and whether the relationship was loaded before Session closure.

### Production takeaway

Loaded data and database-capable object state are different things.

---

## Lab 12 — `expire_on_commit`

### Objective

Observe post-commit expiration behavior.

Default configuration:

```python
SessionFactory = sessionmaker(bind=engine)
```

Explicit no-expiration configuration:

```python
SessionFactoryNoExpire = sessionmaker(
    bind=engine,
    expire_on_commit=False,
)
```

### Experiment

1. Load an object.
2. Commit.
3. Change the same row from another Session.
4. Access the original object's attribute.
5. Repeat with `expire_on_commit=False`.

### Production takeaway

Expiration is a data-freshness behavior. Treat it as a deliberate trade-off.

---

## Lab 13 — Pipeline Metadata

### Objective

Model and manipulate Pipeline, PipelineRun, and Watermark.

Implement:

```text
start_run()
finish_run()
get_watermark()
set_watermark()
```

Use bounded Sessions and explicit transaction behavior.

### Production takeaway

This is the reference workload where ORM can provide meaningful object-level structure.

---

## Lab 14 — ORM Bulk Insert

### Objective

Insert a large batch without constructing one ORM object per row.

```python
from sqlalchemy import insert

rows = [
    {"name": "Alice"},
    {"name": "Bob"},
]

with SessionFactory() as session:
    session.execute(insert(Customer), rows)
    session.commit()
```

### Prediction

How is this different from `session.add(Customer(...))` for each row?

### Production takeaway

ORM-enabled bulk DML can be substantially more SQL-oriented than per-object persistence, but it has different object-state semantics.

---

## Lab 15 — Core Comparison

### Objective

Run a comparable batch through Core.

```python
from sqlalchemy import insert

stmt = insert(Customer)

with engine.begin() as conn:
    conn.execute(stmt, rows)
```

### Compare

Record:

- elapsed time
- rows/second
- SQL statements
- memory
- transaction strategy

### Production takeaway

Use evidence to understand what abstraction overhead matters for the workload.

---

## Lab 16 — Benchmark

### Objective

Build a controlled comparison.

Use one PostgreSQL instance, the same schema, the same logical dataset, the same machine resources, and repeated runs.

Record actual values.

Never invent results.

---

# 56. `pipeline_metadata_orm` Exercise

The exercise is conceptually named `pipeline_metadata_orm.py`, but the implementation remains inside this Markdown file to respect the file-only constraint.

## Requirements

Model:

```text
Pipeline
PipelineRun
Watermark
```

Implement:

```text
start_run()
finish_run()
get_watermark()
set_watermark()
```

## Starter architecture

```python
from datetime import datetime, timezone
from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Pipeline(Base):
    __tablename__ = "pipelines"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    config_json: Mapped[str]

    runs: Mapped[list["PipelineRun"]] = relationship(
        back_populates="pipeline"
    )


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    pipeline_id: Mapped[int] = mapped_column(
        ForeignKey("pipelines.id")
    )
    status: Mapped[str]
    started_at: Mapped[datetime]
    finished_at: Mapped[datetime | None]
    rows_in: Mapped[int] = mapped_column(default=0)
    rows_out: Mapped[int] = mapped_column(default=0)
    error_message: Mapped[str | None]

    pipeline: Mapped[Pipeline] = relationship(
        back_populates="runs"
    )


class Watermark(Base):
    __tablename__ = "watermarks"

    id: Mapped[int] = mapped_column(primary_key=True)
    pipeline_name: Mapped[str] = mapped_column(unique=True)
    last_processed_value: Mapped[str]
```

## Required reasoning

Before writing functions, answer:

1. Which data is object-centric?
2. Which operations are transactional?
3. Which objects need identity inside the Session?
4. Which fields require database uniqueness?
5. Which operations could be expressed as Core DML instead?

## `start_run()` starter

```python
def start_run(session: Session, pipeline_id: int) -> PipelineRun:
    run = PipelineRun(
        pipeline_id=pipeline_id,
        status="running",
        started_at=datetime.now(timezone.utc),
        finished_at=None,
        rows_in=0,
        rows_out=0,
        error_message=None,
    )
    session.add(run)
    session.flush()
    return run
```

## `finish_run()` starter

```python
def finish_run(
    session: Session,
    run: PipelineRun,
    *,
    status: str,
    rows_in: int,
    rows_out: int,
    error_message: str | None = None,
) -> None:
    run.status = status
    run.rows_in = rows_in
    run.rows_out = rows_out
    run.error_message = error_message
    run.finished_at = datetime.now(timezone.utc)
```

The caller decides when to commit the unit of work.

## `get_watermark()` starter

```python
def get_watermark(
    session: Session,
    pipeline_name: str,
) -> Watermark | None:
    return session.scalars(
        select(Watermark).where(
            Watermark.pipeline_name == pipeline_name
        )
    ).first()
```

## `set_watermark()` starter

```python
def set_watermark(
    session: Session,
    pipeline_name: str,
    last_processed_value: str,
) -> None:
    watermark = get_watermark(session, pipeline_name)

    if watermark is None:
        session.add(
            Watermark(
                pipeline_name=pipeline_name,
                last_processed_value=last_processed_value,
            )
        )
    else:
        watermark.last_processed_value = last_processed_value
```

## Task

Run a complete transaction:

```python
with SessionFactory() as session:
    try:
        run = start_run(session, pipeline_id=1)
        set_watermark(session, "orders", "2026-09-29T12:00:00Z")
        finish_run(
            session,
            run,
            status="success",
            rows_in=1000,
            rows_out=998,
        )
        session.commit()
    except Exception:
        session.rollback()
        raise
```

### Production lesson

Keep the repository/service API focused on business operations while keeping Session ownership visible at an appropriate architectural boundary.

---

# 57. Required N+1 Exercise

## Step 1 — Create the problem

Use:

```python
with SessionFactory() as session:
    pipelines = session.scalars(
        select(Pipeline)
    ).all()

    for pipeline in pipelines:
        print(pipeline.name, pipeline.runs)
```

## Step 2 — Turn on SQL logging

```python
engine = create_engine(database_url, echo=True)
```

Observe the actual statements.

## Step 3 — Count queries

Use a test listener or an SQL logging counter.

Do not assume the count from the source code alone.

## Step 4 — Apply `selectinload`

```python
stmt = (
    select(Pipeline)
    .options(selectinload(Pipeline.runs))
)

with SessionFactory() as session:
    pipelines = session.scalars(stmt).all()
```

## Step 5 — Compare

Record:

```text
query count
elapsed time
returned rows
```

## Step 6 — Investigate `joinedload`

```python
stmt = (
    select(Pipeline)
    .options(joinedload(Pipeline.runs))
)

with SessionFactory() as session:
    pipelines = session.scalars(stmt).unique().all()
```

Now inspect:

- SQL row count
- parent row duplication
- network transfer
- result processing

## Required conclusion

Do not answer:

> “`selectinload` is always better.”

Instead answer:

> “For this relationship shape and observed query workload, I chose ___ because ___.”

---

# 58. ORM Performance Benchmark

## The required comparison

The roadmap requires a 1-million-row comparison.

Compare:

```text
1. ORM object insertion
2. ORM bulk execution
3. SQLAlchemy Core
4. PostgreSQL COPY after Topic 09
```

COPY is included here only as a future comparison point. Do not implement its Topic 09 mechanics yet.

## Stage A — Run now

Measure:

- ORM object insertion
- ORM bulk execution
- Core batch insertion

## Stage B — Run after Topic 09

Add:

- PostgreSQL `COPY`

## Do not fabricate results

This module deliberately contains no invented timing numbers.

Your environment determines the results.

## Benchmark design

Use:

- same PostgreSQL server
- same table schema
- same indexes
- same logical dataset
- same machine/container resources
- same Python version
- same SQLAlchemy version
- same PostgreSQL driver
- same transaction strategy for the throughput comparison
- repeated trials
- warm-up where reasonable

### A fair throughput policy

For example, define a fixed batch/commit policy such as:

```text
1,000,000 logical rows
10,000 rows per transaction
100 transactions
```

Then use the same logical transaction policy where the methods support it.

A separate experiment can measure a single giant transaction, but label it separately rather than comparing unlike transaction boundaries.

## Benchmark dimensions

| Dimension | What to record |
|---|---|
| Elapsed time | seconds per run |
| Throughput | rows/second |
| Peak memory | MB/GiB where practical |
| SQL statements | count if measurable |
| Transaction count | commits/rollbacks |
| Batch size | rows per execution |
| Dataset | exact row generator/version |
| Environment | CPU, RAM, PostgreSQL container/resources |
| Software | Python, SQLAlchemy, psycopg, PostgreSQL versions |

## Results table template

Fill this with actual measurements:

| Method | Rows | Batch size | Transactions | Time (s) | Rows/s | Peak memory | SQL statements |
|---|---:|---:|---:|---:|---:|---:|---:|
| ORM objects | 1,000,000 | record your value | record | record | record | record | record |
| ORM bulk | 1,000,000 | record your value | record | record | record | record | record |
| Core | 1,000,000 | record your value | record | record | record | record | record |
| COPY | 1,000,000 | record | record | record | record | record | record |

## Benchmark code skeleton

The following is an experiment skeleton, not a promise of any particular result.

```python
from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter


@dataclass
class BenchResult:
    method: str
    rows: int
    elapsed_seconds: float

    @property
    def rows_per_second(self) -> float:
        return self.rows / self.elapsed_seconds


def benchmark(name: str, rows: int, fn) -> BenchResult:
    start = perf_counter()
    fn()
    elapsed = perf_counter() - start
    return BenchResult(
        method=name,
        rows=rows,
        elapsed_seconds=elapsed,
    )
```

Implement each method separately and ensure the dataset is logically identical.

## ORM object-mode example

```python
def insert_with_orm_objects(
    rows: list[dict[str, object]],
    session_factory,
) -> None:
    with session_factory() as session:
        for row in rows:
            session.add(Customer(**row))
        session.commit()
```

This is intentionally a straightforward object-mode benchmark, not a production prescription for 1 million rows.

## ORM bulk example

```python
def insert_with_orm_bulk(
    rows: list[dict[str, object]],
    session_factory,
) -> None:
    with session_factory() as session:
        session.execute(insert(Customer), rows)
        session.commit()
```

## Core example

```python
def insert_with_core(
    rows: list[dict[str, object]],
    engine,
) -> None:
    stmt = insert(Customer)

    with engine.begin() as conn:
        conn.execute(stmt, rows)
```

For a full 1-million-row benchmark, generate batches rather than holding the entire dataset in memory if you want to isolate database method cost from Python dataset allocation.

## Fairness warning

A benchmark can be misleading if:

```text
ORM = one million objects + one giant transaction
Core = tiny batches + no commit cost
```

Those are different workloads.

Normalize the factors you intend to compare.

## What not to report

Do not write:

> “ORM is 20x slower.”

unless you actually measured 20x slower in a controlled experiment and recorded the environment and method.

Even then, write:

> “In this environment, for this implementation and dataset, method A took X and method B took Y.”

That statement is much more useful than a slogan.

---

# 59. Debugging Exercises

Use the same debugging model for every problem:

```text
Observed behavior
      ↓
Root cause
      ↓
ORM mechanics
      ↓
Database effect
      ↓
Corrective action
      ↓
Production lesson
```

## Problem 1 — `session.add()` assumed to execute INSERT immediately

### Broken code

```python
with SessionFactory() as session:
    customer = Customer(name="Alice")
    session.add(customer)

    print(customer.id)
```

### Diagnosis

The object has been added to the Session, but the database operation may not have been flushed yet.

### Correct pattern

```python
with SessionFactory() as session:
    customer = Customer(name="Alice")
    session.add(customer)
    session.flush()
    print(customer.id)
```

### Production lesson

Separate object tracking, flush, and commit in your reasoning.

## Problem 2 — Forgot to commit

### Symptom

Another Session cannot see the new row.

### Root cause

The first transaction was never committed.

### Fix

```python
session.commit()
```

or use an appropriate transaction context.

### Production lesson

ORM does not eliminate database transaction semantics.

## Problem 3 — N+1

### Symptom

Hundreds or thousands of repeated SELECTs.

### Root cause

Lazy relationship loading inside a loop.

### Fix

Investigate `selectinload()` or `joinedload()` according to relationship shape.

### Production lesson

Measure query count for object-navigation code paths.

## Problem 4 — Detached object

### Symptom

Accessing a relationship after Session closure raises a detached-instance error.

### Root cause

The relationship was not loaded before the object became detached.

### Fix

Load required data inside the Session boundary or transform to a boundary object.

### Production lesson

Object lifetime must match data-access requirements.

## Problem 5 — `expire_on_commit` surprises

### Symptom

An attribute is refreshed after commit.

### Root cause

The object was expired as part of commit behavior.

### Fix

Decide whether the application needs fresh database state or stable post-commit in-memory state.

### Production lesson

Expiration is a consistency/freshness mechanism, not an inconvenience to disable automatically.

## Problem 6 — Long-lived Session

### Symptom

Memory grows and unrelated operations see confusing object state.

### Root cause

Session lifetime is broader than a logical unit of work.

### Fix

Introduce explicit Session boundaries.

### Production lesson

State ownership matters.

## Problem 7 — Million-row ORM loop

### Symptom

Insertion becomes slow and memory-intensive.

### Root cause

Millions of Python objects and Session bookkeeping are being created.

### Fix

Benchmark ORM bulk and Core; investigate native bulk movement for the actual workload.

### Production lesson

Do not make object creation the default data-movement abstraction.

## Problem 8 — Incorrect eager-loading strategy

### Symptom

A query returns far more SQL rows than expected.

### Root cause

Joined eager loading of a high-cardinality collection caused row multiplication.

### Fix

Benchmark `selectinload()` and `joinedload()` for the real relationship shape.

### Production lesson

Loading strategy must match cardinality.

## Problem 9 — ORM bulk behaves differently from object insertion

### Symptom

Code expects newly inserted rows to appear in ORM object state exactly as if each object had been added and flushed.

### Root cause

The execution path is SQL-oriented bulk DML rather than per-object Unit of Work processing.

### Fix

Explicitly choose the semantics you need and test Session synchronization behavior.

### Production lesson

“ORM bulk” does not mean “same as ORM object lifecycle, but faster.”

## Problem 10 — PostgreSQL-specific operation forced through ORM abstraction

### Symptom

Database-specific behavior is difficult to express or review.

### Root cause

An abstraction was imposed on a workload that needs database-specific control.

### Fix

Use the appropriate SQLAlchemy Core/dialect feature or direct driver path where justified.

### Production lesson

Abstraction should simplify the workload, not hide essential database behavior.

---

# 60. ORM Anti-Patterns

## Anti-pattern 1 — One global Session

### Beginner belief

“A Session is expensive, so create one and share it.”

### What actually happens

A Session is stateful and accumulates transaction/object context.

### Production consequence

Poor isolation, stale state, confusing identity behavior, unclear ownership.

### Correct mental model

A Session should have a deliberate unit-of-work scope.

## Anti-pattern 2 — Millions of ORM objects for bulk ingestion

### Beginner belief

“ORM is convenient, so every input row should become an object.”

### What actually happens

Python allocates and tracks a large number of objects.

### Production consequence

CPU and memory overhead can become significant.

### Correct mental model

Measure object-mode cost; use a set/batch/native path when object behavior is unnecessary.

## Anti-pattern 3 — Lazy relationship loading inside loops

### Beginner belief

`parent.children` is just a normal Python attribute.

### What actually happens

It can trigger SQL.

### Production consequence

N+1 query patterns.

### Correct mental model

ORM attribute access can have I/O side effects when a relationship is not loaded.

## Anti-pattern 4 — ORM for large extraction

### Beginner belief

“ORM gives me convenient Python records.”

### What actually happens

Millions of records become Python objects with identity/session overhead.

### Production consequence

High memory and CPU usage.

### Correct mental model

Choose the data representation required by the downstream workload.

## Anti-pattern 5 — ORM for set-based transformations

### Beginner belief

“Loop through objects because Python is easier.”

### What actually happens

The database loses the opportunity to perform one set operation.

### Production consequence

More Python work and potentially more database round trips.

### Correct mental model

Keep set logic in the database when the workload is set-based.

## Anti-pattern 6 — Assuming `session.add()` means INSERT now

### Correct mental model

`add()` tracks; flush synchronizes; commit completes the transaction.

## Anti-pattern 7 — Ignoring flush behavior

### Correct mental model

A query or commit can trigger flush behavior. Know when ORM changes reach the database.

## Anti-pattern 8 — Ignoring detached objects

### Correct mental model

A detached object can hold loaded values but cannot perform new database access without a Session.

## Anti-pattern 9 — Disabling `expire_on_commit` everywhere

### Correct mental model

Expiration is a deliberate consistency behavior. Disable it only when the application has a reason.

## Anti-pattern 10 — Treating ORM bulk as PostgreSQL `COPY`

### Correct mental model

ORM bulk DML is a SQL-oriented ORM path. PostgreSQL `COPY` is a database-native bulk movement mechanism covered later.

## Anti-pattern 11 — Forcing exact SQL control through ORM objects

### Correct mental model

Use the abstraction that keeps the important database behavior visible.

## Anti-pattern 12 — Forcing every database operation through one abstraction

### Correct mental model

A deliberate ORM + Core architecture can be clearer than a purity rule.

## Anti-pattern 13 — Unfair ORM vs Core benchmark

### Correct mental model

Normalize dataset, schema, indexes, transaction boundaries, environment, batch sizes, and measurement method.

---

# 61. ORM Design Patterns

## Pattern A — Metadata Service

```text
Pipeline control plane
      ↓
Session
      ↓
ORM metadata models
      ↓
PostgreSQL
```

Use for small records and object-centric lifecycle operations.

## Pattern B — Small Operational API

```text
API
 ↓
validation boundary
 ↓
service layer
 ↓
Session
 ↓
ORM entities
 ↓
PostgreSQL
```

Object relationships can reduce application mapping complexity.

## Pattern C — ORM + Core

✅ **PRODUCTION-ORIENTED PATTERN**

```text
ORM
 ├── metadata
 ├── entity lifecycle
 └── relationships

Core
 ├── set operations
 ├── dynamic SQL
 └── batch DML
```

Both can share the same Engine.

## Pattern D — Large Ingestion Boundary

```text
Input data
   ↓
validation / transformation
   ↓
Core or native bulk mechanism
   ↓
PostgreSQL
```

The large-volume path does not need to materialize business objects unless the workload explicitly requires that behavior.

## Pattern E — Analytical Query Boundary

```text
Database
   ↓
SQL / Core
   ↓
pandas / Polars / other analytical representation
```

Return only the data and representation the downstream workload needs.

---

# 62. Code Review Checklist

# SQLAlchemy ORM Code Review Checklist

## Model design

- Is ORM actually appropriate for the workload?
- Are `DeclarativeBase`, `Mapped[...]`, and `mapped_column()` used in modern style?
- Are relationships defined correctly?
- Are database constraints represented where useful without assuming the model is the entire schema?
- Is the model being incorrectly reused as an external validation/serialization model?

## Session

- Is Session lifecycle bounded?
- Is one Session being reused across unrelated workflows?
- Is the transaction boundary clear?
- Is rollback handled appropriately after failure?
- Is object state used after Session closure intentionally?

## Queries

- Could lazy relationship loading create N+1?
- Has query count been measured where relationship access is inside loops?
- Is eager loading chosen deliberately?
- Is `selectinload()` or `joinedload()` appropriate for this relationship shape?
- If a collection is joined eagerly, is `unique()` handled correctly?

## Performance

- Are large numbers of ORM objects being materialized?
- Is ORM object insertion being used for bulk loading without evidence?
- Is ORM being used for a set-based transformation that could be executed as SQL?
- Has ORM bulk execution been considered where object materialization is unnecessary?
- Has Core or a database-native bulk mechanism been considered?

## Architecture

- Does ORM reduce complexity for this workload?
- Would Core make the database behavior clearer?
- Can ORM and Core coexist deliberately?
- Are persistence and external validation responsibilities separated?
- Are performance claims backed by benchmark evidence?

---

# 63. Testing Strategy

ORM testing should cover both Python object behavior and database behavior.

## Mapping tests

Verify:

- classes map to expected tables
- primary keys work
- foreign keys work
- relationships load

## Session lifecycle tests

Test:

- Session creation
- successful commit
- rollback after failure
- Session close

## Persistence tests

Test:

- insert
- update
- delete
- flush behavior
- transaction rollback

## Relationship tests

Test:

- one-to-many mapping
- lazy loading behavior where intentionally enabled
- eager loading behavior
- query-count expectations for critical paths

## Detached-object tests

Explicitly test whether boundary objects require relationships after Session closure.

## Bulk-operation tests

Verify:

- rows are inserted
- expected transaction semantics occur
- Session synchronization assumptions are documented

## Core/ORM interoperability tests

Run:

- ORM object operations
- Core DML operations
- then verify expected state from a fresh Session

This is especially important when the same database table is touched through different abstraction layers.

## Representative pytest example

```python
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session


def test_customer_insert_round_trip():
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(Customer(name="Alice"))
        session.commit()

    with Session(engine) as session:
        customer = session.scalars(
            select(Customer).where(Customer.name == "Alice")
        ).one()

    assert customer.name == "Alice"
```

For real PostgreSQL tests, use the PostgreSQL test database rather than assuming SQLite is behaviorally identical.

## SQLite portability test

A small ORM model may also work with SQLite:

```python
sqlite_engine = create_engine("sqlite+pysqlite:///:memory:")
Base.metadata.create_all(sqlite_engine)
```

But passing a mapping test against SQLite does not prove PostgreSQL equivalence.

Differences can include:

- data types
- SQL syntax
- constraints
- locking behavior
- transaction behavior
- database-specific features

> **Production lesson:** SQLite compatibility is a useful portability experiment, not a guarantee of PostgreSQL equivalence.

---

# 64. Performance Measurement Checklist

Before comparing ORM and Core, confirm:

- same database
- same table schema
- same indexes
- same dataset
- same data distribution
- same transaction boundaries
- same batch-size policy where intended
- same machine/container resources
- same Python version
- same SQLAlchemy version
- same driver
- repeated trials
- warm-up policy documented
- memory measurement method documented
- SQL/query counts measured where practical

## Record the environment

```text
Python:
SQLAlchemy:
psycopg:
PostgreSQL:
CPU:
RAM:
Container limits:
Database configuration:
Dataset size:
Dataset generator/version:
Indexes:
Transaction strategy:
Batch size:
```

## Separate experiments

Do not mix these into one number:

```text
throughput
memory stress
query-count investigation
single giant transaction
small transaction batches
```

Each answers a different question.

## Benchmark rule

> **Benchmark the workload, not the library slogan.**

---

# 65. Interview Questions

## Basic

1. What is an ORM?
2. Why does object-relational mapping exist?
3. What is a SQLAlchemy ORM model?
4. What is `DeclarativeBase`?
5. What is `Mapped[...]`?
6. What is `mapped_column()`?
7. What is a Session?
8. What is `sessionmaker`?

## Intermediate

1. What happens when `session.add()` is called?
2. What is flush?
3. What is the difference between flush and commit?
4. What is rollback?
5. What is Unit of Work?
6. What is Identity Map?
7. What are transient, pending, persistent, and detached states?
8. What is a relationship?
9. What is lazy loading?
10. What is N+1?
11. What is `selectinload()`?
12. What is `joinedload()`?
13. What is `expire_on_commit`?
14. What is a detached object?

## Advanced

1. Why can ORM be a poor fit for bulk data movement?
2. Why can Identity Map become expensive at large row counts?
3. What is the difference between ORM object insertion and ORM bulk execution?
4. When would you deliberately mix ORM and Core?
5. Why might `selectinload()` be attractive for a collection relationship?
6. Why might `joinedload()` be attractive for a many-to-one relationship?
7. Why can `joinedload()` increase result complexity for collections?
8. Why does an eager-loaded collection query often require `unique()` before `scalars()`?
9. How would you detect N+1 in production code?
10. How would you benchmark ORM vs Core fairly?
11. What does `expire_on_commit=False` trade away?
12. Why should persistence models and external validation models usually have separate responsibilities?
13. How would you decide whether ORM reduces or increases complexity for a data pipeline?

### Interview answer standard

Do not answer from memory alone.

Use:

```text
workload
+
row volume
+
access pattern
+
relationship shape
+
transaction scope
+
performance measurement
+
maintainability
```

---

# 66. Architecture Questions

1. A pipeline metadata system has Pipeline, PipelineRun, and Watermark tables. What workload characteristics would you evaluate before choosing ORM?
2. A job must insert 10 million rows. What abstraction paths would you investigate, and what would you measure?
3. A developer materializes 500,000 ORM entities into one Session. What memory and lifecycle risks would you investigate?
4. A service has an N+1 problem. How would you diagnose it from both application and database perspectives?
5. How would you decide between `selectinload()` and `joinedload()` for a one-to-many relationship?
6. A team wants one global Session. What correctness and operational concerns would you raise?
7. When would you intentionally mix ORM and Core?
8. How would you build a repository layer using both ORM and Core without creating two inconsistent data models?
9. When does Identity Map simplify application logic, and when can it become unnecessary overhead?
10. How would you formulate a team ORM usage policy?
11. How would you prove ORM is a poor fit for a specific workload without relying on opinion?
12. How would you explain to an architecture review board why a small control-plane component uses ORM while the data plane uses Core/native bulk paths?
13. How would you measure whether a proposed eager-loading strategy actually improves the production workload?
14. What would you do if ORM code is readable but the generated SQL is unexpectedly expensive?
15. How would you preserve portability while accepting a PostgreSQL-specific optimization?

## Senior reasoning framework

Start every answer with:

```text
What is the workload?
```

Then evaluate:

```text
row volume
access pattern
relationship complexity
object identity
Unit of Work value
set-based behavior
transaction scope
performance sensitivity
operational simplicity
team maintainability
```

Do not start with:

> “ORM is faster.”

or:

> “ORM is slower.”

Those are incomplete claims.

---

# 67. Final Decision Framework

# How to Decide Whether ORM Fits a Workload

## 1. What is the row volume?

Small metadata operations and million-row data movement are different workloads.

## 2. Are you working with individual entities or large sets?

Objects favor object-level abstractions.

Large sets favor set-oriented reasoning.

## 3. Do relationships materially simplify the application?

If `pipeline.runs` genuinely reduces complexity, ORM may provide value.

## 4. Do you need Identity Map behavior?

If one object identity per database identity helps coordinate a unit of work, that is a real benefit.

## 5. Do you need Unit of Work behavior?

If several related object changes must be coordinated, Session-managed Unit of Work behavior may be valuable.

## 6. Is this a control/metadata workload?

Small operational metadata is a common ORM evaluation target.

## 7. Is this bulk data movement?

Bulk movement should trigger investigation of object overhead.

## 8. Is this a set-based transformation?

A set-based SQL operation may be a clearer fit than loading rows into Python objects.

## 9. How sensitive is the workload to Python-side overhead?

The more performance-sensitive the path, the more important measurement becomes.

## 10. What does benchmarking show?

Do not make the final decision before measuring the critical workload when performance is part of the requirement.

## Decision worksheet

Fill this out for a real system:

```text
Workload:

Primary operation:

Typical row count per operation:

Peak row count:

Individual entities or sets:

Relationship complexity:

Need for object identity:

Need for Unit of Work:

Transaction scope:

Latency requirement:

Throughput requirement:

Memory constraint:

Expected concurrency:

Database-specific features required:

Could Core express the operation clearly?

Could a native database path materially improve the workload?

Measured ORM cost:

Measured alternative cost:

Maintainability impact:

Decision:

Reason:
```

The “Decision” should be the result of the evidence, not the starting assumption.

---

# 68. Checkpoint

The roadmap checkpoint is:

- [ ] Define ORM models in SQLAlchemy 2.0 style.
- [ ] Explain Unit of Work and Identity Map.
- [ ] Detect and fix an N+1 query problem.
- [ ] Explain when to use ORM and when not to, with numbers.

Expand it into practical verification:

- [ ] Build models with `DeclarativeBase`.
- [ ] Use `Mapped[...]` correctly.
- [ ] Use `mapped_column()` intentionally.
- [ ] Create and scope Sessions deliberately.
- [ ] Explain `sessionmaker`.
- [ ] Demonstrate object creation and `session.add()`.
- [ ] Demonstrate flush vs commit.
- [ ] Demonstrate rollback.
- [ ] Model one-to-many relationships.
- [ ] Diagnose lazy-loading queries.
- [ ] Detect N+1 through SQL observation.
- [ ] Use `selectinload()`.
- [ ] Use `joinedload()`.
- [ ] Explain why joined collections may require `unique()`.
- [ ] Explain `expire_on_commit`.
- [ ] Diagnose detached objects.
- [ ] Use ORM for a pipeline metadata workload.
- [ ] Use ORM-enabled bulk execution.
- [ ] Compare ORM object insertion with Core.
- [ ] Record actual benchmark numbers.
- [ ] Write a workload-based ORM usage policy.
- [ ] Explain why ORM is not automatically the default for large data movement.

## Proof of understanding

You pass this checkpoint by implementing and measuring, not by reciting definitions.

---

# 69. Common Mistakes

## Loading millions of rows as ORM objects

**Beginner belief:** “ORM objects are convenient, so they are convenient at every scale.”

**What actually happens:** object allocation and Session bookkeeping increase with row count.

**Production consequence:** memory/CPU cost can become significant.

**Correct mental model:** choose a representation that matches the workload.

## Long-lived global Sessions

**Beginner belief:** “One Session avoids connection setup.”

**What actually happens:** Session is stateful object/transaction coordination state.

**Production consequence:** stale state and unclear ownership.

**Correct mental model:** Session factory is reusable; Session instances are scoped.

## Lazy loading inside loops

**Beginner belief:** “The loop is only Python.”

**What actually happens:** attribute access can issue SQL.

**Production consequence:** N+1.

**Correct mental model:** inspect ORM access patterns as database access patterns.

## Using ORM models as external data validation models

**Beginner belief:** “One class is simpler.”

**What actually happens:** persistence and external contracts have different responsibilities.

**Production consequence:** accidental coupling.

**Correct mental model:** separate the boundary when responsibilities differ.

## Assuming `session.add()` immediately executes SQL

**Correct mental model:** add tracks; flush synchronizes; commit completes the transaction.

## Ignoring rollback

**Correct mental model:** database failures and Session transaction state must be handled deliberately.

## Choosing eager loading without considering relationship shape

**Correct mental model:** cardinality and result-set shape determine trade-offs.

## Using `joinedload()` blindly on large collections

**Correct mental model:** joined collections can multiply rows and increase transferred data.

## Disabling `expire_on_commit` everywhere

**Correct mental model:** expiration has a data-freshness purpose.

## Treating ORM bulk APIs as identical to object insertion

**Correct mental model:** bulk DML is a different execution path with different object-state semantics.

## Forcing Core/native database operations through ORM

**Correct mental model:** abstraction is valuable only when it helps the actual workload.

## Assuming ORM and Core must be separate

**Correct mental model:** a deliberate mixed architecture is possible.

## Benchmarking ORM vs Core unfairly

**Correct mental model:** normalize schema, dataset, indexes, environment, transaction strategy, and measurement method.

---

# 70. Final Mental Model

# The ORM Mental Model

```text
Relational world

Table
Row
Column
Foreign Key
SQL

        ↕ ORM mapping

Object world

Class
Object
Attribute
Relationship
Session
```

## ORM

```text
ORM
=
mapping between relational data and Python objects
```

## Session

```text
Session
=
unit that coordinates ORM work and object state
```

The Session is not simply a PostgreSQL connection.

## Unit of Work

```text
Unit of Work
=
track changes and synchronize them with the database
```

## Identity Map

```text
Identity Map
=
maintain one current Python identity for a database identity
within a Session scope
```

## Relationships

```text
Relationship
=
object navigation mapped to relational relationships
```

## Loading strategy

```text
Lazy
=
load on access

Eager
=
load deliberately as part of the query strategy
```

## The decision principle

```text
ORM is an abstraction.

Use it when the abstraction reduces complexity.

Be cautious when the abstraction adds Python object overhead

to workloads that are fundamentally set-based or data-movement heavy.
```

The final decision is:

```text
Workload
+
Requirements
+
Measurements
+
Operational constraints
+
Maintainability
```

not ideology.

---

# 71. Final Review

## What You Now Understand

You should now understand:

- ORM and object-relational mapping
- relational model vs object model
- SQLAlchemy 2.x declarative mappings
- `DeclarativeBase`
- `Mapped[...]`
- `mapped_column()`
- Engine vs Session
- `Session`
- `sessionmaker`
- object creation
- `session.add()`
- flush
- commit
- rollback
- Unit of Work
- Identity Map
- ORM object states
- relationships
- lazy loading
- N+1
- N+1 detection
- `selectinload()`
- `joinedload()`
- eager-loading trade-offs
- Session lifecycle
- one Session per unit of work
- `expire_on_commit`
- detached objects
- ORM fit for pipeline metadata
- ORM limitations for large data movement
- ORM bulk execution
- ORM object insertion vs ORM bulk vs Core
- ORM + Core composition
- external validation model separation
- performance measurement
- workload-based policy

## What You Can Implement

You should be able to:

- create SQLAlchemy 2.x ORM models
- create a Session factory
- scope Sessions correctly
- create and persist objects
- use flush deliberately
- commit and rollback transactions
- model relationships
- query ORM entities with `select()`
- diagnose lazy loading
- fix N+1 patterns
- use `selectinload()` and `joinedload()`
- handle detached objects deliberately
- configure `expire_on_commit`
- model pipeline metadata with ORM
- execute ORM bulk inserts
- use Core for set-based operations
- combine ORM and Core
- run an evidence-based ORM benchmark
- write a workload-based ORM usage policy

## What You Can Debug

You should now be able to investigate:

- unexpected SQL from relationship access
- N+1 queries
- excessive ORM object counts
- Session memory growth
- detached-object errors
- expiration surprises
- missing commits
- rollback failures
- bulk-operation behavior differences
- row multiplication from joined eager loading
- unfair performance comparisons

## What Comes Next

Topic 08 focuses on schema migrations with Alembic.

This module does not teach Alembic implementation.

The conceptual relationship is:

```text
Topic 06
SQLAlchemy Core
    ↓
Topic 07
SQLAlchemy ORM
    ↓
Topic 08
Schema migration management with Alembic
```

---

# 72. Production Rules to Remember

1. ORM maps relational structures to Python objects.
2. Session is not the database and is not simply a database connection.
3. Understand `add()`, flush, commit, and rollback separately.
4. Unit of Work coordinates object-level changes with database operations.
5. Identity Map maintains Session-scoped object identity.
6. Keep Session lifetime deliberate and bounded.
7. Treat relationship access as potentially database-active behavior.
8. Watch for N+1 query patterns.
9. Choose eager-loading strategy according to relationship shape and measured behavior.
10. Do not materialize huge numbers of ORM objects without measuring memory and CPU.
11. Do not assume ORM is the right abstraction for bulk data movement.
12. Use set-based database operations for set-based work.
13. ORM bulk execution is not identical to per-object ORM persistence.
14. ORM and Core can coexist deliberately.
15. Separate persistence mappings from external validation/serialization responsibilities when those boundaries differ.
16. Benchmark before making strong performance claims.
17. Build team ORM policies from workload evidence, not ideology.
18. Preserve database visibility: the ORM does not remove SQL, transactions, indexes, constraints, or query planning.
19. Choose the abstraction level that keeps the important behavior understandable.
20. The final answer to “Should we use ORM?” is workload-specific.

---

# Appendix A — Compact ORM Reference

## Model foundation

```python
class Base(DeclarativeBase):
    pass
```

## Mapped class

```python
class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
```

## Session factory

```python
SessionFactory = sessionmaker(bind=engine)
```

## Query

```python
stmt = select(Customer).where(Customer.name == "Alice")

with SessionFactory() as session:
    customers = session.scalars(stmt).all()
```

## Primary-key lookup

```python
customer = session.get(Customer, 1)
```

## Add

```python
session.add(customer)
```

## Flush

```python
session.flush()
```

## Commit

```python
session.commit()
```

## Rollback

```python
session.rollback()
```

## Relationship loading

```python
select(Pipeline).options(selectinload(Pipeline.runs))
```

```python
select(Order).options(joinedload(Order.customer))
```

## ORM bulk execution

```python
session.execute(insert(Customer), rows)
```

## Explicit no-expiration Session factory

```python
SessionFactory = sessionmaker(
    bind=engine,
    expire_on_commit=False,
)
```

Remember: these APIs are tools. Their value depends on workload.

---

# Appendix B — Production Decision Worksheet

Use this worksheet during a design review.

```text
1. Workload
   What exact database problem are we solving?

2. Data volume
   Typical / peak rows per operation?

3. Access pattern
   Individual objects, relationships, or large sets?

4. Object value
   Does Python object identity materially simplify the problem?

5. Unit of Work
   Do several object changes need coordinated persistence?

6. Relationship value
   Do relationships simplify the domain logic?

7. SQL shape
   Is the operation naturally set-based?

8. Performance
   What are the latency/throughput requirements?

9. Memory
   How many ORM objects could exist simultaneously?

10. Query count
    Could relationship access create N+1?

11. Loading strategy
    Why lazy / selectinload / joinedload?

12. Session lifecycle
    What is the unit of work?

13. Alternative abstraction
    Would Core be simpler?

14. Native database capability
    Is a database-native bulk or set-based path required?

15. Measurement
    What did the benchmark show?

16. Maintainability
    Does the abstraction reduce or increase team complexity?

17. Decision
    What are we standardizing, and why?
```

---

# Appendix C — Minimal Production-Oriented Skeleton

```python
from __future__ import annotations

from datetime import datetime
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class Pipeline(Base):
    __tablename__ = "pipelines"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    status: Mapped[str]
    updated_at: Mapped[datetime]


engine = create_engine(database_url)
SessionFactory = sessionmaker(bind=engine)


def mark_running(pipeline_id: int) -> None:
    with SessionFactory.begin() as session:
        pipeline = session.get(Pipeline, pipeline_id)
        if pipeline is None:
            raise ValueError(f"Unknown pipeline id: {pipeline_id}")

        pipeline.status = "running"
        pipeline.updated_at = datetime.now()


def get_running_pipelines() -> list[Pipeline]:
    with SessionFactory() as session:
        return session.scalars(
            select(Pipeline).where(Pipeline.status == "running")
        ).all()
```

This skeleton is deliberately simple. Real production code must add application-specific concerns such as timezone policy, error taxonomy, observability, retries, and repository boundaries.

The important architectural shape is:

```text
Engine
   ↓
SessionFactory
   ↓
bounded Session
   ↓
ORM model
   ↓
transactional work
   ↓
PostgreSQL
```

---

# End of Topic 07

The central lesson is not “use ORM” and not “avoid ORM.”

It is:

```text
Understand the abstraction.
Understand the database work it causes.
Measure the cost.
Choose based on workload.
```

When object relationships, identity, and Unit of Work reduce complexity, ORM may be a useful fit.

When the workload is dominated by large sets, bulk movement, analytical extraction, or database-native operations, investigate lower-level and set-oriented paths and measure them.

A production Data Engineer should be comfortable with both sides of the boundary and should be able to explain why a specific workload uses ORM, Core, database-native methods, or a deliberate combination.
