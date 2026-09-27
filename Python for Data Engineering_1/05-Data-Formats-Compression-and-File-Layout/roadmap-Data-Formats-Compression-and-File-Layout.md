# Roadmap — Module 2.5: Data Formats, Compression, and File Layout

This is the learning roadmap for the fifth module of Stage 2, **Python for
Data Engineering**. It tells you **what** to learn about data formats,
compression, and file layout, **in what order**, **how** to learn each
topic, and **how to prove to yourself** that you have learned it before
you move on.

In Module 2.4 you saw engines skip whole files and read only a fraction of
the bytes in a dataset. That only happens when the data was **written
well**. The format, the codec, the row-group size, the sort order, the
partition scheme, and the number of files are all decided by the data
engineer at write time — and they decide the speed and the cloud bill of
every query that runs for years afterwards. A badly laid-out lake can make
a query 100× slower and 100× more expensive than the same data laid out
well. This module teaches you to make those decisions deliberately.

---

## 1. Module outcome

By the end of this module you will be able to:

- Explain row-oriented vs columnar storage and choose between them for a
  workload.
- Describe Parquet's internal structure — row groups, column chunks, pages,
  encodings, statistics, page indexes, and the footer — and use it to
  predict query performance.
- Read and write Parquet with PyArrow with deliberate control over schema,
  row-group size, encodings, compression, statistics, and datasets.
- Read and write Avro, explain its schema and container file, and know when
  a row format is the right choice.
- Explain ORC's structure and choose between Parquet, ORC, Avro, Arrow IPC,
  CSV, and JSON with written reasons.
- Flatten and explode nested, semi-structured data correctly — without
  silently changing the grain of a table.
- Choose a compression codec and level from measured trade-offs, and
  explain splittability.
- Design partition layouts that match query patterns, and avoid
  over-partitioning.
- Diagnose and fix the small-files problem with target file sizes and
  compaction.
- Ingest legacy formats — Excel, XML, and fixed-width (including mainframe
  data) — safely into a modern columnar lake.

---

## 2. Prerequisites

This module builds on earlier stages and Modules 2.1–2.4. It does **not**
re-teach them.

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Bytes, storage, HDD vs SSD, RAM vs storage | Stage 0 — How Computers Work | File layout is about how many bytes are read, and from where |
| Filesystems | Stage 0 — Operating System Fundamentals | Directories, file metadata, and why listing many files is slow |
| CSV, JSON / JSON Lines, encodings and newlines | Stage 1 — Module 1.5 | Text formats are *not* re-taught; this module compares them with binary formats |
| Safe file writes, idempotent jobs | Stage 1 — Module 1.10 | Compaction and partition overwrites must be atomic and repeatable |
| OLTP vs OLAP, lake and lakehouse | Stage 2 — Module 2.1 | Formats and layouts are the physical side of those architectures |
| dtypes and memory | Stage 2 — Module 2.2 | Encodings and compression depend on types and value distributions |
| pandas I/O basics (`read_parquet`, `read_excel`) | Stage 2 — Module 2.3 | This module goes under the hood of those calls |
| Arrow memory model, IPC, pushdown, DuckDB and Polars scans | Stage 2 — Module 2.4 | Arrow is the in-memory side; this module is the on-disk side |

**Tools needed:**

- Python 3.12+ in a `uv` project: `uv add pyarrow pandas polars duckdb
  fastavro openpyxl python-calamine lxml defusedxml zstandard lz4`.
- `pytest` for tests.
- MinIO in Docker (from Module 2.4) for object-storage experiments.
- Optional command-line inspection tools: `parquet-tools`-style utilities,
  or DuckDB's `parquet_metadata()` and `parquet_schema()`.
- A dataset of at least 5–10 GB (NYC taxi trips or generated data) so that
  layout differences are measurable.

---

## 3. How the module is organised

The ten topics are grouped into five phases. Work through them **in
order**.

```text
Phase A — Storage Layouts                   (Basics)
  01 Row-oriented vs columnar storage

Phase B — Parquet in Depth                  (Intermediate → Advanced)
  02 Parquet internals: row groups, pages, and statistics
  03 Reading and writing Parquet with PyArrow

Phase C — Other Formats and Data Shapes     (Intermediate)
  04 Avro files and row-oriented formats
  05 ORC and format selection trade-offs
  06 Nested, semi-structured data: flatten and explode

Phase D — Physical Optimization             (Intermediate → Advanced)
  07 Compression codecs: Snappy, gzip, Zstandard, LZ4
  08 Partitioning and Hive-style directory layouts
  09 The small-files problem and target file sizing

Phase E — Real-World Ingestion              (Intermediate → Advanced)
  10 Excel, XML, and fixed-width legacy formats

Consolidate
  practice-questions.md
  Module mini-project: from messy sources to an optimized lake layout
```

The dependency chain:

```text
01 ──► 02 ──► 03 ──► 04 ──► 05 ──► 06 ──► 07 ──► 08 ──► 09 ──► 10
row vs  inside  write   row     compare nested  bytes   folders  number  legacy
column  Parquet Parquet format  and     shapes  per     per      and size sources
                well    (Avro)  choose          file    dataset  of files into all
                                                                         of the above
```

Why this order:

- Row vs columnar (01) is the lens for every format that follows.
- Parquet comes before other formats because it is the default analytical
  format; Avro and ORC are easiest to understand as contrasts with it.
- Nested data (06) comes after the formats because how you store nested
  data depends on format support.
- Compression (07), partitioning (08), and file sizing (09) are the three
  physical knobs of a dataset; they build on each other in that order.
- Legacy formats (10) come last because the goal is to convert them *into*
  a well-designed layout using everything above.

---

## 4. Suggested schedule

About **4 weeks at 8–10 hours per week**.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — row vs columnar · Topic 02 — Parquet internals |
| 2 | Topic 03 — Parquet with PyArrow · Topic 04 — Avro · Topic 05 — ORC and format selection |
| 3 | Topic 06 — nested data · Topic 07 — compression · Topic 08 — partitioning |
| 4 | Topic 09 — small files · Topic 10 — legacy formats · practice questions · mini-project |

---

## 5. How to study every topic (the file-layout loop)

```text
Read → Predict size & bytes read → Write the file → Inspect its metadata
→ Query it → Measure size, time, bytes read → Change one knob
→ Measure again → Write it down → Explain aloud
```

1. **Read** the topic file once, fully.
2. **Predict** file size and how many bytes a query will read before you
   write anything.
3. **Write** the data with explicit settings (never rely on defaults
   without knowing them).
4. **Inspect** the result: Parquet footer and row-group statistics, Avro
   header, ORC stripes, directory listing, file sizes.
5. **Query** it with DuckDB or Polars (from Module 2.4) using a realistic
   filter.
6. **Measure** file size on disk, write time, read time, and bytes read.
7. **Change one knob** at a time — codec, level, row-group size, sort
   order, partition column, file count.
8. **Measure again** and record the result in a table.
9. **Write down** the rule you learned in `module-2.5-notes.md`.
10. **Explain aloud** why the knob changed the numbers.

Keep a single `formats_lab/` `uv` project:

```text
formats_lab/
├── data/raw/           # input files (git-ignored)
├── data/out/           # experiment outputs (git-ignored)
├── src/formats_lab/    # one module per topic
├── experiments/        # CSV tables of measurements per experiment
└── tests/
```

---

## 6. Phase A — Storage Layouts (Basics)

### Topic 01 — [Row-oriented vs columnar storage](01-row-oriented-vs-columnar-storage.md)

**Why it comes first:** Every format decision in this module starts with
one question: does the workload read *whole rows* or *a few columns across
many rows*?

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Row-oriented layout: all fields of a record stored together (CSV, JSON Lines, Avro, most OLTP database pages) |
| Basics | Column-oriented layout: all values of one column stored together (Parquet, ORC, Arrow, analytical warehouses) |
| Basics | Which workloads each serves: writing and reading whole records vs scanning and aggregating a few columns |
| Intermediate | Why columnar files compress better: similar values stored together; encodings like dictionary and run-length |
| Intermediate | Column pruning (read only needed columns) and predicate skipping (skip blocks whose min/max cannot match) |
| Intermediate | Write-side costs of columnar formats: buffering rows before writing, poor fit for single-record appends and updates |
| Intermediate | Text vs binary formats: typing, precision, parsing cost, and human readability |
| Advanced | Hybrid layouts: **PAX** (rows grouped into blocks, columns within each block) — the design used by Parquet row groups and ORC stripes |
| Advanced | Self-describing formats (schema embedded in the file) vs schema-less formats (schema lives elsewhere) |
| Advanced | Splittability: whether a large file can be read in parallel by several workers from different offsets |
| Advanced | Where each layout appears in a pipeline: row formats at ingestion and messaging, columnar formats in silver/gold storage |

**How to learn it**

1. Read the topic file.
2. Draw the same 6-row, 4-column table as bytes on disk in row layout,
   column layout, and PAX layout (two row groups).
3. For ten example queries, mark which layout reads fewer bytes.

**Hands-on exercise — `layout_compare.py`**

1. Generate 10 million orders with 20 columns.
2. Write them as CSV, JSON Lines, Avro, Parquet, and ORC (use library
   defaults for now).
3. Record file size, write time, and time to (a) read all columns and (b)
   sum one column.
4. Run a DuckDB query selecting 2 of 20 columns with a date filter on each
   format and compare bytes read.
5. Save all measurements to `experiments/layout_compare.csv`.

**Checkpoint — you are ready to move on when you can:**

- [ ] Explain row vs columnar storage with a diagram.
- [ ] Explain why columnar files compress better.
- [ ] Explain PAX and why Parquet uses row groups.
- [ ] Define splittability and give an example of a non-splittable file.
- [ ] Choose a layout for three workloads and justify each.

**Common mistakes:** believing columnar is always better (it is not for
record-at-a-time writes); comparing formats without controlling for
compression; forgetting that text formats lose types.

---

## 7. Phase B — Parquet in Depth (Intermediate → Advanced)

### Topic 02 — [Parquet internals: row groups, pages, and statistics](02-parquet-internals-row-groups-pages-and-statistics.md)

**Why here:** Parquet is the default file format of modern data lakes and
lakehouses. Every pushdown you saw in Module 2.4 depends on its internal
structure.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | File structure: magic bytes (`PAR1`), **row groups**, **column chunks**, **pages**, and the **footer** with file metadata |
| Basics | Why the footer is at the end (writers stream data first) and why readers read the footer first |
| Basics | Physical types (`BOOLEAN`, `INT32`, `INT64`, `FLOAT`, `DOUBLE`, `BYTE_ARRAY`, `FIXED_LEN_BYTE_ARRAY`) vs logical types (`STRING`, `DATE`, `TIMESTAMP`, `DECIMAL`, `UUID`, …) |
| Intermediate | Page types: dictionary pages and data pages (v1 and v2) |
| Intermediate | **Encodings**: `PLAIN`, dictionary (`RLE_DICTIONARY`), RLE / bit-packing, `DELTA_BINARY_PACKED`, `DELTA_BYTE_ARRAY`, `BYTE_STREAM_SPLIT`; dictionary fallback when a dictionary grows too large |
| Intermediate | Encoding happens **before** compression, and together they produce the final size |
| Intermediate | **Statistics**: min, max, null count per column chunk; how engines use them to skip row groups |
| Intermediate | Why **sort order** decides whether statistics are useful: sorted or clustered columns give tight min/max ranges |
| Advanced | The **page index** (column index + offset index) for page-level skipping, and **bloom filters** for equality lookups on high-cardinality columns |
| Advanced | Nested data in Parquet: the Dremel model with **repetition and definition levels** (and why nullable flat columns also use definition levels) |
| Advanced | Timestamp representations: `isAdjustedToUTC`, units (millis, micros, nanos), and the legacy `INT96` timestamps from older Hive/Spark writers |
| Advanced | Decimal storage and precision; unsigned integers; string statistics truncation |
| Advanced | Format evolution and compatibility: format version (e.g. `"2.6"`), reader compatibility across engines, and newer additions such as the Variant type for semi-structured data (awareness) |
| Advanced | Parquet modular encryption (awareness; security details in Module 2.20) |

**How to learn it**

1. Read the topic file.
2. Open a Parquet file's metadata with `pyarrow.parquet.ParquetFile(...).metadata`
   and DuckDB's `parquet_metadata()`. Map every field you see to the
   diagram in the topic file.
3. Draw repetition and definition levels by hand for three small nested
   records.

**Hands-on exercise — `parquet_inspector.py`**

Build a small CLI (use `argparse` from Stage 1) that, for any Parquet file,
prints:

1. Schema with physical and logical types.
2. Number of row groups, rows per group, and compressed / uncompressed size
   per column chunk.
3. Encodings and compression codec per column.
4. Min / max / null count per column per row group.
5. Whether page indexes and bloom filters are present.

Then write the same 10 million orders twice — once in random order and once
sorted by `created_at` — and use your inspector plus a DuckDB date-filter
query to show how many row groups each version can skip.

**Checkpoint:**

- [ ] Draw a Parquet file's structure from memory.
- [ ] Explain the difference between encoding and compression.
- [ ] Explain how row-group statistics enable skipping, and why sorting
      matters.
- [ ] Explain what a page index and a bloom filter add.
- [ ] Explain definition and repetition levels at a high level.

**Common mistakes:** assuming statistics help on unsorted data; ignoring
`INT96` timestamps from legacy writers; treating string min/max statistics
as exact.

---

### Topic 03 — [Reading and writing Parquet with PyArrow](03-reading-and-writing-parquet-with-pyarrow.md)

**Why here:** Knowing the internals, you can now control every one of them
from Python — the reference implementation that pandas, Polars, and many
other tools build on or mirror.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `pq.write_table` and `pq.read_table`; reading only some columns with `columns=`; row filters with `filters=` |
| Basics | Explicit schemas when writing (never trusting inference for production outputs) |
| Intermediate | `pq.ParquetFile`: `metadata`, `schema_arrow`, `read_row_group`, `iter_batches(batch_size=...)` for bounded-memory reads |
| Intermediate | `pq.ParquetWriter` for writing a file incrementally from many batches (streaming writes) |
| Intermediate | Write options: `row_group_size`, `data_page_size`, `compression` and `compression_level` (per file or per column), `use_dictionary`, `write_statistics`, `version`, `coerce_timestamps`, `use_byte_stream_split`, `write_page_index` |
| Intermediate | Multi-file datasets with `pyarrow.dataset`: `ds.dataset(path, format="parquet", partitioning="hive")`, filtering with expressions, `to_batches()`, `to_table()` |
| Intermediate | `ds.write_dataset`: `partitioning`, `max_rows_per_file`, `min_rows_per_group`, `max_rows_per_group`, `existing_data_behavior`, file-name templates |
| Advanced | Schema differences across files: unifying schemas, missing columns, type widening, and failing loudly on incompatible types (policy in Module 2.11) |
| Advanced | Custom key-value metadata in the footer (e.g. pipeline version, source, run id) |
| Advanced | Reading from object storage via PyArrow filesystems (`pyarrow.fs.S3FileSystem`) and `fsspec` (Module 2.17 goes deeper) |
| Advanced | Atomic output: writing to a temporary prefix and committing by rename or manifest, and why object stores make "rename" expensive (motivation for table formats in Module 2.15) |
| Advanced | Tuning row-group size: too small (weak compression, many footer entries) vs too large (poor skipping, high writer memory) |

**How to learn it**

1. Read the topic file.
2. Write the same table with five different option sets and inspect each
   with your `parquet_inspector.py`.
3. Read a 5 GB Parquet file with `iter_batches` and measure peak memory
   against `read_table`.

**Hands-on exercise — `parquet_writer_lab.py`**

1. Write orders with an explicit schema, per-column settings
   (dictionary for `country` and `status`, `BYTE_STREAM_SPLIT` for a float
   sensor column), `zstd` compression, statistics, and page indexes.
2. Stream a 20 GB generated dataset into one file per day with
   `ParquetWriter`, never holding more than one batch in memory.
3. Write the same data as a Hive-partitioned dataset with
   `ds.write_dataset` and a target of about 1 million rows per row group.
4. Add footer metadata with `pipeline_version` and `run_id`, and read it
   back.
5. Run an experiment on row-group sizes (10k, 100k, 1M, 10M rows) and
   record file size, write memory, and filtered-query time.
6. Write tests that assert the schema, codec, and presence of statistics in
   the output.

**Checkpoint:**

- [ ] Read only the needed columns and row groups from a Parquet file.
- [ ] Write a large file with bounded memory.
- [ ] Set compression, dictionary, and statistics per column.
- [ ] Write and read a partitioned dataset with `pyarrow.dataset`.
- [ ] Choose a row-group size and justify it with measurements.

**Common mistakes:** writing Parquet from pandas `object` columns without
an explicit schema; one giant row group; many tiny row groups from
appending small batches; overwriting output in place without an atomic
commit.

---

## 8. Phase C — Other Formats and Data Shapes (Intermediate)

### Topic 04 — [Avro files and row-oriented formats](04-avro-files-and-row-oriented-formats.md)

**Why here:** After mastering the columnar default, you learn the most
important row-oriented binary format — the one used heavily in ingestion,
CDC, and messaging.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What Avro is: a compact binary row format with a **JSON schema** |
| Basics | Schema building blocks: primitive types, `record`, `enum`, `array`, `map`, `fixed`, and **unions** (`["null", "string"]` for nullable fields) |
| Basics | Reading and writing with `fastavro`: `writer`, `reader`, `parse_schema` |
| Intermediate | The **object container file**: header with schema and codec, data blocks, and **sync markers** — why Avro files are splittable |
| Intermediate | Logical types: `date`, `timestamp-millis` / `timestamp-micros`, `decimal`, `uuid` |
| Intermediate | Block-level compression codecs (`null`, `deflate`, `snappy`, `zstandard`, …) |
| Intermediate | Why Avro suits ingestion and messaging: fast record-at-a-time writes, compact encoding, schema travels with the data |
| Advanced | **Schema resolution**: reading data written with one schema (writer's schema) using another (reader's schema); default values; field addition and removal at the file level (compatibility policies are in Module 2.11; schema registries in Module 2.16) |
| Advanced | Converting Avro to Parquet in bronze → silver pipelines, and type-mapping pitfalls (unions, enums, logical types) |
| Advanced | A short tour of other row formats and when you still meet them: CSV and JSON Lines (Stage 1), Hadoop SequenceFile (legacy), MessagePack (awareness) |

**How to learn it**

1. Read the topic file.
2. Design an Avro schema for your orders data by hand, including nullable
   fields, an enum, a nested record, and logical types.
3. Open an Avro file in a hex viewer and find the header, the schema JSON,
   and the sync markers.

**Hands-on exercise — `avro_ingestion.py`**

1. Write 1 million orders to Avro with `deflate` and `snappy`; compare size
   and speed with the Parquet and JSON Lines outputs from Topic 01.
2. Evolve the schema: add a field with a default, remove a field, and read
   old files with the new reader schema — record which changes work.
3. Stream Avro records one at a time from a large file with bounded memory.
4. Convert Avro to partitioned Parquet with an explicit Arrow schema,
   asserting row counts and values are unchanged.
5. Test the schema-resolution rules you observed.

**Checkpoint:**

- [ ] Write an Avro schema with nullable fields, enums, nested records, and
      logical types.
- [ ] Explain the container file and why Avro is splittable.
- [ ] Explain writer vs reader schemas.
- [ ] Explain when Avro is a better choice than Parquet.

**Common mistakes:** forgetting a `default` on a new field; wrong union
order for nullable defaults (`null` must come first when the default is
`null`); using Avro for analytical storage that should be columnar.

---

### Topic 05 — [ORC and format selection trade-offs](05-orc-and-format-selection-tradeoffs.md)

**Why here:** With Parquet and Avro understood, ORC completes the set of
big-data formats, and you can finally compare them all and choose.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What ORC is: a columnar format from the Hive ecosystem |
| Basics | Structure: **stripes** (similar to Parquet row groups), row indexes (statistics every 10,000 rows by default), stripe footers, file footer, postscript |
| Basics | Reading and writing ORC with `pyarrow.orc` |
| Intermediate | ORC vs Parquet: lightweight indexes, bloom filters, type support, and ecosystem support (Hive, Trino, Spark vs broader Parquet support) |
| Intermediate | ORC in Hive ACID tables (awareness) |
| Intermediate | A **format selection matrix**: Parquet, ORC, Avro, Arrow IPC / Feather (Module 2.4), CSV, JSON Lines — rows for layout, schema, types, compression, splittability, write pattern, engine support, human readability |
| Advanced | Choosing by pipeline stage: landing (whatever the source sends), bronze (often the source format or Avro/JSON Lines), silver and gold (Parquet via a table format), caching and interchange (Arrow IPC), partner exports (CSV/JSON/Excel) |
| Advanced | Format conversions as a cost: when converting early saves money, and when to keep the original for replay |
| Advanced | Awareness of newer formats aimed at ML and AI workloads (e.g. Lance for vector and multimodal data) and how to evaluate a new format fairly |

**How to learn it**

1. Read the topic file.
2. Inspect an ORC file's stripes and statistics and compare them with the
   Parquet file of the same data.
3. Build the format selection matrix from memory, then check it against the
   topic file.

**Hands-on exercise — `format_bakeoff.py`**

1. Using your orders dataset, write Parquet, ORC, Avro, Arrow IPC, CSV,
   and JSON Lines with comparable compression.
2. Run the same four queries with DuckDB or PyArrow (full scan, one-column
   aggregate, selective filter, point lookup) and record size, time, and
   bytes read.
3. Write a one-page "format policy" for a fictional company: which format
   in which layer, and why.

**Checkpoint:**

- [ ] Explain ORC's stripes and indexes.
- [ ] Compare ORC and Parquet in three points.
- [ ] Choose a format for each pipeline layer and justify it.

**Common mistakes:** choosing a format by habit; comparing formats with
different codecs; exporting partner data in a format the partner cannot
read.

---

### Topic 06 — [Nested, semi-structured data: flatten and explode](06-nested-semi-structured-data-flatten-and-explode.md)

**Why here:** APIs, event streams, and document databases deliver nested
JSON. You must decide how to store and reshape it, and every choice changes
the table's grain.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Structured vs semi-structured data; nested objects (structs), arrays (lists), and maps |
| Basics | **Flattening** structs into columns (`customer.address.city` → `customer_address_city`) |
| Basics | **Exploding** arrays into rows — and the fact that exploding **changes the grain** (one row per order becomes one row per order line) |
| Intermediate | Tools: `pd.json_normalize` (`record_path`, `meta`, `sep`), Polars `unnest` / `explode` / `struct` and `list` namespaces, DuckDB `unnest` and struct/list functions, `pyarrow.compute` and `Table.flatten()` |
| Intermediate | Splitting one nested document into several related tables (orders, order_lines, payments) with keys linking them |
| Intermediate | Empty arrays and nulls when exploding: rows that disappear vs rows kept with null values |
| Intermediate | Double counting: aggregating a parent-level amount after exploding a child array |
| Advanced | Keeping nested types in Parquet (lists, structs, maps) vs flattening: query convenience, engine support, and schema-evolution costs |
| Advanced | Schema inference on heterogeneous JSON: fields that change type, optional fields, very sparse keys; when to store the raw JSON string alongside typed columns |
| Advanced | Semi-structured column types in engines and formats (JSON columns, and the Variant type in newer Parquet, Spark, and Iceberg versions — awareness) |
| Advanced | Deeply nested and recursive structures, and limits on flattening |

**How to learn it**

1. Read the topic file.
2. Take one real API response (e.g. a public GitHub or weather API JSON)
   and draw its tree structure, then design the tables you would produce
   from it.
3. For every explode you do, write the grain before and after.

**Hands-on exercise — `nested_orders.py`**

Given JSON Lines of nested orders (customer struct, array of line items
each with an array of discounts, optional payment struct, free-form
`metadata` object):

1. Produce three normalised tables: `orders`, `order_lines`, `discounts`,
   with keys — in pandas, Polars, and DuckDB.
2. Show the double-counting bug when summing `order_total` after exploding
   lines, and fix it.
3. Keep orders with empty line arrays (do not lose them) and test it.
4. Write the same data as nested Parquet (lists and structs kept) and as
   flat Parquet; compare size and query convenience.
5. Keep the unexpected `metadata` keys as a raw JSON string column and
   count how often each key appears.

**Checkpoint:**

- [ ] Explain flatten vs explode and state the grain after each.
- [ ] Split a nested document into related tables with keys.
- [ ] Avoid double counting after an explode.
- [ ] Decide when to keep nested types instead of flattening.

**Common mistakes:** exploding two independent arrays in a row (a
cross-product); losing records with empty arrays; flattening hundreds of
sparse keys into mostly-null columns.

---

## 9. Phase D — Physical Optimization (Intermediate → Advanced)

### Topic 07 — [Compression codecs: Snappy, gzip, Zstandard, LZ4](07-compression-codecs-snappy-gzip-zstd-lz4.md)

**Why here:** Compression is the first physical knob. It trades CPU time for
fewer bytes stored and moved — and on cloud object storage, bytes are money
and latency.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why compress: storage cost, network transfer, I/O time |
| Basics | Compression ratio, compression speed, and decompression speed — three different numbers |
| Basics | Common codecs: **Snappy** (fast, moderate ratio), **gzip / deflate** (good ratio, slower), **Zstandard (zstd)** (tunable, strong ratio at good speed), **LZ4** (very fast, lower ratio), plus Brotli, bzip2, and xz |
| Intermediate | Compression levels (e.g. zstd levels) and their diminishing returns |
| Intermediate | **Splittability**: a raw `.csv.gz` or `.json.gz` file cannot be split for parallel reading; container formats (Parquet, ORC, Avro) compress internally per page/stripe/block, so they stay splittable with any codec |
| Intermediate | Encoding vs compression again (from Topic 02): dictionary and RLE first, general-purpose compression second — and why sorting improves both |
| Intermediate | Choosing by use case: hot data read often (favour decompression speed), cold archive (favour ratio), streaming and messaging (favour low latency) |
| Advanced | Cost modelling: storage cost vs compute cost vs egress cost per month for a dataset at different codecs |
| Advanced | Per-column codec choices in Parquet; incompressible data (already-compressed images, random IDs, encrypted values) |
| Advanced | zstd trained dictionaries for many small similar payloads (awareness) |
| Advanced | Engine and tool compatibility: codecs every consumer can read |

**How to learn it**

1. Read the topic file.
2. Before running anything, guess the ranking of codecs by ratio and by
   speed; then measure.
3. Build a cost table for 10 TB of data under each codec using your
   measured ratios and a storage price per GB-month.

**Hands-on exercise — `codec_benchmark.py`**

1. Write the same orders data as Parquet with no compression, Snappy,
   gzip, LZ4, and zstd at levels 1, 3, 9, and 19.
2. Record file size, write time, full-read time, and one-column-read time
   (three runs each).
3. Compress a large CSV as `.gz` and as `.zst`; show that a DuckDB or
   Polars parallel read cannot split the gzip file, and compare it to
   Parquet.
4. Sort the data by `country, created_at` and repeat one codec; record the
   size change.
5. Produce a recommendation table (hot, warm, cold data) from your numbers.

**Checkpoint:**

- [ ] Explain ratio vs compression speed vs decompression speed.
- [ ] Explain why `.csv.gz` is not splittable but gzip-compressed Parquet
      is.
- [ ] Choose a codec and level for hot, cold, and streaming data.
- [ ] Explain why sorting data can shrink files.

**Common mistakes:** max compression levels on hot data (slow writes, tiny
gains); gzipped giant CSVs as a lake storage format; compressing already
compressed data.

---

### Topic 08 — [Partitioning and Hive-style directory layouts](08-partitioning-and-hive-style-directory-layouts.md)

**Why here:** Compression shrinks bytes inside files; partitioning decides
which files a query opens at all.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Partitioning: splitting a dataset into directories by column values so queries can skip whole directories (**partition pruning**) |
| Basics | **Hive-style** layout: `dataset/year=2025/month=03/day=14/part-0000.parquet`; partition columns stored in paths, not inside files |
| Basics | Writing partitioned data with PyArrow, pandas (`partition_cols=`), Polars, and DuckDB (`PARTITION_BY`) |
| Intermediate | Choosing partition columns: low to moderate cardinality, used in most filters, stable over time (usually a date) |
| Intermediate | Partition granularity: daily vs monthly vs hourly — matching data volume per partition to target file sizes |
| Intermediate | Partition values and types: everything in a path is a string; null values (e.g. `__HIVE_DEFAULT_PARTITION__`); special characters and URL encoding |
| Intermediate | **Idempotent partition overwrite**: rewriting only the partitions a run touched, so re-runs and backfills are safe |
| Advanced | **Over-partitioning**: high-cardinality keys (e.g. `customer_id`) creating millions of tiny directories and files |
| Advanced | Partition skew: one huge partition and many tiny ones; multi-level partitions and their combinatorial explosion |
| Advanced | Partitioning vs clustering: sorting data *within* files (Topic 02 statistics) often beats extra partition levels; bucketing (Module 2.14) and Z-ordering / clustering in table formats (Module 2.15) |
| Advanced | Object-storage behaviour: listing prefixes is slow and costs requests; request-rate limits per prefix |
| Advanced | Limits of directory partitioning: changing a partition scheme means rewriting data — the motivation for hidden partitioning and partition evolution in Iceberg (Module 2.15) |

**How to learn it**

1. Read the topic file.
2. For five query patterns on your dataset, propose a partition scheme and
   estimate files and bytes read per query.
3. Test your estimates with DuckDB `EXPLAIN ANALYZE` on MinIO.

**Hands-on exercise — `partition_design.py`**

1. Write taxi trips (or orders) with four schemes: none, `year/month`,
   `year/month/day`, and `pickup_zone` (high cardinality).
2. For each, record number of directories, number of files, average file
   size, and time and bytes read for three typical queries.
3. Implement `overwrite_partitions(df, root, partition_cols)` that replaces
   only the partitions present in `df`, writing to a temp location first;
   test that re-running it twice gives identical results and that other
   partitions are untouched.
4. Replace the `pickup_zone` partitioning with `year/month` partitions plus
   sorting by `pickup_zone` inside files, and compare results.
5. Write a one-page partitioning guideline for your team.

**Checkpoint:**

- [ ] Explain partition pruning and Hive-style paths.
- [ ] Choose partition columns and granularity for a workload.
- [ ] Explain over-partitioning and partition skew.
- [ ] Implement an idempotent partition overwrite.
- [ ] Explain when sorting within files is better than another partition
      level.

**Common mistakes:** partitioning by high-cardinality IDs; partitioning by
columns nobody filters on; queries that filter on a derived value (e.g. a
timestamp) instead of the partition column, so pruning never happens.

---

### Topic 09 — [The small-files problem and target file sizing](09-small-files-problem-and-target-file-sizing.md)

**Why here:** Partitioning and frequent writes easily create thousands of
tiny files. This topic teaches you to see, prevent, and fix the most common
performance problem in data lakes.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What counts as "small" and why it hurts: per-file open, footer read, and listing cost; poor compression; many tiny tasks in distributed engines; object-storage request charges |
| Basics | Common causes: frequent micro-batch or streaming writes, over-partitioning, many parallel writers each writing a file per partition, appending tiny daily deltas |
| Intermediate | **Target file sizes**: commonly in the range of about 128 MB to 1 GB for analytical Parquet, balanced against parallelism and partition volume |
| Intermediate | The opposite problem: files that are too large (little parallelism, slow rewrites, huge writer memory) |
| Intermediate | Prevention at write time: controlling rows per file (`max_rows_per_file`), reducing writer parallelism per partition, batching writes |
| Intermediate | **Compaction**: reading many small files in a partition and rewriting them as fewer, well-sized, sorted files |
| Advanced | Safe compaction on plain files: write new files to a temporary location, swap atomically (or via a manifest), delete old files only after readers are safe; making compaction idempotent |
| Advanced | Concurrency hazards: a query or writer running during compaction; why plain directories cannot guarantee isolation and how table formats solve it (Module 2.15) |
| Advanced | Monitoring file health: file counts, size distribution per partition, and alerts when a partition drifts out of range (Module 2.20) |
| Advanced | Scheduling compaction: which partitions to compact (recent, frequently queried) and how often |

**How to learn it**

1. Read the topic file.
2. Write a script that reports file count and size percentiles per
   partition for any dataset.
3. Generate a deliberately bad dataset (one file per minute for a month)
   and measure query time before and after compaction.

**Hands-on exercise — `compactor.py`**

1. Simulate a streaming writer that writes one small Parquet file every
   few seconds into `year/month/day` partitions (thousands of files).
2. Build `file_health_report(root)` that prints per-partition file counts,
   total size, and size percentiles, and flags unhealthy partitions.
3. Build `compact_partition(path, target_bytes)` that merges small files
   into target-sized, sorted files using `pyarrow.dataset`, writes to a
   temp prefix, swaps, and then removes old files.
4. Prove with tests: same rows and values after compaction; running it
   twice changes nothing; a crash midway leaves readable data.
5. Measure query time and object-storage request count on MinIO before and
   after compaction.

**Checkpoint:**

- [ ] Explain four costs of small files.
- [ ] Choose a target file size for a dataset and justify it.
- [ ] Compact a partition safely and idempotently.
- [ ] Explain why compaction on plain files is risky under concurrent
      readers.

**Common mistakes:** compacting by deleting old files before new ones are
committed; compacting everything every time; producing one gigantic file
per partition regardless of volume.

---

## 10. Phase E — Real-World Ingestion (Intermediate → Advanced)

### Topic 10 — [Excel, XML, and fixed-width legacy formats](10-excel-xml-and-fixed-width-legacy-formats.md)

**Why last:** Many enterprises still send data as spreadsheets, XML feeds,
and mainframe fixed-width files. Your job is to turn them into the
well-typed, well-laid-out datasets you learned to build in Topics 01–09.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Excel files: `.xlsx` (zipped XML) vs legacy `.xls`; reading with pandas engines (`openpyxl`, `calamine`) and Polars; multiple sheets, header rows, `skiprows`, `usecols` (going beyond the basics of Module 2.3) |
| Basics | XML basics: elements, attributes, text, namespaces; reading with `xml.etree.ElementTree`, `lxml`, and `pandas.read_xml` |
| Basics | Fixed-width text files: column positions instead of delimiters; `pd.read_fwf` with `colspecs` and `widths`; Polars string slicing |
| Intermediate | Excel pitfalls: dates stored as serial numbers (and the 1900 vs 1904 date systems), formulas vs cached values, merged cells, hidden rows and sheets, numbers stored as text, trailing empty rows and columns, leading zeros lost by Excel |
| Intermediate | XML at scale: streaming with `iterparse` and clearing elements to keep memory bounded; XPath queries; mapping repeated elements to child tables (the same grain rules as Topic 06) |
| Intermediate | Fixed-width pitfalls: padding and alignment, implied decimals (e.g. `0001234` meaning `12.34`), signed fields, record-type codes with different layouts per line |
| Intermediate | Layout specifications as code: a versioned layout file (CSV/YAML) that drives the parser, instead of magic numbers |
| Advanced | **XML security**: external entity (XXE) and entity-expansion ("billion laughs") attacks; using `defusedxml` for untrusted input; validating against XSD schemas with `lxml` |
| Advanced | Mainframe data (awareness to working level): COBOL copybooks as layout definitions, **EBCDIC** encodings (e.g. `cp037`), packed decimal (`COMP-3`) and binary fields |
| Advanced | Legacy-to-lake pattern: keep the original file in bronze unchanged, parse into typed Parquet in silver, record parse failures in a quarantine table, and version the layout/spec used |
| Advanced | Reconciliation with the sender: control totals and trailer records (row counts and sums in footer lines) checked on every load |

**How to learn it**

1. Read the topic file.
2. Collect or create three ugly real-world-style samples: an Excel report
   with merged header cells and a totals row, a large nested XML feed, and
   a fixed-width bank statement file with header and trailer records.
3. For each, write the target schema and grain before writing any parsing
   code.

**Hands-on exercise — `legacy_ingestion.py`**

1. **Excel** — parse a multi-sheet workbook with a two-row header, merged
   cells, serial dates, and a totals row; produce a clean typed table and
   check that its sum equals the sheet's totals row.
2. **XML** — stream-parse a 2 GB XML product feed with `iterparse` using
   bounded memory; produce `products` and `product_prices` tables; reject
   files containing DTD entity declarations using `defusedxml`.
3. **Fixed-width** — parse a file with header (`H`), detail (`D`), and
   trailer (`T`) records using a layout spec file; apply implied decimals;
   verify the trailer's record count and amount total.
4. **Mainframe (stretch)** — decode a small EBCDIC file with a `COMP-3`
   packed-decimal field.
5. Write all outputs as partitioned, zstd-compressed Parquet with your
   standard layout, and quarantine every unparseable record with a reason.
6. Test each parser with small hand-made samples, including malformed ones.

**Checkpoint:**

- [ ] Convert Excel serial dates correctly and handle merged header cells.
- [ ] Stream-parse a large XML file with bounded memory.
- [ ] Explain XXE and "billion laughs" and how to prevent them.
- [ ] Parse fixed-width records with implied decimals and control totals.
- [ ] Describe the legacy-to-lake pattern.

**Common mistakes:** trusting Excel's displayed values over the stored
ones; parsing untrusted XML with default settings; hard-coding column
positions throughout the code; skipping control-total checks.

---

## 11. Consolidate — practice questions

When all ten topics are done, open
[`practice-questions.md`](practice-questions.md). For every question:

1. Describe the workload: write pattern, read pattern, filters, size, and
   growth per day.
2. Decide format, codec, partition scheme, sort order, and target file
   size — and write one sentence of justification for each.
3. Estimate file counts, file sizes, and bytes read per typical query.
4. Implement it and measure the real numbers.
5. Explain the gap between your estimate and the measurement.

---

## 12. Module mini-project — from messy sources to an optimized lake layout

This is the proof that you have finished the module.

**Scenario:** A retail company's lake is slow and expensive. It receives:

- daily Excel store reports (one workbook per region, several sheets);
- an XML product catalogue feed (several GB);
- fixed-width bank settlement files with header and trailer records;
- nested JSON Lines order events from the web app;
- Avro files of inventory changes from a CDC tool;

and its current "lake" is thousands of small, gzipped CSV files
partitioned by `store_id`.

Build `lake_layout/`, a `uv` project with:

1. **Bronze** — every source landed unchanged in MinIO, with ingestion
   metadata recorded in a manifest file.
2. **Parsers** — typed, tested parsers for all five sources, with
   quarantine tables and control-total checks.
3. **Silver layout** — Parquet with explicit schemas, a chosen codec per
   dataset, a partition scheme per dataset, sort order for statistics, and
   a target file size. Nested orders split into related tables without
   double counting.
4. **Migration** — convert the legacy small-file CSV lake into the new
   layout with idempotent partition overwrites.
5. **Compaction** — a `compactor` job with a file-health report, safe swap,
   and tests.
6. **Evidence** — a benchmark comparing the old and new layouts for five
   business queries in DuckDB on MinIO: time, bytes read, file count, and
   storage size — plus a monthly cost estimate.
7. **Layout standard** — a written document (your team's "data layout
   standard") covering format per layer, codecs, partitioning rules, file
   sizes, and compaction policy.

**Grading yourself:** every choice in the layout standard is backed by a
measurement from this module; the new layout reads at least 10× fewer
bytes for the typical queries; every parser has tests with malformed input;
and every load reconciles against source control totals.

---

## 13. Module self-assessment — exit criteria

Only move to Module 2.6 when you can tick every box without looking at your
notes:

- [ ] I can explain row vs columnar storage, PAX, and splittability.
- [ ] I can explain Parquet internals and read a file's metadata.
- [ ] I can write Parquet with PyArrow using deliberate row-group, encoding,
      codec, and statistics settings.
- [ ] I can read, write, and evolve Avro files.
- [ ] I can compare ORC, Parquet, Avro, Arrow IPC, CSV, and JSON Lines and
      choose per layer.
- [ ] I can flatten and explode nested data without changing grain by
      accident.
- [ ] I can choose codecs from measured trade-offs.
- [ ] I can design partition layouts and implement idempotent partition
      overwrites.
- [ ] I can diagnose and compact small files safely.
- [ ] I can ingest Excel, XML, and fixed-width files securely and reconcile
      them.
- [ ] I have finished all practice questions and the mini-project.

---

## 14. Recommended reading and references

| Resource | Relevant topics |
| --- | --- |
| Apache Parquet documentation — file format, encodings, page index, bloom filters, nested encoding | 02, 03 |
| *Dremel: Interactive Analysis of Web-Scale Datasets* (Google, 2010) — the paper behind Parquet's nested encoding | 02, 06 |
| PyArrow documentation — "Reading and Writing the Apache Parquet Format" and "Tabular Datasets" | 03, 08, 09 |
| Apache Avro specification; `fastavro` documentation | 04 |
| Apache ORC specification | 05 |
| Zstandard, LZ4, and Snappy project documentation and benchmarks | 07 |
| DuckDB documentation — Parquet, partitioned writes, Hive partitioning | 02, 08 |
| Python `xml` security documentation and `defusedxml` documentation | 10 |
| *Designing Data-Intensive Applications* — Martin Kleppmann, chapters on encoding and storage | 01, 04, 07 |

---

## 15. Where this module leads

| This module's idea | Where it goes deeper |
| --- | --- |
| Loading files into databases | 2.7 Python Database Connectivity — bulk loading with `COPY` |
| Nested and event data | 2.8 Data Modelling — modelling event and clickstream data |
| File-drop and SFTP sources | 2.9 Data Ingestion and Extraction Patterns |
| Schema evolution across files | 2.11 Data Validation — schema evolution and compatibility rules |
| Bucketing and file layout in Spark | 2.14 PySpark — partitioning, bucketing, and save modes |
| Atomic commits, compaction, Z-ordering, hidden partitioning | 2.15 Lakehouse Table Formats |
| Avro and Protobuf with a schema registry | 2.16 Streaming and Event-Driven Data |
| Object storage, storage classes, and cost | 2.17 Cloud Storage and Cloud Data Platforms |
| File-health monitoring | 2.20 Observability, Lineage, Governance, and Security |
| Predicate pushdown and projection pruning at scale | 2.21 Performance, Scaling, and Cost Optimization |

Formats and layouts are decisions you make once and pay for on every query
for years. The measure-first habit you practise here — predict, write,
inspect, measure, and only then standardise — is what keeps a data lake
fast and affordable as it grows from gigabytes to petabytes.
