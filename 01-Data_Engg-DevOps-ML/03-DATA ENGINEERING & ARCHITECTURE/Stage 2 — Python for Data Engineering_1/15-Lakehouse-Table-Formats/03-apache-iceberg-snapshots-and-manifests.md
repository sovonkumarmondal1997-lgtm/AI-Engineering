# CLAUDE CODE PROMPT — LEARN `03-apACHE-ICEBERG-SNAPSHOTS-AND-MANIFESTS.md`

You are a **Senior Data Engineer with 10+ years of production experience** designing enterprise data platforms, lakehouses, distributed data systems, Apache Spark pipelines, CDC systems, object-storage architectures, and multi-engine analytical platforms.

I am learning:

```text
Python for Data Engineering/
└── 15-Lakehouse-Table-Formats/
    └── 03-apache-iceberg-snapshots-and-manifests.md
```

Your job is to teach me the **complete subject covered by `03-apache-iceberg-snapshots-and-manifests.md`**, progressing from absolute beginner level to advanced production-level understanding.

This is one of the most important topics in Module 2.15 because I need to understand **how Apache Iceberg actually represents table state internally**, rather than merely learning how to create an Iceberg table with Spark.

The objective is:

> **I should understand how Iceberg's metadata tree, snapshots, manifests, catalog pointer, partition transforms, schema IDs, and delete files work together to make a collection of Parquet files behave like a reliable analytical table.**

---

# 1. CRITICAL SCOPE RULE

Teach ONLY the concepts belonging to:

```text
03-apache-iceberg-snapshots-and-manifests.md
```

Do NOT modify any other curriculum file.

Do NOT modify:

```text
01-why-open-table-formats-exist.md
02-delta-lake-transaction-log.md
04-apache-hudi-overview.md
05-acid-merge-update-and-delete-on-data-lakes.md
06-time-travel-and-table-versioning.md
07-compaction-z-ordering-and-liquid-clustering.md
08-vacuum-retention-and-table-maintenance.md
09-catalogs-hive-metastore-glue-unity-and-polaris.md
practice-questions.md
```

Do not change:

- filenames
- topic ordering
- curriculum structure
- roadmap scope

Do not turn this lesson into a generic Apache Iceberg tutorial.

The teaching must remain centered on:

> **Iceberg snapshots, metadata, manifests, partitioning, schema evolution, deletes, and multi-engine access.**

You may briefly reference earlier concepts from Topics 01–02 when necessary, but do not reteach them in full.

---

# 2. AUTHORITATIVE ROADMAP SCOPE

The roadmap requires this topic to cover all of the following.

## Basics

- Iceberg metadata tree
- Catalog pointer
- Table metadata JSON
- Snapshots
- Manifest lists
- Manifest files
- Parquet data files
- Creating Iceberg tables from Spark
- Creating Iceberg tables from Python
- PyIceberg
- Local SQL/SQLite catalog
- Iceberg metadata tables
- `snapshots`
- `history`
- `files`
- `manifests`
- `partitions`

## Intermediate

- Iceberg commit process
- Writing new data and metadata files
- Atomic catalog pointer swap
- Catalog as the commit point
- Hidden partitioning
- Partition transforms
- `day(ts)`
- `month(ts)`
- `bucket(n, col)`
- `truncate(n, col)`
- Partition evolution
- Schema evolution using column IDs
- Safe add/drop/rename/reorder/type widening
- Manifest-level statistics
- File-level statistics
- Data pruning
- Why Iceberg avoids unnecessary directory listing

## Advanced

- Row-level deletes
- Position delete files
- Equality delete files
- Copy-on-write
- Merge-on-read
- Format version 2
- Format version 3 awareness
- Deletion vectors
- Row lineage
- `VARIANT`
- Default values
- Sort orders
- Multi-engine access
- PyIceberg → Arrow
- DuckDB Iceberg extension
- Polars `scan_iceberg`
- Warehouse/query-engine compatibility

Do not skip any of these.

---

# 3. START WITH THE CORE QUESTION

Begin with:

> **"If Iceberg stores data in Parquet files, where does Iceberg actually keep the information that tells us which files belong to the current table?"**

Do not immediately give me the complete answer.

First establish the mental model.

Then progressively build:

```text
Catalog
   ↓
Table Metadata
   ↓
Snapshot
   ↓
Manifest List
   ↓
Manifest Files
   ↓
Parquet Data Files
```

This hierarchy is the foundation of the entire lesson.

---

# 4. FIRST EXPLAIN WHAT APACHE ICEBERG IS

Assume I know basic Python and data engineering but do not assume I understand Iceberg internals.

Explain:

> Apache Iceberg is an open table format for large analytical datasets stored on object storage.

Then clarify:

```text
Iceberg ≠ Parquet
```

Instead:

```text
Iceberg
   +
Parquet
   +
Metadata
   +
Catalog
```

Explain what each component contributes.

Compare:

```text
Plain Parquet Dataset
```

with:

```text
Iceberg Table
```

but keep the comparison focused on Iceberg's architecture.

---

# 5. BUILD A SIMPLE ICEBERG TABLE

Create a small table:

```text
customers
```

with:

```text
customer_id
name
email
country
created_at
```

Use a small dataset.

Example:

```python
customers = [
    (1, "Alice", "alice@example.com", "IN"),
    (2, "Bob", "bob@example.com", "US"),
    (3, "Charlie", "charlie@example.com", "UK"),
]
```

Create it using Spark.

Then create/read an Iceberg table using PyIceberg where practical.

Use a local development catalog suitable for the environment, such as a SQL/SQLite catalog.

Do not assume cloud infrastructure is required for the basic lesson.

---

# 6. INSPECT THE PHYSICAL TABLE STRUCTURE

After creating the table, inspect the table's storage layout.

Show a conceptual structure such as:

```text
warehouse/
└── customers/
    ├── metadata/
    │   ├── v1.metadata.json
    │   ├── v2.metadata.json
    │   ├── snap-....avro
    │   └── ...
    │
    └── data/
        ├── 00000-....parquet
        ├── 00001-....parquet
        └── ...
```

Make clear that exact filenames/layout can differ by engine/version.

The important conceptual structure is:

```text
Catalog Pointer
      ↓
Table Metadata
      ↓
Snapshot
      ↓
Manifest List
      ↓
Manifest
      ↓
Data File
```

---

# 7. TEACH THE ICEBERG METADATA TREE

This is the most important concept.

Build the model:

```text
                 CATALOG
                    │
                    ▼
           Table Metadata JSON
                    │
                    ▼
                Snapshot
                    │
                    ▼
             Manifest List
                    │
                    ▼
              Manifest Files
                    │
                    ▼
             Parquet Files
```

Explain every layer.

For every layer answer:

```text
What is it?
Why does it exist?
What does it point to?
Who reads it?
When does it change?
How does it contribute to table state?
```

Do not allow me to memorize only names.

---

# 8. CATALOG POINTER

Explain why Iceberg needs a catalog.

At a high level:

```text
catalog
   ↓
table name
   ↓
current metadata file
```

Explain that the catalog provides the current metadata location.

Use an analogy if helpful:

```text
Catalog = pointer telling us which version of the table metadata is current.
```

Make clear this is a conceptual analogy.

Do not teach the complete catalog ecosystem yet. Topic 09 handles catalogs in depth.

---

# 9. TABLE METADATA JSON

Explain what table metadata contains conceptually.

Cover:

- schema
- schemas/field IDs
- partition specification
- partition spec ID
- sort order information
- snapshots
- current snapshot
- snapshot references where relevant
- metadata/logical state
- table properties

Do not overwhelm me with every possible metadata field.

Focus on the fields needed to understand table state.

---

# 10. SNAPSHOTS

Explain:

```text
Snapshot
```

as a consistent representation of the table at a point in time.

Build:

```text
Snapshot 1
   ↓
Snapshot 2
   ↓
Snapshot 3
```

Explain:

- why snapshots exist
- what changes create snapshots
- how snapshots reference manifests
- how snapshots support time travel
- how snapshots support reproducibility
- how snapshots support auditing

Do not turn this into the full Topic 06 time-travel lesson.

This lesson should explain the **internal role of snapshots**.

---

# 11. MANIFEST LIST

Explain:

```text
Snapshot
   ↓
Manifest List
```

What is a manifest list?

Explain:

- why it exists
- what it points to
- relationship to manifests
- how it helps organize metadata
- why it improves planning

Explain the difference between:

```text
Manifest List
```

and:

```text
Manifest
```

This distinction must be crystal clear.

---

# 12. MANIFEST FILES

Explain:

```text
Manifest
```

as metadata describing data files.

Explain that manifests contain information about data files such as:

- file path
- partition information
- record count
- file size
- column statistics
- lower bounds
- upper bounds
- file format
- sequence information where relevant

Explain why storing this metadata separately from the Parquet data helps query planning.

---

# 13. BUILD A CONCRETE EXAMPLE

Use:

```text
Snapshot 3
```

containing:

```text
Manifest List
   ├── Manifest A
   ├── Manifest B
   └── Manifest C
```

Then:

```text
Manifest A
   ├── file-001.parquet
   ├── file-002.parquet
   └── file-003.parquet

Manifest B
   ├── file-004.parquet
   └── file-005.parquet

Manifest C
   ├── file-006.parquet
   └── file-007.parquet
```

Make me trace:

```text
Table
 ↓
Snapshot
 ↓
Manifest List
 ↓
Manifest
 ↓
Data File
```

Then ask me to reproduce the hierarchy without notes.

---

# 14. CREATE MULTIPLE SNAPSHOTS

Perform:

```text
Write 1
Write 2
Write 3
```

After every write inspect:

- table metadata
- snapshot metadata
- manifest list
- manifests
- data files

Ask me to predict:

```text
What metadata changes?
What data files are added?
Which snapshot becomes current?
Which manifest files change?
```

Then execute.

Compare:

```text
Prediction
vs
Actual metadata
```

This prediction-before-execution loop is mandatory.

---

# 15. ICEBERG METADATA TABLES

Teach:

```text
snapshots
history
files
manifests
partitions
```

Explain what each answers.

Create a table:

| Metadata Table | Main Question |
|---|---|
| snapshots | What snapshots exist? |
| history | How did table state evolve? |
| files | What data files exist? |
| manifests | What manifests exist? |
| partitions | What partition information exists? |

Then query them.

Show practical examples.

---

# 16. USE METADATA TABLES AS A DEBUGGING TOOL

Give me scenarios such as:

> "Why is this table scanning so many files?"

Use:

```text
files
partitions
manifests
```

to investigate.

Another scenario:

> "Why did the table suddenly grow?"

Use:

```text
snapshots
history
files
```

Another:

> "How many files are associated with the current snapshot?"

Make me solve it using metadata.

---

# 17. EXPLAIN THE ICEBERG COMMIT MODEL

This is critical.

Start with:

```text
Writer
  ↓
write data files
  ↓
write manifest(s)
  ↓
write manifest list
  ↓
write new table metadata
  ↓
atomically update catalog pointer
```

Explain why the catalog pointer is the commit point.

Build this mental model:

```text
Old Metadata
     ↓
Current Snapshot
```

then:

```text
New Metadata
     ↓
New Snapshot
```

Then:

```text
Catalog
   ↓
atomic pointer swap
```

Explain why readers can continue seeing the old snapshot until the new metadata becomes current.

---

# 18. COMPARE ICEBERG COMMIT WITH DELTA

Since Topic 02 was about Delta, create a focused comparison:

| Concept | Delta | Iceberg |
|---|---|---|
| Main metadata model | Transaction log | Metadata tree |
| Current state | Log-derived snapshot | Metadata/snapshot tree |
| Commit coordination | Transaction-log commit | Catalog pointer update |
| Data files | Parquet | Parquet |
| Snapshots | Yes | Yes |
| Manifests | Different mechanism | Core concept |
| Catalog importance | Mainly discovery/governance | Critical commit point |

Explain this only at the architectural level.

Do not turn the lesson into a complete Delta-vs-Iceberg comparison.

---

# 19. ATOMIC CATALOG POINTER SWAP

Explain:

```text
Before:
catalog → metadata-v10.json

After:
catalog → metadata-v11.json
```

The pointer changes atomically.

Explain why:

```text
Reader A
```

can continue using:

```text
metadata-v10
```

while:

```text
Reader B
```

uses:

```text
metadata-v11
```

depending on when the read starts.

This should establish the foundation for snapshot isolation.

---

# 20. HIDDEN PARTITIONING

This is a major roadmap requirement.

Start with the traditional approach:

```text
orders/
year=2026/
month=10/
day=05/
```

Then explain the problem with exposing partition columns directly to users.

Introduce:

```text
Hidden Partitioning
```

Explain:

> Users query the actual timestamp/date column rather than manually referencing partition columns.

For example:

```sql
SELECT *
FROM trips
WHERE pickup_ts >= '2026-10-05'
  AND pickup_ts <  '2026-10-06';
```

The table's partition transform can still prune files.

---

# 21. PARTITION TRANSFORMS

Teach each roadmap transform separately.

## `day(ts)`

Explain:

```text
timestamp
   ↓
day transform
```

Use examples.

## `month(ts)`

Explain:

```text
timestamp
   ↓
month transform
```

Explain when month-level partitioning is preferable.

## `bucket(n, col)`

Explain:

```text
customer_id
   ↓
bucket(32, customer_id)
```

Explain why buckets can distribute data.

## `truncate(n, col)`

Explain:

```text
string / numeric
   ↓
truncate transform
```

Explain why truncation can create useful coarse grouping.

For each transform cover:

```text
What?
Why?
Example?
Advantages?
Trade-offs?
Query impact?
```

---

# 22. HANDS-ON HIDDEN PARTITIONING LAB

Create:

```text
silver.trips
```

partitioned by:

```text
day(pickup_ts)
```

Then run:

```sql
SELECT *
FROM silver.trips
WHERE pickup_ts = ...
```

Show that the query does NOT need to reference a physical partition column.

Inspect the query plan where practical.

Demonstrate partition pruning.

Explain:

```text
User filter
     ↓
Partition transform
     ↓
Partition pruning
     ↓
Manifest/file pruning
     ↓
Less data scanned
```

---

# 23. PARTITION EVOLUTION

Explain the problem:

```text
Initial partition:
day(timestamp)
```

Later the workload changes.

We now want:

```text
month(timestamp)
```

Explain why rewriting all historical data just to change the partition strategy is undesirable.

Introduce:

> Partition evolution allows new data to use a new partition specification while old data remains under the old specification.

Create a conceptual example:

```text
Old data
   ↓
day partitioning

New data
   ↓
month partitioning
```

Then:

```text
One logical table
+
Multiple partition specifications
```

Explain how queries can work across both.

---

# 24. HANDS-ON PARTITION EVOLUTION LAB

Perform:

1. Create a table partitioned by `day(pickup_ts)`.
2. Write several batches.
3. Evolve the partition specification to `month(pickup_ts)`.
4. Write new data.
5. Query across old and new data.
6. Inspect metadata.
7. Identify which data uses which partition specification.

Make me predict:

```text
Will old files be rewritten?
Will new files use the new partition transform?
Can one table contain both?
```

Then verify.

---

# 25. SCHEMA EVOLUTION WITH COLUMN IDS

This is extremely important.

Explain why column names alone are not enough.

Example:

```text
Initial:
customer_id
name
email
```

Then:

```text
rename email → email_address
```

Explain how a system can preserve the logical identity of the column using a field ID.

Build:

```text
Field ID 1 → customer_id
Field ID 2 → name
Field ID 3 → email
```

Then:

```text
Field ID 3 → email_address
```

The physical/logical name changes, but the field identity remains.

---

# 26. TEACH SAFE SCHEMA EVOLUTION

Cover:

- add column
- drop column
- rename column
- reorder column
- type widening

Explain why Iceberg's column IDs make these operations safer.

Do not merely state:

> "Iceberg uses field IDs."

Show exactly why this matters.

---

# 27. HANDS-ON SCHEMA EVOLUTION LAB

Perform:

1. Create a table.
2. Add a column.
3. Rename a column.
4. Reorder columns.
5. Perform a compatible type widening where supported.
6. Read old data using the new schema.

Inspect metadata.

Explain how column IDs protect the interpretation of old files.

---

# 28. FILE-LEVEL STATISTICS

Explain the statistics stored in manifests.

Use an example:

```text
File A
amount:
min = 10
max = 100

File B
amount:
min = 1000
max = 2000
```

Query:

```sql
WHERE amount > 1500
```

Explain why:

```text
File A
```

can potentially be skipped.

Build:

```text
Query
 ↓
Manifest statistics
 ↓
File pruning
 ↓
Less data scanned
```

---

# 29. MANIFEST-LEVEL PRUNING

Explain that Iceberg can use metadata before opening every Parquet file.

Teach:

```text
Query predicate
      ↓
Partition metadata
      ↓
Manifest metadata
      ↓
File statistics
      ↓
Selected files
      ↓
Parquet scan
```

Explain why this is more scalable than simply listing every directory and inspecting every file.

---

# 30. WHY ICEBERG AVOIDS EXPENSIVE DIRECTORY LISTING

Explain the problem with:

```text
Object storage
   ↓
millions of files
   ↓
list everything
   ↓
inspect everything
```

Then:

```text
Iceberg metadata
   ↓
metadata-driven planning
   ↓
identify relevant manifests/files
   ↓
read only necessary files
```

Connect this to:

- large tables
- cloud object storage
- query planning
- performance
- cost

---

# 31. ROW-LEVEL DELETE FILES

Now move to advanced concepts.

Explain why row-level deletes are difficult if we only rewrite Parquet files.

Introduce Iceberg format v2 row-level deletes.

Teach:

```text
Position Delete
```

and:

```text
Equality Delete
```

---

# 32. POSITION DELETE FILES

Explain conceptually:

```text
Data file:
file-001.parquet

Delete file:
row positions:
17
31
42
```

Explain:

- what a position delete identifies
- why it can avoid rewriting the entire data file
- read-time implications
- maintenance implications

---

# 33. EQUALITY DELETE FILES

Explain:

```text
Delete rows where:
customer_id = 123
```

Conceptually.

Explain:

- equality conditions
- why this is different from position deletes
- use cases
- trade-offs

Create a comparison:

| Delete Type | Identifies Row By |
|---|---|
| Position delete | File + row position |
| Equality delete | Column value(s) |

---

# 34. COPY-ON-WRITE VS MERGE-ON-READ

Explain:

## Copy-on-write

```text
Update
 ↓
rewrite affected Parquet files
```

## Merge-on-read

```text
Update/Delete
 ↓
write delete/update metadata/files
 ↓
reader merges state
```

Explain trade-offs:

| Dimension | Copy-on-write | Merge-on-read |
|---|---|---|
| Write cost | Higher | Lower |
| Read complexity | Lower | Higher |
| Freshness | Simple | Requires merge |
| File rewrites | More | Less |
| Maintenance | Simpler | More important |

Do not teach complete Topic 05 semantics.

Keep the focus on how Iceberg metadata and delete files represent changes.

---

# 35. FORMAT VERSION 2

Explain why format version 2 matters.

At a high level:

```text
Format v1
   ↓
basic table capabilities
```

then:

```text
Format v2
   ↓
row-level delete support
   ↓
position/equality delete files
```

Explain that engine support must be checked.

---

# 36. FORMAT VERSION 3 AWARENESS

The roadmap requires awareness of:

- deletion vectors
- row lineage
- `VARIANT`
- default values

Do NOT teach all of these deeply.

For each explain:

```text
What problem does it address?
Why does the format need it?
What compatibility question should an engineer ask?
```

Make clear:

> Format-version/feature support varies by engine and version.

---

# 37. SORT ORDERS

Introduce Iceberg table sort orders.

Explain:

```text
Sort order
   ↓
organize rows within data files
   ↓
better locality
   ↓
better statistics/pruning
   ↓
potentially better query performance
```

Explain that sorting is different from partitioning.

Create a comparison:

| Partitioning | Sorting |
|---|---|
| Controls coarse data grouping | Controls row ordering |
| Helps partition pruning | Helps locality/statistics |
| Transform-based | Order-based |
| Can reduce candidate files | Can improve file-level pruning |

Do not go deeply into Topic 07.

---

# 38. MULTI-ENGINE ACCESS

The roadmap explicitly requires:

```text
Spark
PyIceberg
DuckDB
Polars
```

to work with Iceberg.

Build:

```text
                 Iceberg Table
                      │
       ┌──────────────┼──────────────┐
       ▼              ▼              ▼
    Spark         PyIceberg       DuckDB
                                      │
                                      ▼
                                   Polars
```

Explain that all engines should ultimately understand the same Iceberg table metadata and data files.

---

# 39. PYICEBERG

Use:

```python
from pyiceberg.catalog import ...
```

or the appropriate currently supported API.

Show how to:

- load a table
- inspect schema
- inspect snapshots
- inspect metadata
- read table data into Arrow where appropriate

Use a local SQL/SQLite catalog if suitable.

Explain what PyIceberg is doing.

---

# 40. PYICEBERG → ARROW

Demonstrate:

```text
Iceberg
   ↓
PyIceberg
   ↓
Arrow
   ↓
Python analysis
```

Explain why this is useful.

Connect this to earlier Module 2.4 knowledge of Arrow.

---

# 41. DUCKDB ICEBERG ACCESS

Show how DuckDB can query an Iceberg table.

Explain:

```text
DuckDB
   ↓
Iceberg metadata
   ↓
selected Parquet files
   ↓
query result
```

Where syntax depends on the installed DuckDB version, verify it before executing.

---

# 42. POLARS `scan_iceberg`

Demonstrate:

```python
pl.scan_iceberg(...)
```

or the currently supported equivalent.

Explain:

- lazy access
- query planning
- interoperability
- feature compatibility

Again, check installed versions.

---

# 43. ENGINE COMPATIBILITY

This is mandatory.

Never claim:

> "Iceberg works identically everywhere."

Instead teach:

```text
Format feature
      ↓
Engine version
      ↓
Read support?
      ↓
Write support?
      ↓
Catalog support?
      ↓
Feature limitations?
```

Create a compatibility matrix for the actual environment used.

---

# 44. REQUIRED HANDS-ON PROJECT

Use:

```text
lakehouse_lab/
```

with:

```text
lakehouse_lab/
├── docker-compose.yml
├── conf/
├── src/
│   └── lakehouse_lab/
│       └── iceberg_internals.py
├── notebooks_or_scripts/
└── tests/
```

Do not modify unrelated curriculum files.

The primary implementation should be:

```text
src/lakehouse_lab/iceberg_internals.py
```

---

# 45. BUILD AN ICEBERG METADATA INSPECTOR

Create a Python tool that can display:

```text
table metadata
current snapshot
snapshot history
manifest list
manifest files
data files
partition information
file statistics
```

The tool should conceptually support:

```text
show_table_metadata()
show_snapshots()
show_history()
show_manifests()
show_files()
show_partitions()
show_file_statistics()
```

Do not build an unnecessarily huge framework.

The purpose is learning Iceberg internals.

---

# 46. REQUIRED EXPERIMENT SEQUENCE

Follow this sequence:

```text
Experiment 1
Create Iceberg table
        ↓
Experiment 2
Inspect metadata tree
        ↓
Experiment 3
Append data
        ↓
Experiment 4
Inspect snapshots
        ↓
Experiment 5
Inspect manifest list
        ↓
Experiment 6
Inspect manifests
        ↓
Experiment 7
Query metadata tables
        ↓
Experiment 8
Hidden partitioning
        ↓
Experiment 9
Partition evolution
        ↓
Experiment 10
Schema evolution
        ↓
Experiment 11
File statistics/pruning
        ↓
Experiment 12
Position/equality deletes
        ↓
Experiment 13
Copy-on-write vs merge-on-read
        ↓
Experiment 14
Sort order
        ↓
Experiment 15
PyIceberg
        ↓
Experiment 16
DuckDB
        ↓
Experiment 17
Polars
```

For every experiment:

```text
Predict
→ Execute
→ Inspect
→ Explain
→ Compare
→ Document
```

---

# 47. METADATA INSPECTION IS MANDATORY

Do not treat Iceberg as a black box.

After each important operation inspect:

```text
metadata JSON
snapshots
manifest list
manifest files
data files
partition metadata
statistics
```

Ask:

```text
What changed?
Why did it change?
Which layer changed?
Which layer stayed the same?
What does the current snapshot point to?
```

---

# 48. BUILD A MANUAL TABLE-STATE WALKTHROUGH

Give me a concrete example:

```text
Snapshot 1
   ↓
Manifest A
   ↓
Files 1, 2

Snapshot 2
   ↓
Manifest B
   ↓
Files 1, 2, 3

Snapshot 3
   ↓
Manifest C
   ↓
Files 2, 3, 4
```

Make me trace the current state.

Then introduce a delete file.

Make me explain:

```text
Data file
+
Delete file
=
Logical table state
```

This must be understood before moving on.

---

# 49. DEBUGGING SCENARIOS

Create problems such as:

### Problem 1

A user asks:

> "Why does the table contain both old and new data files?"

Make me inspect snapshots/manifests.

### Problem 2

A query scans too many files.

Make me inspect:

```text
partitions
manifests
statistics
```

### Problem 3

Partition strategy changed.

Ask:

> "Did Iceberg rewrite all historical data?"

Make me reason about partition evolution.

### Problem 4

A column was renamed.

Ask:

> "How does Iceberg know it is still the same logical field?"

Make me reason about field IDs.

### Problem 5

Rows were deleted.

Ask:

> "Where is the deletion represented?"

Make me distinguish:

```text
position delete
vs
equality delete
```

---

# 50. COMMON MISCONCEPTIONS

Explicitly test and correct these:

```text
"Iceberg is a storage format like Parquet."
```

```text
"Manifest files contain the actual table data."
```

```text
"A snapshot is a copy of the entire table."
```

```text
"The manifest list and manifest are the same thing."
```

```text
"Changing partitioning requires rewriting all old data."
```

```text
"Partition columns must always appear in the user's SQL."
```

```text
"Renaming a column is dangerous because old Parquet files contain the old name."
```

```text
"Delete means the original Parquet bytes immediately disappear."
```

```text
"All Iceberg engines support every Iceberg feature."
```

```text
"Format version 3 automatically means every engine supports the new features."
```

```text
"Sorting and partitioning are the same thing."
```

For each misconception, explain the correct mental model.

---

# 51. PRODUCTION SCENARIOS

Use realistic scenarios.

## Scenario A — Large Trips Table

```text
billions of rows
pickup_ts
dropoff_ts
pickup_zone
```

Ask me to choose partitioning.

---

## Scenario B — Changing Query Patterns

Initially:

```text
day(timestamp)
```

Later:

```text
month(timestamp)
```

Ask me to design partition evolution.

---

## Scenario C — Multi-Engine Platform

```text
Spark writes
PyIceberg processes
DuckDB analysts query
Polars performs local analytics
```

Ask me to explain the shared architecture.

---

## Scenario D — CDC Deletes

```text
PostgreSQL
   ↓
CDC
   ↓
Iceberg
```

Ask me how row-level deletes could be represented.

Keep the answer scoped to this topic.

---

# 52. ARCHITECTURE DIAGRAM

Build and repeatedly use:

```text
                         Catalog
                            │
                            ▼
                  Table Metadata JSON
                            │
                            ▼
                        Snapshot
                            │
                            ▼
                    Manifest List
                            │
               ┌────────────┼────────────┐
               ▼            ▼            ▼
           Manifest A    Manifest B    Manifest C
               │            │            │
               ▼            ▼            ▼
           Parquet        Parquet      Parquet
             Files          Files        Files
```

Then add:

```text
Delete Files
```

to the diagram.

Explain how they participate in logical table state.

---

# 53. COMPARE DELTA'S LOG MODEL WITH ICEBERG'S METADATA TREE

Ask me to explain:

```text
Delta:
ordered transaction log
```

versus:

```text
Iceberg:
catalog
  ↓
metadata
  ↓
snapshot
  ↓
manifest list
  ↓
manifests
  ↓
files
```

Do not tell me which one is universally better.

Teach me the architectural differences and trade-offs.

---

# 54. ADVANCED REASONING QUESTION

Ask:

> If the catalog points to metadata-v10 and a writer prepares metadata-v11, when does v11 become the current table?

Make me reason about the atomic catalog pointer update.

---

# 55. SECOND ADVANCED QUESTION

Ask:

> Why doesn't Iceberg simply store one huge metadata file containing every data file in the table?

Guide me toward understanding:

- scalability
- manifests
- metadata organization
- incremental changes
- planning efficiency

---

# 56. THIRD ADVANCED QUESTION

Ask:

> Why are manifests separate from Parquet files?

Make me reason about:

```text
data
vs
metadata
```

and:

```text
query planning
vs
data scanning
```

---

# 57. FOURTH ADVANCED QUESTION

Ask:

> Why can Iceberg change its partition specification without rewriting all historical data?

Make me explain:

```text
partition specification
+
partition spec IDs
+
metadata
+
old files
+
new files
```

---

# 58. FIFTH ADVANCED QUESTION

Ask:

> Why does Iceberg use field IDs instead of relying only on column names?

Make me explain the schema-evolution problem.

---

# 59. LEARNING CHECKPOINTS

After each major section stop and test me.

Ask questions such as:

```text
What is the Iceberg metadata tree?

What is a snapshot?

What is a manifest list?

What is a manifest?

What is the difference between a manifest list and a manifest?

What does the catalog point to?

Why is the catalog pointer important?

What is hidden partitioning?

What is day(ts)?

What is month(ts)?

What is bucket(n, col)?

What is truncate(n, col)?

What is partition evolution?

Why are field IDs important?

What are position deletes?

What are equality deletes?

What is copy-on-write?

What is merge-on-read?

Why are statistics stored in metadata?

How does Iceberg avoid unnecessary file listing?
```

If I answer incorrectly:

1. Identify the exact misconception.
2. Re-explain it using a smaller example.
3. Give another analogy.
4. Ask a similar question.
5. Continue only when I demonstrate understanding.

---

# 60. FINAL ASSESSMENT

After completing the lesson, conduct:

## Basic — 10 questions

Focus on:

- Iceberg
- metadata tree
- snapshots
- manifests
- Parquet

## Intermediate — 10 questions

Focus on:

- commits
- hidden partitioning
- partition transforms
- partition evolution
- schema evolution
- metadata tables

## Advanced — 10 questions

Focus on:

- manifest architecture
- delete files
- COW vs MOR
- format versions
- sort orders
- multi-engine interoperability

## Production Architecture — 5 scenarios

Each scenario should require me to reason about a real lakehouse workload.

Do not immediately provide answers.

Wait for my responses and grade them.

---

# 61. FINAL PRACTICAL CHALLENGE

Give me this problem:

> A company has a 5-billion-row trips table stored in object storage. Spark writes daily data. Analysts use DuckDB and Trino-like engines. Query patterns frequently filter on `pickup_ts` and `pickup_zone`. The company wants to change partition strategy over time without rewriting historical data. CDC deletes are also arriving.

Ask me to design the Iceberg table.

I must explain:

```text
Catalog
↓
Table Metadata
↓
Snapshots
↓
Manifest List
↓
Manifests
↓
Parquet
↓
Partitioning
↓
Partition Evolution
↓
Statistics
↓
Delete Files
↓
Multi-Engine Access
```

Do not solve it first.

Review my design as a Senior Data Engineer.

---

# 62. FINAL EXIT CRITERIA

Do not consider this topic complete until I can explain without notes:

- [ ] What Apache Iceberg is
- [ ] Why Iceberg uses Parquet
- [ ] Iceberg metadata tree
- [ ] Catalog pointer
- [ ] Table metadata JSON
- [ ] Snapshots
- [ ] Manifest lists
- [ ] Manifest files
- [ ] Data files
- [ ] How Iceberg commits changes
- [ ] Why the catalog pointer is the commit point
- [ ] Iceberg metadata tables
- [ ] `snapshots`
- [ ] `history`
- [ ] `files`
- [ ] `manifests`
- [ ] `partitions`
- [ ] Hidden partitioning
- [ ] `day(ts)`
- [ ] `month(ts)`
- [ ] `bucket(n, col)`
- [ ] `truncate(n, col)`
- [ ] Partition evolution
- [ ] Column IDs
- [ ] Add/drop/rename/reorder/type widening
- [ ] Manifest statistics
- [ ] File statistics
- [ ] File pruning
- [ ] Why directory listing can be avoided
- [ ] Position deletes
- [ ] Equality deletes
- [ ] Copy-on-write
- [ ] Merge-on-read
- [ ] Iceberg format v2
- [ ] Iceberg format v3 awareness
- [ ] Deletion vectors awareness
- [ ] Row lineage awareness
- [ ] `VARIANT` awareness
- [ ] Default values awareness
- [ ] Sort orders
- [ ] PyIceberg
- [ ] PyIceberg → Arrow
- [ ] DuckDB Iceberg access
- [ ] Polars `scan_iceberg`
- [ ] Engine compatibility

Most importantly, I should be able to answer:

> **"How does Iceberg know exactly which Parquet files belong to the current version of a table without relying on an expensive directory listing?"**

I should be able to explain:

```text
Catalog
   ↓
Metadata
   ↓
Snapshot
   ↓
Manifest List
   ↓
Manifest
   ↓
Data Files
```

and explain why every layer exists.

---

# 63. TEACHING PRINCIPLE

Follow this exact progression:

```text
Understand the problem
        ↓
Understand Iceberg
        ↓
Create a tiny table
        ↓
Inspect the metadata tree
        ↓
Understand snapshots
        ↓
Understand manifest lists
        ↓
Understand manifests
        ↓
Trace data files
        ↓
Query metadata tables
        ↓
Understand commits
        ↓
Learn hidden partitioning
        ↓
Learn partition evolution
        ↓
Learn schema IDs/evolution
        ↓
Learn statistics/pruning
        ↓
Learn delete files
        ↓
Learn COW vs MOR
        ↓
Understand format versions
        ↓
Learn sort orders
        ↓
Use PyIceberg
        ↓
Use DuckDB
        ↓
Use Polars
        ↓
Break the system
        ↓
Debug the metadata
        ↓
Design a production table
        ↓
Explain Iceberg from memory
```

Do not teach this as a list of APIs to memorize.

Teach the **internal architecture and reasoning model**.

---

# 64. START THE LESSON

Start by asking:

> **"If an Iceberg table contains thousands or millions of Parquet files, how can Iceberg know which files belong to the current table snapshot without listing every file in object storage?"**

Use this question to establish my current understanding.

Then teach me progressively from **basic → intermediate → advanced → hands-on → production architecture**.

Follow the authoritative Module 2.15 roadmap exactly.