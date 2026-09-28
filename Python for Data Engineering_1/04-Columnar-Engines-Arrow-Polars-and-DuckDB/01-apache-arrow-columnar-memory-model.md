# Apache Arrow Columnar Memory Model

> **Stage 2 — Python for Data Engineering · Module 2.4 · Topic 01**
>
> This chapter is a complete learning module for Apache Arrow's columnar in-memory model. It is designed to take a learner from first principles to the level where they can reason about memory layout, schema fidelity, copying, interoperability, and production Data Engineering trade-offs.

---

## 0. How to Use This Chapter

Use the chapter sequentially.

A useful study loop for this topic is:

```text
Read
  ↓
Build the smallest example
  ↓
Inspect the schema
  ↓
Inspect the physical buffers
  ↓
Explain the memory layout in your own words
  ↓
Measure memory / time
  ↓
Break the example
  ↓
Fix it
  ↓
Apply the idea to a data pipeline
  ↓
Explain it aloud
```

The objective is not to memorize PyArrow method names. The objective is to develop a durable mental model:

> **What is the logical value? How is that value physically represented? Who owns the memory? Is the operation copying or reusing buffers? What schema crosses the system boundary?**

Those questions become important later when working with Polars, DuckDB, Parquet, Spark, object storage, lakehouses, and ML/AI data pipelines.

---

# 1. Learning Objectives

After completing this chapter, you should be able to:

- Explain what Apache Arrow is and why it exists.
- Distinguish **Arrow**, **PyArrow**, **Parquet**, **DuckDB**, and **Polars**.
- Explain why columnar memory is useful for analytical workloads.
- Create Arrow arrays and tables from Python lists, dictionaries, NumPy arrays, and pandas DataFrames.
- Explain `Array`, `ChunkedArray`, `RecordBatch`, `Table`, `Schema`, `Field`, and `DataType`.
- Inspect `schema`, `num_rows`, and `nbytes`.
- Explain the physical representation of nullable data.
- Explain the role of the validity bitmap.
- Explain the offsets buffer for variable-length values.
- Explain the data buffer.
- Distinguish fixed-width and variable-width layouts.
- Represent nested data using Arrow types such as `list` and `struct`.
- Use explicit schemas for production-safe ingestion.
- Use `pyarrow.compute` for Arrow-native transformations.
- Explain dictionary encoding and its trade-offs.
- Explain run-end encoding at a conceptual level.
- Explain why Arrow columns can be `ChunkedArray` objects.
- Understand why tiny chunks can hurt performance and when `combine_chunks()` helps.
- Explain Arrow's immutability model.
- Explain why some slices can be zero-copy.
- Measure Arrow allocator usage with `pa.total_allocated_bytes()`.
- Explain Arrow IPC, Feather v2, and memory mapping.
- Use schema metadata.
- Explain safe versus unsafe casting.
- Explain why a successful cast is not necessarily a correct cast.
- Reason about zero-copy and low-copy interoperability.
- Explain the Arrow C Data Interface, Arrow Flight, and ADBC at an architectural awareness level.
- Build a realistic Arrow orders table using an explicit schema.
- Test Arrow schemas and values with `pytest`.
- Run performance experiments without assuming universal benchmark numbers.
- Diagnose common memory, schema, null, timestamp, and chunking problems.
- Answer beginner, intermediate, and senior-level Arrow interview questions.
- Decide when Arrow should be part of a production pipeline and when another abstraction is more appropriate.

---

# 2. Prerequisites

This chapter assumes you already have basic familiarity with:

- Python variables, functions, loops, imports, and exceptions.
- NumPy arrays and dtypes.
- pandas DataFrames.
- Missing values / null concepts.
- Views versus copies.
- RAM versus storage.
- Basic Data Engineering ideas such as ingestion, transformation, schemas, and consumers.

You do **not** need to know Apache Arrow beforehand.

This chapter intentionally does not re-teach the earlier modules in full. It builds on them.

### Recommended environment

The module roadmap recommends:

- Python 3.12+.
- A `uv` project.
- `pyarrow`, `polars`, `duckdb`, and `pandas`.
- `pytest`.
- A realistic dataset for later scaling experiments.

Example project setup:

```bash
mkdir columnar_lab
cd columnar_lab

uv init
uv add pyarrow polars duckdb pandas
uv add --dev pytest
```

Check versions:

```python
import pyarrow as pa

print("PyArrow:", pa.__version__)
```

Library APIs can change. When an API is version-sensitive, prefer the documentation for the version installed in your environment.

> **Important:** The examples in this chapter are written to use stable, ordinary PyArrow interfaces. Test them in your environment before embedding them into production code.

---

# 3. Why Apache Arrow Exists

## 3.1 The engineering problem

Imagine a pipeline where data moves through several systems:

```text
Database
   ↓
Python
   ↓
pandas
   ↓
Polars
   ↓
DuckDB
   ↓
Spark
   ↓
another service
```

Every system needs some representation of the data in memory.

Historically, those representations have not always been compatible.

One system may have:

- Python objects.
- NumPy buffers.
- C/C++ structures.
- Java objects.
- JVM columnar structures.
- Custom internal buffers.

If one system cannot directly consume another system's memory representation, the boundary may require:

```text
read
  ↓
deserialize
  ↓
allocate memory
  ↓
convert values
  ↓
copy values
  ↓
construct another representation
```

That is expensive when the dataset is large.

## 3.2 What data movement can cost

Moving data can introduce:

| Cost | What happens |
|---|---|
| Copying | Existing values are copied into new buffers |
| Conversion | One type representation is translated into another |
| Serialization | Objects are encoded for transport or storage |
| Deserialization | Encoded data is reconstructed |
| CPU time | Conversion consumes compute |
| Memory pressure | Multiple representations coexist temporarily |
| Latency | Each boundary adds work before downstream processing can begin |

A 20 GB dataset does not need to be physically copied 20 GB at every pipeline boundary for the pipeline to become slow.

Even smaller intermediate copies can matter when:

- pipelines run repeatedly,
- concurrency is high,
- machines have limited RAM,
- data has many columns,
- strings or nested data are involved,
- latency matters.

## 3.3 Arrow's role

Apache Arrow provides a common specification for representing structured data in memory using a standardized columnar layout.

Conceptually:

```text
System A
   │
   │ Arrow-compatible memory
   ▼
System B
```

The goal is to make data exchange cheaper and more predictable.

Arrow does **not** promise that every conversion is zero-copy.

A better statement is:

> Arrow makes zero-copy or low-copy interoperability possible in cases where the source and target can safely share compatible buffers and types.

That distinction matters in production.

---

# 4. What Apache Arrow Is — and What It Is Not

## 4.1 Apache Arrow IS

Apache Arrow is:

- a language-independent specification,
- a columnar in-memory representation,
- an interoperability standard,
- a foundation for analytical data processing ecosystems.

It defines things such as:

- data types,
- array layouts,
- buffers,
- validity information,
- nested structures,
- interchange interfaces.

## 4.2 Apache Arrow IS NOT

Apache Arrow is not:

- a database,
- a query engine,
- a distributed compute engine,
- Parquet,
- merely a Python package,
- a replacement for DuckDB,
- a replacement for Spark.

A useful architectural classification is:

```text
Arrow      = in-memory data representation/specification
Parquet    = on-disk columnar file format
DuckDB     = analytical query engine / database
Polars     = DataFrame engine
PyArrow    = Python implementation/bindings for Arrow
```

## 4.3 Apache Arrow versus PyArrow

This distinction is critical.

### Apache Arrow

The broader project and specification/ecosystem.

### PyArrow

The Python implementation and bindings that let Python programs use Arrow.

Example:

```python
import pyarrow as pa

arr = pa.array([10, 20, 30])
print(arr)
```

Here, `pa` is the PyArrow Python API.

The Python code is one way of working with the larger Arrow ecosystem.

---

# 5. Row-Oriented vs Columnar Thinking

Before studying Arrow's buffers, understand the core storage idea.

Suppose the logical data is:

| id | name | amount |
|---:|---|---:|
| 1 | A | 100 |
| 2 | B | 200 |
| 3 | C | 300 |

## 5.1 Row-oriented conceptual layout

```text
1, A, 100
2, B, 200
3, C, 300
```

Values belonging to one record are adjacent conceptually.

This is useful when the main access pattern is:

> "Give me the complete record for customer 2."

## 5.2 Columnar conceptual layout

```text
id:
1, 2, 3

name:
A, B, C

amount:
100, 200, 300
```

Values belonging to the same column are grouped.

This is useful when the workload asks:

> "Calculate the average amount across millions of records."

The engine can operate primarily on the `amount` column.

## 5.3 Why columnar layout helps analytics

Columnar layouts can improve:

### Analytical scans

A query using only three of fifty columns does not need to process all fifty columns.

### Vectorized execution

A library can process batches of values using optimized native code rather than repeatedly calling Python functions.

### SIMD opportunities

Modern CPUs can apply one instruction to multiple numeric values where the computation and layout permit it.

### Cache locality

Values required by one computation can be stored close together.

### Compression

Values of the same type often have similar characteristics, creating useful compression opportunities in systems built around columnar data.

### Reduced I/O

When storage and memory layouts support column pruning, unnecessary columns can be avoided.

The important engineering point is:

> Columnar storage is not "automatically faster." It is a layout that matches many analytical access patterns extremely well.

---

# 6. Core Arrow Objects

The seven objects in this section form the basic vocabulary of Arrow.

## 6.1 `DataType`

### What is it?

`DataType` describes what each value means and how values are represented.

Examples:

```python
pa.int64()
pa.float64()
pa.string()
pa.bool_()
pa.timestamp("us", tz="UTC")
```

### Mental model

Think:

> "What kind of value lives in this column?"

### Example

```python
import pyarrow as pa

dtype = pa.int64()

print(dtype)
```

Expected output:

```text
int64
```

### Production lesson

Data types are part of your data contract.

A column called `amount` being interpreted as string instead of decimal can cause downstream errors or silently incorrect calculations.

---

## 6.2 `Field`

A `Field` describes one named schema entry.

Conceptually:

```text
Field
├── name
└── DataType
```

Example:

```python
field = pa.field("customer_id", pa.int64())

print(field)
```

A field can also include nullability and metadata information.

---

## 6.3 `Schema`

A `Schema` is the ordered description of a structured Arrow dataset.

Example:

```python
schema = pa.schema([
    pa.field("order_id", pa.string()),
    pa.field("customer_id", pa.int64()),
    pa.field("amount", pa.decimal128(12, 2)),
])

print(schema)
```

Mental model:

> A schema is the contract for the shape and types of a structured dataset.

---

## 6.4 `Array`

An Arrow `Array` is a column-like sequence of values with one logical data type.

Example:

```python
arr = pa.array([10, 20, 30])

print(arr)
print(arr.type)
print(len(arr))
```

Conceptually:

```text
Array<int64>
[10, 20, 30]
```

An `Array` can also contain nulls.

---

## 6.5 `ChunkedArray`

A `ChunkedArray` is a logical column made from multiple Arrow `Array` chunks.

```text
ChunkedArray
├── Array chunk 1
├── Array chunk 2
└── Array chunk 3
```

This lets a column be assembled from batches without requiring one giant contiguous allocation.

---

## 6.6 `Table`

An Arrow `Table` is a tabular collection of named columns with a schema.

Conceptually:

```text
Table
├── Schema
├── Column A → ChunkedArray
├── Column B → ChunkedArray
└── Column C → ChunkedArray
```

Example:

```python
table = pa.table({
    "id": [1, 2, 3],
    "name": ["A", "B", "C"],
})

print(table)
print(table.schema)
```

---

## 6.7 `RecordBatch`

A `RecordBatch` is a collection of equal-length arrays with a schema.

Think:

> One horizontal batch of records represented as columns.

Example shape:

```text
RecordBatch
├── id:     [1, 2, 3]
├── name:   [A, B, C]
└── amount: [100, 200, 300]
```

Record batches are important for streaming and interchange.

---

## 6.8 How the objects fit together

A useful hierarchy is:

```text
Schema
├── Field
│   └── DataType
│
Table
├── Column
│   └── ChunkedArray
│       ├── Array
│       ├── Array
│       └── Array
│
RecordBatch
├── columns
└── Schema
```

### A practical distinction

| Object | Think of it as |
|---|---|
| `DataType` | What type is this value? |
| `Field` | What is this named schema entry? |
| `Schema` | What columns/types make up this structure? |
| `Array` | One typed sequence of values |
| `ChunkedArray` | One logical column split into arrays |
| `RecordBatch` | One batch of rows represented column-wise |
| `Table` | A complete tabular structure |

---

# 7. Creating Arrow Arrays

Start with the simplest example.

```python
import pyarrow as pa

arr = pa.array([10, 20, 30])

print(arr)
print(arr.type)
```

Expected output:

```text
[
  10,
  20,
  30
]
int64
```

PyArrow inferred the type.

## 7.1 From Python lists

```python
numbers = pa.array([1, 2, 3])
names = pa.array(["Alice", "Bob", "Cara"])
flags = pa.array([True, False, True])
```

## 7.2 Nulls in Python input

```python
arr = pa.array([10, None, 30])

print(arr)
print(arr.type)
```

Arrow represents the column as a typed nullable array.

This is already an important difference from the mental model:

```text
Python list
→ objects / None

Arrow array
→ typed values + Arrow null representation
```

## 7.3 Explicit types

Inference is convenient, but production pipelines often need explicit types.

```python
arr = pa.array(
    [1, 2, 3],
    type=pa.int64(),
)

print(arr.type)
```

For strings:

```python
names = pa.array(
    ["Alice", "Bob", None],
    type=pa.string(),
)

print(names.type)
```

For timestamps:

```python
timestamps = pa.array(
    [
        "2026-01-01 00:00:00",
        "2026-01-02 00:00:00",
    ],
    type=pa.timestamp("us"),
)
```

When timestamp parsing from arbitrary strings becomes important, explicit parsing before construction can make the pipeline easier to reason about.

---

# 8. Creating Arrow Data from Dictionaries

A dictionary of sequences is a convenient way to build a table.

```python
table = pa.table({
    "id": [1, 2, 3],
    "name": ["A", "B", "C"],
    "amount": [100.0, 200.0, 300.0],
})

print(table)
```

A table created this way contains several Arrow columns and a schema.

Inspect it:

```python
print(table.schema)
print(table.num_rows)
print(table.nbytes)
```

### Why this matters

This is useful for:

- small ingestion examples,
- tests,
- fixtures,
- building intermediate Arrow data,
- creating deterministic lab inputs.

For production ingestion, explicit schemas often provide stronger control than inference.

---

# 9. Creating Arrow Data from NumPy

Arrow interoperates naturally with NumPy for many fixed-width types.

```python
import numpy as np
import pyarrow as pa

values = np.array([10, 20, 30], dtype=np.int64)
arr = pa.array(values)

print(arr)
print(arr.type)
```

### Important interoperability idea

For compatible fixed-width arrays, Arrow may be able to reference existing memory rather than creating a second copy.

But do not assume every NumPy → Arrow conversion is zero-copy.

Questions to ask:

1. Is the dtype compatible?
2. Is the data layout compatible?
3. Is the array contiguous?
4. Does the target representation require additional validity information?
5. Is a conversion required for the specific type?

---

# 10. Creating Arrow Data from pandas

Example:

```python
import pandas as pd
import pyarrow as pa

pdf = pd.DataFrame({
    "id": [1, 2, 3],
    "name": ["A", "B", "C"],
})

table = pa.Table.from_pandas(pdf, preserve_index=False)

print(table)
print(table.schema)
```

### Why this matters

Many real pipelines contain a pandas boundary because:

- a library only accepts pandas,
- an older codebase uses pandas,
- an analyst workflow is pandas-based,
- a downstream reporting library expects pandas.

Arrow helps create a common representation between systems, but the exact conversion cost depends on dtypes and memory layout.

---

# 11. Schema, Field, and DataType

The basic inspection APIs from the module roadmap are:

```python
print(table.schema)
print(table.num_rows)
print(table.nbytes)
```

## 11.1 `table.schema`

Shows the table's fields and data types.

```python
print(table.schema)
```

Typical conceptual output:

```text
id: int64
name: string
amount: double
```

## 11.2 `table.num_rows`

```python
print(table.num_rows)
```

This tells you the logical row count.

## 11.3 `table.nbytes`

```python
print(table.nbytes)
```

This reports the number of bytes associated with the Arrow table's buffers according to the table's accounting.

It is useful, but it is not the same thing as:

- total process RSS,
- every Python object allocated,
- every external library allocation,
- disk size,
- compressed file size.

### Production lesson

A single memory metric is never a complete memory profile.

---

# 12. Why Explicit Schemas Matter

Suppose an API emits:

```json
{
  "order_id": "123",
  "amount": "10.50",
  "created_at": "2026-09-26T12:30:00Z"
}
```

If type inference is allowed to decide everything, the pipeline may interpret values differently depending on:

- source data,
- missing values,
- data samples,
- parser behaviour,
- future schema drift.

An explicit schema gives you a contract.

Example:

```python
orders_schema = pa.schema([
    pa.field("order_id", pa.string()),
    pa.field("amount", pa.decimal128(12, 2)),
    pa.field("created_at", pa.timestamp("us", tz="UTC")),
])
```

### Why this matters in Data Engineering

Explicit schemas improve:

- reproducibility,
- validation,
- downstream compatibility,
- data contracts,
- failure visibility,
- type consistency across runs.

---

# 13. Physical Memory Layout — CORE SECTION

This is the most important part of the chapter.

The logical statement:

```text
["cat", null, "apple"]
```

is not simply stored as three Python string objects.

Arrow represents arrays using one or more memory buffers defined by the type layout.

For many nullable variable-length arrays, you can reason about three key pieces:

```text
Arrow array
├── validity bitmap
├── offsets buffer
└── data buffer
```

### Important qualification

**Not every Arrow type requires all three buffers.**

For example:

- a fixed-width `int64` array does not require string-style offsets,
- a non-nullable array may not need a validity bitmap,
- nested types introduce child arrays and additional offsets/validity buffers.

The correct question is:

> Which buffers does this specific Arrow type require?

---

# 14. Validity Bitmap

## 14.1 What is it?

A validity bitmap records whether each logical value is valid or null.

Take:

```text
["A", null, "C", "D", null]
```

Conceptually:

```text
value:
A    null    C    D    null

valid:
1     0      1    1     0
```

Each logical value corresponds to one bit.

```text
1 = valid
0 = null
```

## 14.2 Why one bit?

A byte contains eight bits.

So a bitmap can represent validity for many values using very little space compared with storing a full Python object or byte flag for every value.

Conceptually:

```text
8 values
↓↓↓↓↓↓↓↓
10110110
```

The precise bit order and byte interpretation are implementation details. The logical model is what matters first.

## 14.3 Arrow nulls are first-class

A nullable Arrow array can have:

```text
typed values
+
validity state
```

This is different from the simplistic idea:

```text
"null means a special Python object"
```

Arrow treats nullity as part of the array representation.

## 14.4 Important comparison

### Python list

```python
["A", None, "C"]
```

Contains Python-level objects/references.

### NumPy integer array

Plain NumPy integer arrays do not have a built-in per-element null representation equivalent to Arrow's validity bitmap.

### pandas

pandas supports several missing-value approaches depending on dtype.

### Arrow

Arrow has a standardized nullable representation across its type system.

> Do not infer that all other systems use the same physical representation. The important point is that Arrow defines its own standardized model.

---

# 15. Variable-Length Strings and the Offsets Buffer

This is one of the most important internal models to understand.

Consider:

```text
["cat", "dog", "apple"]
```

These strings have different lengths.

A fixed-width layout cannot simply allocate the same number of bytes for every value.

Instead, Arrow can use:

1. offsets,
2. data bytes,
3. optional validity information.

## 15.1 The offsets idea

Conceptually:

```text
Offsets:

0    3    6    11
|----|----|------|
cat  dog  apple
```

The offset array has one more boundary than the number of values.

For values:

```text
cat
dog
apple
```

the boundaries are:

```text
0
3
6
11
```

Value `i` occupies approximately:

```text
data[offset[i] : offset[i + 1]]
```

So:

```text
value 0 = bytes 0:3
value 1 = bytes 3:6
value 2 = bytes 6:11
```

## 15.2 The data buffer

The actual bytes can be conceptualized as:

```text
catdogapple
```

The offsets tell Arrow how to split those bytes logically.

## 15.3 Add nulls

For:

```text
["cat", null, "apple"]
```

the conceptual model becomes:

```text
validity:
1 0 1

offsets:
0 3 3 8

data:
catapple
```

The null state is described by the validity bitmap.

The offsets/data layout must still satisfy Arrow's structural rules for the array type.

The key mental model is:

> **Validity answers "does a value exist?"**
>
> **Offsets answer "where does this value live in the byte buffer?"**
>
> **The data buffer stores the actual byte payload.**

---

# 16. Inspecting Real Buffers with `arr.buffers()`

For a string array, inspect its buffers.

```python
import pyarrow as pa

arr = pa.array(["cat", None, "apple", "x", None])

print(arr)
buffers = arr.buffers()

for i, buf in enumerate(buffers):
    if buf is None:
        print(i, None)
    else:
        print(i, "size=", buf.size)
```

The exact number and meaning of returned buffers depend on the Arrow type.

For a standard variable-width string array, you should expect the important pieces corresponding to:

- validity bitmap,
- offsets,
- values.

### Important

Do not memorize:

```text
buffer 0 is always X
buffer 1 is always Y
buffer 2 is always Z
```

Instead, learn the array layout for the specific type.

### Investigation exercise

Create:

```python
arr = pa.array(["cat", None, "apple", "x", None])
```

Then inspect:

```python
print(arr.type)
print(arr.buffers())
```

Your task is to connect:

```text
logical values
      ↓
validity bitmap
      ↓
offsets
      ↓
data bytes
```

You should be able to explain the mapping without looking at notes.

---

# 17. Hands-On Buffer Inspection Lab

## Objective

Build a five-element string array with nulls and connect the logical values to the physical layout.

## Step 1 — Build the array

```python
import pyarrow as pa

arr = pa.array([
    "cat",
    None,
    "dog",
    "data",
    None,
], type=pa.string())

print(arr)
print(arr.type)
```

## Step 2 — Inspect buffers

```python
buffers = arr.buffers()

for i, buf in enumerate(buffers):
    print(f"buffer[{i}] =", None if buf is None else buf.size)
```

## Step 3 — Inspect the offsets logically

PyArrow also exposes values through normal array operations. To understand the physical representation, compare the logical values with the buffer structure.

You should write down:

```text
values:
cat
null
dog
data
null
```

Then reason about:

```text
validity:
1 0 1 1 0

offset boundaries:
0 ...
```

## Step 4 — Explain the null case

Ask yourself:

> If the second value is null, why does Arrow not need a Python `None` object stored inside the data buffer?

Because nullity is represented by the validity information.

## What this exercise proves

You are learning to see the difference between:

```text
logical representation
```

and:

```text
physical representation
```

That distinction is central to performance engineering.

---

# 18. Fixed-Width vs Variable-Length Types

## 18.1 Fixed-width types

Examples:

- `int32`
- `int64`
- `float32`
- `float64`

For a fixed-width type, each value has a predictable number of bytes.

For example, conceptually:

```text
int64:
value 0 → 8 bytes
value 1 → 8 bytes
value 2 → 8 bytes
```

A data buffer is enough for values when nullability is not required.

With nullability, a validity bitmap can be added.

## 18.2 Variable-length types

Examples:

- `string`
- `large_string`
- `binary`
- nested list-like structures

Their logical values have different lengths.

Therefore, the physical representation needs additional structural information such as offsets.

### Comparison

| Type | Fixed width? | Offsets required? |
|---|---:|---:|
| `int64` | Yes | No |
| `float64` | Yes | No |
| `bool` | Special bit-packed representation | No string-style offsets |
| `string` | No | Yes |
| `binary` | No | Yes |
| `list<T>` | No | Yes, plus child data |

---

# 19. Arrow Type System

Arrow's type system is broader than simple Python scalar types.

## 19.1 Numeric types

Signed integer families include:

```text
int8
int16
int32
int64
```

Unsigned families include:

```text
uint8
uint16
uint32
uint64
```

Floating-point examples:

```text
float32
float64
```

### Why width matters

Smaller types can reduce memory when the value range safely fits.

But smaller is not automatically better.

Consider:

- maximum value,
- downstream compatibility,
- arithmetic promotion,
- storage format,
- external system expectations.

---

# 20. Decimal Types

Financial amounts often should not be represented as binary floating point if exact decimal semantics are required.

Arrow provides decimal types such as:

```python
pa.decimal128(12, 2)
```

Interpretation:

- precision = 12 total decimal digits,
- scale = 2 digits after the decimal point.

Example:

```python
amounts = pa.array(
    ["10.50", "99.99", None],
    type=pa.decimal128(12, 2),
)

print(amounts)
print(amounts.type)
```

### Why this matters

For money-like values, explicit decimal semantics are often safer than assuming `float64` is equivalent to exact decimal arithmetic.

The correct type depends on the downstream system and business semantics.

---

# 21. Boolean Type

Arrow supports boolean values:

```python
flags = pa.array([True, False, None], type=pa.bool_())

print(flags)
print(flags.type)
```

Boolean storage is optimized differently from ordinary byte-per-value Python objects.

The exact physical representation is governed by Arrow's specification.

The practical lesson:

> Do not assume that the in-memory footprint of a typed Arrow boolean column is equivalent to a Python list of Python `bool` objects.

---

# 22. Temporal Types

Arrow has several temporal types, including:

- `date32`
- `timestamp`
- `duration`

A timestamp includes a time unit and can include a timezone.

Example:

```python
timestamp_type = pa.timestamp("us", tz="UTC")

print(timestamp_type)
```

Conceptually:

```text
timestamp(unit, timezone)
```

Examples of units:

- seconds (`s`)
- milliseconds (`ms`)
- microseconds (`us`)
- nanoseconds (`ns`)

---

# 23. Timestamps and Time Zones

Time semantics are a frequent source of production bugs.

## 23.1 UTC example

```python
import pyarrow as pa

ts_type = pa.timestamp("us", tz="UTC")

values = pa.array(
    [
        "2026-09-26 12:00:00",
        "2026-09-26 13:00:00",
    ],
    type=ts_type,
)

print(values.type)
```

When production systems exchange timestamps, always understand:

- the unit,
- whether the value is timezone-aware,
- the expected timezone,
- how the source encodes time,
- how the target interprets time.

## 23.2 Common production mistakes

### Mistake 1 — Dropping timezone information

A timezone-aware timestamp can be converted into a naive timestamp incorrectly.

### Mistake 2 — Mixing naive and aware timestamps

This can create ambiguous or invalid comparisons.

### Mistake 3 — Changing timestamp units unintentionally

For example:

```text
microseconds
→ milliseconds
```

is not a semantic no-op if precision is lost.

### Mistake 4 — Assuming local time is universal

Distributed systems usually benefit from explicit timezone semantics, often UTC at system boundaries.

### Production lesson

For event pipelines, timestamps are data contracts, not formatting details.

---

# 24. Text and Binary Types

Relevant Arrow text/binary types include:

- `string`
- `large_string`
- `string_view`
- `binary`

## 24.1 `string`

The standard variable-width UTF-8 string type.

## 24.2 `large_string`

Used when a larger offset representation is necessary.

Conceptually, the reason for the distinct type is the range of offsets it can represent.

## 24.3 `string_view`

A view-style string representation can be useful for avoiding some copies in appropriate scenarios.

Do not assume every operation or conversion remains zero-copy.

## 24.4 `binary`

For arbitrary bytes rather than text.

Example:

```python
data = pa.array([
    b"\x01\x02",
    b"\xff\x00",
    None,
], type=pa.binary())

print(data)
```

---

# 25. Nested Types

Modern Data Engineering systems frequently contain nested data.

Examples:

```json
{
  "order_id": "O-1001",
  "tags": ["python", "data", "arrow"],
  "address": {
    "city": "Kolkata",
    "zip": "700001"
  }
}
```

Arrow supports nested structures without simply converting the entire field into opaque Python objects.

Important nested types include:

- `list`
- `struct`
- `map`

---

# 26. Arrow `list` Type

A list-valued column might look like:

```text
tags
---------------------------
["python", "data"]
["arrow"]
[]
null
["sql", "python"]
```

An Arrow list is conceptually represented using:

```text
ListArray
├── validity
├── offsets
└── child array
```

For example:

```text
rows:
0 → ["python", "data"]
1 → ["arrow"]
2 → []
```

The offsets describe where each row's list begins and ends in the child values.

The child values might be:

```text
python
data
arrow
```

This is a crucial idea:

> Nested Arrow data is still structured columnar data.

It is not simply "a Python object blob per row."

---

# 27. Arrow `struct` Type

A struct is like a named record embedded inside each row.

Example:

```text
address:
{
    city: "Kolkata",
    zip: "700001"
}
```

The conceptual layout is:

```text
address
├── city column
└── zip column
```

The nested fields have their own Arrow child arrays.

This allows nested data to preserve type information and structured access.

---

# 28. Arrow `map` Type

A map represents key-value associations.

Conceptually:

```text
attributes:
{
  "tier": "gold",
  "region": "east"
}
```

Map representation is structured rather than being treated as an arbitrary Python dictionary stored in every row.

### Production implication

Use nested types when the source semantics are genuinely nested and downstream systems understand them.

Do not create deeply nested schemas simply because Arrow allows it.

Schema complexity affects:

- query complexity,
- interoperability,
- testing,
- transformations,
- storage layout.

---

# 29. Creating Nested Data with PyArrow

A simple table can use explicit nested types.

```python
import pyarrow as pa

schema = pa.schema([
    pa.field("order_id", pa.string()),
    pa.field("tags", pa.list_(pa.string())),
    pa.field(
        "address",
        pa.struct([
            pa.field("city", pa.string()),
            pa.field("zip", pa.string()),
        ]),
    ),
])

table = pa.Table.from_pydict(
    {
        "order_id": ["O1", "O2"],
        "tags": [
            ["python", "arrow"],
            ["data"],
        ],
        "address": [
            {"city": "Kolkata", "zip": "700001"},
            {"city": "Delhi", "zip": "110001"},
        ],
    },
    schema=schema,
)

print(table.schema)
print(table)
```

The exact rendering can vary by PyArrow version, but the schema should reflect the nested types.

---

# 30. Dictionary Encoding

Dictionary encoding is useful when many values repeat.

Consider:

```text
["IN", "IN", "US", "IN", "US"]
```

Instead of storing every string in full, conceptually create:

```text
dictionary:
0 → IN
1 → US
```

Then store:

```text
indices:
0, 0, 1, 0, 1
```

## 30.1 Why it can save memory

Without dictionary encoding:

```text
IN
IN
US
IN
US
```

With dictionary encoding:

```text
dictionary:
IN
US

indices:
0
0
1
0
1
```

For repeated values, the dictionary can reduce repeated payload storage.

## 30.2 It is not always a win

Dictionary encoding introduces:

- a dictionary,
- indices,
- dictionary management,
- potential complexity during operations.

If almost every value is unique:

```text
country_000001
country_000002
country_000003
...
```

the dictionary can provide little benefit or even add overhead.

### Rule

> Dictionary encoding is a workload-dependent optimization, not a universal compression switch.

---

# 31. Dictionary Encoding with PyArrow

You can use dictionary encoding for a string array.

```python
import pyarrow as pa

countries = pa.array(["IN", "IN", "US", "IN", "US", None])

dictionary_array = countries.dictionary_encode()

print(dictionary_array)
print(dictionary_array.type)
```

You can inspect:

```python
print(dictionary_array.dictionary)
print(dictionary_array.indices)
```

A typical conceptual result is:

```text
dictionary:
["IN", "US"]

indices:
[0, 0, 1, 0, 1, null]
```

The exact printed representation depends on the installed version.

---

# 32. Measuring Dictionary-Encoding Effects

Do not claim a universal memory saving.

Measure it.

```python
import pyarrow as pa

countries = pa.array(["IN"] * 100_000 + ["US"] * 100_000)

plain = countries
encoded = countries.dictionary_encode()

print("plain bytes:", plain.nbytes)
print("dictionary bytes:", encoded.nbytes)
```

Then change the experiment:

```python
unique_values = pa.array([
    f"country_{i}"
    for i in range(100_000)
])

encoded_unique = unique_values.dictionary_encode()

print("plain unique bytes:", unique_values.nbytes)
print("encoded unique bytes:", encoded_unique.nbytes)
```

The result is environment- and implementation-dependent.

Your job is to explain **why** the numbers differ, not to memorize a number.

---

# 33. Run-End Encoding

Run-end encoding is useful when values appear in repeated runs.

Example:

```text
A A A A B B C C C
```

Instead of representing every repeated value independently, the representation can store:

```text
run ends:
4, 6, 9

values:
A, B, C
```

Conceptually:

```text
1–4 → A
5–6 → B
7–9 → C
```

This works especially well when repeated values occur in contiguous runs.

### Compare with dictionary encoding

Dictionary encoding addresses repeated **distinct values**:

```text
A, B, A, C, A, B
```

Run-end encoding is particularly useful when values form long **runs**:

```text
A, A, A, A, A, B, B, B
```

These are different physical compression strategies.

### Scope for this chapter

You need to understand:

- the concept,
- the reason it exists,
- the workload pattern it targets.

The advanced implementation details are outside the core learning objective here.

---

# 34. `pyarrow.compute`

Arrow is more than a storage model.

PyArrow exposes a compute layer through:

```python
pyarrow.compute
```

Example:

```python
import pyarrow as pa
import pyarrow.compute as pc

values = pa.array([10, 20, 30, 40])

result = pc.add(values, 5)

print(result)
```

Expected logical result:

```text
[15, 25, 35, 45]
```

## 34.1 Filtering

```python
mask = pc.greater(values, 20)

filtered = pc.filter(values, mask)

print(filtered)
```

## 34.2 Aggregation

```python
total = pc.sum(values)

print(total.as_py())
```

## 34.3 `take`

```python
indices = pa.array([3, 0, 2])

selected = pc.take(values, indices)

print(selected)
```

## 34.4 Sorting

```python
indices = pc.sort_indices(values)

print(indices)
```

The returned indices can then be used to reorder related columns.

---

# 35. String Compute

Arrow-native string operations avoid turning every value into a Python object just to execute a simple operation.

Example:

```python
import pyarrow as pa
import pyarrow.compute as pc

names = pa.array(["alice", "bob", "charlie"])

lengths = pc.utf8_length(names)

print(lengths)
```

The exact function set depends on the installed PyArrow version.

### Engineering lesson

Prefer native Arrow compute when the required operation exists.

This usually gives the system an opportunity to use optimized native implementations.

But never make the blanket claim:

> "Arrow compute is always faster."

Performance still depends on:

- operation,
- data type,
- data size,
- null density,
- memory access,
- CPU,
- version,
- surrounding pipeline costs.

---

# 36. Python Loops vs Arrow Compute

Python-level loop:

```python
values = [1, 2, 3, 4, 5]

result = []
for value in values:
    result.append(value * 2)
```

Arrow compute:

```python
import pyarrow as pa
import pyarrow.compute as pc

values = pa.array([1, 2, 3, 4, 5])

result = pc.multiply(values, 2)

print(result)
```

The Arrow version allows the computation to remain in the Arrow-native representation.

That matters because repeated conversions like:

```text
Arrow
  ↓
Python objects
  ↓
Python computation
  ↓
Arrow again
```

can erase the performance benefit of the columnar representation.

---

# 37. Complete Orders Table — Production-Oriented Example

The module roadmap specifies this schema:

```text
order_id: string
customer_id: int64 (nullable)
amount: decimal128(12, 2)
created_at: timestamp("us", tz="UTC")
tags: list<string>
address: struct<city: string, zip: string>
```

This example combines:

- primitive types,
- nullable values,
- decimal precision,
- timezone-aware timestamps,
- nested list data,
- nested struct data.

---

# 38. Building the Orders Table

```python
from datetime import datetime, timezone

import pyarrow as pa


orders_schema = pa.schema([
    pa.field("order_id", pa.string()),
    pa.field("customer_id", pa.int64()),
    pa.field("amount", pa.decimal128(12, 2)),
    pa.field(
        "created_at",
        pa.timestamp("us", tz="UTC"),
    ),
    pa.field(
        "tags",
        pa.list_(pa.string()),
    ),
    pa.field(
        "address",
        pa.struct([
            pa.field("city", pa.string()),
            pa.field("zip", pa.string()),
        ]),
    ),
])

orders = pa.Table.from_pydict(
    {
        "order_id": ["O-1001", "O-1002", "O-1003"],
        "customer_id": [101, None, 103],
        "amount": ["125.50", "200.00", "80.25"],
        "created_at": [
            datetime(2026, 9, 26, 10, 0, tzinfo=timezone.utc),
            datetime(2026, 9, 26, 11, 30, tzinfo=timezone.utc),
            datetime(2026, 9, 26, 12, 15, tzinfo=timezone.utc),
        ],
        "tags": [
            ["python", "data"],
            ["arrow"],
            ["sql", "analytics"],
        ],
        "address": [
            {"city": "Kolkata", "zip": "700001"},
            {"city": "Delhi", "zip": "110001"},
            {"city": "Mumbai", "zip": "400001"},
        ],
    },
    schema=orders_schema,
)

print(orders.schema)
print("rows:", orders.num_rows)
print("bytes:", orders.nbytes)
```

### What to observe

Your schema should preserve:

```text
order_id      → string
customer_id   → nullable int64
amount        → decimal128(12, 2)
created_at    → timestamp with microseconds + UTC
tags          → list<string>
address       → struct<city:string, zip:string>
```

### Production lesson

A good ingestion pipeline should make schema decisions deliberately rather than depending on whatever types happen to appear in the first few records.

---

# 39. Filtering the Orders Table

Use Arrow-native compute.

A simple example:

```python
import pyarrow.compute as pc

customer_ids = orders["customer_id"]

mask = pc.equal(customer_ids, 101)

filtered = orders.filter(mask)

print(filtered)
```

Because `customer_id` is nullable, null behavior must be understood rather than guessed.

### Engineering rule

Whenever a field is nullable, test:

- matching non-null values,
- non-matching values,
- null values.

---

# 40. Computing Totals

A decimal column should remain decimal-aware when business semantics require exact decimal processing.

You can inspect the amount column:

```python
amounts = orders["amount"]

print(amounts.type)
print(amounts)
```

For more advanced operations, check the compute-function support in your installed PyArrow version.

The architectural principle is:

> Keep the data in an appropriate typed representation as long as possible.

Avoid unnecessary round trips such as:

```text
decimal
→ Python float
→ computation
→ decimal again
```

unless that conversion is intentional and safe.

---

# 41. Extracting `address.city`

A struct field can be extracted using Arrow's nested-data support.

One approach is to use a field-selection compute function where available:

```python
address = orders["address"]

cities = address.field("city")

print(cities)
```

This keeps the nested structure typed.

### What this demonstrates

The `address` field is not a Python dictionary per row in the conceptual Arrow model.

It is a structured Arrow value composed of child arrays.

---

# 42. Understanding `Table["column"]`

A subtle but important point:

```python
orders["order_id"]
```

returns a column-like Arrow object.

At the table level, the column is commonly a:

```text
ChunkedArray
```

That means:

```text
orders["order_id"]
    ↓
ChunkedArray
    ├── Array
    ├── Array
    └── ...
```

Even when a table has only one chunk, Arrow's table model allows multiple chunks.

---

# 43. `ChunkedArray`

## 43.1 Why chunking exists

Large data rarely arrives as one perfectly sized, permanently allocated block.

Data can be produced incrementally:

```text
batch 1
batch 2
batch 3
batch 4
```

A table can represent those batches as chunks.

```text
Table
└── order_id: ChunkedArray
      ├── chunk 1
      ├── chunk 2
      ├── chunk 3
      └── chunk 4
```

## 43.2 Why chunking is useful

Chunking can improve:

- incremental construction,
- streaming workflows,
- memory management,
- interoperability,
- batch-oriented processing.

## 43.3 Why tiny chunks can hurt

Suppose instead you have:

```text
100,000 tiny chunks
```

The logical column may then carry significant per-chunk overhead.

Operations may need to navigate many arrays rather than a smaller set of reasonably sized chunks.

This can hurt:

- metadata overhead,
- iteration,
- kernel setup,
- cache behavior,
- some downstream operations.

### Production lesson

Chunk count is a performance characteristic worth inspecting.

---

# 44. Inspecting Chunks

```python
column = orders["order_id"]

print("number of chunks:", column.num_chunks)

for i, chunk in enumerate(column.chunks):
    print(i, len(chunk), chunk.type)
```

For a simple table created in one call, you may see one chunk.

A table read from multiple record batches or files can have more.

---

# 45. `combine_chunks()`

Arrow provides:

```python
table.combine_chunks()
```

This can consolidate compatible chunks into fewer chunks.

Example:

```python
combined = orders.combine_chunks()

print(
    "before:",
    orders["order_id"].num_chunks,
)

print(
    "after:",
    combined["order_id"].num_chunks,
)
```

### Important

Combining chunks can require allocating new buffers and copying data.

Therefore:

> `combine_chunks()` is not a free cleanup operation.

Use it intentionally.

### When it can help

- A downstream operation benefits from fewer chunks.
- You need simpler contiguous-ish data access.
- Chunk fragmentation has become measurable overhead.

### When not to do it blindly

- The data is huge.
- Existing chunking is already efficient.
- Memory pressure is high.
- You do not have evidence that consolidation helps.

---

# 46. Chunk Size and Batch Size

Chunking and batch sizing are closely related.

Think of incoming data:

```text
source
  ↓
batch 1
batch 2
batch 3
...
```

If batches are extremely small:

```text
batch
batch
batch
batch
batch
...
```

overhead grows.

If batches are extremely large:

```text
one giant batch
```

memory pressure grows.

The desired outcome is usually:

```text
reasonably sized batches
+
enough throughput
+
acceptable memory usage
```

There is **no universal batch size**.

The right size depends on:

- available RAM,
- row width,
- data types,
- string/nested payloads,
- downstream consumers,
- network transport,
- file format,
- concurrency,
- workload latency requirements.

---

# 47. Chunking in a Real Pipeline

A useful mental model:

```text
API / database / file
        ↓
     batches
        ↓
RecordBatch
        ↓
ChunkedArray
        ↓
Arrow Table
        ↓
Polars / DuckDB / Parquet / another consumer
```

This is one reason the Arrow data model is useful for data engineering.

It does not force every stage to materialize everything as one giant Python object graph.

---

# 48. Immutability

Arrow data structures are designed around immutable arrays.

That means the underlying values are not edited in-place like a normal Python list.

Compare:

```python
values = [1, 2, 3]
values[0] = 100
```

with an Arrow array:

```python
import pyarrow as pa

arr = pa.array([1, 2, 3])
```

You do not normally mutate the underlying Arrow buffer directly.

Instead, transformations produce a new logical result.

## 48.1 Why immutability helps

Immutability makes it easier to reason about:

- shared buffers,
- safe reuse,
- concurrency,
- deterministic pipelines,
- interoperability.

If two consumers share the same immutable buffer, one consumer cannot unexpectedly modify the bytes underneath the other.

## 48.2 Important mental model

```text
input Arrow array
      ↓
transformation
      ↓
new result
```

not:

```text
input array
      ↓
mutate internal bytes
```

### Production lesson

Immutability is one reason buffer-sharing designs can be safer.

---

# 49. Slicing and Zero-Copy Thinking

Suppose:

```python
arr = pa.array([10, 20, 30, 40, 50])
```

You want:

```text
[20, 30, 40]
```

A slice can represent a view over the original buffers instead of eagerly copying all values.

Example:

```python
subset = arr.slice(1, 3)

print(subset)
```

Conceptually:

```text
original buffer:
[10, 20, 30, 40, 50]
      ↑
      └── slice starts here
```

## 49.1 Why slicing can be cheap

The sliced object can maintain:

- a reference to the existing buffer,
- an offset,
- a length.

The bytes do not necessarily need to be copied immediately.

## 49.2 The engineering question

Whenever you create a derived object, ask:

> Does this operation reuse existing buffers, or does it allocate new memory?

This question should become a habit.

---

# 50. Zero-Copy Is Not a Magic Word

Zero-copy can fail or become impossible when:

- types are incompatible,
- values need transformation,
- validity information has to be created,
- a target representation has different memory requirements,
- strings are represented differently,
- timestamps need conversion,
- nested structures differ,
- chunks must be consolidated,
- a consumer requires a different ownership/layout model.

Therefore:

```text
Arrow
≠
everything is zero-copy
```

A more accurate model is:

```text
Arrow
  ↓
can enable low-copy or zero-copy interoperability
  ↓
when memory layouts and semantics are compatible
```

---

# 51. Memory Pools

PyArrow tracks allocations through an Arrow memory pool.

A useful metric is:

```python
import pyarrow as pa

print(pa.total_allocated_bytes())
```

## 51.1 Simple experiment

```python
import pyarrow as pa

before = pa.total_allocated_bytes()

arr = pa.array(range(100_000))

after = pa.total_allocated_bytes()

print("before:", before)
print("after :", after)
print("delta :", after - before)
```

Then make another allocation:

```python
arr2 = pa.array(["data"] * 100_000)

after_second = pa.total_allocated_bytes()

print("after second:", after_second)
```

## 51.2 What the number means

It gives visibility into memory allocated through Arrow's allocator accounting.

It does **not** mean:

> "This is the exact RSS of the entire Python process."

A process can also use memory for:

- Python objects,
- NumPy allocations,
- operating-system mappings,
- native libraries,
- temporary buffers outside the same accounting path.

### Production lesson

Use allocator metrics as one signal within a broader memory profile.

---

# 52. Memory Experiment

Record several stages:

```python
import pyarrow as pa

print("start:", pa.total_allocated_bytes())

numbers = pa.array(range(1_000_000))
print("after numbers:", pa.total_allocated_bytes())

strings = pa.array(["x"] * 1_000_000)
print("after strings:", pa.total_allocated_bytes())

table = pa.table({
    "numbers": numbers,
    "strings": strings,
})
print("after table:", pa.total_allocated_bytes())
```

### Investigation questions

1. Which operation caused the largest allocation?
2. Why do strings have different storage behaviour than integers?
3. Does the table creation itself necessarily duplicate the column buffers?
4. What does `table.nbytes` report?
5. How does process-level memory compare?

---

# 53. Arrow IPC

Arrow needs a way to move Arrow data efficiently between processes, files, and services.

Arrow IPC provides standardized mechanisms for serializing Arrow structures.

At a high level, there are:

- an IPC streaming representation,
- an IPC file representation.

The goal is to preserve Arrow's typed columnar representation efficiently rather than reducing everything to arbitrary Python objects.

---

# 54. In-Memory Arrow vs Arrow IPC

Do not confuse:

```text
Arrow in memory
```

with:

```text
Arrow IPC on disk / in a stream
```

The relationship is:

```text
Arrow arrays/tables
       ↓
Arrow IPC encoding
       ↓
bytes / stream / file
```

Then:

```text
IPC bytes/file
       ↓
Arrow reader
       ↓
Arrow arrays/tables
```

IPC is about interchange/serialization.

Arrow's in-memory layout is about how the data is represented while actively used.

---

# 55. Arrow IPC Streaming

A streaming IPC format is useful when data arrives as record batches over time.

Conceptually:

```text
RecordBatch 1
      ↓
RecordBatch 2
      ↓
RecordBatch 3
      ↓
stream
```

The receiver can process batches incrementally rather than requiring one complete table before any data can be consumed.

This aligns naturally with Data Engineering patterns such as:

- batch ingestion,
- network transport,
- pipelines,
- streaming systems.

---

# 56. Arrow IPC File Format

An IPC file can store Arrow data in a form suitable for file-based exchange.

One common practical use is local analytics workflows where:

- an earlier job produces Arrow-compatible data,
- a later job reads it,
- type fidelity matters,
- fast local loading matters.

---

# 57. Feather v2

Feather is a file format built around Arrow IPC.

A practical mental model is:

```text
Feather v2
≈ Arrow IPC file-oriented storage
```

It is designed for fast data interchange.

## 57.1 Small example

```python
import pyarrow as pa
import pyarrow.feather as feather

table = pa.table({
    "id": [1, 2, 3],
    "name": ["A", "B", "C"],
})

feather.write_feather(table, "example.feather")

loaded = feather.read_table("example.feather")

print(loaded)
```

## 57.2 Feather versus Parquet

They are not interchangeable concepts.

| Concern | Feather / IPC | Parquet |
|---|---|---|
| Primary role | Fast Arrow-oriented interchange | Durable analytical file storage |
| In-memory relationship | Very close to Arrow memory model | Disk-oriented columnar format |
| Row groups/pages | Not its defining structure | Core part of Parquet |
| Lake analytics | Not usually the default lake format | Common choice |
| Interchange between DataFrame tools | Strong fit | Also strong, but different storage semantics |

### Production lesson

Use the format that matches the job.

Do not choose Feather merely because it is "an Arrow format."

---

# 58. Memory Mapping

Memory mapping lets a process access file-backed bytes through the operating system's virtual memory system.

Instead of:

```text
file
 ↓
read whole file
 ↓
allocate RAM
 ↓
copy
```

a memory-mapped design can provide access to file-backed memory through mapped pages.

Conceptually:

```text
disk file
   ↓
memory map
   ↓
virtual address space
   ↓
access pages as needed
```

The operating system manages page loading.

---

# 59. Arrow IPC Memory Mapping

Arrow IPC files are particularly well-suited to memory-mapped access in scenarios where the file representation and access pattern allow it.

The useful mental model is:

```text
IPC file on disk
      ↓
memory map
      ↓
Arrow reader
      ↓
fast access to file-backed buffers
```

This can make local data access very fast and avoid eagerly copying the entire file into ordinary heap allocations.

## Important caveats

Memory mapping does not mean:

- disk is as fast as RAM,
- every query becomes zero-copy,
- all pages are loaded instantly,
- all operations avoid allocations.

Performance depends on:

- storage device,
- OS cache state,
- file structure,
- access pattern,
- working-set size,
- whether downstream operations require new buffers.

---

# 60. Memory Mapping Benchmark

The roadmap asks for a conceptual comparison:

```text
CSV load
    vs
Arrow IPC normal load
    vs
memory-mapped IPC load
```

Create an executable benchmark instead of writing a fixed number.

```python
from pathlib import Path
from time import perf_counter

import pyarrow as pa
import pyarrow.csv as pacsv
import pyarrow.ipc as ipc


table = pa.table({
    "id": list(range(1_000_000)),
    "value": [float(i) / 10 for i in range(1_000_000)],
})

ipc_path = Path("benchmark.arrow")
csv_path = Path("benchmark.csv")

with ipc_path.open("wb") as sink:
    with ipc.new_file(sink, table.schema) as writer:
        writer.write_table(table)

pacsv.write_csv(table, csv_path)


start = perf_counter()
csv_table = pacsv.read_csv(csv_path)
csv_seconds = perf_counter() - start


start = perf_counter()
with ipc_path.open("rb") as source:
    reader = ipc.RecordBatchFileReader(source)
    ipc_table = reader.read_all()
ipc_seconds = perf_counter() - start


print("CSV seconds:", csv_seconds)
print("IPC seconds:", ipc_seconds)
print("rows:", csv_table.num_rows, ipc_table.num_rows)
```

For memory-mapped access, use the Arrow IPC file reader's memory-mapping support available in your installed version.

### Do not hard-code expected performance numbers.

Run it and record:

- elapsed time,
- file sizes,
- machine,
- storage type,
- repeated runs,
- cold/warm conditions.

---

# 61. Schema Metadata

Arrow schemas can carry metadata in addition to field/type definitions.

Conceptually:

```text
Schema
├── fields
└── metadata
```

Metadata can carry information such as:

- application-level conventions,
- producer identifiers,
- semantic hints,
- pipeline version markers,
- other non-value annotations.

## 61.1 Adding metadata

```python
import pyarrow as pa

schema = pa.schema([
    pa.field("id", pa.int64()),
    pa.field("name", pa.string()),
])

metadata = {
    b"producer": b"orders-ingestion",
    b"schema_version": b"1",
}

schema_with_metadata = schema.with_metadata(metadata)

print(schema_with_metadata.metadata)
```

## 61.2 Important caveat

Metadata should not be used as a substitute for the actual schema.

For example, do not store:

```text
amount_is_decimal = "true"
```

in metadata while the actual column is incorrectly typed as string.

The actual Arrow type should express the structural contract.

---

# 62. Schema Metadata — Production Uses

Metadata can help with:

- lineage hints,
- producer identification,
- version tracking,
- compatibility checks,
- integration conventions.

But keep metadata:

- stable,
- documented,
- namespaced where appropriate,
- small,
- useful to downstream consumers.

Do not turn metadata into an undocumented second database of configuration.

---

# 63. Casting and Type Safety

Data pipelines often need type conversion.

For example:

```text
int64
→ int32
```

or:

```text
string
→ timestamp
```

or:

```text
double
→ int64
```

The important distinction is:

```text
can this representation happen?
```

versus:

```text
is this representation safe and semantically correct?
```

---

# 64. Safe Casting

PyArrow's casting APIs support safe conversion controls.

Example:

```python
import pyarrow as pa
import pyarrow.compute as pc

values = pa.array([1, 2, 3], type=pa.int64())

result = pc.cast(
    values,
    pa.int32(),
    safe=True,
)

print(result)
```

If values fit the target type, the cast can succeed.

---

# 65. Unsafe Casting

Consider:

```text
int64
value = 3_000_000_000
```

That value does not fit in signed `int32`.

An unsafe conversion can change the value representation rather than rejecting it.

The exact observed behaviour should be verified in your installed version, but the production lesson is stable:

> An unsafe cast can silently alter data.

That is why safe conversion should be preferred when correctness matters.

---

# 66. Demonstrating a Dangerous Cast

Use an intentionally risky value.

```python
import pyarrow as pa
import pyarrow.compute as pc

values = pa.array([3_000_000_000], type=pa.int64())

try:
    safe_result = pc.cast(
        values,
        pa.int32(),
        safe=True,
    )
    print("safe:", safe_result)
except (pa.ArrowInvalid, pa.ArrowNotImplementedError) as exc:
    print("safe cast rejected:", exc)
```

Then investigate the unsafe form:

```python
unsafe_result = pc.cast(
    values,
    pa.int32(),
    safe=False,
)

print("unsafe:", unsafe_result)
```

Do not rely on a particular numeric result from the unsafe conversion without testing your installed version.

The test demonstrates the principle:

```text
safe=True
→ reject unsafe conversion

safe=False
→ permit conversion that may lose information
```

---

# 67. The Production Rule for Casting

Memorize this:

> **A successful cast is not necessarily a correct cast.**

Before converting a field, ask:

1. Can the target type represent every source value?
2. Can precision be lost?
3. Can scale change?
4. Can timezone information be lost?
5. Can null semantics change?
6. Does the downstream system expect the target type?
7. Do we want failure or silent coercion?

---

# 68. Arrow vs Parquet

This distinction is mandatory for Data Engineers.

| Concern | Arrow | Parquet |
|---|---|---|
| Primary role | In-memory representation/specification | On-disk columnar file format |
| Location | Primarily memory | Storage |
| Core structures | Arrays, buffers, schemas | Files, row groups, pages, statistics |
| Main value | Interoperability + analytics memory layout | Durable analytical storage |
| Compression | Not the central idea of Arrow memory | Important part of Parquet storage |
| Query engine? | No | No |
| Typical role in pipeline | In-memory handoff | Storage layer |

## 68.1 How they work together

A common pipeline:

```text
Parquet file
     ↓
read
     ↓
Arrow representation in memory
     ↓
Polars / DuckDB / pandas / Spark / another consumer
```

And the reverse:

```text
Arrow / DataFrame
     ↓
write
     ↓
Parquet file
     ↓
object storage
```

### Important mental model

```text
Arrow = how data can be represented in memory
Parquet = how data can be stored in a file
```

---

# 69. Why Confusing Arrow and Parquet Is a Mistake

A common beginner statement is:

> "Arrow is a file format like Parquet."

That is incorrect.

Another is:

> "Parquet is just Arrow on disk."

That is also too simplistic.

Parquet and Arrow are related through the broader columnar ecosystem, but they have different purposes and physical designs.

Parquet has its own structures such as:

- row groups,
- pages,
- column chunks,
- statistics.

Those are storage-format concepts.

Arrow's core concepts include:

- arrays,
- buffers,
- record batches,
- tables,
- schemas.

Those are in-memory/interchange concepts.

---

# 70. Arrow vs Database vs Query Engine

Use this architectural map:

```text
Arrow      = data representation
Parquet    = file format
Polars     = DataFrame engine
DuckDB     = analytical SQL engine/database
```

They can cooperate:

```text
Parquet
   ↓
Arrow-compatible data
   ↓
Polars
   ↓
Arrow
   ↓
DuckDB
```

Or:

```text
Parquet
   ↓
DuckDB
   ↓
Arrow result
   ↓
pandas
```

The key is to understand that these components operate at different layers.

---

# 71. Interoperability

Arrow's importance becomes clearer when you think about pipeline boundaries.

Imagine:

```text
pandas
   ↓
Arrow
   ↓
Polars
   ↓
DuckDB
   ↓
Arrow
   ↓
pandas
```

Without a shared memory model, every boundary may need a custom conversion.

With Arrow-compatible interfaces, compatible systems may exchange data more directly.

## 71.1 The cost question

Every boundary should trigger these questions:

```text
Does this conversion allocate?
Does it copy?
Does it preserve nulls?
Does it preserve timezone?
Does it preserve decimals?
Does it preserve nested structures?
Does it consolidate chunks?
```

This is how you think like a performance-oriented Data Engineer.

---

# 72. Interoperability Architecture

A useful conceptual architecture:

```text
                    ┌─────────────┐
                    │   pandas    │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │    Arrow    │
                    └──────┬──────┘
               ┌──────────┼──────────┐
               ▼          ▼          ▼
          ┌────────┐ ┌────────┐ ┌─────────┐
          │ Polars │ │ DuckDB │ │  Spark  │
          └────────┘ └────────┘ └─────────┘
```

The point is not that every path is literally implemented identically.

The point is:

> Arrow acts as a common language for typed columnar data exchange.

---

# 73. Zero-Copy and Low-Copy Boundaries

A good pipeline tries to avoid unnecessary movement.

Bad pattern:

```text
Arrow
 ↓
pandas
 ↓
Arrow
 ↓
Polars
 ↓
pandas
 ↓
Arrow
```

Each boundary may introduce cost.

A better pattern is:

```text
Parquet
 ↓
Arrow / Polars
 ↓
DuckDB
 ↓
small final result
 ↓
pandas
```

The pandas boundary is placed at the edge where it is actually required.

### Engineering principle

> Minimize the number of representation changes, especially on large data.

---

# 74. Type Fidelity at Boundaries

Interoperability is not only about speed.

It is also about correctness.

Watch for:

- nullable integers,
- decimals,
- timestamps,
- timezone information,
- categoricals / dictionaries,
- nested lists,
- structs,
- differing string representations.

A fast conversion that changes a timestamp from:

```text
2026-09-26 12:00 UTC
```

into:

```text
2026-09-26 12:00 naive
```

may be operationally worse than a slower but correct conversion.

---

# 75. Arrow C Data Interface — Awareness Level

The Arrow C Data Interface provides a standardized way for systems to exchange Arrow data structures at a low level.

Why does it exist?

Because independent libraries should not need to know each other's private internal C/C++ implementation details just to exchange columnar data.

Conceptually:

```text
Producer library
      ↓
Arrow C interface
      ↓
Consumer library
```

The benefit is interoperability at the ABI/data-interface level.

### Why a Data Engineer should care

You may not implement the C interface yourself.

But you should understand that:

- it supports cross-language interoperability,
- it can enable efficient exchange,
- it reduces dependence on private implementation details.

---

# 76. Arrow C Data Interface vs Serialization

These are different concepts.

### C Data Interface

Primarily about exchanging Arrow structures in process through a defined interface.

### Serialization

Turns structured data into bytes for:

- files,
- network transport,
- persistence.

Conceptually:

```text
C Data Interface
→ in-process interchange

IPC / Parquet / other serialization
→ bytes for storage/transport
```

This distinction helps you avoid treating every data boundary as the same kind of problem.

---

# 77. Arrow PyCapsule Interface

Modern Python interoperability can use the Arrow-oriented PyCapsule protocol to exchange Arrow data between libraries.

The high-level purpose is:

```text
Python library A
      ↓
Arrow-compatible capsule/interface
      ↓
Python library B
```

The consumer can access the producer's Arrow representation without requiring a Python-level copy of every value.

### Awareness-level takeaway

You do not need to implement the protocol in this chapter.

You need to understand:

> It is one of the mechanisms that makes Python data libraries more interoperable without requiring expensive conversion through ordinary Python objects.

---

# 78. Arrow Flight — Awareness Level

Arrow Flight is a high-performance transport protocol designed around Arrow data.

Think:

```text
Arrow data
   ↓
network transport
   ↓
Arrow data
```

The important distinction is:

```text
write Parquet
```

versus:

```text
stream Arrow data over a transport protocol
```

A file format is optimized around persistent storage semantics.

A transport protocol is optimized around communication between systems.

### Why it matters

For high-throughput distributed analytical systems, moving typed columnar batches efficiently can be important.

---

# 79. ADBC — Awareness Level

ADBC stands for **Arrow Database Connectivity**.

Its goal is conceptually similar to database connectivity interfaces, but oriented around Arrow-native data movement.

The useful mental model is:

```text
Database
   ↓
ADBC
   ↓
Arrow data
   ↓
Data processing engine
```

Why is this useful?

Because a database result can be delivered in a columnar Arrow-friendly representation rather than requiring an expensive round trip through generic Python row objects.

### Senior-engineer awareness

You should recognize ADBC as part of the larger movement toward:

```text
database
→ Arrow
→ analytical processing
```

rather than:

```text
database
→ one Python object per row
→ rebuild columns
```

---

# 80. Performance Principle: Data Movement Can Dominate Computation

Consider a hypothetical pipeline:

```text
10 GB source
     ↓
conversion: 10 GB copy
     ↓
transformation: 1 GB output
     ↓
conversion: another 10 GB copy
```

Even if the transformation itself is fast, the data movement can dominate runtime and memory.

This is why Arrow knowledge matters to a senior Data Engineer.

The optimization target may not be:

```text
"make the SQL 5% faster"
```

It may be:

```text
"remove the 10 GB conversion boundary entirely"
```

---

# 81. Mini Performance Lab

The roadmap requires comparison of:

1. Python list.
2. NumPy object array.
3. pandas object/string column.
4. Arrow string array.

The experiment should measure:

- memory,
- string-length computation time.

Do not fabricate results.

---

# 82. Performance Lab Code

Create a benchmark script such as `benchmarks/string_memory.py`.

```python
from time import perf_counter

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc


N = 1_000_000

values = [f"value-{i % 100}" for i in range(N)]

python_list = values
numpy_object = np.array(values, dtype=object)
pandas_series = pd.Series(values, dtype="object")
arrow_array = pa.array(values, type=pa.string())


def benchmark(name, fn, repetitions=5):
    # Warm-up
    fn()

    times = []

    for _ in range(repetitions):
        start = perf_counter()
        fn()
        times.append(perf_counter() - start)

    average = sum(times) / len(times)

    print(f"{name:20s} avg={average:.6f}s")


benchmark(
    "Python list",
    lambda: [len(v) for v in python_list],
)

benchmark(
    "NumPy object",
    lambda: np.char.str_len(numpy_object),
)

benchmark(
    "pandas object",
    lambda: pandas_series.str.len(),
)

benchmark(
    "Arrow",
    lambda: pc.utf8_length(arrow_array),
)
```

### Important caveat

The NumPy `object` example may use a different implementation path depending on the exact NumPy operation and version. That is part of the experiment.

The goal is not to force one library to win.

The goal is to understand:

- object overhead,
- native vectorized execution,
- typed memory,
- conversion costs.

---

# 83. Measuring Memory

A simple first comparison is:

```python
print("Arrow nbytes:", arrow_array.nbytes)
print("NumPy nbytes:", numpy_object.nbytes)
print("pandas memory:", pandas_series.memory_usage(deep=True))
```

For the Python list, `sys.getsizeof()` alone is not sufficient to describe all nested object memory.

A more careful experiment can use:

- `tracemalloc` for Python allocations,
- process RSS measurement,
- library-specific memory counters,
- OS tools.

### Important

Different memory metrics measure different things.

Do not compare numbers from different measurement systems as though they were the same quantity.

---

# 84. Cold vs Warm Benchmarking

Repeated benchmarks can change because:

- CPU caches become warm,
- the operating system caches files,
- one-time initialization disappears,
- JIT-like internal setup may differ,
- allocations may be reused.

For file benchmarks, record:

```text
cold run
warm run
```

where meaningful.

Run multiple repetitions.

Never report:

```text
"Arrow is 3.72x faster"
```

from one run.

Instead record the experiment.

---

# 85. A Better Benchmark Record

Capture:

```text
Dataset:
Rows:
Columns:
Data types:
Machine:
CPU:
RAM:
Python:
PyArrow:
Storage:
Warm/cold:
Repetitions:
Median:
Mean:
Peak memory:
```

A benchmark without context is weak evidence.

---

# 86. Debugging and Failure Scenarios

This section trains production troubleshooting.

---

## Failure 1 — Unexpected Type Inference

### Symptom

A column unexpectedly becomes string when you expected numeric or decimal data.

### Likely cause

Mixed input values:

```text
10
20
"unknown"
30
```

or inconsistent source files.

### Diagnosis

```python
print(table.schema)
print(table.column("amount").type)
```

Inspect sample source values.

### Fix

Define the intended schema explicitly and validate incompatible records.

### Production lesson

Schema inference is useful for exploration. Explicit schemas are stronger for controlled pipelines.

---

## Failure 2 — Null Handling Confusion

### Symptom

A transformation behaves unexpectedly when a column contains nulls.

### Likely cause

Assuming null is equivalent to:

```python
None
```

at every layer.

### Diagnosis

Check:

```python
print(column.null_count)
print(column.type)
```

Investigate the compute function's documented null behaviour.

### Fix

Test null-containing inputs explicitly.

### Production lesson

Null semantics are part of correctness.

---

## Failure 3 — Unsafe Cast

### Symptom

A type conversion succeeds but the downstream value is different.

### Likely cause

Unsafe conversion:

```python
safe=False
```

or equivalent behaviour.

### Diagnosis

Compare before and after values and verify the target type range.

### Fix

Use safe casts and explicit validation.

### Production lesson

"Conversion succeeded" does not mean "data remained correct."

---

## Failure 4 — Too Many Small Chunks

### Symptom

A table works correctly but a transformation becomes slower after repeated ingestion.

### Likely cause

The same logical column has accumulated many tiny arrays.

### Diagnosis

```python
for name in table.column_names:
    print(
        name,
        table[name].num_chunks,
    )
```

### Fix

Investigate whether `combine_chunks()` improves the measured workload.

### Production lesson

Chunk layout can matter even when row counts and values are unchanged.

---

## Failure 5 — Timezone Mismatch

### Symptom

Events appear shifted, cannot be compared correctly, or become ambiguous.

### Likely cause

Mixing:

```text
UTC-aware
```

with:

```text
naive
```

timestamps.

### Diagnosis

Inspect:

```python
print(column.type)
```

### Fix

Define a clear timestamp contract.

### Production lesson

Timezone semantics must be explicit at system boundaries.

---

## Failure 6 — Nested Schema Mismatch

### Symptom

One file has:

```text
address.city
address.zip
```

while another represents the same field differently.

### Likely cause

Schema drift.

### Diagnosis

Inspect each input schema before combining.

### Fix

Normalize schemas before unioning data.

### Production lesson

Nested schemas need the same discipline as flat schemas.

---

## Failure 7 — Unexpected Memory Growth

### Symptom

Arrow data appears small but process memory grows substantially.

### Likely causes

- Python objects still exist.
- Multiple representations coexist.
- A transformation allocated a new buffer.
- Chunk consolidation copied data.
- Another library owns memory.
- File-backed memory and process RSS are being interpreted incorrectly.

### Diagnosis

Measure more than one layer:

```python
print("Arrow allocated:", pa.total_allocated_bytes())
print("Table bytes:", table.nbytes)
```

Then use OS/process-level measurement if necessary.

### Fix

Find the boundary that creates the extra representation.

### Production lesson

Do not optimize memory based on one metric.

---

# 87. Common Mistakes

## Mistake 1 — Thinking Arrow Is a File Format

Correct model:

```text
Arrow
→ in-memory/interchange model

Parquet
→ file format
```

---

## Mistake 2 — Thinking Arrow Is a Database

Arrow stores and represents data.

It does not decide:

- which rows match,
- how joins are planned,
- how transactions are coordinated,
- how multi-user SQL sessions are managed.

Those are query/database responsibilities.

---

## Mistake 3 — Creating Many Tiny Chunks

Chunking is useful.

Fragmentation is not automatically useful.

Inspect chunk counts when performance changes.

---

## Mistake 4 — Losing Timezone Information

A timestamp without clear timezone semantics can produce subtle production errors.

Treat timestamp types as contractual.

---

## Mistake 5 — Using Unsafe Casts in Production

Unsafe casts can trade an immediate exception for silent data corruption.

Default to safe behaviour unless loss is intentionally part of the design.

---

# 88. Production Engineering Perspective

A realistic data engineering architecture can look like:

```text
API / Database
      ↓
Python ingestion
      ↓
Explicit Arrow schema
      ↓
Arrow data
      ↓
Polars / DuckDB
      ↓
Parquet
      ↓
Object Storage
```

Arrow appears at the boundary because it is a strong typed columnar representation.

## 88.1 Why an experienced Data Engineer cares

### Memory layout

Because expensive representations increase infrastructure requirements.

### Copy behaviour

Because unnecessary copies increase latency and peak memory.

### Schema fidelity

Because silently changing types creates data-quality problems.

### Null semantics

Because missing values are common in real datasets.

### Timestamp semantics

Because distributed systems operate across time zones and precision levels.

### Chunking

Because ingestion often happens in batches.

### Interoperability

Because production systems are rarely built from one library.

### Serialization overhead

Because moving bytes can cost more than transforming them.

### Data movement cost

Because architecture boundaries can dominate overall pipeline performance.

---

# 89. Example Production Data Flow

Consider an order analytics pipeline:

```text
PostgreSQL
   │
   │ extraction
   ▼
Python ingestion
   │
   │ explicit schema
   ▼
Arrow RecordBatches
   │
   ├───────────────┐
   ▼               ▼
Polars           DuckDB
   │               │
   └───────┬───────┘
           ▼
       Parquet
           ▼
      Object Store
```

The Arrow layer can reduce unnecessary conversions between compatible in-process tools.

This does not mean every path is zero-copy.

It means the architecture has a standardized typed representation at the boundaries.

---

# 90. Arrow in Larger Data Engineering Systems

Arrow also appears in ecosystems involving:

- DataFrame libraries,
- query engines,
- database connectivity,
- distributed processing,
- network data transport,
- analytics systems,
- machine learning workflows.

The same core concepts reappear:

```text
schema
buffers
batches
columnar layout
nulls
zero-copy / low-copy exchange
```

Learning them once pays off across many tools.

---

# 91. A Senior Engineer's Mental Model

When someone says:

> "This pipeline is slow."

Do not immediately say:

> "Use Arrow."

Ask:

```text
Where is data stored?
What is the in-memory representation?
How many representations exist at once?
Where are copies created?
What are the data types?
How many chunks?
How many rows?
How wide are the rows?
How many nulls?
How many nested fields?
What is the access pattern?
What does the downstream library require?
```

Then measure.

Arrow is a tool, not a magic performance switch.

---

# 92. Complete Hands-On Exercise — `arrow_basics.py`

Create:

```text
columnar_lab/
└── src/
    └── arrow_basics.py
```

The exercise should build on the previous orders example.

## Task 1 — Build the explicit schema

Required:

```text
order_id: string
customer_id: int64 (nullable)
amount: decimal128(12, 2)
created_at: timestamp("us", tz="UTC")
tags: list<string>
address: struct<city: string, zip: string>
```

## Task 2 — Construct the table

Use realistic values, including:

- at least one null `customer_id`,
- multiple tags,
- multiple cities.

## Task 3 — Inspect the schema

Print:

```python
table.schema
table.num_rows
table.nbytes
```

## Task 4 — Filter

Filter orders for a specific customer.

## Task 5 — Compute

Use `pyarrow.compute` for at least three operations.

For example:

- comparison,
- arithmetic,
- aggregation.

## Task 6 — Extract nested data

Extract:

```text
address.city
```

## Task 7 — Add `country`

Create a new column such as:

```text
country:
IN
IN
US
...
```

## Task 8 — Dictionary encode

Encode `country`:

```python
encoded = country_array.dictionary_encode()
```

Compare:

```python
country_array.nbytes
encoded.nbytes
```

## Task 9 — Arrow IPC

Write the table to an Arrow IPC file.

## Task 10 — Read the IPC file

Load it back.

## Task 11 — Memory-map

Use Arrow's IPC memory-mapped reader available in your installed version.

## Task 12 — Compare loading

Compare:

```text
CSV
vs
Arrow IPC
vs
memory-mapped Arrow IPC
```

Record actual measurements.

## Task 13 — Unsafe cast

Demonstrate a risky cast.

## Task 14 — Safe cast

Show how `safe=True` rejects the dangerous conversion.

## Task 15 — Tests

Write pytest tests for:

- schema,
- row count,
- null count,
- key values,
- output types.

---

# 93. Suggested Incremental Implementation

Do not write the entire lab in one giant script.

### Stage A

```python
schema = ...
table = ...
```

### Stage B

```python
print(table.schema)
print(table.num_rows)
print(table.nbytes)
```

### Stage C

```python
mask = ...
filtered = table.filter(mask)
```

### Stage D

```python
result = ...
```

### Stage E

```python
country = ...
encoded_country = ...
```

### Stage F

```python
write IPC
read IPC
memory-map IPC
```

### Stage G

```text
tests
benchmarks
```

This sequence makes debugging much easier.

---

# 94. Pytest Validation Example

Create:

```text
tests/test_arrow_basics.py
```

Example:

```python
import pyarrow as pa


def test_orders_schema():
    schema = pa.schema([
        pa.field("order_id", pa.string()),
        pa.field("customer_id", pa.int64()),
        pa.field("amount", pa.decimal128(12, 2)),
    ])

    assert schema.field("order_id").type == pa.string()
    assert schema.field("customer_id").type == pa.int64()
    assert schema.field("amount").type == pa.decimal128(12, 2)
```

A stronger test can build the table and assert:

```python
assert table.schema == expected_schema
assert table.num_rows == expected_rows
```

### Production lesson

Test the schema, not only the values.

---

# 95. Schema Assertion Checklist

For each pipeline boundary, consider asserting:

```text
Column names
Column order where significant
Data types
Nullable semantics
Timezone
Decimal precision/scale
Nested field structure
Row count where meaningful
```

This turns Arrow from merely a performance tool into part of a correctness contract.

---

# 96. Interop Experiment

Create a conversion matrix.

Test pairs such as:

```text
Arrow → Polars
Polars → Arrow

Arrow → pandas
pandas → Arrow

DuckDB → Arrow
Arrow → DuckDB
```

For each path record:

```text
input type
output type
row count
schema
time
peak memory
copy likely?
type changes?
```

Use a mixed dataset with:

- integers,
- floats,
- strings,
- nulls,
- timestamps,
- timezone,
- decimals,
- nested list.

---

# 97. Zero-Copy Investigation Questions

For every conversion ask:

1. Can the target consume the same physical buffers?
2. Are the types compatible?
3. Are the null semantics compatible?
4. Do timestamps have the same unit?
5. Do timezones match?
6. Are nested structures supported equivalently?
7. Do chunks need consolidation?
8. Does the target own or merely borrow the memory?
9. Does the operation create a materialized result?

The answers determine whether the boundary is:

```text
zero-copy
low-copy
full-copy
```

---

# 98. Production Design Rule: Keep One Representation as Long as Possible

Bad:

```text
read
 ↓
pandas
 ↓
Arrow
 ↓
pandas
 ↓
Arrow
 ↓
Polars
 ↓
pandas
```

Better:

```text
read
 ↓
Arrow-compatible processing
 ↓
Polars / DuckDB
 ↓
small final DataFrame only where necessary
```

This is one of the highest-value practical lessons in this chapter.

---

# 99. Architectural Boundary Mapping

When designing a pipeline, draw the boundaries explicitly:

```text
System A
   │
   │ representation A
   ▼
[conversion]
   │
   │ representation B
   ▼
System B
```

Then ask:

```text
Can Arrow replace the conversion?
```

Sometimes the answer is yes.

Sometimes it is no because:

- the target format differs,
- a semantic transformation is required,
- the type has no direct equivalent,
- the consumer requires Python objects,
- data must be serialized for transport.

---

# 100. Interview Preparation — Beginner to Senior

## Beginner Questions

### 1. What is Apache Arrow?

Apache Arrow is a language-independent specification and ecosystem for representing structured data in memory using a standardized columnar format. It is designed especially for efficient analytical processing and interoperability between systems.

### 2. What is PyArrow?

PyArrow is the Python implementation/bindings that let Python applications work with Apache Arrow data types, arrays, tables, compute functions, IPC, and related functionality.

### 3. Is Arrow a database?

No. Arrow is a data representation/interchange technology, not a database.

### 4. Is Arrow the same as Parquet?

No. Arrow is primarily an in-memory representation and interoperability model; Parquet is an on-disk columnar file format.

### 5. Why is Arrow columnar?

Columnar layout groups values from the same column together, which matches many analytical workloads and can enable efficient scanning, vectorization, cache use, and selective processing of columns.

---

# 101. Intermediate Interview Questions

## 6. What is an Arrow `Array`?

A typed sequence of Arrow values.

## 7. What is a `ChunkedArray`?

A logical column composed of one or more Arrow arrays called chunks.

## 8. What is a `RecordBatch`?

A set of equal-length Arrow arrays representing one batch of records with a schema.

## 9. What is a `Table`?

A structured collection of named columns with a schema. Its columns are commonly represented as `ChunkedArray` objects.

## 10. What is a schema?

The structured description of field names and their data types, optionally with metadata.

## 11. Why does Arrow use a validity bitmap?

To represent nullability efficiently using bit-level validity information rather than requiring a Python object or full-byte flag for every value.

## 12. Why do strings need offsets?

Because string values can have different lengths. Offsets identify where each value begins and ends in the shared data buffer.

## 13. Why are nested types still considered columnar?

Because nested structures are represented using child arrays and structural buffers such as offsets rather than requiring every row to become an opaque Python object.

---

# 102. Senior-Level Interview Questions

## 14. Why can `combine_chunks()` be expensive?

Because consolidating chunks may require allocating new buffers and copying data. It should be justified by the downstream access pattern rather than done automatically.

## 15. What does zero-copy actually mean?

It means the consumer can use the existing underlying memory buffers without copying the values into a new physical representation.

## 16. Give cases where zero-copy can fail.

Examples include:

- incompatible types,
- required type conversion,
- different timestamp units/timezones,
- unsupported nested mappings,
- creation of new validity state,
- chunk consolidation,
- consumers requiring a different memory layout.

## 17. Why can many small chunks hurt performance?

Each chunk introduces structural overhead, and operations may have to manage many arrays. Excessive fragmentation can hurt throughput and cache behaviour.

## 18. Why are Arrow dtypes important?

Because they make the logical and physical schema explicit and consistent across systems, reducing ambiguity during interoperability.

## 19. Why is an unsafe cast dangerous?

Because the target type may not represent the source value safely, potentially causing truncation or information loss instead of failing fast.

## 20. What would you inspect if Arrow memory suddenly grew?

I would inspect:

- table `nbytes`,
- `pa.total_allocated_bytes()`,
- process RSS,
- number and size of chunks,
- whether conversions created additional representations,
- whether a transformation materialized new buffers,
- whether Python objects remain alive,
- nested/string payload sizes.

## 21. Why does Arrow help Polars and DuckDB interoperate?

Because both ecosystems can work with Arrow-style columnar data and Arrow interchange mechanisms, allowing data to move between them with less custom conversion and, in compatible cases, little or no copying.

---

# 103. Senior Architecture Questions

## 22. Would you put Arrow between every component?

No. Arrow is a useful interoperability representation, but excessive conversions are still undesirable. The goal is to minimize unnecessary boundaries, not maximize the number of Arrow conversions.

## 23. When would you use Arrow rather than pandas?

When typed columnar memory representation, interoperability, lower-level memory control, or high-throughput native computation matters.

Pandas may still be the correct choice when:

- ecosystem compatibility dominates,
- the dataset is manageable,
- the consumer is pandas-specific,
- convenience is the main requirement.

## 24. When would you use Parquet instead of Arrow IPC?

For durable analytical storage, especially in lake/object-storage architectures, where Parquet's storage-oriented features are valuable.

## 25. How would you investigate whether an Arrow optimization is real?

I would define a representative workload and measure:

```text
wall time
peak memory
data size
number of rows
data types
warm/cold state
repetitions
machine
library versions
```

Then compare alternatives under the same conditions.

---

# 104. Explain-Aloud Exercises

You should be able to explain each prompt without notes.

## Exercise 1

> Explain Arrow to a beginner in 30 seconds.

A strong explanation should include:

```text
standardized
columnar
in-memory
interoperability
```

## Exercise 2

> Explain how Arrow stores `["cat", null, "dog"]`.

Your explanation should cover:

```text
validity
offsets
data bytes
```

## Exercise 3

> Explain Arrow versus Parquet in 30 seconds.

## Exercise 4

> Explain why a table column can be a `ChunkedArray`.

## Exercise 5

> Explain zero-copy.

## Exercise 6

> Explain why unsafe casts are dangerous.

## Exercise 7

> Explain why Arrow matters for Polars and DuckDB.

---

# 105. Practice Checklist

Use this as the exit checklist for Topic 01.

- [ ] I can explain what Apache Arrow is.
- [ ] I can explain what PyArrow is.
- [ ] I can explain why Arrow exists.
- [ ] I can explain row-oriented vs columnar thinking.
- [ ] I can distinguish Arrow from Parquet.
- [ ] I can distinguish Arrow from a query engine/database.
- [ ] I can explain `DataType`.
- [ ] I can explain `Field`.
- [ ] I can explain `Schema`.
- [ ] I can explain `Array`.
- [ ] I can explain `ChunkedArray`.
- [ ] I can explain `RecordBatch`.
- [ ] I can explain `Table`.
- [ ] I can create Arrow data from Python lists.
- [ ] I can create Arrow data from dictionaries.
- [ ] I can convert compatible NumPy data.
- [ ] I can convert pandas data.
- [ ] I can inspect `schema`.
- [ ] I can inspect `num_rows`.
- [ ] I can inspect `nbytes`.
- [ ] I can explain the validity bitmap.
- [ ] I can explain offsets.
- [ ] I can explain the data buffer.
- [ ] I can explain fixed-width vs variable-width data.
- [ ] I understand nullable Arrow types.
- [ ] I understand numeric types.
- [ ] I understand `decimal128`.
- [ ] I understand timestamps and timezones.
- [ ] I understand durations.
- [ ] I understand strings and binary types.
- [ ] I can represent list data.
- [ ] I can represent struct data.
- [ ] I understand map data conceptually.
- [ ] I understand dictionary encoding.
- [ ] I understand its trade-offs.
- [ ] I understand run-end encoding conceptually.
- [ ] I can use `pyarrow.compute`.
- [ ] I understand why Python loops can be an expensive boundary.
- [ ] I understand chunking.
- [ ] I can inspect chunk counts.
- [ ] I understand `combine_chunks()`.
- [ ] I understand why chunk size matters.
- [ ] I understand immutability.
- [ ] I understand zero-copy slicing.
- [ ] I understand that zero-copy is not guaranteed.
- [ ] I can use Arrow memory allocation metrics.
- [ ] I understand the limits of those metrics.
- [ ] I understand Arrow IPC.
- [ ] I understand Arrow IPC streaming vs file representations.
- [ ] I understand Feather v2.
- [ ] I understand Feather vs Parquet.
- [ ] I understand memory mapping.
- [ ] I can explain why memory mapping can be fast.
- [ ] I understand schema metadata.
- [ ] I understand safe vs unsafe casting.
- [ ] I can explain Arrow interoperability.
- [ ] I understand the Arrow C Data Interface at awareness level.
- [ ] I understand Arrow Flight at awareness level.
- [ ] I understand ADBC at awareness level.
- [ ] I completed the Arrow orders-table exercise.
- [ ] I inspected real buffers.
- [ ] I completed the dictionary-encoding experiment.
- [ ] I completed the performance lab.
- [ ] I completed the debugging exercises.
- [ ] I can explain Arrow architecture aloud.

---

# 106. Final Mastery Test

Do not look at the answer key until you have attempted every question.

---

## Part A — Fundamentals

### A1

What problem does Apache Arrow solve?

### A2

What is the difference between Apache Arrow and PyArrow?

### A3

Why is columnar layout particularly useful for analytical workloads?

### A4

Arrow versus Parquet: what is the architectural difference?

### A5

Arrow versus DuckDB: what layer does each belong to?

### A6

What is an `Array`?

### A7

What is a `ChunkedArray`?

### A8

What is a `RecordBatch`?

### A9

What is a `Table`?

### A10

What is a schema?

---

## Part B — Internal Memory Model

### B1

Explain the validity bitmap.

### B2

How many logical validity flags can one byte represent?

### B3

Why do variable-length strings need offsets?

### B4

Explain the relationship between offsets and the data buffer.

### B5

For:

```text
["cat", "dog", "apple"]
```

what conceptual offsets identify the three values?

### B6

Why does a fixed-width integer column not need string-style offsets?

### B7

How can nested list data remain columnar?

### B8

Why can dictionary encoding save memory?

### B9

Why can dictionary encoding be worse for nearly unique values?

### B10

Why can an Arrow slice be cheap?

---

## Part C — Python / PyArrow Practical Tasks

### C1

Create an Arrow array of nullable `int64`.

### C2

Create a string array and inspect its buffers.

### C3

Create an explicit schema for an orders table.

### C4

Build the orders table from Python data.

### C5

Print schema, row count, and memory size.

### C6

Use a compute kernel to filter rows.

### C7

Use a compute kernel to calculate a result.

### C8

Dictionary-encode a repeated string column.

### C9

Write and read an Arrow IPC file.

### C10

Demonstrate safe and unsafe casting.

---

## Part D — Performance Investigation

### D1

Design an experiment comparing Python list strings with Arrow strings.

### D2

Measure Arrow allocator bytes before and after allocation.

### D3

Measure `table.nbytes`.

### D4

Create a table with multiple chunks and investigate consolidation.

### D5

Measure the time and memory impact of an unnecessary Arrow → pandas → Arrow round trip.

---

## Part E — Production / Architecture

### E1

Your ingestion API sometimes sends an integer ID as a string. How would you design schema handling?

### E2

A timestamp column is correct in one environment and shifted in another. What would you inspect?

### E3

A pipeline's row count is stable but memory doubled. What would you investigate?

### E4

A team wants to convert a 500 GB Arrow-compatible dataset into pandas because "pandas is easier." What engineering questions should you ask before agreeing?

### E5

A downstream service can consume Arrow directly. How might that change the architecture compared with serializing each row into generic JSON-like Python objects?

---

# 107. Mastery Test — Answer Key

## A1 Answer

Arrow standardizes how typed columnar data can be represented in memory and exchanged efficiently between systems. Its value is strongest at analytical and interoperability boundaries.

## A2 Answer

Apache Arrow is the broader specification/ecosystem. PyArrow is the Python implementation/bindings used to create and manipulate Arrow data in Python.

## A3 Answer

Columnar layout groups values by column, which aligns well with analytical scans, vectorized operations, cache locality, selective column processing, and many compression strategies.

## A4 Answer

Arrow primarily defines an in-memory/interchange representation. Parquet is a disk-oriented columnar file format designed for durable analytical storage.

## A5 Answer

Arrow is a data representation/interchange layer. DuckDB is an analytical query engine/database.

## A6 Answer

A typed sequence of Arrow values.

## A7 Answer

A logical column composed of one or more Arrow arrays called chunks.

## A8 Answer

A batch of equal-length columns represented as Arrow arrays plus a schema.

## A9 Answer

A structured table of named columns with a schema, with columns represented as `ChunkedArray` objects.

## A10 Answer

A schema defines the fields and data types of a structured dataset and can also carry metadata.

---

## B1 Answer

A validity bitmap stores one validity bit per logical value, indicating whether the value is valid or null.

## B2 Answer

Conceptually, one byte contains eight bits, so it can represent eight validity flags.

## B3 Answer

Strings have different lengths, so Arrow needs offsets to determine where each value begins and ends in the underlying data buffer.

## B4 Answer

For a value at position `i`, the logical bytes are identified using the boundaries between consecutive offsets.

## B5 Answer

The conceptual offsets are:

```text
0, 3, 6, 11
```

for:

```text
cat
dog
apple
```

## B6 Answer

Each fixed-width value occupies a predictable number of bytes, so separate per-value offsets are unnecessary.

## B7 Answer

Nested arrays use child arrays plus structural buffers such as offsets and validity. The nested values remain typed Arrow data rather than becoming opaque row-level Python objects.

## B8 Answer

Repeated values can be stored once in a dictionary while the column stores compact indices referring to dictionary entries.

## B9 Answer

A dictionary has overhead. If most values are unique, the dictionary and indices may not save enough space to offset that overhead.

## B10 Answer

A slice may reference existing buffers with a changed logical offset and length rather than eagerly copying the selected values.

---

## C1 Example

```python
import pyarrow as pa

arr = pa.array(
    [10, None, 30],
    type=pa.int64(),
)

print(arr)
```

## C2 Example

```python
import pyarrow as pa

arr = pa.array(
    ["cat", None, "dog"],
    type=pa.string(),
)

print(arr.buffers())
```

## C3 Example

```python
import pyarrow as pa

schema = pa.schema([
    pa.field("order_id", pa.string()),
    pa.field("customer_id", pa.int64()),
    pa.field("amount", pa.decimal128(12, 2)),
])
```

## C4 Example

Build the table using `pa.Table.from_pydict(..., schema=schema)`.

## C5 Example

```python
print(table.schema)
print(table.num_rows)
print(table.nbytes)
```

## C6 Example

```python
import pyarrow.compute as pc

mask = pc.equal(table["customer_id"], 101)
filtered = table.filter(mask)
```

## C7 Example

Use a compute function such as:

```python
result = pc.add(values, 5)
```

or another appropriate Arrow kernel.

## C8 Example

```python
encoded = country_array.dictionary_encode()
```

## C9 Example

Write using Arrow IPC file writer and read with an IPC file reader. The exact implementation should match the PyArrow version installed.

## C10 Example

Use:

```python
pc.cast(values, pa.int32(), safe=True)
```

for a safe conversion and deliberately test `safe=False` with an out-of-range value.

---

## D1 Answer

Use the same string values and row count. Measure the memory footprint using appropriate tools and measure a common operation such as string length. Record environment details and repeat the benchmark.

## D2 Answer

Record:

```python
before = pa.total_allocated_bytes()
```

allocate data, then:

```python
after = pa.total_allocated_bytes()
```

and compare the difference.

## D3 Answer

Use:

```python
table.nbytes
```

while recognizing that this is not a complete process-level memory measurement.

## D4 Answer

Inspect:

```python
table[column].num_chunks
```

then compare the workload before and after:

```python
combined = table.combine_chunks()
```

Measure memory and execution time rather than assuming consolidation is beneficial.

## D5 Answer

Perform the round trip under identical data and benchmark:

```text
Arrow input
→ pandas
→ Arrow
```

against staying in Arrow.

Record time, memory, and schema fidelity.

---

# 108. Production Scenario Answer Key

## E1 Answer

Define the intended schema explicitly. Validate or cast source values according to a clear policy. Prefer safe casts. Quarantine records that cannot satisfy the contract rather than silently changing their meaning.

## E2 Answer

Inspect:

- Arrow timestamp type,
- timezone,
- unit,
- source encoding,
- parsing logic,
- downstream conversion semantics.

Look for a naive/aware mismatch or unit conversion.

## E3 Answer

Inspect:

- Arrow allocation,
- table `nbytes`,
- process RSS,
- Python object retention,
- copies during conversions,
- chunk consolidation,
- nested/string columns,
- materialized transformations.

## E4 Answer

Ask:

- Does the full dataset fit comfortably in memory?
- What is the peak-memory budget?
- What does pandas add in overhead?
- Is there a pandas-only dependency?
- Can Polars/DuckDB operate directly on the data?
- What conversion cost would be introduced?
- Could the operation stay Arrow-native?

## E5 Answer

A direct Arrow-capable transport can reduce repeated row-object serialization and make the producer/consumer boundary more columnar and typed. The design still needs authentication, compatibility, backpressure, failure handling, and transport-level guarantees.

---

# 109. Final Review — The Mental Model You Should Keep

At the end of Topic 01, you should be able to picture this:

```text
                        ARROW
                          │
              ┌───────────┴───────────┐
              │                       │
           Schema                  Data
              │                       │
       ┌──────┼──────┐       ┌───────┴─────────┐
       ▼      ▼      ▼       ▼        ▼        ▼
     Field  Field  Field   Array   ChunkedArray Table
       │                       │
   DataType                 Buffers
                               │
                    ┌──────────┼──────────┐
                    ▼          ▼          ▼
                Validity    Offsets      Data
                 bitmap                  buffer
```

And for interoperability:

```text
Parquet / Database / Python source
              ↓
       Arrow representation
              ↓
      ┌───────┼────────┐
      ▼       ▼        ▼
   Polars   DuckDB   pandas
      │       │        │
      └───────┼────────┘
              ▼
        Arrow / output
```

The core engineering questions are:

```text
What is the schema?
What are the types?
How are nulls represented?
How are variable-length values represented?
How many chunks exist?
Are operations creating copies?
Can buffers be shared?
How much memory is allocated?
How much data actually needs to move?
What does the next system require?
```

---

# 110. Transition to Topic 02

You should now be ready to study:

**02 — Polars Expressions and Contexts**

The bridge is:

```text
Arrow
  ↓
standardized typed columnar memory
  ↓
Polars
  ↓
expressions and contexts
```

You do not need to master Polars yet.

You only need the architectural insight that Polars can operate on a modern columnar representation rather than the Python-object-centric mental model that often dominates beginner DataFrame work.

---

# 111. What a Senior Data Engineer Should Remember

If you remember only ten things from this chapter, remember these:

1. **Arrow is a standardized columnar in-memory representation and interoperability ecosystem.**
2. **PyArrow is the Python implementation/bindings.**
3. **Arrow is not Parquet.**
4. **Arrow is not a database or query engine.**
5. **A nullable variable-length array can be understood through validity, offsets, and data buffers.**
6. **Not every Arrow type needs all of those buffers.**
7. **A table column can be a `ChunkedArray`, not necessarily one contiguous `Array`.**
8. **Zero-copy is possible in suitable cases, not guaranteed everywhere.**
9. **A successful cast is not necessarily a safe or semantically correct cast.**
10. **Measure data movement, memory, and type conversions instead of assuming a library is faster.**

---

# 112. Topic 01 Exit Criteria

Do not move on because you have read the chapter.

Move on when you can demonstrate the following without looking at notes:

```text
[ ] Explain Arrow from first principles.
[ ] Explain Arrow vs Parquet.
[ ] Explain Arrow vs a database/query engine.
[ ] Build a typed Arrow table.
[ ] Inspect a schema.
[ ] Explain validity bitmaps.
[ ] Explain string offsets.
[ ] Inspect real buffers.
[ ] Represent nested list/struct data.
[ ] Use Arrow compute.
[ ] Explain dictionary encoding.
[ ] Explain run-end encoding conceptually.
[ ] Explain ChunkedArray.
[ ] Measure chunk counts.
[ ] Explain combine_chunks trade-offs.
[ ] Explain immutability.
[ ] Explain zero-copy slicing.
[ ] Measure Arrow allocator usage.
[ ] Explain IPC.
[ ] Explain Feather v2.
[ ] Explain memory mapping.
[ ] Use schema metadata.
[ ] Demonstrate safe/unsafe casts.
[ ] Explain Arrow interoperability.
[ ] Explain C Data Interface at awareness level.
[ ] Explain Arrow Flight at awareness level.
[ ] Explain ADBC at awareness level.
[ ] Complete arrow_basics.py.
[ ] Complete the performance lab.
[ ] Complete debugging scenarios.
[ ] Complete the mastery test.
[ ] Explain the entire Arrow memory model aloud.
```

---

# 113. Final Production Reflection

Before leaving this topic, answer these questions in writing:

### Reflection 1

Where in your future data pipelines might an unnecessary copy occur?

### Reflection 2

Which data types are most likely to create interoperability problems?

### Reflection 3

What would you inspect first if a DataFrame pipeline used twice as much memory after adding one conversion step?

### Reflection 4

Why is a shared columnar representation valuable even when a pipeline eventually uses Parquet on disk?

### Reflection 5

Why should a senior Data Engineer care about memory layout instead of leaving it entirely to a library?

A strong answer to the last question is:

> Because system performance is determined not only by business logic but also by how much data must move, how it is represented, how often it is copied, and how efficiently the hardware and software can operate on that representation.

That is the foundation this topic is intended to build.
