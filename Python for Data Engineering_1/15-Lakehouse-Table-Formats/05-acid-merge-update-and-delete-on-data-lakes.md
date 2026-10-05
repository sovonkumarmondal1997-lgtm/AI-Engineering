# CLAUDE CODE PROMPT — LEARN `05-acid-merge-update-and-delete-on-data-lakes.md`

## ROLE

Act as a **Senior Data Engineer with 10+ years of production experience** designing and operating large-scale data platforms, lakehouses, data warehouses, CDC pipelines, Apache Spark, Delta Lake, Apache Iceberg, Apache Hudi, object storage, and distributed data systems.

You are my instructor.

Your job is to teach me the complete topic covered by:

```text
15-Lakehouse-Table-Formats/
└── 05-acid-merge-update-and-delete-on-data-lakes.md
```

Teach this topic from:

```text
absolute beginner
        ↓
fundamentals
        ↓
intermediate
        ↓
advanced
        ↓
production data engineering
```

Use simple language first, then progressively introduce the correct technical terminology.

The objective is not simply to teach SQL syntax.

The objective is to make me understand **how and why ACID mutations work on data lakes**, including:

- why UPDATE and DELETE are difficult on ordinary data lakes
- what ACID means in a lakehouse
- what transactional table formats provide
- how INSERT, UPDATE, DELETE, and MERGE work
- how row-level changes are represented
- how concurrent writers are handled
- how failures affect table state
- how CDC workloads use MERGE
- how SCD patterns use MERGE
- how copy-on-write and merge-on-read affect mutations
- how schema evolution interacts with mutations
- how mutation-heavy workloads affect files and performance
- how to reason about production architecture and trade-offs

---

# 1. STRICT FILE-SCOPE RULE

You are teaching **ONLY**:

```text
05-acid-merge-update-and-delete-on-data-lakes.md
```

Do NOT modify, rewrite, create, rename, delete, or update any other file in:

```text
15-Lakehouse-Table-Formats/
```

Do NOT modify:

```text
README.md
01-why-open-table-formats-exist.md
02-delta-lake-transaction-log.md
03-apache-iceberg-snapshots-and-manifests.md
04-apache-hudi-overview.md
06-time-travel-and-table-versioning.md
07-compaction-z-ordering-and-liquid-clustering.md
08-vacuum-retention-and-table-maintenance.md
09-catalogs-hive-metastore-glue-unity-and-polaris.md
practice-questions.md
```

You may read prerequisite material for context if needed.

However:

> **Do not modify any other file.**

All work must remain scoped to:

```text
05-acid-merge-update-and-delete-on-data-lakes.md
```

---

# 2. AUTHORITATIVE ROADMAP RULE

Treat the existing Module 2.15 roadmap as the authoritative source for this lesson.

The lesson must remain focused on the roadmap's intended scope:

> **ACID, MERGE, UPDATE, and DELETE on data lakes**

Do not silently replace the roadmap with a different curriculum.

Do not turn this file into a complete Delta Lake, Iceberg, or Hudi implementation manual.

Use Delta Lake, Apache Iceberg, and Apache Hudi as examples where they help explain the underlying concepts.

Clearly distinguish:

```text
Core concept
Supporting example
Implementation-specific behavior
Advanced optional context
```

If a detail depends on the specific table format or version, explicitly say so.

---

# 3. CORE LEARNING OBJECTIVE

By the end of this lesson, I should understand this transformation:

```text
Plain Parquet files
        ↓
Immutable file problem
        ↓
Need for transactional semantics
        ↓
ACID table
        ↓
Logical row-level mutations
        ↓
INSERT
UPDATE
DELETE
MERGE
        ↓
CDC / SCD / synchronization
        ↓
Concurrency
        ↓
Failure recovery
        ↓
Production optimization
```

Do not teach this as merely:

```sql
UPDATE ...
DELETE ...
MERGE ...
```

Teach the storage-engineering problem underneath those commands.

---

# 4. START WITH A FUNDAMENTAL QUESTION

Begin with:

> **Why is UPDATE difficult on a data lake?**

Assume I have only:

```text
Parquet
+
object storage
```

and a table:

```text
customers/
    part-000.parquet
    part-001.parquet
    part-002.parquet
```

Suppose:

```text
customer_id = 101
city = "Delhi"
```

must become:

```text
customer_id = 101
city = "Mumbai"
```

Explain why this is not equivalent to:

```sql
UPDATE customers
SET city = 'Mumbai'
WHERE customer_id = 101;
```

in a traditional database.

Explain:

- immutable files
- row-level modification
- file rewriting
- object storage semantics
- partial writes
- readers observing intermediate states
- concurrent writers
- metadata/state management

Build the problem before introducing the solution.

---

# 5. DATABASE TABLE VS DATA-LAKE FILES

Create a fundamental comparison.

Compare:

```text
Traditional Database
```

with:

```text
Parquet Data Lake
```

Explain:

| Capability | Database | Plain Parquet Data Lake |
|---|---|---|
| Row INSERT | Easy | Easy-ish |
| Row UPDATE | Native | Difficult |
| Row DELETE | Native | Difficult |
| Transactions | Native | Not inherently provided |
| Concurrent writes | Managed | Must be engineered |
| Atomic multi-file changes | Supported | Not inherently guaranteed |
| Recovery | Transaction mechanisms | Application/system dependent |

Do not oversimplify.

Explain that "Parquet is immutable" refers to file-level behavior, not that data can never logically change.

---

# 6. WHAT DOES ACID MEAN?

Teach ACID from first principles.

Explain:

```text
A = Atomicity
C = Consistency
I = Isolation
D = Durability
```

For each property:

1. Define it simply.
2. Explain why it matters.
3. Give a database example.
4. Give a lakehouse example.
5. Show what could go wrong without it.

---

## 6.1 ATOMICITY

Example:

```text
Transaction intends to write:

file-A
file-B
file-C
```

Suppose:

```text
file-A → success
file-B → success
file-C → failure
```

Explain the problem.

Then explain the desired behavior:

```text
ALL changes visible
OR
NO changes visible
```

Explain that lakehouse table formats use metadata/commit mechanisms to provide logical atomicity across file changes.

---

## 6.2 CONSISTENCY

Explain what it means for a table to remain valid before and after a transaction.

Use examples such as:

```text
primary/record key uniqueness
schema constraints
referential/business rules where applicable
```

Do not incorrectly imply that every database-style constraint automatically exists in every table format.

Clearly distinguish:

```text
database constraints
```

from:

```text
table-format/data-quality guarantees
```

---

## 6.3 ISOLATION

Explain concurrent readers/writers.

Example:

```text
Writer A
Writer B
Reader C
```

Explain why readers should not normally see an inconsistent intermediate table state.

Introduce snapshot-based thinking at a conceptual level.

---

## 6.4 DURABILITY

Explain:

> Once a transaction is committed, its state should survive process failure.

Connect this to:

```text
object storage
metadata
commits
durable files
```

---

# 7. ACID IN A LAKEHOUSE

Now connect the concepts.

Explain:

```text
Data files
+
Transaction metadata
+
Atomic commit
+
Table state
=
Transactional lakehouse table
```

Use a conceptual architecture:

```text
                 Table
                   |
        +----------+----------+
        |                     |
    Data Files            Metadata
        |                     |
     Parquet              Commits
                              |
                         Table State
```

Explain why the metadata layer is essential.

---

# 8. LOGICAL ROW CHANGE VS PHYSICAL FILE CHANGE

This distinction is mandatory.

Explain:

> A logical UPDATE of one row does not necessarily mean one physical row is edited in place.

Use:

```text
Logical operation:

customer_id=101
city: Delhi → Mumbai
```

versus:

```text
Physical operation:

old file
   ↓
new/rewritten file
```

Explain why this distinction matters.

Teach me to always ask:

```text
What did I logically request?
What happened physically?
What metadata changed?
What files changed?
```

---

# 9. INSERT

Teach INSERT first.

Explain:

```text
INSERT
```

means adding new logical records.

Use a simple table:

| id | name | city |
|---|---|---|
| 1 | Alice | Delhi |
| 2 | Bob | Mumbai |

Incoming:

| id | name | city |
|---|---|---|
| 3 | Charlie | Kolkata |

Explain the logical result.

Then explain the physical implication for a lakehouse table.

Provide a Spark/SQL example where appropriate.

---

# 10. UPDATE

Now introduce UPDATE.

Use:

```text
Before:

id | city
1  | Delhi
2  | Mumbai
```

Operation:

```sql
UPDATE customers
SET city = 'Pune'
WHERE id = 2;
```

Result:

```text
id | city
1  | Delhi
2  | Pune
```

Then explain what may happen physically.

Discuss:

```text
file rewrite
copy-on-write
delete + add
row-level change representation
```

Clearly state that the exact physical mechanism depends on the table format and configuration.

---

# 11. DELETE

Explain DELETE in the same way.

Use:

```sql
DELETE FROM customers
WHERE id = 2;
```

Explain:

```text
Logical result
```

versus:

```text
Physical storage behavior
```

Explain why physically removing one row from a Parquet file is not equivalent to removing a row from a database page.

Discuss:

- rewrite
- delete metadata
- tombstone/deletion representation where applicable
- merge-on-read approaches where applicable

Do not incorrectly generalize one table format's mechanism to all formats.

---

# 12. UPSERT

Introduce:

```text
UPSERT
```

as a fundamental data-engineering pattern.

Explain:

> If the record exists, update it. If it does not exist, insert it.

Example:

Existing:

| id | name | city |
|---|---|---|
| 1 | Alice | Delhi |
| 2 | Bob | Mumbai |

Incoming:

| id | name | city |
|---|---|---|
| 2 | Bob | Pune |
| 3 | Charlie | Kolkata |

Result:

| id | name | city |
|---|---|---|
| 1 | Alice | Delhi |
| 2 | Bob | Pune |
| 3 | Charlie | Kolkata |

Explain why UPSERT is extremely important for:

- CDC
- API synchronization
- database replication
- customer master data
- dimensions
- event-driven pipelines

---

# 13. MERGE

Treat MERGE as one of the most important topics in this lesson.

Start with:

> What problem does MERGE solve?

Explain why separate:

```text
INSERT
+
UPDATE
+
DELETE
```

logic can become complicated when processing a batch of changes.

Then introduce:

```sql
MERGE INTO target
USING source
ON target.id = source.id
...
```

Explain each component.

---

# 14. MERGE ANATOMY

Break MERGE into:

```text
MERGE INTO
USING
ON
WHEN MATCHED
WHEN NOT MATCHED
WHEN NOT MATCHED BY SOURCE
```

Only teach clauses supported by the selected engine/table format.

For each clause explain:

### Target

What table is being changed?

### Source

What incoming data is being applied?

### ON

How are records matched?

### WHEN MATCHED

What happens when the record exists?

### WHEN NOT MATCHED

What happens when the record does not exist?

### NOT MATCHED BY SOURCE

Explain this only where supported.

---

# 15. MERGE EXAMPLE

Use a concrete example.

Target:

| customer_id | name | city |
|---|---|---|
| 1 | Alice | Delhi |
| 2 | Bob | Mumbai |

Source:

| customer_id | name | city |
|---|---|---|
| 2 | Bob | Pune |
| 3 | Charlie | Kolkata |

Write a complete MERGE statement.

Then explain line by line.

Show the final result:

| customer_id | name | city |
|---|---|---|
| 1 | Alice | Delhi |
| 2 | Bob | Pune |
| 3 | Charlie | Kolkata |

Then explain the physical storage implications.

---

# 16. MERGE MATCHING SEMANTICS

Teach this carefully.

Explain that correctness depends heavily on:

```text
ON condition
```

For example:

```sql
ON target.customer_id = source.customer_id
```

Ask:

> What happens if the source contains two records for the same customer_id?

Explain why source duplicates can cause:

- ambiguous matches
- multiple updates
- errors
- incorrect results

Teach the importance of deduplicating the source before MERGE when required.

---

# 17. SOURCE DEDUPLICATION BEFORE MERGE

Create an example.

Source:

| customer_id | updated_at | city |
|---|---|---|
| 101 | 10:00 | Delhi |
| 101 | 10:05 | Mumbai |
| 101 | 10:03 | Pune |

Ask:

> Which record should win?

Teach a deterministic rule such as:

```text
latest updated_at
```

Then demonstrate a window function:

```sql
ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY updated_at DESC
)
```

Use it to produce exactly one source record per key before MERGE.

Explain why deterministic source data is critical.

---

# 18. CDC + MERGE

Connect MERGE to real data engineering.

Use:

```text
OLTP Database
      |
      v
CDC
      |
      v
Kafka / Event Stream
      |
      v
Raw Changes
      |
      v
Deduplication
      |
      v
MERGE
      |
      v
Lakehouse Table
```

Explain:

```text
INSERT
UPDATE
DELETE
```

events.

Show a conceptual CDC record:

```json
{
  "operation": "UPDATE",
  "customer_id": 101,
  "city": "Mumbai",
  "event_time": "2026-10-05T10:00:00"
}
```

Then explain how it becomes a lakehouse mutation.

---

# 19. CDC ORDERING

Teach an important production problem.

Suppose:

```text
UPDATE 1
UPDATE 2
UPDATE 3
```

arrive out of order.

Example:

```text
10:01 → Mumbai
10:03 → Delhi
10:02 → Pune
```

Explain why naïvely applying events can produce the wrong final state.

Discuss:

- event timestamps
- source sequence numbers
- offsets
- version columns
- deterministic ordering
- idempotency

Do not assume timestamps alone are always sufficient.

Explain why source-specific ordering guarantees matter.

---

# 20. IDEMPOTENCY

Teach idempotency carefully.

Example:

A pipeline applies:

```text
customer_id = 101
city = Mumbai
```

Then retries and applies the same event again.

Explain what should happen.

Desired behavior:

```text
First execution → state becomes Mumbai
Second execution → state remains Mumbai
```

Explain why idempotency is critical for:

- retries
- exactly-once-like pipelines
- CDC
- orchestration
- backfills
- distributed systems

Discuss practical techniques:

- event IDs
- transaction IDs
- source sequence numbers
- deterministic merge keys
- processed-event tracking where appropriate

---

# 21. SCD TYPE 1

Teach Slowly Changing Dimension Type 1 as a major MERGE use case.

Example:

```text
Customer:

id = 101
city = Delhi
```

New value:

```text
city = Mumbai
```

SCD1:

```text
overwrite old value
```

Show:

```text
Before:
101 | Delhi

After:
101 | Mumbai
```

Demonstrate using MERGE.

Explain when SCD1 is appropriate.

---

# 22. SCD TYPE 2

Introduce SCD2 carefully.

Example:

```text
Customer 101
Delhi
```

changes to:

```text
Mumbai
```

Instead of overwriting history, create:

```text
101 | Delhi  | valid_from | valid_to | current=false
101 | Mumbai | valid_from | NULL     | current=true
```

Explain:

- historical versions
- effective dates
- current flag
- closing previous record
- inserting new record

Show a MERGE-oriented implementation.

Explain that SCD2 is a modeling pattern built using mutation primitives; it is not itself a table format feature.

---

# 23. ACID + CDC + SCD2

Connect the concepts:

```text
CDC
 ↓
Deduplicate
 ↓
Order
 ↓
MERGE
 ↓
SCD2 state
 ↓
Transactional commit
```

Explain why ACID semantics become important when multiple records and multiple files are affected.

---

# 24. COPY-ON-WRITE

Explain how row-level mutation can result in file rewriting.

Example:

```text
File A
100,000 rows

Only:
1 row changes
```

Explain that depending on implementation, the affected file may need to be rewritten.

Show:

```text
Before:

file-A.parquet
      |
      v
contains old row

After:

file-A-new.parquet
      |
      v
contains updated row
```

Explain:

- write amplification
- storage amplification
- rewrite cost
- why file size matters

---

# 25. MERGE-ON-READ

Explain the alternative conceptually.

```text
Base File
+
Change Records
      ↓
Read-time merge
```

Explain:

- lower write cost in some workloads
- potentially higher read complexity
- compaction
- latency trade-offs
- storage considerations

Connect this to Hudi where relevant.

Do not turn this section into the separate maintenance/compaction topic.

---

# 26. ROW-LEVEL DELETE REPRESENTATION

Explain that different table formats can represent deletion differently.

Discuss at a conceptual level:

```text
Physical rewrite
```

versus:

```text
Delete metadata
```

versus:

```text
Delete records/files
```

Introduce the concepts of:

- copy-on-write
- merge-on-read
- position-based deletion
- equality-based deletion

Only explain these concepts to the extent necessary for understanding ACID mutations.

Do not duplicate the detailed Iceberg internals from the dedicated Iceberg lesson.

---

# 27. CONCURRENT WRITERS

This is mandatory.

Consider:

```text
Writer A
Writer B
```

Both read:

```text
Table version 10
```

Then both attempt to commit.

Explain the problem.

Use:

```text
Writer A → version 11
Writer B → version 11
```

Explain why both cannot blindly publish the same table state.

Introduce optimistic concurrency at a conceptual level.

Explain:

```text
Read current state
      ↓
Prepare changes
      ↓
Attempt commit
      ↓
Validate conflicts
      ↓
Commit or reject/retry
```

Do not claim every table format uses identical conflict-detection semantics.

---

# 28. CONCURRENCY SCENARIOS

Teach at least these scenarios.

### Scenario A — Independent partitions

```text
Writer A → partition=2026-10-01
Writer B → partition=2026-10-02
```

Explain why conflicts may be avoidable depending on the table format.

### Scenario B — Same records

```text
Writer A → customer 101
Writer B → customer 101
```

Explain conflict risk.

### Scenario C — Same file

```text
Writer A → file A
Writer B → file A
```

Explain why this is more difficult.

### Scenario D — Concurrent DELETE and UPDATE

Explain possible outcomes and why transaction semantics matter.

---

# 29. FAILED TRANSACTIONS

Teach failure scenarios.

Example:

```text
MERGE starts
      ↓
files written
      ↓
driver crashes
      ↓
commit not completed
```

Ask:

> What should a reader see?

Explain the difference between:

```text
physical files existing
```

and:

```text
files belonging to the committed table state
```

This distinction is critical.

Explain how transactional metadata prevents partially completed operations from simply becoming visible as valid table state.

---

# 30. PARTIAL FAILURE

Teach:

```text
Network failure
Object-store failure
Executor failure
Driver failure
Application crash
Concurrent commit
```

For each explain:

```text
What could happen?
What should a transactional table do?
What should the engineer inspect?
```

---

# 31. SCHEMA EVOLUTION + MERGE

Explain how schema changes can interact with MERGE.

Example:

Existing:

```text
id
name
city
```

Incoming:

```text
id
name
city
country
```

Explain:

- schema mismatch
- schema enforcement
- schema evolution
- merge behavior
- why automatic schema evolution must be deliberate

Do not assume every table format or engine automatically handles schema evolution the same way.

---

# 32. DATA QUALITY + MERGE

Teach why MERGE can amplify bad data.

Example:

Bad source:

```text
customer_id = NULL
```

or:

```text
customer_id duplicated
```

or:

```text
updated_at = NULL
```

Explain how this can corrupt the target table.

Teach the pattern:

```text
Validate
   ↓
Deduplicate
   ↓
Order
   ↓
MERGE
   ↓
Validate target
```

Connect this concept to data contracts and quality without teaching the entire separate data-quality module.

---

# 33. PERFORMANCE OF MERGE

Teach why MERGE can be expensive.

Discuss:

- target table size
- source size
- target file count
- partition pruning
- clustering
- file size
- predicate selectivity
- number of records changed
- number of files rewritten
- metadata overhead
- write amplification

Explain:

> MERGE performance is not determined only by the number of incoming rows.

Use:

```text
1 million incoming records
```

versus:

```text
1 million incoming records targeting 1 small partition
```

and:

```text
1 million incoming records spread across the entire table
```

Explain why the costs differ.

---

# 34. PARTITION PRUNING DURING MERGE

Use a table:

```text
orders/
    date=2026-10-01/
    date=2026-10-02/
    date=2026-10-03/
    ...
```

Suppose the source only affects:

```text
date=2026-10-05
```

Explain why restricting the target scan can dramatically reduce work.

Show an example where appropriate.

Explain:

```text
Bad:

MERGE scans huge target unnecessarily

Better:

MERGE identifies relevant target partitions
```

---

# 35. SMALL FILE PROBLEM

Explain how frequent mutations can create many small files.

Show:

```text
Before:

10 large files

After many tiny updates:

10,000 small files
```

Explain why this causes:

- metadata overhead
- more file opens
- slower reads
- more scheduling overhead
- inefficient object storage access

Do not deeply teach compaction here; introduce the problem and connect it to the later maintenance lesson.

---

# 36. WRITE AMPLIFICATION

Define:

```text
logical bytes changed
```

versus:

```text
physical bytes rewritten
```

Example:

```text
Logical change:
10 MB

Physical rewrite:
1 GB
```

Explain why this can happen.

Teach the relationship:

```text
file size
+
mutation distribution
+
table format/write strategy
=
write amplification
```

---

# 37. READ AMPLIFICATION

Explain the opposite problem.

For merge-on-read style systems:

```text
small base data
+
many change records
```

can require additional work during reads.

Explain:

```text
Write efficiency
vs
Read efficiency
```

and why table maintenance becomes important.

---

# 38. ACID MUTATION LAB

Create a complete hands-on lab using a small dataset.

Use a compatible local stack, preferably:

```text
PySpark
+
one supported transactional table format
+
Parquet/object-storage-compatible local path
```

Do not blindly assume a specific library version.

First inspect the environment.

Then implement:

```text
1. Initial table
2. INSERT
3. UPDATE
4. DELETE
5. UPSERT
6. MERGE
7. Concurrent write experiment
8. Failure/retry experiment
9. Source deduplication
10. Incremental CDC-style batch
```

After every operation inspect:

```text
logical table
physical files
metadata
table version/state where supported
```

---

# 39. REQUIRED MERGE LAB

Use this dataset.

Initial target:

```text
customer_id | name    | city
------------|---------|--------
1           | Alice   | Delhi
2           | Bob     | Mumbai
3           | Charlie | Kolkata
```

Incoming batch:

```text
customer_id | name    | city
------------|---------|--------
2           | Bob     | Pune
3           | Charlie | Bangalore
4           | David   | Hyderabad
```

Expected result:

```text
customer_id | name    | city
------------|---------|--------
1           | Alice   | Delhi
2           | Bob     | Pune
3           | Charlie | Bangalore
4           | David   | Hyderabad
```

Implement the MERGE.

Then explain:

- match logic
- update logic
- insert logic
- physical consequences
- idempotency

---

# 40. REQUIRED CDC LAB

Create CDC events:

```text
INSERT customer 4
UPDATE customer 2
UPDATE customer 3
DELETE customer 1
```

Represent them using a small synthetic dataset.

Process them into the target table.

Before MERGE:

```text
validate
+
deduplicate
+
order
```

Then:

```text
MERGE
```

After MERGE:

```text
validate final state
```

Explain every stage.

---

# 41. REQUIRED IDEMPOTENCY LAB

Run the same CDC batch twice.

Expected:

```text
First run:
state changes

Second run:
no unintended additional changes
```

Show why this works.

Then intentionally break idempotency and explain the failure.

For example:

```text
missing event identity
```

or:

```text
incorrect merge key
```

Then fix it.

---

# 42. REQUIRED CONCURRENCY LAB

Create two writers where practical.

Conceptually:

```text
Writer A
    |
    +---- update customer 101

Writer B
    |
    +---- update customer 101
```

Observe the behavior.

Then test:

```text
Writer A → customer 101
Writer B → customer 202
```

Compare the results.

Do not assume a particular outcome without observing the selected implementation.

Explain what the behavior teaches about transaction conflict detection.

---

# 43. REQUIRED FAILURE LAB

Simulate:

```text
write starts
files are produced
application fails before commit
```

Then inspect the table.

Explain:

```text
What files exist?
What table state is visible?
What metadata exists?
What is safe to read?
What cleanup/maintenance may eventually be needed?
```

Do not delete files blindly.

Teach safe production reasoning.

---

# 44. CROSS-FORMAT COMPARISON

After understanding the generic concepts, compare how:

```text
Delta Lake
Apache Iceberg
Apache Hudi
```

support:

```text
INSERT
UPDATE
DELETE
MERGE
ACID
concurrency
row-level changes
CDC-oriented workloads
```

Use a conceptual table.

Do not claim identical behavior.

For every difference, explain:

```text
Why the implementation differs
What workload it favors
What trade-off it creates
```

Keep this as a conceptual comparison; the deeper internals belong to the dedicated format-specific lessons.

---

# 45. PRODUCTION DESIGN SCENARIO

Give me this scenario:

> A company receives 500 million customer/order CDC events per day. The data is stored in object storage and queried by Spark, SQL engines, BI workloads, and ML pipelines. Updates and deletes are common. Some records arrive late and events can be retried.

Ask me to design the mutation architecture.

I must reason about:

```text
record identity
source deduplication
ordering
MERGE
idempotency
ACID
concurrency
partitioning
file layout
write amplification
read amplification
schema evolution
failure recovery
observability
maintenance
```

Then provide a model senior-engineer solution.

---

# 46. REAL-WORLD FAILURE SCENARIOS

Give me at least 10 production scenarios.

Examples:

### Scenario 1
MERGE produces duplicate records.

### Scenario 2
MERGE becomes extremely slow.

### Scenario 3
Updates are applied in the wrong order.

### Scenario 4
A CDC batch is processed twice.

### Scenario 5
Concurrent writers conflict.

### Scenario 6
A job crashes after writing files but before commit.

### Scenario 7
Schema changes unexpectedly.

### Scenario 8
A DELETE does not appear to remove data immediately at the physical-file level.

### Scenario 9
The table develops thousands of small files.

### Scenario 10
A 10 MB logical update causes hundreds of MB/GB of physical rewriting.

For every scenario teach:

```text
Symptoms
↓
Likely causes
↓
Investigation
↓
Fix
↓
Prevention
```

---

# 47. COMMON MISCONCEPTIONS

Explicitly teach and correct:

### Misconception 1

> "ACID means the Parquet file itself is transactional."

Correct this.

### Misconception 2

> "UPDATE edits the row directly inside a Parquet file."

Explain the logical vs physical distinction.

### Misconception 3

> "MERGE is just UPDATE + INSERT syntax."

Explain the deeper synchronization semantics.

### Misconception 4

> "MERGE is always expensive."

Explain how partition pruning, file layout, clustering, and workload shape the cost.

### Misconception 5

> "If a file exists in object storage, it is part of the table."

Explain committed table state vs unreferenced/orphaned files.

### Misconception 6

> "Running the same MERGE twice is always safe."

Explain idempotency requirements.

### Misconception 7

> "CDC automatically guarantees correct ordering."

Explain source ordering and event sequencing.

### Misconception 8

> "A successful write always means the transaction committed."

Explain the difference between physical file creation and transactional commit.

---

# 48. PERFORMANCE INVESTIGATION FRAMEWORK

When a mutation job is slow, teach me to investigate in this order:

```text
1. Source volume
2. Target table size
3. Target partitions touched
4. Target files touched
5. File sizes
6. Partition pruning
7. Match predicate
8. Source duplicates
9. Number of records updated
10. Number of records inserted
11. Number of records deleted
12. Physical rewrite volume
13. Metadata overhead
14. Concurrency
15. Object-store behavior
```

For each item explain:

```text
What to measure
Why it matters
What a bad result looks like
Possible remediation
```

Do not invent benchmark values.

If benchmarks are run, use actual observed measurements.

---

# 49. CODING REQUIREMENTS

All code examples must be:

- executable
- incremental
- beginner-friendly
- production-oriented
- version-aware
- thoroughly explained

For every important code block explain:

```text
What this code does
Why it exists
What each important line means
What happens internally
What could go wrong
```

Avoid unexplained magic configuration.

Do not use pseudocode when executable code can reasonably be provided.

When an API differs between Delta, Iceberg, and Hudi, label the implementation clearly.

For example:

```text
# Delta Lake example
```

or:

```text
# Iceberg example
```

or:

```text
# Hudi example
```

---

# 50. VERSION-AWARE TEACHING

Before running implementation examples, inspect:

```text
Python version
Java version
Spark version
Delta/Iceberg/Hudi version
```

Explain compatibility assumptions.

Table-format features and APIs can change between releases.

If a feature is version-dependent:

1. identify the dependency
2. explain it
3. adapt the example
4. state the tested assumption

Never present version-sensitive code as universally valid.

---

# 51. LEARNING LOOP

For every major experiment use:

```text
1. Explain
2. Predict
3. Execute
4. Inspect
5. Explain physical result
6. Break
7. Debug
8. Fix
9. Measure
10. Summarize
```

Do not allow me to simply copy and execute commands without understanding them.

---

# 52. BEGINNER → INTERMEDIATE → ADVANCED STRUCTURE

Organize the lesson into three levels.

## LEVEL 1 — BEGINNER

Teach:

- immutable Parquet
- why UPDATE is difficult
- why DELETE is difficult
- ACID
- transactional lakehouse tables
- INSERT
- UPDATE
- DELETE
- UPSERT
- MERGE

Goal:

> I can explain why lakehouse tables need transactional mutation capabilities.

---

## LEVEL 2 — INTERMEDIATE

Teach:

- MERGE semantics
- matching
- source deduplication
- CDC
- ordering
- idempotency
- SCD1
- SCD2
- COW
- MOR
- row-level delete concepts
- concurrency
- failure recovery
- schema evolution

Goal:

> I can build a reliable mutation pipeline.

---

## LEVEL 3 — ADVANCED

Teach:

- concurrent writers
- optimistic concurrency
- conflict detection
- write amplification
- read amplification
- partition pruning
- file-level behavior
- small-file consequences
- mutation-heavy workload design
- performance investigation
- CDC correctness
- production architecture
- cross-format trade-offs

Goal:

> I can design and troubleshoot a production lakehouse mutation architecture.

---

# 53. KNOWLEDGE CHECKPOINTS

After each major section ask 2–5 questions.

Examples:

```text
Why is UPDATE difficult on plain Parquet?

What does Atomicity mean in a lakehouse?

What is the difference between UPDATE and UPSERT?

Why can duplicate source records break MERGE?

Why does MERGE require a matching condition?

Why is idempotency important in CDC?

What happens if two writers update the same logical records?

Why can a small logical update cause a large physical rewrite?
```

Do not reveal answers immediately.

Let me reason first.

Then provide:

```text
Correct answer
Explanation
Common mistake
Production implication
```

---

# 54. REQUIRED VISUAL MENTAL MODELS

Use ASCII diagrams.

## ACID transaction

```text
Application
    |
    v
Mutation
    |
    v
Data files
    +
Metadata
    |
    v
Atomic Commit
    |
    v
New Table State
```

## MERGE

```text
Source
  |
  v
Match on key
  |
  +------ matched ------> UPDATE
  |
  +--- not matched -----> INSERT
  |
  +--- delete condition -> DELETE
```

## CDC pipeline

```text
OLTP
 |
 v
CDC
 |
 v
Kafka
 |
 v
Raw Changes
 |
 v
Deduplicate
 |
 v
Order
 |
 v
MERGE
 |
 v
Lakehouse Table
```

## Logical vs physical update

```text
Logical:

1 row changed

Physical:

old file
   ↓
rewrite/new representation
   ↓
new table state
```

---

# 55. FINAL CAPSTONE

Build a realistic mini-project:

# "Production-Style CDC MERGE Pipeline"

Architecture:

```text
Synthetic OLTP Changes
          |
          v
      CDC Batch
          |
          v
Validation
          |
          v
Deduplication
          |
          v
Ordering
          |
          v
MERGE
          |
          v
Transactional Lakehouse Table
          |
          +------> Current State
          |
          +------> Downstream Incremental Processing
```

The project must implement:

1. initial load
2. INSERT
3. UPDATE
4. DELETE
5. UPSERT
6. MERGE
7. source deduplication
8. event ordering
9. idempotent retry
10. schema evolution scenario
11. concurrent-write scenario
12. failure scenario
13. performance inspection
14. final data-quality validation

Use a small dataset first.

Then increase the workload.

Measure:

```text
records processed
records inserted
records updated
records deleted
files touched
physical bytes written where measurable
execution time
```

Do not fabricate measurements.

---

# 56. FINAL REVIEW

At the end create:

## A. One-page mental model

```text
Plain Parquet
↓
Immutable files
↓
Mutation problem
↓
ACID
↓
Transactional table
↓
INSERT
↓
UPDATE
↓
DELETE
↓
UPSERT
↓
MERGE
↓
CDC
↓
SCD
↓
Concurrency
↓
Failure recovery
↓
Performance
↓
Production architecture
```

## B. Glossary

Create a concise glossary for:

- ACID
- atomicity
- consistency
- isolation
- durability
- mutation
- UPDATE
- DELETE
- UPSERT
- MERGE
- CDC
- idempotency
- optimistic concurrency
- copy-on-write
- merge-on-read
- write amplification
- read amplification
- partition pruning
- SCD1
- SCD2
- transaction
- commit
- snapshot

---

# 57. INTERVIEW PREPARATION

Create:

### 10 Beginner Questions

Focused on:

- Parquet
- ACID
- UPDATE
- DELETE
- MERGE

### 10 Intermediate Questions

Focused on:

- CDC
- source deduplication
- idempotency
- SCD
- COW/MOR
- concurrency

### 10 Advanced Questions

Focused on:

- distributed transactions
- concurrent MERGE
- conflict detection
- write amplification
- performance
- production architecture

Every advanced question should introduce a realistic engineering problem.

Then provide a model senior-engineer answer.

---

# 58. PRACTICAL EXERCISES

Create at least 12 exercises.

Progress:

```text
Exercise 1 → Understand INSERT
Exercise 2 → UPDATE
Exercise 3 → DELETE
Exercise 4 → UPSERT
Exercise 5 → MERGE
Exercise 6 → Source deduplication
Exercise 7 → CDC
Exercise 8 → Idempotency
Exercise 9 → SCD1
Exercise 10 → SCD2
Exercise 11 → Concurrent writers
Exercise 12 → Performance investigation
```

For each exercise provide:

```text
Problem
Input
Expected reasoning
Task
Success criteria
```

Do not immediately provide the solution.

---

# 59. FINAL ASSESSMENT

Create a final assessment containing:

## Part A — Conceptual

10 questions.

## Part B — SQL / Code

5 questions.

## Part C — Debugging

5 production incidents.

## Part D — Architecture

3 system-design problems.

## Part E — Trade-offs

5 decision-making questions.

Do not provide the answers immediately.

After I attempt them, evaluate my answers as a senior data engineer.

---

# 60. FINAL EXIT CRITERIA

Do not consider this lesson complete until I can independently explain:

1. Why UPDATE is difficult on plain Parquet.
2. Why DELETE is difficult on plain Parquet.
3. What ACID means.
4. How ACID semantics apply to lakehouse tables.
5. Logical row mutation vs physical file mutation.
6. INSERT.
7. UPDATE.
8. DELETE.
9. UPSERT.
10. MERGE.
11. MERGE matching semantics.
12. Source deduplication.
13. CDC + MERGE.
14. Event ordering.
15. Idempotency.
16. SCD Type 1.
17. SCD Type 2.
18. Copy-on-Write.
19. Merge-on-Read.
20. Concurrent writers.
21. Optimistic concurrency at a conceptual level.
22. Failed/partial transactions.
23. Schema evolution during mutation.
24. Partition pruning.
25. Small-file problems.
26. Write amplification.
27. Read amplification.
28. How Delta Lake, Iceberg, and Hudi differ conceptually for mutations.
29. How to troubleshoot a failed MERGE.
30. How to design a production CDC-to-lakehouse mutation pipeline.

---

# 61. FINAL TEACHING PRINCIPLE

Throughout this entire lesson, follow this principle:

> **Teach mutations as a distributed storage problem first and a SQL problem second.**

Always move through:

```text
Problem
   ↓
Why plain Parquet struggles
   ↓
ACID requirement
   ↓
Table-format solution
   ↓
Logical mutation
   ↓
Physical storage behavior
   ↓
MERGE semantics
   ↓
CDC/SCD use cases
   ↓
Concurrency
   ↓
Failure recovery
   ↓
Performance
   ↓
Production architecture
```

Never teach:

```sql
MERGE ...
```

without explaining:

```text
What is being matched?
Why is it being matched?
What happens to the source?
What happens to the target?
What files may change?
What metadata changes?
What happens if the job fails?
What happens if another writer commits?
Can the operation be safely retried?
How expensive is the physical operation?
```

The final outcome should be that I can **reason about, implement, debug, optimize, and architect ACID-based INSERT/UPDATE/DELETE/MERGE workloads on modern data lakes and lakehouse table formats**, rather than merely memorize SQL syntax.