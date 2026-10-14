# Topic 01 — Series, DataFrame, and Index

> **Stage 2 — Python for Data Engineering · Module 2.3 — DataFrames with pandas**
>
> **Target pandas version:** pandas 3.x
>
> **Central question:** **What exactly are Series, DataFrames, and Indexes, and how does the Index change the meaning of my pandas operations?**

---

## Learning objectives

By the end of this chapter, you should be able to:

- explain a `Series` as a one-dimensional labelled array;
- explain a `DataFrame` as multiple aligned labelled columns sharing a row `Index`;
- create pandas objects from dictionaries, lists of records, and NumPy arrays;
- inspect `head`, `tail`, `sample`, `shape`, `columns`, `dtypes`, `info`, `describe`, and `value_counts`;
- distinguish **labels** from **positions**;
- understand `RangeIndex`, `set_index`, `reset_index`, and `rename`;
- predict the result of Series arithmetic using **index alignment**;
- distinguish alignment-generated `NaN` from missing values that were already present in source data;
- validate index properties such as `is_unique` and `is_monotonic_increasing`;
- reason about duplicate labels;
- manage columns intentionally with assignment, `rename`, `drop`, explicit reordering, and `assign`;
- create and query `MultiIndex` structures;
- understand the high-level internal representation of DataFrame columns as NumPy-backed, pandas extension-array-backed, or Arrow-backed data;
- decide when an Index adds useful semantics and when ordinary columns are clearer for Data Engineering pipelines;
- debug index-related surprises systematically;
- complete the `index_alignment.py` exercise with tests for index, row count, and values.

---

## Prerequisites

This chapter assumes you already know:

- Python lists, dictionaries, functions, and exceptions;
- NumPy arrays, shapes, dtypes, vectorization, masks, and basic memory behavior;
- basic Data Engineering ideas such as source data, transformations, bronze/silver/gold layers, batch processing, and pipelines.

You do **not** need previous pandas experience.

---

# 1. Introduction

pandas is a Python library for labelled tabular and time-oriented data. Data Engineers use it for API extracts, reconciliation jobs, data-quality investigations, test fixtures, small-to-medium transformations, feature preparation, and many local batch tasks.

Teams may use SQL, Polars, DuckDB, or Spark for other parts of a platform, yet pandas remains useful because it gives an engineer an expressive way to work with columns and labelled rows in Python.

The most important mental shift in this module is:

```text
A pandas DataFrame is not just a spreadsheet.

It is a labelled data structure.
```

That means the same visible values can behave differently depending on their labels.

Consider two Series:

```text
A:
US → 100
IN → 200

B:
IN → 50
UK → 70
```

A beginner may think “100 goes with 50 because they are both first/second positions.” pandas instead asks:

```text
Which labels should be matched?
```

The result is therefore:

```text
US → NaN
IN → 250
UK → NaN
```

The core ideas of this chapter are:

```text
columns
+
rows
+
labels
+
keys
+
grain
+
alignment
```

These ideas matter in production because a pipeline can produce numerically plausible values while still being wrong at the row-identity level.

### Two classes of pandas failure

A large class of correctness failures comes from confusing:

```text
label
vs
position
```

A second class comes from treating a DataFrame as if its index were always a business key.

A third class appears when the engineer changes the index or uses a `MultiIndex` but forgets that output consumers usually expect explicit columns.

---

# 2. Why pandas matters in Data Engineering

A Data Engineer commonly receives data shaped like:

```text
API response → JSON records
CSV export  → rows and columns
Parquet     → typed columns
Database    → relational records
```

A pandas DataFrame is often the local representation used to inspect and transform that data.

For example:

```text
customers
orders
country revenue
transaction summaries
sensor readings
reconciliation results
```

A good pandas engineer repeatedly asks:

```text
What does one row represent?
What is the grain?
What identifies the row?
What is the Index?
Which fields are ordinary columns?
Will this operation align by labels?
```

### Production scenario: country revenue reconciliation

Suppose one system reports 2024 revenue for:

```text
US, IN, UK
```

and another reports 2025 revenue for:

```text
IN, UK, DE
```

The sets are different. A positional calculation can silently pair the wrong countries. Index alignment prevents that particular mistake by matching on the country labels.

That does **not** mean alignment makes the whole pipeline correct. It only means the pandas operation is following label semantics. You still need to decide what unmatched countries mean.

---

# 3. The central mental model

Use this hierarchy throughout the module:

```text
Python data
    ↓
Series
    ↓
Index
    ↓
DataFrame
    ↓
Rows + columns + labels
    ↓
Index alignment
    ↓
Index properties
    ↓
Column operations
    ↓
MultiIndex
    ↓
Internal storage
    ↓
Index design decisions
```

For every important pandas operation, predict:

```text
1. Number of rows
2. Number of columns
3. Column names
4. Dtypes
5. Index
6. Whether alignment occurs
```

This prediction habit is more valuable than memorizing dozens of method names.

---

# 4. Series fundamentals

## 4.1 What is a Series?

A `Series` is a **one-dimensional labelled array**.

It has at least four concepts worth keeping separate:

```text
values
index
name
dtype
```

Example:

```python
import pandas as pd

revenue = pd.Series(
    [100, 200, 300],
    index=["US", "IN", "UK"],
    name="revenue",
)

print(revenue)
```

Expected display:

```text
US    100
IN    200
UK    300
Name: revenue, dtype: int64
```

The exact integer dtype can depend on the values and pandas/NumPy environment, but the important semantics are stable: there are three labelled observations and the labels are part of the object.

### What each argument means

```python
pd.Series(
    data=[100, 200, 300],
    index=["US", "IN", "UK"],
    name="revenue",
)
```

- `data` provides the values;
- `index` provides the labels;
- `name` identifies the Series conceptually;
- pandas chooses or accepts a dtype for the values.

### Inspect the components

```python
print(revenue.values)
print(revenue.index)
print(revenue.dtype)
print(revenue.name)
```

A Series therefore is not “just an array.” It is:

```text
label → value
```

with dtype metadata attached.

---

## 4.2 Prediction exercise — Series identity

Before running the following:

```python
revenue = pd.Series(
    [100, 200, 300],
    index=["US", "IN", "UK"],
    name="revenue",
)
```

Predict:

```text
Rows/observations: ?
Index: ?
Name: ?
Dtype family: ?
```

Then verify:

```python
assert len(revenue) == 3
assert list(revenue.index) == ["US", "IN", "UK"]
assert revenue.name == "revenue"
```

### Engineering lesson

When you read or create a Series, the labels deserve the same attention as the values.

---

# 5. Series creation from different sources

## 5.1 Series from a list

```python
numbers = pd.Series([10, 20, 30])
print(numbers)
```

By default, pandas gives the observations a `RangeIndex`.

Conceptually:

```text
0 → 10
1 → 20
2 → 30
```

The labels are positions-like integers, but they are still index labels.

---

## 5.2 Series from a dictionary

A dictionary naturally carries keys that can become the index.

```python
revenue = pd.Series({
    "US": 100,
    "IN": 200,
    "UK": 300,
})

print(revenue)
```

The keys become labels:

```text
US → 100
IN → 200
UK → 300
```

This is especially useful when an API or aggregation already gives you key-value pairs.

---

## 5.3 Series from a NumPy array

Because pandas builds on NumPy and other array systems, you can construct a Series from an array.

```python
import numpy as np

values = np.array([10, 20, 30], dtype=np.int32)
series = pd.Series(values, index=["A", "B", "C"], name="score")

print(series)
print(series.dtype)
```

The values come from the NumPy array while pandas adds labels and higher-level metadata.

### Data Engineering use case

When an upstream NumPy computation produces a metric per entity, wrapping the result in a Series with an explicit entity index can make subsequent alignment explicit and safe.

---

# 6. DataFrame fundamentals

## 6.1 What is a DataFrame?

A `DataFrame` is a collection of columns, each behaving like a Series, aligned against a shared row Index.

Example:

```python
df = pd.DataFrame({
    "order_id": [101, 102, 103],
    "amount": [1000, 2000, 1500],
    "country": ["IN", "US", "UK"],
})

print(df)
```

Conceptually:

```text
Index   order_id   amount   country
0       101        1000     IN
1       102        2000     US
2       103        1500     UK
```

And structurally:

```text
DataFrame
├── row Index
├── order_id Series
├── amount Series
└── country Series
```

The columns share the same row index.

---

## 6.2 A DataFrame is not one homogeneous array

NumPy arrays normally have one dtype for all elements. A DataFrame may contain columns with different dtypes.

For example:

```python
df = pd.DataFrame({
    "order_id": [101, 102],
    "country": ["IN", "US"],
    "amount": [1250.50, 980.25],
})

print(df.dtypes)
```

One column may be integer-like, another string-like, and another floating-point.

This is one reason a DataFrame is more than “a 2-D NumPy array.”

---

## 6.3 DataFrame columns are aligned to the shared row index

Consider explicitly indexed Series:

```python
order_id = pd.Series([101, 102, 103], index=[10, 20, 30], name="order_id")
amount = pd.Series([1000, 2000, 1500], index=[10, 20, 30], name="amount")

df = pd.DataFrame({
    "order_id": order_id,
    "amount": amount,
})

print(df)
```

Both columns use the same row labels.

The shared index provides row identity within the DataFrame.

---

# 7. DataFrame creation methods

A DataFrame can be constructed from multiple kinds of Python and NumPy input.

## 7.1 Dictionary of lists — column-oriented construction

```python
df = pd.DataFrame({
    "customer_id": [1, 2, 3],
    "country": ["IN", "US", "UK"],
    "amount": [120, 250, 180],
})

print(df)
```

Think of this as:

```text
column → all values for that column
```

This style is natural when your data is already column-oriented.

---

## 7.2 List of dictionaries — row-oriented construction

This is common for JSON/API data.

```python
records = [
    {"order_id": 101, "country": "IN", "amount": 120},
    {"order_id": 102, "country": "US", "amount": 250},
    {"order_id": 103, "country": "UK", "amount": 180},
]

df = pd.DataFrame(records)
print(df)
```

Think of this as:

```text
one dictionary → one record / row
```

Missing keys can result in missing values in the corresponding column, so production code should inspect the resulting schema.

---

## 7.3 NumPy array — rectangular numeric data

```python
import numpy as np

values = np.array([
    [101, 120],
    [102, 250],
    [103, 180],
])

df = pd.DataFrame(values, columns=["order_id", "amount"])
print(df)
```

Because the source array is homogeneous, both columns initially share the NumPy dtype of the array.

This is useful when the data is genuinely numeric and homogeneous. It may not be the ideal construction method when columns need independent dtypes from the start.

---

## 7.4 Predict before creating

For this input:

```python
records = [
    {"order_id": 1, "amount": 100},
    {"order_id": 2, "amount": 200},
    {"order_id": 3, "amount": 300},
]
```

Predict:

```text
rows: ?
columns: ?
column names: ?
index: ?
```

Verification:

```python
df = pd.DataFrame(records)

assert df.shape == (3, 2)
assert list(df.columns) == ["order_id", "amount"]
assert list(df.index) == [0, 1, 2]
```

---

# 8. Inspecting pandas objects

Inspection is not optional in production data work. Before transforming a dataset, establish what you actually received.

---

## 8.1 `head`

```python
print(df.head())
```

Use `head()` for a quick look at the first rows.

Typical use:

```text
Did parsing roughly work?
Are column names plausible?
Are values in the expected format?
```

---

## 8.2 `tail`

```python
print(df.tail())
```

Useful for checking the end of the dataset and catching issues that only appear later.

---

## 8.3 `sample`

```python
print(df.sample(3, random_state=42))
```

A sample can expose patterns that the first few rows do not show.

Use a fixed `random_state` when you need deterministic inspection or reproducible tests.

---

## 8.4 `shape`

```python
print(df.shape)
```

`shape` is a tuple:

```text
(rows, columns)
```

Example:

```python
rows, columns = df.shape
print(rows)
print(columns)
```

### Production habit

Predict row counts before expensive transformations. A large unexpected jump in row count is often the first signal of a broken transformation.

---

## 8.5 `columns`

```python
print(df.columns)
```

The columns themselves are represented by an Index-like object.

Check exact names before writing transformations that assume a schema.

---

## 8.6 `dtypes`

```python
print(df.dtypes)
```

You should inspect dtypes because the same visual text can represent different semantic types.

A Data Engineer should ask:

```text
Is this identifier numeric or text?
Is this amount numeric?
Is this date truly datetime-like?
Is a label unexpectedly mixed-type?
```

Detailed dtype engineering belongs to Topic 04, but schema awareness starts here.

---

## 8.7 `info`

```python
df.info()
```

`info()` is a compact structural inspection tool. It helps you see:

- number of rows;
- column names;
- non-null counts;
- dtypes;
- a rough memory summary.

For large pipelines, this often catches a bad inference quickly.

---

## 8.8 `describe`

```python
print(df.describe())
```

`describe()` summarizes selected columns statistically.

For numeric columns, it typically provides values such as:

```text
count
mean
std
min
quartiles
max
```

Do not treat `describe()` as a full data-quality report. It does not tell you whether a business key is valid, whether labels are standardized, or whether a value is semantically correct.

---

## 8.9 `value_counts`

For one column:

```python
print(df["country"].value_counts())
```

This is useful for:

- status profiling;
- category profiling;
- finding unexpected labels;
- checking cardinality quickly.

Example:

```python
status = pd.Series([
    "paid",
    "paid",
    "pending",
    "paid",
    "cancelled",
])

print(status.value_counts())
```

Before cleaning labels, inspect what is actually present.

---

# 9. The Index

## 9.1 What is an Index?

The Index is the labelled axis associated with rows of a DataFrame or observations of a Series.

Inspect it with:

```python
print(df.index)
```

And inspect column labels with:

```python
print(df.columns)
```

This gives the foundational distinction:

```text
row Index
vs
column Index
```

Both are label collections.

---

## 9.2 Labels are not the same as positions

Suppose:

```python
df = pd.DataFrame(
    {"amount": [100, 200, 300]},
    index=[10, 20, 30],
)
```

The rows are labelled `10`, `20`, and `30`.

The first row has:

```text
position → 0
label    → 10
```

The second row has:

```text
position → 1
label    → 20
```

These are different concepts. Later, Topic 03 will use this distinction directly with `loc` and `iloc`.

For now, the key rule is:

> **An index label is metadata identifying an observation; it is not automatically the observation's positional number.**

---

# 10. RangeIndex

A newly created DataFrame often starts with a `RangeIndex`:

```python
df = pd.DataFrame({
    "amount": [100, 200, 300],
})

print(df.index)
```

Conceptually the labels are:

```text
0
1
2
```

A `RangeIndex` is compact and efficient for the common case where you simply need default row labels.

### Important warning

A `RangeIndex` does **not** automatically mean:

```text
business key = row number
```

In an orders dataset:

```text
0, 1, 2, 3...
```

usually means “current DataFrame row labels,” not “order IDs.”

Keep real business identifiers in explicit columns unless there is a deliberate reason to use them as an Index.

---

# 11. `set_index`

Use `set_index` when a column should become the row labels.

```python
df = pd.DataFrame({
    "country": ["IN", "US", "UK"],
    "revenue": [100, 200, 150],
})

indexed = df.set_index("country")
print(indexed)
```

Before:

```text
Index   country   revenue
0       IN        100
1       US        200
2       UK        150
```

After:

```text
Index(country)   revenue
IN               100
US               200
UK               150
```

### What changed?

- row labels changed;
- `country` is no longer an ordinary column by default;
- the row count did not change;
- the revenue values did not change.

Prediction:

```text
rows    = 3
columns = 1
index   = IN, US, UK
```

Verify:

```python
assert indexed.shape == (3, 1)
assert list(indexed.index) == ["IN", "US", "UK"]
assert list(indexed.columns) == ["revenue"]
```

### `drop=False`

You can keep the original column when needed:

```python
indexed = df.set_index("country", drop=False)
print(indexed)
```

Now `country` participates in the Index while remaining an explicit column.

### Engineering decision

Do not use `set_index` merely because “indexes are faster.” First ask whether index semantics make the downstream operation clearer.

---

# 12. `reset_index`

Use `reset_index` to move row labels back into columns.

```python
df = pd.DataFrame({
    "country": ["IN", "US"],
    "revenue": [100, 200],
}).set_index("country")

flat = df.reset_index()
print(flat)
```

The index label becomes an explicit column again:

```text
  country  revenue
0 IN       100
1 US       200
```

### `drop=True`

If you do not want the old index as a new column:

```python
reset_only = df.reset_index(drop=True)
print(reset_only)
```

This gives a fresh default index.

### Why this matters in ETL

Many file and interchange formats are easier to understand when important fields are explicit columns.

Before an output boundary, ask:

```text
Should this index remain an index?
Or should it become an explicit column?
```

---

# 13. `rename`

`rename` can change column labels, index labels, or both.

## 13.1 Rename columns

```python
df = pd.DataFrame({
    "amt": [100, 200],
    "cust": [1, 2],
})

renamed = df.rename(columns={
    "amt": "amount",
    "cust": "customer_id",
})

print(renamed)
```

Explicit column names make transformations more readable and schemas more predictable.

## 13.2 Rename index labels

```python
df = pd.DataFrame(
    {"revenue": [100, 200]},
    index=["us", "in"],
)

renamed = df.rename(index={"us": "US", "in": "IN"})
print(renamed)
```

Be careful not to confuse renaming labels with changing the meaning of the row data.

---

# 14. Index alignment — the most important concept

Index alignment means pandas matches labelled values by their labels rather than by physical position for operations that align Series/DataFrame axes.

Start with:

```python
a = pd.Series(
    [100, 200],
    index=["US", "IN"],
    name="revenue_2024",
)

b = pd.Series(
    [50, 70],
    index=["IN", "UK"],
    name="revenue_2025",
)

result = a + b
print(result)
```

The actual output is:

```text
IN     250.0
UK       NaN
US       NaN
```

The important mapping is:

```text
a:
US → 100
IN → 200

b:
IN → 50
UK → 70

align by label:
US → 100 + missing counterpart → NaN
IN → 200 + 50 → 250
UK → missing counterpart + 70 → NaN
```

### The rule

```text
pandas Series arithmetic
        ↓
match labels
        ↓
perform operation on matching labels
        ↓
represent unmatched labels with missing values where required
```

---

## 14.1 Why this protects correctness

Suppose values were accidentally reordered:

```python
a = pd.Series(
    [100, 200],
    index=["US", "IN"],
)

b = pd.Series(
    [70, 50],
    index=["UK", "IN"],
)
```

A positional mental model might think:

```text
100 + 70
200 + 50
```

But pandas sees labels:

```text
IN matches IN
US has no UK counterpart
UK has no US counterpart
```

That is a fundamentally different semantics.

---

# 15. Alignment-generated NaN vs source-data missingness

This distinction is critical.

Consider:

```python
a = pd.Series([100, 200], index=["US", "IN"])
b = pd.Series([50, 70], index=["IN", "UK"])
```

Neither source Series contains `NaN`.

Yet:

```python
result = a + b
print(result)
```

contains `NaN`.

Why?

```text
The source data was not necessarily missing.

The labels did not overlap completely.

Alignment created missing counterparts.
```

This means you should never automatically interpret every `NaN` after an operation as “the source system sent null.”

A `NaN` can be:

```text
source-data missingness
or
operation-induced missingness
```

### Production implication

When a reconciliation result contains unexpected `NaN`, ask:

```text
Was the original value missing?
Or did alignment create the missing value?
```

That question can change the next engineering decision.

---

# 16. Alignment and assignment

Alignment also matters when assigning a Series to a DataFrame column.

Consider:

```python
df = pd.DataFrame(
    {"country": ["US", "IN", "UK"]},
    index=[10, 20, 30],
)

revenue = pd.Series(
    [200, 100, 150],
    index=[20, 10, 30],
    name="revenue",
)

df["revenue"] = revenue
print(df)
```

The values align with the DataFrame's index:

```text
row label 10 → revenue 100
row label 20 → revenue 200
row label 30 → revenue 150
```

They do not simply follow the order in which the Series happened to be written.

Verify:

```python
assert df.loc[10, "revenue"] == 100
assert df.loc[20, "revenue"] == 200
assert df.loc[30, "revenue"] == 150
```

### Prediction question

Before running:

```python
df = pd.DataFrame({"x": [10, 20]}, index=[100, 200])
s = pd.Series([1, 2], index=[200, 100])
df["y"] = s
```

Predict:

```text
row label 100 → y = ?
row label 200 → y = ?
```

Answer only after you have reasoned from labels.

---

# 17. `add(..., fill_value=0)`

Sometimes you intentionally want missing counterparts treated as zero **for the operation**.

```python
combined = a.add(b, fill_value=0)
print(combined)
```

The actual output is:

```text
IN → 200 + 50 = 250
UK → 0 + 70 = 70
US → 100 + 0 = 100
```

But this creates an important Data Engineering question:

> **Does an absent country in a source dataset truly mean zero revenue?**

The answer depends on the business semantics.

Possible interpretations of “country not present” include:

```text
0 revenue
no data available
source extract filtered it out
country was not onboarded
system failure
```

Therefore:

```text
fill_value=0
```

is not merely a syntax choice. It is a semantic assumption.

### Safe reasoning pattern

Before using `fill_value=0`, document:

```text
Why is absence equivalent to zero?
What population does the source represent?
Could the missing label indicate an extraction problem?
```

---

# 18. Index properties

Indexes expose properties that are valuable for validation.

## 18.1 `is_unique`

```python
print(df.index.is_unique)
```

A unique index means no label appears more than once.

Example:

```python
unique_df = pd.DataFrame(
    {"amount": [100, 200]},
    index=["A", "B"],
)

assert unique_df.index.is_unique
```

Duplicate example:

```python
duplicate_df = pd.DataFrame(
    {"amount": [100, 200, 300]},
    index=["A", "A", "B"],
)

assert not duplicate_df.index.is_unique
```

A duplicate index is not automatically invalid. It becomes a problem when later logic assumes one unique row per label.

---

## 18.2 `is_monotonic_increasing`

```python
print(df.index.is_monotonic_increasing)
```

An index is monotonic increasing when its labels are in non-decreasing order according to pandas' ordering rules.

Example:

```python
ordered = pd.DataFrame({"x": [10, 20, 30]}, index=[1, 2, 3])
unordered = pd.DataFrame({"x": [10, 20, 30]}, index=[2, 1, 3])

assert ordered.index.is_monotonic_increasing
assert not unordered.index.is_monotonic_increasing
```

Ordering can matter for time-aware and ordered lookup patterns.

### Production principle

Use index properties as explicit invariants when your business logic expects them.

---

# 19. Duplicate labels

pandas allows duplicate index labels.

Example:

```python
df = pd.DataFrame(
    {"amount": [100, 200, 300]},
    index=["A", "A", "B"],
)

print(df)
print(df.index.is_unique)
```

The label `A` identifies two rows.

That can be perfectly legitimate when the row grain is something like:

```text
one row = one transaction
```

while the Index happens to contain only a customer identifier.

But it becomes dangerous when you intended:

```text
one row = one customer
```

In that case, duplicate labels violate your intended grain.

### Do not memorize “duplicates are bad”

The better rule is:

> **Duplicate labels are allowed; whether they are valid depends on the intended row grain and operation.**

---

## 19.1 Why duplicate labels can surprise you

Suppose:

```python
df = pd.DataFrame(
    {"amount": [100, 200]},
    index=["A", "A"],
)
```

The label `A` does not identify one unique row. A label-based lookup can therefore return multiple rows.

The production question is:

```text
Do I want one observation per index label?
```

If yes, validate:

```python
if not df.index.is_unique:
    raise ValueError("Expected a unique row index")
```

---

# 20. Sorted/unique indexes and lookup

A sorted, unique index can provide pandas with a more predictable lookup structure and can support efficient lookup patterns in relevant cases.

The important concept is not “sorting always makes code faster.” The useful idea is:

```text
unique labels
+
sensible ordering
+
index-aware operation
```

can create a structure that is easier to reason about and can be optimized for certain lookups.

Use `is_unique` and `is_monotonic_increasing` as checks rather than making unsupported performance assumptions.

Example:

```python
index = pd.Index([10, 20, 30])

assert index.is_unique
assert index.is_monotonic_increasing
```

---

# 21. Adding columns

The simplest pattern is direct assignment:

```python
df = pd.DataFrame({
    "quantity": [2, 3, 4],
    "unit_price": [10.0, 20.0, 5.0],
})

df["revenue"] = df["quantity"] * df["unit_price"]
print(df)
```

Here the arithmetic operates element-wise because both input Series share the same index.

Prediction:

```text
rows stay the same
columns increase by 1
new column = revenue
```

Verify:

```python
assert df.shape == (3, 3)
assert list(df.columns) == ["quantity", "unit_price", "revenue"]
assert df["revenue"].tolist() == [20.0, 60.0, 20.0]
```

---

## 21.1 Adding a Series with a different index

Because column assignment aligns Series by index, this can be useful or surprising.

```python
df = pd.DataFrame(
    {"country": ["US", "IN", "UK"]},
    index=[10, 20, 30],
)

metric = pd.Series(
    [200, 100],
    index=[20, 10],
)

df["metric"] = metric
print(df)
```

Row label `30` has no matching Series label, so it receives a missing value.

Again:

```text
alignment-generated missingness
```

is not necessarily source-data missingness.

---

# 22. Renaming columns

Standardized column names are a basic production-quality habit.

```python
df = pd.DataFrame({
    "amt": [100, 200],
    "cust": [1, 2],
    "status_desc": ["paid", "pending"],
})

clean = df.rename(columns={
    "amt": "amount",
    "cust": "customer_id",
})

print(clean)
```

Use names that communicate meaning, not source-system shorthand that only one engineer understands.

---

# 23. Dropping columns

Use `drop(columns=...)` to make the intended schema explicit.

```python
df = pd.DataFrame({
    "customer_id": [1, 2],
    "amount": [100, 200],
    "debug_value": [999, 888],
})

output = df.drop(columns=["debug_value"])
print(output)
```

This is useful before writing an output dataset because it prevents incidental source columns from leaking downstream.

It is also a good engineering habit to remove truly unnecessary columns early in a pipeline when memory matters. Detailed memory reduction belongs to a later topic, but the design principle starts here.

---

# 24. Column order

Column order often matters operationally even when it does not change the abstract DataFrame meaning.

Examples:

- CSV files have ordered fields;
- human reviewers read outputs in order;
- downstream systems may expect a declared schema order;
- tests often validate exact column order;
- documentation becomes easier when output columns follow a deliberate convention.

Explicit reordering is simple:

```python
df = pd.DataFrame({
    "amount": [100, 200],
    "customer_id": [1, 2],
    "country": ["IN", "US"],
})

ordered = df[["customer_id", "country", "amount"]]
print(ordered)
```

### Production rule

Do not rely on accidental column order. Treat the output schema as intentional.

---

# 25. `assign`

`assign` returns a DataFrame with additional or replaced columns and is useful for readable transformations.

Basic example:

```python
df = pd.DataFrame({
    "quantity": [2, 3],
    "unit_price": [10.0, 20.0],
})

result = df.assign(
    revenue=df["quantity"] * df["unit_price"]
)

print(result)
```

A useful feature is that later assignments inside the same `assign` can reference columns created earlier in the call when using lambdas:

```python
result = df.assign(
    revenue=lambda x: x["quantity"] * x["unit_price"],
    tax=lambda x: x["revenue"] * 0.18,
)

print(result)
```

Conceptually:

```text
original columns
      ↓
create revenue
      ↓
create tax from revenue
```

This is an early introduction to transformation expressions. Full method-chaining style belongs to Topic 11.

---

# 26. MultiIndex fundamentals

A `MultiIndex` is an Index with multiple levels of labels.

A natural Data Engineering grain is:

```text
(country, month)
```

For example:

```text
(country, month)

US  2025-01
US  2025-02
IN  2025-01
IN  2025-02
UK  2025-01
UK  2025-02
```

The two levels are:

```text
level 0 → country
level 1 → month
```

This lets the row identity express more than one dimension.

---

# 27. Creating a MultiIndex

There are several practical creation patterns.

## 27.1 From tuples

```python
index = pd.MultiIndex.from_tuples(
    [
        ("US", "2025-01"),
        ("US", "2025-02"),
        ("IN", "2025-01"),
        ("IN", "2025-02"),
    ],
    names=["country", "month"],
)

print(index)
```

Then attach it to a DataFrame:

```python
df = pd.DataFrame(
    {"revenue": [100, 120, 200, 220]},
    index=index,
)

print(df)
```

---

## 27.2 From ordinary columns with `set_index`

Often this is the most natural pipeline pattern:

```python
df = pd.DataFrame({
    "country": ["US", "US", "IN", "IN"],
    "month": ["2025-01", "2025-02", "2025-01", "2025-02"],
    "revenue": [100, 120, 200, 220],
})

indexed = df.set_index(["country", "month"])
print(indexed)
```

Now the row grain is explicitly represented by the index levels.

---

# 28. MultiIndex levels and row grain

A strong Data Engineering habit is to state the grain in plain language.

For the previous example:

> **One row = one country's revenue for one month.**

The index then encodes that grain:

```text
(country, month)
```

This is useful because it connects pandas mechanics to data modeling.

But do not automatically assume:

```text
MultiIndex = better model
```

A MultiIndex is one representation choice. Ordinary columns may be clearer for most ETL interchange.

---

# 29. MultiIndex selection with `loc`

Suppose:

```python
index = pd.MultiIndex.from_tuples(
    [
        ("US", "2025-01"),
        ("US", "2025-02"),
        ("IN", "2025-01"),
        ("IN", "2025-02"),
    ],
    names=["country", "month"],
)

df = pd.DataFrame(
    {"revenue": [100, 120, 200, 220]},
    index=index,
)
```

A tuple identifies a full MultiIndex key:

```python
value = df.loc[("US", "2025-01")]
print(value)
```

The row identified by:

```text
country = US
month   = 2025-01
```

is selected.

For a complete record, this typically returns the row as a Series because one row has multiple columns.

---

## 29.1 Select all rows for one first-level label

```python
us = df.loc["US"]
print(us)
```

The result represents all months for the `US` level.

The remaining index level is `month`.

This is an example of the fact that a MultiIndex is a hierarchy rather than a flat list of labels.

---

# 30. `xs` — cross-section selection

`xs` is useful when you want to select across a particular MultiIndex level.

For example:

```python
us = df.xs("US", level="country")
print(us)
```

This means:

```text
Find label US in the country level.
Return the corresponding cross-section.
```

The returned object keeps the other level as its remaining index.

### Why `xs` can be clearer

Compare:

```python
df.xs("US", level="country")
```

with a more complex tuple-oriented selection. `xs` states the intent directly:

```text
cross-section where country = US
```

---

# 31. Selecting one month across all countries

For the same MultiIndex:

```python
january = df.xs("2025-01", level="month")
print(january)
```

Now you have:

```text
US → January revenue
IN → January revenue
```

This reinforces the idea that:

```text
first level = one dimension
second level = another dimension
```

and selection can target either one.

---

# 32. `swaplevel`

Sometimes the order of hierarchy matters for how you work with the index.

```python
swapped = df.swaplevel("country", "month")
print(swapped)
```

The values do not change. The level order changes from:

```text
(country, month)
```

to:

```text
(month, country)
```

This can be useful when the second dimension becomes the primary access dimension for the next operation.

### Important distinction

`swaplevel` changes index level ordering; it does not change the underlying revenue meaning.

---

# 33. Sorting a MultiIndex

Use:

```python
sorted_df = df.sort_index()
print(sorted_df)
```

Sorting can make the hierarchical structure predictable and easier to inspect.

It can also help certain index-aware operations that benefit from ordered labels.

Do not use the blanket statement:

```text
sorting always makes pandas faster
```

The correct reasoning is:

```text
sorted structure
→ more predictable ordering
→ some operations can exploit ordering
```

but the runtime effect depends on the operation and data.

---

# 34. Flattening a MultiIndex

The most practical flattening technique for ETL output is often:

```python
flat = df.reset_index()
print(flat)
```

A MultiIndex such as:

```text
country   month
US        2025-01
US        2025-02
IN        2025-01
IN        2025-02
```

becomes explicit columns:

```text
country   month      revenue
US        2025-01    100
US        2025-02    120
IN        2025-01    200
IN        2025-02    220
```

This is often clearer for:

- CSV output;
- Parquet schemas;
- downstream ETL tools;
- BI/reporting consumers;
- API payloads.

### Engineering rule

Use hierarchy where it adds useful semantics; flatten it at an interoperability boundary when explicit columns are easier for consumers.

---

# 35. DataFrame internal representation

This is an advanced conceptual section. You do not need to memorize pandas' internal implementation classes to use a DataFrame well.

The useful model is:

```text
DataFrame
    ↓
column-oriented logical structure
    ↓
individual columns backed by appropriate array representations
```

The roadmap expects three broad categories to be understood:

```text
NumPy arrays
pandas extension arrays
Arrow arrays
```

### 35.1 NumPy-backed columns

Many conventional numeric columns can be represented using NumPy arrays.

That connects directly to Module 2.2:

```text
dtype
shape
memory
vectorized operations
```

### 35.2 pandas extension arrays

pandas also has extension-array types that allow pandas-specific dtype and missing-value semantics.

The important idea is that not every column must be a plain NumPy ndarray.

### 35.3 Arrow-backed arrays

pandas can also use Arrow-backed types where configured and supported.

This matters for:

- memory representation;
- nullable data;
- interoperability;
- columnar systems;
- type fidelity.

Do not turn this section into a deep Arrow tutorial. The purpose is to update your mental model:

> **A DataFrame is a high-level labelled structure whose columns may use different underlying array representations.**

---

# 36. Why the internal representation matters

The representation underneath a column influences things such as:

```text
dtype semantics
missing-value representation
memory use
interoperability
performance characteristics
```

For example, two columns may both display strings while using different underlying representations.

Likewise, a nullable integer type can preserve integer semantics while representing missing values differently from an ordinary NumPy integer array.

Detailed dtype choices are covered in Topic 04. For Topic 01, the key lesson is simply:

```text
DataFrame is the logical model.
Columns have concrete storage representations.
```

---

# 37. Index vs ordinary columns

This is one of the most important design decisions in practical pandas code.

There is no universal rule saying:

```text
Always use an Index
```

and no universal rule saying:

```text
Never use an Index
```

Instead, ask what semantics you need.

---

## 37.1 When an Index is useful

An Index can be useful for:

- time-series operations;
- repeated lookup by stable labels;
- hierarchical indexing with `MultiIndex`;
- operations whose semantics are naturally index-aware.

Example time-series concept:

```text
DatetimeIndex
    ↓
rows ordered by time
```

A meaningful Index can make the pandas operation itself expressive.

---

## 37.2 When ordinary columns are clearer

Ordinary columns are often clearer for:

- ETL transformations;
- explicit business keys;
- joins;
- file outputs;
- cross-tool interchange;
- schemas consumed outside pandas.

A Data Engineer should often prefer:

```text
customer_id
order_id
account_id
country
```

as ordinary columns because they are explicit data fields.

---

## 37.3 Index is not automatically the business key

Consider:

```python
df = pd.DataFrame({
    "order_id": [1001, 1002],
    "amount": [500, 700],
})
```

Its default index is:

```text
0
1
```

But the business identifier is:

```text
order_id
```

These are different concepts.

A business key might remain a normal column even when the DataFrame has a useful Index.

### Prepare for later modules

This distinction becomes especially important when you learn joins and cardinality:

```text
Index
vs
business key
vs
row grain
```

They can be related, but they are not interchangeable concepts.

---

# 38. Grain and Index

Data Engineering starts with a precise row definition.

Suppose a DataFrame represents:

> one row = one country's revenue for one month

Then a natural compound identity is:

```text
(country, month)
```

A `MultiIndex` can represent that identity directly.

But the same data can also be represented as ordinary columns:

```text
country | month | revenue
```

Neither representation is automatically “more correct.” The right choice depends on what operations and interfaces the next pipeline stage expects.

### Prediction question

Given:

```text
country = IN
month   = 2025-02
revenue = 250
```

ask:

```text
What is the row grain?
Which fields identify one row?
Should those fields be an Index, ordinary columns, or both?
```

The answer should be driven by semantics, not habit.

---

# 39. Prediction-first workflow

Use this checklist repeatedly.

Before running a pandas operation, write:

```text
Rows:
Columns:
Dtypes:
Index:
Alignment behavior:
Result meaning:
```

### Example 1 — Series addition

```python
a = pd.Series([100, 200], index=["US", "IN"])
b = pd.Series([50, 70], index=["IN", "UK"])

result = a + b
```

Predict before execution:

```text
result index = ?
result length = ?
US value = ?
IN value = ?
UK value = ?
```

Then verify.

---

### Example 2 — `set_index`

```python
df = pd.DataFrame({
    "country": ["US", "IN", "UK"],
    "revenue": [100, 200, 150],
})

result = df.set_index("country")
```

Predict:

```text
rows = ?
columns = ?
index = ?
remaining columns = ?
```

---

### Example 3 — `reset_index`

```python
result = df.set_index("country").reset_index()
```

Predict whether:

```text
country remains a column
row count changes
index returns to RangeIndex-like default labels
```

---

### Example 4 — Series assignment

```python
df = pd.DataFrame(
    {"amount": [100, 200]},
    index=[10, 20],
)

s = pd.Series([900, 800], index=[20, 10])
df["adjusted"] = s
```

Predict the `adjusted` value for each row label before running it.

---

### Example 5 — MultiIndex tuple selection

```python
result = multi_df.loc[("US", "2025-01")]
```

Predict:

```text
Is one full row selected?
How many values does it contain?
What is the returned object's index?
```

---

# 40. Debugging Series, DataFrame, and Index problems

Use this debugging pattern:

```text
Symptom
→ Root cause
→ Inspection
→ Correct approach
→ Prevention rule
```

---

## Bug 1 — Expecting positional Series addition

### Broken code

```python
a = pd.Series([100, 200], index=["US", "IN"])
b = pd.Series([50, 70], index=["IN", "UK"])

result = a + b
```

### Symptom

The result contains `NaN` values the engineer did not expect.

### Root cause

The Series are aligned by labels, not positions.

### Inspect

```python
print(a.index)
print(b.index)
print(result)
```

### Correct reasoning

```text
US matches only US
IN matches IN
UK matches only UK
```

### Prevention

Before arithmetic between labelled objects, compare their indexes.

---

## Bug 2 — Duplicate index labels

### Suspicious code

```python
df = pd.DataFrame(
    {"amount": [100, 200]},
    index=["A", "A"],
)
```

### Symptom

A lookup intended to identify one row matches multiple rows.

### Root cause

The index is not unique.

### Inspect

```python
if not df.index.is_unique:
    print("Duplicate labels exist")
```

### Correct approach

First decide whether duplicates are valid for the intended row grain.

### Prevention

Validate uniqueness only when the business rule requires it.

---

## Bug 3 — `set_index` changed the schema

### Broken expectation

An engineer expects:

```python
df = df.set_index("country")
```

to leave `country` as an ordinary column automatically.

### Root cause

By default, the column becomes the index and is removed from the ordinary columns.

### Inspect

```python
print(df.index)
print(df.columns)
```

### Correct approach

Use `drop=False` when the column should remain explicit:

```python
df = df.set_index("country", drop=False)
```

Or use `reset_index()` at the output boundary when you need flat columns again.

---

## Bug 4 — Resetting the index unexpectedly creates a column

### Symptom

After:

```python
df = df.reset_index()
```

you see an extra column.

### Root cause

`reset_index` converts index labels back into columns by default.

### Correct approach

If you only need fresh row numbering:

```python
df = df.reset_index(drop=True)
```

---

## Bug 5 — Treating RangeIndex as a business key

### Suspicious assumption

```python
df.index == order_id
```

### Root cause

A default `RangeIndex` merely labels the DataFrame rows. It does not acquire business meaning automatically.

### Correct approach

Inspect the actual business key column:

```python
print(df["order_id"])
```

Keep the identifier as an explicit column unless there is a deliberate reason to use it as the Index.

---

## Bug 6 — MultiIndex selection has an unexpected shape

### Symptom

The engineer expects one row but gets a Series or a smaller DataFrame.

### Root cause

MultiIndex selection can consume one or more levels, changing the remaining index structure.

### Inspect

```python
print(df.index.names)
print(df.index)
```

### Correct approach

State the exact desired grain before writing the selection:

```text
one full row?
one country?
one month across countries?
```

Then choose tuple-based `.loc` or `xs(level=...)` accordingly.

---

## Bug 7 — `add(fill_value=0)` is syntactically correct but semantically wrong

### Symptom

A reconciliation reports zero revenue for a country that was absent from one source.

### Root cause

The engineer assumed:

```text
absent label = zero
```

without validating the source semantics.

### Correct approach

Determine whether absence means zero, not applicable, source failure, or missing coverage.

### Prevention

Document the meaning of the fill operation.

---

## Bug 8 — Duplicate labels create ambiguous selection

### Inspect

```python
print(df.index.is_unique)
```

If `False`, explicitly inspect the duplicate labels before designing downstream logic.

---

## Bug 9 — Series assignment aligns by index

### Suspicious code

```python
df["metric"] = metric_series
```

### Symptom

Values appear in “unexpected rows.”

### Root cause

The Series was matched by labels, not by its visible order.

### Inspect

```python
print(df.index)
print(metric_series.index)
```

### Prevention

Always inspect index compatibility when assigning labelled Series.

---

## Bug 10 — MultiIndex leaked into output

### Symptom

A CSV contains confusing hierarchical structure or an unexpected index column.

### Root cause

The engineer wrote a MultiIndex directly instead of flattening it.

### Correct approach

```python
output = df.reset_index()
```

Then explicitly order columns for the output schema.

---

# 41. Hands-on exercise — `index_alignment.py`

This is the main practical exercise for Topic 01.

> **Important:** The exercise specification belongs in this Markdown file. Create the Python and test files separately in your project when you actually perform the exercise; they are not part of this chapter artifact.

---

## Scenario

You are reconciling annual revenue by country.

The 2024 source contains:

```text
US, IN, UK
```

The 2025 source contains:

```text
IN, UK, DE
```

The country sets are intentionally different so that index alignment becomes observable.

Use deterministic numeric values.

Example:

```python
revenue_2024 = pd.Series(
    [1000, 1200, 900],
    index=["US", "IN", "UK"],
    name="revenue_2024",
)

revenue_2025 = pd.Series(
    [1300, 950, 500],
    index=["IN", "UK", "DE"],
    name="revenue_2025",
)
```

---

## Task 1 — Year-over-year calculation

Compute the year-over-year difference or another clearly defined YoY metric.

Before running it, write down:

```text
result index = ?
result length = ?
where will NaN appear?
why?
```

A percentage-growth implementation can be defined as:

```text
(revenue_2025 - revenue_2024) / revenue_2024 * 100
```

but you must explain what happens for countries missing from one side.

### Required learning outcome

Do not just produce numbers. Explain the alignment that created them.

---

## Task 2 — Explain alignment

Explicitly explain why:

```python
revenue_2024 + revenue_2025
```

does not align positionally.

Your explanation must include:

```text
labels
→ matching
→ unmatched labels
→ missing counterparts
→ NaN
```

---

## Task 3 — `add(fill_value=0)`

Compute:

```python
combined = revenue_2024.add(
    revenue_2025,
    fill_value=0,
)
```

Compare the result with normal addition.

Then write a short data-quality decision note:

> Is “country absent from this source” truly equivalent to zero revenue in this business scenario?

Give at least one reason why `0` may be valid and one reason why it may be dangerous.

---

## Task 4 — Build MultiIndex revenue data

Create a DataFrame at the grain:

```text
one row = one country's revenue for one month
```

Required columns before indexing:

```text
country
month
revenue
```

Then set:

```text
(country, month)
```

as the MultiIndex.

---

## Task 5 — Select one country

Select one country, for example:

```text
US
```

Explain:

```text
which index level you selected
what the remaining index represents
how many rows you expect
```

---

## Task 6 — Select one month across all countries

Select:

```text
2025-01
```

across all countries.

Use a clear MultiIndex operation such as:

```python
df.xs("2025-01", level="month")
```

Predict the result before running it.

---

## Task 7 — Flatten the result

Convert the MultiIndex back to explicit columns:

```python
flat = df.reset_index()
```

Verify that `country` and `month` are again ordinary columns.

---

## Task 8 — Tests

Your tests must verify:

- expected index values;
- expected row count;
- expected values.

Use pandas testing helpers where appropriate:

```python
pd.testing.assert_series_equal(...)
pd.testing.assert_frame_equal(...)
```

You may also use direct checks such as:

```python
assert list(result.index) == expected_index
assert len(result) == expected_rows
```

---

## Exercise extension — make the bug visible

Create a deliberately wrong positional calculation in plain Python or NumPy and compare it with the pandas-labelled calculation.

The goal is not to prove pandas is always better. The goal is to see exactly what semantic guarantee index alignment provides.

---

# 42. Testing strategy

A DataFrame result is not correct merely because its displayed values look right.

Test at least:

```text
shape
row count
columns
dtypes
index
values
index uniqueness where required
alignment semantics where relevant
```

## 42.1 Testing a Series

```python
expected = pd.Series(
    [250.0],
    index=["IN"],
    name="revenue",
)

pd.testing.assert_series_equal(actual, expected)
```

---

## 42.2 Testing a DataFrame

```python
expected = pd.DataFrame({
    "country": ["US", "IN"],
    "revenue": [100, 200],
})

pd.testing.assert_frame_equal(actual, expected)
```

These helpers are useful because they test more than a handful of values.

---

## 42.3 Test the Index explicitly

```python
assert result.index.equals(expected.index)
```

This is important because:

```text
same values
+
wrong index
=
wrong DataFrame semantics
```

---

## 42.4 Test row count as an invariant

For operations where row count should not change:

```python
before_rows = len(df)
out = some_transformation(df)
assert len(out) == before_rows
```

For `set_index` and `reset_index`, the row count should normally remain unchanged.

---

# 43. Production Data Engineering patterns

## 43.1 API extraction

JSON APIs commonly produce a list of records:

```python
records = [
    {"customer_id": "001", "country": "IN", "amount": 100},
    {"customer_id": "002", "country": "US", "amount": 200},
]

df = pd.DataFrame(records)
```

Immediately inspect:

```text
shape
columns
dtypes
index
```

Do not assume API order represents business identity.

---

## 43.2 Revenue reconciliation

Label-indexed Series can make reconciliation semantics explicit:

```python
actual = pd.Series(
    [1000, 2000],
    index=["IN", "US"],
)

expected = pd.Series(
    [1000, 2100],
    index=["US", "IN"],
)
```

Even though the order differs, alignment compares the intended countries.

Then inspect unmatched labels before interpreting differences.

---

## 43.3 Transaction pipelines

A transactions DataFrame might have:

```text
order_id
customer_id
country
amount
created_at
```

The DataFrame Index may remain a simple `RangeIndex` because the business identifiers are explicit columns.

This is often clearer for ETL.

---

## 43.4 Time-series data

For time-series workloads, an Index can be a useful semantic tool because time itself can define the row axis.

That pattern becomes important in Topic 09.

---

## 43.5 Reporting tables

A reporting dataset might naturally be represented as:

```text
(country, month) → revenue
```

A MultiIndex can make that hierarchy explicit during analysis.

Before publishing the output, consider flattening it to:

```text
country | month | revenue
```

if that is easier for downstream consumers.

---

# 44. SQL / Data Engineering conceptual mapping

These are useful conceptual correspondences, not one-to-one replacements.

| Data Engineering idea | pandas concept |
| --- | --- |
| row identifier | Index |
| business key | usually an explicit column |
| table-like dataset | DataFrame |
| single labelled field | Series |
| hierarchy of row labels | MultiIndex |
| key-based alignment | Index alignment |
| row grain | meaning of one row, sometimes reflected in the Index |

The key lesson is that pandas has an explicit label model, while database systems have keys, constraints, and relational semantics that are not identical to pandas.

---

# 45. Common mistakes

## Mistake 1 — Assuming arithmetic is positional

### Why it happens
The DataFrame looks tabular, so the engineer thinks in row positions.

### Example

```python
a + b
```

### Correct approach
Inspect indexes and reason about label alignment.

### Prevention
Predict the result index before execution.

---

## Mistake 2 — Assuming duplicate indexes are always invalid

### Why it happens
Engineers confuse an Index with a unique primary key.

### Correct approach
Ask whether the intended grain requires uniqueness.

### Prevention
Check:

```python
df.index.is_unique
```

only when uniqueness is a business invariant.

---

## Mistake 3 — Treating Index as a business key

### Why it happens
A meaningful identifier often feels like it “should” be the Index.

### Correct approach
Distinguish:

```text
Index
business key
row grain
```

### Prevention
Keep important business identifiers explicit when that makes the pipeline clearer.

---

## Mistake 4 — Forgetting `set_index` changes the DataFrame structure

### Correct approach
Inspect:

```python
print(df.index)
print(df.columns)
```

after structural operations.

---

## Mistake 5 — Using `reset_index()` without understanding `drop`

### Correct approach
Use:

```python
df.reset_index(drop=True)
```

when the old labels should not become a column.

---

## Mistake 6 — Treating alignment-generated NaN as source missingness

### Correct approach
Ask whether the NaN existed before the alignment operation.

---

## Mistake 7 — Assuming RangeIndex has business meaning

### Correct approach
Use explicit business columns for identifiers unless a deliberate Index design says otherwise.

---

## Mistake 8 — Using MultiIndex automatically

### Correct approach
Use it when hierarchical row labels make an operation clearer. Otherwise, explicit columns may be easier to share and maintain.

---

## Mistake 9 — Forgetting MultiIndex ordering

### Correct approach
Inspect:

```python
print(df.index.names)
print(df.index)
```

and sort deliberately where ordering matters.

---

## Mistake 10 — Assuming `add(fill_value=0)` is always correct

### Correct approach
Treat zero-fill as a business-semantic decision.

---

## Mistake 11 — Ignoring Series assignment alignment

### Correct approach
Compare the DataFrame index and Series index before assignment.

---

# 46. Checkpoint

Do not move on until you can do these without copying the examples mechanically.

## Required skills

- [ ] Explain index alignment with an example that produces `NaN`.
- [ ] Explain the difference between a Series and a DataFrame column.
- [ ] Convert an Index into a column with `reset_index()`.
- [ ] Convert a column into an Index with `set_index()`.
- [ ] Select a MultiIndex value using a tuple with `loc`.
- [ ] Select a MultiIndex cross-section with `xs()`.
- [ ] Explain why `RangeIndex` is not automatically a business key.
- [ ] Detect duplicate labels with `is_unique`.
- [ ] Check ordering with `is_monotonic_increasing`.
- [ ] Explain why alignment-generated `NaN` is different from source-data missingness.
- [ ] Explain when ordinary columns may be clearer than an Index.

---

## Checkpoint prediction questions

Do not execute these first.

### 1. Series alignment

```python
a = pd.Series([10, 20], index=["A", "B"])
b = pd.Series([1, 2], index=["B", "C"])
result = a + b
```

Predict:

```text
index = ?
length = ?
A = ?
B = ?
C = ?
```

### 2. `set_index`

```python
df = pd.DataFrame({
    "country": ["US", "IN"],
    "revenue": [100, 200],
})
result = df.set_index("country")
```

Predict:

```text
rows = ?
columns = ?
index = ?
```

### 3. Series assignment

```python
df = pd.DataFrame({"x": [100, 200]}, index=[10, 20])
s = pd.Series([5, 7], index=[20, 10])
df["y"] = s
```

Predict the `y` value for labels `10` and `20`.

### 4. MultiIndex selection

```python
idx = pd.MultiIndex.from_tuples(
    [("US", "2025-01"), ("IN", "2025-01")],
    names=["country", "month"],
)
df = pd.DataFrame({"revenue": [100, 200]}, index=idx)
```

Predict what this selects:

```python
df.loc[("US", "2025-01")]
```

### 5. `xs`

Predict the index of:

```python
df.xs("2025-01", level="month")
```

---

# Quick reference — essential patterns

## Create a Series

```python
series = pd.Series(
    [100, 200, 300],
    index=["US", "IN", "UK"],
    name="revenue",
)
```

## Create a DataFrame

```python
df = pd.DataFrame({
    "order_id": [101, 102],
    "amount": [1000, 2000],
})
```

## Inspect

```python
print(df.head())
print(df.tail())
print(df.sample(2, random_state=42))
print(df.shape)
print(df.columns)
print(df.dtypes)
df.info()
print(df.describe())
print(df["amount"].value_counts())
```

## Inspect Index

```python
print(df.index)
print(df.columns)
print(df.index.is_unique)
print(df.index.is_monotonic_increasing)
```

## Move a column into the Index

```python
indexed = df.set_index("order_id")
```

## Move the Index back to a column

```python
flat = indexed.reset_index()
```

## Rename

```python
renamed = df.rename(columns={"amount": "revenue"})
```

## Drop

```python
trimmed = df.drop(columns=["temporary_column"])
```

## Add a column

```python
df["revenue"] = df["quantity"] * df["unit_price"]
```

## Use `assign`

```python
result = df.assign(
    revenue=lambda x: x["quantity"] * x["unit_price"],
)
```

## Align by labels

```python
result = series_a + series_b
```

## Fill unmatched values for an operation

```python
result = series_a.add(series_b, fill_value=0)
```

## Create a MultiIndex

```python
indexed = df.set_index(["country", "month"])
```

## Select one MultiIndex key

```python
row = indexed.loc[("US", "2025-01")]
```

## Select a cross-section

```python
country_view = indexed.xs("US", level="country")
```

## Change MultiIndex level order

```python
swapped = indexed.swaplevel("country", "month")
```

## Sort the MultiIndex

```python
sorted_df = indexed.sort_index()
```

## Flatten a MultiIndex

```python
flat = indexed.reset_index()
```

---

# Topic 01 completion standard

You are ready for Topic 02 when you can independently:

1. create Series and DataFrames from dictionaries, records, and NumPy arrays;
2. explain every part of a Series and DataFrame you create;
3. inspect a DataFrame's shape, columns, dtypes, index, and basic profile;
4. explain labels versus positions;
5. use `set_index`, `reset_index`, and `rename` correctly;
6. predict Series arithmetic results from the Index before running the code;
7. distinguish alignment-generated `NaN` from source-data missingness;
8. validate duplicate labels and index ordering;
9. manage columns deliberately;
10. create, select, reorder, and flatten a MultiIndex;
11. explain when an Index is useful and when ordinary columns are clearer;
12. complete the `index_alignment.py` exercise with tests for expected index, row count, and values.

The next module topic starts from this foundation and asks a different question:

> **How do I read and write production data sources while keeping the schema and types under control?**
