# Topic 02 — DataFrame Equality and Tolerance Assertions

> **Stage 2 — Python for Data Engineering**  
> **Module 2.19 — Testing Data Pipelines**  
> **Level:** Beginner → Intermediate → Advanced → Production  
> **Primary tools:** Python 3.12+, pytest, pandas, Polars, NumPy, DuckDB, PySpark, syrupy, pytest-cov

---

## 1. Introduction

The question at the heart of this topic is:

> **When can we say that two DataFrames are equal?**

A beginner may look at two tables and say:

```text
"The values look the same."
```

A production Data Engineer asks more questions:

```text
Are the columns identical?
Are their positions identical?
Are the dtypes identical?
Are the rows in the same order?
Are duplicate rows preserved?
Are nulls represented the same way?
Are timestamps the same instant?
Are floating-point differences numerical noise or a real bug?
Does the business contract require exact equality?
```

That distinction matters because a pipeline can produce output that looks correct while being technically or semantically different.

For example:

```text
Expected:

order_id | revenue
---------|--------
O-001    | 100.00
O-002    | 200.00


Actual:

order_id | revenue
---------|--------
O-002    | 200.00
O-001    | 100.00
```

The business result may be equivalent if row order is not part of the contract.

But this is different:

```text
Expected:

order_id | revenue
---------|--------
O-001    | 100.00
O-002    | 200.00


Actual:

order_id | revenue
---------|--------
O-001    | 100.00
O-002    | 200.01
```

That is a meaningful numerical difference.

And this is different again:

```text
Expected dtype: Int64
Actual dtype: float64
```

Whether that is acceptable depends on the data contract.

The central engineering principle for this topic is:

> **Make the assertion as strict as the data contract requires—and no stricter.**

Do not weaken assertions simply because they fail.

---

# 2. Learning Objectives

By the end of this topic, you should be able to:

- explain what DataFrame equality means
- compare pandas DataFrames with `assert_frame_equal`
- compare Polars DataFrames with `polars.testing.assert_frame_equal`
- compare Spark DataFrames with `pyspark.testing.assertDataFrameEqual`
- use `numpy.testing.assert_allclose`
- distinguish values, columns, column order, dtypes, row order, and pandas index
- deliberately relax equality requirements when the business contract permits it
- compare unordered outputs correctly
- reason about `None`, `NaN`, `pd.NA`, Polars `null`, Polars `NaN`, and SQL `NULL`
- choose `rtol` and `atol` based on computation and business requirements
- compare money exactly using `Decimal` or integer cents
- compare timestamps by instant rather than textual representation
- create readable row-level and per-column diffs
- use anti-joins for diagnostics
- compare large outputs using counts, hashes, checksums, and deterministic samples
- use snapshot/golden tests with `syrupy`
- normalize legitimate cross-engine dtype differences
- build reusable comparison helpers without hiding important differences
- diagnose failed equality assertions
- design a production-grade DataFrame comparison strategy

---

# 3. The DataFrame Equality Model

A useful mental model is:

```text
DataFrame equality
    =
values
+
columns
+
column order
+
dtypes
+
row order
+
index
+
null semantics
+
timestamp semantics
+
numerical precision
```

But there is an important qualification:

> **Not every test needs every dimension to match.**

Equality is a contract.

For example:

### Strict equality

Everything relevant must match.

```text
values
columns
dtypes
order
index
```

### Order-insensitive equality

The same rows must exist, but their order is not meaningful.

```text
values
columns
dtypes
business keys
```

### Numeric-tolerant equality

Small computational differences are accepted.

```text
values within justified tolerance
```

### Business-level equality

Two physical representations may differ while representing the same business meaning.

Examples:

```text
UTC timestamp
vs
equivalent timezone-aware timestamp

int32
vs
int64
```

Only normalize such differences when the contract explicitly allows them.

---

# 4. Basic pandas DataFrame Equality

Start with pandas because it makes the equality dimensions easy to see.

```python
from __future__ import annotations

import pandas as pd
from pandas.testing import assert_frame_equal
```

Create two DataFrames:

```python
expected = pd.DataFrame(
    {
        "order_id": ["O-001", "O-002"],
        "revenue": [100.0, 200.0],
    }
)

actual = pd.DataFrame(
    {
        "order_id": ["O-001", "O-002"],
        "revenue": [100.0, 200.0],
    }
)
```

Compare:

```python
assert_frame_equal(actual, expected)
```

If they are equal according to the assertion's configured semantics, the test passes.

A complete pytest test:

```python
def test_revenue_output() -> None:
    expected = pd.DataFrame(
        {
            "order_id": ["O-001", "O-002"],
            "revenue": [100.0, 200.0],
        }
    )

    actual = pd.DataFrame(
        {
            "order_id": ["O-001", "O-002"],
            "revenue": [100.0, 200.0],
        }
    )

    assert_frame_equal(actual, expected)
```

Run:

```bash
uv run pytest -q
```

---

# 5. What Happens When Equality Fails?

Change one value:

```python
actual = pd.DataFrame(
    {
        "order_id": ["O-001", "O-002"],
        "revenue": [100.0, 201.0],
    }
)
```

The assertion should fail.

Conceptually, the failure tells you:

```text
Expected: 200.0
Actual:   201.0
```

This is useful because the assertion is telling you which equality dimension failed.

The debugging question should then be:

```text
Is 201.0 a real business bug?
or
Was 201.0 legitimately produced by a different numerical representation?
```

Do not immediately loosen the assertion.

---

# 6. Dimensions of Equality

## 6.1 Values

The most obvious dimension is value equality.

```text
expected: 100
actual:   101
```

This should normally fail.

For business measures such as revenue, the question becomes whether exact or tolerant equality is required.

---

## 6.2 Columns

Suppose:

```text
Expected:

customer_id
revenue
```

Actual:

```text
customer_id
total_revenue
```

Even if the values are identical, the outputs are not equivalent if downstream consumers expect `revenue`.

A column rename is a schema change.

Therefore, column names should normally be strict.

---

## 6.3 Column Order

Consider:

```text
Expected:

customer_id
revenue
status
```

versus:

```text
Actual:

status
customer_id
revenue
```

The columns contain the same names but are ordered differently.

Whether that matters depends on the contract.

For a relational table where consumers address columns by name, order may be irrelevant.

For a serialized positional format, generated file, or snapshot, order may matter.

Never ignore column order automatically.

---

## 6.4 Dtypes

Examples:

```text
int64
float64
string
datetime64
```

A dtype difference may be harmless—or may break downstream behavior.

For example:

```text
quantity: Int64
```

versus:

```text
quantity: float64
```

can affect:

- joins
- serialization
- null handling
- memory usage
- downstream schema contracts

If dtype is part of the contract, compare it strictly.

---

## 6.5 Row Order

These DataFrames contain the same records:

```text
O-001
O-002
O-003
```

and:

```text
O-003
O-001
O-002
```

But they are not the same **ordered DataFrame**.

If the transformation contract says output order is meaningful, the assertion should fail.

If the output is logically unordered, normalize ordering before comparison.

---

## 6.6 pandas Index

pandas has an index in addition to ordinary columns.

For example:

```python
expected = pd.DataFrame(
    {"order_id": ["O-001", "O-002"]},
    index=[0, 1],
)

actual = pd.DataFrame(
    {"order_id": ["O-001", "O-002"]},
    index=[10, 11],
)
```

The visible rows may look identical, but the index differs.

You can deliberately remove index significance when the index is not part of the contract:

```python
actual = actual.reset_index(drop=True)
expected = expected.reset_index(drop=True)

assert_frame_equal(actual, expected)
```

Do not blindly reset indices simply to make tests pass.

First decide whether the index has semantic meaning.

---

# 7. `pandas.testing.assert_frame_equal`

`pandas.testing.assert_frame_equal` should be your primary pandas DataFrame equality assertion.

Use it instead of:

```python
assert actual == expected
```

because DataFrame equality is multidimensional.

A useful strict comparison is:

```python
assert_frame_equal(
    actual,
    expected,
)
```

The assertion can reason about:

- values
- columns
- dtypes
- index
- ordering
- numerical comparison

The exact configuration should reflect the contract.

### Engineering rule

Do not memorize flags in isolation.

For every relaxed option ask:

```text
What difference does this allow?
Why is that difference acceptable?
What production bug could it hide?
```

---

# 8. Strict vs Deliberately Relaxed Assertions

A dangerous testing pattern is:

```python
assert_frame_equal(
    actual,
    expected,
    check_dtype=False,
    check_like=True,
)
```

simply because the strict assertion failed.

This can hide real regressions.

Instead use a decision process:

```text
Did dtype change?
    ↓
Is dtype part of the contract?
    ├── yes → fail
    └── no  → normalize or deliberately relax

Did row order change?
    ↓
Is order part of the contract?
    ├── yes → fail
    └── no  → compare in a stable order
```

### Principle

> Relax an assertion only when the behavior is intentionally unspecified.

---

# 9. Order-Insensitive Comparison

Suppose the business output is:

```text
order_id | revenue
---------|--------
O-001    | 100
O-002    | 200
O-003    | 300
```

The actual result may arrive as:

```text
O-003
O-001
O-002
```

If row order does not matter, sort both outputs using stable business keys.

```python
sort_keys = ["order_id"]

expected_sorted = expected.sort_values(sort_keys).reset_index(drop=True)
actual_sorted = actual.sort_values(sort_keys).reset_index(drop=True)

assert_frame_equal(actual_sorted, expected_sorted)
```

### Why stable keys matter

Do not sort by a non-unique field if that leaves ordering ambiguous.

For example:

```text
customer_id
```

may not uniquely identify rows.

Prefer:

```text
customer_id + order_id
```

or another true deterministic ordering key.

### Duplicate rows matter

Do not use:

```python
set(...)
```

to compare rows.

A set removes duplicates.

That can turn:

```text
A
A
B
```

into:

```text
A
B
```

and hide a duplicate-record bug.

---

# 10. Null, NaN, and Missing-Value Semantics

Missing values are one of the most common sources of confusion in DataFrame tests.

Important representations include:

```text
pandas:
    None
    NaN
    pd.NA

Polars:
    null
    NaN

SQL:
    NULL
```

These are not automatically interchangeable.

---

# 11. pandas: `None`, `NaN`, and `pd.NA`

### `None`

Python's null object:

```python
None
```

### `NaN`

A floating-point "not a number":

```python
float("nan")
```

### `pd.NA`

pandas' nullable missing-value marker:

```python
pd.NA
```

Example:

```python
import pandas as pd

df = pd.DataFrame(
    {
        "a": [1.0, float("nan")],
        "b": [1, pd.NA],
        "c": ["x", None],
    }
)
```

The columns can have different dtype and missing-value semantics.

Do not reason about missing values only from how they print.

Inspect:

```python
print(df.dtypes)
print(df.isna())
```

---

# 12. Polars: `null` vs `NaN`

Polars distinguishes:

```text
null
```

from:

```text
NaN
```

Conceptually:

```text
null = missing value

NaN = floating-point value representing "not a number"
```

That distinction matters for:

- aggregations
- filters
- arithmetic
- serialization
- equality assertions

When comparing Polars DataFrames, determine whether the business contract cares about the distinction.

---

# 13. SQL `NULL`

SQL uses:

```sql
NULL
```

to represent missing/unknown values.

A crucial SQL rule is that:

```sql
NULL = NULL
```

does not behave like ordinary value equality.

Use appropriate SQL null semantics such as:

```sql
IS NULL
```

or:

```sql
IS NOT DISTINCT FROM
```

when comparing nullable values where supported.

This matters when a DataFrame transformation is validated against a SQL implementation.

---

# 14. Null vs NaN Failure Lab

Imagine:

```text
Expected:

customer_id | score
------------|------
1           | NULL

Actual:

customer_id | score
------------|------
1           | NaN
```

Do not immediately answer:

```text
"Yes, they are equal."
```

Ask:

1. Which engine produced the output?
2. What are the actual dtypes?
3. Is `score` numeric?
4. Does the business contract distinguish missing from floating-point NaN?
5. Will serialization preserve the distinction?
6. What will downstream SQL or analytics systems see?

Example inspection:

```python
print(expected.dtypes)
print(actual.dtypes)

print(expected.isna())
print(actual.isna())
```

The correct assertion depends on the data contract.

---

# 15. Floating-Point Precision

A classic example:

```python
0.1 + 0.2
```

is not represented exactly as decimal `0.3` in binary floating-point arithmetic.

Therefore:

```python
0.1 + 0.2 == 0.3
```

should not be treated as a universal model of numerical equality.

For numerical computations, use a tolerance when the computation legitimately introduces numerical error.

NumPy provides:

```python
import numpy as np

np.testing.assert_allclose(
    actual,
    expected,
    rtol=...,
    atol=...,
)
```

---

# 16. `rtol` and `atol`

Two important parameters are:

```text
rtol = relative tolerance
atol = absolute tolerance
```

Conceptually, the comparison allows a difference based on both the expected value's scale and an absolute floor.

A simplified mental model is:

```text
allowed difference
≈
atol + rtol × |expected|
```

### Why both exist

For large values, a relative tolerance can be useful.

For values close to zero, absolute tolerance becomes especially important.

Example:

```text
expected = 1,000,000
actual   = 1,000,001
```

and:

```text
expected = 0.000001
actual   = 0.000002
```

are very different situations.

One universal tolerance is rarely appropriate for every numerical column.

---

# 17. Choosing Tolerance from the Computation

Never default to:

```text
rtol=1e-5
```

just because it is familiar.

A justified tolerance considers:

- expected computational error
- input scale
- number of operations
- algorithm
- numerical stability
- decimal precision
- business requirements

For example, a ratio calculated from floating-point aggregates may legitimately have tiny numerical noise.

A currency total should generally have an exact monetary contract instead.

### Production decision

Ask:

```text
What error does the algorithm legitimately introduce?

What error does the business permit?

Are they the same?
```

If the answer is no, fix the transformation or representation rather than widening the assertion.

---

# 18. Never Use Tolerance to Hide Rounding Bugs

Suppose:

```text
Expected revenue: 100.00
Actual revenue:    99.95
```

Do not write:

```python
atol=0.10
```

just to make the test pass.

Investigate:

```text
floating-point noise?
rounding rule?
currency conversion?
wrong aggregation?
wrong input?
wrong business logic?
```

A tolerance is for legitimate numerical uncertainty, not incorrect business behavior.

---

# 19. Exact Money Comparison

Financial values generally require exact semantics.

Two strong representations are:

```text
Decimal
integer cents
```

## Decimal

```python
from decimal import Decimal

expected = Decimal("10.10")
actual = Decimal("10.10")

assert actual == expected
```

Do not construct financial `Decimal` values from binary floats when exact decimal input is required:

```python
# Avoid as a source of exact monetary values:
Decimal(10.10)
```

Prefer:

```python
Decimal("10.10")
```

## Integer cents

```python
expected_cents = 1010
actual_cents = 1010

assert actual_cents == expected_cents
```

This makes exactness explicit.

### Revenue example

```python
def test_revenue_is_exact() -> None:
    expected = pd.DataFrame(
        {
            "order_id": ["O-001"],
            "revenue_cents": [1010],
        }
    )

    actual = pd.DataFrame(
        {
            "order_id": ["O-001"],
            "revenue_cents": [1010],
        }
    )

    assert_frame_equal(actual, expected)
```

Do not use arbitrary floating-point tolerance to validate exact money.

---

# 20. Timestamp Comparison

Timestamps have several dimensions:

```text
unit
timezone
representation
instant
```

Units can include:

```text
seconds
milliseconds
microseconds
nanoseconds
```

A timestamp may also be:

```text
timezone-aware
timezone-naive
```

Consider:

```text
2026-01-01T00:00:00Z
```

and:

```text
2025-12-31T19:00:00-05:00
```

These can represent the same instant.

Therefore:

> **Same instant is not the same thing as same textual representation.**

---

# 21. Instant vs Representation

Suppose a business rule says:

> "The event occurred at this instant."

Then comparison should generally normalize to a common temporal representation before comparison.

For example:

```python
expected["event_at"] = pd.to_datetime(
    expected["event_at"],
    utc=True,
)

actual["event_at"] = pd.to_datetime(
    actual["event_at"],
    utc=True,
)
```

Then compare the normalized timestamps.

But if the contract requires preserving the original timezone representation, do not normalize it away.

The contract decides.

---

# 22. Timestamp Failure Lab

## Different units

A value representing:

```text
2026-01-01T00:00:00
```

may be stored as seconds, milliseconds, microseconds, or nanoseconds.

A unit mismatch can produce completely different numerical values.

## Different timezones

Test:

```text
UTC
UTC+05:30
UTC-05:00
```

and verify whether they represent the same instant.

## Naive vs aware

Do not silently compare:

```text
2026-01-01 00:00
```

with:

```text
2026-01-01 00:00 UTC
```

as if the semantics were identical.

### Diagnostic checklist

```text
What unit is stored?
Is the timestamp timezone-aware?
What timezone does it represent?
Is the business rule about an instant or a local wall-clock time?
Should the original representation be preserved?
```

---

# 23. Readable DataFrame Diffs

A generic equality failure is sometimes insufficient.

A production-quality diagnostic should answer:

```text
What changed?
Where did it change?
How many rows changed?
Which columns changed?
What were expected and actual values?
```

For small DataFrames, the native assertion may be enough.

For larger outputs, build a diagnostic layer.

---

# 24. Anti-Join Based Diffs

Suppose `order_id` is a unique business key.

We want to identify:

```text
expected - actual
```

and:

```text
actual - expected
```

For pandas:

```python
expected_keys = set(expected["order_id"])
actual_keys = set(actual["order_id"])

missing_ids = expected_keys - actual_keys
unexpected_ids = actual_keys - expected_keys
```

For a richer DataFrame diagnostic, merge on the business key.

```python
comparison = expected.merge(
    actual,
    on="order_id",
    how="outer",
    suffixes=("_expected", "_actual"),
    indicator=True,
)
```

Then:

```python
missing = comparison[comparison["_merge"] == "left_only"]
unexpected = comparison[comparison["_merge"] == "right_only"]
```

This gives a readable explanation of missing and unexpected rows.

### Important limitation

If the key is not unique, a simple key merge can produce multiplicative matches.

Before using an anti-join strategy, establish whether the key is:

```text
unique
composite
non-unique
```

For non-unique data, compare multiplicities explicitly.

---

# 25. Changed Values After Key Matching

For rows present on both sides:

```python
matched = comparison[comparison["_merge"] == "both"].copy()
```

Compare relevant columns:

```python
matched["revenue_changed"] = (
    matched["revenue_expected"]
    != matched["revenue_actual"]
)
```

For multiple columns:

```python
columns = ["revenue", "status", "customer_id"]

for column in columns:
    matched[f"{column}_changed"] = (
        matched[f"{column}_expected"]
        != matched[f"{column}_actual"]
    )
```

This produces a much more useful diagnostic than:

```text
DataFrames are not equal.
```

---

# 26. Per-Column Difference Summaries

A useful report might look like:

```text
column        mismatches
------------------------
revenue       12
status         3
customer_id    0
created_at     7
```

Example helper:

```python
def mismatch_counts(
    expected: pd.DataFrame,
    actual: pd.DataFrame,
    columns: list[str],
) -> dict[str, int]:
    if len(expected) != len(actual):
        raise ValueError("Rows must be aligned before comparison.")

    counts: dict[str, int] = {}

    for column in columns:
        counts[column] = int(
            (expected[column] != actual[column]).fillna(False).sum()
        )

    return counts
```

For production use, extend this to explicit null semantics and numeric tolerances rather than relying on raw `!=`.

The goal is diagnosis, not merely pass/fail.

---

# 27. Large Output Comparison

A full equality comparison becomes increasingly expensive as outputs grow.

Useful techniques include:

```text
row counts
schema checks
checksums
row hashes
deterministic samples
targeted comparisons
```

These are complementary tools.

No single technique proves everything.

---

# 28. Row Counts

The simplest check:

```python
assert len(actual) == len(expected)
```

This is useful but insufficient.

Example:

```text
Expected:
A
B
C

Actual:
A
B
B
```

Both contain three rows.

The row count passes.

The data is still wrong.

Therefore:

```text
row count
```

is a useful invariant, not an equality proof.

---

# 29. Checksums and Hashes

For very large outputs, a dataset fingerprint can be useful.

Conceptual process:

```text
DataFrame
    ↓
canonical representation
    ↓
row hashes
    ↓
aggregate checksum
```

The important prerequisite is **canonicalization**.

You must define:

- column ordering
- row ordering
- serialization
- null representation
- timestamp representation
- numeric representation

Otherwise two equivalent datasets can produce different fingerprints.

Conversely, a hash match is not a substitute for a useful diagnostic when a mismatch occurs.

### Hash collisions

Cryptographic hashes make accidental collisions extremely unlikely, but no hash is mathematically a proof of equality.

Use hashes as an efficient validation mechanism with an appropriate risk model.

---

# 30. Deterministic Samples

Sampling can reduce diagnostic cost.

Useful approaches include:

```text
fixed-seed random sample
stratified sample
business-key sample
```

A fixed seed makes the test reproducible.

```python
sample = df.sample(
    n=min(1000, len(df)),
    random_state=42,
)
```

Do not use an uncontrolled random sample in a deterministic CI test.

### Critical limitation

A sample is not proof that the entire output is equal.

Sampling is useful for:

- diagnostics
- smoke validation
- quick comparisons
- investigating large mismatches

It should not silently replace a required full comparison.

---

# 31. Large-Dataset Comparison Strategy

Use this as a practical decision framework:

```text
Small DataFrame
    ↓
full equality assertion

Medium DataFrame
    ↓
full equality
+
readable diff

Very large DataFrame
    ↓
schema
+
row counts
+
checksums/hashes
+
deterministic samples
+
targeted key-level comparison
```

This is a performance and diagnostic trade-off, not a universal law.

If the business requirement demands exact row-level equivalence, design the validation accordingly.

---

# 32. Snapshot / Golden Testing

Snapshot testing stores a known-good output and compares future results against it.

Conceptually:

```text
Input
  ↓
Transformation
  ↓
Output
  ↓
Stored snapshot
```

Then:

```text
New output
  ↓
Compare with snapshot
```

Snapshots are useful for:

- complex structured outputs
- stable report-like outputs
- generated SQL
- serialized objects
- transformations whose complete output is cumbersome to express manually

They are risky when outputs are:

- enormous
- unstable
- timestamp-dependent
- randomly ordered
- frequently changing

### Snapshot discipline

Never respond to a failing snapshot by immediately accepting the update.

First ask:

```text
Was the behavior intentionally changed?
Why?
What downstream effect does it have?
Did the business contract change?
```

---

# 33. Using `syrupy`

Install:

```bash
uv add --dev syrupy
```

A simple example:

```python
def test_report_output(snapshot) -> None:
    report = build_report()

    assert report == snapshot
```

On the first intentional creation, the snapshot is recorded.

On later runs, the output is compared against the stored snapshot.

A snapshot change should be reviewed like a code change.

### Good snapshot workflow

```text
snapshot fails
    ↓
inspect diff
    ↓
understand why
    ↓
confirm intended behavior
    ↓
review updated snapshot
    ↓
commit change
```

Not:

```text
snapshot fails
    ↓
accept update
    ↓
green CI
```

---

# 34. Cross-Engine Dtype Normalization

The same logical data may have different physical representations across:

```text
pandas
Polars
DuckDB
Spark
```

Examples include:

```text
integer widths
decimal types
nullable integers
timestamps
strings
nulls
floating-point types
```

Use two concepts:

```text
logical schema
```

versus:

```text
physical representation
```

For example:

```text
pandas nullable integer
Spark integer
```

may satisfy the same logical contract.

But do not normalize away differences that matter.

---

# 35. Cross-Engine Comparison

Suppose a transformation is implemented in pandas first and migrated to Spark.

The business rule is:

```text
revenue = quantity × unit_price
```

### pandas

```python
def revenue_pandas(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["revenue"] = result["quantity"] * result["unit_price"]
    return result
```

### Polars

```python
import polars as pl


def revenue_polars(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        (pl.col("quantity") * pl.col("unit_price")).alias("revenue")
    )
```

### DuckDB

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

### Spark

```python
from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def revenue_spark(df: DataFrame) -> DataFrame:
    return df.withColumn(
        "revenue",
        F.col("quantity") * F.col("unit_price"),
    )
```

The comparison strategy should separate:

```text
engine-specific representation difference
```

from:

```text
business-logic difference
```

If all four produce the same business result but different integer widths, that may be a normalization issue.

If one produces a different revenue, that is a business regression.

---

# 36. Building a Reusable Comparison Helper

A mature test suite often benefits from a shared helper.

A useful conceptual interface is:

```python
assert_dataframes_equal(
    actual,
    expected,
    order_by=["order_id"],
    check_dtypes=True,
    numeric_tolerance=None,
)
```

A helper may be responsible for:

- schema validation
- deterministic ordering
- null handling
- numerical tolerance
- timestamp normalization
- readable diagnostics

But avoid creating a giant helper with dozens of hidden policies.

### Good helper

```text
explicit configuration
+
clear defaults
+
useful diagnostics
+
documented semantics
```

### Bad helper

```text
silently disables checks
+
silently sorts
+
silently coerces dtypes
+
silently widens tolerance
```

The helper should make equality semantics more visible, not less.

---

# 37. A Production-Oriented Helper

A small, explicit helper can start with configuration:

```python
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class FrameComparisonConfig:
    order_by: Sequence[str] | None = None
    check_dtypes: bool = True
    rtol: float | None = None
    atol: float | None = None
```

The configuration makes important decisions visible.

A larger production helper can then:

1. validate expected columns
2. normalize only configured dimensions
3. sort only when explicitly requested
4. compare exact columns exactly
5. compare numeric columns using configured tolerances
6. compare timestamps according to the configured contract
7. produce missing/extra/changed-row diagnostics

Do not make every test configure every option. Establish sensible defaults, but make meaningful relaxations explicit.

---

# 38. Failure-First Testing

A strong way to validate the comparison layer is to deliberately introduce defects.

The minimum failure set should include:

```text
1. wrong value
2. missing column
3. extra column
4. wrong dtype
5. wrong column order
6. wrong row order
7. null vs NaN mismatch
8. floating-point difference
9. timestamp mismatch
10. incorrect money rounding
```

For each failure:

```text
Expected
Actual
↓
Why does the test fail?
↓
Which equality dimension changed?
↓
Is the difference legitimate?
↓
What is the correct fix?
```

This teaches diagnostic reasoning rather than assertion memorization.

---

# 39. Common Mistakes

## Mistake 1 — blindly using exact equality

Why dangerous:

```text
legitimate numerical noise
```

may create brittle failures.

Better:

```text
use exact equality unless the computation genuinely requires tolerance
```

---

## Mistake 2 — blindly ignoring dtype

Why dangerous:

```text
schema regressions
```

can pass unnoticed.

Better:

```text
ignore dtype only when the logical contract permits it
```

---

## Mistake 3 — blindly ignoring row order

Why dangerous:

Order may actually be part of the output contract.

Better:

```text
determine whether ordering is semantically meaningful
```

---

## Mistake 4 — huge tolerances

Why dangerous:

```text
real business errors become green tests
```

Better:

```text
derive tolerance from numerical behavior and business requirements
```

---

## Mistake 5 — tolerance for monetary values

Why dangerous:

A five-cent revenue bug is not numerical noise.

Better:

```text
Decimal
or
integer cents
```

---

## Mistake 6 — treating NaN and NULL as identical

Why dangerous:

They have different semantics.

Better:

```text
test the actual missing-value contract
```

---

## Mistake 7 — comparing timestamp strings

Why dangerous:

Equivalent instants can have different representations.

Better:

```text
compare instants when the contract is about instants
```

---

## Mistake 8 — checking only row counts

Why dangerous:

Different records can have the same count.

Better:

```text
count
+
keys
+
values
```

as appropriate.

---

## Mistake 9 — relying only on hashes

Why dangerous:

A hash is a fingerprint, not a useful mismatch explanation.

Better:

```text
hash for efficient validation
+
detailed diff when mismatched
```

---

## Mistake 10 — relying only on samples

Why dangerous:

A bug may exist outside the sample.

Better:

```text
sample for diagnostics
full comparison when the contract requires full comparison
```

---

## Mistake 11 — blindly updating snapshots

Why dangerous:

The regression becomes invisible.

Better:

```text
understand
→ review
→ intentionally update
```

---

## Mistake 12 — ignoring duplicate keys

Why dangerous:

A key-based comparison may accidentally create many-to-many matches.

Better:

```text
validate key uniqueness or compare multiplicities explicitly
```

---

## Mistake 13 — nondeterministic samples

Why dangerous:

CI can fail on different rows from one run to another.

Better:

```text
fixed seed
```

or deterministic business-key selection.

---

## Mistake 14 — hiding semantics inside helpers

Why dangerous:

A reviewer cannot see what the test permits.

Better:

```text
explicit comparison configuration
```

---

## Mistake 15 — over-normalizing cross-engine outputs

Why dangerous:

A real semantic regression can be converted into an apparently harmless representation difference.

Better:

```text
normalize known representation differences
keep meaningful differences visible
```

---

# 40. Production Data Engineering Scenarios

## Scenario 1 — Revenue mismatch

Expected:

```text
100.00
```

Actual:

```text
100.01
```

Investigate:

```text
floating-point noise?
rounding?
currency conversion?
wrong aggregation?
```

Do not widen tolerance automatically.

---

## Scenario 2 — Duplicate orders

Expected:

```text
O-001 → one row
```

Actual:

```text
O-001 → two rows
```

A row-count check may detect the issue, but a key-aware diff explains it.

---

## Scenario 3 — Timezone bug

A daily aggregation moves events across a calendar boundary.

The correct diagnostic is not:

```text
string comparison
```

but:

```text
timestamp unit
+
timezone
+
instant
+
business timezone
```

---

## Scenario 4 — Schema drift

A numeric column changes from:

```text
integer
```

to:

```text
float
```

Even if values appear unchanged, the downstream schema contract may have changed.

---

## Scenario 5 — Cross-engine migration

A pandas transformation is rewritten in Spark.

The comparison should answer:

```text
Are business outputs equivalent?
```

while separately deciding whether:

```text
dtype differences
row ordering
timestamp representation
```

are acceptable.

---

# 41. Hands-On Project — DataFrame Comparison and Validation Framework

## Scenario

An e-commerce pipeline has been migrated from pandas to Spark.

You have:

```text
expected_pandas_output
actual_spark_output
```

The team reports differences in:

```text
row ordering
null representation
floating-point calculations
timestamps
schema types
```

Your task is to build a robust comparison strategy.

---

## Required deliverables

### 1. Schema comparison

Detect:

- missing columns
- extra columns
- type differences

### 2. Column comparison

Determine whether column order is part of the contract.

### 3. Row-count comparison

Detect missing/extra records.

### 4. Order handling

Sort by stable business keys only when order is not part of the contract.

### 5. Null handling

Explicitly define:

```text
None
NaN
pd.NA
null
```

semantics.

### 6. Numeric tolerance

Choose `rtol` and `atol` from the computation.

### 7. Exact money comparison

Use:

```text
Decimal
or integer cents
```

### 8. Timestamp normalization

Compare instants where the contract requires instant equality.

### 9. Readable row-level diff

Report:

```text
missing
extra
changed
```

records.

### 10. Per-column mismatch summary

Produce:

```text
column        mismatches
revenue       ...
status        ...
created_at    ...
```

### 11. Large-output strategy

Design:

```text
schema
+
counts
+
hashes/checksums
+
deterministic samples
```

as appropriate.

### 12. Snapshot/golden test

Use `syrupy` for one complex stable output.

### 13. Reusable comparison helper

Provide an explicit API that does not silently weaken assertions.

---

# 42. Deliberate Failure Lab

Create a deliberately broken transformation and make the comparison framework diagnose it.

Inject:

```text
Bug 1: wrong aggregation
Bug 2: wrong rounding
Bug 3: timezone conversion
Bug 4: dropped column
Bug 5: dtype change
Bug 6: duplicate rows
Bug 7: null converted to NaN
Bug 8: unstable row ordering
```

For each:

```text
Run test
    ↓
Read failure
    ↓
Identify difference dimension
    ↓
Determine whether difference is legitimate
    ↓
Fix transformation or assertion
    ↓
Re-run
```

The objective is not merely to get a green build.

The objective is to understand **why the comparison failed**.

---

# 43. Checkpoint

You should now be able to answer:

1. What does DataFrame equality mean?
2. Which equality dimensions can differ?
3. When should row order matter?
4. When should dtype matter?
5. Why do null and NaN differ?
6. What are `rtol` and `atol`?
7. How should numerical tolerance be chosen?
8. Why should money generally use exact semantics?
9. How should timestamps be compared?
10. What is an anti-join diff?
11. Why are row counts insufficient?
12. Why use checksums and hashes?
13. Why are samples not proof of equality?
14. What is snapshot testing?
15. Why can cross-engine outputs differ?
16. When should normalization happen?
17. How should reusable comparison helpers be designed?

### Coding checkpoint

Implement:

```python
assert_dataframes_equal(
    actual,
    expected,
    order_by=["order_id"],
    check_dtypes=True,
)
```

Then extend it to support:

```text
numeric tolerance
timestamp normalization
readable diffs
```

Finally, inject a defect and prove the helper detects it.

---

# 44. Interview Preparation

## 1. What does DataFrame equality mean?

**Strong answer:** It is multidimensional. Depending on the contract, equality can include values, columns, column order, dtypes, row order, index, null semantics, timestamp representation, and numerical precision. The correct comparison is determined by the business contract.

## 2. Why use `assert_frame_equal` instead of `==`?

**Strong answer:** DataFrame equality is not a simple scalar comparison. `assert_frame_equal` provides structured validation of values, schema-related properties, index, ordering, and other dimensions.

## 3. When should you ignore row order?

**Strong answer:** Only when the output contract is logically unordered. I would sort both outputs by deterministic business keys or use an explicitly order-insensitive comparison rather than relying on arbitrary set conversion.

## 4. Why is dtype important?

**Strong answer:** Dtypes affect nullability, serialization, downstream schemas, arithmetic, joins, memory, and compatibility. A dtype change can be a real contract change.

## 5. What is the difference between `rtol` and `atol`?

**Strong answer:** `rtol` scales the permitted difference relative to the expected magnitude, while `atol` provides an absolute tolerance that is especially important near zero.

## 6. How do you choose a tolerance?

**Strong answer:** From the numerical behavior of the computation, data scale, algorithmic error, representation precision, and business requirements. I never choose an arbitrary tolerance simply to make CI green.

## 7. Should revenue be compared with a floating-point tolerance?

**Strong answer:** Usually not when the business contract requires exact monetary semantics. I prefer decimal arithmetic or integer minor units such as cents.

## 8. Why can two timestamps represent the same instant but compare differently?

**Strong answer:** They may use different timezones, units, or textual representations. If the contract concerns instants, normalize to a common timezone and precision before comparison.

## 9. How would you debug a large DataFrame mismatch?

**Strong answer:** First validate schema and row counts, then identify missing and unexpected keys, then compare changed values by key and produce per-column mismatch summaries. For very large data, hashes and deterministic samples can narrow the investigation.

## 10. Are hashes proof of equality?

**Strong answer:** No. They are efficient fingerprints with an appropriate collision risk, useful for large-data validation. They should be paired with a strategy for detailed diagnosis.

## 11. Why are snapshots dangerous?

**Strong answer:** A snapshot can become a mechanism for approving regressions if developers blindly accept updates. Snapshot changes need intentional review.

## 12. How would you validate a pandas-to-Spark migration?

**Strong answer:** Define the logical business contract, run both implementations on controlled inputs, normalize only known representation differences, compare business outputs, and separately test engine-specific semantics.

## 13. How would you design a comparison helper?

**Strong answer:** Keep important policies explicit: ordering keys, dtype requirements, tolerance, timestamp semantics, and null semantics. The helper should improve diagnostics without silently weakening assertions.

---

# 45. Final Assessment

## Scenario

A production Data Engineering team migrated a critical transformation from pandas to Spark.

The outputs are supposed to be logically equivalent, but the team has discovered differences in:

```text
row ordering
null representation
floating-point calculations
timestamps
schema types
```

You must design and implement a comparison strategy.

## Determine

```text
What must match exactly?
What can be normalized?
What can use tolerance?
What requires business-specific rules?
What should fail?
How should failures be diagnosed?
```

## Required implementation

Your solution must include:

```text
[ ] schema validation
[ ] column validation
[ ] deterministic ordering where required
[ ] order-insensitive comparison where appropriate
[ ] explicit null semantics
[ ] numerical tolerance only where justified
[ ] exact money comparison
[ ] timestamp normalization strategy
[ ] readable row-level diff
[ ] per-column mismatch summary
[ ] large-output strategy
[ ] snapshot/golden test
[ ] reusable comparison helper
[ ] deliberate failure cases
```

### Evaluation standard

A strong solution does not merely produce:

```text
PASS
```

It explains:

```text
what equality means
why the assertion is configured this way
what differences are legitimate
what differences represent bugs
how a failure will be diagnosed
```

---

# 46. Required Coding Stack

Use:

```text
Python 3.12+
pytest
pandas
Polars
NumPy
DuckDB
PySpark
syrupy
pytest-cov
```

Do not introduce dependencies unless they solve a specific problem in the module.

Use type hints where they improve clarity.

Prefer readable production-oriented code over clever abstractions.

---

# 47. Recommended Project Structure

For this topic:

```text
tests/
├── unit/
│   ├── test_dataframe_equality.py
│   ├── test_numeric_tolerance.py
│   ├── test_timestamp_comparison.py
│   └── test_cross_engine_outputs.py
├── helpers/
│   └── dataframe_assertions.py
├── snapshots/
└── conftest.py
```

The helper should be small enough that an engineer can understand its equality policy by reading it.

---

# 48. Code Review Checklist

When reviewing a DataFrame comparison test, ask:

```text
[ ] Is the equality contract explicit?
[ ] Are required columns checked?
[ ] Are dtypes intentionally strict or relaxed?
[ ] Is row order meaningful?
[ ] If order is ignored, is sorting deterministic?
[ ] Are duplicate keys handled correctly?
[ ] Are null semantics explicit?
[ ] Are NaN semantics explicit?
[ ] Are timestamps compared according to the business contract?
[ ] Are numeric tolerances justified?
[ ] Is money compared exactly?
[ ] Could a tolerance hide a business bug?
[ ] Are large-output diagnostics available?
[ ] Are hashes canonicalized?
[ ] Are samples deterministic?
[ ] Are snapshots intentionally reviewed?
[ ] Does cross-engine normalization hide meaningful differences?
[ ] Would a realistic production bug fail this test?
```

---

# 49. Connection to Module 2.19

The testing strategy develops in this order:

```text
01 Testing transformations with fixture DataFrames
        ↓
02 DataFrame equality and tolerance assertions
        ↓
03 Integration tests with Testcontainers
        ↓
04 Property-based testing with Hypothesis
        ↓
05 Synthetic and sampled test data
        ↓
06 Schema and contract regression tests
        ↓
07 End-to-end pipeline smoke tests
```

Topic 01 teaches you how to create controlled transformation tests.

Topic 02 teaches you how to answer the next critical question:

> **Did the transformation produce the right DataFrame?**

Later topics expand the scope to real services, generated inputs, contracts, regression protection, and whole-pipeline behavior. They should not be taught in depth here.

---

# 50. Core Mental Models

### Equality

```text
same values
≠
same DataFrame
```

unless the relevant equality dimensions are also equivalent.

### Assertion strictness

```text
business contract
      ↓
required strictness
      ↓
comparison
```

### Numerical tolerance

```text
legitimate numerical error
      ↓
justified tolerance
      ↓
comparison
```

not:

```text
test failed
      ↓
make tolerance larger
```

### Large-data validation

```text
schema
+
counts
+
keys
+
hashes
+
samples
+
targeted diff
```

### Cross-engine validation

```text
physical representation
        ↓
normalize legitimate differences
        ↓
logical business comparison
```

### Failure diagnosis

```text
assertion failed
      ↓
which dimension?
      ↓
legitimate difference?
      ↓
business bug?
      ↓
fix implementation or contract
```

---

# 51. Final Mastery Checklist

```text
[ ] Fundamental definition of DataFrame equality
[ ] pandas.testing.assert_frame_equal
[ ] Polars assert_frame_equal
[ ] PySpark assertDataFrameEqual
[ ] NumPy assert_allclose
[ ] Values
[ ] Columns
[ ] Column order
[ ] Dtypes
[ ] Row order
[ ] pandas index
[ ] Strict equality
[ ] Deliberately relaxed equality
[ ] Order-insensitive comparison
[ ] Null semantics
[ ] NaN semantics
[ ] None
[ ] pd.NA
[ ] Polars null
[ ] Polars NaN
[ ] SQL NULL
[ ] Floating-point precision
[ ] rtol
[ ] atol
[ ] Computation-based tolerance
[ ] Exact money comparison
[ ] Decimal
[ ] Integer cents
[ ] Rounding bug discussion
[ ] Timestamp units
[ ] Time zones
[ ] Instant vs representation
[ ] Anti-join diffs
[ ] Per-column difference summaries
[ ] Large-output comparison
[ ] Row counts
[ ] Checksums
[ ] Hashes
[ ] Deterministic samples
[ ] Snapshot/golden testing
[ ] syrupy
[ ] Cross-engine normalization
[ ] pandas comparison
[ ] Polars comparison
[ ] DuckDB comparison
[ ] Spark comparison
[ ] Reusable assertion helpers
[ ] Failure-first examples
[ ] Common mistakes
[ ] Production scenarios
[ ] Hands-on project
[ ] Deliberate failure lab
[ ] Checkpoint
[ ] Interview preparation
[ ] Final assessment
```

---

# 52. Final Engineering Principle

The goal of a DataFrame assertion is not:

```text
make CI green
```

The goal is:

```text
make the intended data contract executable
```

A strong comparison framework distinguishes:

```text
real regression
        from
legitimate representation difference
        from
acceptable numerical noise
```

The best assertion is therefore neither the strictest possible nor the loosest possible.

It is the one that faithfully encodes the business and technical contract:

> **Strict where correctness matters, tolerant only where tolerance is mathematically and operationally justified, and diagnostic enough to explain every meaningful failure.**
