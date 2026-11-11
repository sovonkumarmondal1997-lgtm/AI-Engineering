# Topic 01 — Testing Transformations with Fixture DataFrames

> **Stage 2 — Python for Data Engineering**  
> **Module 2.19 — Testing Data Pipelines**  
> **Level:** Beginner → Intermediate → Advanced → Production  
> **Primary tools:** Python 3.12+, pytest, pandas, Polars, DuckDB, PySpark, time-machine, pytest-cov

## 1. Introduction

A data transformation takes data in one shape and produces data in another shape.

A typical pipeline might look like:

```text
raw orders
    ↓
clean orders
    ↓
deduplicate
    ↓
calculate revenue
    ↓
gold DataFrame
```

A transformation can succeed technically while being wrong logically. For example, a duplicate order may be counted twice, a timestamp may be interpreted in the wrong timezone, or a null may be treated as zero. The pipeline can finish with exit code 0 while producing believable but incorrect revenue.

A unit test for a DataFrame transformation protects against that class of failure.

### Tests vs data-quality checks

This topic is about **testing transformation code with controlled inputs**. Production data-quality checks have a different job: they inspect real data after the pipeline is running. A mature platform needs both.

```text
Unit test:
known input → transformation → expected output

Data-quality check:
real production data → quality rule → alert / quarantine / remediation
```

### Why data transformation testing is different

Traditional application tests often ask whether a function returned the right scalar or object. Data-engineering tests must also reason about:

- rows and keys
- schemas and dtypes
- null semantics
- duplicates
- ordering
- timestamps and time zones
- aggregation correctness
- late records
- empty datasets
- business-rule boundaries

The goal is not maximum test volume. The goal is **high confidence that important data behavior is correct**.

---

# 2. What Are We Testing?

The central unit is:

```text
DataFrame → Transformation → DataFrame
```

For example:

```python
from __future__ import annotations

import pandas as pd


def add_total_amount(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["total_amount"] = result["quantity"] * result["unit_price"]
    return result
```

The test follows Arrange–Act–Assert:

```text
Arrange
  ↓
Act
  ↓
Assert
```

```python
import pandas as pd
from pandas.testing import assert_frame_equal


def test_add_total_amount() -> None:
    orders = pd.DataFrame(
        {
            "order_id": ["O-001", "O-002"],
            "quantity": [2, 3],
            "unit_price": [10.0, 5.0],
        }
    )

    expected = pd.DataFrame(
        {
            "order_id": ["O-001", "O-002"],
            "quantity": [2, 3],
            "unit_price": [10.0, 5.0],
            "total_amount": [20.0, 15.0],
        }
    )

    actual = add_total_amount(orders)

    assert_frame_equal(actual, expected)
```

A good unit test makes the business rule obvious without requiring the reader to understand the entire pipeline.

---

# 3. Pure DataFrame-to-DataFrame Transformations

A pure transformation is easiest to test when:

- the input is explicit
- the output depends only on the input and explicit arguments
- there is no network call
- there is no database dependency
- there is no filesystem dependency
- there is no cloud dependency
- there is no hidden mutable state

For example:

```python
def normalize_customer_names(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["customer_name"] = (
        result["customer_name"]
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
    )
    return result
```

The transformation is deterministic:

```text
same input + same arguments → same output
```

That makes it ideal for a fast unit test.

### Production design principle

Keep I/O at the edges of the pipeline.

Prefer:

```text
database → extraction → DataFrame
                         ↓
                    pure transforms
                         ↓
                    DataFrame → database
```

rather than:

```text
transformation function
    ├── reads database
    ├── calls API
    ├── transforms rows
    └── writes database
```

The first design lets the business logic be tested with tiny fixtures.

---

# 4. First DataFrame Unit Test

Start small.

## Production code

```python
def add_total_amount(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["total_amount"] = result["quantity"] * result["unit_price"]
    return result
```

## Test

```python
def test_add_total_amount() -> None:
    orders = pd.DataFrame(
        {
            "order_id": ["O-001"],
            "quantity": [3],
            "unit_price": [100.0],
        }
    )

    actual = add_total_amount(orders)

    expected = pd.DataFrame(
        {
            "order_id": ["O-001"],
            "quantity": [3],
            "unit_price": [100.0],
            "total_amount": [300.0],
        }
    )

    assert_frame_equal(actual, expected)
```

Run:

```bash
uv run pytest -q
```

A passing test proves the selected behavior for the selected input.

A failing test might show:

```text
DataFrame.iloc[:, 3] values are different
[left]:  [300.0]
[right]: [250.0]
```

The important point is that the test tells you **what data behavior changed**, not merely that a line of code was executed.

---

# 5. Minimal Fixture DataFrames

A good fixture contains only the rows and columns necessary to prove the behavior being tested.

### Weak fixture

```text
50 columns
10,000 rows
customer demographics
marketing attributes
unused metadata
unrelated timestamps
```

### Strong fixture

```text
order_id
quantity
unit_price
```

Minimal fixtures are:

- easier to understand
- faster
- easier to debug
- less brittle
- more targeted
- clearer when they fail

For example, to test duplicate handling:

```python
orders = pd.DataFrame(
    {
        "order_id": ["O-001", "O-001", "O-002"],
        "updated_at": pd.to_datetime(
            ["2026-01-01 10:00", "2026-01-01 11:00", "2026-01-01 12:00"],
            utc=True,
        ),
        "amount": [100, 120, 50],
    }
)
```

Do not add twenty unrelated columns merely because the production table has them.

### Rule

> The fixture should expose the behavior under test, not reproduce the production table.

---

# 6. Explicit Schemas

Tests should make types intentional.

Schema differences can hide bugs:

```text
int vs float
string vs categorical
timestamp vs string
Decimal vs float
nullable integer vs ordinary integer
```

## pandas

```python
orders = pd.DataFrame(
    {
        "order_id": pd.Series(["O-001"], dtype="string"),
        "quantity": pd.Series([2], dtype="Int64"),
        "unit_price": pd.Series([100.0], dtype="float64"),
    }
)
```

## Polars

```python
import polars as pl

orders = pl.DataFrame(
    {
        "order_id": ["O-001"],
        "quantity": [2],
        "unit_price": [100.0],
    },
    schema={
        "order_id": pl.String,
        "quantity": pl.Int64,
        "unit_price": pl.Float64,
    },
)
```

## Spark

```python
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

schema = StructType(
    [
        StructField("order_id", StringType(), False),
        StructField("quantity", IntegerType(), False),
        StructField("unit_price", DoubleType(), False),
    ]
)
```

The principle is the same even though each engine expresses schemas differently.

### Why explicit schemas matter

If a fixture silently changes from integer to floating point, a test can pass for the wrong reason. Explicit schemas make assumptions visible and failures reproducible.

Money deserves particular care. Prefer `Decimal` or integer cents for exact financial rules instead of relying on binary floating-point arithmetic.

---

# 7. One Behavior Per Test

Avoid:

```python
def test_everything():
    # cleaning
    # deduplication
    # revenue
    # status mapping
    # timestamps
    # ten unrelated assertions
    ...
```

Prefer focused tests:

```python
def test_duplicate_order_ids_keep_latest_record():
    ...


def test_calculates_total_amount():
    ...


def test_normalizes_customer_name():
    ...
```

One behavior per test does not mean exactly one assertion. It means the test has one clear business purpose.

A focused failure is actionable:

```text
test_duplicate_order_ids_keep_latest_record FAILED
```

A giant test is not:

```text
test_pipeline FAILED
```

---

# 8. Rule-Named Tests

Name tests after the behavior they protect.

Good:

```python
def test_duplicate_order_ids_keep_latest_record():
    ...
```

```python
def test_cancelled_orders_are_not_billable():
    ...
```

```python
def test_late_records_are_included_when_their_event_date_matches():
    ...
```

Weak:

```python
def test_process_orders_v2():
    ...
```

```python
def test_dataframe():
    ...
```

A rule-named test is executable documentation.

A useful naming pattern is:

```text
test_<business_condition>_<expected_behavior>
```

For example:

```python
def test_same_timestamp_uses_sequence_as_tiebreaker():
    ...
```

---

# 9. DataFrame Builders and Factories

As a test suite grows, repeating DataFrame construction becomes noisy.

Use builders when many tests need similar valid records.

```python
from typing import Any


def make_order(**overrides: Any) -> dict[str, Any]:
    order = {
        "order_id": "O-001",
        "quantity": 1,
        "unit_price": 100.0,
        "status": "completed",
    }
    order.update(overrides)
    return order


def orders_frame(*orders: dict[str, Any]) -> pd.DataFrame:
    rows = list(orders) or [make_order()]
    return pd.DataFrame(rows)
```

A test can now say:

```python
orders = orders_frame(
    make_order(quantity=3, unit_price=100.0)
)
```

The test communicates the important difference instead of repeating irrelevant defaults.

---

# 10. Sensible Defaults

A builder should make a valid, unsurprising record.

```python
def make_order(
    order_id: str = "O-001",
    quantity: int = 1,
    unit_price: float = 100.0,
    status: str = "completed",
) -> dict[str, object]:
    return {
        "order_id": order_id,
        "quantity": quantity,
        "unit_price": unit_price,
        "status": status,
    }
```

Good defaults:

- represent a normal valid case
- are stable
- are easy to override
- do not hide important assumptions

Bad builders create magical behavior:

```python
def make_order(**kwargs):
    # 40 hidden defaults, implicit timestamps,
    # random identifiers, global state
    ...
```

Builders should reduce repetition, not conceal the test's meaning.

---

# 11. pytest Fixtures

A pytest fixture can provide reusable test setup.

```python
import pytest


@pytest.fixture
def orders_df() -> pd.DataFrame:
    return orders_frame(
        make_order(order_id="O-001", quantity=2),
        make_order(order_id="O-002", quantity=3),
    )
```

Use it:

```python
def test_add_total_amount(orders_df: pd.DataFrame) -> None:
    actual = add_total_amount(orders_df)

    assert actual["total_amount"].tolist() == [200.0, 300.0]
```

Fixtures are useful when:

- setup is reused
- setup has a clear name
- setup is stable
- fixture scope is appropriate

Do not turn every tiny DataFrame into a fixture. Inline data is often clearer when it is used once.

---

# 12. Table-Driven / Parametrized Tests

Use parametrization when one behavior has several compact cases.

```python
@pytest.mark.parametrize(
    ("status", "expected"),
    [
        ("completed", True),
        ("cancelled", False),
        ("pending", False),
    ],
)
def test_order_status_is_billable(
    status: str,
    expected: bool,
) -> None:
    assert is_billable(status) is expected
```

For DataFrame transformations:

```python
@pytest.mark.parametrize(
    ("raw_name", "expected"),
    [
        (" Alice ", "Alice"),
        ("Alice  Smith", "Alice Smith"),
        ("  José  García ", "José García"),
    ],
)
def test_customer_name_normalization(
    raw_name: str,
    expected: str,
) -> None:
    df = pd.DataFrame({"customer_name": [raw_name]})

    actual = normalize_customer_names(df)

    assert actual.loc[0, "customer_name"] == expected
```

Parametrization:

- reduces duplicate test code
- makes cases explicit
- is useful for boundaries
- should not become so large that the test becomes unreadable

Prefer a few meaningful cases over dozens of nearly identical rows.

---

# 13. Edge-Case Testing

Data bugs often live at boundaries.

For each edge case:

1. identify the failure mode
2. create the smallest fixture
3. write the expected behavior
4. make the test fail against a broken implementation
5. explain why the case matters

## 13.1 Empty input

Bug:

```text
aggregation assumes at least one row
```

Test:

```python
def test_empty_orders_produce_empty_result() -> None:
    orders = pd.DataFrame(
        {
            "order_id": pd.Series(dtype="string"),
            "quantity": pd.Series(dtype="Int64"),
            "unit_price": pd.Series(dtype="float64"),
        }
    )

    actual = add_total_amount(orders)

    assert actual.empty
    assert list(actual.columns) == [
        "order_id",
        "quantity",
        "unit_price",
        "total_amount",
    ]
```

## 13.2 One row

A one-row fixture catches accidental assumptions about multiple records.

```python
def test_single_order_is_transformed() -> None:
    orders = orders_frame(make_order(quantity=2, unit_price=25.0))

    actual = add_total_amount(orders)

    assert actual.loc[0, "total_amount"] == 50.0
```

## 13.3 All-null values

Null behavior must be intentional.

```python
def test_null_quantity_does_not_become_a_fake_sale() -> None:
    orders = pd.DataFrame(
        {
            "order_id": pd.Series(["O-001"], dtype="string"),
            "quantity": pd.Series([pd.NA], dtype="Int64"),
            "unit_price": pd.Series([100.0], dtype="float64"),
        }
    )

    actual = add_total_amount(orders)

    assert pd.isna(actual.loc[0, "total_amount"])
```

The correct expectation depends on the business rule. The important point is that the rule is explicit.

## 13.4 Duplicate records

Typical production bug:

```text
duplicate event/order → duplicate revenue
```

Test the exact uniqueness rule:

```python
def test_duplicate_order_ids_keep_latest_record() -> None:
    orders = pd.DataFrame(
        {
            "order_id": ["O-001", "O-001"],
            "updated_at": pd.to_datetime(
                ["2026-01-01 10:00", "2026-01-01 11:00"],
                utc=True,
            ),
            "amount": [100.0, 120.0],
        }
    )

    actual = keep_latest_order(orders)

    assert actual["order_id"].tolist() == ["O-001"]
    assert actual["amount"].tolist() == [120.0]
```

## 13.5 Ties

What if two records have the same timestamp?

```text
same key
same timestamp
different sequence
```

The test should define the deterministic tiebreaker:

```python
def test_same_timestamp_uses_sequence_as_tiebreaker() -> None:
    orders = pd.DataFrame(
        {
            "order_id": ["O-001", "O-001"],
            "updated_at": pd.to_datetime(
                ["2026-01-01 10:00", "2026-01-01 10:00"],
                utc=True,
            ),
            "sequence": [1, 2],
            "amount": [100.0, 125.0],
        }
    )

    actual = keep_latest_order(orders)

    assert actual["amount"].tolist() == [125.0]
```

## 13.6 Unicode

Names and identifiers are not ASCII-only.

```python
@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("José", "José"),
        ("李明", "李明"),
        ("नमस्ते", "नमस्ते"),
    ],
)
def test_unicode_customer_names_are_preserved(raw: str, expected: str) -> None:
    df = pd.DataFrame({"customer_name": [raw]})

    actual = normalize_customer_names(df)

    assert actual.loc[0, "customer_name"] == expected
```

## 13.7 Whitespace

```python
@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (" Alice", "Alice"),
        ("Alice ", "Alice"),
        ("  Alice  ", "Alice"),
    ],
)
def test_customer_name_whitespace_is_normalized(raw: str, expected: str) -> None:
    ...
```

## 13.8 Numeric extremes

Test:

```text
0
-1
very large values
very small values
```

Do not automatically reject negative values; first determine whether negative values are valid business data.

## 13.9 Time zones

A timestamp represents an instant, not merely a string.

Include fixtures using:

```text
UTC
UTC+05:30
UTC-05:00
```

The transformation should define whether comparisons happen in UTC or another business timezone.

## 13.10 DST boundaries

Daylight-saving transitions can produce:

- missing local times
- repeated local times
- unexpected date boundaries

Even if your primary production timezone does not observe DST, upstream data may.

## 13.11 Month-end

Test:

```text
January 31
February 28
February 29
April 30
```

Month arithmetic frequently contains boundary bugs.

## 13.12 Leap days

```python
def test_leap_day_is_handled() -> None:
    ...
```

A date-based transformation should not silently assume every February has 28 days.

## 13.13 Late-arriving records

A record can arrive today while belonging to yesterday's business date.

```text
event_date = 2026-01-14
arrival_date = 2026-01-15
```

Test whether the transformation correctly assigns the record to the business date.

---

# 14. Inline DataFrames vs External Fixture Files

There is no universal best fixture format.

## Inline fixtures

```python
df = pd.DataFrame(
    {
        "order_id": ["O-001"],
        "amount": [100.0],
    }
)
```

Best when:

- data is tiny
- the behavior is obvious from the values
- readability matters most

## CSV

Useful when:

- the fixture resembles a simple tabular source
- non-Python users may review it
- preserving textual representation matters

Trade-off: schema is less explicit unless validated.

## JSON

Useful for:

- nested structures
- API-like records

## Parquet

Useful when:

- dtype fidelity matters
- the fixture is larger
- you need realistic columnar data

### Decision framework

```text
Tiny + behavior-focused
    → inline

Readable tabular fixture
    → CSV

Nested/API-like fixture
    → JSON

Typed/columnar/larger fixture
    → Parquet
```

Keep fixtures version-controlled and intentionally small.

---

# 15. Testing Time-Dependent Transformations

This is dangerous:

```python
from datetime import datetime


def mark_recent_orders(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    today = datetime.now()
    ...
```

The test depends on the clock.

A better interface is:

```python
from datetime import date


def mark_recent_orders(
    df: pd.DataFrame,
    run_date: date,
) -> pd.DataFrame:
    result = df.copy()
    result["is_recent"] = result["order_date"] >= pd.Timestamp(run_date)
    return result
```

Test:

```python
def test_mark_recent_orders_uses_supplied_run_date() -> None:
    orders = pd.DataFrame(
        {
            "order_id": ["O-001", "O-002"],
            "order_date": pd.to_datetime(
                ["2026-01-14", "2026-01-15"]
            ),
        }
    )

    actual = mark_recent_orders(
        orders,
        run_date=date(2026, 1, 15),
    )

    assert actual["is_recent"].tolist() == [False, True]
```

Dependency injection is generally preferable because the test controls the dependency explicitly.

---

# 16. Using `time-machine`

Sometimes legacy or framework code still reads the current clock.

Install:

```bash
uv add --dev time-machine
```

Freeze time:

```python
import time_machine


@time_machine.travel("2026-01-15")
def test_month_end_logic() -> None:
    ...
```

For example:

```python
from datetime import datetime

import pandas as pd
import time_machine


def mark_current_month(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    today = datetime.now()
    result["is_current_month"] = (
        result["event_at"].dt.year == today.year
    ) & (
        result["event_at"].dt.month == today.month
    )
    return result


@time_machine.travel("2026-01-31 12:00:00")
def test_month_end_is_deterministic() -> None:
    df = pd.DataFrame(
        {
            "event_at": pd.to_datetime(
                ["2026-01-30", "2026-02-01"]
            )
        }
    )

    actual = mark_current_month(df)

    assert actual["is_current_month"].tolist() == [True, False]
```

Use time freezing when it is the appropriate seam. For new code, explicit `run_date` or clock dependency injection is usually clearer.

---

# 17. Testing Multi-Step Transformations

Consider:

```text
raw
 ↓
clean
 ↓
deduplicated
 ↓
enriched
 ↓
aggregated
```

Test each pure step independently:

```python
clean = clean_orders(raw)
deduped = deduplicate_orders(clean)
enriched = enrich_orders(deduped, customers)
daily = aggregate_daily_revenue(enriched)
```

Each function should have focused unit tests.

Then add a small number of composition tests for important contracts:

```python
def test_clean_then_deduplicate_preserves_one_row_per_order() -> None:
    raw = ...

    clean = clean_orders(raw)
    deduped = deduplicate_orders(clean)

    assert deduped["order_id"].is_unique
```

Avoid turning every unit test into a full pipeline test. Full-system protection belongs to later layers of the module.

The right boundary is usually:

```text
many small tests of individual rules
+
a smaller number of meaningful composition tests
```

---

# 18. Cross-Engine Testing

Data platforms commonly use more than one execution engine.

The **business rule** should remain stable even when implementation changes.

Example rule:

> Revenue equals quantity multiplied by unit price for valid orders.

## pandas

```python
def revenue_pandas(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["revenue"] = result["quantity"] * result["unit_price"]
    return result
```

## Polars

```python
import polars as pl


def revenue_polars(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        (pl.col("quantity") * pl.col("unit_price")).alias("revenue")
    )
```

## DuckDB

```python
import duckdb


def revenue_duckdb(df: pd.DataFrame) -> pd.DataFrame:
    return duckdb.sql(
        """
        SELECT
            order_id,
            quantity,
            unit_price,
            quantity * unit_price AS revenue
        FROM df
        """
    ).df()
```

## Spark

```python
from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def revenue_spark(df: DataFrame) -> DataFrame:
    return df.withColumn(
        "revenue",
        F.col("quantity") * F.col("unit_price"),
    )
```

These engines are not identical.

Differences include:

- schema behavior
- null semantics
- numeric types
- ordering
- lazy vs eager execution
- timestamp representation

Therefore:

```text
Normalize what represents the business contract.
Do not erase meaningful engine-specific behavior.
```

A cross-engine test should compare the agreed business result while keeping engine-specific tests for engine-specific behavior.

---

# 19. Fixture Scope and Fixture Cost

pytest fixture scope affects performance and isolation.

Common scopes:

```text
function
module
session
```

### Function scope

Best default for mutable DataFrames:

```python
@pytest.fixture
def orders_df() -> pd.DataFrame:
    return ...
```

Each test receives fresh state.

### Module scope

Useful for expensive setup shared within one module when tests cannot mutate the shared object.

### Session scope

Useful for expensive immutable resources.

A classic example is a Spark session:

```python
@pytest.fixture(scope="session")
def spark():
    ...
```

The same principle applies to expensive connections, but shared mutable state creates contamination risk.

### Cost model

```text
small DataFrame
    → function scope

expensive immutable local engine
    → session scope

mutable test data
    → fresh per test
```

Do not optimize fixture scope before measuring. A fast contaminated test suite is still a bad test suite.

---

# 20. Testing Branches and Business Rules

Suppose:

```python
def is_billable(status: str) -> bool:
    if status == "completed":
        return True
    elif status == "cancelled":
        return False
    else:
        return False
```

Tests should cover:

```text
normal path
alternative path
unexpected/other path
boundary conditions where relevant
```

```python
@pytest.mark.parametrize(
    ("status", "expected"),
    [
        ("completed", True),
        ("cancelled", False),
        ("pending", False),
    ],
)
def test_is_billable(status: str, expected: bool) -> None:
    assert is_billable(status) is expected
```

Branch coverage asks whether execution paths were exercised.

Behavioral coverage asks whether the important data situations and business rules were exercised.

Both matter.

---

# 21. Edge-Case Coverage vs Code Coverage

Code coverage is useful but incomplete.

A suite can achieve:

```text
100% line coverage
```

and still miss:

```text
duplicate key
timezone boundary
null semantics
tie-breaking rule
late-arriving record
```

Example:

```python
def revenue(df: pd.DataFrame) -> pd.Series:
    return df["quantity"] * df["price"]
```

A test with one normal row can execute every line while never checking:

- null quantity
- negative quantity
- duplicate orders
- extreme values
- business-day boundaries

Therefore track two dimensions:

```text
Code coverage
    +
Data edge-case / behavioral coverage
```

Coverage is evidence about the suite, not proof that the suite is good.

---

# 22. Deliberate Bug Injection

A powerful learning technique is to break the transformation intentionally.

## Bug 1 — incorrect duplicate handling

Correct rule:

```text
keep latest record per order_id
```

Broken implementation might sort in ascending order and keep the first record.

The regression test should fail.

## Bug 2 — timezone conversion error

Break a UTC conversion by treating a timestamp as a naive local timestamp.

A timezone fixture should catch it.

## Bug 3 — incorrect null handling

Replace null-aware logic with a fill of zero.

The test should prove that null and zero are not equivalent unless the business rule says they are.

## Bug 4 — wrong aggregation

Change:

```python
.groupby("order_id")["revenue"].sum()
```

to an incorrect aggregation such as `mean()`.

The expected totals should fail.

## Bug 5 — off-by-one date filter

Break:

```python
event_date <= end_date
```

into:

```python
event_date < end_date
```

A fixture containing the exact boundary date should catch it.

## Bug 6 — incorrect late-record handling

Move a late-arriving record to the arrival date instead of the event/business date.

A test should fail.

### Failure-first workflow

```text
Write correct test
      ↓
Confirm green
      ↓
Break implementation
      ↓
Run test
      ↓
Observe failure
      ↓
Fix implementation
      ↓
Confirm green
```

This proves the test has actual defect-detection power.

---

# 23. Mutation Testing Awareness

Mutation testing asks:

> If meaningful code is changed deliberately, do the tests detect the change?

Conceptually:

```text
Production code
      ↓
Intentional mutation
      ↓
Test suite
      ↓
Did tests detect it?
```

Typical mutations:

```text
>  → >=
remove a filter
change sum → mean
alter a constant
remove null handling
```

A test suite that stays green after an important mutation may have a gap.

Tools such as `mutmut` can automate mutation testing, but the engineering principle matters more than memorizing the tool.

The objective is:

```text
meaningful defect
    →
test failure
```

not merely:

```text
line executed
```

---

# 24. Debugging Failed DataFrame Tests

When a DataFrame assertion fails, debug systematically.

## Step 1 — read the assertion

Determine whether the mismatch is:

- values
- columns
- rows
- dtypes
- index
- null behavior

## Step 2 — compare expected and actual

```python
print("EXPECTED")
print(expected)

print("ACTUAL")
print(actual)
```

For larger fixtures, print only the relevant keys and columns.

## Step 3 — inspect schema

```python
print(actual.dtypes)
print(expected.dtypes)
```

## Step 4 — inspect nulls

```python
print(actual.isna().sum())
```

## Step 5 — inspect row counts

```python
assert len(actual) == len(expected)
```

## Step 6 — check ordering

Ask whether the output is ordered by contract or whether the test is accidentally order-dependent.

## Step 7 — check duplicates

```python
duplicates = actual[actual["order_id"].duplicated(keep=False)]
print(duplicates)
```

## Step 8 — check timestamps and time zones

```python
print(actual["event_at"].dtype)
```

## Step 9 — inspect transformation logic

Do not immediately weaken the assertion.

## Step 10 — reproduce with the smallest fixture

The best debugging fixture is often two or three rows that expose the bug.

### Important principle

Do not respond to a failing test by blindly doing:

```python
check_dtype=False
```

or:

```python
check_exact=False
```

First determine whether the mismatch represents a real regression.

---

# 25. Test Quality

A strong transformation test is:

- deterministic
- isolated
- fast
- readable
- focused
- reproducible
- explicit
- maintainable
- meaningful

A useful review question is:

> If this test fails six months from now, will another engineer immediately understand what business rule broke?

If the answer is no, improve the fixture, test name, or assertion.

---

# 26. Common Testing Mistakes

| Mistake | Why it is bad | Better approach |
|---|---|---|
| Huge fixtures | Hide the behavior | Use minimal fixtures |
| Unclear fixtures | Reader cannot infer intent | Use builders or explicit literals |
| Testing implementation | Refactors cause useless failures | Test behavior |
| One test doing everything | Failures are ambiguous | One behavior per test |
| Hidden assumptions | Results become mysterious | Explicit schemas and defaults |
| Inferred schemas | Dtype bugs can be missed | Declare important types |
| Nondeterministic time | Tests change with the clock | Inject run date or freeze time |
| Shared mutable fixtures | Test contamination | Fresh state by default |
| Happy-path only | Production boundaries remain untested | Edge-case catalogue |
| Ignoring nulls | Silent data corruption | Explicit null tests |
| Ignoring duplicate keys | Inflated metrics | Duplicate fixtures |
| Ignoring timezone behavior | Boundary bugs | Explicit timezone fixtures |
| Excessive parametrization | Tests become unreadable | Keep cases focused |
| Excessive abstraction | Intent disappears | Abstract only repeated setup |
| Coverage-only thinking | Executed lines can still be wrong | Measure behavioral coverage |
| Snapshot everything | Blind snapshot updates hide regressions | Snapshot only complex stable outputs |
| Slow unit tests | Developers stop running them | Keep transformations in-memory |
| Passing for the wrong reason | False confidence | Deliberately inject bugs |

---

# 27. Production-Grade Testing Structure

For the broader Module 2.19 suite:

```text
tests/
├── unit/
├── property/
├── integration/
├── regression/
├── e2e/
├── builders/
├── data/
└── conftest.py
```

For this topic, concentrate on:

```text
tests/
├── unit/
│   ├── test_clean_orders.py
│   ├── test_deduplication.py
│   └── test_revenue.py
├── builders/
│   └── orders.py
├── data/
│   └── small fixtures
└── conftest.py
```

Later topics will add broader integration, property, regression, and E2E protection. This topic provides the unit-test foundation for those layers.

---

# 28. Hands-On Project — E-Commerce Order Transformation Pipeline

## Scenario

You are testing:

```text
raw_orders
    ↓
clean_orders
    ↓
deduplicate_orders
    ↓
normalize_customers
    ↓
calculate_revenue
    ↓
prepare_daily_metrics
```

The platform has experienced silent revenue errors caused by duplicate records, nulls, timezone boundaries, and late-arriving orders.

Your task is to build a focused transformation test suite.

## Required components

### 1. Fixture builders

Implement:

```python
make_order(...)
orders_frame(...)
```

with sensible defaults and explicit schema handling.

### 2. Explicit schemas

Define the intended schema for:

```text
order_id
customer_id
order_date
updated_at
quantity
unit_price
status
```

### 3. Unit tests

Test each pure transformation independently.

### 4. Parametrized tests

Cover status normalization and customer-name normalization.

### 5. Edge cases

At minimum:

```text
empty
one row
null
duplicate
tie
Unicode
whitespace
numeric boundary
timezone
DST
month-end
leap day
late record
```

### 6. Time-dependent tests

Use a supplied `run_date` for new code and `time-machine` where appropriate.

### 7. Cross-engine test

Implement the revenue rule in at least two engines and compare the business result.

### 8. Multi-step tests

Add a small number of meaningful composition tests.

### 9. Deliberate bug injection

Break:

```text
deduplication
null handling
timezone handling
date boundary
aggregation
```

and prove that tests catch each defect.

### 10. Coverage analysis

Run:

```bash
uv run pytest --cov=. --cov-report=term-missing
```

Then identify which important behaviors remain untested.

### 11. Mutation awareness

Choose one critical transformation and reason about which mutations its tests should kill.

---

# 29. Deliberate Failure Lab

Work through this cycle for every defect:

```text
Run test
   ↓
Observe failure
   ↓
Identify bug
   ↓
Explain root cause
   ↓
Fix implementation
   ↓
Run test again
   ↓
Confirm regression protection
```

## Lab A — duplicate bug

Inject:

```python
# wrong: keeps the oldest record
```

Expected lesson:

> The test must encode the actual deduplication rule, including the tie-breaker.

## Lab B — null bug

Inject:

```python
# wrong: converts missing quantity to zero
```

Expected lesson:

> Null is a data state, not automatically a numeric zero.

## Lab C — timezone bug

Inject:

```python
# wrong: compares naive local timestamps with UTC business timestamps
```

Expected lesson:

> Timestamp tests must define the timezone contract.

## Lab D — date boundary bug

Inject:

```python
# wrong: excludes the end date
```

Expected lesson:

> Boundary fixtures are essential for date filtering.

## Lab E — aggregation bug

Inject:

```python
# wrong: average instead of sum
```

Expected lesson:

> Small fixtures can expose mathematically incorrect aggregations immediately.

---

# 30. Checkpoint

You are ready to move forward when you can demonstrate all of the following.

### Concepts

- What is a pure DataFrame transformation?
- Why are minimal fixtures important?
- Why are explicit schemas useful?
- What is a DataFrame builder?
- How should builders use sensible defaults?
- How do parametrized tests work?
- What edge cases matter in data transformations?
- How do you test time-dependent code?
- Why use `time-machine`?
- How do you test multiple DataFrame engines?
- How do you choose fixture scope?
- What is branch coverage?
- Why is code coverage insufficient?
- What is mutation testing?
- How do you debug a failed DataFrame assertion?

### Practical demonstration

You should be able to:

```text
Build a fixture
    ↓
Write a rule-named test
    ↓
Run it
    ↓
Inject a bug
    ↓
Observe the failure
    ↓
Debug it
    ↓
Fix the implementation
    ↓
Prove the regression test remains useful
```

---

# 31. Interview Preparation

## 1. What makes a good DataFrame fixture?

**Strong answer:** It is minimal, explicit, deterministic, and contains only the rows and columns needed to prove the behavior. It should expose the failure mode without reproducing an entire production dataset.

## 2. Why are explicit schemas important?

**Strong answer:** DataFrame engines infer types differently. Explicit schemas prevent a test from silently changing because a column becomes nullable, floating point, string, or timestamp unexpectedly.

## 3. How do you test duplicate handling?

**Strong answer:** Create the smallest fixture containing the same business key multiple times, define the deterministic winner rule, and assert that the output contains exactly the expected record.

## 4. How do you test null handling?

**Strong answer:** Explicitly include nulls in relevant columns and assert the intended business behavior. Never assume null equals zero or empty string.

## 5. How should tests handle timestamps?

**Strong answer:** Prefer dependency injection through an explicit run date or clock abstraction. Freeze time when necessary for legacy code. Always define timezone semantics.

## 6. When should you use parametrization?

**Strong answer:** When one behavior has multiple compact examples. It reduces duplication while preserving clear cases. I avoid huge parameter tables that make individual failures difficult to understand.

## 7. When should you use pytest fixtures?

**Strong answer:** When setup is meaningfully reusable and has a clear name. I do not convert every small DataFrame into a fixture because inline data can be more readable.

## 8. What is fixture scope?

**Strong answer:** It controls fixture lifetime. Function scope gives isolation; broader scopes can reduce expensive setup but increase contamination risk if mutable state is shared.

## 9. Is 100% code coverage enough?

**Strong answer:** No. It tells us which code executed, not whether the important data behaviors were tested. Data edge-case coverage and business-rule coverage are essential.

## 10. What is mutation testing?

**Strong answer:** Mutation testing changes code deliberately—such as `>` to `>=` or `sum` to `mean`—and checks whether the test suite detects the defect. It measures the suite's ability to catch meaningful changes.

## 11. How would you test the same transformation across pandas and Spark?

**Strong answer:** Define the business contract independently of the engine, use equivalent controlled fixtures, normalize only legitimate engine differences, and compare the agreed result. Engine-specific semantics should still have dedicated tests.

## 12. How do you debug a failing DataFrame test?

**Strong answer:** Inspect the assertion, expected/actual values, schema, nulls, row counts, ordering, duplicates, timestamps, and transformation logic, then reproduce with the smallest failing fixture.

## 13. What belongs in unit tests versus integration tests?

**Strong answer:** Pure transformations belong in fast unit tests. Database, object-storage, broker, driver, and network behavior belongs in integration tests. The test boundary should follow the dependency boundary.

## 14. How do you prevent tests from becoming brittle?

**Strong answer:** Test behavior rather than implementation, keep fixtures minimal, avoid unnecessary ordering assumptions, use explicit schemas, isolate state, and abstract repeated setup only when it improves readability.

---

# 32. Final Assessment

Build a production-quality test suite for a transformation:

```text
raw_orders
    ↓
clean_orders
    ↓
deduplicate_orders
    ↓
calculate_revenue
    ↓
prepare_daily_metrics
```

Your assessment must include:

```text
Fixture design
Schema design
Unit testing
Edge cases
Parametrization
Time control
Cross-engine thinking
Debugging
Coverage
Mutation awareness
Production test quality
```

## Required deliverables

```text
tests/
├── unit/
├── builders/
├── data/
└── conftest.py
```

Your implementation must:

1. use minimal fixtures
2. use explicit schemas
3. name tests after rules
4. use builders where appropriate
5. use parametrization
6. test the full edge-case catalogue relevant to the transformations
7. control time deterministically
8. test important transformation composition
9. exercise at least two DataFrame/query engines
10. inject at least five realistic defects
11. prove that the tests catch those defects
12. run coverage analysis
13. explain the remaining coverage gaps
14. document why the tests are maintainable

### Assessment standard

A strong submission is not the one with the most tests.

It is the one where:

```text
important business rule
        ↓
small fixture
        ↓
clear test
        ↓
meaningful failure when broken
```

---

# 33. Practical Production Checklist

Before merging a transformation change:

```text
[ ] Is the transformation pure where practical?
[ ] Does each important behavior have a focused test?
[ ] Are fixtures minimal?
[ ] Are important schemas explicit?
[ ] Are test names business-rule oriented?
[ ] Are builders used only where they improve readability?
[ ] Are edge cases represented?
[ ] Are nulls explicit?
[ ] Are duplicates explicit?
[ ] Are ties deterministic?
[ ] Are Unicode and whitespace considered where relevant?
[ ] Are numeric boundaries tested?
[ ] Are time zones tested?
[ ] Are month-end/leap-day cases tested where relevant?
[ ] Are late-arriving records tested?
[ ] Is time deterministic?
[ ] Is fixture scope appropriate?
[ ] Are important branches covered?
[ ] Are behavioral gaps reviewed beyond code coverage?
[ ] Have meaningful bugs been deliberately injected?
[ ] Would a mutation of the critical rule fail a test?
[ ] Are failures easy to diagnose?
[ ] Are unit tests fast enough for normal development?
[ ] Does the test prove behavior rather than implementation?
```

---

# 34. Key Mental Models

Keep these models in mind.

### Transformation testing

```text
controlled input
      ↓
business rule
      ↓
expected data
```

### Fixture design

```text
minimum data
+
maximum clarity
```

### Test strength

```text
coverage
+
edge cases
+
meaningful assertions
+
defect detection
```

### Time

```text
clock dependency
      ↓
explicit run date / controlled clock
      ↓
deterministic test
```

### Debugging

```text
failure
 ↓
schema
 ↓
rows
 ↓
nulls
 ↓
ordering
 ↓
timestamps
 ↓
business rule
```

---

# 35. Connection to the Rest of Module 2.19

This topic establishes the unit-testing foundation for the rest of the module.

```text
01 Fixture DataFrame tests
        ↓
02 DataFrame equality and tolerances
        ↓
03 Integration tests with real services
        ↓
04 Property-based testing
        ↓
05 Synthetic and sampled test data
        ↓
06 Schema / contract regression
        ↓
07 End-to-end smoke tests
```

The later topics expand the testing surface. They do not replace good transformation unit tests.

Keep this topic focused on:

> **Testing transformation code using controlled fixture DataFrames.**

---

# 36. Final Mastery Checklist

Before considering Topic 01 complete:

```text
[ ] Pure DataFrame → DataFrame testing
[ ] Minimal fixtures
[ ] Explicit schemas
[ ] One behavior per test
[ ] Rule-named tests
[ ] DataFrame builders/factories
[ ] Sensible defaults
[ ] pytest fixtures
[ ] Parametrized/table-driven tests
[ ] Empty DataFrames
[ ] One-row DataFrames
[ ] All-null values
[ ] Duplicates
[ ] Ties
[ ] Unicode
[ ] Whitespace
[ ] Numeric extremes
[ ] Time zones
[ ] DST boundaries
[ ] Month-end
[ ] Leap days
[ ] Late-arriving records
[ ] Inline fixtures
[ ] CSV fixtures
[ ] JSON fixtures
[ ] Parquet fixtures
[ ] Time-dependent transformations
[ ] Run-date dependency injection
[ ] time-machine
[ ] Multi-step transformations
[ ] pandas
[ ] Polars
[ ] DuckDB
[ ] Spark
[ ] Fixture scope
[ ] Fixture cost
[ ] Branch coverage
[ ] Edge-case coverage
[ ] Code coverage limitations
[ ] Deliberate bug injection
[ ] Mutation testing awareness
[ ] Debugging failed tests
[ ] Test quality
[ ] Common mistakes
[ ] Production test structure
[ ] Hands-on project
[ ] Failure lab
[ ] Checkpoint
[ ] Interview questions
[ ] Final assessment
```

## Final principle

The strongest transformation test suite is not the largest one.

It is the suite that makes important data behavior **explicit, deterministic, readable, fast, and difficult to accidentally break**.

When a production bug occurs, the best outcome is:

```text
production incident
      ↓
smallest reproducing fixture
      ↓
permanent regression test
      ↓
fixed transformation
      ↓
future protection
```

That is how DataFrame unit tests become an engineering control rather than a collection of assertions.
