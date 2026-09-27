# DataFrames with pandas — 60 Interview Questions and Solutions

## How to Use This Interview Set

Treat each question as a live interview prompt. Answer verbally before reading the model answer. A strong response should make assumptions explicit, define the table grain and keys, predict the output, choose the pandas operation, validate the result, and discuss scale or failure modes when relevant.

Use this loop:

```text
Read the question
      ↓
Clarify assumptions
      ↓
Define grain and keys
      ↓
Think aloud
      ↓
Predict behavior/output
      ↓
Give approach
      ↓
Code if required
      ↓
Validate
      ↓
Discuss edge cases
      ↓
Discuss performance/scale
```

For coding questions, first design the transformation in words. For debugging questions, state the observed symptom, likely root cause, diagnostic checks, fix, and regression test.

## Difficulty Guide

- **Basic (Q01–Q15):** strong pandas fundamentals and semantic understanding.
- **Moderate (Q16–Q30):** multiple concepts, code reading, debugging, and trade-offs.
- **Hard (Q31–Q45):** realistic Data Engineering scenarios, correctness, validation, performance, and failure analysis.
- **Advanced (Q46–Q60):** senior-level pipeline design, memory, state, idempotency, reconciliation, and engine-selection reasoning.

---

# Part 1 — Basic

### Q01 — Why can pandas arithmetic create `NaN` even when both Series contain numbers?

**Difficulty:** Basic  
**Topics:** Topic 01 — Series/DataFrame/Index

#### Interview Question

Consider:

```python
import pandas as pd

left = pd.Series([10, 20, 30], index=["A", "B", "C"])
right = pd.Series([1, 2, 3], index=["B", "C", "D"])

result = left + right
```

What is the result, and why? Explain the role of the Index. How is this different from position-by-position arithmetic?

#### What the Interviewer Is Testing

Whether you understand pandas label alignment rather than treating a Series as an anonymous NumPy array.

#### Expected Candidate Approach

1. Inspect both indexes.
2. Notice that pandas aligns by label.
3. Predict the union of labels.
4. Identify which labels have no matching value.
5. Explain why unmatched labels produce missing values.

#### Model Answer

The result is:

```text
A     NaN
B    21.0
C    32.0
D     NaN
dtype: float64
```

Pandas aligns the operands by **Index label**:

- `B`: `20 + 1 = 21`
- `C`: `30 + 2 = 32`
- `A` has no match in `right`
- `D` has no match in `left`

Therefore unmatched labels receive `NaN`.

This is a correctness feature in labeled data processing, but it can also surprise someone expecting positional arithmetic.

#### Step-by-Step Reasoning

The left Series has labels `A, B, C`; the right has `B, C, D`. The arithmetic operates on the label union `A, B, C, D`, not the first element with the first element.

This is one reason an Index is semantically important in pandas: it carries alignment information.

#### Common Candidate Mistake

Saying the output is `[11, 22, 33]` because they assume positions are used.

#### Production Perspective

Before doing arithmetic between Series from different sources, check whether the indexes represent the same entity and grain. A label mismatch can silently introduce missing values or misalignment.

---

### Q02 — How would you profile a new DataFrame and select columns by schema?

**Difficulty:** Basic  
**Topics:** Topic 01 — inspection; Topic 03 — selection

#### Interview Question

You receive:

```python
df = pd.DataFrame(
    {
        "customer_id": [101, 102, 103, 103],
        "country": ["IN", "US", "IN", "IN"],
        "amount_cents": [500, 900, None, 700],
        "debug_flag": [True, False, True, False],
    }
)
```

Explain how you would inspect the schema and then select only numeric columns or columns whose names contain `"amount"`.

#### What the Interviewer Is Testing

Whether you can profile structure before transformation and use schema-aware selection instead of manually guessing columns.

#### Expected Candidate Approach

Start with `shape`, `columns`, `dtypes`, `info`, and representative values. Then use `select_dtypes()` or `filter()` when selection is based on column metadata.

#### Model Answer

```python
print(df.shape)
print(df.columns)
print(df.dtypes)
df.info()
print(df.head())
print(df.describe(include="all"))

numeric = df.select_dtypes(include="number")
amount_cols = df.filter(like="amount")
debug_cols = df.filter(regex=r"^debug_")

assert "amount_cents" in numeric.columns
assert list(amount_cols.columns) == ["amount_cents"]
assert list(debug_cols.columns) == ["debug_flag"]
```

#### Step-by-Step Reasoning

`select_dtypes()` selects based on dtype, while `filter(like=...)` and `filter(regex=...)` select based on column labels. These answer different questions.

#### Production Perspective

Schema-driven selection is safer when upstream schemas evolve. It also reduces accidental inclusion of operational/debug columns.

### Q03 — What is the difference between `loc` and `iloc`?

**Difficulty:** Basic  
**Topics:** Topic 03 — Selection

#### Interview Question

Given:

```python
df = pd.DataFrame(
    {"amount": [10, 20, 30, 40, 50]},
    index=[10, 11, 12, 13, 14],
)

loc_result = df.loc[10:12]
iloc_result = df.iloc[0:3]
```

What rows are returned by each expression?

#### What the Interviewer Is Testing

Label-based versus positional indexing and inclusive/exclusive slicing rules.

#### Expected Candidate Approach

Identify that the index labels are `10–14`, then distinguish label slicing from positional slicing.

#### Model Answer

Both expressions return three rows in this particular example:

```text
      amount
10       10
11       20
12       30
```

But they reach that result differently.

- `loc[10:12]` is **label-based** and label slicing is inclusive of the endpoint.
- `iloc[0:3]` is **position-based** and the stop position is exclusive, so positions `0, 1, 2` are selected.

The important difference is semantic, not the coincidental output here.

#### Common Candidate Mistake

Saying `.loc[10:12]` means positions 10, 11, and 12.

#### Production Perspective

Use `.loc` when the business logic is expressed in labels and `.iloc` when the logic is explicitly positional.

---

### Q04 — How do you write a safe boolean filter in pandas?

**Difficulty:** Basic  
**Topics:** Topic 03 — Boolean filtering

#### Interview Question

Filter the DataFrame below to orders from India or Singapore with an amount between 500 and 1,000 inclusive:

```python
orders = pd.DataFrame(
    {
        "country": ["IN", "US", "SG", "IN"],
        "amount": [700, 900, 600, 1200],
    }
)
```

#### What the Interviewer Is Testing

Boolean mask construction, vectorized operators, parentheses, `isin`, and `between`.

#### Expected Candidate Approach

Combine vectorized boolean conditions with `&`, and use parentheses around each condition.

#### Model Answer

```python
result = orders.loc[
    orders["country"].isin(["IN", "SG"])
    & orders["amount"].between(500, 1000)
].copy()

assert len(result) == 2
```

The result contains the first and third rows.

#### Step-by-Step Reasoning

`isin(["IN", "SG"])` creates one Boolean Series. `between(500, 1000)` creates another. `&` combines them element by element.

Do not use Python's scalar `and` operator for pandas Series.

#### Common Candidate Mistake

Writing:

```python
orders[(orders["country"] == "IN" or orders["country"] == "SG")]
```

This fails because `or` expects a single truth value, while a Series contains many Boolean values.

#### Production Perspective

For readable complex predicates, `query()` can be useful, but `.loc` is often clearer when you need assignment or more explicit Boolean logic.

---

### Q05 — When should an Index be useful, and when should an ETL key remain a normal column?

**Difficulty:** Basic  
**Topics:** Topic 01 — Index/labels; Topic 11 — assign

#### Interview Question

You have:

```python
orders = pd.DataFrame(
    {
        "order_id": ["O1", "O2"],
        "customer_id": ["C1", "C2"],
        "amount": [500, 800],
    }
)
```

Explain:

1. when `set_index("order_id")` could be useful;
2. when `order_id` is clearer as a normal ETL column;
3. how `reset_index()` restores the column;
4. how `assign()` can create a derived field without mutating the source object.

#### Model Answer

```python
indexed = orders.set_index("order_id")

result = orders.assign(
    fee=lambda x: x["amount"] * 0.02
)

restored = indexed.reset_index()

assert indexed.index.name == "order_id"
assert "fee" not in orders.columns
assert "fee" in result.columns
assert "order_id" in restored.columns
```

An Index is useful when label-based lookup, alignment, or time-series semantics are valuable. A normal column is often clearer when the key participates in merges, validation, schema contracts, or business transformations.

#### Production Perspective

Do not use the Index merely because a column is unique. In ETL code, explicit columns are often easier to inspect and validate.

### Q06 — Why should identifiers such as account numbers usually not be inferred as integers?

**Difficulty:** Basic  
**Topics:** Topic 02 — I/O; Topic 04 — dtypes/schema

#### Interview Question

A CSV contains:

```text
account_id,amount
001245,500
001246,700
```

Why is loading `account_id` as an integer dangerous? Show a reader contract.

#### Model Answer

The leading zeros are part of the identifier's representation. Numeric conversion would turn `001245` into `1245`, losing information.

Use an explicit string dtype:

```python
df = pd.read_csv(
    "accounts.csv",
    dtype={"account_id": "string"},
)
```

#### Step-by-Step Reasoning

An identifier answers “which record/entity?” rather than “how much?” Arithmetic semantics are not required, so integer storage is usually inappropriate.

#### Common Candidate Mistake

Choosing `int64` simply because every value contains digits.

#### Production Perspective

Data ingestion should encode **semantic types**, not only lexical appearance. This matters for IDs, postal codes, product codes, and other zero-padded keys.

---

### Q07 — What problem do nullable integer dtypes solve?

**Difficulty:** Basic  
**Topics:** Topic 04 — Nullable dtypes

#### Interview Question

You need an integer `customer_id` column that can contain missing values. Explain why `Int64` may be preferable to ordinary `int64`, and how `pd.NA` participates in comparisons.

#### Model Answer

```python
df = pd.DataFrame(
    {"customer_id": [101, None, 103]}
).astype({"customer_id": "Int64"})

print(df.dtypes)
```

`Int64` is pandas' nullable integer dtype. It allows integer values plus `pd.NA` without forcing the entire column to floating-point representation.

Pandas' nullable logic can produce an indeterminate result:

```python
mask = df["customer_id"] == 101
```

The missing row does not become a normal Python `False`; it participates in pandas' missing-value semantics.

#### Why This Matters

There is a difference between:

- “the ID is not 101” and
- “we do not know the ID.”

That distinction matters for filtering and downstream data-quality rules.

#### Common Candidate Mistake

Converting nullable identifiers to float just to accommodate missing values.

#### Production Perspective

Choose nullable dtypes when missingness is meaningful and the column's logical type should remain integer.

---

### Q08 — When should you drop, fill, or preserve missing values?

**Difficulty:** Basic  
**Topics:** Topic 05 — Cleaning

#### Interview Question

You have:

```python
df = pd.DataFrame(
    {
        "customer": ["A", "B", "C"],
        "age": [30, None, 40],
        "discount": [0.0, None, 10.0],
    }
)
```

Should the missing discount automatically be replaced by zero? What about age?

#### Model Answer

Not automatically.

A domain-aware decision is required:

- `age`: a missing value means “unknown age”; filling with zero would create a false fact.
- `discount`: zero might mean “no discount,” but a missing value might instead mean “discount was not provided.” Those are not necessarily equivalent.

For example:

```python
age_missing = df["age"].isna()
discount_missing = df["discount"].isna()

assert age_missing.sum() == 1
assert discount_missing.sum() == 1
```


#### Production Example: Choosing a Fill Rule

For a field where the business contract explicitly says missing means unknown, preserve the missing value. When the business contract says a missing value means a known default, `fillna()` can encode that rule:

```python
filled = df["discount"].fillna(0)
```

The important interview answer is not “use `fillna`”; it is “use `fillna` only when zero is the correct semantic default.”

#### Production Perspective

Missing-value handling should follow business semantics. “Make the null disappear” is not a data-quality strategy.

---

### Q09 — Why can `count()` and `size()` disagree?

**Difficulty:** Basic  
**Topics:** Topic 06 — groupby

#### Interview Question

Given:

```python
df = pd.DataFrame(
    {
        "country": ["IN", "IN", "US"],
        "amount": [100, None, 200],
    }
)
```

What is the difference between:

```python
df.groupby("country")["amount"].count()
```

and:

```python
df.groupby("country").size()
```

#### Model Answer

`count()` counts **non-missing values in the selected column**.

`size()` counts **rows in each group**.

For this data:

```text
country
IN    1
US    1
Name: amount, dtype: int64
```

for `count()`, while:

```text
country
IN    2
US    1
dtype: int64
```

for `size()`.

#### Step-by-Step Reasoning

The `IN` group has two rows but only one non-null `amount`.

#### Common Candidate Mistake

Using `count()` as a row-count check when the measure itself can be null.

#### Production Perspective

For cardinality and row-preservation checks, `size()` is often the clearer metric. Use `count()` when non-null measure count is what you actually mean.

---

### Q10 — Predict the row count of a basic left join

**Difficulty:** Basic  
**Topics:** Topic 07 — merge/cardinality

#### Interview Question

You have:

```python
orders = pd.DataFrame(
    {"order_id": [1, 2, 3], "customer_id": [10, 11, 12]}
)

customers = pd.DataFrame(
    {"customer_id": [10, 11, 13], "segment": ["A", "B", "C"]}
)
```

Before running the merge, how many rows should a left join produce?

```python
result = orders.merge(customers, on="customer_id", how="left")
```

#### Model Answer

The expected row count is **3**.

The left table has three order rows, and the customer table has at most one matching row for each key.

```python
result = orders.merge(
    customers,
    on="customer_id",
    how="left",
    validate="many_to_one",
)

assert len(result) == len(orders) == 3
```

`customer_id=12` remains in the output with a missing `segment`.

#### Production Perspective

For a many-to-one enrichment, row preservation is an invariant. `validate="many_to_one"` turns that assumption into an executable contract.

---

### Q11 — Why would you melt a wide report into long format?

**Difficulty:** Basic  
**Topics:** Topic 08 — Reshaping

#### Interview Question

Transform:

```python
wide = pd.DataFrame(
    {
        "product": ["A", "B"],
        "jan": [10, 20],
        "feb": [12, 22],
    }
)
```

into a tidy long representation with columns `product`, `month`, and `units`.

#### Model Answer

```python
long = wide.melt(
    id_vars="product",
    value_vars=["jan", "feb"],
    var_name="month",
    value_name="units",
)

assert len(long) == 4
assert list(long.columns) == ["product", "month", "units"]
```

#### Why This Works

`product` identifies the entity. The month names are measurements represented as separate columns in the wide input, so `melt()` moves that dimension into rows.

The long grain is one row per `product × month`.

#### Production Perspective

Long/tidy data often composes better with grouping, filtering, validation, and visualization, while wide data can be convenient for final presentation.

---

### Q12 — What is the difference between parsing timestamps and extracting datetime features?

**Difficulty:** Basic  
**Topics:** Topic 09 — Time series; Topic 10 — datetime accessors

#### Interview Question

Given:

```python
df = pd.DataFrame(
    {"created_at": ["2026-01-02 13:45:00", "bad"]}
)
```

Parse the column and create a `month` feature.

#### Model Answer

```python
df["created_at"] = pd.to_datetime(
    df["created_at"],
    format="%Y-%m-%d %H:%M:%S",
    errors="coerce",
)

df["month"] = df["created_at"].dt.month

assert df["created_at"].notna().sum() == 1
assert df["month"].iloc[0] == 1
```

#### Step-by-Step Reasoning

`to_datetime` converts the string representation into an actual datetime dtype. `dt.month` then extracts a component from that typed datetime column.

The malformed value becomes missing because `errors="coerce"` was explicitly requested.

#### Common Candidate Mistake

Calling `.dt.month` on a string column.

#### Production Perspective

Count conversion failures instead of silently accepting them:

```python
conversion_failures = (
    df["created_at"].isna().sum()
)
```

after parsing, with an appropriate definition of which missing values were pre-existing.

---

### Q13 — How would you normalize strings safely for joins and labels?

**Difficulty:** Basic  
**Topics:** Topic 10 — String accessors; Topic 04 — string dtype

#### Interview Question

A customer master contains:

```python
df = pd.DataFrame(
    {
        "country": [" in ", "US", " sg ", None],
        "first_name": ["Ada", "Grace", None, "Lin"],
        "last_name": ["Lovelace", "Hopper", "Chen", "Wen"],
    }
)
```

Create a normalized country key and a display name. Explain how you would combine string columns and how missing values affect `contains()`.

#### What the Interviewer Is Testing

String dtype, whitespace/case normalization, safe missing handling, and composition of `.str` operations.

#### Expected Candidate Approach

Use explicit string dtype, normalize Unicode/whitespace, and use vectorized accessors. Avoid row-wise Python functions unless there is no suitable vectorized operation.

#### Model Answer

```python
df["country_key"] = (
    df["country"]
    .astype("string")
    .str.normalize("NFKC")
    .str.strip()
    .str.upper()
)

df["display_name"] = (
    df["first_name"]
    .astype("string")
    .str.cat(
        df["last_name"].astype("string"),
        sep=" ",
    )
)

contains_a = df["display_name"].str.contains(
    "a",
    case=False,
    na=False,
)

assert df["country_key"].tolist() == ["IN", "US", "SG", pd.NA]
assert contains_a.tolist() == [True, False, False, True]
```

#### Step-by-Step Reasoning

`strip()` removes invisible leading/trailing whitespace, `normalize("NFKC")` handles compatible Unicode representations, and `upper()` provides a stable case representation.

`str.cat()` combines string Series vectorially. `contains(..., na=False)` makes the Boolean result explicitly missing-safe.

#### Production Perspective

Use normalized derived keys for matching while preserving raw source values for auditability.

### Q14 — Why can `pivot()` fail while `pivot_table()` succeeds?

**Difficulty:** Basic  
**Topics:** Topic 08 — Reshaping

#### Interview Question

Consider:

```python
df = pd.DataFrame(
    {
        "product": ["A", "A", "B"],
        "month": ["Jan", "Jan", "Jan"],
        "units": [10, 12, 20],
    }
)
```

Why will `pivot()` not produce a single `A × Jan` cell, and what approach should you use when duplicate keys need aggregation?

#### Model Answer

`pivot()` expects each combination of index and columns to identify a single value. Here `("A", "Jan")` occurs twice.

Use `pivot_table()` when duplicates should be aggregated:

```python
wide = df.pivot_table(
    index="product",
    columns="month",
    values="units",
    aggfunc="sum",
)

assert wide.loc["A", "Jan"] == 22
```

#### Common Candidate Mistake

Assuming `pivot()` automatically sums duplicates.

#### Production Perspective

A duplicate pivot key is often a grain problem. Before choosing an aggregation function, clarify what one row represents and whether summing duplicates is semantically valid.

---

### Q15 — Under Copy-on-Write, why is `.loc` the correct pattern for conditional assignment?

**Difficulty:** Basic  
**Topics:** Topic 12 — Copy-on-Write; Topic 03 — Selection

#### Interview Question

Given:

```python
df = pd.DataFrame({"amount": [100, 200, 300]})
mask = df["amount"] > 150
```

Compare these patterns:

```python
df["amount"][mask] = 0
```

and:

```python
df.loc[mask, "amount"] = 0
```

Which one expresses the intended parent mutation clearly under modern Copy-on-Write rules?

#### Model Answer

Use:

```python
df.loc[mask, "amount"] = 0
```

It explicitly selects rows and the target column in one indexing operation.

The chained form:

```python
df["amount"][mask] = 0
```

depends on mutation through an intermediate object and is not the safe assignment pattern under modern Copy-on-Write.

#### Production Perspective

Make mutation boundaries explicit. In review, a one-step `.loc` assignment is much easier to reason about than chained indexing.

---

# Part 2 — Moderate

### Q16 — How would you select efficiently and defensively when the result may be empty?

**Difficulty:** Moderate  
**Topics:** Topic 03 — selection

#### Interview Question

You need to:

- select rows where `country` is one of a runtime-supplied list;
- require `amount` to be non-null;
- select a label range with `.loc`;
- fetch a single known value with `.at`;
- update matching rows safely;
- explain when `where()` or `mask()` is better than filtering rows away.

#### Model Answer

```python
allowed = ["IN", "SG"]

mask = (
    df["country"].isin(allowed)
    & df["amount"].notna()
)

result = df.loc[mask, ["country", "amount"]].copy()

if not result.empty:
    first_index = result.index[0]
    value = result.at[first_index, "amount"]

df.loc[mask, "amount"] = df.loc[mask, "amount"].clip(lower=0)

kept_shape = df["amount"].where(df["amount"].ge(0))
masked = df["amount"].mask(df["amount"].lt(0))

assert len(result) <= len(df)
```

`.loc` and Boolean masks filter rows. `where()` and `mask()` preserve the original shape while conditionally replacing values.

For positional single-cell access, `iat` is the positional counterpart to label-based `at`.

#### Production Perspective

Empty results are normal in production pipelines. Code should not assume at least one matching row exists.

### Q17 — How would you use `IndexSlice`, `xs()`, and level operations on a MultiIndex?

**Difficulty:** Moderate  
**Topics:** Topic 01 — MultiIndex; Topic 03 — IndexSlice

#### Interview Question

Given a DataFrame indexed by `(country, customer_id, month)`, explain how you would:

1. select all months for customer 101 in India;
2. take a cross-section for one country;
3. change the level order;
4. sort the index after changing it;
5. flatten the MultiIndex when moving back to a normal ETL shape.

#### Model Answer

```python
df = (
    pd.DataFrame(
        {
            "country": ["IN", "IN", "US"],
            "customer_id": [101, 101, 201],
            "month": ["Jan", "Feb", "Jan"],
            "amount": [500, 700, 900],
        }
    )
    .set_index(["country", "customer_id", "month"])
    .sort_index()
)

idx = pd.IndexSlice
selected = df.loc[idx["IN", 101, :], :]

india = df.xs("IN", level="country")
swapped = df.swaplevel("country", "customer_id").sort_index()

flat = df.reset_index()

assert len(selected) == 2
assert india.index.names == ["customer_id", "month"]
assert swapped.index.names[:2] == ["customer_id", "country"]
assert set(flat.columns) >= {"country", "customer_id", "month"}
```

#### Step-by-Step Reasoning

`IndexSlice` is useful for readable MultiIndex slicing. `xs()` selects a cross-section at a named level. `swaplevel()` changes the hierarchical ordering, and `sort_index()` restores predictable ordering.

#### Production Perspective

Use MultiIndex when hierarchy is genuinely useful. Flatten it when handing data to transformations that are clearer with ordinary columns.

### Q18 — How would you choose among CSV, JSON Lines, Excel, Parquet, and SQL reads?

**Difficulty:** Moderate  
**Topics:** Topic 02 — I/O; Topic 04 — schema

#### Interview Question

An ingestion service receives:

- a daily CSV;
- application logs in JSON Lines;
- an analyst-supplied Excel file;
- a large Parquet dataset;
- a database query result.

Explain the pandas read/write choices you would make and name important controls for a production read contract. Include an example of handling malformed CSV rows.

#### What the Interviewer Is Testing

Whether you can choose an I/O API based on source format and define an explicit schema contract.

#### Expected Candidate Approach

Match each source to its reader, control dtypes and parsing, define malformed-row behavior, and prevent accidental index serialization on output.

#### Model Answer

Typical reads are:

```python
csv_df = pd.read_csv(
    "orders.csv",
    dtype={"order_id": "string"},
    usecols=["order_id", "amount"],
    on_bad_lines="error",
)

json_df = pd.read_json(
    "events.jsonl",
    lines=True,
)

excel_df = pd.read_excel(
    "manual_adjustments.xlsx",
)

parquet_df = pd.read_parquet(
    "orders.parquet",
    columns=["order_id", "amount"],
)

# A database result can be read with pd.read_sql(...).
```

Typical writes are:

```python
csv_df.to_csv("orders_out.csv", index=False)
json_df.to_json("events_out.jsonl", orient="records", lines=True)
excel_df.to_excel("adjustments_out.xlsx", index=False)
parquet_df.to_parquet("orders_out.parquet", index=False)
```

If the business policy is to tolerate malformed rows, choose that explicitly with `on_bad_lines` rather than relying on an accidental default.

#### Production Perspective

Other reader controls may include `parse_dates`, explicit `date_format`, `na_values`, `keep_default_na=False`, URLs, supported compression such as `gzip`, and deterministic column ordering. After writing important outputs, a round-trip read and schema check can detect accidental index serialization or dtype changes.

### Q19 — How would you keep the latest record for each business key?

**Difficulty:** Moderate  
**Topics:** Topic 05 — Cleaning; Topic 01 — sorting/index

#### Interview Question

The table grain should become one row per `order_id`, keeping the latest `updated_at` record:

```python
df = pd.DataFrame(
    {
        "order_id": [1, 1, 2, 2],
        "updated_at": [
            "2026-01-01",
            "2026-01-03",
            "2026-01-02",
            "2026-01-01",
        ],
        "status": ["created", "paid", "shipped", "created"],
    }
)
```

How would you implement and validate it?

#### Model Answer

```python
df["updated_at"] = pd.to_datetime(
    df["updated_at"],
    format="%Y-%m-%d",
)

result = (
    df.sort_values(["order_id", "updated_at"])
      .drop_duplicates("order_id", keep="last")
      .reset_index(drop=True)
)

assert len(result) == 2
assert result["order_id"].is_unique
assert dict(zip(result["order_id"], result["status"])) == {
    1: "paid",
    2: "shipped",
}
```

#### Step-by-Step Reasoning

`drop_duplicates` is not enough by itself. The business rule determines which duplicate survives, so first impose a deterministic order.

#### Production Perspective

If ties are possible on `updated_at`, add a deterministic tie-breaker such as ingestion sequence. Never rely on accidental row order.

---

### Q20 — When is `transform()` the right choice instead of `agg()`?

**Difficulty:** Moderate  
**Topics:** Topic 06 — groupby/transform

#### Interview Question

You want a `customer_total` column repeated on every order row so that each order can later be compared with the customer's total. Why is `transform("sum")` appropriate while a grouped `agg("sum")` result is not directly equivalent?

#### Model Answer

Because `transform` returns a result aligned to the original rows:

```python
orders = pd.DataFrame(
    {
        "customer_id": [1, 1, 2],
        "amount": [100, 200, 500],
    }
)

orders["customer_total"] = (
    orders.groupby("customer_id")["amount"]
          .transform("sum")
)

assert orders["customer_total"].tolist() == [300, 300, 500]
```

`agg("sum")` changes the grain to one row per customer:

```python
totals = (
    orders.groupby("customer_id", as_index=False)["amount"]
          .sum()
)
```

That result must be joined back if you need it on every original order.

#### Why This Works

`transform` preserves the original row count and aligns the group result back to the source rows.

#### What a Weak Answer Might Miss

Saying simply “transform is faster” without explaining the difference in **output grain and alignment**.

---

### Q21 — What is the performance and semantic trade-off among `agg`, `transform`, `filter`, and `apply`?

**Difficulty:** Moderate  
**Topics:** Topic 06 — groupby

#### Interview Question

For a customer-order table, explain which operation you would choose to:

- produce one row per customer with totals;
- add a customer total to every order;
- keep only customers whose total exceeds 10,000;
- implement a truly custom per-group rule.

Then explain why you would not automatically reach for `apply()`.

#### Model Answer

```python
customer_totals = (
    orders.groupby("customer_id", as_index=False, sort=False)
          .agg(
              total_amount=("amount", "sum"),
              order_count=("order_id", "size"),
          )
)

orders["customer_total"] = (
    orders.groupby("customer_id")["amount"]
          .transform("sum")
)

large_customers = (
    orders.groupby("customer_id")
          .filter(lambda g: g["amount"].sum() > 10_000)
)
```

Use `apply()` only when the required operation genuinely does not fit the more specialized APIs or vectorized transformations.

#### Step-by-Step Reasoning

- `agg` changes the grain to the group.
- `transform` preserves original row alignment.
- `filter` keeps or removes whole groups.
- `apply` executes arbitrary group-level Python logic and can be slower and harder to reason about.

Groupby options such as `sort=False`, `dropna=False`, and `observed=True` should be chosen when their semantics match the data contract.

#### Production Perspective

Prefer the narrowest operation that expresses the business rule. It improves readability, output-shape reasoning, and often performance.

### Q22 — How would you use `rank`, `cumcount`, `cumsum`, `shift`, and `diff`?

**Difficulty:** Moderate  
**Topics:** Topic 06 — grouped analytical operations

#### Interview Question

For each customer, ordered by timestamp, create:

- sequence number;
- cumulative spend;
- previous spend;
- spend difference from previous order;
- within-customer rank by amount.

#### Model Answer

```python
orders = pd.DataFrame(
    {
        "customer_id": [1, 1, 1, 2],
        "created_at": pd.to_datetime(
            [
                "2026-01-01",
                "2026-01-03",
                "2026-01-05",
                "2026-01-02",
            ]
        ),
        "amount": [100, 150, 120, 300],
    }
).sort_values(["customer_id", "created_at"])

g = orders.groupby("customer_id", sort=False)

orders["seq"] = g.cumcount() + 1
orders["customer_cumsum"] = g["amount"].cumsum()
orders["previous_amount"] = g["amount"].shift(1)
orders["diff_from_previous"] = g["amount"].diff()
orders["amount_rank"] = g["amount"].rank(method="dense", ascending=False)
```

#### Production Perspective

Ordering is part of the business logic. `shift`, `diff`, and cumulative operations are meaningful only after the rows are ordered correctly within each entity.

---

### Q23 — How would you test all major join cardinalities?

**Difficulty:** Moderate  
**Topics:** Topic 07 — merge/join/cardinality

#### Interview Question

Explain the expected behavior of:

```text
one-to-one
one-to-many
many-to-one
many-to-many
```

Also explain when you would use `validate=`, `indicator=True`, `suffixes`, an index-based `join()`, and an outer/cross join.

#### Model Answer

A join contract should start with the expected uniqueness of each side.

Example for a many-to-one enrichment:

```python
result = orders.merge(
    customers,
    on="customer_id",
    how="left",
    validate="many_to_one",
    suffixes=("_order", "_customer"),
)
```

For diagnostics:

```python
diagnostic = orders.merge(
    customers,
    on="customer_id",
    how="left",
    indicator=True,
)
```

`join()` is useful when index-based alignment is the intended relationship:

```python
result = orders.set_index("customer_id").join(
    customer_attributes.set_index("customer_id"),
    how="left",
    lsuffix="_order",
    rsuffix="_customer",
)
```

An `outer` join preserves keys from both sides, while a `cross` join deliberately produces the Cartesian product and therefore can multiply rows dramatically.

#### Step-by-Step Reasoning

One-to-one means each key identifies at most one row on each side. Many-to-one means the left can repeat a key but the right cannot. Many-to-many permits repeated keys on both sides and can create a row explosion.

Null keys also require deliberate reasoning: pandas merge behavior for null-like keys is not identical to the way SQL commonly treats `NULL`. Do not assume SQL semantics without checking the pandas behavior.

#### Production Perspective

Use `validate=` as an executable contract and predict output cardinality before the join. Use `indicator=True` when diagnosing unmatched keys.

### Q24 — How would you perform point-in-time enrichment with `merge_asof`?

**Difficulty:** Moderate  
**Topics:** Topic 07 — `merge_asof`; Topic 09 — time semantics

#### Interview Question

Orders need the latest known FX rate at or before the order timestamp. Explain the preconditions for `merge_asof` and show a minimal implementation.

#### Model Answer

Both inputs must be sorted appropriately by the time key:

```python
orders = orders.sort_values(["currency", "created_at"])
rates = rates.sort_values(["currency", "rate_time"])

enriched = pd.merge_asof(
    orders,
    rates,
    left_on="created_at",
    right_on="rate_time",
    by="currency",
    direction="backward",
    tolerance=pd.Timedelta("1D"),
)
```

`direction="backward"` means “take the latest rate at or before the order timestamp.” `tolerance` limits how old the matching rate may be.

#### What a Strong Answer Should Include

A strong candidate also checks:

- timestamps have compatible timezone semantics;
- both inputs are sorted;
- currency is the intended grouping key;
- missing matches are expected and monitored;
- the time tolerance matches the business rule.

#### Production Perspective

Point-in-time enrichment is not an ordinary equality join. Time semantics are part of the join contract.

---

### Q25 — How would you build a reliable multi-format file ingestion layer?

**Difficulty:** Moderate  
**Topics:** Topic 02 — I/O; Topic 07 — concat

#### Interview Question

A batch contains globbed CSV partitions plus a compressed CSV archive and a JSON Lines log file. The output must have deterministic column order and no accidental index column.

What should the ingestion code pay attention to?

#### Model Answer

Use deterministic file discovery and explicit reader contracts:

```python
from pathlib import Path

paths = sorted(Path("orders").glob("*.csv"))

frames = [
    pd.read_csv(
        path,
        dtype={
            "order_id": "string",
            "customer_id": "string",
        },
    )
    for path in paths
]

combined = pd.concat(
    frames,
    ignore_index=True,
)

combined = combined[
    ["order_id", "customer_id", "amount"]
]

combined.to_csv(
    "orders_out.csv",
    index=False,
)
```

A compressed CSV can use the reader's compression support:

```python
compressed = pd.read_csv(
    "orders.csv.gz",
    compression="gzip",
)
```

JSON Lines uses:

```python
logs = pd.read_json(
    "events.jsonl",
    lines=True,
)
```

#### Production Perspective

A reliable write should first create the intended output, validate schema and row counts, and then publish it safely. Round-trip reads are useful for detecting accidental index serialization or column-order changes.

### Q26 — How would you choose among `stack`, `unstack`, `crosstab`, and `wide_to_long`?

**Difficulty:** Moderate  
**Topics:** Topic 08 — Reshaping; Topic 01 — MultiIndex

#### Interview Question

A reporting table may be:

- aggregated by two categorical dimensions;
- represented with multiple measure columns;
- stored with year embedded in column names;
- needed as a frequency table.

Explain which reshape tools fit each case and how MultiIndex columns should be handled.

#### Model Answer

For a MultiIndex Series:

```python
s = pd.Series(
    [10, 20, 30, 40],
    index=pd.MultiIndex.from_tuples(
        [
            ("IN", "A"),
            ("IN", "B"),
            ("US", "A"),
            ("US", "B"),
        ],
        names=["country", "product"],
    ),
)

wide = s.unstack("product")
long_again = wide.stack()

assert long_again.equals(s)
```

Use `crosstab()` for counts/frequencies:

```python
frequency = pd.crosstab(
    df["country"],
    df["status"],
)
```

For year-embedded columns such as `sales_2025` and `sales_2026`, `wide_to_long()` expresses the stub/year relationship:

```python
long = pd.wide_to_long(
    source,
    stubnames="sales",
    i="product",
    j="year",
    sep="_",
    suffix=r"\d+",
).reset_index()
```

For multiple values/measures and totals, `pivot_table()` can produce MultiIndex columns. Flatten them explicitly when an ETL-friendly schema is required:

```python
summary = df.pivot_table(
    index="country",
    columns="status",
    values=["revenue", "order_id"],
    aggfunc={"revenue": "sum", "order_id": "nunique"},
    margins=True,
)

summary.columns = [
    "_".join(str(part) for part in col if str(part) != "")
    if isinstance(col, tuple)
    else str(col)
    for col in summary.columns
]
```

`get_dummies()` is appropriate when categorical values need one-hot columns, but it can produce column explosion when cardinality is high.

#### Production Perspective

Choose the representation that matches the downstream grain and schema. Always inspect what missing cells mean after a reshape.

### Q27 — Why can `rolling(7)` differ from `rolling("7D")`?

**Difficulty:** Moderate  
**Topics:** Topic 09 — Rolling windows

#### Interview Question

An event stream is irregular:

```text
2026-01-01 09:00
2026-01-01 09:05
2026-01-05 09:00
```

Explain why `rolling(7)` and `rolling("7D")` answer different questions.

#### Model Answer

`rolling(7)` is a **count-based** window: it is about the last seven observations.

`rolling("7D")` is a **time-based** window: it is about observations within a seven-day time interval.

On irregular data, seven rows may span minutes or weeks, while seven days may contain many or few rows.

For a time-based window:

```python
df = df.sort_values("created_at").set_index("created_at")
df["rolling_7d"] = df["amount"].rolling("7D").sum()
```

#### Common Candidate Mistake

Treating the two expressions as interchangeable because both contain `7`.

#### Production Perspective

State the business window in semantic terms first: “last seven events” versus “last seven calendar days.”

---

### Q28 — What is the difference between `tz_localize` and `tz_convert`?

**Difficulty:** Moderate  
**Topics:** Topic 09 — Time zones; Topic 10 — datetime accessors

#### Interview Question

A source system records local timestamps in Asia/Kolkata but stores no timezone information. Later, you need to compare them with UTC timestamps. What is the correct sequence?

#### Model Answer

First **localize** the naive timestamps to the timezone they represent:

```python
ts = pd.to_datetime(
    ["2026-01-01 10:00", "2026-01-01 11:00"]
)

ts = ts.tz_localize("Asia/Kolkata")
```

Then convert the same instant to UTC:

```python
utc = ts.tz_convert("UTC")
```

`tz_localize` assigns timezone meaning to a naive timestamp. `tz_convert` changes representation while preserving the instant in time.

#### What a Weak Answer Might Miss

A weak answer often uses `tz_convert()` on naive timestamps or treats localization as merely formatting.

#### Production Perspective

The key question is: “What instant did this timestamp represent?” Incorrect localization changes time semantics.

---

### Q29 — How would you combine regex extraction, splitting, Unicode normalization, and missing-safe string logic?

**Difficulty:** Moderate  
**Topics:** Topic 10 — strings/regex; Topic 04 — string dtype

#### Interview Question

A customer name field may contain:

```text
"  José de Souza  "
```

and a log field contains key-value data:

```text
"customer=12345 action=LOGIN"
```

Explain how you would:

1. normalize Unicode and whitespace;
2. extract named regex fields;
3. split a compound field when useful;
4. count missing-safe matches.

#### Model Answer

```python
df["name_normalized"] = (
    df["name"]
    .astype("string")
    .str.normalize("NFKC")
    .str.strip()
)

parsed = df["message"].str.extract(
    r"customer=(?P<customer>\d+)\s+"
    r"action=(?P<action>\w+)"
)

has_login = df["message"].str.contains(
    "LOGIN",
    na=False,
)
```

For structured compound text:

```python
parts = df["name_normalized"].str.split(
    " ",
    expand=True,
)
```

Other useful operations include `rsplit()`, `partition()`, `findall()`, and `extractall()` when the source contains multiple matches per row.

#### Production Perspective

Normalize invisible whitespace and Unicode before using strings as keys. Missing-safe operations such as `na=False` prevent missing values from producing unexpected Boolean results.

### Q30 — How would you refactor a difficult chain and expose reusable quality checks?

**Difficulty:** Moderate  
**Topics:** Topic 11 — chaining/pipe/accessors; Topic 12 — CoW

#### Interview Question

A pipeline performs cleaning, type conversion, and validation in one chain. Reviewers cannot easily reuse its checks. How could named functions, `pipe()`, and a registered DataFrame accessor improve the design?

#### Model Answer

Named functions give semantic boundaries:

```python
def add_quality_flags(frame):
    out = frame.copy()
    out["is_missing_amount"] = out["amount"].isna()
    return out

def validate_keys(frame):
    assert frame["order_id"].is_unique
    return frame

result = (
    df
    .pipe(add_quality_flags)
    .pipe(validate_keys)
)
```

The module also demonstrates the concept of custom DataFrame accessors using:

```python
@pd.api.extensions.register_dataframe_accessor("dq")
class DataQualityAccessor:
    ...
```

The accessor can expose reusable checks such as `df.dq.null_report()` and `df.dq.duplicate_report()`.

#### Production Perspective

Use `pipe()` for composable functions and accessors for reusable domain-oriented inspection APIs. Keep the transformations testable independently. Avoid defaulting to `inplace=True`; returning a new logical result often makes function boundaries clearer.

### Q31 — A many-to-one join doubled revenue. Diagnose it.

**Difficulty:** Hard  
**Topics:** Topic 07 — Join cardinality; Topic 05 — Cleaning

#### Interview Question

Orders contain one row per order. The customer dimension is supposed to contain one row per customer, but after joining:

```python
orders["amount"].sum()
```

is 100,000 while the joined result sums to 200,000.

What would you investigate before changing the arithmetic?

#### What the Interviewer Is Testing

Join-cardinality reasoning, duplicate-key diagnosis, row-count reconciliation, and data-quality thinking.

#### Expected Candidate Approach

1. Define the intended grain.
2. Check customer key uniqueness.
3. Predict the legal cardinality.
4. Reproduce the join with validation.
5. Identify duplicate dimension rows.
6. Reconcile row counts and totals.

#### Model Answer

The first suspicion is duplicate customer keys in the dimension, causing a many-to-many or one-to-many multiplication.

Check:

```python
dup_customers = (
    customers.loc[
        customers["customer_id"].duplicated(keep=False)
    ]
    .sort_values("customer_id")
)

assert customers["customer_id"].is_unique
```

Then rerun the intended contract:

```python
enriched = orders.merge(
    customers,
    on="customer_id",
    how="left",
    validate="many_to_one",
)

assert len(enriched) == len(orders)
assert enriched["amount"].sum() == orders["amount"].sum()
```

If validation fails, fix the **dimension data quality or grain**, not the revenue calculation.

#### Step-by-Step Reasoning

The order amount is already measured at order grain. A correct many-to-one enrichment should attach attributes without changing order grain.

A duplicate dimension row turns one order into multiple joined rows. Revenue is therefore repeated.

#### What a Weak Answer Might Miss

A weak answer may suggest dividing revenue by two without identifying the structural source of the inflation.

#### What a Strong Answer Should Include

A strong interview answer explicitly states:

```text
one row = one order
customer_id should be unique on the right
expected output rows = input order rows
revenue must be conserved
```

#### Production Perspective

Join contracts are data-quality controls. A silent cardinality violation can corrupt every downstream metric.

---

### Q32 — Design cleaning rules using normalization, flags, outliers, and quarantine.

**Difficulty:** Hard  
**Topics:** Topic 05 — Cleaning; Topic 04 — dtypes; Topic 11 — validation

#### Interview Question

A transaction feed contains:

- whitespace/case variation in `country`;
- negative amounts that are invalid by domain rule;
- occasional extreme values that may be genuine;
- duplicate business keys;
- missing values in optional fields.

Explain when you would normalize, `replace`/`map`, clip, flag, or quarantine.

#### Model Answer

Normalize keys:

```python
df["country"] = (
    df["country"]
    .astype("string")
    .str.strip()
    .str.upper()
)
```

Use `replace` or `map` for controlled code translation:

```python
df["country"] = df["country"].replace(
    {"UK": "GB"}
)
```

Domain-invalid negatives can be flagged or quarantined:

```python
df["is_outlier"] = df["amount"] < 0
```

For a bounded-but-valid metric where clipping is explicitly part of the business rule:

```python
df["bounded_score"] = df["score"].clip(0, 100)
```

For statistical review, the module's IQR and z-score approaches can identify suspicious values, but they should not automatically delete them.

Duplicate keys can be identified with normalized keys plus:

```python
df["is_duplicate"] = df.duplicated(
    ["account_id", "transaction_id"],
    keep=False,
)
```

#### Step-by-Step Reasoning

The action depends on semantics:

```text
normalize → make equivalent representations comparable
fix       → correct a known deterministic defect
flag      → preserve the record while marking concern
quarantine → exclude from trusted output but retain evidence
clip      → enforce a known bounded domain rule
drop      → use only when the business contract explicitly permits loss
```

#### Production Perspective

Extreme values can be legitimate. A production Silver pipeline should prefer explicit flags and quarantine for uncertain anomalies rather than blind deletion.

### Q33 — How would you use nullable dtypes, categories, and explicit schema checks?

**Difficulty:** Hard  
**Topics:** Topic 04 — dtypes/schema

#### Interview Question

A dataset has:

```text
customer_id   integer-like, sometimes missing
status        one of a controlled set of values
amount_cents  money represented in whole cents
```

Explain the dtype design and how you would measure conversion failures, category state, and memory.

#### Model Answer

```python
df["customer_id"] = pd.to_numeric(
    df["customer_id"],
    errors="coerce",
).astype("Int64")

df["status"] = (
    df["status"]
    .astype("string")
    .astype("category")
)

converted = pd.to_numeric(
    df["amount_cents"],
    errors="coerce",
)

conversion_failures = (
    df["amount_cents"].notna()
    & converted.isna()
).sum()

df["amount_cents"] = converted.astype("Int64")

memory_before = df.memory_usage(deep=True).sum()
```

For modern dtype normalization, `convert_dtypes()` can be used when its inferred semantics match the schema. A project may choose a NumPy-nullable or PyArrow-backed `dtype_backend` when that representation is part of the contract.

Category values and codes can be inspected:

```python
print(df["status"].cat.categories)
print(df["status"].cat.codes)
```

Category vocabulary can be managed explicitly:

```python
df["status"] = df["status"].cat.add_categories(["PENDING"])
df["status"] = df["status"].cat.rename_categories(
    lambda value: value.upper()
)
df["status"] = df["status"].cat.reorder_categories(
    ["PENDING", "PAID", "FAILED"],
    ordered=True,
)
df["status"] = df["status"].cat.remove_unused_categories()
```

When grouping categorical fields, `observed=True` is useful when only combinations actually present in the data should be returned.

#### Production Perspective

Nullable integers preserve integer semantics alongside missingness. Categories can reduce memory for suitable low-cardinality fields, but category ordering and vocabulary are semantic schema decisions.

Exact money may require integer cents, `Decimal`, or an Arrow decimal representation depending on the precision and storage contract. Timestamp resolution and supported datetime bounds also matter when ingesting high-resolution or historical data.

### Q34 — How would you rank within groups, find top-N rows, and avoid an unnecessary `apply()`?

**Difficulty:** Hard  
**Topics:** Topic 06 — groupby

#### Interview Question

For each customer, you need:

- rank of each order by amount;
- event sequence number;
- cumulative customer spend;
- previous amount;
- change from the previous amount;
- top three orders.

How would you implement it, and where could `nlargest()` fit?

#### Model Answer

```python
orders = orders.sort_values(
    ["customer_id", "created_at", "order_id"]
)

g = orders.groupby(
    "customer_id",
    sort=False,
)

orders["amount_rank"] = g["amount"].rank(
    method="first",
    ascending=False,
)

orders["seq"] = g.cumcount() + 1
orders["customer_cumsum"] = g["amount"].cumsum()
orders["previous_amount"] = g["amount"].shift()
orders["amount_diff"] = g["amount"].diff()

top3 = (
    orders.sort_values(
        ["customer_id", "amount"],
        ascending=[True, False],
    )
    .groupby("customer_id", sort=False)
    .head(3)
)
```

For a Series where the requirement is specifically “largest values per group,” grouped `nlargest()` can express that directly in suitable cases.

#### Step-by-Step Reasoning

These operations preserve row-level information. The sort order defines the semantics of sequence, lag, and difference. A group reduction such as `agg()` would not preserve the original order-level rows.

For custom group logic, `apply()` remains a tool, but use it because the logic truly requires arbitrary Python code, not simply because a grouping exists.


A time-based grouping can use `pd.Grouper`:

```python
daily = (
    orders.groupby(
        ["customer_id", pd.Grouper(key="created_at", freq="D")],
        as_index=False,
    )
    ["amount"]
    .sum()
)
```

Here the grouping changes the grain to one row per customer × day.

#### Production Perspective

Define tie-breaking explicitly. For reproducibility, include a stable secondary key such as `order_id`.

### Q35 — How do you distinguish missing from zero after reshaping?

**Difficulty:** Hard  
**Topics:** Topic 08 — Reshaping; Topic 05 — Missing values

#### Interview Question

A sales table contains one row per `product × month` when a product has recorded sales. After pivoting, some product-month cells are missing. Should they become zero?

#### Model Answer

Not automatically.

A missing pivot cell can mean either:

1. the product had no sales event, so zero may be the intended measure; or
2. the source data is incomplete, so the value is genuinely unknown.

For example:

```python
wide = sales.pivot_table(
    index="product",
    columns="month",
    values="revenue",
    aggfunc="sum",
)
```

Only use:

```python
fill_value=0
```

when domain semantics establish that “no row” means zero activity.

#### Common Candidate Mistake

Treating every missing reshaped cell as a numeric zero.

#### Production Perspective

Before filling reshaped data, define whether the complete calendar/grid exists independently of observed events.

---

### Q36 — How would you validate a complete time series with `asfreq()` and explicit calendars?

**Difficulty:** Hard  
**Topics:** Topic 09 — Time series

#### Interview Question

An operational metric should have an hourly value for every hour in a reporting day, but the input only contains observed events. Explain how you would detect missing periods and how `asfreq()`, upsampling, `ffill()`, `bfill()`, `interpolate()`, and business day calendars differ conceptually.

#### Model Answer

Make the time index explicit and sorted:

```python
hourly = (
    df.sort_values("timestamp")
      .set_index("timestamp")
)

complete = hourly.asfreq("h")
```

`asfreq()` exposes missing periods at the requested frequency.

For a state-like signal, forward-fill may be appropriate:

```python
state = hourly.asfreq("h").ffill()
```

Backward fill is sometimes appropriate when the next known state is the intended value:

```python
filled_backwards = hourly.asfreq("h").bfill()
```

For a genuinely continuous numeric measure, interpolation may be appropriate:

```python
interpolated = hourly["value"].interpolate()
```

Those are different semantic operations and should not be swapped just to remove `NaN`.

Business-day calendars matter when “every day” excludes weekends or includes a business-specific holiday calendar.

#### Production Perspective

For event counts, a missing hour can mean zero activity or a broken extract. Do not fill it until the business semantics are known.

### Q37 — How should a rolling metric handle DST, ambiguous timestamps, and late-arriving events?

**Difficulty:** Hard  
**Topics:** Topic 09 — Time series; Topic 10 — datetime

#### Interview Question

A 24-hour metric is reported in a local timezone. The reporting period crosses a DST transition, and a late event arrives after publication. What time semantics should the pipeline use?

#### Model Answer

Represent instants unambiguously, preferably in UTC, and convert to the reporting timezone for local reporting semantics:

```python
df["event_time"] = pd.to_datetime(
    df["event_time"],
    utc=True,
)

df["local_time"] = df["event_time"].dt.tz_convert(
    "Europe/London"
)
```

For naive local timestamps, `tz_localize()` is where DST problems such as nonexistent or ambiguous local times must be handled. `tz_convert()` changes the representation of an already timezone-aware instant.

For a time-based window:

```python
events = (
    df.sort_values("event_time")
      .set_index("event_time")
)

events["rolling_24h"] = (
    events["amount"]
    .rolling("24H")
    .sum()
)
```

A late event with event time inside an already published window requires recomputation of affected output if the reporting contract is event-time correct.

#### Production Perspective

Time correctness requires explicit treatment of UTC, local calendar boundaries, DST transitions, and late-arriving data. These are separate concerns from displaying timestamps.

### Q38 — Code review: which parts of this pipeline hide data-quality and CoW problems?

**Difficulty:** Hard  
**Topics:** Topics 03, 05, 11, 12

#### Interview Question

Review:

```python
df["country"] = df["country"].str.upper()
df["amount"][df["amount"] < 0] = 0
df = df.dropna()
df = df.groupby("customer_id").apply(...)
```

What would you challenge in an interview code review?

#### Model Answer

I would challenge four assumptions.

1. String normalization may need `strip()`, Unicode normalization, and explicit `string` dtype:

```python
df["country"] = (
    df["country"]
    .astype("string")
    .str.normalize("NFKC")
    .str.strip()
    .str.upper()
)
```

2. Chained assignment should be replaced:

```python
df.loc[df["amount"] < 0, "amount"] = 0
```

but only if zero is actually the correct business treatment.

3. `dropna()` without a subset silently removes rows based on every column. Missing-value handling should be field-specific.

4. `groupby().apply()` may be slower or unnecessarily general if a vectorized groupby operation expresses the rule.

#### Production Perspective

Code review should ask what assumptions are hidden: null semantics, anomaly treatment, group grain, mutation behavior, and whether the transformation is testable as a named step.

### Q39 — Why is averaging chunk averages generally incorrect?

**Difficulty:** Hard  
**Topics:** Topic 13 — Chunking; Topic 06 — aggregation

#### Interview Question

A 20 GB file is processed in chunks. Each chunk computes:

```python
chunk["amount"].mean()
```

A developer then takes the average of those chunk means. Why is this generally wrong, and what should replace it?

#### Model Answer

Chunk averages give each chunk equal weight, even when chunks contain different numbers of valid observations.

Suppose chunk A has 100 rows and mean 10, while chunk B has 10 rows and mean 100. The simple average is 55, but the overall mean is:

```text
(100 * 10 + 10 * 100) / 110
= 18.1818...
```

The correct streaming sufficient statistics are `sum` and `count`:

```python
total_sum = 0.0
total_count = 0

for chunk in pd.read_csv("large.csv", chunksize=100_000):
    values = pd.to_numeric(chunk["amount"], errors="coerce")
    total_sum += values.sum()
    total_count += values.count()

overall_mean = total_sum / total_count
```

#### Production Perspective

A chunkable computation is one where partial results can be combined without losing the information required to obtain the global result.

---

### Q40 — Why does per-chunk `drop_duplicates()` not guarantee global uniqueness?

**Difficulty:** Hard  
**Topics:** Topic 13 — Chunking; Topic 05 — deduplication

#### Interview Question

A 20 GB CSV is processed with:

```python
for chunk in pd.read_csv("large.csv", chunksize=100_000):
    clean = chunk.drop_duplicates("order_id")
```

Yet the final output still contains duplicate order IDs. Explain the bug and what state is required.

#### Model Answer

A duplicate can occur once in chunk A and again in chunk B. Each chunk knows only about its local rows, so local deduplication cannot detect cross-chunk duplicates.

You need cross-chunk state representing the business keys already retained:

```python
seen = set()

for chunk in pd.read_csv("large.csv", chunksize=100_000):
    keep = ~chunk["order_id"].isin(seen)
    clean = chunk.loc[keep].copy()

    seen.update(clean["order_id"].dropna().tolist())
```

For very high-cardinality keys, an in-memory `set` may itself become too large, so the architecture must reconsider state storage or execution strategy.

#### Production Perspective

Chunking changes the problem from “transform each block” to “transform each block plus manage state that crosses boundaries.”

---

### Q41 — Which rolling/session operations need state across chunk boundaries?

**Difficulty:** Hard  
**Topics:** Topic 13 — Chunking; Topic 09 — Time series

#### Interview Question

Classify these operations as naturally independent per chunk or requiring cross-chunk state:

```text
row-level amount conversion
filter amount > 0
sum/count partial aggregation
deduplication by business key
sessionization
24-hour rolling sum
global sort
```

#### Model Answer

Naturally local:

- row-level conversion;
- row filtering;
- sum/count partial aggregation.

Stateful across chunks:

- deduplication by global business key;
- sessionization;
- time-based rolling windows;
- global sorting.

The rolling operation may need boundary rows from the previous chunk. Sessionization needs the final state of the previous session.

#### Why This Works

Chunking is safe only when the algorithm's required state is either local to a chunk or explicitly carried across chunks.

#### Common Candidate Mistake

Assuming `chunksize` makes every pandas operation independently correct.

---

### Q42 — How would you instrument a pandas pipeline with invariants and reusable quality checks?

**Difficulty:** Hard  
**Topics:** Topic 11 — chaining/pipe; Topic 05 — validation

#### Interview Question

A five-step ETL chain produces an unexpectedly small output. Design a debugging strategy that lets you identify the first stage where the invariant fails.

#### Model Answer

Use named transformations and checks:

```python
def log_shape(frame, name):
    print(
        name,
        "shape=",
        frame.shape,
        "nulls=",
        frame.isna().sum().sum(),
    )
    return frame

def require_unique_order_id(frame):
    assert frame["order_id"].is_unique
    return frame

result = (
    source
    .pipe(lambda x: log_shape(x, "source"))
    .pipe(clean_orders)
    .pipe(lambda x: log_shape(x, "after_clean"))
    .pipe(require_unique_order_id)
    .pipe(enrich_customers)
    .pipe(lambda x: log_shape(x, "after_enrichment"))
)
```

For reusable domain checks, a custom DataFrame accessor can expose APIs such as:

```python
df.dq.null_report()
df.dq.duplicate_report()
```

#### Step-by-Step Reasoning

The first failing boundary narrows the search space. Logging every cell is noisy; logging semantic invariants is more useful.

#### Production Perspective

Good observability is about explaining why a transformation changed grain, rows, nullability, or key uniqueness.

### Q43 — How do Copy-on-Write and NumPy views affect mutation expectations?

**Difficulty:** Hard  
**Topics:** Topic 12 — CoW

#### Interview Question

Suppose:

```python
df = pd.DataFrame({"amount": [100, 200, 300]})
subset = df[["amount"]]

subset.loc[subset["amount"] > 150, "amount"] = 0
```

Should the parent change? Then explain why `to_numpy()` or `.values` requires separate reasoning, including a read-only array.

#### Model Answer

The pandas objects are logically independent under Copy-on-Write, so writing to `subset` should not logically mutate `df`.

The implementation may share physical storage before a write and materialize a copy when needed. That physical optimization does not change pandas' logical independence.

At the NumPy boundary:

```python
arr = subset.to_numpy()
```

or:

```python
arr = subset.values
```

you should not assume the resulting array is an independently mutable buffer. Depending on the pandas representation and sharing state, the array can be read-only. If mutation is required, make the copy explicitly:

```python
arr = subset.to_numpy().copy()
arr[0, 0] = 999
```

#### Production Perspective

Use explicit copies at boundaries where mutation is required. For pure DataFrame transformations, prefer returning new results and test that the input is not mutated.

### Q44 — How do projection and predicate pushdown reduce memory?

**Difficulty:** Hard  
**Topics:** Topic 13 — Memory; Topic 02 — Parquet I/O

#### Interview Question

You only need `customer_id`, `country`, and `amount` from a large Parquet dataset, and only rows for `country == "IN"`. What should you attempt at read time?

#### Model Answer

Project only required columns and, where supported by the Parquet storage layout, push the filter down:

```python
df = pd.read_parquet(
    "transactions.parquet",
    columns=["customer_id", "country", "amount"],
    filters=[("country", "==", "IN")],
)
```

#### Step-by-Step Reasoning

Reading less data is often better than loading a wide table and dropping columns afterward.

Two useful ideas are:

- **column projection**: read only needed columns;
- **predicate pushdown**: avoid reading rows that can be excluded by storage-level filters.

#### Production Perspective

Memory optimization begins before the DataFrame exists. Reducing input volume is often more effective than cleaning up after a large read.

---

### Q45 — How would you benchmark a vectorized, grouped, and Python-level implementation?

**Difficulty:** Hard  
**Topics:** Topics 06, 10, 13 — performance

#### Interview Question

A transformation works three ways:

```text
Series.str operations
groupby/vectorized arithmetic
groupby.apply(lambda ...)
```

How would you compare them without fabricating performance conclusions?

#### Model Answer

Benchmark on representative data and the same hardware:

```python
import time

start = time.perf_counter()
vectorized_result = (
    df["country"]
    .astype("string")
    .str.strip()
    .str.upper()
)
vectorized_seconds = time.perf_counter() - start

start = time.perf_counter()
apply_result = df["country"].apply(
    lambda value: value.strip().upper()
)
apply_seconds = time.perf_counter() - start

print(
    {
        "vectorized_seconds": vectorized_seconds,
        "apply_seconds": apply_seconds,
    }
)
```

Also validate equality:

```python
pd.testing.assert_series_equal(
    vectorized_result.reset_index(drop=True),
    apply_result.astype("string").reset_index(drop=True),
    check_names=False,
)
```

#### Production Perspective

A performance claim requires measurement. Also measure memory and, for large workloads, peak process memory. A faster implementation that changes null or dtype semantics is not an acceptable optimization.

### Q46 — A 20 GB CSV must run on an 8 GB machine. What is your complete memory strategy?

**Difficulty:** Advanced  
**Topics:** Topics 02, 04, 06, 07, 13

#### Interview Question

The file contains 20 GB of raw CSV data and the machine has 8 GB RAM. You need a grouped result and must not load the whole dataset at once.

Explain your strategy, including memory measurement, projection, dtype control, chunking, iterator behavior, SQL-style chunk reads, aggregation, and cleanup.

#### Model Answer

Start with the smallest required input contract:

```python
required = [
    "country",
    "product",
    "amount_cents",
]
```

Read only those columns and use explicit dtypes:

```python
for chunk in pd.read_csv(
    "orders.csv",
    usecols=required,
    dtype={
        "country": "string",
        "product": "string",
        "amount_cents": "Int64",
    },
    chunksize=200_000,
):
    ...
```

`chunksize` creates an iterator-like chunked workflow. The module also teaches `iterator=True` when an explicit text-file iterator is useful. Database ingestion can use the analogous:

```python
for chunk in pd.read_sql(
    query,
    connection,
    chunksize=100_000,
):
    ...
```

Measure DataFrame memory:

```python
chunk.memory_usage(deep=True).sum()
```

and:

```python
chunk.info(memory_usage="deep")
```

Then compute partial sufficient statistics instead of retaining raw chunks:

```python
partial = (
    chunk.groupby(["country", "product"], as_index=False)
         .agg(
             revenue_sum=("amount_cents", "sum"),
             revenue_count=("amount_cents", "count"),
         )
)
```

The combine stage must itself be memory-aware. Do not solve an out-of-memory problem with:

```python
pd.concat(all_chunks)
```

After a chunk is no longer needed:

```python
del chunk
```

#### Critical Memory Reasoning

```text
DataFrame memory
vs
peak process memory / RSS
```

are different. Groupby structures, parsing buffers, temporary arrays, and copies can make peak memory much larger than the final result.

#### Production Perspective

The first optimization is to read less. The next is semantic dtype reduction. Then use bounded chunk processing and compact state. If chunked results must become Parquet, write them incrementally with a suitable writer strategy rather than holding all rows in memory.

### Q47 — Design a pandas Silver-layer transformation for messy orders.

**Difficulty:** Advanced  
**Topics:** Topics 02, 04, 05, 07, 11, 12

#### Interview Question

Input grain: one row per raw order record.

Required Silver grain: one row per valid `order_id`.

The source contains:

- duplicate order IDs;
- malformed amounts;
- inconsistent country casing/whitespace;
- missing customer IDs;
- customer dimension duplicates;
- timestamps in a known local timezone.

Explain the transformation and validation plan.

#### Model Answer

A defensible design is:

```text
raw read
  ↓
explicit schema
  ↓
parse timestamp / count failures
  ↓
normalize join keys
  ↓
identify duplicate business records
  ↓
choose deterministic surviving record
  ↓
separate invalid/quarantine rows
  ↓
validate customer dimension uniqueness
  ↓
many-to-one enrichment
  ↓
assert grain and revenue invariants
  ↓
publish Silver output
```

Key assertions:

```python
assert silver["order_id"].is_unique
assert len(raw) == len(clean) + len(quarantine)
```

Before customer enrichment:

```python
assert customers["customer_id"].is_unique
```

During enrichment:

```python
silver = clean.merge(
    customers,
    on="customer_id",
    how="left",
    validate="many_to_one",
)
```

If every valid order must survive the enrichment:

```python
assert len(silver) == len(clean)
```

#### What a Weak Answer Might Miss

A weak answer may focus on string cleaning while ignoring grain and join cardinality.

#### What a Strong Answer Should Include

A strong answer starts with the contract:

- what one Silver row means;
- which key is unique;
- how invalid data is quarantined;
- what must be preserved across enrichment.

#### Production Perspective

The important architectural principle is that transformations preserve explicit, testable business grain.

---

### Q48 — Design a schema for banking transactions where correctness matters more than convenience.

**Difficulty:** Advanced  
**Topics:** Topic 04 — dtypes; Topics 02 and 09

#### Interview Question

Design a semantic schema for:

```text
transaction_id
account_id
branch_code
amount_cents
transaction_time
is_reversed
status
```

The source contains missing values and some malformed timestamps. Discuss nullable types, categoricals, timezone-aware timestamps, exact money representation, Arrow-backed dtypes, datetime bounds/resolution, and schema validation.

#### Model Answer

A reasonable contract is:

```text
transaction_id   string
account_id       string
branch_code      string
amount_cents     Int64
transaction_time timezone-aware datetime
is_reversed      nullable boolean
status           string/category depending on controlled vocabulary
```

Use explicit conversion:

```python
df["transaction_id"] = df["transaction_id"].astype("string")
df["account_id"] = df["account_id"].astype("string")
df["branch_code"] = df["branch_code"].astype("string")

df["amount_cents"] = pd.to_numeric(
    df["amount_cents"],
    errors="coerce",
).astype("Int64")

df["transaction_time"] = pd.to_datetime(
    df["transaction_time"],
    utc=True,
    errors="coerce",
)
```

For a controlled status vocabulary, category can reduce memory and encode the expected set. If unused categories accumulate after filtering, remove them. If ordering is meaningful, define an ordered category rather than relying on lexical order.

A NumPy-nullable or PyArrow-backed `dtype_backend` can be selected when the project contract calls for those storage semantics.

#### Critical Type Reasoning

Use integer cents when the business amount is expressed in whole cents. For higher decimal precision, the module also considers `Decimal` and Arrow decimal representations. Do not replace exact money semantics with floating-point simply because arithmetic is convenient.

Datetime resolution and representable bounds matter for high-resolution or historical timestamps. A timestamp conversion can fail or become missing when the source timestamp is out-of-bounds for the chosen datetime representation or outside the supported datetime range, so conversion failures must be measured and handled explicitly.

#### Production Perspective

A schema dictionary should define fields, dtypes, nullability, allowed categorical values, timestamp semantics, and monetary precision. Memory optimization is subordinate to correctness.

### Q49 — When would you use `map`, `merge`, or `combine_first` for enrichment?

**Difficulty:** Advanced  
**Topics:** Topic 07 — enrichment; Topic 01 — alignment

#### Interview Question

You have one DataFrame of orders and one small Series mapping `customer_id → segment`. You also have a secondary customer source that should fill missing segment values. Compare `map`, `merge`, and `combine_first`.

#### Model Answer

Use `map` for a simple one-column lookup:

```python
orders["segment"] = orders["customer_id"].map(
    customer_to_segment
)
```

Use `merge` when you need multiple columns or an explicit join contract:

```python
orders = orders.merge(
    customer_dim,
    on="customer_id",
    how="left",
    validate="many_to_one",
)
```

Use `combine_first` when two aligned Series represent fallback sources:

```python
orders["segment"] = (
    orders["primary_segment"]
    .combine_first(orders["secondary_segment"])
)
```

#### Step-by-Step Reasoning

These APIs encode different shapes of relationships:

- `map`: scalar lookup per left value;
- `merge`: table-to-table relational enrichment;
- `combine_first`: aligned fallback.

#### Production Perspective

Choose the simplest operation that expresses the true contract. A lookup should not be hidden inside a full table join if a `Series.map()` is sufficient.

---

### Q50 — How would you build a fiscal time-series report with multiple measures and smoothing metrics?

**Difficulty:** Advanced  
**Topics:** Topics 06, 08, 09, 10

#### Interview Question

A finance team reports using fiscal quarters ending in March. Transactions are UTC-aware. They need one row per business unit and fiscal quarter with revenue, transaction count, average transaction value, and a running/weighted signal for analysis.

Explain the timestamp, period, grouping, and output-schema decisions.

#### Model Answer

Convert to the reporting timezone before deriving local reporting periods:

```python
df["transaction_time"] = pd.to_datetime(
    df["transaction_time"],
    utc=True,
)

df["local_time"] = (
    df["transaction_time"]
    .dt.tz_convert("Asia/Kolkata")
)

df["fiscal_quarter"] = (
    df["local_time"]
    .dt.to_period("Q-MAR")
)
```

Then aggregate:

```python
result = (
    df.groupby(
        ["business_unit", "fiscal_quarter"],
        as_index=False,
        sort=False,
    )
    .agg(
        revenue_cents=("amount_cents", "sum"),
        transaction_count=("transaction_id", "nunique"),
        average_amount_cents=("amount_cents", "mean"),
    )
)
```

For a chronological time series, `expanding()` can represent a cumulative window, while `ewm()` represents an exponentially weighted window. They answer different analytical questions and should be used only when the metric definition calls for them.

#### Step-by-Step Reasoning

`Period` represents a reporting interval rather than an instant. The timezone conversion must happen before local period derivation because the business calendar depends on local time.

#### Production Perspective

Use explicit resampling boundary semantics such as `label` and `closed` when bins matter, and validate period coverage against the expected fiscal calendar.

### Q51 — How would you make partitioned pandas processing idempotent?

**Difficulty:** Advanced  
**Topics:** Topic 13 — partitioning/idempotency; Topic 02 — output safety

#### Interview Question

A daily partition job can be retried. The input partition is:

```text
2026-01-15
```

How would you prevent a retry from duplicating the output?

#### Model Answer

Use deterministic partition-level processing and replacement semantics:

```text
read one input partition
  ↓
process deterministically
  ↓
write to temporary output
  ↓
validate output
  ↓
publish/replace the target partition
```

The job should not blindly append to an already-published partition.

Useful invariants include:

```text
output partition corresponds exactly to input partition
retry produces the same logical result
no duplicate publish occurs
```

#### What a Strong Answer Should Include

A strong candidate discusses:

- deterministic input selection;
- stable sorting/tie rules;
- temporary output;
- validation before publish;
- replacement rather than duplicate append;
- partition-level retry boundaries.

#### Production Perspective

Idempotency is a behavioral property: running the same partition job again should not create a different logical dataset.

---

### Q52 — Why can `del` reduce object lifetime but fail to lower OS-visible memory immediately?

**Difficulty:** Advanced  
**Topics:** Topic 12 — CoW; Topic 13 — memory

#### Interview Question

A job does:

```python
del large_intermediate
```

but operating-system memory remains high. Explain why this can happen and how Copy-on-Write interacts with peak memory.

#### Model Answer

`del` removes a Python reference. If no other references remain, the object can become eligible for deallocation. That does not guarantee that the Python memory allocator immediately returns the underlying memory to the OS.

Also, process RSS can remain high because:

- allocator arenas are retained for reuse;
- other live objects still hold memory;
- temporary join/groupby structures remain;
- copies or arrays were materialized earlier;
- Copy-on-Write may defer a physical copy until a write occurs.

Therefore:

```text
object lifetime
≠
DataFrame logical size
≠
process RSS
```

#### Production Perspective

Profile peak memory during the operation that causes the spike. Reducing final DataFrame memory is valuable, but it does not prove the pipeline is memory-safe.

### Q53 — How would you combine partial aggregates while controlling group-state memory?

**Difficulty:** Advanced  
**Topics:** Topics 06 and 13

#### Interview Question

A chunked pipeline groups 500 million transactions by `(country, product)` and needs sum, count, and average. The number of groups is large. What information must survive between chunks, and what would you monitor?

#### Model Answer

Keep additive sufficient statistics:

```python
partial = (
    chunk.groupby(
        ["country", "product"],
        as_index=False,
    )
    .agg(
        amount_sum=("amount", "sum"),
        amount_count=("amount", "count"),
    )
)
```

Combine by summing the partial sums and counts, then derive:

```python
combined["amount_mean"] = (
    combined["amount_sum"]
    / combined["amount_count"]
)
```

The state that survives chunks is therefore group-level aggregate state, not all source rows.

#### Critical Risk

If group cardinality itself is enormous, the aggregate state may become the dominant memory consumer. At that point, simply reducing chunk size does not solve the fundamental state-size problem.

#### Production Perspective

Track:

```text
rows processed
groups in state
peak memory
number of output groups
```

and compare the chunked result with a full-load result on a smaller representative dataset using `pd.testing.assert_frame_equal()`.

### Q54 — How would you decide when pandas is no longer the right execution engine?

**Difficulty:** Advanced  
**Topics:** Topic 13 — Engine selection

#### Interview Question

A workload has grown beyond what you can process comfortably with pandas. You are considering pandas, Polars, DuckDB, Dask, or Spark. What questions should you answer before choosing?

#### Model Answer

Ask:

```text
How large is the data?
How much RAM is available?
What is the required working set?
Is the workload local or distributed?
How much CPU parallelism is needed?
What is the join/groupby state size?
Can projection and chunking make the workload fit?
How much operational complexity is acceptable?
What engine does the existing team/platform support?
```

Conceptually:

- pandas fits local DataFrame workflows when the working set and execution model are manageable;
- Polars is a local columnar DataFrame alternative;
- DuckDB is useful for analytical processing with a SQL-oriented model over local data;
- Dask can provide partitioned, pandas-like larger-than-memory execution;
- Spark is a distributed execution option when cluster-scale processing is actually justified.

#### What the Interviewer Is Testing

Whether you can distinguish “pandas is slow” from “the workload requires a different execution model.”

#### Production Perspective

First optimize the pandas design: read less, choose semantic dtypes, use vectorization, reduce intermediate objects, and chunk where appropriate. Then decide whether the required state or scale exceeds the tool's practical boundary.

### Q55 — How would you prevent schema drift from silently corrupting a partitioned batch?

**Difficulty:** Advanced  
**Topics:** Topics 02, 04, 07, 13

#### Interview Question

Daily files contain inconsistent columns, different identifier representations, and occasional timestamp format changes. The batch must fail visibly rather than silently changing semantics.

Design the validation boundary and explain why a changed file schema should not automatically be “fixed” by pandas inference.

#### Model Answer

For each partition:

```python
required_columns = {
    "order_id",
    "customer_id",
    "amount_cents",
    "created_at",
}

assert required_columns.issubset(df.columns)

df["order_id"] = df["order_id"].astype("string")
df["customer_id"] = df["customer_id"].astype("string")

df["amount_cents"] = pd.to_numeric(
    df["amount_cents"],
    errors="coerce",
).astype("Int64")

parsed = pd.to_datetime(
    df["created_at"],
    format="%Y-%m-%d %H:%M:%S",
    errors="coerce",
    utc=True,
)
```

Count conversion failures before publishing.

For known heterogeneous source formats, handle them with an explicit source-specific contract rather than silently guessing.

#### Production Perspective

A partition is a contract boundary. A missing required column, changed identifier semantics, or unexpected timestamp format should trigger a visible quality outcome rather than quietly changing the dataset's meaning.

### Q56 — How would you build an anti-join quality check for missing dimension records?

**Difficulty:** Advanced  
**Topics:** Topic 07 — joins; Topic 05 — data quality

#### Interview Question

You have one row per order and a customer dimension. You need a quality report containing all orders whose `customer_id` does not exist in the dimension, while the production output should contain only valid enrichments.

How would you build both the report and the valid output?

#### Model Answer

Use a left merge with an indicator:

```python
check = orders.merge(
    customers[["customer_id"]].drop_duplicates(),
    on="customer_id",
    how="left",
    indicator=True,
)

missing_customers = check.loc[
    check["_merge"].eq("left_only")
].copy()

valid_orders = orders.merge(
    customers,
    on="customer_id",
    how="inner",
    validate="many_to_one",
)

assert len(valid_orders) + len(missing_customers) == len(orders)
```

#### Why This Works

The anti-join identifies the excluded records explicitly. The reconciliation equation proves that every input order is either validly enriched or classified as missing a customer dimension match.

#### Production Perspective

Data-quality reporting is part of the pipeline, not an afterthought.

---

### Q57 — How would you prove a `merge_asof` FX enrichment is point-in-time correct?

**Difficulty:** Advanced  
**Topics:** Topics 07, 09, 10

#### Interview Question

Orders must use the latest FX rate at or before the transaction instant, for the same currency. Explain:

- timestamp normalization;
- sorting;
- `by`;
- `direction`;
- `tolerance`;
- validation of unmatched records.

#### Model Answer

Normalize timestamps first:

```python
orders["created_at"] = pd.to_datetime(
    orders["created_at"],
    utc=True,
)

rates["rate_time"] = pd.to_datetime(
    rates["rate_time"],
    utc=True,
)

orders = orders.sort_values(
    ["currency", "created_at"]
)

rates = rates.sort_values(
    ["currency", "rate_time"]
)

enriched = pd.merge_asof(
    orders,
    rates,
    left_on="created_at",
    right_on="rate_time",
    by="currency",
    direction="backward",
    tolerance=pd.Timedelta("1D"),
)
```

`backward` selects the latest right-side timestamp at or before the left-side timestamp. `by` restricts matching to the same currency. `tolerance` prevents an arbitrarily old rate from being selected.

Validate the number of unmatched rates and inspect them as a data-quality signal.

#### Production Perspective

Point-in-time enrichment is correct only when timestamp semantics, sorting, grouping key, and tolerance are all part of the contract.

### Q58 — Which operations are independent per chunk, and which require state?

**Difficulty:** Advanced  
**Topics:** Topic 13 — chunk boundaries; Topic 09 — time series

#### Interview Question

Classify these operations:

```text
type conversion
row-level arithmetic
simple filtering
sum/count partial aggregation
deduplication by global key
sessionization
24-hour rolling sum
global sort
```

Then explain what state is required and what happens if that state itself becomes too large.

#### Model Answer

Naturally local:

```text
type conversion
row-level arithmetic
simple filtering
sum/count partial aggregation
```

Stateful:

```text
global-key deduplication
sessionization
24-hour rolling sum
global sorting
```

For deduplication, state tracks keys already accepted. For sessions, state includes the current session boundary/state per entity. For rolling windows, state includes the historical observations needed to compute the next window.

A chunked writer can emit output incrementally. For Parquet, a `ParquetWriter` can write batches/row groups incrementally when the schema is stable, avoiding a design that retains every output chunk in memory.

#### Critical Scaling Point

If deduplication or grouping state itself becomes too large, reducing `chunksize` does not remove the global-state requirement. The architecture must reconsider the state representation or execution engine.

#### Production Perspective

Chunking is not a magic memory switch. Ask both:

```text
What information must cross the chunk boundary?
How large can that state become?
```

### Q59 — Daily revenue increased 80% even though source row count did not change. How would you investigate?

**Difficulty:** Advanced  
**Topics:** Topics 04, 05, 06, 07, 09, 13

#### Interview Question

A daily revenue report suddenly rises by 80%. Input row count is unchanged. Give a structured pandas/Data Engineering investigation plan.

#### Expected Candidate Approach

Think in terms of metric lineage:

```text
source
→ typing
→ cleaning
→ deduplication
→ aggregation
→ enrichment
→ time bucketing
→ output
```

#### Model Answer

I would investigate:

1. **Schema/dtypes**
   - Did the amount become string/object?
   - Did a conversion change missing values into a different representation?

2. **Duplicate business keys**
   - Did the same transaction begin surviving multiple times?
   - Did deduplication criteria change?

3. **Join cardinality**
   - Did a dimension gain duplicate keys?
   - Did a one-to-many join multiply transactions?

4. **Time semantics**
   - Did timezone localization/conversion change the reporting day?
   - Did DST or a boundary condition move events?

5. **Aggregation**
   - Did grouping grain change?
   - Are null measures being counted or summed differently?

6. **Chunking**
   - Did a partition retry append duplicate output?
   - Did cross-chunk deduplication state reset?

7. **Reconciliation**
   - Compare pre- and post-enrichment revenue.
   - Compare input rows with clean + quarantine.
   - Compare partition totals with published totals.

A key invariant is:

```python
assert revenue_after_enrichment == revenue_before_enrichment
```

when the enrichment is contractually many-to-one and should not alter order grain.

#### What a Strong Answer Should Include

A strong answer does not start with “recalculate revenue.” It traces where row multiplication, time movement, duplication, or type interpretation could have changed the measure.

#### Production Perspective

Metric incidents should be investigated as pipeline lineage and invariant failures, not only as final-number anomalies.

---

### Q60 — Senior interview: design and defend the complete partitioned pandas pipeline.

**Difficulty:** Advanced  
**Topics:** Topics 01–13 integrated

#### Interview Question

Design a production-oriented pandas pipeline for a three-month e-commerce backfill.

Input:

- daily CSV partitions;
- one row per raw order event;
- possible duplicate raw order events;
- customer dimension expected to be one row per customer;
- UTC-aware order timestamps;
- daily customer revenue output;
- memory-constrained machine;
- retries at partition level.

Your design must be deterministic and auditable. Explain the grain, schema, state, transformations, validations, memory strategy, and publication semantics.

#### What the Interviewer Is Testing

Whether you can turn pandas APIs into a coherent data-engineering system with explicit contracts.

#### Expected Candidate Approach

Start with:

```text
grain
→ schema
→ quality rules
→ join cardinality
→ time semantics
→ computation state
→ memory constraints
→ validation
→ idempotent publication
```

#### Model Answer

### 1. Define the grain

Raw input:

```text
one row = one raw order event
```

Trusted order-level data:

```text
one row = one valid order_id
```

Final metric:

```text
one row = one customer × reporting day
```

### 2. Ingest with an explicit contract

```python
for chunk in pd.read_csv(
    path,
    usecols=[
        "order_id",
        "customer_id",
        "created_at",
        "amount_cents",
    ],
    dtype={
        "order_id": "string",
        "customer_id": "string",
        "amount_cents": "Int64",
    },
    parse_dates=["created_at"],
    chunksize=200_000,
):
    ...
```

Do not accumulate all raw chunks with `pd.concat(all_chunks)`.

For very large Parquet outputs, use an incremental writer such as `ParquetWriter` when the output schema is stable and row-group/batch publication matches the pipeline design.

### 3. Normalize and validate

Normalize key fields:

```python
chunk["customer_id"] = (
    chunk["customer_id"]
    .astype("string")
    .str.normalize("NFKC")
    .str.strip()
)
```

Convert numeric fields explicitly and count failures. Apply domain rules and create `dq_reason`, `is_duplicate`, or `is_outlier` flags as appropriate.

### 4. Handle cross-chunk duplicates

A duplicate order can span two chunks, so local `drop_duplicates()` is insufficient. Carry deterministic state across chunks or use a processing design that provides global key state.

### 5. Validate customer cardinality

Before the join:

```python
assert customer_dim["customer_id"].is_unique
```

Then:

```python
enriched = clean.merge(
    customer_dim,
    on="customer_id",
    how="left",
    validate="many_to_one",
)
```

The join should preserve order grain.

### 6. Establish time semantics

Because source timestamps are UTC-aware, first decide whether the daily metric is defined in UTC or a business timezone.

For a local reporting day:

```python
enriched["reporting_time"] = (
    enriched["created_at"]
    .dt.tz_convert("Asia/Kolkata")
)

enriched["reporting_date"] = (
    enriched["reporting_time"]
    .dt.normalize()
)
```

### 7. Aggregate to final grain

```python
daily = (
    enriched.groupby(
        ["reporting_date", "customer_id"],
        as_index=False,
        sort=False,
    )
    .agg(
        revenue_cents=("amount_cents", "sum"),
        order_count=("order_id", "nunique"),
    )
)
```

### 8. Validate invariants

Examples:

```python
assert enriched["order_id"].is_unique

revenue_before = clean["amount_cents"].sum()
revenue_after = enriched["amount_cents"].sum()

assert revenue_before == revenue_after
```

For quality:

```python
assert rows_in == rows_clean + rows_quarantined
```

For a chunked implementation, compare results against a full-load implementation on a manageable test fixture:

```python
pd.testing.assert_frame_equal(
    expected.sort_values(expected.columns.tolist()).reset_index(drop=True),
    actual.sort_values(actual.columns.tolist()).reset_index(drop=True),
)
```

### 9. Control peak memory

Measure DataFrame memory with:

```python
df.memory_usage(deep=True).sum()
```

and inspect peak process behavior separately. Downcast where semantically safe, use categories for suitable low-cardinality fields, project columns early, and release temporary objects when their lifetime ends.

Remember that allocator behavior can keep process RSS high after an object is released.

### 10. Make retries idempotent

Treat each input partition as a deterministic unit:

```text
read partition
→ transform
→ validate
→ write temporary output
→ publish/replace target partition
```

A retry must replace the logical partition rather than append a duplicate copy.

### 11. Engine boundary

Pandas is appropriate when projection, dtype control, chunking, and partition-level processing keep the working set manageable. If required state or execution scale exceeds those constraints, evaluate another engine based on workload shape, RAM, parallelism, and operational requirements.

#### What a Weak Answer Might Miss

A weak answer lists pandas functions without defining grain, key uniqueness, late data, memory state, or retry behavior.

#### What a Strong Answer Should Include

A strong answer explicitly separates:

```text
data contract
→ transformation
→ state
→ invariants
→ resource limits
→ publication
```

and identifies what can fail at each boundary.

#### Production Perspective

Senior-level pandas engineering is less about knowing every method and more about preserving semantics while data moves through a constrained execution environment.

## Topic Coverage Matrix

| Topic | Representative Questions |
|---|---|
| Topic 01 — Series/DataFrame/Index | Q01, Q02, Q05, Q17, Q60 |
| Topic 02 — Reading/Writing Data Sources | Q06, Q18, Q25, Q44, Q46, Q55, Q60 |
| Topic 03 — Selection | Q03, Q04, Q16, Q15, Q38 |
| Topic 04 — dtypes/Nullable/Categoricals | Q06, Q07, Q18, Q33, Q48, Q52, Q55, Q60 |
| Topic 05 — Cleaning/Data Quality | Q08, Q19, Q32, Q38, Q56, Q60 |
| Topic 06 — groupby | Q09, Q20, Q21, Q22, Q34, Q39, Q53, Q60 |
| Topic 07 — merge/join/cardinality | Q10, Q23, Q24, Q31, Q44, Q49, Q56, Q57, Q60 |
| Topic 08 — reshaping | Q11, Q14, Q26, Q35, Q50 |
| Topic 09 — time series | Q12, Q24, Q27, Q28, Q36, Q37, Q50, Q57, Q58, Q59, Q60 |
| Topic 10 — strings/datetime | Q12, Q13, Q28, Q29, Q45, Q50, Q57, Q60 |
| Topic 11 — chaining/pipe | Q05, Q30, Q42, Q60 |
| Topic 12 — Copy-on-Write | Q15, Q30, Q38, Q43, Q52, Q60 |
| Topic 13 — chunking/memory | Q39, Q40, Q41, Q44, Q46, Q51, Q52, Q53, Q54, Q58, Q60 |

## Interview Skill Matrix

| Interview Skill | Representative Questions |
|---|---|
| Conceptual understanding | Q01, Q06, Q09, Q20, Q27, Q28, Q54 |
| Code reading | Q03, Q15, Q21, Q38, Q43 |
| Output prediction | Q01, Q03, Q09, Q10, Q14, Q27 |
| Debugging | Q31, Q33, Q37, Q38, Q43, Q57, Q59 |
| Coding | Q04, Q12, Q19, Q23, Q29, Q34, Q39, Q46 |
| Data quality | Q08, Q19, Q32, Q33, Q38, Q55, Q56 |
| Join reasoning | Q10, Q23, Q24, Q31, Q49, Q56, Q57 |
| Performance | Q21, Q44, Q45, Q46, Q52, Q54 |
| Memory optimization | Q39, Q40, Q44, Q46, Q52, Q53, Q58 |
| Testing/validation | Q10, Q23, Q31, Q32, Q39, Q42, Q56, Q60 |
| Production design | Q32, Q37, Q46, Q47, Q51, Q52, Q60 |
| Architecture reasoning | Q46, Q47, Q51, Q54, Q55, Q58, Q60 |

## Final Completion Checklist

- [x] Exactly 60 interview questions.
- [x] Exactly 15 Basic questions.
- [x] Exactly 15 Moderate questions.
- [x] Exactly 15 Hard questions.
- [x] Exactly 15 Advanced questions.
- [x] Continuous numbering from Q01 through Q60.
- [x] Every question is immediately followed by its model solution.
- [x] Topics 01–13 are substantially exercised.
- [x] Join cardinality, `validate`, indicators, anti/semi joins, and `merge_asof` are represented.
- [x] `agg`, `transform`, `filter`, `apply`, ranking, sequencing, cumulative, lag, and difference operations are represented.
- [x] Reshaping, pivot failure modes, long/wide semantics, and missing-vs-zero reasoning are represented.
- [x] Timezone, rolling-window, missing-period, and late-arriving-event reasoning are represented.
- [x] String normalization, regex named groups, and datetime accessor reasoning are represented.
- [x] Method chaining, `pipe`, debugging boundaries, and Copy-on-Write are represented.
- [x] Chunked aggregation, cross-chunk deduplication, rolling/session state, peak memory, and idempotency are represented.
- [x] No fabricated benchmark measurements are used.
- [x] Production invariants and reconciliation patterns are included.
