# CLAUDE CODE PROMPT — LEARN `04-apache-hudi-overview.md`

## ROLE

Act as a **Senior Data Engineer with 10+ years of production experience** designing and operating large-scale data platforms, lakehouses, CDC pipelines, distributed data systems, Apache Spark, Delta Lake, Apache Iceberg, and Apache Hudi.

You are my instructor.

Your job is to teach me the complete topic covered by:

```text
15-Lakehouse-Table-Formats/
└── 04-apache-hudi-overview.md
```

Teach this topic **from absolute fundamentals to advanced production-level understanding**, using simple language first and progressively introducing technical terminology.

The goal is not merely to memorize Apache Hudi APIs.

The goal is for me to understand:

- why Hudi exists
- what problem it solves
- how Hudi works internally
- how Hudi manages table state and changes
- how Hudi handles inserts, updates, and deletes
- how Hudi supports incremental processing and CDC-style workloads
- how Hudi's storage/metadata model works
- how Hudi compares conceptually with plain Parquet, Delta Lake, and Iceberg
- when Hudi is an appropriate choice in production
- what trade-offs Hudi introduces
- how to reason about Hudi architecture and operational behavior

---

# 1. STRICT FILE-SCOPE RULE

You are teaching **ONLY**:

```text
04-apache-hudi-overview.md
```

Do NOT modify, rewrite, create, rename, delete, or update any other file in:

```text
15-Lakehouse-Table-Formats/
```

In particular, do NOT modify:

```text
README.md
01-why-open-table-formats-exist.md
02-delta-lake-transaction-log.md
03-apache-iceberg-snapshots-and-manifests.md
05-acid-merge-update-and-delete-on-data-lakes.md
06-time-travel-and-table-versioning.md
07-compaction-z-ordering-and-liquid-clustering.md
08-vacuum-retention-and-table-maintenance.md
09-catalogs-hive-metastore-glue-unity-and-polaris.md
practice-questions.md
```

You may **read prerequisite files for context if necessary**, but do not modify them.

All teaching, examples, experiments, notes, and explanations must remain scoped to:

```text
04-apache-hudi-overview.md
```

---

# 2. AUTHORITATIVE ROADMAP RULE

Treat the existing Module 2.15 roadmap as the authoritative curriculum.

Do NOT silently expand this lesson into unrelated Apache Hudi topics merely because you know additional Hudi features.

If a concept is not supported by the roadmap scope for this file, do not turn it into a major lesson.

If additional context is useful for understanding a roadmap concept, you may briefly explain it, but clearly distinguish:

- required curriculum
- supporting background
- optional advanced context

Do not replace the roadmap's terminology or learning sequence with a different curriculum.

---

# 3. TEACHING PHILOSOPHY

Teach using this progression:

```text
Problem
  ↓
Why the problem exists
  ↓
Plain Parquet approach
  ↓
Why plain Parquet becomes difficult
  ↓
Why a table format is needed
  ↓
Why Hudi was designed
  ↓
Hudi mental model
  ↓
Hudi architecture
  ↓
Hudi table/storage concepts
  ↓
Record-level changes
  ↓
Incremental processing
  ↓
Concurrency and consistency
  ↓
Operational behavior
  ↓
Comparison with Delta Lake and Iceberg
  ↓
Production trade-offs
  ↓
Hands-on implementation
  ↓
Debugging
  ↓
Architecture decisions
```

Never begin with complicated APIs.

First explain the underlying problem.

---

# 4. START WITH THE BIG PICTURE

Begin the lesson with a simple explanation:

> "What is Apache Hudi?"

Explain it as if I have never used Hudi before.

Then answer:

1. What is a data lake?
2. What is Parquet?
3. What happens when data is mostly append-only?
4. What becomes difficult when records need to change?
5. Why are UPDATE and DELETE operations difficult on ordinary Parquet files?
6. Why do CDC workloads create additional challenges?
7. Why does repeatedly rewriting large Parquet files become expensive?
8. What does a transactional/open table format provide?
9. Where does Apache Hudi fit into this architecture?

Use a concrete example such as:

```text
customers/
    part-000.parquet
    part-001.parquet
    part-002.parquet
```

Suppose:

```text
customer_id = 101
email = old@example.com
```

changes to:

```text
customer_id = 101
email = new@example.com
```

Explain what happens with plain Parquet.

Then explain how a table format such as Hudi changes the design.

---

# 5. WHY APACHE HUDI EXISTS

Build the motivation from first principles.

Explain the engineering problems Hudi is intended to address.

Cover:

- mutable datasets on data lakes
- updates
- deletes
- inserts
- upserts
- CDC workloads
- incremental data processing
- avoiding unnecessary full-table rewrites
- maintaining table state
- tracking changes over time
- managing large numbers of data files
- supporting data-lake workloads that behave more like database tables

Explain the difference between:

```text
Append-only data
```

and:

```text
Mutable data
```

Use practical examples:

### Append-only

```text
events
logs
clickstream
telemetry
```

### Mutable

```text
customers
orders
inventory
subscriptions
accounts
```

Explain why the second category creates a fundamentally different storage problem.

---

# 6. HUDI'S CORE MENTAL MODEL

Develop a strong mental model before discussing implementation.

Explain:

```text
Hudi Table
    ↓
Records
    ↓
Record Key
    ↓
Partition
    ↓
Data Files
    ↓
Table Metadata / Timeline
    ↓
Commits and Changes
```

Explain each concept carefully.

For every concept answer:

1. What is it?
2. Why does it exist?
3. What problem does it solve?
4. How does it relate to the other concepts?
5. What happens when data changes?

Do not assume I already understand Hudi terminology.

---

# 7. HUDI TABLE CONCEPT

Explain what makes a Hudi table different from:

```text
directory of Parquet files
```

Explain the conceptual transformation:

```text
Parquet files
      ↓
metadata + transactional table semantics
      ↓
Hudi table
```

Explain the responsibilities of the table layer.

Show a simplified conceptual filesystem layout.

For example, demonstrate the idea of:

```text
table/
├── partition_a/
│   ├── ...
├── partition_b/
│   ├── ...
└── .hoodie/
    ├── ...
```

Do NOT pretend that a simplified example is the complete physical layout.

Clearly distinguish:

```text
Conceptual layout
```

from:

```text
Actual Hudi implementation details
```

When showing real filesystem examples, explain which parts are illustrative and which are actual Hudi concepts.

---

# 8. THE `.HOODIE` DIRECTORY

Explain the importance of:

```text
.hoodie/
```

Build the explanation gradually.

Explain that Hudi maintains metadata and timeline information associated with table state and operations.

Teach:

- why metadata is required
- what the timeline represents
- why data files alone are insufficient
- how table state can be reasoned about from metadata
- how operations become observable through the timeline

Explain the relationship:

```text
Data files
+
Hudi metadata/timeline
=
Hudi table state
```

Do not merely say "`.hoodie` contains metadata."

Explain **why that metadata exists**.

---

# 9. HUDI TIMELINE

Teach the Hudi timeline concept carefully.

Explain:

```text
timeline
```

as a chronological record of table actions/state transitions.

Explain concepts such as:

- commits
- write operations
- table state transitions
- completed operations
- pending/in-flight operations at a conceptual level
- how the timeline helps determine table state

Use a simple example:

```text
T1 → initial write
T2 → insert
T3 → update
T4 → delete
```

Explain how the table evolves.

Build a timeline diagram such as:

```text
Initial State
     |
     v
Commit 001
     |
     v
Commit 002
     |
     v
Commit 003
     |
     v
Current Table State
```

Explain why this is important for:

- recovery
- incremental processing
- debugging
- understanding table history
- determining what changed

---

# 10. RECORD KEYS

Teach Hudi record keys from first principles.

Explain:

> What uniquely identifies a record?

Use:

```text
customer_id
order_id
product_id
```

Explain why a record key is fundamental for mutable data.

Demonstrate:

```text
customer_id = 101
```

Initial record:

```json
{
  "customer_id": 101,
  "name": "Alice",
  "city": "Delhi"
}
```

Updated record:

```json
{
  "customer_id": 101,
  "name": "Alice",
  "city": "Mumbai"
}
```

Explain how the system knows that these are two versions of the same logical record.

Discuss the relationship between:

```text
record key
partition
physical storage
logical record identity
```

---

# 11. PARTITIONING

Explain Hudi partitioning from a data-engineering perspective.

Use examples such as:

```text
event_date
country
region
```

Explain:

- why partitioning exists
- how partitioning affects data organization
- partition pruning
- partition size
- operational implications
- choosing a partition column
- high-cardinality partitioning problems

Use a concrete example:

```text
orders/
    order_date=2026-10-01/
    order_date=2026-10-02/
    order_date=2026-10-03/
```

Then explain what happens when a query filters:

```sql
WHERE order_date = '2026-10-03'
```

---

# 12. UPSERT

This is one of the most important concepts.

Teach:

```text
INSERT
UPDATE
UPSERT
```

carefully.

Explain:

```text
INSERT
```

as:

> Add a new record.

Explain:

```text
UPDATE
```

as:

> Modify an existing logical record.

Explain:

```text
UPSERT
```

as:

> Insert if the record does not exist; update if it does.

Use a simple table:

| customer_id | name | city |
|---|---|---|
| 1 | Alice | Delhi |
| 2 | Bob | Mumbai |

Incoming data:

| customer_id | name | city |
|---|---|---|
| 2 | Bob | Pune |
| 3 | Charlie | Kolkata |

Show the resulting state.

Then demonstrate the same operation conceptually in Hudi.

---

# 13. DELETE OPERATIONS

Explain why DELETE is difficult on ordinary immutable Parquet files.

Use:

```text
Before:

customer_id = 101
customer_id = 102
customer_id = 103
```

Delete:

```text
customer_id = 102
```

Explain why simply deleting one row from a Parquet file is not equivalent to deleting a database row.

Then explain how table formats such as Hudi provide mechanisms for representing record-level changes.

Keep this lesson focused on the Hudi overview rather than duplicating the detailed ACID/DELETE curriculum of:

```text
05-acid-merge-update-and-delete-on-data-lakes.md
```

---

# 14. HUDI WRITE TYPES

Introduce Hudi's major write concepts at an appropriate conceptual level.

Explain:

- Copy-on-Write
- Merge-on-Read

Teach the distinction very carefully.

### Copy-on-Write

Explain:

```text
Incoming update
      ↓
rewrite affected data
      ↓
new base files
```

### Merge-on-Read

Explain:

```text
Base data
+
incremental/log changes
      ↓
merge during read/compaction
```

Create a comparison table:

| Concept | Copy-on-Write | Merge-on-Read |
|---|---|---|
| Write behavior | ... | ... |
| Read behavior | ... | ... |
| Update handling | ... | ... |
| Write latency | ... | ... |
| Read complexity | ... | ... |
| Compaction considerations | ... | ... |
| Typical workload | ... | ... |

Do not oversimplify.

Explain the engineering trade-off.

---

# 15. INCREMENTAL PROCESSING

Treat incremental processing as a major Hudi capability.

Explain the problem:

Suppose a table contains:

```text
10 TB
```

and only:

```text
5 GB
```

changed since the last pipeline execution.

Explain why repeatedly processing all 10 TB is inefficient.

Then introduce the concept of consuming only changes since a previous table state.

Explain:

```text
Previous state
      ↓
New Hudi commits
      ↓
Changed records/files
      ↓
Downstream processing
```

Explain how this supports:

- downstream incremental pipelines
- CDC-like workloads
- event-driven processing
- efficient synchronization
- materialized views
- search/index updates
- downstream warehouses

Provide a Python/Spark example where appropriate.

---

# 16. HUDI AND CDC

Connect Hudi to Change Data Capture.

Use a realistic scenario:

```text
PostgreSQL
     |
     | CDC
     v
Kafka
     |
     v
Hudi
     |
     +----> Analytics
     |
     +----> ML
     |
     +----> Downstream systems
```

Explain:

```text
INSERT
UPDATE
DELETE
```

events.

Show how CDC events can be represented conceptually:

```json
{
  "op": "UPDATE",
  "customer_id": 101,
  "city": "Mumbai"
}
```

Then explain how Hudi can serve as a durable lakehouse table for mutable data.

Clearly distinguish:

```text
CDC source
```

from:

```text
table format
```

Hudi is not itself the source database or Kafka.

---

# 17. HUDI TIMELINE + INCREMENTAL CONSUMPTION

Connect the concepts.

Explain:

```text
Write operation
      ↓
Hudi timeline
      ↓
Table state transition
      ↓
Incremental reader
      ↓
Only relevant changes processed
```

Use a concrete example:

```text
Commit 001 → 1 million records
Commit 002 → 10,000 updates
Commit 003 → 5,000 inserts
Commit 004 → 2,000 deletes
```

Explain how a downstream job can reason about:

```text
"Give me changes since Commit 001."
```

---

# 18. HUDI METADATA AND DATA FILES

Explain the difference between:

```text
Data
```

and:

```text
Metadata about the data
```

Teach why large-scale lakehouse systems need metadata to avoid blindly scanning the entire object store.

Discuss:

- file-level organization
- table state
- commits
- partitions
- record identity
- file locations
- operational history

Do not make unsupported claims about implementation details.

Where exact Hudi internals vary by version, explicitly state that.

---

# 19. SIMPLE HUDI HANDS-ON LAB

Build a minimal working Hudi example.

Prefer:

```text
Python
+
PySpark
+
Apache Hudi
```

where practical.

First verify the installed versions.

Before executing Hudi operations, explain:

```text
Spark version
Hudi version
Java version
Python version
```

and compatibility requirements.

Do not blindly assume every Hudi version works with every Spark version.

---

# 20. FIRST HUDI TABLE

Create a minimal dataset:

```text
customer_id
name
city
updated_at
```

Example:

```python
data = [
    (1, "Alice", "Delhi", "2026-10-01"),
    (2, "Bob", "Mumbai", "2026-10-01"),
]
```

Create a Spark DataFrame.

Then write it as a Hudi table.

Explain every configuration option.

Do not provide unexplained configuration dictionaries.

For every important option explain:

```text
What does it mean?
Why is it required?
What happens if it changes?
```

---

# 21. INSERT DATA

Demonstrate inserting records.

Show:

```text
Source data
    ↓
Spark DataFrame
    ↓
Hudi write
    ↓
Hudi table
```

Then inspect the table.

Explain what changed physically and logically.

---

# 22. UPSERT DATA

Create a second batch:

```python
data = [
    (2, "Bob", "Pune", "2026-10-02"),
    (3, "Charlie", "Kolkata", "2026-10-02"),
]
```

Demonstrate the upsert.

Explain:

```text
customer_id = 2
```

is updated rather than duplicated.

Explain:

```text
customer_id = 3
```

is inserted.

Then read the table and verify the result.

---

# 23. DELETE DATA

Demonstrate a delete operation conceptually and, where supported by the selected Hudi version, practically.

Show:

```text
Before:
1
2
3

Delete:
2

After:
1
3
```

Explain the logical operation and the underlying storage implications.

---

# 24. INSPECT THE HUDI TABLE

After every major operation, inspect the filesystem.

Show:

```text
table/
├── data files
└── .hoodie/
```

Explain what changed.

Do NOT simply run:

```bash
ls
```

and move on.

Teach me how to reason about what the changes mean.

---

# 25. PREDICT → EXECUTE → INSPECT

For every important experiment use this learning loop:

### Step 1 — Predict

Ask me:

> What do you expect to happen?

### Step 2 — Execute

Run the operation.

### Step 3 — Inspect

Inspect:

- table data
- filesystem
- metadata/timeline where practical

### Step 4 — Explain

Explain why the result occurred.

### Step 5 — Break It

Where safe, intentionally create an invalid or conflicting scenario.

### Step 6 — Recover

Explain how production systems should recover.

This is mandatory throughout the lesson.

---

# 26. COPY-ON-WRITE VS MERGE-ON-READ LAB

Build a controlled comparison.

Use the same logical dataset.

Compare:

```text
COW
```

against:

```text
MOR
```

Measure where practical:

- write time
- read time
- files created
- storage footprint
- update behavior

Do not fabricate benchmark numbers.

If performance is measured, report actual measurements from the environment.

Explain why the numbers may differ across machines.

---

# 27. HUDI VS PLAIN PARQUET

Create a conceptual comparison:

| Capability | Plain Parquet | Hudi |
|---|---|---|
| Append | Yes | Yes |
| Record-level update | Difficult | Supported |
| Record-level delete | Difficult | Supported |
| Upsert | Difficult | Supported |
| Transactional table state | No | Yes |
| Incremental processing | Limited/manual | Core capability |
| Metadata/timeline | No transactional timeline | Yes |
| Mutable datasets | Awkward | Strong use case |

Explain each row rather than simply displaying the table.

---

# 28. HUDI VS DELTA LAKE VS ICEBERG

Provide a **high-level conceptual comparison only** because the detailed Delta and Iceberg internals are covered by the neighboring files.

Compare:

```text
Apache Hudi
Apache Delta Lake
Apache Iceberg
```

Use dimensions such as:

- primary design goals
- metadata/transaction model
- mutable data
- upserts
- deletes
- incremental processing
- CDC-oriented workloads
- schema evolution
- time travel
- engine interoperability
- operational complexity
- ecosystem considerations

Do NOT declare a universal winner.

Teach:

> The correct table format depends on workload, engine ecosystem, operational model, and organizational requirements.

---

# 29. WHEN HUDI IS A STRONG FIT

Give practical production scenarios.

Examples:

### Scenario 1 — CDC lakehouse

```text
OLTP database
      ↓
CDC
      ↓
Kafka
      ↓
Hudi
      ↓
Analytics / ML
```

### Scenario 2 — Frequently updated customer dimension

```text
Customer data
      ↓
continuous updates
      ↓
Hudi table
```

### Scenario 3 — Incremental downstream pipelines

```text
Hudi
  ↓
only changed records
  ↓
downstream systems
```

For each scenario explain:

- why Hudi fits
- what alternative could also work
- what trade-offs must be evaluated

---

# 30. WHEN HUDI MAY NOT BE THE BEST CHOICE

Teach decision-making rather than advocacy.

Discuss cases where:

- data is purely append-only
- there are very few updates/deletes
- the existing organization is standardized on another table format
- engine compatibility is more important than Hudi-specific capabilities
- operational expertise is stronger with another ecosystem
- workload characteristics do not justify Hudi's additional machinery

The goal is to understand:

```text
Use Hudi because the workload requires it,
not because it is a fashionable technology.
```

---

# 31. PRODUCTION DESIGN CONSIDERATIONS

Teach practical considerations including:

- record-key design
- partition-key design
- file sizing
- update frequency
- write amplification
- read amplification
- compaction implications
- incremental processing
- metadata management
- schema evolution
- concurrency
- failure recovery
- observability
- version compatibility
- Spark/Hudi compatibility
- object-storage behavior

For each item explain:

```text
Risk
→ Why it happens
→ How to detect it
→ How to mitigate it
```

---

# 32. FAILURE SCENARIOS

Create realistic failure scenarios.

### Failure 1 — Duplicate records

Explain possible causes involving:

```text
record key
```

and incorrect write configuration.

### Failure 2 — Updates become duplicates

Explain how incorrect record identity can cause this.

### Failure 3 — Extremely slow writes

Investigate:

- partitioning
- file layout
- update volume
- write mode
- storage behavior

### Failure 4 — Slow reads

Investigate:

- file count
- file sizes
- table organization
- query patterns

### Failure 5 — Incremental pipeline misses changes

Investigate:

- timeline assumptions
- commit boundaries
- reader configuration
- source/consumer state

Do not provide superficial answers.

Teach the debugging process.

---

# 33. VERSION COMPATIBILITY

This is mandatory.

Before running examples, determine the versions available in the environment.

Check:

```text
Python
Java
Spark
Hudi
```

Explain that Hudi APIs, configuration properties, supported features, and integration behavior can vary by release.

If an example is version-dependent:

1. identify the version dependency
2. explain it
3. adapt the example
4. clearly state the assumption

Never present version-sensitive syntax as universally valid.

---

# 34. CODING STYLE

All code must be:

- executable
- readable
- production-oriented
- heavily explained
- incremental
- easy for a beginner to follow

Prefer complete examples such as:

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("HudiLearning")
    .getOrCreate()
)
```

Then explain each line.

Avoid unexplained magic.

Bad teaching:

```python
options = {...}
df.write.format("hudi").options(**options).save(path)
```

Good teaching:

```text
First explain each option.
Then show the complete configuration.
Then execute it.
Then inspect the result.
```

---

# 35. USE SMALL DATASETS FIRST

Do not start with millions of rows.

Begin with:

```text
5–10 records
```

Then progress to:

```text
hundreds
→ thousands
→ larger synthetic workloads
```

Explain why small datasets are useful for understanding storage behavior.

---

# 36. REQUIRED CONCEPTUAL DIAGRAMS

Use ASCII diagrams whenever useful.

At minimum include diagrams for:

### Hudi architecture

```text
Application / Pipeline
        |
        v
   Spark / Engine
        |
        v
    Hudi Table
     /       \
    v         v
Data Files   Metadata
             |
             v
          Timeline
```

### Upsert

```text
Incoming Record
      |
      v
Record Key
      |
      v
Existing?
   /      \
 Yes       No
 |          |
Update     Insert
```

### Incremental processing

```text
Commit A
   |
Commit B
   |
Commit C
   |
   v
Changes since A
   |
   v
Downstream job
```

### COW vs MOR

Show the data-flow difference clearly.

---

# 37. COMMON MISCONCEPTIONS

Explicitly identify and correct misconceptions such as:

### Misconception 1

> "Hudi is just another Parquet format."

Explain why this is incomplete.

### Misconception 2

> "Hudi replaces Kafka."

Explain the difference between:

```text
streaming transport
```

and:

```text
table storage
```

### Misconception 3

> "Upsert means update only."

Explain:

```text
update existing
+
insert new
```

### Misconception 4

> "Incremental processing means reading only new files."

Explain why this is an incomplete mental model.

### Misconception 5

> "Copy-on-Write and Merge-on-Read are just performance settings."

Explain the architectural implications.

---

# 38. PRODUCTION ARCHITECTURE EXERCISE

At the end of the lesson, give me a realistic system-design problem:

> A company receives millions of customer changes per day from PostgreSQL through CDC. The data must be stored in object storage, support frequent upserts/deletes, allow downstream consumers to process changes incrementally, and serve analytics and ML workloads.

Ask me to design:

```text
PostgreSQL
     ↓
CDC
     ↓
Kafka
     ↓
Hudi
     ↓
Downstream consumers
```

Make me decide:

- record key
- partition strategy
- COW vs MOR
- ingestion strategy
- incremental processing strategy
- schema evolution strategy
- failure recovery
- monitoring
- storage layout
- downstream access

Then provide a model senior-engineer solution.

---

# 39. HANDS-ON CAPSTONE FOR THIS FILE

Build a small but realistic:

# "CDC Customer Lakehouse Table with Apache Hudi"

Pipeline:

```text
Synthetic CDC Events
        |
        v
PySpark
        |
        v
Apache Hudi
        |
        +----> Current Table
        |
        +----> Incremental Changes
```

The synthetic CDC stream should contain:

```text
INSERT
UPDATE
DELETE
```

events.

Implement:

1. initial load
2. insert
3. update
4. upsert
5. delete
6. table inspection
7. timeline inspection where practical
8. incremental consumption
9. failure simulation
10. recovery
11. validation of final state

Keep the implementation small enough to understand.

---

# 40. DEBUGGING CHECKLIST

Create a reusable debugging checklist.

When a Hudi table behaves unexpectedly, teach me to ask:

```text
1. What is the Hudi version?
2. What is the Spark version?
3. What is the record key?
4. What is the partition key?
5. What operation was executed?
6. What write mode was used?
7. What changed in the timeline?
8. What data files changed?
9. Are duplicate logical records present?
10. Is the issue read-side or write-side?
11. Is the issue metadata-related?
12. Is the problem caused by file layout?
13. Is the issue related to incremental consumption?
14. What does the physical filesystem show?
15. What does the logical table show?
```

Explain how to use the checklist systematically.

---

# 41. KNOWLEDGE CHECKPOINTS

After every major section, stop and ask 2–5 questions.

Examples:

```text
Why can't Parquet easily perform a database-style UPDATE?

What is the purpose of a record key?

Why does Hudi maintain a timeline?

What is the difference between INSERT and UPSERT?

Why is incremental processing important?

What is the difference between COW and MOR?

Why can incorrect partitioning hurt a Hudi workload?
```

Do not immediately reveal the answer.

Give me a chance to reason first.

Then provide:

```text
Correct answer
Why it is correct
Common wrong answer
Why that answer is wrong
```

---

# 42. BEGINNER → INTERMEDIATE → ADVANCED STRUCTURE

Organize the complete lesson into three levels.

## LEVEL 1 — BEGINNER

Teach:

- data lakes
- Parquet
- mutable vs append-only data
- updates/deletes
- why table formats exist
- what Hudi is
- Hudi table
- record key
- partition
- `.hoodie`
- timeline
- insert
- update
- upsert
- delete

Goal:

> I can explain Hudi to another beginner.

---

## LEVEL 2 — INTERMEDIATE

Teach:

- Hudi architecture
- COW
- MOR
- incremental processing
- CDC
- table state
- metadata
- write operations
- partition strategy
- record-key design
- Spark integration
- filesystem inspection
- practical debugging
- Delta/Iceberg comparison

Goal:

> I can build and operate a basic Hudi table.

---

## LEVEL 3 — ADVANCED

Teach:

- production CDC architecture
- incremental consumption
- COW vs MOR trade-offs
- write/read amplification
- storage design
- partition strategy
- operational failure modes
- concurrency considerations
- metadata/timeline reasoning
- compatibility management
- performance investigation
- architecture trade-offs
- when not to use Hudi

Goal:

> I can make and defend a production Hudi architecture decision.

---

# 43. DO NOT HIDE COMPLEXITY

If Hudi has an important trade-off, limitation, operational concern, or version-specific behavior, explain it.

Do not teach:

> "Hudi makes updates easy."

Instead teach:

> "Hudi provides table-level mechanisms that make mutable lakehouse workloads practical, but those mechanisms introduce storage, metadata, write-path, compaction, and operational trade-offs that must be understood."

Always prefer engineering accuracy over marketing language.

---

# 44. FINAL REVIEW

At the end, provide:

## A. One-page mental model

Summarize:

```text
Why Hudi exists
↓
What a Hudi table is
↓
Record keys
↓
Partitions
↓
Timeline
↓
Upserts
↓
Deletes
↓
COW
↓
MOR
↓
Incremental processing
↓
CDC
↓
Production trade-offs
```

## B. Key terminology

Create a glossary of important Hudi terms.

## C. Interview questions

Create:

- 10 beginner questions
- 10 intermediate questions
- 10 advanced questions

Questions must be strictly related to this file.

## D. Scenario questions

Create at least 5 production troubleshooting/design scenarios.

Each scenario should include:

```text
Problem
Your task
Expected reasoning
Model senior-engineer solution
```

## E. Practical exercises

Create at least 10 exercises progressing from:

```text
basic
→ intermediate
→ advanced
```

## F. Final assessment

Create a final assessment containing:

- conceptual questions
- code-reading questions
- debugging questions
- architecture questions
- trade-off questions

Do not give the answers immediately.

---

# 45. FINAL EXIT CRITERIA

Do not consider this topic complete until I can independently explain:

1. Why Apache Hudi exists.
2. Why plain Parquet becomes difficult for mutable datasets.
3. What a Hudi table represents.
4. Why the `.hoodie` directory exists.
5. What the Hudi timeline represents.
6. What a record key is.
7. Why partitioning matters.
8. INSERT vs UPDATE vs UPSERT.
9. How deletes are conceptually handled.
10. What Copy-on-Write means.
11. What Merge-on-Read means.
12. COW vs MOR trade-offs.
13. Why incremental processing matters.
14. How Hudi fits into CDC architectures.
15. How Hudi differs conceptually from Delta Lake and Iceberg.
16. How to inspect and debug a Hudi table.
17. How record-key and partition design affect production workloads.
18. How to reason about Hudi failures.
19. How to evaluate Hudi for a real production workload.
20. When Hudi is **not** the right choice.

---

# 46. FINAL TEACHING RULE

Throughout the entire lesson follow this principle:

> **Do not teach Apache Hudi as a collection of commands. Teach it as a storage and table-management system designed to make mutable, incremental, large-scale data-lake workloads practical.**

Always move:

```text
Concept
→ Problem
→ Mental Model
→ Example
→ Code
→ Physical Observation
→ Failure Mode
→ Trade-off
→ Production Decision
```

Teach slowly enough that every layer builds on the previous one.

Do not skip foundational concepts.

Do not jump directly into advanced terminology.

Do not assume database or distributed-systems knowledge that has not yet been established.

Use simple examples first, then progressively increase complexity.

The final outcome should be that I can **explain Apache Hudi from first principles, implement a basic Hudi table, understand its write/read model, reason about incremental processing and CDC workloads, debug common problems, and make a defensible production architecture decision involving Hudi.**