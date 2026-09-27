# 10 — String and Datetime Accessors

> **Stage 2 — Python for Data Engineering → Module 2.3 — DataFrames with pandas**
>
> **Progression:** Basic → Intermediate → Advanced production-oriented Data Engineering

## Learning contract

This is a complete learning chapter, not a shallow API list. Use the loop:

**What → Why → Mental Model → Syntax → Example → Expected Result → Common Mistake → Correct Pattern → Validation → Production Use → Testing → Performance**

The central principle is:

> **Use pandas accessors deliberately to transform, parse, normalize, validate, and derive information from text and time-series columns while preserving data meaning and handling failures explicitly.**

### Scope

This chapter follows Topic 10 of the authoritative pandas roadmap:

- `.str`: `strip`, `lower`, `upper`, `title`, `len`, `startswith`, `endswith`, `contains`, `replace`, `slice`, `zfill`, `pad`
- `.dt`: `year`, `month`, `day`, `hour`, `dayofweek`, `day_name`, `quarter`, `date`, `is_month_end`
- regex: `.str.contains(regex=True)`, `.str.extract`, named groups, `.str.extractall`, `.str.findall`, `.str.replace(regex=True)`
- splitting/joining: `.str.split(expand=True)`, `.str.rsplit(n=1)`, `.str.partition`, `.str.cat`
- datetime bucketing: `.dt.floor`, `.dt.ceil`, `.dt.round`
- timezone conversion: `.dt.tz_convert`
- output formatting: `.dt.strftime`
- periods: `.dt.to_period`
- categorical access: `.cat` for renaming and ordering
- missing-value behavior, Unicode normalization, invisible whitespace
- string dtype vs `object`, Arrow-backed strings, vectorized operations vs `apply`
- mixed timestamp parsing with explicit formats, failure counting, and no silent guessing
- the `text_and_time_cleaning.py` hands-on exercise
- prediction-first learning, debugging, testing, edge cases, production use cases, reconciliation, checkpoint, common mistakes, cheat sheet, and production checklist

> **Scope boundary:** method chaining, Copy-on-Write, and chunked processing are later roadmap topics and are not taught deeply here.

---

# 1. Why String and Datetime Accessors Matter

Real data arrives as messy text and timestamp strings.

```text
"  Shoun Kumar  "
"PAID "
"+91-98765-43210"
"IN"
"2025/09/26 14:35"
```

The visible value is not always the canonical value.

Poor cleaning can cause:

- duplicate entities;
- failed joins;
- inconsistent grouping;
- incorrect filters;
- broken reports;
- malformed timestamps;
- incorrect time buckets.

### Production questions

Before transforming any column, ask:

1. What does the source value actually represent?
2. Is whitespace meaningful?
3. Is case meaningful?
4. Is this a key/code/label or free text?
5. Is Unicode normalization relevant?
6. Is regex actually needed?
7. What happens for missing values?
8. What happens for malformed values?
9. Is the timestamp format known?
10. Is the timestamp naive or timezone-aware?
11. Should the result remain typed or become presentation text?
12. How many values can fail?
13. Can failures be inspected later?
14. Is a vectorized accessor available?
15. Has performance been measured?

---

# 2. What Is a pandas Accessor?

A pandas accessor is a pandas-aware namespace for a class of operations.

The accessors used in this topic are:

```text
.str
.dt
.cat
```

Conceptual model:

```text
Series
  ↓
Accessor
  ↓
vectorized / pandas-aware operation
  ↓
Series, DataFrame, or structured result
```

Examples:

```python
df["name"].str.strip()
df["created_at"].dt.year
df["status"].cat.rename_categories(...)
```

The accessor lets you express intent at the Series level rather than manually looping through rows.

---

# 3. Why Accessors Instead of Row-by-Row Loops?

Compare:

```python
df["name"].str.strip()
```

with:

```python
df["name"].apply(lambda s: s.strip())
```

The accessor communicates:

> "Apply the pandas string operation to this column."

The `apply` expression communicates:

> "Call this arbitrary Python function on each value."

### Why accessors are normally preferred for supported operations

- clearer intent;
- easier composition;
- pandas-aware missing-value behavior;
- opportunity for optimized/native implementations;
- less custom Python code to maintain.

### Do not memorize "vectorized is always faster"

That statement is too strong.

Performance depends on:

- pandas version;
- dtype/storage backend;
- data size;
- string length;
- regex complexity;
- missingness;
- hardware.

The correct engineering rule is:

> **Prefer the operation that naturally expresses the transformation, then benchmark important workloads.**

---

# 4. `.str` Accessor — Foundation

Create a small Series:

```python
import pandas as pd

s = pd.Series(
    [" Shoun Kumar ", "alice", "BOB"],
    dtype="string",
)

print(s.str.strip())
```

Expected logical values:

```text
Shoun Kumar
alice
BOB
```

The result remains aligned with the original index.

### Prediction-first

Before executing:

```python
s.str.strip()
```

predict the result row by row.

Then execute, inspect, and assert.

---

# 5. `strip()`

## What

```python
s.str.strip()
```

removes leading and trailing whitespace.

## Why

Whitespace can break exact key matches.

## Example

```python
s = pd.Series(
    [" C001 ", "C002", "  C003"],
    dtype="string",
)

clean = s.str.strip()

print(clean.tolist())
```

Expected:

```python
["C001", "C002", "C003"]
```

## What it does not do

It does not:

- collapse internal repeated spaces;
- normalize Unicode;
- change case;
- validate a key.

For:

```text
"Shoun    Kumar"
```

`strip()` leaves the internal spaces unchanged.

## Production rule

Trim only when the field contract says leading/trailing whitespace is not meaningful.

## Test

```python
result = pd.Series(
    [" A ", "B", "  C"],
    dtype="string",
).str.strip()

assert result.tolist() == ["A", "B", "C"]
```

---

# 6. `lower()`

## What

```python
s.str.lower()
```

converts text to lowercase.

## Example

```python
s = pd.Series(["IN", "In", "in", "Us"], dtype="string")

print(s.str.lower().tolist())
```

Expected:

```python
["in", "in", "in", "us"]
```

## Data Engineering use

Useful for case-insensitive canonical keys, controlled labels, and machine-readable codes.

## Production warning

Do not lowercase human-facing names simply because a key was normalized.

---

# 7. `upper()`

```python
s = pd.Series(["in", "In", "IN"], dtype="string")

result = s.str.upper()

print(result.tolist())
```

Expected:

```python
["IN", "IN", "IN"]
```

A common code-normalization pattern is:

```python
df["country_code"] = (
    df["country_code"]
    .str.strip()
    .str.upper()
)
```

Use it only when the field is defined as case-insensitive.

---

# 8. `title()`

```python
s = pd.Series(
    ["alice smith", "BOB JONES", "mcdonald"],
    dtype="string",
)

print(s.str.title().tolist())
```

Typical result:

```python
["Alice Smith", "Bob Jones", "Mcdonald"]
```

### Production warning

Title case is not a perfect name-cleaning algorithm.

Real names can include:

- language-specific capitalization;
- apostrophes;
- hyphens;
- prefixes;
- intentional capitalization.

Treat `.str.title()` as presentation-oriented normalization unless the source contract explicitly says otherwise.

---

# 9. `len()`

```python
s = pd.Series(
    ["C001", "C1002", "ABC"],
    dtype="string",
)

result = s.str.len()

print(result.tolist())
```

Expected:

```python
[4, 5, 3]
```

### Data-quality use

A length rule can identify candidates for rejection:

```python
invalid = df["customer_id"].str.len().ne(6)
bad_rows = df.loc[invalid]
```

Length is useful but does not prove structure. A six-character value can still contain invalid characters.

---

# 10. `startswith()`

```python
s = pd.Series(
    ["SKU-001", "SKU-002", "PROD-003"],
    dtype="string",
)

print(s.str.startswith("SKU-").tolist())
```

Expected:

```python
[True, True, False]
```

Useful for:

- product namespaces;
- event IDs;
- source prefixes;
- partition identifiers.

Prefer it over regex when the requirement is literally "starts with this prefix."

---

# 11. `endswith()`

```python
files = pd.Series(
    ["orders.parquet", "customers.csv", "events.parquet"],
    dtype="string",
)

print(files.str.endswith(".parquet").tolist())
```

Expected:

```python
[True, False, True]
```

Useful for:

- file suffixes;
- product-code endings;
- domain suffixes.

---

# 12. `contains()`

`contains()` answers:

> Does this substring or pattern occur in the value?

Example literal search:

```python
messages = pd.Series(
    ["payment error", "payment ok", None],
    dtype="string",
)

result = messages.str.contains(
    "error",
    regex=False,
    na=False,
)

print(result.tolist())
```

Expected:

```python
[True, False, False]
```

### Important parameters

```python
s.str.contains(
    pat,
    case=True,
    flags=0,
    na=...,
    regex=True,
)
```

Current pandas documentation says the default `na` behavior depends on dtype; for pandas' `"str"` dtype it is `False`, while nullable string dtype uses `pd.NA`, and object dtype can produce `np.nan`. citeturn976423search0

### `na=False` is semantic

`na=False` means:

```text
missing → False
```

That is correct only when "missing" logically means "not matched" for the rule.

---

# 13. `replace()`

Current pandas uses an explicit `regex` parameter; string patterns are treated as literal by default in the ordinary case, so make regex intent explicit. citeturn976423search9

### Literal replacement

```python
s = pd.Series(
    ["212-555-1234", "212-555-5678"],
    dtype="string",
)

clean = s.str.replace(
    "-",
    "",
    regex=False,
)

print(clean.tolist())
```

Expected:

```python
["2125551234", "2125555678"]
```

### Regex replacement

```python
clean = s.str.replace(
    r"\D+",
    "",
    regex=True,
)
```

Here:

```regex
\D+
```

means one or more non-digit characters.

### Production rule

Use literal replacement when the requirement is literal.

Use regex when a pattern is actually required.

---

# 14. `slice()`

`slice()` performs positional extraction.

```python
s = pd.Series(
    ["SKU12345", "SKU98765"],
    dtype="string",
)

result = s.str.slice(0, 3)

print(result.tolist())
```

Expected:

```python
["SKU", "SKU"]
```

Use it when position is part of the source contract.

Use `split`, `partition`, or regex extraction when meaning depends on delimiters or patterns.

---

# 15. `zfill()`

```python
s = pd.Series(
    ["12345", "7", "12345678"],
    dtype="string",
)

result = s.str.zfill(8)

print(result.tolist())
```

Expected:

```python
["00012345", "00000007", "12345678"]
```

### Why this matters

An identifier such as:

```text
001234
```

may be semantically different from numeric `1234`.

Do not convert digit-only identifiers to numeric types merely because they look numeric.

---

# 16. `pad()`

```python
s = pd.Series(
    ["A", "AB", "ABC"],
    dtype="string",
)

print(s.str.pad(5, side="left", fillchar="0").tolist())
print(s.str.pad(5, side="right", fillchar="-").tolist())
```

Expected:

```python
["0000A", "000AB", "00ABC"]
["A----", "AB---", "ABC--"]
```

`pad()` supports left, right, and both-side padding. citeturn976423search7

Use `zfill()` when the intent is specifically zero-padding.

---

# 17. `.str` Core Methods Cheat Table

| Method | Purpose | Typical Data Engineering use |
|---|---|---|
| `strip` | Remove outer whitespace | Keys and codes |
| `lower` | Normalize case downward | Case-insensitive keys |
| `upper` | Normalize case upward | Codes |
| `title` | Presentation-style capitalization | Human labels |
| `len` | Count characters | Quality checks |
| `startswith` | Prefix detection | Namespaces |
| `endswith` | Suffix detection | File/code suffixes |
| `contains` | Substring/pattern search | Classification |
| `replace` | Replace text/patterns | Canonicalization |
| `slice` | Positional substring | Fixed-format IDs |
| `zfill` | Left zero-padding | Fixed-width IDs |
| `pad` | General padding | Formatting |

---

# 18. `.dt` Accessor — Foundation

Use `.dt` after the data is datetime-like.

```python
timestamps = pd.Series(
    pd.to_datetime(
        [
            "2025-09-26 14:30:00",
            "2025-09-27 09:15:00",
        ],
        utc=True,
    )
)

print(timestamps.dt.year.tolist())
```

Expected:

```python
[2025, 2025]
```

Typical pipeline:

```text
raw timestamp
    ↓
parse
    ↓
validate
    ↓
timezone strategy
    ↓
datetime dtype
    ↓
.dt operations
```

---

# 19. `.dt.year`

```python
s = pd.Series(
    pd.to_datetime(
        ["2024-12-31 23:59:59", "2025-01-01 00:00:00"],
        utc=True,
    )
)

print(s.dt.year.tolist())
```

Expected:

```python
[2024, 2025]
```

Use for:

- annual reporting;
- partitions;
- year-over-year dimensions.

Calendar year is not automatically a fiscal year.

---

# 20. `.dt.month`

```python
s = pd.Series(
    pd.to_datetime(["2025-01-15", "2025-09-26"])
)

print(s.dt.month.tolist())
```

Expected:

```python
[1, 9]
```

The property returns the calendar month number from 1 to 12.

---

# 21. `.dt.day`

```python
s = pd.Series(
    pd.to_datetime(["2025-09-01", "2025-09-26"])
)

print(s.dt.day.tolist())
```

Expected:

```python
[1, 26]
```

`day` means day of month, not weekday.

---

# 22. `.dt.hour`

```python
s = pd.Series(
    pd.to_datetime(
        ["2025-09-26 00:15:00", "2025-09-26 14:35:00"]
    )
)

print(s.dt.hour.tolist())
```

Expected:

```python
[0, 14]
```

Interpret the hour in the timestamp's timezone. "14" in UTC and "14" in New York can refer to different instants.

---

# 23. `.dt.dayofweek`

Pandas uses:

```text
Monday    0
Tuesday   1
Wednesday 2
Thursday  3
Friday    4
Saturday  5
Sunday    6
```

Example:

```python
s = pd.Series(
    pd.to_datetime(["2025-09-26", "2025-09-27"])
)

print(s.dt.dayofweek.tolist())
```

Expected:

```python
[4, 5]
```

Use this when a numeric weekday is convenient for grouping or rules.

---

# 24. `.dt.day_name()`

```python
s = pd.Series(
    pd.to_datetime(["2025-09-26", "2025-09-27"])
)

print(s.dt.day_name().tolist())
```

Expected:

```python
["Friday", "Saturday"]
```

Useful for human-readable reports.

Do not replace a canonical datetime with these labels.

---

# 25. `.dt.quarter`

```python
s = pd.Series(
    pd.to_datetime(
        ["2025-01-01", "2025-04-01", "2025-09-26", "2025-12-31"]
    )
)

print(s.dt.quarter.tolist())
```

Expected:

```python
[1, 2, 3, 4]
```

This is the **calendar** quarter.

A fiscal quarter may require a separate calendar definition.

---

# 26. `.dt.date`

```python
s = pd.Series(
    pd.to_datetime(["2025-09-26 14:35:00"])
)

result = s.dt.date

print(result.tolist())
```

Conceptually:

```text
2025-09-26 14:35:00 → 2025-09-26
```

This produces date-only Python values rather than preserving the full timestamp semantics.

### Production rule

Keep the original timestamp for downstream time operations. Derive a date-only field for a specific use case instead of destroying the typed timestamp.

---

# 27. `.dt.is_month_end`

```python
s = pd.Series(
    pd.to_datetime(["2025-09-29", "2025-09-30"])
)

print(s.dt.is_month_end.tolist())
```

Expected:

```python
[False, True]
```

Useful for calendar month-end reporting and checks.

Financial close calendars can have business-specific definitions, so do not assume calendar month-end equals accounting close.

---

# 28. Regex Fundamentals for pandas Users

This chapter needs only a practical regex subset.

| Pattern | Meaning |
|---|---|
| `ABC` | Literal text |
| `\d` | Digit |
| `\d+` | One or more digits |
| `[0-9]` | One digit |
| `(...)` | Capturing group |
| `(?:...)` | Non-capturing group |
| `(?P<name>...)` | Named capturing group |
| `^` | Start of string |
| `$` | End of string |
| `?` | Optional preceding component |

Do not turn this chapter into a generic regex textbook.

---

# 29. `.str.contains(..., regex=True)`

Use regex deliberately:

```python
pattern = r"\bERR_[0-9]{3}\b"

result = df["message"].str.contains(
    pattern,
    regex=True,
    na=False,
)
```

The pattern answers:

> Does this message contain an error code matching this structure?

### Literal versus regex

For a literal plus sign:

```python
s.str.contains("+", regex=False, na=False)
```

For a regex representation of a literal plus:

```python
s.str.contains(r"\+", regex=True, na=False)
```

---

# 30. `.str.extract`

`extract` retrieves captured pieces from each input string.

```python
s = pd.Series(
    ["212-555-1234", "415-555-9876"],
    dtype="string",
)

result = s.str.extract(
    r"^(?P<area_code>\d{3})-(?P<number>\d{3}-\d{4})$"
)

print(result)
```

Conceptual result:

```text
  area_code      number
0       212  555-1234
1       415  555-9876
```

Mental model:

```text
one source row
   ↓
one intended match
   ↓
capture groups
   ↓
columns
```

---

# 31. Named Regex Groups

Use:

```python
r"(?P<area_code>\d{3})(?P<number>\d{7})"
```

instead of anonymous groups when extracting production fields.

Example:

```python
s = pd.Series(
    ["2125551234"],
    dtype="string",
)

parts = s.str.extract(
    r"^(?P<area_code>\d{3})(?P<number>\d{7})$"
)

print(parts.columns.tolist())
```

Expected:

```python
["area_code", "number"]
```

### Why named groups help

They make the output schema self-documenting and reduce the need to remember column position.

---

# 32. `.str.extract` vs `.str.extractall`

| Operation | Result grain | Use |
|---|---|---|
| `extract` | One row per input | One meaningful match per row |
| `extractall` | One row per match | Multiple matches per source row |

Example:

```python
s = pd.Series(
    ["codes: P001 P002", "code: P010", "none"],
    index=["a", "b", "c"],
    dtype="string",
)

result = s.str.extractall(
    r"(?P<product_code>P\d{3})"
)

print(result)
```

`extractall` can create multiple match rows from one source row and returns a MultiIndex whose final level identifies the match. citeturn976423search6

### Grain is the key concept

Before `extractall`, decide whether the downstream dataset should be:

```text
one row per source record
```

or:

```text
one row per extracted match
```

---

# 33. `.str.findall`

`findall` keeps all matches together as list-like values.

```python
s = pd.Series(
    ["codes: P001 P002", "code: P010", "none"],
    dtype="string",
)

result = s.str.findall(r"P\d{3}")

print(result.tolist())
```

Expected logical structure:

```python
[
    ["P001", "P002"],
    ["P010"],
    [],
]
```

### Compare

```text
extract
  → capture fields from one match

extractall
  → expand all matches into rows

findall
  → keep all matches as lists
```

---

# 34. Regex Replacement

```python
phones = pd.Series(
    ["(212) 555-1234", "+1 212 555 1234"],
    dtype="string",
)

digits = phones.str.replace(
    r"\D+",
    "",
    regex=True,
)

print(digits.tolist())
```

Expected logical values:

```python
["2125551234", "12125551234"]
```

### Explain the pattern

```regex
\D+
```

means one or more non-digit characters.

### Safety

A broad regex can delete meaningful information.

Test before and after.

---

# 35. Regex Safety — Positive and Negative Test Matrix

For **every regex pattern used in the exercise**, require at least:

- five positive examples;
- five negative examples.

Template:

| Input | Expected match | Expected output |
|---|---|---|
| Positive 1 | yes | expected |
| Positive 2 | yes | expected |
| Positive 3 | yes | expected |
| Positive 4 | yes | expected |
| Positive 5 | yes | expected |
| Negative 1 | no | missing/invalid |
| Negative 2 | no | missing/invalid |
| Negative 3 | no | missing/invalid |
| Negative 4 | no | missing/invalid |
| Negative 5 | no | missing/invalid |

This prevents a regex from being overfit to a few happy-path samples.

---

# 36. `.str.split()`

```python
s = pd.Series(
    ["New Delhi, DL 110001", "Mumbai, MH 400001"],
    dtype="string",
)

result = s.str.split(",")

print(result.tolist())
```

Logical result:

```python
[
    ["New Delhi", " DL 110001"],
    ["Mumbai", " MH 400001"],
]
```

By default, `split` returns list-like values.

---

# 37. `.str.split(expand=True)`

```python
parts = (
    s.str.split(",", expand=True)
)

print(parts)
```

Conceptually:

```text
           0           1
0  New Delhi   DL 110001
1      Mumbai   MH 400001
```

`expand=True` changes the dimensionality to separate columns. Current pandas documentation also makes its regex behavior explicit through the `regex` parameter. citeturn976423search5

### Production caution

Different numbers of delimiters can create unexpected shapes.

Validate the resulting columns.

---

# 38. `.str.rsplit(n=1)`

`rsplit` starts from the right.

```python
paths = pd.Series(
    [
        "/data/bronze/orders/2025-09.parquet",
        "/data/bronze/customers/2025-09.parquet",
    ],
    dtype="string",
)

parts = paths.str.rsplit("/", n=1, expand=True)

print(parts)
```

Conceptually:

```text
                         0                     1
0  /data/bronze/orders       2025-09.parquet
1  /data/bronze/customers    2025-09.parquet
```

Use it when the last token has a stable meaning.

Pandas documents that `rsplit` performs the split from the end and supports `n` to limit the number of splits. citeturn976423search4

---

# 39. `.str.partition()`

`partition()` returns:

```text
before separator
separator
after separator
```

Example:

```python
s = pd.Series(
    ["country=IN", "country=US"],
    dtype="string",
)

parts = s.str.partition("=")

print(parts)
```

Conceptually:

```text
         0  1   2
0  country  =  IN
1  country  =  US
```

If the separator is absent, the first field contains the input and the other fields are empty. citeturn976423search12

Use it for simple first-separator key/value formats.

---

# 40. `.str.cat()`

```python
first = pd.Series(
    ["Shoun", "Alice", "Bob"],
    dtype="string",
)

last = pd.Series(
    ["Kumar", "Smith", "Jones"],
    dtype="string",
)

full = first.str.cat(last, sep=" ")

print(full.tolist())
```

Expected:

```python
["Shoun Kumar", "Alice Smith", "Bob Jones"]
```

`cat` is useful for combining normalized columns.

Missing-value behavior should be part of the field's contract rather than an afterthought.

---

# 41. Splitting Comparison

| Operation | Main use |
|---|---|
| `split` | Split from the left around delimiters |
| `rsplit` | Split from the right |
| `partition` | First separator + separator + remainder |
| `cat` | Concatenate Series |

Decision guide:

```text
multiple tokens?
    → split

need last token?
    → rsplit(n=...)

need separator preserved?
    → partition

need to combine columns?
    → cat
```

# 42. Datetime Bucketing with `.dt.floor()`

`floor` moves a timestamp down to the beginning of a fixed-frequency bucket.

```python
import pandas as pd

s = pd.Series(
    pd.to_datetime(
        [
            "2025-09-26 14:03:12",
            "2025-09-26 14:59:59",
        ]
    )
)

result = s.dt.floor("h")

print(result)
```

Logical result:

```text
2025-09-26 14:00:00
2025-09-26 14:00:00
```

Use `floor` when the business meaning is:

> "Put every event in the bucket it started in."

Current pandas documents `floor` as a fixed-frequency operation; fixed frequencies such as hours or seconds are appropriate, while month-end is not a fixed frequency. citeturn976423search14

---

# 43. `.dt.ceil()`

`ceil` moves a timestamp up to the next fixed-frequency boundary when it is not already on a boundary.

```python
s = pd.Series(
    pd.to_datetime(
        ["2025-09-26 14:03:12", "2025-09-26 14:00:00"]
    )
)

result = s.dt.ceil("h")

print(result)
```

Logical result:

```text
2025-09-26 15:00:00
2025-09-26 14:00:00
```

A timestamp already exactly on a boundary remains there.

---

# 44. `.dt.round()`

`round` chooses the nearest fixed-frequency boundary.

```python
s = pd.Series(
    pd.to_datetime(
        [
            "2025-09-26 14:29:00",
            "2025-09-26 14:31:00",
        ]
    )
)

result = s.dt.round("h")

print(result)
```

Logical result:

```text
14:29 → 14:00
14:31 → 15:00
```

### Compare

| Method | Meaning |
|---|---|
| `floor("h")` | Always move down |
| `ceil("h")` | Move upward to a boundary |
| `round("h")` | Choose the nearest boundary |

### Boundary testing

Always test:

```text
exactly on boundary
just before boundary
just after boundary
midpoint
```

When business semantics matter, document how ties are expected to behave and validate against the installed pandas version.

---

# 45. `.dt.floor` vs `.dt.ceil` vs `.dt.round`

Mental model:

```text
14:03
│
├── floor ──► 14:00
├── round ──► 14:00
└── ceil  ──► 15:00
```

For:

```text
14:58
```

the typical result is:

```text
floor ──► 14:00
round ──► 15:00
ceil  ──► 15:00
```

### Production question

Ask:

> What does my metric mean at the boundary?

A queue SLA, billing interval, sensor aggregation, and report label may require different bucketing semantics.

---

# 46. `.dt.tz_convert()`

`tz_convert` converts timezone-aware datetime values from one timezone to another.

```python
s.dt.tz_convert("America/New_York")
```

It requires timezone-aware data. Pandas documents that calling it on timezone-naive data raises an error. citeturn976423search1

### Example

```python
s = pd.Series(
    pd.to_datetime(
        ["2025-09-26 14:00:00+00:00"],
        utc=True,
    )
)

ny = s.dt.tz_convert("America/New_York")
kolkata = s.dt.tz_convert("Asia/Kolkata")

print(ny)
print(kolkata)
```

The displayed local hour changes because the representation is changed.

The underlying instant is preserved.

### Mental model

```text
same instant
     ↓
different local clock
```

---

# 47. `tz_convert()` vs `tz_localize()`

Do not confuse these operations.

```text
tz_localize
    → establish/attach a timezone interpretation for naive local times

tz_convert
    → convert already-aware timestamps to another timezone
```

### Example of the semantic difference

Suppose the source says:

```text
2025-09-26 14:00:00
```

but the source contract says:

```text
Asia/Kolkata local time
```

The timestamp is naive.

The first problem is not "convert to New York."

The first problem is:

> "What timezone does this naive clock reading represent?"

After the source timezone is established, conversion is meaningful.

### Production rule

Never use timezone conversion to hide uncertainty about what a naive timestamp means.

---

# 48. `.dt.strftime()`

`strftime` formats datetime values into strings.

```python
s = pd.Series(
    pd.to_datetime(
        ["2025-09-26 14:35:00", "2025-09-27 09:10:00"]
    )
)

formatted = s.dt.strftime("%Y-%m-%d")

print(formatted.tolist())
```

Expected:

```python
["2025-09-26", "2025-09-27"]
```

Pandas documents `Series.dt.strftime` as formatting datetime values according to the supplied `strftime` pattern. citeturn976423search2

### Common format codes

| Code | Meaning |
|---|---|
| `%Y` | four-digit year |
| `%m` | zero-padded month |
| `%d` | zero-padded day |
| `%H` | 24-hour hour |
| `%M` | minute |
| `%S` | second |
| `%z` | numeric UTC offset |
| `%Z` | timezone name where available |

### Critical production rule

Keep canonical timestamps typed as datetime.

Use `strftime` for:

- report labels;
- file names;
- presentation;
- export formats.

Do not format a canonical column into strings merely to make it look nice.

---

# 49. Datetime Representation vs Presentation

A good pipeline separates:

```text
data representation
```

from:

```text
presentation formatting
```

### Representation

```python
df["created_at"]
```

remains a datetime column.

### Presentation

```python
df["created_at_label"] = (
    df["created_at"].dt.strftime("%Y-%m-%d")
)
```

### Why?

A string is not equivalent to a datetime.

Once a timestamp becomes:

```text
"2025-09-26"
```

you lose the original typed timestamp semantics needed for:

- timezone conversion;
- timestamp comparisons;
- datetime arithmetic;
- `.dt` extraction;
- time-window calculations.

> **Keep timestamps as datetime types until the pipeline boundary requires a formatted string.**

---

# 50. `.dt.to_period()`

`to_period` changes timestamp values into calendar periods.

```python
s = pd.Series(
    pd.to_datetime(
        ["2025-09-01", "2025-09-26", "2025-10-01"]
    )
)

result = s.dt.to_period("M")

print(result.tolist())
```

Conceptually:

```text
2025-09-01 → 2025-09
2025-09-26 → 2025-09
2025-10-01 → 2025-10
```

### Timestamp vs Period

```text
Timestamp
    → an instant

Period
    → a calendar interval
```

Periods are useful when the business question is explicitly:

```text
month
quarter
fiscal period
```

rather than an exact instant.

---

# 51. `.cat` Accessor

Categorical data has a defined set of categories.

```python
status = pd.Series(
    ["pending", "paid", "shipped"],
    dtype="category",
)

print(status.cat.categories)
```

Pandas describes categoricals as values drawn from a defined category set and internally represented through categories and integer codes. citeturn990257search2turn990257search3

Useful `.cat` operations include:

```python
status.cat.categories
status.cat.codes
status.cat.rename_categories(...)
status.cat.reorder_categories(...)
```

The accessor exists because categorical metadata is more than ordinary string text.

---

# 52. Categorical Renaming

Use:

```python
s.cat.rename_categories(...)
```

when the goal is to change category labels.

```python
status = pd.Series(
    ["paid", "pending", "paid"],
    dtype="category",
)

renamed = status.cat.rename_categories(
    {
        "paid": "PAID",
        "pending": "PENDING",
    }
)

print(renamed.tolist())
print(renamed.cat.categories.tolist())
```

This is category metadata manipulation.

It is different from:

```python
status.astype("string").str.upper()
```

which is an ordinary string transformation.

### Production reason

Keeping category semantics intact can make the intent of a controlled field clearer.

---

# 53. Categorical Ordering

Business workflows have semantic order.

For example:

```text
pending < paid < shipped < delivered
```

Alphabetical order is not the desired order.

```python
dtype = pd.CategoricalDtype(
    categories=[
        "pending",
        "paid",
        "shipped",
        "delivered",
    ],
    ordered=True,
)

status = pd.Series(
    ["paid", "pending", "delivered", "shipped"],
    dtype=dtype,
)

print(status.sort_values().tolist())
```

Expected:

```python
["pending", "paid", "shipped", "delivered"]
```

Pandas documents that an ordered categorical uses its category order for sorting rather than lexical order. citeturn990257search2

---

# 54. Rename vs Reorder Categories

These operations solve different problems.

| Operation | Effect |
|---|---|
| `rename_categories` | Change category labels |
| `reorder_categories` | Change category order |
| `add_categories` | Add allowed categories |
| `remove_categories` | Remove selected categories |
| `remove_unused_categories` | Remove categories not present in current data |

### Mental model

```text
rename
    "paid" → "PAID"

reorder
    pending → paid → shipped → delivered
    becomes the defined sort order
```

Renaming does not mean "move this category earlier."

Reordering does not mean "change the values."

---

# 55. Missing Values Inside Accessors

Real Series can contain:

```text
pd.NA
np.nan
None
```

The representation and propagation depend on the dtype and operation.

The key production rule is:

> **Missing is a data state; do not silently turn it into an ordinary value.**

Example:

```python
s = pd.Series(
    [" paid ", None, "shipped"],
    dtype="string",
)

clean = s.str.strip().str.lower()

print(clean.tolist())
```

Logical result:

```text
["paid", missing, "shipped"]
```

---

# 56. `NA` Propagation

A common accessor pattern is:

```text
valid input
    ↓
valid transformed output

missing input
    ↓
missing output
```

This is desirable because it prevents accidental invention of data.

### But track new failures separately

Suppose parsing creates new missing values.

There are two different concepts:

```text
source was already missing
```

and:

```text
source was present but transformation failed
```

Always distinguish them in quality metrics.

---

# 57. `na=False` — Missing Does Not Automatically Mean False

Consider:

```python
s = pd.Series(
    ["error", None, "ok"],
    dtype="string",
)

result = s.str.contains(
    "error",
    regex=False,
    na=False,
)

print(result.tolist())
```

Logical output:

```python
[True, False, False]
```

The missing value has become `False`.

### Correct interpretation

You explicitly selected:

```text
missing
    ↓
False
```

### Why this is powerful

It creates a clean boolean mask for a rule such as:

> Select rows whose message contains "error"; missing messages do not qualify.

### Why it can be wrong

For a data-quality rule:

> Tell me whether the source message was successfully inspected.

missing is:

```text
unknown
```

not necessarily:

```text
false
```

---

# 58. `NA` Propagation vs `na=False`

| Situation | Often appropriate choice |
|---|---|
| Missing means "not matched" | `na=False` |
| Missing means "unknown" | Preserve missing |
| Missing is a source-quality issue | Preserve and separately flag |
| Missing should follow field default semantics | Do not override unnecessarily |

The right decision comes from field semantics.

---

# 59. Unicode Normalization

Unicode normalization helps make equivalent representations more consistent.

Pandas exposes:

```text
.str.normalize("NFKC")
```

### Example

```python
s = pd.Series(
    ["ＡＢＣ", "ABC"],
    dtype="string",
)

normalized = s.str.normalize("NFKC")

print(normalized.tolist())
```

The full-width representation can be normalized toward a canonical compatibility representation.

### Important

Normalization does not mean "delete anything unusual."

It is a specific Unicode transformation.

---

# 60. Why Unicode Normalization Matters

Two strings can look identical or nearly identical to a human while containing different Unicode representations.

That can create:

```text
failed joins
duplicate entities
failed equality checks
inconsistent grouping
```

Potentially affected fields:

```text
customer names
addresses
identifiers
country labels
product names
```

### Key lesson

Visual inspection is not a sufficient equality test for machine keys.

---

# 61. Accents and Diacritics

Accents can be meaningful data.

A name or product description should not automatically have its diacritics removed simply because unaccented strings are easier to compare.

### Production strategy

If the business needs accent-insensitive search:

```text
original_name
+
derived_search_key
```

can be safer than destroying the original.

The transformation must be domain-specific and documented.

---

# 62. Non-Breaking Spaces

A non-breaking space can appear visually like an ordinary space but behave differently.

Example:

```python
s = pd.Series(
    ["C001", "C001\u00A0"],
    dtype="string",
)

print(s.str.len().tolist())
print([repr(value) for value in s.tolist()])
```

The second value contains an additional Unicode character.

### Detection lesson

For suspicious keys, inspect:

```python
repr(value)
len(value)
```

not just:

```python
print(value)
```

### Normalization

Where appropriate:

```python
clean = (
    s.str.normalize("NFKC")
    .str.strip()
)
```

Then validate the canonical key.

---

# 63. Normalization Pipeline for Keys

A useful field-specific sequence is:

```text
raw
 ↓
Unicode normalize
 ↓
trim
 ↓
case normalize if appropriate
 ↓
normalize known whitespace/formatting artifacts
 ↓
validate allowed structure
 ↓
canonical key
```

Example:

```python
keys = pd.Series(
    [" c001 ", "C002", "Ｃ003"],
    dtype="string",
)

canonical = (
    keys
    .str.normalize("NFKC")
    .str.strip()
    .str.upper()
)

print(canonical.tolist())
```

### Do not apply blindly

A key can have strict normalization.

Free text often should not.

---

# 64. String dtype vs `object`

Modern pandas has a dedicated string dtype.

Pandas 3.0 changed ordinary string inference so that string data uses the new dedicated string dtype by default rather than the old generic object representation in common Series construction. citeturn990257search4turn990257search0

### Conceptual comparison

```text
object
    → generic Python-object container
    → can hold mixed Python types

string
    → explicit text semantics
    → clearer schema
    → dedicated missing-value behavior
```

### Why `object` can be dangerous

This:

```text
object
["C001", "C002", 3, None]
```

does not communicate a clean schema.

### Production rule

Inspect dtype and sample values before deciding which accessor operations are appropriate.

---

# 65. Arrow-Backed Strings

Pandas can use PyArrow-backed string data:

```python
s = pd.Series(
    ["a", "b", None],
    dtype="string[pyarrow]",
)
```

Current pandas documentation describes PyArrow integration as offering additional data types, missing-data support, interoperability, IO integration, and native Arrow computation for some supported operations, including strings and datetimes. citeturn990257search1

### Important distinction

These are not necessarily identical:

```text
string[pyarrow]
pd.StringDtype("pyarrow")
pd.ArrowDtype(pa.string())
```

Pandas explicitly documents differences between the string dtype using Arrow storage and a generic ArrowDtype around `pa.string()`. citeturn990257search1

---

# 66. Arrow-Backed String Performance

Arrow-backed strings can improve:

- interoperability;
- memory behavior;
- some string operations;
- IO workflows.

But:

> **Arrow-backed strings are not guaranteed to be faster for every workload.**

Measure:

```text
row count
string length
missingness
operation
backend
pandas version
Arrow version
memory
runtime
```

### Experiment

```python
import pandas as pd

values = ["alpha", "beta", None, "gamma"] * 100_000

s_default = pd.Series(values, dtype="string")
s_arrow = pd.Series(values, dtype="string[pyarrow]")

print(s_default.dtype)
print(s_arrow.dtype)

print(s_default.memory_usage(deep=True))
print(s_arrow.memory_usage(deep=True))
```

Observe your actual environment rather than copying someone else's benchmark.

---

# 67. Vectorized String Operations vs `apply()`

Compare:

```python
vectorized = (
    df["name"]
    .str.strip()
    .str.lower()
)
```

with:

```python
applied = df["name"].apply(
    lambda s: s.strip().lower()
)
```

### Why the accessor often scales better

A suitable vectorized accessor can:

- use pandas-aware implementations;
- delegate to optimized/native kernels when available;
- avoid an explicit Python callback in your code;
- provide clear missing-value semantics.

### Why `apply` can be slower

A Python lambda is called for individual values.

For millions of rows, repeated Python function invocation can become significant.

### But flexibility matters

`apply` may still be correct when:

```text
the transformation is genuinely custom
```

and no suitable vectorized operation exists.

---

# 68. Performance Benchmark Design

A fair benchmark has:

```text
same input
same transformation
same output check
same environment
same measurement method
```

Use:

```python
time.perf_counter()
```

or:

```python
timeit
```

### Example

```python
import time

start = time.perf_counter()

vectorized = (
    df["name"]
    .str.strip()
    .str.lower()
)

vectorized_seconds = time.perf_counter() - start

start = time.perf_counter()

applied = df["name"].apply(
    lambda s: s.strip().lower()
)

apply_seconds = time.perf_counter() - start

assert vectorized.equals(applied)

print(vectorized_seconds)
print(apply_seconds)
```

---

# 69. The Required 5,000,000-Row Benchmark

Build:

```python
n = 5_000_000
```

rows.

Example:

```python
df = pd.DataFrame(
    {
        "name": ["  Alice Smith  "] * n,
    }
)
```

Compare:

```python
df["name"].str.strip().str.lower()
```

with:

```python
df["name"].apply(
    lambda s: s.strip().lower()
)
```

### Record

```text
Python version
pandas version
PyArrow version if relevant
CPU
RAM
row count
dtype
operation
runtime
result equality
memory
```

### Do not fabricate numbers

The chapter does not contain a made-up "vectorized = X seconds" claim.

Run the experiment on the machine where the pipeline will matter.

---

# 70. Mixed Timestamp Formats

A source may send:

```text
2025-09-26 14:30:00
26/09/2025 14:30
2025-09-26T14:30:00Z
2025/09/26 14:30:00
```

These are not automatically interchangeable.

### Production risk

A parser can:

```text
fail
or
successfully produce the wrong interpretation
```

The second case is often more dangerous.

---

# 71. Safe Mixed-Format Parsing

The required strategy is:

> **Try known formats in order, count failures, never guess silently.**

### Example

```python
raw = pd.Series(
    [
        "2025-09-26 14:30:00",
        "26/09/2025 15:45",
        "2025-09-27 09:10:00",
        "not-a-timestamp",
    ],
    dtype="string",
)

parsed_a = pd.to_datetime(
    raw,
    format="%Y-%m-%d %H:%M:%S",
    errors="coerce",
)

remaining = raw.notna() & parsed_a.isna()

parsed_b = pd.to_datetime(
    raw.where(remaining),
    format="%d/%m/%Y %H:%M",
    errors="coerce",
)

parsed = parsed_a.fillna(parsed_b)
```

The accepted formats are explicitly documented in the code.

---

# 72. Count Timestamp Parsing Failures

Track:

```python
source_missing = raw.isna()

failure_mask = raw.notna() & parsed.isna()

failure_count = int(failure_mask.sum())
```

Then inspect:

```python
failed_values = raw.loc[failure_mask]
```

### Why both count and examples?

```text
count
    → operational metric

examples
    → diagnosis and remediation
```

### Preserve raw values

```python
df["raw_timestamp"] = raw
df["timestamp"] = parsed
```

Do not overwrite the evidence needed to investigate failures.

---

# 73. Distinguish Source Missing from Parse Failure

These are different:

```text
raw missing
```

and:

```text
raw present + parse failed
```

Use separate masks:

```python
source_missing = raw.isna()

parse_failed = (
    raw.notna()
    & parsed.isna()
)
```

This gives you two useful metrics:

```text
source_missing_count
parse_failure_count
```

That distinction matters for data-quality monitoring.

---

# 74. Never Guess Silently

Make this a permanent rule:

> **If a timestamp format is unknown, ambiguous, or invalid, do not silently invent an interpretation.**

Possible actions depend on the pipeline contract:

```text
report
quarantine
reject
fail the pipeline
send to remediation
use a documented fallback
```

### Why?

A wrong timestamp can affect:

- event order;
- SLA calculations;
- financial cutoffs;
- reporting dates;
- time buckets;
- downstream joins;
- partition placement.

A plausible wrong value can be harder to detect than a visible failure.

---

# 75. Phone Number Parsing Exercise Contract

Use phone numbers to demonstrate structured regex extraction.

Supported exercise formats:

```text
(212) 555-1234
212-555-1234
+1 212 555 1234
+12125551234
212.555.1234
```

Normalize into:

```text
area_code
number
```

### Example pattern

```python
PHONE_PATTERN = (
    r"^(?:\+?1[\s.-]*)?"
    r"\(?\s*(?P<area_code>\d{3})\s*\)?"
    r"[\s.-]*"
    r"(?P<number>\d{3}[\s.-]*\d{4})$"
)
```

This is a learning-contract regex for the exercise.

It is not a universal international phone-number parser.

---

# 76. Phone Regex — Positive Test Cases

At least five positive cases:

```text
(212) 555-1234
212-555-1234
+1 212 555 1234
+12125551234
212.555.1234
```

Expected:

```text
match
match
match
match
match
```

### Extraction example

```python
phones = pd.Series(
    [
        "(212) 555-1234",
        "212-555-1234",
        "+1 212 555 1234",
        "+12125551234",
        "212.555.1234",
    ],
    dtype="string",
)

parts = phones.str.extract(PHONE_PATTERN)

print(parts)
```

---

# 77. Phone Regex — Negative Test Cases

At least five negative cases:

```text
212-555-123
ABC-555-1234
21255512345
212/555/1234
```

Add at least one more malformed or unsupported value for the exercise.

Example:

```python
invalid = pd.Series(
    [
        "212-555-123",
        "ABC-555-1234",
        "21255512345",
        "212/555/1234",
        "",
    ],
    dtype="string",
)

parts = invalid.str.extract(PHONE_PATTERN)

assert parts["area_code"].isna().all()
```

Negative testing prevents an overly permissive pattern from appearing "correct."

---

# 78. Hands-On Exercise — `text_and_time_cleaning.py`

The roadmap specifies this implementation as the hands-on exercise.

**Do not create this Python file as part of this Markdown task.**

The exercise should be implemented later by the learner.

### Required tasks

1. Clean customer names.
2. Extract phone fields.
3. Split addresses.
4. Parse two timestamp formats.
5. Derive three datetime fields.
6. Benchmark vectorized vs `apply` on 5,000,000 rows.

The following sections fully specify each task.

# 79. Exercise Task 1 — Clean Customer Names

Perform:

```text
1. trim whitespace
2. collapse repeated internal spaces
3. normalize Unicode
4. title case
```

### Suggested transformation

```python
names = (
    df["customer_name"]
    .astype("string")
    .str.normalize("NFKC")
    .str.strip()
    .str.replace(r"\s+", " ", regex=True)
    .str.title()
)
```

### Required tests

Test at least:

- leading whitespace;
- trailing whitespace;
- repeated internal whitespace;
- missing names;
- Unicode variants;
- punctuation;
- a name for which title casing is not the desired canonical business representation.

### Production note

Do not overwrite an authoritative source name if the transformed field is only a presentation form.

Consider:

```text
customer_name_raw
customer_name_normalized
```

when auditability or legal identity matters.

---

# 80. Exercise Task 2 — Extract `area_code` and `number`

Use:

```text
.str.extract(...)
```

with named groups.

### Required output

```text
area_code
number
```

### Required controls

- five supported phone formats;
- at least five positive regex cases;
- at least five negative regex cases;
- count unparseable non-missing values;
- preserve the raw phone field;
- inspect invalid examples.

### Example

```python
extracted = df["phone"].str.extract(PHONE_PATTERN)

df["area_code"] = extracted["area_code"]
df["number"] = extracted["number"]

phone_failed = (
    df["phone"].notna()
    & df["area_code"].isna()
)

print("phone failures:", int(phone_failed.sum()))
print(df.loc[phone_failed, ["phone"]])
```

### Additional normalization

If the exercise wants `number` as seven digits:

```python
df["number"] = (
    df["number"]
    .str.replace(r"\D+", "", regex=True)
)
```

Then assert the expected width for parsed values.

---

# 81. Exercise Task 3 — Split `City, State ZIP`

Input contract:

```text
City, State ZIP
```

Use:

```python
parts = df["address"].str.split(",", expand=True)
```

Rename explicitly:

```python
parts = parts.rename(
    columns={
        0: "city",
        1: "state_zip",
    }
)
```

### Malformed cases to test

```text
"Malformed Address"
"New York, NY 10001, USA"
""
"   "
None
```

### Required validation

Check:

```text
expected columns
missing city
missing state_zip
extra separators
whitespace
```

Do not pretend the simple exercise format is a universal address parser.

---

# 82. Exercise Task 4 — Parse Timestamp Column

The exercise contains two known formats.

```text
A: 2025-09-26 14:30:00
B: 26/09/2025 15:45
```

### Requirements

1. identify format A;
2. identify format B;
3. parse deliberately;
4. report failures;
5. preserve raw values;
6. produce a typed datetime column;
7. do not silently guess.

### Suggested implementation

```python
raw = df["order_timestamp"].astype("string")

parsed_a = pd.to_datetime(
    raw,
    format="%Y-%m-%d %H:%M:%S",
    errors="coerce",
)

remaining = raw.notna() & parsed_a.isna()

parsed_b = pd.to_datetime(
    raw.where(remaining),
    format="%d/%m/%Y %H:%M",
    errors="coerce",
)

parsed = parsed_a.fillna(parsed_b)

df["order_timestamp_parsed"] = parsed

parse_failed = (
    raw.notna()
    & parsed.isna()
)

print("timestamp parse failures:", int(parse_failed.sum()))
print(df.loc[parse_failed, ["order_timestamp"]])
```

### What the implementation must not do

Do not replace the source column with an unmeasured coercion such as:

```python
df["order_timestamp"] = pd.to_datetime(
    df["order_timestamp"],
    errors="coerce",
)
```

and then assume success because the pipeline did not crash.

---

# 83. Exercise Task 5 — `order_hour`

Use:

```python
df["order_hour"] = (
    df["order_timestamp_parsed"]
    .dt.hour
)
```

### Expected semantics

An integer hour from:

```text
0
...
23
```

depending on the timestamp's timezone.

### Validation

```python
valid = df["order_timestamp_parsed"].notna()

assert (
    df.loc[valid, "order_hour"]
    .between(0, 23)
    .all()
)
```

---

# 84. Exercise Task 5 — `order_weekday`

Use:

```python
df["order_weekday"] = (
    df["order_timestamp_parsed"]
    .dt.dayofweek
)
```

Expected mapping:

```text
Monday    0
Tuesday   1
Wednesday 2
Thursday  3
Friday    4
Saturday  5
Sunday    6
```

Validate the expected range:

```python
valid = df["order_timestamp_parsed"].notna()

assert (
    df.loc[valid, "order_weekday"]
    .between(0, 6)
    .all()
)
```

---

# 85. Exercise Task 5 — `order_week_start`

The definition of "week start" must be explicit.

For a Monday-start week:

```python
ts = df["order_timestamp_parsed"]

df["order_week_start"] = (
    ts
    - pd.to_timedelta(ts.dt.dayofweek, unit="D")
).dt.normalize()
```

### Why normalize?

If the source timestamp is:

```text
Friday 14:35
```

subtracting four days produces:

```text
Monday 14:35
```

`normalize()` then moves it to:

```text
Monday 00:00
```

### Production rule

Document:

```text
week starts Monday
```

or:

```text
week starts Sunday
```

depending on the business definition.

---

# 86. Exercise Task 6 — Benchmark on 5,000,000 Rows

Build 5,000,000 rows.

```python
n = 5_000_000

df_bench = pd.DataFrame(
    {
        "name": ["  Alice Smith  "] * n,
    }
)
```

Compare:

```python
vectorized = (
    df_bench["name"]
    .str.strip()
    .str.lower()
)
```

with:

```python
applied = df_bench["name"].apply(
    lambda s: s.strip().lower()
)
```

### Required methodology

Use:

```python
import time

start = time.perf_counter()
# vectorized
vectorized_seconds = time.perf_counter() - start
```

Then measure the `apply` version separately.

### Required correctness check

```python
assert vectorized.equals(applied)
```

### Required reporting

Record actual:

```text
row count
runtime
dtype
pandas version
Python version
CPU
RAM
result equality
```

Never fabricate a runtime number.

---

# 87. Exercise Quality Gate

The exercise is not complete merely because the code runs.

The final implementation should answer:

```text
How many rows entered?
How many names were normalized?
How many phones parsed?
How many phone values failed?
How many addresses were malformed?
How many timestamps failed?
What raw values caused failures?
Are derived datetime fields correctly typed?
Do vectorized and apply results match?
```

This turns a coding exercise into an engineering exercise.

---

# 88. Debugging Workflow

When something fails:

```text
raw data
   ↓
dtype
   ↓
small reproduction
   ↓
minimal operation
   ↓
expected result
   ↓
actual result
   ↓
root cause
   ↓
corrected transformation
   ↓
regression test
```

Do not debug a giant pipeline when a five-value Series can reproduce the problem.

---

# 89. Debugging Case 1 — `.str` on an Inappropriate Column

### Buggy

```python
df = pd.DataFrame({"value": [1, 2, 3]})
df["value"].str.strip()
```

### Root cause

The values are numeric.

### Correct thinking

First inspect:

```python
print(df["value"].dtype)
```

If the field is actually a code and should be treated as text, convert deliberately:

```python
df["value"] = df["value"].astype("string")
```

provided that conversion matches the source contract.

---

# 90. Debugging Case 2 — Unexpected `object`

### Symptom

```text
object
```

appears for a column expected to contain text.

### Investigation

```python
print(df["value"].map(type).value_counts())
```

### Root cause

`object` can hide mixed Python values.

### Correct approach

Establish an intentional schema rather than guessing from the dtype label.

---

# 91. Debugging Case 3 — Whitespace Breaks a Join

### Symptom

```text
left  = "C001"
right = " C001 "
```

do not match.

### Correct pattern

Apply the same canonicalization rule to both keys:

```python
left["customer_id"] = (
    left["customer_id"]
    .astype("string")
    .str.strip()
)

right["customer_id"] = (
    right["customer_id"]
    .astype("string")
    .str.strip()
)
```

### Prevention

Canonicalize integration keys at the source boundary when justified.

---

# 92. Debugging Case 4 — Case Mismatch

### Symptom

```text
"IN"
"in"
"In"
```

form separate groups.

### Correct pattern

For a case-insensitive code:

```python
canonical = (
    s.astype("string")
    .str.strip()
    .str.upper()
)
```

---

# 93. Debugging Case 5 — Non-Breaking Space

### Symptom

The printed values look the same.

### Investigation

```python
s = pd.Series(
    ["C001", "C001\u00A0"],
    dtype="string",
)

print([repr(value) for value in s.tolist()])
print(s.str.len().tolist())
```

### Prevention

Treat invisible whitespace as a real data-quality dimension.

---

# 94. Debugging Case 6 — Unicode Normalization Difference

### Symptom

Visually similar values are unequal.

### Investigation

```python
s = pd.Series(
    ["ＡＢＣ", "ABC"],
    dtype="string",
)

print(s.str.normalize("NFKC").tolist())
```

Use normalization only when the field semantics justify it.

---

# 95. Debugging Case 7 — Empty Strings vs Missing

These are different states:

```text
""
None
pd.NA
```

Example:

```python
s = pd.Series(
    ["", None, "   "],
    dtype="string",
)

clean = s.str.strip()

print(clean.tolist())
```

After stripping, whitespace-only becomes empty text, while missing remains missing.

If the field contract says empty means missing:

```python
clean = clean.mask(clean.eq(""))
```

Do this intentionally.

---

# 96. Debugging Case 8 — `contains()` Produces Missing

### Symptom

The mask contains `NA`.

### Cause

Missing source values are being preserved under the dtype/operation semantics.

### If false is semantically correct

```python
mask = s.str.contains(
    "error",
    regex=False,
    na=False,
)
```

### If missing means unknown

Do not force it to false. Preserve and handle the missing state.

---

# 97. Debugging Case 9 — Literal Regex Special Character

A literal plus sign:

```text
+
```

should not be searched as an unescaped regex operator.

### Literal search

```python
s.str.contains(
    "+",
    regex=False,
    na=False,
)
```

### Regex representation

```python
s.str.contains(
    r"\+",
    regex=True,
    na=False,
)
```

---

# 98. Debugging Case 10 — Regex Used When Literal Search Was Intended

### Bug

```python
s.str.contains(".", regex=True)
```

In regex, `.` means "any character."

### Correct literal search

```python
s.str.contains(".", regex=False, na=False)
```

or escaped regex:

```python
s.str.contains(r"\.", regex=True, na=False)
```

---

# 99. Debugging Case 11 — Wrong Regex Escaping

Prefer raw strings for regex patterns containing backslashes:

```python
pattern = r"\d+"
```

This makes the distinction between Python-string escaping and regex escaping easier to understand.

---

# 100. Debugging Case 12 — Wrong Capture Group Count

Every capturing group can become an output field.

Instead of:

```python
r"(\d{3})-(\d{4})"
```

use meaningful names:

```python
r"(?P<area_code>\d{3})-(?P<number>\d{4})"
```

Use non-capturing groups:

```text
(?:...)
```

for structural grouping that should not become an output column.

---

# 101. Debugging Case 13 — `extractall()` Changes Grain

### Symptom

Input has 100 rows, output has 137 rows.

### Cause

One source row produced multiple matches.

### Prevention

Define the output grain before extraction.

```text
one source row
```

is not the same as:

```text
one match row
```

---

# 102. Debugging Case 14 — `findall()` Returns Lists

That is expected.

```python
s.str.findall(r"P\d{3}")
```

returns values such as:

```python
["P001", "P002"]
```

If you need one row per match, use `extractall`.

---

# 103. Debugging Case 15 — `split(expand=True)` Unexpected Shape

Different rows can have different token counts.

Investigate separator frequency:

```python
print(s.str.count(",").value_counts(dropna=False))
```

Validate the contract before assigning fixed semantic column names.

---

# 104. Debugging Case 16 — `rsplit(n=1)` Misunderstood

```python
s.str.rsplit("/", n=1)
```

means:

> Split from the right, at most once.

It does not mean:

> Split every separator and keep the last two arbitrary pieces.

Phrase the requirement first:

> "I need the last path component."

Then `rsplit(n=1)` is a natural expression.

---

# 105. Debugging Case 17 — `partition()` Adds a Separator Column

This is intentional.

```python
s.str.partition("=")
```

returns:

```text
before
separator
after
```

Use `split` when the separator itself is not part of the required output.

---

# 106. Debugging Case 18 — `str.cat()` Missing Values

Investigate:

```python
first.isna()
last.isna()
```

Then define the desired rule.

Examples:

```text
missing first + valid last → missing
```

or:

```text
missing first + valid last → last
```

There is no universal business answer.

---

# 107. Debugging Case 19 — `.dt` on String Data

### Symptom

```python
df["created_at"].dt.hour
```

fails.

### Cause

The column has not been parsed to datetime.

### Correct pattern

```python
df["created_at"] = pd.to_datetime(
    df["created_at"],
    format="%Y-%m-%d %H:%M:%S",
    errors="coerce",
)
```

Then measure the newly missing values.

---

# 108. Debugging Case 20 — Timestamp Parse Failures

Use:

```python
failure_mask = (
    raw.notna()
    & parsed.isna()
)

print(raw.loc[failure_mask])
```

Look for:

- malformed dates;
- wrong separators;
- wrong order;
- unexpected time component;
- timezone differences;
- source format drift.

---

# 109. Debugging Case 21 — Mixed Timestamp Formats

A single explicit format cannot parse two different known representations.

Use a controlled sequence:

```text
known format A
↓
remaining
↓
known format B
↓
remaining failures
```

Do not hide format variation behind a generic guessing strategy.

---

# 110. Debugging Case 22 — Silent Timestamp Guessing

Input:

```text
03/04/2025
```

is ambiguous without a documented convention.

Possible interpretations can differ.

### Production answer

Require the source contract to say which convention applies.

Never silently select one interpretation because it "looks likely."

---

# 111. Debugging Case 23 — `tz_convert` on Naive Data

### Bug

```python
s = pd.Series(
    pd.to_datetime(["2025-09-26 14:00:00"])
)

s.dt.tz_convert("Asia/Kolkata")
```

### Root cause

The timestamp has no timezone.

### Correct approach

First establish what the naive clock value means.

Only then perform timezone conversion.

---

# 112. Debugging Case 24 — Wrong Floor Bucket

For:

```text
2025-09-26 14:59:59
```

hourly floor should conceptually be:

```text
2025-09-26 14:00:00
```

If it is not, inspect:

```text
frequency
timezone
operation
input dtype
```

---

# 113. Debugging Case 25 — Floor/Ceil/Round Confusion

For an ordinary non-boundary example:

```text
14:03
```

the expected pattern is:

```text
floor → 14:00
ceil  → 15:00
round → 14:00
```

For:

```text
14:58
```

the expected pattern is:

```text
floor → 14:00
ceil  → 15:00
round → 15:00
```

Test exact boundaries separately.

---

# 114. Debugging Case 26 — `strftime()` Too Early

### Bad design

```python
df["created_at"] = (
    df["created_at"]
    .dt.strftime("%Y-%m-%d")
)
```

### Problem

The canonical timestamp is now a string.

### Correct design

```python
df["created_at_label"] = (
    df["created_at"]
    .dt.strftime("%Y-%m-%d")
)
```

Keep the original typed datetime column.

---

# 115. Debugging Case 27 — Period Conversion Misused

A `Period` expresses a calendar interval.

Do not use:

```text
.dt.to_period("M")
```

as a replacement for exact timestamp storage.

Use it when the business question is explicitly about a calendar period.

---

# 116. Debugging Case 28 — Missing Values Propagate

If a derived accessor field is missing, trace:

```text
was source missing?
```

versus:

```text
did transformation fail?
```

These should be different quality metrics when the pipeline needs diagnosis.

---

# 117. Debugging Case 29 — Category Rename Does Not Change Sort Order

Renaming:

```text
paid → PAID
```

does not mean:

```text
PAID should now sort before pending.
```

Use `reorder_categories` when the semantic order must change.

---

# 118. Debugging Case 30 — `apply()` Introduced Unnecessarily

### Before

```python
df["name"].apply(lambda s: s.strip())
```

### Better when appropriate

```python
df["name"].str.strip()
```

Search for an existing accessor before adding custom Python code.

---

# 119. Debugging Case 31 — Regex Passes Samples but Fails Production

Add source-variation fixtures:

```text
missing
empty
extra whitespace
alternate punctuation
alternate case
optional prefix
unexpected separator
malformed structure
```

Then preserve old positive and negative tests.

---

# 120. Debugging Case 32 — Visually Identical Keys Fail Equality

Use:

```python
print(repr(value))
print(len(value))
```

and Unicode normalization where appropriate.

A UI rendering is not a reliable data-contract test.

---

# 121. Debugging Case 33 — `na=False` Changes Meaning

Document the decision:

```python
# Missing messages are intentionally classified as "not an error match".
mask = df["message"].str.contains(
    "error",
    regex=False,
    na=False,
)
```

This prevents future developers from assuming that `False` was the source value.

---

# 122. Debugging Case 34 — New Production Format Appears

When the source adds:

```text
new phone format
new timestamp format
new delimiter
```

do not silently broaden transformations.

Instead:

1. confirm the source contract;
2. document the new format;
3. add positive tests;
4. add negative tests;
5. preserve previous tests;
6. measure new failures;
7. deploy intentionally.

---

# 123. Testing Strategy — Complete Coverage

A practical `pytest` suite for this topic should cover:

```text
string transformations
regex extraction
regex replacement
split/rsplit/partition
cat
datetime properties
datetime bucketing
timezone conversion
formatting
period conversion
categoricals
missing values
Unicode
timestamp parsing
performance result equivalence
```

---

# 124. String Tests

Test:

```text
strip
lower
upper
title
len
startswith
endswith
contains
replace
slice
zfill
pad
```

Example:

```python
def test_string_accessors():
    s = pd.Series(
        [" A ", "b", None],
        dtype="string",
    )

    assert s.str.strip().iloc[0] == "A"
    assert s.str.lower().iloc[1] == "b"
    assert s.str.upper().iloc[1] == "B"
    assert s.str.len().iloc[0] == 3
```

---

# 125. Regex Tests

Every regex used in the exercise must have:

```text
≥ 5 positive examples
≥ 5 negative examples
```

Also test:

```text
missing
malformed
unexpected separators
named groups
```

Example:

```python
def test_phone_extract_named_groups():
    s = pd.Series(
        ["212-555-1234"],
        dtype="string",
    )

    result = s.str.extract(PHONE_PATTERN)

    assert result.columns.tolist() == [
        "area_code",
        "number",
    ]
    assert result.loc[0, "area_code"] == "212"
```

---

# 126. Extract vs Extractall Test

```python
def test_extractall_multiple_matches():
    s = pd.Series(
        ["P001 P002"],
        dtype="string",
    )

    result = s.str.extractall(
        r"(?P<code>P\d{3})"
    )

    assert len(result) == 2
    assert result["code"].tolist() == [
        "P001",
        "P002",
    ]
```

This verifies both match count and values.

---

# 127. `findall` Test

```python
def test_findall():
    s = pd.Series(
        ["P001 P002"],
        dtype="string",
    )

    result = s.str.findall(r"P\d{3}")

    assert result.iloc[0] == [
        "P001",
        "P002",
    ]
```

This confirms the list-like result contract.

---

# 128. Splitting Tests

Test:

```text
split
split(expand=True)
rsplit
partition
cat
```

Example:

```python
def test_split_expand():
    s = pd.Series(
        ["New York, NY 10001"],
        dtype="string",
    )

    result = s.str.split(",", expand=True)

    assert result.shape == (1, 2)
    assert result.iloc[0, 0] == "New York"
    assert result.iloc[0, 1] == " NY 10001"
```

---

# 129. Datetime Property Tests

```python
def test_datetime_properties():
    s = pd.Series(
        pd.to_datetime(
            ["2025-09-30 14:35:00"],
            utc=True,
        )
    )

    assert s.dt.year.iloc[0] == 2025
    assert s.dt.month.iloc[0] == 9
    assert s.dt.day.iloc[0] == 30
    assert s.dt.hour.iloc[0] == 14
    assert s.dt.dayofweek.iloc[0] == 1
    assert s.dt.quarter.iloc[0] == 3
    assert bool(s.dt.is_month_end.iloc[0])
```

---

# 130. Datetime Bucketing Tests

```python
def test_datetime_bucketing():
    s = pd.Series(
        pd.to_datetime(
            ["2025-09-30 14:35:30"]
        )
    )

    assert s.dt.floor("h").iloc[0] == pd.Timestamp(
        "2025-09-30 14:00:00"
    )

    assert s.dt.ceil("h").iloc[0] == pd.Timestamp(
        "2025-09-30 15:00:00"
    )

    assert s.dt.round("h").iloc[0] == pd.Timestamp(
        "2025-09-30 15:00:00"
    )
```

---

# 131. Timezone Conversion Test

```python
def test_timezone_conversion():
    s = pd.Series(
        pd.to_datetime(
            ["2025-09-26 14:00:00+00:00"],
            utc=True,
        )
    )

    converted = s.dt.tz_convert(
        "Asia/Kolkata"
    )

    assert converted.dt.hour.iloc[0] == 19
```

The test encodes a known instant and expected local representation.

---

# 132. Formatting Test

```python
def test_strftime():
    s = pd.Series(
        pd.to_datetime(
            ["2025-09-26 14:35:00"]
        )
    )

    result = s.dt.strftime("%Y-%m-%d")

    assert result.iloc[0] == "2025-09-26"
```

Also verify that the canonical source remains datetime in the pipeline.

---

# 133. Period Conversion Test

```python
def test_to_period_month():
    s = pd.Series(
        pd.to_datetime(["2025-09-26"])
    )

    result = s.dt.to_period("M")

    assert str(result.iloc[0]) == "2025-09"
```

Test fiscal-period behavior separately when that concept is actually required.

---

# 134. Categorical Tests

Test:

```text
categories
codes
rename_categories
reorder_categories
```

Example:

```python
def test_categorical_order():
    dtype = pd.CategoricalDtype(
        categories=[
            "pending",
            "paid",
            "shipped",
            "delivered",
        ],
        ordered=True,
    )

    s = pd.Series(
        ["shipped", "pending", "paid"],
        dtype=dtype,
    )

    assert s.sort_values().tolist() == [
        "pending",
        "paid",
        "shipped",
    ]
```

---

# 135. Missing-Value Tests

Test:

```text
pd.NA
np.nan
None
na=False
```

Example:

```python
import numpy as np

def test_missing_contains():
    s = pd.Series(
        ["error", pd.NA, np.nan, None],
        dtype="string",
    )

    result = s.str.contains(
        "error",
        regex=False,
        na=False,
    )

    assert result.tolist() == [
        True,
        False,
        False,
        False,
    ]
```

---

# 136. Unicode Tests

Test:

- composed/decomposed representations where relevant;
- full-width/compatibility variants;
- non-breaking spaces;
- normalized keys.

Example:

```python
def test_unicode_normalization():
    s = pd.Series(
        ["ＡＢＣ", "ABC"],
        dtype="string",
    )

    result = s.str.normalize("NFKC")

    assert result.tolist() == [
        "ABC",
        "ABC",
    ]
```

---

# 137. Mixed Timestamp Tests

Test:

```text
format A
format B
invalid
missing
failure count
raw failure evidence
```

Example:

```python
def test_mixed_timestamp_failure_count():
    raw = pd.Series(
        [
            "2025-09-26 14:30:00",
            "26/09/2025 15:45",
            "invalid",
            None,
        ],
        dtype="string",
    )

    first = pd.to_datetime(
        raw,
        format="%Y-%m-%d %H:%M:%S",
        errors="coerce",
    )

    second_mask = raw.notna() & first.isna()

    second = pd.to_datetime(
        raw.where(second_mask),
        format="%d/%m/%Y %H:%M",
        errors="coerce",
    )

    parsed = first.fillna(second)

    failures = raw.notna() & parsed.isna()

    assert int(failures.sum()) == 1
```

---

# 138. Performance Testing Rule

Do not write:

```python
assert runtime < 0.2
```

unless the environment is controlled tightly enough for that threshold to be meaningful.

Do write:

```python
assert vectorized_result.equals(apply_result)
```

and record the actual timings.

---

# 139. Edge Cases — Detailed Checklist

Use these as test fixtures:

- [ ] empty Series;
- [ ] all missing values;
- [ ] empty strings;
- [ ] whitespace-only strings;
- [ ] very long strings;
- [ ] mixed string/object values;
- [ ] Unicode variants;
- [ ] non-breaking spaces;
- [ ] regex metacharacters;
- [ ] no regex matches;
- [ ] multiple regex matches;
- [ ] malformed phone numbers;
- [ ] addresses without separators;
- [ ] addresses with extra separators;
- [ ] missing timestamps;
- [ ] malformed timestamps;
- [ ] multiple timestamp formats;
- [ ] timezone-aware timestamps;
- [ ] timezone-naive timestamps;
- [ ] timestamps around DST;
- [ ] invalid timezone conversion;
- [ ] month-end timestamps;
- [ ] leap-day timestamps;
- [ ] floor boundary;
- [ ] ceil boundary;
- [ ] round boundary;
- [ ] `extractall` with zero matches;
- [ ] variable token counts after split;
- [ ] categorical values outside expected categories.

---

# 140. Edge Case — Empty Series

```python
s = pd.Series([], dtype="string")

result = s.str.strip()

assert len(result) == 0
```

The operation should not create fake rows.

---

# 141. Edge Case — All Missing

```python
s = pd.Series(
    [pd.NA, pd.NA],
    dtype="string",
)

result = s.str.lower()

assert result.isna().all()
```

---

# 142. Edge Case — Very Long Strings

For long text:

```text
measure memory
measure runtime
test regex cost
```

Do not assume a pattern that is cheap for 20 characters is equally cheap for large text blobs.

---

# 143. Edge Case — Regex Metacharacters

If searching for literals such as:

```text
.
+
*
?
(
)
[
]
```

choose:

```text
regex=False
```

where literal behavior is intended, or escape appropriately when regex is required.

---

# 144. Edge Case — No Matches

For:

```python
s.str.findall(pattern)
```

a no-match row can produce an empty list.

For:

```python
s.str.extract(pattern)
```

an unmatched capture can produce missing output.

For:

```python
s.str.extractall(pattern)
```

there may be no match row for that source value.

These are different output models.

---

# 145. Edge Case — Variable Split Counts

Input:

```text
"A,B"
"A,B,C"
"A"
```

should make you question whether:

```text
.str.split(",", expand=True)
```

can safely be assigned to fixed fields.

Validate shape before assuming the schema.

---

# 146. Edge Case — Malformed Phones

Test:

```text
too few digits
too many digits
unsupported separators
bad country prefix
letters
empty string
```

A failed parse should become an observable data-quality result, not disappear silently.

---

# 147. Edge Case — Missing Timestamps

Distinguish:

```text
source missing
```

from:

```text
source present but parse failed
```

Keep both metrics.

---

# 148. Edge Case — DST

Timezone-aware transformations can encounter daylight-saving transitions.

Around a transition, local wall-clock values can be:

```text
nonexistent
ambiguous
```

For this topic, the main rule is:

> Do not invent timezone meaning from an ambiguous local timestamp.

Establish the source timezone contract first, and use timezone-aware data where the application requires it.

For detailed DST localization semantics, revisit Topic 09.

---

# 149. Edge Case — Month End and Leap Day

Test:

```text
2024-02-29
2025-02-28
2025-04-30
2025-09-30
```

and verify:

```text
.dt.is_month_end
```

The end of a month is not always day 30 or day 31.

---

# 150. Edge Case — Categorical Values Outside Expected Set

A categorical field has an explicit category set.

If incoming data contains a new status:

```text
"refunded"
```

while the declared categories are:

```text
pending
paid
shipped
delivered
```

treat that as a schema/data-quality event.

Do not silently interpret an unexpected category as one of the existing categories.

---

# 151. Production Scenarios

## Customer master

```text
raw customer key
→ Unicode normalization
→ whitespace normalization
→ case normalization
→ validation
→ canonical matching key
```

Keep the original name and key where traceability matters.

## E-commerce orders

Use accessors to normalize:

```text
order_id
customer_id
product_id
status
order_timestamp
```

## Event logs

Use regex extraction for structured message fields.

## API payloads

Parse timestamp strings to typed datetimes before `.dt` operations.

## Banking/financial data

Be especially careful with:

```text
reference codes
transaction IDs
timestamp meaning
cut-off times
```

## IoT

Normalize device IDs and derive time fields from event timestamps.

## Data quality

Use string length, pattern checks, and parsing-failure metrics as pipeline quality controls.

---

# 152. Production Key Normalization Pattern

```text
raw_key
   ↓
Unicode normalize
   ↓
strip
   ↓
case normalize if appropriate
   ↓
remove known formatting artifacts
   ↓
validate pattern
   ↓
canonical key
```

### Properties of a good normalization rule

It is:

```text
deterministic
documented
field-specific
tested
observable
reversible where auditability requires it
```

"Reversible" here often means the raw input is retained, not that every normalization operation can mathematically reconstruct the source.

---

# 153. Field Semantics — Key vs Free Text

This distinction prevents many bad transformations.

| Field type | Typical strategy |
|---|---|
| Machine key | Strict canonicalization |
| Country code | Trim/case/format normalization |
| Controlled status | Category semantics |
| Person name | Conservative normalization |
| Address | Contract-specific parsing |
| Free-text note | Preserve meaning; avoid aggressive normalization |

The same `.str` method can be correct for one field and wrong for another.

---

# 154. Data Representation vs Presentation

Think in two layers:

```text
canonical pipeline representation
            ↓
       transformation
            ↓
presentation/export representation
```

For timestamps:

```text
datetime
    ↓
strftime
    ↓
string label
```

Do not reverse that ordering unnecessarily.

---

# 155. Data Quality Rule Catalog

| Rule | Example detection | Example action |
|---|---|---|
| Name not whitespace-only | `strip().eq("")` | quarantine |
| Code has required prefix | `startswith()` | reject/review |
| Code has required width | `len()` | reject/review |
| Phone parses | `extract()` | quarantine |
| Address has separator | `contains(..., regex=False)` | review |
| Timestamp parses | explicit formats | quarantine |
| Timestamp timezone is expected | dtype/timezone validation | reject/review |
| Unknown timestamp format | unresolved after known formats | fail/quarantine |
| Canonical key valid | normalized pattern | reject/review |

These are examples; the actual action depends on the pipeline contract.

---

# 156. Performance Engineering — What to Measure

Measure:

```text
row count
average/max string length
dtype
storage backend
missingness
regex complexity
runtime
peak/working memory
```

### Three questions

1. Is the transformation correct?
2. Is the transformation observable?
3. Is the transformation fast enough?

Do not start with question 3 and accidentally optimize an incorrect parser.

---

# 157. Vectorized Accessor vs Python Loop

Typical hierarchy for ordinary supported transformations:

```text
appropriate pandas accessor
        ↓
custom vectorized formulation
        ↓
apply(custom Python function)
        ↓
explicit Python loop
```

This is not an absolute speed ranking.

It is a useful starting point for code review.

The closer the operation is to a built-in accessor, the more reason you have to use the accessor rather than reinvent the behavior.

---

# 158. Arrow-Backed Strings — When to Consider

Consider Arrow-backed strings when:

- the pipeline already uses Arrow/Parquet heavily;
- interoperability is important;
- supported operations benefit in your environment;
- memory measurements justify the representation.

Current pandas documents Arrow integration for strings and datetimes, but also notes that supported functionality depends on integration with the pandas API. citeturn990257search1

### Decision rule

```text
semantic fit
+
operation support
+
measured memory/runtime
+
ecosystem compatibility
```

not:

```text
Arrow = always better
```

---

# 159. Regex Performance — Practical Guidance

Prefer simple operations for simple contracts.

```text
prefix check
    → startswith

suffix check
    → endswith

literal substring
    → contains(..., regex=False)

position
    → slice
```

Use regex for:

```text
variable separators
structured captures
pattern validation
pattern replacement
```

### Test production variations

A regex can be logically correct and still operationally unsuitable if the source contract was incomplete.

---

# 160. Time Parsing — Practical Guidance

For known formats:

```text
explicit format
→ predictable semantics
→ explicit failures
```

For mixed known formats:

```text
format A
→ remaining
→ format B
→ remaining failures
```

For unknown format:

```text
do not silently guess
```

This is both a correctness principle and an observability principle.

---

# 161. SQL/Data Warehouse Translation

Conceptual mappings:

| pandas | Typical SQL concept |
|---|---|
| `.str.strip()` | `TRIM` |
| `.str.lower()` | `LOWER` |
| `.str.upper()` | `UPPER` |
| `.str.contains(..., regex=False)` | `LIKE`/substring |
| regex `contains` | regex predicate |
| `extract` | regex/string extraction |
| `split` | split/string function |
| `partition` | substring/position |
| `cat` | concatenation |
| `.dt.year` | year/date part |
| `.dt.month` | month/date part |
| `.dt.floor("h")` | hour truncation |
| `.dt.tz_convert` | timezone conversion |
| `.dt.strftime` | date formatting |
| `.dt.to_period` | calendar period derivation |

Exact function names differ among PostgreSQL, BigQuery, Snowflake, Spark SQL, SQL Server, and other engines.

---

# 162. Production Review Questions

### String

1. Is this field a key or free text?
2. Is whitespace normalization required?
3. Is case normalization allowed?
4. Is Unicode normalization relevant?
5. Can the source contain invisible spaces?
6. Does regex add real value?

### Regex

7. Does one row have zero, one, or many matches?
8. Are capture groups named?
9. Are negative cases tested?
10. What happens on malformed input?

### Datetime

11. Is the source format documented?
12. Is the timezone documented?
13. Is the value naive or aware?
14. Can parsing fail?
15. Are failures counted?
16. Should the timestamp remain typed?
17. Is bucketing using the intended operation?

### Performance

18. Is `apply` actually necessary?
19. What does the benchmark show on actual data?
20. Does the chosen string backend make sense?

---

# 163. Production Checklist — String

```text
[ ] Source meaning is known
[ ] Key vs free text is known
[ ] Whitespace strategy is intentional
[ ] Case strategy is intentional
[ ] Unicode normalization is considered
[ ] Non-breaking spaces are considered
[ ] Regex is necessary
[ ] Regex has ≥5 positive and ≥5 negative examples
[ ] Missing semantics are defined
[ ] na=False is used only when appropriate
[ ] Normalized output is validated
[ ] Raw source is preserved when failures must be audited
```

---

# 164. Production Checklist — Datetime

```text
[ ] Source timestamp formats are documented
[ ] Timezone meaning is documented
[ ] Naive vs aware state is known
[ ] Known formats are parsed explicitly
[ ] Parse failures are counted
[ ] Failed raw values can be inspected
[ ] Unknown formats are reported
[ ] Silent guessing is prohibited
[ ] Datetimes remain datetime values until presentation
[ ] Timezone conversion is explicit
[ ] Bucketing semantics are explicit
[ ] Week-start definition is explicit where needed
```

---

# 165. Production Checklist — Performance

```text
[ ] Appropriate vectorized accessor used
[ ] apply justified if present
[ ] String dtype is intentional
[ ] Arrow-backed strings considered where appropriate
[ ] Runtime measured
[ ] Memory measured
[ ] Result equivalence verified for benchmarks
[ ] Benchmark environment recorded
[ ] No universal speed claim made from one experiment
```

---

# 166. Decision Tree — Text

```text
Need trimming?
    ↓
.str.strip()

Need case normalization?
    ↓
.str.lower() / .str.upper()

Need display-style capitalization?
    ↓
.str.title()

Need prefix?
    ↓
.str.startswith()

Need suffix?
    ↓
.str.endswith()

Need literal substring?
    ↓
.str.contains(..., regex=False)

Need regex?
    ↓
.str.contains(..., regex=True)

Need captured fields?
    ↓
.str.extract()

Need all matches?
    ↓
.str.findall() or .str.extractall()

Need splitting?
    ↓
.str.split / .str.rsplit / .str.partition

Need combining?
    ↓
.str.cat()
```

---

# 167. Decision Tree — Datetime

```text
Need calendar component?
    ↓
.dt.year / month / day / hour / ...

Need fixed-frequency bucket?
    ↓
.dt.floor / ceil / round

Need timezone conversion?
    ↓
.dt.tz_convert

Need output text?
    ↓
.dt.strftime

Need calendar period?
    ↓
.dt.to_period
```

---

# 168. Anti-Pattern Review Matrix

| Anti-pattern | Why tempting | Safer production approach |
|---|---|---|
| `apply()` for simple `.str` work | Familiar Python | Use accessor |
| Regex for a simple prefix | Looks powerful | `startswith` |
| Aggressive free-text normalization | Looks cleaner | Preserve meaning |
| `na=False` everywhere | Easy boolean masks | Define missing semantics |
| `errors="coerce"` with no metrics | Pipeline keeps moving | Count and inspect failures |
| Timestamp guessing | Less code | Known-format parsing |
| Early `strftime` | Report-ready appearance | Preserve datetime |
| Untested regex | Happy path passes | 5 positive + 5 negative minimum |
| Title-case every name | Looks polished | Treat as presentation normalization |
| Ignore Unicode | Values look identical | Normalize/test where appropriate |

---

# 169. Reconciliation

For transformations expected to preserve row count:

```python
rows_before = len(df)

# transformation

rows_after = len(df)

assert rows_before == rows_after
```

For transformations that intentionally expand rows, such as `extractall`, define a different reconciliation rule.

### Track metrics

```python
metrics = {
    "rows_before": len(df),
    "timestamp_parse_failures": int(
        timestamp_failure.sum()
    ),
    "phone_parse_failures": int(
        phone_failed.sum()
    ),
}
```

Use these metrics in logs or data-quality reporting as appropriate.

---

# 170. Learning Order

Follow this conceptual progression.

## Basic

1. Why accessors matter
2. What an accessor is
3. `.str`
4. `strip`
5. `lower`
6. `upper`
7. `title`
8. `len`
9. `startswith`
10. `endswith`
11. `contains`
12. `replace`
13. `slice`
14. `zfill`
15. `pad`
16. `.dt`
17. `year`
18. `month`
19. `day`
20. `hour`
21. `dayofweek`
22. `day_name`
23. `quarter`
24. `date`
25. `is_month_end`

## Intermediate

26. regex
27. `.str.contains(regex=True)`
28. `.str.extract`
29. named groups
30. `.str.extractall`
31. `.str.findall`
32. `.str.replace(regex=True)`
33. `.str.split`
34. `.str.split(expand=True)`
35. `.str.rsplit(n=1)`
36. `.str.partition`
37. `.str.cat`
38. `.dt.floor`
39. `.dt.ceil`
40. `.dt.round`
41. `.dt.tz_convert`
42. `.dt.strftime`
43. `.dt.to_period`
44. `.cat`

## Advanced

45. missing-value propagation
46. `na=False`
47. Unicode normalization
48. accents
49. non-breaking spaces
50. key normalization
51. string dtype vs `object`
52. Arrow-backed strings
53. vectorized regex vs `apply`
54. mixed timestamp formats
55. explicit parsing order
56. failure counting
57. never guess silently
58. production normalization strategy
59. regex testing
60. performance engineering

Then:

61. `text_and_time_cleaning.py`
62. prediction exercises
63. debugging
64. testing
65. edge cases
66. anti-patterns
67. reconciliation
68. production checklist
69. checkpoint
70. common mistakes
71. cheat sheet

---

# 171. Final Quality Bar

A professional learner completing this chapter should be able to:

- select an appropriate accessor;
- explain why the accessor fits the data type;
- choose literal vs regex semantics intentionally;
- extract multiple fields with named groups;
- distinguish one-match and many-match output grain;
- split text without assuming perfect input;
- normalize keys without damaging free text;
- reason about missing values;
- parse timestamps with explicit known formats;
- count parsing failures;
- preserve raw evidence;
- convert timezones deliberately;
- keep datetimes typed until presentation;
- use categorical ordering intentionally;
- reason about string storage backends;
- benchmark accessor vs `apply`;
- test regexes with positive and negative cases;
- debug malformed production data.

---

# 172. Technical Accuracy Notes

### String accessor

Pandas provides vectorized string operations through `Series.str`. citeturn976423search11

### `contains`

The `regex` argument determines whether a pattern is treated as a regular expression, and the default missing-value behavior varies by dtype. citeturn976423search0

### `replace`

Use the `regex` parameter explicitly when regex replacement is intended. citeturn976423search9

### `split`

`split` supports `expand=True` and an explicit `regex` argument for controlling pattern interpretation. citeturn976423search5

### `rsplit`

`rsplit` performs splits from the right and supports `n`. citeturn976423search4

### `extractall`

`extractall` produces one row per regex match and exposes match position through its MultiIndex. citeturn976423search6

### `partition`

`partition` returns three pieces around the first separator: before, separator, after. citeturn976423search12

### Datetime timezone conversion

`tz_convert` requires timezone-aware data and converts the same instant to the target timezone. citeturn976423search1

### Datetime formatting

`strftime` formats datetime values into strings. citeturn976423search2

### Categoricals

Categoricals have categories and integer codes, and ordered categoricals sort according to category order. citeturn990257search2turn990257search3

### Arrow

Pandas supports Arrow-backed data types and Arrow-based execution for supported APIs; performance and behavior depend on the specific operation and representation. citeturn990257search1

### Pandas 3 string dtype

Pandas 3.0 introduced a dedicated string dtype as the default representation for ordinary string data in common Series construction. citeturn990257search4turn990257search0

---

# 173. Common Mistakes — Final Summary

| Mistake | Correct mindset |
|---|---|
| Regex special characters treated literally or vice versa | Make regex mode explicit |
| Invisible whitespace ignored | Inspect and normalize where justified |
| `strftime` used too early | Keep timestamps typed |
| Missing forced to false | Decide `NA` vs `False` semantically |
| Mixed timestamp formats guessed | Parse documented formats in order |
| Parse failures hidden | Count and inspect |
| Regex too broad | Add negative tests |
| Regex too narrow | Add production-variation tests |
| `extractall` assumed to preserve row count | Understand match-level grain |
| `findall` expected to create rows | Lists are its result model |
| Split shape assumed fixed | Validate delimiter counts |
| `partition` expected to return two fields | It returns three |
| Title case assumed perfect | Use as presentation normalization |
| Unicode differences ignored | Normalize where the key contract requires it |
| Arrow assumed universally faster | Measure actual workloads |
| `apply` used by default | Search for a suitable accessor first |
| Identifiers converted to numbers | Preserve leading zeros when semantic |
| Naive timezone meaning assumed | Establish source timezone semantics first |

---

# 174. Cheat Sheet — String

```python
s.str.strip()
s.str.lower()
s.str.upper()
s.str.title()
s.str.len()
s.str.startswith(...)
s.str.endswith(...)
s.str.contains(...)
s.str.replace(...)
s.str.slice(...)
s.str.zfill(...)
s.str.pad(...)
```

---

# 175. Cheat Sheet — Regex

```python
s.str.contains(..., regex=True)

s.str.extract(
    r"(?P<field>...)"
)

s.str.extractall(
    r"(?P<field>...)"
)

s.str.findall(...)

s.str.replace(
    pattern,
    replacement,
    regex=True,
)
```

---

# 176. Cheat Sheet — Split/Join

```python
s.str.split(expand=True)

s.str.rsplit(
    pat=",",
    n=1,
    expand=True,
)

s.str.partition(",")

left.str.cat(
    right,
    sep=" ",
)
```

---

# 177. Cheat Sheet — Datetime Properties

```python
s.dt.year
s.dt.month
s.dt.day
s.dt.hour
s.dt.dayofweek
s.dt.day_name()
s.dt.quarter
s.dt.date
s.dt.is_month_end
```

---

# 178. Cheat Sheet — Datetime Methods

```python
s.dt.floor("h")
s.dt.ceil("h")
s.dt.round("h")

s.dt.tz_convert("Asia/Kolkata")

s.dt.strftime("%Y-%m-%d")

s.dt.to_period("M")
```

---

# 179. Cheat Sheet — Categorical

```python
s.cat.categories
s.cat.codes

s.cat.rename_categories(...)

s.cat.reorder_categories(
    [...],
    ordered=True,
)
```

---

# 180. Cheat Sheet — Unicode and Missing

```python
s.str.normalize("NFKC")

s.str.contains(
    "error",
    regex=False,
    na=False,
)
```

Remember:

```text
na=False
    ≠
"this value was really False"
```

It means:

```text
"I choose to treat missing as False for this check."
```

---

# 181. Cheat Sheet — Mixed Timestamp Parsing

```python
raw = df["timestamp"].astype("string")

parsed_a = pd.to_datetime(
    raw,
    format="FORMAT_A",
    errors="coerce",
)

remaining = raw.notna() & parsed_a.isna()

parsed_b = pd.to_datetime(
    raw.where(remaining),
    format="FORMAT_B",
    errors="coerce",
)

parsed = parsed_a.fillna(parsed_b)

failed = raw.notna() & parsed.isna()

failure_count = int(failed.sum())
failed_raw = raw.loc[failed]
```

---

# 182. Cheat Sheet — Performance

```text
appropriate vectorized accessor
        ↓
measure
        ↓
compare with apply when useful
        ↓
assert result equality
        ↓
choose based on evidence
```

---

# 183. Final Checkpoint Answers You Should Be Able to Explain

### 1. Multiple fields from one regex

```python
r"(?P<area_code>\d{3})(?P<number>\d{7})"
```

Named groups become named output columns.

### 2. Missing values

Accessors generally preserve missingness, but operation-specific behavior and dtype matter.

### 3. `na=False`

It explicitly maps missing to false for that operation. Use it only when that semantic interpretation is correct.

### 4. Hour/week bucketing

Use `.dt.floor()` for fixed-frequency bucketing such as hours. For week labels, explicitly define the week-start semantics rather than relying on an unstated convention.

### 5. Vectorized vs `apply`

Accessors express column operations directly and can use optimized implementations. `apply` invokes a Python function for each value. Benchmark material workloads instead of making absolute performance claims.

---

# 184. Final Self-Assessment

You are ready to move forward when you can do all of the following without copying code blindly:

```text
□ normalize a code with strip + case transformation
□ validate a key using len/startswith/contains
□ explain literal vs regex matching
□ build a named-group extraction
□ choose extract vs extractall vs findall
□ split text and reason about shape
□ use partition correctly
□ combine Series with cat
□ derive date/time fields with dt
□ floor/ceil/round timestamps
□ convert a timezone-aware timestamp
□ explain tz_convert vs localization conceptually
□ format only at the output boundary
□ convert timestamps to calendar periods
□ rename and order categories
□ explain NA propagation
□ justify or reject na=False
□ detect Unicode/invisible whitespace problems
□ explain string dtype vs object
□ discuss Arrow-backed strings without absolute claims
□ benchmark vectorized vs apply
□ parse two known timestamp formats explicitly
□ count failures and inspect raw values
□ refuse silent timestamp guessing
□ write five positive and five negative regex tests
□ debug a production-style malformed input
```

---

# 185. Final Production Principle

When handling text and time data, do not ask only:

> "What pandas function can clean this?"

Ask:

> **What does this value mean, what transformations preserve that meaning, what can fail, and how will the pipeline prove that the transformation was correct?**

The operational pattern is:

```text
Understand
   ↓
Choose accessor
   ↓
Transform
   ↓
Validate
   ↓
Measure failures
   ↓
Preserve evidence
   ↓
Test
   ↓
Measure performance
   ↓
Deliver typed, meaningful data
```

> **Text and timestamp transformations must be explicit, vectorized where practical, validated, and traceable.**

# 186. Required Learning Activity — 30 Messy Values

Collect or construct **30 messy real-world-style values** and classify each value before cleaning it.

The following starter set contains exactly 30 values.

| # | Field | Raw value | Likely issue |
|---:|---|---|---|
| 1 | customer_name | `"  Shoun Kumar  "` | outer whitespace |
| 2 | customer_name | `"alice   smith"` | repeated internal whitespace |
| 3 | customer_name | `"BOB JONES"` | case |
| 4 | customer_name | `" Renée Dupont "` | whitespace + diacritic |
| 5 | customer_name | `"Ａｌｉｃｅ"` | full-width Unicode |
| 6 | customer_name | `None` | missing |
| 7 | product_code | `" SKU-001 "` | whitespace |
| 8 | product_code | `"sku-002"` | case |
| 9 | product_code | `"SKU003"` | missing delimiter |
| 10 | product_code | `" SKU-００４ "` | Unicode + whitespace |
| 11 | country_code | `" in "` | whitespace + case |
| 12 | country_code | `"IN\u00A0"` | non-breaking space |
| 13 | country_code | `"Us"` | case |
| 14 | country_code | `None` | missing |
| 15 | phone | `"(212) 555-1234"` | formatting |
| 16 | phone | `"212-555-1234"` | formatting |
| 17 | phone | `"+1 212 555 1234"` | country prefix |
| 18 | phone | `"+12125551234"` | compact format |
| 19 | phone | `"212.555.1234"` | formatting |
| 20 | phone | `"not-a-phone"` | malformed |
| 21 | address | `"New York, NY 10001"` | valid example |
| 22 | address | `" Boston, MA 02108 "` | outer whitespace |
| 23 | address | `"Chicago,IL 60601"` | missing space |
| 24 | address | `"Seattle, WA 98101, USA"` | extra separator |
| 25 | address | `"Malformed Address"` | missing separator |
| 26 | timestamp | `"2025-09-26 14:30:00"` | known format A |
| 27 | timestamp | `"26/09/2025 15:45"` | known format B |
| 28 | timestamp | `"2025/09/26 14:30:00"` | unsupported format for exercise |
| 29 | timestamp | `"2025-13-26 14:30:00"` | invalid date |
| 30 | timestamp | `None` | missing |

### Activity

For every value:

1. identify its semantic type;
2. decide whether it is a key, code, label, address, or free text;
3. predict the transformation;
4. choose the accessor;
5. identify failure modes;
6. execute;
7. inspect;
8. assert;
9. record whether the original value was missing, malformed, or normalized.

The purpose is not to "clean everything."

The purpose is to learn when cleaning is justified and when preserving the source value is safer.

---

# 187. Regex Coverage Pack — Five Positive + Five Negative

The roadmap requires at least five positive and five negative examples for every regex used in the exercise.

To make that concrete, maintain a test matrix for each distinct exercise pattern.

---

## 187.1 Phone extraction pattern

Pattern:

```regex
^(?:\+?1[\s.-]*)\(?\s*(?P<area_code>\d{3})\s*\)?[\s.-]*(?P<number>\d{3}[\s.-]*\d{4})$
```

### Positive

```text
(212) 555-1234
212-555-1234
+1 212 555 1234
+12125551234
212.555.1234
```

### Negative

```text
212-555-123
ABC-555-1234
21255512345
212/555/1234
+44 20 7946 0958
```

---

## 187.2 Error-code search pattern

Pattern:

```regex
\bERR_[0-9]{3}\b
```

### Positive

```text
ERR_001
payment ERR_404
ERR_999 received
retry ERR_120 now
status=ERR_500
```

### Negative

```text
ERR_01
ERR_1000
ERX_001
ERR_ABC
ERR001
```

Use:

```python
pattern = r"\bERR_[0-9]{3}\b"

mask = s.str.contains(
    pattern,
    regex=True,
    na=False,
)
```

---

## 187.3 Product-code search pattern

Pattern:

```regex
P\d{3}
```

### Positive

```text
P001
P123
P999
order P105 confirmed
codes=P007,P008
```

### Negative

```text
P01
P1000
Q123
PX23
PABC
```

For exact validation of a whole value, anchor the expression:

```regex
^P\d{3}$
```

The choice between contains-style search and whole-value validation must match the requirement.

---

## 187.4 Non-digit replacement pattern

Pattern:

```regex
\D+
```

This is used for transformations rather than a simple yes/no rule.

### Positive — replacement should remove the matched non-digits

| Input | Expected result |
|---|---|
| `212-555-1234` | `2125551234` |
| `(212) 555-1234` | `2125551234` |
| `212.555.1234` | `2125551234` |
| `212 555 1234` | `2125551234` |
| `+1-212-555-1234` | `12125551234` |

### Negative — no non-digit run should be present

| Input | Expected result |
|---|---|
| `2125551234` | unchanged |
| `123456` | unchanged |
| `0` | unchanged |
| `987654321` | unchanged |
| `5555` | unchanged |

Example:

```python
digits = phones.str.replace(
    r"\D+",
    "",
    regex=True,
)
```

---

## 187.5 Whitespace-collapse pattern

Pattern:

```regex
\s+
```

### Positive

```text
"alice   smith"
"hello world"
"  leading"
"trailing  "
"a\tb"
```

### Negative

```text
"alice"
"ABC123"
"SKU-001"
"2025-09-26"
"ERR_001"
```

Example:

```python
collapsed = s.str.replace(
    r"\s+",
    " ",
    regex=True,
)
```

Use this for fields where collapsing whitespace is semantically appropriate.

---

## 187.6 Digit pattern

Pattern:

```regex
\d+
```

### Positive

```text
123
A123
123ABC
P001
order-2025
```

### Negative

```text
ABC
P
ERR
SKU
hello
```

This pattern is used here to illustrate digit matching. For a production field, anchor and constrain it to the actual contract.

---

## 187.7 Literal dot in regex

Pattern:

```regex
\.
```

### Positive

```text
file.csv
domain.com
212.555.1234
version.1
a.b
```

### Negative

```text
file_csv
domain-com
212-555-1234
version-1
ab
```

For literal dot search, the clearer option is often:

```python
s.str.contains(
    ".",
    regex=False,
    na=False,
)
```

or escaped regex:

```python
s.str.contains(
    r"\.",
    regex=True,
    na=False,
)
```

---

# 188. Regex Regression-Test Pattern

Keep regex tests small and explicit.

```python
import pandas as pd

def assert_all_match(values: list[str], pattern: str) -> None:
    s = pd.Series(values, dtype="string")
    result = s.str.contains(
        pattern,
        regex=True,
        na=False,
    )
    assert result.all()


def assert_none_match(values: list[str], pattern: str) -> None:
    s = pd.Series(values, dtype="string")
    result = s.str.contains(
        pattern,
        regex=True,
        na=False,
    )
    assert (~result).all()
```

Use these helpers only when their semantics match the test.

The important part is that each regex is tested against both expected positives and expected negatives.

---

# 189. Final Exercise Validation Matrix

Before the `text_and_time_cleaning.py` exercise is considered complete:

| Requirement | Verification |
|---|---|
| Customer names cleaned | Output values inspected |
| Trim applied | Leading/trailing test |
| Repeated spaces collapsed | Multiple-space test |
| Unicode normalized | Full-width/Unicode test |
| Title case applied | Presentation result reviewed |
| Phone formats supported | 5 positive cases |
| Phone invalid formats rejected | 5 negative cases |
| Named groups used | `area_code`, `number` columns |
| Unparseable phones counted | failure metric |
| Raw bad phones retained | invalid-value evidence |
| Addresses split | `split(expand=True)` |
| Malformed addresses visible | shape/content validation |
| Two timestamp formats parsed | explicit format A/B |
| Timestamp failures counted | failure metric |
| Raw timestamp failures inspectable | source evidence |
| `order_hour` derived | `.dt.hour` |
| `order_weekday` derived | `.dt.dayofweek` |
| `order_week_start` derived | explicit week definition |
| 5,000,000-row benchmark | actual measured runtime |
| Vectorized result correct | equality assertion |
| `apply` result correct | equality assertion |
| Performance conclusion evidence-based | actual environment recorded |

---

# 190. Final Technical Decision Rules

```text
STRING
  ↓
Is it a key/code?
  ├─ Yes → normalize only according to contract
  └─ No  → preserve free-text meaning

Need a simple string operation?
  └─ Use .str

Need regex?
  └─ Make regex=True explicit

Need structured captured fields?
  └─ extract

Need multiple matches as rows?
  └─ extractall

Need multiple matches as lists?
  └─ findall

Need tokenization?
  ├─ split
  ├─ rsplit
  └─ partition

Need concatenation?
  └─ cat

DATETIME
  ↓
Is the source a string?
  └─ Parse before .dt

Is the format known?
  ├─ Yes → explicit format
  └─ No  → do not silently guess

Can parsing fail?
  └─ Count + inspect failures

Need fixed bucket?
  └─ floor / ceil / round

Need timezone conversion?
  └─ tz_convert on aware timestamps

Need presentation text?
  └─ strftime at output boundary

Need calendar interval?
  └─ to_period
```

---

# 191. Final Production Mental Model

The complete topic can be reduced to one engineering workflow:

```text
RAW DATA
   ↓
Understand source contract
   ↓
Classify field semantics
   ↓
Choose .str / .dt / .cat
   ↓
Apply explicit transformation
   ↓
Preserve missing meaning
   ↓
Count failures
   ↓
Inspect raw failures
   ↓
Validate output shape/type/values
   ↓
Test representative + negative cases
   ↓
Measure performance where material
   ↓
Keep structured data typed
   ↓
Export only at the appropriate boundary
```

The most important habit is not remembering a function name.

It is noticing when a transformation could silently change meaning.

> **Correctness first, explicitness second, observability third, performance fourth.**

---

# 192. Final Roadmap Coverage Checklist

## Basics — `.str`

- [x] `strip`
- [x] `lower`
- [x] `upper`
- [x] `title`
- [x] `len`
- [x] `startswith`
- [x] `endswith`
- [x] `contains`
- [x] `replace`
- [x] `slice`
- [x] `zfill`
- [x] `pad`

## Basics — `.dt`

- [x] `year`
- [x] `month`
- [x] `day`
- [x] `hour`
- [x] `dayofweek`
- [x] `day_name`
- [x] `quarter`
- [x] `date`
- [x] `is_month_end`

## Intermediate — Regex

- [x] `.str.contains(regex=True)`
- [x] `.str.extract`
- [x] named regex groups
- [x] multiple fields from one regex
- [x] `.str.extractall`
- [x] `.str.findall`
- [x] `.str.replace(regex=True)`
- [x] positive and negative regex testing

## Intermediate — Split/Join

- [x] `.str.split(expand=True)`
- [x] `.str.rsplit(n=1)`
- [x] `.str.partition`
- [x] `.str.cat`

## Intermediate — Datetime

- [x] `.dt.floor`
- [x] `.dt.ceil`
- [x] `.dt.round`
- [x] `.dt.tz_convert`
- [x] `.dt.strftime`
- [x] `.dt.to_period`

## Intermediate — Categorical

- [x] `.cat`
- [x] category renaming
- [x] category ordering

## Advanced

- [x] missing-value propagation
- [x] `na=False`
- [x] Unicode normalization
- [x] `.str.normalize("NFKC")`
- [x] accents
- [x] non-breaking spaces
- [x] string dtype vs `object`
- [x] Arrow-backed strings
- [x] vectorized regex vs `apply`
- [x] mixed timestamp formats
- [x] explicit format order
- [x] failure counting
- [x] no silent guessing

## Required learning activities

- [x] 30 messy real-world-style values
- [x] accessor cleaning chains
- [x] five positive regex examples per pattern
- [x] five negative regex examples per pattern
- [x] customer name cleaning
- [x] phone extraction
- [x] `area_code`
- [x] `number`
- [x] unparseable count
- [x] address split
- [x] two known timestamp formats
- [x] timestamp failure reporting
- [x] `order_hour`
- [x] `order_weekday`
- [x] `order_week_start`
- [x] 5,000,000-row benchmark
- [x] vectorized vs `apply` comparison

## Quality

- [x] prediction-first learning
- [x] debugging
- [x] testing
- [x] edge cases
- [x] production use cases
- [x] anti-patterns
- [x] reconciliation
- [x] production checklist
- [x] checkpoint
- [x] common mistakes
- [x] cheat sheet

---

# 193. Completion Standard

Do not consider the topic mastered until you can explain, without relying on memorized snippets:

1. why `.str` exists;
2. why `.dt` exists;
3. why a key may need Unicode and whitespace normalization;
4. when regex adds value;
5. why `extract`, `extractall`, and `findall` are different;
6. why split shape must be validated;
7. why `na=False` changes semantics;
8. why a timestamp should remain typed until presentation;
9. why `tz_convert` is different from establishing timezone meaning;
10. why explicit timestamp formats make failures observable;
11. why `apply` is not the first choice for ordinary supported transformations;
12. why performance must be measured on the actual workload;
13. why preserving raw values is part of production data quality;
14. why a visually identical Unicode string may still be a different key;
15. why regex correctness requires both positive and negative evidence.

---

# 194. Final Takeaway

When you receive messy text or timestamp data, think:

```text
What does this value mean?
       ↓
What must remain unchanged?
       ↓
What normalization is allowed?
       ↓
What pandas accessor expresses the operation?
       ↓
What happens for missing values?
       ↓
What happens for malformed values?
       ↓
How many values failed?
       ↓
Can I inspect the original evidence?
       ↓
Did I test positive and negative cases?
       ↓
Did I preserve a useful dtype?
       ↓
Did I measure performance where it matters?
```

That mindset is what turns a pandas accessor exercise into production-grade Data Engineering.

> **Text and timestamp transformations must be explicit, vectorized where practical, validated, and traceable.**
