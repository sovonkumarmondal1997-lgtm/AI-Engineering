# Choosing a DataFrame / Analytical Engine

> **Purpose:** learn how to choose an analytical engine for a real workload using requirements, measurements, operational constraints, and explicit trade-offs.
>
> **Core rule:** an engine is chosen for a workload, not chosen in the abstract.

---

## 1. Learning Objectives

After completing this chapter, you should be able to:

- characterize an analytical workload before choosing a tool;
- explain the roles, strengths, and limits of pandas, Polars, DuckDB, and Arrow;
- reason about data size, RAM, working set, joins, windows, sorting, and output size;
- choose between SQL-first, DataFrame-first, and hybrid designs without relying on a permanent ranking;
- design fair, repeatable benchmarks;
- measure wall time, peak memory, I/O, and correctness;
- distinguish cold-cache and warm-cache behavior;
- recognize single-node limits and the situations where distributed systems become relevant;
- evaluate team skills, ecosystem dependencies, deployment targets, concurrency, serverless startup, reproducibility, upgrade churn, and maintenance burden;
- mix engines deliberately and minimize unnecessary boundaries;
- use Arrow as an interoperability layer where appropriate;
- write an Architecture Decision Record (ADR) for an engine decision;
- explain what evidence would change your decision;
- evaluate a new engine such as DataFusion, chDB, or cuDF quickly and systematically.

The goal is not to memorize a tool ranking. The goal is to build a repeatable engineering decision process.

---

## 2. Prerequisites

This chapter assumes you have completed Topics 01–07 of this module:

- Apache Arrow and columnar memory;
- Polars expressions;
- Polars lazy execution and query optimization;
- Polars streaming for larger-than-memory workloads;
- DuckDB in-process analytics;
- DuckDB querying of files/object storage;
- interoperability between pandas, Polars, DuckDB, and Arrow.

The purpose of this topic is different. Earlier topics taught you how the engines work. This topic turns that knowledge into engineering judgement.

---

## 3. The Central Idea: There Is No Universally Best Engine

A useful mental model is:

```text
No universally best analytical engine.

There is:
    best fit for this workload
```

A production decision should follow:

```text
Requirements
     ↓
Workload characteristics
     ↓
Candidate engines
     ↓
Correctness baseline
     ↓
Fair benchmark
     ↓
Operational evaluation
     ↓
Decision
     ↓
ADR
     ↓
Revisit conditions
```

This is different from:

```text
blog post
+
single benchmark
+
personal preference
=
architecture decision
```

A benchmark is evidence. It is not the entire architecture decision.

---

## 4. Why Engine Selection Is a Data Engineering Problem

Imagine a team needs to process analytical data every night. The workload has:

- a known row count and growth rate;
- a memory limit;
- a latency target;
- a preferred language or query interface;
- existing libraries;
- engineers who already know certain tools;
- a deployment environment;
- a reliability expectation.

The choice affects more than query speed.

It can affect:

- infrastructure cost;
- peak memory and failure risk;
- developer productivity;
- package size and startup time;
- test strategy;
- observability and debugging;
- deployment complexity;
- compatibility with downstream libraries;
- concurrency behaviour;
- upgrade and maintenance burden;
- the cost of future migration.

Senior engineering judgement therefore asks not only **"How fast is it?"** but also **"Does this architecture fit the constraints for the next operating horizon?"**

---

## 5. Start With the Workload, Not the Tool

Before comparing engines, describe the workload.

### 5.1 Data characteristics

Record:

- row count;
- column count;
- compressed size;
- approximate uncompressed size;
- likely working-set size;
- data types;
- null frequency;
- nested/list/struct usage;
- cardinality of key columns;
- number and size of files;
- partition layout.

### 5.2 Query characteristics

Record whether the workload contains:

- filters;
- projections;
- aggregations;
- joins;
- window functions;
- sorting;
- deduplication;
- reshaping/pivoting;
- time-series operations;
- SQL-heavy logic;
- Python-specific or library-specific logic.

### 5.3 Execution characteristics

Classify it as:

- interactive;
- batch;
- scheduled pipeline;
- ad-hoc analysis;
- streaming/incremental;
- local;
- object-storage based;
- database-backed;
- mixed.

### 5.4 Operational requirements

Record:

- SLA/SLO;
- concurrency;
- available CPU;
- available RAM;
- local disk capacity;
- temporary disk requirements;
- network characteristics;
- container limits;
- startup constraints;
- reproducibility requirements.

The workload description is the input to the architecture decision.

---

## 6. Workload Characterization Worksheet

Copy this template for each workload:

```text
WORKLOAD NAME
____________________________

Rows
____________________________

Columns
____________________________

Compressed Size
____________________________

Estimated Working Set
____________________________

Common Operations
____________________________

Query Style
SQL / DataFrame / Mixed

Execution Mode
Batch / Interactive / Streaming / Other

Data Location
Local / Object Storage / Database / Mixed

Memory Limit
____________________________

CPU / Cores
____________________________

Temporary Disk
____________________________

SLA / SLO
____________________________

Concurrency
____________________________

Output Size
____________________________

Expected Growth
____________________________

Critical Ecosystem Dependencies
____________________________

Primary Team Skills
____________________________

Deployment Target
____________________________
```

### Why each field matters

**Rows and columns** determine scale and shape. A million very wide rows can stress memory differently from ten million narrow rows.

**Compressed size** tells you about storage and transfer, but not the RAM required during execution.

**Working set** is the actively required data/state during computation. It can be much larger or much smaller than file size.

**Operations** matter because a scan/filter has different resource behaviour from a large join, global sort, or high-cardinality aggregation.

**Execution mode** affects whether interactive simplicity, throughput, bounded memory, or concurrency matters most.

**Deployment target** can change the true resource budget. A 64 GB laptop may run a workload that fails inside an 8 GB container.

---

## 7. The Four Tool Roles

The four technologies are related, but they are not the same category.

```text
Arrow
→ columnar in-memory representation + interoperability layer

pandas
→ Python DataFrame library with a broad ecosystem

Polars
→ expression-oriented DataFrame engine with parallel/lazy/streaming execution

DuckDB
→ embedded analytical database/query engine with SQL as a first-class interface
```

A useful architecture is:

```text
              Arrow
          ↙     ↓      ↘
      pandas  Polars  DuckDB
```

Arrow is not the query engine in this picture. It is a common representation/interchange foundation.

Apache Arrow describes itself as a columnar format and multi-language toolbox for fast data interchange and in-memory analytics.

---

## 8. pandas — Strengths and Limits

### Strengths

pandas is often a strong fit when the primary requirement is the Python DataFrame ecosystem.

Important strengths include:

- very broad library compatibility;
- familiarity across Python teams;
- large amount of existing code and documentation;
- easy integration with libraries whose public APIs expect pandas objects;
- strong support for exploratory analysis and many statistical workflows.

### Limits and trade-offs

pandas is not simply "slow." Its suitability depends on the workload.

Potential issues for larger or more demanding workloads include:

- memory pressure when the working set approaches available RAM;
- Python-level object representations for some data, especially older/object-heavy patterns;
- less natural fit for some larger analytical pipelines that benefit from lazy planning or streaming/out-of-core execution;
- ecosystem constraints when another engine would be a more natural expression/query layer.

The correct engineering question is:

> Does pandas meet this workload's data size, memory, performance, and ecosystem requirements with acceptable operational complexity?

---

## 9. Polars — Strengths and Limits

### Strengths

Polars provides an expression-oriented DataFrame model and supports lazy execution, parallel execution, and streaming execution. Current Polars documentation describes `LazyFrame.collect(..., engine="streaming")` as selecting the streaming engine; current APIs also expose batch-oriented execution such as `collect_batches()`.

Polars can be a natural fit when a workload benefits from:

- expression-based transformations;
- multi-threaded execution;
- lazy query planning;
- streaming for larger-than-memory workflows;
- columnar data and analytical processing.

### Limits and trade-offs

Potential trade-offs include:

- code and habits differ from pandas;
- not every pandas ecosystem dependency accepts Polars directly;
- a team may need time to learn expression-based thinking;
- APIs evolve, so versions should be pinned/tested and version-sensitive features verified;
- specialized operations or third-party libraries can still create pandas boundaries.

The correct question is not "Is Polars better than pandas?" It is:

> Does the workload benefit enough from Polars' execution model to justify its ecosystem and adoption trade-offs?

---

## 10. DuckDB — Strengths and Limits

DuckDB is an embedded analytical database/query engine. Its Python client exposes SQL execution and relational operations inside the Python process, and its relational API is lazily evaluated until an output operation executes.

### Strengths

- SQL is a first-class interface;
- analytical execution is central to the system design;
- direct file analytics work naturally for local analytical workflows;
- persistent local database files are supported;
- DataFrame and Arrow interoperability is built in;
- it can be embedded without running a separate database server.

### Limits and trade-offs

DuckDB is not a conventional OLTP server. A local analytical database is a different architecture from a highly concurrent application database.

Important constraints include:

- process/embedded deployment;
- concurrency characteristics that differ from client/server databases;
- single-node resource limits;
- the need to understand temporary disk and memory behaviour for larger queries;
- SQL dialect differences when DuckDB is used as a development/test double for another warehouse.

The appropriate question is:

> Is SQL-centric analytical execution inside a process or local analytical environment a good fit for this workload and its concurrency/deployment requirements?

---

## 11. Arrow — Role and Limits

Arrow is the interoperability foundation, not a universal DataFrame or database.

```text
Arrow
├── columnar in-memory representation
├── interoperability
└── foundation for analytics systems
```

Compare the roles:

| Technology | Primary role | Not primarily |
|---|---|---|
| Arrow | memory/interchange foundation | end-user query engine |
| pandas | Python DataFrame ecosystem | distributed query engine |
| Polars | DataFrame execution | shared transactional database |
| DuckDB | analytical DB/query engine | general OLTP server |

This distinction matters when designing architecture diagrams. Saying "we use Arrow" does not answer the question "which system executes the transformation?"

---

## 12. Decision Factor #1 — Dataset Size vs RAM

Always distinguish:

```text
total file size
≠
working-set size
≠
peak process memory
```

A 50 GB Parquet dataset does not imply 50 GB of RAM, nor does it imply that only 50 GB of RAM is required.

Peak memory depends on:

- compressed vs decompressed representation;
- selected columns;
- intermediate results;
- join state;
- aggregation state;
- sorting;
- temporary buffers;
- result materialization;
- parallelism.

### Practical classification

```text
Fits comfortably in RAM
    ↓
Eager/lazy single-node engines may be sufficient

Near RAM limit
    ↓
Memory-aware design and benchmarking become critical

Exceeds RAM
    ↓
Streaming/out-of-core execution may be required

State or throughput exceeds one machine
    ↓
Distributed/shared infrastructure may be relevant
```

Do not turn these into fixed size thresholds.

---

## 13. Decision Factor #2 — SQL vs DataFrame API

A workload may be naturally expressed as:

```sql
SELECT customer_id, SUM(amount)
FROM orders
WHERE order_date >= DATE '2026-01-01'
GROUP BY customer_id;
```

Or as a DataFrame expression pipeline.

Neither interface is universally superior.

### SQL-first characteristics

Often useful when:

- transformations are relational;
- SQL readability matters;
- analysts already work in SQL;
- query review and lineage are SQL-centric.

### DataFrame-first characteristics

Often useful when:

- transformations are naturally expressed as DataFrame expressions;
- Python composition is important;
- downstream APIs operate on DataFrames;
- the team already has strong DataFrame engineering practices.

### Hybrid

Many production systems are deliberately hybrid:

```text
DuckDB
  ↓ SQL-heavy step
Arrow
  ↓
Polars
  ↓ expression-heavy step
pandas
  ↓
pandas-only library
```

The question is why each boundary exists and what it costs.

---

## 14. Decision Factor #3 — Team Skills

Technology fit includes the human system around the technology.

Evaluate:

- SQL fluency;
- Python fluency;
- pandas familiarity;
- Polars expression knowledge;
- database/query-plan knowledge;
- ability to debug memory issues;
- deployment/operations experience;
- ability to maintain the tool after initial implementation.

A theoretically faster implementation can create more total engineering cost if only one person understands it or if every upgrade requires significant rework.

This does **not** mean always choosing the most familiar tool. It means explicitly accounting for training and maintenance effort.

---

## 15. Decision Factor #4 — Library Ecosystem

A pipeline may include:

- a scientific library expecting pandas;
- a visualization package with pandas input;
- a legacy internal package;
- a machine-learning library whose integration is easiest with pandas;
- a specialized extension that does not understand Polars.

A deliberate design can therefore be:

```text
Primary processing → Polars
                    ↓
              one pandas boundary
                    ↓
             specialized library
```

The architectural mistake is not using pandas. The mistake is crossing into pandas repeatedly without a reason.

---

## 16. Decision Factor #5 — Deployment Target

The same logical workload has different constraints in:

- a developer laptop;
- a VM;
- Docker;
- Kubernetes;
- CI;
- serverless;
- a managed warehouse.

Deployment changes the resource envelope.

```text
Host machine
64 GB RAM
     ↓
container limit
8 GB RAM
```

The engine decision must be made against the 8 GB runtime limit, not the 64 GB host.

Serverless adds startup concerns:

- package loading;
- process initialization;
- library import time;
- database startup;
- filesystem/network initialization.

A small batch workload may care more about startup and reproducibility than peak steady-state throughput.

---

## 17. Single-Node Architecture

A modern analytical node can contain:

```text
One machine
├── many CPU cores
├── substantial RAM
├── fast local SSD
└── high network bandwidth
```

Columnar engines can use this hardware effectively.

Therefore:

```text
single-node
≠
small data only
```

A single-node architecture can be appropriate for substantial workloads when the workload fits the machine's actual limits and SLA.

The opposite is also important:

```text
a larger machine
≠
unlimited scale
```

---

## 18. When One Machine Is Enough

A single machine may be enough when:

- the working set is manageable;
- operations fit the engine's memory/execution model;
- throughput meets the SLA;
- local/object-store I/O is acceptable;
- concurrency requirements are modest;
- operational simplicity is valuable.

The roadmap mentions that one machine can often handle workloads in the hundreds-of-GB range with efficient columnar engines. Treat this as a workload-dependent engineering range, not a hard boundary.

Do not write a rule such as:

> "Spark is required above 100 GB."

No universal threshold can replace measurement.

---

## 19. Single-Node Limits

Watch for these boundaries:

- RAM becomes the limiting resource;
- aggregation or join state grows too large;
- sorting becomes expensive;
- temporary storage becomes insufficient;
- network throughput is insufficient;
- runtime exceeds SLA;
- concurrency causes resource contention;
- recovery/fault-isolation requirements exceed what one process can provide.

A single-node decision should therefore include a **capacity envelope**, not just a current dataset size.

---

## 20. When Distributed Systems Become Relevant

Distributed systems can become relevant when the problem is no longer comfortably solvable within one machine's practical resource envelope or when organizational requirements demand shared infrastructure.

Examples include:

- multi-terabyte or much larger recurring transformations;
- very high parallel throughput requirements;
- many teams sharing the analytical workload;
- fault isolation and cluster scheduling requirements;
- concurrency that is not suited to an embedded local engine;
- managed warehouse requirements for governance, elasticity, or shared access.

This chapter only provides awareness of:

- Spark;
- Dask;
- Ray Data;
- cloud warehouses.

Their detailed implementation belongs to later topics.

---

## 21. Spark — Awareness Level

Apache Spark is a distributed data-processing ecosystem commonly used for large-scale Data Engineering workloads.

For this chapter, remember only the decision-level concepts:

- execution across multiple workers;
- cluster resource management;
- distributed memory/compute;
- large ecosystem;
- higher operational complexity than an embedded single-node library.

Do not learn Spark APIs here. Ask instead:

> Has the workload actually crossed the point where distributed execution solves a real constraint?

---

## 22. Dask — Awareness Level

Dask provides Python-oriented parallel/distributed execution and includes DataFrame-style computation.

Relevant decision questions are:

- Does the workload fit Dask's execution model?
- Does the team already operate Python distributed workloads?
- Does the additional system complexity solve a real constraint?

No universal ranking against pandas/Polars/DuckDB belongs here.

---

## 23. Ray Data — Awareness Level

Ray Data is part of the broader Ray ecosystem and is relevant when distributed data processing is connected to Python-centric distributed workloads.

At this stage, focus on architectural fit:

- distributed execution;
- integration with a wider Ray application;
- workload partitioning;
- operational complexity.

Detailed Ray APIs belong elsewhere.

---

## 24. Cloud Warehouses — Awareness Level

A managed warehouse may be appropriate when requirements include:

- many concurrent users;
- central shared access;
- governance and managed operations;
- elastic compute;
- organizational SQL workflows;
- centralized analytical platform ownership.

The choice is not "warehouse good, embedded engine bad." It is a question of deployment architecture and requirements.

---

## 25. Operational Factor — Container Memory Limits

The true memory budget is:

```text
available runtime memory
=
what the process is actually allowed to use
```

This may be lower than host RAM because of:

- Docker memory limits;
- Kubernetes resource limits;
- CI worker limits;
- serverless memory settings.

A benchmark should therefore record both the host configuration and the runtime limit.

---

## 26. Operational Factor — Serverless Cold Starts

For a serverless workload, evaluate:

```text
cold start
+
initialization
+
query execution
+
output
```

rather than only steady-state query time.

A workload that runs every few hours may spend a meaningful portion of its lifecycle initializing dependencies.

Do not assume one engine always has the lowest startup cost. Measure the actual deployment package and runtime.

---

## 27. Operational Factor — DuckDB Concurrency

DuckDB's embedded architecture is valuable for local analytics, but concurrency requirements must be checked explicitly.

A useful conceptual model is:

```text
many readers
      ↓
local DuckDB database
      ↑
constrained concurrent writing model
```

If the architecture requires a conventional multi-writer transactional application backend, an embedded analytical engine is solving the wrong class of problem.

Do not call DuckDB "bad". Describe the workload mismatch.

---

## 28. Operational Factor — Reproducibility

An engine choice should be reproducible.

Record:

```text
Python version
pandas version
Polars version
DuckDB version
PyArrow version
OS
CPU
RAM
Disk
Dataset version/checksum
Thread settings
Cache assumptions
Query definitions
```

Why?

Because a future engineer must be able to reproduce the benchmark and understand why a previous decision was made.

---

## 29. Operational Factor — Upgrade Churn

Fast-moving libraries can introduce:

- API changes;
- performance changes;
- behaviour changes;
- compatibility changes;
- new capabilities that change optimization opportunities.

The architecture decision should therefore include:

- version pinning policy;
- compatibility tests;
- upgrade cadence;
- release monitoring;
- rollback plan.

A benchmark performed once is not enough if production upgrades happen every few months.

---

## 30. Performance Starts With a Fair Benchmark

Benchmark the **workload**, not the library in isolation.

A valid comparison should keep the important variables constant:

```text
same dataset
+
same file format
+
same business semantics
+
same hardware
+
same environment
+
same correctness criteria
```

Then measure:

```text
runtime
peak memory
correctness
```

and, where relevant:

```text
bytes read
output size
conversion cost
```

---

## 31. What Makes a Benchmark Unfair?

Avoid comparisons such as:

```text
Engine A → CSV
Engine B → Parquet
```

or:

```text
Engine A → warmed cache
Engine B → cold cache
```

or:

```text
Engine A → filtered query
Engine B → SELECT *
```

These are not engine comparisons. They are comparisons of different workloads.

Also avoid measuring load/setup for one system while excluding it for another unless you clearly define why the measurement boundary differs.

---

## 32. Cold vs Warm Cache

### Cold cache

The relevant data and metadata are not already cached by the environment.

### Warm cache

Some data or metadata is already present in one or more caches.

Potential caches include:

- operating-system page cache;
- local filesystem caches;
- object-storage/client caches where present;
- database or engine-level internal caches.

Therefore:

```text
Run 1 may not equal Run 2
```

A fair report records cache conditions rather than hiding them.

---

## 33. Repeated Runs

For meaningful measurements, run the same benchmark repeatedly.

At minimum:

```text
3 repetitions
```

The roadmap's benchmark exercise also requires three data sizes and cold/warm conditions.

Report a summary such as:

```text
median runtime
mean runtime
range or dispersion
peak memory
```

Use medians or another robust statistic when outliers make a mean misleading.

Do not turn this into a statistics course. The goal is simply to avoid treating one noisy number as a law.

---

## 34. Memory Measurement

Runtime alone is insufficient.

A query that takes 20 seconds and uses 3 GB may be operationally viable, while a query that takes 10 seconds and briefly consumes 20 GB may fail in production.

On Linux, one practical process-level measurement is:

```bash
/usr/bin/time -v python benchmark.py
```

Look for:

- elapsed time;
- maximum resident set size (Max RSS);
- exit status.

Important limitation:

> OS-level process memory is not identical to every Python allocator or library-level memory metric.

The benchmark report should label the measurement method.

---

## 35. I/O Measurement

For file-based workloads, also consider:

- bytes read;
- files touched;
- partitions touched;
- output size.

For remote object storage, request count and network transfer can matter as much as local CPU time.

Do not assume every engine exposes identical I/O telemetry. Document how the number was measured.

---

## 36. Avoid Vendor-Marketing Benchmarks

When reading an external benchmark, ask:

1. Was the workload realistic?
2. Was the same file format used?
3. Were the queries semantically identical?
4. Was loading included consistently?
5. Were thread counts equivalent?
6. Was the data already cached?
7. Were failures omitted?
8. Was peak memory reported?
9. Can I reproduce the test?
10. Does the query resemble my production workload?

A vendor benchmark can be useful evidence. It should not be the only evidence.

---

## 37. TPC-H-Style Benchmark Ideas

TPC-H-style queries are useful because they represent analytical patterns such as:

- joins;
- filters;
- grouped aggregation;
- subqueries;
- ordering;
- complex relational logic.

Standardized benchmark ideas improve repeatability.

But they do not model every production workload.

Your production workload may contain:

- unusual nested types;
- object-storage layout constraints;
- custom Python logic;
- specific joins;
- highly selective filters;
- time-series operations;
- library-specific boundaries.

Therefore:

> TPC-H-style tests are useful for reference. Your own workload matters more for your architecture decision.

---

## 38. Benchmark the Workload, Not the Library

Compare these two workloads conceptually:

```text
Workload A
5 GB CSV
→ type cleanup
→ validation
→ Parquet output
```

and:

```text
Workload B
200 GB Parquet
→ multiple joins
→ window functions
→ aggregation
→ partitioned output
```

They measure different things.

The first may emphasize:

- startup;
- CSV parsing;
- schema handling;
- simple transformation;
- output writing.

The second may emphasize:

- query optimization;
- memory management;
- parallelism;
- join implementation;
- window execution;
- file pruning.

A single benchmark cannot answer both.

---

## 39. Benchmark Dimensions

| Dimension | What to measure | Why it matters |
|---|---|---|
| Speed | wall time | latency/throughput |
| Memory | peak RAM | failure risk and node sizing |
| I/O | bytes/files touched | storage and network efficiency |
| Scale | largest successful size | practical capacity |
| Operations | query coverage | feature fit |
| Development | code complexity | maintainability |
| Deployment | startup/resource needs | operational fit |
| Reliability | repeatability/failures | production risk |
| Compatibility | ecosystem support | integration cost |
| Maintenance | upgrades/ownership | total engineering cost |

Do not convert this table into a universal numerical score.

---

## 40. Five Required Workload Decisions

Use these roadmap scenarios as decision exercises.

### Workload A — Nightly Cleanup

```text
5 GB CSV
→ cleanup
→ Parquet
2 GB container
```

Reason about:

- memory headroom;
- startup/deployment;
- CSV parsing;
- output throughput;
- simplicity.

### Workload B — Analyst SQL

```text
200 GB lake Parquet
→ ad-hoc SQL
```

Reason about:

- SQL-first development;
- file layout;
- selective reads;
- interactive latency;
- local versus shared access.

### Workload C — ML Feature Preparation

```text
DataFrame transformations
+
scikit-learn
```

Reason about:

- DataFrame ergonomics;
- ecosystem boundaries;
- conversion cost;
- correctness;
- feature engineering operations.

### Workload D — Large-Scale Shared Processing

```text
5 TB daily joins across teams
```

Reason about:

- single-node capacity;
- shared concurrency;
- distributed processing;
- scheduling;
- operational ownership.

### Workload E — Warehouse SQL Testing

```text
local unit/integration environment
for analytical SQL
```

Reason about:

- reproducibility;
- startup;
- dialect compatibility;
- local data fixtures;
- remote warehouse dependency.

### Workload F — Your Own Hybrid Workload

Add one workload from your target career/project environment and characterize it using the worksheet.

For every workload, do not ask "Who wins?" Ask:

```text
What are the requirements?
What are the candidate architectures?
What must be measured?
What operational risks exist?
What evidence would change the decision?
```

---

## 41. Challenge Your Initial Decision

For every proposed architecture, ask:

> What measurable condition would cause me to change my decision?

Examples:

```text
Data grows from 5 GB → 100 GB
RAM limit falls from 16 GB → 4 GB
Concurrency rises from 1 → 30 users
SQL complexity doubles
A required library becomes pandas-only
Object storage replaces local SSD
SLA tightens from 10 minutes → 60 seconds
```

This is more mature than defending a tool forever.

---

## 42. Engine Mixing — Deliberate, Not Accidental

One pipeline may legitimately use multiple engines.

Example:

```text
Object storage / Parquet
        ↓
      DuckDB
        ↓ SQL filtering + aggregation
       Arrow
        ↓
      Polars
        ↓ expression-heavy transformation
      pandas
        ↓ pandas-only dependency
```

The design principle is:

> Each boundary should have a technical or business reason.

---

## 43. When Mixing Engines Makes Sense

Use SQL-heavy work in DuckDB when SQL is the natural abstraction.

Use complex expression-oriented DataFrame transformations in Polars when that is the natural representation.

Use pandas near the edge when a downstream library requires it.

Use Arrow as the interchange boundary where its representation matches the data and minimizes unnecessary movement.

Avoid turning engine mixing into a religion. A hybrid pipeline is useful only when the benefits exceed the conversion and operational complexity.

---

## 44. Engine-Mixing Anti-Pattern

A suspicious pipeline is:

```text
DuckDB
 ↓
pandas
 ↓
Polars
 ↓
pandas
 ↓
DuckDB
```

Potential costs include:

- repeated allocations;
- data copies;
- type conversion;
- serialization or reconstruction;
- higher peak memory;
- harder debugging;
- more version coupling.

The right response is not "never use multiple engines." The right response is:

> Identify why each boundary exists and remove boundaries that have no meaningful purpose.

---

## 45. Minimize Boundary Count

A practical engineering pattern is:

```text
choose a primary engine for the main workload
                 ↓
cross boundaries at meaningful integration points
```

Examples:

```text
SQL-heavy workload
→ stay in DuckDB longer

Expression-heavy workload
→ stay in Polars longer

pandas-only consumer
→ convert once near the edge
```

This connects directly to Topic 07: fewer data movements usually mean fewer opportunities for expensive conversion.

---

## 46. Arrow as Glue

A common architecture is:

```text
DuckDB
   ↓
Arrow
   ↓
Polars
```

or:

```text
Polars
   ↓
Arrow
   ↓
pandas
```

Arrow provides a common columnar representation and interchange mechanism. That can reduce the need for every pair of libraries to maintain independent, bespoke conversion layers.

However:

```text
Arrow boundary
≠
automatic zero-copy
```

Type compatibility, chunking, null semantics, timestamps, and destination representation still matter.

---

## 47. Correctness Reference Implementation

Before benchmarking, create a trusted small-data correctness reference.

A simple approach is:

```text
small deterministic input
        ↓
reference result
        ↓
compare other implementations
```

pandas can be a useful reference when it is the simplest trusted implementation, but it is not automatically the correct reference for every workload.

A reference should define:

- expected schema;
- expected row count;
- expected aggregates;
- null behaviour;
- timestamp semantics;
- output ordering rules.

Correctness comes before performance interpretation.

---

## 48. Cross-Engine Reconciliation

For each implementation, validate:

```text
row count
column names
schema
null counts
aggregates
representative values
timestamps
```

When row order is not semantically meaningful, sort both outputs by a deterministic key before comparing.

A benchmark with unequal results is not a valid performance comparison.

---

## 49. Benchmark Contamination

Watch for:

- OS page cache;
- engine cache;
- object-storage cache;
- different thread counts;
- different file layouts;
- different compression;
- different filtering;
- different output handling;
- measuring conversion for one engine but not another.

Document what you controlled and what you could not control.

The objective is not to pretend the environment is perfectly clean. The objective is to make the test conditions explicit.

---

## 50. Statistical Discipline for Benchmarking

Benchmark results vary because of:

- background processes;
- storage latency;
- cache state;
- scheduling;
- garbage collection or memory reclamation;
- network variability.

Use repeated runs and report a robust summary.

Do not make claims like:

> "Engine A is exactly 18.3% faster forever."

Instead say:

> "Under this documented environment, dataset, cache condition, and query, the measured distribution of runtimes was ..."

The benchmark should teach a repeatable method, not a marketing conclusion.

---

## 51. Cost Thinking

Engineering cost is broader than CPU time.

Conceptual cost drivers include:

```text
CPU
+
RAM
+
storage
+
network
+
cloud execution
+
engineering time
+
maintenance
+
operational complexity
```

A faster engine may cost more if it requires a larger node, more memory headroom, or a more complicated deployment.

Do not fabricate cloud prices. Measure the actual platform and contract context when financial modelling is required.

---

## 52. SLA and SLO Thinking

Keep the definitions simple:

- **SLA:** a service commitment, often contractual;
- **SLO:** an internal target used to manage service performance/reliability.

Example:

```text
Batch target
10 minutes
```

versus:

```text
Interactive target
60 seconds
```

The tighter target may justify a different architecture because latency becomes a stronger constraint.

But do not infer the engine from the target alone. Measure the workload.

---

## 53. Interactive vs Batch

### Interactive analytics

Often values:

- fast feedback;
- query readability;
- easy ad-hoc iteration;
- predictable local execution.

### Scheduled batch

Often values:

- throughput;
- repeatability;
- automation;
- resource isolation;
- deterministic output.

### CI

Often values:

- startup time;
- reproducibility;
- deterministic fixtures;
- low operational dependencies.

The same engine can appear in several modes, but the evaluation criteria change.

---

## 54. Data Location as a Decision Factor

Characterize the source as:

- local SSD;
- network filesystem;
- object storage;
- database;
- lakehouse table;
- mixed.

A local query may be CPU-bound while the same logical query against remote object storage becomes network/request-latency bound.

This is why Topic 06 matters to engine selection.

---

## 55. Data Format as a Decision Factor

Compare workload formats:

| Format | Typical engineering concern |
|---|---|
| CSV | parsing, weak typing, schema inference |
| Parquet | columnar scan, pruning, metadata |
| JSON | semi-structured parsing |
| Arrow | in-memory interchange |
| Database table | server/connection semantics |

When benchmarking engines, use the same format unless format conversion is intentionally part of the workload.

---

## 56. Maintainability as a Decision Factor

Evaluate:

- readability;
- code size;
- abstraction complexity;
- testing difficulty;
- debugging difficulty;
- onboarding time;
- documentation quality;
- release cadence;
- ownership model.

Two implementations with similar runtime can have very different long-term maintenance costs.

---

## 57. Architecture Escalation Path

Use this as a decision aid, not a threshold table:

```text
Simple workload
     ↓
pandas / Polars / DuckDB
     ↓
Streaming / out-of-core if needed
     ↓
Larger single node if justified
     ↓
Distributed engine / warehouse when one node no longer meets requirements
```

The correct move may remain at an earlier stage indefinitely if the workload fits comfortably.

---

## 58. Avoid Premature Distribution

Do not choose a distributed platform merely because the dataset "sounds large."

A distributed platform adds:

- more infrastructure;
- more failure modes;
- scheduling/resource-management complexity;
- deployment and observability requirements.

If a workload fits comfortably on one machine, a simpler single-node architecture may be easier to operate.

But the opposite mistake is also dangerous:

> Do not force a single-node architecture past its observed practical capacity.

Both decisions require evidence.

---

## 59. New-Engine Evaluation Framework

When a new engine appears, do not ask:

> Is it the next big thing?

Ask:

1. What workload does it target?
2. What execution model does it use?
3. What data formats does it support?
4. What is its memory model?
5. Is execution lazy?
6. Is execution streaming/out-of-core?
7. Is it CPU, GPU, distributed, or embedded?
8. What is the interoperability story?
9. What ecosystem/support model exists?
10. Can I reproduce performance on my workload?

Then run a small **evaluation spike** using one representative query before committing.

---

## 60. DataFusion — Awareness

Apache DataFusion is an extensible query engine written in Rust and using Apache Arrow as its in-memory format. Its documentation describes SQL and DataFrame APIs, columnar/vectorized/multithreaded/streaming execution, and extensibility for data-centric systems.

For this module, remember only:

```text
DataFusion
→ extensible Arrow-oriented query engine
→ useful as a building block for data systems
```

Do not learn DataFusion APIs here. Use the evaluation framework instead.

---

## 61. chDB — Awareness

chDB is an in-process analytical SQL engine based on ClickHouse for Python. It is relevant as another embedded analytical approach. Current ClickHouse documentation describes it as an in-process SQL OLAP engine for Python that can query local files and other sources without a separate server process.

Evaluate it using the same questions:

- target workload;
- execution model;
- file support;
- memory behaviour;
- ecosystem;
- deployment;
- reproducible benchmark.

Do not treat the existence of another engine as evidence that your current architecture is wrong.

---

## 62. cuDF — Awareness

cuDF is a GPU DataFrame library in the RAPIDS ecosystem. Current documentation describes it as a Python GPU DataFrame library for loading, joining, aggregating, filtering, and transforming data, with pandas-like workflows.

For this chapter:

```text
cuDF
→ GPU-oriented DataFrame computation
```

The important decision distinction is:

```text
CPU streaming
vs
GPU acceleration
vs
distributed execution
```

They address different constraints.

A GPU may help a compute-heavy workload whose operators map well to GPU execution. It does not automatically solve:

- insufficient host RAM;
- huge remote data transfer;
- poor file layout;
- distributed concurrency requirements.

Do not teach CUDA programming here.

---

## 63. CPU vs GPU vs Distributed Decision Matrix

| Constraint | Architecture hypothesis |
|---|---|
| Fits in RAM, local workload | single-node engine |
| Larger than RAM | streaming/out-of-core design |
| CPU-heavy parallel workload | multi-threaded CPU engine |
| GPU-suitable computation | GPU engine |
| Workload exceeds one machine | distributed architecture |
| Many shared analytical users | managed/shared warehouse or server architecture |

These are hypotheses. Validate them experimentally.

---

## 64. Future Growth

A decision should reflect an operating horizon.

Ask:

- Will data double?
- Will query complexity increase?
- Will concurrency increase?
- Will data move to object storage?
- Will the SLA tighten?
- Will the team grow?
- Will the platform become shared?

Do not over-engineer for hypothetical scale. Document what growth is expected and what condition will trigger re-evaluation.

---

## 65. Required Production Decision Workflow

Use this repeatedly:

```text
1. Define workload
       ↓
2. Define requirements
       ↓
3. Select candidate engines
       ↓
4. Build correctness reference
       ↓
5. Build representative benchmark
       ↓
6. Measure time + memory + I/O
       ↓
7. Evaluate deployment/operations
       ↓
8. Evaluate maintainability/ecosystem
       ↓
9. Decide
       ↓
10. Write ADR
       ↓
11. Define revisit conditions
```

The workflow should produce an explainable decision, not merely a tool name.

---

## 66. Architecture Decision Record (ADR)

An **Architecture Decision Record** captures why an important technical decision was made.

A useful ADR structure is:

1. Context
2. Problem
3. Requirements
4. Options
5. Measurements/evidence
6. Decision
7. Consequences
8. Risks
9. Revisit conditions

The ADR is valuable because future engineers will otherwise see the current tool without seeing the reasoning behind it.

### Fill-in ADR template

A reusable template that follows the nine headings above. The bracketed text is a placeholder; do not pre-fill a winning engine or copy numbers from anywhere else.

````markdown
# ADR — [Decision Title]

## 1. Context

[Describe the workload, users, deployment environment, data scale, and constraints.]

## 2. Problem

[State the engineering problem this decision must solve.]

## 3. Requirements

- [Functional requirement]
- [Performance/SLA requirement]
- [Memory/deployment requirement]
- [Correctness requirement]
- [Operational requirement]
- [Team/ecosystem requirement]

## 4. Options

| Option | Description | Relevant strengths | Relevant limitations |
|---|---|---|---|
| Option A | | | |
| Option B | | | |
| Option C | | | |
| Hybrid | | | |

## 5. Measurements / Evidence

[Document dataset, queries, versions, hardware, cache condition, repetitions, runtime, peak memory, I/O where relevant, and correctness.]

| Engine | Query | Size | Cache | Run | Runtime | Peak Memory | Correct? |
|---|---|---|---|---:|---:|---:|---|
| | | | | | | | |

## 6. Decision

[State the conditional decision based on the requirements and measured evidence.]

## 7. Consequences

### Benefits
- [Benefit]

### Costs / Trade-offs
- [Cost]

## 8. Risks

- [Risk]
- [Mitigation]

## 9. Revisit Conditions

- [Observable trigger]
- [Observable trigger]
````

---

## 67. ADR Context

Example context:

```text
The team runs daily analytical transformations over 50 GB of Parquet.
The workload runs in a 16 GB container.
Most transformations are relational, with several joins and aggregations.
The team is strong in SQL and Python.
The output is written to Parquet for downstream consumption.
```

A strong context describes the workload and constraints without pre-judging the answer.

---

## 68. ADR Options

List realistic alternatives:

```text
Option A — pandas
Option B — Polars
Option C — DuckDB
Option D — hybrid DuckDB + Polars
Option E — distributed architecture
```

Do not include an option just to create a long list. Include options that could reasonably satisfy the requirements.

---

## 69. ADR Measurements

Document the benchmark evidence:

```text
Dataset:
50 GB Parquet

Representative queries:
6

Data sizes:
small / RAM-scale / larger-than-RAM

Cache conditions:
cold / warm

Measurements:
runtime / peak memory / correctness / I/O where relevant
```

Never insert invented values.

---

## 70. ADR Decision

The decision should be written as a conditional engineering statement.

For example:

```text
Based on the measured workload and operational constraints,
we select __________________ for the default single-node pipeline
because __________________.
```

Then point to the specific evidence.

Avoid:

```text
Tool X is the best.
```

That sentence contains no workload, requirement, or evidence.

---

## 71. ADR Consequences

Document both benefits and costs.

Examples:

```text
Benefits
- simpler deployment
- SQL readability
- lower measured peak memory

Costs
- warehouse SQL dialect differences
- reduced compatibility with pandas-only libraries
- migration effort for existing code
```

A good architecture decision says what you are giving up as well as what you gain.

---

## 72. ADR Revisit Conditions

Write observable triggers rather than arbitrary thresholds.

Examples:

```text
Revisit if:
- peak memory approaches the measured container limit;
- workload no longer completes inside the documented SLA;
- concurrency requirements increase materially;
- required libraries are no longer compatible;
- data scale exceeds the tested capacity envelope;
- object-storage/network costs become dominant;
- upgrades create unacceptable compatibility churn.
```

---

## 73. Required Engine Benchmark Exercise (`engine_benchmark/`)

> **Important:** this section specifies the exercise. It does not create the benchmark directory, scripts, datasets, plots, or ADR file.

### Step 1 — Define six representative queries

Use:

1. filter + aggregate;
2. top-N per group;
3. large join;
4. window calculation;
5. deduplication;
6. time-series resampling/aggregation.

### Step 2 — Implement each query in

- pandas;
- Polars lazy/streaming where appropriate;
- DuckDB.

### Step 3 — Validate correctness

Use a small reference dataset first.

### Step 4 — Run three data sizes

```text
small
≈ RAM-scale
larger-than-RAM
```

The exact data size must be based on the actual machine.

### Step 5 — Run cold and warm conditions

Document what cold and warm mean in the environment.

### Step 6 — Perform three repetitions

Record each run, not just the final summary.

### Step 7 — Measure

At minimum:

- wall time;
- peak process memory;
- correctness.

Where relevant:

- bytes read;
- output size;
- conversion time.

### Step 8 — Tabulate or plot results

Use actual measurements.

### Step 9 — Write the two-page ADR

The ADR must select a default single-node approach for the hypothetical team based on the measured evidence and requirements.

### Step 10 — Define the distributed boundary

Describe the observed conditions that would cause you to revisit the single-node architecture.

### Embedded Reference Benchmark Harness

This is a reference implementation embedded in the chapter. Save it as your own benchmark script when you do the exercise; the chapter does not create the file, the results CSV, or an `engine_benchmark/` directory. It implements one of the six queries (Query 1, filter + aggregate) in pandas, Polars (lazy) and DuckDB, plus the harness around it. It was run on pandas 3.0, Polars 1.44 and DuckDB 1.5.6; the other five queries are still yours to implement from the specifications below.

How it works:

```text
generate deterministic data → build trusted expected result → run pandas / Polars / DuckDB
→ validate logical equality → measure runtime + peak RSS → repeat → write CSV
```

- **Correctness first.** Each engine's result is normalised (same column names, sorted by `customer_id`) and compared with a pandas reference. A run that disagrees is recorded with `correct = False` and the script prints a warning: do not use its timing.
- **Timing.** `measure()` times only the query call. Data generation, the reference computation, setup and CSV writing are outside the timing. `BENCH_RUNS` sets the number of repetitions, and every run is a CSV row.
- **Peak memory.** `resource.getrusage(...).ru_maxrss` is process-level. On Linux it is in KiB, so it is converted to MB (it is bytes on macOS). It is a monotonic peak for the whole process: it includes data generation and setup, imports, and native allocations that Python tools do not see, so `rss_increase_mb` is only the observed rise of that peak during one run and can be 0 when an earlier step had a higher peak. To keep each measurement separate, every engine, size and cache combination runs in its own fresh worker process. Validate with `/usr/bin/time -v` as well.
- **Three data-size slots.** `small`, `ram-scale` and `larger-than-RAM` are benchmark slots, not promises. Set `BENCH_SMALL_ROWS`, `BENCH_RAM_ROWS` and `BENCH_LARGE_ROWS` from your machine's memory and the physical size of the generated data; the defaults do not necessarily match your RAM. This harness holds the data in memory, so for a truly larger-than-RAM slot use the file-based, streaming approaches from Topics 04 and 06 instead.
- **Cold and warm.** The `cache` column records the condition. `cold` is a fresh worker process with no warm-up run; `warm` runs one unrecorded warm-up first. The script does not, and cannot portably, flush the OS page cache or storage caches. A controlled cold-cache measurement is environment-specific, so document what cold means on your machine.

```python
"""Reference benchmark harness: query 1 (filter + aggregate) in pandas, Polars and DuckDB.

Each (engine, size, cache) combination runs in a fresh worker process so that the
process peak RSS belongs to that combination. Results are written to
engine_benchmark_results.csv when you run this script.
"""

from __future__ import annotations

import csv
import gc
import json
import os
import platform
import resource
import statistics
import subprocess
import sys
import time
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import polars as pl

# Benchmark slots, not machine-specific promises: set the row counts from your
# machine's RAM and the physical size of the generated data.
SIZES = {
    "small": int(os.getenv("BENCH_SMALL_ROWS", "100_000")),
    "ram-scale": int(os.getenv("BENCH_RAM_ROWS", "1_000_000")),
    "larger-than-RAM": int(os.getenv("BENCH_LARGE_ROWS", "5_000_000")),
}
RUNS = int(os.getenv("BENCH_RUNS", "3"))
CACHES = ("cold", "warm")
ENGINES = ("pandas", "polars", "duckdb")
QUERY = "filter_aggregate"
OUTPUT = Path("engine_benchmark_results.csv")
FIELDS = [
    "engine", "query", "data_size", "rows", "cache", "run", "runtime_seconds",
    "peak_rss_mb", "rss_increase_mb", "correct", "notes",
    "python_version", "pandas_version", "polars_version", "duckdb_version",
]


# --- data (never part of a timing) ---------------------------------------------------
def generate_orders(rows: int) -> pd.DataFrame:
    """Deterministic orders: same rows on every run and every machine."""
    ids = np.arange(rows, dtype=np.int64)
    return pd.DataFrame(
        {
            "order_id": ids,
            "customer_id": ids % 10_000,
            "status": np.where((ids * 7) % 10 < 6, "PAID", "PENDING"),
            "amount": ((ids % 500) + 1) * 0.25,
        }
    )


# --- the same query in three engines ------------------------------------------------
# SELECT customer_id, SUM(amount) AS revenue FROM orders
# WHERE status = 'PAID' GROUP BY customer_id
def query_pandas(pdf: pd.DataFrame) -> pd.DataFrame:
    paid = pdf.loc[pdf["status"] == "PAID"]
    return paid.groupby("customer_id", as_index=False)["amount"].sum().rename(columns={"amount": "revenue"})


def query_polars(pldf: pl.DataFrame) -> pl.DataFrame:
    return (
        pldf.lazy()
        .filter(pl.col("status") == "PAID")
        .group_by("customer_id")
        .agg(pl.col("amount").sum().alias("revenue"))
        .collect()
    )


def query_duckdb(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    return con.execute(
        """
        SELECT customer_id, SUM(amount) AS revenue
        FROM orders
        WHERE status = 'PAID'
        GROUP BY customer_id
        """
    ).df()


def normalise(result) -> pd.DataFrame:
    """Same column names, sorted rows, plain pandas, so results can be compared."""
    frame = result.to_pandas() if isinstance(result, pl.DataFrame) else result
    return frame[["customer_id", "revenue"]].sort_values("customer_id").reset_index(drop=True)


def is_correct(expected: pd.DataFrame, actual) -> bool:
    got = normalise(actual)
    return (
        len(got) == len(expected)
        and (got["customer_id"].to_numpy() == expected["customer_id"].to_numpy()).all()
        and np.allclose(got["revenue"].to_numpy(dtype=float), expected["revenue"].to_numpy(dtype=float), rtol=1e-9)
    )


# --- measurement helpers ---------------------------------------------------------------
def measure(fn):
    start = time.perf_counter()
    result = fn()
    return result, time.perf_counter() - start


def peak_rss_mb() -> float:
    """Process peak resident set size so far, in MB.

    On Linux ru_maxrss is reported in KiB (on macOS it is bytes), so it is divided
    by 1024 here. It is a process-wide, monotonic peak: it includes memory from data
    generation and other engines' setup, and it does not separate Python, native and
    allocator memory. Use /usr/bin/time -v for an independent process-level check.
    """
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return peak / 1024.0 if platform.system() == "Linux" else peak / (1024.0 * 1024.0)


# --- worker: one engine, one size, one cache condition -------------------------------
def worker(engine: str, size: str, cache: str) -> list[dict]:
    rows = SIZES[size]
    pdf = generate_orders(rows)
    expected = normalise(query_pandas(pdf))  # trusted reference, not timed or recorded

    if engine == "pandas":
        fn = lambda: query_pandas(pdf)  # noqa: E731
    elif engine == "polars":
        pldf = pl.from_pandas(pdf)  # setup, not timed
        fn = lambda: query_polars(pldf)  # noqa: E731
    else:
        con = duckdb.connect()  # in-memory
        con.register("orders", pdf)
        fn = lambda: query_duckdb(con)  # noqa: E731

    try:
        if cache == "warm":
            fn()  # unrecorded warm-up so caches are populated
        gc.collect()
        results = []
        for run in range(1, RUNS + 1):
            before = peak_rss_mb()
            result, seconds = measure(fn)
            after = peak_rss_mb()
            results.append(
                {
                    "engine": engine, "query": QUERY, "data_size": size, "rows": rows,
                    "cache": cache, "run": run, "runtime_seconds": f"{seconds:.6f}",
                    "peak_rss_mb": f"{after:.1f}",
                    "rss_increase_mb": f"{after - before:.1f}",  # observed rise of the process peak
                    "correct": is_correct(expected, result),
                    "notes": "cold = fresh process, no warm-up (OS page cache not reset)"
                    if cache == "cold" else "warm = one unrecorded warm-up run first",
                    "python_version": platform.python_version(),
                    "pandas_version": pd.__version__,
                    "polars_version": pl.__version__,
                    "duckdb_version": duckdb.__version__,
                }
            )
        return results
    finally:
        if engine == "duckdb":
            con.close()


# --- orchestrator ---------------------------------------------------------------------
def write_results(rows: list[dict]) -> None:
    with OUTPUT.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()  # header written once
        writer.writerows(rows)


def main() -> None:
    if len(sys.argv) == 5 and sys.argv[1] == "--worker":
        print(json.dumps(worker(sys.argv[2], sys.argv[3], sys.argv[4])))
        return

    all_rows: list[dict] = []
    for size in SIZES:
        for cache in CACHES:
            for engine in ENGINES:
                done = subprocess.run(
                    [sys.executable, __file__, "--worker", engine, size, cache],
                    capture_output=True, text=True, check=True,
                )
                all_rows.extend(json.loads(done.stdout.strip().splitlines()[-1]))
    write_results(all_rows)

    wrong = [r for r in all_rows if not r["correct"]]
    if wrong:
        print(f"INVALID: {len(wrong)} runs disagree with the reference; do not use their timings.")
    for r in all_rows:
        print(r["data_size"], r["cache"], r["engine"], r["run"], r["runtime_seconds"], "s",
              r["peak_rss_mb"], "MB", "correct" if r["correct"] else "WRONG")
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
```

Run it with `python engine_benchmark.py`. It writes `engine_benchmark_results.csv` with the columns `engine, query, data_size, rows, cache, run, runtime_seconds, peak_rss_mb, rss_increase_mb, correct, notes` and the library versions. All values are measured when you run it; none are included here.

---

## 74. Six Required Benchmark Query Specifications

### Query 1 — Filter + Aggregate

Conceptual SQL:

```sql
SELECT customer_id, SUM(amount) AS revenue
FROM orders
WHERE status = 'PAID'
GROUP BY customer_id;
```

DataFrame versions should implement identical semantics.

Measure how runtime and memory change as rows increase.

### Query 2 — Top-N Per Group

Use a deterministic ranking/window pattern such as:

```text
partition by customer/region
order by revenue descending
keep top N
```

Validate ties and deterministic semantics.

### Query 3 — Large Join

Join a large fact relation with a second relation.

Record:

- key cardinality;
- join output size;
- memory;
- runtime.

### Query 4 — Window Function

Examples:

- running total;
- lag/lead;
- partitioned ranking.

Ensure the reference implementation uses exactly the same ordering semantics.

### Query 5 — Deduplication

Use a business key plus timestamp/version.

Document which record wins and how ties are resolved.

### Query 6 — Time-Series Aggregation

Use a documented time window and aggregation.

Avoid silently changing time-zone semantics across engines.

---

## 75. Three Data Sizes

### Small

Fits comfortably in RAM and is used primarily for correctness.

### RAM-scale

Approximately comparable to available memory and used to expose resource pressure.

### Larger-than-RAM

Exceeds available RAM and tests streaming/out-of-core capability.

Document the actual machine before selecting the data sizes.

The goal is not to force a failure. The goal is to observe where the workload transitions from comfortable to constrained.

---

## 76. Benchmark Result Table

Use this structure and fill it with real values:

```markdown
| Engine | Query | Data Size | Cache | Run | Runtime (s) | Peak Memory (MB) | Correct? |
|---|---|---|---|---:|---:|---:|---|
| | | | | | | | |
```

For file-based workloads, add:

```text
Files touched
Bytes read
Output size
```

Never pre-fill this with fabricated results.

---

## 77. Benchmark Interpretation Framework

Use these cases to practice reasoning.

### Case A — Faster + reasonable memory

The measured workload is fast and resource usage is within the operational envelope.

Ask whether the result is repeatable and whether the ecosystem/deployment requirements are also satisfied.

### Case B — Faster + dangerous memory

The speed advantage may be irrelevant if the deployment cannot safely contain the memory peak.

### Case C — Slower + much lower memory

A slower workload may still be operationally viable if the SLA is satisfied and the lower memory requirement reduces infrastructure cost/risk.

### Case D — Similar speed + easier deployment

If the workload is well within the SLA, simplicity can be a legitimate architecture factor.

### Case E — Similar performance + stronger ecosystem compatibility

A broader dependency ecosystem can materially reduce engineering work.

None of these cases has a universal answer.

---

## 78. Required “What Would Change My Mind?” Exercise

For each workload, write:

```text
Current decision:
____________________

Evidence supporting it:
____________________

Measured risk:
____________________

What would change my mind?
____________________

Measurement needed:
____________________

Revisit trigger:
____________________
```

This is a senior-level habit: decisions are revisable when the evidence or requirements change.

---

## 79. Production Risk Analysis

Analyze four classes of risk.

### Technical risk

- unsupported operation;
- memory failure;
- type mismatch;
- unexpected execution behaviour.

### Operational risk

- deployment complexity;
- resource limits;
- upgrade churn;
- observability;
- concurrency.

### Organizational risk

- skills;
- ownership;
- hiring/training;
- documentation.

### Financial risk

- compute;
- storage;
- network;
- engineering time;
- operational maintenance.

Do not collapse all risk into a single numeric score.

---

## 80. Required Six-Workload Evaluation Worksheet

For each workload, complete:

```text
WORKLOAD
____________________________

Characteristics
____________________________

Requirements
____________________________

Candidate approaches
____________________________

Correctness reference
____________________________

Benchmark queries
____________________________

Memory concerns
____________________________

I/O concerns
____________________________

Ecosystem concerns
____________________________

Team concerns
____________________________

Deployment concerns
____________________________

Evidence that would change the decision
____________________________

Decision condition
____________________________
```

Do not ask for a universal ranking across all workloads.

---

## 81. Architecture Review Template

```text
ENGINE SELECTION REVIEW

1. Workload
____________________________

2. Data Size
____________________________

3. Growth
____________________________

4. Execution Mode
____________________________

5. Query Interface
____________________________

6. Data Location
____________________________

7. Memory Constraint
____________________________

8. CPU Constraint
____________________________

9. SLA/SLO
____________________________

10. Concurrency
____________________________

11. Ecosystem Dependencies
____________________________

12. Team Skills
____________________________

13. Deployment Target
____________________________

14. Candidate Engines
____________________________

15. Benchmark Evidence
____________________________

16. Peak Memory Evidence
____________________________

17. I/O Evidence
____________________________

18. Operational Risks
____________________________

19. Maintenance Risks
____________________________

20. Decision
____________________________

21. Consequences
____________________________

22. Revisit Conditions
____________________________
```

---

## 82. Required ADR Exercise

### Assignment

> Write a two-page ADR selecting a default single-node analytical engine strategy for a hypothetical Data Engineering team.

Include:

1. context;
2. problem statement;
3. workload characteristics;
4. requirements;
5. candidate options;
6. benchmark methodology;
7. measurement table;
8. operational risks;
9. decision rationale;
10. consequences;
11. revisit conditions.

The final decision must be based on actual benchmark evidence from the learner's environment.

Do not use a predetermined answer.

---

## 83. Required Final Capstone

> **Choose and justify an analytical-engine strategy for a realistic Data Engineering team.**

The capstone must include:

1. workload characterization;
2. requirements;
3. at least three candidate approaches;
4. six representative queries;
5. pandas implementation;
6. Polars lazy/streaming implementation where applicable;
7. DuckDB implementation;
8. correctness validation;
9. three data sizes;
10. cold and warm runs;
11. three repetitions;
12. runtime measurement;
13. peak-memory measurement;
14. bytes-read measurement where relevant;
15. failure analysis;
16. operational-constraint analysis;
17. team/ecosystem analysis;
18. single-node capacity analysis;
19. distributed-architecture boundary analysis;
20. two-page ADR;
21. revisit conditions.

The conclusion must explicitly distinguish:

```text
measured evidence
vs
engineering inference
vs
assumption
```

---

## 84. Correctness Before Performance

A central rule:

```text
correctness
    ↓
then performance
```

Do not interpret a benchmark where implementations produce different results.

For every cross-engine comparison verify:

- row count;
- schema;
- column names;
- null semantics;
- timestamp semantics;
- aggregate values;
- deterministic ordering where required.

The following statement should become habitual:

> Faster does not mean correct.

---

## 85. Reproducibility Checklist

```text
[ ] Workload defined
[ ] Dataset version fixed
[ ] Dataset checksum/version recorded
[ ] Query semantics fixed
[ ] File format fixed
[ ] Python version recorded
[ ] Engine versions recorded
[ ] Hardware recorded
[ ] Memory recorded
[ ] Thread settings recorded
[ ] Deployment limit recorded
[ ] Cache assumptions documented
[ ] Correctness checks defined
[ ] Measurements repeated
[ ] Decision rationale recorded
```

---

## 86. Required Debugging Scenarios

### Scenario 1 — Blog Benchmark Selection

**Symptom:** The team picked an engine because a benchmark blog reported it fastest.

**Root cause:** Workload mismatch and no reproducible evidence.

**Diagnosis:** Reconstruct the production workload, use the same file format, and run representative queries.

**Corrective action:** Benchmark the real workload and document the methodology.

**Lesson:** External benchmarks are evidence, not architecture decisions.

### Scenario 2 — RAM Ignored

**Symptom:** The new implementation is fast locally but fails in CI.

**Root cause:** Local machine had much more RAM than the CI worker.

**Diagnosis:** Record actual runtime limits and measure peak memory under CI constraints.

**Corrective action:** Redesign for the actual envelope or change deployment resources.

**Lesson:** Deployment resources are workload requirements.

### Scenario 3 — Data Grows 10×

**Symptom:** A once-safe pipeline now exceeds memory.

**Root cause:** Capacity planning used today's data only.

**Diagnosis:** Compare historical growth with the tested capacity envelope.

**Corrective action:** Streaming/out-of-core redesign, larger single node, partition redesign, or distributed architecture depending on measurements.

**Lesson:** Engine choices need revisit conditions.

### Scenario 4 — pandas-Only Dependency Appears

**Symptom:** A Polars pipeline now converts to pandas in many places.

**Root cause:** Integration was added without boundary design.

**Diagnosis:** Count conversion points and measure their cost.

**Corrective action:** Keep the main workload in the primary engine and convert once near the dependency edge where possible.

**Lesson:** Integration boundaries should be intentional.

### Scenario 5 — DuckDB Concurrency Bottleneck

**Symptom:** Multiple processes contend while writing one database file.

**Root cause:** Embedded analytical database selected for a shared multi-writer requirement.

**Diagnosis:** Characterize concurrency and write patterns.

**Corrective action:** Change the architecture if shared concurrent writes are a core requirement.

**Lesson:** Concurrency semantics are part of tool selection.

### Scenario 6 — Ecosystem Friction

**Symptom:** A technically fast engine requires many conversion workarounds.

**Root cause:** Library ecosystem requirements were ignored.

**Diagnosis:** Measure the data movement and engineering overhead.

**Corrective action:** Re-evaluate the integration architecture.

**Lesson:** Ecosystem fit matters.

### Scenario 7 — Eager Processing Forced Into a Larger Workload

**Symptom:** Memory grows rapidly as data volume increases.

**Root cause:** An eager execution model was used where lazy/streaming execution was feasible.

**Diagnosis:** Inspect execution mode and peak memory.

**Corrective action:** Evaluate lazy/streaming or out-of-core approaches.

**Lesson:** Execution model is a decision factor.

### Scenario 8 — Remote Workload Benchmarked Locally

**Symptom:** Local SSD performance looked excellent, object-storage execution is slow.

**Root cause:** Network/request costs were not part of the benchmark.

**Diagnosis:** Measure bytes transferred, files touched, request count, and cache conditions.

**Corrective action:** Redesign file layout or benchmark remote execution directly.

**Lesson:** Data location changes the cost model.

### Scenario 9 — CSV vs Parquet Comparison

**Symptom:** An engine looks slower because one implementation parses CSV while another reads Parquet.

**Root cause:** Different input formats.

**Diagnosis:** Re-run using the same file format or define file conversion as part of the workload for both.

**Corrective action:** Make the benchmark apples-to-apples.

**Lesson:** Format is part of workload definition.

### Scenario 10 — Premature Spark Adoption

**Symptom:** A team operates a distributed stack for a workload that fits comfortably on one machine.

**Root cause:** Architecture chosen for hypothetical scale.

**Diagnosis:** Measure current capacity and operational complexity.

**Corrective action:** Consider a simpler single-node architecture if requirements are satisfied.

**Lesson:** Do not pay distributed-system complexity without a real requirement.

### Scenario 11 — Single Node Forced Too Far

**Symptom:** A growing workload repeatedly exceeds the node's capacity.

**Root cause:** Avoidance of architectural escalation despite evidence.

**Diagnosis:** Compare workload growth, peak memory, runtime, and SLA against the tested envelope.

**Corrective action:** Evaluate distributed/shared infrastructure.

**Lesson:** Simplicity does not mean refusing to scale.

### Scenario 12 — Runtime Improves, Peak Memory Becomes Unsafe

**Symptom:** A new version is faster but triggers OOM failures.

**Root cause:** Runtime was optimized without resource validation.

**Diagnosis:** Compare peak memory and container limits.

**Corrective action:** Tune or redesign to stay inside the safe operating envelope.

**Lesson:** Runtime alone is not an architecture metric.

---

## 87. Common Mistakes

Avoid:

- selecting an engine from one benchmark;
- comparing different file formats;
- ignoring RAM;
- ignoring working-set size;
- ignoring cold/warm cache;
- measuring runtime without memory;
- ignoring deployment limits;
- ignoring team skills;
- ignoring ecosystem dependencies;
- ignoring maintenance and upgrade churn;
- choosing distributed systems prematurely;
- forcing single-node tools beyond observed capacity;
- converting between engines at every step;
- comparing implementations without correctness checks;
- trusting invented or non-reproducible performance numbers;
- confusing Arrow with a DataFrame/query engine;
- assuming a new engine is automatically useful because it is fashionable.

---

## 88. Common Production Questions

### Should one engine own the entire pipeline?

Not necessarily. One primary engine often reduces complexity, but deliberate hybrid designs are reasonable when a different engine is materially better at a specific integration point.

### Should everything be persisted in a database?

Not necessarily. File-based analytical workflows, local databases, and shared warehouses solve different problems.

### Can DuckDB replace PostgreSQL?

Not as a general architectural rule. PostgreSQL is a client/server relational database used for many transactional and shared workloads; DuckDB is primarily an embedded analytical engine.

### Can DuckDB replace Spark?

Not as a universal rule. Compare single-node capacity, workload scale, operational requirements, and shared-distributed needs.

### Can DuckDB replace a cloud warehouse?

Not automatically. A shared managed warehouse may satisfy organizational concurrency, governance, elasticity, and platform requirements that an embedded database does not.

### Is the fastest benchmark the correct choice?

No. The result must also satisfy memory, correctness, ecosystem, deployment, operations, and scaling requirements.

### How many engine boundaries should a pipeline have?

As few as are practical without forcing an engine to perform work for which another interface is materially better. Document each boundary's purpose.

### When should I convert to pandas?

Near a pandas-only dependency or a clearly pandas-centric edge, especially when the result is already reduced. Avoid large unnecessary conversions.

---

## 89. Required Explain-Aloud Exercises

Explain each in your own words, without reading notes.

1. Why engine selection begins with the workload.
2. Why there is no universally best analytical engine.
3. pandas strengths and limitations.
4. Polars strengths and limitations.
5. DuckDB strengths and limitations.
6. Arrow's role.
7. Why file format matters.
8. Why RAM and working set matter.
9. Why SQL vs DataFrame preference matters.
10. Why team skills influence architecture.
11. Why ecosystem dependencies matter.
12. Why deployment changes the true resource envelope.
13. Why cold and warm caches differ.
14. Why peak memory must be measured.
15. Why one benchmark is insufficient.
16. When a single-node architecture is sufficient.
17. When a distributed architecture becomes relevant.
18. Why premature distribution can be harmful.
19. Why deliberate engine mixing can be useful.
20. Why unnecessary engine boundaries are expensive.
21. Why Arrow can reduce interoperability friction.
22. What an ADR contains.
23. How to document benchmark evidence.
24. Why consequences belong in an ADR.
25. Why revisit conditions matter.
26. How to evaluate a new analytical engine quickly.
27. How to distinguish an engine limitation from a query/file-layout problem.

---

## 90. Practice Problems — Basic (10)

### B1
Define the difference between an analytical engine and Arrow.

**Answer:** Arrow is a columnar in-memory/interchange representation; an analytical engine executes computations over data.

### B2
List five fields that should appear in a workload characterization.

**Answer:** Any five relevant fields such as row count, working set, common operations, RAM limit, execution mode, data location, SLA, concurrency, or growth.

### B3
Why is file size not the same as peak RAM?

**Answer:** Execution may decompress data, create intermediate structures, maintain join/aggregation state, and materialize results.

### B4
Name the primary role of pandas.

**Answer:** Python DataFrame library/ecosystem.

### B5
Name the primary role of Polars.

**Answer:** Expression-oriented DataFrame execution with parallel/lazy/streaming capabilities.

### B6
Name the primary role of DuckDB.

**Answer:** Embedded analytical database/query engine.

### B7
Why should benchmark formats match?

**Answer:** Different formats create different parsing and I/O workloads and make the comparison ambiguous.

### B8
What is an SLA?

**Answer:** A service commitment, often contractual.

### B9
What is an SLO?

**Answer:** An internal service target used to manage performance/reliability.

### B10
What is an ADR?

**Answer:** A documented architecture decision capturing context, options, evidence, decision, consequences, and related information.

---

## 91. Practice Problems — Moderate (10)

### M1
Why can a team reasonably choose a slower implementation?

**Answer:** Because it may have lower memory risk, better ecosystem compatibility, simpler deployment, easier maintenance, or still satisfy the SLA.

### M2
What is a cold-cache benchmark?

**Answer:** A run designed to represent a state where relevant data/metadata is not already cached by the environment.

### M3
Why perform repeated benchmark runs?

**Answer:** To account for variability and avoid treating a single noisy run as representative.

### M4
Why is `SELECT *` potentially harmful for a wide analytical workload?

**Answer:** It can read and materialize unnecessary columns, increasing I/O and memory.

### M5
Why can a pandas-only dependency justify one pandas boundary in a Polars pipeline?

**Answer:** Because the dependency requires pandas; converting once near the edge can isolate the compatibility requirement and avoid repeated movement.

### M6
Why does an 8 GB container change an engine decision on a 64 GB host?

**Answer:** The process is constrained by the container's runtime memory limit.

### M7
Why is Spark not automatically required for every multi-hundred-GB workload?

**Answer:** A capable single-node columnar engine may process the workload within the required SLA and resource envelope.

### M8
Why might cloud warehouse architecture be relevant even when a local engine is fast?

**Answer:** Shared access, concurrency, governance, managed operations, and elasticity may be requirements.

### M9
Why is Arrow not itself the answer to "which engine should we use?"

**Answer:** Arrow defines a common data representation/interchange layer; execution still happens in a query or DataFrame engine.

### M10
What evidence would make you reconsider an engine choice?

**Answer:** Any measurable change in workload or requirements such as memory pressure, SLA misses, concurrency increases, incompatibility, major growth, or operational cost.

---

## 92. Practice Problems — Hard (10)

### H1
A workload is 60 GB on disk but peaks at 20 GB RAM. A second engine is 5% faster but peaks at 45 GB. The container limit is 32 GB. What should the benchmark report highlight?

**Answer:** The second engine's runtime advantage is operationally unsafe under the current limit. The report should highlight the memory constraint and either reject that configuration or test an architecture/resource change.

### H2
A benchmark shows Engine A faster on the first run, while Engine B is faster on runs 2–3. What must be investigated?

**Answer:** Cache state, startup costs, initialization, and whether the benchmark boundary includes the same work.

### H3
Why can a local SSD benchmark fail to predict object-storage performance?

**Answer:** Remote execution adds network latency, request overhead, authentication, object-store behaviour, and different caching.

### H4
A team wants Spark for 150 GB of Parquet. What questions should be asked first?

**Answer:** What is the working set, query shape, peak memory, SLA, concurrency, growth rate, failure history, and tested single-node capacity?

### H5
A Polars pipeline converts to pandas six times. How should you investigate?

**Answer:** Map the boundaries, identify why each exists, measure conversion time/peak memory, and consolidate unnecessary boundaries.

### H6
Why can an apparently simple join become the reason a single-node workload fails?

**Answer:** Join state, output explosion, key cardinality, or retained build-side data can dominate memory.

### H7
What is the difference between "best benchmark result" and "best production fit"?

**Answer:** Production fit includes requirements, memory, correctness, ecosystem, deployment, operations, maintenance, cost, and future scale in addition to performance.

### H8
Why should an ADR contain consequences?

**Answer:** Every architecture choice trades something away; documenting consequences prevents future engineers from assuming there were no costs.

### H9
When does a standardized TPC-H-style benchmark become insufficient?

**Answer:** When the production workload has materially different data shapes, file layouts, custom logic, operational constraints, or query patterns.

### H10
How do you distinguish an engine problem from a bad query/file-layout problem?

**Answer:** Inspect the plan, measure scan volume, file count, bytes read, partitioning, projection/filter behaviour, operator cost, and compare with a better-designed query/layout before changing engines.

---

## 93. Practice Problems — Advanced (10)

### A1
Design a benchmark to decide between Polars and DuckDB for a 120 GB Parquet workload.

**Answer key:** Characterize six representative queries, create a correctness baseline, keep format/hardware/configuration constant, test small/RAM-scale/larger-than-RAM sizes where feasible, run cold/warm repeated runs, measure runtime + peak memory + I/O, and evaluate deployment/team/ecosystem factors.

### A2
A query is 2× faster after an engine upgrade but peak memory increased 70%. How should the team evaluate the release?

**Answer key:** Re-run the benchmark under production memory limits, inspect correctness, identify which operator changed, compare the new peak against headroom, and decide using the full SLA/resource envelope rather than runtime alone.

### A3
Design an architecture for SQL-heavy transformations followed by a pandas-only package.

**Answer key:** Keep the SQL-heavy computation in DuckDB, reduce the result before crossing the boundary, convert once to pandas near the dependency edge, measure/validate the boundary, and avoid converting intermediate results repeatedly.

### A4
A 5 TB workload currently runs on one machine but misses its SLA. What evidence is needed before moving to distributed processing?

**Answer key:** Identify the current bottleneck, measure CPU/memory/I/O, test whether query/file-layout optimization or a larger single node solves the issue, quantify the SLA gap, and define why distributed execution changes the constraint.

### A5
How would you evaluate DataFusion as a new candidate?

**Answer key:** Characterize the target workload, confirm format/operator coverage, establish a correctness implementation, benchmark representative queries, record memory/I/O, evaluate embedding and ecosystem needs, and compare the measured evidence with the existing architecture.

### A6
A GPU engine is proposed because a CPU query is slow. What should be measured first?

**Answer key:** Determine whether the workload is compute-bound versus I/O/memory/network-bound, identify GPU-compatible operators, measure transfer/setup overhead, and compare end-to-end runtime and memory rather than kernel-level speed alone.

### A7
Write three revisit conditions for a DuckDB local warehouse.

**Answer key:** Examples: concurrency grows beyond the tested model, peak memory reaches the safe container limit, or response time exceeds the documented SLA/capacity envelope.

### A8
A team says "we need distributed computing because data is 300 GB." What is missing?

**Answer key:** Resource measurements, query shape, working set, SLA, concurrency, growth, and evidence that one-node execution cannot satisfy requirements.

### A9
Why can maintainability be a better deciding factor than a small runtime difference?

**Answer key:** If both satisfy the SLA, the lower-complexity solution may reduce engineering and operational cost while improving reliability and upgrade safety.

### A10
Explain how to justify a hybrid architecture without creating engine sprawl.

**Answer key:** Define a primary engine, allow only meaningful boundaries, document each boundary's purpose/cost, benchmark the conversion, and periodically remove boundaries that are no longer justified.

---

## 94. Senior Data Engineer Interview Questions

### Beginner

1. What factors should influence analytical engine selection?
2. What is the difference between pandas, Polars, DuckDB, and Arrow?
3. Why does data size versus RAM matter?
4. Why does SQL versus DataFrame preference matter?
5. Why does ecosystem compatibility matter?

### Intermediate

6. How would you benchmark two analytical engines fairly?
7. Why are cold and warm cache runs different?
8. Why should peak memory be measured?
9. Why might a slower engine still be selected?
10. When is a single-node architecture sufficient?
11. Why should you avoid selecting a tool from a vendor benchmark alone?
12. What makes a benchmark reproducible?
13. Why must file format be controlled in a benchmark?
14. Why can team skills change the effective architecture cost?

### Advanced

15. How do you determine whether a workload has crossed the single-node boundary?
16. How would you design a six-query, three-size benchmark?
17. How do you compare an engine that is faster but uses twice the memory?
18. How should serverless startup influence engine selection?
19. When does DuckDB concurrency become an architectural concern?
20. When should a team intentionally mix DuckDB and Polars?
21. How do you prevent engine-boundary proliferation?
22. How would you structure an ADR for an engine decision?
23. What conditions should trigger revisiting an engine choice?
24. How would you evaluate DataFusion, chDB, or cuDF as a new candidate?
25. How do you distinguish an engine problem from a query or file-layout problem?

### Answer key

**1–5:** Start with workload characteristics, not preferences; identify each tool's role and match it to the workload.

**6–8:** Use same data/format/query semantics/hardware, repeat runs, document cache state, and measure peak memory as well as runtime.

**9:** Architecture includes correctness, memory, deployment, compatibility, operations, and maintainability.

**10:** When measured capacity, SLA, and concurrency requirements fit the single-node resource envelope with sufficient headroom.

**11:** Vendor tests may use selective workloads, caching, formats, thread settings, or semantics that differ from your production workload.

**12–14:** Pin/document versions, hardware, data, queries, configuration, cache assumptions, and correctness criteria; team skill affects training/debugging/maintenance cost.

**15:** Compare measured memory, CPU, I/O, runtime, concurrency, and growth against the tested capacity envelope and SLA.

**16:** Six representative workloads × three data sizes × cold/warm × three repetitions, with correctness checks and peak-memory measurement.

**17:** Test both against the deployment limit and business SLA. A faster but unsafe memory footprint may be operationally unacceptable.

**18:** Include initialization and packaging in the end-to-end measurement when serverless latency matters.

**19:** When shared writers/concurrent access are core requirements rather than incidental development convenience.

**20:** When a second engine is materially better for a specific step and the boundary cost is acceptable.

**21:** Name the primary engine, document boundaries, measure them, and remove unneeded conversions.

**22:** Context → requirements → options → measurements → decision → consequences → revisit conditions.

**23:** Missed SLA, memory pressure, scale growth, concurrency changes, ecosystem incompatibility, or material maintenance/operational changes.

**24:** Use the same workload characterization, correctness baseline, representative benchmark, and deployment/maintenance evaluation.

**25:** Inspect the query, scan volume, file layout, plan/operators, partitioning, I/O, memory, and conversion boundaries before blaming the engine.

---

## 95. Senior Architecture Scenarios (12)

### Scenario 1 — 5 GB CSV in a 2 GB Container

Evaluate parsing, memory, startup, output, and simplicity. Build a small benchmark and determine whether the workload actually needs a heavier architecture.

**Answer key:** The first requirement is to prove the workload can fit inside the 2 GB runtime envelope with headroom. Test CSV ingestion, transformation, and output end-to-end. Engine selection remains workload-dependent.

### Scenario 2 — 200 GB Analyst Parquet

**Answer key:** Evaluate SQL convenience, file layout, partition pruning, interactive latency, and local versus shared access. Benchmark representative queries rather than choosing from a generic ranking.

### Scenario 3 — 500 GB Feature Preparation

**Answer key:** Evaluate DataFrame transformations, ML-library compatibility, memory, conversion boundaries, and whether streaming is useful. A hybrid boundary may be reasonable if the final library has pandas requirements.

### Scenario 4 — 5 TB Daily Joins

**Answer key:** Measure whether the workload exceeds practical single-node throughput or memory. Evaluate distributed scheduling/shared infrastructure if the evidence shows one node cannot satisfy requirements.

### Scenario 5 — Local Warehouse Testing

**Answer key:** Evaluate reproducibility, startup, SQL compatibility, fixture management, and whether the local engine can reproduce the target warehouse semantics sufficiently for the test scope.

### Scenario 6 — pandas-Only Scientific Package

**Answer key:** Keep the primary transformation engine stable and isolate the pandas conversion near the package boundary, with schema/value validation.

### Scenario 7 — Local SSD to Object Storage

**Answer key:** Re-benchmark remotely. Measure files, partitions, bytes transferred, request behaviour, and cache state. File layout becomes more important.

### Scenario 8 — Kubernetes Limit Drops from 32 GB to 8 GB

**Answer key:** Repeat peak-memory tests under 8 GB. The architecture must be judged against the new runtime envelope, not historical laptop performance.

### Scenario 9 — Data Doubles Every Six Months

**Answer key:** Create a capacity envelope and revisit conditions. Test growth points before failure rather than waiting for production OOMs.

### Scenario 10 — SQL-First Team + Complex Python Logic

**Answer key:** A deliberate hybrid may fit: DuckDB for SQL-heavy work and Polars for complex expression-oriented DataFrame work, with Arrow/another narrow boundary when appropriate.

### Scenario 11 — GPU Proposal

**Answer key:** Identify whether the bottleneck is GPU-suitable compute. If the workload is network/I/O/memory-bound, GPU acceleration may not address the real problem.

### Scenario 12 — "300 GB Means Spark"

**Answer key:** Reject the premise as incomplete. Characterize the workload and benchmark single-node capacity first. Move to distributed architecture only when actual constraints justify it.

---

## 96. Required TPC-H-Style Evaluation Lab

The learner should:

1. choose a standardized analytical benchmark family such as TPC-H-style queries;
2. select a small subset of representative queries;
3. implement equivalent semantics in candidate engines;
4. document schema/data-generation assumptions;
5. run controlled benchmarks;
6. measure runtime and memory;
7. validate results;
8. compare standardized results with the learner's own six-query workload;
9. explain why the two benchmark families can lead to different observations.

The learning objective is not to publish a leaderboard. It is to learn how benchmark choice shapes conclusions.

---

## 97. Required New-Engine Evaluation Spike

Choose one of:

- DataFusion;
- chDB;
- cuDF;
- another current analytical engine.

Do not implement a full production system.

### Evaluation protocol

```text
1. Write workload description
2. Identify target execution model
3. Verify feature coverage
4. Implement one representative query
5. Validate correctness
6. Measure runtime
7. Measure peak memory
8. Record interoperability boundary
9. Record deployment implications
10. Decide whether a deeper evaluation is justified
```

The final write-up must state what is known, what was measured, and what remains uncertain.

---

## 98. Production Decision Rules

These are engineering principles, not absolute laws:

```text
1. Start with workload characteristics.
2. Define requirements before selecting tools.
3. Benchmark realistic queries.
4. Measure memory as well as time.
5. Keep the file format identical when comparing engines.
6. Control/document cache and environment conditions.
7. Validate correctness before interpreting performance.
8. Account for team and ecosystem constraints.
9. Account for deployment and operational constraints.
10. Avoid premature distribution.
11. Avoid forcing single-node tools past observed capacity.
12. Mix engines deliberately when justified.
13. Minimize unnecessary engine boundaries.
14. Document important decisions with ADRs.
15. Define conditions that trigger re-evaluation.
```

---

## 99. Decision Matrix — No Universal Scoring

Use a qualitative matrix for a specific workload:

| Requirement | pandas | Polars | DuckDB | Hybrid | Distributed |
|---|---|---|---|---|---|
| Data size | describe fit for workload | describe fit for workload | describe fit for workload | describe fit for workload | describe fit for workload |
| SQL requirement | assess | assess | assess | assess | assess |
| DataFrame requirement | assess | assess | assess | assess | assess |
| Ecosystem dependency | assess | assess | assess | assess | assess |
| Memory constraint | assess | assess | assess | assess | assess |
| Streaming need | assess | assess | assess | assess | assess |
| Persistence | assess | assess | assess | assess | assess |
| Concurrency | assess | assess | assess | assess | assess |
| Deployment simplicity | assess | assess | assess | assess | assess |
| Remote files | assess | assess | assess | assess | assess |
| Future scale | assess | assess | assess | assess | assess |

Use labels such as:

- strong fit for this workload;
- possible fit;
- requires investigation;
- operational concern.

Do not turn the matrix into stars, numerical scores, tiers, or a permanent ranking.

---

## 100. A Practical Design Pattern: Primary Engine + Edges

A useful production pattern is:

```text
               PRIMARY ENGINE
                    │
          ┌─────────┴─────────┐
          │                   │
        INPUT                OUTPUT
          │                   │
      Parquet/Arrow       pandas-only edge
```

The primary engine should perform most of the workload that it handles naturally. Edge integrations should be explicit.

Example:

```text
DuckDB
  ↓
filter + aggregate + join
  ↓
Arrow
  ↓
Polars
  ↓
final transformation
  ↓
pandas
  ↓
legacy package
```

This is a pattern, not a mandate.

---

## 101. Decision Tree for Initial Triage

Use this only as an initial triage tool.

```text
What is the workload?
        ↓
Is it primarily relational/SQL?
   ├── Yes → evaluate DuckDB and alternatives
   └── No
        ↓
Is it primarily DataFrame/expression oriented?
   ├── Yes → evaluate Polars/pandas and alternatives
   └── Mixed → evaluate a hybrid
        ↓
Does it fit comfortably in the runtime memory envelope?
   ├── Yes → single-node candidates remain viable
   └── No → evaluate streaming/out-of-core
        ↓
Does one machine still meet SLA/concurrency/capacity?
   ├── Yes → remain single-node
   └── No → evaluate distributed/shared architecture
```

Every branch still requires evidence.

---

## 102. When a New Engine Is Worth a Deeper Study

A new engine deserves deeper evaluation when it has a credible advantage on a real requirement, such as:

- a missing execution feature;
- substantially lower measured memory;
- a deployment model that materially simplifies operations;
- a required accelerator/GPU path;
- improved interoperability;
- a distributed capability that solves a demonstrated scale problem.

Do not evaluate a new engine merely because benchmark charts look exciting.

---

## 103. Final Engine Selection Worksheet

```text
ENGINE SELECTION REVIEW

Workload:
____________________________

Business requirement:
____________________________

Data size today:
____________________________

Expected growth:
____________________________

Operations:
____________________________

Primary interface:
SQL / DataFrame / Mixed

Data location:
____________________________

Memory limit:
____________________________

CPU:
____________________________

Storage:
____________________________

SLA/SLO:
____________________________

Concurrency:
____________________________

Ecosystem dependencies:
____________________________

Team skills:
____________________________

Deployment target:
____________________________

Candidate engines:
____________________________

Correctness reference:
____________________________

Benchmark evidence:
____________________________

Peak memory evidence:
____________________________

I/O evidence:
____________________________

Operational risks:
____________________________

Maintenance risks:
____________________________

Decision:
____________________________

Consequences:
____________________________

What would change my mind?
____________________________

Revisit conditions:
____________________________
```

---

## 104. Final Mastery Checklist

- [ ] I understand why engine selection starts with workload characterization.
- [ ] I understand the role of pandas.
- [ ] I understand the role of Polars.
- [ ] I understand the role of DuckDB.
- [ ] I understand the role of Arrow.
- [ ] I understand the strengths and limits of pandas.
- [ ] I understand the strengths and limits of Polars.
- [ ] I understand the strengths and limits of DuckDB.
- [ ] I understand data size versus RAM.
- [ ] I understand file size versus working-set size.
- [ ] I understand SQL versus DataFrame considerations.
- [ ] I understand team-skill constraints.
- [ ] I understand ecosystem constraints.
- [ ] I understand deployment-target constraints.
- [ ] I understand single-node architecture.
- [ ] I understand single-node limits.
- [ ] I understand Spark at awareness level.
- [ ] I understand Dask at awareness level.
- [ ] I understand Ray Data at awareness level.
- [ ] I understand cloud warehouses conceptually.
- [ ] I understand container memory limits.
- [ ] I understand serverless cold-start considerations.
- [ ] I understand DuckDB concurrency as a decision factor.
- [ ] I understand reproducibility.
- [ ] I understand upgrade churn.
- [ ] I can design a fair benchmark.
- [ ] I understand cold versus warm cache.
- [ ] I understand repeated runs.
- [ ] I understand why benchmark file formats must match.
- [ ] I can measure peak memory.
- [ ] I understand vendor benchmark limitations.
- [ ] I understand TPC-H-style benchmark concepts.
- [ ] I can benchmark a workload rather than a library abstractly.
- [ ] I understand deliberate engine mixing.
- [ ] I understand Arrow as interoperability glue.
- [ ] I understand engine-boundary costs.
- [ ] I understand ADRs.
- [ ] I can write ADR context.
- [ ] I can define ADR options.
- [ ] I can document benchmark evidence.
- [ ] I can document consequences.
- [ ] I can define revisit conditions.
- [ ] I understand DataFusion at awareness level.
- [ ] I understand chDB at awareness level.
- [ ] I understand cuDF at awareness level.
- [ ] I understand CPU versus GPU versus distributed execution.
- [ ] I understand architecture escalation.
- [ ] I can create a correctness reference.
- [ ] I can reconcile cross-engine results.
- [ ] I understand production risk analysis.
- [ ] I completed the six-workload evaluation.
- [ ] I completed the `engine_benchmark/` exercise.
- [ ] I wrote the two-page ADR.
- [ ] I completed the “what would change my mind?” exercise.
- [ ] I can evaluate a new engine systematically.
- [ ] I completed the final capstone.
- [ ] I can defend an engine decision using evidence.

---

## 105. Final Mastery Assessment

### Part A — Fundamentals (15)

1. Define workload characterization.
2. Why is there no universally best analytical engine?
3. What is pandas primarily designed to provide?
4. What is Polars primarily designed to provide?
5. What is DuckDB primarily designed to provide?
6. What is Arrow's role?
7. Why is file size not equal to working-set size?
8. Why does SQL versus DataFrame preference matter?
9. Why do team skills matter?
10. Why do ecosystem dependencies matter?
11. Why do deployment targets matter?
12. What is an ADR?
13. What is a correctness reference?
14. Why are benchmark results evidence rather than truth?
15. What should trigger revisiting an engine choice?

### Part B — Workload Characterization (10)

16. Characterize a 5 GB CSV → Parquet pipeline.
17. Characterize a 200 GB Parquet analyst workload.
18. Characterize a feature-engineering workflow using scikit-learn.
19. Characterize a 5 TB recurring join workload.
20. Characterize a CI SQL-testing workload.
21. Add a hybrid workload and characterize it.
22. Identify the memory constraints in one workload.
23. Identify the concurrency constraints in one workload.
24. Identify the ecosystem constraints in one workload.
25. Identify the future-growth constraints in one workload.

### Part C — Benchmark Design (10)

26. Design a six-query benchmark.
27. Define three data sizes.
28. Define cold and warm conditions.
29. Explain why three repetitions are useful.
30. Explain why the same file format matters.
31. Define peak-memory measurement.
32. Define I/O measurements.
33. Define correctness criteria.
34. Identify five sources of benchmark contamination.
35. Explain why a vendor benchmark may not generalize.

### Part D — Benchmark Interpretation (10)

36. An engine is faster but uses twice the memory. How do you evaluate it?
37. Run 1 is slow; runs 2–3 are fast. What happened?
38. An engine fails only at the larger-than-RAM size. What do you investigate?
39. Local SSD is much faster than object storage. Why?
40. Runtime improved after an upgrade but peak memory increased. What next?
41. Two engines have nearly identical speed but different code complexity. How do you reason?
42. A benchmark shows a winner but uses different compression. Is it valid?
43. A benchmark shows faster results with `SELECT *` in one engine and selected columns in another. Is it valid?
44. A benchmark result is technically faster but violates the SLA memory limit. What does that mean?
45. How do you distinguish a noisy result from a stable difference?

### Part E — Single-Node vs Distributed (10)

46. When is one machine enough?
47. What evidence indicates a single-node boundary?
48. Why is data size alone insufficient to justify Spark?
49. When is distributed execution relevant?
50. What additional complexity does distributed architecture introduce?
51. How can cloud warehouses solve requirements beyond local query speed?
52. What does Dask add conceptually?
53. What does Ray Data add conceptually?
54. What does Spark add conceptually?
55. Define a sensible architecture escalation path.

### Part F — Engine Mixing (10)

56. Give a valid reason to mix DuckDB and Polars.
57. Give a valid reason to use pandas at the edge.
58. Why can Arrow be useful as glue?
59. What is engine-boundary proliferation?
60. Explain the repeated DuckDB → pandas → Polars → pandas → DuckDB anti-pattern.
61. How do you reduce conversions?
62. Why should a pipeline choose a primary engine?
63. How do you measure a conversion boundary?
64. When is hybrid architecture worth the extra complexity?
65. What evidence would make you simplify a hybrid pipeline?

### Part G — ADR Writing (5)

66. Write the context section for an engine decision.
67. List realistic candidate options.
68. Define what benchmark evidence belongs in an ADR.
69. Write a decision statement without claiming a universal winner.
70. Write three consequences and three revisit conditions.

### Part H — New Engine Evaluation (5)

71. How would you evaluate DataFusion?
72. How would you evaluate chDB?
73. How would you evaluate cuDF?
74. How would you decide whether to run a deeper spike?
75. What must be measured before adopting a new engine?

### Part I — Senior Architecture (10)

76. A 5 GB workload runs in a 2 GB container. Design the evaluation.
77. A 200 GB lake workload is used interactively. What factors matter?
78. A 500 GB feature pipeline ends in a pandas-only library. What architecture would you test?
79. A 5 TB daily workload misses SLA. How do you decide whether to distribute?
80. Kubernetes memory drops from 32 GB to 8 GB. What changes?
81. Data doubles every six months. How do you capacity-plan?
82. A GPU proposal arrives for a network-bound workload. How do you evaluate it?
83. A team wants Spark for 300 GB simply because it is "big data." How do you respond in a design review?
84. A local engine is fast but shared concurrency is increasing. What requirement changed?
85. A benchmark shows one engine ahead, but the production workload has different file layout and query shape. What evidence should dominate the final decision?

### Complete Answer Key

#### A1–A15

1. A structured description of data, queries, execution mode, resources, and operational requirements before choosing a tool.
2. Because different workloads optimize different constraints: SQL, DataFrame ergonomics, memory, ecosystem, concurrency, deployment, and scale.
3. A Python DataFrame library/ecosystem.
4. An expression-oriented high-performance DataFrame engine with lazy and streaming capabilities.
5. An embedded analytical database/query engine.
6. A columnar in-memory representation and interoperability layer.
7. Compression, decoding, intermediates, joins, aggregation, sorting, and output materialization change peak memory.
8. The natural interface affects developer productivity and query expression.
9. Skills influence training, debugging, maintenance, and operational reliability.
10. Downstream libraries may force specific representations or APIs.
11. Runtime memory/CPU, startup, storage, networking, and concurrency differ by deployment.
12. A record of an architecture decision and its reasoning.
13. A trusted implementation/result used to validate other engines.
14. They come from specific workloads and conditions.
15. Observable requirement/capacity changes such as memory pressure, SLA misses, scale growth, concurrency, or compatibility changes.

#### B16–B25

Use the workload worksheet. Full-credit answers must mention data size, working set, operations, execution mode, location, memory, SLA, concurrency, ecosystem, team, deployment, and growth where relevant.

#### C26–C35

A correct design keeps the six representative queries semantically equivalent, uses three data sizes, cold/warm conditions, repeated runs, the same file format, documented hardware/configuration, correctness validation, and runtime/peak-memory measurements. I/O metrics should be added where the workload makes them relevant.

#### D36–D45

Full-credit answers must reason about the complete resource envelope, not speed alone. They should identify cache effects, memory headroom, format consistency, correctness, operational limits, and statistical variability.

#### E46–E55

One machine is sufficient when measured resource use and SLA fit the machine's practical capacity with headroom. Distributed execution becomes relevant when the workload's observed throughput, memory, concurrency, or organizational requirements exceed a single node's practical envelope. No fixed dataset size determines the answer.

#### F56–F65

A valid hybrid boundary has a concrete technical reason. Arrow can reduce interoperability friction. Too many boundaries increase conversion and maintenance cost. A primary engine minimizes unnecessary movement. Every boundary should be measured and documented.

#### G66–G70

A complete ADR contains context, requirements, options, evidence, decision, consequences, and revisit conditions. The decision must reference the actual workload and measured evidence rather than a universal ranking.

#### H71–H75

Evaluate each new engine against workload fit, execution model, format support, memory behaviour, interoperability, deployment, ecosystem, correctness, runtime, peak memory, and maintainability.

#### I76–I85

Full-credit answers identify requirements first, propose measurable hypotheses, and explicitly consider memory, runtime, I/O, deployment, ecosystem, concurrency, growth, and correctness. Senior answers also identify what evidence would change the decision.

---

## 106. Final “Teach It Back” Exercise

Explain the complete topic in your own words, without notes.

You should be able to explain:

1. why engine selection starts with workload characterization;
2. what pandas contributes;
3. what Polars contributes;
4. what DuckDB contributes;
5. what Arrow contributes;
6. why RAM and working set matter;
7. why data format matters;
8. why SQL versus DataFrame preference matters;
9. why ecosystem dependencies matter;
10. why team skills matter;
11. why deployment constraints matter;
12. how to benchmark fairly;
13. why cache state matters;
14. why peak memory matters;
15. why one benchmark is insufficient;
16. when one machine is enough;
17. when distributed systems become relevant;
18. why premature distribution can be harmful;
19. why a hybrid pipeline can be useful;
20. why too many engine boundaries can be expensive;
21. how Arrow supports interoperability;
22. what an ADR is;
23. how measurements should be documented;
24. how consequences should be documented;
25. how revisit conditions work;
26. how to evaluate a new engine;
27. how to determine whether a problem is really an engine problem.

A strong explanation should sound like an engineer defending a design, not a student reciting product descriptions.

---

## 107. Version Awareness

The tools discussed here evolve quickly:

- pandas;
- Polars;
- DuckDB;
- PyArrow;
- Narwhals;
- Dask;
- Ray;
- DataFusion;
- cuDF;
- chDB.

For current APIs:

1. record installed versions;
2. prefer current stable documentation;
3. mark version-sensitive behaviour;
4. never invent parameters or methods;
5. rerun benchmarks after important upgrades;
6. distinguish measured behaviour from documentation and inference.

Current documentation illustrates why this matters. Polars' current LazyFrame API uses an `engine` parameter for execution selection and documents the streaming engine separately from in-memory execution. DuckDB's current Python API documents result retrieval, relations, and batch-oriented Arrow result readers.

Do not assume an API shown in an older tutorial remains current.

---

## 108. Technical Accuracy Requirements

Be precise about:

- engine role;
- workload characterization;
- memory capacity;
- working set;
- query semantics;
- benchmarking fairness;
- cache effects;
- peak memory;
- I/O;
- correctness;
- deployment constraints;
- concurrency;
- ecosystem compatibility;
- maintenance;
- scale boundaries;
- engine mixing;
- Arrow interoperability;
- ADR methodology.

Avoid statements such as:

```text
Polars is always faster.
DuckDB is always best for SQL.
Spark is required above X GB.
One engine should always be used.
More engines are always better.
```

The technically correct form is:

```text
For this workload,
under these requirements,
with these measurements,
this architecture satisfies the constraints.
```

---

## 109. Important Distinction — Performance vs Fit

Remember:

```text
fastest benchmark result
≠
best production fit
```

The engineering decision considers:

```text
performance
+
memory
+
correctness
+
ecosystem
+
deployment
+
team
+
operations
+
scale
+
cost
```

The appropriate decision depends on the relative importance of those requirements for the actual workload.

---

## 110. Important Distinction — Single Node vs Distributed

Remember:

```text
single-node
≠
small data only
```

and:

```text
distributed
≠
automatically better
```

A powerful single machine with an efficient columnar engine may satisfy a substantial workload.

A distributed architecture may be justified when scale, throughput, concurrency, fault isolation, or shared-service requirements exceed single-node capabilities.

---

## 111. Important Distinction — Benchmark vs Production

A benchmark is:

```text
controlled experiment
```

Production is:

```text
real workload
+
variability
+
failure modes
+
operations
+
upgrades
+
organizational constraints
```

Therefore:

> A benchmark is evidence, not the entire architecture decision.

---

## 112. Important Distinction — Engine vs File Layout

When performance is poor, ask both:

```text
Is the engine a problem?
```

and:

```text
Is the workload poorly designed?
```

Investigate:

- unnecessary columns;
- missing predicates;
- poor partitioning;
- tiny files;
- excessive conversion boundaries;
- high-cardinality joins;
- avoidable materialization.

A new engine cannot automatically repair a poorly structured workload.

---

## 113. Required Production Review Checklist

Before approving an engine choice:

```text
[ ] Workload characterized
[ ] Requirements explicit
[ ] Correctness reference available
[ ] Representative queries defined
[ ] Same format used in comparison
[ ] Data sizes defined
[ ] Cache conditions documented
[ ] Repetitions performed
[ ] Runtime measured
[ ] Peak memory measured
[ ] I/O measured where meaningful
[ ] Deployment limit tested
[ ] Ecosystem dependencies reviewed
[ ] Team capability reviewed
[ ] Maintenance/upgrade plan reviewed
[ ] Single-node capacity evaluated
[ ] Distributed boundary defined
[ ] Engine boundaries documented
[ ] ADR written
[ ] Revisit conditions defined
```

---

## 114. Closing Mental Model

When someone asks:

> "Which DataFrame engine should we use?"

do not answer immediately.

Start with:

```text
What workload?
       ↓
What requirements?
       ↓
What data size and working set?
       ↓
What query patterns?
       ↓
What deployment environment?
       ↓
What ecosystem dependencies?
       ↓
What candidate engines?
       ↓
What benchmark?
       ↓
What memory and I/O results?
       ↓
What operational trade-offs?
       ↓
What architecture fits?
       ↓
What would change our mind?
```

That is the core senior-engineering skill this topic is designed to build.

---

## 115. Reference Notes for Current APIs

This chapter deliberately avoids embedding fixed benchmark numbers and avoids depending on obsolete method signatures. When executing the exercises, verify current installed APIs against the documentation for the exact versions in your environment.

Current references used while authoring the chapter include:

- DuckDB Python client and relational API documentation for current relation/result interfaces and Arrow batch readers.
- Polars current `LazyFrame`, `collect`, `collect_batches`, and execution-engine documentation.
- pandas current PyArrow-backed dtype documentation and `DataFrame.from_arrow` support.
- Apache Arrow Python documentation for its columnar interchange role.
- Apache DataFusion documentation for awareness-level positioning.
- Narwhals documentation for dataframe-agnostic interfaces.

These references support current API/role descriptions; benchmark conclusions must still come from the learner's own measurements.

---

# Final principle

> **Choose the engine that best satisfies the workload's requirements under measured technical and operational constraints — and document what evidence would make you change the decision.**
