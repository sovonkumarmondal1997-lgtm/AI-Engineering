# Data Formats, Compression, and File Layout — Practice Questions

> **Stage 2 → Python for Data Engineering → Module 2.5**
>
> This is a 40-question practice set built from the material covered in Topics 01–10. It is designed to test understanding, diagnosis, implementation thinking, measurement, and production reasoning.

## How to Use These Questions

Use the questions in order when you want a guided progression, or answer a difficulty section independently when revising.

For performance and storage questions, follow the module's measurement-first loop:

```text
Read
  ↓
Predict
  ↓
Write
  ↓
Inspect
  ↓
Query
  ↓
Measure
  ↓
Change One Knob
  ↓
Measure Again
  ↓
Explain
```

Before implementing performance or storage questions, write down your estimate first. Estimate the relevant quantities such as file count, file size, bytes read, or expected query behavior. After running the implementation, compare your estimate with the measured result and explain the gap between them. The goal is not to guess perfectly; it is to make your reasoning explicit and then learn from the measurement.

For every question below, the **solution immediately follows the problem**. Try to answer the problem before reading the solution.

---

# Part 1 — Basic

### Question 01 — Row vs Columnar for Two Workloads

**Difficulty:** Basic

#### Problem

A company has two workloads:

1. An operational service frequently reads and writes one complete customer record at a time.
2. A reporting job scans tens of millions of orders but usually needs only `order_date`, `country`, and `amount`.

Which physical storage layout fits each workload more naturally: row-oriented or column-oriented? Explain the physical reason rather than simply saying one is "better."

#### Solution

Workload 1 naturally fits **row-oriented storage**.

Workload 2 naturally fits **column-oriented storage**.

#### How to Solve It

1. Identify how much of a record is normally needed.
2. Identify whether the access pattern is record-at-a-time or scan-and-aggregate.
3. Map that pattern to the physical arrangement of bytes.

#### Explanation

A row-oriented layout keeps fields belonging to the same record close together. That is useful when an application wants most or all fields of one customer record.

A column-oriented layout keeps values from the same column close together. The reporting query needs only three columns across many rows, so a columnar representation can avoid reading unrelated columns through **column pruning**.

The deeper rule is:

```text
Whole-record access      → row-oriented is a natural fit
Many rows + few columns → column-oriented is a natural fit
```

Neither layout is universally superior. The workload determines the physical advantage.

#### Code

No code is required. A useful conceptual sketch is:

```text
Row-oriented
R1: id | name | country | amount
R2: id | name | country | amount
R3: id | name | country | amount

Column-oriented
id:      R1 R2 R3 ...
name:    R1 R2 R3 ...
country: R1 R2 R3 ...
amount:  R1 R2 R3 ...
```

#### Expected Result / Interpretation

You should connect the access pattern to physical locality, I/O, and column pruning instead of memorizing a format ranking.

#### Common Mistake

Saying "columnar is always better for production." It is not a valid general rule because record-at-a-time reads and writes can fit row-oriented layouts better.

---

### Question 02 — Why PAX Is a Useful Mental Model

**Difficulty:** Basic

#### Problem

You are given a logical table with four columns and six rows. Someone says:

> "PAX is just row storage."

Is that an accurate description? Explain PAX and its conceptual relationship to Parquet row groups and ORC stripes.

#### Solution

No. **PAX (Partition Attributes Across)** is a hybrid layout. Rows are grouped into blocks, but inside each block the attributes/columns are stored separately.

#### How to Solve It

Think about the two extremes first:

```text
Row layout     → rows together
Column layout  → columns together
```

Then place PAX between them.

#### Explanation

A conceptual PAX layout looks like:

```text
PAX Block 0
├── Column A values for rows in Block 0
├── Column B values for rows in Block 0
├── Column C values for rows in Block 0
└── Column D values for rows in Block 0

PAX Block 1
├── Column A values for rows in Block 1
├── Column B values for rows in Block 1
├── Column C values for rows in Block 1
└── Column D values for rows in Block 1
```

The important analytical idea is that a **bounded group of rows becomes a physical unit**, while columns remain organized within that unit.

Parquet **row groups** and ORC **stripes** are conceptually related to this hybrid idea: they provide bounded row subsets with column-oriented organization inside them. They are not identical implementations of every PAX design, but the mental model is useful.

#### Code

No code is required. Draw the same table as:

```text
PAX Block 0
  A: a1 a2 a3
  B: b1 b2 b3
  C: c1 c2 c3
  D: d1 d2 d3

PAX Block 1
  A: a4 a5 a6
  B: b4 b5 b6
  C: c4 c5 c6
  D: d4 d5 d6
```

#### Expected Result / Interpretation

You should recognize PAX as the bridge between pure row-major and pure column-major thinking.

#### Common Mistake

Treating PAX as an unrelated file format. It is a **storage-layout concept**, useful for understanding why analytical formats use bounded row groups/stripes.

---

### Question 03 — Identify the Parquet Footer and `PAR1`

**Difficulty:** Basic

#### Problem

A Parquet file starts and ends with the four-byte sequence `PAR1`. The metadata footer is near the end of the file.

Why is the footer placed at the end, and why is that useful to a reader?

#### Solution

The writer can stream data forward and collect the final metadata as writing progresses. At the end, it writes the footer and related metadata. A reader can then seek near the end, read the footer, understand the file structure, and decide which columns or row groups may be relevant before reading most data.

#### How to Solve It

Separate the writer's problem from the reader's problem.

```text
Writer:
write data → collect metadata → finish → write footer

Reader:
open → inspect end → read metadata → choose data → read required pieces
```

#### Explanation

At the start of writing, the writer does not necessarily know final offsets, compressed sizes, row-group counts, and other metadata. Writing metadata after the data supports a forward streaming write pattern.

The reader benefits because the footer acts as a navigation map.

`PAR1` is a **magic signature** for format identification. Seeing it does not prove that the file is complete, semantically correct, or compatible with every reader.

#### Code

```python
from pathlib import Path

path = Path("orders.parquet")

with path.open("rb") as f:
    start = f.read(4)

with path.open("rb") as f:
    f.seek(-4, 2)
    end = f.read(4)

print(start)
print(end)
```

Run this locally and record the observed result.

#### Expected Result / Interpretation

For a normal Parquet file, both printed byte strings should identify the expected Parquet magic marker. The footer still must be interpreted using Parquet-aware tooling.

#### Common Mistake

Assuming that `PAR1` itself is the complete metadata. It is only the signature. The footer contains the structured metadata needed for navigation.

---

### Question 04 — Encoding vs Compression

**Difficulty:** Basic

#### Problem

A teammate says:

> "Dictionary encoding and Zstandard are both compression codecs."

Correct the statement and explain the processing order conceptually.

#### Solution

Dictionary encoding is an **encoding** technique. Zstandard is a **compression codec**. In the Parquet pipeline, encoded data can then be compressed.

A simplified model is:

```text
Logical values
    ↓
Encoding / representation
    ↓
Compression
    ↓
Stored bytes
```

#### How to Solve It

Ask what each stage is trying to accomplish:

- Encoding changes how values are represented.
- Compression reduces redundancy in the resulting byte stream.

#### Explanation

For a low-cardinality string column such as `country`, dictionary encoding may replace repeated strings with compact dictionary references. Run-length encoding can represent repeated patterns compactly. Those encoded bytes can then be passed to a compression codec such as Snappy or Zstandard.

The distinction matters because changing an encoding setting is not the same experiment as changing a codec.

#### Code

Conceptual pseudocode:

```python
values = ["IN", "IN", "US", "IN"]

# Conceptual only:
dictionary = {"IN": 0, "US": 1}
encoded = [0, 0, 1, 0]

# A codec such as zstd would compress the encoded byte representation.
```

#### Expected Result / Interpretation

You should be able to explain why encoding and compression are separate knobs that can interact.

#### Common Mistake

Calling every size-reduction technique "compression". Encoding can improve representational efficiency before a separate compression stage.

---

### Question 05 — Explicit Schema in PyArrow

**Difficulty:** Basic

#### Problem

You are writing a production Parquet dataset from Python. Why might you prefer an explicit PyArrow schema instead of trusting type inference?

#### Solution

An explicit schema makes the intended physical/logical types a deliberate contract rather than an accidental consequence of the current input batch.

#### How to Solve It

Think about what could vary between input batches:

- null-heavy batches;
- identifiers that look numeric;
- timestamps with different representations;
- missing columns;
- values whose inferred type changes.

#### Explanation

The module treats schema as more than documentation. In production it controls meaning, compatibility, and downstream consistency.

For example, an account number such as `00001234` should normally remain a string identifier rather than becoming an integer `1234`.

Explicit schemas are especially useful when writing multiple files that must later form one dataset.

#### Code

```python
import pyarrow as pa
import pyarrow.parquet as pq

schema = pa.schema([
    ("account_id", pa.string()),
    ("amount", pa.decimal128(12, 2)),
])

table = pa.Table.from_pydict(
    {
        "account_id": ["00001234", "00005678"],
        "amount": ["1234.50", "950.00"],
    },
    schema=schema,
)

pq.write_table(table, "accounts.parquet", compression="zstd")
```

#### Expected Result / Interpretation

The target schema is explicit. The output is typed Parquet instead of an uncontrolled inference result.

#### Common Mistake

Thinking explicit schemas are only useful for databases. They are equally important when writing file-based analytical datasets.

---

### Question 06 — Nullable Avro Field and Default

**Difficulty:** Basic

#### Problem

You need an Avro field named `email` that may be missing. The source schema convention in the module is a nullable union.

Design the field so that a missing value can resolve safely when a newer reader encounters an older record that does not contain the field.

#### Solution

Use a nullable union with `null` first and a `null` default:

```json
{
  "name": "email",
  "type": ["null", "string"],
  "default": null
}
```

#### How to Solve It

1. Decide whether the field is optional.
2. Represent optionality using a union with `null`.
3. Match the default to the union branch used for the missing value.

#### Explanation

Avro separates the schema contract from the physical bytes. A new field can be added while old records do not contain that field, but reader/writer schema resolution needs a default so the reader knows what value to use.

The module specifically warns about nullable defaults: when the default is `null`, `null` should be the first union branch in the schema used for the exercise.

#### Code

```python
schema = {
    "type": "record",
    "name": "Order",
    "fields": [
        {"name": "order_id", "type": "long"},
        {"name": "email", "type": ["null", "string"], "default": None},
    ],
}
```

#### Expected Result / Interpretation

An older writer schema can be read using the newer schema with `email` resolved to `null` when the field was absent.

#### Common Mistake

Adding a nullable union without a suitable default and then expecting arbitrary schema evolution to work automatically.

---

### Question 07 — ORC Structure and Format Choice

**Difficulty:** Basic

#### Problem

Name the major high-level physical structures taught for ORC and explain why a Data Engineer should not select ORC versus Parquet using a permanent ranking.

#### Solution

The module teaches ORC structures including:

- stripes;
- row indexes/statistics;
- stripe footers;
- file footer;
- postscript.

Format selection should depend on workload, requirements, ecosystem, read/write pattern, types, and measurements.

#### How to Solve It

Use two separate questions:

```text
What is ORC physically?
        ↓
What workload does the format need to serve?
```

#### Explanation

ORC is a columnar analytical format with its own physical organization and metadata structures. Its historical relationship to the Hive ecosystem can matter operationally.

But "best format" is not a permanent ranking. A landing or bronze layer may need to preserve a source representation, while silver/gold analytical storage may use another format. Conversion itself has CPU, I/O, storage, and operational costs.

The correct principle is:

> **Best fit for this workload, not universally best.**

#### Code

No code is required. Build a decision checklist:

```text
Workload
+ Data shape
+ Read pattern
+ Write pattern
+ Scale
+ Ecosystem
+ Operational requirements
+ Measurements
```

#### Expected Result / Interpretation

A strong answer describes the physical format and then moves immediately to workload and operational constraints.

#### Common Mistake

Treating ORC, Parquet, or Avro as universally superior regardless of pipeline stage.

---

### Question 08 — Grain Before an Explode

**Difficulty:** Basic

#### Problem

An `orders` DataFrame contains one row per order. Each order has a list of line items. You call `explode()` on the line-item list.

What is the grain before and after the operation?

#### Solution

Before:

```text
one row = one order
```

After:

```text
one row = one order-line
```

#### How to Solve It

Ask what one output row represents after the transformation, not what the column used to represent.

#### Explanation

Exploding a list creates one output row for each list element. That is a **grain change**.

If order `1001` has three line items, one input row can become three output rows. The `order_id` must therefore be preserved as a parent key.

This matters because an order-level amount repeated across line rows can be double-counted if aggregated after the explode.

#### Code

```python
import pandas as pd

orders = pd.DataFrame({
    "order_id": [1001, 1002],
    "items": [["A", "B", "C"], ["D"]],
})

order_lines = orders.explode("items", ignore_index=True)
print(order_lines)
```

Run this locally and inspect the row count.

#### Expected Result / Interpretation

The first order contributes three rows and the second contributes one. The logical grain changes from order to order-line.

#### Common Mistake

Thinking `explode()` only reshapes a column and leaves the table's business grain unchanged.

---

### Question 09 — Compression Ratio Calculation

**Difficulty:** Basic

#### Problem

A dataset is 800 MB before compression and 200 MB after compression.

Calculate:

1. the compression ratio using `compressed_size / original_size`;
2. the reduction percentage.

#### Solution

1. Compression ratio as `compressed / original`:

```text
200 / 800 = 0.25
```

2. Reduction percentage:

```text
(800 - 200) / 800 × 100
= 600 / 800 × 100
= 75%
```

#### How to Solve It

First identify which convention the question asks for. A "ratio" can be expressed in multiple ways, so always state the formula.

#### Explanation

Here, the compressed representation is one quarter of the original size, corresponding to a 75% reduction.

Compression ratio alone does not tell you whether the codec is operationally desirable. The module also measures compression speed, decompression speed, CPU cost, and workload impact.

#### Code

```python
original = 800
compressed = 200

ratio = compressed / original
reduction_pct = (original - compressed) / original * 100

print(ratio)
print(reduction_pct)
```

#### Expected Result / Interpretation

You should get `0.25` and `75.0` for this synthetic calculation.

#### Common Mistake

Reporting a single compression ratio as proof that one codec is universally better. Compression performance must be evaluated with CPU and read/write behavior too.

---

### Question 10 — Excel Leading Zeros

**Difficulty:** Basic

#### Problem

An Excel report contains an `account_id` column with values:

```text
00001234
00007890
```

After reading the workbook, the DataFrame contains integers `1234` and `7890`.

Why is this a correctness problem, and what should the target type usually be?

#### Solution

It is a correctness problem because the leading zeros may be part of the identifier's representation. The target type should usually be **string**, not integer.

#### How to Solve It

Distinguish identifiers from measures.

- `amount = 1234.50` → numeric measurement.
- `account_id = "00001234"` → identifier whose exact representation matters.

#### Explanation

Excel's visual formatting is not the same as a durable analytical type contract. Once `00001234` has become integer `1234`, you may not be able to recover the original representation unless the expected width is known.

Production ingestion should deliberately preserve identifiers such as account numbers, postal codes, branch codes, and product codes as strings when their formatting is meaningful.

#### Code

```python
import pandas as pd

# Prefer reading or casting the identifier deliberately as text.
df = pd.DataFrame({"account_id": ["00001234", "00007890"]})
df["account_id"] = df["account_id"].astype("string")
```

#### Expected Result / Interpretation

The exact identifier representation remains available to downstream systems.

#### Common Mistake

Treating every digit-only Excel column as a numeric field.

---

# Part 2 — Moderate

### Question 11 — Row-Group Skipping from Statistics

**Difficulty:** Moderate

#### Problem

A Parquet dataset has two row groups for a column `order_date`:

| Row Group | Minimum | Maximum |
|---|---|---|
| 0 | 2026-01-01 | 2026-01-31 |
| 1 | 2026-02-01 | 2026-02-28 |

A query filters for `order_date >= '2026-02-10'`.

Assuming the engine uses the available statistics correctly, which row group can be skipped based on min/max statistics, and why?

#### Solution

**Row Group 0 can be skipped** because its maximum value is `2026-01-31`, which is earlier than the query's minimum required date `2026-02-10`.

Row Group 1 must remain a candidate because its range overlaps the query predicate.

#### How to Solve It

For each row group ask:

> Can any value in this row group's `[min, max]` range satisfy the predicate?

For Group 0:

```text
max = 2026-01-31
required >= 2026-02-10
```

No value can satisfy it.

#### Explanation

This is **predicate skipping** at the row-group level. It is different from column pruning:

```text
Column pruning  → which columns are needed?
Predicate skip  → which physical blocks might be irrelevant?
```

Statistics are evidence that can enable skipping; they are not a guarantee that every engine or query will skip exactly the same way.

#### Code

Conceptual logic:

```python
from datetime import date

row_groups = [
    {"name": 0, "min": date(2026, 1, 1), "max": date(2026, 1, 31)},
    {"name": 1, "min": date(2026, 2, 1), "max": date(2026, 2, 28)},
]

predicate_min = date(2026, 2, 10)

for rg in row_groups:
    can_match = rg["max"] >= predicate_min
    print(rg["name"], can_match)
```

#### Expected Result / Interpretation

Group 0 is a non-match and is therefore a candidate for skipping. Group 1 can contain matching rows.

#### Common Mistake

Saying statistics guarantee skipping. The file may contain useful statistics, but actual execution depends on the reader/engine and predicate semantics.

---

### Question 12 — `iter_batches()` vs `read_table()`

**Difficulty:** Moderate

#### Problem

You need to process a 5 GB Parquet file on a machine where materializing the entire table is too memory-intensive.

Which PyArrow approach from Topic 03 is appropriate, and what is the main trade-off?

#### Solution

Use `pyarrow.parquet.ParquetFile.iter_batches(batch_size=...)` or an equivalent dataset batch workflow.

The main benefit is **bounded-memory processing**. The trade-off is more incremental processing logic instead of having the whole table materialized at once.

#### How to Solve It

Look at the memory requirement:

```text
read_table()
    ↓
materialize a large table
    ↓
high peak memory risk

iter_batches()
    ↓
process smaller batches
    ↓
lower peak memory
```

#### Explanation

`iter_batches()` exposes the file as a sequence of batches. This allows transformations, validation, or streaming output without requiring the full file in RAM.

This is a different problem from file compression or partitioning. The goal here is **memory control during processing**.

#### Code

```python
import pyarrow.parquet as pq

pf = pq.ParquetFile("large_orders.parquet")

for batch in pf.iter_batches(batch_size=100_000):
    # Process one batch at a time.
    print(batch.num_rows)
```

Run locally and record the observed peak-memory behavior rather than inventing a number.

#### Expected Result / Interpretation

The process handles batches incrementally instead of creating one giant in-memory table.

#### Common Mistake

Assuming `read_table()` is always wrong. For small files, full materialization may be perfectly reasonable. The decision depends on data size and available memory.

---

### Question 13 — Avro Writer Schema vs Reader Schema

**Difficulty:** Moderate

#### Problem

An Avro file was written with:

```text
writer schema:
order_id, amount
```

A newer application uses:

```text
reader schema:
order_id, amount, currency = "INR"
```

What mechanism allows the reader to interpret an older record that does not contain `currency`?

#### Solution

**Avro schema resolution** uses the reader schema together with the writer schema, and the reader's default value for `currency` supplies the missing field.

#### How to Solve It

Separate these two schemas:

```text
Writer schema → describes what bytes mean in the file
Reader schema → describes what the application wants
```

Then ask whether the missing field has a valid default.

#### Explanation

The writer schema is part of the data's contract. The reader can project that older data through a newer schema when the evolution rule is compatible.

For a newly added field, a default can allow older records to be interpreted without the original writer having stored that field.

This is why schema design is an operational concern rather than just serialization syntax.

#### Code

Conceptually:

```python
writer_schema = {
    "type": "record",
    "name": "Order",
    "fields": [
        {"name": "order_id", "type": "long"},
        {"name": "amount", "type": "double"},
    ],
}

reader_schema = {
    "type": "record",
    "name": "Order",
    "fields": [
        {"name": "order_id", "type": "long"},
        {"name": "amount", "type": "double"},
        {"name": "currency", "type": "string", "default": "INR"},
    ],
}
```

Actual schema-resolution behavior should be tested with the project's Avro tooling.

#### Expected Result / Interpretation

Old records can supply `currency = "INR"` through the reader's default when the evolution is compatible.

#### Common Mistake

Assuming any schema change is automatically compatible merely because both schemas are valid JSON.

---

### Question 14 — ORC vs Parquet for a New Analytical Dataset

**Difficulty:** Moderate

#### Problem

Your platform team asks:

> "Should we standardize all analytical datasets on ORC or Parquet?"

Give a production-oriented answer using the module's format-selection framework.

#### Solution

Do not choose a permanent winner from format names alone. Build a workload-specific comparison covering at least:

- physical layout and metadata behavior;
- types and nested-data needs;
- statistics/indexing behavior;
- compression;
- read/write patterns;
- engine/ecosystem support;
- storage location;
- conversion cost;
- operational ownership;
- measured query and write behavior.

#### How to Solve It

Start with the workload, then compare candidate formats.

```text
Workload
  ↓
Requirements
  ↓
Candidate formats
  ↓
Controlled benchmark
  ↓
Operational review
  ↓
Policy + exceptions
```

#### Explanation

The module explicitly teaches that ORC and Parquet have different physical structures and ecosystems. ORC has stripes, row indexes, stripe footers, file footer, and postscript. Parquet has row groups, column chunks, pages, and footer metadata.

A team should standardize based on evidence and operational fit. A policy can still have a default, but it should include justified exceptions and should not pretend that all workloads are identical.

#### Code

A decision table is more useful than a single ranking:

| Dimension | Candidate A | Candidate B | Evidence needed |
|---|---|---|---|
| Typical query |  |  | measured runtime/bytes |
| Write pattern |  |  | write time/resource use |
| Types |  |  | schema compatibility |
| Ecosystem |  |  | actual consumers |
| Conversion cost |  |  | CPU/I/O/storage |

#### Expected Result / Interpretation

A strong answer makes the decision traceable to workload and measurements.

#### Common Mistake

Starting with "Parquet is the industry standard" and stopping there. Familiarity can inform a default, but it is not the whole engineering decision.

---

### Question 15 — Avoiding a Nested Cross-Product

**Difficulty:** Moderate

#### Problem

An order has:

```text
order_id = 1001
order_lines = 3 items
payments = 2 records
```

A developer flattens both arrays into the same DataFrame before aggregation. How many rows could be produced for this order, and why is this dangerous?

#### Solution

A naïve simultaneous expansion can create a **3 × 2 = 6 row cross-product** for that order.

It is dangerous because parent and child facts can become duplicated across combinations, causing incorrect aggregates and double counting.

#### How to Solve It

Treat each repeated collection as a separate child grain.

```text
Order
 ├── 3 order lines
 └── 2 payments
```

Do not force unrelated one-to-many relationships into one flat row set unless the multiplication is explicitly intended.

#### Explanation

The safe analytical model is often:

```text
orders
order_lines
payments
```

with a shared `order_id`.

Each child table preserves its own grain:

```text
orders       → one row per order
order_lines → one row per line
payments    → one row per payment
```

#### Code

```python
order_lines = [
    {"order_id": 1001, "line_id": 1},
    {"order_id": 1001, "line_id": 2},
    {"order_id": 1001, "line_id": 3},
]

payments = [
    {"order_id": 1001, "payment_id": "P1"},
    {"order_id": 1001, "payment_id": "P2"},
]

cross_product_rows = [
    (line["line_id"], payment["payment_id"])
    for line in order_lines
    for payment in payments
]

print(cross_product_rows)
```

#### Expected Result / Interpretation

There are six combinations. That is not the same business meaning as three lines plus two payments.

#### Common Mistake

Thinking that because all rows share the same `order_id`, combining both child arrays is safe.

---

### Question 16 — Design a Fair Compression Benchmark

**Difficulty:** Moderate

#### Problem

You want to compare Snappy, gzip, LZ4, and several Zstandard levels on the same Parquet dataset. Design a fair benchmark.

#### Solution

Keep these variables constant:

- dataset contents;
- schema;
- sort order;
- row-group settings;
- file count;
- storage location;
- hardware;
- reader/writer implementation;
- query;
- query parameters;
- warm/cold cache condition for each comparison;
- number of repeated runs.

Change only the codec (and, in a separate experiment, compression level).

#### How to Solve It

Use the module's measurement-first process:

```text
Same data
   ↓
Codec A → measure
Codec B → measure
Codec C → measure
```

Do not combine codec changes with row-group-size or sorting changes in the same first comparison.

#### Explanation

A codec result can otherwise be confounded by a second variable. For example, a codec written with different row-group sizes is not a clean codec comparison.

Measure at least:

- file size;
- write time;
- full-read time;
- selective column-read time;
- decompression/read CPU where measurable.

The module's key principle is:

> **The goal is the best workload-level trade-off, not maximum compression.**

#### Code

```python
benchmarks = [
    "snappy",
    "gzip",
    "lz4",
    "zstd:1",
    "zstd:3",
    "zstd:9",
]

results = []

for setting in benchmarks:
    # Write the same logical dataset with only this compression setting changed.
    # Record measured values locally rather than fabricating them.
    results.append({
        "setting": setting,
        "file_size_bytes": None,
        "write_seconds": None,
        "full_read_seconds": None,
        "selective_read_seconds": None,
    })
```

#### Expected Result / Interpretation

The benchmark should produce an evidence table in which no result is predeclared as the winner.

#### Common Mistake

Comparing one codec with compression enabled and another with different row-group or sorting settings.

---

### Question 17 — Design a Query-Driven Partition Scheme

**Difficulty:** Moderate

#### Problem

A sales table contains three years of data. Most queries filter by month and occasionally by country. The table has billions of rows, and `customer_id` has tens of millions of distinct values.

Choose a reasonable starting partition design from these options:

```text
A. customer_id
B. year/month/day
C. year/month
D. country/customer_id
```

Explain your choice and what you would benchmark before standardizing it.

#### Solution

A reasonable starting point is **`year/month`**, assuming the monthly partitions contain enough data to create healthy files and the main queries filter by month.

Then benchmark whether adding another level such as day materially improves pruning without creating unhealthy file counts.

#### How to Solve It

Evaluate:

1. filter frequency;
2. cardinality;
3. partition volume;
4. file sizing;
5. operational complexity.

#### Explanation

`customer_id` is high cardinality and would create many small partitions and files. `country/customer_id` is even more aggressive.

`year/month/day` might be appropriate if daily volume is large enough, but it can over-partition lower-volume datasets.

`year/month` aligns directly with the described query pattern while keeping partition cardinality much lower.

#### Code

A practical worksheet:

```text
Query: month filter
Candidate: year/month
Expected benefit: skip irrelevant months
Risk: monthly partition may become large

Candidate: year/month/day
Expected benefit: finer pruning
Risk: more partitions/files

Candidate: customer_id
Expected benefit: point-customer pruning
Risk: extreme cardinality / tiny files
```

#### Expected Result / Interpretation

The answer should be workload-driven rather than based on a blanket "partition by date" rule.

#### Common Mistake

Partitioning by `customer_id` just because one query filters on it. Cardinality and resulting file health matter too.

---

### Question 18 — Diagnose a Small-Files Partition

**Difficulty:** Moderate

#### Problem

A partition contains:

```text
5,000 Parquet files
average file size = 8 MB
```

Most queries scan that partition several times per day.

What problem does this suggest, what should you measure, and what are the first two prevention/fix strategies you would investigate?

#### Solution

This strongly suggests a **small-files problem**. Measure:

- file count;
- total bytes;
- median/p90/p95/p99 file sizes;
- representative query runtime;
- bytes read where observable;
- object-storage request behavior where observable;
- writer/partitioning pattern.

Then investigate **write-side batching/writer parallelism** and **targeted compaction**.

#### How to Solve It

First diagnose whether the fragmentation is being created continuously or is historical.

```text
Frequent writes → prevention
Historical fragmentation → compaction
```

#### Explanation

The module's core mental model is that file count creates costs in addition to total data volume:

- file open/read work;
- footer/metadata work;
- listings;
- object requests;
- task/scheduling overhead;
- potentially weaker compression.

The roadmap's approximate analytical Parquet starting range is **128 MB–1 GB**, but it is a guideline rather than a universal law.

#### Code

A first diagnostic:

```python
from pathlib import Path
from statistics import median

root = Path("orders/year=2026/month=09")
sizes = [p.stat().st_size for p in root.rglob("*.parquet")]

print("files:", len(sizes))
print("total_mb:", sum(sizes) / 1024**2)
print("median_mb:", median(sizes) / 1024**2)
```

#### Expected Result / Interpretation

The important result is not merely "5,000 is large." It is whether fragmentation is material to the actual workload and whether the write pattern can be changed.

#### Common Mistake

Choosing a compaction threshold solely from the average file size without checking the distribution and query value of the partition.

---

### Question 19 — Messy Excel Report and Reconciliation

**Difficulty:** Moderate

#### Problem

A workbook contains this visual structure:

```text
Row 1: Company title
Row 2: Reporting period
Row 3: blank
Row 4–5: merged/two-row header
Rows 6–25: detail records
Row 26: TOTAL
Row 27: preparation note
```

Explain a safe ingestion strategy using pandas and why blindly calling `pd.read_excel()` is insufficient.

#### Solution

Inspect the workbook first, identify the actual data region, normalize the two-row header, read only the intended columns, isolate the totals row from detail records, preserve identifier columns as strings, convert types deliberately, and compare the computed detail total with the reported total.

#### How to Solve It

Use this order:

```text
Inspect workbook
   ↓
Identify header/data/totals regions
   ↓
Read deliberately
   ↓
Normalize columns
   ↓
Convert types
   ↓
Separate totals
   ↓
Reconcile
```

#### Explanation

Excel is a visual document format as much as a data source. Merged cells, titles, notes, hidden content, and totals can become rows or columns if interpreted blindly.

The controls `header`, `skiprows`, and `usecols` exist to describe the source structure. They are correctness controls, not merely convenience options.

#### Code

```python
import pandas as pd

raw = pd.read_excel(
    "sales.xlsx",
    sheet_name="September",
    header=None,
)

# Inspect rows before deciding the real header/data boundary.
print(raw.head(10))

# Example only: adjust after inspection.
detail = pd.read_excel(
    "sales.xlsx",
    sheet_name="September",
    skiprows=4,
    usecols="A:D",
)

# Normalize identifiers before numeric conversion.
detail["Account"] = detail["Account"].astype("string")

# Separate a totals row if it was included.
detail_mask = detail["Store"].astype("string").str.upper().ne("TOTAL")
details = detail.loc[detail_mask].copy()
```

Run locally and adapt the row boundaries to the actual workbook structure.

#### Expected Result / Interpretation

The resulting DataFrame should contain only actual detail records with deliberate column names and types, while the total is validated separately.

#### Common Mistake

Treating the first non-empty row as the table header without inspecting merged cells and report metadata.

---

### Question 20 — XML Namespace Debugging

**Difficulty:** Moderate

#### Problem

An XML feed looks like this:

```xml
<feed xmlns="urn:example:products">
  <product id="P100">
    <name>Keyboard</name>
  </product>
</feed>
```

The following ElementTree search returns no products:

```python
root.findall("product")
```

Why, and how should you fix it?

#### Solution

Because the default namespace means `product` is actually a **qualified name** associated with the namespace URI `urn:example:products`.

Use a namespace mapping:

```python
ns = {"p": "urn:example:products"}
products = root.findall("p:product", ns)
```

#### How to Solve It

Remember that an XML prefix is only a local alias. The namespace URI identifies the namespace.

```text
prefix in document → URI in namespace declaration
```

#### Explanation

Namespace handling is a common source of "XPath returns nothing" bugs. The XML element is not simply named `product` in the no-namespace sense.

`lxml` can use XPath with the same namespace idea. `pandas.read_xml()` also has namespace-aware parameters when a tabular extraction is appropriate.

#### Code

```python
import xml.etree.ElementTree as ET

xml_text = """
<feed xmlns="urn:example:products">
  <product id="P100">
    <name>Keyboard</name>
  </product>
</feed>
"""

root = ET.fromstring(xml_text)
ns = {"p": "urn:example:products"}

for product in root.findall("p:product", ns):
    print(product.attrib["id"])
```

#### Expected Result / Interpretation

The product node is found once the namespace is included in the lookup.

#### Common Mistake

Assuming the visible prefix or default namespace is just decorative text. Namespace URI membership changes the element's qualified name.

---

# Part 3 — Hard

### Question 21 — Filter Is Selective, but Parquet Still Reads Too Much

**Difficulty:** Hard

#### Problem

A Parquet dataset has a highly selective filter on `country = 'IN'`, but the query still scans many row groups.

You inspect the metadata and discover that each row group's `country` min/max range is approximately `['IN', 'US']` because values are randomly interleaved.

What is happening, and what experiment would you run before changing the file format?

#### Solution

The filter is selective logically, but the **row-group statistics are not selective enough to prove whole row groups are irrelevant** because each row group contains a mixture of countries.

Run a controlled experiment comparing:

- the current/randomly ordered data;
- equivalent data sorted by `country`;

while holding schema, codec, row-group settings, partitioning, and query constant.

#### How to Solve It

Inspect the physical evidence first:

```text
Query predicate
   ↓
Row-group min/max
   ↓
Can this row group be proven irrelevant?
```

If every row group overlaps `IN`, statistics cannot provide much skipping.

#### Explanation

This is exactly why **sort order affects statistics usefulness**. Sorting can cluster similar values, making row-group ranges narrower and potentially improving pruning.

The experiment must be fair. Do not change sorting, codec, and row-group size simultaneously.

#### Code

```python
import pyarrow as pa
import pyarrow.parquet as pq

# Conceptual experiment setup.
random_table = pa.table({
    "country": ["IN", "US", "UK", "IN", "US", "UK"],
    "amount": [10, 20, 30, 40, 50, 60],
})

sorted_table = pa.table({
    "country": ["IN", "IN", "UK", "UK", "US", "US"],
    "amount": [10, 40, 30, 60, 20, 50],
})

pq.write_table(random_table, "random.parquet", row_group_size=3, compression="zstd")
pq.write_table(sorted_table, "sorted.parquet", row_group_size=3, compression="zstd")
```

Run the same filtered query against both files and inspect metadata.

#### Expected Result / Interpretation

The sorted dataset should provide narrower row-group ranges in this simple example, but actual query improvements must be measured locally.

#### Common Mistake

Changing the codec first. The symptom is primarily about **data ordering and pruning evidence**, so isolate that variable first.

---

### Question 22 — PyArrow Dataset Schema Mismatch

**Difficulty:** Hard

#### Problem

A directory contains three Parquet files:

```text
part-1.parquet → amount = int64
part-2.parquet → amount = int64
part-3.parquet → amount = string
```

Why can this create a dataset-level problem even if each file is individually readable, and what production policy should the team use?

#### Solution

A multi-file dataset needs a coherent schema. A column that is numeric in some files and string in another creates an incompatible type mismatch unless an explicit, safe conversion/unification policy exists.

Production policy should distinguish:

- compatible schema widening or missing columns that can be reconciled deliberately;
- incompatible type changes that should **fail loudly or quarantine**, rather than being silently coerced.

#### How to Solve It

Think at two levels:

```text
Individual file validity
        ≠
Dataset-level schema compatibility
```

#### Explanation

PyArrow dataset workflows combine multiple physical files under one logical dataset. The schema is therefore a production contract.

A string such as `"100"` is not automatically equivalent to an `int64` field in every dataset context. Silent coercion can hide upstream data-quality or contract changes.

#### Code

```python
import pyarrow as pa

expected_schema = pa.schema([
    ("order_id", pa.int64()),
    ("amount", pa.float64()),
])

# Production parsing/writing should conform inputs to the contract
# before publishing files into a shared dataset.
print(expected_schema)
```

#### Expected Result / Interpretation

A safe pipeline prevents incompatible files from silently joining an existing analytical dataset.

#### Common Mistake

Testing only that each Parquet file opens successfully and assuming that proves the dataset is healthy.

---

### Question 23 — Incremental Parquet Writing with `ParquetWriter`

**Difficulty:** Hard

#### Problem

A source contains 20 GB of data arriving in batches. You want one Parquet file per day without holding all 20 GB in memory.

Describe the role of `ParquetWriter`, what should stay constant across batches, and one physical-layout parameter you should measure rather than guess.

#### Solution

Use `ParquetWriter` to create the file once and append compatible Arrow record batches/tables incrementally.

The **schema must remain compatible** across writes. Writer settings such as compression and physical layout are deliberate configuration choices for the file.

A parameter to benchmark is `row_group_size` because it affects:

- compression efficiency;
- metadata granularity;
- skipping behavior;
- writer memory;
- read behavior.

#### How to Solve It

```text
One day
   ↓
batch 1 → writer
batch 2 → writer
batch 3 → writer
   ↓
close writer
```

#### Explanation

`ParquetWriter` is a file-level incremental writer. It avoids requiring a full in-memory table.

However, incremental writing is not synonymous with "one row per file." If upstream batches are too small or writer/partition parallelism is poorly managed, you can still create fragmented datasets.

#### Code

```python
import pyarrow as pa
import pyarrow.parquet as pq

schema = pa.schema([
    ("order_id", pa.int64()),
    ("amount", pa.float64()),
])

writer = pq.ParquetWriter(
    "orders-2026-09-28.parquet",
    schema=schema,
    compression="zstd",
)

try:
    for batch_rows in [
        {"order_id": [1, 2], "amount": [10.0, 20.0]},
        {"order_id": [3, 4], "amount": [30.0, 40.0]},
    ]:
        table = pa.Table.from_pydict(batch_rows, schema=schema)
        writer.write_table(table)
finally:
    writer.close()
```

#### Expected Result / Interpretation

The file is built incrementally with a stable schema and controlled memory use. Exact row-group boundaries depend on the writing method/settings and should be inspected.

#### Common Mistake

Assuming incremental writing automatically produces ideal row groups and file sizes.

---

### Question 24 — Avro → Parquet Conversion Pitfall

**Difficulty:** Hard

#### Problem

An Avro source contains:

```text
status: enum("NEW", "PAID", "CANCELLED")
amount: ["null", "double"]
created_at: timestamp-millis
```

You are converting it to explicit-schema Parquet. What mapping decisions deserve special attention?

#### Solution

The important mapping decisions are:

- **enum** → decide whether to preserve it as a controlled string/categorical representation and what semantic contract is required;
- **nullable union** → preserve nullability rather than converting the union to an ambiguous generic type;
- **timestamp-millis** → map deliberately to an appropriate Arrow/Parquet timestamp unit and timezone interpretation;
- ensure the resulting schema preserves the source business meaning.

#### How to Solve It

For every source field ask:

```text
Avro type
  ↓
logical meaning
  ↓
Arrow type
  ↓
Parquet representation
  ↓
validation test
```

#### Explanation

The conversion is not just a byte copy. Different formats express types and logical metadata differently.

Unions are especially important because a union represents multiple possible branches. A target analytical schema should make the intended nullability explicit.

Logical types such as timestamps also require deliberate unit and interpretation choices.

#### Code

```python
import pyarrow as pa

schema = pa.schema([
    ("status", pa.string()),
    ("amount", pa.float64()),
    ("created_at", pa.timestamp("ms", tz="UTC")),
])

print(schema)
```

#### Expected Result / Interpretation

The target schema should make the intended types explicit and should be tested against representative source records.

#### Common Mistake

Flattening every Avro type mechanically without considering semantic meaning, nullability, timestamps, or enums.

---

### Question 25 — Heterogeneous JSON/XML-Type Fields

**Difficulty:** Hard

#### Problem

A semi-structured source has a field `discount` that appears as:

```text
{"discount": 10}
{"discount": "10%"}
{"discount": null}
```

What should a production Data Engineer do instead of simply relying on schema inference?

#### Solution

Inspect the source distribution and define a deliberate target model. Depending on the business meaning, options include:

- normalize the field into a numeric amount and/or separate representation;
- preserve the raw source value for replay/audit;
- quarantine records that cannot be mapped unambiguously;
- version or evolve the target schema when the source contract genuinely changed.

#### How to Solve It

Do not begin with a parser setting. Begin with semantics:

```text
10
10%
null
```

may not be three representations of the same measure.

#### Explanation

Topic 06 warns that heterogeneous semi-structured data and changing field types can break naïve schema inference. Topic 10 extends the same principle to legacy sources.

A production parser should distinguish:

- missing/nullable;
- type conversion failure;
- genuinely different business representations;
- source-contract changes.

#### Code

```python
from decimal import Decimal

raw_values = [10, "10%", None]

for raw in raw_values:
    if raw is None:
        parsed = None
    elif isinstance(raw, (int, float)):
        parsed = Decimal(str(raw))
    else:
        parsed = None  # requires an explicit business rule for strings such as "10%"

    print(raw, parsed)
```

#### Expected Result / Interpretation

The pipeline does not silently claim that `10` and `10%` are the same semantic quantity.

#### Common Mistake

Letting a parser infer a single type and silently coercing incompatible source meanings.

---

### Question 26 — `.csv.gz` vs Compressed Parquet

**Difficulty:** Hard

#### Problem

A team proposes storing all analytical data as `.csv.gz` because gzip provides strong compression.

Give three reasons compressed Parquet can serve analytical workloads differently, even though both can reduce storage size.

#### Solution

Compressed Parquet provides a structured analytical layout that can support:

1. **typed columns** instead of reparsing text values;
2. **column pruning**, so a query can read only required columns;
3. **row-group/file metadata and statistics** that can support skipping irrelevant data.

Parquet also compresses within its physical structures instead of wrapping the entire text file in one gzip stream.

#### How to Solve It

Compare the physical access path, not only final file size.

#### Explanation

`.csv.gz` can be useful for exchange and transport because text is broadly interoperable. But compression alone does not create columnar access.

For analytics:

```text
CSV.gz
  ↓
parse text
  ↓
materialize requested values

Parquet
  ↓
inspect schema/metadata
  ↓
prune columns
  ↓
use statistics where possible
  ↓
read compressed columnar data
```

#### Code

A conceptual DuckDB comparison:

```sql
SELECT SUM(amount)
FROM read_parquet('orders.parquet')
WHERE country = 'IN';

SELECT SUM(CAST(amount AS DOUBLE))
FROM read_csv_auto('orders.csv.gz', compression='gzip')
WHERE country = 'IN';
```

Run the benchmark locally and record the actual behavior.

#### Expected Result / Interpretation

The analytical advantage is not simply "smaller file." It comes from structure, typing, selective reads, and metadata-aware execution.

#### Common Mistake

Comparing only compressed file sizes and ignoring parsing and query execution behavior.

---

### Question 27 — Safe Partition Overwrite

**Difficulty:** Hard

#### Problem

A daily backfill recomputes only these partitions:

```text
year=2026/month=09/day=26
year=2026/month=09/day=27
```

The dataset also contains valid data for all other dates.

Describe an idempotent partition-overwrite strategy.

#### Solution

Only replace the partitions touched by the current run. Write replacement data to temporary output, validate it, publish the replacement safely, and leave unrelated partitions unchanged.

#### How to Solve It

Think in terms of **logical scope**:

```text
Run input
  ↓
Touched partition set
  ↓
Write temp replacement for those partitions
  ↓
Validate
  ↓
Publish touched partitions
  ↓
Leave all other partitions alone
```

#### Explanation

A backfill should not require rewriting the entire dataset. Idempotency means a rerun of the same logical input produces the same intended partition state rather than duplicate data.

Plain directories still have concurrency and atomicity limitations; publication must be designed around the storage system's semantics.

#### Code

Conceptual PyArrow dataset write:

```python
import pyarrow.dataset as ds

# Assume df is already filtered to the partitions being replaced.
# The exact publication procedure depends on the storage system.
ds.write_dataset(
    data=table,
    base_dir="_temp/run-123",
    format="parquet",
    partitioning=["year", "month", "day"],
)
```

The production step is not this write alone; it is **temp → validate → publish → cleanup**.

#### Expected Result / Interpretation

A rerun changes only the intended partitions and does not touch unrelated data.

#### Common Mistake

Deleting the entire dataset and rewriting it for a small backfill.

---

### Question 28 — Idempotent Compaction

**Difficulty:** Hard

#### Problem

A partition contains 100 small Parquet files. A compactor combines them into 10 healthy files. The compaction job is accidentally run a second time.

What should happen in a well-designed system, and what implementation mistakes would violate idempotency?

#### Solution

The second run should detect that the partition is healthy and either **skip compaction** or perform a logically equivalent safe rewrite without duplicating data.

Common violations include:

- appending new compacted files while leaving old inputs visible;
- selecting both old and newly created files as inputs on retry;
- using non-deterministic selection without tracking the logical input set;
- publishing partial output.

#### How to Solve It

The desired state is:

```text
100 small files
   ↓
10 healthy files
   ↓
second run
   ↓
no duplicate logical rows
```

#### Explanation

Idempotency is about logical state, not merely whether the process can be executed twice.

A safe compactor:

1. identifies eligible input files;
2. writes a replacement set to temporary output;
3. validates it;
4. publishes the replacement;
5. removes old files only under a safe cleanup policy.

#### Code

A health gate can look like:

```python
def should_compact(file_count, p95_bytes, min_target_bytes):
    return file_count > 50 and p95_bytes < min_target_bytes

print(should_compact(10, 400_000_000, 128 * 1024 * 1024))
```

Use real configurable thresholds in production.

#### Expected Result / Interpretation

An already healthy partition should not continually generate more replacement generations.

#### Common Mistake

Appending compacted output and assuming a later cleanup will make the process idempotent.

---

### Question 29 — Stream a 2 GB XML Feed Safely

**Difficulty:** Hard

#### Problem

A supplier sends a 2 GB XML product feed. Your machine has limited RAM. Design the parser strategy.

#### Solution

Use event-based streaming with `iterparse()`, process one logical record at a time, and clear processed elements with `element.clear()` so the parsed tree does not grow indefinitely.

Also:

- handle namespaces explicitly;
- validate structure/business rules incrementally where possible;
- track progress and record counts;
- quarantine malformed records/files according to the source structure;
- use defensive XML parsing for untrusted input.

#### How to Solve It

Avoid the whole-document model:

```text
2 GB file
  ↓
parse entire tree
  ↓
RAM pressure
```

Prefer:

```text
2 GB file
  ↓
iterparse events
  ↓
process one product
  ↓
clear product node
  ↓
continue
```

#### Explanation

`iterparse` does not magically make every XML operation constant-memory. Your own Python objects, retained references, accumulated output, and parent-tree behavior still matter. The important technique is to process records incrementally and release processed subtrees.

For a nested product feed, you might emit:

```text
products
product_prices
```

while preserving the product key in each child row.

#### Code

```python
import xml.etree.ElementTree as ET

ns = {"p": "urn:example:products"}

for event, elem in ET.iterparse(
    "products.xml",
    events=("end",),
):
    if elem.tag == "{urn:example:products}product":
        product_id = elem.attrib.get("id")
        name = elem.findtext("p:name", namespaces=ns)

        # Emit parent/child records here.
        print(product_id, name)

        # Release processed children from the element.
        elem.clear()
```

For untrusted XML, use a defensive parser strategy rather than unsafe defaults.

#### Expected Result / Interpretation

The parser processes the large source incrementally instead of intentionally materializing the entire 2 GB document.

#### Common Mistake

Using `ET.parse()` on a multi-GB feed and then trying to solve the memory problem by increasing machine RAM without changing the parsing architecture.

---

### Question 30 — Fixed-Width H/D/T Feed with Implied Decimal

**Difficulty:** Hard

#### Problem

A fixed-width feed contains three record types:

```text
H...
D...
D...
T...
```

A detail amount field contains `0001234` with an implied scale of 2 and a sign character appears at the end of the field. The trailer provides an expected detail-record count and expected total amount.

Describe the parsing sequence that correctly handles record types, implied decimals, signs, and reconciliation.

#### Solution

Use this order:

```text
Read raw line
   ↓
Detect record type
   ↓
Choose versioned layout
   ↓
Extract raw fields by fixed positions
   ↓
Interpret padding/alignment
   ↓
Interpret sign
   ↓
Apply implied decimal scale
   ↓
Validate record
   ↓
Accumulate detail count/sum
   ↓
Parse trailer
   ↓
Compare actual vs expected totals
```

For `0001234` with scale 2:

```text
1234 / 100 = 12.34
```

#### How to Solve It

Do not use one universal `read_fwf()` layout if H, D, and T have different record structures. Dispatch based on the record-type code.

#### Explanation

Fixed-width files are contracts expressed through positions. Padding, alignment, sign representation, decimal scaling, and record types all belong to that contract.

The trailer is a **reconciliation gate**. A parser can finish without raising a Python exception and still have lost or misread data.

#### Code

```python
from decimal import Decimal


def parse_implied_decimal(raw: str, scale: int) -> Decimal:
    clean = raw.strip()
    if not clean:
        raise ValueError("blank amount")
    return Decimal(clean) / (Decimal(10) ** scale)


raw_amount = "0001234"
raw_sign = "+"
value = parse_implied_decimal(raw_amount, 2)
if raw_sign == "-":
    value = -value

print(value)
```

Then accumulate detail rows and compare the final count/sum with the trailer values using controlled decimal arithmetic.

#### Expected Result / Interpretation

The detail amount is interpreted as `12.34`, the sign is applied deliberately, and the trailer comparison proves whether the file reconciles.

#### Common Mistake

Parsing the amount as `1234.0` or `12.34` without documenting the source scaling rule and without validating against the trailer.

---

# Part 4 — Advanced

### Question 31 — Design a Physical Parquet Layout for a Large Analytical Table

**Difficulty:** Advanced

#### Problem

You receive a 5 TB orders dataset. Typical queries:

```sql
SELECT country, SUM(amount)
FROM orders
WHERE order_date >= DATE '2026-09-01'
  AND order_date < DATE '2026-10-01'
GROUP BY country;
```

The table has 40 columns, but dashboards usually read only 4–6 columns. Design a starting Parquet layout considering row groups, sorting, compression, partitioning, and file sizing.

#### Solution

A reasonable starting design is:

- partition by a time level aligned with the dominant filters, subject to sufficient partition volume;
- keep the analytical representation columnar;
- select a moderate row-group size rather than a magic number;
- use a workload-appropriate codec such as zstd as a benchmark hypothesis;
- target healthy file sizes, using the roadmap's approximate **128 MB–1 GB** range as a starting hypothesis, not a universal rule;
- consider sorting within partitions by a frequently filtered/grouped column such as `country` only if the benchmark shows improved pruning/compression worth the sort cost.

#### How to Solve It

Use this decision chain:

```text
Query filters
   ↓
Partition pruning
   ↓
Projected columns
   ↓
Column pruning
   ↓
Row-group ranges/statistics
   ↓
Sort order
   ↓
Compression
   ↓
File size / parallelism
```

#### Explanation

Partitioning determines which directories/files are candidates. Row groups and statistics determine what can be skipped inside files. Columnar layout reduces unnecessary columns. Sorting can make statistics more selective. Compression reduces stored bytes and can trade CPU for I/O savings.

These knobs interact, so standardization should follow measured experiments rather than a single assumed configuration.

#### Code

A representative PyArrow write configuration might begin like:

```python
import pyarrow.dataset as ds

# `table` should already have a deliberate schema.
ds.write_dataset(
    table,
    base_dir="orders",
    format="parquet",
    partitioning=["year", "month"],
    max_rows_per_file=1_000_000,
    min_rows_per_group=100_000,
    max_rows_per_group=1_000_000,
)
```

These are **example controls**, not claimed universal production values. Run a benchmark varying one knob at a time.

#### Expected Result / Interpretation

A strong design document should contain a target hypothesis, the reason for each knob, and a measurement plan.

#### Common Mistake

Copying 1 GB files, 1 million-row groups, and one exact partition scheme to every dataset without measuring workload fit.

---

### Question 32 — Integrated Format Selection Across Pipeline Stages

**Difficulty:** Advanced

#### Problem

A new platform receives:

- real-time order events;
- batch supplier exports;
- historical analytical queries;
- partner CSV exports.

You must choose formats for landing/bronze, ingestion/messaging, silver analytical storage, and partner delivery.

Give a workload-based design using formats covered in Module 2.5.

#### Solution

One plausible design is:

```text
Source-sent representation
       ↓
Landing / Bronze
       ↓
Avro where schema-driven record transport is needed
       ↓
Typed transformation
       ↓
Silver / Gold: Parquet or ORC based on measured workload + ecosystem
       ↓
Partner delivery: CSV/JSON/Excel when the consumer contract requires it
```

#### How to Solve It

For every stage ask:

1. Who writes it?
2. Who reads it?
3. Is it record-at-a-time or analytical scan oriented?
4. What schema contract is needed?
5. What interoperability is required?

#### Explanation

Avro is naturally suited to row-oriented ingestion/CDC/messaging because records can be written and read with schema-aware serialization.

Parquet and ORC are columnar analytical formats. The exact choice between them remains workload/ecosystem dependent.

The source and analytical target do not need to have the same format. Keeping the original source in bronze can preserve replay/audit value while allowing a better analytical representation downstream.

#### Code

No single code snippet determines this architecture. A useful decision table is:

| Stage | Typical requirement | Candidate role |
|---|---|---|
| Landing | preserve source exactly | source format |
| Ingestion / events | compact typed records | Avro |
| Analytical storage | scan/filter/aggregate | Parquet or ORC |
| Interchange/cache | in-memory interchange | Arrow IPC/Feather |
| Partner delivery | external compatibility | CSV/JSON/Excel |

#### Expected Result / Interpretation

The answer should contain different representations for different jobs where justified, rather than forcing one format everywhere.

#### Common Mistake

Treating "one standard format" as equivalent to "one physical representation for every pipeline stage."

---

### Question 33 — Page Index vs Row-Group Statistics vs Bloom Filter

**Difficulty:** Advanced

#### Problem

A Parquet dataset has:

- row-group min/max statistics;
- page indexes enabled;
- a bloom filter for a selective equality predicate where supported.

Explain what each mechanism contributes and why none should be described as simply "the same thing." 

#### Solution

They provide different metadata granularity and semantics:

- **Row-group statistics** summarize values at a larger physical unit and can support row-group skipping.
- **Page indexes** add page-level navigation/statistics information, enabling finer-grained decisions inside a column chunk where the reader supports it.
- **Bloom filters** provide probabilistic membership information and can help exclude data for selective equality-style lookups where supported.

#### How to Solve It

Separate by question:

```text
Can this row group match? → row-group statistics
Can this page be narrowed/skipped? → page index information
Does this equality value probably not exist here? → bloom filter
```

#### Explanation

The mechanisms complement each other.

A bloom filter is probabilistic: a "not present" result can support exclusion, while a "maybe present" result does not prove the value exists.

Page indexes are navigation metadata, not a replacement for schema, encoding, or row-group statistics.

#### Code

No implementation is required for the conceptual question. A metadata inspection workflow is:

```python
import pyarrow.parquet as pq

pf = pq.ParquetFile("orders.parquet")
print(pf.metadata)
print(pf.schema_arrow)
```

Then use the specific metadata inspection tools available in the project's PyArrow version to inspect statistics/index-related information.

#### Expected Result / Interpretation

You should describe the mechanisms by **granularity and semantics**, not as interchangeable optimizations.

#### Common Mistake

Calling a bloom filter a min/max summary. It is a probabilistic membership structure with different behavior.

---

### Question 34 — Compaction ROI on Object Storage

**Difficulty:** Advanced

#### Problem

A partition contains 20,000 small files and is queried 200 times per day. A historical partition contains 200 small files and is queried once per year.

Should they automatically receive the same compaction priority? Explain a cost-aware policy.

#### Solution

No. The module teaches **cost-aware compaction scheduling**.

The heavily queried partition is a stronger candidate because repeated future query savings may justify compaction cost. The rarely queried partition may still be unhealthy, but its low query value means compaction should be evaluated against its cost and operational importance.

#### How to Solve It

Use the conceptual model:

```text
Priority
≈
Health Severity
× Query Importance
× Expected Savings
÷ Compaction Cost
```

This is a reasoning model, not a mandatory exact production formula.

#### Explanation

Compaction itself consumes:

- read I/O;
- CPU;
- sorting work if used;
- write I/O;
- temporary storage;
- object-storage requests.

Therefore, "unhealthy" does not automatically mean "compact immediately."

A production scheduler should consider:

- partition health;
- recentness;
- query frequency;
- expected savings;
- compaction resource budget;
- storage economics.

#### Code

```python
def conceptual_priority(health, query_importance, expected_savings, compaction_cost):
    if compaction_cost <= 0:
        raise ValueError("compaction_cost must be positive")
    return health * query_importance * expected_savings / compaction_cost
```

The inputs must be defined and normalized by the real platform; the formula is only a conceptual prioritization model.

#### Expected Result / Interpretation

The scheduler should prioritize work according to value and cost instead of compacting every partition indiscriminately.

#### Common Mistake

Using file count as the only compaction priority signal.

---

### Question 35 — Secure XML Ingestion with XSD and Quarantine

**Difficulty:** Advanced

#### Problem

An enterprise platform accepts XML feeds from external suppliers. The supplier contract provides an XSD, but the files are not trusted.

Design the security and validation sequence.

#### Solution

Use a layered sequence such as:

```text
Receive source
   ↓
Preserve original in bronze/quarantine boundary
   ↓
Parse with a defensive XML approach (`defusedxml` where applicable)
   ↓
Reject dangerous/unacceptable input
   ↓
Check syntactic XML validity
   ↓
Validate against XSD when available
   ↓
Validate business rules
   ↓
Parse into typed parent/child records
   ↓
Quarantine failures with reason + lineage
   ↓
Publish validated output
```

#### How to Solve It

Separate security from schema validation.

```text
XML security
≠
XSD validation
≠
business validation
```

#### Explanation

The module teaches XXE and entity-expansion risks, including the concept behind the "billion laughs" family of attacks. The key production lesson is not to provide an exploit recipe, but to avoid unsafe parser defaults for untrusted input.

XSD validation proves that an XML document conforms to a defined schema. It does **not** automatically eliminate every XML security risk or every business-data error.

#### Code

A defensive parse example:

```python
from defusedxml.ElementTree import fromstring

xml_bytes = b"""
<feed>
  <product id="P100">Keyboard</product>
</feed>
"""

root = fromstring(xml_bytes)
print(root.tag)
```

For XSD validation with `lxml`, the schema should be loaded into an `XMLSchema` object and the parsed document validated against it. Keep untrusted parser handling separate from the XSD validation step.

#### Expected Result / Interpretation

A secure ingestion pipeline uses defensive parsing plus schema/business validation, with rejected inputs recorded for controlled review/reprocessing.

#### Common Mistake

Saying "the XML passed XSD, so it is safe." Schema validity and parser security solve different problems.

---

### Question 36 — EBCDIC + COMP-3 Mainframe Record

**Difficulty:** Advanced

#### Problem

A mainframe feed contains text fields encoded with an EBCDIC code page and a numeric field stored as packed decimal (`COMP-3`).

Explain why generic UTF-8 text slicing is insufficient and outline the conversion pipeline.

#### Solution

The source representation contains multiple physical encodings:

```text
Mainframe bytes
   ↓
Decode EBCDIC text fields using the correct code page, e.g. cp037
   ↓
Interpret field positions from the copybook/layout specification
   ↓
Decode packed/binary numeric fields such as COMP-3
   ↓
Apply scale/sign rules
   ↓
Validate
   ↓
Convert to standard typed analytical values
```

#### How to Solve It

Identify the different layers:

1. character encoding;
2. positional layout;
3. binary numeric representation;
4. logical numeric scale;
5. target analytical type.

#### Explanation

EBCDIC is not UTF-8 or ASCII. Decoding the bytes incorrectly can produce unreadable characters even when the byte offsets are correct.

`COMP-3` stores decimal digits in packed nibbles plus a sign nibble. Its physical width is therefore not the same as a text field containing the decimal digits.

COBOL copybooks are useful because they describe how the record's fields are laid out and typed; a Data Engineer can translate those definitions into versioned parsing specifications.

#### Code

A small EBCDIC demonstration:

```python
raw = "HELLO".encode("cp037")

print(raw)
print(raw.decode("cp037"))
```

A conceptual packed-decimal representation:

```text
Digits: 1 2 3 4
Sign:   positive

Nibble sequence:
1 | 2 | 3 | 4 | C

where C is used here as a conceptual positive-sign nibble.
```

Production decoding should use a thoroughly tested implementation because real copybook definitions can contain additional conventions.

#### Expected Result / Interpretation

You should understand that one parser layer cannot treat all bytes as ordinary text.

#### Common Mistake

Decoding the entire file as UTF-8 and then trying to repair the resulting characters later.

---

### Question 37 — Integrated Excel → Typed, Partitioned, zstd Parquet

**Difficulty:** Advanced

#### Problem

You receive a monthly Excel sales report from 500 stores. Each workbook has a report title, two-row headers, merged cells, account identifiers with leading zeros, a totals row, and a sheet per region.

Design an end-to-end pipeline that turns the workbooks into trustworthy Parquet suitable for analytical queries.

#### Solution

Use:

```text
Excel files
   ↓
Bronze: preserve original files + identity
   ↓
Inspect workbook structure
   ↓
Select sheets/rows/columns deliberately
   ↓
Normalize headers
   ↓
Preserve identifier strings
   ↓
Parse dates/types
   ↓
Separate totals/notes
   ↓
Validate detail records
   ↓
Reconcile totals
   ↓
Quarantine failures
   ↓
Explicit Arrow schema
   ↓
Parquet + zstd
   ↓
Query-driven partitioning
   ↓
Healthy target file sizing
   ↓
Silver dataset
```

#### How to Solve It

Design from the target grain first:

```text
one row = one sales-detail record
```

Then define a schema before writing the parser.

#### Explanation

Topic 10 is where previous topics come together.

- Topic 01 → choose columnar analytical storage.
- Topic 02 → understand Parquet's physical units and metadata.
- Topic 03 → use PyArrow and explicit schemas.
- Topic 07 → choose compression intentionally.
- Topic 08 → choose partitions from query patterns.
- Topic 09 → prevent small files through batching/file-size control.

The source workbook itself should not be overwritten by the ingestion process.

#### Code

```python
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# Example cleaned detail DataFrame.
df = pd.DataFrame({
    "store_id": ["001", "002"],
    "account_id": ["00001234", "00007890"],
    "sales": [1234.50, 950.00],
})

table = pa.Table.from_pandas(
    df,
    schema=pa.schema([
        ("store_id", pa.string()),
        ("account_id", pa.string()),
        ("sales", pa.float64()),
    ]),
    preserve_index=False,
)

pq.write_table(
    table,
    "sales.parquet",
    compression="zstd",
)
```

#### Expected Result / Interpretation

The output is typed analytical storage while the original workbook remains available for audit/replay.

#### Common Mistake

Treating Excel as the final analytical storage format because it is the source format.

---

### Question 38 — Integrated Nested XML → Parent/Child Parquet

**Difficulty:** Advanced

#### Problem

A supplier sends nested XML:

```xml
<product id="P100">
  <name>Keyboard</name>
  <prices>
    <price currency="INR">1499.00</price>
    <price currency="USD">18.00</price>
  </prices>
</product>
```

The feed can be several gigabytes.

Design a target analytical model and parsing strategy that preserves grain and memory safety.

#### Solution

Create at least two logical tables:

```text
products
→ one row per product

product_prices
→ one row per product/currency price
```

Use streaming XML parsing with `iterparse`, explicit namespace handling if present, and `element.clear()` after processing each product.

#### How to Solve It

1. Define the parent grain.
2. Define the child grain.
3. Choose the parent key.
4. Stream records rather than building a complete XML tree.
5. Emit parent and child rows separately.
6. Convert to typed Parquet using an explicit schema.

#### Explanation

The critical idea is not "flatten all XML." It is **preserve business grain**.

The parent product should not be duplicated three or four times merely because it has repeated children. The child table can reference the parent with `product_id`.

This structure also avoids cross-products if the product later gains another repeated collection such as supplier offers.

#### Code

```python
import xml.etree.ElementTree as ET

ns = {"p": "urn:example:products"}

products = []
product_prices = []

for event, elem in ET.iterparse("products.xml", events=("end",)):
    if elem.tag == "{urn:example:products}product":
        product_id = elem.attrib["id"]
        name = elem.findtext("p:name", namespaces=ns)

        products.append({
            "product_id": product_id,
            "name": name,
        })

        for price in elem.findall("p:prices/p:price", ns):
            product_prices.append({
                "product_id": product_id,
                "currency": price.attrib["currency"],
                "amount": price.text,
            })

        elem.clear()
```

For a truly large feed, the `products` and `product_prices` Python lists should themselves be replaced with bounded batches written incrementally.

#### Expected Result / Interpretation

The production implementation should stream both parsing and output batching rather than merely switching from `parse()` to `iterparse()` while accumulating every row in RAM.

#### Common Mistake

Claiming the parser is memory bounded simply because it uses `iterparse` while keeping millions of parsed rows in ordinary Python lists.

---

### Question 39 — Integrated Mainframe Feed → Typed Parquet with Reconciliation

**Difficulty:** Advanced

#### Problem

A bank sends a daily mainframe file containing:

- EBCDIC-encoded text;
- `H` header;
- `D` detail records;
- `T` trailer;
- account IDs with fixed positions;
- amount stored as signed packed decimal/COMP-3;
- trailer count and total amount.

Design a replayable ingestion pipeline that produces typed, partitioned Parquet.

#### Solution

Use:

```text
Receive source
   ↓
Bronze: immutable raw file + file identity
   ↓
Detect encoding/layout version
   ↓
Decode EBCDIC text
   ↓
Dispatch H/D/T records
   ↓
Parse fixed-width/binary fields from layout spec
   ↓
Decode COMP-3 + scale/sign
   ↓
Validate individual records
   ↓
Accumulate detail count + amount
   ↓
Validate trailer control totals
   ↓
Quarantine bad records / reject bad file according to policy
   ↓
Convert to explicit Arrow schema
   ↓
Write partitioned zstd Parquet with healthy file sizing
   ↓
Publish safely
   ↓
Audit + metrics + lineage
```

#### How to Solve It

Make the target schema and layout version explicit before implementing the parser.

Maintain identifiers as strings, use exact decimal handling for financial amounts, and never make a control-total mismatch disappear by simply continuing the pipeline.

#### Explanation

This pipeline combines logical correctness and physical layout.

The raw bronze copy makes replay possible when:

- the parser is corrected;
- a layout version is updated;
- a business rule changes;
- an earlier failure needs backfill.

The trailer provides an external reconciliation signal. A parser process that returns exit code 0 but produces only 99,900 records when the trailer says 100,000 is not a successful ingestion.

#### Code

A layout-driven specification can be represented in Python without scattering slices throughout the parser:

```python
LAYOUT_V1 = {
    "D": {
        "record_type": {"start": 0, "end": 1, "type": "string"},
        "account_id": {"start": 1, "end": 9, "type": "string"},
        "amount": {
            "start": 9,
            "end": 15,
            "type": "comp3",
            "scale": 2,
        },
    }
}

print(LAYOUT_V1)
```

A production implementation would define the actual byte layout from the sender contract/copybook and test every field against known-good examples.

#### Expected Result / Interpretation

A strong design is replayable, auditable, safe under malformed data, and produces a modern analytical representation without losing source evidence.

#### Common Mistake

Deleting the bronze source after a successful load to save storage without considering audit and replay requirements.

---

### Question 40 — Platform-Wide Data-Format and Legacy-Ingestion Policy

**Difficulty:** Advanced

#### Problem

You are designing a company-wide policy for Module 2.5 data. Teams ingest APIs, Avro events, Excel reports, XML feeds, Parquet datasets, ORC datasets, and mainframe fixed-width files.

Create a concise policy framework that avoids universal rankings but still gives teams a consistent engineering process.

#### Solution

Use a **decision-and-evidence policy** rather than one permanent format winner.

Every dataset should document:

```text
Source representation
Target workload
Logical grain
Target schema
Format choice
Compression choice
Partition choice
File-size policy
Validation rules
Control totals where applicable
Quarantine policy
Lineage
Idempotency/replay strategy
Operational owner
Benchmark evidence when performance is material
```

A sensible default may be typed Parquet for analytical lake storage, but the policy must allow exceptions when workload or ecosystem requirements support another choice.

#### How to Solve It

Use the full Module 2.5 decision chain:

```text
Source
  ↓
Workload + Data Shape
  ↓
Logical Model / Grain
  ↓
Format
  ↓
Encoding / Compression
  ↓
Partitioning
  ↓
Row-group / File sizing
  ↓
Validation + Reconciliation
  ↓
Publication
  ↓
Monitoring + Replay
```

#### Explanation

The platform should standardize the **method of deciding**, not merely a filename extension.

Examples:

- Avro can be an appropriate row-oriented transport or ingestion representation.
- Parquet or ORC can be appropriate analytical storage depending on ecosystem/workload evidence.
- CSV/JSON/Excel can remain at external boundaries when a consumer requires them.
- XML and fixed-width sources can be preserved in bronze while transformed into typed analytical storage.

The physical design must include the lessons from Topics 07–09:

```text
Compression
+ Partitioning
+ File sizing
```

And the correctness boundary from Topic 10:

```text
Inspect
→ define grain/schema
→ parse
→ validate
→ reconcile
→ quarantine
→ publish
```

#### Code

A policy object can be represented conceptually as:

```python
policy = {
    "default_analytical_format": "parquet",
    "format_decision": "workload_and_measurement_based",
    "require_explicit_schema": True,
    "preserve_bronze_source": True,
    "require_quarantine": True,
    "require_idempotency": True,
    "require_reconciliation_when_source_provides_control_totals": True,
    "require_file_health_monitoring": True,
}

print(policy)
```

The point is the process and evidence, not the literal Python dictionary.

#### Expected Result / Interpretation

A strong architecture review answer should explain why a format/layout was selected, what alternatives were considered, what was measured, what operational guarantees exist, and how the design will change safely when the source or workload changes.

#### Common Mistake

Replacing engineering analysis with a single company rule such as "everything must be Parquet" while ignoring transport formats, external contracts, replay requirements, and workload-specific trade-offs.

---

# Final Revision Map

| Topic | Questions | Core Skills Tested |
|---|---|---|
| **01 — Row-Oriented vs Columnar Storage** | 01, 02, 26, 32, 40 | Workload-based layout choice, PAX, column pruning, pipeline placement, analytical vs record-oriented access |
| **02 — Parquet Internals** | 03, 04, 11, 21, 23, 31, 33 | `PAR1`, footer, row groups, statistics, encoding vs compression, row-group pruning, page indexes, physical layout |
| **03 — PyArrow Parquet** | 05, 12, 22, 23, 27, 31, 37, 39 | Explicit schemas, `ParquetFile`, `iter_batches`, `ParquetWriter`, datasets, publication, measurement |
| **04 — Avro** | 06, 13, 24, 32 | Nullable unions, defaults, writer/reader schema, schema resolution, conversion to Parquet |
| **05 — ORC and Format Selection** | 07, 14, 32, 40 | ORC structures, workload-based selection, ecosystem/format policy, stage-specific formats |
| **06 — Nested / Semi-Structured Data** | 08, 15, 25, 29, 38 | Grain, explode, cross-products, schema inference, XML-to-child-table modeling |
| **07 — Compression** | 04, 09, 16, 26, 31, 37, 40 | Compression ratio, codec trade-offs, fair benchmarks, zstd, encoding interaction |
| **08 — Partitioning** | 17, 27, 31, 34, 37, 39, 40 | Query-driven partitions, pruning, touched-partition replacement, operational layout |
| **09 — Small Files / File Sizing** | 18, 27, 28, 31, 34, 37, 40 | Diagnosis, target sizing, compaction, idempotency, scheduling, file health |
| **10 — Excel / XML / Fixed-Width Legacy Formats** | 10, 19, 20, 29, 30, 35, 36, 37, 38, 39, 40 | Legacy parsing, security, namespaces, streaming, fixed-width layouts, EBCDIC, COMP-3, reconciliation, bronze/silver/quarantine |

## What You Should Be Able to Do After These 40 Questions

After completing the set, you should be able to:

- reason about row versus columnar physical layouts rather than memorizing format slogans;
- explain how Parquet row groups, column chunks, pages, encodings, and statistics affect query behavior;
- read, write, inspect, and stream Parquet with PyArrow;
- understand Avro's row-oriented, schema-driven role and reason about schema evolution;
- compare ORC, Parquet, Avro, Arrow IPC/Feather, CSV, and JSON Lines by workload and pipeline stage;
- flatten and explode nested data without silently changing business grain;
- select compression settings through measurement and cost trade-offs;
- design partition layouts from query filters, cardinality, volume, and file health;
- diagnose and fix small-files problems without creating an equally serious oversized-file problem;
- ingest Excel, XML, fixed-width, and mainframe-style data safely;
- handle XML namespaces, streaming, XSD validation, and defensive parsing;
- understand EBCDIC and `COMP-3` at a working Data Engineering level;
- reconcile control totals and trailer records rather than trusting parser success alone;
- preserve bronze source evidence while producing typed silver Parquet;
- quarantine malformed or invalid inputs with enough context for investigation and replay;
- design idempotent, replayable, auditable ingestion pipelines;
- defend format, compression, partitioning, row-group, and file-size decisions in an architecture review.

### Final Principle

```text
Do not ask:

"Which format is best?"

Ask:

"What workload am I serving?
 What does the source actually contain?
 What is the grain?
 What physical layout fits the read/write pattern?
 What do measurements show?
 What operational guarantees are required?
 How will the system behave when the source or workload changes?"
```

The correct engineering decision is the **best fit for the workload and operating environment**, supported by evidence and explicit trade-offs.
