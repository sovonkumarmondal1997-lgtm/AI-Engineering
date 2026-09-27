# 07 — merge, join, concat, and join cardinality

> **Stage 2 — Python for Data Engineering → Module 2.3 — DataFrames with pandas**
>
> **Topic 07:** merge, join, concat, and join cardinality  
> **Level:** Basic → Intermediate → Advanced → Production-oriented
>
> **Core production mindset:** Never perform a join without understanding the join keys, expected cardinality, expected row-count behavior, and treatment of unmatched rows.

---

## Learning contract

This chapter follows the authoritative Module 2.3 roadmap for Topic 07.

The goal is not to memorize pandas join syntax. The goal is to reason about a join **before** executing it: define the relationship, predict the result shape, validate the relationship, diagnose mismatches, and reconcile business measures.

For important joins, use this learning loop:

```text
Predict
  ↓
Execute
  ↓
Inspect
  ↓
Validate
  ↓
Reconcile
  ↓
Explain
```

A production join should start with a contract such as:

```text
Join contract
-------------
Left table: orders
Right table: customers
Key: customer_id
Expected cardinality: many-to-one
Join type: left
Expected left-row preservation: yes
Expected unmatched orders: retained and reported
Expected revenue change: none
Validation: validate="many_to_one"
Reconciliation: row count + revenue + unmatched-key report
```

---

# 1. Why Joins Matter in Data Engineering

Joins are not merely a pandas operation. They are a **data-model and correctness operation**.

A bad join can:

- duplicate revenue;
- multiply transaction rows;
- drop valid records;
- create false metrics;
- silently lose customers;
- attach incorrect dimension values;
- distort downstream aggregations;
- create impossible business totals;
- consume large amounts of memory;
- hide source-system data-quality problems.

### Typical production relationships

```text
orders      → customers
orders      → products
transactions → reference data
payments    → FX rates
IoT events  → device registry
marketing events → campaign metadata
```

The engineer must first know **what relationship the join is supposed to represent**.

---

## 1.1 Orders + Customers

Suppose:

```text
orders
------
order_id
customer_id
amount

customers
---------
customer_id
segment
country
```

The intent is to enrich each order with customer attributes.

If `customers.customer_id` is unique:

```text
many orders
      ↓
 one customer
```

The expected relationship is:

```text
many-to-one
```

---

## 1.2 How a duplicate dimension corrupts metrics

Suppose the customer table contains:

```text
customer_id | segment
------------|--------
C001        | Gold
C001        | Silver
```

and orders contain:

```text
order_id | customer_id | amount
---------|-------------|-------
O1001    | C001        | 100
O1002    | C001        | 200
```

A join can produce:

```text
order_id | customer_id | amount | segment
---------|-------------|--------|--------
O1001    | C001        | 100    | Gold
O1001    | C001        | 100    | Silver
O1002    | C001        | 200    | Gold
O1002    | C001        | 200    | Silver
```

Rows changed:

```text
2 → 4
```

Revenue changed:

```text
300 → 600
```

The join did not crash. The code can be syntactically and mechanically correct while the data product is wrong.

> **Production lesson:** Many join failures are data-model failures that pandas executes successfully.

---

# 2. Join Mental Model

Think about a join as:

```text
Left rows
   +
Matching key
   +
Right rows
   ↓
Result rows
```

For an equality join, a useful key-level rule is:

```text
result rows for a matching key
=
left_count(key) × right_count(key)
```

Examples:

```text
1 × 1 = 1
10 × 1 = 10
1 × 10 = 10
2 × 3 = 6
10 × 20 = 200
```

This multiplication is the foundation of row-explosion reasoning.

---

# 3. Join Keys

A **join key** is the field or fields used to decide which records correspond.

Examples:

```text
customer_id
order_id
product_id
account_id
device_id
currency
date
```

## 3.1 Business key

A business key identifies an entity or relationship in business terms.

Examples:

```text
customer_id
policy_id
account_number
product_code
```

Never assume a key is unique just because its name contains `id`.

## 3.2 One-column (single-column) key

```python
left.merge(
    right,
    on="customer_id",
)
```

## 3.3 Composite key

Sometimes identity is defined by several columns:

```text
country + customer_id
```

Then:

```python
left.merge(
    right,
    on=["country", "customer_id"],
)
```

Using only one component can create cross-entity matches.

---

# 4. The Join Contract

Before writing the merge, record:

```text
Join name:
Left dataset:
Right dataset:
Left grain:
Right grain:
Join key(s):
Expected cardinality:
Join type:
Expected left-row behavior:
Expected right-row behavior:
Expected unmatched-left behavior:
Expected unmatched-right behavior:
Expected result row count:
Expected measure behavior:
Null-key policy:
Validation rule:
Diagnostic rule:
Reconciliation rule:
```

### Example

```text
Join name: order customer enrichment
Left dataset: orders
Right dataset: customers
Left grain: one row per order
Right grain: one row per customer
Join key: customer_id
Expected cardinality: many-to-one
Join type: left
Expected left-row behavior: every order survives
Expected unmatched-left behavior: retain + report
Expected result row count: exactly len(orders)
Expected measure behavior: amount total unchanged
Null-key policy: explicit
Validation: many_to_one
Diagnostics: indicator=True during validation
Reconciliation: row count + revenue + unmatched orders
```

This contract is more important than the exact spelling of the API call.

---

# 5. `merge()` Basics

`merge()` performs database-style row matching.

Two common forms are:

```python
pd.merge(
    left,
    right,
    on="customer_id",
)
```

and:

```python
result = left.merge(
    right,
    on="customer_id",
)
```

## Tiny example

```python
import pandas as pd

orders = pd.DataFrame(
    {
        "order_id": ["O1", "O2", "O3"],
        "customer_id": ["C1", "C1", "C2"],
        "amount": [100, 200, 150],
    }
)

customers = pd.DataFrame(
    {
        "customer_id": ["C1", "C2"],
        "segment": ["Gold", "Silver"],
    }
)

result = orders.merge(
    customers,
    on="customer_id",
)
```

Expected result:

```text
  order_id customer_id  amount segment
0       O1          C1     100    Gold
1       O2          C1     200    Gold
2       O3          C2     150  Silver
```

For the matching keys:

```text
C1: 2 × 1 = 2
C2: 1 × 1 = 1

Total = 3 rows
```

The key reasoning is:

```text
orders.customer_id → many
customers.customer_id → one
```

---

# 6. `how=` Join Types

The main join modes are:

```text
inner
left
right
outer
cross
```

| Join type | Keeps | Typical question | Main risk |
|---|---|---|---|
| `inner` | Matching keys | Which records exist on both sides? | Silent row loss |
| `left` | All left rows + matches | Can I enrich the main population? | Duplicate right keys |
| `right` | All right rows + matches | Can I preserve the right population? | Less obvious left/right ownership |
| `outer` | Keys from both sides | Which keys exist on either source? | Mismatch populations can be ignored |
| `cross` | Every pair | Do I intentionally need a Cartesian product? | Very large result |

---

# 7. INNER JOIN

## What

```python
how="inner"
```

keeps only rows whose key has a match on both sides.

## Example

```python
orders = pd.DataFrame(
    {
        "order_id": ["O1", "O2", "O3"],
        "customer_id": ["C1", "C2", "C9"],
        "amount": [100, 200, 300],
    }
)

customers = pd.DataFrame(
    {
        "customer_id": ["C1", "C2"],
        "segment": ["Gold", "Silver"],
    }
)

result = orders.merge(
    customers,
    on="customer_id",
    how="inner",
)
```

Expected:

```text
O1/C1
O2/C2
```

`C9` disappears.

## Data Engineering meaning

An inner join can be exactly right when the requirement is:

> return only records with a valid matching reference.

It is dangerous when the intended population is all orders.

> Never select `inner` merely because it removes missing values from the output.

---

# 8. LEFT JOIN

Use:

```python
how="left"
```

when the left table represents the population that must be preserved.

```python
result = orders.merge(
    customers,
    on="customer_id",
    how="left",
)
```

For an unknown customer:

```text
order row → retained
customer columns → missing
```

This is a common enrichment pattern:

```text
facts/events
    +
reference attributes
    ↓
 enriched facts/events
```

### Important condition

A left join does **not** guarantee the same number of rows when the right key is duplicated.

For a valid many-to-one relationship:

```text
len(result) == len(left)
```

For a duplicated right key, rows can multiply.

---

# 9. RIGHT JOIN

Use:

```python
how="right"
```

when the right table is the population you explicitly want to preserve.

It is conceptually the mirror of a left join.

Many teams prefer a convention in which the main population is written on the left and enrichment on the right because the preservation rule is easy to read:

```python
facts.merge(
    dimension,
    how="left",
)
```

That is a readability convention, not an absolute rule.

---

# 10. OUTER JOIN

Use:

```python
how="outer"
```

when keys from both sides matter.

```python
left = pd.DataFrame(
    {
        "customer_id": ["C1", "C2"],
        "left_value": [10, 20],
    }
)

right = pd.DataFrame(
    {
        "customer_id": ["C2", "C3"],
        "right_value": [200, 300],
    }
)

result = left.merge(
    right,
    on="customer_id",
    how="outer",
)
```

Conceptually:

```text
C1 → left only
C2 → both
C3 → right only
```

This can be valuable for reconciliation.

It becomes dangerous when an outer join is used to make a pipeline appear complete without investigating the mismatch populations.

---

# 11. CROSS JOIN

A cross join creates every possible pair:

```python
result = left.merge(
    right,
    how="cross",
)
```

If:

```text
left = 3 rows
right = 4 rows
```

then:

```text
3 × 4 = 12 rows
```

Example:

```python
countries = pd.DataFrame(
    {"country": ["IN", "US", "GB"]}
)

scenarios = pd.DataFrame(
    {"scenario": ["base", "stress", "upside", "downside"]}
)

result = countries.merge(
    scenarios,
    how="cross",
)
```

Expected rows:

```text
12
```

Before a cross join, calculate:

```text
len(left) × len(right)
```

A cross join can become extremely large even when each input looks reasonable.

---

# 12. `on=`

Use `on=` when both sides use the same key name:

```python
result = orders.merge(
    customers,
    on="customer_id",
    how="left",
)
```

This states exactly which column is being matched.

---

# 13. `left_on=` and `right_on=`

Use these when key names differ:

```text
orders.customer_id
customers.id
```

```python
result = orders.merge(
    customers,
    left_on="customer_id",
    right_on="id",
    how="left",
)
```

The data contract should document that these represent the same identifier.

---

# 14. `suffixes=`

Overlapping non-key columns require disambiguation.

```python
result = left.merge(
    right,
    on="customer_id",
    suffixes=("_order", "_customer"),
)
```

Prefer meaningful names such as:

```text
status_order
status_customer
```

rather than leaving downstream code to interpret:

```text
status_x
status_y
```

Projection can sometimes remove the conflict more cleanly:

```python
customers_small = customers[
    ["customer_id", "segment"]
]
```

---

# 15. Join Output Row Reasoning

The key skill is to predict result size **before** execution.

For each key:

```text
left_count(key) × right_count(key)
```

For a left join, also account for left keys with no right match.

## One-to-one

```text
left key = one occurrence
right key = one occurrence
```

For a matching key:

```text
1 × 1 = 1
```

## Many-to-one

```text
many left rows
one right row
```

For key C1:

```text
5 × 1 = 5
```

A left many-to-one enrichment should keep the left population at the same row count.

## One-to-many

```text
one left row
many right rows
```

For key C1:

```text
1 × 3 = 3
```

The output grows.

## Many-to-many

```text
2 left rows
3 right rows
```

Result:

```text
2 × 3 = 6
```

---

# 16. Join Cardinality

Cardinality describes how many records can exist per key on each side.

| Cardinality | Left key | Right key | Example | Main risk |
|---|---|---|---|---|
| one-to-one | unique | unique | customer ↔ profile | unexpected duplicate key |
| one-to-many | unique | repeated | customer → addresses | intended expansion must be explicit |
| many-to-one | repeated | unique | orders → customer | duplicate reference key causes explosion |
| many-to-many | repeated | repeated | products ↔ tags | multiplicative explosion |

The question is not:

> 

The question is not:

> Are there duplicate keys anywhere?

The useful questions are:

```text
Which side is supposed to be unique?
At what grain is the key unique?
What relationship does that imply?
```

---

# 17. `validate=` — Turn Cardinality Into a Runtime Check

`validate=` lets pandas check the relationship that you expect.

```python
validate="one_to_one"
validate="one_to_many"
validate="many_to_one"
validate="many_to_many"
```

For orders to customers:

```python
orders.merge(
    customers,
    on="customer_id",
    how="left",
    validate="many_to_one",
)
```

This says:

```text
left key may repeat
right key must be unique
```

## Meaning of each setting

| `validate=` | What pandas checks | Meaning |
|---|---|---|
| `one_to_one` | key unique on both sides | one left row ↔ one right row |
| `one_to_many` | key unique on left | one left row ↔ many right rows |
| `many_to_one` | key unique on right | many left rows ↔ one right row |
| `many_to_many` | allows repeated keys on both sides | no uniqueness protection; relationship is explicitly allowed |

### Important

`validate=` does not repair a bad relationship.

It converts the relationship assumption into a **fail-fast test**.

---

# 18. Deliberately Break a `many_to_one` Join

Create a bad customer dimension:

```python
customers_bad = pd.DataFrame(
    {
        "customer_id": ["C1", "C1", "C2"],
        "segment": ["Gold", "Silver", "Bronze"],
    }
)

orders = pd.DataFrame(
    {
        "order_id": ["O1", "O2"],
        "customer_id": ["C1", "C2"],
        "amount": [100, 200],
    }
)
```

Now:

```python
orders.merge(
    customers_bad,
    on="customer_id",
    how="left",
    validate="many_to_one",
)
```

should fail because `C1` appears twice on the right.

Without validation, the result can have three rows:

```text
C1 → 1 × 2 = 2
C2 → 1 × 1 = 1
```

Total:

```text
3 rows
```

The input had two order rows.

### Production lesson

Prefer:

```text
contract violation
→ immediate failure
```

over:

```text
incorrect data
→ downstream corruption
→ later discovery
```

---

# 19. `validate="many_to_many"` Is Not a Safety Check

This is easy to misunderstand.

```python
validate="many_to_many"
```

means:

> The many-to-many relationship is allowed.

It does **not** mean:

> Protect me from many-to-many expansion.

For an unintended many-to-many relationship, the correct response is to investigate the data or contract, not to silence the validation by changing the validation mode.

---

# 20. Deliberate Many-to-Many Example

Use a tiny example so the multiplication can be computed by hand.

```python
left = pd.DataFrame(
    {
        "key": ["A", "A"],
        "left_id": [1, 2],
    }
)

right = pd.DataFrame(
    {
        "key": ["A", "A", "A"],
        "right_id": [10, 11, 12],
    }
)

result = left.merge(
    right,
    on="key",
    how="inner",
)
```

### Predict first

```text
left A = 2 rows
right A = 3 rows

2 × 3 = 6
```

Expected result:

```text
key | left_id | right_id
----|---------|---------
A   | 1       | 10
A   | 1       | 11
A   | 1       | 12
A   | 2       | 10
A   | 2       | 11
A   | 2       | 12
```

### Why this matters

Pandas is doing exactly what a relational equality join says to do.

The engineering error is assuming:

```text
2 + 3
```

when the actual relationship produces:

```text
2 × 3
```

---

# 21. Row Explosion

**Row explosion** occurs when duplicate keys cause the join to create more combinations than the engineer expected.

For a key:

```text
m left occurrences
n right occurrences
```

the matching rows can be:

```text
m × n
```

Examples:

```text
2 × 3   = 6
10 × 20 = 200
100 × 50 = 5,000
```

At scale, a small relationship mistake can become a large memory problem.

### Production rule

> Diagnose the relationship before trying to optimize the join.

---

# 22. Row Loss

The opposite failure mode is **row loss**.

Common causes:

```text
inner join
unmatched keys
incorrect key normalization
incorrect join type
filtering before the join
```

Measure explicitly:

```python
rows_before = len(orders)

joined = orders.merge(
    customers,
    on="customer_id",
    how="inner",
)

rows_after = len(joined)

print(rows_before)
print(rows_after)
```

The difference is not automatically a bug.

It is a signal to investigate:

```text
Was row loss intended?
Which keys were lost?
Why were they lost?
```

---

# 23. `indicator=True`

Use:

```python
indicator=True
```

to add a `_merge` column that identifies the source relationship.

```python
result = left.merge(
    right,
    on="key",
    how="outer",
    indicator=True,
)
```

The categories are:

```text
left_only
right_only
both
```

Inspect:

```python
result["_merge"].value_counts()
```

This is especially useful when you are diagnosing key coverage.

---

# 24. Outer Diagnostic Join

A useful debugging pattern is:

```python
diagnostic = orders.merge(
    customers[["customer_id"]],
    on="customer_id",
    how="outer",
    indicator=True,
)
```

Then:

```python
diagnostic["_merge"].value_counts()
```

Interpretation:

```text
both
→ key exists on both sides

left_only
→ key exists only in orders

right_only
→ key exists only in customers
```

This is often a better diagnostic than staring at a giant joined DataFrame.

---

# 25. Anti-Join

An anti-join returns left-side rows whose keys do not exist on the right.

## Indicator pattern

```python
diagnostic = orders.merge(
    customers[["customer_id"]],
    on="customer_id",
    how="left",
    indicator=True,
)

unmatched_orders = diagnostic.loc[
    diagnostic["_merge"].eq("left_only")
]
```

### Typical use cases

```text
orders with unknown customers
payments with unknown accounts
IoT events with unknown devices
transactions with missing reference records
```

### Production meaning

An anti-join is often a **data-quality report**.

---

# 26. Semi-Join

A semi-join returns left rows whose key exists on the right, without attaching right-side columns.

Simple pandas pattern:

```python
known_orders = orders.loc[
    orders["customer_id"].isin(
        customers["customer_id"]
    )
]
```

This means:

```text
keep the left row
if its key exists in the right key set
```

It is different from:

```python
orders.merge(customers, ...)
```

because the goal is existence, not attribute enrichment.

---

# 27. Anti-Join vs Semi-Join

| Pattern | Question | Right attributes added? |
|---|---|---|
| Anti-join | Which left rows have no matching right key? | No |
| Semi-join | Which left rows have a matching right key? | No |
| Enrichment merge | What right-side attributes belong to each left row? | Yes |

### Mental model

```text
semi
→ key exists

anti
→ key does not exist

merge
→ attach attributes
```

---

# 28. Key Hygiene: Dtype Mismatch

Suppose:

```text
orders.customer_id     → int64
customers.customer_id  → string
```

These are different typed representations.

Inspect before joining:

```python
print(orders["customer_id"].dtype)
print(customers["customer_id"].dtype)
```

Normalize intentionally:

```python
orders["customer_id"] = (
    orders["customer_id"]
    .astype("string")
)

customers["customer_id"] = (
    customers["customer_id"]
    .astype("string")
)
```

### Do not stringify blindly

Ask first:

```text
Is this an identifier?
Can leading zeros matter?
Are non-numeric codes possible?
What should null mean?
```

---

# 29. Key Hygiene: Whitespace

These values differ:

```text
"C001"
" C001 "
```

If whitespace is not meaningful:

```python
def normalize_customer_id(series: pd.Series) -> pd.Series:
    return (
        series
        .astype("string")
        .str.strip()
    )
```

Apply the same rule to both sources.

Then test it.

---

# 30. Key Hygiene: Case

These differ as strings:

```text
"IN"
"in"
```

If the business contract defines uppercase codes:

```python
orders["country"] = (
    orders["country"]
    .astype("string")
    .str.strip()
    .str.upper()
)

rates["country"] = (
    rates["country"]
    .astype("string")
    .str.strip()
    .str.upper()
)
```

Do not force case normalization when case is business-significant.

---

# 31. Key Hygiene: Composite Keys

Suppose customer identity is:

```text
(country, customer_id)
```

Then:

```python
result = orders.merge(
    customers,
    on=["country", "customer_id"],
    how="left",
    validate="many_to_one",
)
```

A join only on:

```python
on="customer_id"
```

can accidentally match:

```text
IN/101
```

to:

```text
US/101
```

if both exist.

---

# 32. Validate Composite-Key Uniqueness

For the right side:

```python
key_counts = (
    customers
    .groupby(
        ["country", "customer_id"],
        dropna=False,
    )
    .size()
)

bad_keys = key_counts.loc[
    key_counts > 1
]
```

If `bad_keys` is not empty, the expected many-to-one contract is not true at that grain.

### Production rule

> Validate uniqueness at the exact grain used by the join.

---

# 33. pandas Null-Key Semantics vs SQL

This is a critical detail.

Pandas `merge` can match missing keys to missing keys.

Example:

```python
left = pd.DataFrame(
    {
        "key": ["A", None],
        "left_value": [1, 2],
    }
)

right = pd.DataFrame(
    {
        "key": ["A", None],
        "right_value": [10, 20],
    }
)

result = left.merge(
    right,
    on="key",
    how="inner",
)
```

The null-key rows can match.

This differs from ordinary SQL equality-join semantics, where:

```text
NULL = NULL
```

does not evaluate as true.

Pandas documents this difference explicitly. citeturn243046search1turn243046search5

## Why it is dangerous

A missing ID normally means:

```text
identity unknown
```

not:

```text
all missing IDs represent the same entity
```

Therefore null-key behavior must be a deliberate data contract.

---

# 34. Explicit Null-Key Policies

Possible policies include:

### Drop null-key rows

Use when the relationship requires a non-null key and invalid rows should be separated.

### Quarantine null-key rows

Useful when source records must be preserved but cannot be safely enriched.

### Preserve left rows without matching

Useful for an enrichment pipeline that must retain the main population while leaving reference attributes missing.

### Use an explicit unknown entity

Appropriate only when the business model defines a legitimate unknown/sentinel entity.

Do not let pandas null matching silently choose the policy for you.

---

# 35. Point-in-Time Enrichment: `merge_asof()`

A normal equality merge asks:

```text
Does the key match exactly?
```

`merge_asof()` asks something different:

```text
Which eligible reference record is nearest in time?
```

It is useful for:

```text
order → FX rate
trade → quote
transaction → price
event → configuration
sensor reading → calibration state
```

Current pandas documentation describes `merge_asof` as a merge by key distance and requires the merge key to be sorted ascending before the operation. citeturn243046search0

---

# 36. Why Equality Join Is Wrong for Many Time-Based Lookups

Suppose:

```text
order_time = 2026-01-03 10:30
rate_time  = 2026-01-03 09:00
```

An equality join asks:

```text
10:30 == 09:00 ?
```

No.

But the business question may be:

> What was the latest known rate before the order?

That is an as-of problem.

---

# 37. `merge_asof()` Basic Pattern

```python
orders = orders.sort_values(
    "order_time",
    kind="stable",
)

rates = rates.sort_values(
    "rate_time",
    kind="stable",
)

enriched = pd.merge_asof(
    orders,
    rates,
    left_on="order_time",
    right_on="rate_time",
    direction="backward",
)
```

The result is left-oriented: every left row remains, with an eligible right match when one exists.

---

# 38. `merge_asof()` Sorting Requirement

Do not interpret:

```text
mostly sorted
```

as sorted.

Establish the required order:

```python
left = left.sort_values(
    "event_time",
    kind="stable",
)

right = right.sort_values(
    "reference_time",
    kind="stable",
)
```

Then call `merge_asof()`.

The current pandas documentation specifies ascending ordering of the merge key. Sorting the additional `by` columns is not required. citeturn243046search0

---

# 39. `direction="backward"`

Backward means:

```text
latest right timestamp
<=
left timestamp
```

Timeline:

```text
09:00 ------- 10:00 ------- 12:00
              ↑
left event = 10:30

backward match = 10:00
```

This is usually the correct direction for:

```text
latest known FX rate
latest known price
latest known configuration
```

---

# 40. `direction="forward"`

Forward means:

```text
earliest right timestamp
>=
left timestamp
```

Timeline:

```text
09:00 ------- 10:00 ------- 12:00
                         ↑
left event = 10:30

forward match = 12:00
```

Use this only when the business rule asks for the next eligible record.

A future rate must not be substituted for a historical rate simply because it is available.

---

# 41. `direction="nearest"`

Nearest selects the right-side time key with the smallest absolute distance.

Use it when the business definition truly is:

```text
closest observation in time
```

Do not use `nearest` for 

substitute `nearest` for `backward` just because it finds a match. The business meaning decides.

---

# 42. `by=` in `merge_asof`

For multi-entity reference data, time proximity alone is not enough.

Suppose FX rates contain:

```text
currency | rate_time | rate
---------|-----------|-----
USD      | 09:00     | 1.00
EUR      | 09:00     | 1.10
```

An EUR order must not receive the USD rate because the timestamps are equally close.

Use:

```python
enriched = pd.merge_asof(
    orders.sort_values("order_time"),
    rates.sort_values("rate_time"),
    left_on="order_time",
    right_on="rate_time",
    by="currency",
    direction="backward",
)
```

The mental model is:

```text
partition by currency
        ↓
search by time inside the partition
```

---

# 43. `tolerance=` in `merge_asof`

`tolerance` limits how far away a candidate reference record may be.

```python
enriched = pd.merge_asof(
    orders.sort_values("order_time"),
    rates.sort_values("rate_time"),
    left_on="order_time",
    right_on="rate_time",
    by="currency",
    direction="backward",
    tolerance=pd.Timedelta("1D"),
)
```

If the most recent prior rate is older than one day, it is not eligible.

Current pandas requires `tolerance` to be compatible with the merge-key type. citeturn243046search0

### Business question

What happens if no rate is within tolerance?

Possible policies:

```text
leave rate missing
quarantine the transaction
fail the pipeline
use a documented fallback
```

There is no universal answer. The policy belongs in the join contract.

---

# 44. Point-in-Time Enrichment Contract

For FX enrichment:

```text
Left: orders
Right: fx_rates
Partition key: currency
Left time: order_time
Right time: rate_time
Direction: backward
Tolerance: 1 day
Meaning: latest known acceptable rate
Unmatched policy: explicit
```

Code:

```python
orders_sorted = orders.sort_values(
    "order_time",
    kind="stable",
)

rates_sorted = rates.sort_values(
    "rate_time",
    kind="stable",
)

enriched_fx = pd.merge_asof(
    orders_sorted,
    rates_sorted,
    left_on="order_time",
    right_on="rate_time",
    by="currency",
    direction="backward",
    tolerance=pd.Timedelta("1D"),
)
```

The operation should be evaluated against the written contract, not merely checked for successful execution.

---

# 45. Multiple Reference Rows at the Same Time

Suppose the reference table has:

```text
currency | rate_time | rate
---------|-----------|-----
EUR      | 10:00     | 1.10
EUR      | 10:00     | 1.11
```

An order at 10:05 has multiple eligible reference rows.

That is an ambiguity in the reference data.

Possible production policies:

```text
deduplicate according to an explicit version rule
choose using an additional business key
fail validation
```

Do not let an ambiguous source silently define financial history.

---

# 46. `map()` vs `merge()`

`Series.map()` is useful for a simple key-to-one-value lookup.

```python
country_lookup = pd.Series(
    {
        "IN": "India",
        "US": "United States",
        "GB": "United Kingdom",
    }
)

orders["country_name"] = (
    orders["country_code"].map(country_lookup)
)
```

The mental model is:

```text
one left key
   ↓
one looked-up value
```

Use `merge` when you need a relational join and multiple right-side attributes.

---

# 47. `map()` Requires a Clear Key-to-Value Contract

This looks simple:

```python
lookup = products.set_index("product_id")["category"]
orders["category"] = orders["product_id"].map(lookup)
```

But first ask:

```text
Is product_id unique in products?
```

If the source has:

```text
P1 → category A
P1 → category B
```

there is no single unambiguous value.

### Production rule

> `map` is simple syntax for a relationship that must already be simple.

---

# 48. `combine_first()`

`combine_first()` is a missing-value fallback, not a relational join.

```python
primary = pd.Series(
    [100, None, 300],
    index=["A", "B", "C"],
)

secondary = pd.Series(
    [10, 20, 30],
    index=["A", "B", "C"],
)

result = primary.combine_first(secondary)
```

Result:

```text
A    100
B     20
C    300
```

The primary values win; missing primary values are filled from the aligned secondary object.

### Difference from merge

```text
merge
→ match records by keys

combine_first
→ fill missing aligned values
```

---

# 49. `merge` vs `map` vs `combine_first`

| Tool | Core question | Typical output | Main assumption |
|---|---|---|---|
| `merge` | Which records correspond? | Joined table | Explicit key relationship |
| `map` | What one value belongs to this key? | One new/updated Series | Clear key → one value mapping |
| `combine_first` | Can a secondary value fill this missing primary value? | Aligned object | Compatible labels/index |

Choose the simplest operation that accurately expresses the relationship.

---

# 50. `concat()` — Stacking and Axis Alignment

`concat` does not primarily ask:

> Which customer belongs to this order?

It asks:

> How should these pandas objects be combined along an axis?

Think:

```text
concat
→ stack or align axes

merge
→ match rows through keys
```

---

# 51. Row-Wise `concat`

Use:

```python
combined = pd.concat(
    [df1, df2],
    axis=0,
)
```

Example:

```python
day_1 = pd.DataFrame(
    {
        "order_id": ["O1", "O2"],
        "amount": [100, 200],
    }
)

day_2 = pd.DataFrame(
    {
        "order_id": ["O3", "O4"],
        "amount": [300, 400],
    }
)

combined = pd.concat(
    [day_1, day_2],
    axis=0,
)
```

Expected records:

```text
O1
O2
O3
O4
```

The original row populations are stacked.

---

# 52. `ignore_index=True`

Daily input files often have local positional indexes such as:

```text
file 1 → 0, 1, 2
file 2 → 0, 1, 2
```

When those indexes have no business meaning:

```python
combined = pd.concat(
    [day_1, day_2],
    ignore_index=True,
)
```

This creates one new positional index for the combined DataFrame.

If the original indexes are meaningful, preserve them instead.

---

# 53. Mismatched Columns in `concat`

Suppose:

```python
day_1 = pd.DataFrame(
    {
        "order_id": ["O1"],
        "amount": [100],
    }
)

day_2 = pd.DataFrame(
    {
        "order_id": ["O2"],
        "amount": [200],
        "country": ["IN"],
    }
)
```

Then:

```python
combined = pd.concat(
    [day_1, day_2],
    ignore_index=True,
)
```

Conceptually:

```text
order_id | amount | country
---------|--------|--------
O1       | 100    | NaN
O2       | 200    | IN
```

This can be valid schema evolution or evidence of an input contract problem.

The pipeline must distinguish the two.

---

# 54. Column-Wise `concat(axis=1)`

Column-wise concatenation aligns on index.

```python
left = pd.DataFrame(
    {"amount": [100, 200]},
    index=["O1", "O2"],
)

right = pd.DataFrame(
    {"currency": ["INR", "USD"]},
    index=["O1", "O3"],
)

result = pd.concat(
    [left, right],
    axis=1,
)
```

Conceptually:

```text
     amount currency
O1    100     INR
O2    200     NaN
O3    NaN     USD
```

This is index alignment, not key-based relational matching.

---

# 55. `concat(axis=1)` Is Not a Replacement for `merge`

If the relationship is:

```text
orders.customer_id
→ customers.customer_id
```

then this:

```python
pd.concat(
    [orders, customers],
    axis=1,
)
```

is normally the wrong operation unless the index alignment itself is the intended relationship.

Use a key-based merge when business keys define identity.

---

# 56. `join()`

`DataFrame.join()` is primarily an index-oriented joining interface.

Example:

```python
customers_indexed = customers.set_index("customer_id")

result = orders.join(
    customers_indexed,
    on="customer_id",
    how="left",
    validate="many_to_one",
)
```

The relationship is:

```text
orders.customer_id
        ↓
customers_indexed.index
```

Use `join()` when index alignment is an intentional part of the design. Use `merge()` when business keys in columns are the clearest expression of the relationship.

---

# 57. `join()` vs `merge()` vs `concat()`

| Operation | Main matching basis | Typical use |
|---|---|---|
| `merge` | Explicit columns and/or indexes | Business-key relationship between tables |
| `join` | Primarily index alignment, with `on=` available | Intentional index-based lookup/alignment |
| `concat` | Axis alignment or stacking | Batches, files, and aligned objects |

Mental model:

```text
Business key in columns?
→ merge()

Intentional index alignment?
→ join()

Stack records?
→ concat(axis=0)

Align columns by index?
→ concat(axis=1)
```

No one operation is universally better. The operation should expose the intended relationship clearly.

---

# 58. SQL Join Comparison

| SQL concept | pandas pattern |
|---|---|
| `INNER JOIN` | `merge(..., how="inner")` |
| `LEFT JOIN` | `merge(..., how="left")` |
| `RIGHT JOIN` | `merge(..., how="right")` |
| `FULL OUTER JOIN` | `merge(..., how="outer")` |
| `CROSS JOIN` | `merge(..., how="cross")` |
| Anti-join | `indicator=True` + `left_only`, or a membership test |
| Semi-join | `isin()` |
| Point-in-time lookup | `merge_asof()` |

Pandas and SQL are conceptually similar for common joins, but they are not identical in every detail. Important differences include null-key behavior, index alignment, output-index behavior, and pandas-specific validation options.

---

# 59. Cardinality Validation Workflow

Use this workflow for production joins:

```text
1. Identify the business key
        ↓
2. Inspect key uniqueness
        ↓
3. Define expected cardinality
        ↓
4. Write the join contract
        ↓
5. Normalize key types and formatting
        ↓
6. Predict result row count
        ↓
7. Perform the join with validate=
        ↓
8. Inspect unmatched rows
        ↓
9. Reconcile row counts and measures
        ↓
10. Publish only when the contract is satisfied
```

This sequence should become automatic for joins that affect important business metrics.

---

# 60. Key Profiling Before a Join

Before joining on a key, inspect it on both sides.

```python
left_null_rate = left["key"].isna().mean()
left_unique = left["key"].nunique()
left_duplicate_rows = left["key"].duplicated().sum()

right_null_rate = right["key"].isna().mean()
right_unique = right["key"].nunique()
right_duplicate_rows = right["key"].duplicated().sum()
```

Ask:

```text
How many rows have no key?
How many distinct keys exist?
How many duplicate observations exist?
Which side should be unique?
```

These are diagnostics, not proof of business-key validity.

---

# 61. Key Frequency Profiles

Frequency tables reveal the relationship more clearly than a single duplicate count.

```python
left_counts = (
    left.groupby("key", dropna=False)
    .size()
)

right_counts = (
    right.groupby("key", dropna=False)
    .size()
)
```

Inspect high-frequency keys:

```python
print(
    left_counts.sort_values(
        ascending=False
    ).head(20)
)

print(
    right_counts.sort_values(
        ascending=False
    ).head(20)
)
```

Use this to identify:

```text
duplicate reference keys
hot keys
unexpected null populations
high-cardinality relationships
```

---

# 62. Checking a Many-to-One Contract

If the relationship is:

```text
orders → customers
```

and the intended cardinality is many-to-one, the right side should have at most one row per key.

```python
customer_counts = (
    customers.groupby(
        "customer_id",
        dropna=False,
    )
    .size()
)

bad_customer_keys = customer_counts.loc[
    customer_counts > 1
]
```

Then:

```python
if not bad_customer_keys.empty:
    raise ValueError(
        "customer_id is not unique in customers"
    )
```

`validate="many_to_one"` is still preferable in the merge because it directly checks the join relationship at execution time.

---

# 63. Join Reconciliation

For an enrichment join, measure before and after.

```python
rows_before = len(orders)
revenue_before = orders["amount"].sum()

enriched = orders.merge(
    customers,
    on="customer_id",
    how="left",
    validate="many_to_one",
)

rows_after = len(enriched)
revenue_after = enriched["amount"].sum()
```

For a genuine many-to-one left enrichment:

```python
assert rows_after == rows_before
```

When the join does not alter transactional values:

```python
assert revenue_after == revenue_before
```

For floating-point arithmetic where exact equality is not appropriate, use a justified tolerance.

---

# 64. Why Revenue Reconciliation Is Powerful

Suppose:

```text
rows_before = 1,000
revenue_before = 500,000
```

and after enrichment:

```text
rows_after = 1,300
revenue_after = 650,000
```

That is an immediate signal that the join changed the transaction population.

Possible causes include:

```text
duplicate right keys
many-to-many relationship
unexpected row filtering
numeric mutation
```

The reconciliation is a safety net. It is not a substitute for cardinality validation.

---

# 65. Why Row Count Alone Is Not Enough

Consider an inner join:

```text
1,000 input rows
1,000 output rows
```

The row count can look healthy even when different rows were removed and other rows were multiplied.

Therefore validate multiple dimensions:

```text
row count
key coverage
cardinality
business measures
schema
```

No single check proves a join is correct.

---

# 66. Join Contracts as Code-Review Artifacts

A join contract makes review concrete.

```text
Join:
Order customer enrichment

Left:
orders — one row per order

Right:
customers — one row per customer

Key:
customer_id

Cardinality:
many-to-one

Type:
left

Expected row count:
len(orders)

Unmatched policy:
retain + report

Measure policy:
amount total unchanged

Validation:
many_to_one

Diagnostics:
indicator=True during development
```

A reviewer can now inspect the code against explicit assumptions.

---

# 67. Production Join Anti-Pattern: No Key Check

Bad:

```python
orders.merge(
    products,
    on="product_id",
)
```

Why it appears reasonable:

```text
same key name
```

Why it is dangerous:

```text
product_id may repeat in products
```

Safer:

```python
orders.merge(
    products[["product_id", "category"]],
    on="product_id",
    how="left",
    validate="many_to_one",
)
```

---

# 68. Production Join Anti-Pattern: Inner Join for Convenience

Bad when all orders must survive:

```python
orders.merge(
    customers,
    on="customer_id",
    how="inner",
)
```

Why it appears reasonable:

```text
no missing customer attributes
```

Why dangerous:

```text
unknown customers disappear
```

Safer:

```text
left join
+
explicit unmatched report
```

---

# 69. Production Join Anti-Pattern: Ignoring Row Counts

Bad:

```python
result = left.merge(
    right,
    on="key",
)
```

with no population check.

Safer:

```python
rows_before = len(left)
result = left.merge(right, on="key")
rows_after = len(result)
```

Then compare the actual result to the join contract.

---

# 70. Production Join Anti-Pattern: Duplicate Dimension Keys

A dimension expected to be:

```text
one row per key
```

may contain:

```text
C1
C1
```

That can multiply every matching fact row.

Do not arbitrarily drop one record unless the business rule says which record wins.

Use:

```python
validate="many_to_one"
```

and repair the source relationship when needed.

---

# 71. Production Join Anti-Pattern: Different Dtypes

Do not assume:

```text
101
```

and:

```text
"101"
```

represent interchangeable join keys.

Normalize according to the canonical identifier definition.

---

# 72. Production Join Anti-Pattern: Outer Join as a Hiding Place

An outer join can expose:

```text
left_only
right_only
both
```

That makes it useful for reconciliation.

It becomes dangerous when the outer result is published without investigating why `left_only` and `right_only` exist.

---

# 73. Production Join Anti-Pattern: Unintended Null Matches

If both sides contain missing keys, pandas can match them.

The safer question is:

```text
Does a missing key represent an entity?
```

Usually, the answer needs an explicit business rule rather than an accidental library default.

---

# 74. Production Join Anti-Pattern: `merge_asof` Without Sorting

A time-distance join requires sorted merge keys.

Correct:

```python
left = left.sort_values(
    "event_time",
    kind="stable",
)

right = right.sort_values(
    "reference_time",
    kind="stable",
)
```

Then:

```python
pd.merge_asof(...)
```

---

# 75. Production Join Anti-Pattern: Wrong As-Of Direction

Requirement:

```text
latest rate known at event time
```

Wrong:

```python
direction="forward"
```

because a future rate can be selected.

Correct for latest-at-or-before semantics:

```python
direction="backward"
```

---

# 76. Production Join Anti-Pattern: Missing Tolerance

Without a freshness boundary, an old reference value may be attached when the business process requires a recent value.

Define:

```python
tolerance=pd.Timedelta("1D")
```

or the appropriate domain-specific window.

---

# 77. Production Join Anti-Pattern: Missing `by`

For multi-entity time data, timestamp proximity is not enough.

Bad:

```python
pd.merge_asof(
    orders,
    rates,
    on="time",
    direction="backward",
)
```

Safer when currency is the partition:

```python
pd.merge_asof(
    orders,
    rates,
    on="time",
    by="currency",
    direction="backward",
)
```

---

# 78. Production Join Anti-Pattern: `map` with Non-Unique Keys

Bad assumption:

```text
product_id → one category
```

while the lookup table actually contains multiple categories for the same product ID.

Validate the lookup relationship first.

---

# 79. Production Join Anti-Pattern: `concat(axis=1)` Instead of `merge`

Bad:

```python
pd.concat(
    [orders, customers],
    axis=1,
)
```

when the business relationship is defined by `customer_id`.

This aligns by index.

Use `merge` for business-key matching.

---

# 80. Production Join Anti-Pattern: Wrong Index with `join()`

Bad:

```python
orders.join(customers)
```

when the current indexes represent row position rather than customer identity.

Correct:

```text
establish the intentional index
or
use a business-key merge
```

---

# 81. Production Join Anti-Pattern: Revenue Changed After Enrichment

If:

```text
revenue_before != revenue_after
```

stop and investigate.

Possible causes:

```text
duplicate right keys
many-to-many expansion
row loss combined with a separate transformation
numeric transformation
```

A revenue reconciliation does not tell you the root cause. It tells you that the contract needs investigation.

---

# 82. Production Join Anti-Pattern: No Join Contract

If an engineer cannot answer:

```text
What cardinality do we expect?
How many rows should result?
What happens to unmatched keys?
What measures must remain unchanged?
```

then the join is not fully specified.

Write the contract before coding.

---

# 83. Join Performance Engineering

Correctness comes first.

After the relationship is correct, consider:

```text
number of rows
number of columns
key cardinality
key representation
duplicate frequency
sort requirements
memory footprint
```

Do not optimize based on a universal rule such as:

```text
"categorical is always faster"
"index join is always faster"
"sorting is always faster"
```

Instead:

> Measure the actual workload.

---

# 84. Reduce Columns Before Joining

If only three reference attributes are required, project them:

```python
customers_small = customers[
    [
        "customer_id",
        "segment",
        "country",
    ]
]

enriched = orders.merge(
    customers_small,
    on="customer_id",
    how="left",
    validate="many_to_one",
)
```

Potential advantages include lower memory traffic and a narrower result.

This is a workload-dependent optimization, not a guaranteed speedup.

---

# 85. Pre-Filtering Before a Join

Pre-filtering can reduce the amount of data entering a join.

For example, if the business requirement really is:

```text
only active products
```

then:

```python
active_products = products.loc[
    products["status"].eq("active")
]
```

may be joined instead.

But filtering is a semantic operation.

If inactive products should remain enrichable, this optimization changes the result and is therefore wrong.

---

# 86. Categorical Join Keys

Categoricals can be useful for repeated low-cardinality labels such as:

```text
country
region
channel
status
```

Potential benefits can include reduced memory and different join behavior depending on the workload.

But:

```text
category ≠ automatic speedup
```

Conversion costs time and memory, and high-cardinality data may not benefit.

Measure the actual workload.

---

# 87. Sorted Indexes and Intentional Alignment Structures

Indexes are useful when index alignment is part of the data model.

Example:

```python
customers_indexed = customers.set_index(
    "customer_id"
)

result = orders.join(
    customers_indexed,
    on="customer_id",
    how="left",
)
```

This may be clear and useful when the right index is intentionally the lookup structure.

Do not assume index-based operations are universally faster than `merge`.

Measure end-to-end behavior.

---

# 88. Wide Result Memory

A join can be expensive because of the number of columns as well as row count.

Compare:

```text
10 million rows + 3 extra columns
```

with:

```text
10 million rows + 60 extra columns
```

The second result can require substantially more memory.

Projection is therefore both:

```text
schema design
+
performance engineering
```

---

# 89. High-Cardinality Keys

High-cardinality keys can require substantial memory and processing work.

Examples:

```text
UUID-like identifiers
transaction IDs
event IDs
```

High cardinality is not a defect. It may be required by the business model.

The correct engineering question is:

> Is this key representation and join strategy appropriate for the data volume and distribution?

---

# 90. Duplicate Hot Keys

A few heavily repeated keys can dominate join cost and output size.

Inspect:

```python
right_counts = (
    right.groupby("key")
    .size()
    .sort_values(ascending=False)
)

print(right_counts.head(20))
```

This can expose hot keys that require special business investigation.

---

# 91. Benchmarking Joins

A basic benchmark:

```python
from time import perf_counter

start = perf_counter()

result = left.merge(
    right,
    on="key",
    how="left",
    validate="many_to_one",
)

elapsed = perf_counter() - start

print(f"{elapsed:.3f} seconds")
```

A meaningful benchmark holds constant:

```text
same input data
same output semantics
same columns
same cardinality
same environment
```

Repeat measurements where practical.

Record:

```text
row count
unique key count
duplicate profile
join type
columns joined
runtime
peak memory when available
Python version
pandas version
machine/environment
```

Never fabricate a benchmark result.

---


# 92. Benchmarking on 5,000,000 Rows

For a realistic performance experiment, use at least **5,000,000 rows** and a defined key cardinality. Do not write a benchmark number into the chapter; the learner must measure it on the local machine.

Example setup:

```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

n_orders = 5_000_000
n_customers = 100_000

orders = pd.DataFrame(
    {
        "customer_id": rng.integers(
            0,
            n_customers,
            size=n_orders,
        ),
        "amount": rng.random(n_orders) * 1000,
    }
)

customers = pd.DataFrame(
    {
        "customer_id": np.arange(n_customers),
        "segment": np.where(
            np.arange(n_customers) % 2 == 0,
            "A",
            "B",
        ),
    }
)
```

Benchmark the validated many-to-one enrichment:

```python
from time import perf_counter

start = perf_counter()

enriched = orders.merge(
    customers,
    on="customer_id",
    how="left",
    validate="many_to_one",
)

elapsed_seconds = perf_counter() - start

print(f"rows={len(orders):,}")
print(f"customers={len(customers):,}")
print(f"elapsed_seconds={elapsed_seconds:.6f}")
```

Then record actual results in a local benchmark note:

```text
rows
right-side key count
join type
columns joined
elapsed time
peak memory, if measured
Python version
pandas version
hardware/environment
```

Repeat the experiment for a narrower projected right table and, where relevant, an intentional categorical-key representation. Compare only workloads that preserve the same semantics.

> Never report a timing as a chapter fact unless it was actually measured in the environment being discussed.

---

# 92. Benchmark: Projection and Key Representation

A useful experiment is to compare:

```text
full reference table
```

against:

```text
projected reference table
```

and, where justified:

```text
intentional categorical representation
```

The comparison must preserve:

```text
same keys
same cardinality
same business output
```

Then measure:

```text
runtime
peak memory
output size
```

---

# 93. Benchmark: Avoiding an Accidental Many-to-Many Join

Do not benchmark:

```text
one correct many-to-one join
```

against:

```text
an unintended many-to-many join
```

and call the latter "faster" or "slower."

Those are different workloads with different semantics.

First make the relationships equivalent, then compare implementation choices.

---

# 94. Performance and Correctness Together

Optimization can change semantics.

Examples:

```text
pre-filtering
null-key removal
deduplication
key conversion
aggregation before join
```

After optimization, re-check:

```text
row count
key coverage
business measures
schema
null behavior
```

The correct sequence is:

```text
correctness
→ tests
→ benchmark
→ optimize
→ tests again
```

---

# 95. Join Risk Matrix

| Relationship / operation | Typical use | Main risk | Recommended control |
|---|---|---|---|
| One-to-one | entity to unique profile | unexpected duplicate key | `validate="one_to_one"` |
| Many-to-one | facts to dimension | duplicate right key | `validate="many_to_one"` |
| One-to-many | entity to child rows | intentional row expansion | `validate="one_to_many"` + row-count expectations |
| Many-to-many | bridge relationships | multiplicative explosion | explicit design + reconciliation |
| Inner | matched population | row loss | coverage checks |
| Left | enrichment | missing matches / right duplicates | `validate` + unmatched report |
| Outer | source reconciliation | mismatch rows ignored | inspect `_merge` |
| Cross | scenario matrix | Cartesian explosion | calculate `len(left) × len(right)` |
| As-of | point-in-time enrichment | stale/wrong reference | sort + `by` + direction + tolerance |

---

# 96. MERGE / JOIN / CONCAT Decision Guide

```text
Do I need to match records by a business key?
        |
       YES
        ↓
      merge()

Do I primarily want intentional index-based alignment?
        |
       YES
        ↓
      join()

Do I want to stack rows or files?
        |
       YES
        ↓
     concat(axis=0)

Do I want to align columns by index?
        |
       YES
        ↓
     concat(axis=1)

Do I need nearest / previous / next time matching?
        |
       YES
        ↓
   merge_asof()
```

The operation should describe the relationship rather than merely being the first API remembered.

---

# 97. Anti-Join / Semi-Join Cheat Sheet

### Anti-join

```python
merged = left.merge(
    right[["key"]],
    on="key",
    how="left",
    indicator=True,
)

anti = merged.loc[
    merged["_merge"].eq("left_only")
]
```

### Semi-join

```python
semi = left.loc[
    left["key"].isin(
        right["key"]
    )
]
```

---


# 97. SQL Translation Practice — 10 Realistic Join Queries

Use these exercises to translate relational reasoning into pandas. Before reading the pandas answer, predict the output row count from the SQL relationship.

## SQL Translation 1 — Inner customer enrichment

### SQL

```sql
SELECT
    o.order_id,
    o.customer_id,
    c.segment
FROM orders AS o
INNER JOIN customers AS c
    ON o.customer_id = c.customer_id;
```

### Pandas

```python
result = orders.merge(
    customers[["customer_id", "segment"]],
    on="customer_id",
    how="inner",
)
```

### Expected shape

One result row per matching equality pair. If the customer key is unique on the right, this is one row per matched order.

### Important semantic difference

Pandas can match null keys to null keys, unlike ordinary SQL equality semantics. Check null-key policy explicitly.

---

## SQL Translation 2 — Left enrichment

### SQL

```sql
SELECT
    o.order_id,
    o.amount,
    c.segment
FROM orders AS o
LEFT JOIN customers AS c
    ON o.customer_id = c.customer_id;
```

### Pandas

```python
result = orders.merge(
    customers[["customer_id", "segment"]],
    on="customer_id",
    how="left",
    validate="many_to_one",
)
```

### Expected shape

Exactly `len(orders)` when the right-side customer key is unique.

### Important semantic difference

`validate="many_to_one"` turns the expected relational shape into a runtime check.

---

## SQL Translation 3 — Full outer reconciliation

### SQL

```sql
SELECT
    c.customer_id AS customer_id,
    c.segment,
    o.order_id
FROM customers AS c
FULL OUTER JOIN orders AS o
    ON c.customer_id = o.customer_id;
```

### Pandas

```python
result = customers.merge(
    orders,
    on="customer_id",
    how="outer",
    indicator=True,
)
```

### Expected shape

Driven by key matches plus unmatched rows, including repeated keys where present.

### Important semantic difference

Pandas `_merge` directly labels `left_only`, `right_only`, and `both`, making reconciliation diagnostics convenient.

---

## SQL Translation 4 — Cross join

### SQL

```sql
SELECT *
FROM countries
CROSS JOIN scenarios;
```

### Pandas

```python
result = countries.merge(
    scenarios,
    how="cross",
)
```

### Expected shape

```text
len(countries) × len(scenarios)
```

### Important semantic difference

A pandas cross merge does not accept ordinary key specifications. Treat the output-size calculation as a required pre-check.

---

## SQL Translation 5 — Anti-join

### SQL

```sql
SELECT o.*
FROM orders AS o
LEFT JOIN customers AS c
    ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;
```

### Pandas

```python
diagnostic = orders.merge(
    customers[["customer_id"]],
    on="customer_id",
    how="left",
    indicator=True,
)

result = diagnostic.loc[
    diagnostic["_merge"].eq("left_only")
]
```

### Expected shape

The number of unmatched left records, assuming the right-side key column is used only as an existence check.

### Important semantic difference

Using a deduplicated right key set is often appropriate for an existence query because the goal is not right-side row expansion.

---

## SQL Translation 6 — Semi-join

### SQL

```sql
SELECT o.*
FROM orders AS o
WHERE EXISTS (
    SELECT 1
    FROM customers AS c
    WHERE c.customer_id = o.customer_id
);
```

### Pandas

```python
result = orders.loc[
    orders["customer_id"].isin(
        customers["customer_id"]
    )
]
```

### Expected shape

At most `len(orders)` rows.

### Important semantic difference

The pandas `isin` pattern does not add customer columns and therefore expresses the existence test directly.

---

## SQL Translation 7 — Composite-key left join

### SQL

```sql
SELECT *
FROM orders AS o
LEFT JOIN customers AS c
    ON o.country = c.country
   AND o.customer_id = c.customer_id;
```

### Pandas

```python
result = orders.merge(
    customers,
    on=["country", "customer_id"],
    how="left",
    validate="many_to_one",
)
```

### Expected shape

Exactly `len(orders)` when the complete composite key is unique on the right.

### Important semantic difference

Do not replace a complete business identity with a shorter key merely because it is convenient.

---

## SQL Translation 8 — Point-in-time lookup

SQL implementations vary by database, but the business requirement is often expressed as a latest-prior reference lookup.

### SQL concept

```sql
SELECT
    o.order_id,
    o.currency,
    o.order_time,
    r.rate
FROM orders AS o
LEFT JOIN fx_rates AS r
    ON r.currency = o.currency
   AND r.rate_time = (
       SELECT MAX(r2.rate_time)
       FROM fx_rates AS r2
       WHERE r2.currency = o.currency
         AND r2.rate_time <= o.order_time
   );
```

### Pandas

```python
result = pd.merge_asof(
    orders.sort_values("order_time"),
    fx_rates.sort_values("rate_time"),
    left_on="order_time",
    right_on="rate_time",
    by="currency",
    direction="backward",
)
```

### Expected shape

One result row per left order, with missing rate fields when no eligible prior rate exists.

### Important semantic difference

The pandas operation depends on correctly sorted time keys and explicit `direction` semantics.

---

## SQL Translation 9 — Latest version enrichment

A common SQL pattern is to select the latest reference record per business key before joining.

### SQL concept

```sql
WITH latest_customer AS (
    SELECT *
    FROM (
        SELECT
            c.*,
            ROW_NUMBER() OVER (
                PARTITION BY customer_id
                ORDER BY updated_at DESC
            ) AS rn
        FROM customer_history AS c
    ) AS x
    WHERE rn = 1
)
SELECT
    o.order_id,
    o.amount,
    c.segment
FROM orders AS o
LEFT JOIN latest_customer AS c
    ON o.customer_id = c.customer_id;
```

### Pandas pattern

```python
latest_customer = (
    customer_history
    .sort_values(
        ["customer_id", "updated_at"],
        ascending=[True, False],
        kind="stable",
    )
    .drop_duplicates(
        "customer_id",
        keep="first",
    )
)

result = orders.merge(
    latest_customer,
    on="customer_id",
    how="left",
    validate="many_to_one",
)
```

### Expected shape

Exactly `len(orders)` when the latest-reference result is unique by `customer_id`.

### Important semantic difference

The important design decision is the version-selection rule. Do not deduplicate arbitrarily.

---

## SQL Translation 10 — Left join plus key-coverage diagnostics

### SQL concept

```sql
SELECT
    o.customer_id,
    CASE
        WHEN c.customer_id IS NULL THEN 'unmatched'
        ELSE 'matched'
    END AS match_status
FROM orders AS o
LEFT JOIN customers AS c
    ON o.customer_id = c.customer_id;
```

### Pandas

```python
result = orders.merge(
    customers[["customer_id"]],
    on="customer_id",
    how="left",
    indicator=True,
    validate="many_to_one",
)

result["match_status"] = result["_merge"].map(
    {
        "left_only": "unmatched",
        "both": "matched",
    }
)
```

### Expected shape

Exactly `len(orders)` for a valid many-to-one left enrichment.

### Important semantic difference

The temporary `_merge` column is pandas-specific and can be removed after the diagnostic report is produced.

### Translation habit

For each query, write down:

```text
What is the preserved population?
Which key defines matching?
What is the expected cardinality?
Can a key repeat?
What should happen to unmatched rows?
What should the output row count be?
```

Then implement.

---

# 98. Hands-On Exercise — `enrich_orders.py`

> **Do not create `enrich_orders.py` as part of this task.** This section is the complete implementation specification for the learner.

## Exercise goal

Build a production-oriented order enrichment flow demonstrating:

```text
many-to-one join
cardinality validation
unmatched-key diagnostics
row-count reconciliation
revenue reconciliation
point-in-time FX enrichment
anti-join
semi-join
row-wise concat
schema alignment
```

Every join in the exercise must start with a written join contract.

---

## Exercise data

### `orders`

Use columns:

```text
order_id
customer_id
country
currency
order_time
product_id
amount
```

### `customers`

Use columns:

```text
customer_id
customer_name
segment
```

### `products`

Use columns:

```text
product_id
product_name
category
```

### `fx_rates`

Use columns:

```text
currency
rate_time
rate_to_usd
```

---

# 99. Exercise Task 1 — Orders → Customers

Goal:

```text
enrich orders with customer attributes
```

Expected cardinality:

```text
many-to-one
```

### Join contract

```text
Left: orders
Right: customers
Key: customer_id
Cardinality: many-to-one
Type: left
Expected row count: exactly len(orders)
Unmatched orders: retain + report
Revenue: unchanged
Validation: many_to_one
```

### Required operation

```python
diagnostic = orders.merge(
    customers,
    on="customer_id",
    how="left",
    validate="many_to_one",
    indicator=True,
)
```

### Unknown customers

```python
unknown_customer_orders = diagnostic.loc[
    diagnostic["_merge"].eq("left_only")
]
```

### Required checks

```python
rows_before = len(orders)
rows_after = len(diagnostic)

assert rows_after == rows_before
```

Also calculate:

```python
unknown_count = len(unknown_customer_orders)
```

### Prediction questions

Before running:

```text
How many duplicate customer IDs exist in customers?
How many order customer IDs are unknown?
How many result rows should exist?
Should revenue change?
```

---

# 100. Exercise Task 2 — Duplicate Products

Create a deliberately broken product table:

```python
products_bad = pd.DataFrame(
    {
        "product_id": ["P1", "P1", "P2"],
        "product_name": [
            "Widget",
            "Widget - old",
            "Gadget",
        ],
    }
)
```

Suppose orders contain multiple P1 rows.

Calculate first:

```python
revenue_before = orders["amount"].sum()
rows_before = len(orders)
```

Then deliberately demonstrate the bad enrichment:

```python
broken = orders.merge(
    products_bad,
    on="product_id",
    how="left",
)
```

Calculate:

```python
rows_after = len(broken)
revenue_after = broken["amount"].sum()
```

### Required explanation

Show:

```text
which key is duplicated
left count for that key
right count for that key
m × n result contribution
row-count change
revenue change
```

Then catch the problem:

```python
orders.merge(
    products_bad,
    on="product_id",
    how="left",
    validate="many_to_one",
)
```

This should fail because the right-side key is not unique.

---

# 101. Exercise Task 3 — Orders → Daily FX Rates

Goal:

```text
convert each order to USD
using the latest acceptable FX rate at order time
```

### Join contract

```text
Left: orders
Right: fx_rates
Time key: order_time ↔ rate_time
Partition key: currency
Direction: backward
Tolerance: explicitly defined
Meaning: latest known acceptable rate
Unmatched rate: explicitly handled
```

### Required sorting

```python
orders_sorted = orders.sort_values(
    "order_time",
    kind="stable",
)

rates_sorted = fx_rates.sort_values(
    "rate_time",
    kind="stable",
)
```

### Required operation

```python
enriched_fx = pd.merge_asof(
    orders_sorted,
    rates_sorted,
    left_on="order_time",
    right_on="rate_time",
    by="currency",
    direction="backward",
    tolerance=pd.Timedelta("1D"),
)
```

Adjust the tolerance to the business scenario you define, and document it.

### Required checks

Verify:

```text
time keys are sorted
currency partitioning is correct
direction is correct
tolerance is intentional
unmatched orders are identified
```

Then calculate:

```python
enriched_fx["amount_usd"] = (
    enriched_fx["amount"]
    * enriched_fx["rate_to_usd"]
)
```

Do not invent an FX rate for unmatched rows.

Choose one documented policy:

```text
leave missing
quarantine
fail the pipeline
```

---

# 102. Exercise Task 4 — Customers With No Orders

Treat customers as the left population.

Use an anti-join to find customers whose IDs do not appear in orders.

```python
customer_order_check = customers.merge(
    orders[["customer_id"]].drop_duplicates(),
    on="customer_id",
    how="left",
    indicator=True,
)

customers_without_orders = (
    customer_order_check.loc[
        customer_order_check["_merge"].eq("left_only")
    ]
)
```

The `drop_duplicates()` here is intentional because the question is existence, not order count.

---

# 103. Exercise Task 5 — Semi-Join

Find orders whose customer IDs exist in the customer table:

```python
known_customer_orders = orders.loc[
    orders["customer_id"].isin(
        customers["customer_id"]
    )
]
```

This keeps only left-side orders and does not add customer columns.

Explain the difference:

```text
semi-join
→ does the customer exist?

merge
→ which customer attributes should be attached?
```

---

# 104. Exercise Task 6 — Concatenate 30 Daily Files

Create/specify 30 daily DataFrames representing:

```text
day 01
...
day 30
```

Some days should use:

```text
order_id
customer_id
amount
```

while later days add a legitimate new field such as:

```text
country
currency
```

Concatenate:

```python
combined = pd.concat(
    daily_frames,
    axis=0,
    ignore_index=True,
)
```

Verify:

```text
30 inputs processed
expected columns exist
missing columns are handled intentionally
new index is created
row counts reconcile
```

Do not treat schema drift as automatically valid or automatically invalid. Compare it to the defined input contract.

---

# 105. Exercise Revenue Reconciliation

For an enrichment-only customer join:

```python
revenue_before = orders["amount"].sum()

customer_enriched = orders.merge(
    customers,
    on="customer_id",
    how="left",
    validate="many_to_one",
)

revenue_after = customer_enriched["amount"].sum()
```

Then, where exact equality is appropriate:

```python
assert revenue_after == revenue_before
```

Also track:

```text
rows_before
rows_after
unknown_customers
duplicate_customer_keys
duplicate_product_keys
```

For floating-point contexts, use a justified tolerance rather than blindly assuming exact equality is always appropriate.

---

# 106. Exercise: Join Contract Before Every Join

For each join in Tasks 1–3, write:

```text
Join:
Left:
Right:
Left grain:
Right grain:
Key(s):
Cardinality:
Join type:
Expected rows:
Unmatched policy:
Null-key policy:
Measure policy:
Validation:
Diagnostics:
Reconciliation:
```

Do not execute until the contract is written.

---

# 107. Exercise: Required Tests

The later implementation should prove:

```text
customer join is many-to-one
customer join preserves order rows
unknown customers are reported
duplicate product key causes validation failure
bad product enrichment changes rows/revenue in the demonstration
FX matching respects currency
FX direction matches the business rule
FX tolerance can produce unmatched rows
anti-join finds customers without orders
semi-join retains only known-customer orders
30 daily frames concatenate correctly
schema differences are handled intentionally
revenue reconciliation passes for valid enrichment
```

---

# 108. Debugging Framework

When a join result looks wrong, do not immediately change `how=` until you know what failed.

Use this sequence:

```text
1. What does one left row represent?
2. What does one right row represent?
3. What is the exact key?
4. Is the key unique where expected?
5. What cardinality did we expect?
6. What row count did we predict?
7. What row count did we get?
8. Which keys are unmatched?
9. Are nulls involved?
10. Are dtypes/formatting consistent?
11. Did a composite key get reduced to one column?
12. Is time-aware matching required?
13. Did business measures reconcile?
```

---

# 109. Debugging Case 1 — Wrong Key

### Buggy

```python
orders.merge(
    customers,
    on="country",
)
```

### Expected

Customer enrichment.

### Actual

Customers are matched by country.

### Root cause

The business relationship was expressed with the wrong column.

### Correct

```python
orders.merge(
    customers,
    on="customer_id",
    how="left",
    validate="many_to_one",
)
```

### Prevention

State the business key in the join contract.

---

# 110. Debugging Case 2 — Wrong `how=`

### Buggy

```python
orders.merge(
    customers,
    on="customer_id",
    how="inner",
)
```

### Expected

Every order survives.

### Actual

Orders with unknown customers disappear.

### Root cause

An inner join was selected for an enrichment problem.

### Correct

```text
left join + unmatched-key report
```

### Prevention

Write the unmatched-row policy before coding.

---

# 111. Debugging Case 3 — Row Loss

### Symptom

```text
rows_before = 1,000
rows_after  = 920
```

### Root cause candidates

```text
inner join
unmatched keys
bad key normalization
incorrect filters
```

### Inspection

```python
diagnostic = orders.merge(
    customers[["customer_id"]],
    on="customer_id",
    how="left",
    indicator=True,
)

print(
    diagnostic["_merge"].value_counts()
)
```

### Prevention

Make row-count behavior part of the contract.

---

# 112. Debugging Case 4 — Row Multiplication

### Symptom

```text
orders = 1,000 rows
result = 1,450 rows
```

### Root cause

The right-side key may be duplicated.

### Inspection

```python
right_counts = (
    customers.groupby("customer_id")
    .size()
)

print(
    right_counts.loc[right_counts > 1]
)
```

### Correct response

Determine whether the relationship is actually one-to-many or whether the dimension is invalid.

### Prevention

Use `validate="many_to_one"` when many-to-one is the intended relationship.

---

# 113. Debugging Case 5 — Many-to-Many Explosion

### Symptom

A result is much larger than expected.

### Inspection

```python
left_counts = left.groupby("key").size()
right_counts = right.groupby("key").size()
```

For a suspicious key:

```text
left_count × right_count
```

### Correct response

Determine whether many-to-many is valid. If not, identify and fix the relationship before proceeding.

---

# 114. Debugging Case 6 — Missing `validate=`

### Symptom

A join succeeds but the expected relationship was violated.

### Root cause

The assumption existed only in human reasoning.

### Correct

```python
result = orders.merge(
    customers,
    on="customer_id",
    how="left",
    validate="many_to_one",
)
```

### Prevention

Use `validate=` for important production joins whenever the relationship can be stated.

---

# 115. Debugging Case 7 — Null-Key Match

### Symptom

Records with missing keys unexpectedly receive values from records with missing keys on the other side.

### Root cause

Pandas merge can match null keys.

### Correct

Define and implement an explicit null-key policy.

### Prevention

Add a test with missing keys on both sides.

---

# 116. Debugging Case 8 — Integer vs String Key

### Symptom

Keys that look equivalent do not match.

### Inspection

```python
print(left["key"].dtype)
print(right["key"].dtype)
```

### Correct

Normalize to a documented canonical representation.

### Prevention

Validate key dtypes before the join.

---

# 117. Debugging Case 9 — Whitespace

### Symptom

```text
"C001"
```

does not match:

```text
" C001 "
```

### Inspection

```python
print(repr(left.loc[0, "key"]))
print(repr(right.loc[0, "key"]))
```

### Correct

```python
left["key"] = (
    left["key"].astype("string").str.strip()
)

right["key"] = (
    right["key"].astype("string").str.strip()
)
```

when whitespace is not business-significant.

---

# 118. Debugging Case 10 — Case Differences

### Symptom

```text
"IN"
```

does not match:

```text
"in"
```

### Correct

Normalize according to the defined code system.

### Prevention

Keep key normalization in a tested transformation step.

---

# 119. Debugging Case 11 — Incomplete Composite Key

### Symptom

Records appear to match across entities.

### Root cause

Only one part of a composite identity was used.

### Correct

```python
orders.merge(
    customers,
    on=["country", "customer_id"],
    how="left",
)
```

when those two fields together define identity.

### Prevention

Document key grain explicitly.

---

# 120. Debugging Case 12 — Timestamp Equality Instead of As-Of Logic

### Buggy

```python
orders.merge(
    rates,
    left_on="order_time",
    right_on="rate_time",
)
```

### Expected

Latest acceptable prior rate.

### Root cause

Equality matching was used for a time-distance relationship.

### Correct

```python
pd.merge_asof(
    orders.sort_values("order_time"),
    rates.sort_values("rate_time"),
    left_on="order_time",
    right_on="rate_time",
    direction="backward",
)
```

---

# 121. Debugging Case 13 — `merge_asof` Not Sorted

### Symptom

The as-of join fails because the merge key is not correctly ordered.

### Correct

```python
orders = orders.sort_values(
    "order_time",
    kind="stable",
)

rates = rates.sort_values(
    "rate_time",
    kind="stable",
)
```

before the operation.

### Prevention

Make sorting part of the function that performs point-in-time enrichment.

---

# 122. Debugging Case 14 — Wrong `direction`

### Symptom

A future reference value is attached to a historical event.

### Root cause

`direction="forward"` was used when latest-known semantics were required.

### Correct

```python
direction="backward"
```

for the latest reference record at or before the event.

---

# 123. Debugging Case 15 — Wrong `tolerance`

### Symptom

A stale rate is accepted.

### Root cause

Tolerance was absent or too broad.

### Correct

Set a domain-appropriate tolerance and test an out-of-window event.

---

# 124. Debugging Case 16 — Missing `by`

### Symptom

An event receives a rate belonging to another currency/entity.

### Root cause

Time proximity was evaluated globally rather than inside the correct entity partition.

### Correct

```python
by="currency"
```

or the appropriate entity key.

---

# 125. Debugging Case 17 — `map` with Non-Unique Lookup

### Symptom

The lookup table contains multiple values for one key.

### Root cause

The key-to-one-value mapping contract was violated.

### Correct

Validate the lookup key or use a real relational join if the relationship is not one-to-one.

---

# 126. Debugging Case 18 — `concat(axis=1)` Used as a Join

### Symptom

Attributes line up by row position rather than business identity.

### Root cause

Column-wise concatenation aligns on index.

### Correct

Use `merge` when keys define the relationship.

---

# 127. Debugging Case 19 — Unexpected `concat` Columns

### Symptom

New columns contain many missing values.

### Root cause

Input files had different schemas.

### Correct response

Determine whether this is legitimate schema evolution or invalid input.

---

# 128. Debugging Case 20 — `join()` on the Wrong Index

### Symptom

Values appear attached to the wrong entity.

### Root cause

The index represented file position instead of the intended key.

### Correct

Use an explicit key-based merge or establish the correct index first.

---

# 129. Debugging Case 21 — Revenue Changed

### Symptom

```text
revenue_before != revenue_after
```

### Inspection

```text
rows before/after
right-side duplicate keys
unmatched keys
numeric transformations
```

### Prevention

Make measure reconciliation a standard enrichment check.

---

# 130. Debugging Case 22 — Row Count Not Reconciled

### Symptom

Nobody knows whether a change is intended.

### Correct

Record:

```python
rows_before = len(left)
rows_after = len(result)
```

and compare with the contract.

---

# 131. Debugging Case 23 — Outer Join Hides Problems

### Symptom

The result contains every key, so the team assumes the data is healthy.

### Root cause

`left_only` and `right_only` populations were not inspected.

### Correct

```python
result["_merge"].value_counts()
```

### Prevention

Treat mismatch populations as diagnostics.

---

# 132. Debugging Case 24 — Unexpected Suffixes

### Symptom

```text
status_x
status_y
```

### Root cause

Both inputs contain an overlapping non-key column.

### Correct

Use:

```python
suffixes=("_order", "_customer")
```

or project the unnecessary column out.

---

# 133. Debugging Case 25 — Cross Join Too Large

### Symptom

Memory usage or output size grows unexpectedly.

### Root cause

Cartesian product.

### Correct reasoning

Before the join:

```text
expected rows = len(left) × len(right)
```

If that number is unacceptable, the operation itself may be wrong for the workload.

---

# 134. Testing Strategy with pytest

Join tests should prove **your relationship assumptions**, not merely that pandas executes a function call.

Start with tiny deterministic fixtures whose correct results can be calculated by hand.

---

## 134.1 Basic join tests

Cover:

```text
inner
left
right
outer
cross
```

Example:

```python
def test_left_join_preserves_rows_when_right_key_is_unique():
    result = left.merge(
        right,
        on="key",
        how="left",
        validate="many_to_one",
    )

    assert len(result) == len(left)
```

This test is meaningful because the cardinality contract is also enforced.

---

## 134.2 Test `on=`

Create matching key columns with the same name:

```python
result = orders.merge(
    customers,
    on="customer_id",
    how="left",
)
```

Assert the expected rows and attributes.

---

## 134.3 Test `left_on=` / `right_on=`

Use different key names:

```python
result = orders.merge(
    customers,
    left_on="customer_id",
    right_on="id",
    how="left",
)
```

Verify the intended records match.

---

## 134.4 Test suffixes

```python
result = left.merge(
    right,
    on="key",
    suffixes=("_left", "_right"),
)

assert "status_left" in result.columns
assert "status_right" in result.columns
```

---

## 134.5 Test cardinality

Create fixtures for:

```text
one-to-one
one-to-many
many-to-one
many-to-many
```

Then use the corresponding `validate=` setting.

---

## 134.6 Test validation failure

For a many-to-one relationship:

```python
import pytest


def test_many_to_one_rejects_duplicate_right_keys():
    with pytest.raises(ValueError):
        orders.merge(
            customers_bad,
            on="customer_id",
            how="left",
            validate="many_to_one",
        )
```

For a production codebase, prefer the specific exception type exposed by the pandas version you pin, rather than a broad exception, when stable project behavior requires it.

The important behavior is:

```text
duplicate right key
→ cardinality contract fails
```

---

## 134.7 Test row count

For a controlled one-to-one fixture:

```python
assert len(result) == len(left)
```

For a controlled many-to-many fixture, calculate the expected multiplicative result first.

---

## 134.8 Test `indicator=True`

```python
result = left.merge(
    right,
    on="key",
    how="outer",
    indicator=True,
)

assert "_merge" in result.columns
assert set(result["_merge"].astype(str)) <= {
    "left_only",
    "right_only",
    "both",
}
```

---

## 134.9 Test anti-join

Given known input keys, assert the exact unmatched set:

```python
anti = result.loc[
    result["_merge"].eq("left_only")
]

assert set(anti["key"]) == {"C9", "C10"}
```

Exact expected sets are more useful than merely testing that an anti-join is non-empty.

---

## 134.10 Test semi-join

```python
semi = left.loc[
    left["key"].isin(right["key"])
]
```

Verify:

```text
only matching left keys remain
no right attributes were introduced
```

---

# 135. Key-Hygiene Tests

Test normalization independently from the join.

Examples:

```text
integer vs string
whitespace
case
composite keys
```

A normalization helper might be tested with:

```python

def normalize_code(values: pd.Series) -> pd.Series:
    return (
        values
        .astype("string")
        .str.strip()
        .str.upper()
    )
```

The function should only normalize rules that are actually part of the business contract.

---

# 136. Testing pandas Null-Key Behavior

Include a fixture with missing keys on both sides:

```python
left = pd.DataFrame({"key": ["A", None]})
right = pd.DataFrame({"key": ["A", None]})

result = left.merge(
    right,
    on="key",
    how="inner",
)
```

Then assert the behavior your pipeline expects.

The purpose is to prevent future developers from assuming ordinary SQL `NULL = NULL` semantics.

---

# 137. Testing `merge_asof`

Create hand-computable timestamps and test:

```text
backward
forward
nearest
by
tolerance
sorted inputs
```

Example:

```python
result = pd.merge_asof(
    orders.sort_values("order_time"),
    rates.sort_values("rate_time"),
    left_on="order_time",
    right_on="rate_time",
    by="currency",
    direction="backward",
    tolerance=pd.Timedelta("1D"),
)
```

Test exact expected rate assignments.

---

# 138. Testing `concat`

Cover:

```text
row-wise concat
column-wise concat
mismatched columns
ignore_index=True
```

Example:

```python
combined = pd.concat(
    [day_1, day_2],
    ignore_index=True,
)

assert len(combined) == len(day_1) + len(day_2)
```

---

# 139. Testing `join()`

Test that the intended index is actually the relationship key.

```python
customers_indexed = customers.set_index(
    "customer_id"
)

result = orders.join(
    customers_indexed,
    on="customer_id",
    how="left",
    validate="many_to_one",
)
```

Do not rely on index position accidentally matching business identity.

---

# 140. Testing `map()`

Create a unique lookup:

```python
lookup = pd.Series(
    ["India", "United States"],
    index=["IN", "US"],
)

result = orders["country"].map(lookup)
```

Verify known and unknown keys separately.

---

# 141. Testing `combine_first()`

```python
primary = pd.Series(
    [100, None],
    index=["A", "B"],
)

secondary = pd.Series(
    [10, 20],
    index=["A", "B"],
)

result = primary.combine_first(secondary)
```

Assert:

```text
primary non-null wins
primary null uses secondary
```

---

# 142. Reconciliation Tests

For enrichment:

```python
rows_before = len(orders)
revenue_before = orders["amount"].sum()

result = orders.merge(
    customers,
    on="customer_id",
    how="left",
    validate="many_to_one",
)

assert len(result) == rows_before
assert result["amount"].sum() == revenue_before
```

Add an appropriate floating-point tolerance when the data and operation require it.

---

# 143. Edge Cases

Production testing should cover unusual populations explicitly.

---

## 143.1 Empty left DataFrame

For a left join:

```text
left = 0 rows
right = populated
```

expected population:

```text
0 rows
```

The output schema should still be predictable.

---

## 143.2 Empty right DataFrame

For a left join:

```text
left = populated
right = 0 rows
```

expected:

```text
all left rows survive
right columns are missing
```

provided the schemas are valid for the operation.

---

## 143.3 Both sides empty

Expected:

```text
0 rows
```

with a known schema.

---

## 143.4 All keys unmatched

Inner join:

```text
0 rows
```

Left join:

```text
all left rows
right attributes missing
```

---

## 143.5 All keys matched

Useful as the baseline for row-count and measure reconciliation.

---

## 143.6 Duplicate key only on the right

For a many-to-one contract:

```text
validation must fail
```

unless the relationship is intentionally changed.

---

## 143.7 Duplicate key only on the left

Often valid for:

```text
many orders → one customer
```

Do not treat every repeated left key as an error.

---

## 143.8 Duplicates on both sides

Use:

```text
left_count × right_count
```

and predict the result before execution.

---

## 143.9 Null keys on both sides

Pandas can match them.

Test the explicit null policy.

---

## 143.10 Null key on only one side

No null-to-null match can occur, but the overall result still depends on the join type.

---

## 143.11 Mixed dtypes

Test that the canonical normalization step makes both sides compatible without losing identifier information.

---

## 143.12 Whitespace differences

Test both normalized and unnormalized behavior so future changes cannot silently alter key coverage.

---

## 143.13 Case differences

Test code normalization only where case is not semantically meaningful.

---

## 143.14 Composite-key missing component

A missing component can make the intended relationship impossible to establish.

Do not silently fall back to a partial key.

---

## 143.15 Empty cross join side

```text
0 × N = 0
```

---

## 143.16 Repeated indexes in `concat(axis=1)`

Because column-wise concat aligns on index, repeated labels can create non-obvious results.

Test index uniqueness and intended alignment.

---

## 143.17 `merge_asof` with no valid match

The left row remains, with the right-side enrichment missing.

---

## 143.18 `merge_asof` tolerance exceeded

A reference record outside tolerance must not be treated as acceptable merely because it is nearby relative to all available values.

---

## 143.19 Fewer FX-rate rows than orders

Not every event necessarily has an eligible reference value.

The unmatched policy must be explicit.

---

## 143.20 Multiple rates at the same timestamp

Ambiguous reference data requires a source-level business rule.

---

## 143.21 Duplicate mapping keys

A `map()` lookup requires a well-defined key-to-value relationship.

---

## 143.22 Very wide right table

Project required columns and test memory-sensitive workloads.

---

## 143.23 Very high-cardinality key

Measure runtime and memory instead of assuming a particular representation is best.

---

# 144. Production Data Engineering Scenarios

## 144.1 E-commerce

Illustrative flow:

```text
orders
  │
  ├── customer_id → customers
  │
  └── product_id  → products
```

Before the joins:

```text
customer_id unique in customers?
product_id unique in products?
orders must be preserved?
revenue must remain unchanged?
unknown keys reported?
```

---

## 144.2 Banking

Illustrative example:

```text
transactions
    │
    ├── customer_id → customer master
    ├── branch_code → branch reference
    └── currency + timestamp → FX/reference data
```

Typical join concerns include:

```text
source-specific key formats
reference-data duplicates
historical versions
missing identifiers
effective-dated rates
```

This is an illustrative architecture, not a universal bank design.

---

## 144.3 IoT

```text
device events
    │
    └── device_id → device registry
```

Unknown devices may be a source-data quality signal.

---

## 144.4 Payments

```text
payments
   │
   └── currency + payment_time
               ↓
            FX rates
```

A point-in-time rule may be:

```text
latest known acceptable rate
```

which is not the same as an exact timestamp equality join.

---

## 144.5 Marketing

```text
campaign events
    │
    └── campaign_id → campaign metadata
```

If campaigns have versions, the data model may require more than a simple equality join.

---

# 145. Data Contract for Reference Tables

A reference dataset should expose its expected key contract.

Example:

```text
Dataset: customers

Expected grain:
one row per customer_id

Key:
customer_id

Uniqueness:
unique

Nullability:
non-null

Expected relationship:
orders.customer_id → customers.customer_id
```

Then the enrichment can encode:

```python
validate="many_to_one"
```

This is a practical way to convert a data-model assumption into an executable control.

---

# 146. Join Contract Template

Reuse this template in code reviews, design documents, and tests:

```text
Join name:

Left dataset:

Right dataset:

Left grain:

Right grain:

Join key(s):

Key dtype(s):

Key normalization:

Expected cardinality:

Join type:

Expected left-row behavior:

Expected right-row behavior:

Expected unmatched-left behavior:

Expected unmatched-right behavior:

Expected result row count:

Expected measure behavior:

Null-key policy:

Validation rule:

Diagnostics:

Reconciliation rule:

Performance notes:
```

---

# 147. Prediction-First Join Exercises

Before each exercise, write the answer before running the code.

### Exercise A

```text
left key counts:
A=4
B=2

right key counts:
A=1
B=1
```

Predict a left-join result:

```text
4 × 1 + 2 × 1 = 6
```

### Exercise B

```text
left:
A=4

right:
A=3
```

Predict:

```text
4 × 3 = 12
```

### Exercise C

```text
left = 3 rows
right = 7 rows
```

Cross join:

```text
21 rows
```

### Exercise D

Both sides contain a missing key.

Predict pandas behavior before running the inner merge.

### Exercise E

A right-side reference key is duplicated twice.

Predict what `validate="many_to_one"` should do.

### Exercise F

A left join has one unmatched left key.

Predict:

```text
row count
indicator value
right-side missing attributes
```

### Exercise G

An as-of order occurs between two rate timestamps.

Predict the backward match.

### Exercise H

The next rate is closer than the previous rate.

Predict how `nearest` differs from `backward`.

### Exercise I

A timestamp is outside tolerance.

Predict the missing enrichment.

### Exercise J

Two daily files have disjoint extra columns.

Predict the unioned schema and missing values after row-wise `concat`.

---

# 148. Production Performance Checklist

```text
[ ] Use only required columns
[ ] Check key dtypes
[ ] Profile key cardinality
[ ] Check duplicate keys
[ ] Define expected cardinality
[ ] Use validate=
[ ] Use indicator=True while diagnosing
[ ] Pre-filter only when semantically correct
[ ] Consider categorical keys for appropriate low-cardinality data
[ ] Consider intentional indexes when index alignment is the operation
[ ] Avoid accidental many-to-many joins
[ ] Estimate cross-join size first
[ ] Measure memory
[ ] Measure runtime
[ ] Benchmark equivalent semantics
[ ] Reconcile row counts
[ ] Reconcile business measures
```

---

# 149. Production Join Review Checklist

A production reviewer should be able to answer:

```text
[ ] What does one left row represent?
[ ] What does one right row represent?
[ ] What key defines identity?
[ ] Is the key complete?
[ ] Is it unique where expected?
[ ] What cardinality is intended?
[ ] What `how=` is intended?
[ ] What output row count is expected?
[ ] Can the result grow?
[ ] Can rows disappear?
[ ] Are unmatched keys expected?
[ ] Are null keys possible?
[ ] Can null keys match?
[ ] Is a composite key required?
[ ] Is validate= present?
[ ] Is indicator= needed during diagnostics?
[ ] Do measures reconcile?
[ ] Are only required columns being joined?
[ ] Is point-in-time matching required?
[ ] Is as-of direction correct?
[ ] Is tolerance defined?
[ ] Are performance measurements available where scale demands them?
```

---

# 150. Checkpoint

The roadmap checkpoint is the minimum completion standard.

## 1. Predict the row count of a left join given key cardinalities

Example:

```text
left:
A × 5
B × 2

right:
A × 1
B × 1
```

Expected:

```text
5 + 2 = 7
```

Change the right side:

```text
A × 2
B × 1
```

Now:

```text
A → 5 × 2 = 10
B → 2 × 1 = 2

Total = 12
```

You should be able to derive this before execution.

---

## 2. Use `validate=` to catch a many-to-many join

Given:

```text
left A × 2
right A × 3
```

an expected many-to-one contract must fail because the right side is not unique.

Use:

```python
validate="many_to_one"
```

Do not change it to `many_to_many` merely to silence the failure unless the business relationship really is many-to-many.

---

## 3. Write an anti-join

```python
diagnostic = left.merge(
    right[["key"]],
    on="key",
    how="left",
    indicator=True,
)

anti = diagnostic.loc[
    diagnostic["_merge"].eq("left_only")
]
```

---

## 4. Write a semi-join

```python
semi = left.loc[
    left["key"].isin(
        right["key"]
    )
]
```

---

## 5. Explain pandas null keys differently from SQL

You should be able to explain:

```text
Pandas merge can match null keys to null keys.
Ordinary SQL equality joins do not treat NULL = NULL as true.
Therefore a null-key policy must be explicit.
```

---

## 6. Use `merge_asof` for point-in-time enrichment

You should know:

```text
sort merge keys
choose by/partition key when needed
choose direction
set tolerance when freshness matters
handle unmatched rows explicitly
```

---

# 151. Advanced Self-Check Questions

Answer these without running code first.

1. What is the intended grain on the left?
2. What is the intended grain on the right?
3. Which side must have unique keys?
4. What cardinality is expected?
5. What happens if the right key appears twice?
6. For a key with 7 left rows and 4 right rows, how many equality-match rows can it generate?
7. Why can a left join increase row count?
8. Why can an inner join decrease row count?
9. What does `validate="many_to_one"` protect against?
10. What does `validate="many_to_many"` not protect against?
11. What does `indicator=True` provide?
12. What is an anti-join?
13. What is a semi-join?
14. Why is `concat(axis=1)` not a general replacement for `merge`?
15. When is `join()` a clearer choice than `merge()`?
16. What does pandas do with null keys during `merge`?
17. Why can that differ from SQL?
18. When should a composite key be used?
19. What is the purpose of `merge_asof`?
20. Why must its time key be sorted?
21. What does `direction="backward"` mean?
22. What does `direction="forward"` mean?
23. What does `direction="nearest"` mean?
24. Why might `by="currency"` be necessary?
25. What does `tolerance` protect against?
26. When is `map()` simpler than `merge()`?
27. When is `combine_first()` appropriate?
28. What is row explosion?
29. Why is revenue reconciliation useful?
30. Why can row-count reconciliation alone miss a problem?
31. What performance dimensions should be benchmarked?
32. Why should optimizations preserve the same business semantics?

---

# 152. Cheat Sheet

## `merge`

```python
left.merge(
    right,
    on="key",
    how="left",
    validate="many_to_one",
)
```

## Different key names

```python
left.merge(
    right,
    left_on="left_key",
    right_on="right_key",
    how="left",
)
```

## Suffixes

```python
suffixes=("_left", "_right")
```

## Diagnostics

```python
indicator=True
```

Then:

```python
merged["_merge"].value_counts()
```

## Cardinality

```text
one_to_one
one_to_many
many_to_one
many_to_many
```

Remember:

```text
many_to_many
= allowed relationship
≠ safety guarantee
```

## Anti-join

```python
merged.loc[
    merged["_merge"].eq("left_only")
]
```

## Semi-join

```python
left.loc[
    left["key"].isin(
        right["key"]
    )
]
```

## Row-wise concat

```python
pd.concat(
    frames,
    axis=0,
    ignore_index=True,
)
```

## Column-wise concat

```python
pd.concat(
    [left, right],
    axis=1,
)
```

Remember:

```text
axis=1
→ index alignment
```

## Index-oriented join

```python
left.join(
    right,
    on="key",
    how="left",
)
```

## As-of join

```python
pd.merge_asof(
    left.sort_values("timestamp"),
    right.sort_values("timestamp"),
    on="timestamp",
    by="currency",
    direction="backward",
    tolerance=...,
)
```

## Map

```python
df["label"] = df["key"].map(lookup)
```

## Fill missing aligned values

```python
primary.combine_first(secondary)
```

---

# 153. Common Mistakes Summary

| Mistake | Why it happens | Correct approach |
|---|---|---|
| Joining keys with different dtypes | Separate source systems use different schema representations | Normalize to a canonical key type according to business meaning |
| Not checking row counts after a join | A successful merge looks like a successful pipeline | Record predicted and actual row counts |
| Duplicate keys in dimension tables | Reference data may contain multiple versions or source defects | Understand the source rule and use `validate=` for the intended relationship |
| Outer joins that hide data problems | Keeping everything feels safer | Use outer joins deliberately for reconciliation and inspect `_merge` |
| No `validate=` on a critical enrichment | Cardinality remains an undocumented assumption | Encode the relationship with `validate=` |
| Many-to-many row explosion | Duplicate keys occur on both sides | Calculate `m × n` and decide whether the relationship is intentional |
| Unintended null-key matching | Engineers assume SQL null semantics | Establish an explicit pandas null-key policy |
| Using `inner` to avoid missing attributes | Output looks cleaner | Preserve the required population and report unmatched keys |
| Using one component of a composite key | A shorter join is easier to write | Use the full business key |
| Ignoring whitespace/case | Values look visually similar | Apply tested normalization rules |
| Using exact timestamp equality for point-in-time logic | Equality merge is familiar | Use `merge_asof` when the requirement is nearest/previous/next time matching |
| Wrong as-of direction | Direction is treated as a technical detail | Translate the business rule into backward/forward/nearest explicitly |
| Missing as-of tolerance | A match exists, so it is accepted | Define a freshness window when stale values are unacceptable |
| Missing `by` in an as-of join | Time is treated as globally comparable | Partition the search by the relevant entity key |
| Using `map` with non-unique lookup keys | Lookup syntax hides the relationship | Validate key uniqueness or use a relational join |
| Using `concat(axis=1)` for relational matching | Column-wise concat is short | Use a key-based merge when business keys define identity |
| Using `join()` with an accidental index | Index alignment is mistaken for key matching | Make the index intentional or use `merge()` |
| Assuming `left` always preserves row count | Right-side duplicates are ignored | A left join preserves each left row but may multiply rows when the right key repeats |
| Treating `validate=` as data repair | Validation failure is inconvenient | Investigate and correct the relationship rather than weakening validation |
| Optimizing before correctness | Runtime gets attention before semantics | Prove the join contract first, then benchmark |
| Assuming categorical keys are always faster | A common optimization becomes a rule | Measure the real workload |
| Assuming indexes are always faster | Index-based methods can look specialized | Benchmark end-to-end |
| Failing to reconcile revenue | Row count alone feels sufficient | Reconcile transactional measures when enrichment should not alter them |

---

# 154. Join Risk Matrix by Failure Mode

| Failure mode | Typical symptom | Primary diagnostic |
|---|---|---|
| Wrong key | Strange matches | Join contract + sampled keys |
| Wrong join type | Unexpected row loss | `how=` + row count + `_merge` |
| Duplicate right key | Row expansion | Right-side key counts + `validate=` |
| Duplicates on both sides | Severe explosion | Left/right frequency product |
| Null-key match | Missing IDs unexpectedly enrich each other | Explicit null-key test |
| Dtype mismatch | Unexpected unmatched keys | `.dtype` inspection |
| Whitespace/case issue | Visually equal keys fail | `repr()` + normalization |
| Incomplete composite key | Cross-entity matches | Full-key uniqueness/profile |
| Wrong as-of direction | Future reference value attached | Timeline inspection |
| Missing tolerance | Stale value attached | Time-gap analysis |
| Missing as-of `by` | Wrong entity's reference value | Entity-level sample |
| Wrong concat axis | Positional/index misalignment | Index inspection |
| Wrong `join()` index | Attributes attached to wrong business entity | Verify index meaning |
| Revenue change | Business total changed | Before/after measure reconciliation |
| Cross join too large | Memory/result explosion | `len(left) × len(right)` |

---

# 155. Production Join Architecture Pattern

A reliable enrichment step often looks like:

```text
SOURCE
  ↓
PROFILE KEYS
  ↓
NORMALIZE KEYS
  ↓
DEFINE JOIN CONTRACT
  ↓
PREDICT CARDINALITY / ROW COUNT
  ↓
VALIDATED JOIN
  ↓
DIAGNOSTICS
  ↓
ROW RECONCILIATION
  ↓
BUSINESS-MEASURE RECONCILIATION
  ↓
TESTS
  ↓
PUBLISH
```

For high-risk enrichment, keep a diagnostic output during development or operational investigations.

---

# 156. Production Scenario: E-Commerce

Illustrative pipeline:

```text
orders
  │
  ├── customer_id → customers
  │
  └── product_id  → products
```

Required questions:

```text
Are customer IDs unique in customers?
Are product IDs unique in products?
Are either dimensions versioned?
What happens to unknown orders?
Should every order survive?
Should revenue remain unchanged?
```

The join contract should exist independently for each enrichment.

---

# 157. Production Scenario: Banking

Illustrative relationships:

```text
transactions
  │
  ├── customer_id → customer master
  ├── branch_code → branch reference
  └── currency/time → reference-rate data
```

Potential concerns:

```text
source-specific key formats
reference duplicates
historical versions
missing identifiers
effective dates
point-in-time accuracy
```

The architecture is illustrative; specific banks and systems use different designs.

---

# 158. Production Scenario: IoT

```text
device_events
      │
      └── device_id → device_registry
```

An anti-join can detect events for unknown devices.

A many-to-one validation can verify that the current registry has one active row per device key when that is the intended contract.

---

# 159. Production Scenario: Payments and FX

```text
payments
  │
  └── currency + payment_time
                  ↓
               fx_rates
```

The correct business rule may be:

```text
latest acceptable FX rate at payment time
```

which suggests:

```python
pd.merge_asof(
    payments.sort_values("payment_time"),
    fx_rates.sort_values("rate_time"),
    left_on="payment_time",
    right_on="rate_time",
    by="currency",
    direction="backward",
    tolerance=pd.Timedelta("1D"),
)
```

The exact tolerance must come from the business requirement.

---

# 160. Production Scenario: Marketing

```text
campaign_events
      │
      └── campaign_id → campaign_metadata
```

Before enrichment:

```text
Is campaign_id unique?
Are campaign versions modeled separately?
What happens to retired campaign IDs?
How are unmatched events reported?
```

---

# 161. Complete `merge` Pattern

```python
enriched = (
    orders.merge(
        customers[
            [
                "customer_id",
                "segment",
                "country",
            ]
        ],
        on="customer_id",
        how="left",
        validate="many_to_one",
        indicator=True,
        suffixes=("_order", "_customer"),
    )
)
```

Then:

```python
unknown = enriched.loc[
    enriched["_merge"].eq("left_only")
]
```

And after validation:

```python
enriched = enriched.drop(
    columns="_merge"
)
```

only if the diagnostic column is not part of the published schema.

---

# 162. Complete As-Of Pattern

```python
orders_sorted = orders.sort_values(
    "order_time",
    kind="stable",
)

rates_sorted = rates.sort_values(
    "rate_time",
    kind="stable",
)

enriched = pd.merge_asof(
    orders_sorted,
    rates_sorted,
    left_on="order_time",
    right_on="rate_time",
    by="currency",
    direction="backward",
    tolerance=pd.Timedelta("1D"),
)
```

Then inspect missing rates:

```python
missing_rate = enriched.loc[
    enriched["rate_to_usd"].isna()
]
```

Do not silently fill missing reference rates without a business rule.

---

# 163. What `validate=` Does and Does Not Do

### It does

```text
check the declared relationship
fail when the relationship is violated
```

### It does not

```text
repair duplicate records
choose the correct duplicate
remove bad rows
resolve null-key business meaning
reconcile revenue
```

Think of it as a **contract enforcement tool**, not a cleaning algorithm.

---

# 164. What `indicator=True` Does and Does Not Do

### It does

```text
classify each merged observation as:
left_only
right_only
both
```

### It does not

```text
identify why a key is missing
repair missing records
prove the join is cardinality-safe
```

It is a diagnostic instrument.

---

# 165. What `concat()` Does and Does Not Do

### It does

```text
stack or align pandas objects along an axis
```

### It does not

```text
perform business-key matching
validate relational cardinality
prevent row multiplication from keys
```

Use it for the problem it actually solves.

---

# 166. Final Decision Tree

```text
Do I need to match records using a business key?
        |
       YES
        ↓
      merge()

Do I primarily need index-based alignment?
        |
       YES
        ↓
      join()

Do I need to stack multiple record batches/files?
        |
       YES
        ↓
  concat(axis=0)

Do I need column alignment by index?
        |
       YES
        ↓
  concat(axis=1)

Do I need nearest / previous / next time matching?
        |
       YES
        ↓
  merge_asof()

Do I need a simple key → one value lookup?
        |
       YES
        ↓
      map()

Do I need to fill missing primary values from aligned secondary values?
        |
       YES
        ↓
 combine_first()
```

---

# 167. Final Production Checklist

## Before the join

```text
[ ] I know the left grain.
[ ] I know the right grain.
[ ] I know the exact key(s).
[ ] The key is complete.
[ ] Key dtypes are intentional.
[ ] Key formatting is standardized.
[ ] Null-key policy is explicit.
[ ] Key uniqueness has been profiled.
[ ] Expected cardinality is written down.
[ ] Expected row count is predicted.
[ ] Unmatched-row behavior is defined.
[ ] Business-measure behavior is defined.
```

## During the join

```text
[ ] I chose the correct `how=`.
[ ] I used `on`, `left_on`, and `right_on` correctly.
[ ] I used `validate=` when the relationship is known.
[ ] I used `indicator=True` when diagnosing coverage.
[ ] I projected only necessary columns.
[ ] For `cross`, I calculated the Cartesian size.
[ ] For `merge_asof`, time keys are sorted.
[ ] `by` is correct.
[ ] `direction` matches business meaning.
[ ] `tolerance` matches data-freshness requirements.
```

## After the join

```text
[ ] Actual row count matches the contract.
[ ] Unexpected row multiplication is absent.
[ ] Unexpected row loss is explained.
[ ] Unmatched keys are accounted for.
[ ] Revenue/amount totals reconcile where required.
[ ] Output schema is intentional.
[ ] Tests pass.
[ ] Performance is measured at realistic scale when needed.
```

---

# 168. Topic 07 Master Checkpoint

You should now be able to explain all of these from memory:

```text
merge
join
concat
inner
left
right
outer
cross
on
left_on
right_on
suffixes
one-to-one
one-to-many
many-to-one
many-to-many
validate
indicator
anti-join
semi-join
key hygiene
composite keys
null-key behavior
merge_asof
by
direction
tolerance
map
combine_first
row explosion
row loss
reconciliation
benchmarking
```

More importantly, you should be able to take two new DataFrames and write the join contract before executing the operation.

---

# 169. Topic 07 Exit Questions

Before moving to Topic 08, answer these without looking anything up.

1. A left key occurs 6 times and a right key occurs 4 times. How many matching equality-join rows can that key produce?
2. Why is `many_to_one` the natural relationship for orders → customers when each customer is unique in the customer table?
3. Why can a left join increase row count?
4. Why can an inner join decrease row count?
5. What happens when both sides contain the same null key in pandas?
6. Why is that different from ordinary SQL equality semantics?
7. What does `validate="many_to_one"` check?
8. Why does `validate="many_to_many"` not prevent row explosion?
9. What does `_merge == "left_only"` mean?
10. What is a semi-join?
11. Why can `concat(axis=1)` be a dangerous substitute for `merge`?
12. Why might `join()` be appropriate when a lookup table is intentionally indexed by the business key?
13. Why does a composite key need to be treated as one identity when both components define uniqueness?
14. Why must `merge_asof` time keys be sorted?
15. When should `direction="backward"` be used?
16. Why can `tolerance` be necessary for FX or price enrichment?
17. Why is `by="currency"` important in an FX as-of join?
18. When is `map()` simpler than `merge()`?
19. When is `combine_first()` more appropriate than either?
20. Why is revenue reconciliation useful after an enrichment join?
21. Why is row-count reconciliation alone insufficient?
22. What should you measure when benchmarking joins?
23. Why should optimization come after semantic validation?

---

# 170. Final Mental Model

```text
                    JOIN
                      |
            +---------+---------+
            |                   |
         KEY(S)             RELATIONSHIP
            |                   |
   +--------+--------+   +------+-------+
   |        |        |   |      |       |
 single  composite  clean  1:1  m:1   m:n
   |        |        |          |       |
   +--------+--------+          |    explosion risk
            |                   |
            +---------+---------+
                      |
                  JOIN TYPE
                      |
        +-------------+-------------+
        |       |       |      |      |
      inner   left    right  outer   cross
        |       |       |      |      |
        +-------+-------+------+------+
                      |
                  OUTPUT SHAPE
                      |
        +-------------+-------------+
        |                           |
      row loss                  row growth
        |                           |
    unmatched                    m × n
                      |
                  VALIDATION
                      |
                 validate=
                 indicator=True
                      |
                 RECONCILIATION
                      |
          rows + keys + measures
                      |
                  PERFORMANCE
                      |
        project + measure + benchmark
```

The production sequence is:

```text
DATAFRAME GRAIN
      ↓
JOIN KEYS
      ↓
CARDINALITY
      ↓
JOIN CONTRACT
      ↓
KEY HYGIENE
      ↓
ROW-COUNT PREDICTION
      ↓
JOIN TYPE
      ↓
VALIDATION
      ↓
DIAGNOSTICS
      ↓
RECONCILIATION
      ↓
PERFORMANCE
      ↓
PRODUCTION OUTPUT
```

The central rule is simple:

> **Never perform a join without understanding the join keys, expected cardinality, expected row-count behavior, and treatment of unmatched rows.**

---

# 171. Official References

The chapter uses current pandas join concepts documented by pandas:

- `pandas.merge`: https://pandas.pydata.org/docs/reference/api/pandas.merge.html
- `pandas.merge_asof`: https://pandas.pydata.org/docs/reference/api/pandas.merge_asof.html
- SQL comparison: https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sql.html
- `pandas.concat`: https://pandas.pydata.org/docs/reference/api/pandas.concat.html
- `DataFrame.join`: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.join.html

For current pandas behavior, pay particular attention to:

```text
null-key matching in merge
validate=
indicator=True
merge_asof sorting
direction
by
tolerance
```

---

# Final Topic 07 Coverage Checklist

## Basics

- [ ] `merge`
- [ ] `how="inner"`
- [ ] `how="left"`
- [ ] `how="right"`
- [ ] `how="outer"`
- [ ] `how="cross"`
- [ ] `on`
- [ ] `left_on`
- [ ] `right_on`
- [ ] `suffixes`
- [ ] row-wise `concat`
- [ ] column-wise `concat`
- [ ] `ignore_index=True`
- [ ] mismatched columns
- [ ] `join`
- [ ] index-based `join` vs key-based `merge`

## Intermediate

- [ ] one-to-one
- [ ] one-to-many
- [ ] many-to-one
- [ ] many-to-many
- [ ] `validate="one_to_one"`
- [ ] `validate="one_to_many"`
- [ ] `validate="many_to_one"`
- [ ] `validate="many_to_many"` discussed correctly
- [ ] join contracts
- [ ] row-count prediction
- [ ] row explosion
- [ ] row loss
- [ ] `indicator=True`
- [ ] `_merge`
- [ ] anti-join
- [ ] semi-join
- [ ] dtype matching
- [ ] whitespace normalization
- [ ] case normalization
- [ ] composite keys

## Advanced

- [ ] pandas null-key matching
- [ ] SQL null-key contrast
- [ ] explicit null-key handling
- [ ] `merge_asof`
- [ ] `by`
- [ ] `direction`
- [ ] `tolerance`
- [ ] point-in-time enrichment
- [ ] `map`
- [ ] `combine_first`
- [ ] categorical join keys
- [ ] sorted indexes / intentional alignment structures
- [ ] pre-filtering
- [ ] reducing columns before join
- [ ] wide-result memory
- [ ] benchmarking

## Hands-on exercise

- [ ] `enrich_orders.py` fully specified
- [ ] orders → customers many-to-one
- [ ] `validate=`
- [ ] `indicator=True`
- [ ] unknown-customer reporting
- [ ] duplicate product IDs
- [ ] revenue inflation demonstration
- [ ] failure caught with `validate=`
- [ ] FX `merge_asof`
- [ ] currency `by`
- [ ] correct `direction`
- [ ] `tolerance`
- [ ] customer anti-join
- [ ] customer/order semi-join
- [ ] 30 daily-file concat
- [ ] mismatched-column alignment
- [ ] revenue reconciliation
- [ ] row-count reconciliation

## Quality

- [ ] prediction-first exercises
- [ ] debugging
- [ ] testing
- [ ] edge cases
- [ ] production scenarios
- [ ] join contract template
- [ ] performance checklist
- [ ] anti-patterns
- [ ] SQL comparison
- [ ] checkpoint
- [ ] common mistakes
- [ ] cheat sheet

---

## Topic Completion Standard

Do not consider this topic complete because the following code runs:

```python
orders.merge(customers, on="customer_id")
```

Consider it complete when you can explain, before execution:

```text
what one row means on each side
which key defines the relationship
which side must be unique
what cardinality is expected
how many rows should result
whether rows can multiply
whether rows can disappear
how unmatched keys are handled
how null keys are handled
whether a composite key is required
whether an as-of join is required
whether map or combine_first is a better fit
whether concat or join is actually the intended operation
which business measures must reconcile
how validate= will fail fast
how indicator= will diagnose coverage
how the join will be tested
how it will be benchmarked at realistic scale
```

That is the production Data Engineering skill this topic is designed to build.
