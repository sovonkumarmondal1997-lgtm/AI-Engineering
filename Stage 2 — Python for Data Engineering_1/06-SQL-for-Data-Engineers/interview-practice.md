# SQL for Data Engineers — Interview Practice

## How to Use This Interview Practice

This is the cumulative interview-preparation set for **Module 2.6 — SQL for Data Engineers**. Questions 01–40 cover the learned Topics 01–10, with difficulty increasing from foundational SQL correctness to senior-level production pipeline architecture.

This is **interview practice, not a second copy of the hands-on practice set**. The goal is to make you explain assumptions, reason about grain and cardinality, write or defend SQL, diagnose failures, validate results, and discuss production behavior.

For every question, use this loop:

```text
Interview Problem
      ↓
Clarify assumptions
      ↓
Think aloud
      ↓
Solution / Answer
      ↓
Validate correctness
      ↓
Discuss edge cases
      ↓
Discuss performance / concurrency / reliability
      ↓
Give a concise verbal answer
```

Before coding, explicitly consider:

- **Grain:** “One row represents ______.”
- **Keys:** what identifies the entity or relationship?
- **Expected output:** how many rows should exist?
- **NULLs:** where can UNKNOWN or NULL-sensitive comparisons appear?
- **Duplicates:** what defines a duplicate and which survivor should win?
- **Ties:** does the business want all tied rows or exactly one?
- **Time:** what timezone and boundary semantics apply?
- **Validation:** what assertion or reconciliation check would prove correctness?

Use **standard SQL concepts first**, then label PostgreSQL or DuckDB behavior when the question is dialect-specific. The primary environments taught by this module are PostgreSQL 16+ and DuckDB.

### Difficulty Guide

- **Basic (Q01–Q10):** foundational correctness, core SQL, simple debugging, and small implementation.
- **Moderate (Q11–Q20):** combines several learned concepts and introduces production-oriented reasoning.
- **Hard (Q21–Q30):** realistic data-quality, performance, concurrency, and incremental-load problems.
- **Advanced (Q31–Q40):** senior Data Engineer scenarios that integrate multiple topics and require architecture-level reasoning.

### Interview Habit

Practice the answers aloud. For hard and advanced questions, give yourself roughly 5–20 minutes depending on the scope. Do not start with syntax. Start with the data model, grain, invariant, and failure mode.

# Part I — Basic

## Question 01 — Logical Query Order and Alias Visibility

**Difficulty:** Basic  
**Primary Topic(s):** SELECT, FROM, WHERE, GROUP BY, HAVING, SELECT aliases  
**Integrated Topic(s):** logical execution order, expressions, debugging

### Interview Problem

An interviewer shows you:

```sql
SELECT
    customer_id,
    amount * 1.18 AS gross_amount
FROM orders
WHERE gross_amount > 100;
```

Will this query work as written? Explain the logical order of SQL processing, then rewrite it correctly. Finally, explain why logical order does not require the database to physically execute every operator in exactly that order.

### What the Interviewer Is Testing

Whether you understand SQL as a logical transformation system rather than a line-by-line programming language.

### Candidate Clarification Questions

Before solving, clarify:

- Is the intended output grain one row per order?
- Is `gross_amount` a row-level expression or an aggregate?
- Is the question asking about SQL semantics or physical optimizer behavior?

### Recommended Thinking Process

1. Identify the row grain.
2. Find where `gross_amount` is defined.
3. Recall that `WHERE` is logically before `SELECT`.
4. Conclude that the alias is not available to `WHERE` in the same query block.
5. Move the expression into the predicate or create a new query boundary.
6. Separate logical semantics from the physical plan.

### Solution

Either repeat the expression:

```sql
SELECT
    customer_id,
    amount * 1.18 AS gross_amount
FROM orders
WHERE amount * 1.18 > 100;
```

or use a CTE:

```sql
WITH priced_orders AS (
    SELECT
        customer_id,
        amount * 1.18 AS gross_amount
    FROM orders
)
SELECT
    customer_id,
    gross_amount
FROM priced_orders
WHERE gross_amount > 100;
```

A useful logical-order model is:

```text
FROM
→ WHERE
→ GROUP BY
→ HAVING
→ window functions
→ SELECT
→ DISTINCT
→ ORDER BY
→ LIMIT
```

The optimizer may reorder or combine physical operations while preserving the logical result.

### Detailed Explanation

`gross_amount` is created by `SELECT`, but `WHERE` is logically evaluated earlier. A CTE or derived table creates a new relation in which the alias already exists as a column.

The distinction between **logical query processing** and **physical execution** matters later when reading `EXPLAIN`: the plan describes physical operators, not the pedagogical clause order above.

### Worked Example

If the input is:

```text
order_id | amount
---------+-------
1        | 80
2        | 100
```

then the gross amounts are 94.40 and 118.00. A `gross_amount > 100` filter keeps only order 2.

### Edge Cases

- `amount = NULL` makes the expression NULL, so the filter is not TRUE.
- Grouping or windowing can change the grain later.
- Repeating complex expressions can hurt readability; a CTE can create a clearer boundary.

### Common Wrong Approach

Reading SQL strictly top-to-bottom and assuming any `SELECT` alias is immediately available to `WHERE`.

### Production Considerations

For production SQL, make the grain and query stages explicit. Use `EXPLAIN` separately when you need to understand the physical access path or cost.

### Interviewer Follow-Up

1. Can the alias be used in `ORDER BY`?
2. What changes if you need `FETCH FIRST 100 ROWS ONLY`?

### Strong Interview Answer

A strong answer is: “`WHERE` is logically evaluated before `SELECT`, so the `gross_amount` alias is not available there. I would either repeat the expression or create a CTE/derived table. I would treat that logical model separately from the physical execution plan shown by `EXPLAIN`.”

## Question 02 — The NOT IN + NULL Trap

**Difficulty:** Basic  
**Primary Topic(s):** NULL, three-valued logic, IN, NOT IN  
**Integrated Topic(s):** anti-joins, NOT EXISTS, debugging

### Interview Problem

Consider:

```sql
CREATE TEMP TABLE customers (
    customer_id INTEGER PRIMARY KEY
);

INSERT INTO customers VALUES (1), (2), (3);

CREATE TEMP TABLE blocked_customers (
    customer_id INTEGER
);

INSERT INTO blocked_customers VALUES (2), (NULL);
```

A candidate writes:

```sql
SELECT customer_id
FROM customers
WHERE customer_id NOT IN (
    SELECT customer_id
    FROM blocked_customers
);
```

The result is empty. Explain why and write a production-safe version.

### What the Interviewer Is Testing

Whether you understand SQL's three-valued logic rather than treating NULL as an ordinary value.

### Candidate Clarification Questions

- Is NULL in the blocked list expected or a data-quality defect?
- Does the business question mean “no matching blocked row exists”?
- Is the outer key guaranteed non-NULL?

### Recommended Thinking Process

1. Expand the `NOT IN` predicate into equality comparisons.
2. Notice that comparison with NULL produces UNKNOWN.
3. Recall that `WHERE` keeps only TRUE.
4. Choose a relationship-oriented anti-join.
5. Validate the result at one-row-per-customer grain.

### Solution

Use `NOT EXISTS`:

```sql
SELECT c.customer_id
FROM customers AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM blocked_customers AS b
    WHERE b.customer_id = c.customer_id
);
```

Result:

```text
1
3
```

For customer 3, the logic behind the dangerous predicate is effectively:

```text
3 <> 2      → TRUE
3 <> NULL   → UNKNOWN
TRUE AND UNKNOWN → UNKNOWN
```

`WHERE` rejects UNKNOWN, so the row disappears.

### Detailed Explanation

SQL uses three truth values: TRUE, FALSE, and UNKNOWN. NULL is not an ordinary value, so `3 = NULL` is UNKNOWN rather than TRUE or FALSE.

`NOT EXISTS` asks a different question: “Is there no matching row?” Duplicate rows inside the subquery do not duplicate the outer customer.

### Worked Example

For customer 1:

```text
1 = 2      → FALSE
1 = NULL   → UNKNOWN
1 NOT IN (2, NULL) → UNKNOWN
```

For customer 2, one comparison is FALSE because of the match, but the NULL is still present in the overall membership test.

### Edge Cases

- An empty blocked table is different from one containing NULL.
- NULL outer keys need explicit business semantics.
- `col <> 'x'` also does not include NULL rows automatically.

### Common Wrong Approach

Adding `OR customer_id IS NULL` without understanding the predicate, or using `DISTINCT` to hide the issue.

### Production Considerations

Use `NOT EXISTS` when the requirement is an anti-relationship. If the blocking key is supposed to be non-NULL, enforce or test that invariant separately.

### Interviewer Follow-Up

1. Would duplicate blocked IDs duplicate the result?
2. What constraint would you add if blocked IDs are supposed to be a real key?

### Strong Interview Answer

“The issue is three-valued logic. A NULL inside `NOT IN` can turn the predicate into UNKNOWN, and `WHERE` keeps only TRUE. I would use `NOT EXISTS` for an anti-join because it directly expresses the relationship and avoids the nullable-subquery trap.”

## Question 03 — Time Filters, Pagination, and Deterministic Ordering

**Difficulty:** Basic  
**Primary Topic(s):** WHERE, ORDER BY, LIMIT/OFFSET/FETCH, timestamps  
**Integrated Topic(s):** BETWEEN, half-open ranges, CAST, integer division, sargability, keyset pagination

### Interview Problem

A daily ingestion job uses:

```sql
SELECT
    event_id,
    user_id,
    event_ts,
    amount
FROM events
WHERE event_ts BETWEEN TIMESTAMPTZ '2026-09-01 00:00:00+00'
                  AND TIMESTAMPTZ '2026-09-02 00:00:00+00'
ORDER BY event_ts
LIMIT 1000 OFFSET 2000;
```

Identify the correctness and scalability risks. Rewrite the daily filter and show a stable keyset-pagination pattern.

### What the Interviewer Is Testing

Whether you can combine timestamp semantics, deterministic ordering, sargability, and pagination into a production-safe extraction.

### Candidate Clarification Questions

- What timezone defines the batch day?
- Is `event_ts` a `timestamp` or `timestamptz`?
- Can multiple events share the same timestamp?
- Is the extraction restartable?

### Recommended Thinking Process

1. Define the batch as `[start, end)`.
2. Use `>= start AND < end`.
3. Add a unique tie-breaker to ordering.
4. Prefer keyset pagination for deep pages when a stable cursor exists.
5. Keep the timestamp predicate directly on the filtered column.

### Solution

Use a half-open time range:

```sql
SELECT
    event_id,
    user_id,
    event_ts,
    amount
FROM events
WHERE event_ts >= TIMESTAMPTZ '2026-09-01 00:00:00+00'
  AND event_ts <  TIMESTAMPTZ '2026-09-02 00:00:00+00'
ORDER BY event_ts, event_id
FETCH FIRST 1000 ROWS ONLY;
```

For the next page:

```sql
SELECT
    event_id,
    user_id,
    event_ts,
    amount
FROM events
WHERE event_ts >= :start_ts
  AND event_ts <  :end_ts
  AND (event_ts, event_id) > (:last_ts, :last_event_id)
ORDER BY event_ts, event_id
FETCH FIRST 1000 ROWS ONLY;
```

### Detailed Explanation

`BETWEEN` is inclusive at both ends. Adjacent daily ranges can therefore overlap on their boundary. Half-open ranges make batch partitioning clean:

```text
[start, end)
```

Ordering only by `event_ts` is not deterministic when timestamps tie. A unique `event_id` creates a total order and a stable keyset cursor.

For large offsets, the engine can spend increasing effort walking past earlier rows. Keyset pagination instead resumes from a known ordered key.

### Worked Example

An event exactly at `2026-09-02 00:00:00+00` belongs to the next batch, not both batches.

### Edge Cases

- NULL timestamps need an explicit policy.
- Late inserts can change OFFSET page contents.
- Timezone conversion must match business-day semantics.
- PostgreSQL integer division can truncate ratios unless a decimal type is introduced.

### Common Wrong Approach

Using `BETWEEN` for adjacent ETL windows and ordering only by a timestamp that is not unique.

### Production Considerations

Keep predicates sargable and test the access path with `EXPLAIN ANALYZE`. Keyset pagination is particularly useful for deep pages and repeatable batch extraction.

### Interviewer Follow-Up

1. What index would support this keyset query?
2. Why can `OFFSET 2,000,000` become expensive?
3. How would you write `5 / 2` if you need a decimal result in PostgreSQL?

### Strong Interview Answer

“I would define the batch as a half-open time interval, use a deterministic `(event_ts, event_id)` order, and prefer keyset pagination over deep offsets. I would preserve sargability and validate the access path with `EXPLAIN ANALYZE`.”

## Question 04 — Predict Join Cardinality Before Writing SQL

**Difficulty:** Basic  
**Primary Topic(s):** INNER/LEFT/RIGHT/FULL/CROSS JOIN, self-join, ON, USING  
**Integrated Topic(s):** grain, keys, 1:1, 1:N, N:1, N:M, NATURAL JOIN awareness

### Interview Problem

Given:

```text
customers
customer_id
-----------
1
2
3

orders
order_id | customer_id
---------+------------
101      | 1
102      | 1
103      | 2

payments
payment_id | order_id
-----------+---------
1001       | 101
1002       | 101
1003       | 103
```

Predict the row count of:

```sql
customers
JOIN orders ON customers.customer_id = orders.customer_id
JOIN payments ON orders.order_id = payments.order_id
```

Then explain INNER, LEFT, RIGHT, FULL OUTER, CROSS, and self-joins, and when `USING` is safe.

### What the Interviewer Is Testing

Whether you reason from grain and cardinality instead of memorizing join diagrams.

### Candidate Clarification Questions

- What is the grain of every table?
- Which columns are unique?
- Is the desired output customer, order, or payment grain?
- Must unmatched rows survive?

### Recommended Thinking Process

1. Customers to orders is 1:N.
2. Orders to payments is 1:N for order 101 and 1:0/1 for others.
3. INNER JOIN removes unmatched rows.
4. Compute the output row count before writing code.
5. Only then choose the join syntax.

### Solution

The first join produces three order rows. The second join removes order 102 because it has no payment, while order 101 produces two payment matches and order 103 produces one.

Final output row count: **3**.

Join meanings:

- `INNER JOIN`: keep matching combinations.
- `LEFT JOIN`: keep all left rows.
- `RIGHT JOIN`: keep all right rows.
- `FULL OUTER JOIN`: keep all rows from both sides.
- `CROSS JOIN`: Cartesian product.
- self-join: the same table participates twice under different aliases.

`USING(customer_id)` is appropriate when both sides deliberately share the same join-column name and the merged column semantics are wanted. `NATURAL JOIN` is risky because schema evolution can silently add columns to the join condition.

### Detailed Explanation

A join is a combination operation: each left row can match zero, one, or many right rows. A 1:N join is therefore not “one row becomes one row.”

This mental model is central to preventing join explosion and fan traps later in the module.

### Worked Example

Customer 1 has two orders. Order 101 has two payments. Therefore the customer row for customer 1 appears twice in the final relation.

### Edge Cases

- Duplicate supposed keys invalidate 1:1 or N:1 assumptions.
- NULL join keys do not match ordinary equality joins.
- N:M relationships can grow very quickly.
- A `LEFT JOIN` can behave like an inner filter if a right-side predicate is pushed into `WHERE`.

### Common Wrong Approach

Assuming a join should preserve the number of rows on the left or counting only distinct customers after the join and calling the join “correct.”

### Production Considerations

In code review, write down: “One row represents ___.” Then state the expected output row count and the uniqueness assumption for each join key.

### Interviewer Follow-Up

1. What would a deliberate `CROSS JOIN` use case look like?
2. When is a self-join useful?
3. Why is `NATURAL JOIN` dangerous in production?

### Strong Interview Answer

“I would define grain and key uniqueness before writing the join. Here customers are 1:N with orders and orders are 1:N with payments, so the final INNER JOIN returns three payment-level rows. Join type determines which unmatched rows survive; cardinality determines how many combinations each row can produce.”

## Question 05 — COUNT, NULLs, and the Average-of-Averages Trap

**Difficulty:** Basic  
**Primary Topic(s):** COUNT, SUM, AVG, MIN, MAX, GROUP BY, HAVING  
**Integrated Topic(s):** COUNT(*), COUNT(col), COUNT(DISTINCT), NULL handling, ratios, numeric precision

### Interview Problem

A report uses:

```sql
WITH store_metrics AS (
    SELECT
        store_id,
        AVG(order_amount) AS avg_order_amount
    FROM orders
    GROUP BY store_id
)
SELECT AVG(avg_order_amount)
FROM store_metrics;
```

The interviewer says the “overall average order value” is wrong because stores have different order counts. Explain the problem and give the correct metric. Also explain `COUNT(*)`, `COUNT(order_amount)`, and `COUNT(DISTINCT customer_id)`.

### What the Interviewer Is Testing

Whether you understand that `GROUP BY` changes grain and that mathematically plausible SQL can still be wrong.

### Candidate Clarification Questions

- Is the requested metric average per order or average per store?
- What does one row in the source represent?
- How should NULL order amounts behave?

### Recommended Thinking Process

1. State the mathematical definition of the metric.
2. Identify the grain of `store_metrics`.
3. Notice that every store gets equal weight in the second AVG.
4. Use raw-order aggregation or a weighted average.

### Solution

For average over orders:

```sql
SELECT AVG(order_amount) AS overall_aov
FROM orders;
```

If starting from store summaries:

```sql
WITH store_metrics AS (
    SELECT
        store_id,
        AVG(order_amount) AS store_avg,
        COUNT(order_amount) AS order_count
    FROM orders
    GROUP BY store_id
)
SELECT
    SUM(store_avg * order_count)
    / NULLIF(SUM(order_count), 0) AS overall_aov
FROM store_metrics;
```

Remember:

```text
COUNT(*)                    → rows
COUNT(order_amount)        → non-NULL order amounts
COUNT(DISTINCT customer_id)→ distinct non-NULL customers
```

### Detailed Explanation

Suppose one store has 100 orders averaging 10 and another has one order averaging 100. A simple average of store averages is 55, while the order-level average is about 10.89.

The difference is weighting. Aggregate metrics must preserve the intended numerator, denominator, and grain.

### Worked Example

```text
Store A: 100 orders × 10 = 1000
Store B:   1 order  × 100 = 100

True AOV = 1100 / 101 ≈ 10.89
Average of store averages = (10 + 100) / 2 = 55
```

### Edge Cases

- NULL amounts are ignored by AVG and COUNT(column).
- A group with no contributing rows may produce NULL.
- Replacing NULL with zero changes the business meaning if NULL means “unknown.”
- Integer division can truncate ratios.

### Common Wrong Approach

Applying `AVG()` to already-aggregated averages without weighting.

### Production Considerations

Write the metric definition before writing SQL. For money or other exact decimal measures, choose numeric types deliberately.

### Interviewer Follow-Up

1. When should `COUNT(DISTINCT customer_id)` replace `COUNT(*)`?
2. How would you prevent division by zero in a ratio metric?
3. What changes if the KPI is average spend per customer?

### Strong Interview Answer

“I first define the metric mathematically and state the grain. An average of group averages gives each group equal weight, which is wrong when group sizes differ. I would aggregate at order grain directly or use a weighted average based on the correct denominator.”

## Question 06 — EXISTS vs IN vs JOIN, and Scalar-Subquery Safety

**Difficulty:** Basic  
**Primary Topic(s):** subqueries, scalar subqueries, IN, EXISTS, JOIN, CTEs  
**Integrated Topic(s):** correlation, duplicates, NULL semantics, output grain

### Interview Problem

You need all customers who have at least one completed order. Compare:

```sql
SELECT c.customer_id
FROM customers c
JOIN orders o
  ON o.customer_id = c.customer_id
WHERE o.status = 'completed';
```

with:

```sql
SELECT c.customer_id
FROM customers c
WHERE c.customer_id IN (
    SELECT o.customer_id
    FROM orders o
    WHERE o.status = 'completed'
);
```

Explain why output multiplicity can differ, when `EXISTS` is clearer, and what can go wrong with a scalar subquery that returns more than one row.

### What the Interviewer Is Testing

Whether you understand the semantic difference between combining rows, membership, and existence.

### Candidate Clarification Questions

- Should one customer appear once or once per order?
- Can `orders.customer_id` repeat?
- Is the subquery key nullable?
- Is a scalar subquery guaranteed to be at most one row?

### Recommended Thinking Process

1. Desired grain is one row per customer.
2. JOIN can multiply a customer by matching orders.
3. IN and EXISTS preserve the outer row's multiplicity.
4. EXISTS directly expresses an existence requirement.
5. Scalar subqueries require a proof of cardinality.

### Solution

Use `EXISTS`:

```sql
SELECT c.customer_id
FROM customers AS c
WHERE EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.customer_id
      AND o.status = 'completed'
);
```

For a scalar value such as latest order amount, create a relation that is guaranteed to be one row per customer before selecting the scalar value.

### Detailed Explanation

If a customer has three completed orders, the JOIN returns three rows for that customer. EXISTS returns one because it answers a boolean relationship question.

A correlated scalar subquery that returns two matching rows is an error, not an arbitrary choice. An aggregate like `MAX()` or a deterministic window step can establish the needed one-row shape.

### Worked Example

```text
customer 10 → three completed orders
JOIN        → 3 rows
EXISTS      → 1 row
```

### Edge Cases

- `NOT IN` requires special care when NULL can exist.
- Correlated subqueries can be expensive depending on the workload.
- Optimizers may decorrelate a subquery into another physical shape.

### Common Wrong Approach

Using `JOIN + DISTINCT` for every existence question without first defining the desired grain.

### Production Considerations

Choose the construct whose semantics match the business question. If a correlated subquery is slow, inspect the plan before rewriting it as a join plus pre-aggregation.

### Interviewer Follow-Up

1. What happens when a scalar subquery returns zero rows?
2. Can an optimizer rewrite a correlated subquery?
3. How would you get latest order per customer using a window function?

### Strong Interview Answer

“I would state the output grain first. If the question is ‘does a related row exist?’, `EXISTS` is the clearest choice and avoids join multiplication. Scalar subqueries must be proven to return at most one row.”

## Question 07 — ROW_NUMBER vs RANK vs DENSE_RANK on Ties

**Difficulty:** Basic  
**Primary Topic(s):** window functions, OVER, PARTITION BY, ORDER BY  
**Integrated Topic(s):** ROW_NUMBER, RANK, DENSE_RANK, NTILE, PERCENT_RANK, CUME_DIST

### Interview Problem

Given:

```text
product | revenue
--------+--------
A       | 100
B       | 100
C       | 90
D       | 80
```

Explain what `ROW_NUMBER`, `RANK`, and `DENSE_RANK` return when ordered by revenue descending. Then answer two business questions:

1. Return exactly three rows.
2. Return every product tied for the third position.

Finally, explain the purpose of `NTILE`, `PERCENT_RANK`, and `CUME_DIST`.

### What the Interviewer Is Testing

Whether you understand ranking semantics and tie behavior.

### Candidate Clarification Questions

- Does “top 3” mean three rows or three rank positions?
- Should ties be preserved?
- Is the partition per country or global?
- Do we need deterministic ordering for single survivors?

### Recommended Thinking Process

1. Keep one row per product.
2. Compare the three ranking functions.
3. Choose based on business semantics.
4. Add a tie-breaker only when you actually want peers separated.

### Solution

```sql
SELECT
    product,
    revenue,
    ROW_NUMBER() OVER (ORDER BY revenue DESC) AS rn,
    RANK()       OVER (ORDER BY revenue DESC) AS rnk,
    DENSE_RANK() OVER (ORDER BY revenue DESC) AS drnk
FROM product_revenue;
```

The result is:

```text
product | revenue | rn | rnk | drnk
--------+---------+----+-----+-----
A       | 100     | 1  | 1   | 1
B       | 100     | 2  | 1   | 1
C       | 90      | 3  | 3   | 2
D       | 80      | 4  | 4   | 3
```

- Exactly three rows: `ROW_NUMBER() <= 3`.
- Every product tied at the third position: `RANK() <= 3`.

`NTILE(k)` creates k buckets, `PERCENT_RANK` expresses relative rank, and `CUME_DIST` gives the cumulative proportion through the current peer group.

### Detailed Explanation

`ROW_NUMBER` always generates unique sequence positions, so it is appropriate when exactly one row per position is required. `RANK` preserves ties and leaves gaps. `DENSE_RANK` preserves ties without leaving gaps.

Adding `product_id` as a tie-breaker to the ranking ORDER BY changes peer semantics for `RANK` and `DENSE_RANK`, so do that only when the business meaning actually calls for distinct ordering.

### Worked Example

Two rows tied at 100 get rank 1. The next revenue of 90 gets rank 3 under `RANK` but rank 2 under `DENSE_RANK`.

### Edge Cases

- NULL ordering requires an explicit policy.
- `ROW_NUMBER` without a unique tie-breaker is not deterministic.
- `NTILE` creates equal-ish row counts, not equal metric ranges.

### Common Wrong Approach

Using `ROW_NUMBER` automatically for every “top 3” requirement.

### Production Considerations

State whether top-N means N rows or N rank positions. This distinction is a frequent source of subtle reporting bugs.

### Interviewer Follow-Up

1. How would you return top 3 products per country?
2. Which function is appropriate for deterministic latest-record deduplication?
3. How would `QUALIFY` help in DuckDB?

### Strong Interview Answer

“`ROW_NUMBER` gives unique positions, `RANK` preserves ties with gaps, and `DENSE_RANK` preserves ties without gaps. I choose the function from the business definition of top-N, and I add a tie-breaker when I need one deterministic survivor.”

## Question 08 — Deterministic Deduplication with a Survivor Rule

**Difficulty:** Basic  
**Primary Topic(s):** ROW_NUMBER, duplicate detection, latest-record pattern  
**Integrated Topic(s):** source priority, completeness, tie-breakers, DISTINCT ON awareness

### Interview Problem

A staging table contains multiple rows for one `customer_id`. The business rule is:

1. CRM beats ERP.
2. Newest `updated_at` wins.
3. Non-NULL email beats NULL email.
4. Highest `ingestion_id` breaks any remaining tie.

Write a deterministic query that returns one survivor per `customer_id`.

### What the Interviewer Is Testing

Whether you can translate business survivor policy into deterministic SQL.

### Candidate Clarification Questions

- What is the business key?
- Which timestamp is authoritative?
- Can timestamps tie?
- Is `ingestion_id` unique?

### Recommended Thinking Process

1. Define target grain: one row per customer.
2. Translate each business rule into an ordered criterion.
3. Rank within each business key.
4. Keep `rn = 1`.
5. Assert the output has no duplicate business keys.

### Solution

```sql
WITH ranked AS (
    SELECT
        s.*,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY
                CASE WHEN source = 'CRM' THEN 1 ELSE 0 END DESC,
                updated_at DESC NULLS LAST,
                CASE WHEN email IS NOT NULL THEN 1 ELSE 0 END DESC,
                ingestion_id DESC
        ) AS rn
    FROM staging_customers AS s
)
SELECT
    customer_id,
    source,
    updated_at,
    email,
    ingestion_id
FROM ranked
WHERE rn = 1;
```

### Detailed Explanation

The critical idea is not merely “use `ROW_NUMBER`.” It is “define a complete deterministic ordering.” A business-key duplicate can contain different values, so `DISTINCT` cannot decide which row is authoritative.

PostgreSQL `DISTINCT ON` can express a similar pattern, while DuckDB can often use `QUALIFY` to filter the window result directly.

### Worked Example

If two CRM rows tie on timestamp, the non-NULL email is preferred. If they still tie, the larger `ingestion_id` wins.

### Edge Cases

- NULL timestamps need deliberate ordering.
- A missing final tie-breaker leaves nondeterminism.
- Duplicate business keys may indicate upstream data-quality failure even if a survivor can be chosen.

### Common Wrong Approach

Using `SELECT DISTINCT` and assuming it means “pick the best row.”

### Production Considerations

Add a zero-row assertion:

```sql
SELECT customer_id
FROM deduped
GROUP BY customer_id
HAVING COUNT(*) > 1;
```

The query should return zero rows.

### Interviewer Follow-Up

1. Why is `RANK()` not enough for exactly one survivor?
2. What if two rows still tie after all business criteria?
3. How would you safely delete victims?

### Strong Interview Answer

“I define the business key and target grain first. Then I encode the survivor policy as a complete ordering inside `ROW_NUMBER`, keep `rn = 1`, and assert that the deduped result contains at most one row per business key.”

## Question 09 — Design a Table with Correct Types and Constraints

**Difficulty:** Basic  
**Primary Topic(s):** CREATE TABLE, data types, PRIMARY KEY, UNIQUE, NOT NULL  
**Integrated Topic(s):** NUMERIC, BIGINT, TIMESTAMPTZ, identity, foreign key, CHECK, DEFAULT

### Interview Problem

Design a PostgreSQL `subscriptions` table with:

```text
subscription_id
customer_id
plan_code
price
status
started_at
cancelled_at
```

Requirements:

- one row per subscription;
- database-generated ID;
- exact cents for price;
- required customer reference;
- known set of status values;
- `started_at` is an instant;
- cancellation is optional.

Explain the types and constraints.

### What the Interviewer Is Testing

Whether you treat a schema as an executable data-quality contract.

### Candidate Clarification Questions

- Can one customer have multiple subscriptions?
- Is `subscription_id` a surrogate key?
- What statuses are valid?
- Is `started_at` an instant or timezone-less wall-clock time?

### Recommended Thinking Process

1. State the grain.
2. Choose the primary key.
3. Choose exact numeric semantics.
4. Make required values `NOT NULL`.
5. Add FK and CHECK constraints for real invariants.
6. Use `TIMESTAMPTZ` for an instant.

### Solution

```sql
CREATE TABLE subscriptions (
    subscription_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id BIGINT NOT NULL
        REFERENCES customers(customer_id),
    plan_code TEXT NOT NULL,
    price NUMERIC(12, 2) NOT NULL
        CHECK (price >= 0),
    status TEXT NOT NULL
        CHECK (status IN ('trial', 'active', 'cancelled')),
    started_at TIMESTAMPTZ NOT NULL,
    cancelled_at TIMESTAMPTZ
);
```

### Detailed Explanation

`NUMERIC(12,2)` gives exact decimal semantics appropriate for monetary values. `TIMESTAMPTZ` represents an instant. The identity column gives a stable generated surrogate key.

`PRIMARY KEY`, `NOT NULL`, `CHECK`, and `FOREIGN KEY` constraints move business invariants into the database.

### Worked Example

A row with `status = 'paused'` fails the CHECK constraint. A NULL customer ID fails `NOT NULL`. A non-existing customer fails the foreign key.

### Edge Cases

- Optional unique identifiers need explicit NULL semantics.
- Existing dirty data can make adding a constraint fail.
- `INTEGER` may be insufficient for identifiers expected to grow substantially.

### Common Wrong Approach

Using `DOUBLE PRECISION` for exact currency or storing timestamps as strings.

### Production Considerations

Schema changes on large tables can create locks or rewrites. Plan migrations with expand-and-contract awareness when necessary.

### Interviewer Follow-Up

1. When would you choose UUID instead of an integer identity?
2. What does PostgreSQL `UNIQUE NULLS NOT DISTINCT` solve?
3. What migration risk can arise when adding constraints to an existing table?

### Strong Interview Answer

“I start from grain, then key, then types, then constraints. Money needs exact decimal semantics, event instants need timezone-aware timestamps, and the schema should reject invalid states instead of relying only on application code.”

## Question 10 — A NULL-Safe, Change-Only Upsert

**Difficulty:** Basic  
**Primary Topic(s):** INSERT ... ON CONFLICT, unique constraints, EXCLUDED  
**Integrated Topic(s):** IS DISTINCT FROM, idempotency, unnecessary writes

### Interview Problem

You have:

```sql
CREATE TABLE product_state (
    product_id BIGINT PRIMARY KEY,
    name TEXT,
    price NUMERIC(12, 2),
    is_active BOOLEAN NOT NULL
);
```

Write a PostgreSQL upsert that inserts new products, updates changed products, treats NULL-to-value and value-to-NULL as changes, and does not rewrite unchanged rows.

### What the Interviewer Is Testing

Whether you understand NULL-safe change detection and idempotent state updates.

### Candidate Clarification Questions

- Is the source already one row per `product_id`?
- Are NULLs meaningful values?
- Should unchanged rows update audit columns?

### Recommended Thinking Process

1. Require a real uniqueness definition.
2. Use the unique key as conflict target.
3. Compare nullable attributes with `IS DISTINCT FROM`.
4. Put the change condition on the update branch.

### Solution

```sql
INSERT INTO product_state (
    product_id,
    name,
    price,
    is_active
)
SELECT
    product_id,
    name,
    price,
    is_active
FROM staged_products
ON CONFLICT (product_id)
DO UPDATE SET
    name = EXCLUDED.name,
    price = EXCLUDED.price,
    is_active = EXCLUDED.is_active
WHERE product_state.name IS DISTINCT FROM EXCLUDED.name
   OR product_state.price IS DISTINCT FROM EXCLUDED.price
   OR product_state.is_active IS DISTINCT FROM EXCLUDED.is_active;
```

### Detailed Explanation

`EXCLUDED` refers to the incoming row. `IS DISTINCT FROM` treats two NULLs as not distinct and a NULL versus a non-NULL value as distinct.

That gives change detection like:

```text
NULL → 'A'   = changed
'A'  → NULL  = changed
NULL → NULL  = unchanged
```

The conditional update also avoids unnecessary writes.

### Worked Example

If the target has `price = 10.00` and the incoming row has `price = NULL`, the condition is TRUE and the row changes. Replaying the same input causes no logical update.

### Edge Cases

- Duplicate source keys remain a separate staging problem.
- Audit columns can make every row appear changed if included in the comparison.
- String normalization rules may need to be applied before comparison.

### Common Wrong Approach

Using `product_state.price <> EXCLUDED.price` for nullable fields.

### Production Considerations

Change-only updates reduce write amplification and can reduce lock duration, WAL, and maintenance work.

### Interviewer Follow-Up

1. How would a tombstone be represented?
2. What makes this idempotent?
3. What schema object makes the conflict target valid?

### Strong Interview Answer

“I need a real uniqueness definition first. Then I compare only business attributes with `IS DISTINCT FROM`. New keys insert, changed keys update, and unchanged keys do nothing, so replaying the same input is safe.”

# Part II — Moderate

## Question 11 — Debug a LEFT JOIN That Behaves Like an INNER JOIN

**Difficulty:** Moderate  
**Primary Topic(s):** LEFT JOIN, WHERE, EXISTS, anti/semi-joins  
**Integrated Topic(s):** NULL semantics, join grain, debugging

### Interview Problem

You need every customer with completed-order revenue, including customers with none. A candidate writes:

```sql
SELECT
    c.customer_id,
    COALESCE(SUM(o.amount), 0) AS completed_revenue
FROM customers c
LEFT JOIN orders o
  ON o.customer_id = c.customer_id
WHERE o.status = 'completed'
GROUP BY c.customer_id;
```

Customers without completed orders disappear. Diagnose and fix it.

### What the Interviewer Is Testing

Whether you understand the `LEFT JOIN` + `WHERE` trap.

### Candidate Clarification Questions

- Must every customer survive?
- Does “completed” define matching rows or final filtering?
- Should no completed revenue be represented as zero?

### Recommended Thinking Process

1. Left side defines the required output grain.
2. Unmatched right columns become NULL.
3. The `WHERE` predicate rejects those NULL-extended rows.
4. Move the right-side filter into `ON`.

### Solution

```sql
SELECT
    c.customer_id,
    COALESCE(SUM(o.amount), 0) AS completed_revenue
FROM customers AS c
LEFT JOIN orders AS o
  ON o.customer_id = c.customer_id
 AND o.status = 'completed'
GROUP BY c.customer_id;
```

For “customers with no completed orders,” use:

```sql
SELECT c.customer_id
FROM customers AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.customer_id
      AND o.status = 'completed'
);
```

### Detailed Explanation

A LEFT JOIN preserves the left row only until a later predicate removes it. In the original query, an unmatched customer has `o.status = NULL`; `NULL = 'completed'` is UNKNOWN, so `WHERE` removes the row.

### Worked Example

Customer 3 has no matching order, so the joined row is effectively:

```text
customer_id = 3, status = NULL
```

The broken `WHERE` removes it. The corrected `ON` keeps it and lets `COALESCE` map missing revenue to zero.

### Edge Cases

- Multiple orders still multiply rows at order grain.
- NULL amounts are not automatically zero.
- Ratios need explicit denominator logic.

### Common Wrong Approach

Adding `DISTINCT` to “bring customers back.” It does not fix the semantic loss or any duplicated measures.

### Production Considerations

Review every right-side filter in a LEFT JOIN and ask whether it defines the relationship or the final result set.

### Interviewer Follow-Up

1. How would you write customers with no completed orders?
2. What happens if `orders.amount` is NULL?
3. How would duplicate order keys affect the revenue sum?

### Strong Interview Answer

“The LEFT JOIN is being undone by the `WHERE` predicate. Unmatched customers have NULL right-side values, so the status comparison becomes UNKNOWN. I would move the status predicate into `ON`, then aggregate at customer grain.”

## Question 12 — Build a Date Spine for Missing-Date Reporting

**Difficulty:** Moderate  
**Primary Topic(s):** generate_series, CTEs, LEFT JOIN, aggregation  
**Integrated Topic(s):** missing dates, zero vs NULL, date arithmetic

### Interview Problem

Produce daily order counts for September 1–7 even when a day has no orders.

### What the Interviewer Is Testing

Whether you understand that missing periods are missing rows and must be created explicitly.

### Candidate Clarification Questions

- What timezone defines the reporting day?
- Is the endpoint inclusive?
- Should an empty day show 0 or NULL?

### Recommended Thinking Process

1. Generate the complete date domain.
2. Aggregate facts to daily grain.
3. LEFT JOIN facts to the domain.
4. `COALESCE` the count where “no rows” means zero.

### Solution

```sql
WITH date_spine AS (
    SELECT day::date AS order_date
    FROM generate_series(
        DATE '2026-09-01',
        DATE '2026-09-07',
        INTERVAL '1 day'
    ) AS g(day)
),
daily_orders AS (
    SELECT
        order_ts::date AS order_date,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY order_ts::date
)
SELECT
    d.order_date,
    COALESCE(o.order_count, 0) AS order_count
FROM date_spine d
LEFT JOIN daily_orders o
  ON o.order_date = d.order_date
ORDER BY d.order_date;
```

### Detailed Explanation

A normal `GROUP BY` only returns groups that exist. There is no row for a date with no facts. The date spine supplies the missing members of the reporting domain first.

### Worked Example

If facts exist only on Sep 1 and Sep 3, the final result still has all seven dates; Sep 2 receives a zero count.

### Edge Cases

- Empty source table still returns the full date range.
- Timezone conversions can move events across reporting days.
- A nullable right-side key should be handled carefully when counting matched rows.

### Common Wrong Approach

Trying to make `GROUP BY order_ts::date` produce missing dates automatically.

### Production Considerations

Keep the date-spine CTE separate from fact aggregation so each stage has a clear grain. This pattern also supports customer-by-day and cohort reporting.

### Interviewer Follow-Up

1. Could a recursive CTE generate the same calendar?
2. How would you create a month-by-month customer grid?
3. What changes if reporting days are Asia/Kolkata but timestamps are stored as UTC instants?

### Strong Interview Answer

“A missing day is a missing row, not a NULL value in an existing row. I would generate the full date domain, aggregate facts separately, left join the two, and use `COALESCE` only where the business meaning of no facts is zero.”

## Question 13 — Running Totals, LAG/LEAD, and the LAST_VALUE Trap

**Difficulty:** Moderate  
**Primary Topic(s):** window functions, LAG, LEAD, SUM OVER  
**Integrated Topic(s):** ROWS/RANGE/GROUPS, moving averages, FIRST_VALUE/LAST_VALUE/NTH_VALUE, named windows

### Interview Problem

An analyst writes:

```sql
SELECT
    customer_id,
    order_id,
    order_ts,
    amount,
    SUM(amount) OVER (
        PARTITION BY customer_id
        ORDER BY order_ts
    ) AS running_total,
    LAST_VALUE(amount) OVER (
        PARTITION BY customer_id
        ORDER BY order_ts
    ) AS final_amount
FROM orders;
```

They expect `final_amount` to be the customer's last order amount on every row. Diagnose the problem and show a corrected query that also calculates time since the previous order.

### What the Interviewer Is Testing

Whether you understand window frames rather than treating `ORDER BY` as sufficient for every window calculation.

### Candidate Clarification Questions

- Can `order_ts` tie?
- Should the running total be row-based?
- Does “last value” mean last value in the frame or last row in the partition?

### Recommended Thinking Process

1. Add deterministic ordering with `order_ts, order_id`.
2. Choose explicit frames.
3. Use a full-partition frame for a true final value.
4. Use `LAG` for prior-row comparison.

### Solution

```sql
SELECT
    customer_id,
    order_id,
    order_ts,
    amount,
    SUM(amount) OVER (
        PARTITION BY customer_id
        ORDER BY order_ts, order_id
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total,
    LAST_VALUE(amount) OVER (
        PARTITION BY customer_id
        ORDER BY order_ts, order_id
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS final_amount,
    order_ts
      - LAG(order_ts) OVER (
            PARTITION BY customer_id
            ORDER BY order_ts, order_id
        ) AS time_since_previous
FROM orders;
```

### Detailed Explanation

The default frame for an ordered window does not necessarily mean “the whole partition.” `LAST_VALUE` therefore often returns the value at the end of the current frame, which can be the current row or peer group rather than the final row in the partition.

Frame types matter:

- `ROWS` counts ordered rows.
- `RANGE` groups peer rows by ordering value and can support time-oriented frames in supported forms.
- `GROUPS` advances by peer groups.

A named window can improve readability when specifications are shared, but multiple different window definitions can also require multiple sorts.

### Worked Example

For amounts 10, 20, 30, the desired final amount is 30 on all rows. Without the full-partition frame, `LAST_VALUE` can return 10, then 20, then 30.

### Edge Cases

- Equal timestamps require a tie-breaker.
- `ROWS 6 PRECEDING` means up to seven rows, not seven calendar days.
- `LAG` returns NULL for the first row unless a default is provided.

### Common Wrong Approach

Using `LAST_VALUE` without an explicit frame and assuming it means “last row in partition.”

### Production Considerations

Treat the window frame as part of the metric definition. For large datasets, minimize unnecessary independent window sorts.

### Interviewer Follow-Up

1. When would `RANGE` be preferable to `ROWS`?
2. How would you filter to the latest record per customer?
3. What does `LEAD(amount, 1, 0)` do for the final row?

### Strong Interview Answer

“I would make the ordering deterministic, define the frame explicitly, and use `LAG` for prior-row comparisons. `LAST_VALUE` needs a full-partition frame when the business question is truly the final value for the whole partition.”

## Question 14 — Source-to-Target Reconciliation with Set Operations

**Difficulty:** Moderate  
**Primary Topic(s):** UNION, UNION ALL, INTERSECT, EXCEPT  
**Integrated Topic(s):** reconciliation, missing/extra/changed rows, NULL behavior, schema alignment

### Interview Problem

After a warehouse load, compare `staging_customers` and `warehouse_customers` to detect:

1. keys missing from the target;
2. keys extra in the target;
3. changed attributes for keys that exist in both.

Explain when you would use `UNION ALL`, `INTERSECT`, and `EXCEPT`, and write the reconciliation pattern.

### What the Interviewer Is Testing

Whether you can use set operations as a correctness and reconciliation tool rather than only for report composition.

### Candidate Clarification Questions

- What is the target grain?
- Are duplicates allowed?
- Which columns define equality?
- Are the schemas aligned by position?

### Recommended Thinking Process

1. Compare business-key sets.
2. Use `EXCEPT` in both directions for missing and extra rows.
3. Join on the key for changed attributes.
4. Use NULL-safe comparison.

### Solution

```sql
-- Missing in target
SELECT customer_id, email, status
FROM staging_customers
EXCEPT
SELECT customer_id, email, status
FROM warehouse_customers;
```

```sql
-- Extra in target
SELECT customer_id, email, status
FROM warehouse_customers
EXCEPT
SELECT customer_id, email, status
FROM staging_customers;
```

```sql
-- Changed attributes
SELECT s.customer_id
FROM staging_customers s
JOIN warehouse_customers t
  ON t.customer_id = s.customer_id
WHERE s.email  IS DISTINCT FROM t.email
   OR s.status IS DISTINCT FROM t.status;
```

`UNION ALL` preserves duplicates; `UNION` removes duplicate rows; `INTERSECT` finds rows present in both; `EXCEPT` finds rows in the first result not present in the second.

### Detailed Explanation

Set operations compare row sets. Changed rows are different complete rows, so a keyed comparison is better for identifying which business entity changed.

Columns in set operations match by position, so explicit column lists are safer. DuckDB's `UNION BY NAME` can be useful when schema alignment by name is intended.

### Worked Example

If customer 10 exists in both datasets but the email differs, the two-direction `EXCEPT` checks show row differences, while the keyed join identifies customer 10 as changed.

### Edge Cases

- Duplicate rows and business-key duplicates are different concepts.
- NULL has special behavior in ordinary predicates versus set operations.
- Large reconciliation scans may need partition-level checks.

### Common Wrong Approach

Comparing only total row counts and assuming equality.

### Production Considerations

Use row counts, distinct-key counts, missing/extra keys, and financial totals as complementary reconciliation evidence.

### Interviewer Follow-Up

1. How would you align schemas with different column order?
2. How would you prove a second load changes nothing?
3. When can set-operation reconciliation become expensive?

### Strong Interview Answer

“I use `EXCEPT` in both directions to detect missing and extra rows, then compare shared business keys with `IS DISTINCT FROM` to detect changes. Counts and partition-level totals are additional evidence, not substitutes for row-level reconciliation.”

## Question 15 — CTE Pipelines and Materialization Choices

**Difficulty:** Moderate  
**Primary Topic(s):** CTEs, derived tables, subqueries  
**Integrated Topic(s):** MATERIALIZED, NOT MATERIALIZED, temp tables, views, materialized views

### Interview Problem

A transformation has these stages:

```text
raw events
→ filter valid rows
→ deterministic deduplication
→ aggregate by customer
→ enrich with customer attributes
```

The SQL is a deeply nested single SELECT. Refactor it into a CTE chain and explain the practical distinction between a CTE, temporary table, view, and materialized view. When might PostgreSQL `MATERIALIZED` or `NOT MATERIALIZED` be considered?

### What the Interviewer Is Testing

Whether you can decompose SQL into explicit, reviewable, testable stages without confusing logical structure with physical persistence.

### Candidate Clarification Questions

- What is the grain after each step?
- Is the dedup deterministic?
- Is an intermediate relation reused?
- Does the transformation span one statement or several?

### Recommended Thinking Process

1. Give every CTE a purpose and grain.
2. Filter early when semantically safe.
3. Deduplicate before aggregation if necessary.
4. Treat the CTE as a logical query boundary, not automatically a stored table.
5. Use materialization intentionally and verify with plans.

### Solution

```sql
WITH valid_events AS (
    SELECT *
    FROM raw_events
    WHERE event_type IS NOT NULL
),
ranked AS (
    SELECT
        e.*,
        ROW_NUMBER() OVER (
            PARTITION BY business_key
            ORDER BY event_ts DESC, ingestion_id DESC
        ) AS rn
    FROM valid_events e
),
deduped AS (
    SELECT *
    FROM ranked
    WHERE rn = 1
),
customer_totals AS (
    SELECT
        customer_id,
        SUM(amount) AS total_amount
    FROM deduped
    GROUP BY customer_id
)
SELECT
    c.customer_id,
    ct.total_amount
FROM customers c
LEFT JOIN customer_totals ct
  ON ct.customer_id = c.customer_id;
```

In PostgreSQL, `MATERIALIZED` can force materialization and `NOT MATERIALIZED` can request inlining when eligible. A temporary table is an actual session-scoped relation. A view stores a query definition. A materialized view stores query results and has refresh semantics.

### Detailed Explanation

CTEs improve transformation reasoning because each stage can have a clear grain and invariant. They are not automatically temporary tables.

Choose a temporary table when the intermediate relation must survive across statements or benefit from its own indexes. Choose a view for reusable logical access and a materialized view when persisted query results make sense.

### Worked Example

If `deduped` is supposed to be one row per business key, this assertion should return zero rows:

```sql
SELECT business_key
FROM deduped
GROUP BY business_key
HAVING COUNT(*) > 1;
```

### Edge Cases

- Every CTE is not automatically an optimization barrier.
- Forced materialization can create unnecessary work.
- A skipped dedup stage can create downstream metric multiplication.

### Common Wrong Approach

Treating CTEs as guaranteed performance barriers and adding `MATERIALIZED` everywhere.

### Production Considerations

Choose materialization based on measured reuse and plan behavior. Keep CTE names semantic and testable.

### Interviewer Follow-Up

1. When would a temporary table be better than a CTE?
2. Could a view solve the readability problem?
3. Why might `NOT MATERIALIZED` help?

### Strong Interview Answer

“I use CTEs to make the transformation pipeline explicit and track grain at every stage. A CTE is primarily a logical construct; physical materialization is a deliberate performance choice that I would validate with the query plan.”

## Question 16 — Production Schema Review: Types, Constraints, Nested Data, and Partitioning

**Difficulty:** Moderate  
**Primary Topic(s):** DDL, data types, constraints, partitioning  
**Integrated Topic(s):** JSONB, arrays, DuckDB nested types, generated columns, views, migrations

### Interview Problem

Review this proposed event table:

```text
event_id        TEXT
customer_id     INT
event_type      VARCHAR(500)
price           DOUBLE PRECISION
event_time      TIMESTAMP
tags            TEXT
payload         TEXT
created_date    DATE
```

The table receives millions of append-oriented events and is queried mainly by time range with occasional payload inspection. Defend a better PostgreSQL-oriented schema design and discuss JSONB/arrays, partitioning, generated columns, and safe schema evolution.

### What the Interviewer Is Testing

Whether you can choose types and structural features from semantics and workload rather than convenience.

### Candidate Clarification Questions

- Is `event_id` globally unique?
- Is `event_time` an instant?
- Is `price` exact or approximate?
- Are payload fields frequently queried?
- Does the time range dominate access patterns?

### Recommended Thinking Process

1. Define event grain and identity.
2. Choose types from meaning.
3. Add constraints for true invariants.
4. Separate relational attributes from nested payload.
5. Partition only for a justified time-based workload.
6. Plan risky schema changes around locking/rewrite behavior.

### Solution

A reasonable design is:

```sql
CREATE TABLE events (
    event_id UUID PRIMARY KEY,
    customer_id BIGINT,
    event_type TEXT NOT NULL,
    price NUMERIC(12, 2),
    event_time TIMESTAMPTZ NOT NULL,
    tags TEXT[],
    payload JSONB,
    event_date DATE GENERATED ALWAYS AS
        ((event_time AT TIME ZONE 'UTC')::date) STORED
) PARTITION BY RANGE (event_time);
```

The exact schema depends on business semantics. DuckDB offers nested types such as `STRUCT`, `LIST`, and `MAP` where those are the appropriate representation.

### Detailed Explanation

`NUMERIC` is appropriate when exact decimal semantics matter. `TIMESTAMPTZ` is suitable for instants. `BIGINT` provides more identifier headroom than small integer types.

JSONB and nested types are useful when nested structure is genuinely part of the source model. Frequently queried business fields may deserve first-class relational columns.

Partitioning can support partition pruning for time-window access. It should not be added simply because the table is large.

### Worked Example

A query for one day can prune unrelated time partitions when the partition key and predicate align. If a payload field becomes a high-frequency filter, promoting it to a regular column may improve clarity and access-path options.

### Edge Cases

- Existing dirty data can block new constraints.
- Schema changes can take locks or rewrite data.
- Semi-structured columns can become a dumping ground.

### Common Wrong Approach

Making every field `TEXT`, every number `DOUBLE PRECISION`, and every timestamp a plain `TIMESTAMP`.

### Production Considerations

Use expand-and-contract awareness for risky changes. In systems where constraints are informational rather than enforced, compensate with data-quality assertions.

### Interviewer Follow-Up

1. When would JSONB be preferable to normal columns?
2. Why might `BIGINT` be preferred over `INTEGER` for identifiers?
3. What is the operational risk of adding a constraint to a large table?

### Strong Interview Answer

“I start from row meaning and access patterns. Types should preserve semantics, constraints should encode invariants, and partitioning should serve a measurable pruning need. Nested data belongs in JSONB or nested types when that matches its usage, but high-value relational attributes should be explicit.”

## Question 17 — Which Index Would You Create?

**Difficulty:** Moderate  
**Primary Topic(s):** indexes, B-tree, composite indexes  
**Integrated Topic(s):** leftmost-prefix, INCLUDE, partial/expression indexes, selectivity, GIN/GiST/BRIN

### Interview Problem

A 500-million-row `orders` table commonly serves:

```sql
SELECT order_id, amount
FROM orders
WHERE customer_id = :customer_id
  AND created_at >= :start_at
ORDER BY created_at DESC
FETCH FIRST 50 ROWS ONLY;
```

and:

```sql
SELECT order_id
FROM orders
WHERE LOWER(email) = LOWER(:email);
```

and:

```sql
SELECT order_id
FROM orders
WHERE status = 'pending'
ORDER BY created_at
FETCH FIRST 100 ROWS ONLY;
```

Which indexes would you propose and why?

### What the Interviewer Is Testing

Whether you design indexes from real access patterns.

### Candidate Clarification Questions

- What is selectivity?
- Does `created_at` correlate with physical order?
- Are reads or writes dominant?
- Which queries are frequent enough to justify extra maintenance?

### Recommended Thinking Process

1. Map each query to equality, range, ordering, and returned columns.
2. Build a composite index around the common predicate order.
3. Use INCLUDE for coverage when useful.
4. Use expression/partial indexes for stable repeated predicates.
5. Validate all proposals with plans.

### Solution

A strong starting point:

```sql
CREATE INDEX idx_orders_customer_created
ON orders (customer_id, created_at DESC)
INCLUDE (order_id, amount);
```

For the normalized email predicate:

```sql
CREATE INDEX idx_orders_lower_email
ON orders (LOWER(email));
```

For a highly selective pending subset:

```sql
CREATE INDEX idx_orders_pending_created
ON orders (created_at)
WHERE status = 'pending';
```

`GIN` can help PostgreSQL JSONB/array search. `GiST` supports broader search structures such as range data. `BRIN` can be useful for very large physically correlated columns such as append-oriented timestamps.

### Detailed Explanation

The leftmost-prefix idea means `(customer_id, created_at)` naturally supports predicates beginning with `customer_id`. `INCLUDE` adds non-key columns for possible index-only access without changing search order.

Indexes are not free: they use storage and add write and maintenance work.

### Worked Example

Query A can seek to a customer and then walk that customer's records by timestamp. Query C may benefit from a small partial index if only a small fraction of rows are pending.

### Edge Cases

- Low selectivity may make an index unattractive.
- An index that looks perfect on paper can still lose to a sequential scan.
- Write-heavy tables can suffer from excessive indexing.

### Common Wrong Approach

Indexing every filtered column independently without considering composite access paths.

### Production Considerations

Follow the module's tuning loop: measure, inspect plan, form a hypothesis, change one thing, measure again. `CREATE INDEX CONCURRENTLY` may be useful for online production index creation where supported.

### Interviewer Follow-Up

1. Why might PostgreSQL ignore one of these indexes?
2. When is `CREATE INDEX CONCURRENTLY` useful?
3. What is the trade-off of creating indexes before a bulk load?

### Strong Interview Answer

“I map each high-value query to its equality, range, ordering, and output columns. For the customer query I would start with `(customer_id, created_at DESC)` and optionally INCLUDE projected fields. I would use expression or partial indexes only for repeated workload patterns and validate everything with the plan.”

## Question 18 — Read a Hypothetical EXPLAIN ANALYZE Plan

**Difficulty:** Moderate  
**Primary Topic(s):** EXPLAIN, EXPLAIN ANALYZE, plan operators  
**Integrated Topic(s):** estimated vs actual rows, loops, scans, joins, aggregates, statistics

### Interview Problem

Suppose the plan is:

```text
HashAggregate  (actual rows=1)
  -> Nested Loop
       -> Seq Scan on customers
          (estimated rows=10,000 actual rows=9,800)
       -> Index Scan on orders_customer_idx
          (estimated rows=5 actual rows=8,500 loops=9,800)
```

Explain the biggest red flag, the meaning of `loops`, and what you would investigate before changing indexes.

### What the Interviewer Is Testing

Whether you can read a plan from the inside out and form a measured hypothesis.

### Candidate Clarification Questions

- Which node dominates total work?
- How different are estimated and actual rows?
- Why is the inner scan repeated so many times?
- Are statistics current?

### Recommended Thinking Process

1. Start at the leaf scans.
2. Compare estimate to actual.
3. Use `loops` to understand repeated work.
4. Question whether nested loop remains appropriate at the actual cardinality.
5. Investigate statistics and data skew before changing schema.

### Solution

The major red flag is:

```text
estimated rows per inner lookup: 5
actual rows per lookup:           8,500
loops:                            9,800
```

The planner believed the inner scan was cheap, but it is actually enormous.

Investigate:

- planner statistics and `ANALYZE`;
- data skew or duplicate-key issues;
- filter and join selectivity;
- alternative join algorithms;
- whether the chosen index is appropriate;
- whether the query shape is creating unexpected multiplicity.

### Detailed Explanation

`EXPLAIN` gives estimates. `EXPLAIN ANALYZE` executes and gives actual timing/cardinality. `BUFFERS` adds I/O information.

`loops` means the node was executed repeatedly. High actual rows multiplied by high loops explains why an apparently simple index scan can dominate runtime.

### Worked Example

If the inner scan returns 8,500 rows on 9,800 loops, the system may be processing tens of millions of rows even though the planner expected only tens of thousands.

### Edge Cases

- A nested loop can be correct when the outer side is highly selective.
- An index scan is not automatically efficient.
- A sequential scan can be the correct choice when most table pages are needed.

### Common Wrong Approach

Seeing “Index Scan” and assuming the query is optimized.

### Production Considerations

Use `EXPLAIN (ANALYZE, BUFFERS)` for real measurements. `pg_stat_statements` and `auto_explain` provide production awareness for recurring slow queries.

### Interviewer Follow-Up

1. What would stale statistics look like?
2. When would a Hash Join be preferable to a Nested Loop?
3. What does a Bitmap Heap Scan represent?

### Strong Interview Answer

“The planner estimated five rows per index lookup but saw 8,500, repeated 9,800 times. That cardinality error makes the nested loop far more expensive than expected. I would investigate statistics and join selectivity first, then test an alternative plan rather than blindly adding indexes.”

## Question 19 — Prevent a Lost Update with Transaction Reasoning

**Difficulty:** Moderate  
**Primary Topic(s):** transactions, ACID, isolation, UPDATE  
**Integrated Topic(s):** row locking, MVCC, BEGIN/COMMIT, lost updates

### Interview Problem

Two workers both process the same account:

```text
Initial balance = 100

A reads 100
B reads 100
A writes 110
B writes 120
```

The intended final balance is 130 because both adjustments should apply. Explain the lost update and show a safer SQL pattern.

### What the Interviewer Is Testing

Whether you can reason about concurrent read-modify-write operations.

### Candidate Clarification Questions

- Are the operations additive or replacement-style?
- Is the same account allowed to be processed concurrently?
- Does the business invariant require exactly-once adjustment?

### Recommended Thinking Process

1. State the invariant.
2. Prefer an atomic update if possible.
3. Use a transaction around the business unit.
4. Use `FOR UPDATE` when a read-dependent decision needs a protected row.

### Solution

For additive adjustments:

```sql
BEGIN;

UPDATE accounts
SET balance = balance + 10
WHERE account_id = 42;

UPDATE accounts
SET balance = balance + 20
WHERE account_id = 42;

COMMIT;
```

If the application must read first:

```sql
BEGIN;

SELECT balance
FROM accounts
WHERE account_id = 42
FOR UPDATE;

UPDATE accounts
SET balance = :new_balance
WHERE account_id = 42;

COMMIT;
```

### Detailed Explanation

A transaction gives atomicity, but the business operation still has to be concurrency-safe. Atomic arithmetic avoids the stale-read overwrite. `FOR UPDATE` protects a selected row until commit so another transaction cannot perform a conflicting update simultaneously.

PostgreSQL uses MVCC, so readers and writers can often proceed without simple blocking; explicit row locks are used when the business logic requires coordinated access.

### Worked Example

Atomic increments:

```text
100 + 10 + 20 = 130
```

Stale read/replace logic can produce 110 or 120 instead.

### Edge Cases

- Duplicate job execution is separate from locking correctness.
- Stronger isolation can produce serialization failures that need retries.
- Long transactions increase contention.

### Common Wrong Approach

Assuming “put BEGIN/COMMIT around it” automatically prevents lost updates.

### Production Considerations

Keep transactions short and choose locking/isolation based on the actual business invariant.

### Interviewer Follow-Up

1. What anomaly is this?
2. When would SERIALIZABLE be more appropriate?
3. How does MVCC relate to reader/writer blocking?

### Strong Interview Answer

“This is a lost update caused by stale read-modify-write behavior. If possible I would express the operation atomically as `balance = balance + delta`. If the decision depends on the current row, I would use a short transaction with `FOR UPDATE`.”

## Question 20 — MERGE Requires a Deterministic Source

**Difficulty:** Moderate  
**Primary Topic(s):** MERGE, ON CONFLICT, source deduplication  
**Integrated Topic(s):** MATCHED, NOT MATCHED, conditional delete, idempotency

### Interview Problem

You write a MERGE from `staging_products`, but the staging data can contain multiple rows per `product_id`. Explain why that is unsafe, deduplicate the source deterministically, and show how a tombstone can be represented as a conditional delete.

### What the Interviewer Is Testing

Whether you understand that MERGE correctness starts with source grain and not MERGE syntax alone.

### Candidate Clarification Questions

- Is the target one row per product?
- Which source row wins?
- Can deletes be mixed with upserts?
- What timestamp and tie-breaker define source order?

### Recommended Thinking Process

1. State source and target grains.
2. Reduce staging to one row per merge key.
3. Encode a deterministic survivor rule.
4. Apply matched, not-matched, and delete branches.
5. Validate source uniqueness before the merge.

### Solution

```sql
WITH ranked_source AS (
    SELECT
        s.*,
        ROW_NUMBER() OVER (
            PARTITION BY product_id
            ORDER BY updated_at DESC NULLS LAST,
                     ingestion_id DESC
        ) AS rn
    FROM staging_products s
),
deduped_source AS (
    SELECT *
    FROM ranked_source
    WHERE rn = 1
)
MERGE INTO product_state AS t
USING deduped_source AS s
ON t.product_id = s.product_id
WHEN MATCHED AND s.is_deleted THEN
    DELETE
WHEN MATCHED AND (
       t.price IS DISTINCT FROM s.price
    OR t.is_active IS DISTINCT FROM s.is_active
) THEN
    UPDATE SET
        price = s.price,
        is_active = s.is_active
WHEN NOT MATCHED AND NOT s.is_deleted THEN
    INSERT (product_id, price, is_active)
    VALUES (s.product_id, s.price, s.is_active);
```

### Detailed Explanation

If multiple source rows map to one target key, the merge action can be ambiguous or fail with a cardinality error depending on the exact engine and actions. Source deduplication is therefore part of correctness.

The survivor must be deterministic. A timestamp alone may tie, so a final ingestion sequence or other stable criterion is needed.

### Worked Example

Two rows for product 7 at 09:00 and 10:00 produce exactly one source row after deduplication; the 10:00 row survives.

### Edge Cases

- Tied timestamps need tie-breakers.
- Tombstones should have explicit delete semantics.
- Unchanged rows do not necessarily need updates.

### Common Wrong Approach

Using `DISTINCT` over the full row and assuming business-key duplicates are gone.

### Production Considerations

Assert source uniqueness before MERGE and treat the staging-to-apply boundary as a controlled publication step.

### Interviewer Follow-Up

1. What if the source contains a tombstone and a later upsert for the same key?
2. How would you verify idempotency?
3. What changes across PostgreSQL and DuckDB MERGE implementations?

### Strong Interview Answer

“Before MERGE, I need one deterministic source row per target key. I would deduplicate staging with `ROW_NUMBER`, assert uniqueness, then apply `MATCHED`, `NOT MATCHED`, and delete semantics. Source normalization is a correctness requirement, not an optimization.”

# Part III — Hard

## Question 21 — Debug an Inflated Revenue Report

**Difficulty:** Hard  
**Primary Topic(s):** Joins, aggregation, grain, reconciliation  
**Integrated Topic(s):** Fan trap, cardinality assertions, preaggregation, point-in-time awareness

### Interview Problem

A finance report shows 2.4× the expected revenue. The query is:

```sql
SELECT
    o.order_id,
    SUM(ol.extended_amount) AS item_revenue,
    SUM(p.amount) AS payment_amount,
    SUM(r.amount) AS refund_amount
FROM orders o
LEFT JOIN order_lines ol
  ON ol.order_id = o.order_id
LEFT JOIN payments p
  ON p.order_id = o.order_id
LEFT JOIN refunds r
  ON r.order_id = o.order_id
GROUP BY o.order_id;
```

You discover that some orders have multiple lines, payments, and refunds. Diagnose the bug and redesign the query.

### What the Interviewer Is Testing

Whether you can diagnose a fan trap from grain and row multiplication, then repair the calculation rather than hiding the symptom.

### Candidate Clarification Questions

Before solving, clarify:

- What is the intended output grain?
- What is the grain of each child table?
- Which keys are unique?
- How many rows can each child contribute per order?
- What source totals are trusted for reconciliation?

### Recommended Thinking Process

1. State the target grain: one row per order.
2. State the child grains: one row per order line/payment/refund event.
3. Recognize that joining independent one-to-many children multiplies combinations.
4. Compute the theoretical multiplication as the product of child row counts.
5. Pre-aggregate each child independently to order grain.
6. Join the order-grain results.
7. Reconcile the repaired measures to source totals.

### Solution

Pre-aggregate each child relation before joining:

```sql
WITH line_totals AS (
    SELECT
        order_id,
        SUM(extended_amount) AS item_revenue
    FROM order_lines
    GROUP BY order_id
),
payment_totals AS (
    SELECT
        order_id,
        SUM(amount) AS payment_amount
    FROM payments
    GROUP BY order_id
),
refund_totals AS (
    SELECT
        order_id,
        SUM(amount) AS refund_amount
    FROM refunds
    GROUP BY order_id
)
SELECT
    o.order_id,
    COALESCE(l.item_revenue, 0) AS item_revenue,
    COALESCE(p.payment_amount, 0) AS payment_amount,
    COALESCE(r.refund_amount, 0) AS refund_amount
FROM orders AS o
LEFT JOIN line_totals AS l
  ON l.order_id = o.order_id
LEFT JOIN payment_totals AS p
  ON p.order_id = o.order_id
LEFT JOIN refund_totals AS r
  ON r.order_id = o.order_id;
```

### Detailed Explanation

Suppose one order has 3 lines, 2 payments, and 2 refunds. The direct join can create up to:

```text
3 × 2 × 2 = 12 rows
```

for that single order. Every child measure can therefore be repeated across those combinations.

The repair works because each measure is first calculated at its natural grain and then converted to the common target grain of one row per order.

A useful validation is:

```sql
SELECT COUNT(*) AS output_rows,
       COUNT(DISTINCT order_id) AS distinct_orders
FROM repaired_order_metrics;
```

For an order-grain relation, those values should agree. You should also compare the repaired financial totals with trusted source totals.

### Worked Example

If order 101 has:

```text
3 lines      → $300 item revenue
2 payments   → $300 payments
2 refunds    → $50 refunds
```

the broken join can have 12 rows. The repaired query has one row and returns the intended totals.

### Edge Cases

- Missing child rows should normally become NULL after the LEFT JOIN and become 0 only if zero is the business meaning.
- Duplicate child keys can indicate a data-quality problem rather than a legitimate one-to-many relationship.
- A historical customer dimension can also multiply rows if more than one effective version matches the fact.
- `COUNT(*)` after a fan-trap join is not a valid order count.

### Common Wrong Approach

Using `SELECT DISTINCT` on the final result. DISTINCT can hide duplicated entity rows, but it does not undo duplicated amounts that were already summed.

### Production Considerations

Add zero-row uniqueness assertions for each pre-aggregated relation and reconcile raw totals before publishing the report. Keep the correctness fix separate from later performance tuning.

### Interviewer Follow-Up

1. How would you prove the repaired report is correct?
2. What if one order has no payments?
3. How would you detect an order that joins to multiple historical dimension versions?

### Strong Interview Answer

A strong candidate would say:

> “The target grain is one row per order, but the query joins several independent one-to-many child tables. That creates a fan trap and multiplies measures. I would pre-aggregate each child to order grain, join those summaries, then reconcile row counts and financial totals against trusted sources.”

## Question 22 — Top-N Per Group with Ties and Window Frames

**Difficulty:** Hard  
**Primary Topic(s):** Window functions, ranking  
**Integrated Topic(s):** Ties, top-N semantics, filtering windows, moving averages

### Interview Problem

A marketplace wants:

> “For each country, return the top 3 products by revenue, including every product tied at the third position.”

It also wants a 7-row moving average of daily country revenue.

Explain which ranking function you would choose and why. Then write the SQL and explain the frame used for the moving average.

### What the Interviewer Is Testing

Whether you choose a ranking function and window frame from explicit business semantics rather than from memorized syntax.

### Candidate Clarification Questions

- Does “top 3” mean exactly three rows or three rank positions?
- Should tied products all be returned?
- Is product revenue already at one row per country/product?
- Does “7-day” actually mean seven rows or seven calendar days?

### Recommended Thinking Process

1. Aggregate raw sales to country/product grain.
2. Rank products inside each country.
3. Use `RANK` if tied rank positions must all survive.
4. Filter the ranking in a CTE or a dialect-supported `QUALIFY` clause.
5. For the moving average, choose `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` only when seven rows, not seven dates, is the intended metric.

### Solution

Top products:

```sql
WITH product_revenue AS (
    SELECT
        country,
        product_id,
        SUM(revenue) AS revenue
    FROM sales
    GROUP BY country, product_id
),
ranked AS (
    SELECT
        *,
        RANK() OVER (
            PARTITION BY country
            ORDER BY revenue DESC
        ) AS rnk
    FROM product_revenue
)
SELECT
    country,
    product_id,
    revenue
FROM ranked
WHERE rnk <= 3;
```

A seven-row moving average is:

```sql
AVG(revenue) OVER (
    PARTITION BY country
    ORDER BY revenue_date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
)
```

### Detailed Explanation

`ROW_NUMBER` gives exactly one sequential position per row. `RANK` preserves ties and leaves gaps after a tie. `DENSE_RANK` preserves ties but removes the gaps.

For the tied-third-position requirement, rank only on revenue. Adding a unique tie-breaker to the `RANK` ordering would change which rows are peers and therefore change the business meaning.

A `ROWS` frame counts ordered rows. It is not automatically the same as seven calendar days. If dates are missing, a seven-row window can span much more than seven days.

### Worked Example

For revenue values `100, 90, 90, 80`:

```text
RANK        → 1, 2, 2, 4
DENSE_RANK  → 1, 2, 2, 3
ROW_NUMBER  → 1, 2, 3, 4
```

`RANK <= 3` returns all three rows through the tied 90s.

### Edge Cases

- Ties need deliberate semantics.
- Missing dates make a row-based moving average differ from a seven-day average.
- NULL revenue needs an ordering policy.
- Ranking after a join explosion can rank duplicated revenue instead of real revenue.

### Common Wrong Approach

Using `ROW_NUMBER <= 3` without asking whether ties should be preserved. Another mistake is adding a unique tie-breaker to `RANK` while still claiming that all tied values should share a rank.

### Production Considerations

State the tie rule in the metric definition. In DuckDB, a window result can also be filtered with `QUALIFY`; in standard SQL, use a CTE or derived table.

### Interviewer Follow-Up

1. How would you return exactly three products per country?
2. When would `DENSE_RANK` be preferable?
3. How would you implement a true seven-calendar-day window when dates can be missing?

### Strong Interview Answer

> “I first aggregate to country/product grain. Because the requirement is top three rank positions including ties, I use `RANK` over revenue and filter `rnk <= 3`. For the moving average, I would explicitly decide whether seven rows or seven calendar days is intended before selecting the frame.”

## Question 23 — Gaps and Islands: Longest Consecutive Activity Streak

**Difficulty:** Hard  
**Primary Topic(s):** Window functions, date arithmetic  
**Integrated Topic(s):** Deduplication, gaps-and-islands, grouping

### Interview Problem

A user activity table contains many events per day. You need the longest streak of consecutive calendar days on which each user was active.

Explain the gaps-and-islands method and write PostgreSQL SQL that first reduces the data to one row per user/day.

### What the Interviewer Is Testing

Whether you can transform an ordered sequence into stable groups using window functions and careful grain control.

### Candidate Clarification Questions

- Does multiple activity on one day count once?
- What timezone defines the activity date?
- Is “consecutive” based on calendar dates?
- Should ties between equally long streaks return all tied streaks or one deterministic row?

### Recommended Thinking Process

1. Deduplicate to one `(user_id, activity_date)` row.
2. Number each user's dates in order.
3. Subtract the row number from the date.
4. Consecutive dates produce the same derived island key.
5. Group each island and count its length.
6. Select the longest island per user.

### Solution

```sql
WITH active_days AS (
    SELECT DISTINCT
        user_id,
        event_ts::date AS activity_date
    FROM activity_events
),
numbered AS (
    SELECT
        user_id,
        activity_date,
        activity_date
          - ROW_NUMBER() OVER (
                PARTITION BY user_id
                ORDER BY activity_date
            )::int AS island_key
    FROM active_days
),
islands AS (
    SELECT
        user_id,
        island_key,
        MIN(activity_date) AS start_date,
        MAX(activity_date) AS end_date,
        COUNT(*) AS streak_days
    FROM numbered
    GROUP BY user_id, island_key
)
SELECT
    i.user_id,
    i.start_date,
    i.end_date,
    i.streak_days
FROM islands AS i
WHERE i.streak_days = (
    SELECT MAX(i2.streak_days)
    FROM islands AS i2
    WHERE i2.user_id = i.user_id
);
```

### Detailed Explanation

Suppose a user has:

```text
Jan 1
Jan 2
Jan 3
Jan 7
Jan 8
```

The first three dates form one island and Jan 7–8 form another. Because both the date and the row number increase together inside a consecutive run, their difference remains constant within each island.

The first `DISTINCT` is important because duplicate events on the same day would otherwise consume sequence positions and break the island calculation.

### Worked Example

For one user:

```text
Jan 1 → row 1
Jan 2 → row 2
Jan 3 → row 3
Jan 7 → row 4
Jan 8 → row 5
```

The derived date-minus-row-number value is constant for Jan 1–3 and changes at the gap to Jan 7.

### Edge Cases

- Duplicate daily events.
- Timezone conversion changing the date boundary.
- A one-day streak.
- Multiple equally long streaks.
- Users with no qualifying events.

### Common Wrong Approach

Grouping by month or simply comparing each date to the previous date without first converting the sequence into stable islands.

### Production Considerations

Test with tiny data containing duplicates, gaps, one-day streaks, and ties. If the same logic runs on very large event tables, make event-time semantics and deduplication rules explicit before optimizing.

### Interviewer Follow-Up

1. How would you return exactly one longest streak per user?
2. How is this different from sessionisation?
3. How would a timezone change affect the answer?

### Strong Interview Answer

> “I first normalize the grain to one row per user per active day. Then I assign row numbers by date and use date minus row number as an island key. Consecutive dates share that key, so I can aggregate each island and identify the longest streak.”

## Question 24 — Sessionisation with LAG and a Running Session ID

**Difficulty:** Hard  
**Primary Topic(s):** LAG, running SUM, window functions  
**Integrated Topic(s):** Event ordering, session grain, threshold logic

### Interview Problem

A clickstream contains `user_id`, `event_id`, and `event_ts`. A new session starts whenever the gap from the previous event for the same user is greater than 30 minutes.

Write SQL that assigns a session number and returns session start, session end, event count, and duration.

### What the Interviewer Is Testing

Whether you can convert row-to-row state into a cumulative session identifier and then change the grain from event to session.

### Candidate Clarification Questions

- Is exactly 30 minutes still the same session?
- Are timestamps unique?
- What is the first event's session flag?
- Is the output one row per event or one row per session?
- Is event order based on event time or ingestion time?

### Recommended Thinking Process

1. Order deterministically by `event_ts, event_id`.
2. Use `LAG` to get the previous timestamp.
3. Mark the first event and every gap greater than 30 minutes as a new session.
4. Running-sum the flag to create a session identifier.
5. Aggregate to session grain.

### Solution

```sql
WITH ordered AS (
    SELECT
        e.*,
        LAG(event_ts) OVER (
            PARTITION BY user_id
            ORDER BY event_ts, event_id
        ) AS prev_event_ts
    FROM click_events AS e
),
flagged AS (
    SELECT
        *,
        CASE
            WHEN prev_event_ts IS NULL THEN 1
            WHEN event_ts - prev_event_ts > INTERVAL '30 minutes' THEN 1
            ELSE 0
        END AS new_session
    FROM ordered
),
sessionized AS (
    SELECT
        *,
        SUM(new_session) OVER (
            PARTITION BY user_id
            ORDER BY event_ts, event_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS session_id
    FROM flagged
)
SELECT
    user_id,
    session_id,
    MIN(event_ts) AS session_start,
    MAX(event_ts) AS session_end,
    COUNT(*) AS event_count,
    MAX(event_ts) - MIN(event_ts) AS duration
FROM sessionized
GROUP BY user_id, session_id
ORDER BY user_id, session_id;
```

### Detailed Explanation

The pattern is:

```text
LAG
→ new-session flag
→ running SUM
→ session grain aggregation
```

`LAG` gives local information about the previous event. The running sum turns those local boundaries into a stable session identifier.

A 30-minute boundary is an explicit business rule. Here a gap of exactly 30 minutes remains inside the existing session because only gaps greater than 30 minutes create a new one.

### Worked Example

For a user with events at:

```text
10:00
10:20
10:50
11:31
```

the session IDs are:

```text
10:00 → 1
10:20 → 1
10:50 → 1
11:31 → 2
```

The final gap is 41 minutes.

### Edge Cases

- Tied timestamps require a tie-breaker.
- The first row has no previous event.
- NULL timestamps require a policy.
- Late-arriving events can change session boundaries if recomputation is event-time based.

### Common Wrong Approach

Using a 30-row window and assuming it means 30 minutes. Window row counts are not time intervals.

### Production Considerations

Document whether sessionisation uses event time or ingestion time. Late events can invalidate previously computed session boundaries, so the pipeline may need a reproducible recomputation strategy for the affected users/time range.

### Interviewer Follow-Up

1. What happens when a late event arrives between two existing events?
2. How would you count sessions per day?
3. How would the logic change for a 15-minute threshold?

### Strong Interview Answer

> “I order each user's events deterministically, use `LAG` to measure the gap, flag session boundaries, then cumulative-sum that flag to produce a session ID. Finally I aggregate at session grain. The important distinction is that a time threshold is not the same thing as a row-based window frame.”

## Question 25 — Advanced Deduplication: Priority, Completeness, and Safe Deletion

**Difficulty:** Hard  
**Primary Topic(s):** Deduplication, ROW_NUMBER, duplicate detection  
**Integrated Topic(s):** DISTINCT ON, source priority, completeness, safe deletion

### Interview Problem

A customer staging table contains several rows for the same `customer_id`. The survivor policy is:

1. CRM outranks ERP.
2. Newer `updated_at` wins.
3. Non-NULL email is preferred.
4. Highest `ingestion_id` breaks any remaining tie.

Explain how you would define the duplicate, select the survivor, and safely identify rows that could be deleted from a live table.

### What the Interviewer Is Testing

Whether you can translate business survivor rules into deterministic SQL and separate duplicate selection from destructive cleanup.

### Candidate Clarification Questions

- What is the business key?
- Is there a stable physical row identifier?
- Are timestamps authoritative?
- What happens if all listed criteria tie?
- Is the delete reversible inside a transaction?

### Recommended Thinking Process

1. Duplicate means multiple rows for the same business key, not necessarily identical full rows.
2. Encode the survivor rule as a complete ordering.
3. Use `ROW_NUMBER()` to select exactly one row.
4. Preview victims before deleting anything.
5. Delete by exact row identifier inside a transaction.
6. Assert that business-key duplicates are gone afterward.

### Solution

```sql
WITH ranked AS (
    SELECT
        row_id,
        customer_id,
        source,
        updated_at,
        email,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY
                CASE WHEN source = 'CRM' THEN 1 ELSE 0 END DESC,
                updated_at DESC NULLS LAST,
                CASE WHEN email IS NOT NULL THEN 1 ELSE 0 END DESC,
                ingestion_id DESC,
                row_id DESC
        ) AS rn
    FROM customer_staging
)
SELECT *
FROM ranked
WHERE rn = 1;
```

Victims can be previewed with:

```sql
WITH ranked AS (
    SELECT
        row_id,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY
                CASE WHEN source = 'CRM' THEN 1 ELSE 0 END DESC,
                updated_at DESC NULLS LAST,
                CASE WHEN email IS NOT NULL THEN 1 ELSE 0 END DESC,
                ingestion_id DESC,
                row_id DESC
        ) AS rn
    FROM customer_staging
)
SELECT row_id
FROM ranked
WHERE rn > 1;
```

PostgreSQL can also express the survivor with `DISTINCT ON`:

```sql
SELECT DISTINCT ON (customer_id)
    row_id,
    customer_id,
    source,
    updated_at,
    email
FROM customer_staging
ORDER BY
    customer_id,
    CASE WHEN source = 'CRM' THEN 1 ELSE 0 END DESC,
    updated_at DESC NULLS LAST,
    CASE WHEN email IS NOT NULL THEN 1 ELSE 0 END DESC,
    ingestion_id DESC,
    row_id DESC;
```

### Detailed Explanation

`DISTINCT` removes duplicate complete rows. It does not know that two rows with the same business key represent competing versions of the same entity.

`RANK()` can leave multiple rows tied at rank 1, so it is not the right tool when exactly one deterministic survivor is required. `ROW_NUMBER()` is appropriate once the ordering is total.

The final physical tie-breaker ensures that two otherwise indistinguishable candidates still produce a stable survivor.

### Worked Example

For customer 10:

```text
CRM,  Sep 21, non-NULL, ingestion 103
ERP,  Sep 22, non-NULL, ingestion 104
```

CRM wins because source priority is the first rule. If two CRM rows tie on all business criteria, the highest final tie-breaker wins.

### Edge Cases

- Tied timestamps.
- NULL timestamps.
- Duplicate ingestion IDs.
- Missing stable physical row IDs.
- A business key that itself can be NULL.

### Common Wrong Approach

Using `SELECT DISTINCT` and assuming it means “keep the best record.” Another error is deleting by `customer_id` rather than by specific victim row IDs.

### Production Considerations

Use a preview query, execute deletes inside a controlled transaction, and assert the final uniqueness condition. Large deletes can create lock pressure and table bloat, so operational execution matters as much as logical correctness.

### Interviewer Follow-Up

1. Why is `ROW_NUMBER` deterministic only if the ordering is complete?
2. How would you detect duplicate business keys before deletion?
3. When is `DISTINCT ON` a good PostgreSQL shortcut?

### Strong Interview Answer

> “I define duplicates at business-key grain, then express the survivor policy as an ordered priority list. `ROW_NUMBER()` selects exactly one stable survivor. Before deleting anything, I preview the victim row IDs, delete inside a transaction, and assert the business key is unique afterward.”

## Question 26 — Advanced Aggregation: ROLLUP, Ratios, Weighted Averages, and Precision

**Difficulty:** Hard  
**Primary Topic(s):** GROUP BY, conditional aggregation, ROLLUP, GROUPING SETS  
**Integrated Topic(s):** FILTER, percentiles, weighted averages, numeric precision, approximate distinct

### Interview Problem

A product analytics report must contain:

- revenue by country and month;
- country subtotals;
- a grand total;
- order count;
- distinct customers;
- conversion rate;
- p95 latency;
- weighted average price.

Explain how you would structure the query and how you would distinguish a subtotal NULL from a real NULL country.

### What the Interviewer Is Testing

Whether you can combine several aggregate metrics without losing control of grain, denominator, or subtotal semantics.

### Candidate Clarification Questions

- What is the base fact grain?
- Is a NULL country a real business value?
- What exactly is the conversion denominator?
- Must p95 and distinct counts be exact?
- Is price quantity-weighted?

### Recommended Thinking Process

1. Establish the base filtered relation and grain.
2. Define each metric mathematically.
3. Use `ROLLUP` or `GROUPING SETS` for subtotal levels.
4. Use `GROUPING()` to identify subtotal markers.
5. Protect ratio denominators with `NULLIF`.
6. Use weights explicitly for weighted averages.
7. Choose exact versus approximate aggregation from the metric requirement.

### Solution

A PostgreSQL-style pattern is:

```sql
SELECT
    country,
    DATE_TRUNC('month', event_ts) AS month,
    GROUPING(country) AS country_total,
    GROUPING(DATE_TRUNC('month', event_ts)) AS month_total,
    COUNT(*) AS event_count,
    COUNT(DISTINCT customer_id) AS customer_count,
    SUM(revenue) AS revenue,
    SUM(CASE WHEN converted THEN 1 ELSE 0 END)::NUMERIC
        / NULLIF(COUNT(*), 0) AS conversion_rate,
    PERCENTILE_CONT(0.95)
        WITHIN GROUP (ORDER BY latency_ms) AS p95_latency,
    SUM(unit_price * quantity)
        / NULLIF(SUM(quantity), 0) AS weighted_avg_price
FROM events
GROUP BY ROLLUP (
    country,
    DATE_TRUNC('month', event_ts)
)
ORDER BY country, month;
```

Conditional aggregates can also use PostgreSQL's `FILTER` syntax:

```sql
COUNT(*) FILTER (WHERE status = 'success')
```

### Detailed Explanation

`ROLLUP(country, month)` creates:

```text
(country, month)
(country)
()
```

A subtotal row can contain NULL in a grouping column. That does not necessarily mean the original data had a NULL value. `GROUPING(column)` identifies whether the column was rolled up.

Ratios need explicit numerator and denominator definitions. Weighted averages require:

```text
SUM(value × weight) / SUM(weight)
```

not `AVG(value)` when weights vary.

`NUMERIC` is appropriate when exact decimal semantics matter. Floating-point types are approximate. Distinct counts can also be implemented approximately in engines that support it, but approximation should be a conscious business decision rather than an invisible optimization.

### Worked Example

Suppose the result contains:

```text
India | 2026-09 | 0 | 0
India | NULL    | 0 | 1
NULL  | NULL    | 1 | 1
```

The second row is the country subtotal and the third is the grand total. `GROUPING(country)` distinguishes them from ordinary data NULLs.

### Edge Cases

- Real NULL countries.
- Zero denominator for a ratio.
- Zero total weight.
- Large sums that stress numeric precision.
- Approximate distinct when exact reconciliation is required.

### Common Wrong Approach

Calculating a simple average of already-aggregated averages or treating every NULL country as a subtotal.

### Production Considerations

Large exact distinct counts and exact percentiles can be expensive. Use measured performance and explicit correctness requirements. Avoid positional grouping such as `GROUP BY 1,2` in long-lived production SQL when explicit expressions would be clearer and safer.

### Interviewer Follow-Up

1. What is the difference between `ROLLUP` and `GROUPING SETS`?
2. How would you use `CUBE` for country × device × month?
3. When would approximate distinct counting be acceptable?

### Strong Interview Answer

> “I define the base grain and every numerator/denominator first. Then I use conditional aggregation plus `ROLLUP` or `GROUPING SETS` for subtotal levels, `GROUPING()` to distinguish rollups from real NULLs, and weighted formulas where weights matter. Exact versus approximate metrics must be an explicit requirement.”

## Question 27 — Why Isn't the Index Being Used?

**Difficulty:** Hard  
**Primary Topic(s):** Indexes, EXPLAIN ANALYZE, predicates  
**Integrated Topic(s):** Sargability, selectivity, statistics

### Interview Problem

The table has:

```sql
CREATE INDEX idx_events_created_at
ON events (created_at);
```

But PostgreSQL executes:

```sql
SELECT COUNT(*)
FROM events
WHERE DATE(created_at) = DATE '2026-09-28';
```

with a sequential scan over hundreds of millions of rows.

Explain why the index may not be used, rewrite the query, and describe how you would validate the fix.

### What the Interviewer Is Testing

Whether you can identify non-sargable predicates and apply the module's measure → hypothesis → change → measure process.

### Candidate Clarification Questions

- What type is `created_at`?
- What timezone defines the business day?
- What fraction of the table matches the date?
- Are statistics current?
- What does `EXPLAIN (ANALYZE, BUFFERS)` report?

### Recommended Thinking Process

1. The index is on the raw column.
2. The predicate wraps that column in `DATE()`.
3. Replace the expression with a half-open range on the raw timestamp.
4. Inspect the actual plan and buffers.
5. If the range is still unselective, accept that a sequential scan may be correct.

### Solution

```sql
SELECT COUNT(*)
FROM events
WHERE created_at >= TIMESTAMPTZ '2026-09-28 00:00:00+00'
  AND created_at <  TIMESTAMPTZ '2026-09-29 00:00:00+00';
```

Validate with:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*)
FROM events
WHERE created_at >= TIMESTAMPTZ '2026-09-28 00:00:00+00'
  AND created_at <  TIMESTAMPTZ '2026-09-29 00:00:00+00';
```

### Detailed Explanation

`DATE(created_at)` computes a transformed value for comparison. A direct range on `created_at` preserves the column's searchable form and can use an ordinary B-tree range access path.

But an index is not a command to the planner. If the filter matches most of the table, reading the table sequentially can be cheaper than many random index-driven accesses. Other reasons for a sequential scan include stale statistics, data skew, type mismatches, or a query that needs most pages anyway.

### Worked Example

If only one day's events represent 0.2% of the table, an index or partition-pruned path is often a plausible choice. If the same predicate matches 70% of the table, a sequential scan may be entirely reasonable.

### Edge Cases

- Timezone boundaries.
- NULL timestamps.
- Type mismatches between parameters and columns.
- Stale statistics.
- Very low-selectivity predicates.

### Common Wrong Approach

Saying “the index exists, so PostgreSQL should use it.” Another mistake is immediately creating an expression index without first testing the simpler half-open predicate.

### Production Considerations

Follow:

```text
measure
→ inspect plan
→ form hypothesis
→ change one thing
→ measure again
```

For very large append-correlated time-series tables, BRIN or partition pruning may fit better than an OLTP-style B-tree. That decision should be based on the actual workload and physical layout.

### Interviewer Follow-Up

1. Why can a sequential scan be faster than an index scan?
2. What would stale statistics look like in a plan?
3. How would a partitioned table change the access strategy?

### Strong Interview Answer

> “The index is on `created_at`, but the predicate transforms the column with `DATE()`. I would rewrite the filter as a half-open timestamp range, run `EXPLAIN ANALYZE (BUFFERS)`, and compare actual rows, timing, and I/O. I would not assume an index must be used; selectivity and planner cost matter.”

## Question 28 — Two-Session Write Skew Under Stronger Isolation

**Difficulty:** Hard  
**Primary Topic(s):** Transactions, isolation levels, MVCC  
**Integrated Topic(s):** Write skew, SERIALIZABLE, retry semantics

### Interview Problem

Two doctors are on call. The invariant is that at least one doctor must remain on duty.

Initial state:

```text
doctor A → on_call = true
doctor B → on_call = true
```

Session A and Session B both read that two doctors are on call. Each transaction sets its own doctor to false and commits.

Walk through the timeline, identify the anomaly, and explain how SERIALIZABLE changes the outcome.

### What the Interviewer Is Testing

Whether you can distinguish write skew from lost update and reason about isolation at the level of business invariants.

### Candidate Clarification Questions

- What isolation level is active?
- Is the invariant across one row or multiple rows?
- Which rows are read and which are updated?
- What should happen if both transactions attempt to commit?

### Recommended Thinking Process

1. State the invariant across the full set.
2. Notice that each session modifies a different row.
3. Explain why locking only the row being changed may not protect the cross-row invariant.
4. Use stronger isolation when the invariant requires it.
5. Design complete-transaction retry handling for serialization failures.

### Solution

At a weaker isolation level, the timeline can be:

```text
A: SELECT count(on_call) → 2
B: SELECT count(on_call) → 2

A: UPDATE doctor A → false
B: UPDATE doctor B → false

A: COMMIT
B: COMMIT
```

The final state can violate the invariant.

Under PostgreSQL `SERIALIZABLE`, one transaction can be aborted with a serialization error rather than allowing the dangerous interleaving to commit. The application should then retry the **entire transaction** from a fresh snapshot.

### Detailed Explanation

This is write skew, not a simple lost update. No transaction overwrites the same row written by the other; the problem is that two individually valid decisions become invalid together.

PostgreSQL's MVCC means transactions work with snapshots according to their isolation level. SERIALIZABLE adds stronger conflict detection so unsafe concurrent executions cannot both commit.

### Worked Example

A final state of:

```text
doctor A → false
doctor B → false
```

means the invariant is false:

```sql
SELECT COUNT(*)
FROM doctors
WHERE on_call;
```

returns 0.

### Edge Cases

- A transaction may be aborted after doing work; the complete transaction must be retried.
- Locking one row does not automatically protect a multi-row invariant.
- Long transactions increase contention and cleanup pressure.

### Common Wrong Approach

Treating SERIALIZABLE as a magic switch that removes the need for retries. Another mistake is assuming `FOR UPDATE` on one row automatically protects every row participating in the invariant.

### Production Considerations

Choose isolation from the invariant you must protect. Keep transactions short and make the business operation retryable. Use explicit assertions to verify the invariant after successful publication.

### Interviewer Follow-Up

1. How is this different from a lost update?
2. What might REPEATABLE READ allow?
3. Why must the application retry the entire transaction?

### Strong Interview Answer

> “This is write skew because two transactions update different rows while relying on the same cross-row invariant. Under SERIALIZABLE, one transaction may fail instead of both committing the invalid state. The application should restart the whole transaction against a fresh snapshot.”

## Question 29 — Design a Concurrent Work Queue with SKIP LOCKED

**Difficulty:** Hard  
**Primary Topic(s):** Transactions, row locking, SKIP LOCKED  
**Integrated Topic(s):** Job queues, NOWAIT, deadlock prevention, advisory locks

### Interview Problem

You have:

```sql
CREATE TABLE work_items (
    work_id BIGINT PRIMARY KEY,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    payload JSONB
);
```

Twenty workers should claim ready jobs without processing the same row at the same time, and workers should not wait behind already-claimed tasks.

Design the claim SQL and explain how consistent lock ordering helps prevent deadlocks in multi-row workflows.

### What the Interviewer Is Testing

Whether you can design a practical concurrent worker-claim pattern and separate task claiming from long-running processing.

### Candidate Clarification Questions

- How many jobs should one worker claim at a time?
- When does a job become `running`?
- What happens if a worker crashes after claiming?
- How long can the claim transaction hold locks?

### Recommended Thinking Process

1. Select a bounded set of ready rows.
2. Lock them with `FOR UPDATE SKIP LOCKED`.
3. Mark them running in the same transaction.
4. Return the claimed work.
5. Commit quickly.
6. Process outside the claim transaction when safe.
7. Reclaim stale work with an explicit recovery policy.

### Solution

```sql
WITH next_jobs AS (
    SELECT work_id
    FROM work_items
    WHERE status = 'ready'
    ORDER BY created_at, work_id
    FOR UPDATE SKIP LOCKED
    LIMIT 10
)
UPDATE work_items AS w
SET status = 'running'
FROM next_jobs AS n
WHERE w.work_id = n.work_id
RETURNING w.*;
```

`SKIP LOCKED` tells a worker to skip rows another worker has already locked rather than waiting for them.

### Detailed Explanation

The claim transaction should be short. The lock protects the transition from `ready` to `running`, not the entire minutes-long processing task.

A classic deadlock is:

```text
A locks row 1
B locks row 2
A waits for row 2
B waits for row 1
```

A consistent rule such as “lock rows in ascending `work_id` order” reduces the chance of circular wait.

`NOWAIT` is a different policy: fail immediately if a conflicting lock cannot be acquired.

### Worked Example

Worker A locks jobs 101–110. Worker B runs the same claim query and skips those rows, selecting the next available jobs instead of waiting.

### Edge Cases

- Worker crashes after claim.
- A task remains `running` forever without recovery.
- Unbounded batch sizes increase lock duration.
- Multi-row updates performed in inconsistent order can deadlock.

### Common Wrong Approach

Using a single global table lock or holding row locks while performing external network calls.

### Production Considerations

Add stale-claim recovery, bounded batches, and monitoring of queue depth and claim age. `lock_timeout` can bound unexpected waits, while `statement_timeout` bounds statement duration. Advisory locks can coordinate singleton pipeline runs separately from row-level work claiming.

### Interviewer Follow-Up

1. When would `NOWAIT` be preferable?
2. How would you recover work after a crashed worker?
3. How would you ensure the same logical daily pipeline is not launched twice?

### Strong Interview Answer

> “I would claim a bounded batch in a short transaction using `FOR UPDATE SKIP LOCKED`, update those rows to `running`, return them, and commit. Processing happens after the claim lock is released. For multi-row workflows I would lock resources in a consistent order to reduce deadlocks and define recovery for abandoned claims.”

## Question 30 — Design an Idempotent Incremental Load with Deletes

**Difficulty:** Hard  
**Primary Topic(s):** Incremental loading, upsert, deletes  
**Integrated Topic(s):** Staging, deduplication, `IS DISTINCT FROM`, idempotency, Type 1/2 awareness

### Interview Problem

A daily CDC feed contains duplicate updates and tombstones:

```text
customer_id | operation | updated_at          | email          | status
------------+-----------+---------------------+----------------+--------
10          | upsert    | 09:00               | a@example.com  | active
10          | upsert    | 09:05               | a2@example.com | active
11          | delete    | 10:00               | NULL           | NULL
12          | upsert    | 08:00               | c@example.com  | active
```

Design an idempotent current-state load. Explain hard delete, soft delete, and tombstone semantics, and explain when Type 1 versus Type 2 is appropriate.

### What the Interviewer Is Testing

Whether you can integrate staging, validation, source deduplication, change detection, delete handling, and replay safety.

### Candidate Clarification Questions

- What timestamp defines source ordering?
- Is one customer allowed multiple source records in the batch?
- What does a delete mean in the target?
- Does the business require historical versions?
- How will you prove a rerun is idempotent?

### Recommended Thinking Process

1. Stage raw changes without mutating the target.
2. Validate operation values and required keys.
3. Deduplicate to one winning event per customer.
4. Apply insert/update/delete semantics.
5. Use `IS DISTINCT FROM` for nullable change detection.
6. Protect the publication with an appropriate transaction.
7. Reconcile and replay the same batch.

### Solution

```sql
WITH ranked AS (
    SELECT
        s.*,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY updated_at DESC, ingestion_id DESC
        ) AS rn
    FROM staging_customer_cdc AS s
),
deduped AS (
    SELECT *
    FROM ranked
    WHERE rn = 1
)
MERGE INTO customer_current AS t
USING deduped AS s
ON t.customer_id = s.customer_id
WHEN MATCHED AND s.operation = 'delete' THEN
    DELETE
WHEN MATCHED AND s.operation = 'upsert'
 AND (
       t.email IS DISTINCT FROM s.email
    OR t.status IS DISTINCT FROM s.status
 ) THEN
    UPDATE SET
        email = s.email,
        status = s.status
WHEN NOT MATCHED AND s.operation = 'upsert' THEN
    INSERT (customer_id, email, status)
    VALUES (s.customer_id, s.email, s.status);
```

### Detailed Explanation

Type 1 means current state replaces prior state. Type 2 means historical changes are preserved as versions.

A hard delete removes the current row. A soft delete marks the row deleted. A tombstone is often an explicit delete event retained in the change stream even when the current-state representation removes or marks the entity.

Idempotency means applying the same logical batch again leaves the durable state unchanged. That requires deterministic source selection and NULL-safe comparisons, not merely “the query can be rerun without a syntax error.”

### Worked Example

Customer 10's 09:05 event wins over 09:00. Customer 11 follows the selected delete semantics. Customer 12 is inserted. Replaying the same deduplicated input should not create an additional state change.

### Edge Cases

- A delete can arrive before the corresponding insert.
- Source ordering may be ambiguous if timestamps tie.
- NULL changes must be handled explicitly.
- A retry after partial work requires safe transaction boundaries.

### Common Wrong Approach

Processing every CDC event in arrival order and assuming the latest arrival is the correct business state.

### Production Considerations

Stage and validate first. Index the merge key. Avoid rewriting unchanged rows. For large workloads, scope processing by batch or partition when the data model permits it.

### Interviewer Follow-Up

1. How would you prove idempotency using `EXCEPT`?
2. What changes if the target must preserve history?
3. When could a full refresh be simpler?

### Strong Interview Answer

> “I treat the CDC load as state reconciliation: stage, validate, deduplicate, then apply explicit insert, update, and delete rules. `IS DISTINCT FROM` handles NULL-safe changes. If history is required I use Type 2; otherwise Type 1 keeps current state only. Finally I replay the batch and prove that durable state is unchanged.”

# Part IV — Advanced

## Question 31 — Production Incident: Revenue Inflation, Join Explosion, and Reconciliation

**Difficulty:** Advanced  
**Primary Topic(s):** Joins, aggregation, reconciliation  
**Integrated Topic(s):** Fan traps, historical dimensions, range joins, performance

### Interview Problem

A production revenue dashboard is suddenly 18% higher than the trusted financial source. The query joins:

```text
orders
→ order_lines
→ payments
→ refunds
→ customer_segment_history
```

Some child tables are one-to-many, and the customer segment table contains multiple historical versions per customer.

You are the Senior Data Engineer on call. Walk through how you would diagnose the incident, repair the SQL, and prove the corrected result reconciles.

### What the Interviewer Is Testing

Whether you can debug a production metric by following grain and cardinality through every join, then validate both correctness and historical semantics.

### Candidate Clarification Questions

- What is the intended output grain?
- Which columns are unique on each input?
- Is the segment needed “as it is now” or “as it was when the order happened”?
- Can payments/refunds/lines contain duplicate business records?
- What source totals are the trusted reconciliation baseline?

### Recommended Thinking Process

1. Reproduce on a small affected time range.
2. State the grain of every input.
3. Measure row counts and distinct keys after each join.
4. Identify the first stage where multiplication appears.
5. Pre-aggregate independent child facts to order grain.
6. Ensure the dimension contributes at most one effective row per order.
7. Reconcile counts, keys, and financial sums.
8. Only after correctness is restored, inspect the physical plan for performance.

### Solution

Build explicit order-grain aggregates:

```sql
WITH base_orders AS (
    SELECT *
    FROM orders
    WHERE order_ts >= :start_ts
      AND order_ts <  :end_ts
),
line_totals AS (
    SELECT order_id, SUM(extended_amount) AS item_revenue
    FROM order_lines
    GROUP BY order_id
),
payment_totals AS (
    SELECT order_id, SUM(amount) AS payment_amount
    FROM payments
    GROUP BY order_id
),
refund_totals AS (
    SELECT order_id, SUM(amount) AS refund_amount
    FROM refunds
    GROUP BY order_id
),
order_grain AS (
    SELECT
        o.order_id,
        o.customer_id,
        o.order_ts,
        COALESCE(l.item_revenue, 0) AS item_revenue,
        COALESCE(p.payment_amount, 0) AS payment_amount,
        COALESCE(r.refund_amount, 0) AS refund_amount
    FROM base_orders AS o
    LEFT JOIN line_totals AS l ON l.order_id = o.order_id
    LEFT JOIN payment_totals AS p ON p.order_id = o.order_id
    LEFT JOIN refund_totals AS r ON r.order_id = o.order_id
)
SELECT *
FROM order_grain;
```

If the historical dimension is needed as of order time, join it by effective range:

```sql
SELECT
    o.order_id,
    o.customer_id,
    o.order_ts,
    d.segment
FROM order_grain AS o
JOIN customer_segment_history AS d
  ON d.customer_id = o.customer_id
 AND o.order_ts >= d.valid_from
 AND o.order_ts <  d.valid_to;
```

A PostgreSQL `LATERAL` lookup or a DuckDB `ASOF JOIN` can be appropriate for other as-of lookup shapes where taught.

### Detailed Explanation

If one order has 4 lines, 2 payments, 2 refunds, and 3 overlapping dimension rows, a naïve join can create up to:

```text
4 × 2 × 2 × 3 = 48 rows
```

The repair must happen before the final aggregation. The dimension join is a separate correctness concern: a historical dimension should contribute one effective version for the fact's timestamp.

Useful invariants include:

```text
rows = distinct order_id
one effective dimension version per order
repaired source revenue = trusted revenue
missing keys = 0
extra keys = 0
```

### Worked Example

An order with 3 lines, 2 payments, and 2 refunds can create 12 child combinations before even considering the dimension. The repaired relation has one row per order before the dimension enrichment.

### Edge Cases

- Overlapping historical dimension versions.
- Missing dimension versions.
- Duplicate child business keys.
- Missing payments or refunds.
- A report asking for current rather than point-in-time attributes.

### Common Wrong Approach

Using `DISTINCT` to make the final row count look correct. That does not undo repeated financial measures or historical multiplicity.

### Production Considerations

Treat the dashboard as a correctness incident. Preserve evidence from the failing query and plan, repair the grain, add assertions, reconcile to trusted totals, then optimize. Partition-scoped checks can make large reconciliations operationally feasible.

### Interviewer Follow-Up

1. Which join would you inspect first?
2. How would you identify orders matching multiple history rows?
3. How would you prove the repaired query is idempotent?

### Strong Interview Answer

> “I would map grain and cardinality after every join. Independent one-to-many children create a fan trap, and historical dimensions can multiply rows if their effective ranges overlap. I would pre-aggregate children, enforce one point-in-time dimension match, then reconcile row counts, keys, and financial totals before optimizing.”

## Question 32 — Recursive Hierarchy with Cycle Protection

**Difficulty:** Advanced  
**Primary Topic(s):** Recursive CTEs, self-joins  
**Integrated Topic(s):** Hierarchy traversal, depth, path, cycle protection

### Interview Problem

An `employees` table has:

```text
employee_id
manager_id
name
```

Write a recursive CTE that returns every employee with:

```text
employee_id
name
depth
path
root_employee_id
```

The path should list manager-to-employee IDs. Explain how you prevent a cycle such as `1 → 2 → 3 → 1`.

### What the Interviewer Is Testing

Whether you understand recursive CTEs as controlled graph expansion and explicitly design for termination.

### Candidate Clarification Questions

- What defines a root?
- What is the output grain?
- What should happen to orphaned employees?
- What is the maximum expected depth?
- How should cycles be handled?

### Recommended Thinking Process

1. Anchor at employees with `manager_id IS NULL`.
2. Recursively join children to their current manager.
3. Track depth.
4. Track the full path.
5. Reject a child already present in the path.
6. Allow recursion to stop when no new children match.

### Solution

```sql
WITH RECURSIVE org AS (
    SELECT
        e.employee_id,
        e.name,
        0 AS depth,
        ARRAY[e.employee_id] AS path,
        e.employee_id AS root_employee_id
    FROM employees AS e
    WHERE e.manager_id IS NULL

    UNION ALL

    SELECT
        child.employee_id,
        child.name,
        org.depth + 1,
        org.path || child.employee_id,
        org.root_employee_id
    FROM org
    JOIN employees AS child
      ON child.manager_id = org.employee_id
    WHERE NOT child.employee_id = ANY(org.path)
)
SELECT
    employee_id,
    name,
    depth,
    path,
    root_employee_id
FROM org
ORDER BY root_employee_id, path;
```

### Detailed Explanation

A recursive CTE has two parts:

```text
anchor member
    ↓
recursive member
    ↓
recursive expansion
```

The anchor creates the roots. Each recursive step adds one level of descendants.

The path serves two purposes: it is useful output and it prevents revisiting a node. Without a cycle guard, cyclic data can cause non-termination or uncontrolled growth.

### Worked Example

For:

```text
1
└── 2
    └── 3
```

the paths are:

```text
[1]
[1,2]
[1,2,3]
```

with depths 0, 1, and 2.

### Edge Cases

- An employee points to a missing manager.
- A cycle has no root and may not be reached from root-based traversal.
- Multiple parents can create multiple paths.
- Very deep trees can make recursive state large.

### Common Wrong Approach

Writing a recursive query with no cycle guard and assuming the source data is always a tree.

### Production Considerations

Add data-quality checks for invalid foreign-key relationships and unexpected multiple paths. The recursive query should be tested against cyclic, orphaned, and deep inputs.

### Interviewer Follow-Up

1. How would you start from a selected employee instead of roots?
2. How could you identify cycles explicitly?
3. Can the same pattern traverse arbitrary graph edges?

### Strong Interview Answer

> “I use the null-manager employees as the anchor, recursively join children, and carry both depth and path. The path allows me to reject any child already visited, giving the query an explicit cycle-protection and termination mechanism.”

## Question 33 — Senior Query Tuning: From EXPLAIN ANALYZE to a Validated Fix

**Difficulty:** Advanced  
**Primary Topic(s):** EXPLAIN ANALYZE, indexes, joins  
**Integrated Topic(s):** Sargability, statistics, partition pruning, aggregate performance

### Interview Problem

A production query degraded from 2 seconds to 45 seconds:

```sql
SELECT
    o.customer_id,
    DATE_TRUNC('month', o.created_at) AS month,
    SUM(o.amount) AS revenue
FROM orders o
JOIN customers c
  ON c.customer_id = o.customer_id
WHERE DATE(o.created_at) = DATE '2026-09-28'
  AND c.country = 'India'
GROUP BY o.customer_id, DATE_TRUNC('month', o.created_at);
```

The plan shows a large sequential scan and a nested loop with high actual row counts.

Describe your complete tuning process and give a plausible corrected SQL shape. Do not assume the index is automatically the answer.

### What the Interviewer Is Testing

Whether you use evidence-driven performance engineering rather than random index changes.

### Candidate Clarification Questions

- What timezone defines the date?
- How selective is the country filter?
- Is `orders` partitioned?
- Where are estimated and actual rows most different?
- Which node consumes the most time and buffers?

### Recommended Thinking Process

1. Capture a baseline using `EXPLAIN (ANALYZE, BUFFERS)`.
2. Identify non-sargable predicates.
3. Inspect cardinality estimates.
4. Rewrite the time filter as a half-open range.
5. Evaluate the join strategy and table statistics.
6. Consider indexes or partition pruning based on evidence.
7. Change one thing.
8. Re-run the same representative workload.

### Solution

A more sargable shape is:

```sql
SELECT
    o.customer_id,
    DATE_TRUNC('month', o.created_at) AS month,
    SUM(o.amount) AS revenue
FROM orders AS o
JOIN customers AS c
  ON c.customer_id = o.customer_id
WHERE o.created_at >= TIMESTAMPTZ '2026-09-28 00:00:00+00'
  AND o.created_at <  TIMESTAMPTZ '2026-09-29 00:00:00+00'
  AND c.country = 'India'
GROUP BY o.customer_id, DATE_TRUNC('month', o.created_at);
```

Then inspect:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT ...;
```

The exact index or partitioning strategy should be selected from the observed plan and workload, not from the SQL text alone.

### Detailed Explanation

The tuning loop is:

```text
measure
→ inspect plan
→ form hypothesis
→ change one thing
→ measure again
```

If a plan estimates 20,000 rows but sees 30 million, the optimizer may choose a poor join strategy because its cost model is based on bad cardinality assumptions. Refreshing statistics and investigating skew can matter more than adding a new index.

A sequential scan can be correct when a large fraction of the table is needed. Likewise, a nested loop can be excellent for a highly selective outer relation and small inner results.

### Worked Example

Imagine the query's date filter matches 0.3% of orders. A selective access path can be valuable. If it matches 70%, scanning the table may be reasonable.

### Edge Cases

- Data distribution changed but statistics were not refreshed.
- A type mismatch changes selectivity or prevents an efficient operator.
- Partition pruning is unavailable because of the predicate form.
- An index is used but the query remains slow because of the join/aggregate work.

### Common Wrong Approach

Creating several indexes immediately and declaring success because one appears in the plan. The plan must be compared against the baseline and the actual business query measured.

### Production Considerations

Use `pg_stat_statements` awareness to identify recurring expensive queries and `auto_explain` awareness to capture useful plans. For large time-based tables, also consider partition pruning and physical data layout rather than assuming B-tree indexes solve every analytical workload.

### Interviewer Follow-Up

1. Why might a sequential scan still be the right choice?
2. What does a large estimate/actual mismatch tell you?
3. What would you inspect in `BUFFERS`?

### Strong Interview Answer

> “I would baseline the exact workload with `EXPLAIN ANALYZE (BUFFERS)`, identify the largest estimate errors and non-sargable predicates, rewrite the time filter, then test indexing or partition pruning based on evidence. I would make one change at a time and re-measure the same workload.”

## Question 34 — Concurrency Incident: Lost Update, Locks, and Retry Semantics

**Difficulty:** Advanced  
**Primary Topic(s):** Transactions, MVCC, row locks  
**Integrated Topic(s):** Lost updates, SERIALIZABLE, deadlocks, advisory locks

### Interview Problem

Two workers run the same customer-balance job concurrently. Sometimes one worker overwrites the other's change; other times the application reports a serialization failure.

As the incident owner, explain how you distinguish:

- lost update;
- blocking;
- serialization failure;
- deadlock.

Then propose a transaction pattern and retry policy.

### What the Interviewer Is Testing

Whether you can classify concurrency failures correctly and design recovery semantics rather than treating all database errors as interchangeable.

### Candidate Clarification Questions

- Which isolation level is configured?
- Are the operations additive or replacement-style?
- Which rows are locked?
- Can workers process the same logical batch?
- Is singleton execution required?

### Recommended Thinking Process

1. Draw a two-session timeline.
2. Separate visibility from blocking.
3. Determine whether the final state is wrong, a transaction is waiting, the engine aborted a transaction, or a circular wait exists.
4. Select the smallest coordination mechanism that protects the invariant.
5. Retry the complete transaction only for retryable concurrency failures.

### Solution

If the operation is a read-dependent state transition, use a short transaction with an explicit row lock:

```sql
BEGIN;

SELECT customer_id, status
FROM customer_state
WHERE customer_id = :customer_id
FOR UPDATE;

-- make the business decision

UPDATE customer_state
SET status = :new_status
WHERE customer_id = :customer_id;

COMMIT;
```

For an invariant requiring serializable behavior, use `SERIALIZABLE` and retry the entire transaction after a serialization failure.

For singleton pipeline coordination, a PostgreSQL advisory lock can provide an application-defined mutex around a logical job key.

### Detailed Explanation

A lost update is an incorrect final state caused by concurrent read-modify-write behavior. Blocking means one transaction is waiting on a lock held by another. A serialization failure is an explicit abort because the concurrent execution cannot be serialized safely. A deadlock is circular waiting:

```text
A → waits for B
B → waits for A
```

PostgreSQL resolves a detected deadlock by aborting one participant.

Retry semantics must be transaction-level. Retrying only one statement can violate the original read/decision/write logic.

### Worked Example

If both sessions read balance 100 and then write 110 and 120 based on stale state, a final balance of 120 is a lost update when the intended operation was additive.

### Edge Cases

- A retry can duplicate external side effects if the transaction is not the whole unit of work.
- Long transactions increase lock duration and cleanup pressure.
- DDL can block behind incompatible locks.
- Inconsistent lock ordering can create deadlocks.

### Common Wrong Approach

Using SERIALIZABLE everywhere without measuring or adding retry logic, or assuming a transaction alone prevents lost updates.

### Production Considerations

Keep transactions short, use consistent lock ordering, use `lock_timeout` and `statement_timeout` for operational containment, and make retried work idempotent. Use advisory locks only for resources that need application-level singleton coordination.

### Interviewer Follow-Up

1. How does MVCC explain concurrent reader/writer visibility?
2. When would `NOWAIT` be useful?
3. How would you investigate a deadlock after the incident?

### Strong Interview Answer

> “First I classify the symptom. Lost update means wrong final state, blocking means waiting, serialization failure means the database aborted a transaction under stronger isolation, and deadlock means circular wait. I then choose atomic updates or row locks for row invariants, SERIALIZABLE plus whole-transaction retries for stronger cross-row invariants, and advisory locks for singleton coordination.”

## Question 35 — Senior Work-Queue Design with SKIP LOCKED

**Difficulty:** Advanced  
**Primary Topic(s):** Transactions, row locking, SKIP LOCKED  
**Integrated Topic(s):** Retryable workers, stale claims, idempotency, deadlocks

### Interview Problem

You have 1,000,000 pending ingestion tasks and 20 concurrent workers.

Requirements:

- no two workers claim the same task at the same time;
- workers should not wait behind already-claimed tasks;
- a crashed worker's tasks must become retryable;
- claiming must be fast and short-lived;
- processing must not hold task locks for minutes.

Design the claim pattern and explain the task state machine.

### What the Interviewer Is Testing

Whether you can turn the row-locking concepts into a production work-queue protocol.

### Candidate Clarification Questions

- How many tasks should a worker claim in one transaction?
- What states exist?
- How is claim time recorded?
- How are stale claims recovered?
- What makes task processing idempotent?

### Recommended Thinking Process

1. Claim a bounded batch with `FOR UPDATE SKIP LOCKED`.
2. Mark those rows `running` in the same transaction.
3. Commit immediately.
4. Process outside the lock-holding transaction.
5. Recover stale `running` rows according to a lease/timeout policy.
6. Ensure processing can be safely retried.

### Solution

```sql
WITH next_tasks AS (
    SELECT task_id
    FROM ingestion_tasks
    WHERE status = 'ready'
    ORDER BY created_at, task_id
    FOR UPDATE SKIP LOCKED
    LIMIT 50
)
UPDATE ingestion_tasks AS t
SET status = 'running',
    claimed_at = CURRENT_TIMESTAMP
FROM next_tasks AS n
WHERE t.task_id = n.task_id
RETURNING t.task_id, t.payload, t.claimed_at;
```

A simple state model is:

```text
ready → running → succeeded
                  ↘ failed/retry
running (stale) → ready
```

### Detailed Explanation

`SKIP LOCKED` lets workers choose available work without waiting on rows another worker has already claimed.

The critical design choice is to separate **claim** from **process**. The claim transaction protects ownership of the task. Once committed, the worker can perform longer operations without holding the queue row lock.

Crash recovery requires a rule for abandoned `running` tasks. That can use `claimed_at` plus a carefully defined lease policy.

### Worked Example

Worker 1 claims tasks 1–50. Worker 2 skips those locked rows and claims another available batch. They do not need to wait for one another's claim transactions.

### Edge Cases

- Worker crashes after claiming.
- Two recovery processes try to reclaim the same stale row.
- A task runs for longer than the lease duration.
- The same task is retried after a partial external side effect.

### Common Wrong Approach

Holding the task lock while running external API calls, or assuming SKIP LOCKED alone guarantees exactly-once external processing.

### Production Considerations

Monitor claim age, retries, queue depth, transaction duration, and stale leases. Keep worker actions idempotent. Use consistent lock ordering whenever one transaction needs multiple resources.

### Interviewer Follow-Up

1. How would you recover a crashed worker?
2. What if the same task is delivered twice?
3. Why is processing outside the claim transaction usually preferable?

### Strong Interview Answer

> “I would use a short claim transaction with `FOR UPDATE SKIP LOCKED`, update tasks to `running`, commit, and then process outside the lock. A stale-claim recovery rule makes crashed work retryable, and idempotent processing protects against duplicate execution.”

## Question 36 — Production Daily Upsert: Stage → Validate → Deduplicate → Apply

**Difficulty:** Advanced  
**Primary Topic(s):** Staging, validation, deduplication, upsert  
**Integrated Topic(s):** `IS DISTINCT FROM`, `ON CONFLICT`, reconciliation, idempotency

### Interview Problem

You own a daily customer snapshot feed. It can contain:

- duplicate business keys;
- NULL changes;
- invalid status values;
- late records;
- unchanged rows.

Design the SQL pipeline from raw staging to current-state target. Your answer must include validation, deterministic deduplication, a PostgreSQL upsert, and a proof strategy for reruns.

### What the Interviewer Is Testing

Whether you can build a complete publication pipeline rather than stopping at a single upsert statement.

### Candidate Clarification Questions

- What is the source grain after deduplication?
- What field determines latest source state?
- Which statuses are legal?
- Are NULLs meaningful?
- What is the target key?
- What assertions prove success?

### Recommended Thinking Process

1. Land raw input.
2. Validate legal values and required keys.
3. Deduplicate to one row per customer.
4. Apply a change-only upsert.
5. Commit the publication unit.
6. Reconcile source/target.
7. Replay the same batch and verify that state is unchanged.

### Solution

```sql
WITH validated AS (
    SELECT *
    FROM staging_customer_snapshot
    WHERE customer_id IS NOT NULL
      AND status IN ('active', 'inactive')
),
ranked AS (
    SELECT
        v.*,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY source_updated_at DESC, ingestion_id DESC
        ) AS rn
    FROM validated AS v
),
deduped AS (
    SELECT *
    FROM ranked
    WHERE rn = 1
)
INSERT INTO customer_current (
    customer_id,
    email,
    status
)
SELECT
    customer_id,
    email,
    status
FROM deduped
ON CONFLICT (customer_id)
DO UPDATE SET
    email = EXCLUDED.email,
    status = EXCLUDED.status
WHERE customer_current.email IS DISTINCT FROM EXCLUDED.email
   OR customer_current.status IS DISTINCT FROM EXCLUDED.status;
```

Validation assertions should include:

```sql
SELECT customer_id
FROM deduped
GROUP BY customer_id
HAVING COUNT(*) > 1;
```

which must return zero rows.

### Detailed Explanation

The target is current-state only, so Type 1 semantics are appropriate. Staging isolates raw input from publication.

`ROW_NUMBER` provides one deterministic source survivor. `IS DISTINCT FROM` treats NULL-to-value and value-to-NULL as real changes while treating NULL-to-NULL as unchanged.

Idempotency should be validated by rerunning the same logical batch and comparing target state before and after the rerun.

### Worked Example

If customer 5 appears twice and the later record is chosen, only that record reaches the target. If the target already matches the surviving state, the change-only predicate skips the update.

### Edge Cases

- Source timestamp ties.
- Late records that arrive after newer records.
- Status values outside the approved set.
- Required key NULLs.
- A snapshot that omits a customer versus one that explicitly represents deletion.

### Common Wrong Approach

Applying raw staging directly to the target and hoping the upsert resolves duplicates.

### Production Considerations

Index the merge key, keep validation visible, and avoid unnecessary updates. For high-volume daily loads, scope work by batch and reconcile at useful partitions when possible.

### Interviewer Follow-Up

1. How would you handle snapshot deletions?
2. How would you detect a sudden spike in duplicate source keys?
3. How would you benchmark the load at 10× the current volume?

### Strong Interview Answer

> “I separate ingestion from publication. I validate the staging data, deduplicate to one row per business key using deterministic ordering, then perform a change-only `ON CONFLICT` upsert with NULL-safe comparisons. Finally I reconcile and replay the same batch to prove idempotency.”

## Question 37 — MERGE Incident: Duplicate Source Keys and a Nondeterministic Survivor

**Difficulty:** Advanced  
**Primary Topic(s):** MERGE, source deduplication  
**Integrated Topic(s):** ROW_NUMBER, deterministic ordering, delete semantics, assertions

### Interview Problem

A PostgreSQL MERGE intermittently fails:

```sql
MERGE INTO customer_current t
USING customer_stage s
ON t.customer_id = s.customer_id
WHEN MATCHED THEN
    UPDATE SET
        email = s.email,
        status = s.status
WHEN NOT MATCHED THEN
    INSERT (customer_id, email, status)
    VALUES (s.customer_id, s.email, s.status);
```

The staging table can contain multiple rows for one customer. An engineer adds `SELECT DISTINCT`, but failures continue and the selected survivor changes between runs.

Diagnose both problems and build a deterministic merge source.

### What the Interviewer Is Testing

Whether you understand that exact duplicate removal is different from business-key deduplication and that deterministic survivor selection is a correctness requirement.

### Candidate Clarification Questions

- What is the merge key?
- Which source event wins?
- Can timestamps tie?
- Is there a stable ingestion sequence?
- Are delete/tombstone operations possible?

### Recommended Thinking Process

1. `DISTINCT` only removes complete-row duplicates.
2. The MERGE source must be one row per target key.
3. Encode an explicit survivor ordering.
4. Use `ROW_NUMBER()`.
5. Assert zero duplicate merge keys.
6. Then perform MERGE.

### Solution

```sql
WITH ranked AS (
    SELECT
        s.*,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY
                source_priority DESC,
                effective_at DESC NULLS LAST,
                completeness_score DESC,
                ingestion_id DESC
        ) AS rn
    FROM customer_stage AS s
),
merge_source AS (
    SELECT *
    FROM ranked
    WHERE rn = 1
)
MERGE INTO customer_current AS t
USING merge_source AS s
ON t.customer_id = s.customer_id
WHEN MATCHED AND (
       t.email IS DISTINCT FROM s.email
    OR t.status IS DISTINCT FROM s.status
) THEN
    UPDATE SET
        email = s.email,
        status = s.status
WHEN NOT MATCHED THEN
    INSERT (customer_id, email, status)
    VALUES (s.customer_id, s.email, s.status);
```

Pre-merge assertion:

```sql
SELECT customer_id
FROM merge_source
GROUP BY customer_id
HAVING COUNT(*) > 1;
```

must return zero rows.

### Detailed Explanation

Two rows can share the same `customer_id` while differing in email or status. `DISTINCT` sees them as different complete rows, but the target business key sees them as competing source representations of one entity.

`ROW_NUMBER` selects one row only after the business survivor order has been fully specified. If the ordering is incomplete, the survivor may be unstable.

### Worked Example

Two rows:

```text
42 | CRM | 09:00 | old@example.com | 100
42 | ERP | 09:00 | new@example.com | 101
```

If CRM has the higher `source_priority`, the CRM record wins despite the timestamp tie.

### Edge Cases

- Multiple rows tie on timestamp and source.
- A tombstone competes with an upsert.
- An audit column changes but business values do not.
- Source ordering is not authoritative.

### Common Wrong Approach

Using `DISTINCT` and assuming the database will pick one business-key row. Another mistake is using `RANK() = 1`, which can return multiple tied rows.

### Production Considerations

Make the survivor policy reviewable. If the business cannot define which row wins, SQL cannot invent a correct rule. Track duplicate source-key rates as a load-quality metric.

### Interviewer Follow-Up

1. What if the ordering still ties after `ingestion_id`?
2. How would you handle tombstones?
3. How does the answer change in DuckDB or another warehouse dialect?

### Strong Interview Answer

> “MERGE requires a deterministic source grain. `DISTINCT` is not business-key deduplication. I would rank source rows by an explicit survivor policy, keep `ROW_NUMBER() = 1`, assert zero duplicate keys, and only then perform the MERGE.”

## Question 38 — Implement and Validate SCD Type 2

**Difficulty:** Advanced  
**Primary Topic(s):** SCD Type 2, valid_from, valid_to, is_current  
**Integrated Topic(s):** Surrogate keys, half-open intervals, transactions, integrity assertions

### Interview Problem

Design a PostgreSQL customer dimension:

```text
customer_sk
customer_id
segment
valid_from
valid_to
is_current
```

Customer 10 changes from Bronze to Silver at `2026-09-28 10:00 UTC`.

Implement the change while preserving history. Include a transaction boundary and assertions for:

- exactly one current row;
- no overlapping ranges;
- valid interval ordering.

Then explain when a periodic snapshot table might be simpler than SCD2.

### What the Interviewer Is Testing

Whether you can change historical state atomically and validate the resulting timeline.

### Candidate Clarification Questions

- Is `customer_id` the business key?
- What identifies a dimension version?
- Are intervals half-open?
- What value represents “current” in `valid_to`?
- What happens if the new segment is identical to the current one?

### Recommended Thinking Process

1. State the dimension grain: one row per customer version.
2. Lock the current version for the customer.
3. Compare tracked attributes.
4. Expire the current row at the new effective timestamp.
5. Insert the new version.
6. Commit both actions atomically.
7. Run structural assertions.

### Solution

```sql
BEGIN;

SELECT customer_sk, segment, valid_from, valid_to
FROM dim_customer
WHERE customer_id = 10
  AND is_current
FOR UPDATE;

UPDATE dim_customer
SET
    valid_to = TIMESTAMPTZ '2026-09-28 10:00:00+00',
    is_current = false
WHERE customer_id = 10
  AND is_current;

INSERT INTO dim_customer (
    customer_sk,
    customer_id,
    segment,
    valid_from,
    valid_to,
    is_current
)
VALUES (
    :new_customer_sk,
    10,
    'Silver',
    TIMESTAMPTZ '2026-09-28 10:00:00+00',
    NULL,
    true
);

COMMIT;
```

Exactly-one-current assertion:

```sql
SELECT customer_id
FROM dim_customer
GROUP BY customer_id
HAVING COUNT(*) FILTER (WHERE is_current) <> 1;
```

Interval ordering/continuity assertion:

```sql
WITH ordered AS (
    SELECT
        customer_id,
        valid_from,
        valid_to,
        LEAD(valid_from) OVER (
            PARTITION BY customer_id
            ORDER BY valid_from
        ) AS next_valid_from
    FROM dim_customer
)
SELECT *
FROM ordered
WHERE valid_from >= COALESCE(valid_to, 'infinity'::timestamptz)
   OR (
        valid_to IS NOT NULL
        AND next_valid_from IS NOT NULL
        AND valid_to <> next_valid_from
      );
```

The continuity check is intentionally strict: a closed historical interval should end exactly where the next interval starts. A separate policy may allow gaps, but then that should be an explicit business rule.

### Detailed Explanation

SCD2 changes the grain from one row per customer to one row per customer version.

Half-open intervals are especially useful:

```text
[Jan 1, Sep 28 10:00)
[Sep 28 10:00, infinity)
```

A fact at exactly `Sep 28 10:00` belongs to the new version.

The transaction protects the invariant that the old row is expired and the new row exists together. `FOR UPDATE` prevents two concurrent changes from both trying to replace the same current row.

A snapshot table may be simpler when the business needs periodic “as of snapshot date” states rather than continuous effective-dated history.

### Worked Example

Before:

```text
10 | Bronze | Jan 1 | NULL | true
```

After:

```text
10 | Bronze | Jan 1      | Sep 28 10:00 | false
10 | Silver | Sep 28 10:00 | NULL         | true
```

### Edge Cases

- Unchanged segment should not create a new version.
- Two concurrent changes target the same customer.
- A late-arriving change is earlier than the current `valid_from`.
- Existing history already contains a gap or overlap.

### Common Wrong Approach

Updating the current row's segment in place and losing history, or inserting a new version without expiring the old one.

### Production Considerations

Consider a uniqueness rule for the current row where supported, plus zero-row assertion queries. Keep the transaction short and isolate affected business keys when processing batches.

### Interviewer Follow-Up

1. How would you handle a late-arriving change?
2. What would a point-in-time fact join look like?
3. How would you detect multiple current rows?

### Strong Interview Answer

> “SCD2 stores one row per customer version. For a change, I lock the current row, expire it at the new effective timestamp, insert the new version, and commit both steps together. I use half-open intervals and assert one current row plus valid interval continuity.”

## Question 39 — Repair a Late-Arriving SCD2 Change and Perform a Point-in-Time Join

**Difficulty:** Advanced  
**Primary Topic(s):** SCD2, LAG/LEAD, CTEs  
**Integrated Topic(s):** Late-arriving changes, historical resequencing, range repair, point-in-time joins

### Interview Problem

The current customer history is:

```text
customer_id | segment | valid_from | valid_to
------------+---------+------------+----------------
10          | Bronze  | Jan 1      | Apr 1
10          | Silver  | Apr 1      | NULL
```

A late event arrives:

```text
customer_id = 10
segment = Gold
effective_at = Feb 15
```

Design a safe repair and then show how an order at Feb 20 should join to the historical dimension.

### What the Interviewer Is Testing

Whether you can treat late-arriving history as interval reconstruction rather than as a simple append.

### Candidate Clarification Questions

- Is `effective_at` the authoritative business time?
- Can multiple changes share the same effective timestamp?
- Is there an ingestion sequence for ties?
- Is the existing dimension itself trusted?
- How should existing gaps/overlaps be treated?

### Recommended Thinking Process

1. Lock the affected customer's history.
2. Gather authoritative change points.
3. Reconstruct the timeline in deterministic order.
4. Use `LEAD` to derive end boundaries.
5. Mark exactly one final interval current.
6. Validate no overlap and intended continuity.
7. Join facts using half-open point-in-time predicates.

### Solution

The corrected timeline should be:

```text
Bronze [Jan 1, Feb 15)
Gold   [Feb 15, Apr 1)
Silver [Apr 1, infinity)
```

A repair workflow can reconstruct change points:

```sql
WITH change_points AS (
    SELECT customer_id, valid_from AS effective_at
    FROM dim_customer
    WHERE customer_id = 10

    UNION

    SELECT
        10,
        TIMESTAMPTZ '2026-02-15 00:00:00+00'
),
ordered_points AS (
    SELECT
        customer_id,
        effective_at,
        LEAD(effective_at) OVER (
            PARTITION BY customer_id
            ORDER BY effective_at
        ) AS next_effective_at
    FROM change_points
)
SELECT *
FROM ordered_points
ORDER BY customer_id, effective_at;
```

The segment value for each change point should come from the authoritative change history using its deterministic effective-time ordering. Then write the repaired intervals in one transaction.

A point-in-time join is:

```sql
SELECT
    o.order_id,
    o.customer_id,
    o.order_ts,
    d.segment
FROM orders AS o
JOIN dim_customer AS d
  ON d.customer_id = o.customer_id
 AND o.order_ts >= d.valid_from
 AND (
        d.valid_to IS NULL
        OR o.order_ts < d.valid_to
     );
```

### Detailed Explanation

The late event changes the past, so blindly inserting another current record is wrong. The affected customer's timeline must be resequenced.

`LEAD(valid_from)` is useful because each version's next start is its end boundary. Once the sequence of effective points is correct, the intervals are naturally derived.

The fact join is “as it was then,” not “as it is now.” An order at Feb 20 should match Gold because:

```text
Feb 20 >= Feb 15
AND
Feb 20 < Apr 1
```

### Worked Example

Order at Feb 20:

```text
Bronze → does not match because Feb 20 >= Apr 1 is false
Gold   → matches
Silver → does not match because Feb 20 >= Apr 1 is false
```

Therefore the historical segment is Gold.

### Edge Cases

- Multiple changes at the same effective timestamp.
- A late change before the first known boundary.
- A late change that lands exactly on an existing boundary.
- Pre-existing gaps/overlaps.
- A fact timestamp equal to an interval boundary.

### Common Wrong Approach

Joining facts with `is_current = true`. That returns the current state and answers a different business question.

### Production Considerations

Repair only the affected business keys when possible, hold a transaction that prevents conflicting concurrent history edits, and validate the full affected timeline before publication. Large historical repairs should be planned for lock duration and reconciliation.

### Interviewer Follow-Up

1. How would you assert there is no overlap after repair?
2. What if the history already contains a gap?
3. When could snapshots be simpler?

### Strong Interview Answer

> “A late-arriving change requires historical resequencing. I would rebuild the affected customer's effective timeline from authoritative change points, derive interval ends with `LEAD`, validate the SCD2 invariants, and then use a half-open point-in-time join so facts see the version that was valid at their event time.”

## Question 40 — Senior-Level Production SQL Pipeline Architecture

**Difficulty:** Advanced  
**Primary Topic(s):** Incremental loading, MERGE/upsert, SCD, transactions  
**Integrated Topic(s):** Validation, deduplication, reconciliation, performance, concurrency, retries

### Interview Problem

Design a production daily warehouse pipeline for customer and subscription data:

```text
source
  ↓
staging
  ↓
validation
  ↓
deduplication
  ↓
incremental merge/upsert
  ↓
SCD2 customer history
  ↓
point-in-time fact joins
  ↓
reconciliation
```

Constraints:

- source data can contain duplicate business keys;
- tombstones can appear;
- the same batch can be retried;
- multiple workers can operate concurrently;
- historical changes can arrive late;
- customer history must contain exactly one current row;
- financial metrics must not be inflated by joins;
- the load must remain performant as volume grows.

Walk through the architecture, SQL patterns, transaction boundaries, assertions, indexes, retry behavior, and trade-offs you would defend in a senior architecture interview.

### What the Interviewer Is Testing

Whether you can integrate the entire module into a coherent, production-safe SQL system and communicate the reasoning clearly.

### Candidate Clarification Questions

- What is the source grain?
- What is the target grain at each stage?
- Which timestamp is authoritative?
- Which operations are Type 1 and which require Type 2 history?
- What must be atomic?
- What is the trusted reconciliation source?
- Which operations can safely run concurrently?

### Recommended Thinking Process

1. Define grain and business keys for every stage.
2. Keep raw ingestion separate from target publication.
3. Validate before mutation.
4. Deduplicate source keys deterministically.
5. Apply current-state inserts/updates/deletes with NULL-safe change detection.
6. Build or repair SCD2 history transactionally.
7. Keep fact joins at the intended grain and use point-in-time logic where needed.
8. Reconcile counts, keys, and financial totals.
9. Make batch replay produce no durable difference.
10. Choose indexes from observed predicates and merge keys.
11. Separate claim/locking transactions from long-running processing.
12. Design retry behavior for serialization/deadlock failures.

### Solution

A production-oriented architecture is:

```text
Source
  ↓
Raw staging
  ↓
Validation
  ├─ required keys
  ├─ legal status/operation values
  └─ valid timestamp/state rules
  ↓
Deterministic deduplication
  └─ one source row per business key
  ↓
Current-state upsert / MERGE
  ├─ insert new
  ├─ update changed
  └─ delete/soft-delete tombstones
  ↓
SCD2 publication
  ├─ lock affected business keys
  ├─ expire current version
  └─ insert new version(s)
  ↓
Point-in-time fact join
  └─ fact_ts >= valid_from AND fact_ts < valid_to
  ↓
Reconciliation
  ├─ row counts
  ├─ distinct keys
  ├─ missing / extra rows
  ├─ changed rows
  └─ financial totals
  ↓
Idempotency replay
  └─ second identical run changes nothing
```

For a PostgreSQL current-state table, an upsert can use:

```sql
INSERT INTO customer_current (
    customer_id,
    email,
    status
)
SELECT
    customer_id,
    email,
    status
FROM deduped_source
ON CONFLICT (customer_id)
DO UPDATE SET
    email = EXCLUDED.email,
    status = EXCLUDED.status
WHERE customer_current.email IS DISTINCT FROM EXCLUDED.email
   OR customer_current.status IS DISTINCT FROM EXCLUDED.status;
```

Where MERGE better fits the source/target actions, make the same source-grain and determinism rules explicit.

SCD2 changes should expire the current row and insert the new version inside the transaction protecting that business key. Late changes require historical resequencing and point-in-time validation.

### Detailed Explanation

The senior-level insight is that this is a sequence of **invariants**, not one magical SQL statement.

Examples:

```text
staging invariant
→ required keys and legal states

dedup invariant
→ one source row per business key

current-state invariant
→ at most one target row per business key

SCD2 invariant
→ exactly one current row and valid non-overlapping ranges

fact metric invariant
→ one row at intended reporting grain

reconciliation invariant
→ source/target state agrees within defined semantics

retry invariant
→ replay produces the same durable state
```

Transactions should be scoped around coherent database invariants, not around minutes of external processing. A worker claim may use a short `FOR UPDATE SKIP LOCKED` transaction; long-running processing can happen after commit when the workflow is designed for it.

Performance follows the same reasoning loop:

```text
measure
→ inspect EXPLAIN ANALYZE
→ form hypothesis
→ change one thing
→ measure again
```

Index the real merge/join/filter keys. Preserve sargability for time filters. Use partition pruning when the layout and query support it. Avoid unnecessary updates because they increase write and maintenance cost.

Concurrency must distinguish blocking, deadlocks, lost updates, and serialization failures. Serialization failures should trigger a complete transaction retry, not an isolated statement retry.

PostgreSQL, DuckDB, and warehouse/lakehouse systems do not have identical DML or concurrency behavior, so engine-specific claims should be labeled rather than generalized.

### Worked Example

Suppose a batch has:

```text
customer 10 → two duplicate updates
customer 11 → unchanged
customer 12 → tombstone
```

The source stage chooses one deterministic survivor for 10. The current-state layer updates 10 only if tracked values changed, leaves 11 unchanged, and applies the selected delete semantics to 12. If 10 has a historical change, the SCD2 layer creates the new version and preserves the old interval. A second identical execution leaves the durable state unchanged.

### Edge Cases

- Late and out-of-order source events.
- NULL-to-value and value-to-NULL changes.
- Duplicate source keys with tied timestamps.
- Multiple current SCD2 rows.
- Overlapping history.
- Worker crashes after claiming a job.
- Serialization failures and deadlocks.
- A malformed join that multiplies financial measures.
- Large reconciliation workloads becoming a new bottleneck.

### Common Wrong Approach

Putting the entire daily pipeline inside one huge transaction and assuming that guarantees correctness. Large transaction scopes can increase lock duration and failure blast radius.

Another common mistake is optimizing before proving the output grain and reconciliation logic.

### Production Considerations

Use explicit assertions, short transaction boundaries, deterministic survivor rules, bounded work claims, consistent lock ordering, timeouts, retry-safe operations, and measurable execution plans. For singleton pipeline coordination, an advisory lock can guard the logical job key. For large workloads, partition-scoped processing and reconciliation can reduce operational pressure when consistent with the data model.

### Interviewer Follow-Up

1. What changes if the same batch is delivered twice?
2. Where would you use an advisory lock?
3. What assertions must pass before SCD2 publication commits?
4. How would you investigate a 10× slowdown after a volume increase?
5. What is the difference between “as it is now” and “as it was when the fact occurred”?
6. How would you prove the final financial totals were not inflated by joins?

### Strong Interview Answer

> “I would design the pipeline around grain and invariants: stage and validate first, deduplicate deterministically, then apply current-state changes and SCD2 changes inside appropriate short transactions. I would use `IS DISTINCT FROM` for NULL-safe change detection, point-in-time joins for historical facts, reconciliation and assertions for correctness, and EXPLAIN-based measurement for performance. For concurrency I would use row locks or SKIP LOCKED where appropriate, consistent lock ordering, advisory locks for singleton coordination, and whole-transaction retries for serialization failures. Finally, I would replay the batch and prove that the durable state is unchanged.”

# Final Interview Readiness Checklist

- [ ] I can explain SQL logical execution order.
- [ ] I understand NULL and three-valued logic.
- [ ] I can reason about join cardinality.
- [ ] I can diagnose join explosion.
- [ ] I can aggregate without changing the intended grain.
- [ ] I can use subqueries and CTEs.
- [ ] I can write recursive CTEs.
- [ ] I understand window functions and frames.
- [ ] I can solve gaps-and-islands and sessionisation problems.
- [ ] I can deduplicate deterministically.
- [ ] I can reconcile source and target datasets.
- [ ] I can design tables and constraints.
- [ ] I can choose appropriate data types.
- [ ] I can reason about indexes.
- [ ] I can read EXPLAIN ANALYZE.
- [ ] I can diagnose a slow SQL query.
- [ ] I understand transactions and isolation.
- [ ] I can explain MVCC.
- [ ] I can reason about row locks and SKIP LOCKED.
- [ ] I can identify and prevent deadlocks.
- [ ] I can write an idempotent upsert.
- [ ] I can explain MERGE.
- [ ] I can deduplicate MERGE sources.
- [ ] I can implement SCD Type 1.
- [ ] I can implement SCD Type 2.
- [ ] I can validate SCD2 integrity.
- [ ] I can handle late-arriving SCD2 changes.
- [ ] I can write point-in-time joins.
- [ ] I can discuss merge performance.
- [ ] I can defend a production SQL design in an interview.

## Final Coverage Audit

The curriculum is intentionally cumulative across Topics 01–10 rather than ten disconnected interview sets.

| Topic | Representative Questions |
|---|---|
| 01 — SELECT, filter, sort, NULL semantics | Q01–Q03, Q05, Q10, Q30 |
| 02 — Joins and join explosion | Q04, Q11, Q21, Q31, Q40 |
| 03 — Aggregation, GROUP BY, HAVING | Q05, Q11, Q12, Q14, Q26, Q31 |
| 04 — Subqueries and CTEs | Q06, Q12, Q15, Q23, Q31, Q32, Q39 |
| 05 — Window functions | Q07, Q08, Q13, Q22–Q25, Q32, Q39 |
| 06 — Set operations and deduplication | Q08, Q14, Q25, Q30, Q36, Q37, Q39 |
| 07 — DDL, constraints, data types | Q09, Q16, Q17, Q38, Q40 |
| 08 — Indexes and EXPLAIN | Q03, Q17, Q18, Q27, Q33, Q36, Q40 |
| 09 — Transactions, isolation, locking | Q19, Q28, Q29, Q34, Q35, Q38, Q40 |
| 10 — MERGE, upsert, and SCD | Q10, Q20, Q30, Q36–Q40 |

### Interview Question-Type Audit

This set intentionally includes:

- conceptual explanation;
- SQL writing;
- result prediction;
- debugging;
- data-quality diagnosis;
- reconciliation;
- performance tuning;
- concurrency timelines;
- incremental loading;
- SCD Type 1 and Type 2;
- late-arriving history repair;
- production architecture reasoning.

### Final Interview Practice Loop

For every SQL problem, practice:

```text
Clarify assumptions
→ state grain
→ predict row count
→ think aloud
→ write the smallest correct relation
→ validate with assertions
→ test edge cases
→ inspect EXPLAIN ANALYZE when relevant
→ discuss production behavior
→ give the concise verbal answer
```
