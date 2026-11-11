# Design Case 07 — Batch Analytics Platform

> **G5 — Data Engineering System Design Interviews**  
> **Case 07:** Design the analytics platform for a company with several operational systems and SaaS tools; Finance needs daily reports by 07:00.

This is a complete, production-oriented Data Engineering system-design interview case. It is designed to take a learner from first-principles reasoning to a credible senior/staff-level 45-minute interview performance.

> **Source basis:** This module follows the supplied Topic 07 Claude Code specification, including its mandatory case framing, required design areas, deep dives, practice workflow, interview drills, and coverage audit.

## 1. Case Overview

### The interview prompt

> **Design the analytics platform for a company with several operational systems and SaaS tools; Finance needs daily reports by 07:00.**

The prompt is intentionally incomplete. The candidate is expected to discover the requirements before selecting technologies.

### What this case tests

The interviewer is primarily testing:

- end-to-end ELT thinking;
- source analysis and ingestion strategy;
- incremental ingestion and CDC;
- warehouse/lake/lakehouse reasoning;
- storage layering;
- dimensional modelling;
- dbt-style transformations;
- orchestration and dependencies;
- data-quality gates;
- write–audit–publish;
- SLA design;
- late data and restatements;
- backfills;
- semantic-layer thinking;
- metric consistency;
- cost controls;
- production reliability;
- communication and trade-off reasoning.

### The central mental model

```text
Requirements
    ↓
Scope
    ↓
Estimates
    ↓
Source analysis
    ↓
Ingestion strategy
    ↓
Storage architecture
    ↓
Data modelling
    ↓
Transformation
    ↓
Orchestration
    ↓
Quality gates
    ↓
Publishing
    ↓
Serving / Semantic Layer
    ↓
SLA / Reliability
    ↓
Backfills / Late Data
    ↓
Cost / Governance
    ↓
Evolution
```

Do not memorize one vendor architecture. Learn the reasoning chain.

## 2. Why This Case Matters

Batch analytics is often underestimated because the system does not need sub-second latency. In a production Finance environment, however, the difficult problems are frequently:

- correctness;
- historical consistency;
- source reliability;
- incremental change capture;
- late-arriving data;
- restatements;
- auditability;
- reproducibility;
- daily deadlines;
- backfills without damaging production;
- consistent metrics across dashboards;
- cost control.

A strong answer therefore does not stop at:

```text
Sources → Warehouse → BI
```

It explains:

```text
How data enters
→ how it becomes trustworthy
→ how historical truth is preserved
→ how transformations remain reproducible
→ how the 07:00 SLA is protected
→ how corrections are handled
→ how Finance knows what was published
→ how the platform evolves
```

## 3. Prerequisites

You should already be comfortable with:

- SQL;
- Python fundamentals;
- relational databases;
- ETL/ELT concepts;
- basic data modelling;
- batch processing;
- object storage;
- orchestration concepts;
- data quality concepts;
- basic cloud/data-platform architecture;
- Topic 01 interview format and rubric;
- Topic 02 requirements clarification;
- Topic 03 estimation;
- Topic 04 reusable system-design framework;
- Topic 05 trade-offs;
- Topic 06 diagramming and communication.

This case applies those skills rather than replacing them.

## 4. What the Interviewer Is Testing

| Dimension | What good performance demonstrates |
|---|---|
| Requirements | You clarify ambiguity before designing |
| Estimates | Numbers influence architecture |
| Source analysis | You protect OLTP and respect SaaS constraints |
| Ingestion | You choose full, incremental, CDC, or connectors deliberately |
| Storage | You explain warehouse/lake/lakehouse trade-offs |
| Modelling | You define grain and business entities |
| Transformations | You build dependency-aware, testable models |
| Orchestration | You make execution predictable and recoverable |
| Quality | You gate publication rather than merely alerting |
| SLA | You design backward from 07:00 |
| Late data | You have a correction and restatement strategy |
| Backfill | You can safely recompute two years |
| Semantic layer | Metrics have centralized definitions |
| Cost | You understand the major cost drivers |
| Reliability | You can detect, contain, recover, validate, and prevent |
| Security | Finance/PII access is controlled |
| Communication | You draw and explain without losing the story |
| Trade-offs | You make requirement-driven decisions |
| Evolution | You explain what changes at 10× scale |

# 5. Step 1 — Clarify the Requirements

Start by saying:

> "Before choosing the architecture, I want to clarify the reporting SLA, source characteristics, scale, correctness requirements, retention, consumers, and how historical corrections should work."

### Questions to ask

1. How many operational systems are there?
2. Which databases are transactional?
3. Which SaaS systems are involved?
4. Are file feeds also required?
5. How much data arrives each day?
6. What is the expected annual growth?
7. Is daily freshness enough for all consumers?
8. Must Finance reports be available exactly at 07:00 or before 07:00?
9. What happens if one source is late?
10. Is yesterday's report allowed to be provisional?
11. How long must history be retained?
12. Are corrections/restatements expected?
13. Does Finance require auditability of published numbers?
14. Are there PII or regulated fields?
15. How many analysts/dashboard users query the data?
16. Are there executive dashboards with stricter latency?
17. Is ad-hoc analytics in scope?
18. Do consumers need raw historical data?
19. What is the expected backfill frequency?
20. What availability is required outside the daily reporting window?

### The key interview principle

Do not ask questions for the sake of asking questions. Ask questions that can change the architecture.

# 6. Functional Requirements

The platform should:

- ingest operational database data;
- ingest SaaS data;
- ingest file data where required;
- preserve historical records;
- support initial loads;
- support incremental ingestion;
- support CDC where appropriate;
- normalize/conform source data;
- build analytics-ready datasets;
- support dimensional models;
- support daily Finance reports;
- support dashboards;
- support controlled ad-hoc analytics;
- maintain consistent metric definitions;
- support corrections and restatements;
- support historical reprocessing;
- provide audit evidence for Finance;
- provide lineage and ownership information.

### MVP boundary

A reasonable interview MVP could be:

- five operational sources;
- five SaaS sources;
- daily ingestion;
- durable raw history;
- conformed/silver layer;
- dimensional gold layer;
- Finance semantic layer;
- daily 07:00 publication;
- quality gates;
- reconciliation;
- backfill capability;
- monitoring and alerting.

### Future extensions

Defer unless requirements justify them:

- real-time analytics;
- ML workloads;
- self-service ingestion;
- multi-region disaster recovery;
- reverse ETL;
- streaming dashboards.

The point is not to build everything. The point is to build enough to satisfy the stated requirements safely.

# 7. Non-Functional Requirements

## SLA

Finance reports must be ready by 07:00.

## Correctness

Financial metrics must be reproducible, reconcilable, and auditable.

## Freshness

The candidate should clarify the freshness of each source and each consumer. Daily Finance reporting does not automatically imply that every dataset should be refreshed only once per day.

## Reliability

A source or transformation failure must not silently produce incorrect Finance data.

## Scalability

The platform should handle growth without requiring a complete redesign.

## Recoverability

Failed runs, late data, historical corrections, and backfills must be supported.

## Retention

The system should support the required historical reporting period.

## Security

Least-privilege access, encryption, auditability, classification, and appropriate controls for Finance/PII data.

## Cost

Storage, compute, query, data movement, and operational overhead must be considered.

## Auditability

The organization should be able to answer:

- what data was used;
- which transformation version produced a report;
- what checks passed;
- what was restated;
- who published/approved the result;
- what changed between versions.

# 8. Hidden Requirements

The phrase **Finance needs daily reports by 07:00** carries more information than it appears to.

### Finance implies

- correctness;
- reproducibility;
- reconciliation;
- auditability;
- controlled restatements;
- stable definitions;
- traceability.

### Multiple operational systems imply

- heterogeneous schemas;
- different update semantics;
- source-specific extraction;
- source protection;
- incremental loading;
- possible CDC.

### Multiple SaaS systems imply

- API rate limits;
- pagination;
- authentication;
- connector failures;
- schema drift;
- vendor outages;
- different incremental mechanisms.

### A 07:00 deadline implies

- an end-to-end SLA;
- a critical path;
- dependency management;
- buffer;
- freshness monitoring;
- early warning;
- failure recovery;
- explicit publication semantics.

### Historical reporting implies

- durable raw data;
- retention;
- reproducibility;
- backfills;
- correction strategy.

# 9. Assumptions

Use explicit assumptions in an interview. These are **illustrative**, not facts from the problem statement.

| Parameter | Illustrative assumption |
|---|---:|
| Operational sources | 5 |
| SaaS sources | 5 |
| Daily records | 100M |
| Average logical record | 1 KB |
| Annual growth | 30% |
| Historical retention | 7 years |
| Peak processing multiplier | 3× |
| Finance deadline | 07:00 |
| Target publish buffer | 15–30 minutes |

Always say:

> "I'll use these as working assumptions and adjust them if you give me different numbers."

# 10. Step 2 — Back-of-the-Envelope Estimates

Estimates should influence architecture.

## Daily storage

```text
100M records/day × 1 KB/record
≈ 100 GB/day raw logical volume
```

If compression is approximately 4:1:

```text
≈ 25 GB/day compressed
```

At 365 days:

```text
≈ 9.1 TB/year compressed
```

At seven years:

```text
≈ 63.9 TB compressed
```

This is deliberately an order-of-magnitude estimate. Real storage must also account for metadata, file overhead, table versions, replicas, temporary data, indexes, and retained raw data.

## Average record rate

```text
100,000,000 / 86,400
≈ 1,157 records/sec
```

A 3× peak multiplier gives:

```text
≈ 3,472 records/sec
```

### Python estimation example

```python
events_per_day = 100_000_000
record_size_bytes = 1_000
compression_ratio = 4
days_per_year = 365

raw_bytes_per_day = events_per_day * record_size_bytes
compressed_bytes_per_day = raw_bytes_per_day / compression_ratio
annual_compressed = compressed_bytes_per_day * days_per_year

print(f"Raw/day: {raw_bytes_per_day / 1e9:.2f} GB")
print(f"Compressed/day: {compressed_bytes_per_day / 1e9:.2f} GB")
print(f"Compressed/year: {annual_compressed / 1e12:.2f} TB")
```

### Architecture implications

If the workload is tens of gigabytes/day, a simple warehouse may be sufficient.

If it becomes hundreds of terabytes of retained history with heavy transformation and multiple consumers, a lakehouse or hybrid architecture may become attractive.

The estimate informs the choice; it does not determine it by itself.

# 11. Step 3 — Source Systems

## Operational databases

Typical examples:

- PostgreSQL;
- MySQL;
- ERP databases;
- order systems;
- billing systems.

Primary concerns:

```text
OLTP protection
+
incremental extraction
+
CDC where justified
+
source consistency
+
delete handling
```

Avoid repeatedly scanning a production OLTP database for large tables if incremental extraction or CDC can satisfy the requirement.

## SaaS systems

Examples:

- CRM;
- payments;
- marketing;
- support;
- subscription systems.

Key concerns:

- API rate limits;
- pagination;
- cursor semantics;
- incremental endpoints;
- authentication;
- deleted objects;
- vendor outages;
- schema changes.

## Files

Possible inputs:

- CSV;
- JSON;
- Parquet;
- partner files;
- scheduled exports.

Concerns:

- file arrival;
- naming conventions;
- schema validation;
- duplicate files;
- partial uploads;
- checksums;
- completeness.

## Source classification table

| Source | Typical extraction | Main risk |
|---|---|---|
| OLTP DB | CDC/incremental | Source load |
| SaaS API | Connector/API | Rate limits |
| File feed | Arrival-based | Missing/partial files |
| CDC stream | Change events | Ordering/lag |
| Manual Finance file | Controlled upload | Human error |

# 12. Step 4 — Ingestion Architecture

A useful conceptual flow is:

```text
Operational DBs ──┐
SaaS APIs ────────┼──> Ingestion / Connectors ──> Bronze / Raw
Files ────────────┘
```

The ingestion layer should:

- extract safely;
- preserve source information;
- capture metadata;
- maintain checkpoints;
- support retries;
- avoid duplicates;
- expose lag/freshness;
- isolate source failures.

## Full extraction

Use when:

- the dataset is small;
- the source has no useful incremental field;
- correctness is easier through complete replacement;
- the source explicitly supports efficient snapshots.

Do not use full extraction automatically for large high-change tables.

## Incremental extraction

Possible mechanisms:

- `updated_at`;
- monotonically increasing ID;
- source version;
- high-water mark;
- cursor/token.

## CDC

CDC is useful when:

- updates/deletes matter;
- source change volume is manageable;
- low-latency replication is desired;
- transaction-level changes are important.

Conceptually:

```text
OLTP
  |
  v
CDC Capture
  |
  v
Change Log
  |
  v
Bronze / Raw
  |
  v
Merge / Transform
```

## Managed connector vs custom ingestion

Prefer a managed connector when it reliably supports:

- source;
- authentication;
- incremental state;
- deletes;
- schema evolution;
- observability;
- retry semantics.

Custom ingestion is justified when:

- source behavior is unusual;
- connector capability is insufficient;
- transformation must happen during extraction for a valid reason;
- the connector's operational/cost model is unacceptable.

Do not build custom ingestion merely because writing an API client is easy.

# 13. Incremental Ingestion and Watermarks

A simple incremental query is:

```sql
SELECT *
FROM orders
WHERE updated_at > :last_watermark
  AND updated_at <= :current_watermark;
```

This is useful but incomplete.

### Failure modes

#### Clock skew

Source timestamps may not be perfectly aligned.

#### Same timestamp

Multiple records can share an `updated_at`.

#### Late update

A row can be modified after the watermark window.

#### Duplicate extraction

Retrying the same interval can extract the same records.

#### Deletes

A simple query may never observe deleted records.

#### Transaction ordering

A timestamp alone may not represent source commit ordering.

### More robust pattern

Use:

```text
Persisted checkpoint
+
overlap window where necessary
+
deduplication
+
idempotent write
+
source reconciliation
```

Example:

```text
Last successful watermark = 10:00

Read:
10:00 - overlap
        through
current upper bound

Deduplicate downstream
        ↓
Persist new checkpoint only after success
```

Never advance the checkpoint before the corresponding data is durably and correctly written.

# 14. CDC Design

A robust conceptual CDC path is:

```text
Source DB
   |
   | initial snapshot
   v
Raw Snapshot
   |
   +----------------------+
                          |
                          v
                     CDC Capture
                          |
                          v
                     Change Log
                          |
                          v
                    Raw CDC Events
                          |
                          v
                   Dedup / Ordering
                          |
                          v
                     Merge Logic
                          |
                          v
                   Curated Tables
```

The design must answer:

- How does initial snapshot hand off to CDC?
- How are inserts represented?
- How are updates represented?
- How are deletes represented?
- What is the ordering key?
- How is duplicate delivery handled?
- How is consumer replay performed?
- How are CDC gaps detected?
- How is source-to-target reconciliation performed?

Do not claim exactly-once semantics merely because the pipeline is transactional. In an interview, describe the actual mechanism that provides effective correctness.

# 15. Step 5 — Storage Architecture

## Warehouse

Strengths:

- SQL analytics;
- managed operations;
- BI ecosystem;
- predictable analytical workloads.

Potential limitations:

- storage/compute economics at very large scale;
- raw-data flexibility;
- specialized processing patterns.

## Data lake

Strengths:

- inexpensive durable storage;
- flexible raw retention;
- broad file/data-format support.

Potential challenges:

- governance;
- table semantics;
- query performance;
- operational discipline.

## Lakehouse

Strengths:

- durable object storage;
- table semantics;
- transactional updates;
- SQL and data-engineering workloads;
- flexible historical data.

Potential challenges:

- platform complexity;
- optimization;
- governance;
- team expertise.

### Decision criteria

```text
Volume
+
SQL workload
+
Freshness
+
Historical retention
+
Governance
+
Team expertise
+
Cost
+
Operational burden
```

Do not say one architecture is universally best.

# 16. Bronze / Silver / Gold

A useful logical layering is:

```text
Sources
   |
   v
Bronze / Raw
   |
   v
Silver / Conformed
   |
   v
Gold / Business
   |
   v
Semantic Layer
   |
   v
Finance / BI
```

### Bronze

Preserve source information and enough metadata to support:

- replay;
- debugging;
- audit;
- historical reconstruction.

### Silver

Perform:

- cleaning;
- typing;
- normalization where useful;
- deduplication;
- conformance;
- business-key alignment.

### Gold

Produce:

- facts;
- dimensions;
- marts;
- business-ready aggregates.

Do not mechanically create three layers if the workload does not require them. The layers are responsibilities, not mandatory vendor objects.

# 17. Step 6 — Data Modelling

## Grain

Define the grain before writing the fact table.

Example:

> One row in `fact_sales` represents one order line.

If the grain is unclear, the design is not ready.

### Why grain matters

Unclear grain causes:

- double counting;
- invalid joins;
- incorrect aggregates;
- inconsistent metrics.

## Star schema

```text
                 Dim Customer
                      |
                      |
Dim Product — Fact Sales — Dim Date
                      |
                      |
                  Dim Store
```

### Fact tables

Possible types:

- transaction fact;
- periodic snapshot;
- accumulating snapshot.

### Dimension tables

Typical dimensions:

- customer;
- product;
- date;
- geography;
- organization.

### Conformed dimensions

A customer or date dimension should have a stable meaning across marts so Finance does not receive different definitions of the same entity.

## Surrogate keys

Useful when dimension history is versioned and facts must refer to a particular dimensional version.

# 18. SCD Type 1

Type 1 overwrites the previous value.

Example:

```text
customer_id | segment
------------+----------
C123        | SMB
```

Later:

```text
customer_id | segment
------------+----------
C123        | Enterprise
```

Use Type 1 when historical changes are not analytically required.

Do not use Type 1 simply because it is easier if Finance needs historical point-in-time reporting.

# 19. SCD Type 2 — Mandatory Deep Dive

SCD Type 2 preserves historical versions.

Example:

```text
customer_sk | customer_id | segment     | valid_from | valid_to   | is_current
------------+-------------+-------------+------------+------------+-----------
101         | C123        | SMB         | 2025-01-01 | 2025-06-30 | false
205         | C123        | Enterprise  | 2025-07-01 | NULL       | true
```

### Why it exists

Suppose a customer was classified as SMB in March and Enterprise in August.

A report for March should use the March classification, not today's classification.

### Core invariants

For each business key:

- at most one current row;
- validity intervals should not overlap;
- `valid_from < valid_to` for closed intervals;
- historical rows should remain reproducible;
- surrogate keys identify versions.

### Point-in-time join

Conceptually:

```sql
SELECT
    f.order_id,
    f.order_date,
    f.customer_id,
    d.segment
FROM fact_orders f
JOIN dim_customer d
  ON f.customer_id = d.customer_id
 AND f.order_date >= d.valid_from
 AND f.order_date < COALESCE(d.valid_to, TIMESTAMP '9999-12-31');
```

### Common bugs

- two current rows;
- overlapping intervals;
- incorrect close date;
- using ingestion time instead of business-effective time;
- joining on current dimension state;
- duplicate source changes;
- late-arriving dimension changes.

### Senior-level answer

Do not just say "use SCD2." Explain:

```text
Business requirement
→ historical truth
→ versioned dimension
→ point-in-time join
→ validation invariants
→ late-data correction
```

# 20. Step 7 — Transformation Layer

A dbt-style conceptual structure is:

```text
Raw
 ↓
Staging
 ↓
Intermediate
 ↓
Marts
```

### Staging

Typical responsibilities:

- source-specific naming;
- type casting;
- basic filtering;
- source metadata.

Example:

```sql
SELECT
    order_id,
    customer_id,
    order_date,
    amount,
    updated_at,
    is_deleted
FROM {{ ref('raw_orders') }};
```

### Intermediate

Responsibilities:

- joins;
- business rules;
- conformance;
- reusable logic.

### Marts

Responsibilities:

- Finance-ready facts;
- dimensions;
- reporting aggregates;
- stable business semantics.

### Dependencies

A transformation should have an explicit dependency graph.

```text
stg_orders
    |
    v
int_orders_enriched
    |
    v
fact_orders
    |
    +----> finance_revenue
    +----> finance_margin
```

Tests, documentation, and lineage should follow the same dependency structure.

# 21. Incremental Models — Mandatory Deep Dive

Full refresh is conceptually simple:

```text
Read everything
→ transform everything
→ replace output
```

It becomes expensive as history grows.

Incremental processing instead:

```text
Identify affected data
→ transform affected data
→ merge/update target
```

Example:

```sql
MERGE INTO fact_orders AS target
USING staged_orders AS source
ON target.order_id = source.order_id

WHEN MATCHED THEN UPDATE SET
    amount = source.amount,
    updated_at = source.updated_at

WHEN NOT MATCHED THEN
    INSERT (order_id, customer_id, amount, updated_at)
    VALUES (source.order_id, source.customer_id, source.amount, source.updated_at);
```

### Why this is not only a performance problem

Incremental correctness must handle:

- updates;
- deletes;
- late records;
- duplicate records;
- corrections;
- restatements;
- schema changes;
- failed runs;
- backfills.

### Robust incremental design

```text
Watermark
+
Affected-window logic
+
Idempotent merge
+
Deduplication
+
Delete handling
+
Audit
+
Reconciliation
```

### Interview question

> "When would you choose a full refresh?"

Strong answer:

> "When the dataset is small enough, correctness is simpler through full recomputation, or the model's dependencies make affected-row identification more complex than a full rebuild. I would compare runtime, cost, SLA, and failure risk rather than treating incremental processing as automatically superior."

# 22. Step 8 — Orchestration

A conceptual DAG:

```text
Extract Sources
      |
      v
Load Bronze
      |
      v
Validate Bronze
      |
      v
Transform Silver
      |
      v
Run Quality Checks
      |
      v
Build Gold
      |
      v
Audit / Reconcile
      |
      v
Publish
      |
      v
Finance Dashboard
```

### Orchestration responsibilities

- dependencies;
- scheduling;
- retries;
- timeouts;
- idempotency;
- sensors/event triggers where appropriate;
- backfills;
- notifications;
- run history;
- SLA monitoring.

### Dependency rule

Do not publish downstream data merely because the upstream task succeeded.

The meaningful dependency is:

```text
Completed
+
Validated
+
Reconciled
```

when Finance correctness requires it.

# 23. The 07:00 SLA

Treat 07:00 as an end-to-end property.

Illustrative schedule:

```text
01:00–02:00  Source extraction
02:00–03:00  Bronze loading
03:00–04:30  Silver transformations
04:30–05:00  Quality validation
05:00–06:00  Gold marts
06:00–06:30  Audit/reconciliation
06:30–06:45  Publish
06:45–07:00  Safety buffer
```

These times are illustrative assumptions.

### Design backward from the deadline

```text
07:00 required
← 06:45 publish complete
← 06:30 reconciliation complete
← 06:00 gold complete
← 05:00 quality complete
← 03:00 silver complete
← 02:00 bronze complete
← 01:00 extraction complete
```

### Critical path

The candidate should identify:

- longest dependency chain;
- tasks with no slack;
- external dependencies;
- likely bottlenecks;
- early-warning thresholds.

A good SLA design includes a buffer. A pipeline that normally finishes at 06:59 is not a robust 07:00 pipeline.

# 24. Step 9 — Data Quality

Quality dimensions:

- completeness;
- uniqueness;
- validity;
- consistency;
- freshness;
- referential integrity;
- distribution anomalies.

Examples:

```sql
SELECT COUNT(*) AS null_order_ids
FROM orders
WHERE order_id IS NULL;
```

```sql
SELECT order_id, COUNT(*)
FROM orders
GROUP BY order_id
HAVING COUNT(*) > 1;
```

### Quality should be contextual

Not every anomaly must block every dataset.

For Finance-critical outputs, however, a known material correctness failure should normally block publication rather than silently alerting.

# 25. Quality Gates

Use:

```text
Raw
 |
 v
Quality Gate
 |  |  +--> FAIL → Quarantine / Alert / Stop
 |
 v
Transform
 |
 v
Quality Gate
 |  |  +--> FAIL → Do not publish
 |
 v
Audit
 |
 v
Publish
```

A quality gate should specify:

- what is checked;
- threshold;
- owner;
- action on failure;
- alert;
- recovery path.

Avoid:

> "We have data quality."

Instead say:

> "If yesterday's Finance revenue differs from the source reconciliation beyond an agreed threshold, the publish step is blocked and an incident is raised."

# 26. Write–Audit–Publish

This is central to the case.

### Write

Generate candidate output.

### Audit

Check:

- row counts;
- totals;
- source-to-target reconciliation;
- expected partitions;
- freshness;
- duplicate rates;
- null rates;
- anomaly thresholds.

### Publish

Expose the candidate only after the audit passes.

```text
Transform
   |
   v
Candidate Output
   |
   v
Audit / Reconcile
   |
   +---- FAIL → Do not publish
   |
   v
Publish
```

For Finance, this creates a controlled publication boundary.

### Why it matters

Without this boundary, a pipeline can be technically "successful" while publishing incorrect financial numbers.

# 27. Reconciliation

Examples:

- source order count vs warehouse order count;
- source revenue vs warehouse revenue;
- transaction count by day;
- partition completeness;
- expected vs observed file counts.

Example:

```sql
SELECT SUM(amount) AS source_revenue
FROM source_orders
WHERE order_date = CURRENT_DATE - INTERVAL '1 day';
```

versus:

```sql
SELECT SUM(amount) AS warehouse_revenue
FROM fact_orders
WHERE order_date = CURRENT_DATE - INTERVAL '1 day';
```

The reconciliation result should have an explicit tolerance or exact-match rule.

If a difference is acceptable, document why.

If it is not acceptable:

```text
Detect
→ Investigate
→ Block or qualify publication
→ Correct
→ Reconcile again
```

# 28. Step 10 — Late Data

Late data is normal in real systems.

Sources can be late because of:

- outages;
- API delays;
- source processing;
- clock differences;
- manual corrections;
- network problems;
- delayed files.

### Late-arriving fact

A record for Day 1 arrives on Day 2.

The system must:

1. detect it;
2. identify the affected partition;
3. recompute affected metrics;
4. audit;
5. restate if policy requires;
6. record the correction.

```text
Day 1 report
     |
     v
Day 2 late record
     |
     v
Detect affected date
     |
     v
Recompute
     |
     v
Audit
     |
     v
Restate / publish correction
```

### Watermark and grace period

A practical design may define:

```text
Expected data window
+
grace period
+
late-data correction path
```

Do not assume the grace period makes late data disappear. It only reduces the frequency of corrections.

# 29. Late-Arriving Dimensions

Suppose a fact arrives before the corresponding customer dimension version.

Possible strategies:

- temporary/unknown dimension key;
- delayed fact processing;
- subsequent correction;
- late dimension update.

The correct strategy depends on reporting requirements.

The important interview behavior is to recognize the dependency and explain how historical correctness is preserved.

# 30. Month-End Processing and Restatements

Finance reporting can have stricter correctness requirements than ordinary analytics.

Month-end may involve:

- late transactions;
- accounting adjustments;
- corrected source records;
- revised classifications;
- manual approved adjustments;
- restated historical periods.

A mature design preserves:

```text
Original published result
+
Correction reason
+
New result
+
Timestamp
+
Source/transformation version
+
Approval/audit information
```

Do not silently overwrite history when the business needs to understand what changed.

# 31. Step 11 — Semantic Layer

Different dashboards must not independently implement the same business metric.

Example failure:

```text
Dashboard A:
Revenue = SUM(order_amount)

Dashboard B:
Revenue = SUM(order_amount - refunds)

Dashboard C:
Revenue excludes cancelled orders
```

All three may be technically valid SQL and still produce organizational chaos.

### Semantic layer responsibilities

- metric definitions;
- dimensions;
- filters;
- ownership;
- documentation;
- tests;
- lineage;
- controlled versioning.

```text
Gold Data
    |
    v
Semantic Layer
    |
    +----> Finance Dashboard
    +----> Executive Dashboard
    +----> Analyst Queries
```

### Metric contract

A metric definition should answer:

```text
Name
Definition
Grain
Included records
Excluded records
Time basis
Owner
Source
Refresh expectation
Known caveats
```

# 32. Metric Consistency — Mandatory Deep Dive

### The problem

Finance says "revenue" and receives three answers.

This often happens because dashboards contain embedded business logic.

### Better design

```text
Conformed Data
      |
      v
Canonical Business Metrics
      |
      v
Semantic Layer
      |
      +----> Dashboard A
      +----> Dashboard B
      +----> Dashboard C
```

### Controls

- centralized definitions;
- semantic models;
- documentation;
- ownership;
- versioning;
- metric tests;
- reconciliation;
- lineage.

### Senior-level reasoning

A semantic layer is not just a BI convenience. It is an organizational control against divergent business logic.

If two teams genuinely need different definitions, name them differently and document the difference.

For example:

```text
Gross Revenue
Net Revenue
Recognized Revenue
```

are better than three dashboards all calling different calculations "Revenue."

# 33. Step 12 — Serving Layer

Consumers include:

- Finance BI;
- executive dashboards;
- analysts;
- controlled ad-hoc queries;
- downstream data products.

Choose serving based on:

- concurrency;
- query latency;
- cost;
- semantic requirements;
- security;
- workload isolation.

### Pre-aggregation

Useful when:

- queries repeatedly scan large datasets;
- dimensions and measures are predictable;
- SLA requires lower latency.

Do not pre-aggregate everything. Each additional aggregate is another object to maintain and validate.

# 34. Step 13 — Cost Optimization

Major cost drivers:

```text
Storage
+
Compute
+
Queries
+
Data movement
+
Operational complexity
```

Controls include:

- columnar formats;
- partition pruning;
- compression;
- incremental models;
- avoiding unnecessary full refreshes;
- compute scheduling;
- workload isolation;
- query optimization;
- pre-aggregation;
- retention/lifecycle policies;
- cost monitoring.

### Cost reasoning

```text
Requirement
→ workload
→ resource consumption
→ cost driver
→ optimization
→ SLA/correctness trade-off
```

The cheapest architecture is not automatically the best architecture.

For example, aggressively reducing compute may cause the 07:00 SLA to fail.

# 35. Step 14 — Security and Governance

Keep security proportional to the case.

Cover:

- least privilege;
- role-based access;
- service identities;
- encryption;
- PII classification;
- masking;
- audit logs;
- Finance dataset access;
- retention.

A useful trust model:

```text
Raw sensitive data
      |
      v
Restricted processing
      |
      v
Governed curated data
      |
      v
Finance-approved serving
```

The design should identify who can access sensitive data and why.

# 36. Step 15 — Observability

## Pipeline observability

Monitor:

- task success/failure;
- duration;
- retries;
- dependency state;
- queue/backlog where relevant.

## Data observability

Monitor:

- freshness;
- row volume;
- schema;
- null rates;
- duplicates;
- distribution changes.

## SLA observability

Monitor:

```text
Current time
+
expected completion
+
critical-path status
+
time remaining until 07:00
```

A useful alert is not:

> "Job failed."

It is:

> "Finance publish is projected to miss the 07:00 SLA because source X is 70 minutes behind and has no successful retry."

# 37. Step 16 — Failure Scenarios

Use:

```text
Detect
→ Contain
→ Recover
→ Validate
→ Publish / Republish
→ Prevent
```

## Source API unavailable

Detect connector failure and freshness breach.

Contain by preventing incomplete data from silently entering gold.

Recover through retry/backoff or source-specific recovery.

Validate completeness before publication.

## Database unavailable

Avoid repeated aggressive retries against the source.

Use checkpointed recovery.

## CDC lagging

Monitor lag against SLA budget. Decide whether the downstream report can proceed with a qualified dataset or must wait.

## Duplicate ingestion

Use source identifiers, checkpoints, deduplication, and idempotent writes.

## Missing partition

Detect expected partition absence before downstream publication.

## Schema change

Fail fast when the change is unsafe, quarantine incompatible data, update the contract, and replay if necessary.

## Transformation failure

Retry only when the failure is transient. Fix deterministic failures before repeated execution.

## Data-quality failure

Block publication when the failure is material.

## Warehouse unavailable

Use retry and workload recovery. Do not claim zero downtime unless the design actually provides it.

## Dashboard overload

Separate BI workloads from critical transformation compute where necessary.

# 38. Mandatory Deep Dive — Two-Year Backfill

### Scenario

Finance discovers a transformation bug and asks:

> "Correct the last two years of historical data."

A naive response is:

> "Run the pipeline for two years."

That is not sufficient.

### Risks of naive backfill

- massive compute load;
- production contention;
- corrupting current tables;
- changing numbers silently;
- breaking downstream consumers;
- violating the daily 07:00 SLA;
- inconsistent model versions;
- non-idempotent writes.

### Safer design

```text
Historical Raw Data
        |
        v
Backfill Planning
        |
        v
Isolated / Controlled Compute
        |
        v
Recomputed Candidate Data
        |
        v
Quality + Reconciliation
        |
        v
Controlled Publish
        |
        v
Downstream Reconciliation
```

### Backfill procedure

1. Identify the affected transformation version.
2. Identify affected date ranges.
3. Identify downstream models.
4. Estimate compute and storage impact.
5. Isolate or throttle backfill compute.
6. Re-run deterministic transformations.
7. Write candidate results separately where possible.
8. Validate row counts and business totals.
9. Reconcile against source data.
10. Publish in controlled partitions.
11. Validate downstream dashboards.
12. Record what changed.
13. Preserve audit evidence.

### Protect the daily SLA

A backfill must not automatically compete with the critical morning pipeline.

Possible controls:

- separate compute;
- lower priority;
- scheduling windows;
- workload quotas;
- partitioned backfill;
- controlled publication.

### Interview statement

> "I would treat the two-year correction as a controlled historical recomputation rather than a giant production rerun. I would isolate the workload, validate affected partitions, publish in controlled steps, and explicitly reconcile downstream Finance metrics."

# 39. Full Reference Architecture

```text
                         +----------------------+
                         | Operational Systems  |
                         | DB / ERP / Billing   |
                         +----------+-----------+
                                    |
                              CDC / Incremental
                                    |
                         +----------v-----------+
                         | Ingestion / Connectors|
                         +----------+-----------+
                                    |
                         +----------v-----------+
                         | Bronze / Raw Storage |
                         +----------+-----------+
                                    |
                         +----------v-----------+
                         | Validation / Quality |
                         +----------+-----------+
                                    |
                         +----------v-----------+
                         | Silver / Conformed    |
                         +----------+-----------+
                                    |
                         +----------v-----------+
                         | Transform / ELT       |
                         | dbt-style models      |
                         +----------+-----------+
                                    |
                         +----------v-----------+
                         | Gold / Dimensional    |
                         | Facts + Dimensions    |
                         +----------+-----------+
                                    |
                         +----------v-----------+
                         | Semantic Layer        |
                         | Canonical Metrics     |
                         +----------+-----------+
                                    |
                         +----------v-----------+
                         | Finance / BI / Users  |
                         +------------------------+

      +--------------------------------------------------+
      | Cross-cutting: Orchestration | Quality | Audit   |
      | Observability | Security | Lineage | Cost       |
      +--------------------------------------------------+

      Historical Raw
           |
           +--> Controlled Backfill --> Candidate --> Audit --> Publish
```

### Read the architecture as responsibilities

- Ingestion protects and captures source data.
- Bronze preserves replayable history.
- Silver creates conformed data.
- Transformation creates reusable business logic.
- Gold provides analytics-ready facts and dimensions.
- Semantic layer standardizes metrics.
- Publication is gated by quality and reconciliation.
- Cross-cutting controls make the platform operable.

# 40. Technology Selection

Technology should come after requirements.

A technology-neutral example is:

```text
Sources
  ↓
Managed connectors / CDC / custom extraction
  ↓
Object storage / warehouse / lakehouse
  ↓
SQL / distributed transformation / dbt-style models
  ↓
Warehouse or lakehouse serving
  ↓
Semantic layer
  ↓
BI
```

Possible implementation families include:

- managed cloud ingestion;
- open-source CDC;
- warehouse-centric ELT;
- lakehouse-centric ELT;
- hybrid architectures.

### Selection criteria

| Criterion | Questions |
|---|---|
| Volume | How much data and growth? |
| Freshness | Daily, hourly, minutes? |
| SQL | How SQL-centric are consumers? |
| Historical data | How much raw retention? |
| Governance | How strong are access/lineage needs? |
| Team | What can the team operate? |
| Cost | Storage and compute economics? |
| Reliability | What managed capabilities exist? |
| Ecosystem | What is already standardized? |
| Migration | What existing assets must remain? |

Correct answer pattern:

> "I would choose X because requirement Y makes it appropriate, accepting trade-off Z."

Not:

> "X is the best technology."

# 41. Alternative Architectures

## A. Warehouse-centric

```text
Sources
  ↓
Connectors / CDC
  ↓
Warehouse
  ↓
Staging
  ↓
Intermediate
  ↓
Marts
  ↓
Semantic Layer
  ↓
BI
```

### Strengths

- simple SQL workflow;
- strong BI integration;
- fewer storage layers;
- potentially lower operational burden.

### Weaknesses

- raw historical flexibility may be reduced;
- very large raw retention may be less economical depending on platform;
- specialized data-engineering workloads may be less natural.

## B. Lakehouse-centric

```text
Sources
  ↓
Ingestion
  ↓
Raw Object Storage
  ↓
Conformed Tables
  ↓
Gold Tables
  ↓
SQL / Semantic
  ↓
BI
```

### Strengths

- durable raw history;
- flexible retention;
- broad data-engineering workload support.

### Weaknesses

- more platform engineering;
- optimization/governance complexity.

## C. Hybrid

```text
Sources
  ↓
Raw / Lakehouse
  ↓
Curated Data
  ↓
Warehouse / SQL Serving
  ↓
Semantic Layer
  ↓
BI
```

Useful when the organization wants inexpensive durable storage plus a highly optimized analytical serving layer.

### Interview decision

Choose based on:

```text
Requirements
→ constraints
→ decision criteria
→ architecture
→ trade-offs
```

# 42. Trade-Off Catalogue

## Full vs incremental ingestion

**Full:** simpler, potentially expensive.

**Incremental:** efficient, more correctness complexity.

## CDC vs periodic extraction

**CDC:** captures changes efficiently, but introduces operational complexity.

**Periodic:** simpler, but can miss change timing and create more source load.

## Warehouse vs lakehouse

Choose based on SQL workload, retention, flexibility, cost, governance, and team capability.

## Managed connectors vs custom code

Managed reduces plumbing; custom provides control at an operational cost.

## Full refresh vs incremental models

Full refresh favors simplicity; incremental favors scale but requires careful change semantics.

## Dimensional vs normalized models

Dimensional models simplify analytics; normalized models can preserve source-like structure and transactional relationships.

## Semantic layer vs dashboard-specific logic

Centralization improves consistency; local logic can be faster for experimentation but creates metric divergence.

## Strict quality gates vs availability

Strict gates protect correctness but can delay reports. The decision should be based on business impact and materiality.

## Write–audit–publish vs immediate publication

Write–audit–publish adds latency but provides a stronger financial control.

## Retention vs cost

Longer retention increases storage and governance cost but supports historical analysis and audit.

## Performance vs compute cost

More compute can protect SLA; optimize based on business value.

## Simplicity vs flexibility

Every additional platform increases operational surface area.

For every trade-off:

```text
Requirement
→ Options
→ Decision criteria
→ Choice
→ Consequences
```

# 43. 45-Minute Interview Walkthrough

## 0–5 minutes — Requirements

Clarify:

- sources;
- volume;
- freshness;
- retention;
- Finance correctness;
- consumers;
- restatement expectations.

## 5–8 minutes — Estimates

Calculate:

- records/day;
- bytes/day;
- annual storage;
- peak throughput;
- query workload;
- growth.

## 8–15 minutes — High-level architecture

Draw:

```text
Sources
→ Ingestion
→ Bronze
→ Silver
→ Gold
→ Semantic
→ Finance
```

Add orchestration, quality, audit, and observability.

## 15–25 minutes — Ingestion + storage + modelling

Deep dive into:

- CDC/incremental;
- raw history;
- dimensional grain;
- facts/dimensions;
- SCD2.

## 25–33 minutes — Transformations + orchestration + quality

Discuss:

- staging/intermediate/marts;
- incremental models;
- dependencies;
- retries;
- quality gates;
- write–audit–publish.

## 33–38 minutes — Late data + backfills + failures

Discuss:

- late arrivals;
- month-end;
- two-year backfill;
- source failures.

## 38–42 minutes — Cost + governance + evolution

Discuss:

- cost drivers;
- security;
- audit;
- 10× scale.

## 42–45 minutes — Summary

State:

- architecture;
- key assumptions;
- critical trade-offs;
- main risks;
- evolution path.

Protect the last few minutes. Do not spend the whole interview drawing boxes.

# 44. What to Draw First

Start with:

```text
Sources
   ↓
Ingestion
   ↓
Storage
   ↓
Transformation
   ↓
Serving
   ↓
Consumers
```

Then expand.

Do not begin with:

- individual tables;
- every DAG task;
- every cloud service;
- every monitoring metric.

### What to say

> "I'll start with the end-to-end flow. We have several operational and SaaS sources, so the first design decision is how to ingest them without overloading source systems. I'll use incremental extraction or CDC where supported, preserve raw data for replay and audit, and make the 07:00 SLA explicit."

Then continue from source to serving.

# 45. Interviewer Pushback

## "Why not just use a warehouse?"

**Weak:** "Because lakehouses are better."

**Acceptable:** "A warehouse is a valid option; I would choose it if the workload is primarily SQL analytics and raw historical flexibility is not a major constraint."

**Strong:** "I would first compare the raw-retention requirement, SQL workload, governance, source diversity, cost, and team capability. If the organization is strongly SQL-centric and the warehouse meets retention economics, warehouse-centric ELT is simpler. If raw retention and heterogeneous processing are first-class requirements, a lakehouse or hybrid design may be better."

## "Why do you need raw storage?"

**Strong:** "For replay, auditability, debugging, historical reconstruction, and controlled backfills. If those requirements are weak and the source systems already provide reliable historical snapshots, the raw layer can be simplified."

## "Why CDC?"

**Strong:** "Only where update/delete semantics and incremental change capture justify it. If daily snapshots are small enough and source load is acceptable, periodic extraction may be simpler."

## "Why not full refresh?"

**Strong:** "I would use full refresh when the dataset is small or simplicity is more valuable. At larger history and tighter SLA, incremental models reduce compute, but I must handle updates, deletes, late data, and restatements correctly."

## "What if the source API fails?"

**Strong:** "I would detect freshness/arrival failure early, retry with bounded backoff, prevent incomplete data from silently reaching Finance, and either recover before the SLA budget is exhausted or apply the business-approved degraded reporting policy."

## "What if Finance says yesterday's number was wrong?"

**Strong:** "Trace the metric through the semantic definition and lineage, identify whether the error is source, transformation, or metric logic, correct the affected data, reconcile, publish a controlled restatement, and retain an audit trail."

## "What if the pipeline finishes at 07:15?"

**Strong:** "The SLA has already failed. I would determine the critical-path cause, protect downstream correctness, communicate the breach, and then redesign capacity/slack/retry policy so normal variance does not consume the entire deadline."

## "How do you backfill two years?"

**Strong:** "Isolate and plan the affected partitions, estimate compute, run deterministic historical recomputation, validate and reconcile, publish in controlled steps, and protect the normal 07:00 workload."

## "Why SCD2?"

**Strong:** "Because historical reports may need the dimension state that existed when the fact occurred. SCD2 preserves those versions and supports point-in-time joins."

## "Why not let every dashboard define revenue?"

**Strong:** "Because independent definitions create metric drift. I would centralize canonical definitions and explicitly name genuinely different metrics."

# 46. Follow-Up Question Bank — Requirements

1. What is the exact 07:00 contract?
2. Is the report allowed to be provisional?
3. How many sources exist?
4. Which sources are transactional?
5. Which sources are SaaS APIs?
6. Are files included?
7. What is the daily volume?
8. What is the growth rate?
9. What is the retention period?
10. Who consumes the data?

Strong pattern:

```text
Ask only questions that can change the architecture or SLA.
```

# 47. Follow-Up Question Bank — Estimation

1. How many records arrive per day?
2. What is average record size?
3. What is peak rate?
4. What is annual storage?
5. What is seven-year storage?
6. What compression ratio are you assuming?
7. What is the query concurrency?
8. What is the critical-path compute window?
9. What happens at 10× volume?
10. What is the largest cost driver?

Use order-of-magnitude reasoning rather than fake precision.

# 48. Follow-Up Question Bank — Ingestion

1. When is full extraction acceptable?
2. What makes a good incremental key?
3. What if `updated_at` is not reliable?
4. How do you handle duplicate extraction?
5. How do you handle deletes?
6. How do you protect the OLTP system?
7. When would you use CDC?
8. How do you handle initial snapshot + CDC handoff?
9. What if a SaaS API has a rate limit?
10. What if the API cursor expires?
11. How do you detect missing records?
12. How do you checkpoint?
13. When do you advance the watermark?
14. What happens after a failed ingestion?
15. When is custom ingestion justified?

# 49. Follow-Up Question Bank — Storage

1. Why warehouse?
2. Why lake?
3. Why lakehouse?
4. What belongs in raw?
5. What belongs in conformed storage?
6. What belongs in gold?
7. How do you partition?
8. How do you avoid tiny files?
9. How do you manage retention?
10. What changes at 10× retained history?

# 50. Follow-Up Question Bank — Modelling

1. What is the grain of the sales fact?
2. Why dimensional modelling?
3. What is a fact table?
4. What is a dimension?
5. What is a conformed dimension?
6. When would you use a snapshot fact?
7. What is a surrogate key?
8. When is normalization preferable?
9. What happens if the grain changes?
10. How do you prevent double counting?
11. How do you model refunds?
12. How do you model order lines?
13. How do you model daily balances?
14. How do you model organizational hierarchy?
15. How do you document grain?

# 51. Follow-Up Question Bank — SCD

1. When is Type 1 enough?
2. Why Type 2?
3. What is a surrogate key?
4. What is `valid_from`?
5. What is `valid_to`?
6. How do you identify the current row?
7. How do you prevent overlapping ranges?
8. How do facts join to historical dimensions?
9. What if a dimension change arrives late?
10. What if two changes share a timestamp?

# 52. Follow-Up Question Bank — Transformations

1. Why staging models?
2. Why intermediate models?
3. Why marts?
4. How do dependencies work?
5. When is full refresh acceptable?
6. When is incremental appropriate?
7. How do you handle deletes?
8. How do you test incremental models?
9. How do you reproduce a historical result?
10. How do you handle a transformation bug?

# 53. Follow-Up Question Bank — Orchestration

1. What belongs in one task?
2. How do dependencies work?
3. How many retries?
4. What should not be retried?
5. How do you make tasks idempotent?
6. How do you schedule around the 07:00 SLA?
7. How do you detect a critical-path breach?
8. How do you backfill?
9. How do you prevent backfills from starving production?
10. What happens when an upstream task is late?

# 54. Follow-Up Question Bank — Data Quality

1. How do you test completeness?
2. How do you test uniqueness?
3. How do you test validity?
4. How do you test freshness?
5. How do you test referential integrity?
6. What blocks publication?
7. What is quarantined?
8. What is only alerted?
9. How do you reconcile source and target?
10. How do you handle an unexplained 20% revenue drop?

# 55. Follow-Up Question Bank — Late Data

1. What is late data?
2. How do you detect it?
3. What is a watermark?
4. What is a grace period?
5. How do you correct a prior day's report?
6. How do late dimensions affect facts?
7. What if a source is six hours late?
8. What if late data arrives after month-end?
9. How do you preserve audit history?
10. Who decides the restatement policy?

# 56. Follow-Up Question Bank — Backfills

1. How do you backfill one day?
2. How do you backfill one month?
3. How do you backfill two years?
4. How do you estimate backfill compute?
5. How do you isolate backfill workload?
6. How do you prevent production contention?
7. How do you validate backfill output?
8. How do you publish corrected history?
9. How do you protect current-day data?
10. How do you document what changed?

# 57. Follow-Up Question Bank — Finance and Reconciliation

1. Why does Finance require stronger controls?
2. What is write–audit–publish?
3. What does reconciliation compare?
4. What if totals differ by 0.1%?
5. What if totals differ by 20%?
6. What is a restatement?
7. How do you preserve prior published values?
8. How do you reproduce a report?
9. How do you trace a metric?
10. Who owns a business metric?

# 58. Follow-Up Question Bank — Semantic Layer

1. Why centralize metrics?
2. What is a metric contract?
3. Who owns definitions?
4. How do you version definitions?
5. What if two teams use different definitions?
6. How do you test a metric?
7. How do you trace a metric to source?
8. How do you prevent dashboard drift?
9. When is dashboard-specific logic acceptable?
10. How do you explain a metric change to Finance?

# 59. Follow-Up Question Bank — Cost

1. What costs the most?
2. How does retention affect cost?
3. How does full refresh affect cost?
4. How does partition pruning reduce cost?
5. When are pre-aggregations worthwhile?
6. How do you control scheduled compute?
7. How do you identify expensive queries?
8. What happens when budget is cut 50%?
9. What should not be optimized away?
10. How do you attribute cost to workloads?

# 60. Follow-Up Question Bank — Security

1. Who can access raw PII?
2. Who can access Finance gold data?
3. How do service identities work?
4. How do you classify sensitive columns?
5. Where is masking applied?
6. How is data encrypted?
7. What should be audited?
8. How do you implement least privilege?
9. How does retention affect compliance?
10. How do you investigate unauthorized access?

# 61. Follow-Up Question Bank — Reliability and Evolution

1. What happens if CDC stops?
2. What if the warehouse is unavailable?
3. What if a schema changes?
4. What if a pipeline fails halfway?
5. What if duplicate data is published?
6. What if a report misses 07:00?
7. What changes at 10× scale?
8. What changes with 100 sources?
9. What changes if hourly reporting is added?
10. What changes if real-time reporting is added?

# 62. Strong Answer Patterns

For almost every follow-up, use:

```text
Requirement
→ Current design
→ Failure/risk
→ Control
→ Trade-off
```

Examples:

### Source outage

```text
Requirement: complete Finance data
→ source unavailable
→ freshness breach
→ retry + early alert + publication gate
→ possible SLA impact
```

### Backfill

```text
Requirement: correct history
→ isolate affected partitions
→ recompute deterministically
→ validate/reconcile
→ controlled publication
→ protects daily workload
```

### Metric inconsistency

```text
Requirement: consistent Finance reporting
→ centralized metric definition
→ semantic layer
→ tests + ownership + lineage
→ controlled versioning
```

# 63. Break/Fix Scenarios

## Broken 1 — Sources directly into BI

```text
Sources → Warehouse → Dashboards
```

### Problems

- unclear ingestion;
- no durable raw history;
- no controlled transformation boundary;
- no quality gate;
- weak replay/backfill story.

### Fix

Introduce explicit ingestion, raw history, transformations, validation, and publication.

## Broken 2 — Full refresh every day

### Problem

Historical processing grows with retention.

### Fix

Use incremental models where justified and retain full-refresh paths for models where they remain simpler.

## Broken 3 — Every dashboard calculates revenue

### Problem

Metric drift.

### Fix

Canonical metric definition in semantic layer.

## Broken 4 — No 07:00 critical path

### Problem

The design has a daily schedule but no SLA decomposition.

### Fix

Back-plan from 07:00, identify critical path, add buffer, monitor projected completion.

## Broken 5 — No raw history

### Problem

Backfills and audits depend on source systems.

### Fix

Preserve appropriate raw data with retention policy.

## Broken 6 — No late-data policy

### Problem

A late record silently changes history or is ignored.

### Fix

Define watermark/grace/restatement policy.

## Broken 7 — Backfill shares all compute with production

### Problem

Historical correction can break the daily report.

### Fix

Isolate, throttle, schedule, or prioritize workloads.

## Broken 8 — No write–audit–publish

### Problem

Technically successful but incorrect data can reach Finance.

### Fix

Candidate output → audit/reconciliation → controlled publish.

## Broken 9 — No source protection

### Problem

Large extraction damages OLTP.

### Fix

CDC, replicas, incremental extraction, bounded extraction windows, or managed replication.

## Broken 10 — No lineage/ownership

### Problem

Nobody can explain where a Finance number came from.

### Fix

Track source → transformation → metric → dashboard and assign owners.

# 64. Production Incident Scenarios

## Incident 1 — Finance report missing at 06:30

Response:

```text
Detect
→ inspect critical path
→ identify blocker
→ contain downstream publication
→ recover
→ validate
→ communicate ETA
→ post-incident prevention
```

## Incident 2 — CDC is six hours behind

Do not blindly process stale data. Determine whether the report can be safely produced, whether the business policy allows a qualified report, and how much SLA budget remains.

## Incident 3 — SaaS rate limit changes

Throttle, checkpoint, retry with bounded backoff, and adjust connector behavior. Monitor completeness.

## Incident 4 — Duplicate orders appear

Identify whether duplication occurred in extraction, raw loading, merge logic, or modelling. Correct at the earliest safe layer and reconcile downstream.

## Incident 5 — Revenue drops 20%

Do not assume a business change. Compare source totals, ingestion counts, transformations, filters, metric definition, and dashboard logic.

## Incident 6 — Unannounced schema change

Quarantine or fail safely, inspect compatibility, update contract, test, then replay affected data.

## Incident 7 — Gold model fails

Protect publication, identify deterministic vs transient failure, repair, rerun affected partitions, and validate.

## Incident 8 — Backfill consumes all compute

Throttle or isolate it, restore the production SLA path, and redesign workload governance.

## Incident 9 — Finance disputes a metric

Trace metric lineage, definition, filters, source data, transformation version, and published output.

## Incident 10 — Historical correction required

Use the controlled backfill/restatement process rather than ad-hoc SQL edits in production.

# 65. Coding Examples

## Python — volume estimation

```python
daily_rows = 100_000_000
row_size = 1_000
compression_ratio = 4

daily_raw = daily_rows * row_size
daily_compressed = daily_raw / compression_ratio

print(f"Raw/day: {daily_raw / 1e9:.2f} GB")
print(f"Compressed/day: {daily_compressed / 1e9:.2f} GB")
```

## SQL — incremental extraction

```sql
SELECT *
FROM source_orders
WHERE updated_at > :last_watermark
  AND updated_at <= :current_watermark;
```

## SQL — deduplication

```sql
SELECT *
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY order_id
            ORDER BY updated_at DESC
        ) AS rn
    FROM staged_orders
) t
WHERE rn = 1;
```

## SQL — duplicate-quality check

```sql
SELECT order_id, COUNT(*) AS duplicate_count
FROM fact_orders
GROUP BY order_id
HAVING COUNT(*) > 1;
```

## SQL — reconciliation

```sql
SELECT SUM(amount) AS warehouse_revenue
FROM fact_orders
WHERE order_date = CURRENT_DATE - INTERVAL '1 day';
```

## SQL — SCD2 point-in-time join

```sql
SELECT
    f.order_id,
    f.order_date,
    d.segment
FROM fact_orders f
JOIN dim_customer d
  ON f.customer_id = d.customer_id
 AND f.order_date >= d.valid_from
 AND f.order_date < COALESCE(d.valid_to, TIMESTAMP '9999-12-31');
```

These examples demonstrate reasoning patterns. They are not a vendor-specific implementation guide.

# 66. Hands-On Practice

## Lab 1 — Requirements discovery

Given only:

> "Finance needs daily reports by 07:00."

Write:

- 15 clarification questions;
- 5 assumptions;
- MVP;
- future scope;
- top five risks.

## Lab 2 — Estimation

Use:

```text
100M rows/day
1 KB/row
4:1 compression
7-year retention
30% annual growth
```

Calculate:

- daily raw;
- daily compressed;
- annual compressed;
- approximate retained volume;
- average records/sec;
- 3× peak.

Then explain which numbers affect architecture.

## Lab 3 — Incremental ingestion

Implement a toy pipeline with:

- watermark;
- overlap;
- deduplication;
- checkpoint only after success.

Inject:

- duplicate records;
- late updates;
- failed run.

Document behavior.

## Lab 4 — Dimensional model

Design:

```text
fact_orders
dim_customer
dim_product
dim_date
dim_store
```

State the grain of every table.

## Lab 5 — SCD2

Create a customer dimension and simulate:

```text
SMB
→ Enterprise
→ Mid-Market
```

Verify:

- one current row;
- no overlapping ranges;
- correct point-in-time joins.

## Lab 6 — 07:00 DAG

Draw the critical path and allocate a safety buffer.

## Lab 7 — Write–audit–publish

Generate candidate Finance output and intentionally introduce:

- missing rows;
- duplicate rows;
- revenue mismatch.

The publish step must block.

## Lab 8 — Late data

Publish Day 1, introduce Day 1 records on Day 2, and implement a correction path.

## Lab 9 — Two-year backfill

Create a plan that protects the normal daily pipeline.

## Lab 10 — Semantic consistency

Define `net_revenue` once and use it across three simulated dashboards.

# 67. Three Practice Levels

## Level 1 — Guided

Use the assumptions and architecture skeleton in this document.

Goal:

- learn the sequence;
- understand the vocabulary;
- practice explaining choices.

## Level 2 — Semi-guided

Use only:

> "Design the analytics platform for a company with several operational systems and SaaS tools; Finance needs daily reports by 07:00."

You may use a timer but no architecture template.

## Level 3 — Blind

Use only the prompt.

You must independently:

```text
Clarify
→ Estimate
→ Design
→ Draw
→ Explain
→ Handle pushback
→ Summarize
```

# 68. Mock Interview A — Standard

### Prompt

> Design the analytics platform for a company with several operational systems and SaaS tools; Finance needs daily reports by 07:00.

### Expected flow

Requirements → estimates → sources → ingestion → storage → model → transforms → orchestration → quality → SLA → late data → backfill → semantic layer → cost → security → recap.

### Interviewer prompts

- Why CDC?
- Why raw history?
- How do you handle late data?
- What is the grain?
- How do you meet 07:00?
- How do you backfill two years?
- How do you keep dashboards consistent?

### Scoring

Use the 18-category rubric below.

# 69. Mock Interview B — Ambiguous

### Prompt

> "We need a new analytics platform for Finance."

The interviewer provides no numbers unless asked.

### Goal

Test requirements clarification.

You should discover:

- sources;
- scale;
- freshness;
- retention;
- consumers;
- correctness;
- audit;
- restatement;
- security;
- budget.

### Failure pattern

Starting with:

> "I would use Snowflake and Airflow."

The problem is not the tools. The problem is missing requirements.

# 70. Mock Interview C — Adversarial

Start with the standard prompt.

Then change:

1. Daily volume increases 10×.
2. Finance needs hourly reporting.
3. One SaaS provider is rate-limited.
4. A source begins delivering late records.
5. Finance requires two years of correction.
6. Budget is reduced 50%.

For each change:

```text
State what changed
→ identify affected assumptions
→ update architecture
→ state new trade-off
→ protect correctness/SLA
```

# 71. Self-Scoring Rubric

| Category | 1 — Weak | 3 — Good | 5 — Senior |
|---|---|---|---|
| Requirements | Jumps to design | Clarifies basics | Finds hidden requirements |
| Estimates | Missing | Reasonable | Drives decisions |
| Architecture | Tool list | Coherent flow | Requirement-driven boundaries |
| Ingestion | Generic | Incremental considered | CDC/full/incremental trade-offs |
| Storage | One answer | Alternatives | Explicit decision criteria |
| Modelling | Tables only | Facts/dims | Grain + historical correctness |
| Transformations | Generic | Layered | Incremental/reproducible |
| Orchestration | Schedule only | DAG | SLA-aware recovery |
| Quality | Alerts | Tests | Publication gates |
| SLA | Mentions 07:00 | Critical path | Budget + buffer + prediction |
| Late Data | Ignored | Basic policy | Restatement/reconciliation |
| Backfill | "Rerun" | Partitioned | Isolated, validated, controlled |
| Semantic Layer | Optional | Mentioned | Metric governance |
| Cost | Generic | Some controls | Workload economics |
| Reliability | Retry only | Recovery | Detect/contain/recover/validate/prevent |
| Communication | Rambling | Clear | Concise and adaptive |
| Trade-offs | Lists options | Makes choice | Explains consequences |
| Evolution | Vague | 10× mentioned | Architecture evolves deliberately |

### Interpretation

- **80+**: strong case readiness;
- **65–79**: good foundation; identify weak categories;
- **50–64**: intermediate; repeat guided practice;
- **<50**: return to requirements, estimates, and architecture fundamentals.

No single score substitutes for interview feedback.

# 72. Interview Practice Loop

Follow this exact cycle:

1. Read only the problem statement.
2. Attempt the design in **45 minutes**.
3. Speak aloud.
4. Draw the architecture.
5. Record the attempt.
6. Compare against the reference solution.
7. Score using the Topic 01 rubric.
8. Log mistakes.
9. Re-attempt after a week.
10. Perform a partner mock.

### Error log

```text
Case:
Date:
Total time:

Requirements missed:
Estimates missed:
Architecture mistake:
Modelling mistake:
Reliability mistake:
Quality mistake:
Backfill mistake:
Metric mistake:
Cost mistake:
Communication mistake:

Top recurring error:
Correction:
Next drill:
```

# 73. Common Interview Mistakes

- jumping directly to technologies;
- not clarifying requirements;
- no estimates;
- ignoring the 07:00 SLA;
- ignoring Finance correctness;
- treating batch as trivial;
- using full refresh everywhere;
- no incremental strategy;
- no CDC discussion;
- no modelling;
- unclear grain;
- ignoring SCD;
- no data quality gates;
- no reconciliation;
- no late-data strategy;
- no backfill strategy;
- no semantic layer;
- inconsistent metrics;
- no cost discussion;
- no operational story;
- over-engineering;
- under-engineering;
- drawing one giant architecture;
- failing to communicate while drawing;
- ignoring interviewer hints;
- spending too much time on technology details;
- running out of time before failure handling.

# 74. Mental Models

### 1. Finance data must be correct, reproducible, and auditable.

### 2. Start with requirements, not tools.

### 3. Estimates should drive architecture.

### 4. Preserve raw data when replay and auditability matter.

### 5. Incremental processing is a correctness problem as much as a performance problem.

### 6. A daily SLA is an end-to-end pipeline property.

### 7. Data quality should gate publication.

### 8. Historical correctness requires a deliberate restatement strategy.

### 9. Backfills must coexist safely with normal production workloads.

### 10. Shared metric definitions prevent organizational data inconsistency.

# 75. Final Interview Cheat Sheet

```text
1. Clarify
2. Scope
3. Estimate
4. Identify sources
5. Choose ingestion
6. Choose storage
7. Define layers
8. Define grain
9. Define facts/dimensions
10. Build transformations
11. Build DAG
12. Add quality gates
13. Add write–audit–publish
14. Handle late data
15. Handle restatements
16. Design serving
17. Define semantic layer
18. Add observability
19. Discuss cost
20. Discuss security
21. Discuss failures
22. Discuss backfills
23. Discuss 10× evolution
24. Summarize
```

### 60-second answer template

> "I would first clarify source count, volume, freshness, retention, Finance correctness, and the exact 07:00 contract. Based on the estimated workload, I would use incremental ingestion or CDC where appropriate, preserve raw history, create conformed data, and build dimensional gold models. Orchestration would run the dependency graph backward from the 07:00 deadline, with quality gates and write–audit–publish before Finance sees the data. Late records and corrections would follow a controlled restatement path, and two-year corrections would use isolated, validated backfills. A semantic layer would centralize Finance metrics. The main trade-offs are operational complexity versus correctness, freshness, and cost."

# 76. Final Assessment

## Part A — Requirements

1. What information is missing from the prompt?
2. Which clarification can most change the architecture?
3. What does Finance imply beyond "daily reports"?
4. What does 07:00 imply operationally?
5. What should be MVP?
6. What should be deferred?
7. What assumptions must be stated?
8. What consumers should be identified?
9. What retention questions matter?
10. What security questions matter?

## Part B — Estimation

1. Calculate daily raw volume for 100M × 1KB.
2. Calculate 4:1 compressed volume.
3. Calculate annual compressed volume.
4. Calculate seven-year compressed volume.
5. Calculate average events/sec.
6. Calculate 3× peak.
7. Explain how volume affects storage choice.
8. Explain how peak affects compute.
9. Explain how retention affects cost.
10. Explain how query load affects serving.

## Part C — Architecture

1. Draw the six-layer flow.
2. Identify the durable boundary.
3. Identify the transformation boundary.
4. Identify the publication boundary.
5. Identify the consumer boundary.
6. Add orchestration.
7. Add quality gates.
8. Add audit.
9. Add observability.
10. Explain the main architecture trade-off.

## Part D — Modelling

1. Define fact-table grain.
2. Explain dimensions.
3. Explain conformed dimensions.
4. Compare normalized and dimensional models.
5. Explain transaction facts.
6. Explain periodic snapshots.
7. Explain accumulating snapshots.
8. Explain surrogate keys.
9. Explain double counting.
10. Model a Finance sales fact.

## Part E — Incremental / CDC

1. Explain high-water marks.
2. Explain timestamp weaknesses.
3. Handle duplicate extraction.
4. Handle deletes.
5. Explain CDC.
6. Explain initial snapshot + CDC handoff.
7. Explain ordering.
8. Explain replay.
9. Explain reconciliation.
10. Explain when full extraction is better.

## Part F — Data Quality

1. Test completeness.
2. Test uniqueness.
3. Test validity.
4. Test freshness.
5. Test referential integrity.
6. Define a blocking gate.
7. Define a warning.
8. Define quarantine.
9. Design reconciliation.
10. Handle a 20% revenue anomaly.

## Part G — Late Data

1. Define late data.
2. Detect it.
3. Explain watermarks.
4. Explain grace periods.
5. Correct a prior day.
6. Handle late dimensions.
7. Handle late facts.
8. Handle delayed SaaS.
9. Handle month-end late data.
10. Preserve audit history.

## Part H — SCD2

1. Explain why Type 2 exists.
2. Define surrogate key.
3. Define validity interval.
4. Identify current row.
5. Prevent overlaps.
6. Join facts point-in-time.
7. Handle late dimension changes.
8. Handle duplicate changes.
9. Detect two current rows.
10. Explain Type 1 vs Type 2.

## Part I — Backfills

1. Backfill one day.
2. Backfill one month.
3. Backfill two years.
4. Estimate backfill compute.
5. Isolate workload.
6. Protect 07:00.
7. Validate candidate data.
8. Reconcile.
9. Publish corrected partitions.
10. Audit the change.

## Part J — Semantic Layer

1. Why centralize metrics?
2. Define revenue.
3. Explain metric ownership.
4. Explain versioning.
5. Explain metric tests.
6. Explain lineage.
7. Handle two valid definitions.
8. Prevent dashboard drift.
9. Explain semantic-layer trade-offs.
10. Handle Finance metric dispute.

## Part K — Cost

1. Identify storage cost.
2. Identify compute cost.
3. Identify query cost.
4. Identify movement cost.
5. Optimize full refresh.
6. Optimize retention.
7. Optimize partitions.
8. Optimize BI queries.
9. Respond to 50% budget reduction.
10. Protect SLA while optimizing.

## Part L — Failure

1. Source outage.
2. SaaS outage.
3. CDC lag.
4. Duplicate ingestion.
5. Missing partition.
6. Schema drift.
7. Transform failure.
8. Quality failure.
9. Warehouse outage.
10. SLA breach.

## Part M — Full Design Prompts

### Prompt 1

> Design the analytics platform for a company with several operational systems and SaaS tools; Finance needs daily reports by 07:00.

### Prompt 2

> Design the same platform when volume increases 10× and Finance now requires hourly reporting.

### Prompt 3

> Design the same platform after Finance discovers a transformation bug affecting two years of historical reports.

For each prompt, complete:

```text
Requirements
→ Estimates
→ Architecture
→ Modelling
→ Ingestion
→ Transformation
→ Orchestration
→ Quality
→ SLA
→ Late data
→ Backfill
→ Semantic layer
→ Cost
→ Security
→ Failure handling
→ Evolution
```

# 77. Completion Standard

Do not consider this case complete until you can:

- clarify the incomplete prompt in approximately five minutes;
- state assumptions explicitly;
- estimate scale without false precision;
- classify operational, SaaS, and file sources;
- choose full/incremental/CDC deliberately;
- explain source protection;
- choose warehouse/lake/lakehouse using criteria;
- define Bronze/Silver/Gold responsibilities;
- state fact-table grain;
- design facts and dimensions;
- explain SCD1 and SCD2;
- design incremental models;
- explain late updates and deletes;
- build an orchestration DAG;
- design the 07:00 critical path;
- create data-quality gates;
- explain write–audit–publish;
- reconcile source and target;
- handle late-arriving data;
- handle month-end restatements;
- design a semantic layer;
- prevent metric inconsistency;
- plan a two-year backfill;
- protect production from backfill workloads;
- explain cost drivers;
- explain security/governance;
- troubleshoot at least ten failure scenarios;
- draw the full architecture in under eight minutes;
- explain the design coherently in a 45-minute interview;
- handle requirement changes;
- defend trade-offs;
- explain evolution at 10× scale;
- give a concise final summary.

# 78. Roadmap Coverage Audit

| Roadmap Requirement | Covered? | Location |
|---|---|---|
| Batch analytics platform case | ✅ | Case Overview |
| Several operational systems | ✅ | Requirements / Sources |
| SaaS sources | ✅ | Sources / Ingestion |
| Finance daily reports | ✅ | Case Prompt |
| 07:00 SLA | ✅ | SLA sections |
| End-to-end ELT thinking | ✅ | Architecture flow |
| Data modelling | ✅ | Modelling |
| SLAs | ✅ | 07:00 SLA |
| Backfills | ✅ | Two-Year Backfill |
| Cost | ✅ | Cost Controls |
| Incremental ingestion | ✅ | Ingestion |
| CDC | ✅ | CDC Design |
| Connectors | ✅ | Ingestion |
| Warehouse/lakehouse choice | ✅ | Storage / Alternatives |
| Data layers | ✅ | Bronze/Silver/Gold |
| Dimensional modelling | ✅ | Modelling |
| dbt-style transformations | ✅ | Transformation |
| Orchestration dependencies | ✅ | Orchestration |
| Quality gates | ✅ | Data Quality |
| Write–audit–publish | ✅ | Dedicated section |
| Late data | ✅ | Late Data |
| Month-end restatements | ✅ | Month-End |
| Consumers | ✅ | Serving |
| Semantic layer | ✅ | Semantic Layer |
| Cost controls | ✅ | Cost |
| Incremental models deep dive | ✅ | Incremental Models |
| SCD Type 2 deep dive | ✅ | SCD2 |
| Two-year backfill deep dive | ✅ | Backfill |
| Metric consistency deep dive | ✅ | Metric Consistency |
| Related Stage 2 concepts | ✅ | Prerequisites / applied concepts |
| 45-minute interview attempt | ✅ | Interview Walkthrough |
| Reference design | ✅ | Full Architecture |
| Follow-up questions | ✅ | Question Bank |
| Failure scenarios | ✅ | Failure / Incident sections |
| Trade-offs | ✅ | Trade-Off Catalogue |
| Interview communication | ✅ | Interview sections |
| Self-scoring | ✅ | Rubric |

# 79. Final Operating Standard

The candidate should reason in this order:

```text
CLARIFY
    ↓
SCOPE
    ↓
ESTIMATE
    ↓
CLASSIFY SOURCES
    ↓
INGEST SAFELY
    ↓
PRESERVE HISTORY
    ↓
CONFORM DATA
    ↓
DEFINE GRAIN
    ↓
MODEL FACTS + DIMENSIONS
    ↓
TRANSFORM IN DEPENDENCY ORDER
    ↓
ORCHESTRATE
    ↓
VALIDATE
    ↓
AUDIT
    ↓
PUBLISH
    ↓
SERVE CONSISTENT METRICS
    ↓
MONITOR SLA + DATA
    ↓
HANDLE LATE DATA
    ↓
RESTATE WHEN REQUIRED
    ↓
BACKFILL SAFELY
    ↓
OPTIMIZE COST
    ↓
GOVERN ACCESS
    ↓
HANDLE FAILURE
    ↓
EVOLVE
```

The strongest final mental model is:

> **Design backward from the business outcome and SLA, preserve enough history to recover and audit, make correctness observable, publish only after validation, and choose technologies only after the requirements justify them.**

A production batch analytics platform is not merely:

```text
Extract → Transform → Load → BI
```

It is:

```text
Business requirement
→ trustworthy ingestion
→ durable history
→ reproducible transformation
→ controlled publication
→ consistent metrics
→ measurable SLA
→ recoverable operations
→ auditable corrections
→ sustainable cost
```

That is the level expected for a senior Data Engineering system-design interview.

# 80. Expanded Follow-Up Bank

> This bank contains **180 questions** across the major dimensions of the case. Use it after the 45-minute attempt; answer aloud first, then compare against the reasoning patterns in this module.

## Requirements — 10 Questions

### 1. What exact report must be ready by 07:00?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 2. Is 07:00 a hard SLA or target?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 3. Can Finance consume provisional data?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 4. Which sources are business-critical?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 5. What is the required retention period?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 6. What is the required freshness per dataset?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 7. Who owns Finance metric definitions?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 8. Are restatements expected?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 9. Are historical reports immutable after publication?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 10. What query concurrency is expected?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

## Estimation — 10 Questions

### 1. What is the daily record count?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 2. What is the average record size?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 3. What is the peak multiplier?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 4. What is the annual growth rate?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 5. How much storage is needed for one year?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 6. How much storage is needed for seven years?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 7. What compression ratio is reasonable?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 8. What is the average record rate?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 9. What is the peak record rate?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 10. Which estimate most changes the architecture?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

## Ingestion — 15 Questions

### 1. When would you choose full extraction?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 2. When would you choose incremental extraction?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 3. When is CDC justified?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 4. How do you protect an OLTP source?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 5. How do you checkpoint an API extraction?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 6. When do you advance a watermark?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 7. How do you handle duplicate extraction?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 8. How do you handle deletes?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 9. How do you handle API rate limits?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 10. How do you handle pagination?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 11. What if an API cursor expires?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 12. How do you detect missing records?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 13. How do you handle an initial snapshot?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 14. How do you hand off from snapshot to CDC?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 15. When is custom ingestion justified?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

## Storage — 10 Questions

### 1. Why use a warehouse?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 2. Why use a lake?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 3. Why use a lakehouse?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 4. What belongs in raw storage?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 5. What belongs in Silver?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 6. What belongs in Gold?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 7. How do you partition data?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 8. How do you avoid tiny files?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 9. How do you manage historical retention?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 10. What changes at 10× retained volume?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

## Modelling — 15 Questions

### 1. What is the grain of fact_sales?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 2. Why is grain defined before implementation?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 3. What is a transaction fact?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 4. What is a periodic snapshot?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 5. What is an accumulating snapshot?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 6. What is a dimension?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 7. What is a conformed dimension?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 8. Why use surrogate keys?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 9. When is normalization preferable?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 10. How do you prevent double counting?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 11. How do you model order lines?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 12. How do you model refunds?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 13. How do you model daily balances?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 14. How do you model organizational hierarchy?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 15. How do you document grain?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

## SCD — 10 Questions

### 1. When is SCD Type 1 sufficient?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 2. Why use SCD Type 2?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 3. What is a surrogate key in SCD2?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 4. What does valid_from mean?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 5. What does valid_to mean?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 6. How do you identify the current row?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 7. How do you prevent overlapping validity intervals?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 8. How do facts join to historical dimensions?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 9. How do you handle a late dimension change?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 10. How do you handle two changes with the same timestamp?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

## Transformations — 10 Questions

### 1. Why use staging models?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 2. Why use intermediate models?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 3. Why use marts?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 4. How are dependencies represented?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 5. When is full refresh appropriate?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 6. When is an incremental model appropriate?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 7. How do incremental models handle updates?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 8. How do incremental models handle deletes?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 9. How do you test incremental logic?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 10. How do you reproduce a historical transformation?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

## Orchestration — 10 Questions

### 1. What belongs in one orchestration task?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 2. How should dependencies be expressed?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 3. What failures should be retried?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 4. What failures should not be retried?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 5. How do you make tasks idempotent?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 6. How do you schedule backward from 07:00?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 7. How do you monitor the critical path?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 8. How do you execute backfills?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 9. How do you prevent backfills from starving production?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 10. What happens when an upstream task is late?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

## Data Quality — 10 Questions

### 1. How do you test completeness?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 2. How do you test uniqueness?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 3. How do you test validity?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 4. How do you test freshness?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 5. How do you test referential integrity?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 6. Which checks should block publication?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 7. Which checks should only alert?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 8. When should data be quarantined?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 9. How do you reconcile source and target?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 10. How do you investigate a 20% revenue drop?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

## Late Data — 10 Questions

### 1. What is a late-arriving fact?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 2. How do you detect late data?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 3. What is a watermark?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 4. What is a grace period?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 5. How do you correct a prior-day report?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 6. How do late dimensions affect facts?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 7. How do you handle a delayed SaaS source?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 8. What if late data arrives after month-end?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 9. How do you preserve an audit trail for corrections?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 10. Who should own restatement policy?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

## Backfills — 10 Questions

### 1. How would you backfill one day?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 2. How would you backfill one month?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 3. How would you backfill two years?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 4. How do you estimate backfill compute?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 5. How do you isolate backfill workloads?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 6. How do you protect the 07:00 pipeline?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 7. How do you validate candidate backfill output?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 8. How do you reconcile corrected history?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 9. How do you publish corrected partitions?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 10. How do you document a historical correction?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

## Finance — 10 Questions

### 1. Why does Finance need stronger controls?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 2. What does write–audit–publish mean?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 3. What should reconciliation compare?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 4. What if source and warehouse totals differ?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 5. What if the difference is immaterial?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 6. What if the difference is material?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 7. How do you preserve a previously published report?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 8. How do you reproduce a report?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 9. How do you trace a Finance metric?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 10. Who approves a material restatement?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

## Semantic Layer — 10 Questions

### 1. Why centralize business metrics?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 2. What is a metric contract?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 3. Who owns a metric definition?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 4. How should metric definitions be versioned?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 5. What if two teams need different definitions?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 6. How do you test a semantic metric?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 7. How do you trace a metric to source data?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 8. How do you prevent dashboard drift?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 9. When is dashboard-specific logic acceptable?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 10. How do you communicate a metric definition change?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

## Cost — 10 Questions

### 1. What are the largest cost drivers?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 2. How does retention affect cost?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 3. How does full refresh affect cost?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 4. How does partition pruning reduce cost?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 5. When are pre-aggregations worthwhile?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 6. How do you control scheduled compute?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 7. How do you find expensive BI queries?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 8. What if the budget is cut by 50%?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 9. What should not be optimized away?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 10. How do you attribute cost to workloads?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

## Security — 10 Questions

### 1. Who should access raw PII?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 2. Who should access Finance Gold data?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 3. How do service identities work?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 4. How should sensitive columns be classified?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 5. Where should masking occur?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 6. How is data encrypted?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 7. What should be audited?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 8. How do you implement least privilege?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 9. How does retention interact with governance?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 10. How would you investigate unauthorized access?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

## Reliability — 10 Questions

### 1. What if CDC stops?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 2. What if a source database is unavailable?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 3. What if a SaaS provider is unavailable?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 4. What if a pipeline fails halfway?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 5. What if duplicate data reaches Gold?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 6. What if a partition is missing?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 7. What if a schema changes without notice?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 8. What if the warehouse is unavailable?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 9. What if the report misses 07:00?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 10. How do you prevent recurrence after an incident?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

## Evolution — 10 Questions

### 1. What changes at 10× volume?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 2. What changes with 100 sources?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 3. What changes if Finance requires hourly reports?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 4. What changes if real-time reporting is required?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 5. What changes if retention increases to 10 years?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 6. What changes after a company acquisition?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 7. What changes if regulatory requirements become stricter?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 8. What changes if cost must fall 50%?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 9. What changes if another business unit becomes a consumer?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

### 10. How do you evolve without a full redesign?

**Strong reasoning:** State the relevant requirement, identify the design consequence, explain the control or trade-off, and mention how you would validate it in production.

# 81. Final Assessment Answer Guide

Use these as evaluation anchors rather than memorized scripts.

| Area | A strong answer should include |
|---|---|
| Requirements | Source types, scale, freshness, retention, consumers, correctness, audit, restatement |
| Estimates | Explicit assumptions, unit consistency, order-of-magnitude calculations |
| Ingestion | Source protection, full/incremental/CDC choice, checkpoints, idempotency |
| Storage | Requirement-based warehouse/lake/lakehouse comparison |
| Modelling | Grain, facts, dimensions, conformed dimensions, historical correctness |
| SCD2 | Versioned dimension rows and point-in-time joins |
| Incremental | Affected-window logic, updates/deletes, dedup, reconciliation |
| Orchestration | Dependency graph, retries, idempotency, SLA awareness |
| Quality | Blocking gates, quarantine, reconciliation |
| Write–audit–publish | Candidate output before controlled publication |
| Late data | Detection, correction, restatement, audit |
| Backfill | Isolation, partition selection, validation, controlled publication |
| Semantic | Canonical metric definitions and ownership |
| Cost | Workload economics without compromising SLA/correctness |
| Security | Least privilege, PII, auditability |
| Reliability | Detect → contain → recover → validate → prevent |
| Evolution | Requirement-driven changes at larger scale |
| Communication | Clear diagram, rationale, deep dives, recap |

# 82. Architecture Decision Matrix

| Decision | Prefer simpler option when | Prefer more capable option when |
|---|---|---|
| Full vs incremental | Small data / simple rebuild | Large history / tight SLA |
| Snapshot vs CDC | Low update volume / simple source | Frequent updates/deletes / lower latency |
| Warehouse vs lakehouse | SQL-first, managed analytics | Large raw retention / broad workloads |
| Managed connector vs custom | Connector covers requirements | Source behavior is unusual |
| Full refresh vs incremental model | Small model / simpler correctness | Large model / high refresh cost |
| Strict gate vs warning | Low materiality | Finance-critical correctness |
| Immediate vs controlled publish | Low-risk exploratory data | Financial/regulated outputs |
| Shared vs isolated compute | Low workload contention | Backfills / critical SLA |
| Pre-aggregation vs direct query | Low query load | Repeated heavy queries / strict latency |

# 83. Final Quality Gate

Before calling the case interview-ready, verify:

```text
[ ] Prompt clarified
[ ] Hidden requirements identified
[ ] Assumptions stated
[ ] Scale estimated
[ ] Sources classified
[ ] Incremental strategy justified
[ ] CDC discussed
[ ] Storage choice justified
[ ] Bronze/Silver/Gold responsibilities clear
[ ] Grain defined
[ ] Facts/dimensions designed
[ ] SCD2 understood
[ ] Incremental models understood
[ ] Orchestration DAG drawn
[ ] 07:00 SLA decomposed
[ ] Quality gates defined
[ ] Write–audit–publish explained
[ ] Reconciliation defined
[ ] Late-data strategy defined
[ ] Month-end restatement strategy defined
[ ] Two-year backfill strategy defined
[ ] Semantic layer defined
[ ] Metric consistency defended
[ ] Cost controls discussed
[ ] Security/governance discussed
[ ] Failure scenarios practiced
[ ] 10× evolution explained
[ ] Three mocks completed
[ ] 45-minute blind attempt completed
[ ] Self-score recorded
[ ] Error log updated
```
