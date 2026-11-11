# 13 — Chunked Processing and Memory Reduction

> **Stage 2 — Python for Data Engineering · Module 2.3 — DataFrames with pandas**

> **Central production question:** What do I do when the data does not fit comfortably in memory?

This is the final production-oriented pandas topic in the module. It combines ideas learned earlier:

- **Topic 02 — Reading and writing data:** read only the data that is needed.
- **Topic 04 — dtypes and memory representation:** choose types deliberately.
- **Topic 06 — groupby and aggregation:** reduce large row sets into small partial results.
- **Topic 12 — Copy-on-Write:** avoid unnecessary copies while making ownership explicit.

The central skill is not memorizing one API such as `chunksize`. The skill is learning how to design a **bounded-memory, correct, observable, retry-safe data pipeline**.

---

## 1. What Problem Are We Solving?

Imagine a CSV containing 20 GB of transaction records and a machine with 4 GB of RAM.

A naïve program might start with:

```python
import pandas as pd

df = pd.read_csv("transactions.csv")
```

That asks pandas to build one complete DataFrame. Even if the file is exactly 20 GB on disk, the required RAM is not 20 GB exactly. CSV is text, and operations may create additional temporary objects.

A more useful mental model is:

```text
File on disk
    ↓
parse / decode
    ↓
DataFrame representation
    ↓
temporary arrays / objects
    ↓
groupby / sort / merge / copy
    ↓
peak working memory
```

Therefore the production question becomes:

> **How can I control the amount of data that is simultaneously live in memory without changing the mathematical meaning of the computation?**

The answer often combines several techniques:

```text
measure
  ↓
read less
  ↓
choose better dtypes
  ↓
drop unused columns
  ↓
process in chunks
  ↓
reduce each chunk
  ↓
carry only necessary state
  ↓
write incrementally
  ↓
validate correctness
  ↓
measure peak memory
  ↓
change engine when pandas is no longer the right tool
```

---

## 2. Learning Standard

For every major technique, keep asking:

1. What memory problem does this solve?
2. Does it reduce input size, working-set size, or both?
3. Does it change the mathematics of the result?
4. Does the algorithm need state across chunks?
5. Can the partial results be combined exactly?
6. What happens if the job fails halfway through?
7. Can the job be retried safely?
8. What is the peak memory, not only the final memory?
9. When should a different engine be considered?

---

# SECTION A — MEMORY FUNDAMENTALS

## 3. RAM, Disk, and DataFrame Memory

A file is a serialized representation. A DataFrame is an in-memory representation.

For example, a CSV row might be stored on disk as:

```text
1000001,IN,12345.67,2026-09-26T14:30:00
```

In memory, pandas may represent these fields using different typed buffers and objects.

The important result is:

> **Disk size is not a reliable prediction of DataFrame memory.**

Compressed storage makes the difference even larger.

A compressed 2 GB file can expand to substantially more data after decoding.

---

## 4. The Working-Set Mental Model

Think about the largest set of objects that must be alive simultaneously.

```text
Peak memory
≈ current input
+ temporary objects
+ aggregation state
+ boundary state
+ output buffers
+ library/runtime overhead
```

This is a planning model, not an exact accounting formula.

The main production lesson is:

> **Optimize the working set, not just the final output.**

---

## 5. `df.info(memory_usage="deep")`

A quick interactive inspection:

```python
import pandas as pd

df = pd.DataFrame(
    {
        "customer": ["Alice", "Bob", "Alice"],
        "amount": [100.0, 200.0, 150.0],
    }
)

df.info(memory_usage="deep")
```

`deep=True` asks pandas to make a deeper accounting of object-dtype contents.

This is especially useful for string-heavy object columns.

Use it during exploration when asking:

> Which columns are consuming most of my DataFrame's memory?

---

## 6. `memory_usage(deep=True)`

For programmatic analysis:

```python
memory = df.memory_usage(
    index=False,
    deep=True,
)

print(memory)
print("total bytes:", memory.sum())
```

`DataFrame.memory_usage()` returns per-column memory usage in bytes. With `deep=True`, pandas inspects object-dtype elements more deeply. 

---

## 7. Shallow vs Deep Memory

| Measurement | Meaning |
| --- | --- |
| `memory_usage(deep=False)` | Faster, shallower accounting |
| `memory_usage(deep=True)` | More detailed accounting for object data |
| Process RSS | Memory resident in the whole process |
| Peak RSS | Highest observed process residency |

Do not confuse:

```python
df.memory_usage(deep=True).sum()
```

with:

```text
complete process memory
```

A process also contains Python objects, temporary arrays, imported libraries, allocator state, PyArrow buffers, and other resources.

---

## 8. Memory by Column

Create a simple report:

```python
memory = (
    df.memory_usage(index=False, deep=True)
    .rename("bytes")
    .sort_values(ascending=False)
    .to_frame()
)

memory["percent"] = (
    memory["bytes"] / memory["bytes"].sum() * 100
)

print(memory)
```

This changes a vague problem:

> “The DataFrame is huge.”

into a concrete problem:

> “This string column consumes 42% of the DataFrame memory.”

That is a much better starting point for optimization.

---

## 9. Before/After Measurement

Use a reusable helper:

```python
import pandas as pd


def dataframe_memory_bytes(df: pd.DataFrame) -> int:
    return int(
        df.memory_usage(
            index=False,
            deep=True,
        ).sum()
    )
```

Then:

```python
before = dataframe_memory_bytes(df)

optimized = df.copy()
optimized["country"] = optimized["country"].astype("category")

after = dataframe_memory_bytes(optimized)

reduction_pct = (before - after) / before * 100

print(
    {
        "before": before,
        "after": after,
        "reduction_percent": reduction_pct,
    }
)
```

The roadmap's formula is:

```text
memory_reduction_%
    = (before - after) / before * 100
```

The objective is always:

> **Measure first. Optimize second. Measure again.**

---

## 10. Peak Memory vs Final Memory

Suppose:

```text
input frame     = 900 MB
final result    = 200 MB
temporary work  = 700 MB
```

The process can fail even though the final result is small.

Think:

```text
start
  ↓
read
  ↓
temporary conversion
  ↓
groupby / sort / merge
  ↓
peak memory
  ↓
final output
```

A production engineer cares about the peak because the machine must survive the peak.

---

# SECTION B — READ LESS DATA

## 11. The Cheapest Allocation Is the One You Never Make

Before chunking, ask whether all input columns and rows are necessary.

If a file has 50 columns and the pipeline needs 5, reading all 50 columns can waste:

- RAM;
- parsing work;
- CPU;
- I/O;
- downstream processing time.

The production principle is:

> **Read less before optimizing computation.**

---

## 12. `usecols`

For CSV:

```python
df = pd.read_csv(
    "orders.csv",
    usecols=[
        "order_id",
        "country",
        "amount_cents",
        "created_at",
    ],
)
```

This is an input projection.

### Why it helps

```text
50 source columns
        ↓
5 required columns
        ↓
smaller DataFrame
        ↓
smaller downstream operations
```

### Production use

Always treat `usecols` as part of the data contract when you know which columns are needed.

---

## 13. Explicit `dtype`

If the source contract is known, define dtypes at ingestion:

```python
df = pd.read_csv(
    "orders.csv",
    usecols=[
        "order_id",
        "quantity",
        "country",
        "amount_cents",
    ],
    dtype={
        "order_id": "int64",
        "quantity": "int16",
        "country": "category",
        "amount_cents": "int64",
    },
)
```

The exact choice depends on:

- value range;
- nullability;
- business meaning;
- downstream operations;
- precision requirements.

Never select a tiny integer dtype just because it is smaller.

---

## 14. Safe Dtype Selection

Use this reasoning loop:

```text
inspect min / max
       ↓
understand semantic meaning
       ↓
choose compatible dtype
       ↓
validate range / precision
       ↓
measure memory
```

Example:

```python
s = pd.Series([0, 12, 255, 1000])

print("min:", s.min())
print("max:", s.max())

candidate = pd.to_numeric(
    s,
    downcast="integer",
)

print(candidate.dtype)
```

---

## 15. `nrows`

`nrows` is useful for controlled exploration:

```python
sample = pd.read_csv(
    "orders.csv",
    nrows=10_000,
)
```

Use it for:

- schema discovery;
- profiling;
- local debugging;
- benchmark setup;
- testing parsing assumptions.

Do not confuse sampling with full-data correctness validation.

---

## 16. Parquet Column Pruning

For Parquet:

```python
df = pd.read_parquet(
    "orders.parquet",
    columns=[
        "order_id",
        "country",
        "amount_cents",
    ],
)
```

Pandas exposes `columns=` for Parquet reads, and because Parquet is columnar, irrelevant columns can often be avoided. 

---

## 17. Parquet Filtering

Pandas also supports filters:

```python
df = pd.read_parquet(
    "orders.parquet",
    columns=[
        "order_id",
        "country",
        "amount_cents",
    ],
    filters=[
        ("country", "==", "IN"),
    ],
)
```

Supported filter operators include comparisons and membership-style predicates. Exact I/O savings depend on storage layout, partitioning, row-group statistics, and the engine. 

### Important distinction

```text
columns=
    ↓
controls which columns are returned/read

filters=
    ↓
controls which rows qualify when the engine can push filtering down
```

---

## 18. CSV vs Parquet for the Memory Problem

| Property | CSV | Parquet |
| --- | --- | --- |
| Schema | Inferred unless declared | Stored schema |
| Column pruning | Limited by row-oriented format | Natural in columnar storage |
| Predicate filtering | Usually application-side | Can exploit partitions/row groups |
| Compression | Text/compression dependent | Columnar encoding + compression |
| Analytical access | Less specialized | Designed for analytical workloads |

Do not turn this into “Parquet is always faster.”

The practical lesson is:

> **Storage format determines what the reader can avoid doing.**

---

# SECTION C — REDUCING COLUMN MEMORY

## 19. Numeric Downcasting

Pandas supports numeric downcasting:

```python
import pandas as pd

quantity = pd.Series([1, 2, 3, 100])

compact = pd.to_numeric(
    quantity,
    downcast="integer",
)

print(compact)
print(compact.dtype)
```

`pd.to_numeric()` supports downcast modes such as:

- `integer`;
- `signed`;
- `unsigned`;
- `float`.

Pandas documents `downcast` as a way to convert to the smallest compatible numeric dtype where possible. 

---

## 20. Signed and Unsigned Integers

Signed types support negative values.

Unsigned types do not.

Example reasoning:

```text
quantity
min = 0
max = 500
→ unsigned may be appropriate if source contract guarantees non-negative values
```

But:

```text
balance
min = -500
max = 500
→ unsigned would be invalid
```

Always validate against the actual domain, not just today's sample.

---

## 21. Float Downcasting and Precision

```python
values = pd.Series([1.25, 2.50, 100.75])

compact = pd.to_numeric(
    values,
    downcast="float",
)

print(compact.dtype)
```

Float downcasting is a precision decision.

For financial values, do not blindly optimize for byte size. Define the numerical contract first.

---

## 22. Validate Downcasting

A simple integer check:

```python
original = pd.Series([0, 10, 255, 1000])

compact = pd.to_numeric(
    original,
    downcast="integer",
)

assert compact.astype("int64").equals(
    original.astype("int64")
)
```

In a real pipeline, validate:

- range;
- sign;
- null behavior;
- precision;
- business invariants.

---

## 23. `category` for Low-Cardinality Strings

Suppose a 10-million-row column contains only 12 status values.

A categorical representation can conceptually store:

```text
category dictionary
    pending
    paid
    shipped
    delivered
    ...

row codes
    0
    1
    1
    2
    3
```

Repeated strings are represented by a dictionary plus codes instead of repeated full values.

Pandas' scaling guidance shows low-cardinality string columns as strong category candidates. 

---

## 24. Category: Good and Bad Candidates

Good candidate:

```text
10 million rows
20 distinct status values
```

Potentially poor candidate:

```text
10 million rows
9.5 million distinct IDs
```

Why?

Because category has to store the unique-value dictionary.

Measure:

```python
s = pd.Series(
    ["pending", "paid", "paid", "shipped"],
    dtype="string",
)

categorical = s.astype("category")

print("string bytes:", s.memory_usage(deep=True))
print("category bytes:", categorical.memory_usage(deep=True))
```

---

## 25. Arrow-Backed Strings

Pandas supports PyArrow-backed string storage:

```python
import pandas as pd

s = pd.Series(
    ["IN", "US", "IN", None],
    dtype="string[pyarrow]",
)

print(s)
print(s.dtype)
```

Pandas documents Arrow-backed nullable dtypes through `dtype_backend="pyarrow"` and Arrow string dtypes such as `string[pyarrow]`. 

Potential benefits depend on workload, backend, interoperability requirements, and supported operations.

Do not state:

> Arrow-backed strings are always faster.

State instead:

> **Arrow-backed strings can be beneficial; measure actual memory and runtime for the workload.**

---

## 26. Arrow-Backed Data from Readers

For example:

```python
df = pd.read_csv(
    "orders.csv",
    dtype_backend="pyarrow",
)
```

Pandas documents that readers can return PyArrow-backed nullable data with this option. 

This can produce columns such as:

```text
int64[pyarrow]
double[pyarrow]
string[pyarrow]
bool[pyarrow]
```

Use Arrow-backed data deliberately rather than simply because “Arrow is modern.”

---

## 27. Drop Unused Columns Early

For an already-loaded DataFrame:

```python
needed = [
    "order_id",
    "country",
    "amount",
    "created_at",
]

df = df[needed]
```

The principle is:

> **Do not carry data you do not need.**

Narrower frames can reduce the cost of later transformations, temporary objects, serialization, and output.

---

# SECTION D — CHUNKED READING

## 28. What Is Chunked Processing?

Instead of:

```text
large file
   ↓
read everything
   ↓
one giant DataFrame
```

use:

```text
large file
   ↓
chunk 1 → process → discard/reduce/write
   ↓
chunk 2 → process → discard/reduce/write
   ↓
chunk 3 → process → discard/reduce/write
   ↓
...
```

The entire dataset never needs to be present as one DataFrame.

---

## 29. `read_csv(chunksize=...)`

The central API is:

```python
reader = pd.read_csv(
    "large.csv",
    chunksize=100_000,
)

for chunk in reader:
    print(chunk.shape)
```

Pandas documents `chunksize` as causing `read_csv()` to return an iterator over DataFrame chunks. 

---

## 30. What Is a Chunk?

A chunk is an ordinary pandas DataFrame representing a bounded portion of the source.

If:

```python
chunksize=100_000
```

then the target working set is around 100,000 input rows at a time, though actual memory depends heavily on row width and operation behavior.

The chunk is not a magic memory boundary. Operations performed on that chunk can still allocate temporary objects.

---

## 31. Choosing a Starting Chunk Size

There is no universal best value.

Start experimentally, for example:

```python
chunksize=100_000
```

Then measure:

- per-chunk memory;
- peak process memory;
- throughput;
- total runtime.

Think:

```text
chunk too small
    ↓
loop/parsing overhead

chunk too large
    ↓
memory pressure

useful region
    ↓
acceptable memory + acceptable throughput
```

---

## 32. `iterator=True`

You can request an explicit reader:

```python
reader = pd.read_csv(
    "large.csv",
    iterator=True,
)

chunk = reader.get_chunk(100_000)
print(chunk.shape)
```

For a straightforward loop, `chunksize=` is usually easier:

```python
for chunk in pd.read_csv(
    "large.csv",
    chunksize=100_000,
):
    process(chunk)
```

The important concept is not the flag. It is **incremental materialization of the input**.

---

## 33. `low_memory` Is Not the Same as Chunking

This distinction is important.

Pandas' `read_csv(low_memory=True)` can process a file internally in smaller pieces during parsing, but it still returns one full DataFrame unless `chunksize` or `iterator` is used. The documentation explicitly distinguishes parser behavior from returning the file in chunks. 

Therefore:

```text
low_memory=True
→ parser memory strategy
→ one DataFrame result unless chunking requested
```

versus:

```text
chunksize=...
→ caller receives chunks
→ caller controls incremental processing
```

This distinction prevents a common misunderstanding.

---

## 34. Canonical Chunk Loop

```python
reader = pd.read_csv(
    "large.csv",
    chunksize=100_000,
)

for chunk in reader:
    # validate
    # clean
    # transform
    # aggregate / write
    pass
```

At every iteration ask:

> **What remains alive after this chunk finishes?**

That question is as important as the chunk size itself.

---

# SECTION E — CHUNKED SQL READING

## 35. Why Database Results Need Chunking

A SQL query can return millions of rows.

Naïve approach:

```python
df = pd.read_sql(
    "SELECT * FROM huge_table",
    connection,
)
```

Chunked approach:

```python
reader = pd.read_sql(
    "SELECT order_id, country, amount FROM huge_table",
    connection,
    chunksize=100_000,
)

for chunk in reader:
    process(chunk)
```

Pandas documents `read_sql(..., chunksize=N)` as returning an iterator with N rows per chunk. 

---

## 36. SQL Projection

Prefer:

```python
query = """
SELECT
    order_id,
    country,
    amount_cents
FROM orders
"""

reader = pd.read_sql(
    query,
    connection,
    chunksize=100_000,
)
```

instead of:

```python
query = "SELECT * FROM orders"
```

Projection reduces data movement and client memory.

---

## 37. SQL Filtering

If the database can eliminate irrelevant rows:

```python
query = """
SELECT
    order_id,
    country,
    amount_cents
FROM orders
WHERE country = :country
"""

reader = pd.read_sql(
    query,
    connection,
    params={"country": "IN"},
    chunksize=100_000,
)
```

The principle is:

> **Push work toward the source when it reduces unnecessary data movement.**

Do not turn this into a full SQL course.

---

## 38. SQL Aggregation Before pandas

If the database can safely perform a required aggregation, that can reduce the result size dramatically.

Conceptually:

```text
database rows
   ↓
SQL filter / aggregate
   ↓
smaller result
   ↓
pandas chunk processing
```

The right choice depends on where the business logic belongs and what the source system can safely support.

---

# SECTION F — PROCESSING EACH CHUNK

## 39. Standard Chunk Lifecycle

```text
read chunk
    ↓
validate / clean
    ↓
transform
    ↓
aggregate or write
    ↓
retain minimum state
    ↓
next chunk
```

The ideal chunk has a short lifetime.

---

## 40. Pattern 1 — Row-Level Transformation

If every row can be transformed independently:

```python
for chunk in pd.read_csv(
    "orders.csv",
    chunksize=100_000,
):
    chunk["amount_dollars"] = (
        chunk["amount_cents"] / 100
    )
    write_clean_chunk(chunk)
```

This is naturally chunk-safe.

---

## 41. Pattern 2 — Filter Then Aggregate

```python
partials = []

for chunk in pd.read_csv(
    "orders.csv",
    chunksize=100_000,
):
    chunk = chunk.loc[
        chunk["status"].eq("paid")
    ]

    partial = (
        chunk.groupby("country", as_index=False)
        .agg(
            revenue_cents=("amount_cents", "sum"),
            order_count=("order_id", "count"),
        )
    )

    partials.append(partial)
```

The important observation is:

> `partials` stores compact aggregated results, not all original rows.

---

## 42. Pattern 3 — Chunk → Groupby → Partial Aggregate

```text
chunk
  ↓
groupby
  ↓
partial aggregate
  ↓
discard input chunk
  ↓
next chunk
  ↓
combine partials
```

This is often one of the most effective ways to process data larger than RAM.

---

## 43. Pattern 4 — Chunk → Write Output

```python
for i, chunk in enumerate(
    pd.read_csv("orders.csv", chunksize=100_000)
):
    clean = clean_orders(chunk)

    clean.to_csv(
        f"clean-part-{i:05d}.csv",
        index=False,
    )
```

The whole output is never accumulated in one DataFrame.

---

## 44. Pattern 5 — Chunk → Quality Check → Quarantine

```python
for chunk in pd.read_csv(
    "orders.csv",
    chunksize=100_000,
):
    valid = chunk.loc[
        chunk["amount_cents"] >= 0
    ]

    invalid = chunk.loc[
        chunk["amount_cents"] < 0
    ]

    write_clean_chunk(valid)
    write_quarantine_chunk(invalid)
```

A production rule should come from the source contract. Do not invent a business rule merely to illustrate chunking.

---

## 45. Why `chunks = []` Can Defeat Chunking

This pattern looks chunked:

```python
chunks = []

for chunk in pd.read_csv(
    "large.csv",
    chunksize=100_000,
):
    chunks.append(process(chunk))

result = pd.concat(chunks)
```

But if each processed chunk remains large, memory grows with the total dataset.

Conceptually:

```text
chunk 1 → retained
chunk 2 → retained
chunk 3 → retained
...
chunk N → retained
           ↓
large final in-memory collection
```

The chunk loop controls input materialization but **does not guarantee bounded memory** if your own data structures retain everything.

---

# SECTION G — COMBINING PARTIAL GROUPBY RESULTS

## 46. The Mathematics of Chunked Aggregation

Suppose the target is:

- daily trip counts;
- daily revenue;
- average fare per payment type.

The data is larger than RAM.

The correct design is usually:

```text
chunk
  ↓
partial sufficient statistics
  ↓
next chunk
  ↓
...
  ↓
combine statistics
  ↓
final metric
```

---

## 47. The Average-of-Averages Trap

Suppose:

```text
Chunk 1
count = 10
mean = 10

Chunk 2
count = 2
mean = 20
```

Average of the two means:

```text
(10 + 20) / 2 = 15
```

Correct global mean:

```text
(10×10 + 20×2) / (10 + 2)
= 140 / 12
= 11.666...
```

The chunk means have unequal weights.

Therefore:

> **Never combine chunk means by taking an unweighted average of those means unless equal weighting is actually part of the metric definition.**

---

## 48. Sufficient Statistics

For an ordinary arithmetic mean, retain:

```text
sum
count
```

Then:

```text
global_mean = total_sum / total_count
```

Example:

```text
Chunk 1
sum = 100
count = 10

Chunk 2
sum = 20
count = 2

Combined
sum = 120
count = 12

mean = 120 / 12 = 10
```

This is exact for an ordinary mean under consistent inclusion rules.

---

## 49. Complete Partial-Aggregation Example

```python
import pandas as pd

partials = []

reader = pd.read_csv(
    "trips.csv",
    chunksize=100_000,
    usecols=[
        "pickup_date",
        "payment_type",
        "trip_id",
        "fare",
    ],
)

for chunk in reader:
    partial = (
        chunk.groupby(
            ["pickup_date", "payment_type"],
            as_index=False,
        )
        .agg(
            fare_sum=("fare", "sum"),
            trip_count=("trip_id", "count"),
        )
    )

    partials.append(partial)

partial_df = pd.concat(
    partials,
    ignore_index=True,
)

final = (
    partial_df.groupby(
        ["pickup_date", "payment_type"],
        as_index=False,
    )
    .agg(
        fare_sum=("fare_sum", "sum"),
        trip_count=("trip_count", "sum"),
    )
)

final["average_fare"] = (
    final["fare_sum"] / final["trip_count"]
)
```

Notice what the `partials` list stores: grouped results, not raw rows.

---

## 50. Why the Final `groupby` Is Correct

Suppose `payment_type="card"` appears in five chunks.

Each chunk creates one partial row for `card`.

The second `groupby` combines the five partial rows:

```text
sum of sums
sum of counts
```

Then:

```text
average = combined sum / combined count
```

This gives the same answer as aggregating the full dataset, assuming the same row-selection and null-handling rules.

---

## 51. Which Aggregates Combine Easily?

| Metric | Partial strategy | Main warning |
| --- | --- | --- |
| Sum | Sum partial sums | Usually straightforward |
| Count | Sum partial counts | Define what counts |
| Min | Min of partial minima | Handle empty groups |
| Max | Max of partial maxima | Handle empty groups |
| Mean | Sum + count | Do not average means blindly |
| Variance | Appropriate sufficient statistics | More complex than mean |
| Median | Not from simple medians | Global distribution information needed |
| Exact distinct count | Retain keys or global state | State can become huge |

The general rule is:

> **Chunking works naturally when the computation has a compact, mergeable state.**

---

## 52. Full-Load vs Chunked Correctness

For a test-sized dataset:

```python
full = (
    data.groupby("country", as_index=False)
    .agg(
        revenue=("amount", "sum"),
        trips=("order_id", "count"),
    )
)

chunked = (
    partial_results
    .groupby("country", as_index=False)
    .agg(
        revenue=("revenue", "sum"),
        trips=("trips", "sum"),
    )
)
```

Then normalize ordering:

```python
expected = (
    full.sort_values("country")
    .reset_index(drop=True)
)

actual = (
    chunked.sort_values("country")
    .reset_index(drop=True)
)

pd.testing.assert_frame_equal(
    expected,
    actual,
)
```

This is a critical testing pattern for chunked systems.

---

# SECTION H — CHUNKED WRITING

## 53. CSV Writing — Header Once

```python
from pathlib import Path

final_path = Path("clean_orders.csv")
temp_path = Path("clean_orders.csv.tmp")

if temp_path.exists():
    temp_path.unlink()

header = True

for chunk in pd.read_csv(
    "orders.csv",
    chunksize=100_000,
):
    clean = clean_orders(chunk)

    clean.to_csv(
        temp_path,
        mode="a",
        header=header,
        index=False,
    )

    header = False

temp_path.replace(final_path)
```

The header is written exactly once.

- chunks are appended to the temporary file, not the final file;
- a stale temporary file is removed before starting;
- the final output is replaced only after the complete run succeeds;
- therefore a failed run does not partially append to the committed output;
- a rerun does not double the final dataset.

---

## 54. The Repeated-Header Bug

Wrong:

```python
for chunk in pd.read_csv(
    "orders.csv",
    chunksize=100_000,
):
    chunk.to_csv(
        "clean_orders.csv",
        mode="a",
        header=True,
        index=False,
    )
```

Potential result:

```text
order_id,country,amount
1,IN,100
2,US,200
order_id,country,amount
3,IN,150
```

That is not one clean logical table.

---

## 55. CSV Failure and Retry Semantics

Appending directly to the final file creates questions:

- What if chunk 7 fails?
- Is the output complete or partial?
- What if the job is retried?
- Will retry append duplicate rows?

Therefore:

> **Chunking controls memory. It does not automatically solve output correctness.**

When possible, use a temporary output followed by a validation and publish/replace step appropriate to the storage system.

---

## 56. One Parquet File per Chunk

A simple pattern:

```python
from pathlib import Path

output_dir = Path("clean_parts")
output_dir.mkdir(exist_ok=True)

for i, chunk in enumerate(
    pd.read_csv("orders.csv", chunksize=100_000)
):
    clean = clean_orders(chunk)

    clean.to_parquet(
        output_dir / f"part-{i:05d}.parquet",
        index=False,
    )
```

This avoids accumulating all cleaned data in RAM.

But it may create too many files.

---

## 57. The Small-File Problem

Suppose:

```text
1,000,000 input rows
chunksize = 100
```

You may create:

```text
10,000 output files
```

That can create:

- filesystem metadata overhead;
- object-store request overhead;
- downstream discovery overhead;
- query-planning overhead.

Therefore output file sizing is an architectural decision.

---

## 58. `pyarrow.parquet.ParquetWriter`

PyArrow can stream multiple tables into one Parquet file.

```python
import pyarrow as pa
import pyarrow.parquet as pq

writer = None

try:
    for chunk in pd.read_csv(
        "orders.csv",
        chunksize=100_000,
    ):
        clean = clean_orders(chunk)

        table = pa.Table.from_pandas(
            clean,
            preserve_index=False,
        )

        if writer is None:
            writer = pq.ParquetWriter(
                "clean_orders.parquet",
                table.schema,
            )

        writer.write_table(table)
finally:
    if writer is not None:
        writer.close()
```

PyArrow documents `ParquetWriter` as a way to write multiple tables/row groups into one Parquet file. 

---

## 59. Writer Lifecycle

Think:

```text
create writer
    ↓
write table 1
    ↓
write table 2
    ↓
write table 3
    ↓
close writer
```

Production considerations:

- schema must stay compatible;
- the writer must be closed;
- failure handling must be deliberate;
- temporary output should be distinguishable from committed output.

The Arrow documentation demonstrates using a context manager around `ParquetWriter`, which is a clean pattern for resource lifetime. 

---

# SECTION I — CHUNK-BOUNDARY BUGS

## 60. The Core Question: Can Each Chunk Stand Alone?

Classify operations.

```text
Independent row operations
        ↓
usually safe per chunk

Mergeable aggregates
        ↓
partial state + final combine

Stateful operations
        ↓
carry state between chunks

Global operations
        ↓
may defeat simple chunking
```

This classification is one of the most valuable production habits in the topic.

---

## 61. Deduplication Within a Chunk Is Not Global Deduplication

Suppose:

```text
Chunk 1
order_101
order_102

Chunk 2
order_102
order_103
```

Then:

```python
chunk = chunk.drop_duplicates("order_id")
```

only sees duplicates inside the current chunk.

It cannot know that `order_102` existed in a previous chunk.

---

## 62. Cross-Chunk Deduplication with `seen_ids`

A simple exact strategy:

```python
seen_ids = set()

for chunk in pd.read_csv(
    "orders.csv",
    chunksize=100_000,
):
    is_new = ~chunk["order_id"].isin(seen_ids)
    new_rows = chunk.loc[is_new].drop_duplicates("order_id")

    seen_ids.update(
        new_rows["order_id"].tolist()
    )

    process(new_rows)
```

This can be correct when:

- `order_id` is truly the deduplication key;
- first-seen semantics are acceptable;
- the set can fit in memory.

---

## 63. The `seen_ids` State Can Become the Memory Problem

If there are hundreds of millions of unique IDs, the state itself may become too large.

This produces an important insight:

> **Chunking can move the memory problem from the data rows to the algorithmic state.**

Possible alternatives include:

- source-side uniqueness;
- sorted input with adjacent-key logic;
- database uniqueness constraints;
- partition-aware design;
- external state;
- specialized approximate structures when exactness is not required.

The correct choice depends on the business contract.

---

## 64. Sessions That Span Chunks

Consider:

```text
Chunk 1
09:00 login
09:10 click

Chunk 2
09:40 click
10:20 logout
```

If a session is defined by a 30-minute inactivity threshold, the first event in Chunk 2 depends on state from Chunk 1.

A naïve design:

```python
for chunk in reader:
    chunk = sessionize(chunk)
```

may incorrectly restart session state at every boundary.

---

## 65. Carrying Session State

The state might be:

```text
user_id
last_event_time
current_session_id
```

Conceptually:

```text
Chunk N
   ↓
last known state
   ↓
Chunk N+1
   ↓
continue sessionization
```

Carry only the minimum state necessary to continue the algorithm.

---

## 66. Rolling Windows Across Chunks

This is another boundary problem.

If you write:

```python
for chunk in reader:
    chunk["rolling_mean"] = (
        chunk["value"].rolling(24).mean()
    )
```

the rolling operation does not know the previous 23 rows from the prior chunk.

The result can therefore be wrong at every boundary.

---

## 67. Carrying Rolling History

For a count-based 24-row window:

```python
history = pd.DataFrame()

for chunk in reader:
    working = pd.concat(
        [history, chunk],
        ignore_index=True,
    )

    working["rolling_mean"] = (
        working["value"]
        .rolling(24)
        .mean()
    )

    output = working.iloc[len(history):]

    history = working.tail(23).copy()

    write(output)
```

Why 23 rows?

For a 24-row window, each new row needs access to the previous 23 rows.

For a time-based window such as `24h`, the required history depends on timestamp spacing, so the state is defined by the time rule rather than by a fixed number of rows.

---

## 68. Chunk-Safe Classification Table

| Operation | Independent per chunk? | Additional state | Key concern |
| --- | --- | --- | --- |
| Column selection | Yes | None | None |
| Type conversion | Yes | None | Validate |
| Row arithmetic | Yes | None | None |
| Simple filtering | Usually | None | Business semantics |
| Sum | Yes, partial | Final aggregate | Add sums |
| Count | Yes, partial | Final aggregate | Add counts |
| Mean | No, not from means | Sum + count | Weighting |
| Min / max | Yes, partial | Final aggregate | Combine extrema |
| Deduplication | No | Seen-key state | State growth |
| Sessions | No | Previous-session state | Boundary continuity |
| Rolling windows | No | Window history | Boundary overlap |
| Global sort | No | Global coordination | Can defeat simple chunking |

---

# SECTION J — PARTITIONED INPUTS AS NATURAL CHUNKS

## 69. Partitioned Data

Sometimes the data is already organized:

```text
data/
    2026-01-01.parquet
    2026-01-02.parquet
    2026-01-03.parquet
    ...
```

or:

```text
data/
    year=2026/
        month=01/
            day=01/
                part-000.parquet
```

These partitions can become natural processing units.

---

## 70. Chunking a File vs Processing Partitions

### Huge single file

```text
one huge file
  ↓
chunk 1
chunk 2
chunk 3
...
```

### Already partitioned data

```text
day 1
  ↓
day 2
  ↓
day 3
  ↓
...
```

Partitioning can improve:

- retry scope;
- monitoring;
- output organization;
- backfills;
- idempotency.

---

## 71. Partition-Level Processing

```python
from pathlib import Path

for path in sorted(
    Path("input").glob("*.parquet")
):
    process_partition(path)
```

One partition can itself be processed with batches if it is still too large.

Therefore:

> **Partitioning and chunking are complementary techniques.**

---

## 72. Why Daily Partitions Are Operationally Useful

If the business process is daily:

```text
partition = business date
```

then the workflow can be:

```text
daily input
   ↓
process
   ↓
validate
   ↓
publish daily output
   ↓
mark complete
```

That creates a useful failure boundary.

---

# SECTION K — IDEMPOTENT RE-RUNS

## 73. What Does Idempotent Mean?

In this context:

> **Running the same partition again should produce the same intended dataset state rather than duplicated output.**

Suppose:

```text
input partition = 2026-09-01
output partition = 2026-09-01
```

If the job fails halfway through, retry should replace or safely re-establish that logical partition rather than append a second copy.

---

## 74. Bad Retry Pattern

Appending blindly:

```python
append_to_output(
    "output/2026-09-01.parquet"
)
```

can create duplicate logical records after retry.

---

## 75. Safer Temporary-Then-Publish Pattern

Conceptually:

```python
from pathlib import Path

final_path = Path("output/2026-09-01.parquet")
temp_path = Path("output/.2026-09-01.tmp.parquet")

write_partition(temp_path)
validate_partition(temp_path)
temp_path.replace(final_path)
```

The exact atomicity and overwrite semantics depend on the filesystem or object store.

The architectural sequence is:

```text
write temporary
    ↓
validate
    ↓
commit / replace
```

---

## 76. Deterministic Output Paths

Prefer business-meaningful paths such as:

```text
output/date=2026-09-01/
```

or:

```text
output/2026-09-01.parquet
```

when the partition is the logical unit.

Deterministic paths simplify:

- retries;
- backfills;
- validation;
- monitoring;
- downstream discovery.

---

# SECTION L — FREEING MEMORY

## 77. Chunk Lifetime

A good loop minimizes retained references:

```python
for chunk in reader:
    processed = process(chunk)
    write(processed)
```

After the iteration, objects become eligible for cleanup when no references remain.

---

## 78. `del`

You can remove a reference explicitly:

```python
del chunk
del processed
```

`del` removes a Python name/reference.

It does **not** mean:

> “Return exactly these bytes to the operating system immediately.”

---

## 79. Python Object Lifetime vs Allocator vs OS

Think in three layers:

```text
Python object lifetime
        ↓
allocator / library memory management
        ↓
OS-visible process memory (RSS)
```

An object can become unreachable while the process keeps memory in its allocator for later reuse.

Therefore:

```text
del chunk
```

does not guarantee:

```text
RSS drops immediately
```

---

## 80. `gc.collect()`

Python lets you request garbage collection:

```python
import gc

gc.collect()
```

But do not call this after every chunk automatically.

It can add overhead and is not a substitute for:

- avoiding unnecessary references;
- reducing retained state;
- keeping chunks small enough;
- writing/aggregating incrementally.

Use manual collection only when measurement shows a reason.

---

# SECTION M — PEAK MEMORY VS FINAL MEMORY

## 81. Why Final Size Is Insufficient

Suppose:

```text
final result = 100 MB
```

but the pipeline temporarily creates:

```text
900 MB intermediate
```

A machine with only 512 MB of usable memory still fails.

Therefore track:

- current chunk memory;
- temporary working memory;
- process RSS;
- peak RSS;
- final output memory.

---

## 82. Linux RSS Experiment

In Linux/WSL, a simple process-level helper can inspect `/proc/self/status`:

```python
from pathlib import Path


def rss_kb() -> int:
    for line in Path("/proc/self/status").read_text().splitlines():
        if line.startswith("VmRSS:"):
            return int(line.split()[1])
    return 0


print("RSS:", rss_kb(), "KB")
```

This is process-level memory, not DataFrame-only memory.

---

## 83. Measuring Around a Chunk

```python
print("before:", rss_kb(), "KB")

for chunk in pd.read_csv(
    "large.csv",
    chunksize=100_000,
):
    print("loaded:", rss_kb(), "KB")

    process(chunk)

    print("processed:", rss_kb(), "KB")
```

A real benchmark should use representative data and should not rely on a single noisy observation.

To measure the peak of a whole chunked run, `tracemalloc` can record the maximum traced allocation:

```python
import tracemalloc

tracemalloc.start()

for chunk in pd.read_csv(
    "large.csv",
    chunksize=100_000,
):
    process(chunk)

current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(
    {
        "current_traced_bytes": current,
        "peak_traced_bytes": peak,
    }
)
```

`peak` is the maximum memory traced by `tracemalloc` during the measured interval. That is different from whole-process RSS, which also includes memory the tracer does not see. Run the measurement on representative data, and record the numbers you actually observe; never fabricate benchmark results.

---

# SECTION N — STOP CONDITIONS: WHEN PANDAS IS THE WRONG TOOL

## 84. “Can” vs “Should”

Pandas can sometimes technically process data much larger than RAM through careful chunking.

That does not mean it is always the right architecture.

Warning signs include:

- data several times larger than RAM;
- sustained multi-core requirements;
- many large joins;
- state that is too large for one machine;
- distributed processing requirements;
- increasingly complex coordination logic.

---

## 85. High-Level Tool Comparison

| Tool | Why it may be considered |
| --- | --- |
| pandas | Single-machine DataFrame processing |
| Polars | High-performance columnar DataFrame workflows |
| DuckDB | Local analytical SQL / columnar processing |
| Dask | Parallel/distributed Python DataFrame-style workflows |
| Spark | Large-scale distributed data processing |

The roadmap points to:

- **Polars and DuckDB → Module 2.4**;
- **Spark → Module 2.14**;
- **Dask → Module 2.21**.

This chapter does not teach those engines in depth. It teaches when to evaluate them.

---

## 86. Tool Decision Framework

```text
Does the dataset fit comfortably in RAM?
        ↓
      YES
        ↓
Is pandas fast enough?
        ↓
      YES → use pandas
```

If not:

```text
Can projection + dtype optimization + chunking solve it?
        ↓
      YES → optimize pandas
        ↓
      NO
        ↓
Evaluate a larger engine
```

Possible next questions:

```text
local columnar analytics?
    → evaluate DuckDB / Polars

parallel Python data processing?
    → evaluate Dask

large distributed computation?
    → evaluate Spark
```

Tool choice depends on:

- data size;
- workload shape;
- latency requirements;
- CPU parallelism;
- deployment environment;
- team expertise;
- operational complexity.

---

# 87. MEMORY OPTIMIZATION PLAYBOOK

```text
1. Measure
        ↓
2. Read less
        ↓
3. Choose better dtypes
        ↓
4. Drop unused columns
        ↓
5. Filter early when semantically valid
        ↓
6. Chunk the input
        ↓
7. Aggregate partial results
        ↓
8. Carry only required state
        ↓
9. Write incrementally
        ↓
10. Make outputs idempotent
        ↓
11. Measure peak memory
        ↓
12. Re-evaluate engine choice
```

---

## 88. Playbook Step 1 — Measure

Ask:

> Which columns, operations, and intermediate objects create the memory problem?

Use:

```python
df.info(memory_usage="deep")
```

and:

```python
df.memory_usage(
    index=False,
    deep=True,
)
```

---

## 89. Playbook Step 2 — Read Less

Use:

- `usecols`;
- `dtype`;
- `nrows` for exploration;
- Parquet `columns=`;
- Parquet `filters=`.

---

## 90. Playbook Step 3 — Choose Better Dtypes

Consider:

- downcasting;
- category;
- Arrow-backed strings;
- compact numeric types.

Validate before accepting the optimization.

---

## 91. Playbook Step 4 — Drop Unused Columns

Reduce DataFrame width as early as practical.

```text
wide
  ↓
project required fields
  ↓
narrow working set
```

---

## 92. Playbook Step 5 — Filter Early

If a filter safely removes rows before expensive work:

```python
chunk = chunk.loc[
    chunk["country"].eq("IN")
]
```

But do not remove rows that later calculations need.

---

## 93. Playbook Step 6 — Chunk

```python
for chunk in pd.read_csv(
    "large.csv",
    chunksize=100_000,
):
    process(chunk)
```

Tune the chunk size experimentally.

---

## 94. Playbook Step 7 — Aggregate Partial Results

Use compact mergeable statistics instead of retaining raw rows.

```text
raw rows
  ↓
partial aggregate
  ↓
small state
```

---

## 95. Playbook Step 8 — Carry Minimum State

Examples:

```text
deduplication → seen keys
sessions      → last relevant state
rolling       → window history
```

Do not carry more historical data than necessary.

---

## 96. Playbook Step 9 — Write Incrementally

Write:

- cleaned chunks;
- compact partials;
- partitions.

Do not wait until the end if the output itself would exceed available memory.

---

## 97. Playbook Step 10 — Idempotent Outputs

Use:

- deterministic partition paths;
- temporary files;
- validation;
- safe publish/replace semantics.

---

## 98. Playbook Step 11 — Measure Peak Memory

Measure the process where necessary, not only the final DataFrame.

---

## 99. Playbook Step 12 — Re-Evaluate Engine Choice

When the architecture becomes dominated by:

```text
large joins
+ large state
+ high parallelism
+ distributed requirements
```

stop asking “How do I make this pandas loop more complicated?” and ask whether the execution engine should change.

---

# 100. Decision Table

| Problem | Technique | Main trade-off |
| --- | --- | --- |
| Too many columns | `usecols` / projection | Required fields must be known |
| Exploration needs only sample | `nrows` | Not full-data validation |
| Over-wide numeric types | `dtype` / downcasting | Overflow / precision risk |
| Repeated low-cardinality strings | `category` | Poor fit for high cardinality |
| String-heavy workload | Arrow-backed strings | Backend/API compatibility varies |
| Huge CSV | `chunksize` | More pipeline logic |
| Huge SQL result | `read_sql(chunksize=...)` | Iterative processing |
| Grouped totals | Partial aggregates | Need correct merge math |
| Huge output | Incremental writes | Retry semantics need design |
| Cross-chunk duplicates | Carried key state | State can grow |
| Cross-chunk sessions | Carried session state | Boundary logic |
| Cross-chunk rolling | Carried history | Window complexity |
| Daily partitions | Process partition-by-partition | Partition-aware retries needed |
| Retry safety | Idempotent partition writes | Explicit commit strategy |
| Data far beyond one machine | Larger engine | More infrastructure/complexity |

---

# 101. Safe-Per-Chunk Mental Model

Ask for every algorithm:

```text
Can this row be processed without history?
        ↓
      YES → likely chunk-safe
        ↓
      NO
        ↓
What minimum state is required?
        ↓
Can that state remain bounded?
        ↓
      YES → carry it
        ↓
      NO → reconsider the algorithm or engine
```

---

# 102. Hands-On Learning Method

The roadmap specifies two core activities.

## Exercise 1 — Memory Reduction Lab

Take one realistic DataFrame and try to reduce in-memory size by **at least 70% through typing alone**.

Record:

```text
baseline memory
↓
after numeric dtype changes
↓
after categorical changes
↓
after string backend changes where appropriate
↓
final memory
↓
measured reduction percentage
```

Important:

> The 70% target is an exercise target, not a universal property of every dataset.

If your real dataset cannot safely achieve 70%, document why.

---

## Exercise 2 — Full Load vs Chunked

Take a test-sized aggregation that fits in memory.

Implement it in two ways:

```text
full load
vs
chunked partial aggregation
```

Then prove:

```text
full-load result == chunked result
```

Use `pandas.testing.assert_frame_equal()` after normalizing row order and dtypes where necessary.

---

# 103. Hands-On Exercise — `big_file_pipeline.py`

> **Exercise specification only:** create this Python file in your project when you are ready to implement it. This chapter does not create the file, test files, datasets, or supporting files.

## Objective

Build a production-style memory-aware pandas pipeline on a CSV larger than a comfortable fraction of available RAM.

Suggested inputs:

- several years of NYC taxi-style trip data; or
- generated data in the 5–10 GB range.

The machine must have enough free resources to run the chosen experiment safely.

---

## Step 1 — Read with `usecols` and Explicit Compact Dtypes

At minimum identify fields similar to:

```text
trip_id
pickup_datetime
payment_type
fare_amount
country
```

A starting pattern:

```python
reader = pd.read_csv(
    "large_trips.csv",
    chunksize=100_000,
    usecols=[
        "trip_id",
        "pickup_datetime",
        "payment_type",
        "fare_amount",
        "country",
    ],
    dtype={
        "trip_id": "int64",
        "payment_type": "category",
        "fare_amount": "float32",
        "country": "category",
    },
)
```

Choose the actual dtypes from the source contract.

For each chunk record:

- row count;
- dtypes;
- DataFrame memory.

---

## Step 2 — Daily Trip Counts, Revenue, and Average Fare

Produce metrics by:

```text
date
payment_type
```

Required outputs:

- trip count;
- revenue;
- average fare.

Do not use:

```text
average(chunk averages)
```

Instead retain:

```text
fare_sum
fare_count
```

and derive:

```text
average_fare = fare_sum / fare_count
```

---

## Step 3 — Deduplicate Across Chunk Boundaries

Carry a set of seen trip keys:

```python
seen_trip_ids = set()
```

The exercise must document:

- why per-chunk deduplication is insufficient;
- what first-seen semantics mean;
- how the set grows;
- when that approach stops being practical.

---

## Step 4 — Write Monthly Parquet Output

Target a partitioned shape such as:

```text
output/
    month=2026-01/
        data.parquet
    month=2026-02/
        data.parquet
    ...
```

or another equivalent one-file-per-month layout.

Document how multiple months inside one input chunk are split.

---

## Step 5 — Compare Runtime and Peak Memory

Compare a naïve full-load approach and the chunked approach using a subset that fits safely in memory.

Record:

```text
runtime
peak memory
final output size
throughput
```

Controls:

- same input subset;
- same transformation logic;
- same machine;
- same software versions;
- equivalent output validation.

Never fabricate benchmark values.

---

## Step 6 — Engine-Choice Note

Write a short engineering note:

> When would you stop optimizing pandas and evaluate Polars or DuckDB?

Base the note on:

- measured runtime;
- measured peak memory;
- data size;
- join complexity;
- parallelism requirements;
- operational complexity.

---

## Exercise Input Schema

| Column | Example | Meaning |
| --- | --- | --- |
| `trip_id` | `123456` | Unique trip identifier |
| `pickup_datetime` | `2026-09-01 10:15:00` | Event timestamp |
| `payment_type` | `card` | Low-cardinality payment code |
| `fare_amount` | `12.50` | Fare amount |
| `country` | `IN` | Low-cardinality country code |

Adapt this schema when using a different source dataset.

---

## Exercise Output Schema

| Column | Meaning |
| --- | --- |
| `date` | Reporting date |
| `payment_type` | Payment category |
| `trip_count` | Accepted trip count |
| `revenue` | Total fare amount |
| `average_fare` | Correct combined average |

---

## Exercise Assumptions

Document:

- timestamp semantics;
- duplicate-key definition;
- null handling;
- invalid-record policy;
- numeric precision;
- chunk size;
- partition layout;
- retry behavior.

---

## Acceptance Criteria

```text
[ ] Baseline memory measured
[ ] Required columns projected
[ ] Explicit dtypes documented
[ ] Chunk size selected experimentally
[ ] Daily trip counts correct
[ ] Daily revenue correct
[ ] Average fare mathematically correct
[ ] Cross-chunk duplicates handled
[ ] Monthly Parquet output created
[ ] Retry behavior documented
[ ] Full-load and chunked results reconciled
[ ] Peak memory measured
[ ] Runtime measured
[ ] Engine-choice note written
```

---

# 104. Correctness Testing Strategy

## Aggregation Correctness

```python
pd.testing.assert_frame_equal(
    expected.sort_values(keys).reset_index(drop=True),
    actual.sort_values(keys).reset_index(drop=True),
)
```

The expected result should come from a trusted full-load implementation on test-sized data.

---

## Row-Level Correctness

For transformations that preserve row count:

```python
assert len(before) == len(after)
```

For filters, document expected reduction instead.

---

## Duplicate Handling

Construct an explicit boundary test:

```text
Chunk 1
A
B

Chunk 2
B
C
```

If the contract is first-seen deduplication, expected accepted keys are:

```text
A
B
C
```

---

## Average Arithmetic

Test unequal chunk sizes.

Expected:

```text
Chunk 1: count 10, mean 10
Chunk 2: count 2, mean 20
Global: 11.666...
```

This catches mean-of-means errors.

---

## Boundary Correctness

Test:

- duplicate across chunks;
- session starts in one chunk and ends in another;
- rolling window crosses a boundary;
- date/month changes in a chunk;
- partition retries.

---

## Output Correctness

Verify:

- expected partitions exist;
- schema is consistent;
- no duplicate permanent outputs;
- row counts reconcile.

---

## Memory Correctness

Record:

- maximum observed chunk memory;
- peak process memory;
- carried-state size.

Do not assert fragile exact runtime thresholds in unit tests.

---

# 105. Debugging Chunked Pipelines

Use this structure:

> **Bug → expected behavior → actual behavior → root cause → corrected design → prevention rule**

## Problem 1 — Memory Keeps Growing

Typical investigation:

- `chunks.append(...)`;
- accumulated DataFrames;
- global lists;
- retained references;
- oversized partial results;
- growing `seen_ids` state;
- accidental copies.

A suspicious pattern:

```python
all_results = []

for chunk in reader:
    all_results.append(process(chunk))
```

Correct question:

> Can each result be reduced or written before the next chunk is processed?

---

## Problem 2 — Final Averages Are Wrong

Check:

- average-of-averages;
- sum/count mismatch;
- null filtering differences;
- inconsistent denominators.

Correct pattern:

```text
partial sum + partial count
→ final sum + final count
→ final mean
```

---

## Problem 3 — Duplicates Remain

Check:

- `drop_duplicates()` only inside each chunk;
- missing cross-chunk state;
- inconsistent keys;
- key normalization problems;
- state reset on every iteration.

---

## Problem 4 — Rolling Values Are Wrong at Boundaries

Check:

- previous-row/history state;
- timestamp sorting;
- count-based vs time-based window;
- insufficient carried history.

---

## Problem 5 — Sessions Restart Every Chunk

Check:

- last event state;
- current session state;
- user-level continuity.

---

## Problem 6 — CSV Contains Repeated Headers

Check:

```python
header=True
```

inside every append operation.

Use header-once logic.

---

## Problem 7 — `del` Does Not Lower RSS

Possible explanation:

```text
Python object becomes unreachable
        ↓
memory becomes reusable
        ↓
allocator may keep memory
        ↓
RSS can remain high
```

This does not automatically mean a memory leak.

---

# 106. Edge Cases

## Empty chunks

Test that the pipeline keeps a valid schema and does not create invalid output.

## Final chunk smaller than `chunksize`

Never assume all chunks are equal-sized.

## Malformed records

Define whether they are rejected, quarantined, corrected, or fatal.

## Missing keys

Define the null-key deduplication policy.

## Duplicate keys

Test duplicates within one chunk and across two chunks.

## Null group keys

Define whether missing group keys are valid business data.

## Integer overflow

Test values near dtype limits.

## Float precision

Test representative numerical values and tolerances.

## High-cardinality categories

Measure before converting.

## Inconsistent schemas

Validate partition/file schemas explicitly.

## Interrupted output

Determine whether partial output is discoverable as uncommitted.

## Rerun of an existing partition

Verify idempotency.

## Duplicate input files

Validate source discovery.

## Out-of-order timestamps

Stateful and rolling logic may require sorting.

## Rolling windows across boundaries

Carry sufficient history.

## Sessions across boundaries

Carry sufficient session state.

## Very large state sets

Treat state as a resource with its own memory budget.

## Output filesystem limits

Consider file counts, object-store behavior, and commit semantics.

---

# 107. Performance Engineering

## Chunk Size

Trade:

```text
memory
↔
throughput
```

There is no universal optimum.

---

## Parsing Overhead

Very small chunks can increase loop and parsing overhead.

---

## CPU Utilization

Chunking does not automatically create parallelism.

A loop over chunks is still a loop.

If CPU parallelism becomes a requirement, evaluate an engine designed for it.

---

## Expensive Groupby

Reduce rows and columns before groupby when semantically safe.

High-cardinality grouping keys can also increase memory.

---

## Avoiding Unnecessary `concat`

Safe:

```text
many chunks
    ↓
small partial aggregates
    ↓
concat partials
```

Potentially unsafe:

```text
many chunks
    ↓
retain all processed rows
    ↓
concat all data
```

---

## Writing Too Many Tiny Files

Chunking can reduce RAM while increasing file-management cost.

The output layout must balance:

- file size;
- partition count;
- downstream access pattern;
- retry granularity.

---

## Benchmarking

Use:

```python
from time import perf_counter

start = perf_counter()
run_pipeline()
elapsed = perf_counter() - start

print(f"Elapsed: {elapsed:.3f}s")
```

For memory, use DataFrame accounting plus an appropriate process-level method.

Do not fabricate results.

---

# 108. Production Data Engineering Use Cases

## Daily Bank Transaction Processing

### Input

Millions of transactions per day.

### Problem

Historical backfill may exceed RAM.

### Approach

```text
daily partition
→ chunk
→ validate
→ transform
→ aggregate
→ output
```

### State

Potentially transaction-ID deduplication and account-level continuity.

### Correctness

Reconcile totals and transaction counts.

### Trade-off

Partitioning improves retry scope, but cross-day calculations may require additional state.

---

## E-Commerce Orders

### Input

Years of order history.

### Approach

- projection;
- compact dtypes;
- chunked ingestion;
- partial revenue aggregation;
- monthly Parquet output.

### Correctness

Reconcile revenue and order counts against a test-sized full-load result.

---

## Application Logs

### Input

Very large log export.

### Approach

- project required fields;
- parse only required information;
- filter early;
- aggregate error/status counts;
- write compact output.

---

## Customer Events

### Input

High-volume event stream export.

### Challenge

Sessionization crosses chunk boundaries.

### Approach

Carry minimum per-user state.

---

## Financial Data

Key concerns:

- monetary precision;
- duplicate records;
- exact aggregation;
- partition retries;
- auditability.

---

## ETL Backfill

A practical pattern:

```text
partition
→ process
→ validate
→ publish
→ mark complete
```

This narrows the retry scope.

---

# 109. Anti-Patterns to Avoid

## Anti-Pattern 1 — Load 20 GB into a 4 GB Machine

```python
df = pd.read_csv("20GB.csv")
```

Why it fails:

- full materialization;
- parsing overhead;
- temporary memory.

Better:

- project;
- dtype;
- chunk;
- or change engine.

---

## Anti-Pattern 2 — Keep All Chunks

```python
chunks = []

for chunk in reader:
    chunks.append(process(chunk))
```

Why it fails:

The processed data remains live.

---

## Anti-Pattern 3 — Average Chunk Means

```text
mean(chunk 1)
mean(chunk 2)
mean(chunk 3)
↓
mean of these means
```

Why it fails:

Chunk sizes can differ.

---

## Anti-Pattern 4 — Deduplicate Only Within Each Chunk

Why it fails:

A duplicate in another chunk remains invisible.

---

## Anti-Pattern 5 — Ignore Boundary State

Why it fails:

Sessions and rolling windows reset at chunk boundaries.

---

## Anti-Pattern 6 — Write Header Every Time

Why it fails:

The CSV structure becomes invalid as one logical table.

---

## Anti-Pattern 7 — Let State Grow Without a Budget

Why it fails:

The state itself can exceed the available memory.

---

## Anti-Pattern 8 — Force Pandas Beyond the Architecture

Why it fails:

A growing web of Python state and manual coordination can become harder to operate than a fit-for-purpose analytical/distributed engine.

---

# 110. Real-World Architecture Example

```text
Raw / partitioned input
        ↓
Required-column projection
        ↓
Explicit dtypes
        ↓
Chunked processing
        ↓
Validation / cleansing
        ↓
Chunk-level aggregation
        ↓
Carry minimum state
        ↓
Partitioned Parquet output
        ↓
Output validation
        ↓
Idempotent commit
        ↓
Monitoring / metrics
```

---

## 111. Scale-Based Variants

### Data comfortably fits RAM

Use normal pandas processing if it is simple and fast enough.

### Data approaches RAM limits

Use projection, dtype optimization, measured chunking, and peak-memory tracking.

### Data is many times larger than RAM

Chunking may work for composable algorithms, but state and global operations become architectural constraints.

### Distributed execution is required

Evaluate a larger execution engine.

---

# 112. What Is Safe to Do Per Chunk?

| Operation | Independent per chunk? | Additional state? | Notes |
| --- | --- | --- | --- |
| Column selection | Yes | No | Safe |
| Type conversion | Yes | No | Validate |
| Row arithmetic | Yes | No | Safe |
| Simple filter | Usually | No | Confirm semantics |
| Sum | Yes, partial | Final aggregate | Add partial sums |
| Count | Yes, partial | Final aggregate | Add counts |
| Min | Yes, partial | Final aggregate | Combine minima |
| Max | Yes, partial | Final aggregate | Combine maxima |
| Mean | Not from chunk means | Sum + count | Critical |
| Deduplication | No | Seen keys | State growth |
| Sessions | No | Previous session state | Boundary |
| Rolling | No | History | Boundary |
| Global sort | No | Global coordination | Often defeats simple chunking |
| Exact median | No simple partial median | Distribution state | Complex |

---

# 113. Seven Mental Models

## Mental Model 1 — RAM Is the Scarce Resource

Think about the working set, not merely the file size.

## Mental Model 2 — Read Less First

Do not allocate for data you will immediately discard.

## Mental Model 3 — A Chunk Is a Temporary Working Set

The goal is to keep its lifetime short.

## Mental Model 4 — Carry Minimum State

State is also memory.

## Mental Model 5 — Chunking Changes Organization, Not Mathematics

The chunked result should reconcile to the full-load result on test data.

## Mental Model 6 — Peak Memory Matters

Final DataFrame size is not enough.

## Mental Model 7 — State Can Outgrow the Data Chunk

A `seen_ids` set, session map, or other global state can become the new bottleneck.

---

# 114. Interview Questions

## 1. Why is CSV file size different from DataFrame memory?

Because CSV is a serialized text representation, while DataFrame memory includes decoded values, indexes, object/string storage, metadata, and temporary processing structures.

## 2. How would you process a 20 GB CSV on a 4 GB machine?

A strong answer includes projection, intentional dtypes, chunked reading, incremental aggregation/output, bounded state, peak-memory measurement, and an engine-choice decision if the design remains impractical.

## 3. Why does `chunksize` reduce memory?

It limits how much input is materialized as the active DataFrame at once.

## 4. How do you calculate a global mean across chunks?

Keep sum and count and compute `total_sum / total_count`.

## 5. Why does per-chunk `drop_duplicates()` fail for global deduplication?

Because it cannot see duplicate keys in other chunks.

## 6. How do rolling windows cross chunk boundaries?

They require sufficient history from the preceding chunk.

## 7. What if carried state becomes huge?

Redesign the algorithm, move state externally, change partitioning, push work upstream, or evaluate a different engine.

## 8. How do you make a partition retry-safe?

Use deterministic output paths, temporary output, validation, and safe publish/replace semantics.

## 9. Why might `del chunk` not lower RSS immediately?

The Python object can be released while its allocator or a library retains memory for reuse.

## 10. How do you measure peak memory?

Use DataFrame memory accounting and a process-level peak-memory measurement appropriate to the environment.

## 11. When would you consider Polars or DuckDB?

When single-machine pandas is no longer meeting memory/performance requirements and the workload fits a local columnar/analytical engine better.

## 12. When would you consider Dask or Spark?

When parallel/distributed execution requirements exceed a practical single-machine pandas design.

## 13. Why can `pd.concat(all_chunks)` defeat chunking?

Because it retains all processed rows before final concatenation.

## 14. What if chunks have inconsistent schemas?

The pipeline can fail or silently create unexpected columns/coercions; validate schema explicitly.

## 15. How do you benchmark fairly?

Use equivalent inputs and logic, control the environment, measure runtime and peak memory, and repeat representative runs.

---

# 115. Architecture Thinking

## Scenario A — 50 GB CSV, 16 GB RAM

Reason about:

- projection;
- dtypes;
- chunk size;
- per-chunk operations;
- output strategy;
- peak memory.

## Scenario B — Daily Revenue from Multi-Year Data

Design:

```text
partition
→ chunk if necessary
→ partial aggregate
→ final aggregate
→ output
```

## Scenario C — Duplicates Across Chunks

Decide:

- dedup key;
- ordering semantics;
- state structure;
- state memory budget;
- external/source-side alternatives.

## Scenario D — Rolling 24-Hour Metrics

Decide:

- timestamp ordering;
- time-based window semantics;
- retained history;
- late events;
- whether chunking remains operationally sensible.

## Scenario E — Retry After Partial Output

Decide:

- deterministic partition path;
- temporary output;
- validation;
- replacement semantics;
- completion state.

---

# 116. Predict Before Running

Before executing important examples, predict:

- peak memory direction;
- chunk output row count;
- whether the algorithm is chunk-safe;
- whether state is required;
- whether the aggregate math is correct;
- whether a retry can duplicate output.

Then use:

```text
Prediction
    ↓
Execution
    ↓
Inspection
    ↓
Assertion
    ↓
Explanation
```

---

## 117. Prediction Exercise Set

### Prediction 1

If you remove 45 of 50 columns before a groupby, what should happen to the working-set size?

### Prediction 2

If a filter removes 90% of rows before an expensive aggregation, what should happen to later work?

### Prediction 3

Can `sum` be aggregated independently per chunk?

### Prediction 4

Can `mean` be aggregated independently by taking the mean of chunk means?

### Prediction 5

Can `drop_duplicates()` on each chunk guarantee global deduplication?

### Prediction 6

Does a 24-row rolling window need history from the previous chunk?

### Prediction 7

Does `del chunk` guarantee an immediate RSS drop?

### Prediction 8

Will writing every 100-row chunk create an operationally reasonable number of files?

### Prediction 9

Can a huge `seen_ids` set itself become the memory bottleneck?

### Prediction 10

Will a retried append-only partition necessarily remain idempotent?

---

# 118. Mini Examples Reference

## Memory measurement

```python
df.info(memory_usage="deep")
df.memory_usage(index=False, deep=True)
```

## Column projection

```python
pd.read_csv(
    "orders.csv",
    usecols=["order_id", "amount"],
)
```

## Explicit dtype

```python
pd.read_csv(
    "orders.csv",
    dtype={
        "quantity": "int16",
        "country": "category",
    },
)
```

## Controlled sample

```python
pd.read_csv(
    "orders.csv",
    nrows=10_000,
)
```

## Parquet columns

```python
pd.read_parquet(
    "orders.parquet",
    columns=["order_id", "amount"],
)
```

## Parquet filters

```python
pd.read_parquet(
    "orders.parquet",
    columns=["order_id", "amount"],
    filters=[("country", "==", "IN")],
)
```

## Numeric downcasting

```python
pd.to_numeric(
    series,
    downcast="integer",
)
```

## Category

```python
series.astype("category")
```

## Arrow strings

```python
pd.Series(
    ["IN", "US", None],
    dtype="string[pyarrow]",
)
```

## Chunked CSV

```python
pd.read_csv(
    "large.csv",
    chunksize=100_000,
)
```

## Iterator mode

```python
reader = pd.read_csv(
    "large.csv",
    iterator=True,
)
chunk = reader.get_chunk(100_000)
```

## Chunked SQL

```python
pd.read_sql(
    query,
    connection,
    chunksize=100_000,
)
```

## Partial aggregate

```python
partial = (
    chunk.groupby("country", as_index=False)
    .agg(
        revenue=("amount", "sum"),
        trips=("order_id", "count"),
    )
)
```

## Chunked CSV append

```python
clean.to_csv(
    output_path,
    mode="a",
    header=header,
    index=False,
)
```

## Chunked Parquet

```python
clean.to_parquet(
    output_path,
    index=False,
)
```

## ParquetWriter

```python
writer.write_table(table)
writer.close()
```

## Carried deduplication state

```python
seen_ids = set()
seen_ids.update(new_ids)
```

## Carried rolling history

```python
history = working.tail(window_size - 1).copy()
```

## Release reference

```python
del chunk
```

---

# 119. Reusable Production Checklist

## Input

- [ ] Source format documented
- [ ] Required columns known
- [ ] `usecols` used where appropriate
- [ ] `dtype` choices documented
- [ ] `nrows` limited to exploration/testing
- [ ] Parquet `columns=` considered
- [ ] Parquet `filters=` considered

## Memory

- [ ] Baseline memory measured
- [ ] Per-column memory inspected
- [ ] Peak memory considered
- [ ] Temporary objects considered
- [ ] Retained references reviewed

## Dtypes

- [ ] Downcasting validated
- [ ] Overflow checked
- [ ] Float precision checked
- [ ] Category cardinality justified
- [ ] Arrow-backed strings considered where appropriate

## Chunking

- [ ] Chunk size experimentally selected
- [ ] One input chunk processed at a time
- [ ] All chunks are not retained unnecessarily
- [ ] Partial aggregates are compact
- [ ] Boundary state is explicit

## Correctness

- [ ] Full-load vs chunked reconciliation exists
- [ ] Average math is correct
- [ ] Cross-chunk duplicates tested
- [ ] Session boundaries tested
- [ ] Rolling boundaries tested
- [ ] Output schema validated

## Output

- [ ] CSV header written once
- [ ] Parquet schema is consistent
- [ ] File count is operationally reasonable
- [ ] Output paths are deterministic
- [ ] Partial output is distinguishable from committed output

## Retries

- [ ] Partition reruns are idempotent
- [ ] Temporary output is used where appropriate
- [ ] Validation occurs before publish
- [ ] Completion is observable

## Performance

- [ ] Runtime measured
- [ ] Peak memory measured
- [ ] Chunk size tested
- [ ] Expensive operations identified
- [ ] Engine alternatives considered

---

# 120. Common Mistakes Summary

| Mistake | Why it happens | Correct approach |
| --- | --- | --- |
| Using file size as RAM estimate | Disk and memory are assumed equivalent | Measure actual DataFrame/chunk memory |
| Reading every column | `read_csv()` defaults are convenient | Use `usecols` |
| Blind dtype shrinking | Smaller sounds automatically better | Validate range/precision |
| High-cardinality category | Category is remembered as a generic memory trick | Measure cardinality and memory |
| Keeping all chunks | Code is technically chunked but retains results | Reduce/write incrementally |
| Averaging chunk means | It feels mathematically intuitive | Combine sum + count |
| Deduplicating only within chunks | Each chunk is treated as globally complete | Carry state or redesign |
| Resetting session state | Chunk boundary is mistaken for business boundary | Carry minimum session state |
| Resetting rolling windows | History is discarded | Carry required history |
| Repeating CSV headers | Append logic is written inside loop | Header once |
| Closing ParquetWriter incorrectly | Writer lifecycle ignored | Use `finally` or context manager |
| Creating thousands of tiny files | Chunk size is treated as file size | Separate processing batch size from output layout |
| Assuming `del` returns RSS immediately | Object lifetime is confused with OS memory | Distinguish object, allocator, RSS |
| Unbounded state | State is treated as free | Budget state memory explicitly |
| Ignoring peak memory | Final output looks small | Measure peak working set |
| Treating chunking as automatic parallelism | Iteration is mistaken for concurrency | Evaluate parallel/distributed engines |
| Forcing pandas indefinitely | “It works” becomes the architecture | Re-evaluate the engine |

---

# 121. Checkpoint

The learner must be able to:

## Requirement 1 — Reduce Memory and Measure It

> Reduce a DataFrame's memory with dtype decisions and measure the result.

Evidence should include:

```text
before
→ conversion
→ after
→ reduction percentage
```

## Requirement 2 — Aggregate Data Larger Than Memory

> Aggregate an input larger than available memory with `chunksize`.

Evidence should include:

```text
read chunk
→ process
→ partial aggregate
→ final combine
```

## Requirement 3 — Explain Boundary Risks

> Explain which operations are unsafe across chunk boundaries.

At minimum:

- deduplication;
- sessions;
- rolling windows;
- global sort;
- large global state.

## Requirement 4 — Know When Pandas Is No Longer the Right Tool

> Explain when pandas should be replaced or supplemented by another execution engine.

A strong answer considers:

- RAM;
- workload shape;
- multi-core requirements;
- join complexity;
- state size;
- distributed execution needs.

### Practical checkpoint prompt

> **You are given a CSV larger than RAM. Explain the architecture before writing code.**

Your answer should include:

```text
projection
→ dtypes
→ chunk size
→ transformation
→ state
→ aggregation
→ output
→ idempotency
→ validation
→ peak memory
→ engine choice
```

---

# 122. Interview / Architecture Deep-Dive Questions

1. Why can a CSV that is 3 GB on disk require substantially more RAM in pandas?
2. What is the difference between DataFrame memory and process RSS?
3. Why can a groupby cause peak memory to exceed chunk memory?
4. Why is `usecols` often more valuable than a micro-optimization after loading?
5. How do you choose a safe downcast?
6. Why is category most useful for low-cardinality repeated values?
7. Why does `chunksize` control memory but not automatically guarantee bounded memory?
8. When is `iterator=True` preferable to a simple `chunksize` loop?
9. Why can `pd.concat(all_processed_chunks)` defeat chunking?
10. Which aggregations are naturally mergeable?
11. How would you compute a weighted average across chunks?
12. How would you deduplicate across chunk boundaries?
13. What happens when the deduplication state no longer fits in RAM?
14. How would you carry session state across chunks?
15. How would you carry history for a time-based rolling window?
16. What is the difference between a partition and a chunk?
17. Why are partitioned inputs useful for retries?
18. Why is append-only output dangerous for retries?
19. What does an idempotent partition write look like?
20. Why might `del` not lower RSS immediately?
21. How would you prove the chunked algorithm is correct?
22. How would you compare full-load and chunked results?
23. What is the small-file problem?
24. When would you use `ParquetWriter`?
25. What signals tell you that pandas is the wrong execution engine?

---

# 123. Final Mental Model

```text
Do not load everything just because you can.

Measure
  ↓
Read less
  ↓
Use intentional dtypes
  ↓
Drop unused columns
  ↓
Chunk input
  ↓
Process one chunk
  ↓
Reduce to output / partial state
  ↓
Carry minimum necessary state
  ↓
Write incrementally
  ↓
Validate against trusted results
  ↓
Make retries idempotent
  ↓
Measure peak memory
  ↓
Change engines when the workload outgrows pandas
```

The real production skill is not knowing `chunksize`.

It is being able to answer:

> **How much memory can this pipeline require at its peak, what state must survive between chunks, how do I prove the chunked result is mathematically correct, and what happens when a partition fails and is retried?**

---

# 124. Final Roadmap Coverage Checklist

## Memory Fundamentals

- [x] `df.info(memory_usage="deep")`
- [x] `memory_usage(deep=True)`
- [x] File size vs DataFrame memory
- [x] pandas memory overhead / working-set reasoning
- [x] Temporary objects
- [x] Peak memory vs final memory
- [x] Memory by column
- [x] Before/after memory measurement
- [x] Reduction percentage

## Read Less

- [x] `usecols`
- [x] `dtype`
- [x] `nrows`
- [x] Parquet `columns=`
- [x] Parquet `filters=`

## Reduce Column Memory

- [x] Numeric downcasting
- [x] `downcast="integer"`
- [x] `downcast="signed"`
- [x] `downcast="unsigned"`
- [x] `downcast="float"`
- [x] Overflow reasoning
- [x] Precision reasoning
- [x] `category`
- [x] Category dictionary/codes mental model
- [x] Low-cardinality benefit
- [x] High-cardinality warning
- [x] Arrow-backed strings
- [x] Drop unused columns early

## Chunked Reading

- [x] `read_csv(chunksize=...)`
- [x] `iterator=True`
- [x] `get_chunk()`
- [x] Chunk lifecycle
- [x] Chunk-size tuning
- [x] Memory vs throughput
- [x] Parsing overhead
- [x] `low_memory` distinction

## Chunked SQL

- [x] `read_sql(chunksize=...)`
- [x] Projection
- [x] Filtering
- [x] Source-side aggregation principle

## Processing Chunks

- [x] Row-level transformation
- [x] Filter then aggregate
- [x] Partial groupby
- [x] Chunk → write
- [x] Chunk → quality checks
- [x] Why retaining all chunks defeats the goal

## Partial Groupby

- [x] Partial sums
- [x] Partial counts
- [x] Correct mean mathematics
- [x] Average-of-averages failure
- [x] Sufficient statistics
- [x] Mergeable vs harder aggregates
- [x] Full-load vs chunked reconciliation

## Chunked Writing

- [x] CSV append
- [x] Header exactly once
- [x] Retry/failure implications
- [x] One Parquet file per chunk
- [x] Small-file trade-off
- [x] `pyarrow.parquet.ParquetWriter`
- [x] Writer lifecycle
- [x] Schema consistency

## Chunk Boundaries

- [x] Cross-chunk deduplication
- [x] `seen_ids`
- [x] State growth
- [x] Sessions spanning chunks
- [x] Session state
- [x] Rolling windows spanning chunks
- [x] Carried history
- [x] Safe-per-chunk classification
- [x] Global sort limitation

## Partitioned Inputs

- [x] One file per day
- [x] Natural processing units
- [x] Partition-level retry concept
- [x] Partition-level monitoring concept
- [x] Partition-level output
- [x] Partition vs chunk

## Idempotent Re-Runs

- [x] Idempotency definition
- [x] Deterministic paths
- [x] Temporary output
- [x] Validation before publish
- [x] Replace/commit concept

## Freeing Memory

- [x] Dropping references
- [x] `del`
- [x] Object lifetime vs allocator vs OS
- [x] RSS
- [x] `gc.collect()` caution

## Stop Conditions

- [x] Data several times larger than RAM
- [x] Multi-core needs
- [x] Large joins
- [x] Distributed processing requirements
- [x] Polars
- [x] DuckDB
- [x] Dask
- [x] Spark
- [x] Module references
- [x] Decision framework

## Learning Activities

- [x] 70%+ memory reduction typing exercise
- [x] Full-load vs chunked exercise
- [x] Actual measurement requirement
- [x] No fabricated benchmark results

## `big_file_pipeline.py`

- [x] Exercise specification
- [x] Large input requirement
- [x] `usecols`
- [x] Compact dtypes
- [x] Per-chunk memory
- [x] Daily trip counts
- [x] Daily revenue
- [x] Average fare
- [x] Correct partial aggregation
- [x] Cross-chunk deduplication
- [x] State-size discussion
- [x] Monthly Parquet output
- [x] Runtime comparison
- [x] Peak-memory comparison
- [x] Polars/DuckDB note
- [x] Input schema
- [x] Output schema
- [x] Assumptions
- [x] Acceptance criteria
- [x] Debugging guidance
- [x] Production considerations

## Quality

- [x] Correctness testing
- [x] Debugging
- [x] Edge cases
- [x] Performance discussion
- [x] Production use cases
- [x] Anti-patterns
- [x] Architecture example
- [x] Safe-per-chunk table
- [x] Mental models
- [x] Interview questions
- [x] Architecture thinking
- [x] Prediction-first learning
- [x] Cheat sheet
- [x] Common mistakes
- [x] Checkpoint
- [x] Production checklist

---

# 125. Primary References

- Pandas 3.0.6 `DataFrame.memory_usage()` documentation. 
- Pandas 3.0.6 `read_csv()` documentation. 
- Pandas 3.0.6 `read_sql()` documentation. 
- Pandas 3.0.6 `read_parquet()` documentation. 
- Pandas 3.0.6 scaling guidance. 
- Pandas 3.0.6 PyArrow functionality. 
- Apache Arrow Parquet writing and `ParquetWriter` documentation. 
