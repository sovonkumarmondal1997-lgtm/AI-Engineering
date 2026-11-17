# SQL for Data Engineers — 40 Practice Questions

## How to Use This Practice Set

This is the cumulative practice set for **Module 2.6 — SQL for Data Engineers**. It covers Topics 01–10 in the same progression as the module:

```text
Basic
  ↓
Moderate
  ↓
Hard
  ↓
Advanced
```

There are exactly:

```text
10 Basic
10 Moderate
10 Hard
10 Advanced
----------------
40 total
```

Every question follows:

```text
Problem
  ↓
Solution
```

Attempt the problem before reading its solution. For every relational transformation, practice the module's engineering loop:

```text
state the grain
→ predict output row count
→ build tiny data
→ write SQL
→ inspect the result
→ validate with assertions
→ test edge cases
→ explain correctness
→ reason about performance / concurrency where relevant
```

Use **PostgreSQL 16+** unless the question explicitly asks for DuckDB awareness.

> **No question in this file should require knowledge from a later module.** The questions combine concepts already taught in Topics 01–10 because this is cumulative practice.

---

## SQL Engineering Practice Method

Before writing a query, say these out loud:

```text
One input row represents: __________
One output row should represent: __________
Expected output rows: __________
Business key: __________
Important NULL cases: __________
Duplicate / tie cases: __________
Correctness assertion: __________
Likely performance risk: __________
```

For concurrency questions, add:

```text
Session A sees: __________
Session B sees: __________
Locks held: __________
Locks requested: __________
Blocking or anomaly: __________
Isolation level: __________
Failure / retry behavior: __________
```

For incremental/SCD questions, add:

```text
Source grain: __________
Target grain: __________
Identity key: __________
Change rule: __________
Insert rule: __________
Update rule: __________
Delete rule: __________
History rule: __________
Idempotency proof: __________
```

---

# Part I — Basic

## Question 01 — Customer Cleanup and NULL Semantics

**Difficulty:** Basic

**Primary topics:** SELECT, WHERE, aliases, CASE, string functions, NULL, COALESCE, deterministic ordering

**Integrated topics:** `ILIKE`, `TRIM`, `LOWER`, `NULLS LAST`, `ORDER BY`

### Problem

Create the following table:

```sql
CREATE TEMP TABLE customers (
    customer_id INTEGER,
    full_name TEXT,
    email TEXT,
    country TEXT,
    credit_limit NUMERIC(12, 2)
);

INSERT INTO customers VALUES
    (1, '  Alice Smith  ', 'ALICE@example.com', 'India', 5000.00),
    (2, 'Bob Jones', NULL, 'India', 3000.00),
    (3, '  carol  ', 'carol@example.com', NULL, NULL),
    (4, 'David Chen', 'david@example.com', 'Singapore', 1000.00),
    (5, NULL, 'eve@example.com', 'India', 1000.00);
```

Write a query that returns:

```text
customer_id
normalized_name
normalized_email
risk_level
```

Rules:

- trim and lowercase `full_name`;
- lowercase email;
- `high` when `credit_limit >= 4000`;
- `medium` when `credit_limit >= 2000`;
- otherwise `low`;
- return only customers from known countries other than Singapore;
- order by credit limit descending with NULLs last and `customer_id` as a tie-breaker.

State the input grain, output grain, expected row count, and explain what happens to NULL values.

### Solution

#### Step 1 — Grain

```text
Input grain:
one row per customer

Output grain:
one row per selected customer

Expected rows:
3
```

#### Step 2 — SQL

```sql
SELECT
    customer_id,
    LOWER(TRIM(full_name)) AS normalized_name,
    LOWER(email) AS normalized_email,
    CASE
        WHEN credit_limit >= 4000 THEN 'high'
        WHEN credit_limit >= 2000 THEN 'medium'
        ELSE 'low'
    END AS risk_level
FROM customers
WHERE country IS NOT NULL
  AND country <> 'Singapore'
ORDER BY
    credit_limit DESC NULLS LAST,
    customer_id;
```

#### Step 3 — Expected Result

```text
customer_id | normalized_name | normalized_email     | risk_level
------------+-----------------+----------------------+-----------
1           | alice smith     | alice@example.com    | high
2           | bob jones       | NULL                 | medium
5           | NULL            | eve@example.com      | low
```

#### Why This Is Correct

The query explicitly tests:

```sql
country IS NOT NULL
AND country <> 'Singapore'
```

because:

```sql
NULL <> 'Singapore'
```

evaluates to `UNKNOWN`.

`WHERE` keeps only rows whose predicate is `TRUE`.

#### Edge Cases

```text
TRIM(NULL) → NULL
LOWER(NULL) → NULL
credit_limit >= 4000 when credit_limit is NULL → UNKNOWN
```

#### Assertion

```sql
SELECT customer_id
FROM customers
WHERE country IS NULL
   OR country = 'Singapore'
EXCEPT
SELECT customer_id
FROM customers
WHERE country IS NOT NULL
  AND country <> 'Singapore';
```

This returns rows that are intentionally excluded; use it as a check when validating the filter specification.

#### Common Wrong Approach

```sql
WHERE country <> 'Singapore'
```

This silently excludes NULL countries.

#### Production Note

Do not confuse normalization with identity. Lowercasing a name is a display/cleaning rule, not evidence that two customers are the same entity.

---

## Question 02 — Half-Open Time Window and Integer Division

**Difficulty:** Basic

**Primary topics:** timestamp/timestamptz, half-open ranges, CAST, integer division, intervals, `DATE_TRUNC`

### Problem

Given:

```sql
CREATE TEMP TABLE orders (
    order_id INTEGER,
    created_at TIMESTAMPTZ,
    amount NUMERIC(12, 2),
    quantity INTEGER
);

INSERT INTO orders VALUES
    (1, '2026-09-28 00:00:00+05:30', 100.00, 2),
    (2, '2026-09-28 12:00:00+05:30', 300.00, 3),
    (3, '2026-09-28 23:59:59+05:30', 50.00, 1),
    (4, '2026-09-29 00:00:00+05:30', 500.00, 5);
```

Return the three orders from September 28 with:

```text
order_id
day
unit_value
```

Use a half-open time window and protect against division by zero.

Also explain the difference between:

```sql
SELECT 5 / 2;
SELECT 5::NUMERIC / 2;
```

### Solution

```sql
SELECT
    order_id,
    DATE_TRUNC('day', created_at) AS day,
    amount / NULLIF(quantity, 0)::NUMERIC AS unit_value
FROM orders
WHERE created_at >= TIMESTAMPTZ '2026-09-28 00:00:00+05:30'
  AND created_at <  TIMESTAMPTZ '2026-09-29 00:00:00+05:30'
ORDER BY created_at, order_id;
```

Expected:

```text
1 | 2026-09-28 00:00:00+05:30 | 50
2 | 2026-09-28 00:00:00+05:30 | 100
3 | 2026-09-28 00:00:00+05:30 | 50
```

Order 4 is outside the interval.

### Why Half-Open?

Use:

```text
[start, end)
```

so adjacent windows fit exactly:

```text
[Sep 28 00:00, Sep 29 00:00)
[Sep 29 00:00, Sep 30 00:00)
```

### Integer Division

In PostgreSQL:

```sql
SELECT 5 / 2;
```

produces integer division:

```text
2
```

Casting changes the numeric semantics:

```sql
SELECT 5::NUMERIC / 2;
```

produces:

```text
2.5
```

### Common Wrong Approach

Using:

```sql
BETWEEN '2026-09-28 00:00:00' AND '2026-09-28 23:59:59'
```

This creates an artificial final instant and can mishandle higher-precision timestamps.

### Production Note

Half-open intervals are especially valuable for incremental extraction and partition-aligned time filtering.

---

## Question 03 — Deterministic Pagination

**Difficulty:** Basic

**Primary topics:** ORDER BY, LIMIT, OFFSET, FETCH FIRST, tie-breakers, keyset pagination

### Problem

Given:

```sql
CREATE TEMP TABLE events (
    event_id INTEGER,
    created_at TIMESTAMP,
    payload TEXT
);

INSERT INTO events VALUES
    (101, '2026-09-28 10:00:00', 'a'),
    (102, '2026-09-28 10:00:00', 'b'),
    (103, '2026-09-28 10:01:00', 'c'),
    (104, '2026-09-28 10:02:00', 'd'),
    (105, '2026-09-28 10:02:00', 'e');
```

Return the second page of two rows using `OFFSET`.

Then write a keyset/seek query returning rows after:

```text
created_at = '2026-09-28 10:00:00'
event_id = 102
```

Explain why `created_at` alone is not deterministic.

### Solution

#### OFFSET

```sql
SELECT
    event_id,
    created_at,
    payload
FROM events
ORDER BY
    created_at,
    event_id
OFFSET 2
FETCH FIRST 2 ROWS ONLY;
```

Expected:

```text
103
104
```

#### Keyset

```sql
SELECT
    event_id,
    created_at,
    payload
FROM events
WHERE (created_at, event_id) >
      (TIMESTAMP '2026-09-28 10:00:00', 102)
ORDER BY
    created_at,
    event_id
FETCH FIRST 2 ROWS ONLY;
```

### Grain

```text
one row per event
```

### Common Wrong Approach

```sql
ORDER BY created_at
LIMIT 2;
```

Two rows can have the same timestamp, so the selected subset is not fully specified.

### Production Note

`OFFSET` is simple but can become expensive at large offsets. Keyset pagination can avoid walking over a large number of earlier rows when the ordered key is suitable.

---

## Question 04 — Join Types and Cardinality

**Difficulty:** Basic

**Primary topics:** INNER/LEFT/RIGHT/FULL/CROSS/self-join, ON, USING, join grain

### Problem

Create:

```sql
CREATE TEMP TABLE departments (
    department_id INTEGER PRIMARY KEY,
    department_name TEXT
);

CREATE TEMP TABLE employees (
    employee_id INTEGER PRIMARY KEY,
    employee_name TEXT,
    department_id INTEGER
);

INSERT INTO departments VALUES
    (1, 'Engineering'),
    (2, 'Finance'),
    (3, 'Sales');

INSERT INTO employees VALUES
    (10, 'Asha', 1),
    (11, 'Ben', 1),
    (12, 'Cara', 2),
    (13, 'Dan', NULL),
    (14, 'Eve', 9);
```

Write:

1. an inner join;
2. a left join;
3. a full outer join;
4. a cross join;
5. a self-join that produces each same-department employee pair only once.

Predict cardinality before running each query.

### Solution

#### Inner

```sql
SELECT
    e.employee_id,
    e.employee_name,
    d.department_name
FROM employees AS e
JOIN departments AS d
  ON e.department_id = d.department_id
ORDER BY e.employee_id;
```

Matches:

```text
Asha
Ben
Cara
```

#### Left

```sql
SELECT
    e.employee_id,
    e.employee_name,
    d.department_name
FROM employees AS e
LEFT JOIN departments AS d
  ON e.department_id = d.department_id
ORDER BY e.employee_id;
```

Output grain remains:

```text
one row per employee
```

#### Full

```sql
SELECT
    e.employee_id,
    e.employee_name,
    d.department_id,
    d.department_name
FROM employees AS e
FULL OUTER JOIN departments AS d
  ON e.department_id = d.department_id
ORDER BY
    COALESCE(e.employee_id, 0),
    COALESCE(d.department_id, 0);
```

This exposes unmatched employees and unmatched departments.

#### Cross

```sql
SELECT
    e.employee_name,
    d.department_name
FROM employees AS e
CROSS JOIN departments AS d;
```

Cardinality:

```text
5 × 3 = 15 rows
```

#### Self-join

```sql
SELECT
    e1.employee_name AS employee_a,
    e2.employee_name AS employee_b,
    e1.department_id
FROM employees AS e1
JOIN employees AS e2
  ON e1.department_id = e2.department_id
 AND e1.employee_id < e2.employee_id
WHERE e1.department_id IS NOT NULL
ORDER BY e1.employee_id, e2.employee_id;
```

Expected pair:

```text
Asha | Ben | 1
```

### Common Wrong Approach

Assuming:

```text
employee × department
```

is always one-to-one.

### Production Note

Join cardinality comes from key relationships, not from the spelling of `JOIN`.

---

## Question 05 — Customers with No Completed Orders

**Difficulty:** Basic

**Primary topics:** LEFT JOIN, WHERE trap, EXISTS, NOT EXISTS, NULL

### Problem

Create:

```sql
CREATE TEMP TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT
);

CREATE TEMP TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    status TEXT
);

INSERT INTO customers VALUES
    (1, 'Asha'),
    (2, 'Ben'),
    (3, 'Cara');

INSERT INTO orders VALUES
    (100, 1, 'completed'),
    (101, 1, 'cancelled'),
    (102, 2, 'pending');
```

Find customers who have **no completed orders**.

Provide:

1. a `LEFT JOIN` solution;
2. a `NOT EXISTS` solution.

### Solution

#### LEFT JOIN

```sql
SELECT
    c.customer_id,
    c.customer_name
FROM customers AS c
LEFT JOIN orders AS o
  ON o.customer_id = c.customer_id
 AND o.status = 'completed'
WHERE o.order_id IS NULL
ORDER BY c.customer_id;
```

Expected:

```text
2 | Ben
3 | Cara
```

#### NOT EXISTS

```sql
SELECT
    c.customer_id,
    c.customer_name
FROM customers AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.customer_id
      AND o.status = 'completed'
)
ORDER BY c.customer_id;
```

### Common Wrong Approach

```sql
LEFT JOIN orders AS o
  ON o.customer_id = c.customer_id
WHERE o.status <> 'completed';
```

For customers with no order:

```text
o.status = NULL
```

so the predicate is `UNKNOWN`.

### Production Note

`NOT EXISTS` directly expresses an anti-membership question and avoids many accidental row-removal problems.

---

## Question 06 — Aggregates and the Average-of-Averages Error

**Difficulty:** Basic

**Primary topics:** COUNT, SUM, AVG, COUNT(DISTINCT), NULL, weighted average

### Problem

You have:

```sql
CREATE TEMP TABLE orders (
    order_id INTEGER,
    region TEXT,
    customer_id INTEGER,
    amount NUMERIC(12, 2)
);

INSERT INTO orders VALUES
    (1, 'India', 101, 100),
    (2, 'India', 102, 100),
    (3, 'US', 201, 10),
    (4, 'US', 202, 10),
    (5, 'US', 203, 10),
    (6, 'US', 204, 10);
```

Calculate globally:

```text
order_count
non_null_amount_count
revenue
average_order_value
distinct_customer_count
```

Then explain why:

```text
(India AOV + US AOV) / 2
```

is not the global AOV.

### Solution

```sql
SELECT
    COUNT(*) AS order_count,
    COUNT(amount) AS non_null_amount_count,
    SUM(amount) AS revenue,
    AVG(amount) AS average_order_value,
    COUNT(DISTINCT customer_id) AS distinct_customer_count
FROM orders;
```

Expected:

```text
6 | 6 | 240 | 40 | 6
```

### Why the average of averages is wrong

The regional averages are:

```text
India = 100
US = 10
```

A simple average gives:

```text
55
```

but India has two orders and US has four.

The correct global metric is:

```text
SUM(amount) / COUNT(order)
= 240 / 6
= 40
```

### Common Wrong Approach

```text
AVG(regional_average)
```

without weighting by row count.

### Production Note

Define the mathematics of a KPI before choosing SQL aggregate functions.

---

## Question 07 — Scalar Subquery vs CTE

**Difficulty:** Basic

**Primary topics:** scalar subquery, CTE, aggregation, output grain

### Problem

Given:

```sql
CREATE TEMP TABLE orders (
    order_id INTEGER,
    customer_id INTEGER,
    amount NUMERIC(12, 2)
);

INSERT INTO orders VALUES
    (1, 10, 100),
    (2, 10, 200),
    (3, 20, 50);
```

Return:

```text
customer_id
customer_total
average_customer_total
```

The `average_customer_total` is the average of the customer totals.

Write the solution twice:

1. with a scalar subquery;
2. with a CTE.

### Solution

#### Scalar subquery

```sql
SELECT
    customer_id,
    SUM(amount) AS customer_total,
    (
        SELECT AVG(customer_total)
        FROM (
            SELECT
                customer_id,
                SUM(amount) AS customer_total
            FROM orders
            GROUP BY customer_id
        ) AS totals
    ) AS average_customer_total
FROM orders
GROUP BY customer_id
ORDER BY customer_id;
```

#### CTE

```sql
WITH customer_totals AS (
    SELECT
        customer_id,
        SUM(amount) AS customer_total
    FROM orders
    GROUP BY customer_id
),
overall AS (
    SELECT
        AVG(customer_total) AS average_customer_total
    FROM customer_totals
)
SELECT
    ct.customer_id,
    ct.customer_total,
    o.average_customer_total
FROM customer_totals AS ct
CROSS JOIN overall AS o
ORDER BY ct.customer_id;
```

Expected:

```text
10 | 300 | 175
20 | 50  | 175
```

### Grain

```text
customer_totals → one row per customer
overall         → one row for entire input
final           → one row per customer
```

### Common Wrong Approach

Writing a scalar subquery that returns multiple customer rows.

### Production Note

CTEs are especially useful when you need to inspect transformation stages independently during debugging.

---

## Question 08 — Ranking Ties Correctly

**Difficulty:** Basic

**Primary topics:** ROW_NUMBER, RANK, DENSE_RANK, ties, deterministic ordering

### Problem

Given:

```sql
CREATE TEMP TABLE sales (
    salesperson TEXT,
    revenue INTEGER
);

INSERT INTO sales VALUES
    ('Asha', 100),
    ('Ben', 100),
    ('Cara', 80),
    ('Dan', 70);
```

Return:

```text
salesperson
revenue
ROW_NUMBER
RANK
DENSE_RANK
```

and explain how ties are treated.

### Solution

```sql
SELECT
    salesperson,
    revenue,
    ROW_NUMBER() OVER (
        ORDER BY revenue DESC, salesperson
    ) AS row_number_value,
    RANK() OVER (
        ORDER BY revenue DESC
    ) AS rank_value,
    DENSE_RANK() OVER (
        ORDER BY revenue DESC
    ) AS dense_rank_value
FROM sales
ORDER BY revenue DESC, salesperson;
```

Expected:

```text
Asha | 100 | 1 | 1 | 1
Ben  | 100 | 2 | 1 | 1
Cara | 80  | 3 | 3 | 2
Dan  | 70  | 4 | 4 | 3
```

### Meaning

```text
ROW_NUMBER
→ unique sequence

RANK
→ ties share rank, gaps follow

DENSE_RANK
→ ties share rank, no gaps
```

### Common Wrong Approach

Using only:

```sql
ROW_NUMBER() OVER (ORDER BY revenue DESC)
```

when ties must be deterministic.

### Production Note

A stable tie-breaker is part of correctness whenever reproducibility matters.

---

## Question 09 — Deterministic Latest Record

**Difficulty:** Basic

**Primary topics:** ROW_NUMBER, deduplication, business key, tie-breaker

### Problem

Staging contains:

```sql
CREATE TEMP TABLE staging_customers (
    customer_id INTEGER,
    segment TEXT,
    updated_at TIMESTAMP,
    record_id INTEGER
);

INSERT INTO staging_customers VALUES
    (101, 'Bronze', '2026-09-28 10:00:00', 1),
    (101, 'Silver', '2026-09-28 10:00:00', 2),
    (102, 'Gold',   '2026-09-28 11:00:00', 3),
    (102, 'Silver', '2026-09-28 12:00:00', 4),
    (103, 'Bronze', '2026-09-28 13:00:00', 5);
```

Keep one row per `customer_id` using:

```text
latest updated_at
then highest record_id
```

### Solution

```sql
WITH ranked AS (
    SELECT
        s.*,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY
                updated_at DESC,
                record_id DESC
        ) AS rn
    FROM staging_customers AS s
)
SELECT
    customer_id,
    segment,
    updated_at,
    record_id
FROM ranked
WHERE rn = 1
ORDER BY customer_id;
```

Expected:

```text
101 | Silver | 2026-09-28 10:00:00 | 2
102 | Silver | 2026-09-28 12:00:00 | 4
103 | Bronze | 2026-09-28 13:00:00 | 5
```

### Assertion

```sql
SELECT
    customer_id
FROM staging_customers
GROUP BY customer_id
HAVING COUNT(*) > 1;
```

This catches duplicate source keys before the merge.

### Common Wrong Approach

```sql
SELECT DISTINCT customer_id, segment
```

This removes exact duplicates but does not tell the database which conflicting segment should survive.

### Production Note

The survivor rule is business logic. `ROW_NUMBER()` is merely how the rule is implemented.

---

## Question 10 — Constrained Product Table and Upsert

**Difficulty:** Basic

**Primary topics:** CREATE TABLE, identity, PK, UNIQUE, CHECK, NOT NULL, upsert

### Problem

Design a temporary PostgreSQL table `products` with:

```text
product_id
product_name
sku
price
```

Requirements:

- generated identity primary key;
- `product_name` required;
- `sku` required and unique;
- `price` required and non-negative.

Insert one product, then replay the SKU with a new name and price using an upsert.

### Solution

```sql
CREATE TEMP TABLE products (
    product_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_name TEXT NOT NULL,
    sku TEXT NOT NULL UNIQUE,
    price NUMERIC(12, 2) NOT NULL CHECK (price >= 0)
);
```

Initial insert:

```sql
INSERT INTO products (
    product_name,
    sku,
    price
)
VALUES (
    'Keyboard',
    'KB-001',
    50.00
);
```

Upsert:

```sql
INSERT INTO products (
    product_name,
    sku,
    price
)
VALUES (
    'Keyboard Pro',
    'KB-001',
    60.00
)
ON CONFLICT (sku)
DO UPDATE
SET
    product_name = EXCLUDED.product_name,
    price = EXCLUDED.price;
```

Expected final business state:

```text
Keyboard Pro | KB-001 | 60
```

### Common Wrong Approach

Using `product_name` as the identity key.

Product names can change and need not be unique.

### Production Note

Upsert depends on a key that actually answers:

> "Which existing row is this incoming row supposed to represent?"

---

# Part II — Moderate

## Question 11 — Pre-Aggregate to Prevent Join Explosion

**Difficulty:** Moderate

**Primary topics:** join grain, 1:N relationships, preaggregation, aggregation, COALESCE

### Problem

You need one row per customer containing:

```text
order_revenue
payment_total
```

Data:

```sql
CREATE TEMP TABLE customers (
    customer_id INTEGER PRIMARY KEY
);

CREATE TEMP TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    amount NUMERIC(12, 2)
);

CREATE TEMP TABLE payments (
    payment_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    amount NUMERIC(12, 2)
);

INSERT INTO customers VALUES (1), (2);

INSERT INTO orders VALUES
    (101, 1, 100),
    (102, 1, 200),
    (103, 2, 50);

INSERT INTO payments VALUES
    (201, 1, 80),
    (202, 1, 120),
    (203, 1, 50);
```

Return one row per customer without inflating either metric.

### Solution

```sql
WITH order_totals AS (
    SELECT
        customer_id,
        SUM(amount) AS order_revenue
    FROM orders
    GROUP BY customer_id
),
payment_totals AS (
    SELECT
        customer_id,
        SUM(amount) AS payment_total
    FROM payments
    GROUP BY customer_id
)
SELECT
    c.customer_id,
    COALESCE(o.order_revenue, 0) AS order_revenue,
    COALESCE(p.payment_total, 0) AS payment_total
FROM customers AS c
LEFT JOIN order_totals AS o
  ON o.customer_id = c.customer_id
LEFT JOIN payment_totals AS p
  ON p.customer_id = c.customer_id
ORDER BY c.customer_id;
```

Expected:

```text
1 | 300 | 250
2 | 50  | 0
```

### Why

Raw customer 1 data would have:

```text
2 orders × 3 payments = 6 joined rows
```

Preaggregation changes each child to:

```text
one row per customer
```

before the final join.

### Common Wrong Approach

Join raw orders and raw payments and aggregate afterward.

### Production Note

A many-to-many fan trap is a correctness problem before it is a performance problem.

---

## Question 12 — NULL-Safe Anti-Join

**Difficulty:** Moderate

**Primary topics:** NOT EXISTS, NOT IN, NULL, anti-join

### Problem

Given:

```sql
CREATE TEMP TABLE customers (
    customer_id INTEGER
);

CREATE TEMP TABLE blocked_customers (
    customer_id INTEGER
);

INSERT INTO customers VALUES
    (1), (2), (3);

INSERT INTO blocked_customers VALUES
    (2), (NULL);
```

Return customers not present in `blocked_customers`.

Then explain the behavior of:

```sql
customer_id NOT IN (
    SELECT customer_id
    FROM blocked_customers
)
```

### Solution

```sql
SELECT
    c.customer_id
FROM customers AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM blocked_customers AS b
    WHERE b.customer_id = c.customer_id
)
ORDER BY c.customer_id;
```

Expected:

```text
1
3
```

### Why

`NOT EXISTS` asks:

> "Is there no matching row?"

The NULL in `blocked_customers` does not match customer 1 or 3.

`NOT IN` can become UNKNOWN because its comparison is affected by a NULL in the subquery.

### Common Wrong Approach

Assuming `NULL` is simply ignored by `NOT IN`.

### Production Note

Membership semantics are part of SQL correctness. Never choose an anti-join pattern without considering nullable keys.

---

## Question 13 — Recursive Employee Hierarchy

**Difficulty:** Moderate

**Primary topics:** recursive CTE, anchor member, recursive member, depth, path, cycle protection

### Problem

Given:

```sql
CREATE TEMP TABLE employees (
    employee_id INTEGER PRIMARY KEY,
    employee_name TEXT,
    manager_id INTEGER
);

INSERT INTO employees VALUES
    (1, 'CEO', NULL),
    (2, 'VP Engineering', 1),
    (3, 'Engineer A', 2),
    (4, 'Engineer B', 2),
    (5, 'VP Finance', 1);
```

Return:

```text
employee_id
employee_name
depth
path
```

where:

```text
CEO > VP Engineering > Engineer A
```

is the path for Engineer A.

Include a cycle guard.

### Solution

```sql
WITH RECURSIVE org AS (
    SELECT
        employee_id,
        employee_name,
        manager_id,
        0 AS depth,
        employee_name::TEXT AS path,
        ARRAY[employee_id] AS visited_ids
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    SELECT
        e.employee_id,
        e.employee_name,
        e.manager_id,
        o.depth + 1,
        o.path || ' > ' || e.employee_name,
        o.visited_ids || e.employee_id
    FROM employees AS e
    JOIN org AS o
      ON e.manager_id = o.employee_id
    WHERE NOT e.employee_id = ANY(o.visited_ids)
)
SELECT
    employee_id,
    employee_name,
    depth,
    path
FROM org
ORDER BY depth, employee_id;
```

### Why

```text
anchor
→ root employees

recursive member
→ direct reports

visited_ids
→ cycle protection
```

### Common Wrong Approach

A recursive CTE with no termination/cycle strategy.

### Production Note

Recursive SQL needs an explicit traversal model. A depth limit may also be appropriate as a resource-safety guard, but it should not silently change the business meaning of the hierarchy.

---

## Question 14 — Date Spine for Missing Periods

**Difficulty:** Moderate

**Primary topics:** generate_series, date spine, LEFT JOIN, COALESCE

### Problem

Revenue exists for only:

```text
Sep 1 → 100
Sep 3 → 250
Sep 5 → 50
```

Return all five days with missing revenue represented as zero because the report contract defines missing activity as zero.

### Solution

```sql
WITH date_spine AS (
    SELECT
        day::DATE AS day
    FROM generate_series(
        DATE '2026-09-01',
        DATE '2026-09-05',
        INTERVAL '1 day'
    ) AS g(day)
)
SELECT
    ds.day,
    COALESCE(r.revenue, 0) AS revenue
FROM date_spine AS ds
LEFT JOIN daily_revenue AS r
  ON r.day = ds.day
ORDER BY ds.day;
```

Expected:

```text
2026-09-01 | 100
2026-09-02 | 0
2026-09-03 | 250
2026-09-04 | 0
2026-09-05 | 50
```

### Common Wrong Approach

Aggregating directly from the revenue table and expecting missing dates to appear.

### Production Note

A missing row is not inherently the same as zero. `COALESCE(..., 0)` is correct here only because the report specification defines that semantic.

---

## Question 15 — Running Total and Window Frame

**Difficulty:** Moderate

**Primary topics:** window aggregates, ROWS, running totals, moving average

### Problem

Given:

```sql
CREATE TEMP TABLE revenue_by_day (
    day DATE,
    revenue INTEGER
);

INSERT INTO revenue_by_day VALUES
    ('2026-09-01', 100),
    ('2026-09-02', 200),
    ('2026-09-04', 50);
```

Calculate:

```text
running_revenue
two_row_moving_average
```

Also explain why the missing September 3 matters to the interpretation of the moving average.

### Solution

```sql
SELECT
    day,
    revenue,
    SUM(revenue) OVER (
        ORDER BY day
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_revenue,
    AVG(revenue) OVER (
        ORDER BY day
        ROWS BETWEEN 1 PRECEDING AND CURRENT ROW
    ) AS two_row_moving_average
FROM revenue_by_day
ORDER BY day;
```

Expected:

```text
Sep 1 | 100 | 100 | 100
Sep 2 | 200 | 300 | 150
Sep 4 | 50  | 350 | 125
```

The final moving average is based on the previous **row**, not the previous calendar day.

### Common Wrong Approach

Assuming:

```text
ROWS BETWEEN 1 PRECEDING
```

means "previous calendar day."

### Production Note

`ROWS`, `RANGE`, and `GROUPS` encode different business meanings. Choose the frame based on what "previous" actually means.

---

## Question 16 — Gaps and Islands

**Difficulty:** Moderate

**Primary topics:** ROW_NUMBER, gaps-and-islands, consecutive dates

### Problem

A user logged in on:

```text
Sep 1
Sep 2
Sep 3
Sep 5
Sep 6
Sep 9
```

Find each consecutive streak.

### Solution

```sql
WITH numbered AS (
    SELECT
        user_id,
        login_date,
        login_date
            - ROW_NUMBER() OVER (
                PARTITION BY user_id
                ORDER BY login_date
              )::INTEGER AS island_key
    FROM logins
),
streaks AS (
    SELECT
        user_id,
        MIN(login_date) AS streak_start,
        MAX(login_date) AS streak_end,
        COUNT(*) AS streak_length
    FROM numbered
    GROUP BY
        user_id,
        island_key
)
SELECT *
FROM streaks
ORDER BY user_id, streak_start;
```

Expected for one user:

```text
Sep 1 → Sep 3 | 3
Sep 5 → Sep 6 | 2
Sep 9 → Sep 9 | 1
```

### Why

Subtracting a row number from consecutive dates produces the same island key for each consecutive run.

### Common Wrong Approach

Grouping by month or week and assuming that produces consecutive streaks.

### Production Note

Always define what "consecutive" means. Here it means adjacent calendar dates.

---

## Question 17 — Sessionise Click Events

**Difficulty:** Moderate

**Primary topics:** LAG, running SUM, intervals, sessionisation

### Problem

A new session starts when the gap from the previous event is **greater than 30 minutes**.

Data:

```sql
CREATE TEMP TABLE clicks (
    user_id INTEGER,
    event_time TIMESTAMP,
    event_id INTEGER
);

INSERT INTO clicks VALUES
    (1, '2026-09-28 09:00:00', 1),
    (1, '2026-09-28 09:10:00', 2),
    (1, '2026-09-28 09:40:00', 3),
    (1, '2026-09-28 10:20:00', 4),
    (1, '2026-09-28 11:30:00', 5);
```

Generate a session number.

### Solution

```sql
WITH with_previous AS (
    SELECT
        c.*,
        LAG(event_time) OVER (
            PARTITION BY user_id
            ORDER BY event_time, event_id
        ) AS previous_event_time
    FROM clicks AS c
),
flags AS (
    SELECT
        *,
        CASE
            WHEN previous_event_time IS NULL THEN 1
            WHEN event_time - previous_event_time > INTERVAL '30 minutes'
                THEN 1
            ELSE 0
        END AS new_session
    FROM with_previous
)
SELECT
    user_id,
    event_id,
    event_time,
    SUM(new_session) OVER (
        PARTITION BY user_id
        ORDER BY event_time, event_id
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS session_id
FROM flags
ORDER BY user_id, event_time, event_id;
```

Expected sessions:

```text
09:00, 09:10 → session 1
09:40        → session 2
10:20        → session 3
11:30        → session 4
```

### Common Wrong Approach

Using `DATE_TRUNC('hour', event_time)` to define sessions.

### Production Note

Equal timestamps need a deterministic event tie-breaker such as `event_id`.

---

## Question 18 — Reconcile Source and Target with EXCEPT

**Difficulty:** Moderate

**Primary topics:** EXCEPT, reconciliation, missing rows, extra rows

### Problem

Compare:

```sql
CREATE TEMP TABLE source_customers (
    customer_id INTEGER,
    segment TEXT
);

CREATE TEMP TABLE target_customers (
    customer_id INTEGER,
    segment TEXT
);

INSERT INTO source_customers VALUES
    (1, 'Bronze'),
    (2, 'Silver'),
    (3, 'Gold');

INSERT INTO target_customers VALUES
    (1, 'Bronze'),
    (2, 'Silver'),
    (4, 'Bronze');
```

Find:

1. source-only rows;
2. target-only rows.

Explain why equal row counts do not prove table equality.

### Solution

#### Source minus target

```sql
SELECT
    customer_id,
    segment
FROM source_customers
EXCEPT
SELECT
    customer_id,
    segment
FROM target_customers;
```

Result:

```text
3 | Gold
```

#### Target minus source

```sql
SELECT
    customer_id,
    segment
FROM target_customers
EXCEPT
SELECT
    customer_id,
    segment
FROM source_customers;
```

Result:

```text
4 | Bronze
```

### Why

Both tables have three rows, but the row sets differ.

```text
equal count
≠
equal content
```

### Common Wrong Approach

Comparing only:

```sql
SELECT COUNT(*) FROM ...
```

### Production Note

For reconciliation, compare both directions and, where useful, also compare measures and partition-level counts.

---

## Question 19 — Sargable Time Predicate

**Difficulty:** Moderate

**Primary topics:** sargability, index, half-open range, EXPLAIN

### Problem

You have:

```sql
CREATE INDEX idx_events_created_at
ON events(created_at);
```

The query is:

```sql
SELECT *
FROM events
WHERE DATE(created_at) = DATE '2026-09-28';
```

Rewrite it as a half-open timestamp range. Then show how you would validate the performance change.

### Solution

```sql
SELECT *
FROM events
WHERE created_at >= TIMESTAMP '2026-09-28 00:00:00'
  AND created_at <  TIMESTAMP '2026-09-29 00:00:00';
```

Validate with:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM events
WHERE created_at >= TIMESTAMP '2026-09-28 00:00:00'
  AND created_at <  TIMESTAMP '2026-09-29 00:00:00';
```

Inspect:

```text
scan type
estimated rows
actual rows
loops
buffers
execution time
```

### Common Wrong Approach

Assuming that an index must be used because it exists.

### Production Note

The optimizer chooses the physical plan from cost estimates and statistics. Performance changes must be measured rather than assumed.

---

## Question 20 — Safe Lost-Update Prevention

**Difficulty:** Moderate

**Primary topics:** transactions, READ COMMITTED, lost updates, FOR UPDATE, atomic UPDATE

### Problem

Two workers need to increment the same counter.

Initial state:

```text
counter = 0
```

Explain the lost-update risk in:

```text
read → calculate → overwrite
```

Then provide:

1. a `FOR UPDATE` solution;
2. an atomic `UPDATE` solution.

### Solution

Unsafe reasoning:

```text
A reads 0
B reads 0
A writes 1
B writes 1
```

One logical increment is lost.

#### FOR UPDATE

```sql
BEGIN;

SELECT value
FROM counters
WHERE counter_id = 1
FOR UPDATE;

UPDATE counters
SET value = value + 1
WHERE counter_id = 1;

COMMIT;
```

#### Atomic update

```sql
UPDATE counters
SET value = value + 1
WHERE counter_id = 1;
```

### Why

The atomic SQL expression does not require the application to overwrite a stale absolute value.

### Common Wrong Approach

Read the counter into application code, increment it, then update:

```sql
SET value = 1
```

### Production Note

Always ask whether the business state transition can be expressed directly as an atomic SQL operation.

---

# Part III — Hard

## Question 21 — KPI Bundle with Ratios and Percentiles

**Difficulty:** Hard

**Primary topics:** conditional aggregation, FILTER, ratio metrics, percentiles, STDDEV, NULLIF

### Problem

Given:

```sql
CREATE TEMP TABLE order_metrics (
    country TEXT,
    order_id INTEGER,
    amount NUMERIC(12, 2),
    status TEXT
);

INSERT INTO order_metrics VALUES
    ('India', 1, 100, 'completed'),
    ('India', 2, 300, 'completed'),
    ('India', 3, 50,  'cancelled'),
    ('US',    4, 1000, 'completed'),
    ('US',    5, 10,   'cancelled');
```

For each country calculate:

```text
total_orders
completed_orders
completed_revenue
completion_rate
average_completed_order
median_completed_order
p95_completed_order
stddev_completed_order
```

The completion rate is:

```text
completed_orders / total_orders
```

### Solution

```sql
SELECT
    country,
    COUNT(*) AS total_orders,
    COUNT(*) FILTER (
        WHERE status = 'completed'
    ) AS completed_orders,
    SUM(amount) FILTER (
        WHERE status = 'completed'
    ) AS completed_revenue,
    COUNT(*) FILTER (
        WHERE status = 'completed'
    )::NUMERIC
    / NULLIF(COUNT(*), 0) AS completion_rate,
    AVG(amount) FILTER (
        WHERE status = 'completed'
    ) AS average_completed_order,
    PERCENTILE_CONT(0.50)
        WITHIN GROUP (ORDER BY amount)
        FILTER (WHERE status = 'completed') AS median_completed_order,
    PERCENTILE_CONT(0.95)
        WITHIN GROUP (ORDER BY amount)
        FILTER (WHERE status = 'completed') AS p95_completed_order,
    STDDEV(amount) FILTER (
        WHERE status = 'completed'
    ) AS stddev_completed_order
FROM order_metrics
GROUP BY country
ORDER BY country;
```

### Why

The numerator and denominator use compatible populations.

`FILTER` avoids repeating a CASE expression for each metric.

### Common Wrong Approach

Using:

```text
completed_orders / COUNT(DISTINCT customer_id)
```

when the metric is supposed to be completion per order.

### Production Note

Percentiles and standard deviation can be more expensive than simple counts and sums. First preserve the correct metric definition, then measure performance.

---

## Question 22 — Effective-Dated Range Join with LATERAL

**Difficulty:** Hard

**Primary topics:** range join, half-open interval, LATERAL, latest-effective-record

### Problem

Given:

```sql
CREATE TEMP TABLE product_prices (
    product_id INTEGER,
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    price NUMERIC(12, 2)
);

CREATE TEMP TABLE orders (
    order_id INTEGER,
    product_id INTEGER,
    ordered_at TIMESTAMP
);

INSERT INTO product_prices VALUES
    (1, '2026-09-01', '2026-09-10', 50),
    (1, '2026-09-10', '2026-09-20', 60),
    (1, '2026-09-20', '9999-12-31', 70);

INSERT INTO orders VALUES
    (100, 1, '2026-09-05'),
    (101, 1, '2026-09-12'),
    (102, 1, '2026-09-25');
```

Return the price that was effective for each order.

Then write a PostgreSQL `LATERAL` alternative.

### Solution

#### Range join

```sql
SELECT
    o.order_id,
    o.ordered_at,
    p.price
FROM orders AS o
JOIN product_prices AS p
  ON p.product_id = o.product_id
 AND o.ordered_at >= p.valid_from
 AND o.ordered_at < p.valid_to
ORDER BY o.order_id;
```

Expected:

```text
100 | 2026-09-05 | 50
101 | 2026-09-12 | 60
102 | 2026-09-25 | 70
```

#### LATERAL

```sql
SELECT
    o.order_id,
    o.ordered_at,
    p.price
FROM orders AS o
LEFT JOIN LATERAL (
    SELECT
        pp.price
    FROM product_prices AS pp
    WHERE pp.product_id = o.product_id
      AND pp.valid_from <= o.ordered_at
    ORDER BY pp.valid_from DESC
    FETCH FIRST 1 ROW ONLY
) AS p
  ON TRUE
ORDER BY o.order_id;
```

### Why

The range join explicitly checks:

```text
event >= valid_from
event < valid_to
```

The `LATERAL` query instead finds the latest version at or before the event.

### Common Wrong Approach

Join only on:

```sql
product_id
```

This can return multiple price versions for one order.

### Production Note

Effective-dated joins are common in historical analytics. Boundary semantics must be defined before SQL is written.

---

## Question 23 — Top-N Per Group with Ties

**Difficulty:** Hard

**Primary topics:** RANK, ROW_NUMBER, DENSE_RANK, PARTITION BY, deterministic ordering, QUALIFY

### Problem

Given:

```sql
CREATE TEMP TABLE salesperson_revenue (
    country TEXT,
    salesperson TEXT,
    revenue INTEGER
);

INSERT INTO salesperson_revenue VALUES
    ('India', 'Asha', 100),
    ('India', 'Ben', 100),
    ('India', 'Cara', 80),
    ('US', 'Dan', 200),
    ('US', 'Eve', 150),
    ('US', 'Finn', 150);
```

Return the top **two rank positions** per country, preserving ties.

Then explain how the result changes if the requirement is exactly two rows per country.

### Solution

```sql
WITH ranked AS (
    SELECT
        country,
        salesperson,
        revenue,
        RANK() OVER (
            PARTITION BY country
            ORDER BY revenue DESC
        ) AS rnk
    FROM salesperson_revenue
)
SELECT
    country,
    salesperson,
    revenue,
    rnk
FROM ranked
WHERE rnk <= 2
ORDER BY country, rnk, salesperson;
```

Expected conceptually:

```text
India | Asha | 100 | 1
India | Ben  | 100 | 1
India | Cara | 80  | 3

US    | Dan  | 200 | 1
US    | Eve  | 150 | 2
US    | Finn | 150 | 2
```

For exactly two rows per country:

```sql
WITH ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY country
            ORDER BY revenue DESC, salesperson
        ) AS rn
    FROM salesperson_revenue
)
SELECT *
FROM ranked
WHERE rn <= 2;
```

Where supported, DuckDB-style filtering can use:

```sql
SELECT
    *,
    RANK() OVER (
        PARTITION BY country
        ORDER BY revenue DESC
    ) AS rnk
FROM salesperson_revenue
QUALIFY rnk <= 2;
```

### Common Wrong Approach

Using `ROW_NUMBER()` for a requirement that says ties must be preserved.

### Production Note

Clarify "top N rows" versus "top N rank positions" before implementing.

---

## Question 24 — ROLLUP with Actual NULL Data

**Difficulty:** Hard

**Primary topics:** ROLLUP, GROUPING, NULL, aggregation

### Problem

Given:

```sql
CREATE TEMP TABLE orders (
    country TEXT,
    payment_method TEXT,
    amount NUMERIC(12, 2)
);

INSERT INTO orders VALUES
    ('India', 'card', 100),
    ('India', 'bank', 200),
    ('US', 'card', 300),
    (NULL, 'card', 50);
```

Produce:

```text
country
payment_method
revenue
```

for:

```text
country + payment_method detail
country subtotal
grand total
```

Use `GROUPING()` so a real NULL country is not confused with a subtotal marker.

### Solution

```sql
SELECT
    country,
    payment_method,
    SUM(amount) AS revenue,
    GROUPING(country) AS country_grouped,
    GROUPING(payment_method) AS payment_method_grouped
FROM orders
GROUP BY ROLLUP (
    country,
    payment_method
)
ORDER BY
    GROUPING(country),
    country,
    GROUPING(payment_method),
    payment_method;
```

### Why

A row can contain:

```text
country = NULL
```

because the source data contains a NULL.

A subtotal can also display:

```text
country = NULL
```

`GROUPING(country)` tells them apart.

### Common Wrong Approach

Treating every NULL in the result as a subtotal.

### Production Note

Aggregation-level metadata and business data values must not be conflated.

---

## Question 25 — CTE Materialization Choice

**Difficulty:** Hard

**Primary topics:** CTEs, MATERIALIZED, NOT MATERIALIZED, performance reasoning

### Problem

A PostgreSQL query contains an expensive CTE that may be referenced more than once.

Explain when you might test:

```sql
MATERIALIZED
```

versus:

```sql
NOT MATERIALIZED
```

and show one valid example of each.

### Solution

#### MATERIALIZED

```sql
WITH customer_totals AS MATERIALIZED (
    SELECT
        customer_id,
        SUM(amount) AS total_spend
    FROM orders
    GROUP BY customer_id
)
SELECT *
FROM customer_totals
WHERE total_spend > 1000;
```

The explicit materialization creates a deliberate intermediate boundary.

#### NOT MATERIALIZED

```sql
WITH customer_totals AS NOT MATERIALIZED (
    SELECT
        customer_id,
        SUM(amount) AS total_spend
    FROM orders
    GROUP BY customer_id
)
SELECT *
FROM customer_totals
WHERE total_spend > 1000;
```

This gives the optimizer more opportunity to inline/transform the expression.

### Reasoning

Materialization can help when:

```text
expensive result
+
multiple references
```

but can hurt when:

```text
large intermediate
+
filter could otherwise be pushed down
```

Inlining can also hurt if expensive work is effectively repeated.

### Common Wrong Approach

```text
MATERIALIZED = fast
NOT MATERIALIZED = fast
```

Those are not universal rules.

### Production Note

Use `EXPLAIN` and measurements rather than CTE folklore.

---

## Question 26 — Production Event Schema

**Difficulty:** Hard

**Primary topics:** DDL, data types, constraints, JSONB, arrays, identity, partitioning, safe schema change

### Problem

Design a PostgreSQL event table with:

```text
event_id
customer_id
event_time
event_type
amount
metadata
tags
```

Requirements:

- identity event ID;
- required customer and event time;
- non-negative exact monetary amount;
- JSON metadata;
- text-array tags;
- range partition by event time;
- a future compatible column must be addable without immediately breaking existing writers.

### Solution

```sql
CREATE TABLE events (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY,
    customer_id BIGINT NOT NULL,
    event_time TIMESTAMPTZ NOT NULL,
    event_type TEXT NOT NULL,
    amount NUMERIC(18, 2) NOT NULL CHECK (amount >= 0),
    metadata JSONB,
    tags TEXT[],
    PRIMARY KEY (event_id, event_time)
) PARTITION BY RANGE (event_time);
```

Example partition:

```sql
CREATE TABLE events_2026_09
PARTITION OF events
FOR VALUES FROM ('2026-09-01')
           TO ('2026-10-01');
```

Compatible schema evolution:

```sql
ALTER TABLE events
ADD COLUMN source_system TEXT;
```

Use an expand-and-contract approach for breaking changes:

```text
expand
→ migrate writers
→ backfill
→ validate
→ cut over
→ contract later
```

### Common Wrong Approach

Using `FLOAT` for exact monetary semantics.

### Production Note

Partitioning should align with the workload's access boundaries. It is not automatically beneficial.

---

## Question 27 — Choose Indexes for a Mixed Workload

**Difficulty:** Hard

**Primary topics:** B-tree, composite indexes, leftmost-prefix, INCLUDE, partial indexes, expression indexes

### Problem

For:

```sql
CREATE TABLE orders (
    order_id BIGINT PRIMARY KEY,
    customer_id BIGINT,
    status TEXT,
    email TEXT,
    created_at TIMESTAMP,
    amount NUMERIC(12, 2)
);
```

the workload often runs:

```text
A. recent orders for one customer
B. active orders for one customer
C. case-insensitive email lookup
D. return order_id + amount for active customer orders
```

Propose a small set of indexes and explain the trade-offs.

### Solution

#### A/B — Composite

```sql
CREATE INDEX idx_orders_customer_created
ON orders (customer_id, created_at DESC);
```

For the active subset:

```sql
CREATE INDEX idx_orders_active_customer_created
ON orders (customer_id, created_at DESC)
WHERE status = 'active';
```

#### C — Expression

```sql
CREATE INDEX idx_orders_lower_email
ON orders (LOWER(email));
```

#### D — Covering/partial

```sql
CREATE INDEX idx_orders_active_customer_covering
ON orders (customer_id, created_at DESC)
INCLUDE (order_id, amount)
WHERE status = 'active';
```

### Leftmost-prefix reasoning

An index:

```text
(customer_id, created_at)
```

is naturally aligned with:

```text
customer_id equality
+
created_at ordering/range
```

It is not equivalent to an independent index on `created_at`.

### Common Wrong Approach

Adding many indexes without checking actual workload and write cost.

### Production Note

Every index is an access path with a read benefit and write/storage maintenance cost.

---

## Question 28 — Read a Simulated EXPLAIN Plan

**Difficulty:** Hard

**Primary topics:** EXPLAIN, estimated vs actual rows, loops, Nested Loop

### Problem

A query has this **simulated** plan:

```text
Nested Loop
  actual rows=50 loops=1
  -> Seq Scan on customers
       actual rows=50 loops=1
  -> Index Scan using idx_orders_customer_id on orders
       actual rows=1 loops=50
```

The team expected roughly 20,000 orders per customer but the final result contains only 50 rows.

Explain what you inspect first.

### Solution

The plan says:

```text
outer rows = 50
inner rows per loop = 1
loops = 50
final rows = 50
```

The primary suspicion is semantic/cardinality mismatch, not automatically a bad Nested Loop.

Investigate:

```sql
SELECT
    customer_id,
    COUNT(*) AS order_count
FROM orders
GROUP BY customer_id
ORDER BY order_count DESC;
```

Then inspect the join predicate and any filters.

### Correct professional reasoning

```text
expected grain
vs
actual grain
```

The plan shows the physical result, but the mismatch may be caused by:

- an overly restrictive join;
- unexpected data;
- a filter;
- incorrect assumptions about relationship cardinality.

### Common Wrong Approach

Immediately replacing the Nested Loop with another join algorithm.

### Production Note

Plans are evidence. Read cardinality, loops, timing, and predicates together.

---

## Question 29 — Write Skew Under Stronger Isolation

**Difficulty:** Hard

**Primary topics:** write skew, REPEATABLE READ, SERIALIZABLE, invariant

### Problem

Two doctors are on call:

```text
Doctor A → true
Doctor B → true
```

Invariant:

```text
At least one doctor must remain on call.
```

Each transaction checks the number of on-call doctors and, if there are two, turns one doctor off.

Explain how both transactions can independently make a locally reasonable decision yet jointly violate the invariant.

Then explain a PostgreSQL approach that can detect the unsafe concurrent outcome.

### Solution

The transactions can see:

```text
2 doctors on call
```

Then:

```text
A turns A off
B turns B off
```

Final state:

```text
0 doctors on call
```

The invariant spans multiple rows.

A suitable stronger strategy is:

```sql
BEGIN ISOLATION LEVEL SERIALIZABLE;
```

and then perform the read and write in the transaction.

PostgreSQL can reject one transaction when the concurrent execution cannot safely be serialized.

### Recovery

```text
ROLLBACK
→ backoff
→ retry entire transaction
```

### Common Wrong Approach

Locking only the row that each doctor updates and assuming that one-row lock automatically protects the full business rule.

### Production Note

Concurrency controls should protect the **invariant**, not merely the most obvious row.

---

## Question 30 — Incremental State with Tombstones

**Difficulty:** Hard

**Primary topics:** ON CONFLICT, source deduplication, tombstones, `IS DISTINCT FROM`, delete semantics

### Problem

Target:

```sql
CREATE TEMP TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    segment TEXT,
    is_deleted BOOLEAN NOT NULL DEFAULT false
);

INSERT INTO customers VALUES
    (1, 'Bronze', false),
    (2, 'Silver', false);
```

Incoming source:

```sql
CREATE TEMP TABLE staging_customers (
    customer_id INTEGER,
    segment TEXT,
    operation TEXT,
    updated_at TIMESTAMP,
    ingestion_id INTEGER
);

INSERT INTO staging_customers VALUES
    (1, 'Bronze', 'UPSERT', '2026-09-28 10:00:00', 1),
    (2, 'Gold',   'UPSERT', '2026-09-28 10:00:00', 2),
    (2, 'Platinum','UPSERT','2026-09-28 10:00:00', 3),
    (3, 'Bronze', 'UPSERT', '2026-09-28 10:00:00', 4),
    (1, NULL,     'DELETE', '2026-09-28 11:00:00', 5);
```

Define a deterministic rule:

```text
latest updated_at
→ highest ingestion_id
```

Resolve source duplicates, then apply the result with delete and upsert semantics.

### Solution

Resolve the source:

```sql
WITH ranked AS (
    SELECT
        s.*,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY
                updated_at DESC,
                ingestion_id DESC
        ) AS rn
    FROM staging_customers AS s
)
SELECT
    customer_id,
    segment,
    operation
FROM ranked
WHERE rn = 1;
```

For customer 2, ingestion 3 wins.

Apply inside one transaction:

```sql
BEGIN;

WITH ranked AS (
    SELECT
        s.*,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY
                updated_at DESC,
                ingestion_id DESC
        ) AS rn
    FROM staging_customers AS s
),
resolved AS (
    SELECT *
    FROM ranked
    WHERE rn = 1
)
UPDATE customers AS c
SET
    is_deleted = true
FROM resolved AS r
WHERE c.customer_id = r.customer_id
  AND r.operation = 'DELETE';

WITH ranked AS (
    SELECT
        s.*,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY
                updated_at DESC,
                ingestion_id DESC
        ) AS rn
    FROM staging_customers AS s
),
resolved AS (
    SELECT *
    FROM ranked
    WHERE rn = 1
)
INSERT INTO customers (
    customer_id,
    segment,
    is_deleted
)
SELECT
    customer_id,
    segment,
    false
FROM resolved
WHERE operation = 'UPSERT'
ON CONFLICT (customer_id)
DO UPDATE
SET
    segment = EXCLUDED.segment,
    is_deleted = false
WHERE
    customers.segment IS DISTINCT FROM EXCLUDED.segment
    OR customers.is_deleted IS DISTINCT FROM EXCLUDED.is_deleted;

COMMIT;
```

Expected business result:

```text
1 → deleted
2 → Platinum
3 → Bronze
```

### Common Wrong Approach

Applying raw staging rows directly and letting customer 2 mutate twice without an explicit survivor rule.

### Production Note

Delete semantics and source ordering are part of the data contract. Missing rows are not automatically deletes.

---

# Part IV — Advanced

## Question 31 — Diagnose a Fan Trap and Reconcile It

**Difficulty:** Advanced

**Primary topics:** join explosion, preaggregation, aggregation, reconciliation, grain

### Problem

A customer has:

```text
orders:
100
200

refunds:
50
20
```

The query joins raw orders and raw refunds and reports:

```text
order_revenue = 600
refunds = 140
```

Correct values are:

```text
order_revenue = 300
refunds = 70
```

Explain exactly how the multiplication happened and produce a corrected query.

### Solution

The raw join creates:

```text
2 orders × 2 refunds = 4 rows
```

Each order is repeated once for each refund.

Preaggregate separately:

```sql
WITH order_totals AS (
    SELECT
        customer_id,
        SUM(amount) AS order_revenue
    FROM orders
    GROUP BY customer_id
),
refund_totals AS (
    SELECT
        customer_id,
        SUM(amount) AS refund_total
    FROM refunds
    GROUP BY customer_id
)
SELECT
    c.customer_id,
    COALESCE(o.order_revenue, 0) AS order_revenue,
    COALESCE(r.refund_total, 0) AS refund_total
FROM customers AS c
LEFT JOIN order_totals AS o
  ON o.customer_id = c.customer_id
LEFT JOIN refund_totals AS r
  ON r.customer_id = c.customer_id;
```

### Reconciliation

```sql
SELECT
    (SELECT SUM(amount) FROM orders WHERE customer_id = 1)
        AS expected_order_revenue,
    (SELECT SUM(amount) FROM refunds WHERE customer_id = 1)
        AS expected_refund_total;
```

Compare those to the final query.

### Common Wrong Approach

Using `DISTINCT` after the inflated join.

`DISTINCT` cannot reconstruct the correct aggregate contribution.

### Production Note

When a metric is inflated, first ask whether a join changed the grain before changing the aggregate function.

---

## Question 32 — Performance Tuning with a Simulated Plan

**Difficulty:** Advanced

**Primary topics:** EXPLAIN ANALYZE, sargability, composite/partial indexes, measure-first tuning

### Problem

A 500-million-row orders table runs:

```sql
SELECT
    order_id,
    customer_id,
    amount
FROM orders
WHERE status = 'active'
  AND DATE(created_at) = DATE '2026-09-28'
ORDER BY created_at DESC
LIMIT 100;
```

Existing indexes:

```text
PRIMARY KEY(order_id)
INDEX(status)
```

Propose a tuning sequence and explain why you should not simply add five indexes.

### Solution

#### Step 1 — Fix the predicate shape

```sql
SELECT
    order_id,
    customer_id,
    amount
FROM orders
WHERE status = 'active'
  AND created_at >= TIMESTAMP '2026-09-28 00:00:00'
  AND created_at <  TIMESTAMP '2026-09-29 00:00:00'
ORDER BY created_at DESC
LIMIT 100;
```

#### Step 2 — Consider a partial access path

```sql
CREATE INDEX idx_orders_active_created
ON orders (created_at DESC)
INCLUDE (order_id, customer_id, amount)
WHERE status = 'active';
```

Test this against the real data.

#### Step 3 — Measure

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    order_id,
    customer_id,
    amount
FROM orders
WHERE status = 'active'
  AND created_at >= TIMESTAMP '2026-09-28 00:00:00'
  AND created_at <  TIMESTAMP '2026-09-29 00:00:00'
ORDER BY created_at DESC
LIMIT 100;
```

Inspect:

```text
actual rows
loops
sorts
buffers
execution time
```

### Why the existing status index may not be enough

The workload needs:

```text
status restriction
+
time restriction
+
recent ordering
```

An index only on status may still require large filtering and sorting work.

### Common Wrong Approach

"Indexes are cheap; add every possible combination."

### Production Note

Use:

```text
measure
→ read plan
→ form hypothesis
→ one change
→ remeasure
```

---

## Question 33 — Isolation Timeline: Visibility vs Blocking

**Difficulty:** Advanced

**Primary topics:** READ COMMITTED, REPEATABLE READ, MVCC, snapshots, blocking

### Problem

Initial:

```text
balance = 100
```

Session A:

```sql
BEGIN;
SELECT balance
FROM accounts
WHERE account_id = 1;
```

Session B:

```sql
BEGIN;
UPDATE accounts
SET balance = 150
WHERE account_id = 1;
COMMIT;
```

Session A then runs:

```sql
SELECT balance
FROM accounts
WHERE account_id = 1;
```

Explain the expected PostgreSQL behavior under:

```text
READ COMMITTED
REPEATABLE READ
```

Then explain how `FOR UPDATE` changes the question from ordinary visibility to explicit locking.

### Solution

#### READ COMMITTED

```text
A first SELECT → 100
B UPDATE + COMMIT → 150
A second SELECT → can see 150
```

because each statement gets an appropriate committed view.

#### REPEATABLE READ

```text
A begins transaction
→ transaction snapshot established

B commits update

A's ordinary reads remain consistent with A's snapshot
```

#### `FOR UPDATE`

```sql
SELECT balance
FROM accounts
WHERE account_id = 1
FOR UPDATE;
```

A is now explicitly requesting a row lock.

A later conflicting transaction may have to wait.

### Common Wrong Approach

"MVCC means reads never block and there are no locks."

### Production Note

Always separate:

```text
visibility
```

from:

```text
blocking
```

and inspect both.

---

## Question 34 — Multi-Worker Queue with SKIP LOCKED

**Difficulty:** Advanced

**Primary topics:** transactions, FOR UPDATE, SKIP LOCKED, worker claiming, idempotency

### Problem

Create:

```sql
CREATE TEMP TABLE jobs (
    job_id INTEGER PRIMARY KEY,
    status TEXT NOT NULL,
    payload TEXT
);

INSERT INTO jobs VALUES
    (1, 'ready', 'a'),
    (2, 'ready', 'b'),
    (3, 'ready', 'c'),
    (4, 'ready', 'd'),
    (5, 'ready', 'e');
```

Design a claim operation where two workers can claim different ready jobs without waiting for already-claimed rows.

### Solution

#### SESSION A

```sql
BEGIN;

WITH next_jobs AS (
    SELECT job_id
    FROM jobs
    WHERE status = 'ready'
    ORDER BY job_id
    FOR UPDATE SKIP LOCKED
    LIMIT 2
)
UPDATE jobs AS j
SET status = 'running'
FROM next_jobs AS n
WHERE j.job_id = n.job_id
RETURNING j.job_id;

COMMIT;
```

Suppose A gets:

```text
1, 2
```

#### SESSION B

Run the same operation while A's claim is still uncommitted if you want to demonstrate the skip:

```sql
BEGIN;

WITH next_jobs AS (
    SELECT job_id
    FROM jobs
    WHERE status = 'ready'
    ORDER BY job_id
    FOR UPDATE SKIP LOCKED
    LIMIT 2
)
UPDATE jobs AS j
SET status = 'running'
FROM next_jobs AS n
WHERE j.job_id = n.job_id
RETURNING j.job_id;

COMMIT;
```

B can obtain:

```text
3, 4
```

### Why

`SKIP LOCKED` changes the policy from:

```text
wait for locked rows
```

to:

```text
find other unlocked work
```

### Common Wrong Approach

Use `SKIP LOCKED` for work that must be processed in strict order.

### Production Note

A real queue also needs recovery for abandoned jobs and idempotent processing after worker failure.

---

## Question 35 — Incremental Product Load with Validation and Reconciliation

**Difficulty:** Advanced

**Primary topics:** staging, deduplication, ON CONFLICT, IS DISTINCT FROM, validation, reconciliation

### Problem

Target:

```sql
CREATE TEMP TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT,
    price NUMERIC(12, 2)
);

INSERT INTO products VALUES
    (1, 'Keyboard', 50),
    (2, 'Mouse', 25);
```

Staging:

```sql
CREATE TEMP TABLE staging_products (
    product_id INTEGER,
    product_name TEXT,
    price NUMERIC(12, 2),
    updated_at TIMESTAMP,
    source_priority INTEGER,
    ingestion_id INTEGER
);

INSERT INTO staging_products VALUES
    (1, 'Keyboard', 50, '2026-09-28 10:00:00', 1, 100),
    (2, 'Mouse Pro', 30, '2026-09-28 11:00:00', 1, 101),
    (2, 'Mouse Pro', 31, '2026-09-28 11:00:00', 2, 102),
    (3, 'Monitor', 200, '2026-09-28 12:00:00', 1, 103);
```

Rule:

```text
latest updated_at
→ highest source_priority
→ highest ingestion_id
```

Build the pipeline:

```text
validate
→ dedupe
→ upsert
→ reconcile
```

### Solution

#### Validation

```sql
SELECT *
FROM staging_products
WHERE product_id IS NULL
   OR product_name IS NULL;
```

Expected:

```text
0 rows
```

#### Dedupe

```sql
WITH ranked AS (
    SELECT
        s.*,
        ROW_NUMBER() OVER (
            PARTITION BY product_id
            ORDER BY
                updated_at DESC,
                source_priority DESC,
                ingestion_id DESC
        ) AS rn
    FROM staging_products AS s
)
SELECT
    product_id,
    product_name,
    price
FROM ranked
WHERE rn = 1;
```

Product 2 resolves to:

```text
price = 31
```

#### Apply

```sql
INSERT INTO products (
    product_id,
    product_name,
    price
)
SELECT
    product_id,
    product_name,
    price
FROM (
    SELECT
        s.*,
        ROW_NUMBER() OVER (
            PARTITION BY product_id
            ORDER BY
                updated_at DESC,
                source_priority DESC,
                ingestion_id DESC
        ) AS rn
    FROM staging_products AS s
) AS ranked
WHERE rn = 1
ON CONFLICT (product_id)
DO UPDATE
SET
    product_name = EXCLUDED.product_name,
    price = EXCLUDED.price
WHERE
    products.product_name IS DISTINCT FROM EXCLUDED.product_name
    OR products.price IS DISTINCT FROM EXCLUDED.price;
```

Expected target:

```text
1 | Keyboard   | 50
2 | Mouse Pro  | 31
3 | Monitor    | 200
```

#### Duplicate-source assertion

```sql
SELECT product_id
FROM staging_products
GROUP BY product_id
HAVING COUNT(*) > 1;
```

This is diagnostic and should drive the deduplication step rather than being silently ignored.

### Common Wrong Approach

Blindly applying the raw staging table.

### Production Note

Staging is a controllable boundary between ingestion and target mutation.

---

## Question 36 — MERGE with Delete and Deterministic Source

**Difficulty:** Advanced

**Primary topics:** MERGE, matched/not-matched, source deduplication, conditional update, delete branch

### Problem

Target:

```sql
CREATE TEMP TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT,
    price NUMERIC(12, 2)
);

INSERT INTO products VALUES
    (1, 'Keyboard', 50),
    (2, 'Mouse', 25);
```

Source:

```sql
CREATE TEMP TABLE staging_products (
    product_id INTEGER,
    product_name TEXT,
    price NUMERIC(12, 2),
    operation TEXT,
    updated_at TIMESTAMP,
    ingestion_id INTEGER
);

INSERT INTO staging_products VALUES
    (1, 'Keyboard', 50, 'UPSERT', '2026-09-28 10:00:00', 1),
    (2, 'Mouse Pro', 30, 'UPSERT', '2026-09-28 11:00:00', 2),
    (2, 'Mouse Pro', 31, 'UPSERT', '2026-09-28 11:00:00', 3),
    (3, 'Monitor', 200, 'UPSERT', '2026-09-28 12:00:00', 4),
    (1, NULL, NULL, 'DELETE', '2026-09-28 13:00:00', 5);
```

Rule:

```text
latest timestamp
→ highest ingestion_id
```

Apply:

```text
DELETE → delete target
UPSERT + changed → update
UPSERT + new → insert
```

### Solution

```sql
WITH ranked AS (
    SELECT
        s.*,
        ROW_NUMBER() OVER (
            PARTITION BY product_id
            ORDER BY
                updated_at DESC,
                ingestion_id DESC
        ) AS rn
    FROM staging_products AS s
),
resolved AS (
    SELECT
        product_id,
        product_name,
        price,
        operation
    FROM ranked
    WHERE rn = 1
)
MERGE INTO products AS t
USING resolved AS s
ON t.product_id = s.product_id

WHEN MATCHED
     AND s.operation = 'DELETE'
THEN
    DELETE

WHEN MATCHED
     AND s.operation = 'UPSERT'
     AND (
         t.product_name IS DISTINCT FROM s.product_name
         OR t.price IS DISTINCT FROM s.price
     )
THEN
    UPDATE SET
        product_name = s.product_name,
        price = s.price

WHEN NOT MATCHED
     AND s.operation = 'UPSERT'
THEN
    INSERT (
        product_id,
        product_name,
        price
    )
    VALUES (
        s.product_id,
        s.product_name,
        s.price
    );
```

Expected:

```text
2 | Mouse Pro | 31
3 | Monitor   | 200
```

Product 1 is deleted because its latest source row is the DELETE event.

### Common Wrong Approach

Merging directly from raw staging and hoping duplicate source keys never occur.

### Production Note

`MERGE` is powerful, but source-grain discipline remains the responsibility of the pipeline.

---

## Question 37 — Prove Incremental Idempotency

**Difficulty:** Advanced

**Primary topics:** idempotency, repeated runs, EXCEPT, business state vs metadata

### Problem

You have a deterministic upsert:

```sql
INSERT INTO products (...)
SELECT ...
FROM staging_products
ON CONFLICT (product_id)
DO UPDATE
SET ...
WHERE
    products.product_name IS DISTINCT FROM EXCLUDED.product_name
    OR products.price IS DISTINCT FROM EXCLUDED.price;
```

Design a SQL test proving that running the same source twice leaves the same business state after the second run.

### Solution

Capture the business state after the first successful run:

```sql
CREATE TEMP TABLE state_after_first_run AS
SELECT
    product_id,
    product_name,
    price
FROM products;
```

Replay the same source.

Then compare:

```sql
(
    SELECT
        product_id,
        product_name,
        price
    FROM state_after_first_run

    EXCEPT

    SELECT
        product_id,
        product_name,
        price
    FROM products
)
UNION ALL
(
    SELECT
        product_id,
        product_name,
        price
    FROM products

    EXCEPT

    SELECT
        product_id,
        product_name,
        price
    FROM state_after_first_run
);
```

Expected:

```text
0 rows
```

### Why

The comparison is bidirectional.

A single `EXCEPT` would detect only one direction of difference.

### Common Wrong Approach

Compare only:

```sql
COUNT(*)
```

Equal counts can hide changed values.

### Production Note

Define idempotency against **business state**. Operational metadata such as `pipeline_run_id` may legitimately change.

---

## Question 38 — Build and Validate SCD Type 2

**Difficulty:** Advanced

**Primary topics:** SCD2, surrogate key, LEAD, validity intervals, integrity assertions

### Problem

A customer's history is:

```text
Bronze → 2026-01-01
Silver → 2026-01-10
Gold   → 2026-01-20
```

Build an SCD2 result containing:

```text
customer_sk
customer_id
segment
valid_from
valid_to
is_current
```

Use:

```text
[valid_from, valid_to)
```

Then write assertions for:

1. exactly one current row;
2. no overlaps;
3. no unintended gaps.

### Solution

Source:

```sql
CREATE TEMP TABLE customer_history_source (
    customer_id INTEGER,
    segment TEXT,
    effective_date DATE,
    source_event_id INTEGER
);

INSERT INTO customer_history_source VALUES
    (101, 'Bronze', '2026-01-01', 1),
    (101, 'Silver', '2026-01-10', 2),
    (101, 'Gold',   '2026-01-20', 3);
```

Build:

```sql
WITH ordered AS (
    SELECT
        customer_id,
        segment,
        effective_date,
        source_event_id,
        LEAD(effective_date) OVER (
            PARTITION BY customer_id
            ORDER BY effective_date, source_event_id
        ) AS next_effective_date,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY effective_date DESC, source_event_id DESC
        ) AS reverse_rank
    FROM customer_history_source
)
SELECT
    ROW_NUMBER() OVER (
        ORDER BY customer_id, effective_date, source_event_id
    ) AS customer_sk,
    customer_id,
    segment,
    effective_date AS valid_from,
    COALESCE(
        next_effective_date,
        DATE '9999-12-31'
    ) AS valid_to,
    reverse_rank = 1 AS is_current
FROM ordered
ORDER BY customer_id, valid_from;
```

Expected:

```text
101 | Bronze | 2026-01-01 | 2026-01-10 | false
101 | Silver | 2026-01-10 | 2026-01-20 | false
101 | Gold   | 2026-01-20 | 9999-12-31 | true
```

#### Assertion 1 — Exactly one current row

```sql
SELECT customer_id
FROM dim_customer
GROUP BY customer_id
HAVING COUNT(*) FILTER (WHERE is_current) <> 1;
```

Expected:

```text
0 rows
```

#### Assertion 2 — No overlap

```sql
WITH ordered AS (
    SELECT
        *,
        LAG(valid_to) OVER (
            PARTITION BY customer_id
            ORDER BY valid_from, customer_sk
        ) AS previous_valid_to
    FROM dim_customer
)
SELECT *
FROM ordered
WHERE previous_valid_to IS NOT NULL
  AND valid_from < previous_valid_to;
```

#### Assertion 3 — No unintended gap

```sql
WITH ordered AS (
    SELECT
        *,
        LAG(valid_to) OVER (
            PARTITION BY customer_id
            ORDER BY valid_from, customer_sk
        ) AS previous_valid_to
    FROM dim_customer
)
SELECT *
FROM ordered
WHERE previous_valid_to IS NOT NULL
  AND valid_from <> previous_valid_to;
```

### Common Wrong Approach

Using inclusive end dates for both neighboring versions.

### Production Note

SCD2 correctness is a set of invariants. Successful SQL execution does not prove historical integrity.

---

## Question 39 — Late-Arriving SCD2 Repair and Point-in-Time Revenue

**Difficulty:** Advanced

**Primary topics:** late-arriving changes, out-of-order history, SCD2, LEAD, point-in-time joins

### Problem

Existing customer history:

```text
Bronze [2026-01-01, 2026-01-10)
Silver [2026-01-10, 2026-01-20)
Gold   [2026-01-20, 9999-12-31)
```

A late event arrives on January 25:

```text
customer_id = 101
segment = Starter
effective_date = 2026-01-07
```

An order happened on:

```text
2026-01-08
```

Tasks:

1. repair the SCD2 history;
2. write the point-in-time join;
3. explain what a current-state join would return instead.

### Solution

Correct repaired history:

```text
Bronze  [2026-01-01, 2026-01-07)
Starter [2026-01-07, 2026-01-10)
Silver  [2026-01-10, 2026-01-20)
Gold    [2026-01-20, 9999-12-31)
```

For an affected customer, a robust repair can rebuild its effective-time sequence from authoritative history:

```sql
BEGIN;

DELETE FROM dim_customer
WHERE customer_id = 101;

INSERT INTO dim_customer (
    customer_id,
    segment,
    valid_from,
    valid_to,
    is_current
)
WITH ordered AS (
    SELECT
        customer_id,
        segment,
        effective_date,
        source_event_id,
        LEAD(effective_date) OVER (
            PARTITION BY customer_id
            ORDER BY effective_date, source_event_id
        ) AS next_effective_date,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY effective_date DESC, source_event_id DESC
        ) AS reverse_rank
    FROM authoritative_customer_history
    WHERE customer_id = 101
)
SELECT
    customer_id,
    segment,
    effective_date,
    COALESCE(
        next_effective_date,
        DATE '9999-12-31'
    ),
    reverse_rank = 1
FROM ordered;

COMMIT;
```

Point-in-time join:

```sql
SELECT
    f.order_id,
    f.event_time,
    d.segment
FROM fact_orders AS f
JOIN dim_customer AS d
  ON f.customer_id = d.customer_id
 AND f.event_time >= d.valid_from
 AND f.event_time < d.valid_to
WHERE f.order_id = 9001;
```

Expected:

```text
order 9001 → Starter
```

A current-state join:

```sql
SELECT
    f.order_id,
    d.segment
FROM fact_orders AS f
JOIN dim_customer AS d
  ON f.customer_id = d.customer_id
 AND d.is_current = true
WHERE f.order_id = 9001;
```

returns:

```text
Gold
```

### Common Wrong Approach

Appending the late Starter row without recalculating neighboring validity ranges.

### Production Note

Historical truth and current truth answer different analytical questions.

---

## Question 40 — Full Production Incremental Warehouse Pipeline

**Difficulty:** Advanced

**Primary topics:** full cumulative integration across Topics 01–10

**Integrated topics:** CTEs, joins, aggregation, windows, deduplication, EXCEPT, constraints, indexes, EXPLAIN, transactions, SKIP LOCKED, advisory locks, upsert, MERGE, SCD2, point-in-time joins, idempotency

### Problem

A subscription business receives a daily feed containing:

```text
customers
subscriptions
orders
delete/tombstone events
```

The system has:

```text
daily scheduled load
multiple workers
dashboard readers
large target tables
occasional schema changes
retries
duplicate source events
late-arriving customer changes
```

Requirements:

1. duplicate source records must be resolved deterministically;
2. NULL keys must be rejected;
3. unchanged records must not be rewritten;
4. target publication must be atomic;
5. only one logical daily job should run;
6. multiple workers should safely claim independent jobs;
7. customer segment history must be preserved;
8. orders must use customer segment valid at order time;
9. late historical changes must repair affected history;
10. the load must be replayable;
11. performance must be measured;
12. DDL should not wait indefinitely.

Design the pipeline and provide representative SQL for:

```text
staging
validation
deduplication
current-state upsert
worker claiming
SCD2
point-in-time join
reconciliation
idempotency
DDL timeout
```

### Solution

#### Step 1 — State the grains

```text
raw customer event:
one row per source event

resolved current customer change:
one authoritative row per customer for the current-state batch

customer_current:
one row per customer

dim_customer:
one row per customer version

fact_orders:
one row per order

job_queue:
one row per logical work item
```

#### Step 2 — Define stable identity

Prefer:

```text
customer_id
```

or a stable compound business key such as:

```text
(source_system, source_customer_id)
```

Do not use mutable email as identity unless the source contract says it is stable identity.

#### Step 3 — Stage

```sql
CREATE TEMP TABLE staging_customer_events (
    customer_id BIGINT,
    segment TEXT,
    effective_at TIMESTAMP,
    operation TEXT,
    source_event_id BIGINT,
    ingestion_id BIGINT
);
```

#### Step 4 — Validate

```sql
SELECT *
FROM staging_customer_events
WHERE customer_id IS NULL
   OR effective_at IS NULL;
```

Expected:

```text
0 rows
```

#### Step 5 — Deduplicate

For current-state reconciliation:

```sql
WITH ranked AS (
    SELECT
        s.*,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY
                effective_at DESC,
                source_event_id DESC,
                ingestion_id DESC
        ) AS rn
    FROM staging_customer_events AS s
)
SELECT *
FROM ranked
WHERE rn = 1;
```

For true historical CDC, do not collapse legitimately distinct effective-time events merely to simplify the query. The source contract determines the correct grain.

#### Step 6 — Singleton pipeline coordination

Use a stable advisory-lock convention:

```sql
SELECT pg_try_advisory_lock(12345);
```

Document:

```text
Job:
daily_customer_load

Key:
12345

Owner:
scheduler/worker

If already held:
skip or retry later

Invariant:
one logical daily run at a time

Hard correctness:
job-run uniqueness / constraints where possible
```

#### Step 7 — Multi-worker queue

```sql
BEGIN;

WITH next_jobs AS (
    SELECT job_id
    FROM job_queue
    WHERE status = 'ready'
    ORDER BY job_id
    FOR UPDATE SKIP LOCKED
    LIMIT 100
)
UPDATE job_queue AS j
SET status = 'running'
FROM next_jobs AS n
WHERE j.job_id = n.job_id
RETURNING j.job_id;

COMMIT;
```

The claim and state transition are atomic.

#### Step 8 — Current-state upsert

```sql
INSERT INTO customer_current (
    customer_id,
    segment
)
SELECT
    customer_id,
    segment
FROM resolved_customer_changes
WHERE operation <> 'DELETE'
ON CONFLICT (customer_id)
DO UPDATE
SET
    segment = EXCLUDED.segment
WHERE
    customer_current.segment IS DISTINCT FROM EXCLUDED.segment;
```

Explicit delete events are handled separately:

```sql
UPDATE customer_current AS c
SET
    is_deleted = true
FROM resolved_customer_changes AS s
WHERE c.customer_id = s.customer_id
  AND s.operation = 'DELETE';
```

#### Step 9 — SCD2 publication

For a simple current-to-new-version transition:

```sql
BEGIN;

UPDATE dim_customer AS d
SET
    valid_to = s.effective_at,
    is_current = false
FROM resolved_customer_changes AS s
WHERE d.customer_id = s.customer_id
  AND d.is_current = true
  AND d.segment IS DISTINCT FROM s.segment;

INSERT INTO dim_customer (
    customer_id,
    segment,
    valid_from,
    valid_to,
    is_current
)
SELECT
    s.customer_id,
    s.segment,
    s.effective_at,
    TIMESTAMP '9999-12-31',
    true
FROM resolved_customer_changes AS s
WHERE s.operation <> 'DELETE';

-- integrity assertions

COMMIT;
```

For late or multiple effective-time changes, rebuild/resequence affected customer history rather than blindly appending.

#### Step 10 — SCD2 assertions

Exactly one current row:

```sql
SELECT
    customer_id
FROM dim_customer
GROUP BY customer_id
HAVING COUNT(*) FILTER (WHERE is_current) <> 1;
```

Overlap:

```sql
WITH ordered AS (
    SELECT
        *,
        LAG(valid_to) OVER (
            PARTITION BY customer_id
            ORDER BY valid_from
        ) AS previous_valid_to
    FROM dim_customer
)
SELECT *
FROM ordered
WHERE previous_valid_to IS NOT NULL
  AND valid_from < previous_valid_to;
```

Gap:

```sql
WITH ordered AS (
    SELECT
        *,
        LAG(valid_to) OVER (
            PARTITION BY customer_id
            ORDER BY valid_from
        ) AS previous_valid_to
    FROM dim_customer
)
SELECT *
FROM ordered
WHERE previous_valid_to IS NOT NULL
  AND valid_from <> previous_valid_to;
```

#### Step 11 — Point-in-time order attribution

```sql
SELECT
    o.order_id,
    o.customer_id,
    o.order_time,
    d.segment
FROM fact_orders AS o
JOIN dim_customer AS d
  ON o.customer_id = d.customer_id
 AND o.order_time >= d.valid_from
 AND o.order_time < d.valid_to;
```

#### Step 12 — Reconciliation

Source-only customer keys:

```sql
SELECT customer_id
FROM resolved_customer_changes
WHERE operation <> 'DELETE'
EXCEPT
SELECT customer_id
FROM customer_current
WHERE is_deleted = false;
```

Target-only keys should be checked in the reverse direction when the source scope is authoritative.

Also compare:

```text
source row count
resolved row count
insert count
update count
delete count
distinct keys
partition counts
financial totals
```

#### Step 13 — Idempotency

Capture business state after run one:

```sql
CREATE TEMP TABLE first_state AS
SELECT
    customer_id,
    segment,
    is_deleted
FROM customer_current;
```

Run the identical batch again and compare bidirectionally:

```sql
(
    SELECT *
    FROM first_state
    EXCEPT
    SELECT
        customer_id,
        segment,
        is_deleted
    FROM customer_current
)
UNION ALL
(
    SELECT
        customer_id,
        segment,
        is_deleted
    FROM customer_current
    EXCEPT
    SELECT *
    FROM first_state
);
```

Expected:

```text
0 rows
```

#### Step 14 — Performance

Measure the large target with:

```sql
EXPLAIN (ANALYZE, BUFFERS)
...
```

Reason about:

```text
source reduction
target access path
merge-key index
partition pruning
changed fraction
unnecessary updates
transaction duration
```

#### Step 15 — DDL safety

Use:

```sql
BEGIN;

SET LOCAL lock_timeout = '2s';

ALTER TABLE customer_current
ADD COLUMN source_system TEXT;

COMMIT;
```

Use `statement_timeout` separately when execution itself must be bounded:

```sql
SET statement_timeout = '30s';
```

#### Step 16 — Retry behavior

Transient concurrency failure:

```text
ROLLBACK
→ backoff
→ retry whole transaction
```

Do not retry only the failed statement.

### Common Wrong Approach

Build the entire workflow as:

```text
download
→ parse
→ external API calls
→ dedupe
→ build history
→ publish
```

inside one giant database transaction.

### Why That Is Bad

It unnecessarily increases:

```text
transaction duration
lock duration
snapshot lifetime
rollback scope
operational risk
```

### Production Note

The correct architecture starts with:

```text
grain
→ identity
→ change semantics
→ delete semantics
→ history
→ transaction boundary
→ concurrency
→ validation
→ idempotency
→ performance
```

Only then choose:

```text
ON CONFLICT
MERGE
two-step SCD2
snapshot
```

---

# Final Coverage Check

The 40 questions intentionally distribute the curriculum progressively.

| Topic | Basic | Moderate | Hard | Advanced |
|---|---|---|---|---|
| 01 SELECT / NULL / time / pagination | Q01–Q03 | Q12, Q14, Q19 | Q21, Q24 | Q32, Q40 |
| 02 Joins / cardinality / explosion / anti-joins / LATERAL | Q04–Q05 | Q11–Q12 | Q22 | Q31, Q39, Q40 |
| 03 Aggregation / ratios / ROLLUP / weighted average | Q06 | Q11 | Q21, Q24 | Q31, Q40 |
| 04 Subqueries / CTE / recursion / date spine / materialization | Q07 | Q13–Q14 | Q25 | Q35, Q40 |
| 05 Windows / ranking / frames / LAG / islands / sessions | Q08–Q09 | Q15–Q17 | Q23 | Q35, Q38–Q40 |
| 06 Sets / dedupe / EXCEPT / reconciliation | Q09 | Q18 | Q30 | Q35–Q40 |
| 07 DDL / types / constraints / partitioning | Q10 | — | Q26 | Q40 |
| 08 Indexes / EXPLAIN / sargability | — | Q19 | Q27–Q28 | Q32, Q40 |
| 09 Transactions / isolation / MVCC / locks / queues | — | Q20 | Q29 | Q33–Q34, Q40 |
| 10 Upsert / MERGE / SCD / idempotency | Q10 | — | Q30 | Q35–Q40 |

### Required special cases

```text
NULL / three-valued logic          → Q01, Q05, Q12, Q21
NOT IN + NULL                     → Q12
Join explosion / fan trap         → Q11, Q31
Average-of-averages               → Q06
Recursive hierarchy               → Q13
Date spine                        → Q14
Window frame                       → Q15
Gaps and islands                   → Q16
Sessionisation                     → Q17
EXCEPT reconciliation              → Q18, Q37, Q40
Sargability                        → Q19, Q32
Lost update                        → Q20, Q33
Range join                         → Q22, Q39
LATERAL                            → Q22
ROW_NUMBER/RANK/DENSE_RANK         → Q08, Q23
ROLLUP/GROUPING                    → Q24
CTE materialization                → Q25
DDL/types/partitioning             → Q26
Composite/partial/expression index → Q27
EXPLAIN ANALYZE                    → Q19, Q28, Q32, Q40
Write skew                          → Q29
ON CONFLICT                        → Q10, Q30, Q35
MERGE                              → Q36
Tombstones/delete semantics        → Q30, Q36
Idempotency                        → Q37, Q40
SCD2 integrity                     → Q38
Late-arriving SCD2                 → Q39
Point-in-time join                 → Q22, Q39, Q40
SKIP LOCKED                        → Q34, Q40
Advisory locks                     → Q40
lock_timeout / statement_timeout   → Q40
```

---

# Final 40-Question Completion Checklist

## Basic Foundations

- [ ] I can write SELECT/WHERE/ORDER BY queries correctly.
- [ ] I understand SQL NULL and three-valued logic.
- [ ] I can write half-open time filters.
- [ ] I can explain deterministic ordering and tie-breakers.
- [ ] I can reason about basic join cardinality.
- [ ] I can write an anti-join safely.
- [ ] I can avoid the average-of-averages trap.
- [ ] I can use scalar subqueries and CTEs.
- [ ] I understand ranking ties.
- [ ] I can define keys and constraints before upsert.

## Analytical SQL

- [ ] I can preaggregate before a risky join.
- [ ] I can use NOT EXISTS when nullable membership is involved.
- [ ] I can write recursive CTEs with termination/cycle protection.
- [ ] I can build a date spine.
- [ ] I can select the correct window frame.
- [ ] I can solve gaps-and-islands.
- [ ] I can sessionise event data.
- [ ] I can reconcile tables with EXCEPT in both directions.
- [ ] I can diagnose a non-sargable predicate.
- [ ] I can prevent a lost update.

## Hard SQL

- [ ] I can calculate ratios from the correct numerator/denominator.
- [ ] I can perform effective-dated range joins.
- [ ] I can use LATERAL for per-row lookups.
- [ ] I can distinguish ROW_NUMBER, RANK, and DENSE_RANK.
- [ ] I can use ROLLUP and GROUPING correctly.
- [ ] I can reason about MATERIALIZED vs NOT MATERIALIZED.
- [ ] I can design a constrained, partitioned table.
- [ ] I can choose indexes based on workload.
- [ ] I can read a simulated EXPLAIN plan.
- [ ] I can reason about write skew and SERIALIZABLE.

## Advanced Production Skills

- [ ] I can diagnose a fan trap and repair the aggregation.
- [ ] I can tune a query using measure → plan → hypothesis → change → remeasure.
- [ ] I can separate visibility from blocking.
- [ ] I can build a safe SKIP LOCKED work queue.
- [ ] I can build a validated incremental upsert.
- [ ] I can deduplicate a MERGE source deterministically.
- [ ] I can handle delete/tombstone semantics.
- [ ] I can prove idempotency with state comparison.
- [ ] I can build and validate SCD2 history.
- [ ] I can repair a late-arriving SCD2 event.
- [ ] I can write a point-in-time fact-to-dimension join.
- [ ] I can design a production incremental warehouse workflow.

## Final Engineering Standard

Before considering a SQL problem finished, I should be able to answer:

```text
What is the grain?
What rows are included?
How many rows should come out?
What is the key?
What happens with NULL?
What happens with duplicates?
What happens with ties?
How do I validate correctness?
How could the query become slow?
How does it behave under rerun?
How does it behave under concurrency?
```

The goal is not merely:

> **"I can write SQL."**

The goal is:

> **"I can reason about data state, grain, correctness, performance, concurrency, idempotency, and historical accuracy, then express that reasoning in production-quality SQL."**
