# 03 — Aggregation, GROUP BY, and HAVING

> **Module:** 2.6 — SQL for Data Engineers  
> **Phase:** A — Querying Correctly  
> **Primary engines:** PostgreSQL 16+ and DuckDB  
> **Core idea:** Aggregation changes the grain of a dataset. A correct metric requires correct grain, correct rows, correct NULL semantics, and a correct mathematical definition.

Aggregation is where raw rows become business information.

A table may contain millions of orders, events, payments, or measurements. A business usually does not want to inspect every raw row. It wants questions answered:

- How much revenue did we make?
- How many orders did we receive?
- How many customers purchased?
- What is the average order value?
- What is the p95 API latency?
- How many orders were completed?
- What was revenue by country and month?
- What is the payment success rate?
- What is the total across all regions and the subtotal for each region?

SQL aggregation answers these questions.

But aggregation is also one of the easiest places to produce **plausible but wrong metrics**.

A query can execute successfully while:

- grouping at the wrong grain,
- counting rows instead of entities,
- counting NULLs incorrectly,
- treating missing values as zero,
- calculating an average of averages,
- using the wrong denominator,
- aggregating after a join explosion,
- using integer division,
- overflowing a numeric type,
- using an approximate metric where an exact value is required,
- or misreading subtotal rows containing NULL markers.

The central skill in this chapter is therefore not memorizing `SUM()` or `GROUP BY`.

It is learning to reason:

```text
Input grain
    ↓
Rows included
    ↓
Grouping definition
    ↓
Output grain
    ↓
Metric definition
    ↓
NULL / edge-case behavior
    ↓
Numeric correctness
    ↓
Validation / reconciliation
```

---

# 1. Learning Objectives

By the end of this chapter, you should be able to:

- Explain what aggregation does to a dataset.
- Explain how `GROUP BY` changes the grain of the input.
- State the input grain and output grain before writing an aggregate query.
- Use:
  - `COUNT`
  - `SUM`
  - `AVG`
  - `MIN`
  - `MAX`
- Distinguish:
  - `COUNT(*)`
  - `COUNT(column)`
  - `COUNT(DISTINCT column)`
- Explain how aggregate functions behave with `NULL`.
- Explain the difference between an average over NULL values and an average over zeros.
- Explain what happens when `SUM()` receives no contributing rows.
- Use `COALESCE` intentionally around aggregates.
- Explain `WHERE` versus `HAVING`.
- Write conditional aggregations with `CASE WHEN`.
- Write conditional aggregations using `FILTER (WHERE ...)`.
- Build pivot-style reports with conditional aggregation.
- Understand DuckDB's `PIVOT` as a dialect-specific convenience.
- Use `STRING_AGG` and `ARRAY_AGG`.
- Make collection aggregates deterministic by ordering the values inside the aggregate.
- Calculate percentiles with `PERCENTILE_CONT` and `PERCENTILE_DISC` where supported.
- Explain `WITHIN GROUP`.
- Use `MODE` and `STDDEV` where supported.
- Use `GROUPING SETS`.
- Use `ROLLUP`.
- Use `CUBE`.
- Use `GROUPING()` to distinguish real NULLs from subtotal/grand-total markers.
- Explain approximate aggregation.
- Explain approximate distinct counting and the HyperLogLog idea.
- Decide when approximate results are acceptable.
- Avoid average-of-averages errors.
- Build correct ratio metrics from the right numerator and denominator.
- Use `NULLIF` to protect ratios from division by zero.
- Understand integer division.
- Understand aggregation precision and integer overflow.
- Choose `NUMERIC` versus `DOUBLE PRECISION` based on the data's semantics.
- Understand dialect conveniences such as `GROUP BY ALL`.
- Understand the risks of ordinal grouping such as `GROUP BY 1, 2`.
- Validate aggregate results with reconciliation and assertion queries.
- Debug incorrect metrics systematically.
- Defend aggregation logic during code reviews and technical interviews.

---

# 2. Why Aggregation Matters in Data Engineering

Aggregation is not merely a reporting feature.

It is part of the transformation layer of a data platform.

Typical analytical pipelines move through grains such as:

```text
raw events
    ↓
one row per event
    ↓
daily user metrics
    ↓
one row per user per day
    ↓
daily business metrics
    ↓
one row per day
    ↓
monthly reporting
    ↓
one row per month
```

Each aggregation changes what a row means.

That means an aggregation query is simultaneously:

1. a SQL query,
2. a grain transformation,
3. a metric definition,
4. and often a business contract.

---

## 2.1 Why this matters for Data Engineers

Aggregation powers:

- gold-layer tables,
- warehouse marts,
- KPI pipelines,
- finance reporting,
- operational dashboards,
- customer analytics,
- reconciliation,
- anomaly detection,
- quality checks,
- dimensional reporting.

Examples:

```text
SUM(revenue)
COUNT(orders)
COUNT(DISTINCT customer_id)
AVG(order_value)
PERCENTILE_CONT(...)
```

Each one encodes an assumption about:

- which rows matter,
- which values are missing,
- what one row represents,
- and what the result is supposed to mean.

---

## 2.2 A query can be syntactically correct and mathematically wrong

This is one of the most important production lessons.

Suppose:

```sql
SELECT
    customer_id,
    AVG(order_amount) AS average_order_value
FROM orders
GROUP BY customer_id;
```

This is valid SQL.

But the metric can still be wrong if `orders` was previously duplicated by an incorrect join.

Likewise:

```sql
AVG(country_conversion_rate)
```

can be valid SQL while being the wrong way to compute overall conversion.

Or:

```sql
SUM(amount)
```

can be valid SQL while using an inappropriate numeric type or including rows that should have been excluded.

The database checks SQL semantics.

It does not know your business definition unless you encode it.

---

# 3. The Core Mental Model: Aggregation Changes Grain

This is the central idea of the chapter.

> **Aggregation changes the grain of a dataset.**

Suppose the input table is:

```text
orders
```

with:

```text
one row per order
```

Now run:

```sql
SELECT
    customer_id,
    SUM(amount) AS total_spend
FROM orders
GROUP BY customer_id;
```

The result is:

```text
one row per customer
```

The grain changed.

---

## 3.1 Grain template

Before every important aggregation, write:

```text
Input grain:
Grouping columns:
Output grain:
Metric:
Rows contributing:
NULL behavior:
```

Example:

```text
Input grain:
one row per order

Grouping columns:
customer_id

Output grain:
one row per customer

Metric:
SUM(order_amount)

Rows contributing:
orders surviving WHERE

NULL behavior:
NULL order_amount values are ignored by SUM
```

This simple habit prevents many mistakes.

---

## 3.2 Adding a grouping column changes the grain again

Compare:

```sql
GROUP BY country
```

with:

```sql
GROUP BY country, month
```

The first means:

```text
one row per country
```

The second means:

```text
one row per country per month
```

Adding a grouping column generally makes groups more specific and can increase the number of output rows.

---

# 4. Row-Level Data vs Group-Level Data

Consider:

```text
orders

order_id | customer_id | country | amount
---------+-------------+---------+-------
101      | 1           | India   | 100
102      | 1           | India   | 200
103      | 2           | India   | 300
104      | 3           | Nepal   | 400
```

At the raw level:

```text
one row = one order
```

Now:

```sql
SELECT
    customer_id,
    SUM(amount) AS total_spend
FROM orders
GROUP BY customer_id;
```

Result:

```text
customer_id | total_spend
-------------+------------
1            | 300
2            | 300
3            | 400
```

Now:

```text
one row = one customer
```

The important transformation is:

```text
order grain
    ↓
GROUP BY customer_id
    ↓
customer grain
```

---

## 4.1 Why "grouping" is the right word

Conceptually, SQL partitions input rows into groups based on the grouping expressions.

For:

```sql
GROUP BY country
```

all rows with the same `country` value belong to one group.

Then:

```sql
SUM(amount)
COUNT(*)
AVG(amount)
```

operate within each group.

The final result contains one output row for each grouping combination.

---

# 5. COUNT

`COUNT` answers a family of different questions.

The most important variants are:

```sql
COUNT(*)
COUNT(column)
COUNT(DISTINCT column)
```

Do not treat them as interchangeable.

---

## 5.1 COUNT(*) — count rows

```sql
SELECT COUNT(*)
FROM orders;
```

This asks:

> How many rows are in the input relation after any earlier filters?

If there are 1,000 rows, the result is:

```text
1000
```

It does not matter whether individual columns contain NULLs.

---

## 5.2 COUNT(column) — count non-NULL values

```sql
SELECT COUNT(email)
FROM customers;
```

This asks:

> How many rows have a non-NULL `email` value?

Suppose:

```text
customer_id | email
------------+----------------
1           | a@example.com
2           | NULL
3           | b@example.com
4           | NULL
```

Then:

```text
COUNT(*)     = 4
COUNT(email) = 2
```

The distinction is fundamental.

---

## 5.3 COUNT(DISTINCT column)

```sql
SELECT COUNT(DISTINCT customer_id)
FROM orders;
```

This asks:

> How many distinct non-NULL customer IDs occur in the input?

For:

```text
customer_id
-----------
1
1
2
3
3
```

the answer is:

```text
3
```

This is often the right metric when the business question is about entities rather than rows.

---

# 6. COUNT(*), COUNT(column), COUNT(DISTINCT column)

Use this example:

```sql
CREATE TEMP TABLE count_demo (
    customer_id INTEGER,
    email TEXT,
    country TEXT
);

INSERT INTO count_demo
VALUES
    (1, 'a@example.com', 'India'),
    (2, NULL, 'India'),
    (3, 'a@example.com', 'Nepal'),
    (4, NULL, NULL);
```

Now:

```sql
SELECT
    COUNT(*) AS row_count,
    COUNT(email) AS non_null_email_count,
    COUNT(DISTINCT email) AS distinct_email_count,
    COUNT(country) AS non_null_country_count,
    COUNT(DISTINCT country) AS distinct_country_count
FROM count_demo;
```

Conceptually:

```text
row_count               = 4
non_null_email_count    = 2
distinct_email_count    = 1
non_null_country_count  = 3
distinct_country_count  = 2
```

The exact output display is engine-specific, but the semantics are the key lesson.

---

## 6.1 What should you count?

Ask the business question first.

### Question

> How many orders occurred?

Use:

```sql
COUNT(*)
```

### Question

> How many orders contain a populated coupon code?

Use:

```sql
COUNT(coupon_code)
```

### Question

> How many customers placed orders?

Use:

```sql
COUNT(DISTINCT customer_id)
```

These are three different metrics.

---

## 6.2 Production mistake: counting rows instead of entities

Suppose:

```text
100 orders
```

were placed by:

```text
20 customers
```

Then:

```sql
COUNT(*)
```

returns:

```text
100
```

while:

```sql
COUNT(DISTINCT customer_id)
```

returns:

```text
20
```

Calling the first number "customer count" would be a metric-definition error.

---

# 7. SUM

`SUM` adds the numeric values that contribute to a group.

```sql
SELECT
    SUM(amount) AS total_revenue
FROM orders;
```

If:

```text
100
200
300
```

are present, the result is:

```text
600
```

---

## 7.1 SUM and NULL

Suppose:

```text
amount
------
100
NULL
300
```

Then:

```sql
SELECT SUM(amount)
FROM orders;
```

returns:

```text
400
```

The NULL is ignored.

This does **not** mean SQL treated NULL as zero in a universal semantic sense.

A better mental model is:

> NULL does not contribute a known numeric value to the aggregate.

That distinction becomes important when reasoning about metrics.

---

## 7.2 SUM versus SUM(COALESCE(...))

Compare:

```sql
SUM(amount)
```

with:

```sql
SUM(COALESCE(amount, 0))
```

In many ordinary non-empty cases, both can produce the same numeric total because NULL amounts contribute nothing.

But they are not conceptually identical.

The explicit version says:

> For this metric, treat missing amount as zero.

That is a business decision.

Use it when that meaning is correct.

---

## 7.3 SUM of no rows

Suppose:

```sql
SELECT SUM(amount)
FROM orders
WHERE false;
```

No rows contribute.

For standard aggregate semantics, `SUM` returns NULL on an empty input rather than a numeric zero.

If the report's contract requires zero:

```sql
SELECT
    COALESCE(SUM(amount), 0) AS total_revenue
FROM orders
WHERE false;
```

Now the output is:

```text
0
```

This is often useful in reporting, but only when:

```text
"No contributing rows"
```

should be represented as:

```text
0
```

rather than:

```text
NULL
```

---

# 8. AVG

`AVG` calculates an average over the values that contribute.

For numeric data, conceptually:

```text
average
=
sum of contributing values
--------------------------
number of contributing values
```

NULL values do not contribute to the count used by the aggregate.

---

## 8.1 AVG with NULL

Input:

```text
amount
------
100
NULL
300
```

Then:

```sql
SELECT AVG(amount)
FROM orders;
```

Conceptually:

```text
(100 + 300) / 2
=
200
```

It is not:

```text
(100 + 0 + 300) / 3
=
133.33
```

because NULL is not automatically zero.

---

# 9. AVG: NULL vs Zero

This distinction is critical for metric engineering.

Consider:

```text
measurement
-----------
10
20
NULL
```

Interpretation A:

```text
NULL = measurement missing
```

Then:

```sql
AVG(measurement)
```

averages only known measurements:

```text
15
```

Interpretation B:

```text
0 = actual measured zero
```

Then:

```text
10
20
0
```

has an average of:

```text
10
```

Those represent different datasets.

---

## 9.1 Why replacing NULL with zero can be wrong

Suppose a payment system has:

```text
payment_fee
-----------
2.50
NULL
4.00
```

Maybe NULL means:

> Fee was not received from the source.

Replacing it with zero claims:

> The fee was definitely zero.

Those are not equivalent.

Use:

```sql
AVG(payment_fee)
```

when missing values should be excluded.

Use:

```sql
AVG(COALESCE(payment_fee, 0))
```

only when the business definition explicitly says missing means zero.

---

# 10. MIN and MAX

`MIN` and `MAX` return the smallest/largest contributing value.

Examples:

```sql
SELECT
    MIN(amount) AS minimum_order,
    MAX(amount) AS maximum_order
FROM orders;
```

They can be used with:

- numbers,
- dates,
- timestamps,
- comparable strings,
- other types supported by the engine.

---

## 10.1 Temporal examples

Earliest order:

```sql
SELECT MIN(created_at) AS first_order_at
FROM orders;
```

Latest order:

```sql
SELECT MAX(created_at) AS last_order_at
FROM orders;
```

These are useful for:

- activity boundaries,
- freshness checks,
- first/last event analysis,
- data-quality monitoring.

---

## 10.2 NULL behavior

As with many standard aggregate functions, NULL values do not contribute.

If all contributing values are NULL, the result is NULL.

If no rows contribute, the result is also NULL.

---

# 11. GROUP BY

The basic form is:

```sql
SELECT
    country,
    COUNT(*) AS order_count
FROM orders
GROUP BY country;
```

The grouping expression is:

```text
country
```

Therefore the output grain is:

```text
one row per country
```

---

## 11.1 Simple rule for SELECT expressions

At beginner level, use this rule:

> Every selected expression should either be a grouping expression or be aggregated.

For example:

```sql
SELECT
    country,
    COUNT(*) AS order_count
FROM orders
GROUP BY country;
```

is valid because:

```text
country → grouped
COUNT(*) → aggregated
```

But this is generally invalid:

```sql
SELECT
    country,
    customer_id,
    COUNT(*)
FROM orders
GROUP BY country;
```

because:

```text
customer_id
```

is neither grouped nor aggregated.

Some engines can permit additional expressions in cases involving functional dependencies or engine-specific extensions. Do not use those exceptions to avoid understanding the basic rule.

---

# 12. Output Grain of GROUP BY

This is the most important practical section.

## 12.1 Group by one column

```sql
GROUP BY country
```

means:

```text
one row per country
```

---

## 12.2 Group by two columns

```sql
GROUP BY country, month
```

means:

```text
one row per country per month
```

---

## 12.3 Group by customer

```sql
GROUP BY customer_id
```

means:

```text
one row per customer
```

assuming customer_id identifies the business entity for this result.

---

## 12.4 Add another grouping dimension

Compare:

```sql
GROUP BY country
```

to:

```sql
GROUP BY country, payment_method
```

The first output grain:

```text
country
```

The second:

```text
country + payment_method
```

A single country can now have multiple output rows.

---

## 12.5 Example

Input:

```text
country | payment_method | amount
--------+----------------+-------
India   | card           | 100
India   | card           | 200
India   | bank           | 300
Nepal   | card           | 400
```

Grouping by country:

```sql
SELECT
    country,
    SUM(amount) AS revenue
FROM orders
GROUP BY country;
```

Output:

```text
India | 600
Nepal | 400
```

Grouping by country and payment method:

```sql
SELECT
    country,
    payment_method,
    SUM(amount) AS revenue
FROM orders
GROUP BY
    country,
    payment_method;
```

Output:

```text
India | card | 300
India | bank | 300
Nepal | card | 400
```

The grain changed.

---

# 13. WHERE vs GROUP BY vs HAVING

A useful mental model is:

```text
raw rows
   ↓
WHERE
   ↓
remaining rows
   ↓
GROUP BY
   ↓
groups
   ↓
aggregate functions
   ↓
HAVING
   ↓
final grouped rows
```

---

## 13.1 WHERE filters rows

Example:

```sql
SELECT
    country,
    COUNT(*) AS completed_orders
FROM orders
WHERE status = 'completed'
GROUP BY country;
```

`WHERE` decides which raw rows enter the grouping.

---

## 13.2 HAVING filters groups

Example:

```sql
SELECT
    country,
    COUNT(*) AS order_count
FROM orders
GROUP BY country
HAVING COUNT(*) > 1000;
```

`HAVING` decides which groups survive.

---

## 13.3 Combined example

```sql
SELECT
    country,
    COUNT(*) AS completed_orders
FROM orders
WHERE status = 'completed'
GROUP BY country
HAVING COUNT(*) > 1000;
```

Read it as:

```text
1. Keep completed order rows.
2. Group the remaining rows by country.
3. Count each country.
4. Keep only countries whose count is above 1000.
```

---

# 14. WHERE vs HAVING — Practical Rule

Ask:

> Am I filtering raw rows or filtering an already-created group?

### Raw-row filter

```sql
WHERE status = 'completed'
```

### Group filter

```sql
HAVING COUNT(*) > 1000
```

Do not use HAVING simply because an aggregate appears somewhere in the query.

Example:

```sql
SELECT
    country,
    COUNT(*)
FROM orders
WHERE country = 'India'
GROUP BY country;
```

Filtering country before grouping with `WHERE` is clear and efficient.

---

# 15. NULLs and Aggregate Functions

NULL behavior differs by aggregate and needs deliberate attention.

Use this dataset:

```sql
CREATE TEMP TABLE aggregate_nulls (
    group_id INTEGER,
    amount NUMERIC,
    customer_id INTEGER
);

INSERT INTO aggregate_nulls
VALUES
    (1, 100, 10),
    (1, NULL, 11),
    (1, 300, 11),
    (2, NULL, NULL),
    (2, NULL, NULL);
```

For group 1:

```text
rows                    = 3
non-NULL amount values  = 2
amount sum              = 400
amount average          = 200
distinct customers      = 2
```

For group 2:

```text
rows                    = 2
non-NULL amount values  = 0
sum                     = NULL
average                 = NULL
distinct customer IDs   = 0
```

---

## 15.1 Summary table

| Expression | General behavior with NULL |
|---|---|
| `COUNT(*)` | counts rows |
| `COUNT(col)` | counts non-NULL values |
| `COUNT(DISTINCT col)` | counts distinct non-NULL values |
| `SUM(col)` | NULL values do not contribute |
| `AVG(col)` | NULL values do not contribute |
| `MIN(col)` | NULL values do not contribute |
| `MAX(col)` | NULL values do not contribute |

Always verify dialect-specific details when working with less common aggregates.

---

# 16. SUM and Empty Inputs

This case often appears in reporting.

Consider:

```sql
SELECT
    SUM(amount) AS revenue
FROM orders
WHERE status = 'cancelled';
```

What happens if there are no cancelled orders?

There are no rows contributing to the aggregate.

The result is:

```text
NULL
```

not necessarily:

```text
0
```

If the report's contract says that "no cancelled orders" should display as zero:

```sql
SELECT
    COALESCE(SUM(amount), 0) AS revenue
FROM orders
WHERE status = 'cancelled';
```

---

## 16.1 Distinguish these meanings

```text
NULL
```

may mean:

> No contributing value / not available.

```text
0
```

may mean:

> The metric is known and equals zero.

Do not erase that distinction by default.

---

# 17. COALESCE Around Aggregates

A common pattern is:

```sql
COALESCE(SUM(amount), 0)
```

Use this when the output contract requires a numeric zero when no values contribute.

---

## 17.1 Where to apply COALESCE

Compare:

```sql
SUM(COALESCE(amount, 0))
```

with:

```sql
COALESCE(SUM(amount), 0)
```

They can produce the same result for many non-empty groups, but they express different intentions.

### Inner COALESCE

```sql
SUM(COALESCE(amount, 0))
```

means:

> Treat each missing amount as zero before summing.

### Outer COALESCE

```sql
COALESCE(SUM(amount), 0)
```

means:

> Compute the normal aggregate, then represent an empty/NULL aggregate result as zero.

This distinction is useful for metric definitions and code review.

---

# 18. Conditional Aggregation

Conditional aggregation is one of the most useful SQL patterns for Data Engineers.

It allows several related metrics to be calculated from the same grouped input.

Example:

```sql
SELECT
    country,
    SUM(
        CASE
            WHEN payment_method = 'card'
            THEN amount
            ELSE 0
        END
    ) AS card_revenue,
    SUM(
        CASE
            WHEN payment_method = 'bank_transfer'
            THEN amount
            ELSE 0
        END
    ) AS bank_revenue
FROM orders
GROUP BY country;
```

The output is still:

```text
one row per country
```

but contains multiple metrics.

---

# 19. SUM(CASE WHEN ...)

## 19.1 Count rows conditionally

```sql
SELECT
    country,
    SUM(
        CASE
            WHEN status = 'completed' THEN 1
            ELSE 0
        END
    ) AS completed_orders
FROM orders
GROUP BY country;
```

This produces:

```text
one row per country
```

with:

```text
number of completed orders
```

---

## 19.2 Sum values conditionally

```sql
SELECT
    country,
    SUM(
        CASE
            WHEN status = 'completed'
            THEN amount
            ELSE 0
        END
    ) AS completed_revenue
FROM orders
GROUP BY country;
```

Now the metric is:

```text
sum of amounts from completed rows
```

---

## 19.3 Conditional aggregation with NULL

Be deliberate about:

```sql
ELSE 0
```

Suppose:

```text
status = completed
amount = NULL
```

Then:

```sql
CASE
    WHEN status = 'completed' THEN amount
    ELSE 0
END
```

returns NULL for the completed row.

`SUM` ignores that NULL.

If you need NULL amount to mean zero:

```sql
CASE
    WHEN status = 'completed'
    THEN COALESCE(amount, 0)
    ELSE 0
END
```

Do not add the COALESCE unless that interpretation is correct.

---

# 20. CASE-Based Conditional Counting

An often-used pattern is:

```sql
COUNT(
    CASE
        WHEN status = 'completed' THEN 1
    END
)
```

Why does this work?

For completed rows:

```text
CASE → 1
```

For non-completed rows:

```text
CASE → NULL
```

`COUNT(expression)` counts only non-NULL results.

So the count includes only completed rows.

Another common form is:

```sql
SUM(
    CASE
        WHEN status = 'completed' THEN 1
        ELSE 0
    END
)
```

Both can be useful. Choose the form your team finds most readable and consistent.

---

# 21. FILTER (WHERE ...)

SQL also supports conditional aggregation through `FILTER`.

Example:

```sql
SELECT
    country,
    COUNT(*) FILTER (
        WHERE status = 'completed'
    ) AS completed_orders,
    COUNT(*) FILTER (
        WHERE status = 'cancelled'
    ) AS cancelled_orders
FROM orders
GROUP BY country;
```

This is often clearer than repeating CASE expressions.

---

## 21.1 Conditional sums

```sql
SELECT
    country,
    SUM(amount) FILTER (
        WHERE payment_method = 'card'
    ) AS card_revenue,
    SUM(amount) FILTER (
        WHERE payment_method = 'bank_transfer'
    ) AS bank_revenue
FROM orders
GROUP BY country;
```

---

## 21.2 CASE versus FILTER

### CASE

```sql
SUM(
    CASE
        WHEN status = 'completed'
        THEN amount
        ELSE 0
    END
)
```

### FILTER

```sql
SUM(amount) FILTER (
    WHERE status = 'completed'
)
```

The FILTER form often communicates the metric more directly:

> Sum amount for rows where status is completed.

The exact support of FILTER should be verified for the engine/version you use.

---

# 22. Pivot-Style Reporting

A pivot-style report turns category values into separate output columns.

Suppose the source contains:

```text
payment_method | amount
---------------+-------
card           | 100
cash           | 200
bank           | 300
```

A pivot-style result might look like:

```text
card_revenue | cash_revenue | bank_revenue
-------------+--------------+-------------
100          | 200          | 300
```

Conditional aggregation is a portable way to build this style of report.

```sql
SELECT
    SUM(amount) FILTER (WHERE payment_method = 'card')
        AS card_revenue,
    SUM(amount) FILTER (WHERE payment_method = 'cash')
        AS cash_revenue,
    SUM(amount) FILTER (WHERE payment_method = 'bank')
        AS bank_revenue
FROM orders;
```

---

## 22.1 Why pivoting can be useful

Common reporting dimensions include:

- payment method,
- order status,
- region,
- device type,
- subscription state.

The choice should be driven by the downstream report contract.

---

# 23. PIVOT in DuckDB

DuckDB supports a `PIVOT` feature for pivot-style transformations.

A representative DuckDB pattern is:

```sql
PIVOT orders
ON payment_method
USING SUM(amount)
GROUP BY country;
```

This is:

> **DuckDB-specific / dialect-specific syntax.**

The exact PIVOT syntax can evolve, so verify it against the DuckDB version in your environment.

---

## 23.1 Why conditional aggregation remains important

Conditional aggregation:

```sql
SUM(amount) FILTER (WHERE payment_method = 'card')
```

is often easier to move between SQL engines.

DuckDB PIVOT may be more concise for some reports.

Use a dialect-specific convenience when its benefits outweigh portability requirements.

---

# 24. STRING_AGG

`STRING_AGG` collects multiple string values into one string.

Example:

```sql
SELECT
    customer_id,
    STRING_AGG(product_name, ', ') AS products
FROM order_items
GROUP BY customer_id;
```

Possible output:

```text
customer_id | products
------------+-------------------------
1           | Keyboard, Mouse, Monitor
```

---

## 24.1 Ordering inside STRING_AGG

For deterministic results:

```sql
SELECT
    customer_id,
    STRING_AGG(
        product_name,
        ', '
        ORDER BY product_name
    ) AS products
FROM order_items
GROUP BY customer_id;
```

This says:

> Collect the values and order them alphabetically inside the aggregate.

Do not assume the collection order is stable without an explicit ordering requirement.

---

## 24.2 NULL values

NULL input handling can vary somewhat by aggregate and engine, but common SQL string aggregation semantics do not treat NULL as a literal string `"NULL"` automatically.

Always test when NULL presence affects a downstream contract.

---

## 24.3 Production concerns

A concatenated string can become very large.

Before using `STRING_AGG` for an operational interface, consider:

- maximum output length,
- downstream parsing,
- deterministic ordering,
- NULL behavior,
- whether an array/structured value is more appropriate.

---

# 25. ARRAY_AGG

`ARRAY_AGG` collects values into an array.

Example:

```sql
SELECT
    customer_id,
    ARRAY_AGG(product_id) AS product_ids
FROM order_items
GROUP BY customer_id;
```

---

## 25.1 Deterministic ordering

Prefer:

```sql
SELECT
    customer_id,
    ARRAY_AGG(
        product_id
        ORDER BY product_id
    ) AS product_ids
FROM order_items
GROUP BY customer_id;
```

This creates a stable representation for comparison and testing.

---

## 25.2 Why ordering matters

These two arrays contain the same values:

```text
[10, 20, 30]
[30, 10, 20]
```

but are not the same ordered sequence.

If a downstream consumer compares arrays directly, unordered aggregation can cause false differences.

---

# 26. Ordering Inside Collection Aggregates

This is a production-quality detail.

Compare:

```sql
ARRAY_AGG(product_id)
```

with:

```sql
ARRAY_AGG(
    product_id
    ORDER BY product_id
)
```

and:

```sql
STRING_AGG(
    product_name,
    ', '
    ORDER BY product_name
)
```

The explicit ordering provides a deterministic result where the business contract needs one.

Use this for:

- reproducible tests,
- snapshots,
- generated dimensions,
- deterministic exports,
- stable comparisons.

---

# 27. Statistical Aggregates

Simple aggregates describe basic properties:

```text
COUNT
SUM
AVG
MIN
MAX
```

But real production metrics often need distribution information.

Examples:

```text
API latency
order value
data-processing duration
delivery time
```

An average can hide a long tail.

Consider:

```text
99 requests = 10 ms
1 request  = 10 seconds
```

The average reflects both values, but users may care about the tail.

Percentiles can show that tail.

---

# 28. PERCENTILE_CONT

A continuous percentile can interpolate between ordered values.

A representative PostgreSQL query is:

```sql
SELECT
    country,
    PERCENTILE_CONT(0.50)
        WITHIN GROUP (ORDER BY amount) AS p50_order_value,
    PERCENTILE_CONT(0.95)
        WITHIN GROUP (ORDER BY amount) AS p95_order_value
FROM orders
GROUP BY country;
```

---

## 28.1 What p50 means

The p50 is the 50th percentile.

It is commonly called the median in contexts where the percentile definition corresponds to the median.

---

## 28.2 What p95 means

p95 is a value below which approximately 95% of the ordered observations fall, according to the aggregate's percentile definition.

For operational latency:

```text
p50 = typical middle behavior
p95 = upper-tail behavior
```

This can be more informative than average latency.

---

## 28.3 WITHIN GROUP

The syntax:

```sql
PERCENTILE_CONT(0.95)
WITHIN GROUP (
    ORDER BY amount
)
```

means the percentile is computed over the ordered values of `amount`.

This is an ordered-set aggregate.

---

# 29. PERCENTILE_DISC

`PERCENTILE_DISC` chooses an actual value from the ordered input rather than interpolating a value between observations.

Representative syntax:

```sql
SELECT
    PERCENTILE_DISC(0.95)
        WITHIN GROUP (ORDER BY amount) AS p95
FROM orders;
```

---

## 29.1 Continuous vs discrete

Use the mental model:

```text
PERCENTILE_CONT
→ may interpolate

PERCENTILE_DISC
→ chooses an observed value
```

The exact percentile definition and interpolation details should be verified against the target engine's documentation.

---

# 30. Percentiles — Tiny Example

Consider ordered values:

```text
10
20
30
40
```

A percentile calculation may land between observed values.

That is why a continuous percentile can produce a value not literally present in the input.

A discrete percentile chooses one of the observed values.

Do not memorize a single hand-calculated interpolation formula unless your specific use case requires it. Understand the distinction and verify engine semantics for boundary cases.

---

# 31. MODE

The mode is the most frequently occurring value.

A representative ordered-set aggregate expression is:

```sql
MODE() WITHIN GROUP (
    ORDER BY payment_method
)
```

For example:

```text
card
card
cash
card
bank
```

the mode is:

```text
card
```

Use cases include:

- most common payment method,
- most frequent status,
- common device type.

Tie behavior may be engine-specific, so verify the target engine when multiple values have the same frequency.

---

# 32. STDDEV

Standard deviation measures dispersion.

A representative query is:

```sql
SELECT
    country,
    STDDEV(amount) AS amount_stddev
FROM orders
GROUP BY country;
```

This can answer questions such as:

> How variable is order value across customers in this country?

Or:

> How variable is processing duration across runs?

---

## 32.1 Average versus standard deviation

Think:

```text
AVG
→ center

STDDEV
→ spread
```

A dataset can have the same average but very different variability.

---

# 33. GROUPING SETS

`GROUPING SETS` lets one query produce several grouping levels.

Example:

```sql
SELECT
    country,
    payment_method,
    SUM(amount) AS revenue
FROM orders
GROUP BY GROUPING SETS (
    (country, payment_method),
    (country),
    ()
);
```

This requests:

```text
1. country + payment_method
2. country subtotal
3. grand total
```

---

## 33.1 Why GROUPING SETS matter

Without GROUPING SETS, you might write multiple queries and combine them.

With GROUPING SETS, the different group levels can be expressed together.

This is useful for:

- reporting cubes,
- subtotals,
- reconciliation,
- multi-level KPI outputs.

---

# 34. GROUPING SETS — Grain Reasoning

The query:

```sql
GROUP BY GROUPING SETS (
    (country, payment_method),
    (country),
    ()
)
```

has multiple output grains.

```text
(country, payment_method)
    → one row per country per payment method

(country)
    → one row per country

()
    → one grand-total row
```

A crucial lesson:

> `GROUP BY` no longer corresponds to one single grain when grouping sets are used; the result contains several intentional grains.

---

# 35. ROLLUP

`ROLLUP` is useful for hierarchical subtotals.

Example:

```sql
SELECT
    country,
    month,
    SUM(amount) AS revenue
FROM orders
GROUP BY ROLLUP (
    country,
    month
);
```

Conceptually this generates levels:

```text
country + month
country
grand total
```

---

## 35.1 Order of ROLLUP columns matters

Consider:

```sql
ROLLUP(country, month)
```

This creates a hierarchy based on the listed order.

The conceptual levels are:

```text
(country, month)
(country)
()
```

This differs from:

```sql
ROLLUP(month, country)
```

whose hierarchy is:

```text
(month, country)
(month)
()
```

Choose the order according to the reporting hierarchy.

---

# 36. CUBE

`CUBE` generates combinations of grouping dimensions.

Example:

```sql
SELECT
    country,
    payment_method,
    SUM(amount) AS revenue
FROM orders
GROUP BY CUBE (
    country,
    payment_method
);
```

Conceptually the output includes:

```text
country + payment_method
country
payment_method
grand total
```

---

## 36.1 Why CUBE can grow quickly

With:

```text
N grouping dimensions
```

a full cube can conceptually generate up to:

```text
2^N
```

grouping combinations.

For two dimensions:

```text
2^2 = 4
```

For five:

```text
2^5 = 32
```

For ten:

```text
2^10 = 1024
```

This is why CUBE should be used deliberately rather than automatically.

---

# 37. GROUPING()

Subtotal rows introduce a subtle problem.

Suppose real data contains:

```text
country = NULL
```

A ROLLUP subtotal can also produce:

```text
country = NULL
```

These two NULLs have different meanings.

One means:

> The actual data value is NULL.

The other means:

> This row is a subtotal/grand-total marker.

`GROUPING()` helps distinguish them.

---

## 37.1 Example

```sql
SELECT
    country,
    payment_method,
    SUM(amount) AS revenue,
    GROUPING(country) AS country_is_grouped,
    GROUPING(payment_method) AS payment_is_grouped
FROM orders
GROUP BY ROLLUP (
    country,
    payment_method
);
```

Conceptually:

```text
GROUPING(country) = 0
→ country is a real grouping value

GROUPING(country) = 1
→ country has been rolled up
```

The same logic applies to payment method.

---

# 38. Real NULL vs Subtotal NULL

This distinction matters in production reporting.

Suppose the input contains:

```text
country = NULL
payment_method = card
```

A real group might be:

```text
NULL | card | 500
```

A country subtotal might also appear as:

```text
India | NULL | 10000
```

The NULL in the second row does not mean:

```text
payment_method was missing
```

It means:

```text
payment_method dimension has been rolled up
```

Use `GROUPING()` instead of trying to infer subtotal rows from NULL alone.

---

# 39. GROUPING SETS vs ROLLUP vs CUBE

| Feature | Main idea |
|---|---|
| `GROUPING SETS` | Explicitly choose the grouping combinations |
| `ROLLUP` | Hierarchical subtotals |
| `CUBE` | All combinations of listed dimensions |
| `GROUPING()` | Identify which columns are rolled up in a result row |

A useful mental model:

```text
GROUPING SETS
→ you choose the levels

ROLLUP
→ hierarchy

CUBE
→ combinations
```

---

# 40. Approximate Aggregation

Exact metrics are not always the cheapest metrics.

At very large scale, an exact distinct count can require significant computation and memory.

For example:

```text
COUNT(DISTINCT user_id)
```

over billions of events can be expensive.

Some engines provide approximate aggregations.

The basic idea is:

```text
exact
→ more resources, exact answer

approximate
→ fewer resources / often faster, small bounded error
```

The choice is a product requirement, not simply a performance trick.

---

# 41. Approximate Distinct Counting

Where supported, engines may provide functions such as:

```sql
approx_count_distinct(customer_id)
```

or another engine-specific approximate-cardinality function.

Do not present this name as universal SQL.

The exact function name and behavior must be verified for the target engine.

---

## 41.1 Why it can be useful

Suppose you need:

> Approximate number of unique users viewing a page.

You may not need:

```text
17,482,193
```

to be exact.

You may only need:

```text
approximately 17.5 million
```

with known error characteristics.

---

# 42. HyperLogLog

**HyperLogLog (HLL)** is a probabilistic technique for estimating distinct cardinality.

The learner does not need the mathematical derivation here.

Use this mental model:

```text
Many distinct values
      ↓
compact probabilistic summary
      ↓
estimated distinct count
```

Compared with exact distinct counting, the summary can use much less memory while producing an estimate with known statistical error characteristics.

---

## 42.1 Why HLL matters to Data Engineers

It is useful when:

- the input is very large,
- approximate cardinality is acceptable,
- memory efficiency matters,
- distributed aggregation is important.

This technique is common conceptually in large analytics systems because compact summaries can be merged across partitions or workers.

---

# 43. When Approximation Is Acceptable

Use business requirements.

## Often reasonable

- dashboard trend counts,
- exploratory analysis,
- approximate audience size,
- large-scale usage analytics,
- early-stage capacity planning.

## Generally not appropriate without explicit approval

- billing,
- financial reconciliation,
- regulatory reporting,
- contractual metrics,
- audit-critical totals.

The key question is:

> **What is the allowed error, and what happens if the estimate is wrong?**

---

# 44. Ratio Metrics

Ratios deserve special treatment because they combine two quantities.

A metric such as:

```text
conversion rate
```

should first be defined mathematically:

```text
successful conversions
----------------------
eligible opportunities
```

Only then should you write SQL.

---

## 44.1 Simple example

```sql
SELECT
    SUM(
        CASE
            WHEN status = 'converted' THEN 1
            ELSE 0
        END
    )::numeric
    / NULLIF(COUNT(*), 0) AS conversion_rate
FROM opportunities;
```

The exact denominator must match the business definition.

---

# 45. Correct Ratio Construction

Suppose a daily table contains:

```text
day        successful   total
---------- -----------  -----
2025-03-01 90           100
2025-03-02 1            10
```

Daily rates:

```text
90%
10%
```

If you average them:

```text
(90% + 10%) / 2
=
50%
```

But the overall conversion rate is:

```text
(90 + 1) / (100 + 10)
=
91 / 110
=
82.727...%
```

The correct aggregate ratio uses the underlying totals.

---

# 46. The Average-of-Averages Trap

This is one of the most important metric-engineering mistakes.

Suppose:

```text
Region A
10 customers
9 conversions

Region B
1000 customers
500 conversions
```

The rates are:

```text
Region A = 9 / 10 = 90%
Region B = 500 / 1000 = 50%
```

A naïve average gives:

```text
(90% + 50%) / 2
=
70%
```

But the true overall rate is:

```text
(9 + 500) / (10 + 1000)
=
509 / 1010
≈ 50.396%
```

The large region must contribute more weight because it contains more opportunities.

---

# 47. Correct Weighted Averages

A weighted average accounts for the quantity represented by each observation.

General form:

```text
weighted average
=
Σ(value × weight)
-----------------
Σ(weight)
```

SQL:

```sql
SELECT
    SUM(score * weight)
    / NULLIF(SUM(weight), 0) AS weighted_score
FROM observations;
```

---

## 47.1 Data-engineering example

Suppose:

```text
product | price | units
--------+-------+------
A       | 10    | 100
B       | 20    | 10
```

A simple average price is:

```text
(10 + 20) / 2
=
15
```

But the units-weighted average selling price is:

```text
(10 × 100 + 20 × 10) / (100 + 10)
=
1200 / 110
≈ 10.9091
```

The second metric reflects actual sales volume.

---

# 48. Ratio Safety

For ratio metrics, a common production pattern is:

```sql
SUM(numerator)
/
NULLIF(SUM(denominator), 0)
```

For example:

```sql
SELECT
    SUM(successful_payments)::numeric
    / NULLIF(SUM(total_payments), 0) AS payment_success_rate
FROM daily_payment_metrics;
```

This protects against a zero denominator.

---

## 48.1 Why NULLIF is preferable to inventing a value

If:

```text
denominator = 0
```

the ratio may not have a meaningful numeric value.

Returning NULL communicates:

> Undefined because there were no eligible observations.

Returning zero would communicate:

> The rate was exactly zero.

Those are different meanings.

---

# 49. Ratio Metrics and Grain

Always ask:

```text
What is the numerator grain?
What is the denominator grain?
Are they compatible?
```

For example:

```text
successful_orders = number of successful orders
eligible_orders   = number of eligible orders
```

If you accidentally use:

```text
successful_order_lines
```

against:

```text
eligible_orders
```

you may produce a mathematically structured but semantically invalid ratio.

Metric definitions must match the grain.

---

# 50. Numeric Precision and Overflow

Aggregation can create numbers much larger than individual source values.

For example:

```text
amount per row:
100.00

rows:
10,000,000,000
```

The total is enormous relative to one row.

The data type must be able to represent the aggregate safely.

---

# 51. INTEGER vs BIGINT vs NUMERIC

At a high level:

```text
INTEGER
→ smaller exact integer range

BIGINT
→ larger exact integer range

NUMERIC
→ exact decimal arithmetic with declared precision/scale semantics

DOUBLE PRECISION
→ binary floating-point approximation
```

The exact limits are engine-specific.

For high-value financial aggregations, select an appropriate exact decimal type rather than assuming floating point is interchangeable.

---

# 52. Integer Overflow

A query such as:

```sql
SELECT SUM(quantity)
FROM order_lines;
```

can overflow if the aggregate result cannot be represented safely by the chosen numeric type.

The exact behavior depends on the database and type involved.

Do not wait for an overflow incident to discover the range.

---

## 52.1 Production questions

Before large aggregations ask:

- What is the source type?
- What type does the aggregate produce?
- How large can the result become?
- Can the data volume grow materially?
- Does the destination have enough range?
- Is an explicit cast required?

---

# 53. NUMERIC vs DOUBLE PRECISION

Use `NUMERIC` when exact decimal semantics matter.

Typical examples:

- money,
- tax,
- invoice amounts,
- account balances,
- contractual decimal values.

Example:

```sql
NUMERIC(18, 2)
```

may be appropriate for a currency amount where the data model allows two decimal places.

`DOUBLE PRECISION` is often appropriate for:

- scientific measurements,
- approximate numerical computation,
- values where binary floating-point error is acceptable.

Do not reduce this to:

> "DOUBLE is bad."

The right choice depends on the semantics and precision requirements.

---

# 54. Money and Aggregation

For money, think about all of these together:

```text
data type
+
precision
+
rounding
+
aggregation
+
currency
```

For example, this is not merely a type issue:

```sql
SUM(amount)
```

You also need to know:

- Is `amount` already rounded?
- Are all values in the same currency?
- Should conversion happen before aggregation?
- What rounding policy applies?
- Could the sum exceed the chosen precision?

The SQL syntax is only one part of metric correctness.

---

# 55. Rounding and Aggregation

These operations are not always interchangeable:

```sql
ROUND(AVG(amount), 2)
```

versus:

```sql
AVG(ROUND(amount, 2))
```

They can produce different results.

The first means:

> Calculate the average, then round the final metric.

The second means:

> Round each row first, then calculate the average.

That distinction matters in financial and statistical calculations.

Do not round early simply because the final report displays two decimal places.

---

# 56. GROUP BY ALL

Some engines, including DuckDB, support `GROUP BY ALL`.

Example:

```sql
SELECT
    country,
    payment_method,
    SUM(amount) AS revenue
FROM orders
GROUP BY ALL;
```

Conceptually, `GROUP BY ALL` tells the engine to group by the non-aggregate selected expressions.

This is:

```text
DIALECT-SPECIFIC
```

and is not a universal SQL portability assumption.

---

## 56.1 Why teams may like it

It can reduce repetition:

```sql
SELECT
    country,
    payment_method,
    SUM(amount)
FROM orders
GROUP BY country, payment_method;
```

becomes:

```sql
SELECT
    country,
    payment_method,
    SUM(amount)
FROM orders
GROUP BY ALL;
```

This can be convenient in exploratory and analytical work.

But production code still needs a clear dialect policy.

---

# 57. GROUP BY Ordinal Positions

Some engines allow:

```sql
SELECT
    country,
    payment_method,
    SUM(amount)
FROM orders
GROUP BY 1, 2;
```

Here:

```text
1 = first selected expression
2 = second selected expression
```

---

## 57.1 Why it can be risky

Suppose the select list changes:

```sql
SELECT
    payment_method,
    country,
    SUM(amount)
FROM orders
GROUP BY 1, 2;
```

The grouping expressions now follow the new select-list order.

A reviewer must mentally map numbers to expressions.

---

## 57.2 Production recommendation

For maintainable transformation code, explicit grouping columns are often easier to read:

```sql
GROUP BY
    country,
    payment_method;
```

Ordinal grouping is not inherently invalid.

It is simply less self-documenting.

---

# 58. Standard SQL vs PostgreSQL vs DuckDB

SQL is standardized, but practical SQL is dialect-specific.

Use this mental model:

```text
SQL concept
    ↓
engine implementation
    ↓
dialect syntax / extension
```

---

## 58.1 Common core concepts

These are broadly standard SQL ideas:

```text
COUNT
SUM
AVG
MIN
MAX
GROUP BY
HAVING
CASE
FILTER
GROUPING SETS
ROLLUP
CUBE
```

The exact support and syntax details can still vary.

---

## 58.2 PostgreSQL-specific examples

PostgreSQL has its own:

- aggregate functions,
- ordered-set aggregate behavior,
- casting syntax,
- type system,
- extensions.

For this topic, do not present PostgreSQL-only conveniences as universal SQL.

---

## 58.3 DuckDB-specific conveniences

Relevant examples include:

```text
PIVOT
GROUP BY ALL
```

and engine-specific approximate functions where supported.

Always verify exact version support.

---

# 59. Aggregation After Joins

The previous topic taught that joins can change grain.

This topic must build on that.

Consider:

```text
orders
   |
   +---- order_lines
   |
   +---- payments
```

Suppose:

```text
one order
3 lines
2 payments
```

A raw join can create:

```text
3 × 2
=
6 rows
```

If you then write:

```sql
SUM(o.amount)
```

you may sum the same order amount six times.

---

## 59.1 Correct mental flow

```text
wrong join grain
      ↓
duplicated rows
      ↓
aggregation
      ↓
wrong metric
```

The correct flow can be:

```text
identify metric grain
      ↓
pre-aggregate independent children
      ↓
join at compatible grain
      ↓
aggregate/report
```

---

## 59.2 Example

Bad:

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

Better:

```sql
WITH payment_totals AS (
    SELECT
        order_id,
        SUM(amount) AS paid_amount
    FROM payments
    GROUP BY order_id
),
line_totals AS (
    SELECT
        order_id,
        SUM(quantity * unit_price) AS line_revenue
    FROM order_lines
    GROUP BY order_id
)
SELECT
    o.order_id,
    o.amount AS order_revenue,
    lt.line_revenue,
    pt.paid_amount
FROM orders AS o
LEFT JOIN line_totals AS lt
    ON lt.order_id = o.order_id
LEFT JOIN payment_totals AS pt
    ON pt.order_id = o.order_id;
```

The detailed join reasoning belongs to Topic 02, but the aggregation lesson is:

> **A correct aggregate cannot repair an incorrect row set.**

---

# 60. Production Aggregation Patterns

For every production aggregation, state:

```text
Input grain:
Grouping columns:
Output grain:
Metric:
Rows included:
NULL behavior:
Potential correctness risk:
Validation:
```

---

## Pattern 1 — Daily revenue

### Requirement

One row per day.

### Input

```text
one row per order
```

### SQL

```sql
SELECT
    DATE_TRUNC('day', created_at) AS order_day,
    SUM(amount) AS revenue
FROM orders
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY order_day;
```

### Output grain

```text
one row per day
```

### Validation

```text
sum(daily revenue)
=
sum(source order amount)
```

provided the same filters are applied.

---

# 61. Production Pattern — Revenue by Country and Month

### Grain

```text
one row per order
```

### Grouping

```text
country + month
```

### Output

```text
one row per country per month
```

### SQL

```sql
SELECT
    country,
    DATE_TRUNC('month', created_at) AS month,
    SUM(amount) AS revenue
FROM orders
GROUP BY
    country,
    DATE_TRUNC('month', created_at)
ORDER BY
    country,
    month;
```

### Risk

If `orders` was duplicated before this aggregation, revenue is duplicated too.

---

# 62. Production Pattern — KPI Report

A single grouped query can calculate:

```text
order count
completed order count
cancelled order count
revenue
completed revenue
average order value
```

Example:

```sql
SELECT
    country,
    COUNT(*) AS order_count,
    COUNT(*) FILTER (
        WHERE status = 'completed'
    ) AS completed_orders,
    COUNT(*) FILTER (
        WHERE status = 'cancelled'
    ) AS cancelled_orders,
    SUM(amount) AS revenue,
    SUM(amount) FILTER (
        WHERE status = 'completed'
    ) AS completed_revenue,
    AVG(amount) AS average_order_value
FROM orders
GROUP BY country;
```

The output grain remains:

```text
one row per country
```

---

# 63. Production Pattern — Percentile Latency

### Requirement

One row per API endpoint.

### Input grain

```text
one row per API request
```

### SQL

```sql
SELECT
    endpoint,
    PERCENTILE_CONT(0.50)
        WITHIN GROUP (ORDER BY latency_ms) AS p50_ms,
    PERCENTILE_CONT(0.95)
        WITHIN GROUP (ORDER BY latency_ms) AS p95_ms
FROM api_requests
GROUP BY endpoint;
```

### Output grain

```text
one row per endpoint
```

### Risk

Averages and percentiles answer different questions. Do not replace a product-defined percentile SLA with an average.

---

# 64. Production Pattern — Conditional Payment Metrics

```sql
SELECT
    payment_date,
    COUNT(*) AS payments,
    COUNT(*) FILTER (
        WHERE status = 'succeeded'
    ) AS succeeded,
    COUNT(*) FILTER (
        WHERE status = 'failed'
    ) AS failed,
    SUM(amount) FILTER (
        WHERE status = 'succeeded'
    ) AS succeeded_amount
FROM payments
GROUP BY payment_date
ORDER BY payment_date;
```

Potential ratio:

```sql
SELECT
    payment_date,
    COUNT(*) FILTER (
        WHERE status = 'succeeded'
    )::numeric
    / NULLIF(COUNT(*), 0) AS success_rate
FROM payments
GROUP BY payment_date;
```

---

# 65. Production Pattern — Exact vs Approximate Distinct

Requirement:

> Dashboard needs daily unique viewers over extremely large event volumes.

Exact:

```sql
COUNT(DISTINCT user_id)
```

Approximate, if supported:

```sql
approx_count_distinct(user_id)
```

The production choice depends on:

```text
allowed error
cost
latency
data volume
business consequence
```

An approximate dashboard metric may be acceptable.

A billing metric may not be.

---

# 66. Production Pattern — Subtotals and Grand Total

A reporting table may require:

```text
country
payment_method
revenue
```

plus:

```text
country subtotal
grand total
```

Use:

```sql
SELECT
    country,
    payment_method,
    SUM(amount) AS revenue
FROM orders
GROUP BY ROLLUP (
    country,
    payment_method
);
```

Then use `GROUPING()` when consumers need to distinguish subtotal markers from real NULL values.

---

# 67. Aggregation Debugging Methodology

When a metric looks wrong, do not immediately rewrite the aggregate.

Use a structured process.

## Step 1 — State the input grain

Example:

```text
one row per order
```

---

## Step 2 — State the intended output grain

Example:

```text
one row per customer per month
```

---

## Step 3 — State the metric definition

Example:

```text
monthly revenue
=
sum of order revenue for included orders
```

---

## Step 4 — Confirm filters

Inspect:

```sql
WHERE ...
```

Ask:

- Which rows are included?
- Are NULLs filtered unintentionally?
- Are date boundaries correct?

---

## Step 5 — Check joins

Ask:

> Did anything happen before the aggregation that could multiply rows?

This is a major source of incorrect sums.

---

## Step 6 — Compare row counts

```sql
SELECT COUNT(*)
FROM orders;
```

and compare with the relevant transformed input.

---

## Step 7 — Compare distinct entities

```sql
SELECT COUNT(DISTINCT order_id)
FROM orders;
```

Compare with the result after joins/filters.

---

## Step 8 — Inspect NULL counts

```sql
SELECT
    COUNT(*) AS total_rows,
    COUNT(amount) AS non_null_amounts
FROM orders;
```

---

## Step 9 — Inspect numerator and denominator separately

For a ratio:

```sql
SELECT
    SUM(successful) AS successful,
    SUM(total) AS total
FROM metrics;
```

Then calculate the ratio.

Do not debug the final decimal alone.

---

## Step 10 — Inspect numeric types

Check whether:

```text
integer division
overflow
floating-point precision
```

could affect the result.

---

## Step 11 — Verify with a tiny dataset

Construct five to ten rows where the correct answer is known by hand.

---

## Step 12 — Reconcile

Use independent totals or counts.

---

# 68. Assertion Queries for Aggregations

Treat SQL like code.

A useful assertion returns zero rows when the invariant is valid.

---

## 68.1 No NULL customer IDs

```sql
SELECT *
FROM customers
WHERE customer_id IS NULL;
```

Expected:

```text
0 rows
```

when the model requires a non-NULL customer ID.

---

## 68.2 No duplicate customer IDs

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

if customers should be unique.

---

## 68.3 Revenue reconciliation

Suppose:

```text
daily revenue
=
sum of order revenue
```

An assertion can be constructed as:

```sql
WITH daily AS (
    SELECT
        DATE_TRUNC('day', created_at) AS day,
        SUM(amount) AS revenue
    FROM orders
    GROUP BY DATE_TRUNC('day', created_at)
),
check_result AS (
    SELECT
        (SELECT SUM(revenue) FROM daily) AS grouped_total,
        (SELECT SUM(amount) FROM orders) AS source_total
)
SELECT *
FROM check_result
WHERE grouped_total IS DISTINCT FROM source_total;
```

Expected:

```text
0 rows
```

The use of `IS DISTINCT FROM` makes the comparison NULL-safe.

---

# 69. Assertion — Ratio Bounds

For a rate that must be between 0 and 1:

```sql
SELECT *
FROM daily_metrics
WHERE conversion_rate < 0
   OR conversion_rate > 1;
```

Expected:

```text
0 rows
```

This is a simple but valuable quality check.

---

# 70. Assertion — Additive Grouping

Suppose:

```text
country revenue
```

must add to:

```text
overall revenue
```

Then compare:

```sql
WITH by_country AS (
    SELECT
        country,
        SUM(amount) AS revenue
    FROM orders
    GROUP BY country
),
totals AS (
    SELECT
        (SELECT SUM(revenue) FROM by_country) AS grouped_total,
        (SELECT SUM(amount) FROM orders) AS source_total
)
SELECT *
FROM totals
WHERE grouped_total IS DISTINCT FROM source_total;
```

Expected:

```text
0 rows
```

This is valid only when the filters and grouping semantics mean every source amount belongs to exactly one country bucket.

---

# 71. Assertion — No Impossible Negative Counts

For a derived metric:

```sql
SELECT *
FROM metrics
WHERE completed_orders < 0
   OR cancelled_orders < 0;
```

This sounds obvious, but assertions should encode business invariants, not only SQL structure.

---

# 72. Aggregation Testing with Tiny Tables

Large data can hide logic errors.

Use tiny controlled datasets.

Example:

```sql
CREATE TEMP TABLE tiny_orders (
    order_id INTEGER,
    customer_id INTEGER,
    country TEXT,
    amount NUMERIC
);

INSERT INTO tiny_orders
VALUES
    (1, 10, 'India', 100),
    (2, 10, 'India', 200),
    (3, 20, 'Nepal', 300),
    (4, 20, 'Nepal', NULL),
    (5, 30, NULL, 0);
```

Before executing, write down:

```text
India revenue = 300
Nepal revenue = 300
NULL-country revenue = 0
order count = 5
distinct customers = 3
```

Then verify.

This is much faster than trying to reason about a billion-row production result.

---

# 73. Common Aggregation Mistakes

## Mistake 1 — Wrong output grain

### Wrong reasoning

> "I grouped by country, but I expected one row per customer."

### Fix

Review the grouping definition.

```text
GROUP BY country
```

means:

```text
one row per country
```

not one row per customer.

---

## Mistake 2 — Aggregating after join explosion

### Symptom

Revenue doubles or triples after adding a join.

### Cause

The input to the aggregate has duplicated business facts.

### Fix

Repair the join grain before aggregation.

---

## Mistake 3 — Averaging averages

### Wrong

```sql
AVG(country_conversion_rate)
```

for an overall conversion rate.

### Fix

Aggregate raw numerators and denominators:

```sql
SUM(successful)::numeric
/
NULLIF(SUM(total), 0)
```

---

## Mistake 4 — COUNT(*) when distinct entities are needed

### Wrong:

```sql
COUNT(*)
```

for customer count.

### Correct:

```sql
COUNT(DISTINCT customer_id)
```

when the metric is distinct customers.

---

## Mistake 5 — COUNT(column) misunderstood

`COUNT(email)` does not count rows.

It counts non-NULL email values.

---

## Mistake 6 — Treating NULL as zero without business justification

```sql
COALESCE(amount, 0)
```

changes semantics.

Use it intentionally.

---

## Mistake 7 — Filtering an aggregate in WHERE

This is wrong:

```sql
SELECT
    country,
    COUNT(*) AS order_count
FROM orders
WHERE COUNT(*) > 1000
GROUP BY country;
```

`COUNT(*)` is a group-level result.

Use:

```sql
HAVING COUNT(*) > 1000
```

---

## Mistake 8 — Filtering raw rows with HAVING unnecessarily

This:

```sql
HAVING country = 'India'
```

may be technically possible in some contexts but is less direct than:

```sql
WHERE country = 'India'
```

Use WHERE for row filtering.

---

## Mistake 9 — Integer division

Wrong:

```sql
successful / total
```

when both are integers and the target metric requires decimals.

Use an explicit decimal type:

```sql
successful::numeric
/
NULLIF(total, 0)
```

---

## Mistake 10 — Division by zero

Wrong:

```sql
SUM(successful) / SUM(total)
```

when `SUM(total)` may be zero.

Use:

```sql
SUM(successful)::numeric
/
NULLIF(SUM(total), 0)
```

---

## Mistake 11 — Unordered ARRAY_AGG or STRING_AGG

If deterministic output is required, explicitly order inside the aggregate.

---

## Mistake 12 — Misreading ROLLUP NULLs

A NULL can mean:

```text
actual data value
```

or:

```text
subtotal marker
```

Use `GROUPING()`.

---

## Mistake 13 — Approximate metric used where exactness is required

A dashboard estimate can be fine.

A billing total may not be.

---

## Mistake 14 — Numeric overflow

A query can fail or produce an unsafe result when aggregate ranges exceed the selected type.

---

## Mistake 15 — Floating-point for exact decimal semantics

Do not assume `DOUBLE PRECISION` is equivalent to exact decimal arithmetic.

---

## Mistake 16 — Grouping by ordinal positions without thinking

```sql
GROUP BY 1, 2
```

can become confusing when the SELECT list changes.

---

## Mistake 17 — GROUP BY ALL treated as universal SQL

It is a dialect convenience.

Verify engine support.

---

# 74. Hands-On Exercises

The exercises below intentionally move from fundamentals to production reasoning.

---

## Exercise 1 — Daily revenue

### Objective

Calculate daily revenue.

### Setup

Use an `orders` table with:

```text
order_id
created_at
amount
```

### Task

Write a query producing:

```text
day
revenue
```

### Required reasoning

State:

```text
Input grain:
one row per order

Grouping:
day

Output grain:
one row per day
```

### Solution

```sql
SELECT
    DATE_TRUNC('day', created_at) AS day,
    SUM(amount) AS revenue
FROM orders
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY day;
```

### Edge case

What should happen if a day has no orders?

A grouped table over raw orders will have no row for that day. A complete calendar spine is a later modeling concern.

---

## Exercise 2 — Revenue, orders, customers, AOV

### Objective

Build a country-level KPI.

### Task

Calculate:

- total revenue,
- order count,
- distinct customers,
- average order value

by country.

### Solution

```sql
SELECT
    country,
    SUM(amount) AS revenue,
    COUNT(*) AS order_count,
    COUNT(DISTINCT customer_id) AS customer_count,
    AVG(amount) AS average_order_value
FROM orders
GROUP BY country;
```

### Expected reasoning

```text
Input grain:
one row per order

Output grain:
one row per country
```

---

# Exercise 3 — FILTER

### Objective

Use multiple conditional metrics.

### Task

For each country calculate:

- total orders,
- completed orders,
- cancelled orders,
- completed revenue.

### Solution

```sql
SELECT
    country,
    COUNT(*) AS total_orders,
    COUNT(*) FILTER (
        WHERE status = 'completed'
    ) AS completed_orders,
    COUNT(*) FILTER (
        WHERE status = 'cancelled'
    ) AS cancelled_orders,
    SUM(amount) FILTER (
        WHERE status = 'completed'
    ) AS completed_revenue
FROM orders
GROUP BY country;
```

### Edge case

How should NULL `amount` values in completed orders be interpreted?

Answer according to the business metric definition.

---

# Exercise 4 — HAVING

### Objective

Filter groups after aggregation.

### Task

Find countries with:

```text
more than 1,000 orders
AND
average order value > 500
```

### Solution

```sql
SELECT
    country,
    COUNT(*) AS order_count,
    AVG(amount) AS average_order_value
FROM orders
GROUP BY country
HAVING COUNT(*) > 1000
   AND AVG(amount) > 500;
```

### Expected reasoning

`WHERE` cannot directly use `COUNT(*)` because the count belongs to the group result.

---

# Exercise 5 — ROLLUP

### Objective

Produce detail, subtotal, and grand-total levels.

### Task

Calculate:

```text
country + month
country subtotal
grand total
```

### Solution

```sql
SELECT
    country,
    DATE_TRUNC('month', created_at) AS month,
    SUM(amount) AS revenue,
    GROUPING(country) AS country_grouped,
    GROUPING(DATE_TRUNC('month', created_at)) AS month_grouped
FROM orders
GROUP BY ROLLUP (
    country,
    DATE_TRUNC('month', created_at)
);
```

### Edge case

Do not assume a NULL country is necessarily a subtotal. Use the GROUPING flags.

---

# Exercise 6 — Percentiles

### Objective

Calculate p50 and p95 order value.

### Solution

```sql
SELECT
    country,
    PERCENTILE_CONT(0.50)
        WITHIN GROUP (ORDER BY amount) AS p50,
    PERCENTILE_CONT(0.95)
        WITHIN GROUP (ORDER BY amount) AS p95
FROM orders
GROUP BY country;
```

### Production lesson

If a service-level objective is defined in terms of p95 latency, replacing it with average latency changes the metric.

---

# Exercise 7 — Average of averages

### Objective

Prove why averaging rates can be wrong.

### Setup

```text
region | successful | total
-------+------------+------
A      | 9          | 10
B      | 500        | 1000
```

### Task

Calculate:

```text
average of regional rates
```

and:

```text
overall rate
```

### Solution

Regional rates:

```text
90%
50%
```

Unweighted average:

```text
70%
```

Overall rate:

```text
509 / 1010
≈ 50.396%
```

### Production lesson

Use the metric's underlying numerator and denominator for an overall ratio.

---

# Exercise 8 — NULL behavior

### Objective

Understand how NULL changes aggregation.

### Setup

```text
amount
------
100
NULL
300
0
```

### Task

Calculate:

```text
COUNT(*)
COUNT(amount)
SUM(amount)
AVG(amount)
MIN(amount)
MAX(amount)
```

Then replace NULL with zero and calculate again.

### Discussion

Explain why AVG changes while SUM may not.

---

# Exercise 9 — GROUPING SETS

### Objective

Produce several reporting levels.

### Task

Generate:

```text
country + payment_method
country subtotal
grand total
```

### Solution

```sql
SELECT
    country,
    payment_method,
    SUM(amount) AS revenue
FROM orders
GROUP BY GROUPING SETS (
    (country, payment_method),
    (country),
    ()
);
```

---

# Exercise 10 — CUBE

### Objective

Understand multi-dimensional summaries.

### Task

Use:

```sql
GROUP BY CUBE(country, payment_method)
```

and explain the four expected grouping combinations.

### Expected reasoning

```text
(country, payment_method)
(country)
(payment_method)
()
```

---

# Exercise 11 — Exact versus approximate distinct

### Objective

Reason about exactness.

### Task

Compare:

```sql
COUNT(DISTINCT user_id)
```

with an engine-supported approximate distinct function.

Document:

```text
difference
runtime
memory/cost behavior
business acceptability
```

### Production lesson

The correct choice depends on the allowed error and business consequence.

---

# Exercise 12 — Numeric precision

### Objective

Understand aggregate type safety.

### Task

Create values using:

```text
INTEGER
BIGINT
NUMERIC
DOUBLE PRECISION
```

Aggregate them and examine:

```text
type
precision
range
```

Then explain which representation you would choose for a financial metric and why.

---

# Exercise 13 — Conditional KPI report

### Objective

Build a single production-style grouped query.

### Requirement

For each country return:

```text
orders
completed_orders
cancelled_orders
revenue
completed_revenue
average_order_value
p95_order_value
```

Also calculate:

```text
completed_order_rate
```

using a correct numerator/denominator.

### Validation

Check that:

```text
completed_orders <= orders
cancelled_orders <= orders
completed_order_rate between 0 and 1
```

---

# Exercise 14 — Join + aggregation diagnosis

### Objective

Detect a metric that became inflated after a join.

### Scenario

Revenue was:

```text
1,000,000
```

before a new payment join and:

```text
1,800,000
```

afterward.

### Task

Do not modify the aggregate first.

Investigate:

1. source grain,
2. join grain,
3. duplicate keys,
4. row multiplication,
5. distinct order count,
6. raw revenue before aggregation,
7. corrected grain,
8. final reconciliation.

### Production lesson

The aggregate is often the last place where the problem appears, not the place where it began.

---

# 75. Beginner Practice

Complete at least these 10 tasks without copying the worked examples.

## 1. Count orders

Return total order count.

---

## 2. Sum revenue

Return total revenue.

---

## 3. Average order value

Return average order value.

State how NULL order amounts behave.

---

## 4. Minimum and maximum

Find minimum and maximum order amount.

---

## 5. Count non-NULL email addresses

Compare:

```sql
COUNT(*)
```

and:

```sql
COUNT(email)
```

---

## 6. Distinct customers

Count distinct customers who ordered.

---

## 7. Group by country

Return one row per country with order count.

---

## 8. Group by country and payment method

State the output grain before running the query.

---

## 9. HAVING

Return countries with more than 100 orders.

---

## 10. Conditional count

Count completed orders per country.

For each task, write:

```text
Input grain:
Output grain:
Metric:
```

---

# 76. Intermediate Practice

## 1. Conditional revenue

Calculate completed revenue and cancelled revenue by country.

---

## 2. FILTER

Rewrite CASE-based conditional metrics using FILTER.

---

## 3. NULL versus zero

Compare averages under both interpretations.

---

## 4. Empty aggregate

Create a filter that returns no rows and inspect SUM.

---

## 5. COALESCE

Decide where to use:

```sql
COALESCE(SUM(...), 0)
```

and explain why.

---

## 6. STRING_AGG

Collect product names per customer in alphabetical order.

---

## 7. ARRAY_AGG

Collect product IDs per customer in deterministic order.

---

## 8. Weighted average

Calculate average selling price weighted by units.

---

## 9. Safe ratio

Calculate successful payments / total payments with zero-denominator protection.

---

## 10. Grouped KPI

Build at least eight metrics in one grouped query without changing the intended grain.

---

# 77. Advanced Practice

## 1. GROUPING SETS

Produce three reporting levels in one query.

---

## 2. ROLLUP

Build a hierarchical country/month report with subtotals.

---

## 3. CUBE

Build a two-dimensional cube and explain every grouping level.

---

## 4. GROUPING()

Create real NULL values and subtotal NULL markers and distinguish them.

---

## 5. PERCENTILE_CONT

Calculate p50, p95, and p99 latency by endpoint.

---

## 6. PERCENTILE_DISC

Compare discrete and continuous percentiles on a small dataset.

---

## 7. Approximate distinct

Compare exact and approximate unique-user counts and document the trade-off.

---

## 8. Overflow analysis

Design an aggregate that could exceed the range of its source integer type. Explain how you would make the calculation safe.

---

## 9. Average-of-averages

Take multiple daily metrics and derive the correct monthly aggregate.

---

## 10. Production metric mart

Build a country/month metric table with:

```text
revenue
orders
customers
AOV
p95
completed_rate
```

and include validation assertions for each important relationship.

---

# 78. Debugging Challenges

Diagnose each before looking at the solution.

---

## Challenge 1 — Revenue doubled

Broken:

```sql
SELECT
    SUM(o.amount)
FROM orders AS o
JOIN payments AS p
    ON p.order_id = o.order_id;
```

### Symptom

Revenue doubled.

### Investigation

Ask:

```text
Are multiple payments allowed per order?
```

If yes, an order can appear multiple times.

### Lesson

Aggregation cannot repair a one-to-many join automatically.

---

# Challenge 2 — Customer count too high

Broken:

```sql
SELECT
    COUNT(*) AS customers
FROM orders;
```

### Symptom

The dashboard reports 1 million customers when only 250,000 customers purchased.

### Root cause

Rows were counted instead of distinct entities.

### Corrected

```sql
SELECT
    COUNT(DISTINCT customer_id) AS customers
FROM orders;
```

---

# Challenge 3 — Average too low

Data:

```text
100
300
NULL
```

Someone reports:

```text
133.33
```

### Root cause

NULL was treated as zero.

### Correct result

```text
200
```

if the metric is average over known amounts.

---

# Challenge 4 — "No rows" versus zero

Broken reporting query:

```sql
SELECT SUM(amount)
FROM orders
WHERE status = 'cancelled';
```

The report expects:

```text
0
```

but sees NULL.

### Solution

```sql
SELECT
    COALESCE(SUM(amount), 0)
FROM orders
WHERE status = 'cancelled';
```

### Lesson

Choose the output representation intentionally.

---

# Challenge 5 — Average conversion rate is wrong

Broken:

```sql
SELECT
    AVG(daily_conversion_rate)
FROM daily_metrics;
```

### Root cause

This may weight a day with 10 opportunities the same as a day with 100,000 opportunities.

### Correct approach

```sql
SELECT
    SUM(successful)::numeric
    / NULLIF(SUM(total), 0)
FROM daily_metrics;
```

---

# Challenge 6 — Ratio always shows 0 or 1

Broken:

```sql
SELECT
    successful_orders / total_orders
FROM metrics;
```

### Root cause

Integer division.

### Corrected

```sql
SELECT
    successful_orders::numeric
    / NULLIF(total_orders, 0)
FROM metrics;
```

---

# Challenge 7 — Division by zero

Broken:

```sql
SELECT
    SUM(successful)::numeric / SUM(total)
FROM metrics;
```

### Root cause

`SUM(total)` can be zero.

### Corrected

```sql
SELECT
    SUM(successful)::numeric
    / NULLIF(SUM(total), 0)
FROM metrics;
```

---

# Challenge 8 — Unstable ARRAY_AGG

Broken:

```sql
SELECT
    customer_id,
    ARRAY_AGG(product_id)
FROM order_items
GROUP BY customer_id;
```

### Symptom

Tests occasionally detect a changed array order.

### Solution

```sql
SELECT
    customer_id,
    ARRAY_AGG(product_id ORDER BY product_id)
FROM order_items
GROUP BY customer_id;
```

---

# Challenge 9 — ROLLUP NULL confusion

A report contains:

```text
country = NULL
```

for two different reasons.

### Root cause

A subtotal row and a real NULL country are being mixed.

### Solution

Use:

```sql
GROUPING(country)
```

to distinguish them.

---

# Challenge 10 — Approximate count used for billing

### Symptom

Billing totals differ from the source.

### Root cause

A probabilistic distinct-count function was used where exactness was required.

### Lesson

Approximation must be driven by requirements, not convenience.

---

# 79. Production Case Study

## 79.1 Scenario

An e-commerce company wants a monthly KPI mart.

Available source tables:

```text
customers
orders
order_lines
payments
```

Required output:

```text
one row per country per month
```

Metrics:

```text
total revenue
order count
distinct customers
average order value
card revenue
bank-transfer revenue
p50 order value
p95 order value
payment-success rate
```

---

## 79.2 Step 1 — State input grains

```text
customers
→ one row per customer

orders
→ one row per order

order_lines
→ one row per order line

payments
→ one row per payment
```

---

## 79.3 Step 2 — Define the output grain

```text
one row per country per month
```

---

## 79.4 Step 3 — Define metrics

### Revenue

```text
sum of eligible order amounts
```

### Order count

```text
count of eligible orders
```

### Customer count

```text
distinct customers among eligible orders
```

### Average order value

```text
total eligible order revenue
/
eligible order count
```

### Payment success rate

This must use the business-approved definition. One possible definition is:

```text
successful payments
/
all payment attempts
```

Do not substitute another denominator without agreement.

---

## 79.5 Step 4 — Protect against join multiplication

Suppose the final country/month report only needs `orders` and payment-derived metrics.

Do not join raw:

```text
orders
+
payments
```

and then sum order-level revenue if payments are one-to-many.

Instead, aggregate payment information first.

For example:

```sql
WITH payment_summary AS (
    SELECT
        order_id,
        COUNT(*) AS payment_attempts,
        COUNT(*) FILTER (
            WHERE status = 'succeeded'
        ) AS successful_payments
    FROM payments
    GROUP BY order_id
)
SELECT
    DATE_TRUNC('month', o.created_at) AS month,
    o.country,
    SUM(o.amount) AS revenue,
    COUNT(*) AS order_count,
    COUNT(DISTINCT o.customer_id) AS customer_count,
    SUM(
        CASE
            WHEN o.payment_method = 'card'
            THEN o.amount
            ELSE 0
        END
    ) AS card_revenue,
    SUM(
        CASE
            WHEN o.payment_method = 'bank_transfer'
            THEN o.amount
            ELSE 0
        END
    ) AS bank_transfer_revenue,
    PERCENTILE_CONT(0.50)
        WITHIN GROUP (ORDER BY o.amount) AS p50_order_value,
    PERCENTILE_CONT(0.95)
        WITHIN GROUP (ORDER BY o.amount) AS p95_order_value
FROM orders AS o
LEFT JOIN payment_summary AS ps
    ON ps.order_id = o.order_id
GROUP BY
    DATE_TRUNC('month', o.created_at),
    o.country;
```

For a true payment-success rate, the ratio should be defined at the intended population and grain. A safer explicit formulation is to calculate the numerator and denominator first and then divide them.

---

## 79.6 Step 5 — Separate ratio metrics

For example:

```sql
WITH payment_summary AS (
    SELECT
        order_id,
        COUNT(*) AS payment_attempts,
        COUNT(*) FILTER (
            WHERE status = 'succeeded'
        ) AS successful_payments
    FROM payments
    GROUP BY order_id
),
monthly AS (
    SELECT
        DATE_TRUNC('month', o.created_at) AS month,
        o.country,
        SUM(ps.successful_payments) AS successful_payments,
        SUM(ps.payment_attempts) AS payment_attempts
    FROM orders AS o
    LEFT JOIN payment_summary AS ps
        ON ps.order_id = o.order_id
    GROUP BY
        DATE_TRUNC('month', o.created_at),
        o.country
)
SELECT
    month,
    country,
    successful_payments,
    payment_attempts,
    successful_payments::numeric
        / NULLIF(payment_attempts, 0) AS payment_success_rate
FROM monthly;
```

This makes the metric construction visible.

---

## 79.7 Step 6 — Validate revenue independently

```sql
SELECT
    SUM(amount)
FROM orders;
```

Then compare to the corresponding grouped total after applying the same filters.

---

## 79.8 Step 7 — Validate grouping

```sql
SELECT
    month,
    country,
    COUNT(*) AS rows_per_group
FROM monthly_kpi
GROUP BY
    month,
    country
HAVING COUNT(*) > 1;
```

Expected:

```text
0 rows
```

This proves the output grain is actually one row per country/month.

---

## 79.9 Step 8 — Validate metric relationships

Examples:

```sql
SELECT *
FROM monthly_kpi
WHERE completed_orders > order_count;
```

Expected:

```text
0 rows
```

And:

```sql
SELECT *
FROM monthly_kpi
WHERE payment_success_rate < 0
   OR payment_success_rate > 1;
```

Expected:

```text
0 rows
```

---

# 80. Interview Questions

## 1. What is aggregation?

### Concise answer

Aggregation computes one or more summary values over a set of rows.

### Deeper explanation

Aggregate functions such as `SUM`, `COUNT`, and `AVG` operate over the rows in a group. When combined with GROUP BY, the result contains one output row per grouping combination.

### Example

```sql
SELECT
    country,
    SUM(amount)
FROM orders
GROUP BY country;
```

### Follow-up

> What changed?

The grain changed from order-level input to country-level output.

### Common mistake

Thinking aggregation merely "reduces row count" without identifying the new grain.

---

# 81. Explain COUNT(*) vs COUNT(column).

### Concise answer

`COUNT(*)` counts rows. `COUNT(column)` counts non-NULL values in that column.

### Example

```sql
SELECT
    COUNT(*) AS rows,
    COUNT(email) AS non_null_emails
FROM customers;
```

### Follow-up

> What happens if email is NULL?

That row is not counted by `COUNT(email)`.

### Common mistake

Treating both as row counts.

---

# 82. Explain COUNT(DISTINCT column).

### Concise answer

It counts distinct non-NULL values.

### Engineering use

Use it for entity counts such as:

```sql
COUNT(DISTINCT customer_id)
```

when the metric means unique customers.

### Follow-up

> Why not COUNT(*)?

Because multiple rows can belong to the same customer.

---

# 83. How does AVG treat NULL?

### Concise answer

NULL values do not contribute to the aggregate.

### Example

```text
100, NULL, 300
```

produces:

```text
200
```

### Follow-up

> What if NULL means zero?

Then transform it explicitly according to the business definition, for example with `COALESCE`.

---

# 84. What happens when SUM receives no rows?

### Concise answer

The result is NULL.

### Follow-up

> How can you display zero?

```sql
COALESCE(SUM(amount), 0)
```

### Common mistake

Assuming aggregate SUM always returns zero.

---

# 85. WHERE vs HAVING?

### Concise answer

`WHERE` filters rows before grouping. `HAVING` filters groups after aggregation.

### Example

```sql
WHERE status = 'completed'
```

versus:

```sql
HAVING COUNT(*) > 1000
```

### Follow-up

> Why can't a group count normally be used in WHERE?

Because the grouped result does not exist yet at the WHERE stage.

---

# 86. How does GROUP BY determine grain?

### Concise answer

The grouping columns define the combinations represented by output rows.

### Example

```sql
GROUP BY country
```

means one row per country.

```sql
GROUP BY country, month
```

means one row per country/month combination.

---

# 87. How does conditional aggregation work?

### Concise answer

It computes metrics over only the rows satisfying a condition.

### Example

```sql
SUM(amount) FILTER (
    WHERE status = 'completed'
)
```

or:

```sql
SUM(
    CASE
        WHEN status = 'completed' THEN amount
        ELSE 0
    END
)
```

### Follow-up

> Which is more readable?

The answer depends on team conventions, but FILTER often expresses the condition directly.

---

# 88. FILTER vs CASE WHEN?

### Concise answer

Both can express conditional aggregation.

FILTER applies a condition to the aggregate itself. CASE changes each row's expression before the aggregate.

### Follow-up

> Which is more portable?

Always verify target-engine support and syntax rather than assuming all engines are identical.

---

# 89. How would you implement a pivot without PIVOT?

### Concise answer

Use conditional aggregation.

Example:

```sql
SUM(amount) FILTER (
    WHERE payment_method = 'card'
)
```

### Follow-up

> Why might DuckDB PIVOT be preferred?

It can be more concise for some pivot transformations.

---

# 90. Why should ARRAY_AGG often have ORDER BY?

### Concise answer

To make the aggregated collection deterministic.

### Example

```sql
ARRAY_AGG(product_id ORDER BY product_id)
```

### Follow-up

> Why does deterministic order matter?

For repeatability, tests, downstream comparisons, and reproducibility.

---

# 91. What are p50 and p95?

### Concise answer

They are percentile-based distribution metrics. p50 describes the midpoint; p95 describes a high-tail threshold according to the percentile definition.

### Follow-up

> Why not use average latency?

Because average can hide the tail of the distribution.

---

# 92. PERCENTILE_CONT vs PERCENTILE_DISC?

### Concise answer

`PERCENTILE_CONT` can interpolate between ordered values; `PERCENTILE_DISC` returns an observed value according to its discrete percentile definition.

### Follow-up

> Why verify engine semantics?

Ordered-set aggregate implementations and edge-case details can be dialect-specific.

---

# 93. What are GROUPING SETS?

### Concise answer

They allow one query to return several explicitly chosen grouping levels.

### Example

```sql
GROUP BY GROUPING SETS (
    (country, month),
    (country),
    ()
)
```

---

# 94. ROLLUP vs CUBE?

### Concise answer

`ROLLUP` generates hierarchical subtotal levels. `CUBE` generates combinations of the listed dimensions.

### Example

```text
ROLLUP(country, month)
→ country/month, country, total

CUBE(country, payment_method)
→ country/payment, country, payment, total
```

---

# 95. What does GROUPING() do?

### Concise answer

It identifies whether a grouping column was rolled up in a subtotal/grand-total row.

### Engineering use

It distinguishes:

```text
real NULL data
```

from:

```text
NULL used as subtotal marker
```

---

# 96. What is approximate distinct counting?

### Concise answer

It estimates the number of distinct values using a probabilistic algorithm instead of calculating the exact count.

### Follow-up

> When is it appropriate?

When the business accepts bounded error and the scale/cost of exact counting is too high.

---

# 97. What is HyperLogLog?

### Concise answer

A probabilistic cardinality-estimation technique that uses a compact summary to estimate the number of distinct values.

### Follow-up

> Why is it useful?

It can dramatically reduce memory needed for large distinct-count estimates.

---

# 98. Why is averaging percentages dangerous?

### Concise answer

Because different groups can represent very different numbers of observations.

### Correct approach

For an overall rate:

```text
SUM(successes)
/
SUM(total opportunities)
```

subject to the metric definition.

---

# 99. Explain average-of-averages.

### Concise answer

An unweighted average of group averages gives every group equal weight, which can be wrong when group sizes differ.

### Example

```text
10 observations at 90%
1000 observations at 50%
```

The overall rate is nowhere near the simple average of the two percentages.

---

# 100. How do you calculate a weighted average?

### Concise answer

```sql
SUM(value * weight)
/
SUM(weight)
```

with zero-denominator protection when appropriate:

```sql
SUM(value * weight)
/
NULLIF(SUM(weight), 0)
```

---

# 101. Why use NULLIF for ratios?

### Concise answer

To avoid division by zero while preserving an undefined result as NULL.

### Example

```sql
SUM(successful)::numeric
/
NULLIF(SUM(total), 0)
```

### Follow-up

> Why not use zero?

Because zero implies a measured zero rate, while NULL can correctly represent an undefined ratio.

---

# 102. NUMERIC vs DOUBLE PRECISION?

### Concise answer

`NUMERIC` provides exact decimal arithmetic semantics; `DOUBLE PRECISION` is binary floating-point and is often appropriate when approximation is acceptable.

### Typical financial choice

Use an appropriate exact decimal type for exact monetary calculations.

### Follow-up

> Is DOUBLE always wrong?

No. It depends on the application's precision requirements.

---

# 103. How can aggregation overflow?

### Concise answer

The aggregate result can exceed the numeric range of the data type used to represent it.

### Follow-up

> What should you inspect?

Source type, aggregate return type, maximum expected volume, and destination type.

---

# 104. What is GROUP BY ALL?

### Concise answer

A dialect convenience supported by engines such as DuckDB that groups by all non-aggregate selected expressions.

### Follow-up

> Is it standard SQL?

Treat it as dialect-specific.

---

# 105. What are the risks of GROUP BY 1, 2?

### Concise answer

It depends on select-list position, so reordering columns can change grouping semantics or make the query harder to review.

### Follow-up

> What is usually clearer?

Explicit grouping expressions.

---

# 106. How can join explosion corrupt aggregates?

### Concise answer

If a business fact appears multiple times before aggregation, `SUM` and other row-sensitive metrics may count it multiple times.

### Follow-up

> How do you fix it?

Repair the join grain, often by pre-aggregating independent child tables before joining.

---

# 107. Production Checklist

Before shipping an aggregation query, verify:

- [ ] Input grain is known.
- [ ] Output grain is known.
- [ ] Grouping columns define the intended output grain.
- [ ] The metric has a written mathematical/business definition.
- [ ] Rows entering the aggregation are the correct rows.
- [ ] Any joins before aggregation have been reviewed for multiplication.
- [ ] `COUNT(*)` versus `COUNT(column)` is intentional.
- [ ] `COUNT(DISTINCT ...)` is used when entity uniqueness is required.
- [ ] NULL behavior is intentional.
- [ ] NULL is not blindly interpreted as zero.
- [ ] Empty-input behavior is known.
- [ ] `COALESCE` is used only when its semantic meaning is correct.
- [ ] `WHERE` is used for row filtering.
- [ ] `HAVING` is used for group filtering.
- [ ] Conditional aggregation uses the correct condition.
- [ ] FILTER/CASE semantics are understood.
- [ ] STRING_AGG output is deterministic where needed.
- [ ] ARRAY_AGG output is deterministic where needed.
- [ ] Percentile semantics are appropriate.
- [ ] ROLLUP/CUBE/Grouping Sets are interpreted correctly.
- [ ] `GROUPING()` is used when subtotal NULLs could be confused with real NULLs.
- [ ] Exact versus approximate aggregation is a deliberate decision.
- [ ] Approximate metrics are not used for metrics requiring exactness.
- [ ] Ratio numerator and denominator are correct.
- [ ] Division by zero is handled.
- [ ] Integer division is not silently truncating the metric.
- [ ] Numeric precision is appropriate.
- [ ] Overflow risk has been considered.
- [ ] The chosen numeric type matches the business semantics.
- [ ] Dialect-specific syntax is clearly identified.
- [ ] Reconciliation checks exist for critical totals.
- [ ] Assertion queries return zero rows when the invariant holds.
- [ ] A tiny test dataset was used to verify tricky semantics.

---

# 108. Final Knowledge Check

Do this without looking at your notes.

## Theory

1. What does aggregation do to the grain of a dataset?
2. What is the difference between input grain and output grain?
3. What does `COUNT(*)` count?
4. What does `COUNT(column)` count?
5. What does `COUNT(DISTINCT column)` count?
6. How do NULL values affect `SUM`?
7. How do NULL values affect `AVG`?
8. Why is `AVG(100, NULL, 300)` 200 rather than 133.33?
9. What happens when `SUM` receives no rows?
10. Why might `COALESCE(SUM(amount), 0)` be appropriate?
11. Why might it be semantically wrong?
12. What is the difference between WHERE and HAVING?
13. What does GROUP BY country mean about output grain?
14. What does GROUP BY country, month mean about output grain?
15. What is conditional aggregation?
16. How does FILTER work?
17. How would you build a pivot-style report without PIVOT?
18. Why can STRING_AGG ordering matter?
19. Why can ARRAY_AGG ordering matter?
20. What is PERCENTILE_CONT?
21. What is PERCENTILE_DISC?
22. What does WITHIN GROUP mean conceptually?
23. What is MODE?
24. What does STDDEV tell you?
25. What are GROUPING SETS?
26. What is ROLLUP?
27. What is CUBE?
28. What does GROUPING() tell you?
29. Why can subtotal NULL be confused with real NULL?
30. What is approximate aggregation?
31. What is approximate distinct counting?
32. What problem does HyperLogLog address?
33. When is approximation acceptable?
34. Why is average-of-averages dangerous?
35. How do you construct an overall ratio correctly?
36. Why use NULLIF in ratios?
37. What is integer division?
38. Why can aggregation overflow?
39. Why use NUMERIC for exact financial decimal semantics?
40. When might DOUBLE PRECISION be appropriate?
41. What is GROUP BY ALL?
42. What is the risk of GROUP BY 1, 2?
43. How can a join corrupt an aggregate?
44. How do you validate an aggregate result?

---

## Practical tasks

### Task 1 — Revenue

Write total revenue.

---

### Task 2 — Entity counts

Write both:

```text
number of orders
number of unique customers
```

Explain why they differ.

---

### Task 3 — Group grain

Write a query for:

```text
one row per country per month
```

State the grain before executing.

---

### Task 4 — HAVING

Find groups with:

```text
more than 1,000 records
```

---

### Task 5 — Conditional metrics

Calculate:

```text
completed
cancelled
pending
```

in one grouped query.

---

### Task 6 — FILTER

Rewrite the previous query using FILTER.

---

### Task 7 — NULL

Given:

```text
100
NULL
0
300
```

predict:

```text
COUNT(*)
COUNT(value)
SUM(value)
AVG(value)
```

---

### Task 8 — Empty input

Produce a SUM query where no rows match and explain the result.

---

### Task 9 — Ratio

Calculate:

```text
successful / total
```

with integer-division and zero-denominator protection.

---

### Task 10 — Average-of-averages

Given several daily conversion rates and denominators, calculate the correct monthly conversion rate.

---

### Task 11 — GROUPING SETS

Generate:

```text
country/payment_method
country
grand total
```

---

### Task 12 — ROLLUP

Generate:

```text
country/month
country
grand total
```

and distinguish subtotal rows.

---

### Task 13 — CUBE

Generate all combinations of:

```text
country
payment_method
```

---

### Task 14 — Percentiles

Calculate:

```text
p50
p95
```

for order value.

---

### Task 15 — Approximate distinct

Explain whether you would use approximate distinct counting for:

```text
a dashboard
billing
```

and why.

---

### Task 16 — Precision

Choose between:

```text
NUMERIC
DOUBLE PRECISION
```

for:

```text
invoice amount
sensor measurement
```

and defend each choice.

---

# 109. Final Checkpoint — Ready for Topic 04?

The Module 2.6 roadmap defines these checkpoint capabilities.

You must be able to:

- [ ] Explain `COUNT(*)` vs `COUNT(col)` vs `COUNT(DISTINCT col)`.
- [ ] Explain `WHERE` vs `HAVING`.
- [ ] Write conditional aggregation with `FILTER`.
- [ ] Produce subtotals with `ROLLUP` or `GROUPING SETS`.
- [ ] Compute a correct ratio metric across groups.

You should also be able to demonstrate each one with actual SQL.

---

## Checkpoint Gate 1 — COUNT

Given a table containing:

```text
duplicates
NULLs
multiple customers
```

you can correctly choose among:

```sql
COUNT(*)
COUNT(column)
COUNT(DISTINCT column)
```

without guessing.

---

## Checkpoint Gate 2 — WHERE vs HAVING

Given:

```text
status = completed
group_count > 1000
```

you can correctly place:

```text
status filter → WHERE
group-count filter → HAVING
```

and explain why.

---

## Checkpoint Gate 3 — FILTER

You can write:

```sql
COUNT(*) FILTER (WHERE ...)
```

and:

```sql
SUM(amount) FILTER (WHERE ...)
```

and explain which rows contribute.

---

## Checkpoint Gate 4 — Subtotals

You can write:

```sql
ROLLUP(...)
```

or:

```sql
GROUPING SETS(...)
```

and explain the grain of each output level.

---

## Checkpoint Gate 5 — Ratio

You can calculate:

```sql
SUM(numerator)::numeric
/
NULLIF(SUM(denominator), 0)
```

and explain:

- why the numerator is summed,
- why the denominator is summed,
- why integer division is dangerous,
- why zero needs explicit handling,
- and when the business definition might use a different denominator.

---

## Do Not Move On Yet If

You still think:

```text
GROUP BY = just syntax
AVG = always SUM / total rows
NULL = zero
COUNT(*) = customer count
HAVING = another WHERE
DISTINCT = a safe aggregation fix
```

Those misunderstandings will cause problems in every later module.

---

# 110. Common Mistakes — Final Summary

Remember these rules:

```text
1. Aggregation changes grain.
2. The grouping columns define the output grain.
3. COUNT(*) counts rows.
4. COUNT(column) counts non-NULL values.
5. COUNT(DISTINCT column) counts distinct non-NULL values.
6. NULL is not zero.
7. AVG does not automatically count NULL as zero.
8. SUM over no rows can return NULL.
9. COALESCE changes the output meaning and should be intentional.
10. WHERE filters rows.
11. HAVING filters groups.
12. Conditional aggregation is a core production SQL pattern.
13. FILTER often makes conditional metrics clearer.
14. Collection aggregates should be explicitly ordered when deterministic output matters.
15. Percentiles and averages answer different questions.
16. GROUPING() distinguishes subtotal markers from real NULLs.
17. Approximate aggregation is a requirements decision.
18. Never average averages blindly.
19. Ratios need correct numerators and denominators.
20. Protect ratios from division by zero.
21. Cast before division when needed.
22. Consider numeric precision and overflow.
23. Exact financial values generally require exact decimal semantics.
24. GROUP BY ALL and similar conveniences are dialect-specific.
25. Ordinal grouping can reduce readability.
26. A correct aggregate over an incorrect joined row set is still wrong.
27. Validate totals and invariants instead of trusting a plausible-looking number.
```

---

# Final Mental Model

When you write an aggregation query, think in this order:

```text
1. What does one input row represent?
        ↓
2. Which rows should contribute?
        ↓
3. What grouping dimensions define the output?
        ↓
4. What will one output row represent?
        ↓
5. What exactly is the metric definition?
        ↓
6. How do NULLs behave?
        ↓
7. Are there duplicate rows before aggregation?
        ↓
8. Is the mathematical formula correct?
        ↓
9. Are numerator and denominator at compatible grains?
        ↓
10. Are numeric types safe?
        ↓
11. Is approximation acceptable?
        ↓
12. Can I reconcile the result independently?
        ↓
13. What assertion should return zero rows when correct?
```

The senior Data Engineering habit is not:

> "I know how to use GROUP BY."

It is:

> **"I know what one input row means, what one output row means, which rows contribute to every metric, how NULLs affect the calculation, and how to prove the result is mathematically and operationally correct."**
