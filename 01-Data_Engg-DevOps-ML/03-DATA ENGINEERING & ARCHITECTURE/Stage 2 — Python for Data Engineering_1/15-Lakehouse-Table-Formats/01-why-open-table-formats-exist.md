# CLAUDE CODE PROMPT — LEARN `01-why-open-table-formats-exist.md`

You are a **Senior Data Engineer with 10+ years of production experience** designing and operating large-scale data platforms, lakehouses, data warehouses, batch pipelines, streaming systems, and distributed data infrastructure.

I am learning **Stage 2 — Python for Data Engineering**, specifically:

```text
15-Lakehouse-Table-Formats/
└── 01-why-open-table-formats-exist.md
```

Your job is to teach me the complete subject covered by:

```text
01-why-open-table-formats-exist.md
```

from **absolute beginner level to advanced production-level understanding**.

## CRITICAL INSTRUCTIONS

### 1. Follow the Module 2.15 roadmap exactly

This topic is the foundation for the entire Lakehouse Table Formats module.

The authoritative roadmap requires this topic to explain:

- Why a directory of Parquet files is a dataset, not a transactional table
- Problems with plain data lakes
- Partial writes
- Lack of atomic multi-file commits
- Lack of row-level UPDATE/DELETE
- Unsafe concurrent writers
- Schema drift
- Expensive directory listing
- Small-files problem
- The metadata-layer concept
- ACID transactions
- Snapshot isolation
- MERGE / UPDATE / DELETE
- Schema enforcement
- Schema evolution
- Time travel
- File-level statistics and data skipping
- Lakehouse architecture
- Delta Lake
- Apache Iceberg
- Apache Hudi
- Hive-style tables and their limitations
- Interoperability efforts
- Delta UniForm
- Apache XTable
- When plain Parquet is still the correct choice

Do **not skip any of these concepts**.

Do not prematurely teach the internal implementation details of Delta, Iceberg, or Hudi that belong primarily to Topics 02–04. Introduce only enough of those formats here to establish **why they exist, what problems they solve, and how they differ at a high level**.

---

# 2. DO NOT MODIFY OTHER FILES

This is extremely important.

You are teaching me the contents of:

```text
15-Lakehouse-Table-Formats/01-why-open-table-formats-exist.md
```

Do **not**:

- modify another `.md` file
- rewrite the roadmap
- create another curriculum
- reorder Module 2.15
- change filenames
- remove existing topics
- teach unrelated Module 2.15 topics in depth
- jump ahead into detailed Delta/Iceberg/Hudi internals

If you need to create temporary code for demonstrations, keep it inside the learning workspace or use clearly isolated examples.

The conceptual scope must remain focused on:

> **Why Open Table Formats Exist**

---

# 3. TEACH ME FROM FIRST PRINCIPLES

Assume I am a beginner.

Do not assume I already understand:

- data lakes
- Parquet
- object storage
- transactions
- ACID
- concurrency
- snapshots
- metadata
- schema evolution
- data warehouses
- lakehouses
- table formats

If a concept is necessary, explain it before using it.

For every important concept, follow this teaching pattern:

```text
What is it?
↓
Why does it exist?
↓
What problem does it solve?
↓
How does it work conceptually?
↓
Simple example
↓
Real data-engineering example
↓
Failure scenario
↓
How table formats solve it
↓
Production implications
```

Use simple language first.

Then progressively introduce professional terminology.

---

# 4. START WITH THE MENTAL MODEL

Before discussing Delta Lake, Iceberg, or Hudi, establish this mental model:

```text
Data source
    ↓
Raw files
    ↓
Parquet dataset
    ↓
??? 
    ↓
Transactional table
    ↓
Lakehouse
```

Explain why:

```text
Parquet ≠ Table Format
```

and:

```text
Object Storage + Parquet ≠ Lakehouse
```

Then introduce:

```text
Object Storage
      +
Open File Format
      +
Table Format / Metadata Layer
      +
Catalog
      +
Compute Engines
      =
Lakehouse
```

Explain each component individually.

---

# 5. EXPLAIN WHAT A PLAIN DATA LAKE ACTUALLY IS

Start with a concrete example.

Create a simple dataset such as:

```text
orders/
├── date=2026-01-01/
│   ├── part-000.parquet
│   └── part-001.parquet
├── date=2026-01-02/
│   ├── part-000.parquet
│   └── part-001.parquet
└── date=2026-01-03/
    └── part-000.parquet
```

Explain:

- object storage
- files
- directories/prefixes
- partitions
- Parquet
- dataset
- logical table

Make it clear that the directory structure does not automatically provide transactional semantics.

---

# 6. TEACH "A DIRECTORY OF PARQUET FILES IS NOT A TABLE"

This is the central concept.

Explain the difference between:

```text
Dataset
```

and:

```text
Transactional Table
```

Create a detailed comparison covering:

| Capability | Plain Parquet Dataset | Open Table Format |
|---|---|---|
| File storage | Yes | Yes |
| Schema | Limited | Managed |
| Atomic commits | No | Yes |
| Transactions | No | Yes |
| UPDATE | Difficult/rewrites | Supported |
| DELETE | Difficult/rewrites | Supported |
| MERGE | Difficult | Supported |
| Concurrent writers | Unsafe without external coordination | Controlled |
| Time travel | No built-in table history | Yes |
| Snapshot isolation | No | Yes |
| Schema evolution | Manual | Managed |
| Data skipping metadata | Limited | Integrated |
| Table history | No | Yes |
| Maintenance | Manual | Transactionally managed |

Explain why every row matters.

---

# 7. DEMONSTRATE THE FAILURE OF PLAIN PARQUET

Use Python and PyArrow/PySpark examples where appropriate.

Create a small realistic dataset:

```text
customer_id
order_id
order_date
amount
status
```

Show how it is written to Parquet.

Then explain:

```python
df.write.mode("overwrite").parquet(...)
```

and why a multi-file overwrite can expose intermediate state.

Do not merely state the problem.

Demonstrate it conceptually and, where practical, reproduce it.

---

# 8. FAILURE SCENARIO 1 — PARTIAL WRITE

Demonstrate:

```text
Writer
  ↓
writes file 1
  ↓
writes file 2
  ↓
writes file 3
  ↓
CRASH
```

while:

```text
Reader
  ↓
reads the directory
```

Explain what the reader can see.

Show why:

```text
"files eventually become correct"
```

is not equivalent to:

```text
"the table changed atomically"
```

Explain:

- partial visibility
- inconsistent snapshots
- incomplete datasets
- downstream corruption
- why atomic commit metadata is needed

Use a small reproducible example if possible.

---

# 9. FAILURE SCENARIO 2 — CONCURRENT WRITERS

Demonstrate two writers:

```text
Writer A
    ↓
reads current dataset
    ↓
modifies data
    ↓
writes

Writer B
    ↓
reads current dataset
    ↓
modifies data
    ↓
writes
```

Explain the lost-update problem.

Show a concrete example.

For example:

```text
Initial:
customer_id=1, balance=100

Writer A:
balance=150

Writer B:
balance=200
```

Explain how one writer can overwrite the other.

Then explain why a table format needs a transactional commit mechanism and concurrency control.

Do NOT yet go deeply into Delta optimistic concurrency internals. That belongs to Topic 02.

---

# 10. FAILURE SCENARIO 3 — ROW-LEVEL DELETE

Explain why this is problematic:

```text
DELETE customer_id = 123
```

when the data exists in:

```text
1 billion rows
500 Parquet files
```

Explain:

- why Parquet itself does not provide row-level table semantics
- why rewriting files may be required
- why this is expensive
- why GDPR/right-to-be-forgotten requirements make this important
- why logical deletion and physical deletion are different

Do not teach the complete VACUUM/retention process yet. That belongs to Topic 08.

---

# 11. FAILURE SCENARIO 4 — SCHEMA DRIFT

Demonstrate a situation where different Parquet files contain:

```text
File A:
customer_id
name
email
```

and:

```text
File B:
customer_id
name
email
phone
```

Then another file changes:

```text
customer_id
name
email
phone
country
```

Explain:

- schema drift
- inconsistent schemas
- reader complexity
- producer/consumer problems
- why schema management matters

Then introduce:

```text
Schema Enforcement
```

and:

```text
Schema Evolution
```

at a conceptual level.

Do not go deeply into implementation-specific Delta/Iceberg schema mechanics yet.

---

# 12. FAILURE SCENARIO 5 — EXPENSIVE DIRECTORY LISTING

Explain why traditional data lakes can suffer from:

```text
Query
 ↓
list directories
 ↓
find files
 ↓
inspect files
 ↓
determine relevant files
 ↓
read data
```

Explain why this becomes expensive with:

```text
millions of files
```

and:

```text
deep partition structures
```

Introduce the idea of table metadata and file-level statistics.

---

# 13. FAILURE SCENARIO 6 — SMALL FILES

Explain:

```text
10,000 tiny Parquet files
```

versus:

```text
100 well-sized Parquet files
```

Discuss:

- file-open overhead
- metadata overhead
- scheduling overhead
- object-store requests
- query planning overhead
- poor scan performance
- why streaming and frequent writes can create small files

Do not go deeply into Topic 07's compaction algorithms yet.

Only establish why table-layout maintenance becomes necessary.

---

# 14. INTRODUCE THE METADATA-LAYER CONCEPT

This is one of the most important parts.

Explain:

```text
Parquet files
       +
Metadata
       =
Table
```

Then explain conceptually what metadata can record:

```text
Current table version
        ↓
Which files belong to the table
        ↓
Which files were removed
        ↓
Schema
        ↓
Partition information
        ↓
Statistics
        ↓
History
```

Explain why this changes the architecture.

Use a simple analogy if helpful:

```text
Files = pages
Metadata = index/catalog describing the valid version of the book
```

But make clear that this is only an analogy and not a literal implementation.

---

# 15. EXPLAIN ACID TRANSACTIONS

Teach ACID from first principles.

Explain:

### Atomicity

Either:

```text
all changes become visible
```

or:

```text
none become visible
```

### Consistency

The table remains within defined validity rules.

### Isolation

Readers should see a consistent snapshot rather than half-finished changes.

### Durability

Once a commit succeeds, it should survive process failure.

Then explain why these properties are valuable for data lakes.

Use concrete examples.

---

# 16. EXPLAIN SNAPSHOT ISOLATION

Start with:

```text
Reader starts
    ↓
sees version 10
```

Meanwhile:

```text
Writer commits version 11
```

The reader should still be able to finish against its consistent snapshot.

Explain:

```text
Reader → Snapshot 10

Writer → Snapshot 11
```

instead of:

```text
Reader → half version 10 + half version 11
```

Connect this to:

- concurrent readers
- concurrent writers
- reproducibility
- analytics queries
- long-running jobs

Do not teach format-specific implementation details yet.

---

# 17. EXPLAIN MERGE / UPDATE / DELETE

Teach the conceptual value of:

```sql
MERGE
UPDATE
DELETE
```

on a lakehouse table.

Use a small example:

```sql
MERGE INTO customers AS target
USING updates AS source
ON target.customer_id = source.customer_id
...
```

Explain:

- insert
- update
- delete
- CDC workloads
- SCD workloads
- why this is difficult with plain files
- why transactional table semantics make it practical

Do not yet teach the detailed Delta/Iceberg implementation.

---

# 18. EXPLAIN TIME TRAVEL

Start with:

```text
Version 1
   ↓
Version 2
   ↓
Version 3
```

Explain why historical versions are valuable for:

- auditing
- debugging
- reproducibility
- ML training datasets
- rollback
- "what changed?"
- incident investigation

Use a conceptual example:

```text
Today:
Revenue = ₹10M

Yesterday:
Revenue = ₹8M
```

Explain how a historical snapshot helps investigate the difference.

Do not yet teach the complete implementation of Delta/Iceberg time travel.

---

# 19. EXPLAIN FILE-LEVEL STATISTICS AND DATA SKIPPING

Teach the basic idea.

Example:

```text
File A:
amount min = 10
amount max = 100

File B:
amount min = 1000
amount max = 2000
```

For:

```sql
WHERE amount > 1500
```

explain why File A can potentially be skipped.

Explain:

```text
Metadata
   ↓
Statistics
   ↓
Pruning
   ↓
Less data scanned
   ↓
Faster query
   ↓
Lower compute cost
```

Do not dive into advanced Z-ordering or liquid clustering yet.

---

# 20. BUILD THE LAKEHOUSE ARCHITECTURE

Teach this architecture carefully:

```text
                    ┌────────────────────┐
                    │   Query Engines    │
                    │ Spark / DuckDB /   │
                    │ Trino / Flink / ML │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │      Catalog       │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │   Table Format     │
                    │ Delta / Iceberg /  │
                    │ Hudi               │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │   Object Storage   │
                    │ S3 / MinIO / GCS / │
                    │ ADLS               │
                    └────────────────────┘
```

Explain each layer.

Then explain why:

```text
Open storage
+
Open table format
+
Catalog
+
Multiple engines
```

creates a lakehouse architecture.

---

# 21. INTRODUCE DELTA LAKE, ICEBERG, AND HUDI

At this stage, do NOT teach their internal architecture in depth.

Only explain:

## Delta Lake

High-level characteristics:

- transactional lakehouse table format
- strong integration with Spark/Databricks ecosystem
- transaction-log-based design
- ACID operations
- schema management
- time travel

## Apache Iceberg

High-level characteristics:

- open table format
- designed for large analytical tables
- strong multi-engine ecosystem
- snapshot-based metadata architecture
- hidden partitioning
- schema/partition evolution

## Apache Hudi

High-level characteristics:

- designed heavily around upserts and incremental processing
- strong CDC-oriented use cases
- copy-on-write and merge-on-read
- timeline-based model

Create a high-level comparison:

| Area | Delta | Iceberg | Hudi |
|---|---|---|---|
| Core purpose | Transactional lakehouse | Open analytical tables | Upsert/incremental lake workloads |
| Transactions | Yes | Yes | Yes |
| Time travel | Yes | Yes | Yes |
| Updates/deletes | Yes | Yes | Yes |
| CDC/upserts | Strong | Strong | Very strong |
| Multi-engine | Strong and growing | Very strong | Strong |
| Metadata model | Transaction log | Metadata/snapshot tree | Timeline |
| Best known strength | Transactional lakehouse workflows | Open multi-engine architecture | Incremental/upsert-heavy workloads |

Clearly label this as a **high-level introduction** because Topics 02–04 will teach their internals separately.

---

# 22. EXPLAIN HIVE-STYLE TABLES

Teach:

```text
Hive-style partitioning
```

such as:

```text
orders/
year=2026/
month=01/
day=01/
```

Explain:

- why Hive-style layouts were useful
- metastore concept
- partition discovery
- schema metadata
- limitations
- why a metastore plus directory partitions was still not equivalent to a modern transactional table format

Make the historical progression clear:

```text
Files
 ↓
Partitioned Files
 ↓
Hive-style Tables
 ↓
Open Table Formats
 ↓
Lakehouse
```

---

# 23. EXPLAIN INTEROPERABILITY

Explain the problem:

```text
Engine A writes
Engine B reads
Engine C performs analytics
Engine D performs ML
```

Why open table formats aim to provide shared table semantics across engines.

Introduce at a high level:

- Delta UniForm
- Apache XTable

Explain what interoperability means conceptually.

Do not make unsupported claims about universal feature compatibility.

Emphasize:

> A table format may be readable by an engine while specific advanced features are not supported for reading or writing.

---

# 24. EXPLAIN WHEN PLAIN PARQUET IS STILL THE RIGHT CHOICE

Do NOT teach:

> "Table formats are always better."

Instead explain when plain Parquet remains appropriate.

Examples:

```text
Immutable historical dataset
```

```text
Write once, read many
```

```text
No updates
```

```text
No deletes
```

```text
No concurrent writers
```

```text
No requirement for time travel
```

```text
Simple analytical file exchange
```

Create a decision framework:

```text
Does the dataset change?
        │
        ├── No
        │    ↓
        │  Plain Parquet may be sufficient
        │
        └── Yes
             ↓
       Do you need transactions?
             │
             ├── No → evaluate carefully
             │
             └── Yes
                  ↓
             Table format
```

Explain the trade-offs rather than blindly recommending table formats.

---

# 25. HANDS-ON LAB — PLAIN LAKE FAILURES

Follow the roadmap's required experiments.

Create:

```text
experiments/01_plain_lake_failures/
```

Use MinIO/object storage where practical.

Perform these experiments:

### Experiment 1 — Partial Write

1. Write a Parquet dataset.
2. Simulate a multi-file write.
3. Interrupt the write.
4. Read the dataset.
5. Document what the reader sees.

### Experiment 2 — Concurrent Overwrite

Run two concurrent writers against the same partition.

Document:

```text
Writer A
Writer B
Final state
Lost updates
Potential inconsistency
```

### Experiment 3 — Expensive Row Delete

Create a realistic smaller dataset.

Estimate what happens if one customer's rows must be removed.

Explain the scaling implications for:

```text
10K rows
1M rows
100M rows
1B rows
```

Do not actually create a 1-billion-row dataset if it is impractical.

Use analytical estimation.

### Experiment 4 — Compare With Delta and Iceberg

Repeat the partial-write/concurrent-write experiments conceptually or practically using Delta and Iceberg.

The goal is to observe the difference.

---

# 26. REQUIRE ME TO INSPECT THE FILE SYSTEM

For every experiment, inspect:

```text
data files
metadata
directories
file counts
file sizes
```

Explain:

```text
What changed?
Why did it change?
What does the reader see?
What metadata would be required to make the operation atomic?
```

This is important because I want to understand the system internally rather than memorize commands.

---

# 27. CODING REQUIREMENTS

Use practical Python examples.

Prefer:

- Python
- PyArrow
- PySpark
- DuckDB
- MinIO
- Parquet

Use SQL where useful.

Every code example must include:

1. Purpose
2. Code
3. Expected result
4. Explanation
5. Failure mode
6. Production implication

Do not provide unexplained code dumps.

If a dependency is required, explain:

```bash
pip install ...
```

or the appropriate environment setup.

Do not introduce unnecessary libraries.

---

# 28. FORCE PREDICTION BEFORE EXECUTION

For every important experiment, ask me to predict:

```text
What files will exist?
What will happen if the job fails?
What will the reader see?
What happens if two writers run simultaneously?
What metadata is missing?
How would a table format solve this?
```

Then execute the experiment and compare:

```text
My prediction
vs
Actual result
```

This should be part of the teaching methodology.

---

# 29. USE PROGRESSIVE DIFFICULTY

Structure the lesson as:

```text
Level 0 — Absolute basics
Level 1 — Data lake fundamentals
Level 2 — Plain Parquet limitations
Level 3 — Metadata and transaction concepts
Level 4 — Lakehouse architecture
Level 5 — Delta/Iceberg/Hudi overview
Level 6 — Failure experiments
Level 7 — Production reasoning
Level 8 — Architecture decisions
```

Do not jump from beginner concepts directly into advanced terminology.

---

# 30. USE REAL-WORLD SCENARIOS

Use realistic scenarios such as:

### Scenario A — E-commerce

```text
orders
customers
payments
```

### Scenario B — CDC

```text
PostgreSQL
   ↓
CDC
   ↓
Data Lake
```

### Scenario C — Analytics

```text
Spark
DuckDB
Trino
BI
```

### Scenario D — ML

```text
Lakehouse snapshot
      ↓
Training dataset
      ↓
ML model
```

For each scenario, explain why plain Parquet becomes difficult and why table semantics help.

---

# 31. PRODUCTION ENGINEERING PERSPECTIVE

For each major concept, explain the production consequences.

Cover:

- correctness
- reliability
- concurrency
- recoverability
- auditability
- reproducibility
- cost
- performance
- interoperability
- operational complexity
- governance

Teach me to think like a production Data Engineer rather than someone who merely knows syntax.

---

# 32. COMMON MISCONCEPTIONS

Explicitly correct these misconceptions:

```text
"Parquet is a table format."
```

```text
"Partitioning makes a dataset transactional."
```

```text
"A Hive metastore automatically gives ACID transactions."
```

```text
"UPDATE on Parquet is equivalent to UPDATE on a table format."
```

```text
"DELETE means the physical bytes are immediately gone."
```

```text
"Time travel means infinite historical retention."
```

```text
"Every engine supports every table-format feature."
```

```text
"Table formats eliminate the small-files problem automatically."
```

```text
"Lakehouse means object storage alone."
```

```text
"Open table formats make warehouses unnecessary in every workload."
```

Explain why each statement is incorrect or incomplete.

---

# 33. ARCHITECTURE COMPARISON

Make me compare:

```text
Architecture A

Object Storage
+
Parquet
```

versus:

```text
Architecture B

Object Storage
+
Parquet
+
Hive Metastore
```

versus:

```text
Architecture C

Object Storage
+
Parquet
+
Open Table Format
+
Catalog
+
Multiple Engines
```

Explain what capabilities are gained at each step.

---

# 34. DECISION-MAKING EXERCISES

Give me production scenarios and ask me to choose:

```text
Plain Parquet
vs
Delta
vs
Iceberg
vs
Hudi
```

But for this topic, keep the format selection high-level.

Examples:

1. Immutable monthly government data.
2. High-volume CDC customer database.
3. Multi-engine enterprise lakehouse.
4. Frequent updates to customer records.
5. ML training datasets requiring reproducibility.
6. Simple archival data.
7. Large analytical tables requiring partition evolution.

For every answer, require justification based on workload characteristics.

---

# 35. CHECKPOINTS

After each major section, stop and ask me 3–5 questions.

Examples:

```text
Why is a directory of Parquet files not a transactional table?

What problem does metadata solve?

Why can a reader see partial data?

What is snapshot isolation?

Why is UPDATE difficult on plain Parquet?

Why are table formats useful for CDC?

When would plain Parquet still be better?
```

Do not proceed if my understanding is weak.

If I answer incorrectly:

1. Identify the exact misconception.
2. Explain it again more simply.
3. Give another example.
4. Ask a similar question.
5. Only continue after I demonstrate understanding.

---

# 36. FINAL KNOWLEDGE CHECK

At the end, conduct a structured assessment.

### Basic

10 questions.

### Intermediate

10 questions.

### Advanced

10 questions.

### Production Architecture

5 scenario-based questions.

Do not immediately provide the answers.

Wait for my responses and grade them.

---

# 37. FINAL PRACTICAL CHALLENGE

Give me this problem:

> We have an e-commerce data lake containing billions of orders stored as Parquet files in object storage. Multiple pipelines write concurrently. CDC updates arrive continuously. Analysts query the data through multiple engines. Compliance requires customer deletion. ML engineers need reproducible historical datasets.

Ask me to design the architecture.

I must explain:

```text
Storage
+
File format
+
Table format
+
Metadata
+
Catalog
+
Transactions
+
Concurrency
+
Updates
+
Deletes
+
Time travel
+
Interoperability
+
Maintenance
```

Do not solve it immediately.

First ask me to propose the architecture.

Then review my design as a Senior Data Engineer.

---

# 38. FINAL EXIT CRITERIA

Do not consider this topic complete until I can independently explain:

- [ ] Why a directory of Parquet files is not a table
- [ ] What a data lake is
- [ ] Why plain Parquet lacks transactional semantics
- [ ] Partial-write failure
- [ ] Concurrent-writer failure
- [ ] Row-level update/delete limitations
- [ ] Schema drift
- [ ] Small-files problem
- [ ] Directory-listing/planning problems
- [ ] Metadata-layer concept
- [ ] ACID transactions
- [ ] Snapshot isolation
- [ ] MERGE / UPDATE / DELETE conceptually
- [ ] Schema enforcement
- [ ] Schema evolution
- [ ] Time travel
- [ ] File-level statistics
- [ ] Data skipping
- [ ] Lakehouse architecture
- [ ] Delta Lake at a high level
- [ ] Apache Iceberg at a high level
- [ ] Apache Hudi at a high level
- [ ] Hive-style tables
- [ ] Interoperability
- [ ] Delta UniForm at a high level
- [ ] Apache XTable at a high level
- [ ] When plain Parquet is still appropriate
- [ ] Trade-offs between simplicity and transactional table semantics

Most importantly, I should be able to answer:

> **"Why do open table formats exist?"**

without memorizing an answer.

I should be able to reason from the underlying data-engineering problems and derive the need for table formats myself.

---

# 39. TEACHING STYLE

Use:

- Simple language first
- Precise technical terminology second
- ASCII diagrams
- Tables
- Small datasets
- Python code
- SQL examples
- Failure simulations
- File-system inspection
- Metadata inspection
- Production scenarios
- Architecture diagrams
- Questions
- Exercises
- Debugging
- Prediction-before-execution
- Incremental difficulty

Avoid:

- unexplained jargon
- huge code dumps
- superficial definitions
- memorization-only teaching
- skipping failure scenarios
- jumping directly to advanced internals
- unrelated technologies
- unrelated Module 2.15 topics
- modifying other curriculum files

---

# 40. IMPORTANT FINAL RULE

Teach this topic as the **foundation for the rest of Module 2.15**.

The purpose is not merely to teach me:

> "What is Delta Lake?"

The purpose is to make me understand:

> **Why the data-engineering industry needed something beyond directories of Parquet files, how those limitations manifest in real systems, and why open table formats are the architectural response.**

Build that mental model deeply enough that when I later study:

```text
02-delta-lake-transaction-log.md
03-apache-iceberg-snapshots-and-manifests.md
04-apache-hudi-overview.md
05-acid-merge-update-and-delete-on-data-lakes.md
...
```

I already understand **why those mechanisms exist**.

Follow the roadmap's dependency order and do not skip concepts.

Start with:

# "What exactly is a data lake, and why isn't a directory full of Parquet files a table?"

Then teach me step by step.