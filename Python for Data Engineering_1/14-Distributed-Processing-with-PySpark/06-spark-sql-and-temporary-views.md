# Spark SQL and Temporary Views

## 1. Learning Objectives

By the end of this chapter, you should be able to:

1. Explain what Spark SQL is.
2. Explain why Spark SQL exists.
3. Explain how Spark SQL relates to PySpark DataFrames.
4. Explain how `SparkSession` provides access to Spark SQL.
5. Treat a DataFrame as structured data that can be exposed to SQL.
6. Create temporary views from DataFrames.
7. Distinguish `createTempView()` from `createOrReplaceTempView()`.
8. Query temporary views with `spark.sql()`.
9. Use SQL `SELECT`, `WHERE`, aliases, expressions, `CASE`, and `NULL` handling.
10. Perform foundational aggregations with `COUNT`, `SUM`, `AVG`, `MIN`, and `MAX`.
11. Use `GROUP BY`, `HAVING`, `ORDER BY`, `DISTINCT`, and `LIMIT`.
12. Understand temporary-view lifecycle and session scope.
13. Explain global temporary views and the `global_temp` namespace.
14. Move between SQL and the DataFrame API.
15. Choose SQL, DataFrame API, or a hybrid approach based on the task.
16. Explain lazy evaluation for SQL-created DataFrames.
17. Recognize common Spark SQL errors and debug them systematically.
18. Avoid unsafe or wasteful patterns such as collecting large results to the driver.
19. Write readable, maintainable Spark SQL.
20. Explain which advanced execution topics should be investigated when a Spark SQL workload becomes expensive.

---

## 2. Prerequisites

This topic follows the established Module 2.14 dependency chain:

```text
01 → Distributed Computing: Driver, Executors and Cluster Managers
02 → SparkSession, Configuration and Deploy Modes
03 → RDDs vs DataFrames
04 → Transformations, Actions and Lazy Evaluation
05 → DataFrame API: select, filter and withColumn
06 → Spark SQL and Temporary Views
07 → Joins, Shuffle and Broadcast Joins
...
```

You should already understand:

- what a Spark application is
- the role of the driver
- the role of executors
- partitions at a conceptual level
- `SparkSession`
- DataFrames
- schemas
- transformations
- actions
- lazy evaluation
- `select()`
- `filter()`
- `withColumn()`

This chapter deliberately does **not** reteach those topics in full.

The goal is to add another structured interface:

```text
DataFrame API
      +
Spark SQL
      ↓
Structured Spark transformations
```

---

# 3. What Is Spark SQL?

## Definition

**Spark SQL is Spark's structured interface for querying and transforming data using SQL and structured DataFrame operations.**

In practical terms:

> Spark SQL lets you use SQL to work with distributed Spark data.

For example:

```python
result = spark.sql("""
    SELECT
        name,
        age
    FROM people
    WHERE age >= 25
""")
```

The result is a Spark DataFrame.

```python
result.show()
```

### Mental model

```text
SQL
 ↓
Structured Spark computation
 ↓
DataFrame
 ↓
Distributed execution
```

Spark SQL is therefore not merely a string parser attached to Spark. It is a structured way to describe data transformations that Spark can execute.

---

# 4. Why Spark SQL Exists

SQL is one of the most widely used languages for data work.

Data Engineers, Analytics Engineers, Analysts, and many Data Scientists already understand concepts such as:

```text
SELECT
FROM
WHERE
GROUP BY
HAVING
ORDER BY
```

Spark SQL lets that knowledge apply to data processed by Spark.

### Problems it helps solve

Spark SQL is useful when teams need to:

- transform large datasets
- aggregate analytical data
- build reporting datasets
- prepare feature data
- investigate data quality
- perform batch transformations
- combine Python application logic with SQL transformations
- allow SQL-oriented engineers to work with Spark data

A practical pipeline might look like:

```text
Source Data
    ↓
DataFrame ingestion
    ↓
Data cleaning
    ↓
Temporary View
    ↓
Spark SQL transformation
    ↓
Result DataFrame
    ↓
Further DataFrame transformations
    ↓
Output
```

---

# 5. SQL as a Declarative Language

SQL is generally described as a **declarative language**.

Instead of writing a procedural loop such as:

```text
for every row:
    inspect age
    if age >= 25:
        keep row
```

you express the desired result:

```sql
SELECT *
FROM people
WHERE age >= 25
```

The SQL statement describes **what data is required**.

Spark is responsible for determining how the structured computation is executed.

This distinction is important:

```text
Procedural thinking:
"Do these operations one row at a time."

Declarative thinking:
"Return rows satisfying this relational condition."
```

Spark SQL uses the second style.

---

# 6. Relational Data Concepts

Spark SQL builds on familiar relational concepts.

## Table

A table is a structured collection of rows and columns.

## Row

A row represents one record.

## Column

A column represents a named field with a data type.

## Schema

A schema describes the fields and their types.

For example:

```text
name     string
age      integer
country  string
```

## Query

A query describes the desired result.

Example:

```sql
SELECT name
FROM people
WHERE age >= 25
```

## Result

The result is another structured dataset.

In PySpark:

```python
result = spark.sql(...)
```

returns a DataFrame.

---

# 7. Spark SQL vs Traditional SQL

Spark SQL uses familiar SQL concepts, but Spark is not simply a conventional relational database server.

## Traditional relational database

A simplified architecture is:

```text
Application
    ↓
Database Server
    ↓
SQL Engine
    ↓
Database-managed storage
```

Traditional relational databases commonly provide:

- persistent tables
- database-managed storage
- transactions
- indexes
- constraints
- database-specific query engines
- long-lived database objects

## Spark

A simplified conceptual architecture is:

```text
PySpark Application
        ↓
   SparkSession
        ↓
    Spark SQL
        ↓
Distributed Spark Execution
        ↓
Files / Object Storage / Databases / Other Sources
```

Spark is primarily a distributed compute engine.

Spark SQL should therefore not be understood as:

> "A complete replacement for every relational database."

Instead, think:

```text
Relational database
    → persistent transactional/analytical database system

Spark SQL
    → distributed analytical computation over structured data
```

The appropriate technology depends on the workload.

---

# 8. Spark SQL and PySpark DataFrames

Spark SQL and the DataFrame API provide different ways to express structured transformations.

For example, using the DataFrame API:

```python
from pyspark.sql import functions as F

result = (
    df
    .filter(F.col("age") >= 25)
    .select(
        "name",
        "age",
    )
)
```

Equivalent SQL can be:

```python
df.createOrReplaceTempView("people")

result = spark.sql("""
    SELECT
        name,
        age
    FROM people
    WHERE age >= 25
""")
```

Both produce a DataFrame.

### Core idea

```text
Same structured data
        ↓
 ┌───────────────┐
 │               │
DataFrame API   SQL
 │               │
 └───────┬───────┘
         ↓
    Spark DataFrame
```

The syntax is different, but the underlying structured data workflow can be closely related.

Do not assume that SQL and DataFrame code are literally identical internally in every situation. The important lesson is that both are structured interfaces to Spark computation.

---

# 9. SparkSession and Spark SQL

This topic connects directly to Topic 02.

Create a SparkSession:

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("SparkSQLDemo")
    .getOrCreate()
)
```

The `SparkSession` provides the entry point for Spark SQL functionality.

The central SQL method is:

```python
spark.sql(...)
```

Example:

```python
result = spark.sql("""
    SELECT 1 AS value
""")

result.show()
```

## What does `spark.sql()` do?

At a conceptual level:

```text
SQL string
   ↓
Spark SQL interpretation
   ↓
Structured query representation
   ↓
DataFrame result
   ↓
Action
   ↓
Execution
```

Do not jump immediately to optimizer internals.

Later:

> Topic 12 — Catalyst Optimizer and Explain Plans

will explain query planning and optimization in much greater depth.

---

# 10. A DataFrame as Structured Data

Create a DataFrame:

```python
data = [
    ("Alice", 25, "India"),
    ("Bob", 30, "USA"),
    ("Charlie", 28, "India"),
]

df = spark.createDataFrame(
    data,
    ["name", "age", "country"],
)

df.show()
df.printSchema()
```

Conceptually:

```text
+-------+---+-------+
|name   |age|country|
+-------+---+-------+
|Alice  |25 |India  |
|Bob    |30 |USA    |
|Charlie|28 |India  |
+-------+---+-------+
```

Schema:

```text
root
 |-- name: string
 |-- age: long/integer-like
 |-- country: string
```

The DataFrame already contains the structured information Spark SQL needs:

```text
columns
types
rows
```

The next step is to give the DataFrame a SQL-accessible name.

---

# 11. What Is a Temporary View?

## Definition

A temporary view gives a DataFrame a SQL-accessible name within the relevant Spark session.

The relationship is:

```text
DataFrame
    ↓
createOrReplaceTempView()
    ↓
Temporary View
    ↓
spark.sql()
    ↓
Result DataFrame
```

Example:

```python
df.createOrReplaceTempView("people")
```

Now SQL can reference:

```sql
people
```

Example:

```python
result = spark.sql("""
    SELECT *
    FROM people
""")

result.show()
```

The temporary view is not a permanent table.

It is a session-scoped SQL name associated with the DataFrame's structured data.

---

# 12. Creating a Temporary View

## `createTempView()`

```python
df.createTempView("people")
```

This registers a temporary view under the name:

```text
people
```

If the name already exists in the applicable session, attempting to create another view with the same name can result in an error rather than silently replacing it.

## `createOrReplaceTempView()`

```python
df.createOrReplaceTempView("people")
```

This registers the view and replaces an existing temporary view with that name.

This is convenient during iterative development:

```python
clean_df = ...
clean_df.createOrReplaceTempView("people")
```

You can rebuild the DataFrame and register the updated version under the same view name.

### Comparison

| API | Existing same-name temporary view |
|---|---|
| `createTempView()` | Does not silently replace it |
| `createOrReplaceTempView()` | Replaces the existing temporary view |

Use replacement intentionally. A view replacement can change what later SQL statements resolve to.

---

# 13. Querying a Temporary View

Start with:

```python
df.createOrReplaceTempView("people")
```

Then:

```python
result = spark.sql("""
    SELECT *
    FROM people
""")
```

The SQL engine resolves the name `people` through Spark's catalog/session context.

The result is a DataFrame:

```python
type(result)
```

Conceptually:

```text
DataFrame
   ↓
registered as "people"
   ↓
SQL query
   ↓
DataFrame result
```

This is one of the most useful interoperability patterns in PySpark.

---

# 14. Basic `SELECT`

Select all columns:

```sql
SELECT *
FROM people
```

Select specific columns:

```sql
SELECT
    name,
    age
FROM people
```

Select a subset and rename fields:

```sql
SELECT
    name AS customer_name,
    age AS customer_age
FROM people
```

### Production principle

Prefer explicit columns when the intended schema is known:

```sql
SELECT
    customer_id,
    order_id,
    revenue
FROM orders
```

rather than blindly propagating:

```sql
SELECT *
FROM orders
```

This makes the output contract easier to understand.

---

# 15. SQL Column Expressions

SQL can calculate derived values.

Example:

```sql
SELECT
    name,
    age,
    age + 1 AS next_age
FROM people
```

The expression:

```sql
age + 1
```

is evaluated for each applicable row.

Another example:

```sql
SELECT
    product,
    price,
    quantity,
    price * quantity AS revenue
FROM orders
```

This is conceptually similar to:

```python
df.withColumn(
    "revenue",
    F.col("price") * F.col("quantity"),
)
```

The APIs differ in syntax but express the same broad transformation intent.

---

# 16. SQL Aliases

An alias gives a selected field or expression a useful output name.

Example:

```sql
SELECT
    name AS customer_name,
    age AS customer_age
FROM people
```

Aliases improve:

- readability
- downstream schema clarity
- analytics output naming
- business-friendly datasets

For a derived expression:

```sql
SELECT
    price * quantity AS revenue
FROM orders
```

Without an alias, the generated expression name may be less useful to downstream consumers.

---

# 17. SQL Filtering with `WHERE`

The basic pattern is:

```sql
SELECT
    name,
    age
FROM people
WHERE age >= 25
```

The `WHERE` clause defines the row predicate.

Conceptually:

```text
Input rows
    ↓
WHERE predicate
    ↓
Rows satisfying condition
```

This corresponds closely to:

```python
df.filter(
    F.col("age") >= 25
)
```

---

# 18. SQL Boolean Logic

SQL uses:

```text
AND
OR
NOT
```

Example:

```sql
SELECT *
FROM people
WHERE age >= 25
  AND country = 'India'
```

OR:

```sql
SELECT *
FROM people
WHERE country = 'India'
   OR country = 'USA'
```

NOT:

```sql
SELECT *
FROM people
WHERE NOT (country = 'India')
```

Do not confuse this with the DataFrame Column API.

In Python DataFrame expressions:

```python
(F.col("age") >= 25) & (F.col("country") == "India")
```

uses:

```text
&
|
~
```

Inside SQL:

```sql
age >= 25 AND country = 'India'
```

uses SQL:

```text
AND
OR
NOT
```

The syntax differs because the expressions are written in different languages.

---

# 19. `IN`

SQL `IN` is useful for membership checks:

```sql
SELECT *
FROM people
WHERE country IN ('India', 'USA')
```

This corresponds conceptually to:

```python
df.filter(
    F.col("country").isin("India", "USA")
)
```

The same business condition can therefore be expressed through either API.

---

# 20. `BETWEEN`

Example:

```sql
SELECT *
FROM people
WHERE age BETWEEN 25 AND 35
```

`BETWEEN` expresses a range condition.

Always understand the boundary semantics relevant to the SQL dialect and data type being used rather than treating range operators as informal English.

---

# 21. `LIKE`

String pattern matching can use `LIKE`.

Example:

```sql
SELECT *
FROM people
WHERE name LIKE 'A%'
```

This means the name begins with `A` under the applicable SQL string-matching semantics.

Use it when the business rule is pattern-based rather than exact equality.

---

# 22. SQL `NULL`

`NULL` represents missing or unknown data.

It is not the same as:

```text
0
```

and not the same as:

```text
''
```

For example:

```text
age = NULL
```

does not mean age is zero.

It means the value is missing/unknown.

SQL uses three-valued logic involving:

```text
TRUE
FALSE
UNKNOWN
```

This is why null-aware predicates matter.

---

# 23. `IS NULL` and `IS NOT NULL`

Correct:

```sql
SELECT *
FROM people
WHERE country IS NULL
```

Correct:

```sql
SELECT *
FROM people
WHERE country IS NOT NULL
```

Do not write:

```sql
WHERE country = NULL
```

or:

```sql
WHERE country != NULL
```

Use the explicit null predicates.

---

# 24. `COALESCE`

`COALESCE` can provide a fallback for null values.

Example:

```sql
SELECT
    name,
    COALESCE(country, 'Unknown') AS country
FROM people
```

Conceptually:

```text
country exists
    ↓
use country

country is NULL
    ↓
use "Unknown"
```

The technical expression is straightforward.

The business decision is not.

Before replacing nulls, ask:

> Does `"Unknown"` accurately represent the meaning of missing data?

A technically convenient default can be semantically incorrect.

---

# 25. Conditional Logic with `CASE`

SQL uses `CASE` for conditional logic.

Example:

```sql
SELECT
    name,
    age,
    CASE
        WHEN age < 18 THEN 'minor'
        WHEN age < 60 THEN 'adult'
        ELSE 'senior'
    END AS age_group
FROM people
```

The structure is:

```text
CASE
    WHEN condition THEN result
    WHEN condition THEN result
    ELSE fallback
END
```

The conditions are evaluated in order.

Therefore, condition ordering matters.

---

# 26. `CASE` and the DataFrame API

The DataFrame equivalent uses `when()` and `otherwise()`:

```python
from pyspark.sql import functions as F

result = df.withColumn(
    "age_group",
    F.when(
        F.col("age") < 18,
        "minor",
    )
    .when(
        F.col("age") < 60,
        "adult",
    )
    .otherwise("senior"),
)
```

SQL:

```sql
CASE
    WHEN age < 18 THEN 'minor'
    WHEN age < 60 THEN 'adult'
    ELSE 'senior'
END
```

DataFrame API:

```python
F.when(...)
 .when(...)
 .otherwise(...)
```

Same general business transformation; different expression syntax.

---

# 27. Derived Business Columns

A realistic SQL transformation might calculate revenue:

```sql
SELECT
    customer_id,
    product,
    quantity,
    unit_price,
    quantity * unit_price AS revenue
FROM orders
```

Another might calculate tax:

```sql
SELECT
    order_id,
    revenue,
    revenue * 0.18 AS tax
FROM orders
```

Another might create a status flag:

```sql
SELECT
    order_id,
    CASE
        WHEN revenue >= 1000 THEN 'high_value'
        ELSE 'standard'
    END AS order_segment
FROM orders
```

Production caution:

> The expression is only technically correct if the business definition behind the calculation is correct.

---

# 28. Aggregation Fundamentals

Spark SQL supports foundational aggregate functions such as:

```text
COUNT
SUM
AVG
MIN
MAX
```

Example:

```sql
SELECT
    COUNT(*) AS total_people
FROM people
```

The output shape changes.

Instead of one output row per person, the result may contain a single aggregate row:

```text
+------------+
|total_people|
+------------+
|3           |
+------------+
```

---

# 29. `COUNT`

Count rows:

```sql
SELECT
    COUNT(*) AS total_people
FROM people
```

Count non-null values of a field:

```sql
SELECT
    COUNT(country) AS known_country_count
FROM people
```

These have different meanings when `country` contains nulls.

Therefore, always ask:

> Am I counting rows or non-null values of a specific expression?

---

# 30. `SUM`

Example:

```sql
SELECT
    SUM(revenue) AS total_revenue
FROM orders
```

`SUM` is useful for:

- sales totals
- quantities
- monetary metrics
- event counts represented numerically

Always understand how null values and input data types affect the result.

---

# 31. `AVG`

Example:

```sql
SELECT
    AVG(age) AS average_age
FROM people
```

`AVG` computes an average over the applicable values.

The business meaning matters.

For example:

```text
average customer age
```

may not mean the same thing as:

```text
average age across customer events
```

Aggregation logic must align with the dataset's grain.

---

# 32. `MIN` and `MAX`

Examples:

```sql
SELECT
    MIN(age) AS minimum_age,
    MAX(age) AS maximum_age
FROM people
```

These are useful for:

- range inspection
- quality checks
- temporal boundaries
- metric analysis

---

# 33. `GROUP BY`

`GROUP BY` changes the result from:

```text
one result row per source row
```

to:

```text
one result row per grouping key
```

Example:

```sql
SELECT
    country,
    COUNT(*) AS people_count
FROM people
GROUP BY country
```

If the data contains:

```text
India
India
USA
```

the output is conceptually:

```text
India → 2
USA   → 1
```

---

# 34. Grouping Key and Aggregate

This query:

```sql
SELECT
    country,
    COUNT(*) AS people_count
FROM people
GROUP BY country
```

contains two important roles:

```text
country
    ↓
grouping key

COUNT(*)
    ↓
aggregate
```

A useful mental model is:

```text
Input rows
    ↓
group by country
    ↓
one group per country
    ↓
calculate COUNT for each group
    ↓
result rows
```

---

# 35. Non-Aggregated Selected Columns

In a grouped query, selected expressions generally need to be either:

- grouping expressions, or
- aggregate expressions

For example:

```sql
SELECT
    country,
    COUNT(*) AS people_count
FROM people
GROUP BY country
```

is coherent.

But a query such as:

```sql
SELECT
    country,
    name,
    COUNT(*) AS people_count
FROM people
GROUP BY country
```

does not define which `name` should represent a group containing multiple people.

The exact error wording can vary, but the underlying problem is that the query asks for a non-grouped field whose value is not uniquely defined for each group.

---

# 36. `HAVING`

`WHERE` and `HAVING` serve different roles.

## `WHERE`

Filters rows before grouping.

```sql
SELECT
    country,
    COUNT(*) AS people_count
FROM people
WHERE age >= 25
GROUP BY country
```

## `HAVING`

Filters grouped results.

```sql
SELECT
    country,
    COUNT(*) AS people_count
FROM people
GROUP BY country
HAVING COUNT(*) >= 10
```

Mental model:

```text
Rows
 ↓
WHERE
 ↓
GROUP BY
 ↓
Aggregate
 ↓
HAVING
 ↓
Grouped result
```

This is the foundational distinction to remember.

---

# 37. `ORDER BY`

Example:

```sql
SELECT
    name,
    age
FROM people
ORDER BY age DESC
```

Ascending:

```sql
ORDER BY age ASC
```

Descending:

```sql
ORDER BY age DESC
```

Multiple columns:

```sql
SELECT
    country,
    name,
    age
FROM people
ORDER BY
    country ASC,
    age DESC
```

Ordering is useful for:

- reports
- top/bottom inspection
- deterministic presentation requirements
- exploratory analysis

At scale, ordering can be expensive. Detailed distributed ordering and shuffle mechanics are deferred to later topics.

---

# 38. `DISTINCT`

`DISTINCT` removes duplicate result rows.

Example:

```sql
SELECT DISTINCT country
FROM people
```

For multiple columns:

```sql
SELECT DISTINCT
    country,
    city
FROM customers
```

The distinctness applies to the selected combination.

This:

```sql
SELECT DISTINCT country, city
```

does not mean distinct countries independently from distinct cities. It means distinct `(country, city)` combinations.

Use `DISTINCT` intentionally. Removing duplicates may be expensive and may also hide an upstream data-quality or grain problem.

---

# 39. `LIMIT`

Example:

```sql
SELECT *
FROM people
LIMIT 10
```

`LIMIT` is useful for:

- exploration
- debugging
- sample inspection
- small interactive outputs

For example:

```python
result = spark.sql("""
    SELECT *
    FROM people
    LIMIT 20
""")

result.show(truncate=False)
```

Do not treat `LIMIT` as a universal performance guarantee.

It limits the result requested by the query, but the amount of underlying work Spark needs to perform depends on the query and data source.

---

# 40. Temporary View Lifecycle and Scope

Temporary views are associated with the Spark SQL session context.

A useful mental model is:

```text
SparkSession
     |
     +---- temporary view "people"
     |
     +---- temporary view "orders"
     |
     +---- SQL queries
```

A temporary view is not a permanent table.

Its lifecycle is tied to the applicable Spark session/application context.

When that context ends, you should not expect the temporary view to remain available as a permanent database object.

---

# 41. Checking Temporary Views

You can inspect catalog state.

For example:

```python
spark.catalog.tableExists("people")
```

can be used to check whether the named object is available in the applicable catalog context.

You can also inspect catalog information:

```python
spark.catalog.listTables()
```

Example:

```python
for table in spark.catalog.listTables():
    print(table.name, table.tableType)
```

The exact metadata fields and catalog behavior can depend on Spark version and catalog configuration, so treat this as an inspection tool rather than assuming every catalog object has identical semantics.

---

# 42. Dropping a Temporary View

Remove a temporary view with:

```python
spark.catalog.dropTempView("people")
```

After dropping it, a query such as:

```python
spark.sql("""
    SELECT *
    FROM people
""")
```

will fail because the SQL name is no longer registered.

Dropping a temporary view removes the session-level SQL registration. It is not equivalent to deleting an underlying persistent dataset.

---

# 43. `createTempView()` vs `createOrReplaceTempView()`

### `createTempView()`

Use when you want registration to fail rather than silently replace an existing view.

```python
df.createTempView("people")
```

This can be useful when duplicate registration should indicate a programming or lifecycle error.

### `createOrReplaceTempView()`

Use when the intended workflow is to refresh the SQL view definition:

```python
df.createOrReplaceTempView("people")
```

This is particularly convenient in notebooks, iterative development, and staged transformations.

The key production question is:

> Is replacement intentional?

---

# 44. Global Temporary Views

A global temporary view is a different scope mechanism.

Create one:

```python
df.createOrReplaceGlobalTempView("people")
```

Query it through the special namespace:

```python
result = spark.sql("""
    SELECT *
    FROM global_temp.people
""")
```

The important naming difference is:

```text
Temporary view:
people

Global temporary view:
global_temp.people
```

The `global_temp` namespace makes the scope explicit.

---

# 45. Why `global_temp` Is Required

When a global temporary view is created:

```python
df.createOrReplaceGlobalTempView("people")
```

the SQL reference is:

```sql
SELECT *
FROM global_temp.people
```

not:

```sql
SELECT *
FROM people
```

The namespace distinguishes the global temporary-view catalog from ordinary session-scoped temporary views.

This is one of the most common mistakes when first learning global temporary views.

---

# 46. Temporary View vs Global Temporary View

| Attribute | Temporary View | Global Temporary View |
|---|---|---|
| Creation | `createTempView()` / `createOrReplaceTempView()` | `createGlobalTempView()` / `createOrReplaceGlobalTempView()` |
| SQL name | `people` | `global_temp.people` |
| Scope | Session-scoped | Shared through the global temporary-view namespace across Spark sessions in the application context |
| Lifecycle | Temporary | Temporary |
| Persistent table? | No | No |
| Typical use | Local/session SQL transformations | Controlled cross-session temporary sharing |
| Namespace | Current session/catalog context | `global_temp` |

### Important engineering point

A global temporary view is still temporary.

It should not be treated as a durable data contract or a replacement for a persistent table or managed dataset.

---

# 47. When Global Temporary Views Can Be Useful

They can be useful when multiple Spark sessions within the same application context need to reference a temporary view through the global temporary namespace.

However, this introduces a lifecycle dependency.

Therefore, ask:

- Who owns the view?
- Who creates it?
- Who is allowed to replace it?
- When is it dropped?
- Which sessions depend on it?
- Would a persistent dataset be clearer?

Global scope can increase coordination requirements.

---

# 48. SQL and DataFrame API Interoperability

This is one of the most important production patterns.

Suppose:

```python
result = (
    df
    .filter(F.col("age") >= 25)
    .select(
        "name",
        "age",
    )
)
```

The SQL representation can be:

```python
df.createOrReplaceTempView("people")

result = spark.sql("""
    SELECT
        name,
        age
    FROM people
    WHERE age >= 25
""")
```

Both `result` objects are DataFrames.

That means you can continue using the DataFrame API after running SQL.

For example:

```python
result = spark.sql("""
    SELECT
        name,
        age
    FROM people
    WHERE age >= 25
""")

result = result.withColumn(
    "age_plus_one",
    F.col("age") + 1,
)
```

The APIs are interoperable.

---

# 49. Switching Between SQL and DataFrame APIs

A realistic hybrid flow is:

```text
DataFrame
   ↓
DataFrame API preparation
   ↓
Temporary View
   ↓
Spark SQL
   ↓
Result DataFrame
   ↓
DataFrame API
   ↓
Temporary View
   ↓
Spark SQL
```

Example:

```python
prepared = (
    raw_df
    .filter(F.col("status") == "active")
    .withColumn(
        "revenue",
        F.col("price") * F.col("quantity"),
    )
)

prepared.createOrReplaceTempView("prepared_orders")

aggregated = spark.sql("""
    SELECT
        customer_id,
        SUM(revenue) AS total_revenue
    FROM prepared_orders
    GROUP BY customer_id
""")

final_df = (
    aggregated
    .filter(F.col("total_revenue") > 1000)
)
```

This is a realistic combination:

```text
Python/DataFrame logic
        ↓
SQL analytics logic
        ↓
Python/DataFrame logic
```

---

# 50. Why Hybrid Workflows Are Common

Different parts of a team may have different strengths.

For example:

```text
Python-heavy engineers
        +
SQL-heavy analytics engineers
        +
shared Spark execution environment
```

Spark SQL lets SQL-oriented contributors express transformations in familiar syntax.

The DataFrame API makes it convenient to integrate those transformations with:

- Python functions
- configuration
- application logic
- reusable transformation code
- programmatic branching

A hybrid workflow can therefore be a maintainability decision rather than a performance contest.

---

# 51. When to Use SQL vs DataFrame API

There is no universal winner.

Use the following decision framework.

| Situation | SQL | DataFrame API | Hybrid |
|---|---|---|---|
| SQL-heavy analytical transformation | Strong fit | Possible | Possible |
| Python application integration | Possible | Strong fit | Strong fit |
| Reusable Python transformation function | Possible through generated SQL, but less direct | Strong fit | Strong fit |
| Team primarily writes SQL | Strong fit | Possible | Strong fit |
| Complex programmatic branching | Less natural | Strong fit | Strong fit |
| Clear relational aggregation | Strong fit | Strong fit | Strong fit |
| Need to combine SQL and Python logic | Possible | Possible | Strong fit |
| Shared SQL review culture | Strong fit | Possible | Strong fit |

The objective is not to rank the APIs.

The objective is to choose the representation that makes the transformation easiest to understand, maintain, test, and integrate.

---

# 52. SQL Readability and Maintainability

Production SQL should be written for the next engineer, not only for the current author.

Prefer:

```sql
SELECT
    customer_id,
    SUM(revenue) AS total_revenue
FROM orders
WHERE status = 'active'
GROUP BY customer_id
```

over an unreadable one-line query.

Good practices include:

- meaningful aliases
- explicit columns
- consistent indentation
- descriptive temporary-view names
- readable CTEs
- comments for non-obvious business rules
- avoiding unnecessary magic constants
- avoiding deeply nested expressions when a clearer structure exists

---

# 53. Common Table Expressions

A CTE can organize a SQL transformation.

Example:

```sql
WITH filtered_people AS (
    SELECT
        name,
        age,
        country
    FROM people
    WHERE age >= 25
)
SELECT
    country,
    COUNT(*) AS people_count
FROM filtered_people
GROUP BY country
```

The CTE:

```sql
filtered_people
```

gives a meaningful name to an intermediate relational result.

CTEs can improve readability when a transformation has clear logical stages.

They should not be treated as automatically materialized datasets. They are a query-organization construct.

---

# 54. Spark SQL Built-In Functions

Spark SQL provides many built-in functions.

Representative categories include:

```text
string
numeric
conditional
date/time
null-handling
```

Example:

```sql
SELECT
    UPPER(name) AS name_upper,
    TRIM(country) AS country_clean
FROM people
```

Null handling:

```sql
SELECT
    COALESCE(country, 'Unknown') AS country
FROM people
```

The goal is not to memorize every function.

Instead, learn the pattern:

```text
SQL expression
     ↓
Spark SQL built-in function
     ↓
Derived structured column
```

For exact function availability and syntax, consult the Spark version's SQL function documentation used by your project.

---

# 55. SQL Data Types

Foundational Spark SQL types include:

```text
string
integer
long
double
decimal
boolean
date
timestamp
```

Data types matter because expressions depend on type compatibility.

For example:

```sql
SELECT
    CAST(age AS INT) AS age
FROM people
```

Type conversion is useful when source data does not match the expected schema.

---

# 56. Casting and Type Mismatch

Suppose a source field arrives as text:

```text
"125.50"
```

You can cast it:

```sql
SELECT
    CAST(amount AS DOUBLE) AS amount_numeric
FROM orders
```

However, casting should not be treated as a magic data-quality fix.

Ask:

- Is the source field really numeric?
- Can invalid values occur?
- Is `DOUBLE` appropriate for the business meaning?
- Would a decimal type be more appropriate for monetary data?
- What should happen to malformed input?

Type handling is part of data-contract design.

---

# 57. Date and Timestamp Basics

Spark SQL supports date and timestamp expressions.

For example:

```sql
SELECT
    CURRENT_DATE() AS today
```

A DataFrame containing a timestamp can be queried using SQL functions appropriate to its type.

Conceptually:

```text
date
  ↓
calendar date

timestamp
  ↓
date + time
```

Do not treat a timestamp as an arbitrary string if downstream logic requires chronological operations.

Date/time parsing, formatting, and advanced temporal transformations are outside the main scope of this chapter.

---

# 58. Debugging Spark SQL: Missing View

Broken code:

```python
result = spark.sql("""
    SELECT *
    FROM customer
""")
```

But the registered view is:

```python
df.createOrReplaceTempView("customers")
```

### Problem

The query references:

```text
customer
```

while the view is:

```text
customers
```

### Fix

```python
result = spark.sql("""
    SELECT *
    FROM customers
""")
```

### Debugging approach

Inspect the catalog:

```python
spark.catalog.listTables()
```

Ask:

```text
What is the registered name?
Does the name match the SQL query?
```

---

# 59. Debugging Spark SQL: Wrong Column

Broken:

```sql
SELECT customer_name
FROM customers
```

But the schema contains:

```text
name
```

Inspect:

```python
df.printSchema()
```

or:

```python
df.columns
```

Then use the actual field:

```sql
SELECT name
FROM customers
```

Do not guess column names.

---

# 60. Debugging Spark SQL: Incorrect NULL Comparison

Broken:

```sql
SELECT *
FROM people
WHERE country = NULL
```

Correct:

```sql
SELECT *
FROM people
WHERE country IS NULL
```

Why?

Because SQL NULL represents unknown/missing data and requires null-aware predicates.

---

# 61. Debugging Spark SQL: Invalid GROUP BY

Broken:

```sql
SELECT
    country,
    name,
    COUNT(*) AS people_count
FROM people
GROUP BY country
```

Problem:

```text
country → grouped
name    → neither grouped nor aggregated
```

A group can contain multiple names, so the query does not define which name should appear.

Possible correction:

```sql
SELECT
    country,
    COUNT(*) AS people_count
FROM people
GROUP BY country
```

Or, if the business requirement genuinely needs names, redesign the aggregation appropriately.

---

# 62. Debugging Spark SQL: Wrong Alias

Suppose:

```sql
SELECT
    price * quantity AS revenue
FROM orders
```

and later code expects:

```text
total_revenue
```

The output schema contains:

```text
revenue
```

not:

```text
total_revenue
```

Use:

```sql
SELECT
    price * quantity AS total_revenue
FROM orders
```

or update the downstream reference.

Schema inspection is the fastest way to confirm the actual output:

```python
result.printSchema()
```

---

# 63. Debugging Global Temporary Views

Broken:

```python
df.createOrReplaceGlobalTempView("people")

spark.sql("""
    SELECT *
    FROM people
""")
```

Problem:

A global temporary view must be referenced through:

```text
global_temp
```

Correct:

```python
spark.sql("""
    SELECT *
    FROM global_temp.people
""")
```

Remember:

```text
temporary:
people

global temporary:
global_temp.people
```

---

# 64. Debugging Type Mismatch

Suppose:

```sql
SELECT
    price * quantity AS revenue
FROM orders
```

fails or produces unexpected behavior because the source fields are strings or contain malformed values.

Inspect:

```python
df.printSchema()
```

Then inspect sample values:

```python
df.select(
    "price",
    "quantity",
).show(truncate=False)
```

A possible standardization step is:

```sql
SELECT
    CAST(price AS DOUBLE) AS price,
    CAST(quantity AS DOUBLE) AS quantity
FROM orders
```

But verify the business and data-quality implications before relying on the cast.

---

# 65. Debugging Accidental Driver Collection

This is dangerous:

```python
rows = result.collect()
```

if `result` contains a large dataset.

`collect()` requests all result rows and brings them to the driver.

Safer inspection:

```python
result.show(20)
```

or:

```python
sample = result.limit(20).collect()
```

The second pattern still collects data to the driver, but the explicitly bounded result is much smaller.

The key question is:

> How many rows can this action return?

---

# 66. Lazy Evaluation and Spark SQL

Consider:

```python
result = spark.sql("""
    SELECT *
    FROM people
    WHERE age >= 25
""")
```

This returns a DataFrame representing the SQL result.

It does not mean that every result row has already been materialized into Python memory.

Conceptually:

```text
SQL statement
     ↓
structured transformation
     ↓
lazy computation
     ↓
action
     ↓
distributed execution
```

For example:

```python
result.show()
```

requires execution to produce rows for display.

Likewise:

```python
result.count()
```

requires execution to compute the count.

This is the direct connection to Topic 04.

---

# 67. SQL Actions

A SQL query produces a DataFrame:

```python
result = spark.sql("""
    SELECT *
    FROM people
    WHERE age >= 25
""")
```

Then actions can consume it.

### `show()`

```python
result.show()
```

Useful for inspection.

### `count()`

```python
result.count()
```

Computes the number of result rows.

### `collect()`

```python
result.collect()
```

Brings all result rows to the driver.

Use `collect()` only when the result size is known to be safely bounded.

---

# 68. Foundational Performance Awareness

This chapter is not the optimization chapter.

However, some habits should begin now.

## Select required columns

Prefer:

```sql
SELECT
    customer_id,
    revenue
FROM orders
```

when only those fields are needed.

## Filter appropriately

Use the business predicate:

```sql
WHERE status = 'active'
```

when appropriate.

## Avoid unnecessary `DISTINCT`

Ask:

> Why are duplicates being removed?

If duplicate rows indicate an upstream data-quality issue, `DISTINCT` may hide the actual problem.

## Avoid unnecessary `ORDER BY`

Ordering is useful when required, but it should not be added merely for presentation inside a large pipeline unless ordering is actually part of the requirement.

## Avoid large `collect()`

Never assume that Spark being distributed makes driver collection safe.

---

# 69. SQL and Distributed Execution

Consider:

```sql
SELECT
    country,
    COUNT(*) AS people_count
FROM people
GROUP BY country
```

Conceptually:

```text
1. Spark receives SQL.
2. Spark resolves the referenced relation/view.
3. Spark interprets the requested relational operations.
4. Spark represents the computation.
5. An action requires execution.
6. Spark executes the work through its distributed runtime.
7. A result is produced.
```

Do not infer that the SQL text itself describes individual executor operations.

SQL expresses intent.

Spark determines how that structured computation is executed.

Advanced query optimization belongs to Topic 12.

---

# 70. Production Use Case 1 — Customer Segmentation

## Problem

Create customer segments based on spending.

```sql
SELECT
    customer_id,
    CASE
        WHEN total_spend >= 10000 THEN 'high_value'
        WHEN total_spend >= 5000 THEN 'medium_value'
        ELSE 'standard'
    END AS customer_segment
FROM customers
```

## Input

```text
customer_id
total_spend
```

## Output

```text
customer_id
customer_segment
```

## Production consideration

The thresholds are business rules.

They should not be treated as universal technical constants.

---

# 71. Production Use Case 2 — Daily Sales Aggregation

Suppose orders contain:

```text
order_id
order_date
quantity
unit_price
status
```

Query:

```sql
SELECT
    order_date,
    SUM(quantity * unit_price) AS daily_revenue,
    COUNT(*) AS order_count
FROM orders
WHERE status = 'completed'
GROUP BY order_date
ORDER BY order_date
```

This creates an analytical daily summary.

Production questions:

- Is `order_date` a date or timestamp?
- What counts as `completed`?
- Are cancelled orders excluded correctly?
- Is each row truly one order?
- Is revenue defined as `quantity × unit_price`?

---

# 72. Production Use Case 3 — Event Analytics

Suppose event data contains:

```text
event_type
event_date
user_id
```

Query:

```sql
SELECT
    event_date,
    event_type,
    COUNT(*) AS event_count
FROM events
GROUP BY
    event_date,
    event_type
ORDER BY
    event_date,
    event_type
```

This can support reporting and exploratory analysis.

The important engineering consideration is dataset grain:

> What does one event row represent?

---

# 73. Production Use Case 4 — Data Quality Analysis

Find missing country values:

```sql
SELECT
    COUNT(*) AS missing_country_count
FROM customers
WHERE country IS NULL
```

Find countries and counts:

```sql
SELECT
    country,
    COUNT(*) AS row_count
FROM customers
GROUP BY country
ORDER BY row_count DESC
```

This is a practical use of Spark SQL for data-quality investigation.

---

# 74. Production Use Case 5 — ML/AI Dataset Preparation

Suppose a training dataset requires:

```text
customer_id
total_spend
order_count
customer_segment
```

A SQL transformation might produce:

```sql
SELECT
    customer_id,
    total_spend,
    order_count,
    CASE
        WHEN total_spend >= 10000 THEN 'high_value'
        WHEN total_spend >= 5000 THEN 'medium_value'
        ELSE 'standard'
    END AS customer_segment
FROM customer_metrics
```

The SQL layer can provide a structured transformation that later Python/ML code consumes as a DataFrame.

---

# 75. Mini Project — Customer Sales Analytics with Spark SQL

## Objective

Build a small end-to-end Spark SQL workflow that demonstrates:

```text
SparkSession
   ↓
DataFrame
   ↓
Schema inspection
   ↓
Temporary view
   ↓
SQL filtering
   ↓
Derived revenue
   ↓
NULL handling
   ↓
CASE
   ↓
GROUP BY
   ↓
HAVING
   ↓
ORDER BY
   ↓
LIMIT
   ↓
DataFrame API
   ↓
Second temporary view
   ↓
SQL
```

---

## Step 1 — Create SparkSession

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = (
    SparkSession.builder
    .appName("CustomerSalesAnalytics")
    .master("local[*]")
    .getOrCreate()
)
```

The SparkSession provides access to:

- DataFrame operations
- Spark SQL
- catalog/view operations

---

## Step 2 — Create Sample Data

```python
data = [
    ("C001", " Alice ", "India", "Laptop", 2, 800.0, "2026-01-10", "completed"),
    ("C002", "Bob", "USA", "Phone", 3, 500.0, "2026-01-10", "completed"),
    ("C003", "Charlie", None, "Tablet", 1, 300.0, "2026-01-11", "completed"),
    ("C001", " Alice ", "India", "Mouse", 4, 25.0, "2026-01-11", "completed"),
    ("C004", "Diana", "UK", "Monitor", 2, 250.0, "2026-01-12", "cancelled"),
]
```

Create the DataFrame:

```python
orders = spark.createDataFrame(
    data,
    [
        "customer_id",
        "customer_name",
        "country",
        "product",
        "quantity",
        "unit_price",
        "order_date",
        "status",
    ],
)
```

---

## Step 3 — Inspect Schema

```python
orders.printSchema()
```

Inspect rows:

```python
orders.show(truncate=False)
```

Before transforming, understand:

```text
field names
data types
nullability
sample values
```

---

## Step 4 — Register a Temporary View

```python
orders.createOrReplaceTempView("orders")
```

Now SQL can reference:

```text
orders
```

---

## Step 5 — Query Valid Orders

```python
valid_orders = spark.sql("""
    SELECT
        customer_id,
        TRIM(customer_name) AS customer_name,
        country,
        product,
        quantity,
        unit_price,
        order_date
    FROM orders
    WHERE status = 'completed'
""")
```

The result is a DataFrame.

```python
valid_orders.show(truncate=False)
```

---

## Step 6 — Calculate Revenue

```python
valid_orders.createOrReplaceTempView("valid_orders")
```

Then:

```python
with_revenue = spark.sql("""
    SELECT
        customer_id,
        customer_name,
        country,
        product,
        quantity,
        unit_price,
        quantity * unit_price AS revenue,
        order_date
    FROM valid_orders
""")
```

---

## Step 7 — Handle NULL Country

```python
with_revenue.createOrReplaceTempView("sales")

sales_clean = spark.sql("""
    SELECT
        customer_id,
        customer_name,
        COALESCE(country, 'Unknown') AS country,
        product,
        quantity,
        unit_price,
        revenue,
        order_date
    FROM sales
""")
```

The choice of `"Unknown"` should be validated against the business meaning of missing country.

---

## Step 8 — Create Revenue Category

```python
sales_clean.createOrReplaceTempView("sales_clean")
```

Then:

```python
categorized = spark.sql("""
    SELECT
        customer_id,
        customer_name,
        country,
        product,
        quantity,
        unit_price,
        revenue,
        CASE
            WHEN revenue >= 1000 THEN 'high'
            WHEN revenue >= 100 THEN 'medium'
            ELSE 'low'
        END AS revenue_category,
        order_date
    FROM sales_clean
""")
```

---

## Step 9 — Aggregate Customer Revenue

```python
categorized.createOrReplaceTempView("categorized_sales")

customer_summary = spark.sql("""
    SELECT
        customer_id,
        customer_name,
        country,
        SUM(revenue) AS total_revenue,
        COUNT(*) AS order_line_count
    FROM categorized_sales
    GROUP BY
        customer_id,
        customer_name,
        country
""")
```

---

## Step 10 — Apply `HAVING`

```python
customer_summary.createOrReplaceTempView("customer_summary")

high_value_customers = spark.sql("""
    SELECT
        customer_id,
        customer_name,
        country,
        total_revenue,
        order_line_count
    FROM customer_summary
    WHERE total_revenue >= 100
""")
```

Note that this uses `WHERE` because `total_revenue` is already present in the intermediate relation.

An equivalent grouped query can use `HAVING` directly:

```sql
SELECT
    customer_id,
    customer_name,
    country,
    SUM(revenue) AS total_revenue
FROM categorized_sales
GROUP BY
    customer_id,
    customer_name,
    country
HAVING SUM(revenue) >= 100
```

This is a useful opportunity to understand the distinction between filtering source rows and filtering grouped results.

---

## Step 11 — Order Results

```python
ranked_customers = spark.sql("""
    SELECT
        customer_id,
        customer_name,
        country,
        total_revenue,
        order_line_count
    FROM customer_summary
    ORDER BY total_revenue DESC
""")
```

---

## Step 12 — Limit for Inspection

```python
ranked_customers.limit(10).show(truncate=False)
```

This is useful for bounded inspection.

---

## Step 13 — Return to DataFrame API

```python
final_df = (
    ranked_customers
    .withColumn(
        "revenue_band",
        F.when(
            F.col("total_revenue") >= 1000,
            "high",
        )
        .when(
            F.col("total_revenue") >= 100,
            "medium",
        )
        .otherwise("low"),
    )
)
```

The SQL result is still a DataFrame.

---

## Step 14 — Register Another Temporary View

```python
final_df.createOrReplaceTempView("final_customer_summary")
```

Now SQL can continue:

```python
final_report = spark.sql("""
    SELECT
        country,
        revenue_band,
        COUNT(*) AS customer_count,
        SUM(total_revenue) AS revenue
    FROM final_customer_summary
    GROUP BY
        country,
        revenue_band
    ORDER BY
        country,
        revenue_band
""")
```

Inspect:

```python
final_report.show(truncate=False)
```

---

## Step 15 — Explain Execution

The important execution concept is:

```text
DataFrame creation
       ↓
View registration
       ↓
SQL transformations
       ↓
More DataFrame transformations
       ↓
More SQL
       ↓
Action
       ↓
Spark executes the required computation
```

For example:

```python
final_report.show()
```

is an action.

Until an action requires a result, the transformation chain remains lazy.

---

# 76. Hands-On Lab 1 — Create a DataFrame

## Objective

Create a DataFrame representing customers.

## Starter data

```python
data = [
    ("C001", "Alice", 25, "India"),
    ("C002", "Bob", 30, "USA"),
    ("C003", "Charlie", 28, "India"),
]
```

## Task

Create:

```text
customer_id
name
age
country
```

## Expected behavior

The DataFrame should have four columns.

## Hints

Use:

```python
spark.createDataFrame(...)
```

## Common mistakes

- wrong column count
- wrong column names
- accidentally creating a Python list instead of a DataFrame

## Verification

```python
df.printSchema()
df.show()
```

---

# 77. Hands-On Lab 2 — Create a Temporary View

## Objective

Register the DataFrame for SQL.

## Task

Create:

```text
people
```

as a temporary view.

## Expected behavior

This should work:

```python
spark.sql("""
    SELECT *
    FROM people
""").show()
```

## Hint

Use:

```python
df.createOrReplaceTempView("people")
```

## Common mistake

Querying:

```text
person
```

when the registered name is:

```text
people
```

## Verification

```python
spark.catalog.tableExists("people")
```

---

# 78. Hands-On Lab 3 — Basic SELECT

## Objective

Select a subset of columns.

## Task

Return:

```text
name
country
```

from `people`.

## Expected behavior

The result should contain only those columns.

## Hint

Use:

```sql
SELECT
    name,
    country
FROM people
```

## Common mistake

Using `SELECT *` and assuming that counts as explicit projection.

---

# 79. Hands-On Lab 4 — WHERE Filtering

## Objective

Filter rows using SQL.

## Task

Return customers with:

```text
age >= 25
```

## Expected behavior

Rows below the threshold should not appear.

## Hint

Use:

```sql
WHERE age >= 25
```

## Common mistake

Putting the condition in `HAVING` when no grouping is involved.

---

# 80. Hands-On Lab 5 — Derived Columns

## Objective

Create a calculated field.

## Task

Given:

```text
price
quantity
```

calculate:

```text
revenue
```

## Hint

Use:

```sql
price * quantity AS revenue
```

## Verification

Inspect:

```python
result.printSchema()
result.show()
```

---

# 81. Hands-On Lab 6 — CASE Expressions

## Objective

Create a category using business conditions.

## Task

Create:

```text
age_group
```

with:

```text
<18 → minor
18–59 → adult
60+ → senior
```

## Hint

Use `CASE WHEN`.

## Common mistake

Changing the condition order so that an earlier condition captures values intended for a later branch.

---

# 82. Hands-On Lab 7 — NULL Handling

## Objective

Practice null-aware SQL.

## Task

1. Find rows where country is null.
2. Create an output where null country values become `"Unknown"`.

## Hint

Use:

```sql
IS NULL
```

and:

```sql
COALESCE(...)
```

## Common mistake

Using:

```sql
country = NULL
```

---

# 83. Hands-On Lab 8 — GROUP BY and Aggregation

## Objective

Aggregate data by country.

## Task

Return:

```text
country
people_count
average_age
```

## Hint

Use:

```sql
COUNT(*)
AVG(age)
GROUP BY country
```

## Verification

Check that the result has one row per grouping key.

---

# 84. Hands-On Lab 9 — SQL/DataFrame Interoperability

## Objective

Express the same transformation using both APIs.

## Task

Create this DataFrame API transformation:

```python
df.filter(
    F.col("age") >= 25
).select(
    "name",
    "age",
)
```

Then express the same logical transformation in SQL.

## Verification

Compare:

```python
result.printSchema()
result.show()
```

for both outputs.

---

# 85. Hands-On Lab 10 — Production-Style Transformation

## Objective

Build a small transformation pipeline.

## Requirements

Given:

```text
customer_id
status
price
quantity
country
```

produce:

```text
customer_id
country
revenue
revenue_band
```

Rules:

- only active rows
- null country → `"Unknown"`
- revenue = price × quantity
- revenue >= 1000 → high
- revenue >= 100 → medium
- otherwise low

## Hint

Combine:

```text
WHERE
COALESCE
arithmetic expression
CASE
SELECT
```

## Verification

Check:

```python
result.printSchema()
result.show()
```

and explain each transformation.

---

# 86. Debugging Exercise 1 — Missing View

Broken code:

```python
df.createOrReplaceTempView("customers")

result = spark.sql("""
    SELECT *
    FROM customer
""")
```

## Diagnosis task

Identify the naming mismatch.

## Hint

Compare:

```text
customers
customer
```

## Corrected version

```python
result = spark.sql("""
    SELECT *
    FROM customers
""")
```

## Explanation

SQL must reference the registered temporary-view name.

---

# 87. Debugging Exercise 2 — Wrong Column

Broken:

```python
result = spark.sql("""
    SELECT customer_name
    FROM customers
""")
```

But the DataFrame schema contains:

```text
name
```

## Diagnosis

The query references a field not present in the relation.

## Corrected version

```sql
SELECT name
FROM customers
```

## Verification

```python
df.printSchema()
```

---

# 88. Debugging Exercise 3 — Incorrect NULL Comparison

Broken:

```sql
SELECT *
FROM customers
WHERE country = NULL
```

## Diagnosis

SQL NULL requires a null-aware predicate.

## Corrected version

```sql
SELECT *
FROM customers
WHERE country IS NULL
```

---

# 89. Debugging Exercise 4 — Invalid GROUP BY

Broken:

```sql
SELECT
    country,
    name,
    COUNT(*) AS people_count
FROM people
GROUP BY country
```

## Diagnosis task

Explain why `name` is problematic.

## Corrected version

```sql
SELECT
    country,
    COUNT(*) AS people_count
FROM people
GROUP BY country
```

If names are required, the aggregation must be redesigned around the actual business requirement.

---

# 90. Debugging Exercise 5 — Wrong Alias

Broken:

```sql
SELECT
    price * quantity AS revenue
FROM orders
```

Downstream:

```python
result.select("total_revenue")
```

## Diagnosis

The actual output column is:

```text
revenue
```

not:

```text
total_revenue
```

## Fix

Either use:

```python
result.select("revenue")
```

or create:

```sql
price * quantity AS total_revenue
```

---

# 91. Debugging Exercise 6 — Global Temporary View

Broken:

```python
df.createOrReplaceGlobalTempView("people")

result = spark.sql("""
    SELECT *
    FROM people
""")
```

## Diagnosis

The query omitted the required global temporary namespace.

## Corrected version

```python
result = spark.sql("""
    SELECT *
    FROM global_temp.people
""")
```

---

# 92. Debugging Exercise 7 — Type Mismatch

Broken:

```sql
SELECT
    price * quantity AS revenue
FROM orders
```

where both fields are strings.

## Diagnosis task

Inspect:

```python
orders.printSchema()
```

and sample values.

## Possible correction

```sql
SELECT
    CAST(price AS DOUBLE) *
    CAST(quantity AS DOUBLE) AS revenue
FROM orders
```

## Production consideration

Before applying this blindly, establish how malformed source values should be handled.

---

# 93. Debugging Exercise 8 — Accidental Driver Collection

Broken:

```python
rows = spark.sql("""
    SELECT *
    FROM huge_orders
""").collect()
```

## Diagnosis

All result rows are requested at the driver.

## Safer inspection

```python
spark.sql("""
    SELECT *
    FROM huge_orders
    LIMIT 20
""").show()
```

or:

```python
sample = (
    spark.sql("""
        SELECT *
        FROM huge_orders
    """)
    .limit(20)
    .collect()
)
```

The bounded result is still driver-side, but its size is explicitly limited.

---

# 94. SQL Readability Checklist

Before merging Spark SQL into a production pipeline, ask:

```text
Are the selected columns explicit?

Are aliases meaningful?

Are temporary-view names descriptive?

Are business rules easy to locate?

Are NULL rules explicit?

Are magic constants documented?

Is the query formatted consistently?

Would another engineer understand the grain?

Is the query mixing too many responsibilities?

Would a CTE improve readability?

Are intermediate dependencies obvious?

Is the output schema understood?
```

Readable SQL is an engineering asset.

---

# 95. Production Engineering Guidance

## Naming

Prefer:

```text
customer_orders
active_orders
customer_summary
daily_sales
```

over:

```text
tmp1
data2
x
test_view
```

Names should communicate meaning.

## Lifecycle

Know:

```text
who creates the view
who consumes it
who replaces it
when it disappears
```

## Hidden dependencies

Avoid pipelines where SQL silently depends on a temporary view created somewhere unrelated.

A temporary view is a runtime dependency.

## Schema awareness

Know:

```text
field names
types
grain
nullability assumptions
```

## Validation

At minimum, inspect:

```python
result.printSchema()
result.show()
```

and validate important business assumptions.

## Logging

Production applications should make major transformation stages observable through appropriate application logging and job monitoring.

Detailed Spark UI debugging belongs to Topic 15.

---

# 96. Common Spark SQL Mistakes

## Mistake 1 — Treating a temporary view as a permanent table

Temporary views are temporary SQL registrations.

They are not durable storage.

## Mistake 2 — Assuming Spark SQL is a relational database

Spark SQL is part of a distributed compute engine.

## Mistake 3 — Assuming `spark.sql()` immediately materializes everything

The returned DataFrame remains subject to Spark's lazy execution model.

## Mistake 4 — Assuming SQL is always faster than DataFrame API

There is no general rule that one API is inherently faster.

## Mistake 5 — Treating SQL and DataFrame APIs as unrelated engines

They are interoperable structured APIs within Spark.

## Mistake 6 — Collecting large SQL results

```python
result.collect()
```

can overwhelm driver memory.

## Mistake 7 — Forgetting `global_temp`

Global temporary views require the appropriate namespace:

```sql
global_temp.view_name
```

## Mistake 8 — Assuming LIMIT guarantees trivial execution

`LIMIT` bounds the requested result, but does not mean the underlying computation is always free or limited to exactly the number of source rows requested.

---

# 97. Common Misconceptions

### Misconception 1

> "A temporary view is a permanent table."

**Correction:** It is a temporary SQL-accessible name associated with structured Spark data.

### Misconception 2

> "Spark SQL means Spark is a relational database."

**Correction:** Spark is a distributed compute engine that provides SQL and structured DataFrame interfaces.

### Misconception 3

> "`spark.sql()` immediately executes everything."

**Correction:** It returns a DataFrame representing the query result; execution remains subject to Spark's lazy model until an action requires a result.

### Misconception 4

> "SQL always performs better than the DataFrame API."

**Correction:** Do not make an unconditional performance claim based only on API syntax.

### Misconception 5

> "The DataFrame API and Spark SQL use completely separate execution systems."

**Correction:** They are interoperable structured interfaces within Spark.

### Misconception 6

> "`collect()` is safe because Spark is distributed."

**Correction:** `collect()` moves the entire result to the driver.

### Misconception 7

> "A global temporary view is a permanent shared table."

**Correction:** It is temporary and has a specific global temporary-view namespace.

### Misconception 8

> "LIMIT means Spark never needs to process the underlying data."

**Correction:** The required work depends on the query, data source, and execution requirements.

---

# 98. Forward Connections to Later Topics

Spark SQL is the beginning of a larger execution story.

When a SQL query becomes expensive, later topics become relevant:

```text
Spark SQL
    ↓
07 Joins / Shuffle / Broadcast
    ↓
08 Partitioning
    ↓
09 Data Skew / Salting
    ↓
10 Caching / Persistence
    ↓
11 UDFs / pandas UDFs / Built-ins
    ↓
12 Catalyst / Explain Plans
    ↓
13 AQE
    ↓
15 Spark UI / Slow Job Debugging
```

Do not prematurely optimize a SQL query by guessing at these topics.

First understand:

```text
what the query means
what data it consumes
what result it should produce
```

Then use the appropriate advanced topic when performance or execution behavior requires deeper investigation.

---

# 99. Learning Checkpoints

## Checkpoint 1 — Spark SQL

Can you explain:

> What is Spark SQL?

A strong answer should mention:

```text
SQL
+
structured Spark data
+
distributed computation
```

---

## Checkpoint 2 — Temporary Views

Can you explain:

> What does `createOrReplaceTempView()` do?

A strong answer should mention:

```text
DataFrame
→ SQL-accessible name
→ temporary/session scope
```

---

## Checkpoint 3 — SQL Query

Can you write:

```sql
SELECT
    name,
    age
FROM people
WHERE age >= 25
```

and explain every clause?

---

## Checkpoint 4 — Scope

Can you explain the difference between:

```text
people
```

and:

```text
global_temp.people
```

?

---

## Checkpoint 5 — WHERE vs HAVING

Can you explain:

```text
WHERE → row filtering
HAVING → grouped-result filtering
```

?

---

## Checkpoint 6 — NULL

Can you explain why:

```sql
country = NULL
```

is not the correct null test?

---

## Checkpoint 7 — Interoperability

Can you convert this:

```python
df.filter(
    F.col("age") >= 25
).select(
    "name",
    "age",
)
```

into SQL?

---

## Checkpoint 8 — Lazy Evaluation

Can you explain why:

```python
result = spark.sql(...)
```

and:

```python
result.show()
```

play different roles?

---

## Checkpoint 9 — Driver Safety

Can you explain why:

```python
result.collect()
```

can be dangerous?

---

## Checkpoint 10 — Production Choice

Can you explain when SQL, DataFrame API, or a hybrid approach would be appropriate?

---

# 100. Interview Questions

## Basic

### 1. What is Spark SQL?

**Answer:**  
Spark SQL is Spark's structured interface for querying and transforming distributed data using SQL and interoperable DataFrame operations.

### 2. What is a temporary view?

**Answer:**  
A temporary view gives a DataFrame a SQL-accessible name within the applicable Spark session context.

### 3. What does `spark.sql()` return?

**Answer:**  
It returns a Spark DataFrame representing the query result.

### 4. How does a DataFrame relate to a temporary view?

**Answer:**  
A DataFrame can be registered under a temporary view name, allowing SQL to reference that structured data.

### 5. What is `SparkSession`'s role?

**Answer:**  
It provides the application-level entry point for Spark functionality, including Spark SQL operations through `spark.sql()` and catalog/view access.

---

## Intermediate

### 6. Temporary view vs global temporary view?

**Answer:**  
A temporary view is session-scoped. A global temporary view is exposed through the `global_temp` namespace and is intended for the broader global temporary-view scope available within the application context.

### 7. What is the difference between `createTempView()` and `createOrReplaceTempView()`?

**Answer:**  
`createTempView()` does not silently replace an existing same-name temporary view, while `createOrReplaceTempView()` explicitly replaces the existing temporary view.

### 8. Why use temporary views?

**Answer:**  
They provide a convenient SQL-accessible name for structured DataFrame data without requiring a persistent table.

### 9. What is the difference between WHERE and HAVING?

**Answer:**  
`WHERE` filters source rows before grouping, while `HAVING` filters grouped results after aggregation.

### 10. Why is `IS NULL` used instead of `= NULL`?

**Answer:**  
SQL NULL has special unknown-value semantics and must be tested with null-aware predicates.

### 11. Why can `collect()` be dangerous?

**Answer:**  
It brings all result rows to the driver, so a large result can exhaust driver memory.

### 12. Can SQL results be used with the DataFrame API?

**Answer:**  
Yes. `spark.sql()` returns a DataFrame, so DataFrame transformations can continue after SQL.

---

## Advanced

### 13. How does Spark SQL integrate with distributed execution?

**Answer:**  
SQL describes structured relational intent. Spark resolves the referenced data, represents the query as structured computation, and executes it through Spark's distributed runtime when an action requires a result.

### 14. Why can SQL and DataFrame APIs express similar transformations?

**Answer:**  
Both provide structured interfaces for describing transformations over DataFrame data. SQL uses relational syntax while the DataFrame API uses Python expressions and methods.

### 15. When would you choose SQL?

**Answer:**  
When the transformation is naturally relational, the team is SQL-oriented, and SQL makes the business logic concise and reviewable.

### 16. When would you choose the DataFrame API?

**Answer:**  
When transformation logic needs strong integration with Python application code, reusable Python functions, or programmatic composition.

### 17. When would you use a hybrid approach?

**Answer:**  
When different stages benefit from different representations—for example, Python/DataFrame preparation followed by SQL-heavy analytical transformations and then further DataFrame processing.

### 18. Why should a temporary view not be treated as a durable interface?

**Answer:**  
Its lifecycle and availability are tied to the temporary-view/session context. Durable contracts should use persistent data structures or explicitly managed interfaces.

---

## Architecture Questions

### 19. Design a Spark pipeline where Python logic and SQL transformations coexist.

**Strong answer should include:**

```text
DataFrame ingestion
→ DataFrame preparation
→ temporary view
→ SQL transformation
→ result DataFrame
→ DataFrame validation/processing
→ output
```

It should also define:

- view naming
- lifecycle
- schema contracts
- ownership
- action boundaries

### 20. How would you structure SQL transformations so multiple engineers can maintain them?

**Strong answer should include:**

- explicit columns
- descriptive names
- consistent formatting
- clear CTEs where useful
- documented business rules
- stable schemas
- bounded responsibilities
- visible temporary-view dependencies

### 21. A developer wants to collect a million-row SQL result. What concerns should you raise?

**Strong answer should include:**

- driver memory
- result size
- whether Python actually needs every row
- whether aggregation/filtering can happen in Spark first
- bounded inspection alternatives
- downstream processing design

### 22. A team uses global temporary views everywhere. What should they consider?

**Strong answer should include:**

- scope
- lifecycle
- naming
- replacement ownership
- hidden dependencies
- maintainability
- whether persistent storage would be a clearer contract

### 23. A Spark SQL query is logically correct but extremely expensive. What later topics should you investigate?

**Answer:**  
Depending on the query and symptoms, investigate:

```text
joins / shuffle
partitioning
skew
caching
UDF choices
Catalyst/explain plans
AQE
Spark UI
```

Those topics are deliberately deferred to later files in the roadmap.

---

# 101. Architecture Thinking

## Question 1

A team has SQL-heavy analysts and Python-heavy Data Engineers.

How can they coexist?

### Reasoning

Use Spark SQL where SQL makes analytical transformations readable and the DataFrame API where Python composition or application logic is clearer.

A shared Spark runtime allows both representations to operate on structured data.

---

## Question 2

A pipeline has five logical transformation stages.

Where could temporary views be useful?

### Reasoning

Temporary views can provide named SQL boundaries:

```text
raw_df
   ↓
cleaned_view
   ↓
aggregated_view
   ↓
final_view
```

But avoid creating a maze of hidden runtime dependencies. Each view should have a clear owner, purpose, and lifecycle.

---

## Question 3

A developer wants to collect a million-row SQL result.

What should be considered?

### Reasoning

Ask:

```text
Does Python actually need all rows?
Can the data be filtered?
Can it be aggregated?
Can it be written directly?
Can inspection use LIMIT?
```

Remember:

```python
collect()
```

moves all result rows to the driver.

---

## Question 4

A team uses global temporary views everywhere.

What concerns should they understand?

### Reasoning

Global temporary views can create:

- lifecycle dependencies
- naming dependencies
- replacement dependencies
- hidden coupling between sessions

They are temporary coordination mechanisms, not automatically durable architecture.

---

## Question 5

A SQL query is logically correct but expensive.

Which later topics should the engineer investigate?

### Reasoning

Follow the roadmap:

```text
07 joins/shuffle
08 partitioning
09 skew
10 caching
11 UDFs
12 Catalyst
13 AQE
15 Spark UI
```

The important engineering behavior is to investigate evidence rather than randomly adding optimizations.

---

# 102. Practice Questions

## Basic — 10 Questions

### 1.
What is Spark SQL?

### 2.
What is a temporary view?

### 3.
What does `spark.sql()` return?

### 4.
What is the role of `SparkSession` in Spark SQL?

### 5.
What is the purpose of `createOrReplaceTempView()`?

### 6.
How do you reference a global temporary view?

### 7.
What does `WHERE` do?

### 8.
What does `GROUP BY` do?

### 9.
How do you check for NULL in SQL?

### 10.
Why can `collect()` be dangerous?

### Answers

1. A structured SQL interface for querying and transforming Spark data.
2. A temporary SQL-accessible name for structured DataFrame data.
3. A DataFrame.
4. It provides the application-level entry point for Spark SQL functionality.
5. It registers or replaces a temporary view.
6. Through `global_temp`, for example `global_temp.people`.
7. Filters rows.
8. Forms groups for aggregate processing.
9. Use `IS NULL` or `IS NOT NULL`.
10. It brings the full result to the driver.

---

## Moderate — 10 Questions

### 11.
Write SQL to select `name` and `age` from `people`.

### 12.
Write SQL to select people with age at least 25.

### 13.
Write SQL to calculate `age + 1 AS next_age`.

### 14.
Write SQL to classify age into minor/adult/senior.

### 15.
Write SQL to replace a null country with `"Unknown"`.

### 16.
Write SQL to count people by country.

### 17.
Explain WHERE versus HAVING.

### 18.
Explain `DISTINCT country, city`.

### 19.
Explain the difference between a temporary view and a global temporary view.

### 20.
Convert this to SQL:

```python
df.filter(
    F.col("age") >= 25
).select(
    "name",
    "age",
)
```

### Answers

11.

```sql
SELECT name, age
FROM people
```

12.

```sql
SELECT *
FROM people
WHERE age >= 25
```

13.

```sql
SELECT
    age + 1 AS next_age
FROM people
```

14.

```sql
CASE
    WHEN age < 18 THEN 'minor'
    WHEN age < 60 THEN 'adult'
    ELSE 'senior'
END
```

15.

```sql
COALESCE(country, 'Unknown')
```

16.

```sql
SELECT
    country,
    COUNT(*) AS people_count
FROM people
GROUP BY country
```

17. WHERE filters rows; HAVING filters grouped results.

18. It removes duplicate `(country, city)` combinations.

19. A normal temporary view is session-scoped; a global temporary view uses the `global_temp` namespace and broader temporary scope within the application context.

20.

```sql
SELECT
    name,
    age
FROM people
WHERE age >= 25
```

---

## Hard — 10 Questions

### 21.
A query returns no rows even though the source contains matching values. Give five debugging steps.

### 22.
Why does `country = NULL` fail to implement a null test?

### 23.
Why can `SELECT country, name, COUNT(*) GROUP BY country` be invalid?

### 24.
Why does `createOrReplaceTempView()` make iterative development easier?

### 25.
Why is `SELECT *` often less explicit than a production pipeline should be?

### 26.
Why is `LIMIT 20` useful for exploration but not a complete performance strategy?

### 27.
Why can a temporary view be a hidden dependency?

### 28.
Explain why a SQL result can immediately be processed with DataFrame methods.

### 29.
What is the difference between SQL `AND` and DataFrame API `&`?

### 30.
Why can `collect()` create a driver-side scalability problem?

### Expected reasoning

For each answer, connect:

```text
syntax
→ semantics
→ DataFrame/result
→ execution
→ production impact
```

---

## Advanced — 10 Questions

### 31.
Design a hybrid SQL/DataFrame transformation pipeline.

### 32.
Define a lifecycle policy for temporary views in a production Spark application.

### 33.
Explain how you would prevent SQL transformations from silently depending on unrelated temporary views.

### 34.
Design a stable output schema for a SQL-based analytics dataset.

### 35.
Explain when a CTE improves maintainability.

### 36.
Design a data-quality investigation using Spark SQL.

### 37.
Explain how you would decide between SQL and DataFrame API for a new transformation.

### 38.
A SQL query is correct but slow. Which later roadmap topics should you investigate and why?

### 39.
Design a safe exploratory workflow for a large SQL result without collecting everything to the driver.

### 40.
Explain how SQL/DataFrame interoperability can support a mixed-skill Data Engineering team.

### Evaluation standard

A strong advanced answer should discuss:

- correctness
- schema
- lifecycle
- maintainability
- execution model
- driver safety
- business semantics
- appropriate forward topics

---

# 103. Final Knowledge Check

## 10 Conceptual Questions

1. Explain Spark SQL in your own words.
2. Why does Spark SQL exist?
3. What is a temporary view?
4. What is a global temporary view?
5. Why is `global_temp` required?
6. What is the relationship between SQL and DataFrames?
7. What is lazy evaluation?
8. What is the difference between WHERE and HAVING?
9. Why does NULL require special handling?
10. Why is `collect()` dangerous for large results?

---

## 5 Code-Reading Questions

### Code 1

```python
df.createOrReplaceTempView("people")

result = spark.sql("""
    SELECT
        name,
        age + 1 AS next_age
    FROM people
    WHERE age >= 25
""")
```

Explain:

- input
- filtering
- derived expression
- output schema
- why `result` is a DataFrame

### Code 2

```python
df.createOrReplaceGlobalTempView("people")

result = spark.sql("""
    SELECT *
    FROM global_temp.people
""")
```

Explain the namespace.

### Code 3

```sql
SELECT
    country,
    COUNT(*) AS people_count
FROM people
GROUP BY country
HAVING COUNT(*) >= 10
ORDER BY people_count DESC
```

Explain the logical roles of:

```text
GROUP BY
COUNT
HAVING
ORDER BY
```

### Code 4

```sql
SELECT
    COALESCE(country, 'Unknown') AS country
FROM people
```

Explain the null behavior.

### Code 5

```python
result = spark.sql("""
    SELECT *
    FROM people
""")

result.show()
```

Explain why the SQL DataFrame and `show()` have different execution roles.

---

## 5 Debugging Questions

1. A view cannot be found. What do you inspect?
2. A SQL field cannot be resolved. What do you inspect?
3. A null filter returns unexpected results. What do you inspect?
4. A grouped query fails because a selected field is not grouped. What does that mean?
5. A developer collects a huge result. What should be changed?

---

## 5 Implementation Tasks

### Task 1

Create a temporary view from a DataFrame.

### Task 2

Write a SQL query that filters active records and selects three fields.

### Task 3

Calculate revenue using `quantity * unit_price`.

### Task 4

Aggregate revenue by country and retain only countries above a threshold.

### Task 5

Convert the SQL result into a DataFrame transformation that creates an additional classification field.

---

## 3 Architecture Questions

### Architecture 1

Design a pipeline where SQL-heavy and Python-heavy engineers can safely collaborate.

### Architecture 2

Design a temporary-view naming and lifecycle strategy.

### Architecture 3

Design an investigation workflow for a logically correct but unexpectedly expensive Spark SQL query.

---

# 104. Topic Completion Checklist

You should not consider this topic complete until you can independently:

- [ ] Explain Spark SQL.
- [ ] Explain why Spark SQL exists.
- [ ] Explain SQL as a declarative language.
- [ ] Explain how Spark SQL differs conceptually from a traditional database.
- [ ] Create a SparkSession.
- [ ] Explain the role of `spark.sql()`.
- [ ] Create a DataFrame.
- [ ] Inspect its schema.
- [ ] Create a temporary view.
- [ ] Distinguish `createTempView()` from `createOrReplaceTempView()`.
- [ ] Query a temporary view.
- [ ] Use `SELECT`.
- [ ] Use explicit column selection.
- [ ] Use aliases.
- [ ] Create SQL expressions.
- [ ] Use `WHERE`.
- [ ] Use `AND`, `OR`, and `NOT`.
- [ ] Use `IN`.
- [ ] Use `BETWEEN`.
- [ ] Use `LIKE`.
- [ ] Use `IS NULL`.
- [ ] Use `IS NOT NULL`.
- [ ] Use `COALESCE`.
- [ ] Use `CASE`.
- [ ] Use `COUNT`.
- [ ] Use `SUM`.
- [ ] Use `AVG`.
- [ ] Use `MIN`.
- [ ] Use `MAX`.
- [ ] Use `GROUP BY`.
- [ ] Use `HAVING`.
- [ ] Use `ORDER BY`.
- [ ] Use `DISTINCT`.
- [ ] Use `LIMIT`.
- [ ] Explain temporary-view lifecycle.
- [ ] Explain global temporary views.
- [ ] Use `global_temp`.
- [ ] Move from DataFrame API to SQL.
- [ ] Move from SQL back to DataFrame API.
- [ ] Choose SQL/DataFrame/hybrid appropriately.
- [ ] Explain SQL lazy evaluation.
- [ ] Explain actions.
- [ ] Avoid unsafe large `collect()`.
- [ ] Debug common Spark SQL errors.
- [ ] Build a production-oriented SQL transformation.
- [ ] Explain when later optimization topics are required.

---

# 105. Glossary

**Spark SQL** — Spark's structured interface for querying and transforming data using SQL and related structured APIs.

**SparkSession** — The main application-level entry point for Spark functionality, including SQL and DataFrame operations.

**DataFrame** — A distributed structured dataset organized into named columns with a schema.

**Relation** — A structured data object that can be queried through relational operations.

**Temporary View** — A temporary SQL-accessible name associated with structured Spark data.

**Global Temporary View** — A temporary view exposed through the `global_temp` namespace with broader temporary visibility within the application context.

**Catalog** — The metadata layer through which Spark resolves tables, views, and related SQL objects.

**SQL Query** — A declarative statement describing the structured data result required.

**Schema** — The names, types, and structural information describing a DataFrame.

**Column Expression** — A Spark expression describing a value derived from columns, literals, operators, or functions.

**Alias** — A name assigned to a selected field or expression.

**Predicate** — A condition used to determine whether a row satisfies a filter.

**NULL** — A SQL representation of missing or unknown data.

**Aggregation** — A transformation that combines multiple rows into summary values such as counts or sums.

**GROUP BY** — A SQL clause that forms groups according to one or more expressions.

**HAVING** — A SQL clause that filters grouped/aggregated results.

**CTE** — Common Table Expression; a named query subexpression introduced with `WITH` for organizing SQL.

**Lazy Evaluation** — Spark's deferred execution model in which transformations are represented before execution is required.

**Action** — An operation that requires Spark to execute a computation and return a result or produce an external effect.

**Driver** — The process coordinating a Spark application.

**DataFrame API** — PySpark's programmatic API for expressing structured transformations with DataFrame methods and Column expressions.

---

# 106. Final Summary

Spark SQL provides a declarative way to work with structured distributed data in Spark.

The core mental model is:

```text
DataFrame
    ↓
Temporary View
    ↓
Spark SQL
    ↓
Structured Transformation
    ↓
Result DataFrame
    ↓
Action
    ↓
Distributed Execution
```

The key concepts are:

```text
SparkSession
    ↓
Spark SQL
    ↓
Temporary Views
    ↓
SELECT / WHERE / expressions
    ↓
CASE / NULL handling
    ↓
Aggregation
    ↓
GROUP BY / HAVING
    ↓
ORDER BY / DISTINCT / LIMIT
    ↓
DataFrame interoperability
    ↓
Lazy execution
```

The most important production lesson is:

> **SQL and the DataFrame API are complementary ways to express structured Spark transformations.**

Use SQL when it makes relational logic clearer.

Use the DataFrame API when Python composition and application integration are clearer.

Use both when a hybrid pipeline produces the most maintainable design.

Do not optimize based on API preference alone. First establish:

```text
correctness
→ schema
→ business semantics
→ maintainability
→ execution behavior
→ performance evidence
```

Then investigate later topics such as:

```text
joins
shuffle
partitioning
skew
caching
UDFs
Catalyst
AQE
Spark UI
```

when the workload requires them.

---

# 107. What You Should Be Able to Do Now

After completing this topic, you should be able to build this workflow without step-by-step guidance:

```text
Create SparkSession
        ↓
Create/load DataFrame
        ↓
Inspect schema
        ↓
Register temporary view
        ↓
Write Spark SQL
        ↓
Filter rows
        ↓
Create derived columns
        ↓
Handle NULLs
        ↓
Aggregate
        ↓
GROUP BY
        ↓
HAVING
        ↓
ORDER BY
        ↓
LIMIT for inspection
        ↓
Receive DataFrame
        ↓
Continue DataFrame transformations
        ↓
Register another view if appropriate
        ↓
Run another SQL transformation
        ↓
Trigger an action
        ↓
Explain the lazy execution model
```

You should also be able to explain why the following are different:

```text
temporary view
vs
global temporary view
```

and:

```text
WHERE
vs
HAVING
```

and:

```text
SQL
vs
DataFrame API
```

and:

```text
DataFrame transformation
vs
action
```

Finally, you should be able to recognize when a SQL pipeline has reached the point where later Spark topics must be investigated rather than trying to solve every performance problem inside the SQL syntax itself.

---

# 108. Final Self-Review

Before considering this file complete, verify:

- [x] Spark SQL fundamentals are taught.
- [x] The reason Spark SQL exists is explained.
- [x] Spark SQL is distinguished from a traditional relational database.
- [x] SparkSession is connected to SQL execution.
- [x] DataFrames are connected to SQL relations/views.
- [x] Temporary views are thoroughly explained.
- [x] `createTempView()` is covered.
- [x] `createOrReplaceTempView()` is covered.
- [x] Temporary-view lifecycle and scope are covered.
- [x] Global temporary views are covered.
- [x] `global_temp` is explained.
- [x] Temporary vs global temporary views are compared.
- [x] `SELECT` is covered.
- [x] `WHERE` is covered.
- [x] SQL aliases are covered.
- [x] SQL expressions are covered.
- [x] `CASE` is covered.
- [x] NULL semantics are covered.
- [x] `COALESCE` is covered.
- [x] Aggregation is covered.
- [x] `GROUP BY` is covered.
- [x] `HAVING` is covered.
- [x] `ORDER BY` is covered.
- [x] `DISTINCT` is covered.
- [x] `LIMIT` is covered.
- [x] SQL/DataFrame interoperability is demonstrated.
- [x] SQL-to-DataFrame switching is demonstrated.
- [x] SQL-vs-DataFrame decision guidance is neutral and practical.
- [x] SQL readability and maintainability are addressed.
- [x] CTEs are introduced at a foundational level.
- [x] Representative Spark SQL functions are introduced.
- [x] Basic data types and casting are covered.
- [x] Basic date/timestamp concepts are covered.
- [x] Common Spark SQL mistakes are covered.
- [x] Debugging exercises are included.
- [x] Lazy evaluation is connected to Topic 04.
- [x] Actions and `collect()` risks are covered.
- [x] Foundational performance awareness is included.
- [x] Advanced optimizer topics are deferred.
- [x] Production use cases are included.
- [x] A complete mini-project is included.
- [x] At least 10 progressive labs are included.
- [x] At least 8 debugging exercises are included.
- [x] Exactly 40 practice questions are included.
- [x] Interview preparation is included.
- [x] Architecture thinking is included.
- [x] Common misconceptions are corrected.
- [x] Forward connections to later roadmap topics are included.
- [x] A final knowledge check is included.
- [x] A glossary is included.
- [x] The chapter remains within Topic 06 scope.
- [x] Deep Catalyst, AQE, joins, skew, caching, UDF, and Spark UI material is deferred to later topics.
- [x] The file is standalone and suitable for beginner-to-production-oriented learning.

---

## Final Topic Takeaway

The core mental model to retain is:

```text
SparkSession
     |
     +-------------------+
     |                   |
DataFrame API        Spark SQL
     |                   |
     +---------+---------+
               |
       Structured Data
               |
        Lazy Transformation
               |
             Action
               |
       Distributed Spark
```

And for temporary views:

```text
DataFrame
    |
    | createOrReplaceTempView("people")
    v
Temporary View
    |
    | spark.sql(...)
    v
Result DataFrame
    |
    | DataFrame API
    v
Further Transformation
```

If you can move confidently between these representations while preserving schema, business semantics, lifecycle awareness, and driver safety, you have established the core Spark SQL foundation required for the next stage of the Distributed Processing with PySpark roadmap.
