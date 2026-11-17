# Row-Oriented vs Columnar Storage

> **Stage 2 → Python for Data Engineering → Module 2.5 — Data Formats, Compression, and File Layout**
>
> **Topic 01 — Row-oriented vs Columnar Storage**

This topic establishes the physical-storage mental model used throughout the rest of Module 2.5.

The central question is not:

> **"Which format is better?"**

The better question is:

> **"What physical arrangement of bytes best fits this workload?"**

A row-oriented layout keeps the fields of a record physically close to one another. A column-oriented layout keeps values from the same column close to one another. Neither arrangement is universally better. Each creates different I/O, CPU, compression, write, and parallel-processing behavior.

Later topics will go deeper into Parquet internals, PyArrow writing, Avro, ORC, nested data, compression codecs, partitioning, and file sizing. This topic gives you the physical intuition needed to understand those topics rather than memorizing format-specific rules.

---

## Learning Objectives

By the end of this topic, you should be able to:

- explain what row-oriented storage is;
- explain what columnar storage is;
- describe how data is physically organized in both layouts;
- connect physical organization to I/O, CPU work, parsing, compression, and query performance;
- identify workloads that naturally fit row-oriented storage;
- identify workloads that naturally fit columnar storage;
- explain why "columnar is better" is not a valid universal rule;
- explain why columnar storage often creates better compression opportunities;
- distinguish encoding from compression at a foundational level;
- explain column pruning;
- explain predicate skipping using block-level min/max statistics;
- explain why columnar systems can avoid unnecessary reads;
- explain the write-side costs of columnar storage;
- explain why frequent record-at-a-time appends and updates can be a poor fit for columnar files;
- distinguish text and binary formats in terms of typing, precision, parsing cost, and readability;
- explain PAX and hybrid layouts;
- explain the conceptual relationship between PAX, Parquet row groups, and ORC stripes;
- explain self-describing files versus external/schema-managed files;
- define splittability and explain why it matters for parallel processing;
- identify where row-oriented and columnar representations commonly appear in a data pipeline;
- make a workload-based layout decision and defend that decision in a production architecture discussion.

---

## Prerequisites

You should already have a basic understanding of:

- bytes and storage;
- files and directories;
- RAM versus persistent storage;
- basic CSV and JSON / JSON Lines;
- the difference between OLTP and OLAP at a high level.

You should also be comfortable with basic Python and the idea of a table containing rows and columns.

This topic does **not** re-teach the earlier modules. It uses those concepts to reason about what happens to data physically.

---

# 1. Start With the Physical-Storage Mental Model

Before discussing CSV, Parquet, Avro, or ORC, ignore the format names for a moment.

Imagine this logical table:

| order_id | customer | country | amount |
| ---: | --- | --- | ---: |
| 1 | Alice | IN | 100 |
| 2 | Bob | US | 250 |
| 3 | Carol | IN | 180 |
| 4 | David | UK | 120 |
| 5 | Eve | IN | 300 |
| 6 | Frank | US | 220 |

Logically, this is one table.

Physically, the same logical information can be arranged in different ways.

## 1.1 Row-oriented representation

Conceptually:

```text
1, Alice, IN, 100
2, Bob,   US, 250
3, Carol, IN, 180
4, David, UK, 120
5, Eve,   IN, 300
6, Frank, US, 220
```

Think:

```text
ROW 1 → all fields for order 1
ROW 2 → all fields for order 2
ROW 3 → all fields for order 3
...
```

The fields belonging to the same record are kept close together.

## 1.2 Column-oriented representation

Conceptually:

```text
order_id: 1, 2, 3, 4, 5, 6
customer: Alice, Bob, Carol, David, Eve, Frank
country:  IN, US, IN, UK, IN, US
amount:   100, 250, 180, 120, 300, 220
```

Think:

```text
COLUMN order_id → values for many rows
COLUMN customer → values for many rows
COLUMN country  → values for many rows
COLUMN amount   → values for many rows
```

The values belonging to the same column are kept close together.

## 1.3 PAX / hybrid representation

A hybrid arrangement groups rows into blocks and then organizes each column inside each block.

Conceptually:

```text
Block 1
  rows 1–3

  order_id: 1, 2, 3
  customer: Alice, Bob, Carol
  country:  IN, US, IN
  amount:   100, 250, 180

Block 2
  rows 4–6

  order_id: 4, 5, 6
  customer: David, Eve, Frank
  country:  UK, IN, US
  amount:   120, 300, 220
```

This is a conceptual physical-layout model, not a byte-for-byte specification of every format.

The important idea is:

> **A logical table does not determine one unique physical layout.**

That choice changes what a reader has to touch.

---

# 2. Why Storage Layout Matters

A table in a data model is logical.

Storage is physical.

Suppose a dataset contains:

- 1 billion rows;
- 20 columns;
- a query needs only 2 columns.

The logical question is:

> "What result should the query return?"

The physical question is:

> "Which bytes must the system actually read, move, parse, decompress, and process to produce that result?"

That second question is where storage layout matters.

## 2.1 A conceptual I/O example

Assume, purely for illustration, that the 20 columns contribute roughly the same amount of physical data.

A row-oriented representation conceptually places:

```text
row 1: c1 c2 c3 ... c20
row 2: c1 c2 c3 ... c20
...
```

If a query needs only `c5` and `c17`, the needed values are mixed with the other 18 columns.

A columnar representation conceptually places:

```text
c1:  all c1 values
c2:  all c2 values
...
c5:  all c5 values
...
c17: all c17 values
...
c20: all c20 values
```

Now a reader can potentially focus on the physical regions for `c5` and `c17`.

The exact amount of data read depends on the format, engine, compression, metadata, block structure, execution path, and query. The important lesson is not an exact multiplier.

The lesson is:

> **Physical organization controls how much unnecessary data a query may have to touch.**

## 2.2 I/O amplification

**I/O amplification** means the system reads or moves more physical data than the logical result actually requires.

For example:

```text
Logical request:
  "Calculate SUM(amount)"

Potentially useful values:
  amount

Potentially unnecessary values:
  order_id
  customer
  country
  address
  device
  campaign
  ...
```

A good analytical layout can reduce unnecessary reads.

Reducing unnecessary reads can reduce:

- storage I/O;
- object-storage bytes transferred;
- network traffic;
- decompression work;
- memory pressure;
- downstream CPU work.

## 2.3 CPU cost also matters

Storage layout is not only about disk or object storage.

Reading a text value may require parsing:

```text
"12345"
```

into a typed integer.

A binary typed representation may already encode the value in a form the reader can interpret more directly.

Similarly, compressed data must be decompressed before it can be processed.

So an analytical query can involve:

```text
Storage
   ↓
Read bytes
   ↓
Transfer bytes
   ↓
Decompress
   ↓
Decode / parse
   ↓
Convert to in-memory representation
   ↓
Execute computation
```

A physical layout can affect several stages in this pipeline.

## 2.4 Storage cost

For large datasets, physical layout can also affect storage volume.

That matters because the same data may be:

- stored for months or years;
- copied between environments;
- replicated;
- transferred over a network;
- queried repeatedly.

On cloud object storage, bytes and object operations can also have cost implications.

Therefore, a storage-format decision is not merely a file-format preference. It can become a recurring operational decision.

## 2.5 The same logical dataset can behave differently

Imagine two datasets containing exactly the same business facts.

Dataset A:

```text
many row-oriented records
```

Dataset B:

```text
columnar blocks
```

A query asking for:

```text
country, SUM(amount)
```

may have very different physical work on the two layouts.

A query asking for:

```text
one complete order by order_id
```

may have a different access pattern.

This is why Data Engineers should reason about **workloads**, not slogans.

---

# 3. What Is Row-Oriented Storage?

## 3.1 The basic idea

**Row-oriented storage** stores the fields belonging to a record close together.

A useful mental model is:

```text
Record 1
  field A
  field B
  field C
  field D

Record 2
  field A
  field B
  field C
  field D

Record 3
  field A
  field B
  field C
  field D
```

In simpler terms:

> **One record is the main unit of physical locality.**

The exact low-level representation differs across technologies, but the access pattern is the important concept.

## 3.2 Key terminology

### Row

A **row** is one record in a table.

Example:

```text
1, Alice, IN, 100
```

### Record

"Record" is often used as a synonym for a row when discussing record-oriented systems.

### Field

A **field** is one attribute of the record.

For example:

```text
customer = Alice
```

is one field.

### Record-at-a-time access

Record-at-a-time means the system naturally wants to consume or modify complete records.

Examples:

```text
read order 12345
insert one transaction
update one customer record
publish one event
```

The physical layout matches this style of work naturally.

---

## 3.3 Conceptual byte layout

Imagine each value has a fixed conceptual width:

```text
Row 1:
[order_id][customer][country][amount]

Row 2:
[order_id][customer][country][amount]

Row 3:
[order_id][customer][country][amount]
```

This is useful when an operation wants most or all of a row.

The system does not need to reconstruct a complete record by gathering values from many separate column regions.

Again, this is a conceptual model. Real systems may add pages, indexes, headers, padding, variable-width fields, compression, and other structures.

---

# 4. Why Row-Oriented Storage Is Useful

Row-oriented storage naturally fits workloads such as:

### 4.1 Reading complete records

Suppose an application needs:

```text
order_id = 1009281
```

and wants:

```text
order_id
customer
shipping_address
payment_status
order_total
created_at
...
```

The application needs a broad set of fields for one or a few records.

A row-oriented physical arrangement is naturally aligned with that access pattern.

### 4.2 Writing complete records

Suppose a transaction system receives:

```text
one order
one payment
one customer update
```

at a time.

The application may want the record to become durable without waiting for a large analytical batch.

A record-oriented representation is a natural fit for this kind of write pattern.

### 4.3 Transaction-oriented applications

Operational systems often care about:

- individual transactions;
- point reads;
- small targeted updates;
- complete records.

This is one reason row-oriented physical organization appears in many OLTP-oriented storage systems.

### 4.4 Point lookups

A point lookup is a request for a small number of specific records.

Examples:

```text
find customer 8127
find order 392018
find payment transaction 7f...
```

A row-oriented representation can align well with this access pattern, although indexing and other physical structures also determine performance.

---

# 5. Representative Row-Oriented Formats and Systems

The following are representative examples from the roadmap:

- CSV
- JSON Lines
- Avro
- many OLTP database page designs

These examples should not be interpreted as saying every implementation of the format has identical physical behavior.

## CSV

CSV is text and logically represents records separated by delimiters.

Example:

```text
1,Alice,IN,100
2,Bob,US,250
3,Carol,IN,180
```

The records appear row-by-row.

CSV is therefore easy to reason about as a record-oriented text representation.

## JSON Lines

JSON Lines commonly stores one JSON object per line:

```json
{"order_id":1,"customer":"Alice","country":"IN","amount":100}
{"order_id":2,"customer":"Bob","country":"US","amount":250}
{"order_id":3,"customer":"Carol","country":"IN","amount":180}
```

Each line is a complete logical record.

## Avro

Avro is a binary row format with an embedded JSON schema.

It is commonly encountered in ingestion, change-data-capture, and messaging-oriented data flows.

Its record-oriented design is important enough that Module 2.5 Topic 04 studies it separately.

## OLTP database pages

Many transaction-oriented database storage engines organize physical pages around records or tuples.

The exact layout varies significantly across database engines, so use this as a physical-design category rather than as a single implementation rule.

---

# 6. What Is Column-Oriented Storage?

## 6.1 The basic idea

**Columnar storage** stores values from the same column together.

A useful mental model is:

```text
Column A:
  A1
  A2
  A3
  A4
  A5

Column B:
  B1
  B2
  B3
  B4
  B5

Column C:
  C1
  C2
  C3
  C4
  C5
```

The key idea is:

> **One column is the main unit of physical locality.**

This is especially useful when a workload scans many rows but needs only some columns.

---

# 7. Why Columnar Storage Is Useful for Analytics

Analytical queries commonly look like:

```sql
SELECT country, SUM(amount)
FROM orders
GROUP BY country;
```

The query needs:

```text
country
amount
```

It does not need every attribute of the order.

A columnar layout can keep those values physically separated from unrelated columns.

This creates an opportunity to avoid unnecessary work.

## 7.1 Large scans over a few columns

Consider:

```text
1 billion rows
20 columns
query needs 2 columns
```

An analytical engine can potentially process:

```text
column 5
column 17
```

without reading all 20 columns.

The exact bytes read depend on the implementation, but the physical arrangement gives the engine the opportunity.

## 7.2 Aggregations

Columnar layouts fit operations such as:

```text
SUM
AVG
MIN
MAX
COUNT
GROUP BY
```

over very large numbers of rows, especially when the query references a relatively small subset of columns.

## 7.3 Reporting

Reports often ask for:

```text
sales by country
sales by month
average order amount
conversion by campaign
```

The query may touch billions of values in a few columns rather than needing complete records.

## 7.4 Batch transformations

Large data transformations frequently involve:

```text
read selected columns
filter
join
aggregate
write result
```

Columnar storage can align naturally with this scan-and-transform pattern.

---

# 8. Arrow Is Columnar, But It Is Not the Same Kind of Thing as Parquet

A foundational distinction is important.

### Apache Arrow

Arrow is primarily a **columnar in-memory representation and interoperability model**.

Conceptually:

```text
Python / pandas / Polars / another system
              ↓
       Arrow memory model
              ↓
      computational work
```

### Parquet and ORC

Parquet and ORC are **on-disk columnar file formats**.

Conceptually:

```text
Object storage / filesystem
              ↓
        Parquet / ORC
              ↓
    read selected columns
              ↓
      Arrow-like memory
              ↓
      analytical engine
```

This means "columnar" is a broader physical-storage idea.

A file format and an in-memory representation can both be columnar without being the same technology.

Module 2.4 covered Arrow's memory model. Module 2.5 now focuses on the on-disk side.

---

# 9. Row vs Column: The Physical Difference

Start with the same logical table:

```text
order_id | customer | country | amount
---------+----------+---------+-------
1        | Alice    | IN      | 100
2        | Bob      | US      | 250
3        | Carol    | IN      | 180
4        | David    | UK      | 120
```

## Row-oriented

```text
R1: [1][Alice][IN][100]
R2: [2][Bob][US][250]
R3: [3][Carol][IN][180]
R4: [4][David][UK][120]
```

## Column-oriented

```text
order_id: [1][2][3][4]
customer: [Alice][Bob][Carol][David]
country:  [IN][US][IN][UK]
amount:   [100][250][180][120]
```

The difference is not the logical table.

The difference is:

> **Which values are physically adjacent?**

That determines the opportunities available to the storage engine.

---

# 10. Four Workload Examples

The best way to understand layout is to reason from actual access patterns.

## Query A — Fetch one complete order

```text
"Fetch one complete order."
```

Likely access:

```text
order_id
customer
address
status
amount
payment
shipping
...
```

A row-oriented representation can be a natural fit because many fields for one record are physically related.

A columnar representation can still support point lookups, especially with metadata or indexes outside the simple layout model, but the basic columnar advantage is not strongest here.

### Lesson

When the workload wants **many fields for very few records**, row-oriented locality can be useful.

---

## Query B — Calculate average amount for all orders

```sql
SELECT AVG(amount)
FROM orders;
```

The logical request needs one column:

```text
amount
```

A columnar layout can keep the amount values together.

A row-oriented layout mixes amount with other fields.

### Lesson

When the workload wants **one or a few columns across many rows**, columnar locality becomes useful.

---

## Query C — Read country and amount for 500 million rows

```sql
SELECT country, amount
FROM orders;
```

The query references:

```text
country
amount
```

but not the remaining columns.

A columnar layout can potentially avoid the physical regions associated with unrelated columns.

### Lesson

This is a classic analytical access pattern.

---

## Query D — Read 20 columns for a small number of records

```sql
SELECT *
FROM orders
WHERE order_id IN (...);
```

The workload wants nearly every column, but only a small number of records.

The natural advantage of columnar pruning is much smaller because most columns are needed anyway.

### Lesson

Columnar storage does not magically make every access pattern optimal.

---

# 11. Workload-Based Thinking

The core Data Engineering principle is:

> **Storage layout should follow workload characteristics.**

Do not start with:

```text
"Our platform always uses Parquet."
```

Start with:

```text
"What does this dataset need to do?"
```

A practical first-pass matrix is:

| Workload | Typical access pattern | Natural physical fit | Main reason |
| --- | --- | --- | --- |
| Full-record lookup | Few records, many fields | Row-oriented | Record locality |
| Transaction processing | Frequent record-level writes/updates | Row-oriented | Record-at-a-time operations |
| Point lookup | Very small number of records | Often row-oriented thinking | Small-record access pattern |
| Event ingestion | Record-at-a-time or streaming records | Often row-oriented | Efficient movement of complete events |
| Analytical aggregation | Many rows, few columns | Columnar | Column locality and pruning |
| Reporting | Large scans of selected metrics/dimensions | Columnar | Read selected columns |
| Large fact-table analysis | Many rows, subset of attributes | Columnar | Reduce unnecessary reads |
| Batch transformations | Scan, filter, project, aggregate | Columnar | Column access and batch processing |
| Downstream messaging | Complete event/record movement | Often row-oriented | Message/record boundary |

"Natural fit" does not mean "only valid choice."

A production architecture can deliberately use more than one representation.

---

# 12. Why Columnar Storage Often Compresses Better

Columnar storage often creates stronger compression opportunities because similar kinds of values are physically close together.

Consider this country column:

```text
country
-------
IN
IN
US
IN
UK
IN
US
```

A row-oriented layout mixes these strings with names, identifiers, timestamps, amounts, and other data.

A columnar layout brings:

```text
IN
IN
US
IN
UK
IN
US
```

together.

Now the encoding/compression stage can exploit patterns in this one column.

## 12.1 Locality creates patterns

Suppose we have:

```text
status
------
PAID
PAID
PAID
PAID
CANCELLED
PAID
PAID
```

A compression algorithm sees many repeated values close together.

The same is true for:

- low-cardinality categories;
- repeated country codes;
- repeated status values;
- repeated flags;
- slowly changing attributes.

The opportunity comes from **physical locality**.

---

# 13. Dictionary Encoding

Dictionary encoding replaces repeated values with compact references to a dictionary.

Start with:

```text
country
-------
IN
IN
US
IN
UK
IN
US
```

A conceptual dictionary could be:

```text
0 → IN
1 → US
2 → UK
```

The data can then be represented conceptually as:

```text
0
0
1
0
2
0
1
```

The exact binary representation is format-specific.

The important idea is:

> **Repeated values can be represented once plus compact references.**

This is particularly attractive for columns with repeated values and relatively low cardinality.

### When it helps

Examples:

```text
country
status
region
device_type
payment_method
```

### When it may help less

A column in which almost every value is unique may provide less opportunity for dictionary encoding.

For example:

```text
random_uuid
```

may have very high cardinality.

Do not turn this into an absolute rule. Actual effectiveness depends on the values, encoding, format, and implementation.

---

# 14. Run-Length Encoding

**Run-Length Encoding (RLE)** represents repeated values as runs.

Consider:

```text
IN IN IN IN IN US US US
```

Conceptually, this can become:

```text
(IN, 5)
(US, 3)
```

Instead of storing the same symbol repeatedly.

Again, this is a conceptual explanation rather than a specification for a particular file format.

RLE is especially useful when values appear in long runs.

Sorting can create longer runs:

```text
Before sorting:
IN US IN UK IN US IN IN UK

After sorting:
IN IN IN IN UK UK US US
```

The second arrangement may create better opportunities for run-length encoding and other compression techniques.

---

# 15. Encoding Is Not the Same as Compression

These terms are often mixed together.

They are related, but they are not identical.

## Encoding

Encoding can change the representation of values into a form that is more efficient or easier to compress.

Examples at a foundational level include:

- dictionary encoding;
- run-length encoding;
- bit-packing;
- delta-style representations.

## Compression

Compression then applies a general compression algorithm or codec to reduce the byte representation further.

A simplified conceptual pipeline is:

```text
Logical values
     ↓
Encoding
     ↓
More compact / structured representation
     ↓
Compression codec
     ↓
Compressed bytes
```

The exact implementation order and available encodings are format-specific. The mental model is enough for Topic 01.

Topic 02 will explain Parquet's encoding and compression mechanics in substantially more detail.

---

# 16. Sorting and Clustering Can Help Compression

Suppose a column contains:

```text
IN
US
IN
UK
IN
US
IN
IN
```

The values are mixed.

Now imagine the rows are arranged so that similar countries are close:

```text
IN
IN
IN
IN
US
US
UK
```

The physical locality may create:

- longer repeated runs;
- tighter value ranges;
- stronger compression opportunities.

This is one reason **sort order** and **clustering** matter to physical layout.

Sorting is not free, so the correct engineering question is not:

> "Should we always sort?"

It is:

> "Does the performance and storage benefit justify the extra work and operational complexity for this workload?"

Later topics will explore sort order, partitioning, and physical optimization in more depth.

---

# 17. Column Pruning

## 17.1 What is column pruning?

**Column pruning** means reading only the columns required by a query instead of materializing every column in the dataset.

Consider:

```sql
SELECT country, SUM(amount)
FROM orders
GROUP BY country;
```

The referenced columns are:

```text
country
amount
```

The query does not need:

```text
order_id
customer
address
device
campaign
...
```

A columnar file can physically organize those columns separately.

This creates the opportunity for the engine to read only the necessary column regions.

---

# 18. Why Column Pruning Matters

Reading fewer columns can reduce:

- bytes read;
- storage I/O;
- network transfer;
- decompression work;
- memory needed for unused values;
- CPU work associated with decoding and materialization.

A simplified view is:

```text
Without useful column pruning:

file
 ├─ order_id
 ├─ customer
 ├─ country      ← needed
 ├─ amount       ← needed
 ├─ address
 ├─ campaign
 ├─ device
 └─ ...

With column-oriented physical organization:

country      ← read
amount       ← read

other columns ← potentially skipped
```

The exact behavior depends on the file format and query engine.

That last sentence matters.

> **Selecting fewer columns in SQL does not guarantee that every system will perform the minimum physically possible work.**

The engine, file format, compression, metadata, execution plan, storage layer, and query shape all matter.

---

# 19. Coding Demonstration — Column Selection

The following examples demonstrate the **logical request** for fewer columns. They also show the APIs you will encounter in real Data Engineering work.

The examples are intentionally simple. Advanced Parquet metadata inspection comes later.

## 19.1 Create a small dataset with pandas

```python
import pandas as pd

orders = pd.DataFrame(
    {
        "order_id": [1, 2, 3, 4],
        "customer": ["Alice", "Bob", "Carol", "David"],
        "country": ["IN", "US", "IN", "UK"],
        "amount": [100.0, 250.0, 180.0, 120.0],
    }
)

print(orders)
```

### What this code does

- `import pandas as pd` loads pandas.
- `pd.DataFrame(...)` creates a table.
- Each dictionary key becomes a column.
- Each list contains the values for that column.

Conceptual output:

```text
   order_id customer country  amount
0         1    Alice      IN   100.0
1         2      Bob      US   250.0
2         3    Carol      IN   180.0
3         4    David      UK   120.0
```

### Why it matters

This is the logical table we will store physically in different ways.

---

## 19.2 Row-like access

Suppose an application wants the complete record for row 1:

```python
record = orders.iloc[1]

print(record)
```

Conceptually:

```text
order_id        2
customer       Bob
country        US
amount        250.0
```

This is not proof that pandas itself is a row-oriented storage engine. It simply demonstrates **row-oriented thinking**:

> "Give me the fields belonging to this record."

The important distinction is between:

```text
logical access pattern
```

and

```text
physical file layout
```

---

## 19.3 Column-oriented access

Now request only two columns:

```python
selected = orders[["country", "amount"]]

print(selected)
```

Conceptual output:

```text
  country  amount
0      IN   100.0
1      US   250.0
2      IN   180.0
3      UK   120.0
```

This demonstrates the analytical access pattern:

> "I need these columns for many rows."

---

# 20. PyArrow Example — Writing and Selecting Columns

Install the required package in a `uv` project:

```bash
uv add pyarrow
```

Write the DataFrame as Parquet:

```python
import pyarrow as pa
import pyarrow.parquet as pq

table = pa.Table.from_pandas(orders)

pq.write_table(
    table,
    "orders.parquet",
)
```

Now read only two columns:

```python
selected = pq.read_table(
    "orders.parquet",
    columns=["country", "amount"],
)

print(selected)
```

### What happened?

The important part is:

```python
columns=["country", "amount"]
```

The request explicitly says:

```text
Do not return every column.
Return only country and amount.
```

A columnar format such as Parquet can organize those columns separately on disk, allowing the reader to avoid unrelated column data when the format and execution path support it.

### Production lesson

Do not write:

```python
pq.read_table("orders.parquet")
```

automatically for every workload if you only need two columns.

Explicit projection makes the intended access pattern clear and gives the engine an opportunity to minimize physical work.

---

# 21. Polars Example — Projecting Columns

Polars makes column-oriented expressions explicit:

```python
import polars as pl

orders_pl = pl.DataFrame(
    {
        "order_id": [1, 2, 3, 4],
        "customer": ["Alice", "Bob", "Carol", "David"],
        "country": ["IN", "US", "IN", "UK"],
        "amount": [100.0, 250.0, 180.0, 120.0],
    }
)

result = orders_pl.select(
    ["country", "amount"]
)

print(result)
```

Conceptual result:

```text
shape: (4, 2)
┌─────────┬────────┐
│ country ┆ amount │
│ ---     ┆ ---    │
│ str     ┆ f64    │
╞═════════╪════════╡
│ IN      ┆ 100    │
│ US      ┆ 250    │
│ IN      ┆ 180    │
│ UK      ┆ 120    │
└─────────┴────────┘
```

Again, the important concept is projection:

```text
input:   4 columns
output:  2 columns
```

For file scans, engines can often push this requirement down toward the scan layer when the format supports it.

---

# 22. DuckDB Example — SQL Projection

DuckDB lets us express the same concept in SQL:

```python
import duckdb

result = duckdb.sql(
    """
    SELECT country, amount
    FROM 'orders.parquet'
    """
)

print(result)
```

The query references only:

```text
country
amount
```

A columnar file gives the engine a physical organization that can support column pruning.

This is why file layout and query engines are tightly connected.

---

# 23. Predicate Skipping

Column pruning answers:

> **"Which columns do I need?"**

Predicate skipping answers another question:

> **"Within those columns, which blocks do I need?"**

A **predicate** is a condition used to filter data.

Examples:

```sql
WHERE country = 'IN'
```

```sql
WHERE amount > 1000
```

```sql
WHERE created_at >= '2025-03-01'
```

A physical block can sometimes store metadata such as:

```text
min
max
null count
```

A query engine can use this metadata to determine whether a block could possibly contain a matching value.

---

# 24. Simple Predicate-Skipping Example

Suppose a block contains:

```text
created_at min = 2025-01-01
created_at max = 2025-01-31
```

The query asks for:

```sql
WHERE created_at >= '2025-03-01'
```

Compare:

```text
Block range:
2025-01-01 → 2025-01-31

Query requirement:
2025-03-01 and later
```

The block's maximum value is still before the query's minimum required value.

Therefore:

```text
Block cannot contain a match
        ↓
Skip the block
```

No row-by-row examination is required for that block.

This is a **conceptual foundation** for data skipping. Topic 02 will explain the Parquet structures that make this possible.

---

# 25. Predicate Skipping and Sorting

Now consider two blocks.

### Unclustered data

```text
Block A:
2025-01-01
2025-06-20
2025-02-14
2025-09-01
2025-03-18
...

min = 2025-01-01
max = 2025-09-01
```

### Data with a useful sort/cluster order

```text
Block A:
2025-01-01
2025-01-03
2025-01-05
2025-01-08
2025-01-12
...

min = 2025-01-01
max = 2025-01-12
```

For a filter such as:

```sql
WHERE created_at >= '2025-06-01'
```

the first block has a broad range and may be harder to skip.

The second block has a narrow range and can be ruled out more easily.

This does not mean sorting always improves end-to-end performance. Sorting costs CPU and I/O during data production.

The engineering lesson is:

> **A physical ordering decision can influence how useful block-level statistics become later.**

---

# 26. Coding Demonstration — Predicate Skipping as a Concept

The following example does not inspect Parquet metadata. It simply models the logical decision an engine can make.

```python
blocks = [
    {
        "name": "block_1",
        "min_date": "2025-01-01",
        "max_date": "2025-01-31",
    },
    {
        "name": "block_2",
        "min_date": "2025-03-01",
        "max_date": "2025-03-31",
    },
    {
        "name": "block_3",
        "min_date": "2025-06-01",
        "max_date": "2025-06-30",
    },
]

query_start = "2025-05-01"

for block in blocks:
    can_match = block["max_date"] >= query_start

    if can_match:
        print("Read:", block["name"])
    else:
        print("Skip:", block["name"])
```

Conceptual output:

```text
Skip: block_1
Skip: block_2
Read: block_3
```

Why?

- `block_1` ends on January 31.
- `block_2` ends on March 31.
- The query starts on May 1.
- Neither earlier block can contain a May-or-later value.
- `block_3` may contain a match, so it must be considered.

This is intentionally simpler than a real Parquet implementation.

---

# 27. Column Pruning vs Predicate Skipping

These concepts are related but different.

| Technique | Main question | Example |
| --- | --- | --- |
| Column pruning | Which columns are needed? | `country`, `amount` |
| Predicate skipping | Which blocks might contain matching rows? | Skip blocks whose max date is too early |
| Both together | Which column data and which blocks are needed? | Read only `country` and `amount` from relevant blocks |

A strong analytical layout can create opportunities for both.

Conceptually:

```text
Dataset
  ↓
Choose required columns
  ↓
Choose relevant blocks
  ↓
Read only necessary physical data
  ↓
Execute query
```

The exact implementation is engine- and format-dependent.

---

# 28. What Is Not Being Taught Yet

At this point, you only need the conceptual model.

Do **not** memorize details such as:

- exact Parquet footer fields;
- page indexes;
- bloom-filter implementation;
- row-group encoding internals;
- precise page formats;
- detailed codec behavior.

Those topics belong to later parts of Module 2.5.

The foundation is:

```text
Columnar layout
     ↓
separate column regions
     ↓
possible column pruning

Physical blocks
     ↓
metadata about value ranges
     ↓
possible predicate skipping
```

---

# 29. Write-Side Trade-Offs of Columnar Storage

Columnar storage provides important analytical benefits, but those benefits are not free.

A common beginner mistake is:

> "Columnar is good for reading, therefore it must always be good for writing."

That is incomplete.

## 29.1 Why buffering is needed

Imagine receiving these records:

```text
record 1
record 2
record 3
record 4
...
```

A columnar file wants something closer to:

```text
column A values
column B values
column C values
column D values
```

The writer may therefore need to collect a batch of rows before writing an efficient physical representation.

Conceptually:

```text
Incoming rows
     ↓
Buffer / batch
     ↓
Separate values by column
     ↓
Encode
     ↓
Compress
     ↓
Write physical blocks
```

The exact pipeline depends on the implementation.

---

# 30. Buffering and Memory

If a writer tries to construct useful columnar blocks from incoming rows, it may need temporary memory for the batch.

Very small batches can cause problems such as:

- weak compression opportunities;
- too many tiny physical pieces;
- excessive file metadata;
- poor amortization of fixed write costs.

Very large batches can create:

- higher writer memory usage;
- longer time before a batch is committed;
- larger failure/retry units.

Therefore, batch size is itself a production design variable.

---

# 31. Frequent Small Appends

Imagine a system receives one transaction every few milliseconds.

A naive design might attempt:

```text
transaction 1 → write file
transaction 2 → write file
transaction 3 → write file
...
```

For an optimized analytical columnar dataset, that can be inefficient.

Why?

Because each tiny append may have to pay for:

- opening/writing a file or object;
- constructing physical structures;
- metadata/footer work;
- compression setup;
- object-store requests;
- eventual small-file management.

A better analytical pattern may be:

```text
events
  ↓
buffer
  ↓
micro-batch
  ↓
write efficient columnar file
  ↓
repeat
```

Later topics will cover the small-files problem and target file sizes in detail.

---

# 32. Record-at-a-Time Updates

A row-oriented operational design can naturally express:

```text
UPDATE order
SET status = 'PAID'
WHERE order_id = 100;
```

A plain analytical columnar file often does not behave like a mutable row store.

Changing one record may involve rewriting a larger physical region or generating additional files that later require consolidation.

The exact behavior depends on the file format, table architecture, and engine.

The important foundational distinction is:

> **Columnar files are optimized around batches and scans more naturally than around arbitrary record-at-a-time mutation.**

Do not oversimplify this into:

> "Columnar cannot handle inserts."

That statement is false.

Columnar systems can be written efficiently when the workload is batch-oriented.

The issue is **mismatch between the access/write pattern and the physical layout**.

---

# 33. Batch Writes, Micro-Batches, and Buffering

Three useful patterns are:

## Batch

Accumulate a large amount of data before writing.

```text
1 hour of data
      ↓
write optimized files
```

## Micro-batch

Accumulate smaller groups.

```text
1 minute of data
      ↓
write optimized files
```

## Buffering

Keep incoming records temporarily in memory or another durable staging area until enough data exists for efficient file creation.

The correct strategy depends on:

- latency requirements;
- memory limits;
- failure handling;
- file-size objectives;
- query freshness requirements.

---

# 34. A Crucial Distinction: Logical Rows vs Physical Files

Do not confuse:

```text
"one row"
```

with:

```text
"one physical write"
```

A logical dataset may contain:

```text
10 million rows
```

while the physical representation contains:

```text
many files
many blocks
many row groups
many column chunks
```

The mapping between logical rows and physical storage units is a major part of Data Engineering.

---

# 35. Text Formats vs Binary Formats

"Row vs columnar" and "text vs binary" are related concepts, but they are not the same axis.

For example:

```text
CSV       → text, commonly row-record-oriented
JSON Lines → text, commonly record-oriented
Avro      → binary, row-oriented
Parquet   → binary, columnar
ORC       → binary, columnar
Arrow IPC → binary, columnar
```

This gives us two different questions:

### Question 1

How are values physically organized?

```text
rows vs columns
```

### Question 2

How are those values represented?

```text
text vs binary
```

Do not collapse these into one distinction.

---

# 36. Text Formats

Common examples:

- CSV
- JSON Lines

## 36.1 Advantages

### Human-readable

A developer can open:

```text
1,Alice,IN,100
```

and understand it immediately.

JSON is also often easy to inspect:

```json
{"order_id":1,"customer":"Alice","country":"IN","amount":100}
```

### Easy debugging

Text is convenient for:

- quick inspection;
- manual troubleshooting;
- simple command-line tools;
- interoperability with systems that expect text.

### Broad interoperability

Many systems can produce or consume CSV and JSON.

This makes them common at system boundaries and partner interfaces.

---

# 37. Costs of Text Representation

Text has important physical costs.

## 37.1 Parsing

The reader may have to interpret:

```text
"12345"
```

as a number.

Likewise:

```text
"2025-09-28T10:00:00"
```

must be interpreted as a timestamp if that is the intended type.

Parsing consumes CPU.

## 37.2 Representation overhead

A number represented as text includes characters that are not present in the same conceptual way in a typed binary representation.

For example:

```text
123456789
```

is ten text characters.

A binary typed representation can use a fixed physical representation appropriate to its type.

The exact size depends on the binary type and encoding.

## 37.3 Type ambiguity

This text:

```text
00123
```

could mean:

- integer `123`;
- string `"00123"`;
- account code;
- identifier where leading zeros are meaningful.

The text itself does not always provide enough information to know the business meaning.

## 37.4 Precision and interpretation

Typed binary formats can preserve explicit numeric and temporal types.

With text, correctness can depend on:

- parser behavior;
- declared schema;
- locale assumptions;
- formatting;
- conversion rules.

Do not claim that "text always loses precision." A text format can represent high-precision values if the producer and reader agree on the representation. The engineering concern is that the type and interpretation need to be handled explicitly.

---

# 38. Binary Formats

Examples from this module include:

- Avro;
- Parquet;
- ORC;
- Arrow IPC.

Binary formats can provide:

- typed representations;
- compact encodings;
- efficient machine parsing;
- schema information;
- better integration with typed execution engines.

But binary formats can also trade away:

- direct human readability;
- ease of manual inspection;
- simple text-based debugging.

Binary is therefore not automatically "better."

It is a different representation with different operational trade-offs.

---

# 39. Typing: Why It Matters

Consider:

```text
"00123"
```

Imagine three possible interpretations.

### Interpretation A — integer

```text
123
```

### Interpretation B — identifier

```text
"00123"
```

### Interpretation C — account code

```text
"00123"
```

The leading zeros matter for B and C but not A.

Now consider:

```text
"2025-03-01"
```

Is this:

- a string;
- a date;
- a partition key;
- a display value?

Text alone does not guarantee the intended semantic type.

A typed format can represent:

```text
INT64
DATE
TIMESTAMP
DECIMAL
STRING
```

as explicit data types.

That reduces ambiguity when the producer and consumer agree on the schema.

---

# 40. Precision: A Careful Explanation

Precision concerns are easiest to understand with numeric values.

Suppose a business system has:

```text
amount = 1234.5678
```

A parser may need to know whether the field should be:

```text
FLOAT
DOUBLE
DECIMAL
STRING
```

These types have different numerical semantics.

A good production data pipeline therefore does not depend on appearance alone.

Instead:

```text
raw representation
      ↓
explicit schema
      ↓
validated type
      ↓
typed downstream storage
```

The exact precision guarantees come from the type and representation chosen.

This is why type semantics matter when comparing text and binary formats.

---

# 41. Self-Describing vs External-Schema Formats

Another important axis is:

> **Where does the schema live?**

## 41.1 Self-describing

A file contains enough schema information for the reader to understand the structure.

Examples to discuss at this level:

- Avro;
- Parquet.

This does not mean the file carries every piece of platform metadata ever needed. It means the data format itself carries schema information relevant to interpreting its contents.

## 41.2 External / schema-managed

The file representation alone may not provide a complete strong schema.

A common example is:

```text
orders.csv
orders-schema.yaml
```

Or:

```text
raw CSV
   +
catalog/metastore definition
```

The surrounding platform supplies the interpretation.

---

# 42. Why Schema Location Matters

Schema placement affects:

- portability;
- discoverability;
- validation;
- evolution;
- compatibility;
- operational complexity.

## Embedded schema

```text
file
 ├─ data
 └─ schema information
```

Benefits can include:

- easier self-contained interpretation;
- more portable files;
- fewer hidden dependencies.

## External schema

```text
file
   +
schema registry/catalog/definition
```

Benefits can include:

- centralized management;
- explicit governance;
- standardized evolution rules.

Costs can include:

- dependency on the external schema system;
- more operational coordination.

Neither model eliminates the need for good schema-management practices.

---

# 43. Important Nuance: Embedded Schema Does Not Mean "No Catalog Needed"

A Parquet or Avro file can carry schema information while the platform also maintains:

```text
catalog
registry
dataset metadata
lineage
governance information
```

So the useful distinction is:

```text
schema embedded in the file
```

versus

```text
schema managed by the surrounding platform
```

These can coexist.

A production data platform commonly uses both.

---

# 44. PAX: The Hybrid Layout

PAX is an important advanced concept because it helps bridge row-oriented and column-oriented thinking.

**PAX** stands for:

> **Partition Attributes Across**

The basic idea is:

1. divide the table's rows into blocks;
2. within each block, organize values by column.

This creates a hybrid between pure row and pure column locality.

---

# 45. Pure Row vs Pure Column vs PAX

## Pure row-oriented

```text
R1: A1 B1 C1 D1
R2: A2 B2 C2 D2
R3: A3 B3 C3 D3
R4: A4 B4 C4 D4
```

## Pure column-oriented

```text
A: A1 A2 A3 A4
B: B1 B2 B3 B4
C: C1 C2 C3 C4
D: D1 D2 D3 D4
```

## PAX / hybrid

```text
Block 1
  A: A1 A2
  B: B1 B2
  C: C1 C2
  D: D1 D2

Block 2
  A: A3 A4
  B: B3 B4
  C: C3 C4
  D: D3 D4
```

The exact low-level layout depends on the implementation.

The concept is what matters.

---

# 46. Why PAX Exists

PAX attempts to gain useful locality from both directions.

Within a block:

```text
A values are together
B values are together
C values are together
D values are together
```

But the block still contains a bounded set of nearby rows.

This can create a useful balance between:

- row locality;
- column locality;
- cache behavior;
- bounded physical units.

You should think of PAX as a **hybrid physical-layout idea**, not as a synonym for every modern columnar file.

---

# 47. PAX and Modern Analytical File Formats

Parquet uses **row groups**.

ORC uses **stripes**.

These structures are:

> **Conceptually related to the PAX idea because they group rows into larger physical units and organize column data within those units.**

Do not say:

> "Parquet is literally PAX."

That is too strong.

The useful relationship is:

```text
PAX conceptual idea
       ↓
rows grouped into blocks
       ↓
columns organized within blocks
       ↓
modern analytical file designs use related physical organization
       ↓
Parquet row groups / ORC stripes
```

This relationship helps explain why a columnar file does not necessarily mean:

```text
one giant column for the entire dataset
```

Instead, modern formats often combine:

```text
dataset
  ↓
physical groups / stripes
  ↓
column chunks inside those groups
```

Detailed Parquet structure comes in Topic 02.

---

# 48. A Practical PAX Thought Experiment

Suppose a dataset contains:

```text
1 billion rows
20 columns
```

A pure conceptual column store might look like:

```text
column 1: 1 billion values
column 2: 1 billion values
...
column 20
```

A hybrid block design might instead divide the dataset into:

```text
block 1 → 1 million rows
block 2 → 1 million rows
...
block 1000 → 1 million rows
```

Within each block:

```text
20 column regions
```

Now the system has bounded physical units it can:

- read;
- skip;
- decode;
- process in parallel.

This is one reason physical blocks matter so much to analytical systems.

---

# 49. Splittability

A file can be large.

The question is:

> **Can multiple workers independently process different portions of that file?**

This property is called **splittability**.

A useful definition is:

> **Splittability is whether a large file can be divided into independently readable pieces so multiple workers can process different portions in parallel.**

---

# 50. Why Splittability Matters

Suppose a file contains:

```text
100 GB
```

and one machine must process all 100 GB sequentially.

Now imagine the file can safely be divided into four independent pieces:

```text
Worker 1 → 25 GB
Worker 2 → 25 GB
Worker 3 → 25 GB
Worker 4 → 25 GB
```

The work can proceed in parallel.

The exact speedup is not guaranteed to be 4× because real systems also deal with:

- startup overhead;
- network bandwidth;
- CPU limits;
- skew;
- coordination;
- memory constraints;
- data dependencies.

Still, parallel processing can be a major reason splittability matters.

---

# 51. Uncompressed CSV and JSON Lines

An uncompressed large CSV can generally be processed in chunks from different offsets, provided the reader can find record boundaries safely.

JSON Lines is commonly amenable to splitting because records are line-delimited:

```text
record 1\n
record 2\n
record 3\n
```

A worker can start near a byte offset and move to the next record boundary.

Again, exact behavior depends on the parser and execution engine.

---

# 52. Why a Single Gzip Text Stream Is Usually Not Splittable in the Same Straightforward Way

Consider:

```text
large.csv.gz
```

The file is one gzip-compressed stream.

A worker cannot simply jump to an arbitrary compressed byte offset and independently decode the remainder as though it were a complete gzip stream.

Conceptually:

```text
gzip stream
████████████████████████████████████
        ↑
     worker 2 cannot simply start here
```

That makes one large gzip-compressed text stream awkward for parallel splitting.

This is one reason:

```text
"compressing a giant CSV into .gz"
```

is not equivalent to:

```text
"using an analytical file format that compresses internal physical units"
```

---

# 53. Compression Does Not Automatically Mean "Not Splittable"

This misconception is important.

The incorrect statement is:

> "Compression makes files non-splittable."

The correct statement is:

> **Splittability depends on how the file and compression are organized.**

A container format may compress data internally in independently readable units.

Conceptually:

```text
File
 ├─ block 1 → compressed independently
 ├─ block 2 → compressed independently
 ├─ block 3 → compressed independently
 └─ block 4 → compressed independently
```

Now different workers can process different internal units.

This is a key idea in formats such as Parquet, ORC, and Avro, although their internal structures differ.

Topic 07 will examine compression codecs and splittability in more depth.

---

# 54. File Format vs Container Design

Do not think:

```text
codec = splittability
```

Think:

```text
format/container design
        +
compression organization
        +
record/block boundaries
        ↓
parallel-read possibilities
```

A compression codec is only one part of the physical design.

---

# 55. Where Row and Columnar Formats Appear in a Data Pipeline

A modern data pipeline may look conceptually like:

```text
Source systems
      ↓
Ingestion / Messaging
      ↓
Bronze
      ↓
Silver
      ↓
Gold / Analytics
      ↓
BI / ML / Applications
```

Different stages may benefit from different physical representations.

---

# 56. Ingestion and Messaging

At the ingestion boundary, data often arrives as:

```text
one record
one event
one message
```

A row-oriented representation can fit this boundary naturally.

Examples:

```text
Avro event
JSON record
CSV row
message payload
```

The key requirement may be:

```text
"move or persist one complete record"
```

rather than:

```text
"scan 500 million rows while reading only two columns"
```

---

# 57. Bronze

Bronze storage often represents the source boundary.

The original source representation may be retained for:

- replay;
- audit;
- troubleshooting;
- forensic analysis;
- reproducible reprocessing.

This means bronze may legitimately contain:

```text
source JSON
source Avro
source CSV
source XML
```

rather than immediately converting everything to one analytical format.

The architecture depends on the organization's requirements.

---

# 58. Silver

Silver typically contains validated, typed, transformed data.

At this stage, analytical workloads become more important.

Columnar storage can therefore become attractive because the dataset may be:

- large;
- repeatedly scanned;
- filtered;
- aggregated;
- joined;
- shared by many downstream consumers.

A common conceptual pattern is:

```text
raw source
   ↓
typed transformation
   ↓
columnar analytical storage
```

---

# 59. Gold / Analytics

Gold datasets often serve:

- BI;
- reporting;
- dashboards;
- analytical applications;
- large historical queries.

These workloads frequently scan many rows while using a subset of dimensions and measures.

Columnar organization can therefore fit naturally.

But even here, the workload decides.

A gold dataset serving a small number of point lookups may have different physical requirements from a fact table scanned by a reporting engine.

---

# 60. Real Architectures Often Use Both

A production pipeline may legitimately contain:

```text
row-oriented ingestion
        ↓
row-oriented transport
        ↓
raw bronze
        ↓
columnar silver
        ↓
columnar gold
        ↓
BI / analytics
```

Or:

```text
source event
   ↓
message bus
   ↓
Avro
   ↓
stream processor
   ↓
Parquet
```

Or another arrangement entirely.

The point is not to memorize one architecture.

The point is:

> **Different pipeline stages can have different physical workload requirements.**

---

# 61. Format Examples: Foundational Comparison

This table is intentionally foundational. It is **not** the detailed format-selection matrix from Topic 05.

| Format | Typical layout | Main use | Schema behavior | Human readability | Typical workload | Major trade-off |
| --- | --- | --- | --- | --- | --- | --- |
| CSV | Record-oriented text | Simple interchange, exports, ingestion boundaries | Usually external/implicit | High | Row/record-oriented movement | Parsing and typing ambiguity |
| JSON Lines | Record-oriented text | Events, APIs, logs, ingestion | Usually carried by data conventions/external rules | High | Record-at-a-time processing | Parsing and larger representation |
| Avro | Row-oriented binary | Ingestion, CDC, messaging | Embedded schema | Low | Record-oriented serialization | Less convenient for broad analytical scans |
| Parquet | Columnar binary | Analytical storage | Embedded file schema plus platform metadata | Low | Scans, aggregation, selected columns | Batch-oriented write design |
| ORC | Columnar binary | Analytical storage, Hive ecosystem | Embedded schema | Low | Large analytical scans | Ecosystem choices and format-specific trade-offs |
| Arrow IPC | Columnar binary | In-memory/interchange transport | Schema carried with the representation | Low | Data interchange and analytic memory workflows | Primarily an interchange/memory representation rather than lake storage |

Remember:

> A format's "typical use" is not a law.

A format can be used outside its most common workload.

---

# 62. A Useful Two-Axis Mental Model

When comparing storage choices, mentally separate at least these dimensions:

```text
Dimension 1:
How are values organized?
    row
    column
    hybrid

Dimension 2:
How are values represented?
    text
    binary
```

Then consider additional dimensions:

```text
schema
compression
encoding
splittability
write pattern
read pattern
metadata
parallelism
operational requirements
```

This prevents shallow reasoning such as:

```text
binary = good
text = bad
columnar = good
row = bad
```

Those statements are not useful engineering rules.

---

# 63. Hands-On Coding Lab

This section demonstrates the physical ideas with beginner-friendly Python.

## 63.1 Environment

Inside your existing `formats_lab/` `uv` project:

```bash
uv add pyarrow pandas polars duckdb
```

You may already have these packages from Module 2.4.

---

# 64. Example A — Create a Simple Orders Dataset

Start small.

```python
import pandas as pd

orders = pd.DataFrame(
    {
        "order_id": [1, 2, 3, 4, 5, 6],
        "customer": [
            "Alice",
            "Bob",
            "Carol",
            "David",
            "Eve",
            "Frank",
        ],
        "country": ["IN", "US", "IN", "UK", "IN", "US"],
        "amount": [100, 250, 180, 120, 300, 220],
    }
)

print(orders)
```

### Line-by-line explanation

```python
import pandas as pd
```

Loads pandas.

```python
orders = pd.DataFrame(
    {
        "order_id": [1, 2, 3, 4, 5, 6],
        "customer": ["Alice", "Bob", "Carol", "David", "Eve", "Frank"],
        "country": ["IN", "US", "IN", "UK", "IN", "US"],
        "amount": [100, 250, 180, 120, 300, 220],
    }
)
```

Creates a table.

Defines four columns.

The result is:

```text
6 rows × 4 columns
```

### Why this matters

Every storage discussion starts with a logical dataset like this.

---

# 65. Example B — Demonstrate Row-Like Access

```python
order = orders.iloc[2]

print(order)
```

Conceptual output:

```text
order_id        3
customer    Carol
country         IN
amount        180
```

The access pattern is:

```text
give me one record
```

That is row-oriented thinking.

Again, pandas' in-memory behavior is not the same thing as an on-disk row store. This example demonstrates the **workload pattern**, not pandas' file layout.

---

# 66. Example C — Demonstrate Column-Oriented Access

```python
selected = orders[["country", "amount"]]

print(selected)
```

Conceptual output:

```text
  country  amount
0      IN     100
1      US     250
2      IN     180
3      UK     120
4      IN     300
5      US     220
```

The access pattern is:

```text
give me two columns for many records
```

That is classic analytical column-oriented thinking.

---

# 67. Example D — Write a Columnar File and Read a Projection

```python
import pyarrow as pa
import pyarrow.parquet as pq

table = pa.Table.from_pandas(orders)

pq.write_table(
    table,
    "orders.parquet",
)
```

Then:

```python
selected = pq.read_table(
    "orders.parquet",
    columns=["country", "amount"],
)

print(selected)
```

### Important physical idea

The query asks for:

```text
country
amount
```

The Parquet layout keeps column data in separate physical structures, making column projection possible.

Do not interpret this simple example as exposing the full mechanics of Parquet.

Topic 02 will explain row groups, column chunks, pages, statistics, and the footer.

---

# 68. Example E — Compare Column Selection Across Libraries

### PyArrow

```python
arrow_table = pq.read_table(
    "orders.parquet",
    columns=["country", "amount"],
)
```

### Polars

```python
import polars as pl

orders_pl = pl.read_parquet(
    "orders.parquet"
)

result = orders_pl.select(
    ["country", "amount"]
)

print(result)
```

### DuckDB

```python
import duckdb

result = duckdb.sql(
    """
    SELECT country, amount
    FROM 'orders.parquet'
    """
)

print(result)
```

All three examples express a similar logical requirement:

```text
Only country and amount are needed.
```

The engines differ internally, but the workload concept is shared.

---

# 69. Example F — Demonstrate Compression-Friendly Values

Create repetitive and high-cardinality columns:

```python
import pandas as pd

df = pd.DataFrame(
    {
        "country": ["IN"] * 8 + ["US"] * 4 + ["UK"] * 2,
        "random_id": [f"id-{i:08d}" for i in range(14)],
    }
)

print(df["country"].nunique())
print(df["random_id"].nunique())
```

Conceptual output:

```text
3
14
```

The `country` column has only three distinct values.

The `random_id` column has fourteen distinct values.

This does **not** prove a compression ratio. It demonstrates why cardinality matters when thinking about encoding opportunities.

A real experiment must write the data and measure the resulting file sizes.

---

# 70. Example G — Sort to Create More Local Similarity

Start with:

```python
countries = [
    "IN",
    "US",
    "IN",
    "UK",
    "IN",
    "US",
    "IN",
    "IN",
]
```

Sort it:

```python
sorted_countries = sorted(countries)

print(countries)
print(sorted_countries)
```

Conceptual output:

```text
['IN', 'US', 'IN', 'UK', 'IN', 'US', 'IN', 'IN']

['IN', 'IN', 'IN', 'IN', 'IN', 'UK', 'US', 'US']
```

The sorted version contains longer runs.

This can create better opportunities for:

- run-length encoding;
- tighter min/max ranges;
- compression;
- predicate skipping.

Actual benefits should be measured rather than assumed.

---

# 71. Example H — Model Block Skipping

```python
blocks = [
    ("block_1", 1, 100),
    ("block_2", 101, 200),
    ("block_3", 201, 300),
]

query_min = 250

for name, block_min, block_max in blocks:
    if block_max < query_min:
        print("Skip:", name)
    else:
        print("Read:", name)
```

Conceptual output:

```text
Skip: block_1
Skip: block_2
Read: block_3
```

The mental model is:

```text
block 1 → maximum is 100 → cannot match 250+
block 2 → maximum is 200 → cannot match 250+
block 3 → maximum is 300 → may match
```

These are **partition-independent physical blocks** in the conceptual sense: the point is that a query may skip internal blocks based on their value ranges even when the dataset is not divided into directory partitions. This differs from partition pruning, which skips whole directory-level partitions.

Again, this is a conceptual model of metadata-based skipping.

---

# 72. A Small Full Example

The following example combines several ideas in one place.

```python
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import duckdb

output = Path("orders.parquet")

orders = pd.DataFrame(
    {
        "order_id": [1, 2, 3, 4, 5, 6],
        "customer": [
            "Alice",
            "Bob",
            "Carol",
            "David",
            "Eve",
            "Frank",
        ],
        "country": ["IN", "US", "IN", "UK", "IN", "US"],
        "amount": [100.0, 250.0, 180.0, 120.0, 300.0, 220.0],
    }
)

table = pa.Table.from_pandas(orders)

pq.write_table(
    table,
    output,
)

result = duckdb.sql(
    f"""
    SELECT country, SUM(amount) AS total_amount
    FROM '{output}'
    GROUP BY country
    ORDER BY country
    """
)

print(result)
```

### Why this example matters

The query needs:

```text
country
amount
```

The file is columnar.

Therefore, the physical layout is aligned with the query's access pattern.

The experiment becomes interesting when the dataset becomes large enough that bytes read and physical scan behavior become measurable.

---

# 73. Required Hands-On Exercise — `layout_compare.py`

The roadmap requires a comparison exercise across common row-oriented and columnar representations.

You will create `layout_compare.py` yourself in your existing lab project.

**This task documentation is part of this Markdown file. No script is created by this exercise description.**

## Objective

Generate:

> **10 million orders with 20 columns**

and compare:

- CSV;
- JSON Lines;
- Avro;
- Parquet;
- ORC.

Initially, use library defaults.

The goal is not to find a universal winner.

The goal is to observe how workload and physical layout affect measurements.

---

# 74. Exercise Dataset Design

Create a realistic 20-column order schema.

For example:

```text
order_id
customer_id
customer_name
country
region
currency
status
payment_method
channel
product_category
quantity
unit_price
amount
discount
tax
created_at
updated_at
warehouse_id
sales_rep_id
is_priority
```

You may generate synthetic values.

Aim for realistic distributions:

```text
country            → low/moderate cardinality
status             → low cardinality
payment_method     → low cardinality
customer_id        → higher cardinality
order_id           → unique
created_at         → time-like
amount             → numeric
quantity           → integer
```

The data should be identical logically across the format outputs.

---

# 75. Exercise Step 1 — Generate 10 Million Rows

Your learner-created script should produce:

```text
10,000,000 rows
20 columns
```

Do not optimize prematurely.

Start with a reproducible random seed.

Example pattern:

```python
import numpy as np

rng = np.random.default_rng(42)
```

The exact generator implementation is left to you.

The important requirements are:

- reproducibility;
- same logical dataset across formats;
- realistic enough value distributions to create meaningful measurements.

---

# 76. Exercise Step 2 — Write Each Format

Write:

```text
orders.csv
orders.jsonl
orders.avro
orders.parquet
orders.orc
```

Use library defaults initially.

Do not compare:

```text
Parquet with zstd level 19
```

against:

```text
CSV with no compression
```

and then conclude the format itself caused every difference.

At this first stage, you are learning the effect of the broader representation and default configuration.

Later topics will teach controlled benchmarking of codecs and physical knobs in more detail.

---

# 77. Exercise Step 3 — Record File Size

Measure the physical file size.

For each output record:

```text
format
file_size_bytes
file_size_mb
```

A simple Python helper:

```python
from pathlib import Path

def file_size_bytes(path: str) -> int:
    return Path(path).stat().st_size
```

Then:

```python
size = file_size_bytes("orders.parquet")
print(size)
```

The size is a measurement, not a judgment.

---

# 78. Exercise Step 4 — Measure Full-Column Read Time

Measure the time to read all columns.

A generic pattern:

```python
from time import perf_counter

start = perf_counter()

# format-specific read here

elapsed = perf_counter() - start

print(f"Read time: {elapsed:.3f}s")
```

Record:

```text
format
full_read_seconds
```

Do not treat one measurement as truth.

Repeat the experiment.

---

# 79. Exercise Step 5 — Measure One-Column Aggregation

For example:

```text
SUM(amount)
```

The logical operation is:

```sql
SELECT SUM(amount)
FROM orders;
```

For each format, measure the time required to produce the result.

Record:

```text
format
sum_one_column_seconds
```

This is where columnar physical organization becomes especially relevant.

---

# 80. Exercise Step 6 — Two-Column Query With Date Filter

Run a query that:

- selects 2 of the 20 columns;
- applies a date filter.

Example:

```sql
SELECT country, amount
FROM orders
WHERE created_at >= DATE '2025-01-01'
```

Adjust the date to match your generated dataset.

The important pattern is:

```text
projection:
  2 columns

predicate:
  date filter
```

This lets you study both:

```text
column pruning
```

and the conceptual foundation of:

```text
predicate skipping
```

---

# 81. Exercise Step 7 — Compare Bytes Read

Where the chosen engine exposes reliable physical bytes-read information, record it.

For example, DuckDB provides execution information through its profiling and explain tooling.

At this stage, you do not need to reverse-engineer every statistic.

Record what the tool can expose consistently.

Use a result table such as:

| Format | File size | Full read | One-column sum | Filtered query | Bytes read |
| --- | ---: | ---: | ---: | ---: | ---: |
| CSV | | | | | |
| JSON Lines | | | | | |
| Avro | | | | | |
| Parquet | | | | | |
| ORC | | | | | |

Leave cells blank until measured.

Never invent values.

---

# 82. Exercise Step 8 — Save Results

The roadmap specifies:

```text
experiments/layout_compare.csv
```

Your learner-created script should write the measurement table there.

Again:

> **This Markdown file documents the exercise. It does not create the CSV.**

A simple conceptual output schema is:

```text
format
file_size_bytes
write_seconds
full_read_seconds
sum_one_column_seconds
filtered_query_seconds
bytes_read
notes
```

---

# 83. How to Interpret the Experiment

Do not ask:

> "Which file format won?"

Ask:

### Question 1

Which representation produced the largest file?

### Question 2

Which representation made one-column access cheap?

### Question 3

Which representation required more parsing?

### Question 4

Which results changed between cold and warm cache?

### Question 5

Which results were dominated by the query engine instead of the file format?

### Question 6

Which measurements are comparable and which are not?

### Question 7

What workload would make each representation reasonable?

This is Data Engineering reasoning.

---

# 84. Fair Experimentation

A format comparison can be meaningless if the experiment is poorly controlled.

## 84.1 Same dataset

Use the same logical records.

```text
same rows
same values
same column semantics
```

Do not generate a different dataset for each format.

## 84.2 Same row count

All formats should contain the same number of records.

## 84.3 Same query

Use the same logical query pattern.

For example:

```sql
SELECT country, amount
FROM orders
WHERE created_at >= ...
```

Do not compare one format using a full scan with another using a highly selective filter.

## 84.4 Comparable environment

Try to keep constant:

- machine;
- CPU limits;
- RAM;
- operating-system environment;
- storage location;
- engine version.

## 84.5 Cache awareness

A second read may be faster because:

- the operating system cache is warm;
- the object-store or filesystem cache is warm;
- the engine has internal caches.

Therefore distinguish:

```text
cold-ish run
warm-ish run
```

You do not need a perfect laboratory environment to learn from the experiment. You do need to record conditions.

## 84.6 Repeat measurements

One timing is noise-sensitive.

Run each workload multiple times.

Record:

```text
run 1
run 2
run 3
...
```

Then summarize using a consistent method.

## 84.7 Compare compression deliberately

Do not accidentally mix:

```text
compressed Parquet
```

with:

```text
uncompressed ORC
```

and attribute every difference to row-vs-column layout.

Later Topic 07 covers controlled compression benchmarking.

## 84.8 Avoid vendor-marketing benchmarks

A vendor benchmark may be useful evidence, but it is not the same as a benchmark designed around your workload.

Your workload should include:

- your data shape;
- your query pattern;
- your file system or object storage;
- your engine;
- your memory constraints;
- your expected scale.

## 84.9 Do not declare a universal winner

A benchmark teaches you about:

```text
this dataset
+
this workload
+
this environment
+
this configuration
```

It does not prove:

```text
format X is universally best.
```

---

# 85. Common Misconceptions

## Misconception 1 — "Columnar is always better."

### Correction

It depends on the workload.

Columnar storage is often attractive for large scans over a subset of columns.

Row-oriented storage can fit record-level and transaction-oriented workloads naturally.

---

## Misconception 2 — "Row-oriented means slow."

### Correction

A row-oriented design can be efficient for:

- complete-record reads;
- record-at-a-time writes;
- point lookups;
- transactional access patterns.

"Slow" only makes sense relative to a workload and a measured system.

---

## Misconception 3 — "Columnar cannot be written efficiently."

### Correction

Batch-oriented columnar writes can be efficient.

The issue is usually the mismatch between:

```text
record-at-a-time mutation
```

and:

```text
batch-oriented physical organization
```

---

## Misconception 4 — "Compression alone makes data analytical."

### Correction

Compression and physical layout solve different problems.

Compression reduces bytes.

Columnar organization changes which values are physically adjacent and therefore what the reader can potentially select or skip.

---

## Misconception 5 — "Encoding and compression are the same thing."

### Correction

Encoding changes or simplifies the representation.

Compression reduces the resulting byte representation.

Conceptually:

```text
values
  ↓
encoding
  ↓
compression
```

---

## Misconception 6 — "Every compressed file is non-splittable."

### Correction

Splittability depends on the file/container design and how compressed data is organized.

A single compressed text stream may be awkward to split.

A structured file can maintain independent compressed units.

---

## Misconception 7 — "Text formats have no schema."

### Correction

A text file may lack a strong embedded schema, but the surrounding platform can provide one.

For example:

```text
CSV
+
schema definition
```

or:

```text
CSV
+
catalog
```

The schema can exist outside the text file.

---

## Misconception 8 — "Reading one column always means the system reads only that column from storage."

### Correction

Column pruning depends on:

- physical format;
- engine;
- file layout;
- compression;
- metadata;
- execution path.

The query engine may still perform extra work in some situations.

---

# 86. Debugging and Troubleshooting

Performance experiments often produce surprising results.

That is useful.

The goal is to investigate rather than immediately conclude that a format is "bad."

---

## 86.1 "Why did my CSV comparison show unexpected results?"

### Symptom

Two logically identical datasets do not have exactly the same values after reading.

### Likely causes

- delimiter parsing issues;
- embedded newlines;
- quoting;
- missing-value interpretation;
- numeric conversion;
- timestamp parsing;
- leading zeros;
- encoding differences.

### How to investigate

Check:

```text
row count
column count
column names
null counts
dtypes
representative values
```

For numeric and identifier columns, specifically inspect values such as:

```text
00123
0
0.00
123.456789
```

### What to measure

Compare:

```text
row count
null count
min/max
distinct count
sample rows
schema
```

### Lesson

Text is flexible, but flexibility creates parsing and typing responsibilities.

---

## 86.2 "Why is my file larger than expected?"

### Symptom

A file is larger than anticipated.

### Likely causes

- high-cardinality values;
- poor repetition;
- low compressibility;
- large textual representations;
- different codec defaults;
- metadata overhead;
- small physical batches;
- already-compressed data.

### How to investigate

Ask:

```text
How many unique values are there?
Are the values repetitive?
Was compression enabled?
What compression setting was used?
Are files extremely small?
```

### What to measure

Record:

```text
unique counts
file size
rows
average bytes per row
codec
```

### Lesson

Compression is data-dependent.

---

## 86.3 "Why did selecting fewer columns not reduce runtime?"

### Symptom

You changed:

```sql
SELECT *
```

to:

```sql
SELECT country, amount
```

but runtime barely changed.

### Likely causes

- dataset is small;
- storage was already cached;
- query startup dominates;
- engine overhead dominates;
- other parts of the query dominate;
- only a small percentage of time was spent reading unused columns;
- the engine or format did not prune as expected;
- results are constrained by CPU rather than storage.

### How to investigate

Measure:

```text
bytes read
CPU time
wall-clock time
cache state
query plan
```

### Lesson

Lower physical bytes do not necessarily produce a proportional reduction in end-to-end runtime.

---

## 86.4 "Why do two runs have different timings?"

### Symptom

Run 1:

```text
8 seconds
```

Run 2:

```text
3 seconds
```

### Likely causes

- filesystem cache;
- object-store cache;
- engine cache;
- CPU frequency variation;
- background workload;
- Python process startup;
- JIT or initialization effects in some engines.

### How to investigate

Run repeated measurements.

Record:

```text
cold-ish / warm-ish
run number
environment
```

### Lesson

Benchmarking is measurement science, not stopwatch theater.

---

## 86.5 "Why can't I compare compressed and uncompressed formats directly?"

### Symptom

A compressed file is much smaller, and you conclude the format is better.

### Likely cause

You changed two variables:

```text
format
+
compression
```

### How to investigate

Run a controlled comparison.

For example:

```text
same logical dataset
same or comparable compression strategy
```

### Lesson

Change one important variable at a time.

---

## 86.6 "Why did my query still touch many bytes?"

### Possible causes

- weak column pruning;
- broad predicate;
- poor physical clustering;
- high fraction of rows matching;
- format/engine limitations;
- small dataset where metadata does not save much;
- compressed data and accounting differences.

### Investigation

Check:

```text
selected columns
filter selectivity
physical file layout
metadata
query plan
bytes read
```

### Lesson

A filter is only useful for skipping if the physical layout gives the engine evidence that blocks can be ruled out.

---

## 86.7 "Why did my string column not compress as much as expected?"

### Possible causes

The strings may be:

- mostly unique;
- long;
- random;
- high-cardinality;
- already compressed or encoded in an awkward way.

### Investigation

Measure:

```text
row count
distinct count
average string length
frequency distribution
sorted vs unsorted layout
```

### Lesson

The value distribution matters as much as the format.

---

# 87. Decision Framework

Use this decision sequence whenever choosing a physical layout.

```text
1. What does the workload read?
2. What does the workload write?
3. Whole records or a few columns?
4. Point lookups or large scans?
5. Frequent small writes or batched writes?
6. How much data?
7. How much data must a typical query touch?
8. Is compression important?
9. Is parallel processing important?
10. Where in the pipeline is this data?
```

Then evaluate:

```text
requirements
    ↓
workload characteristics
    ↓
candidate layouts
    ↓
measure
    ↓
operational constraints
    ↓
decision
```

A useful principle is:

> **There is no universally best layout. The best layout is the one that fits the workload and operating constraints.**

---

# 88. Three Required Workload Decisions

The following scenarios are deliberately different.

The purpose is not to memorize the "answer."

The purpose is to practice the reasoning process.

---

## Workload Decision 1 — Operational Order Lookup

### Scenario

A retail application serves customer-service users.

A support agent enters:

```text
order_id = 81278392
```

The system returns:

```text
customer
address
payment status
shipping status
items
amount
timestamps
```

### Workload description

**Read pattern**

```text
few records
many fields
```

**Write pattern**

```text
frequent order creation and updates
```

**Dataset characteristics**

```text
large number of orders
continuous change
point lookups are important
```

### Candidate layout to evaluate

A row-oriented physical design is a natural candidate.

### Reasoning

The workload strongly values:

```text
complete records
+
small targeted operations
+
frequent updates
```

These characteristics align with row-oriented locality.

### Trade-offs

A row-oriented representation may not be ideal for huge analytical scans such as:

```text
SUM(amount)
GROUP BY country
```

on the full history.

### What to measure

Before standardizing, measure:

```text
point-lookup latency
insert throughput
update latency
storage size
concurrency behavior
```

---

## Workload Decision 2 — Historical Sales Analytics

### Scenario

A retail company stores:

```text
2 billion orders
```

A common query is:

```sql
SELECT
    country,
    SUM(amount)
FROM orders
WHERE created_at >= DATE '2025-01-01'
GROUP BY country;
```

### Workload description

**Read pattern**

```text
many rows
few columns
```

**Write pattern**

```text
daily or hourly batches
```

**Dataset characteristics**

```text
large historical table
repeated analytical scans
time-based filters
```

### Candidate layout to evaluate

A columnar physical design is a natural candidate.

### Reasoning

The workload aligns with:

```text
column projection
+
large scans
+
batch writes
+
analytical aggregation
```

### Trade-offs

A highly optimized columnar layout may require:

- batching;
- compaction;
- deliberate file organization;
- additional work during ingestion.

### What to measure

Measure:

```text
bytes read
filtered-query time
full-scan time
storage size
write throughput
```

---

## Workload Decision 3 — Event Ingestion Plus Analytics

### Scenario

A web platform receives millions of events:

```text
click
page_view
add_to_cart
purchase
```

The event is generated continuously.

Operational requirements:

```text
low-latency event ingestion
```

Analytical requirements:

```text
daily reporting
large historical scans
```

### Workload description

**Read pattern**

```text
recent event reads
+
large analytical scans
```

**Write pattern**

```text
continuous record-at-a-time ingestion
+
periodic batch processing
```

**Dataset characteristics**

```text
high volume
continuous growth
long retention
```

### Candidate architectural pattern to evaluate

A hybrid representation can make sense:

```text
event transport / ingestion
        ↓
row-oriented event representation
        ↓
batch or streaming transformation
        ↓
columnar analytical storage
```

### Reasoning

The workload has two different access patterns.

Trying to force one physical layout to serve both equally well may create unnecessary trade-offs.

### Trade-offs

You may introduce:

- transformation cost;
- duplicate representations;
- additional storage;
- ingestion-to-analytics latency;
- more operational components.

### What to measure

Measure:

```text
ingestion latency
event throughput
analytical query time
storage cost
conversion cost
freshness
```

---

# 89. Production Case Study

## Retail Platform

A retail platform receives:

- millions of order events;
- frequent operational updates;
- daily analytical reporting;
- customer-level point lookups;
- large historical scans.

The architecture question is:

> **Where could row-oriented storage make sense, where could columnar storage make sense, and why might both exist?**

---

## Step 1 — Identify the workloads

We have at least four access patterns:

```text
1. frequent operational updates
2. point lookup by order/customer
3. daily analytics
4. historical large scans
```

These are not the same workload.

---

## Step 2 — Map the access patterns

```text
Operational update
    ↓
complete or targeted records
    ↓
row-oriented candidate

Point lookup
    ↓
few records, many fields
    ↓
row-oriented candidate

Historical aggregation
    ↓
many rows, selected columns
    ↓
columnar candidate

Reporting
    ↓
large scans of dimensions/measures
    ↓
columnar candidate
```

---

## Step 3 — Consider a hybrid architecture

Conceptually:

```text
Operational source
      ↓
row-oriented transaction system
      ↓
ingestion/event boundary
      ↓
batch / stream transformation
      ↓
columnar analytical lake
      ↓
BI / reporting / analytics
```

This is not a mandatory architecture.

It is one example of matching physical representations to different workloads.

---

## Step 4 — Identify the trade-offs

A hybrid design can improve workload fit, but may add:

```text
more storage
more pipelines
more transformations
more failure points
more schema coordination
```

Therefore the architecture must justify the complexity.

---

## Step 5 — Define the measurements

An architecture review should ask for evidence such as:

```text
point-lookup latency
transaction throughput
analytical query latency
bytes read
storage size
ingestion latency
data freshness
operational cost
```

The senior engineer does not argue from format preference.

The senior engineer connects:

```text
requirement
   ↓
workload
   ↓
physical layout
   ↓
measurement
```

---

# 90. How a Senior Data Engineer Thinks About This Decision

A senior engineer does not begin with:

> "I prefer Parquet."

They begin with:

### Workload

What does the consumer actually do?

```text
scan
lookup
update
aggregate
stream
batch
```

### Access pattern

Does the consumer need:

```text
one record
many records
many columns
few columns
```

### Write pattern

Does the producer write:

```text
one record
micro-batch
hourly batch
daily batch
```

### Data volume

Is this:

```text
10 MB
10 GB
10 TB
1 PB
```

The correct design pressure changes with scale.

### Query selectivity

How much of the dataset does a typical query actually need?

```text
0.01%
10%
80%
100%
```

### Compression characteristics

Ask:

```text
Are values repetitive?
Are columns low-cardinality?
Are values random?
```

### CPU cost

Consider:

```text
parsing
decoding
decompression
aggregation
```

### I/O cost

Consider:

```text
bytes read
bytes transferred
number of physical units touched
```

### Storage cost

Consider:

```text
persistent size
replication
backups
retention
```

### Interoperability

Ask:

```text
Who consumes this data?
Which tools must read it?
Is the format widely supported?
```

### Operational constraints

Consider:

```text
memory
compute
deployment
object storage
failure recovery
reprocessing
```

### Pipeline stage

Ask:

```text
ingestion?
bronze?
silver?
gold?
interchange?
```

---

# 91. How to Defend a Decision in an Architecture Review

A strong architecture-review explanation sounds like this:

> "The workload is primarily large historical scans that usually project 4 of 30 columns and filter by event date. Writes arrive in hourly batches. We therefore evaluated a columnar layout because it aligns with the read and write pattern. We measured file size, filtered-query latency, full-scan latency, and bytes read using the same dataset and query shape. We also measured operational behavior under our memory and storage constraints. The decision is based on those workload-specific measurements rather than a universal assumption about formats."

Notice what is missing:

```text
"Columnar is always faster."
```

The reasoning is:

```text
workload
+
measurements
+
constraints
=
defensible design
```

---

# 92. What to Say When Someone Says "Just Use Parquet"

A useful response is not:

> "Parquet is bad."

Nor is it:

> "Parquet is always right."

Instead ask:

```text
What is the workload?
What is the write pattern?
What are the consumers?
What columns are typically read?
What is the dataset size?
What latency is required?
What storage system are we using?
What do our measurements show?
```

Parquet may turn out to be appropriate.

But the decision should follow the workload.

---

# 93. Architecture Review Template

When presenting a row-vs-column layout decision, write down:

```text
Dataset:
  __________________________

Primary consumers:
  __________________________

Read pattern:
  __________________________

Write pattern:
  __________________________

Typical query:
  __________________________

Typical columns used:
  __________________________

Dataset size:
  __________________________

Growth rate:
  __________________________

Candidate layout:
  __________________________

Expected benefit:
  __________________________

Expected cost:
  __________________________

Measurements:
  __________________________

Operational constraints:
  __________________________

Final decision:
  __________________________

Why:
  __________________________
```

The goal is traceability.

---

# 94. Interview Questions

## Basic

### 1. What is row-oriented storage?

**Model answer:** Row-oriented storage keeps the fields belonging to the same record physically close together. It naturally fits workloads that read or write complete records.

### 2. What is columnar storage?

**Model answer:** Columnar storage keeps values from the same column physically close together. It naturally fits workloads that scan many rows while using a subset of columns.

### 3. Why is columnar storage useful for analytics?

**Model answer:** Analytical queries often scan many rows but need only a few columns. Columnar organization can enable column pruning and can create strong compression opportunities.

---

## Intermediate

### 4. Why can columnar storage compress well?

**Model answer:** Values from the same column are physically close, so repeated and similar values are grouped together. This can create opportunities for dictionary encoding, run-length encoding, and general compression.

### 5. What is column pruning?

**Model answer:** Column pruning means reading only the columns required by a query instead of reading every column in the dataset.

### 6. What is predicate skipping?

**Model answer:** Predicate skipping uses metadata about a physical block, such as min/max values, to determine that the block cannot satisfy a filter and can therefore be skipped.

### 7. Why can columnar storage have write-side trade-offs?

**Model answer:** Efficient columnar files often benefit from batching and organizing values into column-oriented physical structures. Frequent tiny writes and record-level updates can therefore be a poor physical match and may cause buffering, rewrite, or small-file costs.

### 8. Is text always worse than binary?

**Model answer:** No. Text can be easier to inspect, debug, and exchange. Binary formats can provide stronger typing and more efficient machine representation. The correct choice depends on the workload and operational requirements.

---

## Advanced

### 9. What is PAX?

**Model answer:** PAX, or Partition Attributes Across, is a hybrid layout that groups rows into blocks and organizes column values within each block.

### 10. Why are Parquet row groups conceptually related to PAX?

**Model answer:** Both use a bounded group of rows as a physical unit while organizing columns within that unit. They are conceptually related, although Parquet row groups are not identical to every PAX implementation.

### 11. What is splittability?

**Model answer:** Splittability is the ability to divide a large file into independently readable portions so multiple workers can process different parts in parallel.

### 12. Why does splittability matter in distributed processing?

**Model answer:** Splittability allows large data to be divided among workers. That can improve parallelism and reduce the amount of work assigned to any one worker, subject to coordination and resource constraints.

### 13. Why might a production architecture use both row and columnar representations?

**Model answer:** Different pipeline stages may have different workloads. Operational systems and event movement can favor record-oriented access, while analytical storage often benefits from column-oriented scans. A hybrid architecture can match each representation to its workload.

---

## Senior / Architecture

### 14. How would you choose row vs columnar storage for a new dataset?

**Model answer:** Start with workload characterization: read pattern, write pattern, row count, growth rate, typical columns used, query selectivity, latency requirements, and consumers. Select candidate layouts, benchmark the real workload under a controlled environment, evaluate operational constraints, and then choose based on evidence.

### 15. What measurements would you collect before standardizing a format?

**Model answer:** At minimum, measure physical size, write time, full-read time, selective-read time, bytes read where available, memory usage, and behavior under representative cache conditions. Also measure workload-specific latency and operational cost.

### 16. How would you defend the decision during an architecture review?

**Model answer:** Explain the workload, show the candidate layouts considered, describe the benchmark methodology, present measured results, state operational constraints, and explain why the chosen design fits those requirements. Avoid universal claims.

---

# 95. Additional Understanding Checks

Answer these without looking back.

### Question 1

A query reads 3 columns from a 50-column dataset. Why might columnar storage reduce physical work?

### Question 2

A system updates one record every few milliseconds. Why might an optimized analytical columnar file be an awkward write target?

### Question 3

What is the difference between:

```text
encoding
```

and:

```text
compression
```

### Question 4

Why can sorting improve the usefulness of min/max statistics?

### Question 5

What does "splittable" mean for a large file?

### Question 6

Why is a single `.csv.gz` file different from a structured analytical file containing compressed internal blocks?

### Question 7

Why can CSV be useful even when it is not the most compact analytical representation?

### Question 8

Why can a dataset legitimately have a row-oriented representation in one stage and a columnar representation in another?

---

# 96. Answers to the Additional Checks

### Answer 1

Because values from the needed columns can be stored separately from unrelated columns, creating an opportunity to avoid reading unnecessary columns.

### Answer 2

Because the file is designed around batch-oriented physical organization rather than arbitrary record-at-a-time mutation. Frequent tiny writes can create buffering, rewrite, and small-file costs.

### Answer 3

Encoding changes the representation of values to exploit structure. Compression further reduces the byte representation.

### Answer 4

Sorting can make each physical block cover a narrower range of values, making it easier to prove that some blocks cannot match a filter.

### Answer 5

It means a large file can be divided into independently readable portions that multiple workers can process in parallel.

### Answer 6

A single gzip stream is difficult to start decoding independently at arbitrary compressed offsets. A structured format may organize compression into independently readable internal units.

### Answer 7

CSV is readable, easy to inspect, broadly interoperable, and useful at data boundaries even when it has parsing and typing costs.

### Answer 8

Because pipeline stages can have different workloads. Ingestion may need record-oriented movement while analytical storage may need large columnar scans.

---

# 97. Checkpoint

You are ready to move on when you can do all of the following without reading your notes.

- [ ] Explain row vs columnar storage with a diagram.
- [ ] Explain why columnar files can compress better.
- [ ] Explain PAX and why Parquet row groups are conceptually related to it.
- [ ] Define splittability and give an example of a non-splittable file.
- [ ] Choose a layout for three workloads and justify each.
- [ ] Explain column pruning.
- [ ] Explain predicate skipping at a conceptual level.
- [ ] Explain why record-at-a-time updates can be awkward for columnar files.
- [ ] Distinguish text vs binary representation.
- [ ] Distinguish embedded schema from externally managed schema.
- [ ] Explain why row and columnar formats can coexist in one architecture.
- [ ] Design a fair first-pass format experiment.

## Practical test

Draw these three diagrams from memory:

### Diagram 1 — Row

```text
R1: [A][B][C][D]
R2: [A][B][C][D]
R3: [A][B][C][D]
```

### Diagram 2 — Column

```text
A: [A][A][A]
B: [B][B][B]
C: [C][C][C]
D: [D][D][D]
```

### Diagram 3 — PAX / hybrid

```text
Block 1
  A: [...]
  B: [...]
  C: [...]
  D: [...]

Block 2
  A: [...]
  B: [...]
  C: [...]
  D: [...]
```

Then explain, in your own words:

```text
What bytes are next to what bytes?
Why does that matter for this workload?
```

---

# 98. Final Review

## Final Mental Model

Use this framework:

```text
Logical table
      ↓
Physical layout
      ↓
What bytes sit next to what bytes?
      ↓
What does the workload need?
      ↓
How much data must be read?
      ↓
How well can the data be encoded/compressed?
      ↓
How efficiently can it be written?
      ↓
How easily can it be processed in parallel?
      ↓
Choose layout based on workload
```

The most important shift in thinking is:

```text
Do not start with the file format.
Start with the workload.
```

---

# 99. Remember This

## Principle 1 — A logical table is not a physical layout

The same:

```text
row 1
row 2
row 3
```

can be physically organized in very different ways.

---

## Principle 2 — Row orientation favors record locality

Think:

```text
"Give me the whole record."
```

Typical examples:

```text
transaction processing
point lookups
record-oriented ingestion
messaging
```

---

## Principle 3 — Column orientation favors column locality

Think:

```text
"Scan many rows, but only these few columns."
```

Typical examples:

```text
analytical aggregation
reporting
historical scans
batch transformations
```

---

## Principle 4 — Columnar is not universally better

A physical layout is good when it fits its workload.

---

## Principle 5 — Compression benefits from locality

Similar values physically close together create better opportunities for:

```text
dictionary encoding
run-length encoding
compression
```

---

## Principle 6 — Column pruning reduces unnecessary reads

If a query needs:

```text
country
amount
```

a suitable columnar layout gives the engine an opportunity to avoid unrelated columns.

---

## Principle 7 — Predicate skipping reduces unnecessary block reads

If a block's value range proves that a filter cannot match, the block can potentially be skipped.

---

## Principle 8 — Columnar writes are optimized around batches

This does not mean columnar storage cannot be written efficiently.

It means:

```text
batch-oriented writes
```

are usually a more natural physical fit than:

```text
arbitrary record-at-a-time updates
```

---

## Principle 9 — Text vs binary is a separate dimension

Ask both:

```text
row or column?
```

and:

```text
text or binary?
```

Then consider:

```text
schema
compression
encoding
splittability
workload
```

---

## Principle 10 — PAX is the hybrid mental model

Think:

```text
rows grouped into blocks
+
columns organized within each block
```

This gives useful intuition for modern analytical file structures such as Parquet row groups and ORC stripes.

---

## Principle 11 — Splittability is about parallel processing

Do not assume:

```text
compressed = not splittable
```

Instead ask:

```text
How does the file/container organize independently readable compressed units?
```

---

## Principle 12 — Production layouts are workload decisions

A defensible Data Engineering decision looks like:

```text
Requirements
     ↓
Workload characterization
     ↓
Candidate layouts
     ↓
Fair benchmark
     ↓
Operational evaluation
     ↓
Decision
```

Not:

```text
"We always use X."
```

---

# 100. Production Application

When you encounter a new dataset at work, ask these questions before choosing a physical layout:

```text
1. Who writes this data?
2. How frequently is it written?
3. Does the writer send one record or a batch?
4. Who reads it?
5. Do readers want complete records or a few columns?
6. Is the workload point lookup or large scan?
7. How large is the dataset?
8. How quickly will it grow?
9. Which values repeat?
10. Is compression important?
11. Is parallel processing important?
12. Does the format need to be human-readable?
13. Does the file need to carry its own schema?
14. Will the data be used for analytics, ingestion, interchange, or more than one purpose?
15. What measurements will prove the design works?
```

If you can answer those questions clearly, you are no longer choosing a format by habit.

You are making a physical data-layout decision.

---

# 101. Where This Topic Leads Next

This topic gives you the conceptual lens for the remaining parts of Module 2.5.

Next:

```text
Topic 02
Parquet internals
```

You will take the physical-layout ideas from this chapter and examine:

```text
row groups
column chunks
pages
statistics
encodings
footer
```

Then:

```text
Topic 03
PyArrow Parquet
```

You will learn how to control those physical choices from Python.

Later topics will extend the same mental model to:

```text
Avro
ORC
nested data
compression
partitioning
file sizing
legacy ingestion
```

Keep the same question throughout:

> **What physical arrangement of data best matches the workload?**
