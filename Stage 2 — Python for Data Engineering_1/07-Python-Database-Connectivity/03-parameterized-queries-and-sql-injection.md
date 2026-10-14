# Parameterized Queries and SQL Injection

## Learning Objectives

By the end of this module, you should be able to:

- Explain what SQL injection is and how it happens.
- Show exactly how unsafe string construction changes SQL structure.
- Explain why SQL values must be passed as parameters instead of being inserted into SQL strings.
- Explain what the database driver does with SQL text and parameter values.
- Distinguish SQL **values** from SQL **identifiers**, SQL keywords, and other structural elements.
- Use psycopg parameter placeholders correctly for values.
- Explain the five DB-API parameter styles and how they relate to drivers.
- Safely compose dynamic table names, column names, and other identifiers with `psycopg.sql`.
- Use `sql.SQL`, `sql.Identifier`, `sql.Placeholder`, `sql.Literal`, and `.join()` appropriately.
- Use allowlists to control dynamic structural choices.
- Safely handle lists of PostgreSQL values with `WHERE id = ANY(%s)`.
- Build safe literal `LIKE` searches when `%` and `_` are part of user-supplied text.
- Explain second-order SQL injection.
- Explain why parameterized storage does not guarantee safe future SQL construction.
- Apply least privilege to reduce the impact of database-access mistakes.
- Recognize injection-style risks beyond SQL.
- Review Python database code for common injection vulnerabilities.
- Design tests that prove dynamic SQL boundaries are safe.
- Defend parameterization and SQL-composition decisions in code reviews, security reviews, architecture reviews, and interviews.

---

## Prerequisites

You should already understand:

- DB-API connections and cursors from Topic 01.
- psycopg 3 connections and PostgreSQL interaction from Topic 02.
- Basic SQL syntax.
- The idea of a query placeholder.

The sequence is intentional:

```text
Topic 01
DB-API foundation
      ↓
Topic 02
psycopg + PostgreSQL
      ↓
Topic 03
Parameterized Queries + SQL Injection
      ↓
Topic 04
Transaction Control
```

Topic 02 showed how psycopg executes parameterized statements.

This topic explains **why that separation is a critical security boundary**.

> **Scope boundary:** detailed transaction engineering belongs to Topic 04, connection pooling to Topic 05, SQLAlchemy to Topics 06–07, migrations to Topic 08, bulk loading to Topic 09, and server-side cursor/streaming patterns to Topic 10.

---

# Why This Topic Matters

A data engineering system often accepts information that did not originate directly from the Python source code.

Examples include:

- API requests;
- uploaded files;
- pipeline configuration;
- metadata tables;
- command-line arguments;
- workflow parameters;
- search input;
- upstream system data;
- object-storage metadata;
- administrative forms.

That creates an important security boundary:

```text
Input
   ↓
Python program
   ↓
database query
```

The dangerous failure occurs when the application accidentally turns **data** into **SQL syntax**.

This is SQL injection.

A common misconception is:

> "It is an internal pipeline, so SQL injection does not matter."

Internal systems can still consume:

- user-controlled values;
- configuration values;
- uploaded content;
- upstream data;
- API payloads;
- values stored in metadata tables.

Internal does not automatically mean trusted.

The engineering goal is not to become suspicious of every string.

The goal is to maintain a strict boundary:

```text
SQL structure
      +
data values
```

The two must not be confused.

---

# 1. The Core Security Mental Model

The most important idea in this entire module is:

```text
A VALUE is data.

An IDENTIFIER is part of SQL structure.

A SQL KEYWORD is part of SQL grammar.

A DATABASE PERMISSION controls what the process is allowed to do.
```

That leads to four different controls:

```text
Values
   ↓
parameterize

Identifiers
   ↓
safe SQL composition + allowlist

Structural choices
   ↓
strict allowlist / validation

Database permissions
   ↓
least privilege
```

And for hostile inputs:

```text
untrusted input
      ↓
never allow data to become executable SQL structure unintentionally
```

Memorize the mental model, not a particular code snippet.

---

# 2. What Is SQL Injection?

SQL injection occurs when data-controlled text becomes part of the SQL command structure.

Suppose the application expects:

```text
name = Alice
```

and intends to execute:

```sql
SELECT id, name
FROM customers
WHERE name = 'Alice';
```

The problem begins when the application creates that SQL by directly embedding the input:

```python
query = f"""
    SELECT id, name
    FROM customers
    WHERE name = '{name}'
"""
```

The application has now mixed:

```text
SQL structure
```

with:

```text
input data
```

inside one string before PostgreSQL gets a chance to distinguish them.

That is the root problem.

---

# 3. How SQL Injection Happens

Think about two very different designs.

## 3.1 Unsafe design

```text
input
  ↓
string formatting
  ↓
one combined SQL string
  ↓
PostgreSQL parses the combined text
```

The database cannot know which characters originally came from the developer and which came from the user. Once everything has been combined into SQL text, the text is parsed as SQL.

## 3.2 Safe design

```text
SQL structure
      +
parameter value
      ↓
database driver
      ↓
PostgreSQL
```

The driver maintains the conceptual distinction between the command and its values.

That distinction is the security boundary.

---

# 4. The Vulnerable String-Formatting Pattern

## 4.1 Deliberately vulnerable training example

> ⚠️ **INTENTIONALLY VULNERABLE TRAINING EXAMPLE**
>
> Run this only against a disposable local database that you own. Never test injection payloads against systems without explicit authorization.

```python
def find_customer(conn, name: str):
    query = f"""
        SELECT id, name, email
        FROM customers
        WHERE name = '{name}'
    """

    return conn.execute(query).fetchall()
```

At first glance it appears reasonable.

Suppose:

```python
name = "Alice"
```

The Python program constructs:

```sql
SELECT id, name, email
FROM customers
WHERE name = 'Alice'
```

That may return Alice.

The problem is not that the query works.

The problem is **where the SQL grammar is decided**.

The value is inserted into the SQL source text before parsing.

---

# 5. What the Database Sees

This is the crucial exercise.

Consider:

```python
name = "Alice"
```

The application creates:

```text
"SELECT ... WHERE name = 'Alice'"
```

PostgreSQL receives SQL text where `'Alice'` is part of a valid SQL string literal.

Now imagine a controlled training input containing quote characters and SQL syntax.

The vulnerability allows the input to change the shape of the SQL text.

Conceptually:

```text
Normal value
    ↓
quoted SQL string literal

Hostile value
    ↓
can terminate the intended literal
    ↓
additional SQL grammar may follow
```

The important lesson is not the exact payload.

It is:

> **The input escaped the intended data context and entered SQL syntax.**

---

# 6. Classic Injection Patterns

The roadmap requires awareness of three classic categories:

1. boolean-bypass style input;
2. `UNION`-based data leakage;
3. destructive-statement injection.

All demonstrations below are for a disposable local training database only.

---

## 6.1 Boolean-bypass concept

A classic training input is:

```text
' OR '1'='1
```

The exact resulting SQL depends on how the vulnerable application builds the query.

The important transformation is conceptual:

```text
ordinary value
     ↓
closes the intended string
     ↓
adds a boolean condition
     ↓
changes the WHERE condition
```

The application intended:

```sql
WHERE name = '<data>'
```

but unsafe construction permits the input to participate in:

```sql
WHERE name = '<data>' OR <additional-condition>
```

The database parses the resulting SQL as grammar.

### Consequence

A search intended to find one matching customer can become much broader than intended.

### Secure fix

```python
conn.execute(
    """
    SELECT id, name, email
    FROM customers
    WHERE name = %s
    """,
    (name,),
)
```

The input is a value.

It does not become SQL structure merely because it contains quotes or SQL-looking words.

### Production rule

> Parameterize values. Do not construct SQL values with string formatting.

---

## 6.2 UNION-based data leak concept

`UNION` combines compatible result sets.

For example:

```sql
SELECT id, name
FROM customers
WHERE name = 'Alice'

UNION

SELECT id, name
FROM some_other_relation;
```

In a vulnerable application, an attacker-controlled input can sometimes alter the SQL text so that a `UNION` becomes part of the executed statement.

The security problem is:

```text
untrusted input
   ↓
SQL structure changes
   ↓
additional SELECT
   ↓
data outside intended query may become visible
```

### Why it works conceptually

`UNION` is SQL syntax.

A value parameter must remain a value.

If untrusted text is allowed to become SQL syntax, an attacker may be able to introduce operations the developer did not intend.

### Secure fix

Use parameter binding for ordinary values:

```python
conn.execute(
    """
    SELECT id, name
    FROM customers
    WHERE name = %s
    """,
    (name,),
)
```

### Production rule

> The application should decide the SQL structure. Input should supply data values.

---

## 6.3 Destructive-statement concept

Another dangerous category is input that changes SQL into a destructive statement.

The exact possibility of multiple statements depends on the database API and driver behavior.

For example, do not assume that this:

```python
cursor.execute(untrusted_sql_text)
```

means every SQL statement-delivery mode is identical across all drivers.

The important security principle is broader:

```text
If untrusted input can become SQL syntax,
the application may execute database operations
that were never intended by the developer.
```

### Consequence

The damage can include:

- modifying data;
- deleting data;
- changing schema;
- exposing data;
- causing operational disruption.

### Secure fix

Keep user-controlled values parameterized and dynamic structure tightly controlled.

### Production rule

> Do not rely on "this driver probably blocks multiple statements." Remove the injection vulnerability itself.

---

# 7. Why SQL Injection Is a Boundary Failure

Imagine SQL as a programming language.

The query contains:

```text
grammar + identifiers + operators + literals
```

A string such as:

```text
Alice
```

should be treated as **data**.

The vulnerability happens when the program lets:

```text
data
```

be interpreted as:

```text
program syntax
```

This is the same general pattern seen in other injection classes:

```text
untrusted data
      ↓
interpreted as executable syntax
```

That is why SQL injection is best understood as an **input-language boundary failure**, not just a database-specific trick.

---

# 8. Why F-Strings Are Wrong for SQL Values

Never build SQL values using:

```python
f"...{value}..."
```

or:

```python
"...%s" % value
```

or:

```python
"...{}".format(value)
```

or:

```python
"..." + value
```

For example:

```python
# ❌ UNSAFE
query = f"""
    SELECT *
    FROM users
    WHERE name = '{name}'
"""

cursor.execute(query)
```

The application has already combined the input with SQL.

The correct pattern is:

```python
# ✅ PRODUCTION-SAFE PATTERN
query = """
    SELECT *
    FROM users
    WHERE name = %s
"""

cursor.execute(query, (name,))
```

The critical difference is:

```text
UNSAFE
Python value → string formatting → final SQL text

SAFE
SQL template + parameter value → driver → database
```

---

# 9. Why Manual Quoting Is Not the Primary Defense

A common attempted fix is:

> "I will just escape the quote character myself."

Do not make that your primary defense.

Manual escaping is fragile because SQL has many contexts:

- string literals;
- identifiers;
- LIKE patterns;
- different database-specific syntaxes;
- encoding/representation rules.

Even worse, an escaping technique that is correct in one context may be incorrect in another.

The safer default is:

```text
ordinary SQL value
      ↓
driver parameter binding
```

not:

```text
ordinary SQL value
      ↓
hand-written escaping
      ↓
string concatenation
```

The database driver exists partly to manage these protocol/data-boundary details for you.

---

# 10. How Parameterized Queries Work

The central model is:

```text
SQL template
     +
parameter values
     ↓
driver
     ↓
PostgreSQL
```

Example:

```python
name = "Alice"

row = conn.execute(
    """
    SELECT id, name
    FROM customers
    WHERE name = %s
    """,
    (name,),
).fetchone()
```

There are two logical inputs:

### SQL structure

```sql
SELECT id, name
FROM customers
WHERE name = %s
```

### Parameter data

```python
(name,)
```

The driver processes them according to psycopg's parameter-binding mechanism.

The important property is that:

> **The parameter is treated as data rather than being interpreted as SQL grammar.**

---

# 11. Parameters Are Not Python `%` Formatting

This is an important beginner mistake.

Consider:

```python
query = "SELECT * FROM users WHERE name = %s"
```

Then:

```python
cursor.execute(query, (name,))
```

This is **not** equivalent to:

```python
query % name
```

The `%s` here is a psycopg parameter placeholder, not Python's string-formatting operator.

The driver owns the parameter-binding behavior.

This distinction is fundamental.

---

# 12. Parameter Placeholder Styles

DB-API supports several parameter styles.

The five standard styles are:

| Style | Example placeholder | Typical example |
|---|---|---|
| `qmark` | `?` | `sqlite3` |
| `numeric` | `:1` | Drivers that support numeric parameters |
| `named` | `:name` | Drivers that support named parameters |
| `format` | `%s` | psycopg |
| `pyformat` | `%(name)s` | psycopg |

The important point is not that every driver supports every style.

The point is:

> **Your application must use the parameter syntax required by the interface/driver being used.**

## 12.1 psycopg

Typical psycopg syntax:

```python
cursor.execute(
    "SELECT * FROM users WHERE id = %s",
    (user_id,),
)
```

Named parameters can also be used:

```python
cursor.execute(
    """
    SELECT *
    FROM users
    WHERE country = %(country)s
      AND status = %(status)s
    """,
    {
        "country": country,
        "status": status,
    },
)
```

## 12.2 sqlite3

SQLite commonly uses:

```python
cursor.execute(
    "SELECT * FROM users WHERE id = ?",
    (user_id,),
)
```

## 12.3 SQLAlchemy later

SQLAlchemy `text()` commonly uses named parameters:

```python
text(
    "SELECT * FROM users WHERE id = :user_id"
)
```

SQLAlchemy is covered in later topics.

For now, recognize that placeholder syntax belongs to the API layer rather than to Python itself.

---

# 13. Values vs SQL Structure

This is the most important practical distinction in the module.

## 13.1 Things that are normally values

These can normally be parameters:

```text
customer ID
customer name
price
country
status
date
timestamp
email
```

Examples:

```sql
WHERE customer_id = %s
WHERE amount > %s
WHERE country = %s
```

## 13.2 Things that are SQL structure

These normally cannot be passed as ordinary value placeholders:

```text
table names
column names
database names
ORDER BY direction
SQL keywords
```

For example:

```python
table_name = "customers"

# ❌ Does not mean "select from this table"
cursor.execute(
    "SELECT * FROM %s",
    (table_name,),
)
```

The placeholder represents a value.

It does not instruct PostgreSQL:

> "Interpret this value as an identifier."

Why?

Because these are different categories of SQL:

```text
value
    → data

identifier
    → name of something in SQL structure
```

That is why dynamic identifiers require another technique.

---

# 14. What Can Be Parameterized?

Typical value positions include:

```sql
WHERE customer_id = %s
WHERE amount >= %s
WHERE country = %s
```

and:

```sql
INSERT INTO customers (id, name)
VALUES (%s, %s)
```

and:

```sql
UPDATE customers
SET email = %s
WHERE id = %s
```

and:

```sql
DELETE FROM customers
WHERE id = %s
```

The pattern is:

```text
SQL structure
   ↓
written by application

data value
   ↓
provided separately
```

---

# 15. What Cannot Normally Be Parameterized as a Value?

Consider:

```text
SELECT * FROM customers
```

Now suppose the table name changes.

You cannot normally write:

```python
cursor.execute(
    "SELECT * FROM %s",
    (table_name,),
)
```

because `%s` is a **value placeholder**.

Similarly, these are structural:

```text
SELECT <column>
FROM <table>
ORDER BY <column> <direction>
```

The database needs to parse those names and keywords as SQL structure.

The application therefore needs to compose that structure safely.

---

# 16. SQL Identifiers

An **identifier** is a name used by SQL to refer to something such as:

- a table;
- a column;
- a schema;
- another database object.

Examples:

```text
customers
email
public
orders
```

A value is:

```text
"Alice"
```

A column identifier is:

```text
name
```

Those are not interchangeable.

A useful classification table:

| Item | Example | Normal value parameter? |
|---|---|---:|
| Value | `"Alice"` | Yes |
| ID value | `123` | Yes |
| Table name | `customers` | No |
| Column name | `email` | No |
| ORDER BY direction | `ASC` / `DESC` | No |
| SQL keyword | `WHERE` | No |

This table is one of the most important references in this module.

---

# 17. Safe Dynamic SQL with `psycopg.sql`

psycopg provides SQL-composition tools:

```python
from psycopg import sql
```

Important components:

```text
sql.SQL
sql.Identifier
sql.Literal
sql.Placeholder
.join()
```

They solve different problems.

The high-level model is:

```text
ordinary values
    ↓
parameters

dynamic SQL structure
    ↓
safe SQL composition
```

---

# 18. `sql.SQL`

`sql.SQL()` represents SQL text that the application itself is deliberately composing.

Example:

```python
from psycopg import sql

query = sql.SQL(
    "SELECT {fields} FROM {table}"
)
```

The braces here are composition placeholders for the `sql.SQL` object.

They are not Python f-string interpolation.

The surrounding structure should be controlled by the application.

Do not insert arbitrary untrusted SQL text directly into `sql.SQL()`.

---

# 19. `sql.Identifier`

Use `sql.Identifier()` when an application needs to insert an SQL identifier into a composed statement.

Example:

```python
from psycopg import sql

table_name = "customers"

query = sql.SQL(
    "SELECT * FROM {table}"
).format(
    table=sql.Identifier(table_name),
)
```

The important idea is:

```text
table_name
    ↓
Identifier
    ↓
SQL identifier representation
```

The application is telling psycopg:

> "This string is intended to be an identifier."

That is fundamentally different from:

```python
%s
```

which denotes a value.

---

# 20. Dynamic Column Lists

Suppose a pipeline supports a configured set of columns:

```python
columns = ["id", "name", "email"]
```

Do not do:

```python
# ❌ UNSAFE
query = (
    "SELECT "
    + ", ".join(columns)
    + " FROM customers"
)
```

The list now becomes raw SQL structure.

Instead:

```python
from psycopg import sql

column_sql = sql.SQL(", ").join(
    sql.Identifier(column)
    for column in columns
)

query = sql.SQL(
    "SELECT {columns} FROM {table}"
).format(
    columns=column_sql,
    table=sql.Identifier("customers"),
)
```

But even this is not the whole policy.

If `columns` comes from an external actor, you should also decide which columns are actually allowed.

That leads to allowlists.

---

# 21. `sql.Placeholder`

`sql.Placeholder()` can help when dynamically composing statements while keeping values parameterized.

Conceptually:

```python
from psycopg import sql

query = sql.SQL(
    "SELECT * FROM {table} WHERE {column} = {value}"
).format(
    table=sql.Identifier("customers"),
    column=sql.Identifier("country"),
    value=sql.Placeholder("country_value"),
)
```

The structural pieces are composed safely.

The actual value is supplied separately:

```python
cursor.execute(
    query,
    {"country_value": "India"},
)
```

The conceptual separation is:

```text
Identifier("customers")
    → SQL structure

Identifier("country")
    → SQL structure

Placeholder("country_value")
    → location for data

"India"
    → actual data
```

This is the boundary you must learn to see.

---

# 22. `sql.Literal`

psycopg also provides:

```python
sql.Literal(...)
```

A literal explicitly represents a value as an SQL literal for SQL composition.

Example:

```python
from psycopg import sql

query = sql.SQL(
    "SELECT * FROM customers WHERE status = {status}"
).format(
    status=sql.Literal("active"),
)
```

However:

> **Do not treat `sql.Literal()` as a reason to abandon normal parameter binding for ordinary runtime values.**

The default pattern should remain:

```text
runtime values
    ↓
parameters
```

Use SQL composition tools when you genuinely need to construct SQL structure.

---

# 23. `.join()`

A dynamic list of SQL objects can be joined using:

```python
sql.SQL(", ").join(...)
```

Example:

```python
from psycopg import sql

columns = ["id", "name", "email"]

column_sql = sql.SQL(", ").join(
    sql.Identifier(column)
    for column in columns
)
```

This produces a composable SQL fragment representing the identifiers.

The important security property is:

```text
each item
  ↓
Identifier(...)
  ↓
safe structural object
```

Do not replace this with:

```python
", ".join(raw_columns)
```

when the inputs can be controlled externally.

---

# 24. Allowlists

An **allowlist** says:

> Only explicitly approved choices are accepted.

For dynamic SQL, allowlists are extremely useful.

Example:

```python
ALLOWED_SORT_COLUMNS = {
    "name": "name",
    "created": "created_at",
    "total": "total_amount",
}
```

Then:

```python
sort_key = "created"

if sort_key not in ALLOWED_SORT_COLUMNS:
    raise ValueError("Unsupported sort field")

order_by_column = ALLOWED_SORT_COLUMNS[sort_key]
```

Now the input is not allowed to define arbitrary SQL structure.

It chooses from a controlled set.

---

# 25. Allowlist vs Validation vs Escaping vs Parameterization

These techniques solve different problems.

| Technique | Main purpose |
|---|---|
| Parameterization | Keep data values separate from SQL |
| Identifier composition | Safely represent dynamic SQL identifiers |
| Allowlisting | Restrict structural choices to approved values |
| Validation | Reject malformed or unsupported input |
| Escaping | Represent special characters safely in contexts where escaping is required |

Do not treat them as interchangeable.

For example:

```text
user asks for sort direction
    ↓
allowlist ASC / DESC

user provides customer name
    ↓
parameterize value

pipeline chooses a table
    ↓
allowlist approved tables
+
Identifier()
```

A strong security design usually combines controls.

---

# 26. Safe Dynamic SQL Builder

The roadmap requires a practical function:

```python
def export_table(
    table_name: str,
    columns: list[str],
    order_by: str,
    direction: str,
):
    ...
```

The function must control **every structural input**.

## 26.1 Unsafe implementation

> ⚠️ **INTENTIONALLY UNSAFE EXAMPLE**

```python
def export_table(conn, table_name, columns, order_by, direction):
    query = (
        f"SELECT {', '.join(columns)} "
        f"FROM {table_name} "
        f"ORDER BY {order_by} {direction}"
    )

    return conn.execute(query).fetchall()
```

Why is it dangerous?

Every parameter can affect SQL structure.

```text
table_name
columns
order_by
direction
```

are all being inserted into raw SQL text.

## 26.2 Safe design

First define explicit policy.

```python
ALLOWED_TABLES = {
    "customers": "customers",
    "orders": "orders",
    "products": "products",
}

ALLOWED_COLUMNS = {
    "customers": {"id", "name", "email", "created_at"},
    "orders": {"id", "customer_id", "total", "created_at"},
    "products": {"id", "name", "price"},
}
```

Then validate:

```python
def validate_export_request(
    table_name: str,
    columns: list[str],
    order_by: str,
    direction: str,
) -> None:
    if table_name not in ALLOWED_TABLES:
        raise ValueError("Unsupported table")

    allowed_columns = ALLOWED_COLUMNS[table_name]

    if not columns:
        raise ValueError("At least one column is required")

    if any(column not in allowed_columns for column in columns):
        raise ValueError("Unsupported column")

    if order_by not in allowed_columns:
        raise ValueError("Unsupported order_by")

    if direction.upper() not in {"ASC", "DESC"}:
        raise ValueError("Unsupported order direction")
```

Then compose the SQL:

```python
from psycopg import sql


def export_table(
    conn,
    table_name: str,
    columns: list[str],
    order_by: str,
    direction: str,
):
    validate_export_request(
        table_name,
        columns,
        order_by,
        direction,
    )

    column_sql = sql.SQL(", ").join(
        sql.Identifier(column)
        for column in columns
    )

    table_sql = sql.Identifier(
        ALLOWED_TABLES[table_name]
    )

    order_sql = sql.Identifier(order_by)

    direction_sql = sql.SQL(
        direction.upper()
    )

    query = sql.SQL(
        """
        SELECT {columns}
        FROM {table}
        ORDER BY {order_by} {direction}
        """
    ).format(
        columns=column_sql,
        table=table_sql,
        order_by=order_sql,
        direction=direction_sql,
    )

    return conn.execute(query).fetchall()
```

## 26.3 Why this is safe structurally

The logic is:

```text
1. Validate requested table
2. Validate requested columns
3. Validate requested order_by
4. Validate direction
5. Compose identifiers with Identifier()
6. Use controlled SQL for the structural keyword
7. Execute
```

There are no runtime values being inserted by f-string formatting.

## 26.4 A better architectural variation

For highly controlled applications, the allowlist can map friendly API names directly to safe SQL objects:

```python
ALLOWED_TABLES = {
    "customers": sql.Identifier("customers"),
    "orders": sql.Identifier("orders"),
}
```

The underlying principle remains:

> **External input chooses among approved structures; it does not invent SQL structure.**

---

# 27. Dynamic ORDER BY

A common mistake is:

```python
# ❌ UNSAFE
query = f"""
    SELECT *
    FROM customers
    ORDER BY {order_by} {direction}
"""
```

Both pieces affect SQL grammar.

A safe pattern is:

```python
ALLOWED_SORT_COLUMNS = {
    "name": "name",
    "created": "created_at",
    "email": "email",
}

if order_by not in ALLOWED_SORT_COLUMNS:
    raise ValueError("Unsupported sort column")

direction = direction.upper()

if direction not in {"ASC", "DESC"}:
    raise ValueError("Unsupported direction")
```

Then:

```python
query = sql.SQL(
    """
    SELECT id, name, email
    FROM customers
    ORDER BY {column} {direction}
    """
).format(
    column=sql.Identifier(
        ALLOWED_SORT_COLUMNS[order_by]
    ),
    direction=sql.SQL(direction),
)
```

The key distinction:

```text
order_by
    → identifier

direction
    → controlled SQL keyword choice
```

Neither is an ordinary value parameter.

---

# 28. Dynamic Table Names

Suppose configuration chooses:

```python
table_name = "orders"
```

You cannot use:

```python
cursor.execute(
    "SELECT * FROM %s",
    (table_name,),
)
```

Instead:

```python
from psycopg import sql

query = sql.SQL(
    "SELECT * FROM {table}"
).format(
    table=sql.Identifier(table_name),
)
```

But if `table_name` came from an external source, add an allowlist:

```python
ALLOWED_TABLES = {
    "customers",
    "orders",
    "products",
}

if table_name not in ALLOWED_TABLES:
    raise ValueError("Unsupported table")
```

Use both controls where appropriate:

```text
allowlist
+
Identifier()
```

The allowlist answers:

> Is this table allowed?

`Identifier()` answers:

> How should this approved string be represented as an SQL identifier?

Those are different questions.

---

# 29. Dynamic Column Lists

Suppose a configuration requests:

```python
columns = ["id", "name", "email"]
```

Safe composition:

```python
from psycopg import sql

column_sql = sql.SQL(", ").join(
    sql.Identifier(column)
    for column in columns
)

query = sql.SQL(
    "SELECT {columns} FROM {table}"
).format(
    columns=column_sql,
    table=sql.Identifier("customers"),
)
```

But do not skip policy:

```python
allowed = {"id", "name", "email", "created_at"}

if any(column not in allowed for column in columns):
    raise ValueError("Unsupported column")
```

This gives:

```text
policy check
    ↓
approved identifiers
    ↓
safe composition
```

---

# 30. Lists of Values with `ANY(%s)`

The roadmap requires a PostgreSQL-specific pattern for lists.

Suppose the pipeline has:

```python
ids = [10, 20, 30]
```

Do not build:

```python
# ❌ A poor pattern
id_list = ",".join(str(value) for value in ids)

query = f"""
    SELECT id, name
    FROM customers
    WHERE id IN ({id_list})
"""
```

The values have been turned into SQL text.

Instead:

```python
ids = [10, 20, 30]

rows = conn.execute(
    """
    SELECT id, name
    FROM customers
    WHERE id = ANY(%s)
    """,
    (ids,),
).fetchall()
```

The conceptual flow is:

```text
Python list
   ↓
psycopg adaptation
   ↓
PostgreSQL array value
   ↓
ANY(...)
```

## 30.1 Why `ANY(%s)`?

The expression:

```sql
id = ANY(%s)
```

asks PostgreSQL to compare the column against the elements of the provided array value.

This keeps the IDs as data.

## 30.2 Large lists

This pattern can be useful for a large set of IDs.

But there is no universal "10,000 IDs is always fine" rule.

Consider:

- parameter payload size;
- server planning;
- query selectivity;
- index use;
- memory;
- workload latency.

Very large-scale data movement belongs to later bulk-loading patterns.

---

# 31. Safe `LIKE` Searches

Parameterization solves SQL-value injection.

It does not automatically change SQL's wildcard semantics.

PostgreSQL `LIKE` uses:

```text
% = any sequence of characters
_ = exactly one character
```

Suppose the user searches for:

```text
50%
```

Do they mean:

```text
the literal characters "50%"
```

or:

```text
a LIKE wildcard pattern
```

Those are different application requirements.

---

# 32. Escaping `%` and `_`

If the requirement is:

> Search for a literal substring entered by the user.

You should escape `%` and `_`.

Example:

```python
def escape_like_literal(value: str) -> str:
    return (
        value
        .replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )
```

Then:

```python
search_text = escape_like_literal(user_input)

pattern = f"%{search_text}%"

row = conn.execute(
    """
    SELECT id, name
    FROM customers
    WHERE name LIKE %s ESCAPE '\\'
    """,
    (pattern,),
).fetchall()
```

Notice the distinction:

```text
parameterization
    ↓
keeps value separate from SQL structure

LIKE escaping
    ↓
controls wildcard semantics inside the value
```

Parameterization and wildcard escaping solve different problems.

---

# 33. SQL Injection vs LIKE Wildcards

It is important not to confuse these.

## SQL injection

Goal/problem:

```text
input becomes SQL syntax
```

Defense:

```text
parameterization / safe SQL composition
```

## Literal `LIKE` search

Goal/problem:

```text
user's % or _ becomes wildcard semantics
```

Defense:

```text
escape LIKE metacharacters
+
ESCAPE clause
+
parameterization
```

A value can be safely parameterized while still intentionally acting as a wildcard pattern.

That is not SQL injection.

---

# 34. Second-Order SQL Injection

This is one of the most important advanced concepts for Data Engineering.

## 34.1 What is it?

Second-order SQL injection occurs when a malicious value is stored as data, but later retrieved and incorrectly reused as SQL structure.

Conceptual flow:

```text
Input
  ↓
stored safely in database
  ↓
later retrieved by pipeline
  ↓
developer treats it as SQL structure
  ↓
SQL is dynamically constructed
  ↓
stored value becomes executable SQL syntax
```

The dangerous misconception is:

> "The value was safely parameterized when we stored it, so we are safe forever."

Not necessarily.

Parameterization protects the **specific execution boundary** where it is used as a value.

It does not magically mark the string as trustworthy for every future context.

---

# 35. Second-Order Injection Example

Imagine a metadata table contains:

```text
requested_table
```

A user or upstream process supplies a value.

It is safely stored:

```python
conn.execute(
    """
    INSERT INTO export_requests (requested_table)
    VALUES (%s)
    """,
    (requested_table,),
)
```

That storage operation can be correctly parameterized.

Later, another pipeline reads it:

```python
row = conn.execute(
    """
    SELECT requested_table
    FROM export_requests
    WHERE id = %s
    """,
    (request_id,),
).fetchone()
```

Now suppose a developer does:

```python
# ❌ UNSAFE
query = f"SELECT * FROM {row[0]}"
```

The previously stored value has become SQL structure.

The problem is no longer the INSERT.

The problem is the later dynamic SQL construction.

---

# 36. Defending Against Second-Order Injection

Treat stored metadata as potentially untrusted when it influences SQL structure.

For a table name:

```python
ALLOWED_TABLES = {
    "customers",
    "orders",
    "products",
}

requested_table = row["requested_table"]

if requested_table not in ALLOWED_TABLES:
    raise ValueError("Unsupported export table")

query = sql.SQL(
    "SELECT * FROM {table}"
).format(
    table=sql.Identifier(requested_table),
)
```

The full protection is:

```text
safe storage
+
safe retrieval
+
structural validation
+
allowlist
+
safe identifier composition
```

This is a major lesson for metadata-driven pipeline systems.

---

# 37. Defense in Depth

A strong security design does not depend on one technique.

Think in layers:

```text
Parameterization
      +
Safe identifier composition
      +
Allowlists
      +
Input validation
      +
Least privilege
      +
Safe logging
      +
Security tests
      +
Monitoring
```

Each control handles a different failure mode.

For example:

```text
parameterization
    → protects ordinary SQL values

Identifier()
    → safely represents approved SQL identifiers

allowlist
    → restricts structural choices

validation
    → rejects malformed/unexpected input

least privilege
    → reduces potential impact

tests
    → prove the boundary behaves as intended

monitoring
    → helps detect and diagnose unexpected activity
```

Defense in depth means:

> If one control fails or is misunderstood, another control still limits the damage.

---

# 38. Least-Privilege Database Roles

SQL injection prevention is necessary, but it is not sufficient.

Database permissions are another security boundary.

## 38.1 What is least privilege?

Least privilege means:

> Give a process only the database permissions it actually needs.

For example:

```text
read_only_extractor
    SELECT on required source tables

loader_role
    INSERT / UPDATE / DELETE on required target tables

admin_role
    administrative privileges
```

These are conceptual roles, not universal prescriptions.

## 38.2 Why does it matter?

Suppose an application is compromised by a database-access mistake.

If it has:

```text
SELECT only
```

the potential actions are narrower than if it has:

```text
superuser
```

Least privilege therefore reduces **impact**, even when prevention is imperfect.

## 38.3 Extractor role

A read-only extraction job might use a role that is permitted to:

```sql
SELECT ...
```

but not:

```sql
UPDATE ...
DELETE ...
ALTER ...
DROP ...
```

The exact grants depend on the system.

## 38.4 Do not use superuser connections for normal application code

A pipeline that only needs to read data should not normally connect using a role that can modify the entire database.

A production review should ask:

> What is the smallest useful permission set for this workload?

---

# 39. Injection Beyond SQL

The same security pattern appears elsewhere.

The general form is:

```text
untrusted data
      ↓
interpreted as executable syntax
```

Examples in Data Engineering include:

- shell command construction;
- file-path construction;
- templated SQL;
- orchestration parameters;
- dbt-style templating.

## 39.1 Shell commands

Dangerous pattern:

```python
# Conceptually unsafe
command = f"tool --input {filename}"
```

The broader lesson is the same:

```text
data becomes command syntax
```

Use argument-list APIs rather than manually constructing shell syntax where possible.

## 39.2 File paths

A string representing a path can also become dangerous if the application assumes a value is always a safe location.

The exact risks differ from SQL injection, but the mental model transfers:

> Validate where the input is allowed to point, rather than assuming the string is harmless because it came from a configuration table.

## 39.3 SQL templating

A templating engine may replace text before SQL reaches the database.

That creates another structural boundary:

```text
template rendering
      ↓
SQL text
      ↓
database
```

Be careful about which template variables are allowed to control SQL structure.

Do not confuse SQL templating with DB-API parameterization.

---

# 40. Vulnerable Local Security Lab

> ⚠️ **LOCAL TRAINING ONLY**
>
> The following lab is for a disposable PostgreSQL database you own. Do not run these experiments against production, public services, third-party systems, or any system without explicit permission.

The goal is to understand the vulnerability deeply enough to prevent it.

## 40.1 Local schema

Create a disposable table:

```sql
CREATE TABLE IF NOT EXISTS training_customers (
    id integer PRIMARY KEY,
    name text NOT NULL,
    email text NOT NULL
);

INSERT INTO training_customers (id, name, email)
VALUES
    (1, 'Alice', 'alice@example.test'),
    (2, 'Bob', 'bob@example.test'),
    (3, 'Carol', 'carol@example.test')
ON CONFLICT (id) DO NOTHING;
```

## 40.2 Intentionally vulnerable function

```python
import psycopg


def vulnerable_find_customers(conn, name: str):
    query = f"""
        SELECT id, name, email
        FROM training_customers
        WHERE name = '{name}'
    """

    return conn.execute(query).fetchall()
```

## 40.3 Prediction

Before using a normal value, predict the SQL:

```python
name = "Alice"
```

Now predict what happens when the training value contains SQL syntax.

The key question is:

> Does the value remain inside the intended SQL string literal, or can it change the SQL structure?

## 40.4 Classic boolean-bypass training input

Use a controlled training string corresponding to:

```text
' OR '1'='1
```

Observe whether the vulnerable function returns more rows than the intended search.

Record:

```text
expected behavior
actual behavior
why the SQL structure changed
```

## 40.5 UNION-based training concept

Use only your toy schema to understand the concept.

The idea is:

```text
intended SELECT
    +
attacker-controlled UNION SELECT
```

The exercise is not about building an attack tool.

The exercise is about seeing that unsafe SQL construction can let data control query structure.

## 40.6 Destructive-statement concept

Study how a vulnerable application can become dangerous when arbitrary SQL text is accepted as part of a constructed statement.

Do not assume that every driver/API allows multiple statements in the same way.

The safety lesson is independent of that implementation detail:

```text
untrusted text must never control arbitrary SQL structure
```

---

# 41. Secure Implementation

Replace the vulnerable function with:

```python
def safe_find_customers(conn, name: str):
    return conn.execute(
        """
        SELECT id, name, email
        FROM training_customers
        WHERE name = %s
        """,
        (name,),
    ).fetchall()
```

Now the same malicious-looking text is a value.

The database query structure remains:

```sql
SELECT id, name, email
FROM training_customers
WHERE name = <value>
```

The input does not become additional SQL grammar.

---

# 42. Proving the Fix

A security fix should be tested.

Do not write:

> "The code uses parameters, so it must be secure."

Write tests.

A useful proof pattern is:

```text
same normal inputs
+
same hostile-looking inputs
↓
vulnerable implementation
→ demonstrates structural change

secure implementation
→ treats inputs as values
```

For example:

```python
def test_quote_is_data(conn):
    value = "O'Reilly"

    rows = safe_find_customers(conn, value)

    # The quote is part of the value.
    # It does not terminate the SQL string.
    assert rows == []
```

For a training payload:

```python
def test_injection_string_is_data(conn):
    payload = "' OR '1'='1"

    rows = safe_find_customers(conn, payload)

    assert rows == []
```

The important assertion is not merely the row count.

The security property is:

> The input does not change the SQL structure.

---

# 43. Safe Queries Exercise

The module's main hands-on exercise is a security-focused version of `safe_queries.py`.

No additional file is required by this document. Implement the exercise in the existing lab environment.

## Objective

Build database functions that safely handle:

- ordinary values;
- dynamic identifiers;
- lists of IDs;
- search text;
- least-privilege roles.

---

## Exercise A — Vulnerable `find_customers`

Start with:

```python
def find_customers_vulnerable(conn, name: str):
    query = f"""
        SELECT id, name, email
        FROM training_customers
        WHERE name = '{name}'
    """
    return conn.execute(query).fetchall()
```

### Learner prediction

For:

```python
"O'Reilly"
```

predict what happens.

Then predict what happens with the training input:

```text
' OR '1'='1
```

### Production takeaway

Raw formatting is the wrong abstraction for SQL values.

---

## Exercise B — Safe `find_customers`

Rewrite:

```python
def find_customers_safe(conn, name: str):
    return conn.execute(
        """
        SELECT id, name, email
        FROM training_customers
        WHERE name = %s
        """,
        (name,),
    ).fetchall()
```

### Debugging question

What changed?

Answer:

```text
Not the SQL intent.

The data/SQL boundary changed.
```

---

## Exercise C — Safe export function

Implement:

```python
def export_table(
    conn,
    table_name: str,
    columns: list[str],
    order_by: str,
    direction: str,
):
    ...
```

Requirements:

- approved tables only;
- approved columns only;
- approved `ORDER BY` columns only;
- direction limited to `ASC` or `DESC`;
- dynamic identifiers use `psycopg.sql`;
- no string-formatting of SQL structure.

### Prediction before coding

Classify every argument:

```text
table_name  → identifier
columns     → identifiers
order_by    → identifier
direction   → keyword/structural choice
```

There are no ordinary runtime data values in this function yet.

---

## Exercise D — Ten-thousand-ID query

Create or generate a list of 10,000 IDs:

```python
ids = list(range(1, 10_001))
```

Use:

```sql
WHERE id = ANY(%s)
```

Do not build an SQL `IN (...)` string manually.

### Learner question

Why can a list be one parameter value while a table name cannot?

Expected reasoning:

```text
The list is data.

The table name changes SQL structure.
```

---

## Exercise E — Literal contains search

Implement:

```python
def contains_customer_name(conn, search_text: str):
    ...
```

Requirements:

- `%` and `_` in search text must be treated literally;
- use an explicit `ESCAPE` clause;
- keep the final pattern parameterized.

### Test inputs

Use values containing:

```text
%
_
\
ordinary text
quotes
SQL-like text
```

---

## Exercise F — Read-only role

Create a conceptual or local read-only role that can select from the training table but cannot update it.

Then prove:

```sql
SELECT ...
```

works while:

```sql
UPDATE ...
```

fails.

### Production takeaway

Least privilege reduces impact even when another control is bypassed or misconfigured.

---

# 44. One Coherent Safe Dynamic Query Builder

The following is the pattern you should eventually be able to explain from memory.

```python
from collections.abc import Sequence

from psycopg import sql


ALLOWED_TABLES = {
    "customers": "customers",
    "orders": "orders",
}

ALLOWED_COLUMNS = {
    "customers": {"id", "name", "email", "created_at"},
    "orders": {"id", "customer_id", "total", "created_at"},
}


def export_table(
    conn,
    table_name: str,
    columns: Sequence[str],
    order_by: str,
    direction: str,
):
    if table_name not in ALLOWED_TABLES:
        raise ValueError("Unsupported table")

    allowed_columns = ALLOWED_COLUMNS[table_name]

    if not columns:
        raise ValueError("At least one column is required")

    if any(column not in allowed_columns for column in columns):
        raise ValueError("Unsupported column")

    if order_by not in allowed_columns:
        raise ValueError("Unsupported order column")

    normalized_direction = direction.upper()

    if normalized_direction not in {"ASC", "DESC"}:
        raise ValueError("Unsupported order direction")

    selected_columns = sql.SQL(", ").join(
        sql.Identifier(column)
        for column in columns
    )

    query = sql.SQL(
        """
        SELECT {columns}
        FROM {table}
        ORDER BY {order_by} {direction}
        """
    ).format(
        columns=selected_columns,
        table=sql.Identifier(
            ALLOWED_TABLES[table_name]
        ),
        order_by=sql.Identifier(order_by),
        direction=sql.SQL(normalized_direction),
    )

    return conn.execute(query).fetchall()
```

## 44.1 Why each layer exists

### Allowlisted table

```python
if table_name not in ALLOWED_TABLES:
```

This answers:

> Is the requested table permitted at all?

### Allowlisted columns

```python
if any(column not in allowed_columns for column in columns):
```

This prevents arbitrary schema objects from becoming SQL structure.

### Direction validation

```python
if normalized_direction not in {"ASC", "DESC"}:
```

This restricts a SQL structural choice to two known possibilities.

### Identifier composition

```python
sql.Identifier(column)
```

This safely represents a column name.

### SQL structure

```python
sql.SQL(...)
```

This holds the application's intended SQL template.

The function therefore implements:

```text
policy
 ↓
validation
 ↓
safe composition
 ↓
execution
```

---

# 45. Bad vs Good Comparison Table

| Problem | Unsafe pattern | Safe pattern | Why |
|---|---|---|---|
| Value | f-string | parameter placeholder | Separates data from SQL |
| Value | `%` formatting | driver binding | Driver handles value boundary |
| Table name | raw interpolation | `Identifier()` + allowlist | Table name is SQL structure |
| Column list | `",".join(raw)` | `sql.SQL(", ").join(Identifier(...))` | Each identifier is represented safely |
| Sort column | raw string interpolation | allowlist + `Identifier()` | Structural choice must be controlled |
| Sort direction | raw user text | strict `ASC`/`DESC` allowlist | Direction is SQL grammar |
| IDs | manually built `IN (...)` text | `ANY(%s)` | IDs remain data values |
| Search text | raw pattern assembly | escaped pattern + parameter | Controls wildcard semantics |
| Stored metadata | trusted blindly | validate + allowlist before structural use | Prevents second-order injection |
| Database identity | superuser | least-privilege role | Limits impact |

Return to this table during code review.

---

# 46. Internal Mechanics — What the Database Actually Sees

Compare two designs.

## 46.1 Unsafe

```python
query = f"""
    SELECT id, name
    FROM customers
    WHERE name = '{name}'
"""

cursor.execute(query)
```

Conceptual flow:

```text
Python value
     ↓
string formatting
     ↓
one combined SQL string
     ↓
PostgreSQL parses all of it as SQL
```

At that point, PostgreSQL is not told:

> "This substring came from an untrusted value."

It simply parses SQL text.

## 46.2 Safe

```python
cursor.execute(
    """
    SELECT id, name
    FROM customers
    WHERE name = %s
    """,
    (name,),
)
```

Conceptual flow:

```text
SQL structure
      +
separate parameter value
      ↓
psycopg
      ↓
PostgreSQL
```

The driver is responsible for the parameter-binding mechanism.

## 46.3 Why this prevents ordinary value injection

Suppose:

```python
name = "Robert'); DROP TABLE customers; --"
```

With safe value binding, that string remains a value.

The characters:

```text
'
)
;
--
```

do not become SQL grammar simply because they appear inside the value.

This is the security property.

Do not reduce the explanation to:

> "The driver escapes the string."

That description is incomplete across all APIs and protocol modes.

The deeper principle is:

> **SQL structure and data values are handled as separate categories.**

---

# 47. Security Boundaries

Think in three layers.

## 47.1 Data

Examples:

```text
Alice
123
2026-01-01
India
50%
```

These are application values.

## 47.2 SQL structure

Examples:

```text
SELECT
FROM
WHERE
ORDER BY
ASC
DESC
customers
email
```

These affect SQL grammar or object selection.

## 47.3 Database permissions

Examples:

```text
SELECT
INSERT
UPDATE
DELETE
DDL permissions
```

These determine what the connected role is allowed to do.

A secure design uses the right control for the right category:

```text
Data values
    → parameterization

SQL identifiers / structure
    → safe composition + allowlist

Database capabilities
    → least privilege
```

---

# 48. Data Engineering Scenarios

## Scenario A — Customer Search

A platform provides an internal customer-search endpoint:

```text
GET /customers?name=...
```

The Python service should do:

```python
conn.execute(
    """
    SELECT id, name, email
    FROM customers
    WHERE name = %s
    """,
    (name,),
)
```

The user's name is a value.

It should never become SQL source code.

---

## Scenario B — Dynamic Table Export

An internal export job accepts:

```text
table = orders
```

The table name is not an ordinary SQL value.

Use:

```text
approved-table allowlist
+
sql.Identifier()
```

rather than:

```python
f"SELECT * FROM {table}"
```

---

## Scenario C — Metadata-Driven Pipeline

A metadata table stores:

```text
requested_table
```

A later pipeline retrieves the value and builds SQL.

This is a second-order injection boundary.

The solution is not simply:

> "It came from our database, so trust it."

Instead:

```text
stored metadata
    ↓
treat as potentially untrusted
    ↓
allowlist
    ↓
Identifier()
```

---

## Scenario D — Ten Thousand IDs

A pipeline needs orders for thousands of IDs.

Use:

```sql
WHERE id = ANY(%s)
```

with:

```python
(ids,)
```

The IDs remain data.

---

## Scenario E — Search Box

A user searches for:

```text
50%
```

The application requirement is:

> Find the literal characters `50%`.

Escape the wildcard:

```text
%
```

and:

```text
_
```

then use a parameterized `LIKE`.

---

## Scenario F — Compromised Pipeline Role

Imagine a bug allows an unintended SQL operation.

The connected role has only:

```text
SELECT
```

on the required source tables.

That reduces the possible impact compared with a superuser account.

This is why least privilege is a security control, not merely an administrative preference.

---

# 49. Debugging Exercises

## Problem 1 — Injection hidden inside an f-string

### Code

```python
def search(conn, name: str):
    query = f"""
        SELECT id, name
        FROM customers
        WHERE name = '{name}'
    """
    return conn.execute(query).fetchall()
```

### Observed behavior

A specially crafted input changes which rows are returned.

### Root cause

Input was inserted into SQL source text.

### Security problem

Data became SQL structure.

### Correct implementation

```python
return conn.execute(
    """
    SELECT id, name
    FROM customers
    WHERE name = %s
    """,
    (name,),
).fetchall()
```

### Production lesson

Parameterize values.

---

## Problem 2 — Placeholder used for table name

### Code

```python
table_name = "customers"

conn.execute(
    "SELECT * FROM %s",
    (table_name,),
)
```

### Observed behavior

The query does not interpret the parameter as a table name.

### Root cause

Value placeholders represent values, not identifiers.

### Correct implementation

```python
query = sql.SQL(
    "SELECT * FROM {table}"
).format(
    table=sql.Identifier(table_name),
)
```

Add an allowlist if the table selection is external.

### Production lesson

Identifiers are SQL structure.

---

## Problem 3 — Raw dynamic `ORDER BY`

### Code

```python
query = f"""
    SELECT id, name
    FROM customers
    ORDER BY {direction}
"""
```

### Root cause

`direction` affects SQL syntax.

### Correct implementation

```python
direction = direction.upper()

if direction not in {"ASC", "DESC"}:
    raise ValueError("Invalid direction")

query = sql.SQL(
    """
    SELECT id, name
    FROM customers
    ORDER BY name {direction}
    """
).format(
    direction=sql.SQL(direction),
)
```

### Production lesson

Use a strict allowlist for SQL keywords.

---

## Problem 4 — Unsafe dynamic column list

### Code

```python
query = (
    "SELECT "
    + ", ".join(columns)
    + " FROM customers"
)
```

### Root cause

Raw strings become SQL structure.

### Correct pattern

```python
column_sql = sql.SQL(", ").join(
    sql.Identifier(column)
    for column in columns
)
```

Then restrict columns with an allowlist.

### Production lesson

Validate first; compose second.

---

## Problem 5 — Hand-built `IN` clause

### Code

```python
id_list = ",".join(str(value) for value in ids)

query = f"""
    SELECT *
    FROM orders
    WHERE id IN ({id_list})
"""
```

### Root cause

Data was converted into SQL text.

### Correct pattern

```python
conn.execute(
    """
    SELECT *
    FROM orders
    WHERE id = ANY(%s)
    """,
    (ids,),
)
```

### Production lesson

Keep lists as values.

---

## Problem 6 — LIKE search incorrectly handles `%`

### Problem

The application intends a literal search but `%` is interpreted as a wildcard.

### Root cause

SQL wildcard semantics are distinct from injection.

### Correct pattern

```python
def escape_like_literal(value: str) -> str:
    return (
        value
        .replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )
```

Then:

```python
pattern = f"%{escape_like_literal(search_text)}%"

conn.execute(
    """
    SELECT id, name
    FROM customers
    WHERE name LIKE %s ESCAPE '\\'
    """,
    (pattern,),
)
```

### Production lesson

Parameterization and wildcard escaping solve different problems.

---

## Problem 7 — Stored metadata becomes SQL

### Observed behavior

A value stored safely in a configuration table later changes query structure.

### Root cause

The stored value was treated as SQL structure later.

### Correct approach

```text
retrieve metadata
    ↓
validate
    ↓
allowlist
    ↓
safe composition
```

### Production lesson

Safe storage does not permanently label a string as trusted SQL structure.

---

## Problem 8 — Excessive database permissions

### Observed behavior

A read-only extraction job has a role that can modify schema and data.

### Root cause

Permissions exceed workload requirements.

### Correct approach

Create a narrowly scoped extraction role.

### Production lesson

Preventing injection and limiting impact are separate controls.

---

# 50. Testing Strategy

Security behavior should be tested, not merely assumed.

The goal of tests is to prove the boundary between data and SQL structure.

## 50.1 Normal values

Test:

```text
Alice
Bob
Carol
```

## 50.2 Quotes and apostrophes

Test:

```text
O'Reilly
"quoted"
```

## 50.3 SQL-like text

Test:

```text
SELECT
DROP TABLE
UNION SELECT
```

These should remain data when passed as ordinary values.

## 50.4 Classic training inputs

Use controlled strings such as:

```text
' OR '1'='1
```

The secure function should not return unintended rows.

## 50.5 Unsupported table names

Test:

```text
unknown_table
training_customers; ...
```

The structural allowlist should reject them.

## 50.6 Unsupported columns

Test:

```text
password_hash
unknown_column
```

The allowlist should reject them.

## 50.7 Invalid direction

Test:

```text
ASC
DESC
anything-else
```

Only the approved values should pass.

## 50.8 LIKE wildcard input

Test:

```text
%
_
50%
A_B
```

Make sure literal-search semantics are preserved.

## 50.9 Large ID lists

Test:

```python
list(range(1, 10_001))
```

and confirm that the function remains parameterized.

---

# 51. Pytest Examples

These examples belong inside the learning document; no separate test file is required.

## 51.1 Value injection test

```python
def test_sql_like_text_is_data(conn):
    payload = "' OR '1'='1"

    rows = safe_find_customers(conn, payload)

    assert rows == []
```

## 51.2 Quote handling

```python
def test_apostrophe_is_data(conn):
    payload = "O'Reilly"

    rows = safe_find_customers(conn, payload)

    assert rows == []
```

## 51.3 Unsupported table

```python
import pytest


def test_unknown_table_is_rejected(conn):
    with pytest.raises(ValueError, match="Unsupported table"):
        export_table(
            conn,
            table_name="not_allowed",
            columns=["id"],
            order_by="id",
            direction="ASC",
        )
```

## 51.4 Unsupported direction

```python
def test_bad_order_direction_is_rejected(conn):
    with pytest.raises(ValueError, match="Unsupported order direction"):
        export_table(
            conn,
            table_name="customers",
            columns=["id"],
            order_by="id",
            direction="DROP",
        )
```

## 51.5 The security assertion

The most important test is conceptually:

```text
hostile-looking input
    ↓
database receives it as data
    ↓
SQL structure remains unchanged
```

A test that only verifies "the function returns a row" is not a security proof.

---

# 52. Code Review Checklist

Before approving Python database code, ask:

### Value handling

- Are SQL values parameterized?
- Is any SQL built using f-strings?
- Is `%` formatting being used on SQL?
- Is `.format()` being used on SQL?
- Is string concatenation being used to assemble query text?
- Is anyone manually quoting values?

### Identifier handling

- Are table names dynamically constructed?
- Are column names dynamically constructed?
- Are schemas dynamically selected?
- Are those names allowlisted?
- Are identifiers composed with `psycopg.sql.Identifier`?

### Structural choices

- Can external input control `ORDER BY` direction?
- Can external input control a SQL keyword?
- Can external input control a function/operator/expression?

### Lists

- Is an `IN (...)` string being built manually?
- Can values remain parameters instead?

### Search

- Are `%` and `_` intended as wildcards?
- If not, are they escaped correctly?
- Is the final pattern still parameterized?

### Stored metadata

- Could a previously stored value later become SQL structure?
- Is there a second-order injection boundary?

### Permissions

- Does the database role have more privileges than necessary?
- Is a read-only extraction role available where appropriate?
- Is application code avoiding superuser accounts?

### Testing

- Are quote and apostrophe cases tested?
- Are SQL-like values tested?
- Are classic injection training strings tested?
- Are invalid identifiers rejected?
- Are invalid structural choices rejected?

### Secrets

- Are credentials protected?
- Could an exception/log accidentally expose secrets?

A useful review rule:

> **Every place where data becomes SQL structure deserves explicit inspection.**

---

# 53. From Working Code to Secure Production Code

Security maturity can be viewed as a progression.

## Version 1 — Vulnerable

```python
query = f"""
    SELECT *
    FROM customers
    WHERE name = '{value}'
"""
```

Problem:

```text
value → SQL source
```

## Version 2 — Parameterized

```python
cursor.execute(
    """
    SELECT *
    FROM customers
    WHERE name = %s
    """,
    (value,),
)
```

Now:

```text
value → parameter
```

## Version 3 — Dynamic identifiers safely composed

```python
query = sql.SQL(
    "SELECT * FROM {table}"
).format(
    table=sql.Identifier(table_name),
)
```

Now the code has separate handling for structural names.

## Version 4 — Allowlists

```python
if table_name not in ALLOWED_TABLES:
    raise ValueError("Unsupported table")
```

Now the system controls which structures are even permitted.

## Version 5 — Least privilege + tests

Add:

```text
least-privilege database role
+
malicious-input tests
+
code-review checklist
+
monitoring
```

The mature design is:

```text
parameterize
+
compose safely
+
restrict choices
+
limit permissions
+
test
+
observe
```

---

# 54. Threat-Model Thinking

For every Python database-access function, ask these eight questions.

## 1. What inputs can be externally controlled?

Examples:

```text
API parameters
CLI arguments
uploaded files
metadata tables
workflow variables
```

## 2. Which inputs are values?

Examples:

```text
customer_id
name
country
date
amount
```

These are candidates for parameter binding.

## 3. Which inputs influence SQL structure?

Examples:

```text
table
column
sort direction
selected schema
```

These need structural controls.

## 4. Which inputs come from stored metadata?

Remember:

```text
stored ≠ automatically trusted
```

## 5. What happens if the input is malicious?

Ask:

```text
Can it change SQL?
Can it expand data access?
Can it modify data?
Can it alter schema?
Can it expose secrets?
```

## 6. What permissions does the process have?

This determines the potential impact.

## 7. How do tests prove the boundary is safe?

Security should be demonstrated.

## 8. How would operators know something unexpected happened?

Think about:

- logging;
- monitoring;
- database audit controls;
- application identifiers.

This is threat modeling applied specifically to Python → PostgreSQL data access.

---

# 55. A Senior Engineer's Review of a Dynamic SQL Function

Suppose you receive this code:

```python
def run_export(conn, table, fields, sort, direction):
    query = f"""
        SELECT {", ".join(fields)}
        FROM {table}
        ORDER BY {sort} {direction}
    """

    return conn.execute(query).fetchall()
```

Do not start by rewriting it.

First classify the inputs.

```text
table
    → identifier

fields
    → identifiers

sort
    → identifier

direction
    → SQL keyword
```

There are no ordinary data values here.

Now ask:

```text
Where is policy?
Where is validation?
Where is the allowlist?
Where is identifier composition?
```

The function has none of these controls.

A production review should therefore treat this as a structural SQL injection risk.

A safe redesign introduces:

```text
approved structures
    ↓
allowlist
    ↓
Identifier()
    ↓
controlled SQL composition
```

This is how experienced engineers reason about security: classify inputs first, then choose the correct control.

---

# 56. Architecture Question: Secure Metadata-Driven Exporter

Consider a platform where a configuration table contains:

```text
pipeline_id
table_name
columns
order_by
direction
```

A naive system might do:

```text
metadata
   ↓
f-string
   ↓
SQL
```

A safer architecture is:

```text
metadata
   ↓
load as data
   ↓
validate configuration
   ↓
allowlisted table
   ↓
allowlisted columns
   ↓
allowlisted order field
   ↓
approved direction
   ↓
psycopg.sql composition
   ↓
PostgreSQL
```

This creates a deliberate trust boundary.

The metadata becomes a **configuration language** rather than arbitrary SQL.

That distinction is important for data platforms.

---

# 57. Interview Questions

## Basic

### 1. What is SQL injection?

Explain that untrusted input becomes part of SQL command structure.

### 2. Why are f-strings dangerous in SQL?

Because the input is inserted into SQL source text before the database parses it.

### 3. What is a parameterized query?

A query where SQL structure and data values are supplied separately to the database driver.

### 4. Why are placeholders used?

To represent values separately from SQL structure.

### 5. What does a database driver do with parameters?

It implements the binding/adaptation mechanism between Python values and the database protocol.

---

## Intermediate

### 6. Why can't a table name normally be passed as a normal query parameter?

Because a value placeholder represents a data value, while a table name is SQL structure.

### 7. What is an SQL identifier?

A name used by SQL to refer to an object such as a table or column.

### 8. Why use `psycopg.sql.Identifier`?

To safely represent a dynamic identifier during SQL composition.

### 9. What is an allowlist?

A finite set of explicitly approved choices.

### 10. Why is manually quoting values dangerous?

Because quoting/escaping rules are context-sensitive and easy to implement incorrectly.

### 11. How would you safely query 10,000 IDs?

Keep the IDs as parameterized data, such as with PostgreSQL's:

```sql
WHERE id = ANY(%s)
```

---

## Advanced

### 12. Explain the difference between SQL values and SQL structure.

Values are data supplied to a statement.

Structure determines the SQL program itself.

### 13. Explain second-order SQL injection.

A value is safely stored, but later retrieved and incorrectly used as SQL structure.

### 14. Why can parameterized storage still result in an injection vulnerability later?

Because parameterization protects the specific operation where a value is bound; it does not permanently classify that string as trusted SQL structure.

### 15. When would you use `sql.SQL`, `sql.Identifier`, `sql.Placeholder`, and `sql.Literal`?

- `sql.SQL` for controlled SQL composition;
- `sql.Identifier` for dynamic SQL identifiers;
- `sql.Placeholder` when composing SQL while keeping values parameterized;
- `sql.Literal` when an SQL literal must explicitly be represented as part of composed SQL, while ordinary runtime values should normally remain parameters.

### 16. Why isn't parameterization alone enough for dynamic identifiers?

Because the placeholder mechanism represents values, not object names or SQL keywords.

### 17. Why is least privilege important even when parameterization is correctly implemented?

Because it limits the damage if another vulnerability, credential compromise, or implementation error occurs.

### 18. How would you design a secure metadata-driven extraction system?

Use:

```text
controlled configuration
+
validation
+
allowlisting
+
safe identifier composition
+
parameterized values
+
least privilege
+
security tests
+
monitoring
```

---

# 58. Architecture Questions

## 1. Design a secure Python database-access layer that supports dynamic exports.

Discuss:

```text
configuration
→ input classification
→ validation
→ allowlists
→ SQL composition
→ parameter binding
→ permission boundaries
→ tests
→ monitoring
```

## 2. How would you allow pipelines to select tables without allowing arbitrary SQL structure?

Expose a controlled logical name:

```text
"customer_export"
```

and map it to an approved database identifier:

```python
{
    "customer_export": sql.Identifier("customers")
}
```

The external caller chooses a known option rather than supplying arbitrary SQL.

## 3. How would you store configuration for dynamic extraction safely?

Store data as data.

At execution time:

```text
retrieve
→ validate
→ allowlist
→ compose safely
```

Do not treat database-stored text as trusted SQL merely because the database produced it.

## 4. How would you defend against second-order injection?

Trace every data lifecycle:

```text
input
→ storage
→ retrieval
→ interpretation
```

and inspect any point where a stored string becomes SQL structure.

## 5. How would you design database roles for extraction, transformation, loading, and administration?

Use separate roles with permissions aligned to actual work.

For example:

```text
extractor
    SELECT only

loader
    target-table write permissions

administrator
    schema/database administration
```

Exact grants must match the system.

## 6. How would you review an existing repository for SQL injection vulnerabilities?

Search for:

```text
f"..."
"...".format(...)
"...%s" % ...
"..." + variable
",".join(variable_list)
raw ORDER BY
raw table names
raw column names
```

Then trace where each input originates.

## 7. How would you test a dynamic SQL builder?

Test:

```text
valid values
valid identifiers
invalid identifiers
invalid keywords
quote characters
SQL-like text
classic injection strings
empty inputs
unexpected types
```

Then inspect both successful and rejected cases.

## 8. How would you balance flexibility and security in a pipeline framework?

Prefer controlled configuration languages over arbitrary SQL input.

For example:

```text
table: logical_table_name
columns: approved set
sort: approved field
direction: ASC/DESC
filters: parameterized values
```

This provides flexibility without granting the configuration language the full power of SQL.

## 9. What would you log when a dynamic identifier is rejected?

Useful information can include:

```text
pipeline/job identity
requested logical operation
reason for rejection
allowed category
run/correlation ID
```

Do not log sensitive input blindly.

## 10. How would you prove during a security review that values never become executable SQL syntax?

Use:

```text
code inspection
+
automated tests
+
review of query-building functions
+
input-origin tracing
+
database permissions
+
observability
```

The proof should be based on the actual implementation, not a claim that the code "uses parameters."

---

# 59. Checkpoint

Do not move on until you can perform these tasks without relying on copied examples.

## Roadmap checkpoint

- [ ] Explain SQL injection with an example.
- [ ] Pass values with placeholders in psycopg, sqlite3, and SQLAlchemy.
- [ ] Compose dynamic identifiers safely with `psycopg.sql` and an allowlist.
- [ ] Explain why a least-privilege role limits damage.

## Practical checkpoint

- [ ] Identify SQL injection in an unfamiliar Python database snippet.
- [ ] Rewrite an f-string query into a parameterized query.
- [ ] Explain why a table name cannot be a normal value parameter.
- [ ] Build a safe dynamic `SELECT`.
- [ ] Safely handle a dynamic column list.
- [ ] Safely handle `ORDER BY` direction.
- [ ] Query thousands of IDs with `ANY(%s)`.
- [ ] Escape `%` and `_` for literal `LIKE` searches.
- [ ] Explain second-order SQL injection.
- [ ] Explain defense in depth.
- [ ] Explain the difference between validation, allowlisting, escaping, and parameterization.
- [ ] Explain why least privilege matters.

## Behavioral test

Given:

```python
def export(conn, table, fields, value):
    query = f"SELECT {','.join(fields)} FROM {table} WHERE name = '{value}'"
    return conn.execute(query).fetchall()
```

You should immediately classify:

```text
table
    → identifier

fields
    → identifiers

value
    → data value
```

Then choose:

```text
table/fields
    → allowlist + Identifier()

value
    → parameter

execution
    → psycopg API
```

If you can do this reliably, you understand the core skill.

---

# 60. Common Mistakes

## Mistake 1 — "It's only internal data, so f-strings are fine."

### Beginner belief

Internal systems are trusted.

### Actual problem

Internal inputs may come from:

- users;
- upstream systems;
- metadata;
- files;
- API payloads.

### Correct pattern

Parameterize values and safely compose structure.

### Production lesson

Internal does not automatically mean trusted.

---

## Mistake 2 — Quoting values by hand

### Beginner belief

"I can add quotes around the string."

### Actual problem

SQL escaping is context-sensitive.

### Correct pattern

Use driver parameter binding.

### Production lesson

Do not hand-build SQL literals.

---

## Mistake 3 — Passing identifiers as parameters

### Beginner belief

Everything dynamic is a parameter.

### Actual problem

A table name is SQL structure, not a normal value.

### Correct pattern

Allowlist + `Identifier()`.

### Production lesson

Classify the input before choosing the API.

---

## Mistake 4 — Falling back to formatting when parameters "do not work"

### Beginner belief

"If the placeholder cannot represent this thing, I can interpolate it."

### Actual problem

You may turn untrusted text into SQL structure.

### Correct pattern

Use safe SQL composition.

### Production lesson

A limitation of value binding is not permission to use raw SQL formatting.

---

## Mistake 5 — Raw joining of columns

### Beginner belief

Column names are harmless because they "look like words."

### Actual problem

Column names are SQL syntax.

### Correct pattern

```python
sql.SQL(", ").join(
    sql.Identifier(column)
    for column in columns
)
```

plus an allowlist.

---

## Mistake 6 — Arbitrary `ORDER BY` direction

### Beginner belief

`ASC`/`DESC` is just text.

### Actual problem

It is SQL structure.

### Correct pattern

```python
if direction.upper() not in {"ASC", "DESC"}:
    raise ValueError(...)
```

---

## Mistake 7 — Assuming parameterization handles identifiers

### Beginner belief

"Everything is safe once I use `%s`."

### Actual problem

Value parameters do not represent table or column names.

### Correct pattern

Use `Identifier()` for dynamic identifiers.

---

## Mistake 8 — Assuming safely stored metadata is permanently trusted

### Beginner belief

"The database stored it, so it is safe."

### Actual problem

It can later become SQL structure.

### Correct pattern

Validate and allowlist before structural use.

---

## Mistake 9 — Manually building `IN (...)`

### Beginner belief

"Just join the IDs."

### Actual problem

Data becomes SQL text.

### Correct pattern

Use a parameterized approach such as:

```sql
WHERE id = ANY(%s)
```

---

## Mistake 10 — Forgetting LIKE wildcard semantics

### Beginner belief

"Parameterization means `%` is always literal."

### Actual problem

`%` and `_` are meaningful to `LIKE`.

### Correct pattern

Escape them when literal-search semantics are intended.

---

## Mistake 11 — Giving a pipeline a superuser account

### Beginner belief

"More permission means fewer permission errors."

### Actual problem

A compromise has a larger blast radius.

### Correct pattern

Least privilege.

---

# 61. Final Mental Model

## The Security Mental Model

```text
VALUES
   ↓
PARAMETERS


IDENTIFIERS
   ↓
SAFE SQL COMPOSITION + ALLOWLISTS


STRUCTURAL CHOICES
   ↓
ALLOWLIST / VALIDATE


DATABASE PERMISSIONS
   ↓
LEAST PRIVILEGE


STORED METADATA
   ↓
TREAT AS UNTRUSTED UNTIL VALIDATED


HOSTILE INPUT
   ↓
TEST EXPLICITLY
```

And the most important rule:

```text
Never let data become executable SQL structure unintentionally.
```

Another compact form:

```text
Parameterize values.
Safely compose identifiers.
Allowlist structural choices.
Use least privilege.
Test hostile inputs.
```

---

# 62. Final Review

## What You Now Understand

You should now understand:

- SQL injection mechanics;
- why direct string formatting is dangerous;
- parameterized queries;
- the difference between values and identifiers;
- safe SQL composition with `psycopg.sql`;
- `sql.SQL`;
- `sql.Identifier`;
- `sql.Placeholder`;
- `sql.Literal`;
- `.join()`;
- allowlists;
- dynamic table selection;
- dynamic column selection;
- safe `ORDER BY`;
- `ANY(%s)`;
- literal `LIKE` searches;
- second-order injection;
- defense in depth;
- least-privilege roles;
- injection beyond SQL.

## What You Can Implement

You should be able to:

- write safe parameterized PostgreSQL queries;
- identify vulnerable string-built SQL;
- safely build dynamic `SELECT` statements;
- validate and allowlist structural choices;
- compose dynamic identifiers with psycopg;
- safely query thousands of IDs;
- safely implement literal contains searches;
- test hostile-looking inputs;
- design a least-privilege database role.

## What You Can Debug

You should be able to diagnose:

```text
f-string SQL injection
raw dynamic table names
raw dynamic columns
unsafe ORDER BY
hand-built IN clauses
LIKE wildcard surprises
second-order SQL injection
excessive database privileges
```

The debugging method is:

```text
observed behavior
      ↓
root cause
      ↓
input classification
      ↓
correct control
      ↓
production lesson
```

## What Comes Next

The next topic is:

`04-transaction-control-from-python.md`

It focuses on:

- transaction blocks;
- savepoints;
- autocommit;
- isolation levels;
- failed transactions;
- idle-in-transaction;
- retrying serialization failures and deadlocks;
- idempotent transaction design.

Do not re-teach those subjects here.

This topic's job is to make the SQL/data boundary safe.

---

# 63. Production Rules to Remember

## Rules I should remember

1. **Never build SQL values with string formatting.**
2. **Parameterize values.**
3. **Do not treat identifiers like values.**
4. **Use `psycopg.sql.Identifier` for dynamic identifiers.**
5. **Use allowlists for dynamic structural choices.**
6. **Do not manually quote SQL values.**
7. **Use proper parameterized handling for lists.**
8. **Escape `%` and `_` when literal `LIKE` semantics are required.**
9. **Treat stored metadata as potentially untrusted when it becomes SQL structure.**
10. **Use least-privilege database roles.**
11. **Test malicious-looking inputs.**
12. **Separate SQL structure from data.**
13. **Never assume "internal" means "trusted."**
14. **Do not confuse parameterization with authorization.**
15. **Make security properties visible in code review.**

---

# 64. One-Page Engineering Summary

```text
                 PYTHON APPLICATION
                         |
                         | SQL structure
                         | +
                         | parameter values
                         v
                   PSYCOPG DRIVER
                         |
                         | safe parameter binding
                         | + SQL composition
                         v
                  POSTGRESQL SERVER
                         |
              +----------+----------+
              |                     |
          execute SQL          enforce permissions
              |                     |
              v                     v
           results              least privilege
              |
              v
        psycopg adapts values
              |
              v
        PYTHON OBJECTS
```

When reviewing code, classify each input:

```text
Is it DATA?
    → parameterize

Is it an IDENTIFIER?
    → allowlist + Identifier()

Is it a KEYWORD / structural choice?
    → strict allowlist

Is it a DATABASE CAPABILITY?
    → least privilege

Is it STORED METADATA?
    → do not assume trusted

Is it UNTRUSTED?
    → test hostile cases
```

This is the core reasoning skill Topic 03 is designed to develop.

---

# 65. Scope Boundary Before Topic 04

You should finish this topic understanding:

```text
DB-API
   ↓
psycopg 3
   ↓
parameter placeholders
   ↓
SQL values
   ↓
safe binding
   ↓
SQL identifiers
   ↓
safe composition
   ↓
allowlists
   ↓
LIKE escaping
   ↓
second-order injection
   ↓
least privilege
   ↓
security testing
```

Then Topic 04 takes the safely executed database operation and asks:

```text
What happens when multiple operations must succeed or fail together?
```

That is transaction engineering.

Keep the boundaries deliberate.

---

# 66. Final Quality Audit

Before considering Topic 03 complete, verify:

- [ ] Only `03-parameterized-queries-and-sql-injection.md` is modified.
- [ ] No other files are created or changed.
- [ ] SQL injection is explained mechanically rather than superficially.
- [ ] The vulnerable f-string pattern is demonstrated.
- [ ] The controlled training examples include the roadmap's classic categories.
- [ ] All exploit demonstrations are explicitly confined to the learner's own disposable local database.
- [ ] Parameterized queries are explained deeply.
- [ ] Parameter syntax for psycopg, sqlite3, and awareness-level SQLAlchemy is explained.
- [ ] Values and SQL structure are clearly distinguished.
- [ ] `psycopg.sql.SQL` is covered.
- [ ] `psycopg.sql.Identifier` is covered.
- [ ] `psycopg.sql.Placeholder` is covered.
- [ ] `psycopg.sql.Literal` is covered.
- [ ] `.join()` is covered.
- [ ] Allowlists are explained and demonstrated.
- [ ] Dynamic column lists are handled safely.
- [ ] Dynamic `ORDER BY` is handled safely.
- [ ] Dynamic direction is handled safely.
- [ ] `ANY(%s)` is demonstrated.
- [ ] `%` and `_` are escaped for literal LIKE searches.
- [ ] Second-order SQL injection is explained.
- [ ] Least privilege is explained.
- [ ] Read-only extraction role is discussed.
- [ ] Injection beyond SQL is discussed.
- [ ] Defense in depth is explained.
- [ ] The vulnerable local lab is included.
- [ ] The secure replacement is included.
- [ ] Security tests are included.
- [ ] Debugging exercises are included.
- [ ] The code-review checklist is included.
- [ ] Production hardening progression is included.
- [ ] Threat-model thinking is introduced.
- [ ] Interview questions are included.
- [ ] Architecture questions are included.
- [ ] The roadmap checkpoint is preserved.
- [ ] The roadmap common mistakes are preserved.
- [ ] Later topics are not re-taught.
- [ ] No universal claims are made where behavior depends on driver/database context.
- [ ] Practical examples are included for every major concept.
- [ ] The document teaches reasoning rather than memorization.

> **Most important:** this file is a complete security-focused Data Engineering learning module, not a short SQL-injection article and not a cheat sheet.

A beginner who studies it carefully and completes the exercises should be able to inspect Python database code, recognize unsafe SQL construction, explain why it is unsafe, replace it with parameterized or safely composed SQL, use allowlists for structural choices, identify second-order injection, and defend the design with least privilege and testing.
