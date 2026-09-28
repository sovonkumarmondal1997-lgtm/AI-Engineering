# Reading and Writing Parquet with PyArrow

> **Stage 2 → Python for Data Engineering → Module 2.5 → Phase B → Topic 03**
>
> This module teaches the practical control layer between the physical Parquet concepts you learned in Topics 01–02 and production data pipelines. The goal is not to memorize PyArrow APIs. The goal is to understand what each API controls, why the control exists, what it means physically, and when it is appropriate.

---

## Learning Objectives

By the end of this module, you should be able to:

- Explain the role of PyArrow in Parquet processing.
- Explain the relationship between Arrow in memory and Parquet on disk.
- Create `pyarrow.Table` objects and inspect schemas.
- Read and write Parquet files with PyArrow.
- Read only required columns with `columns=`.
- Apply row filters with `filters=` and understand the limits of filter pushdown.
- Use explicit Arrow schemas as production contracts.
- Inspect files with `pyarrow.parquet.ParquetFile`.
- Inspect file, row-group, and column metadata.
- Read an individual row group.
- Process large files with `iter_batches()` instead of materializing the entire file.
- Write incrementally with `ParquetWriter`.
- Understand row-group boundaries during incremental writes.
- Control `row_group_size` and `data_page_size` deliberately.
- Configure compression and compression levels.
- Control dictionary encoding and byte-stream-split encoding.
- Write statistics and page indexes.
- Use Parquet `version` and timestamp coercion intentionally.
- Build and scan multi-file datasets with `pyarrow.dataset`.
- Write datasets with `ds.write_dataset`.
- Use Hive-style partitioning from PyArrow.
- Control rows per file and row-group bounds.
- Select deliberate behavior for existing output.
- Use predictable file-name templates.
- Detect and handle schema differences across files.
- Attach custom provenance metadata to Parquet outputs.
- Work with object storage through `pyarrow.fs`, including S3-compatible systems such as MinIO.
- Design safer temporary-output and commit patterns.
- Measure row-group size trade-offs instead of copying a magic number.
- Build tests that validate both logical data and important physical settings.
- Diagnose common PyArrow/Parquet production failures.
- Defend a Parquet read/write design in a production architecture discussion.

---

## Prerequisites

This module assumes you have already studied:

- **Topic 01 — Row-Oriented vs Columnar Storage**
- **Topic 02 — Parquet Internals: Row Groups, Pages, and Statistics**
- Earlier Stage 2 Python/Data Engineering foundations
- Basic Python
- Basic DataFrame concepts
- Basic file handling
- Basic Arrow concepts from Module 2.4

You should already be comfortable with the following mental model:

```text
Rows
Columns
Columnar storage
Row groups
Column chunks
Pages
Statistics
Column pruning
Predicate skipping
```

Topic 02 taught you **what the Parquet structures mean**. Topic 03 answers a new question:

> **How do I deliberately control those physical concepts from Python?**

This distinction is important. Topic 02 is about understanding the file. Topic 03 is about engineering the read/write process that creates and consumes the file.

---

# 1. Why PyArrow Matters

## 1.1 What is PyArrow?

**PyArrow** is the Python interface to Apache Arrow's in-memory structures and its integrations with file formats and data systems, including Apache Parquet.

For this module, think of PyArrow as the layer that lets Python code move structured tabular data between memory and durable storage while retaining strong typing and access to physical-storage controls.

A simplified mental model is:

```text
Python data
    ↓
Arrow Table / RecordBatch
    ↓
PyArrow Parquet writer
    ↓
Parquet file
```

And on the read path:

```text
Parquet file
    ↓
PyArrow reader
    ↓
Arrow Table / RecordBatch
    ↓
Python processing
```

PyArrow is useful because the Arrow model and Parquet model fit together naturally:

- Arrow is a **columnar representation in memory**.
- Parquet is a **columnar storage format on disk**.
- PyArrow provides APIs for moving between them.

The Apache Arrow documentation describes `ParquetFile`, `read_table`, datasets, and S3-compatible filesystems as first-class parts of this ecosystem. citeturn617091search0turn617091search3

## 1.2 Why not just use pandas?

pandas is excellent for many Python data tasks, but a production data engineer often needs more control than a DataFrame convenience API provides.

You may need to answer questions such as:

- What is the exact Arrow/Parquet schema?
- How many row groups were written?
- How large is each row group?
- Which compression codec is used?
- Are statistics written?
- Can I process the file one batch at a time?
- How do I write many files with a partition layout?
- How do I publish files to object storage?

PyArrow exposes these lower-level choices directly.

## 1.3 Arrow and Parquet are related, not identical

Do not say:

> "Arrow is Parquet in memory."

That statement is too loose.

A better model is:

```text
Arrow
→ in-memory columnar data model and interchange structures

Parquet
→ persistent columnar file format with pages, row groups, metadata, encodings, etc.
```

The two work well together because they both use strongly typed columnar concepts, but their physical representations are different.

## 1.4 Where PyArrow fits in a production stack

A common pattern looks like:

```text
Source API / files / database / stream
                ↓
         Python ingestion
                ↓
       Arrow Table / batches
                ↓
          Validation
                ↓
        Parquet writer
                ↓
      Object storage / lake
                ↓
     DuckDB / Polars / Spark / warehouse
```

The exact architecture varies. The important point is that PyArrow can be used as a **physical-storage control point** rather than only as a convenience library.

### Production implication

If your team treats Parquet as a production contract, a writer that explicitly controls schema, file boundaries, row groups, statistics, and publication behavior is much easier to reason about than a pipeline that simply calls `to_parquet()` and hopes defaults remain appropriate forever.

---

# 2. Arrow in Memory vs Parquet on Disk

## 2.1 Arrow Table: your main in-memory object

The primary tabular object used throughout this module is `pyarrow.Table`.

Conceptually:

```text
Table
├── Schema
│   ├── order_id: int64
│   ├── country: string
│   └── amount: double
│
├── Column array: order_id
├── Column array: country
└── Column array: amount
```

Create one with `pa.table()`:

```python
import pyarrow as pa

orders = pa.table(
    {
        "order_id": [1, 2, 3],
        "country": ["IN", "US", "UK"],
        "amount": [100.5, 200.0, 150.25],
    }
)

print(orders)
print(orders.schema)
```

### What this code does

1. Imports the Arrow package.
2. Creates three named columns.
3. Lets Arrow infer types for this simple example.
4. Produces a `Table` containing the columns.
5. Prints the table and its schema.

For simple examples, inference is convenient. Production pipelines often need explicit schemas; that becomes a major topic later in this chapter.

## 2.2 Schema inspection

The schema is the type contract associated with the Arrow table.

For example:

```python
print(orders.schema)
```

A conceptual result might look like:

```text
order_id: int64
country: string
amount: double
```

The exact display formatting can vary by Arrow release, so do not build production logic around pretty-printed output. Inspect structured properties in code instead.

## 2.3 A useful mental separation

Keep these layers separate:

```text
Logical business data
        ↓
Arrow schema + Arrow arrays
        ↓
PyArrow write configuration
        ↓
Parquet physical layout
        ↓
File + metadata + bytes
```

This makes debugging much easier.

If a downstream system sees `amount` as text, ask:

1. Was the Arrow schema wrong?
2. Was the input table wrong?
3. Did the writer coerce a type?
4. Is the reader interpreting the logical type differently?

Do not jump immediately to "Parquet is broken."

---

# 3. Your First Parquet Read

## 3.1 Write a tiny file first

Before reading Parquet, create a known file.

```python
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

output_path = Path("orders.parquet")

table = pa.table(
    {
        "order_id": [1, 2, 3, 4],
        "country": ["IN", "US", "IN", "UK"],
        "amount": [100.5, 200.0, 150.25, 75.0],
    }
)

pq.write_table(table, output_path)
print(output_path)
```

The core operation is:

```python
pq.write_table(table, "orders.parquet")
```

Conceptually, PyArrow takes the Arrow table and creates a Parquet file containing schema, row groups, column chunks, pages, encodings, compression, and file metadata.

Do not assume the defaults are bad. Defaults are often useful. The engineering principle is:

> **Use defaults deliberately, not invisibly.**

Current PyArrow documentation exposes `write_table()` options including `row_group_size`, `version`, `compression`, `write_statistics`, `compression_level`, `use_byte_stream_split`, `coerce_timestamps`, `write_page_index`, and other controls. Exact defaults can vary across versions, so inspect your installed version when a default matters to a production contract. citeturn467189search2

## 3.2 Read it back

```python
read_back = pq.read_table("orders.parquet")

print(read_back)
print(read_back.schema)
```

This reads the Parquet dataset represented by that file into an Arrow `Table`.

For a manageable file, this is wonderfully convenient.

For a file that is larger than the memory budget, it may be the wrong abstraction. Later we will use `iter_batches()` for progressive processing.

## 3.3 Converting to pandas

You can convert an Arrow table to pandas:

```python
df = read_back.to_pandas()
print(df)
```

This is useful when the next step is genuinely a pandas operation.

But do not form the habit:

```text
Parquet
 ↓
read entire file
 ↓
pandas
```

for every workload.

That pattern materializes the selected data in memory and may add another memory representation.

### Production rule

Move into pandas because the workload needs pandas—not because pandas is familiar.

---

# 4. Your First Parquet Write

## 4.1 The simplest production-relevant form

Start simple:

```python
import pyarrow as pa
import pyarrow.parquet as pq

schema = pa.schema(
    [
        pa.field("order_id", pa.int64(), nullable=False),
        pa.field("country", pa.string(), nullable=False),
        pa.field("amount", pa.float64(), nullable=False),
    ]
)

table = pa.Table.from_pydict(
    {
        "order_id": [1, 2, 3],
        "country": ["IN", "US", "UK"],
        "amount": [100.5, 200.0, 150.25],
    },
    schema=schema,
)

pq.write_table(table, "orders.parquet")
```

This version makes an important production choice explicit: the schema.

## 4.2 Why explicit schema matters

Schema inference can be correct on today's input and wrong on tomorrow's input.

Consider values such as:

```text
00123
00124
00125
```

These might be:

- strings
- account codes
- customer identifiers
- postal codes

They are not necessarily integers just because they contain digits.

Similarly:

```text
1
2
None
3.5
```

can lead to different type interpretations depending on the source and transformation path.

Explicit schemas reduce ambiguity.

### Production benefits

An explicit schema can improve:

- reproducibility
- interoperability
- testability
- downstream expectations
- incident diagnosis
- schema-contract enforcement

It does not solve all schema-evolution problems. You still need compatibility policies and validation when multiple files or producers are involved.

---

# 5. Reading Selected Columns

Column selection is one of the first physical optimizations you can control from Python.

## 5.1 The basic API

```python
selected = pq.read_table(
    "orders.parquet",
    columns=["country", "amount"],
)

print(selected)
```

The query or application only asks for two columns.

Conceptually:

```text
Parquet file
├── order_id column chunk   ← not requested
├── country column chunk    ← requested
├── amount column chunk     ← requested
└── created_at column chunk ← not requested
```

The reader can use the Parquet physical organization to avoid unnecessary column data.

This is the practical form of **projection pruning** or **column pruning**.

## 5.2 Why fewer columns can matter

Selecting fewer columns can reduce:

- bytes read
- decompression work
- decoded values in memory
- data transferred over a remote filesystem
- downstream processing work

But the actual improvement depends on the file layout, storage system, engine implementation, selected columns, cache state, and query itself.

Never translate:

> "I selected 2 of 30 columns"

into:

> "The query must be 15× faster."

There is no such universal relationship.

## 5.3 Stop and Think

A Parquet file has 30 columns. Your transformation uses only 3.

**Question:** What should you consider before reading the file?

**Answer:** Read only the required columns, for example with `columns=[...]`, unless the transformation genuinely needs the complete table.

The reason is physical: unused column chunks do not need to become part of the decoded result.

---

# 6. Filtering Rows

## 6.1 `filters=`

PyArrow can accept filters when reading Parquet:

```python
filtered = pq.read_table(
    "orders.parquet",
    filters=[("country", "=", "IN")],
)

print(filtered)
```

For more complex expressions, the accepted form depends on the API being used; the practical point here is that a filter can be expressed to the Parquet reader rather than materializing everything and filtering afterward.

## 6.2 What does the filter actually buy us?

A filter can enable the reader to reduce work when metadata and layout allow it.

Conceptually:

```text
Filter requested
      ↓
Can metadata prove some data cannot match?
      ↓
Yes ─────────────── No
 ↓                    ↓
skip                  read
irrelevant            candidate
units                 data
```

For Parquet this can interact with:

- row-group statistics
- page-level information
- partition metadata when using datasets
- the physical ordering of values
- engine/reader implementation

## 6.3 Requesting a filter vs guaranteeing pruning

These are different:

```text
I supplied a filter
```

versus:

```text
The engine skipped every irrelevant byte
```

The second statement is much stronger and may be false.

A filter still has to be executed. If statistics are broad or the predicate is not selective, the reader may still need to inspect a large amount of data.

Current PyArrow documentation describes filtering/predicate pushdown for Parquet and dataset scanning, but the amount of physical data skipped depends on the available metadata and scan plan. citeturn617091search0turn693043search4

---

# 7. Explicit Schemas

## 7.1 Why schemas are a production concern

An analytical pipeline often runs repeatedly:

```text
run 1
run 2
run 3
...
run 500
```

If the inferred representation changes between runs, downstream systems can break in ways that are difficult to debug.

Typical risks include:

- integer becoming floating-point because of nulls
- timestamps arriving at different resolutions
- decimal values represented as general floating-point values
- identifier strings accidentally interpreted as numbers
- mixed Python values widening a type
- source-system changes silently affecting the output contract

## 7.2 Build an Arrow schema

```python
import pyarrow as pa

schema = pa.schema(
    [
        pa.field("order_id", pa.int64(), nullable=False),
        pa.field("country", pa.string(), nullable=False),
        pa.field("amount", pa.decimal128(12, 2), nullable=False),
        pa.field("created_at", pa.timestamp("us", tz="UTC"), nullable=False),
    ]
)

print(schema)
```

This says, in plain language:

- `order_id` is a 64-bit integer.
- `country` is text.
- `amount` is a decimal with precision 12 and scale 2.
- `created_at` is a timestamp stored at microsecond resolution with UTC timezone semantics in Arrow.

## 7.3 Make the data conform to the schema

A useful pattern is:

```python
table = pa.table(
    {
        "order_id": [1, 2, 3],
        "country": ["IN", "US", "UK"],
        "amount": ["100.50", "200.00", "150.25"],
        "created_at": [
            "2025-01-01T10:00:00Z",
            "2025-01-01T10:05:00Z",
            "2025-01-01T10:10:00Z",
        ],
    }
)
```

For real production code, build typed Arrow arrays intentionally rather than relying on string parsing inside this example.

One explicit way to build a typed table is to create correctly typed Python/Arrow values before constructing the table. The important lesson is the contract, not a particular parser.

## 7.4 Schema is not only a type declaration

Think of a schema as:

```text
Field name
   +
Physical/logical type
   +
Nullability
   +
Business meaning
```

The final business meaning does not live entirely in Arrow. But the schema is a strong technical boundary.

### Production implication

When a pipeline writes Parquet that other teams will consume, schema policy should usually be explicit enough that a test can reject an unexpected type before publication.

---

# 8. `ParquetFile` and Metadata Inspection

## 8.1 Why `ParquetFile` exists

Use `ParquetFile` when you need controlled access to a specific file and its metadata.

```python
import pyarrow.parquet as pq

pf = pq.ParquetFile("orders.parquet")

print(pf.metadata)
print(pf.schema_arrow)
```

The current PyArrow documentation exposes file metadata through `ParquetFile.metadata`, and the Arrow schema through `ParquetFile.schema_arrow`. It also exposes row-group-oriented methods such as `read_row_group`. citeturn617091search0

## 8.2 File-level information

Useful properties include:

```python
print("rows:", pf.metadata.num_rows)
print("row groups:", pf.metadata.num_row_groups)
print("schema:")
print(pf.schema_arrow)
```

Conceptually:

```text
ParquetFile
│
├── file metadata
│   ├── number of rows
│   ├── number of row groups
│   ├── writer/version information
│   └── file-level metadata
│
└── Arrow schema
```

## 8.3 Row-group metadata

```python
metadata = pf.metadata

for row_group_index in range(metadata.num_row_groups):
    row_group = metadata.row_group(row_group_index)
    print("row group:", row_group_index)
    print("rows:", row_group.num_rows)
    print("bytes:", row_group.total_byte_size)
```

The exact properties exposed on metadata objects can vary by PyArrow version. Prefer using documented structured properties rather than scraping string representations.

## 8.4 Column metadata inside a row group

```python
for row_group_index in range(pf.metadata.num_row_groups):
    row_group = pf.metadata.row_group(row_group_index)

    print(f"Row group {row_group_index}")

    for column_index in range(row_group.num_columns):
        column = row_group.column(column_index)
        print("  path:", column.path_in_schema)
        print("  compression:", column.compression)
        print("  encodings:", column.encodings)
        print("  compressed size:", column.total_compressed_size)
        print("  uncompressed size:", column.total_uncompressed_size)
```

This is where Topic 02 turns into actual engineering.

You can now answer:

> "What did my writer actually create?"

rather than guessing.

---

# 9. Reading Row Groups

A Parquet file is organized into row groups. `ParquetFile` lets you read one directly.

```python
first_group = pf.read_row_group(0)

print(first_group)
```

## 9.1 Why read a row group directly?

Useful cases include:

- investigating physical layout
- building specialized batch processing loops
- debugging one region of a file
- processing a large file in controlled chunks
- understanding how file layout maps to memory

## 9.2 A row group is not a memory limit

This is important.

A row group is a **physical file organization unit**. It is not automatically equivalent to:

```text
"This operation will always use only X MB of RAM."
```

Suppose a single row group contains a large amount of data. Reading it may still consume substantial memory.

Think:

```text
row group
→ storage granularity

batch
→ processing granularity

memory budget
→ resource constraint
```

These are related, but not identical.

---

# 10. Reading in Batches with `iter_batches`

## 10.1 Why batch reading exists

`read_table()` is convenient because it gives you the whole selected result as one Arrow table.

For very large files, you may want this instead:

```python
for batch in pf.iter_batches(batch_size=100_000):
    print(batch.num_rows)
```

The idea is:

```text
Large Parquet file
       ↓
   batch 1
       ↓
   process
       ↓
   batch 2
       ↓
   process
       ↓
   batch 3
       ↓
   process
```

rather than:

```text
Large Parquet file
       ↓
load everything
       ↓
large in-memory table
```

## 10.2 What is a RecordBatch?

An Arrow `RecordBatch` is a rectangular set of rows with a schema.

Think of it as:

```text
Schema
+
A manageable batch of rows
```

You can inspect it:

```python
for batch in pf.iter_batches(batch_size=100_000):
    print(batch.schema)
    print(batch.num_rows)
    print(batch.num_columns)
```

## 10.3 Batch size is a control knob

A larger batch can reduce loop overhead and may improve throughput.

A smaller batch can reduce peak working memory and provide finer control.

Therefore:

```text
small batch
→ lower per-batch memory
→ potentially more overhead

large batch
→ more work per iteration
→ potentially higher memory
```

There is no universal best batch size.

## 10.4 Bounded-memory thinking

`iter_batches()` can support bounded-memory processing because you consume the dataset progressively rather than materializing the full result at once.

But avoid saying:

> "`iter_batches(batch_size=100_000)` guarantees a 100,000-row fixed memory footprint."

The real footprint also depends on:

- selected columns
- value widths
- nested structures
- decoding state
- downstream transformations
- buffering/readahead
- Python objects you create inside the loop

### Production rule

A batch-processing design is a **memory-control strategy**, not a magic memory number.

---

# 11. Bounded-Memory Processing

## 11.1 Full read versus progressive read

Compare these patterns.

### Full materialization

```python
import pyarrow.parquet as pq

table = pq.read_table("large/orders.parquet")

result = table.column("amount").combine_chunks().sum()
print(result)
```

This is convenient, but the selected data is materialized as a table.

### Progressive processing

```python
import pyarrow.compute as pc
import pyarrow.parquet as pq

running_total = 0.0

pf = pq.ParquetFile("large/orders.parquet")

for batch in pf.iter_batches(
    batch_size=100_000,
    columns=["amount"],
):
    amount = batch.column(batch.schema.get_field_index("amount"))
    batch_total = pc.sum(amount).as_py()
    if batch_total is not None:
        running_total += batch_total

print(running_total)
```

The second example has an important advantage: it requests only the required column and processes it progressively.

## 11.2 A more explicit batch-processing helper

```python
from collections.abc import Callable

import pyarrow as pa
import pyarrow.parquet as pq


def process_in_batches(
    path: str,
    columns: list[str],
    batch_size: int,
    process_batch: Callable[[pa.RecordBatch], None],
) -> None:
    """Read a Parquet file progressively and process one batch at a time."""
    parquet_file = pq.ParquetFile(path)

    for batch in parquet_file.iter_batches(
        batch_size=batch_size,
        columns=columns,
    ):
        process_batch(batch)
```

This example demonstrates an important engineering separation:

```text
I/O policy
     ↓
iter_batches()
     ↓
application-specific batch processing
```

The reader does not need to know what the application does with each batch.

## 11.3 When this pattern is useful

Common production uses include:

- large aggregations
- validation scans
- transformation pipelines
- conversion from one file layout to another
- generating summary statistics
- writing derived Parquet files
- feeding a downstream API or processing stage that accepts batches

---

# 12. `ParquetWriter` and Incremental Writes

## 12.1 Why does `ParquetWriter` exist?

`pq.write_table()` is excellent when you already have the complete Arrow table.

But suppose data arrives in batches:

```text
batch 1
batch 2
batch 3
...
batch 1000
```

You do not want to build one enormous Arrow table just to write one file.

That is the role of `ParquetWriter`.

## 12.2 Basic writer lifecycle

```python
import pyarrow.parquet as pq

writer = pq.ParquetWriter(
    "orders_incremental.parquet",
    schema,
)

try:
    for batch in batches:
        writer.write_batch(batch)
finally:
    writer.close()
```

Depending on the exact object available in your pipeline, `write_table()` can also be used on the writer:

```python
writer = pq.ParquetWriter("orders_incremental.parquet", schema)

try:
    for table in tables:
        writer.write_table(table)
finally:
    writer.close()
```

Current PyArrow documentation exposes `write_table()` and `write_batch()` on `ParquetWriter`, both with optional `row_group_size`. citeturn467189search1

## 12.3 Why `close()` matters

Parquet is not simply a stream of independent rows.

A valid file needs final metadata to be written. If a process exits before the writer is correctly finalized, the output may be incomplete or unreadable.

That is why a `try/finally` pattern is useful.

A context-manager pattern is also appropriate when supported by the installed release:

```python
with pq.ParquetWriter("orders_incremental.parquet", schema) as writer:
    for batch in batches:
        writer.write_batch(batch)
```

For code that must support multiple pinned versions, verify context-manager support against your deployed PyArrow version.

## 12.4 How incremental writes relate to row groups

Each call to `write_batch()` or `write_table()` contributes data to the Parquet file. The writer then organizes the rows into row groups according to its row-group rules and the `row_group_size` supplied to the write operation.

A key point is:

> **One Python batch is not automatically identical to one Parquet row group in every configuration.**

The writer may split large inputs, and the row-group size is a separate physical setting.

---

# 13. Streaming Read → Transform → Write

This is one of the most important production patterns in the module.

## 13.1 Architecture

```text
Existing Parquet
      ↓
iter_batches()
      ↓
Transform one RecordBatch
      ↓
ParquetWriter.write_batch()
      ↓
New Parquet
```

## 13.2 Complete example

```python
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

INPUT = Path("input/orders.parquet")
OUTPUT = Path("output/orders_enriched.parquet")

input_file = pq.ParquetFile(INPUT)

output_schema = pa.schema(
    [
        pa.field("order_id", pa.int64(), nullable=False),
        pa.field("country", pa.string(), nullable=False),
        pa.field("amount", pa.float64(), nullable=False),
        pa.field("amount_with_tax", pa.float64(), nullable=False),
    ]
)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

writer = pq.ParquetWriter(
    OUTPUT,
    schema=output_schema,
    compression="zstd",
)

try:
    for batch in input_file.iter_batches(
        batch_size=100_000,
        columns=["order_id", "country", "amount"],
    ):
        order_id = batch.column(batch.schema.get_field_index("order_id"))
        country = batch.column(batch.schema.get_field_index("country"))
        amount = batch.column(batch.schema.get_field_index("amount"))

        amount_with_tax = pc.multiply(amount, pa.scalar(1.18))

        output_batch = pa.RecordBatch.from_arrays(
            [order_id, country, amount, amount_with_tax],
            schema=output_schema,
        )

        writer.write_batch(output_batch, row_group_size=100_000)
finally:
    writer.close()
```

## 13.3 What this example demonstrates

The important engineering properties are:

1. The input is read incrementally.
2. Only required input columns are requested.
3. One batch is transformed at a time.
4. The output schema is explicit.
5. The output writer is configured deliberately.
6. The writer is finalized even if an exception occurs.

## 13.4 What it does not guarantee

It does not guarantee a fixed RAM usage.

The true peak memory depends on:

- the batch size
- the size of each value
- temporary arrays created during transformation
- Parquet encoding/compression buffers
- Arrow memory allocator behavior
- Python objects created by your transformation

Measure memory for the workload you actually care about.

---

# 14. Controlling Row Groups

## 14.1 Why `row_group_size` matters

`row_group_size` controls the maximum number of rows in each row group when writing a table or batch through the Parquet writer APIs.

Current PyArrow documentation describes the default behavior as using the smaller of the input row count and a default maximum of 1,048,576 rows when `row_group_size` is not explicitly supplied to a writer write operation; exact behavior and defaults should be verified against the version you deploy. citeturn467189search1

The key engineering idea is not the default number.

It is this:

```text
row_group_size
→ changes physical granularity
```

## 14.2 Small row groups

Potential benefits:

- finer-grained statistics
- potentially finer skipping
- smaller units of work
- more opportunities for parallel scheduling

Potential costs:

- more row-group metadata
- potentially weaker compression
- more overhead
- greater metadata complexity

## 14.3 Large row groups

Potential benefits:

- fewer metadata entries
- larger contiguous encoding/compression units
- potentially better compression
- fewer row groups to manage

Potential costs:

- coarser skipping
- larger units to read
- more writer and reader working memory
- reduced granularity for some workloads

Use the mental model:

| Row-group choice | Potential benefit | Potential cost |
|---|---|---|
| Smaller | finer granularity and potentially stronger skipping | more metadata/overhead and possible compression loss |
| Larger | larger encoding/compression units and less metadata | coarser skipping and potentially more memory |

This is a workload trade-off, not a universal constant.

## 14.4 Example

```python
pq.write_table(
    table,
    "orders_100k.parquet",
    row_group_size=100_000,
)
```

Then inspect what was actually written:

```python
pf = pq.ParquetFile("orders_100k.parquet")
print("row groups:", pf.metadata.num_row_groups)

for i in range(pf.metadata.num_row_groups):
    rg = pf.metadata.row_group(i)
    print(i, "rows:", rg.num_rows)
```

Never assume that because you requested a setting, the resulting file has exactly the mental model you imagined. Inspect it.

---

# 15. Controlling Pages and Writer Options

Parquet contains pages inside column chunks. PyArrow exposes several controls that affect how the file is written.

The important engineering approach is to classify each option by what it changes physically.

| Option | Controls | Why it matters | What to measure |
|---|---|---|---|
| `row_group_size` | rows per row group | read/skipping granularity, memory, metadata | row-group count, query time, memory |
| `data_page_size` | approximate encoded page target | page granularity and overhead | file size, read behavior, metadata |
| `compression` | codec | storage/CPU trade-off | size, write time, read time |
| `compression_level` | codec-specific intensity | CPU vs size trade-off | size and CPU/time |
| `use_dictionary` | dictionary encoding eligibility | representation efficiency | encodings, size, query time |
| `write_statistics` | statistics emission | pruning potential | metadata and filtered reads |
| `version` | available Parquet logical types/features | interoperability | reader compatibility |
| `coerce_timestamps` | timestamp resolution on write | precision and compatibility | schema and round-trip values |
| `use_byte_stream_split` | encoding for eligible columns | encoding efficiency for some numeric data | encoding + file size |
| `write_page_index` | page-level index writing | finer-grained metadata | metadata availability and reader behavior |

Current PyArrow documentation lists these options on `write_table()` and `ParquetWriter`; some arguments are version-sensitive, so production environments should pin and test the PyArrow version. citeturn467189search1turn467189search2

---

# 16. Data Page Size

## 16.1 What `data_page_size` means

```python
pq.write_table(
    table,
    "orders.parquet",
    data_page_size=1 * 1024 * 1024,
)
```

The value is a target threshold for the approximate encoded size of data pages inside a column chunk. It is not a guarantee that every page will have exactly that many bytes. Current PyArrow documentation describes a default target of approximately 1 MiB when this parameter is not supplied. citeturn467189search1turn467189search2

## 16.2 Why change it?

A page is a smaller physical unit than a row group.

Changing page sizing can affect:

- page-level granularity
- metadata/index considerations
- writer behavior
- memory and read behavior

But do not tune it in isolation.

A sensible experiment changes **one variable at a time**.

---

# 17. Compression, Dictionaries, and Statistics

## 17.1 Compression

A simple writer:

```python
pq.write_table(
    table,
    "orders.parquet",
    compression="zstd",
)
```

Common choices include codecs such as:

- `snappy`
- `zstd`
- `gzip`
- `brotli`
- `lz4`
- `none`

Exact availability depends on the PyArrow build and environment.

Compression is not the same thing as Parquet encoding.

A useful model is:

```text
Logical values
      ↓
Parquet encoding
      ↓
Compression codec
      ↓
Bytes on disk
```

Topic 07 goes much deeper into codec selection, so this module only needs enough knowledge to configure a writer responsibly.

## 17.2 Compression level

Some codecs expose levels:

```python
pq.write_table(
    table,
    "orders.parquet",
    compression="zstd",
    compression_level=3,
)
```

The meaning of a numeric level is codec-specific.

Do not assume:

```text
level 9 = universally better
```

A higher level may reduce file size while increasing CPU and write time, and the incremental size reduction may diminish.

Current PyArrow documentation states that compression levels are codec-specific and that unsupported levels/codecs can raise exceptions. citeturn467189search1

## 17.3 Dictionary encoding

```python
pq.write_table(
    table,
    "orders.parquet",
    use_dictionary=True,
)
```

Dictionary encoding can be useful when a column repeats a relatively small set of values.

For example:

```text
country
IN
IN
US
IN
UK
IN
US
```

Conceptually:

```text
Dictionary:
0 → IN
1 → US
2 → UK

Indices:
0, 0, 1, 0, 2, 0, 1
```

That can be much more compact than storing every string independently.

For a high-cardinality identifier column:

```text
customer_id
C-0000000001
C-0000000002
C-0000000003
...
```

dictionary benefits may be limited, and the writer can abandon dictionary encoding when it is no longer effective.

Current PyArrow documentation allows `use_dictionary` to be configured globally or for selected columns. It also documents interactions with other encoding controls. citeturn467189search1

## 17.4 Statistics

Statistics are critical to predicate pruning.

```python
pq.write_table(
    table,
    "orders.parquet",
    write_statistics=True,
)
```

At the row-group/column-chunk level, statistics can include values such as:

- minimum
- maximum
- null count

Conceptually:

```text
Writer
  ↓
write statistics
  ↓
Parquet metadata
  ↓
reader sees min/max/null count
  ↓
may skip irrelevant row groups
```

Disabling statistics can reduce the metadata available to readers and therefore reduce some pruning opportunities.

But:

> **Statistics are an optimization input, not a promise that pruning will occur.**

---

# 18. Timestamp and Encoding Controls

## 18.1 Parquet version

You can specify a Parquet logical-type/version target:

```python
pq.write_table(
    table,
    "orders.parquet",
    version="2.6",
)
```

Current PyArrow documentation lists `1.0`, `2.4`, and `2.6` as version choices for its Parquet writer APIs. These settings affect which Parquet logical types/features are available, and consumer compatibility must be considered. citeturn467189search1

Do not hard-code a version merely because it is newer.

Ask:

```text
Which readers consume this file?
What features do they support?
What version is the deployment pinned to?
```

## 18.2 Timestamp coercion

Use `coerce_timestamps` when you deliberately need a timestamp resolution:

```python
pq.write_table(
    table,
    "orders.parquet",
    coerce_timestamps="us",
)
```

Current PyArrow documentation supports coercion targets such as milliseconds (`ms`) and microseconds (`us`). It also documents behavior around loss of precision and the separate `allow_truncated_timestamps` option. citeturn467189search1turn467189search2

### Why this matters

Suppose your in-memory timestamp contains nanosecond precision:

```text
2025-03-01 10:00:00.123456789
```

Coercing to microseconds can preserve:

```text
2025-03-01 10:00:00.123456
```

but the remaining nanoseconds are no longer represented.

That is a data contract decision.

### Production rule

Never treat timestamp coercion as a harmless formatting operation. It can change information content.

## 18.3 Legacy INT96 behavior

PyArrow also exposes an explicit legacy option for writing INT96 timestamps:

```python
pq.write_table(
    table,
    "legacy.parquet",
    use_deprecated_int96_timestamps=True,
)
```

Only use this when a real compatibility requirement justifies it. New production outputs should normally avoid introducing legacy representation without a consumer reason.

When migrating old data, inspect what is already present rather than assuming every timestamp column uses the same representation.

## 18.4 Byte-stream split

```python
pq.write_table(
    table,
    "numeric.parquet",
    use_byte_stream_split=["sensor_value"],
    compression="zstd",
)
```

`BYTE_STREAM_SPLIT` is an encoding designed for eligible fixed-width values such as floating-point data and some fixed-size binary/decimal representations.

Current PyArrow documentation describes it as an encoding option and notes that combining it with a compression codec is useful for size reduction. If dictionary encoding and byte-stream split are both enabled for a column, dictionary encoding takes precedence where applicable. citeturn467189search1turn467189search2

The key distinction is:

```text
BYTE_STREAM_SPLIT
→ encoding choice

ZSTD / SNAPPY / ...
→ compression choice
```

---

# 19. Page Index

## 19.1 Writing a page index

```python
pq.write_table(
    table,
    "orders.parquet",
    write_page_index=True,
)
```

A page index provides page-level metadata in a centralized structure, extending the coarse-grained idea of row-group statistics.

Conceptually:

```text
Row group statistics
→ coarse decision

Page index
→ finer page-level decision
```

## 19.2 An important PyArrow reader caveat

Current PyArrow documentation states that `write_page_index=True` writes page-index statistics, but PyArrow does not yet use the page index on the read side for its own reads. citeturn467189search6

That is exactly the kind of production detail you should know.

The feature can be useful for ecosystem interoperability, but you must not infer:

```text
I enabled page indexes
→ this particular PyArrow version must now prune pages during reads
```

That conclusion is not justified.

## 19.3 Inspect what was written

The right workflow is:

```text
Enable feature
    ↓
Inspect metadata
    ↓
Run target readers
    ↓
Measure behavior
```

---

# 20. Per-Column Settings

Different columns have different physical characteristics.

Consider:

```text
country       → low cardinality strings
status        → low cardinality strings
action_id     → high cardinality identifiers
sensor_value  → floating-point measurements
created_at    → timestamp
```

A sensible physical strategy may therefore be column-aware.

For example, current PyArrow APIs permit compression to be supplied as a mapping and dictionary use to be specified for selected columns:

```python
pq.write_table(
    table,
    "orders.parquet",
    compression={
        "country": "zstd",
        "status": "zstd",
        "sensor_value": "zstd",
    },
    use_dictionary=["country", "status"],
)
```

Current documentation explicitly shows per-column compression and selected-column dictionary configuration. citeturn617091search0

If you need exact per-column encoding controls, use the API appropriate for your installed PyArrow version. Do not invent a dictionary-shaped parameter when the version you deploy expects a boolean or list.

### Senior-engineer question

For every column, ask:

> "What is the distribution of this data, and which physical representation is likely to serve the workload?"

Do not optimize every column identically simply because one setting was convenient.

---

# 21. Writing Multi-File Parquet Datasets

A single Parquet file is useful for learning. Production analytical datasets are often a **collection of Parquet files**.

## 21.1 File versus dataset

Keep these concepts separate:

```text
Parquet file
├── Row groups
│   ├── Column chunks
│   └── Pages
└── Footer

Parquet dataset
├── File A
├── File B
├── File C
└── Directory/partition metadata
```

The dataset layer introduces additional concerns:

- file discovery
- partitioning
- dataset schema
- file-level pruning
- multiple writers
- file count
- object-store listing

PyArrow's dataset API is specifically designed for tabular multi-file datasets and supports filesystem abstraction, schema discovery, filtering, projection, and iterative reads. citeturn693043search4

## 21.2 Why many files?

A multi-file design can provide:

- parallel read opportunities
- independent partition replacement
- easier incremental ingestion
- manageable file sizes
- lifecycle operations at a file or partition level

But many files can become a liability when each file is too small. That becomes a later topic in this module.

---

# 22. `pyarrow.dataset`

## 22.1 Create a dataset

```python
import pyarrow.dataset as ds

orders_dataset = ds.dataset(
    "data/orders",
    format="parquet",
)

print(orders_dataset.schema)
print(orders_dataset.files)
```

The `Dataset` object represents a potentially multi-file collection of data.

Current Apache Arrow documentation describes dataset discovery as a process that can crawl directories, infer schema, and represent files as fragments. Creating the Dataset object itself does not necessarily materialize all data into memory. citeturn693043search4

## 22.2 Dataset mental model

```text
Dataset
│
├── File fragment A
├── File fragment B
├── File fragment C
│
└── Dataset schema
```

This is different from:

```python
table = pq.read_table("data/orders")
```

because the dataset API is explicitly about describing and scanning collections of files.

---

# 23. Dataset Filtering

## 23.1 Dataset expressions

A basic scan can look like:

```python
import pyarrow.dataset as ds

result = orders_dataset.to_table(
    columns=["country", "amount"],
    filter=ds.field("country") == "IN",
)

print(result)
```

This combines two ideas:

```text
Projection
→ columns=[...]

Filter
→ filter=...
```

## 23.2 Why use expressions?

Expressions provide a structured representation of what the scan needs.

That gives the dataset machinery an opportunity to apply:

- partition pruning
- file/fragment pruning
- Parquet statistics-based filtering
- column projection
- parallel scanning

Current PyArrow dataset documentation describes filtering, projection, and iterative scanning as core dataset capabilities. citeturn693043search4

Again, the word is **opportunity**, not guarantee.

## 23.3 `get_fragments()` and pruning visibility

You can inspect fragments conceptually:

```python
for fragment in orders_dataset.get_fragments(
    filter=ds.field("country") == "IN"
):
    print(fragment)
```

The dataset API can use partition expressions and Parquet information such as statistics when determining relevant fragments. citeturn617091search8

---

# 24. `to_batches()` and `to_table()`

## 24.1 `to_table()`

```python
table = orders_dataset.to_table(
    columns=["country", "amount"],
    filter=ds.field("country") == "IN",
)
```

Use this when the resulting materialized table is manageable for your memory budget and downstream processing model.

## 24.2 `to_batches()`

```python
scanner = orders_dataset.scanner(
    columns=["country", "amount"],
    filter=ds.field("country") == "IN",
)

for batch in scanner.to_batches():
    print(batch.num_rows)
```

This moves the dataset scan toward progressive consumption.

### Practical comparison

| API | Good for | Main consideration |
|---|---|---|
| `to_table()` | manageable materialized results | can require substantial memory |
| `to_batches()` | large scans and batch processing | caller must process batches correctly |

Do not interpret this table as an absolute rule. A large table can be filtered to a very small result, making `to_table()` completely reasonable.

---

# 25. `ds.write_dataset`

## 25.1 The basic form

```python
import pyarrow.dataset as ds

schema = table.schema

ds.write_dataset(
    table,
    base_dir="data/orders",
    format="parquet",
    schema=schema,
)
```

The current `write_dataset()` API accepts Arrow tables, record batches, datasets, and other supported inputs. It exposes controls for partitioning, file naming, rows per file, rows per row group, existing-data behavior, filesystem, and more. citeturn467189search0

## 25.2 Why use dataset writing instead of a loop of `write_table()` calls?

You can absolutely build a dataset manually, but `ds.write_dataset()` provides a higher-level abstraction for:

- file creation
- partition directories
- batching
- row-group bounds
- file naming
- existing-data behavior
- filesystem integration

This is particularly useful once your output is no longer one file.

---

# 26. Hive-Style Partitioning with PyArrow

## 26.1 What is Hive partitioning?

A typical directory tree looks like:

```text
orders/
├── year=2025/
│   ├── month=01/
│   │   ├── part-0.parquet
│   │   └── part-1.parquet
│   └── month=02/
│       └── part-0.parquet
└── year=2026/
    └── month=01/
        └── part-0.parquet
```

The partition values are encoded in the path.

## 26.2 Writing with a partition specification

```python
import pyarrow.dataset as ds

ds.write_dataset(
    table,
    base_dir="data/orders",
    format="parquet",
    partitioning=["year", "month"],
    partitioning_flavor="hive",
)
```

The exact partitioning configuration should match the Arrow schema and the data columns.

## 26.3 What partitioning changes

Partitioning adds an extra pruning layer:

```text
Dataset directory
      ↓
Partition pruning
      ↓
Candidate files
      ↓
Parquet row-group pruning
      ↓
Candidate pages/values
```

Topic 08 will cover partition design deeply. Here the important lesson is that PyArrow can create and scan partitioned datasets; the partition strategy itself must still be chosen from workload characteristics.

---

# 27. `max_rows_per_file`

## 27.1 What it controls

```python
ds.write_dataset(
    table,
    base_dir="data/orders",
    format="parquet",
    max_rows_per_file=1_000_000,
)
```

This places an upper bound on rows written to a file.

## 27.2 Critical production insight

Rows are not bytes.

Suppose Dataset A has:

```text
1,000,000 rows
mostly short integers
```

and Dataset B has:

```text
1,000,000 rows
large strings + nested structures
```

The files can have dramatically different byte sizes.

Therefore:

> **`max_rows_per_file` is a row-count control, not a direct file-byte target.**

Current `write_dataset()` documentation also distinguishes `max_rows_per_file` from row-group controls. citeturn467189search0

## 27.3 When it is useful

Use row limits when you want predictable approximate record counts per file or when coordinating with known workload characteristics.

But measure actual file sizes before establishing a hard platform standard.

---

# 28. Row-Group Bounds in Dataset Writing

PyArrow dataset writing exposes:

- `min_rows_per_group`
- `max_rows_per_group`

Example:

```python
ds.write_dataset(
    table,
    base_dir="data/orders",
    format="parquet",
    min_rows_per_group=900_000,
    max_rows_per_group=1_000_000,
)
```

Current documentation explains that the dataset writer can buffer incoming data until the minimum is reached and can split large incoming batches according to the maximum. It also warns that setting only a maximum without the minimum can result in very small row groups. citeturn467189search0

This makes the relationship clearer:

```text
Dataset writer input batches
        ↓
row-group buffering/splitting
        ↓
Parquet row groups
```

Use these controls to make row-group formation more predictable, but still inspect the resulting files.

---

# 29. Existing Data Behavior

## 29.1 Why this matters

Writing into an existing dataset is an operational action, not just an I/O operation.

You need to know:

```text
Does this job append?
Does it replace?
Should it fail?
Should it delete matching partitions?
```

`ds.write_dataset()` exposes `existing_data_behavior`.

Current documentation lists supported values including:

- `error`
- `overwrite_or_ignore`
- `delete_matching`

and explains their different operational semantics. citeturn467189search0

## 29.2 Why explicit behavior matters

Suppose a daily pipeline is rerun for `2025-03-15`.

Without deliberate behavior, you could create:

```text
duplicate files
or
stale files
or
silently overwritten files
```

A production pipeline should make rerun semantics explicit.

## 29.3 Important design idea

For partition replacement, the desired behavior often resembles:

```text
Identify partitions touched by the run
          ↓
Write replacement output
          ↓
Validate
          ↓
Publish according to commit strategy
```

Do not confuse `existing_data_behavior` with a full transactional table format. It is a dataset-write control, not a universal ACID guarantee.

---

# 30. File-Name Templates

## 30.1 Why file names matter

A dataset writer may generate file names automatically, but you can provide a template:

```python
ds.write_dataset(
    table,
    base_dir="data/orders",
    format="parquet",
    basename_template="orders-{i}.parquet",
)
```

The current API documents `{i}` as the incrementing token in the basename template. citeturn467189search0

## 30.2 Why predictable names help

Predictable names can improve:

- debugging
- reproducibility
- operational inspection
- test assertions
- log interpretation

But uniqueness still matters. A naming template that causes collisions can create overwrites or failures depending on the selected existing-data behavior.

---

# 31. Schema Differences Across Files

A dataset can contain files created by different runs or producers.

Suppose:

```text
part-001.parquet
id: int64
name: string
amount: double

part-002.parquet
id: int64
name: string
amount: double
currency: string
```

The second file has an additional column.

## 31.1 Missing columns

A scanner may need to represent missing columns for files that do not contain them.

For example:

```text
file A
currency missing

file B
currency present
```

A production policy might normalize the logical dataset to:

```text
currency: string, nullable
```

But that should be deliberate.

## 31.2 Type widening

Sometimes two types are compatible under an explicit policy.

For example, a numeric type might be widened to another numeric representation when the conversion is safe and tested.

But do not assume every change is safe.

## 31.3 Incompatible types

This is a clear failure case:

```text
part-001.amount → int64
part-002.amount → string
```

Do not blindly concatenate these files.

A production pipeline should have a policy such as:

```text
compatible change
→ normalize / promote / accept

incompatible change
→ fail loudly / quarantine / repair source
```

## 31.4 Schema inspection and unification

At dataset-discovery time, inspect the schema rather than trusting a directory to be healthy.

Useful concepts include:

- explicit schema
- schema unification
- type normalization
- missing-column policy
- compatibility checks

Current dataset documentation notes schema discovery and basic normalization behavior. citeturn693043search4

### Production rule

> A multi-file dataset is only as reliable as the policy that defines what schemas may coexist inside it.

---

# 32. Custom Footer Metadata

## 32.1 Why add custom metadata?

Parquet files can carry key-value metadata that can help answer:

- Which pipeline version wrote this?
- Which source produced it?
- Which ingestion run created it?
- Which transformation version was used?

Useful keys might be:

```text
pipeline_version
source
run_id
```

## 32.2 Adding metadata through the Arrow schema

An accurate and portable approach is to attach metadata to the Arrow schema before writing.

```python
import pyarrow as pa
import pyarrow.parquet as pq

metadata = {
    b"pipeline_version": b"2026.09",
    b"source": b"orders_api",
    b"run_id": b"run-000123",
}

table_with_metadata = table.replace_schema_metadata(metadata)

pq.write_table(
    table_with_metadata,
    "orders_with_metadata.parquet",
)
```

The values in Arrow schema metadata are byte-like key/value entries.

## 32.3 Reading it back

```python
pf = pq.ParquetFile("orders_with_metadata.parquet")

file_metadata = pf.metadata.metadata or {}

for key, value in file_metadata.items():
    print(key, value)
```

The precise set of metadata entries may include implementation-generated entries in addition to your custom keys.

## 32.4 Writer-level metadata

`ParquetWriter` also exposes `add_key_value_metadata()` in current PyArrow versions:

```python
writer.add_key_value_metadata(
    {
        "pipeline_version": "2026.09",
        "run_id": "run-000123",
    }
)
```

The method is documented by the current ParquetWriter API. citeturn467189search1

For a project that supports multiple PyArrow versions, choose one metadata approach and test it under the pinned version.

## 32.5 What metadata can and cannot do

Metadata is useful for:

- provenance
- debugging
- lineage hints
- reproducibility
- audits

It is not a substitute for a proper catalog, lineage platform, or table-level governance system.

---

# 33. Object Storage

## 33.1 Why local files and object storage are different

A local file:

```text
/path/to/orders.parquet
```

and an object:

```text
s3://bucket/orders/part-000.parquet
```

look similar conceptually, but they are accessed through different storage semantics.

Object storage introduces concerns such as:

- remote requests
- network latency
- object listing
- authentication
- prefix organization
- publication semantics
- rename behavior

## 33.2 `pyarrow.fs.S3FileSystem`

PyArrow supports S3-compatible filesystems through `pyarrow.fs.S3FileSystem`.

A conceptual example for AWS-style usage is:

```python
from pyarrow import fs

s3 = fs.S3FileSystem(
    region="us-east-1",
)
```

Then pass the filesystem to a reader/writer API when appropriate.

Current PyArrow documentation shows `filesystem=` support for Parquet APIs and S3 filesystem usage. citeturn617091search0

## 33.3 MinIO

MinIO can emulate an S3 API locally. A commonly used PyArrow pattern is:

```python
from pyarrow import fs

minio = fs.S3FileSystem(
    scheme="http",
    endpoint_override="localhost:9000",
)
```

Then use the filesystem with a dataset or Parquet operation:

```python
import pyarrow.dataset as ds

dataset = ds.dataset(
    "my-bucket/orders",
    format="parquet",
    filesystem=minio,
)
```

Apache Arrow's dataset documentation explicitly documents MinIO/S3-compatible use through `S3FileSystem`, including `scheme="http"` and `endpoint_override` for a local MinIO instance. citeturn693043search0

### Security rule

Never hard-code real object-storage credentials in source code.

Use environment variables, a local development credential store, or the cloud runtime's credential mechanism.

## 33.4 fsspec awareness

PyArrow can also interoperate with fsspec-compatible filesystems in supported scenarios.

The practical lesson is not to memorize every integration.

Understand the abstraction:

```text
PyArrow I/O API
     ↓
Filesystem abstraction
     ↓
Local / S3 / MinIO / other supported filesystem
```

The exact adapter and performance characteristics depend on the filesystem implementation.

---

# 34. MinIO Experiment

This exercise assumes MinIO is available from Module 2.4.

## 34.1 Architecture

```text
Python application
       ↓
PyArrow
       ↓
S3-compatible filesystem
       ↓
MinIO
       ↓
Parquet objects
```

## 34.2 Exercise: write and read a dataset

Use environment variables for credentials if your MinIO instance requires them.

```python
import pyarrow as pa
import pyarrow.dataset as ds
from pyarrow import fs

minio = fs.S3FileSystem(
    scheme="http",
    endpoint_override="localhost:9000",
    access_key="${MINIO_ACCESS_KEY}",
    secret_key="${MINIO_SECRET_KEY}",
)

table = pa.table(
    {
        "order_id": [1, 2, 3],
        "country": ["IN", "US", "IN"],
        "amount": [100.0, 200.0, 175.0],
    }
)

ds.write_dataset(
    table,
    base_dir="orders-bucket/orders",
    format="parquet",
    filesystem=minio,
)

dataset = ds.dataset(
    "orders-bucket/orders",
    format="parquet",
    filesystem=minio,
)

print(dataset.files)
print(dataset.to_table())
```

The credential strings above are placeholders, not working credentials. In actual code, read the values from the environment:

```python
import os

access_key = os.environ["MINIO_ACCESS_KEY"]
secret_key = os.environ["MINIO_SECRET_KEY"]
```

## 34.3 What to inspect

After the exercise, inspect:

- the bucket/prefix
- the number of files
- partition directories if used
- successful reads
- successful filtered reads
- dataset schema
- Parquet metadata

The point is to prove that the filesystem abstraction still leads to real Parquet objects with the same physical layout concepts.

---

# 35. Atomic Output and Commit Patterns

Writing directly into the final production location is risky.

## 35.1 The failure scenario

Imagine:

```text
Job starts
  ↓
Writes 100 files
  ↓
Writes files 1–43
  ↓
Process crashes
```

If readers can discover those 43 files as final output, your dataset may now be incomplete.

Possible consequences include:

- partial data
- duplicate reruns
- inconsistent partitions
- difficult rollback
- consumers reading intermediate state

## 35.2 Temporary output + commit

A safer conceptual pattern is:

```text
Write to temporary location
        ↓
Validate output
        ↓
Commit / publish
        ↓
Expose final dataset
```

For local filesystems, a rename/swap can sometimes provide atomic publication semantics.

For object storage, the semantics differ. A "rename" may not be a native atomic metadata operation and may be implemented through copy/delete behavior or another mechanism depending on the system.

Therefore, object-store publication often uses patterns such as:

```text
temporary prefix
        ↓
validate
        ↓
manifest/commit marker
        ↓
consumer discovers committed version
```

## 35.3 Manifest-based thinking

A simple conceptual manifest might say:

```json
{
  "dataset_version": "2026-09-28-run-123",
  "files": [
    "tmp/run-123/part-0.parquet",
    "tmp/run-123/part-1.parquet"
  ],
  "row_count": 2000000,
  "schema_hash": "..."
}
```

The exact commit protocol belongs to the larger lakehouse/table-format discussion later in the roadmap.

The learning objective here is:

> **Do not confuse successfully writing bytes with safely publishing a dataset.**

---

# 36. Atomic Partition Output

Suppose a daily partition is being rebuilt:

```text
orders/year=2025/month=03/day=15/
```

A safer pattern is:

```text
tmp/run-123/year=2025/month=03/day=15/
                     ↓
                 write files
                     ↓
             validate row count
             validate schema
             validate values
                     ↓
                 commit
```

The same principle applies to:

- reruns
- backfills
- repair jobs
- migration jobs
- late-arriving corrections

## 36.1 Idempotency

A job is easier to operate when repeating the same logical input produces the same logical result.

Think:

```text
run A
→ partition P

run A again
→ partition P should not gain a duplicate copy of A
```

This topic connects directly to the earlier Stage 1 lesson on idempotent jobs.

---

# 37. Row-Group Size Experiment

The roadmap specifically asks for a controlled experiment at:

- 10,000 rows
- 100,000 rows
- 1,000,000 rows
- 10,000,000 rows

## 37.1 Experimental rule

Change **only the row-group setting**.

Keep constant:

- input dataset
- row count
- schema
- file format
- codec
- machine
- Python/PyArrow version
- query
- random seed where data is generated

## 37.2 Experiment plan

```text
Same input
    ↓
write row_group_size=10k
    ↓
measure

Same input
    ↓
write row_group_size=100k
    ↓
measure

Same input
    ↓
write row_group_size=1M
    ↓
measure

Same input
    ↓
write row_group_size=10M
    ↓
measure
```

## 37.3 Record these values

| Configuration | File size | Write time | Peak memory | Filtered-query time | Row groups | Notes |
|---|---:|---:|---:|---:|---:|---|
| 10k | | | | | | |
| 100k | | | | | | |
| 1M | | | | | | |
| 10M | | | | | | |

Do not fill the table with invented benchmark values.

## 37.4 Questions to answer

After measuring, explain:

1. Did smaller row groups improve filtering?
2. Did they increase file/metadata overhead?
3. Did compression change?
4. Did writer memory change?
5. Did query latency change?
6. Did the relationship remain consistent across all four sizes?

This is the beginning of production physical-design thinking.

---

# 38. Practical Parquet Writer Lab — `parquet_writer_lab.py`

The roadmap requires a hands-on lab named:

```text
parquet_writer_lab.py
```

**File-safety rule:** do not physically create that Python file as part of this module generation. The complete implementation belongs below as a code block for the learner to save and run in their own lab project.

## 38.1 Part 1 — Explicit schema

Design a schema for an orders dataset.

```python
import pyarrow as pa

schema = pa.schema(
    [
        pa.field("order_id", pa.int64(), nullable=False),
        pa.field("country", pa.string(), nullable=False),
        pa.field("status", pa.string(), nullable=False),
        pa.field("sensor_value", pa.float64(), nullable=True),
        pa.field("created_at", pa.timestamp("us", tz="UTC"), nullable=False),
    ]
)
```

Explain why each type is explicit.

## 38.2 Part 2 — Deliberate writer settings

A representative configuration is:

```python
pq.write_table(
    table,
    "orders_optimized.parquet",
    schema=table.schema,
    compression="zstd",
    use_dictionary=["country", "status"],
    write_statistics=True,
    write_page_index=True,
    use_byte_stream_split=["sensor_value"],
    version="2.6",
)
```

### Important version/API note

The exact interaction among dictionary settings, byte-stream split, compression, and writer options should be verified against the PyArrow version pinned in your project. Current documentation notes, for example, that dictionary encoding can take precedence over byte-stream split when both are enabled for a column. citeturn467189search1

## 38.3 Part 3 — Generate and stream a logical 20 GB workload

The requirement is to process a **20 GB generated dataset** without requiring the entire dataset to reside in memory.

The 20 GB figure describes the generated logical workload, not a promised exact output-file size.

A practical generator should yield batches rather than build one huge table.

```python
from collections.abc import Iterator

import pyarrow as pa


def generate_order_batches(
    total_rows: int,
    batch_size: int = 100_000,
) -> Iterator[pa.RecordBatch]:
    """Generate synthetic order batches without materializing all rows."""
    remaining = total_rows
    order_id = 1

    while remaining > 0:
        size = min(batch_size, remaining)

        batch = pa.record_batch(
            [
                pa.array(range(order_id, order_id + size), type=pa.int64()),
                pa.array(["IN", "US", "UK", "IN"] * ((size + 3) // 4))[:size],
                pa.array(["PAID", "PAID", "FAILED", "PAID"] * ((size + 3) // 4))[:size],
                pa.array([10.5, 20.0, 7.25, 35.0] * ((size + 3) // 4))[:size],
            ],
            names=["order_id", "country", "status", "sensor_value"],
        )

        yield batch

        order_id += size
        remaining -= size
```

For a real 20 GB test, the generator must be made wide enough to create a meaningful storage workload. The exact row count needed depends on the schema and value distribution.

### Incremental writer pattern

```python
import pyarrow.parquet as pq

writer = pq.ParquetWriter(
    "orders_20gb.parquet",
    schema=schema,
    compression="zstd",
    use_dictionary=["country", "status"],
    write_statistics=True,
    write_page_index=True,
)

try:
    for batch in generate_order_batches(total_rows=100_000_000):
        writer.write_batch(batch, row_group_size=1_000_000)
finally:
    writer.close()
```

The row count above is an example workload, not a claim that it produces 20 GB. Measure actual output size.

## 38.4 Part 4 — Hive-partitioned dataset

Use `ds.write_dataset()` with a deliberate schema and row-group target.

```python
import pyarrow.dataset as ds

# Assume `orders` is an Arrow Table with year/month columns.
ds.write_dataset(
    orders,
    base_dir="data/orders",
    format="parquet",
    partitioning=["year", "month"],
    partitioning_flavor="hive",
    min_rows_per_group=1_000_000,
    max_rows_per_group=1_000_000,
    max_rows_per_file=5_000_000,
    existing_data_behavior="error",
    basename_template="orders-{i}.parquet",
)
```

The exact row count and file boundaries produced still depend on the input data and writer behavior. Inspect the resulting dataset.

## 38.5 Part 5 — Add metadata

```python
table_with_metadata = orders.replace_schema_metadata(
    {
        b"pipeline_version": b"2026.09",
        b"run_id": b"run-123",
    }
)
```

Write and then read back the metadata.

## 38.6 Part 6 — Row-group experiment

Repeat the same write for:

```text
10_000
100_000
1_000_000
10_000_000
```

Record:

- file size
- write time
- write memory
- filtered-query time
- row-group count

## 38.7 Part 7 — Tests

The tests should verify at minimum:

- exact schema
- expected compression
- statistics present where exposed
- expected row count
- round-trip values

Example test functions can live in the learner's separate test module:

```python
import pyarrow.parquet as pq


def test_schema(tmp_path, expected_schema):
    path = tmp_path / "orders.parquet"
    pq.write_table(table, path)

    actual = pq.ParquetFile(path).schema_arrow
    assert actual == expected_schema


def test_codec(tmp_path):
    path = tmp_path / "orders.parquet"
    pq.write_table(table, path, compression="zstd")

    metadata = pq.ParquetFile(path).metadata
    for row_group_index in range(metadata.num_row_groups):
        row_group = metadata.row_group(row_group_index)
        for column_index in range(row_group.num_columns):
            assert row_group.column(column_index).compression == "ZSTD"
```

Check the exact metadata representation for the deployed PyArrow version if you write strict assertions around enumeration casing.

---

# 39. Testing Parquet Outputs

Production testing should validate two different layers.

## 39.1 Logical correctness

Ask:

- Are row counts correct?
- Are column names correct?
- Are types correct?
- Are values preserved?
- Are nulls preserved?
- Are timestamps preserved at the intended resolution?

A simple round-trip test is:

```text
source
  ↓
write Parquet
  ↓
read Parquet
  ↓
compare logical values
```

## 39.2 Physical correctness

Ask:

- Is the codec correct?
- Are statistics written when expected?
- Is the row-group strategy correct?
- Is the file count within expectations?
- Are the intended partitions present?
- Is page-index writing enabled if required by the contract?

These are different assertions.

A dataset can be logically correct and physically wrong for the intended workload.

## 39.3 Example verification helper

```python
import pyarrow.parquet as pq


def inspect_contract(path: str) -> dict:
    pf = pq.ParquetFile(path)
    metadata = pf.metadata

    compression = set()
    encodings = set()

    for row_group_index in range(metadata.num_row_groups):
        row_group = metadata.row_group(row_group_index)
        for column_index in range(row_group.num_columns):
            column = row_group.column(column_index)
            compression.add(str(column.compression))
            encodings.update(str(value) for value in column.encodings)

    return {
        "rows": metadata.num_rows,
        "row_groups": metadata.num_row_groups,
        "schema": pf.schema_arrow,
        "compression": sorted(compression),
        "encodings": sorted(encodings),
    }
```

This is useful because tests can consume structured values instead of comparing the output of `print(metadata)`.

---

# 40. Reproducibility

Physical-layout experiments are easy to invalidate accidentally.

Keep these fixed when comparing alternatives:

- input dataset
- row count
- schema
- random seed
- PyArrow version
- Python version
- machine/CPU
- available memory
- filesystem
- query
- codec
- compression level
- row-group strategy except for the variable under test

Record the environment alongside the measurements.

A simple experiment manifest could contain:

```text
experiment_id
input_hash
pyarrow_version
python_version
machine
row_count
schema_hash
codec
compression_level
row_group_size
query
run_number
```

The exact metadata system can be simple CSV during learning. The important principle is repeatability.

### Production implication

A claimed optimization that cannot be reproduced is difficult to trust during an architecture review.

---

# 41. Debugging Common PyArrow Problems

The standard troubleshooting pattern is:

> **symptom → likely causes → inspect → measure → fix**

## Problem 1 — Schema unexpectedly changes

### Symptom

A dataset that used to read as:

```text
amount: double
```

now reads differently.

### Likely causes

- input inference changed
- nulls changed type inference
- mixed Python values
- producer schema changed
- one file was written differently

### Inspect

```python
pf = pq.ParquetFile("orders.parquet")
print(pf.schema_arrow)
```

Then inspect multiple files through the dataset API.

### Fix

- establish an explicit schema
- validate input
- reject incompatible changes
- normalize known compatible differences

### Lesson

Schema is part of the pipeline contract.

---

## Problem 2 — Memory usage becomes too high

### Symptom

A large read causes swapping, OOM, or an unexpectedly large memory spike.

### Likely causes

- `read_table()` materialized too much
- conversion to pandas created another large representation
- batches are too large
- selected columns are too wide
- transformations create temporary arrays
- row groups are physically large

### Inspect

Compare:

```python
pq.read_table(...)
```

with:

```python
pf.iter_batches(...)
```

and measure peak memory.

### Fix

- select fewer columns
- batch the read
- lower batch size where useful
- avoid unnecessary pandas conversion
- reduce transformation intermediates

### Lesson

Memory management is a pipeline design problem, not merely a Python syntax problem.

---

## Problem 3 — Filtering does not reduce work as much as expected

### Symptom

You add a selective filter but the scan remains expensive.

### Likely causes

- row-group statistics are broad
- values are poorly ordered
- the filter is not selective
- statistics are absent or limited
- the reader/engine does not use a particular metadata feature
- partition layout is not aligned with the filter

### Inspect

Look at:

```python
pf.metadata.row_group(0).column(0).statistics
```

where supported by your version.

Then compare min/max ranges across row groups.

### Measure

- bytes read where exposed
- rows returned
- row groups examined/skipped where observable
- query time
- cache state

### Fix

Do not immediately change the codec.

First determine whether the physical layout is allowing effective pruning.

---

## Problem 4 — Incremental output cannot be opened

### Symptom

A newly written Parquet file fails to read.

### Likely causes

- writer was not closed
- process crashed during finalization
- output path exposed partial data
- underlying storage operation failed

### Inspect

Check:

- process logs
- file existence
- file size
- object listing
- whether the writer reached `close()`

### Fix

Use `try/finally`, temporary output, validation, and an explicit commit/publish mechanism.

### Lesson

A file is not production-ready merely because its pathname exists.

---

## Problem 5 — Dataset schema differs across files

### Symptom

Dataset discovery or scanning fails or produces unexpected nulls/types.

### Likely causes

- schema drift
- missing column
- incompatible type
- writer-version differences

### Inspect

Open representative files individually:

```python
for path in ["part-001.parquet", "part-002.parquet"]:
    pf = pq.ParquetFile(path)
    print(path)
    print(pf.schema_arrow)
```

### Fix

- define compatibility policy
- normalize compatible files
- quarantine incompatible files
- repair the producer

---

## Problem 6 — Files are unexpectedly numerous

### Symptom

A single dataset write creates many more files than expected.

### Likely causes

- partition cardinality
- `max_open_files` behavior
- tiny input batches
- row/file settings
- high writer parallelism

Current `write_dataset()` documentation warns that setting `max_open_files` too low can fragment output into many small files. citeturn467189search0

### Inspect

Count:

- files
- directories
- rows per file
- file-size distribution

### Fix

Adjust dataset-write configuration and revisit partition design.

---

## Problem 7 — MinIO/S3 behaves differently from local files

### Symptom

A workflow succeeds locally but has surprising behavior remotely.

### Likely causes

- endpoint configuration
- credentials
- TLS differences
- object listing behavior
- network latency
- rename/commit semantics
- request overhead

### Inspect

Verify:

- filesystem configuration
- bucket/prefix
- connectivity
- object paths
- publication sequence

### Fix

Treat object storage as an actual remote filesystem rather than pretending it is a local directory.

---

# 42. Common Mistakes

## 1. Using `read_table()` for huge datasets without considering memory

`read_table()` is convenient, but convenience is not the same thing as bounded resource usage.

## 2. Converting everything immediately to pandas

This can add another memory representation and discard the benefits of staying in Arrow.

## 3. Trusting schema inference in production

Inference can be correct until the input changes.

## 4. Treating `row_group_size` as an arbitrary number

It changes physical granularity and therefore can affect several workload dimensions.

## 5. Confusing rows-per-file with bytes-per-file

Variable-width data makes row counts a weak proxy for actual file size.

## 6. Assuming compression settings guarantee smaller files

Encoding, data distribution, and codec behavior interact.

## 7. Assuming statistics always produce strong pruning

Statistics can exist while still being too broad to eliminate much work.

## 8. Assuming filters always eliminate all irrelevant I/O

A filter request does not imply perfect physical skipping.

## 9. Writing directly into the final production path

Partial writes can become visible to consumers.

## 10. Ignoring incomplete writer finalization

The footer/final metadata must be finalized for a valid file.

## 11. Assuming every PyArrow release has identical APIs

PyArrow evolves. Pin versions and verify version-sensitive behavior.

## 12. Ignoring schema differences across files

A directory can look healthy while containing incompatible files.

## 13. Creating too many files through small writes or excessive partitioning

File count is an operational concern, not just a storage concern.

## 14. Changing multiple variables in one benchmark

If codec, row-group size, schema, and sort order all change together, you cannot know which factor caused the result.

## 15. Comparing performance without controlling cache/environment

Timing is not a property of the file alone.

## 16. Inventing physical guarantees from API parameters

For example:

```text
row_group_size=1_000_000
```

does not mean:

```text
exactly one million rows in every physical group forever
```

Inspect the output.

---

# 43. Production Data Engineering Pattern

A practical end-to-end pattern is:

```text
Source data
    ↓
Arrow Table / RecordBatch
    ↓
Validation
    ↓
Explicit schema
    ↓
Batch transformation
    ↓
ParquetWriter / write_dataset
    ↓
Metadata
    ↓
Validation
    ↓
Temporary output
    ↓
Commit
    ↓
Final dataset
```

## 43.1 Stage 1 — Source data

Source data may come from:

- APIs
- databases
- messages
- CSV
- Avro
- existing Parquet

## 43.2 Stage 2 — Arrow representation

Convert the input into a known Arrow schema and batch structure.

## 43.3 Stage 3 — Validation

Check:

- required fields
- types
- ranges
- row counts
- source control totals where available

## 43.4 Stage 4 — Explicit schema

Make the output contract explicit.

## 43.5 Stage 5 — Batch transformation

Do work on batches rather than materializing unnecessarily large intermediate objects.

## 43.6 Stage 6 — Deliberate write

Choose:

- compression
- row groups
- page behavior
- statistics
- timestamp handling
- partition strategy

## 43.7 Stage 7 — Metadata

Add run/provenance information where useful.

## 43.8 Stage 8 — Validation

Inspect the actual Parquet output.

## 43.9 Stage 9 — Temporary output

Keep incomplete output away from the consumer-visible location.

## 43.10 Stage 10 — Commit

Publish only validated output.

---

# 44. Production Case Study — 200 GB/day Retail Pipeline

Imagine a retail company receives approximately **200 GB/day** of order data.

Most downstream queries:

- filter by date
- select 5 of 30 columns
- aggregate amounts
- rerun partitions during backfills

The question is not:

> "Which PyArrow setting is best?"

The question is:

> "What write/read design gives this workload predictable behavior under our resource and operational constraints?"

## 44.1 One file or dataset?

At 200 GB/day, a single monolithic file can make lifecycle management and parallel processing unnecessarily difficult.

A dataset of files is more natural to evaluate.

But the correct file count should still be measured from:

- query parallelism
- expected file size
- partition volume
- object-store behavior
- update/backfill requirements

## 44.2 Explicit schema

Use one explicit output schema for the dataset contract.

Why?

Because reruns and producer changes must not silently redefine columns.

## 44.3 Row-group strategy

Begin with a plausible candidate, perhaps around 1 million rows per row group, because the roadmap uses that as a practical experimental point—not because 1 million is universally best.

Then measure:

- file size
- row-group count
- filtered query latency
- memory
- bytes read

## 44.4 Compression

Choose a candidate codec based on:

- storage cost
- write CPU
- read CPU
- query patterns

Then benchmark it.

## 44.5 Statistics

Keep statistics enabled where they contribute to pruning and verify the ranges are useful.

## 44.6 Partitioning

If date is the dominant access path, date partitions are a candidate design.

But the exact granularity—day, month, hour—must follow volume and query patterns rather than habit.

## 44.7 Batch writes

Use batch-oriented writing so the application does not create one tiny file per transaction.

## 44.8 Metadata

Include:

```text
pipeline_version
run_id
source
```

when those fields materially help traceability.

## 44.9 Atomic output

Backfills should not expose a half-written partition.

A temporary-output + validation + commit design makes reruns safer.

### Worked engineering conclusion

The final design should be justified with measurements. The key is not memorizing a standard configuration but proving that the chosen configuration behaves acceptably for the real workload.

---

# 45. Decision Table

| Requirement | PyArrow technique |
|---|---|
| Read fewer columns | `columns=` |
| Filter while reading | `filters=` |
| Inspect one Parquet file | `ParquetFile` |
| Inspect schema | `schema_arrow` |
| Read a specific row group | `read_row_group()` |
| Process large files progressively | `iter_batches()` |
| Incremental write | `ParquetWriter` |
| Control row groups | `row_group_size` / dataset row-group controls |
| Control data pages | `data_page_size` |
| Choose compression | `compression=` |
| Choose compression level | `compression_level=` |
| Enable/disable dictionary encoding | `use_dictionary=` |
| Write statistics | `write_statistics=` |
| Control timestamp resolution | `coerce_timestamps=` |
| Enable byte-stream split where appropriate | `use_byte_stream_split=` |
| Write page index | `write_page_index=` |
| Scan many Parquet files | `pyarrow.dataset` |
| Dataset filter | `filter=ds.field(...) ...` |
| Batch dataset scan | `scanner(...).to_batches()` |
| Materialize dataset | `to_table()` |
| Write dataset | `ds.write_dataset()` |
| Hive partitions | `partitioning` + `partitioning_flavor="hive"` |
| Control rows per file | `max_rows_per_file` |
| Control row-group bounds | `min_rows_per_group`, `max_rows_per_group` |
| Control existing output behavior | `existing_data_behavior` |
| Predictable file names | `basename_template` |
| Add provenance | schema metadata / `add_key_value_metadata()` |
| Remote object storage | `pyarrow.fs` / `S3FileSystem` |
| Safer publication | temporary output + validation + commit |

These are tools, not recipes. The workload determines how they should be combined.

---

# 46. API Cheat Sheet

## Reading a single file

```python
pq.read_table(...)
```

Read the selected result as an Arrow table.

## Writing a single file

```python
pq.write_table(...)
```

Write an Arrow table to one Parquet file.

## Inspecting a file

```python
pq.ParquetFile(...)
```

Open a Parquet file for metadata inspection and controlled reads.

## Read one row group

```python
pf.read_row_group(...)
```

Read a specific physical row-group unit.

## Read progressively

```python
pf.iter_batches(...)
```

Consume the file batch by batch.

## Incremental writing

```python
pq.ParquetWriter(...)
```

Build a Parquet file from multiple writes.

## Multi-file dataset

```python
ds.dataset(...)
```

Describe a collection of files as one logical dataset.

## Dataset writing

```python
ds.write_dataset(...)
```

Write a dataset with file, partition, and row-group controls.

Do not use the cheat sheet as a replacement for understanding the physical implications of each API.

---

# 47. Interview Questions

## Basic

### 1. What is PyArrow?

**Model answer:**

PyArrow is the Python interface to Apache Arrow and related data-processing capabilities. It provides Python-native ways to represent typed columnar data in memory and to read/write formats such as Parquet.

### 2. How is Arrow different from Parquet?

**Model answer:**

Arrow is an in-memory columnar data model/interchange representation. Parquet is an on-disk columnar file format with row groups, column chunks, pages, encodings, compression, and metadata.

### 3. How do you write a Parquet file?

**Model answer:**

Create an Arrow table and call `pyarrow.parquet.write_table()` for a complete in-memory table, or use `ParquetWriter` for incremental/batch-based output.

### 4. How do you read a Parquet file?

**Model answer:**

Use `pyarrow.parquet.read_table()` when materializing a manageable result is appropriate, or use `ParquetFile.iter_batches()` for progressive processing.

---

## Intermediate

### 1. Why use an explicit schema?

**Model answer:**

Because production pipelines need predictable field types and interoperability. Explicit schemas reduce silent changes caused by inference and make contracts testable.

### 2. What is `ParquetFile`?

**Model answer:**

It is a PyArrow object for opening an individual Parquet file, inspecting its metadata/schema, and reading row groups or batches from it.

### 3. What is `iter_batches()`?

**Model answer:**

It provides a batch-oriented reading pattern, allowing a large Parquet file to be processed progressively instead of materializing the entire result at once.

### 4. Why is batch processing useful?

**Model answer:**

It helps control memory and supports streaming-style transformations, validations, aggregations, and rewrites. The actual memory usage still depends on batch contents and downstream processing.

### 5. What is `ParquetWriter`?

**Model answer:**

It is a writer for incrementally building a Parquet file from multiple Arrow tables or record batches, which is useful for large or streaming/batched pipelines.

### 6. What is `row_group_size`?

**Model answer:**

It controls the maximum number of rows in a written row group for supported writer operations. Row-group size affects physical granularity, statistics, skipping, compression, memory, and metadata overhead.

### 7. What does `filters=` do?

**Model answer:**

It expresses a read predicate that the Parquet reader may use for filter pushdown. Actual pruning depends on metadata, data layout, statistics, and implementation.

### 8. What is `pyarrow.dataset`?

**Model answer:**

It is PyArrow's dataset abstraction for working with multi-file tabular data, including discovery, schema handling, filtering, projection, partitioning, and iterative scanning.

---

## Advanced

### 1. Why can `read_table()` be inappropriate for huge datasets?

**Model answer:**

It materializes the selected result as an Arrow table, which may consume too much memory for a large workload. Batch scanning can provide a more controlled memory profile.

### 2. How do row groups influence query behavior?

**Model answer:**

They are major physical units containing column chunks and statistics. Their boundaries influence pruning granularity, read work, compression, and parallelism.

### 3. Why might changing row-group size affect both write and read performance?

**Model answer:**

Changing row-group size changes physical granularity and encoding/compression opportunities. Smaller groups can improve selectivity but increase metadata/overhead, while larger groups can improve compression and reduce metadata but make skipping coarser.

### 4. Why should schema differences across files be handled explicitly?

**Model answer:**

A dataset can only be safely scanned when the files are compatible under a defined schema policy. Missing columns may be normal, while incompatible types can produce incorrect or failed reads.

### 5. Why is direct writing to final object-storage paths potentially unsafe?

**Model answer:**

A crash can leave partial files visible to consumers. Object storage also does not necessarily provide the same atomic rename semantics as a local filesystem. A temporary-write + validation + commit pattern reduces that risk.

### 6. Why can object-store rename behavior matter?

**Model answer:**

Because object stores are object-oriented systems rather than traditional directory-based filesystems. A rename may not be a simple atomic metadata update, affecting publication and failure-recovery design.

---

## Senior / Architecture

### 1. How would you design a 500 GB/day Parquet ingestion pipeline in PyArrow?

**Model answer:**

I would start from workload requirements, define an explicit schema, ingest into Arrow batches, validate each batch, write with deliberate row-group and compression settings, partition according to query patterns, validate the output metadata, publish through a safe commit pattern, and continuously measure file counts, sizes, query performance, and memory.

### 2. How would you guarantee bounded memory?

**Model answer:**

I would design the pipeline around batch processing, avoid whole-table materialization, project only required columns, limit transformation intermediates, and measure peak memory under representative data. I would not claim a hard bound without accounting for all buffers and downstream operations.

### 3. How would you publish files atomically?

**Model answer:**

I would write to a temporary prefix, validate the output, then publish a commit marker/manifest or use an appropriate atomic local filesystem operation. On object storage I would not assume rename is atomic.

### 4. How would you design a partitioned dataset?

**Model answer:**

I would start from query filters and data volume, select low-to-moderate-cardinality partition keys that are commonly filtered, then determine granularity from file-size and query measurements. I would avoid blindly partitioning by high-cardinality identifiers.

### 5. How would you debug a sudden increase in Parquet query scan volume?

**Model answer:**

I would inspect recent file schemas, row-group counts, row-group statistics, sort/order characteristics, compression, partition layout, file-size distribution, and engine plan changes. Then I would compare representative old and new files and run the same query under controlled conditions.

### 6. How would you establish a standard row-group strategy?

**Model answer:**

I would define representative workloads and benchmark several row-group configurations with the same data, schema, codec, environment, and queries. I would compare file size, write time, memory, filtered-query latency, and pruning behavior, then document the resulting policy and its exceptions.

### 7. How would you validate that a writer change improved production performance?

**Model answer:**

I would first establish a baseline, isolate the writer variable, reproduce the benchmark, compare production-like queries, and monitor both storage/scan metrics and downstream outcomes. A smaller file alone would not prove success.

---

# 48. Practical Scenarios

## Scenario 1 — 5 GB Single Parquet File

You have a 5 GB Parquet file.

Should you use `read_table()` or `iter_batches()`?

### Reasoning

There is no automatic answer.

Ask:

- How much RAM is available?
- How many columns are needed?
- What transformation follows?
- Is the output small enough to materialize?

If the result is comfortably within the memory budget, `read_table()` may be convenient.

If memory is constrained or the transformation can be streamed, investigate `iter_batches()`.

---

## Scenario 2 — 100 GB Transformation

A pipeline must transform 100 GB of Parquet.

### Required reasoning

Use a design centered on:

- batch reading
- projection
- explicit schema
- incremental writing
- memory measurement

A conceptual architecture is:

```text
100 GB input
     ↓
iter_batches
     ↓
transform one batch
     ↓
ParquetWriter
     ↓
validated output
```

Do not materialize the full dataset by default.

---

## Scenario 3 — Multi-File Daily Dataset

A dataset is partitioned by date and queried mostly by date.

### Reasoning

Evaluate:

- `pyarrow.dataset`
- Hive-style partitioning
- partition filters
- dataset schema
- row-group statistics inside each file
- file count

The dataset layer and Parquet layer work together:

```text
partition pruning
      ↓
file selection
      ↓
row-group pruning
      ↓
column pruning
```

---

## Scenario 4 — Failed Production Write

A job dies after writing half of the expected files.

### Reasoning

The underlying problem is not simply a Python exception.

It is a **publication strategy** problem.

Evaluate:

- temporary output
- validation
- commit marker/manifest
- cleanup
- idempotent rerun
- reader visibility

---

# 49. Stop and Think Exercises

## Exercise A

A file has 30 columns, but a query needs 3.

**Which PyArrow capability should you consider first?**

### Answer

Column projection with `columns=[...]`.

### Why?

The Parquet file stores columns separately within row groups, so the reader can avoid materializing unrelated column chunks when the physical layout and read path support it.

---

## Exercise B

A 50 GB dataset does not fit comfortably into memory.

**Which reading pattern should you investigate?**

### Answer

Batch processing with `iter_batches()` or dataset scanning with `scanner(...).to_batches()`.

### Why?

These patterns let you consume the dataset progressively instead of materializing the entire result as one table.

---

## Exercise C

Two files contain:

```text
part1.amount = int64
part2.amount = string
```

**Should you blindly merge them?**

### Answer

No.

### Why?

The files contain incompatible representations of the same field. A production pipeline needs an explicit compatibility policy before scanning them as one dataset.

---

## Exercise D

A job fails after writing half of its files.

**What production design problem does this reveal?**

### Answer

Unsafe publication or insufficient commit semantics.

### Why?

A partially written dataset should not automatically become the final consumer-visible state.

---

## Exercise E

A query selects only two columns, but the runtime barely changes.

**What should you investigate before changing the codec?**

### Answer

Investigate:

- whether the selected columns dominate the file size
- filter selectivity
- decompression CPU
- cache state
- row-group size
- dataset/file overhead
- engine execution behavior

Column pruning can reduce I/O without necessarily dominating total runtime.

---

# 50. Mini Benchmark Table

Populate this during your lab.

| Experiment | File size | Write time | Peak memory | Read time | Filtered read time | Row groups |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | | | | | | |
| Smaller row groups | | | | | | |
| Larger row groups | | | | | | |
| Different codec | | | | | | |
| Sorted input | | | | | | |

Do not use this as a scorecard with an assumed winner.

The purpose is to understand which physical changes affect your workload.

---

# 51. Metadata-to-Physical-Structure Mapping Exercise

The point of this exercise is to connect the API you can inspect to the file model from Topic 02.

Start with:

```text
Parquet file
 ├── Row Groups
 │    ├── Column Chunks
 │    │    └── Pages
 │    └── ...
 └── Footer
```

Now inspect a real file with:

```python
import pyarrow.parquet as pq

pf = pq.ParquetFile("orders.parquet")
metadata = pf.metadata

print("rows:", metadata.num_rows)
print("row groups:", metadata.num_row_groups)
print("schema:")
print(pf.schema_arrow)

for rg_index in range(metadata.num_row_groups):
    rg = metadata.row_group(rg_index)
    print("row group", rg_index)
    print("rows:", rg.num_rows)
    print("bytes:", rg.total_byte_size)

    for column_index in range(rg.num_columns):
        column = rg.column(column_index)
        print("  column:", column.path_in_schema)
        print("  compression:", column.compression)
        print("  encodings:", column.encodings)
        print("  compressed bytes:", column.total_compressed_size)
        print("  uncompressed bytes:", column.total_uncompressed_size)
```

Fill in:

| Metadata field | Physical concept | Why it matters |
|---|---|---|
| `num_rows` | file row count | total logical data volume |
| `num_row_groups` | row-group count | physical granularity |
| `row_group(i).num_rows` | row-group size | pruning/read unit |
| `compression` | column-chunk encoding pipeline | storage/CPU behavior |
| `encodings` | page/column representation | representation efficiency |
| `statistics` | value summaries | pruning potential |
| file/column offsets | physical locations | targeted reads |

### Worked solution

The important relationship is:

```text
ParquetFile.metadata
       ↓
row-group objects
       ↓
column-chunk objects
       ↓
statistics / compression / encodings / locations
```

You are not looking at random metadata fields. You are looking at the machine-readable description of the physical artifact you learned in Topic 02.

---

# 52. Connection to Topic 02

Do not re-learn Parquet internals here. Instead, connect what you already know to PyArrow controls.

```text
Topic 02
Parquet internals
       ↓
Topic 03
PyArrow controls
```

The correspondence looks like:

```text
Row Groups
→ row_group_size

Statistics
→ write_statistics

Page Index
→ write_page_index

Encoding choices
→ use_dictionary / use_byte_stream_split / column_encoding where supported

Logical timestamps
→ coerce_timestamps / timestamp options

Compression
→ compression / compression_level
```

This connection is the core purpose of Topic 03:

> **Conceptual Parquet structure becomes an engineering control surface.**

---

# 53. Connection to Future Topics

The roadmap intentionally keeps the boundaries clear.

Later topics will deepen:

- **Topic 04** — Avro and row-oriented formats
- **Topic 05** — ORC and format-selection trade-offs
- **Topic 06** — nested and semi-structured data
- **Topic 07** — compression codecs and detailed benchmarking
- **Topic 08** — partitioning and Hive layouts
- **Topic 09** — small files and compaction
- **Later data-validation modules** — schema evolution and compatibility policy
- **Module 2.15** — lakehouse table formats and stronger commit semantics
- **Module 2.17** — cloud storage and cost
- **Module 2.20** — observability, governance, security, and encryption
- **Module 2.21** — performance, scaling, and cost optimization

This module gives you the practical PyArrow controls required to work with those later concepts.

---

# 54. What Should Be Measured?

A production Parquet change should be evidence-based.

| Measurement | Why it matters |
|---|---|
| File size | storage/network cost |
| File count | operational overhead |
| Row-group count | physical granularity |
| Rows per row group | physical organization |
| Column-chunk size | column-level storage cost |
| Encodings | representation behavior |
| Compression codec | storage/CPU trade-off |
| Statistics | pruning potential |
| Query runtime | user-visible performance |
| Bytes read | I/O efficiency |
| Peak memory | resource pressure |
| Write time | ingestion throughput |

No one metric tells the full story.

For example:

```text
File A = smaller
```

does not automatically mean:

```text
File A = faster
```

A compressed file can be smaller but more CPU-intensive to decode. A file with smaller row groups can skip more effectively but carry more metadata. A file with fewer files can reduce listing overhead but reduce parallelism.

Measure the dimension that matters to the workload.

---

# 55. How a Senior Data Engineer Thinks About PyArrow Parquet

Use this reasoning sequence during architecture reviews, performance incidents, code reviews, and platform decisions:

```text
What is the logical schema?
        ↓
How is the data represented in Arrow?
        ↓
How will the Parquet writer represent it?
        ↓
How many files should exist?
        ↓
How many row groups per file?
        ↓
What encodings are appropriate?
        ↓
What compression is appropriate?
        ↓
Which statistics should be written?
        ↓
Will readers be able to prune?
        ↓
What memory profile does reading require?
        ↓
How will output be validated?
        ↓
How will output be published safely?
        ↓
How will we measure the result?
```

## Architecture-review language

A strong engineering explanation sounds like:

> "The workload is dominated by date-filtered analytical scans and only five of thirty columns are commonly needed. We will therefore test a partitioned Parquet dataset with explicit schema, selective column reads, row-group statistics, and a measured row-group strategy. We will process input in batches and publish through a temporary-output commit pattern. The standard will be adopted only after we compare file size, memory, filtered query latency, and bytes read under a representative workload."

That is stronger than:

> "We always use one-million-row groups because that is the standard."

The first statement explains the reasoning and the evidence. The second memorizes a number.

---

# 56. Practical Verification Checklist

Before treating a PyArrow Parquet pipeline as production-ready, verify:

### Schema

- [ ] Output schema is explicit.
- [ ] Expected nullability is defined.
- [ ] Timestamp resolution is deliberate.
- [ ] Decimal precision/scale is deliberate.

### Reading

- [ ] Required columns are projected intentionally.
- [ ] Large scans have a batch-processing path.
- [ ] Memory has been measured.
- [ ] Filter behavior has been tested on representative data.

### Writing

- [ ] Row-group strategy is deliberate.
- [ ] Compression is deliberate.
- [ ] Dictionary settings are deliberate.
- [ ] Statistics policy is deliberate.
- [ ] Timestamp coercion is deliberate.
- [ ] Page-index policy is understood.

### Dataset

- [ ] File naming is predictable.
- [ ] Rows-per-file policy is defined.
- [ ] Row-group bounds are understood.
- [ ] Partitioning is workload-driven.
- [ ] Existing-data behavior is explicit.
- [ ] Schema differences across files have a policy.

### Operations

- [ ] Provenance metadata is useful and retrievable.
- [ ] Object-storage access is configured safely.
- [ ] Credentials are not hard-coded.
- [ ] Temporary output is separated from final output.
- [ ] Publication is validated and deliberate.
- [ ] Reruns are understood.

### Evidence

- [ ] Benchmarks use controlled inputs.
- [ ] Environment is recorded.
- [ ] Results are repeatable.
- [ ] No universal performance claim is being made from one run.

---

# 57. Learning Checkpoint

Do not move on until you can honestly say you can do all of the following without copying a tutorial.

## Core skills

- [ ] Read a Parquet file with PyArrow.
- [ ] Select only required columns.
- [ ] Apply a row filter.
- [ ] Explain why explicit schemas matter.
- [ ] Inspect metadata using `ParquetFile`.
- [ ] Read a specific row group.
- [ ] Process a large file with `iter_batches()`.
- [ ] Write incrementally with `ParquetWriter`.
- [ ] Control row-group size.
- [ ] Control compression and dictionary settings.
- [ ] Enable statistics.
- [ ] Write page indexes where appropriate.
- [ ] Control timestamp coercion.
- [ ] Build a multi-file dataset with `pyarrow.dataset`.
- [ ] Filter a dataset with Arrow expressions.
- [ ] Read datasets in batches.
- [ ] Write a dataset with `ds.write_dataset`.
- [ ] Use Hive-style partitioning.
- [ ] Control rows per file and row-group bounds.
- [ ] Select deliberate existing-data behavior.
- [ ] Use predictable file names.
- [ ] Recognize schema incompatibility across files.
- [ ] Add and retrieve provenance metadata.
- [ ] Explain object-storage considerations.
- [ ] Explain temporary-output + commit patterns.
- [ ] Run the row-group-size experiment.
- [ ] Write tests that validate Parquet outputs.

## Practical verification

You should also be able to:

1. Explain the physical consequence of a PyArrow writer parameter.
2. Inspect a real output file instead of trusting the configuration.
3. Explain why a filtered query may still read substantial data.
4. Explain why `read_table()` and `iter_batches()` have different operational profiles.
5. Explain why a production dataset can be logically correct but physically poorly designed.

---

# 58. Final Master Mental Model

Keep this model in your head:

```text
                         PYARROW
                            │
              ┌─────────────┴─────────────┐
              │                           │
             READ                        WRITE
              │                           │
        ParquetFile                 Arrow Table / Batch
              │                           │
       columns / filters             explicit schema
              │                           │
      row groups / batches         writer settings
              │                           │
       bounded memory             row groups / pages
              │                           │
              └─────────────┬─────────────┘
                            │
                         PARQUET
                            │
                     Metadata + Data
                            │
                      Object Storage
                            │
                         Dataset
                            │
                 Partitioning + Filtering
                            │
                        Production
```

And the production read path:

```text
Parquet file/dataset
       ↓
Inspect schema + metadata
       ↓
Select required columns
       ↓
Apply filters
       ↓
Use partition / file / row-group metadata
       ↓
Read batches
       ↓
Decode + decompress
       ↓
Transform
       ↓
Write batches
       ↓
Validate output
       ↓
Commit safely
```

## 58.1 The engineering loop

```text
Define schema
      ↓
Batch data
      ↓
Validate
      ↓
Write deliberately
      ↓
Inspect metadata
      ↓
Measure
      ↓
Validate output
      ↓
Commit safely
      ↓
Publish
```

Every arrow is an engineering responsibility.

---

# 59. Final “Remember This”

1. **PyArrow gives Python direct control over Arrow and Parquet workflows.**
2. **A Parquet file should be treated as a deliberately designed physical artifact, not merely an output filename.**
3. **Explicit schemas make production pipelines predictable.**
4. **`read_table()` is convenient; batch APIs matter when data becomes large.**
5. **`ParquetFile` is valuable for inspection and controlled access.**
6. **`ParquetWriter` enables incremental output.**
7. **Row-group size is a performance trade-off, not a magic constant.**
8. **Statistics, encodings, compression, and page indexes are physical controls with measurable consequences.**
9. **Datasets are more than collections of files—they have schema, partitioning, and scanning behavior.**
10. **Object storage requires different publication thinking from local filesystems.**
11. **Production writes should be validated and published deliberately.**
12. **Measure before standardizing.**

The deepest lesson is this:

> **Do not ask only, “What PyArrow API should I call?” Ask, “What physical data layout am I trying to create, what workload must it serve, and how will I prove that the result is correct and efficient?”**

---

# 60. Reference Documentation and Version Discipline

PyArrow is an actively evolving library. For any production deployment, pin the PyArrow version and verify version-sensitive API behavior against the documentation for that version.

Useful official references include:

- Apache Arrow: Reading and Writing Parquet — https://arrow.apache.org/docs/python/parquet.html
- Apache Arrow: `ParquetWriter` — https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetWriter.html
- Apache Arrow: `write_table` — https://arrow.apache.org/docs/python/generated/pyarrow.parquet.write_table.html
- Apache Arrow: Dataset API — https://arrow.apache.org/docs/python/dataset.html
- Apache Arrow: `write_dataset` — https://arrow.apache.org/docs/python/generated/pyarrow.dataset.write_dataset.html
- Apache Arrow: Parquet encryption — https://arrow.apache.org/docs/python/parquet/encryption.html

The official documentation confirms, among other things, the current single-file writer controls, `ParquetFile` metadata inspection, dataset filtering/iteration, `S3FileSystem`, and MinIO support used in this module. citeturn467189search1turn467189search2turn693043search4turn693043search0

---

## Final Principle

```text
PyArrow API
    ↓
Physical Parquet choice
    ↓
Metadata + bytes on storage
    ↓
Reader behavior
    ↓
Observed workload performance
```

**Learn the physical model, control it deliberately, inspect what was actually written, measure the result, and only then standardize the configuration.**
