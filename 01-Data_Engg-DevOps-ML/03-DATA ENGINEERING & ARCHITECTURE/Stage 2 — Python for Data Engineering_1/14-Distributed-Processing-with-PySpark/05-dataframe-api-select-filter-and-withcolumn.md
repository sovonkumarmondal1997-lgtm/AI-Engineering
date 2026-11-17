# Topic 05 — DataFrame API: `select()`, `filter()` and `withColumn()`

## Learning Objectives

By the end of this chapter, you should be able to:

1. Explain what a PySpark DataFrame is.
2. Explain what a Spark `Column` represents.
3. Understand column expressions.
4. Access columns safely.
5. Select columns with `select()`.
6. Rename selected columns using aliases.
7. Select literal values and expressions.
8. Filter rows using `filter()`.
9. Use `where()` correctly.
10. Combine filter conditions.
11. Understand boolean expression rules in PySpark.
12. Create derived columns with `withColumn()`.
13. Replace existing columns with `withColumn()`.
14. Use arithmetic column expressions.
15. Use conditional expressions.
16. Handle nulls in transformation expressions.
17. Chain multiple DataFrame transformations.
18. Understand lazy evaluation in DataFrame transformations.
19. Avoid common PySpark API mistakes.
20. Write readable production-oriented DataFrame transformations.

---

## 1. The Fundamental Question: How Do We Transform Structured Distributed Data?

The central question for this topic is:

> **How do we transform structured distributed data in PySpark?**

Start with a small DataFrame:

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("DataFrameApiFundamentals")
    .master("local[*]")
    .getOrCreate()
)

data = [
    ("Alice", 30, "Delhi"),
    ("Bob", 25, "Pune"),
    ("Charlie", 40, "Mumbai"),
]

df = spark.createDataFrame(
    data,
    ["name", "age", "city"],
)

df.show()
```

Expected output:

```text
+-------+---+------+
|name   |age|city  |
+-------+---+------+
|Alice  |30 |Delhi |
|Bob    |25 |Pune  |
|Charlie|40 |Mumbai|
+-------+---+------+
```

The DataFrame API lets us describe **which rows and columns we want** without manually iterating through every record.

The fundamental vocabulary is:

```text
DataFrame
    ↓
Column references
    ↓
Column expressions
    ↓
select()
filter()
withColumn()
    ↓
Transformation chain
    ↓
Lazy execution
    ↓
Action
    ↓
Distributed processing
```

---

# 2. Where This Topic Fits in the Roadmap

The dependency chain is:

```text
01 Distributed Computing
        ↓
02 SparkSession, Configuration and Deploy Modes
        ↓
03 RDDs vs DataFrames
        ↓
04 Transformations, Actions and Lazy Evaluation
        ↓
05 DataFrame API: Select, Filter and WithColumn
        ↓
06 Spark SQL and Temporary Views
        ↓
07 Joins, Shuffle and Broadcast Joins
        ↓
...
```

You already need to understand:

### From Topic 01

- driver
- executors
- partitions
- tasks
- jobs
- stages
- cluster managers
- distributed execution

### From Topic 02

- `SparkSession`
- Spark configuration
- local mode
- cluster mode
- `spark-submit`

### From Topic 03

- RDDs
- DataFrames
- schema
- distributed structured data
- RDD versus DataFrame

### From Topic 04

- transformations
- actions
- lazy evaluation
- lineage
- narrow and wide dependencies
- jobs, stages, and tasks

This chapter does **not** repeat those topics. Instead, it uses them to explain how ordinary DataFrame transformations become part of Spark's deferred computation.

---

# 3. DataFrame as Structured Distributed Data

## 3.1 Simple Definition

A PySpark DataFrame is a distributed, structured collection of data organized into rows and named columns with a schema.

A useful mental model is:

```text
DataFrame
├── rows
├── columns
├── schema
├── expressions
└── distributed partitions
```

It may look like a table, but it is not merely a local Python table.

## 3.2 Why the DataFrame Abstraction Exists

A Python object such as:

```python
rows = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
]
```

is a local Python data structure.

A Spark DataFrame, by contrast, describes structured data that Spark can process across distributed partitions.

This lets you express operations such as:

```python
df.filter(...)
df.select(...)
df.withColumn(...)
```

without manually writing a Python loop over every distributed record.

The DataFrame abstraction gives Spark structured information about the intended computation.

---

# 4. What Is a `Column`?

This is one of the most important concepts in PySpark.

A Spark `Column` is **not** a Python value containing all the values from that column.

For example:

```python
df["age"]
```

returns a Spark `Column` object.

Likewise:

```python
df.age
```

returns a Spark `Column` representing the `age` field.

That is fundamentally different from:

```python
30
```

which is an ordinary Python integer.

A useful mental model is:

```text
Python code
    ↓
Spark Column reference / expression
    ↓
DataFrame transformation
    ↓
Distributed execution later
```

For example:

```python
from pyspark.sql import functions as F

age_column = F.col("age")
```

`age_column` does not mean:

> "Load every age into this Python variable."

It means, conceptually:

> "Use the DataFrame column named `age` in a Spark expression."

---

# 5. Column Access Methods

There are three common forms.

## 5.1 Bracket notation

```python
df["name"]
```

This is explicit and useful when building expressions.

Example:

```python
df.select(df["name"], df["age"])
```

## 5.2 Attribute notation

```python
df.name
```

This is concise:

```python
df.select(df.name, df.age)
```

It can be readable, but attribute-style access is less explicit and can be awkward when column names collide with DataFrame attributes or contain characters that are inconvenient in Python attribute syntax.

## 5.3 `F.col()`

The explicit functional form is:

```python
from pyspark.sql import functions as F

F.col("name")
```

Example:

```python
df.select(
    F.col("name"),
    F.col("age"),
)
```

### Comparison

| Form | Meaning | Typical use |
|---|---|---|
| `df["name"]` | Column reference | Explicit column access |
| `df.name` | Column reference | Concise/simple access |
| `F.col("name")` | Column reference/expression | Explicit transformation code |

For production transformation code, `F.col()` is often useful because it makes the expression boundary obvious:

```python
F.col("price") * F.col("quantity")
```

---

# 6. Column Expressions

A Column becomes especially useful when combined with operators or Spark functions.

For example:

```python
F.col("age") + 1
```

describes:

```text
age + 1
```

Another expression:

```python
F.col("age") > 30
```

describes a predicate.

Another:

```python
F.upper(F.col("name"))
```

describes a string transformation.

The mental model is:

```text
Column
   +
Operator / Function
   ↓
Column Expression
```

Examples:

```text
age + 1
age > 30
upper(name)
```

These are not ordinary Python scalar operations over the entire distributed dataset. They are Spark expressions that can be incorporated into a DataFrame transformation.

---

# 7. `select()` — Fundamentals

## 7.1 What `select()` Does

`select()` constructs a new DataFrame containing the requested columns or expressions.

```python
df.select("name", "age")
```

The result has only:

```text
name
age
```

The original `df` is not mutated.

## 7.2 Why `select()` Exists

A production pipeline often needs a deliberate output schema.

For example:

```python
selected_df = df.select(
    "name",
    "city",
)
```

The resulting DataFrame expresses:

> "For this transformation step, these are the output columns I want."

## 7.3 Lazy Behavior

`select()` is a transformation.

Therefore:

```python
selected_df = df.select("name", "age")
```

does not by itself mean:

> "Immediately scan all data and materialize the result."

It builds another step in Spark's computation.

An action such as:

```python
selected_df.show()
```

requires Spark to execute enough of the plan to produce the result.

---

# 8. `select()` with Column References

These forms express the same basic selection:

```python
df.select("name", "age")
```

```python
df.select(
    df["name"],
    df["age"],
)
```

```python
df.select(
    F.col("name"),
    F.col("age"),
)
```

The last form is especially useful when selections become expressions.

Example:

```python
df.select(
    F.col("name"),
    F.col("age") + 1,
)
```

Now the second output is an expression rather than a direct column reference.

---

# 9. `select()` with Expressions

A major strength of `select()` is that it can select and derive columns at the same time.

```python
df.select(
    F.col("name"),
    (F.col("age") + 1).alias("next_age"),
)
```

Conceptually:

```text
existing column
      ↓
   expression
      ↓
new output column
```

The resulting schema is conceptually:

```text
name      string
next_age  integer/long-like numeric type
```

depending on the input schema.

This is a projection: the output contains the columns and expressions specified by the `select()` call.

---

# 10. `alias()`

## 10.1 What `alias()` Does

`alias()` gives a name to a column or expression in the output.

```python
df.select(
    F.col("name").alias("customer_name"),
)
```

The output column is named:

```text
customer_name
```

For a derived expression:

```python
df.select(
    (F.col("age") + 1).alias("next_age"),
)
```

The alias provides a clear output name.

## 10.2 Why Aliases Matter

Aliases help with:

- schema clarity
- readable transformation logic
- naming derived metrics
- downstream contracts
- avoiding unintuitive expression-generated names

## 10.3 Important Distinction

This:

```python
F.col("name").alias("customer_name")
```

does **not** mutate the original DataFrame.

It describes how the expression should be named in the output of the transformation using it.

---

# 11. Selecting All Columns

You can write:

```python
df.select("*")
```

This selects all columns.

It is useful when you explicitly need the complete current schema.

However, production pipelines often benefit from deliberate projections:

```python
df.select(
    "customer_id",
    "price",
    "quantity",
)
```

Carrying unnecessary fields through a pipeline can make schemas harder to understand and can cause more data to be carried through later operations.

This chapter only introduces the principle; detailed optimizer behavior belongs to later topics.

---

# 12. Selecting a Mix of Columns and Expressions

A realistic example:

```python
df.select(
    "name",
    "city",
    (F.col("age") + 1).alias("next_age"),
    F.upper(F.col("name")).alias("name_upper"),
)
```

Each item has a role:

```text
"name"
    → existing column

"city"
    → existing column

age + 1
    → derived expression

upper(name)
    → derived expression
```

This is a core DataFrame pattern.

---

# 13. `selectExpr()`

PySpark also provides:

```python
df.selectExpr(
    "name",
    "age + 1 AS next_age",
)
```

`selectExpr()` accepts SQL-style expression strings.

It is a convenient bridge between DataFrame code and SQL expression syntax.

For example:

```python
df.selectExpr(
    "name",
    "age + 1 AS next_age",
)
```

and:

```python
df.select(
    F.col("name"),
    (F.col("age") + 1).alias("next_age"),
)
```

can express the same conceptual projection.

### Trade-off

Expression strings can be concise:

```python
"age + 1 AS next_age"
```

while function-based expressions make the Spark expression structure explicit in Python:

```python
(F.col("age") + 1).alias("next_age")
```

Neither syntax is universally superior. Team conventions, readability, expression complexity, and the surrounding codebase matter.

This chapter only introduces `selectExpr()` as a DataFrame API convenience. Full Spark SQL is covered in Topic 06.

---

# 14. `filter()` — Fundamentals

## 14.1 What Is Filtering?

`filter()` selects rows that satisfy a condition.

```python
df.filter(
    F.col("age") > 30
)
```

The condition is called a **predicate**.

A predicate is a condition that determines whether a row satisfies a requirement.

Mental model:

```text
Every row
   ↓
Predicate
   ↓
TRUE  → keep
FALSE → remove
```

For:

```python
F.col("age") > 30
```

the predicate asks:

> Is this row's `age` greater than 30?

## 14.2 Lazy Behavior

`filter()` is a transformation.

Therefore:

```python
filtered_df = df.filter(F.col("age") > 30)
```

creates a new logical transformation step.

An action such as:

```python
filtered_df.show()
```

causes Spark to execute the required computation.

---

# 15. `where()`

`where()` provides equivalent filtering semantics:

```python
df.where(
    F.col("age") > 30
)
```

and:

```python
df.filter(
    F.col("age") > 30
)
```

are equivalent for ordinary DataFrame row filtering.

The choice is commonly a readability or team-convention decision.

A team may prefer `filter()` because it clearly communicates row filtering. Another may use `where()` because it aligns with SQL terminology.

Do not invent a semantic difference between them where none exists.

---

# 16. String Filter Conditions

You can express a predicate as a SQL-style expression string:

```python
df.filter("age > 30")
```

or with a Column expression:

```python
df.filter(
    F.col("age") > 30
)
```

The string form is concise and familiar to SQL users.

The Column form is explicit Python expression construction.

For maintainability, choose a consistent style that your team can understand. Explicit Column expressions are often particularly clear when conditions become complex:

```python
df.filter(
    (F.col("age") > 30)
    & F.col("city").isin("Delhi", "Mumbai")
)
```

String expressions remain useful when SQL expression syntax makes the intent straightforward.

---

# 17. Multiple Filter Conditions

PySpark Column expressions use:

```text
&  → logical AND
|  → logical OR
~  → logical NOT
```

Example:

```python
df.filter(
    (F.col("age") > 30)
    & (F.col("city") == "Delhi")
)
```

This means:

```text
age > 30
AND
city = Delhi
```

OR:

```python
df.filter(
    (F.col("age") > 30)
    | (F.col("city") == "Delhi")
)
```

means:

```text
age > 30
OR
city = Delhi
```

NOT:

```python
df.filter(
    ~(F.col("age") > 30)
)
```

means the logical negation of the predicate.

---

# 18. The Critical Python Boolean Operator Trap

A common beginner mistake is:

```python
df.filter(
    F.col("age") > 30 and
    F.col("city") == "Delhi"
)
```

Do not write Spark Column predicates this way.

Python's:

```text
and
or
not
```

are Python boolean operators. Spark Column expressions use overloaded operators designed to build Spark expressions:

```text
&
|
~
```

Write:

```python
df.filter(
    (F.col("age") > 30)
    & (F.col("city") == "Delhi")
)
```

### Why Parentheses Matter

Write:

```python
(F.col("age") > 30) & (F.col("city") == "Delhi")
```

rather than relying on Python operator precedence.

The parentheses make the intended expression tree explicit and prevent confusing parsing behavior.

This is one of the most important PySpark API rules to memorize through understanding rather than rote memorization:

```text
Spark Column logical combination:
AND → &
OR  → |
NOT → ~
```

---

# 19. Comparison Operators

Column comparisons create Spark expressions.

Common operators are:

```text
==
!=
>
<
>=
<=
```

Examples:

```python
F.col("age") >= 18
```

```python
F.col("status") != "inactive"
```

```python
F.col("amount") > 1000
```

These do not produce ordinary Python booleans representing the entire distributed dataset. They construct expressions that Spark can evaluate against DataFrame rows.

---

# 20. Membership Conditions with `isin()`

When a field may match one of several values, `isin()` is useful:

```python
df.filter(
    F.col("city").isin(
        "Delhi",
        "Mumbai",
        "Pune",
    )
)
```

You can combine it with other predicates:

```python
df.filter(
    (F.col("status") == "active")
    & F.col("city").isin("Delhi", "Mumbai")
)
```

This is generally clearer than writing a long chain of equality comparisons.

---

# 21. Null Filtering

Nulls require special handling.

Use:

```python
F.col("age").isNull()
```

or:

```python
F.col("age").isNotNull()
```

For example:

```python
df.filter(
    F.col("age").isNotNull()
)
```

Do not use:

```python
F.col("age") == None
```

as your null-checking pattern.

Conceptually, SQL-style logic includes three outcomes:

```text
TRUE
FALSE
UNKNOWN
```

A null does not behave like an ordinary Python value. Spark SQL's null semantics therefore require explicit null-aware expressions.

For this reason, learn these as standard DataFrame tools:

```python
F.col("age").isNull()
F.col("age").isNotNull()
```

---

# 22. String Predicates

A practical subset of string predicates includes:

```python
F.col("name").startswith("A")
```

```python
F.col("name").contains("li")
```

```python
F.col("name").like("A%")
```

These are Spark expressions, not ordinary Python string method calls over the entire distributed column.

For example:

```python
df.filter(
    F.col("name").startswith("A")
)
```

describes a distributed DataFrame filter condition.

---

# 23. `withColumn()` — Fundamentals

`withColumn()` is used to create or replace a DataFrame column using a Spark expression.

Example:

```python
df2 = df.withColumn(
    "age_plus_one",
    F.col("age") + 1,
)
```

Conceptually:

```text
Original DataFrame
       ↓
   withColumn()
       ↓
New DataFrame
```

The new DataFrame has an additional output column:

```text
name
age
city
age_plus_one
```

Like `select()` and `filter()`, `withColumn()` is a transformation and therefore participates in lazy execution.

---

# 24. `withColumn()` and Immutability

DataFrames are immutable logical objects.

This:

```python
df2 = df.withColumn(
    "age_plus_one",
    F.col("age") + 1,
)
```

does not mutate `df` in place.

Think:

```text
df  → original logical DataFrame
df2 → derived logical DataFrame
```

This matters because the transformation must be captured by assigning the returned DataFrame:

```python
df = df.withColumn(...)
```

or:

```python
df2 = df.withColumn(...)
```

If you merely call:

```python
df.withColumn(
    "age_plus_one",
    F.col("age") + 1,
)
```

and discard the returned DataFrame, you have not changed `df`.

---

# 25. Replacing an Existing Column

`withColumn()` can also replace an existing column.

```python
df2 = df.withColumn(
    "age",
    F.col("age") + 1,
)
```

The output column is still named `age`, but its expression has changed.

Conceptually:

```text
existing age
    ↓
new expression: age + 1
    ↓
output age
```

This is powerful but potentially dangerous.

Replacing an existing column can silently alter the meaning of a field if the transformation is not carefully reviewed.

Production questions should include:

- Is this replacement intentional?
- Is the data type still correct?
- Is the business meaning unchanged?
- Should the original value be preserved under another name?

---

# 26. Multiple `withColumn()` Calls

Chaining is common:

```python
df2 = (
    df
    .withColumn(
        "age_plus_one",
        F.col("age") + 1,
    )
    .withColumn(
        "age_group",
        F.when(F.col("age") < 18, "minor")
         .otherwise("adult"),
    )
)
```

This reads naturally as:

```text
input
  ↓
derive age_plus_one
  ↓
derive age_group
  ↓
output DataFrame
```

However, a large number of independent column derivations can become difficult to read if spread across a long sequence of transformations. In such cases, a deliberate projection with `select()` can sometimes communicate the intended output schema more clearly.

Do not assume a universal performance rule from the API shape alone; actual planning behavior depends on Spark version and expression structure.

---

# 27. `select()` vs `withColumn()`

| Requirement | `select()` | `withColumn()` |
|---|---|---|
| Choose output columns | Yes | Keeps existing columns |
| Add derived column | Yes | Yes |
| Rename output expression | Yes | Yes |
| Replace existing column | Through selected expression/output | Directly supported |
| Explicit final schema | Strong fit | Preserves existing schema plus change |
| Projection-style transformation | Natural | Less direct |

The key distinction is **intent**.

Use `select()` when the main intent is:

> "This is the set of columns and expressions that should form the output."

Use `withColumn()` when the main intent is:

> "Keep the DataFrame shape and add or replace this particular column."

They overlap in capability, but they communicate different transformation intent.

---

# 28. Column Arithmetic

Spark Column expressions support arithmetic.

For example:

```python
F.col("price") * F.col("quantity")
```

can derive transaction revenue:

```python
df2 = df.withColumn(
    "total_amount",
    F.col("price") * F.col("quantity"),
)
```

Another example:

```python
df2 = df.withColumn(
    "amount_with_tax",
    F.col("amount") * 1.18,
)
```

When using arithmetic, consider:

- source data types
- result data type
- null propagation
- business meaning
- numeric precision requirements

For financial workloads, choose numeric types and transformations deliberately rather than treating every number as an arbitrary floating-point value.

---

# 29. Conditional Expressions with `when()` and `otherwise()`

Conditional business logic can be represented as a Spark expression.

Example:

```python
age_group = (
    F.when(
        F.col("age") >= 18,
        "adult",
    )
    .otherwise("minor")
)

df2 = df.withColumn(
    "age_group",
    age_group,
)
```

Mental model:

```text
condition
   ↓
TRUE  → first result
FALSE → otherwise result
```

`when()` builds a conditional expression. `otherwise()` supplies the fallback branch.

---

# 30. Multiple Conditions

You can chain conditions:

```python
df2 = df.withColumn(
    "age_group",
    F.when(
        F.col("age") < 18,
        "minor",
    )
    .when(
        F.col("age") < 65,
        "adult",
    )
    .otherwise("senior"),
)
```

The conditions are evaluated in sequence.

Therefore, overlapping conditions require careful ordering.

For example:

```text
age < 18
age < 65
otherwise
```

means:

```text
0–17  → minor
18–64 → adult
65+   → senior
```

assuming the data and business rules make those boundaries meaningful.

Always ask:

> What happens if more than one condition could be true?

The first matching branch controls the result.

---

# 31. Null Handling in `withColumn()`

A useful function for defaulting null values is `coalesce()`.

```python
df2 = df.withColumn(
    "age_clean",
    F.coalesce(
        F.col("age"),
        F.lit(0),
    ),
)
```

Conceptually:

```text
age is present → use age
age is null    → use 0
```

Another approach is explicit conditional logic:

```python
df2 = df.withColumn(
    "age_clean",
    F.when(
        F.col("age").isNull(),
        F.lit(0),
    ).otherwise(
        F.col("age"),
    ),
)
```

These examples show the mechanics. The correct default is a **business-rule decision**, not merely a technical choice.

For example, replacing an unknown age with `0` may make a pipeline technically executable but semantically misleading.

---

# 32. `lit()` — Literal Values

`F.lit()` represents a literal value inside a Spark expression.

Examples:

```python
F.lit(1)
```

```python
F.lit("unknown")
```

A practical example:

```python
df2 = df.withColumn(
    "source",
    F.lit("customer_system"),
)
```

This creates the same literal value for each output row.

### `F.col()` vs `F.lit()`

These are fundamentally different:

```python
F.col("source")
```

means:

> Reference the DataFrame column named `source`.

Whereas:

```python
F.lit("source")
```

means:

> Use the literal string `"source"`.

Mental model:

```text
F.col("name")
    ↓
column reference

F.lit("name")
    ↓
literal value: "name"
```

This distinction is critical.

---

# 33. Practical Spark Functions for This Topic

This chapter uses a focused subset rather than attempting to catalog Spark's entire function library.

| Function | Typical purpose |
|---|---|
| `col()` | Column reference |
| `lit()` | Literal value |
| `upper()` | Uppercase text |
| `lower()` | Lowercase text |
| `trim()` | Remove surrounding whitespace |
| `length()` | String length |
| `concat()` | Concatenate expressions |
| `concat_ws()` | Concatenate with separator |
| `coalesce()` | Choose first non-null expression |
| `when()` | Conditional expression |
| `regexp_replace()` | Regex-based string replacement |

Example:

```python
from pyspark.sql import functions as F

cleaned = df.withColumn(
    "name_clean",
    F.trim(F.col("name")),
)
```

---

# 34. String Transformations

## Trim

```python
df2 = df.withColumn(
    "name_clean",
    F.trim(F.col("name")),
)
```

This removes surrounding whitespace.

## Uppercase

```python
df2 = df.withColumn(
    "name_upper",
    F.upper(F.col("name")),
)
```

## Lowercase

```python
df2 = df.withColumn(
    "name_lower",
    F.lower(F.col("name")),
)
```

## Concatenation

```python
df2 = df.withColumn(
    "full_name",
    F.concat_ws(
        " ",
        F.col("first_name"),
        F.col("last_name"),
    ),
)
```

The important pattern is:

```text
existing columns
      ↓
Spark function/expression
      ↓
derived column
```

---

# 35. Type Casting

Sometimes a source field arrives with an incorrect or overly general type.

For example:

```python
df2 = df.withColumn(
    "age_int",
    F.col("age").cast("int"),
)
```

Or:

```python
df2 = df.withColumn(
    "amount_double",
    F.col("amount").cast("double"),
)
```

Casting is useful for:

- schema correctness
- expression compatibility
- downstream contracts
- consistent analytics types

But casting can expose invalid input.

For example, if a string contains text that cannot be interpreted as the intended numeric type, the result may not be usable as expected.

Production code should therefore treat casting as part of schema and data-contract reasoning rather than blindly applying casts everywhere.

---

# 36. Basic Date and Timestamp Expressions

Date/time transformations are introduced here only as practical examples.

For example:

```python
df2 = df.withColumn(
    "event_date",
    F.to_date(F.col("event_timestamp")),
)
```

You can also derive the current date:

```python
df2 = df.withColumn(
    "processing_date",
    F.current_date(),
)
```

Keep the conceptual distinction clear:

```text
date
timestamp
```

are not interchangeable concepts.

Explicit types matter because filtering, ordering, arithmetic, and downstream analytics depend on the expression's data type.

Detailed date/time processing belongs elsewhere.

---

# 37. Transformation Chaining

A realistic DataFrame pipeline often combines the three core operations.

```python
from pyspark.sql import functions as F

result = (
    df
    .filter(
        F.col("status") == "active"
    )
    .withColumn(
        "total_amount",
        F.col("price") * F.col("quantity"),
    )
    .select(
        "customer_id",
        "total_amount",
    )
)
```

Read it from top to bottom:

```text
Input DataFrame
      ↓
filter()
      ↓
withColumn()
      ↓
select()
      ↓
Result DataFrame
```

The transformations are lazy.

No action has yet been called in the example.

To inspect the result:

```python
result.show()
```

`show()` is an action and causes Spark to execute enough of the computation to produce the displayed result.

---

# 38. `select()` as Projection

A useful relational concept is:

> **Projection = choosing or deriving the columns that should appear in the output.**

Therefore:

```python
df.select(
    "customer_id",
    "order_id",
    "amount",
)
```

is a projection.

Mental model:

```text
filter → row selection
select → column projection
```

This distinction is foundational.

---

# 39. `filter()` as a Predicate

Filtering is row selection based on a predicate.

```python
df.filter(
    F.col("age") >= 18
)
```

Mental model:

```text
Every row
   ↓
Predicate
   ↓
TRUE  → keep
FALSE → remove
UNKNOWN/null semantics → handled according to Spark SQL rules
```

This is why understanding expressions is more important than memorizing the method name.

---

# 40. `withColumn()` as Derivation

The core mental model is:

```text
Existing columns
       ↓
Spark expression
       ↓
New or replaced column
```

For example:

```python
df.withColumn(
    "revenue",
    F.col("price") * F.col("quantity"),
)
```

means:

> Define the output column `revenue` using the expression `price × quantity`.

---

# 41. Lazy Evaluation Connection

Consider:

```python
result = (
    df
    .filter(F.col("status") == "active")
    .withColumn(
        "revenue",
        F.col("price") * F.col("quantity"),
    )
    .select(
        "customer_id",
        "revenue",
    )
)
```

All three are transformations:

```text
filter      → transformation
withColumn  → transformation
select      → transformation
```

At this point, you have described a computation.

Then:

```python
result.show()
```

is an action.

Conceptually:

```text
No action yet
     ↓
Transformation chain
     ↓
Action
     ↓
Distributed execution
```

This is the direct connection to Topic 04.

---

# 42. Common ETL Transformation Pattern

A very common Data Engineering pattern is:

```text
Read
 ↓
Filter
 ↓
Derive
 ↓
Project
 ↓
Write
```

For example:

```python
result = (
    df
    .filter(
        F.col("status") == "active"
    )
    .withColumn(
        "revenue",
        F.col("price") * F.col("quantity"),
    )
    .select(
        "customer_id",
        "revenue",
    )
)
```

This is useful because each transformation has a clear responsibility:

- `filter()` controls row eligibility.
- `withColumn()` expresses a derived field.
- `select()` defines the output projection.

---

# 43. Introductory Column Pruning Awareness

Suppose the input has:

```text
customer_id
price
quantity
status
debug_flag
raw_payload
internal_note
```

but the downstream output only needs:

```text
customer_id
price
quantity
```

A deliberate projection is clearer:

```python
working_df = df.select(
    "customer_id",
    "price",
    "quantity",
)
```

Conceptually:

```text
unnecessary columns
       ↓
less useful pipeline state
```

The exact physical optimization of column pruning belongs to later optimizer material, but the engineering principle is useful now:

> Carry the data you actually need.

---

# 44. Introductory Filter-Early Awareness

A common logical pattern is:

```python
df.filter(
    F.col("status") == "active"
)
```

before downstream transformations when that is logically appropriate.

The motivation is simple:

```text
fewer relevant rows
      ↓
less downstream work to reason about
```

However, do **not** assume that manually moving every filter earlier guarantees a different or faster physical plan.

Spark can optimize structured operations. Later topics cover Catalyst and physical planning in depth.

The production rule at this stage is:

> Express correct logical transformations clearly first; understand optimization separately.

---

# 45. Schema Inspection

When debugging transformations, inspect the schema.

## `printSchema()`

```python
df.printSchema()
```

This is useful for understanding field names and types.

## `columns`

```python
df.columns
```

returns the column names.

## `dtypes`

```python
df.dtypes
```

provides name/type pairs.

Inspect before and after transformations:

```python
df.printSchema()

transformed_df = df.withColumn(
    "age_int",
    F.col("age").cast("int"),
)

transformed_df.printSchema()
```

Schema inspection helps answer:

- Did the column exist?
- Did its type change?
- Did `select()` remove a field?
- Did `withColumn()` create the expected field?
- Did an expression produce an unexpected type?

---

# 46. Output Inspection

`show()` is a practical inspection tool:

```python
df.show()
```

For long strings:

```python
df.show(truncate=False)
```

For a limited number of rows:

```python
df.show(10)
```

Remember:

> `show()` is an action.

It therefore causes Spark to execute enough work to return rows for display.

Do not confuse inspecting a small sample with a general strategy for processing a large dataset.

---

# 47. Debugging Transformation Chains

## Scenario 1 — A Derived Column Contains Unexpected Nulls

Inspect:

```text
1. schema
2. expression
3. source values
4. null behavior
```

For example:

```python
df.printSchema()

df.select(
    "age",
    F.col("age") + 1,
).show()
```

Ask:

- Is `age` actually numeric?
- Is `age` null?
- Does the expression propagate null?
- Is a default value appropriate?

## Scenario 2 — A Filter Returns Zero Rows

Use a systematic process:

```text
Inspect schema
      ↓
Inspect sample data
      ↓
Check data types
      ↓
Check predicate
      ↓
Check null behavior
      ↓
Test a simpler predicate
```

For example, if this returns no rows:

```python
df.filter(
    (F.col("age") > 30)
    & (F.col("city") == "Delhi")
)
```

test each condition separately:

```python
df.filter(F.col("age") > 30).show()
```

then:

```python
df.filter(F.col("city") == "Delhi").show()
```

Then combine them again.

## Scenario 3 — A Derived Column Has Unexpected Values

Inspect the exact expression:

```python
df.select(
    "price",
    "quantity",
    (F.col("price") * F.col("quantity")).alias("revenue"),
).show()
```

Compare source values with the expected calculation.

## Scenario 4 — A Column Disappears

Check the nearest `select()`.

Remember:

```python
df.select("customer_id", "amount")
```

creates an output containing those requested fields, not every field from the input.

## Scenario 5 — A Column Changes Type

Inspect:

```python
df.printSchema()
```

and look for operations such as:

```python
.cast(...)
```

or expressions whose result type differs from the source.

---

# 48. Data Types and Expression Compatibility

Common Spark SQL/DataFrame types include:

```text
string
integer
long
double
boolean
date
timestamp
```

Expression semantics depend on these types.

For example:

```python
F.col("price") * F.col("quantity")
```

assumes compatible numeric semantics.

Likewise:

```python
F.col("age") > 30
```

assumes that `age` can be compared meaningfully to the numeric literal.

This is why schema inspection is a core debugging skill.

---

# 49. Final `select()` for Schema Design

A final projection can make the intended output contract explicit:

```python
final_df = df.select(
    "customer_id",
    "order_id",
    "order_date",
    F.col("price").cast("double").alias("price"),
    (F.col("price") * F.col("quantity")).alias("revenue"),
)
```

This provides a clear place to reason about:

- output columns
- column order
- output names
- derived columns
- type conversions
- downstream schema expectations

For analytics pipelines, explicit final schemas are often easier to review than accidentally carrying every input column forward.

---

# 50. `withColumn()` Design Considerations

`withColumn()` is appropriate when you want to:

- add one or a small number of derived columns
- replace a particular column intentionally
- express incremental transformations clearly

For example:

```python
df2 = (
    df
    .withColumn(
        "revenue",
        F.col("price") * F.col("quantity"),
    )
    .withColumn(
        "customer_name_clean",
        F.trim(F.col("customer_name")),
    )
)
```

If there are many independent output expressions, consider whether one deliberate `select()` projection communicates the target schema more clearly.

Do not turn this into an unsupported rule such as "`withColumn()` is always slow." Actual behavior depends on Spark version, the expression structure, and the resulting logical plan.

---

# 51. Python Loops vs DataFrame Expressions

For distributed DataFrame transformations, avoid manually iterating over rows:

```python
for row in rows:
    ...
```

and instead express the transformation with Spark-native operations:

```python
df.withColumn(
    "new_value",
    F.col("value") * 2,
)
```

Why?

Because DataFrame expressions describe transformations in a form Spark can reason about as structured distributed computation.

This does **not** mean every Python loop is inherently bad. A small local loop for configuration, orchestration, or non-distributed control logic can be perfectly reasonable.

The important distinction is:

```text
Local Python control logic
        ≠
Distributed DataFrame row processing
```

---

# 52. UDF Boundary — Introduction Only

A Python function is not automatically the same thing as a Spark-native Column expression.

Conceptually, this is different:

```python
def some_python_function(value):
    return value * 2
```

from:

```python
F.col("value") * 2
```

Spark-native expressions provide structured information about the operation.

Arbitrary Python functions may require a UDF mechanism with different execution characteristics.

Detailed treatment of:

- Python UDFs
- pandas UDFs
- built-in functions

belongs to Topic 11.

For this topic, remember:

> Prefer an available Spark-native expression for ordinary DataFrame transformations rather than reaching for arbitrary Python row logic.

---

# 53. Production Mini-Project: Customer Transaction Transformation

## Scenario

You receive a transaction DataFrame with:

```text
customer_id
price
quantity
status
customer_name
```

Requirements:

1. Keep only active transactions.
2. Remove unnecessary columns.
3. Clean customer names.
4. Calculate transaction revenue.
5. Create a transaction category.
6. Cast numeric types correctly.
7. Produce a final output schema.

## Example Input

```python
from pyspark.sql import functions as F

data = [
    ("C001", " Alice ", "active", "10.50", 2),
    ("C002", "Bob", "inactive", "25.00", 1),
    ("C003", " Charlie ", "active", "100.00", 3),
]

transactions = spark.createDataFrame(
    data,
    [
        "customer_id",
        "customer_name",
        "status",
        "price",
        "quantity",
    ],
)
```

## Transformation

```python
result = (
    transactions
    .filter(
        F.col("status") == "active"
    )
    .withColumn(
        "customer_name_clean",
        F.trim(F.col("customer_name")),
    )
    .withColumn(
        "price",
        F.col("price").cast("double"),
    )
    .withColumn(
        "revenue",
        F.col("price") * F.col("quantity"),
    )
    .withColumn(
        "transaction_category",
        F.when(
            F.col("revenue") >= 200,
            "high",
        )
        .when(
            F.col("revenue") >= 50,
            "medium",
        )
        .otherwise("low"),
    )
    .select(
        "customer_id",
        "customer_name_clean",
        "price",
        "quantity",
        "revenue",
        "transaction_category",
    )
)
```

### Pipeline

```text
Input
  ↓
filter active rows
  ↓
trim customer name
  ↓
cast price
  ↓
calculate revenue
  ↓
categorize transaction
  ↓
select final schema
  ↓
output
```

### Production reasoning

The important questions are not just:

> "Does this code run?"

Also ask:

- Is `status` the correct business criterion for an active transaction?
- Is replacing `price` with a cast intentional?
- What happens if `price` is invalid?
- What happens if `quantity` is null?
- Are the revenue thresholds correct?
- Is `customer_name_clean` the desired canonical field?
- Is the final schema stable for downstream consumers?

---

# 54. Hands-On Labs

## Lab 1 — Basic `select()`

Given:

```text
name
age
city
```

select:

```text
name
age
city
```

using the DataFrame API.

Then select only:

```text
name
city
```

### Goal

Understand projection.

---

## Lab 2 — Column Expressions

Create:

```text
age_plus_one
```

using:

```python
df.select(
    "name",
    (F.col("age") + 1).alias("age_plus_one"),
)
```

### Goal

Understand that `select()` can create derived output columns.

---

## Lab 3 — Filtering

Filter:

```text
age > 30
```

using:

```python
df.filter(
    F.col("age") > 30
)
```

### Goal

Understand predicates.

---

## Lab 4 — Multiple Predicates

Filter:

```text
age > 30
AND
city = Delhi
```

using:

```python
df.filter(
    (F.col("age") > 30)
    & (F.col("city") == "Delhi")
)
```

### Goal

Understand `&` and parentheses.

---

## Lab 5 — `withColumn()`

Create:

```text
total_amount
```

from:

```text
price * quantity
```

Example:

```python
df2 = df.withColumn(
    "total_amount",
    F.col("price") * F.col("quantity"),
)
```

### Goal

Understand derived columns.

---

## Lab 6 — Conditional Column

Create:

```text
customer_segment
```

using `when()` and `otherwise()`.

For example:

```python
df2 = df.withColumn(
    "customer_segment",
    F.when(
        F.col("amount") >= 1000,
        "high_value",
    )
    .otherwise("standard"),
)
```

### Goal

Understand conditional expressions.

---

## Lab 7 — Null Handling

Create a cleaned field using `coalesce()`:

```python
df2 = df.withColumn(
    "age_clean",
    F.coalesce(
        F.col("age"),
        F.lit(0),
    ),
)
```

Then discuss whether `0` is a valid business default.

### Goal

Separate technical null handling from business semantics.

---

## Lab 8 — Type Casting

Assume:

```text
amount = "125.50"
```

Convert it to a numeric type:

```python
df2 = df.withColumn(
    "amount_numeric",
    F.col("amount").cast("double"),
)
```

### Goal

Understand schema-aware expressions.

---

## Lab 9 — Transformation Chain

Build:

```text
filter
→
withColumn
→
select
```

Example:

```python
result = (
    df
    .filter(F.col("status") == "active")
    .withColumn(
        "revenue",
        F.col("price") * F.col("quantity"),
    )
    .select(
        "customer_id",
        "revenue",
    )
)
```

### Goal

Understand composable DataFrame transformations.

---

## Lab 10 — Debugging

Intentionally introduce:

1. incorrect boolean operator
2. wrong column name
3. wrong null comparison
4. incorrect data type

For each:

- observe the error or incorrect output
- identify the expression causing it
- explain why it is wrong
- fix it
- rerun the transformation

### Goal

Develop debugging rather than memorization.

---

# 55. Predict → Run → Observe → Explain

For every lab, use this workflow:

```text
Predict
   ↓
Write expression
   ↓
Predict output schema
   ↓
Run
   ↓
Inspect result
   ↓
Inspect schema
   ↓
Explain
   ↓
Modify one thing
   ↓
Run again
```

Before executing a transformation, ask:

> What will the output columns be?

> What type will each derived column have?

> Which rows will survive?

> What happens if an input value is null?

This habit builds expression-level reasoning.

---

# 56. Production Scenarios

## Scenario 1 — Customer Filtering

Requirement:

> Keep active customers only.

Transformation:

```python
active = df.filter(
    F.col("status") == "active"
)
```

Consider:

- exact status vocabulary
- case sensitivity requirements
- null status behavior
- downstream expectations

---

## Scenario 2 — Revenue Calculation

Requirement:

```text
revenue = price × quantity
```

Transformation:

```python
df.withColumn(
    "revenue",
    F.col("price") * F.col("quantity"),
)
```

Consider:

- numeric types
- null inputs
- decimal precision
- business definition of revenue

---

## Scenario 3 — Data Cleaning

Requirement:

> Remove surrounding whitespace from customer names and replace missing values according to a defined rule.

Example:

```python
df.withColumn(
    "customer_name_clean",
    F.coalesce(
        F.trim(F.col("customer_name")),
        F.lit("unknown"),
    ),
)
```

The value `"unknown"` is a business choice, not an automatic technical truth.

---

## Scenario 4 — Final Projection

Requirement:

> Provide only the fields needed by a downstream analytics table.

```python
final_df = df.select(
    "customer_id",
    "order_id",
    "order_date",
    "revenue",
)
```

This creates an explicit output contract.

---

## Scenario 5 — Schema Standardization

Requirement:

> Ensure a numeric field has the expected type.

```python
standardized = df.withColumn(
    "amount",
    F.col("amount").cast("double"),
)
```

Consider invalid source values before relying on the cast.

---

## Scenario 6 — Business Rule

Requirement:

> Create customer categories using business thresholds.

```python
categorized = df.withColumn(
    "customer_category",
    F.when(
        F.col("revenue") >= 10000,
        "enterprise",
    )
    .when(
        F.col("revenue") >= 1000,
        "growth",
    )
    .otherwise("standard"),
)
```

For each production scenario, reason through:

```text
Input
 ↓
Expression
 ↓
Output
 ↓
Schema
 ↓
Production consideration
```

---

# 57. Foundational Performance Awareness

This topic should establish good habits without duplicating later optimization topics.

## Avoid unnecessary columns

Use:

```python
df.select(
    "customer_id",
    "price",
    "quantity",
)
```

when that is the intended working schema.

## Avoid unnecessary rows

Use:

```python
df.filter(
    F.col("status") == "active"
)
```

when that is logically correct.

## Prefer Spark-native expressions

Prefer:

```python
F.col(...)
F.upper(...)
F.when(...)
```

for ordinary DataFrame transformations rather than arbitrary Python row loops.

Do not deeply optimize:

- Python UDF performance
- Catalyst
- AQE
- partition tuning
- shuffle optimization

Those are later topics.

---

# 58. Common API Mistakes and Corrections

## Mistake 1 — Using Python `and`

Incorrect:

```python
df.filter(
    (F.col("age") > 30)
    and (F.col("city") == "Delhi")
)
```

Correct:

```python
df.filter(
    (F.col("age") > 30)
    & (F.col("city") == "Delhi")
)
```

---

## Mistake 2 — Using Python `or`

Incorrect:

```python
df.filter(
    (F.col("city") == "Delhi")
    or (F.col("city") == "Mumbai")
)
```

Correct:

```python
df.filter(
    (F.col("city") == "Delhi")
    | (F.col("city") == "Mumbai")
)
```

---

## Mistake 3 — Using Python `not`

Incorrect:

```python
df.filter(
    not (F.col("age") > 30)
)
```

Correct:

```python
df.filter(
    ~(F.col("age") > 30)
)
```

---

## Mistake 4 — Forgetting Parentheses

Prefer:

```python
(F.col("age") > 30) & (F.col("city") == "Delhi")
```

rather than relying on complicated operator precedence.

---

## Mistake 5 — Incorrect Null Comparison

Do not use:

```python
F.col("age") == None
```

Use:

```python
F.col("age").isNull()
```

or:

```python
F.col("age").isNotNull()
```

---

## Mistake 6 — Confusing `col()` and `lit()`

```python
F.col("name")
```

means:

> column named `name`

while:

```python
F.lit("name")
```

means:

> literal string `"name"`

---

## Mistake 7 — Assuming In-Place Mutation

Incorrect mental model:

```python
df.withColumn(...)
```

means `df` was changed.

Correct:

```python
df2 = df.withColumn(...)
```

or:

```python
df = df.withColumn(...)
```

---

## Mistake 8 — Forgetting Assignment

This result is discarded:

```python
df.withColumn(
    "revenue",
    F.col("price") * F.col("quantity"),
)
```

Capture the returned DataFrame:

```python
df = df.withColumn(
    "revenue",
    F.col("price") * F.col("quantity"),
)
```

---

## Mistake 9 — Accidentally Replacing a Column

This:

```python
df.withColumn(
    "price",
    F.col("price") * 1.18,
)
```

replaces the output `price` expression.

If the intent is to preserve the original price:

```python
df.withColumn(
    "price_with_tax",
    F.col("price") * 1.18,
)
```

is clearer.

---

## Mistake 10 — Selecting a Nonexistent Column

```python
df.select("customer_id", "does_not_exist")
```

will fail because the requested field is not available in the input schema.

Debug with:

```python
df.columns
df.printSchema()
```

---

## Mistake 11 — Ambiguous Column References

When transformations become more complex, explicit references such as:

```python
F.col("customer_id")
```

can be clearer than relying on attribute-style access.

Detailed join-related ambiguity is covered later.

---

## Mistake 12 — Using `collect()` to Process Data

Do not use:

```python
rows = df.collect()
```

as a normal way to process a large DataFrame.

`collect()` moves all resulting rows to the driver and can exhaust driver memory.

For this topic, inspect small samples with:

```python
df.show()
```

and perform distributed transformations with DataFrame expressions.

---

# 59. Common Misconceptions

## Misconception 1

> "`df.age` is a Python integer."

No. It is a Spark `Column` reference.

## Misconception 2

> "`select()` immediately processes the data."

No. `select()` is a transformation and is lazy.

## Misconception 3

> "`withColumn()` mutates the DataFrame."

No. It returns a new DataFrame representing the transformation.

## Misconception 4

> "`filter()` uses normal Python boolean evaluation."

No. It expects a Spark expression/predicate.

## Misconception 5

> "`and` and `or` should be used with Spark Column expressions."

No. Use `&` and `|`.

## Misconception 6

> "`None` should be checked with `==`."

Use:

```python
isNull()
isNotNull()
```

## Misconception 7

> "`select()` only selects existing columns."

No. It can contain expressions and therefore produce derived columns.

## Misconception 8

> "`withColumn()` can only create new columns."

No. It can replace an existing output column.

## Misconception 9

> "`F.col()` contains the actual column data."

No. It represents a column reference/expression.

## Misconception 10

> "`collect()` is a normal way to process a DataFrame."

No. It brings the result to the driver and should be used only when the resulting data is known to be appropriately small.

---

# 60. Advanced Foundation: Expression Trees and Structured Transformations

You do not yet need to understand Catalyst internals, but you should understand that a Spark expression has structure.

Consider:

```python
F.col("price") * F.col("quantity")
```

Conceptually:

```text
       multiply
       /      \
    price   quantity
```

Likewise:

```python
(F.col("age") > 30) & (F.col("city") == "Delhi")
```

can be understood as:

```text
             AND
            /   \
       age > 30  city = Delhi
```

This is very different from a Python loop that manually examines one record at a time.

DataFrame APIs let you describe **logical operations over structured data**.

---

# 61. Logical Transformation Model

The core DataFrame transformations in this topic describe different logical operations:

```text
filter
  ↓
row selection

select
  ↓
column projection

withColumn
  ↓
column derivation/replacement
```

These operations form a lazy computation.

Later topics will examine how Spark optimizes and physically executes these structured operations. For now, focus on writing correct expressions and predicting their schema and row behavior.

---

# 62. Interview Preparation

## Basic

### 1. What is a PySpark DataFrame?

**Model answer:**  
A PySpark DataFrame is a distributed, structured collection of data organized into rows and named columns with a schema. It provides a high-level API for expressing transformations over distributed data.

### 2. What is a Spark `Column`?

**Model answer:**  
A `Column` represents a reference to a field or an expression used in a DataFrame transformation. It is not a Python container holding all values of the distributed column.

### 3. What does `select()` do?

**Model answer:**  
`select()` constructs a new DataFrame containing the requested columns and/or expressions. It is a transformation and is evaluated lazily.

### 4. What does `filter()` do?

**Model answer:**  
`filter()` selects rows satisfying a predicate expression.

### 5. What is the difference between `filter()` and `where()`?

**Model answer:**  
For ordinary DataFrame row filtering, they provide equivalent filtering semantics. The choice is primarily about readability and team convention.

### 6. What does `withColumn()` do?

**Model answer:**  
It returns a new DataFrame with a named column defined by a Spark expression. If the name already exists, the output expression for that column is replaced.

### 7. Does `withColumn()` mutate the original DataFrame?

**Model answer:**  
No. DataFrames are immutable logical objects. `withColumn()` returns another DataFrame representing the transformation.

### 8. What is `F.col()`?

**Model answer:**  
`F.col("name")` creates an explicit Spark Column reference for the named DataFrame field.

### 9. Why use `F.lit()`?

**Model answer:**  
`F.lit()` embeds a literal Python value as a Spark expression, such as `F.lit("unknown")`.

### 10. Why cannot Python `and` and `or` be used for Column expressions?

**Model answer:**  
Spark Column expressions use overloaded operators to construct Spark logical expressions. Use `&`, `|`, and `~` for AND, OR, and NOT, with parentheses around individual predicates.

---

## Moderate

### 11. How do you combine multiple filter conditions?

```python
df.filter(
    (F.col("age") > 30)
    & (F.col("city") == "Delhi")
)
```

Use `&`, `|`, and `~` rather than Python `and`, `or`, and `not`.

### 12. How do you handle nulls in a filter?

Use:

```python
F.col("age").isNull()
```

or:

```python
F.col("age").isNotNull()
```

### 13. What is the difference between `select()` and `withColumn()`?

`select()` defines the output projection and can retain only explicitly requested columns and expressions. `withColumn()` is intended to add or replace a named column while retaining the other columns.

### 14. What is a column expression?

It is a structured Spark expression that describes how a value should be derived from columns, literals, operators, and Spark functions.

### 15. Why are DataFrame transformations lazy?

Lazy evaluation lets Spark build a computation before executing it, allowing the engine to reason about the transformation chain and execute it when an action requires a result.

### 16. How can `select()` create a derived column?

```python
df.select(
    (F.col("price") * F.col("quantity")).alias("revenue")
)
```

### 17. What is `alias()` used for?

It gives a clear name to a selected column or derived expression in the output schema.

### 18. What does `df.select("*")` mean?

It selects all columns from the DataFrame.

---

## Hard

### 19. Why might a filter return zero rows even though the source appears to contain matching values?

Possible causes include:

- incorrect predicate
- unexpected data type
- whitespace or casing differences
- null values
- incorrect column name
- business-rule mismatch
- combining predicates more restrictively than expected

Debug by testing each predicate independently and inspecting the schema and sample values.

### 20. Why can a derived column contain nulls?

Because source values may be null, and many expressions propagate nulls. Inspect the input values and expression semantics before deciding whether a default should be applied.

### 21. How would you debug an unexpected output schema?

Inspect:

```python
df.printSchema()
df.columns
df.dtypes
```

Then identify which transformation changed the projection or expression type.

### 22. Why can `select()` be useful at the end of a pipeline?

It makes the intended final schema explicit: selected columns, column names, order, casts, and derived expressions.

### 23. Why can replacing a column with `withColumn()` be risky?

The transformation can change the meaning or type of an existing field while retaining the same field name. Downstream systems may therefore receive a semantically different value without an obvious schema-name change.

### 24. What is the difference between a Python value and a Spark Column expression?

A Python value exists locally in Python. A Spark Column describes a computation or field reference that Spark can apply to distributed DataFrame data.

### 25. Why are parentheses important in complex predicates?

They make the intended expression tree explicit and prevent Python operator-precedence rules from producing an unintended expression.

### 26. Why should Spark-native expressions generally be preferred for ordinary DataFrame transformations?

They express the transformation in Spark's structured DataFrame API rather than requiring arbitrary Python row processing. Detailed UDF execution trade-offs belong to Topic 11.

---

## Advanced / Production

### 27. When would you prefer `select()` over a long sequence of `withColumn()` calls?

When the primary goal is to define a clear final projection or a set of derived output expressions. A single projection can make the intended schema easier to review.

### 28. How would you design a production transformation chain?

Start from an explicit input contract, filter according to business rules, derive fields using Spark-native expressions, standardize types, and finish with an explicit output projection. Then use an action or downstream write to execute the computation.

### 29. How should null defaults be chosen?

Based on the business meaning of the field. A technically convenient default can be semantically incorrect.

### 30. How do you reason about performance at this stage?

Avoid unnecessary columns and rows, use Spark-native expressions, and understand lazy transformations. Deeper physical optimization belongs to later topics.

### 31. Why is a final schema contract valuable?

It makes downstream expectations explicit and reduces accidental propagation of irrelevant or unstable source fields.

### 32. What questions should you ask before using `withColumn()` to replace an existing field?

Ask whether the replacement is intentional, whether the type remains correct, whether the semantic definition remains correct, and whether the original value should be retained.

---

## Architecture-Level Questions

### 33. Design a transaction transformation API boundary.

Your function should accept a DataFrame with a documented input schema and return a DataFrame with a documented output schema.

### 34. Where should business rules live?

They should be expressed clearly in transformation code or a defined configuration/rules layer, rather than being hidden inside arbitrary row-level Python logic.

### 35. How would you make a DataFrame transformation reviewable?

Use meaningful column names, explicit expressions, small composable transformations, a final schema projection, and tests that verify representative input/output behavior.

### 36. How would you investigate a production transformation producing unexpectedly low row counts?

Start with the input count and schema, inspect each predicate separately, examine null and type behavior, and identify the first transformation where rows diverge from expectations.

### 37. How would you design a transformation so downstream consumers are protected from source schema drift?

Use an explicit input contract and explicit final projection with deliberate type conversions and names rather than blindly propagating every input column.

### 38. Why should transformation intent be visible in code?

Because production pipelines are maintained by multiple engineers. Code that clearly communicates filtering, derivation, and projection is easier to review, debug, and evolve.

---

# 63. Practice Questions

## Basic — 10 Questions

1. What is a PySpark DataFrame?
2. What is a Spark `Column`?
3. What does `df.select("name")` return?
4. What does `df.filter(F.col("age") > 30)` mean?
5. What does `df.where(...)` do?
6. What does `withColumn()` return?
7. Does `withColumn()` mutate the input DataFrame?
8. What is the purpose of `F.col()`?
9. What is the purpose of `F.lit()`?
10. What does `df.select("*")` do?

### Suggested answers

1. A distributed structured dataset with named columns and a schema.
2. A field reference or expression used in DataFrame transformations.
3. A new DataFrame projected to the `name` column.
4. A filtered DataFrame containing rows whose `age` satisfies the predicate.
5. It performs DataFrame row filtering with equivalent semantics to `filter()`.
6. A new DataFrame containing the added or replaced output column.
7. No.
8. To explicitly construct a Column reference/expression.
9. To construct a literal expression.
10. It selects all columns.

---

## Moderate — 10 Questions

1. Rewrite a filter using two conditions with AND.
2. Rewrite a filter using two conditions with OR.
3. How do you negate a Spark predicate?
4. Why is `and` incorrect for Spark Column expressions?
5. How do you test whether a column is null?
6. How do you create `revenue = price * quantity`?
7. How do you rename `name` to `customer_name` in `select()`?
8. How do you create an age category with `when()`?
9. How do you replace a null value with a literal?
10. How do you cast a string amount to `double`?

### Suggested solutions

```python
df.filter(
    (F.col("age") > 30)
    & (F.col("city") == "Delhi")
)
```

```python
df.filter(
    (F.col("city") == "Delhi")
    | (F.col("city") == "Mumbai")
)
```

```python
df.filter(~(F.col("age") > 30))
```

Use Spark expression operators `&`, `|`, and `~`.

```python
F.col("age").isNull()
```

```python
df.withColumn(
    "revenue",
    F.col("price") * F.col("quantity"),
)
```

```python
df.select(
    F.col("name").alias("customer_name")
)
```

```python
F.when(
    F.col("age") < 18,
    "minor",
).otherwise("adult")
```

```python
F.coalesce(
    F.col("age"),
    F.lit(0),
)
```

```python
F.col("amount").cast("double")
```

---

## Hard — 10 Questions

1. A filter returns zero rows. Describe a systematic debugging process.
2. A `select()` unexpectedly removes a field. Explain why.
3. A `withColumn()` unexpectedly changes the meaning of an existing field. What happened?
4. Why can a `revenue` expression return null?
5. Explain the difference between `F.col("source")` and `F.lit("source")`.
6. Explain why `select()` can act as both a projection and a derivation step.
7. Explain why a final explicit projection can improve maintainability.
8. Explain how null semantics can affect a predicate.
9. Explain why `df.show()` changes the execution behavior of a lazy pipeline.
10. Rewrite a long series of independent transformations into a clear final projection when appropriate.

### Reasoning direction

For each question, identify:

```text
Input schema
   ↓
Expression
   ↓
Transformation semantics
   ↓
Output schema
   ↓
Action/inspection
```

---

## Advanced — 10 Questions

1. Design a transformation boundary with explicit input and output schemas.
2. Explain when `select()` communicates intent better than `withColumn()`.
3. Design a reusable transaction-cleaning transformation without Python row loops.
4. Explain how a careless null default can create semantic data corruption.
5. Design a debugging workflow for a production filter that suddenly returns fewer rows.
6. Explain why Spark-native expressions are useful for structured transformations.
7. Design a final analytics-ready projection that standardizes names and types.
8. Explain the difference between logical transformation intent and physical optimization.
9. Explain why manually moving every filter earlier is not a guarantee of a different physical plan.
10. Design a transformation chain that another engineer can review without knowing the entire source system.

For each answer, explicitly discuss:

- business rule
- expression
- schema
- null behavior
- transformation intent
- lazy execution
- production maintainability

---

# 64. Final Architecture Exercise

## Scenario

A transaction dataset contains:

```text
transaction_id
customer_id
customer_name
price
quantity
status
created_at
```

Requirements:

1. Keep only valid active transactions.
2. Clean customer names.
3. Calculate revenue.
4. Create a transaction category.
5. Standardize data types.
6. Produce a final analytics-ready schema.

Design:

```text
Input DataFrame
       ↓
filter()
       ↓
withColumn()
       ↓
withColumn()
       ↓
select()
       ↓
Final DataFrame
       ↓
write/output action
```

## Reference Solution

```python
from pyspark.sql import functions as F

final_df = (
    transactions
    .filter(
        (F.col("status") == "active")
        & F.col("transaction_id").isNotNull()
        & F.col("customer_id").isNotNull()
    )
    .withColumn(
        "customer_name",
        F.trim(F.col("customer_name")),
    )
    .withColumn(
        "price",
        F.col("price").cast("double"),
    )
    .withColumn(
        "quantity",
        F.col("quantity").cast("long"),
    )
    .withColumn(
        "revenue",
        F.col("price") * F.col("quantity"),
    )
    .withColumn(
        "transaction_category",
        F.when(
            F.col("revenue") >= 1000,
            "high",
        )
        .when(
            F.col("revenue") >= 100,
            "medium",
        )
        .otherwise("low"),
    )
    .select(
        "transaction_id",
        "customer_id",
        "customer_name",
        "price",
        "quantity",
        "revenue",
        "transaction_category",
        "created_at",
    )
)
```

### Explain the design

#### Why `filter()` first?

The pipeline establishes row eligibility:

```python
(F.col("status") == "active")
```

and rejects rows missing key identifiers:

```python
F.col("transaction_id").isNotNull()
F.col("customer_id").isNotNull()
```

Whether those are the correct validity rules is a business decision; the exercise demonstrates how such rules are expressed.

#### Why `withColumn()`?

It derives or standardizes individual fields:

```text
customer_name
price
quantity
revenue
transaction_category
```

#### Why `select()` last?

It makes the final analytics schema explicit.

#### Which operations are lazy?

The following are transformations:

```text
filter()
withColumn()
withColumn()
withColumn()
withColumn()
select()
```

The actual work is triggered by an action such as a write or:

```python
final_df.show()
```

#### What mistakes could occur?

Examples:

- incorrect status vocabulary
- null identifiers
- invalid numeric values
- incorrect type assumptions
- incorrect category thresholds
- unexpected null customer names
- accidentally changing a field's semantic meaning
- missing output columns

#### How would you debug it?

Inspect:

```python
final_df.printSchema()
final_df.show(truncate=False)
```

Then isolate transformations and predicates until the first incorrect result is found.

---

# 65. Knowledge Checkpoint

Do not move forward until you can explain these without notes.

## DataFrame

- What is a DataFrame?
- What is a Column?
- How is a Spark Column different from a Python scalar?

## `select()`

- What does it do?
- Can it create derived columns?
- What is `alias()`?
- What does `"*"` mean?
- Why is it useful for final schema design?

## `filter()`

- What is a predicate?
- How do you combine conditions?
- What is `where()`?
- Why are `&`, `|`, and `~` used?
- How do null predicates work?

## `withColumn()`

- How do you create a column?
- How do you replace an existing column?
- Does it mutate the original DataFrame?
- Why does assignment matter?

## Expressions

- What is `F.col()`?
- What is `F.lit()`?
- What is `when()`?
- What is `otherwise()`?
- What is `coalesce()`?
- How do null checks work?
- How does casting affect schema?

## Production

- How would you design a clean transformation chain?
- How would you debug an incorrect filter?
- How would you avoid unnecessary columns?
- Why should Spark-native expressions generally be preferred for ordinary transformations?
- What business questions should you ask before applying a null default?
- How would you make a final schema explicit?

A strong learner should be able to write a transformation and explain the **expression, schema, row behavior, and lazy execution model** without relying on trial and error.

---

# 66. Production Engineering Mindset

For every transformation, ask:

```text
What columns do I actually need?

Which rows should survive?

What is the business rule?

What is the expression?

What data type does the expression produce?

What happens with nulls?

Am I replacing an existing column accidentally?

Is this transformation lazy?

What action eventually executes it?

Is the transformation readable?

Can another engineer understand the schema?

Am I using Spark-native expressions?

Am I accidentally moving data to the driver?

Is the output schema explicit?
```

This is the mindset that turns API knowledge into production Data Engineering skill.

---

# 67. Topic Completion Standard

You should consider this topic complete only when you can independently:

1. Create a small PySpark DataFrame.
2. Inspect its schema.
3. Reference columns with `F.col()`.
4. Explain what a Column expression represents.
5. Use `select()` for projection.
6. Use aliases for output naming.
7. Create derived expressions inside `select()`.
8. Use `selectExpr()` when appropriate.
9. Filter with `filter()` and `where()`.
10. Combine predicates using `&`, `|`, and `~`.
11. Handle null predicates correctly.
12. Create derived columns with `withColumn()`.
13. Replace a column intentionally.
14. Use `lit()`.
15. Use `when()` and `otherwise()`.
16. Use `coalesce()` appropriately.
17. Cast basic types.
18. Build readable transformation chains.
19. Inspect output using `show()`.
20. Debug incorrect filters and schemas.
21. Explain why transformations are lazy.
22. Explain why Spark-native expressions fit distributed DataFrame processing.
23. Design a final explicit output projection.
24. Explain the production trade-offs between `select()` and `withColumn()`.

---

# 68. Final Summary

The central mental model is:

```text
DataFrame
    ↓
Column references
    ↓
Column expressions
    ↓
select()
filter()
withColumn()
    ↓
Transformation chain
    ↓
Lazy execution
    ↓
Action
    ↓
Distributed processing
```

The essential distinction is:

> **`select()` controls which columns and expressions form the output, `filter()` controls which rows satisfy a predicate, and `withColumn()` creates or replaces a column using a Spark expression.**

These APIs are the fundamental vocabulary for expressing structured transformations in PySpark.

The deeper skill is not memorizing method names. It is being able to look at a transformation and reason about:

```text
What is the input schema?
        ↓
What is the Column expression?
        ↓
Which rows survive?
        ↓
Which columns are produced?
        ↓
What are their types?
        ↓
What happens with nulls?
        ↓
What remains lazy?
        ↓
Which action eventually executes it?
```

That reasoning becomes the foundation for later topics such as Spark SQL, joins, partitioning, skew, caching, UDFs, Catalyst, AQE, data sources, and Spark UI debugging.

---

# 69. Glossary

**DataFrame** — A distributed structured dataset with named columns and a schema.

**Column** — A Spark object representing a field reference or expression.

**Column expression** — A structured Spark expression describing a computation over DataFrame fields, literals, operators, and functions.

**Projection** — Selecting or deriving the columns that appear in an output.

**Predicate** — A condition used to decide whether a row satisfies a filter.

**Transformation** — A lazy DataFrame operation that describes a new computation.

**Action** — An operation that requires Spark to execute the computation and produce a result or external effect.

**Lazy evaluation** — Spark's deferred execution model in which transformations build a computation before execution is required.

**Schema** — The structured description of DataFrame fields and their data types.

**Alias** — A name assigned to a selected column or expression in an output.

**Literal** — A fixed value represented as part of a Spark expression.

**Null** — A missing/unknown value with SQL-style semantics distinct from ordinary Python values.

**`select()`** — A DataFrame transformation for defining output columns and expressions.

**`selectExpr()`** — A DataFrame projection API that accepts SQL-style expression strings.

**`filter()`** — A DataFrame transformation that retains rows satisfying a predicate.

**`where()`** — An equivalent DataFrame row-filtering API.

**`withColumn()`** — A DataFrame transformation that adds or replaces a named output column.

**`when()`** — A function for constructing conditional Spark expressions.

**`otherwise()`** — Defines the fallback branch of a `when()` expression.

**`coalesce()`** — Returns the first non-null expression among its arguments.

**`cast()`** — Converts an expression to a specified data type.

**Spark-native expression** — A DataFrame expression represented using Spark's structured API rather than arbitrary row-level Python logic.

**Driver** — The process coordinating a Spark application and requesting distributed computation.

**Executor** — A Spark worker process that executes tasks and holds executor-side data.

---

# 70. Final Self-Review

## File Scope

- [x] This chapter is self-contained.
- [x] It is intended only for `05-dataframe-api-select-filter-and-withcolumn.md`.
- [x] No additional project files are required by the chapter.
- [x] No notebooks or configuration changes are required.

## Roadmap Alignment

- [x] Topic 05 is covered.
- [x] Topic 03 DataFrame concepts are connected.
- [x] Topic 04 transformations/actions/lazy evaluation are connected.
- [x] Later topics are referenced only for context.
- [x] Joins, partition tuning, skew, caching, UDFs, Catalyst, AQE, data sources, Spark UI, and advanced testing are not deeply duplicated.

## DataFrame Fundamentals

- [x] DataFrame
- [x] Column
- [x] Column expression
- [x] Schema
- [x] Column references
- [x] `F.col()`
- [x] `F.lit()`

## `select()`

- [x] Basic selection
- [x] Column expressions
- [x] Aliases
- [x] `"*"`
- [x] Derived columns
- [x] `selectExpr()`
- [x] Projection concept

## `filter()`

- [x] Basic predicates
- [x] `where()`
- [x] Comparison operators
- [x] `&`
- [x] `|`
- [x] `~`
- [x] `isin()`
- [x] Null checks
- [x] String predicates

## `withColumn()`

- [x] Creating columns
- [x] Replacing columns
- [x] Immutability
- [x] Arithmetic
- [x] Conditional expressions
- [x] `when()`
- [x] `otherwise()`
- [x] `coalesce()`
- [x] Casting
- [x] Date/timestamp basics

## Practical Learning

- [x] Transformation chaining
- [x] Schema inspection
- [x] Output inspection
- [x] Debugging
- [x] Common mistakes
- [x] Hands-on labs
- [x] Production scenarios
- [x] Mini-project

## Learning Validation

- [x] Knowledge checkpoint
- [x] Practice questions
- [x] Interview questions
- [x] Architecture exercise
- [x] Glossary
- [x] Final summary

---

## Final Topic Takeaway

You should now be able to mentally and programmatically move through:

```text
DataFrame
    ↓
Column
    ↓
Column Expression
    ↓
select()
    ↓
filter()
    ↓
withColumn()
    ↓
Transformation Chain
    ↓
Lazy Evaluation
    ↓
Action
    ↓
Distributed Execution
```

And you should be comfortable writing foundational production-oriented transformations with:

```python
from pyspark.sql import functions as F
```

and:

```python
F.col()
F.lit()
F.when()
F.coalesce()
F.upper()
F.lower()
F.trim()
F.concat_ws()
```

together with:

```python
df.select(...)
df.filter(...)
df.where(...)
df.withColumn(...)
```

The goal is not to memorize an API cheat sheet. The goal is to understand how **structured Spark expressions describe distributed transformations**, how those transformations remain lazy until an action requires execution, and how to express production DataFrame logic clearly and safely.
