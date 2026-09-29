# Parquet Internals — Row Groups, Pages, and Statistics

> **Stage 2 → Python for Data Engineering → Module 2.5 → Phase B → Topic 02**

## Learning Objectives

By the end of this module, you should be able to:

- draw the high-level physical structure of a Parquet file
- explain `PAR1`, row groups, column chunks, pages, and the footer
- explain why metadata is written at the end and read before most data
- distinguish physical types from logical types
- explain dictionary pages, data pages, and data page v1/v2 at a high level
- explain `PLAIN`, dictionary / `RLE_DICTIONARY`, `RLE`, bit-packing, delta encodings, and `BYTE_STREAM_SPLIT`
- explain dictionary fallback and distinguish encoding from compression
- explain `min`, `max`, and `null_count` statistics and row-group skipping
- explain why sort order changes the usefulness of statistics
- explain page indexes, column indexes, offset indexes, and bloom filters
- understand nested data using definition and repetition levels
- understand timestamp units, `isAdjustedToUTC`, and legacy `INT96`
- understand decimal precision/scale, unsigned-integer considerations, and string-statistics truncation
- understand format evolution, reader compatibility, Variant awareness, and modular encryption awareness
- inspect real Parquet metadata with PyArrow and DuckDB
- compare random and sorted datasets and measure pruning behavior
- debug misleading Parquet observations
- reason about Parquet design in production architecture reviews

> **Core mental model:** A Parquet file is a physical storage structure designed so readers can understand the file and, when possible, avoid reading irrelevant data.

## Prerequisites

You should already understand:

- bytes and storage
- files and file paths
- RAM versus persistent storage
- basic CSV and JSON
- basic OLTP versus OLAP concepts
- the row-oriented versus columnar storage mental model from Topic 01

This topic focuses on Parquet internals. It does not re-teach the earlier topics in full.

---

# 1. The Physical Model First

Start with a normal logical table:

```text
+----------+----------+---------+--------+
| order_id | customer | country | amount |
+----------+----------+---------+--------+
| 1        | Alice    | IN      | 100    |
| 2        | Bob      | US      | 250    |
| 3        | Carol    | IN      | 180    |
| 4        | David    | UK      | 120    |
| 5        | Eve      | IN      | 300    |
| 6        | Frank    | US      | 220    |
+----------+----------+---------+--------+
```

A conceptual Parquet layout is:

```text
Parquet File
│
├── Row Group 0
│   ├── Column Chunk: order_id
│   │   ├── Page
│   │   └── Page
│   ├── Column Chunk: customer
│   │   ├── Page
│   │   └── Page
│   ├── Column Chunk: country
│   │   ├── Page
│   │   └── Page
│   └── Column Chunk: amount
│       ├── Page
│       └── Page
│
├── Row Group 1
│   ├── Column Chunk: order_id
│   ├── Column Chunk: customer
│   ├── Column Chunk: country
│   └── Column Chunk: amount
│
└── Footer
```

The hierarchy to remember is:

```text
Row group
    ↓
Column chunk
    ↓
Pages
```

A **row group** is a subset of rows.

A **column chunk** is one column inside one row group.

A **page** is a smaller storage unit inside a column chunk.

Keep those three concepts separate.

---

# 2. Complete Parquet File Structure

At a high level, a Parquet file has this shape:

```text
BEGINNING
┌──────────────────────────────────────────────────────┐
│ PAR1                                                 │
├──────────────────────────────────────────────────────┤
│ Row Group 0                                          │
│   ├── Column Chunks                                  │
│   │    └── Pages                                     │
│   └── ...                                            │
│                                                      │
│ Row Group 1                                          │
│   ├── Column Chunks                                  │
│   └── ...                                            │
│                                                      │
│ More row groups                                      │
├──────────────────────────────────────────────────────┤
│ File Metadata / Footer                               │
├──────────────────────────────────────────────────────┤
│ Metadata length                                      │
├──────────────────────────────────────────────────────┤
│ PAR1                                                 │
└──────────────────────────────────────────────────────┘
END
```

The physical model is:

```text
Logical Table
      ↓
Parquet File
      ↓
Row Groups
      ↓
Column Chunks
      ↓
Pages
      ↓
Encoding
      ↓
Compression
      ↓
Bytes on Storage
```

The metadata path is separate:

```text
Parquet File
      ↓
Footer
      ↓
Schema + Row-group / Column-chunk Metadata
      ↓
Statistics / Encodings / Locations / Index Information
      ↓
Reader decides what to read
```

This separation is fundamental to Parquet's design.

---

# 3. Why the Footer Is at the End

A writer often streams data forward.

At the start, it may not know the final:

- number of row groups
- compressed sizes
- page and chunk offsets
- complete metadata structure

So the writer can conceptually do:

```text
write data
   ↓
collect metadata while writing
   ↓
finish data
   ↓
write metadata/footer
```

The reader then works in the opposite direction:

```text
open file
   ↓
seek near the end
   ↓
read footer
   ↓
understand structure
   ↓
choose relevant columns / row groups / pages
   ↓
read required data
```

This supports single-pass writing and avoids requiring a reader to scan all data just to discover where the interesting data is.

The Parquet specification describes the file metadata as being written after the data so writers can write in a single pass, and readers are expected to read the metadata first to locate the column chunks they need.

---

# 4. What Is `PAR1`?

`PAR1` is the four-byte magic signature associated with the Parquet file format.

A beginner-friendly check:

```python
with open("orders.parquet", "rb") as f:
    start = f.read(4)

print(start)
```

Conceptually, for a valid Parquet file, you expect:

```text
b'PAR1'
```

You can also inspect the final four bytes:

```python
from pathlib import Path

path = Path("orders.parquet")

with path.open("rb") as f:
    f.seek(-4, 2)
    end = f.read(4)

print(end)
```

### Why magic bytes exist

A file signature helps tools identify the expected format.

It does **not** prove that the file is:

- semantically correct
- complete
- readable by every engine
- safe to process

Treat it as format identification, not full validation.

---

# 5. Row Groups

A row group is a horizontal subset of rows.

Imagine:

```text
1,000,000 orders
```

The file could be organized conceptually as:

```text
Row Group 0 → rows 1–100,000
Row Group 1 → rows 100,001–200,000
Row Group 2 → rows 200,001–300,000
...
```

The exact row-group size is a writer/layout decision.

## Why row groups exist

They create a practical unit for:

- selective reading
- statistics
- parallel work
- memory management
- data skipping

Suppose:

```text
Row Group 0
created_at = January

Row Group 1
created_at = February

Row Group 2
created_at = March
```

A March-only query may have evidence that the first two row groups cannot match.

The important word is **may**.

Metadata gives the engine information it can use. It does not guarantee a particular execution plan.

---

# 6. Column Chunks

A column chunk is one column inside one row group.

For:

```text
order_id
customer
country
amount
```

Row Group 0 conceptually contains:

```text
Row Group 0
│
├── order_id column chunk
├── customer column chunk
├── country column chunk
└── amount column chunk
```

The `amount` column chunk contains the `amount` values for rows belonging to Row Group 0.

This is what lets an analytical engine reason about columns independently.

---

# 7. Pages

Column chunks contain pages.

```text
Row Group
    ↓
Column Chunk
    ↓
Page 0
Page 1
Page 2
...
```

A column chunk may contain:

```text
Dictionary Page (optional)
Data Page
Data Page
Data Page
...
```

The pages are stored sequentially within the column chunk.

The Parquet specification describes column chunks as being composed of pages written back-to-back and allows readers to skip pages they do not need.

Why have pages?

Because they create smaller physical units for:

- encoded values
- compression
- reading
- navigation
- page-level metadata

---

# 8. Never Confuse These Four Levels

```text
Logical row
     ↓
Row group
     ↓
Column chunk
     ↓
Page
```

Example:

```text
Row Group 7
│
├── country column chunk
│   ├── page 0
│   ├── page 1
│   └── page 2
│
└── amount column chunk
    ├── page 0
    ├── page 1
    └── page 2
```

A good test is to answer:

> "Where is `amount` for Row Group 7?"

Answer:

```text
Row Group 7
    ↓
amount column chunk
```

Then:

> "Where are the encoded `amount` values inside that chunk?"

Answer:

```text
pages
```

---

# 9. The Footer as the Navigation Map

The footer contains metadata describing the file.

Conceptually it can describe:

- schema
- row count
- row groups
- column chunks
- encodings
- compression
- statistics
- data locations/offsets
- additional metadata

Think of it as a map:

```text
                         FOOTER
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
        Schema          Row groups        Other metadata
                            │
                       Column chunks
                            │
                         Locations
                            │
                        Statistics
```

The footer is powerful because a reader can use it to decide what **not** to read.

---

# 10. Query Planning Mental Model

Consider:

```sql
SELECT country, SUM(amount)
FROM orders
WHERE created_at >= DATE '2025-03-01'
GROUP BY country;
```

The physical reasoning is:

```text
Read footer
   ↓
Understand schema
   ↓
Need:
    country
    amount
    created_at
   ↓
Inspect row-group statistics for created_at
   ↓
Skip groups that cannot match
   ↓
Read relevant column chunks/pages
   ↓
Decode
   ↓
Decompress
   ↓
Execute aggregation
```

This is the foundational idea behind analytical data skipping.

---

# 11. Connection to Topic 01 — PAX and Hybrid Thinking

Topic 01 introduced the difference between:

```text
row-oriented storage
```

and:

```text
column-oriented storage
```

It also introduced **PAX**, a hybrid organization:

> **PAX (Partition Attributes Across) groups rows into blocks, then organizes the attributes/columns separately inside each block.**

Conceptually:

```text
Pure row-oriented

Row 1: A1 B1 C1 D1
Row 2: A2 B2 C2 D2
Row 3: A3 B3 C3 D3
```

versus:

```text
Pure column-oriented

A: A1 A2 A3
B: B1 B2 B3
C: C1 C2 C3
D: D1 D2 D3
```

and the PAX-style hybrid:

```text
Block 0
    A: A1 A2
    B: B1 B2
    C: C1 C2
    D: D1 D2

Block 1
    A: A3 A4
    B: B3 B4
    C: C3 C4
    D: D3 D4
```

Why is this useful?

It provides two kinds of locality:

```text
within a block:
    columns are organized together
```

while still keeping:

```text
different blocks
    → separate units of work
```

Parquet's **row groups are conceptually related to this hybrid idea**:

```text
Row Group
    ↓
multiple rows in one physical region
    ↓
one column chunk per column
    ↓
pages inside each chunk
```

ORC stripes are conceptually similar in that they also represent larger horizontal groups containing column-oriented data structures.

Do not treat these as byte-for-byte identical implementations of PAX. The useful connection is architectural:

```text
hybrid block
    ↓
row-group locality
    +
column locality
```

This connection helps explain why modern analytical formats can simultaneously support:

- large-scan parallelism
- column-oriented access
- statistics at a useful block granularity
- finer-grained page processing

---

# 12. Physical Types vs Logical Types

A physical type answers:

> "How are the values represented at the low level?"

A logical type answers:

> "What do those values mean?"

Required physical types include:

- `BOOLEAN`
- `INT32`
- `INT64`
- `FLOAT`
- `DOUBLE`
- `BYTE_ARRAY`
- `FIXED_LEN_BYTE_ARRAY`

Common logical types include:

- `STRING`
- `DATE`
- `TIMESTAMP`
- `DECIMAL`
- `UUID`

The key equation is:

```text
physical representation ≠ semantic meaning
```

For example:

```text
INT64 + TIMESTAMP semantics
```

is not semantically equivalent to:

```text
INT64 + customer_id semantics
```

The physical carrier can be similar while the meaning differs.

---

# 12. Why Physical vs Logical Type Matters

Suppose:

```text
INT32
```

appears in metadata.

It does not necessarily mean:

```text
"this is an ordinary integer."
```

It could carry logical date semantics.

Similarly:

```text
BYTE_ARRAY
```

does not automatically mean:

```text
"arbitrary text."
```

The schema tells the reader how to interpret it.

This matters for:

- interoperability
- type correctness
- query semantics
- Python/Java/SQL conversions
- migration
- downstream processing

---

# 13. Dictionary Pages

Dictionary encoding stores distinct values once in a dictionary page and refers to them using compact indexes in data pages.

Example:

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
Dictionary

0 → IN
1 → US
2 → UK
```

Data-page indexes:

```text
0, 0, 1, 0, 2, 0, 1
```

This is a teaching illustration, not a byte-for-byte file dump.

The dictionary page belongs to the column chunk and is written before the data pages when dictionary encoding is used.

---

# 14. Why Dictionary Encoding Helps

Suppose:

```text
status

PAID
PAID
PAID
PAID
FAILED
PAID
PENDING
PAID
```

There are relatively few distinct values.

A dictionary can be:

```text
0 → PAID
1 → FAILED
2 → PENDING
```

The repeated strings no longer need to be independently represented in the conceptual encoded sequence.

Potential benefits:

- reduced encoded representation
- less repeated byte content
- better input for later compression

---

# 15. Dictionary Fallback

Dictionary encoding is not automatically beneficial for every column.

Compare:

```text
status:
PAID
PAID
PAID
FAILED
PAID
```

with:

```text
unique_id:
a8f1...
91bc...
27aa...
6c02...
...
```

For a high-cardinality column, the dictionary can grow substantially.

Conceptually:

```text
many repeated values
       ↓
small dictionary
       ↓
dictionary encoding can work well

many unique values
       ↓
large dictionary
       ↓
benefit decreases
       ↓
writer may fall back
```

Parquet permits dictionary encoding to fall back to plain encoding when the dictionary becomes too large or otherwise inefficient. The exact threshold is implementation-dependent.

Do not memorize a single universal dictionary-size threshold.

The engineering skill is to inspect:

```python
column.encodings
```

and understand the data distribution.

---

# 16. Data Page v1 vs v2

You should recognize:

```text
DATA_PAGE_V1
DATA_PAGE_V2
```

The important learning goal is conceptual.

Data page v1 is the original page representation.

Data page v2 reorganizes the level/value portions so that their handling is more explicit and can support different compression treatment.

You do not need to memorize every byte field to understand the system.

Remember:

```text
page version
    ↓
implementation / compatibility detail
```

not:

```text
page v2 = universally faster
```

Always verify reader support when compatibility matters.

---

# 17. Data Pages and Their Logical Pieces

At a useful conceptual level, a data page can contain:

```text
Data Page
│
├── Repetition level data (when needed)
├── Definition level data (when needed)
└── Encoded values
```

The Parquet specification states that data-page contents are organized around repetition levels, definition levels, and encoded values, with repetition/definition sections omitted when the schema makes them unnecessary.

For a simple required flat column:

```text
order_id: required INT64
```

the page can conceptually need only:

```text
encoded order_id values
```

There is no need to repeatedly encode structure that the schema already proves.

---

# 18. Encodings

Encoding changes how values are represented before general-purpose compression.

The roadmap requires:

- `PLAIN`
- dictionary encoding / `RLE_DICTIONARY`
- `RLE`
- bit-packing
- `DELTA_BINARY_PACKED`
- `DELTA_BYTE_ARRAY`
- `BYTE_STREAM_SPLIT`

A useful mental pipeline is:

```text
Logical values
      ↓
Encoding
      ↓
Encoded representation
      ↓
Compression
      ↓
Bytes on disk
```

Encoding and compression are not the same thing.

---

# 19. `PLAIN` Encoding

`PLAIN` is a direct baseline representation.

Conceptually:

```text
10
20
30
40
```

remain represented according to their physical type without using a specialized dictionary/delta representation.

Why does a baseline matter?

Because not every dataset has structure that makes a specialized encoding worthwhile.

It can also serve as a fallback representation.

The exact byte representation depends on the physical type and specification.

---

# 20. RLE and Bit-Packing

### Run-Length Encoding

Suppose:

```text
IN IN IN IN IN US US
```

A conceptual run-length form is:

```text
IN × 5
US × 2
```

The repeated value and run length communicate the same logical sequence more compactly.

### Bit-Packing

If a value can only be:

```text
0, 1, 2, 3
```

then two bits can represent every value:

```text
0 → 00
1 → 01
2 → 10
3 → 11
```

Parquet uses the RLE/bit-packing hybrid encoding in important contexts such as:

- repetition levels
- definition levels
- dictionary indexes
- relevant boolean page values

This is why the name:

```text
RLE / Bit-Packing Hybrid
```

is more accurate than thinking of RLE alone.

---

# 21. `DELTA_BINARY_PACKED`

Delta encoding represents differences between consecutive numeric values.

Example:

```text
100
101
102
103
104
```

becomes conceptually:

```text
100
+1
+1
+1
+1
```

The deltas are small and repetitive.

It can be useful for values such as:

- sorted integers
- counters
- regular timestamps
- monotonically increasing identifiers

Random values may provide less structure.

The encoding is defined for `INT32` and `INT64`.

---

# 22. `DELTA_BYTE_ARRAY`

This encoding can exploit common prefixes between adjacent byte-array values.

Consider:

```text
customer_000001
customer_000002
customer_000003
customer_000004
```

Large portions are shared.

A useful conceptual representation is:

```text
first value
shared prefix + changing suffix
shared prefix + changing suffix
...
```

This is especially relevant when values with similar prefixes are adjacent.

Ordering can therefore affect more than statistics; it can also expose patterns useful to encodings and later compression.

---

# 23. `BYTE_STREAM_SPLIT`

`BYTE_STREAM_SPLIT` rearranges bytes of fixed-width values into separate streams.

Conceptually:

```text
A: A1 A2 A3 A4
B: B1 B2 B3 B4
C: C1 C2 C3 C4
D: D1 D2 D3 D4
```

can become:

```text
Stream 1: A1 B1 C1 D1
Stream 2: A2 B2 C2 D2
Stream 3: A3 B3 C3 D3
Stream 4: A4 B4 C4 D4
```

The goal is to expose byte-level patterns that may compress better.

The important lesson:

> Some encodings transform the data representation to make regularity easier for compression to exploit.

Do not treat this as a universal requirement for floating-point columns.

---

# 24. Encoding vs Compression — The Critical Distinction

Remember this diagram:

```text
Logical values
      ↓
   Encoding
      ↓
Encoded values
      ↓
 Compression
      ↓
Final page bytes
```

Encoding examples:

```text
dictionary
RLE
delta
byte-stream split
```

Compression codecs are a different category.

Examples from later topics include:

```text
Snappy
GZIP
Zstandard
LZ4
```

A good mental sentence is:

> **Encoding changes the representation; compression reduces the size of that representation.**

Both can contribute to the final file size.

The detailed codec trade-offs belong to Topic 07.

---

# 25. Row-Group Statistics

Row-group statistics summarize values in a column chunk.

Common statistics include:

- `min`
- `max`
- `null_count`

Example:

```text
Row Group 0

created_at:
    min = 2025-01-01
    max = 2025-01-31
    null_count = 0
```

These statistics give the query engine evidence about the values stored in that row group.

---

# 26. Predicate Skipping

Suppose:

```text
Row Group 0
created_at:
    min = 2025-01-01
    max = 2025-01-31

Row Group 1
created_at:
    min = 2025-02-01
    max = 2025-02-28

Row Group 2
created_at:
    min = 2025-03-01
    max = 2025-03-31
```

Query:

```sql
WHERE created_at >= DATE '2025-03-01'
```

The engine can reason:

```text
Row Group 0
Jan only
→ cannot match
→ candidate for skipping

Row Group 1
Feb only
→ cannot match
→ candidate for skipping

Row Group 2
March
→ can match
→ inspect
```

The key concept is:

```text
Can this region possibly satisfy the predicate?

NO
→ skip

YES / UNKNOWN
→ inspect
```

This is the conceptual foundation of row-group pruning.

---

# 27. `min`, `max`, and `null_count`

### `min`

Smallest relevant value according to the statistic's semantics.

### `max`

Largest relevant value according to the statistic's semantics.

### `null_count`

Number of null values represented by the statistic.

These are metadata.

They are not a second copy of the complete column.

A useful production question is:

> "How much work can this metadata safely eliminate?"

---

# 28. Statistics Are Evidence, Not a Guarantee

Do not conclude:

```text
Statistics exist
→ query will be fast
```

Instead:

```text
Statistics exist
→ engine has metadata it may use
```

For skipping to be effective, the metadata must be selective enough.

Consider:

```text
min = 1
max = 1,000,000,000
```

for every row group.

A predicate:

```text
value = 50,000
```

cannot be rejected using only that range.

The statistics are valid but not very useful for elimination.

---

# 29. Column Pruning vs Predicate Skipping

Keep these distinct:

```text
Column pruning
    ↓
avoid unused columns

Predicate skipping
    ↓
avoid irrelevant row groups/pages
```

Example query:

```sql
SELECT country, SUM(amount)
FROM orders
WHERE created_at >= DATE '2025-03-01'
GROUP BY country;
```

Potentially needed columns:

```text
country
amount
created_at
```

Potentially skipped columns:

```text
customer
address
campaign
...
```

And potentially skipped row groups:

```text
groups whose created_at range cannot match
```

These mechanisms can work together.

---

# 30. Sorting and Statistics

Now compare two physical layouts containing the same logical data.

## Random order

```text
Row Group 0:

Jan
Mar
Feb
Dec
Apr
...
```

Statistics could be:

```text
min = Jan
max = Dec
```

The range is broad.

## Sorted by `created_at`

```text
Row Group 0
January

Row Group 1
February

Row Group 2
March
```

The ranges can become much tighter.

That makes date predicates more selective.

---

# 31. Why Sorting Can Dramatically Change Skipping

The relationship is:

```text
Sort order
     ↓
Value locality
     ↓
Tighter row-group ranges
     ↓
More selective min/max statistics
     ↓
More possible pruning
```

The critical statement is:

> **Statistics are useful when they allow the engine to eliminate data.**

Sorting does not automatically improve every query.

If most queries filter by:

```text
customer_id
```

but the data is sorted by:

```text
created_at
```

then the timestamp ordering may be less helpful for those customer filters.

Sorting is a physical optimization decision, not a universal rule.

---

# 32. Page Indexes

Row-group statistics are coarse.

A row group can contain many pages.

A page index provides finer-grained page-level information.

Conceptually:

```text
Row Group
    ↓
Column Chunk
    ↓
Page 1
Page 2
Page 3
Page 4
```

Row-group statistics might say:

```text
whole row group = 1–1,000,000
```

A page index might say:

```text
Page 1 = 1–100,000
Page 2 = 100,001–200,000
...
```

A selective predicate may therefore eliminate pages even when the row group itself cannot be eliminated.

Page indexes are optional.

---

# 33. Column Index

The column index provides page-level metadata useful for judging whether a page may contain matching values.

Conceptually:

```text
Column Chunk: created_at

Page 1
min = Jan 01
max = Jan 07

Page 2
min = Jan 08
max = Jan 15

Page 3
min = Feb 01
max = Feb 07
```

A query for March may have evidence to skip all these pages.

The exact specification has more detail than this conceptual model.

---

# 34. Offset Index

The offset index is about navigating to pages.

Think:

```text
Column Index
    ↓
"What values/ranges are associated with this page?"

Offset Index
    ↓
"Where is this page, and how do I reach it?"
```

The Parquet specification describes the offset index as supporting navigation by row index and enabling readers to locate corresponding positions across columns when some pages are skipped.

The distinction is:

```text
ColumnIndex → page-level value metadata
OffsetIndex → page location/navigation metadata
```

---

# 35. Page Index Mental Model

```text
Row Group
│
└── Column Chunk
    │
    ├── Page 1 → values A–F
    ├── Page 2 → values G–L
    ├── Page 3 → values M–R
    └── Page 4 → values S–Z
```

Then:

```text
Row-group statistics
    ↓
coarse elimination

Page index
    ↓
fine-grained page elimination
```

A file may have row-group statistics without having a page index.

Do not assume optional features are always present.

---

# 36. Bloom Filters

A bloom filter is a probabilistic membership structure.

It answers a question like:

> "Could this value be present?"

Example:

```sql
WHERE customer_id = 'C12345'
```

Conceptually:

```text
Bloom filter
     │
     ├── definitely absent
     │       ↓
     │      skip
     │
     └── possibly present
             ↓
         inspect actual data
```

A bloom filter can produce false positives:

```text
says "maybe present"
when value is absent
```

That causes extra work.

In the normal conceptual model it avoids false negatives:

```text
it should not say "absent"
when a matching value is actually present
```

---

# 37. Bloom Filters vs Min/Max

Think:

```text
Min / Max
    ↓
range reasoning

Bloom filter
    ↓
membership/equality reasoning
```

Example:

```sql
WHERE amount >= 1000
```

naturally aligns with range statistics.

Example:

```sql
WHERE customer_id = 'C12345'
```

can naturally benefit from membership information.

Bloom filters do not replace min/max statistics.

---

# 38. Nested Data — Why Special Metadata Is Needed

Consider:

```json
{
  "order_id": 101,
  "customer": {
    "name": "Alice"
  },
  "items": [
    {"sku": "A", "qty": 2},
    {"sku": "B", "qty": 1}
  ]
}
```

The leaf values might include:

```text
order_id:
101

customer.name:
Alice

items.sku:
A
B

items.qty:
2
1
```

But simply storing:

```text
A
B
```

does not tell the decoder everything it needs to reconstruct:

```text
both belong to Order 101
```

Nested structures therefore need structural information.

Two core concepts are:

- definition levels
- repetition levels

---

# 39. Definition Levels — Intuition

A definition level answers a question similar to:

> **How deeply defined/present is this path in the nested schema?**

Schema:

```text
customer
└── address
    └── city
```

Consider:

```text
customer exists
address exists
city exists
```

versus:

```text
customer exists
address is null
city cannot exist
```

The physical data must distinguish these states.

Conceptually:

```text
0 → required path not defined
1 → customer exists
2 → address exists
3 → city exists
```

These numbers are illustrative.

The actual level numbers depend on the schema's repetition/optional structure.

---

# 40. Definition Levels and Nullable Flat Columns

Consider a simple flat field:

```text
email: STRING, nullable
```

Values:

```text
alice@example.com
NULL
carol@example.com
NULL
```

The reader must know:

```text
defined
not defined
defined
not defined
```

This is why definition information is conceptually relevant even without deeply nested structures.

For required flat fields, the definition level can be omitted because the schema already tells the reader that every value is defined.

---

# 41. Repetition Levels — Intuition

Repetition levels help represent repeated structures such as lists.

Example:

```text
Order 101
    Item A
    Item B

Order 102
    Item C
```

The reader needs to distinguish:

```text
Item B continues the list belonging to Order 101
```

from:

```text
Item C begins a new order
```

Conceptually:

```text
Order 101
    ├── A
    └── B

Order 102
    └── C
```

Repetition information helps preserve those boundaries.

---

# 42. Definition + Repetition Levels Together

A useful conceptual model is:

```text
Leaf values
    +
Definition levels
    +
Repetition levels
    ↓
reconstruct nested structure
```

Definition answers:

```text
Is the path defined?
```

Repetition answers:

```text
Does this value continue a repeated structure or begin a new repetition?
```

This is the high-level idea behind the Dremel-style nested encoding used by Parquet.

---

# 43. Hand-Drawn Exercise 1 — Nullable Field

Schema:

```text
customer
└── email (optional)
```

Records:

```text
1. email exists
2. email is null
3. email exists
```

### Task

Write:

```text
record 1 → defined
record 2 → not defined
record 3 → defined
```

Then explain:

> Why can a reader reconstruct nullability without storing the literal word `NULL` as a string?

### Answer

Because the physical representation includes structural/definition information that distinguishes a defined value from an absent/null value.

The exact numeric level depends on the schema.

---

# 44. Hand-Drawn Exercise 2 — Repeated List

Schema:

```text
order
└── items (list)
    └── sku
```

Data:

```text
Order 101:
    A
    B

Order 102:
    C
```

### Task

Mark:

```text
A → first item of Order 101
B → another item of Order 101
C → item of new Order 102
```

### Answer

The repetition structure lets the decoder preserve these parent boundaries.

You do not need to memorize numeric repetition levels to understand the architecture.

---

# 45. Hand-Drawn Exercise 3 — Optional Nested Path

Schema:

```text
order
└── customer (optional)
    └── address (optional)
        └── city (optional)
```

Records:

```text
1. customer + address + city
2. customer + address, city null
3. customer null
```

### Solution

```text
Record 1:
customer = yes
address  = yes
city     = yes

Record 2:
customer = yes
address  = yes
city     = no

Record 3:
customer = no
address  = no
city     = no
```

Definition information represents the deepest defined path.

---

# 46. Timestamp Semantics

Parquet timestamps require attention to:

```text
unit
isAdjustedToUTC
```

Common units include:

- milliseconds (`MILLIS`)
- microseconds (`MICROS`)
- nanoseconds (`NANOS`)

A timestamp with an `INT64` carrier is conceptually a count of the selected unit from the Unix epoch.

The important engineering lesson is:

```text
timestamp value
+
timestamp unit
+
semantic interpretation
```

is one data contract.

---

# 47. `isAdjustedToUTC`

When:

```text
isAdjustedToUTC = true
```

the timestamp uses instant semantics normalized to UTC.

Conceptually:

```text
real-world instant
      ↓
UTC-normalized representation
      ↓
integer count since epoch
```

Timezone display information is not retained merely by storing the instant.

When:

```text
isAdjustedToUTC = false
```

the timestamp has local timestamp semantics rather than a unique global instant.

The Parquet specification distinguishes these two cases explicitly.

---

# 48. Why Timestamp Unit Matters

Consider:

```text
2025-01-01 12:00:00.123456
```

With millisecond precision:

```text
.123
```

is representable.

With microsecond precision:

```text
.123456
```

can be represented.

Nanoseconds provide a still finer unit where the supported representation and ecosystem permit it.

Therefore, when debugging timestamp discrepancies, inspect:

```text
physical type
logical type
unit
isAdjustedToUTC
writer
reader
```

Do not assume all systems interpret timestamps identically.

---

# 49. Legacy `INT96`

You may encounter:

```text
INT96
```

in older Parquet data.

This is a legacy timestamp representation frequently encountered in historical Hive/Spark-oriented datasets.

Why does it matter?

Because production data has history.

You may have:

```text
old partitions → INT96
new partitions → modern logical timestamp representation
```

During migration:

1. inspect the physical schema
2. inspect writer metadata where available
3. identify the producing system/version
4. inspect representative values
5. compare reader interpretations
6. test the conversion before bulk rewriting

Do not assume every historical `INT96` file has the same semantic history.

---

# 50. Decimal Precision and Scale

Decimal semantics are important in:

- finance
- billing
- pricing
- accounting
- exact measurements

Example:

```text
12.34
```

has:

```text
precision = 4
scale = 2
```

Precision:

```text
total number of digits
```

Scale:

```text
digits to the right of the decimal point
```

The logical representation matters even when the physical carrier is an integer or fixed-length byte representation.

---

# 51. Decimal Physical Representation

Depending on precision and writer behavior, Parquet decimals can use physical representations such as:

```text
INT32
INT64
FIXED_LEN_BYTE_ARRAY
```

The critical idea is:

```text
logical type:
DECIMAL(precision, scale)

physical carrier:
one supported representation
```

Do not assume every decimal always uses one physical type.

The appropriate representation depends on precision and writer choices.

---

# 52. Unsigned Integers

Signed and unsigned integers have different ranges and semantics.

A producer may represent:

```text
large positive identifier
```

using unsigned semantics while a reader expects a signed integer.

This creates an interoperability problem.

The production question is:

> Do the writer and reader agree on both the physical representation and its logical meaning?

Do not rely on the generic word:

```text
integer
```

as the entire data contract.

---

# 53. String Statistics

String min/max statistics require care.

The metadata does not always have to preserve the full original long string in a form that can be treated as an exact verbatim value.

Conceptually:

```text
very long string value
        ↓
bounded statistic representation
        ↓
min/max metadata
```

Therefore:

```text
stats_max
```

should not automatically be treated as:

```text
the exact full longest original string
```

DuckDB exposes fields such as `min_is_exact` and `max_is_exact`, reinforcing that statistic interpretation matters.

Do not memorize a universal truncation length.

The exact behavior depends on the format semantics and implementation/version.

---

# 54. Format Evolution and Compatibility

Parquet evolves.

You may inspect metadata indicating a **format version** or format-version context such as:

```text
2.6
```

The engineering concern is:

```text
newer writer
    ↓
newer optional feature
    ↓
older reader
```

Does the reader support what the writer emitted?

There are three distinct compatibility questions:

### Format feature compatibility

Can the reader understand the Parquet features used by the file?

### Schema compatibility

Do producer and consumer agree on the dataset's columns/types?

### Logical-type compatibility

Do they agree on what the physical values mean?

Keep these concepts separate.

---

# 55. Variant Awareness

Modern analytical systems increasingly deal with semi-structured data.

A Variant-style type is a concept for representing values with more flexible structure inside analytical systems.

For this chapter, know:

```text
Variant
```

exists because strict flat schemas do not cover every semi-structured workload conveniently.

Do not turn this section into a deep Variant implementation lesson.

That belongs to later topics.

---

# 56. Modular Encryption — Awareness Only

Parquet supports modular encryption.

At a high level:

```text
data pages
dictionary pages
indexes
metadata
footer
```

can have different visibility/encryption treatment depending on the configured mode.

Why it matters here:

```text
reader needs metadata
        ↓
encrypted metadata may require keys
        ↓
query planning/access can change
```

Detailed configuration and security design belong to the later security module.

Do not infer that every Parquet file is encrypted or that encryption always applies to the same modules.

---

# 57. Query Path: Put Everything Together

Use this complete mental model:

```text
Query
  ↓
Read Footer
  ↓
Understand Schema
  ↓
Identify Required Columns
  ↓
Column Pruning
  ↓
Inspect Row-group Statistics
  ↓
Skip Irrelevant Row Groups
  ↓
Inspect Page Index / Bloom Information when available
  ↓
Locate Relevant Pages
  ↓
Read Bytes
  ↓
Decompress
  ↓
Decode
  ↓
Execute Query
```

The actual order of low-level operations is implementation-specific.

This is a conceptual model for reasoning about the reader.

---

# 58. Create a Small Parquet File

Start with a beginner-friendly PyArrow example:

```python
import pyarrow as pa
import pyarrow.parquet as pq

table = pa.table(
    {
        "order_id": [1, 2, 3, 4],
        "country": ["IN", "US", "IN", "UK"],
        "amount": [100.0, 250.0, 180.0, 120.0],
        "customer": ["Alice", "Bob", "Carol", "David"],
    }
)

pq.write_table(
    table,
    "orders.parquet",
)
```

### What happened?

```text
Python values
   ↓
Arrow Table
   ↓
Parquet writer
   ↓
Parquet file
```

The writer chooses physical structures and metadata according to the supplied data and settings.

Now inspect the file instead of guessing.

---

# 59. Inspect With `ParquetFile`

```python
import pyarrow.parquet as pq

pf = pq.ParquetFile("orders.parquet")

print("Rows:", pf.metadata.num_rows)
print("Row groups:", pf.num_row_groups)
print("Arrow schema:")
print(pf.schema_arrow)
```

Current PyArrow exposes `metadata`, `num_row_groups`, `schema`, and `schema_arrow` on `ParquetFile`.

This lets you move from:

```text
logical values
```

to:

```text
physical metadata
```

---

# 60. Inspect Row Groups

```python
import pyarrow.parquet as pq

pf = pq.ParquetFile("orders.parquet")

for row_group_id in range(pf.num_row_groups):
    row_group = pf.metadata.row_group(row_group_id)

    print(f"Row Group: {row_group_id}")
    print(f"Rows: {row_group.num_rows}")
    print(f"Columns: {row_group.num_columns}")
    print(f"Byte size: {row_group.total_byte_size}")
```

This directly demonstrates:

```python
pf.metadata.row_group(...)
```

maps to:

```text
Row group
```

---

# 61. Inspect Column Chunks

```python
import pyarrow.parquet as pq

pf = pq.ParquetFile("orders.parquet")

for row_group_id in range(pf.num_row_groups):
    row_group = pf.metadata.row_group(row_group_id)

    for column_id in range(row_group.num_columns):
        column = row_group.column(column_id)

        print("Path:", column.path_in_schema)
        print("Physical type:", column.physical_type)
        print("Compression:", column.compression)
        print("Encodings:", column.encodings)
        print("Compressed size:", column.total_compressed_size)
        print("Uncompressed size:", column.total_uncompressed_size)
        print()
```

### Why this matters

You are not merely reading rows.

You are inspecting the physical representation.

---

# 62. Inspect Statistics

```python
import pyarrow.parquet as pq

pf = pq.ParquetFile("orders.parquet")

for row_group_id in range(pf.num_row_groups):
    row_group = pf.metadata.row_group(row_group_id)

    for column_id in range(row_group.num_columns):
        column = row_group.column(column_id)

        if not column.is_stats_set:
            continue

        stats = column.statistics

        print("Column:", column.path_in_schema)
        print("Min:", stats.min)
        print("Max:", stats.max)
        print("Null count:", stats.null_count)
```

The important path is:

```text
row group
    ↓
column chunk
    ↓
statistics
```

---

# 63. Inspect Dictionary and Page Index Presence

```python
import pyarrow.parquet as pq

pf = pq.ParquetFile("orders.parquet")

for row_group_id in range(pf.num_row_groups):
    row_group = pf.metadata.row_group(row_group_id)

    for column_id in range(row_group.num_columns):
        column = row_group.column(column_id)

        print(column.path_in_schema)
        print("Dictionary page:", column.has_dictionary_page)
        print("Column index:", column.has_column_index)
        print("Offset index:", column.has_offset_index)
```

These high-level properties are exposed by current PyArrow.

Some lower-level or older APIs do not expose every Parquet feature directly. Inspect the documentation for the installed version rather than assuming every metadata field has a Python property.

---

# 64. Inspect With DuckDB

Run:

```sql
SELECT *
FROM parquet_metadata('orders.parquet');
```

You can also inspect:

```sql
SELECT *
FROM parquet_schema('orders.parquet');
```

and file-level metadata:

```sql
SELECT *
FROM parquet_file_metadata('orders.parquet');
```

DuckDB's metadata functions expose row-group information, statistics, compression, encodings, offsets, and other Parquet metadata.

---

# 65. Targeted DuckDB Metadata Query

Instead of printing everything, select useful fields:

```sql
SELECT
    row_group_id,
    path_in_schema,
    stats_min,
    stats_max,
    stats_null_count,
    compression,
    encodings,
    total_compressed_size,
    total_uncompressed_size,
    data_page_offset,
    dictionary_page_offset
FROM parquet_metadata('orders.parquet')
ORDER BY
    row_group_id,
    path_in_schema;
```

This is often more useful during debugging than a giant metadata dump.

---

# 66. Schema Inspection With DuckDB

```sql
SELECT
    name,
    type,
    repetition_type,
    logical_type,
    precision,
    scale
FROM parquet_schema('orders.parquet');
```

This gives a useful bridge between:

```text
physical schema
```

and:

```text
logical interpretation
```

For query-facing inspection, you can also use:

```sql
DESCRIBE
SELECT *
FROM 'orders.parquet';
```

---

# 67. Required Metadata-Mapping Exercise

Draw:

```text
Parquet file
│
├── Row Groups
│   ├── Column Chunks
│   │   └── Pages
│   └── ...
└── Footer
```

Then inspect a real file and complete:

| Metadata field | Physical concept | Why it matters |
|---|---|---|
| `num_rows` | row/file count | amount of logical data |
| `row_group_id` | row group | identifies a physical block |
| `path_in_schema` | column path | identifies the represented column |
| `compression` | encoded/compressed bytes | storage and CPU trade-off |
| `encodings` | value representation | reveals physical encoding |
| `stats_min` | row-group lower bound | pruning evidence |
| `stats_max` | row-group upper bound | pruning evidence |
| `stats_null_count` | null count | data-quality/statistical information |
| `data_page_offset` | page location | physical navigation |
| `dictionary_page_offset` | dictionary location | dictionary-page navigation |
| `total_compressed_size` | compressed chunk size | storage footprint |
| `total_uncompressed_size` | original encoded-size estimate | compression effectiveness |

### Worked interpretation

```text
stats_min / stats_max
    ↓
row-group metadata
    ↓
possible predicate elimination

compression / encodings
    ↓
column-chunk representation
    ↓
storage + CPU behavior

offsets
    ↓
physical locations
    ↓
reader navigation
```

---

# 68. Required Hands-On Exercise — `parquet_inspector.py`

The roadmap asks for a small CLI named:

```text
parquet_inspector.py
```

Because this lesson is allowed to modify only this Markdown file, the implementation is presented here as a code block.

When doing the exercise yourself, save it separately as:

```text
parquet_inspector.py
```

Do not create it as part of editing this module.

```python
#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect useful Parquet metadata."
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Path to a Parquet file.",
    )
    return parser


def inspect_parquet(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"File does not exist: {path}")

    if not path.is_file():
        raise ValueError(f"Not a file: {path}")

    parquet = pq.ParquetFile(path)
    metadata = parquet.metadata

    print("=== FILE ===")
    print("path:", path)
    print("rows:", metadata.num_rows)
    print("row_groups:", metadata.num_row_groups)
    print()

    print("=== ARROW SCHEMA ===")
    print(parquet.schema_arrow)
    print()

    print("=== PARQUET SCHEMA ===")
    print(parquet.schema)
    print()

    for row_group_id in range(metadata.num_row_groups):
        row_group = metadata.row_group(row_group_id)

        print(f"=== ROW GROUP {row_group_id} ===")
        print("rows:", row_group.num_rows)
        print("columns:", row_group.num_columns)
        print("total_byte_size:", row_group.total_byte_size)

        for column_id in range(row_group.num_columns):
            column = row_group.column(column_id)

            print(f"\n--- COLUMN CHUNK {column_id} ---")
            print("path:", column.path_in_schema)
            print("physical_type:", column.physical_type)
            print("num_values:", column.num_values)
            print("compression:", column.compression)
            print("encodings:", column.encodings)
            print("has_dictionary_page:", column.has_dictionary_page)
            print("compressed_size:", column.total_compressed_size)
            print("uncompressed_size:", column.total_uncompressed_size)

            if column.is_stats_set:
                stats: Any = column.statistics
                print("statistics:")
                print("  min:", repr(stats.min))
                print("  max:", repr(stats.max))
                print("  null_count:", stats.null_count)
            else:
                print("statistics: not available")

            print(
                "has_column_index:",
                getattr(column, "has_column_index", "not exposed"),
            )
            print(
                "has_offset_index:",
                getattr(column, "has_offset_index", "not exposed"),
            )

            bloom_offset = getattr(
                column,
                "bloom_filter_offset",
                None,
            )
            bloom_length = getattr(
                column,
                "bloom_filter_length",
                None,
            )

            if (
                bloom_offset is not None
                or bloom_length is not None
            ):
                print(
                    "bloom_filter_offset:",
                    bloom_offset,
                )
                print(
                    "bloom_filter_length:",
                    bloom_length,
                )
            else:
                print(
                    "bloom_filter:",
                    "not exposed by this PyArrow metadata API",
                )

        print()


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        inspect_parquet(args.path)
    except Exception as exc:
        parser.error(str(exc))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### Why the implementation uses `getattr`

The Parquet format can support a feature without every library/version exposing that feature through exactly the same Python attribute.

So this:

```python
getattr(column, "has_column_index", "not exposed")
```

means:

```text
If this API exposes the property:
    print it

Otherwise:
    say it is not exposed
```

That is safer than inventing an attribute.

---

# 69. What the Inspector Should Print

For each file, the learning goal is to obtain evidence about:

```text
Schema
Row-group count
Rows per row group
Column chunks
Physical types
Encodings
Compression
Compressed size
Uncompressed size
Statistics
Column-index presence
Offset-index presence
Bloom-filter metadata when exposed
```

Do not try to make the CLI a full Parquet binary decoder.

Its purpose is to build the habit:

```text
inspect the file
before guessing about the file
```

---

# 70. Required 10-Million-Row Experiment

Create two logically equivalent datasets.

### Dataset A

```text
10 million orders
randomly ordered
```

### Dataset B

```text
the same 10 million orders
sorted by created_at
```

Then:

1. write both to Parquet
2. inspect both with the conceptual inspector
3. compare row-group statistics
4. compare `created_at` min/max ranges
5. run the same DuckDB date-filter query
6. determine how many row groups can be skipped, if your measurement method exposes this
7. record observations
8. explain why ordering changed the usefulness of statistics

Do not publish a fixed skip count unless you actually measured it.

---

# 71. Build the Experiment Dataset

A simple starting point:

```python
import pandas as pd

n = 10_000_000

df = pd.DataFrame(
    {
        "order_id": range(1, n + 1),
        "created_at": pd.date_range(
            "2025-01-01",
            periods=n,
            freq="s",
        ),
        "amount": 100.0,
    }
)

random_df = (
    df.sample(
        frac=1,
        random_state=42,
    )
    .reset_index(drop=True)
)

sorted_df = (
    df.sort_values("created_at")
    .reset_index(drop=True)
)
```

This is intentionally simple.

A production benchmark should use a workload-representative schema and value distribution.

---

# 72. Write the Two Files

```python
import pyarrow as pa
import pyarrow.parquet as pq

random_table = pa.Table.from_pandas(
    random_df,
    preserve_index=False,
)

sorted_table = pa.Table.from_pandas(
    sorted_df,
    preserve_index=False,
)

pq.write_table(
    random_table,
    "orders_random.parquet",
)

pq.write_table(
    sorted_table,
    "orders_sorted.parquet",
)
```

Use comparable writer settings for both files.

The variable you are testing is:

```text
ordering
```

not:

```text
ordering + compression + row-group-size + data type changes
```

---

# 73. Inspect Row-Group Ranges

```python
import pyarrow.parquet as pq

for filename in [
    "orders_random.parquet",
    "orders_sorted.parquet",
]:
    pf = pq.ParquetFile(filename)

    print(f"\n=== {filename} ===")

    for row_group_id in range(pf.num_row_groups):
        row_group = pf.metadata.row_group(row_group_id)

        for column_id in range(row_group.num_columns):
            column = row_group.column(column_id)

            if (
                column.path_in_schema == "created_at"
                and column.is_stats_set
            ):
                stats = column.statistics

                print(
                    "row_group=",
                    row_group_id,
                    "min=",
                    stats.min,
                    "max=",
                    stats.max,
                )
```

Your output is expected to depend on your environment.

That is intentional.

---

# 74. Run the Same Query Against Both Files

```sql
SELECT
    COUNT(*),
    SUM(amount)
FROM 'orders_random.parquet'
WHERE created_at >= TIMESTAMP '2025-03-01';
```

Then:

```sql
SELECT
    COUNT(*),
    SUM(amount)
FROM 'orders_sorted.parquet'
WHERE created_at >= TIMESTAMP '2025-03-01';
```

For execution inspection:

```sql
EXPLAIN ANALYZE
SELECT
    COUNT(*),
    SUM(amount)
FROM 'orders_sorted.parquet'
WHERE created_at >= TIMESTAMP '2025-03-01';
```

Repeat for the random version.

Do not fabricate timing or bytes-read results.

---

# 75. What a Good Experiment Record Looks Like

Record something such as:

| Variant | Row groups | Date range width | File size | Query time | Bytes read* |
|---|---:|---|---:|---:|---:|
| Random | measured | measured | measured | measured | measured |
| Sorted | measured | measured | measured | measured | measured |

`*` Only record bytes read when your actual engine/environment exposes a trustworthy measurement.

Then explain:

```text
What changed?
What stayed constant?
What physical metadata changed?
What query behavior changed?
What was the measured cost?
```

---

# 76. Fair Benchmarking

A fair experiment uses:

- the same logical dataset
- the same row count
- the same columns
- the same machine/environment
- the same query
- comparable writer settings
- repeated runs
- awareness of cold versus warm cache
- explicit recording of results

Avoid:

```text
one file
vs
another file

with different codecs
different row-group sizes
different sorting
different data
```

That is not a controlled comparison.

---

# 77. Cold Cache vs Warm Cache

A first query may have different behavior because data is not already cached.

A later query may benefit from:

```text
OS cache
engine cache
filesystem cache
object-storage effects
```

Therefore:

```text
Run 1
```

and:

```text
Run 5
```

may not be measuring exactly the same condition.

Record whether your benchmark is:

```text
cold-cache oriented
```

or:

```text
warm-cache oriented
```

Do not mix the two silently.

---

# 78. Do Not Trust One Timing

A timing like:

```text
1.42 seconds
```

is a measurement, not a law of nature.

Run multiple times.

Look for:

```text
median
variation
outliers
```

Then relate the timing back to:

```text
bytes read
row groups
statistics
CPU work
cache state
```

The detailed benchmarking discipline will be expanded in later modules.

---

# 79. Debugging — "Statistics Exist, But Many Row Groups Are Read"

### Symptom

You see:

```text
min
max
```

but the query still touches a large portion of the file.

### Possible causes

- broad ranges
- random ordering
- weak predicate selectivity
- statistics limitations
- reader behavior
- predicate semantics

### Inspect

```python
column.statistics
```

and:

```sql
SELECT
    row_group_id,
    path_in_schema,
    stats_min,
    stats_max
FROM parquet_metadata('orders.parquet');
```

### Measure

Record:

```text
number of row groups
range widths
query runtime
bytes read where exposed
```

### Lesson

```text
statistics present
≠
statistics selective
```

---

# 80. Debugging — "I Selected Two Columns, But the Query Is Still Slow"

### Symptom

You selected:

```text
country
amount
```

but performance did not improve as much as expected.

### Possible causes

- most rows still qualify
- grouping is expensive
- decoding is expensive
- decompression is expensive
- cache is cold
- storage is slow
- row groups are large
- engine overhead dominates the workload

### Investigate

Start with the physical evidence:

```text
column sizes
row-group sizes
query predicate
query plan
cache condition
```

### Lesson

Column pruning removes some work.

It does not remove all work.

---

# 81. Debugging — "Dictionary Encoding Exists, But the File Is Large"

### Possible causes

- high cardinality
- long values
- another column dominates size
- dictionary fallback
- compression interaction
- data distribution

### Inspect

```python
column.encodings
column.total_compressed_size
column.total_uncompressed_size
```

Then compare the column's cardinality and actual values.

### Lesson

Never diagnose the entire file using one encoding attribute.

---

# 82. Debugging — "Timestamp Behavior Differs Across Engines"

### Investigate

```text
physical timestamp carrier
logical type
unit
isAdjustedToUTC
legacy INT96
writer version
reader version
```

### Test

Create a small known-value dataset:

```text
2025-01-01T00:00:00Z
2025-01-01T05:30:00+05:30
2025-01-01T00:00:00.123456Z
```

Write it once.

Read it with both systems.

Compare:

```text
instant
precision
display
```

### Lesson

Timestamp interoperability is a data-contract problem.

---

# 83. Debugging — "String Statistics Look Wrong"

### Possible causes

- truncated/bounded statistics
- exactness differences
- long strings
- reader/writer version differences
- misunderstood semantics

### Inspect

With DuckDB:

```sql
SELECT
    path_in_schema,
    stats_min,
    stats_max,
    min_is_exact,
    max_is_exact
FROM parquet_metadata('orders.parquet');
```

### Lesson

Statistics should be interpreted according to their specification and metadata semantics.

---

# 84. Debugging — "Expected Metadata Is Missing"

Possible explanations:

```text
optional feature not written
writer settings
reader API limitations
library/version differences
feature not exposed by this inspection API
```

Correct response:

```text
inspect
    ↓
check installed version
    ↓
check documentation
    ↓
use another trustworthy inspection path
```

Do not fabricate an API field.

---

# 85. Common Mistakes

## 1. Confusing row groups and column chunks

Correct:

```text
Row group = subset of rows
Column chunk = one column inside that row group
```

## 2. Confusing column chunks and pages

Correct:

```text
Column chunk
    ↓
contains pages
```

## 3. Assuming statistics guarantee skipping

They only provide evidence.

## 4. Assuming statistics without sorting are useless

They can be valid but less selective.

## 5. Treating encoding and compression as the same

They are distinct.

## 6. Assuming every file uses the same encoding

Inspect the actual metadata.

## 7. Ignoring `INT96`

Legacy data exists in production.

## 8. Treating string min/max as always exact

Interpret the statistic carefully.

## 9. Assuming bloom filters replace min/max

They address different filtering patterns.

## 10. Assuming every file has a page index

Page indexes are optional.

## 11. Assuming every engine exposes the same metadata

Format support and API exposure are different things.

## 12. Trusting a single benchmark timing

Measure repeatedly.

## 13. Assuming smaller file size means faster queries

Runtime depends on more than file size.

## 14. Assuming more row groups are always better

More granularity can add overhead.

## 15. Assuming fewer row groups are always better

Very coarse groups can weaken pruning and selective reads.

---

# 86. Production Example — Large Date-Filtered Fact Table

Imagine:

```text
3 billion rows
20 columns
most queries filter by created_at
most queries aggregate a few columns
```

A query:

```sql
SELECT
    country,
    SUM(amount)
FROM orders
WHERE created_at >= DATE '2025-03-01'
GROUP BY country;
```

The engineer should investigate:

```text
required columns
    ↓
country, amount, created_at

row groups
    ↓
how many?
how large?

created_at statistics
    ↓
how selective?

sort order
    ↓
how localized are dates?

page indexes
    ↓
available?

encodings/compression
    ↓
how large are the final chunks?
```

No universal optimization recipe should be applied before measurement.

---

# 87. Production Example — High-Cardinality Equality Lookup

Suppose:

```sql
SELECT *
FROM orders
WHERE customer_id = 'C12345';
```

The engineer should ask:

```text
Are min/max ranges useful for customer_id?
Are they broad?
Are bloom filters present?
Are page indexes present?
How large are the row groups?
How selective is the predicate?
```

Then measure.

A good architecture discussion sounds like:

> "We will inspect the actual customer_id distribution and metadata, then measure equality-query behavior with and without the relevant file features."

A weak discussion sounds like:

> "Bloom filters always make these queries fast."

---

# 88. Production Example — Nested Events

Suppose an event contains:

```json
{
  "event_id": "E1",
  "device": {
    "os": "Android"
  },
  "items": [
    {"sku": "A", "qty": 2},
    {"sku": "B", "qty": 1}
  ],
  "debug": null
}
```

The engineer must understand:

```text
leaf values
+
repetition
+
definition
+
parent boundaries
```

Questions:

```text
Which fields are optional?
Which field repeats?
Where does a new event start?
Which item belongs to which event?
```

These are physical-storage questions, not merely JSON parsing questions.

---

# 89. How a Senior Data Engineer Thinks About a Parquet File

Use this checklist:

```text
What is the logical schema?
        ↓
How is it physically represented?
        ↓
How many row groups?
        ↓
How many rows per row group?
        ↓
How large are the column chunks?
        ↓
What encodings are used?
        ↓
What compression is used?
        ↓
What statistics exist?
        ↓
How selective are those statistics?
        ↓
Is the data ordered/clustered?
        ↓
Are page indexes present?
        ↓
Are bloom filters present?
        ↓
Are timestamp / decimal semantics correct?
        ↓
Are compatibility constraints present?
```

This sequence is useful during:

- architecture reviews
- performance investigations
- lake migrations
- production incidents
- code reviews
- interoperability debugging

---

# 90. A Real Architecture Review

Proposal:

> "We should sort every Parquet dataset by timestamp because that makes queries faster."

A senior engineer should ask:

```text
1. Which queries filter on timestamp?
2. What percentage of workload uses that predicate?
3. How selective are the predicates?
4. What row-group ranges currently exist?
5. What is the cost of sorting?
6. Could another important workload become worse?
7. How frequently is data rewritten?
8. Can we reproduce the effect in a controlled benchmark?
```

A defensible conclusion is evidence-based:

```text
We tested the real workload.
We compared equivalent datasets.
We inspected row-group ranges.
We measured query behavior.
We included the cost of producing the sort order.
```

---

# 91. What Should Be Measured?

| Measurement | Why it matters |
|---|---|
| File size | storage/network footprint |
| Row-group count | physical granularity |
| Rows per row group | data represented by a group |
| Column-chunk size | per-column storage footprint |
| Encodings | representation strategy |
| Compression | final stored representation |
| Statistics ranges | pruning potential |
| Page-index presence | finer-grained pruning capability |
| Bloom-filter metadata | equality-pruning potential |
| Query runtime | user-visible performance |
| Bytes read | I/O efficiency |
| Memory | execution pressure |

No single metric tells the complete story.

---

# 92. Stop and Think — Row-Group Skipping

A row group has:

```text
min(created_at) = 2025-01-01
max(created_at) = 2025-01-31
```

Can it match:

```text
created_at = 2025-02-15
```

### Answer

No.

Therefore it is a candidate for skipping.

---

# 93. Stop and Think — Broad Statistics

A row group has:

```text
min = 1
max = 1,000,000
```

Query:

```text
value = 500
```

Can min/max prove that the row group cannot match?

### Answer

No.

`500` falls inside the recorded range.

The row group must remain a candidate.

---

# 94. Stop and Think — Dictionary Encoding

Column:

```text
US US US US US CA CA US US
```

Could dictionary encoding help?

### Answer

Potentially yes.

The number of distinct values is small compared with the number of occurrences.

---

# 95. Stop and Think — High Cardinality

Column:

```text
one unique UUID per row
```

Would dictionary encoding necessarily help?

### Answer

No.

The dictionary could become almost as large as the data it is trying to organize, so the writer may fall back to another encoding.

---

# 96. Stop and Think — Page Index

A row group has a broad range:

```text
1 → 1,000,000
```

but page-level ranges are narrow.

Can page indexes still help?

### Answer

Potentially yes.

The row group cannot be rejected as a whole, but individual pages may be rejected.

---

# 97. Stop and Think — Bloom Filter

A bloom filter says:

```text
customer_id = C12345
definitely absent
```

What does that imply?

### Answer

The indexed region can be excluded from the candidate set for that lookup.

If the bloom filter instead says:

```text
possibly present
```

the actual data still needs to be checked.

---

# 98. Interview — Basic

### What is Parquet?

**Model answer:** Parquet is a column-oriented analytical file format whose physical structure is built around row groups, column chunks, pages, and metadata.

### What is a row group?

**Model answer:** A horizontal subset of rows in a Parquet file. Each column in the row group has a column chunk.

### What is a column chunk?

**Model answer:** One column's data inside one row group. It is composed of pages.

### What is a page?

**Model answer:** A smaller storage unit inside a column chunk that contains encoded data and related page information.

### What is the footer?

**Model answer:** The metadata area describing the file schema and physical structure, including information readers use to locate and reason about data.

### Why is the footer at the end?

**Model answer:** It lets the writer stream the data and finalize metadata after the relevant offsets and sizes are known. Readers can then seek to the end and inspect metadata before reading selected data.

---

# 99. Interview — Intermediate

### What is encoding versus compression?

**Model answer:** Encoding changes the representation to exploit data structure; compression reduces the size of the resulting representation. They are distinct stages.

### What is dictionary encoding?

**Model answer:** Distinct values are stored in a dictionary page and occurrences are represented using dictionary indexes in data pages.

### Why can dictionary encoding fall back?

**Model answer:** The dictionary can become too large or lose its advantage as distinct-value cardinality grows, so the writer may use another encoding.

### What are row-group statistics?

**Model answer:** Metadata summarizing values in a column chunk, commonly including min, max, and null count. Engines can use this metadata to eliminate row groups that cannot match predicates.

### How does column pruning work?

**Model answer:** Because columns are stored separately within row groups, a reader can avoid reading unrelated column chunks.

### Why does sorting help statistics?

**Model answer:** Sorting localizes similar values into nearby physical regions, making min/max ranges narrower and potentially more selective.

---

# 100. Interview — Advanced

### What do page indexes add?

**Model answer:** They provide finer-grained page-level metadata and navigation, allowing a reader to reason about individual pages rather than only whole row groups.

### What is the column index?

**Model answer:** Page-level metadata that can describe values/bounds for individual pages and help a reader decide which pages may be relevant.

### What is the offset index?

**Model answer:** Metadata used to navigate to pages and their row positions/offsets.

### What does a bloom filter add?

**Model answer:** Probabilistic membership information that can help exclude data for selective equality-style predicates.

### What are definition levels?

**Model answer:** Metadata levels representing how deeply a nested field path is defined or present.

### What are repetition levels?

**Model answer:** Metadata that represents repeated-structure boundaries, such as whether a value continues the same list/parent or starts another repeated group.

---

# 101. Interview — Senior / Architecture

### How would you investigate a Parquet query that scans too much data?

**Model answer:** Inspect the schema, row-group count and sizes, relevant column chunks, statistics, ordering, encodings, compression, page-index availability, and bloom-filter metadata where relevant. Then compare these facts with the query predicate and projection and measure the actual execution behavior.

### How would you determine whether sorting could improve pruning?

**Model answer:** Identify workload predicates, create equivalent randomly ordered and sorted datasets, hold other variables constant, inspect row-group ranges, measure query behavior, and include the cost of sorting.

### How would you inspect an unfamiliar Parquet dataset?

**Model answer:** Start with file metadata, schema, row groups, column chunks, statistics, encodings, compression, indexes, timestamps, decimals, version information, and writer metadata. Then relate those facts to real query patterns.

### How would you diagnose writer/reader incompatibility?

**Model answer:** Compare versions, inspect physical/logical types, investigate timestamp and decimal representation, identify legacy constructs such as `INT96`, inspect optional features, and reproduce the issue using representative files.

---

# 102. Final Production Mental Model

```text
Parquet
│
├── File Signature
│      └── PAR1
│
├── Row Groups
│      │
│      ├── Column Chunks
│      │      │
│      │      ├── Dictionary Page (optional)
│      │      ├── Data Pages
│      │      └── Encoded + Compressed Bytes
│      │
│      └── Row-group Statistics
│
└── Footer / Metadata
       │
       ├── Schema
       ├── Row-group metadata
       ├── Column metadata
       ├── Locations
       ├── Encodings
       ├── Compression
       └── Optional index / bloom metadata
```

And the query path:

```text
Query
  ↓
Read Footer
  ↓
Understand Schema + Metadata
  ↓
Prune Unneeded Columns
  ↓
Use Statistics / Indexes
  ↓
Skip Irrelevant Data
  ↓
Read Required Pages
  ↓
Decompress
  ↓
Decode
  ↓
Execute
```

This is the central model for Topic 02.

---

# 103. Final Review

Try to explain each item without looking at your notes:

```text
What is PAR1?

What is a row group?

What is a column chunk?

What is a page?

Why are pages inside column chunks?

Why is the footer at the end?

Why can a reader inspect the footer first?

What is a physical type?

What is a logical type?

What is a dictionary page?

What is a data page?

What is data page v1/v2?

What is PLAIN?

What is dictionary encoding?

What is dictionary fallback?

What is RLE?

What is bit-packing?

What is DELTA_BINARY_PACKED?

What is DELTA_BYTE_ARRAY?

What is BYTE_STREAM_SPLIT?

What is the difference between encoding and compression?

What are min/max statistics?

What is null_count?

How does row-group skipping work?

Why does sorting affect pruning?

What does a page index add?

What is a column index?

What is an offset index?

What does a bloom filter add?

What are definition levels?

What are repetition levels?

Why do nullable fields involve definition information?

What does isAdjustedToUTC mean?

Why does INT96 still matter?

Why do decimal precision and scale matter?

Why should string statistics be interpreted carefully?

Why can two logically identical Parquet datasets have different query behavior?
```

If you cannot explain a concept in your own words, revisit that section before continuing.

---

# 104. Learning Checkpoint

You should be able to tick all of these.

## Roadmap checkpoint

- [ ] I can draw a Parquet file's structure from memory.
- [ ] I can explain the difference between encoding and compression.
- [ ] I can explain how row-group statistics enable skipping.
- [ ] I can explain why sorting matters.
- [ ] I can explain what a page index adds.
- [ ] I can explain what a bloom filter adds.
- [ ] I can explain definition and repetition levels at a high level.

## Practical checkpoint

- [ ] I can identify row groups, column chunks, and pages conceptually.
- [ ] I can inspect metadata using PyArrow.
- [ ] I can inspect metadata using DuckDB.
- [ ] I can map metadata fields to the physical file model.
- [ ] I can explain physical versus logical types.
- [ ] I can recognize `INT96`.
- [ ] I can explain timestamp units and `isAdjustedToUTC`.
- [ ] I can explain decimal precision/scale.
- [ ] I can inspect encodings and compression.
- [ ] I can explain dictionary fallback.
- [ ] I can distinguish row-group statistics from page indexes.
- [ ] I can distinguish bloom filters from min/max statistics.
- [ ] I can reason about nested data using definition/repetition concepts.
- [ ] I can compare random and sorted datasets.
- [ ] I can investigate a performance problem using metadata before guessing.
- [ ] I can explain Parquet internals during an architecture review.

---

# 105. Final "Remember This"

1. **A Parquet file is not simply a bag of rows.**

2. **Row groups are major physical units of analytical organization.**

3. **A row group contains a subset of rows.**

4. **A column chunk contains one column within one row group.**

5. **Pages are smaller storage units inside column chunks.**

6. **The footer tells readers how to understand and navigate the file.**

7. **The footer is written at the end so data can be streamed and metadata finalized afterward.**

8. **Physical type and logical type are different concepts.**

9. **Encoding and compression are different stages.**

10. **Dictionary encoding is data-dependent and may fall back.**

11. **Statistics are useful when they can eliminate work.**

12. **Sorting can make min/max statistics more selective.**

13. **Column pruning avoids unnecessary columns.**

14. **Predicate skipping avoids unnecessary row groups/pages.**

15. **Page indexes provide finer-grained page-level information.**

16. **Column indexes describe page-level value information; offset indexes help locate pages.**

17. **Bloom filters provide probabilistic membership information and complement range statistics.**

18. **Nested data requires definition and repetition concepts.**

19. **Timestamps require careful handling of units and `isAdjustedToUTC`.**

20. **Legacy `INT96` still matters because real datasets have history.**

21. **Decimal precision and scale are part of the data contract.**

22. **String statistics need careful interpretation.**

23. **Reader/writer compatibility is a production concern.**

24. **Inspect the file before guessing how it behaves.**

25. **Measure before standardizing an optimization.**

The highest-value engineering habit from this topic is:

```text
Inspect
  ↓
Understand
  ↓
Form a hypothesis
  ↓
Measure
  ↓
Change one physical factor
  ↓
Measure again
  ↓
Standardize only when evidence supports the decision
```

---

# 106. Connection to Later Topics

This topic is the physical foundation for:

- **Topic 03:** reading and writing Parquet with PyArrow
- **Topic 07:** compression codecs and benchmarking
- **Topic 08:** partitioning and pruning
- **Topic 09:** file sizing and compaction
- later schema-evolution work
- lakehouse table formats
- cloud-storage optimization
- observability and performance engineering

The boundary is intentional:

```text
Topic 02
→ understand the file

Topic 03
→ control the file from Python

Topic 07
→ tune compression

Topic 08
→ design partitions

Topic 09
→ manage file health
```

Do not skip the physical model. Later optimizations are difficult to reason about when the underlying file hierarchy is unclear.
