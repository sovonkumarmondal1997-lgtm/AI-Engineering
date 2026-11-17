# 07 — DDL, Constraints, and Column Data Types

> **Stage 2 — Python for Data Engineering**  
> **Module 2.6 — SQL for Data Engineers**  
> **Topic 07 — DDL, Constraints, and Column Data Types**
>
> Primary environments: **PostgreSQL 16+** and **DuckDB**
>
> This chapter is intentionally production-oriented. It teaches schema design as an engineering discipline rather than as a collection of DDL commands.

---

## 1. Learning Objectives

By the end of this chapter, you should be able to:

- explain what DDL is;
- create tables with intentional grain, types, keys, and constraints;
- organize objects with database schemas/namespaces;
- alter tables safely;
- use `CREATE TABLE AS SELECT` (CTAS);
- choose appropriate numeric, text, boolean, date/time, interval, and UUID types;
- explain why exact monetary values usually need exact decimal semantics;
- explain when `BIGINT` is safer for identifiers that can grow;
- distinguish `DATE`, `TIMESTAMP`, and `TIMESTAMPTZ`;
- use `INTERVAL`;
- understand UUID key strategies;
- define `PRIMARY KEY`, `UNIQUE`, `NOT NULL`, `CHECK`, `FOREIGN KEY`, and `DEFAULT`;
- reason about `ON DELETE` behavior;
- compare natural keys and surrogate keys;
- use identity columns and understand legacy `SERIAL`;
- use PostgreSQL `JSONB` and arrays;
- understand DuckDB `STRUCT`, `LIST`, `MAP`, and JSON;
- decide when semi-structured data should become first-class relational columns;
- distinguish views, materialized views, temporary tables, and generated columns;
- explain PostgreSQL `UNIQUE` behavior with multiple `NULL`s;
- use PostgreSQL 15+ `NULLS NOT DISTINCT`;
- design safer schema changes for large tables;
- recognize table-rewrite and lock risks;
- apply expand-and-contract migrations;
- create declarative PostgreSQL partitioned tables;
- use range partitioning by date;
- explain partition pruning;
- distinguish database partitioning from file/object-store partitioning;
- recognize when analytical warehouses may treat constraints as informational;
- compensate with explicit data-quality tests;
- use consistent naming conventions and `COMMENT ON`;
- debug schema problems systematically;
- write zero-row assertion queries;
- defend a production schema design in a technical review.

The durable principle is:

> **A database schema is an executable definition of what data is allowed to exist.**

---

## 2. Why Schema Design Matters in Data Engineering

Schema design affects much more than whether an `INSERT` statement succeeds.

It influences:

```text
data meaning
    ↓
stored representation
    ↓
comparison and arithmetic behavior
    ↓
constraint behavior
    ↓
query correctness
    ↓
pipeline reliability
    ↓
migration cost
```

A Data Engineer makes decisions about:

- what a row represents;
- which values are valid;
- which values are required;
- what identifies a row;
- which relationships must exist;
- which states should be impossible;
- how values should be represented;
- how the schema will evolve.

### Example

Consider:

```sql
CREATE TABLE orders (
    id INT,
    customer_email VARCHAR(255),
    amount FLOAT,
    status VARCHAR(255),
    created VARCHAR(50),
    metadata TEXT
);
```

This schema technically describes columns, but it does not adequately express:

```text
Is id unique?
Can id be NULL?
Is amount exact money?
What statuses are valid?
Is customer_email a relationship or just copied text?
What is created?
Does it represent an absolute instant?
Can created be NULL?
Is metadata structured JSON?
```

A stronger schema puts appropriate answers into the database design itself.

### Schema design as risk control

Good schema design can prevent:

```text
duplicate identities
invalid amounts
orphan foreign keys
missing required timestamps
impossible states
ambiguous names
unsafe assumptions
```

The closer a data-quality rule is enforced to the data boundary, the fewer downstream consumers need to compensate for it.

---

## 3. The Core Mental Model

The central principle is:

> **A database schema is an executable definition of what data is allowed to exist.**

A schema does not merely describe:

```text
column name
+
column type
```

It can also express:

```text
nullability
uniqueness
relationships
valid ranges
allowed states
defaults
generated values
physical organization
documentation
```

Think of table design as:

```text
Table design
    |
    +-- Types
    |
    +-- Keys
    |
    +-- Constraints
    |
    +-- Defaults
    |
    +-- Relationships
    |
    +-- Physical layout
    |
    +-- Documentation
```

### Semantics before syntax

Before writing DDL, answer:

```text
What does this data mean?

What values are valid?

What values are missing?

What identifies the row?

What relationships exist?

What should be impossible?
```

Only then write the SQL.

### Three connected models

#### Model 1 — Type correctness

```text
Data type
   ↓
stored representation
   ↓
comparison semantics
   ↓
constraint behavior
   ↓
query correctness
```

#### Model 2 — Key correctness

```text
grain
   ↓
key design
   ↓
constraints
   ↓
join correctness
```

#### Model 3 — Physical behavior

```text
schema design
   ↓
physical organization
   ↓
query behavior
   ↓
performance
```

This chapter introduces physical layout only where it is directly tied to schema design. Detailed index and `EXPLAIN` work belongs to Topic 08.

---

## 4. What Is DDL?

**DDL** means **Data Definition Language**.

It defines or changes database structures.

The core DDL verbs for this chapter are:

```text
CREATE
ALTER
DROP
```

Examples:

```sql
CREATE TABLE ...
```

```sql
ALTER TABLE ...
```

```sql
DROP TABLE ...
```

### DDL vs DML

You will also see **DML**:

```text
SELECT
INSERT
UPDATE
DELETE
```

The distinction is:

```text
DDL
→ changes the structure

DML
→ works with table rows
```

You do not need to treat DML as a separate course here. The important point is to understand how structural design affects the correctness of row operations.

---

## 5. CREATE TABLE

A table definition describes the intended row shape.

Example:

```sql
CREATE TABLE customers (
    customer_id BIGINT PRIMARY KEY,
    email TEXT NOT NULL,
    country TEXT,
    created_at TIMESTAMPTZ NOT NULL
);
```

Break it down:

```text
customer_id
    ↓
BIGINT
    ↓
PRIMARY KEY
```

means:

```text
column name
+
data type
+
identity/uniqueness rule
```

and:

```text
email TEXT NOT NULL
```

means:

```text
email
+
text representation
+
required value
```

### Column definition pattern

A useful mental template is:

```text
name
→ type
→ nullability
→ constraints
→ default/generated behavior
```

### Table-level constraints

A constraint can also be written at table level:

```sql
CREATE TABLE order_lines (
    order_id BIGINT NOT NULL,
    line_number INTEGER NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INTEGER NOT NULL,
    CONSTRAINT pk_order_lines
        PRIMARY KEY (order_id, line_number)
);
```

Table-level syntax is especially useful for:

- composite keys;
- named constraints;
- complex multi-column checks;
- clearer schema documentation.

---

## 6. Database Schemas as Namespaces

A database **schema** is a namespace for database objects.

PostgreSQL example:

```sql
CREATE SCHEMA app;
CREATE SCHEMA analytics;
```

Then:

```sql
CREATE TABLE app.customers (
    customer_id BIGINT PRIMARY KEY,
    email TEXT NOT NULL
);
```

and:

```sql
CREATE TABLE analytics.customer_summary (
    customer_id BIGINT NOT NULL,
    total_orders BIGINT NOT NULL
);
```

### Why namespaces help

Schemas can separate:

```text
application objects
analytics objects
staging objects
reporting objects
```

They also provide a useful organizational and permission boundary.

You do not need deep security knowledge here. The important engineering idea is that the same object name can exist in different namespaces without representing the same table.

For example:

```text
app.orders
analytics.orders
```

are different objects.

### Production naming habit

Prefer fully qualified names when ambiguity matters:

```sql
SELECT *
FROM analytics.customer_summary;
```

rather than relying on an implicit search path.

---

## 7. DROP TABLE

The basic command is:

```sql
DROP TABLE customers;
```

It is destructive.

Safer existence handling:

```sql
DROP TABLE IF EXISTS customers;
```

### Production risks

Dropping a table can affect:

- dependent views;
- application code;
- ETL/ELT jobs;
- downstream reports;
- permissions;
- foreign-key relationships.

Never treat:

```sql
DROP TABLE
```

as routine cleanup without confirming the dependency graph.

### Important distinction

`DROP TABLE` removes the table object.

It is not the same thing as:

```sql
DELETE FROM customers;
```

which removes rows while leaving the table structure.

Detailed transaction/locking behavior belongs to Topic 09. Here the key lesson is:

> **DDL can have broad dependency and deployment consequences.**

---

## 8. ALTER TABLE

`ALTER TABLE` changes an existing table definition.

### Add a column

```sql
ALTER TABLE customers
ADD COLUMN phone TEXT;
```

### Drop a column

```sql
ALTER TABLE customers
DROP COLUMN phone;
```

### Rename a column

```sql
ALTER TABLE customers
RENAME COLUMN phone TO phone_number;
```

### Why schema evolution matters

Production tables are usually not static.

Requirements change:

```text
new business field
new source attribute
renamed concept
retired field
new constraint
new type
new relationship
```

The challenge is not merely:

> “Can SQL perform the alteration?”

It is:

> “Can we change the schema without breaking readers, writers, jobs, and operational SLAs?”

That question becomes central in the later migration sections.

---

## 9. CREATE TABLE AS SELECT — CTAS

`CREATE TABLE AS SELECT` creates a new table from a query result.

Example:

```sql
CREATE TABLE customer_totals AS
SELECT
    customer_id,
    SUM(amount) AS total_spend
FROM orders
GROUP BY customer_id;
```

### Mental model

```text
query result
    ↓
new table
```

This is useful for:

- derived datasets;
- staging;
- one-off transformations;
- materializing intermediate results;
- rebuilding a table from transformed data.

### What CTAS does not automatically guarantee

Do not assume CTAS creates the full source table contract.

The resulting table may not carry the source table's:

- primary key;
- foreign keys;
- unique constraints;
- check constraints;
- comments;
- application-level metadata.

The exact inherited metadata depends on the engine and syntax.

Therefore:

> **CTAS creates a table from a result set; it is not automatically a full schema clone.**

### Production habit

If a CTAS result becomes a long-lived production table, explicitly review:

```text
grain
types
keys
constraints
defaults
documentation
```

---

## 10. Understanding SQL Data Types

A data type tells the database what kind of value a column represents and how that value should be interpreted.

A good type provides:

```text
correct semantics
+
appropriate range
+
appropriate precision
+
predictable comparison
+
interoperability
```

### Bad type selection often creates delayed bugs

For example:

```text
money → FLOAT
timestamp → TEXT
id → too-small integer
flag → VARCHAR
```

may appear to work initially.

The failures appear later:

```text
rounding differences
overflow
bad sorting
invalid arithmetic
ambiguous time zones
weak validation
inconsistent downstream schemas
```

### Data-type decision template

Before a major type choice, write:

```text
Column:
Business meaning:
Expected values:
Can it be NULL?
Expected range:
Precision requirement:
Time-zone requirement:
Chosen type:
Why:
Alternative considered:
Why not:
```

Example:

```text
Column:
amount

Business meaning:
monetary order amount

Expected values:
non-negative decimal values

Can it be NULL?
No

Expected range:
normal retail order values

Precision requirement:
exact decimal semantics

Time-zone requirement:
not applicable

Chosen type:
NUMERIC(18,2)

Why:
financial amount requires controlled decimal semantics

Alternative considered:
DOUBLE PRECISION

Why not:
binary floating-point approximation is not the intended representation for exact currency arithmetic
```

Repeat this habit whenever the type matters.

---

## 11. Numeric Types

The roadmap requires:

```text
SMALLINT
INTEGER
BIGINT
NUMERIC(p,s)
REAL
DOUBLE PRECISION
```

The decision should be driven by:

```text
meaning
range
precision
storage
engine semantics
```

### High-level map

| Type | Core idea | Typical use |
|---|---|---|
| `SMALLINT` | smaller integer range | bounded small integers |
| `INTEGER` | standard integer | common counts/IDs |
| `BIGINT` | larger integer range | long-lived IDs, large counts |
| `NUMERIC(p,s)` | exact decimal | financial values |
| `REAL` | approximate floating point | measurements where lower precision is acceptable |
| `DOUBLE PRECISION` | approximate floating point | scientific/analytical calculations |

Do not choose a numeric type by habit.

---

## 12. INTEGER Family: SMALLINT, INTEGER, BIGINT

The integer family stores whole numbers.

### `SMALLINT`

Use when the value range is genuinely small and bounded.

Examples might include:

```text
rating 0–5
small status code
limited category ordinal
```

Do not choose `SMALLINT` merely because the current values are small. Consider future valid values.

### `INTEGER`

Useful for ordinary whole-number values:

```text
quantity
moderate counters
bounded identifiers
```

### `BIGINT`

Use when the identifier or count may grow substantially over the lifetime of the system.

A good engineering explanation is:

> `BIGINT` provides a substantially larger integer range than `INTEGER`, making it a safer choice when an identifier can grow significantly over the lifetime of a production system. The correct choice still depends on expected cardinality and engine semantics.

This is the roadmap principle:

> **Use `BIGINT` for IDs that may grow.**

### Type-selection example

```text
Column:
customer_id

Business meaning:
stable customer identifier

Expected values:
whole-number identifiers

Can it be NULL?
No

Expected range:
potentially large over system lifetime

Precision requirement:
exact integer

Time-zone requirement:
not applicable

Chosen type:
BIGINT

Why:
the identifier's lifetime cardinality may exceed the comfortable range of INTEGER

Alternative considered:
INTEGER

Why not:
less headroom for long-lived growth
```

---

## 13. NUMERIC(p,s)

`NUMERIC(p,s)` represents exact decimal values.

Example:

```sql
amount NUMERIC(18,2)
```

Interpret the parameters:

```text
precision = total significant decimal digits
scale     = digits to the right of the decimal point
```

So:

```text
NUMERIC(18,2)
```

means:

```text
18 total digits
2 fractional digits
```

The exact accepted range follows the type's precision/scale rules.

### Why it fits money

Suppose:

```text
order amount = 19.99
tax = 1.60
total = 21.59
```

Financial systems generally want:

```text
exact decimal arithmetic
```

rather than approximate binary floating-point semantics.

### Data-type decision template

```text
Column:
amount

Business meaning:
order money

Expected values:
decimal currency amounts

Can it be NULL?
usually no for confirmed orders

Expected range:
depends on domain

Precision requirement:
exact decimal

Chosen type:
NUMERIC(18,2)

Why:
explicit decimal precision and scale match currency semantics

Alternative:
DOUBLE PRECISION

Why not:
approximate floating-point representation
```

### Scale is a business decision

Do not automatically choose:

```text
NUMERIC(18,2)
```

for every monetary domain.

Currencies, tax calculations, rates, quantities, and high-precision financial measures may need different scales.

The schema should reflect the actual domain.

---

## 14. REAL and DOUBLE PRECISION

`REAL` and `DOUBLE PRECISION` use approximate floating-point semantics.

That is useful for:

- scientific measurements;
- sensor values;
- model outputs;
- calculations where tiny representation differences are acceptable.

### Core distinction

```text
NUMERIC
→ exact decimal semantics

REAL / DOUBLE PRECISION
→ approximate floating-point semantics
```

Do not say floating point is “wrong.”

The correct statement is:

> Floating-point types are appropriate when approximate numerical representation is acceptable or desirable for the workload.

### Engineering decision

Ask:

```text
Do I need exact decimal equality?

Or do I need approximate numeric performance/range?
```

For money:

```text
NUMERIC
```

is usually the clearer choice.

For scientific measurements:

```text
DOUBLE PRECISION
```

may be appropriate.

---

## 15. Text Types

Common PostgreSQL choices include:

```sql
TEXT
VARCHAR
VARCHAR(n)
```

### `TEXT`

Use for unconstrained text where the business domain has no meaningful maximum length enforced at the database boundary.

Example:

```sql
description TEXT
```

### `VARCHAR(n)`

Use when the maximum length itself is a real domain rule.

Example:

```sql
country_code VARCHAR(2)
```

when the business definition truly requires two characters.

### Bad habit

Do not blindly create:

```sql
name VARCHAR(255)
```

for every text column.

Ask:

```text
Is 255 a meaningful business limit?

Or is it just a copied convention?
```

---

## 16. TEXT vs VARCHAR(n)

In PostgreSQL, `TEXT` and unconstrained `VARCHAR` are both variable-length string types.

The important design decision is whether a length limit is meaningful.

### Good reason for a bounded type

```sql
country_code VARCHAR(2)
```

if the domain guarantees a two-character code.

### Weak reason

```sql
customer_name VARCHAR(255)
```

because “all databases use 255.”

That is not a schema rule. It is a habit.

### Production principle

> A type constraint should communicate a real domain rule.

If the business does not care about a maximum length, `TEXT` is often the clearer PostgreSQL choice.

---

## 17. BOOLEAN

Boolean values represent a logical state.

Typical values:

```text
TRUE
FALSE
NULL
```

Example:

```sql
is_active BOOLEAN NOT NULL DEFAULT TRUE
```

Other useful names:

```text
is_deleted
is_verified
has_paid
has_address
```

### Naming conventions

Prefer names that read naturally:

```text
is_active
has_paid
```

rather than:

```text
active_flag
paid_status
```

unless the latter are established organizational conventions.

### NULL matters

A nullable boolean has three states:

```text
TRUE
FALSE
UNKNOWN / NULL
```

That can be useful when:

```text
we do not yet know the answer
```

But if the domain only allows:

```text
TRUE/FALSE
```

then use:

```sql
BOOLEAN NOT NULL
```

---

## 18. DATE

`DATE` represents a calendar date without a time-of-day.

Examples:

```text
birthday
accounting_date
contract_start_date
business_date
partition_date
```

Example:

```sql
order_date DATE NOT NULL
```

### Use `DATE` when time is not part of the meaning

If the event happened at:

```text
2026-09-28 15:42:11 UTC
```

then `DATE` alone loses meaningful information.

If the business meaning is simply:

```text
the accounting day is 2026-09-28
```

then `DATE` is the better semantic type.

---

## 19. TIMESTAMP

`TIMESTAMP` without time zone represents a date and clock time without PostgreSQL's timezone-aware instant semantics.

Example:

```sql
local_open_time TIMESTAMP
```

This can be appropriate when the value intentionally represents a local wall-clock concept.

### Why naive timestamps can be dangerous

Imagine:

```text
2026-03-29 02:30
```

If this represents an event in an international system, the missing timezone context makes the instant ambiguous.

Do not assume:

```text
TIMESTAMP
=
UTC
```

It does not inherently communicate that.

### Ask the semantic question

> Does this column mean a local wall-clock value, or an absolute point in time?

That decision determines the type.

---

## 20. TIMESTAMPTZ

> **POSTGRESQL**

`TIMESTAMPTZ` is PostgreSQL's timezone-aware timestamp type for representing an absolute instant.

Example:

```sql
created_at TIMESTAMPTZ NOT NULL
```

This is often appropriate for:

```text
event_time
created_at
updated_at
processed_at
published_at
```

### Important PostgreSQL behavior

PostgreSQL does not store a timezone name as row metadata for a `timestamptz` value.

The value represents an instant, while output is rendered using the session's timezone setting.

### Why event timestamps often need it

Suppose an event occurs at the same instant as:

```text
2026-09-28 10:00 UTC
```

A user in India may see:

```text
2026-09-28 15:30 +05:30
```

and a user in another timezone may see another local representation.

The underlying instant remains the same.

### Data-type decision template

```text
Column:
event_time

Business meaning:
absolute event instant

Expected values:
valid event timestamps

Can it be NULL?
No

Expected range:
application lifetime

Precision requirement:
timestamp precision supported by engine

Time-zone requirement:
required

Chosen type:
TIMESTAMPTZ

Why:
the business meaning is an absolute point in time

Alternative:
TIMESTAMP

Why not:
would not communicate timezone-aware instant semantics
```

---

## 21. INTERVAL

`INTERVAL` represents a duration or time span.

Examples:

```sql
INTERVAL '7 days'
```

```sql
INTERVAL '30 minutes'
```

```sql
INTERVAL '2 months'
```

Use it in date/time arithmetic:

```sql
SELECT
    created_at + INTERVAL '30 days'
FROM customers;
```

### Practical uses

- trial windows;
- retention windows;
- event inactivity thresholds;
- expiration calculations;
- scheduled validity periods.

### Important semantic distinction

An interval is not a timestamp.

```text
timestamp
→ when

interval
→ how long / how far
```

---

## 22. UUID

`UUID` stores a universally unique identifier value.

Example:

```sql
customer_id UUID PRIMARY KEY
```

UUIDs can be useful when identifiers need to be generated across distributed systems without a single database sequence coordinating every writer.

### UUID decision template

```text
Column:
external_customer_id

Business meaning:
globally unique customer identifier

Expected values:
UUID identifiers

Can it be NULL?
No

Expected range:
not applicable in the integer sense

Precision requirement:
exact identifier

Time-zone requirement:
not applicable

Chosen type:
UUID

Why:
distributed identifier generation and cross-system identity

Alternative:
BIGINT identity

Why not:
would require a different coordination model for externally generated IDs
```

### Trade-offs

UUID strategies can affect:

- readability;
- storage;
- index locality;
- generation location;
- interoperability.

Keep detailed UUID modeling for the later key-focused module.

---

## 23. NULLability and NOT NULL

`NOT NULL` means:

> This column must contain a non-NULL value.

Example:

```sql
email TEXT NOT NULL
```

### Three different concepts

```text
NOT NULL
→ value must exist

DEFAULT
→ value is supplied when the column is omitted

CHECK
→ value must satisfy a rule
```

They solve different problems.

### Example

```sql
status TEXT NOT NULL
    CHECK (status IN ('pending', 'paid', 'cancelled'))
    DEFAULT 'pending'
```

This means:

```text
must exist
must be one of the allowed states
defaults to pending when omitted
```

A default does not make a nullable column non-null.

---

## 24. PRIMARY KEY

A primary key represents the table's primary row identity.

Example:

```sql
CREATE TABLE customers (
    customer_id BIGINT PRIMARY KEY,
    email TEXT NOT NULL
);
```

A primary key provides:

```text
uniqueness
+
non-NULL identity
```

and has important indexing implications in PostgreSQL.

### Composite primary key

Consider `order_lines`.

The grain may be:

```text
one row per order line
```

A line number may only be unique within an order.

So:

```sql
PRIMARY KEY (order_id, line_number)
```

can express:

```text
order_id + line_number
```

as the entity identity.

### Grain-first template

```text
Table:
order_lines

Purpose:
individual products within orders

Grain:
one row per order line

Primary key:
(order_id, line_number)

Business key:
order_id + line_number

Important foreign keys:
order_id → orders
product_id → products
```

### Key lesson

A primary key is not “just an ID column.”

It represents the intended entity identity.

---

## 25. UNIQUE

`UNIQUE` enforces uniqueness according to the constraint's semantics.

Example:

```sql
CREATE TABLE customers (
    customer_id BIGINT PRIMARY KEY,
    email TEXT UNIQUE
);
```

Or a composite rule:

```sql
UNIQUE (country_code, external_customer_id)
```

### When to use it

Use `UNIQUE` when the business says:

```text
No two rows should have the same X
```

Examples:

```text
email
external_customer_id
country + account_number
```

### Important distinction

```text
PRIMARY KEY
→ primary entity identity

UNIQUE
→ another value or combination that must be unique
```

A table may have one primary key and multiple unique constraints.

---

## 26. CHECK

`CHECK` expresses row-level validity rules.

Example:

```sql
amount NUMERIC(18,2)
    CHECK (amount >= 0)
```

Another:

```sql
status TEXT
    CHECK (status IN ('pending', 'paid', 'cancelled'))
```

### Constraint decision template

```text
Business rule:
Order amount cannot be negative.

Constraint chosen:
CHECK (amount >= 0)

What invalid data it prevents:
negative amount values

What it does NOT prevent:
duplicate order IDs
orphan customer IDs
NULL amounts unless NOT NULL is also specified
```

### What CHECK is good at

- ranges;
- enum-like allowed states;
- simple cross-column invariants.

### What it does not replace

Do not use a `CHECK` constraint as a substitute for:

- complex workflow logic;
- external-service validation;
- multi-table business processes.

---

## 27. FOREIGN KEY

A foreign key expresses a parent-child relationship.

Example:

```sql
CREATE TABLE orders (
    order_id BIGINT PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);
```

Conceptually:

```text
customers
   ↑
   |
orders
```

The child row cannot point to a referenced key that does not satisfy the foreign-key relationship.

### Constraint decision template

```text
Business rule:
Every order must belong to an existing customer.

Constraint chosen:
FOREIGN KEY (customer_id)
REFERENCES customers(customer_id)

What invalid data it prevents:
orphan order.customer_id values

What it does NOT prevent:
duplicate orders for the same customer
negative amounts
invalid status values
```

### Parent vs child

```text
customers
→ parent

orders
→ child
```

The referenced key is on the parent side.

---

## 28. ON DELETE Behavior

Foreign keys can define behavior when a parent row is deleted.

Common actions include:

```text
NO ACTION
RESTRICT
CASCADE
SET NULL
SET DEFAULT
```

Exact timing and behavior can vary by engine and constraint semantics.

### `NO ACTION`

The default PostgreSQL behavior is generally to prevent an invalid referential state, with enforcement timing depending on whether the constraint is deferrable.

### `RESTRICT`

Reject the parent deletion when dependent rows exist; in PostgreSQL, `RESTRICT` is more immediate and cannot be deferred in the same way as `NO ACTION`.

### `CASCADE`

Delete child rows when the parent is deleted.

This can be useful for tightly owned dependent data.

It can also be dangerous.

### `SET NULL`

Set the child foreign-key column to `NULL`.

This requires the child column to allow `NULL`.

### Constraint decision example

```text
Business rule:
Order lines cannot exist without their order.

Constraint:
FOREIGN KEY (order_id)
REFERENCES orders(order_id)
ON DELETE CASCADE

What it prevents:
orphan order lines

What it does:
deletes dependent order lines with an order

What it does NOT mean:
that CASCADE is appropriate for every domain
```

Never use:

```text
CASCADE everywhere
```

as a default design philosophy.

The correct action depends on lifecycle semantics.

### Bulk-load consideration

Foreign keys can also add work during ingestion and validation.

For bulk loads, carefully consider:

```text
parent data availability
load order
validation cost
constraint enforcement behavior
batch size
```

Do not disable referential integrity casually.

---

## 29. DEFAULT

A default supplies a value when an insert omits the column.

Example:

```sql
created_at TIMESTAMPTZ
    NOT NULL
    DEFAULT CURRENT_TIMESTAMP
```

If the application does:

```sql
INSERT INTO customers (email)
VALUES ('a@example.com');
```

the database can populate:

```text
created_at
```

automatically.

### Explicit NULL is different

If a column is nullable:

```sql
INSERT INTO customers (email, created_at)
VALUES ('a@example.com', NULL);
```

the explicit `NULL` is not the same operation as omitting the column.

A default generally applies when the column is omitted rather than when an explicit `NULL` is supplied.

### Good default

A default should represent valid domain behavior.

Good example:

```text
created_at → current timestamp
```

Potentially dangerous example:

```text
country → 'UNKNOWN'
```

when the real meaning is “we do not know.”

Do not use defaults to hide missing data.

---

## 30. Constraint Interaction

Real tables use constraints together.

Example:

```sql
CREATE TABLE orders (
    order_id BIGINT GENERATED ALWAYS AS IDENTITY,
    customer_id BIGINT NOT NULL,
    amount NUMERIC(18,2) NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_orders
        PRIMARY KEY (order_id),

    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    CONSTRAINT chk_orders_amount
        CHECK (amount >= 0),

    CONSTRAINT chk_orders_status
        CHECK (status IN ('pending', 'paid', 'cancelled'))
);
```

### What each rule protects

| Constraint | Protects against |
|---|---|
| `PRIMARY KEY` | duplicate entity identity |
| `NOT NULL` | missing required value |
| `UNIQUE` | duplicate business value |
| `CHECK` | invalid value/range/state |
| `FOREIGN KEY` | broken relationship |
| `DEFAULT` | omission when a valid default exists |

### Why interaction matters

A `CHECK` does not replace `NOT NULL`.

For example:

```sql
CHECK (amount > 0)
```

does not necessarily mean the column cannot be `NULL` under SQL's three-valued logic.

When the business rule says:

```text
amount must exist
AND
amount must be positive
```

write:

```sql
amount NUMERIC(18,2) NOT NULL
    CHECK (amount > 0)
```

---

## 31. Natural Keys vs Surrogate Keys

### Natural key

A natural key is a real-world business identifier.

Examples:

```text
external_customer_id
country_code + account_number
email
```

### Surrogate key

A surrogate key is an identifier introduced for database design rather than because the real world requires that exact identifier.

Examples:

```text
BIGINT identity
UUID
```

### Comparison

| Factor | Natural key | Surrogate key |
|---|---|---|
| Business meaning | high | low |
| May change | potentially | usually stable |
| Cross-system usefulness | often high | depends |
| Join convenience | depends on width | often simple |
| Identity strategy | source/domain | database/application |

### Do not rank them universally

The correct choice depends on:

```text
stability
mutability
source integration
history
size
join patterns
business semantics
```

A common pattern is:

```text
surrogate primary key
+
unique business key
```

when both database identity and business identity are useful.

---

## 32. Identity Columns

Modern PostgreSQL identity columns are a declarative way to generate numeric identifiers.

Example:

```sql
CREATE TABLE customers (
    customer_id BIGINT
        GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,
    email TEXT NOT NULL
);
```

Another option:

```sql
customer_id BIGINT
    GENERATED BY DEFAULT AS IDENTITY
```

### `GENERATED ALWAYS`

The database normally generates the value.

### `GENERATED BY DEFAULT`

The database generates a value when the application does not supply one, while explicit values can be provided subject to the syntax and override rules.

### Why identity is useful

It communicates:

```text
this column is database-generated identity
```

in the table definition itself.

It is the modern declarative approach for new PostgreSQL designs.

---

## 33. SERIAL

PostgreSQL historically provided:

```sql
customer_id BIGSERIAL
```

`SERIAL` is a convenience notation built around a sequence-backed implementation.

It remains supported.

### Identity vs SERIAL

| Feature | Identity | `SERIAL` |
|---|---|---|
| Style | modern declarative | historical convenience |
| Uses sequence | yes, via identity mechanism | yes |
| New schema choice | generally clearer | legacy but valid |
| Standard-ish model | closer to SQL-standard identity concept | PostgreSQL-specific |

Do not say `SERIAL` is invalid.

The engineering lesson is:

> For new PostgreSQL designs, identity columns usually express generated-key intent more explicitly.

---

## 34. UUID Key Design

UUIDs can be generated in different places:

```text
application
database
upstream source
distributed service
```

### Source-generated UUID

Useful when multiple services need to create identifiers independently.

### Database-generated UUID

Useful when PostgreSQL owns the identity generation.

### Application-generated UUID

Useful when the application needs the identifier before the database insert.

### Distributed generation

Useful when multiple writers must generate unique identifiers without a central sequence.

### Trade-offs

Consider:

```text
identifier size
index behavior
sort locality
generation ownership
interoperability
operational tooling
```

Use UUID when distributed identity or external interoperability justifies it.

---

## 35. PostgreSQL JSONB

> **POSTGRESQL-SPECIFIC**

`JSONB` stores JSON-like semi-structured data in a binary representation suitable for PostgreSQL's JSON functionality.

Example:

```sql
CREATE TABLE orders (
    order_id BIGINT PRIMARY KEY,
    metadata JSONB
);
```

Querying a text field from JSON:

```sql
SELECT
    metadata ->> 'campaign_id' AS campaign_id
FROM orders;
```

### Good uses

- optional event metadata;
- evolving payload fields;
- nested source payloads;
- fields that are genuinely flexible.

### Trade-off versus relational columns

A real column is often better when a field is:

```text
frequently filtered
frequently joined
frequently aggregated
strongly typed
stable
governed
```

JSONB is often better when:

```text
schema is genuinely flexible
attributes vary significantly
raw payload preservation matters
occasional access is acceptable
```

Do not make JSONB a replacement for the relational model.

---

## 36. PostgreSQL Arrays

> **POSTGRESQL-SPECIFIC**

PostgreSQL supports array columns.

Example:

```sql
CREATE TABLE products (
    product_id BIGINT PRIMARY KEY,
    tags TEXT[]
);
```

A row might contain:

```text
['sale', 'premium', 'electronics']
```

### Good uses

- naturally list-like attributes;
- compact nested values;
- analytical or operational cases where the list is truly one attribute.

### Trade-off

If each array element needs:

```text
its own lifecycle
its own foreign key
frequent joins
independent constraints
```

a child table may be more appropriate.

Do not assume arrays are always preferable to normalization.

---

## 37. DuckDB STRUCT

> **DUCKDB-SPECIFIC**

DuckDB supports nested structured data with `STRUCT`.

Conceptually:

```text
STRUCT
→ one value
→ multiple named fields
```

Representative example:

```sql
SELECT
    {
        country: 'IN',
        tier: 'gold'
    } AS customer_profile;
```

The exact syntax can be version-sensitive; verify the installed DuckDB documentation.

### Why `STRUCT` is useful

It is useful for analytical data where nested named attributes need to remain together.

Conceptually:

```text
customer_profile
├── country
└── tier
```

This differs from a flat table where every attribute is a top-level column.

---

## 38. DuckDB LIST

> **DUCKDB-SPECIFIC**

`LIST` represents an ordered collection of values.

Example:

```sql
SELECT [10, 20, 30] AS scores;
```

A list can represent:

```text
multiple related values
nested analytics data
array-like structures
```

Like PostgreSQL arrays, a list is not automatically the right answer for relational child entities.

Ask:

```text
Is the collection part of one value?

Or does each element need independent identity?
```

---

## 39. DuckDB MAP

> **DUCKDB-SPECIFIC**

A `MAP` represents key/value data.

Conceptually:

```text
key → value
```

This is useful for:

- semi-structured attributes;
- dynamic key/value payloads;
- analytical exploration of flexible data.

Representative usage is version-sensitive, so verify exact DuckDB syntax for the installed version.

The design question remains:

> Is this data genuinely key/value and dynamic, or has it become a stable relational attribute?

---

## 40. DuckDB JSON

> **DUCKDB-SPECIFIC**

DuckDB provides JSON support for analytical processing of semi-structured data.

Representative shape:

```sql
SELECT
    json_extract(
        '{"campaign_id":"C123"}',
        '$.campaign_id'
    );
```

Exact function syntax can vary by DuckDB version; verify the installed version's documentation.

### PostgreSQL `JSONB` vs DuckDB JSON

High-level difference:

```text
PostgreSQL JSONB
→ database table type with PostgreSQL JSON operators and indexing ecosystem

DuckDB JSON
→ analytical database support for JSON processing and nested analytics
```

Do not assume identical syntax or identical physical behavior.

---

## 41. Semi-Structured Data Design

The production decision is not:

```text
JSON good
relational good
```

It is:

> **What structure best matches the stability, access pattern, and governance requirements of the data?**

### Prefer a real column when a field is:

- frequently filtered;
- frequently joined;
- frequently aggregated;
- strongly typed;
- stable;
- important to governance;
- part of business identity;
- part of a frequently enforced invariant.

### Prefer JSON/nested structures when:

- schema is genuinely flexible;
- attributes vary significantly;
- raw payload preservation matters;
- access is occasional;
- extracting every possible field would create schema churn.

### Promotion pattern

Start with:

```json
{
  "country": "India",
  "customer_tier": "gold"
}
```

Later, if those fields become stable and operationally important:

```text
country
customer_tier
```

may deserve first-class columns.

The transition is:

```text
flexible source representation
        ↓
stable business semantics
        ↓
promote important fields
```

This is a common Data Engineering evolution.

---

## 42. Views

A view is a stored logical query.

Example:

```sql
CREATE VIEW customer_summary AS
SELECT
    c.customer_id,
    COUNT(o.order_id) AS order_count,
    COALESCE(SUM(o.amount), 0) AS total_spend
FROM customers AS c
LEFT JOIN orders AS o
    ON o.customer_id = c.customer_id
GROUP BY c.customer_id;
```

### Mental model

```text
view
→ saved query interface
```

The query result is generally computed when the view is read rather than stored as an ordinary physical result table.

### Why use views?

- reusable abstraction;
- stable consumer interface;
- simplify complex queries;
- hide implementation details;
- centralize definitions.

A view is an interface, not automatically a performance optimization.

---

## 43. Materialized Views

A materialized view stores a query result.

Example:

```sql
CREATE MATERIALIZED VIEW daily_sales_summary AS
SELECT
    order_date,
    SUM(amount) AS total_amount
FROM orders
GROUP BY order_date;
```

### Mental model

```text
query
  ↓
stored result
```

Advantages:

```text
faster repeated reads
precomputed expensive logic
```

Trade-off:

```text
stored result can become stale
```

Refresh is therefore part of the design.

### View vs materialized view

| Property | View | Materialized view |
|---|---|---|
| Stores result | generally no | yes |
| Reads | recompute query logic | read stored result |
| Freshness | reflects current base data | depends on refresh |
| Storage | little result storage | result storage required |
| Main use | abstraction/interface | repeated expensive reads |

---

## 44. Temporary Tables

Temporary tables are useful for session-scoped intermediate work.

Example:

```sql
CREATE TEMP TABLE recent_orders AS
SELECT *
FROM orders
WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '7 days';
```

Uses include:

- multi-step SQL workflows;
- debugging;
- intermediate transformations;
- simplifying repeated references in a session.

### What they are not

A temporary table should not be treated as a persistent production schema object.

It is especially useful when:

```text
step A
→ materialize
→ inspect
→ step B
→ materialize
→ validate
```

is easier to reason about than one enormous query.

Use them intentionally rather than automatically.

---

## 45. Generated Columns

Generated columns derive a value from other columns according to database-defined generation logic.

> **POSTGRESQL**

Representative PostgreSQL syntax:

```sql
CREATE TABLE order_items (
    unit_price NUMERIC(18,2) NOT NULL,
    quantity INTEGER NOT NULL,
    line_total NUMERIC(20,2)
        GENERATED ALWAYS AS (unit_price * quantity) STORED
);
```

The generated value is derived by the database from the expression.

### Generated column vs DEFAULT

A default answers:

> “What value should be supplied when this column is omitted?”

A generated column answers:

> “What value should be derived from other column values?”

For example:

```text
DEFAULT
created_at → now()

GENERATED
line_total → unit_price * quantity
```

### Design considerations

Generated columns can:

- centralize repeated derivation;
- reduce application duplication;
- make invariants easier to express.

But support and restrictions are engine-specific. Verify the installed engine's documentation.

---

## 46. NULL and UNIQUE Semantics

This is an important PostgreSQL edge case.

Suppose:

```sql
CREATE TABLE customers (
    customer_id BIGINT PRIMARY KEY,
    email TEXT UNIQUE
);
```

Rows may be:

```text
email
----------------
a@example.com
NULL
NULL
```

PostgreSQL's default unique semantics allow multiple `NULL` values.

Why?

Because ordinary SQL `NULL` represents unknown/missing rather than an ordinary comparable value.

### Important warning

Do not say:

> “UNIQUE means the column can never contain duplicates including NULL.”

That is not the default PostgreSQL behavior.

### Business meaning question

If the business rule is:

```text
at most one unknown/null email
```

then ordinary `UNIQUE` does not express that rule.

This leads to:

```text
NULLS NOT DISTINCT
```

---

## 47. NULLS NOT DISTINCT

> **POSTGRESQL-SPECIFIC — PostgreSQL 15+**

PostgreSQL supports unique constraints/indexes that treat `NULL` values as not distinct.

Representative syntax:

```sql
CREATE TABLE customer_contacts (
    customer_id BIGINT PRIMARY KEY,
    email TEXT,
    CONSTRAINT uq_customer_contacts_email
        UNIQUE NULLS NOT DISTINCT (email)
);
```

Now multiple `NULL` values are not allowed under that uniqueness rule.

### Semantic change

Default:

```text
NULL
NULL
```

can coexist under `UNIQUE`.

With:

```sql
UNIQUE NULLS NOT DISTINCT
```

they conflict.

### Why this matters

The right choice depends on the business rule.

Ask:

```text
Does NULL mean:
"unknown, and many unknowns are acceptable"?

Or:
"missing value, but only one row may have it"?
```

Do not use `NULLS NOT DISTINCT` simply because it sounds stricter.

---

## 48. Safe Schema Changes

A one-line `ALTER TABLE` can have very different production consequences depending on:

- PostgreSQL version;
- exact operation;
- table size;
- existing data;
- dependencies;
- lock requirements;
- concurrent traffic.

The correct mental model is:

> **A schema change is both a database problem and a deployment problem.**

### Questions to ask

```text
Does this operation rewrite existing rows?

What lock does it need?

Can the lock wait behind long-running queries?

How long could the operation run?

Will old application code continue to work?

Can writers handle the transitional schema?

What is the rollback path?
```

Do not assume:

```text
every ALTER TABLE is expensive
```

and do not assume:

```text
every ALTER TABLE is metadata-only
```

The operation determines the risk.

---

## 49. ALTER TABLE on Large Tables

Consider:

```sql
ALTER TABLE orders
ADD COLUMN status TEXT DEFAULT 'pending';
```

The exact operational behavior depends on PostgreSQL version and the form of the default/constraint.

Modern PostgreSQL versions can optimize some constant-default additions without rewriting every existing row, but that does not mean every schema change is cheap.

### Think in terms of the operation

For any large-table change, ask:

```text
Does it rewrite the table?

Does it scan existing rows?

What lock is required?

What happens to concurrent traffic?

How does the migration interact with replicas?

How do we monitor it?

What happens if it is blocked?
```

Do not invent exact durations.

Use measurements and the actual PostgreSQL version documentation for production planning.

---

## 50. Table Rewrites

A table rewrite means existing table rows must be physically rewritten into a new representation.

Possible consequences:

```text
I/O
+
longer runtime
+
lock contention
+
storage pressure
+
replica impact
```

Not every schema change causes a rewrite.

Examples of operations that may be more operationally expensive include certain type changes or changes requiring existing row values to be transformed.

### Production habit

Before a migration on a large table, classify it:

```text
metadata-only / low rewrite risk
vs
row transformation / rewrite risk
```

Then verify against the exact PostgreSQL version and migration plan.

---

## 51. Locking Risks During Schema Changes

Think of a busy production table:

```text
application queries
        ↓
production table
        ↑
   ALTER TABLE
```

A schema change may need a lock that conflicts with concurrent operations.

Potential outcomes:

```text
ALTER waits
queries wait
deployment stalls
latency rises
timeouts occur
```

### Important questions

```text
Which lock is required?

What currently holds conflicting locks?

Can the migration wait safely?

How long is the lock likely to be held?

Is a lock timeout configured?

Can traffic continue during the migration?
```

Detailed lock modes belong to Topic 09. Here, the key lesson is operational awareness.

---

## 52. Expand-and-Contract Migrations

For breaking schema changes, an expand-and-contract approach reduces coordination risk.

Pattern:

```text
OLD SCHEMA
   ↓
EXPAND
(add compatible structures)
   ↓
MIGRATE CODE / DATA
   ↓
VERIFY
   ↓
CUTOVER
   ↓
CONTRACT
(remove old structures)
```

### Example

Current:

```text
customer_name
```

Desired:

```text
first_name
last_name
```

A risky direct change would immediately remove `customer_name`.

A safer conceptual sequence:

```text
add first_name
add last_name
keep customer_name
        ↓
deploy code that can read/write both
        ↓
backfill new columns
        ↓
validate equivalence
        ↓
switch readers/writers
        ↓
monitor
        ↓
remove old column later
```

### Safe-migration template

Before every schema-evolution task, write:

```text
Current schema:
Desired schema:
Application dependencies:
Compatibility period:
Expand step:
Data migration:
Validation:
Cutover:
Contract step:
Rollback considerations:
```

### Production principle

> **Schema changes are deployment coordination problems as well as DDL problems.**

---

## 53. Declarative Table Partitioning

> **POSTGRESQL**

PostgreSQL supports declarative partitioning.

Representative example:

```sql
CREATE TABLE events (
    event_id BIGINT NOT NULL,
    event_time TIMESTAMPTZ NOT NULL,
    payload JSONB
) PARTITION BY RANGE (event_time);
```

This creates a partitioned parent.

### Partitioning requirement

Before every partitioning design, state:

```text
Workload:
large event table queried by event time

Partition key:
event_time

Partition grain/range:
monthly partitions

Expected pruning predicate:
event_time >= lower_bound
AND event_time < upper_bound

Partition lifecycle:
create future partitions
retain/drop/archive old partitions

Why partitioning is justified:
large time-oriented workload with predictable access boundaries
```

### What partitioning is

```text
logical parent table
       ↓
multiple physical partitions
```

The query can target the parent while the database routes and manages rows across partitions according to the partition key.

Partitioning is not a magic performance switch.

---

## 54. Range Partitioning by Date

A common event design is monthly range partitioning.

```text
events
 ├── 2026-01
 ├── 2026-02
 ├── 2026-03
 └── ...
```

Example:

```sql
CREATE TABLE events_2026_03
PARTITION OF events
FOR VALUES FROM ('2026-03-01')
           TO ('2026-04-01');
```

### Half-open boundaries

The partition is:

```text
[start, end)
```

meaning:

```text
>= 2026-03-01
AND
< 2026-04-01
```

This aligns well with standard half-open time filtering:

```sql
WHERE event_time >= TIMESTAMPTZ '2026-03-01 00:00:00+00'
  AND event_time <  TIMESTAMPTZ '2026-04-01 00:00:00+00';
```

### Partitioning requirement

```text
Workload:
time-range event queries

Partition key:
event_time

Partition grain/range:
monthly

Expected pruning predicate:
half-open timestamp range

Partition lifecycle:
pre-create future partitions and manage historical retention

Why partitioning is justified:
queries and lifecycle operations align with month boundaries
```

---

## 55. Partition Pruning

Partition pruning allows the planner to avoid scanning partitions that cannot contain matching rows.

Example query:

```sql
SELECT COUNT(*)
FROM events
WHERE event_time >= TIMESTAMPTZ '2026-03-01 00:00:00+00'
  AND event_time <  TIMESTAMPTZ '2026-04-01 00:00:00+00';
```

If the table is partitioned by `event_time`, the planner can use the predicate to eliminate unrelated partitions.

### Mental model

```text
all partitions
     ↓
predicate on partition key
     ↓
identify relevant partitions
     ↓
scan only relevant partitions
```

### Partitioning requirement

```text
Workload:
March event analytics

Partition key:
event_time

Partition grain/range:
monthly

Expected pruning predicate:
event_time >= '2026-03-01'
AND event_time < '2026-04-01'

Partition lifecycle:
monthly creation and retention

Why partitioning is justified:
query predicates align with the partition boundary
```

### Important caution

Partitioning does not automatically improve every query.

A query with no useful predicate on the partition key may still need to inspect many partitions.

Detailed plan inspection belongs to Topic 08.

---

## 56. Database Partitioning vs File Partitioning

Partitioning also appeared in Module 2.5 for analytical files such as Parquet.

Compare:

| Database partitioning | File partitioning |
|---|---|
| Database-managed physical partitions | directory/object/file layout |
| SQL table abstraction | filesystem/object-store abstraction |
| partition pruning | file/partition pruning |
| transactional DB context | lake/lakehouse context |
| database lifecycle | object-store/data-layout lifecycle |

### Similarity

Both try to exploit:

```text
query predicate
+
physical organization
=
avoid unnecessary reads
```

### Difference

They operate at different layers.

```text
PostgreSQL
→ partitioned table inside database storage

Lake/lakehouse
→ partitions represented in files/directories/object-store layout
```

Do not treat them as identical technologies.

---

## 57. Constraints in Analytical Warehouses

Not every analytical warehouse behaves like PostgreSQL.

Some warehouses may record:

```text
PRIMARY KEY
UNIQUE
FOREIGN KEY
```

as metadata or optimizer information without enforcing those constraints in the same way a transactional database does.

The exact behavior is warehouse-specific.

### Critical distinction

```text
declared constraint
≠
guaranteed enforced invariant
```

in an environment where the engine does not enforce it.

### Why this matters

If the platform only records:

```text
PRIMARY KEY(customer_id)
```

informationally, your pipeline may still contain:

```text
duplicate customer_id
```

unless you test for it.

---

## 58. When Constraints Are Not Enforced

This creates two categories of invariants.

### Database-enforced invariant

```text
database
→ rejects invalid data
```

### Pipeline-tested invariant

```text
database accepts data
→ pipeline test detects invalid state
→ deployment/load fails
```

The engineering response is not:

> “The warehouse cannot enforce it, so the rule does not matter.”

Instead:

> **Move the invariant into explicit data-quality tests.**

Examples:

```text
uniqueness
referential integrity
allowed statuses
non-negative amounts
required timestamps
```

---

## 59. Data Tests for Informational Constraints

### Uniqueness

```sql
SELECT
    customer_id
FROM dim_customer
GROUP BY customer_id
HAVING COUNT(*) > 1;
```

Expected:

```text
zero rows
```

### Referential integrity

```sql
SELECT
    o.customer_id
FROM orders AS o
LEFT JOIN customers AS c
    ON c.customer_id = o.customer_id
WHERE c.customer_id IS NULL;
```

Expected:

```text
zero rows
```

### Invalid status

```sql
SELECT *
FROM orders
WHERE status NOT IN (
    'pending',
    'paid',
    'cancelled'
);
```

### Important production principle

> **When the database cannot enforce a business rule, the data pipeline must test it.**

These tests are not optional documentation. They are operational controls.

---

## 60. Naming Conventions

A consistent naming scheme makes SQL easier to understand and review.

A common convention is:

```text
snake_case
```

Examples:

```text
customer_id
order_id
created_at
updated_at
event_time
is_active
has_paid
```

### Recommended semantic suffixes/prefixes

```text
_id
→ identifier

_at
→ timestamp representing an instant

is_
→ boolean state

has_
→ boolean possession/existence
```

### Examples

Good:

```text
created_at
updated_at
customer_id
is_active
has_paid
```

Less descriptive:

```text
created
cust
active_flag
date1
status_code2
```

Do not blindly impose naming rules without understanding organizational conventions, but make semantic naming a deliberate standard.

---

## 61. `COMMENT ON` and Documentation

> **POSTGRESQL**

Documentation is part of schema design.

Example:

```sql
COMMENT ON TABLE customers
IS 'One row per customer account.';
```

And:

```sql
COMMENT ON COLUMN customers.created_at
IS 'Account creation instant represented as a timezone-aware timestamp.';
```

### Why comments matter

A future engineer should not need to reverse-engineer:

```text
what this table means
what one row represents
what created_at means
what source defines this field
```

### Documentation should answer

```text
grain
definition
business meaning
units
timezone semantics
source
lifecycle
```

Comments are not a substitute for proper naming, but they are useful metadata when names alone cannot carry the full meaning.

---

## 62. Production Schema Design Patterns

We will build a representative e-commerce model.

Tables:

```text
customers
addresses
products
orders
order_lines
payments
```

### `customers`

```text
Table:
customers

Purpose:
customer identity and account attributes

Grain:
one row per customer

Primary key:
customer_id

Business key:
email or external_customer_id depending on domain

Important foreign keys:
none in this simplified table
```

Representative DDL:

```sql
CREATE TABLE customers (
    customer_id BIGINT
        GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    external_customer_id TEXT
        UNIQUE,

    email TEXT
        NOT NULL
        UNIQUE,

    country_code VARCHAR(2),

    is_active BOOLEAN
        NOT NULL
        DEFAULT TRUE,

    created_at TIMESTAMPTZ
        NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ
        NOT NULL
        DEFAULT CURRENT_TIMESTAMP
);
```

Note that a default on `updated_at` only initializes the value. It does not automatically update the timestamp on every future change.

### `products`

```text
Table:
products

Purpose:
sellable product catalog

Grain:
one row per product

Primary key:
product_id

Business key:
sku

Important foreign keys:
none in this simplified model
```

```sql
CREATE TABLE products (
    product_id BIGINT
        GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    sku TEXT
        NOT NULL
        UNIQUE,

    product_name TEXT
        NOT NULL,

    unit_price NUMERIC(18,2)
        NOT NULL
        CHECK (unit_price >= 0),

    is_active BOOLEAN
        NOT NULL
        DEFAULT TRUE,

    created_at TIMESTAMPTZ
        NOT NULL
        DEFAULT CURRENT_TIMESTAMP
);
```

### `orders`

```text
Table:
orders

Purpose:
customer order header

Grain:
one row per order

Primary key:
order_id

Business key:
external_order_id where supplied

Important foreign keys:
customer_id → customers
```

```sql
CREATE TABLE orders (
    order_id BIGINT
        GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    external_order_id TEXT
        UNIQUE,

    customer_id BIGINT
        NOT NULL,

    status TEXT
        NOT NULL
        DEFAULT 'pending',

    order_total NUMERIC(18,2)
        NOT NULL
        CHECK (order_total >= 0),

    created_at TIMESTAMPTZ
        NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    CONSTRAINT chk_orders_status
        CHECK (status IN ('pending', 'paid', 'cancelled'))
);
```

### `order_lines`

```text
Table:
order_lines

Purpose:
individual products within orders

Grain:
one row per order line

Primary key:
(order_id, line_number)

Business key:
order_id + line_number

Important foreign keys:
order_id → orders
product_id → products
```

```sql
CREATE TABLE order_lines (
    order_id BIGINT NOT NULL,
    line_number INTEGER NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(18,2) NOT NULL CHECK (unit_price >= 0),

    CONSTRAINT pk_order_lines
        PRIMARY KEY (order_id, line_number),

    CONSTRAINT fk_order_lines_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_order_lines_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);
```

### `payments`

```text
Table:
payments

Purpose:
payment attempts and confirmed payments

Grain:
one row per payment transaction/attempt

Primary key:
payment_id

Business key:
external_payment_id

Important foreign keys:
order_id → orders
```

```sql
CREATE TABLE payments (
    payment_id BIGINT
        GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    external_payment_id TEXT
        NOT NULL
        UNIQUE,

    order_id BIGINT
        NOT NULL,

    status TEXT
        NOT NULL,

    amount NUMERIC(18,2)
        NOT NULL
        CHECK (amount >= 0),

    processed_at TIMESTAMPTZ,

    CONSTRAINT fk_payments_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id),

    CONSTRAINT chk_payments_status
        CHECK (status IN ('pending', 'authorized', 'captured', 'failed'))
);
```

---

## 63. Schema Design Debugging

When a schema causes problems, use a systematic process.

### Step 1 — Identify table grain

Write:

```text
one row per ...
```

If the answer is unclear, the schema is not ready.

### Step 2 — Identify entity identity

Ask:

```text
What makes two rows the same entity?
```

### Step 3 — Identify business keys

Ask:

```text
Which real-world identifiers should be unique?
```

### Step 4 — Review types

Check:

```text
money
IDs
timestamps
flags
text
semi-structured fields
```

### Step 5 — Review NULLability

For each column ask:

```text
Can the value genuinely be unknown/missing?
```

### Step 6 — Review constraints

Ask:

```text
What should be impossible?
```

### Step 7 — Review relationships

Check every foreign key:

```text
parent
child
delete behavior
```

### Step 8 — Review defaults

Ask:

```text
Does omission legitimately imply this value?
```

### Step 9 — Review schema evolution

Ask:

```text
How likely is this column to change?
What readers depend on it?
```

### Step 10 — Review partitioning needs

Ask:

```text
Does the table have a large-scale workload that aligns with a partition key?
```

### Step 11 — Review warehouse enforcement

If constraints are informational:

```text
Which tests enforce the same invariants?
```

### Step 12 — Add assertions

Make critical invariants executable.

---

## 64. Assertion Queries

Assertions should return zero rows when the schema and data satisfy the intended invariants.

### Duplicate identity

```sql
SELECT
    customer_id
FROM customers
GROUP BY customer_id
HAVING COUNT(*) > 1;
```

Expected:

```text
zero rows
```

### Invalid amount

```sql
SELECT *
FROM orders
WHERE order_total < 0;
```

Expected:

```text
zero rows
```

### Invalid status

```sql
SELECT *
FROM orders
WHERE status NOT IN (
    'pending',
    'paid',
    'cancelled'
);
```

Expected:

```text
zero rows
```

### Orphan foreign key

```sql
SELECT
    o.customer_id
FROM orders AS o
LEFT JOIN customers AS c
    ON c.customer_id = o.customer_id
WHERE c.customer_id IS NULL;
```

Expected:

```text
zero rows
```

### Missing event time

```sql
SELECT *
FROM events
WHERE event_time IS NULL;
```

Expected:

```text
zero rows
```

### Assertion mindset

A good assertion expresses:

```text
this must never be true
```

It should fail loudly when the invariant is violated.

---

## 65. Common Mistakes

### Mistake 1 — Money stored as FLOAT

**Bad example:**

```sql
amount FLOAT
```

**Why risky:** Exact currency arithmetic is not the intended numeric model.

**Correct approach:**

```sql
amount NUMERIC(18,2)
```

or another domain-appropriate exact decimal definition.

**Engineering lesson:** Choose a numeric representation that matches the business semantics.

---

### Mistake 2 — ID type too small

**Bad example:**

```sql
customer_id INTEGER
```

for a system expected to accumulate very large cardinality.

**Why risky:** Future growth can exceed the intended range.

**Correct approach:** Consider `BIGINT`.

---

### Mistake 3 — `VARCHAR(255)` everywhere

**Why risky:** The limit may communicate no real domain rule.

**Correct approach:** Use `TEXT` when unrestricted variable-length text is the actual semantic requirement, or a meaningful bounded type when the limit is real.

---

### Mistake 4 — Timestamp stored as text

**Bad:**

```sql
created_at TEXT
```

**Why risky:**

- weak validation;
- poor arithmetic semantics;
- difficult timezone handling;
- ambiguous formats.

**Correct:** Choose `DATE`, `TIMESTAMP`, or `TIMESTAMPTZ` according to meaning.

---

### Mistake 5 — Naive event timestamps

**Bad:**

```sql
event_time TIMESTAMP
```

when the value represents an absolute cross-system event.

**Correct:** Usually `TIMESTAMPTZ`.

---

### Mistake 6 — Missing primary key

Without a primary key, row identity may be ambiguous.

**Correct:** Explicitly define entity identity.

---

### Mistake 7 — Missing uniqueness

A business identifier can silently duplicate without a unique constraint or equivalent test.

---

### Mistake 8 — Missing NOT NULL

If a field is mandatory, the schema should normally make that requirement explicit.

---

### Mistake 9 — Overusing foreign keys without considering load behavior

Foreign keys provide valuable integrity but also influence load ordering and validation work.

Do not disable them casually.

---

### Mistake 10 — Careless `ON DELETE CASCADE`

Cascade can remove large amounts of dependent data.

Use it only when the child lifecycle is truly dependent on the parent.

---

### Mistake 11 — Defaults that hide missing data

Do not turn:

```text
unknown
```

into:

```text
'UNKNOWN'
```

just to avoid NULLs unless that value is part of the actual domain.

---

### Mistake 12 — Assuming NULL means zero

These are semantically different:

```text
0
NULL
```

Use the value that represents the real meaning.

---

### Mistake 13 — Assuming UNIQUE forbids multiple NULLs

In PostgreSQL's default unique semantics, multiple NULLs can coexist.

Use `NULLS NOT DISTINCT` when the business rule explicitly requires NULLs to be treated as the same missing value.

---

### Mistake 14 — Misusing JSON

Putting every new field inside JSON avoids schema changes but can weaken:

```text
types
constraints
discoverability
query ergonomics
governance
```

Use nested data intentionally.

---

### Mistake 15 — Unsafe ALTER TABLE

Do not execute a large-table schema change without assessing:

```text
rewrite
locks
duration
dependencies
rollback
```

---

### Mistake 16 — Assuming every ALTER rewrites

False.

The exact operation and PostgreSQL version matter.

---

### Mistake 17 — Assuming no ALTER ever rewrites

Also false.

Some operations can require row rewriting.

---

### Mistake 18 — Skipping expand-and-contract

Breaking a shared schema in one deployment can create incompatible readers and writers.

---

### Mistake 19 — Partitioning without a workload reason

Partitioning adds operational complexity.

Use it when:

```text
data size
access pattern
retention/lifecycle
```

justify the design.

---

### Mistake 20 — Assuming partitioning automatically makes queries faster

Partition pruning helps when predicates align with the partitioning strategy.

---

### Mistake 21 — Ignoring pruning

A partitioned table with poorly aligned predicates may still scan many partitions.

---

### Mistake 22 — Assuming warehouse constraints are enforced

Verify the actual engine behavior.

If constraints are informational:

```text
declare
+
test
```

rather than:

```text
declare
+
assume
```

---

### Mistake 23 — Inconsistent naming

Names such as:

```text
date1
cust
created
flag
```

increase semantic ambiguity.

---

### Mistake 24 — Missing documentation

Future engineers should not have to infer grain and meaning from SQL joins.

---

## 66. Beginner Practice

### Exercise 1 — `CREATE TABLE`

**Objective:** Create a basic customer table.

**Task:**

```text
customer_id
email
created_at
```

Use:

```text
BIGINT
TEXT
TIMESTAMPTZ
```

Add a primary key and `NOT NULL` where appropriate.

**Solution:**

```sql
CREATE TABLE customers (
    customer_id BIGINT PRIMARY KEY,
    email TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);
```

**Explanation:** The table expresses customer identity, required email, and a required event instant.

---

### Exercise 2 — `DROP TABLE`

**Task:** Safely remove a practice table.

**Solution:**

```sql
DROP TABLE IF EXISTS practice_customers;
```

**Production lesson:** Destructive DDL should be intentional.

---

### Exercise 3 — `ALTER TABLE`

**Task:** Add a phone column.

```sql
ALTER TABLE customers
ADD COLUMN phone TEXT;
```

Then rename it:

```sql
ALTER TABLE customers
RENAME COLUMN phone TO phone_number;
```

---

### Exercise 4 — CTAS

**Task:** Create a customer summary table from orders.

```sql
CREATE TABLE customer_order_counts AS
SELECT
    customer_id,
    COUNT(*) AS order_count
FROM orders
GROUP BY customer_id;
```

**Question:** Which constraints did CTAS automatically give you?

**Expected reasoning:** Do not assume primary keys, foreign keys, or source metadata were copied.

---

### Exercise 5 — Schemas

**Task:** Create:

```text
staging
analytics
```

and create one table in each.

**Solution:**

```sql
CREATE SCHEMA staging;
CREATE SCHEMA analytics;

CREATE TABLE staging.raw_orders (
    order_id BIGINT,
    payload TEXT
);

CREATE TABLE analytics.order_summary (
    order_id BIGINT,
    amount NUMERIC(18,2)
);
```

---

### Exercise 6 — Numeric type

**Task:** Choose a type for a monetary price.

Use the data-type decision template before answering.

**Expected answer:** An exact decimal type such as `NUMERIC(18,2)` when the domain requires cents and this precision is appropriate.

---

### Exercise 7 — Timestamp type

**Task:** Choose among:

```text
DATE
TIMESTAMP
TIMESTAMPTZ
```

for:

```text
birthday
office opening time in local wall-clock terms
distributed event occurrence
```

**Expected reasoning:**

```text
birthday → DATE
local wall-clock → TIMESTAMP
absolute event → TIMESTAMPTZ
```

subject to domain semantics.

---

### Exercise 8 — Primary key

Create a table with:

```sql
PRIMARY KEY (order_id)
```

Then attempt to insert the same key twice in a PostgreSQL practice table.

Document the failure.

---

### Exercise 9 — UNIQUE

Create:

```sql
email TEXT UNIQUE
```

and test a duplicate email.

---

### Exercise 10 — CHECK and DEFAULT

Create:

```sql
status TEXT NOT NULL DEFAULT 'pending'
```

with:

```sql
CHECK (status IN ('pending', 'paid', 'cancelled'))
```

Attempt an invalid status.

---

### Exercise 11 — Foreign key

Create:

```text
customers
orders
```

and attempt to insert an order for a customer that does not exist.

---

### Exercise 12 — `NOT NULL`

Attempt:

```sql
INSERT INTO customers (customer_id, email)
VALUES (1, NULL);
```

with:

```sql
email TEXT NOT NULL
```

Explain the failure.

---

## 67. Intermediate Practice

### Exercise 1 — Correct numeric types

Design types for:

```text
item_quantity
order_id
unit_price
sensor_reading
```

For each, provide:

```text
business meaning
range
precision
chosen type
alternative
why not
```

---

### Exercise 2 — Timestamp strategy

Design a table with:

```text
created_at
updated_at
event_time
birth_date
```

Choose appropriate types and justify each.

---

### Exercise 3 — UUID

Design a table whose identifier is externally generated as UUID.

Explain why you chose UUID instead of a database identity.

---

### Exercise 4 — Natural and surrogate keys

Design:

```text
customer_id BIGINT identity
external_customer_id TEXT UNIQUE
```

Explain why both can coexist.

---

### Exercise 5 — Identity

Create:

```sql
customer_id BIGINT
    GENERATED ALWAYS AS IDENTITY
    PRIMARY KEY
```

Insert rows without specifying the ID.

Explain how the database supplies identity values.

---

### Exercise 6 — SERIAL

Create a practice table with:

```sql
id BIGSERIAL PRIMARY KEY
```

Compare it conceptually with an identity column.

---

### Exercise 7 — Foreign key deletion

Design two relationships:

```text
order → order_lines
customer → orders
```

Choose different `ON DELETE` behaviors and defend them.

---

### Exercise 8 — JSONB

Create:

```sql
metadata JSONB
```

Insert:

```json
{"campaign_id":"C123","channel":"email"}
```

Query:

```sql
metadata ->> 'campaign_id'
```

Then identify one attribute that should become a real column if it becomes frequently filtered.

---

### Exercise 9 — PostgreSQL arrays

Create:

```sql
tags TEXT[]
```

Store a list of tags.

Then discuss whether a separate table would be better if tags need independent governance.

---

### Exercise 10 — Views

Create a reusable customer summary view.

Explain:

```text
why a view
vs
why a materialized view
```

---

### Exercise 11 — Temporary table

Materialize a filtered subset into a temp table and use it in a multi-step workflow.

Explain why the temporary object should not become an accidental persistent dependency.

---

### Exercise 12 — Generated column

Create a line-item table with:

```text
unit_price
quantity
line_total
```

where `line_total` is generated.

Explain how this differs from a default.

---

## 68. Advanced Practice

### Exercise 1 — UNIQUE + NULL

Demonstrate PostgreSQL behavior with:

```text
NULL
NULL
```

under a normal unique constraint.

Explain why both can be present.

---

### Exercise 2 — `NULLS NOT DISTINCT`

Create:

```sql
UNIQUE NULLS NOT DISTINCT (email)
```

and demonstrate the changed behavior.

---

### Exercise 3 — Safe large-table change

Design a migration for adding a required field to a very large table.

Require:

```text
Current schema:
Desired schema:
Dependencies:
Expand:
Backfill:
Validate:
Cutover:
Contract:
Rollback
```

---

### Exercise 4 — Table rewrite assessment

For several `ALTER TABLE` examples, classify:

```text
likely metadata-only
vs
potentially rewrite/scan intensive
```

Then state that exact behavior must be verified against the target PostgreSQL version.

---

### Exercise 5 — Lock-risk assessment

Design a checklist for deploying DDL to a busy production database.

---

### Exercise 6 — Expand-and-contract

Migrate:

```text
customer_name
```

into:

```text
first_name
last_name
```

without requiring one instantaneous breaking deployment.

---

### Exercise 7 — Partitioned events

Create monthly partitions and define:

```text
partition key
boundaries
future partition creation
retention lifecycle
pruning predicate
```

---

### Exercise 8 — Partition pruning

Write:

```sql
WHERE event_time >= ...
  AND event_time < ...
```

and explain why this predicate aligns with range-partitioned event data.

---

### Exercise 9 — File vs database partitioning

Compare the PostgreSQL design with a Parquet dataset partitioned by:

```text
year=2026/month=09
```

Explain the different layers.

---

### Exercise 10 — Unenforced warehouse constraints

Assume a warehouse accepts:

```text
PRIMARY KEY
FOREIGN KEY
```

as informational metadata.

Write tests for:

```text
duplicate customer IDs
orphan orders
```

---

### Exercise 11 — Naming and documentation

Take a poorly named schema:

```text
cust
dt
flag
amt
```

and redesign the names using:

```text
snake_case
_id
_at
is_
has_
```

Then add `COMMENT ON` statements.

---

### Exercise 12 — Complete design review

Given:

```text
millions of orders
event timestamps
money
customer relationship
semi-structured metadata
monthly lifecycle
future schema change
```

propose:

```text
types
keys
constraints
partition strategy
documentation
migration strategy
data tests
```

---

## 69. Debugging Challenges

### Challenge 1 — Money stored in FLOAT

**Symptom:** Financial reconciliation shows small numeric differences.

**Broken schema:**

```sql
CREATE TABLE payments (
    payment_id BIGINT PRIMARY KEY,
    amount DOUBLE PRECISION NOT NULL
);
```

**Diagnostic questions:**

```text
Does exact decimal arithmetic matter?
What rounding semantics are required?
```

**Root cause:** The type expresses approximate floating-point semantics.

**Corrected DDL:**

```sql
CREATE TABLE payments (
    payment_id BIGINT PRIMARY KEY,
    amount NUMERIC(18,2) NOT NULL
        CHECK (amount >= 0)
);
```

**Production lesson:** Choose numeric types from business semantics.

---

### Challenge 2 — IDs stored in too-small integer type

**Symptom:** Future inserts approach the type's representational limit.

**Broken:**

```sql
customer_id SMALLINT
```

**Root cause:** The chosen range does not match expected lifetime cardinality.

**Correction:** Consider `BIGINT`.

---

### Challenge 3 — Timestamps stored as TEXT

**Broken:**

```sql
created_at TEXT
```

**Symptom:**

- inconsistent formats;
- poor temporal comparisons;
- timezone ambiguity.

**Corrected approach:** Choose:

```text
DATE
TIMESTAMP
TIMESTAMPTZ
```

according to meaning.

---

### Challenge 4 — Missing primary key

**Symptom:** Two rows that represent the same entity cannot be reliably distinguished.

**Broken:**

```sql
CREATE TABLE customers (
    email TEXT
);
```

**Root cause:** Entity identity is undefined.

**Corrected:** Add an intentional primary key and, if appropriate, a business-key uniqueness constraint.

---

### Challenge 5 — Duplicate business key

**Symptom:** Multiple customers have the same external identifier.

**Diagnostic query:**

```sql
SELECT
    external_customer_id,
    COUNT(*)
FROM customers
GROUP BY external_customer_id
HAVING COUNT(*) > 1;
```

**Corrected approach:** Add a unique constraint if the business rule is truly “one row per external customer.”

---

### Challenge 6 — Missing foreign key

**Symptom:** Orders reference customer IDs that do not exist.

**Corrected:**

```sql
FOREIGN KEY (customer_id)
REFERENCES customers(customer_id)
```

or pipeline-level referential-integrity testing if the target engine does not enforce it.

---

### Challenge 7 — Unsafe `ON DELETE CASCADE`

**Symptom:** Deleting one parent unexpectedly deletes a large dependent graph.

**Root cause:** Cascade was selected without checking lifecycle semantics.

**Correct approach:** Choose deletion behavior from the domain relationship.

---

### Challenge 8 — JSON used where a stable column is required

**Symptom:** A frequently-filtered field exists only inside JSON.

**Root cause:** Flexibility was optimized before workload semantics.

**Corrected approach:** Promote the field to a typed column when it becomes stable and operationally important.

---

### Challenge 9 — Breaking schema change

**Symptom:** New deployment writes `first_name`, but old application code still expects `customer_name`.

**Root cause:** Direct breaking migration.

**Correct approach:** Expand-and-contract.

---

### Challenge 10 — Partition setup prevents effective pruning

**Symptom:** Monthly event query still scans many partitions.

**Diagnostic questions:**

```text
Is the predicate on the partition key?
Is the predicate shaped as a useful range?
Is the partition key actually aligned with workload?
```

**Production lesson:** Partitioning only helps when physical organization and access patterns align.

---

### Challenge 11 — UNIQUE + NULL misunderstanding

**Symptom:** Multiple NULL emails appear and the engineer assumes a unique constraint was violated.

**Root cause:** PostgreSQL default unique semantics allow multiple NULLs.

**Correction:** Decide whether the business wants:

```text
multiple NULLs
```

or:

```text
NULLS NOT DISTINCT
```

---

### Challenge 12 — Warehouse constraint not enforced

**Symptom:** A declared primary key exists but duplicate IDs are present.

**Root cause:** The analytical engine treats the key as informational.

**Corrected approach:** Add:

```sql
GROUP BY ... HAVING COUNT(*) > 1
```

tests and fail the pipeline when the invariant is violated.

---

## 70. Schema Design Challenges

### Challenge 1 — Customer table

Design:

```text
customer identity
email uniqueness
timestamps
optional fields
active status
```

Require a written rationale for each type and constraint.

---

### Challenge 2 — Orders

Design:

```text
order identity
customer relationship
money
status
created_at
```

Document:

```text
grain
primary key
foreign key
CHECK
DEFAULT
```

---

### Challenge 3 — Order lines

Design:

```text
order_id
line_number
product_id
quantity
unit_price
```

Decide whether:

```text
(order_id, line_number)
```

is the primary key.

Explain the grain.

---

### Challenge 4 — Event table

Choose:

```text
event_id
event_time
event_type
payload
```

Decide:

```text
TIMESTAMPTZ
JSONB
partitioning
required fields
```

---

### Challenge 5 — Semi-structured metadata

A marketing payload has hundreds of optional attributes.

Decide which stay in:

```text
JSONB / nested structures
```

and which should become:

```text
relational columns
```

Require explicit workload and governance reasoning.

---

### Challenge 6 — Warehouse dimension

Assume:

```text
PRIMARY KEY
UNIQUE
FOREIGN KEY
```

are informational.

Design:

```text
uniqueness tests
referential-integrity tests
status tests
required-field tests
```

---

## 71. Production Case Study

### Scenario

An e-commerce company is redesigning a PostgreSQL schema.

Current schema:

```sql
CREATE TABLE orders (
    id INT,
    customer_email VARCHAR(255),
    amount FLOAT,
    status VARCHAR(255),
    created VARCHAR(50),
    metadata TEXT
);
```

Requirements:

- millions of orders;
- exact financial amounts;
- customer relationships;
- multiple order lines;
- payment records;
- event timestamps;
- optional evolving metadata;
- reliable data-quality enforcement;
- monthly event partitioning;
- future schema evolution.

### Step 1 — Define the grain

Before writing SQL:

```text
Table:
orders

Purpose:
order header

Grain:
one row per order

Primary key:
order_id

Business key:
external_order_id where supplied

Important foreign keys:
customer_id → customers
```

For line items:

```text
Table:
order_lines

Purpose:
individual products within orders

Grain:
one row per order line

Primary key:
(order_id, line_number)

Business key:
order_id + line_number

Important foreign keys:
order_id → orders
product_id → products
```

For events:

```text
Table:
order_events

Purpose:
operational event history for orders

Grain:
one row per order event

Primary key:
event_id

Business key:
event_id or source_event_id

Important foreign keys:
order_id → orders
```

### Step 2 — Fix the money type

```text
Column:
amount

Business meaning:
financial order/payment amount

Expected values:
non-negative currency amount

Can it be NULL?
No

Expected range:
domain-dependent

Precision requirement:
exact decimal

Time-zone requirement:
not applicable

Chosen type:
NUMERIC(18,2)

Why:
exact financial semantics

Alternative:
DOUBLE PRECISION

Why not:
approximate floating-point semantics
```

### Step 3 — Fix IDs

```text
Column:
order_id

Business meaning:
internal order identity

Expected values:
monotonically generated integer identity

Can it be NULL?
No

Expected range:
large lifetime cardinality

Precision requirement:
exact integer

Chosen type:
BIGINT GENERATED ALWAYS AS IDENTITY

Why:
stable internal surrogate identity with large range

Alternative:
INTEGER

Why not:
less headroom
```

### Step 4 — Fix timestamps

```text
Column:
created_at

Business meaning:
order creation instant

Expected values:
absolute timestamp

Can it be NULL?
No

Expected range:
application lifetime

Precision requirement:
timestamp precision appropriate to event system

Time-zone requirement:
yes

Chosen type:
TIMESTAMPTZ

Why:
orders are distributed events and must represent an absolute instant

Alternative:
TIMESTAMP

Why not:
does not encode timezone-aware instant semantics
```

### Step 5 — Build customers

```sql
CREATE TABLE customers (
    customer_id BIGINT
        GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    external_customer_id TEXT
        UNIQUE,

    email TEXT
        NOT NULL
        UNIQUE,

    country_code VARCHAR(2),

    is_active BOOLEAN
        NOT NULL
        DEFAULT TRUE,

    created_at TIMESTAMPTZ
        NOT NULL
        DEFAULT CURRENT_TIMESTAMP
);
```

### Step 6 — Build products

```sql
CREATE TABLE products (
    product_id BIGINT
        GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    sku TEXT
        NOT NULL
        UNIQUE,

    product_name TEXT
        NOT NULL,

    unit_price NUMERIC(18,2)
        NOT NULL
        CHECK (unit_price >= 0),

    is_active BOOLEAN
        NOT NULL
        DEFAULT TRUE,

    created_at TIMESTAMPTZ
        NOT NULL
        DEFAULT CURRENT_TIMESTAMP
);
```

### Step 7 — Build orders

```sql
CREATE TABLE orders (
    order_id BIGINT
        GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    external_order_id TEXT
        UNIQUE,

    customer_id BIGINT
        NOT NULL,

    status TEXT
        NOT NULL
        DEFAULT 'pending',

    order_total NUMERIC(18,2)
        NOT NULL
        CHECK (order_total >= 0),

    created_at TIMESTAMPTZ
        NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ
        NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    CONSTRAINT chk_orders_status
        CHECK (status IN ('pending', 'paid', 'cancelled'))
);
```

### Step 8 — Build order lines

```sql
CREATE TABLE order_lines (
    order_id BIGINT NOT NULL,
    line_number INTEGER NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INTEGER NOT NULL
        CHECK (quantity > 0),
    unit_price NUMERIC(18,2) NOT NULL
        CHECK (unit_price >= 0),

    CONSTRAINT pk_order_lines
        PRIMARY KEY (order_id, line_number),

    CONSTRAINT fk_order_lines_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_order_lines_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);
```

### Why `ON DELETE CASCADE` here?

The business lifecycle says:

```text
order lines are owned by their order
```

If an order is intentionally removed in this particular domain, its dependent line rows should not remain independently.

That does **not** imply cascade is appropriate for every relationship.

### Step 9 — Build payments

```sql
CREATE TABLE payments (
    payment_id BIGINT
        GENERATED ALWAYS AS IDENTITY
        PRIMARY KEY,

    external_payment_id TEXT
        NOT NULL
        UNIQUE,

    order_id BIGINT
        NOT NULL,

    amount NUMERIC(18,2)
        NOT NULL
        CHECK (amount >= 0),

    status TEXT
        NOT NULL,

    processed_at TIMESTAMPTZ,

    CONSTRAINT fk_payments_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id),

    CONSTRAINT chk_payments_status
        CHECK (status IN (
            'pending',
            'authorized',
            'captured',
            'failed'
        ))
);
```

### Step 10 — Build order events

Partitioning requirement:

```text
Workload:
millions of operational order events queried by time

Partition key:
event_time

Partition grain/range:
monthly

Expected pruning predicate:
event_time >= month_start
AND event_time < next_month_start

Partition lifecycle:
create future partitions; archive/drop historical partitions according to retention

Why partitioning is justified:
large event volume, predictable time-window access, and lifecycle alignment
```

DDL:

```sql
CREATE TABLE order_events (
    event_id BIGINT
        GENERATED ALWAYS AS IDENTITY,

    order_id BIGINT NOT NULL,

    event_type TEXT NOT NULL,

    event_time TIMESTAMPTZ NOT NULL,

    payload JSONB,

    PRIMARY KEY (event_id, event_time),

    CONSTRAINT fk_order_events_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
) PARTITION BY RANGE (event_time);
```

The exact primary-key design on a partitioned table should also be reviewed against PostgreSQL's partition-key uniqueness rules and the intended identity semantics.

### Step 11 — Create monthly partitions

```sql
CREATE TABLE order_events_2026_09
PARTITION OF order_events
FOR VALUES FROM ('2026-09-01')
           TO ('2026-10-01');
```

Next month:

```sql
CREATE TABLE order_events_2026_10
PARTITION OF order_events
FOR VALUES FROM ('2026-10-01')
           TO ('2026-11-01');
```

### Step 12 — Pruning-aligned query

```sql
SELECT
    event_type,
    COUNT(*)
FROM order_events
WHERE event_time >= TIMESTAMPTZ '2026-09-01 00:00:00+00'
  AND event_time <  TIMESTAMPTZ '2026-10-01 00:00:00+00'
GROUP BY event_type;
```

The time predicate aligns with the partition boundaries.

### Step 13 — Semi-structured metadata decision

Keep:

```text
raw external attributes
```

in `payload JSONB` when they are evolving and not frequently queried.

Promote a field such as:

```text
event_type
```

to a real column because it is:

```text
stable
frequently filtered
frequently grouped
important to analytics
```

This is the “promote JSON to a real column” pattern.

### Step 14 — Naming/documentation

```sql
COMMENT ON TABLE orders
IS 'One row per customer order header.';

COMMENT ON COLUMN orders.order_total
IS 'Exact monetary order total in the system currency.';

COMMENT ON COLUMN orders.created_at
IS 'Order creation instant represented as TIMESTAMPTZ.';
```

### Step 15 — Data-quality assertions

Uniqueness:

```sql
SELECT
    external_order_id
FROM orders
WHERE external_order_id IS NOT NULL
GROUP BY external_order_id
HAVING COUNT(*) > 1;
```

Orphan customers:

```sql
SELECT
    o.order_id,
    o.customer_id
FROM orders AS o
LEFT JOIN customers AS c
    ON c.customer_id = o.customer_id
WHERE c.customer_id IS NULL;
```

Invalid statuses:

```sql
SELECT *
FROM orders
WHERE status NOT IN (
    'pending',
    'paid',
    'cancelled'
);
```

Invalid amounts:

```sql
SELECT *
FROM orders
WHERE order_total < 0;
```

### Step 16 — Future schema change example

Suppose the business wants to split a current:

```text
customer_name
```

into:

```text
first_name
last_name
```

Migration plan:

```text
Current schema:
customer_name

Desired schema:
first_name + last_name

Application dependencies:
old code reads/writes customer_name

Compatibility period:
at least one deployment cycle

Expand step:
add first_name and last_name

Data migration:
backfill where deterministic

Validation:
compare reconstructed full name where rules allow

Cutover:
new application versions read/write new columns

Contract step:
retire old column after all consumers migrate

Rollback:
retain old column during compatibility window
```

### Case-study conclusion

The redesign fixes:

```text
grain
+
identity
+
types
+
constraints
+
relationships
+
timestamps
+
semi-structured data
+
partitioning
+
documentation
+
future migrations
+
tests
```

That is what production schema design means.

---

## 72. Production Checklist

Before shipping a schema, verify:

- [ ] Table grain is explicitly known.
- [ ] Entity identity is defined.
- [ ] Primary key is intentional.
- [ ] Business/natural keys are identified.
- [ ] Surrogate key choice is justified.
- [ ] Numeric types match business semantics.
- [ ] Money uses exact decimal semantics where required.
- [ ] IDs have sufficient range.
- [ ] Timestamp types are appropriate.
- [ ] Event timestamps are timezone-aware where required.
- [ ] Required fields are `NOT NULL`.
- [ ] `UNIQUE` constraints match actual business uniqueness.
- [ ] `CHECK` constraints encode real invariants.
- [ ] Foreign-key relationships are intentional.
- [ ] `ON DELETE` behavior matches domain semantics.
- [ ] `DEFAULT` values are semantically valid.
- [ ] JSON/nested fields are used intentionally.
- [ ] Frequently used JSON attributes have been evaluated for promotion to real columns.
- [ ] Views/materialized views are chosen intentionally.
- [ ] Temporary tables are not being used as persistent schema.
- [ ] Generated columns are used only when appropriate.
- [ ] `NULL` + `UNIQUE` behavior is understood.
- [ ] `NULLS NOT DISTINCT` is deliberate where used.
- [ ] Large-table `ALTER` operations have been assessed.
- [ ] Possible table rewrites have been assessed.
- [ ] Locking/deployment risk is understood.
- [ ] Expand-and-contract is considered for breaking changes.
- [ ] Partitioning has a workload-based reason.
- [ ] Partition key and boundaries are correct.
- [ ] Queries can benefit from partition pruning where intended.
- [ ] Database/file partitioning distinction is understood.
- [ ] Analytical warehouse constraint enforcement has been verified.
- [ ] Assertion tests exist where enforcement is unavailable.
- [ ] Naming conventions are consistent.
- [ ] Important tables and columns are documented.

---

## 73. Final Knowledge Check

Complete the following without looking at the earlier examples.

### Task 1 — DDL

Create a `customers` table with:

```text
BIGINT identity primary key
email TEXT NOT NULL UNIQUE
is_active BOOLEAN NOT NULL DEFAULT TRUE
created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
```

Explain each decision.

---

### Task 2 — Schemas

Create:

```text
staging.customers
analytics.customer_summary
```

Explain why namespaces help.

---

### Task 3 — ALTER

Write SQL to:

```text
add phone
rename phone to phone_number
drop phone_number
```

Then explain why production drop operations need dependency review.

---

### Task 4 — CTAS

Create a customer-level summary from orders.

Then list which schema properties you would explicitly review before calling that CTAS result production-ready.

---

### Task 5 — Numeric types

Choose types for:

```text
quantity
order_id
amount
sensor_reading
```

Provide:

```text
business meaning
range
precision
chosen type
alternative
why not
```

---

### Task 6 — Text

Choose between:

```text
TEXT
VARCHAR(2)
VARCHAR(255)
```

for:

```text
country_code
product_description
customer_name
```

Explain which limits are actual business rules.

---

### Task 7 — Time

Choose among:

```text
DATE
TIMESTAMP
TIMESTAMPTZ
```

for:

```text
birth_date
local_store_open_time
order_event_time
```

---

### Task 8 — UUID

Design a UUID identifier for a distributed service.

Explain:

```text
generation ownership
storage considerations
interoperability
```

---

### Task 9 — Constraints

Create a table using all six required constraint concepts:

```text
PRIMARY KEY
UNIQUE
NOT NULL
CHECK
FOREIGN KEY
DEFAULT
```

Then create invalid insert attempts for each relevant rule.

---

### Task 10 — ON DELETE

Explain the difference among:

```text
NO ACTION
RESTRICT
CASCADE
SET NULL
```

and choose one for an order/order-line relationship.

---

### Task 11 — Natural vs surrogate key

Design:

```text
surrogate customer_id
+
external business identifier
```

Explain why both may be necessary.

---

### Task 12 — Identity vs SERIAL

Create one practice table with identity and one with `SERIAL`.

Explain why identity is generally the clearer modern choice.

---

### Task 13 — JSONB

Store evolving metadata in PostgreSQL `JSONB`.

Then identify a field that should become a first-class column.

---

### Task 14 — Nested analytical data

Explain when to use:

```text
DuckDB STRUCT
LIST
MAP
JSON
```

versus first-class columns.

---

### Task 15 — View vs materialized view

Given a report queried thousands of times per day, decide whether a regular view or materialized view might be more appropriate.

Explain the freshness trade-off.

---

### Task 16 — Temporary table

Use a temporary table for a multi-step debugging workflow.

Explain why it should not become a persistent contract accidentally.

---

### Task 17 — Generated column

Create:

```text
quantity
unit_price
line_total
```

where `line_total` is generated.

Explain why a default would not express the same rule.

---

### Task 18 — UNIQUE + NULL

Demonstrate PostgreSQL's default behavior:

```text
one email
NULL
NULL
```

under `UNIQUE`.

Then explain the business meaning.

---

### Task 19 — `NULLS NOT DISTINCT`

Create a PostgreSQL 15+ uniqueness rule where multiple NULLs are not permitted.

---

### Task 20 — Safe `ALTER`

Design a migration for adding a required field to a huge live table.

Answer:

```text
rewrite?
lock?
compatibility?
expand?
backfill?
validate?
cutover?
contract?
rollback?
```

---

### Task 21 — Expand-and-contract

Design the `customer_name` to `first_name`/`last_name` migration.

---

### Task 22 — Partitioning

Create a monthly range-partitioned event table.

Show:

```text
partition key
range boundaries
lifecycle
pruning predicate
```

---

### Task 23 — Partition pruning

Write a time-bounded query and explain which partitions are eligible.

---

### Task 24 — Database vs file partitioning

Compare:

```text
PostgreSQL table partitions
```

with:

```text
Parquet year/month partitions
```

---

### Task 25 — Warehouse constraints

Assume a warehouse records:

```text
PRIMARY KEY
UNIQUE
FOREIGN KEY
```

as informational.

Write explicit tests for:

```text
duplicate IDs
orphan foreign keys
```

---

### Task 26 — Naming

Rename:

```text
cust_id
dt
flag
haspayment
```

using clear semantic conventions.

---

### Task 27 — Documentation

Write `COMMENT ON` statements for a table and two important columns.

---

### Task 28 — Complete schema review

Given the bad schema:

```sql
CREATE TABLE orders (
    id INT,
    customer_email VARCHAR(255),
    amount FLOAT,
    status VARCHAR(255),
    created VARCHAR(50),
    metadata TEXT
);
```

List every design problem.

Then create the corrected production-oriented design.

---

## 74. Checkpoint — Ready for Topic 08?

You are ready to continue only when you can practically demonstrate all five capabilities.

### 1. Choose correct types for money, IDs, timestamps, and flags

You should be able to defend:

```text
money      → exact decimal when required
IDs        → sufficient integer range / UUID as justified
events     → timezone-aware timestamp when absolute instant matters
flags      → BOOLEAN
```

using semantics rather than memorized slogans.

### 2. Use all six constraint types

You should be able to explain and implement:

```text
PRIMARY KEY
UNIQUE
NOT NULL
CHECK
FOREIGN KEY
DEFAULT
```

and explain what each prevents and does not prevent.

### 3. Explain TIMESTAMP vs TIMESTAMPTZ

You should be able to answer:

```text
What does TIMESTAMP mean?
What does TIMESTAMPTZ mean in PostgreSQL?
When is a wall-clock value appropriate?
When is an absolute instant required?
```

### 4. Explain why warehouse constraints may be unenforced

You should understand:

```text
database-enforced invariant
vs
pipeline-tested invariant
```

and be able to write tests that compensate for informational constraints.

### 5. Create a partitioned table and show pruning

You should be able to:

```text
define a time-range partition key
create monthly partitions
write an aligned half-open time predicate
explain why irrelevant partitions can be pruned
```

### Practical demonstration requirement

Do not continue until you can perform the five tasks in SQL and explain the reasoning behind the DDL.

---

# Final Mental Model

For every major schema decision, use this sequence:

```text
1. What does this data mean?

2. What is one row?

3. What identifies the row?

4. Which values are valid?

5. Which values are allowed to be NULL?

6. What relationships exist?

7. What should be impossible?

8. Which type expresses the meaning?

9. Which constraint enforces the rule?

10. What happens when the schema must change?

11. Does physical layout need to support the workload?

12. If the database cannot enforce a rule, what test will?
```

Then write the DDL.

The production design chain is:

```text
business meaning
      ↓
grain
      ↓
key design
      ↓
data types
      ↓
constraints
      ↓
relationships
      ↓
physical organization
      ↓
documentation
      ↓
tests
      ↓
safe evolution
```

That is the durable skill.

---

# Common Mistakes — Final Summary

Remember these failure modes:

```text
FLOAT for exact money
→ use exact decimal semantics when required

insufficient ID range
→ choose a type with appropriate lifetime headroom

VARCHAR(255) by habit
→ use real domain limits or TEXT

timestamps as text
→ choose an actual temporal type

naive timestamps for global events
→ use timezone-aware instant semantics

missing primary keys
→ define identity

missing uniqueness
→ encode or test business uniqueness

missing NOT NULL
→ encode required fields

careless foreign keys
→ model real relationships and load implications

unsafe CASCADE
→ match deletion behavior to domain lifecycle

misleading defaults
→ do not hide missing data

NULL confused with zero
→ preserve semantics

UNIQUE + NULL misunderstood
→ understand PostgreSQL default behavior

JSON used for everything
→ promote stable operational fields

unsafe ALTER TABLE
→ assess rewrite and lock risk

assuming every ALTER rewrites
→ false

assuming no ALTER rewrites
→ false

skipping expand-and-contract
→ can break old readers/writers

partitioning without workload justification
→ creates unnecessary complexity

ignoring partition pruning
→ physical organization may not help the query

assuming warehouse constraints are enforced
→ verify and add pipeline tests

inconsistent naming
→ reduce semantic clarity

missing documentation
→ increase operational ambiguity
```

A senior Data Engineer should be able to explain not only:

```sql
CREATE TABLE ...
```

but also:

```text
Why this grain?
Why this key?
Why this type?
Why this constraint?
Why this relationship?
Why this partition?
Why this migration path?
How is the invariant tested?
```

That is Topic 07.
