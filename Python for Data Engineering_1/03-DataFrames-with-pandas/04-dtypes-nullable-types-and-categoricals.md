# 04 — dtypes, Nullable Types, and Categoricals

> **Stage 2 — Python for Data Engineering · Module 2.3 — DataFrames with pandas**
>
> **Primary environment:** pandas 3.x, Python 3.12+
>
> **Central question:**  
> **How do I choose, validate, and enforce the right dtype for every column so that data remains correct, memory-aware, and safe for downstream Data Engineering work?**

---

## 1. Why Data Types Matter in Data Engineering

A pandas column is not just a collection of values. Its dtype affects what those values **mean**, how missing values are represented, which operations are safe, how much memory is used, and how other systems consume the result.

A production pipeline should be able to answer:

```text
What is this column?
What values are valid?
Can it be missing?
How is it represented?
What happens during conversion?
How will it sort?
How will it compare?
How will it aggregate?
How will it serialize?
How much memory will it use?
```

A dtype mistake can become a business-data mistake.

### Example: an identifier is not a measurement

Suppose a customer identifier arrives as:

```text
000123
000124
001025
```

If the parser interprets that column as an integer, the values become:

```text
123
124
1025
```

The numeric magnitude looks reasonable, but the identifier's **meaning** has changed.

That can break:

- joins against another system that preserves leading zeros
- reconciliation
- downstream API calls
- partition or key generation
- audit records

The correct question is not:

> "Can these characters be converted to a number?"

It is:

> "What does this column represent?"

### Another example: missing integer values

Imagine:

```text
customer_id
101
102
<missing>
104
```

A normal NumPy integer dtype cannot represent a missing value directly. Depending on how the data is constructed, pandas may use a floating dtype:

```text
101.0
102.0
NaN
104.0
```

That may be workable for some analytical tasks, but it is a poor semantic representation for an identifier.

Pandas provides nullable extension dtypes such as `Int64` so that an integer column can remain integer-like while supporting missing values.

### Another example: status ordering

Alphabetical sorting says:

```text
delivered
paid
pending
shipped
```

But a business lifecycle might be:

```text
pending < paid < shipped < delivered
```

An ordered categorical dtype can represent that intended domain ordering.

### Another example: timestamps

These two values are not the same kind of information:

```text
2026-01-01 10:00:00
2026-01-01 10:00:00+00:00
```

The first is timezone-naive. The second is timezone-aware.

A distributed pipeline that silently mixes naive and aware timestamps is inviting ambiguity.

### Production principle

> **A dtype is part of a data contract, not merely an implementation detail.**

---

## 2. The Dtype Mental Model

Start with a simple hierarchy:

```text
Raw source value
      ↓
Python value / parsed token
      ↓
pandas Series
      ↓
dtype
      ↓
storage / representation
      ↓
operations + missing-value semantics
```

A useful way to reason about a column is:

```text
Semantic meaning
      ↓
Allowed values
      ↓
Missing allowed?
      ↓
Representation choice
      ↓
Validation
      ↓
Measurement
```

### A dtype answers more than "what Python type is this?"

Consider:

```python
import pandas as pd

df = pd.DataFrame(
    {
        "amount": [100, 250, 900],
        "country": ["IN", "US", "GB"],
    }
)

print(df.dtypes)
print(df["amount"].dtype)
```

The Series has a pandas dtype. The DataFrame contains multiple Series-like columns, and each column can have a different dtype.

Do not confuse:

```python
type(df["amount"])
```

with:

```python
df["amount"].dtype
```

The first describes the Python/pandas object you are holding. The second describes the dtype of the values stored in that column.

### Prediction exercise

Before running the previous example, predict:

```text
Column names:
Row count:
amount dtype:
country dtype:
```

Then verify.

```python
assert list(df.columns) == ["amount", "country"]
assert len(df) == 3
print(df.dtypes)
```

The habit matters because production pipelines should not rely on visual inspection alone.

---

# 3. Default pandas dtypes

The roadmap's default-type set includes:

- `int64`
- `float64`
- `bool`
- `datetime64[ns]`
- `object`
- pandas 3's dedicated default string dtype, displayed as `str`

These are useful starting points, but **inference is not a production schema**.

| dtype | Typical values | Missing-value considerations | Typical use |
|---|---|---|---|
| `int64` | whole numbers | cannot directly carry a missing integer value | dense integer measurements |
| `float64` | real-valued numbers | `NaN` is natural | measurements, calculations |
| `bool` | `True` / `False` | not a three-state nullable boolean | flags when missing is impossible |
| `datetime64[ns]` | timestamps | `NaT` can represent missing time | time values in common range |
| `object` | arbitrary Python objects | representation varies | legacy/mixed values, `Decimal`, arbitrary objects |
| `str` | text in pandas 3 default string dtype | pandas 3 default string uses its modern string representation | text columns |

The exact dtype a newly created or read DataFrame gets depends on the values, construction method, and options.

## Important production rule

> **Inspect inferred dtypes, then decide whether they are semantically correct.**

---

# 4. `object` dtype — Why It Requires Special Attention

`object` is a flexible container. It is not a semantic declaration saying:

> "this column contains strings."

An object-backed column can contain arbitrary Python objects.

For example:

```python
import pandas as pd
from decimal import Decimal

df = pd.DataFrame(
    {
        "value": ["10", "20", 30, None],
        "money": [Decimal("10.00"), Decimal("20.50"), Decimal("5.25"), None],
    }
)

print(df.dtypes)
```

The `value` column contains mixed Python types:

```text
"10"  → str
"20"  → str
30    → int
None  → NoneType
```

That is a data-quality smell when the intended semantic type is "numeric."

### Why mixed object columns are dangerous

A mixed object column can hide:

- strings that look numeric
- numbers mixed with strings
- Python `Decimal`
- `None`
- custom objects
- inconsistent source-system values

The column may look acceptable when printed but behave differently during sorting, comparison, arithmetic, or serialization.

### Incorrect production assumption

```text
dtype == object
therefore
column == string
```

This is wrong.

### Better reasoning

```text
object
  ↓
inspect actual values
  ↓
determine semantic type
  ↓
convert explicitly
  ↓
measure conversion failures
  ↓
validate final dtype
```

### Production rule

> **Never treat `object` as a complete schema definition.**

---

# 5. pandas 3's Default String dtype

Pandas 3 introduced a dedicated string dtype as the default representation for string data. The official pandas 3 migration documentation describes this as a move away from using generic NumPy `object` for ordinary strings. citeturn980602search3turn980602search8

This matters because `object` is not specific to strings.

A useful conceptual comparison is:

```text
object
→ generic Python-object container

str
→ pandas 3 dedicated default string dtype
```

### Why dedicated strings are useful

A declared string column communicates intent more clearly:

```python
order_ids = pd.Series(["0001", "0002", "0003"], dtype="str")
```

The column is now explicitly text.

### Important distinction: `str` versus `string`

Modern pandas has more than one string-related representation.

For production code, distinguish:

```text
"str"
→ pandas 3 default string dtype

"string"
→ pandas' nullable StringDtype
```

The roadmap specifically asks you to compare `object`, `str`, and `string`. Do not assume they have identical missing-value behavior.

Pandas 3's default string dtype uses `NaN` as its missing indicator for consistency with other default dtypes, while the older nullable `StringDtype` continues to use `pd.NA`. citeturn980602search3

Example:

```python
default_strings = pd.Series(["IN", "US", None], dtype="str")
nullable_strings = pd.Series(["IN", "US", None], dtype="string")

print(default_strings.dtype)
print(nullable_strings.dtype)
print(default_strings)
print(nullable_strings)
```

The important engineering lesson is not memorizing display details.

It is:

> **Know which string dtype your pipeline intends to use, and test its missing-value semantics.**

---

# 6. Inspecting dtypes

Before changing a schema, inspect the current state.

## `df.dtypes`

```python
import pandas as pd

df = pd.DataFrame(
    {
        "order_id": ["001", "002"],
        "quantity": [2, 5],
        "is_gift": [True, False],
    }
)

print(df.dtypes)
```

This is the first broad schema inspection.

## `df["column"].dtype`

```python
print(df["quantity"].dtype)
```

Use this when validating one column.

## `df.info()`

```python
df.info()
```

`info()` gives a compact view of:

- columns
- non-null counts
- dtypes
- DataFrame size information

For deeper memory work, later use:

```python
df.memory_usage(deep=True)
```

### Data-type audit pattern

Create a schema-review table mentally or explicitly:

| Column | Current dtype | Intended meaning | Problem? | Action |
|---|---|---|---|---|
| `order_id` | `object` / `str` | identifier | maybe | preserve as string |
| `quantity` | `object` | integer | yes | convert safely |
| `country` | `str` | low-cardinality label | maybe | consider category |
| `created_at` | `object` | timestamp | yes | parse |
| `is_gift` | `object` | boolean with possible unknown | maybe | nullable boolean |

This is how dtype management starts becoming Data Engineering rather than "pandas syntax."

---

# 7. `astype()`

`astype()` performs dtype conversion when the requested conversion is valid.

```python
import pandas as pd

quantity = pd.Series(["1", "2", "3"], dtype="str")
converted = quantity.astype("int64")

print(converted)
print(converted.dtype)
```

Expected semantic result:

```text
1
2
3
dtype: int64
```

### When `astype()` works well

Use it when:

- the values are already clean enough
- the desired dtype is known
- failure should be explicit
- you have already validated the input

### Example

```python
df = pd.DataFrame({"quantity": ["2", "5", "7"]})
df["quantity"] = df["quantity"].astype("int64")

assert str(df["quantity"].dtype) == "int64"
```

### When `astype()` fails

Consider:

```python
df = pd.DataFrame({"quantity": ["2", "bad", "7"]})

df["quantity"] = df["quantity"].astype("int64")
```

This should fail rather than silently invent a number for `"bad"`.

That failure is valuable information.

### Production rule

> **Do not use `astype()` as a substitute for understanding dirty input.**

For messy data, first identify invalid values and choose a policy.

---

# 8. Safe Numeric Conversion with `pd.to_numeric()`

For source values that need parsing, `pd.to_numeric()` is often a better foundation.

```python
import pandas as pd

raw = pd.Series(["100", "250", "bad", "500"], dtype="str")

converted = pd.to_numeric(raw, errors="coerce")

print(converted)
print(converted.dtype)
```

Conceptually:

```text
"100" → 100
"250" → 250
"bad" → missing
"500" → 500
```

The critical point is that:

```python
errors="coerce"
```

does not mean "the data is now clean."

It means:

> values that cannot be parsed are converted to a missing representation.

### Production conversion pattern

```python
raw = pd.Series(["100", "250", "bad", "500"], dtype="str")

converted = pd.to_numeric(raw, errors="coerce")

failed_mask = raw.notna() & converted.isna()
failed_count = int(failed_mask.sum())
failed_values = raw.loc[failed_mask]

print("failed_count:", failed_count)
print("failed_values:", failed_values.tolist())

if failed_count:
    print("Investigate or quarantine failed source values.")
```

The exact remediation depends on the source contract.

### Why this matters

Blind coercion turns:

```text
bad source data
```

into:

```text
missing data
```

Those are not necessarily equivalent.

---

# 9. Safe Datetime Conversion with `pd.to_datetime()`

Datetime columns deserve the same contract-based discipline.

A common pattern is:

```python
import pandas as pd

raw = pd.Series(
    [
        "2025-01-01 10:00:00",
        "2025-01-02 11:30:00",
        "invalid",
    ],
    dtype="str",
)

parsed = pd.to_datetime(
    raw,
    format="%Y-%m-%d %H:%M:%S",
    errors="coerce",
    utc=True,
)

print(parsed)
print(parsed.dtype)
```

The important options are:

```text
format=
→ how the source string is written

errors="coerce"
→ invalid values become missing timestamps

utc=True
→ normalize timezone handling to UTC
```

Pandas documents that `utc=True` localizes timezone-naive inputs as UTC and converts timezone-aware inputs to UTC; it is also useful when inputs contain mixed timezone-awareness. citeturn980602search7

### Count parsing failures

```python
failed_mask = raw.notna() & parsed.isna()
failed_count = int(failed_mask.sum())

assert failed_count == 1
print(raw.loc[failed_mask].tolist())
```

### Production principle

> **Timestamp parsing is schema enforcement, not cosmetic formatting.**

---

# 10. Why Explicit Datetime Parsing Matters

Consider:

```text
01/02/2026
```

Without a source contract, a reader may not know whether this means:

```text
1 February 2026
```

or:

```text
January 2 2026
```

When a source format is known, state it.

```python
parsed = pd.to_datetime(
    raw,
    format="%d/%m/%Y",
    errors="coerce",
    utc=True,
)
```

This improves:

- reproducibility
- correctness
- debugging
- performance in many parsing scenarios
- source-contract clarity

Do not encourage a production pipeline to "guess" its way through ambiguous dates.

---

# 11. Nullable Extension Types

Pandas provides nullable extension dtypes including:

```text
Int64
Float64
boolean
string
```

The capital `I` in:

```text
Int64
```

is significant.

Compare:

```text
int64
```

with:

```text
Int64
```

They are not the same dtype.

The same pattern appears in:

```text
float64  vs  Float64
bool     vs  boolean
```

These extension dtypes are designed to support missing values while preserving a clearer semantic dtype. Pandas documents nullable integer, floating, boolean, and string representations as extension types. citeturn980602search5

---

# 12. `int64` vs `Int64`

This distinction is one of the most important concepts in the module.

## Standard NumPy-style integer dtype

```python
import pandas as pd

dense = pd.Series([1, 2, 3], dtype="int64")

print(dense)
print(dense.dtype)
```

Every element is an integer.

Now try:

```python
mixed = pd.Series([1, 2, None])

print(mixed)
print(mixed.dtype)
```

Because a normal NumPy integer array cannot represent `None` as an integer element, pandas commonly falls back to a floating representation for this construction.

You may see:

```text
1.0
2.0
NaN
dtype: float64
```

## Nullable `Int64`

```python
nullable = pd.Series([1, 2, None], dtype="Int64")

print(nullable)
print(nullable.dtype)
```

Conceptually:

```text
1
2
<NA>
dtype: Int64
```

### Why `Int64` exists

You can preserve:

```text
integer semantics
+
missing values
```

without changing the semantic dtype to floating point.

### Data Engineering example

```python
customers = pd.DataFrame(
    {
        "customer_id": pd.Series([1001, 1002, None], dtype="Int64"),
        "quantity": pd.Series([2, None, 5], dtype="Int64"),
    }
)

print(customers.dtypes)
```

This is usually clearer than carrying identifiers as floating point numbers.

### Production rule

> **If an integer column is allowed to be missing, explicitly evaluate a nullable integer dtype such as `Int64`.**

---

# 13. `float64` vs `Float64`

The distinction is parallel to integers.

```python
standard_float = pd.Series([1.5, 2.5, None], dtype="float64")
nullable_float = pd.Series([1.5, 2.5, None], dtype="Float64")

print(standard_float.dtype)
print(nullable_float.dtype)
```

Both can represent missing information, but the missing-value semantics and extension-array behavior differ.

### When this distinction matters

A pipeline may require:

```text
nullable extension semantics
```

for consistency with:

- nullable integers
- nullable booleans
- nullable strings
- Arrow-backed workflows

Do not choose `Float64` automatically. Choose it when the schema and downstream operations benefit from the extension representation.

---

# 14. `bool` vs `boolean`

A normal boolean has two states:

```text
True
False
```

But real source data may contain three logical states:

```text
True
False
Unknown
```

For example:

```text
is_verified
-----------
True
False
<missing>
```

Use the nullable boolean dtype when "unknown" is meaningfully different from False.

```python
flags = pd.Series(
    [True, False, None],
    dtype="boolean",
)

print(flags)
print(flags.dtype)
```

### Why this matters

Suppose:

```text
False = customer explicitly failed verification
missing = source did not report verification status
```

Replacing missing with `False` changes the business meaning.

### Production principle

> **Do not collapse "unknown" into False unless the source contract says they are equivalent.**

---

# 15. Nullable Strings

A nullable string dtype can be explicitly requested:

```python
labels = pd.Series(
    ["IN", "US", None],
    dtype="string",
)

print(labels)
print(labels.dtype)
```

The important semantic point is that nullable string data has dedicated missing-value handling rather than relying on arbitrary Python objects.

### Compare representations

```text
object
→ generic object container

str
→ pandas 3 default string dtype

string
→ pandas nullable StringDtype
```

Treat the chosen representation as a schema decision.

---

# 16. `pd.NA` vs `np.nan` vs `None`

Three missing-value markers commonly appear in pandas work:

```python
pd.NA
```

```python
import numpy as np
np.nan
```

```python
None
```

They have different origins and can interact differently with dtypes.

| Marker | Origin | Common context | Key idea |
|---|---|---|---|
| `pd.NA` | pandas missing scalar | nullable extension dtypes | missing value with pandas nullable semantics |
| `np.nan` | IEEE floating-point NaN | NumPy floating data | a special floating-point value |
| `None` | Python null object | object-like data, input values | Python-level absence |

### Example

```python
import numpy as np
import pandas as pd

values = pd.Series([pd.NA, np.nan, None], dtype="object")

print(values)
print(values.isna())
```

All three can be recognized as missing by pandas' missing-data machinery in appropriate contexts, but they are not the same scalar and should not be treated as interchangeable in every operation.

Pandas' missing-data documentation describes `NA` as the missing indicator used by several extension dtypes, while `NaN` remains the floating-point "not a number" representation. citeturn980602search5turn980602search10

### Important production lesson

> **Missingness is a semantic concept; the marker is part of the representation.**

---

# 17. Three-Valued Logic with `pd.NA`

Nullable booleans introduce three logical states:

```text
True
False
Unknown
```

This is different from ordinary two-valued Boolean logic.

Pandas documents examples such as:

```python
import pandas as pd

print(pd.NA | True)
print(pd.NA & True)
print(pd.NA | False)
print(pd.NA & False)
```

The important truth-table intuition is:

| Expression | Meaning |
|---|---|
| `NA | True` | True is already enough to make OR true |
| `NA & True` | still unknown |
| `NA | False` | still unknown |
| `NA & False` | False is already enough to make AND false |

Pandas documents this as part of `pd.NA` semantics. citeturn980602search10

### Think in three states

```text
True
False
Unknown
```

This matters in production filters.

Suppose:

```text
is_verified
-----------
True
False
<NA>
```

The `<NA>` row does not mean:

```text
False
```

It means:

```text
not known
```

### Prediction exercise

Before execution, predict:

```python
pd.NA | True
pd.NA & True
pd.NA | False
pd.NA & False
```

Then verify.

---

# 18. Missing Values in Boolean Filters

A nullable boolean Series can contain:

```text
True
False
<NA>
```

Consider:

```python
import pandas as pd

df = pd.DataFrame(
    {
        "order_id": ["A", "B", "C"],
        "approved": pd.Series([True, False, None], dtype="boolean"),
    }
)

print(df)
print(df["approved"])
```

A production engineer must ask:

> What should "unknown approval status" mean for this particular operation?

Sometimes the right policy is:

```text
keep only explicitly approved rows
```

Sometimes the correct policy is:

```text
quarantine unknown approvals
```

Sometimes:

```text
treat missing as False
```

is valid—but only if the domain contract explicitly says so.

Do not let dtype mechanics silently define your business rule.

---

# 19. `convert_dtypes()`

`convert_dtypes()` helps migrate a DataFrame toward more appropriate nullable dtypes.

```python
import pandas as pd

df = pd.DataFrame(
    {
        "customer_id": [101, 102, None],
        "active": [True, False, None],
        "name": ["A", "B", None],
    }
)

converted = df.convert_dtypes()

print(converted)
print(converted.dtypes)
```

It can be useful after exploratory reads where inference produced less desirable dtypes.

### Why it exists

A convenient workflow is:

```text
read
  ↓
inspect
  ↓
convert_dtypes()
  ↓
inspect again
```

### Why it is not a complete production schema

`convert_dtypes()` makes general-purpose dtype improvements; it does not know your business contract.

For example:

```text
customer_id
```

might need:

```text
Int64
```

while:

```text
country
```

might need:

```text
category
```

and:

```text
status
```

might need a particular ordered category.

A production pipeline usually benefits from an explicit schema in addition to generic conversion.

---

# 20. `dtype_backend=`

Modern pandas supports choosing the backend used for dtype representation in operations such as supported I/O and conversion APIs.

Two important values are:

```python
dtype_backend="numpy_nullable"
```

and:

```python
dtype_backend="pyarrow"
```

Pandas documents these backend choices for DataFrame-returning APIs: `"numpy_nullable"` produces nullable-dtype-backed data and `"pyarrow"` produces PyArrow-backed nullable data. citeturn980602search0turn980602search2turn980602search4

### Semantic dtype versus storage/backend representation

Think in two layers:

```text
What does the column mean?
        ↓
semantic dtype

How is that column represented?
        ↓
backend/storage model
```

For example:

```text
customer_id
→ nullable integer semantics

backend
→ pandas nullable representation
or
→ Arrow-backed representation
```

Do not confuse those layers.

### When `numpy_nullable` is useful

It can be a sensible choice when:

- you want pandas nullable dtypes
- NumPy-oriented interoperability is important
- you want predictable pandas extension semantics

### When `pyarrow` is useful

It can be useful when:

- Arrow interoperability matters
- nullable columnar representations are valuable
- other parts of the pipeline use Arrow
- the actual workload benefits from that representation

### Production rule

> **Backend selection is a workload decision, not a universal optimization.**

---

# 21. Categoricals — Why They Exist

A categorical column is useful when values repeat from a relatively small vocabulary.

Example:

```text
country
-------
IN
IN
US
IN
GB
US
```

There are six rows but only three distinct categories:

```text
IN
US
GB
```

A categorical representation can conceptually use:

```text
categories:
[GB, IN, US]

codes:
[1, 1, 2, 1, 0, 2]
```

The exact category ordering is implementation detail; the useful mental model is:

```text
repeated labels
      ↓
category vocabulary
      +
codes referring to the vocabulary
```

### Inspect categories

```python
import pandas as pd

countries = pd.Series(
    ["IN", "IN", "US", "IN", "GB", "US"],
    dtype="category",
)

print(countries.cat.categories)
print(countries.cat.codes)
```

### Why this can help

If a column has many repeated values and relatively few unique values, a categorical representation can reduce repeated storage and may make certain operations more efficient.

But it is not automatically the right choice.

---

# 22. What Does "Low Cardinality" Mean?

Cardinality means:

> **How many distinct values are present.**

Suppose there are 1,000,000 rows.

### Low cardinality

```text
country → 20 distinct values
```

Very low relative to row count.

### Moderate cardinality

```text
department → 500 distinct values
```

Potentially useful depending on workload.

### High cardinality

```text
order_id → 1,000,000 distinct values
```

Almost every row is unique.

### Why cardinality matters

Categoricals are most attractive when:

```text
number of rows
≫
number of distinct values
```

For unique IDs or free text, category may provide little benefit and can add complexity.

---

# 23. When `category` Is a Good Choice

Good candidates often include:

```text
country
region
status
channel
device_type
business_segment
```

when the vocabulary is:

- relatively small
- reused heavily
- stable enough to be meaningful

Example:

```python
df["country"] = df["country"].astype("category")
```

### Measure instead of guessing

```python
before = df.memory_usage(deep=True).sum()

df["country"] = df["country"].astype("category")

after = df.memory_usage(deep=True).sum()

print("before:", before)
print("after:", after)
```

The result depends on data characteristics, so measure the actual dataset.

---

# 24. When `category` Is a Poor Choice

Be careful with:

```text
UUID
unique transaction ID
unique URL
free-text description
```

If almost every value is distinct, a category vocabulary can become almost as large as the data itself.

That weakens the main reason to use categorical encoding.

### Production rule

> **Use category because the data has suitable semantics and cardinality—not simply because category sounds memory-efficient.**

---

# 25. Ordered Categoricals

A categorical can represent an explicit business ordering.

Consider:

```text
pending
paid
shipped
delivered
```

The desired lifecycle is:

```text
pending < paid < shipped < delivered
```

An alphabetical sort would not reliably express that business meaning.

Define an ordered categorical:

```python
import pandas as pd

status_order = [
    "pending",
    "paid",
    "shipped",
    "delivered",
]

status = pd.Series(
    ["delivered", "pending", "paid", "shipped"],
    dtype=pd.CategoricalDtype(
        categories=status_order,
        ordered=True,
    ),
)

print(status.sort_values())
```

The sort now follows the declared business order.

### Why `ordered=True` matters

Without ordered semantics, you have a set of labels.

With ordered semantics, you are defining a meaningful relation among them.

That can make comparisons such as:

```python
status >= "paid"
```

meaningful for the categorical dtype, provided the categories are properly defined and comparable.

### Production caution

The category order is a **business rule**.

Document it and test it.

---

# 26. Adding and Removing Categories

Categorical metadata is separate from simply looking at the currently visible values.

## Add a category

```python
import pandas as pd

status = pd.Series(
    ["pending", "paid"],
    dtype=pd.CategoricalDtype(
        categories=["pending", "paid"],
        ordered=True,
    ),
)

status = status.cat.add_categories(["cancelled"])

print(status.cat.categories)
```

Use this when a legitimate new state becomes part of the domain.

## Remove unused categories

After filtering or transformation, category metadata may contain values that no longer appear.

```python
countries = pd.Series(
    ["IN", "US", "GB"],
    dtype="category",
)

filtered = countries.loc[countries != "GB"]

print(filtered.cat.categories)

filtered = filtered.cat.remove_unused_categories()

print(filtered.cat.categories)
```

### Why this matters

Unused categories can:

- confuse inspection
- affect categorical operations
- matter to grouping behavior
- keep outdated domain metadata around

Do not remove categories blindly when they are intentionally part of a shared schema; remove them when the pipeline wants the category vocabulary to represent the current data.

---

# 27. Categoricals and `groupby(..., observed=True)`

Categorical columns have an important grouping behavior.

Suppose:

```python
import pandas as pd

df = pd.DataFrame(
    {
        "country": pd.Series(
            ["IN", "IN", "US"],
            dtype=pd.CategoricalDtype(
                categories=["IN", "US", "GB"]
            ),
        ),
        "revenue": [100, 200, 300],
    }
)
```

The category vocabulary contains:

```text
IN
US
GB
```

but the current data contains no `GB`.

When grouping categorical data, use:

```python
grouped = (
    df.groupby("country", observed=True)["revenue"]
    .sum()
)

print(grouped)
```

`observed=True` tells pandas to work with combinations actually observed in the data rather than materializing unused categorical levels.

### Why this matters

It is a dtype-specific data-shape consideration.

The general production lesson is:

> **Category metadata can affect downstream grouping semantics, so validate group behavior instead of assuming it is identical to string grouping.**

Do not turn this into a full `groupby` tutorial; that belongs to Topic 06.

---

# 28. PyArrow-Backed dtypes

PyArrow-backed pandas columns provide another representation option.

You may encounter dtypes such as:

```text
int64[pyarrow]
string[pyarrow]
timestamp[us, tz=UTC][pyarrow]
```

Pandas documents Arrow-backed extension arrays as being backed by PyArrow arrays rather than NumPy arrays. citeturn980602search6

### Conceptual model

```text
Pandas DataFrame
        ↓
Arrow-backed column
        ↓
PyArrow array / type
```

This can be useful for:

- interoperability
- nullable data
- columnar memory representations
- cross-tool data exchange

### Example

When PyArrow is installed:

```python
import pandas as pd
import pyarrow as pa

arrow_int = pd.Series(
    [1, 2, None],
    dtype=pd.ArrowDtype(pa.int64()),
)

arrow_text = pd.Series(
    ["IN", "US", None],
    dtype=pd.ArrowDtype(pa.string()),
)

print(arrow_int.dtype)
print(arrow_text.dtype)
```

The exact displayed dtype depends on the pandas/PyArrow versions in use, so test your production environment.

---

# 29. NumPy-Nullable vs Arrow-Backed Types

These are related but different representation choices.

| Concern | NumPy nullable | Arrow-backed |
|---|---|---|
| Main idea | pandas extension dtypes with nullable semantics | pandas columns backed by Arrow arrays |
| Missing values | supported | first-class nullable Arrow representation |
| Interoperability | strong with pandas/NumPy-oriented code | strong with Arrow ecosystem |
| Backend | pandas extension / NumPy-oriented representation | PyArrow |
| Performance | workload-dependent | workload-dependent |
| Memory | workload- and data-dependent | workload- and data-dependent |
| API coverage | mature pandas support | coverage depends on pandas/PyArrow operation |
| Best choice | depends on pipeline | depends on pipeline |

Pandas describes PyArrow-backed types as providing data type support similar to NumPy plus first-class nullability and other properties, while marking the feature as experimental in current documentation. citeturn980602search6

### Important principle

Do not say:

```text
Arrow is always faster.
```

or:

```text
Arrow always uses less memory.
```

Instead:

```text
What is the workload?
What are the consumers?
What operations are needed?
What is the measured memory?
What is the measured runtime?
```

---

# 30. Arrow dtype Examples

## `int64[pyarrow]`

Conceptually:

```python
import pandas as pd
import pyarrow as pa

s = pd.Series(
    [10, 20, None],
    dtype=pd.ArrowDtype(pa.int64()),
)

print(s.dtype)
```

This means:

```text
semantic values → integer
backend → PyArrow
nullability → supported
```

## `string[pyarrow]`

```python
s = pd.Series(
    ["IN", "US", None],
    dtype=pd.ArrowDtype(pa.string()),
)

print(s.dtype)
```

## Arrow timestamp

```python
timestamp_dtype = pd.ArrowDtype(
    pa.timestamp("us", tz="UTC")
)

s = pd.Series(
    [
        "2025-01-01T00:00:00Z",
        None,
    ],
    dtype="string[pyarrow]",
)

parsed = pd.to_datetime(
    s,
    utc=True,
)

print(parsed)
```

The precise dtype shown after a conversion depends on the conversion path and environment. Verify it rather than hard-coding an assumption.

---

# 31. Timezone-Aware Datetimes

A timezone-aware timestamp contains timezone information.

A common pandas representation is:

```text
datetime64[ns, UTC]
```

A timezone-naive timestamp does not carry timezone information:

```text
datetime64[ns]
```

### Why the distinction matters

Suppose two source systems report:

```text
System A: 10:00 UTC
System B: 10:00 Asia/Kolkata
```

These are not the same instant.

Production pipelines should establish an intentional timezone strategy.

A common convention is:

```text
ingest
  ↓
parse
  ↓
normalize to UTC
  ↓
store/process
  ↓
convert only for presentation where needed
```

### Example

```python
import pandas as pd

raw = pd.Series(
    [
        "2025-01-01 10:00:00",
        "2025-01-01 11:00:00",
    ],
    dtype="str",
)

timestamps = pd.to_datetime(
    raw,
    format="%Y-%m-%d %H:%M:%S",
    utc=True,
)

print(timestamps)
print(timestamps.dtype)
```

### Production principle

> **Choose a timezone convention deliberately; do not let source-system ambiguity decide for you.**

---

# 32. Timestamp Resolution: `s`, `ms`, `us`, `ns`

Timestamp resolution answers:

> How finely can each timestamp be represented?

Common units are:

```text
s  → seconds
ms → milliseconds
us → microseconds
ns → nanoseconds
```

### Why this matters

Higher resolution does not mean universally better.

Consider:

```text
source emits milliseconds
```

There may be no benefit in forcing nanosecond precision.

Conversely, a scientific or high-frequency system may genuinely require microsecond or nanosecond detail.

### Resolution affects range

A finer fixed-width timestamp representation can have a smaller supported range than a coarser one, depending on the representation and backend.

That means the question is not simply:

```text
"Which unit is most precise?"
```

It is:

```text
What precision does the source provide?
What precision does the consumer need?
What date range must be supported?
What representation does the backend use?
```

Pandas' datetime APIs can display different timestamp resolutions in modern versions, so production code should test the actual target environment. citeturn980602search7

---

# 33. Out-of-Bounds Timestamps

A source can contain values outside the range supported by a chosen datetime representation.

For example:

```text
very old historical date
very far-future date
```

may not fit safely into the selected nanosecond representation.

### Debugging pattern

```python
import pandas as pd

raw = pd.Series(
    [
        "2025-01-01",
        "not-a-date",
    ],
    dtype="str",
)

parsed = pd.to_datetime(
    raw,
    format="%Y-%m-%d",
    errors="coerce",
    utc=True,
)

print(parsed)
```

For a real out-of-range dataset, first identify the failing values, then choose an appropriate strategy.

Do not silently:

```text
clip
truncate
replace with a random date
```

unless the source contract explicitly specifies that behavior.

---

# 34. Money and Exact Numeric Semantics

Money deserves explicit representation choices.

The roadmap requires comparison of:

1. Python `Decimal` in an `object` column
2. integer cents
3. Arrow `decimal128`

These are different tools for different contexts.

## Option 1 — `Decimal`

```python
from decimal import Decimal
import pandas as pd

amounts = pd.Series(
    [
        Decimal("19.99"),
        Decimal("12.50"),
        None,
    ],
    dtype="object",
)

print(amounts)
print(amounts.dtype)
```

`Decimal` provides decimal arithmetic semantics in Python, but an object column carries Python objects and has different performance/interoperability characteristics from compact native numeric arrays.

## Option 2 — Integer cents

Represent:

```text
₹19.99
```

as:

```text
1999
```

Example:

```python
amount_cents = pd.Series(
    [1999, 1250, None],
    dtype="Int64",
)

print(amount_cents)
```

Advantages include:

- exact scaled-integer representation
- clear arithmetic semantics for fixed minor units
- convenient nullable integer support

Trade-off:

- the scale is a business/schema rule
- currencies can have different minor-unit conventions

## Option 3 — Arrow `decimal128`

Arrow provides fixed-precision decimal types such as decimal128, which can be useful when interoperating with systems that support decimal semantics.

The representation is more explicitly decimal than binary floating point.

### Comparison

| Representation | Exact decimal semantics | Nullable | Main trade-off |
|---|---|---|---|
| `Decimal` objects | Yes | Yes via object missing values | Python-object overhead/interoperability |
| integer cents | Yes for a fixed scale | Yes with `Int64` | scale must be explicit |
| Arrow decimal128 | Yes within declared precision/scale | Yes | backend/API compatibility must be tested |
| binary float | No exact decimal representation in general | Yes | convenient but can introduce rounding surprises |

### Why ordinary float is risky for canonical money

Binary floating point cannot represent many decimal fractions exactly.

For example:

```python
print(0.1 + 0.2)
```

The familiar result is not exactly mathematical `0.3`.

The engineering question is:

> **Is this approximate numeric representation acceptable for this field?**

For exact monetary storage, make the representation deliberate.

---

# 35. Semantic Type vs Physical Representation

At this point, distinguish three layers:

```text
Business meaning
       ↓
pandas semantic dtype
       ↓
backend/storage representation
```

Example:

```text
customer_id
    ↓
nullable integer
    ↓
pandas Int64
```

Another example:

```text
country
    ↓
low-cardinality categorical label
    ↓
category codes + vocabulary
```

Another:

```text
revenue
    ↓
exact monetary value
    ↓
integer cents / Decimal / Arrow decimal
```

Another:

```text
created_at
    ↓
UTC timestamp
    ↓
datetime64[...] or Arrow timestamp
```

A good Data Engineer can explain all three layers.

---

# 36. Schema Enforcement

An explicit schema turns assumptions into executable rules.

Consider an orders dataset:

```python
SCHEMA = {
    "order_id": "string",
    "customer_id": "Int64",
    "quantity": "Int16",
    "amount_cents": "Int64",
    "country": "category",
    "status": "category",
    "created_at": "datetime64[ns, UTC]",
    "is_gift": "boolean",
}
```

The exact status category definition is separate because it needs an explicit category vocabulary and order.

### Why schema enforcement matters

Without a declared schema:

```text
source changes
   ↓
inference changes
   ↓
dtype changes
   ↓
downstream behavior changes
```

With a schema:

```text
source changes
   ↓
conversion/validation
   ↓
pipeline detects drift
   ↓
explicit decision
```

### Applying a schema

For compatible columns, `astype()` can be used:

```python
df["order_id"] = df["order_id"].astype("string")
df["customer_id"] = df["customer_id"].astype("Int64")
df["quantity"] = df["quantity"].astype("Int16")
df["amount_cents"] = df["amount_cents"].astype("Int64")
df["country"] = df["country"].astype("category")
df["is_gift"] = df["is_gift"].astype("boolean")
```

Datetime conversion should generally be handled with `pd.to_datetime()` rather than treating it as an ordinary string-to-dtype cast.

---

# 37. `validate_schema(df, schema)`

A lightweight schema validator can catch structural problems early.

A practical design:

```python
from collections.abc import Mapping
import pandas as pd


def validate_schema(
    df: pd.DataFrame,
    schema: Mapping[str, str],
) -> None:
    expected_columns = list(schema)
    actual_columns = list(df.columns)

    missing = [c for c in expected_columns if c not in actual_columns]
    unexpected = [c for c in actual_columns if c not in schema]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if unexpected:
        raise ValueError(f"Unexpected columns: {unexpected}")

    for column, expected_dtype in schema.items():
        actual_dtype = str(df[column].dtype)

        if actual_dtype != expected_dtype:
            raise TypeError(
                f"{column}: expected {expected_dtype!r}, "
                f"got {actual_dtype!r}"
            )
```

### Important limitation

This is intentionally lightweight.

It does not attempt to become a complete enterprise contract system.

It teaches the foundation:

```text
expected schema
+
actual schema
→
explicit comparison
```

Later validation modules can provide richer checks.

---

# 38. Schema Drift

Schema drift means the source changes in a way that affects pipeline expectations.

Examples:

```text
customer_id
```

was:

```text
integer-like
```

and suddenly arrives as:

```text
"unknown"
```

Or:

```text
created_at
```

was:

```text
YYYY-MM-DD
```

and now appears as:

```text
DD/MM/YYYY
```

Or:

```text
country
```

gains an unexpected code.

A schema-aware pipeline should make these changes visible.

### Production rule

> **A conversion error is often a source-system signal, not merely a parsing inconvenience.**

---

# 39. Data-Type Conversion Failure Analysis

Consider raw values:

```text
"100"
"250"
"bad"
""
"unknown"
"2025-01-01"
"31/13/2025"
```

Do not immediately label all failures as "missing."

Classify values into:

```text
valid
missing
malformed
unexpected
out-of-range
ambiguous
```

### Numeric example

```python
import pandas as pd

raw = pd.Series(
    ["100", "250", "bad", ""],
    dtype="str",
)

converted = pd.to_numeric(
    raw,
    errors="coerce",
)

print(converted)
```

Now identify the values that failed conversion.

```python
failed_mask = raw.notna() & converted.isna()
failed_values = raw.loc[failed_mask]

print(failed_values.tolist())
```

### Production choices

Depending on source contracts, failed values might be:

```text
fail the batch
warn and continue
quarantine records
retain raw and produce a null parsed value
```

The dtype conversion API does not decide the business policy for you.

---

# 40. Measuring Memory with `memory_usage(deep=True)`

Dtype decisions should be measured.

```python
memory_by_column = df.memory_usage(deep=True)
print(memory_by_column)
```

Total:

```python
total_bytes = df.memory_usage(deep=True).sum()
print(total_bytes)
```

### Why `deep=True` matters

For object-like data, the shallow DataFrame accounting does not necessarily capture the cost of referenced Python objects in the way you need for a realistic comparison.

Use:

```python
df.memory_usage(deep=True)
```

when comparing text-heavy representations.

### Example

```python
import pandas as pd

countries = ["IN", "US", "GB"] * 10_000

df = pd.DataFrame({"country": countries})

before = df.memory_usage(deep=True).sum()

df["country"] = df["country"].astype("category")

after = df.memory_usage(deep=True).sum()

print("before:", before)
print("after:", after)
```

Do not make a universal statement such as:

```text
category always wins.
```

The data distribution determines the result.

---

# 41. Practical Memory Experiment

Create three representations of repeated labels:

```python
import pandas as pd

values = ["IN", "US", "GB", "IN", "US"] * 20_000

object_df = pd.DataFrame({"country": pd.Series(values, dtype="object")})
string_df = pd.DataFrame({"country": pd.Series(values, dtype="string")})
category_df = pd.DataFrame({"country": pd.Series(values, dtype="category")})

memory = pd.DataFrame(
    {
        "representation": ["object", "string", "category"],
        "bytes": [
            object_df.memory_usage(deep=True).sum(),
            string_df.memory_usage(deep=True).sum(),
            category_df.memory_usage(deep=True).sum(),
        ],
    }
)

print(memory)
```

### Questions to answer

Before running:

```text
Which will use the most memory?
Which will use the least?
Why?
What changes if every value is unique?
```

Then measure.

This teaches the right habit:

> **Dtype optimization is a measurement problem.**

---

# 42. dtype Decision Framework

For every production column, ask:

```text
1. What values does this column contain?
2. What does the column mean?
3. Can it be missing?
4. Is it numeric, text, boolean, datetime, category, or money?
5. How many distinct values does it contain?
6. Does ordering matter?
7. Does exact numeric representation matter?
8. Does timezone matter?
9. What timestamp range is required?
10. Which downstream systems consume it?
11. How much memory does the representation use?
12. What should happen when conversion fails?
13. How will this dtype be validated?
14. Is the choice reproducible?
```

### Example decision table

| Semantic field | Typical target | Why |
|---|---|---|
| identifier with leading zeros | `string` | preserves representation |
| nullable whole number | `Int64` / suitable nullable integer | keeps integer semantics with missing |
| nullable measurement | `Float64` when nullable extension semantics are useful | explicit missing-aware numeric type |
| three-state flag | `boolean` | distinguishes unknown from False |
| low-cardinality label | `category` | vocabulary + codes can reduce repeated storage |
| ordered lifecycle | ordered `category` | encodes business order |
| timestamp | timezone-aware datetime | preserves temporal meaning |
| exact fixed-scale money | `Int64` cents / Decimal / Arrow decimal | deliberate exactness |
| free text | `str` / `string` | textual semantics |
| cross-tool nullable column | Arrow-backed dtype when appropriate | interoperability |

No row is a universal rule. The source contract and downstream requirements decide.

---

# 43. Data Engineering Scenario — Orders Ingestion

Suppose raw orders arrive as strings:

```text
order_id       customer_id quantity amount_cents country status created_at                 is_gift
000001         101         2        1999         IN      paid   2026-01-01T10:00:00Z      true
000002         102         1        2500         US      paid   2026-01-01T10:02:00Z      false
000003         unknown     bad      N/A          GB      ???    invalid                   true
```

A production transformation should make the schema explicit.

Conceptually:

```text
order_id
→ string

customer_id
→ Int64

quantity
→ Int16

amount_cents
→ Int64

country
→ category

status
→ ordered category

created_at
→ datetime64[ns, UTC] or an appropriate UTC timestamp dtype

is_gift
→ boolean
```

The third record contains multiple quality problems.

Do not solve them by silently inventing values.

Instead:

```text
raw value
→ parse attempt
→ failure accounting
→ validation
→ business policy
```

---

# 44. Ordered Status as a Production Rule

Suppose the pipeline uses:

```python
status_dtype = pd.CategoricalDtype(
    categories=[
        "pending",
        "paid",
        "shipped",
        "delivered",
        "cancelled",
    ],
    ordered=True,
)
```

Then:

```python
df["status"] = df["status"].astype(status_dtype)
```

Now the status field is carrying an explicit domain definition.

### Why this is better than alphabetical order

The following:

```python
df.sort_values("status")
```

can follow the business lifecycle instead of lexical order.

### What if a new source value appears?

For example:

```text
returned
```

If it is not part of the category vocabulary, that needs an explicit decision.

The source contract has changed.

---

# 45. `category` vs `string`

Use this comparison:

| Aspect | `category` | `string` |
|---|---|---|
| Values | constrained/repeated vocabulary | arbitrary text |
| Cardinality | strongest benefit at low cardinality | handles general text |
| Ordering | can be explicitly ordered | text ordering, not business category ordering |
| Memory | can save memory | depends on backend/data |
| Domain semantics | strong | generic text |
| Good examples | country, status | names, descriptions, free text |

A key question is:

> Is this column a **domain vocabulary** or merely **text**?

---

# 46. `category` vs Identifier Columns

Do not confuse:

```text
order_id
```

with:

```text
status
```

An order ID might be unique for every row.

A status might have only a handful of possible values.

So:

```text
order_id → usually string / integer identifier
status   → candidate for category
```

Do not category-encode an identifier simply because it is repeated in one particular sample. The choice should reflect expected cardinality and semantics over the data lifecycle.

---

# 47. Debugging — Unexpected `object` dtype

### Symptom

```text
df["quantity"].dtype == object
```

but the pipeline expects integers.

### Possible root cause

The source contains:

```text
"10"
"20"
"bad"
"30"
```

### Inspection

```python
print(df["quantity"])
print(df["quantity"].map(type).value_counts())
```

### Correct approach

```python
converted = pd.to_numeric(
    df["quantity"],
    errors="coerce",
)

failed = df["quantity"].notna() & converted.isna()

print("failed:", int(failed.sum()))
```

### Prevention rule

> Inspect inferred data and define an explicit schema before downstream arithmetic.

---

# 48. Debugging — Integer Column Became `float64`

### Symptom

```text
customer_id
101.0
102.0
NaN
104.0
```

### Root cause

A missing value is being represented in a normal numeric column that cannot remain a dense integer dtype.

### Correct pattern

```python
customer_id = pd.Series(
    [101, 102, None, 104],
    dtype="Int64",
)

print(customer_id)
print(customer_id.dtype)
```

### Prevention

> Use a nullable integer dtype when missing identifiers or counts are legitimate.

---

# 49. Debugging — `errors="coerce"` Hid Bad Data

### Buggy code

```python
converted = pd.to_numeric(
    raw,
    errors="coerce",
)
```

and then the developer never checks how many values became missing.

### Problem

A source corruption has been converted into apparent missingness.

### Correct approach

```python
converted = pd.to_numeric(
    raw,
    errors="coerce",
)

failed_mask = raw.notna() & converted.isna()

if failed_mask.any():
    raise ValueError(
        f"{int(failed_mask.sum())} numeric values failed conversion"
    )
```

Or route those records to quarantine according to the pipeline's contract.

### Prevention rule

> Coercion must be observable.

---

# 50. Debugging — Invalid Timestamp Became Missing

### Symptom

```text
created_at
<valid timestamp>
NaT
```

### Root cause

An invalid source value was coerced.

### Inspection

```python
parsed = pd.to_datetime(
    raw,
    format="%Y-%m-%d",
    errors="coerce",
    utc=True,
)

failed = raw.notna() & parsed.isna()

print(raw.loc[failed])
```

### Correct approach

Investigate the original values and decide whether to:

```text
fail
quarantine
repair according to a documented rule
accept as missing
```

Never assume `NaT` proves the source was missing.

---

# 51. Debugging — Naive and Aware Timestamps Mixed

### Symptom

A source contains:

```text
2026-01-01 10:00:00
2026-01-01 10:00:00+00:00
```

### Risk

The first has no timezone. The second does.

### Correct pattern

If the source contract allows interpreting the naive values as UTC:

```python
parsed = pd.to_datetime(
    raw,
    utc=True,
)
```

Pandas documents that `utc=True` can normalize timezone-aware inputs to UTC and localize naive inputs to UTC. citeturn980602search7

### Prevention

> Define the timezone assumption explicitly. Do not invent one silently.

---

# 52. Debugging — High-Cardinality Category

### Symptom

A developer converts a nearly unique column to category and sees little benefit.

### Example

```text
transaction_id
→ one unique value per row
```

### Root cause

The category vocabulary is nearly as large as the data.

### Correct approach

Measure:

```python
unique_ratio = (
    df["transaction_id"].nunique(dropna=False)
    / len(df)
)

print(unique_ratio)
```

Then decide whether category is justified.

### Prevention

> Evaluate cardinality before using categorical encoding for memory optimization.

---

# 53. Debugging — Assigning an Unknown Category

Suppose:

```python
status_dtype = pd.CategoricalDtype(
    categories=["pending", "paid", "shipped", "delivered"],
    ordered=True,
)

status = pd.Series(
    ["pending", "paid"],
    dtype=status_dtype,
)
```

Now a new source value arrives:

```text
returned
```

If the category vocabulary does not contain `"returned"`, do not silently pretend it is already part of the domain.

Possible policy:

```python
status = status.cat.add_categories(["returned"])
```

but only when that new category is actually valid according to the business/source contract.

### Prevention

> Category vocabularies are schema metadata; changes should be deliberate.

---

# 54. Debugging — Unused Categories

### Symptom

After filtering:

```python
filtered = countries[countries != "GB"]
```

the data contains no `"GB"` rows, but `"GB"` can remain in the category vocabulary.

### Inspection

```python
print(filtered.cat.categories)
```

### Correct approach

```python
filtered = filtered.cat.remove_unused_categories()
```

Use this when the desired semantics are:

```text
category vocabulary = values currently represented
```

Do not use it when the full vocabulary itself is intentionally part of the schema.

---

# 55. Debugging — Unexpected Grouping from Categories

A category can contain levels that are not observed.

Inspect:

```python
print(df["country"].dtype)
print(df["country"].cat.categories)
```

When grouping a categorical column and you only want observed categories:

```python
result = (
    df.groupby("country", observed=True)["amount"]
    .sum()
)
```

The important lesson is not memorizing one argument.

It is recognizing:

```text
dtype metadata
→
downstream operation semantics
```

---

# 56. Debugging — `pd.NA` Is Not Just `np.nan`

### Symptom

A developer expects ordinary Python/NumPy Boolean behavior from a nullable value.

### Example

```python
import pandas as pd

print(pd.NA | True)
print(pd.NA & True)
```

The outcomes reflect three-valued logic.

### Prevention

When nullable extension dtypes are involved, explicitly test:

```text
True
False
Unknown
```

rather than assuming a binary Boolean model.

---

# 57. Debugging — Arrow Is Not Automatically Better

### Bad assumption

```text
Arrow-backed = faster
```

### Correct question

```text
Which operations?
Which data?
Which pandas/PyArrow versions?
Which downstream systems?
What memory?
What runtime?
```

Arrow-backed types can improve interoperability and provide first-class nullable representations, but performance and compatibility are workload-dependent. citeturn980602search6

### Prevention rule

> Benchmark the actual workload.

---

# 58. Debugging — Smaller dtype Is Not Automatically Safer

Suppose someone changes:

```text
int64
→ int8
```

because it uses less memory.

That is only correct when the value range is safely inside `int8`.

The same principle from NumPy still applies:

```text
memory optimization
must not
break correctness
```

In pandas, dtype selection should consider:

- range
- missingness
- precision
- business semantics
- downstream compatibility

---

# 59. Debugging — String Comparison of Dtypes

This is easy to oversimplify:

```python
if str(df["id"].dtype) == "Int64":
    ...
```

Sometimes comparing dtype strings is convenient, but string equality alone is not a complete semantic framework.

Prefer pandas dtype APIs when the distinction is richer, and test actual behavior.

For a simple contract, a clear string comparison can still be acceptable when the exact target representation is intentional.

### Prevention rule

> Use the level of dtype comparison that matches the contract you are enforcing.

---

# 60. Practical Testing Strategy

Dtype code should be tested as carefully as transformation code.

Test:

```text
expected dtype
expected values
expected missing-value behavior
expected conversion failures
expected categories
expected ordering
expected timezone
expected backend where required
schema validity
```

### Example

```python
import pandas as pd

result = pd.DataFrame(
    {
        "customer_id": pd.Series([101, None], dtype="Int64"),
        "is_gift": pd.Series([True, None], dtype="boolean"),
    }
)

assert str(result["customer_id"].dtype) == "Int64"
assert str(result["is_gift"].dtype) == "boolean"

assert result["customer_id"].isna().sum() == 1
assert result["is_gift"].isna().sum() == 1
```

### Ordered categorical test

```python
status_dtype = pd.CategoricalDtype(
    categories=["pending", "paid", "shipped"],
    ordered=True,
)

status = pd.Series(
    ["shipped", "pending", "paid"],
    dtype=status_dtype,
)

sorted_status = status.sort_values()

expected = pd.Series(
    ["pending", "paid", "shipped"],
    dtype=status_dtype,
)

pd.testing.assert_series_equal(
    sorted_status.reset_index(drop=True),
    expected,
)
```

### Schema test

```python
schema = {
    "customer_id": "Int64",
    "is_gift": "boolean",
}

for column, expected_dtype in schema.items():
    assert str(result[column].dtype) == expected_dtype
```

---

# 61. Testing Conversion Failures

Do not only test that valid data converts.

Test invalid values.

```python
import pandas as pd

raw = pd.Series(
    ["10", "20", "bad"],
    dtype="str",
)

converted = pd.to_numeric(
    raw,
    errors="coerce",
)

failed = raw.notna() & converted.isna()

assert int(failed.sum()) == 1
assert raw.loc[failed].tolist() == ["bad"]
```

This verifies that your ingestion logic can detect source-quality problems instead of hiding them.

---

# 62. Testing Datetime Conversion

```python
import pandas as pd

raw = pd.Series(
    [
        "2026-01-01 10:00:00",
        "bad-date",
    ],
    dtype="str",
)

parsed = pd.to_datetime(
    raw,
    format="%Y-%m-%d %H:%M:%S",
    errors="coerce",
    utc=True,
)

assert parsed.notna().sum() == 1
assert parsed.isna().sum() == 1
```

Also verify that the timezone strategy is what the pipeline expects.

---

# 63. Testing Category Semantics

```python
import pandas as pd

dtype = pd.CategoricalDtype(
    categories=["pending", "paid", "shipped"],
    ordered=True,
)

status = pd.Series(
    ["paid", "pending", "shipped"],
    dtype=dtype,
)

assert status.dtype == dtype
assert list(status.cat.categories) == [
    "pending",
    "paid",
    "shipped",
]
assert status.cat.ordered
```

This protects both the values and the domain definition.

---

# 64. Testing `observed=True`

For categorical grouping behavior, make the category vocabulary intentionally include an unused value.

```python
import pandas as pd

country_dtype = pd.CategoricalDtype(
    categories=["IN", "US", "GB"]
)

df = pd.DataFrame(
    {
        "country": pd.Series(
            ["IN", "US"],
            dtype=country_dtype,
        ),
        "amount": [100, 200],
    }
)

result = (
    df.groupby("country", observed=True)["amount"]
    .sum()
)

assert list(result.index) == ["IN", "US"]
```

The exact downstream requirement determines whether observed categories or the full category vocabulary should be retained.

---

# 65. Memory Tests Without Fragile Numbers

Avoid tests such as:

```python
assert memory == 123456
```

because memory measurements can vary across:

- pandas versions
- Python versions
- platforms
- allocator behavior
- Arrow versions
- data size

Instead, test stable semantic properties.

For example:

```python
before = df["country"].nunique()
df["country"] = df["country"].astype("category")

assert df["country"].nunique() == before
```

Then use memory measurement as an observational benchmark rather than a brittle unit-test assertion.

---

# 66. Production Schema Design Table

A reusable production schema template:

| Column | Raw type | Target dtype | Why | Missing allowed? | Primary risk |
|---|---|---|---|---|---|
| `order_id` | string | `string` / `str` | identifier representation | usually no | leading-zero loss |
| `customer_id` | string | `Int64` or string, depending on contract | nullable identifier | maybe | numeric conversion |
| `quantity` | string | `Int16` | compact integer when range is known | maybe | invalid values / overflow |
| `amount_cents` | string | `Int64` | fixed-scale exact amount | maybe | malformed amounts |
| `country` | string | `category` when low-cardinality | repeated domain values | maybe | category drift |
| `status` | string | ordered category | lifecycle ordering | maybe | invalid status |
| `created_at` | string | UTC-aware datetime | consistent time semantics | maybe | timezone ambiguity |
| `is_gift` | string | `boolean` | true/false/unknown semantics | maybe | missing ≠ false |

The target dtype is a contract proposal, not an automatic answer for every dataset.

---

# 67. Hands-on Exercise — `typed_orders.py`

> **Do not create `typed_orders.py` as part of this chapter task.**
>
> This Markdown section specifies the exercise. The implementation and test file are created later in the learning workflow.

## Scenario

You receive an orders dataset where every field has initially been loaded as text.

The declared target schema is:

```text
order_id: string
customer_id: Int64
quantity: Int16
amount_cents: Int64
country: category
status: ordered category
created_at: datetime64[ns, UTC]
is_gift: boolean
```

For the example status domain, use an order such as:

```text
pending
paid
shipped
delivered
cancelled
```

and explicitly define the category ordering.

---

## Task 1 — Load Raw Strings

Treat the source as untyped input.

Inspect:

```python
print(df.dtypes)
```

Record:

```text
columns
row count
starting dtypes
obvious invalid values
```

Do not convert anything yet.

### Required reasoning

Explain:

```text
What does the raw source say?
What does pandas infer?
What does the pipeline actually need?
```

---

## Task 2 — Apply the Declared Schema

Convert each field deliberately.

A possible pattern is:

```python
df["order_id"] = df["order_id"].astype("string")

df["customer_id"] = pd.to_numeric(
    df["customer_id"],
    errors="coerce",
).astype("Int64")

df["quantity"] = pd.to_numeric(
    df["quantity"],
    errors="coerce",
).astype("Int16")

df["amount_cents"] = pd.to_numeric(
    df["amount_cents"],
    errors="coerce",
).astype("Int64")
```

Then define country and status categoricals.

```python
status_dtype = pd.CategoricalDtype(
    categories=[
        "pending",
        "paid",
        "shipped",
        "delivered",
        "cancelled",
    ],
    ordered=True,
)

df["country"] = df["country"].astype("category")
df["status"] = df["status"].astype(status_dtype)
```

Parse timestamps:

```python
df["created_at"] = pd.to_datetime(
    df["created_at"],
    errors="coerce",
    utc=True,
)
```

For boolean values, establish an explicit mapping if the source contains textual forms rather than literal Boolean values.

---

## Task 3 — Track Failed Conversions

For each conversion:

```text
1. preserve the raw value
2. convert
3. identify newly missing values
4. count failures
5. inspect original failed values
6. report them
7. decide fail / quarantine / accept
```

Example:

```python
raw_customer_id = df["customer_id"].copy()

customer_id = pd.to_numeric(
    raw_customer_id,
    errors="coerce",
)

failed = raw_customer_id.notna() & customer_id.isna()

print("customer_id failures:", int(failed.sum()))
print(raw_customer_id.loc[failed])
```

Do not count pre-existing missing values as conversion failures.

---

## Task 4 — Demonstrate Nullable Integers

Create the pair:

```python
import pandas as pd

standard = pd.Series([1, 2, None])
nullable = pd.Series([1, 2, None], dtype="Int64")

print(standard)
print(standard.dtype)

print(nullable)
print(nullable.dtype)
```

Explain why the second representation preserves integer semantics with missingness.

---

## Task 5 — Ordered Categorical Status

Sort the status column:

```python
sorted_orders = df.sort_values("status")
```

Then demonstrate:

```python
paid_or_later = df["status"] >= "paid"
```

Explain:

```text
Why does the comparison make sense?
Which category order is being used?
What should happen to missing status?
What should happen to an unknown status?
```

Do not leave category order implicit.

---

## Task 6 — Memory Comparison

Create at least four representations:

```text
1. all-object/raw
2. NumPy-typed
3. nullable-typed
4. Arrow-typed
```

Measure:

```python
df.memory_usage(deep=True)
df.memory_usage(deep=True).sum()
```

Record:

```text
representation
total bytes
bytes per row
relative change
```

The point is not to prove one backend is universally superior.

The point is to explain the measured difference.

---

## Task 7 — Schema Validation

Implement a function conceptually equivalent to:

```python
def validate_schema(df, schema):
    ...
```

It must check:

```text
required columns exist
expected dtypes match
unexpected columns handled according to contract
errors identify the exact mismatch
```

Test at least:

```text
valid DataFrame
wrong dtype
missing required column
unexpected column
conversion-invalid input
```

---

## Exercise Deliverables

The completed exercise should produce:

```text
raw schema report
→ converted DataFrame
→ conversion failure report
→ dtype report
→ category definition
→ memory comparison
→ schema validation result
→ tests
```

The exercise is complete only when you can explain every dtype choice.

---

# 68. Prediction-First Learning Drills

Before executing code, predict the answer.

## Drill A — Nullable integer

```python
import pandas as pd

s = pd.Series([1, 2, None])
```

Predict:

```text
dtype:
missing marker:
```

Then compare with:

```python
s = pd.Series([1, 2, None], dtype="Int64")
```

---

## Drill B — Numeric coercion

```python
raw = pd.Series(
    ["10", "20", "bad"],
    dtype="str",
)

converted = pd.to_numeric(
    raw,
    errors="coerce",
)
```

Predict:

```text
number of missing values:
failed source values:
```

---

## Drill C — Nullable Boolean

```python
s = pd.Series(
    [True, False, None],
    dtype="boolean",
)
```

Predict:

```text
dtype:
meaning of None:
```

---

## Drill D — Three-valued logic

Predict:

```python
pd.NA | True
pd.NA & True
pd.NA | False
pd.NA & False
```

---

## Drill E — Category

```python
s = pd.Series(
    ["IN", "US", "IN", "GB"],
    dtype="category",
)
```

Predict:

```text
number of rows:
number of unique values:
category vocabulary:
```

Then inspect:

```python
print(s.cat.categories)
print(s.cat.codes)
```

---

## Drill F — Ordered status

Given:

```text
pending < paid < shipped < delivered
```

predict the sorted result of:

```python
["delivered", "pending", "shipped", "paid"]
```

before creating the categorical.

---

## Drill G — Timestamp

Predict what this is intended to produce:

```python
pd.to_datetime(
    ["2025-01-01 10:00:00", "bad"],
    format="%Y-%m-%d %H:%M:%S",
    errors="coerce",
    utc=True,
)
```

---

## Drill H — Backend

Given:

```python
dtype_backend="pyarrow"
```

predict what changes:

```text
values?
semantic meaning?
underlying representation?
interoperability?
```

The answer should distinguish semantic dtype from backend.

---

# 69. Production Data Engineering Patterns

## Orders ingestion

```text
raw strings
   ↓
explicit parsing
   ↓
nullable types
   ↓
category/domain rules
   ↓
UTC timestamps
   ↓
schema validation
```

## Customer identifiers

Preserve the representation:

```text
"000123"
```

rather than converting to:

```text
123
```

when those leading zeros are part of the identifier.

## Quantities

Choose a safe integer representation based on:

```text
range
missingness
downstream compatibility
```

## Money

Choose deliberately among:

```text
integer cents
Decimal
Arrow decimal
```

according to required exactness and interoperability.

## Status

Use an ordered category when the lifecycle order is part of the domain.

## Country

Category is a candidate when the vocabulary is small and repeated.

## Event timestamps

Normalize timezone semantics intentionally, often to UTC.

## Boolean flags

Nullable boolean is useful when:

```text
False
```

and:

```text
unknown
```

have different meanings.

## Schema drift

Detect unexpected:

```text
columns
types
timestamp formats
categories
```

before downstream transformations.

---

# 70. Production Workflow for Dtype Management

Use this repeatable workflow:

```text
1. Read raw data
        ↓
2. Inspect current dtypes
        ↓
3. Define semantic schema
        ↓
4. Parse numeric / datetime values
        ↓
5. Count conversion failures
        ↓
6. Apply nullable / categorical types
        ↓
7. Validate categories and ordering
        ↓
8. Normalize timezone strategy
        ↓
9. Validate final dtypes
        ↓
10. Measure memory
        ↓
11. Test edge cases
        ↓
12. Document the schema
```

This is much stronger than:

```python
df = df.convert_dtypes()
```

and hoping for the best.

---

# 71. Deep Reasoning Questions

Keep these questions active throughout the topic.

### 1. Why can a missing integer become `float64`?

Because normal integer representations do not directly encode a missing floating-style marker such as `NaN`, so inference may select a floating representation.

### 2. Why does `Int64` solve the problem?

It provides pandas nullable integer semantics, allowing integer values plus missingness.

### 3. Why is `pd.NA` not simply another spelling of `np.nan`?

Because they come from different dtype/representation systems and have different scalar and logical semantics.

### 4. Why can missing Boolean mean "unknown"?

Because a nullable Boolean domain can represent three states rather than only True/False.

### 5. Why can category save memory?

Because repeated values can share a category vocabulary and be represented through codes.

### 6. Why can category be poor for high cardinality?

Because the category vocabulary becomes large relative to the number of rows.

### 7. Why does ordered category matter?

Because domain order is often not alphabetical order.

### 8. Why is UTC normalization useful?

Because a shared time basis reduces ambiguity when data crosses systems and time zones.

### 9. Why can timestamp resolution affect range?

Because fixed-width datetime representations trade time precision against representable range.

### 10. Why should money representation be deliberate?

Because binary floating-point is approximate for many decimal fractions, while some financial requirements need exact decimal or scaled-integer semantics.

### 11. Why can `errors="coerce"` be dangerous?

Because failed input values become missing values and can disappear as distinct data-quality signals unless failures are counted.

### 12. Why is a production schema stronger than inference?

Inference responds to the current sample. A schema states what the pipeline expects.

### 13. Why measure memory?

Because dtype choices are workload/data dependent.

### 14. Why is Arrow not automatically the correct choice?

Because interoperability, supported operations, runtime, and memory behavior depend on the actual workload and versions.

---

# 72. Comparison — Standard vs Nullable

| Concept | Standard | Nullable | Key difference |
|---|---|---|---|
| Integer | `int64` | `Int64` | nullable integer preserves integer semantics |
| Float | `float64` | `Float64` | nullable extension representation |
| Boolean | `bool` | `boolean` | nullable three-state-capable representation |
| String | generic/object legacy representation | `string` | dedicated pandas nullable string dtype |
| Missing scalar | often `NaN` / `None` depending on data | `pd.NA` in extension types | dtype-aware missing semantics |

Pandas 3 also introduces a dedicated default string dtype (`str`), which should be distinguished from the explicit nullable `string` dtype. citeturn980602search3

---

# 73. Comparison — Missing Value Markers

| Marker | Meaning / origin | Typical context | Important consideration |
|---|---|---|---|
| `pd.NA` | pandas missing scalar | extension dtypes | participates in nullable semantics |
| `np.nan` | floating-point NaN | floating data | is a float value, not an integer-null marker |
| `None` | Python null | object/input data | may trigger object-like representation |

Use:

```python
series.isna()
```

rather than relying on equality comparisons to detect missingness.

---

# 74. Comparison — Category vs String

| Aspect | `category` | `string` |
|---|---|---|
| Intended semantics | finite/repeated domain | general textual data |
| Cardinality | best when relatively low | works for general text |
| Vocabulary | explicit categories | arbitrary values |
| Ordering | can be ordered | not a business ordering model |
| Memory | can save memory | depends on backend and data |
| Common examples | country, status | name, code, description |
| Risk | category vocabulary drift | generic text can hide domain constraints |

---

# 75. Comparison — Money Representations

| Representation | Precision | Missing values | Trade-offs |
|---|---|---|---|
| binary float | approximate | supported | convenient, but not exact for many decimals |
| integer cents | exact for fixed scale | `Int64` | scale must be explicit |
| `Decimal` objects | decimal exactness | object-level missingness | Python-object overhead |
| Arrow decimal128 | decimal exactness | Arrow nullable semantics | backend compatibility must be tested |

---

# 76. Comparison — NumPy Nullable vs Arrow-Backed

| Aspect | NumPy nullable | Arrow-backed |
|---|---|---|
| Representation | pandas nullable extension types | PyArrow-backed arrays |
| Nullability | yes | yes |
| NumPy interoperability | generally natural | may require conversion depending on operation |
| Arrow interoperability | less direct | strong conceptual fit |
| Memory | workload-dependent | workload-dependent |
| Performance | benchmark | benchmark |
| API support | pandas-native | depends on pandas/PyArrow operation |
| Production choice | contract + workload | contract + workload |

Pandas currently documents Arrow-backed arrays as an experimental area whose API may change, so pin and test the versions used by your production environment. citeturn980602search6

---

# 77. Common Mistakes Summary

| Mistake | Why it happens | Correct approach |
|---|---|---|
| Treating `object` as "string" | old pandas habits / generic dtype | inspect actual values and use an intentional string dtype |
| Choosing `category` for every text column | assuming category always saves memory | check cardinality and measure |
| Using `errors="coerce"` without counting failures | convenience hides bad source values | count and inspect failed conversions |
| Mixing naive and aware timestamps | source systems use different conventions | define timezone semantics and normalize deliberately |
| Using `int64` when integers may be missing | forgetting nullable extension types | evaluate `Int64` |
| Treating `pd.NA` as identical to `np.nan` | simplifying too aggressively | understand dtype-specific missing semantics |
| Treating missing Boolean as False | collapsing unknown into false | use nullable boolean and explicit business policy |
| Trusting dtype inference in production | exploration becomes production code | use explicit schemas |
| Assuming ordered categories are alphabetical | category order not explicitly declared | define `CategoricalDtype(..., ordered=True)` |
| Assigning an undeclared category | source vocabulary changed | validate/update the category domain deliberately |
| Leaving unused categories accidentally | filtering does not automatically redefine the vocabulary | use `remove_unused_categories()` when appropriate |
| Assuming Arrow is always faster | cargo-cult optimization | benchmark actual workloads |
| Assuming the smallest dtype is safest | memory optimization without range analysis | choose based on range and semantics |
| Comparing only dtype strings | representation can have richer semantics | validate the actual contract and behavior |
| Measuring memory with fragile fixed thresholds | platform/version variation | benchmark trends and stable semantic invariants |

---

# 78. Production Checklist

### Before accepting a DataFrame schema

- [ ] Every column has an intentional dtype.
- [ ] Text columns are not accidentally generic `object`.
- [ ] Integer columns with missing values use an appropriate nullable representation.
- [ ] Numeric conversion failures are counted.
- [ ] Datetime conversion failures are counted.
- [ ] Timestamps have an intentional timezone strategy.
- [ ] UTC normalization is applied where required.
- [ ] Timestamp resolution is appropriate for the source and consumers.
- [ ] Categorical columns have justified cardinality.
- [ ] Ordered categories have an explicitly defined order.
- [ ] Money has an intentional representation.
- [ ] Memory has been measured.
- [ ] NumPy-nullable vs Arrow-backed representation has been considered.
- [ ] Expected columns are documented.
- [ ] Expected dtypes are documented.
- [ ] Schema validation is tested.
- [ ] Invalid source values are observable rather than silently discarded.
- [ ] Edge cases are tested.

---

# 79. Dtype Cheat Sheet

## Inspect

```python
df.dtypes
df["col"].dtype
df.info()
```

## Convert

```python
df["col"] = df["col"].astype("Int64")

df["amount"] = pd.to_numeric(
    df["amount"],
    errors="coerce",
)

df["created_at"] = pd.to_datetime(
    df["created_at"],
    format="%Y-%m-%d",
    errors="coerce",
    utc=True,
)
```

## Nullable types

```text
int64
Int64

float64
Float64

bool
boolean

str
string
```

## Convert broadly

```python
df = df.convert_dtypes()
```

## Category

```python
df["country"] = df["country"].astype("category")

s.cat.categories
s.cat.codes

s = s.cat.add_categories(["new_value"])
s = s.cat.remove_unused_categories()
```

## Ordered category

```python
status_dtype = pd.CategoricalDtype(
    categories=["pending", "paid", "shipped", "delivered"],
    ordered=True,
)

df["status"] = df["status"].astype(status_dtype)
```

## Categorical grouping

```python
df.groupby(
    "country",
    observed=True,
)
```

## Memory

```python
df.memory_usage(deep=True)
df.memory_usage(deep=True).sum()
```

## Arrow backend

```python
df.convert_dtypes(dtype_backend="pyarrow")
```

## Schema idea

```python
SCHEMA = {
    "order_id": "string",
    "customer_id": "Int64",
    "quantity": "Int16",
    "amount_cents": "Int64",
}
```

---

# 80. Checkpoint

Do not move forward until you can answer these without looking at your notes.

## Required checkpoint

### 1. Explain the difference between `pd.NA` and `np.nan`

You should be able to explain:

```text
origin
dtype context
missing semantics
logical behavior
```

### 2. Explain why an integer column with missing values can become `float64`

Then explain how a nullable integer such as:

```text
Int64
```

preserves integer semantics with missing values.

### 3. Choose when to use `category`

You should be able to explain:

```text
low cardinality
high cardinality
domain vocabulary
ordered domain
memory trade-off
```

### 4. Safely convert strings to timezone-aware UTC timestamps

You should be able to explain and use:

```python
pd.to_datetime(
    values,
    format=...,
    errors="coerce",
    utc=True,
)
```

## Advanced self-check

Answer these aloud:

1. Why is `object` an incomplete schema?
2. How does pandas 3's default `str` differ conceptually from `string`?
3. What is the difference between semantic dtype and backend representation?
4. When does `convert_dtypes()` help?
5. Why might a nullable Boolean need three states?
6. Why can category reduce memory?
7. Why can category become a poor choice for high-cardinality data?
8. What does `observed=True` change for categorical grouping?
9. Why can timestamp resolution affect range?
10. Which money representation would you choose for fixed-scale transaction amounts, and why?
11. How would you detect values coerced to missing?
12. What evidence would make you choose Arrow-backed types?
13. How would you detect schema drift?
14. What would you test before allowing a new source into production?

---

# 81. Final Mental Model

The chapter can be compressed into this hierarchy:

```text
RAW VALUES
    ↓
SEMANTIC MEANING
    ↓
EXPECTED DOMAIN
    ↓
MISSINGNESS RULE
    ↓
PANDAS DTYPE
    ↓
BACKEND / REPRESENTATION
    ↓
CONVERSION
    ↓
VALIDATION
    ↓
MEMORY MEASUREMENT
    ↓
DOWNSTREAM BEHAVIOR
```

Or, operationally:

```text
Source
  ↓
What does each column mean?
  ↓
What values are valid?
  ↓
Can values be missing?
  ↓
What dtype expresses that meaning?
  ↓
How do invalid values behave?
  ↓
How will timestamps and money be represented?
  ↓
Does category make semantic sense?
  ↓
Would NumPy-nullable or Arrow-backed storage help?
  ↓
How much memory does it use?
  ↓
Can tests prove the contract?
```

### Production dtype checklist

Before shipping a DataFrame downstream, ask:

```text
1. What does each column mean?
2. Is the current dtype intentional?
3. Is missingness represented correctly?
4. Could conversion lose information?
5. Are identifiers preserved exactly?
6. Are timestamps timezone-safe?
7. Is timestamp resolution appropriate?
8. Is money represented exactly enough?
9. Is category justified by cardinality and domain semantics?
10. Is category ordering explicit where needed?
11. Does schema validation pass?
12. Have conversion failures been counted?
13. Have memory implications been measured?
14. Does the chosen backend fit downstream consumers?
15. Have edge cases been tested?
```

If you can answer all fifteen confidently, you are no longer merely "casting columns." You are managing a production data contract.

---

# 82. Connection to the Next Topics

This module progresses from:

```text
Topic 01
Series / DataFrame / Index
        ↓
Topic 02
Reading and writing data sources
        ↓
Topic 03
Selection with loc / iloc / query
        ↓
Topic 04
dtypes / nullable types / categoricals
        ↓
Topic 05
cleaning missing values / duplicates / outliers
```

The key dependency is:

> **Once you can select the right data, you must ensure every selected column has the right type before you clean, aggregate, join, reshape, or publish it.**

Topic 05 will build on this schema discipline when it teaches missing values, duplicates, outliers, and cleaning decisions.

---

# 83. Module Integration

The larger Stage 2 progression is:

```text
NumPy
  ↓
dense numerical arrays
  ↓
pandas DataFrame
  ↓
label-aware columns and indexes
  ↓
explicit dtypes
  ↓
nullable values
  ↓
categorical domains
  ↓
typed transformations
  ↓
cleaning
  ↓
aggregation
  ↓
joins
  ↓
reshaping
  ↓
time series
  ↓
production-scale DataFrame processing
```

The central engineering lesson is:

```text
DATA TYPE
is not decoration.

DATA TYPE
is part of correctness.
```

A DataFrame with the wrong values but the right shape is incorrect.

A DataFrame with the right values but the wrong dtype can also be incorrect.

A production Data Engineer therefore reasons about:

```text
values
+
meaning
+
missingness
+
representation
+
memory
+
downstream compatibility
```

That is the foundation required for the rest of pandas and for later Data Engineering systems.
