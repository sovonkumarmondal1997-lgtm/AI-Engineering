# DataFrames with pandas — 60 Practice Questions and Solutions

## How to Use This Practice Set

This workbook consolidates **Stage 2 → Module 2.3 — DataFrames with pandas**, Topics 01–13. The objective is to practice pandas as a Data Engineering tool: reason about grain, labels, dtypes, missingness, row counts, cardinality, time semantics, memory, state, correctness, and production behavior.

Every exercise uses the engineering loop:

```text
Predict → Run → Inspect → Assert → Explain
```

Unless a question says otherwise, use modern pandas practices and prefer explicit, readable transformations.

## Practice Method

1. Read the **Problem** and stop before the **Solution**.
2. Predict row count, grain, index behavior, important values, and dtypes where requested.
3. Solve independently.
4. Compare your solution with the provided solution.
5. Run the assertions.
6. Explain why the result is correct and what could fail in production.

## Difficulty Guide

| Part | Questions | Focus |
|---|---:|---|
| Basic | Q01–Q15 | Foundations and direct reasoning |
| Moderate | Q16–Q30 | Combined concepts, edge cases, debugging, validation |
| Hard | Q31–Q45 | Realistic Data Engineering transformations and performance |
| Advanced | Q46–Q60 | Production design, correctness contracts, memory, state, idempotency |

# Part 1 — Basic

## Q01–Q15

### Q01 — Predict index alignment in two revenue Series

**Difficulty:** Basic  
**Topics:** Topic 01 — Series, Index, label alignment

#### Problem

```python
import pandas as pd

revenue_2024 = pd.Series(
    [100, 200, 300], index=["IN", "US", "UK"], name="revenue_2024"
)
revenue_2025 = pd.Series(
    [120, 260, 80], index=["US", "UK", "DE"], name="revenue_2025"
)
```

**Grain:** one value per country-year Series.

Calculate `revenue_2025 - revenue_2024` and `revenue_2025.add(revenue_2024, fill_value=0)`.

**Expected output row count:** 4 for both results.

#### Predict Before Running

Predict the output index and the values for `IN`, `US`, `UK`, and `DE`.

#### Solution

```python
change = revenue_2025 - revenue_2024
combined = revenue_2025.add(revenue_2024, fill_value=0)

assert change.index.tolist() == ["DE", "IN", "UK", "US"]
assert pd.isna(change.loc["DE"])
assert pd.isna(change.loc["IN"])
assert change.loc["US"] == 60
assert change.loc["UK"] == -220

assert combined.loc["DE"] == 80
assert combined.loc["IN"] == 100
assert combined.loc["US"] == 460
assert combined.loc["UK"] == 380
```

#### Step-by-Step Explanation

pandas aligns Series by labels before arithmetic. `US` and `UK` have matching labels, so subtraction is defined. `IN` exists only in the first Series and `DE` only in the second, so subtraction produces `NaN` there. `add(..., fill_value=0)` changes the arithmetic rule for an unmatched label.

#### Expected Result

`change`: `DE=NaN`, `IN=NaN`, `UK=-220`, `US=60`.  
`combined`: `DE=80`, `IN=100`, `UK=380`, `US=460`.

#### Why This Works

The Index is semantic data, not decoration. Alignment-generated `NaN` is different from source-data missingness.

#### Validation

The assertions check the index and representative values.

#### Common Mistake

Treating two Series as positional arrays.

#### Production Note

Use `fill_value=0` only when absence of a country from one Series truly means zero for the business measure.

---

### Q02 — Build and inspect an order DataFrame

**Difficulty:** Basic  
**Topics:** Topic 01 — DataFrame creation, RangeIndex, `head`, `tail`, `sample`, `shape`, `columns`, `dtypes`, `info`, `describe`, `value_counts`, `set_index`, `reset_index`, `rename`, `drop`, `assign`

#### Problem

Create a DataFrame from these records:

```python
records = [
    {"order_id": "O1", "country": "IN", "quantity": 2, "unit_price": 100.0, "status": "paid"},
    {"order_id": "O2", "country": "US", "quantity": 1, "unit_price": 250.0, "status": "pending"},
    {"order_id": "O3", "country": "IN", "quantity": 3, "unit_price": 50.0, "status": "paid"},
]
```

**Input grain:** one row = one order.  
**Expected output row count:** 3.

Inspect the frame with `head`, `tail`, `sample`, `shape`, `columns`, `dtypes`, `info`, `describe`, and `value_counts`. Then add `revenue`, rename `status` to `order_status`, temporarily move `order_id` into the Index, restore it, and drop `unit_price`.

#### Predict Before Running

Predict the three revenue values, the final column names, and whether the final DataFrame still has three rows.

#### Solution

```python
import pandas as pd

records = [
    {"order_id": "O1", "country": "IN", "quantity": 2, "unit_price": 100.0, "status": "paid"},
    {"order_id": "O2", "country": "US", "quantity": 1, "unit_price": 250.0, "status": "pending"},
    {"order_id": "O3", "country": "IN", "quantity": 3, "unit_price": 50.0, "status": "paid"},
]

df = pd.DataFrame.from_records(records)

df.head(2)
df.tail(2)
df.sample(2, random_state=42)
shape = df.shape
columns = df.columns
dtypes = df.dtypes
df.info()
description = df.describe()
status_counts = df["status"].value_counts()

result = (
    df.assign(revenue=lambda d: d["quantity"] * d["unit_price"])
    .rename(columns={"status": "order_status"})
    .set_index("order_id")
    .reset_index()
    .drop(columns=["unit_price"])
)

assert shape == (3, 5)
assert result.shape == (3, 5)
assert result.columns.tolist() == ["order_id", "country", "quantity", "order_status", "revenue"]
assert result["revenue"].tolist() == [200.0, 250.0, 150.0]
assert status_counts.to_dict() == {"paid": 2, "pending": 1}
assert result.index.tolist() == [0, 1, 2]
```

#### Explanation

`DataFrame.from_records` makes the row structure explicit. The default Index is a `RangeIndex`. `assign` creates a derived column without changing the original frame. `set_index` changes the row-label role of `order_id`, while `reset_index` returns it to ordinary columns. `rename` changes a label and `drop` removes an unwanted column.

#### Expected Result

Three rows remain. Revenue is 200, 250, and 150. The final columns are `order_id`, `country`, `quantity`, `order_status`, and `revenue`.

#### Why This Works

The exercise makes the DataFrame's rows, columns, labels, and derived values explicit before more advanced transformations depend on them.

#### Validation

The assertions check shape, column order, values, status counts, and the restored index.

#### Common Mistake

Treating the Index as a cosmetic label and forgetting that `set_index` changes where the key lives.

#### Production Note

At pipeline boundaries, inspect and validate `shape`, `columns`, `dtypes`, and key uniqueness before applying downstream transformations.

---

### Q03 — Predict `.loc` versus `.iloc`

**Difficulty:** Basic  
**Topics:** Topic 03 — `loc`, `iloc`, label versus position

#### Problem

```python
import pandas as pd

df = pd.DataFrame(
    {"status": ["new", "paid", "shipped", "cancelled"]},
    index=[10, 20, 30, 40],
)
```

Compare `df.loc[20:30]` and `df.iloc[1:3]`.

**Expected output row count:** 2 for each.

#### Predict Before Running

Predict selected labels and statuses.

#### Solution

```python
loc_result = df.loc[20:30]
iloc_result = df.iloc[1:3]
assert loc_result.index.tolist() == [20, 30]
assert iloc_result.index.tolist() == [20, 30]
assert loc_result["status"].tolist() == ["paid", "shipped"]
assert iloc_result["status"].tolist() == ["paid", "shipped"]
```

#### Explanation

`.loc` is label-based and includes both slice endpoints. `.iloc` is position-based and excludes the stop position. They happen to select the same rows here.

#### Expected Result

Labels 20 and 30 with `paid` and `shipped`.

#### Why This Works

The important distinction is label versus position.

#### Validation

Check labels and values, not only length.

#### Common Mistake

Thinking `.loc[1]` means the second row.

#### Production Note

Use semantic labels for business selection and positions only when position is actually required.

---

### Q04 — Build a compound Boolean filter

**Difficulty:** Basic  
**Topics:** Topic 03 — Boolean masks, `isin`, `between`, `notna`

#### Problem

```python
import pandas as pd

orders = pd.DataFrame(
    {
        "order_id": [101, 102, 103, 104, 105],
        "country": ["IN", "US", "IN", "GB", "IN"],
        "amount": [500, 1200, None, 800, 1500],
        "status": ["paid", "paid", "paid", "pending", "paid"],
    }
)
```

**Grain:** one row = one order.

Select paid orders from `IN` or `US` with non-missing amount between 500 and 1500 inclusive.

**Expected output row count:** 3.

#### Predict Before Running

Predict the order IDs.

#### Solution

```python
mask = (
    orders["status"].eq("paid")
    & orders["country"].isin(["IN", "US"])
    & orders["amount"].between(500, 1500, inclusive="both")
    & orders["amount"].notna()
)
result = orders.loc[mask, ["order_id", "country", "amount"]]
assert len(result) == 3
assert result["order_id"].tolist() == [101, 102, 105]
```

#### Explanation

Series conditions are combined with element-wise `&`, with parentheses around each condition. `.between()` includes both endpoints here.

#### Expected Result

Orders 101, 102, 105.

#### Why This Works

The filter preserves one-row-per-order grain.

#### Validation

Assert row count and expected keys.

#### Common Mistake

Using Python `and` / `or` for Series.

#### Production Note

Record before/after counts around important filters.

---

### Q05 — Use `query()` parameters and backticks

**Difficulty:** Basic  
**Topics:** Topic 03 — `query`, `@local_variable`, backticks

#### Problem

```python
import pandas as pd

df = pd.DataFrame(
    {
        "country": ["IN", "US", "IN", "GB"],
        "order amount": [700, 900, 1500, 400],
        "status": ["paid", "paid", "paid", "pending"],
    }
)
threshold = 800
```

Return paid Indian rows with `order amount > threshold`.

**Expected output row count:** 1.

#### Solution

```python
result = df.query(
    "status == 'paid' and country == 'IN' and `order amount` > @threshold"
)
assert len(result) == 1
assert result["order amount"].iloc[0] == 1500
```

#### Explanation

Backticks allow a column containing spaces. `@threshold` refers to the Python variable outside the DataFrame.

#### Expected Result

One IN row with amount 1500.

#### Why This Works

`query()` changes selection syntax, not data grain.

#### Validation

Check the row count and amount.

#### Common Mistake

Omitting backticks around `order amount`.

#### Production Note

Keep runtime values as explicit parameters.

---

### Q06 — Preserve identifier formatting while reading CSV

**Difficulty:** Basic  
**Topics:** Topic 02 — `read_csv`, `dtype`, `parse_dates`, `date_format`, NA contract

#### Problem

Given:

```text
customer_id,zip_code,signup_date,status
0012,00701,2026-01-05,ACTIVE
0013,94105,2026-01-06,N/A
0014,02010,2026-01-07,
```

**Grain:** one row = one customer.

Read the file so IDs remain strings, the date is parsed, and `N/A` plus blank status are missing.


**Expected output row count:** 3.
#### Solution

```python
import pandas as pd

customers = pd.read_csv(
    "customers.csv",
    dtype={"customer_id": "string", "zip_code": "string", "status": "string"},
    parse_dates=["signup_date"],
    date_format="%Y-%m-%d",
    na_values=["N/A", ""],
    keep_default_na=False,
)

assert customers["customer_id"].tolist() == ["0012", "0013", "0014"]
assert customers["zip_code"].tolist() == ["00701", "94105", "02010"]
assert pd.api.types.is_datetime64_any_dtype(customers["signup_date"])
assert customers["status"].isna().sum() == 2
```

#### Explanation

IDs are labels, so integer inference would destroy leading zeros. A reader contract makes typing and missing-value semantics deliberate.

#### Expected Result

Three customer rows with preserved IDs, parsed dates, and two missing statuses.

#### Why This Works

Source ingestion defines schema semantics.

#### Validation

Check IDs, date dtype, missingness, and row count.

#### Common Mistake

Accepting inferred integer IDs.

#### Production Note

Keep the full reader contract under version control with the pipeline.

---

### Q07 — Use nullable `Int64` for missing identifiers

**Difficulty:** Basic  
**Topics:** Topic 04 — nullable integer, `pd.NA`, semantic dtype

#### Problem

```python
import pandas as pd

orders = pd.DataFrame({"customer_id": [101, None, 103]})
```

Convert the column to nullable integer without converting it to floating point.

**Expected output row count:** 3.

#### Solution

```python
orders["customer_id"] = orders["customer_id"].astype("Int64")
assert str(orders["customer_id"].dtype) == "Int64"
assert orders["customer_id"].tolist() == [101, pd.NA, 103]
assert len(orders) == 3
```

#### Explanation

Nullable `Int64` represents integer values and `pd.NA` together.

#### Expected Result

101, missing, 103 with dtype `Int64`.

#### Why This Works

The dtype preserves the identifier's integer domain and its missingness.

#### Validation

Check dtype and missing position.

#### Common Mistake

Using `float64` because it happens to hold `NaN`.

#### Production Note

Semantic schema decisions should survive ingestion and validation.

---

### Q08 — Decide whether to drop or fill missing values

**Difficulty:** Basic  
**Topics:** Topic 05 — missing values, `dropna`, `fillna`

#### Problem

```python
import pandas as pd

orders = pd.DataFrame(
    {
        "order_id": [1, 2, 3, 4],
        "amount": [100.0, None, 50.0, None],
        "coupon_code": ["SAVE10", None, None, "WELCOME"],
    }
)
```

Revenue calculations require amount, but missing coupon means “not recorded.” Produce the revenue-ready rows and fill only the coupon field.

**Expected output row count:** 2.

#### Solution

```python
result = orders.loc[orders["amount"].notna()].copy()
result["coupon_code"] = result["coupon_code"].fillna("NONE_RECORDED")

assert len(result) == 2
assert result["order_id"].tolist() == [1, 3]
assert result["coupon_code"].tolist() == ["SAVE10", "NONE_RECORDED"]

series = pd.Series([1.0, None, 3.0, None])
forward_filled = series.ffill()
backward_filled = series.bfill()
interpolated = series.interpolate()
assert forward_filled.tolist() == [1.0, 1.0, 3.0, 3.0]
assert backward_filled.tolist() == [1.0, 3.0, 3.0, 3.0]
assert interpolated.tolist() == [1.0, 2.0, 3.0, 3.0]
```

#### Explanation

Different missing fields can have different business meanings.

#### Expected Result

Orders 1 and 3 remain.

#### Why This Works

Only the metric-required missingness is used for row removal.

#### Validation

Assert retained keys and fill value.

#### Common Mistake

Dropping every row that has any missing value.

#### Production Note

Document drop/fill/fix/flag/quarantine decisions per field.

---

### Q09 — Distinguish `size()` from `count()`

**Difficulty:** Basic  
**Topics:** Topic 06 — `groupby`, `size`, `count`

#### Problem

```python
import pandas as pd

orders = pd.DataFrame(
    {
        "customer_id": ["C1", "C1", "C2", "C2"],
        "amount": [100, None, 50, None],
    }
)
```

Compute rows per customer with `size()` and non-missing amounts with `count()`.

**Expected output row count:** 2 for each result.

#### Solution

```python
size_result = orders.groupby("customer_id", as_index=False).size()
count_result = orders.groupby("customer_id", as_index=False)["amount"].count()

assert size_result["size"].tolist() == [2, 2]
assert count_result["amount"].tolist() == [1, 1]
```

#### Explanation

`size()` counts rows. `count()` ignores missing values in the selected column.

#### Expected Result

Both customers have two orders but one non-missing amount.

#### Why This Works

The metric definition determines the appropriate aggregation.

#### Validation

Assert values and row counts.

#### Common Mistake

Using `count()` for row volume when the counted field can be missing.

#### Production Note

State what exactly is being counted in every KPI.

---

### Q10 — Predict a many-to-one left join

**Difficulty:** Basic  
**Topics:** Topic 07 — `merge`, left join, `validate`, cardinality

#### Problem

```python
import pandas as pd

orders = pd.DataFrame({"order_id": [1, 2, 3], "customer_id": ["C1", "C1", "C2"], "amount": [100, 200, 50]})
customers = pd.DataFrame({"customer_id": ["C1", "C2"], "segment": ["Gold", "Silver"]})
```

**Grain:** orders = one row per order; customers = one row per customer.

Join segments onto orders.

**Expected output row count:** 3.

#### Predict Before Running

Will rows multiply or disappear?

#### Solution

```python
result = orders.merge(customers, on="customer_id", how="left", validate="many_to_one")
assert len(result) == 3
assert result["segment"].tolist() == ["Gold", "Gold", "Silver"]
assert result["amount"].sum() == 350

customer_lookup = customers.set_index("customer_id")
joined = orders.join(customer_lookup, on="customer_id", how="left", validate="many_to_one")
assert joined[["order_id", "customer_id", "amount", "segment"]].equals(result[["order_id", "customer_id", "amount", "segment"]])
```

#### Explanation

The right key is unique, so each order receives at most one customer record and the left population is preserved.

#### Expected Result

Three rows, unchanged total amount.

#### Why This Works

The join respects the declared many-to-one contract.

#### Validation

Check row count and revenue reconciliation.

#### Common Mistake

Assuming a merge call is correct without checking cardinality.

#### Production Note

Use `validate=` on important joins.

---

### Q11 — Melt wide monthly data into tidy form

**Difficulty:** Basic  
**Topics:** Topic 08 — `melt`, long format

#### Problem

```python
import pandas as pd

wide = pd.DataFrame({"country": ["IN", "US"], "Jan": [100, 200], "Feb": [120, 250], "Mar": [90, 300]})
```

**Input grain:** one row per country.  
**Output grain:** one row per country × month.

Melt to `country`, `month`, `revenue`.

**Expected output row count:** 6.

#### Solution

```python
long = wide.melt(
    id_vars="country",
    value_vars=["Jan", "Feb", "Mar"],
    var_name="month",
    value_name="revenue",
)
assert len(long) == 6
assert long.columns.tolist() == ["country", "month", "revenue"]
assert long.groupby("country").size().eq(3).all()
```

#### Explanation

Each country row expands into three country-month observations.

#### Expected Result

Six rows.

#### Why This Works

Month becomes data rather than a column-name convention.

#### Validation

Check row count and schema.

#### Common Mistake

Including the identifier in `value_vars`.

#### Production Note

State the grain before and after reshaping.

---

### Q12 — Extract datetime features, bucket timestamps, and compute daily revenue

**Difficulty:** Basic  
**Topics:** Topic 09 — `.dt`, DatetimeIndex, `resample`; Topic 10 — datetime accessors and formatting

#### Problem

```python
import pandas as pd

orders = pd.DataFrame(
    {
        "created_at": pd.to_datetime(
            [
                "2026-01-31 09:10",
                "2026-01-31 15:40",
                "2026-02-01 10:20",
            ]
        ),
        "amount": [100, 50, 75],
    }
)
```

Derive calendar features from `created_at`, create hourly floor/ceil/round buckets, format a stable reporting label, and calculate daily revenue.

**Output grain:** one row per observed calendar day for the revenue result.  
**Expected output row count:** 2.

#### Solution

```python
featured = orders.assign(
    year=orders["created_at"].dt.year,
    month=orders["created_at"].dt.month,
    day=orders["created_at"].dt.day,
    hour=orders["created_at"].dt.hour,
    dayofweek=orders["created_at"].dt.dayofweek,
    day_name=orders["created_at"].dt.day_name(),
    quarter=orders["created_at"].dt.quarter,
    date=orders["created_at"].dt.date,
    is_month_end=orders["created_at"].dt.is_month_end,
    hour_floor=orders["created_at"].dt.floor("h"),
    hour_ceil=orders["created_at"].dt.ceil("h"),
    hour_round=orders["created_at"].dt.round("h"),
    reporting_label=orders["created_at"].dt.strftime("%Y-%m-%d %H:%M"),
)

daily = (
    featured.set_index("created_at")["amount"]
    .resample("D")
    .sum()
    .rename("revenue")
    .reset_index()
)

assert featured["year"].tolist() == [2026, 2026, 2026]
assert featured["month"].tolist() == [1, 1, 2]
assert featured["day"].tolist() == [31, 31, 1]
assert featured["hour"].tolist() == [9, 15, 10]
assert featured["dayofweek"].tolist() == [5, 5, 6]
assert featured["quarter"].tolist() == [1, 1, 1]
assert featured["is_month_end"].tolist() == [True, True, False]
assert featured["reporting_label"].tolist() == [
    "2026-01-31 09:10",
    "2026-01-31 15:40",
    "2026-02-01 10:20",
]
assert featured["hour_floor"].tolist() == [
    pd.Timestamp("2026-01-31 09:00"),
    pd.Timestamp("2026-01-31 15:00"),
    pd.Timestamp("2026-02-01 10:00"),
]
assert featured["hour_ceil"].tolist() == [
    pd.Timestamp("2026-01-31 10:00"),
    pd.Timestamp("2026-01-31 16:00"),
    pd.Timestamp("2026-02-01 11:00"),
]
assert daily["revenue"].tolist() == [150, 75]
assert len(daily) == 2
```

#### Explanation

`.dt` provides vectorized calendar features. `floor`, `ceil`, and `round` are useful for deterministic time buckets. `strftime` creates a controlled text label instead of relying on locale-specific display formatting. Resampling uses the timestamp index to create daily bins.

#### Expected Result

January 31 revenue is 150 and February 1 revenue is 75. The first two rows are month-end observations; the third is not.

#### Why This Works

A datetime value contains multiple useful semantic dimensions. The important design step is to derive the intended business calendar explicitly rather than repeatedly parsing strings later.

#### Validation

Assert representative calendar fields, exact bucket boundaries, reporting labels, and the final row count.

#### Common Mistake

Using string slicing on timestamps for business logic and forgetting timezone or calendar semantics.

#### Production Note

Choose the reporting timezone before deriving `date`, month-end, weekday, or other calendar fields in production systems.

### Q13 — Normalize text with string accessors and named regex groups

**Difficulty:** Basic  
**Topics:** Topic 10 — `.str.strip`, `.str.lower`, `.str.upper`, `.str.title`, `.str.len`, `.str.startswith`, `.str.endswith`, `.str.contains`, `.str.replace`, `.str.slice`, `.str.zfill`, `.str.pad`, splitting, regex

#### Problem

```python
import pandas as pd

customers = pd.DataFrame(
    {
        "raw_code": ["  IN-12345  ", "us-77881", None, "GB-420"],
        "raw_name": pd.Series([" alice ", "BOB", None, "Charlie"], dtype="string"),
    }
)
```

Create a normalized code, title-case names, and demonstrate the common string-quality operations needed for this small dataset. Also split and regex-extract the code with named groups.

**Expected output row count:** 4.

#### Solution

```python
clean = customers.assign(
    code=customers["raw_code"].astype("string").str.strip().str.upper(),
    name=customers["raw_name"].str.strip(),
)

clean = clean.assign(
    name_lower=clean["name"].str.lower(),
    name_title=clean["name"].str.title(),
    name_len=clean["name"].str.len(),
    starts_with_a=clean["name"].str.lower().str.startswith("a", na=False),
    ends_with_e=clean["name"].str.endswith("e", na=False),
    code_contains_digits=clean["code"].str.contains(r"-\d+$", regex=True, na=False),
    compact_code=clean["code"].str.replace("-", "", regex=False),
    country_slice=clean["code"].str.slice(0, 2),
    export_code=clean["code"].str.pad(10, side="right", fillchar=" "),
)

clean[["country", "separator", "number_text"]] = clean["code"].str.partition("-")
clean["customer_number"] = clean["number_text"].str.zfill(5)
clean[["country_rx", "number_rx"]] = clean["code"].str.extract(
    r"^(?P<country_rx>[A-Z]{2})-(?P<number_rx>\d+)$"
)

rsplit_parts = clean["code"].str.rsplit("-", n=1, expand=True)
recombined = rsplit_parts[0].str.cat(rsplit_parts[1], sep="-")
all_matches = clean["code"].str.findall(r"[A-Z]{2}|\d+")
all_occurrences = clean.loc[clean["code"].notna(), "code"].str.extractall(
    r"(?P<token>[A-Z]{2}|\d+)"
)

assert len(clean) == 4
assert clean["name_title"].tolist() == ["Alice", "Bob", pd.NA, "Charlie"]
assert clean["name_len"].tolist() == [5, 3, pd.NA, 7]
assert clean["starts_with_a"].tolist() == [True, False, False, False]
assert clean["ends_with_e"].tolist() == [True, False, False, True]
assert clean["compact_code"].tolist() == ["IN12345", "US77881", pd.NA, "GB420"]
assert clean["country_slice"].tolist() == ["IN", "US", pd.NA, "GB"]
assert clean["customer_number"].tolist() == ["12345", "77881", pd.NA, "00420"]
assert clean.loc[0, "country_rx"] == "IN"
assert clean.loc[3, "number_rx"] == "420"
assert recombined.iloc[0] == "IN-12345"
assert recombined.iloc[3] == "GB-420"
assert all_matches.iloc[0] == ["IN", "12345"]
assert "token" in all_occurrences.columns
```

#### Explanation

The `.str` accessor keeps text transformations vectorized and readable. Missing-safe operations such as `na=False` make Boolean quality checks deterministic. `partition`/`rsplit` are useful for separator-based structure, while named regex groups make extracted fields self-documenting.

#### Expected Result

Codes are normalized to uppercase and whitespace-free; `GB-420` becomes `GB` + `00420`; names are normalized without inventing a value for the missing name.

#### Why This Works

Identifiers and text fields have semantics beyond display. Preserving them as strings avoids accidental loss of leading zeros and makes join keys stable.

#### Validation

Check row count, missing behavior, normalized values, regex output, and recombination.

#### Common Mistake

Calling `astype(int)` on a fixed-width identifier or using `.str.contains()` without deciding how missing values should behave.

#### Production Note

For Unicode text, apply an explicit normalization policy when visually equivalent values can have different underlying code points; test the rule before using it for joins.

### Q14 — Compose a readable transformation chain

**Difficulty:** Basic  
**Topics:** Topic 11 — method chaining, `assign`

#### Problem

```python
import pandas as pd

df = pd.DataFrame({"quantity": [2, 0, 3], "unit_price": [100.0, 200.0, 50.0]})
```

Create `revenue`, then a positive-order flag, then keep positive orders.

**Expected output row count:** 2.

#### Solution

```python
result = (
    df
    .assign(revenue=lambda d: d["quantity"] * d["unit_price"])
    .assign(is_positive=lambda d: d["quantity"].gt(0))
    .loc[lambda d: d["is_positive"]]
    .reset_index(drop=True)
)

assert len(result) == 2
assert result["revenue"].tolist() == [200.0, 150.0]
```

#### Explanation

Each method returns a DataFrame for the next method. The second `assign` can reference columns created by the first.

#### Expected Result

Two rows with revenue 200 and 150.

#### Why This Works

The data flow is visible without mutation-heavy scripting.

#### Validation

Check row count and values.

#### Common Mistake

Referencing a derived column before it is created.

#### Production Note

Break a chain into named intermediates when debugging becomes harder than reading it.

---

### Q15 — Stream a large CSV and keep only sufficient state

**Difficulty:** Basic  
**Topics:** Topic 13 — `chunksize`, `usecols`, bounded memory

#### Problem

A large CSV contains `order_id` and `amount_cents`. For this reproducible sample, stream two rows at a time and calculate total amount without keeping all rows.

```python
from io import StringIO
import pandas as pd

csv = StringIO("order_id,amount_cents\n1,100\n2,200\n3,50\n4,150\n")
```

#### Solution

```python
total = 0
for chunk in pd.read_csv(csv, chunksize=2, usecols=["amount_cents"]):
    total += chunk["amount_cents"].sum()

assert total == 500
```

#### Explanation

Only one chunk is held at a time and sum is exactly combinable across chunks.

#### Expected Result

500 cents.

#### Why This Works

The retained state is a scalar, not the raw dataset.

#### Validation

Assert the final total.

#### Common Mistake

Appending all chunks before aggregating.

#### Production Note

Chunk only after identifying the operation's recombination/state requirements.

---

# Part 2 — Moderate

## Q16–Q30

### Q16 — Detect duplicate and unsorted index labels before aligned arithmetic

**Difficulty:** Moderate  
**Topics:** Topic 01 — duplicate labels, `Index.is_unique`, `Index.is_monotonic_increasing`, alignment

#### Problem

```python
import pandas as pd

left = pd.Series([10, 20], index=["A", "A"], name="left")
right = pd.Series([3], index=["A"], name="right")
ordered = pd.Index(["A", "B", "C"])
unordered = pd.Index(["B", "A", "C"])
```

Determine whether the indexes are unique/monotonic and predict `left + right`.

**Expected output row count:** 2.

#### Solution

```python
assert left.index.is_unique is False
assert ordered.is_monotonic_increasing
assert not unordered.is_monotonic_increasing

result = left + right
assert len(result) == 2
assert result.index.tolist() == ["A", "A"]
assert result.tolist() == [13, 23]
```

#### Explanation

Duplicate labels are legal in pandas, so uniqueness must be validated when an index is intended to act like a key. `is_monotonic_increasing` answers an ordering question; it does not imply uniqueness. Arithmetic aligns by label, so the single `A` in `right` aligns with both `A` rows in `left`.

#### Expected Result

The aligned result has two `A` rows with values 13 and 23. The ordered index is monotonic; the unsorted index is not.

#### Why This Works

The index is part of pandas semantics, not merely presentation. Correctness requires reasoning about both label identity and label properties.

#### Validation

Assert uniqueness, monotonicity, output index, and values.

#### Common Mistake

Assuming duplicate labels are automatically rejected or assuming arithmetic is positional.

#### Production Note

For time-series selection and other order-sensitive operations, validate monotonic ordering explicitly when the downstream contract requires it.

### Q17 — Test JSON Lines, Parquet, Excel, and SQL round trips

**Difficulty:** Moderate  
**Topics:** Topic 02 — JSON Lines, Parquet, Excel, SQL, `to_*`/`read_*` contracts, round-trip testing

#### Problem

```python
import pandas as pd

source = pd.DataFrame(
    {
        "customer_id": pd.Series(["001", "002", "003"], dtype="string"),
        "amount": pd.Series([100, 250, 300], dtype="Int64"),
    }
)
```

Round-trip this small table through JSON Lines, Parquet, Excel, and an in-memory SQL table. Preserve customer identifiers exactly. Validate Parquet exactly; for text/spreadsheet/SQL formats validate the business values and explain why dtype reconstruction can differ.

**Input/output grain:** one row per customer.  
**Expected output row count:** 3 for every round-trip result.

#### Predict Before Running

Predict which formats are most likely to preserve the pandas nullable dtypes exactly and which may require dtype normalization after reading.

#### Solution

```python
from io import StringIO
from pathlib import Path
import tempfile

import pandas as pd
from sqlalchemy import create_engine

source = pd.DataFrame(
    {
        "customer_id": pd.Series(["001", "002", "003"], dtype="string"),
        "amount": pd.Series([100, 250, 300], dtype="Int64"),
    }
)

json_text = source.to_json(orient="records", lines=True)
json_back = pd.read_json(StringIO(json_text), lines=True)
assert len(json_back) == 3
assert json_back["customer_id"].astype("string").tolist() == ["001", "002", "003"]
assert json_back["amount"].tolist() == [100, 250, 300]

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)

    parquet_path = tmp / "customers.parquet"
    source.to_parquet(parquet_path, index=False)
    parquet_back = pd.read_parquet(parquet_path)
    pd.testing.assert_frame_equal(source, parquet_back)

    excel_path = tmp / "customers.xlsx"
    source.to_excel(excel_path, sheet_name="Customers", index=False, engine="openpyxl")
    excel_back = pd.read_excel(excel_path, sheet_name="Customers", engine="openpyxl")
    assert len(excel_back) == 3
    assert excel_back["customer_id"].astype("string").tolist() == ["001", "002", "003"]
    assert excel_back["amount"].tolist() == [100, 250, 300]

    engine = create_engine("sqlite:///:memory:")
    source.to_sql("customers", engine, index=False, if_exists="replace")
    sql_back = pd.read_sql("SELECT customer_id, amount FROM customers ORDER BY customer_id", engine)
    assert len(sql_back) == 3
    assert sql_back["customer_id"].astype("string").tolist() == ["001", "002", "003"]
    assert sql_back["amount"].tolist() == [100, 250, 300]


    malformed = StringIO("customer_id,amount\n001,100,EXTRA\n002,250\n")
    try:
        pd.read_csv(malformed, on_bad_lines="error")
    except pd.errors.ParserError:
        bad_input_detected = True
    else:
        bad_input_detected = False
    assert bad_input_detected


    tsv_gz = tmp / "customers.tsv.gz"
    source.to_csv(tsv_gz, sep="\t", header=True, index=False, encoding="utf-8", compression="gzip")
    tsv_back = pd.read_csv(tsv_gz, sep="\t", header=0, encoding="utf-8", compression="gzip", dtype={"customer_id": "string"})
    assert tsv_back["customer_id"].tolist() == ["001", "002", "003"]

    headerless = StringIO("001|100\n002|250\n")
    headerless_back = pd.read_csv(headerless, sep="|", header=None, names=["customer_id", "amount"], dtype={"customer_id": "string", "amount": "Int64"})
    assert headerless_back["customer_id"].tolist() == ["001", "002"]

    malformed = StringIO("customer_id,amount\n001,100,EXTRA\n002,250\n")
    try:
        pd.read_csv(malformed, on_bad_lines="error")
    except pd.errors.ParserError:
        bad_input_detected = True
    else:
        bad_input_detected = False
    assert bad_input_detected
```

#### Explanation

JSON Lines and Excel are format-specific representations whose readers may reconstruct dtypes differently. Parquet carries typed columnar metadata and is therefore well suited to exact typed round-trip contracts. SQL has database-side types but still requires an explicit pandas schema check after reading.

#### Expected Result

Three customer rows are preserved in every representation, including leading zeros in `customer_id`.

#### Why This Works

Round-trip testing verifies values, row count, column identity, and—where required—dtype.

#### Validation

Use `assert_frame_equal` where exact representation is part of the contract and explicit value/schema assertions where a format legitimately reconstructs a different pandas dtype.

#### Common Mistake

Assuming a write/read cycle is lossless merely because the row count stayed the same.

#### Production Note

For Excel, inspect header placement and merged-cell layouts rather than relying on defaults. For SQL, use a controlled engine/connection and explicit schema expectations.

---

### Q18 — Debug mixed selection and preserve schema for empty results

**Difficulty:** Moderate  
**Topics:** Topic 03 — `at`, `iat`, `where`, `mask`, `select_dtypes`, `filter`, empty results

#### Problem

```python
import pandas as pd

orders = pd.DataFrame(
    {"order_id": [10, 20, 30], "amount": [100, 200, 300], "status": ["paid", "pending", "paid"]},
    index=[101, 102, 103],
)
```

Read one value with `at`, another with `iat`; create a paid-only amount Series without dropping rows; select numeric columns and `status` using both `filter(like=...)` and `filter(regex=...)`; and return a schema-preserving empty result for `cancelled`.

#### Solution

```python
label_value = orders.at[101, "amount"]
position_value = orders.iat[1, 2]
paid = orders["amount"].where(orders["status"].eq("paid"))
masked = orders["amount"].mask(orders["status"].ne("paid"))
numeric = orders.select_dtypes(include="number")
status_like = orders.filter(like="status")
status_regex = orders.filter(regex=r"^status$")
empty = orders.loc[orders["status"].eq("cancelled"), orders.columns]

assert label_value == 100
assert position_value == "pending"
assert paid.iloc[0] == 100 and pd.isna(paid.iloc[1]) and paid.iloc[2] == 300
assert masked.equals(paid)
assert numeric.columns.tolist() == ["order_id", "amount"]
assert status_like.columns.tolist() == ["status"]
assert status_regex.columns.tolist() == ["status"]
assert empty.empty and empty.columns.tolist() == orders.columns.tolist()
```

#### Explanation

`at` is label-based and `iat` is position-based. `where` keeps values that pass its condition while `mask` replaces values where its condition is true. `filter(like=...)` and `filter(regex=...)` operate on labels, while `select_dtypes` operates on dtype metadata.

#### Expected Result

The scalar values are 100 and `pending`; paid amounts are 100/missing/300; and the empty result still has all three expected columns.

#### Why This Works

Good pandas selection code reasons about row labels, positions, values, and output schema separately.

#### Validation

Assert scalar values, selected columns, and empty-frame schema.

#### Common Mistake

Confusing row label 101 with position 101, or assuming an empty filter should return no columns.

#### Production Note

Stable empty schemas make downstream pipeline stages easier to test and compose.

### Q19 — Reason about `pd.NA` and nullable Boolean logic

**Difficulty:** Moderate  
**Topics:** Topic 04 — `boolean`, `pd.NA`, three-valued logic

**Expected output row count:** 3 for each Boolean Series.

#### Problem

```python
import pandas as pd
flags = pd.Series([True, False, pd.NA], dtype="boolean")
```

Evaluate `flags & True`, `flags | True`, and `~flags`.

#### Solution

```python
and_true = flags & True
or_true = flags | True
not_flags = ~flags

assert and_true.tolist() == [True, False, pd.NA]
assert or_true.tolist() == [True, True, True]
assert not_flags.tolist() == [False, True, pd.NA]


import numpy as np
nullable_int = pd.Series([1, pd.NA, 3], dtype="Int64")
float_missing = pd.Series([1.0, np.nan, 3.0])
object_missing = pd.Series([1, None, 3], dtype="object")
assert pd.isna(nullable_int.iloc[1])
assert pd.isna(float_missing.iloc[1])
assert pd.isna(object_missing.iloc[1])
```

#### Explanation

Nullable Boolean supports unknown state. A missing value is not automatically false; some logical expressions can resolve an unknown and some cannot.

#### Expected Result

Unknown remains unknown under `& True` and negation, while `| True` is always true.

#### Why This Works

The logic preserves uncertainty.

#### Validation

Assert exact three-valued results.

#### Common Mistake

Filling missing flags with false without checking meaning.

#### Production Note

Use nullable Boolean when “unknown” and “false” are distinct business states.

---

### Q20 — Keep the latest record per business key

**Difficulty:** Moderate  
**Topics:** Topic 05 — business-key deduplication, sorting, `drop_duplicates`

**Expected output row count:** 2.

#### Problem

```python
import pandas as pd

orders = pd.DataFrame(
    {
        "order_id": ["O1", "O1", "O2", "O2"],
        "updated_at": pd.to_datetime(["2026-01-01", "2026-01-03", "2026-01-02", "2026-01-01"]),
        "amount": [100, 120, 50, 45],
    }
)
```

**Input grain:** one source row per order version.  
**Output grain:** one latest row per order.

#### Solution

```python
latest = (
    orders.sort_values(["order_id", "updated_at"])
    .drop_duplicates("order_id", keep="last")
    .sort_values("order_id")
    .reset_index(drop=True)
)

assert len(latest) == 2
assert latest["order_id"].is_unique
assert latest["amount"].tolist() == [120, 50]
```

#### Explanation

The business key is `order_id`; `updated_at` defines which source version survives.

#### Expected Result

O1 = 120, O2 = 50.

#### Why This Works

A duplicate rule needs both identity and survivor ordering.

#### Validation

Check key uniqueness and exact survivor values.

#### Common Mistake

Using full-row equality as the only definition of duplication.

#### Production Note

Keep raw versions for auditability.

---

### Q21 — Use `transform` for row-level group context

**Difficulty:** Moderate  
**Topics:** Topic 06 — `groupby`, `transform`, `agg`

#### Problem

```python
import pandas as pd

orders = pd.DataFrame(
    {"order_id": [1, 2, 3, 4], "customer_id": ["C1", "C1", "C2", "C2"], "amount": [100, 300, 50, 75]}
)
```

Add customer total to every order and flag an order when its amount exceeds half its customer's total.

**Output grain:** one row per order.  
**Expected output row count:** 4.

#### Solution

```python
result = orders.assign(
    customer_total=orders.groupby("customer_id")["amount"].transform("sum")
)
result["over_half"] = result["amount"] > result["customer_total"].mul(0.5)

assert len(result) == 4
assert result["customer_total"].tolist() == [400, 400, 125, 125]
assert result["over_half"].tolist() == [False, True, False, True]


summary = (
    orders.groupby("customer_id", dropna=False, observed=True, sort=False)
    .agg(
        order_count=("order_id", "size"),
        amount_count=("amount", "count"),
        distinct_orders=("order_id", "nunique"),
        first_order=("order_id", "first"),
        last_order=("order_id", "last"),
    )
    .reset_index()
)
assert "order_count" in summary.columns
assert summary["order_count"].sum() == len(orders)
```

#### Explanation

`agg` would reduce to one row per customer. `transform` broadcasts each group's total back to the original rows, preserving order grain.

#### Expected Result

Totals 400,400,125,125 and flags False,True,False,True.

#### Why This Works

The output needs group context without changing row count.

#### Validation

Assert row count and aligned totals.

#### Common Mistake

Using `agg` and then forgetting to restore the original grain.

#### Production Note

Choose grouped operations from the required output grain.

---

### Q22 — Use `filter` for whole-group retention

**Difficulty:** Moderate  
**Topics:** Topic 06 — `filter`, `transform`, `apply`

#### Problem

Keep all orders belonging to customers whose total amount exceeds 200.

```python
import pandas as pd

orders = pd.DataFrame(
    {"customer_id": ["C1", "C1", "C2", "C2", "C3"], "amount": [100, 150, 50, 75, 500]}
)
```

**Expected output row count:** 3.

#### Solution

```python
result = (
    orders.groupby("customer_id", group_keys=False)
    .filter(lambda g: g["amount"].sum() > 200)
    .reset_index(drop=True)
)

vectorized = orders.loc[orders.groupby("customer_id")["amount"].transform("sum") > 200].reset_index(drop=True)
pd.testing.assert_frame_equal(result, vectorized)
assert len(result) == 3
```

#### Explanation

`filter` expresses whole-group retention. A vectorized `transform` alternative avoids general-purpose `apply` when the predicate is simple.

#### Expected Result

C1 and C3 orders remain.

#### Why This Works

The question is whether an entire group survives, not what one aggregate row should look like.

#### Validation

Compare the two correct approaches.

#### Common Mistake

Using `apply` automatically for every group-level task.

#### Production Note

Use `apply` when its generality is actually required.

---

### Q23 — Predict join explosion, suffix collisions, and cardinality contracts

**Difficulty:** Moderate  
**Topics:** Topic 07 — join cardinality, `validate`, `suffixes`, row multiplication

#### Problem

```python
import pandas as pd

orders = pd.DataFrame(
    {
        "order_id": [1, 2],
        "customer_id": ["C1", "C1"],
        "amount": [100, 200],
        "status": ["pending", "paid"],
    }
)
customers = pd.DataFrame(
    {
        "customer_id": ["C1", "C1"],
        "segment": ["Gold", "Silver"],
        "status": ["active", "blocked"],
    }
)
```

The intended relationship is many orders → one customer, but the dimension contains duplicate customer keys. Predict the unconstrained row count, keep overlapping column names understandable with `suffixes=`, and show why `many_to_one` fails while `many_to_many` merely acknowledges the actual shape. Also demonstrate a genuine one-to-many contract with a unique left key.

**Expected output row count:** 4 for the unconstrained merge.

#### Solution

```python
unconstrained = orders.merge(
    customers,
    on="customer_id",
    how="left",
    suffixes=("_order", "_customer"),
)
assert len(unconstrained) == 4
assert unconstrained["amount"].sum() == 600
assert "status_order" in unconstrained.columns
assert "status_customer" in unconstrained.columns

try:
    orders.merge(customers, on="customer_id", how="left", validate="many_to_one")
except Exception:
    contract_failed = True
else:
    contract_failed = False
assert contract_failed

acknowledged = orders.merge(
    customers,
    on="customer_id",
    how="left",
    validate="many_to_many",
    suffixes=("_order", "_customer"),
)
assert len(acknowledged) == 4

one_left = pd.DataFrame({"customer_id": ["C1"]})
one_to_many = one_left.merge(customers, on="customer_id", how="left", validate="one_to_many")
assert len(one_to_many) == 2
```

#### Explanation

Two orders each match two customer rows, so the unconstrained result contains four rows and duplicates the order amounts. `suffixes` makes overlapping non-key columns explicit. `many_to_one` rejects the broken dimension contract; `many_to_many` does not protect the metric because it simply declares that duplicates are allowed. `one_to_many` is valid only when the left key is unique and the right key may repeat.

#### Expected Result

Unconstrained merge = 4 rows; the intended `many_to_one` contract fails; `many_to_many` succeeds but does not prevent row multiplication.

#### Why This Works

Join cardinality should be reasoned about before execution and encoded as a runtime contract.

#### Validation

Check row count, amount inflation, suffix handling, and contract outcomes.

#### Common Mistake

Using `validate="many_to_many"` as if it were a safety check.

#### Production Note

For financial measures, reconcile totals before and after joins and reject unexpected cardinality changes before publication.

### Q24 — Use `indicator=True`, `map`, and `combine_first` for reference-data checks

**Difficulty:** Moderate  
**Topics:** Topic 07 — `indicator`, anti-join, semi-join, key lookup, `combine_first`

#### Problem

```python
import pandas as pd

orders = pd.DataFrame({"order_id": [1, 2, 3], "customer_id": ["C1", "C2", "C3"]})
customers = pd.DataFrame({"customer_id": ["C1", "C3"], "tier": ["Gold", "Silver"]})
```

Return the anti-join and semi-join populations. Then use a Series lookup to attach customer tiers and apply a fallback only where the lookup is missing.

**Expected output row counts:** anti-join = 1; semi-join = 2.

#### Solution

```python
checked = orders.merge(customers, on="customer_id", how="left", indicator=True)
anti = checked.loc[checked["_merge"].eq("left_only"), orders.columns]
semi = checked.loc[checked["_merge"].eq("both"), orders.columns]

assert anti["order_id"].tolist() == [2]
assert semi["order_id"].tolist() == [1, 3]
assert len(anti) + len(semi) == len(orders)

lookup = customers.set_index("customer_id")["tier"]
mapped = orders["customer_id"].map(lookup)
fallback = mapped.combine_first(pd.Series("Unknown", index=orders.index))
assert fallback.tolist() == ["Gold", "Unknown", "Silver"]
```

#### Explanation

The left join preserves every order so `_merge` can classify rows. `map` is concise for a unique-key lookup into one output Series. `combine_first` fills missing aligned values from a fallback Series without changing the row index.

#### Expected Result

Anti = order 2; semi = orders 1 and 3; mapped tiers are Gold/missing/Silver, then fallback produces Gold/Unknown/Silver.

#### Why This Works

Lookup strategy should match the problem shape: `merge` for table enrichment, `map` for a single Series lookup, and `combine_first` when an aligned fallback is required.

#### Validation

Reconcile anti + semi populations to the input and assert the lookup values.

#### Common Mistake

Using a non-unique lookup Series with `map` and assuming it behaves like a safe many-to-one join.

#### Production Note

Validate reference-key uniqueness before using `map` as a business-critical enrichment mechanism.

### Q25 — Diagnose duplicate pivot keys

**Difficulty:** Moderate  
**Topics:** Topic 08 — `pivot`, `pivot_table`, duplicate keys, `aggfunc`

**Expected output row count:** 2 countries after aggregation.

#### Problem

```python
import pandas as pd

sales = pd.DataFrame({"country": ["IN", "IN", "US"], "month": ["Jan", "Jan", "Jan"], "revenue": [100, 25, 200]})
```

Explain why `pivot` is ambiguous and aggregate duplicate country-month rows correctly.

#### Solution

```python
try:
    sales.pivot(index="country", columns="month", values="revenue")
except ValueError:
    failed = True
else:
    failed = False

wide = sales.pivot_table(index="country", columns="month", values="revenue", aggfunc="sum", fill_value=0).reset_index()
assert failed
assert wide.loc[wide["country"].eq("IN"), "Jan"].iloc[0] == 125
assert wide.loc[wide["country"].eq("US"), "Jan"].iloc[0] == 200
assert len(wide) == 2
```

#### Explanation

`pivot` requires one value for each dimension pair. Duplicate IN/Jan values make the mapping ambiguous; `pivot_table` lets you define the aggregation rule.

#### Expected Result

IN/Jan = 125 and US/Jan = 200.

#### Why This Works

Reshaping depends on key uniqueness.

#### Validation

Assert the failure and the corrected output.

#### Common Mistake

Using aggregation to hide an unexplained data-quality problem.

#### Production Note

Investigate duplicate keys before choosing `aggfunc`.

---

### Q26 — Unstack a MultiIndex result

**Difficulty:** Moderate  
**Topics:** Topic 08 — `unstack`, MultiIndex, flattened columns

**Expected output row count:** 2 countries.

#### Problem

```python
import pandas as pd

orders = pd.DataFrame({"country": ["IN", "IN", "US"], "status": ["paid", "pending", "paid"], "amount": [100, 20, 200]})
```

Aggregate by country/status, unstack status into columns, and flatten the result to ordinary columns.

#### Solution

```python
grouped = orders.groupby(["country", "status"])["amount"].sum()
wide = grouped.unstack(fill_value=0).reset_index()
wide.columns = [str(c) for c in wide.columns]

assert wide["country"].tolist() == ["IN", "US"]
assert wide.loc[wide["country"].eq("IN"), "paid"].iloc[0] == 100
assert wide.loc[wide["country"].eq("US"), "pending"].iloc[0] == 0
```

#### Explanation

The groupby result has hierarchical index labels. `unstack` moves one level to columns; `reset_index` flattens the remaining hierarchy.

#### Expected Result

IN = paid 100/pending 20; US = paid 200/pending 0.

#### Why This Works

Unstack changes shape while groupby produced the measure.

#### Validation

Check key cells and column schema.

#### Common Mistake

Assuming an absent combination necessarily means a business zero.

#### Production Note

Zero-fill only when the source semantics justify it.

---

### Q27 — Prove a wide-to-long-to-wide round trip

**Difficulty:** Moderate  
**Topics:** Topic 08 — `melt`, `pivot`, round-trip validation

**Expected output row counts:** long = 4; round-trip wide = 2.

#### Problem

```python
import pandas as pd

wide = pd.DataFrame({"country": ["IN", "US"], "Jan": [100, 200], "Feb": [120, 250]})
```

Round-trip through long format and recover the exact original table.

#### Solution

```python
long = wide.melt(id_vars="country", value_vars=["Jan", "Feb"], var_name="month", value_name="revenue")
roundtrip = long.pivot(index="country", columns="month", values="revenue").reset_index().loc[:, ["country", "Jan", "Feb"]]

pd.testing.assert_frame_equal(wide, roundtrip)
assert len(long) == 4
```

#### Explanation

Each `(country, month)` pair is unique, so `pivot` is a lossless inverse of `melt` for this dataset.

#### Expected Result

The round-tripped DataFrame equals `wide`.

#### Why This Works

Full-frame equality validates shape, values, and representation together.

#### Validation

Use `assert_frame_equal`.

#### Common Mistake

Using an aggregation step that could hide duplicate keys.

#### Production Note

Define whether dtype and column order are part of the reshape contract.

---

### Q28 — Localize UTC, convert timezone, and use partial date selection

**Difficulty:** Moderate  
**Topics:** Topic 09 — `tz_localize`, `tz_convert`, DatetimeIndex, partial string selection; Topic 03 — `.loc`

#### Problem

```python
import pandas as pd

raw = pd.DataFrame(
    {
        "event_time": pd.to_datetime(["2026-01-10 18:30", "2026-01-11 19:00", "2026-02-01 10:00"]),
        "amount": [100, 50, 75],
    }
)
```

The source timestamps are UTC. Convert them to `Asia/Kolkata`, sort/set the DatetimeIndex, and select January 2026.

**Expected output row count:** 2.

#### Solution

```python
df = (
    raw.assign(event_time=raw["event_time"].dt.tz_localize("UTC"))
    .assign(event_time=lambda d: d["event_time"].dt.tz_convert("Asia/Kolkata"))
    .sort_values("event_time")
    .set_index("event_time")
)

january = df.loc["2026-01"]
assert len(january) == 2
assert str(january.index.tz) == "Asia/Kolkata"
assert january["amount"].tolist() == [100, 50]
```

#### Explanation

Localization assigns meaning to naive values; conversion changes their displayed timezone without changing the instant. The partial-string selection is then made against the business reporting timezone.

#### Expected Result

Two January rows in the India timezone.

#### Why This Works

Reporting date depends on the chosen timezone.

#### Validation

Check row count, timezone, and values.

#### Common Mistake

Adding a fixed number of hours manually.

#### Production Note

Separate UTC/event time from local business calendar semantics.

---

### Q29 — Compare `rolling(7)` with `rolling("7D")` and inspect `center`

**Difficulty:** Moderate  
**Topics:** Topic 09 — count-based rolling, time-based rolling, `center`, `pct_change`, irregular timestamps

#### Problem

```python
import pandas as pd

s = pd.Series([10, 20, 30], index=pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-10"]))
```

Explain and calculate the difference between a seven-observation window and a seven-day elapsed-time window. Also calculate percentage change and a centered time window.

**Expected output row count:** 3 observations in each result.

#### Solution

```python
count_window = s.rolling(7, min_periods=1).sum()
time_window = s.rolling("7D", min_periods=1).sum()
pct_change = s.pct_change(fill_method=None)
centered = s.rolling("7D", min_periods=1, center=True).sum()

assert count_window.tolist() == [10.0, 30.0, 60.0]
assert time_window.tolist() == [10.0, 30.0, 30.0]
assert pd.isna(pct_change.iloc[0])
assert pct_change.iloc[1] == 1.0
assert pct_change.iloc[2] == 0.5
assert len(centered) == 3
```

#### Explanation

`rolling(7)` means seven observations; `rolling("7D")` means a seven-day time interval. `center=True` centers the time window around each timestamp rather than looking only backward. On irregular data, these definitions are materially different.

#### Expected Result

At January 10, the observation-count window still contains all three observations, while the seven-day time window includes only the January 10 observation under the default time-window closure semantics. Percentage changes are 100% and 50% after the first missing value.

#### Why This Works

Window semantics encode the business definition of recency and direction. Irregular event spacing makes observation-count windows especially different from elapsed-time windows.

#### Validation

Assert both rolling definitions and percentage changes; inspect centered output rather than assuming it matches the backward-looking window.

#### Common Mistake

Reading `7` as seven calendar days or assuming `center=True` is equivalent to the default backward-looking window.

#### Production Note

Document window semantics, closure, and centering explicitly for business KPIs.

### Q30 — Normalize Unicode keys before joining

**Difficulty:** Moderate  
**Topics:** Topic 10 — Unicode NFKC, invisible whitespace; Topic 07 — key hygiene

#### Problem

```python
import pandas as pd
import unicodedata

left = pd.DataFrame({"customer_key": [" ACME\u00a0", "ＭＥＧＡ"]})
right = pd.DataFrame({"customer_key": ["ACME", "MEGA"], "tier": ["Gold", "Silver"]})
```

Normalize NFKC, replace non-breaking spaces, strip, uppercase, and then perform the join.

**Expected output row count:** 2.

#### Solution

```python
def normalize_key(value):
    if pd.isna(value):
        return value
    return unicodedata.normalize("NFKC", str(value)).replace("\u00a0", " ").strip().upper()

left_clean = left.assign(customer_key=left["customer_key"].map(normalize_key))
right_clean = right.assign(customer_key=right["customer_key"].map(normalize_key))
result = left_clean.merge(right_clean, on="customer_key", how="left", validate="one_to_one")

assert len(result) == 2
assert result["tier"].tolist() == ["Gold", "Silver"]
```

#### Explanation

Unicode compatibility normalization and invisible-whitespace cleanup address key mismatches that are not obvious visually.

#### Expected Result

Both keys match their reference tiers.

#### Why This Works

Join correctness depends on semantic key normalization.

#### Validation

Check row count, tiers, and one-to-one cardinality.

#### Common Mistake

Assuming `strip()` handles every Unicode equivalence issue.

#### Production Note

Version and test normalization rules.

---

# Part 3 — Hard

## Q31–Q45

### Q31 — Clean, quarantine, reconcile, and flag an outlier

**Difficulty:** Hard  
**Topics:** Topics 03, 04, 05 — selection, typing, normalization, business-key deduplication, quarantine, IQR, z-score, flagging

#### Problem

```python
import pandas as pd

raw = pd.DataFrame(
    {
        "order_id": ["O1", "O2", "O2", "O3", "O4", "O5"],
        "customer_id": ["C1", "C2", "C2", "C3", "C4", None],
        "amount": ["1000", "bad", "1200", "-50", "oops", "700"],
        "status": [" paid ", "PAID", "paid", "paid", "paid", "paid"],
    }
)
```

**Input grain:** one source row; duplicate `order_id` can represent later source versions.  
**Output grain:** clean/quarantine rows after business-key resolution.

Normalize status, flag source duplicates, coerce amount, exclude rows without customers, keep the last `order_id` version, quarantine non-positive/invalid amounts, and preserve a reason. Also demonstrate IQR and z-score outlier flags rather than automatically deleting an unusual value.

**Expected clean row count:** 2.  
**Expected quarantine row count:** 2.

#### Predict Before Running

Which order IDs survive and which are quarantined?

**Expected output row count:** 4 clean-or-quarantine rows after the mandatory-customer filter.

#### Solution

```python
raw = raw.assign(is_duplicate=raw.duplicated("order_id", keep=False))

converted_amount = pd.to_numeric(raw["amount"], errors="coerce")
cleaned = (
    raw.assign(
        status=raw["status"].str.strip().str.upper(),
        amount_num=converted_amount,
    )
    .loc[lambda d: d["customer_id"].notna()]
    .drop_duplicates("order_id", keep="last")
)

conversion_failures = raw["amount"].notna() & converted_amount.isna()
assert conversion_failures.sum() == 2

cleaned["dq_reason"] = pd.NA
cleaned.loc[cleaned["amount_num"].isna(), "dq_reason"] = "INVALID_AMOUNT"
cleaned.loc[
    cleaned["amount_num"].notna() & cleaned["amount_num"].le(0),
    "dq_reason",
] = "NON_POSITIVE_AMOUNT"

quarantine = cleaned.loc[cleaned["dq_reason"].notna()].copy()
valid = cleaned.loc[cleaned["dq_reason"].isna()].copy()

assert valid["order_id"].tolist() == ["O1", "O2"]
assert quarantine["order_id"].tolist() == ["O3", "O4"]
assert len(valid) == 2
assert len(quarantine) == 2
assert valid["order_id"].is_unique
assert len(valid) + len(quarantine) == len(cleaned)
assert cleaned.loc[cleaned["order_id"].eq("O2"), "is_duplicate"].iloc[0]

sample = pd.Series([100, 110, 120, 130, 1000])
q1, q3 = sample.quantile([0.25, 0.75])
iqr = q3 - q1
is_outlier_iqr = (sample < q1 - 1.5 * iqr) | (sample > q3 + 1.5 * iqr)
assert is_outlier_iqr.tolist() == [False, False, False, False, True]

z_sample = pd.Series([10, 11, 12, 11, 10, 100])
z_scores = (z_sample - z_sample.mean()) / z_sample.std(ddof=0)
z_flag = z_scores.abs().gt(2)
assert z_flag.iloc[-1]

clipped = z_sample.clip(lower=z_sample.min(), upper=50)
assert clipped.iloc[-1] == 50
```

#### Explanation

O2's later numeric version replaces its earlier bad version. O3 is non-positive; O4 is invalid; O5 is excluded because customer identity is required. The duplicate flag is retained as lineage information even after the latest-version reduction. IQR and z-score are detection tools, not automatic deletion policies.

#### Expected Result

Clean = O1, O2. Quarantine = O3, O4. The separate IQR example flags only 1000, and the z-score example flags the extreme final value.

#### Why This Works

Cleaning separates detection, business rules, action, and reconciliation. A statistical flag is evidence for investigation; a quarantine rule is an explicit business decision.

#### Validation

```python
assert len(valid) + len(quarantine) == len(cleaned)
assert valid["order_id"].is_unique
```

#### Common Mistake

Deleting every statistical outlier or collapsing duplicates before recording why the source was considered anomalous.

#### Production Note

Keep raw/Bronze records and audit Silver decisions with flags/reasons and count reconciliation.

### Q32 — Build multiple within-customer sequence metrics

**Difficulty:** Hard  
**Topics:** Topic 06 — `rank`, `cumcount`, `cumsum`, `shift`, `diff`; Topic 09 — ordering semantics

#### Problem

```python
import pandas as pd

orders = pd.DataFrame(
    {
        "customer_id": ["C1", "C1", "C1", "C2", "C2"],
        "order_id": ["O1", "O2", "O3", "O4", "O5"],
        "order_date": pd.to_datetime(
            ["2026-01-01", "2026-01-05", "2026-01-08", "2026-01-02", "2026-01-10"]
        ),
        "amount": [100, 50, 80, 40, 60],
    }
)
```

**Input grain:** one row = one order.

For each customer, sorted by `order_date`, calculate:

- `order_rank` by amount descending;
- `sequence` starting at 1;
- `running_amount`;
- `previous_amount`;
- `change_from_previous`.

**Expected output row count:** 5.

#### Solution

```python
result = orders.sort_values(["customer_id", "order_date"]).copy()
g = result.groupby("customer_id")

result["order_rank"] = g["amount"].rank(method="dense", ascending=False)
result["sequence"] = g.cumcount().add(1)
result["running_amount"] = g["amount"].cumsum()
result["previous_amount"] = g["amount"].shift()
result["change_from_previous"] = g["amount"].diff()

assert len(result) == 5
assert result.loc[result["customer_id"].eq("C1"), "sequence"].tolist() == [1, 2, 3]
assert result.loc[result["customer_id"].eq("C1"), "running_amount"].tolist() == [100, 150, 230]
assert pd.isna(result.loc[result["customer_id"].eq("C1"), "previous_amount"].iloc[0])
assert result.loc[result["customer_id"].eq("C1"), "change_from_previous"].iloc[1:].tolist() == [-50, 30]

top2 = (
    orders.groupby("customer_id")["amount"]
    .nlargest(2)
    .reset_index(name="amount")
)
assert len(top2) == 4
assert top2.loc[top2["customer_id"].eq("C1"), "amount"].tolist() == [100, 80]
```

#### Step-by-Step Explanation

These operations require a meaningful group order, so sorting by customer and date comes first. `rank` compares values within each group; `cumcount` numbers rows; `cumsum` computes a running total; `shift` exposes the previous value; `diff` subtracts the previous value.

#### Expected Result

For C1, running amounts are 100, 150, 230 and changes are missing, -50, +30. For C2, the same calculations restart at the group boundary.

#### Why This Works

Group-wise window-like calculations are only meaningful when the ordering is explicit.

#### Validation

Check row count, sequence boundaries, running totals, and first-value missingness.

#### Common Mistake

Calling `shift` or `diff` before sorting, which produces a mathematically valid but semantically wrong sequence.

#### Production Note

Make the ordering column part of the transformation contract whenever order-dependent metrics are published.

---

### Q33 — Predict join shape with composite keys and null keys

**Difficulty:** Hard  
**Topics:** Topic 04 — dtype/key hygiene; Topic 07 — composite keys, null-key behavior, cardinality

#### Problem

```python
import pandas as pd

orders = pd.DataFrame(
    {
        "order_id": [1, 2, 3, 4],
        "customer_id": ["C1", "C1", None, "C2"],
        "country": ["IN", "US", "IN", "US"],
        "amount": [100, 200, 50, 75],
    }
)
customers = pd.DataFrame(
    {
        "customer_id": ["C1", "C1", "C2"],
        "country": ["IN", "US", "US"],
        "segment": ["Gold-IN", "Gold-US", "Silver-US"],
    }
)
```

**Grain:** orders = one row per order; customer reference = one row per customer-country key.

1. Predict the row count of a left merge on both `customer_id` and `country`.
2. Explain what happens to the null customer key.
3. Validate that the composite right key is many-to-one.


**Expected output row count:** 4.
#### Solution

```python
result = orders.merge(
    customers,
    on=["customer_id", "country"],
    how="left",
    validate="many_to_one",
)

assert len(result) == 4
assert result.loc[result["order_id"].eq(1), "segment"].iloc[0] == "Gold-IN"
assert result.loc[result["order_id"].eq(3), "segment"].isna().iloc[0]
assert result["order_id"].is_unique
```

#### Step-by-Step Explanation

The composite key uniquely identifies each customer-country combination in the right table, so each order has at most one matching reference row. The unmatched null customer row is retained by the left join and receives missing dimension attributes. The key relationship is many-to-one from orders to the customer reference.

#### Expected Result

Four rows remain. Order 3 is unmatched. Orders 1, 2, and 4 receive their matching segments.

#### Why This Works

A business key may be composite; validating one column alone would not establish uniqueness.

#### Validation

Check row count, order uniqueness, and the unmatched order explicitly.

#### Common Mistake

Joining only on `customer_id` and accidentally attaching the wrong country-specific segment.

#### Production Note

Normalize key dtypes, whitespace, case, and composite-key components before the join, then validate cardinality.

---

### Q34 — Perform point-in-time FX enrichment with `merge_asof`

**Difficulty:** Hard  
**Topics:** Topic 07 — `merge_asof`, `by`, `direction`, `tolerance`; Topic 09 — timestamps, sorting

**Expected output row count:** 3, one output row per transaction.

#### Problem

Transactions must be enriched with the most recent FX rate at or before the transaction timestamp, separately by currency.

```python
import pandas as pd

transactions = pd.DataFrame(
    {
        "txn_id": [1, 2, 3],
        "currency": ["USD", "USD", "EUR"],
        "txn_time": pd.to_datetime(
            ["2026-01-01 10:05", "2026-01-01 10:35", "2026-01-01 10:20"]
        ),
        "amount": [100, 200, 50],
    }
)

rates = pd.DataFrame(
    {
        "currency": ["USD", "USD", "EUR", "EUR"],
        "rate_time": pd.to_datetime(
            ["2026-01-01 10:00", "2026-01-01 10:30", "2026-01-01 10:00", "2026-01-01 10:30"]
        ),
        "usd_per_unit": [1.00, 1.01, 1.10, 1.11],
    }
)
```

**Output grain:** one row per transaction.

Match the last rate at or before each transaction.

#### Solution

```python
left = transactions.sort_values("txn_time")
right = rates.sort_values("rate_time")

enriched = pd.merge_asof(
    left,
    right,
    left_on="txn_time",
    right_on="rate_time",
    by="currency",
    direction="backward",
)

assert len(enriched) == 3
assert enriched["usd_per_unit"].tolist() == [1.00, 1.10, 1.01]
assert enriched["txn_id"].is_unique
```

#### Step-by-Step Explanation

`merge_asof(..., direction="backward")` performs a temporal lookup to the latest right-side timestamp that is not after the left timestamp. `by="currency"` prevents USD transactions from using EUR rates. Both sides must be sorted by the time key for correct as-of matching.

#### Expected Result

Transaction 1 uses 1.00; transaction 3 uses 1.10; transaction 2 uses 1.01.

#### Why This Works

A point-in-time join is different from an equality join because the correct dimension record depends on time.

#### Validation

Check one-to-one transaction output and exact selected rates.

#### Common Mistake

Using a regular equality merge and losing valid transactions that occur between rate observations.

#### Production Note

Use `tolerance=` when a rate older than an acceptable business horizon should not be considered valid.

---

### Q35 — Produce grouped hourly metrics, detect gaps, build a calendar, and compute windows

**Difficulty:** Hard  
**Topics:** Topic 09 — `pd.Grouper`, `pd.date_range`, `resample`, rolling, gap detection, `asfreq`, expanding, ewm, business-day calendars; Topic 06 — grouped calculations

#### Problem

```python
import pandas as pd

logs = pd.DataFrame(
    {
        "device": ["A", "A", "A", "B", "B"],
        "event_time": pd.to_datetime(
            [
                "2026-01-01 09:10",
                "2026-01-01 09:50",
                "2026-01-01 11:05",
                "2026-01-01 09:20",
                "2026-01-01 10:10",
            ],
            utc=True,
        ),
        "value": [10, 20, 30, 5, 15],
    }
)
```

For each device, aggregate hourly means, detect gaps over one hour in the raw event stream, build the expected hourly calendar for device A, calculate a two-hour time-based rolling mean, and demonstrate `asfreq`, `expanding`, `ewm`, and a business-day calendar.

#### Solution

```python
hourly = (
    logs.groupby(["device", pd.Grouper(key="event_time", freq="1h")], as_index=False)
    .agg(mean_value=("value", "mean"))
    .sort_values(["device", "event_time"])
)

ordered = logs.sort_values(["device", "event_time"]).copy()
ordered["gap"] = ordered.groupby("device")["event_time"].diff()
gaps = ordered.loc[ordered["gap"] > pd.Timedelta(hours=1)]

expected_a_hours = pd.date_range(
    "2026-01-01 09:00",
    "2026-01-01 11:00",
    freq="1h",
    tz="UTC",
)
observed_a_hours = pd.DatetimeIndex(hourly.loc[hourly["device"].eq("A"), "event_time"])
missing_a_hours = expected_a_hours.difference(observed_a_hours)

hourly["rolling_2h"] = (
    hourly.set_index("event_time")
    .groupby("device")["mean_value"]
    .rolling("2h", min_periods=1)
    .mean()
    .reset_index(level=0, drop=True)
    .to_numpy()
)

series_a = (
    logs.loc[logs["device"].eq("A"), ["event_time", "value"]]
    .set_index("event_time")
    .sort_index()
)
regular = series_a["value"].asfreq("1h")
expanding_mean = regular.expanding(min_periods=1).mean()
ema = regular.ewm(span=3, adjust=False).mean()
business_calendar = pd.date_range("2026-01-01", "2026-01-07", freq="B", tz="UTC")

assert hourly["device"].nunique() == 2
assert gaps["device"].tolist() == ["A"]
assert missing_a_hours.tolist() == [pd.Timestamp("2026-01-01 10:00", tz="UTC")]
assert len(expanding_mean) == len(regular)
assert len(ema) == len(regular)
assert len(business_calendar) == 5
```

#### Step-by-Step Explanation

`Grouper` expresses an entity-plus-time grouping key. `date_range` creates the expected calendar, making missing periods explicit instead of inferring them from observed events. Gap detection depends on sorted timestamps. Rolling uses elapsed time; `asfreq` creates a regular frequency without inventing values; expanding and EWM summarize history differently.

#### Expected Result

Device A has a gap at 10:00 between observed 09:00 and 11:00 hourly bins. The business-day calendar contains five dates in the Monday–Friday convention for this range.

#### Why This Works

Time-series pipelines must distinguish observed events, expected calendars, and historical windows.

#### Validation

Check devices, missing calendar periods, gap detection, and derived-series lengths.

#### Common Mistake

Filling `asfreq` gaps without deciding whether “no event” means zero or unknown.

#### Production Note

A complete calendar is a business rule. Use it only when the metric's denominator and “no event” semantics are explicitly defined.

### Q36 — Reshape embedded year columns and one-hot encode a bounded category

**Difficulty:** Hard  
**Topics:** Topic 08 — `wide_to_long`, `get_dummies`, categorical thinking, shape-driven risk

**Expected output row count:** 4 long-form rows; 2 source rows for the encoded DataFrame.

#### Problem

```python
import pandas as pd

sales = pd.DataFrame(
    {
        "country": ["IN", "US"],
        "sales_2024": [100, 200],
        "sales_2025": [120, 250],
        "segment": ["Gold", "Silver"],
    }
)
```

1. Convert `sales_2024` and `sales_2025` into a long `year`/`sales` representation using `wide_to_long`.
2. One-hot encode the bounded `segment` field.
3. Explain why encoding a very high-cardinality identifier would create a dangerous number of columns.

#### Solution

```python
long = pd.wide_to_long(
    sales,
    stubnames="sales",
    i=["country", "segment"],
    j="year",
    sep="_",
    suffix=r"\d+",
).reset_index()

encoded = pd.get_dummies(
    sales,
    columns=["segment"],
    dtype="int8",
)

assert len(long) == 4
assert sorted(long["year"].tolist()) == [2024, 2024, 2025, 2025]
assert set(encoded.columns) == {"country", "sales_2024", "sales_2025", "segment_Gold", "segment_Silver"}

segment_counts = pd.crosstab(sales["country"], sales["segment"])
assert segment_counts.loc["IN", "Gold"] == 1
assert segment_counts.loc["US", "Silver"] == 1
```

#### Step-by-Step Explanation

`wide_to_long` extracts the embedded year dimension from column names. `get_dummies` converts a categorical field into indicator columns. For a bounded business category this may be practical; for millions of distinct customer IDs it can create extreme column explosion and memory pressure.

#### Expected Result

Four long-form rows and two additional indicator columns for the two observed segments.

#### Why This Works

Reshaping makes hidden dimensions explicit, while encoding changes the number of columns and therefore the memory/compute shape of the DataFrame.

#### Validation

Check output row count, year values, and encoded schema.

#### Common Mistake

One-hot encoding an identifier that was never intended to be a model feature.

#### Production Note

Treat column count as a resource constraint; wide and long forms have different operational costs.

---

### Q37 — Refactor a transformation into testable `pipe` steps

**Difficulty:** Hard  
**Topics:** Topic 05 — cleaning; Topic 06 — groupby; Topic 11 — method chaining, `pipe`, invariant checks

#### Problem

A Silver pipeline must:

1. normalize country codes;
2. remove rows without amount;
3. calculate customer revenue;
4. retain customers with revenue ≥ 200;
5. verify that customer IDs remain unique after aggregation.

```python
import pandas as pd

orders = pd.DataFrame(
    {
        "customer_id": ["C1", "C1", "C2", "C3"],
        "country": [" in ", "IN", "US", "us"],
        "amount": [100, 150, None, 250],
    }
)
```

Use named functions with `pipe()` rather than hiding all logic in lambdas.

#### Solution

```python
def normalize_country(df):
    return df.assign(country=df["country"].str.strip().str.upper())


def require_amount(df):
    return df.loc[df["amount"].notna()].copy()


def customer_revenue(df):
    return (
        df.groupby(["customer_id", "country"], as_index=False, sort=False)
        .agg(revenue=("amount", "sum"))
    )


def keep_large_customers(df, minimum=200):
    return df.loc[df["revenue"].ge(minimum)].copy()


def check_unique_customer_keys(df):
    expected = len(df)
    if not df["customer_id"].is_unique:
        raise ValueError("customer_id must be unique after aggregation")
    if len(df) != expected:
        raise AssertionError("unexpected row-count mutation")
    return df

result = (
    orders
    .pipe(normalize_country)
    .pipe(require_amount)
    .pipe(customer_revenue)
    .pipe(keep_large_customers, minimum=200)
    .pipe(check_unique_customer_keys)
)

assert result.to_dict("records") == [
    {"customer_id": "C1", "country": "IN", "revenue": 250},
    {"customer_id": "C3", "country": "US", "revenue": 250},
]


legacy = result.copy()
legacy.drop(columns=["country"], inplace=True)
safe = result.drop(columns=["country"])
assert legacy.equals(safe)
```

#### Step-by-Step Explanation

Each named function has one responsibility and receives a DataFrame through `pipe()`. The grouping changes the grain from order to customer-country. The uniqueness check is now explicit at a meaningful phase boundary.

#### Expected Result

Two aggregated customers remain: C1/IN = 250 and C3/US = 250.

#### Why This Works

`pipe()` is most useful when custom DataFrame-level logic can be named, tested, and composed rather than buried inside a giant expression.

#### Validation

The exact expected records and uniqueness invariant are checked.

#### Common Mistake

Forcing every operation into a single 30-line chain and making debugging harder.

#### Production Note

A readable pipeline should expose meaningful phase boundaries and invariants, not maximize the number of chained methods.

---

### Q38 — Debug chained assignment and prove input immutability

**Difficulty:** Hard  
**Topics:** Topic 12 — CoW, chained assignment, `.loc`, `.copy()`, `to_numpy`; Topic 11 — pure transformations/testing

#### Problem

```python
import pandas as pd

source = pd.DataFrame({"amount": [50, 150, 250], "flag": [False, False, False]})
subset = source[source["amount"] > 100]
subset["flag"] = True
```

Under modern Copy-on-Write semantics, answer whether `source` changes. Then write a function that intentionally does not mutate its input and prove it with a deep-copy snapshot.

#### Solution

```python
assert source["flag"].tolist() == [False, False, False]
assert subset["flag"].tolist() == [True, True]


def add_high_value_flag(df, threshold=100):
    return df.assign(high_value=df["amount"].gt(threshold))

original = source.copy(deep=True)
result = add_high_value_flag(source)
pd.testing.assert_frame_equal(source, original)
assert result["high_value"].tolist() == [False, True, True]
```

For conditional mutation of the parent itself, the explicit pattern is:

```python
source.loc[source["amount"] > 100, "flag"] = True
```

#### Step-by-Step Explanation

The filtered `subset` is a derived pandas object and, under modern CoW semantics, modifying it does not mutate the parent. When the intended owner is the parent, use one `.loc` assignment. For reusable transformations, returning a new result makes input ownership explicit and easy to test.

#### Expected Result

`source.flag` remains all false after modifying `subset`.

#### Why This Works

CoW separates logical mutation semantics from internal storage sharing. `.copy()` is useful when explicit independent ownership is part of a function or memory-lifetime contract.

#### Validation

The deep-copy comparison proves the transformation did not mutate the caller's DataFrame.

#### Common Mistake

Treating the absence of a visible warning as proof that mutation semantics are correct.

#### Production Note

Also test NumPy boundaries deliberately; `to_numpy()` may produce a read-only array, and an explicit copy may be required before mutation.

---

### Q39 — Correct an average-of-averages chunking bug

**Difficulty:** Hard  
**Topics:** Topic 13 — chunked processing, partial aggregation, sufficient statistics; Topic 06 — groupby aggregation

#### Problem

A 20 GB CSV contains `country` and `amount`. A developer calculates a mean per country in each chunk and then averages those chunk means. Explain why this can be wrong and implement the correct method.

#### Solution

```python
from io import StringIO
import pandas as pd

csv = StringIO(
    "country,amount\n"
    "IN,10\n"
    "IN,20\n"
    "IN,100\n"
    "US,5\n"
    "US,15\n"
)

partials = []
for chunk in pd.read_csv(csv, chunksize=2):
    partials.append(
        chunk.groupby("country")["amount"]
        .agg(total="sum", count="count")
    )

combined = pd.concat(partials).groupby(level=0).sum()
correct_mean = combined["total"] / combined["count"]

assert correct_mean["IN"] == 130 / 3
assert correct_mean["US"] == 10
```

#### Step-by-Step Explanation

The simple average of chunk means gives every chunk equal weight even if chunks contain different numbers of rows for a country. The mathematically sufficient state for an ordinary mean is `sum` plus `count`. Combine those across chunks and divide once at the end.

#### Expected Result

IN mean = `43.333...`; US mean = `10`.

#### Why This Works

Chunking changes the computation strategy but must not change the mathematics.

#### Validation

Compare the final mean to the direct mathematical result; for real data, compare with a smaller full-load sample as a correctness test.

#### Common Mistake

`partials.groupby(...).mean()` on already-computed chunk means.

#### Production Note

For every chunked metric, identify the minimum sufficient statistics required for exact recombination.

---

### Q40 — Deduplicate across chunk boundaries

**Difficulty:** Hard  
**Topics:** Topic 13 — cross-chunk deduplication, state; Topic 05 — business-key deduplication

#### Problem

Each chunk below is independently deduplicated, but the same `order_id` can occur in different chunks. Keep the first occurrence globally.

```python
import pandas as pd

chunks = [
    pd.DataFrame({"order_id": ["O1", "O2"], "amount": [100, 200]}),
    pd.DataFrame({"order_id": ["O2", "O3"], "amount": [250, 300]}),
]
```

Explain why chunk-local `drop_duplicates()` is insufficient and implement a global solution without concatenating the raw chunks first.

#### Solution

```python
seen = set()
outputs = []

for chunk in chunks:
    keep = ~chunk["order_id"].isin(seen)
    current = chunk.loc[keep].copy()
    seen.update(current["order_id"].tolist())
    outputs.append(current)

result = pd.concat(outputs, ignore_index=True)

assert result["order_id"].tolist() == ["O1", "O2", "O3"]
assert result["order_id"].is_unique
```

#### Step-by-Step Explanation

The second chunk does not know that `O2` appeared earlier unless state is carried across the boundary. A global `seen` set supplies that state. For a more complex “latest record wins” rule, the carried state must retain the necessary version information rather than only the key.

#### Expected Result

Three global records: O1, O2 from the first chunk, and O3.

#### Why This Works

Deduplication by business key is not inherently chunk-independent.

#### Validation

Assert global uniqueness and exact survivor order.

#### Common Mistake

Calling `chunk.drop_duplicates()` and assuming local uniqueness implies global uniqueness.

#### Production Note

For partitioned production data, consider whether the partitioning key can make the deduplication naturally local; otherwise design an explicit cross-partition state strategy.

---

### Q41 — Carry session and rolling state across chunks

**Difficulty:** Hard  
**Topics:** Topic 13 — stateful chunk processing; Topic 09 — session/window semantics

#### Problem

A clickstream arrives in timestamp order but is split into chunks:

```text
chunk 1: A at 10:00, A at 10:20
chunk 2: A at 10:35, A at 11:40
```

A new session begins after 30 minutes of inactivity. Also calculate a three-event rolling total per user. Explain what state must cross the chunk boundary.

#### Solution

```python
import pandas as pd

chunks = [
    pd.DataFrame({
        "user": ["A", "A"],
        "event_time": pd.to_datetime(["2026-01-01 10:00", "2026-01-01 10:20"]),
        "value": [10, 20],
    }),
    pd.DataFrame({
        "user": ["A", "A"],
        "event_time": pd.to_datetime(["2026-01-01 10:35", "2026-01-01 11:40"]),
        "value": [30, 40],
    }),
]

last_time = {}
rolling_values = {}
outputs = []

for chunk in chunks:
    chunk = chunk.sort_values(["user", "event_time"]).copy()
    session_ids = []
    rolling_totals = []

    for row in chunk.itertuples(index=False):
        previous = last_time.get(row.user)
        is_new = previous is None or row.event_time - previous > pd.Timedelta(minutes=30)
        state = rolling_values.setdefault(row.user, [])
        state.append(row.value)
        state[:] = state[-3:]
        session_ids.append(is_new)
        rolling_totals.append(sum(state))
        last_time[row.user] = row.event_time

    chunk["new_session"] = session_ids
    chunk["rolling_3_event_sum"] = rolling_totals
    outputs.append(chunk)

result = pd.concat(outputs, ignore_index=True)

assert result["new_session"].tolist() == [True, False, False, True]
assert result["rolling_3_event_sum"].tolist() == [10, 30, 60, 90]
```

#### Step-by-Step Explanation

The first event initializes state. For later chunks, the last event time per user determines whether a new session begins, and the previous two values may be needed to continue a three-event rolling window. The exact carried state depends on the window/session definition.

#### Expected Result

Session starts occur at 10:00 and 11:40. Rolling sums continue across the boundary: 10, 30, 60, 90.

#### Why This Works

Stateful operations cannot be treated as independent chunks because the answer for the first rows of a new chunk can depend on prior data.

#### Validation

Assert both session boundaries and rolling values.

#### Common Mistake

Resetting session/rolling state at the beginning of every chunk.

#### Production Note

Document carried state explicitly; it is part of the job's correctness contract and restart behavior.

---

### Q42 — Measure dtype memory reduction without inventing a benchmark

**Difficulty:** Hard  
**Topics:** Topic 04 — dtype choice, categories, Arrow strings; Topic 13 — memory measurement, deep memory, peak vs final memory

#### Problem

```python
import pandas as pd

orders = pd.DataFrame(
    {
        "country": ["IN", "US", "IN", "IN", "US"],
        "status": ["paid", "paid", "pending", "paid", "pending"],
        "quantity": [1, 2, 3, 4, 5],
        "customer_note": ["ok", "ok", "hold", "ok", "review"],
    }
)
```

Measure memory before and after reasonable dtype optimization. Do not report a fabricated percentage. Explain why DataFrame memory and process peak memory are different measurements.

#### Solution

```python
before = orders.memory_usage(deep=True).sum()

optimized = orders.astype(
    {
        "country": "category",
        "status": "category",
        "quantity": "int8",
        "customer_note": "string",
    }
)
after = optimized.memory_usage(deep=True).sum()

assert after <= before

reduction = before - after
print({"before_bytes": int(before), "after_bytes": int(after), "reduction_bytes": int(reduction)})
```

#### Step-by-Step Explanation

`memory_usage(deep=True)` estimates DataFrame-level memory more fully than shallow object accounting. Low-cardinality repeated labels can benefit from categorical storage, while a small integer domain can fit in a smaller integer dtype. None of these numbers tell you the peak resident memory of a running process: temporary objects, groupby structures, copies, retained chunks, and allocator behavior can push process RSS higher than the final frame's footprint.

#### Expected Result

The exact byte counts are machine/version-dependent and must be measured by the learner. The code asserts only the observed direction for this sample.

#### Why This Works

Memory engineering requires measurement rather than assumptions, and peak memory is a different operational concern from final object size.

#### Validation

Record before/after bytes and, for production jobs, separately measure process peak memory with an appropriate system/profiling method.

#### Common Mistake

Saying “the optimized frame uses 70% less memory” without measuring it.

#### Production Note

Optimize semantic dtypes first, then measure representative workloads including peak memory and runtime.

---

### Q43 — Design a reliable Parquet output contract

**Difficulty:** Hard  
**Topics:** Topic 02 — Parquet, explicit schema, `columns`, `partition_cols`, reliable writing; Topic 13 — memory-aware output

#### Problem

A Silver pipeline produces an orders DataFrame with extra debug columns. Downstream consumers need deterministic columns `order_id`, `customer_id`, `amount_cents`, `country`. Data should be partitioned by `country`.

Describe and implement the DataFrame-side part of the contract, including deterministic column order and a safe output finalization pattern.

#### Solution

```python
import os
from pathlib import Path
import pandas as pd

orders = pd.DataFrame(
    {
        "debug_message": ["x", "y"],
        "country": ["IN", "US"],
        "amount_cents": [100, 200],
        "customer_id": ["C1", "C2"],
        "order_id": [1, 2],
    }
)

columns = ["order_id", "customer_id", "amount_cents", "country"]
output = orders.loc[:, columns].copy()

assert output.columns.tolist() == columns
assert len(output) == len(orders)

# Read-side projection/filtering examples for the published dataset:
# projected = pd.read_parquet("silver/orders", columns=["order_id", "amount_cents"])
# india_only = pd.read_parquet(
#     "silver/orders",
#     columns=["order_id", "amount_cents", "country"],
#     filters=[("country", "==", "IN")],
# )

# Safe-finalization pattern for a real filesystem job:
# final_dir = Path("silver/orders")
# temp_dir = Path("silver/orders._tmp")
# output.to_parquet(temp_dir, index=False, partition_cols=["country"])
# os.replace(temp_dir, final_dir)  # use the filesystem-safe strategy appropriate to the job
```

For reads, downstream consumers can project only required columns with `read_parquet(columns=[...])` and use filters where the dataset layout supports them.

#### Step-by-Step Explanation

The DataFrame is reduced to a deterministic contract before serialization. `partition_cols` shapes the Parquet directory layout; `columns=` and `filters=` can reduce downstream work. The temporary-output pattern prevents a consumer from seeing a partially written final location when the underlying filesystem supports atomic replacement for the chosen object/layout.

#### Expected Result

The contract has exactly four columns in fixed order, with row count unchanged.

#### Why This Works

Reliable output is both a schema problem and a failure-handling problem.

#### Validation

Assert exact columns and row preservation. A write/read round trip should use `pd.testing.assert_frame_equal` when exact representation is part of the contract.

#### Common Mistake

Allowing accidental debug columns or writing the DataFrame index when it is not part of the business schema.

#### Production Note

Keep output schemas deterministic and separate temporary output from the published location.

---

### Q44 — Select and flatten a MultiIndex safely

**Difficulty:** Hard  
**Topics:** Topics 01 and 03 — MultiIndex, tuple selection, `xs`, `IndexSlice`, `swaplevel`, sorting, flattening

#### Problem

```python
import pandas as pd

revenue = pd.DataFrame(
    {
        "country": ["IN", "IN", "US", "US"],
        "month": ["2026-01", "2026-02", "2026-01", "2026-02"],
        "revenue": [100, 120, 80, 200],
    }
).set_index(["country", "month"])
```

Select IN/2026-02 by tuple, January across countries with `xs`, both IN months with `IndexSlice`, then swap/sort levels and flatten.


**Expected output row count:** 4.
#### Solution

```python
idx = pd.IndexSlice
in_feb = revenue.loc[("IN", "2026-02"), "revenue"]
jan = revenue.xs("2026-01", level="month")
in_all = revenue.loc[idx["IN", :], :]
swapped = revenue.swaplevel("country", "month").sort_index()
flat = revenue.reset_index()

assert in_feb == 120
assert jan["revenue"].to_dict() == {"IN": 100, "US": 80}
assert len(in_all) == 2
assert list(swapped.index.names) == ["month", "country"]
assert flat.columns.tolist() == ["country", "month", "revenue"]
assert len(flat) == 4
```

#### Step-by-Step Explanation

A tuple targets a complete hierarchical key. `xs` selects across one level; `IndexSlice` handles multi-level slices. Swapping levels does not imply sorting, so `sort_index()` restores ordered hierarchy. `reset_index()` converts the hierarchy to ordinary columns.

#### Expected Result

IN/Feb = 120; Jan = IN 100/US 80; flat output = four rows.

#### Why This Works

MultiIndex adds hierarchical labels, but ordinary columns are often clearer at ETL boundaries.

#### Validation

Check values, levels, schema, and row count.

#### Common Mistake

Assuming swapped levels are automatically sorted.

#### Production Note

Use MultiIndex when hierarchy improves the workload; flatten it when interoperability is more important.

### Q45 — Replace a slow grouped `apply` and benchmark both approaches

**Difficulty:** Hard  
**Topics:** Topic 06 — `apply`, `agg`, vectorization; Topic 13 — runtime measurement

#### Problem

A developer wants revenue and maximum order value per customer and wrote a Python function through `groupby.apply`. Refactor it using named aggregation and explain what should be benchmarked.

```python
import pandas as pd

orders = pd.DataFrame(
    {
        "customer_id": ["C1", "C1", "C2", "C2"],
        "amount": [100, 200, 50, 75],
    }
)
```

#### Solution

```python
import time

slow = (
    orders.groupby("customer_id")
    .apply(lambda g: pd.Series({"revenue": g["amount"].sum(), "max_order": g["amount"].max()}),
           include_groups=False)
    .reset_index()
)

fast = (
    orders.groupby("customer_id", as_index=False)
    .agg(revenue=("amount", "sum"), max_order=("amount", "max"))
)

slow = slow.sort_values("customer_id").reset_index(drop=True)
fast = fast.sort_values("customer_id").reset_index(drop=True)
pd.testing.assert_frame_equal(slow, fast)

start = time.perf_counter()
_ = (
    orders.groupby("customer_id", as_index=False)
    .agg(revenue=("amount", "sum"), max_order=("amount", "max"))
)
elapsed_fast = time.perf_counter() - start

print({"fast_seconds": elapsed_fast})
```

#### Step-by-Step Explanation

The custom `apply` version is more general than needed. Named aggregation directly expresses the required reductions and leaves pandas in optimized grouped operations. A benchmark should use a representative dataset, repeat measurements enough to reduce noise, and compare runtime and memory under the same environment. Do not claim a speedup until measurements demonstrate it.

#### Expected Result

Both approaches produce C1 = revenue 300/max 200 and C2 = revenue 125/max 75.

#### Why This Works

Use `apply` when custom per-group logic is actually required; do not pay the generality cost for ordinary reductions.

#### Validation

`assert_frame_equal` proves the refactor preserved semantics.

#### Common Mistake

Declaring a method “faster” from intuition without benchmarking representative data.

#### Production Note

Correctness first, then benchmark the whole workload including group count, key cardinality, memory pressure, and downstream serialization.

# Part 4 — Advanced

## Q46–Q60

### Q46 — Build an end-to-end order-to-revenue pipeline

**Difficulty:** Advanced  
**Topics:** Topics 02, 03, 04, 05, 06, 07, 09, 11 — ingestion, selection, typing, cleaning, aggregation, joins, time, chaining

#### Problem

You receive this raw order data and customer dimension:

```python
import pandas as pd

raw_orders = pd.DataFrame(
    {
        "order_id": ["O1", "O2", "O2", "O3", "O4"],
        "customer_id": [" C1 ", "C2", "C2", "C3", None],
        "status": ["paid", " PAID ", "paid", "cancelled", "paid"],
        "amount": [100, "200", "220", 50, 500],
        "created_at": [
            "2026-01-01T10:00:00Z",
            "2026-01-02T10:00:00Z",
            "2026-01-03T10:00:00Z",
            "2026-01-04T10:00:00Z",
            "2026-01-05T10:00:00Z",
        ],
    }
)

customers = pd.DataFrame(
    {
        "customer_id": ["C1", "C2", "C3"],
        "country": ["IN", "US", "IN"],
    }
)
```

**Input grain:** one source row per order event; duplicate order IDs are possible source versions.  
**Gold output grain:** one row per customer-country pair.

Design a readable pipeline that:

1. normalizes customer IDs and status;
2. parses UTC timestamps;
3. keeps the latest source version per order;
4. keeps paid orders with non-null positive amounts and valid customers;
5. enriches from customers with a many-to-one contract;
6. aggregates revenue and order count by customer-country.

#### Predict Before Running

Which orders survive the business rules, and how many Gold rows should result?

#### Solution

```python
def prepare_orders(df):
    return (
        df.assign(
            customer_id=df["customer_id"].str.strip().str.upper(),
            status=df["status"].str.strip().str.lower(),
            amount=pd.to_numeric(df["amount"], errors="coerce"),
            created_at=pd.to_datetime(df["created_at"], utc=True),
        )
        .sort_values(["order_id", "created_at"])
        .drop_duplicates("order_id", keep="last")
    )

silver = (
    raw_orders
    .pipe(prepare_orders)
    .loc[lambda d: d["customer_id"].notna() & d["status"].eq("paid")]
    .loc[lambda d: d["amount"].gt(0)]
)

enriched = silver.merge(
    customers.assign(customer_id=customers["customer_id"].str.strip().str.upper()),
    on="customer_id",
    how="left",
    validate="many_to_one",
)

gold = (
    enriched
    .groupby(["customer_id", "country"], as_index=False)
    .agg(
        revenue=("amount", "sum"),
        order_count=("order_id", "nunique"),
    )
)

assert silver["order_id"].tolist() == ["O1", "O2"]
assert len(gold) == 2
assert gold["order_count"].sum() == 2
assert gold["revenue"].sum() == 320
assert gold["customer_id"].is_unique
```

#### Step-by-Step Explanation

The pipeline changes grain only at the final aggregation. The latest-record rule removes the older O2 version, so O2 uses amount 220. O3 is cancelled and O4 lacks customer identity, so neither reaches revenue. The customer dimension is validated as many-to-one before aggregation.

#### Expected Result

Two Gold rows: C1/IN revenue 100 and C2/US revenue 220.

#### Why This Works

The pipeline makes each business rule visible and places validation at the join boundary and output boundary.

#### Validation

Check order uniqueness, join cardinality, Gold key uniqueness, and revenue reconciliation.

#### Common Mistake

Aggregating before deduplication, which would double-count the older O2 version.

#### Production Note

A production implementation would also persist ingestion/quality counts and write the final dataset using a deterministic output schema.

---

### Q47 — Build a memory-aware banking transaction rollup

**Difficulty:** Advanced  
**Topics:** Topics 02, 04, 05, 06, 13 — chunked I/O, nullable dtypes, money semantics, partial aggregation, reconciliation

#### Problem

A banking transaction CSV is 12 GB and the machine has 8 GB RAM. Columns are:

```text
transaction_id string
account_id     string
status         string
amount_cents   integer-like, sometimes missing
currency       string
```

The required output is total valid posted amount by currency. Explain why integer cents are preferable here to binary floating-point for fixed-scale money and design a chunked solution.

#### Solution

```python
import pandas as pd

partials = []

for chunk in pd.read_csv(
    "transactions.csv",
    usecols=["transaction_id", "status", "amount_cents", "currency"],
    dtype={
        "transaction_id": "string",
        "status": "string",
        "amount_cents": "Int64",
        "currency": "string",
    },
    chunksize=100_000,
):
    valid = chunk.loc[
        chunk["status"].str.upper().eq("POSTED")
        & chunk["amount_cents"].notna()
        & chunk["currency"].notna()
    ]
    partials.append(
        valid.groupby("currency", as_index=False)["amount_cents"].sum()
    )

result = (
    pd.concat(partials, ignore_index=True)
    .groupby("currency", as_index=False)["amount_cents"].sum()
)
```

For a truly memory-constrained pipeline, even the `partials` list should be kept small; merge each partial into a running dictionary/DataFrame rather than retaining a large number of intermediate frames. If the same source comes from a database, the analogous chunked pattern is `pd.read_sql(query, engine, chunksize=...)`. For fixed-scale banking amounts, integer cents provide exact whole-cent accumulation; `Decimal` is also appropriate when decimal semantics must be retained and validated.

#### Step-by-Step Explanation

`usecols` prevents unused data from entering memory, `Int64` preserves integer semantics with missingness, and chunking limits input frame size. Sum is safely combinable across chunks. Fixed-scale integer cents avoid the representation ambiguity of binary floating point for many monetary calculations.

#### Expected Result

One row per currency with exact integer-cent totals. The numeric totals must be calculated from the actual file, not invented in advance.

#### Why This Works

The aggregation has an associative partial-state representation: currency → total cents.

#### Validation

For a representative subset, compare chunked totals to a full-load calculation. Reconcile input posted/non-null rows against rows accepted into the aggregation.

#### Common Mistake

Reading the entire 12 GB CSV first or using a Python float for money simply because it is convenient.

#### Production Note

A production banking pipeline should make currency semantics, source schema, missingness, and reconciliation explicit before the aggregation is published.

---

### Q48 — Design a 20 GB CSV pipeline on an 8 GB machine

**Difficulty:** Advanced  
**Topics:** Topic 02 — I/O contracts; Topic 04 — dtypes; Topic 13 — memory, peak memory, chunking, Parquet

#### Problem

You must transform a 20 GB CSV on an 8 GB RAM machine. The downstream report needs only five of the forty columns. The job also creates temporary grouped structures and must not exceed practical memory limits.

Explain the pipeline design, specifically distinguishing **final DataFrame memory** from **peak process memory**.

#### Solution

A suitable design is:

```text
20 GB CSV
   ↓
reader contract: usecols + explicit dtype + known dates
   ↓
read fixed-size chunks
   ↓
transform only required columns
   ↓
aggregate or write per chunk
   ↓
retain only sufficient state
   ↓
combine final summaries
   ↓
write deterministic Parquet output
```

The important decisions are:

- use `usecols` to avoid loading 35 unnecessary columns;
- use `nrows=` for a small schema/quality smoke test before full processing;
- set explicit dtypes so inference does not create unnecessarily large or semantically wrong objects;
- choose `chunksize` based on measured peak-memory behavior, not only the final result size;
- avoid `pd.concat(all_chunks)` when the raw input is larger than memory;
- release references to processed chunks when they are no longer needed;
- measure process peak memory separately from `memory_usage(deep=True)` on the final DataFrame;
- write partial outputs when the operation cannot be reduced to a small in-memory result;
- `iterator=True` is another iterative CSV consumption style and uses the same state/recombination reasoning as `chunksize=`;
- for database input, use `pd.read_sql(..., chunksize=...)` when a query result must also be consumed incrementally.

#### Step-by-Step Explanation

A final 200 MB DataFrame does not prove the job stayed below 200 MB while running. Temporary copies, joins, groupby structures, concatenation, retained chunks, and allocator behavior can make the process peak much higher. Conversely, a modest-looking input can still create a large intermediate result.

#### Expected Result

No numeric memory guarantee can be stated without measurement on the actual machine and representative data.

#### Why This Works

Memory design must target the highest point of the workload, not just its final artifact.

#### Validation

Measure DataFrame-level memory with `memory_usage(deep=True)` and process-level peak memory with the chosen operating-system/profiling tooling. Also measure runtime.

#### Common Mistake

Choosing a chunk size only because the final output is small.

#### Production Note

Treat peak memory as an operational capacity constraint and test with representative cardinalities, string lengths, and group counts.

---

### Q49 — Make daily partition processing idempotent and deterministic

**Difficulty:** Advanced  
**Topics:** Topics 02, 05, 11, 13 — partition processing, cleaning, `pipe`, deterministic output, idempotency

#### Problem

```python
import pandas as pd

source_df = pd.DataFrame(
    {
        "order_id": [" O1 ", "O2", "O2"],
        "status": ["paid", " PAID ", "paid"],
        "updated_at": pd.to_datetime(["2026-01-01", "2026-01-01", "2026-01-02"]),
        "amount": [100, 200, 220],
    }
)
```

A daily partition may be retried. Produce the same logical output on every run: normalized keys/status, latest order version, and unique order IDs. Explain the write behavior required to avoid duplicate publication on retry.

**Output grain:** one row per final order in the partition.

#### Solution

```python
def normalize(df):
    return df.assign(
        order_id=df["order_id"].astype("string").str.strip(),
        status=df["status"].astype("string").str.strip().str.upper(),
    )


def latest_per_order(df):
    return (
        df.sort_values(["order_id", "updated_at"])
        .drop_duplicates("order_id", keep="last")
        .reset_index(drop=True)
    )


def validate(df):
    if not df["order_id"].is_unique:
        raise ValueError("order_id must be unique")
    return df

result = source_df.pipe(normalize).pipe(latest_per_order).pipe(validate)
assert result["order_id"].tolist() == ["O1", "O2"]
assert result.loc[result["order_id"].eq("O2"), "amount"].iloc[0] == 220

rerun = source_df.copy(deep=True).pipe(normalize).pipe(latest_per_order).pipe(validate)
pd.testing.assert_frame_equal(result, rerun)
```

#### Step-by-Step Explanation

The same partition and rules must yield the same logical output. The storage stage should write to a temporary location and finalize/replace the partition using the safe write strategy supported by the target filesystem rather than blindly appending a retry.

#### Expected Result

O1 and the latest O2 version are present exactly once.

#### Why This Works

Deterministic transformation plus replacement-based publication gives a restartable boundary.

#### Validation

Check key uniqueness and repeat-run equality.

#### Common Mistake

Treating a retry as a new business partition and appending it.

#### Production Note

Idempotency is a transformation-plus-output property, not only a pandas property.

### Q50 — Combine chunked deduplication with a Parquet writer strategy

**Difficulty:** Advanced  
**Topics:** Topics 05, 07, 13 — business-key deduplication, chunk state, Parquet output, memory

#### Problem

A 30 GB daily feed contains repeated `order_id` versions and must become a Parquet dataset. You cannot retain every raw chunk in RAM. Explain what state is required for a “latest update wins” rule and how you would avoid creating an enormous number of tiny output files.

#### Solution

For each chunk:

```python
seen_latest = {}

for chunk in pd.read_csv("orders.csv", chunksize=200_000):
    chunk["updated_at"] = pd.to_datetime(chunk["updated_at"], utc=True)

    for row in chunk.itertuples(index=False):
        key = row.order_id
        previous = seen_latest.get(key)
        if previous is None or row.updated_at > previous["updated_at"]:
            seen_latest[key] = row
```

The conceptual issue is more important than this illustrative state structure: “latest wins” requires retaining enough state per business key to compare versions. A simple `seen` set is insufficient.

For output, write reasonable batches to Parquet rather than one file per tiny chunk. When a single logical Parquet file is appropriate, use a `ParquetWriter` and write batches with a consistent schema. For a partitioned dataset, choose a controlled file-sizing strategy rather than blindly mapping every input chunk to one output file.

For a CSV sink, write the header only once:

```python
for batch_number, output_chunk in enumerate(processed_chunks):
    output_chunk.to_csv(
        "orders.csv",
        mode="w" if batch_number == 0 else "a",
        header=batch_number == 0,
        index=False,
    )
```

#### Step-by-Step Explanation

Cross-chunk deduplication requires state that survives chunk boundaries. Output file layout is a separate design problem: very small Parquet files create metadata and operational overhead, while an oversized in-memory batch defeats the memory goal.

#### Expected Result

No fixed row count or file count should be invented. The output must preserve one winning record per business key according to the version rule.

#### Why This Works

Chunk size is an input-memory parameter; output file size is a storage-layout parameter. They do not have to be identical.

#### Validation

Assert final key uniqueness and reconcile accepted business keys to the source key set. Validate that all written batches share the intended schema.

#### Common Mistake

Assuming `chunk.drop_duplicates("order_id")` guarantees global uniqueness or creating one tiny Parquet file for every small chunk.

#### Production Note

Persist enough state to restart safely and use deterministic output naming/finalization so a retry does not duplicate published data.

---

### Q51 — Combine point-in-time FX, local reporting day, DST policy, and late arrivals

**Difficulty:** Advanced  
**Topics:** Topics 07 and 09 — `merge_asof`, timezone conversion, DST, late events, recomputation

#### Problem

```python
import pandas as pd

transactions = pd.DataFrame(
    {
        "txn_id": [1, 2, 3],
        "currency": ["USD", "USD", "EUR"],
        "event_time": pd.to_datetime(["2026-01-01 23:30Z", "2026-01-02 00:35Z", "2026-01-02 00:20Z"], utc=True),
        "amount": [100, 200, 50],
    }
)
rates = pd.DataFrame(
    {
        "currency": ["USD", "USD", "EUR", "EUR"],
        "rate_time": pd.to_datetime(["2026-01-01 23:00Z", "2026-01-02 00:30Z", "2026-01-02 00:00Z", "2026-01-02 00:30Z"], utc=True),
        "usd_per_unit": [1.00, 1.01, 1.10, 1.11],
    }
)
```

Assign `Asia/Kolkata` reporting dates and enrich each transaction with the most recent FX rate at or before the event. Explain what policy is required for ambiguous/nonexistent DST wall-clock times in DST-observing zones, and how late-arriving events should be handled.

#### Solution

```python
transactions = transactions.assign(
    reporting_time=transactions["event_time"].dt.tz_convert("Asia/Kolkata")
)

enriched = pd.merge_asof(
    transactions.sort_values("event_time"),
    rates.sort_values("rate_time"),
    left_on="event_time",
    right_on="rate_time",
    by="currency",
    direction="backward",
)

enriched["reporting_date"] = enriched["reporting_time"].dt.date

assert enriched["txn_id"].is_unique
assert enriched["usd_per_unit"].tolist() == [1.00, 1.10, 1.01]
```

DST-sensitive naive wall-clock input needs an explicit `ambiguous=` and `nonexistent=` policy during localization. Late events require a completeness/watermark rule or deterministic recomputation of affected reporting partitions.

#### Step-by-Step Explanation

The UTC instant is converted to business timezone before deriving the reporting date. `merge_asof(..., direction="backward")` performs point-in-time lookup; `by` prevents cross-currency matches. DST is a wall-clock interpretation problem, while late arrival is a data-completeness problem.

#### Expected Result

FX rates are 1.00, 1.10, and 1.01 for transactions 1, 3, and 2 respectively.

#### Why This Works

The join and the reporting calendar use event-time semantics consistently.

#### Validation

Check sort order, timezone, transaction uniqueness, rate coverage, and affected-partition reconciliation after late events.

#### Common Mistake

Using ingestion time as reporting date or manually adding hours to timestamps.

#### Production Note

Define event time, reporting timezone, DST policy, FX tolerance, and late-data recomputation policy explicitly.

### Q52 — Build a monthly revenue report with periods, totals, and missing-vs-zero semantics

**Difficulty:** Advanced  
**Topics:** Topics 06, 08, 09, 10 — groupby, `pivot_table`, periods, `margins`, missing-vs-zero, categorical/reporting semantics

#### Problem

```python
import pandas as pd

sales = pd.DataFrame(
    {
        "country": ["IN", "IN", "US"],
        "created_at": pd.to_datetime(["2026-01-10", "2026-03-10", "2026-01-12"]),
        "amount": [100, 120, 200],
        "status": ["paid", "paid", "paid"],
    }
)
```

Produce a country × month report for January through March 2026. Explain why an absent `IN` February observation is not automatically evidence that revenue was zero. Also create a totals view and derive a fiscal period using the taught Period tools.

#### Solution

```python
sales = sales.assign(
    month=sales["created_at"].dt.to_period("M"),
    fiscal_quarter=sales["created_at"].dt.to_period("Q"),
)

report = (
    sales.groupby(["country", "month"], as_index=False)["amount"]
    .sum()
    .pivot_table(
        index="country",
        columns="month",
        values="amount",
        aggfunc="sum",
    )
    .reindex(columns=pd.period_range("2026-01", "2026-03", freq="M"))
)

totals = sales.pivot_table(
    index="country",
    columns="month",
    values="amount",
    aggfunc="sum",
    margins=True,
    margins_name="Total",
)

assert report.loc["IN", pd.Period("2026-01", freq="M")] == 100
assert report.loc["IN", pd.Period("2026-03", freq="M")] == 120
assert pd.isna(report.loc["IN", pd.Period("2026-02", freq="M")])
assert report.loc["US", pd.Period("2026-01", freq="M")] == 200
assert totals.loc["Total", pd.Period("2026-01", freq="M")] == 300
assert sales["fiscal_quarter"].astype(str).tolist() == ["2026Q1", "2026Q1", "2026Q1"]
```

#### Step-by-Step Explanation

The missing February cell means no observed paid revenue row for IN in this input. It does not prove a business zero unless the source contract guarantees complete country-month coverage. `margins=True` adds subtotal/total calculations to the report without altering the underlying observations. Periods make the reporting month and fiscal quarter explicit.

#### Expected Result

IN has January 100, February missing, March 120. US has January 200. The total for January is 300, and every sample row falls in fiscal quarter 2026Q1 under the default quarterly Period definition.

#### Why This Works

Reshaping exposes the distinction between “no observed row” and “observed amount equals zero,” while Period values make reporting windows explicit.

#### Validation

Check specific country-month cells, total values, and fiscal period labels. Keep missing values until the business rule authorizes a zero fill.

#### Common Mistake

Calling `.fillna(0)` immediately after a pivot and silently changing unknown/no-observation into zero.

#### Production Note

For financial reporting, the missing-vs-zero rule, fiscal calendar, and totals definitions should be part of the reporting contract.

### Q53 — Normalize customer events, derive local day, and calculate a grouped rolling metric

**Difficulty:** Advanced  
**Topics:** Topics 09, 10, 06 — string normalization, UTC conversion, local calendar day, grouped rolling

#### Problem

```python
import pandas as pd

events = pd.DataFrame(
    {
        "customer": [" c1 ", "C1", "C1", "c2"],
        "event_time": pd.to_datetime(
            [
                "2026-03-01 18:00Z",
                "2026-03-01 19:00Z",
                "2026-03-01 20:00Z",
                "2026-03-01 19:00Z",
            ],
            utc=True,
        ),
        "value": [10, 20, 30, 5],
    }
)
```

Normalize customer IDs, convert to `Asia/Kolkata`, derive the local reporting date, sort by customer/time, and calculate a three-observation rolling sum per customer.

#### Solution

```python
clean = (
    events.assign(
        customer=events["customer"].str.strip().str.upper(),
        local_time=events["event_time"].dt.tz_convert("Asia/Kolkata"),
    )
    .assign(reporting_date=lambda d: d["local_time"].dt.date)
    .sort_values(["customer", "local_time"])
)

clean["rolling_3"] = (
    clean.groupby("customer")["value"]
    .rolling(3, min_periods=1)
    .sum()
    .reset_index(level=0, drop=True)
)

assert clean["customer"].tolist() == ["C1", "C1", "C1", "C2"]
assert clean.loc[clean["customer"].eq("C1"), "rolling_3"].tolist() == [10.0, 30.0, 60.0]
assert clean["reporting_date"].nunique() == 1
```

#### Step-by-Step Explanation

String normalization makes customer identity stable before grouping. Timezone conversion changes the calendar representation of each UTC instant without changing the instant. The grouped rolling operation keeps C1 and C2 sequences independent.

#### Expected Result

C1 rolling sums are 10, 30, 60; C2 has 5.

#### Why This Works

The group key and ordering key are explicit, and local reporting date is derived only after the source timestamp has a defined timezone.

#### Validation

Check normalized keys, local date count, and per-customer rolling sequence.

#### Common Mistake

Grouping before normalizing customer IDs, causing `c1` and ` C1 ` to become different groups.

#### Production Note

For an elapsed-time rolling requirement rather than an observation-count requirement, use a time-based window and confirm the intended semantics.

---

### Q54 — Build a testable `pipe` pipeline with logging and a custom validation accessor

**Difficulty:** Advanced  
**Topics:** Topic 11 — `pipe`, pure functions, `log_shape`, custom DataFrame accessor, unit/integration testing; Topic 05 — invariants

#### Problem

```python
import pandas as pd

source = pd.DataFrame({"order_id": [" O1 ", "O2"], "amount": [100, 0]})
```

Normalize `order_id`, keep positive amounts, log the DataFrame shape after major steps, and validate uniqueness through a `df.dq.require_unique("order_id")` accessor. Design the steps so they can be unit-tested independently and then integration-tested as one pipeline.

#### Solution

```python
@pd.api.extensions.register_dataframe_accessor("dq")
class DataQualityAccessor:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def require_unique(self, column):
        if not self._obj[column].is_unique:
            raise ValueError(f"{column} must be unique")
        return self._obj


def log_shape(df, name):
    print(f"{name}: rows={len(df)}, cols={len(df.columns)}")
    return df


def normalize(df):
    return df.assign(order_id=df["order_id"].astype("string").str.strip())


def positive_amounts(df):
    return df.loc[df["amount"].gt(0)].copy()

normalized = normalize(source)
assert normalized["order_id"].tolist() == ["O1", "O2"]

filtered = positive_amounts(normalized)
assert len(filtered) == 1

result = (
    source
    .pipe(log_shape, "raw")
    .pipe(normalize)
    .pipe(log_shape, "normalized")
    .pipe(positive_amounts)
    .pipe(log_shape, "positive")
    .dq.require_unique("order_id")
)

assert len(result) == 1
assert result["order_id"].tolist() == ["O1"]
pd.testing.assert_frame_equal(result, filtered)
```

#### Step-by-Step Explanation

`pipe` passes the current DataFrame through named functions. `log_shape` is a small observational side-effect that returns the same DataFrame, so it can be inserted without breaking the chain. The accessor groups a reusable data-quality check under a domain namespace. The individual functions can be unit-tested directly; the final chain can be integration-tested with an expected fixture.

#### Expected Result

The independent step tests and the whole pipeline both produce one row, `O1`, and the uniqueness invariant passes.

#### Why This Works

A pipeline is easier to debug when transformations have explicit contracts and when observability does not change data semantics.

#### Validation

Unit-test `normalize` and `positive_amounts` separately. Integration-test the complete pipeline with `assert_frame_equal` and a duplicate-key fixture that must raise `ValueError`.

#### Common Mistake

Turning an accessor into a dumping ground for file writes or unrelated business logic.

#### Production Note

Use custom accessors when they create a coherent team-wide validation API; otherwise named functions may be clearer.

### Q55 — Migrate legacy chained assignment and NumPy mutation under CoW

**Difficulty:** Advanced  
**Topics:** Topic 12 — Copy-on-Write, chained assignment, `.loc`, `.copy()`, NumPy interoperability, `SettingWithCopyWarning`/`ChainedAssignmentError`; Topic 11 — non-mutating functions

#### Problem

```python
import pandas as pd

# Imagine this code is running with pandas Copy-on-Write semantics enabled.
df = pd.DataFrame(
    {
        "amount": [50, 150, 250],
        "status": ["inactive", "active", "active"],
        "flag": [False, False, False],
    }
)
```

A legacy routine uses chained assignment such as `df["flag"][mask] = True` and then mutates a NumPy representation. Refactor it so the caller's DataFrame is not mutated and NumPy mutation has explicit ownership. Explain how modern CoW differs from historical `SettingWithCopyWarning` behavior.

#### Solution

```python
def transform(df):
    result = df.copy()
    active = result["status"].eq("active")
    result.loc[active, "flag"] = True

    arr = result.to_numpy().copy()
    arr[0, 0] = 999
    return result

original = df.copy(deep=True)
result = transform(df)
pd.testing.assert_frame_equal(df, original)
assert result["flag"].tolist() == [False, True, True]
```

The correct parent mutation pattern, when mutation is actually intended, is:

```python
df.loc[df["status"].eq("active"), "flag"] = True
```

#### Step-by-Step Explanation

`df["col"][mask] = value` is chained assignment: a selection is produced and a second indexing operation attempts to mutate that derived object. Under modern Copy-on-Write semantics, chained assignment is not the supported way to mutate the parent and can surface as a `ChainedAssignmentError`. Older pandas versions commonly surfaced `SettingWithCopyWarning` because view/copy behavior was historically ambiguous. A single `.loc` call names the parent target directly.

`.copy()` at the function boundary makes ownership explicit. `to_numpy()` exposes NumPy storage for interoperability; `.copy()` gives the NumPy array independently writable memory instead of relying on sharing behavior. The older `.values` attribute is less explicit, so `to_numpy()` is the clearer production choice.

#### Expected Result

The original input stays unchanged; the returned result has active flags set. The NumPy mutation affects only the independent array copy.

#### Why This Works

Copy-on-Write separates logical independence from physical copying, while explicit `.copy()` is still useful when a function deliberately creates an owned working object or writable NumPy buffer.

#### Validation

Use a deep snapshot plus `assert_frame_equal`. Add a regression test that checks the original DataFrame before and after the function call.

#### Common Mistake

Relying on historical warning behavior or assuming a slice is a safe writable view into the parent.

#### Production Note

Benchmark copy/CoW behavior on representative workloads; do not infer memory or speed solely from the presence of `.copy()`.

### Q56 — Enforce semantic dtypes, ordered categories, category operations, and backend alternatives

**Difficulty:** Advanced  
**Topics:** Topic 04 — nullable dtypes, `category`, category add/remove/rename/reorder, `convert_dtypes`, `dtype_backend`, UTC timestamps, memory; Topic 13 — memory measurement

#### Problem

```python
import pandas as pd

raw = pd.DataFrame(
    {
        "customer_id": ["001", "002", "003"],
        "country": ["IN", "IN", "US"],
        "is_active": [True, None, False],
        "amount_cents": [1000, None, 2500],
        "event_time": [
            "2026-01-01T00:00:00Z",
            "bad",
            "2026-01-03T00:00:00Z",
        ],
    }
)
```

Choose semantic dtypes, count timestamp failures, create an ordered country category, exercise category add/remove/rename/reorder operations, and compare NumPy-nullable and PyArrow-backed conversions.

#### Solution

```python
before = raw.memory_usage(deep=True).sum()
converted_time = pd.to_datetime(raw["event_time"], utc=True, errors="coerce")
time_failures = raw["event_time"].notna() & converted_time.isna()

typed = raw.assign(
    customer_id=raw["customer_id"].astype("string"),
    country=raw["country"].astype("category"),
    is_active=raw["is_active"].astype("boolean"),
    amount_cents=raw["amount_cents"].astype("Int64"),
    event_time=converted_time,
)
typed["country"] = typed["country"].cat.set_categories(["IN", "US"], ordered=True)

expanded = typed["country"].cat.add_categories(["GB"])
expanded = expanded.cat.rename_categories({"IN": "India", "US": "United States", "GB": "United Kingdom"})
expanded = expanded.cat.reorder_categories(
    ["United States", "India", "United Kingdom"],
    ordered=True,
)
expanded = expanded.cat.remove_unused_categories()

numpy_nullable = raw.convert_dtypes(dtype_backend="numpy_nullable")
try:
    import pyarrow as pa  # noqa: F401
except ImportError:
    arrow_backend = None
else:
    arrow_backend = raw.convert_dtypes(dtype_backend="pyarrow")
after = typed.memory_usage(deep=True).sum()

assert time_failures.tolist() == [False, True, False]
assert str(typed["event_time"].dt.tz) == "UTC"
assert str(typed["amount_cents"].dtype) == "Int64"
assert str(typed["is_active"].dtype) == "boolean"
assert typed["country"].cat.ordered is True
assert expanded.cat.categories.tolist() == ["United States", "India"]
assert "customer_id" in numpy_nullable.columns
if arrow_backend is not None:
    assert "customer_id" in arrow_backend.columns
assert after <= before
```

#### Step-by-Step Explanation

Dtypes encode business semantics: an identifier remains textual, a missing integer remains a nullable `Int64`, a Boolean with missing values uses nullable `boolean`, and timestamps are parsed as UTC. Categoricals can encode a controlled finite vocabulary and ordering. `add_categories`, `rename_categories`, `reorder_categories`, and `remove_unused_categories` are separate operations with different meanings.

`convert_dtypes` can produce NumPy-nullable or PyArrow-backed extension dtypes. The backend choice is an implementation decision that should be tested on the workload, not assumed from the function name alone.

#### Expected Result

There is exactly one invalid timestamp conversion, country is ordered, and the optimized frame has no more reported DataFrame memory than the raw frame for this sample. When PyArrow is installed, the solution also constructs an Arrow-backed conversion; otherwise it records that the optional backend dependency is unavailable. Exact memory bytes remain a measurement, not a claim about all workloads.

#### Why This Works

Semantic typing prevents downstream ambiguity and makes schemas explicit before analytics and serialization.

#### Validation

Assert failure counts, dtypes, timezone, category state, and measured memory direction.

#### Common Mistake

Changing a dtype only because it makes a calculation run, without asking whether the dtype still represents the business meaning.

#### Production Note

Validate schema dictionaries at pipeline boundaries and benchmark the chosen dtype/backend combination on representative data.

### Q57 — Diagnose join-driven revenue inflation

**Difficulty:** Advanced  
**Topics:** Topics 05, 06, 07 — duplicate reference data, group counts, cardinality, indicator, reconciliation

#### Problem

```python
import pandas as pd

orders = pd.DataFrame(
    {
        "order_id": [1, 2, 3],
        "product_id": ["P1", "P1", "P2"],
        "amount": [100, 200, 50],
    }
)
products = pd.DataFrame(
    {
        "product_id": ["P1", "P1", "P2"],
        "category": ["A", "B", "C"],
    }
)
```

The revenue report doubles after enrichment. Diagnose the cause, identify unmatched product IDs with `indicator=True`, and state the correct contract.

#### Solution

```python
before = orders["amount"].sum()
key_counts = products.groupby("product_id").size()

assert key_counts.loc["P1"] == 2

try:
    orders.merge(products, on="product_id", how="left", validate="many_to_one")
except Exception:
    contract_failed = True
else:
    contract_failed = False

assert contract_failed

enriched = orders.merge(
    products,
    on="product_id",
    how="left",
    indicator=True,
)

unmatched = enriched.loc[enriched["_merge"].eq("left_only"), orders.columns]

after = enriched["amount"].sum()
assert before == 350
assert after == 550
assert unmatched.empty
```

#### Step-by-Step Explanation

P1 appears twice in the reference table, so each P1 order matches two dimension rows. That changes 3 input rows into 5 output rows and inflates the repeated order amounts from 350 to 550. There are no unmatched product IDs in this example, so the indicator confirms that the problem is duplication rather than key loss.

#### Expected Result

The validated many-to-one contract fails. The unconstrained left merge has five rows and amount total 550.

#### Why This Works

Group counts can expose cardinality problems before a join. `indicator=True` diagnoses missing matches, while `validate` diagnoses unexpected relationships.

#### Validation

Reconcile pre- and post-join revenue and inspect right-key counts.

#### Common Mistake

Focusing only on unmatched keys and missing the more dangerous case where every key matches—but matches too many rows.

#### Production Note

For production enrichment, validate both key coverage and key uniqueness, then reconcile business measures such as revenue before and after the join.

---

### Q58 — Classify chunk operations as independent or stateful

**Difficulty:** Advanced  
**Topics:** Topic 13 — chunking/state; Topics 05, 06, 09 — deduplication, aggregation, rolling/session semantics

#### Problem

For each operation below, classify it as:

- **Safe independently per chunk** when the final result can be obtained by combining chunk-local results without carrying row-level historical context;
- **Requires additional state** when previous chunks can affect the answer for later chunks.

Operations:

1. global sum;
2. count and sum for deriving a global mean;
3. `drop_duplicates("order_id")` with first occurrence globally;
4. customer running `cumsum` by event time;
5. three-observation rolling sum by customer;
6. independent row normalization with `.str.strip().str.upper()`;
7. group-level total revenue by country;
8. session detection after 30 minutes of inactivity.

#### Solution

| Operation | Classification | Required reasoning |
|---|---|---|
| Global sum | Safe independently | Partial sums combine exactly |
| Count + sum for mean | Safe independently | Mean can be reconstructed as total/count |
| Global first dedup | Requires state | Earlier chunks determine whether a key was already seen |
| Group running `cumsum` | Requires state | Need prior running total per group |
| Three-observation rolling sum | Requires state | Need prior observations crossing the boundary |
| Row string normalization | Safe independently | Each row can be transformed without history |
| Country total revenue | Safe independently | Partial country sums combine exactly |
| Session detection | Requires state | Need previous event time per entity |

#### Step-by-Step Explanation

The key question is whether the answer for a row or aggregate in chunk N depends on information from chunks 1…N-1. Associative reductions such as sum, and sufficient-statistic combinations such as sum+count, can be aggregated independently. Ordering and history-dependent logic require carried state.

#### Expected Result

Four operations are safely chunk-independent as stated; four require additional state.

#### Why This Works

Chunking is a computation strategy, not a guarantee that every pandas method becomes independent.

#### Validation

For any proposed chunked implementation, compare it with a full-load reference on a manageable sample and assert equivalence.

#### Common Mistake

Calling every groupby operation “streamable” without asking what state is necessary to preserve exact semantics.

#### Production Note

Document the state model, state key, state lifetime, and restart behavior for stateful chunk processors.

---

### Q59 — Prove full-load and chunked equivalence while measuring runtime and memory

**Difficulty:** Advanced  
**Topics:** Topics 02, 06, 13 — full-load vs chunked, correctness testing, benchmark methodology, memory

#### Problem

A manageable CSV sample contains `country`, `amount`, and `order_id`. Build a full-load result and a chunked result that compute total revenue and order count by country. Then benchmark both methods without inventing performance numbers.

#### Solution

```python
from io import StringIO
import time
import pandas as pd

csv_text = (
    "order_id,country,amount\n"
    "1,IN,100\n"
    "2,IN,200\n"
    "3,US,50\n"
    "4,US,75\n"
)

full_df = pd.read_csv(StringIO(csv_text))
full = (
    full_df.groupby("country", as_index=False)
    .agg(revenue=("amount", "sum"), order_count=("order_id", "count"))
    .sort_values("country")
    .reset_index(drop=True)
)

partials = []
for chunk in pd.read_csv(StringIO(csv_text), chunksize=2):
    partials.append(
        chunk.groupby("country", as_index=False)
        .agg(revenue=("amount", "sum"), order_count=("order_id", "count"))
    )

chunked = (
    pd.concat(partials, ignore_index=True)
    .groupby("country", as_index=False)
    .sum()
    .sort_values("country")
    .reset_index(drop=True)
)

pd.testing.assert_frame_equal(full, chunked)

start = time.perf_counter()
_ = full_df.groupby("country")["amount"].sum()
full_seconds = time.perf_counter() - start

start = time.perf_counter()
for chunk in pd.read_csv(StringIO(csv_text), chunksize=2):
    _ = chunk.groupby("country")["amount"].sum()
chunked_seconds = time.perf_counter() - start

print({"full_seconds": full_seconds, "chunked_seconds": chunked_seconds})
```

For a production benchmark, also measure DataFrame memory and process peak memory on a representative dataset, and repeat the comparison under the same environment.

#### Step-by-Step Explanation

The equivalence test is the first requirement: chunking must not change results. Only after semantic equivalence is established should runtime and memory be compared. Small synthetic data can demonstrate the method, but it should not be used to claim production performance.

#### Expected Result

The two result DataFrames are exactly equal for the supplied sample. Benchmark timings are produced only when the learner runs the code.

#### Why This Works

Performance engineering without correctness equivalence can optimize the wrong computation.

#### Validation

`assert_frame_equal` checks the complete grouped result; benchmark output is explicitly machine-dependent.

#### Common Mistake

Reporting a percentage speedup from an unmeasured or non-representative example.

#### Production Note

Benchmark representative row counts, group cardinality, string sizes, I/O format, CPU/storage environment, and peak memory—not only a tiny in-memory toy frame.

---

### Q60 — Choose the right pandas boundary for a production workload

**Difficulty:** Advanced  
**Topics:** Topic 13 — engine-selection concepts; Topics 01–12 — grain, schema, selection, cleaning, joins, time, chaining, CoW, correctness

#### Problem

You are asked to build a production job with these characteristics:

```text
Input: 80 GB Parquet dataset
Machine: 16 GB RAM
Work: filter columns, join two large datasets, time-window metrics,
      repeated transformations, and a final report
Output: partitioned analytical files
```

The team says “use pandas because the company knows pandas.” Use the Module 2.3 decision framework to explain how you would decide whether pandas remains appropriate. You may mention Polars, DuckDB, Dask, or Spark only conceptually; do not implement them.

#### Solution

Start with the workload, not the library name.

```text
1. Can the required working set fit comfortably in pandas memory?
2. Can column projection and filters reduce the amount read enough?
3. Can the workload be solved chunk-wise with bounded state?
4. Do joins create large intermediates or row explosions?
5. Are time windows local/stateful in ways that make chunking complex?
6. Are there repeated scans or operations that benefit from a different execution engine?
7. What are the correctness and validation requirements?
```

Pandas remains a reasonable choice for small-to-medium working sets and controlled chunked workloads where explicit memory/state design is sufficient. For a dataset far larger than RAM with substantial joins and repeated analytics, the module's conceptual guidance says to recognize the boundary and consider another engine rather than forcing everything into one in-memory DataFrame.

A conceptual comparison is:

| Situation | Consideration |
|---|---|
| Controlled local DataFrame work | pandas is natural |
| Large columnar analytical scans | DuckDB/Polars may be worth evaluating |
| Larger-than-memory DataFrame-style processing | Dask may be evaluated |
| Distributed cluster-scale processing | Spark may be evaluated |
| Any choice | Measure correctness, runtime, memory, operational fit |

#### Step-by-Step Explanation

The choice is not “pandas is bad at 80 GB.” The question is whether the actual working set, intermediate state, join behavior, and operational constraints can be handled predictably. The module also teaches that moving engines does not remove the need for pandas-style reasoning about schema, grain, joins, time semantics, and validation.

#### Expected Result

A defensible design decision should document the measured working-set size, expected intermediate growth, memory/CPU constraints, state requirements, correctness checks, and operational requirements before selecting an engine.

#### Why This Works

Engine selection is a Data Engineering architecture decision. The important skill is recognizing when a pandas-based approach is becoming unpredictable or operationally expensive and choosing based on workload characteristics.

#### Validation

A production decision document should include explicit invariants such as:

```text
input key uniqueness where required
row-count reconciliation
revenue reconciliation
expected output partitions
full-load vs sampled/chunked equivalence
no unexpected nulls
no join-cardinality violations
```

#### Common Mistake

Selecting a tool solely because the team already knows its API, without analyzing memory, intermediate results, join cardinality, and execution scale.

#### Production Note

Even when another engine is selected, pandas remains valuable for small fixtures, reconciliation, data-quality investigations, contract tests, and local samples—the same reasoning skills transfer.

# Final Coverage Matrix

| Topic | Questions |
|---|---|
| Topic 01 — Series, DataFrame, and Index | Q01, Q02, Q03, Q16, Q44, Q46, Q60 |
| Topic 02 — Reading and writing data sources | Q06, Q17, Q43, Q46, Q47, Q48, Q49, Q59 |
| Topic 03 — Selection with `loc`, `iloc`, and `query` | Q03, Q04, Q05, Q18, Q31, Q46 |
| Topic 04 — dtypes, nullable types, and categoricals | Q07, Q19, Q30, Q31, Q33, Q42, Q47, Q56, Q60 |
| Topic 05 — Cleaning missing values, duplicates, and outliers | Q08, Q20, Q31, Q37, Q40, Q46, Q49, Q50, Q57 |
| Topic 06 — `groupby`: aggregate, transform, and apply | Q09, Q21, Q22, Q32, Q35, Q37, Q39, Q45, Q46, Q47, Q52, Q53, Q57, Q58, Q59 |
| Topic 07 — merge, join, concat, and join cardinality | Q10, Q23, Q24, Q30, Q33, Q34, Q43, Q46, Q51, Q57, Q60 |
| Topic 08 — Reshaping | Q11, Q25, Q26, Q27, Q36, Q52 |
| Topic 09 — Time series | Q12, Q28, Q29, Q34, Q35, Q41, Q46, Q51, Q52, Q53, Q58 |
| Topic 10 — String and datetime accessors | Q12, Q13, Q28, Q30, Q46, Q51, Q52, Q53, Q56 |
| Topic 11 — Method chaining and `pipe` | Q14, Q37, Q46, Q49, Q54, Q55 |
| Topic 12 — Copy-on-Write and chained assignment | Q38, Q43, Q55, Q60 |
| Topic 13 — Chunked processing and memory reduction | Q15, Q39, Q40, Q41, Q42, Q43, Q47, Q48, Q49, Q50, Q58, Q59, Q60 |

## Final Completion Checklist

### Count

- [x] 15 Basic questions: Q01–Q15
- [x] 15 Moderate questions: Q16–Q30
- [x] 15 Hard questions: Q31–Q45
- [x] 15 Advanced questions: Q46–Q60
- [x] Exactly 60 numbered questions

### Structure

- [x] Every question presents the Problem before the Solution.
- [x] Solutions are immediately attached to their questions.
- [x] There is no separate answer key.
- [x] Numbering is continuous from Q01 to Q60.

### Engineering coverage

- [x] Row-count prediction and validation
- [x] Output grain and schema reasoning
- [x] Index and alignment reasoning
- [x] Nullable dtype and semantic schema reasoning
- [x] Cleaning decisions and reconciliation
- [x] Groupby `agg` / `transform` / `filter` / `apply` choices
- [x] Join cardinality, anti/semi joins, and `merge_asof`
- [x] Reshaping and round-trip testing
- [x] Timezone, rolling, periods, and late-event semantics
- [x] String normalization, regex, and datetime parsing
- [x] Method chaining, `pipe`, validation, and testing
- [x] Copy-on-Write and input ownership
- [x] Chunking, partial aggregation, cross-chunk state, memory, and idempotency
- [x] Production decision-making and engine-selection concepts

### Required tricky cases

- [x] `loc` inclusive versus `iloc` exclusive
- [x] Boolean `&` / `|` / `~` semantics
- [x] `count` versus `size`
- [x] Duplicate join keys and revenue inflation
- [x] `validate="many_to_one"`
- [x] `indicator=True`
- [x] `pivot` duplicate-key failure versus `pivot_table`
- [x] Missing versus zero after reshaping
- [x] `rolling(7)` versus `rolling("7D")`
- [x] Timezone localization versus conversion
- [x] Chained assignment under CoW
- [x] Average-of-averages chunking error
- [x] Cross-chunk deduplication
- [x] Cross-chunk rolling/session state
- [x] Peak memory versus final DataFrame memory
