# 01 — SELECT, Filter, Sort, and NULL Semantics

> **Module:** 2.6 — SQL for Data Engineers  
> **Phase:** A — Querying Correctly  
> **Primary engines:** PostgreSQL 16+ and DuckDB  
> **Core idea:** Write SQL that is correct before trying to make it fast.

This chapter establishes the foundation for production-grade SQL. The goal is not to memorize clauses. The goal is to understand **what rows exist at each logical stage, what each expression means, how `NULL` changes truth values, how ordering affects repeatability, and how small syntax choices can create silent data-quality or performance problems**.

The chapter follows the Module 2.6 dependency chain. Later topics will build on these foundations for joins, aggregation, CTEs, windows, deduplication, indexing, and incremental loads.

---

## 1. Learning Objectives

By the end of this chapter, you should be able to:

- Explain SQL's logical order of execution:
  `FROM → WHERE → GROUP BY → HAVING → window functions → SELECT → DISTINCT → ORDER BY → LIMIT`.
- Explain the difference between **logical query processing** and **physical query execution**.
- Write `SELECT`, `FROM`, `WHERE`, `ORDER BY`, `LIMIT`, `OFFSET`, and `FETCH FIRST`.
- Use column aliases, expressions, arithmetic, literals, and qualified names.
- Write correct comparison and boolean predicates using `AND`, `OR`, `NOT`, `IN`, `BETWEEN`, `LIKE`, and `CASE`.
- Use `LOWER`, `TRIM`, `SUBSTRING`, `CONCAT`, `||`, `ROUND`, `ABS`, `CURRENT_DATE`, `DATE_TRUNC`, `EXTRACT`, and intervals.
- Explain `NULL` and SQL's three-valued logic: `TRUE`, `FALSE`, and `UNKNOWN`.
- Explain why `NULL = NULL` is not `TRUE` and why `WHERE` keeps only rows whose condition is `TRUE`.
- Use `IS NULL`, `IS NOT NULL`, `COALESCE`, `NULLIF`, and `IS DISTINCT FROM` intentionally.
- Explain the `NOT IN` + `NULL` trap instead of memorizing a workaround.
- Handle `NULL` in comparisons, arithmetic, concatenation, and sorting.
- Use deterministic ordering with tie-breaker columns.
- Cast values explicitly with `CAST(...)` and PostgreSQL's `::type` syntax.
- Explain integer division and why `5 / 2` behaves differently when operands are cast to a decimal type.
- Distinguish `timestamp` and `timestamptz` in PostgreSQL.
- Write production-safe **half-open time ranges** using `>= start AND < end`.
- Explain **sargable predicates** and understand why a function or transformation around a filtered column can interfere with efficient index usage or partition pruning.
- Use **keyset / seek pagination** and explain its trade-offs against `OFFSET`.
- Identify relevant PostgreSQL/DuckDB dialect differences.
- Test SQL like code using small datasets and assertion queries that return zero rows when correct.

---

## 2. Why This Topic Is Foundational for Data Engineering

This topic comes first because nearly every later SQL technique depends on these semantics.

A data engineer frequently writes queries that:

- extract rows from an operational database,
- filter records for an incremental load,
- classify records,
- generate derived values,
- produce deterministic exports,
- validate source data,
- feed later joins and aggregations,
- filter event data by time,
- paginate through a large source table.

A query can be syntactically valid and still be wrong.

The dangerous failures are often **silent**:

```sql
WHERE email = NULL
```

returns no rows rather than raising an obvious error.

```sql
WHERE country <> 'India'
```

does not mean "everything except India" when `country` can be `NULL`.

```sql
ORDER BY created_at
LIMIT 100
```

does not define a deterministic subset when many rows share the same timestamp.

```sql
WHERE created_at BETWEEN '2025-03-01' AND '2025-03-31'
```

can mishandle the end of a timestamp window.

```sql
WHERE DATE(created_at) = DATE '2025-03-01'
```

may be logically correct while also giving an optimizer fewer opportunities to use an index or prune partitions.

The engineering habit introduced here is:

> **First make the semantics explicit. Then consider performance.**

Later topics depend directly on these foundations:

| Foundation here | Later dependency |
|---|---|
| Logical query order | Understanding joins, aggregation, CTEs, and windows |
| `NULL` semantics | Joins, `NOT IN`, aggregation, deduplication |
| Deterministic ordering | Window functions, deduplication, pagination |
| Half-open time ranges | Incremental extraction and partition pruning |
| Sargability | Indexes and execution plans |
| Explicit casts | Correct metrics and cross-dialect behavior |

This chapter does **not** teach joins, aggregation, windows, indexes, or incremental loading in depth. It gives you the semantic foundation required for those topics.

---

## 3. SQL Mental Model

### 3.1 SQL is declarative

SQL is primarily a **declarative language**.

You say what result you want:

```sql
SELECT customer_id, email
FROM customers
WHERE country = 'India';
```

You generally do not tell the database:

> "Scan page 1, inspect row 1, compare the country, then move to row 2."

The database chooses an execution strategy.

### 3.2 Two different ways to think about a query

There are two important models:

1. **Logical query processing** — the semantic order used to understand what the query means.
2. **Physical execution** — the actual operations chosen by the optimizer and executor.

These are related but are not the same thing.

### 3.3 Logical processing is a reasoning tool

For example:

```sql
SELECT
    amount * 1.18 AS gross_amount
FROM orders
WHERE gross_amount > 100;
```

The important question is not:

> "Does PostgreSQL happen to evaluate `gross_amount` early?"

The semantic question is:

> "At the logical point where `WHERE` is evaluated, has the `SELECT` alias been created?"

No. The alias belongs to the `SELECT` output stage.

### 3.4 Physical execution can be different

A database optimizer may:

- push filters down,
- choose an index,
- reorder joins,
- avoid unnecessary work,
- combine operations,
- use a parallel plan.

Those are **physical execution decisions**.

The optimizer must preserve the query's required result semantics even when the physical execution order differs from the logical model.

---

# 4. Logical Order of SQL Execution

For this module, use the roadmap's logical order:

```text
FROM
  ↓
WHERE
  ↓
GROUP BY
  ↓
HAVING
  ↓
Window functions
  ↓
SELECT
  ↓
DISTINCT
  ↓
ORDER BY
  ↓
LIMIT / OFFSET
```

This is a conceptual model for understanding visibility and semantics.

## 4.1 Stage 1 — `FROM`

### What it receives

The named table or table source.

### What it produces

A row source that later stages can filter and transform.

### What it can see

Columns exposed by the table source.

### What it cannot see

Columns or aliases that are created later in the logical pipeline.

Example:

```sql
SELECT customer_id, email
FROM customers;
```

Conceptually:

```text
customers table
      ↓
   FROM
      ↓
set of customer rows
```

Detailed join processing belongs to Topic 02, so keep the current mental model simple: `FROM` establishes where rows come from.

---

## 4.2 Stage 2 — `WHERE`

`WHERE` filters rows.

```sql
SELECT customer_id, email
FROM customers
WHERE country = 'India';
```

Conceptually:

```text
all rows
   ↓
WHERE predicate
   ↓
rows whose predicate is TRUE
```

An important rule:

> `WHERE` keeps rows where the predicate is **TRUE**.

It does not keep rows where the predicate is merely "not FALSE". This becomes critical when the predicate evaluates to `UNKNOWN` because of `NULL`.

---

## 4.3 Stage 3 — `GROUP BY`

`GROUP BY` changes the row shape by forming groups.

Example:

```sql
SELECT
    country,
    COUNT(*) AS customer_count
FROM customers
GROUP BY country;
```

The important concept is the **output grain**.

Before grouping:

```text
one row per customer
```

After grouping:

```text
one row per country
```

Detailed aggregation is Topic 03. Here, the key point is that later stages do not necessarily see the same individual rows that entered the query.

---

## 4.4 Stage 4 — `HAVING`

`HAVING` filters groups after grouping.

```sql
SELECT
    country,
    COUNT(*) AS customer_count
FROM customers
GROUP BY country
HAVING COUNT(*) > 100;
```

`WHERE` filters rows.

`HAVING` filters groups.

---

## 4.5 Stage 5 — Window functions

Window functions calculate across related rows without collapsing them into one row per group.

Example:

```sql
SELECT
    customer_id,
    order_id,
    amount,
    SUM(amount) OVER (
        PARTITION BY customer_id
    ) AS customer_total
FROM orders;
```

Detailed window semantics belong to Topic 05. For this chapter, know that window functions are logically later than `WHERE`, `GROUP BY`, and `HAVING`, which explains why you normally cannot use a window result directly in `WHERE`.

---

## 4.6 Stage 6 — `SELECT`

`SELECT` forms the output columns.

This is where expressions and aliases are normally created:

```sql
SELECT
    amount,
    amount * 1.18 AS gross_amount
FROM orders;
```

The alias `gross_amount` is now part of the output expression.

### Why this matters

Consider:

```sql
SELECT
    amount * 1.18 AS gross_amount
FROM orders
WHERE gross_amount > 100;
```

The problem is that `WHERE` comes logically before `SELECT`.

A portable mental model is:

```text
FROM
  ↓
WHERE
  ↓
...
  ↓
SELECT creates gross_amount
```

Therefore `WHERE` cannot generally refer to that `SELECT` alias.

### Correct alternative 1 — repeat the expression

```sql
SELECT
    amount * 1.18 AS gross_amount
FROM orders
WHERE amount * 1.18 > 100;
```

### Correct alternative 2 — use a derived table

```sql
SELECT
    gross_amount
FROM (
    SELECT
        amount * 1.18 AS gross_amount
    FROM orders
) AS q
WHERE gross_amount > 100;
```

The second form creates a new query boundary where the alias already exists.

---

## 4.7 Stage 7 — `DISTINCT`

`DISTINCT` removes duplicate output rows.

```sql
SELECT DISTINCT country
FROM customers;
```

It operates on the selected result.

A key warning:

> `DISTINCT` is a result-set operation. It is not a universal fix for a logic problem.

Later join and deduplication topics will show why blindly adding `DISTINCT` can hide an incorrect grain.

---

## 4.8 Stage 8 — `ORDER BY`

`ORDER BY` determines the requested output ordering.

```sql
SELECT customer_id, created_at
FROM customers
ORDER BY created_at DESC;
```

Without `ORDER BY`, the SQL language does not promise a useful business ordering.

---

## 4.9 Stage 9 — `LIMIT` / pagination

`LIMIT`, `OFFSET`, and `FETCH FIRST` restrict how many rows are returned.

```sql
SELECT customer_id
FROM customers
ORDER BY customer_id
LIMIT 10;
```

The `ORDER BY` matters when you care which rows are included.

---

## 4.10 Why logical order matters

The logical model helps answer questions such as:

- Why can't a `WHERE` clause usually see a `SELECT` alias?
- Why must row filtering happen before grouping?
- Why must a window result usually be filtered by an outer query?
- Why does `LIMIT` without `ORDER BY` fail to define "the first 10 rows"?
- Why can a `NULL` predicate remove a row silently?

---

## 4.11 Logical order is not physical execution order

Do not conclude that PostgreSQL literally performs every query in the exact sequence shown above.

For example, an optimizer may push a filter closer to the storage layer.

That is a **physical optimization**.

The query's semantics still correspond to the logical model.

---

# 5. SELECT Fundamentals

## 5.1 `SELECT *`

The simplest query is:

```sql
SELECT *
FROM customers;
```

This means:

> Return all columns from `customers`.

It is useful during exploration.

### Why production SQL usually prefers explicit columns

Prefer:

```sql
SELECT
    customer_id,
    email,
    country
FROM customers;
```

Reasons include:

- You document what the query actually needs.
- Schema additions do not silently change the output shape.
- Downstream consumers are less likely to break unexpectedly.
- Reviews are easier.
- Data transfer can be smaller.
- Accidental exposure of unnecessary columns is reduced.

`SELECT *` is not "always wrong." It is simply a risky default for stable production interfaces.

---

## 5.2 Column aliases

Aliases improve readability:

```sql
SELECT
    customer_id AS id,
    created_at AS registered_at
FROM customers;
```

Good aliases communicate meaning.

Prefer:

```sql
amount * 1.18 AS gross_amount
```

over:

```sql
amount * 1.18 AS x
```

---

## 5.3 Expressions

A `SELECT` expression can calculate a value.

```sql
SELECT
    order_id,
    amount,
    amount * 1.18 AS gross_amount,
    amount - discount AS net_before_tax
FROM orders;
```

The database evaluates the expressions using the values visible to the query.

---

## 5.4 Literals

You can return constant values:

```sql
SELECT
    customer_id,
    'source_a' AS source_system
FROM customers;
```

Numeric literals:

```sql
SELECT
    customer_id,
    1 AS batch_version
FROM customers;
```

Literals are useful for labeling extracted or unioned data.

---

## 5.5 Qualified column names

Use a qualifier when it improves clarity:

```sql
SELECT
    customers.customer_id,
    customers.email
FROM customers;
```

Aliases are usually shorter:

```sql
SELECT
    c.customer_id,
    c.email
FROM customers AS c;
```

This becomes especially important once queries use multiple tables.

---

## 5.6 Arithmetic operators

Typical arithmetic:

```sql
SELECT
    amount,
    amount + tax AS total,
    amount - discount AS discounted_amount,
    amount * 1.18 AS gross_amount,
    amount / 100.0 AS amount_in_hundreds
FROM orders;
```

Remember that arithmetic involving `NULL` is usually also `NULL`. We cover this in the NULL sections.

---

## 5.7 Production mistake: `SELECT *` as a contract

Suppose a source table starts as:

```text
customer_id
email
country
```

and later gets:

```text
internal_risk_score
```

A production query using:

```sql
SELECT *
FROM customers;
```

now returns a different schema.

An explicit query:

```sql
SELECT
    customer_id,
    email,
    country
FROM customers;
```

keeps its output contract stable.

---

# 6. FROM and Table Sources

## 6.1 What `FROM` means

For a simple table:

```sql
FROM orders
```

means the query gets its rows from `orders`.

Think:

```text
orders
  ↓
row source
  ↓
later query stages
```

---

## 6.2 Table aliases

```sql
FROM orders AS o
```

Then:

```sql
SELECT
    o.order_id,
    o.created_at,
    o.amount
FROM orders AS o;
```

Aliases improve readability and become important in multi-table queries.

---

## 6.3 Schema-qualified names

PostgreSQL commonly uses:

```sql
FROM analytics.orders;
```

The schema is a namespace.

Schema qualification can make dependencies clearer and reduce ambiguity in larger systems.

---

## 6.4 Keep the current mental model simple

Joins are intentionally not taught here.

For now:

> `FROM` answers **"Where do these rows come from?"**

Topic 02 will expand that into how multiple row sources are combined and how join cardinality changes row counts.

---

# 7. WHERE and Row Filtering

## 7.1 What `WHERE` does

`WHERE` selects rows based on a predicate.

```sql
SELECT
    order_id,
    amount
FROM orders
WHERE amount >= 100;
```

Each row is tested against the condition.

---

## 7.2 Comparison operators

Common comparison operators:

| Operator | Meaning |
|---|---|
| `=` | equal |
| `<>` | not equal |
| `!=` | not equal; widely supported, but `<>` is standard SQL |
| `<` | less than |
| `<=` | less than or equal |
| `>` | greater than |
| `>=` | greater than or equal |

Example:

```sql
SELECT *
FROM orders
WHERE amount >= 100;
```

Negative condition:

```sql
SELECT *
FROM customers
WHERE country <> 'India';
```

This looks simple, but becomes subtle with `NULL`.

---

## 7.3 Predicates are expressions

A predicate evaluates to a truth value in SQL's three-valued logic.

You will see:

```text
TRUE
FALSE
UNKNOWN
```

The `UNKNOWN` case is the reason NULL handling is so important.

---

## 7.4 Positive versus negative filters

Positive filter:

```sql
WHERE status = 'active'
```

Negative filter:

```sql
WHERE status <> 'active'
```

The negative filter does **not** automatically include missing status values.

If `status` is `NULL`, then:

```sql
status <> 'active'
```

is `UNKNOWN`, not `TRUE`.

---

# 8. Logical Operators

The main boolean operators are:

- `AND`
- `OR`
- `NOT`

## 8.1 `AND`

```sql
SELECT *
FROM customers
WHERE country = 'India'
  AND status = 'active';
```

Both conditions must be `TRUE`.

---

## 8.2 `OR`

```sql
SELECT *
FROM customers
WHERE country = 'India'
   OR country = 'Bangladesh';
```

At least one condition must be `TRUE`.

---

## 8.3 `NOT`

```sql
SELECT *
FROM customers
WHERE NOT is_deleted;
```

Be careful when `is_deleted` can be `NULL`: `NOT NULL` is `UNKNOWN`, so such a row does not pass the `WHERE`.

---

## 8.4 Operator precedence

Use parentheses when combining `AND` and `OR`.

Potentially confusing:

```sql
WHERE country = 'India'
   OR country = 'Bangladesh'
  AND status = 'active'
```

A reader must know the precedence rules to understand the intended meaning.

Write the business rule explicitly:

```sql
WHERE (
        country = 'India'
        OR country = 'Bangladesh'
      )
  AND status = 'active';
```

This is easier to review and less likely to be misunderstood.

---

## 8.5 Safe production habit

When the logic represents a business rule, prefer explicit parentheses even when you know precedence.

Readability is part of correctness.

---

# 9. IN

`IN` checks whether a value belongs to a set.

```sql
SELECT *
FROM customers
WHERE country IN ('India', 'Nepal', 'Bhutan');
```

Conceptually, this is similar to:

```sql
WHERE country = 'India'
   OR country = 'Nepal'
   OR country = 'Bhutan';
```

`IN` is usually much easier to read for larger lists.

---

## 9.1 `IN` and NULL

A condition involving `NULL` can become `UNKNOWN`.

For example:

```sql
SELECT
    NULL IN ('India', 'Nepal') AS result;
```

The comparison cannot establish that NULL is equal to any listed value, so the result is `UNKNOWN`.

A `WHERE` clause therefore excludes the row.

---

## 9.2 `NOT IN`

```sql
SELECT *
FROM customers
WHERE country NOT IN ('India', 'Nepal');
```

This deserves special caution.

The expression is conceptually a conjunction of "not equal" comparisons. If a relevant comparison becomes `UNKNOWN`, the entire boolean expression can become `UNKNOWN`.

The most dangerous form is when a subquery produces `NULL`:

```sql
WHERE customer_id NOT IN (
    SELECT customer_id
    FROM blocked_customers
);
```

If `blocked_customers.customer_id` contains a `NULL`, the result can be surprising and may return no rows for the outer query.

We will prove why in the dedicated NULL trap section.

---

# 10. BETWEEN

For ordinary scalar values:

```sql
SELECT *
FROM orders
WHERE amount BETWEEN 100 AND 500;
```

`BETWEEN` is **inclusive** at both ends.

Conceptually:

```sql
amount >= 100
AND amount <= 500
```

Therefore:

- `100` is included.
- `500` is included.

This is often exactly what you want for values such as numeric ranges.

---

## 10.1 Why timestamp `BETWEEN` is different

A common mistake is:

```sql
WHERE created_at
      BETWEEN TIMESTAMP '2025-03-01 00:00:00'
          AND TIMESTAMP '2025-03-31 00:00:00'
```

This includes exactly the beginning of March 31, but not the rest of that day.

Another attempted pattern is:

```sql
WHERE created_at
      BETWEEN TIMESTAMP '2025-03-01 00:00:00'
          AND TIMESTAMP '2025-03-31 23:59:59.999999'
```

This is fragile because timestamp precision and literal assumptions can vary. It also makes adjacent windows awkward.

The production pattern is a half-open interval.

---

# 11. LIKE and ILIKE

## 11.1 Wildcards

`LIKE` supports pattern matching.

Two common wildcards are:

| Pattern | Meaning |
|---|---|
| `%` | zero or more characters |
| `_` | exactly one character |

Example:

```sql
SELECT *
FROM customers
WHERE email LIKE '%@example.com';
```

The `%` before `@example.com` means any preceding string.

Example with `_`:

```sql
SELECT *
FROM products
WHERE sku LIKE 'A_23';
```

This matches values such as `AB23` or `AX23`.

---

## 11.2 Case sensitivity

`LIKE` behavior is generally case-sensitive according to the engine's string comparison semantics.

PostgreSQL provides:

```sql
SELECT *
FROM customers
WHERE name ILIKE 'sovon%';
```

`ILIKE` is PostgreSQL-specific syntax for case-insensitive pattern matching.

DuckDB and other engines may provide different mechanisms for case-insensitive matching, so verify the target engine's documentation.

---

## 11.3 Production consideration

Pattern predicates can be useful, but a large table and a leading wildcard such as:

```sql
WHERE email LIKE '%@example.com'
```

may not have the same optimization opportunities as a prefix search.

Do not assume that any `LIKE` predicate will be equally efficient.

Full-text search is outside this chapter.

---

# 12. CASE WHEN

`CASE` implements conditional logic inside SQL expressions.

## 12.1 Searched CASE

```sql
SELECT
    order_id,
    amount,
    CASE
        WHEN amount >= 1000 THEN 'high'
        WHEN amount >= 500 THEN 'medium'
        ELSE 'low'
    END AS order_band
FROM orders;
```

---

## 12.2 Evaluation order

Conditions are evaluated from top to bottom.

For:

```sql
CASE
    WHEN amount >= 1000 THEN 'high'
    WHEN amount >= 500 THEN 'medium'
    ELSE 'low'
END
```

an amount of `1500` matches the first condition.

An amount of `700` fails the first and matches the second.

An amount of `200` reaches `ELSE`.

This means **condition order matters**.

---

## 12.3 What if `ELSE` is omitted?

If no condition matches and there is no `ELSE`, the result is `NULL`.

Example:

```sql
SELECT
    CASE
        WHEN status = 'active' THEN 1
    END AS active_flag
FROM customers;
```

Inactive or unexpected statuses produce `NULL`.

That may be correct or may be an unintended missing value. Be deliberate.

---

## 12.4 NULL and CASE

A condition involving NULL can be `UNKNOWN`, so it may not match a `WHEN`.

For example:

```sql
CASE
    WHEN country = 'India' THEN 'IN'
    ELSE 'OTHER'
END
```

A `NULL` country does not make `country = 'India'` true. It therefore falls through to `ELSE`.

If you need to identify NULL explicitly:

```sql
CASE
    WHEN country IS NULL THEN 'UNKNOWN'
    WHEN country = 'India' THEN 'IN'
    ELSE 'OTHER'
END
```

---

## 12.5 Production use

Typical data-engineering uses include:

- classification,
- mapping status codes,
- building reporting categories,
- deriving quality flags,
- creating standardized labels.

Do not use `CASE` to hide an unclear business rule. The conditions should be reviewable.

---

# 13. Common String Functions

String behavior matters heavily in source-system normalization and data-quality logic.

## 13.1 `LOWER`

Converts text to lowercase.

```sql
SELECT
    LOWER(email) AS normalized_email
FROM customers;
```

Typical use:

- normalization,
- case-insensitive comparisons,
- producing stable keys when business rules define case-insensitive identity.

### NULL behavior

If `email` is `NULL`, the result is normally `NULL`.

```sql
SELECT LOWER(NULL) AS result;
```

The important lesson is that `LOWER` does not turn missing data into text.

---

## 13.2 `TRIM`

Removes surrounding whitespace.

```sql
SELECT
    TRIM(email) AS cleaned_email
FROM customers;
```

Useful for source cleanup.

Again, a `NULL` input remains `NULL`.

---

## 13.3 `SUBSTRING`

Extracts part of a string.

A common SQL form is:

```sql
SELECT
    SUBSTRING(email FROM 1 FOR 5) AS prefix
FROM customers;
```

Check target-engine syntax for dialect variations.

Use it when you intentionally need a portion of a string, such as a code prefix.

---

## 13.4 `CONCAT`

Concatenates values.

```sql
SELECT
    CONCAT(first_name, ' ', last_name) AS full_name
FROM customers;
```

One important reason `CONCAT` is useful is its handling of NULL arguments can differ from the `||` operator. Do not assume the two forms are interchangeable in every edge case.

---

## 13.5 `||`

PostgreSQL and DuckDB support `||` for string concatenation.

```sql
SELECT
    first_name || ' ' || last_name AS full_name
FROM customers;
```

### Important NULL behavior

In PostgreSQL-style concatenation:

```sql
SELECT
    'A' || NULL AS result;
```

produces `NULL`.

This means:

```sql
first_name || ' ' || last_name
```

can become `NULL` if one component is `NULL`.

If the business meaning is "build a name from whatever components exist", `CONCAT` may produce different behavior and may be more appropriate.

Do not silently replace missing names with an empty string unless that matches the business meaning.

---

## 13.6 Comparison summary

| Function/expression | Typical purpose | NULL input |
|---|---|---|
| `LOWER(x)` | case normalization | remains `NULL` |
| `TRIM(x)` | whitespace cleanup | remains `NULL` |
| `SUBSTRING(...)` | extract text segment | generally remains `NULL` |
| `CONCAT(...)` | concatenate values | engine-specific handling; verify |
| `x || y` | concatenate strings | PostgreSQL-style concatenation propagates NULL |

---

# 14. Common Numeric Functions

## 14.1 `ROUND`

Rounds a numeric value.

```sql
SELECT
    ROUND(amount, 2) AS amount_rounded
FROM orders;
```

This is useful for presentation or explicit calculation rules.

### Precision matters

Do not confuse:

```sql
ROUND(amount, 2)
```

with changing how the value is stored.

Rounding an expression can change the metric's meaning. For financial calculations, choose types and rounding rules deliberately.

---

## 14.2 `ABS`

Returns absolute value:

```sql
SELECT
    ABS(-42) AS distance_from_zero;
```

Data-engineering examples include:

```sql
SELECT
    order_id,
    ABS(source_total - target_total) AS reconciliation_difference
FROM reconciliation;
```

A `NULL` input produces `NULL`.

---

## 14.3 Arithmetic with NULL

Consider:

```sql
SELECT
    amount + tax AS total
FROM orders;
```

If:

```text
amount = 100
tax = NULL
```

the result is `NULL`.

SQL does not assume:

```text
100 + missing = 100
```

That assumption would be inventing information.

If zero is genuinely the business meaning, make that explicit:

```sql
SELECT
    amount + COALESCE(tax, 0) AS total
FROM orders;
```

But only do this when NULL really means "no tax" rather than "tax value is unknown."

---

# 15. Date and Time Fundamentals

Time filtering is one of the most important SQL skills for data engineers.

## 15.1 `CURRENT_DATE`

Returns the current date according to the engine/session context.

```sql
SELECT CURRENT_DATE;
```

Avoid assuming a production pipeline's "current date" is identical to a user's local date. Time zone semantics matter.

---

## 15.2 Date versus timestamp

A `DATE` represents a calendar date.

A timestamp represents a date and time.

For example:

```text
DATE
2025-03-01

TIMESTAMP
2025-03-01 14:35:12
```

When filtering event data, the distinction matters.

---

## 15.3 `DATE_TRUNC`

`DATE_TRUNC` truncates a temporal value to a chosen boundary.

```sql
SELECT
    DATE_TRUNC('month', created_at) AS month_start
FROM orders;
```

Example:

```text
2025-03-19 15:20:30
        ↓
2025-03-01 00:00:00
```

This is useful for reporting buckets.

---

## 15.4 `EXTRACT`

Extracts a date/time component.

```sql
SELECT
    EXTRACT(YEAR FROM created_at) AS year
FROM orders;
```

Other fields may include month, day, hour, and similar units depending on the engine.

Remember that extraction is a transformation. For filtering, a direct range predicate may be preferable to wrapping the filtered timestamp in a function.

---

## 15.5 Intervals

An interval represents a duration.

For example, conceptually:

```sql
SELECT
    TIMESTAMP '2025-03-01 00:00:00'
    + INTERVAL '1 day';
```

The result is the timestamp one day later.

Intervals are useful for:

- window boundaries,
- date arithmetic,
- retention calculations,
- time-based logic.

Exact interval syntax can vary by dialect.

---

# 16. NULL — The Core Concept

This is the most important semantic section in the chapter.

## 16.1 What is NULL?

`NULL` represents the absence of a known value.

Depending on the business context, it can mean:

- the source did not provide a value,
- the value is currently unknown,
- the concept does not apply.

Those meanings are related but are **not identical**.

---

## 16.2 NULL is not zero

```text
0
```

means a known numeric value of zero.

```text
NULL
```

means there is no known value.

These are not interchangeable.

---

## 16.3 NULL is not an empty string

```text
''
```

is a string with zero characters.

```text
NULL
```

is not a string value.

---

## 16.4 NULL is not FALSE

```text
FALSE
```

is a known boolean result.

```text
NULL
```

is missing/unknown and participates in three-valued logic.

---

## 16.5 Tiny example

```sql
CREATE TEMP TABLE customers_demo (
    customer_id INTEGER,
    email TEXT
);

INSERT INTO customers_demo (customer_id, email)
VALUES
    (1, 'a@example.com'),
    (2, NULL),
    (3, 'b@example.com');
```

Data:

| customer_id | email |
|---:|---|
| 1 | a@example.com |
| 2 | NULL |
| 3 | b@example.com |

Now:

```sql
SELECT *
FROM customers_demo
WHERE email = 'a@example.com';
```

returns customer 1.

But:

```sql
SELECT *
FROM customers_demo
WHERE email <> 'a@example.com';
```

returns customer 3, **not** customer 2.

Why?

For customer 2:

```text
NULL <> 'a@example.com'
```

is `UNKNOWN`.

`WHERE` keeps only `TRUE`.

---

# 17. Three-Valued Logic

SQL uses three logical states:

```text
TRUE
FALSE
UNKNOWN
```

This is called **three-valued logic**.

## 17.1 Why does SQL need UNKNOWN?

Suppose:

```text
country = NULL
```

and the query asks:

```sql
country = 'India'
```

The database cannot truthfully say:

```text
TRUE
```

because it does not know the country.

It also cannot truthfully say:

```text
FALSE
```

because it does not know whether the missing value would have been India.

Therefore:

```text
UNKNOWN
```

---

## 17.2 What happens to comparisons with NULL?

These are all `UNKNOWN`:

```sql
SELECT NULL = NULL;
SELECT NULL <> NULL;
SELECT NULL > 5;
SELECT NULL = 'x';
```

They are not `TRUE`.

The exact result display may be shown as a blank/NULL in client tools, but semantically the boolean result is unknown.

---

## 17.3 Why is `NULL = NULL` not TRUE?

Equality asks:

> "Are these two known values equal?"

But two missing values are not two known values that happen to be equal.

A useful mental model:

```text
5 = 5        → TRUE
5 = 7        → FALSE
NULL = 5     → UNKNOWN
NULL = NULL  → UNKNOWN
```

This is one of the most important SQL differences from ordinary two-valued boolean reasoning.

---

## 17.4 `IS NULL`

To ask whether a value is NULL, use:

```sql
SELECT *
FROM customers_demo
WHERE email IS NULL;
```

This returns customer 2.

Do not write:

```sql
WHERE email = NULL;
```

That comparison evaluates to `UNKNOWN`.

---

## 17.5 `IS NOT NULL`

To select known values:

```sql
SELECT *
FROM customers_demo
WHERE email IS NOT NULL;
```

This returns customers 1 and 3.

---

# 18. Truth Tables for AND, OR, and NOT

Use:

```text
T = TRUE
F = FALSE
U = UNKNOWN
```

## 18.1 `AND`

| A | B | A AND B |
|---|---|---|
| TRUE | TRUE | TRUE |
| TRUE | FALSE | FALSE |
| TRUE | UNKNOWN | UNKNOWN |
| FALSE | TRUE | FALSE |
| FALSE | FALSE | FALSE |
| FALSE | UNKNOWN | FALSE |
| UNKNOWN | TRUE | UNKNOWN |
| UNKNOWN | FALSE | FALSE |
| UNKNOWN | UNKNOWN | UNKNOWN |

The key reasoning rule:

> `FALSE AND anything` is `FALSE`.

Because one false requirement is enough to make the entire `AND` condition false.

---

## 18.2 `OR`

| A | B | A OR B |
|---|---|---|
| TRUE | TRUE | TRUE |
| TRUE | FALSE | TRUE |
| TRUE | UNKNOWN | TRUE |
| FALSE | TRUE | TRUE |
| FALSE | FALSE | FALSE |
| FALSE | UNKNOWN | UNKNOWN |
| UNKNOWN | TRUE | TRUE |
| UNKNOWN | FALSE | UNKNOWN |
| UNKNOWN | UNKNOWN | UNKNOWN |

The key reasoning rule:

> `TRUE OR anything` is `TRUE`.

---

## 18.3 `NOT`

| A | NOT A |
|---|---|
| TRUE | FALSE |
| FALSE | TRUE |
| UNKNOWN | UNKNOWN |

`NOT UNKNOWN` is still `UNKNOWN`.

---

## 18.4 Verify in PostgreSQL

You can verify the behavior directly:

```sql
SELECT
    TRUE AND NULL AS true_and_unknown,
    FALSE AND NULL AS false_and_unknown,
    TRUE OR NULL AS true_or_unknown,
    FALSE OR NULL AS false_or_unknown,
    NOT NULL AS not_unknown;
```

The results should correspond to:

```text
TRUE AND UNKNOWN   → UNKNOWN
FALSE AND UNKNOWN  → FALSE
TRUE OR UNKNOWN    → TRUE
FALSE OR UNKNOWN   → UNKNOWN
NOT UNKNOWN        → UNKNOWN
```

---

## 18.5 Why this matters in production

Consider:

```sql
WHERE is_active
  AND country <> 'India'
```

If `country` is NULL:

```text
country <> 'India' → UNKNOWN
TRUE AND UNKNOWN   → UNKNOWN
```

The row is removed.

This can look like a normal filtering decision when it is actually a NULL semantics issue.

---

# 19. WHERE and UNKNOWN

The operational rule is:

> **`WHERE` keeps only rows whose condition is `TRUE`.**

| Predicate result | Row kept? |
|---|---|
| TRUE | Yes |
| FALSE | No |
| UNKNOWN | No |

This is why NULL bugs are often silent.

Example:

```sql
SELECT *
FROM customers_demo
WHERE email <> 'a@example.com';
```

Customer 2 has:

```text
email = NULL
```

The predicate becomes:

```text
NULL <> 'a@example.com' → UNKNOWN
```

So the row is removed.

There is no SQL error.

---

## 19.1 Making intent explicit

If the business requirement is:

> "Customers whose email is not `a@example.com`, including customers whose email is missing."

Then write the rule explicitly:

```sql
SELECT *
FROM customers_demo
WHERE email <> 'a@example.com'
   OR email IS NULL;
```

This is not merely SQL syntax. It is business semantics.

---

# 20. COALESCE

`COALESCE` returns the first non-NULL expression.

```sql
COALESCE(value, fallback)
```

Example:

```sql
SELECT
    COALESCE(country, 'unknown') AS country
FROM customers;
```

If:

```text
country = 'India'
```

result:

```text
India
```

If:

```text
country = NULL
```

result:

```text
unknown
```

---

## 20.1 Left-to-right evaluation

`COALESCE` can take multiple values:

```sql
SELECT
    COALESCE(work_email, personal_email, 'missing') AS contact_email
FROM customers;
```

Conceptually:

```text
first non-NULL value wins
```

---

## 20.2 Common use

A classic example:

```sql
SELECT
    order_id,
    amount + COALESCE(tax, 0) AS total
FROM orders;
```

Use this only when the business meaning says:

> missing tax means zero tax.

Do **not** use:

```sql
COALESCE(missing_quality_score, 0)
```

just because zero is convenient.

You may be converting "unknown" into "known zero", which changes the meaning of the data.

---

## 20.3 COALESCE is not "remove NULLs"

This is a crucial distinction.

`COALESCE` changes a result.

Example:

```text
NULL → 0
```

The data is no longer semantically the same.

Use it when that transformation is intentional.

---

# 21. NULLIF

`NULLIF(a, b)` returns `NULL` when `a` and `b` are equal. Otherwise it returns `a`.

```sql
NULLIF(a, b)
```

A common data-engineering use is divide-by-zero protection:

```sql
SELECT
    revenue / NULLIF(order_count, 0) AS average_order_value
FROM daily_metrics;
```

If:

```text
order_count = 0
```

then:

```sql
NULLIF(order_count, 0)
```

becomes `NULL`, so the division produces `NULL` rather than attempting to divide by zero.

---

## 21.1 Why this is better than inventing zero

Suppose a day has:

```text
revenue = 0
order_count = 0
```

What is:

```text
revenue / order_count
```

There is no meaningful numeric rate.

Returning NULL can correctly communicate "undefined/not available" rather than inventing `0`.

---

# 22. IS DISTINCT FROM

Normal equality/inequality operators are NULL-sensitive.

PostgreSQL provides:

```sql
a IS DISTINCT FROM b
```

and:

```sql
a IS NOT DISTINCT FROM b
```

These are **NULL-safe comparisons**.

## 22.1 Why they exist

Compare:

```sql
a <> b
```

with:

```sql
a IS DISTINCT FROM b
```

When one side is NULL, `<>` produces `UNKNOWN`, but `IS DISTINCT FROM` returns a definite boolean.

---

## 22.2 Truth table

| A | B | `A IS DISTINCT FROM B` |
|---|---|---|
| 10 | 10 | FALSE |
| 10 | 20 | TRUE |
| 10 | NULL | TRUE |
| NULL | 10 | TRUE |
| NULL | NULL | FALSE |

And:

| A | B | `A IS NOT DISTINCT FROM B` |
|---|---|---|
| 10 | 10 | TRUE |
| 10 | 20 | FALSE |
| 10 | NULL | FALSE |
| NULL | 10 | FALSE |
| NULL | NULL | TRUE |

This makes `IS DISTINCT FROM` valuable when "both NULL" should count as "unchanged/equal".

---

## 22.3 Data-engineering example

Suppose a daily source snapshot should update a target only if a field changed.

This:

```sql
WHERE source.country <> target.country
```

fails to distinguish NULL transitions cleanly.

A NULL-safe comparison is:

```sql
WHERE source.country IS DISTINCT FROM target.country
```

It detects:

```text
India → Nepal        changed
India → NULL         changed
NULL → India         changed
NULL → NULL          unchanged
```

This is particularly useful in incremental data-change logic.

---

# 23. NULL Traps

## Trap 1 — `NOT IN` with NULL

Consider:

```sql
CREATE TEMP TABLE blocked_customers (
    customer_id INTEGER
);

INSERT INTO blocked_customers
VALUES
    (2),
    (NULL);
```

Now:

```sql
SELECT *
FROM customers_demo
WHERE customer_id NOT IN (
    SELECT customer_id
    FROM blocked_customers
);
```

To understand the problem, imagine `customer_id = 1`.

The condition is effectively:

```text
1 <> 2
AND
1 <> NULL
```

The first comparison is:

```text
TRUE
```

The second is:

```text
UNKNOWN
```

So:

```text
TRUE AND UNKNOWN
→ UNKNOWN
```

`WHERE` removes the row.

Because the subquery contains a NULL, the `NOT IN` predicate can therefore produce a result very different from the intended:

> "Return customers whose ID is not present in blocked_customers."

---

### Safer anti-membership pattern

Use `NOT EXISTS` when the intent is "no matching row exists":

```sql
SELECT c.*
FROM customers_demo AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM blocked_customers AS b
    WHERE b.customer_id = c.customer_id
);
```

Now the matching condition itself uses equality and the existence test answers the actual question:

> Is there a matching blocked customer?

For data-engineering work, understand **why** the two expressions have different NULL semantics.

---

## Trap 2 — `<>` excludes NULL

This query:

```sql
SELECT *
FROM customers
WHERE country <> 'India';
```

does not mean:

> "Every row except those known to be India."

It means:

> "Rows for which `country <> 'India'` is TRUE."

For NULL:

```text
NULL <> 'India'
→ UNKNOWN
```

Therefore NULL rows disappear.

If you need them included:

```sql
WHERE country <> 'India'
   OR country IS NULL;
```

---

## Trap 3 — String concatenation with NULL

```sql
SELECT
    first_name || ' ' || last_name AS full_name
FROM customers;
```

Suppose:

```text
first_name = 'Ada'
last_name  = NULL
```

The concatenation can result in:

```text
NULL
```

If you intentionally want a fallback:

```sql
SELECT
    CONCAT(first_name, ' ', last_name) AS full_name
FROM customers;
```

The exact behavior of concatenation functions/operators is dialect-specific, so test the target engine when missing strings matter.

---

## Trap 4 — Arithmetic with NULL

```sql
SELECT
    amount + tax AS total
FROM orders;
```

If:

```text
amount = 100
tax = NULL
```

result:

```text
NULL
```

If NULL semantically means zero:

```sql
SELECT
    amount + COALESCE(tax, 0) AS total
FROM orders;
```

If NULL means unknown, do not replace it blindly.

---

# 24. Sorting with ORDER BY

## 24.1 Ascending

```sql
SELECT
    order_id,
    amount
FROM orders
ORDER BY amount ASC;
```

`ASC` is the default direction in many SQL implementations.

---

## 24.2 Descending

```sql
SELECT
    order_id,
    amount
FROM orders
ORDER BY amount DESC;
```

---

## 24.3 Multiple sort columns

```sql
SELECT
    order_id,
    created_at,
    amount
FROM orders
ORDER BY
    created_at DESC,
    amount DESC;
```

The first sort key is considered first. The second is used to break ties.

---

## 24.4 Sorting by an expression

```sql
SELECT
    order_id,
    amount
FROM orders
ORDER BY
    amount * 1.18 DESC;
```

---

## 24.5 Sorting by output alias

A SELECT alias is generally available to `ORDER BY` in SQL dialects because `ORDER BY` is logically later than `SELECT` in the roadmap model.

Example:

```sql
SELECT
    amount * 1.18 AS gross_amount
FROM orders
ORDER BY gross_amount DESC;
```

This contrasts with `WHERE`, which is logically earlier.

---

# 25. NULL Sorting

NULL ordering is an area where dialect defaults matter.

You can make your intent explicit:

```sql
ORDER BY country ASC NULLS LAST;
```

or:

```sql
ORDER BY country ASC NULLS FIRST;
```

This is preferable when the placement of missing values matters to the consumer.

## 25.1 PostgreSQL defaults

In PostgreSQL:

- ascending order defaults to `NULLS LAST`
- descending order defaults to `NULLS FIRST`

Therefore:

```sql
ORDER BY country ASC;
```

and:

```sql
ORDER BY country ASC NULLS LAST;
```

express the same NULL placement in PostgreSQL.

Do not generalize PostgreSQL's defaults to every SQL engine.

## 25.2 DuckDB

DuckDB also supports explicit `NULLS FIRST` / `NULLS LAST`. Verify its current default ordering behavior rather than relying on assumptions when cross-engine reproducibility matters.

### Engineering rule

When the placement of NULLs is part of the requirement, write it explicitly:

```sql
ORDER BY country ASC NULLS LAST;
```

---

# 26. Deterministic Ordering

This is a critical production concept.

Consider:

```sql
SELECT
    order_id,
    created_at
FROM orders
ORDER BY created_at DESC;
```

Suppose three rows have exactly the same timestamp:

```text
order_id  created_at
101       2025-03-01 12:00:00
102       2025-03-01 12:00:00
103       2025-03-01 12:00:00
```

`ORDER BY created_at DESC` does not define how 101, 102, and 103 should be ordered relative to each other.

If you need repeatability, add a tie-breaker:

```sql
SELECT
    order_id,
    created_at
FROM orders
ORDER BY
    created_at DESC,
    order_id DESC;
```

Now the ordering is deterministic **provided `order_id` is unique**.

---

## 26.1 Why deterministic ordering matters

It affects:

- pagination,
- exports,
- tests,
- repeatability,
- reproducibility,
- "latest record" decisions,
- later window-function logic.

For data engineering, deterministic ordering is an explicit requirement, not a cosmetic preference.

---

## 26.2 A common mistake

This:

```sql
ORDER BY created_at
LIMIT 100;
```

does not mean:

> "Give me the same 100 rows every time."

It means:

> "Return up to 100 rows that satisfy the query, in created_at order, with ties not fully specified."

Use a unique or effectively unique tie-breaker when row identity matters.

---

# 27. LIMIT, OFFSET, and FETCH FIRST

## 27.1 LIMIT

```sql
SELECT *
FROM orders
ORDER BY order_id
LIMIT 10;
```

Returns at most 10 rows.

---

## 27.2 OFFSET

```sql
SELECT *
FROM orders
ORDER BY order_id
LIMIT 10
OFFSET 100;
```

Conceptually:

1. identify the ordered result,
2. skip 100 rows,
3. return the next 10.

---

## 27.3 FETCH FIRST

Standard-style syntax:

```sql
SELECT *
FROM orders
ORDER BY order_id
FETCH FIRST 10 ROWS ONLY;
```

This communicates the same general idea as:

```sql
LIMIT 10
```

Dialect support and syntax details should be verified for the target engine.

---

## 27.4 LIMIT without ORDER BY

Avoid:

```sql
SELECT *
FROM orders
LIMIT 10;
```

when you mean "the first 10 by some business definition."

There is no business definition of "first" without an ordering.

---

## 27.5 Why large OFFSET values become expensive

Consider:

```sql
LIMIT 100
OFFSET 1000000;
```

The database must generally account for a large preceding portion of the ordered result before it can return the requested page.

This makes large offsets increasingly unattractive for extraction jobs.

The solution is often **keyset / seek pagination**.

---

# 28. Type Casting

Explicit casting makes intent clear.

## 28.1 Standard form

```sql
CAST(x AS type)
```

Example:

```sql
SELECT
    CAST(customer_id_text AS INTEGER)
FROM raw_customers;
```

---

## 28.2 PostgreSQL shortcut

PostgreSQL supports:

```sql
x::type
```

Example:

```sql
SELECT
    customer_id_text::INTEGER
FROM raw_customers;
```

This is PostgreSQL-specific syntax and should not be presented as universal SQL.

---

## 28.3 Useful examples

Text to integer:

```sql
SELECT CAST('42' AS INTEGER);
```

Text to date:

```sql
SELECT CAST('2025-03-01' AS DATE);
```

Integer to numeric:

```sql
SELECT CAST(5 AS NUMERIC) / 2;
```

---

## 28.4 Why explicit casts matter

Explicit casts help with:

- correctness,
- comparison behavior,
- metric calculations,
- schema boundaries,
- avoiding ambiguous implicit conversions.

A cast can also affect performance if it is applied to a column used in a filter and prevents the query from matching the stored type cleanly.

Do not cast blindly. Cast when the semantic conversion is intentional.

---

# 29. Integer Division

A classic PostgreSQL example:

```sql
SELECT 5 / 2;
```

With integer operands, PostgreSQL performs integer division, producing:

```text
2
```

If you need a decimal result:

```sql
SELECT 5::numeric / 2;
```

which produces:

```text
2.5
```

or:

```sql
SELECT CAST(5 AS NUMERIC) / 2;
```

---

## 29.1 Why this matters for data engineering

Metrics such as:

```text
conversion rate
error rate
utilization
share of total
growth rate
```

are often ratios.

This can be wrong:

```sql
SELECT
    successful_orders / total_orders AS conversion_rate
FROM metrics;
```

when both columns are integers.

A safer form is:

```sql
SELECT
    successful_orders::numeric
    / NULLIF(total_orders, 0) AS conversion_rate
FROM metrics;
```

This addresses two problems:

1. integer division,
2. division by zero.

`NULLIF` is used because a zero denominator usually means the rate is undefined.

---

# 30. Timestamp vs Timestamptz

PostgreSQL distinguishes:

```text
timestamp
timestamptz
```

The conceptual difference is important for event data.

## 30.1 `timestamp`

A `timestamp without time zone` represents a date and clock time without an associated absolute time-zone interpretation.

Example:

```text
2025-03-01 14:30:00
```

It does not, by itself, establish whether that means:

```text
UTC
India Standard Time
America/New_York
```

---

## 30.2 `timestamptz`

PostgreSQL's `timestamp with time zone` (`timestamptz`) represents an **absolute instant**.

PostgreSQL does not store a time-zone name with each `timestamptz` value. It stores the instant and displays it according to the session's time-zone setting.

This distinction is important.

For example, the same instant can display differently in different session time zones.

---

## 30.3 Why event pipelines care

Suppose an event happens at:

```text
2025-03-01 18:30:00 UTC
```

A user in India might see:

```text
2025-03-02 00:00:00
```

If you are filtering events by business-day boundaries, the time zone used to define those boundaries matters.

A date boundary in:

```text
Asia/Kolkata
```

is not necessarily the same UTC boundary.

---

## 30.4 Production rule

For event timestamps, decide explicitly:

- what represents the source event instant,
- what time zone defines business-day boundaries,
- how timestamps are stored,
- how timestamps are displayed,
- what time zone the extraction job uses.

Do not assume the server's local time zone matches the business requirement.

---

# 31. Half-Open Time Ranges

For timestamp filtering, use:

```sql
WHERE ts >= start
  AND ts < end
```

This defines the mathematical interval:

```text
[start, end)
```

The start is included.

The end is excluded.

---

## 31.1 Canonical monthly filter

```sql
SELECT *
FROM orders
WHERE created_at >= TIMESTAMP '2025-03-01 00:00:00'
  AND created_at <  TIMESTAMP '2025-04-01 00:00:00';
```

This includes every timestamp from the start of March up to, but not including, the start of April.

---

## 31.2 Timeline

```text
March window

start                                      end
  |                                         |
  ▼                                         ▼
  [=========================================)
  included                                  excluded
2025-03-01 00:00:00                 2025-04-01 00:00:00
```

---

## 31.3 Why this is safer

### Exact boundaries

An event exactly at:

```text
2025-04-01 00:00:00
```

belongs to April, not March.

### No overlapping adjacent windows

March:

```sql
ts >= '2025-03-01'
AND ts <  '2025-04-01'
```

April:

```sql
ts >= '2025-04-01'
AND ts <  '2025-05-01'
```

There is no overlap and no gap.

### No maximum-precision guessing

You do not need to invent:

```text
23:59:59
23:59:59.999
23:59:59.999999
```

### Incremental extraction

The pattern works naturally for daily/hourly/monthly extraction windows.

### Partition pruning

A direct range predicate can also provide the optimizer/storage layer a clean range condition to use for partition pruning where supported.

---

## 31.4 Why timestamp BETWEEN is dangerous

A naïve monthly filter:

```sql
WHERE created_at
      BETWEEN TIMESTAMP '2025-03-01 00:00:00'
          AND TIMESTAMP '2025-03-31 23:59:59'
```

depends on an assumed precision and misses values after that exact instant, such as:

```text
2025-03-31 23:59:59.500000
```

Even an attempt to specify a very precise end-of-day timestamp is unnecessarily fragile.

Use the next boundary instead.

---

## 31.5 Half-open ranges across time zones

If business requirements define a local calendar day, derive the local start and next local boundary deliberately, then compare consistently against the representation used by the source.

The important engineering principle is:

> **The meaning of the boundary matters as much as the SQL syntax.**

---

# 32. Sargable Predicates

A **sargable predicate** is a filter written in a form that gives the database optimizer a good opportunity to use an index or another efficient access path.

"Sargable" does **not** mean:

> "An index is guaranteed to be used."

The optimizer can still choose a sequential scan or another strategy if it estimates that strategy is cheaper.

---

## 32.1 A non-sargable timestamp example

Problematic:

```sql
SELECT *
FROM orders
WHERE DATE(created_at) = DATE '2025-03-01';
```

The expression applies a function to the column.

Conceptually, the database is being asked to transform each candidate timestamp into a date before comparing it.

If `created_at` is indexed, that form can make ordinary range-based index access less straightforward.

Rewrite as:

```sql
SELECT *
FROM orders
WHERE created_at >= TIMESTAMP '2025-03-01 00:00:00'
  AND created_at <  TIMESTAMP '2025-03-02 00:00:00';
```

Now the column is compared directly against bounds.

---

## 32.2 Numeric example

Potentially problematic:

```sql
WHERE amount * 1.1 > 100
```

A direct rewrite is:

```sql
WHERE amount > 100 / 1.1
```

provided that:

- the algebra is valid,
- numeric precision is handled appropriately,
- the business rule is really equivalent.

The principle is:

> Move the transformation away from the stored column when you can preserve the same meaning.

---

## 32.3 Sargable does not mean "always faster"

Even a sargable predicate may result in:

```text
Sequential Scan
```

if a large percentage of the table matches.

For example, if:

```sql
WHERE status = 'active'
```

matches 95% of a table, scanning the table may be cheaper than using an index and visiting most rows anyway.

The planner decides.

---

## 32.4 Other reasons an index may not be used

Even when a predicate looks sargable:

- low selectivity,
- stale statistics,
- type mismatches,
- estimated I/O cost,
- table size,
- competing indexes,
- storage characteristics

can affect the final plan.

Detailed index and plan analysis belongs to Topic 08.

---

## 32.5 Partition pruning

Sargability is also relevant to partitioned data.

A filter such as:

```sql
WHERE created_at >= TIMESTAMP '2025-03-01'
  AND created_at <  TIMESTAMP '2025-04-01'
```

gives the system clear boundaries.

A transformed expression such as:

```sql
WHERE DATE(created_at) = DATE '2025-03-01'
```

may make partition pruning harder depending on the engine and layout.

Again, these are opportunities for the optimizer, not absolute promises.

---

# 33. Keyset / Seek Pagination

For large result sets, keyset pagination is often preferable to large `OFFSET`s.

## 33.1 OFFSET pagination

```sql
SELECT
    order_id,
    created_at,
    amount
FROM orders
ORDER BY created_at, order_id
LIMIT 100
OFFSET 100000;
```

As the offset grows, the database generally has to account for more preceding rows.

---

## 33.2 Keyset pagination

Suppose the previous page ended at:

```text
last_created_at = 2025-03-10 12:00:00
last_order_id   = 5000
```

Then:

```sql
SELECT
    order_id,
    created_at,
    amount
FROM orders
WHERE (created_at, order_id)
      > (:last_created_at, :last_order_id)
ORDER BY
    created_at,
    order_id
LIMIT 100;
```

The previous row becomes the cursor.

---

## 33.3 How the cursor works

Conceptually:

```text
page 1
───────────────────────────────>
last row = (time=A, id=100)

page 2
WHERE (time, id) > (A, 100)
───────────────────────────────>
```

The database starts from the position after the cursor rather than asking it to skip a huge number of rows.

---

## 33.4 Why two columns?

This is better:

```sql
ORDER BY created_at, order_id
```

than:

```sql
ORDER BY created_at
```

because timestamps can tie.

The pair:

```text
(created_at, order_id)
```

creates a deterministic traversal when `order_id` is unique.

---

## 33.5 Stability under concurrent inserts

Keyset pagination can be more stable than offset pagination when new rows are inserted between requests.

With a deterministic key:

```text
(created_at, order_id)
```

the cursor describes an actual position in the ordered key space.

Offset pagination describes a row number. If rows are inserted before that row number, later pages can shift.

This does not make keyset pagination immune to all concurrency concerns, but it avoids a major class of offset-shifting behavior.

---

## 33.6 When OFFSET is still fine

Do not oversell keyset pagination.

`OFFSET` is perfectly reasonable when:

- the result set is small,
- offsets are small,
- users need arbitrary page jumps,
- a simple administrative UI is involved,
- the performance requirement is modest.

Keyset pagination becomes especially valuable for:

- large exports,
- extraction jobs,
- APIs traversing many pages,
- high-volume operational tables.

---

## 33.7 Descending pagination

If the ordering is descending:

```sql
ORDER BY created_at DESC, order_id DESC
```

the cursor comparison must also be designed for that direction.

For example:

```sql
WHERE (created_at, order_id)
      < (:last_created_at, :last_order_id)
ORDER BY
    created_at DESC,
    order_id DESC
LIMIT 100;
```

The important principle is consistency:

> The cursor predicate and the `ORDER BY` must describe the same ordered key space.

---

# 34. PostgreSQL vs DuckDB

SQL is standardized, but practical SQL is dialect-specific.

Use the following classification:

```text
STANDARD SQL
POSTGRESQL-SPECIFIC
DUCKDB-SPECIFIC
```

Verify target-engine documentation whenever version-specific behavior matters.

| Topic | PostgreSQL | DuckDB | Engineering note |
|---|---|---|---|
| `SELECT`, `FROM`, `WHERE`, `ORDER BY` | Supported | Supported | Standard concepts |
| `LIMIT` | Supported | Supported | Common dialect syntax |
| `FETCH FIRST` | Supported | Supported | Standard-style syntax; verify details |
| `ILIKE` | Supported | Supported | Not universal SQL |
| `::type` | Supported | Supported in DuckDB for PostgreSQL-style casting | Treat cast shorthand as dialect syntax, not universal SQL |
| Integer division | `5 / 2` gives integer result for integer operands | DuckDB's numeric typing/division rules should be verified for the exact operand types/version | Cast deliberately for ratios |
| `NULLS FIRST/LAST` | Supported | Supported | Use explicitly when NULL placement matters |
| `timestamp` / `timestamptz` | Distinct PostgreSQL concepts; `timestamptz` represents an absolute instant | DuckDB has timestamp types with timezone support, but semantics and implementation details differ | Do not assume identical behavior |
| `DATE_TRUNC` | Supported | Supported | Syntax is similar |
| `EXTRACT` | Supported | Supported | Syntax is similar |
| `||` | Supported for concatenation | Supported | NULL behavior should be tested for target engine |
| `CASE` | Supported | Supported | Core SQL feature |
| `COALESCE` | Supported | Supported | Standard SQL |
| `NULLIF` | Supported | Supported | Standard SQL |
| `IS DISTINCT FROM` | Supported | Supported | Useful NULL-safe comparison |
| Keyset pagination | Supported | Supported | Strategy, not a special engine feature |

### Dialect rule

Never think:

> "I know SQL, so every engine will accept the same syntax."

Instead think:

> "I know the semantic idea, then I verify the dialect implementation."

This is especially important when moving between PostgreSQL, DuckDB, warehouses, and Spark SQL.

---

# 35. Production Patterns

## 35.1 Pattern — Daily event extraction

### Requirement

Extract all events for March 1, 2025.

### Query

```sql
SELECT
    event_id,
    user_id,
    event_type,
    event_at
FROM events
WHERE event_at >= TIMESTAMP '2025-03-01 00:00:00'
  AND event_at <  TIMESTAMP '2025-03-02 00:00:00'
ORDER BY event_at, event_id;
```

### Why it is correct

- Explicit columns.
- Half-open time interval.
- Deterministic ordering with `event_id` as a tie-breaker.

### Edge cases

- Events exactly at midnight belong to the correct day.
- Events with the same timestamp remain deterministically ordered.
- Time-zone semantics must match the business definition of the day.

### Performance consideration

The timestamp filter is written as direct bounds, giving the optimizer a clear opportunity for efficient access or partition pruning.

---

## 35.2 Pattern — Nullable dimension attribute

### Requirement

Find customers who are not from India, while keeping customers with unknown country.

```sql
SELECT
    customer_id,
    country
FROM customers
WHERE country <> 'India'
   OR country IS NULL;
```

### Why it is correct

It explicitly defines the desired treatment of NULL.

### Edge case

A NULL country is not automatically a non-India country. The query intentionally chooses to include unknowns.

---

## 35.3 Pattern — Deterministic extract

```sql
SELECT
    order_id,
    created_at,
    amount
FROM orders
WHERE created_at >= TIMESTAMP '2025-03-01'
  AND created_at <  TIMESTAMP '2025-04-01'
ORDER BY created_at, order_id;
```

This is preferable to:

```sql
ORDER BY created_at;
```

when downstream processing depends on reproducibility.

---

## 35.4 Pattern — Large export with keyset pagination

```sql
SELECT
    order_id,
    created_at,
    amount
FROM orders
WHERE (created_at, order_id)
      > (:last_created_at, :last_order_id)
ORDER BY
    created_at,
    order_id
LIMIT 1000;
```

This is a common pattern for extracting a large ordered stream of records without repeatedly paying the cost of large offsets.

---

## 35.5 Pattern — Ratio metric

```sql
SELECT
    successful_orders::numeric
    / NULLIF(total_orders, 0) AS success_rate
FROM daily_metrics;
```

This intentionally handles:

- integer division,
- zero denominator.

---

# 36. Common SQL Mistakes

Use this troubleshooting table as a quick reference.

| Wrong query/pattern | Why it is wrong | Correct pattern | Lesson |
|---|---|---|---|
| `WHERE email = NULL` | equality with NULL becomes UNKNOWN | `WHERE email IS NULL` | NULL requires NULL-aware predicates |
| `SELECT ... LIMIT 10` without `ORDER BY` | "first" rows are undefined | add meaningful `ORDER BY` | Ordering is not implicit |
| `WHERE ts BETWEEN start AND end` for a time window | inclusive upper bound causes boundary/precision problems | `ts >= start AND ts < end` | Prefer half-open intervals |
| `WHERE country <> 'India'` when NULLs should be included | NULL comparison becomes UNKNOWN | add `OR country IS NULL` | Define NULL semantics explicitly |
| `NOT IN (subquery)` with nullable result | NULL can turn the predicate UNKNOWN | `NOT EXISTS` for anti-membership | Understand three-valued logic |
| `COALESCE(x, 0)` everywhere | converts unknown into a known zero | use only when semantics support it | NULL replacement changes meaning |
| `amount + tax` with nullable tax | NULL propagates | use `COALESCE` only if NULL means zero | Missing is not automatically zero |
| `first_name || ' ' || last_name` | NULL can propagate | choose concatenation semantics deliberately | Test NULL behavior |
| `ORDER BY created_at` alone | ties are unresolved | add unique tie-breaker | Deterministic results matter |
| `SELECT *` in stable production interfaces | schema changes silently change output | explicit columns | Output shape is a contract |
| `OFFSET 1000000` for extraction | large offsets become costly | keyset pagination | Use an ordered cursor |
| `WHERE DATE(created_at) = ...` | transformation around column can hurt access-path optimization | direct range predicate | Prefer sargable filters |
| `5 / 2` for a percentage | integer division may truncate | cast one operand | Metric semantics depend on types |
| Treating PostgreSQL syntax as universal | dialects differ | label and verify dialect-specific syntax | SQL is standardized but implementations vary |
| Assuming logical order is physical order | optimizer can reorder operations | separate semantics from execution | Learn both mental models |

---

# 37. Debugging SQL

Use a systematic process instead of randomly changing clauses.

## 37.1 Debugging loop

1. **State the input grain.**
2. **State the expected output.**
3. **Inspect a tiny sample.**
4. **Check NULL counts.**
5. **Check duplicate values where uniqueness is assumed.**
6. **Check timestamp boundaries.**
7. **Check ordering and ties.**
8. **Simplify the query.**
9. **Test one condition at a time.**
10. **Compare expected and actual row counts.**

---

## 37.2 Example — unexpected row loss

Suppose:

```sql
SELECT *
FROM customers
WHERE country <> 'India';
```

returns fewer rows than expected.

Debug:

```sql
SELECT
    COUNT(*) AS total_rows,
    COUNT(country) AS non_null_country_rows
FROM customers;
```

Then:

```sql
SELECT *
FROM customers
WHERE country IS NULL;
```

You may discover that many rows are NULL.

The issue is not that SQL "lost" those rows.

The predicate evaluated to `UNKNOWN`.

---

## 37.3 Example — unexpected monthly count

Suppose March counts look too low.

First inspect the boundary:

```sql
SELECT
    MIN(created_at),
    MAX(created_at)
FROM orders
WHERE created_at >= TIMESTAMP '2025-03-01'
  AND created_at <  TIMESTAMP '2025-04-01';
```

Then deliberately test boundary rows:

```sql
SELECT *
FROM orders
WHERE created_at >= TIMESTAMP '2025-03-31 23:59:59'
  AND created_at <  TIMESTAMP '2025-04-01 00:00:01'
ORDER BY created_at;
```

This often reveals precision assumptions.

---

## 37.4 Example — unstable pages

If page 2 occasionally contains duplicate or missing records, inspect:

```sql
ORDER BY created_at
```

The likely issue is unresolved ties.

Change to:

```sql
ORDER BY created_at, order_id
```

and make the pagination condition use the same key.

---

# 38. SQL Testing Mindset

Treat SQL like production code.

A useful assertion query returns **zero rows when correct**.

## 38.1 Assertion — unexpected NULL primary identifier

```sql
SELECT *
FROM customers
WHERE customer_id IS NULL;
```

Expected:

```text
0 rows
```

---

## 38.2 Assertion — duplicate customer keys

```sql
SELECT
    customer_id,
    COUNT(*) AS row_count
FROM customers
GROUP BY customer_id
HAVING COUNT(*) > 1;
```

Expected:

```text
0 rows
```

---

## 38.3 Assertion — invalid time ranges

```sql
SELECT *
FROM events
WHERE end_at < start_at;
```

Expected:

```text
0 rows
```

---

## 38.4 Assertion — NULL country policy

Suppose your requirement says country must be known:

```sql
SELECT *
FROM customers
WHERE country IS NULL;
```

Expected:

```text
0 rows
```

If the requirement allows NULL, then this should not be a failing test. The assertion must encode the actual business rule.

---

## 38.5 Tiny-table verification

Before using millions of rows, create a tiny test dataset:

```sql
CREATE TEMP TABLE tiny_orders (
    order_id INTEGER,
    created_at TIMESTAMP,
    amount INTEGER
);

INSERT INTO tiny_orders
VALUES
    (1, '2025-03-01 00:00:00', 100),
    (2, '2025-03-31 23:59:59', 200),
    (3, '2025-03-31 23:59:59.500000', 300),
    (4, '2025-04-01 00:00:00', 400);
```

Now verify:

```sql
SELECT *
FROM tiny_orders
WHERE created_at >= TIMESTAMP '2025-03-01 00:00:00'
  AND created_at <  TIMESTAMP '2025-04-01 00:00:00'
ORDER BY created_at, order_id;
```

You can compute the expected answer by hand before executing the query.

This is often much more informative than debugging a 10-million-row result.

---

# 39. Hands-On Exercises

The following exercises follow the Module 2.6 roadmap and progressively move from semantics to production usage.

---

## Exercise 1 — Logical execution order

### Objective

Learn to reason about what each clause can see.

### Setup

Use a table:

```sql
CREATE TEMP TABLE orders_e1 (
    order_id INTEGER,
    customer_id INTEGER,
    amount NUMERIC,
    created_at TIMESTAMP
);

INSERT INTO orders_e1 VALUES
    (1, 10, 100, '2025-03-01 10:00:00'),
    (2, 10, 200, '2025-03-01 11:00:00'),
    (3, 20, 50,  '2025-03-02 10:00:00');
```

### Task

For each of 10 queries, write the logical execution order next to the clauses before running it.

Include examples using:

- `FROM`
- `WHERE`
- `GROUP BY`
- `HAVING`
- window function
- `SELECT`
- `DISTINCT`
- `ORDER BY`
- `LIMIT`

### Expected reasoning

For every query answer:

```text
What rows exist before this stage?
What columns/aliases can this stage see?
What does it output?
```

### Solution idea

Use:

```text
FROM → WHERE → GROUP BY → HAVING → windows → SELECT → DISTINCT → ORDER BY → LIMIT
```

### Edge cases

Include a query that attempts to use a SELECT alias in `WHERE` and explain why it is invalid in the normal logical model.

---

## Exercise 2 — Customers not from India

### Objective

Compare three ways of expressing "not India".

### Setup

```sql
CREATE TEMP TABLE customers_e2 (
    customer_id INTEGER,
    country TEXT
);

INSERT INTO customers_e2 VALUES
    (1, 'India'),
    (2, 'Nepal'),
    (3, 'Bangladesh'),
    (4, NULL);
```

### Task

Write:

```sql
country <> 'India'
```

then:

```sql
country NOT IN ('India')
```

then:

```sql
country IS DISTINCT FROM 'India'
```

### Expected reasoning

Predict the row count before running each query.

### Solution

```sql
SELECT *
FROM customers_e2
WHERE country <> 'India';
```

and:

```sql
SELECT *
FROM customers_e2
WHERE country NOT IN ('India');
```

and:

```sql
SELECT *
FROM customers_e2
WHERE country IS DISTINCT FROM 'India';
```

The first two exclude NULL because the comparison becomes UNKNOWN.

The third treats NULL as distinct from the known value.

### Edge case

Ask:

> Do I want NULL to mean "not India", "unknown", or "invalid"?

There is no universally correct answer. The business semantics determine the query.

---

## Exercise 3 — `NOT IN` + NULL

### Objective

Reproduce and understand the classic NULL trap.

### Setup

```sql
CREATE TEMP TABLE customers_e3 (
    customer_id INTEGER
);

INSERT INTO customers_e3 VALUES
    (1),
    (2),
    (3);

CREATE TEMP TABLE blocked_e3 (
    customer_id INTEGER
);

INSERT INTO blocked_e3 VALUES
    (2),
    (NULL);
```

### Task

Run:

```sql
SELECT *
FROM customers_e3
WHERE customer_id NOT IN (
    SELECT customer_id
    FROM blocked_e3
);
```

Then run:

```sql
SELECT *
FROM customers_e3 AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM blocked_e3 AS b
    WHERE b.customer_id = c.customer_id
);
```

### Expected reasoning

Explain the result using:

```text
TRUE
FALSE
UNKNOWN
```

### Edge cases

Remove the NULL from `blocked_e3` and compare the two results again.

---

## Exercise 4 — Timestamp boundaries

### Objective

Understand why half-open ranges are safer.

### Setup

Use:

```sql
CREATE TEMP TABLE orders_e4 (
    order_id INTEGER,
    created_at TIMESTAMP
);

INSERT INTO orders_e4 VALUES
    (1, '2025-03-01 00:00:00'),
    (2, '2025-03-31 23:59:59'),
    (3, '2025-03-31 23:59:59.500000'),
    (4, '2025-04-01 00:00:00');
```

### Task

Compare:

```sql
WHERE created_at BETWEEN
      TIMESTAMP '2025-03-01 00:00:00'
  AND TIMESTAMP '2025-03-31 23:59:59'
```

against:

```sql
WHERE created_at >= TIMESTAMP '2025-03-01 00:00:00'
  AND created_at <  TIMESTAMP '2025-04-01 00:00:00'
```

### Expected reasoning

Identify exactly which order IDs appear in each result.

### Edge case

Explain why using a "last possible timestamp" is fragile compared with specifying the next boundary.

---

## Exercise 5 — Keyset pagination

### Objective

Implement deterministic pagination.

### Setup

Create a table with repeated timestamps:

```sql
CREATE TEMP TABLE orders_e5 (
    order_id INTEGER,
    created_at TIMESTAMP
);

INSERT INTO orders_e5 VALUES
    (1, '2025-03-01 10:00:00'),
    (2, '2025-03-01 10:00:00'),
    (3, '2025-03-01 10:00:00'),
    (4, '2025-03-01 11:00:00'),
    (5, '2025-03-01 12:00:00');
```

### Task

Implement pages using:

```text
(created_at, order_id)
```

First page:

```sql
SELECT *
FROM orders_e5
ORDER BY created_at, order_id
LIMIT 2;
```

Second page should use the last row from page 1 as the cursor.

### Solution

If page 1 ends at:

```text
('2025-03-01 10:00:00', 2)
```

then:

```sql
SELECT *
FROM orders_e5
WHERE (created_at, order_id)
      > (TIMESTAMP '2025-03-01 10:00:00', 2)
ORDER BY created_at, order_id
LIMIT 2;
```

### Edge case

Explain why `created_at` alone is not enough when timestamps tie.

---

## Exercise 6 — Truth-table verification

### Objective

Verify three-valued logic rather than merely memorizing it.

### Task

Run:

```sql
SELECT TRUE AND NULL;
SELECT FALSE AND NULL;
SELECT TRUE OR NULL;
SELECT FALSE OR NULL;
SELECT NOT NULL;
```

### Expected reasoning

Map each result to:

```text
TRUE
FALSE
UNKNOWN
```

### Edge cases

Add combinations using all values:

```text
TRUE
FALSE
NULL
```

for both sides of `AND` and `OR`.

---

## Exercise 7 — NULL-safe comparisons

### Objective

Compare normal inequality with NULL-safe distinctness.

### Task

Build a result table containing:

```text
10 vs 10
10 vs 20
10 vs NULL
NULL vs 10
NULL vs NULL
```

Evaluate both:

```sql
a <> b
```

and:

```sql
a IS DISTINCT FROM b
```

### Expected reasoning

Explain why the first can produce UNKNOWN while the second always returns TRUE/FALSE.

---

## Exercise 8 — Sargability

### Objective

Rewrite predicates that transform the filtered column.

### Task

Rewrite:

```sql
WHERE DATE(created_at) = DATE '2025-03-01'
```

and:

```sql
WHERE amount * 1.1 > 100
```

### Solution

Timestamp:

```sql
WHERE created_at >= TIMESTAMP '2025-03-01 00:00:00'
  AND created_at <  TIMESTAMP '2025-03-02 00:00:00'
```

Numeric:

```sql
WHERE amount > 100 / 1.1
```

provided the rewritten predicate is mathematically and numerically equivalent for the intended data type.

### Edge case

Explain why a sargable predicate does not guarantee index usage.

---

## Exercise 9 — Deterministic ordering

### Objective

Prove why a tie-breaker matters.

### Task

Create ten rows where five rows share the same timestamp.

Run:

```sql
ORDER BY created_at
LIMIT 5;
```

Then:

```sql
ORDER BY created_at, order_id
LIMIT 5;
```

Repeat enough times or examine the plan/result behavior to reason about unresolved ties.

### Expected reasoning

The first ordering does not fully define the relative order of equal timestamps.

---

## Exercise 10 — Production extraction

### Objective

Combine the major concepts.

### Requirement

Design an extract for one day's events with:

- half-open time boundaries,
- deterministic ordering,
- keyset pagination,
- explicit columns.

### Example

```sql
SELECT
    event_id,
    user_id,
    event_type,
    event_at
FROM events
WHERE event_at >= :day_start
  AND event_at <  :next_day_start
  AND (event_at, event_id)
      > (:last_event_at, :last_event_id)
ORDER BY
    event_at,
    event_id
LIMIT 1000;
```

### Edge cases

Explain:

- What happens when there are no rows?
- What if two events have the same timestamp?
- What if `event_id` is not unique?
- What time zone defines `:day_start`?
- What happens if the cursor belongs to a row that was deleted?

---

# 40. Mini Debugging Scenarios

Diagnose each before looking at the solution.

---

## Scenario 1 — `email = NULL`

Broken SQL:

```sql
SELECT *
FROM customers
WHERE email = NULL;
```

### Root cause

`NULL` is not compared using normal equality.

```text
email = NULL
→ UNKNOWN
```

### Corrected query

```sql
SELECT *
FROM customers
WHERE email IS NULL;
```

### Lesson

Use `IS NULL` for NULL testing.

---

## Scenario 2 — Nullable subquery with `NOT IN`

Broken SQL:

```sql
SELECT *
FROM customers
WHERE customer_id NOT IN (
    SELECT customer_id
    FROM blocked_customers
);
```

### Root cause

A NULL in the subquery can make the outer `NOT IN` predicate evaluate to UNKNOWN for candidates that do not match known IDs.

### Corrected query

```sql
SELECT c.*
FROM customers AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM blocked_customers AS b
    WHERE b.customer_id = c.customer_id
);
```

### Lesson

For anti-membership, reason from the business question: "Does a matching row exist?"

---

## Scenario 3 — Timestamp BETWEEN

Broken:

```sql
WHERE created_at BETWEEN
      TIMESTAMP '2025-03-01'
  AND TIMESTAMP '2025-03-31 23:59:59';
```

### Root cause

The upper bound is inclusive and represents one exact timestamp, not the whole remaining precision range.

### Corrected

```sql
WHERE created_at >= TIMESTAMP '2025-03-01'
  AND created_at <  TIMESTAMP '2025-04-01';
```

### Lesson

Use half-open intervals for time windows.

---

## Scenario 4 — Non-deterministic ORDER BY

Broken:

```sql
SELECT *
FROM orders
ORDER BY created_at
LIMIT 100;
```

### Root cause

Ties at `created_at` are unresolved.

### Corrected

```sql
SELECT *
FROM orders
ORDER BY created_at, order_id
LIMIT 100;
```

provided `order_id` is unique.

### Lesson

Pagination and exports need a deterministic ordering key.

---

## Scenario 5 — Bad NULL concatenation

Broken:

```sql
SELECT
    first_name || ' ' || last_name AS full_name
FROM customers;
```

### Root cause

NULL can propagate through the concatenation expression.

### Corrected approach

Choose semantics intentionally. For example:

```sql
SELECT
    CONCAT(first_name, ' ', last_name) AS full_name
FROM customers;
```

or:

```sql
SELECT
    CONCAT_WS(' ', first_name, last_name) AS full_name
FROM customers;
```

when supported and appropriate.

### Lesson

Do not let missing-value behavior be accidental.

---

## Scenario 6 — Integer division

Broken:

```sql
SELECT
    successful_orders / total_orders AS success_rate
FROM daily_metrics;
```

### Root cause

Integer operands can produce integer division.

### Corrected

```sql
SELECT
    successful_orders::numeric
    / NULLIF(total_orders, 0) AS success_rate
FROM daily_metrics;
```

### Lesson

Data types are part of metric correctness.

---

## Scenario 7 — Non-sargable date filter

Broken:

```sql
SELECT *
FROM events
WHERE DATE(event_at) = DATE '2025-03-01';
```

### Root cause

The function transforms the filtered column.

### Corrected

```sql
SELECT *
FROM events
WHERE event_at >= TIMESTAMP '2025-03-01'
  AND event_at <  TIMESTAMP '2025-03-02';
```

### Lesson

Express filters as direct ranges when that preserves the intended meaning.

---

## Scenario 8 — Large OFFSET

Broken:

```sql
SELECT *
FROM orders
ORDER BY created_at, order_id
LIMIT 100
OFFSET 1000000;
```

### Root cause

Large offsets can force the database to account for a large preceding result.

### Corrected approach

Use a cursor:

```sql
SELECT *
FROM orders
WHERE (created_at, order_id)
      > (:last_created_at, :last_order_id)
ORDER BY created_at, order_id
LIMIT 100;
```

### Lesson

For large sequential extraction, keyset pagination is often a better fit.

---

# 41. Beginner → Intermediate → Advanced Practice

## Level 1 — Basic

### 1. Explicit columns

Write a query returning:

```text
customer_id
email
country
```

from `customers`.

**Goal:** avoid `SELECT *`.

---

### 2. Derived column

Return:

```text
order_id
amount
gross_amount = amount * 1.18
```

**Goal:** expressions and aliases.

---

### 3. Simple filtering

Return orders where:

```text
amount >= 500
```

**Goal:** comparison operators.

---

### 4. Multiple conditions

Return active customers from India.

**Goal:** `AND`.

---

### 5. Alternative values

Return customers from India or Nepal.

**Goal:** `OR` and `IN`.

---

### 6. Numeric range

Return orders with amount between 100 and 500.

**Goal:** inclusive `BETWEEN`.

---

### 7. Pattern matching

Find emails ending in:

```text
@example.com
```

**Goal:** `%`.

---

### 8. Classification

Classify order amount as high/medium/low using `CASE`.

**Goal:** conditional expressions.

---

### 9. Sorting

Return the largest orders first.

**Goal:** `ORDER BY ... DESC`.

---

### 10. Limited result

Return the top 10 orders by amount.

**Goal:** `ORDER BY` + `LIMIT`.

---

## Level 2 — Intermediate

### 1. NULL detection

Return customers whose email is missing.

Use:

```sql
IS NULL
```

---

### 2. NULL exclusion

Return customers whose email is known.

Use:

```sql
IS NOT NULL
```

---

### 3. NULL equality reasoning

Explain why:

```sql
NULL = NULL
```

is not TRUE.

---

### 4. Three-valued logic

Predict:

```sql
TRUE AND NULL
FALSE OR NULL
NOT NULL
```

before executing them.

---

### 5. Safe default

Replace a NULL country with:

```text
unknown
```

using `COALESCE`.

Explain the semantic consequence.

---

### 6. Divide safely

Calculate:

```text
revenue / order_count
```

without division by zero.

Use `NULLIF`.

---

### 7. NULL-safe comparison

Determine whether two source columns changed, treating NULL-to-NULL as unchanged.

Use `IS DISTINCT FROM`.

---

### 8. Deterministic sorting

Sort orders by:

```text
created_at DESC
order_id DESC
```

Explain why both are needed.

---

### 9. Timestamp window

Extract all orders in March 2025 using a half-open interval.

---

### 10. Type conversion

Convert a text ID to integer and a text date to date.

Explain why explicit casts are safer at system boundaries.

---

## Level 3 — Advanced

### 1. `NOT IN` trap

Construct a subquery containing NULL and explain exactly why `NOT IN` behaves unexpectedly.

---

### 2. Anti-membership redesign

Replace a risky `NOT IN` query with `NOT EXISTS` and explain the semantic difference.

---

### 3. Timestamp boundary proof

Create boundary rows exactly at:

```text
start
end
end - 1 microsecond
```

and prove the half-open range behavior.

---

### 4. Sargability rewrite

Rewrite:

```sql
WHERE DATE(created_at) = ...
```

without applying a function to the timestamp column.

---

### 5. Numeric sargability

Rewrite:

```sql
WHERE amount * 1.1 > 100
```

and explain when algebraic rewriting is valid.

---

### 6. Keyset pagination

Implement three sequential pages using:

```text
(created_at, order_id)
```

and no OFFSET.

---

### 7. Pagination under ties

Create duplicate timestamps and prove that using only the timestamp is insufficient for deterministic pagination.

---

### 8. Time-zone-aware extraction

Design a query for one calendar day in a specified business time zone while the source stores absolute instants.

Document the boundary conversion explicitly.

---

### 9. Cross-engine comparison

Run equivalent queries in PostgreSQL and DuckDB for:

- casts,
- NULL sorting,
- `ILIKE`,
- integer division,
- timestamp operations.

Record differences rather than assuming them.

---

### 10. Production extraction challenge

Design a query that includes:

- explicit columns,
- half-open boundaries,
- deterministic ordering,
- keyset pagination,
- NULL-aware logic,
- a clear statement of grain,
- an assertion for an expected invariant.

---

# 42. Real-World Data Engineering Scenarios

For every scenario, first answer:

> **What is the grain?**

Then answer:

- What should the query return?
- What edge cases exist?
- How does NULL affect it?
- How should timestamps be filtered?
- Is the predicate sargable?
- Is ordering deterministic?
- Is OFFSET or keyset pagination appropriate?

---

## Scenario 1 — Daily event extraction

**Grain:** one row per event.

Requirement:

> Extract all events for one UTC day.

Questions:

- Are event timestamps absolute instants?
- Is UTC really the intended boundary?
- Can multiple events share the same timestamp?
- What is the tie-breaker?

---

## Scenario 2 — Monthly financial reporting

**Grain:** one row per reportable transaction before later aggregation.

Requirement:

> Extract every transaction occurring in March.

Use:

```text
[start of March, start of April)
```

Questions:

- What timezone defines the accounting day?
- Could transaction timestamps include fractional seconds?
- Are adjacent month windows guaranteed not to overlap?

---

## Scenario 3 — Customer data with nullable attributes

**Grain:** one row per customer.

Requirement:

> Find customers outside India while preserving unknown country values.

Questions:

- Does NULL mean unknown?
- Should unknown be included?
- What downstream logic depends on this decision?

---

## Scenario 4 — Incremental source extraction

**Grain:** one source record per row.

Requirement:

> Extract only records created or changed within a window.

Questions:

- What is the exact lower boundary?
- What is the exact upper boundary?
- Are boundaries inclusive/exclusive?
- Is the timestamp indexed?
- Is the filter sargable?
- Is pagination needed?

---

## Scenario 5 — Deterministic export

**Grain:** one row per exported source record.

Requirement:

> Generate an export that is reproducible across runs.

Questions:

- Is there a unique ordering key?
- Are NULLs sorted explicitly if their position matters?
- Are timestamps tied?
- Is `ORDER BY` complete?

---

## Scenario 6 — API/event data with missing values

**Grain:** one row per event.

Requirement:

> Build a normalized event result while preserving meaningful missing fields.

Questions:

- Is a missing field unknown or not applicable?
- Would `COALESCE(..., '')` destroy useful meaning?
- Does concatenation propagate NULL?

---

## Scenario 7 — Data-quality validation

**Grain:** one row per record or one row per violation.

Requirement:

> Verify that customer IDs are non-NULL and unique.

Questions:

- What should a correct assertion return?
- Zero rows or a success count?
- Does the test itself handle NULL correctly?

---

## Scenario 8 — Large-table pagination

**Grain:** one row per order.

Requirement:

> Export 50 million rows.

Questions:

- Is OFFSET sustainable?
- Is there a stable unique ordering key?
- Can you use `(created_at, order_id)`?
- What happens if records are inserted while extraction runs?

---

# 43. Interview-Oriented Questions

The goal in an interview is not to recite syntax. Explain the reasoning.

---

## Question 1 — What is SQL's logical execution order?

### Expected thought process

Start from the row source, then row filters, grouping, group filters, windows, projection, distinctness, ordering, and row limiting.

### Concise answer

```text
FROM → WHERE → GROUP BY → HAVING → window functions
→ SELECT → DISTINCT → ORDER BY → LIMIT
```

### Deeper engineering explanation

This is a semantic model. The optimizer may use a different physical execution strategy as long as it preserves the required result.

### Common follow-up

> Why can `ORDER BY` generally use a SELECT alias but `WHERE` cannot?

Because `ORDER BY` is logically later than `SELECT` in this model.

---

## Question 2 — Why can't a SELECT alias normally be used in WHERE?

### Expected thought process

Ask when the alias becomes visible.

### Concise answer

`WHERE` is logically evaluated before `SELECT`, so the SELECT alias has not yet been created.

### Deeper explanation

Use an expression directly or introduce a derived-table/CTE boundary where the alias becomes an input column.

### Follow-up

> Can an optimizer physically calculate the expression early?

Yes. Physical execution can differ from logical processing.

---

## Question 3 — What is three-valued logic?

### Expected thought process

Explain why normal TRUE/FALSE is insufficient when information is missing.

### Concise answer

SQL predicates can evaluate to `TRUE`, `FALSE`, or `UNKNOWN`.

### Deeper explanation

Comparisons involving NULL are usually UNKNOWN. `WHERE` keeps only TRUE.

### Follow-up

> What is `TRUE AND UNKNOWN`?

UNKNOWN.

---

## Question 4 — Why does `NULL = NULL` not return TRUE?

### Expected thought process

Distinguish "two missing values" from "two known equal values".

### Concise answer

Equality comparison with NULL yields UNKNOWN; use `IS NULL` to test for NULL.

### Follow-up

> What if you want NULL-safe equality?

Use `IS NOT DISTINCT FROM`.

---

## Question 5 — Why can `NOT IN` fail with NULL?

### Expected thought process

Expand the predicate into comparisons and apply the truth tables.

### Concise answer

A NULL in the candidate set can make a non-matching comparison UNKNOWN, which can propagate through the `NOT IN` logic and cause the outer `WHERE` to reject rows.

### Follow-up

> What pattern is often safer?

`NOT EXISTS`.

---

## Question 6 — Difference between COALESCE and NULLIF?

### Concise answer

`COALESCE` chooses the first non-NULL value. `NULLIF` turns equality into NULL.

### Engineering use

- `COALESCE`: intentional fallback.
- `NULLIF`: intentionally represent a disallowed/undefined value as NULL, such as a zero denominator.

### Follow-up

> Why not replace all NULLs with zero?

Because NULL and zero have different meanings.

---

## Question 7 — Difference between `<>` and `IS DISTINCT FROM`?

### Concise answer

`<>` is ordinary inequality and can return UNKNOWN with NULL. `IS DISTINCT FROM` always returns a definite TRUE/FALSE result and treats NULL-safe equality semantics explicitly.

### Follow-up

> What does NULL vs NULL produce?

`IS DISTINCT FROM` → FALSE.

---

## Question 8 — Why is timestamp BETWEEN dangerous?

### Concise answer

`BETWEEN` is inclusive at both ends. For timestamps this encourages fragile "end of day" literals and awkward adjacent windows.

### Better pattern

```sql
ts >= start
AND ts < end
```

### Follow-up

> Why is that better?

It handles exact boundaries, arbitrary precision, and adjacent windows cleanly.

---

## Question 9 — What is a sargable predicate?

### Concise answer

A predicate written in a form that gives the optimizer a good opportunity to use an index or another efficient access path.

### Follow-up

> Does sargable guarantee an index scan?

No. The optimizer may choose another plan when it estimates that it is cheaper.

---

## Question 10 — Why can a function on a filtered column hurt performance?

### Concise answer

The function transforms the stored column, which can make direct index/range access less straightforward.

Example:

```sql
WHERE DATE(created_at) = DATE '2025-03-01'
```

can often be rewritten as:

```sql
WHERE created_at >= TIMESTAMP '2025-03-01'
  AND created_at <  TIMESTAMP '2025-03-02'
```

### Follow-up

> Could an expression index help?

Sometimes, depending on the engine and workload. That decision belongs to performance tuning and should be measured.

---

## Question 11 — OFFSET vs keyset pagination?

### Concise answer

OFFSET identifies a page by how many rows precede it. Keyset identifies a page by the last ordered key.

### Engineering trade-off

Keyset is often better for large sequential scans and extraction jobs. OFFSET remains useful for small datasets and arbitrary page navigation.

### Follow-up

> What is required for good keyset pagination?

A stable, deterministic ordering, usually including a unique tie-breaker.

---

## Question 12 — `timestamp` vs `timestamptz` in PostgreSQL?

### Concise answer

`timestamp without time zone` is a calendar date/time without an absolute-time-zone interpretation. `timestamptz` represents an absolute instant and is displayed according to the session time zone.

### Follow-up

> Does PostgreSQL store a timezone name with a `timestamptz` value?

No. It represents the instant rather than storing the original zone name as part of the value.

---

## Question 13 — Why does `5 / 2` behave differently depending on operand types?

### Concise answer

Because division follows the operand data types. With integer operands in PostgreSQL, integer division yields 2.

### Corrected ratio

```sql
SELECT 5::numeric / 2;
```

### Follow-up

> What else should you protect?

A zero denominator, using `NULLIF`.

---

# 44. Production Checklist

Before shipping a SELECT/filter/sort query, verify:

- [ ] Input grain is known.
- [ ] Output grain is known.
- [ ] Explicit columns are selected where appropriate.
- [ ] NULL behavior is intentional.
- [ ] `NOT IN` has been reviewed for NULL.
- [ ] Timestamp boundaries are half-open.
- [ ] Time-zone semantics are understood.
- [ ] Ordering is deterministic when order matters.
- [ ] Pagination strategy is appropriate.
- [ ] Predicates are reasonably sargable.
- [ ] Dialect-specific syntax is identified.
- [ ] Edge cases were tested.
- [ ] A tiny-table verification was performed.
- [ ] Important invariants have assertion queries.
- [ ] The query's business meaning can be explained without relying on implementation accidents.

---

# 45. Knowledge Check

Do not look at your notes until you can answer these.

## Theory

1. What is SQL's logical execution order?
2. What is the difference between logical processing and physical execution?
3. Why can't `WHERE` normally use a SELECT alias?
4. What are TRUE, FALSE, and UNKNOWN?
5. Why is `NULL = NULL` UNKNOWN?
6. Why does `WHERE` remove UNKNOWN rows?
7. What is the difference between NULL, zero, empty string, and FALSE?
8. What does `COALESCE` do?
9. What does `NULLIF` do?
10. What does `IS DISTINCT FROM` solve?
11. Why can `NOT IN` fail in the presence of NULL?
12. Why is `BETWEEN` often inappropriate for timestamp windows?
13. What is a half-open interval?
14. What is the difference between `timestamp` and `timestamptz` in PostgreSQL?
15. What is a sargable predicate?
16. Why does a sargable predicate not guarantee index usage?
17. Why is deterministic ordering important?
18. Why does large OFFSET pagination become expensive?
19. What problem does keyset pagination solve?
20. Why does `(created_at, order_id)` make a better cursor than `created_at` alone?

---

## Practical SQL tasks

### Task A — NULL semantics

Given:

```text
country = India
country = Nepal
country = NULL
```

Write a query that returns Nepal and NULL but not India.

### Task B — Safe ratio

Write a query for:

```text
completed_orders / total_orders
```

that avoids integer truncation and divide-by-zero.

### Task C — March extraction

Write a correct March 2025 timestamp filter.

### Task D — Stable ordering

Write an ordering for:

```text
created_at DESC
```

with a unique tie-breaker.

### Task E — Sargability

Rewrite:

```sql
WHERE DATE(created_at) = DATE '2025-03-01'
```

### Task F — Anti-membership

Replace a nullable `NOT IN` subquery with `NOT EXISTS`.

### Task G — Keyset pagination

Write page 2 of an ordered query using:

```text
(created_at, order_id)
```

### Task H — Dialect awareness

Identify which of the following are PostgreSQL-specific or non-universal:

```sql
ILIKE
x::type
NULLS LAST
```

---

# 46. Checkpoint — Ready for Topic 02?

The Module 2.6 roadmap says you are ready to move on only when you can do all of these without looking at your notes:

- [ ] List the logical order of SQL clauses from memory.
- [ ] Explain three-valued logic.
- [ ] Explain why `NOT IN` with NULL can return no rows.
- [ ] Use `COALESCE` correctly.
- [ ] Use `NULLIF` correctly.
- [ ] Use `IS DISTINCT FROM` correctly.
- [ ] Filter timestamps with half-open ranges.
- [ ] Explain what makes a predicate sargable.
- [ ] Explain why sargability does not guarantee index usage.
- [ ] Use deterministic ordering with a tie-breaker.
- [ ] Explain why large OFFSET pagination can be costly.
- [ ] Implement keyset pagination with `(created_at, order_id)`.
- [ ] Explain the PostgreSQL `timestamp` vs `timestamptz` distinction.
- [ ] Identify important PostgreSQL/DuckDB dialect differences.

## Practical coding gates

### Gate 1 — NULL

Build a tiny table containing NULLs and prove:

```text
NULL = NULL       → UNKNOWN
NULL IS NULL      → TRUE
NULL <> 'x'       → UNKNOWN
```

### Gate 2 — `NOT IN`

Create a nullable subquery and reproduce the trap. Then rewrite it with `NOT EXISTS`.

### Gate 3 — Time window

Prove that:

```sql
ts >= start
AND ts < end
```

includes the start and excludes the end.

### Gate 4 — Sargability

Rewrite:

```sql
WHERE DATE(created_at) = ...
```

into a direct timestamp range and explain why the form is more optimizer-friendly.

### Gate 5 — Keyset pagination

Implement two or more pages using `(created_at, order_id)` with no OFFSET.

Do **not** move to Topic 02 until each gate is understood, not merely copied.

---

# 47. Common Mistakes — Final Summary

The roadmap's critical mistakes are:

- `= NULL` instead of `IS NULL`.
- Relying on result order without `ORDER BY`.
- Using `BETWEEN` for timestamp windows.
- Wrapping filtered columns in functions.

Also remember:

- `NOT IN` with a nullable subquery can be logically wrong.
- `<>` does not automatically include NULL.
- `NULL` is not zero, empty string, or FALSE.
- `COALESCE` changes semantics; it does not merely "clean" data.
- `NULLIF` can express undefined values safely.
- `IS DISTINCT FROM` is useful for NULL-safe change detection.
- Arithmetic and concatenation can propagate NULL.
- `LIMIT` without meaningful ordering does not identify a deterministic subset.
- A timestamp alone may not produce deterministic ordering.
- Large OFFSET pagination can be inefficient.
- Sargability is an optimizer opportunity, not an index-use guarantee.
- Integer division can silently corrupt ratios.
- `timestamp` and `timestamptz` have different semantics in PostgreSQL.
- Standard SQL and dialect-specific SQL are not the same thing.
- Logical query processing order and physical execution order are not the same thing.

---

# Final Mental Model

When you write a SQL query in production, think in this sequence:

```text
1. What is the input grain?
        ↓
2. What exact rows do I want?
        ↓
3. What should NULL mean?
        ↓
4. What is the logical query order?
        ↓
5. Are comparisons and boolean predicates correct?
        ↓
6. What are the exact time boundaries?
        ↓
7. Is the ordering deterministic?
        ↓
8. Do I need LIMIT/OFFSET or keyset pagination?
        ↓
9. Is the predicate written in an optimizer-friendly form?
        ↓
10. Did I test NULLs, ties, empty input, and boundaries?
```

The senior data-engineering habit is not:

> "I know SQL syntax."

It is:

> **"I can predict what rows this query will return, including edge cases, explain why, and write the query so that its semantics remain correct in production."**
