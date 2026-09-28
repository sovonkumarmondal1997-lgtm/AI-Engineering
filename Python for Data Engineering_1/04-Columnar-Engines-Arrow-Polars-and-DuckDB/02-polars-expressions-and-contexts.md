# Polars Expressions and Contexts

> **Stage 2 — Python for Data Engineering · Module 2.4 · Topic 02**
>
> This chapter teaches Polars from fundamentals to production-oriented reasoning. The central skill is learning to **think in Polars expressions** instead of writing procedural, row-by-row Python transformations.

---

## 0. Chapter Map

```text
Polars mental model
      ↓
DataFrame + no index + explicit dtypes
      ↓
Expressions
      ↓
Contexts
      ├── select()
      ├── with_columns()
      ├── filter()
      └── group_by().agg()
      ↓
Conditional logic + namespaces + selectors
      ↓
Null/NaN + dtypes
      ↓
Joins + cardinality + join_asof()
      ↓
Window expressions with .over()
      ↓
Reshaping + dynamic/rolling time operations
      ↓
Expression parallelism
      ↓
Native expressions vs Python UDFs
      ↓
Pandas → Polars translation
      ↓
Production orders pipeline
      ↓
Testing + benchmarking + debugging
```

The current Polars documentation describes expressions as abstract computations that need a context such as `select`, `with_columns`, `filter`, or `group_by` before they produce concrete results. citeturn700248search0turn700248search1

---

# 1. Learning Objectives

After completing this chapter, you should be able to:

- Explain the Polars mental model.
- Explain why Polars does not use a pandas-style DataFrame index.
- Explain immutability and explicit typing.
- Create and inspect DataFrames.
- Explain what an expression is.
- Explain an expression tree.
- Use `pl.col()`, `pl.lit()`, arithmetic, comparisons, `alias()`, and `cast()`.
- Distinguish an expression from an eager operation.
- Choose the correct context:
  - `select()`
  - `with_columns()`
  - `filter()`
  - `group_by().agg()`
- Read and write CSV, Parquet, and NDJSON.
- Understand `schema=` and `schema_overrides=`.
- Use conditional expressions.
- Use `.str`, `.dt`, `.list`, `.struct`, `.cat`, and `.name`.
- Use `polars.selectors`, including `cs.numeric()` and `cs.starts_with(...)`.
- Apply multi-column expressions safely.
- Distinguish `null` from `NaN`.
- Understand the major Polars numeric, temporal, categorical, and nested dtypes.
- Distinguish `Categorical` from `Enum`.
- Perform inner, left, full, semi, anti, and cross joins.
- Validate expected join cardinality.
- Explain and diagnose join explosion.
- Use `join_asof()` for time-aware matching.
- Use `.over()` for group-wise calculations while retaining the original rows.
- Relate `.over()` to pandas `transform()` and SQL window functions.
- Understand `pivot`, `unpivot`, `explode`, and `implode`.
- Understand `group_by_dynamic()` and rolling operations.
- Explain why grouping independent expressions in one `with_columns()` can be useful.
- Recognize when `map_elements()` is inappropriate.
- Replace simple Python UDFs with native Polars expressions.
- Translate pandas transformations into idiomatic Polars.
- Build the roadmap's eager `polars_orders.py` exercise.
- Validate results against pandas.
- Benchmark without fabricating results.
- Debug common failures.
- Explain the topic at senior Data Engineer level.

---

# 2. Prerequisites

This topic builds on:

- Python fundamentals.
- NumPy fundamentals.
- pandas DataFrames.
- pandas selection.
- pandas `groupby`.
- pandas joins.
- pandas reshaping.
- pandas time-series operations.
- Basic Data Engineering concepts.
- **Topic 01 — Apache Arrow Columnar Memory Model.**

Do not think:

> "I know pandas, therefore I already know Polars."

Instead think:

```text
Pandas skill
    ↓
understand the business intent
    ↓
express the intent in Polars
```

The syntax may look similar in places, but the execution-oriented mental model is different.

---

# 3. Why Polars Exists

Data processing becomes difficult when a pipeline repeatedly does:

```text
row
 ↓
Python callback
 ↓
row
 ↓
Python callback
 ↓
millions of times
```

Analytical workloads often benefit from:

```text
columns
 ↓
typed expressions
 ↓
native engine execution
```

Polars is a DataFrame library and execution engine built around:

- an expression API,
- typed data,
- column-oriented processing,
- native execution,
- multi-threaded execution.

Polars fits naturally with the Arrow-oriented columnar ecosystem from Topic 01.

## 3.1 What problem does it address?

Common problems include:

- large DataFrames,
- repeated transformations,
- memory pressure,
- inefficient Python-level callbacks,
- complex analytical logic,
- expensive joins,
- wide datasets.

## 3.2 What it does not mean

Do not memorize:

> "Polars is always faster than pandas."

That is not an engineering rule.

Performance depends on:

- dataset size,
- workload,
- file format,
- data types,
- operation,
- machine,
- memory,
- execution strategy,
- library version.

Use benchmarks as evidence.

---

# 4. The Polars Mental Model

## 4.1 DataFrame

A DataFrame is concrete tabular data.

```python
import polars as pl

df = pl.DataFrame(
    {
        "name": ["A", "B", "C"],
        "amount": [100, 200, 300],
    }
)

print(df)
print(df.schema)
print(df.dtypes)
print(df.height)
print(df.width)
```

Mental model:

```text
DataFrame
├── rows
├── columns
└── schema
```

---

## 4.2 No Traditional pandas-Style Index

Pandas can use:

```python
df.loc[5]
```

with an explicit index object.

Polars does not use that pandas-style index alignment model.

Instead, row semantics come from:

- row position,
- predicates,
- keys,
- joins,
- ordering.

Example:

```python
df.filter(pl.col("amount") > 100)
```

There is no hidden requirement that rows first be aligned through a special index.

### Why this design?

It makes alignment explicit.

For example:

```python
orders.join(
    customers,
    on="customer_id",
)
```

says exactly which key defines the relationship.

### Important nuance

An index is not universally bad.

It is useful in some systems and workloads. Polars simply makes a different architectural choice.

---

## 4.3 Immutable DataFrames

Transformations return a new logical DataFrame result.

```python
df2 = df.with_columns(
    (pl.col("amount") * 1.18).alias("gross_amount")
)
```

Think:

```text
df
 │
 └── transformation → df2
```

rather than:

```text
mutate hidden internal state
```

This encourages predictable pipelines.

---

## 4.4 Strict and Explicit Dtypes

Inspect:

```python
print(df.schema)
```

Example conceptual schema:

```text
name: String
amount: Int64
```

Types influence:

- arithmetic,
- joins,
- null handling,
- grouping,
- output compatibility.

In production, explicit types often make failures visible earlier.

---

## 4.5 Multi-Threaded Execution

Polars is designed to execute suitable work across multiple CPU resources.

Conceptually:

```text
expression
    ↓
native execution
    ↓
independent work
    ↓
multiple threads where applicable
```

Not every operation uses all cores.

Parallelism depends on:

- the operation,
- data size,
- dependencies,
- engine,
- machine.

Topic 03 will cover lazy plans and optimization in more depth.

---

# 5. Installing and Verifying Polars

Install:

```bash
uv add polars
```

Verify:

```python
import polars as pl

print(pl.__version__)
```

Polars evolves quickly.

For version-sensitive APIs, always verify the syntax against the installed version.

Especially verify:

- schema arguments,
- `Enum`,
- selectors,
- joins,
- `join_asof`,
- reshaping,
- `group_by_dynamic`,
- rolling operations,
- `map_elements`.

---

# 6. First Polars DataFrame

```python
import polars as pl

df = pl.DataFrame(
    {
        "name": ["A", "B", "C"],
        "amount": [100, 200, 300],
    }
)

print(df)
```

Inspect:

```python
print("schema:", df.schema)
print("dtypes:", df.dtypes)
print("rows:", df.height)
print("columns:", df.width)
```

The first habit to develop is:

> Inspect the schema before reasoning about transformations.

---

# 7. The Most Important Concept — Expressions

An **expression** describes a computation.

```python
pl.col("amount")
```

means:

> refer to the `amount` column inside an expression.

Then:

```python
pl.col("amount") * 2
```

describes:

```text
take amount
     ↓
multiply by 2
```

Then:

```python
(pl.col("amount") * 1.18).alias("gross_amount")
```

describes:

```text
take amount
    ↓
multiply by 1.18
    ↓
name the result gross_amount
```

The expression itself is not the same as the final materialized Series.

---

# 8. Expression vs Context

Memorize this:

```text
Expression
    ↓
WHAT computation?

Context
    ↓
WHERE / HOW is the expression applied?
```

For example:

```python
expr = pl.col("amount") * 1.18
```

Then:

```python
df.select(expr.alias("gross_amount"))
```

and:

```python
df.with_columns(expr.alias("gross_amount"))
```

use closely related expressions in different contexts.

The same expression can therefore participate in different output semantics.

---

# 9. Expression Trees

Consider:

```python
(
    (pl.col("amount") > 100)
    & (pl.col("status") == "PAID")
)
```

Conceptually:

```text
                   AND
                  /   \
                >       ==
               / \     /  \
          amount 100 status "PAID"
```

Another:

```python
(pl.col("amount") * 1.18).alias("gross_amount")
```

Conceptually:

```text
          alias
            │
         multiply
         /      \
      amount    1.18
```

Thinking in trees helps you identify:

- input columns,
- constants,
- operations,
- output names,
- dependencies.

---

# 10. `pl.col()`

## What is it?

A column reference expression.

```python
pl.col("amount")
```

## Why does it exist?

Polars needs a way to refer to a column symbolically.

## Basic example

```python
df.select(
    pl.col("amount")
)
```

## Multiple columns

```python
df.select(
    pl.col("amount"),
    pl.col("name"),
)
```

## Multiple named columns

```python
df.select(
    pl.col(["amount", "name"])
)
```

The exact forms accepted by the installed release should be verified when writing reusable production code.

---

# 11. `pl.lit()`

## What is it?

A literal expression.

```python
pl.lit(10)
pl.lit("IN")
pl.lit(True)
```

Example:

```python
df.select(
    (pl.col("amount") + pl.lit(10)).alias("adjusted")
)
```

Mental model:

```text
pl.col("amount")
→ column reference

pl.lit(10)
→ constant value
```

Explicit literals are especially useful in complex expressions where the distinction between a column and a constant needs to be clear.

---

# 12. Arithmetic Expressions

Polars expressions support standard arithmetic:

```text
+
-
*
/
%
**
```

Examples:

```python
pl.col("amount") + 10
```

```python
pl.col("quantity") * pl.col("price")
```

```python
(pl.col("quantity") ** 2).alias("quantity_squared")
```

Inspect the resulting dtype when numeric semantics matter.

---

# 13. Comparison Expressions

Comparisons include:

```text
>
<
>=
<=
==
!=
```

Example:

```python
pl.col("amount") > 100
```

This is a Boolean expression.

Combine conditions with:

```python
&
|
```

Example:

```python
(
    (pl.col("amount") > 100)
    & (pl.col("status") == "PAID")
)
```

## Common error

Do not use Python's:

```python
and
or
```

for element-wise column logic.

Use:

```python
&
|
```

with parentheses.

---

# 14. `alias()`

Use `alias()` to give a derived expression a stable name.

```python
(
    pl.col("amount") * 1.18
).alias("gross_amount")
```

Why it matters:

- readable code,
- stable output schema,
- easier testing,
- easier downstream references,
- better production contracts.

---

# 15. `cast()`

Casting changes a value to another dtype.

```python
pl.col("customer_id").cast(pl.Int64)
```

or:

```python
pl.col("amount").cast(pl.Float64)
```

Use casting intentionally.

Ask:

```text
Is the source type correct?
Is the target type safe?
Could precision be lost?
Could a downstream system reject the type?
```

For monetary data, consider whether Decimal is more appropriate than Float64.

---

# 16. Four Core Contexts

| Context | Main purpose | Typical result |
|---|---|---|
| `select()` | choose/compute output columns | projection/derived output |
| `with_columns()` | add/replace columns | original columns + changes |
| `filter()` | keep rows | fewer rows |
| `group_by().agg()` | aggregate groups | usually fewer rows, one/more rows per group |

Official Polars documentation presents these as the core expression contexts and demonstrates that the same expression can yield different shapes depending on context. citeturn700248search0

---

# 17. `select()`

## What is it?

A projection context.

## Mental model

```text
"Build the result from these expressions."
```

Example:

```python
df.select(
    "name",
    "amount",
)
```

Derived output:

```python
df.select(
    pl.col("name"),
    (pl.col("amount") * 1.18).alias("gross_amount"),
)
```

The result is defined by the selected expressions.

---

# 18. `with_columns()`

## What is it?

A transformation context that retains existing columns and adds or replaces columns.

```python
df.with_columns(
    (pl.col("amount") * 1.18).alias("gross_amount")
)
```

Multiple expressions:

```python
df.with_columns(
    (pl.col("amount") * 1.18).alias("gross_amount"),
    (pl.col("amount") * 0.18).alias("tax"),
)
```

Mental model:

```text
existing DataFrame
        +
new/replacement columns
```

---

# 19. `select()` vs `with_columns()`

Start with:

```text
name
amount
status
```

### `select()`

```python
df.select(
    (pl.col("amount") * 1.18).alias("gross_amount")
)
```

Focus:

```text
output expressions
```

### `with_columns()`

```python
df.with_columns(
    (pl.col("amount") * 1.18).alias("gross_amount")
)
```

Focus:

```text
existing columns
+
derived/replacement columns
```

### Rule

```text
Need to define the output columns?
→ select()

Need to keep the current columns and add/replace?
→ with_columns()
```

---

# 20. `filter()`

## What is it?

A row-selection context.

```python
df.filter(
    pl.col("amount") > 100
)
```

Compound condition:

```python
df.filter(
    (pl.col("amount") > 100)
    & (pl.col("status") == "PAID")
)
```

Mental model:

```text
"Which rows survive?"
```

A filter predicate is a Boolean expression.

Rows whose predicate is not true are not retained. Polars' expression documentation explicitly notes this behaviour, including null predicate values. citeturn700248search7

---

# 21. `group_by().agg()`

## What is it?

A grouped aggregation context.

Example:

```python
df.group_by("customer_id").agg(
    pl.col("amount").sum().alias("total_amount")
)
```

Conceptually:

```text
many rows
   ↓
group by key
   ↓
aggregation
   ↓
fewer rows
```

Multiple metrics:

```python
df.group_by("customer_id").agg(
    pl.len().alias("order_count"),
    pl.col("amount").sum().alias("total_amount"),
    pl.col("amount").mean().alias("average_amount"),
    pl.col("amount").min().alias("min_amount"),
    pl.col("amount").max().alias("max_amount"),
)
```

---

# 22. Context Decision Tree

Use this until it becomes automatic:

```text
Do I want fewer rows?
        │
        └── YES → filter()

Do I want to define output columns?
        │
        └── YES → select()

Do I want to keep current columns
and add/replace columns?
        │
        └── YES → with_columns()

Do I want grouped output?
        │
        └── YES → group_by().agg()

Do I want group-wise values
while retaining original rows?
        │
        └── YES → .over()
```

This is one of the most important learning aids in Topic 02.

---

# 23. Reading and Writing Data

CSV:

```python
df = pl.read_csv("orders.csv")
```

Parquet:

```python
df = pl.read_parquet("orders.parquet")
```

NDJSON:

```python
df = pl.read_ndjson("orders.ndjson")
```

Parquet output:

```python
df.write_parquet("orders.parquet")
```

## Why this matters

Data Engineering often starts with:

```text
files
  ↓
typed DataFrame
```

The read boundary is where schema decisions become important.

---

# 24. Explicit Schema Controls

Polars supports schema-related parameters such as:

```python
schema=
```

and:

```python
schema_overrides=
```

A common pattern is:

```python
schema_overrides = {
    "customer_id": pl.Int64,
    "status": pl.String,
}
```

then:

```python
df = pl.read_csv(
    "orders.csv",
    schema_overrides=schema_overrides,
)
```

Use the exact form supported by your installed version.

## Why schema control matters

Without controlled typing:

```text
first batch
→ inferred Int64

future batch
→ string value appears

schema changes
→ downstream breakage
```

A reliable pipeline should have an intentional schema strategy.

---

# 25. Conditional Expressions

Use:

```python
pl.when(...)
  .then(...)
  .otherwise(...)
```

Example:

```python
df.with_columns(
    pl.when(pl.col("amount") >= 1000)
      .then(pl.lit("HIGH"))
      .otherwise(pl.lit("NORMAL"))
      .alias("order_class")
)
```

Multiple conditions:

```python
df.with_columns(
    pl.when(pl.col("amount") >= 5000)
      .then(pl.lit("VIP"))
      .when(pl.col("amount") >= 1000)
      .then(pl.lit("HIGH"))
      .otherwise(pl.lit("NORMAL"))
      .alias("order_class")
)
```

Read from top to bottom.

Keep branch types compatible.

---

# 26. Namespace Model

Polars organizes many native operations into namespaces:

```text
.str
.dt
.list
.struct
.cat
.name
```

Mental model:

```text
column expression
      ↓
"what kind of data am I operating on?"
      ↓
namespace
```

Native namespaces should usually be preferred over Python callbacks when they express the required business logic.

---

# 27. `.str` Namespace

Use for strings.

```python
df.with_columns(
    pl.col("name")
      .str.to_lowercase()
      .alias("name_lower")
)
```

Other common categories:

- contains,
- replace,
- split,
- trimming,
- case conversion.

Example:

```python
df.with_columns(
    pl.col("email")
      .str.to_lowercase()
      .alias("email_normalized")
)
```

### Production use

- identifier normalization,
- email normalization,
- text cleanup,
- parsing structured text.

---

# 28. `.dt` Namespace

Use for temporal values.

```python
df.with_columns(
    pl.col("created_at").dt.year().alias("year"),
    pl.col("created_at").dt.month().alias("month"),
    pl.col("created_at").dt.day().alias("day"),
)
```

Use cases:

- partition keys,
- reporting periods,
- event timestamps,
- time-window preparation.

Always keep timezone and time unit semantics intentional.

---

# 29. `.list` Namespace

For list-valued columns.

Example:

```python
df.select(
    pl.col("tags").list.len().alias("tag_count")
)
```

Conceptual operations include:

- list length,
- element access,
- membership,
- list evaluation,
- transformations inside lists.

The exact API is version-sensitive; verify installed documentation before using less-common list methods.

---

# 30. `.struct` Namespace

For struct-valued columns.

Example:

```python
df.select(
    pl.col("address").struct.field("city")
)
```

A struct conceptually contains:

```text
address
├── city
└── zip
```

This lets nested data remain structured rather than being turned into generic Python dictionaries for every row.

---

# 31. `.cat` Namespace

The `.cat` namespace provides categorical-data operations.

Categorical columns are useful when:

```text
distinct values << row count
```

Examples:

```text
country
region
department
```

Use it when categorical representation matches the business/data semantics.

---

# 32. `.name` Namespace

The `.name` namespace can manipulate the names generated from expressions.

For example:

```python
df.select(
    pl.col("amount", "quantity")
      .name.prefix("raw_")
)
```

Conceptual output:

```text
raw_amount
raw_quantity
```

This is useful for wide transformations.

---

# 33. Polars Selectors

Import:

```python
import polars.selectors as cs
```

Use:

```python
df.select(cs.numeric())
```

This selects numeric columns.

Use:

```python
df.select(cs.starts_with("amt_"))
```

to select columns whose names start with `amt_`.

## Why selectors matter

A 300-column table may have:

```text
amt_usd
amt_eur
amt_inr
amt_gbp
...
```

A selector expresses the rule instead of hard-coding every name.

---

# 34. Selector Safety

Selectors are powerful because they are dynamic.

That is also the risk.

Suppose you write:

```python
df.with_columns(
    cs.numeric().fill_null(0)
)
```

Today there are five numeric columns.

Next month, engineering adds:

```text
fraud_score
```

The selector may include it automatically.

Therefore:

> Dynamic selection should be part of a deliberate schema contract.

Use a narrow selector when the blast radius must be controlled.

---

# 35. Multi-Column Expressions

Selectors allow broad operations.

Example:

```python
df.with_columns(
    cs.numeric().fill_null(0)
)
```

Another:

```python
df.select(
    cs.starts_with("amt_")
)
```

Another naming transformation:

```python
df.select(
    cs.numeric().name.prefix("num_")
)
```

The goal is:

```text
one expression rule
+
many matching columns
```

rather than repetitive code.

---

# 36. `null` vs `NaN`

These are different:

```text
null = missing value
NaN  = floating-point Not-a-Number
```

Example data:

```text
10.0
null
NaN
20.0
```

Check separately:

```python
df.select(
    pl.col("value").is_null().alias("is_null"),
    pl.col("value").is_nan().alias("is_nan"),
)
```

Also available:

```python
pl.col("value").is_not_null()
pl.col("value").is_not_nan()
```

### Why this matters

A data-quality rule might say:

```text
null → missing source value
NaN  → computationally invalid numeric value
```

Those may require different remediation.

---

# 37. Polars Dtype System

Required categories:

```text
Signed integers
Unsigned integers
Float32 / Float64
Decimal
String
Categorical
Enum
Date
Datetime
Duration
List
Struct
```

---

# 38. Integer Types

Signed:

```text
Int8
Int16
Int32
Int64
```

Use a width that safely fits the domain.

Example:

```python
df.with_columns(
    pl.col("quantity").cast(pl.Int32)
)
```

Do not choose a smaller integer merely because it uses less memory.

Check:

- value range,
- arithmetic behaviour,
- downstream compatibility,
- future growth.

---

# 39. Unsigned Types

```text
UInt8
UInt16
UInt32
UInt64
```

These represent non-negative values.

They are appropriate only when that semantic constraint makes sense and downstream systems handle them as expected.

---

# 40. Floating-Point Types

```text
Float32
Float64
```

Float32 can use less memory but has lower precision than Float64.

For monetary values, evaluate Decimal when exact decimal semantics matter.

---

# 41. Decimal

Use Decimal when exact decimal semantics are required.

Conceptual example:

```python
df.with_columns(
    pl.col("amount").cast(pl.Decimal(12, 2))
)
```

The business requirements should define:

- precision,
- scale,
- acceptable rounding,
- downstream compatibility.

---

# 42. String

String values:

```python
df = pl.DataFrame(
    {
        "country": ["IN", "US", "IN"],
    }
)
```

Use `.str` for native operations.

---

# 43. Categorical

Categoricals are useful for repeated labels:

```text
country
status
department
region
```

Use them when:

```text
many rows
+
relatively few distinct labels
```

---

# 44. Enum vs Categorical

Do not treat them as identical.

### `Enum`

Best mental model:

```text
known, explicitly declared category set
```

Example:

```python
status_type = pl.Enum([
    "PAID",
    "PENDING",
    "CANCELLED",
])
```

### `Categorical`

Best mental model:

```text
categorical representation where the category set can be managed more flexibly
```

Current Polars documentation treats both as dedicated categorical types and explains their different use cases; it also notes performance reasons to prefer `Enum` when its fixed-domain semantics fit the workload. citeturn700248search3

Do not make them interchangeable by habit.

---

# 45. Date, Datetime, Duration

## Date

Calendar date:

```text
2026-09-26
```

## Datetime

Date plus time:

```text
2026-09-26 12:34:56
```

Important properties:

```text
time unit
timezone
```

## Duration

Elapsed amount of time.

Conceptual example:

```text
end_time - start_time
→ duration
```

---

# 46. Time Semantics

Before time-based processing, define:

```text
timestamp unit
timezone
business timezone
naive vs timezone-aware
```

A production pipeline should not silently turn:

```text
UTC-aware
```

into:

```text
timezone-naive
```

without an explicit reason.

---

# 47. List and Struct

## List

A row contains a list:

```text
["python", "arrow"]
```

## Struct

A row contains a named record:

```text
{
    city: "Kolkata",
    zip: "700001"
}
```

These are nested dtypes, not generic Python object columns by default.

They are particularly useful for semi-structured data.

---

# 48. Join Fundamentals

Suppose:

```text
orders
customer_id | amount
------------|-------
100         | 100
100         | 200
200         | 300
```

and:

```text
customers
customer_id | name
------------|------
100         | Alice
200         | Bob
```

Join:

```python
orders.join(
    customers,
    on="customer_id",
    how="left",
)
```

The key defines the relationship.

---

# 49. Inner Join

Keeps matching rows.

```python
orders.join(
    customers,
    on="customer_id",
    how="inner",
)
```

Use when only matched entities should appear.

---

# 50. Left Join

Keeps all left rows.

```python
orders.join(
    customers,
    on="customer_id",
    how="left",
)
```

Missing customers result in nulls on right-side columns.

---

# 51. Full Join

Keeps unmatched rows from both sides.

Conceptually:

```text
left:
A B C

right:
  B C D

full:
A B C D
```

Useful in reconciliation.

---

# 52. Semi Join

Keep left rows that have a matching right key.

Conceptually:

```text
orders
   ↓
customer exists?
   ↓
yes → keep
```

Example:

```python
valid_orders = orders.join(
    customers,
    on="customer_id",
    how="semi",
)
```

---

# 53. Anti Join

Keep left rows with no matching right key.

```python
invalid_orders = orders.join(
    customers,
    on="customer_id",
    how="anti",
)
```

This is highly useful for data-quality checks.

---

# 54. Cross Join

A cross join creates a Cartesian product.

If:

```text
left = 3 rows
right = 4 rows
```

then:

```text
3 × 4 = 12 rows
```

Use deliberately.

An accidental cross join can be catastrophic.

---

# 55. Join Cardinality

Common key relationships:

```text
1:1
1:m
m:1
m:m
```

For example:

```text
orders → customers
many → one
```

which is:

```text
m:1
```

---

# 56. Join Cardinality Validation

Polars supports:

```python
validate="1:1"
validate="1:m"
validate="m:1"
```

Example:

```python
orders.join(
    customers,
    on="customer_id",
    how="left",
    validate="m:1",
)
```

Interpretation:

```text
many order rows
→ one customer row
```

---

# 57. Why Validation Matters

Suppose the customer table accidentally contains:

```text
customer_id
-----------
100
100
200
```

and an order has:

```text
customer_id = 100
```

The one order can match two customer rows.

That creates a second output row.

If:

```text
left duplicate count = L
right duplicate count = R
```

a many-to-many relationship can create up to:

```text
L × R
```

matches for that key.

This can:

- inflate revenue,
- inflate counts,
- increase memory use,
- slow pipelines,
- corrupt downstream metrics.

This is **join explosion**.

---

# 58. Production Join Pattern

For a transaction-to-dimension join:

```python
enriched = orders.join(
    customers,
    on="customer_id",
    how="left",
    validate="m:1",
)
```

Before the join, also investigate:

```python
duplicates = (
    customers
    .group_by("customer_id")
    .agg(pl.len().alias("count"))
    .filter(pl.col("count") > 1)
)
```

If duplicates are found, determine whether they are:

- data-quality errors,
- historical versions,
- legitimate multiple records.

Never silently assume uniqueness.

---

# 59. `join_asof()`

An as-of join solves a different problem.

Business statement:

> Match each event with the most recent applicable record as of the event timestamp.

Classic example:

```text
transaction time → FX rate in effect at that time
```

Rates:

```text
10:00 → 83.10
10:20 → 83.15
10:50 → 83.40
```

Transactions:

```text
10:05 → 83.10
10:30 → 83.15
10:55 → 83.40
```

---

# 60. `join_asof()` Example

```python
from datetime import datetime, timezone

import polars as pl


rates = (
    pl.DataFrame(
        {
            "timestamp": [
                datetime(2026, 9, 26, 10, 0, tzinfo=timezone.utc),
                datetime(2026, 9, 26, 10, 20, tzinfo=timezone.utc),
                datetime(2026, 9, 26, 10, 50, tzinfo=timezone.utc),
            ],
            "usd_inr": [83.10, 83.15, 83.40],
        }
    )
    .sort("timestamp")
)

transactions = (
    pl.DataFrame(
        {
            "timestamp": [
                datetime(2026, 9, 26, 10, 5, tzinfo=timezone.utc),
                datetime(2026, 9, 26, 10, 30, tzinfo=timezone.utc),
                datetime(2026, 9, 26, 10, 55, tzinfo=timezone.utc),
            ],
            "amount_usd": [100.0, 200.0, 300.0],
        }
    )
    .sort("timestamp")
)

result = transactions.join_asof(
    rates,
    on="timestamp",
    strategy="backward",
)

print(result)
```

The `backward` strategy represents:

```text
latest right-side timestamp
that is not after the left timestamp
```

### Production checks

- timestamps compatible,
- inputs correctly sorted,
- timezone intentional,
- strategy intentional,
- grouping keys intentional,
- boundary cases tested.

---

# 61. Window Expressions — `.over()`

Now compare:

```python
group_by().agg()
```

with:

```python
.over()
```

Suppose:

```text
customer | order | amount
---------|-------|-------
A        | O1    | 100
A        | O2    | 200
B        | O3    | 300
```

You want customer total **on every order**.

Use:

```python
pl.col("amount")
  .sum()
  .over("customer")
```

This is a **window expression**.

---

# 62. `.over()` Mental Model

```text
partition rows by key
        ↓
calculate expression within partition
        ↓
keep original row structure
```

Example:

```python
result = df.with_columns(
    pl.col("amount")
      .sum()
      .over("customer_id")
      .alias("customer_total")
)
```

Output shape remains approximately:

```text
same number of rows
+
new group-derived column
```

---

# 63. `.over()` vs `group_by().agg()`

## `group_by().agg()`

```text
many rows
    ↓
groups
    ↓
aggregate
    ↓
fewer rows
```

Example:

```python
df.group_by("customer_id").agg(
    pl.col("amount").sum().alias("customer_total")
)
```

## `.over()`

```text
many rows
    ↓
group-wise computation
    ↓
same rows
+
group-derived value
```

Example:

```python
df.with_columns(
    pl.col("amount")
      .sum()
      .over("customer_id")
      .alias("customer_total")
)
```

This distinction is critical.

---

# 64. `.over()` vs pandas `transform()`

Pandas:

```python
df["customer_total"] = (
    df.groupby("customer_id")["amount"]
      .transform("sum")
)
```

Polars:

```python
df = df.with_columns(
    pl.col("amount")
      .sum()
      .over("customer_id")
      .alias("customer_total")
)
```

Conceptual mapping:

```text
pandas transform
≈
Polars over
```

The implementations are not identical; the important point is equivalent analytical intent.

---

# 65. `.over()` vs SQL Window Functions

SQL:

```sql
SUM(amount) OVER (
    PARTITION BY customer_id
)
```

Polars:

```python
pl.col("amount")
  .sum()
  .over("customer_id")
```

This helps connect:

```text
pandas
Polars
SQL
```

through the same analytical concept.

---

# 66. Advanced `.over()` Examples

## Customer total

```python
pl.col("amount").sum().over("customer_id")
```

## Customer average

```python
pl.col("amount").mean().over("customer_id")
```

## Customer maximum

```python
pl.col("amount").max().over("customer_id")
```

## Customer order count

```python
pl.len().over("customer_id")
```

## Customer share

```python
(
    pl.col("amount")
    / pl.col("amount").sum().over("customer_id")
).alias("customer_share")
```

## Rank within group

A ranking expression can be combined with `.over(...)`:

```python
pl.col("amount")
  .rank()
  .over("customer_id")
```

Always verify ranking/tie semantics for the precise business rule.

---

# 67. Multi-Key Windows

Sometimes the business partition requires more than one key.

For example:

```python
.over(["customer_id", "currency"])
```

This means:

```text
partition by customer AND currency
```

The window partition is part of the business definition.

Do not add grouping columns casually.

---

# 68. Reshaping

Required operations:

```text
pivot
unpivot
explode
implode
```

Reshaping changes table shape.

Always document:

```text
input shape
→ transformation
→ output shape
```

---

# 69. `pivot`

Conceptual input:

```text
customer | month | revenue
---------|-------|--------
A        | Jan   | 100
A        | Feb   | 200
B        | Jan   | 300
B        | Feb   | 400
```

Conceptual pivot:

```text
customer | Jan | Feb
---------|-----|----
A        | 100 | 200
B        | 300 | 400
```

A current-style Polars example is:

```python
result = df.pivot(
    on="month",
    index="customer",
    values="revenue",
    aggregate_function="sum",
)
```

Verify the signature against your installed version because pivot APIs have evolved.

---

# 70. `unpivot`

Conceptual input:

```text
customer | Jan | Feb
---------|-----|----
A        | 100 | 200
```

Conceptual output:

```text
customer | month | revenue
---------|-------|--------
A        | Jan   | 100
A        | Feb   | 200
```

A current-style pattern is:

```python
result = df.unpivot(
    on=["Jan", "Feb"],
    index=["customer"],
    variable_name="month",
    value_name="revenue",
)
```

Verify current parameter names in your installed version.

---

# 71. `explode`

Input:

```text
order_id | tags
---------|----------------
O1       | ["python","etl"]
O2       | ["sql"]
```

Code:

```python
result = df.explode("tags")
```

Conceptual output:

```text
order_id | tags
---------|-------
O1       | python
O1       | etl
O2       | sql
```

### Production warning

`explode()` can multiply rows.

Always estimate the potential output size.

---

# 72. `implode`

The conceptual reverse direction is:

```text
many values
   ↓
list-valued result
```

For example, after processing tags:

```python
result = df.group_by("order_id").agg(
    pl.col("tag").implode().alias("tags")
)
```

This creates list-valued results.

Depending on the task, grouping a column directly may also create list output:

```python
df.group_by("order_id").agg(
    pl.col("tag").alias("tags")
)
```

The exact shape should be checked in your installed Polars version.

---

# 73. `group_by_dynamic()`

Ordinary grouping:

```python
df.group_by("customer_id")
```

groups by discrete keys.

Dynamic grouping creates time/index-based windows.

Example:

```python
daily = (
    df.sort("timestamp")
      .group_by_dynamic(
          "timestamp",
          every="1d",
      )
      .agg(
          pl.col("amount").sum().alias("daily_revenue")
      )
)
```

This is useful for:

- daily revenue,
- hourly events,
- periodic operational metrics.

Current Polars documentation defines dynamic windows through parameters such as `every`, `period`, `offset`, boundaries, labeling, and grouping. citeturn700248search8

---

# 74. Dynamic vs Ordinary Grouping

Ordinary:

```text
same discrete key
→ same group
```

Dynamic:

```text
time value
→ assigned to a time window
```

The business question determines which model you need.

---

# 75. Rolling Operations

A rolling operation uses a moving window around each observation.

Conceptually:

```text
timestamp
1 2 3 4 5

rolling window:
[1]
[1 2]
[2 3]
[3 4]
[4 5]
```

Typical use:

- moving average,
- rolling sum,
- recent-period metric,
- anomaly feature.

Use a sorted temporal column and verify the current rolling API in your installed version.

---

# 76. Rolling vs Dynamic

```text
dynamic
→ time windows as groups

rolling
→ moving window relative to an observation
```

Example business difference:

```text
daily revenue
→ dynamic grouping

7-day moving average
→ rolling
```

---

# 77. Expression Parallelism

Suppose you have:

```python
df.with_columns(
    (pl.col("amount") * 1.18).alias("gross_amount"),
    (pl.col("amount") * 0.18).alias("tax"),
    (pl.col("quantity") * pl.col("price")).alias("calculated_total"),
)
```

These expressions are independently described.

Grouping them into one transformation can give the engine more opportunity to execute independent work efficiently.

The key is not to memorize:

> "One call is always faster."

The correct statement is:

> Grouping logically independent native expressions can expose more parallel work and reduce unnecessary pipeline fragmentation.

Measure performance when it matters.

---

# 78. When Separate `with_columns()` Calls Are Still Reasonable

Do not over-optimize structure.

Separate stages can improve clarity when:

```text
step 1 creates column used by step 2
```

or:

```text
business stage A
→ validation
→ business stage B
```

A reasonable pipeline may be:

```python
df = df.with_columns(...)
df = df.with_columns(...)
```

if each stage has a meaningful dependency or business boundary.

Use one call for independent related expressions where that improves clarity and execution opportunities.

---

# 79. Python UDFs and `map_elements()`

Polars provides:

```python
map_elements()
```

for applying Python functions to individual elements.

Example:

```python
df.with_columns(
    pl.col("amount")
      .map_elements(
          lambda x: x * 1.18,
          return_dtype=pl.Float64,
      )
      .alias("gross_amount")
)
```

This is an escape hatch, not the default transformation style.

Polars' official documentation warns that `map_elements()` is much slower than native expressions and recommends using it only when the logic cannot be implemented otherwise. citeturn700248search4

---

# 80. Why `map_elements()` Can Be Expensive

Potential costs include:

- Python function calls per element,
- Python interpreter overhead,
- reduced native execution,
- reduced optimizer visibility,
- GIL-related constraints around Python callbacks,
- inability to use the same native execution path as built-in expressions.

### Important nuance

Not every UDF is equally expensive.

The right engineering approach is:

```text
Can native Polars express this?
    ↓
YES → use native expression

NO
    ↓
Is a Python UDF truly required?
    ↓
YES → isolate + benchmark + document
```

---

# 81. Native Alternative Example

Bad for a simple operation:

```python
pl.col("name").map_elements(
    lambda x: x.lower(),
)
```

Prefer:

```python
pl.col("name").str.to_lowercase()
```

Bad:

```python
pl.col("amount").map_elements(
    lambda x: x * 2,
    return_dtype=pl.Float64,
)
```

Prefer:

```python
pl.col("amount") * 2
```

The native form keeps the logic in the Polars expression system.

---

# 82. `map_elements()` Before/After Exercise

### Version A

```python
slow = df.with_columns(
    pl.col("amount")
      .map_elements(
          lambda x: x * 1.18,
          return_dtype=pl.Float64,
      )
      .alias("gross_amount")
)
```

### Version B

```python
native = df.with_columns(
    (pl.col("amount") * 1.18)
      .alias("gross_amount")
)
```

Compare:

```text
business result
readability
execution model
runtime
memory
```

Do not invent benchmark numbers.

---

# 83. Benchmarking the Native vs UDF Versions

```python
from time import perf_counter

import polars as pl


N = 2_000_000

df = pl.DataFrame(
    {
        "amount": [float(i) for i in range(N)]
    }
)


def benchmark(label, fn, repeats=3):
    fn()  # warm-up

    times = []

    for _ in range(repeats):
        start = perf_counter()
        fn()
        times.append(perf_counter() - start)

    print(
        label,
        "avg_seconds=",
        sum(times) / len(times),
    )


benchmark(
    "native",
    lambda: df.with_columns(
        (pl.col("amount") * 1.18)
        .alias("gross_amount")
    ),
)

benchmark(
    "map_elements",
    lambda: df.with_columns(
        pl.col("amount")
          .map_elements(
              lambda x: x * 1.18,
              return_dtype=pl.Float64,
          )
          .alias("gross_amount")
    ),
)
```

Record:

```text
Python version
Polars version
CPU
RAM
row count
repetitions
observed timings
```

Benchmark values are machine- and workload-dependent.

---

# 84. Pandas-to-Polars Translation Method

Do not translate syntax mechanically.

Translate **intent**.

```text
Pandas operation
    ↓
What business operation does this represent?
    ↓
What output shape is required?
    ↓
Which Polars context represents that shape?
    ↓
Which expressions implement the logic?
```

---

# 85. Fifteen Pandas-to-Polars Translations

## 85.1 Selection

Pandas:

```python
df[["customer_id", "amount"]]
```

Polars:

```python
df.select(
    "customer_id",
    "amount",
)
```

Context:

```text
select
```

---

## 85.2 Filtering

Pandas:

```python
df[df["amount"] > 100]
```

Polars:

```python
df.filter(
    pl.col("amount") > 100
)
```

Context:

```text
filter
```

---

## 85.3 Derived Column

Pandas:

```python
df["gross"] = df["amount"] * 1.18
```

Polars:

```python
df.with_columns(
    (pl.col("amount") * 1.18)
    .alias("gross")
)
```

---

## 85.4 Type Conversion

Pandas:

```python
df["customer_id"] = df["customer_id"].astype("int64")
```

Polars:

```python
df.with_columns(
    pl.col("customer_id").cast(pl.Int64)
)
```

---

## 85.5 Null Filling

Pandas:

```python
df["amount"] = df["amount"].fillna(0)
```

Polars:

```python
df.with_columns(
    pl.col("amount").fill_null(0)
)
```

---

## 85.6 String Normalization

Pandas:

```python
df["country"] = df["country"].str.lower()
```

Polars:

```python
df.with_columns(
    pl.col("country")
      .str.to_lowercase()
      .alias("country")
)
```

---

## 85.7 Datetime Extraction

Pandas:

```python
df["year"] = df["created_at"].dt.year
```

Polars:

```python
df.with_columns(
    pl.col("created_at")
      .dt.year()
      .alias("year")
)
```

---

## 85.8 Grouped Sum

Pandas:

```python
df.groupby("customer_id", as_index=False)["amount"].sum()
```

Polars:

```python
df.group_by("customer_id").agg(
    pl.col("amount").sum().alias("amount")
)
```

---

## 85.9 Group Mean

Pandas:

```python
df.groupby("customer_id")["amount"].mean()
```

Polars:

```python
df.group_by("customer_id").agg(
    pl.col("amount").mean().alias("avg_amount")
)
```

---

## 85.10 Groupby Transform

Pandas:

```python
df["customer_total"] = (
    df.groupby("customer_id")["amount"]
      .transform("sum")
)
```

Polars:

```python
df.with_columns(
    pl.col("amount")
      .sum()
      .over("customer_id")
      .alias("customer_total")
)
```

---

## 85.11 Join

Pandas:

```python
df.merge(
    customers,
    on="customer_id",
    how="left",
)
```

Polars:

```python
df.join(
    customers,
    on="customer_id",
    how="left",
)
```

---

## 85.12 Deduplication

Pandas:

```python
df.sort_values("updated_at").drop_duplicates(
    "order_id",
    keep="last",
)
```

Polars concept:

```python
(
    df.sort("updated_at")
      .unique(
          subset=["order_id"],
          keep="last",
      )
)
```

Verify the exact signature for the installed release.

---

## 85.13 Conditional Logic

Pandas:

```python
import numpy as np

df["class"] = np.where(
    df["amount"] >= 1000,
    "HIGH",
    "NORMAL",
)
```

Polars:

```python
df.with_columns(
    pl.when(pl.col("amount") >= 1000)
      .then(pl.lit("HIGH"))
      .otherwise(pl.lit("NORMAL"))
      .alias("class")
)
```

---

## 85.14 Explode

Pandas:

```python
df.explode("tags")
```

Polars:

```python
df.explode("tags")
```

The method name is similar; the surrounding expression model is what you must learn.

---

## 85.15 Time-Based Aggregation

Pandas often uses resampling.

Polars can use:

```python
(
    df.sort("timestamp")
      .group_by_dynamic(
          "timestamp",
          every="1d",
      )
      .agg(
          pl.col("amount")
            .sum()
            .alias("daily_revenue")
      )
)
```

Verify exact current API parameters for your installed version.

---

# 86. Mandatory `.over()` Translation Lab

Complete at least these three.

## Example 1

Pandas:

```python
df.groupby("customer_id")["amount"].transform("sum")
```

Polars:

```python
pl.col("amount").sum().over("customer_id")
```

---

## Example 2

Pandas:

```python
df.groupby("customer_id")["amount"].transform("mean")
```

Polars:

```python
pl.col("amount").mean().over("customer_id")
```

---

## Example 3

Pandas:

```python
df.groupby("customer_id")["amount"].transform("max")
```

Polars:

```python
pl.col("amount").max().over("customer_id")
```

For every translation, explain:

```text
input grain
→ grouping
→ operation
→ retained row shape
```

---

# 87. Production Orders Example

A realistic eager pipeline can look like:

```text
raw orders
    ↓
typed DataFrame
    ↓
deduplicate
    ↓
validate reference joins
    ↓
customer metrics
    ↓
window metrics
    ↓
time-aware FX matching
    ↓
daily revenue
    ↓
Parquet
```

This topic stays in **eager mode**.

Lazy execution belongs to Topic 03.

---

# 88. Example Orders DataFrame

```python
from datetime import datetime, timezone

import polars as pl


status_type = pl.Enum([
    "PAID",
    "PENDING",
    "CANCELLED",
])


orders = pl.DataFrame(
    {
        "order_id": ["O1", "O2", "O3", "O4"],
        "customer_id": [100, 100, 200, 200],
        "product_id": [10, 20, 10, 30],
        "amount": [100.0, 200.0, 300.0, 50.0],
        "quantity": [1, 2, 3, 1],
        "status": ["PAID", "PAID", "PENDING", "PAID"],
        "created_at": [
            datetime(2026, 9, 26, 10, 0, tzinfo=timezone.utc),
            datetime(2026, 9, 26, 11, 0, tzinfo=timezone.utc),
            datetime(2026, 9, 26, 12, 0, tzinfo=timezone.utc),
            datetime(2026, 9, 26, 13, 0, tzinfo=timezone.utc),
        ],
        "currency": ["INR", "INR", "INR", "INR"],
    },
    schema_overrides={
        "status": status_type,
    },
)

print(orders.schema)
```

---

# 89. Latest Version Per Order

Suppose the source can emit several versions.

You need an explicit definition of "latest."

Example:

```python
latest = (
    orders
    .sort(["order_id", "created_at"])
    .unique(
        subset=["order_id"],
        keep="last",
    )
)
```

### Important

The sorting column must represent the true update/version sequence.

Do not call something "latest" merely because it happens to be last in the file.

---

# 90. Customer Metrics

```python
customer_metrics = (
    latest
    .group_by("customer_id")
    .agg(
        pl.len().alias("order_count"),
        pl.col("amount").sum().alias("customer_total"),
        pl.col("amount").mean().alias("customer_average"),
    )
)
```

This produces:

```text
one row per customer
```

---

# 91. Attach Customer Total to Each Order

```python
orders_enriched = latest.with_columns(
    pl.col("amount")
      .sum()
      .over("customer_id")
      .alias("customer_total")
)
```

Then:

```python
orders_enriched = orders_enriched.with_columns(
    (
        pl.col("amount")
        / pl.col("customer_total")
    ).alias("order_share")
)
```

Handle zero totals explicitly if they are possible in your domain.

---

# 92. Customer Join

```python
customers = pl.DataFrame(
    {
        "customer_id": [100, 200],
        "customer_name": ["Alice", "Bob"],
        "segment": ["Gold", "Silver"],
    }
)

enriched = orders_enriched.join(
    customers,
    on="customer_id",
    how="left",
    validate="m:1",
)
```

Expected grain:

```text
many orders
→ one customer record
```

---

# 93. Product Join

```python
products = pl.DataFrame(
    {
        "product_id": [10, 20, 30],
        "product_name": ["A", "B", "C"],
        "category": ["X", "Y", "Z"],
    }
)

enriched = enriched.join(
    products,
    on="product_id",
    how="left",
    validate="m:1",
)
```

Again, validation protects the expected relationship.

---

# 94. FX As-Of Matching

For historical currency conversion:

```text
transaction timestamp
+
currency
→
latest applicable FX rate
```

Make sure:

```text
timestamp is sorted
timestamp semantics match
currency is included in matching when required
strategy matches the business rule
```

Use `join_asof()` only when the temporal matching semantics are correct.

---

# 95. Daily Revenue

```python
daily_revenue = (
    enriched
    .sort("created_at")
    .group_by_dynamic(
        "created_at",
        every="1d",
    )
    .agg(
        pl.col("amount")
          .sum()
          .alias("daily_revenue")
    )
)
```

For production:

```text
timezone
business date
window boundary
missing days
currency treatment
```

must be explicit.

---

# 96. Correctness Validation

Use:

```python
from polars.testing import assert_frame_equal
```

When comparing two Polars outputs:

```python
expected = expected.sort(
    ["customer_id", "order_id"]
)

actual = actual.sort(
    ["customer_id", "order_id"]
)

assert_frame_equal(
    expected,
    actual,
)
```

Before comparing, normalize only differences that are not semantically meaningful.

---

# 97. Testing Beyond Values

A strong pipeline test checks:

```text
column names
dtypes
null behaviour
timezone
row count
duplicate key handling
boundary timestamps
output grain
```

Do not make tests only:

```python
assert result.height == 100
```

A dataset can have 100 rows and still be wrong.

---

# 98. Production Testing Pattern

Test at least:

```text
normal input
empty input
single row
null-heavy input
duplicate keys
unexpected status
timestamp boundaries
missing reference records
join explosion
zero denominator
```

This is where Data Engineering becomes software engineering.

---

# 99. Performance Perspective

Important performance levers in eager Polars include:

- typed data,
- native expressions,
- fewer Python callbacks,
- validated joins,
- avoiding unnecessary row explosion,
- sensible expression grouping,
- minimizing representation changes.

Think:

```text
business rule
    ↓
native expression
    ↓
engine
```

rather than:

```text
business rule
    ↓
Python callback per row
```

---

# 100. Performance Experiment: Native vs UDF

Benchmark:

```text
amount * 1.18
```

using:

```text
native expression
vs
map_elements()
```

Use the benchmark function from the earlier section.

Do not report a universal ratio.

Report:

```text
machine
data size
Polars version
observed times
```

---

# 101. Performance Experiment: Selectors

Compare code maintenance rather than only runtime.

Explicit:

```python
pl.col(
    "amount_usd",
    "amount_eur",
    "amount_gbp",
)
```

Selector:

```python
cs.starts_with("amount_")
```

Ask:

```text
Which is easier to review?
Which is safer as schema evolves?
What new columns could be included unintentionally?
```

This is an architecture question as much as a syntax question.

---

# 102. Performance Experiment: `.over()` vs Aggregate + Join

Approach A:

```python
df.with_columns(
    pl.col("amount")
      .sum()
      .over("customer_id")
      .alias("customer_total")
)
```

Approach B:

```text
group_by customer
    ↓
aggregate
    ↓
join aggregate back
```

Compare:

- runtime,
- intermediate data,
- code complexity,
- memory.

The semantic goal is the main decision:

```text
Need original rows + group metric?
→ .over()

Need group summary?
→ group_by().agg()
```

Do not assume one is universally faster.

---

# 103. Production Pipeline Review Questions

A senior Data Engineer reviewing Polars code asks:

```text
What is the input grain?
What is the output grain?
What is the schema?
Which context is being used?
Why this context?
Which expressions are native?
Could a UDF be removed?
What is the join cardinality?
Is validate= appropriate?
Can this join multiply rows?
Are timestamps correctly typed?
Is null vs NaN intentional?
Are selectors safe?
Is output order meaningful?
Is the eager model sufficient for dataset size?
```

---

# 104. Debugging — Wrong Boolean Operator

### Broken

```python
df.filter(
    pl.col("amount") > 100
    and pl.col("status") == "PAID"
)
```

### Correct

```python
df.filter(
    (pl.col("amount") > 100)
    & (pl.col("status") == "PAID")
)
```

### Production lesson

Do not confuse Python scalar Boolean logic with Polars expression logic.

---

# 105. Debugging — Unexpected Dtype

### Symptom

Arithmetic or join behaviour is unexpected.

### Diagnosis

```python
print(df.schema)
print(df.dtypes)
```

### Causes

- inference,
- mixed source values,
- schema drift,
- missing explicit cast.

### Fix

Define the intended schema or cast explicitly.

---

# 106. Debugging — Null vs NaN

### Symptom

Your missing-value checks disagree.

### Diagnosis

```python
df.select(
    pl.col("value").is_null(),
    pl.col("value").is_nan(),
)
```

### Production lesson

Null and NaN are different data-quality states.

---

# 107. Debugging — Wrong Context

### Symptom

Original columns disappear.

### Likely cause

Using:

```python
select()
```

when you intended:

```python
with_columns()
```

### Fix

Choose context based on output shape.

---

# 108. Debugging — Join Explosion

### Symptom

Revenue doubles or row count jumps.

### Diagnosis

Check key counts:

```python
(
    customers
    .group_by("customer_id")
    .agg(pl.len().alias("count"))
    .filter(pl.col("count") > 1)
)
```

Then verify the expected relationship.

### Fix

Deduplicate/normalize as appropriate and add:

```python
validate="m:1"
```

where valid.

---

# 109. Debugging — `join_asof()`

### Symptom

Wrong historical rate is selected.

### Check

```text
sorted timestamps
strategy
timezone
time unit
grouping key
boundary semantics
```

### Production lesson

An as-of join is a temporal business rule, not simply another join type.

---

# 110. Debugging — `map_elements()`

### Symptom

A simple transformation is unexpectedly slow.

### Check

```python
.map_elements(...)
```

### Question

Can the logic be written with:

```text
.str
.dt
.list
.struct
arithmetic
conditional expressions
aggregations
window expressions
```

If yes, use the native expression.

---

# 111. Debugging — Unexpected Aggregation Shape

### Symptom

You expected one row per input row, but got one row per group.

### Cause

```python
group_by().agg()
```

was used.

### Fix

Use:

```python
.over(...)
```

when the group-wise value must stay attached to each original row.

---

# 112. Debugging — Incorrect `.over()`

### Symptom

Group-derived values appear to be calculated across the wrong records.

### Diagnosis

Check the partition key:

```python
.over("customer_id")
```

or:

```python
.over(["customer_id", "currency"])
```

depending on the business definition.

### Production lesson

Window partitioning defines the analytical population.

---

# 113. Debugging — Datetime/Timezone Mismatch

### Symptom

Temporal joins or grouping produce errors or incorrect values.

### Diagnosis

```python
print(df.schema)
```

Check:

```text
Date vs Datetime
time unit
timezone
sorting
```

---

# 114. Common Mistakes

## 114.1 Writing pandas-style row loops

Avoid row-by-row Python when native Polars can express the transformation.

## 114.2 Unnecessary separate `with_columns()`

Group independent expressions when doing so improves clarity and execution opportunities.

## 114.3 Using `map_elements()` for native functionality

Prefer:

```python
.str
.dt
.list
.struct
```

and other native expressions.

## 114.4 Forgetting output order

Grouped and joined outputs should not be assumed to have a business order unless explicitly ordered.

## 114.5 Ignoring join cardinality

A left join can still duplicate rows.

---

# 115. Production Pattern — Validate Before Enriching

```text
raw dimension
     ↓
key uniqueness test
     ↓
deduplicate/version handling
     ↓
validated join
     ↓
row-count reconciliation
```

This pattern protects correctness.

---

# 116. Production Pattern — Native Transformation Functions

Structure business transformations into testable functions:

```python
import polars as pl


def add_gross_amount(
    df: pl.DataFrame,
) -> pl.DataFrame:
    return df.with_columns(
        (pl.col("amount") * 1.18)
        .alias("gross_amount")
    )


def customer_metrics(
    df: pl.DataFrame,
) -> pl.DataFrame:
    return (
        df.group_by("customer_id")
          .agg(
              pl.len().alias("order_count"),
              pl.col("amount")
                .sum()
                .alias("customer_total"),
          )
    )
```

The code is:

```text
typed
composable
testable
readable
```

---

# 117. Testing a Transformation

```python
import polars as pl
from polars.testing import assert_frame_equal


def add_gross_amount(
    df: pl.DataFrame,
) -> pl.DataFrame:
    return df.with_columns(
        (pl.col("amount") * 1.18)
        .alias("gross_amount")
    )


def test_add_gross_amount() -> None:
    source = pl.DataFrame(
        {
            "amount": [100.0, 200.0],
        }
    )

    actual = add_gross_amount(source)

    expected = pl.DataFrame(
        {
            "amount": [100.0, 200.0],
            "gross_amount": [118.0, 236.0],
        }
    )

    assert_frame_equal(actual, expected)
```

Add edge cases for:

- null,
- empty,
- boundary values.

---

# 118. Mandatory Hands-On Project — `polars_orders.py`

Implement the roadmap exercise in eager Polars.

Required steps:

```text
1. typed input
2. latest version per order
3. customer metrics
4. .over() customer total/share
5. validated customer join
6. validated product join
7. join_asof() FX
8. group_by_dynamic() daily revenue
9. pandas correctness comparison
10. benchmark pandas vs Polars
```

---

# 119. Project Step 1 — Typed Input

Use:

```text
schema_overrides
```

Use:

```text
Enum for status
UTC-aware Datetime
```

Verify the exact current constructor and reader syntax in your installed version.

---

# 120. Project Step 2 — Latest Version

Use:

```python
sort(...)
unique(...)
```

or another appropriate eager approach.

Explain:

```text
What column defines recency?
What happens on ties?
What happens when an order has multiple versions?
```

---

# 121. Project Step 3 — Customer Metrics

Use:

```python
group_by().agg()
```

for:

```text
order count
customer total
customer average
```

Then use:

```python
.over(...)
```

for:

```text
customer total attached to each order
```

---

# 122. Project Step 4 — Order Share

```python
(
    pl.col("amount")
    / pl.col("customer_total")
).alias("order_share")
```

Handle:

```text
null amount
zero customer total
```

intentionally.

---

# 123. Project Step 5 — Validated Joins

Customers:

```python
validate="m:1"
```

Products:

```python
validate="m:1"
```

Add tests where the dimension contains duplicate keys.

---

# 124. Project Step 6 — FX

Implement:

```text
transaction timestamp
→ historical FX rate
```

with:

```python
join_asof(...)
```

Test:

```text
exact match
between rates
before first rate
after last rate
```

and define business behaviour for missing rates.

---

# 125. Project Step 7 — Daily Revenue

Use:

```python
group_by_dynamic(...)
```

on the typed timestamp.

Define:

```text
timezone
day boundary
window semantics
```

---

# 126. Project Step 8 — pandas Correctness

Run both implementations on the same input.

Normalize:

```text
row ordering
expected column order
comparison dtypes
```

Then compare.

If values differ, investigate the semantics before coercing the outputs.

---

# 127. Project Step 9 — Benchmark

Compare:

```text
pandas
Polars eager
```

Use the same dataset and workload.

Record:

```text
data size
rows
runtime
peak memory
machine
versions
```

Do not fabricate results.

---

# 128. Conceptual Project Architecture

```text
polars_lab/
├── data/
├── src/
│   └── polars_orders.py
├── tests/
└── benchmarks/
```

This section describes architecture only.

---

# 129. Senior Data Engineer Decision Framework

Before choosing a Polars operation, ask:

```text
1. What is the business intent?
2. What is the input grain?
3. What is the required output grain?
4. What is the schema?
5. What context represents the output?
6. Can the operation be native?
7. Is the join cardinality known?
8. Are time semantics explicit?
9. Can row count multiply?
10. What should be tested?
```

This is more important than memorizing syntax.

---

# 130. Interview Preparation — Beginner

## Q1. What is a Polars expression?

A symbolic description of a computation over data. It is evaluated in a context to produce a concrete result.

## Q2. What does `pl.col("amount")` do?

Creates an expression referencing the `amount` column.

## Q3. What does `pl.lit(10)` do?

Represents a constant value inside an expression.

## Q4. What is `select()`?

A context for defining the output columns/results from expressions.

## Q5. What is `with_columns()`?

A context that retains existing columns and adds or replaces columns.

## Q6. What does `filter()` do?

Keeps rows where the predicate expression evaluates to true.

## Q7. What does `group_by().agg()` do?

Groups rows and applies aggregation expressions, generally producing grouped output with fewer rows.

---

# 131. Interview Preparation — Intermediate

## Q8. Why does Polars not use a pandas-style index?

Polars chooses explicit key-, row-, and expression-based semantics instead of pandas-style index alignment.

## Q9. Why are explicit dtypes important?

They make pipeline semantics predictable and improve validation and interoperability.

## Q10. What is the difference between null and NaN?

Null means missing; NaN is a floating-point special value.

## Q11. What is a semi join?

Keeps left rows for which matching right keys exist without appending right-side columns.

## Q12. What is an anti join?

Keeps left rows for which no matching right key exists.

## Q13. Why validate join cardinality?

To catch broken key assumptions before the join multiplies rows and corrupts metrics.

## Q14. When do you use `join_asof()`?

For ordered time-aware matching, such as the latest FX rate applicable to a transaction.

---

# 132. Interview Preparation — Advanced

## Q15. Why can native expressions outperform Python UDFs?

Native expressions stay inside the engine's optimized execution path and avoid per-element Python callback overhead.

## Q16. Why is `map_elements()` a poor default?

Because it introduces Python-level element processing and is generally much slower than equivalent native expressions. citeturn700248search4

## Q17. `.over()` vs `group_by().agg()`?

`group_by().agg()` reduces to grouped output. `.over()` computes within partitions while retaining original rows.

## Q18. `.over()` vs pandas `transform()`?

They often express the same analytical intent: group-wise computation while preserving row shape.

## Q19. `.over()` vs SQL window functions?

Polars `.over()` corresponds conceptually to SQL window expressions such as `SUM(...) OVER (PARTITION BY ...)`.

## Q20. What causes join explosion?

Duplicate keys on one or both sides of a join can create many matching combinations.

## Q21. How do you protect an `m:1` join?

Validate key uniqueness and specify:

```python
validate="m:1"
```

## Q22. Why can broad selectors be dangerous?

New columns matching the selector can automatically become part of the transformation.

## Q23. Why use explicit `Enum`?

When the category domain is known and should be represented explicitly.

---

# 133. Senior Architecture Questions

## Q24

A transaction table joins to a customer table and revenue increases 30%. What do you inspect?

Answer:

```text
input grain
join key uniqueness
duplicate customer rows
expected cardinality
null keys
versioned records
actual output row count
```

## Q25

A team uses `map_elements()` everywhere. What do you do?

Inventory the UDFs and replace those that have native equivalents. Keep only unavoidable Python logic, isolated and benchmarked.

## Q26

A 500-column table is growing. How can selectors help?

They express selection rules based on dtype/name rather than repeated column lists.

## Q27

How can selectors become risky?

The transformation may automatically start including future columns that happen to match the selector.

## Q28

When is `.over()` better than aggregate + join?

When you need a group-derived metric on every original row.

## Q29

When should you use `group_by().agg()`?

When the required output is grouped/reduced rather than original-row-shaped.

## Q30

Why should timestamps be treated as schema?

Because unit, timezone, and temporal semantics affect joins, grouping, ordering, and business correctness.

---

# 134. Explain-Aloud Exercises

## E1

Explain:

```python
(pl.col("amount") * 1.18).alias("gross_amount")
```

without merely saying:

> "It multiplies the amount."

Include:

```text
column reference
constant
operation
derived expression
output name
```

## E2

Explain why:

```python
select()
```

differs from:

```python
with_columns()
```

## E3

Explain:

```python
group_by().agg()
```

in terms of output grain.

## E4

Explain:

```python
pl.col("amount").sum().over("customer_id")
```

in terms of partitioning and retained rows.

## E5

Explain why:

```python
validate="m:1"
```

can prevent a metric-corruption incident.

## E6

Explain why native expressions are preferred to `map_elements()` when both can implement the same business rule.

## E7

Explain the difference between:

```text
null
NaN
```

## E8

Explain a join explosion using actual numbers.

---

# 135. Practice Problems — Level 1 Basic

## B1

Create a DataFrame with `name` and `amount` and select both.

## B2

Create `gross_amount = amount * 1.18`.

## B3

Filter amounts above 500.

## B4

Create an `order_class` using `when/then/otherwise`.

## B5

Cast an ID to `Int64`.

## B6

Select all numeric columns.

## B7

Lowercase a string column.

## B8

Extract year from a datetime.

## B9

Calculate customer revenue.

## B10

Explain `select` vs `with_columns`.

---

# 136. Level 1 Answer Key

### B1

```python
df.select("name", "amount")
```

### B2

```python
df.with_columns(
    (pl.col("amount") * 1.18).alias("gross_amount")
)
```

### B3

```python
df.filter(pl.col("amount") > 500)
```

### B4

```python
df.with_columns(
    pl.when(pl.col("amount") >= 1000)
      .then(pl.lit("HIGH"))
      .otherwise(pl.lit("NORMAL"))
      .alias("order_class")
)
```

### B5

```python
df.with_columns(
    pl.col("id").cast(pl.Int64)
)
```

### B6

```python
df.select(cs.numeric())
```

### B7

```python
df.with_columns(
    pl.col("name").str.to_lowercase()
)
```

### B8

```python
df.with_columns(
    pl.col("created_at").dt.year().alias("year")
)
```

### B9

```python
df.group_by("customer_id").agg(
    pl.col("amount").sum().alias("total")
)
```

### B10

`select` defines output expressions; `with_columns` keeps existing columns and adds/replaces columns.

---

# 137. Practice Problems — Level 2 Moderate

## M1

Add `gross_amount` and `tax` in one `with_columns()` call.

## M2

Filter by amount and status.

## M3

Use `cs.numeric()` to fill numeric nulls.

## M4

Create a Categorical column.

## M5

Create an Enum status type.

## M6

Calculate count, sum, mean, min, max per customer.

## M7

Perform a left join.

## M8

Find valid foreign keys with a semi join.

## M9

Find invalid foreign keys with an anti join.

## M10

Attach customer totals with `.over()`.

---

# 138. Level 2 Answer Key

### M1

```python
df.with_columns(
    (pl.col("amount") * 1.18).alias("gross_amount"),
    (pl.col("amount") * 0.18).alias("tax"),
)
```

### M2

```python
df.filter(
    (pl.col("amount") > 100)
    & (pl.col("status") == "PAID")
)
```

### M3

```python
df.with_columns(
    cs.numeric().fill_null(0)
)
```

Verify that every selected numeric column should receive this rule.

### M4

```python
df.with_columns(
    pl.col("country").cast(pl.Categorical)
)
```

### M5

```python
pl.Enum([
    "PAID",
    "PENDING",
    "CANCELLED",
])
```

### M6

```python
df.group_by("customer_id").agg(
    pl.len().alias("count"),
    pl.col("amount").sum().alias("sum"),
    pl.col("amount").mean().alias("mean"),
    pl.col("amount").min().alias("min"),
    pl.col("amount").max().alias("max"),
)
```

### M7

```python
orders.join(
    customers,
    on="customer_id",
    how="left",
)
```

### M8

```python
orders.join(
    customers,
    on="customer_id",
    how="semi",
)
```

### M9

```python
orders.join(
    customers,
    on="customer_id",
    how="anti",
)
```

### M10

```python
df.with_columns(
    pl.col("amount")
      .sum()
      .over("customer_id")
      .alias("customer_total")
)
```

---

# 139. Practice Problems — Level 3 Hard

## H1

Identify duplicate customer keys before an `m:1` join.

## H2

Calculate order share of customer total.

## H3

Rank orders within customer.

## H4

Normalize email and derive a domain using native string expressions.

## H5

Calculate daily revenue.

## H6

Explode order tags and count tags.

## H7

Reconstruct tags after processing.

## H8

Use a semi join for valid references.

## H9

Apply a null-fill rule to numeric columns using selectors.

## H10

Replace a simple Python UDF with native Polars.

---

# 140. Level 3 Answer Key

### H1

```python
duplicates = (
    customers
    .group_by("customer_id")
    .agg(pl.len().alias("count"))
    .filter(pl.col("count") > 1)
)
```

Then use:

```python
validate="m:1"
```

on the join.

### H2

```python
df.with_columns(
    pl.col("amount")
      .sum()
      .over("customer_id")
      .alias("customer_total")
).with_columns(
    (
        pl.col("amount")
        / pl.col("customer_total")
    ).alias("order_share")
)
```

Add zero-denominator handling if required.

### H3

Use a rank expression with:

```python
.over("customer_id")
```

and verify tie semantics.

### H4

Use `.str` operations.

### H5

```python
(
    df.sort("timestamp")
      .group_by_dynamic("timestamp", every="1d")
      .agg(
          pl.col("amount").sum().alias("daily_revenue")
      )
)
```

### H6

```python
(
    df.explode("tags")
      .group_by("tags")
      .agg(pl.len().alias("tag_count"))
)
```

### H7

Group processed tag rows and collect them into a list using native list aggregation.

### H8

Use:

```python
how="semi"
```

### H9

```python
df.with_columns(
    cs.numeric().fill_null(0)
)
```

### H10

Replace the callback with the equivalent native expression.

---

# 141. Practice Problems — Level 4 Advanced

## A1

Design an eager transaction-to-customer enrichment pipeline with cardinality validation.

## A2

Attach each transaction's account total without changing row count.

## A3

Explain why `.over()` can be simpler than aggregate + join for retained-row metrics.

## A4

A left key appears 100 times and a right key appears 50 times. What is the maximum many-to-many multiplication for that key?

## A5

Design a native-vs-UDF benchmark.

## A6

Design an explicit schema strategy for evolving CSV inputs.

## A7

Design an Enum strategy for fixed status values.

## A8

Design an FX `join_asof()` rule.

## A9

Design safe selectors for a wide dataset.

## A10

Review a Polars pipeline and identify pandas-style procedural thinking.

---

# 142. Level 4 Answer Key

### A1

```text
validate dimension uniqueness
→ use m:1
→ join
→ reconcile row counts
```

### A2

```python
pl.col("amount")
  .sum()
  .over("account_id")
```

### A3

`.over()` directly describes a partitioned calculation while preserving original rows.

### A4

```text
100 × 50 = 5,000
```

possible matching rows for that key.

### A5

Same input, same workload, same machine, warm-up, multiple repetitions, runtime measurement, and memory where relevant.

### A6

Define expected schema, use `schema=` or `schema_overrides=`, and define how invalid values are handled.

### A7

Use `Enum` when the valid category set is intentionally fixed.

### A8

Define:

```text
event timestamp
rate timestamp
ordering
strategy
grouping key
timezone
boundary behaviour
```

### A9

Prefer selectors that match the intended schema rule and document which future columns can be included.

### A10

Look for:

```text
row loops
Python callbacks
unnecessary conversion
imperative per-column repetition
unvalidated joins
unclear output grain
```

---

# 143. Final Mastery Assessment

Do not read the answer key until all sections are attempted.

---

## Part A — Conceptual Understanding (15)

### Q1
Explain Polars without saying "faster pandas."

### Q2
Why does Polars use expressions?

### Q3
Why does an expression need a context?

### Q4
DataFrame vs expression?

### Q5
Why no pandas-style index?

### Q6
What does immutability mean?

### Q7
Why do explicit dtypes matter?

### Q8
`select()` vs `with_columns()`?

### Q9
`filter()` vs `group_by().agg()`?

### Q10
Null vs NaN?

### Q11
Why validate joins?

### Q12
What problem does `join_asof()` solve?

### Q13
Why is `.over()` different from `group_by().agg()`?

### Q14
Why can `map_elements()` be expensive?

### Q15
Why are benchmark results not universal truths?

---

# 144. Part A Answer Key

1. Polars is a typed, expression-oriented, columnar DataFrame engine designed for efficient analytical processing and native execution.
2. Expressions let you describe transformations at the column level.
3. The context determines how the expression is evaluated and what output shape it participates in.
4. A DataFrame is concrete data; an expression describes a computation.
5. Polars chooses explicit key/row semantics rather than pandas-style index alignment.
6. Transformations return derived results rather than relying on mutable DataFrame state.
7. Explicit dtypes improve predictability, validation, and interoperability.
8. `select` defines output expressions; `with_columns` preserves existing columns while adding/replacing.
9. `filter` removes rows; `group_by().agg()` groups and usually reduces rows.
10. Null means missing; NaN is a floating-point special value.
11. To detect violated key relationships before metrics are corrupted by row multiplication.
12. Time-aware matching such as latest applicable FX rate.
13. `group_by().agg()` reduces rows; `.over()` retains them.
14. It invokes Python-level element processing and can leave the native execution path.
15. Hardware, data size, workload, versions, caching, and operations influence measurements.

---

# 145. Part B — Expression and Context Selection (15)

Choose the primary operation.

### Q1
Return only `customer_id` and `amount`.

### Q2
Add `gross_amount`.

### Q3
Keep only paid orders.

### Q4
Return one row per customer with total revenue.

### Q5
Keep all orders and attach customer total.

### Q6
Add three independent derived columns.

### Q7
Filter amount > 1000 and currency = INR.

### Q8
Calculate average amount by product.

### Q9
Attach product average to every order.

### Q10
Select all numeric columns.

### Q11
Normalize emails.

### Q12
Keep orders whose customer exists.

### Q13
Find orders whose customer does not exist.

### Q14
Explode tags.

### Q15
Calculate daily revenue.

---

# 146. Part B Answer Key

| Question | Answer |
|---|---|
| Q1 | `select` |
| Q2 | `with_columns` |
| Q3 | `filter` |
| Q4 | `group_by().agg()` |
| Q5 | `.over()` |
| Q6 | `with_columns` |
| Q7 | `filter` |
| Q8 | `group_by().agg()` |
| Q9 | `.over()` |
| Q10 | `select(cs.numeric())` |
| Q11 | `with_columns` + `.str` |
| Q12 | semi join |
| Q13 | anti join |
| Q14 | `explode` |
| Q15 | `group_by_dynamic` |

---

# 147. Part C — Coding (15)

Implement:

### Q1
Create a typed orders DataFrame.

### Q2
Add gross amount.

### Q3
Add tax.

### Q4
Filter paid orders.

### Q5
Create an Enum status.

### Q6
Use `cs.numeric()`.

### Q7
Aggregate by customer.

### Q8
Attach group total with `.over()`.

### Q9
Calculate order share.

### Q10
Perform a validated `m:1` join.

### Q11
Perform a semi join.

### Q12
Perform an anti join.

### Q13
Normalize a string with `.str`.

### Q14
Calculate daily revenue.

### Q15
Replace one `map_elements()` implementation with a native expression.

---

# 148. Part C Reference Solutions

```python
import polars as pl

status_type = pl.Enum([
    "PAID",
    "PENDING",
    "CANCELLED",
])
```

Derived column:

```python
df = df.with_columns(
    (pl.col("amount") * 1.18)
    .alias("gross_amount")
)
```

Tax:

```python
df = df.with_columns(
    (pl.col("amount") * 0.18)
    .alias("tax")
)
```

Filter:

```python
paid = df.filter(
    pl.col("status") == "PAID"
)
```

Selector:

```python
numeric = df.select(
    cs.numeric()
)
```

Aggregation:

```python
customer_totals = df.group_by(
    "customer_id"
).agg(
    pl.col("amount")
      .sum()
      .alias("customer_total")
)
```

Window:

```python
df = df.with_columns(
    pl.col("amount")
      .sum()
      .over("customer_id")
      .alias("customer_total")
)
```

Share:

```python
df = df.with_columns(
    (
        pl.col("amount")
        / pl.col("customer_total")
    ).alias("order_share")
)
```

Validated join:

```python
result = orders.join(
    customers,
    on="customer_id",
    how="left",
    validate="m:1",
)
```

Semi join:

```python
orders.join(
    customers,
    on="customer_id",
    how="semi",
)
```

Anti join:

```python
orders.join(
    customers,
    on="customer_id",
    how="anti",
)
```

String normalization:

```python
df.with_columns(
    pl.col("email")
      .str.to_lowercase()
      .alias("email")
)
```

Daily revenue:

```python
(
    df.sort("timestamp")
      .group_by_dynamic(
          "timestamp",
          every="1d",
      )
      .agg(
          pl.col("amount")
            .sum()
            .alias("daily_revenue")
      )
)
```

Native UDF replacement:

```python
df.with_columns(
    (pl.col("amount") * 1.18)
    .alias("gross_amount")
)
```

---

# 149. Part D — Debugging (10)

### Q1
A filter uses `and`. Fix it.

### Q2
A numeric column unexpectedly becomes string.

### Q3
Null and NaN counts differ.

### Q4
A derived-column operation removes original columns.

### Q5
A join doubles revenue.

### Q6
`join_asof()` selects an incorrect rate.

### Q7
A transformation is slow because of `map_elements()`.

### Q8
An aggregation returns too few rows.

### Q9
An `.over()` result uses the wrong partition.

### Q10
A datetime join fails because of incompatible time semantics.

---

# 150. Part D Answer Key

### Q1
Use `&` / `|` with parentheses.

### Q2
Inspect schema, inference, source drift, and casts.

### Q3
They are different states; test them separately.

### Q4
Use `with_columns()` if original columns should remain.

### Q5
Inspect duplicate join keys and validate cardinality.

### Q6
Inspect sorting, strategy, timestamps, timezone, and grouping.

### Q7
Replace it with native expressions where possible.

### Q8
Check whether you needed `.over()` instead of grouped reduction.

### Q9
Verify the `.over()` partition key(s).

### Q10
Check Date vs Datetime, time unit, timezone, and ordering.

---

# 151. Part E — Production/Data Engineering (10)

### Q1
Transactions join to customers and output rows increase by 25%. Design the investigation.

### Q2
A CSV source changes ID type intermittently. Design ingestion.

### Q3
A team uses UDFs for every transformation. Review the design.

### Q4
A 700-column schema changes monthly. How do selectors help and hurt?

### Q5
Business asks for customer total on every order. Choose between aggregate + join and `.over()`.

### Q6
FX rates change throughout the day. Design the temporal matching rule.

### Q7
A status field has five fixed allowed values. Discuss Enum vs Categorical.

### Q8
Daily revenue is required in a business timezone. What must be defined?

### Q9
An eager pipeline runs out of memory at production scale. What should you study next?

### Q10
A reviewer says all expressions must be put into exactly one `with_columns()` call for performance. Evaluate the claim.

---

# 152. Part E Answer Key

### Q1

Investigate:

```text
input grain
join key uniqueness
duplicates
expected cardinality
null keys
versioning
actual output count
```

Then add reconciliation and validation.

### Q2

Define an explicit schema policy, use controlled reader schema options, and define how invalid records are rejected/quarantined.

### Q3

Replace UDFs where native expressions exist. Isolate and benchmark unavoidable custom Python.

### Q4

Selectors reduce repetitive code but may include future columns unexpectedly.

### Q5

Use `.over()` when the result must retain each order row with the customer metric.

### Q6

Define event timestamp, effective timestamp, ordering, strategy, timezone, grouping key, and missing-rate behaviour.

### Q7

Enum fits a fixed declared domain. Categorical can be more flexible. Choose based on domain semantics and downstream requirements.

### Q8

Define timezone, window boundaries, business-day semantics, timestamp type, and missing-period behaviour.

### Q9

Study Topic 03 lazy execution and Topic 04 streaming, then reassess dataset size and execution architecture.

### Q10

Grouping independent expressions can provide useful execution opportunities, but one giant call is not a universal speed rule. Readability and dependencies matter; measure when performance is important.

---

# 153. Final Mastery Checklist

Do not move to Topic 03 until you can truthfully check all of these.

- [ ] I understand the Polars DataFrame mental model.
- [ ] I understand why there is no pandas-style index.
- [ ] I understand immutable DataFrames.
- [ ] I understand explicit dtypes.
- [ ] I understand multi-threaded execution conceptually.
- [ ] I can create a DataFrame.
- [ ] I can inspect `schema`, `dtypes`, `height`, and `width`.
- [ ] I understand expressions.
- [ ] I can draw a simple expression tree.
- [ ] I can use `pl.col()`.
- [ ] I can use `pl.lit()`.
- [ ] I can write arithmetic expressions.
- [ ] I can write comparison expressions.
- [ ] I can combine conditions using `&` and `|`.
- [ ] I can use `alias()`.
- [ ] I can use `cast()`.
- [ ] I understand `select()`.
- [ ] I understand `with_columns()`.
- [ ] I understand `filter()`.
- [ ] I understand `group_by().agg()`.
- [ ] I can choose the correct context.
- [ ] I can read CSV.
- [ ] I can read Parquet.
- [ ] I can read NDJSON.
- [ ] I can write Parquet.
- [ ] I understand `schema=`.
- [ ] I understand `schema_overrides=`.
- [ ] I can write conditional expressions.
- [ ] I can use `.str`.
- [ ] I can use `.dt`.
- [ ] I can use `.list`.
- [ ] I can use `.struct`.
- [ ] I understand `.cat`.
- [ ] I understand `.name`.
- [ ] I can use `cs.numeric()`.
- [ ] I can use `cs.starts_with(...)`.
- [ ] I understand multi-column expressions.
- [ ] I can distinguish null and NaN.
- [ ] I understand signed integers.
- [ ] I understand unsigned integers.
- [ ] I understand Float32 and Float64.
- [ ] I understand Decimal.
- [ ] I understand String.
- [ ] I understand Categorical.
- [ ] I understand Enum.
- [ ] I understand Date.
- [ ] I understand Datetime.
- [ ] I understand Duration.
- [ ] I understand List.
- [ ] I understand Struct.
- [ ] I can perform inner joins.
- [ ] I can perform left joins.
- [ ] I can perform full joins.
- [ ] I can perform semi joins.
- [ ] I can perform anti joins.
- [ ] I understand cross joins.
- [ ] I understand cardinality.
- [ ] I can use `validate="1:1"`.
- [ ] I can use `validate="1:m"`.
- [ ] I can use `validate="m:1"`.
- [ ] I understand join explosion.
- [ ] I can use `join_asof()`.
- [ ] I understand `.over()`.
- [ ] I understand `.over()` vs `group_by().agg()`.
- [ ] I understand `.over()` vs pandas `transform()`.
- [ ] I understand `.over()` vs SQL windows.
- [ ] I understand `pivot`.
- [ ] I understand `unpivot`.
- [ ] I can use `explode`.
- [ ] I understand `implode`.
- [ ] I understand `group_by_dynamic()`.
- [ ] I understand rolling operations.
- [ ] I understand expression parallelism.
- [ ] I know when grouping expressions is useful.
- [ ] I understand why `map_elements()` can be slow.
- [ ] I can replace simple UDFs with native expressions.
- [ ] I completed 15 pandas-to-Polars translations.
- [ ] I completed at least 3 `.over()` translations.
- [ ] I completed `polars_orders.py`.
- [ ] I compared results against pandas.
- [ ] I benchmarked fairly.
- [ ] I completed debugging scenarios.
- [ ] I completed practice problems.
- [ ] I completed the final mastery assessment.
- [ ] I can explain the topic aloud without notes.

---

# 154. Final Oral Mastery Challenge

Explain these without looking at notes.

## Challenge 1

```python
pl.col("amount") * 1.18
```

## Challenge 2

```python
df.select(...)
```

## Challenge 3

```python
df.with_columns(...)
```

## Challenge 4

```python
df.filter(...)
```

## Challenge 5

```python
df.group_by(...).agg(...)
```

## Challenge 6

```python
pl.col("amount").sum().over("customer_id")
```

## Challenge 7

```python
validate="m:1"
```

## Challenge 8

```python
join_asof(...)
```

## Challenge 9

```python
cs.numeric()
```

## Challenge 10

```python
map_elements(...)
```

For every item explain:

```text
What?
Why?
How?
Output shape?
Use case?
Production risk?
```

---

# 155. Final Mental Model

At the end of this topic you should be able to visualize Polars as:

```text
                       POLARS
                          │
             ┌────────────┴────────────┐
             │                         │
         DataFrame                Expression
             │                         │
       concrete data            computation recipe
             │                         │
             └────────────┬────────────┘
                          │
                       Context
                          │
       ┌──────────┬───────┼────────┬──────────┐
       ▼          ▼       ▼        ▼          ▼
    select   with_columns filter group_by     over
                                      │
                                      ▼
                                     agg
```

The central mental model:

```text
Expression
=
WHAT should happen?

Context
=
WHERE / HOW should it happen?
```

---

# 156. Senior Data Engineer Mental Model

Before writing Polars code, think in this order:

```text
Business question
       ↓
Input grain
       ↓
Schema
       ↓
Desired output grain
       ↓
Context
       ↓
Native expressions
       ↓
Join cardinality
       ↓
Temporal semantics
       ↓
Tests
       ↓
Benchmark
```

This prevents a common failure mode:

```text
write code first
→ discover semantics later
```

---

# 157. Transition to Topic 03

The next topic is:

**03 — Polars Lazy API and Query Optimization**

The progression becomes:

```text
Topic 02
Expressions + contexts
        ↓
Topic 03
LazyFrame + query plan
        ↓
pushdown
        ↓
optimization
        ↓
profiling
```

The conceptual bridge is:

> Topic 02 teaches you how to describe transformations. Topic 03 teaches you how to let Polars see and optimize the complete transformation plan before execution.

---

# 158. Current API Discipline

Polars changes frequently.

Always check:

```python
import polars as pl

print(pl.__version__)
```

Then verify the current installed API for:

- readers and schema arguments,
- `Enum`,
- selectors,
- namespaces,
- joins,
- `join_asof`,
- `pivot`,
- `unpivot`,
- `group_by_dynamic`,
- rolling operations,
- `map_elements`.

A production Data Engineer pins dependencies and verifies upgrade impacts instead of assuming examples from an older release remain unchanged.

---

# 159. Final Summary

The most important ideas are:

1. **Think in expressions, not row loops.**
2. **An expression describes a computation.**
3. **A context defines how that expression is applied.**
4. **Use `select` for output projection.**
5. **Use `with_columns` to add/replace columns.**
6. **Use `filter` to control row survival.**
7. **Use `group_by().agg()` for reduced grouped output.**
8. **Use `.over()` for group-wise values while retaining rows.**
9. **Treat schema and dtypes as production contracts.**
10. **Treat null and NaN as different states.**
11. **Validate join cardinality.**
12. **Treat unexpected row multiplication as a correctness problem.**
13. **Use `join_asof()` only for real temporal matching rules.**
14. **Use native namespaces before Python UDFs.**
15. **Use selectors deliberately and understand their dynamic scope.**
16. **Benchmark real workloads instead of repeating generic performance claims.**
17. **Know the output grain of every transformation.**

---

# 160. Topic 02 Exit Criteria

Move to Topic 03 only when you can demonstrate:

```text
[ ] Polars mental model
[ ] no-index semantics
[ ] immutable DataFrames
[ ] explicit dtypes
[ ] expressions
[ ] expression trees
[ ] pl.col()
[ ] pl.lit()
[ ] arithmetic
[ ] comparisons
[ ] alias()
[ ] cast()
[ ] select()
[ ] with_columns()
[ ] filter()
[ ] group_by().agg()
[ ] schema controls
[ ] conditionals
[ ] all required namespaces
[ ] selectors
[ ] null vs NaN
[ ] all required dtypes
[ ] all required join types
[ ] cardinality validation
[ ] join explosion
[ ] join_asof()
[ ] .over()
[ ] pandas transform mapping
[ ] SQL window mapping
[ ] pivot
[ ] unpivot
[ ] explode
[ ] implode
[ ] group_by_dynamic()
[ ] rolling
[ ] expression parallelism
[ ] native-vs-UDF reasoning
[ ] 15 pandas translations
[ ] .over() translation lab
[ ] polars_orders.py
[ ] correctness validation
[ ] benchmark
[ ] debugging
[ ] practice problems
[ ] final assessment
[ ] oral explanation
```

---

# 161. Final Reflection

Answer these in your own words.

### Reflection 1

Why is:

```python
pl.col("amount") * 1.18
```

an expression instead of a final result?

### Reflection 2

Why are:

```python
select()
```

and:

```python
with_columns()
```

different even when they contain the same expression?

### Reflection 3

Why is:

```python
group_by().agg()
```

not interchangeable with:

```python
.over()
```

### Reflection 4

Why can:

```python
validate="m:1"
```

protect both correctness and performance?

### Reflection 5

Why is:

```python
pl.col("name").str.to_lowercase()
```

preferable to a Python callback when both represent the same business rule?

A strong answer connects:

```text
native expression
→ engine-level execution
→ lower Python overhead
→ greater optimization opportunity
```

---

# 162. Final Takeaway

The objective of Topic 02 is a change in engineering thinking:

```text
Procedural mental model

row
 ↓
Python logic
 ↓
row
 ↓
Python logic
 ↓
repeat
```

becomes:

```text
Expression-oriented mental model

business intent
      ↓
expression
      ↓
context
      ↓
typed native execution
      ↓
validated result
```

That mental shift is the foundation for the next topics:

```text
Expressions
    ↓
Lazy execution
    ↓
Query optimization
    ↓
Streaming
    ↓
DuckDB interoperability
    ↓
Production Data Engineering
```

