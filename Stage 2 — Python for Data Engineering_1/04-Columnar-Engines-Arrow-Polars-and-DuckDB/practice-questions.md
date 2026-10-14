# Module 2.4 Practice Questions

## How to Use This Practice Set

This practice set consolidates the eight topics in Module 2.4: Apache Arrow, Polars expressions and contexts, the Polars Lazy API and query optimization, Polars streaming, DuckDB in-process analytics, DuckDB file/object-storage querying, cross-engine interoperability, and engine selection.

Each problem is immediately followed by its solution. Do not read the solution first. For implementation questions, first attempt the task on a small deterministic dataset, validate correctness, then scale or benchmark where requested.

For benchmark questions, all measurements must come from the learner's own environment. Hardware, library versions, file format, cache state, data distribution, and configuration materially affect results.

## Practice Data Setup

Some implementation questions use small local files so the solutions can be executed without relying on external datasets. Run this setup once before those questions. It is deterministic (no random data), safe to run repeatedly, and creates `practice_data/orders/part-001.parquet`, `practice_data/orders/part-002.parquet`, `practice_data/orders.parquet` and `practice_data/data.csv` in the current directory. It needs `pandas` and `pyarrow`.

```python
from pathlib import Path

import pandas as pd

DATA_DIR = Path("practice_data")
ORDERS_DIR = DATA_DIR / "orders"
ORDERS_DIR.mkdir(parents=True, exist_ok=True)  # safe to run repeatedly

orders = pd.DataFrame(
    {
        "order_id": [1, 2, 3, 4, 5, 6, 7, 8],
        "customer_id": [10, 10, 20, 20, 30, 30, 10, 20],
        "order_date": pd.to_datetime(
            [
                "2025-12-30",
                "2026-01-02",
                "2026-01-03",
                "2026-01-04",
                "2026-01-05",
                "2026-01-06",
                "2026-01-07",
                "2026-01-08",
            ]
        ),
        "amount": [100.0, 50.0, 80.0, 120.0, 60.0, 40.0, 25.0, 75.0],
        "status": ["PAID", "CANCELLED", "PAID", "PAID", "PENDING", "PAID", "PAID", "CANCELLED"],
        "notes": ["", "late", "", "gift", "", "", "repeat", "refund"],
    }
)

# orders/*.parquet: two part files; orders.parquet: the same rows in one file
orders.iloc[:4].to_parquet(ORDERS_DIR / "part-001.parquet", index=False)
orders.iloc[4:].to_parquet(ORDERS_DIR / "part-002.parquet", index=False)
orders.to_parquet(DATA_DIR / "orders.parquet", index=False)

# data.csv, including a string column for the pandas object-dtype question
orders.to_csv(DATA_DIR / "data.csv", index=False)

print(sorted(str(p) for p in DATA_DIR.rglob("*") if p.is_file()))
```

The fixture has 8 rows. It is far too small to reproduce a real out-of-memory condition or meaningful performance differences; it only makes the plan and API semantics executable. Questions about remote storage (`s3://...`) stay conceptual, and their setup belongs to Topic 06.

## Coverage Map

| Range | Primary focus | Typical evidence |
|---|---|---|
| Questions 1–10 | Fundamentals across all eight topics | simple code, schemas, direct reasoning |
| Questions 11–20 | Multi-concept practice | joins, plans, files, memory, interoperability, benchmark setup |
| Questions 21–30 | Debugging and performance engineering | optimizer blockers, streaming state, remote I/O, conversion cost |
| Questions 31–40 | Senior architecture and decision-making | production design, ADRs, benchmark interpretation, scale boundaries |

---

# Part I — Basic

## Question 1 — B01: Inspect an Arrow Nullable String Column

### Difficulty
Basic

### Topics Covered
- Topic 01 — Apache Arrow columnar memory model
- `Array`, `DataType`, validity bitmap, offsets buffer, data buffer, `buffers()`, null semantics

### Problem

You receive the following logical data:

```text
name
----
Alice
NULL
Bob

```

You need to explain how Arrow represents this nullable variable-width string column. A teammate says, "Arrow stores each Python string as an individual object and keeps a Boolean flag beside every value."

### What You Need to Do

1. Create the array with PyArrow.
2. Print its type, length, and buffers.
3. Explain what the validity bitmap represents.
4. Explain what the offsets buffer represents.
5. Explain what the data buffer represents.
6. State why this representation differs from a Python list of strings.

### Solution

```python
import pyarrow as pa

arr = pa.array(["Alice", None, "Bob"], type=pa.string())

print("type:", arr.type)
print("length:", len(arr))
print("buffers:", arr.buffers())
```

Conceptually, the array contains three important pieces for this nullable string representation:

```text
validity bitmap
    ↓
which logical slots are valid/null

offsets buffer
    ↓
where each string begins/ends in the data bytes

data buffer
    ↓
raw string bytes
```

The validity bitmap identifies the second logical value as null. The offsets describe the boundaries of the string values in the byte buffer. The data buffer contains the actual bytes for the non-null strings.

### Additional consolidation

Also inspect Arrow construction through several input forms and measure allocator usage:

```python
import numpy as np
import pandas as pd
import pyarrow as pa

arr_from_list = pa.array([1, 2, None], type=pa.int64())
table_from_dict = pa.Table.from_pydict({"id": [1, 2], "name": ["A", "B"]})
array_from_numpy = pa.array(np.array([1, 2, 3], dtype=np.int64))
table_from_pandas = pa.Table.from_pandas(pd.DataFrame({"id": [1, 2]}))

print(table_from_dict.schema)
print(table_from_dict.num_rows)
print(table_from_dict.nbytes)
print(pa.total_allocated_bytes())
```

For compute, know the Arrow-native family represented by `pyarrow.compute`, including filtering, arithmetic, aggregation, `take`, and `sort_indices`. These operate on Arrow data without first requiring a pandas conversion.
### How to Solve It

1. Start from the logical type: a nullable variable-length string array.
2. Because strings are variable-length, Arrow needs offsets to determine boundaries.
3. Because null is a first-class state, Arrow may need a validity bitmap.
4. Use `arr.buffers()` to inspect the underlying buffers instead of guessing.
5. Compare the result with a Python list, where each element is a Python object/reference rather than one Arrow columnar representation.

### Why This Works

Arrow separates logical values from their physical storage. Variable-length strings cannot be represented as one fixed-width value per row, so offsets identify the byte ranges belonging to each value. Nullability is represented separately from the string bytes.

The important lesson is that Arrow is a columnar memory representation, not a collection of Python string objects. The exact low-level buffer layout depends on the Arrow data type, but the mental model of validity plus offsets plus data is the correct foundation for nullable strings.

### Production Lesson

When performance matters, reason from the physical representation instead of only the logical schema. Fixed-width columns, variable-width strings, and nested values have different memory costs. `nbytes`, `buffers()`, and the Arrow schema are useful investigative tools when a pipeline unexpectedly consumes memory.

---

## Question 2 — B02: Array, ChunkedArray, RecordBatch, or Table?

### Difficulty
Basic

### Topics Covered
- Topic 01 — Arrow object model
- `Array`, `ChunkedArray`, `RecordBatch`, `Table`, `Schema`, immutability, `combine_chunks()`

### Problem

A data engineer is confused by four Arrow objects. They have a full table, one logical column split into several chunks, and a batch used for incremental processing. They want to know which object represents each concept.

### What You Need to Do

Match these concepts to Arrow objects:

1. One typed sequence of values.
2. One logical column made from multiple arrays.
3. A collection of equal-length arrays for one batch of rows.
4. A complete tabular structure with named columns and a schema.
5. Explain when `combine_chunks()` may be relevant.

### Solution

```text
1. Array
2. ChunkedArray
3. RecordBatch
4. Table
5. combine_chunks() can consolidate a chunked logical column into fewer/one chunk when the consumer benefits from that layout; consolidation can require additional allocation/copying.
```

A compact construction example is:

```python
import pyarrow as pa

arr = pa.array([1, 2, 3])
chunked = pa.chunked_array([[1, 2], [3, 4]])
batch = pa.record_batch({"id": [1, 2], "amount": [10.0, 20.0]})
table = pa.table({"id": [1, 2, 3], "amount": [10.0, 20.0, 30.0]})

print(type(arr))
print(type(chunked))
print(type(batch))
print(type(table))
```

### Additional consolidation

Extend the investigation to these Arrow concepts:

- dictionary encoding for repeated categorical-like values;
- run-end encoding as a compact representation for runs;
- slicing and the zero-copy slicing concept;
- batch sizing when producing `RecordBatch` objects;
- `table.combine_chunks()` as a possible but non-free consolidation step;
- `pa.total_allocated_bytes()` and the Arrow memory pool as allocator observations;
- schema metadata attached to an Arrow schema;
- Arrow IPC streaming/file representations;
- Feather v2 as an Arrow IPC-oriented file format;
- memory-mapped access to suitable Arrow IPC files;
- Arrow Flight as an Arrow-oriented transport;
- ADBC as Arrow Database Connectivity.

For the transport items, remain at architecture-awareness depth: distinguish serialization/transport from in-process shared buffers.
### How to Solve It

Think about the unit being represented:

```text
Array         → one typed sequence
ChunkedArray  → one logical column, multiple chunks
RecordBatch   → one batch of rows, columnar internally
Table         → complete table across columns/chunks
```

If a consumer requires a different chunk layout, consolidation may be necessary. That is precisely why chunking matters in interoperability work.

### Why This Works

These objects serve different layers of the Arrow model. A `RecordBatch` is naturally suited to incremental movement, while a `Table` is a complete logical table. A `ChunkedArray` lets one logical column consist of multiple physical arrays without requiring immediate consolidation.

Arrow is also designed around immutable array/table semantics: transformations generally create new logical objects rather than mutating existing buffers in place.

### Production Lesson

Do not treat "Arrow table" and "Arrow batch" as interchangeable. Large pipelines often benefit from streaming `RecordBatch` objects, while small analytical results can use a `Table`. Chunk layout can become a real performance consideration when data crosses engine boundaries.

---

## Question 3 — B03: Choose the Correct Polars Context

### Difficulty
Basic

### Topics Covered
- Topic 02 — Polars expressions and contexts
- `pl.col`, `pl.lit`, `select`, `with_columns`, `filter`, `group_by().agg()`, immutability

### Problem

You have this DataFrame:

```python
import polars as pl

df = pl.DataFrame(
    {
        "customer": ["A", "A", "B"],
        "amount": [100, 50, 200],
        "status": ["PAID", "REFUND", "PAID"],
    }
)
```

You need to perform four different tasks:

1. Create only `customer` and a derived `gross_amount = amount * 1.18`.
2. Keep every existing column and add `gross_amount`.
3. Keep only rows where `status == "PAID"`.
4. Produce one row per customer with total amount.

### What You Need to Do

Write idiomatic Polars expressions for all four tasks and explain why each context is different.

### Solution

```python
import polars as pl

df = pl.DataFrame(
    {
        "customer": ["A", "A", "B"],
        "amount": [100, 50, 200],
        "status": ["PAID", "REFUND", "PAID"],
    }
)

# 1. Projection / derived output
result_1 = df.select(
    "customer",
    (pl.col("amount") * 1.18).alias("gross_amount"),
)

# 2. Keep existing columns and add a derived column
result_2 = df.with_columns(
    (pl.col("amount") * 1.18).alias("gross_amount")
)

# 3. Filter rows
result_3 = df.filter(
    pl.col("status") == "PAID"
)

# 4. Aggregate by customer
result_4 = df.group_by("customer").agg(
    pl.col("amount").sum().alias("total_amount")
)
```

### Additional consolidation

For one derived expression, use both a column reference and a literal, then show an explicit cast:

```python
result = df.with_columns(
    (pl.col("amount") * pl.lit(1.18)).alias("gross"),
    pl.col("amount").cast(pl.Float64).alias("amount_float"),
)
```

For file ingestion, be prepared to use an explicit `schema=` or `schema_overrides=` policy rather than relying on inference when the data contract requires stable types.
### How to Solve It

Use the intent of the operation:

```text
select()           → define the output columns
with_columns()     → retain columns and add/replace columns
filter()           → retain rows
filter group_by    → summarize groups
```

The expressions such as `pl.col("amount") * 1.18` are recipes. The context determines how the recipe is applied.

### Why This Works

Polars separates expressions from contexts. The same expression can behave differently depending on whether it is evaluated as a projection, a column transformation, a filter, or a group aggregation. This is one reason Polars code is declarative rather than row-by-row procedural.

The DataFrame itself is treated as immutable from the learner's perspective: these operations produce results rather than silently mutating the original object.

### Production Lesson

Correct context selection improves readability and reduces accidental shape changes. In production pipelines, make the intended output explicit. A transformation that accidentally drops columns because `select()` was used instead of `with_columns()` can create a data-loss bug that is harder to detect than a syntax error.

---

## Question 4 — B04: Fix Null-vs-NaN Logic in Polars

### Difficulty
Basic

### Topics Covered
- Topic 02 — `null` vs `NaN`, conditional expressions, dtypes, `when().then().otherwise()`

### Problem

A pipeline needs to classify orders using this rule:

- missing `amount` (`null`) → `"MISSING"`
- actual IEEE floating-point `NaN` → `"INVALID"`
- positive amount → `"VALID"`
- zero or negative amount → `"NON_POSITIVE"`

The engineer says, "`null` and `NaN` are the same thing." That is incorrect.

### What You Need to Do

Create a Polars DataFrame containing all four cases and write an expression using `when().then().otherwise()` that distinguishes them correctly. Also demonstrate, briefly, how you would use `cs.numeric()` to target numeric columns, `.str` for string cleanup, `.dt` for temporal extraction, and `.name`/other namespaces when they are relevant. State how `Categorical`, `Enum`, `Date`, `Datetime`, `Duration`, `List`, and `Struct` differ conceptually from plain strings/numbers. Explain the semantic difference between `null` and `NaN`.

### Solution

```python
import math
import polars as pl

df = pl.DataFrame(
    {
        "amount": [100.0, None, float("nan"), -5.0]
    }
)

result = df.with_columns(
    pl.when(pl.col("amount").is_null())
      .then(pl.lit("MISSING"))
      .when(pl.col("amount").is_nan())
      .then(pl.lit("INVALID"))
      .when(pl.col("amount") > 0)
      .then(pl.lit("VALID"))
      .otherwise(pl.lit("NON_POSITIVE"))
      .alias("classification")
)
```

Expected classifications:

```text
100.0       → VALID
null        → MISSING
NaN         → INVALID
-5.0        → NON_POSITIVE
```

### Additional consolidation

Useful related operations to recognize from this module include:

```python
import polars.selectors as cs

numeric_filled = df.with_columns(
    cs.numeric().fill_null(0)
)
```

The namespace model includes `.str`, `.dt`, `.list`, `.struct`, `.cat`, and `.name`. A selector such as `cs.starts_with("amt")` can express a schema-level rule across columns. Use such selectors deliberately: a broad selector can accidentally include future columns.
### How to Solve It

1. Test `is_null()` first because null is missingness, not a floating-point value.
2. Test `is_nan()` separately for floating-point NaN.
3. Apply the positive-value rule.
4. Use `otherwise()` for the remaining numeric values.

Do not replace the first two conditions with a single generic missingness test.

### Why This Works

Null has a semantic meaning of missing/absent value. NaN is a floating-point value representing an undefined or non-finite numeric result. Polars exposes different operations for them because they are physically and semantically different concepts.

This matters for analytics because aggregations, comparisons, validation, and downstream serialization can treat them differently.

### Production Lesson

Null semantics are part of the data contract. A pipeline that collapses null and NaN without a business decision can silently change metrics or data-quality signals. Validate missingness semantics explicitly when moving between pandas, Arrow, Polars, and DuckDB.

---

## Question 5 — B05: Lazy or Eager?

### Difficulty
Basic

### Topics Covered
- Topic 03 — eager vs lazy execution, `LazyFrame`, `collect()`, `scan_parquet()`, projection/filter pushdown

### Problem

A developer writes:

```python
import polars as pl

lf = (
    pl.scan_parquet("orders/*.parquet")
    .filter(pl.col("status") == "PAID")
    .select(["customer_id", "amount"])
)
```

They say, "The file has already been read because `lf` exists." Another engineer says, "No, the work starts when `collect()` is called."

### What You Need to Do

1. State which engineer is correct.
2. Explain the role of `LazyFrame`.
3. Show the line that triggers execution.
4. Explain two optimizations the engine may apply before reading the final required data.

### Solution

The second engineer is correct: creating the `LazyFrame` builds a description of the work rather than immediately materializing the result.

```python
result = lf.collect()
```

Two important optimization opportunities are:

```text
predicate pushdown
→ push the compatible status filter toward the scan

projection pushdown
→ request/use only customer_id and amount where the source supports it
```

### Additional consolidation

In the same family of lazy scans, the module also covers:

```python
pl.scan_csv(...)
pl.scan_ndjson(...)
pl.scan_ipc(...)
```

Use `lf.collect_schema()` when you need schema information without executing the full data transformation. Where supported, `lf.show_graph()` gives a visual plan. Other optimization topics to recognize are slice pushdown, common subplan elimination, common subexpression elimination, and simplification. The module also treats `pl.collect_all([...])`, lazy sinks, and `LazyFrame → LazyFrame` function design as production patterns.
### How to Solve It

Separate the lifecycle:

```text
scan_parquet()
    ↓
LazyFrame / logical plan
    ↓
optimizations
    ↓
collect()
    ↓
execution
```

The important distinction is:

```text
lazy = when the work is described
collect = when the work is executed
```

### Optimization checklist

After building the plan, investigate:

```text
predicate pushdown
projection pushdown
slice pushdown
common subplan elimination
common subexpression elimination
simplification
Parquet column pruning
row-group skipping
Hive partition pruning
```

Do not treat these as guaranteed. The exact optimized plan depends on the query, source, and installed Polars version.
### Why This Works

Lazy execution lets the optimizer see the whole query before execution. That visibility can reduce the amount of data read and processed. The optimized plan can preserve the same result while representing less work than a naive step-by-step execution.

A `LazyFrame` is therefore not just a delayed DataFrame; it is a query description.

### Production Lesson

Do not assume that writing code line-by-line means execution happens line-by-line. When working with large files, keeping the pipeline lazy until the intended execution boundary gives the optimizer the opportunity to reduce I/O and memory use.

---

## Question 6 — B06: Lazy Is Not the Same as Streaming

### Difficulty
Basic

### Topics Covered
- Topic 03 and Topic 04 — lazy vs streaming, `collect(engine="streaming")`, streaming sinks

### Problem

A colleague writes:

```python
lf = pl.scan_parquet("huge/*.parquet").filter(pl.col("amount") > 0)
```

and claims, "Because it is lazy, the query will automatically use constant memory."

### What You Need to Do

Explain why that statement is wrong. Then show:

1. how to explicitly request streaming execution when a final DataFrame is required;
2. how to use a sink when the final result itself is too large to materialize comfortably.

### Solution

The important distinction is:

```text
Lazy execution
= defer execution + build/optimize a plan

Streaming execution
= execute a compatible plan incrementally
```

A final DataFrame can be collected explicitly with:

```python
result = lf.collect(engine="streaming")
```

If the output is large, a sink may be more appropriate:

```python
lf.sink_parquet("gold/result.parquet")
```

A runnable variant against the practice fixture (run the Practice Data Setup first). This 8-row fixture demonstrates the plan semantics and the API calls; it is not large enough to reproduce a real out-of-memory condition.

```python
from pathlib import Path

import polars as pl

lf = pl.scan_parquet("practice_data/orders/*.parquet").filter(pl.col("amount") > 0)

result = lf.collect(engine="streaming")
print(result.height)

Path("practice_data/out").mkdir(exist_ok=True)
lf.sink_parquet("practice_data/out/result.parquet")
```

### Sink API coverage

For the same concept, know the lazy sink family explicitly:

```python
lf.sink_parquet("out.parquet")
lf.sink_csv("out.csv")
lf.sink_ipc("out.arrow")
lf.sink_ndjson("out.ndjson")
```

Use the current installed Polars API when executing these examples.
### How to Solve It

1. Ask first whether the query should remain lazy. Yes.
2. Ask how execution should happen. That is a separate decision.
3. If the output is small enough, `collect(engine="streaming")` can request streaming execution while still producing a DataFrame.
4. If the output is itself very large, use a sink to avoid materializing the entire result.
5. Remember that state-heavy operators can still consume significant memory.

### Streaming investigation checklist

Classify the operators in the pipeline as generally streaming-friendly, potentially state-heavy, often difficult for straightforward streaming, or version/query dependent. Investigate group-by state, join/build-side state, global sort, selected windows, pivot, partition-wise semantics, and fallback behaviour. Measure peak memory with a documented process-level method such as:

```bash
/usr/bin/time -v python pipeline.py
```

Record maximum resident set size, elapsed time, dataset size, CPU/RAM, and thread configuration. `POLARS_MAX_THREADS` is a resource-control lever, not a promise that more threads are better.
### Why This Works

Streaming reduces peak working memory by processing data incrementally. It does not guarantee constant memory because aggregations, joins, sorts, windows, and output buffering may require retained state.

Likewise, lazy execution does not itself guarantee streaming. A LazyFrame can still be executed using a non-streaming strategy.

### Production Lesson

Resource behaviour is an execution-property question, not a syntax-property question. In production, explicitly identify the execution strategy, measure peak memory, and inspect whether the final output should be collected or sunk incrementally.

---

## Question 7 — B07: First DuckDB Query and Result Representation

### Difficulty
Basic

### Topics Covered
- Topic 05 — DuckDB in-process architecture, `duckdb.sql()`, result retrieval, `.fetchall()`, `.df()`, `.pl()`, `.to_arrow_table()` for an Arrow Table

### Problem

You want to run a tiny analytical query directly inside Python without starting a database server.

### What You Need to Do

1. Write a one-query example using `duckdb.sql()`.
2. Show how the result can be retrieved as Python rows, pandas, Polars, and Arrow.
3. Explain what "in-process" means.

### Solution

```python
import duckdb

result = duckdb.sql(
    """
    SELECT 1 AS id, 25.5 AS amount
    """
)

rows = result.fetchall()
pandas_df = result.df()
polars_df = result.pl()
arrow_table = result.to_arrow_table()

print(rows)
print(pandas_df)
print(polars_df)
print(arrow_table)
```

Conceptually:

```text
Python process
    ├── application code
    └── DuckDB engine
```

There is no separate DuckDB server required for this in-process execution.

`.to_arrow_table()` returns a `pyarrow.Table`. (`.arrow()` is only a legacy/compatibility alias for the Arrow reader path, so it is not used for table retrieval.)

### Additional consolidation

This same result object can also lead into the DuckDB relational Python API. Know that the module covers analytics-friendly SQL such as `GROUP BY ALL`, `SELECT * EXCLUDE`, `REPLACE`, `QUALIFY`, `ASOF JOIN`, `PIVOT`, `UNPIVOT`, FROM-first syntax, list functions, and struct functions. The relational API can be useful for programmatic composition, while plain SQL is often clearer when the transformation is naturally expressed as SQL.
### Result-conversion coverage

For small numerical results, the module also covers `.fetchnumpy()`. Treat it like `.fetchall()`: choose it because a downstream NumPy representation is actually useful, not simply because the method exists.
### How to Solve It

1. Import DuckDB.
2. Use `duckdb.sql()` for convenient SQL execution.
3. Keep the returned result object until you choose the representation needed by the next stage.
4. Use `.fetchall()` for tiny results; use DataFrame/Arrow representations when the downstream consumer requires them.

### Parameter and resource awareness

When values are user-controlled, use parameterized SQL with `?` placeholders rather than string interpolation. For production resource control, the module also covers `memory_limit`, `threads`, and `temp_directory`, plus `EXPLAIN`/`EXPLAIN ANALYZE`. These concerns are part of using DuckDB as an analytical engine rather than treating it as a convenience SQL helper.
### Why This Works

DuckDB embeds the analytical database/query engine into the process. That gives a direct local execution path and makes DuckDB particularly convenient for embedded analytics, local ETL, CI, and analytical SQL over files or Python objects.

The result conversion method is a separate design choice from the SQL itself.

### Production Lesson

Do not pull a huge analytical result into Python tuples merely because `.fetchall()` is convenient. Keep data in an analytical representation as long as practical, and convert only at a meaningful integration boundary.

---

## Question 8 — B08: Query a Parquet File Directly

### Difficulty
Basic

### Topics Covered
- Topic 06 — direct file querying, `read_parquet()`, projection, filter pushdown
- Topic 05 — DuckDB SQL

### Problem

You have `orders.parquet` with columns:

```text
order_id
customer_id
order_date
amount
status
notes
```

You need the total paid amount per customer for orders after January 1, 2026. You do not need `notes`.

### What You Need to Do

Write the DuckDB SQL query using direct Parquet access, and explain why selecting only needed columns is important.

### Solution

```sql
SELECT
    customer_id,
    SUM(amount) AS total_amount
FROM 'practice_data/orders.parquet'
WHERE status = 'PAID'
  AND order_date >= DATE '2026-01-01'
GROUP BY customer_id;
```

An equivalent reader-function form is:

```sql
SELECT
    customer_id,
    SUM(amount) AS total_amount
FROM read_parquet('practice_data/orders.parquet')
WHERE status = 'PAID'
  AND order_date >= DATE '2026-01-01'
GROUP BY customer_id;
```

### Additional consolidation

The same file-query family includes:

```sql
SELECT * FROM read_csv('orders.csv');
SELECT * FROM read_json('orders.json');
```

For CSV, know the role of `columns=`, `types=`, and `dateformat=` when inference is not reliable enough for a production contract. Multi-file reads can use globs or explicit file lists. Writing is covered through `COPY (...) TO ... (FORMAT PARQUET)` and `PARTITION_BY`, with compression chosen as a workload-dependent storage/I/O/CPU trade-off.
### How to Solve It

1. Identify the source relation: the Parquet file itself.
2. Identify required columns: `customer_id`, `amount`, `status`, `order_date`.
3. Apply predicates to reduce rows.
4. Aggregate by customer.
5. Do not use `SELECT *` because `notes` is irrelevant to the calculation.

### Why This Works

Parquet is columnar, so projection can reduce the amount of data that must be read or carried downstream. A selective predicate can also reduce processing. Exact bytes read depend on the file layout, statistics, predicate shape, and engine behaviour, so the performance benefit should be measured rather than assumed.

### Production Lesson

SQL expresses business logic, but file layout and projection determine much of the physical work. A production Data Engineer asks not only "Is the query correct?" but also "Which columns and rows will the engine actually need?"

---

## Question 9 — B09: Recognize Hive Partitioning

### Difficulty
Basic

### Topics Covered
- Topic 06 — Hive-style partitions, `hive_partitioning=true`, partition pruning, object storage

### Problem

Your data lake is organized as:

```text
lake/trips/
├── year=2025/
│   ├── month=01/
│   └── month=02/
└── year=2026/
    ├── month=01/
    └── month=02/
```

You need only February 2026. A developer proposes reading every file and filtering rows afterward.

### What You Need to Do

1. Explain the role of `hive_partitioning=true`.
2. Show a DuckDB reader example that understands the directory partition columns.
3. Explain conceptually how partition pruning can reduce work.
4. Distinguish partition pruning from Parquet row-group skipping.

### Solution

```sql
SELECT COUNT(*)
FROM read_parquet(
    'lake/trips/**/*.parquet',
    hive_partitioning = true
)
WHERE year = 2026
  AND month = 2;
```

Conceptually:

```text
query predicate
    ↓
partition values in directory layout
    ↓
select matching partitions
    ↓
read fewer files
```

Partition pruning happens at the partition/directory level. Row-group skipping occurs inside Parquet files and relies on row-group metadata/statistics.

### Remote-query extension

For object storage, distinguish:

```text
bucket → object/key → prefix → endpoint/credentials
```

from local filesystem semantics. DuckDB's `httpfs` supports remote access patterns, and `CREATE SECRET` separates credentials from query text. Never hard-code real access keys. At the advanced level, understand that remote Parquet access can use metadata/footer reads and HTTP range requests to fetch selected byte ranges/column chunks instead of necessarily downloading the entire file. Exact request patterns depend on implementation and environment.
### Parquet metadata investigation

For a deeper storage-level investigation, use:

```sql
SELECT * FROM parquet_schema('practice_data/orders.parquet');
SELECT * FROM parquet_metadata('practice_data/orders.parquet');
```

Use the schema function to inspect fields/types and the metadata function to investigate row-group/file statistics and related metadata. Exact output columns are version-sensitive; focus on the information the engine can use for pruning and diagnostics.
### How to Solve It

1. Identify `year` and `month` as directory-encoded partition values.
2. Tell DuckDB to interpret those directory names as partition columns.
3. Put predicates on those partition columns in the query.
4. Do not assume every predicate can prune partitions; the query must align with the partition metadata and reader capabilities.
5. Then consider row-group statistics as a second pruning opportunity.

### Why This Works

A query engine does not have to treat a lake directory as an opaque bag of bytes. Hive-style layout makes partition values explicit in the path. This can let the engine avoid opening or scanning partitions that cannot satisfy the query predicate.

This is different from row-group skipping, which uses metadata inside a Parquet file after the relevant file has been selected.

### Production Lesson

Partition design is part of the data contract. Choosing useful partition keys can reduce remote I/O dramatically, but over-partitioning can create a small-files problem. Partitioning should follow common query predicates and sensible cardinality.

---

## Question 10 — B10: What Does Zero-Copy Actually Mean?

### Difficulty
Basic

### Topics Covered
- Topic 07 and Topic 08 — zero-copy, Arrow interoperability, data movement, engine choice

### Problem

A developer converts a Polars DataFrame to Arrow:

```python
arrow_table = df.to_arrow()
```

and says, "The values are the same, so this proves zero-copy."

### What You Need to Do

1. Explain why the statement is not proof of zero-copy.
2. Define zero-copy precisely.
3. Distinguish zero-copy from minimal-copy.
4. State what you should verify after the conversion.

### Solution

The correct principle is:

```text
same values
≠
same underlying buffers
```

Zero-copy means the destination can use the existing underlying data buffers without copying the actual data. Metadata, wrappers, schemas, and small bookkeeping structures may still be allocated.

Minimal-copy means unnecessary full-data duplication is avoided, even when some conversion or allocation is required.

After conversion, verify:

```text
schema
→ dtypes
→ null semantics
→ chunk layout
→ memory behaviour
→ buffer sharing where it can be safely inspected
```

### Advanced interoperability extension

Also explain the distinction among:

```text
Arrow C Data Interface
Arrow C Stream / __arrow_c_stream__
PyCapsule-based Python interchange
Arrow RecordBatch streaming
```

Then distinguish these from cross-process/network mechanisms such as Arrow IPC, Arrow Flight, and ADBC. A stream of Arrow `RecordBatch` objects can reduce full-result materialization, but only if the consumer itself processes batches correctly.
### How to Solve It

1. Separate logical equality from physical representation.
2. Ask whether the destination representation is compatible with the source buffers.
3. Identify possible copy triggers such as type conversion, null representation changes, timezone handling, or chunk consolidation.
4. Measure and inspect rather than inferring from equal values.

### Why This Works

Two systems can produce identical values using different memory allocations. Conversely, an interoperable representation such as Arrow may allow data buffers to be reused for compatible layouts, while still constructing new metadata objects.

Therefore a conversion API names a transformation path; it does not automatically provide a universal zero-copy guarantee.

### Production Lesson

The engineering habit is:

```text
Convert → measure → inspect → verify
```

This prevents performance work from being based on assumptions about memory ownership. It also helps identify when an apparently harmless engine boundary becomes the dominant memory or latency cost.

---

# Part II — Moderate

## Question 11 — M01: Polars Join Explosion and Cardinality Validation

### Difficulty
Moderate

### Topics Covered
- Topic 02 — joins, cardinality, `validate`, join explosion, `.over()`

### Problem

You have:

```text
orders
order_id | customer_id | amount
---------|-------------|-------
1        | A           | 100
2        | A           | 200
3        | B           | 50

customers
customer_id | segment
------------|--------
A           | GOLD
A           | VIP
B           | SILVER
```

A developer performs a left join on `customer_id` and gets four rows instead of three. They expected exactly one customer record per order.

### What You Need to Do

1. Diagnose the problem.
2. Explain why the join multiplies rows.
3. Show how to validate the expected relationship.
4. State how inner, left, full, semi, anti, and cross joins differ at the conceptual level.
5. Explain when `join_asof()` is appropriate.
6. Give one semantically valid redesign if there should really be one customer row.

### Solution

The customer table violates the expected `many-to-one` relationship because customer `A` appears twice.

```text
orders:      many orders per customer
customers:   should be one row per customer
relationship: orders.customer_id → customers.customer_id = m:1
```

Use validation:

```python
import polars as pl

joined = orders.join(
    customers,
    on="customer_id",
    how="left",
    validate="m:1",
)
```

This should fail fast if the lookup side is not unique.

If the business rule says only one customer record is current, first create a semantically correct unique lookup table, then join it.

### Additional join coverage

Use the join family deliberately:

```text
inner → matching rows only
left  → preserve left rows
full  → preserve both sides
semi  → keep left rows with a match
anti  → keep left rows without a match
cross → Cartesian product
```

For time-aware lookup, use `join_asof()` when the business rule is "match to the relevant nearest/prior timestamp" and its ordering/time semantics are satisfied.
### How to Solve It

1. Count duplicate keys on the lookup side.
2. Identify the intended relationship.
3. Encode the relationship with `validate="m:1"`.
4. Only deduplicate if there is a business rule for choosing the surviving record.
5. Re-run the join and compare row counts.

### Why This Works

Joins do not merely append columns. If both sides contain multiple rows for the same key, a many-to-many relationship can create a multiplicative number of output rows. Cardinality validation is an explicit correctness guard against accidental join explosion.

### Production Lesson

Join cardinality is both a correctness and performance concern. A duplicate lookup row can inflate revenue, counts, memory, and runtime simultaneously. Treat expected cardinality as part of the data contract rather than as an assumption hidden in code.

---

## Question 12 — M02: Translate a Group-Wise Calculation to `.over()`

### Difficulty
Moderate

### Topics Covered
- Topic 02 — `.over()`, window expressions, `group_by`, pandas `transform`, SQL windows

### Problem

Given:

```text
customer | amount
---------|-------
A        | 100
A        | 300
B        | 50
```

you need a new column `customer_total` while retaining every original row.

### What You Need to Do

1. Write the Polars expression using `.over("customer")`.
2. Explain why `group_by().agg()` alone is not equivalent.
3. Relate `.over()` to pandas `transform` and SQL window functions.

### Solution

```python
import polars as pl

df = pl.DataFrame(
    {
        "customer": ["A", "A", "B"],
        "amount": [100, 300, 50],
    }
)

result = df.with_columns(
    pl.col("amount")
      .sum()
      .over("customer")
      .alias("customer_total")
)
```

Conceptual result:

```text
customer | amount | customer_total
---------|--------|---------------
A        | 100    | 400
A        | 300    | 400
B        | 50     | 50
```

### Related advanced Polars operations

The same DataFrame-expression model also covers `pivot`, `unpivot`, `explode`, `implode`, `group_by_dynamic()`, and rolling operations. They should be selected according to the required result shape and time semantics; do not treat them as interchangeable with a window expression.
### How to Solve It

`group_by().agg()` is designed to produce grouped output, usually with fewer rows. `.over()` applies a window-style calculation while preserving the original row shape.

The mental mapping is:

```text
Polars: pl.col("amount").sum().over("customer")
pandas: groupby("customer")["amount"].transform("sum")
SQL:    SUM(amount) OVER (PARTITION BY customer)
```

### Why This Works

A window expression computes over a partition but maps the result back to each participating row. That is fundamentally different from an aggregation that collapses rows to one result per group.

### Production Lesson

When requirements say "calculate a group statistic but keep every event row," think window expression, not aggregation. This prevents accidental row loss and makes the intent clearer to reviewers.

---

## Question 13 — M03: Read a Polars Plan and Find Pushdown Opportunities

### Difficulty
Moderate

### Topics Covered
- Topic 03 — `explain()`, predicate pushdown, projection pushdown, scan nodes
- Topic 06 — Parquet columnar file behaviour

### Problem

Suppose a lazy pipeline is:

```python
lf = (
    pl.scan_parquet("practice_data/orders/*.parquet")
    .with_columns((pl.col("amount") * 1.2).alias("gross"))
    .filter(pl.col("status") == "PAID")
    .select(["customer_id", "gross"])
)
```

A teammate says the engine must first read every column, calculate `gross` for every row, and only then filter.

### What You Need to Do

1. State which parts can often be optimized toward the scan.
2. Explain which source columns are actually needed for this query.
3. Show how to inspect the plan.
4. Explain why exact textual plan formatting should not be hard-coded into tests.

### Solution

Inspect the plan with:

```python
print(lf.explain())
```

The query needs these source columns:

```text
customer_id
amount
status
```

`gross` depends on `amount`, while the filter depends on `status`. The optimizer may push the compatible filter toward the scan and perform projection pushdown so irrelevant columns are not carried into the plan.

### Diagnostic extension

For a more complete investigation, use:

```python
print(lf.explain())
# where supported:
lf.show_graph()
profile = lf.profile()
```

The exact structure/rendering of these diagnostics is version-sensitive. For large pipelines, also separate correctness tests from optimizer expectations: test the result semantically, then use plan/profiling evidence to investigate performance. Lazy transformation functions should preferably accept and return `LazyFrame` so optimization can remain end-to-end.
### How to Solve It

1. Trace column dependencies backward from the final `select`.
2. Add dependencies introduced by computed expressions.
3. Add columns required for predicates.
4. Inspect `explain()` rather than trusting the source-code order.
5. Treat plan structure as diagnostic evidence, not as a fixed string contract.

### Why This Works

Lazy optimization sees the whole computation before execution. That makes transformations such as predicate pushdown and projection pushdown possible without changing the logical result.

The exact optimized plan can vary by Polars version and data source, so the important skill is recognizing the operator structure and reduced source requirements.

### Production Lesson

A correct query can still be inefficient. Query plans are the bridge between declarative code and actual work. Review the plan when I/O or runtime is surprising rather than guessing from the order in which methods appear in Python.

---

## Question 14 — M04: High-Cardinality Group-By in Streaming

### Difficulty
Moderate

### Topics Covered
- Topic 04 — streaming, state, high-cardinality aggregation, memory

### Problem

Two datasets each contain 10 billion events:

```text
Dataset A: 100 unique customer IDs
Dataset B: 500 million unique customer IDs
```

Both run the same grouped aggregation in streaming mode. A developer expects nearly identical memory usage because the input is streamed.

### What You Need to Do

Explain why this expectation is wrong. Describe what state the aggregation can retain and give three ways to reduce memory pressure without changing business semantics.

### Solution

Streaming controls how input is processed, but the aggregation still needs state for groups it has encountered.

Conceptually:

```text
batch 1 → update group state
batch 2 → update group state
batch 3 → update group state
...
```

Dataset B can require vastly more retained hash/group state because its key cardinality is much higher.

Ways to reduce legitimate pressure include:

1. filter early;
2. project only required columns;
3. pre-aggregate or partition work where that preserves the intended global semantics.

### How to Solve It

Separate two memory components:

```text
streaming input working set
        +
retained aggregation state
```

Ask how many unique groups must remain known until the computation is complete. The answer is very different for 100 groups versus hundreds of millions.

### Stateful-operator extension

Streaming is not a statement that every operator has bounded state. Global sorts, some windows, and pivots can require substantial retained information. This is why the same streaming pipeline can have very different memory profiles depending on query shape.
### Why This Works

Streaming does not mean one batch disappears before all state is needed. Stateful operators retain information across batches. High-cardinality group-bys therefore create memory growth proportional to the required aggregation state, not merely to batch size.

### Production Lesson

When a streaming query still approaches a memory limit, inspect stateful operators first. "Streaming is enabled" is not a sufficient memory guarantee. Capacity planning must include the number and size of retained groups.

---

## Question 15 — M05: Handle Schema Drift Across DuckDB Files

### Difficulty
Moderate

### Topics Covered
- Topic 06 — schema drift, `union_by_name`, `filename=true`, multi-file reads

### Problem

You have:

```text
2026-01.csv:
id,name,amount
1,Alice,100

2026-02.csv:
id,name,amount,currency
2,Bob,200,USD
```

A normal multi-file read reports a schema mismatch.

### What You Need to Do

Show a DuckDB query that aligns columns by name and preserves the originating filename. Then explain what happens to `currency` for the first file and what still needs validation.

### Solution

```sql
SELECT *
FROM read_csv(
    ['2026-01.csv', '2026-02.csv'],
    union_by_name = true,
    filename = true
);
```

The conceptual result is:

```text
id | name  | amount | currency | filename
---|-------|--------|----------|----------------
1  | Alice | 100    | NULL     | 2026-01.csv
2  | Bob   | 200    | USD      | 2026-02.csv
```

The missing `currency` field is filled with `NULL` where compatible with the union-by-name behaviour.

### How to Solve It

1. Identify this as schema evolution/drift across files.
2. Use `union_by_name=true` so matching is based on column names rather than only position.
3. Add `filename=true` for lineage/debugging.
4. Inspect resulting types because compatible column names can still have incompatible physical types.
5. Validate the output schema and null semantics.

### Lineage note

`filename=true` is not merely a convenience column. It can support lineage, reconciliation, quarantine, and investigation of which producer or file introduced an unexpected schema or value.
### Why This Works

A file collection is effectively a logical union of multiple physical relations. `union_by_name` aligns columns by name and provides a consistent logical shape when fields are absent from some inputs.

It does not make arbitrary incompatible types magically correct, and it does not eliminate the need for schema governance.

### Production Lesson

Schema drift should be observable, not silently normalized away. Source filenames are valuable evidence during reconciliation, producer debugging, and quarantine workflows. A resilient pipeline both handles expected evolution and detects unexpected changes.

---

## Question 16 — M06: Diagnose a Remote Query With Too Many Files

### Difficulty
Moderate

### Topics Covered
- Topic 06 — object storage, MinIO/S3, small-files problem, network cost, partitions

### Problem

A query against MinIO scans a dataset containing 50,000 small Parquet objects. The same logical data stored in fewer larger Parquet files is substantially easier to query.

### What You Need to Do

Explain why the file count matters even when the total logical data size is the same. Identify at least four measurements you would collect.

### Solution

Many small files can increase:

- object-storage request count;
- metadata/request overhead;
- network latency amplification;
- planning and file-discovery overhead;
- operational complexity.

Measure at least:

```text
files touched
partitions touched
HTTP/object-store request count where observable
bytes transferred/read
wall-clock time
cache state
```

### How to Solve It

Do not compare only total bytes. Decompose the remote cost model:

```text
metadata/request overhead
+
bytes transferred
+
latency
+
CPU/decompression
+
query work
```

Then compare the same query and same data on different file layouts.

### Measurement note

Remote performance should separate request count from bytes transferred and should document cold versus warm cache state. A larger file layout can reduce request overhead, but a poorly selected partition key can still cause excessive bytes to be scanned.
### Why This Works

Object storage is accessed through requests and APIs, not like a local disk with the same latency characteristics. A high object count can impose many small request/metadata costs even if the total data volume is unchanged.

### Production Lesson

File layout is part of query architecture. A fast SQL engine cannot fully compensate for a pathological remote layout. Treat file count, partition cardinality, and typical file size as production design variables.

---

## Question 17 — M07: Why pandas `object` Strings Increase Copy Risk

### Difficulty
Moderate

### Topics Covered
- Topic 07 — pandas object dtype, Arrow conversion, Arrow-backed pandas, zero-copy

### Problem

You convert a pandas DataFrame containing one million strings stored as `dtype=object` to Arrow. Memory spikes unexpectedly.

### What You Need to Do

1. Explain why object strings are a common copy/conversion risk.
2. Explain how Arrow-backed pandas can improve interoperability.
3. Give one way to create an Arrow-backed pandas DataFrame for an experiment.

### Solution

A pandas `object` column can contain Python object references rather than a compact contiguous Arrow-style string representation. Building an Arrow string array may therefore require scanning values and constructing Arrow-compatible offsets/data buffers.

For experimentation, pandas supports Arrow-backed dtypes through interfaces such as:

```python
import pandas as pd

arrow_df = pd.read_csv(
    "practice_data/data.csv",
    dtype_backend="pyarrow",
)
```

When converting Arrow to pandas, `types_mapper=pd.ArrowDtype` can also be used where appropriate.

### Related Arrow/pandas conversion path

When converting Arrow to pandas, the module also covers `table.to_pandas()` with `types_mapper=pd.ArrowDtype`. Compare this with a default pandas conversion when appropriate. The purpose is not to claim the Arrow-backed route is always zero-copy, but to investigate whether a more Arrow-compatible representation reduces conversion work on the actual dtype mix.
### How to Solve It

1. Inspect `df.dtypes` before conversion.
2. Identify `object` columns.
3. Recognize that Python-object representation is not the same as Arrow's compact columnar string buffers.
4. Compare with Arrow-backed pandas.
5. Measure conversion time and peak memory rather than assuming the Arrow-backed path is universally zero-copy.

### Why This Works

Zero-copy or low-copy interoperability requires compatible physical representations. Arrow-native string buffers and Python-object references are fundamentally different layouts.

Arrow-backed pandas can make the pandas side closer to Arrow's representation, reducing some conversion work, but it is not a universal zero-copy guarantee for every dtype and operation.

### Production Lesson

When a conversion boundary becomes expensive, inspect types before optimizing code around it. A single `object` column can undermine an otherwise efficient columnar pipeline. Treat dtype choices as part of performance engineering.

---

## Question 18 — M08: DuckDB Memory Limit and Temporary Storage

### Difficulty
Moderate

### Topics Covered
- Topic 05 — `memory_limit`, `threads`, `temp_directory`, out-of-core execution, spilling

### Problem

You are running a large DuckDB aggregation in a memory-constrained environment. The process should not consume the whole machine's memory, and out-of-core execution may need temporary disk space.

### What You Need to Do

Show how you would configure:

1. a DuckDB memory limit;
2. a thread limit;
3. a temporary directory.

Then explain why the temp directory must have sufficient capacity and why more threads can increase memory pressure.

### Solution

```sql
SET memory_limit = '8GB';
SET threads = 4;
SET temp_directory = '/tmp/duckdb-tmp';
```

The exact values must be chosen from the environment, not copied from this example.

Conceptually:

```text
memory limit
→ constrain DuckDB's managed memory budget

threads
→ control parallelism

temp_directory
→ location for temporary/spill data when needed
```

### How to Solve It

1. Identify the process/container memory budget.
2. Select a memory limit with operational headroom.
3. Use a thread count appropriate to the CPU and memory budget.
4. Put temporary storage on a location with enough free space and acceptable I/O performance.
5. Measure actual execution; do not assume a spill will always occur for a particular query.

### Broader DuckDB operations context

The same resource-managed DuckDB chapter covers transactions and ACID, the embedded concurrency model, the single-writer limitation, and extensions such as `httpfs`, `json`, `delta`, `iceberg`, and `spatial`. These are architectural constraints/capabilities, not reasons to treat DuckDB as a general OLTP server.
### Why This Works

Out-of-core execution can trade some disk I/O for lower memory pressure. Parallel execution can improve throughput but may create more simultaneous work and temporary state.

### Production Lesson

Resource controls are part of deployment architecture, not just troubleshooting. A query that succeeds on an unrestricted laptop can fail in a container if memory and temporary-disk budgets are different.

---

## Question 19 — M09: Cross-Engine Correctness Check

### Difficulty
Moderate

### Topics Covered
- Topic 07 and Topic 08 — pandas/Polars/DuckDB/Arrow interoperability, schema fidelity, correctness reference

### Problem

You need the same customer-level revenue result in pandas, Polars, and DuckDB. The result must be considered equivalent only if values and important semantics match.

### What You Need to Do

Design a correctness checklist that must be applied after each engine produces its result. Include at least six checks and explain why each matters.

### Solution

A robust checklist is:

```text
1. row count
2. column names
3. schema / dtypes
4. null counts and null semantics
5. aggregate values
6. timestamp semantics/time zones where applicable
7. Decimal precision/scale where applicable
8. representative value equality
9. deterministic ordering before row-by-row comparison when order is unspecified
```

A small pandas implementation can serve as a correctness reference when appropriate, but it is not automatically the canonical reference for every workload.

### Interoperability coverage

The conversion family to recognize includes:

```text
pl.from_arrow()
df.to_arrow()
pl.from_pandas()
df.to_pandas()
pa.Table.from_pandas()
table.to_pandas()
DuckDB .to_arrow_table() / .to_arrow_reader()
DuckDB .pl()
DuckDB .df()
```

Where a conversion is large, also evaluate whether a DuckDB Arrow reader / RecordBatch path is more appropriate than full materialization.
### How to Solve It

Start with logical equivalence, then inspect representation:

```text
logical result
→ row/column structure
→ types
→ missingness
→ domain-specific numeric/time semantics
```

Do not stop after comparing printed values.

### Why This Works

Engine boundaries can preserve values while changing physical types or semantics. For example, a timestamp may retain the same visible instant but lose timezone information, or a Decimal can become another numeric representation.

Correctness validation must therefore include both data values and relevant schema semantics.

### Production Lesson

Performance results are meaningless when the implementations are not semantically equivalent. In cross-engine evaluation, correctness is the gate that makes a performance comparison trustworthy.

---

## Question 20 — M10: Design a Fair Small Benchmark

### Difficulty
Moderate

### Topics Covered
- Topic 08 — fair benchmarking, same format, repeated runs, cold/warm cache, runtime, peak memory

### Problem

A team wants to compare pandas, Polars, and DuckDB on a 5 GB analytical workload. One engineer proposes CSV for pandas, Parquet for Polars, and a database table for DuckDB.

### What You Need to Do

Redesign the benchmark methodology. State what must remain constant, what must be measured, and how you would handle cold/warm runs.

### Solution

Use:

```text
same logical dataset
same physical file format where file-based comparison is intended
same query semantics
same hardware
same software environment
same relevant thread/configuration assumptions
same correctness criteria
```

Measure:

```text
wall-clock time
peak memory
result correctness
and, when relevant, bytes/files read
```

Use repeated runs and document cache state. A practical structure is:

```text
cold: run 1, run 2, run 3
warm: run 1, run 2, run 3
```

### Benchmark extension

Use TPC-H-style query ideas only as standardized workload patterns, not as a universal prediction of production performance. Explicitly record software versions, CPU/RAM, thread configuration, file format, cache state, and correctness checks, and challenge vendor-produced rankings by reproducing important measurements independently.
### How to Solve It

1. Fix the input and schema.
2. Define six or another small set of representative queries.
3. Implement semantically equivalent versions.
4. Keep file format identical for file-based comparison.
5. Run on the same machine and environment.
6. Record software versions and configuration.
7. Measure both runtime and peak memory.
8. Compare results for correctness before interpreting speed.

### Why This Works

Changing file format or cache state changes the workload itself. A benchmark then measures several uncontrolled variables at once rather than engine behaviour.

A fair benchmark is a controlled experiment. It does not need to make every system identical internally, but it must keep the external workload and measurement conditions comparable.

### Production Lesson

A benchmark should be reproducible by another engineer. If the benchmark cannot explain what data was processed, under what conditions, and how correctness was checked, it is weak architectural evidence.

---

# Part III — Hard

## Question 21 — H01: Safe vs Unsafe Arrow Casting

### Difficulty
Hard

### Topics Covered
- Topic 01 — Arrow `cast`, safe/unsafe conversion, numeric types, schema

### Problem

You have an Arrow array:

```python
import pyarrow as pa

arr = pa.array([1, 2, 300], type=pa.int64())
```

A downstream system expects `int8`.

### What You Need to Do

1. Attempt a safe cast to `int8`.
2. Explain why a safe cast must reject values that cannot be represented correctly.
3. Explain the danger of unsafe casting.
4. State what should happen in a production pipeline before narrowing a numeric type.

### Solution

```python
import pyarrow as pa

arr = pa.array([1, 2, 300], type=pa.int64())

try:
    narrowed = arr.cast(pa.int8(), safe=True)
    print(narrowed)
except (pa.ArrowInvalid, pa.ArrowNotImplementedError) as exc:
    print("Safe cast rejected:", exc)
```

Because `300` is not representable as signed 8-bit integer, a safe cast should reject the conversion rather than silently corrupt the value.

An unsafe cast may allow truncation/overflow semantics depending on the conversion; that is why it must be used only when the data contract proves the values are safe.

### Additional Arrow reasoning

For a complete schema audit, distinguish `Field`, `Schema`, and `DataType`, and explain how explicit schema construction can prevent inference surprises. For categorical-like repeated strings, explain dictionary encoding and why it can help when values repeat but add overhead when values are mostly unique. For transformations, use `pyarrow.compute` rather than converting to pandas simply to filter, take, sort, or aggregate an Arrow array.
### How to Solve It

1. Check the source range.
2. Compare it with the destination type's representable range.
3. Prefer safe casting for production schema narrowing.
4. If narrowing is required, validate or normalize the data first.
5. Treat any unsafe cast as an explicit, documented contract decision.

### Why This Works

Type conversion is a semantic operation. A smaller integer type has a smaller representable range. Safe casting turns a potentially silent correctness problem into an explicit failure.

### Production Lesson

A type cast that makes a schema smaller can make memory usage better, but correctness comes first. In production Data Engineering, schema optimization must be backed by observed or validated domain ranges, not optimism.

---

## Question 22 — H02: Remove a Polars Python UDF From a Lazy Pipeline

### Difficulty
Hard

### Topics Covered
- Topic 02/03 — `map_elements()`, native expressions, lazy optimization, pushdown blockers

### Problem

The following pipeline is used on a large Parquet dataset:

```python
lf = (
    pl.scan_parquet("orders/*.parquet")
    .with_columns(
        pl.col("amount").map_elements(lambda x: x * 1.18).alias("gross")
    )
    .filter(pl.col("status") == "PAID")
    .select(["customer_id", "gross"])
)
```

The query is slow, and the developer wants to "make Polars use more threads."

### What You Need to Do

1. Identify the main design issue.
2. Replace the Python UDF with a native expression.
3. Explain why the native expression gives the optimizer more opportunities.
4. State what you would inspect with `explain()` after the change.

### Solution

Replace the UDF with:

```python
import polars as pl

lf = (
    pl.scan_parquet("practice_data/orders/*.parquet")
    .with_columns(
        (pl.col("amount") * 1.18).alias("gross")
    )
    .filter(pl.col("status") == "PAID")
    .select(["customer_id", "gross"])
)

print(lf.explain())
```

The native expression stays inside Polars' expression engine instead of calling Python once per element.

### How to Solve It

1. Ask whether the operation can be expressed with built-in Polars expressions.
2. Replace `map_elements()` with arithmetic or another native namespace operation.
3. Inspect the optimized plan.
4. Confirm the output matches the original implementation on a small dataset.
5. Only then benchmark at scale.

### Broader optimization lesson

The optimizer can also benefit from common subplan elimination, common subexpression elimination, simplification, slice pushdown, and source-level pruning. These optimizations are conditional; a Python UDF or eager conversion can make the logical boundaries less visible to the optimizer.
### Why This Works

Native expressions are visible to the optimizer and can execute in the engine's optimized execution model. A Python UDF introduces a Python boundary that can reduce optimization opportunities and create Python-level overhead.

The right lesson is not "UDFs are always forbidden." It is:

```text
Use native expressions when the transformation can be expressed natively.
```

### Production Lesson

Increasing thread count is not a substitute for removing an inefficient execution boundary. First fix the query shape and execution model, then tune resources based on evidence.

---

## Question 23 — H03: Redesign a Larger-Than-RAM Polars Pipeline

### Difficulty
Hard

### Topics Covered
- Topic 03/04/06 — lazy scans, pushdown, streaming, sink, larger-than-RAM processing, Parquet

### Problem

A 100 GB Parquet dataset must be processed on a 16 GB machine. The current pipeline is conceptually:

```text
read everything
 ↓
keep every column
 ↓
sort globally
 ↓
join a large lookup
 ↓
collect full result
```

### What You Need to Do

Redesign the pipeline for a streaming-friendly approach where the business semantics allow it. Explain which operations are likely to dominate memory and where you would validate correctness.

### Solution

A better conceptual design is:

```text
scan_parquet
    ↓
early filter
    ↓
projection to required columns
    ↓
pre-aggregate where semantically valid
    ↓
careful join / reduce retained join state
    ↓
collect(engine="streaming") when the final result is small
or sink_parquet() when the output is large
```

For example:

```python
import polars as pl

lf = (
    pl.scan_parquet("silver/*.parquet")
    .filter(pl.col("event_date") >= pl.date(2026, 1, 1))
    .select(["customer_id", "event_date", "amount", "zone_id"])
    # Add only semantically valid transformations here.
)

lf.sink_parquet("gold/result.parquet")
```

### Required resource discipline

Run the final candidate inside the actual memory-constrained environment when practical. Record:

```bash
/usr/bin/time -v python pipeline.py
```

and capture maximum resident set size. If the workload is containerized, document the container limit rather than only host RAM. Tune `POLARS_MAX_THREADS` only after measuring the CPU/memory trade-off.
### How to Solve It

1. Remove unnecessary rows before expensive operations.
2. Remove unnecessary columns before expensive operations.
3. Challenge the global sort: is global order truly required?
4. Challenge the join: can the lookup be reduced or deduplicated first?
5. Preserve global semantics when partitioning or pre-aggregating.
6. Avoid collecting a huge final output.
7. Measure peak memory and runtime before and after.
8. Compare results using schema, row counts, and values.

### Why This Works

Streaming reduces input materialization, but it cannot make inherently state-heavy operations free. The goal is to control the working set and retained state:

```text
total input size
≠
active working set
```

### Production Lesson

The most effective larger-than-RAM redesign often starts before the streaming call itself. Push less data into expensive operators. Streaming is an execution capability; good pipeline design determines how much state the engine must retain.

---

## Question 24 — H04: Diagnose Memory Growth From a Group-By and Join

### Difficulty
Hard

### Topics Covered
- Topic 04/05 — aggregation state, high-cardinality joins, build-side reasoning, DuckDB/Polars memory

### Problem

A workload has:

```text
fact table: 400 GB
lookup table: 20 GB
```

The pipeline filters the fact table only after joining, then groups by a very high-cardinality key. Memory usage is much higher than expected.

### What You Need to Do

Identify at least five independent contributors to memory pressure and propose a redesign sequence that preserves semantics.

### Solution

Likely contributors include:

1. a large retained join/build side;
2. joining rows that could have been filtered earlier;
3. carrying unnecessary columns into the join;
4. a high-cardinality aggregation state;
5. large intermediate results from the join;
6. parallelism increasing simultaneous working state;
7. result materialization.

A redesign sequence is:

```text
filter fact early
    ↓
project fact early
    ↓
reduce/deduplicate lookup semantically
    ↓
project lookup to join-required columns + outputs
    ↓
join
    ↓
pre-aggregate where valid
    ↓
stream/sink result
```

### Semantic guardrail

If you pre-aggregate, first prove that the aggregation is associative/mergeable for the required business result and that reducing dimensionality does not remove columns needed by later joins. Optimization that changes grain can silently change business meaning.
### How to Solve It

Treat each operator as a possible working-set boundary. Ask:

```text
How many rows enter?
How wide are they?
What state must be retained?
Which side of the join is retained/build state?
How many unique groups are created?
```

Then measure after each redesign.

### Why This Works

Memory is shaped by intermediate state, not only the source file size. Reducing rows and columns before a join lowers the amount of data that the join must hold and process. Reducing the number of groups reduces aggregation state when the business semantics permit it.

### Production Lesson

Senior-level memory diagnosis is operator-by-operator reasoning. Saying "the dataset is 400 GB" is not enough. You need to know which operator creates the peak and why its state grows.

---

## Question 25 — H05: Read a DuckDB `EXPLAIN ANALYZE` Result Conceptually

### Difficulty
Hard

### Topics Covered
- Topic 05 — `EXPLAIN`, `EXPLAIN ANALYZE`, physical operators, timings, bottleneck investigation

### Problem

A query is:

```sql
SELECT
    c.segment,
    SUM(o.amount) AS revenue
FROM orders o
JOIN customers c
  ON o.customer_id = c.customer_id
WHERE o.order_date >= DATE '2026-01-01'
GROUP BY c.segment;
```

A hypothetical `EXPLAIN ANALYZE` observation says the join consumes most of the operator time, while the scan and final aggregation are comparatively small.

### What You Need to Do

Explain:

1. why `EXPLAIN` and `EXPLAIN ANALYZE` answer different questions;
2. what the join timing suggests;
3. what you would investigate next;
4. why you must not claim a query is optimized just because the result is correct.

### Solution

Conceptually:

```text
EXPLAIN
= planned execution

EXPLAIN ANALYZE
= actual execution + runtime information
```

If the join dominates, investigate:

- join input sizes after filtering;
- join key cardinality and duplicates;
- whether unnecessary columns are carried;
- whether the lookup side is larger than expected;
- whether predicate placement or query structure can reduce join input;
- memory pressure and temporary work.

Then re-run `EXPLAIN ANALYZE` after a semantically equivalent change.

### Plan-reading discipline

Use `EXPLAIN` for the planned work and `EXPLAIN ANALYZE` for observed execution. The module's broader plan vocabulary includes scan, filter, projection, join, aggregate, and sort. Treat exact textual plan output as version-sensitive evidence rather than a fixed API contract.
### How to Solve It

1. Read the operator tree from sources toward the result.
2. Identify actual row counts and timings where shown.
3. Locate the dominant operator.
4. Identify upstream factors feeding that operator.
5. Change one meaningful thing.
6. Validate results.
7. Measure again.

### Why This Works

A SQL query describes intent, not cost. The physical plan determines the actual work. `EXPLAIN ANALYZE` connects the logical query to observed runtime behaviour.

### Production Lesson

Performance investigations should be evidence-driven. Avoid rewriting queries merely because a pattern "looks slow." First identify the actual bottleneck and measure the effect of the change.

---

## Question 26 — H06: Debug a Slow MinIO Query

### Difficulty
Hard

### Topics Covered
- Topic 06 — S3-compatible storage, MinIO, partitions, pushdown, request counts, cache

### Problem

A query against local Parquet takes a small amount of time, but the same query against MinIO is unexpectedly slow. The logical data is identical.

### What You Need to Do

Create a diagnosis plan that investigates, in order:

- query selectivity;
- partitions/files touched;
- projection;
- bytes transferred;
- request count;
- cache state;
- file sizes;
- credentials/endpoints only when access itself is suspect.

### Solution

A practical sequence is:

```text
1. Confirm the query and data are the same.
2. Inspect partition predicates.
3. Inspect whether SELECT * is being used.
4. Count files/partitions touched.
5. Measure bytes transferred where possible.
6. Inspect MinIO request logs/metrics.
7. Compare small-file and larger-file layouts.
8. Record cold vs warm state.
9. Verify endpoint/credentials if authentication or connectivity is involved.
```

The key hypothesis is not simply "MinIO is slower." Remote cost includes request latency, bytes transferred, object count, network conditions, and cache effects.

### Security branch

If the failure is authentication rather than performance, inspect the `httpfs` configuration, endpoint, credential chain/managed identity, and `CREATE SECRET` setup. Never move a real access key into a SQL file just to make the benchmark work.
### How to Solve It

Start with the biggest avoidable data movement:

```text
Can fewer partitions be selected?
Can fewer columns be read?
Can more row groups be skipped?
Can file count be reduced?
```

Then separate engine work from transport work.

### Why This Works

A local SSD and object storage have different cost structures. The same query plan can have very different wall-clock behaviour because remote metadata and data access introduce network latency and request overhead.

### Production Lesson

Never benchmark a remote lake solely from a local-disk benchmark. Data location is a workload characteristic. A remote performance regression may be a file-layout or network problem rather than an engine problem.

---

## Question 27 — H07: Design a Zero-Copy Verification Experiment

### Difficulty
Hard

### Topics Covered
- Topic 07 — buffer sharing, chunks, Arrow/Polars interop, memory measurement

### Problem

You need to investigate whether an Arrow → Polars conversion reuses underlying buffers. You are given one compatible numeric array and one multi-chunk string column.

### What You Need to Do

Design an experiment that distinguishes:

```text
likely shared
potentially shared
likely copied
requires verification
```

Your experiment must measure time, peak memory, schema, and chunk behaviour.

### Solution

Use two cases:

```text
Case A: simple fixed-width numeric Arrow array
Case B: multi-chunk string ChunkedArray
```

Then:

```python
import pyarrow as pa
import polars as pl

numeric = pa.array([1, 2, 3], type=pa.int64())
text = pa.chunked_array([
    pa.array(["a", "b"]),
    pa.array(["c"]),
])

table = pa.table({"numeric": numeric, "text": text})

df = pl.from_arrow(table, rechunk=False)

print(table.schema)
print(df.schema)
print("Arrow text chunks:", table.column("text").num_chunks)
```

Classify the result only after measurement and safe inspection. Do not infer zero-copy from value equality alone.

### Interface-awareness extension

At architecture level, explain that common low-level interchange mechanisms such as the Arrow C Data Interface and C Stream interface let libraries exchange columnar data descriptions/batches without implementing custom pairwise converters. This supports the broader goal of fewer conversion layers, but it does not remove type incompatibility or metadata work.
### How to Solve It

1. Record source schema and chunk counts.
2. Measure process memory before conversion.
3. Convert with `rechunk=False` for an experiment focused on preserving chunk layout.
4. Measure after conversion.
5. Inspect destination chunk behaviour.
6. Where low-level buffer inspection is appropriate, compare underlying addresses/layouts.
7. Repeat with types known to require conversions.

### Why This Works

A fixed-width numeric array has a relatively direct columnar representation, while multi-chunk strings combine variable-width buffers and chunk structure. A consumer may preserve chunks or consolidate them depending on the conversion path and parameters.

The experiment separates prediction from proof.

### Production Lesson

"Likely zero-copy" is a hypothesis, not a production guarantee. When memory cost matters, verify with a reproducible experiment under the actual library versions and data shapes you deploy.

---

## Question 28 — H08: Stream a DuckDB Result as Arrow RecordBatches

### Difficulty
Hard

### Topics Covered
- Topic 05/07 — DuckDB Arrow interop, `RecordBatchReader`, incremental consumption, avoiding full materialization

### Problem

A DuckDB query returns a very large result. Converting the entire result to pandas would create an unnecessarily large in-memory object. The downstream consumer can process Arrow `RecordBatch` objects incrementally.

### What You Need to Do

Write the current DuckDB pattern for producing an Arrow reader in batches and show a loop that consumes each batch without collecting the entire result into pandas.

### Solution

```python
import duckdb

relation = duckdb.sql(
    """
    SELECT
        i AS id,
        i * 2 AS value
    FROM range(1_000_000) AS t(i)
    """
)

reader = relation.to_arrow_reader(batch_size=100_000)

for batch in reader:
    # Batch-aware downstream processing.
    print(batch.num_rows)
```

The current topic material treats `to_arrow_reader()` as the incremental Arrow path and notes that older batch-fetching APIs may be deprecated in favour of it.

### Batch correctness requirement

If the consumer performs a running aggregation, demonstrate that state crosses batch boundaries. For example:

```text
batch 1: customer A → 100
batch 2: customer A → 200
```

The correct global total is 300; calculating each batch independently and forgetting to merge state is incorrect.
### How to Solve It

1. Keep the result in DuckDB as long as practical.
2. Request an Arrow reader rather than a giant DataFrame.
3. Process one `RecordBatch` at a time.
4. Ensure downstream aggregation/state is correct across batches.
5. Do not accumulate all batches into a Python list if the objective is bounded working memory.

### Why This Works

A `RecordBatchReader` exposes the result incrementally. This changes the working-set shape from:

```text
entire result in memory
```

to:

```text
one batch + downstream state
```

The downstream logic still needs correct state handling. Streaming is not correctness-free.

### Production Lesson

For very large results, interoperability design includes the consumption pattern, not just the data format. A perfectly efficient Arrow boundary can be defeated by a consumer that immediately materializes every batch.

---

## Question 29 — H09: Reconcile a Type Change Across Engines

### Difficulty
Hard

### Topics Covered
- Topic 01/02/07 — Arrow/Polars/pandas/DuckDB types, Decimal, timezone, schema fidelity

### Problem

A financial pipeline has this intended schema:

```text
order_id: string
amount: decimal128(12,2)
created_at: timestamp(us, UTC)
```

After crossing engine boundaries, the destination shows:

```text
order_id: string
amount: double
created_at: timestamp(us) without timezone
```

### What You Need to Do

1. Identify the two semantic risks.
2. Explain why logical values may still look correct on a small sample.
3. Describe what validation should be performed before production approval.
4. Propose a redesign principle.

### Solution

The risks are:

```text
amount: Decimal → floating point
→ precision/scale semantics may change

created_at: timezone-aware → timezone-naive
→ timezone semantics may be lost
```

Validation should include:

- exact schema/type checks;
- Decimal precision and scale checks;
- timezone metadata/semantic checks;
- representative value comparisons;
- null handling;
- boundary-specific conversion tests.

The redesign principle is to choose an interoperable representation and minimize unnecessary conversions. Do not accept a type change just because a small sample prints the same visible values.

### Additional type coverage

Also consider nullable integers, pandas categoricals, Arrow dictionaries, Polars `Enum`, nested `List` and `Struct`, and chunked columns. These may have logically similar meanings across engines while differing in physical representation. Record both source and destination types and treat unexpected changes as investigation items.
### How to Solve It

1. Compare source and destination schema programmatically.
2. Classify changes as physical-only or semantic.
3. Treat Decimal and timezone changes as semantic until proven otherwise.
4. Test boundary conversions on representative and edge-case data.
5. Record the chosen representation as part of the data contract.

### Why This Works

Interoperability is not only about values. Data types encode business semantics such as money precision and temporal context. A destination that uses a different physical type can silently alter those semantics even when simple examples appear unchanged.

### Production Lesson

Schema fidelity is part of correctness. For finance, timestamps, identifiers, and nested data, an engine boundary should be reviewed like a schema migration, not like a cosmetic format conversion.

---

## Question 30 — H10: Design the Six-Query Multi-Engine Benchmark

### Difficulty
Hard

### Topics Covered
- Topic 08 plus Topics 02–07 — benchmarking, correctness, pandas/Polars/DuckDB, lazy/streaming, interoperability

### Problem

Your team wants to compare pandas, Polars lazy/streaming, and DuckDB using six realistic workloads:

1. filter + aggregate;
2. top-N per group;
3. large join;
4. window function;
5. deduplication;
6. time-series resampling.

### What You Need to Do

Design the benchmark protocol for three data sizes:

```text
small
approximately RAM-scale
larger-than-RAM
```

Include cold/warm conditions, repetitions, correctness, runtime, and peak memory.

### Solution

The protocol should be:

```text
Same dataset and schema
        ↓
Same semantics in each engine
        ↓
Correctness validation on small input
        ↓
Three data sizes
        ↓
Cold and warm conditions
        ↓
Three repetitions per condition
        ↓
Runtime + peak memory
        ↓
I/O/conversion measurements when relevant
        ↓
Interpret results against requirements
```

Use a result table such as:

```text
| Engine | Query | Data Size | Cache | Run | Runtime | Peak Memory | Correct? |
|---|---|---|---|---|---:|---:|---|
```

### Statistical discipline

After three repetitions, record the individual observations rather than only the fastest run. Inspect variability/outliers and use median/mean appropriately. Document cold/warm semantics, avoid mixing setup time inconsistently, and never turn one workload into a universal ranking.
### How to Solve It

1. Define semantics for each query.
2. Write a trusted small-data reference implementation.
3. Keep physical input format consistent for the main file benchmark.
4. Implement each query in each engine.
5. Validate outputs before scaling.
6. Measure using the same machine/configuration.
7. Separate cold and warm conditions explicitly.
8. Repeat measurements and preserve raw evidence.
9. Analyze memory and correctness alongside time.

### Why This Works

A benchmark is an experiment. Varying engine plus file format plus cache state plus data size at once makes the result ambiguous.

The larger-than-RAM test is especially valuable because it reveals execution and resource boundaries that a small in-memory test cannot expose.

### Production Lesson

Benchmark design is itself a senior engineering skill. The goal is not to generate the fastest chart; it is to generate evidence that survives review and can support an architecture decision.

---

# Part IV — Advanced

## Question 31 — A01: Design a 100 GB MinIO → Polars Production Pipeline

### Difficulty
Advanced

### Topics Covered
- Topics 03, 04, 06 — lazy scanning, Hive partitions, pushdown, streaming, object storage, memory limits, sinks

### Problem

A 100 GB trip dataset lives in MinIO as Hive-partitioned Parquet:

```text
s3://lake/trips/year=2026/month=03/*.parquet
```

A nightly job runs in a 16 GB container and must produce daily metrics. The job currently downloads all files, keeps every column, sorts globally, and writes one huge local CSV.

### What You Need to Do

Design an execution architecture and justify every major step. Include failure/measurement points and explain what would make you abandon a single-node Polars solution.

### Solution

A suitable architecture hypothesis is:

```text
MinIO / object storage
      ↓
Hive-aware lazy scan
      ↓
partition pruning for relevant dates
      ↓
predicate pushdown
      ↓
projection pushdown
      ↓
semantically valid pre-aggregation
      ↓
streaming execution
      ↓
sink Parquet
      ↓
partitioned gold dataset
```

Example shape:

```python
import polars as pl

lf = (
    pl.scan_parquet(
        "s3://lake/trips/**/*.parquet",
        hive_partitioning=True,
    )
    .filter(
        (pl.col("year") == 2026)
        & (pl.col("month") == 3)
    )
    .select([
        "trip_date",
        "zone_id",
        "fare",
    ])
)

# Use the current supported remote-storage configuration for the environment.
# Keep the final result streamed to an appropriate sink where supported.
lf.sink_parquet("gold/trip_metrics.parquet")
```

The exact remote-storage options are version- and environment-sensitive and must be verified in the deployed Polars version.

### Architecture extension

For remote access, document the storage endpoint and credential source separately from query logic. For output, prefer an analytical format such as Parquet and partition only by keys that support real downstream pruning without producing pathological small-file counts.
### How to Solve It

1. Reduce partitions first.
2. Reduce rows with predicates.
3. Reduce width with projection.
4. Remove the global sort unless business semantics require globally ordered output.
5. Reduce join/aggregation state where semantically valid.
6. Stream the execution.
7. Sink the large result instead of collecting it.
8. Measure container peak memory, runtime, bytes/request behaviour, and output correctness.
9. Reconsider the architecture if stateful operations or SLA requirements exceed the machine's practical capacity.

### Why This Works

The design reduces the working set before expensive operators. It also avoids the final full-result materialization that can undermine streaming.

But 100 GB by itself does not prove the workload must be distributed. The actual boundary depends on query shape, state, storage, memory, CPU, and SLA.

### Production Lesson

A production pipeline should be designed around the smallest useful working set and an explicit resource budget. If a single node remains reliable and meets the SLA, distributed execution may add unnecessary complexity; if it does not, escalation should be evidence-driven.

---

## Question 32 — A02: Design a Deliberate DuckDB → Arrow → Polars → pandas Pipeline

### Difficulty
Advanced

### Topics Covered
- Topics 05, 07, 08 — DuckDB, Arrow interchange, Polars, pandas edge dependency, boundary minimization

### Problem

A pipeline must:

1. read Parquet and perform SQL filtering/aggregation;
2. perform several complex expression-based DataFrame transformations;
3. call one library that accepts only pandas;
4. avoid converting the large dataset back and forth repeatedly.

### What You Need to Do

Design the pipeline and explain why each engine boundary exists. State where you would prefer full materialization and where you would prefer an incremental boundary.

### Solution

A deliberate architecture is:

```text
Parquet
  ↓
DuckDB
  ↓ SQL-heavy filtering / aggregation
Arrow
  ↓
Polars
  ↓ expression-heavy transformation
small final result
  ↓
pandas-only library
```

The key rule is to convert to pandas near the edge only after reducing the data to the size required by that library.

For a very large DuckDB result, the Arrow boundary may use a reader/RecordBatch path if the Polars-side processing can consume batches appropriately. For a small result, a table-based Arrow conversion is simpler.

### Boundary evidence

At each boundary, record:

```text
reason for boundary
input schema
output schema
likely copy risk
measured conversion time
measured peak memory
chunk behaviour
```

If Narwhals is used for shared DataFrame utility code, understand `nw.from_native()` / `.to_native()` conceptually and still validate backend-specific semantics.
### How to Solve It

1. Identify the natural abstraction for each stage.
2. Keep SQL-heavy work in DuckDB.
3. Cross to Arrow because it is a common columnar interchange layer.
4. Keep DataFrame-heavy work in Polars.
5. Convert to pandas once for the pandas-only dependency.
6. Record schema and measure memory at each boundary.
7. Avoid returning from pandas to Polars unless there is a real requirement.

### Why This Works

Engine mixing is useful when it is intentional. The goal is not "one engine everywhere" but "few, justified boundaries." Arrow helps reduce coupling between analytical components, while pandas can remain an edge integration dependency.

### Production Lesson

A good architecture can contain multiple engines without becoming an engine maze. Every boundary should have a business or technical reason, a known schema, and an observable cost.

---

## Question 33 — A03: Decide Whether a 5 TB Daily Workload Has Crossed the Single-Node Boundary

### Difficulty
Advanced

### Topics Covered
- Topic 08 — single-node limits, distributed systems, operational requirements
- Topics 04–06 — streaming, joins, object storage, resource state

### Problem

A team processes 5 TB of data daily. One proposal says, "5 TB means Spark immediately." Another says, "Polars can stream, so one machine is always enough."

### What You Need to Do

Evaluate the decision without choosing by dataset size alone. Build a workload and requirements checklist and identify evidence that would justify moving to a distributed engine or managed warehouse.

### Solution

Evaluate:

```text
data size
working-set characteristics
join cardinality
aggregation state
sort/window requirements
available RAM/CPU/disk
object-storage throughput
SLA/SLO
concurrency
failure/retry requirements
cost
team operations
future growth
```

Evidence for escalation could include:

- reliable peak memory exceeds available single-node resources;
- required execution time exceeds the SLA even after query/file-layout optimization;
- join/state size cannot be kept within one machine's practical capacity;
- workload concurrency or isolation requirements exceed the single-node model;
- operational requirements demand cluster-level fault isolation or shared compute.

### Candidate architecture awareness

The distributed candidates covered by the module include Spark, Dask, Ray Data, and cloud warehouses. The point is not to learn their APIs here; it is to evaluate why their architecture might become justified and what operational complexity they introduce. GPU execution is a separate axis and should be considered only when the workload is actually GPU-suitable.
### How to Solve It

Start with a representative benchmark, not the headline dataset size. Determine whether the workload is actually streamable and whether its retained state is manageable.

Then compare the cost and complexity of a larger single node with a distributed design.

### Why This Works

Single-node does not mean "small data only," and distributed does not mean "automatically better." Modern columnar engines can handle substantial workloads on one machine, while some workloads exceed that boundary because of state, SLA, concurrency, or operational needs rather than raw storage volume alone.

### Production Lesson

Architecture boundaries are empirical. Senior engineers defend them using measured capacity, not slogans such as "X TB means Spark."

---

## Question 34 — A04: Write an Evidence-Based Engine ADR

### Difficulty
Advanced

### Topics Covered
- Topic 08 — Architecture Decision Records, workload characterization, measurements, consequences, revisit conditions

### Problem

A team needs a default strategy for single-node analytical pipelines. Candidates are pandas, Polars, DuckDB, and a deliberate hybrid. The team wants an Architecture Decision Record rather than an informal preference.

### What You Need to Do

Write the structure and content requirements of the ADR. Do not choose a universal winner. The ADR must be based on a specified workload and measured evidence.

### Solution

Use this structure:

```text
Context
Problem / requirements
Candidate options
Benchmark methodology
Measurements
Decision
Consequences
Risks
Revisit conditions
```

For example:

```text
Context:
50 GB Parquet workload in a 16 GB container; SQL-heavy staging plus DataFrame transformations.

Requirements:
10-minute batch SLA, deterministic results, maintainable CI deployment.

Options:
A. pandas
B. Polars
C. DuckDB
D. DuckDB + Arrow + Polars hybrid

Measurements:
Representative queries, same data/format, cold/warm runs, three repetitions,
runtime + peak memory + correctness.

Decision:
Selected based on measured fit to requirements.

Consequences:
Document ecosystem gains, boundary costs, operational complexity, and limitations.

Revisit:
Re-evaluate if memory approaches the measured limit, SLA changes, concurrency rises,
or workload grows beyond tested capacity.
```

### ADR quality check

A strong ADR does not hide uncertainty. It records what was measured, which assumptions were not tested, the consequences of the decision, and what future observation would trigger re-evaluation.
### How to Solve It

1. Describe the actual operating context.
2. State requirements before tools.
3. List realistic options.
4. Attach benchmark evidence.
5. Record the decision and what it sacrifices.
6. Define explicit triggers for re-evaluation.

### Why This Works

An ADR preserves reasoning. Without it, a future engineer sees only the selected library and may repeat or reverse the decision without understanding the original constraints.

### Production Lesson

An architectural choice is a hypothesis tied to a context. A good ADR makes that context and the evidence recoverable months or years later.

---

## Question 35 — A05: Interpret a Hypothetical Benchmark Without Ranking Engines

### Difficulty
Advanced

### Topics Covered
- Topic 08 — benchmark interpretation, runtime vs memory, correctness, requirements

### Problem

The following are **hypothetical** benchmark inputs, not real measurements:

```text
Container memory limit = 32 GB

Engine A: 100 seconds, 28 GB peak, correct
Engine B: 108 seconds, 12 GB peak, correct
Engine C: 90 seconds, 45 GB peak, correct
```

### What You Need to Do

Interpret the evidence for a production decision without declaring a universal winner.

### Solution

First apply the resource constraint:

```text
Engine C
→ peak memory exceeds the 32 GB container limit
→ the observed configuration is operationally infeasible for that deployment
```

Between A and B, the decision depends on requirements. A is faster but uses substantially more memory. B is slower but has much more headroom.

The next step is to determine whether the workload SLA has sufficient margin for B and whether A's memory leaves acceptable room for variability, concurrency, or data growth.

### Second-order interpretation

Before concluding that Engine A or B is intrinsically faster, check whether the result could be explained by different file layout, pruning, conversion cost, or memory pressure. An engine benchmark should isolate the engine question from storage-layout and interoperability effects.
### How to Solve It

1. Treat all values as hypothetical inputs.
2. Filter out configurations that violate hard deployment constraints.
3. Compare remaining candidates against SLA, memory headroom, correctness, and maintainability.
4. Ask what happens if data grows or workload variance increases.
5. Document the evidence rather than turning it into a global ranking.

### Why This Works

Performance is multidimensional. A faster runtime is not automatically better when the memory profile makes the deployment unsafe. Conversely, a memory-efficient engine can be unsuitable if it cannot meet the required latency.

### Production Lesson

Production fit is the intersection of constraints. Benchmark interpretation should start with hard requirements, not with whichever number is visually smaller.

---

## Question 36 — A06: Evaluate a New Engine Quickly

### Difficulty
Advanced

### Topics Covered
- Topic 08 — DataFusion/chDB/cuDF awareness, new-engine evaluation framework

### Problem

A colleague proposes replacing the team's current analytical engine with DataFusion, chDB, or cuDF because a conference demo looked impressive.

### What You Need to Do

Create a ten-step technical evaluation process that can be applied to any new engine. Include how you would test DataFusion, chDB, and cuDF at awareness level.

### Solution

Use this repeatable process:

```text
1. What workload does it target?
2. What execution model does it use?
3. What data formats does it support?
4. What is its memory model?
5. Does it support lazy execution?
6. Does it support streaming/out-of-core execution?
7. Is execution CPU, GPU, or distributed?
8. What is the interoperability story?
9. What are ecosystem and operational requirements?
10. Can performance and correctness be reproduced on our workload?
```

Awareness examples:

- **DataFusion:** Apache Arrow-oriented, Rust-based analytical query engine ecosystem.
- **chDB:** ClickHouse-based embedded analytical SQL approach for Python/local use cases.
- **cuDF:** GPU DataFrame ecosystem in RAPIDS, relevant when GPU-suitable computation is a real requirement.

### Evaluation record

For each new engine, record its release/version, supported formats, execution model, memory behaviour, interoperability path, operational maturity, and reproducibility of your benchmark. The existing Module 2.4 framework is designed to be re-used for future engines rather than rebuilt from scratch.
### How to Solve It

Do not start with benchmark results. First determine whether the engine targets the actual problem. Then run a small spike using the team's representative query set.

For cuDF specifically, establish that the workload can benefit from GPU resources and that GPU memory/transfer characteristics are acceptable; GPU acceleration is not a substitute for streaming or distributed architecture when the actual problem is capacity or scale.

### Why This Works

Technology evaluation is a hypothesis-testing process. A new engine can be technically excellent while being a poor fit for a particular team or workload.

### Production Lesson

A two-day evaluation spike that measures the right questions is usually more useful than weeks of argument from benchmark headlines. Evaluate capabilities, operational fit, and reproducibility—not demo quality.

---

## Question 37 — A07: Find Benchmark Contamination

### Difficulty
Advanced

### Topics Covered
- Topic 08 — cold/warm cache, same format, reproducibility, benchmark methodology
- Topics 03/06 — file scans and caching

### Problem

A benchmark report says:

```text
Polars: 20 s
DuckDB: 22 s
pandas: 31 s
```

But you discover:

- Polars used warm cache;
- DuckDB used cold cache;
- pandas read CSV;
- Polars and DuckDB read Parquet;
- thread counts differed;
- no peak memory was measured.

### What You Need to Do

Identify why the comparison is contaminated and redesign the experiment.

### Solution

The comparison changes multiple variables:

```text
cache state
file format
thread configuration
measurement dimensions
```

Use the same physical input format for the main comparison, controlled cache conditions, documented thread/configuration settings, repeated runs, and correctness checks. Add peak memory and relevant I/O measures.

### Reproducibility record

At minimum capture Python, pandas, Polars, DuckDB, and PyArrow versions plus CPU, RAM, OS, storage, dataset version/checksum, thread configuration, and cache assumptions. When new engines are included, add their versions too.
### How to Solve It

Ask for every reported number:

```text
Same data?
Same format?
Same semantics?
Same hardware?
Same cache condition?
Same thread assumptions?
Same correctness?
Same measurement scope?
```

If the answer is no, the numbers cannot be interpreted as a clean engine comparison.

### Why This Works

Benchmark contamination turns one experiment into a mixture of experiments. For example, a CSV-vs-Parquet comparison measures format differences in addition to engine behaviour.

### Production Lesson

Benchmark evidence is only as trustworthy as the controls around it. A senior engineer should be comfortable rejecting a benchmark report when its methodology is not comparable.

---

## Question 38 — A08: Fix a Bad Lake Layout Before Changing Engines

### Difficulty
Advanced

### Topics Covered
- Topic 06 and Topic 08 — Hive partitions, small files, pushdown, file layout vs engine choice

### Problem

A 5 TB lake contains:

```text
year/month/day/customer_id/
```

The result is hundreds of thousands of tiny Parquet files. Queries are slow, and the team proposes switching engines.

### What You Need to Do

1. Identify the likely file-layout problem.
2. Explain the trade-off between coarse and fine partitioning.
3. Propose a redesign process.
4. Explain why changing engines first may be premature.

### Solution

The highly granular partition key, especially `customer_id`, can create excessive partition cardinality and tiny files.

A redesign should start by studying common query predicates and then choosing partition keys with useful pruning value but manageable cardinality. Write fewer, reasonably sized Parquet files and validate that downstream queries can still prune relevant partitions.

### Partition design extension

Evaluate partition cardinality against actual query predicates. The design objective is not the maximum number of partitions; it is useful pruning with manageable file and metadata overhead. Measure both query speed and file/request behaviour after any layout change.
### How to Solve It

1. Measure file count and file-size distribution.
2. Measure which partition keys real queries actually filter.
3. Identify partitions with little data.
4. Test a lower-cardinality partition design.
5. Compare files touched, bytes read, request count, and runtime.
6. Only after file-layout optimization should you ask whether engine capacity remains the bottleneck.

### Why This Works

Query performance depends on both engine execution and physical layout. An engine that sees a badly fragmented lake may spend substantial effort discovering and reading many small objects.

### Production Lesson

Do not confuse an engine problem with a data-layout problem. Sometimes the highest-leverage optimization is changing how data is stored rather than changing the query engine.

---

## Question 39 — A09: Define Revisit Conditions for a Production Engine Choice

### Difficulty
Advanced

### Topics Covered
- Topic 08 — capacity planning, revisit conditions, SLA, growth, operational risk

### Problem

A team has selected a single-node engine for current workloads. Data volume and complexity are increasing, but no formal trigger exists for reconsidering the architecture.

### What You Need to Do

Create a set of measurable revisit conditions. Do not use a universal threshold such as "move to Spark at X TB."

### Solution

Revisit conditions should be tied to observed capacity and requirements, for example:

```text
Revisit if:
- peak memory approaches the safe deployment limit;
- runtime consistently exceeds the SLA;
- join/aggregation state cannot be kept within capacity;
- required concurrency exceeds the engine's tested model;
- data growth exceeds the measured operating envelope;
- object-store or network throughput becomes the bottleneck;
- operational reliability requires distributed fault isolation;
- an ecosystem dependency changes the required interface;
- upgrade churn makes the current architecture costly to maintain.
```

### Operational extension

Revisit conditions can also include:

- a new serverless deployment with a tighter cold-start requirement;
- a new container memory limit;
- increased concurrency;
- higher cloud/network cost;
- an upgrade that introduces API or performance churn;
- a new ecosystem dependency requiring pandas or another interface.

These are architectural triggers because the workload context has changed.
### How to Solve It

1. Record today's measured baseline.
2. Identify the resource or requirement that could become limiting.
3. Turn it into a measurable trigger.
4. Define who reviews the condition and what evidence is required.
5. Re-run representative benchmarks before migrating.

### Why This Works

An architecture decision is valid within a context. Revisit conditions make that context explicit and prevent both premature migration and late crisis-driven migration.

### Production Lesson

Good architecture has an exit plan. You should know what evidence would change your mind before the workload becomes too large to migrate comfortably.

---

## Question 40 — A10: End-to-End Module 2.4 Architecture Review

### Difficulty
Advanced

### Topics Covered
- All eight topics — Arrow, Polars, Lazy, streaming, DuckDB, files/object storage, interoperability, engine selection

### Problem

You are reviewing this proposed production pipeline:

```text
S3-compatible object storage
        ↓
500 GB Hive-partitioned Parquet
        ↓
DuckDB query
        ↓
pandas DataFrame
        ↓
Polars transformation
        ↓
DuckDB again
        ↓
CSV output
```

The deployment is a 32 GB container. The final business requirement is daily revenue by customer segment, with a pandas-only library needed for one small enrichment step. The proposal contains no benchmark, ADR, or memory measurements.

### What You Need to Do

Perform a senior-level architecture review. Your answer must include:

1. workload characterization;
2. schema/type considerations;
3. query/file-layout considerations;
4. lazy/streaming opportunities;
5. interoperability risks;
6. memory risks;
7. benchmark plan;
8. candidate architectures;
9. correctness validation;
10. ADR structure and revisit conditions.

Do not choose a universal "best" engine. Choose a defensible architecture only after stating the evidence that must be collected.

### Solution

A strong review starts by challenging unnecessary boundaries.

#### 1. Workload characterization

Record:

```text
500 GB compressed/on-disk size
partition structure
expected selected partitions/day
required columns
join/aggregation cardinality
output size
32 GB container limit
SLA
concurrency
expected growth
```

The 500 GB figure alone does not determine the architecture.

#### 2. File and query design

Prefer direct Parquet querying with partition pruning and projection/filter pushdown. Verify the Hive partition columns align with daily query predicates. Inspect file count and size because remote I/O can dominate.

#### 3. Execution strategy

For a SQL-heavy aggregation, keeping the main computation in DuckDB can be reasonable. If the result is large, avoid converting the full result to pandas. If the result becomes small after aggregation, the pandas-only step should occur near the edge.

#### 4. Interoperability redesign

A more deliberate pattern is:

```text
S3-compatible Parquet
       ↓
DuckDB SQL
       ↓
small result / Arrow boundary
       ↓
pandas-only enrichment
       ↓
Arrow or Polars if further transformation is genuinely needed
       ↓
Parquet output
```

If substantial DataFrame transformation is required before the pandas-only step, evaluate:

```text
DuckDB → Arrow → Polars → small pandas edge
```

rather than:

```text
DuckDB → pandas → Polars → DuckDB
```

#### 5. Memory risks

Potential peaks come from:

- remote scan buffers;
- join state;
- aggregation state;
- pandas materialization;
- conversions;
- final output materialization.

Use process-level peak memory measurement and, where relevant, DuckDB resource controls or streaming/sink behaviour.

#### 6. Benchmark plan

Use representative queries, the same Parquet data, the same hardware/container, cold/warm conditions, repeated runs, and correctness checks. Measure:

```text
runtime
peak memory
bytes read/transferred where meaningful
files/partitions touched
conversion time
output size
```

#### 7. Candidate architectures

Evaluate at least:

```text
A. DuckDB-first
B. Polars-first
C. DuckDB → Arrow → Polars
D. DuckDB → small pandas edge
E. distributed/managed architecture if single-node evidence fails
```

The final selection depends on measured workload fit and operational requirements.

#### 8. Correctness validation

Verify:

```text
row counts
schema
null semantics
timestamps/time zones
Decimal semantics where used
revenue aggregates
cross-engine equivalence
```

#### 9. ADR

Document:

```text
Context
Requirements
Options
Measurements
Decision
Consequences
Risks
Revisit conditions
```

#### 10. Revisit conditions

Define measurable triggers such as:

```text
peak memory approaches safe container capacity
SLA is exceeded
remote I/O becomes dominant despite layout optimization
concurrency changes
workload growth exceeds tested capacity
single-node state becomes unmanageable
```

### Final consolidation requirement

Your final review should also identify the appropriate awareness-level alternatives from the module—Spark, Dask, Ray Data, cloud warehouses, DataFusion, chDB, and cuDF—and explain why each is or is not relevant to the stated constraint. This is an evidence map, not a ranking.
### How to Solve It

Use the Module 2.4 engineering sequence:

```text
Workload
   ↓
Requirements
   ↓
Schema and file layout
   ↓
Candidate architecture
   ↓
Correctness reference
   ↓
Small experiment
   ↓
Plan inspection
   ↓
Scale-up benchmark
   ↓
Runtime + memory + I/O + conversion evidence
   ↓
Operational review
   ↓
ADR
   ↓
Revisit conditions
```

The critical move is to reduce unnecessary work and boundaries before concluding that the engine itself is insufficient.

### Why This Works

The proposed pipeline mixes several engines but does not justify the transitions. Each additional boundary may add allocation, type conversion, and memory pressure. At the same time, no single component should be selected simply because it sounds suited to "500 GB."

Module 2.4's central lesson is that engine choice is a workload-fit decision. Query design, file layout, memory state, data movement, team constraints, and operational requirements all contribute to the final architecture.

### Production Lesson

A senior architecture review asks three questions repeatedly:

```text
Are the results correct?
Are we doing unnecessary work?
Can the chosen design operate safely under real constraints?
```

The outcome should be a measured, documented decision—not a permanent ranking of pandas, Polars, DuckDB, or distributed engines.

---

# Module 2.4 Mini-Project — One Workload, Four Engines

This is the final synthesis exercise for Module 2.4. It is a project, not a 41st practice question.

## Goal

Build a single-node pipeline that replaces a slow nightly pandas job and a small Spark cluster where the evidence justifies it, and document the decision.

## Scenario

Your team runs a slow nightly pandas job plus a small Spark cluster. You must build the replacement pipeline and justify the architecture from workload evidence and your own measurements, not from a generic engine ranking.

## Data

- several years of NYC Taxi trips, or generated equivalent data at least 2× your RAM, stored as Hive-partitioned Parquet in MinIO (Topic 06 has the MinIO Compose file; Topics 03 and 04 have data generators);
- a zone lookup CSV;
- a daily fare-rules JSON file.

## Required Deliverables

Build `lake_analytics/`, a `uv` project:

```text
Ingestion
   ↓
Bronze
   ↓
Polars lazy + streaming
   ↓
Silver
   ↓
DuckDB
   ↓
Gold
   ↓
pandas-only consumer edge where needed
```

1. **Ingestion:** land raw CSV/JSON files in MinIO and convert them to partitioned Parquet with explicit Arrow schemas.
2. **Silver in Polars (lazy, streaming where appropriate):** typed, deduplicated, validated trips. Invalid rows go to a quarantine dataset.
3. **Gold in DuckDB:** daily and monthly zone metrics; top-N routes per borough with `QUALIFY`; an `ASOF JOIN` to the fare rules; written back to MinIO with `COPY ... PARTITION_BY`.
4. **Consumer edge:** one step hands a small result to a pandas-only library (for example a plotting or reporting library) with minimal copying.
5. **Tests:** pytest tests for every transformation on tiny inputs, schema assertions after every engine boundary, and a reconciliation check.

## Benchmark Requirements

Run the same silver + gold logic in pandas (chunked), Polars and DuckDB at three data sizes. Record, for every run:

- runtime and peak memory;
- bytes read where relevant;
- cold and warm conditions where meaningful;
- repeated runs (record each run, not only a summary);
- the dataset, file format, machine, and library versions.

Do not compare different datasets, file formats or workloads and attribute the difference to the engine. All numbers must come from your own measurements.

## Correctness Requirements

- All engines produce identical gold outputs (sort before comparing).
- Trip counts and revenue reconcile across engines.
- Schema assertions pass after every engine boundary, and every boundary is documented.
- The pipeline processes a dataset larger than your RAM without crashing.

## ADR Requirements

Write an evidence-based ADR recommending the default engine(s), with:

- the workload and benchmark evidence (the results table);
- operational constraints and risks;
- team and ecosystem considerations;
- single-node capacity and the point at which you would move to Spark or another distributed engine;
- consequences of the decision.

Do not choose an engine in advance; the recommendation must follow from your own measurements.

## Revisit Conditions

State the observable conditions that would make you revisit the decision, for example data growth beyond the measured single-node capacity, a missed runtime target, a new library requirement, or a change in team skills.

## Completion Checklist

- [ ] The pipeline runs from ingestion to gold and processes data larger than RAM.
- [ ] All engines produce identical gold outputs.
- [ ] Every engine boundary is documented and schema-checked.
- [ ] Benchmarks cover three sizes with repeated runs, peak memory and correctness.
- [ ] The ADR's recommendation follows from my own measurements and includes revisit conditions.

---

# Module 2.4 Practice Completion Checklist

- [ ] Completed all 10 Basic questions.
- [ ] Completed all 10 Moderate questions.
- [ ] Completed all 10 Hard questions.
- [ ] Completed all 10 Advanced questions.
- [ ] Practiced Arrow memory reasoning.
- [ ] Practiced Polars expressions and contexts.
- [ ] Practiced lazy query planning.
- [ ] Practiced streaming and memory reasoning.
- [ ] Practiced DuckDB analytical SQL.
- [ ] Practiced file and object-storage querying.
- [ ] Practiced interoperability and zero-copy reasoning.
- [ ] Practiced benchmarking.
- [ ] Practiced engine-selection reasoning.
- [ ] Completed the Module 2.4 mini-project.
- [ ] Practiced production architecture.
- [ ] Validated benchmark questions without using fabricated numbers.
- [ ] Can explain the solutions aloud rather than merely copying them.
