# 05 — Window Functions: Ranking, Running Totals, and LAG / LEAD

> **Stage 2 — Python for Data Engineering**  
> **Module 2.6 — SQL for Data Engineers**  
> **Topic 05 — Window functions: ranking, running totals, LAG / LEAD**  
> **Primary environments:** PostgreSQL 16+ and DuckDB

---

## 1. Learning Objectives

By the end of this chapter, you should be able to:

- Explain why window functions exist.
- State the input grain and output grain before writing a window query.
- Explain the difference between `GROUP BY` and window functions.
- Read and write `OVER (...)`.
- Use `PARTITION BY` to define independent logical populations.
- Use `ORDER BY` inside a window to define calculation order.
- Distinguish window ordering from the final query `ORDER BY`.
- Use:
  - `ROW_NUMBER`
  - `RANK`
  - `DENSE_RANK`
  - `NTILE`
  - `PERCENT_RANK`
  - `CUME_DIST`
- Explain how ties affect each ranking/distribution function.
- Use `LAG` and `LEAD` with offsets and defaults.
- Use:
  - `FIRST_VALUE`
  - `LAST_VALUE`
  - `NTH_VALUE`
- Use aggregate functions as window functions:
  - `SUM`
  - `AVG`
  - `MIN`
  - `MAX`
  - `COUNT`
- Calculate running totals and shares of totals.
- Explain the three dimensions of a window specification:
  - partition,
  - order,
  - frame.
- Distinguish:
  - `ROWS`
  - `RANGE`
  - `GROUPS`
- Build moving averages.
- Build time-based `RANGE` windows with intervals where supported.
- Explain the default-frame behavior relevant to ordered windows.
- Diagnose the `LAST_VALUE` default-frame trap.
- Filter window results correctly with a CTE or subquery.
- Use `QUALIFY` where the target engine supports it.
- Solve top-N-per-group problems.
- Find the latest record per key deterministically.
- Solve gaps-and-islands problems.
- Calculate consecutive streaks.
- Sessionize event streams.
- Calculate period-over-period changes:
  - month-over-month,
  - year-over-year.
- Build a basic cohort-retention analysis.
- Make window ordering deterministic with tie-breakers.
- Reuse window definitions with named windows.
- Explain why multiple different window specifications may require additional processing or sorting.
- Reason about memory, partition size, and production scale.
- Debug window queries systematically.
- Write zero-row assertion queries for important invariants.

The central habit of this chapter is:

> **Before evaluating a window function, ask: What is the partition? What is the order? What is the frame? What does the function calculate from those rows?**

---

## 2. Why Window Functions Matter in Data Engineering

Many data-engineering questions require information about neighboring or related rows while still returning the current row.

Examples:

- “What is this customer's previous order?”
- “What is this product's rank in its country?”
- “What was the cumulative revenue at this point in time?”
- “What was the latest state for this customer?”
- “How long since the previous event?”
- “What is the longest streak of active days?”
- “When did a new user session start?”
- “How much did revenue change from last month?”
- “What percentage of the cohort remained active?”

A `GROUP BY` query is excellent when you want to collapse many rows into summary rows.

A window function is useful when you want to keep those rows and attach contextual information to each one.

Think:

```text
GROUP BY
many rows
    ↓
fewer rows
    ↓
summary grain

Window function
many rows
    ↓
same rows
    +
context about related rows
```

This distinction appears repeatedly in production SQL:

```text
raw events
   ↓
cleaned rows
   ↓
ordered rows
   ↓
window calculations
   ↓
business metric
```

Window functions are therefore not just an analytics feature. They are a major tool for:

- deterministic latest-record selection;
- incremental transformation logic;
- sequence analysis;
- deduplication patterns;
- operational event analysis;
- retention;
- ranking;
- cumulative metrics;
- historical reasoning.

The hardest part is usually not syntax.

The hardest part is defining the correct:

```text
grain
partition
order
frame
```

---

## 3. The Core Mental Model

A window function:

> **looks at a related set of rows for each current row, computes a value using that window, and attaches the result back to the current row.**

Consider:

```text
customer | order_date | amount
---------+------------+-------
A        | Jan 1      | 100
A        | Jan 3      | 200
A        | Jan 7      |  50
B        | Jan 2      | 400
B        | Jan 5      | 100
```

Now:

```sql
SELECT
    customer,
    order_date,
    amount,
    SUM(amount) OVER (
        PARTITION BY customer
        ORDER BY order_date
    ) AS running_total
FROM orders;
```

Conceptually:

```text
A Jan 1 → 100
A Jan 3 → 300
A Jan 7 → 350

B Jan 2 → 400
B Jan 5 → 500
```

The rows remain:

```text
5 input rows
↓
5 output rows
```

Only an additional column is attached.

### The per-current-row mental model

For the row:

```text
A | Jan 3 | 200
```

the window says:

```text
partition = customer A

ordered rows:
Jan 1 | 100
Jan 3 | 200
Jan 7 |  50

current row = Jan 3

frame:
Jan 1 → Jan 3

SUM:
100 + 200 = 300
```

This mental model is more useful than memorizing syntax.

---

## 4. GROUP BY vs Window Functions

This is the most important contrast in the chapter.

### `GROUP BY`

```sql
SELECT
    customer_id,
    SUM(amount) AS customer_total
FROM orders
GROUP BY customer_id;
```

If there are:

```text
100 orders
20 customers
```

the result might have:

```text
20 rows
```

The grain changed from:

```text
one row per order
```

to:

```text
one row per customer
```

### Window function

```sql
SELECT
    order_id,
    customer_id,
    amount,
    SUM(amount) OVER (
        PARTITION BY customer_id
    ) AS customer_total
FROM orders;
```

The result still has:

```text
100 rows
```

because the grain stays:

```text
one row per order
```

Each order now carries the customer-level total.

### Comparison

| Property | `GROUP BY` | Window function |
|---|---|---|
| Collapses rows | Yes | No |
| Changes output grain | Usually yes | Usually no |
| Returns one result per group | Yes | No |
| Keeps current row | No, unless regrouped | Yes |
| Good for summaries | Yes | Sometimes |
| Good for neighboring-row context | No | Yes |
| Good for ranking within a population | No | Yes |
| Good for running totals | Not by itself | Yes |

### Engineering rule

Before writing a window query, say:

> **“One row represents ______.”**

Then ask:

> **“Do I want that row to remain visible?”**

If yes, a window function may be the right abstraction.

---

## 5. Anatomy of `OVER(...)`

A window function commonly looks like:

```sql
function(...) OVER (
    PARTITION BY ...
    ORDER BY ...
    frame
)
```

For example:

```sql
SUM(amount) OVER (
    PARTITION BY customer_id
    ORDER BY order_date, order_id
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
)
```

Break it into four ideas:

```text
function
    ↓
SUM(amount)

partition
    ↓
customer_id

order
    ↓
order_date, order_id

frame
    ↓
from partition start
to current row
```

The clauses are independent concepts.

### Not every window needs every clause

This is valid:

```sql
COUNT(*) OVER ()
```

It means:

```text
count rows over the entire input relation
```

This is valid:

```sql
COUNT(*) OVER (
    PARTITION BY country
)
```

It means:

```text
count rows within each country
```

This is valid:

```sql
ROW_NUMBER() OVER (
    PARTITION BY country
    ORDER BY revenue DESC
)
```

The ranking needs ordering, but it does not require a frame clause.

### Grain-first description

A good engineering description is:

```text
Input grain:
one row per order

Partition:
customer_id

Ordering:
order_date, order_id

Frame:
from partition start to current row

Output grain:
one row per order
```

That description should exist in your head before the SQL.

---

## 6. `PARTITION BY`

`PARTITION BY` divides rows into independent logical windows.

Example:

```sql
ROW_NUMBER() OVER (
    PARTITION BY country
    ORDER BY revenue DESC
)
```

means:

```text
India
    rank starts at 1
    continues within India only

Nepal
    rank starts at 1
    continues within Nepal only
```

### No `PARTITION BY`

```sql
ROW_NUMBER() OVER (
    ORDER BY revenue DESC
)
```

means:

```text
one global ranking
```

Every row participates in the same ordered population.

### Partition is not database partitioning

Do not confuse:

```sql
PARTITION BY
```

inside a window with:

```text
table partitioning
```

The former is a logical window concept.

The latter is a physical storage/layout concept.

They solve different problems.

### Example

```sql
SELECT
    country,
    product_id,
    revenue,
    ROW_NUMBER() OVER (
        PARTITION BY country
        ORDER BY revenue DESC, product_id
    ) AS country_position
FROM product_revenue;
```

If the data is:

```text
country | product | revenue
--------+---------+--------
IN      | A       | 100
IN      | B       |  80
NP      | C       | 120
NP      | D       |  90
```

the ranks are:

```text
IN A → 1
IN B → 2

NP C → 1
NP D → 2
```

The window restarts for each country.

---

## 7. `ORDER BY` Inside a Window

There are two different `ORDER BY` concepts.

### Window `ORDER BY`

```sql
ROW_NUMBER() OVER (
    ORDER BY created_at
)
```

This defines how the window function sees the rows.

### Final query `ORDER BY`

```sql
SELECT ...
FROM orders
ORDER BY created_at;
```

This defines the presentation order of the final result.

These are not the same thing.

### Example

```sql
SELECT
    order_id,
    customer_id,
    amount,
    ROW_NUMBER() OVER (
        PARTITION BY customer_id
        ORDER BY amount DESC
    ) AS customer_rank
FROM orders
ORDER BY order_id;
```

The ranking is by amount descending within each customer.

The final output is displayed by `order_id`.

So:

```text
window ORDER BY
→ calculation semantics

final ORDER BY
→ result presentation
```

### Production implication

A query can calculate the correct ranking while displaying rows in a completely different order.

Never assume the final result order tells you how the window calculation was performed.

---

## 8. `ROW_NUMBER`

`ROW_NUMBER()` assigns a unique sequence number to each row in the window.

```sql
ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY created_at DESC
)
```

Typical uses:

- latest record per key;
- top N rows;
- deterministic survivor selection;
- sequence numbers;
- event ordering.

### Example

```text
customer | order | date
---------+-------+----------
A        | 10    | Jan 10
A        | 11    | Jan 12
A        | 12    | Jan 15
```

```sql
ROW_NUMBER() OVER (
    PARTITION BY customer
    ORDER BY date
)
```

gives:

```text
A | order 10 | 1
A | order 11 | 2
A | order 12 | 3
```

### Critical issue: ties

Suppose:

```text
customer | order | created_at
---------+-------+----------------
A        | 10    | 2026-09-01 10:00
A        | 11    | 2026-09-01 10:00
```

Then:

```sql
ROW_NUMBER() OVER (
    PARTITION BY customer
    ORDER BY created_at
)
```

does not define how order 10 and order 11 should be ranked relative to each other.

Add a tie-breaker:

```sql
ROW_NUMBER() OVER (
    PARTITION BY customer
    ORDER BY created_at DESC, order_id DESC
)
```

Now the order is deterministic, assuming `order_id` is unique.

### Rule

> **If the ordering carries business meaning, make the ordering total and deterministic.**

---

## 9. `RANK`

`RANK()` gives tied rows the same rank.

Example:

```text
scores
------
100
100
90
80
```

```sql
RANK() OVER (
    ORDER BY score DESC
)
```

produces:

```text
score | rank
------+-----
100   | 1
100   | 1
90    | 3
80    | 4
```

The next rank after a two-row tie skips a number.

### When this is useful

Use `RANK` when:

> tied values should occupy the same position, and gaps in rank are meaningful.

Examples:

- competition ranking;
- leaderboard position;
- top-N by rank where all ties at the cutoff should survive.

---

## 10. `DENSE_RANK`

`DENSE_RANK()` also gives tied rows the same rank, but does not leave gaps.

For:

```text
100
100
90
80
```

you get:

```text
score | dense_rank
------+-----------
100   | 1
100   | 1
90    | 2
80    | 3
```

### Comparison with `RANK`

```text
Values:
100, 100, 90, 80

ROW_NUMBER:
1, 2, 3, 4

RANK:
1, 1, 3, 4

DENSE_RANK:
1, 1, 2, 3
```

### Engineering interpretation

- `ROW_NUMBER`: unique row position.
- `RANK`: tied positions, gaps after ties.
- `DENSE_RANK`: tied positions, no gaps.

The correct function depends on the business definition.

---

## 11. `NTILE`

`NTILE(n)` divides ordered rows into approximately equal-sized buckets.

Example:

```sql
NTILE(4) OVER (
    ORDER BY revenue
)
```

can divide data into four buckets:

```text
1 → low bucket
2 → next bucket
3 → next bucket
4 → high bucket
```

This can support:

- quartile-style segmentation;
- deciles;
- approximate equal-row cohorts;
- ordered bucketing.

### Important warning

`NTILE(4)` is not the same thing as calculating an exact 25th/50th/75th percentile.

It creates row-count buckets.

A percentile asks about a position in the value distribution.

That distinction matters.

### Remainders

If 10 rows are divided into 4 buckets, the rows cannot be divided perfectly evenly.

Some buckets receive one extra row.

Therefore:

```text
NTILE
→ approximately equal row counts
```

not:

```text
equal numeric width
```

and not:

```text
exact percentile value boundaries
```

---

## 12. `PERCENT_RANK`

`PERCENT_RANK()` expresses the relative rank position of a row.

Conceptually:

```text
lowest position
→ 0

highest position
→ 1
```

It is based on rank rather than simply assigning equal-size row buckets.

Example:

```sql
PERCENT_RANK() OVER (
    ORDER BY revenue
)
```

A conceptual result might look like:

```text
revenue | percent_rank
--------+-------------
100     | 0
200     | 0.25
300     | 0.50
400     | 0.75
500     | 1
```

The exact values depend on row count and ties.

### Why it differs from `NTILE`

`NTILE(4)` says:

```text
put rows into four buckets
```

`PERCENT_RANK()` says:

```text
where does this row sit in the ordered rank distribution?
```

Do not substitute one for the other without checking the business definition.

---

## 13. `CUME_DIST`

`CUME_DIST()` returns the proportion of rows whose ordering value is less than or equal to the current row's value.

Example:

```sql
CUME_DIST() OVER (
    ORDER BY revenue
)
```

Suppose:

```text
revenue
-------
100
200
200
400
```

Conceptually:

```text
100 → 1/4
200 → 3/4
200 → 3/4
400 → 4/4
```

The two `200` rows share the same cumulative distribution because the peer group is included together.

### Compare to `PERCENT_RANK`

A useful mental distinction:

```text
PERCENT_RANK
→ relative rank position

CUME_DIST
→ fraction of rows at or below the current ordering value
```

The two measures can be similar but are not interchangeable.

---

## 14. Ranking and Ties

Ties are not a cosmetic detail.

They affect:

- `ROW_NUMBER`;
- `RANK`;
- `DENSE_RANK`;
- `PERCENT_RANK`;
- `CUME_DIST`;
- latest-record selection;
- top-N outputs;
- running calculations;
- `LAG` / `LEAD` interpretation;
- reproducibility.

### Tiny tie example

```text
product | revenue
--------+--------
A       | 100
B       | 100
C       |  90
D       |  80
```

Questions to ask:

```text
Do ties share rank?

Should exactly three rows be returned?

Should every product tied at third place be returned?

Does a tie need deterministic row ordering?
```

These questions lead to different SQL.

### Deterministic ordering

For exact row selection:

```sql
ROW_NUMBER() OVER (
    ORDER BY revenue DESC, product_id
)
```

For rank-as-a-business-position:

```sql
RANK() OVER (
    ORDER BY revenue DESC
)
```

Do not add a unique tie-breaker to `RANK` without understanding the consequence: it changes what SQL treats as a peer.

---

## 15. `LAG`

`LAG` returns a value from an earlier row within the current ordered window.

Precise definition:

> `LAG` evaluates the window ordering and returns the value of an expression from a row at a specified offset before the current row within the current partition.

Example:

```sql
LAG(amount) OVER (
    PARTITION BY customer_id
    ORDER BY order_date, order_id
)
```

### Example

```text
customer | order_date | amount
---------+------------+-------
A        | Jan 1      | 100
A        | Jan 3      | 200
A        | Jan 7      |  50
```

Then:

```text
Jan 1 → previous = NULL
Jan 3 → previous = 100
Jan 7 → previous = 200
```

### Difference from `MAX`

Do not confuse:

```sql
LAG(amount)
```

with:

```sql
MAX(amount)
```

`LAG` is position-based.

It asks:

> What was the value at an earlier ordered position?

It does not ask:

> What was the largest value seen so far?

---

## 16. `LEAD`

`LEAD` is the forward-looking counterpart of `LAG`.

```sql
LEAD(amount) OVER (
    PARTITION BY customer_id
    ORDER BY order_date, order_id
)
```

Conceptually:

```text
current row
    ↓
look forward
    ↓
return a later row's value
```

Typical uses:

- next event;
- next order;
- next state;
- time until next event;
- transition analysis;
- valid-until calculations.

### Example

```text
customer | date | amount
---------+------+-------
A        | 1    | 100
A        | 2    | 200
A        | 3    | 300
```

`LEAD(amount)` gives:

```text
1 → 200
2 → 300
3 → NULL
```

---

## 17. Defaults in `LAG` and `LEAD`

Both functions support:

```text
expression
offset
default
```

For example:

```sql
LAG(amount, 1, 0) OVER (
    PARTITION BY customer_id
    ORDER BY order_date
)
```

means:

```text
offset = 1 row backward
default = 0 if that row does not exist
```

### Multiple offsets

```sql
LAG(amount, 2) OVER (...)
```

means:

```text
two rows backward
```

Similarly:

```sql
LEAD(amount, 3, 0) OVER (...)
```

means:

```text
three rows forward
default to 0 if unavailable
```

### Be careful with semantic defaults

A default of `0` should mean something.

For the first order, a “previous revenue” of zero may be useful for a business metric.

But for an unknown previous measurement, converting absence to zero may hide important information.

Use:

```text
NULL
```

when absence is meaningful.

Use:

```text
0
```

only when the business definition says “no previous value” should behave as zero.

---

## 18. `FIRST_VALUE`

`FIRST_VALUE` returns the expression associated with the first row of the relevant frame according to window ordering.

```sql
FIRST_VALUE(amount) OVER (
    PARTITION BY customer_id
    ORDER BY order_date, order_id
)
```

Potential uses:

- first purchase amount;
- first status;
- initial event;
- cohort entry value.

### Frame matters

Like other value functions, `FIRST_VALUE` is affected by the frame.

A strong mental model is:

```text
partition
→ order rows
→ determine frame
→ identify first row visible to current row
→ return expression from that row
```

If your business definition is “the first value of the whole customer history,” make sure the frame actually covers that intended history.

---

## 19. `LAST_VALUE`

`LAST_VALUE` is where many otherwise strong SQL learners get surprised.

Example:

```sql
LAST_VALUE(amount) OVER (
    PARTITION BY customer_id
    ORDER BY order_date
)
```

Many learners read that as:

> “Return the last amount in the customer's entire history.”

That is not necessarily what the frame says.

### The critical idea

`LAST_VALUE` returns:

> the value from the **last row of the current window frame**.

If the default frame ends at the current row or peer group, then the “last row” can be the current row or current peer group.

That can make the function appear broken even when SQL is behaving exactly according to the frame.

### Explicit whole-partition frame

If the business requirement is:

> “Give me the final value in the whole partition on every row,”

make the frame explicit:

```sql
LAST_VALUE(amount) OVER (
    PARTITION BY customer_id
    ORDER BY order_date, order_id
    ROWS BETWEEN UNBOUNDED PRECEDING
             AND UNBOUNDED FOLLOWING
)
```

Now the frame covers the whole partition.

### Engineering rule

When using `LAST_VALUE`, ask:

```text
Do I mean:
last value in the current frame?
or
last value in the whole partition?
```

Do not rely on memory of a simplified default-frame rule.

---

## 20. `NTH_VALUE`

`NTH_VALUE(expression, n)` returns the expression from the nth row in the current frame according to window ordering.

Example:

```sql
NTH_VALUE(amount, 2) OVER (
    PARTITION BY customer_id
    ORDER BY order_date, order_id
)
```

This asks for:

```text
the second value visible in the frame
```

### Edge case

If fewer than two rows are visible in the relevant frame, the result can be `NULL`.

### Frame dependence

Like `FIRST_VALUE` and `LAST_VALUE`, `NTH_VALUE` is frame-sensitive.

If the business requirement refers to the second value of the entire partition, ensure the frame actually covers the entire partition.

---

## 21. Aggregate Window Functions

Ordinary aggregate functions can become window functions by adding `OVER (...)`:

```sql
SUM(amount) OVER (...)
AVG(amount) OVER (...)
MIN(amount) OVER (...)
MAX(amount) OVER (...)
COUNT(*) OVER (...)
```

### Example

```sql
SELECT
    order_id,
    customer_id,
    amount,
    SUM(amount) OVER (
        PARTITION BY customer_id
    ) AS customer_total
FROM orders;
```

The `SUM` is calculated per customer, but the output still has one row per order.

### Aggregate vs windowed aggregate

```sql
SUM(amount)
```

inside:

```sql
GROUP BY customer_id
```

collapses rows.

But:

```sql
SUM(amount) OVER (
    PARTITION BY customer_id
)
```

preserves them.

That is the same aggregation operation embedded in a different relational behavior.

### Other aggregate windows

```sql
AVG(amount) OVER (
    PARTITION BY customer_id
)
```

```sql
MIN(order_date) OVER (
    PARTITION BY customer_id
)
```

```sql
MAX(order_date) OVER (
    PARTITION BY customer_id
)
```

```sql
COUNT(*) OVER (
    PARTITION BY customer_id
)
```

These can attach group context to each current row.

---

## 22. Running Totals

A running total is one of the most common window patterns.

Use:

```sql
SUM(amount) OVER (
    PARTITION BY customer_id
    ORDER BY order_date, order_id
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
)
```

### Meaning

```text
PARTITION BY
→ whose history?

ORDER BY
→ in what sequence?

ROWS frame
→ from the beginning of that history to this row

SUM
→ add the visible amounts
```

### Example

```text
customer | date | amount
---------+------+-------
A        | 1    | 100
A        | 2    | 200
A        | 3    |  50
```

Results:

```text
date 1 → 100
date 2 → 300
date 3 → 350
```

### Why deterministic ordering matters

If two rows share a timestamp:

```text
A | 2026-09-01 10:00 | order 10 | 100
A | 2026-09-01 10:00 | order 11 | 200
```

then:

```sql
ORDER BY order_ts
```

does not fully define which row comes first.

Add:

```sql
ORDER BY order_ts, order_id
```

when business semantics require a stable row order.

---

## 23. Share of Total

A window can calculate a denominator without collapsing rows.

Example:

```sql
SELECT
    customer_id,
    order_id,
    amount,
    amount / NULLIF(
        SUM(amount) OVER (
            PARTITION BY customer_id
        ),
        0
    ) AS share_of_customer_total
FROM orders;
```

Conceptually:

```text
current row amount
------------------
customer total
```

### Example

Customer A:

```text
order 1 → 100
order 2 → 300
```

Total:

```text
400
```

Shares:

```text
100 / 400 = 0.25
300 / 400 = 0.75
```

### Production considerations

Be explicit about:

- partition;
- denominator;
- numeric type;
- zero denominator;
- NULL values.

If integer operands are used in PostgreSQL, integer division can truncate.

Prefer an appropriate decimal expression:

```sql
amount::NUMERIC
/
NULLIF(
    SUM(amount) OVER (...),
    0
)
```

when exact decimal behavior is required.

---

## 24. Window Frames

A frame is the subset of rows within a partition that contributes to the current row's window calculation.

A highly useful mental model is:

```text
PARTITION
   ↓
population

ORDER BY
   ↓
sequence

FRAME
   ↓
visible rows for this current row

FUNCTION
   ↓
calculation
```

Or:

```text
PARTITION
→ who belongs?

ORDER
→ how are they arranged?

FRAME
→ which of them are visible for this calculation?

FUNCTION
→ what do I calculate?
```

### Frame is not always present

Functions such as `ROW_NUMBER` are ranking functions and do not use a frame in the same way aggregate/value functions do.

Frames become especially important with:

- `SUM`;
- `AVG`;
- `FIRST_VALUE`;
- `LAST_VALUE`;
- `NTH_VALUE`.

---

## 25. `ROWS`

`ROWS` defines a frame in terms of physical row positions in the ordered window.

Example:

```sql
ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
```

means:

```text
current row
+
previous 6 ordered rows
```

That gives at most seven rows.

### Example

```text
day | revenue
----+--------
1   | 100
2   | 200
3   | 300
4   | 400
5   | 500
6   | 600
7   | 700
8   | 800
```

For day 8:

```sql
ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
```

includes:

```text
days 2,3,4,5,6,7,8
```

### Critical warning

Seven rows is not automatically seven calendar days.

If the data is:

```text
Jan 1
Jan 2
Jan 8
```

then the third row has only three physical rows available.

This is why time semantics matter.

---

## 26. `RANGE`

`RANGE` frames are value/order based rather than simply counting physical rows.

Peer rows can therefore behave differently from `ROWS`.

A simplified example is:

```sql
SUM(amount) OVER (
    ORDER BY order_date
    RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
)
```

With duplicate `order_date` values, peer rows sharing the same ordering value can be included together under the default/current-peer semantics.

### Why this matters

Consider:

```text
date  | amount
------+-------
Jan 1 | 100
Jan 1 | 200
Jan 2 | 300
```

Under a value-based frame, both Jan 1 peer rows can be visible together when the current ordering value is Jan 1.

Under:

```sql
ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
```

the exact row position matters.

### Time-based RANGE

In engines that support the relevant syntax, an interval can express a time-oriented frame:

```sql
RANGE BETWEEN INTERVAL '6 days' PRECEDING
          AND CURRENT ROW
```

This means:

```text
all rows whose ordering timestamp
falls within the preceding six-day interval
through the current timestamp
```

It is fundamentally different from:

```sql
ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
```

---

## 27. `GROUPS`

`GROUPS` defines frame movement in terms of peer groups created by the window ordering.

Suppose:

```text
date | amount
-----+-------
Jan1 | 100
Jan1 | 200
Jan2 | 300
Jan3 | 400
```

The peer groups are:

```text
Group 1 → Jan1, Jan1
Group 2 → Jan2
Group 3 → Jan3
```

A `GROUPS` frame moves by peer groups rather than individual rows.

### Comparison

| Frame | Unit of movement |
|---|---|
| `ROWS` | individual physical rows |
| `RANGE` | ordering value / peers |
| `GROUPS` | peer groups |

### When this is useful

`GROUPS` is useful when business meaning is tied to ordered peer groups rather than individual row positions.

For example:

> “Include the current score group and the previous two distinct score groups.”

That is conceptually a `GROUPS` question.

---

## 28. `ROWS` vs `RANGE` vs `GROUPS`

Consider:

```text
date | amount
-----+-------
Jan1 | 100
Jan1 | 200
Jan2 | 300
Jan3 | 400
```

For the second Jan1 row:

### `ROWS`

```text
ROWS BETWEEN 1 PRECEDING AND CURRENT ROW
```

could include:

```text
Jan1 | 100
Jan1 | 200
```

because the frame is position-based.

### `RANGE`

```text
RANGE BETWEEN ...
```

uses the ordering value. Peer rows with the same order key can be included together.

### `GROUPS`

A frame expressed in group units treats:

```text
Jan1 rows
```

as one peer group.

### Frame reasoning template

For any frame question, write:

```text
Partition:
__________

Order:
__________

Current row:
__________

Peer group:
__________

Frame:
__________

Rows/groups visible:
__________

Rows/groups excluded:
__________

Function:
__________

Result:
__________
```

This is the skill you should practice by hand.

---

## 29. Moving Averages

A moving average combines aggregate windows with frames.

Example:

```sql
AVG(revenue) OVER (
    ORDER BY revenue_date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
) AS moving_avg_7_rows
```

This is a seven-row moving average.

### Important

It is not automatically a seven-day moving average.

If the data contains:

```text
Jan 1
Jan 2
Jan 8
```

the third row's seven-row frame does not magically create Jan 3–Jan 7.

### First rows

On the first row:

```text
available rows = 1
```

On the second row:

```text
available rows = 2
```

and so on until the maximum frame width is reached.

That is normal.

### Production design

If the business says:

> “Average revenue during the previous seven calendar days”

then the query must use time semantics, often through:

- a date spine;
- a time-based `RANGE` frame where supported;
- or another explicit calendar-domain construction.

---

## 30. Time-Based `RANGE` Frames

Where supported, a time-based range frame can express a calendar/time interval directly.

Example:

```sql
AVG(amount) OVER (
    ORDER BY event_ts
    RANGE BETWEEN INTERVAL '6 days' PRECEDING
              AND CURRENT ROW
)
```

Conceptually, for an event at:

```text
2026-09-10 12:00
```

the frame can cover:

```text
2026-09-04 12:00
through
2026-09-10 12:00
```

according to the engine's exact frame semantics.

### Why it differs from `ROWS`

```text
ROWS
→ previous physical rows

RANGE
→ rows whose ordering values lie in the specified range
```

### Missing timestamps

Suppose events exist only on:

```text
Sep 1
Sep 7
Sep 10
```

A time-based range still reasons about elapsed time.

A seven-row frame cannot.

### Dialect note

**PostgreSQL:** supports value-based window frames and interval-based range syntax for compatible temporal ordering.

**DuckDB:** supports rich window framing, but exact syntax and edge behavior should be checked against the installed version.

Do not assume every analytical engine implements every frame form identically.

---

## 31. The Default Frame

The default frame is one of the most common sources of confusion.

Do not memorize an oversimplified statement such as:

> “The default frame is always rows from the beginning to the current row.”

That is not sufficiently precise.

The relevant behavior depends on the presence of window ordering and the frame semantics of the engine/function. In PostgreSQL-oriented work, an ordered window commonly uses a peer-aware default frame that extends through the current row's peer group.

### Why peers matter

If:

```sql
ORDER BY order_date
```

and two rows have the same `order_date`, those rows are peers under that ordering.

The current frame can therefore include the peer group rather than only one physical row.

### Safe engineering rule

When the metric's boundary matters:

> **Write the frame explicitly.**

For example:

```sql
ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
```

or:

```sql
ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
```

### Why explicit frames help

They make business intent visible in code review.

A reviewer can immediately see:

```text
running from the beginning → current row
```

or:

```text
entire partition
```

instead of inferring intent from defaults.

---

## 32. Why `LAST_VALUE` Often Looks Wrong

Consider:

```sql
SELECT
    order_date,
    amount,
    LAST_VALUE(amount) OVER (
        ORDER BY order_date
    ) AS last_amount
FROM orders;
```

A learner may expect:

```text
last amount in the whole table
```

on every row.

But `LAST_VALUE` returns the value from the last row in the current frame.

If the frame ends at the current row or current peer group, the “last row” can be the current row.

### Explicit whole-partition example

```sql
SELECT
    order_date,
    amount,
    LAST_VALUE(amount) OVER (
        ORDER BY order_date, order_id
        ROWS BETWEEN UNBOUNDED PRECEDING
                 AND UNBOUNDED FOLLOWING
    ) AS final_amount
FROM orders;
```

Now the frame is the whole ordered partition.

### Before/after reasoning

Without explicit frame:

```text
current frame
    ↓
current row / peer group
    ↓
LAST_VALUE
    ↓
often current/peer value
```

With explicit full frame:

```text
whole partition
    ↓
last row in partition
    ↓
LAST_VALUE
    ↓
final value
```

### Important distinction

The function did not “behave incorrectly.”

The frame was different from the learner's mental model.

---

## 33. Filtering Window Results

A common mistake is:

```sql
SELECT
    *,
    ROW_NUMBER() OVER (
        PARTITION BY customer_id
        ORDER BY amount DESC
    ) AS rn
FROM orders
WHERE rn <= 3;
```

This is not the standard logical shape you want because the window result is not available at the earlier filtering stage.

### Correct idea

Create the window result first:

```text
rows
↓
window calculation
↓
ranked relation
↓
filter
```

---

## 34. CTE Pattern for Window Filtering

The standard SQL pattern is a CTE or derived table.

```sql
WITH ranked AS (
    SELECT
        order_id,
        customer_id,
        amount,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY amount DESC, order_id DESC
        ) AS rn
    FROM orders
)
SELECT
    order_id,
    customer_id,
    amount
FROM ranked
WHERE rn <= 3;
```

### Why this works

The CTE creates a relation containing:

```text
order_id
customer_id
amount
rn
```

Now the outer query can filter `rn`.

### Grain-first explanation

Before the CTE:

```text
one row per order
```

Inside `ranked`:

```text
one row per order
+
ranking context
```

After:

```sql
WHERE rn <= 3
```

the output is:

```text
up to three rows per customer
```

depending on the ranking strategy.

---

## 35. `QUALIFY`

`QUALIFY` lets an engine filter on a window result without forcing a separate visible CTE/subquery boundary.

Example:

```sql
SELECT
    *
FROM orders
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY amount DESC, order_id DESC
) <= 3;
```

### Dialect-specific

`QUALIFY` is **not universal standard SQL syntax**.

It is supported by engines including DuckDB and several analytical platforms.

For portability:

```text
standard SQL
→ CTE/subquery

supported dialect
→ QUALIFY can be convenient
```

### DuckDB example

```sql
SELECT
    customer_id,
    order_id,
    amount
FROM orders
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY amount DESC, order_id DESC
) <= 3;
```

When writing portable library SQL, prefer the CTE/subquery pattern unless the target dialect is intentionally fixed.

---

## 36. Top-N Per Group

“Top N” is not one universal requirement.

Ask:

```text
Do I need exactly N rows?
or
Do I need every row tied at the Nth position?
```

### Exactly three rows

Use `ROW_NUMBER`:

```sql
WITH ranked AS (
    SELECT
        country,
        product_id,
        revenue,
        ROW_NUMBER() OVER (
            PARTITION BY country
            ORDER BY revenue DESC, product_id
        ) AS rn
    FROM product_revenue
)
SELECT *
FROM ranked
WHERE rn <= 3;
```

### Include every tied row at third position

Use `RANK`:

```sql
WITH ranked AS (
    SELECT
        country,
        product_id,
        revenue,
        RANK() OVER (
            PARTITION BY country
            ORDER BY revenue DESC
        ) AS rnk
    FROM product_revenue
)
SELECT *
FROM ranked
WHERE rnk <= 3;
```

### Why the tie-breaker differs

For `ROW_NUMBER`, the tie-breaker is part of deterministic row selection.

For `RANK`, adding a unique tie-breaker can destroy the peer relationship.

Therefore:

```text
ROW_NUMBER
→ include tie-breaker for deterministic row identity

RANK
→ do not add a unique tie-breaker if ties must share rank
```

---

## 37. Latest Record Per Key

This is one of the most valuable production patterns.

Suppose:

```text
customer_id | updated_at | email
------------+------------+----------------
10          | Sep 1      | old@example.com
10          | Sep 5      | new@example.com
11          | Sep 2      | b@example.com
```

Use:

```sql
WITH ranked AS (
    SELECT
        c.*,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY updated_at DESC, record_id DESC
        ) AS rn
    FROM customer_events AS c
)
SELECT *
FROM ranked
WHERE rn = 1;
```

### Why not just `MAX(updated_at)`?

Because:

```sql
MAX(updated_at)
```

returns the maximum timestamp, not the entire row associated with that timestamp.

Joining back on timestamp can still produce multiple rows if the timestamp ties.

`ROW_NUMBER` expresses:

> “Select exactly one deterministic row per business key according to this survivor order.”

This pattern is heavily reused in:

- incremental ingestion;
- source cleanup;
- CDC processing;
- event pipelines;
- latest-state extraction.

---

## 38. Gaps and Islands

Gaps-and-islands is a sequence problem.

You often have:

```text
ordered events
```

and need to identify:

```text
consecutive runs
```

Examples:

- login streaks;
- active days;
- uptime periods;
- consecutive purchase days;
- service availability;
- repeated status periods.

### Example

```text
user | day
-----+-------
A    | Jan 1
A    | Jan 2
A    | Jan 3
A    | Jan 6
A    | Jan 7
```

There are two islands:

```text
Island 1:
Jan 1
Jan 2
Jan 3

Island 2:
Jan 6
Jan 7
```

### The key insight

Create a sequence number.

Then compare:

```text
actual date
vs
expected date implied by row position
```

For consecutive dates, the difference stays constant.

---

## 39. Gaps-and-Islands with `ROW_NUMBER`

A PostgreSQL-friendly pattern is:

```sql
WITH ordered AS (
    SELECT
        user_id,
        activity_date,
        ROW_NUMBER() OVER (
            PARTITION BY user_id
            ORDER BY activity_date
        ) AS rn
    FROM active_days
),
islands AS (
    SELECT
        user_id,
        activity_date,
        activity_date
            - rn::int AS island_key
    FROM ordered
)
SELECT
    user_id,
    island_key,
    MIN(activity_date) AS start_date,
    MAX(activity_date) AS end_date,
    COUNT(*) AS streak_days
FROM islands
GROUP BY user_id, island_key;
```

### Why it works

For:

```text
Jan 1
Jan 2
Jan 3
```

row numbers are:

```text
1
2
3
```

Now subtract:

```text
Jan 1 - 1 day
Jan 2 - 2 days
Jan 3 - 3 days
```

The derived value is constant.

That constant becomes the island key.

At the gap:

```text
Jan 6
```

the row number has advanced, but the date jumped forward, so the derived key changes.

### Do not memorize the formula only

Understand the mechanism:

```text
ordered rows
    ↓
row number
    ↓
expected position
    ↓
compare actual date with expected position
    ↓
constant key inside consecutive runs
    ↓
group the key
```

---

## 40. Consecutive Streaks

Once islands exist, streak metrics are ordinary aggregation.

```text
events
→ daily activity
→ ordered rows
→ island key
→ islands
→ streak length
→ longest streak
```

Example:

```sql
WITH active_days AS (
    SELECT DISTINCT
        user_id,
        activity_date
    FROM activity
),
numbered AS (
    SELECT
        user_id,
        activity_date,
        ROW_NUMBER() OVER (
            PARTITION BY user_id
            ORDER BY activity_date
        ) AS rn
    FROM active_days
),
islands AS (
    SELECT
        user_id,
        activity_date,
        activity_date - rn::int AS island_key
    FROM numbered
),
streaks AS (
    SELECT
        user_id,
        island_key,
        MIN(activity_date) AS start_date,
        MAX(activity_date) AS end_date,
        COUNT(*) AS streak_days
    FROM islands
    GROUP BY user_id, island_key
)
SELECT
    user_id,
    start_date,
    end_date,
    streak_days
FROM streaks;
```

To return a single maximum streak per user, apply another ranking step.

### Edge cases

Test:

- one-day streak;
- all days consecutive;
- no gap at all;
- duplicate events on one day;
- two equally long longest streaks;
- timezone-driven day boundaries.

---

## 41. Sessionisation

Sessionisation turns an event stream into sessions.

Definition:

> A session is a sequence of events separated by no more than a chosen inactivity threshold.

Suppose the threshold is 30 minutes:

```text
10:00
10:10
10:20
11:05
11:15
```

Then:

```text
Session 1
10:00
10:10
10:20

Session 2
11:05
11:15
```

The key sequence is:

```text
events
  ↓
LAG previous timestamp
  ↓
time gap
  ↓
new-session flag
  ↓
running SUM
  ↓
session_id
  ↓
aggregate sessions
```

This is a major example of windows turning row-to-row comparisons into state.

---

## 42. Sessionisation with `LAG`

### Step 1 — define the event grain

```text
one row per event
```

### Step 2 — define partition

```text
user_id
```

### Step 3 — define ordering

```text
event_time, event_id
```

### Step 4 — find previous event

```sql
LAG(event_time) OVER (
    PARTITION BY user_id
    ORDER BY event_time, event_id
)
```

### Step 5 — calculate gap

```sql
event_time - previous_event_time
```

### Step 6 — define new-session flag

```text
first event → 1
gap > 30 minutes → 1
otherwise → 0
```

### Step 7 — running sum

```sql
SUM(new_session) OVER (
    PARTITION BY user_id
    ORDER BY event_time, event_id
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
)
```

This gives a session sequence.

### Step 8 — aggregate

```sql
GROUP BY user_id, session_id
```

Now the grain becomes:

```text
one row per session
```

---

## 43. Complete Sessionisation Example

```sql
WITH ordered AS (
    SELECT
        event_id,
        user_id,
        event_time,
        LAG(event_time) OVER (
            PARTITION BY user_id
            ORDER BY event_time, event_id
        ) AS previous_event_time
    FROM click_events
),
flagged AS (
    SELECT
        *,
        CASE
            WHEN previous_event_time IS NULL THEN 1
            WHEN event_time - previous_event_time > INTERVAL '30 minutes' THEN 1
            ELSE 0
        END AS new_session
    FROM ordered
),
sessionized AS (
    SELECT
        *,
        SUM(new_session) OVER (
            PARTITION BY user_id
            ORDER BY event_time, event_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS session_id
    FROM flagged
)
SELECT
    user_id,
    session_id,
    MIN(event_time) AS session_start,
    MAX(event_time) AS session_end,
    COUNT(*) AS event_count,
    MAX(event_time) - MIN(event_time) AS session_duration
FROM sessionized
GROUP BY user_id, session_id
ORDER BY user_id, session_id;
```

### Boundary rule

The example says:

```text
gap > 30 minutes
→ new session
```

Therefore:

```text
gap = exactly 30 minutes
→ same session
```

If the business rule instead says:

```text
gap >= 30 minutes
```

the SQL must change.

Do not let punctuation in the requirement become an accidental business rule.

---

## 44. Session Output Metrics

Once session IDs exist, useful session metrics include:

```text
session_start
session_end
event_count
session_duration
```

The grain changes:

```text
event rows
   ↓
sessionized event rows
   ↓
one row per session
```

This is an important grain transformation.

### Session length

```sql
MAX(event_time) - MIN(event_time)
```

### Event count

```sql
COUNT(*)
```

### Session sequence

The running sum creates a session number within each user.

---

## 45. Period-over-Period Analysis

Period-over-period metrics compare one period with an earlier period.

A common pattern is:

```sql
LAG(monthly_revenue) OVER (
    ORDER BY month
)
```

Then:

```text
absolute change
=
current - previous
```

and:

```text
percentage change
=
(current - previous) / previous
```

Use:

```sql
NULLIF(previous_value, 0)
```

to avoid division by zero.

### Core pattern

```sql
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', order_ts) AS month,
        SUM(amount) AS revenue
    FROM orders
    GROUP BY 1
),
with_previous AS (
    SELECT
        month,
        revenue,
        LAG(revenue) OVER (
            ORDER BY month
        ) AS previous_revenue
    FROM monthly
)
SELECT
    month,
    revenue,
    previous_revenue,
    revenue - previous_revenue AS change,
    (revenue - previous_revenue)
        / NULLIF(previous_revenue, 0) AS pct_change
FROM with_previous
ORDER BY month;
```

### Important issue

Missing periods matter.

If you have:

```text
Jan
Feb
Apr
```

then:

```sql
LAG(revenue)
```

for April returns February revenue.

That may be wrong if the business means:

> compare each month with the immediately previous calendar month.

This is why missing-period handling and date-spine techniques from Topic 04 matter.

---

## 46. Month-over-Month Change

Suppose:

```text
month | revenue
------+--------
Jan   | 100
Feb   | 120
Mar   |  90
```

The expected output:

```text
month | revenue | previous | change | pct_change
------+---------+----------+--------+-----------
Jan   | 100     | NULL     | NULL   | NULL
Feb   | 120     | 100      | 20     | 0.20
Mar   | 90      | 120      | -30    | -0.25
```

The first month has no previous month in the available sequence, so `LAG` naturally returns NULL.

### Deterministic month ordering

Use a real month value:

```sql
ORDER BY month
```

not:

```sql
ORDER BY month_name
```

because lexical month names do not represent chronological order.

---

## 47. Year-over-Year Change

For a complete monthly series, a 12-row offset can compare the same month in the prior year:

```sql
LAG(revenue, 12) OVER (
    ORDER BY month
)
```

This assumes:

```text
one row per month
```

and:

```text
no missing months
```

### Why missing months break the assumption

If one month is absent:

```text
Jan 2025
Feb 2025
Apr 2025
...
Jan 2026
```

then:

```sql
LAG(revenue, 12)
```

means:

```text
12 rows earlier
```

not:

```text
12 calendar months earlier
```

A date spine can make the month sequence explicit before applying the window.

---

## 48. Cohort Retention

Cohort retention groups users by signup period and asks whether they remain active later.

The basic transformation is:

```text
user
 ↓
signup month
 ↓
activity month
 ↓
months since signup
 ↓
active users
 ↓
cohort denominator
 ↓
retention %
```

### Typical grain

At one intermediate stage:

```text
one row per user per activity month
```

At another:

```text
one row per signup cohort per activity month
```

### Example structure

```sql
WITH user_activity AS (
    SELECT DISTINCT
        user_id,
        DATE_TRUNC('month', activity_time) AS activity_month
    FROM user_events
),
user_cohorts AS (
    SELECT
        user_id,
        DATE_TRUNC('month', signup_time) AS signup_month
    FROM users
),
cohort_activity AS (
    SELECT
        c.signup_month,
        a.activity_month,
        COUNT(DISTINCT a.user_id) AS active_users
    FROM user_cohorts AS c
    JOIN user_activity AS a
      ON a.user_id = c.user_id
    GROUP BY c.signup_month, a.activity_month
)
SELECT *
FROM cohort_activity;
```

A final retention rate requires:

```text
active users
/
users in original cohort
```

The denominator must represent the cohort population, not the number active in the current month.

### Why window functions can help

After defining cohort totals, a window can attach the cohort denominator to each row:

```sql
COUNT(*) OVER (
    PARTITION BY signup_month
)
```

or an appropriate aggregated relation can be joined to the cohort grid.

The exact implementation depends on the data shape.

---

## 49. Deterministic Ordering

Determinism matters whenever the window's order affects business meaning.

Potentially unstable:

```sql
ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY created_at DESC
)
```

if `created_at` ties.

Safer:

```sql
ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY created_at DESC, record_id DESC
)
```

### Tie-breakers matter for

- latest record;
- deduplication;
- top-N;
- running totals;
- `LAG`;
- `LEAD`;
- sessionization;
- streak calculations;
- reproducible tests.

### Production principle

> **If two rows are peers under the business ordering and the result depends on which one comes first, you need a deterministic tie-breaker.**

The tie-breaker should itself have a clear uniqueness and business meaning.

Avoid random ordering for production transformations.

---

## 50. Named Windows

When several window functions share the same specification, a named window can improve readability.

Example:

```sql
SELECT
    customer_id,
    order_date,
    amount,
    SUM(amount) OVER w AS running_total,
    AVG(amount) OVER w AS running_average,
    LAG(amount) OVER w AS previous_amount
FROM orders
WINDOW w AS (
    PARTITION BY customer_id
    ORDER BY order_date, order_id
);
```

### Benefits

- less repeated SQL;
- clearer intent;
- easier maintenance;
- lower risk of accidental specification drift.

### Important distinction

A named window is a query-language convenience for defining and reusing a specification.

It does not automatically mean:

```text
one physical sort
```

That is a separate optimizer question.

---

## 51. Multiple Window Specifications and Cost

Suppose a query contains:

```sql
SUM(amount) OVER (
    PARTITION BY customer_id
    ORDER BY order_date
)

AVG(amount) OVER (
    PARTITION BY customer_id
    ORDER BY order_date
)

LAG(amount) OVER (
    PARTITION BY customer_id
    ORDER BY order_date
)
```

These specifications are compatible and may allow the engine to share some ordering work.

But if you add:

```sql
ROW_NUMBER() OVER (
    PARTITION BY country
    ORDER BY amount DESC
)
```

the partitioning and ordering differ.

That may require additional processing or sorting.

### Do not make the false claim

> “Every window function requires a separate sort.”

That is not generally true.

The more accurate model is:

```text
compatible specifications
→ potential reuse

different partition/order requirements
→ potentially additional work
```

The optimizer and engine decide the actual physical strategy.

### Production implication

A query with 20 logically different window definitions may be substantially more expensive than a query with 20 functions sharing one window specification.

---

## 52. Window Function Performance Intuition

Do not reduce performance to:

> “Window functions are slow.”

That is too simplistic.

A more accurate model is:

```text
window operation
    ↓
partitioning
    ↓
ordering
    ↓
frame evaluation
    ↓
memory / CPU / I/O considerations
```

Potential cost drivers include:

- large partitions;
- expensive ordering;
- wide rows carried through the operation;
- many distinct window specifications;
- unnecessary rows entering the window;
- unnecessary columns;
- large unbounded frames;
- poor upstream filtering;
- missing pre-aggregation where an earlier reduction is possible.

### Large single partition

This:

```sql
SUM(amount) OVER (
    ORDER BY event_time
)
```

creates one global partition.

If the table contains billions of rows, the operation is fundamentally global.

A partitioned window:

```sql
SUM(amount) OVER (
    PARTITION BY customer_id
    ORDER BY event_time
)
```

may create many smaller logical populations, although whether this is cheaper depends on cardinality and the actual workload.

### Reduce before windowing

If raw data contains:

```text
millions of events
```

but the metric only needs:

```text
one row per customer per day
```

pre-aggregate first when semantically valid:

```text
raw events
↓
daily customer aggregate
↓
window over daily rows
```

This can reduce the volume entering the expensive ordered operation.

Do not optimize this way unless the transformation preserves the required metric semantics.

---

## 53. Production Pattern 1 — Top 3 Products Per Country

```text
Input grain:
one row per product/country metric

Window partition:
country

Window order:
revenue DESC

Frame:
not needed for ranking

Output grain:
one row per selected product/country

Tie-breaking:
ROW_NUMBER needs a unique tie-breaker if exactly 3 rows are required

NULL behavior:
define how NULL revenue should rank
```

Example:

```sql
WITH ranked AS (
    SELECT
        country,
        product_id,
        revenue,
        ROW_NUMBER() OVER (
            PARTITION BY country
            ORDER BY revenue DESC NULLS LAST, product_id
        ) AS rn
    FROM product_revenue
)
SELECT
    country,
    product_id,
    revenue
FROM ranked
WHERE rn <= 3;
```

Validation:

```sql
SELECT
    country
FROM top_products
GROUP BY country
HAVING COUNT(*) > 3;
```

That assertion is valid only when the requirement is exactly at most three rows per country.

---

## 54. Production Pattern 2 — Latest Record Per Customer

```text
Input grain:
one row per customer event/version

Partition:
customer_id

Order:
updated_at DESC, record_id DESC

Output grain:
one row per customer

Tie-breaker:
record_id

NULL behavior:
updated_at NULL policy must be explicit
```

Example:

```sql
WITH ranked AS (
    SELECT
        customer_id,
        email,
        status,
        updated_at,
        record_id,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY updated_at DESC NULLS LAST,
                     record_id DESC
        ) AS rn
    FROM customer_events
)
SELECT *
FROM ranked
WHERE rn = 1;
```

### Why not `MAX(updated_at)`?

Because the max timestamp does not uniquely identify the full row.

### Validation

```sql
SELECT customer_id
FROM latest_customers
GROUP BY customer_id
HAVING COUNT(*) <> 1;
```

This should return zero rows if every customer must have exactly one current row.

---

## 55. Production Pattern 3 — Running Daily Revenue

First reduce to daily grain:

```text
one row per day
```

Then:

```sql
SELECT
    revenue_date,
    revenue,
    SUM(revenue) OVER (
        ORDER BY revenue_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_revenue
FROM daily_revenue
ORDER BY revenue_date;
```

### Grain

```text
Input:
one row per day

Output:
one row per day
+
running metric
```

### Determinism

If the data has exactly one row per day, the order is naturally unique.

If not, add a tie-breaker or fix the upstream grain.

---

## 56. Production Pattern 4 — Seven-Row Moving Average

```sql
SELECT
    revenue_date,
    revenue,
    AVG(revenue) OVER (
        ORDER BY revenue_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7_rows
FROM daily_revenue
ORDER BY revenue_date;
```

### Required interpretation

```text
7 rows
≠
7 calendar days
```

If a date can be absent, create a complete date domain or use a time-based frame where it matches the engine and metric semantics.

---

## 57. Production Pattern 5 — Month-over-Month Revenue

```sql
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', order_ts) AS month,
        SUM(amount) AS revenue
    FROM orders
    GROUP BY 1
),
compared AS (
    SELECT
        month,
        revenue,
        LAG(revenue) OVER (
            ORDER BY month
        ) AS previous_revenue
    FROM monthly
)
SELECT
    month,
    revenue,
    previous_revenue,
    revenue - previous_revenue AS change,
    (revenue - previous_revenue)
        / NULLIF(previous_revenue, 0) AS pct_change
FROM compared
ORDER BY month;
```

### Edge cases

- first month;
- previous month with zero revenue;
- missing month;
- NULL revenue;
- timezone boundaries before monthly truncation.

---

## 58. Production Pattern 6 — Longest Activity Streak

```text
daily activity
→ ordered dates
→ row number
→ island key
→ island aggregation
→ longest streak
```

A practical PostgreSQL pattern:

```sql
WITH active_days AS (
    SELECT DISTINCT
        user_id,
        activity_date
    FROM daily_activity
),
numbered AS (
    SELECT
        user_id,
        activity_date,
        ROW_NUMBER() OVER (
            PARTITION BY user_id
            ORDER BY activity_date
        ) AS rn
    FROM active_days
),
grouped AS (
    SELECT
        user_id,
        activity_date,
        activity_date - rn::int AS island_key
    FROM numbered
),
streaks AS (
    SELECT
        user_id,
        island_key,
        MIN(activity_date) AS start_date,
        MAX(activity_date) AS end_date,
        COUNT(*) AS streak_days
    FROM grouped
    GROUP BY user_id, island_key
),
ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY user_id
            ORDER BY streak_days DESC, start_date, end_date
        ) AS rn
    FROM streaks
)
SELECT
    user_id,
    start_date,
    end_date,
    streak_days
FROM ranked
WHERE rn = 1;
```

The final `ROW_NUMBER` uses deterministic tie-breaking if multiple streaks have the same length.

---

## 59. Production Pattern 7 — 30-Minute Event Sessionisation

The standard pipeline is:

```text
event rows
→ previous event
→ inactivity gap
→ new-session flag
→ cumulative session number
→ session aggregate
```

Use:

```sql
LAG(event_time)
```

then:

```sql
CASE
    WHEN previous_event_time IS NULL THEN 1
    WHEN event_time - previous_event_time > INTERVAL '30 minutes' THEN 1
    ELSE 0
END
```

then:

```sql
SUM(new_session) OVER (
    PARTITION BY user_id
    ORDER BY event_time, event_id
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
)
```

and finally:

```sql
GROUP BY user_id, session_id
```

### Output grain

```text
one row per session
```

### Validation

```sql
SELECT *
FROM sessions
WHERE session_end < session_start;
```

should return zero rows.

---

## 60. Production Pattern 8 — Cohort Retention

A practical workflow:

```text
signup timestamp
→ signup month

activity events
→ activity month

join user to cohort
→ calculate month offset

aggregate active users
→ calculate cohort denominator

active users / cohort size
→ retention
```

At every step, state:

```text
Input grain
Window partition
Window order
Frame
Output grain
Tie-breaking
NULL behavior
Edge cases
Validation
```

### Example month offset

In PostgreSQL-oriented SQL, the exact date arithmetic can be implemented through month-based calculations after normalizing to month boundaries. The important window concept is what comes after:

```text
cohort month
→ ordered activity month
→ prior/current cohort metrics
```

Do not hide an incorrect denominator behind correct-looking window syntax.

---

## 61. Debugging Window Queries

When a window result is wrong, do not stare at the function first.

Use this sequence:

### Step 1 — Inspect the input rows

```text
What rows actually reached the window?
```

### Step 2 — State the grain

```text
One row represents __________
```

### Step 3 — Identify the partition

```text
PARTITION BY __________
```

### Step 4 — Identify the order

```text
ORDER BY __________
```

### Step 5 — Check determinism

Ask:

```text
Can two rows tie on the ordering columns?
```

### Step 6 — Identify the frame

```text
ROWS / RANGE / GROUPS
```

or:

```text
implicit/default frame
```

### Step 7 — Pick one current row

Write down exactly which rows are visible.

### Step 8 — Check peers

If the order key ties, identify the peer group.

### Step 9 — Verify first/last behavior

For:

- `LAG`;
- `LEAD`;
- `FIRST_VALUE`;
- `LAST_VALUE`;
- `NTH_VALUE`.

### Step 10 — Hand-compute a tiny example

This is often the fastest way to find a semantic mistake.

---

## 62. Debugging Challenge 1 — `ROW_NUMBER` Changes Between Runs

### Symptom

The “latest customer row” occasionally changes.

### Broken query

```sql
ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY updated_at DESC
)
```

### Diagnosis

Multiple rows share `updated_at`.

### Fix

```sql
ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY updated_at DESC, record_id DESC
)
```

### Production lesson

A ranking function does not invent deterministic business meaning.

You must define it.

---

## 63. Debugging Challenge 2 — Wrong Top-N Result

### Symptom

The business asks for every product tied at third place, but the query returns exactly three rows.

### Broken query

```sql
ROW_NUMBER() OVER (
    PARTITION BY country
    ORDER BY revenue DESC
)
```

### Diagnosis

`ROW_NUMBER` selects exactly one unique position per row.

### Fix

Use:

```sql
RANK() OVER (
    PARTITION BY country
    ORDER BY revenue DESC
)
```

then:

```sql
WHERE rnk <= 3
```

### Production lesson

First define:

```text
N rows?
or
N rank positions?
```

---

## 64. Debugging Challenge 3 — Running Total Is Unexpected

### Symptom

Two same-timestamp orders receive surprising cumulative totals.

### Broken query

```sql
SUM(amount) OVER (
    PARTITION BY customer_id
    ORDER BY order_time
)
```

### Diagnosis

The ordering has peers.

The default frame may include peer rows together, which is not the same as a physical-row cumulative sequence.

### Fix

If the business metric is row-by-row:

```sql
SUM(amount) OVER (
    PARTITION BY customer_id
    ORDER BY order_time, order_id
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
)
```

### Production lesson

Timestamp order alone may not define a total order.

---

## 65. Debugging Challenge 4 — Seven Rows vs Seven Days

### Symptom

A “7-day moving average” changes unexpectedly when dates are missing.

### Broken query

```sql
AVG(revenue) OVER (
    ORDER BY revenue_date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
)
```

### Diagnosis

This is a seven-row window.

### Fix

Depending on the requirement:

- build a complete daily spine and use seven physical rows;
- or use an appropriate time-based `RANGE` frame where supported.

### Production lesson

Always translate the business phrase:

```text
seven rows
seven calendar days
rolling week
```

into explicit SQL semantics.

---

## 66. Debugging Challenge 5 — `LAST_VALUE` Returns the Current Row

### Symptom

`LAST_VALUE(amount)` appears to return the current amount.

### Broken query

```sql
LAST_VALUE(amount) OVER (
    PARTITION BY customer_id
    ORDER BY order_date
)
```

### Diagnosis

`LAST_VALUE` returns the last value in the current frame.

The default ordered frame does not necessarily mean “the entire partition.”

### Fix

```sql
LAST_VALUE(amount) OVER (
    PARTITION BY customer_id
    ORDER BY order_date, order_id
    ROWS BETWEEN UNBOUNDED PRECEDING
             AND UNBOUNDED FOLLOWING
)
```

### Production lesson

When function semantics are frame-sensitive, inspect the frame before blaming the function.

---

## 67. Debugging Challenge 6 — Window Result in `WHERE`

### Symptom

A query tries to filter on a window alias directly.

### Broken query

```sql
SELECT
    *,
    ROW_NUMBER() OVER (
        PARTITION BY customer_id
        ORDER BY amount DESC
    ) AS rn
FROM orders
WHERE rn <= 3;
```

### Fix

Use a CTE:

```sql
WITH ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY amount DESC
        ) AS rn
    FROM orders
)
SELECT *
FROM ranked
WHERE rn <= 3;
```

Or use `QUALIFY` in a supporting engine:

```sql
SELECT *
FROM orders
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY amount DESC
) <= 3;
```

### Production lesson

Know the logical query stage at which the window result becomes available.

---

## 68. Debugging Challenge 7 — `QUALIFY` on the Wrong Engine

### Symptom

A query works in DuckDB but fails in another SQL engine.

### Diagnosis

`QUALIFY` is dialect-specific.

### Fix

Rewrite using a CTE/subquery:

```sql
WITH ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY amount DESC
        ) AS rn
    FROM orders
)
SELECT *
FROM ranked
WHERE rn <= 3;
```

### Production lesson

SQL portability is not the same as SQL correctness.

Label engine-specific syntax clearly.

---

## 69. Debugging Challenge 8 — `LAG` Compares the Wrong Event

### Symptom

Session gaps or previous-order calculations are inconsistent.

### Common cause

Wrong partition or ordering.

For example:

```sql
LAG(event_time) OVER (
    ORDER BY event_time
)
```

when the intended sequence is per user.

### Fix

```sql
LAG(event_time) OVER (
    PARTITION BY user_id
    ORDER BY event_time, event_id
)
```

### Production lesson

`LAG` answers a relative-position question inside the specified partition and ordering. Get those two dimensions wrong and the function is faithfully returning the wrong relationship.

---

## 70. Debugging Challenge 9 — Session Boundaries Are Wrong

### Symptom

Two events exactly 30 minutes apart are split into different sessions.

### Diagnosis

The implementation used:

```sql
>= INTERVAL '30 minutes'
```

but the business rule was:

```text
new session only when gap > 30 minutes
```

### Fix

```sql
> INTERVAL '30 minutes'
```

### Production lesson

Threshold operators are business logic.

---

## 71. Debugging Challenge 10 — Broken Gaps-and-Islands

### Symptom

A streak is split incorrectly.

### Common causes

- duplicate dates were not removed;
- order is not deterministic;
- dates are timestamps with inconsistent timezones;
- row number partition is missing;
- the derived island key is computed at the wrong grain.

### Fix sequence

```text
1. Normalize date/time semantics.
2. Deduplicate to one row per user/day if required.
3. Order by activity_date.
4. Number within user.
5. Create island key.
6. Inspect the key manually on five rows.
```

### Production lesson

The formula is secondary.

The grain and sequence are primary.

---

## 72. Assertion Queries

Assertion queries are queries that should return zero rows when the data is correct.

They turn assumptions into testable contracts.

### Exactly one latest row per customer

```sql
SELECT
    customer_id
FROM latest_customers
GROUP BY customer_id
HAVING COUNT(*) <> 1;
```

Expected:

```text
zero rows
```

### At most three top products per country

```sql
SELECT
    country
FROM top_products
GROUP BY country
HAVING COUNT(*) > 3;
```

### Session duration invariant

```sql
SELECT *
FROM sessions
WHERE session_end < session_start;
```

### Retention bounds

```sql
SELECT *
FROM retention
WHERE retention_rate < 0
   OR retention_rate > 1;
```

### Duplicate ranking keys

If the ranking requires a unique tie-breaker:

```sql
SELECT
    customer_id,
    updated_at,
    record_id,
    COUNT(*) OVER (
        PARTITION BY customer_id, updated_at, record_id
    ) AS duplicate_count
FROM customer_events;
```

For a true assertion, isolate the violated condition and return only invalid rows.

### Assertions must match business invariants

Do not add meaningless checks just to have tests.

A useful assertion answers:

> “What impossible or invalid state should this transformation never produce?”

---

## 73. Common Window-Function Mistakes

### Mistake 1 — Treating a window like `GROUP BY`

Window functions preserve row visibility.

### Mistake 2 — Forgetting `PARTITION BY`

A global calculation is accidentally performed when the business requires per-customer or per-country logic.

### Mistake 3 — Adding an unnecessary partition

An extra partition can reset a running calculation when it should be global.

### Mistake 4 — Confusing window `ORDER BY` with final `ORDER BY`

The calculation can be correct while the displayed order differs.

### Mistake 5 — Missing tie-breakers

A latest record can change between runs.

### Mistake 6 — Using `ROW_NUMBER` when ties must survive

You silently discard tied records.

### Mistake 7 — Using `RANK` when exactly N rows are required

You may return more than N rows.

### Mistake 8 — Misunderstanding `DENSE_RANK`

You assume rank gaps should exist when they should not.

### Mistake 9 — Treating `NTILE` as a percentile-value function

Buckets are not the same as percentile cut points.

### Mistake 10 — Misreading `PERCENT_RANK`

It is a relative rank concept, not an equal-width numeric bucket.

### Mistake 11 — Misreading `CUME_DIST`

It measures cumulative distribution at or below the current ordering value.

### Mistake 12 — Wrong `LAG` / `LEAD` offset

For example, using 2 when the business means the immediately previous row.

### Mistake 13 — Ignoring first/last rows

`LAG` on the first row and `LEAD` on the last row naturally have no referenced row.

### Mistake 14 — Treating NULL defaults as universally safe

A default can change business meaning.

### Mistake 15 — Choosing the wrong frame

This is especially dangerous for moving averages and running totals.

### Mistake 16 — Confusing `ROWS` and `RANGE`

Seven rows is not always seven days.

### Mistake 17 — Ignoring peer rows

Ordered ties can change frame membership.

### Mistake 18 — Misunderstanding `GROUPS`

Peer groups are not individual rows.

### Mistake 19 — Ignoring the default frame

Defaults can produce surprising value-function behavior.

### Mistake 20 — Using `LAST_VALUE` without considering the frame

The result may be the current/peer value rather than the final partition value.

### Mistake 21 — Filtering the window result in `WHERE`

Use a CTE/subquery or supported `QUALIFY`.

### Mistake 22 — Using `QUALIFY` where unsupported

Remember dialect boundaries.

### Mistake 23 — Forgetting missing periods

MoM and YoY logic can silently compare the wrong periods.

### Mistake 24 — Incorrect session threshold

`>` and `>=` are different business rules.

### Mistake 25 — Assuming every window requires its own sort

Compatible specifications may share work.

### Mistake 26 — Assuming every window is cheap

Large partitions and heavy ordering can be expensive.

---

## 74. Hands-On Exercise 1 — Ranking Functions

### Objective

Understand ties by hand.

### Sample data

```sql
CREATE TEMP TABLE scores (
    player TEXT,
    score INTEGER
);

INSERT INTO scores VALUES
    ('A', 100),
    ('B', 100),
    ('C', 90),
    ('D', 80),
    ('E', 80);
```

### Task

Compute:

```text
ROW_NUMBER
RANK
DENSE_RANK
```

ordered by score descending.

### Before running SQL

Predict:

```text
player A:
ROW_NUMBER = ?

RANK = ?

DENSE_RANK = ?
```

and do the same for each row.

### Solution

```sql
SELECT
    player,
    score,
    ROW_NUMBER() OVER (
        ORDER BY score DESC, player
    ) AS row_number_result,
    RANK() OVER (
        ORDER BY score DESC
    ) AS rank_result,
    DENSE_RANK() OVER (
        ORDER BY score DESC
    ) AS dense_rank_result
FROM scores
ORDER BY score DESC, player;
```

Notice that the `ROW_NUMBER` expression uses `player` as a tie-breaker, while `RANK` and `DENSE_RANK` order only by score so ties remain peers.

---

## 75. Hands-On Exercise 2 — Top 3 Products Per Country

### Task

Return the top three products per country by revenue.

First answer:

```text
Do ties count as separate rank positions?

Do we need exactly three rows?

Or all rows tied at the third position?
```

### Solution A — exactly three rows

```sql
WITH ranked AS (
    SELECT
        country,
        product_id,
        revenue,
        ROW_NUMBER() OVER (
            PARTITION BY country
            ORDER BY revenue DESC, product_id
        ) AS rn
    FROM product_revenue
)
SELECT *
FROM ranked
WHERE rn <= 3;
```

### Solution B — all tied rows at rank three

```sql
WITH ranked AS (
    SELECT
        country,
        product_id,
        revenue,
        RANK() OVER (
            PARTITION BY country
            ORDER BY revenue DESC
        ) AS rnk
    FROM product_revenue
)
SELECT *
FROM ranked
WHERE rnk <= 3;
```

---

## 76. Hands-On Exercise 3 — Running Total

### Task

Given one row per day:

```text
date | revenue
-----+--------
1    | 100
2    |  50
3    | 200
```

calculate running revenue.

### Solution

```sql
SELECT
    revenue_date,
    revenue,
    SUM(revenue) OVER (
        ORDER BY revenue_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_revenue
FROM daily_revenue
ORDER BY revenue_date;
```

Expected:

```text
1 → 100
2 → 150
3 → 350
```

---

## 77. Hands-On Exercise 4 — Seven-Row vs Time-Based Window

### Task

Given:

```text
Jan 1
Jan 2
Jan 8
Jan 9
```

compare:

```sql
ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
```

with an appropriate time-based range.

### Required reasoning

For Jan 8:

```text
Which physical rows are in the ROWS frame?

Which calendar timestamps are in the time-based frame?
```

The purpose is not memorizing syntax.

The purpose is learning that:

```text
row count
≠
elapsed time
```

---

## 78. Hands-On Exercise 5 — `LAG`

### Task

Calculate the number of days since the previous order for each customer.

### Solution

```sql
SELECT
    customer_id,
    order_id,
    order_date,
    order_date
        - LAG(order_date) OVER (
            PARTITION BY customer_id
            ORDER BY order_date, order_id
          ) AS gap_since_previous
FROM orders;
```

The first order per customer naturally has no previous row.

---

## 79. Hands-On Exercise 6 — Month-over-Month

### Task

Return:

```text
month
revenue
previous_revenue
absolute_change
percentage_change
```

### Solution

```sql
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', order_ts) AS month,
        SUM(amount) AS revenue
    FROM orders
    GROUP BY 1
),
compared AS (
    SELECT
        month,
        revenue,
        LAG(revenue) OVER (
            ORDER BY month
        ) AS previous_revenue
    FROM monthly
)
SELECT
    month,
    revenue,
    previous_revenue,
    revenue - previous_revenue AS absolute_change,
    (revenue - previous_revenue)
        / NULLIF(previous_revenue, 0) AS percentage_change
FROM compared
ORDER BY month;
```

---

## 80. Hands-On Exercise 7 — Gaps and Islands

### Task

Find each user's longest consecutive active-day streak.

### Required pipeline

```text
daily activity
→ one row per user/day
→ row number
→ island key
→ group islands
→ calculate streak length
→ choose longest
```

### Solution

Use the pattern from Sections 39–40 and explicitly verify the island key on at least five hand-calculated rows before relying on the final query.

---

## 81. Hands-On Exercise 8 — Sessionisation

### Task

Sessionize click events using a 30-minute inactivity threshold.

Return:

```text
user_id
session_id
session_start
session_end
event_count
duration
```

### Required fields before coding

```text
Event grain:
Partition key:
Event ordering:
Inactivity threshold:
Previous event:
Gap:
New-session flag:
Session ID:
Session output grain:
```

### Solution

Use the CTE chain from Section 43.

Do the first five events by hand before running the full SQL.

---

## 82. Hands-On Exercise 9 — Cohort Retention

### Task

Build a monthly cohort-retention table.

At minimum produce:

```text
signup_month
activity_month
active_users
cohort_size
retention_rate
```

### Required reasoning

Write:

```text
One row in the base activity relation represents ______.

One row in the cohort relation represents ______.

One row in the retention output represents ______.

The denominator is ______ because ______.
```

The hardest part is usually the denominator, not the window function.

---

## 83. Hands-On Exercise 10 — `QUALIFY`

### Task

Rewrite a top-three-per-country query using DuckDB `QUALIFY`.

### Solution

```sql
SELECT
    country,
    product_id,
    revenue
FROM product_revenue
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY country
    ORDER BY revenue DESC, product_id
) <= 3;
```

### Dialect note

This is deliberately a DuckDB-aware exercise.

For portable SQL, use the CTE/subquery pattern.

---

# 84. Beginner Practice

The following exercises should be solved without looking at the solution immediately.

## Exercise 1 — `OVER()`

Calculate the total number of orders while keeping every order row.

```sql
COUNT(*) OVER ()
```

State the output grain.

## Exercise 2 — `PARTITION BY`

Attach each customer's order count to every order row.

```sql
COUNT(*) OVER (
    PARTITION BY customer_id
)
```

## Exercise 3 — Window `ORDER BY`

Assign a global sequence based on order time.

Add a tie-breaker if needed.

## Exercise 4 — `ROW_NUMBER`

Number each customer's orders from oldest to newest.

## Exercise 5 — `RANK`

Rank products by revenue with ties preserved.

## Exercise 6 — `DENSE_RANK`

Explain how the result differs from `RANK`.

## Exercise 7 — `LAG`

Return the previous order amount per customer.

## Exercise 8 — `LEAD`

Return the next order date per customer.

## Exercise 9 — `FIRST_VALUE`

Show each customer's first order amount on every row.

## Exercise 10 — Aggregate Window

Attach each customer's total revenue to every order.

For every exercise, state:

```text
partition
order
output grain
tie behavior
```

---

# 85. Intermediate Practice

## Exercise 1 — Customer Running Total

Build a deterministic running total.

## Exercise 2 — Share of Customer Total

Calculate order contribution as a decimal ratio.

## Exercise 3 — Window Frame Prediction

Given duplicate order dates, predict frame membership for `ROWS` and `RANGE`.

## Exercise 4 — `GROUPS`

Construct a tiny peer-group example and explain which groups are included.

## Exercise 5 — Moving Average

Calculate:

```text
ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
```

and explain its exact row count.

## Exercise 6 — Time-Based Moving Metric

Design a time-based window for the previous seven calendar days where the target engine supports the required syntax.

## Exercise 7 — Top-N

Return exactly three products per country.

## Exercise 8 — Tied Top-N

Return all products tied at the third rank.

## Exercise 9 — Latest Record

Return one deterministic current row per customer.

## Exercise 10 — Window Filtering

Write both:

```text
CTE solution
```

and:

```text
QUALIFY solution
```

when supported.

For each exercise, write:

```text
Input grain:
Partition:
Ordering:
Frame:
Output grain:
Tie-breaking:
NULL behavior:
Validation:
```

---

# 86. Advanced Practice

## Exercise 1 — `PERCENT_RANK`

Calculate relative rank and explain how ties affect the output.

## Exercise 2 — `CUME_DIST`

Use a dataset with ties and manually compute the cumulative proportions.

## Exercise 3 — Gaps and Islands

Find all activity islands for each user.

## Exercise 4 — Longest Streak

Return one deterministic longest streak per user.

## Exercise 5 — Sessionisation

Sessionize events with a 30-minute threshold and explain the session-number running sum.

## Exercise 6 — MoM

Build a monthly revenue comparison with zero-safe percentage change.

## Exercise 7 — YoY

Calculate 12-period lag and verify that the input month series is complete.

## Exercise 8 — Cohort Retention

Build a cohort-retention grid and justify the denominator.

## Exercise 9 — Default-Frame Debugging

Explain why a `LAST_VALUE` query is returning an unexpected result and repair it with an explicit frame.

## Exercise 10 — Multiple Windows

Write a query that calculates:

```text
running total
running average
previous value
rank
```

using the same partition/order where possible.

Then explain which parts might be shareable and which changes would potentially require additional work.

---

# 87. Production Case Study

## E-Commerce Analytics Pipeline

An e-commerce platform has:

```text
customers
orders
order_events
products
daily_activity
```

The analytics team needs:

1. top three products by country;
2. latest customer state;
3. running daily revenue;
4. seven-day moving revenue;
5. previous-order gap;
6. longest activity streak;
7. 30-minute sessions;
8. month-over-month revenue;
9. cohort retention.

### Required design

```text
raw data
   ↓
clean/order data
   ↓
window calculations
   ↓
intermediate CTEs
   ↓
final metrics
```

### Metric 1 — Top 3 Products

```text
Input grain:
one row per product/country

Partition:
country

Order:
revenue DESC

Frame:
not applicable

Output:
one row per selected product/country

Tie-break:
product_id if exactly three rows are required

Validation:
≤ 3 rows per country
```

### Metric 2 — Latest Customer State

```text
Input grain:
one row per customer event/version

Partition:
customer_id

Order:
updated_at DESC, record_id DESC

Output:
one row per customer

Validation:
exactly one row per customer
```

### Metric 3 — Running Revenue

```text
Input grain:
one row per day

Partition:
global, unless a per-country metric is requested

Order:
revenue_date

Frame:
UNBOUNDED PRECEDING → CURRENT ROW

Output:
one row per day
```

### Metric 4 — Moving Revenue

First decide:

```text
7 rows
or
7 calendar days?
```

Do not proceed until this is explicit.

### Metric 5 — Previous-Order Gap

```text
Partition:
customer_id

Order:
order_date, order_id

Function:
LAG(order_date)
```

### Metric 6 — Longest Activity Streak

```text
activity rows
→ user/day
→ row_number
→ island key
→ streaks
→ longest streak
```

### Metric 7 — Sessions

```text
event
→ previous event
→ inactivity gap
→ new-session flag
→ running sum
→ session aggregate
```

### Metric 8 — MoM

```text
orders
→ monthly revenue
→ LAG
→ change
→ percentage change
```

### Metric 9 — Retention

```text
users
→ signup cohort
activity
→ activity month
→ month offset
→ active users
→ cohort denominator
→ retention
```

### Production review questions

Before shipping, ask:

```text
Is every input grain known?

Is every output grain known?

Are partitions intentional?

Are orders deterministic?

Are tie rules explicit?

Are frames intentional?

Are missing dates handled?

Are first/last rows understood?

Are NULLs intentional?

Can a reviewer explain the query without executing it?

What invariant proves correctness?

What happens when data volume grows 100×?
```

---

# 88. Interview Questions

## Question 1 — What Is a Window Function?

### Concise answer

A window function calculates across a related set of rows while preserving the current row instead of collapsing the rows into one row per group.

### Deeper explanation

The window is defined by partition, ordering, and sometimes a frame.

### SQL example

```sql
SUM(amount) OVER (
    PARTITION BY customer_id
)
```

### Likely follow-up

How does that differ from `GROUP BY`?

### Common mistake

Saying a window function “groups rows.”

---

## Question 2 — What Does `OVER()` Mean?

### Concise answer

`OVER()` tells SQL to evaluate a function as a window function.

### Deeper explanation

`OVER` can optionally contain:

```text
PARTITION BY
ORDER BY
frame
```

### SQL example

```sql
COUNT(*) OVER ()
```

### Likely follow-up

What changes if you add `PARTITION BY customer_id`?

### Common mistake

Thinking `OVER()` automatically means a running total. It does not; the window specification determines behavior.

---

## Question 3 — What Does `PARTITION BY` Do?

### Concise answer

It splits rows into independent logical window populations.

### SQL example

```sql
ROW_NUMBER() OVER (
    PARTITION BY country
    ORDER BY revenue DESC
)
```

### Follow-up

What happens with no `PARTITION BY`?

### Common mistake

Confusing logical window partitions with physical database partitions.

---

## Question 4 — Window `ORDER BY` vs Final `ORDER BY`

### Concise answer

Window `ORDER BY` defines calculation sequence; final `ORDER BY` controls final result presentation.

### Example

```sql
ROW_NUMBER() OVER (
    ORDER BY created_at
)
```

versus:

```sql
ORDER BY customer_id
```

### Common mistake

Assuming the final displayed order determines the window's calculation order.

---

## Question 5 — `ROW_NUMBER` vs `RANK`

### Concise answer

`ROW_NUMBER` gives unique row positions. `RANK` gives tied rows the same rank and leaves gaps after ties.

### Example

```text
100, 100, 90

ROW_NUMBER:
1,2,3

RANK:
1,1,3
```

### Follow-up

What would you use for exactly three rows per group?

### Common mistake

Using `RANK` when the requirement is exactly three rows.

---

## Question 6 — `RANK` vs `DENSE_RANK`

### Concise answer

Both share ranks for ties. `RANK` leaves gaps; `DENSE_RANK` does not.

### Common mistake

Claiming the two functions always return the same values.

---

## Question 7 — What Is `NTILE`?

### Concise answer

`NTILE(n)` places ordered rows into approximately equal-sized buckets.

### Follow-up

Is that the same as exact percentile computation?

### Common mistake

Calling `NTILE(4)` an exact quartile-value calculation.

---

## Question 8 — What Is `PERCENT_RANK`?

### Concise answer

It describes a row's relative rank position on a roughly 0-to-1 scale.

### Follow-up

How does it differ from `CUME_DIST`?

### Common mistake

Treating it as an equal-size numeric bucket.

---

## Question 9 — What Is `CUME_DIST`?

### Concise answer

It is the proportion of rows whose ordering value is less than or equal to the current row's ordering value.

### Follow-up

How do ties affect it?

### Common mistake

Using it as a replacement for `PERCENT_RANK` without checking the metric definition.

---

## Question 10 — What Is a Window Frame?

### Concise answer

A frame defines which rows inside the ordered partition are visible to the current row for frame-sensitive calculations.

### Mental model

```text
partition
→ order
→ frame
→ function
```

### Common mistake

Treating the partition as the frame.

---

## Question 11 — `ROWS` vs `RANGE`

### Concise answer

`ROWS` is based on physical row positions; `RANGE` is based on ordering values and peer/value boundaries.

### Follow-up

Why does this matter with duplicate timestamps?

### Common mistake

Saying “both mean previous N rows.”

---

## Question 12 — What Is `GROUPS`?

### Concise answer

`GROUPS` moves the frame in units of peer groups created by the window ordering.

### Follow-up

Give a use case involving duplicate ordering values.

### Common mistake

Calling `GROUPS` equivalent to `ROWS`.

---

## Question 13 — Why Does `LAST_VALUE` Surprise People?

### Concise answer

Because `LAST_VALUE` returns the last value in the current frame, not necessarily the final value of the entire partition.

### Fix

Use an explicit frame when the whole partition is intended:

```sql
ROWS BETWEEN UNBOUNDED PRECEDING
         AND UNBOUNDED FOLLOWING
```

### Common mistake

Changing the function instead of inspecting the frame.

---

## Question 14 — How Do You Calculate a Running Total?

### Concise answer

Use an ordered `SUM` window with an explicit cumulative frame.

```sql
SUM(amount) OVER (
    ORDER BY order_date
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
)
```

### Follow-up

What if timestamps tie?

### Common mistake

Ignoring deterministic ordering.

---

## Question 15 — How Do You Get the Previous Row?

### Concise answer

Use `LAG`.

```sql
LAG(amount) OVER (
    PARTITION BY customer_id
    ORDER BY order_date, order_id
)
```

### Follow-up

How do you supply a default?

### Common mistake

Forgetting that the first row has no previous row.

---

## Question 16 — `LAG` vs `LEAD`

### Concise answer

`LAG` looks backward in window order; `LEAD` looks forward.

### Follow-up

How would you use `LEAD` to calculate a validity end date?

### Common mistake

Confusing `LEAD` with `MAX`.

---

## Question 17 — How Do You Find Top-N Per Group?

### Concise answer

Rank within the group and filter the rank.

### Exactly N rows

Use:

```sql
ROW_NUMBER()
```

### Preserve ties at the cutoff

Use:

```sql
RANK()
```

### Common mistake

Choosing a ranking function before clarifying the tie requirement.

---

## Question 18 — How Do You Find the Latest Record Per Key?

### Concise answer

Use `ROW_NUMBER()` partitioned by the key and ordered by recency plus deterministic tie-breakers.

### Example

```sql
ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY updated_at DESC, record_id DESC
)
```

### Follow-up

Why is `MAX(updated_at)` alone insufficient?

### Common mistake

Joining back only on timestamp and allowing multiple matching rows.

---

## Question 19 — What Are Gaps and Islands?

### Concise answer

It is a pattern for grouping ordered records into consecutive runs.

### Follow-up

How can `ROW_NUMBER` help?

### Common mistake

Trying to aggregate before identifying the sequence.

---

## Question 20 — How Do You Sessionize Events?

### Concise answer

Use `LAG` to compare each event with the previous event, mark session boundaries, then running-sum the flags to create session IDs.

### Pattern

```text
LAG
→ gap
→ flag
→ running SUM
→ session
```

### Common mistake

Using row count rather than elapsed time for an inactivity threshold.

---

## Question 21 — How Do You Calculate Month-over-Month Change?

### Concise answer

Aggregate to month, use `LAG`, then calculate absolute and relative change.

### Common mistake

Ignoring missing months.

---

## Question 22 — How Do You Calculate Year-over-Year Change?

### Concise answer

For a complete monthly series, compare to the row twelve positions earlier or construct another explicit prior-year relation.

### Common mistake

Assuming “12 rows ago” always means “12 calendar months ago.”

---

## Question 23 — How Does Cohort Retention Work?

### Concise answer

Assign users to a signup cohort, map activity into periods, count active users by cohort/period, and divide by the original cohort population.

### Follow-up

Why is the denominator important?

### Common mistake

Using current-month active users as the denominator.

---

## Question 24 — Why Are Deterministic Tie-Breakers Important?

### Concise answer

Because a non-unique window ordering does not fully define which peer row comes first, which can make row-selection outputs unstable.

### Common mistake

Assuming a timestamp is unique because it “usually” is.

---

## Question 25 — Can Multiple Window Functions Share Sorting Work?

### Concise answer

Compatible partitioning and ordering specifications may allow work to be shared, while materially different specifications may require additional processing.

### Common mistake

Claiming one function always equals one sort.

---

## Question 26 — What Can Make a Window Query Expensive?

### Concise answer

Large partitions, expensive ordering, wide rows, many distinct window specifications, and large data volumes can all increase cost.

### Follow-up

What do you inspect next?

### Answer

Measure the actual plan and avoid guessing.

---

## Question 27 — Debug This Latest-Record Query

### Broken query

```sql
SELECT *
FROM customer_events
WHERE updated_at = (
    SELECT MAX(updated_at)
    FROM customer_events e2
    WHERE e2.customer_id = customer_events.customer_id
);
```

### Problem

A customer can have multiple rows at the maximum timestamp.

### Window-based repair

```sql
WITH ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY updated_at DESC, record_id DESC
        ) AS rn
    FROM customer_events
)
SELECT *
FROM ranked
WHERE rn = 1;
```

### Follow-up

What happens when `updated_at` ties?

---

## Question 28 — Predict the `RANK` Output

Given:

```text
score
-----
100
100
90
```

what is:

```sql
RANK() OVER (
    ORDER BY score DESC
)
```

### Answer

```text
1
1
3
```

### Follow-up

What does `DENSE_RANK` return?

```text
1
1
2
```

---

## Question 29 — Diagnose a Seven-Day Metric

A business user says:

> “Your seven-day average is not a seven-day average.”

The query uses:

```sql
ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
```

### Answer

That is a seven-row moving average.

The candidate should ask whether the business means:

```text
seven rows
```

or:

```text
seven calendar days
```

---

## Question 30 — Diagnose a Sessionisation Bug

A sessionization query uses:

```sql
LAG(event_time) OVER (
    ORDER BY event_time
)
```

### Problem

Events from different users are being compared.

### Fix

```sql
LAG(event_time) OVER (
    PARTITION BY user_id
    ORDER BY event_time, event_id
)
```

### Production lesson

Partitioning is part of the definition of “previous.”

---

# 89. Production Checklist

Before shipping a window-function query:

### Data shape

- [ ] Input grain is explicitly known.
- [ ] Output grain is explicitly known.
- [ ] Upstream joins do not accidentally multiply rows.

### Partition

- [ ] `PARTITION BY` is intentional.
- [ ] Global windows are intentional when `PARTITION BY` is absent.
- [ ] No accidental partition reset exists.

### Ordering

- [ ] Window `ORDER BY` represents business sequence.
- [ ] Final result `ORDER BY` is understood separately.
- [ ] Tie-breakers are explicit where required.
- [ ] Ordering is deterministic where survivor selection matters.

### Ranking

- [ ] `ROW_NUMBER` vs `RANK` vs `DENSE_RANK` is a deliberate choice.
- [ ] `NTILE` is not being confused with percentiles.
- [ ] `PERCENT_RANK` and `CUME_DIST` semantics are understood.

### Offsets

- [ ] `LAG` offset is correct.
- [ ] `LEAD` offset is correct.
- [ ] Defaults are semantically appropriate.
- [ ] First/last-row NULL behavior is intentional.

### Frames

- [ ] Frame semantics have been reviewed.
- [ ] `ROWS`, `RANGE`, or `GROUPS` is deliberate.
- [ ] Peer behavior is understood.
- [ ] Default-frame behavior is not being assumed incorrectly.
- [ ] `LAST_VALUE` has the intended frame.

### Advanced patterns

- [ ] Top-N tie semantics are explicit.
- [ ] Latest-record selection is deterministic.
- [ ] Gaps-and-islands grain is correct.
- [ ] Session threshold is explicit.
- [ ] Missing periods are handled for MoM/YoY where necessary.
- [ ] Cohort denominator is correct.

### Dialect

- [ ] `QUALIFY` is used only where supported.
- [ ] Engine-specific frame syntax is verified.
- [ ] Standard SQL alternatives exist where portability matters.

### Performance

- [ ] Large partitions have been considered.
- [ ] Rows are reduced before windowing when semantically safe.
- [ ] Unnecessary columns are not carried through the window.
- [ ] Multiple distinct window specifications are understood.
- [ ] Performance is measured with the execution plan when the workload is significant.

### Validation

- [ ] Important invariants have assertion queries.
- [ ] Tiny hand-computed test data exists for difficult semantics.
- [ ] First-row, last-row, NULL, tie, and missing-period cases are tested.

---

# 90. Final Knowledge Check

The following is a practical assessment. Write the SQL before reading the expected direction.

## Assessment 1 — `OVER()`

Explain what:

```sql
COUNT(*) OVER ()
```

returns and state its output grain.

### Expected reasoning

All current rows remain visible, and each row receives the same overall count.

---

## Assessment 2 — `PARTITION BY`

Write SQL that assigns each order its customer's total revenue.

### Expected direction

```sql
SUM(amount) OVER (
    PARTITION BY customer_id
)
```

---

## Assessment 3 — Window Ordering

Explain why:

```sql
ROW_NUMBER() OVER (
    ORDER BY created_at
)
```

can be non-deterministic when timestamps tie.

### Expected reasoning

The order does not define which peer row comes first.

---

## Assessment 4 — Ranking

Given:

```text
100, 100, 90
```

state:

```text
ROW_NUMBER
RANK
DENSE_RANK
```

### Expected result

One valid deterministic `ROW_NUMBER` sequence is:

```text
1, 2, 3
```

`RANK`:

```text
1, 1, 3
```

`DENSE_RANK`:

```text
1, 1, 2
```

---

## Assessment 5 — `NTILE`

Explain what:

```sql
NTILE(4)
```

is trying to accomplish.

### Expected reasoning

Approximately equal-sized ordered row buckets.

---

## Assessment 6 — `PERCENT_RANK`

Explain the conceptual range and meaning of the function.

### Expected reasoning

Relative rank position on a 0-to-1 scale.

---

## Assessment 7 — `CUME_DIST`

Explain what population is accumulated for the current ordering value.

### Expected reasoning

Rows whose ordering value is less than or equal to the current ordering value.

---

## Assessment 8 — `LAG`

Write the previous order amount per customer.

### Expected direction

```sql
LAG(amount) OVER (
    PARTITION BY customer_id
    ORDER BY order_date, order_id
)
```

---

## Assessment 9 — `LEAD`

Write the next order date per customer.

### Expected direction

```sql
LEAD(order_date) OVER (
    PARTITION BY customer_id
    ORDER BY order_date, order_id
)
```

---

## Assessment 10 — First Value

Return each customer's first order date on every row.

### Expected direction

```sql
FIRST_VALUE(order_date) OVER (
    PARTITION BY customer_id
    ORDER BY order_date, order_id
)
```

---

## Assessment 11 — Last Value

Explain why this can surprise:

```sql
LAST_VALUE(amount) OVER (
    PARTITION BY customer_id
    ORDER BY order_date
)
```

### Expected reasoning

The result is the last value in the current frame, not automatically the final value of the entire partition.

---

## Assessment 12 — Running Total

Write a deterministic cumulative sum.

### Expected direction

```sql
SUM(amount) OVER (
    PARTITION BY customer_id
    ORDER BY order_date, order_id
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
)
```

---

## Assessment 13 — Share of Total

Write a customer-level share of total.

### Expected direction

```sql
amount / NULLIF(
    SUM(amount) OVER (
        PARTITION BY customer_id
    ),
    0
)
```

Cast to an appropriate numeric type when needed.

---

## Assessment 14 — Frame Selection

Explain the semantic difference between:

```sql
ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
```

and:

```text
a six-day elapsed-time window
```

### Expected reasoning

The first is seven physical ordered rows at most; the second is based on elapsed time.

---

## Assessment 15 — `GROUPS`

Explain why peer groups matter to `GROUPS`.

### Expected reasoning

A peer group is a set of rows tied on the window's ordering values.

---

## Assessment 16 — Filtering a Window

Fix:

```sql
SELECT
    *,
    ROW_NUMBER() OVER (
        PARTITION BY customer_id
        ORDER BY amount DESC
    ) AS rn
FROM orders
WHERE rn <= 3;
```

### Expected direction

Use a CTE/subquery or supported `QUALIFY`.

---

## Assessment 17 — Top-N with Ties

The requirement is:

> Include all products tied for third place.

Which ranking function is appropriate?

### Expected answer

`RANK` or another ranking strategy matching the tie requirement; do not use `ROW_NUMBER` if tied third-place rows must all survive.

---

## Assessment 18 — Latest Record

Write a latest-record-per-customer query.

### Required reasoning

Include a deterministic tie-breaker.

---

## Assessment 19 — Gaps and Islands

Explain why:

```text
date - row_number
```

can become a constant island key across consecutive dates.

### Expected reasoning

Both the date and row position advance by one for each consecutive date, leaving the difference unchanged.

---

## Assessment 20 — Sessionisation

Explain the full pipeline:

```text
LAG
→ gap
→ flag
→ running SUM
→ session
```

### Expected reasoning

Each stage converts local sequence information into a cumulative session identifier.

---

## Assessment 21 — MoM

Why can:

```sql
LAG(revenue)
```

produce the wrong business comparison when months are missing?

### Expected reasoning

It returns the previous available row, not necessarily the previous calendar month.

---

## Assessment 22 — YoY

Why can:

```sql
LAG(revenue, 12)
```

fail to represent one year earlier?

### Expected reasoning

It means twelve rows earlier, not automatically twelve calendar months earlier.

---

## Assessment 23 — Cohort Retention

State the denominator for cohort retention.

### Expected reasoning

The original cohort population, not the active population of the comparison month.

---

## Assessment 24 — Determinism

Give an example of a tie-breaker.

### Expected direction

```sql
ORDER BY updated_at DESC, record_id DESC
```

where `record_id` is an appropriate unique tie-breaker.

---

## Assessment 25 — Named Window

Write one named window reused by:

```text
SUM
AVG
LAG
```

### Expected direction

```sql
WINDOW w AS (
    PARTITION BY customer_id
    ORDER BY order_date, order_id
)
```

then:

```sql
SUM(amount) OVER w
AVG(amount) OVER w
LAG(amount) OVER w
```

---

## Assessment 26 — Multiple Windows

Explain why ten window functions do not necessarily imply ten sorts.

### Expected reasoning

Compatible window definitions may share work; materially different partition/order specifications can require additional processing.

---

## Assessment 27 — Debugging

A `LAG` query compares events across users.

What do you inspect first?

### Expected answer

The window partition.

---

## Assessment 28 — Debugging

A moving average uses:

```sql
ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
```

but the business says “seven calendar days.”

What do you inspect?

### Expected answer

The time semantics and whether a complete date domain or time-based frame is required.

---

## Assessment 29 — Assertions

Write an assertion that should return zero rows if a latest-record table has exactly one row per customer.

### Expected direction

```sql
SELECT customer_id
FROM latest_customers
GROUP BY customer_id
HAVING COUNT(*) <> 1;
```

---

## Assessment 30 — Senior Reasoning

A production window query is unexpectedly slow.

What is your first sequence of actions?

### Expected answer

```text
state the grain
→ inspect data volume
→ identify partitioning and ordering
→ look for unnecessary upstream rows
→ identify multiple distinct window specifications
→ inspect the execution plan
→ form a hypothesis
→ make one change
→ measure again
```

---

# 91. Final Checkpoint — Ready for Topic 06?

You are ready to move to the next topic when you can demonstrate all four of these capabilities.

## Checkpoint 1 — Ranking

Explain and demonstrate:

```text
ROW_NUMBER
vs
RANK
vs
DENSE_RANK
```

using ties.

You should be able to answer:

```text
Do ties share rank?

Are gaps introduced?

Do I need exactly N rows?

Or all rows tied at rank N?
```

## Checkpoint 2 — Frames

Explain and demonstrate:

```text
ROWS
vs
RANGE
vs
GROUPS
```

and explain the default-frame behavior relevant to your PostgreSQL/DuckDB workload.

You should be able to state:

```text
Partition:
Order:
Current row:
Frame:
Visible rows:
Function:
Result:
```

## Checkpoint 3 — Gaps and Islands + Sessionisation

You should be able to solve both from scratch.

For gaps-and-islands:

```text
ordered rows
→ row number
→ island key
→ streak
```

For sessionisation:

```text
LAG
→ gap
→ new-session flag
→ running SUM
→ session
```

## Checkpoint 4 — Window Filtering

You should be able to solve the same top-N problem:

```text
with a standard CTE/subquery
```

and:

```text
with QUALIFY
```

where supported.

### Practical checkpoint test

Do not merely explain these concepts.

Actually write SQL for:

1. top three products per country with ties handled deliberately;
2. a seven-row running/moving metric with an explicit frame;
3. a latest-record-per-key query with a deterministic tie-breaker;
4. a longest consecutive-day streak;
5. a 30-minute sessionization query;
6. a standard CTE-filtered window query;
7. a DuckDB `QUALIFY` equivalent.

If you can do those correctly and explain the grain, partition, order, frame, tie behavior, and edge cases, the Topic 05 checkpoint is complete.

---

# 92. Final Summary — The Window-Function Mental Model

Keep this model:

```text
Start with rows
     ↓
What does one row represent?
     ↓
Choose the partition
     ↓
Choose the order
     ↓
Choose the frame when relevant
     ↓
Choose the function
     ↓
Check ties and NULLs
     ↓
Check determinism
     ↓
Validate with tiny data
     ↓
Measure at production scale
```

And remember:

```text
GROUP BY
→ collapses rows

WINDOW FUNCTION
→ preserves rows
+
adds context
```

The deepest production habit is:

> **Do not choose a window function because you recognize a familiar pattern. Choose it because you can state exactly which related rows the current row is supposed to see, in what order, under what frame, and why the resulting value answers the business question.**

For difficult window queries, return to four questions:

```text
1. What is the partition?
2. What is the order?
3. What is the frame?
4. What does the function calculate from those rows?
```

That reasoning scales much better than memorizing isolated SQL recipes.
