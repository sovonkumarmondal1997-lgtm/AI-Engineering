# Practice Questions — Module 2.1

> **Scope:** Topics 01–08 of `Python for Data Engineering/01-Data-Engineering-Foundations-and-Pipeline-Thinking/`  
> **Total:** 32 questions  
> **Distribution:** 8 Basic + 8 Moderate + 8 Hard + 8 Advanced  
> **Coverage rule:** Every topic appears exactly once at every difficulty level.  
> **Answer rule:** Attempt the **Problem** yourself before reading **How to Solve the Problem** and **Solution**.

---

# How to Use This File

The purpose of this file is not to test vocabulary.

It is to train you to reason about a real Data Engineering system.

For every question:

```text
Problem
   ↓
Understand the scenario
   ↓
Identify sources and consumers
   ↓
Identify workload and data characteristics
   ↓
Draw the architecture
   ↓
Choose the relevant pattern
   ↓
Consider failures and trade-offs
   ↓
Write the solution
   ↓
Explain why
```

For architecture questions, use:

```text
Context
→ Requirements
→ Constraints
→ Options
→ Trade-offs
→ Decision
→ Consequences
```

For pipeline questions, reason through:

```text
Source
→ Ingestion
→ Storage
→ Transformation
→ Serving
→ Consumer
```

For operational/reliability questions, reason through:

```text
Consumer
→ Requirement
→ SLI
→ SLO
→ Dependencies
→ Budget
→ Operational response
```

Do not look at a solution first.

Being wrong on paper is cheap.

Being wrong in production is not.

---

# Question Map

| Question | Difficulty | Primary Topic | Main Focus |
|---|---|---|---|
| Q01 | Basic | Topic 01 | Data engineer deliverables and data products |
| Q02 | Basic | Topic 02 | Complete data lifecycle |
| Q03 | Basic | Topic 03 | Batch vs micro-batch vs streaming |
| Q04 | Basic | Topic 04 | ETL vs ELT |
| Q05 | Basic | Topic 05 | OLTP vs OLAP |
| Q06 | Basic | Topic 06 | Warehouse vs lake vs lakehouse |
| Q07 | Basic | Topic 07 | Bronze / Silver / Gold responsibilities |
| Q08 | Basic | Topic 08 | SLI / SLO / SLA and freshness |
| Q09 | Moderate | Topic 01 | Production pipeline vs one-off script |
| Q10 | Moderate | Topic 02 | Source characteristics and architecture |
| Q11 | Moderate | Topic 03 | Processing-mode selection |
| Q12 | Moderate | Topic 04 | ETL / ELT / EtLT with replay and security |
| Q13 | Moderate | Topic 05 | Read replica vs CDC vs analytical workload |
| Q14 | Moderate | Topic 06 | Platform choice and governance |
| Q15 | Moderate | Topic 07 | Transformation placement and grain |
| Q16 | Moderate | Topic 08 | Measurable freshness/completeness SLO |
| Q17 | Hard | Topic 01 | Centralized vs embedded vs data mesh |
| Q18 | Hard | Topic 02 | Multi-source lifecycle and validation |
| Q19 | Hard | Topic 03 | Backlog, rates, state, and hybrid processing |
| Q20 | Hard | Topic 04 | Reverse ETL control loop |
| Q21 | Hard | Topic 05 | Protecting production OLTP from analytics |
| Q22 | Hard | Topic 06 | Warehouse/lake/lakehouse requirements analysis |
| Q23 | Hard | Topic 07 | Replay, quarantine, idempotency, grain |
| Q24 | Hard | Topic 08 | SLO breach diagnosis and latency budget |
| Q25 | Advanced | Topic 01 | Enterprise operating model and data products |
| Q26 | Advanced | Topic 02 | End-to-end banking data architecture |
| Q27 | Advanced | Topic 03 | Lambda vs Kappa vs hybrid |
| Q28 | Advanced | Topic 04 | E-commerce analytics + reverse ETL + backfill |
| Q29 | Advanced | Topic 05 | Mixed OLTP/OLAP production architecture |
| Q30 | Advanced | Topic 06 | Analytical-platform ADR |
| Q31 | Advanced | Topic 07 | Medallion redesign of a complex data platform |
| Q32 | Advanced | Topic 08 | Consumer-centric SLO and reliability architecture |

---

# Part I — Basic

## Question 01 — What Does a Data Engineer Actually Build?

**Difficulty:** Basic

**Primary Topic:** Topic 01 — What Data Engineers Build

**Concepts Tested:**
- Data Engineer responsibility
- pipeline
- dataset
- job
- table
- data product
- ingestion and transformation pipelines
- consumers and owners

### Problem

A small e-commerce company has these requests:

1. Move orders from an operational database into an analytical environment every night.
2. Clean and standardize the order data.
3. Publish a trusted `daily_revenue` dataset.
4. Provide a stable internal interface for another application to read that dataset.
5. Create a reusable command-line tool that checks whether a pipeline produced the expected output.

The engineering manager asks:

> "Which of these are Data Engineering responsibilities, and what kinds of artifacts are being built?"

Classify each request and explain the relationship among:

```text
pipeline
job
dataset
table
data product
internal tooling
```

### How to Solve the Problem

1. Identify whether the work moves data, transforms data, serves data, or supports the operation of the data system.
2. Separate a logical data asset from the executable work that produces it.
3. Identify which outputs are intended for reuse by consumers.
4. Ask whether the result has an owner, consumers, documentation, and reliability expectations.
5. Do not assume every artifact is simply "a table."

### Solution

1. Moving orders from the operational database is an **ingestion pipeline**.
2. Cleaning and standardizing the orders is a **transformation pipeline**.
3. `daily_revenue` is a **curated dataset** and can become a **data product** when it has a defined owner, consumers, meaning, documentation, and expectations.
4. A stable internal interface for reading the dataset is a **data API** or data-serving interface.
5. The command-line checker is **internal data tooling**.

A useful relationship is:

```text
Pipeline
=
definition of the data-processing flow

Job
=
an executable unit/run of work

Dataset
=
logical reusable collection of data

Table
=
one possible structured representation of a dataset

Data Product
=
a managed data asset with consumers, ownership,
documentation, quality expectations, and usable interfaces

Internal Tooling
=
software that helps engineers build, operate, debug,
or maintain the data system
```

### Why This Is the Solution

A Data Engineer does not merely "move rows."

The role includes building and operating systems that make data:

- available
- usable
- reliable
- maintainable
- understandable
- reusable

The same dataset can therefore have:

```text
source
→ ingestion pipeline
→ transformation job
→ curated table
→ data product
→ consumers
```

The production distinction is important: a one-time script can transform data, but a production data system also needs ownership, failure handling, documentation, and operational discipline.

---

## Question 02 — Trace One Order Through the Data Lifecycle

**Difficulty:** Basic

**Primary Topic:** Topic 02 — Data Lifecycle from Sources to Consumers

**Concepts Tested:**
- generation
- ingestion
- storage
- transformation
- serving
- consumption
- archival/deletion
- source and consumer
- metadata

### Problem

A customer places an order on an e-commerce website.

Trace the order through the complete lifecycle from creation to end-of-life.

Your answer must identify:

```text
Generation
Ingestion
Storage
Transformation
Serving
Consumption
Archival / Deletion
```

Also identify one likely producer and two possible consumers.

### How to Solve the Problem

1. Start at the business event that creates the data.
2. Identify the operational system where the event first exists.
3. Follow the movement into the analytical environment.
4. Identify where raw data is retained.
5. Identify transformations that make the data useful.
6. Identify how consumers access the result.
7. Finish with retention, archival, or deletion.

### Solution

A possible lifecycle is:

```text
Customer places order
        ↓
Order service / operational database
        ↓
Ingestion
        ↓
Raw / landing storage
        ↓
Transformation
        ↓
Curated analytical dataset
        ↓
Serving layer
        ↓
BI / Finance / ML / Operations
        ↓
Retention / archival / deletion
```

One producer:

```text
Order service
```

Possible consumers:

```text
Finance
Operations
ML team
```

The stages are:

1. **Generation:** the order service creates the order record.
2. **Ingestion:** the data engineering system extracts or receives the data.
3. **Storage:** the data is stored in an analytical platform.
4. **Transformation:** the raw order is cleaned, standardized, deduplicated, or aggregated.
5. **Serving:** a curated table, analytical model, or other access layer makes it usable.
6. **Consumption:** Finance, BI, Operations, or ML consumes the result.
7. **Archival/deletion:** data follows retention and lifecycle rules.

### Why This Is the Solution

Data does not begin when the Data Engineer touches it.

The lifecycle starts in the business system that generates the information.

The architectural lesson is:

```text
source characteristics
→ ingestion design
→ storage
→ transformation
→ serving
→ consumer requirements
```

A production engineer must understand the entire path because failures can occur at any stage.

---

## Question 03 — Batch, Micro-Batch, or Streaming?

**Difficulty:** Basic

**Primary Topic:** Topic 03 — Batch, Micro-Batch, and Streaming

**Concepts Tested:**
- batch
- micro-batch
- streaming
- bounded/unbounded data
- freshness
- latency
- requirements-first thinking

### Problem

Classify each workload as primarily **batch**, **micro-batch**, or **streaming**.

1. Generate a monthly executive finance report.
2. Refresh a website analytics dashboard every five minutes.
3. Process fraud events continuously as they arrive.

Give one reason for each choice.

### How to Solve the Problem

For each use case ask:

```text
How fresh must data be?
How quickly must the consumer react?
Is the input bounded or continuously arriving?
Is the additional operational complexity justified?
```

### Solution

1. **Monthly finance report → Batch**
   - The requirement is periodic.
   - Data can be processed in a bounded window.
   - Low operational complexity is useful.

2. **Dashboard every five minutes → Micro-batch**
   - The consumer needs relatively fresh data.
   - A small scheduled interval may be sufficient.
   - Continuous processing may not provide enough business value to justify its extra complexity.

3. **Fraud events continuously → Streaming**
   - Events arrive continuously.
   - The consumer may need low-latency decisions.
   - Delaying processing into a large batch can reduce the usefulness of the system.

### Why This Is the Solution

The correct mode is not determined by fashion.

The sequence is:

```text
consumer requirement
→ freshness/latency need
→ workload characteristics
→ processing mode
```

Batch is not "old."

Streaming is not automatically "better."

Micro-batch can be a useful middle ground.

---

## Question 04 — Where Does the Transformation Happen?

**Difficulty:** Basic

**Primary Topic:** Topic 04 — ETL, ELT, and Reverse ETL

**Concepts Tested:**
- Extract
- Transform
- Load
- ETL
- ELT
- transformation location

### Problem

Two pipelines are described.

**Pipeline A**

```text
Source database
   ↓
Python transformation
   ↓
Analytical database
```

**Pipeline B**

```text
Source database
   ↓
Raw analytical storage
   ↓
SQL transformation
   ↓
Curated table
```

Identify which is ETL and which is ELT.

### How to Solve the Problem

Ignore the programming language.

Ask only:

> **Does transformation happen before loading into the analytical target, or after loading?**

### Solution

**Pipeline A = ETL**

```text
Extract
  ↓
Transform
  ↓
Load
```

The transformation happens before the analytical destination receives the transformed result.

**Pipeline B = ELT**

```text
Extract
  ↓
Load
  ↓
Transform
```

Raw data is loaded first, and transformation happens inside or against the analytical platform afterward.

### Why This Is the Solution

The defining distinction is **where transformation occurs**.

It is not:

```text
Python = ETL
SQL = ELT
```

A Python program can participate in ELT.

A SQL-based transformation can also be part of an ETL architecture.

The architecture name follows the transformation location.

---

## Question 05 — OLTP or OLAP?

**Difficulty:** Basic

**Primary Topic:** Topic 05 — OLTP vs OLAP Workloads

**Concepts Tested:**
- OLTP
- OLAP
- point lookup
- aggregation
- operational vs analytical workload

### Problem

Classify each query as primarily OLTP or OLAP.

**Query A**

```sql
SELECT *
FROM customers
WHERE customer_id = 42;
```

**Query B**

```sql
SELECT country, SUM(amount)
FROM orders
GROUP BY country;
```

Explain why.

### How to Solve the Problem

Look at:

- how many rows the query may touch
- whether the query changes state
- whether it retrieves a specific entity
- whether it summarizes a large population

### Solution

**Query A → OLTP**

It is a selective point lookup for a specific customer.

**Query B → OLAP**

It may scan many orders and aggregate them by country.

The key difference is:

```text
OLTP
→ targeted operational work

OLAP
→ broad analytical work
```

### Why This Is the Solution

Both are SQL.

The difference is the workload shape.

A point lookup often needs:

```text
small amount of data
+
predictable access
+
low latency
```

An analytical aggregation can require:

```text
large scan
+
grouping
+
aggregation
+
more resources
```

That workload difference is the foundation for later platform and storage decisions.

---

## Question 06 — Warehouse, Lake, or Lakehouse?

**Difficulty:** Basic

**Primary Topic:** Topic 06 — Warehouse, Lake, and Lakehouse Architectures

**Concepts Tested:**
- warehouse
- lake
- lakehouse
- schema-on-write
- schema-on-read
- structured vs broad data

### Problem

Consider three organizations:

**A.** A small company mainly needs SQL dashboards over structured business data.

**B.** An AI company stores PDFs, images, raw JSON, logs, and other files before deciding how every dataset will be analyzed.

**C.** A company wants object-storage-based data plus stronger table management semantics and the potential to use multiple analytical engines.

Identify the architecture that may fit each scenario:

```text
Warehouse
Lake
Lakehouse
```

### How to Solve the Problem

Ask:

1. Is the workload primarily structured SQL analytics?
2. Is broad raw-data flexibility important?
3. Are managed table semantics and open table formats important?

### Solution

**A → Warehouse may fit strongly.**

The workload is primarily structured analytics with SQL-oriented consumption.

**B → Lake may fit strongly.**

Object storage and broad data-type flexibility are important.

**C → Lakehouse may fit.**

The organization wants object-storage flexibility plus table-management capabilities and potential multi-engine access through open table formats.

### Why This Is the Solution

These are architecture patterns, not universal product categories.

A warehouse emphasizes:

```text
structured analytics
+
managed analytical platform
```

A lake emphasizes:

```text
flexible object storage
+
broad data types
```

A lakehouse emphasizes:

```text
object storage
+
managed table semantics
+
analytical usability
```

Actual production systems can combine patterns.

---

## Question 07 — Bronze, Silver, Gold, or Quarantine?

**Difficulty:** Basic

**Primary Topic:** Topic 07 — Medallion Bronze, Silver, Gold Layers

**Concepts Tested:**
- Bronze
- Silver
- Gold
- quarantine
- ingestion metadata
- business logic
- grain

### Problem

Assign each item to the most appropriate layer:

1. `_ingested_at`
2. raw source `country = " india "`
3. standardized `country = "India"`
4. deduplicated order records
5. invalid record with `amount = "abc"`
6. `daily_revenue_by_country`

### How to Solve the Problem

Use the layer questions:

```text
Bronze:
What did the source give us?

Silver:
What data can we trust and reuse?

Gold:
What does the consumer need?

Quarantine:
What failed validation and needs investigation?
```

### Solution

1. `_ingested_at` → **Bronze**
2. raw `country = " india "` → **Bronze**
3. standardized country → **Silver**
4. deduplicated orders → **Silver**
5. invalid `amount = "abc"` → **Quarantine**
6. `daily_revenue_by_country` → **Gold**

### Why This Is the Solution

Bronze preserves source values and ingestion context.

Silver establishes a trusted, typed, deduplicated, conformed boundary.

Gold contains business-oriented consumer datasets.

Quarantine isolates invalid records without silently discarding them.

A key principle is:

> Put logic where the responsibility is stable, reusable, and appropriate for downstream consumers.

---

## Question 08 — SLI, SLO, SLA, and Freshness

**Difficulty:** Basic

**Primary Topic:** Topic 08 — SLAs, Freshness, Latency, and Data Consumers

**Concepts Tested:**
- data consumer
- freshness
- latency
- SLI
- SLO
- SLA

### Problem

Finance says:

> "Yesterday's revenue should be available by 07:00 UTC on at least 99% of days."

Identify:

1. The consumer.
2. An SLI.
3. An SLO.
4. What an SLA would represent.
5. Whether the statement is about freshness or only pipeline runtime.

### How to Solve the Problem

Translate the business statement into:

```text
consumer
→ measurable property
→ target
```

Then separate the internal target from any formal commitment.

### Solution

1. **Consumer:** Finance.
2. **Possible SLI:** whether `daily_revenue` was complete and available by 07:00 UTC, or delivery delay in minutes.
3. **SLO:** `daily_revenue` should meet the stated 07:00 UTC delivery requirement on at least 99% of expected days.
4. **SLA:** a formal service commitment made to another party, potentially with defined escalation or consequences.
5. The statement is a **consumer delivery/freshness-style requirement**, not simply a pipeline-runtime requirement.

### Why This Is the Solution

The simple memory aid is:

```text
SLI = what we measure
SLO = what level we target
SLA = formal commitment
```

The important engineering lesson is that:

```text
pipeline completed
```

is not the same as:

```text
consumer requirement satisfied
```

---

# Part II — Moderate

## Question 09 — Turn a Script Into a Production Data Asset

**Difficulty:** Moderate

**Primary Topic:** Topic 01 — What Data Engineers Build

**Concepts Tested:**
- one-off script vs production pipeline
- dataset
- job
- data product
- owners
- consumers
- documentation
- versioning
- quality guarantees

### Problem

A developer has a Python script that reads an order CSV and produces `revenue.csv`.

It works on the developer's laptop.

Finance wants to rely on this output every morning.

The current setup has:

```text
No owner
No documented schema
No stated grain
No quality checks
No rerun procedure
No versioning policy
No consumer definition
```

Explain what must change before you would treat this as a production-oriented data product.

### How to Solve the Problem

Compare the current script with the characteristics of a managed data asset.

Ask:

```text
Who owns it?
Who consumes it?
What does a row mean?
What inputs does it depend on?
How often does it run?
What happens when it fails?
How can it be rerun?
What quality expectations exist?
What happens when the schema changes?
```

### Solution

The script should become part of a managed pipeline with at least:

```text
Defined source
Defined job/run behavior
Defined dataset schema
Defined grain
Owner
Consumers
Documentation
Validation/quality checks
Logging and error handling
Repeatable rerun behavior
Versioned transformation logic
Change-management expectations
```

A useful data-product description could be:

```text
Dataset:
daily_revenue

Owner:
Finance Data Team

Consumer:
Finance

Grain:
one row per business date and country

Source:
orders dataset

Refresh:
daily

Quality:
defined completeness and correctness checks

Failure behavior:
alert + rerun procedure

Change policy:
documented schema/business-rule changes
```

### Why This Is the Solution

A production data system is more than executable code.

The important progression is:

```text
script
→ pipeline
→ production pipeline
→ data platform capability
→ data product
```

The same data can become much more valuable once its meaning, ownership, reliability, and operational behavior are explicit.

---

## Question 10 — Source Characteristics Drive the Architecture

**Difficulty:** Moderate

**Primary Topic:** Topic 02 — Data Lifecycle from Sources to Consumers

**Concepts Tested:**
- source systems
- volume
- velocity
- variety
- schema stability
- mutable data
- pull vs push
- PII
- consumers

### Problem

A company has these sources:

```text
1. Customer database with updates and deletes
2. Payment events arriving continuously
3. Daily CSV file from a partner
4. Healthcare document archive containing sensitive information
```

Consumers include:

```text
Finance
Operations
Fraud
Analytics
Regulatory reporting
```

Explain what source characteristics should influence the ingestion and lifecycle design.

### How to Solve the Problem

For every source identify:

```text
volume
velocity
variety
schema stability
mutable vs append-only
push vs pull
sensitivity
consumer requirements
```

Then connect those characteristics to architecture.

### Solution

**1. Customer database**

Characteristics:

- mutable
- updates/deletes possible
- structured
- likely accessed through pull or another controlled extraction mechanism

The pipeline must account for changes rather than assuming append-only records.

**2. Payment events**

Characteristics:

- high velocity
- potentially unbounded
- event-oriented
- likely needs lower latency for fraud or operations

A streaming or event-driven ingestion pattern may fit depending on requirements.

**3. Partner CSV**

Characteristics:

- bounded
- batch-oriented
- predictable delivery window
- schema may be relatively stable but must still be validated

A scheduled batch ingestion pattern is reasonable.

**4. Healthcare documents**

Characteristics:

- unstructured
- potentially large variety
- sensitive
- strong access/classification requirements
- retention and governance matter

Storage and ingestion must include appropriate security and lifecycle controls.

### Why This Is the Solution

Source characteristics directly influence design.

The wrong abstraction is:

```text
"All sources are just files or tables."
```

A Data Engineer instead asks:

```text
How fast does data arrive?
How does it change?
What format is it?
How stable is its schema?
How sensitive is it?
Who consumes it?
```

That source-boundary reasoning is foundational.

---

## Question 11 — Choose the Processing Mode

**Difficulty:** Moderate

**Primary Topic:** Topic 03 — Batch, Micro-Batch, and Streaming

**Concepts Tested:**
- batch
- micro-batch
- streaming
- event time
- processing time
- latency
- freshness
- cost
- operational complexity

### Problem

A retailer has these requirements:

### Requirement A

A monthly finance package.

### Requirement B

Inventory status should refresh every two minutes.

### Requirement C

Fraud events should be evaluated continuously.

For each, choose a processing mode and explain one trade-off.

Then explain why processing time and event time are not necessarily identical for Requirement C.

### How to Solve the Problem

Start from the consumer.

For each workload:

```text
required freshness
required latency
data arrival pattern
cost
operational complexity
```

For the streaming case, distinguish:

```text
when the event happened
```

from:

```text
when the processor received it
```

### Solution

**Requirement A → Batch**

The workload is periodic and bounded.

Trade-off:

```text
lower operational complexity
but higher data freshness delay
```

**Requirement B → Micro-batch**

A two-minute refresh interval may provide sufficient freshness without full always-on streaming.

Trade-off:

```text
simpler than full streaming
but introduces scheduled delay
```

**Requirement C → Streaming**

Continuous arrival and rapid fraud decisions make low-latency processing valuable.

Trade-off:

```text
lower latency
but higher operational complexity
```

For event time:

```text
Event time
=
when the payment actually happened
```

while:

```text
Processing time
=
when the processing system handled the event
```

An event can occur at 10:00 and arrive at 10:03.

### Why This Is the Solution

Processing mode is a requirements decision.

Streaming also introduces complexity around:

- ordering
- late events
- state
- backlog
- always-on compute
- operational response

The architecture should pay that complexity only when the consumer requirement justifies it.

---

## Question 12 — ETL, ELT, or EtLT?

**Difficulty:** Moderate

**Primary Topic:** Topic 04 — ETL, ELT, and Reverse ETL

**Concepts Tested:**
- ETL
- ELT
- EtLT
- PII removal
- complex preprocessing
- raw preservation
- replayability
- source and target constraints

### Problem

A bank receives a large file containing:

```text
customer_id
name
email
address
transactions
```

The organization has these requirements:

1. Sensitive customer fields must not land in the general analytics area.
2. The transaction section requires complex parsing.
3. The organization wants as much raw history as is appropriate after required controls.
4. Analysts want flexible analytical transformations later.

Should you use pure ETL, pure ELT, or a hybrid/EtLT approach?

### How to Solve the Problem

Identify which work must happen before landing and which work can safely happen later.

Ask:

```text
What must be removed/protected before storage?
What must be parsed before the data becomes usable?
What transformations are flexible analytical logic?
```

### Solution

A **hybrid/EtLT-style approach** is reasonable.

For example:

```text
Source
  ↓
Extract
  ↓
Light transformation / protection
  ├── remove or protect sensitive fields as required
  └── perform necessary preprocessing/parsing
  ↓
Load
  ↓
Analytical storage
  ↓
Further transformations
```

This preserves the useful part of ELT while recognizing that some controls and preprocessing belong before the data reaches a broader analytical boundary.

### Why This Is the Solution

ETL is still useful when:

- PII needs to be removed before landing
- strict target constraints exist
- complex parsing must happen before loading
- source data is unsuitable for direct landing

ELT is attractive when:

- storage is scalable
- compute can scale
- raw or source-aligned data can be safely retained
- analysts need flexible transformation

EtLT helps describe a practical middle ground.

---

## Question 13 — Read Replica or Analytical Replication?

**Difficulty:** Moderate

**Primary Topic:** Topic 05 — OLTP vs OLAP Workloads

**Concepts Tested:**
- OLTP
- OLAP
- read replica
- CDC
- replication lag
- resource isolation
- rows scanned
- latency
- concurrency

### Problem

An e-commerce company's PostgreSQL production database handles customer traffic.

During business hours, analysts run queries that scan millions of order rows and calculate long historical aggregates.

The team is considering:

```text
Option A: Read replica
Option B: CDC into an analytical system
Option C: HTAP
```

Explain what each option solves and why a read replica is not automatically the same as an analytical platform.

### How to Solve the Problem

First identify the workload:

```text
production OLTP
+
large analytical scans
```

Then ask what resource or architectural boundary each option provides.

### Solution

**Option A — Read replica**

A read replica moves some read traffic away from the primary.

Benefits:

- reduces some primary read load
- can isolate certain read queries

Limitations:

- the replica still has to process the analytical query
- large scans can still consume substantial resources
- replication lag can exist
- it is not automatically a specialized analytical engine

**Option B — CDC into an analytical system**

CDC captures changes from the operational system and propagates them to an analytical platform.

Benefits:

- separates analytical workload from OLTP resources
- can maintain relatively fresh analytical data
- avoids repeatedly extracting the entire source

Costs:

- pipeline complexity
- change handling
- additional platform operations

**Option C — HTAP**

HTAP attempts to support transactional and analytical workloads in one broader system.

Potential benefit:

- reduce the need for completely separate systems in some architectures

Challenges:

- workload interference can remain a concern
- operational and analytical requirements are difficult to balance
- it is not a universal replacement for an analytical platform

### Why This Is the Solution

A read replica changes **where reads happen**.

CDC-based analytical replication changes **where the analytical workload happens**.

The distinction is:

```text
read replica
=
separate copy of the operational data source

CDC analytical platform
=
separate analytical workload boundary
```

The correct architecture depends on:

- rows scanned
- QPS
- concurrency
- latency
- analytical query complexity
- freshness requirement
- cost

---

## Question 14 — Choose the Analytical Platform

**Difficulty:** Moderate

**Primary Topic:** Topic 06 — Warehouse, Lake, and Lakehouse Architectures

**Concepts Tested:**
- warehouse
- lake
- lakehouse
- schema-on-write
- schema-on-read
- storage/compute separation
- governance
- catalog
- data swamp

### Problem

A mid-size organization has:

```text
structured business tables
event JSON
documents
some ML workloads
multiple analytics teams
```

The team wants to avoid an unmanaged collection of files.

It also wants:

```text
strong governance
discoverability
reuse
reasonable cost
```

Which architectural family should the team evaluate first and why?

### How to Solve the Problem

Do not choose from brand names.

Evaluate:

```text
data types
workloads
schema needs
governance
consumer needs
team skills
cost
operational complexity
```

Then compare the three patterns.

### Solution

A **lakehouse should be seriously evaluated**, but the decision should remain requirements-driven.

Why?

The organization has:

- structured data
- semi-structured data
- documents
- ML workloads
- multiple analytical consumers
- a governance requirement

A lake can provide flexible object storage, but unmanaged storage risks becoming a data swamp.

A warehouse can provide strong structured analytics and governance, but broad document/raw-data requirements may make a lake-style foundation useful.

A lakehouse can combine:

```text
object-storage foundation
+
managed table semantics
+
analytical processing
+
open table formats
+
potential multi-engine access
```

The final decision still depends on:

- team skills
- cost
- required governance
- desired engine independence
- data scale
- operational maturity

### Why This Is the Solution

The correct reasoning is not:

```text
"lakehouse is modern"
```

It is:

```text
broad data types
+
analytical needs
+
ML
+
governance
+
reuse
```

lead to a platform comparison in which lakehouse capabilities may fit well.

The phrase **"may fit"** is important.

Architecture is a system of trade-offs.

---

## Question 15 — Where Should These Transformations Go?

**Difficulty:** Moderate

**Primary Topic:** Topic 07 — Medallion Bronze, Silver, Gold Layers

**Concepts Tested:**
- Bronze
- Silver
- Gold
- Quarantine
- grain
- metadata
- business logic
- conformance
- replayability

### Problem

For an order pipeline, decide where each rule belongs:

1. Add `_batch_id`.
2. Preserve `country = " india "`.
3. Trim whitespace.
4. Convert `amount` into a numeric representation.
5. Deduplicate by `order_id`, keeping the latest version.
6. Join a country reference table.
7. Calculate `daily_revenue_by_country`.
8. Classify a customer as `high_value`.
9. Store `amount = "abc"` with its rejection reason.
10. State that `silver_orders` has one row per order.

### How to Solve the Problem

Use:

```text
Bronze = source preservation + ingestion metadata
Silver = trusted/conformed reusable data
Gold = consumer-oriented business logic
Quarantine = failed validation
```

Then ask whether a rule defines the dataset contract itself.

### Solution

| Rule | Layer |
|---|---|
| Add `_batch_id` | Bronze |
| Preserve raw country | Bronze |
| Trim whitespace | Silver |
| Numeric conversion | Silver |
| Deduplication | Silver |
| Country reference join | Silver |
| Daily revenue aggregation | Gold |
| High-value classification | Gold or an appropriate shared business-model layer |
| Invalid amount + reason | Quarantine |
| One row per order | Silver contract / grain definition |

### Why This Is the Solution

The most important distinction is between:

```text
technical normalization
```

and:

```text
consumer/business semantics
```

Silver should establish a trusted reusable representation.

Gold should express consumer-oriented business meaning.

The grain statement belongs to the Silver contract because it defines what one row represents.

---

## Question 16 — Write a Measurable Freshness SLO

**Difficulty:** Moderate

**Primary Topic:** Topic 08 — SLAs, Freshness, Latency, and Data Consumers

**Concepts Tested:**
- consumer
- freshness
- SLI
- SLO
- completeness
- measurement window
- population
- calculation

### Problem

Finance consumes:

```text
daily_revenue
```

They say:

> "We need yesterday's complete data every morning."

The current observed values are:

```text
Expected rows = 100,000
Received rows = 99,700
Newest usable event = 05:30 UTC
Current time = 07:00 UTC
```

Write a measurable freshness SLO and calculate:

1. Freshness.
2. Completeness.

Assume a completeness target of at least 99.5% for this exercise.

### How to Solve the Problem

Freshness:

```text
current time - newest usable event time
```

Completeness:

```text
received / expected × 100
```

Then write the SLO with:

```text
dataset
metric
population/window
target
```

### Solution

Freshness:

```text
07:00 - 05:30
=
90 minutes
```

Completeness:

```text
99,700 / 100,000 × 100
=
99.7%
```

A suitable exercise SLO could be:

```text
For expected daily production datasets,
daily_revenue should have freshness under 120 minutes
and completeness of at least 99.5%.
```

Observed result:

```text
Freshness:
90 min
Target:
< 120 min
PASS

Completeness:
99.7%
Target:
>= 99.5%
PASS
```

### Why This Is the Solution

The SLO is measurable because it defines:

```text
what
+
how measured
+
population
+
target
```

A vague statement such as:

```text
"daily_revenue should be fresh"
```

is not sufficient.

The consumer requirement becomes useful only after converting it into an observable signal and target.

---

# Part III — Hard

## Question 17 — Centralized Team, Embedded Engineers, or Data Mesh?

**Difficulty:** Hard

**Primary Topic:** Topic 01 — What Data Engineers Build

**Concepts Tested:**
- centralized data team
- embedded engineers
- data mesh
- domain ownership
- data as a product
- self-service platform
- federated governance
- trade-offs

### Problem

A company has grown from 100 to 2,000 employees.

It now has:

```text
20 business domains
multiple analytics teams
ML teams
many reusable datasets
repeated data incidents
```

The central data team controls most pipelines, but domain teams complain that:

- they do not own the meaning of their datasets
- changes take too long
- central engineers do not understand every domain
- teams repeatedly request similar pipelines

The company is considering:

```text
A. Keep a centralized data team
B. Embed Data Engineers in domains
C. Move toward a data-mesh-style model
```

Analyze the options.

### How to Solve the Problem

Use:

```text
Context
→ problem
→ ownership
→ platform needs
→ governance
→ team capability
→ trade-offs
```

Do not choose based on the popularity of a model.

### Solution

### Option A — Centralized

Potential strengths:

- standardized platform
- centralized expertise
- easier common tooling
- centralized governance

Potential risks:

- domain knowledge may be weaker
- central team becomes a bottleneck
- ownership can remain distant from consumers

### Option B — Embedded

Potential strengths:

- strong domain understanding
- faster domain-specific decisions
- closer relationship with business consumers

Potential risks:

- duplicated tooling
- inconsistent standards
- fragmented architecture
- governance can become difficult

### Option C — Data Mesh Style

A data-mesh-style approach can combine:

```text
domain ownership
+
data as a product
+
self-service platform
+
federated governance
```

Potential strengths:

- domains own their data products
- common platform capabilities reduce duplicated infrastructure
- governance is shared rather than completely centralized

Potential risks:

- higher organizational complexity
- requires mature domain teams
- governance must actually work
- self-service platform capability must exist
- data-product ownership must be real, not only a label

### Why This Is the Solution

There is no universal winner.

The architecture should follow organizational requirements and maturity.

A useful decision is often not:

```text
centralized OR decentralized
```

but:

```text
Which responsibilities should be centralized?
Which should be owned by domains?
Which capabilities should be platformized?
How will governance remain consistent?
```

That is the deeper architectural problem.

---

## Question 18 — Trace and Control a Multi-Source Lifecycle

**Difficulty:** Hard

**Primary Topic:** Topic 02 — Data Lifecycle from Sources to Consumers

**Concepts Tested:**
- lifecycle
- source analysis
- mutable data
- event streams
- files
- volume/velocity/variety
- PII
- metadata
- data contracts
- validation
- lineage
- failure points

### Problem

A bank wants one analytical customer platform fed by:

```text
Core banking database
Payments event stream
Daily partner CSV
Customer-service SaaS API
```

Consumers include:

```text
Fraud
Finance
Regulatory reporting
Analysts
RAG search for internal documents
```

Identify the important lifecycle and control questions before designing the pipeline.

### How to Solve the Problem

For each source:

1. Identify how data is generated.
2. Classify the source.
3. Determine whether it is mutable or append-only.
4. Determine its velocity and variety.
5. Determine how access occurs.
6. Identify data sensitivity.
7. Identify the relevant consumer.
8. Put validation and metadata at meaningful boundaries.

### Solution

The architecture should begin with a source inventory.

| Source | Key Characteristics | Design Questions |
|---|---|---|
| Core banking DB | Structured, mutable | How are updates/deletes captured? What is the safe extraction pattern? |
| Payments stream | High velocity, event-oriented | What freshness/latency is required? How is ordering handled? |
| Partner CSV | Bounded, batch, schema-dependent | How is file delivery verified? What validation is required? |
| SaaS API | External dependency | What pull behavior, rate/availability constraints, and schema changes exist? |

Lifecycle:

```text
Source generation
   ↓
Ingestion
   ↓
Raw storage
   ↓
Transformation
   ↓
Curated data
   ↓
Serving
   ↓
Consumers
```

Controls should include:

- source data contracts where appropriate
- source metadata
- ingestion/batch identity
- schema validation
- quality checks at meaningful stages
- lineage
- ownership
- PII classification
- retention information
- failure detection

### Why This Is the Solution

A source-to-consumer design is not simply:

```text
extract everything
→ put it somewhere
```

The source's behavior determines the pipeline.

The bank's consumer requirements also differ:

```text
Fraud
→ low latency

Regulatory
→ completeness + correctness + deadline

Analysts
→ flexible access

RAG
→ document freshness + retrieval usability
```

Validation should not exist only at the final output because an upstream problem can be much easier to isolate closer to where it occurs.

---

## Question 19 — Backlog, Arrival Rate, State, and Hybrid Processing

**Difficulty:** Hard

**Primary Topic:** Topic 03 — Batch, Micro-Batch, and Streaming

**Concepts Tested:**
- arrival rate
- processing rate
- backlog
- state
- ordering
- late data
- streaming
- batch transformation
- hybrid architecture

### Problem

A SaaS company receives:

```text
10,000 events/second
```

During a normal period, the streaming processor can handle:

```text
12,000 events/second
```

During a traffic spike, incoming traffic rises to:

```text
20,000 events/second
```

The processor remains at:

```text
12,000 events/second
```

The team also needs a daily historical recomputation.

Explain:

1. What happens to the backlog?
2. Why does processing rate vs arrival rate matter?
3. What additional complexity appears around state and ordering?
4. Would a hybrid architecture make sense?

### How to Solve the Problem

Compare:

```text
arrival rate
vs
processing rate
```

Then examine the state needed to process events correctly and the need for historical recomputation.

### Solution

During the spike:

```text
Arrival = 20,000/sec
Processing = 12,000/sec
```

So the instantaneous backlog growth is:

```text
20,000 - 12,000
=
8,000 events/sec
```

The stream cannot keep up during that period.

Backlog therefore grows until:

- traffic falls
- processing increases
- the architecture scales
- or some other recovery strategy takes effect

State and ordering become important if processing requires:

```text
per-customer history
windows
deduplication
ordering
aggregations
```

Late and out-of-order events can require event-time-aware handling.

A hybrid architecture may make sense:

```text
Streaming ingestion
        ↓
Durable event storage
        ↓
Low-latency processing
        +
scheduled batch recomputation
        ↓
Consumer outputs
```

### Why This Is the Solution

Streaming does not mean infinite capacity.

A critical operational invariant is:

```text
processing rate >= arrival rate
```

over the sustained period that matters to the workload.

If:

```text
arrival > processing
```

backlog grows.

The daily historical recomputation is another reason not to force every computation into one always-on path.

---

## Question 20 — Design the Reverse ETL Control Loop

**Difficulty:** Hard

**Primary Topic:** Topic 04 — ETL, ELT, and Reverse ETL

**Concepts Tested:**
- reverse ETL
- operational analytics
- CRM
- authoritative system
- validation
- API rate limits
- synchronization conflicts
- idempotency
- ownership

### Problem

An e-commerce company computes customer lifetime value in its analytical platform.

Marketing wants the value written back into its CRM.

The sync has these risks:

```text
wrong customer value
CRM API rate limit
CRM user edits same customer
duplicate updates
warehouse value changes later
```

Design a safe reverse ETL flow.

### How to Solve the Problem

Think of reverse ETL as an operational boundary.

Identify:

```text
source of analytical truth
target system
validation
identity mapping
rate limits
conflict rules
idempotency
auditability
ownership
```

### Solution

A reasonable flow is:

```text
Analytical customer dataset
        ↓
Validate records
        ↓
Select approved changes
        ↓
Map customer identity
        ↓
Dry-run / compare where appropriate
        ↓
Rate-limited sync
        ↓
CRM
        ↓
Record outcome / audit
```

Controls:

### Wrong data

Validate:

- customer identity
- expected data types
- acceptable ranges
- business rules

### API rate limits

Use controlled batching and rate-aware execution.

### Synchronization conflicts

Define which system is authoritative for each field.

For example:

```text
LTV
→ analytical system authoritative

Phone number
→ CRM authoritative
```

### Duplicate updates

Use idempotent write behavior where supported and track a stable sync identity.

### Ownership

The analytical team may own the dataset.

The CRM/application team may own the target system.

The process needs an explicit operational owner.

### Why This Is the Solution

Reverse ETL is not:

```text
export CSV
→ upload
```

It is a data flow from an analytical environment into an operational system.

That means the target can affect real business operations.

Correctness, rate limits, synchronization conflicts, and ownership therefore matter.

---

## Question 21 — Protect Production OLTP From Analytical Workloads

**Difficulty:** Hard

**Primary Topic:** Topic 05 — OLTP vs OLAP Workloads

**Concepts Tested:**
- OLTP
- OLAP
- QPS
- rows scanned
- latency
- concurrency
- production resource contention
- read replica
- CDC
- HTAP

### Problem

A bank's production database handles:

```text
3,000 point-lookups/second
```

with strict customer-facing latency expectations.

Analysts begin running queries that scan:

```text
hundreds of millions of transaction rows
```

and group by:

```text
country + month + transaction type
```

During those queries, application latency increases.

Evaluate:

```text
read replica
CDC into analytical platform
HTAP
```

and explain what workload metrics should be monitored.

### How to Solve the Problem

First characterize each workload:

```text
Operational:
many small requests, low latency, high concurrency

Analytical:
large scans, joins, aggregations, resource-intensive
```

Then evaluate architecture against the measured workload.

### Solution

The first architectural conclusion is:

> The workloads should not automatically compete for the same production resources.

A **read replica** may help by shifting read traffic away from the primary, but large analytical queries can still consume substantial resources on the replica.

A **CDC-based analytical platform** provides stronger workload isolation:

```text
Production OLTP
      ↓
CDC
      ↓
Analytical platform
      ↓
Large scans / BI / analysis
```

This is often attractive when the primary database must protect operational traffic.

**HTAP** is another architecture to evaluate when an organization wants transactional and analytical workloads in a unified system and the technology can meet both requirements.

Metrics to measure include:

```text
QPS
rows scanned
query latency
concurrency
read/write ratio
query complexity
transaction latency
replication lag
```

### Why This Is the Solution

The problem is not "analytics is bad."

It is:

```text
large analytical work
+
resource-sensitive operational workload
+
shared system
=
possible interference
```

A Data Engineer therefore measures workload characteristics rather than guessing from database names.

---

## Question 22 — Warehouse, Lake, or Lakehouse Under Real Constraints

**Difficulty:** Hard

**Primary Topic:** Topic 06 — Warehouse, Lake, and Lakehouse Architectures

**Concepts Tested:**
- warehouse
- lake
- lakehouse
- data types
- storage/compute separation
- open formats
- engine independence
- governance
- catalogs
- team skills
- cost
- vendor lock-in
- ML

### Problem

A mid-size retailer has:

```text
structured orders
JSON clickstream events
product images
documents
ML workloads
BI workloads
```

The team has:

```text
strong SQL skills
moderate cloud skills
limited distributed-systems expertise
```

The company wants:

```text
reasonable operating complexity
governance
ML flexibility
potential multi-engine access
```

Compare warehouse, lake, and lakehouse and recommend what should be evaluated first.

### How to Solve the Problem

Build a decision matrix:

```text
data types
workloads
team skills
governance
ML
cost
operational complexity
engine independence
lock-in
```

### Solution

### Warehouse

Strong fit for:

```text
structured BI
SQL
managed analytics
```

Potential concern:

```text
broad image/document/raw-data requirements
```

### Lake

Strong fit for:

```text
object storage
broad data types
raw retention
flexibility
```

Potential concern:

```text
governance
table semantics
operational complexity
data swamp risk
```

### Lakehouse

Strong fit for:

```text
broad data
object storage
managed tables
ML
analytics
open table formats
potential engine independence
```

Potential concern:

```text
higher platform complexity
requires governance and catalog discipline
team must operate more components
```

Given the combination of:

```text
multiple data types
ML
BI
governance
multi-engine aspirations
```

a lakehouse is a strong candidate to evaluate.

But the decision should explicitly account for the team's limited distributed-systems skills.

### Why This Is the Solution

A technically capable architecture can still be operationally inappropriate.

The senior-engineer question is:

> Can the team reliably operate the platform that the requirements demand?

The architecture should therefore be justified by:

```text
requirements
+
team capability
+
cost
+
governance
+
future needs
```

not by product popularity.

---

## Question 23 — Rebuild Silver and Gold After a Bug

**Difficulty:** Hard

**Primary Topic:** Topic 07 — Medallion Bronze, Silver, Gold Layers

**Concepts Tested:**
- Bronze
- Silver
- Gold
- replayability
- backfill
- idempotency
- quarantine
- grain
- business logic
- deduplication

### Problem

A company discovers that for the last six months:

```text
Silver incorrectly kept duplicate order records.
```

Because of that:

```text
Gold daily revenue
```

is too high.

The source system is difficult to re-extract historically.

Bronze contains retained source-aligned records.

Explain how you would repair the historical outputs without re-extracting the source.

### How to Solve the Problem

Use the dependency direction:

```text
Bronze
→ Silver
→ Gold
```

Ask:

```text
Can Bronze reproduce the required inputs?
Can Silver be rebuilt deterministically?
Is the Gold output derived from Silver?
```

### Solution

1. Keep Bronze unchanged.
2. Fix the Silver deduplication rule.
3. Define the Silver grain explicitly:

```text
one row per logical order
```

4. Define deterministic latest-version selection.
5. Rebuild Silver from retained Bronze for the affected historical period.
6. Validate the new Silver:
   - duplicates
   - row counts
   - grain
   - rejected/quarantined records
7. Rebuild Gold from the corrected Silver.
8. Compare old and new Gold outputs.
9. Record the logic change and affected period.
10. Verify rerunning the process does not create new duplicates.

### Why This Is the Solution

This is replayability:

```text
Bronze
  ↓
new Silver logic
  ↓
new Gold
```

without going back to the source.

Idempotency matters because rebuilding the same period multiple times should not create additional logical records.

The architecture is valuable precisely because the raw-preserving boundary remains available.

---

## Question 24 — The Pipeline Succeeded, but the SLO Failed

**Difficulty:** Hard

**Primary Topic:** Topic 08 — SLAs, Freshness, Latency, and Data Consumers

**Concepts Tested:**
- freshness
- latency
- completeness
- pipeline success vs service success
- SLO
- latency budget
- upstream dependency
- source SLA
- error budget

### Problem

Finance has an SLO:

```text
daily_revenue
available by 07:00 UTC on at least 99% of expected days
```

The pipeline reports:

```text
exit code = 0
run duration = 40 minutes
```

But the source data arrived very late.

The end-to-end timing was:

```text
Source delay       30 min
Ingestion           5 min
Silver             10 min
Gold                8 min
Serving             2 min
Buffer               5 min
```

The source is contractually expected to be available by 06:00 UTC, but arrived at 06:30 UTC.

Determine:

1. Whether the pipeline execution was successful.
2. Whether the consumer SLO could still be breached.
3. The total budget.
4. Which dependency caused the problem.
5. What should happen next.

### How to Solve the Problem

Separate:

```text
execution state
```

from:

```text
consumer service state
```

Then sum the latency components.

### Solution

The pipeline execution may be considered **successful** if the process completed normally:

```text
exit code = 0
```

But the consumer SLO can still be breached.

Total timing contribution:

```text
30 + 5 + 10 + 8 + 2 + 5
=
60 minutes
```

The timing budget is exactly 60 minutes.

However, because the source itself arrived late relative to its expected delivery time, the downstream system has consumed available budget before processing could fully execute.

The primary dependency issue is:

```text
upstream source delivery
```

The team should:

1. confirm the measurement
2. record the dependency delay
3. evaluate consumer impact
4. determine whether the finance SLO was breached
5. communicate status
6. investigate the source dependency
7. review the latency budget
8. assess error-budget consumption
9. consider whether the upstream contract or downstream architecture needs improvement

### Why This Is the Solution

The key lesson is:

```text
Pipeline Success
≠
Data Reliability Success
```

The process can execute correctly while the data is still too late for the consumer.

A downstream SLO cannot ignore the reliability constraints of the systems it depends on.

---

# Part IV — Advanced

## Question 25 — Design an Enterprise Data Operating Model

**Difficulty:** Advanced

**Primary Topic:** Topic 01 — What Data Engineers Build

**Concepts Tested:**
- data products
- domain ownership
- centralized team
- embedded engineers
- data mesh
- self-service platform
- federated governance
- architecture
- DataOps
- software engineering
- ML/AI data pipelines

### Problem

A 5,000-person organization has:

```text
30 business domains
500 analytical datasets
multiple ML teams
multiple AI/RAG applications
central cloud infrastructure
```

The current problem is:

```text
Central team:
- overloaded
- slow to respond

Domain teams:
- understand the data well
- duplicate pipelines
- duplicate quality logic
- disagree on definitions
```

Design an organizational model that addresses:

```text
domain ownership
platform reuse
governance
data-product quality
ML/AI needs
```

You must compare:

```text
centralized
embedded
data mesh
```

and propose a responsibility split.

### How to Solve the Problem

Do not ask:

> "Which organizational model is best?"

Ask:

```text
Which responsibilities require domain knowledge?
Which capabilities should be platformized?
Which standards must remain consistent?
Who owns data products?
Who maintains shared tooling?
How is governance enforced?
```

Then compare the options.

### Solution

A plausible architecture is a **hybrid operating model influenced by data-mesh principles**.

For example:

```text
Central Platform Team
    |
    +-- ingestion capabilities
    +-- storage/compute foundations
    +-- developer tooling
    +-- common reliability capabilities
    +-- shared governance mechanisms
    |
    +------------------------------+
                                   |
Domain Data Teams                 |
    |                             |
    +-- own domain datasets       |
    +-- own data products         |
    +-- define business meaning   |
    +-- manage domain consumers   |
    +-- maintain domain pipelines |
```

Governance can be federated:

```text
central standards
+
domain-specific accountability
```

Data products should have:

- owner
- consumers
- documentation
- schema
- grain
- quality expectations
- freshness expectations
- change policy

ML/AI teams can consume reusable domain data products while platform teams provide common infrastructure for:

- training-data pipelines
- feature pipelines
- retrieval pipelines
- embedding pipelines

### Why This Is the Solution

The strongest response does not eliminate centralization.

It distinguishes:

```text
platform capability
```

from:

```text
domain data ownership
```

A fully centralized model can become a bottleneck.

A fully decentralized model can create fragmented tooling and inconsistent standards.

A mesh-style model adds organizational requirements:

```text
real domain ownership
+
data-as-a-product mindset
+
self-service platform
+
federated governance
```

Without those foundations, renaming teams "data mesh" does not solve the underlying problems.

---

## Question 26 — Design the End-to-End Banking Data Architecture

**Difficulty:** Advanced

**Primary Topic:** Topic 02 — Data Lifecycle from Sources to Consumers

**Concepts Tested:**
- source systems
- lifecycle
- batch and streaming
- mutable data
- pull/push
- PII
- metadata
- validation
- storage
- transformation
- serving
- regulators
- ML
- RAG

### Problem

Design a conceptual banking data architecture for:

```text
Core banking
Payments
Cards
Customer platform
Regulatory files
Internal documents
```

Consumers:

```text
Fraud
Finance
Regulators
Analysts
ML
RAG
```

Requirements include:

```text
fraud needs low-latency information
finance needs reliable daily reporting
regulators need complete and auditable datasets
RAG needs approved documents
```

Provide the end-to-end architecture and explain different processing modes and controls.

### How to Solve the Problem

Start from source characteristics.

Then map each major source to:

```text
ingestion mode
storage
transformation
consumer
```

Then add:

```text
metadata
classification
ownership
validation
retention
```

### Solution

A conceptual architecture:

```text
Core Banking ------\
Payments -----------\
Cards ---------------+--> Ingestion --> Analytical Storage
Customer Platform --/
Regulatory Files ---/
Documents ----------/

Analytical Storage
       |
       +--> low-latency path --> Fraud
       |
       +--> daily analytical path --> Finance
       |
       +--> controlled reporting path --> Regulators
       |
       +--> analytical datasets --> Analysts / ML
       |
       +--> document pipeline --> RAG
```

Processing choices may differ:

```text
Payment events
→ streaming or low-latency processing

Daily finance reporting
→ batch

Regulatory file ingestion
→ batch + validation

Internal documents
→ file/document ingestion + processing
```

Controls include:

- PII classification
- access boundaries
- source ownership
- ingestion metadata
- batch/run identity
- schema validation
- completeness checks
- lineage
- retention
- explicit serving contracts

### Why This Is the Solution

A banking platform is not one workload.

The correct architecture recognizes multiple clocks:

```text
fraud clock
finance clock
regulatory clock
AI/document clock
```

The lifecycle is therefore shared, but the processing and serving requirements can differ by consumer.

---

## Question 27 — Lambda, Kappa, or Hybrid?

**Difficulty:** Advanced

**Primary Topic:** Topic 03 — Batch, Micro-Batch, and Streaming

**Concepts Tested:**
- streaming
- batch
- replay
- state
- ordering
- Lambda
- Kappa
- duplicated logic
- hybrid architecture
- historical recomputation

### Problem

A company needs:

```text
low-latency operational metrics
daily historical recomputation
ability to replay events
```

The team proposes:

### Architecture A

Lambda architecture:

```text
same source
→ batch path
→ speed path
→ combined result
```

### Architecture B

Kappa-style architecture:

```text
events
→ streaming system
→ replay the event history through the stream path
```

### Architecture C

Hybrid:

```text
streaming ingestion
+
batch transformation
```

Evaluate all three and explain which type of requirement each handles well.

### How to Solve the Problem

Compare:

```text
latency
historical recomputation
replay
logic duplication
operational complexity
state
```

### Solution

### Lambda

Potential strength:

- combines low-latency results with batch recomputation

Main weakness:

```text
duplicated logic
```

The same business transformation may need to exist in both speed and batch paths.

### Kappa

Potential strength:

- one dominant processing path
- replay can rebuild history if the event history is retained and the system supports the necessary replay model

Potential challenge:

- the streaming path must handle historical recomputation efficiently
- state and operational complexity can still be significant

### Hybrid

A practical design may be:

```text
Streaming ingestion
        ↓
Durable historical event store
        ↓
Low-latency consumer path
        +
Batch transformation/reprocessing path
```

This can avoid duplicating all ingestion while allowing different processing modes for different purposes.

### Why This Is the Solution

The question is not:

```text
Lambda or Kappa?
```

The real questions are:

```text
Do we need low latency?
Do we need historical recomputation?
How valuable is one processing path?
How expensive is duplicated logic?
How will replay work?
```

A hybrid design may be a practical fit when ingestion and downstream processing have different timing requirements.

---

## Question 28 — Design an E-Commerce Analytics and Reverse-ETL System

**Difficulty:** Advanced

**Primary Topic:** Topic 04 — ETL, ELT, and Reverse ETL

**Concepts Tested:**
- ETL
- ELT
- EtLT
- raw history
- replayability
- backfill
- business transformations
- reverse ETL
- CRM
- API rate limits
- sync conflicts
- ownership
- idempotency

### Problem

An e-commerce company receives:

```text
orders
customers
payments
clickstream events
product data
```

It needs:

```text
BI reporting
ML datasets
customer lifetime value
CRM synchronization
```

Six months later, the business changes the definition of customer lifetime value.

At the same time:

```text
CRM API has a rate limit
CRM agents can manually edit fields
```

Design an ETL/ELT/reverse-ETL architecture and explain how the six-month rule change should be handled.

### How to Solve the Problem

Separate the problem into:

```text
source ingestion
analytics transformation
historical replay
operational sync
```

Then identify where each transformation belongs.

### Solution

A plausible architecture:

```text
Sources
   ↓
Extract / Ingest
   ↓
Raw retained analytical data
   ↓
Reusable analytical transformations
   ↓
Curated datasets
   ↓
Business models
   ↓
BI / ML

Business-approved customer metrics
   ↓
validation
   ↓
rate-limited reverse ETL
   ↓
CRM
```

For the LTV rule change:

```text
Keep raw history
      ↓
Update transformation logic
      ↓
Rebuild historical analytical output
      ↓
Recompute LTV
      ↓
Validate
      ↓
Synchronize approved results to CRM
```

The CRM sync must define field ownership.

Example:

```text
Analytical LTV
→ analytical system authoritative

Manual CRM notes
→ CRM authoritative
```

Rate limits require controlled throughput.

Idempotency reduces duplicate updates.

### Why This Is the Solution

The most valuable architectural property is replayability.

The organization should not need to ask the original operational system for six months of data again merely because a business rule changed.

Reverse ETL adds a second operational boundary:

```text
analytical truth
→ operational system
```

That boundary must be treated as a controlled system integration, not as a simple export.

---

## Question 29 — Mixed OLTP/OLAP Architecture Decision

**Difficulty:** Advanced

**Primary Topic:** Topic 05 — OLTP vs OLAP Workloads

**Concepts Tested:**
- OLTP
- OLAP
- workload isolation
- QPS
- rows scanned
- latency
- concurrency
- normalized/denormalized
- row/column orientation
- read replica
- CDC
- HTAP
- production reliability

### Problem

A ride-sharing company has:

```text
Millions of trip transactions
High-concurrency mobile requests
Real-time operational queries
Years of historical analytics
ML feature generation
```

The engineering team asks whether one database should be used for everything.

Design the workload architecture and explain:

```text
operational database
analytical system
read replica
CDC
HTAP
row-oriented storage
column-oriented storage
normalized vs denormalized models
```

### How to Solve the Problem

Start with workloads.

Separate:

```text
small operational reads/writes
```

from:

```text
large analytical scans and aggregations
```

Then connect each workload to an appropriate storage/modeling pattern.

### Solution

A strong conceptual design is:

```text
Mobile / transactional requests
        ↓
OLTP system
        |
        +--> operational tables
        |
        +--> CDC
              ↓
        Analytical platform
              |
              +--> large scans
              +--> aggregations
              +--> ML datasets
```

A read replica can be useful for:

```text
selected read isolation
```

but it does not automatically create a purpose-built analytical system.

HTAP may be evaluated if the organization wants one broader system to support both workload categories and the technology satisfies the requirements.

Storage considerations:

### OLTP

Row-oriented storage often fits well because operational queries commonly access specific entities or complete records.

Normalized modeling can reduce duplication and support consistent current-state updates.

### OLAP

Column-oriented storage can be effective for projection-heavy analytical queries because only required columns may need to be read and compressed/processed efficiently.

Analytical models are often more denormalized and aggregation-friendly.

### Metrics

Monitor:

```text
OLTP QPS
transaction latency
analytical rows scanned
analytical query latency
concurrency
replication lag
read/write ratio
```

### Why This Is the Solution

The problem is workload contention.

The architecture should avoid asking:

> "Can one database technically execute both queries?"

and instead ask:

> "Can one system reliably serve both workloads under the required latency, concurrency, and resource constraints?"

That is the workload-driven architecture mindset.

---

## Question 30 — ADR: Choose the Analytical Platform

**Difficulty:** Advanced

**Primary Topic:** Topic 06 — Warehouse, Lake, and Lakehouse Architectures

**Concepts Tested:**
- architecture selection
- warehouse
- lake
- lakehouse
- open formats
- engine independence
- catalog
- governance
- cost
- team skills
- ML
- vendor lock-in
- ADR

### Problem

A 500-person company has:

```text
structured transactional data
website events
documents
images
ML workloads
multiple analytics teams
```

The organization wants:

```text
reasonable cost
strong governance
multiple query engines
less dependence on one processing engine
```

Write an ADR using:

```text
Context
Requirements
Constraints
Options
Trade-offs
Decision
Consequences
Open Questions
```

Compare:

```text
warehouse
lake
lakehouse
```

### How to Solve the Problem

Do not make the brand name the decision.

Build the decision from:

```text
data types
workloads
team capabilities
governance
cost
engine independence
vendor lock-in
operational complexity
```

### Solution

### Context

The organization needs one analytical platform serving both structured analytics and broader ML/document workloads.

### Requirements

- structured SQL analytics
- raw/broad data support
- ML flexibility
- governance
- multiple consumers
- potential multi-engine access

### Constraints

- finite engineering capacity
- operating complexity must remain manageable
- cost must be controlled
- governance must be enforceable

### Options

**Warehouse**

Strengths:

- strong SQL
- structured analytics
- managed experience

Risks:

- may be less natural for broad document/raw-data use depending on architecture
- potential platform coupling

**Lake**

Strengths:

- flexible object storage
- broad data types
- potentially lower storage-layer lock-in

Risks:

- governance burden
- data-swamp risk
- table semantics may require additional systems

**Lakehouse**

Strengths:

- object-storage foundation
- managed table semantics
- open table formats
- potential multi-engine access
- suitable for analytics and ML

Risks:

- operational complexity
- governance/catalog still required
- compatibility is not automatically universal

### Decision

The ADR may reasonably select a lakehouse-oriented architecture as the leading option **under these assumptions**, with explicit governance and catalog requirements.

### Consequences

Benefits:

- broad data support
- analytical reuse
- table semantics
- multi-engine potential

Costs:

- more operational complexity
- platform governance required
- engine compatibility must be verified

### Open Questions

- Which engines need to be supported?
- Which open table features are actually required?
- What is the team's operational maturity?
- What are the retention requirements?
- What level of lock-in is acceptable?

### Why This Is the Solution

The decision is justified by requirements rather than by hype.

The important architectural statement is:

> **The selected architecture is a consequence of data characteristics, consumer workloads, team capability, governance, cost, and interoperability requirements.**

---

## Question 31 — Redesign a Weak Medallion Platform

**Difficulty:** Advanced

**Primary Topic:** Topic 07 — Medallion Bronze, Silver, Gold Layers

**Concepts Tested:**
- Bronze
- Silver
- Gold
- quarantine
- replayability
- idempotency
- layer contracts
- grain
- ownership
- consumer-specific Gold
- data-product thinking
- architecture trade-offs

### Problem

A company has:

```text
20 source systems
200 downstream datasets
```

But all transformations happen inside:

```text
one enormous "analytics" table-building pipeline
```

Problems include:

```text
raw data overwritten
business logic mixed with ingestion
duplicate records
no quarantine
unclear grain
different consumers use different definitions
historical rebuilds are painful
```

Redesign the architecture using meaningful Bronze/Silver/Gold responsibilities.

### How to Solve the Problem

First identify what responsibility is currently mixed together.

Then establish:

```text
source-preserving boundary
trusted reusable boundary
consumer-specific boundary
invalid-data boundary
```

Then define contracts, ownership, and rebuild behavior.

### Solution

A conceptual redesign:

```text
Sources
   ↓
Ingestion
   ↓
Bronze
   |
   +--> raw values
   +--> _ingested_at
   +--> _source
   +--> _batch_id
   +--> source-file metadata
   |
   v
Validation
   | \
   |  \--> Quarantine
   |
   v
Silver
   |
   +--> typed
   +--> cleaned
   +--> deduplicated
   +--> conformed
   +--> explicit grain
   |
   +-------------------+
   |                   |
   v                   v
Gold A              Gold B
Finance             ML/Marketing
```

Contracts:

### Bronze

```text
source-preserving + ingestion metadata
```

### Silver

```text
validated
typed
deduplicated
conformed
clear grain
```

### Gold

```text
consumer-oriented business datasets
```

Quarantine:

```text
invalid record
+
reason
+
source metadata
```

Replay:

```text
Bronze
→ rebuild Silver
→ rebuild Gold
```

Idempotency:

```text
same logical input
+
same transformation
=
same logical result
```

Ownership should be explicit by layer/dataset.

### Why This Is the Solution

The redesign does not exist merely because "Medallion is standard."

It creates meaningful responsibility boundaries:

```text
capture
→ trust/conformance
→ consumer meaning
```

It also makes historical correction safer.

If a business rule changes:

```text
Bronze stays stable
Silver/Gold logic changes
downstream data is rebuilt
```

The architecture should not create unnecessary layers; every boundary should solve a real problem.

---

## Question 32 — Design a Consumer-Centric Reliability Contract

**Difficulty:** Advanced

**Primary Topic:** Topic 08 — SLAs, Freshness, Latency, and Data Consumers

**Concepts Tested:**
- data consumer
- freshness
- latency
- completeness
- accuracy
- availability
- SLI
- SLO
- SLA
- latency budget
- error budget
- upstream dependency
- source SLA
- dataset tiering
- p95/p99
- run metadata
- pipeline vs service success

### Problem

A company operates a critical Gold dataset:

```text
fraud_features
```

Consumers say:

```text
Fraud decisions are suffering because features can become stale.
```

The upstream payment source is expected to provide events within:

```text
10 minutes
```

The downstream pipeline stages are estimated as:

```text
Source            10 min
Ingestion          5 min
Silver             15 min
Gold               15 min
Serving             5 min
Buffer              10 min
```

The dataset is classified as:

```text
Critical
```

The team wants a formal reliability contract.

Design:

```text
consumer requirement
SLIs
SLOs
60-minute latency budget
upstream dependency expectation
dataset tier
error budget
run metadata
incident response
```

### How to Solve the Problem

Work backward from the fraud consumer.

Ask:

```text
How fresh must features be?
What latency matters?
What does completeness mean?
What does availability mean?
How will we measure success?
What upstream commitment is required?
What happens when the budget is consumed?
```

Then check whether the supplied latency components fit inside the end-to-end requirement.

### Solution

## Consumer

```text
Fraud detection system
```

## Business consequence

Stale features can reduce the usefulness of fraud decisions.

## Core SLI

A primary SLI should be:

```text
feature freshness
```

Additional SLIs may include:

```text
event-to-consumer latency
completeness
availability
```

For an event-latency requirement, a percentile such as:

```text
p95 event-to-consumer latency
```

can be useful if tail latency matters.

## SLO

A concrete target must be based on the actual fraud decision requirement.

For example, as an exercise:

```text
95% of valid fraud events should reach the consumer
within an agreed threshold.
```

The threshold should be negotiated from the business requirement rather than copied from another system.

## Latency budget

The provided budget is:

```text
Source            10
Ingestion          5
Silver             15
Gold               15
Serving             5
Buffer              10
----------------------
Total               60
```

So the total end-to-end target is:

```text
60 minutes
```

## Upstream dependency

The source is expected within:

```text
10 minutes
```

Therefore the downstream SLO cannot simply assume instantaneous source availability.

The source delivery expectation is part of the reliability chain.

## Dataset tier

```text
Critical
```

Therefore the system may justify:

- strong alerting
- explicit ownership
- active incident response
- tighter reliability controls

## Error budget

If the chosen SLO is:

```text
99% successful windows
```

then conceptually:

```text
1%
=
allowed unreliability
```

The team should define how that budget is consumed and what operational action occurs as it is depleted.

## Run metadata

At minimum capture:

```text
run_id
start time
end time
rows in/out by layer
maximum relevant event timestamp
SLO result
```

## Incident response

When an SLO is breached:

```text
Confirm measurement
      ↓
Classify failure
      ↓
Check source dependency
      ↓
Check latency budget
      ↓
Check completeness/accuracy
      ↓
Assess consumer impact
      ↓
Mitigate
      ↓
Record incident
      ↓
Fix root cause
```

### Why This Is the Solution

The core lesson is:

```text
consumer
→ requirement
→ SLI
→ SLO
→ dependency
→ budget
→ operational response
```

The dataset is not reliable simply because:

```text
pipeline exit code = 0
```

Reliability is a service property experienced by the consumer.

Because the dataset is critical, the operational burden should be stronger than for a best-effort analytical export.

The exact SLO values must come from business requirements and actual system capabilities.

---

# Final Module Review

The 32 questions should collectively force you to connect:

```text
What Data Engineers Build
        ↓
Data Lifecycle
        ↓
Batch / Micro-Batch / Streaming
        ↓
ETL / ELT / Reverse ETL
        ↓
OLTP / OLAP
        ↓
Warehouse / Lake / Lakehouse
        ↓
Bronze / Silver / Gold
        ↓
Consumers
        ↓
Freshness / Latency / Completeness
        ↓
SLI / SLO / SLA
        ↓
Architecture Decision
```

Before moving to Module 2.2, confirm:

- [ ] I can explain what a Data Engineer builds.
- [ ] I can distinguish a dataset, table, job, pipeline, and data product.
- [ ] I can trace data from generation to consumer.
- [ ] I can identify source characteristics that affect architecture.
- [ ] I can choose batch, micro-batch, or streaming from requirements.
- [ ] I can explain event time vs processing time.
- [ ] I can distinguish ETL, ELT, and EtLT.
- [ ] I can explain replayability and backfills.
- [ ] I can explain reverse ETL risks.
- [ ] I can classify OLTP and OLAP workloads.
- [ ] I can explain why large analytics can interfere with operational workloads.
- [ ] I can compare read replicas, CDC-based analytical replication, and HTAP conceptually.
- [ ] I can compare warehouse, lake, and lakehouse.
- [ ] I can explain schema-on-write and schema-on-read.
- [ ] I can explain storage/compute separation.
- [ ] I can explain data swamps, catalogs, governance, and open formats.
- [ ] I can explain Bronze, Silver, Gold, and Quarantine.
- [ ] I can define grain.
- [ ] I can explain replayability and idempotency.
- [ ] I can decide where a transformation belongs.
- [ ] I can identify a data consumer.
- [ ] I can distinguish freshness, latency, completeness, accuracy, and availability.
- [ ] I can distinguish SLI, SLO, and SLA.
- [ ] I can write a measurable SLO.
- [ ] I can build a 60-minute latency budget.
- [ ] I can reason about upstream dependency limitations.
- [ ] I can explain an error budget.
- [ ] I can tier datasets by business criticality.
- [ ] I can reason about centralized, embedded, and data-mesh-style organization.
- [ ] I can design an end-to-end architecture and justify trade-offs.
- [ ] I can explain my decisions aloud without relying on memorized technology names.

## Final Solving Standard

For future architecture problems, aim to move through:

```text
Scenario
   ↓
Problem definition
   ↓
Sources
   ↓
Consumers
   ↓
Data characteristics
   ↓
Workload
   ↓
Processing mode
   ↓
ETL / ELT choice
   ↓
Platform
   ↓
Layering
   ↓
Validation / failure handling
   ↓
Consumer requirements
   ↓
SLOs
   ↓
Dependencies
   ↓
Trade-offs
   ↓
Decision
   ↓
Consequences
```

The target is not:

> "I know the terminology."

The target is:

> **"I can reason about a real Data Engineering system."**
