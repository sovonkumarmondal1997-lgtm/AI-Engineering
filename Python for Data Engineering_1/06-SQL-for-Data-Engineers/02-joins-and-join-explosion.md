# 02 — Joins and Join Explosion

> **Module:** 2.6 — SQL for Data Engineers  
> **Phase:** A — Querying Correctly  
> **Primary engines:** PostgreSQL 16+ and DuckDB  
> **Core idea:** Before you run a join, know the grain, keys, cardinality, and expected row count.

A SQL join is one of the most useful operations in data engineering and one of the easiest places to introduce silent correctness bugs.

The dangerous mistake is not usually writing invalid SQL. The dangerous mistake is writing **valid SQL that produces the wrong number of rows**.

That happens because a join does not inherently mean:

> one input row → one output row

Instead, think:

> **For each row on the left, find all matching rows on the right according to the join condition.**

If one left row matches three right rows, that left row can produce three output rows.

That one idea explains much of:

- join cardinality,
- 1:1 / 1:N / N:1 / N:M relationships,
- duplicated facts,
- inflated revenue,
- fan traps,
- accidental many-to-many joins,
- incorrect counts,
- missing customers,
- and many production reconciliation failures.

This chapter teaches joins as an engineering problem, not as a syntax memorization exercise.

---

# 1. Learning Objectives

By the end of this chapter, you should be able to:

- Explain what a SQL join does without relying on simplistic Venn diagrams.
- Write and reason about:
  - `INNER JOIN`
  - `LEFT JOIN`
  - `RIGHT JOIN`
  - `FULL OUTER JOIN`
  - `CROSS JOIN`
  - self-joins
  - joins using `ON`
  - joins using `USING`
- State the **grain** of every input table and the expected grain of the output.
- Identify join keys and state which side is unique.
- Classify relationships as:
  - 1:1
  - 1:N
  - N:1
  - N:M
- Predict exact or approximate output row counts before executing a join.
- Understand the relationship between SQL key assumptions and pandas `merge(validate=...)`.
- Detect duplicate-key problems on a supposed "one" side.
- Detect many-to-many multiplication.
- Explain and diagnose **join explosion**.
- Explain and fix a **fan trap**.
- Prevent join explosion through:
  - pre-aggregation,
  - deduplication,
  - explicit grain control,
  - uniqueness assertions.
- Explain why `SELECT DISTINCT` is often a poor band-aid.
- Understand why a `LEFT JOIN` can appear to behave like an `INNER JOIN`.
- Write semi-joins with `EXISTS` or `IN`.
- Write anti-joins with `NOT EXISTS` or an appropriate `LEFT JOIN` pattern.
- Explain how NULL join keys behave.
- Write non-equi joins and range joins.
- Understand DuckDB `ASOF JOIN`.
- Express ASOF-style lookups in PostgreSQL using `LATERAL`.
- Use `LATERAL` for per-row lookups such as latest N records per parent.
- Explain the production risks of `NATURAL JOIN`.
- Use `USING` deliberately rather than mechanically.
- Explain nested-loop, hash, and merge joins conceptually.
- Reconcile:
  - row counts,
  - distinct keys,
  - unmatched records,
  - financial totals,
  - and other business metrics.
- Debug inflated revenue, missing records, and unexpectedly large join outputs.
- Write assertion queries that catch join assumptions before they damage downstream data.

---

# 2. Why Joins Matter in Data Engineering

Joins are not just a SQL-language feature.

They are a **data modeling and correctness operation**.

A typical data platform contains tables with different grains:

```text
customers
    one row per customer

orders
    one row per order

order_lines
    one row per order line

payments
    one row per payment

shipments
    one row per shipment

products
    one row per product
```

The business often wants a result that combines information across those tables.

For example:

> "Show revenue, customer country, payment totals, and shipment status for every order."

That sounds straightforward.

But an order can have:

```text
3 order lines
2 payments
1 shipment
```

If you join all of those raw child tables directly, the one order can become:

```text
3 × 2 × 1 = 6 joined rows
```

If you then write:

```sql
SUM(o.amount)
```

you may count the same order-level amount six times.

That is a correctness bug, not merely a performance issue.

---

## 2.1 Why join mistakes are dangerous

A bad join can create:

- inflated revenue,
- inflated order counts,
- duplicated customers,
- false conversion rates,
- incorrect inventory totals,
- missing unmatched records,
- incorrect dimension attributes,
- unexpectedly huge intermediate results,
- excessive memory use,
- slow queries,
- downstream data-quality failures.

The most important skill in this chapter is therefore:

> **Reason about row multiplication before running the query.**

---

# 3. Prerequisite Mental Model: Grain and Keys

Before writing a join, answer two questions:

1. **What is the grain of each input?**
2. **What does the join key mean on each side?**

---

## 3.1 What is grain?

The **grain** of a table tells you what one row represents.

Examples:

```text
customers
→ one row per customer

orders
→ one row per order

order_lines
→ one row per order line

payments
→ one row per payment

events
→ one row per event
```

Grain is one of the most important habits in data engineering because row counts only make sense relative to a grain.

---

## 3.2 What is a key?

A **key** is a column or set of columns used to identify or relate rows.

For example:

```text
customers.customer_id
orders.customer_id
```

may represent the relationship:

```text
one customer → many orders
```

while:

```text
orders.order_id
order_lines.order_id
```

usually represents:

```text
one order → many order lines
```

The same column name does not guarantee uniqueness.

---

## 3.3 Grain-first join template

Before every substantial join, write:

```text
Left input grain:
Right input grain:
Join key:
Is left key unique?
Is right key unique?
Join relationship:
Expected output grain:
Expected row-count behavior:
```

Example:

```text
Left input grain:
one row per order

Right input grain:
one row per payment

Join key:
order_id

Is left key unique?
yes

Is right key unique?
no

Join relationship:
1:N

Expected output grain:
one row per payment for orders that have payments

Expected row-count behavior:
an order with multiple payments becomes multiple joined rows
```

This habit prevents many production bugs before SQL is executed.

---

# 4. The Core Mental Model of a SQL Join

## 4.1 Do not start with a Venn diagram

Venn diagrams can be useful for remembering which unmatched rows are preserved by different outer joins.

They are not a sufficient model for row multiplication.

The more useful mental model is:

> **For each row on the left, find every matching row on the right. Emit one joined result for every match.**

Suppose the left side has:

```text
customer_id = 1
```

and the right side has:

```text
customer_id = 1
customer_id = 1
customer_id = 1
```

Then one left row can become three output rows.

```text
1 left row
×
3 matching right rows
=
3 output rows
```

---

## 4.2 Tiny example

Left table:

```text
orders
+----------+--------+
| order_id | amount |
+----------+--------+
| 101      | 100    |
| 102      | 200    |
+----------+--------+
```

Right table:

```text
payments
+------------+----------+--------+
| payment_id | order_id | amount |
+------------+----------+--------+
| 1          | 101      | 60     |
| 2          | 101      | 40     |
| 3          | 102      | 200    |
+------------+----------+--------+
```

Query:

```sql
SELECT
    o.order_id,
    o.amount AS order_amount,
    p.payment_id,
    p.amount AS payment_amount
FROM orders AS o
INNER JOIN payments AS p
    ON p.order_id = o.order_id
ORDER BY
    o.order_id,
    p.payment_id;
```

Result:

```text
order_id | order_amount | payment_id | payment_amount
---------+--------------+------------+---------------
101      | 100          | 1          | 60
101      | 100          | 2          | 40
102      | 200          | 3          | 200
```

Notice:

```text
order 101
    matched payment 1
    matched payment 2

so:
1 order row → 2 joined rows
```

This is not an error. It is the correct result for the relationship.

The error happens when the engineer **forgets that row multiplication happened**.

---

## 4.3 A useful equation

For one left row:

```text
output rows for that left row
=
number of matching right rows
```

For multiple left rows, conceptually:

```text
total output
=
sum of matching-right-row counts for the left rows
```

This is why key uniqueness matters so much.

---

# 5. INNER JOIN

## 5.1 What is it?

An `INNER JOIN` returns combinations where the join condition matches.

```sql
SELECT
    o.order_id,
    c.customer_id
FROM orders AS o
INNER JOIN customers AS c
    ON c.customer_id = o.customer_id;
```

`JOIN` without a qualifier normally means:

```sql
INNER JOIN
```

---

## 5.2 What happens to each left row?

For every left row:

- if there are matching right rows, emit one output row per match;
- if there are no matches, emit nothing.

Example:

```text
customers
+-------------+---------+
| customer_id | country |
+-------------+---------+
| 1           | India   |
| 2           | Nepal   |
| 3           | Bhutan  |
+-------------+---------+

orders
+----------+-------------+
| order_id | customer_id |
+----------+-------------+
| 101      | 1           |
| 102      | 1           |
| 103      | 2           |
| 104      | 99          |
+----------+-------------+
```

Query:

```sql
SELECT
    o.order_id,
    o.customer_id,
    c.country
FROM orders AS o
INNER JOIN customers AS c
    ON c.customer_id = o.customer_id
ORDER BY o.order_id;
```

Result:

```text
101 | 1 | India
102 | 1 | India
103 | 2 | Nepal
```

Order 104 disappears because customer 99 does not match.

---

## 5.3 INNER JOIN is not "common values" in a simple set sense

Suppose the right side contains duplicate keys:

```text
customer_id
1
1
```

and the left side has one row:

```text
customer_id = 1
```

The result has two rows.

So the useful rule is not:

> "Return the overlapping entities."

The useful rule is:

> **Return every matching pair of rows.**

---

## 5.4 Grain reasoning

Suppose:

```text
orders       → one row per order
payments     → one row per payment
```

and the relationship is:

```text
orders → payments = 1:N
```

Then an INNER JOIN has a natural result closer to:

```text
one row per payment for matched orders
```

It is no longer at order grain.

That is a critical observation before aggregation.

---

# 6. LEFT JOIN

## 6.1 What is it?

A `LEFT JOIN` keeps every row from the left input.

For each left row:

- matching right rows are emitted;
- if there is no right match, one output row is emitted with NULLs for right-side columns.

Example:

```sql
SELECT
    c.customer_id,
    c.country,
    o.order_id
FROM customers AS c
LEFT JOIN orders AS o
    ON o.customer_id = c.customer_id
ORDER BY
    c.customer_id,
    o.order_id;
```

---

## 6.2 Customers with no orders

Suppose:

```text
customers
1
2
3
```

and:

```text
orders
customer 1
customer 1
customer 2
```

Customer 3 has no order.

A LEFT JOIN produces:

```text
1 | order A
1 | order B
2 | order C
3 | NULL
```

The NULL means:

> no matching right-side row was found.

---

## 6.3 LEFT JOIN does not guarantee one output row per left row

This is a common misunderstanding.

A LEFT JOIN preserves all left rows, but a left row can still be repeated.

If one customer has five matching orders:

```text
1 customer row
×
5 order rows
=
5 output rows
```

The customer is preserved, but not at one-row-per-customer grain.

---

## 6.4 Duplicate right-side keys

If:

```text
customers.customer_id = 1
```

and the orders table accidentally has two rows with the same logical key:

```text
customer_id = 1
customer_id = 1
```

the LEFT JOIN returns two rows for that customer.

This is why expected uniqueness must be validated.

---

# 7. RIGHT JOIN

## 7.1 What is it?

`RIGHT JOIN` is the mirror image of `LEFT JOIN`.

It preserves all rows from the **right** input.

```sql
SELECT
    c.customer_id,
    o.order_id
FROM customers AS c
RIGHT JOIN orders AS o
    ON o.customer_id = c.customer_id;
```

Every order remains in the result.

If an order refers to a missing customer:

```text
customer_id = NULL
```

can appear in the customer columns.

---

## 7.2 Why many teams prefer LEFT JOIN

You can often rewrite:

```sql
customers
RIGHT JOIN orders
```

as:

```sql
orders
LEFT JOIN customers
```

This keeps the "preserved" table on the left, which many teams find easier to read.

That is a readability convention, not a rule that RIGHT JOIN is invalid.

---

# 8. FULL OUTER JOIN

## 8.1 What is it?

A `FULL OUTER JOIN` preserves:

- matched rows,
- left-only rows,
- right-only rows.

Example:

```sql
SELECT
    s.id AS source_id,
    t.id AS target_id,
    s.value AS source_value,
    t.value AS target_value
FROM source_table AS s
FULL OUTER JOIN target_table AS t
    ON s.id = t.id;
```

This is useful for reconciliation.

---

## 8.2 Tiny reconciliation example

Source:

```text
id | value
---+------
1  | A
2  | B
3  | C
```

Target:

```text
id | value
---+------
2  | B
3  | X
4  | D
```

FULL OUTER JOIN by `id` can reveal:

```text
1 → source-only
2 → matched and equal
3 → matched but different
4 → target-only
```

This makes full outer joins useful for understanding source/target differences.

---

## 8.3 A common reconciliation expression

```sql
SELECT
    COALESCE(s.id, t.id) AS id,
    s.value AS source_value,
    t.value AS target_value
FROM source_table AS s
FULL OUTER JOIN target_table AS t
    ON s.id = t.id;
```

`COALESCE` is useful here because either side may contain the identifier when the other side is missing.

The important engineering question remains:

> Is the join key actually unique?

If not, FULL OUTER JOIN can itself multiply rows.

---

# 9. CROSS JOIN

## 9.1 What is it?

A `CROSS JOIN` produces every combination of left and right rows.

```sql
SELECT *
FROM a
CROSS JOIN b;
```

If:

```text
rows(a) = 3
rows(b) = 4
```

then:

```text
3 × 4 = 12
```

rows are produced.

---

## 9.2 Tiny example

A:

```text
A1
A2
A3
```

B:

```text
B1
B2
B3
B4
```

The result is:

```text
A1 B1
A1 B2
A1 B3
A1 B4
A2 B1
A2 B2
A2 B3
A2 B4
A3 B1
A3 B2
A3 B3
A3 B4
```

---

## 9.3 Legitimate uses

CROSS JOIN can be useful for:

- entity × date grids,
- test matrices,
- parameter combinations,
- scenario generation,
- small controlled Cartesian products.

Example:

```text
customers × reporting_dates
```

can be useful for building a complete customer-date grid.

---

## 9.4 Why accidental Cartesian products are dangerous

If:

```text
customers = 10,000,000
events = 100,000,000
```

then:

```text
10,000,000 × 100,000,000
=
1,000,000,000,000,000
```

potential combinations.

That can be catastrophic.

An accidental missing or ineffective join condition can therefore produce extreme intermediate data volumes.

---

# 10. Self-Joins

A self-join joins a table to itself.

The table appears more than once, so aliases are essential.

## 10.1 Employee hierarchy

Suppose:

```text
employees
+-------------+---------------+-----------+
| employee_id | employee_name | manager_id|
+-------------+---------------+-----------+
| 1           | Priya         | NULL      |
| 2           | Arun          | 1         |
| 3           | Mei           | 1         |
| 4           | Daniel        | 2         |
+-------------+---------------+-----------+
```

Query:

```sql
SELECT
    e.employee_name AS employee,
    m.employee_name AS manager
FROM employees AS e
LEFT JOIN employees AS m
    ON m.employee_id = e.manager_id;
```

Result:

```text
Priya  | NULL
Arun   | Priya
Mei    | Priya
Daniel | Arun
```

---

## 10.2 Why aliases matter

Without aliases, the database cannot clearly distinguish the two logical copies of the table.

Think:

```text
employees AS e → employee row
employees AS m → manager row
```

The two references are to the same physical table but play different logical roles.

---

## 10.3 Production risks

Self-joins can multiply rows when the supposed key is not unique.

Do not assume:

```text
employee_id
```

is unique just because its name suggests it should be.

Validate important assumptions.

Recursive organizational structures belong to a later CTE topic. Here, focus on the basic self-join mental model.

---

# 11. ON vs USING

## 11.1 `ON`

The most explicit form is:

```sql
SELECT
    ...
FROM customers AS c
JOIN orders AS o
    ON o.customer_id = c.customer_id;
```

`ON` lets you write the exact matching condition.

This makes complex logic explicit.

For example:

```sql
ON o.customer_id = c.customer_id
AND o.status = 'completed'
```

---

## 11.2 `USING`

When both tables have a column with the same join-column name, you can write:

```sql
SELECT
    ...
FROM customers AS c
JOIN orders AS o
    USING (customer_id);
```

This is concise and communicates:

> join these sources using the shared `customer_id` column.

---

## 11.3 Readability trade-off

`USING` can be very readable when the relationship is obvious.

`ON` is often clearer when:

- the column names differ,
- conditions are more complex,
- you want the matching logic fully visible,
- the query needs explicit qualification.

---

## 11.4 Schema-evolution considerations

`USING` and `NATURAL JOIN` should not be confused.

`USING` explicitly names the columns:

```sql
USING (customer_id)
```

so adding a new same-named column does not silently add that column to the join condition.

`NATURAL JOIN`, discussed later, can do exactly that.

Still, `USING` can change output-column behavior because a shared join column is represented as a single common column in many SQL implementations.

Use it deliberately.

---

# 12. Join Cardinality

**Cardinality** describes how rows relate between two tables through a key.

The core patterns are:

```text
1:1
1:N
N:1
N:M
```

These are not just database-design labels.

They predict how a join changes row counts.

---

## 12.1 1:1

One row on the left matches at most one row on the right.

Example:

```text
users
user_id unique
```

and:

```text
user_profiles
user_id unique
```

Relationship:

```text
users → user_profiles = 1:1
```

A match does not inherently multiply the row.

But remember: if uniqueness is only assumed and not enforced, the actual relationship could become 1:N.

---

## 12.2 1:N

One left row can match many right rows.

Example:

```text
customer
    |
    +-- order
    +-- order
    +-- order
```

Relationship:

```text
customers → orders = 1:N
```

A customer with ten orders can become ten joined rows.

---

## 12.3 N:1

This is the same relationship viewed from the other direction.

```text
orders → customers = N:1
```

Many orders can match one customer.

This often appears as:

```sql
orders
JOIN customers
  ON customers.customer_id = orders.customer_id
```

The order side is many.

The customer side is one.

---

## 12.4 N:M

Many rows on both sides can match multiple rows.

Examples:

```text
students ↔ courses
products ↔ tags
orders ↔ payments
users ↔ permissions
```

if neither side is unique on the linking key.

These joins are where row multiplication can become especially large.

---

# 13. Predicting Join Output Row Counts

This is one of the most important sections of the chapter.

> **Predict the row count before running the join.**

Do not wait for the database to surprise you.

---

## 13.1 1:1 intuition

Suppose:

```text
A = 100 rows
B = 100 rows
```

and the join key is unique on both sides.

If every row matches:

```text
output ≈ 100
```

If 10 rows on A do not match:

```text
output ≈ 90
```

for an INNER JOIN.

---

## 13.2 1:N intuition

Suppose:

```text
customers = 100 rows
orders = 900 rows
```

and every order belongs to exactly one customer.

Then:

```text
customers → orders
```

is:

```text
1:N
```

An INNER JOIN from customers to orders can produce approximately:

```text
900 rows
```

not 100.

The result is closer to the child grain:

```text
one row per order
```

---

## 13.3 N:1 intuition

If you start from orders:

```text
orders = 900
customers = 100
```

and every order maps to one customer:

```text
orders → customers = N:1
```

the output can still be:

```text
900 rows
```

assuming all orders have matching customers.

The number of rows is not determined by "number of tables."

It is determined by matching multiplicity.

---

## 13.4 N:M intuition

Suppose:

```text
customer 1 has 3 tags
customer 1 has 4 interests
```

If you join:

```text
customer
JOIN tags
JOIN interests
```

then for customer 1:

```text
3 tag rows
×
4 interest rows
=
12 combinations
```

This is the key pattern behind many fan traps.

---

## 13.5 A more useful mental equation

For each left row:

```text
joined output rows
=
number of right-side matches
```

For many-to-many joins, think:

```text
matching multiplicity on left
×
matching multiplicity on right
```

for the shared entity.

---

# 14. Relationship to pandas `validate=`

Earlier pandas work may have taught merge validation concepts such as:

```python
merge(validate="one_to_one")
merge(validate="one_to_many")
merge(validate="many_to_one")
```

The SQL mental model is related.

The assumption:

```text
customer_id is unique in customers
```

is equivalent to saying:

> the customer side is the "one" side.

The important difference is that a normal SQL join does not generally reject an accidental many-to-many relationship merely because you expected one-to-many.

Therefore SQL engineers must validate important assumptions themselves.

A useful mapping is:

```text
pandas validation expectation
            ↕
SQL key uniqueness assertion
            ↕
join cardinality assumption
```

Do not rely on the column name alone.

---

# 15. Join Explosion

## 15.1 Definition

A **join explosion** occurs when a join produces far more rows than intended because matching multiplicities multiply.

The result may still be syntactically and semantically valid SQL.

The problem is that the **business grain is wrong**.

---

## 15.2 Simple example

Suppose:

```text
one order
3 order lines
```

and:

```text
one order
2 payments
```

Directly joining both:

```text
orders
  ↓
order_lines
  ↓
payments
```

can produce:

```text
3 × 2 = 6 rows
```

The six rows are all valid combinations of line and payment.

But the business may have intended:

```text
one row per order
```

The join produced:

```text
one row per order-line/payment combination
```

That is the grain error.

---

## 15.3 Why join explosion is often invisible

An engineer may look at:

```sql
SELECT
    o.order_id,
    ...
FROM orders AS o
JOIN order_lines AS ol
  ON ...
JOIN payments AS p
  ON ...
```

and think:

> "Both joins use the correct foreign key."

That can be true.

The problem is not necessarily the individual join condition.

The problem is combining **two independent one-to-many children at the same parent grain**.

---

# 16. Fan Trap

A **fan trap** is a common structure that causes many-to-many multiplication.

```text
                   orders
                  /      \
                 /        \
                /          \
        order_lines       payments
           1:N               1:N
```

The two child branches "fan out" from the same parent.

Suppose one order has:

```text
3 order lines
2 payments
```

Directly combining those child tables at order grain can produce:

```text
3 × 2 = 6
```

combinations.

---

## 16.1 Why this is dangerous

Suppose the order amount is:

```text
$100
```

and you run:

```sql
SELECT
    o.order_id,
    SUM(o.amount) AS revenue
FROM orders AS o
JOIN order_lines AS ol
    ON ol.order_id = o.order_id
JOIN payments AS p
    ON p.order_id = o.order_id
GROUP BY o.order_id;
```

For an order with:

```text
3 lines
2 payments
```

there are six joined rows.

The order amount appears on each row:

```text
100
100
100
100
100
100
```

The sum becomes:

```text
600
```

instead of:

```text
100
```

The SQL did exactly what it was told to do.

The grain was wrong.

---

# 17. Why Revenue Gets Inflated

Let's build a complete example.

## 17.1 Data

Orders:

```sql
CREATE TEMP TABLE orders_demo (
    order_id INTEGER,
    amount NUMERIC
);

INSERT INTO orders_demo VALUES
    (101, 100),
    (102, 200);
```

Order lines:

```sql
CREATE TEMP TABLE order_lines_demo (
    order_line_id INTEGER,
    order_id INTEGER,
    quantity INTEGER
);

INSERT INTO order_lines_demo VALUES
    (1, 101, 1),
    (2, 101, 2),
    (3, 101, 1),
    (4, 102, 1);
```

Payments:

```sql
CREATE TEMP TABLE payments_demo (
    payment_id INTEGER,
    order_id INTEGER,
    amount NUMERIC
);

INSERT INTO payments_demo VALUES
    (1, 101, 60),
    (2, 101, 40),
    (3, 102, 200);
```

---

## 17.2 Grain

```text
orders_demo
→ one row per order

order_lines_demo
→ one row per order line

payments_demo
→ one row per payment
```

---

## 17.3 Cardinalities

```text
orders → order_lines
101 → 3 lines
102 → 1 line

orders → payments
101 → 2 payments
102 → 1 payment
```

---

## 17.4 Broken query

```sql
SELECT
    o.order_id,
    SUM(o.amount) AS revenue
FROM orders_demo AS o
JOIN order_lines_demo AS ol
    ON ol.order_id = o.order_id
JOIN payments_demo AS p
    ON p.order_id = o.order_id
GROUP BY o.order_id
ORDER BY o.order_id;
```

For order 101:

```text
3 order lines
×
2 payments
=
6 rows
```

So:

```text
SUM(100 over 6 rows)
=
600
```

The output is logically correct for the query but wrong for the intended business metric.

---

# 18. How to Prevent Join Explosion

There are several reliable strategies.

## Strategy 1 — Choose the desired output grain first

Suppose the desired output is:

```text
one row per order
```

Then every source joined into the final result should ideally also be represented at:

```text
one row per order
```

before the final join.

This is the most important principle.

---

## Strategy 2 — Pre-aggregate child tables

Turn:

```text
many payments per order
```

into:

```text
one payment-total row per order
```

and do the same for order lines.

Then join the summaries.

---

## Strategy 3 — Deduplicate dimensions

If a dimension is supposed to have one row per key, verify that assumption.

A duplicate dimension key can turn:

```text
N:1
```

into:

```text
N:M
```

without the query visibly changing.

---

## Strategy 4 — Assert key uniqueness

Run a validation query.

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

If rows appear, your "one" side is not unique.

---

# 19. Pre-Aggregating Child Tables

This is the primary repair for the fan trap.

## 19.1 Bad structure

```text
orders
  |
  +---- order_lines (many)
  |
  +---- payments (many)
```

---

## 19.2 Desired structure

First reduce each child:

```text
order_lines
      ↓
one row per order

payments
      ↓
one row per order
```

Then:

```text
orders
  |
  +---- line_totals     1:1
  |
  +---- payment_totals  1:1
```

Now the final result can remain at:

```text
one row per order
```

---

## 19.3 Correct SQL

```sql
WITH line_totals AS (
    SELECT
        order_id,
        SUM(quantity) AS total_units
    FROM order_lines_demo
    GROUP BY order_id
),
payment_totals AS (
    SELECT
        order_id,
        SUM(amount) AS paid_amount
    FROM payments_demo
    GROUP BY order_id
)
SELECT
    o.order_id,
    o.amount AS order_amount,
    COALESCE(lt.total_units, 0) AS total_units,
    COALESCE(pt.paid_amount, 0) AS paid_amount
FROM orders_demo AS o
LEFT JOIN line_totals AS lt
    ON lt.order_id = o.order_id
LEFT JOIN payment_totals AS pt
    ON pt.order_id = o.order_id
ORDER BY o.order_id;
```

---

## 19.4 Grain after each step

Before:

```text
orders_demo
→ one row per order

order_lines_demo
→ one row per line

payments_demo
→ one row per payment
```

After `line_totals`:

```text
one row per order
```

After `payment_totals`:

```text
one row per order
```

Final join:

```text
order
1:1
line_totals
1:1
payment_totals
```

The fan trap has been removed.

---

## 19.5 Engineering principle

> **Pre-aggregate to the intended parent grain before combining independent child relationships.**

This principle is more useful than memorizing a specific SQL template.

---

# 20. Deduplicating Dimensions

A supposed dimension can accidentally contain duplicate business keys.

Suppose:

```text
products
+------------+-------+
| product_id | price |
+------------+-------+
| 10         | 100   |
| 10         | 105   |
+------------+-------+
```

The engineer expects:

```text
product_id
```

to be unique.

It is not.

---

## 20.1 Impact

Orders:

```text
order_id | product_id
---------+-----------
101      | 10
```

Join:

```sql
SELECT
    o.order_id,
    p.price
FROM orders AS o
JOIN products AS p
    ON p.product_id = o.product_id;
```

returns:

```text
101 | 100
101 | 105
```

One order row became two rows.

If you then aggregate:

```sql
SUM(o.amount)
```

the order can be counted twice.

---

## 20.2 Correct engineering response

Do not immediately add:

```sql
DISTINCT
```

First determine:

> Why are there two rows for the supposed unique product?

Maybe:

- the source data is duplicated,
- the dimension contains history,
- a business key is not actually unique,
- the table grain was misunderstood.

The repair depends on the real model.

---

# 21. Asserting Key Uniqueness

An assertion query should return zero rows when the assumption is valid.

## 21.1 Product uniqueness

```sql
SELECT
    product_id,
    COUNT(*) AS row_count
FROM products
GROUP BY product_id
HAVING COUNT(*) > 1;
```

Expected:

```text
0 rows
```

---

## 21.2 Customer uniqueness

```sql
SELECT
    customer_id,
    COUNT(*) AS row_count
FROM customers
GROUP BY customer_id
HAVING COUNT(*) > 1;
```

---

## 21.3 Composite key uniqueness

If the actual grain is:

```text
one row per customer per day
```

then:

```sql
SELECT
    customer_id,
    event_date,
    COUNT(*) AS row_count
FROM daily_customer_metrics
GROUP BY
    customer_id,
    event_date
HAVING COUNT(*) > 1;
```

This is an important extension:

> **Keys should be validated at the grain actually required by the business model.**

---

# 22. LEFT JOIN + WHERE Trap

This is one of the most common SQL mistakes.

Suppose the requirement is:

> Return every customer, but include only completed orders when they exist.

A first attempt might be:

```sql
SELECT
    c.customer_id,
    o.order_id
FROM customers AS c
LEFT JOIN orders AS o
    ON o.customer_id = c.customer_id
WHERE o.status = 'completed';
```

This looks like a LEFT JOIN.

But the WHERE condition removes rows where:

```text
o.status = NULL
```

For customers with no order, the right-side columns are NULL.

Therefore:

```text
o.status = 'completed'
→ UNKNOWN
```

and the row is removed.

The result behaves like an INNER JOIN for that condition.

---

## 22.1 Correct pattern

Put the right-side condition into the join predicate:

```sql
SELECT
    c.customer_id,
    o.order_id
FROM customers AS c
LEFT JOIN orders AS o
    ON o.customer_id = c.customer_id
   AND o.status = 'completed';
```

Now:

```text
all customers remain
```

and only completed orders are matched.

---

## 22.2 Why the difference matters

Conceptually:

### Query A

```text
LEFT JOIN
    ↓
preserve unmatched customers
    ↓
WHERE removes NULL-side rows
```

### Query B

```text
LEFT JOIN with status condition
    ↓
only completed orders qualify as matches
    ↓
unmatched customers remain
```

This is an important example of how **filter location changes semantics**.

---

# 23. Semi-Joins

Sometimes you do not need columns from the right table.

You only need to know:

> Does a matching row exist?

That is the conceptual purpose of a **semi-join**.

---

## 23.1 EXISTS pattern

```sql
SELECT
    c.customer_id,
    c.country
FROM customers AS c
WHERE EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.customer_id
);
```

This answers:

> Return customers for whom at least one matching order exists.

---

## 23.2 Why this is not the same as JOIN

Suppose customer 1 has three orders.

Normal join:

```sql
SELECT c.customer_id
FROM customers AS c
JOIN orders AS o
    ON o.customer_id = c.customer_id;
```

can produce:

```text
1
1
1
```

because there are three matching order rows.

But:

```sql
SELECT c.customer_id
FROM customers AS c
WHERE EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.customer_id
);
```

produces:

```text
1
```

once.

The business question is different.

```text
JOIN:
"Give me every matching pair."

EXISTS:
"Does at least one match exist?"
```

---

## 23.3 `IN` as a membership test

You can also write:

```sql
SELECT
    c.customer_id
FROM customers AS c
WHERE c.customer_id IN (
    SELECT o.customer_id
    FROM orders AS o
);
```

This expresses membership.

As covered in the previous topic, `NOT IN` has important NULL hazards. Use care when moving from positive membership to negative membership.

---

# 24. Anti-Joins

An **anti-join** answers:

> Which left rows have no matching right row?

A common data-engineering example:

> Find customers who never placed an order.

---

## 24.1 `NOT EXISTS`

Preferred reasoning pattern:

```sql
SELECT
    c.customer_id
FROM customers AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.customer_id
);
```

This directly expresses:

> no matching order exists.

---

## 24.2 LEFT JOIN anti-join pattern

Another common form:

```sql
SELECT
    c.customer_id
FROM customers AS c
LEFT JOIN orders AS o
    ON o.customer_id = c.customer_id
WHERE o.customer_id IS NULL;
```

This works when the chosen right-side column is NULL for unmatched rows and cannot otherwise be NULL in a way that confuses the test.

The exact assertion should reflect the key's semantics.

---

## 24.3 Why anti-joins matter

They appear in:

- data reconciliation,
- missing-record detection,
- quality checks,
- "customers who never..." reports,
- incremental pipeline validation,
- source-target completeness checks.

---

# 25. NULL Join Keys

This is mandatory to understand.

With an ordinary equality condition:

```sql
ON a.customer_id = b.customer_id
```

a NULL does not equal another NULL.

Remember:

```text
NULL = NULL
→ UNKNOWN
```

So:

```text
a.customer_id = NULL
AND
b.customer_id = NULL
```

does not become TRUE.

---

## 25.1 Example

Table A:

```text
id | customer_id
---+------------
1  | 10
2  | NULL
```

Table B:

```text
id | customer_id
---+------------
7  | 10
8  | NULL
```

Join:

```sql
SELECT
    a.id AS a_id,
    b.id AS b_id
FROM a
JOIN b
    ON a.customer_id = b.customer_id;
```

Only the rows with:

```text
10 = 10
```

match.

The two NULLs do not match.

---

## 25.2 Why this can surprise data engineers

A source system may use NULL to represent:

- unknown customer,
- anonymous user,
- unavailable foreign key,
- not yet assigned relationship.

Then a standard equality join silently leaves those rows unmatched.

That may be correct.

But it must be intentional.

---

## 25.3 Contrast with pandas

Earlier pandas work may have different missing-value matching behavior depending on the data types and pandas semantics.

Do not assume:

```text
"it matched in pandas"
```

means:

```text
"it will match in SQL"
```

Always reason from the target engine's semantics.

---

# 26. Non-Equi Joins

A join does not have to use `=`.

A **non-equi join** uses another comparison or predicate.

Examples:

```sql
a.value >= b.min_value
```

or:

```sql
a.event_time >= b.valid_from
AND a.event_time < b.valid_to
```

These are useful when relationships are based on ranges.

---

## 26.1 Common use cases

- event to price valid at the event time,
- transaction to exchange-rate interval,
- employee to salary band,
- shipment to SLA interval,
- event to campaign validity,
- measurement to threshold range.

---

# 27. Range Joins

## 27.1 Price-validity problem

Suppose historical product prices are stored by validity interval.

```text
product_id | valid_from | valid_to   | price
-----------+------------+------------+------
10         | 2025-01-01 | 2025-02-01 | 100
10         | 2025-02-01 | 2025-03-01 | 105
10         | 2025-03-01 | NULL       | 110
```

Orders:

```text
order_id | product_id | order_time
----------+------------+---------------------
101       | 10         | 2025-02-10 09:00:00
102       | 10         | 2025-03-12 10:00:00
```

---

## 27.2 Range join

For closed-open intervals:

```sql
SELECT
    ol.order_id,
    ol.product_id,
    ol.order_time,
    pp.price
FROM order_lines AS ol
JOIN product_price_history AS pp
    ON pp.product_id = ol.product_id
   AND ol.order_time >= pp.valid_from
   AND ol.order_time < pp.valid_to;
```

If the current row has no upper bound represented as NULL, handle that model explicitly, for example:

```sql
AND (
       ol.order_time < pp.valid_to
       OR pp.valid_to IS NULL
    )
```

depending on the table's design.

---

## 27.3 Why half-open intervals help

Using:

```text
[valid_from, valid_to)
```

means adjacent versions can be written as:

```text
2025-02-01 ≤ time < 2025-03-01
2025-03-01 ≤ time < 2025-04-01
```

The shared boundary belongs to exactly one version.

---

## 27.4 Critical edge case — overlapping ranges

Suppose the price history accidentally contains:

```text
10 | 2025-03-01 | 2025-04-01 | 110
10 | 2025-03-15 | 2025-04-15 | 115
```

An order on:

```text
2025-03-20
```

matches both rows.

The join has become:

```text
one order
×
two price records
=
two outputs
```

This may silently duplicate revenue.

Therefore range joins require a stronger integrity rule:

> **For a given business key, validity intervals must not overlap unless multiple matches are intentionally allowed.**

---

# 28. DuckDB ASOF JOIN

DuckDB provides `ASOF JOIN` for a common temporal lookup pattern.

The business question is:

> For each left row, find the most recent right-side record at or before the left timestamp.

This is different from a simple equality join.

---

## 28.1 Conceptual example

Orders:

```text
product_id | order_time
-----------+-------------------
10         | 2025-02-10 09:00
10         | 2025-03-12 10:00
```

Price history:

```text
product_id | price_time | price
-----------+------------+------
10         | 2025-01-01 | 100
10         | 2025-02-01 | 105
10         | 2025-03-01 | 110
```

For:

```text
2025-02-10
```

the correct price is:

```text
105
```

because that is the latest price at or before the order time.

For:

```text
2025-03-12
```

the correct price is:

```text
110
```

---

## 28.2 Representative DuckDB syntax

A representative DuckDB ASOF query is:

```sql
SELECT
    o.order_id,
    o.product_id,
    o.order_time,
    p.price
FROM orders AS o
ASOF JOIN product_prices AS p
    ON o.product_id = p.product_id
   AND o.order_time >= p.price_time;
```

The exact ASOF syntax and behavior should be verified against the DuckDB version in your environment.

> **Dialect:** DuckDB-specific / non-standard SQL feature.

---

## 28.3 Mental model

Think:

```text
for each order:
    find price rows for the same product
    keep rows at or before order_time
    choose the latest eligible price
```

This is why ASOF JOIN is especially useful for time-series enrichment.

---

# 29. PostgreSQL LATERAL Alternative

PostgreSQL provides `LATERAL`, which can express an ASOF-style correlated lookup.

Example:

```sql
SELECT
    o.order_id,
    o.product_id,
    o.order_time,
    p.price
FROM orders AS o
LEFT JOIN LATERAL (
    SELECT
        pp.price
    FROM product_price_history AS pp
    WHERE pp.product_id = o.product_id
      AND pp.valid_from <= o.order_time
      AND (
            pp.valid_to > o.order_time
            OR pp.valid_to IS NULL
          )
    ORDER BY
        pp.valid_from DESC
    LIMIT 1
) AS p
    ON TRUE;
```

The right-side subquery can reference:

```text
o.product_id
o.order_time
```

from the current left row.

This is the key purpose of `LATERAL`.

---

# 30. LATERAL Joins

## 30.1 What is LATERAL?

Conceptually:

> A `LATERAL` subquery is allowed to reference columns from the row currently being processed on the left.

Without LATERAL, a derived table normally behaves as an independent query source.

With LATERAL:

```text
left row
   ↓
right-side subquery can see left-row values
   ↓
return matching right-side rows
```

---

## 30.2 Why it exists

Some problems are naturally expressed as:

> "For each parent row, find the best N related records."

Examples:

- latest 3 orders,
- most recent event,
- nearest price,
- top candidate per entity,
- most recent status,
- per-customer lookup against history.

---

## 30.3 Why it can be expensive

The conceptual model is close to:

```text
for each left row
    run a correlated lookup
```

That can be extremely useful when the lookup is selective and has a good access path.

But if the left side contains millions of rows and the inner operation is expensive, the repeated work can become costly.

The optimizer may transform or optimize parts of the operation, but the engineering point remains:

> Understand the number and cost of per-row lookups.

Detailed plan analysis belongs to Topic 08.

---

# 31. Latest N Rows Per Parent

This is the required production pattern.

Suppose:

```text
customers
→ one row per customer

orders
→ one row per order
```

Requirement:

> Return the latest three orders for every customer.

Using PostgreSQL `LATERAL`:

```sql
SELECT
    c.customer_id,
    o.order_id,
    o.created_at
FROM customers AS c
LEFT JOIN LATERAL (
    SELECT
        order_id,
        created_at
    FROM orders
    WHERE orders.customer_id = c.customer_id
    ORDER BY
        created_at DESC,
        order_id DESC
    LIMIT 3
) AS o
    ON TRUE
ORDER BY
    c.customer_id,
    o.created_at DESC,
    o.order_id DESC;
```

---

## 31.1 Why the tie-breaker matters

This:

```sql
ORDER BY created_at DESC
```

may leave ties unresolved.

Use:

```sql
ORDER BY created_at DESC, order_id DESC
```

when `order_id` is unique.

This makes the "latest three" definition deterministic.

---

## 31.2 Output grain

For this query the output is:

```text
one row per selected customer-order combination
```

not:

```text
one row per customer
```

Customers with no orders can still appear because the outer join is a LEFT JOIN.

---

## 31.3 Why `LIMIT 3` works here

Because the subquery is correlated to each customer.

Conceptually:

```text
customer 1 → find that customer's orders → keep 3
customer 2 → find that customer's orders → keep 3
customer 3 → find that customer's orders → keep 3
```

That is different from:

```sql
SELECT *
FROM orders
ORDER BY created_at DESC
LIMIT 3;
```

which would return three orders globally.

---

# 32. NATURAL JOIN Dangers

`NATURAL JOIN` automatically joins columns that have the same names.

Example:

```sql
SELECT *
FROM customers
NATURAL JOIN orders;
```

This can be dangerous in production because the join condition is implicit.

---

## 32.1 Schema evolution example

Suppose today:

```text
customers
customer_id
name

orders
order_id
customer_id
```

A NATURAL JOIN effectively matches:

```text
customer_id
```

Now later the schema evolves:

```text
customers
customer_id
name
status

orders
order_id
customer_id
status
```

The NATURAL JOIN may now use:

```text
customer_id
AND
status
```

instead of only:

```text
customer_id
```

The SQL text did not change.

The schema changed.

The join semantics changed.

That is a dangerous production property.

---

## 32.2 Recommended production habit

Prefer explicit:

```sql
JOIN orders AS o
    ON o.customer_id = c.customer_id
```

when the business relationship needs to be obvious.

Explicitness protects queries from accidental semantic changes caused by future shared column names.

---

# 33. USING Dangers and Deliberate Use

`USING` is not the same as `NATURAL JOIN`.

With:

```sql
JOIN orders
USING (customer_id)
```

you explicitly named:

```text
customer_id
```

as the join column.

That is much more controlled.

Still, there are reasons to prefer `ON`:

- the join logic may be more complex,
- column names may differ,
- you may want explicit qualified comparisons,
- reviewers may need to see exactly which columns participate.

Use:

```sql
USING (customer_id)
```

when the shared-key relationship is simple and obvious.

Use:

```sql
ON o.customer_id = c.customer_id
```

when the explicit condition improves clarity.

---

# 34. Join Algorithms

So far we have discussed **logical joins**.

The database also needs a **physical algorithm** to find matching rows.

Keep these concepts separate:

```text
Logical question:
Which rows should match?

Physical question:
How can the database find those matches efficiently?
```

The main conceptual join algorithms are:

- nested loop,
- hash join,
- merge join.

This section is intentionally conceptual. Detailed `EXPLAIN` analysis belongs to Topic 08.

---

# 35. Nested Loop Join

## 35.1 Mental model

Conceptually:

```text
For each row in A:
    look for matching rows in B
```

If:

```text
A has 5 rows
```

the database conceptually performs five inner-side lookup phases.

---

## 35.2 When it can be useful

Nested loops can be attractive when:

- the outer side is small,
- the inner lookup is selective,
- the inner side has an efficient access path,
- a correlated/per-row lookup is appropriate.

Example:

```text
1 customer
→ find that customer's latest orders
```

can naturally resemble a repeated lookup.

---

## 35.3 When it can be expensive

If:

```text
A = millions of rows
B = millions of rows
```

and each outer row causes a large scan of B, the work can become very large.

Do not simplify this to:

> "Nested loops are always bad."

The optimizer chooses based on the estimated cost and available access paths.

---

# 36. Hash Join

## 36.1 Mental model

For an equality join, the engine can conceptually:

```text
1. Build a hash structure for one side.
2. Read the other side.
3. Hash its join key.
4. Find matching entries.
```

Visual:

```text
Build side
rows
  ↓
hash table
  ↑
probe keys
from other side
```

---

## 36.2 Good fit

Hash joins are often useful for:

- equality joins,
- large unsorted inputs,
- situations where a hash structure fits the workload.

---

## 36.3 Main concern

Memory matters.

A large hash structure can require significant memory and may need execution strategies that account for limited memory.

Do not confuse:

```text
logical join cardinality
```

with:

```text
physical hash-table memory usage
```

They are related but different questions.

---

# 37. Merge Join

## 37.1 Mental model

A merge join works from ordered inputs.

Conceptually:

```text
sorted A
   +
sorted B
   ↓
walk through both inputs
```

When keys are ordered, the engine can advance through the inputs without comparing every possible pair.

---

## 37.2 Why sort order matters

If inputs are already appropriately ordered, a merge join may avoid some sorting work.

If they are not ordered, obtaining the required order has a cost.

---

## 37.3 Conceptual comparison

| Algorithm | Good fit | Typical requirement | Main concern |
|---|---|---|---|
| Nested Loop | small/selective lookup | efficient inner access path | repeated work |
| Hash Join | equality joins | hashable keys and memory | memory |
| Merge Join | ordered inputs | sorted inputs or affordable sorting | sort cost |

These are conceptual patterns, not absolute rules.

---

# 38. Join Algorithm Decision Intuition

As a data engineer, you do not normally choose the algorithm manually in everyday SQL.

You write correct SQL and the optimizer chooses a physical plan.

Your job is to understand enough to interpret the behavior.

Think:

```text
Logical join
    ↓
Cardinality
    ↓
Available access paths / ordering / memory
    ↓
Optimizer chooses physical strategy
```

Later, Topic 08 will teach how to inspect this with execution plans.

---

# 39. Join Reconciliation

After a significant join, especially one feeding a business metric, reconcile the result.

Check:

- source row count,
- joined row count,
- distinct key count,
- unmatched rows,
- duplicate keys,
- totals,
- expected business metrics.

---

## 39.1 Basic row-count check

Source:

```sql
SELECT COUNT(*)
FROM orders;
```

Joined:

```sql
SELECT COUNT(*)
FROM orders AS o
JOIN customers AS c
    ON c.customer_id = o.customer_id;
```

If the count falls, ask:

> How many orders lack a matching customer?

That may be expected or may expose missing dimension data.

---

## 39.2 Unmatched-order assertion

```sql
SELECT
    o.order_id
FROM orders AS o
LEFT JOIN customers AS c
    ON c.customer_id = o.customer_id
WHERE c.customer_id IS NULL;
```

Expected:

```text
0 rows
```

if every order is required to have a customer.

---

## 39.3 Distinct-key comparison

```sql
SELECT
    COUNT(DISTINCT order_id)
FROM orders;
```

Compare with the joined result:

```sql
SELECT
    COUNT(DISTINCT o.order_id)
FROM orders AS o
JOIN customers AS c
    ON c.customer_id = o.customer_id;
```

This can reveal whether orders were lost during an INNER JOIN.

---

## 39.4 Total reconciliation

For financial measures:

```sql
SELECT SUM(amount)
FROM orders;
```

Then compare to the intended joined metric.

If the amount increases after a join, do not immediately conclude the join is wrong.

First determine whether:

- row grain changed,
- the metric should be summed at the new grain,
- the same amount is legitimately repeated,
- the join created multiplication.

---

# 40. Join Reconciliation Checks

A production join should have explicit checks for its expected behavior.

---

## 40.1 Duplicate dimension keys

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

if customers are intended to be one row per customer.

---

## 40.2 Orphan fact keys

```sql
SELECT
    o.order_id
FROM orders AS o
LEFT JOIN customers AS c
    ON c.customer_id = o.customer_id
WHERE c.customer_id IS NULL;
```

Expected:

```text
0 rows
```

if referential completeness is required.

---

## 40.3 Unexpected multiplicity after join

Suppose the output should be one row per order.

Use:

```sql
SELECT
    o.order_id,
    COUNT(*) AS joined_rows
FROM orders AS o
JOIN order_lines AS ol
    ON ol.order_id = o.order_id
GROUP BY o.order_id
HAVING COUNT(*) > 1;
```

But note:

> This query is not necessarily a failure.

If the intended output is one row per order line, multiple rows per order are expected.

The assertion must match the **intended output grain**.

---

## 40.4 Metric reconciliation

A useful pattern is:

```sql
WITH source_totals AS (
    SELECT
        SUM(amount) AS source_amount
    FROM orders
),
joined_totals AS (
    SELECT
        SUM(...) AS joined_amount
    FROM ...
)
SELECT
    source_amount,
    joined_amount,
    joined_amount - source_amount AS difference
FROM source_totals
CROSS JOIN joined_totals;
```

The exact metric expression depends on the intended grain.

The purpose is to make discrepancies visible before they reach a report.

---

# 41. Join Debugging Methodology

When a join produces too many rows, do not randomly add `DISTINCT`.

Use a repeatable investigation.

## Step 1 — State the grain

```text
orders
→ one row per order

payments
→ one row per payment
```

---

## Step 2 — State the intended output grain

Example:

```text
one row per order
```

---

## Step 3 — Identify join keys

```text
orders.order_id
payments.order_id
```

---

## Step 4 — Validate uniqueness

```sql
SELECT
    order_id,
    COUNT(*)
FROM payments
GROUP BY order_id
HAVING COUNT(*) > 1;
```

If payments are intentionally one-to-many, the result should contain duplicates by order.

That is not a data-quality failure.

It simply tells you the cardinality is 1:N.

---

## Step 5 — Classify cardinality

```text
orders → payments = 1:N
```

---

## Step 6 — Predict output row count

Suppose:

```text
Order 101 → 3 payments
Order 102 → 1 payment
Order 103 → 0 payments
```

INNER JOIN output:

```text
3 + 1 = 4 rows
```

LEFT JOIN output:

```text
3 + 1 + 1 unmatched row = 5 rows
```

This is exactly the kind of prediction you should make before executing.

---

## Step 7 — Run the join without aggregation

Do not start with:

```sql
SUM(...)
GROUP BY ...
```

First inspect raw joined rows.

```sql
SELECT
    o.order_id,
    p.payment_id
FROM orders AS o
LEFT JOIN payments AS p
    ON p.order_id = o.order_id
ORDER BY
    o.order_id,
    p.payment_id;
```

Aggregation can hide the multiplication.

---

## Step 8 — Measure multiplicity

```sql
SELECT
    o.order_id,
    COUNT(*) AS joined_rows
FROM orders AS o
JOIN payments AS p
    ON p.order_id = o.order_id
GROUP BY o.order_id
ORDER BY joined_rows DESC;
```

This quickly exposes exploding keys.

---

## Step 9 — Isolate each join

Run:

```text
orders → order_lines
```

then:

```text
orders → payments
```

then:

```text
orders → order_lines → payments
```

Compare row growth after each step.

---

## Step 10 — Repair at the correct grain

Pre-aggregate:

```text
order_lines → one row per order
payments → one row per order
```

then join.

---

## Step 11 — Reconcile again

Check:

- row count,
- distinct orders,
- totals,
- unmatched keys.

---

# 42. Debugging a Fan Trap Step by Step

Use this scenario as a production debugging drill.

## 42.1 Scenario

A report says:

```text
Revenue before new joins: 300
Revenue after new joins: 700
```

The query was changed from:

```sql
FROM orders
```

to:

```sql
FROM orders
JOIN order_lines
    ON ...
JOIN payments
    ON ...
```

---

## 42.2 Step 1 — Inspect grain

```text
orders
→ one row per order

order_lines
→ one row per order line

payments
→ one row per payment
```

---

## 42.3 Step 2 — Inspect one order

Suppose:

```text
order_id = 101
```

has:

```text
3 order lines
2 payments
```

---

## 42.4 Step 3 — Predict

```text
3 × 2
=
6 joined rows
```

---

## 42.5 Step 4 — Prove it

```sql
SELECT
    o.order_id,
    ol.order_line_id,
    p.payment_id
FROM orders AS o
JOIN order_lines AS ol
    ON ol.order_id = o.order_id
JOIN payments AS p
    ON p.order_id = o.order_id
WHERE o.order_id = 101
ORDER BY
    ol.order_line_id,
    p.payment_id;
```

You should see six combinations.

---

## 42.6 Step 5 — Inspect the metric

If:

```text
order amount = 100
```

then:

```text
100 repeated × 6 rows
=
600
```

The inflation is now explained.

---

## 42.7 Step 6 — Fix

Aggregate independently:

```sql
WITH line_totals AS (
    SELECT
        order_id,
        SUM(quantity * unit_price) AS line_revenue
    FROM order_lines
    GROUP BY order_id
),
payment_totals AS (
    SELECT
        order_id,
        SUM(amount) AS paid_amount
    FROM payments
    GROUP BY order_id
)
SELECT
    o.order_id,
    o.amount,
    lt.line_revenue,
    pt.paid_amount
FROM orders AS o
LEFT JOIN line_totals AS lt
    ON lt.order_id = o.order_id
LEFT JOIN payment_totals AS pt
    ON pt.order_id = o.order_id;
```

---

## 42.8 Step 7 — Reconcile

```text
order count
distinct order count
sum of source order amount
sum of intended revenue
```

Only after the totals reconcile should the query be considered repaired.

---

# 43. Production Patterns

## Pattern 1 — Parent + one child

Scenario:

```text
customers
JOIN orders
```

If the output is order grain, this can be straightforward:

```text
orders → customers = N:1
```

Check customer uniqueness first.

---

## Pattern 2 — Parent + multiple children

Scenario:

```text
orders
+ order_lines
+ payments
```

If the desired output is order grain:

```text
pre-aggregate each child to order grain first
```

This is the classic fan-trap prevention pattern.

---

## Pattern 3 — Existence testing

Requirement:

> Customers who have at least one order.

Use:

```sql
WHERE EXISTS (...)
```

rather than creating duplicate customers through a regular join.

---

## Pattern 4 — Missing-record detection

Requirement:

> Customers who have no orders.

Use:

```sql
WHERE NOT EXISTS (...)
```

or an appropriate anti-join.

---

## Pattern 5 — Point-in-time/range lookup

Requirement:

> Price valid when the order occurred.

Use a range join or an engine-specific temporal join.

---

## Pattern 6 — Latest N related records

Requirement:

> Latest three orders per customer.

Use PostgreSQL `LATERAL` when appropriate:

```sql
LEFT JOIN LATERAL (...)
```

with deterministic ordering.

---

## Pattern 7 — Source-to-target reconciliation

Requirement:

> Find records present in one table but not the other.

A FULL OUTER JOIN can help expose:

```text
source-only
matched
target-only
```

provided the join key and uniqueness assumptions are sound.

---

## Pattern 8 — Dimension uniqueness validation

Before joining facts to dimensions:

```sql
SELECT
    business_key,
    COUNT(*)
FROM dimension
GROUP BY business_key
HAVING COUNT(*) > 1;
```

Expected:

```text
0 rows
```

if the dimension is supposed to be unique at that grain.

---

# 44. Common Join Mistakes

## Mistake 1 — Thinking in Venn diagrams only

### Why it fails

Venn diagrams do not naturally show how duplicate matches multiply rows.

### Better approach

Think:

```text
for each left row
    find every matching right row
```

---

## Mistake 2 — Not stating table grain

### Why it fails

You cannot predict output cardinality without knowing what one row represents.

### Better approach

Write:

```text
orders → one row per order
payments → one row per payment
```

before the SQL.

---

## Mistake 3 — Assuming a key is unique

### Why it fails

A column named:

```text
customer_id
```

does not prove uniqueness.

### Better approach

Assert:

```sql
GROUP BY customer_id
HAVING COUNT(*) > 1
```

---

## Mistake 4 — Joining two child tables directly

### Why it fails

Independent one-to-many relationships multiply.

### Better approach

Pre-aggregate each child to the intended parent grain.

---

## Mistake 5 — Using DISTINCT as a band-aid

### Why it fails

```sql
SELECT DISTINCT ...
```

may hide duplicated rows without fixing the underlying grain problem.

Worse, it can remove legitimate duplicates.

### Better approach

Fix the relationship or aggregation grain.

---

## Mistake 6 — Aggregating after an exploding join

### Why it fails

The aggregation sees multiplied rows.

### Better approach

Aggregate independent child datasets before combining them.

---

## Mistake 7 — LEFT JOIN + WHERE on the right table

### Why it fails

The WHERE predicate removes NULL-side rows and can effectively turn the result into inner-join behavior.

### Better approach

Move the right-side filter into `ON` when unmatched left rows must be preserved.

---

## Mistake 8 — Ignoring NULL join keys

### Why it fails

NULLs do not match through ordinary equality.

### Better approach

Understand the source semantics and explicitly define how unknown keys should behave.

---

## Mistake 9 — Accidental many-to-many join

### Why it fails

Both sides contain multiple matches for the joining key.

### Better approach

Classify cardinality before execution.

---

## Mistake 10 — Accidental CROSS JOIN

### Why it fails

Rows can multiply as:

```text
rows(A) × rows(B)
```

### Better approach

Verify that every intended relationship has an appropriate join condition.

---

## Mistake 11 — NATURAL JOIN in production

### Why it fails

Schema changes can silently change the join condition.

### Better approach

Use explicit `ON` or deliberate `USING`.

---

## Mistake 12 — Overlapping range intervals

### Why it fails

One event can match multiple historical versions.

### Better approach

Validate temporal interval integrity.

---

## Mistake 13 — Non-deterministic latest-record lookup

### Why it fails

If timestamps tie and there is no tie-breaker, "latest" may not uniquely identify one row.

### Better approach

Use:

```sql
ORDER BY event_time DESC, unique_id DESC
```

when appropriate.

---

## Mistake 14 — Failing to reconcile totals

### Why it fails

The query may look plausible while metrics are already corrupted.

### Better approach

Compare counts, distinct keys, and business totals before and after the join.

---

# 45. Why SELECT DISTINCT Is Often a Bad Fix

Suppose your join creates:

```text
order_id = 101
6 joined rows
```

You may be tempted to write:

```sql
SELECT DISTINCT
    o.order_id,
    o.amount
FROM ...
```

This might collapse six identical-looking order rows into one.

But that does not prove the query is correct.

Why?

Because the join may contain important information that was different across the six rows.

For example:

```text
payment_id
order_line_id
```

may differ.

If you use:

```sql
DISTINCT
```

on a reduced set of columns, you may simply discard evidence of the join problem.

---

## 45.1 The correct question

Do not ask:

> "How do I make the duplicates disappear?"

Ask:

> **"Why did these rows become duplicates at the business grain?"**

Then repair the grain.

---

# 46. Why "Just GROUP BY" Is Not a Universal Fix

Another common reaction is:

```sql
GROUP BY order_id
```

This can reduce row count.

But aggregation does not necessarily make the metric correct.

Example:

```sql
SUM(o.amount)
```

after a fan-trap join is still inflated.

Changing the grouping key does not remove the multiplication that already happened.

The correct repair is to choose the right grain **before** the metric is repeated.

---

# 47. Production Case Study

## 47.1 Business context

A subscription/e-commerce business has:

```text
customers
orders
order_lines
payments
shipments
```

The finance report needs:

```text
one row per order
```

with:

```text
order revenue
number of units
amount paid
shipment count
```

---

## 47.2 The new engineer's query

```sql
SELECT
    o.order_id,
    SUM(o.amount) AS revenue,
    SUM(ol.quantity) AS units,
    SUM(p.amount) AS paid_amount,
    COUNT(s.shipment_id) AS shipment_count
FROM orders AS o
LEFT JOIN order_lines AS ol
    ON ol.order_id = o.order_id
LEFT JOIN payments AS p
    ON p.order_id = o.order_id
LEFT JOIN shipments AS s
    ON s.order_id = o.order_id
GROUP BY
    o.order_id;
```

The query looks reasonable.

It is also dangerous.

---

## 47.3 State grains

```text
orders
→ one row per order

order_lines
→ one row per line

payments
→ one row per payment

shipments
→ one row per shipment
```

---

## 47.4 Suppose order 101 has

```text
3 order lines
2 payments
2 shipments
```

The combination count can become:

```text
3 × 2 × 2
=
12 rows
```

---

## 47.5 Consequences

If:

```text
order revenue = 100
```

then:

```text
SUM(o.amount)
=
100 × 12
=
1200
```

The units and paid amount can also be inflated.

Shipment count can be inflated as well.

---

## 47.6 Correct strategy

Create one summary per child:

```text
line_summary
→ one row per order

payment_summary
→ one row per order

shipment_summary
→ one row per order
```

Then:

```text
orders
1:1
line_summary
1:1
payment_summary
1:1
shipment_summary
```

---

## 47.7 Corrected query

```sql
WITH line_summary AS (
    SELECT
        order_id,
        SUM(quantity) AS units
    FROM order_lines
    GROUP BY order_id
),
payment_summary AS (
    SELECT
        order_id,
        SUM(amount) AS paid_amount
    FROM payments
    GROUP BY order_id
),
shipment_summary AS (
    SELECT
        order_id,
        COUNT(*) AS shipment_count
    FROM shipments
    GROUP BY order_id
)
SELECT
    o.order_id,
    o.amount AS revenue,
    COALESCE(ls.units, 0) AS units,
    COALESCE(ps.paid_amount, 0) AS paid_amount,
    COALESCE(ss.shipment_count, 0) AS shipment_count
FROM orders AS o
LEFT JOIN line_summary AS ls
    ON ls.order_id = o.order_id
LEFT JOIN payment_summary AS ps
    ON ps.order_id = o.order_id
LEFT JOIN shipment_summary AS ss
    ON ss.order_id = o.order_id;
```

---

## 47.8 Why this is correct

Every source is represented at order grain:

```text
orders
→ one row/order

line_summary
→ one row/order

payment_summary
→ one row/order

shipment_summary
→ one row/order
```

No independent child multiplicities remain.

---

## 47.9 Required reconciliation

Before trusting the report:

```sql
SELECT
    SUM(amount)
FROM orders;
```

Compare with:

```text
SUM(revenue in final report)
```

Also compare:

```text
COUNT(orders)
COUNT(DISTINCT order_id in final report)
```

and:

```text
orders without valid customer
orders without expected children
duplicate summary keys
```

---

# 48. Documentation Requirement

Production SQL should document critical assumptions.

A useful block is:

```text
Assumption:
customer_id is unique in customers.

Expected relationship:
customers → orders = 1:N.

Expected output grain:
one row per order.

Validation:
GROUP BY customer_id HAVING COUNT(*) > 1
must return zero rows.
```

Another example:

```text
Assumption:
payment_summary contains at most one row per order.

Expected relationship:
orders → payment_summary = 1:1.

Output grain:
one row per order.

Validation:
GROUP BY order_id HAVING COUNT(*) > 1
must return zero rows.
```

This makes the query reviewable by another engineer.

---

# 49. Hands-On Exercises

These exercises follow the module roadmap and are designed to force grain-first reasoning.

---

## Exercise 1 — Revenue with fan-trap inflation

### Objective

See row multiplication numerically.

### Setup

```sql
CREATE TEMP TABLE e1_orders (
    order_id INTEGER,
    amount NUMERIC
);

INSERT INTO e1_orders VALUES
    (101, 100),
    (102, 200);

CREATE TEMP TABLE e1_order_lines (
    line_id INTEGER,
    order_id INTEGER,
    quantity INTEGER,
    unit_price NUMERIC
);

INSERT INTO e1_order_lines VALUES
    (1, 101, 1, 40),
    (2, 101, 1, 30),
    (3, 101, 1, 30),
    (4, 102, 2, 100);

CREATE TEMP TABLE e1_payments (
    payment_id INTEGER,
    order_id INTEGER,
    amount NUMERIC
);

INSERT INTO e1_payments VALUES
    (1, 101, 60),
    (2, 101, 40),
    (3, 102, 200);
```

### Task

1. State every table's grain.
2. Predict the cardinality.
3. Predict output rows for order 101.
4. Run:

```sql
SELECT
    o.order_id,
    SUM(o.amount) AS revenue
FROM e1_orders AS o
JOIN e1_order_lines AS ol
    ON ol.order_id = o.order_id
JOIN e1_payments AS p
    ON p.order_id = o.order_id
GROUP BY o.order_id;
```

5. Explain the incorrect revenue.
6. Fix it with two pre-aggregation CTEs.

### Expected reasoning

For order 101:

```text
3 lines × 2 payments = 6 rows
```

### Production lesson

Never aggregate parent-level metrics after combining independent child tables unless you have proven the resulting grain is appropriate.

---

# Exercise 2 — Duplicate product key

### Objective

Show how a duplicate "dimension" key multiplies facts.

### Setup

```sql
CREATE TEMP TABLE e2_products (
    product_id INTEGER,
    price NUMERIC
);

INSERT INTO e2_products VALUES
    (10, 100),
    (10, 105),
    (20, 200);

CREATE TEMP TABLE e2_orders (
    order_id INTEGER,
    product_id INTEGER,
    amount NUMERIC
);

INSERT INTO e2_orders VALUES
    (101, 10, 100),
    (102, 20, 200);
```

### Task

Run:

```sql
SELECT
    o.order_id,
    o.amount,
    p.price
FROM e2_orders AS o
JOIN e2_products AS p
    ON p.product_id = o.product_id;
```

Then write:

```sql
SELECT
    product_id,
    COUNT(*)
FROM e2_products
GROUP BY product_id
HAVING COUNT(*) > 1;
```

### Expected behavior

Order 101 appears twice.

### Production lesson

A supposed one-side must be validated.

---

# Exercise 3 — LEFT JOIN + WHERE bug

### Objective

Understand the semantic difference between filtering before versus after an outer join.

### Setup

```sql
CREATE TEMP TABLE e3_customers (
    customer_id INTEGER
);

INSERT INTO e3_customers VALUES
    (1), (2), (3);

CREATE TEMP TABLE e3_orders (
    order_id INTEGER,
    customer_id INTEGER,
    status TEXT
);

INSERT INTO e3_orders VALUES
    (101, 1, 'completed'),
    (102, 1, 'cancelled'),
    (103, 2, 'completed');
```

### Task

Compare:

```sql
SELECT
    c.customer_id,
    o.order_id
FROM e3_customers AS c
LEFT JOIN e3_orders AS o
    ON o.customer_id = c.customer_id
WHERE o.status = 'completed';
```

with:

```sql
SELECT
    c.customer_id,
    o.order_id
FROM e3_customers AS c
LEFT JOIN e3_orders AS o
    ON o.customer_id = c.customer_id
   AND o.status = 'completed';
```

### Expected reasoning

The first removes customer 3.

The second preserves customer 3.

### Production lesson

When preserving unmatched left rows, think carefully about whether a right-side predicate belongs in `ON` or `WHERE`.

---

# Exercise 4 — Customers with no orders

### Objective

Practice anti-joins.

### Task

Solve the requirement three ways where appropriate:

> Find customers who have no orders.

Use:

```sql
NOT EXISTS
```

and:

```sql
LEFT JOIN ... WHERE right_key IS NULL
```

Then examine a `NOT IN` form and explain its NULL risks.

### Expected reasoning

Focus on the business question:

```text
No matching order exists.
```

---

# Exercise 5 — Range price lookup

### Objective

Match each order to the price valid at order time.

### Setup

```sql
CREATE TEMP TABLE e5_price_history (
    product_id INTEGER,
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    price NUMERIC
);

INSERT INTO e5_price_history VALUES
    (10, '2025-01-01 00:00:00', '2025-02-01 00:00:00', 100),
    (10, '2025-02-01 00:00:00', '2025-03-01 00:00:00', 105),
    (10, '2025-03-01 00:00:00', NULL, 110);

CREATE TEMP TABLE e5_orders (
    order_id INTEGER,
    product_id INTEGER,
    order_time TIMESTAMP
);

INSERT INTO e5_orders VALUES
    (101, 10, '2025-01-15 10:00:00'),
    (102, 10, '2025-02-10 10:00:00'),
    (103, 10, '2025-03-10 10:00:00');
```

### Task

Write a range join using:

```text
valid_from <= order_time < valid_to
```

and explicitly handle an open-ended current interval.

### Edge case

What happens if two price intervals overlap?

Prove that one order may then produce multiple rows.

---

# Exercise 6 — DuckDB ASOF JOIN

### Objective

Use DuckDB's temporal join feature.

### Task

Rewrite the price lookup as a DuckDB `ASOF JOIN`.

### Requirements

Explain:

- what "as of" means,
- why the latest eligible timestamp is selected,
- what part is DuckDB-specific.

### Edge case

Create two price records with the same timestamp and explain why the versioning rules must be well defined.

---

# Exercise 7 — LATERAL

### Objective

Use a per-parent lookup.

### Task

Return the latest three orders per customer in PostgreSQL.

Use:

```sql
LEFT JOIN LATERAL
```

and:

```sql
ORDER BY created_at DESC, order_id DESC
LIMIT 3
```

### Expected reasoning

State:

```text
Left grain:
one row per customer

Right subquery:
customer-specific order lookup

Output:
up to three order rows per customer
```

---

# Exercise 8 — Join cardinality prediction

### Objective

Train row-count intuition.

Create tiny tables that represent:

```text
1:1
1:N
N:1
N:M
```

Before every query, write:

```text
left rows:
right rows:
unique key:
relationship:
expected output rows:
```

Then execute and compare.

---

# Exercise 9 — Join reconciliation

### Objective

Detect data loss and row multiplication.

For a source table and joined target:

Compare:

```text
COUNT(*)
COUNT(DISTINCT business_key)
SUM(metric)
unmatched records
duplicate keys
```

Write assertion queries that return zero rows when the relationship is valid.

---

# Exercise 10 — Production debugging

### Scenario

A report's revenue increased 3× after a JOIN.

### Task

Do not immediately use `DISTINCT`.

Instead:

1. State grain.
2. Identify keys.
3. Check key uniqueness.
4. Determine cardinality.
5. Count matches per parent.
6. Remove aggregation.
7. Identify multiplication.
8. Pre-aggregate.
9. Reconcile totals.
10. Write a test that prevents regression.

### Production lesson

A join bug is often a grain problem disguised as a metric problem.

---

# 50. Beginner Practice

Complete these without copying the examples.

## 1. INNER JOIN basics

Join orders to customers and return:

```text
order_id
customer_id
country
```

State the output grain.

---

## 2. LEFT JOIN

Return every customer and their order ID where available.

State what an unmatched customer looks like.

---

## 3. RIGHT JOIN

Write a RIGHT JOIN that preserves every order.

Then rewrite it as a LEFT JOIN with the preserved table on the left.

---

## 4. FULL OUTER JOIN

Reconcile two small customer tables.

Identify:

```text
left-only
matched
right-only
```

---

## 5. CROSS JOIN

Create:

```text
3 customers
×
4 dates
```

and predict the exact row count.

---

## 6. Self-join

Show employees and managers.

State the grain on each side.

---

## 7. ON

Join tables where the key names differ.

Example:

```text
customer_id
cust_id
```

---

## 8. USING

Rewrite a simple shared-key join with:

```sql
USING (customer_id)
```

Explain why it is explicit enough for this case.

---

## 9. Duplicate matching

Create one left row with three right-side matches.

Predict the result count.

---

## 10. Unmatched rows

Create an INNER JOIN and LEFT JOIN over the same data and compare the row counts.

---

# 51. Intermediate Practice

## 1. Cardinality

Given:

```text
customers = 100
orders = 1000
```

with every order belonging to one customer, predict the INNER JOIN output.

---

## 2. One-side uniqueness

Write an assertion proving whether `customer_id` is unique in customers.

---

## 3. Duplicate dimension

Insert a duplicate key and measure row multiplication.

---

## 4. Fan trap

Create:

```text
1 customer
3 orders
2 support tickets
```

then join all three tables by customer and predict:

```text
3 × 2 = 6
```

rows for that customer.

---

## 5. Fan-trap repair

Aggregate orders and tickets separately to customer grain before joining.

---

## 6. LEFT JOIN filtering

Demonstrate why:

```sql
WHERE right.status = ...
```

can remove unmatched rows.

---

## 7. Semi-join

Find customers who have at least one order without returning one row per order.

---

## 8. Anti-join

Find customers with no orders.

---

## 9. NULL keys

Create NULL on both sides and prove that an ordinary equality join does not match them.

---

## 10. Reconciliation

Compare source row counts and joined row counts. Explain every difference.

---

# 52. Advanced Practice

## 1. Range join

Match transactions to exchange-rate intervals.

---

## 2. Overlapping ranges

Create overlapping validity intervals and identify transactions that match more than one version.

---

## 3. ASOF JOIN

Use DuckDB to match events to the most recent prior price.

---

## 4. PostgreSQL LATERAL

Solve the same problem with PostgreSQL.

---

## 5. Latest N

Return the latest three events per user using LATERAL.

---

## 6. Deterministic latest row

Create timestamp ties and add a unique tie-breaker.

---

## 7. NATURAL JOIN hazard

Create two tables whose schemas evolve to introduce another same-named column. Demonstrate how NATURAL JOIN semantics change.

---

## 8. Multi-child fan trap

Join:

```text
orders
order_lines
payments
shipments
refunds
```

and predict the multiplication for an order with:

```text
3 lines
2 payments
2 shipments
2 refunds
```

Expected conceptual multiplier:

```text
3 × 2 × 2 × 2 = 24
```

before considering other unmatched-row behavior.

---

## 9. Algorithm intuition

For several join shapes, discuss when a nested loop, hash join, or merge join might conceptually fit.

Do not attempt to force the database to use one without evidence.

---

## 10. Production case

Build a complete order report at one-row-per-order grain using independent child summaries.

Add:

- grain documentation,
- key uniqueness assertions,
- reconciliation checks,
- deterministic latest-record logic where applicable.

---

# 53. Debugging Challenges

## Challenge 1 — Accidentally duplicated customers

Broken query:

```sql
SELECT
    c.customer_id,
    c.country
FROM customers AS c
JOIN orders AS o
    ON o.customer_id = c.customer_id;
```

### Symptom

Customer rows appear multiple times.

### Diagnosis

The output grain is order-level because customers can have multiple orders.

### Fix

If the requirement is simply "customers with orders", use a semi-join:

```sql
SELECT
    c.customer_id,
    c.country
FROM customers AS c
WHERE EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.customer_id
);
```

---

# Challenge 2 — Revenue inflated by payments and lines

Broken:

```sql
SELECT
    o.order_id,
    SUM(o.amount)
FROM orders AS o
JOIN order_lines AS ol
    ON ol.order_id = o.order_id
JOIN payments AS p
    ON p.order_id = o.order_id
GROUP BY o.order_id;
```

### Symptom

Revenue increases after adding payments.

### Diagnosis

Independent one-to-many children multiply.

### Fix

Pre-aggregate both children.

---

# Challenge 3 — LEFT JOIN became INNER JOIN

Broken:

```sql
SELECT
    c.customer_id,
    o.order_id
FROM customers AS c
LEFT JOIN orders AS o
    ON o.customer_id = c.customer_id
WHERE o.status = 'completed';
```

### Symptom

Customers without completed orders disappear.

### Fix

Move the condition:

```sql
LEFT JOIN orders AS o
    ON o.customer_id = c.customer_id
   AND o.status = 'completed'
```

---

# Challenge 4 — Duplicate dimension key

Symptom:

```text
one order → two product matches
```

Investigation:

```sql
SELECT
    product_id,
    COUNT(*)
FROM products
GROUP BY product_id
HAVING COUNT(*) > 1;
```

Fix the data/model rather than hiding the duplicate with DISTINCT.

---

# Challenge 5 — NULL join key

Symptom:

```text
records expected to match do not match
```

Investigate:

```sql
SELECT *
FROM source
WHERE customer_id IS NULL;
```

and:

```sql
SELECT *
FROM target
WHERE customer_id IS NULL;
```

Remember:

```text
NULL = NULL
→ UNKNOWN
```

---

# Challenge 6 — Accidental Cartesian product

Broken:

```sql
SELECT *
FROM customers AS c
CROSS JOIN orders AS o;
```

or an intended join missing an effective condition.

### Symptom

Row count becomes approximately:

```text
customers × orders
```

### Fix

State the actual business relationship and use an appropriate join predicate.

---

# Challenge 7 — Range join returns multiple prices

### Symptom

One order gets two historical prices.

### Investigation

```sql
SELECT
    product_id,
    valid_from,
    valid_to,
    COUNT(*)
FROM product_price_history
GROUP BY
    product_id,
    valid_from,
    valid_to;
```

Then search for overlapping intervals at the same product.

### Root cause

Temporal validity is not unique.

---

# Challenge 8 — LATERAL latest row is unstable

Broken:

```sql
LEFT JOIN LATERAL (
    SELECT *
    FROM orders
    WHERE orders.customer_id = c.customer_id
    ORDER BY created_at DESC
    LIMIT 1
) AS o ON TRUE;
```

### Symptom

A customer with tied timestamps does not have a stable "latest" row.

### Fix

Add a deterministic tie-breaker:

```sql
ORDER BY
    created_at DESC,
    order_id DESC
```

provided `order_id` uniquely identifies an order.

---

# 54. Interview Questions

## 1. Explain INNER JOIN.

### Short answer

It returns every matching pair of rows.

### Detailed explanation

For each left row, all matching right rows are emitted. Unmatched left and right rows do not appear.

### Example

```sql
SELECT *
FROM orders AS o
JOIN customers AS c
    ON c.customer_id = o.customer_id;
```

### Follow-up

> What happens if the customer key is duplicated?

One order row can match multiple customer rows.

### Common mistake

Thinking "one order will always match one customer because customer_id looks like a key."

---

# 55. Explain LEFT JOIN.

### Short answer

It preserves all left rows and adds matching right-side rows; unmatched right columns become NULL.

### Detailed explanation

A left row can still multiply if multiple right rows match.

### Follow-up

> Can LEFT JOIN produce more rows than the left table?

Yes.

---

# 56. What's the difference between LEFT and FULL OUTER JOIN?

### Short answer

LEFT preserves all left rows. FULL preserves all rows from both sides.

### Follow-up

> When is FULL useful?

Source-target reconciliation.

---

# 57. What happens when the right side has duplicate keys?

### Short answer

A left row can match multiple right rows, producing multiple output rows.

### Example

One customer row + three order rows:

```text
1 × 3 = 3 joined rows
```

---

# 58. How do you predict join output row count?

### Short answer

State the grain, determine uniqueness, classify cardinality, count matching multiplicities, and predict before executing.

### Engineering answer

Think:

```text
left grain
+
right grain
+
key uniqueness
+
matching multiplicity
=
expected output cardinality
```

### Follow-up

> What is the first thing you do when actual row count differs?

Inspect key multiplicity and unmatched records.

---

# 59. What is join cardinality?

### Short answer

It describes how many rows on one side can match rows on the other:

```text
1:1
1:N
N:1
N:M
```

### Follow-up

> Which is most dangerous for accidental multiplication?

N:M, especially when it arises unexpectedly.

---

# 60. What is join explosion?

### Short answer

Unexpected row multiplication caused by matching multiplicities.

### Example

```text
3 lines × 2 payments = 6 rows
```

for one order.

### Follow-up

> How do you prevent it?

Control the grain and pre-aggregate independent child tables.

---

# 61. What is a fan trap?

### Short answer

Two or more one-to-many child relationships branch from the same parent, and joining the children together multiplies their row counts.

### Example

```text
orders
 /   \
lines payments
3      2
```

→ six combinations.

### Follow-up

> How do you fix it?

Aggregate each child to parent grain before joining.

---

# 62. Why can SELECT DISTINCT be a bad fix?

### Short answer

It can hide the symptom rather than fixing the incorrect grain and can discard legitimate duplicates.

### Follow-up

> What should you do instead?

Understand why multiple rows exist and repair the relationship or aggregation level.

---

# 63. How do you find customers who never ordered?

### Short answer

Use an anti-join, commonly:

```sql
WHERE NOT EXISTS (...)
```

### Follow-up

> Why not blindly use NOT IN?

NULLs can make `NOT IN` produce unexpected results.

---

# 64. What is a semi-join?

### Short answer

A semi-join returns left rows for which at least one right-side match exists without returning one row per match.

### Common SQL expression

```sql
WHERE EXISTS (...)
```

---

# 65. What is an anti-join?

### Short answer

It returns left rows with no matching right-side row.

### Common SQL expression

```sql
WHERE NOT EXISTS (...)
```

---

# 66. What happens when join keys are NULL?

### Short answer

Ordinary equality does not match NULL to NULL.

### Reason

```text
NULL = NULL
→ UNKNOWN
```

### Follow-up

> Is that always what the business wants?

No. The business meaning of missing keys must be understood.

---

# 67. Why can a LEFT JOIN become an INNER JOIN accidentally?

### Short answer

A WHERE condition on the right-side table can remove the NULL-extended unmatched rows.

### Example

```sql
LEFT JOIN orders AS o
    ON ...
WHERE o.status = 'completed'
```

### Follow-up

> What is a common fix?

Move the right-side filter into `ON` when unmatched left rows must remain.

---

# 68. What is a range join?

### Short answer

A join based on an interval or inequality instead of simple equality.

### Example

```sql
event_time >= valid_from
AND event_time < valid_to
```

---

# 69. What is ASOF JOIN?

### Short answer

A temporal join pattern that finds the most recent right-side record at or before the left-side timestamp.

### Follow-up

> Is ASOF standard SQL?

No. It is an engine-specific feature; DuckDB provides ASOF JOIN.

---

# 70. What is LATERAL?

### Short answer

It allows a right-side subquery to reference values from the current left-side row.

### Follow-up

> When is it useful?

Per-row lookups such as latest N related records or temporal lookups.

---

# 71. Why are NATURAL JOINs dangerous?

### Short answer

They infer join columns from same-named columns, so schema evolution can silently change the join condition.

### Follow-up

> What is safer?

Explicit `ON` conditions or deliberate `USING`.

---

# 72. What are nested-loop, hash, and merge joins?

### Short answer

They are physical algorithms used to execute logical joins:

```text
Nested Loop → repeated lookups
Hash Join   → build/probe hash structure
Merge Join  → walk ordered inputs
```

### Follow-up

> Does the SQL author normally choose the algorithm?

No. The optimizer typically chooses based on estimates and available execution paths.

---

# 73. How would you debug a 3× increase in revenue after adding a JOIN?

### Expected thought process

1. State source grain.
2. State new output grain.
3. Check relationship cardinality.
4. Check key uniqueness.
5. Inspect raw joined rows.
6. Count matches per parent.
7. Identify multiplication.
8. Pre-aggregate independent child tables.
9. Reconcile totals.
10. Add a test that encodes the fixed grain.

### Common mistake

Adding:

```sql
DISTINCT
```

without understanding why the multiplication occurred.

---

# 74. Production Checklist

Before shipping an important JOIN, verify:

- [ ] I know the grain of every input.
- [ ] I know the intended output grain.
- [ ] I know the join key(s).
- [ ] I know whether each key is unique.
- [ ] I know the expected cardinality.
- [ ] I predicted the approximate or exact output row count.
- [ ] I checked for duplicate keys where uniqueness is assumed.
- [ ] I considered NULL join keys.
- [ ] I checked for many-to-many relationships.
- [ ] I checked for a fan trap.
- [ ] I did not use `DISTINCT` merely as a band-aid.
- [ ] I used pre-aggregation when required.
- [ ] I placed LEFT JOIN predicates intentionally.
- [ ] I checked whether a RIGHT JOIN could be clearer as a LEFT JOIN without changing semantics.
- [ ] I avoided production `NATURAL JOIN`.
- [ ] I used `USING` deliberately.
- [ ] Range intervals do not unexpectedly overlap.
- [ ] Latest-record logic has deterministic ordering.
- [ ] Semi-joins/anti-joins are used when existence is the real requirement.
- [ ] Row counts were reconciled.
- [ ] Distinct business keys were reconciled.
- [ ] Business totals were reconciled.
- [ ] Assertion queries were written.
- [ ] Engine-specific syntax is clearly identified.
- [ ] The final query can be explained in terms of grain and cardinality.

---

# 75. Final Knowledge Check

Do this without looking at the chapter.

## Theory

1. Explain an INNER JOIN using the "for each left row, find matches" mental model.
2. Explain why one left row can become three output rows.
3. Explain the difference between LEFT and RIGHT JOIN.
4. Explain what FULL OUTER JOIN adds for reconciliation.
5. Explain why CROSS JOIN multiplies row counts.
6. Explain a self-join using employees and managers.
7. Explain `ON` versus `USING`.
8. Define grain.
9. Define join cardinality.
10. Explain 1:1.
11. Explain 1:N.
12. Explain N:1.
13. Explain N:M.
14. Explain why duplicate keys on the "one" side are dangerous.
15. Explain join explosion.
16. Explain a fan trap.
17. Explain why revenue can become inflated.
18. Explain why pre-aggregation fixes many fan traps.
19. Explain why DISTINCT is not a universal fix.
20. Explain semi-join.
21. Explain anti-join.
22. Explain why NULL join keys do not match under ordinary equality.
23. Explain a non-equi join.
24. Explain a range join.
25. Explain DuckDB ASOF JOIN.
26. Explain PostgreSQL LATERAL.
27. Explain why latest-record logic needs deterministic ordering.
28. Explain NATURAL JOIN risk.
29. Explain nested-loop join.
30. Explain hash join.
31. Explain merge join.
32. Explain join reconciliation.

---

## Practical coding tasks

### Task 1 — Cardinality

Given:

```text
customers:
100 rows

orders:
1000 rows

customer_id unique in customers
every order has one customer
```

Predict:

```text
customers JOIN orders
```

row count.

---

### Task 2 — 1:N

Given one customer with:

```text
5 orders
```

Predict the number of joined rows for that customer.

---

### Task 3 — Fan trap

Given one order with:

```text
4 lines
3 payments
```

predict the raw joined rows.

---

### Task 4 — Repair

Pre-aggregate both children to order grain.

---

### Task 5 — Anti-join

Write a query for:

```text
customers who never ordered
```

---

### Task 6 — Semi-join

Write a query for:

```text
customers who ordered at least once
```

without one output row per order.

---

### Task 7 — Range join

Match events to the validity interval of a price.

---

### Task 8 — LATERAL

Return the latest three orders per customer.

---

### Task 9 — Reconciliation

Compare row counts and distinct order IDs before and after a customer join.

---

### Task 10 — Production debugging

Given:

```text
Revenue = 100 before a new join
Revenue = 900 after a new join
```

write the investigation queries you would use to determine whether the join caused row multiplication.

---

# 76. Final Mental Model

When you see a JOIN, do not begin by asking:

> "Which JOIN keyword should I use?"

Start with:

```text
1. What does one row mean on the left?
        ↓
2. What does one row mean on the right?
        ↓
3. What column(s) relate them?
        ↓
4. Which side is unique?
        ↓
5. What is the cardinality?
        ↓
6. What output grain do I actually want?
        ↓
7. How many matches can one left row have?
        ↓
8. Will independent child relationships multiply?
        ↓
9. Are NULL keys involved?
        ↓
10. How will I prove the result is correct?
```

Then write the SQL.

---

# 77. Checkpoint — Ready for Topic 03?

The Module 2.6 roadmap says you are ready to move on only when you can:

- [ ] Predict a join's output row count from key cardinalities.
- [ ] Explain and fix a fan trap.
- [ ] Write semi-joins.
- [ ] Write anti-joins.
- [ ] Explain why a `WHERE` filter can turn a LEFT JOIN into an INNER JOIN.
- [ ] Write a range join.
- [ ] Write a LATERAL join.
- [ ] Explain NULL join-key behavior.
- [ ] Validate supposed unique keys with assertion queries.
- [ ] Reconcile row counts after a join.
- [ ] Reconcile business totals after a join.
- [ ] Explain nested-loop, hash, and merge joins at a conceptual level.
- [ ] Explain why `DISTINCT` is not a safe substitute for fixing grain.
- [ ] Identify and repair a multi-child fan trap.

## Practical gate

You should be able to build this kind of pipeline from scratch:

```text
orders
  |
  +------ line_summary
  |
  +------ payment_summary
  |
  +------ shipment_summary
  |
  ↓
one row per order
```

and explain:

```text
why each source has its current grain
why each join is safe
what the cardinality is
what row count you expect
how NULLs are handled
how you prove the result is correct
```

Do not move to Topic 03 until you can explain the result of a join before you execute it.

---

# 78. Final Engineering Rules to Remember

## Rule 1

> **Grain first. SQL second.**

---

## Rule 2

> **A join returns matching row combinations, not business entities.**

---

## Rule 3

> **A "one" side is an assumption until uniqueness is validated.**

---

## Rule 4

> **1:N relationships naturally multiply rows.**

---

## Rule 5

> **N:M relationships can multiply dramatically.**

---

## Rule 6

> **Independent one-to-many child tables can create a fan trap.**

---

## Rule 7

> **Pre-aggregate child data to the intended parent grain before combining independent children.**

---

## Rule 8

> **Do not use DISTINCT to hide an unexplained grain problem.**

---

## Rule 9

> **A LEFT JOIN preserves left rows, but a WHERE predicate can still remove the NULL-extended rows.**

---

## Rule 10

> **`EXISTS` is for existence; JOIN is for returning matching combinations.**

---

## Rule 11

> **NULL does not match NULL under ordinary equality.**

---

## Rule 12

> **Range joins require carefully designed and non-overlapping validity intervals when one match is expected.**

---

## Rule 13

> **ASOF JOIN and LATERAL solve useful per-row temporal/lookup problems, but they are not interchangeable with ordinary equality joins.**

---

## Rule 14

> **Use deterministic ordering when "latest" or "top N" must be reproducible.**

---

## Rule 15

> **Prefer explicit join conditions in production.**

---

## Rule 16

> **After an important join, reconcile row counts, distinct keys, unmatched records, and business totals.**

---

# Final Summary

The most important skill in SQL joins is not remembering:

```sql
INNER JOIN
LEFT JOIN
RIGHT JOIN
FULL OUTER JOIN
```

The most important skill is being able to reason:

```text
grain
   ↓
key uniqueness
   ↓
cardinality
   ↓
matching multiplicity
   ↓
expected output rows
   ↓
business meaning
   ↓
validation
```

Once you develop that habit, join debugging becomes much more systematic.

When a metric suddenly doubles, triples, or grows by an unexpected factor, you can ask:

```text
Which table multiplied the row?
Why did that happen?
What was the relationship?
What grain did the result reach?
Should I pre-aggregate?
Which assertion would catch this?
```

That is the mindset of a production Data Engineer.

