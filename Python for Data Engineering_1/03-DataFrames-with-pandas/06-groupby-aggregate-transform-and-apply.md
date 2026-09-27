# 06 — groupby, aggregate, transform, and apply

> **Stage 2 — Python for Data Engineering → Module 2.3 — DataFrames with pandas**
>
> **Topic 06:** groupby: aggregate, transform, and apply  
> **Level:** Basic → Intermediate → Advanced → Production-oriented  
> **Primary mental model:** **Rows → Grouping keys → Groups → Apply operation → Combine results**

---

## Learning contract

This chapter follows the authoritative Module 2.3 roadmap for Topic 06.

The goal is not to memorize a list of `GroupBy` methods. The goal is to understand the **shape, alignment, semantics, and cost** of grouped operations well enough to design reliable Data Engineering transformations.

By the end of this chapter, you should be able to answer, without guessing:

- What does grouping actually mean?
- What happens with one grouping key versus several?
- How many rows should a grouped result contain?
- What do `count`, `size`, and `nunique` count?
- When should a task use `agg`, `transform`, `filter`, or `apply`?
- How are group-wise ranking and running calculations expressed?
- What happens to null grouping keys?
- What changes when grouping keys are categoricals?
- How do named aggregations keep Gold-table schemas readable?
- How do you preserve row-level alignment with `transform`?
- Why can `apply` be expensive, and what alternatives should you test first?
- How can group counts expose key-cardinality problems before a join?
- How can SQL `GROUP BY` and common window-function logic be translated into pandas?
- How do you benchmark grouped operations on millions of rows without inventing performance numbers?

### The habit for this entire chapter

For important examples use:

```text
Predict
  ↓
Run
  ↓
Inspect
  ↓
Assert
  ↓
Explain
```

Do not let pandas run first and reason later. In production Data Engineering, **shape reasoning is a correctness skill**.

---

# 1. Why `groupby` Matters in Data Engineering

Most Gold tables are aggregates.

A raw or Silver table often has **event-level rows**:

```text
order_id | customer_id | country | product_id | amount | order_date
---------|-------------|---------|------------|--------|-----------
O1001    | C001        | IN      | P10        | 500    | 2026-01-03
O1002    | C001        | IN      | P11        | 250    | 2026-01-05
O1003    | C002        | US      | P10        | 900    | 2026-01-06
...
```

A Gold table may instead contain one row per customer:

```text
customer_id | total_revenue | order_count | distinct_products
------------|---------------|-------------|------------------
C001        | 750           | 2           | 2
C002        | 900           | 1           | 1
```

That change in **grain** is exactly what grouping is for.

Typical Data Engineering metrics include:

| Business question | Typical grouped operation |
|---|---|
| Revenue by customer | `groupby(...).sum()` |
| Revenue by country | `groupby(...).sum()` |
| Average order value by country | `groupby(...).mean()` |
| Number of orders per customer | `groupby(...).size()` or `count()` depending on semantics |
| Distinct products per customer | `groupby(...).nunique()` |
| First/last event date | grouped `min` / `max` or order-sensitive `first` / `last` |
| Customer share of total revenue | `transform("sum")` |
| Customers with at least 3 orders | grouped `filter` |
| Product rank inside each country | grouped `rank()` |
| Running revenue by customer | grouped `cumsum()` |
| Previous event amount | grouped `shift()` |
| Days since previous event | grouped `diff()` |
| Top 3 products per country | grouped `nlargest()` or group-wise rank/filter |

## SQL `GROUP BY` and pandas `groupby`

The conceptual relationship is:

```sql
SELECT
    country,
    SUM(amount) AS revenue
FROM orders
GROUP BY country;
```

and:

```python
df.groupby("country", as_index=False).agg(
    revenue=("amount", "sum"),
)
```

The mental model is similar:

```text
SQL:
rows
  → GROUP BY keys
  → one logical group per key combination
  → aggregate
  → grouped result

pandas:
rows
  → groupby(keys)
  → GroupBy object
  → aggregate / transform / filter / apply
  → combined result
```

Pandas goes beyond ordinary SQL `GROUP BY` because the grouped object can also support many operations that resemble SQL window functions, such as `rank`, `cumsum`, `shift`, `diff`, and `cumcount`.

They are **conceptually related, not syntactically identical**. Ordering, missing values, index behavior, and output shape still have to be reasoned about explicitly.

---

# 2. The Split-Apply-Combine Mental Model

The foundational model is:

```text
              rows
                |
              Split
                |
        +-------+-------+
        |       |       |
      group A group B group C
        |       |       |
      Apply   Apply   Apply
        |       |       |
        +-------+-------+
                |
             Combine
                |
             result
```

## 2.1 Split

Suppose:

```python
df.groupby("country")
```

Pandas uses the `country` values to determine which rows belong together.

Conceptually:

```text
country = IN
    rows 0, 1, 4

country = US
    rows 2, 3

country = GB
    row 5
```

The actual object returned is a `DataFrameGroupBy`, not a materialized table containing one copy of every group.

```python
grouped = df.groupby("country")

print(type(grouped))
```

Expected result conceptually:

```text
pandas.core.groupby.generic.DataFrameGroupBy
```

The important point is that `grouped` represents the grouping operation and gives you a family of grouped operations.

## 2.2 Apply

For:

```python
df.groupby("country")["amount"].sum()
```

the operation is:

```text
group each country
→ take amount inside that group
→ calculate sum for that group
```

## 2.3 Combine

The per-group results are put together into a new pandas object.

That means grouping often **changes the grain**.

### Prediction-first question

Before running:

```python
result = df.groupby("country")["amount"].sum()
```

ask:

> How many rows should `result` contain?

A strong first approximation is:

> One output row per distinct, retained grouping-key combination.

But do not blindly memorize "number of unique combinations." Null-key handling and categorical grouping options can change which groups are retained.

---

# 3. Tiny DataFrame: Your First Groupby

Use this DataFrame throughout the first part of the chapter:

```python
import pandas as pd

orders = pd.DataFrame(
    {
        "order_id": ["O1", "O2", "O3", "O4", "O5", "O6"],
        "customer_id": ["C1", "C1", "C2", "C2", "C2", "C3"],
        "country": ["IN", "IN", "US", "US", "US", "IN"],
        "status": ["paid", "paid", "paid", "cancelled", "paid", "paid"],
        "product_id": ["P1", "P2", "P1", "P3", "P1", "P4"],
        "amount": [100.0, 250.0, 80.0, 120.0, 160.0, 90.0],
    }
)

print(orders)
```

Conceptually:

```text
  order_id customer_id country     status product_id  amount
0       O1          C1      IN       paid         P1   100.0
1       O2          C1      IN       paid         P2   250.0
2       O3          C2      US       paid         P1    80.0
3       O4          C2      US  cancelled         P3   120.0
4       O5          C2      US       paid         P1   160.0
5       O6          C3      IN       paid         P4    90.0
```

### Predict

For:

```python
orders.groupby("country")["amount"].sum()
```

how many output rows should there be?

Distinct countries:

```text
IN
US
```

So the expected group count is:

```text
2
```

### Run

```python
revenue_by_country = (
    orders.groupby("country")["amount"]
    .sum()
)

print(revenue_by_country)
```

Expected values:

```text
country
IN    440.0
US    360.0
```

### Explain

The source has 6 rows, but the result has 2 rows.

That is not a bug.

It is the intended grain change:

```text
source grain:
one row per order

result grain:
one row per country
```

This distinction is central to Data Engineering.

---

# 4. One Grouping Key

## 4.1 Grouping by one DataFrame column

Basic syntax:

```python
grouped = df.groupby("country")
```

You can then choose what to calculate:

```python
df.groupby("country")["amount"].sum()
```

or:

```python
df.groupby("country")["amount"].mean()
```

The grouping key controls **which rows belong together**.

The selected column controls **what values are operated on**.

## 4.2 Grouping a Series by another key

A Series can also be grouped by a same-length key:

```python
amount_by_country = orders["amount"].groupby(orders["country"]).sum()
print(amount_by_country)
```

The important semantic idea is:

> The values being calculated and the values used as grouping keys are separate inputs.

## 4.3 Predicting output size

For a simple aggregation:

```python
result = orders.groupby("customer_id")["amount"].sum()
```

look at:

```text
C1
C2
C3
```

There are three retained groups, so the grouped result should contain three rows.

### Rule

For a normal aggregation:

```text
input rows ≠ output rows

output rows ≈ number of retained distinct key values
```

The word **retained** matters because:

- null keys may be dropped by default;
- categorical keys can have observed/unobserved category behavior;
- additional grouping options affect the result.

---

# 5. Multiple Grouping Keys

Grouping by several columns creates a group for a **combination** of key values.

```python
orders.groupby(["country", "status"])["amount"].sum()
```

Conceptually the groups are:

```text
(IN, paid)
(US, paid)
(US, cancelled)
```

There are three actual combinations in the data.

The output is therefore at the grain:

```text
country + status
```

not simply:

```text
country
```

## 5.1 Star-schema thinking

This maps naturally to dimensional analysis.

For example:

```text
Gold fact-like grain:
one row per country + status
```

or:

```text
country + product
```

or:

```text
customer + month
```

When choosing grouping keys, ask:

> What is the grain of the output table?

## 5.2 Prediction-first exercise

Given:

```python
df = pd.DataFrame(
    {
        "country": ["IN", "IN", "US", "US", "US"],
        "status": ["paid", "cancelled", "paid", "paid", "cancelled"],
        "amount": [10, 20, 30, 40, 50],
    }
)
```

Predict the result of:

```python
df.groupby(["country", "status"])["amount"].sum()
```

Distinct combinations:

```text
IN + paid
IN + cancelled
US + paid
US + cancelled
```

Expected group count:

```text
4
```

Now ask:

> Would `2 countries × 2 statuses = 4` always be a safe rule?

No.

It happens to be true for this data because all combinations exist.

If `(US, cancelled)` did not occur, the number of observed groups would be 3.

With categorical groupers, `observed=False` can additionally represent unobserved category combinations. In current pandas 3.x, `observed=True` is the default, but making the option explicit in production code can improve semantic readability. See the grouping-options section later.

---

# 6. Core Aggregations

A grouped aggregation asks:

> Give me one or more summary values per group.

The roadmap requires:

```text
sum
mean
count
size
nunique
min
max
first
last
```

## 6.1 Aggregation reference

| Operation | Meaning | Missing-value behavior | Typical Data Engineering use |
|---|---|---|---|
| `sum` | Add values | Missing values are generally skipped; all-missing groups can require `min_count=1` when zero is not semantically valid | Revenue, quantity, balances |
| `mean` | Arithmetic average | Missing values are skipped | Average order value, average latency |
| `count` | Number of non-null values in the selected column | Null selected values are not counted | Count rows with a populated field |
| `size` | Number of rows in each group | Counts rows even when selected values are null | Event/order row counts |
| `nunique` | Number of distinct values | Drops null by default unless `dropna=False` | Unique products, devices, sessions |
| `min` | Minimum value | Missing values are skipped | Earliest numeric/date value |
| `max` | Maximum value | Missing values are skipped | Latest numeric/date value |
| `first` | First valid value encountered in group order by default | Current pandas default skips NA values for `first` | First observed non-null attribute in row order |
| `last` | Last valid value encountered in group order by default | Current pandas default skips NA values for `last` | Last observed non-null attribute in row order |

### Important distinction

```text
first ≠ min
last  ≠ max
```

`min` and `max` compare values.

`first` and `last` are order-sensitive.

---

# 7. `sum`

## What

Calculate the total of a numeric value within each group.

## Why

Gold metrics frequently contain sums:

```text
revenue by customer
sales by country
units by product
```

## Syntax

```python
df.groupby("country")["amount"].sum()
```

## Example

```python
revenue = (
    orders.groupby("customer_id")["amount"]
    .sum()
)

print(revenue)
```

Expected:

```text
customer_id
C1    350.0
C2    360.0
C3     90.0
```

## A subtle production point: all-null groups

Suppose a numeric column is entirely missing for a group.

```python
df = pd.DataFrame(
    {
        "customer_id": ["C1", "C1", "C2"],
        "amount": [10.0, None, None],
    }
)
```

A plain `sum()` can treat an all-missing group differently from the business meaning "no known amount."

When the distinction matters, use an explicit `min_count`:

```python
result = (
    df.groupby("customer_id")["amount"]
    .sum(min_count=1)
)
```

Now an all-null amount group can remain missing instead of being silently interpreted as zero.

### Production rule

> Decide whether "no observed value" means zero or missing before choosing aggregation semantics.

---

# 8. `mean`

## What

Calculate the arithmetic mean per group.

```python
df.groupby("country")["amount"].mean()
```

## Example

```python
avg_order = (
    orders.groupby("country")["amount"]
    .mean()
)

print(avg_order)
```

Expected:

```text
country
IN    146.666666...
US    120.0
```

because:

```text
IN = (100 + 250 + 90) / 3
US = (80 + 120 + 160) / 3
```

## Common mistake

Do not assume that:

```text
mean of group means
```

is equal to:

```text
mean of all underlying rows
```

when group sizes differ.

This matters later when processing data in chunks or combining pre-aggregated datasets.

The correct mental model is:

```text
mean = sum(values) / count(non-null values)
```

unless your business definition says something different.

---

# 9. `count`

## What

`count` counts **non-null values in the selected column**.

```python
df.groupby("customer_id")["amount"].count()
```

If a group has five rows but two amounts are missing:

```text
count("amount") = 3
```

## Example

```python
df = pd.DataFrame(
    {
        "customer_id": ["C1", "C1", "C1", "C2"],
        "order_id": ["O1", "O2", "O3", "O4"],
        "amount": [100.0, None, 50.0, None],
    }
)

result = (
    df.groupby("customer_id")["amount"]
    .count()
)

print(result)
```

Expected:

```text
customer_id
C1    2
C2    0
```

The rows exist. The `amount` values do not all exist.

### Data Engineering use case

Use `count` when your metric truly means:

> How many non-null observations are present in this column?

---

# 10. `size`

## What

`size` counts **rows in each group**.

```python
df.groupby("customer_id").size()
```

It does not require a selected column to be non-null.

Using the same data:

```python
result = (
    df.groupby("customer_id")
    .size()
)

print(result)
```

Expected:

```text
customer_id
C1    3
C2    1
```

## Why this matters

Suppose every row represents an order.

Then:

```text
size = number of order rows
```

while:

```text
count("amount") = number of orders with a non-null amount
```

Those are different business metrics.

---

# 11. `count` vs `size`: Deep Dive

This distinction is important enough to memorize.

> **count vs size:** `count` counts non-null values in the selected column; `size` counts rows in the group.

### `count`

```python
df.groupby("customer_id")["amount"].count()
```

means:

```text
How many non-null amount values are inside each customer group?
```

### `size`

```python
df.groupby("customer_id").size()
```

means:

```text
How many rows are inside each customer group?
```

## Prediction-first exercise

Given:

```python
df = pd.DataFrame(
    {
        "customer_id": ["C1", "C1", "C1", "C2", "C2"],
        "amount": [100, None, 50, None, 200],
    }
)
```

Predict:

```python
count_result = df.groupby("customer_id")["amount"].count()
size_result = df.groupby("customer_id").size()
```

Expected:

```text
count:
C1    2
C2    1

size:
C1    3
C2    2
```

### Why the difference matters in a pipeline

Imagine this schema:

```text
one row = one order
amount = nullable monetary value
```

Then:

```text
size → order rows
count(amount) → orders with known amount
```

Using `count()` when you mean rows can undercount activity.

Using `size()` when you mean populated monetary observations can overstate financial completeness.

### Simple rule

> `count` asks "how many values are present?"  
> `size` asks "how many rows exist?"

---

# 12. `nunique`

## What

`nunique` counts **distinct** values.

```python
df.groupby("customer_id")["product_id"].nunique()
```

## Example

```python
df = pd.DataFrame(
    {
        "customer_id": ["C1", "C1", "C1", "C2"],
        "product_id": ["P1", "P1", "P2", "P1"],
    }
)

distinct_products = (
    df.groupby("customer_id")["product_id"]
    .nunique()
)

print(distinct_products)
```

Expected:

```text
customer_id
C1    2
C2    1
```

## `nunique` vs `count`

For C1:

```text
product values: P1, P1, P2

count   = 3
nunique = 2
```

So:

```text
count   → number of non-null observations
nunique → number of distinct non-null observations
```

## Missing values

By default, `nunique()` excludes missing values.

If the business definition requires missing to be treated as a distinct state, use:

```python
df.groupby("customer_id")["product_id"].nunique(dropna=False)
```

Do not make that choice implicitly.

---

# 13. `min` and `max`

These compare values within the group.

```python
df.groupby("customer_id")["amount"].min()
df.groupby("customer_id")["amount"].max()
```

For timestamps:

```python
df.groupby("customer_id")["order_date"].min()
df.groupby("customer_id")["order_date"].max()
```

This is a common pattern for Gold customer metrics.

## Important semantic distinction

For dates:

```python
min(order_date)
```

means:

> earliest date value

while:

```python
first(order_date)
```

means:

> first valid `order_date` encountered according to the current row order.

They often match **only when the data is already ordered chronologically and missing-value behavior is understood**.

---

# 14. `first` vs `last`

This section is intentionally careful because `first` and `last` are easy to misuse.

## 14.1 Order-sensitive mental model

Suppose:

```text
customer C1 rows arrive as:

2026-02-10
2026-01-03
2026-03-20
```

Then:

```python
df.groupby("customer_id")["order_date"].first()
```

does not mean:

```text
2026-01-03
```

just because that is the minimum date.

It follows group row order.

Similarly:

```python
df.groupby("customer_id")["order_date"].last()
```

follows the last valid value in group order.

## 14.2 Demonstration

```python
df = pd.DataFrame(
    {
        "customer_id": ["C1", "C1", "C1"],
        "order_date": pd.to_datetime(
            ["2026-02-10", "2026-01-03", "2026-03-20"]
        ),
    }
)

print(df.groupby("customer_id")["order_date"].first())
print(df.groupby("customer_id")["order_date"].last())
print(df.groupby("customer_id")["order_date"].min())
print(df.groupby("customer_id")["order_date"].max())
```

Conceptually:

```text
first = 2026-02-10
last  = 2026-03-20
min   = 2026-01-03
max   = 2026-03-20
```

This is the key lesson:

```text
row order
    ↓
first / last

value ordering
    ↓
min / max
```

## 14.3 Production rule

If the business requirement is:

> "earliest order date"

prefer:

```python
("order_date", "min")
```

If the requirement is:

> "first observed value after sorting by a business-defined sequence"

then make the ordering explicit first and use an order-sensitive operation.

Do not rely on accidental input ordering.

### Null values

Current pandas `GroupBy.first()` and `GroupBy.last()` default to skipping missing values. Therefore, "first row" and "first valid value" are not always the same requirement.

When the literal first row is required, consider whether a position-based operation such as `nth(0)` better expresses the business rule. Keep the distinction explicit.

---

# 15. Named Aggregation

Named aggregation is one of the most important production patterns in this chapter.

## What

You provide:

```text
output column name
    = (source column, aggregation function)
```

Example:

```python
df.groupby("customer_id").agg(
    total=("amount", "sum"),
    orders=("order_id", "nunique"),
)
```

## Why

You get readable output columns immediately.

Example:

```python
customer_metrics = (
    orders.groupby("customer_id", as_index=False)
    .agg(
        total_revenue=("amount", "sum"),
        order_count=("order_id", "nunique"),
        distinct_products=("product_id", "nunique"),
    )
)
```

Expected schema:

```text
customer_id
total_revenue
order_count
distinct_products
```

This is much easier for:

- downstream SQL writes
- Parquet/CSV exports
- schema contracts
- tests
- dashboards
- code review

than ambiguous generated names.

## 15.1 The three pieces

For:

```python
total_revenue=("amount", "sum")
```

read it as:

```text
output name: total_revenue
source:      amount
operation:   sum
```

For:

```python
orders=("order_id", "nunique")
```

read it as:

```text
output name: orders
source:      order_id
operation:   distinct count
```

## 15.2 Multiple columns

```python
customer_metrics = orders.groupby(
    "customer_id",
    as_index=False,
).agg(
    total_revenue=("amount", "sum"),
    average_order=("amount", "mean"),
    order_count=("order_id", "nunique"),
    first_order_date=("order_date", "min"),
    last_order_date=("order_date", "max"),
)
```

This is a clean Gold-table design.

---

# 16. Named Aggregation vs Dictionary/List Aggregation

You can also request several functions for each input column:

```python
result = orders.groupby("customer_id").agg(
    {
        "amount": ["sum", "mean"],
        "order_id": ["count", "nunique"],
    }
)

print(result)
```

The result has MultiIndex columns conceptually like:

```text
amount              order_id
------              --------
sum       mean      count     nunique
```

That can be useful during exploration, but the resulting column structure is more awkward for downstream consumers.

## Compare

### Explicit flat schema

```python
result = orders.groupby("customer_id").agg(
    total_revenue=("amount", "sum"),
    average_order=("amount", "mean"),
    order_count=("order_id", "nunique"),
)
```

### MultiIndex columns

```python
result = orders.groupby("customer_id").agg(
    {
        "amount": ["sum", "mean"],
        "order_id": ["count", "nunique"],
    }
)
```

### Production preference

For a defined Gold output, named aggregation is often the clearest approach because the schema is visible in the transformation itself.

That is a maintainability advantage, not a claim that dictionary aggregation is invalid.

---

# 17. `as_index=False`

By default, DataFrame groupby aggregation places grouping labels in the result index:

```python
result = (
    orders.groupby("country")["amount"]
    .sum()
)
```

Result shape:

```text
index = country
value = amount sum
```

For SQL-style flat output, use:

```python
result = (
    orders.groupby("country", as_index=False)["amount"]
    .sum()
)
```

Now `country` is a normal column.

## Compare

```python
with_index = orders.groupby("country")["amount"].sum()

without_group_index = (
    orders.groupby("country", as_index=False)["amount"]
    .sum()
)
```

Think:

```text
as_index=True
→ group labels become index labels in ordinary DataFrame aggregation

as_index=False
→ group labels remain columns
```

### Gold-table use case

When the next step is:

```text
write to Parquet
write to SQL
join as a table
publish as a dataset
```

a flat schema is often easier to consume.

`as_index=False` is effectively SQL-style grouped output for DataFrame aggregation.

### Important boundary

`as_index` does not change the conceptual number of groups.

It changes **where the grouping keys are represented**.

---

# 18. `sort=False`

By default, `groupby` sorts group keys for many grouped results.

You can request:

```python
result = (
    orders.groupby("country", sort=False, as_index=False)
    .agg(revenue=("amount", "sum"))
)
```

## What it means

The option controls ordering of **group labels in the result**.

It does not mean:

> "Sort the rows inside every group."

Pandas preserves the order of observations within each group.

## Why this matters

These are separate questions:

```text
Question 1:
How should groups appear in the output?

Question 2:
In what order should observations inside a group be processed?
```

`sort=False` addresses the first.

Sorting the DataFrame addresses the second.

### Performance

Current pandas documentation notes that turning group-key sorting off can improve performance. However:

> Do not assume a fixed percentage improvement.

The result depends on:

- data size
- number of groups
- key types
- memory pressure
- downstream operations
- pandas version
- hardware

Measure on the actual workload.

---

# 19. `dropna=False`

By default, `groupby` drops rows whose grouping keys contain missing values.

Current pandas uses:

```python
dropna=True
```

by default.

That means:

```python
df.groupby("customer_id")
```

does **not** retain an NA key as a group.

## Example

```python
df = pd.DataFrame(
    {
        "customer_id": [101, 102, None, 101],
        "amount": [10, 20, 30, 40],
    }
)

default_result = df.groupby("customer_id").size()

keep_null_result = (
    df.groupby("customer_id", dropna=False)
    .size()
)

print(default_result)
print(keep_null_result)
```

Conceptual default result:

```text
customer_id
101.0    2
102.0    1
```

With `dropna=False`:

```text
customer_id
101.0    2
102.0    1
NaN      1
```

## Why this is a production issue

Suppose every row is an event.

If null customer IDs are meaningful data-quality cases, silently dropping them can cause:

```text
source rows > grouped rows represented
```

That creates a reconciliation problem.

### Production rule

Before aggregating on a key, decide:

> Are rows with missing grouping keys supposed to be excluded or represented as an explicit unknown group?

Do not let the pandas default make the business decision for you.

---

# 20. `observed=True` for Categoricals

Categorical groupers can contain categories that are not present in the current DataFrame.

Example:

```python
df = pd.DataFrame(
    {
        "country": pd.Categorical(
            ["IN", "US", "IN"],
            categories=["IN", "US", "GB"],
        ),
        "amount": [10, 20, 30],
    }
)
```

The category list contains:

```text
IN
US
GB
```

but observed rows contain only:

```text
IN
US
```

## `observed=True`

```python
result = (
    df.groupby("country", observed=True)
    .agg(total=("amount", "sum"))
)
```

Only observed categories appear.

## `observed=False`

```python
result = (
    df.groupby("country", observed=False)
    .agg(total=("amount", "sum"))
)
```

Unobserved categories can be represented as groups as well.

### Current pandas note

In pandas 3.0, `observed=True` is the default for categorical groupers.

Even so, understanding the option matters because:

- old code may specify `observed=False`;
- multi-key categorical groupings can make unused combinations important;
- production code should make intended semantics obvious.

### Why this matters

An output can have more rows than you predicted if you misunderstand category expansion.

### Production rule

> Predict observed combinations first. Then inspect categorical metadata and `observed` semantics before trusting output row counts.

---

# 21. Grouped Output Row-Count Reasoning

This is one of the highest-value habits in the chapter.

For:

```python
df.groupby(["country", "status"])
```

do not execute immediately.

First write:

```text
Countries:
IN
US

Statuses:
paid
cancelled

Observed combinations:
(IN, paid)
(IN, cancelled)
(US, paid)
```

Predicted groups:

```text
3
```

Then run the aggregation and assert.

## Exercise A

```python
df = pd.DataFrame(
    {
        "country": ["IN", "IN", "US", "US", "IN"],
        "status": ["paid", "paid", "paid", "cancelled", "cancelled"],
        "amount": [10, 20, 30, 40, 50],
    }
)
```

Predict:

```python
result = df.groupby(["country", "status"]).size()
```

Answer:

```text
(IN, paid)
(US, paid)
(US, cancelled)
(IN, cancelled)

→ 4 groups
```

## Exercise B: missing key

```python
df = pd.DataFrame(
    {
        "country": ["IN", "IN", None, "US"],
        "amount": [10, 20, 30, 40],
    }
)
```

Predict:

```python
df.groupby("country").size()
```

Default:

```text
2 retained groups
```

because the null key is dropped.

Predict:

```python
df.groupby("country", dropna=False).size()
```

Now:

```text
3 retained groups
```

## Exercise C: categorical key

```python
df = pd.DataFrame(
    {
        "country": pd.Categorical(
            ["IN", "US"],
            categories=["IN", "US", "GB"],
        ),
        "amount": [10, 20],
    }
)
```

With:

```python
observed=True
```

predict:

```text
2 groups
```

With:

```python
observed=False
```

predict:

```text
category space may include GB
```

The exact value representation is less important than understanding **why output shape changed**.

## Exercise D: every row unique

```python
df = pd.DataFrame(
    {
        "customer_id": ["C1", "C2", "C3", "C4"],
        "amount": [10, 20, 30, 40],
    }
)
```

Predict:

```python
df.groupby("customer_id")["amount"].sum()
```

Output rows:

```text
4
```

Grouping does not necessarily reduce row count.

It reduces to **one row per group**.

If every row is its own group, the number of output rows stays the same.

## Exercise E: one giant group

```python
df = pd.DataFrame(
    {
        "country": ["IN"] * 1000,
        "amount": range(1000),
    }
)
```

Predict:

```python
df.groupby("country").size()
```

Output rows:

```text
1
```

Input rows:

```text
1000
```

This is the other extreme.

---

# 22. `transform()`: Group Results Aligned to Original Rows

This is the central intermediate concept.

> `transform` returns group-based results aligned to the original observations.

For example:

```python
group_total = (
    orders.groupby("customer_id")["amount"]
    .transform("sum")
)
```

Suppose there are 6 input rows.

The transform result also has 6 values.

Each row receives the total for **its own customer**.

## Example

```python
orders = pd.DataFrame(
    {
        "order_id": ["O1", "O2", "O3", "O4"],
        "customer_id": ["C1", "C1", "C2", "C2"],
        "amount": [100, 250, 80, 120],
    }
)

orders["customer_total"] = (
    orders.groupby("customer_id")["amount"]
    .transform("sum")
)

print(orders)
```

Expected:

```text
  order_id customer_id  amount  customer_total
0       O1          C1     100             350
1       O2          C1     250             350
2       O3          C2      80             200
3       O4          C2     120             200
```

## Predict

Ask:

> How many values will `transform("sum")` return?

Answer:

```text
4
```

because:

```text
len(transform_result) == len(input)
```

That is the core contract.

---

# 23. `agg` vs `transform`

Compare:

```python
aggregated = (
    orders.groupby("customer_id")["amount"]
    .sum()
)
```

with:

```python
transformed = (
    orders.groupby("customer_id")["amount"]
    .transform("sum")
)
```

### `agg` / reduction

Conceptually:

```text
C1 → 350
C2 → 200

2 output values
```

### `transform`

Conceptually:

```text
C1 row → 350
C1 row → 350
C2 row → 200
C2 row → 200

4 output values
```

Memorization anchor:

> `agg` collapses groups.  
> `transform` broadcasts group information back to original rows.

---

# 24. Share of Group Total with `transform`

Suppose we want:

```text
order amount / customer's total revenue
```

Use:

```python
group_total = (
    orders.groupby("customer_id")["amount"]
    .transform("sum")
)

orders["revenue_share"] = (
    orders["amount"] / group_total
)
```

Example:

```python
orders = pd.DataFrame(
    {
        "customer_id": ["C1", "C1", "C2", "C2"],
        "amount": [100.0, 250.0, 80.0, 120.0],
    }
)

group_total = (
    orders.groupby("customer_id")["amount"]
    .transform("sum")
)

orders["revenue_share"] = (
    orders["amount"] / group_total
)

print(orders)
```

Expected:

```text
C1:
100 / 350 ≈ 0.285714
250 / 350 ≈ 0.714286

C2:
80 / 200 = 0.4
120 / 200 = 0.6
```

## Validate the metric

```python
share_sums = (
    orders.groupby("customer_id")["revenue_share"]
    .sum()
)

print(share_sums)
```

Expected conceptually:

```text
C1    1.0
C2    1.0
```

For floating-point calculations, use an approximate assertion:

```python
import pandas as pd

pd.testing.assert_series_equal(
    share_sums,
    pd.Series(
        [1.0, 1.0],
        index=pd.Index(["C1", "C2"], name="customer_id"),
        name="revenue_share",
    ),
    check_exact=False,
    rtol=1e-12,
    atol=1e-12,
)
```

### Semantic caution

If amounts can be negative, zero, missing, or contain adjustments/refunds, "share" may not have the intuitive 0-to-1 meaning.

The calculation is mathematically simple.

The business definition is not always.

---

# 25. `transform` for Group-Level Statistics: Z-Score

A group-wise z-score is:

```text
(x - group_mean) / group_std
```

Use aligned group statistics:

```python
group_mean = (
    df.groupby("country")["amount"]
    .transform("mean")
)

group_std = (
    df.groupby("country")["amount"]
    .transform("std")
)

df["group_zscore"] = (
    (df["amount"] - group_mean)
    / group_std
)
```

## Example

```python
df = pd.DataFrame(
    {
        "country": ["IN", "IN", "IN", "US", "US"],
        "amount": [100.0, 120.0, 140.0, 20.0, 40.0],
    }
)

mean_by_country = (
    df.groupby("country")["amount"]
    .transform("mean")
)

std_by_country = (
    df.groupby("country")["amount"]
    .transform("std")
)

df["zscore"] = (
    (df["amount"] - mean_by_country)
    / std_by_country
)

print(df)
```

## Edge cases

### One-row group

The standard deviation is not defined in the usual sample-standard-deviation calculation.

Result:

```text
NaN
```

### Zero standard deviation

If every value in a group is identical:

```text
group_std = 0
```

Division produces an invalid result for the ordinary z-score formula.

### Production pattern

Decide how to represent these cases:

```python
df["zscore"] = (
    (df["amount"] - group_mean)
    .div(group_std.where(group_std.ne(0)))
)
```

Then explicitly test:

```text
one-row group
zero-variance group
missing amount
```

Do not silently treat an undefined z-score as zero unless that is a documented business rule.

---

# 26. Filling with Group Mean

Suppose missing amounts should be filled using the **country's** average amount rather than one global average.

Use:

```python
group_mean = (
    df.groupby("country")["amount"]
    .transform("mean")
)

df["amount_filled"] = (
    df["amount"].fillna(group_mean)
)
```

Example:

```python
df = pd.DataFrame(
    {
        "country": ["IN", "IN", "US", "US"],
        "amount": [100.0, None, 80.0, 120.0],
    }
)

group_mean = (
    df.groupby("country")["amount"]
    .transform("mean")
)

df["amount_filled"] = (
    df["amount"].fillna(group_mean)
)

print(df)
```

Expected:

```text
IN mean = 100
US mean = 100
```

so the missing IN amount becomes 100.

## Why not global mean automatically?

A global mean ignores group context.

Suppose:

```text
IN average = 100
US average = 10,000
```

A missing US value filled with the global average may be wildly different from a business-appropriate group estimate.

### Production warning

Group-mean imputation is a business decision, not merely a pandas trick.

Record:

- why the value was missing;
- why group mean is appropriate;
- whether imputation is allowed for the metric;
- how many values were filled.

The cleaning-policy details belong to Topic 05; here the important lesson is how `transform` provides the group-specific value.

---

# 27. `filter()`: Keep or Remove Whole Groups

`filter` answers:

> Which entire groups should remain?

Example:

```python
large_customers = (
    orders.groupby("customer_id")
    .filter(lambda g: len(g) >= 3)
)
```

The predicate is evaluated **per group**.

If C1 has 5 rows, all five remain.

If C2 has 2 rows, all two are removed.

This is not ordinary row-wise filtering.

---

# 28. `filter` vs Row Filtering

Imagine:

```python
customer_counts = (
    orders.groupby("customer_id")
    .size()
)
```

A row-level expression such as:

```python
orders[orders["amount"] > 100]
```

asks:

> Which individual rows have amount > 100?

A group filter:

```python
orders.groupby("customer_id").filter(
    lambda g: len(g) >= 3
)
```

asks:

> Which customers have groups containing at least 3 rows?

Every row from a surviving customer is retained.

## Roadmap example

Customers with at least 3 orders:

```python
customers_3_plus = (
    orders.groupby("customer_id")
    .filter(lambda g: len(g) >= 3)
)
```

### Prediction-first question

Suppose:

```text
C1 → 4 rows
C2 → 2 rows
C3 → 5 rows
```

Predict:

```python
orders.groupby("customer_id").filter(
    lambda g: len(g) >= 3
)
```

Rows retained:

```text
C1 → all 4
C2 → none
C3 → all 5
```

Total:

```text
9 rows
```

The filter operates on groups, not individual rows.

---

# 29. Group-wise Ranking with `rank`

Ranking answers:

> What is the position of this row relative to other rows in the same group?

Example:

```python
df["country_rank"] = (
    df.groupby("country")["revenue"]
    .rank(method="dense", ascending=False)
)
```

If:

```text
country = IN
revenue = 500
revenue = 300
revenue = 100
```

then descending ranks are:

```text
1
2
3
```

## Ties

Ranking requires a tie policy.

Common methods include:

```text
average
min
max
first
dense
```

For production metrics, choose intentionally.

Example with `method="first"`:

```python
df["rank"] = (
    df.groupby("country")["revenue"]
    .rank(method="first", ascending=False)
)
```

This assigns unique sequential ranks within each group using row order to break ties.

### Determinism warning

If tie-breaking matters, make the ordering explicit before ranking.

Do not depend on arbitrary input order.

---

# 30. SQL `RANK()` Conceptual Translation

SQL:

```sql
RANK() OVER (
    PARTITION BY country
    ORDER BY revenue DESC
)
```

Conceptually maps to:

```python
df["rank"] = (
    df.groupby("country")["revenue"]
    .rank(method="min", ascending=False)
)
```

This is a conceptual translation.

The exact behavior of ties depends on the chosen pandas ranking method.

The SQL and pandas versions should be compared by their **semantics**, not by assuming one-to-one syntax.

---

# 31. `cumcount()`

`cumcount()` numbers rows within each group.

Example:

```python
df["order_number"] = (
    df.groupby("customer_id")
    .cumcount()
    + 1
)
```

If C1 has three order rows:

```text
C1 → 1
C1 → 2
C1 → 3
```

## Why it is useful

This supports:

- first order
- second order
- nth event
- sequence IDs
- session/event ordering
- "repeat purchase number"

## Order matters

`cumcount()` follows the current row order.

If business sequence means chronological order, sort first.

---

# 32. `cumsum()`: Running Totals

Use:

```python
df["running_revenue"] = (
    df.groupby("customer_id")["amount"]
    .cumsum()
)
```

Example:

```python
df = pd.DataFrame(
    {
        "customer_id": ["C1", "C1", "C1", "C2", "C2"],
        "order_date": pd.to_datetime(
            [
                "2026-01-03",
                "2026-01-01",
                "2026-01-04",
                "2026-01-02",
                "2026-01-05",
            ]
        ),
        "amount": [100, 50, 200, 80, 40],
    }
)

df["running_revenue_current_order"] = (
    df.groupby("customer_id")["amount"]
    .cumsum()
)
```

This running total follows **input row order**.

It is not automatically chronological.

## Correct chronological pattern

```python
ordered = (
    df.sort_values(
        ["customer_id", "order_date"],
        kind="stable",
    )
    .copy()
)

ordered["running_revenue"] = (
    ordered.groupby("customer_id")["amount"]
    .cumsum()
)
```

### Production rule

> Window-style grouped calculations are only as meaningful as the ordering that defines them.

---

# 33. `shift()`

`shift()` gives a previous or next value within each group.

Previous value:

```python
df["previous_amount"] = (
    df.groupby("customer_id")["amount"]
    .shift(1)
)
```

## Example

For:

```text
C1: 100, 250, 300
C2: 80, 40
```

you get:

```text
C1: NaN, 100, 250
C2: NaN, 80
```

The first row in every group has no previous value.

That is why the first `shift(1)` result is missing.

## Business use

- previous order amount
- previous account balance
- previous sensor reading
- previous event
- prior customer state

### Ordering requirement

If "previous" means previous chronologically, sort by:

```python
["customer_id", "order_date"]
```

before calling `shift()`.

---

# 34. `diff()`

`diff()` subtracts the previous value within each group.

Numeric difference:

```python
df["amount_change"] = (
    df.groupby("customer_id")["amount"]
    .diff()
)
```

For dates:

```python
df["days_since_previous_order"] = (
    df.groupby("customer_id")["order_date"]
    .diff()
    .dt.days
)
```

## Example

```python
df = pd.DataFrame(
    {
        "customer_id": ["C1", "C1", "C1", "C2"],
        "order_date": pd.to_datetime(
            ["2026-01-03", "2026-01-10", "2026-01-12", "2026-01-05"]
        ),
        "amount": [100.0, 150.0, 120.0, 90.0],
    }
)

df["days_since_previous_order"] = (
    df.groupby("customer_id")["order_date"]
    .diff()
    .dt.days
)

df["amount_change"] = (
    df.groupby("customer_id")["amount"]
    .diff()
)
```

Expected conceptual results:

```text
C1:
first row → NaN
second row → 7 days, +50
third row  → 2 days, -30

C2:
first row → NaN
```

Again, that assumes the rows are already in the intended order.

If not, sort first.

---

# 35. `shift` vs `diff`

These are related but different:

```text
shift
→ return the previous value

diff
→ current value minus previous value
```

Example:

```python
previous = (
    df.groupby("customer_id")["amount"]
    .shift()
)

change = (
    df.groupby("customer_id")["amount"]
    .diff()
)
```

Conceptually:

```text
amount:    100   150   120

shift:     NaN   100   150

diff:      NaN    50   -30
```

---

# 36. `nlargest()` Per Group

There is a major difference between:

```text
global top 3
```

and:

```text
top 3 inside every group
```

For example:

> Top 3 products by revenue per country.

A global:

```python
df.nlargest(3, "revenue")
```

returns only three rows in total.

That is not the requested business metric.

## Group-wise pattern

For a Series grouped by country:

```python
top_products = (
    df.groupby("country")["revenue"]
    .nlargest(3)
)
```

This produces a MultiIndex-like result containing country and the original row index.

To retrieve complete rows safely:

```python
top_index = (
    df.groupby("country")["revenue"]
    .nlargest(3)
    .reset_index()
)

top_products = (
    top_index[["country", "level_1"]]
    .rename(columns={"level_1": "row_index"})
)
```

A simpler production-friendly approach is often to compute a group-wise rank and filter:

```python
ranked = df.assign(
    revenue_rank=(
        df.groupby("country")["revenue"]
        .rank(method="first", ascending=False)
    )
)

top3 = (
    ranked.loc[ranked["revenue_rank"] <= 3]
)
```

## Ties matter

You must define what "top 3" means.

### Exactly three rows

Use a tie-breaking rule such as:

```python
method="first"
```

after a deterministic sort.

### Top three distinct revenue levels

A different ranking policy such as:

```python
method="dense"
```

can produce more than three rows when several products share a rank.

### Production rule

> Top-N is incomplete until the tie policy is defined.

---

# 37. SQL Window Functions → pandas Mental Model

Common SQL window functions:

```text
PARTITION BY
ORDER BY
ROW_NUMBER()
RANK()
SUM(...) OVER (...)
LAG(...)
```

The pandas mental model is:

```text
groupby(partition_keys)
+
an order-aware GroupBy operation
```

The concepts align, but pandas requires you to be explicit about row order and result alignment.

---

# 38. SQL Translation Table

| SQL concept | pandas pattern | Important semantic point |
|---|---|---|
| `GROUP BY` + `SUM` | `groupby(keys)["amount"].sum()` | Output collapses to groups |
| `GROUP BY` + `AVG` | `groupby(keys)["amount"].mean()` | Null observations are skipped |
| `COUNT(column)` | `groupby(keys)["column"].count()` | Counts non-null values |
| `COUNT(*)` | `groupby(keys).size()` | Counts rows |
| `COUNT(DISTINCT product_id)` | `groupby(keys)["product_id"].nunique()` | Distinct, null excluded by default |
| `RANK() OVER (PARTITION BY ...)` | `groupby(keys)["value"].rank(...)` | Tie method must be chosen |
| `ROW_NUMBER() OVER (...)` | `groupby(keys).cumcount() + 1` | Requires correct row ordering |
| `SUM(...) OVER (PARTITION BY ... ORDER BY ...)` | `groupby(keys)["value"].cumsum()` | Sort before cumulative calculation |
| `LAG(value) OVER (...)` | `groupby(keys)["value"].shift()` | First row in each group is missing |
| Previous-to-current difference | `groupby(keys)["value"].diff()` | Sort according to business sequence |

---

# 39. SQL Translation Practice — 11 Realistic Examples

For every aggregation below, practice the question:

> **How many output rows should this produce?**

Do not execute until you predict.

---

## 39.1 SQL Example 1 — Revenue by country

### SQL

```sql
SELECT
    country,
    SUM(amount) AS revenue
FROM orders
GROUP BY country;
```

### Pandas

```python
result = (
    orders.groupby("country", as_index=False)
    .agg(revenue=("amount", "sum"))
)
```

### Output shape

One row per retained country.

### Important semantic difference

If country is null, pandas drops the null-key group by default. Use:

```python
dropna=False
```

when null should be a retained group.

---

## 39.2 SQL Example 2 — Average order value by country

### SQL

```sql
SELECT
    country,
    AVG(amount) AS average_order_value
FROM orders
GROUP BY country;
```

### Pandas

```python
result = (
    orders.groupby("country", as_index=False)
    .agg(average_order_value=("amount", "mean"))
)
```

### Output shape

One row per retained country.

### Important semantic difference

Both SQL engines and pandas have nuanced null semantics. Confirm the source schema and business definition before assuming averages include missing values.

---

## 39.3 SQL Example 3 — `COUNT(*)`

### SQL

```sql
SELECT
    customer_id,
    COUNT(*) AS order_rows
FROM orders
GROUP BY customer_id;
```

### Pandas

```python
result = (
    orders.groupby("customer_id", as_index=False)
    .size()
    .rename(columns={"size": "order_rows"})
)
```

### Output shape

One row per retained customer.

### Important semantic difference

`COUNT(*)` corresponds conceptually to group row count, which is why `size()` is the relevant pandas operation.

---

## 39.4 SQL Example 4 — `COUNT(amount)`

### SQL

```sql
SELECT
    customer_id,
    COUNT(amount) AS known_amount_rows
FROM orders
GROUP BY customer_id;
```

### Pandas

```python
result = (
    orders.groupby("customer_id", as_index=False)
    .agg(known_amount_rows=("amount", "count"))
)
```

### Output shape

One row per retained customer.

### Important semantic difference

Null amount values are excluded.

---

## 39.5 SQL Example 5 — `COUNT(DISTINCT product_id)`

### SQL

```sql
SELECT
    customer_id,
    COUNT(DISTINCT product_id) AS distinct_products
FROM orders
GROUP BY customer_id;
```

### Pandas

```python
result = (
    orders.groupby("customer_id", as_index=False)
    .agg(distinct_products=("product_id", "nunique"))
)
```

### Output shape

One row per retained customer.

### Important semantic difference

Pandas `nunique()` drops missing by default. Make `dropna=False` explicit if the business metric treats missing as a distinct state.

---

## 39.6 SQL Example 6 — Multiple grouping keys

### SQL

```sql
SELECT
    country,
    status,
    SUM(amount) AS revenue
FROM orders
GROUP BY country, status;
```

### Pandas

```python
result = (
    orders.groupby(
        ["country", "status"],
        as_index=False,
    )
    .agg(revenue=("amount", "sum"))
)
```

### Output shape

One row per retained `(country, status)` combination.

### Prediction question

Count the actual combinations in the source data. Do not multiply the number of unique countries by the number of unique statuses unless every combination is observed and no categorical expansion changes the grouping space.

---

## 39.7 SQL Example 7 — Grouping while retaining null keys

### SQL

Null grouping semantics differ across SQL engines and should be checked for the specific engine.

### Pandas

```python
result = (
    orders.groupby(
        "customer_id",
        dropna=False,
        as_index=False,
    )
    .agg(
        revenue=("amount", "sum"),
        rows=("order_id", "size"),
    )
)
```

### Output shape

One row per retained customer key, including the null-key group.

### Important semantic difference

Do not assume SQL and pandas have identical null-key behavior.

This is a semantic area to validate explicitly.

---

## 39.8 SQL Example 8 — Rank within country

### SQL

```sql
SELECT
    country,
    product_id,
    revenue,
    RANK() OVER (
        PARTITION BY country
        ORDER BY revenue DESC
    ) AS revenue_rank
FROM country_product_revenue;
```

### Pandas

```python
result = country_product_revenue.copy()

result["revenue_rank"] = (
    result.groupby("country")["revenue"]
    .rank(method="min", ascending=False)
)
```

### Output shape

Same number of rows as the input.

### Important semantic difference

This is a window-style operation. It does **not** collapse to one row per group.

Tie behavior must match the intended rank method.

---

## 39.9 SQL Example 9 — Running total

### SQL

```sql
SELECT
    customer_id,
    order_date,
    amount,
    SUM(amount) OVER (
        PARTITION BY customer_id
        ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_revenue
FROM orders;
```

### Pandas

```python
ordered = (
    orders.sort_values(
        ["customer_id", "order_date"],
        kind="stable",
    )
    .copy()
)

ordered["running_revenue"] = (
    ordered.groupby("customer_id")["amount"]
    .cumsum()
)
```

### Output shape

Same number of rows as input.

### Important semantic difference

The pandas result depends on the DataFrame's ordering. SQL explicitly encodes the window ordering.

Therefore, sort the DataFrame when chronological or business ordering is required.

---

## 39.10 SQL Example 10 — Row number

### SQL

```sql
SELECT
    customer_id,
    order_date,
    ROW_NUMBER() OVER (
        PARTITION BY customer_id
        ORDER BY order_date, order_id
    ) AS order_number
FROM orders;
```

### Pandas

```python
ordered = (
    orders.sort_values(
        ["customer_id", "order_date", "order_id"],
        kind="stable",
    )
    .copy()
)

ordered["order_number"] = (
    ordered.groupby("customer_id")
    .cumcount()
    + 1
)
```

### Output shape

Same number of rows as input.

### Important semantic difference

The secondary `order_id` key makes duplicate timestamps deterministic.

---

## 39.11 SQL Example 11 — Previous event value

### SQL

```sql
SELECT
    customer_id,
    order_date,
    amount,
    LAG(amount) OVER (
        PARTITION BY customer_id
        ORDER BY order_date, order_id
    ) AS previous_amount
FROM orders;
```

### Pandas

```python
ordered = (
    orders.sort_values(
        ["customer_id", "order_date", "order_id"],
        kind="stable",
    )
    .copy()
)

ordered["previous_amount"] = (
    ordered.groupby("customer_id")["amount"]
    .shift()
)
```

### Output shape

Same number of rows as input.

### Important semantic difference

The first row in every customer partition has no previous value, so the result is missing there.

---

# 40. `agg` vs `transform` vs `filter` vs `apply`

Memorize this table.

| Method | Output shape | Main purpose | Example |
|---|---|---|---|
| `agg` | Usually one result per group/summary column | Produce group summaries | Revenue per customer |
| `transform` | Same row count as the original selected object | Broadcast a group-based result back to original rows | Customer total on every order |
| `filter` | Subset of original rows | Keep/remove complete groups | Keep customers with ≥ 3 orders |
| `apply` | Depends on function result | Arbitrary custom Python logic per group | Specialized group-specific computation |

### One-sentence anchors

**`agg`**

> Give me one or more summary values per group.

**`transform`**

> Give me one result per original row based on its group.

**`filter`**

> Keep or remove whole groups based on a group-level condition.

**`apply`**

> Run custom Python logic for each group and combine the returned results.

---

# 41. How to Choose Among `agg`, `transform`, `filter`, and `apply`

Use this decision process:

```text
Do I need summary values per group?
        |
       YES
        ↓
       agg()

Do I need a group-derived value aligned to every original row?
        |
       YES
        ↓
    transform()

Do I want to keep/remove whole groups?
        |
       YES
        ↓
     filter()

Do I need arbitrary custom logic per group?
        |
       YES
        ↓
      apply()
```

Before `apply`, ask:

```text
Can agg solve it?
        ↓
Can transform solve it?
        ↓
Can vectorized pandas/NumPy solve it?
        ↓
Only then consider apply.
```

This is an engineering heuristic, not an absolute law.

---

# 42. `apply()`

`apply` is deliberately introduced late because it is powerful enough to hide poor design.

Conceptually:

```python
grouped.apply(function)
```

means:

```text
split into groups
→ call your function for each group
→ combine returned DataFrame/Series/scalars
```

The function can return:

- a scalar
- a Series
- a DataFrame

That flexibility is the main reason `apply` exists.

## Simple example

```python
def revenue_range(group):
    return group["amount"].max() - group["amount"].min()

result = (
    orders.groupby("customer_id")
    .apply(revenue_range)
)

print(result)
```

The output is one scalar per customer.

But this specific calculation can often be expressed more directly using grouped aggregation.

---

# 43. Why `apply()` Can Be Slow

The central reason is:

> **Python call per group:** a Python function may be called once for each group.

Suppose a DataFrame has:

```text
5,000,000 rows
100,000 customer groups
```

A custom `apply` can mean roughly:

```text
100,000 Python-level function calls
```

plus:

- group materialization/iteration overhead
- Python interpreter overhead
- object creation
- result combination
- less opportunity to use specialized optimized pandas paths

By contrast:

```python
orders.groupby("customer_id")["amount"].sum()
```

uses a specialized built-in grouped reduction.

Current pandas documentation explicitly recommends trying more specific methods such as `agg` or `transform` before `apply` when they express the same operation. citeturn245631search0turn245631search1

### Important qualification

`apply` is not "bad."

The correct statement is:

> `apply` is highly flexible, but can be significantly slower than specific grouped operations when a built-in or vectorized operation expresses the same semantics.

---

# 44. When `apply()` Is Justified

`apply` can be reasonable when the logic is genuinely custom.

Examples:

- complicated group-specific business rules;
- a custom output shape that is awkward to express otherwise;
- a specialized computation not available as a grouped reducer or transform;
- logic whose clarity would be materially worse if forced into a chain of low-level operations.

Example:

```python
def customer_risk_summary(group):
    total = group["amount"].sum()
    suspicious = (group["amount"] > 10_000).sum()

    return pd.Series(
        {
            "total": total,
            "suspicious_ratio": (
                suspicious / len(group)
                if len(group)
                else float("nan")
            ),
        }
    )

result = (
    orders.groupby("customer_id")
    .apply(customer_risk_summary)
)
```

This is more specialized than a simple `sum`.

Still, the function should be:

- small;
- deterministic;
- tested independently;
- explicit about null and ordering semantics;
- benchmarked on realistic data.

---

# 45. Replacing `apply()`

Before:

```python
def total_revenue(group):
    return group["amount"].sum()

slow_result = (
    orders.groupby("customer_id")
    .apply(total_revenue)
)
```

After:

```python
fast_result = (
    orders.groupby("customer_id")["amount"]
    .sum()
)
```

Why is the second preferable?

```text
same business metric
+
clearer intent
+
specialized grouped reduction
+
less Python-level function dispatch
```

## Another replacement: group mean

### Custom apply

```python
slow_mean = (
    orders.groupby("country")["amount"]
    .apply(lambda s: s.mean())
)
```

### Specific operation

```python
fast_mean = (
    orders.groupby("country")["amount"]
    .mean()
)
```

## Another replacement: group total broadcast

### Awkward custom logic

```python
orders["customer_total"] = (
    orders.groupby("customer_id")["amount"]
    .apply(lambda s: s.sum())
)
```

That does not express the required row-aligned semantics.

### Correct transform

```python
orders["customer_total"] = (
    orders.groupby("customer_id")["amount"]
    .transform("sum")
)
```

The lesson is not "never apply."

The lesson is:

> Choose the operation whose output contract matches the problem.

---

# 46. Custom Aggregation Functions

Sometimes a useful metric is not a built-in reducer.

Example:

```python
def spread(values):
    return values.max() - values.min()
```

Use it with aggregation:

```python
result = (
    orders.groupby("customer_id")
    .agg(
        amount_spread=("amount", spread),
    )
)
```

## Why this can be useful

A named custom function can make a domain metric readable.

For example:

```text
exposure_range
response_time_spread
balance_range
price_dispersion
```

## Cost

A custom Python function may be slower than an existing built-in operation.

In this example, the same metric can be written as:

```python
result = (
    orders.groupby("customer_id")
    .agg(
        amount_spread=("amount", "max")
    )
)
```

That is not the same calculation, of course.

The actual equivalent is:

```python
result = (
    orders.groupby("customer_id")
    .agg(
        amount_max=("amount", "max"),
        amount_min=("amount", "min"),
    )
)

result["amount_spread"] = (
    result["amount_max"] - result["amount_min"]
)
```

The second version exposes more intermediate values but may use built-in grouped reducers.

### Production decision

Choose between:

```text
custom function
vs
built-in operations + vectorized combination
```

based on:

- correctness;
- readability;
- data volume;
- number of groups;
- benchmark results;
- maintenance cost.

---

# 47. Multiple Aggregations Across Many Columns

A realistic Gold metric table often needs several metrics:

```python
customer_metrics = (
    orders.groupby(
        "customer_id",
        as_index=False,
    )
    .agg(
        total_revenue=("amount", "sum"),
        average_order=("amount", "mean"),
        order_count=("order_id", "nunique"),
        distinct_products=("product_id", "nunique"),
        min_amount=("amount", "min"),
        max_amount=("amount", "max"),
        first_order_date=("order_date", "min"),
        last_order_date=("order_date", "max"),
    )
)
```

This is usually easier to review than dynamically generating a huge aggregation structure.

## Design principle

Treat the aggregation result as a **data product**.

Define:

```text
grain
schema
metric definitions
null semantics
reconciliation rules
```

For example:

```text
grain:
one row per customer

columns:
customer_id
total_revenue
average_order
order_count
distinct_products
first_order_date
last_order_date
```

A Gold dataset should not be "whatever pandas happened to return."

---

# 48. `pd.Grouper()`: Grouping by Time

The roadmap requires the time-grouping bridge:

```python
pd.Grouper(key="created_at", freq="D")
```

This lets a grouping operation use time frequency boundaries.

Example:

```python
daily_revenue = (
    orders.groupby(
        pd.Grouper(key="created_at", freq="D")
    )["amount"]
    .sum()
)
```

The mental model is:

```text
created_at timestamp
       ↓
assign each row to a daily bin
       ↓
group by that bin
       ↓
aggregate
```

## Multiple keys

```python
daily_country_revenue = (
    orders.groupby(
        [
            "country",
            pd.Grouper(
                key="created_at",
                freq="D",
            ),
        ],
        as_index=False,
    )
    .agg(
        revenue=("amount", "sum"),
    )
)
```

Now the grain is:

```text
country + day
```

## Why this matters

Many Data Engineering Gold tables have grains such as:

```text
customer + day
country + day
product + week
region + month
```

`pd.Grouper` lets the time bucket participate directly in the group definition.

### Scope boundary

This chapter only introduces time grouping through `pd.Grouper`.

Detailed resampling, rolling windows, time-based windows, and as-of logic belong to Topic 09.

---

# 49. Performance Engineering for `groupby`

Grouped operations can become expensive at millions or tens of millions of rows.

The main cost drivers include:

```text
number of input rows
number of groups
group-key representation
number of selected columns
number of grouping operations
sort requirements
Python-level function calls
memory pressure
result width
```

There is no single universally fastest pattern.

The production rule is:

> **Measure first, optimize the actual bottleneck, and validate that semantics remain identical.**

---

# 50. Built-in Reductions First

Prefer specialized operations when they directly express the metric:

```python
df.groupby("customer_id")["amount"].sum()
```

rather than:

```python
df.groupby("customer_id")["amount"].apply(lambda s: s.sum())
```

The built-in operation has a clearer semantic contract and usually gives pandas more opportunity to use optimized internals.

Current pandas documentation makes the same practical recommendation for `apply`: specific methods such as `agg` and `transform` can be considerably faster for their intended operations. citeturn245631search1turn245631search2

---

# 51. Reduce Unnecessary Columns Before Grouping

If a DataFrame contains 80 columns and the grouping needs only:

```text
customer_id
amount
order_id
order_date
```

avoid carrying unrelated wide columns through the operation unless they are needed.

Example:

```python
needed = orders[
    [
        "customer_id",
        "amount",
        "order_id",
        "order_date",
    ]
]

customer_metrics = (
    needed.groupby("customer_id", as_index=False)
    .agg(
        total_revenue=("amount", "sum"),
        orders=("order_id", "nunique"),
        first_order=("order_date", "min"),
    )
)
```

This can reduce memory traffic and intermediate object size.

It is not a guarantee of faster execution in every workload; benchmark if the optimization matters.

---

# 52. Avoid Repeated Groupby Work

This pattern may repeat expensive grouping unnecessarily:

```python
df["customer_total"] = (
    df.groupby("customer_id")["amount"]
    .transform("sum")
)

df["customer_mean"] = (
    df.groupby("customer_id")["amount"]
    .transform("mean")
)

df["customer_max"] = (
    df.groupby("customer_id")["amount"]
    .transform("max")
)
```

Sometimes that is perfectly acceptable and very readable.

But if profiling shows grouping dominates the workload, consider whether the grouping can be consolidated or group-level metrics can be computed once and then reused.

For example, several customer metrics can be calculated together:

```python
customer_stats = (
    df.groupby("customer_id")
    .agg(
        total=("amount", "sum"),
        mean=("amount", "mean"),
        maximum=("amount", "max"),
    )
)
```

The correct optimization depends on how those statistics will be consumed.

---

# 53. Sorted Grouping Keys

Sorted group keys can matter because grouping algorithms have different work to do depending on input layout.

However:

> Sorted data is not automatically faster.

Sorting itself costs time and memory.

Compare:

```text
unsorted input
→ groupby
```

with:

```text
sort input
→ groupby
```

and ask:

```text
Does the sort benefit enough to pay for the sort?
```

If the pipeline already requires sorting for business ordering, such as:

```python
customer_id + order_date
```

then the same sort may serve both:

```text
window-style logic
+
grouped calculations
```

This is a good reuse opportunity.

### Benchmark rule

Measure:

```text
sort time
+
groupby time
```

not just:

```text
groupby time after sort
```

---

# 54. Categorical Grouping Keys

Categoricals can be useful when a grouping key is:

- low-cardinality;
- repeated heavily;
- a controlled vocabulary.

Example:

```python
orders["country"] = orders["country"].astype("category")
```

Then:

```python
country_revenue = (
    orders.groupby(
        "country",
        observed=True,
        as_index=False,
    )
    .agg(revenue=("amount", "sum"))
)
```

Potential advantages can include:

- lower memory usage;
- compact representation of repeated labels;
- different grouping behavior for category metadata.

Potential downsides:

- category management adds semantics you must understand;
- high-cardinality columns may not benefit;
- category combinations can affect grouped output;
- converting types itself has a cost.

Do not claim:

> "category is always faster."

Measure on the real workload.

---

# 55. Generic `object` Grouping Keys

Before optimizing a key, inspect it.

```python
print(df["country"].dtype)
```

Generic `object` columns can hide mixed representations and may be less efficient than intentional typed representations for large repeated-key workloads.

Examples of intentional choices may include:

```text
string dtype
category for low-cardinality repeated labels
numeric nullable integer for IDs that are numeric by meaning
```

Do not turn this into a blanket rule that all object columns must be converted.

The production process is:

```text
inspect dtype
→ understand business meaning
→ measure workload
→ choose representation
→ test semantics
```

---

# 56. Group Counts as a Data-Quality and Join-Validation Tool

Topic 07 will teach joins deeply.

This topic should teach one critical prerequisite:

> Know your key cardinality before you join.

Example:

```python
customer_counts = (
    orders.groupby("customer_id")
    .size()
)
```

Inspect:

```python
customer_counts.sort_values(ascending=False).head()
```

This can reveal:

```text
customers with many orders
unexpected duplicate-like activity
one-to-many relationships
unexpected repeated keys
```

You can also inspect whether a supposed unique key really is unique:

```python
counts = (
    dimension.groupby("customer_id")
    .size()
)

duplicate_keys = counts[counts > 1]
```

If `duplicate_keys` is non-empty, a future join expected to be many-to-one may not actually be many-to-one.

This is not join syntax.

It is **cardinality awareness before a join**.

---

# 57. Benchmarking Grouped Operations

Never fabricate timing results.

Use a real benchmark.

The simplest tool is:

```python
from time import perf_counter

start = perf_counter()

result = (
    df.groupby("customer_id")
    .agg(total=("amount", "sum"))
)

elapsed = perf_counter() - start

print(f"{elapsed:.3f} seconds")
```

For more careful micro-benchmarks, `timeit` can also be used.

## Benchmark design

Compare operations using:

1. exactly the same input data;
2. equivalent output semantics;
3. the same environment;
4. warm-up/rerun behavior where useful;
5. repeated measurements where practical;
6. realistic group cardinality;
7. realistic dtypes.

Record:

```text
rows
groups
operation
wall-clock time
peak memory if available
pandas version
Python version
machine/environment
```

### Good benchmark question

Compare:

```text
built-in groupby sum
vs
custom apply sum
```

Do not compare unrelated workloads.

---

# 58. Benchmark: 5,000,000 Rows

The roadmap exercise requires a 5,000,000-row benchmark.

Generate a reproducible test frame:

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

n = 5_000_000
n_customers = 100_000

benchmark_df = pd.DataFrame(
    {
        "customer_id": rng.integers(
            0,
            n_customers,
            size=n,
        ),
        "amount": rng.random(n) * 1000,
    }
)
```

Then benchmark an optimized grouped operation:

```python
from time import perf_counter

start = perf_counter()

optimized = (
    benchmark_df.groupby("customer_id")
    .agg(total_revenue=("amount", "sum"))
)

optimized_seconds = perf_counter() - start
```

And an equivalent custom `apply`:

```python
start = perf_counter()

custom = (
    benchmark_df.groupby("customer_id")["amount"]
    .apply(lambda values: values.sum())
)

apply_seconds = perf_counter() - start
```

Check semantic agreement before interpreting timings:

```python
optimized_series = (
    optimized["total_revenue"]
    .sort_index()
)

custom_series = (
    custom
    .sort_index()
)

pd.testing.assert_series_equal(
    optimized_series,
    custom_series,
    check_names=False,
    check_dtype=False,
)
```

Then record the actual measured values.

### Do not write

```text
apply is 17.4× slower
```

unless you actually measured it in your environment.

### Explain the gap

Your explanation should discuss:

```text
Python function call per group
+
group iteration overhead
+
result construction/combination
+
specialized optimized reducer in the built-in version
```

and then relate those costs to your measured environment.

---

# 59. Hands-on Exercise — `customer_metrics.py`

> **Do not create `customer_metrics.py` as part of this chapter task.**
>
> This section is the complete implementation specification for the learner. The actual exercise file and test file belong outside this Markdown-only deliverable.

## Business scenario

You are building a Gold-layer customer analytics dataset from an `orders` DataFrame.

Assume:

```text
one row = one order event
```

Expected columns:

```text
order_id
customer_id
country
product_id
amount
order_date
```

The exercise should be written as a production-oriented `.py` module with pytest tests when you implement it later.

---

## Task 1 — Per-customer metrics

Create one row per customer with:

- total revenue;
- order count;
- distinct products;
- first order date;
- last order date.

Use **named aggregation**.

Required conceptual pattern:

```python
customer_metrics = orders.groupby(
    "customer_id",
    as_index=False,
).agg(
    total_revenue=("amount", "sum"),
    order_count=("order_id", "nunique"),
    distinct_products=("product_id", "nunique"),
    first_order_date=("order_date", "min"),
    last_order_date=("order_date", "max"),
)
```

### Why named aggregation?

Because the Gold output has a clear schema:

```text
customer_id
total_revenue
order_count
distinct_products
first_order_date
last_order_date
```

### Tests

Verify:

```text
one row per retained customer
expected column names
expected values on a tiny hand-calculated fixture
```

---

## Task 2 — Share of customer revenue

For every order calculate:

```text
order amount / customer's total revenue
```

Use `transform`:

```python
customer_total = (
    orders.groupby("customer_id")["amount"]
    .transform("sum")
)

orders["revenue_share"] = (
    orders["amount"] / customer_total
)
```

### Why not `agg` alone?

`agg` collapses the data to one row per customer.

The task requires one result per order.

`transform` preserves row alignment.

### Validation

Where business semantics support the calculation:

```python
share_check = (
    orders.groupby("customer_id")["revenue_share"]
    .sum()
)
```

Validate that group share totals are approximately 1.

Explicitly document how zero-total and missing-amount customers are handled.

---

## Task 3 — Order sequence and days since previous order

Calculate:

- order sequence number;
- days since previous order.

First establish the correct business order:

```python
ordered = (
    orders.sort_values(
        ["customer_id", "order_date", "order_id"],
        kind="stable",
    )
    .copy()
)
```

Order sequence:

```python
ordered["order_sequence"] = (
    ordered.groupby("customer_id")
    .cumcount()
    + 1
)
```

Days since previous order:

```python
ordered["days_since_previous_order"] = (
    ordered.groupby("customer_id")["order_date"]
    .diff()
    .dt.days
)
```

### Why include `order_id` in the sort?

If two orders share the same timestamp, a deterministic secondary key prevents ambiguous sequence order.

### Tests

For every customer:

```text
first order sequence = 1
first days_since_previous_order = missing
later rows reference the previous chronological order
```

---

## Task 4 — Top 3 products by revenue per country

Compute:

> Top 3 products by revenue **within each country**.

First aggregate to:

```text
country + product_id
```

```python
product_country = (
    orders.groupby(
        ["country", "product_id"],
        as_index=False,
    )
    .agg(
        revenue=("amount", "sum"),
    )
)
```

Then rank within country:

```python
product_country = product_country.assign(
    revenue_rank=(
        product_country.groupby("country")["revenue"]
        .rank(
            method="first",
            ascending=False,
        )
    )
)
```

Then:

```python
top3 = (
    product_country.loc[
        product_country["revenue_rank"] <= 3
    ]
)
```

### Tie policy

The exercise must explicitly define how ties are handled.

For exactly three rows per country, use a deterministic tie-breaking order before ranking.

For "all products tied at the third rank," use a different ranking policy and accept more than three rows.

### Test

Create a fixture where:

```text
country A → at least 4 products
country B → fewer than 3 products
```

Verify top-N is computed independently within each country.

---

## Task 5 — Customers with at least 5 orders

Use group-level filtering:

```python
active_customers = (
    orders.groupby("customer_id")
    .filter(
        lambda group: len(group) >= 5
    )
)
```

### Required understanding

This keeps **all rows** belonging to surviving customers.

It does not keep "the five largest orders."

### Test

Fixture:

```text
C1 → 5 orders
C2 → 4 orders
C3 → 8 orders
```

Expected:

```text
C1 → all 5 rows
C2 → no rows
C3 → all 8 rows
```

---

## Task 6 — `apply` vs non-`apply`

Choose a meaningful metric that can be expressed both ways.

Recommended benchmark metric:

```text
total revenue per customer
```

### `apply` implementation

```python
apply_result = (
    orders.groupby("customer_id")["amount"]
    .apply(
        lambda values: values.sum()
    )
)
```

### Non-`apply` implementation

```python
agg_result = (
    orders.groupby("customer_id")["amount"]
    .sum()
)
```

### Semantic equivalence

Align the results before comparing:

```python
apply_result = apply_result.sort_index()
agg_result = agg_result.sort_index()

pd.testing.assert_series_equal(
    apply_result,
    agg_result,
    check_names=False,
    check_dtype=False,
)
```

### Benchmark

Use:

```text
5,000,000 rows
```

with a realistic number of groups.

Recommended starting setup:

```text
5,000,000 rows
100,000 customers
```

Do not fabricate timings.

Record the actual result:

```text
operation
row count
group count
seconds
```

Explain why the two approaches differ.

### Extension

Repeat the benchmark with:

```text
10,000 groups
100,000 groups
500,000 groups
```

and observe how the number of Python function calls can affect `apply`.

---

# 60. Prediction-First Lab Set

Do these before running code.

## Lab 1

```python
df.groupby("country").size()
```

Predict:

```text
number of retained countries
```

## Lab 2

```python
df.groupby(["country", "status"]).size()
```

Predict:

```text
number of retained key combinations
```

## Lab 3

```python
df.groupby("country")["amount"].count()
```

Predict:

```text
non-null amount count per country
```

## Lab 4

```python
df.groupby("country").size()
```

Predict:

```text
all row counts per country
```

## Lab 5

```python
df.groupby("customer_id")["product_id"].nunique()
```

Predict:

```text
distinct non-null products per customer
```

## Lab 6

```python
df.groupby("customer_id")["amount"].transform("sum")
```

Predict:

```text
same number of output rows as df
```

## Lab 7

```python
df.groupby("customer_id").cumcount()
```

Predict the first three values in every customer group.

## Lab 8

```python
df.groupby("customer_id")["amount"].shift()
```

Predict:

```text
first row per customer = missing
```

## Lab 9

```python
df.groupby("customer_id")["amount"].diff()
```

Predict the first value and subsequent differences.

## Lab 10

For top 3 per country, list which products belong to each country before executing.

Then verify the result.

---

# 61. Debugging: A Production Troubleshooting Guide

When a grouped result looks wrong, first ask:

```text
1. What is the intended grain?
2. What are the grouping keys?
3. How many groups should exist?
4. Are null keys allowed?
5. Are keys typed and standardized?
6. Does order matter?
7. Is this agg, transform, filter, or apply?
8. What is the expected output shape?
```

---

## Debug Case 1 — Grouping by the wrong column

### Buggy code

```python
df.groupby("country")["amount"].sum()
```

### Expected behavior

Revenue per customer.

### Actual behavior

Revenue per country.

### Why

The grouping key defines the grain.

### Correct

```python
df.groupby("customer_id")["amount"].sum()
```

### Prevention

Write the intended grain in a comment or design note before coding.

---

## Debug Case 2 — Dirty grouping key

### Buggy data

```text
IN
IN
"IN "
in
```

### Expected

One logical country group.

### Actual

Multiple groups.

### Why

Grouping compares key values; `"IN"`, `"IN "`, and `"in"` are different strings.

### Correct

Standardize the key upstream.

### Prevention

Profile:

```python
df["country"].value_counts(dropna=False)
```

before grouping.

---

## Debug Case 3 — Forgetting multiple keys

### Buggy code

```python
df.groupby("country")["amount"].sum()
```

### Expected

Revenue by country and status.

### Actual

Revenue by country only.

### Correct

```python
df.groupby(["country", "status"])["amount"].sum()
```

### Prevention

Write the output grain explicitly:

```text
country + status
```

---

## Debug Case 4 — Null-key rows disappear

### Symptom

Source has 1,000 rows.

Grouped reconciliation accounts for only 980 rows.

### Root cause

Null grouping keys were dropped.

### Inspection

```python
df["customer_id"].isna().sum()
```

### Correct

```python
df.groupby(
    "customer_id",
    dropna=False,
).size()
```

### Prevention

Make null-key semantics an explicit pipeline decision.

---

## Debug Case 5 — Forgot `dropna=False`

### Buggy code

```python
df.groupby("customer_id").size()
```

### Expected

An "unknown customer" bucket should be visible.

### Actual

Null customer rows are absent.

### Correct

```python
df.groupby(
    "customer_id",
    dropna=False,
).size()
```

### Prevention

Use a reconciliation that compares source row counts to represented group rows when appropriate.

---

## Debug Case 6 — Unexpected categorical groups

### Symptom

Grouped output contains category combinations that do not appear in source rows.

### Root cause

Categorical grouping and unobserved categories.

### Inspection

```python
print(df["country"].dtype)
print(df["country"].cat.categories)
```

### Correct

When only observed categories are intended:

```python
df.groupby(
    "country",
    observed=True,
)
```

### Prevention

Treat category metadata as part of the grouping contract.

---

## Debug Case 7 — Forgot `observed=True`

### Symptom

The output has unexpected category combinations.

### Root cause

`observed=False` can represent unused categories.

### Correct

```python
df.groupby(
    ["country", "status"],
    observed=True,
)
```

### Prevention

Understand the categorical vocabulary and output-grain requirements.

---

## Debug Case 8 — Confusing `count` with `size`

### Buggy code

```python
order_count = (
    df.groupby("customer_id")["amount"]
    .count()
)
```

### Expected

Number of orders.

### Actual

Number of non-null amount values.

### Correct

```python
order_count = (
    df.groupby("customer_id")
    .size()
)
```

### Prevention

Ask whether the metric counts rows or populated values.

---

## Debug Case 9 — Confusing `nunique` with `count`

### Buggy code

```python
df.groupby("customer_id")["product_id"].count()
```

### Expected

Distinct products.

### Actual

Non-null product observations.

### Correct

```python
df.groupby("customer_id")["product_id"].nunique()
```

### Prevention

Say the metric aloud:

```text
distinct products
```

then choose `nunique`.

---

## Debug Case 10 — Assuming grouped output equals input row count

### Buggy assumption

```python
result = df.groupby("country").sum()

assert len(result) == len(df)
```

### Actual

The grouped result usually has fewer rows.

### Correct expectation

```text
one result row per retained group
```

### Prevention

Predict group count before execution.

---

## Debug Case 11 — Misunderstanding `as_index`

### Symptom

Grouping key is unexpectedly the index.

### Correct

```python
df.groupby(
    "country",
    as_index=False,
).agg(
    revenue=("amount", "sum"),
)
```

### Prevention

For flat Gold outputs, choose the output structure intentionally.

---

## Debug Case 12 — Unreadable MultiIndex columns

### Buggy code

```python
result = df.groupby("country").agg(
    {
        "amount": ["sum", "mean"],
        "order_id": ["count", "nunique"],
    }
)
```

### Symptom

Downstream code has to reference:

```text
("amount", "sum")
```

### Correct pattern

```python
result = df.groupby("country").agg(
    total_revenue=("amount", "sum"),
    average_order=("amount", "mean"),
    orders=("order_id", "count"),
    unique_orders=("order_id", "nunique"),
)
```

### Prevention

Use named aggregation for production schemas.

---

## Debug Case 13 — `first`/`last` without understanding row order

### Buggy code

```python
first_seen = (
    df.groupby("customer_id")["order_date"]
    .first()
)
```

### Expected

Earliest chronological date.

### Actual

First valid value according to current group row order.

### Correct

For earliest date:

```python
earliest = (
    df.groupby("customer_id")["order_date"]
    .min()
)
```

### Prevention

Use `first` only when the business requirement is order-sensitive.

---

## Debug Case 14 — Using `transform` when aggregation was intended

### Buggy code

```python
df["customer_total"] = (
    df.groupby("customer_id")["amount"]
    .transform("sum")
)
```

### Expected

One row per customer.

### Actual

One value per original row.

### Correct

```python
customer_total = (
    df.groupby("customer_id", as_index=False)
    .agg(total=("amount", "sum"))
)
```

### Prevention

Choose based on required output shape.

---

## Debug Case 15 — Using `agg` when row-aligned output was required

### Buggy code

```python
customer_total = (
    df.groupby("customer_id")["amount"]
    .sum()
)
```

### Expected

A value on every original order row.

### Correct

```python
df["customer_total"] = (
    df.groupby("customer_id")["amount"]
    .transform("sum")
)
```

### Prevention

Ask:

```text
Do I need one value per group?
or
one value per original row?
```

---

## Debug Case 16 — Using `filter` for row-level filtering

### Buggy code

```python
result = (
    df.groupby("customer_id")
    .filter(lambda g: g["amount"].max() > 1000)
)
```

### Expected

Rows whose own amount is > 1000.

### Actual

All rows of customers whose group maximum exceeds 1000.

### Correct

```python
result = df.loc[df["amount"] > 1000]
```

### Prevention

Distinguish group predicates from row predicates.

---

## Debug Case 17 — `cumsum` without chronological sorting

### Buggy code

```python
df["running_revenue"] = (
    df.groupby("customer_id")["amount"]
    .cumsum()
)
```

### Expected

Chronological running revenue.

### Actual

Running revenue in current row order.

### Correct

```python
df = (
    df.sort_values(
        ["customer_id", "order_date", "order_id"],
        kind="stable",
    )
    .copy()
)

df["running_revenue"] = (
    df.groupby("customer_id")["amount"]
    .cumsum()
)
```

### Prevention

Treat ordering as part of window logic.

---

## Debug Case 18 — `shift` on unsorted groups

### Symptom

"Previous order" is actually a later order.

### Root cause

Rows were not sorted by the business sequence.

### Correct

```python
ordered = (
    df.sort_values(
        ["customer_id", "order_date", "order_id"],
        kind="stable",
    )
    .copy()
)

ordered["previous_amount"] = (
    ordered.groupby("customer_id")["amount"]
    .shift()
)
```

### Prevention

Define and test the ordering key.

---

## Debug Case 19 — `diff` without correct ordering

### Symptom

Negative or nonsensical "days since previous order."

### Root cause

The preceding row is not necessarily the preceding event.

### Correct

Sort first, then call `diff()`.

### Prevention

Test a tiny fixture where chronological order differs from input order.

---

## Debug Case 20 — Global top N instead of per-group top N

### Buggy code

```python
df.nlargest(3, "revenue")
```

### Expected

Top 3 products in every country.

### Actual

Only the top 3 products globally.

### Correct

Use:

```python
df.groupby("country")["revenue"].nlargest(3)
```

or a group-wise rank/filter.

### Prevention

Write:

```text
PARTITION BY country
```

in your design notes before implementing top N.

---

## Debug Case 21 — `apply` for a built-in aggregation

### Buggy code

```python
df.groupby("customer_id")["amount"].apply(
    lambda s: s.sum()
)
```

### Expected

Simple grouped total.

### Actual

Correct values, but potentially more Python overhead.

### Correct

```python
df.groupby("customer_id")["amount"].sum()
```

### Prevention

Check `agg`/built-in methods first.

---

## Debug Case 22 — Custom `apply` causes severe slowdown

### Symptom

Runtime increases dramatically as group count rises.

### Root cause

Python callable is invoked once per group.

### Inspection

Measure:

```python
df["customer_id"].nunique()
```

and benchmark the custom operation.

### Correct

Replace with built-in/vectorized logic when semantics permit.

### Prevention

Benchmark at realistic group cardinality.

---

## Debug Case 23 — Unexpected shape from `apply`

### Symptom

Expected a Series but got a DataFrame or MultiIndex result.

### Root cause

The returned object from the function controls how pandas combines groups.

### Inspection

Print:

```python
print(type(result))
print(result.shape)
print(result.index)
print(result.columns)
```

### Correct

Make the function's return contract explicit.

### Prevention

Unit-test the return type and shape of custom group functions.

---

## Debug Case 24 — Incorrect custom aggregation

### Buggy function

```python
def average(values):
    return values.sum() / len(values)
```

### Problem

If values contain missing data, this does not match `mean()` semantics.

### Correct

Use:

```python
values.mean()
```

or:

```python
df.groupby("customer_id")["amount"].mean()
```

### Prevention

Compare custom metric definitions against built-in semantics using edge-case tests.

---

## Debug Case 25 — High-cardinality/object keys without measuring

### Symptom

Grouping consumes more time or memory than expected.

### Root cause

Large generic key representations and/or very high group counts.

### Inspection

```python
print(df["customer_id"].dtype)
print(df["customer_id"].nunique())
print(df["customer_id"].memory_usage(deep=True))
```

### Correct

Consider intentional dtypes and benchmark.

### Prevention

Treat key representation and cardinality as performance dimensions.

---

## Debug Case 26 — Repeatedly grouping a large DataFrame

### Symptom

Several near-identical grouped operations dominate runtime.

### Root cause

Repeated grouping work.

### Correct

Consolidate metrics where it improves the actual workload:

```python
stats = (
    df.groupby("customer_id")
    .agg(
        total=("amount", "sum"),
        mean=("amount", "mean"),
        maximum=("amount", "max"),
    )
)
```

### Prevention

Profile before optimizing.

---

## Debug Case 27 — Confusing group order with business order

### Symptom

Output appears sorted by group label, so a developer assumes event order is chronological.

### Root cause

Group-key ordering and within-group observation ordering are different concepts.

### Correct

For chronological operations, sort explicitly:

```python
df.sort_values(
    ["customer_id", "order_date", "order_id"],
    kind="stable",
)
```

### Prevention

Document the ordering column(s) required by every window-style metric.

---

# 62. Edge Cases

Production code must survive small and strange groups.

## 62.1 Empty DataFrame

```python
empty = pd.DataFrame(
    {
        "customer_id": pd.Series(dtype="string"),
        "amount": pd.Series(dtype="float64"),
    }
)

result = (
    empty.groupby("customer_id", as_index=False)
    .agg(total=("amount", "sum"))
)
```

Expected principle:

- no group rows;
- schema should still be intentionally defined;
- downstream code should not confuse "no rows" with "pipeline failure."

Test the exact output schema you require.

---

## 62.2 One-row groups

For:

```text
C1 → one amount
```

then:

```python
df.groupby("customer_id")["amount"].transform("mean")
```

simply returns that amount.

But:

```python
transform("std")
```

may be missing because a sample standard deviation is not defined for a single observation.

---

## 62.3 All rows belong to one group

Input:

```text
1,000 rows
country = IN for every row
```

Aggregation output:

```text
1 row
```

Transform output:

```text
1,000 rows
```

This is a useful mental contrast:

```text
agg      → one value per group
transform → one value per original row
```

---

## 62.4 Every row has a unique group

Input:

```text
1,000 rows
1,000 unique customer IDs
```

Aggregation can return:

```text
1,000 rows
```

Grouping does not guarantee row-count reduction.

---

## 62.5 Missing grouping keys

Default:

```python
dropna=True
```

Null groups are not retained.

When needed:

```python
dropna=False
```

Test the exact row count.

---

## 62.6 Empty categorical levels

A categorical key may define categories not present in the current batch.

Use:

```python
observed=True
```

when only observed categories should participate in the grouped result.

---

## 62.7 Group with one non-null value

Example:

```text
amount = [None, None, 100, None]
```

Then:

```text
count(amount) = 1
size()        = 4
```

This is a good edge-case fixture.

---

## 62.8 All-null aggregation column

For:

```text
amount = [None, None]
```

different reducers have different meanings.

For example:

- `count` → 0
- `size` → number of rows
- `mean` → missing
- `min`/`max` → missing
- `sum` → consider `min_count=1` if zero would be misleading

Write tests for business-critical metrics rather than assuming every reducer behaves the same way.

---

## 62.9 Zero standard deviation

For:

```text
amount = [100, 100, 100]
```

group std is zero.

A standard z-score formula divides by zero.

Robust logic must define what to do.

---

## 62.10 Ranking ties

Values:

```text
100
100
90
```

different ranking methods produce different rank values.

Tests must name the desired tie policy.

---

## 62.11 Duplicate ordering timestamps

If two records share the same `order_date`, a stable secondary key is useful:

```python
["customer_id", "order_date", "order_id"]
```

This is especially important for:

```text
cumcount
shift
diff
cumsum
row numbering
tie-breaking
```

---

## 62.12 First `shift()` value

The first row in each group has no previous row.

Expect missing.

That is normal, not an error.

---

## 62.13 First `diff()` value

The first row in each group has no preceding value to subtract.

Expect missing.

---

## 62.14 Fewer than N products

If a country has only two products:

```text
.nlargest(3)
```

can return only two rows for that country.

"Top 3" means:

> up to three available observations

unless your business rules require a different output contract.

---

## 62.15 Custom aggregation returning unexpected types

A custom function may return:

```text
float
int
None
Series
DataFrame
mixed values
```

This can affect:

- output dtype;
- output shape;
- downstream schema.

Test custom function outputs directly.

---

## 62.16 `apply` returning unexpected shapes

A function returning a scalar produces a different combined structure from one returning a Series or DataFrame.

Before using custom `apply`, define:

```text
expected return type
expected columns
expected row count
expected index
```

and test them.

---

# 63. Production Data Engineering Patterns

`groupby` is not merely exploratory analysis.

It appears throughout a production data platform.

## Gold metrics

Examples:

```text
customer revenue
country revenue
daily sales
product metrics
```

Typical code:

```python
gold_customer = (
    orders.groupby("customer_id", as_index=False)
    .agg(
        total_revenue=("amount", "sum"),
        orders=("order_id", "nunique"),
    )
)
```

## Data quality

Group counts can reveal:

```text
rows per key
duplicate keys
missing-key populations
unexpected cardinality
```

Example:

```python
rows_per_customer = (
    orders.groupby(
        "customer_id",
        dropna=False,
    )
    .size()
)
```

## Behavioral metrics

Group-wise transforms and window-style operations support:

```text
order sequence
repeat purchase timing
running revenue
previous event amount
change since previous event
rank within market
```

## Reporting

Grouped outputs support:

```text
top products per country
customer segments
regional summaries
daily metrics
```

---

# 64. Grouped Output as a Data Product

A production grouped result should have a documented contract.

For example:

## Dataset

```text
customer_metrics
```

## Grain

```text
one row per customer_id
```

## Schema

```text
customer_id: string
total_revenue: numeric
order_count: integer
distinct_products: integer
first_order_date: datetime
last_order_date: datetime
```

## Null rules

```text
customer_id null rows:
included/excluded — explicitly documented
```

## Ordering

Do not confuse display ordering with business semantics.

If an output must be sorted for a downstream interface, sort it intentionally.

---

# 65. Data Reconciliation for Grouped Outputs

A grouped transformation should often be reconcilable to source totals.

For a revenue aggregation:

```python
source_total = df["amount"].sum()

grouped_total = (
    df.groupby(
        "country",
        dropna=False,
    )["amount"]
    .sum()
    .sum()
)

print(source_total)
print(grouped_total)
```

If the aggregation includes all source rows and the metric uses compatible null semantics, the totals should reconcile.

## Important caveat

They may differ when:

- rows are filtered before aggregation;
- null grouping keys are dropped;
- the metric uses different missing-value rules;
- `amount` is transformed before grouping;
- business logic deliberately excludes records.

### Better validation

```python
assert (
    source_total == grouped_total
), "Revenue reconciliation failed"
```

For floating-point data, prefer an approximate comparison:

```python
import numpy as np

np.testing.assert_allclose(
    source_total,
    grouped_total,
    rtol=1e-12,
    atol=1e-12,
)
```

### Data Engineering principle

> A grouped Gold metric should be explainable from the source rows.

If it cannot be reconciled, investigate before publishing.

---

# 66. Testing Strategy with pytest

Every important grouping behavior should have a small fixture.

## 66.1 Grouping tests

Test:

- one key;
- multiple keys;
- expected group count;
- null-key behavior;
- categorical grouping.

Example:

```python
def test_group_count():
    result = (
        df.groupby("customer_id")
        .size()
    )

    assert len(result) == 3
```

---

# 67. Aggregation Tests

Test every roadmap-required reducer where the metric is production-critical:

```text
sum
mean
count
size
nunique
min
max
first
last
```

Example:

```python
def test_count_vs_size():
    count = (
        df.groupby("customer_id")["amount"]
        .count()
    )

    size = (
        df.groupby("customer_id")
        .size()
    )

    assert count["C1"] == 2
    assert size["C1"] == 3
```

This is more valuable than a huge test that only checks that pandas executes.

---

# 68. Named Aggregation Tests

Verify flat columns:

```python
def test_named_aggregation_columns():
    result = (
        df.groupby("customer_id", as_index=False)
        .agg(
            total_revenue=("amount", "sum"),
            orders=("order_id", "nunique"),
        )
    )

    assert list(result.columns) == [
        "customer_id",
        "total_revenue",
        "orders",
    ]
```

This protects the Gold schema.

---

# 69. `transform` Tests

Always verify alignment:

```python
def test_transform_preserves_row_count():
    result = (
        df.groupby("customer_id")["amount"]
        .transform("sum")
    )

    assert len(result) == len(df)
```

Also verify actual group values.

Example:

```python
def test_transform_group_total():
    result = (
        df.assign(
            customer_total=(
                df.groupby("customer_id")["amount"]
                .transform("sum")
            )
        )
    )

    assert result.loc[0, "customer_total"] == 350
```

---

# 70. `filter` Tests

The test should prove that **whole groups** survive.

Example concept:

```python
def test_filter_keeps_complete_groups():
    result = (
        df.groupby("customer_id")
        .filter(lambda group: len(group) >= 3)
    )

    assert set(result["customer_id"]) == {"C1", "C3"}
    assert (result["customer_id"] == "C1").sum() == 3
    assert (result["customer_id"] == "C3").sum() == 5
```

Use a fixture whose group sizes are known.

---

# 71. Window-Style Operation Tests

Test:

```text
rank
cumcount
cumsum
shift
diff
nlargest
```

For order-sensitive functions, create a fixture where input order is deliberately not chronological.

This catches accidental dependence on the current layout.

---

# 72. `apply` Equivalence Tests

When replacing `apply`, test the semantics before measuring speed.

```python
apply_result = (
    df.groupby("customer_id")["amount"]
    .apply(lambda s: s.sum())
    .sort_index()
)

agg_result = (
    df.groupby("customer_id")["amount"]
    .sum()
    .sort_index()
)

pd.testing.assert_series_equal(
    apply_result,
    agg_result,
    check_names=False,
    check_dtype=False,
)
```

Performance optimization is not complete if the outputs differ.

---

# 73. Edge-Case Test Matrix

At minimum test:

| Case | What to verify |
|---|---|
| Empty input | Empty but correctly typed result |
| One-row group | Correct aggregate and missing window predecessor |
| One group | One aggregation row, full transform length |
| Unique group per row | Aggregation can equal input row count |
| Missing key | `dropna` semantics |
| Categorical levels | `observed` semantics |
| All-null values | Correct reducer behavior |
| Zero variance | Z-score handling |
| Ranking ties | Explicit tie policy |
| Duplicate timestamps | Deterministic secondary order |
| Fewer than N | Top-N returns available rows |
| Custom `apply` | Return type and shape |
| No matching filter groups | Empty result with expected schema |

---

# 74. `assert_frame_equal`

For table outputs, use:

```python
from pandas.testing import assert_frame_equal
```

Example:

```python
expected = pd.DataFrame(
    {
        "customer_id": ["C1", "C2"],
        "total_revenue": [350.0, 200.0],
    }
)

actual = (
    orders.groupby("customer_id", as_index=False)
    .agg(total_revenue=("amount", "sum"))
)

assert_frame_equal(
    actual,
    expected,
    check_dtype=False,
)
```

For production tests, prefer checking dtypes too when the schema depends on them.

Do not disable every check just to make a test pass.

---

# 75. Performance Checklist

Before optimizing grouped code:

```text
[ ] How many rows are processed?
[ ] How many groups exist?
[ ] How wide is the DataFrame?
[ ] What are the grouping-key dtypes?
[ ] Are keys low-cardinality or high-cardinality?
[ ] Is sorting required by business logic?
[ ] Is group-key sorting required for output?
[ ] Is Python-level apply involved?
[ ] Are repeated groupby operations dominating?
[ ] What is peak memory?
[ ] What does the benchmark actually measure?
```

After optimizing:

```text
[ ] Values are identical or within defined numerical tolerance
[ ] Output row count is identical
[ ] Output schema is identical
[ ] Null semantics are identical
[ ] Ordering semantics are intentional
[ ] Tests pass
```

---

# 76. Groupby Design Checklist

## Before grouping

- [ ] Are grouping keys correctly typed?
- [ ] Are key values standardized?
- [ ] Do null keys matter?
- [ ] Are categorical keys intentional?
- [ ] Do I need `dropna=False`?
- [ ] Do I need `observed=True`?

## During grouping

- [ ] Am I using one or multiple keys correctly?
- [ ] Do I need `agg`, `transform`, `filter`, or `apply`?
- [ ] Do I need named aggregation?
- [ ] Is row order meaningful?
- [ ] Do I need to sort?
- [ ] Is `sort=False` appropriate?

## After grouping

- [ ] Is the output row count what I predicted?
- [ ] Are null groups accounted for?
- [ ] Are column names readable?
- [ ] Does the result preserve intended semantics?
- [ ] Have I tested edge cases?
- [ ] Can the result reconcile to source totals?

---

# 77. AGG / TRANSFORM / FILTER / APPLY Decision Tree

```text
Do I need one or more summary values per group?
        |
       YES
        ↓
       agg()

Do I need one result value aligned to every original row?
        |
       YES
        ↓
    transform()

Do I want to keep/remove entire groups?
        |
       YES
        ↓
     filter()

Do I need arbitrary custom Python logic per group?
        |
       YES
        ↓
      apply()
```

Then remember:

```text
apply is a flexibility tool, not the default tool.
```

Before `apply`, test:

```text
agg
transform
vectorized pandas
NumPy operations
```

---

# 78. Common Mistakes Summary

| Mistake | Why it happens | Correct approach |
|---|---|---|
| Losing null-key rows because `dropna=True` is the default | Default behavior is easy to overlook | Use `dropna=False` when null keys must be represented |
| Unused categories creating empty groups | Categorical metadata is larger than observed data | Use `observed=True` when only observed combinations are intended |
| Using `apply` everywhere | It appears to be the most flexible API | Check built-ins, `agg`, `transform`, and vectorized operations first |
| Producing unreadable MultiIndex columns | Dictionary/list aggregation creates hierarchical columns | Use named aggregation for production-facing schemas |
| Using `count` for row counts | Confuses values with rows | Use `size()` for group row counts |
| Using `size` for non-null metrics | Counts rows regardless of target-column completeness | Use `count()` on the relevant column |
| Using `count` for distinct entities | Counts repeated observations | Use `nunique()` |
| Treating `first` as `min` | Confuses row position with value order | Use `min` for earliest value; use `first` for order-sensitive logic |
| Treating `last` as `max` | Same confusion in reverse | Use `max` for latest value; use `last` when row order defines meaning |
| Assuming aggregation preserves row count | Forgetting that groups collapse | Predict one row per retained group |
| Using `agg` when row-aligned output is required | Group output is too small for original rows | Use `transform()` |
| Using `transform` when a Gold summary is required | Produces one value per source row | Use `agg()` |
| Using `filter` for row predicates | Group predicates and row predicates are different | Use ordinary boolean filtering for row-level rules |
| Running `cumsum` on unsorted data | Current row order is not necessarily business order | Sort by the intended sequence first |
| Running `shift` on unsorted data | "Previous" becomes arbitrary | Sort first and define tie-breakers |
| Running `diff` without correct ordering | Differences follow current row order | Sort first |
| Using global top N for a per-group request | `nlargest` on the full frame ignores partitions | Use grouped `nlargest` or group-wise rank |
| Ignoring ranking ties | "Top 3" is ambiguous | Choose a tie policy and test it |
| Grouping on object keys without measuring | Generic object representation may be expensive at scale | Inspect dtype/cardinality and benchmark alternatives |
| Assuming categoricals always improve speed | Performance depends on workload | Benchmark the real dataset |
| Assuming sorted keys always improve performance | Sorting has its own cost | Measure end-to-end time |
| Repeating groupby operations unnecessarily | The same grouping work is redone | Consolidate where profiling shows a bottleneck |
| Treating group display order as business order | Group-key ordering differs from observation order | Sort explicitly for order-sensitive logic |

---

# 79. Checkpoint

You are ready to move on when you can do all of the following without looking up the answer.

## Required roadmap checkpoint

### 1. Explain

```text
count
vs
size
vs
nunique
```

in your own words.

Expected answer:

```text
count   = non-null values in the selected column
size    = rows in the group
nunique = distinct values, excluding null by default
```

### 2. Explain each in one sentence

```text
agg       = summary values per group
transform = group-derived values aligned to every original row
filter    = keep/remove complete groups
apply     = custom Python logic per group
```

### 3. Compute a per-group running total

```python
df["running_total"] = (
    df.groupby("customer_id")["amount"]
    .cumsum()
)
```

with correct ordering when chronology matters.

### 4. Compute a per-group rank

```python
df["rank"] = (
    df.groupby("country")["revenue"]
    .rank(
        method="min",
        ascending=False,
    )
)
```

with an intentional tie policy.

### 5. Replace a slow `apply`

Explain why:

```python
df.groupby("customer_id")["amount"].apply(
    lambda s: s.sum()
)
```

can be replaced with:

```python
df.groupby("customer_id")["amount"].sum()
```

when the semantics are the same.

---

## Additional self-check questions

6. What changes when `dropna=False` is used?

7. What does `observed=True` mean for categorical groupers?

8. What changes when `as_index=False` is passed?

9. Given 12 distinct observed `(country, status)` combinations, how many rows should a normal two-key aggregation return?

10. How can categorical and null semantics make naive group-count reasoning wrong?

11. What does `cumcount()` return for the first row in each group?

12. What does `shift()` return for the first row in each group?

13. What does `diff()` return for the first row in each group?

14. What is the difference between global top 3 and top 3 per country?

15. When does `nlargest(3)` return fewer than three rows for a group?

16. How would you express daily grouping with `pd.Grouper`?

17. Why is named aggregation useful for Gold tables?

18. When is a custom aggregation function justified?

19. What performance costs can `apply` introduce?

20. What dimensions should you record in a benchmark?

21. Why can sorting improve one metric while increasing total runtime?

22. Why should group counts be inspected before joins?

---

# 80. Cheat Sheet

## Basic groupby

```python
df.groupby("customer_id")
```

```python
df.groupby(["country", "status"])
```

## Core aggregations

```text
.sum()
.mean()
.count()
.size()
.nunique()
.min()
.max()
.first()
.last()
```

## Named aggregation

```python
df.groupby("customer_id").agg(
    total=("amount", "sum"),
    orders=("order_id", "nunique"),
)
```

## Flat grouped output

```python
df.groupby(
    "customer_id",
    as_index=False,
).agg(
    total=("amount", "sum"),
)
```

## Grouping options

```python
as_index=False
sort=False
dropna=False
observed=True
```

## Transform

```python
df.groupby(...)[...].transform(...)
```

Example:

```python
df["group_total"] = (
    df.groupby("customer_id")["amount"]
    .transform("sum")
)
```

## Filter

```python
df.groupby(...).filter(...)
```

Example:

```python
df.groupby("customer_id").filter(
    lambda group: len(group) >= 3
)
```

## Window-like operations

```python
rank()
cumcount()
cumsum()
shift()
diff()
```

## Group-wise top N

```python
df.groupby("country")["revenue"].nlargest(3)
```

or:

```python
ranked = df.assign(
    rank=(
        df.groupby("country")["revenue"]
        .rank(
            method="first",
            ascending=False,
        )
    )
)

top3 = ranked.loc[ranked["rank"] <= 3]
```

## Advanced

```python
df.groupby(...).apply(...)
```

```python
pd.Grouper(
    key="created_at",
    freq="D",
)
```

## Mental model

```text
Rows
  ↓
Grouping keys
  ↓
Groups
  ↓
Apply operation
  ↓
Combine
```

## Method decision rule

```text
agg       = summary per group
transform = one result per original row
filter    = keep/remove whole groups
apply     = custom per-group logic
```

## Shape rule

```text
agg
→ usually fewer rows; one per retained group

transform
→ same number of rows as original input

filter
→ subset of original rows; whole groups survive or disappear

apply
→ output shape depends on the returned object
```

---

# 81. Production Review Checklist

Before publishing a grouped transformation:

```text
[ ] I can state the input grain.
[ ] I can state the output grain.
[ ] Grouping keys are typed correctly.
[ ] Key values are standardized.
[ ] Null-key semantics are intentional.
[ ] Categorical semantics are intentional.
[ ] I predicted group count before execution.
[ ] `count` vs `size` semantics are correct.
[ ] `nunique` is used for distinct entities.
[ ] `first`/`last` are used only when row order is meaningful.
[ ] Named aggregation gives a readable schema.
[ ] `as_index` behavior is intentional.
[ ] `sort` behavior is intentional.
[ ] Window-style calculations have explicit ordering where needed.
[ ] Top-N tie behavior is defined.
[ ] `apply` is justified or replaced.
[ ] Built-in/vectorized alternatives were considered.
[ ] Edge cases are tested.
[ ] Output shape is asserted.
[ ] Financial/business totals reconcile.
[ ] Performance has been measured if scale requires it.
[ ] The result is documented as a data product.
```

---

# 82. Learning Loop for This Topic

Use this loop until the behavior becomes automatic:

## 1. Read

Read one operation.

## 2. Predict

Write down:

```text
number of groups
output row count
null behavior
ordering behavior
output type
```

## 3. Run

Execute on a tiny DataFrame.

## 4. Verify

Check:

```python
result.shape
result.dtypes
result.index
result.columns
result.head()
```

## 5. Assert

Convert your understanding into a test.

## 6. Break it

Try:

```text
null keys
categoricals
duplicates
one-row groups
unsorted timestamps
ties
empty input
```

## 7. Measure

For important workloads:

```text
rows
groups
runtime
memory
```

## 8. Explain aloud

Explain:

```text
why the operation returned this shape
why nulls were kept or dropped
why ordering mattered
why one implementation was faster or slower
```

That is the difference between knowing pandas syntax and engineering reliable grouped transformations.

---

# 83. Final Mental Model

The entire topic can be compressed into one idea:

```text
                   GROUPBY
                     |
          +----------+----------+
          |                     |
       summarize             preserve rows
          |                     |
        agg()              transform()
          |                     |
      one result            one result
      per group             per input row
          |
          +--------------------------+
          |                          |
       filter()                   apply()
          |                          |
   keep/remove groups       custom group logic
```

And for window-style work:

```text
groupby(partition)
       +
explicit order
       +
window-like operation
       ↓
rank / cumcount / cumsum / shift / diff
```

The production mindset is:

```text
1. Define the grain.
2. Define the grouping keys.
3. Predict the number of groups.
4. Decide how null keys behave.
5. Decide how categorical keys behave.
6. Choose agg / transform / filter / apply from output semantics.
7. Sort when business ordering matters.
8. Validate shape and values.
9. Reconcile totals.
10. Benchmark the actual workload.
11. Replace unnecessary Python-level work.
12. Publish a defined, testable output schema.
```

---

# 84. Official pandas references

For current pandas 3.x behavior, consult the official documentation:

- [pandas `DataFrame.groupby`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html)
- [pandas GroupBy user guide — split-apply-combine](https://pandas.pydata.org/docs/user_guide/groupby.html)
- [pandas `DataFrameGroupBy.apply`](https://pandas.pydata.org/docs/reference/api/pandas.api.typing.DataFrameGroupBy.apply.html)
- [pandas GroupBy reference](https://pandas.pydata.org/docs/reference/groupby.html)

A particularly important current-version detail is that pandas 3.0 changed the default for categorical grouping to `observed=True`; `dropna` remains `True` by default. Verify the installed version in your own environment when reproducing examples. citeturn245631search3

---

# Topic 06 Exit Criteria

Do not leave this topic because you can make code execute.

Leave it when you can take a new DataFrame and reliably answer, before execution:

```text
What is the grain?
What are the groups?
How many groups should survive?
What happens to null keys?
What happens to categories?
Do I need agg, transform, filter, or apply?
Does ordering matter?
What is the expected output shape?
How will I test it?
How will I reconcile it?
How will I benchmark it at scale?
```

That is the level at which `groupby` becomes a Data Engineering tool rather than a pandas trick.
