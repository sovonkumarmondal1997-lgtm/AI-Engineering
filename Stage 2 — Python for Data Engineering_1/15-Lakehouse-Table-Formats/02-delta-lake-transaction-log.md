# CLAUDE CODE PROMPT — LEARN `02-delta-lake-transaction-log.md`

You are a **Senior Data Engineer with 10+ years of production experience** designing lakehouses, data platforms, distributed data pipelines, Spark systems, CDC architectures, object-storage data lakes, and transactional data systems.

I am learning:

```text
Python for Data Engineering/
└── 15-Lakehouse-Table-Formats/
    └── 02-delta-lake-transaction-log.md
```

Your job is to teach me the **complete contents and concepts of `02-delta-lake-transaction-log.md`**, from absolute beginner level through advanced production-level understanding.

This is a foundational topic in Module 2.15.

The goal is not merely to teach me how to use Delta Lake commands. The goal is to make me understand **how the Delta transaction log turns Parquet files in object storage into a transactional table**.

---

# 1. CRITICAL SCOPE RULE

Teach ONLY the subject covered by:

```text
02-delta-lake-transaction-log.md
```

Do NOT modify or rewrite any other curriculum file.

Do NOT change:

```text
01-why-open-table-formats-exist.md
03-apache-iceberg-snapshots-and-manifests.md
04-apache-hudi-overview.md
05-acid-merge-update-and-delete-on-data-lakes.md
06-time-travel-and-table-versioning.md
07-compaction-z-ordering-and-liquid-clustering.md
08-vacuum-retention-and-table-maintenance.md
09-catalogs-hive-metastore-glue-unity-and-polaris.md
practice-questions.md
```

Do not create a new curriculum.

Do not reorder Module 2.15.

Do not skip any concept from this topic.

You may use concepts from Topic 01 as prerequisites, but do not reteach Topic 01 in full.

---

# 2. AUTHORITATIVE TOPIC SCOPE

The roadmap requires this topic to cover the following.

## Basics

- Delta table layout
- Parquet data files
- `_delta_log/`
- Numbered JSON commit files
- Creating Delta tables
- Appending to Delta tables
- Overwriting Delta tables
- Spark-based Delta operations
- Python-based Delta operations using `deltalake` / delta-rs
- `DESCRIBE HISTORY`
- Reading the Delta transaction log with delta-rs

## Intermediate

- Delta commit actions:
  - `add`
  - `remove`
  - `metaData`
  - `protocol`
  - `commitInfo`
  - `txn`
- File statistics stored in `add`
- Reconstructing a table version
- Checkpoints
- Optimistic concurrency
- Writer version
- Commit process
- Conflict detection
- Retry/rejection behavior
- Schema enforcement
- Schema evolution
- `mergeSchema`
- Adding columns
- `CHECK` constraints
- `NOT NULL`
- Generated columns

## Advanced

- Protocol versions
- Delta table features
- Feature compatibility
- Deletion vectors
- Column mapping
- Change Data Feed
- Clustering
- Type widening
- `VARIANT`
- Atomic commits on object storage
- "put if absent"
- Coordination services
- Storage-specific commit considerations
- Idempotent writes
- Application transaction IDs
- Retry-safe pipelines
- Delta interoperability without Spark
- delta-rs
- DuckDB Delta extension
- Polars `scan_delta`

Do NOT skip any of these.

---

# 3. TEACHING OBJECTIVE

By the end, I should be able to look at:

```text
my_table/
├── part-00000-....parquet
├── part-00001-....parquet
├── part-00002-....parquet
└── _delta_log/
    ├── 00000000000000000000.json
    ├── 00000000000000000001.json
    ├── 00000000000000000002.json
    └── ...
```

and explain exactly:

1. What each component is.
2. Why `_delta_log` exists.
3. What happens when a write occurs.
4. What the JSON commit files represent.
5. How a reader determines the current table state.
6. How an old table version is reconstructed.
7. Why checkpoints exist.
8. How concurrent writers are handled.
9. How schema changes are recorded.
10. How table features affect compatibility.
11. How failed/retried writes can be made idempotent.
12. How other engines can read the table.

The ultimate mental model should be:

```text
Parquet files
      +
Delta transaction log
      ↓
Transactional table state
```

---

# 4. DO NOT START WITH ADVANCED DELTA FEATURES

Start from first principles.

Begin with:

> "What exactly is a Delta table?"

Then progressively build:

```text
Parquet
   ↓
Delta table directory
   ↓
_delta_log
   ↓
Commit
   ↓
Actions
   ↓
Table state
   ↓
Snapshots
   ↓
Checkpoints
   ↓
Concurrency
   ↓
Schema management
   ↓
Table features
   ↓
Idempotency
   ↓
Multi-engine access
```

Do not jump directly into deletion vectors or protocol versions.

---

# 5. FIRST BUILD THE CORE MENTAL MODEL

Explain:

```text
Delta Lake is not a replacement for Parquet.
```

Instead explain:

```text
Delta Lake
    =
Parquet data files
+
transaction log
+
metadata/protocol semantics
```

Make this distinction extremely clear.

Explain:

```text
Parquet
```

stores the actual data.

Whereas:

```text
_delta_log
```

records the transactional history and metadata required to determine the valid table state.

---

# 6. BUILD A SIMPLE DELTA TABLE

Create a small example table such as:

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

For example:

```python
customers = [
    (1, "Alice", "alice@example.com", "IN"),
    (2, "Bob", "bob@example.com", "US"),
    (3, "Charlie", "charlie@example.com", "UK"),
]
```

Use PySpark to create a Delta table.

Show:

```python
df.write.format("delta").mode("overwrite").save(path)
```

Then inspect the resulting directory.

Explain every generated file.

---

# 7. EXPLAIN THE DELTA DIRECTORY STRUCTURE

Show a realistic conceptual structure:

```text
customers/
├── part-00000-....snappy.parquet
├── part-00001-....snappy.parquet
├── _delta_log/
│   ├── 00000000000000000000.json
│   ├── 00000000000000000001.json
│   ├── 00000000000000000002.json
│   └── ...
```

Explain:

- data files
- transaction-log directory
- version numbers
- commit files
- relationship between data files and log files

Make this foundational.

---

# 8. EXPLAIN VERSION NUMBERS

Explain:

```text
00000000000000000000.json
00000000000000000001.json
00000000000000000002.json
```

as table commits/versions.

Build this model:

```text
Version 0
   ↓
Version 1
   ↓
Version 2
   ↓
Version 3
```

Explain that the table's logical state evolves through commits.

Make clear that the current table is not simply:

> "all Parquet files currently sitting in the directory."

Instead, the valid table state is determined by the transaction log.

This distinction is critical.

---

# 9. FIRST WRITE — INSPECT THE JSON LOG

After creating the table, open:

```text
_delta_log/00000000000000000000.json
```

Show the actual structure where practical.

Explain each action line.

For example, teach concepts such as:

```json
{
  "protocol": {...}
}
```

```json
{
  "metaData": {...}
}
```

```json
{
  "add": {...}
}
```

```json
{
  "commitInfo": {...}
}
```

Do not simply paste JSON.

For every action explain:

```text
What is it?
Why is it recorded?
Who uses it?
What does it change?
```

---

# 10. TEACH DELTA COMMIT ACTIONS ONE BY ONE

This is one of the most important parts.

Create a dedicated teaching section for each action.

---

## 10.1 `add`

Explain:

```text
add
```

records a data file that becomes part of the table.

Teach:

- path
- partition values
- size
- modification information
- dataChange
- statistics
- other relevant metadata

Explain why statistics matter.

Use an example such as:

```text
File A
customer_id: 1–1000
amount: 10–500

File B
customer_id: 1001–2000
amount: 500–5000
```

Explain how statistics can support data skipping.

---

## 10.2 `remove`

Explain that:

```text
remove
```

marks a previously active file as no longer part of the current table snapshot.

Explain the distinction between:

```text
logically removed
```

and:

```text
physically deleted
```

Very important:

Do NOT deeply teach VACUUM here.

Only establish the concept that removing a file from the active table state does not necessarily immediately delete its physical bytes.

---

## 10.3 `metaData`

Explain what table metadata represents.

Cover:

- schema
- partition columns
- table configuration
- table identity/metadata
- schema-related information

Explain why a table needs metadata beyond the Parquet files themselves.

---

## 10.4 `protocol`

Explain:

```text
protocol
```

as the mechanism that communicates what protocol capabilities/readers/writers are required.

Explain:

- reader requirements
- writer requirements
- compatibility
- why table features can change protocol requirements

Do not simply memorize field names.

Explain the compatibility problem:

```text
Writer enables feature X
        ↓
Old reader may not understand feature X
        ↓
Compatibility concern
```

---

## 10.5 `commitInfo`

Explain:

- operation
- operation parameters
- timestamp
- user/job information where available
- operation metrics
- transaction history context

Show how this supports:

- debugging
- auditing
- observability
- operational investigation

---

## 10.6 `txn`

This is extremely important.

Explain application transaction identifiers.

Teach the problem:

```text
Pipeline
   ↓
writes successfully
   ↓
network timeout
   ↓
pipeline retries
```

Without idempotency:

```text
same logical batch
       ↓
written twice
```

With application transaction IDs:

```text
transaction ID
       ↓
Delta can recognize the retry
       ↓
duplicate logical write can be prevented
```

Connect this to:

- Airflow retries
- streaming jobs
- CDC pipelines
- distributed systems
- exactly-once-style application design

Be precise about what Delta guarantees versus what the application still needs to guarantee.

---

# 11. EXPLAIN HOW DELTA RECONSTRUCTS TABLE STATE

This is the heart of the topic.

Suppose:

```text
Version 0:
add A
add B
```

Then:

```text
Version 1:
remove A
add C
```

Then:

```text
Version 2:
remove B
add D
```

Teach me to calculate:

```text
Version 0 active files:
A, B

Version 1 active files:
B, C

Version 2 active files:
C, D
```

Make me manually derive the state.

Then explain how Delta readers conceptually reconstruct the table from the transaction history.

Use diagrams.

---

# 12. BUILD A SMALL PYTHON DELTA LOG READER

The roadmap explicitly requires:

> Write a small log reader in Python that lists commits, operations, files added and removed per version, and the current file set.

Implement this.

Create:

```text
src/lakehouse_lab/delta_internals.py
```

The script should be able to:

```text
list_versions()
show_commit(version)
list_added_files(version)
list_removed_files(version)
current_active_files()
show_operation_summary()
```

Use Python JSON processing.

Do NOT hide the logic behind a high-level Delta library.

The goal is to understand the transaction log itself.

Explain the algorithm:

```text
Read commits
    ↓
Process actions
    ↓
Add active files
    ↓
Remove inactive files
    ↓
Produce current snapshot
```

---

# 13. EXPLAIN CHECKPOINTS

Once I understand JSON commits, introduce checkpoints.

Explain the problem with replaying:

```text
100,000 JSON commits
```

from the beginning.

Then introduce:

```text
Checkpoint
```

Conceptually:

```text
Version 0
Version 1
Version 2
...
Version 1000
        ↓
Checkpoint
        ↓
Version 1001
Version 1002
...
```

Instead of replaying everything:

```text
Checkpoint
+
Recent commits
```

can reconstruct the latest state more efficiently.

Explain:

- what a checkpoint is
- why it exists
- why checkpoints are generally Parquet-based
- how checkpoints accelerate snapshot reconstruction
- relationship between JSON transaction files and checkpoints

---

# 14. DRAW THE SNAPSHOT RECONSTRUCTION PROCESS

Make me understand:

```text
                    Delta Table
                        │
                        ▼
                 Transaction Log
                        │
              ┌─────────┴─────────┐
              │                   │
         Checkpoint          JSON commits
              │                   │
              └─────────┬─────────┘
                        ▼
                 Table Snapshot
                        │
                        ▼
                  Active Files
                        │
                        ▼
                  Parquet Data
```

Explain every step.

---

# 15. TEACH APPEND

Perform:

```python
df.write.format("delta").mode("append").save(path)
```

Then inspect the new commit.

Ask me to predict:

```text
How many new files?
Which JSON version?
Which actions?
Does the old data disappear?
```

Then execute.

Compare prediction versus reality.

---

# 16. TEACH OVERWRITE

Perform:

```python
df.write.format("delta").mode("overwrite").save(path)
```

Inspect the transaction log.

Explain:

```text
old files
   ↓
remove actions

new files
   ↓
add actions
```

Make the distinction between:

```text
physical file rewrite
```

and:

```text
transaction-log state transition
```

very clear.

---

# 17. TEACH SCHEMA ENFORCEMENT

Create an existing table:

```text
customer_id
name
email
```

Then attempt to write:

```text
customer_id
name
email
age
```

without schema evolution.

Show the failure.

Explain why rejecting incompatible writes is valuable.

Teach:

```text
Schema Enforcement
```

as a protection mechanism.

---

# 18. TEACH SCHEMA EVOLUTION

Then show an explicitly allowed schema evolution.

Use:

```python
.option("mergeSchema", "true")
```

where appropriate.

Show the resulting metadata change.

Explain:

```text
Schema Enforcement
vs
Schema Evolution
```

Do not confuse them.

Create a comparison table.

---

# 19. TEACH CHECK CONSTRAINTS

Create a constraint such as:

```sql
ALTER TABLE customers
ADD CONSTRAINT valid_customer_id
CHECK (customer_id > 0);
```

Then attempt:

```text
customer_id = -1
```

Show the failure.

Explain:

- why constraints matter
- where they fit in data quality
- why constraints are part of table semantics
- how this differs from external validation

---

# 20. TEACH NOT NULL

Demonstrate a NOT NULL constraint.

Explain:

```text
NULL
```

versus:

```text
missing value
```

and why table-level constraints protect downstream consumers.

Keep the implementation compatible with the actual Delta environment being used.

If a feature is version-dependent, explicitly say so.

---

# 21. TEACH GENERATED COLUMNS

Introduce generated columns.

Explain:

```text
Input columns
     ↓
Derived expression
     ↓
Generated column
```

Use a simple example.

Explain:

- why generated columns exist
- consistency
- derived values
- table-level semantics
- how generated columns interact with writes

Do not over-expand into unrelated feature areas.

---

# 22. TEACH OPTIMISTIC CONCURRENCY

This is a critical advanced concept.

Start with:

```text
Writer A reads Version 10
Writer B reads Version 10
```

Then:

```text
Writer A prepares changes
Writer B prepares changes
```

Suppose A commits first:

```text
Version 11
```

Now B attempts to commit.

Explain why B cannot blindly create another commit based on stale assumptions.

Teach the conceptual process:

```text
Read current version
       ↓
Prepare new data files
       ↓
Attempt commit
       ↓
Check whether conflicting changes occurred
       ↓
Commit / retry / reject
```

Do not reduce this to:

> "Delta uses locks."

Explain that the model is optimistic.

---

# 23. CONCURRENT WRITER EXPERIMENT

The roadmap requires concurrent writer testing.

Create two writers.

For example:

```text
Writer A → append/update
Writer B → append/update
```

Start them around the same time.

Observe:

- starting version
- commit order
- conflicts
- retries
- failures
- resulting table state

Repeat with:

```text
Different partitions
```

and:

```text
Same logical data / same partition
```

Explain why the conflict behavior differs.

Do not invent exact behavior if the installed Delta version behaves differently.

Record actual observations.

---

# 24. EXPLAIN ATOMIC COMMITS ON OBJECT STORAGE

This is an advanced conceptual section.

Explain why object storage is not a traditional database.

Discuss the challenge:

```text
How do we safely publish:

00000000000000000010.json
```

as the next transaction?

Explain the conceptual requirement:

```text
"Commit version N only if version N does not already exist."
```

Introduce:

```text
put-if-absent
```

and coordination mechanisms.

Explain why this matters.

Discuss that commit behavior depends on the storage/Delta configuration and version.

Do not make unsupported claims about every object store behaving identically.

---

# 25. EXPLAIN A COMMIT STEP BY STEP

Build this mental model:

```text
1. Read current table version
        ↓
2. Read relevant metadata
        ↓
3. Write new Parquet files
        ↓
4. Prepare transaction actions
        ↓
5. Attempt next log commit
        ↓
6. Validate concurrency assumptions
        ↓
7. Commit transaction
        ↓
8. New table version becomes visible
```

Explain what happens if the commit fails.

Explain why data files written during an unsuccessful attempt can become orphan candidates.

Do not teach complete orphan cleanup procedures yet; that belongs to Topic 08.

---

# 26. TEACH PROTOCOL VERSIONS

Introduce:

```text
reader protocol
writer protocol
```

Explain why a table format needs protocol compatibility.

Use:

```text
Engine A
```

that understands an older feature set and:

```text
Engine B
```

that understands a newer feature set.

Show how enabling a new table capability can change compatibility requirements.

---

# 27. TEACH DELTA TABLE FEATURES

Explain the concept of:

```text
Table Features
```

Then cover, at the roadmap level:

- deletion vectors
- column mapping
- Change Data Feed
- clustering
- type widening
- `VARIANT`

For each:

```text
What problem does it solve?
Why was it introduced?
What changes about the table?
What compatibility concern does it create?
```

Do not go deeply into the implementation of each feature because later topics cover some of these concepts.

---

# 28. DELETION VECTORS

Explain at a conceptual level.

Start with the traditional model:

```text
DELETE row
   ↓
rewrite Parquet file
```

Then:

```text
Deletion Vector
   ↓
record rows that should be considered deleted
```

Explain:

- why this can reduce rewrite cost
- impact on readers
- compatibility considerations
- why enabling a feature can change protocol requirements

Do not turn this into a full Topic 05/07 lesson.

---

# 29. COLUMN MAPPING

Explain why physical column names and logical column names may need to be separated.

Discuss:

- renaming columns
- preserving column identity
- schema evolution
- compatibility
- why column mapping exists

Keep implementation details appropriate to this topic.

---

# 30. CHANGE DATA FEED

Explain:

```text
Change Data Feed
```

at a conceptual and practical level.

Show the idea:

```text
Version 10
     ↓
Version 11
     ↓
What rows changed?
```

Explain:

- inserts
- updates
- deletes
- incremental downstream processing
- CDC consumers

Do not replace Topic 06's detailed time-travel/change-feed lesson.

---

# 31. CLUSTERING AS A TABLE FEATURE

Introduce clustering only at the required awareness level.

Explain that table features can influence:

```text
physical layout
```

and:

```text
query performance
```

Mention clustering as a Delta capability but do not deeply teach Z-ordering/liquid clustering here because that is Topic 07.

---

# 32. TYPE WIDENING

Explain why a schema might evolve:

```text
INT
  ↓
BIGINT
```

and why some type changes are safer than others.

Explain:

```text
compatible evolution
vs
breaking evolution
```

Then explain why Delta can encode feature/protocol requirements around supported type evolution.

---

# 33. VARIANT

Explain `VARIANT` at a conceptual level.

Use a simple semi-structured example:

```json
{
  "device": "mobile",
  "campaign": "summer",
  "attributes": {
      "browser": "Chrome"
  }
}
```

Explain why a table format may need to understand newer data types and why engine support must be checked.

Do not turn this into a semi-structured-data course.

---

# 34. IDEMPOTENT WRITES

This is one of the most important production concepts.

Start with:

```text
Job runs
   ↓
writes successfully
   ↓
network failure before acknowledgement
   ↓
job retries
```

Explain the duplicate-write problem.

Then introduce:

```text
Application transaction ID
```

Build an example:

```text
batch_id = "orders-2026-10-05"
```

The retry should use the same logical transaction identifier.

Explain:

```text
Same logical batch
        +
Same application transaction ID
        ↓
Retry can be recognized
```

Connect this to:

- Airflow
- Kafka
- CDC
- batch pipelines
- distributed processing

Be extremely precise about the difference between:

```text
idempotent application design
```

and:

```text
exactly-once end-to-end guarantees
```

Do not claim that Delta alone magically makes an entire distributed pipeline exactly-once.

---

# 35. BUILD AN IDEMPOTENCY EXPERIMENT

Create a small example:

```text
batch-001
batch-002
batch-003
```

Write each batch.

Then retry:

```text
batch-002
```

Show how the transaction identifier can prevent duplicate logical application.

Inspect the log.

Explain exactly what changed.

---

# 36. NON-SPARK DELTA ACCESS

The roadmap requires understanding Delta without Spark.

Teach:

```text
delta-rs / deltalake
DuckDB delta extension
Polars scan_delta
```

Explain why this matters.

The architecture should be:

```text
                    Delta Table
                        │
          ┌─────────────┼──────────────┐
          ▼             ▼              ▼
       Spark         DuckDB         Polars
          │             │              │
          └─────────────┼──────────────┘
                        ▼
                    Parquet +
                   Delta Log
```

Explain that multiple engines can consume the same open table.

---

# 37. DELTA-RS / `DELTALAKE`

Show how to:

- open a Delta table
- inspect history
- inspect metadata
- read table data
- inspect versions where supported
- perform supported writes where appropriate

Use:

```python
from deltalake import DeltaTable
```

where appropriate.

Explain what the library is doing conceptually.

Do not hide the transaction-log mechanics.

---

# 38. DUCKDB

Show a small example of reading a Delta table using DuckDB's Delta extension.

Explain:

```text
DuckDB
   ↓
Delta reader
   ↓
Delta transaction log
   ↓
active Parquet files
```

Explain interoperability.

---

# 39. POLARS

Show:

```python
pl.scan_delta(...)
```

or the currently supported equivalent for the installed version.

Explain:

- lazy execution
- reading Delta
- why engine compatibility matters

If syntax differs by installed version, check the installed version and use the correct syntax.

---

# 40. VERSION COMPATIBILITY RULE

The roadmap explicitly warns that table formats evolve quickly.

Therefore:

Before teaching or executing version-sensitive features:

1. Check installed versions.
2. Identify compatibility requirements.
3. Explain if a feature is unavailable.
4. Use the supported alternative.
5. Never pretend a feature exists if the installed environment does not support it.

Pay particular attention to:

- Spark version
- Delta Spark package
- `deltalake`
- DuckDB
- Polars
- Delta table features

---

# 41. REQUIRED HANDS-ON PROJECT

Create/use:

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
│       └── delta_internals.py
├── notebooks_or_scripts/
└── tests/
```

Do not unnecessarily modify unrelated existing curriculum files.

The focus is the Delta transaction-log experiment.

---

# 42. REQUIRED EXPERIMENT SEQUENCE

Perform experiments in this order:

```text
Experiment 1
Create Delta table
        ↓
Experiment 2
Inspect _delta_log
        ↓
Experiment 3
Append
        ↓
Experiment 4
Overwrite
        ↓
Experiment 5
Inspect add/remove actions
        ↓
Experiment 6
Build Python log reader
        ↓
Experiment 7
Checkpoint inspection
        ↓
Experiment 8
Schema enforcement
        ↓
Experiment 9
Schema evolution
        ↓
Experiment 10
Constraints
        ↓
Experiment 11
Concurrent writers
        ↓
Experiment 12
Idempotent writes
        ↓
Experiment 13
Non-Spark readers
        ↓
Experiment 14
Enable/test selected table feature
```

For every experiment require:

```text
Predict
→ Execute
→ Inspect
→ Explain
→ Compare
→ Document
```

---

# 43. FILE INSPECTION IS MANDATORY

Do not teach Delta as a black box.

After important operations inspect:

```text
_delta_log/
```

and identify:

```text
version
action
file added
file removed
schema
protocol
operation
transaction ID
statistics
```

Make me read the JSON myself.

The objective is:

> I should be able to understand what Delta is doing internally by inspecting its transaction log.

---

# 44. WRITE A TABLE-STATE RECONSTRUCTOR

Create a simplified Python implementation that demonstrates:

```text
commit files
     ↓
parse actions
     ↓
maintain active-file set
     ↓
produce snapshot
```

For example:

```python
active_files = set()

for commit in commits:
    for action in commit:
        if "add" in action:
            active_files.add(action["add"]["path"])

        if "remove" in action:
            active_files.discard(action["remove"]["path"])
```

Do not present this as production Delta implementation.

Explicitly explain:

> This is a teaching model that demonstrates the core state-reconstruction idea, not a complete Delta implementation.

Then compare the simplified model with actual Delta behavior.

---

# 45. DEBUGGING EXERCISES

Intentionally create situations such as:

### Problem 1

A table contains unexpected files.

Ask:

> Are they necessarily active table files?

Make me inspect `_delta_log`.

### Problem 2

A schema mismatch occurs.

Ask:

> Is this a Parquet problem or Delta schema enforcement?

### Problem 3

Two writers conflict.

Ask:

> What version did each writer read?

### Problem 4

A pipeline retries.

Ask:

> How can application transaction IDs make the operation retry-safe?

### Problem 5

A new feature is enabled.

Ask:

> Which readers can still access the table?

These should be reasoning exercises.

---

# 46. PRODUCTION SCENARIOS

Use realistic scenarios.

## Scenario A — Airflow Batch Pipeline

```text
Airflow
   ↓
Python
   ↓
Spark
   ↓
Delta
```

Explain retries and idempotency.

## Scenario B — CDC Pipeline

```text
PostgreSQL
   ↓
CDC
   ↓
Spark
   ↓
Delta
```

Explain transaction boundaries.

## Scenario C — Multiple Query Engines

```text
Spark
DuckDB
Polars
```

reading the same Delta table.

Explain compatibility.

## Scenario D — Concurrent Writers

```text
Pipeline A
Pipeline B
    ↓
Same Delta table
```

Explain optimistic concurrency.

---

# 47. COMMON MISCONCEPTIONS

Explicitly test and correct:

```text
"Delta replaces Parquet."
```

```text
"_delta_log contains the actual table data."
```

```text
"Every JSON commit contains the entire table."
```

```text
"remove means the physical Parquet file is immediately deleted."
```

```text
"Checkpoint = backup."
```

```text
"Optimistic concurrency means there can never be conflicts."
```

```text
"Schema evolution means every schema change is automatically safe."
```

```text
"Delta automatically gives exactly-once semantics to every pipeline."
```

```text
"If Spark can read a Delta feature, every other engine can read it."
```

```text
"Enabling a table feature has no compatibility consequences."
```

For each misconception, explain the correct mental model.

---

# 48. DELTA INTERNALS DIAGRAM

Build and repeatedly use a diagram like:

```text
                 DELTA TABLE
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
   Parquet Files              _delta_log
        │                         │
        │                 ┌───────┼────────┐
        │                 ▼       ▼        ▼
        │              JSON   Checkpoints Metadata
        │              commits
        │                 │
        └────────┬────────┘
                 ▼
           Table Snapshot
                 │
                 ▼
          Active File Set
                 │
                 ▼
              Reader
```

Explain this diagram until I can reproduce it from memory.

---

# 49. ADVANCED ARCHITECTURAL QUESTION

Ask me:

> If Delta did not have `_delta_log`, could Parquet files alone safely provide atomic multi-file transactions?

Make me reason about:

- object storage
- multi-file writes
- readers
- versioning
- concurrent writers
- metadata

Do not answer immediately.

---

# 50. SECOND ADVANCED QUESTION

Ask:

> Why does Delta write Parquet data files first and then commit metadata rather than modifying the existing Parquet files in place?

Guide me toward understanding:

```text
immutable/new files
        +
transactional metadata commit
        ↓
safe snapshot transition
```

Do not simply provide the answer.

---

# 51. THIRD ADVANCED QUESTION

Ask:

> If a writer creates new Parquet files but fails before committing the Delta transaction log, are those files automatically part of the table?

Make me inspect and reason from the transaction log.

---

# 52. FOURTH ADVANCED QUESTION

Ask:

> Why can a table contain physical files that are not currently part of the active logical table state?

Connect this to:

```text
remove actions
failed writes
historical versions
maintenance
```

Do not go deeply into Topic 08.

---

# 53. LEARNING CHECKPOINTS

After each major section, stop.

Ask 3–5 questions.

For example:

```text
What is the relationship between Parquet and Delta?

What is the purpose of _delta_log?

What does an add action represent?

What does a remove action represent?

How is table state reconstructed?

Why do checkpoints exist?

What is optimistic concurrency?

Why can concurrent writers conflict?

What is schema enforcement?

What is schema evolution?

Why does protocol compatibility matter?

What is an application transaction ID?
```

If I fail:

1. Identify the misconception.
2. Explain again simply.
3. Give a concrete example.
4. Ask a similar question.
5. Continue only after I demonstrate understanding.

---

# 54. FINAL ASSESSMENT

After teaching the complete topic, conduct:

## Basic — 10 questions

Focus on:

- Delta table structure
- `_delta_log`
- Parquet
- versions
- commits
- actions

## Intermediate — 10 questions

Focus on:

- snapshot reconstruction
- checkpoints
- schema enforcement
- schema evolution
- constraints
- concurrency

## Advanced — 10 questions

Focus on:

- protocol versions
- table features
- atomic commits
- idempotency
- transaction IDs
- interoperability

## Production Scenarios — 5 questions

Each should present a realistic failure or architecture problem.

Do NOT give me the answers immediately.

Wait for my answers and grade them.

---

# 55. FINAL PRACTICAL CHALLENGE

Give me this architecture problem:

> A company receives 500 million customer CDC records every day. The pipeline runs through Spark and writes to Delta on object storage. Airflow retries failed jobs. Two pipelines may occasionally target the same table. Analysts use Spark, DuckDB, and Polars. The company also wants schema evolution and reproducible historical datasets.

Ask me to design the Delta architecture.

I must explain:

```text
Storage
↓
Parquet
↓
Delta transaction log
↓
Commit versions
↓
Actions
↓
Snapshots
↓
Checkpoints
↓
Concurrency
↓
Schema enforcement/evolution
↓
Idempotency
↓
Protocol compatibility
↓
Multi-engine reads
```

Do not solve it immediately.

First evaluate my architecture.

---

# 56. FINAL EXIT CRITERIA

Do not consider this topic complete until I can explain without notes:

- [ ] What a Delta table is
- [ ] Why Delta still uses Parquet
- [ ] What `_delta_log` is
- [ ] How commit versions work
- [ ] What an `add` action means
- [ ] What a `remove` action means
- [ ] What `metaData` represents
- [ ] What `protocol` represents
- [ ] What `commitInfo` represents
- [ ] What `txn` represents
- [ ] How Delta reconstructs table state
- [ ] Why checkpoints exist
- [ ] How append changes the transaction log
- [ ] How overwrite changes the transaction log
- [ ] Schema enforcement
- [ ] Schema evolution
- [ ] `mergeSchema`
- [ ] `CHECK` constraints
- [ ] `NOT NULL`
- [ ] Generated columns
- [ ] Optimistic concurrency
- [ ] Conflict detection
- [ ] Atomic object-storage commits
- [ ] Put-if-absent concept
- [ ] Protocol versions
- [ ] Delta table features
- [ ] Deletion vectors at a conceptual level
- [ ] Column mapping
- [ ] Change Data Feed
- [ ] Clustering as a table capability
- [ ] Type widening
- [ ] `VARIANT` awareness
- [ ] Application transaction IDs
- [ ] Idempotent writes
- [ ] Why idempotency is different from end-to-end exactly-once
- [ ] delta-rs / `deltalake`
- [ ] DuckDB Delta support
- [ ] Polars Delta support
- [ ] Engine/feature compatibility

Most importantly, I should be able to answer:

> **"If Parquet stores the data, what exactly does the Delta transaction log contribute that makes the collection of Parquet files behave like a transactional table?"**

I should be able to explain this using:

```text
files
+
actions
+
versions
+
snapshots
+
atomic commits
+
concurrency control
+
metadata
```

rather than memorizing a definition.

---

# 57. TEACHING PRINCIPLE

Follow this exact progression:

```text
Understand the problem
        ↓
Build a tiny Delta table
        ↓
Inspect the directory
        ↓
Inspect _delta_log
        ↓
Understand actions
        ↓
Understand versions
        ↓
Reconstruct table state manually
        ↓
Understand checkpoints
        ↓
Understand schema management
        ↓
Understand concurrency
        ↓
Understand protocol/features
        ↓
Understand idempotency
        ↓
Read Delta without Spark
        ↓
Break the system
        ↓
Debug it
        ↓
Design it
        ↓
Explain it from memory
```

Do not skip directly to API usage.

The goal is to understand **the internal system design**.

---

# 58. START THE LESSON

Start with this question:

> **"If Parquet already stores the data, why does Delta Lake need a `_delta_log` at all?"**

Do not immediately give me the complete answer.

Use the question to establish my current understanding, then teach the topic progressively from basic to advanced.

Follow the Module 2.15 roadmap exactly.