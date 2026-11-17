# 04 — Subqueries and CTEs

> **Module:** 2.6 — SQL for Data Engineers  
> **Phase:** B — Expressive Analytical SQL  
> **Primary engines:** PostgreSQL 16+ and DuckDB  
> **Core idea:** A complex SQL transformation can be designed as a sequence of well-defined relational steps, where every step has a known input grain, output grain, purpose, and correctness condition.

Subqueries and Common Table Expressions (CTEs) are the structural tools that let you turn complicated SQL into understandable stages.

The goal of this chapter is not to memorize:

```sql
SELECT ...
FROM (
    ...
)
```

or:

```sql
WITH step_1 AS (...),
step_2 AS (...)
SELECT ...
FROM step_2;
```

The goal is to learn how to decompose a production transformation into explicit relational steps.

The central mental model is:

```text
Raw rows
    ↓
filter / clean
    ↓
join / enrich
    ↓
aggregate
    ↓
final transformation
```

A subquery gives you a way to build an intermediate relation or value.

A CTE gives that intermediate relation a name.

A recursive CTE extends the same idea to repeated traversal.

The professional habit is:

> **Know the grain, purpose, cardinality, NULL behavior, and termination condition of every intermediate step.**

---

# 1. Learning Objectives

By the end of this chapter, you should be able to:

- Explain what a subquery is.
- Distinguish:
  - scalar subqueries,
  - subqueries in `FROM`,
  - derived tables,
  - subqueries in `WHERE`,
  - `IN`,
  - `EXISTS`,
  - correlated subqueries,
  - CTEs,
  - recursive CTEs.
- Explain when a scalar subquery is appropriate.
- Recognize when a scalar subquery returns too many rows.
- Use subqueries as intermediate relations.
- Use `IN` for membership questions.
- Use `EXISTS` for existence questions.
- Explain why `JOIN`, `IN`, and `EXISTS` are not merely interchangeable syntactic styles.
- Explain how duplicates and NULLs affect `IN`, `NOT IN`, `EXISTS`, `JOIN`, and anti-join patterns.
- Explain correlated versus uncorrelated subqueries.
- Explain the conceptual row-by-row model of a correlated subquery without assuming that the physical engine literally executes it once per outer row.
- Explain why optimizers may decorrelate or rewrite correlated subqueries.
- Recognize situations where correlated subqueries can still be expensive.
- Rewrite appropriate correlated subqueries as joins plus pre-aggregation.
- Build multi-stage CTE pipelines.
- Track grain across every CTE.
- Use meaningful CTE names.
- Connect CTE pipeline thinking to dbt-style transformation models.
- Write recursive CTEs.
- Explain the anchor member and recursive member.
- Traverse:
  - employee-manager hierarchies,
  - category trees,
  - graph edges.
- Track recursion depth.
- Define explicit termination conditions.
- Protect recursive traversals against cycles.
- Generate date ranges using `generate_series` where supported.
- Build date spines.
- Fill missing dates with zeroes intentionally.
- Explain recursive alternatives to `generate_series`.
- Explain that CTEs are logical query constructs, not automatically materialized temporary tables.
- Explain PostgreSQL CTE inlining behavior at a practical level.
- Use PostgreSQL `MATERIALIZED` and `NOT MATERIALIZED` deliberately.
- Compare CTEs, temporary tables, views, and materialized views conceptually.
- Debug subqueries and CTE pipelines one stage at a time.
- Write assertion queries for transformation invariants.
- Choose the clearest correct SQL structure for production.

---

# 2. Why Subqueries and CTEs Matter in Data Engineering

Production SQL rarely stays small.

A realistic transformation may involve:

```text
raw source
    ↓
remove invalid rows
    ↓
normalize values
    ↓
join dimensions
    ↓
aggregate
    ↓
calculate business metrics
    ↓
publish final relation
```

Trying to express every step in one deeply nested query can make the logic difficult to:

- read,
- test,
- review,
- debug,
- explain,
- maintain,
- and validate.

Subqueries and CTEs provide structure.

---

## 2.1 The transformation-pipeline mindset

Think:

```text
raw
  ↓
clean
  ↓
enriched
  ↓
aggregated
  ↓
final
```

rather than:

```text
one giant query containing everything
```

A CTE can give each stage a name:

```sql
WITH clean_orders AS (...),
enriched_orders AS (...),
customer_totals AS (...)
SELECT ...
FROM customer_totals;
```

This is useful because the names communicate intent.

---

# 3. The Core Mental Model

Use these definitions:

```text
Scalar subquery
→ "What single value do I need?"

FROM / derived-table subquery
→ "What intermediate relation should I build?"

IN
→ "Is this value contained in this set?"

EXISTS
→ "Does at least one matching row exist?"

Correlated subquery
→ "What result depends on the current outer row?"

CTE
→ "What transformation step should I name?"

Recursive CTE
→ "How do I repeatedly follow a relationship?"
```

These are different problem shapes.

Do not choose the syntax first.

Choose the question first.

---

# 4. What Is a Subquery?

A **subquery** is a query embedded inside another SQL statement.

Example:

```sql
SELECT
    customer_id,
    (
        SELECT COUNT(*)
        FROM orders
    ) AS total_orders
FROM customers;
```

The query inside:

```sql
(
    SELECT COUNT(*)
    FROM orders
)
```

is a subquery.

The outer query can use its result.

---

## 4.1 Subqueries can return different shapes

A subquery can produce:

```text
one value
    ↓
scalar subquery

many rows / columns
    ↓
relation

a boolean existence test
    ↓
EXISTS

a membership set
    ↓
IN
```

The shape of the result determines where the subquery can be used.

---

# 5. Scalar Subqueries

A scalar subquery is a subquery expected to return:

```text
one row
+
one column
=
one value
```

Example:

```sql
SELECT
    customer_id,
    (
        SELECT AVG(amount)
        FROM orders
    ) AS overall_average_order_value
FROM customers;
```

The inner query produces one scalar:

```text
overall average order value
```

The outer query can then place that value beside each customer.

---

## 5.1 Grain reasoning

Outer query:

```text
one row per customer
```

Scalar subquery:

```text
one scalar value for the entire statement
```

Final output:

```text
one row per customer
+
same scalar average on each row
```

The scalar subquery does not create additional customer rows.

---

## 5.2 Another scalar example

Suppose:

```text
customer_totals
→ one row per customer
```

Requirement:

> Return customers whose spend is above the average customer spend.

```sql
SELECT
    customer_id,
    total_spend
FROM customer_totals
WHERE total_spend > (
    SELECT AVG(total_spend)
    FROM customer_totals
);
```

The inner query returns:

```text
one value
```

The outer WHERE compares every customer against that value.

---

# 6. Scalar Subquery Rules and Failure Cases

A scalar context expects a single value.

This can be valid:

```sql
SELECT (
    SELECT AVG(amount)
    FROM orders
);
```

because `AVG` returns one aggregate row for a scalar aggregate query.

But this can fail:

```sql
SELECT (
    SELECT customer_id
    FROM customers
);
```

if `customers` contains multiple rows.

The database cannot put multiple values into a single scalar slot.

---

## 6.1 The important question

Whenever you use a scalar subquery, ask:

```text
Can this subquery return:
0 rows?
1 row?
multiple rows?
```

The expected cardinality must be intentional.

---

## 6.2 Zero rows

A scalar subquery that produces no row can result in a NULL-like scalar result depending on the expression/context.

For example, an aggregate often still returns one row with NULL:

```sql
SELECT (
    SELECT SUM(amount)
    FROM orders
    WHERE false
);
```

The result is a scalar NULL.

This is different from a non-aggregate scalar query that simply produces no row.

The exact behavior of scalar subquery contexts should be verified for unusual expressions, but the practical rule is:

> **Know whether your subquery is guaranteed to return exactly one row.**

---

## 6.3 Multiple rows

A scalar subquery returning multiple rows is an error in a scalar context.

Do not "fix" this blindly by adding:

```sql
LIMIT 1
```

unless the business requirement actually defines which row should survive.

For example:

```sql
(
    SELECT amount
    FROM orders
    WHERE customer_id = c.customer_id
    ORDER BY created_at DESC, order_id DESC
    LIMIT 1
)
```

can be correct when the requirement is:

> latest order amount.

But:

```sql
LIMIT 1
```

without a meaningful ordering is usually not a business definition.

---

# 7. Subqueries in FROM

A subquery in `FROM` produces an intermediate relation.

Example:

```sql
SELECT
    customer_id,
    total_spend
FROM (
    SELECT
        customer_id,
        SUM(amount) AS total_spend
    FROM orders
    GROUP BY customer_id
) AS customer_totals;
```

The inner query creates a derived relation.

---

## 7.1 Grain

Inner query:

```text
input grain:
one row per order

GROUP BY customer_id

output grain:
one row per customer
```

Outer query receives:

```text
one row per customer
```

This is a key reason derived tables are useful.

---

# 8. Derived Tables

A subquery in `FROM` is commonly called a **derived table**.

Mental model:

```text
inner query
     ↓
temporary relation for this statement
     ↓
outer query consumes it
```

Example:

```sql
SELECT
    customer_id,
    total_spend
FROM (
    SELECT
        customer_id,
        SUM(amount) AS total_spend
    FROM orders
    GROUP BY customer_id
) AS customer_totals
WHERE total_spend > 1000;
```

---

## 8.1 Why use a derived table?

It gives you:

- a query boundary,
- a named intermediate result,
- separation between stages,
- a place where calculated columns become input columns to the outer query.

This can solve visibility issues.

For example:

```sql
SELECT
    amount * 1.18 AS gross_amount
FROM orders
WHERE gross_amount > 100;
```

is problematic because the WHERE stage does not normally see the SELECT alias.

A derived-table rewrite is:

```sql
SELECT
    gross_amount
FROM (
    SELECT
        amount * 1.18 AS gross_amount
    FROM orders
) AS x
WHERE gross_amount > 100;
```

Now the outer query receives `gross_amount` as an input column.

---

# 9. Derived Table vs CTE

These often express the same logical idea.

Derived table:

```sql
SELECT ...
FROM (
    SELECT ...
) AS x;
```

CTE:

```sql
WITH x AS (
    SELECT ...
)
SELECT ...
FROM x;
```

The CTE form is often easier to read when there are multiple stages.

Use a derived table when the intermediate logic is:

- short,
- local,
- used once,
- clearer inline.

Use a CTE when:

- there are several stages,
- each stage deserves a name,
- grain changes need to be documented,
- debugging and review benefit from named steps.

---

# 10. Subqueries in WHERE

A subquery in `WHERE` can answer membership or existence questions.

Example:

```sql
SELECT
    customer_id
FROM customers
WHERE customer_id IN (
    SELECT customer_id
    FROM orders
);
```

The inner query produces a set of customer IDs.

The outer query asks:

> Is this customer ID in that set?

---

# 11. IN Subqueries

`IN` expresses set membership.

```sql
SELECT
    c.customer_id
FROM customers AS c
WHERE c.customer_id IN (
    SELECT o.customer_id
    FROM orders AS o
);
```

The subquery can contain duplicate values.

Suppose:

```text
orders
customer_id
-----------
1
1
1
2
```

The membership set conceptually contains:

```text
1
2
```

Customer 1 is still returned once by the outer query.

This differs from an ordinary JOIN, which can produce multiple customer rows.

---

## 11.1 Duplicate behavior

Consider:

```sql
SELECT c.customer_id
FROM customers AS c
JOIN orders AS o
    ON o.customer_id = c.customer_id;
```

Customer 1 with three orders can produce:

```text
1
1
1
```

But:

```sql
SELECT c.customer_id
FROM customers AS c
WHERE c.customer_id IN (
    SELECT o.customer_id
    FROM orders AS o
);
```

still returns:

```text
1
```

once.

That difference is semantic, not merely stylistic.

---

# 12. EXISTS

`EXISTS` asks:

> Does the subquery produce at least one matching row?

Example:

```sql
SELECT
    c.customer_id
FROM customers AS c
WHERE EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.customer_id
);
```

This is naturally read as:

> Return customers for whom at least one order exists.

---

## 12.1 Why SELECT 1?

The conventional form is:

```sql
SELECT 1
```

because the actual selected value is not the business question.

The condition only cares whether the subquery can produce a row.

The important semantic result is:

```text
at least one row exists
→ TRUE

no rows exist
→ FALSE
```

---

## 12.2 Duplicates do not duplicate the outer row

If customer 1 has 100 orders, EXISTS is still simply:

```text
TRUE
```

for customer 1.

It does not create 100 copies of the customer.

That makes it a natural choice for existence testing.

---

# 13. IN vs EXISTS

Use the question to guide the form.

| Situation | Typical expression |
|---|---|
| Membership in a value set | `IN` |
| Existence related to current outer row | `EXISTS` |
| Need columns from matching rows | `JOIN` |
| Need only whether a match exists | `EXISTS` |
| Need "no match exists" | `NOT EXISTS` |

Do not turn this into:

> "`EXISTS` is always faster."

That is not a reliable engineering rule.

Modern optimizers can rewrite subqueries, and performance depends on:

- data volume,
- cardinality,
- indexes/access paths,
- statistics,
- selectivity,
- engine behavior,
- query structure.

Semantics come first.

---

# 14. IN vs EXISTS — NULL Semantics

NULLs make membership predicates more subtle.

Suppose:

```text
blocked_customers
-----------------
2
NULL
```

Then:

```sql
WHERE customer_id NOT IN (
    SELECT customer_id
    FROM blocked_customers
)
```

can produce unexpected results because NULL can introduce UNKNOWN into the logical comparison.

This is why anti-membership logic requires special care.

---

## 14.1 EXISTS is relationship-based

For:

```sql
WHERE NOT EXISTS (
    SELECT 1
    FROM blocked_customers AS b
    WHERE b.customer_id = c.customer_id
)
```

the question is:

> Is there a matching blocked row for this outer customer?

A NULL in an unrelated blocked row does not automatically make every outer customer match.

This is one reason NOT EXISTS is often easier to reason about for anti-membership.

---

# 15. Correlated Subqueries

A correlated subquery references a value from the outer query.

Example:

```sql
SELECT
    c.customer_id,
    (
        SELECT COUNT(*)
        FROM orders AS o
        WHERE o.customer_id = c.customer_id
    ) AS order_count
FROM customers AS c;
```

The inner query references:

```sql
c.customer_id
```

from the outer query.

That makes it correlated.

---

# 16. Uncorrelated vs Correlated Subqueries

## Uncorrelated

```sql
SELECT
    AVG(amount)
FROM orders;
```

The subquery does not depend on the current outer row.

Conceptually it asks:

> What is the overall average?

---

## Correlated

```sql
SELECT
    c.customer_id,
    (
        SELECT COUNT(*)
        FROM orders AS o
        WHERE o.customer_id = c.customer_id
    ) AS order_count
FROM customers AS c;
```

The result depends on:

```text
which customer row is currently being considered
```

---

## Mental model

```text
Uncorrelated:

one independent result
        ↓
outer query uses it


Correlated:

outer row
   ↓
subquery can reference outer values
   ↓
result for that outer context
```

---

# 17. Correlated Subquery Conceptual Execution

For learning purposes, imagine:

```text
for each customer:
    find orders for that customer
    count them
    attach the count
```

But this is only the **logical/conceptual model**.

Do not assume PostgreSQL or DuckDB must literally execute the subquery separately for every outer row.

The optimizer may transform the query.

---

# 18. Correlated Subquery Performance

A correlated query can be expensive when:

- the outer input is large,
- the inner logic is expensive,
- the optimizer cannot efficiently decorrelate it,
- required access paths are missing,
- correlation causes repeated work.

Conceptually:

```text
1 million outer rows
×
expensive inner operation
```

can be a warning sign.

But this does not imply:

> all correlated subqueries are slow.

Modern optimizers can transform many correlated forms.

---

# 19. How Optimizers May Rewrite Correlated Subqueries

Consider:

```sql
SELECT
    c.customer_id,
    (
        SELECT SUM(o.amount)
        FROM orders AS o
        WHERE o.customer_id = c.customer_id
    ) AS total_spend
FROM customers AS c;
```

A relationally equivalent strategy is:

```sql
WITH customer_totals AS (
    SELECT
        customer_id,
        SUM(amount) AS total_spend
    FROM orders
    GROUP BY customer_id
)
SELECT
    c.customer_id,
    COALESCE(ct.total_spend, 0) AS total_spend
FROM customers AS c
LEFT JOIN customer_totals AS ct
    ON ct.customer_id = c.customer_id;
```

The second form makes the transformation more explicit.

An optimizer may perform similar rewrites internally in some cases.

---

## 19.1 Why the rewrite can help

The rewritten form makes:

```text
orders
→ aggregate once by customer
→ join one summary row per customer
```

explicit.

This can avoid conceptual repeated work.

But:

> **Do not claim the CTE/JOIN version is automatically faster.**

The database optimizer may already find an efficient strategy for the correlated query.

Measure when performance matters.

---

# 20. When to Rewrite a Correlated Subquery

A rewrite is often useful when:

- the inner calculation is naturally an aggregate by outer key,
- several outer rows would otherwise request the same type of computation,
- the transformation becomes easier to inspect as a relation,
- grain is clearer in a CTE pipeline.

Keep the original correlated form when it is:

- clearer,
- naturally per-row,
- small in scope,
- performant enough,
- or better aligned with the actual business question.

The goal is not "eliminate all correlated subqueries."

The goal is:

> **Choose the clearest correct structure and verify performance when it matters.**

---

# 21. Common Table Expressions

A **Common Table Expression (CTE)** is a named query relation declared before the main query.

Basic syntax:

```sql
WITH clean_orders AS (
    SELECT
        *
    FROM orders
    WHERE status <> 'invalid'
)
SELECT
    *
FROM clean_orders;
```

The CTE name:

```text
clean_orders
```

can be referenced by the main query.

---

# 22. WITH Syntax

General form:

```sql
WITH
step_1 AS (
    ...
),
step_2 AS (
    ...
)
SELECT ...
FROM step_2;
```

A later CTE can depend on an earlier CTE.

---

## 22.1 CTE scope

A normal CTE exists for the statement in which it is declared.

Think:

```text
WITH clause
      ↓
named intermediate relations
      ↓
main statement
```

A CTE is not automatically a permanent database object.

---

# 23. Multiple CTEs

Example:

```sql
WITH clean_orders AS (
    SELECT
        order_id,
        customer_id,
        amount
    FROM orders
    WHERE status = 'completed'
),
customer_totals AS (
    SELECT
        customer_id,
        SUM(amount) AS total_spend
    FROM clean_orders
    GROUP BY customer_id
)
SELECT
    customer_id,
    total_spend
FROM customer_totals
ORDER BY total_spend DESC;
```

Dependency chain:

```text
orders
  ↓
clean_orders
  ↓
customer_totals
  ↓
final SELECT
```

This is one of the most useful patterns in transformation SQL.

---

# 24. CTE Dependency Chains

Think of a multi-CTE statement as a directed dependency graph:

```text
raw_orders
     ↓
clean_orders
     ↓
enriched_orders
     ↓
customer_totals
     ↓
final_metrics
```

Each stage should have one primary responsibility.

---

# 25. CTEs as Transformation Pipelines

A production transformation often follows:

```text
import
  ↓
clean
  ↓
join
  ↓
aggregate
  ↓
final
```

A CTE pipeline can represent exactly that:

```sql
WITH raw_orders AS (
    ...
),
clean_orders AS (
    ...
),
enriched_orders AS (
    ...
),
customer_totals AS (
    ...
),
final AS (
    ...
)
SELECT *
FROM final;
```

---

# 26. Grain Tracking Across CTEs

This is a mandatory production habit.

For every important CTE, document:

```text
CTE name:
Purpose:
Input grain:
Output grain:
Important assumptions:
NULL behavior:
Duplicate behavior:
```

Example:

```text
CTE:
clean_orders

Purpose:
remove invalid orders

Input grain:
one row per source order event

Output grain:
one row per valid source order event
```

Then:

```text
CTE:
customer_totals

Purpose:
summarize orders by customer

Input grain:
one row per order

Output grain:
one row per customer
```

---

# 27. Grain Tracking Example

Consider:

```sql
WITH clean_orders AS (
    SELECT
        order_id,
        customer_id,
        amount
    FROM orders
    WHERE status = 'completed'
),
customer_totals AS (
    SELECT
        customer_id,
        SUM(amount) AS total_spend
    FROM clean_orders
    GROUP BY customer_id
)
SELECT *
FROM customer_totals;
```

Grain map:

```text
orders
→ one row per order

clean_orders
→ one row per valid completed order

customer_totals
→ one row per customer
```

This is far easier to reason about than an unexplained chain of nested subqueries.

---

# 28. CTEs and dbt-Style Transformation Thinking

The purpose here is not to teach dbt itself.

The useful connection is structural.

A dbt-style transformation often resembles:

```text
source
  ↓
staging
  ↓
clean model
  ↓
intermediate model
  ↓
mart
```

Within one SQL statement, CTEs let you think similarly:

```text
raw
  ↓
clean
  ↓
enrich
  ↓
aggregate
  ↓
final
```

This develops the same professional habit:

> **Separate logical transformations and make each transformation's contract explicit.**

---

# 29. EXISTS vs IN vs JOIN

Use one common business problem:

> Find customers who have placed at least one completed order.

---

## 29.1 JOIN

```sql
SELECT DISTINCT
    c.customer_id
FROM customers AS c
JOIN orders AS o
    ON o.customer_id = c.customer_id
WHERE o.status = 'completed';
```

Why the `DISTINCT`?

Because one customer can have multiple completed orders.

The JOIN creates matching row combinations.

---

## 29.2 IN

```sql
SELECT
    c.customer_id
FROM customers AS c
WHERE c.customer_id IN (
    SELECT o.customer_id
    FROM orders AS o
    WHERE o.status = 'completed'
);
```

This asks:

> Is the customer ID contained in the completed-order customer-ID set?

---

## 29.3 EXISTS

```sql
SELECT
    c.customer_id
FROM customers AS c
WHERE EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.customer_id
      AND o.status = 'completed'
);
```

This asks:

> Does at least one completed order exist for this customer?

---

# 30. Semantic Comparison

| Property | JOIN | IN | EXISTS |
|---|---|---|---|
| Primary idea | matching row combinations | membership | existence |
| Duplicate matches | can duplicate outer rows | do not duplicate outer rows | do not duplicate outer rows |
| Need right-side columns | yes, naturally | no | no |
| Correlation | optional | optional | common |
| NULL semantics | join predicate dependent | important | predicate dependent |
| Best mental model | "which rows match?" | "is value in set?" | "does a match exist?" |

Do not turn the table into a speed ranking.

The database optimizer decides the physical strategy.

---

# 31. Duplicates and NULL Semantics

This section must be reasoned through with tiny data.

Create:

```sql
CREATE TEMP TABLE customers_semantics (
    customer_id INTEGER
);

INSERT INTO customers_semantics
VALUES
    (1),
    (2),
    (3),
    (NULL);

CREATE TEMP TABLE orders_semantics (
    order_id INTEGER,
    customer_id INTEGER
);

INSERT INTO orders_semantics
VALUES
    (101, 1),
    (102, 1),
    (103, 2),
    (104, NULL);
```

Now compare:

```text
JOIN
IN
EXISTS
NOT IN
NOT EXISTS
```

before executing.

---

# 32. JOIN and Duplicates

```sql
SELECT
    c.customer_id,
    o.order_id
FROM customers_semantics AS c
JOIN orders_semantics AS o
    ON o.customer_id = c.customer_id
ORDER BY
    c.customer_id,
    o.order_id;
```

Customer 1 appears twice because two orders match.

This is expected JOIN behavior.

---

# 33. IN and Duplicates

```sql
SELECT
    customer_id
FROM customers_semantics
WHERE customer_id IN (
    SELECT customer_id
    FROM orders_semantics
);
```

The presence of two orders for customer 1 does not produce two outer customer rows.

The question is membership, not row pairing.

---

# 34. EXISTS and Duplicates

```sql
SELECT
    c.customer_id
FROM customers_semantics AS c
WHERE EXISTS (
    SELECT 1
    FROM orders_semantics AS o
    WHERE o.customer_id = c.customer_id
);
```

Again:

```text
customer 1 → TRUE
```

not:

```text
customer 1
customer 1
```

because EXISTS is a boolean existence test.

---

# 35. NOT IN and NULL

With:

```text
orders_semantics.customer_id
=
1, 1, 2, NULL
```

this:

```sql
SELECT
    customer_id
FROM customers_semantics
WHERE customer_id NOT IN (
    SELECT customer_id
    FROM orders_semantics
);
```

must be treated carefully.

For a customer ID that does not match any known value, comparison against the NULL in the subquery can introduce UNKNOWN.

This is the classic negative-membership NULL trap.

---

# 36. NOT EXISTS

The relationship-based form:

```sql
SELECT
    c.customer_id
FROM customers_semantics AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM orders_semantics AS o
    WHERE o.customer_id = c.customer_id
);
```

asks:

> Is there no matching order row for this current customer?

A NULL order key does not match a known customer key under normal equality.

This is often the easier anti-membership expression to reason about.

---

# 37. Empty Subqueries

An empty membership set behaves differently from a NULL-containing set.

Suppose:

```sql
SELECT customer_id
FROM empty_orders;
```

returns no rows.

Then:

```sql
WHERE customer_id IN (...)
```

has no positive membership matches.

And:

```sql
NOT EXISTS (...)
```

is TRUE for each outer row with no matching row.

This is one reason tiny test datasets should include:

```text
empty
```

as an explicit case.

---

# 38. Recursive CTEs

Recursive CTEs extend the CTE model to repeated traversal.

Use them for structures such as:

- employee-manager hierarchies,
- category trees,
- parent-child relationships,
- dependency chains,
- graph traversal.

A recursive CTE repeatedly adds rows generated from its previous result.

---

# 39. Recursive CTE Anatomy

A recursive CTE contains two conceptual parts:

```text
Anchor member
+
Recursive member
```

Basic pattern:

```sql
WITH RECURSIVE hierarchy AS (
    -- Anchor
    SELECT
        ...

    UNION ALL

    -- Recursive member
    SELECT
        ...
    FROM hierarchy
    JOIN ...
)
SELECT *
FROM hierarchy;
```

---

# 40. Anchor Member

The **anchor member** establishes the starting rows.

For an employee hierarchy, that might be the CEO:

```sql
SELECT
    employee_id,
    employee_name,
    manager_id,
    0 AS depth
FROM employees
WHERE manager_id IS NULL;
```

The anchor says:

> These are the roots of the traversal.

---

# 41. Recursive Member

The recursive member finds the next level.

Example:

```sql
SELECT
    e.employee_id,
    e.employee_name,
    e.manager_id,
    h.depth + 1
FROM employees AS e
JOIN hierarchy AS h
    ON e.manager_id = h.employee_id;
```

The recursive member says:

> From the employees already discovered, find their direct reports.

---

# 42. UNION ALL in Recursive CTEs

The common structure is:

```sql
anchor
UNION ALL
recursive_member
```

This lets the recursive result accumulate levels.

Conceptually:

```text
level 0
   ↓
level 1
   ↓
level 2
   ↓
...
```

---

# 43. Recursion Termination

Every recursive query needs an understandable stopping condition.

Ask:

> What causes the recursive member to stop producing new rows?

Possible answers:

- reached a leaf,
- no child exists,
- filtered traversal,
- cycle detection,
- explicit maximum depth.

Never teach or deploy recursive SQL without explaining how the recursion terminates.

---

# 44. Employee-Manager Hierarchy

Use:

```text
employee_id
employee_name
manager_id
```

Example data:

```text
1 | CEO             | NULL
2 | VP Engineering  | 1
3 | Engineer A      | 2
4 | Engineer B      | 2
5 | VP Sales        | 1
6 | Sales Rep       | 5
```

Hierarchy:

```text
CEO
├── VP Engineering
│   ├── Engineer A
│   └── Engineer B
└── VP Sales
    └── Sales Rep
```

---

## 44.1 Recursive query

```sql
WITH RECURSIVE employee_tree AS (
    SELECT
        employee_id,
        employee_name,
        manager_id,
        0 AS depth,
        employee_name::TEXT AS path
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    SELECT
        e.employee_id,
        e.employee_name,
        e.manager_id,
        et.depth + 1,
        et.path || ' > ' || e.employee_name
    FROM employees AS e
    JOIN employee_tree AS et
        ON e.manager_id = et.employee_id
)
SELECT
    employee_id,
    employee_name,
    manager_id,
    depth,
    path
FROM employee_tree
ORDER BY
    path;
```

The exact concatenation/type syntax may need adaptation for DuckDB.

---

# 45. Employee Hierarchy Grain

For each recursion level:

```text
one row
=
one discovered employee at one traversal path
```

If the underlying hierarchy should contain each employee only once from a root, you must validate that assumption.

Graph-like structures can generate multiple paths to the same node.

Therefore:

> **Node uniqueness and path uniqueness are separate concepts.**

---

# 46. Category Trees

Use:

```text
category_id
category_name
parent_category_id
```

Example:

```text
10 | Electronics | NULL
20 | Phones      | 10
30 | Android     | 20
40 | iPhone      | 20
```

Hierarchy:

```text
Electronics
├── Phones
│   ├── Android
│   └── iPhone
```

---

## 46.1 Recursive category path

```sql
WITH RECURSIVE category_tree AS (
    SELECT
        category_id,
        category_name,
        parent_category_id,
        0 AS depth,
        category_name::TEXT AS path
    FROM categories
    WHERE parent_category_id IS NULL

    UNION ALL

    SELECT
        c.category_id,
        c.category_name,
        c.parent_category_id,
        ct.depth + 1,
        ct.path || ' > ' || c.category_name
    FROM categories AS c
    JOIN category_tree AS ct
        ON c.parent_category_id = ct.category_id
)
SELECT
    category_id,
    category_name,
    depth,
    path
FROM category_tree;
```

---

# 47. Graph Walks

Recursive CTEs can also traverse an edge table.

Example:

```text
edges

from_node | to_node
----------+--------
A         | B
B         | C
C         | D
```

Requirement:

> Find nodes reachable from A.

---

## 47.1 Conceptual structure

```sql
WITH RECURSIVE reachable AS (
    SELECT
        'A' AS node,
        0 AS depth

    UNION ALL

    SELECT
        e.to_node,
        r.depth + 1
    FROM reachable AS r
    JOIN edges AS e
        ON e.from_node = r.node
)
SELECT *
FROM reachable;
```

Result conceptually:

```text
A | 0
B | 1
C | 2
D | 3
```

---

# 48. Why Graph Traversal Can Be Dangerous

Consider:

```text
A → B
B → C
C → A
```

Now recursion can loop.

The traversal does not naturally reach a leaf.

It can keep rediscovering:

```text
A
B
C
A
B
C
...
```

This is why cycle protection matters.

---

# 49. Cycle Protection

A common strategy is to carry a path of already visited nodes.

Conceptually:

```text
path = [A]

next:
[A, B]

next:
[A, B, C]

before moving to A:
A already exists in path
→ do not recurse
```

In SQL, the exact representation can be an array, list, or other engine-supported structure.

---

# 50. PostgreSQL Cycle-Safe Pattern

For a simple integer node ID, a PostgreSQL-style approach is:

```sql
WITH RECURSIVE graph_walk AS (
    SELECT
        1 AS node,
        0 AS depth,
        ARRAY[1] AS path

    UNION ALL

    SELECT
        e.to_node AS node,
        gw.depth + 1,
        gw.path || e.to_node
    FROM graph_walk AS gw
    JOIN edges AS e
        ON e.from_node = gw.node
    WHERE NOT e.to_node = ANY(gw.path)
      AND gw.depth < 100
)
SELECT
    node,
    depth,
    path
FROM graph_walk;
```

This shows two defensive mechanisms:

```text
cycle guard
+
maximum depth
```

---

# 51. Why Use Both a Cycle Guard and Depth Limit?

A cycle guard protects semantic traversal.

A depth limit protects operational resources.

Even if the model is expected to be acyclic, a defensive depth limit can prevent an unexpected data corruption event from consuming unbounded resources.

The depth limit must be chosen intentionally.

Do not hide business requirements behind an arbitrary number.

---

# 52. Recursion Depth

Track:

```sql
depth
```

during recursion.

This gives you:

- hierarchy level,
- traversal length,
- debugging visibility,
- a possible safety bound.

Example:

```sql
WHERE h.depth < 20
```

can prevent traversal past level 20.

But ask:

> Is 20 really a valid business boundary?

A safety control should not silently change a valid result set.

---

# 53. Recursion Termination Checklist

Every recursive CTE should answer:

```text
Anchor:
What are the starting rows?

Recursive member:
How are the next rows generated?

Termination:
Why does recursion eventually stop?

Cycle protection:
What happens if a node repeats?

Depth limit:
What is the operational safety bound?

Output grain:
What does one recursive row represent?
```

If you cannot answer these questions, the recursive SQL is not ready for production.

---

# 54. generate_series

`generate_series` is useful for generating sequences.

PostgreSQL supports it directly.

Example:

```sql
SELECT *
FROM generate_series(
    DATE '2025-03-01',
    DATE '2025-03-07',
    INTERVAL '1 day'
);
```

It can generate dates or numeric sequences, with syntax adapted to the target type.

DuckDB also supports series-generation functionality, but exact syntax and return types can differ by version and context.

Verify the installed engine documentation.

---

# 55. Date Spines

A **date spine** is a complete sequence of dates used as the backbone of a time-based report.

Suppose actual events exist on:

```text
March 1
March 3
March 6
```

A complete date spine is:

```text
March 1
March 2
March 3
March 4
March 5
March 6
```

The spine gives the report a row even when no event occurred.

---

# 56. Building a Date Spine

PostgreSQL-style example:

```sql
WITH date_spine AS (
    SELECT
        gs::date AS day
    FROM generate_series(
        DATE '2025-03-01',
        DATE '2025-03-31',
        INTERVAL '1 day'
    ) AS gs
),
daily AS (
    SELECT
        created_at::date AS day,
        SUM(amount) AS revenue
    FROM orders
    GROUP BY created_at::date
)
SELECT
    ds.day,
    COALESCE(d.revenue, 0) AS revenue
FROM date_spine AS ds
LEFT JOIN daily AS d
    ON d.day = ds.day
ORDER BY ds.day;
```

---

# 57. Why the Date Spine Works

Without a date spine:

```text
March 1 → revenue
March 3 → revenue
March 6 → revenue
```

Days without activity have no row.

With the date spine:

```text
March 1 → revenue
March 2 → 0
March 3 → revenue
March 4 → 0
March 5 → 0
March 6 → revenue
```

The LEFT JOIN preserves every date from the spine.

---

# 58. Grain of a Date-Spine Pipeline

For:

```sql
WITH date_spine AS (...)
```

the grain is:

```text
one row per date
```

For:

```sql
daily AS (...)
```

the grain is also:

```text
one row per date
```

For the final result:

```text
one row per date
```

This compatibility makes the join straightforward.

---

# 59. Missing Dates vs Zero Revenue

This distinction is important.

Before the LEFT JOIN:

```text
missing date
→ no daily row
```

After:

```sql
COALESCE(d.revenue, 0)
```

you may produce:

```text
date exists
revenue = 0
```

This is useful when the business wants every date represented.

But again:

> **A missing row and a known zero are not inherently the same semantic state.**

The report contract determines whether the conversion is correct.

---

# 60. Date-Spine Boundary Safety

Be deliberate about the range.

For a full month:

```text
2025-03-01
through
2025-03-31
```

or, for timestamp generation, a half-open pattern may be easier to reason about.

For timestamp event extraction, use the previously established principle:

```sql
ts >= start
AND ts < end
```

Do not accidentally create an incomplete day or duplicate boundary.

---

# 61. Recursive Alternatives to generate_series

Recursive CTEs can generate sequences.

Conceptually:

```sql
WITH RECURSIVE dates AS (
    SELECT DATE '2025-03-01' AS day

    UNION ALL

    SELECT day + INTERVAL '1 day'
    FROM dates
    WHERE day < DATE '2025-03-31'
)
SELECT
    day
FROM dates;
```

This teaches recursion clearly:

```text
anchor:
March 1

recursive member:
add one day

termination:
stop after March 31
```

---

# 62. generate_series vs Recursive Date Generation

Use `generate_series` when it is supported and expresses the task directly.

Use a recursive CTE when:

- the recursion itself is part of the learning/problem,
- the next value depends on previous state in a more complex way,
- you need to demonstrate recursive logic,
- another traversal-like requirement exists.

Do not use recursion simply because it is more complicated.

The simplest correct set generator is usually easier to review.

---

# 63. CTE Materialization

A critical advanced concept:

> **A CTE is a logical query construct. It is not automatically a physical temporary table.**

Do not think:

```text
CTE
=
always materialized table
```

and do not think:

```text
CTE
=
always inlined
```

Physical behavior depends on the engine and the query.

---

# 64. PostgreSQL CTE Inlining

In PostgreSQL, non-recursive CTEs may be folded into the surrounding query under conditions where the optimizer considers inlining appropriate.

The practical lesson is:

> Writing a CTE does not automatically mean PostgreSQL will execute it as a separately materialized intermediate table.

This gives the optimizer freedom to apply transformations.

---

# 65. MATERIALIZED

PostgreSQL supports:

```sql
WITH customer_totals AS MATERIALIZED (
    SELECT
        customer_id,
        SUM(amount) AS total_spend
    FROM orders
    GROUP BY customer_id
)
SELECT *
FROM customer_totals;
```

`MATERIALIZED` asks PostgreSQL to treat the CTE as a materialization boundary.

---

## 65.1 When materialization can help

Conceptually useful cases can include:

- an expensive intermediate result is referenced multiple times,
- you intentionally want to avoid repeated recomputation,
- you need an optimizer boundary for a specific reason.

But this can also introduce:

- extra storage work,
- memory usage,
- I/O,
- fewer opportunities for predicate pushdown,
- fewer optimizer transformations.

Therefore:

> **Materialized is not synonymous with faster.**

---

# 66. NOT MATERIALIZED

PostgreSQL also supports:

```sql
WITH customer_totals AS NOT MATERIALIZED (
    SELECT
        customer_id,
        SUM(amount) AS total_spend
    FROM orders
    GROUP BY customer_id
)
SELECT *
FROM customer_totals;
```

This encourages treatment as an inlineable query expression rather than forcing materialization.

Potential benefits include more optimizer freedom.

Potential costs depend on how the expression is reused and transformed.

Again:

> **Use it deliberately and measure when performance matters.**

---

# 67. When Materialization Can Hurt

Suppose a CTE has:

```text
1 billion intermediate rows
```

but the outer query only needs:

```text
1,000 rows
```

If materialization prevents a useful filter from being pushed down, the engine may do unnecessary work.

This is why the optimizer's ability to transform the query can be valuable.

---

# 68. When NOT MATERIALIZED Can Hurt

Inlining can also have trade-offs.

If an expensive expression is referenced multiple times, allowing repeated inlining can potentially repeat work depending on the final plan.

The right choice depends on:

```text
query structure
+
reuse
+
selectivity
+
optimizer behavior
+
data volume
```

There is no universal:

```text
MATERIALIZED = good
NOT MATERIALIZED = good
```

rule.

---

# 69. Recursive CTEs and Materialization

Recursive CTEs are a separate category from ordinary CTE inlining.

Do not generalize ordinary non-recursive CTE behavior to recursive traversal.

The recursive execution process inherently depends on accumulated recursive results.

---

# 70. PostgreSQL vs DuckDB

Keep semantics and engine implementation separate.

| Area | PostgreSQL | DuckDB | Engineering note |
|---|---|---|---|
| Ordinary CTEs | Supported | Supported | Core SQL pattern |
| Recursive CTEs | Supported | Supported | Verify exact version behavior where needed |
| `MATERIALIZED` / `NOT MATERIALIZED` | PostgreSQL supports these controls | Do not assume identical syntax/behavior | Engine-specific |
| `generate_series` | Supported | Series-generation functionality is supported, with syntax/details to verify | Check exact version |
| `EXISTS` / `IN` | Supported | Supported | Common semantics |
| Derived tables | Supported | Supported | Common SQL |
| DuckDB analytical conveniences | Rich analytical SQL support | Strong | Verify dialect specifics |
| dbt-style CTE thinking | Useful conceptually | Useful conceptually | CTE structure is not dbt itself |

When behavior is version-sensitive:

> **Verify the exact installed engine version and documentation.**

---

# 71. CTE Readability Rules

CTEs are often introduced to improve readability.

They can also become unreadable if used carelessly.

---

## Rule 1 — Name by contents

Prefer:

```text
clean_orders
customer_totals
active_customers
daily_revenue
```

over:

```text
tmp1
step2
foo
x
```

A reader should understand what a CTE represents without opening every line.

---

## Rule 2 — One primary purpose per CTE

Good:

```text
clean_orders
→ remove invalid records

customer_totals
→ aggregate by customer

final_metrics
→ calculate final output
```

Poor:

```text
step1
→ filters
→ joins
→ aggregates
→ renames
→ business rules
→ unrelated formatting
```

The second style makes debugging harder.

---

# 72. CTE Length and Complexity

There is no universal line-count threshold.

The useful engineering question is:

> Can another engineer understand the CTE's purpose, grain, and invariants without reverse-engineering a giant block?

A very long CTE may deserve decomposition.

But do not split every two-line expression into its own CTE.

The goal is:

```text
clarity
+
appropriate granularity
```

not maximal fragmentation.

---

# 73. CTE Naming and Grain

A powerful convention is to name CTEs by their semantic level.

Examples:

```text
raw_orders
clean_orders
enriched_orders
daily_orders
customer_totals
active_customers
monthly_customer_metrics
```

The name should help communicate the grain.

For example:

```text
customer_totals
```

suggests:

```text
one row per customer
```

provided the implementation matches the name.

---

# 74. CTE vs Temporary Table vs View

| Tool | Scope | Typical purpose | Physical storage | Good fit |
|---|---|---|---|---|
| CTE | one statement | named transformation stage | engine-dependent | complex single-statement SQL |
| TEMP TABLE | session/transaction scope depending on engine | reusable intermediate result | physical table | multi-step workflows and debugging |
| VIEW | persistent database object | reusable logical query interface | generally logical | stable semantic interface |
| MATERIALIZED VIEW | persistent object | precomputed reusable result | physical | repeated expensive query results |

The exact lifecycle and locking semantics differ by engine.

---

# 75. When to Use a CTE

CTEs are a strong choice when:

- a single statement has several logical steps,
- each stage has a clear purpose,
- you need to track grain transitions,
- the query benefits from named intermediate relations,
- the intermediate result is not needed by separate statements.

---

# 76. When a TEMP TABLE May Be Better

A temporary table can be more appropriate when:

- multiple statements need the same intermediate result,
- you need to inspect intermediate data interactively,
- a transformation is naturally staged across several SQL statements,
- a very large intermediate dataset benefits from being explicitly stored,
- debugging requires a persistent session-local checkpoint.

Do not create temp tables just because a query has more than one logical step.

---

# 77. When a VIEW May Be Better

A view is often appropriate when you need:

- a reusable semantic interface,
- multiple consumers,
- centralized SQL logic,
- a stable relation definition.

But a view can also hide complexity.

A downstream engineer may query:

```sql
SELECT *
FROM customer_metrics;
```

without realizing the view itself contains multiple joins and transformations.

Therefore document important view semantics.

---

# 78. Materialized View

A materialized view stores a precomputed result.

This can be useful for expensive queries that are repeatedly consumed.

The trade-off is:

```text
faster reads
+
refresh complexity
+
storage
+
staleness
```

Materialized views are conceptually different from ordinary CTEs because they are persistent database objects.

---

# 79. Production Transformation Pattern — Customer Spend Above Average

Requirement:

> Find customers whose total spend is above the average customer spend.

### Pattern A — CTE

```sql
WITH customer_totals AS (
    SELECT
        customer_id,
        SUM(amount) AS total_spend
    FROM orders
    GROUP BY customer_id
)
SELECT
    customer_id,
    total_spend
FROM customer_totals
WHERE total_spend > (
    SELECT AVG(total_spend)
    FROM customer_totals
);
```

### Grain

```text
orders
→ one row per order

customer_totals
→ one row per customer

final
→ one row per customer above the average
```

The scalar subquery is operating over the already-created customer-level relation.

---

# 80. Production Transformation Pattern — Date Spine

```sql
WITH date_spine AS (
    SELECT
        gs::date AS day
    FROM generate_series(
        DATE '2025-03-01',
        DATE '2025-03-31',
        INTERVAL '1 day'
    ) AS gs
),
daily AS (
    SELECT
        created_at::date AS day,
        SUM(amount) AS revenue
    FROM orders
    GROUP BY created_at::date
)
SELECT
    ds.day,
    COALESCE(d.revenue, 0) AS revenue
FROM date_spine AS ds
LEFT JOIN daily AS d
    ON d.day = ds.day
ORDER BY ds.day;
```

Grain:

```text
date_spine
→ one row per date

daily
→ one row per date

final
→ one row per date
```

---

# 81. Production Transformation Pattern — Recursive Hierarchy

```text
employees
    ↓
employee_tree
    ↓
depth / path
    ↓
final hierarchy result
```

The CTE should document:

```text
anchor:
root employees

recursive member:
children of discovered employees

termination:
no further child matches

cycle protection:
prevent already visited IDs from repeating

depth:
track hierarchy level
```

---

# 82. Production Transformation Pattern — Multi-Stage Gold Transformation

A useful structure is:

```text
raw_orders
     ↓
clean_orders
     ↓
enriched_orders
     ↓
daily_customer_metrics
     ↓
gold_customer_metrics
```

Example:

```sql
WITH raw_orders AS (
    SELECT
        order_id,
        customer_id,
        created_at,
        amount,
        status
    FROM source_orders
),
clean_orders AS (
    SELECT
        order_id,
        customer_id,
        created_at,
        amount
    FROM raw_orders
    WHERE status = 'completed'
      AND order_id IS NOT NULL
      AND customer_id IS NOT NULL
),
enriched_orders AS (
    SELECT
        co.*,
        c.country
    FROM clean_orders AS co
    JOIN customers AS c
        ON c.customer_id = co.customer_id
),
daily_customer_metrics AS (
    SELECT
        customer_id,
        country,
        created_at::date AS day,
        SUM(amount) AS revenue,
        COUNT(*) AS order_count
    FROM enriched_orders
    GROUP BY
        customer_id,
        country,
        created_at::date
)
SELECT
    customer_id,
    country,
    day,
    revenue,
    order_count
FROM daily_customer_metrics;
```

---

## 82.1 Grain map

```text
raw_orders
→ one row per source order

clean_orders
→ one row per valid completed order

enriched_orders
→ one row per valid completed order + customer attributes

daily_customer_metrics
→ one row per customer per country per day
```

The final SQL becomes easier to review because each step has a recognizable contract.

---

# 83. Debugging Subqueries

When a subquery returns an unexpected result:

## Step 1

Run the inner query by itself.

---

## Step 2

Inspect its row count.

---

## Step 3

Inspect its columns.

---

## Step 4

Check NULLs.

---

## Step 5

Check duplicates.

---

## Step 6

Determine whether it is supposed to return:

```text
one value
many rows
existence
membership
```

---

## Step 7

Check correlation.

Ask:

> Does this subquery reference the outer query?

---

## Step 8

Rewrite temporarily as a derived table or CTE if it helps inspect the relation.

---

# 84. Debugging a Scalar Subquery

Suppose this fails:

```sql
SELECT
    customer_id,
    (
        SELECT order_id
        FROM orders
        WHERE orders.customer_id = customers.customer_id
    ) AS order_id
FROM customers;
```

The question is:

> Can a customer have multiple orders?

If yes, then the scalar subquery is not scalar.

The business requirement may instead be:

> latest order.

Then define it:

```sql
SELECT
    c.customer_id,
    (
        SELECT o.order_id
        FROM orders AS o
        WHERE o.customer_id = c.customer_id
        ORDER BY o.created_at DESC, o.order_id DESC
        LIMIT 1
    ) AS latest_order_id
FROM customers AS c;
```

Now the cardinality is intentionally one row.

---

# 85. Debugging IN

If an IN query gives unexpected results:

1. Run the subquery.
2. Inspect distinct values.
3. Check for NULLs.
4. Check whether the outer value can be NULL.
5. Compare to EXISTS.

Example:

```sql
SELECT DISTINCT customer_id
FROM orders;
```

Then:

```sql
SELECT
    c.customer_id
FROM customers AS c
WHERE c.customer_id IN (
    SELECT o.customer_id
    FROM orders AS o
);
```

---

# 86. Debugging EXISTS

For a correlated EXISTS:

```sql
WHERE EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.customer_id
)
```

test the inner relationship for one known customer:

```sql
SELECT *
FROM orders
WHERE customer_id = 123;
```

Then ask:

```text
Should this customer produce TRUE or FALSE?
```

This makes correlated logic much easier to reason about.

---

# 87. Debugging CTE Pipelines

Suppose:

```text
raw
 ↓
clean
 ↓
join
 ↓
aggregate
 ↓
final
```

Do not inspect only the final output.

Instead inspect each stage.

---

## Stage 1

```sql
SELECT *
FROM raw_orders
LIMIT 20;
```

---

## Stage 2

```sql
SELECT *
FROM clean_orders
LIMIT 20;
```

---

## Stage 3

```sql
SELECT *
FROM enriched_orders
LIMIT 20;
```

---

## Stage 4

```sql
SELECT *
FROM customer_totals
LIMIT 20;
```

For each stage ask:

```text
What is the row count?
What is the grain?
What changed?
What invariant should hold?
```

---

# 88. CTE Pipeline Validation

A useful test matrix is:

| Stage | Expected grain | Example invariant |
|---|---|---|
| `raw_orders` | one row/source event | source row count known |
| `clean_orders` | one row/valid order | no NULL order ID |
| `enriched_orders` | one row/order | no unexpected join multiplication |
| `customer_totals` | one row/customer | unique customer ID |
| `final` | defined reporting grain | no duplicate business keys |

This is how you turn a CTE chain into a testable transformation.

---

# 89. Assertion Queries

Assertions should return zero rows when the invariant holds.

## Duplicate customer totals

```sql
SELECT
    customer_id,
    COUNT(*) AS row_count
FROM customer_totals
GROUP BY customer_id
HAVING COUNT(*) > 1;
```

Expected:

```text
0 rows
```

---

## Unexpected NULL order ID

```sql
SELECT *
FROM clean_orders
WHERE order_id IS NULL;
```

Expected:

```text
0 rows
```

---

## Date-spine duplicates

```sql
SELECT
    day,
    COUNT(*) AS row_count
FROM date_spine
GROUP BY day
HAVING COUNT(*) > 1;
```

Expected:

```text
0 rows
```

---

# 90. Recursive Assertion Examples

Suppose every employee should appear at most once in a tree.

Then:

```sql
SELECT
    employee_id,
    COUNT(*) AS row_count
FROM employee_tree
GROUP BY employee_id
HAVING COUNT(*) > 1;
```

This may expose multiple paths or multiple roots.

But do not assume duplicates are automatically wrong in graph traversal.

If one node can legitimately be reachable by multiple paths, the correct invariant may be:

```text
unique (start_node, path, node)
```

The assertion must match the intended traversal grain.

---

# 91. Common Mistakes

## Mistake 1 — Scalar subquery returns multiple rows

### Broken

```sql
SELECT (
    SELECT customer_id
    FROM customers
);
```

### Why it fails

The scalar position expects one value.

### Fix

Aggregate, filter to one logically defined row, or use a relation/existence form instead.

### Lesson

Know expected cardinality.

---

## Mistake 2 — JOIN used for existence testing

### Broken idea

```sql
SELECT c.*
FROM customers AS c
JOIN orders AS o
    ON o.customer_id = c.customer_id;
```

### Problem

Customers with multiple orders are duplicated.

### Better

```sql
WHERE EXISTS (...)
```

when existence is all you need.

---

## Mistake 3 — DISTINCT used to hide the JOIN

`DISTINCT` may hide the symptom without making the semantics clearer.

Use it only when the final relation genuinely means:

```text
distinct rows
```

---

## Mistake 4 — NOT IN + NULL

A nullable subquery can turn negative membership into UNKNOWN.

Use a NULL-aware design, often `NOT EXISTS` for relationship-based anti-membership.

---

## Mistake 5 — Assuming IN and EXISTS are identical in all cases

They can be equivalent under some conditions, but NULL and correlation semantics matter.

---

## Mistake 6 — Assuming correlated subqueries always execute row-by-row physically

That is a logical teaching model, not a physical-plan guarantee.

Optimizers can decorrelate.

---

## Mistake 7 — Assuming correlated subqueries are always slow

They are not.

Performance depends on the actual query and engine.

---

## Mistake 8 — Assuming all CTEs materialize

They do not.

CTEs are logical query constructs, and engines can inline or otherwise optimize them.

---

## Mistake 9 — Assuming all CTEs are inlined

They are not guaranteed to be.

PostgreSQL can be influenced by `MATERIALIZED` and `NOT MATERIALIZED`, and engine behavior differs.

---

## Mistake 10 — CTEs with meaningless names

```text
x
tmp
step2
```

do not communicate the data model.

---

## Mistake 11 — CTEs that are too long

A CTE containing unrelated transformations is hard to review.

Split by logical responsibility.

---

## Mistake 12 — Losing grain across CTEs

If you do not document grain, it becomes easy to join or aggregate at the wrong level.

---

## Mistake 13 — Recursive CTE without termination

A recursion must have a clear stop condition.

---

## Mistake 14 — Recursive CTE without cycle protection

A corrupted hierarchy or graph cycle can create unbounded traversal.

---

## Mistake 15 — Arbitrary recursion limit

A depth limit that is too low can silently cut valid data.

A limit that is too high may fail to protect resources.

---

## Mistake 16 — Date spine boundary errors

An incorrect start/end range can omit or duplicate dates.

---

## Mistake 17 — Treating missing dates as zero automatically

The business may distinguish:

```text
no observation
```

from:

```text
known zero
```

---

## Mistake 18 — Using recursion for simple sequence generation

If `generate_series` clearly expresses the task, recursive SQL can add unnecessary complexity.

---

## Mistake 19 — Forcing MATERIALIZED without measuring

Materialization can add work and prevent useful optimization.

---

## Mistake 20 — Choosing a temp table when a CTE is enough

Temp tables introduce a physical staging object when a single statement would suffice.

---

## Mistake 21 — Creating views to hide local complexity

A view can become a hidden dependency and make downstream logic harder to trace.

---

# 92. Hands-On Exercises

---

## Exercise 1 — Spend Above Average

### Objective

Solve the same business problem with different SQL structures.

### Requirement

> Find customers whose total spend is above the average customer spend.

### Input grain

```text
one row per order
```

### Expected intermediate grain

```text
one row per customer
```

### Task A — Scalar subquery

First create customer totals:

```sql
SELECT
    customer_id,
    SUM(amount) AS total_spend
FROM orders
GROUP BY customer_id;
```

Then compare each total with a scalar aggregate.

### Task B — CTE

```sql
WITH customer_totals AS (
    SELECT
        customer_id,
        SUM(amount) AS total_spend
    FROM orders
    GROUP BY customer_id
)
SELECT
    customer_id,
    total_spend
FROM customer_totals
WHERE total_spend > (
    SELECT AVG(total_spend)
    FROM customer_totals
);
```

### Expected reasoning

Explain:

```text
orders
→ customer_totals
→ scalar average
→ filtered customer result
```

### Production lesson

The important part is not whether the average is written as a scalar subquery. It is that the comparison occurs at customer grain.

---

# Exercise 2 — Zero-Revenue Days

### Objective

Build a complete date spine.

### Input grain

```text
one row per order
```

### Output grain

```text
one row per calendar day
```

### Task

Generate March 2025 dates and left join daily revenue.

### Required edge cases

Test:

- day with orders,
- day with no orders,
- first day,
- last day.

### Solution

```sql
WITH date_spine AS (
    SELECT
        gs::date AS day
    FROM generate_series(
        DATE '2025-03-01',
        DATE '2025-03-31',
        INTERVAL '1 day'
    ) AS gs
),
daily AS (
    SELECT
        created_at::date AS day,
        SUM(amount) AS revenue
    FROM orders
    GROUP BY created_at::date
)
SELECT
    ds.day,
    COALESCE(d.revenue, 0) AS revenue
FROM date_spine AS ds
LEFT JOIN daily AS d
    ON d.day = ds.day
ORDER BY ds.day;
```

### Production lesson

The date spine creates the required reporting grain before joining observations.

---

# Exercise 3 — Recursive Category Hierarchy

### Objective

Build hierarchical paths.

### Setup

```text
category_id | category_name | parent_category_id
------------+---------------+-------------------
10          | Electronics   | NULL
20          | Phones        | 10
30          | Android       | 20
40          | iPhone        | 20
```

### Task

Return:

```text
category_id
category_name
depth
path
```

### Required recursion-safety documentation

```text
Anchor:
root categories

Recursive member:
children of discovered categories

Termination:
no additional child rows

Cycle protection:
prevent revisiting an existing category

Depth:
track hierarchy depth
```

### Production lesson

Hierarchy traversal must be explicit about its termination and cycle behavior.

---

# Exercise 4 — Five-Step CTE Pipeline

### Objective

Build a transformation that resembles a warehouse staging pipeline.

### Required stages

```text
raw
→ clean
→ enrich
→ aggregate
→ final
```

### Task

Each stage must state:

```text
purpose
input grain
output grain
```

### Example structure

```sql
WITH raw_orders AS (
    ...
),
clean_orders AS (
    ...
),
enriched_orders AS (
    ...
),
customer_totals AS (
    ...
),
final AS (
    ...
)
SELECT *
FROM final;
```

### Production lesson

Every CTE is a named transformation contract.

---

# Exercise 5 — EXISTS vs JOIN

### Objective

Understand duplicate-sensitive semantics.

### Setup

```text
Customer 1 → 5 orders
Customer 2 → 1 order
Customer 3 → 0 orders
```

### Task

Return customers who have at least one order using:

```text
JOIN
IN
EXISTS
```

Predict output before running.

### Expected result

All three approaches can express the same entity-level requirement under appropriate semantics, but JOIN may need DISTINCT to remove multiplicity.

### Production lesson

Use a construct that expresses the actual business question.

---

# Exercise 6 — NULL Semantics

### Objective

Compare membership and existence under NULL.

### Setup

```text
outer customers:
1
2
3

subquery values:
2
NULL
```

### Task

Compare:

```sql
IN
NOT IN
EXISTS
NOT EXISTS
```

### Requirement

Explain each result using:

```text
TRUE
FALSE
UNKNOWN
```

### Production lesson

Negative membership is especially sensitive to NULL.

---

# Exercise 7 — Correlated Subquery

### Objective

Understand correlation and rewriting.

### Task

Calculate customer spend using:

```sql
SELECT
    c.customer_id,
    (
        SELECT SUM(o.amount)
        FROM orders AS o
        WHERE o.customer_id = c.customer_id
    ) AS total_spend
FROM customers AS c;
```

Then rewrite it using:

```text
CTE
+
JOIN
```

### Compare

- semantics,
- grain,
- readability,
- performance considerations.

Do not claim one is always faster.

---

# Exercise 8 — Recursive Employee Hierarchy

### Objective

Build:

```text
employee
manager
depth
path
```

### Required

Include:

- root employees,
- recursive child lookup,
- depth,
- path,
- cycle protection,
- maximum depth.

---

# Exercise 9 — Graph Reachability

### Objective

Find every node reachable from a starting node.

### Setup

```text
A → B
B → C
C → D
```

Add a cycle:

```text
D → B
```

### Task

Return reachable nodes without infinite recursion.

### Required

Track:

```text
node
depth
path
```

### Production lesson

Graph data must be treated as potentially cyclic unless the data model guarantees acyclicity and validates it.

---

# Exercise 10 — CTE Materialization Reasoning

### Objective

Understand optimizer trade-offs.

### Task

Construct a query where a costly intermediate CTE is logically referenced more than once.

Discuss:

```text
MATERIALIZED
NOT MATERIALIZED
default behavior
```

### Requirement

Do not create a benchmark file.

Reason about:

```text
reuse
intermediate size
filter pushdown
optimizer freedom
storage/I/O
```

Then state what you would measure in a real production investigation.

---

# 93. Beginner Practice

## 1. Scalar average

Use a scalar subquery to display the global average order amount.

---

## 2. Compare to scalar

Find orders whose amount exceeds the global average.

---

## 3. Derived table

Create customer totals in a subquery in FROM.

---

## 4. IN

Find customers who appear in orders.

---

## 5. EXISTS

Find customers for whom at least one order exists.

---

## 6. Simple CTE

Create:

```text
clean_orders
```

that filters completed orders.

---

## 7. Two-CTE chain

Build:

```text
clean_orders
→ customer_totals
```

---

## 8. Grain identification

For each query, state:

```text
input grain
output grain
```

---

## 9. Inner-query debugging

Run a subquery separately and inspect its row count.

---

## 10. Membership semantics

Create duplicate values in the subquery and explain why IN does not duplicate the outer rows.

Every beginner exercise should be solved by explaining the intermediate relation, not merely by typing syntax.

---

# 94. Intermediate Practice

## 1. Correlated count

Calculate order count per customer using a correlated subquery.

---

## 2. Correlated rewrite

Rewrite the previous query as:

```text
CTE + JOIN
```

---

## 3. EXISTS vs JOIN

Return customers with completed orders using both forms.

---

## 4. IN vs EXISTS

Use duplicate order data and compare results.

---

## 5. NULL-sensitive membership

Add NULL to the subquery and compare IN/NOT IN.

---

## 6. Date spine

Create a one-month date spine and attach daily revenue.

---

## 7. Missing-day report

Ensure days without activity still appear.

---

## 8. Multi-stage CTE

Build:

```text
raw → clean → enrich → aggregate
```

---

## 9. Assertions

Write zero-row tests for every major stage.

---

## 10. Debugging

Take a multi-CTE query and inspect each CTE independently.

---

# 95. Advanced Practice

## 1. Recursive hierarchy

Build a full employee tree with depth and path.

---

## 2. Category traversal

Return complete category paths.

---

## 3. Graph walk

Find all reachable nodes from a starting node.

---

## 4. Cycle protection

Introduce a cycle and prevent repeated traversal.

---

## 5. Depth limit

Add a maximum recursion depth and explain the business trade-off.

---

## 6. Recursive date generation

Build a date sequence without `generate_series`.

---

## 7. Date-spine comparison

Compare recursive date generation with `generate_series`.

---

## 8. MATERIALIZED

Analyze a repeated expensive CTE and explain when materialization could help.

---

## 9. NOT MATERIALIZED

Explain when optimizer freedom could be more useful than a materialized boundary.

---

## 10. Architecture choice

Given a multi-step transformation, choose between:

```text
CTE
TEMP TABLE
VIEW
MATERIALIZED VIEW
```

and defend the choice based on:

```text
scope
reuse
debugging
performance
freshness
maintainability
```

---

# 96. Recursive CTE Challenges

## Challenge 1 — Employee hierarchy

### Input

```text
employee_id
employee_name
manager_id
```

### Task

Produce:

```text
employee
depth
path
```

### Termination

A leaf employee has no children.

### Cycle safety

Protect against an employee indirectly managing themselves.

---

# Challenge 97 — Category Tree

### Task

Generate:

```text
Electronics > Phones > Android
```

### Required

Track:

```text
depth
path
```

### Edge case

Introduce:

```text
Android → Electronics
```

as a bad data cycle.

Prevent infinite traversal.

---

# 98. Graph Reachability

### Task

Given:

```text
A → B
B → C
C → D
D → E
```

find all reachable nodes from A.

Then add:

```text
E → B
```

and prevent cycles.

---

# 99. Cycle Detection

### Task

Return enough information to show:

```text
A → B → C → A
```

contains a cycle.

### Production lesson

Do not merely stop recursion; make it possible to diagnose the bad data.

---

# 100. Depth-Limited Traversal

### Task

Return at most:

```text
depth <= 5
```

### Discussion

Explain:

```text
semantic boundary
vs
resource-safety boundary
```

---

# 101. Full Path String

### Task

Return:

```text
CEO > VP Engineering > Engineer A
```

for each employee.

### Edge cases

- NULL names,
- special characters,
- very deep hierarchy.

---

# 102. Leaf Nodes

### Task

Find categories with no children.

A recursive hierarchy can be filtered against the base table to identify leaf nodes.

---

# 103. Descendant Counts

### Task

For each manager, count the number of descendants.

Explain why the recursive output grain matters.

---

# 104. Debugging Challenges

## Challenge 1 — Scalar subquery returns multiple rows

Broken:

```sql
SELECT
    c.customer_id,
    (
        SELECT o.order_id
        FROM orders AS o
        WHERE o.customer_id = c.customer_id
    ) AS order_id
FROM customers AS c;
```

### Symptoms

The query fails when a customer has multiple orders.

### Root cause

The inner query is not scalar.

### Investigation

```sql
SELECT
    customer_id,
    COUNT(*)
FROM orders
GROUP BY customer_id
HAVING COUNT(*) > 1;
```

### Corrected approach

Define the intended one row:

```sql
SELECT
    c.customer_id,
    (
        SELECT o.order_id
        FROM orders AS o
        WHERE o.customer_id = c.customer_id
        ORDER BY o.created_at DESC, o.order_id DESC
        LIMIT 1
    ) AS latest_order_id
FROM customers AS c;
```

### Lesson

`LIMIT 1` is correct only when the ordering expresses a real business rule.

---

# Challenge 2 — JOIN duplicates entities

Broken:

```sql
SELECT
    c.customer_id
FROM customers AS c
JOIN orders AS o
    ON o.customer_id = c.customer_id;
```

### Symptoms

Customers repeat.

### Root cause

The relationship is one customer to many orders.

### Correction

```sql
WHERE EXISTS (...)
```

when only existence is required.

---

# Challenge 3 — NOT IN + NULL

Broken:

```sql
SELECT
    c.customer_id
FROM customers AS c
WHERE c.customer_id NOT IN (
    SELECT o.customer_id
    FROM orders AS o
);
```

### Symptom

Unexpectedly few or no rows.

### Investigation

```sql
SELECT *
FROM orders
WHERE customer_id IS NULL;
```

### Correction

Use:

```sql
WHERE NOT EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.customer_id
)
```

when the requirement is anti-membership.

---

# Challenge 4 — Correlated alias mistake

Broken:

```sql
SELECT
    c.customer_id,
    (
        SELECT COUNT(*)
        FROM orders AS o
        WHERE o.customer_id = x.customer_id
    ) AS order_count
FROM customers AS c;
```

### Root cause

The correlated reference uses the wrong outer alias.

### Fix

```sql
WHERE o.customer_id = c.customer_id
```

### Lesson

Correlated references must be traceable.

---

# Challenge 5 — CTE grain unexpectedly changes

Suppose:

```sql
WITH clean_orders AS (
    SELECT *
    FROM orders
),
customer_totals AS (
    SELECT
        customer_id,
        SUM(amount) AS total_spend
    FROM clean_orders
    GROUP BY customer_id
)
SELECT *
FROM customer_totals
JOIN orders
    USING (customer_id);
```

### Symptom

Customer totals repeat once per order.

### Root cause

`customer_totals` is customer grain, then it is joined back to order grain.

### Lesson

A CTE's grain does not determine the final query's grain automatically. Every downstream join must be reasoned about.

---

# Challenge 6 — Date spine missing days

Broken:

```sql
SELECT
    created_at::date AS day,
    SUM(amount)
FROM orders
GROUP BY created_at::date;
```

### Symptom

Days with no orders are absent.

### Fix

Create a date spine and LEFT JOIN daily activity.

---

# Challenge 7 — Recursive CTE never terminates

Broken graph:

```text
A → B
B → C
C → A
```

### Root cause

Cycle with no stopping condition.

### Fix

Track visited nodes and prevent revisiting them.

---

# Challenge 8 — Recursive CTE follows a cycle

The query has a depth limit but no cycle detection.

### Problem

The same nodes may be repeatedly emitted until the arbitrary depth boundary is reached.

### Fix

Add a path-based cycle guard.

### Lesson

Depth limits and cycle protection solve different problems.

---

# Challenge 9 — CTE materialization assumption is wrong

### Symptom

An engineer expected:

```text
CTE = stored intermediate result
```

but the engine optimized it differently.

### Root cause

CTE syntax describes a logical relation, not a universal materialization contract.

### Fix

Read the engine's plan and documentation before making performance assumptions.

---

# Challenge 10 — Unreadable CTE chain

Bad:

```text
a
b
c
d
e
```

with each CTE performing unrelated work.

### Fix

Rename and restructure:

```text
raw_orders
clean_orders
enriched_orders
daily_customer_metrics
final
```

Each stage gets one primary purpose.

---

# 105. Production Case Study

## 105.1 Scenario

A subscription/e-commerce system contains:

```text
customers
orders
order_lines
payments
categories
employees
```

The analytics team needs:

1. customers whose total spend exceeds the average customer spend;
2. daily revenue including zero-activity days;
3. category hierarchy paths;
4. customer existence checks;
5. a multi-stage gold-layer transformation.

---

# 106. Case Study Part 1 — Customer Spend Above Average

### Input grain

```text
one row per order
```

### Stage 1

```sql
WITH customer_totals AS (
    SELECT
        customer_id,
        SUM(amount) AS total_spend
    FROM orders
    GROUP BY customer_id
)
```

### Grain

```text
one row per customer
```

### Stage 2

```sql
SELECT
    customer_id,
    total_spend
FROM customer_totals
WHERE total_spend > (
    SELECT AVG(total_spend)
    FROM customer_totals
);
```

The scalar subquery operates at customer-total grain.

---

# 107. Case Study Part 2 — Zero-Activity Days

```sql
WITH date_spine AS (
    SELECT
        gs::date AS day
    FROM generate_series(
        DATE '2025-03-01',
        DATE '2025-03-31',
        INTERVAL '1 day'
    ) AS gs
),
daily_revenue AS (
    SELECT
        created_at::date AS day,
        SUM(amount) AS revenue
    FROM orders
    GROUP BY created_at::date
)
SELECT
    ds.day,
    COALESCE(dr.revenue, 0) AS revenue
FROM date_spine AS ds
LEFT JOIN daily_revenue AS dr
    ON dr.day = ds.day
ORDER BY ds.day;
```

Grain:

```text
date_spine
→ one row/day

daily_revenue
→ one row/day

final
→ one row/day
```

---

# 108. Case Study Part 3 — Category Paths

```sql
WITH RECURSIVE category_tree AS (
    SELECT
        category_id,
        category_name,
        parent_category_id,
        0 AS depth,
        CAST(category_name AS TEXT) AS path,
        ARRAY[category_id] AS visited
    FROM categories
    WHERE parent_category_id IS NULL

    UNION ALL

    SELECT
        c.category_id,
        c.category_name,
        c.parent_category_id,
        ct.depth + 1,
        ct.path || ' > ' || c.category_name,
        ct.visited || c.category_id
    FROM categories AS c
    JOIN category_tree AS ct
        ON c.parent_category_id = ct.category_id
    WHERE NOT c.category_id = ANY(ct.visited)
      AND ct.depth < 100
)
SELECT
    category_id,
    category_name,
    depth,
    path
FROM category_tree;
```

The exact array/type syntax should be verified for the engine.

The important recursion controls are:

```text
visited path
+
depth limit
```

---

# 109. Case Study Part 4 — Customer Existence

Requirement:

> Return customers with at least one order.

Use:

```sql
SELECT
    c.customer_id
FROM customers AS c
WHERE EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.customer_id
);
```

This avoids generating duplicate customer rows.

---

# 110. Case Study Part 5 — Multi-Stage Gold Transformation

Structure:

```text
raw
 ↓
clean
 ↓
filter
 ↓
enrich
 ↓
aggregate
 ↓
final
```

Example:

```sql
WITH raw_orders AS (
    SELECT
        order_id,
        customer_id,
        created_at,
        amount,
        status
    FROM source_orders
),
clean_orders AS (
    SELECT
        order_id,
        customer_id,
        created_at,
        amount
    FROM raw_orders
    WHERE status = 'completed'
      AND order_id IS NOT NULL
      AND customer_id IS NOT NULL
),
enriched_orders AS (
    SELECT
        co.order_id,
        co.customer_id,
        co.created_at,
        co.amount,
        c.country
    FROM clean_orders AS co
    JOIN customers AS c
        ON c.customer_id = co.customer_id
),
daily_customer_metrics AS (
    SELECT
        customer_id,
        country,
        created_at::date AS day,
        COUNT(*) AS order_count,
        SUM(amount) AS revenue
    FROM enriched_orders
    GROUP BY
        customer_id,
        country,
        created_at::date
),
final AS (
    SELECT
        customer_id,
        country,
        day,
        order_count,
        revenue
    FROM daily_customer_metrics
)
SELECT *
FROM final
ORDER BY
    day,
    customer_id;
```

---

# 111. Case Study Grain Map

```text
raw_orders
→ one row/source order

clean_orders
→ one row/valid completed order

enriched_orders
→ one row/order with customer attributes

daily_customer_metrics
→ one row/customer/country/day

final
→ one row/customer/country/day
```

This is the kind of documentation that makes a production SQL transformation reviewable.

---

# 112. Case Study Assertion Queries

## No NULL order IDs

```sql
SELECT *
FROM clean_orders
WHERE order_id IS NULL;
```

Expected:

```text
0 rows
```

---

## No duplicate daily customer rows

```sql
SELECT
    customer_id,
    country,
    day,
    COUNT(*) AS row_count
FROM daily_customer_metrics
GROUP BY
    customer_id,
    country,
    day
HAVING COUNT(*) > 1;
```

Expected:

```text
0 rows
```

---

## Date-spine uniqueness

```sql
SELECT
    day,
    COUNT(*)
FROM date_spine
GROUP BY day
HAVING COUNT(*) > 1;
```

Expected:

```text
0 rows
```

---

# 113. Interview Questions

# Question 1 — What is a subquery?

### Concise answer

A query embedded inside another SQL statement.

### Deeper explanation

Its output can serve as:

```text
a scalar value
a derived relation
a membership set
an existence test
```

### Example

```sql
SELECT *
FROM customers
WHERE customer_id IN (
    SELECT customer_id
    FROM orders
);
```

### Follow-up

> How is a correlated subquery different?

It references an outer query column.

### Common mistake

Thinking all subqueries behave the same way.

---

# 114. Question 2 — What is a scalar subquery?

### Concise answer

A subquery that returns one value.

### Example

```sql
SELECT (
    SELECT AVG(amount)
    FROM orders
);
```

### Follow-up

> What if it returns multiple rows?

The scalar context raises an error.

### Common mistake

Adding LIMIT 1 without defining which row should win.

---

# 115. Question 3 — What is a derived table?

### Concise answer

A subquery in `FROM` that produces an intermediate relation.

### Example

```sql
SELECT *
FROM (
    SELECT
        customer_id,
        SUM(amount) AS total_spend
    FROM orders
    GROUP BY customer_id
) AS customer_totals;
```

### Follow-up

> How does it compare with a CTE?

Both can define an intermediate relation; a CTE often improves readability for multi-stage logic.

### Common mistake

Forgetting to reason about the derived table's grain.

---

# 116. Question 4 — What is a correlated subquery?

### Concise answer

A subquery that references columns from the outer query.

### Example

```sql
SELECT
    c.customer_id,
    (
        SELECT COUNT(*)
        FROM orders AS o
        WHERE o.customer_id = c.customer_id
    )
FROM customers AS c;
```

### Follow-up

> Does it always execute once per outer row?

No. That is a conceptual model; optimizers can rewrite/decorrelate.

### Common mistake

Assuming logical correlation dictates physical execution.

---

# 117. Question 5 — Can a correlated subquery be rewritten as a JOIN?

### Concise answer

Often, yes, especially when the correlated operation is an aggregate by outer key.

### Example

```sql
WITH customer_totals AS (
    SELECT
        customer_id,
        SUM(amount) AS total_spend
    FROM orders
    GROUP BY customer_id
)
SELECT
    c.customer_id,
    ct.total_spend
FROM customers AS c
LEFT JOIN customer_totals AS ct
    ON ct.customer_id = c.customer_id;
```

### Follow-up

> Is the rewrite always faster?

No. Measure.

---

# 118. Question 6 — What is a CTE?

### Concise answer

A named query relation declared in a `WITH` clause.

### Example

```sql
WITH clean_orders AS (...)
SELECT *
FROM clean_orders;
```

### Follow-up

> Is a CTE a temporary table?

Not automatically.

---

# 119. Question 7 — Why use CTEs?

### Concise answer

To structure complex SQL into named, understandable transformation stages.

### Follow-up

> What should each CTE have?

A clear purpose and understandable grain.

### Common mistake

Creating many arbitrary CTEs that make the query longer without making it clearer.

---

# 120. Question 8 — Are CTEs always materialized?

### Concise answer

No.

CTE semantics are logical; physical materialization is engine- and query-dependent.

### Follow-up

> What does PostgreSQL provide?

`MATERIALIZED` and `NOT MATERIALIZED` controls.

---

# 121. Question 9 — What does MATERIALIZED mean?

### Concise answer

In PostgreSQL, it requests a materialization boundary for the CTE.

### Follow-up

> Is it always faster?

No. It can add storage/I/O and prevent some optimizer transformations.

---

# 122. Question 10 — What does NOT MATERIALIZED mean?

### Concise answer

It allows PostgreSQL to treat the CTE more like an inlineable query expression rather than forcing materialization.

### Follow-up

> Why might that help?

It can preserve optimization opportunities such as predicate pushdown.

---

# 123. Question 11 — EXISTS vs IN?

### Concise answer

`IN` expresses membership. `EXISTS` expresses whether at least one matching row exists.

### Follow-up

> Are they always identical?

No. NULL and correlation semantics matter.

---

# 124. Question 12 — EXISTS vs JOIN?

### Concise answer

JOIN produces matching row combinations. EXISTS answers an existence question without duplicating the outer row because of multiple matches.

### Common mistake

Using JOIN plus DISTINCT just to test existence.

---

# 125. Question 13 — How do duplicates affect JOIN vs EXISTS?

### Concise answer

JOIN can multiply the outer row once per matching row. EXISTS remains a boolean test.

### Example

One customer + five orders:

```text
JOIN → five customer rows
EXISTS → one TRUE result
```

---

# 126. Question 14 — How do NULLs affect IN and NOT IN?

### Concise answer

NULL can produce UNKNOWN in membership comparisons, making NOT IN especially dangerous when the subquery contains NULL.

### Follow-up

> What is often easier to reason about?

`NOT EXISTS` for anti-membership.

---

# 127. Question 15 — What is a recursive CTE?

### Concise answer

A CTE that repeatedly consumes rows from its previous result to traverse a hierarchy or graph.

### Follow-up

> What are its two parts?

Anchor and recursive member.

---

# 128. Question 16 — What are anchor and recursive members?

### Concise answer

The anchor establishes starting rows. The recursive member generates subsequent rows.

### Common mistake

Writing a recursive member without explaining termination.

---

# 129. Question 17 — How does recursive SQL terminate?

### Concise answer

The recursive member stops producing rows when there are no more matches or the query explicitly prevents further recursion through conditions such as leaf detection, cycle protection, or a depth limit.

### Follow-up

> Why does termination need to be documented?

Because unbounded recursion can create correctness and resource failures.

---

# 130. Question 18 — How do you prevent recursive cycles?

### Concise answer

Track visited nodes and prevent revisiting them.

### Example

```text
path = [A,B,C]
next node = A
A already in path
→ stop that branch
```

### Follow-up

> Is depth limiting enough?

No. It limits work but does not identify or prevent the semantic cycle by itself.

---

# 131. Question 19 — How would you traverse an employee hierarchy?

### Concise answer

Use a recursive CTE with:

```text
anchor = root employees
recursive member = direct reports
depth = depth + 1
path = accumulated hierarchy
cycle guard = visited employee IDs
```

---

# 132. Question 20 — How would you build a date spine?

### Concise answer

Generate a complete date sequence, aggregate real activity separately, then LEFT JOIN the activity onto the spine.

### Follow-up

> Why?

Because days with no activity otherwise disappear.

---

# 133. Question 21 — generate_series vs recursive CTE?

### Concise answer

Use `generate_series` when a simple built-in sequence generator expresses the requirement directly. Use recursive CTEs when the next value depends on recursion or when traversal semantics are the actual problem.

---

# 134. Question 22 — CTE vs temp table vs view?

### Concise answer

```text
CTE
→ one-statement transformation structure

TEMP TABLE
→ reusable intermediate data across statements

VIEW
→ persistent logical interface

MATERIALIZED VIEW
→ persistent precomputed result
```

### Follow-up

> What determines the choice?

Scope, reuse, freshness, debugging, storage, performance, and maintainability.

---

# 135. Question 23 — How do you debug a five-stage CTE pipeline?

### Concise answer

Inspect each stage separately.

For every stage:

```text
row count
grain
NULLs
duplicates
invariants
```

Then compare expected and actual transformations.

---

# 136. Production Checklist

Before shipping a complex SQL transformation, verify:

- [ ] I know the grain of every input.
- [ ] I know the grain of every CTE.
- [ ] I know the grain of the final result.
- [ ] Every scalar subquery is guaranteed to have appropriate cardinality.
- [ ] I have tested what happens if a scalar subquery returns multiple rows.
- [ ] `IN` versus `EXISTS` is a deliberate semantic choice.
- [ ] `NOT IN` has been reviewed for NULL hazards.
- [ ] `NOT EXISTS` is used when relationship-based anti-membership is clearer.
- [ ] JOINs are not being used merely to test existence.
- [ ] Correlated subqueries are intentional.
- [ ] I am not assuming logical row-by-row correlation means physical row-by-row execution.
- [ ] I understand that optimizers may decorrelate queries.
- [ ] Important correlated queries have been considered for performance.
- [ ] CTE names describe their contents.
- [ ] Each CTE has one primary logical responsibility.
- [ ] Each CTE's grain is documented or obvious.
- [ ] CTE chains are not unnecessarily complex.
- [ ] Recursive CTEs have an explicit anchor.
- [ ] Recursive CTEs have an explicit recursive member.
- [ ] Recursive CTEs have a clear termination condition.
- [ ] Recursive CTEs have cycle protection where cycles are possible.
- [ ] Recursive depth is tracked where useful.
- [ ] Any depth limit is intentional and documented.
- [ ] Date-spine start and end boundaries are correct.
- [ ] Missing dates are represented intentionally.
- [ ] NULL-to-zero conversion is justified.
- [ ] `generate_series` syntax is verified for the installed engine.
- [ ] CTE materialization assumptions are not based on myths.
- [ ] PostgreSQL `MATERIALIZED` / `NOT MATERIALIZED` usage is intentional.
- [ ] Engine-specific behavior has been verified.
- [ ] Assertion queries exist for critical stages.
- [ ] The transformation can be explained stage by stage during code review.

---

# 137. Final Knowledge Check

Complete these without referring to the chapter.

## Theory

1. Define a subquery.
2. Define a scalar subquery.
3. What cardinality does a scalar subquery require?
4. What happens when it returns multiple rows?
5. What is a derived table?
6. How does a subquery in FROM differ conceptually from a scalar subquery?
7. What question does IN answer?
8. What question does EXISTS answer?
9. How do duplicates affect JOIN?
10. How do duplicates affect EXISTS?
11. How do NULLs affect NOT IN?
12. Why is NOT EXISTS often easier to reason about for anti-membership?
13. Define a correlated subquery.
14. Define an uncorrelated subquery.
15. Is a correlated subquery necessarily executed once per outer row?
16. What is decorrelation?
17. What is a CTE?
18. Why are CTEs useful in transformation pipelines?
19. What should you document for each important CTE?
20. What is dbt-style transformation thinking?
21. What is a recursive CTE?
22. What is an anchor member?
23. What is a recursive member?
24. How does recursion terminate?
25. Why is cycle protection required?
26. What is a date spine?
27. Why use a date spine?
28. What is generate_series?
29. What is CTE materialization?
30. Are CTEs always materialized?
31. Are CTEs always inlined?
32. What is PostgreSQL MATERIALIZED?
33. What is PostgreSQL NOT MATERIALIZED?
34. When might a temporary table be better than a CTE?
35. When might a view be better?
36. How do you debug a CTE pipeline?

---

# 138. Practical Final Assessment

## Task 1 — Scalar subquery

Calculate the global average order amount and show it beside each order.

---

## Task 2 — Derived table

Calculate customer totals in a derived table, then filter high-spend customers.

---

## Task 3 — IN

Find customers whose IDs appear in orders.

---

## Task 4 — EXISTS

Solve the same requirement using EXISTS.

Explain the semantic difference from JOIN.

---

## Task 5 — Correlated

Write a per-customer correlated order count.

Then rewrite it using a CTE and JOIN.

---

## Task 6 — NULL semantics

Create a NULL-containing membership set.

Predict:

```text
IN
NOT IN
EXISTS
NOT EXISTS
```

before execution.

---

## Task 7 — CTE pipeline

Build:

```text
raw
→ clean
→ enrich
→ aggregate
→ final
```

and document every stage's grain.

---

## Task 8 — Recursive hierarchy

Build an employee tree with:

```text
employee
depth
path
```

and cycle protection.

---

## Task 9 — Graph walk

Find all nodes reachable from:

```text
A
```

with a cycle in the graph.

---

## Task 10 — Date spine

Build a one-month date spine and show zero-activity days.

---

## Task 11 — Recursive date generation

Solve the same date generation requirement using a recursive CTE.

---

## Task 12 — Materialization reasoning

Given a costly repeated CTE, explain:

```text
default behavior
MATERIALIZED
NOT MATERIALIZED
```

and what measurements you would use before changing the query.

---

## Task 13 — CTE vs TEMP TABLE vs VIEW

Given a transformation consumed:

```text
once in one statement
across five statements
by many analysts
as a repeatedly expensive report
```

choose an appropriate structure for each case and defend it.

---

# 139. Final Checkpoint — Ready for Topic 05?

The Module 2.6 roadmap requires these capabilities.

You must be able to:

- [ ] Explain correlated versus uncorrelated subqueries.
- [ ] Structure a complex transformation as a clear CTE chain.
- [ ] Write a recursive CTE for a hierarchy.
- [ ] Build a date spine to fill missing periods.

---

## Checkpoint Gate 1 — Correlation

Without notes, explain:

```text
uncorrelated
vs
correlated
```

and write one example of each.

---

## Checkpoint Gate 2 — CTE Pipeline

Build:

```text
clean
→ enrich
→ aggregate
→ final
```

and state the grain after every stage.

---

## Checkpoint Gate 3 — Recursive CTE

Build an employee hierarchy and explicitly identify:

```text
anchor
recursive member
termination
cycle protection
depth
```

---

## Checkpoint Gate 4 — Date Spine

Generate a complete date sequence and LEFT JOIN activity so missing periods remain visible.

Explain:

```text
why missing dates disappear without the spine
why the spine restores them
when COALESCE to zero is semantically appropriate
```

---

# 140. Do Not Move On Yet If

You still believe:

```text
CTE = temporary table
```

or:

```text
CTE = always materialized
```

or:

```text
correlated subquery = physically executed once per outer row
```

or:

```text
JOIN and EXISTS always produce the same row semantics
```

or:

```text
NULL behaves like a normal value in IN/NOT IN
```

or:

```text
recursive SQL can be written without a termination design
```

Those misunderstandings will cause production failures later.

---

# 141. Common Mistakes — Final Summary

Remember:

```text
1. Know the expected cardinality of every subquery.
2. A scalar subquery must represent one value.
3. Use derived tables when you need an inline intermediate relation.
4. Use IN for membership questions.
5. Use EXISTS for existence questions.
6. JOIN produces matching combinations; EXISTS does not duplicate the outer row.
7. NULL can make IN/NOT IN logic subtle.
8. NOT EXISTS is often a clearer anti-membership expression.
9. Correlation is a logical dependency, not a guaranteed physical execution strategy.
10. Optimizers may decorrelate correlated subqueries.
11. Correlated queries are not automatically slow.
12. A CTE is a named logical transformation stage.
13. Track grain through every CTE.
14. Name CTEs by their contents and purpose.
15. Keep each CTE focused on one primary transformation.
16. Recursive CTEs need an anchor.
17. Recursive CTEs need a recursive member.
18. Recursive CTEs need explicit termination.
19. Recursive traversal may need cycle protection.
20. Depth limits protect resources but should not silently change business meaning.
21. Date spines make missing periods visible.
22. Missing dates and zero values are not inherently identical.
23. generate_series is usually preferable to recursive SQL for simple sequences when supported.
24. Do not assume CTEs materialize.
25. Do not assume CTEs are always inlined.
26. PostgreSQL provides MATERIALIZED and NOT MATERIALIZED controls.
27. Materialization can help or hurt depending on the workload.
28. A temp table is useful when intermediate data must survive across statements.
29. A view is useful as a persistent logical interface.
30. Always debug complex SQL one transformation stage at a time.
```

---

# 142. Final Mental Model

When faced with a complex SQL transformation, think:

```text
1. What question am I answering?
        ↓
2. What shape should the subquery produce?
        ↓
3. What is the input grain?
        ↓
4. What is the intermediate grain?
        ↓
5. What is the output grain?
        ↓
6. Are duplicates expected?
        ↓
7. How do NULLs behave?
        ↓
8. Is the subquery correlated?
        ↓
9. Could an optimizer rewrite the structure?
        ↓
10. Should the transformation be a CTE stage?
        ↓
11. If recursive:
        anchor?
        recursive member?
        termination?
        cycle protection?
        depth?
        ↓
12. If time-based:
        do I need a date spine?
        ↓
13. What are the engine-specific semantics?
        ↓
14. What assertion proves the stage is correct?
```

The senior Data Engineering habit is not:

> "I know how to write a CTE."

It is:

> **"I can decompose a complex transformation into explicit relational stages, state the grain and correctness condition of every stage, reason about duplicates and NULLs, control recursive traversal safely, and choose the appropriate SQL structure without making unsupported performance assumptions."**
