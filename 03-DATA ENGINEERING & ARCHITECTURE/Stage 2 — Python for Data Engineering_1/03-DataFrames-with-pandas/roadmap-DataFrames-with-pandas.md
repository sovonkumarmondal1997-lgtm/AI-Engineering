# Roadmap — Module 2.3: DataFrames with pandas

This is the learning roadmap for the third module of Stage 2, **Python for
Data Engineering**. It tells you **what** to learn about pandas, **in what
order**, **how** to learn each topic, and **how to prove to yourself** that
you have learned it before you move on.

pandas is the most widely used DataFrame library in Python and the lingua
franca of small-to-medium data work: ingestion scripts, data-quality checks,
API extracts, reconciliation jobs, feature preparation, test fixtures for
Spark jobs, and quick investigations during incidents. Even teams that run
Spark or Polars in production use pandas every day. A data engineer must be
able to use it **correctly** (no silent type changes, no row explosions in
joins, no chained-assignment bugs) and **efficiently** (right dtypes, no
row-by-row loops, predictable memory).

This roadmap targets **pandas 3.x**, where Copy-on-Write is the only mode
and text columns default to a dedicated string dtype. Where behaviour
differs from pandas 2.x — which you will still meet in older codebases —
the roadmap says so.

---

## 1. Module outcome

By the end of this module you will be able to:

- Explain a `Series`, a `DataFrame`, and an `Index`, and how **index
  alignment** changes the result of arithmetic and assignment.
- Read and write CSV, JSON Lines, Parquet, Excel, and SQL sources with
  explicit dtypes, date parsing, null handling, and compression.
- Select rows and columns precisely with `loc`, `iloc`, boolean masks, and
  `query`.
- Choose correct **dtypes**: nullable integers, booleans, strings,
  categoricals, timezone-aware datetimes, and PyArrow-backed types.
- Clean data: missing values, duplicates, inconsistent labels, and outliers
  — and record what you changed.
- Aggregate with `groupby` using named aggregation, `transform`, and
  `filter`, and know when `apply` is a performance trap.
- Join tables safely with `merge`, verify **join cardinality**, and detect
  row explosions and lost rows.
- Reshape between long and wide formats with `pivot_table`, `melt`,
  `stack`, and `unstack`.
- Work with time series: resampling, rolling and time-based windows, and
  as-of joins.
- Write readable, testable transformation pipelines with **method
  chaining** and `pipe`.
- Avoid Copy-on-Write and chained-assignment bugs.
- Process files larger than memory with chunking and memory reduction, and
  recognise when to leave pandas for Polars, DuckDB, or Spark.

---

## 2. Prerequisites

This module builds on earlier stages and Modules 2.1–2.2. It does **not**
re-teach them.

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| CSV, JSON, encodings, pathlib | Stage 1 — Module 1.5 | pandas readers wrap these formats; encoding and newline bugs still apply |
| Regular expressions | Stage 1 — Module 1.4 | Used heavily by the `.str` accessor |
| datetime, time zones, timestamps | Stage 1 — Module 1.9 | pandas timestamps follow the same UTC-first rules |
| Pure functions, separating side effects | Stage 1 — Module 1.8 | The basis for testable `pipe` steps |
| Pytest, fixtures, parametrization | Stage 1 — Module 1.7 | Every exercise has tests |
| Safe file writes, idempotency, logging | Stage 1 — Module 1.10 | Output files of every exercise |
| Medallion layers, OLTP vs OLAP | Stage 2 — Module 2.1 | Exercises are organised as bronze → silver → gold |
| dtypes, NaN, vectorization, views vs copies | Stage 2 — Module 2.2 | pandas is built on these; this module only covers pandas-specific behaviour |

**Tools needed:**

- Python 3.12+ in a `uv` project: `uv add pandas pyarrow openpyxl
  sqlalchemy`.
- `pytest` for tests; `pandas.testing.assert_frame_equal` for comparing
  results.
- Jupyter or IPython for exploration — but every exercise's final version
  must be a `.py` module with tests.
- Sample datasets: generate them with NumPy (Module 2.2), or use a public
  dataset such as the NYC Taxi trip records (Parquet) for the larger
  exercises.

---

## 3. How the module is organised

The thirteen topics are grouped into five phases. Work through them **in
order**.

```text
Phase A — Core Objects and I/O                 (Basics)
  01 Series, DataFrame, and Index
  02 Reading and writing data sources

Phase B — Selecting and Typing Data            (Basics → Intermediate)
  03 Selection with loc, iloc, and query
  04 dtypes, nullable types, and categoricals

Phase C — Cleaning and Transforming            (Intermediate)
  05 Cleaning missing values, duplicates, and outliers
  06 groupby: aggregate, transform, and apply
  07 merge, join, concat, and join cardinality
  08 Reshaping: pivot, melt, stack, and unstack

Phase D — Time and Text                        (Intermediate → Advanced)
  09 Time series: resampling and rolling windows
  10 String and datetime accessors

Phase E — Production-Grade pandas              (Advanced)
  11 Method chaining and pipe
  12 Copy-on-Write and chained-assignment pitfalls
  13 Chunked processing and memory reduction

Consolidate
  practice-questions.md
  interview-practice.md
  Module mini-project: order-to-revenue pipeline in pandas
```

The dependency chain:

```text
01 ► 02 ► 03 ► 04 ► 05 ► 06 ► 07 ► 08 ► 09 ► 10 ► 11 ► 12 ► 13
objects I/O  select types clean group join shape time text chain CoW  scale
```

Why this order:

- You cannot read files correctly (02) without knowing what an Index is
  (01), and you cannot pick `dtype=` arguments on read without Topic 04 —
  so Topic 02 teaches reading with defaults first, and Topic 04 returns to
  set explicit types.
- Cleaning (05) needs selection (03) and dtypes (04).
- `groupby` (06) comes before joins (07) because checking cardinality uses
  group counts.
- Time series (09) needs `groupby`, reshaping, and dtypes.
- Method chaining (11), Copy-on-Write (12), and memory (13) are about
  *how* you write everything above; they only make sense once you have
  written plenty of pandas code.

---

## 4. Suggested schedule

About **5–6 weeks at 8–10 hours per week**. This is the largest module in
the early part of Stage 2 — do not rush it.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — Series, DataFrame, Index · Topic 02 — Reading and writing |
| 2 | Topic 03 — Selection · Topic 04 — dtypes and categoricals |
| 3 | Topic 05 — Cleaning · Topic 06 — groupby |
| 4 | Topic 07 — merge and join cardinality · Topic 08 — reshaping |
| 5 | Topic 09 — time series · Topic 10 — accessors · Topic 11 — method chaining |
| 6 | Topic 12 — Copy-on-Write · Topic 13 — chunking and memory · practice, interview practice, mini-project |

---

## 5. How to study every topic (the DataFrame engineering loop)

```text
Read → Predict (rows, columns, dtypes, index) → Run on a tiny frame
→ Verify invariants → Run on a big frame → Break it → Measure
→ Write it down → Explain aloud
```

1. **Read** the topic file once, fully.
2. **Predict** the result's **row count**, **columns**, **dtypes**, and
   **index** before running anything. Most pandas bugs are a wrong
   prediction here — especially row counts after joins and dtypes after
   cleaning.
3. **Run on a tiny frame** (3–10 rows you typed yourself) so you can check
   every value by eye.
4. **Verify invariants** in code: `assert len(out) == expected`,
   `assert out["id"].is_unique`, `assert out.dtypes["amount"] == "Int64"`.
   Make this a reflex — production pipelines live or die on invariants.
5. **Run on a big frame** (1–10 million rows) to see performance.
6. **Break it on purpose** — empty frames, all-null columns, duplicate
   keys, mixed types, time-zone mismatches, unexpected categories.
7. **Measure** runtime and `df.memory_usage(deep=True).sum()`.
8. **Write down** the rule you learned in `module-2.3-notes.md`.
9. **Explain aloud** what the code does and why the result has that shape.

Keep a single `pandas_lab/` `uv` project for all exercises:

```text
pandas_lab/
├── data/            # generated or downloaded inputs (git-ignored)
├── src/pandas_lab/  # one module per topic
└── tests/           # one test file per topic
```

---

## 6. Phase A — Core Objects and I/O (Basics)

### Topic 01 — [Series, DataFrame, and Index](01-series-dataframe-and-index.md)

**Why it comes first:** Every pandas behaviour that surprises people —
misaligned arithmetic, unexpected NaN, duplicate labels, slow lookups —
comes from the Index.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `Series` (1-D labelled array) and `DataFrame` (collection of Series sharing one Index); creating them from dicts, lists of records, and NumPy arrays |
| Basics | Inspecting data: `head`, `tail`, `sample`, `shape`, `columns`, `dtypes`, `info`, `describe`, `value_counts` |
| Basics | The Index: row labels, `RangeIndex`, `set_index`, `reset_index`, `rename`, column Index |
| Intermediate | **Index alignment**: arithmetic between two Series aligns on labels, not positions — the source of surprise NaN |
| Intermediate | Index properties: `is_unique`, `is_monotonic_increasing`, duplicate labels, and why lookups on a sorted, unique index are fast |
| Intermediate | Adding, renaming, and dropping columns; column order; `assign` introduction |
| Advanced | `MultiIndex` (hierarchical index): creating, selecting with tuples and `xs`, `swaplevel`, `sort_index`; when to flatten it back to columns |
| Advanced | How a DataFrame stores data: columns backed by NumPy arrays, pandas extension arrays, or Arrow arrays |
| Advanced | Choosing: when an Index is useful (time series, fast lookup) and when plain columns are clearer (most ETL code) |

**How to learn it**

1. Read the topic file.
2. Build a DataFrame from a list of dicts (like JSON records) and from a
   dict of lists (columnar). Compare them.
3. Add two Series with partially overlapping labels and explain every NaN.

**Hands-on exercise — `index_alignment.py`**

1. Build `revenue_2024` and `revenue_2025` Series indexed by country, with
   different sets of countries.
2. Compute year-over-year growth; explain the NaN rows; then use
   `add(..., fill_value=0)` and discuss whether 0 is the right fill.
3. Build a `MultiIndex` frame of revenue by `(country, month)`; select one
   country, one month across all countries, and flatten it back with
   `reset_index`.
4. Write tests asserting the expected index, row count, and values.

**Checkpoint:**

- [ ] Explain index alignment with an example that produces NaN.
- [ ] Explain the difference between a Series and a DataFrame column.
- [ ] Convert between an index and a column in both directions.
- [ ] Select from a `MultiIndex` with `loc` and `xs`.

**Common mistakes:** assuming arithmetic is positional; leaving duplicate
index labels that later break joins and reindexing; carrying a meaningless
index into output files.

---

### Topic 02 — [Reading and writing data sources](02-reading-and-writing-data-sources.md)

**Why here:** Every pipeline starts with a read and ends with a write. Most
data-type bugs are born at read time.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `read_csv` / `to_csv`: `sep`, `header`, `names`, `usecols`, `index=False`, `encoding`, `compression` |
| Basics | `read_json(lines=True)` / `to_json(orient="records", lines=True)` for JSON Lines |
| Basics | `read_parquet` / `to_parquet` with PyArrow: why Parquet preserves types and CSV does not |
| Basics | `read_excel` / `to_excel` with `openpyxl`; `sheet_name`, header rows, merged cells |
| Intermediate | Explicit typing on read: `dtype=`, `parse_dates=`, `date_format=`, `na_values=`, `keep_default_na=False` (so values like `"NA"` or `"null"` are not silently turned into missing) |
| Intermediate | Keeping identifiers as strings: ZIP codes, phone numbers, and IDs with leading zeros |
| Intermediate | Bad input: `on_bad_lines=`, quoting, thousands and decimal separators, BOMs |
| Intermediate | `read_sql` / `to_sql` with a SQLAlchemy engine (introduction — Module 2.7 goes deep): `chunksize`, `if_exists`, `method="multi"` |
| Intermediate | Reading from URLs, compressed files, and globbed file lists (`pd.concat` of many files) |
| Advanced | `engine="pyarrow"` for faster CSV parsing, and `dtype_backend="pyarrow"` / `"numpy_nullable"` |
| Advanced | Parquet options: `columns=` (column pruning), `filters=` (row-group filtering), `partition_cols=` for Hive-style output (Module 2.5 explains the internals) |
| Advanced | Writing reliably: deterministic column order, explicit schemas, writing to a temp path then renaming (Stage 1 safe writes applied to DataFrames) |
| Advanced | Round-trip testing: write → read → `assert_frame_equal` to prove nothing changed |

**How to learn it**

1. Read the topic file.
2. Take one dataset and write it to CSV, JSON Lines, Parquet, and Excel.
   Read each back with defaults and compare `dtypes` — write down every
   difference.
3. Build a "reader contract" table for one source: column, dtype, null
   tokens, date format.

**Hands-on exercise — `io_contracts.py`**

Given a messy `customers.csv` (IDs with leading zeros, `"N/A"` and `""` as
nulls, dates in `DD/MM/YYYY`, a `Latin-1` encoding, and two malformed
lines):

1. Read it with defaults and list every problem you see.
2. Write `read_customers(path) -> pd.DataFrame` with explicit `dtype`,
   `na_values`, `keep_default_na=False`, `date_format`, `encoding`, and
   `on_bad_lines` handling; log how many bad lines were skipped.
3. Write it to Parquet and prove the round trip with `assert_frame_equal`.
4. Load the same data into SQLite with `to_sql` and read it back with
   `read_sql`.
5. Benchmark `read_csv` with the default engine vs `engine="pyarrow"` on a
   1 GB CSV.

**Checkpoint:**

- [ ] Explain why CSV loses type information and Parquet keeps it.
- [ ] Read a CSV that keeps leading zeros in IDs.
- [ ] Explain what `keep_default_na=False` protects you from.
- [ ] Read only selected columns and rows from a Parquet file.

**Common mistakes:** relying on type inference in production; writing the
index to CSV by accident (`Unnamed: 0` columns); mixing date formats
silently; leaving half-written output files after a crash.

---

## 7. Phase B — Selecting and Typing Data (Basics → Intermediate)

### Topic 03 — [Selection with loc, iloc, and query](03-selection-with-loc-iloc-and-query.md)

**Why here:** Every transformation starts by selecting the right rows and
columns. Getting selection precise prevents most assignment bugs later.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Column selection: `df["col"]`, `df[["a", "b"]]`; Series vs DataFrame result |
| Basics | `loc` (label-based, **inclusive** slice end) vs `iloc` (position-based, **exclusive** slice end) |
| Basics | Boolean filtering with `&`, `\|`, `~` and parentheses; `isin`, `between`, `isna`, `notna` |
| Intermediate | `query()` with column names, `@local_variable`, and backticks for column names with spaces |
| Intermediate | Assignment through selection: `df.loc[mask, "col"] = value` as the one correct pattern |
| Intermediate | `at` / `iat` for single values; `where` and `mask` for conditional replacement that keeps shape |
| Intermediate | Selecting by dtype and name patterns: `select_dtypes`, `filter(like=..., regex=...)` |
| Advanced | Selecting with a `MultiIndex` and `pd.IndexSlice`; selecting on a sorted DatetimeIndex with partial strings (`df.loc["2025-03"]`) |
| Advanced | Performance: repeated boolean filtering vs one combined mask; `isin` with large sets; when `query` is faster (with `numexpr`) and when it is not |
| Advanced | Selection that returns an empty frame: making downstream code robust to zero rows |

**How to learn it**

1. Read the topic file.
2. Translate 15 SQL `WHERE` clauses into `loc`, boolean masks, and `query`
   — all three styles for each.
3. For each, predict the row count before running it.

**Hands-on exercise — `order_filters.py`**

On a 1,000,000-row orders frame:

1. Paid orders from three countries in Q1, over a threshold amount — write
   it with `loc`, then with `query`.
2. Flag orders as `high_value` using `df.loc[mask, "high_value"] = True`.
3. Replace negative amounts with NA using `mask`.
4. Select the first and last 10 rows per position with `iloc`, and a date
   range with `loc` on a DatetimeIndex.
5. Write a function that takes filter parameters and returns an empty (but
   correctly typed) frame when nothing matches; test it.

**Checkpoint:**

- [ ] Explain why `df.loc[0:5]` and `df.iloc[0:5]` can return different
      row counts.
- [ ] Use a local variable inside `query`.
- [ ] Assign to a filtered subset of rows correctly in one statement.
- [ ] Explain the difference between `where` and filtering.

**Common mistakes:** using `and`/`or` instead of `&`/`|`; forgetting
parentheses around conditions; `iloc` with labels; assuming the index is
`0..n-1` after filtering.

---

### Topic 04 — [dtypes, nullable types, and categoricals](04-dtypes-nullable-types-and-categoricals.md)

**Why here:** Once you can select data, you must make sure every column has
the **right type**. Wrong types cause wrong joins, wrong sorts, wrong sums,
and bloated memory.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Default dtypes: `int64`, `float64`, `bool`, `datetime64[ns]`, `object`, and the pandas 3 default string dtype (`str`) |
| Basics | Converting: `astype`, `pd.to_numeric(errors="coerce")`, `pd.to_datetime(format=..., errors="coerce", utc=True)` |
| Intermediate | **Nullable extension types**: `Int64`, `Float64`, `boolean`, `string` — and the missing-value marker `pd.NA` vs `np.nan` vs `None` |
| Intermediate | Three-valued logic with `pd.NA` (`NA \| True` is `True`, `NA & True` is `NA`) and what it means for filters |
| Intermediate | `convert_dtypes()` and `dtype_backend=` to switch whole frames to nullable or Arrow types |
| Intermediate | **Categoricals**: `category` dtype, categories and codes, `ordered=True`, `.cat.add_categories`, `.cat.remove_unused_categories`; memory savings for low-cardinality columns |
| Intermediate | Categoricals in `groupby`: pass `observed=True` so unused categories do not create empty groups |
| Advanced | PyArrow-backed dtypes (`pd.ArrowDtype`, e.g. `int64[pyarrow]`, `string[pyarrow]`, `timestamp[us, tz=UTC][pyarrow]`): benefits and remaining gaps |
| Advanced | Timezone-aware datetimes (`datetime64[ns, UTC]`), timestamp resolution (`s`, `ms`, `us`, `ns`), and out-of-bounds dates |
| Advanced | `Decimal` for money: `object` column of `decimal.Decimal` vs integer cents vs Arrow `decimal128` |
| Advanced | Schema enforcement: a single `SCHEMA` dict applied with `astype`, and checking `df.dtypes` against it (a lightweight version of Module 2.11) |

**How to learn it**

1. Read the topic file.
2. For one dataset, write a table: column → default inferred dtype →
   correct dtype → reason.
3. Measure memory before and after typing each column with
   `memory_usage(deep=True)`.

**Hands-on exercise — `typed_orders.py`**

1. Load raw orders (all strings) and convert them to a declared schema:
   `order_id: string`, `customer_id: Int64`, `quantity: Int16`,
   `amount_cents: Int64`, `country: category`, `status: ordered category`,
   `created_at: datetime64[ns, UTC]`, `is_gift: boolean`.
2. Log and count every value that failed conversion (`errors="coerce"`
   then compare null counts before and after).
3. Show that an integer column with missing values stays integer with
   `Int64` but becomes float with `int64` defaults.
4. Sort by the ordered `status` category and filter `status >= "paid"`.
5. Compare memory: all `object`, NumPy-typed, nullable-typed, Arrow-typed.
6. Write a `validate_schema(df, schema)` function and tests for it.

**Checkpoint:**

- [ ] Explain the difference between `pd.NA` and `np.nan`.
- [ ] Explain why a column with missing integers becomes `float64` and how
      to prevent it.
- [ ] Choose when to use `category` and when not to (high cardinality).
- [ ] Convert strings to timezone-aware UTC timestamps safely.

**Common mistakes:** `object` columns hiding mixed types; categoricals with
very high cardinality (no savings); using `errors="coerce"` without counting
what was coerced; naive timestamps mixed with aware ones.

---

## 8. Phase C — Cleaning and Transforming (Intermediate)

### Topic 05 — [Cleaning: missing values, duplicates, and outliers](05-cleaning-missing-duplicates-and-outliers.md)

**Why here:** With correct selection and types, you can clean data the way
the silver layer requires — deliberately and traceably.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Detecting missing values: `isna().sum()`, `isna().mean()` per column, rows with any/all missing |
| Basics | `dropna(subset=..., how=..., thresh=...)` and `fillna(value)` / `fillna(dict_per_column)` |
| Basics | `duplicated(subset=..., keep=...)` and `drop_duplicates` |
| Intermediate | Forward/backward fill (`ffill`, `bfill`) and `interpolate`, including per-group fills with `groupby(...).ffill()` |
| Intermediate | Deduplication by business key keeping the **latest** record: `sort_values` then `drop_duplicates(keep="last")` |
| Intermediate | Standardising values: `replace`, `map`, trimming and case-folding labels (preview of Topic 10), consistent country and status codes |
| Intermediate | Outlier detection: IQR rule, z-scores, domain rules (negative quantity, future dates); `clip` for capping |
| Advanced | Fuzzy duplicates: normalised keys (lowercase, stripped, punctuation removed) before deduplicating |
| Advanced | Flagging instead of deleting: `is_outlier`, `is_duplicate`, `dq_reason` columns, and splitting a frame into `clean` and `quarantine` parts |
| Advanced | Cleaning reports: a before/after summary of rows removed, values filled, and values changed per rule — the audit trail for silver layers |
| Advanced | When *not* to clean: keeping raw values in bronze and never "fixing" data you do not understand |

**How to learn it**

1. Read the topic file.
2. Profile a dirty dataset: missing rate per column, duplicate rate per
   key, obvious outliers. Write down every problem before fixing anything.
3. For each problem, decide: drop, fill, fix, flag, or quarantine — and
   write the reason.

**Hands-on exercise — `clean_orders.py`**

1. Deduplicate orders to the latest version per `order_id` using
   `updated_at`.
2. Fill missing `country` from the customer's last known country
   (group-wise forward fill).
3. Standardise `status` values (`"PAID"`, `"paid "`, `"Paid"` → `"paid"`).
4. Flag outliers in `amount_cents` using the IQR rule per country.
5. Split the output into `silver_orders` and `quarantine_orders` with a
   `dq_reason` column.
6. Produce a cleaning report (rows in, rows out, rows quarantined per
   reason) and assert that `rows_in == rows_out + rows_quarantined`.

**Checkpoint:**

- [ ] Keep the latest record per key correctly.
- [ ] Choose between dropping, filling, and flagging for a given column.
- [ ] Detect outliers with the IQR rule per group.
- [ ] Produce a reconciliation that proves no row was silently lost.

**Common mistakes:** `drop_duplicates()` on all columns when you meant a
business key; forgetting to sort before `keep="last"`; filling with 0 where
0 is a real value; deleting outliers that were actually valid.

---

### Topic 06 — [groupby: aggregate, transform, and apply](06-groupby-aggregate-transform-and-apply.md)

**Why here:** Most gold tables are aggregations. `groupby` is the pandas
equivalent of SQL `GROUP BY` plus window functions.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Split-apply-combine; `groupby(keys)` with one or many keys; `sum`, `mean`, `count`, `size`, `nunique`, `min`, `max`, `first`, `last` |
| Basics | `count` (non-null) vs `size` (all rows) |
| Basics | **Named aggregation**: `agg(total=("amount", "sum"), orders=("order_id", "nunique"))` for clean, flat output columns |
| Intermediate | `as_index=False`, `sort=False`, `dropna=False` (keep null keys as a group), `observed=True` for categoricals |
| Intermediate | `transform`: return a result aligned to the original rows (share of group total, group-level z-score, fill with group mean) |
| Intermediate | `filter`: keep whole groups meeting a condition (customers with at least 3 orders) |
| Intermediate | Group-wise ranking and numbering: `rank`, `cumcount`, `cumsum`, `shift`, `diff`, `nlargest` per group — the pandas version of SQL window functions |
| Advanced | `apply`: when it is needed, why it is slow (a Python call per group), and how to replace it with `agg`/`transform` or vectorized code |
| Advanced | Grouping by time with `pd.Grouper(key=..., freq=...)` (bridges to Topic 09) |
| Advanced | Custom aggregation functions and their cost; multiple aggregations on many columns |
| Advanced | Performance: sorted keys, categorical keys, avoiding `object` keys; group counts as a quick cardinality check before joins |

**How to learn it**

1. Read the topic file.
2. Translate 10 SQL `GROUP BY` and window-function queries into pandas.
3. For every aggregation, predict how many rows the output has (= number
   of distinct key combinations).

**Hands-on exercise — `customer_metrics.py`**

1. Per customer: total revenue, order count, distinct products, first and
   last order date — with named aggregation.
2. Each order's share of the customer's total revenue with `transform`.
3. Each customer's order sequence number and days since previous order
   (`cumcount`, `diff` per group).
4. Top 3 products by revenue per country.
5. Customers with at least 5 orders using `filter`.
6. Write the same metrics once with `apply` and once without; benchmark on
   5,000,000 rows and explain the gap.

**Checkpoint:**

- [ ] Explain `count` vs `size` vs `nunique`.
- [ ] Explain `agg` vs `transform` vs `filter` vs `apply` in one sentence
      each.
- [ ] Compute a per-group running total and rank.
- [ ] Replace a slow `apply` with a vectorized alternative.

**Common mistakes:** losing null-key rows because `dropna=True` is the
default; unused categories creating empty groups; `apply` everywhere;
producing `MultiIndex` columns nobody can read.

---

### Topic 07 — [merge, join, concat, and join cardinality](07-merge-join-concat-and-join-cardinality.md)

**Why here:** Joins are the most dangerous operation in data engineering. A
wrong join silently duplicates revenue or drops customers.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `merge` with `how="inner" \| "left" \| "right" \| "outer" \| "cross"`; `on`, `left_on`, `right_on`, `suffixes` |
| Basics | `concat` along rows (stacking files) and columns; `ignore_index=True`; mismatched columns |
| Basics | `join` (index-based) vs `merge` (column-based) |
| Intermediate | **Join cardinality**: one-to-one, one-to-many, many-to-one, many-to-many — and `validate="one_to_one"` / `"one_to_many"` / `"many_to_one"` to fail fast |
| Intermediate | Row-count reasoning: predicting output rows before joining; detecting **row explosion** and **row loss** |
| Intermediate | `indicator=True` and `_merge` for diagnosing unmatched rows; anti-joins (`left_only`) and semi-joins (`isin`) |
| Intermediate | Key hygiene: matching dtypes (`int64` vs `string` keys), whitespace, case, and composite keys |
| Advanced | **Null keys**: pandas matches missing keys to each other in `merge` (unlike SQL, where `NULL` never equals `NULL`) — drop or handle them explicitly |
| Advanced | `merge_asof` for as-of joins (latest price or exchange rate at the time of each order), with `by=`, `direction=`, and `tolerance=` |
| Advanced | Enrichment with lookup tables via `map` vs `merge`; `combine_first` for filling gaps from a secondary source |
| Advanced | Join performance: joining on categoricals or sorted indexes, pre-filtering, reducing columns before joins, memory of wide results |

**How to learn it**

1. Read the topic file.
2. For every join, write a three-line **join contract** first: expected
   cardinality, expected output row count, and how unmatched rows are
   handled.
3. Deliberately create a many-to-many join and measure how many rows it
   produces.

**Hands-on exercise — `enrich_orders.py`**

1. Join orders to customers (`many_to_one`) with `validate=` and
   `indicator=True`; report orders with unknown customers.
2. Join to a products table that accidentally contains duplicate product
   IDs; show the revenue inflation, then catch it with `validate=`.
3. Convert every order to USD with `merge_asof` against a daily FX rate
   table, by currency.
4. Find customers with no orders (anti-join).
5. Concatenate 30 daily files with slightly different columns and align
   them.
6. Assert revenue before and after enrichment is identical — the standard
   join reconciliation check.

**Checkpoint:**

- [ ] Predict the row count of a left join given key cardinalities.
- [ ] Use `validate=` to catch a many-to-many join.
- [ ] Write an anti-join and a semi-join.
- [ ] Explain how pandas treats null keys differently from SQL.
- [ ] Use `merge_asof` for point-in-time enrichment.

**Common mistakes:** joining on keys of different dtypes (no matches, no
error); not checking row counts after a join; duplicate keys in dimension
tables; `outer` joins that hide data problems.

---

### Topic 08 — [Reshaping: pivot, melt, stack, and unstack](08-reshaping-pivot-melt-stack-and-unstack.md)

**Why here:** Sources and consumers disagree about shape. APIs and
spreadsheets deliver wide data; pipelines want long (tidy) data; reports
want wide again.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Long (tidy) vs wide formats and why long is the default for pipelines |
| Basics | `melt` (wide → long) with `id_vars`, `value_vars`, `var_name`, `value_name` |
| Basics | `pivot` (long → wide) and why it raises on duplicate index/column pairs |
| Intermediate | `pivot_table` with `aggfunc`, `fill_value`, `margins`, and multiple values |
| Intermediate | `stack` / `unstack` with `MultiIndex` levels; `crosstab` for frequency tables |
| Intermediate | Flattening `MultiIndex` columns to single strings for output files |
| Advanced | `wide_to_long` for columns like `sales_2023`, `sales_2024` |
| Advanced | One-hot encoding with `get_dummies` (and its column-explosion risk) |
| Advanced | Missing cells created by reshaping: telling "no data" from "zero" |
| Advanced | Shape-driven performance: wide frames with thousands of columns vs long frames with millions of rows |

**How to learn it**

1. Read the topic file.
2. Take one dataset and move it wide → long → wide, asserting you get the
   original back.
3. Predict the output shape of every reshape before running it.

**Hands-on exercise — `reshape_reports.py`**

1. Melt a spreadsheet-style file (one column per month) into long format.
2. Build a country × month revenue report with `pivot_table` and margins.
3. Show `pivot` failing on duplicates and fix it with `pivot_table` or
   deduplication.
4. `unstack` a `groupby` result into a report, then flatten its columns for
   CSV output.
5. Round-trip test: wide → long → wide equals the original.

**Checkpoint:**

- [ ] Explain long vs wide and when each is right.
- [ ] Explain why `pivot` fails where `pivot_table` succeeds.
- [ ] Flatten `MultiIndex` columns into clean names.
- [ ] Distinguish missing cells from true zeros after reshaping.

**Common mistakes:** `fill_value=0` hiding missing data; exploding column
counts with `get_dummies` on high-cardinality columns; leaving `MultiIndex`
columns in output files.

---

## 9. Phase D — Time and Text (Intermediate → Advanced)

### Topic 09 — [Time series: resampling and rolling windows](09-time-series-resampling-and-rolling-windows.md)

**Why here:** Almost every dataset a data engineer handles is time-stamped:
events, orders, logs, metrics, sensor readings.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `DatetimeIndex`, `pd.date_range`, sorting by time, partial-string selection |
| Basics | `tz_localize` (attach a zone to naive times) vs `tz_convert` (change the zone of aware times) |
| Basics | `shift`, `diff`, `pct_change` for period-over-period change |
| Intermediate | **Resampling**: `resample("D").sum()`, `"h"`, `"min"`, `"W"`, `"ME"` (month end), `"MS"` (month start) — and the newer lowercase frequency aliases |
| Intermediate | `label=` and `closed=` for bin edges; `asfreq` vs `resample`; upsampling with `ffill` |
| Intermediate | **Rolling windows**: fixed-count (`rolling(7)`) vs time-based (`rolling("7D")`), `min_periods`, `center`; `expanding`; `ewm` |
| Intermediate | Per-group time series: `groupby(...).resample(...)` and `groupby(...).rolling(...)` |
| Advanced | Detecting gaps and missing periods; building a complete calendar with `reindex` and telling "no events" from "missing data" |
| Advanced | Daylight-saving time: non-existent and ambiguous local times (`nonexistent=`, `ambiguous=`); why pipelines store UTC and convert only for reporting |
| Advanced | Periods (`to_period`, `Period`) for fiscal months and quarters; business days and custom calendars |
| Advanced | Late and out-of-order events in batch data — why rolling windows must be recomputed for affected periods (preview of Modules 2.12 and 2.16) |

**How to learn it**

1. Read the topic file.
2. Draw bins on a timeline for `resample("1h")` with `closed="left"` and
   `closed="right"` and check against the output.
3. Compare `rolling(7)` and `rolling("7D")` on data with missing days.

**Hands-on exercise — `timeseries_metrics.py`**

On 90 days of per-minute website events in UTC:

1. Hourly and daily event counts with `resample`.
2. 7-day rolling average of daily revenue with `rolling("7D")`, per
   country.
3. Detect missing hours per country and report them.
4. Convert to `America/New_York` and `Asia/Kolkata` for a report, and show
   what happens on a daylight-saving transition day.
5. Month-end revenue with `"ME"` and fiscal quarters with periods.
6. Test the results on small frames whose answers you computed by hand.

**Checkpoint:**

- [ ] Explain `tz_localize` vs `tz_convert`.
- [ ] Explain the difference between `rolling(7)` and `rolling("7D")`.
- [ ] Control bin edges with `label` and `closed`.
- [ ] Detect missing periods in a time series.

**Common mistakes:** naive timestamps treated as UTC; resampling unsorted
data; count-based windows on irregular data; daily aggregates computed in
local time without saying which zone.

---

### Topic 10 — [String and datetime accessors](10-string-and-datetime-accessors.md)

**Why here:** Real data arrives as messy text: names, codes, addresses,
free-text fields, and timestamps in strings. Accessors clean it without
loops.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `.str` methods: `strip`, `lower`, `upper`, `title`, `len`, `startswith`, `endswith`, `contains`, `replace`, `slice`, `zfill`, `pad` |
| Basics | `.dt` properties: `year`, `month`, `day`, `hour`, `dayofweek`, `day_name`, `quarter`, `date`, `is_month_end` |
| Intermediate | Regex with `.str.contains(regex=True)`, `.str.extract` (named groups → columns), `.str.extractall`, `.str.findall`, `.str.replace(regex=True)` |
| Intermediate | Splitting: `.str.split(expand=True)`, `.str.rsplit(n=1)`, `.str.partition`; `.str.cat` for joining |
| Intermediate | `.dt.floor`, `.dt.ceil`, `.dt.round` for bucketing; `.dt.tz_convert`; `.dt.strftime` for output formatting; `.dt.to_period` |
| Intermediate | `.cat` accessor for renaming and ordering categories |
| Advanced | Missing values inside accessors: `NA` propagation and `na=False` in `contains` |
| Advanced | Unicode normalisation (`.str.normalize("NFKC")`), accents, and non-breaking spaces in matching keys |
| Advanced | Performance: string dtype vs `object`, Arrow-backed strings, vectorized regex vs `apply` with Python functions |
| Advanced | Parsing mixed timestamp formats safely: try formats in order, count failures, never guess silently |

**How to learn it**

1. Read the topic file.
2. Collect 30 messy values from a real dataset (names, phone numbers,
   product codes) and write the accessor chain that cleans each kind.
3. For every regex, test it on at least five positive and five negative
   examples.

**Hands-on exercise — `text_and_time_cleaning.py`**

1. Clean customer names (trim, collapse spaces, normalise Unicode, title
   case).
2. Extract `area_code` and `number` from phone numbers in five different
   formats with `.str.extract` and named groups; count unparseable values.
3. Split `"City, State ZIP"` addresses into columns.
4. Parse a timestamp column with two known formats, reporting failures.
5. Derive `order_hour`, `order_weekday`, `order_week_start` with `.dt`.
6. Benchmark `.str` methods vs `apply(lambda s: ...)` on 5,000,000 rows.

**Checkpoint:**

- [ ] Extract multiple fields from text with one regex and named groups.
- [ ] Handle missing values safely inside `.str` operations.
- [ ] Bucket timestamps into hours or weeks with `.dt.floor`.
- [ ] Explain why vectorized string methods beat `apply`.

**Common mistakes:** regex special characters treated literally (or vice
versa); ignoring invisible whitespace; `strftime` producing strings too
early in the pipeline.

---

## 10. Phase E — Production-Grade pandas (Advanced)

### Topic 11 — [Method chaining and pipe](11-method-chaining-and-pipe.md)

**Why here:** You now know the operations. This topic is about writing them
as a readable, testable pipeline instead of a long script of mutations.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Chaining methods that return new frames: `.rename().astype().query().assign().sort_values()` |
| Basics | `assign` with lambdas to reference columns created earlier in the same chain |
| Intermediate | `pipe(func, *args)` to insert your own functions into a chain |
| Intermediate | Structuring a transformation as small, pure, named steps (`standardise_columns`, `drop_test_orders`, `add_revenue`) composed with `pipe` |
| Intermediate | Formatting long chains (one method per line, inside parentheses); naming intermediate results when a chain gets too long |
| Advanced | Debugging chains: a `log_shape` / `check` step inserted with `pipe` to log row counts and assert invariants mid-chain |
| Advanced | Avoiding `inplace=True` (no real benefit, breaks chaining) |
| Advanced | Custom accessors with `pd.api.extensions.register_dataframe_accessor` for team-wide helpers (e.g. `df.dq.null_report()`) |
| Advanced | Testing chains: each step unit-tested on tiny frames; the whole chain tested end to end |

**How to learn it**

1. Read the topic file.
2. Take your messiest script from Topics 05–08 and rewrite it as a chain of
   `pipe` steps.
3. Compare the two versions for readability, testability, and debugging.

**Hands-on exercise — `silver_pipeline.py`**

1. Build `build_silver_orders(raw: pd.DataFrame) -> pd.DataFrame` as one
   chain of at least eight `pipe` steps reusing your earlier functions.
2. Add a `check_step(df, name, min_rows=..., unique=...)` helper that logs
   row counts and raises on violated invariants.
3. Unit-test each step and integration-test the whole chain.
4. Register a `dq` accessor with `null_report()` and `duplicate_report(key)`
   methods.

**Checkpoint:**

- [ ] Rewrite a mutation-heavy script as a method chain.
- [ ] Use `assign` with a lambda that references a column created earlier.
- [ ] Log and assert invariants in the middle of a chain.
- [ ] Explain why `inplace=True` is discouraged.

**Common mistakes:** 40-line chains nobody can debug; hiding side effects
(file writes, network calls) inside `pipe` steps; lambdas that capture the
wrong variable.

---

### Topic 12 — [Copy-on-Write and chained-assignment pitfalls](12-copy-on-write-and-chained-assignment-pitfalls.md)

**Why here:** After writing a lot of pandas, you are ready to understand
exactly when a change to one object does or does not affect another — and
why legacy code behaves differently.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The problem: does `subset = df[df.x > 0]; subset["y"] = 1` change `df`? |
| Basics | **Chained assignment** (`df["col"][mask] = value`) and why it never updates `df` under Copy-on-Write |
| Basics | The fix: always assign with one `loc` call: `df.loc[mask, "col"] = value` |
| Intermediate | **Copy-on-Write (CoW)**: every indexing result *behaves* like a copy; data is only physically copied when one side is modified — so no hidden aliasing, and fewer defensive copies |
| Intermediate | Migrating legacy pandas 1.x / 2.x code: `SettingWithCopyWarning` (removed in pandas 3), `ChainedAssignmentError` warnings, and code that relied on views |
| Intermediate | When `.copy()` is still useful: making intent explicit at function boundaries, or releasing a large parent frame's memory |
| Advanced | CoW and performance: avoiding unnecessary copies in chains; methods that now return lazy copies |
| Advanced | CoW and NumPy interop: `df.to_numpy()` / `.values` may return read-only arrays; copying before mutating the array |
| Advanced | Writing functions that never mutate their inputs, and tests that prove it (compare against a deep copy) |

**How to learn it**

1. Read the topic file.
2. Write ten small snippets that modify a subset, a column, or a NumPy
   array from a frame. Predict whether the parent changes; verify.
3. If you have access to legacy code (or examples online), migrate one
   script that uses chained assignment.

**Hands-on exercise — `cow_lab.py`**

1. Reproduce a chained-assignment bug and show `df` unchanged; fix it with
   `loc`.
2. Show that modifying a filtered subset never changes the parent.
3. Show that `df.to_numpy()` can be read-only and handle it correctly.
4. Write a pytest fixture that deep-copies inputs and a test helper that
   asserts a transformation function did not mutate its input.
5. Refactor a function that used `inplace=True` and defensive `.copy()`
   calls everywhere; measure memory before and after.

**Checkpoint:**

- [ ] Explain Copy-on-Write in two sentences.
- [ ] Explain why chained assignment silently does nothing.
- [ ] Write every conditional assignment as a single `loc` call.
- [ ] Prove with a test that a function does not mutate its input.

**Common mistakes:** trusting behaviour from old Stack Overflow answers
written for pandas 1.x; sprinkling `.copy()` everywhere "to silence
warnings"; mutating arrays returned by `to_numpy()`.

---

### Topic 13 — [Chunked processing and memory reduction](13-chunked-processing-and-memory-reduction.md)

**Why last:** It combines dtypes (04), I/O (02), groupby (06), and
Copy-on-Write (12) to answer the production question: *what do I do when
the data does not fit?*

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Measuring memory: `df.info(memory_usage="deep")`, `memory_usage(deep=True)`; the rule of thumb that pandas needs several times the data size in RAM for operations |
| Basics | Reading less: `usecols`, `dtype`, `nrows`, Parquet `columns=` and `filters=` |
| Intermediate | Shrinking columns: downcasting with `pd.to_numeric(downcast=...)`, `category` for low-cardinality strings, Arrow-backed strings, dropping unused columns early |
| Intermediate | **Chunked reading**: `read_csv(chunksize=...)` / `iterator=True` and `read_sql(chunksize=...)`; processing each chunk and combining results |
| Intermediate | Combining chunk results for group aggregates: partial `groupby` sums and counts per chunk, then a final `groupby` over the partials |
| Intermediate | Chunked writing: appending to CSV safely (header only once), writing one Parquet file per chunk or streaming with `pyarrow.parquet.ParquetWriter` |
| Advanced | Chunk-boundary bugs: deduplication, sessions, and rolling windows that span two chunks; carrying state between chunks |
| Advanced | Processing partitioned inputs (one file per day) as natural chunks; idempotent re-runs per partition |
| Advanced | Freeing memory: dropping references, `del`, and why memory may not return to the OS immediately |
| Advanced | Knowing when to stop: signs that pandas is the wrong tool (data several times larger than RAM, multi-core needs, many joins on big tables) and the alternatives — Polars and DuckDB (Module 2.4), Dask (Module 2.21), Spark (Module 2.14) |

**How to learn it**

1. Read the topic file.
2. Take one dataset and reduce its in-memory size by at least 70% through
   typing alone; record each step's saving.
3. Rewrite one full-load aggregation as a chunked aggregation and prove
   both give the same answer.

**Hands-on exercise — `big_file_pipeline.py`**

Using a CSV larger than a comfortable share of your RAM (e.g. several years
of NYC taxi trips, or generated data of 5–10 GB):

1. Read with `usecols` and explicit compact dtypes; measure memory per
   chunk.
2. Compute daily trip counts, revenue, and average fare per payment type by
   combining chunked partial aggregates.
3. Deduplicate trips across chunk boundaries by carrying the set of seen
   keys (and discuss the memory limits of that approach).
4. Write cleaned output as partitioned Parquet (one file per month).
5. Compare total runtime and peak memory against a naive full load (on a
   subset small enough to fit), and write a note on when you would switch
   to Polars or DuckDB.

**Checkpoint:**

- [ ] Reduce a frame's memory with dtypes and measure the result.
- [ ] Aggregate a file larger than memory with `chunksize`.
- [ ] Explain which operations are unsafe across chunk boundaries.
- [ ] Explain when pandas is no longer the right tool.

**Common mistakes:** computing averages of averages across chunks;
appending CSV headers for every chunk; deduplicating only within each
chunk; forcing pandas onto data that should go to a columnar engine.

---

## 11. Consolidate — practice questions and interview practice

### [`practice-questions.md`](practice-questions.md)

For every question:

1. Write the input schema (columns and dtypes) and the expected output
   schema.
2. Predict the output row count and write it as an assertion.
3. Solve it on a 5–10 row frame you typed yourself.
4. Write the solution as a small function (or `pipe` chain) with tests.
5. Run it on a large generated frame and check runtime and memory.

### [`interview-practice.md`](interview-practice.md)

Data engineering interviews test pandas through realistic tasks, not API
trivia. Practise each question **out loud** with a 20-minute timer:

1. Clarify: keys, grain, nulls, duplicates, time zones, expected size.
2. State the plan in plain English before coding.
3. Code it, then state the output row count and how you would verify it.
4. Discuss trade-offs: performance at 100× the data, and whether you would
   use pandas, SQL, Polars, or Spark for it.

Typical question themes to expect: latest record per key, top-N per group,
sessionisation, month-over-month growth, join row-count reasoning, pivoting
a report, deduplication with rules, gaps in a time series, and "this job
runs out of memory — what do you do?".

---

## 12. Module mini-project — order-to-revenue pipeline in pandas

This is the proof that you have finished the module.

**Scenario:** An e-commerce company gives you:

- `orders_*.csv` — 90 daily files, about 200,000 rows each, with updates
  to the same order across days, messy statuses, and mixed timestamp
  formats.
- `customers.jsonl` — customer records with leading-zero IDs and messy
  names.
- `products.xlsx` — a product catalogue with one accidental duplicate
  product ID.
- `fx_rates.parquet` — daily exchange rates per currency.

Build `revenue_pipeline/`, a `uv` project with:

1. **Bronze** — read every source with explicit reader contracts; write
   each to Parquet unchanged plus `_ingested_at` and `_source_file`
   columns.
2. **Silver** — typed schemas (nullable and categorical dtypes, UTC
   timestamps), cleaned strings, latest version per order, outlier flags,
   a quarantine table with `dq_reason`, and a cleaning report.
3. **Enrichment** — validated `many_to_one` joins to customers and
   products (catch the duplicate product); `merge_asof` to convert to USD.
4. **Gold** — daily revenue by country (with 7-day rolling average), a
   customer summary (lifetime value, order count, days between orders), and
   a country × month pivot report.
5. **Scale** — process the daily order files in chunks or per-partition so
   peak memory stays under a limit you set (e.g. 1 GB).
6. **Code quality** — every stage written as `pipe` chains of pure
   functions; no chained assignment; no `inplace=True`; no `apply` where a
   vectorized method exists.
7. **Checks and tests** — pytest tests for each step; reconciliation checks
   (rows in = rows out + quarantined; revenue unchanged by joins);
   a `run_metadata.json` with row counts, runtime, and peak memory.

**Grading yourself:** the pipeline is idempotent (running twice produces
identical outputs), every join has a written cardinality contract enforced
with `validate=`, every dtype is intentional, and you can explain every row
count in the run metadata.

---

## 13. Module self-assessment — exit criteria

Only move to Module 2.4 when you can tick every box without looking at your
notes:

- [ ] I can explain Index alignment and use `MultiIndex` when needed.
- [ ] I can read and write CSV, JSON Lines, Parquet, Excel, and SQL with
      explicit types.
- [ ] I can select and assign precisely with `loc`, `iloc`, and `query`.
- [ ] I can choose nullable, categorical, and timezone-aware dtypes.
- [ ] I can clean missing values, duplicates, and outliers with an audit
      trail.
- [ ] I can use `agg`, `transform`, and `filter`, and avoid slow `apply`.
- [ ] I can predict and validate join cardinality and row counts.
- [ ] I can reshape between long and wide formats.
- [ ] I can resample, roll, and as-of join time series in UTC.
- [ ] I can clean text and timestamps with accessors.
- [ ] I can write testable `pipe` chains and avoid chained assignment.
- [ ] I can process data larger than memory and know when to leave pandas.
- [ ] I have finished the practice questions, interview practice, and the
      mini-project.

---

## 14. Recommended reading and references

| Resource | Relevant topics |
| --- | --- |
| pandas official documentation — User Guide (IO tools, indexing, groupby, merging, reshaping, time series, text data, Copy-on-Write, scaling to large datasets) | All topics |
| pandas docs — "What's new" pages for 2.x and 3.x releases | 04, 12 |
| *Python for Data Analysis*, 3rd edition — Wes McKinney (O'Reilly) | 01–10 |
| *Effective Pandas*, 2nd edition — Matt Harrison | 04, 06, 11 |
| *Pandas Cookbook*, 3rd edition — William Ayd and Matthew Harrison (Packt) | 02, 04, 06–09, 13 |
| Tom Augspurger — "Modern Pandas" blog series | 11, 13 |

---

## 15. Where this module leads

| This module's idea | Where it goes deeper |
| --- | --- |
| Arrow-backed dtypes, zero-copy, faster engines | 2.4 Arrow, Polars, and DuckDB |
| Parquet `columns=` / `filters=` / partitions | 2.5 Data Formats — Parquet internals and partitioning |
| `groupby` and window-like operations | 2.6 SQL for Data Engineers — window functions |
| `read_sql` / `to_sql` | 2.7 Python Database Connectivity — bulk loading and server-side cursors |
| Grain, keys, and join cardinality | 2.8 Data Modelling for Analytics |
| Schema checks and quarantine | 2.11 Data Validation — Pandera and data contracts |
| Deduplication, merge loads, late data | 2.12 Transformation Patterns and Pipeline Design |
| pandas UDFs and Arrow batches | 2.14 PySpark |
| DataFrame testing | 2.19 Testing Data Pipelines |
| Out-of-core processing | 2.21 Performance — Dask and Ray |

pandas is where most engineers first learn to think in columns, keys, and
grains. The habits you build here — predicting row counts, enforcing
dtypes, validating joins, and reconciling totals — are exactly the habits
that keep Spark, SQL, and streaming pipelines correct later in Stage 2.
