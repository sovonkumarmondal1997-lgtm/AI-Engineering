# Lakeflow Declarative Pipelines and Expectations

> **Topic 07 — Lakeflow Declarative Pipelines and expectations**  
> **Phase C — Ingestion and Pipelines**  
> **Learning level:** Beginner → Intermediate → Advanced → Production  
> **Dependency chain:** `01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11 → 12 → 13 → 14`

> **Documentation safety:** Databricks Lakeflow terminology, APIs, decorators, event-log schemas, pipeline configuration, CDC syntax, serverless behavior, CLI commands, and pricing evolve. Conceptual behavior in this module is intentionally stable; exact version-sensitive syntax must be checked against the current Databricks documentation before production use.

---

## 1. Learning Objectives

By the end of this module, you should be able to:

- Explain declarative data engineering and why it exists.
- Define datasets in SQL and Python using current Lakeflow Declarative Pipelines patterns.
- Explain how a dependency graph is inferred and why dependency order matters.
- Distinguish streaming tables, materialized views, and temporary/intermediate views.
- Design expectations and choose `WARN`, `DROP`, or `FAIL` deliberately.
- Interpret expectation metrics without confusing pipeline health with data correctness.
- Use event-log evidence and lineage for operational diagnosis.
- Reason about CDC, SCD Type 1, SCD Type 2, sequencing, deletes, and out-of-order changes.
- Integrate Auto Loader and Kafka without re-learning their underlying technologies.
- Explain incremental updates, full refreshes, selective refreshes, flows, backfills, and late data.
- Parameterize environments safely.
- Compare Lakeflow Declarative Pipelines with custom Structured Streaming and dbt.
- Design governed, observable, cost-aware production pipelines.
- Troubleshoot real incidents using evidence instead of blind restarts.
- Architect an end-to-end multi-source Lakehouse pipeline.

### The production question

This module is successful when you can answer:

> **Can I understand, build, operate, troubleshoot, optimize, and architect Lakeflow Declarative Pipelines in a real production Data Engineering environment?**

The target answer is **yes**.

---

## 2. Prerequisites and Roadmap Position

This module is deliberately not a generic Spark tutorial.

Earlier roadmap modules already cover:

- Spark and PySpark fundamentals
- Delta Lake fundamentals
- Structured Streaming
- Kafka
- Auto Loader
- dbt
- Airflow/Lakeflow Jobs concepts
- Unity Catalog
- cloud storage and IAM fundamentals

Use the rule:

> **You learned this earlier; here is the minimum context required here.**

### Position in G4

```text
Unity Catalog
      ↓
Auto Loader / Lakeflow Connect
      ↓
Lakeflow Declarative Pipelines
      ↓
Lakeflow Jobs
```

Topic 07 is therefore the bridge between **ingestion** and **orchestration**.

### Operating loop

```text
Read
  ↓
Map the business requirement to a dataset graph
  ↓
Build
  ↓
Govern with Unity Catalog
  ↓
Define quality contracts
  ↓
Run incrementally
  ↓
Observe
  ↓
Break
  ↓
Diagnose
  ↓
Fix
  ↓
Measure cost/performance
  ↓
Document
  ↓
Explain
```

---

## 3. What Problem Does Declarative Data Engineering Solve?

A traditional data platform often evolves into a chain of imperative jobs:

```text
Raw files
   ↓
Python job
   ↓
Spark transformation
   ↓
Write bronze
   ↓
Another job
   ↓
Write silver
   ↓
Another job
   ↓
Write gold
   ↓
Scheduler
   ↓
Retries
   ↓
Monitoring
```

At small scale, this is understandable. At production scale, the difficult part is no longer writing one transformation. It is managing the system around the transformations.

Typical problems include:

- dependency management
- state management
- retries
- partial failures
- data quality
- incremental processing
- lineage
- refreshes
- backfills
- orchestration
- operational ownership
- environment configuration
- cost control

### Declarative alternative

Instead of manually encoding every execution step, declare the desired data products and relationships:

```text
Dataset A depends on source X
Dataset B depends on A
Dataset C depends on B
```

The platform can then reason about:

```text
Definitions
   ↓
Dependency graph
   ↓
Execution order
   ↓
Incremental processing
   ↓
Pipeline state
   ↓
Quality/operational results
```

Declarative does **not** mean the engineer stops understanding execution.

A production engineer still needs to understand:

- source behavior
- dependency graphs
- incremental semantics
- state
- data quality
- compute
- failures
- refreshes
- cost
- correctness

---

## 4. Declarative vs Imperative

### Imperative mental model

```text
Step 1: read source
Step 2: transform data
Step 3: write table
Step 4: run another job
Step 5: retry if required
Step 6: run downstream job
```

The program describes **how** to execute the workflow.

### Declarative mental model

```text
Source X → Dataset A → Dataset B → Dataset C
```

The definitions describe **what the data products should be** and how they depend on one another.

### Detailed comparison

| Dimension | Imperative Pipeline | Declarative Pipeline |
|---|---|---|
| Developer specifies | Execution steps | Desired datasets and transformations |
| Dependency management | Often explicit in orchestration code | Inferred from dataset relationships |
| Execution planning | Developer/platform scheduler | Platform-managed planning |
| State management | Often custom | More platform-managed |
| Incremental processing | Custom implementation frequently required | Dataset semantics can provide managed incremental behavior |
| Data quality | Separate validation framework often required | Expectations can be attached to datasets |
| Retry handling | Job/orchestrator-specific | Platform can manage pipeline execution behavior |
| Lineage | Often assembled from jobs/tools | Dataset graph provides a strong declarative basis |
| Maintainability | Can become orchestration-heavy | Usually clearer for supported workloads |
| Debugging | Follow job chain and state | Inspect graph, update state, logs/events, source behavior |
| Portability | Usually high at code level | More platform-specific |
| Operational control | Maximum low-level control | More abstraction, less direct control |
| Cost | Depends heavily on implementation | Can be efficient when incremental/platform-managed semantics fit |
| Flexibility | Very high | High, but bounded by supported declarative capabilities |

### Important misconception

Declarative does not mean:

> "The platform magically solves data engineering."

It means the platform takes responsibility for more of the execution model **within the supported abstraction**.

Your responsibility remains:

```text
Correct requirement
      ↓
Correct dataset model
      ↓
Correct incremental semantics
      ↓
Correct quality rules
      ↓
Correct governance
      ↓
Correct operations
```

---

## 5. Lakeflow Declarative Pipelines Architecture

Conceptual architecture:

```text
                         SOURCES
                    /       |       \
                   /        |        \
              S3 files   PostgreSQL   Kafka
                 |           |          |
            Auto Loader   CDC/Connect  Stream
                 \           |          /
                  \          |         /
                   +---------+---------+
                             |
                   Lakeflow Declarative
                         Pipeline
                             |
                    Dependency Graph
                             |
                    +--------+--------+
                    |                 |
                 Bronze            Bronze
                    |                 |
                    +--------+--------+
                             |
                           Silver
                             |
                       Expectations
                             |
                      Quality Actions
                   /         |         \
                WARN        DROP       FAIL
                             |
                            Gold
                             |
                  Materialized Results
                             |
                        BI / ML / AI
```

### Layer responsibilities

**Sources** provide raw or change-oriented information.

**Ingestion** handles the source-specific mechanics.

**Bronze** preserves source-aligned data with minimal business transformation.

**Silver** applies normalization, business rules, quality enforcement, CDC application, and dimensional logic.

**Gold** exposes business-oriented products such as aggregates and analytical results.

**Expectations** make data-quality policy executable and observable.

**Lineage/event information** helps engineers understand what happened.

---

## 6. Core Terminology

| Term | Meaning |
|---|---|
| Pipeline | A managed collection of declarative dataset definitions and execution state |
| Dataset | A named data product produced by the pipeline |
| Flow | A logical ingestion/transformation path contributing data to a target |
| Source | External or upstream data entering a pipeline |
| Dependency | Relationship where one dataset requires another |
| Streaming table | Incrementally maintained table suited to streaming/append-oriented processing |
| Materialized view | Persisted derived result maintained from an underlying query |
| Temporary/intermediate view | Non-persistent logical transformation used inside pipeline logic where supported |
| Expectation | A data-quality rule attached to a dataset |
| Event log | Operational record used to understand pipeline updates, progress, quality results, and failures |
| Update | A pipeline execution/update cycle |
| Refresh | Recomputing or reprocessing a dataset according to supported refresh semantics |
| Full refresh | Recompute/reset behavior for a dataset rather than simply consuming new incremental input |
| Incremental update | Process newly available changes while retaining existing state/results |
| Development mode | Execution mode optimized for iterative development |
| Production mode | Controlled execution mode intended for stable production workloads |
| Triggered | Run, process available work, and stop |
| Continuous | Keep processing as new data becomes available |
| Expectation metric | Measurement of rows satisfying or violating a quality condition |
| CDC | Change Data Capture: inserts, updates, and deletes representing source changes |
| SCD1 | Slowly Changing Dimension Type 1: current value replaces historical value |
| SCD2 | Slowly Changing Dimension Type 2: preserve historical versions |

---

## 7. Dataset Types

The core design question is:

> **What kind of dataset are you trying to maintain?**

A useful first distinction is:

```text
Incoming / append-oriented data
        ↓
Streaming table

Derived analytical result
        ↓
Materialized view

Intermediate transformation
        ↓
Temporary/intermediate view where appropriate
```

Do not choose a dataset type because it sounds modern. Choose it because its semantics match the workload.

---

## 8. Streaming Tables

### 8.1 Simple explanation

A streaming table is an incrementally maintained dataset designed for workloads where new data arrives over time.

Conceptually:

```text
New data arrives
      ↓
Pipeline processes new data
      ↓
Existing state is retained
      ↓
Streaming table is updated
```

### 8.2 Typical workloads

- clickstream events
- order events
- application logs
- IoT events
- append-oriented transactional feeds
- files arriving through Auto Loader
- Kafka records

### 8.3 Minimum streaming context

You previously learned Structured Streaming. Here, the important concepts are:

- source
- offsets/checkpoint state
- incremental progress
- micro-batch execution conceptually
- freshness
- latency
- replay/recovery
- schema evolution
- late records

You do not need to re-learn the entire Structured Streaming API to reason about Lakeflow pipelines.

### 8.4 Streaming table example

Illustrative SQL pattern:

```sql
-- Illustrative pattern. Verify the current Lakeflow SQL syntax
-- and supported dataset declaration in your Databricks runtime.

CREATE OR REFRESH STREAMING TABLE silver_orders
AS
SELECT
    order_id,
    customer_id,
    amount,
    order_timestamp
FROM STREAM(bronze_orders);
```

**What the definition expresses:**

- `silver_orders` is a desired dataset.
- It depends on `bronze_orders`.
- The source is treated incrementally.
- The platform manages execution according to supported pipeline semantics.

### 8.5 When streaming tables fit

Use them when:

- input is naturally incremental
- new records arrive continuously or in batches
- replay/state semantics matter
- freshness is important
- recomputing the entire dataset would be wasteful

### 8.6 When they do not fit

Do not force a streaming table onto a workload whose primary requirement is:

- large derived aggregations
- broad recomputation
- complex analytical refresh
- a persisted query result whose semantics are better represented as a materialized view

---

## 9. Materialized Views

### 9.1 Simple explanation

A materialized view is a persisted derived result that Databricks maintains so consumers do not have to recompute the complete query on every access.

Example:

```sql
SELECT
    order_date,
    SUM(amount) AS daily_revenue
FROM orders
GROUP BY order_date;
```

The important question is not:

> "Can this SQL run?"

The important question is:

> "Should this derived result be maintained as a persisted analytical product?"

### 9.2 Typical workloads

- aggregations
- derived business metrics
- analytical joins
- curated reporting datasets
- BI-facing results
- query acceleration where supported

### 9.3 Trade-offs

Benefits:

- consumers query a persisted result
- avoids repeated ad hoc computation
- can provide predictable analytical access
- can simplify downstream BI

Costs/risks:

- maintenance consumes compute
- refresh behavior affects freshness
- complex transformations may be expensive
- the materialized result itself becomes an operational asset

### 9.4 Example

```sql
-- Illustrative SQL. Verify current supported Lakeflow syntax.

CREATE OR REFRESH MATERIALIZED VIEW gold_daily_revenue
AS
SELECT
    CAST(order_timestamp AS DATE) AS order_date,
    SUM(amount) AS daily_revenue
FROM silver_orders
GROUP BY CAST(order_timestamp AS DATE);
```

### 9.5 Key rule

> Do not use materialized views for append-only high-volume ingestion when a streaming table is the better fit.

Conversely:

> Do not use streaming tables for broad analytical aggregations when a materialized view is the more appropriate abstraction.

---

## 10. Temporary and Intermediate Views

Temporary/intermediate views allow transformations without turning every intermediate step into a persistent production table.

Conceptually:

```text
Raw source
   ↓
Intermediate transformation
   ↓
Silver streaming table
```

Use them when:

- an intermediate result has no independent consumer
- persisting it adds unnecessary storage and maintenance
- the transformation is naturally part of another dataset definition

Avoid using intermediate views as an excuse for:

- enormous monolithic definitions
- hidden business logic
- untestable transformations
- undocumented dependencies

A production design should make important data products visible and independently understandable.

---

## 11. Pipeline Configuration

### 11.1 Target catalog and schema

Unity Catalog provides the governance namespace:

```text
catalog
   ↓
schema
   ↓
dataset
```

Example conceptual environments:

```text
dev_catalog.analytics.orders
prod_catalog.analytics.orders
```

The target should be governed deliberately rather than embedded randomly throughout source code.

### 11.2 Configuration responsibilities

A production pipeline typically needs explicit decisions for:

- target catalog
- target schema
- source locations/connections
- execution mode
- compute
- permissions
- environment
- operational ownership
- quality policy

### 11.3 Compute

Topic 02 covered compute deeply. Here the decision is:

> What compute model gives this pipeline the cheapest adequate execution while meeting freshness and reliability requirements?

Consider:

- serverless vs classic
- workload size
- latency
- throughput
- startup characteristics
- operational overhead
- concurrency
- development vs production economics

Do not interpret "cheapest" as "smallest machine."

The correct principle is:

> **Cheapest adequate compute.**

---

## 12. Triggered vs Continuous Execution

### Triggered

```text
Run
 ↓
Process available data
 ↓
Stop
```

Useful for:

- scheduled ingestion
- hourly/daily workloads
- cost-sensitive pipelines
- workloads where minute-level latency is unnecessary

### Continuous

```text
Pipeline running
 ↓
New data arrives
 ↓
Process
 ↓
Continue
 ↓
New data arrives
```

Useful for:

- low-latency event processing
- operational dashboards
- near-real-time analytics
- continuously arriving critical feeds

### Comparison

| Dimension | Triggered | Continuous |
|---|---|---|
| Latency | Higher | Lower |
| Cost | Often easier to bound | Can accumulate continuously |
| Operations | Simpler | More continuously operational |
| Freshness | Schedule-dependent | Near-continuous |
| Best fit | Batch-like incremental workloads | Low-latency workloads |

Do not choose continuous mode merely because the data source is called "streaming." The business freshness requirement should drive the decision.

---

## 13. Development vs Production Mode

### Development mode

Optimized for:

- iteration
- debugging
- experimentation
- rapid feedback

### Production mode

Optimized for:

- stable execution
- controlled ownership
- predictable operations
- monitoring
- controlled permissions
- production cost management

### Production transition checklist

```text
Code reviewed
      ↓
Quality rules tested
      ↓
Environment target verified
      ↓
Permissions verified
      ↓
Observability verified
      ↓
Cost guardrails verified
      ↓
Production deployment
```

A common production failure is not a transformation bug. It is a development pipeline pointing at a production destination.

---

## 14. Expectations

### 14.1 Core concept

An expectation is a data-quality rule attached to a dataset.

Examples:

```text
order_id IS NOT NULL
```

```text
amount >= 0
```

Conceptually:

```text
Data
 ↓
Expectation
 ↓
Valid?
 ├── Yes → continue
 └── No  → configured action
```

### 14.2 Expectations are executable policy

Do not think of expectations as random assertions.

They express an operational contract:

```text
Dataset
   +
Quality rule
   +
Business severity
   =
Executable quality policy
```

### 14.3 Practical examples

```text
order_id IS NOT NULL
customer_id IS NOT NULL
amount >= 0
event_timestamp IS NOT NULL
country IN ('IN', 'US', 'GB')
email RLIKE '^[^@]+@[^@]+\\.[^@]+$'
```

Every rule should answer:

1. What does this protect?
2. What is the expected business invariant?
3. What happens if it fails?
4. Who owns the remediation?
5. How is the trend monitored?

---

## 15. Expectation Actions: WARN / DROP / FAIL

The correct action depends on severity.

### WARN / keep and record

Conceptually:

```text
Bad row
   ↓
Keep row
   ↓
Record quality result
```

Use when:

- the issue is suspicious rather than catastrophic
- you need observability
- downstream consumers can tolerate the row
- you want to measure a new quality problem before enforcing it

**Risk:** warnings can become permanent noise if nobody owns the metric.

### DROP

Conceptually:

```text
Bad row
   ↓
Remove
   ↓
Pipeline continues
```

Use when:

- invalid rows should not enter a downstream dataset
- dropping is explicitly acceptable
- valid downstream processing can continue safely

**Risk:** silent data loss.

Always measure how many rows were dropped and why.

### FAIL

Conceptually:

```text
Contract violation
   ↓
Pipeline update fails
   ↓
Engineer investigates
```

Use for:

- critical primary-key violations
- mandatory field failures
- contractual violations
- security/compliance-sensitive conditions
- conditions where downstream processing would be unsafe

**Risk:** overusing `FAIL` creates operational noise and brittle pipelines.

> Do not use `FAIL` for every non-critical quality rule.

---

## 16. Data Quality Architecture

A production quality architecture is layered:

```text
Source Contract
      ↓
Schema Validation
      ↓
Row-Level Expectations
      ↓
Business Rules
      ↓
Reconciliation
      ↓
Monitoring
```

### Quality dimensions

**Structural quality**

- schema compatibility
- required fields
- type validity

**Completeness**

- null checks
- missing records
- expected partitions

**Validity**

- ranges
- enumerations
- format rules

**Uniqueness**

- keys
- duplicate detection

**Referential integrity**

- valid customer/order relationships

**Business correctness**

- amount rules
- state transitions
- domain constraints

**Freshness**

- arrival latency
- processing lag
- expected update frequency

### Severity model

| Severity | Example | Action |
|---|---|---|
| Critical | Missing primary key | FAIL |
| Recoverable | Invalid optional row | DROP |
| Informational | Unexpected but usable country code | WARN |

The action is a policy decision, not merely a technical setting.

---

## 17. Expectation Metrics

Track at least conceptually:

- passed rows
- failed rows
- dropped rows
- pass percentage
- failure percentage
- expectation result
- trends over time
- affected dataset
- affected update

A green pipeline means:

> The execution completed according to its configured operational semantics.

It does **not** automatically mean:

> Data quality is 100%.

For example:

```text
Pipeline status = SUCCESS
Rows processed = 10,000,000
Rows dropped = 250,000
```

The pipeline can be operationally successful while the data-quality situation is unacceptable.

### Quality SLO thinking

Define targets such as:

```text
Critical expectation failures = 0
Drop rate < 0.1%
Freshness < 10 minutes
Duplicate rate < 0.01%
```

The exact thresholds must come from business requirements.

---

## 18. Event Log and Lineage

### 18.1 Event log

The event log is an operational evidence source for understanding pipeline activity.

Use it to reason about:

- pipeline progress
- updates
- errors
- expectations
- operational state
- lineage-related information
- execution diagnostics

### 18.2 Important safety rule

Event-log schemas and exact query interfaces can change with product versions.

> **Verify current Databricks documentation before using an exact event-log query, field name, or API.**

Do not fabricate table names or event fields.

### 18.3 Investigation model

When a pipeline is wrong:

```text
Symptom
  ↓
Identify update
  ↓
Inspect events
  ↓
Identify failing dataset
  ↓
Inspect source/input
  ↓
Inspect expectation results
  ↓
Inspect dependency
  ↓
Inspect code/configuration
  ↓
Fix
  ↓
Verify
```

### 18.4 Lineage

A typical lineage graph:

```text
Bronze
  ↓
Silver
  ↓
Gold
```

Lineage supports:

- debugging
- impact analysis
- governance
- incident response
- change management
- consumer communication

A dependency graph is not merely a scheduler artifact. It is a system-understanding artifact.

---

## 19. Automatic CDC

### 19.1 Why CDC is hard

Suppose the source emits:

```text
INSERT customer 1
UPDATE customer 1
DELETE customer 2
```

A custom implementation must reason about:

- ordering
- deduplication
- sequencing
- update semantics
- deletes
- late events
- replay
- idempotency
- target state

Conceptually:

```text
CDC source
   ↓
Change records
   ↓
Sequence changes
   ↓
Apply INSERT / UPDATE / DELETE
   ↓
Target table
```

Lakeflow Declarative Pipelines provides managed CDC/application capabilities for supported patterns.

The important engineering lesson is:

> A managed CDC abstraction reduces implementation plumbing; it does not remove the need to understand change semantics.

### 19.2 API safety

Exact CDC syntax and APIs are version-sensitive.

Use the current Databricks documentation for the exact implementation. Do not copy an old decorator, function, option, or parameter without checking its current support.

---

## 20. SCD Type 1

SCD1 maintains current state.

Before:

```text
customer_id | name
1           | Alice
```

After:

```text
customer_id | name
1           | Alicia
```

The old value is replaced.

### Useful for

- current customer dimensions
- current account attributes
- operational reporting
- cases where history is not required

### Limitation

You cannot answer:

> "What was the customer's name on March 1?"

because the prior value was intentionally overwritten.

---

## 21. SCD Type 2

SCD2 preserves historical versions.

Example:

```text
customer_id | name   | valid_from | valid_to   | current
1           | Alice  | 2025-01-01 | 2025-05-01 | false
1           | Alicia | 2025-05-01 | NULL       | true
```

It models:

- historical versions
- effective timestamps
- end timestamps
- current record
- sequencing
- deletes
- late changes
- out-of-order changes

### Why SCD2 matters

Business users may need:

- historical reporting
- auditability
- "as of" analysis
- customer segmentation at a past point in time
- regulatory traceability

### Production invariant

For a key with SCD2 history, you typically want:

```text
At most one current record
No overlapping validity windows
Correct sequencing
Correct delete semantics
```

Exact implementation depends on the CDC contract and current Lakeflow capabilities.

---

## 22. Sequencing and Out-of-Order Changes

Processing order is not arrival order.

Source sequence:

```text
seq=100 → Alice
seq=101 → Alison
seq=102 → Alicia
```

Arrival:

```text
100
102
101
```

If you apply arrival order blindly:

```text
Alice
→ Alicia
→ Alison
```

you can end with the wrong current state.

### Reliable sequencing

Possible sequencing evidence includes:

- source sequence number
- commit sequence
- monotonically increasing version
- source event timestamp when sufficiently reliable
- compound ordering keys

Consider:

- ties
- duplicate events
- clock skew
- missing sequence values
- replay
- late arrival

> **Processing order is not necessarily business-event order.**

For SCD2, sequencing is part of correctness, not a performance detail.

---

## 23. Delete Handling

CDC contains three fundamental change classes:

```text
INSERT
UPDATE
DELETE
```

A delete may mean different things:

### Hard delete

The current record should disappear.

### Soft delete

The record remains but gets a flag such as:

```text
is_deleted = true
```

### Tombstone

A CDC event represents deletion without carrying the complete prior row.

### SCD1 interpretation

The current representation is removed or marked according to business policy.

### SCD2 interpretation

Historical records may remain while the current version is closed/marked deleted.

Do not assume that "delete" means the same thing for every downstream consumer.

---

## 24. Auto Loader Integration

Topic 05 already covered Auto Loader in depth. Here the required context is integration:

```text
Files
  ↓
Auto Loader
  ↓
Streaming Table
  ↓
Expectations
  ↓
Silver
```

Example conceptual flow:

```text
cloudFiles source
      ↓
bronze_events
      ↓
quality checks
      ↓
silver_events
```

Relevant concerns:

- incremental file discovery
- checkpoint state
- schema evolution
- rescued data
- corrupt input
- file metadata
- source freshness

Do not reimplement Auto Loader mechanics inside every pipeline definition. Keep source-specific logic modular.

---

## 25. Kafka Integration

Kafka was covered earlier. Inside a declarative pipeline, the important mapping is:

```text
Kafka topic
   ↓
Streaming source
   ↓
Declarative pipeline
   ↓
Streaming table
```

Reason about:

- offsets
- partitions
- ordering
- checkpoints
- schema
- late events
- throughput
- consumer lag
- replay semantics

Do not assume partition arrival order equals global business-event order.

---

## 26. Full Refresh and Selective Refresh

### Incremental update

```text
Existing state
     +
New changes
     ↓
Updated dataset
```

### Full refresh

```text
Existing result
     ↓
Recompute/reset according to supported semantics
     ↓
New complete result
```

### Full refresh can be appropriate when

- source history was corrected
- transformation logic changed materially
- state is known to be invalid
- historical data must be reconstructed
- a controlled recovery requires recomputation

### Full refresh can be dangerous when

- the table is very large
- source data is expensive to scan
- downstream consumers depend on stable state
- the operation causes long downtime
- it hides an underlying incremental-processing bug

> Frequent full refreshes of large tables are often a bad operational strategy.

### Selective refresh

Prefer targeting the smallest affected dataset where the product supports selective refresh semantics.

Example graph:

```text
bronze.orders
      ↓
silver.orders
      ↓
gold.daily_revenue
```

If `silver.orders` is wrong, investigate whether the correct action is:

```text
repair bronze
→ refresh silver
→ refresh affected gold
```

rather than blindly rebuilding the entire pipeline.

Always verify current refresh controls and dependency behavior before executing a production refresh.

---

## 27. Flows

A flow is a logical data path contributing to a target.

Example:

```text
partner_a_orders ─┐
partner_b_orders ─┼──→ silver.orders
partner_c_orders ─┘
```

Multiple flows can be useful when:

- multiple partners produce equivalent feeds
- regional sources converge
- source-specific ingestion logic differs
- one target data product has multiple upstream producers

Production considerations:

- schema alignment
- source-specific quality
- deduplication
- ownership
- source attribution
- failure isolation
- idempotency

Add a source identifier when business consumers need to understand origin.

---

## 28. Backfills

A backfill repairs or populates historical data.

Suppose the source contains:

```text
2025-01-01 → 2025-01-10
```

but the pipeline only processed:

```text
2025-01-05 → 2025-01-10
```

You need a controlled strategy to recover:

```text
2025-01-01 → 2025-01-04
```

### Backfill checklist

```text
Define missing interval
      ↓
Identify source of truth
      ↓
Confirm idempotency
      ↓
Understand downstream dependencies
      ↓
Process historical interval
      ↓
Validate counts
      ↓
Validate business totals
      ↓
Check duplicates
      ↓
Check downstream products
```

### Backfill questions

- Is the source immutable?
- Can the same records arrive twice?
- Will CDC ordering remain correct?
- Does the target support safe replay?
- Will historical corrections alter gold metrics?
- Is the backfill within a maintenance window?
- What is the cost?

A backfill is a production change, not simply "run it again."

---

## 29. Late Data

Example:

```text
Event time:   10:00
Arrival:      10:30
```

The event is late by event-time semantics.

Distinguish:

- event time
- processing time
- arrival time

Structured Streaming concepts such as watermarks were covered earlier. Here the focus is pipeline consequences.

### Late data can affect

- aggregations
- windows
- SCD2 history
- freshness metrics
- reconciliation
- downstream BI

### Production strategy

Define:

```text
Expected lateness
      ↓
Watermark/processing policy
      ↓
Correction strategy
      ↓
Reconciliation
      ↓
Backfill if necessary
```

Never assume "processed successfully" means "event-time result is final."

---

## 30. Environment Parameterization

A production pipeline should not hardcode environment-specific destinations.

Bad:

```python
catalog = "prod_catalog"
```

Better conceptual design:

```text
Environment
   ↓
Configuration
   ↓
Target catalog/schema
   ↓
Pipeline
```

For example:

```text
DEV  → dev_catalog
TEST → test_catalog
PROD → prod_catalog
```

### Why this matters

Hardcoded environment values can cause:

- accidental production writes
- test data contamination
- incorrect permissions
- broken deployment automation
- confusing lineage
- cost attribution problems

### Parameterization principle

Keep:

- business transformation logic
- environment configuration
- deployment configuration

separate.

---

## 31. Modular Pipeline Design

Conceptual source organization:

```text
pipeline/
├── bronze/
├── silver/
├── gold/
├── quality/
└── shared/
```

This is an **illustrative structure only**. Do not create these directories as part of this document-generation task.

### Why modularity matters

Good modular organization improves:

- readability
- testability
- code reuse
- ownership
- dependency clarity
- change isolation
- reviewability

Avoid:

```text
one enormous pipeline source file
```

where ingestion, transformations, expectations, CDC, and business metrics are all interleaved.

A useful rule:

> A dataset definition should be understandable without requiring the engineer to mentally execute the entire platform.

---

## 32. Structured Streaming Comparison — Declarative Pipelines vs Custom Structured Streaming

| Dimension | Lakeflow Declarative Pipelines | Custom Structured Streaming |
|---|---|---|
| Abstraction | Higher | Lower |
| Execution control | Platform-managed | Engineer-managed |
| Dependency graph | Declarative | Usually explicit |
| State management | More managed | More custom |
| CDC | Managed patterns where supported | Engineer builds/maintains logic |
| Quality | Expectations | Custom checks/frameworks |
| Observability | Platform-integrated | Engineer assembles |
| Portability | More Databricks-specific | More Spark-portable |
| Flexibility | High within supported model | Very high |
| Operational effort | Lower for supported workloads | Higher |
| Debugging | Graph + platform evidence | Application + Spark evidence |
| Team skill | Databricks/Lakeflow expertise | Deep Spark/streaming expertise |
| Cost | Potentially efficient with managed execution | Depends on implementation |
| Best fit | Standardized production pipelines | Specialized/custom execution |

### Decision rule

Choose Lakeflow Declarative Pipelines when:

- the workload fits supported declarative semantics
- managed incremental processing is valuable
- expectations and lineage integration matter
- reduced operational plumbing is valuable

Choose custom Structured Streaming when:

- the required execution semantics are outside the declarative abstraction
- custom stateful processing is essential
- very specialized behavior is required
- portability/control outweighs platform convenience

---

## 33. dbt Comparison — Declarative Pipelines vs dbt

| Dimension | Lakeflow Declarative Pipelines | dbt |
|---|---|---|
| Primary strength | Managed Lakehouse pipelines | SQL-centric transformation engineering |
| SQL | Strong | Strong |
| Python | Supported in relevant pipeline patterns | More limited depending on execution/model |
| Streaming | Stronger native fit | Primarily batch/warehouse transformation model |
| CDC | Managed patterns available | Usually delegated to upstream ingestion/warehouse logic |
| Orchestration | Pipeline-native plus platform ecosystem | Usually paired with an orchestrator/platform |
| Quality | Expectations + platform integration | Tests/assertions + ecosystem |
| Lineage | Platform-native | Strong project lineage |
| Portability | Lower | Generally broader SQL ecosystem |
| Open ecosystem | More Databricks-centric | Broad ecosystem |
| Lock-in | Higher | Often lower |
| Operational model | Managed pipeline platform | Transformation framework |

### Choose dbt when

- the team is primarily SQL-oriented
- transformation logic is warehouse-style
- broad multi-platform portability matters
- dbt project conventions are already organizational standard

### Choose Lakeflow Declarative Pipelines when

- streaming is central
- CDC is central
- managed incremental execution matters
- Unity Catalog and Databricks platform integration are strategic
- operational pipeline management should be platform-native

These tools can coexist.

---

## 34. Apache Spark Declarative Pipeline Awareness

Declarative pipeline ideas are increasingly relevant to the broader Spark ecosystem.

The important distinction is:

```text
Databricks Lakeflow capability
          vs
Open-source Apache Spark capability
```

Do not assume feature parity.

A platform implementation can provide:

- managed control plane behavior
- integrated governance
- managed execution
- platform-specific expectations
- platform-specific event/operational features

An open-source project may expose related declarative ideas differently.

### Engineering principle

Learn the abstraction:

> Define data products and relationships, then let a compatible engine manage supported execution.

Then learn the platform-specific implementation separately.

---

## 35. Serverless Performance and Cost

A declarative abstraction does not eliminate performance engineering.

Consider:

```text
Data volume
×
Processing frequency
×
Compute
×
Inefficiency
```

This is a **conceptual model**, not an exact Databricks billing formula.

### Major cost drivers

- input volume
- update frequency
- continuous runtime
- full refreshes
- inefficient transformations
- concurrency
- materialized-view maintenance
- compute size
- pipeline complexity

### Performance questions

Before scaling compute, ask:

1. Is the workload unnecessarily recomputing data?
2. Is the source producing duplicates?
3. Is the dependency graph too broad?
4. Is a full refresh occurring unexpectedly?
5. Is the materialized result more expensive than expected?
6. Is data skew present?
7. Is the pipeline processing far more data than required?
8. Is continuous execution actually required?

### Cost principle

```text
Requirement
   ↓
Freshness
   ↓
Throughput
   ↓
Compute model
   ↓
Cheapest adequate execution
```

Not:

```text
Smallest compute possible
```

---

## 36. Security and Governance

Declarative pipelines do not automatically solve governance.

Separate:

```text
Pipeline capability
        vs
Governance capability
```

A governed architecture looks like:

```text
Pipeline
   ↓
Governed destination
   ↓
Unity Catalog
   ↓
Controlled consumers
```

### Controls

Use:

- Unity Catalog catalogs/schemas
- ownership
- least-privilege permissions
- service principals for automation where appropriate
- row filters
- column masks
- PII classification
- lineage
- auditability

### Production security checklist

```text
[ ] Correct identity
[ ] Least privilege
[ ] Correct target catalog
[ ] Correct target schema
[ ] PII controls
[ ] No accidental public exposure
[ ] Service principal reviewed
[ ] Environment isolation
[ ] Audit evidence
```

---

# 37. Hands-on Labs

All labs below are contained in this Markdown module. No external lab files are required.

---

## Lab 1 — First Declarative Pipeline

### Goal

Build:

```text
orders source
   ↓
bronze streaming table
   ↓
silver streaming table
   ↓
gold materialized view
```

### Tasks

1. Define the source.
2. Define bronze.
3. Define silver.
4. Add a quality rule.
5. Define a gold aggregation.
6. Draw the dependency graph.
7. Identify which datasets are incrementally maintained.
8. Explain why the gold result is derived.

### Expected evidence

```text
Source → Bronze → Silver → Gold
```

You should be able to explain every dependency.

### Failure exercise

Delete or intentionally break the upstream dataset definition.

Answer:

- Which downstream datasets are affected?
- Where should you inspect first?
- Why should you not immediately rebuild everything?

---

## Lab 2 — Streaming Table with Auto Loader

### Goal

Use JSON input and incremental file ingestion.

Conceptual flow:

```text
JSON files
   ↓
Auto Loader
   ↓
bronze_events
```

### Requirements

- JSON input
- incremental processing
- schema handling
- checkpoint/state
- output table

### Exercise

Add records over multiple runs.

Verify:

```text
Run 1 → files A/B
Run 2 → only newly available files
Run 3 → newly available files
```

### Break/fix

Introduce:

- malformed JSON
- schema change
- duplicate file arrival

Document expected behavior and recovery.

---

## Lab 3 — Materialized View

Build:

```text
gold.daily_revenue
```

from orders.

Example:

```sql
SELECT
    CAST(order_timestamp AS DATE) AS order_date,
    SUM(amount) AS daily_revenue
FROM silver_orders
GROUP BY CAST(order_timestamp AS DATE);
```

### Explain

- Why is this a derived product?
- Why is it not the ingestion layer?
- What freshness is required?
- What would make it expensive?
- Which consumers benefit?

---

## Lab 4 — Expectations

Create at least:

```text
order_id IS NOT NULL
amount >= 0
customer_id IS NOT NULL
```

Demonstrate three policies:

```text
WARN
DROP
FAIL
```

### Test data

Include:

```text
valid order
null order_id
negative amount
null customer_id
```

### Record

- number processed
- invalid rows
- action taken
- final quality percentage

### Discussion

Which rule should be `FAIL`?

Which rule could be `DROP`?

Which rule might initially be `WARN`?

---

## Lab 5 — Event Log Investigation

Inject bad records.

Investigate:

- quality metrics
- pipeline events
- errors
- affected dataset
- lineage/dependency

Use current Databricks documentation for exact event-log query syntax.

### Deliverable

Write an incident timeline:

```text
12:01 — update started
12:02 — dataset processed
12:03 — expectation violations increased
12:03 — quality policy triggered
12:04 — investigation started
```

---

## Lab 6 — CDC SCD Type 1

Create a customer change stream:

```text
INSERT customer 1
UPDATE customer 1
DELETE customer 2
```

Demonstrate:

- initial state
- update
- delete
- final current state

### Questions

- What is the source key?
- What is the sequencing field?
- What does delete mean?
- Is history required?

---

## Lab 7 — CDC SCD Type 2

Build the conceptual target:

```text
silver.dim_customer
```

with:

- history
- sequence
- effective timestamps
- current record
- deletes
- out-of-order events

### Test sequence

Source:

```text
1, Alice, seq=100
1, Alison, seq=101
1, Alicia, seq=102
```

Arrival:

```text
100
102
101
```

### Required outcome

The latest source sequence should determine current state, not arbitrary arrival order.

Validate:

```text
No overlapping validity windows
One current record
Correct historical sequence
Correct delete behavior
```

---

## Lab 8 — Full Refresh

Run a controlled full refresh of one dataset.

Document:

- what changed
- runtime
- records processed
- downstream effect
- cost implication
- why the refresh was justified

### Reflection

What would happen if the dataset contained 5 TB instead of 5 GB?

---

## Lab 9 — Backfill

Create a historical gap:

```text
Jan 01 → Jan 10 expected
Jan 05 → Jan 10 present
```

Backfill:

```text
Jan 01 → Jan 04
```

Verify:

- no duplicates
- correct timestamps
- correct row counts
- correct business totals
- downstream correctness

---

## Lab 10 — Late Data

Introduce events with:

```text
event_time = 10:00
arrival_time = 10:30
```

Measure:

- freshness
- aggregate impact
- correction behavior

Explain whether the final result is immediately correct or requires a correction/backfill policy.

---

## Lab 11 — Multiple Flows

Simulate:

```text
partner_a
partner_b
partner_c
```

feeding:

```text
silver.orders
```

Test:

- schema differences
- duplicate orders
- source attribution
- bad partner records
- one partner being unavailable

---

## Lab 12 — Environment Parameterization

Create conceptual:

```text
DEV → dev_catalog
PROD → prod_catalog
```

Run the same logical pipeline definition against each environment.

### Failure exercise

Intentionally configure development to target production.

Then answer:

- What evidence would expose the mistake?
- What permission boundary should prevent damage?
- What deployment guardrail should prevent recurrence?

---

## Lab 13 — Architecture Comparison

Implement the same conceptual workload three ways:

1. Lakeflow Declarative Pipeline
2. Structured Streaming + custom state/merge logic
3. dbt-oriented transformation architecture

Compare:

| Dimension | Your finding |
|---|---|
| Code size | |
| Operational effort | |
| Data quality | |
| Observability | |
| Cost | |
| Portability | |
| CDC complexity | |
| Streaming fit | |
| Team skill requirements | |

Do not choose a winner in advance. Explain the workload-specific trade-off.

---

# 38. Break/Fix Incidents

Use the following production incidents as diagnostic exercises.

## Incident 1 — Expectation failure stops pipeline

**Symptoms**

- update fails
- one quality rule reports widespread violations

**Initial hypothesis**

The new source release may violate a contract.

**Evidence**

Inspect expectation metrics, source schema, and affected update.

**Root cause**

A mandatory field became nullable.

**Fix**

Coordinate source contract correction or implement a controlled compatibility strategy.

**Verification**

Replay representative input and confirm critical violations return to zero.

**Prevention**

Schema contract monitoring and source-change review.

**Runbook entry**

Use the expectation-failure runbook below.

---

## Incident 2 — Too many rows are being dropped

**Symptoms**

Pipeline succeeds but output volume falls 30%.

**Initial hypothesis**

A quality rule is too strict.

**Evidence**

Compare source/output counts and expectation-level failure percentages.

**Root cause**

A country-code rule did not include a newly introduced legitimate country.

**Fix**

Update the business rule after validation.

**Verification**

Reprocess affected data and reconcile counts.

**Prevention**

Versioned domain-value contracts.

---

## Incident 3 — Streaming table is not receiving new data

**Symptoms**

Table is stale.

**Evidence**

Check source arrival, checkpoint/update progress, permissions, schema, and pipeline events.

**Possible root causes**

- no new input
- source connectivity
- checkpoint/state issue
- schema problem
- pipeline not executing

**Fix**

Identify evidence before restarting.

**Verification**

Confirm new source records appear exactly once according to expected semantics.

---

## Incident 4 — Materialized view is unexpectedly expensive

**Symptoms**

Compute usage increases sharply.

**Evidence**

Inspect refresh frequency, source volume, query shape, and dependency changes.

**Root causes**

- broader source scan
- transformation change
- full recomputation
- unnecessary refresh frequency

**Fix**

Reduce unnecessary work, redesign the result, or revisit dataset type.

---

## Incident 5 — CDC produces incorrect current state

**Symptoms**

Customer state is wrong.

**Evidence**

Inspect source sequence values and arrival order.

**Root cause**

Arrival order was used instead of reliable source sequencing.

**Fix**

Use the correct sequence semantics supported by the CDC design.

---

## Incident 6 — Out-of-order CDC corrupts history

**Symptoms**

SCD2 versions overlap or current record is wrong.

**Evidence**

Compare source sequence against target validity windows.

**Root cause**

Late sequence was treated as latest arrival.

**Fix**

Correct sequence-aware application and reprocess affected history.

---

## Incident 7 — Delete events are missing

**Symptoms**

Deleted customers remain active.

**Evidence**

Check whether delete/tombstone events exist upstream and whether the ingestion path preserves them.

**Root cause**

The source connector or transformation discarded deletes.

**Fix**

Restore delete semantics and repair affected records.

---

## Incident 8 — Full refresh takes several hours

**Symptoms**

A refresh exceeds its normal window.

**Evidence**

Compare input volume, historical size, execution plan, and prior incremental runtime.

**Root cause**

A large dataset was rebuilt unnecessarily.

**Fix**

Use incremental processing where valid; reserve full refresh for justified recovery/reconstruction.

---

## Incident 9 — Late data produces incorrect aggregates

**Symptoms**

Yesterday's dashboard is later corrected unexpectedly.

**Evidence**

Compare event time and arrival time.

**Root cause**

Business consumers assumed early aggregates were final.

**Fix**

Define lateness/correction semantics and communicate freshness.

---

## Incident 10 — Pipeline succeeds but data quality is poor

**Symptoms**

Pipeline status is green; users report incorrect data.

**Evidence**

Inspect expectation metrics, reconciliation, business totals, freshness, and source completeness.

**Root cause**

Operational success was treated as data correctness.

**Fix**

Add business-quality SLOs and reconciliation.

---

## Incident 11 — Development pipeline writes to production

**Symptoms**

Development records appear in production.

**Evidence**

Inspect target catalog/schema, pipeline configuration, deployment identity, and lineage.

**Root cause**

Hardcoded production target.

**Fix**

Parameterize environment and enforce deployment guardrails.

---

## Incident 12 — Serverless pipeline cost unexpectedly increases

**Symptoms**

Daily spend rises sharply.

**Evidence**

Compare data volume, execution frequency, continuous runtime, refresh behavior, and transformation changes.

**Root cause**

An unintended continuous workload and repeated recomputation.

**Fix**

Correct execution mode and eliminate unnecessary recomputation.

---

# 39. Production Runbooks

## Runbook 1 — Pipeline Failed

```text
SYMPTOM
↓
Identify failed update
↓
Inspect event/error evidence
↓
Identify dataset
↓
Check source
↓
Check quality
↓
Check dependency/configuration
↓
FIX
↓
VERIFICATION
↓
PREVENTION
```

Do not restart blindly.

---

## Runbook 2 — Expectation Failure

1. Identify failing expectation.
2. Quantify failed rows.
3. Identify source/version change.
4. Determine severity.
5. Decide whether `WARN`, `DROP`, or `FAIL` remains appropriate.
6. Repair data or rule.
7. Reprocess safely.
8. Verify quality metrics.

---

## Runbook 3 — Too Many Records Dropped

1. Compare source/output counts.
2. Group violations by expectation.
3. Inspect sample invalid records.
4. Determine whether source or rule changed.
5. Validate business impact.
6. Fix rule/source.
7. Reprocess affected interval.
8. Reconcile.

---

## Runbook 4 — Streaming Table Stale

Check:

- source arrival
- pipeline trigger
- update state
- checkpoint/state
- permissions
- schema
- errors
- upstream dependencies

Only restart after evidence identifies restart as a valid corrective action.

---

## Runbook 5 — CDC State Incorrect

Check:

- source sequence
- duplicate changes
- arrival order
- delete events
- replay behavior
- target current-state invariant

Then repair the smallest affected interval possible.

---

## Runbook 6 — SCD2 History Incorrect

Validate:

```text
One current record
No overlapping validity windows
Correct sequence
Correct effective timestamps
Correct delete behavior
```

Trace the source change feed before editing target records manually.

---

## Runbook 7 — Late Data Issue

1. Quantify lateness distribution.
2. Separate event time from processing time.
3. Identify affected aggregates.
4. Determine correction policy.
5. Recompute/backfill affected interval.
6. Verify downstream results.

---

## Runbook 8 — Full Refresh Decision

Ask:

- Is state corrupted?
- Is source history authoritative?
- Can incremental repair solve it?
- What is the dataset size?
- What downstream consumers are affected?
- What is the expected cost?
- Is the maintenance window sufficient?

If the answers do not justify a full refresh, prefer a narrower repair.

---

## Runbook 9 — Backfill Procedure

```text
Define interval
↓
Validate source
↓
Check idempotency
↓
Assess downstream impact
↓
Execute controlled backfill
↓
Reconcile
↓
Monitor
↓
Document
```

---

## Runbook 10 — Event-Log Investigation

Use:

```text
Update
↓
Dataset
↓
Event/error
↓
Expectation
↓
Source
↓
Dependency
↓
Configuration
```

Use current documentation for exact event-log query syntax.

---

## Runbook 11 — Cost Spike

Compare against the previous baseline:

- input volume
- run count
- continuous runtime
- refresh type
- compute
- transformation changes
- materialized-view maintenance

Do not assume the compute size is the root cause.

---

## Runbook 12 — Wrong Environment Target

Immediately:

1. stop further writes if safe
2. identify affected datasets
3. identify deployment identity
4. inspect configuration
5. assess data impact
6. correct target parameterization
7. validate permissions
8. document incident

---

# 40. Decision Matrices

## 40.1 Streaming Table vs Materialized View

| Workload | Streaming Table | Materialized View |
|---|---|---|
| High-volume append ingestion | Recommended | Usually not first choice |
| Continuous events | Strong fit | Usually downstream |
| Simple incremental transformations | Strong fit | Possible but not primary |
| Aggregations | Possible depending on semantics | Strong fit |
| Analytical derived result | Usually not ideal | Strong fit |
| Freshness-sensitive ingestion | Strong fit | Depends on maintenance |
| Broad recomputation | Usually not ideal | Often more appropriate |
| Main risk | State/source semantics | Maintenance cost |

---

## 40.2 Declarative Pipeline vs Custom Structured Streaming

| Decision factor | Prefer Declarative | Prefer Custom |
|---|---|---|
| Managed execution | Yes | Less important |
| Custom state | Limited/unsupported requirement | Strong |
| Platform integration | Critical | Less critical |
| Portability | Less important | Critical |
| CDC abstraction | Valuable | Need custom behavior |
| Operational burden | Reduce | Accept |
| Specialized algorithm | No | Yes |

---

## 40.3 Declarative Pipeline vs dbt

| Decision factor | Lakeflow | dbt |
|---|---|---|
| Streaming | Strong | Usually not primary |
| CDC | Stronger managed fit | Usually external |
| SQL transformation | Strong | Strong |
| Python | Stronger platform integration | Depends on architecture |
| Databricks-native governance | Strong | Strong when integrated, but different abstraction |
| Portability | Lower | Higher |
| Existing dbt organization | Possible coexistence | Strong reason to use dbt |
| Managed pipeline execution | Strong | Usually paired with orchestration |

---

## 40.4 WARN vs DROP vs FAIL

| Condition | WARN | DROP | FAIL |
|---|---:|---:|---:|
| Suspicious but usable | Strong | No | No |
| Invalid row must not propagate | No | Strong | Possible |
| Critical contract violation | No | Usually no | Strong |
| Compliance-sensitive | Usually insufficient | Depends | Strong |
| Exploratory monitoring | Strong | No | No |

---

## 40.5 Incremental vs Full Refresh

| Condition | Incremental | Full Refresh |
|---|---:|---:|
| New append data | Strong | No |
| Large historical dataset | Strong | Expensive |
| Correcting state corruption | Maybe | Strong candidate |
| Transformation rewrite | Maybe | Possible |
| Cost sensitivity | Strong | Weak |
| Recovery from source reconstruction | Depends | Strong candidate |

---

## 40.6 Triggered vs Continuous

| Requirement | Triggered | Continuous |
|---|---:|---:|
| Daily analytics | Strong | Usually unnecessary |
| Hourly pipeline | Strong | Usually unnecessary |
| Near-real-time dashboard | Possible | Strong |
| Low operational complexity | Strong | Lower |
| Lowest idle compute | Strong | Depends |
| Constant freshness | Weak | Strong |

---

# 41. Architecture Decision Records

## ADR 1 — Streaming Table vs Materialized View

**Context:** Orders arrive continuously and daily revenue is consumed by BI.

**Problem:** Should the revenue dataset itself be an ingestion-oriented streaming table?

**Options:**
1. Streaming table
2. Materialized view
3. Custom batch job

**Decision:** Use a streaming table for incremental order ingestion and a materialized view for the derived revenue result, assuming the workload fits current supported semantics.

**Why:** Separates ingestion semantics from analytical-result maintenance.

**Trade-offs:** Additional dataset and maintenance layer.

**Risks:** Unexpected materialized-view maintenance cost.

**Cost:** Measure source volume, refresh frequency, and compute.

**Operational impact:** Two observable products instead of one.

**Future reconsideration trigger:** Requirements change to specialized stateful processing.

---

## ADR 2 — Declarative Pipeline vs Custom Structured Streaming

**Context:** The workload is standard event ingestion with quality and CDC requirements.

**Problem:** Custom state logic would require substantial operational plumbing.

**Options:** Lakeflow Declarative Pipelines or custom Structured Streaming.

**Decision:** Prefer Lakeflow Declarative Pipelines while the workload remains inside supported semantics.

**Why:** Managed dependencies, quality, CDC patterns, and operational integration reduce engineering overhead.

**Trade-offs:** Lower portability and less low-level control.

**Risks:** Platform-specific feature changes.

**Cost:** Validate serverless economics with real workload measurements.

**Future reconsideration trigger:** Required behavior cannot be represented safely in the declarative model.

---

## ADR 3 — Declarative Pipeline vs dbt

**Context:** The platform contains both streaming ingestion and warehouse-style transformations.

**Problem:** One transformation framework should not be forced onto every workload.

**Decision:** Use Lakeflow for streaming/CDC/pipeline-native workloads and dbt where SQL-first transformation conventions provide higher value; integrate them deliberately.

**Why:** Each abstraction is stronger in different workload categories.

**Trade-offs:** More than one development model.

**Risks:** Duplicate logic and ownership confusion.

**Cost:** Include operational complexity in total cost.

**Future reconsideration trigger:** Organization standardizes on one platform model.

---

## ADR 4 — WARN vs DROP vs FAIL

**Context:** A quality rule detects invalid customer records.

**Decision:** Classify by business severity.

**Why:** Prevents both silent corruption and unnecessary pipeline failures.

**Trade-offs:** More policy design.

**Risks:** Poor thresholds can hide quality degradation.

**Cost:** Failed pipelines can have operational cost; dropped data can have business cost.

**Future reconsideration trigger:** Data contract changes.

---

## ADR 5 — Incremental Processing vs Full Refresh

**Context:** A large silver table needs correction.

**Decision:** Prefer incremental repair when correctness permits; reserve full refresh for justified reconstruction.

**Why:** Reduces cost, runtime, and downstream disruption.

**Trade-offs:** Incremental repair may require more reasoning.

**Risks:** Partial repair can leave hidden inconsistencies.

**Future reconsideration trigger:** State is proven unrecoverable incrementally.

---

# 42. Common Mistakes

## Mistake 1 — Materialized view for append-only high-volume data

**Why it happens:** "Materialized" sounds efficient.

**Why dangerous:** Maintenance may be expensive for an ingestion workload.

**Detection:** Unexpected compute/refresh behavior.

**Prevention:** Model ingestion as a streaming table when appropriate.

---

## Mistake 2 — Streaming table for broad recomputation

**Why it happens:** Streaming is treated as the universal answer.

**Why dangerous:** The workload semantics may not fit incremental maintenance.

**Detection:** Excessive recomputation or complex correction behavior.

**Prevention:** Evaluate a materialized result.

---

## Mistake 3 — FAIL for every quality rule

**Why it happens:** Failing feels safest.

**Why dangerous:** Operators become overwhelmed by non-critical failures.

**Detection:** High failure frequency with low business impact.

**Prevention:** Classify quality rules by severity.

---

## Mistake 4 — Ignoring expectation metrics

**Why it happens:** Green pipeline status creates false confidence.

**Why dangerous:** Data can be wrong while execution is successful.

**Detection:** Reconciliation mismatch.

**Prevention:** Quality SLOs and dashboards.

---

## Mistake 5 — Frequent full refreshes

**Why it happens:** Full refresh appears simpler.

**Why dangerous:** Cost and runtime scale with data volume.

**Detection:** Large scans and long updates.

**Prevention:** Fix incremental semantics.

---

## Mistake 6 — Blindly trusting the dependency graph

**Why dangerous:** Correct graph does not guarantee correct source semantics.

**Prevention:** Validate source contracts and business invariants.

---

## Mistake 7 — Weak CDC sequencing

**Why dangerous:** Arrival order can produce incorrect state.

**Prevention:** Use reliable source sequencing.

---

## Mistake 8 — Ignoring late data

**Why dangerous:** Event-time results can be wrong or temporarily incomplete.

**Prevention:** Define lateness and correction policy.

---

## Mistake 9 — No reconciliation

**Why dangerous:** Quality rules may not detect missing but individually valid records.

**Prevention:** Source-to-target counts and business totals.

---

## Mistake 10 — No quality ownership

**Why dangerous:** Warnings accumulate without action.

**Prevention:** Assign owner, threshold, SLA, and escalation.

---

## Mistake 11 — Hardcoded environments

**Why dangerous:** Development can write to production.

**Prevention:** Parameterization plus deployment controls.

---

## Mistake 12 — Overusing temporary views

**Why dangerous:** Important business logic becomes hidden.

**Prevention:** Persist meaningful data products and document transformations.

---

## Mistake 13 — Monolithic pipelines

**Why dangerous:** Changes become difficult to test and review.

**Prevention:** Modular dataset definitions.

---

## Mistake 14 — No production observability

**Why dangerous:** Engineers discover failures through consumers.

**Prevention:** Event evidence, metrics, freshness, reconciliation, alerts.

---

## Mistake 15 — No cost controls

**Why dangerous:** Continuous processing and recomputation can grow spend quickly.

**Prevention:** Measure volume, frequency, runtime, and compute.

---

## Mistake 16 — Confusing pipeline success with data correctness

**Why dangerous:** Execution health and business correctness are different dimensions.

**Prevention:** Quality SLOs and reconciliation.

---

# 43. Mental Models

## Mental Model 1

```text
Declarative
=
Tell the platform WHAT you want
not every step of HOW to execute it
```

The engineer still controls the model, contracts, governance, and requirements.

---

## Mental Model 2

```text
Streaming Table
=
Continuously/incrementally maintained dataset
```

Think incoming state, not simply "table with streaming code."

---

## Mental Model 3

```text
Materialized View
=
Persisted derived result kept up to date
```

Think analytical product, not raw ingestion.

---

## Mental Model 4

```text
Expectation
=
Data-quality contract attached to a dataset
```

A quality rule should have a business owner and severity.

---

## Mental Model 5

```text
WARN
=
Keep + measure

DROP
=
Remove + continue

FAIL
=
Stop + investigate
```

---

## Mental Model 6

```text
CDC
=
Change + ordering + application + correctness
```

CDC without sequencing is not a reliable state-management strategy.

---

## Mental Model 7

```text
Pipeline Success
≠
Data Correctness
```

Always operate both dimensions.

---

# 44. Interview Preparation

## Basic — 15

### B1
**Question:** What is declarative data engineering?

**Expected thinking:** Contrast desired state with execution steps.

**Strong answer:** Declarative data engineering describes datasets and relationships while the platform manages supported execution details.

**Why:** It separates data-product intent from orchestration plumbing.

**Follow-up:** Does declarative mean engineers no longer need Spark knowledge?

---

### B2
**Question:** What is a streaming table?

**Expected thinking:** Incremental dataset semantics.

**Strong answer:** An incrementally maintained table suited to streaming/append-oriented data.

**Why:** It aligns source arrival with incremental processing.

**Follow-up:** When would you prefer a materialized view?

---

### B3
**Question:** What is a materialized view?

**Expected thinking:** Persisted derived result.

**Strong answer:** A maintained derived result that avoids recomputing the query from scratch for every consumer query.

**Why:** It is an analytical data product.

**Follow-up:** What can make it expensive?

---

### B4
**Question:** What is an expectation?

**Expected thinking:** Quality contract.

**Strong answer:** A data-quality rule attached to a dataset with a configured response to violations.

**Why:** It turns quality policy into executable behavior.

**Follow-up:** Explain WARN/DROP/FAIL.

---

### B5
**Question:** Why is pipeline success not data correctness?

**Expected thinking:** Execution vs business quality.

**Strong answer:** A pipeline can execute successfully while expectations, completeness, freshness, or reconciliation indicate incorrect data.

**Why:** Operational success is only one health dimension.

**Follow-up:** Give a metric.

---

### B6
**Question:** What is SCD1?

**Expected thinking:** Current-state dimension.

**Strong answer:** SCD1 overwrites the prior attribute value.

**Why:** It intentionally does not preserve attribute history.

**Follow-up:** When is that desirable?

---

### B7
**Question:** What is SCD2?

**Expected thinking:** Historical versions.

**Strong answer:** SCD2 preserves versions using validity/current-state metadata.

**Why:** It supports historical analysis.

**Follow-up:** Why does sequencing matter?

---

### B8
**Question:** Why does CDC need ordering?

**Expected thinking:** Arrival is not event order.

**Strong answer:** Updates must be applied according to reliable source sequence rather than arbitrary arrival order.

**Why:** Otherwise current state and history can be wrong.

**Follow-up:** How do you handle late events?

---

### B9
**Question:** What is a full refresh?

**Expected thinking:** Recompute rather than incremental update.

**Strong answer:** A refresh that reconstructs the relevant result according to supported semantics rather than consuming only new incremental changes.

**Why:** Useful for controlled reconstruction but expensive at scale.

**Follow-up:** When is it dangerous?

---

### B10
**Question:** What is a backfill?

**Expected thinking:** Historical recovery.

**Strong answer:** Controlled processing of a missing/corrected historical interval.

**Why:** It restores historical completeness.

**Follow-up:** What validates a successful backfill?

---

### B11
**Question:** What is late data?

**Expected thinking:** Event time vs arrival.

**Strong answer:** Data whose event time precedes its arrival/processing time beyond the expected delay.

**Why:** It can change previously computed results.

**Follow-up:** How do you correct aggregates?

---

### B12
**Question:** What is a flow?

**Expected thinking:** Source path into target.

**Strong answer:** A logical ingestion/transformation path contributing to a target dataset.

**Why:** Multiple source paths can converge into one data product.

**Follow-up:** What can go wrong?

---

### B13
**Question:** Why parameterize environments?

**Expected thinking:** Prevent accidental cross-environment writes.

**Strong answer:** To keep the same logic deployable across dev/test/prod without hardcoded destinations.

**Why:** It reduces deployment risk.

**Follow-up:** What guardrail should exist?

---

### B14
**Question:** What does the event log help with?

**Expected thinking:** Evidence.

**Strong answer:** It provides operational information about updates, progress, quality results, and failures.

**Why:** Diagnosis should be evidence-driven.

**Follow-up:** Is its exact schema permanent?

---

### B15
**Question:** Why are expectations not a complete data-quality system?

**Expected thinking:** Layered quality.

**Strong answer:** Expectations cover row/dataset rules, but completeness, reconciliation, source contracts, freshness, and business correctness also matter.

**Why:** No single quality mechanism catches every failure mode.

**Follow-up:** Give a reconciliation example.

---

## Intermediate — 15

### I1
**Question:** When should an orders ingestion dataset be a streaming table rather than a materialized view?**

**Expected thinking:** Ingestion semantics.

**Strong answer:** When the workload is primarily incremental/append-oriented and freshness is driven by arriving orders. A materialized view is more appropriate for derived analytical results.

**Why:** The dataset type matches the workload.

**Follow-up:** What if the orders table is rebuilt nightly?

---

### I2
**Question:** When should an expectation use WARN?**

**Expected thinking:** Severity.

**Strong answer:** When the data is suspicious but retaining it is acceptable and the team wants measurable visibility.

**Why:** WARN preserves data while creating evidence.

**Follow-up:** How do you prevent warning fatigue?

---

### I3
**Question:** When should invalid rows be dropped?

**Expected thinking:** Explicit loss policy.

**Strong answer:** When the rows are known invalid, downstream processing must exclude them, and business owners accept the loss with metrics and remediation.

**Why:** DROP is a data-loss action and must be intentional.

**Follow-up:** What metric should you monitor?

---

### I4
**Question:** Why can FAIL be harmful?

**Expected thinking:** Operational severity.

**Strong answer:** If applied to non-critical issues, it creates noisy failures and operational instability.

**Why:** Pipeline availability becomes tied to low-severity anomalies.

**Follow-up:** Give a critical example.

---

### I5
**Question:** How would you investigate a stale streaming table?

**Expected thinking:** Evidence chain.

**Strong answer:** Check source arrival, pipeline execution/update state, source permissions/schema, checkpoint/state behavior, upstream dependencies, and event evidence before restarting.

**Why:** Staleness has many possible causes.

**Follow-up:** What would prove source starvation?

---

### I6
**Question:** How does lineage help incident response?

**Expected thinking:** Impact analysis.

**Strong answer:** It identifies upstream causes and downstream consumers affected by a dataset change.

**Why:** It reduces diagnostic search space.

**Follow-up:** How does it help change management?

---

### I7
**Question:** Why can a pipeline be green while losing 2% of records?

**Expected thinking:** Completeness vs execution.

**Strong answer:** If no configured failure condition catches the loss, the execution can succeed while source-to-target reconciliation reveals missing records.

**Why:** Pipeline health is not completeness.

**Follow-up:** What checks would you add?

---

### I8
**Question:** Explain SCD2 with an out-of-order update.

**Expected thinking:** Source sequence.

**Strong answer:** Preserve versions according to source sequence, not arrival order, and maintain non-overlapping validity intervals.

**Why:** Arrival order can be wrong.

**Follow-up:** What if two events have the same sequence?

---

### I9
**Question:** Why are full refreshes dangerous on large tables?

**Expected thinking:** Volume × compute.

**Strong answer:** They can scan/recompute large volumes, increase runtime and cost, and affect downstream consumers.

**Why:** Incremental processing avoids unnecessary work.

**Follow-up:** When would you accept one?

---

### I10
**Question:** How should you design a backfill?

**Expected thinking:** Controlled historical repair.

**Strong answer:** Define interval, verify source truth, confirm idempotency, assess dependencies, execute narrowly, reconcile, and document.

**Why:** Backfills can alter business history.

**Follow-up:** How do you prevent duplicates?

---

### I11
**Question:** How does Auto Loader fit into a declarative pipeline?

**Expected thinking:** Ingestion abstraction.

**Strong answer:** Auto Loader discovers/processes arriving files incrementally, while the declarative pipeline defines the resulting dataset and quality/dependency behavior.

**Why:** Source ingestion and dataset orchestration have different responsibilities.

**Follow-up:** What state does file ingestion depend on?

---

### I12
**Question:** What Kafka concepts still matter inside Lakeflow?

**Expected thinking:** Source semantics remain.

**Strong answer:** Partitions, offsets, ordering, checkpoints, schema, lag, and late data still matter.

**Why:** Abstraction does not erase source behavior.

**Follow-up:** Does Kafka partition order imply global event order?

---

### I13
**Question:** Why parameterize catalogs and schemas?

**Expected thinking:** Deployment safety.

**Strong answer:** Environment-specific configuration should not be hardcoded into transformation logic.

**Why:** It reduces accidental production writes.

**Follow-up:** How would you test it?

---

### I14
**Question:** When might dbt be preferable?

**Expected thinking:** Workload/team fit.

**Strong answer:** SQL-first analytical transformation workloads with strong dbt conventions and portability requirements may fit dbt better.

**Why:** Tool choice should follow workload.

**Follow-up:** Can dbt and Lakeflow coexist?

---

### I15
**Question:** What does serverless change for a pipeline engineer?

**Expected thinking:** Operational abstraction.

**Strong answer:** It reduces infrastructure-management work but does not eliminate decisions about workload shape, latency, volume, cost, and performance.

**Why:** Managed compute still has consumption economics.

**Follow-up:** What causes cost spikes?

---

## Advanced — 15

### A1
**Question:** A customer CDC feed contains sequence 100, 102, then 101. How do you preserve SCD2 correctness?**

**Expected thinking:** Sequence-aware application.

**Strong answer:** Treat source sequence as the authoritative ordering signal, detect/reconcile the late 101 event, and ensure target validity windows and current state reflect source order.

**Why:** Arrival order is not business order.

**Follow-up:** What if 101 arrives after 102 has already been consumed?

---

### A2
**Question:** 30% of rows fail an expectation. Should the pipeline fail?**

**Expected thinking:** Severity/business policy.

**Strong answer:** Not automatically. Determine whether the rule is critical, whether the source changed, whether the invalid rows are safe to drop, and what downstream risk exists.

**Why:** Failure policy must be evidence- and business-driven.

**Follow-up:** What if the field is a regulated identifier?

---

### A3
**Question:** The pipeline is green, but source count is 10 million and target count is 9.8 million. What do you investigate?**

**Expected thinking:** Reconciliation.

**Strong answer:** Inspect expectation drops, source completeness, duplicates, filters, partition gaps, late data, CDC behavior, and update boundaries.

**Why:** Missing records are not necessarily execution failures.

**Follow-up:** How would you isolate the missing 200k?

---

### A4
**Question:** A materialized view suddenly becomes expensive. What is your diagnostic order?**

**Expected thinking:** Evidence before scaling.

**Strong answer:** Compare volume, refresh frequency, query changes, dependency changes, refresh type, and execution evidence; identify unnecessary recomputation before increasing compute.

**Why:** Compute scaling can hide the root cause.

**Follow-up:** What would indicate a source-volume problem?

---

### A5
**Question:** A full refresh is requested because "the table looks wrong." What do you do?**

**Expected thinking:** Challenge recovery strategy.

**Strong answer:** Establish the defect, identify the affected interval, determine whether incremental repair is possible, assess source truth and downstream impact, then decide.

**Why:** Full refresh is a recovery action, not a default troubleshooting step.

**Follow-up:** When is full reconstruction justified?

---

### A6
**Question:** How would you design quality policy for customer data?**

**Expected thinking:** Layered quality.

**Strong answer:** Combine schema checks, key completeness, validity, uniqueness, referential integrity, business rules, freshness, reconciliation, and severity-based expectations.

**Why:** Row-level checks alone are insufficient.

**Follow-up:** Which rule should block production?

---

### A7
**Question:** How do you distinguish source failure from pipeline failure?**

**Expected thinking:** Dependency evidence.

**Strong answer:** Compare source arrival/health with pipeline execution, update events, permissions, and processing progress.

**Why:** A stale table can have a healthy pipeline and an empty source.

**Follow-up:** What metrics prove source starvation?

---

### A8
**Question:** How do you make backfills safe?**

**Expected thinking:** Idempotency and bounded scope.

**Strong answer:** Use an explicit interval, authoritative source, deterministic keys, duplicate detection, dependency assessment, reconciliation, and rollback/recovery planning.

**Why:** Historical writes can alter downstream truth.

**Follow-up:** What if consumers are reading during the backfill?

---

### A9
**Question:** When should you use custom Structured Streaming instead of Lakeflow?**

**Expected thinking:** Abstraction boundary.

**Strong answer:** When required stateful or execution behavior is not safely expressible in the declarative platform or when portability/control outweighs managed operational benefits.

**Why:** Do not force specialized workloads into an abstraction that does not fit.

**Follow-up:** What operational burden returns?

---

### A10
**Question:** When would dbt and Lakeflow coexist?**

**Expected thinking:** Separate transformation domains.

**Strong answer:** Use Lakeflow for streaming/CDC/managed ingestion and dbt for SQL-first analytical transformations where its project model provides value.

**Why:** Different abstractions can be complementary.

**Follow-up:** How do you avoid duplicate business logic?

---

### A11
**Question:** How do you prevent development-to-production contamination?**

**Expected thinking:** Defense in depth.

**Strong answer:** Parameterize environments, isolate catalogs/schemas, use identity/permission boundaries, validate deployment configuration, and add pre-production checks.

**Why:** No single control is sufficient.

**Follow-up:** Which control is last-resort containment?

---

### A12
**Question:** What does "incremental" actually mean operationally?**

**Expected thinking:** State and source semantics.

**Strong answer:** It means processing only newly relevant changes while preserving previously processed state/result according to the dataset's supported semantics; it does not mean "run less code."

**Why:** Incrementality depends on source and state semantics.

**Follow-up:** What breaks incremental correctness?

---

### A13
**Question:** How would you reason about late data in a daily revenue product?**

**Expected thinking:** Event-time correctness.

**Strong answer:** Define expected lateness, decide whether daily results are provisional, establish correction/backfill semantics, and expose freshness/finality to consumers.

**Why:** Revenue metrics often have financial consequences.

**Follow-up:** How would you communicate provisional values?

---

### A14
**Question:** How do expectations interact with reconciliation?**

**Expected thinking:** Different failure classes.

**Strong answer:** Expectations detect record-level/data-rule violations; reconciliation detects missing/excess records or business totals across boundaries.

**Why:** A record can satisfy every row rule and still be missing from the dataset.

**Follow-up:** Give an example.

---

### A15
**Question:** What is the most important production skill in declarative pipelines?**

**Expected thinking:** Systems thinking.

**Strong answer:** Understanding the semantics behind the abstraction—source behavior, dependency graph, state, quality, refresh, governance, and cost—rather than memorizing syntax.

**Why:** APIs change; engineering principles persist.

**Follow-up:** What evidence would you inspect during an incident?

---

## Production/System Design — 10

### P1
**Question:** Design a production pipeline for S3 clickstream, PostgreSQL orders, CRM CDC, and Kafka events.**

**Expected thinking:** Source-specific ingestion plus unified quality/governance.

**Strong answer:** Use Auto Loader for files, managed CDC/connect patterns for PostgreSQL/CRM where supported, Kafka streaming for events, declarative bronze/silver/gold layers, expectations, SCD2 for customer history, materialized analytical products, Unity Catalog governance, event monitoring, parameterized environments, and cost controls.

**Why:** Each source is handled according to its semantics.

**Follow-up:** How do you handle late data?

---

### P2
**Question:** Design SCD2 for a high-value customer dimension with deletes and out-of-order changes.**

**Expected thinking:** Correct sequencing and historical invariants.

**Strong answer:** Define authoritative source sequence, preserve historical versions, represent deletes explicitly, detect duplicates, and reconcile validity windows.

**Why:** Business history must remain deterministic.

**Follow-up:** What is your repair strategy?

---

### P3
**Question:** Design quality controls for a payments pipeline.**

**Expected thinking:** Criticality classification.

**Strong answer:** Fail on critical identifiers/security conditions, drop explicitly invalid rows where business policy allows, warn on anomalies, and add reconciliation/freshness checks.

**Why:** Payments need defense in depth.

**Follow-up:** What quality metrics become SLOs?

---

### P4
**Question:** A pipeline processes 50 TB daily and costs far more than expected. What is your optimization strategy?**

**Expected thinking:** Work elimination first.

**Strong answer:** Measure input/output volume, remove unnecessary full refreshes, reduce unnecessary columns/data, validate incremental semantics, inspect expensive derived results, choose adequate compute, and monitor cost after each change.

**Why:** Optimization should reduce work before increasing hardware.

**Follow-up:** How do you validate no correctness regression?

---

### P5
**Question:** Design a multi-environment Lakeflow platform.**

**Expected thinking:** Separation and promotion.

**Strong answer:** Separate dev/test/prod targets, parameterize environment configuration, use controlled identities and permissions, promote reviewed definitions, and verify target destinations before production execution.

**Why:** Environment isolation is a safety requirement.

**Follow-up:** What prevents a bad configuration from writing to prod?

---

### P6
**Question:** How would you build an incident-response process for declarative pipelines?**

**Expected thinking:** Evidence-driven operations.

**Strong answer:** Define alerts, event evidence, dataset ownership, runbooks, quality SLOs, source health checks, dependency/lineage investigation, recovery procedures, and post-incident prevention.

**Why:** A pipeline platform needs an operating model.

**Follow-up:** What should not be the first action?

---

### P7
**Question:** When would you reject Lakeflow in favor of custom Spark?**

**Expected thinking:** Abstraction fit.

**Strong answer:** Reject it when required stateful semantics, execution control, portability, or specialized algorithms cannot be expressed safely and economically within the supported declarative model.

**Why:** Platform convenience must not compromise correctness.

**Follow-up:** What new operational burden appears?

---

### P8
**Question:** When would you reject dbt in favor of Lakeflow?**

**Expected thinking:** Streaming/CDC requirements.

**Strong answer:** When the dominant requirement is managed streaming ingestion, CDC, event-driven incremental state, and platform-native operational integration.

**Why:** These workloads require capabilities beyond conventional SQL transformation.

**Follow-up:** Could dbt still be used downstream?

---

### P9
**Question:** A green pipeline is producing incorrect executive revenue numbers. How do you respond?**

**Expected thinking:** Business-critical incident.

**Strong answer:** Freeze unsafe downstream consumption if needed, establish source/target reconciliation, inspect quality metrics, identify missing/duplicate/late records, trace lineage, quantify impact, correct the smallest safe interval, validate financial totals, and document prevention.

**Why:** Business correctness takes priority over a green execution status.

**Follow-up:** What evidence supports declaring recovery complete?

---

### P10
**Question:** Design the operating standard for a Lakeflow platform.**

**Expected thinking:** End-to-end engineering.

**Strong answer:**

```text
SOURCE
→ CONNECT
→ DECLARE
→ GRAPH
→ INGEST
→ VALIDATE
→ APPLY CDC
→ GOVERN
→ OBSERVE
→ RECONCILE
→ OPTIMIZE
→ RECOVER
→ DOCUMENT
```

**Why:** Production data engineering is a lifecycle, not a code-generation exercise.

**Follow-up:** Which stages require explicit ownership?

---

# 45. Practice Questions

## Basic — 10

### Q1
What is the difference between declarative and imperative pipeline design?

**Answer:** Declarative design specifies desired datasets and relationships; imperative design specifies execution steps.

---

### Q2
When is a streaming table a natural fit?

**Answer:** Incremental, append-oriented, continuously arriving workloads.

---

### Q3
When is a materialized view a natural fit?

**Answer:** Persisted derived results such as analytical aggregations.

---

### Q4
What is an expectation?

**Answer:** A data-quality rule attached to a dataset.

---

### Q5
What does WARN do conceptually?

**Answer:** Keeps the data while recording quality violations.

---

### Q6
What does DROP do conceptually?

**Answer:** Removes invalid rows and continues processing.

---

### Q7
What does FAIL do conceptually?

**Answer:** Stops the pipeline update when the configured rule is violated.

---

### Q8
What is SCD1?

**Answer:** Current state replaces historical attribute values.

---

### Q9
What is SCD2?

**Answer:** Historical versions are preserved.

---

### Q10
Why is sequencing important in CDC?

**Answer:** Because arrival order may differ from source-event order.

---

## Intermediate — 10

### Q11
A pipeline is green but output count is lower than source count. What do you inspect?

**Answer:** Expectations, filters, duplicates, source completeness, partition gaps, late data, CDC semantics, and reconciliation.

---

### Q12
When should you choose DROP instead of FAIL?

**Answer:** When invalid rows are explicitly non-critical and business policy permits excluding them.

---

### Q13
Why can full refresh be expensive?

**Answer:** It can recompute large volumes instead of processing only new changes.

---

### Q14
What makes a backfill safe?

**Answer:** Bounded interval, authoritative source, idempotency, dependency analysis, reconciliation, and monitoring.

---

### Q15
What is late data?

**Answer:** Data that arrives after the expected processing point relative to event time.

---

### Q16
Why parameterize environments?

**Answer:** To prevent hardcoded destinations and make promotion safe.

---

### Q17
Why is an event log useful?

**Answer:** It provides operational evidence for updates, quality, progress, and failures.

---

### Q18
Why is lineage valuable?

**Answer:** It supports debugging, impact analysis, governance, and change management.

---

### Q19
Why can declarative pipelines reduce operational effort?

**Answer:** They move supported dependency, incremental, quality, and execution concerns into a managed platform abstraction.

---

### Q20
When might custom Structured Streaming be better?

**Answer:** When specialized stateful/execution requirements exceed the declarative abstraction.

---

## Advanced — 10

### Q21
A customer update with sequence 101 arrives after 102. What is your strategy?

**Answer:** Apply according to authoritative source sequence, reconcile affected history, and preserve deterministic SCD2 invariants.

---

### Q22
30% of rows fail a quality rule. Should you fail?

**Answer:** Not automatically. Classify severity, inspect source change, business impact, and downstream risk.

---

### Q23
A materialized view cost doubles. What should you do before increasing compute?

**Answer:** Inspect data volume, refresh frequency, query/dependency changes, and unnecessary recomputation.

---

### Q24
A pipeline has frequent full refreshes. What does that suggest?

**Answer:** Either a deliberate reconstruction requirement or an incremental-processing design problem that needs investigation.

---

### Q25
How do you distinguish pipeline staleness from source staleness?

**Answer:** Compare source arrival/health with pipeline execution/update evidence.

---

### Q26
How can expectation metrics and reconciliation complement each other?

**Answer:** Expectations detect rule violations; reconciliation detects missing/excess data and business-total mismatches.

---

### Q27
What is the danger of treating arrival order as CDC order?

**Answer:** It can produce incorrect current state and historical validity.

---

### Q28
How would you prevent development writes to production?

**Answer:** Environment parameterization, isolated targets, least privilege, deployment validation, and automated guardrails.

---

### Q29
When would you use dbt downstream of Lakeflow?

**Answer:** When SQL-first analytical transformations benefit from dbt conventions after streaming/CDC ingestion has produced governed datasets.

---

### Q30
What does "cheapest adequate compute" mean?

**Answer:** The lowest-cost execution configuration that meets workload correctness, freshness, throughput, and reliability requirements.

---

## Expert / Production — 10

### Q31
A 50 TB pipeline has a 6-hour SLA but currently takes 11 hours. What is your approach?

**Answer:** Establish baseline, identify data processed versus necessary, remove full refreshes, optimize incremental semantics, inspect skew/recomputation, evaluate materialized-result strategy, and then size compute based on evidence.

---

### Q32
A financial revenue table is wrong because late events arrived after close. What do you do?

**Answer:** Determine finality policy, quantify impact, apply controlled correction/backfill, reconcile totals, communicate revised values, and update freshness/finality expectations.

---

### Q33
A source silently stops sending delete events. What breaks?

**Answer:** Current-state targets can retain records that should be removed, and SCD2 current/history semantics can become incorrect.

---

### Q34
A source changes a nullable field to mandatory but downstream expectations still WARN. What is the engineering concern?

**Answer:** The pipeline may continue while violating a new contract; severity and source contract must be reassessed.

---

### Q35
How do you decide between a full refresh and a targeted backfill?

**Answer:** Use the smallest operation that restores correctness safely, considering state corruption, dependency scope, data volume, source truth, and downstream impact.

---

### Q36
A declarative pipeline is operationally simple but cannot express a required custom state machine. What do you do?

**Answer:** Step outside the abstraction for that component using custom Structured Streaming or another appropriate engine, while preserving governance and operational standards.

---

### Q37
How would you prove a pipeline is production-ready?

**Answer:** Demonstrate correctness, quality SLOs, lineage, observability, failure recovery, security, environment isolation, cost controls, repeatable deployment, backfill strategy, and operational ownership.

---

### Q38
How would you design quality ownership?

**Answer:** Each critical rule has an owner, threshold, severity, alert, remediation SLA, and documented business rationale.

---

### Q39
What evidence is required before declaring an incident resolved?

**Answer:** Corrected pipeline execution, reconciled counts/totals, restored freshness, expected quality metrics, downstream validation, and prevention actions.

---

### Q40
What is the most important architectural principle in this module?

**Answer:**

> **Choose dataset semantics, quality policy, incremental behavior, and execution mode from the workload—not from feature popularity.**

---

# 46. Production Capstone

## Scenario

A company has four sources:

```text
S3 clickstream files
PostgreSQL orders
CRM customer CDC
Kafka events
```

### Target architecture

```text
                         SOURCES
                            |
             +--------------+--------------+
             |              |              |
          S3 files      PostgreSQL       Kafka
             |              |              |
        Auto Loader     CDC/Connect      Streaming
             |              |              |
             +--------------+--------------+
                            |
                 Lakeflow Declarative
                       Pipeline
                            |
                      +-----+-----+
                      |           |
                   Bronze       Bronze
                      |           |
                      +-----+-----+
                            |
                          Silver
                            |
                      Expectations
                            |
                    SCD Type 2 Customer
                            |
                           Gold
                            |
                  +---------+---------+
                  |                   |
                 BI                  ML/AI
```

### Required capabilities

Your capstone must include:

- streaming tables
- materialized views
- expectations
- WARN
- DROP
- FAIL
- CDC
- SCD Type 2
- deletes
- out-of-order events
- late data
- backfills
- event-log monitoring
- environment parameterization
- governance
- cost optimization

### Required documentation

Document:

1. architecture
2. dependencies
3. source strategy
4. quality rules
5. CDC strategy
6. SCD strategy
7. late-data strategy
8. backfill strategy
9. monitoring
10. governance
11. cost
12. failure recovery
13. ADRs
14. trade-offs

### Capstone acceptance criteria

```text
[ ] Dataset graph is explicit
[ ] Every source has a source-specific ingestion strategy
[ ] Critical quality rules have explicit severity
[ ] CDC sequencing is documented
[ ] SCD2 invariants are documented
[ ] Delete semantics are documented
[ ] Late-data policy is documented
[ ] Backfill procedure is documented
[ ] Environment targets are parameterized
[ ] Governance is enforced
[ ] Event evidence is monitored
[ ] Cost is measured
[ ] Failure recovery is tested
[ ] Architecture decisions are recorded
```

---

# 47. Final Knowledge Checkpoint

```text
[ ] I understand declarative data engineering.
[ ] I can explain declarative vs imperative pipelines.
[ ] I understand dependency graphs.
[ ] I understand streaming tables.
[ ] I understand materialized views.
[ ] I understand temporary/intermediate views.
[ ] I can reason about target catalogs and schemas.
[ ] I understand serverless/classic compute choices for pipelines.
[ ] I understand triggered execution.
[ ] I understand continuous execution.
[ ] I understand development mode.
[ ] I understand production mode.
[ ] I understand expectations.
[ ] I can choose WARN.
[ ] I can choose DROP.
[ ] I can choose FAIL.
[ ] I understand expectation metrics.
[ ] I can use event evidence for investigation.
[ ] I understand lineage.
[ ] I understand automatic CDC concepts.
[ ] I understand SCD Type 1.
[ ] I understand SCD Type 2.
[ ] I understand sequencing.
[ ] I understand delete handling.
[ ] I understand out-of-order CDC.
[ ] I can use Auto Loader inside a pipeline.
[ ] I understand Kafka integration.
[ ] I understand incremental updates.
[ ] I understand full refresh.
[ ] I understand selective refresh.
[ ] I understand flows.
[ ] I understand backfills.
[ ] I understand late data.
[ ] I can parameterize environments.
[ ] I can organize pipeline source code modularly.
[ ] I can compare declarative pipelines with Structured Streaming.
[ ] I can compare declarative pipelines with dbt.
[ ] I understand Apache Spark declarative-pipeline awareness.
[ ] I understand serverless pipeline performance/cost.
[ ] I can troubleshoot pipeline failures.
[ ] I can investigate data-quality problems.
[ ] I can design a production declarative pipeline.
```

---

# 48. Roadmap Coverage Audit

| Roadmap Requirement | Covered? | Section | Code Example? | Hands-on? | Production Depth? |
|---|---|---|---|---|---|
| Declarative model | COMPLETE | 3–4 | Yes | Lab 1 | Yes |
| SQL datasets | COMPLETE | 8–9 | Yes | Lab 1 | Yes |
| Python datasets | COMPLETE | 54 / version-safe implementation guidance | Yes | Labs | Yes |
| Dependency graph | COMPLETE | 3–5, 17 | Yes | Lab 1 | Yes |
| Streaming tables | COMPLETE | 7–8 | Yes | Labs 1–2 | Yes |
| Materialized views | COMPLETE | 9 | Yes | Lab 3 | Yes |
| Temporary views | COMPLETE | 10 | Conceptual | Lab 1 | Yes |
| Target catalog/schema | COMPLETE | 11, 29 | Conceptual | Lab 12 | Yes |
| Serverless/classic compute | COMPLETE | 11, 34 | Conceptual | Lab 13 | Yes |
| Triggered mode | COMPLETE | 12 | Conceptual | Lab 13 | Yes |
| Continuous mode | COMPLETE | 12 | Conceptual | Lab 13 | Yes |
| Development mode | COMPLETE | 13 | Conceptual | Lab 12 | Yes |
| Production mode | COMPLETE | 13 | Conceptual | Lab 12 | Yes |
| Expectations | COMPLETE | 14–16 | Yes | Lab 4 | Yes |
| WARN | COMPLETE | 15 | Yes | Lab 4 | Yes |
| DROP | COMPLETE | 15 | Yes | Lab 4 | Yes |
| FAIL | COMPLETE | 15 | Yes | Lab 4 | Yes |
| Expectation metrics | COMPLETE | 17 | Yes | Lab 4–5 | Yes |
| Automatic CDC | COMPLETE | 19 | Version-safe conceptual patterns | Labs 6–7 | Yes |
| SCD Type 1 | COMPLETE | 20 | Conceptual | Lab 6 | Yes |
| SCD Type 2 | COMPLETE | 21 | Conceptual | Lab 7 | Yes |
| Sequencing | COMPLETE | 22 | Yes | Lab 7 | Yes |
| Delete handling | COMPLETE | 23 | Conceptual | Labs 6–7 | Yes |
| Auto Loader | COMPLETE | 24 | Yes | Lab 2 | Yes |
| Kafka | COMPLETE | 25 | Conceptual | Lab 13 | Yes |
| Event log | COMPLETE | 17 | Version-safe guidance | Lab 5 | Yes |
| Lineage | COMPLETE | 17 | Conceptual | Lab 5 | Yes |
| Full refresh | COMPLETE | 26 | Conceptual | Lab 8 | Yes |
| Selective refresh | COMPLETE | 26 | Conceptual | Lab 8 | Yes |
| Flows | COMPLETE | 27 | Conceptual | Lab 11 | Yes |
| Backfills | COMPLETE | 28 | Yes | Lab 9 | Yes |
| Late data | COMPLETE | 29 | Conceptual | Lab 10 | Yes |
| Environment parameterization | COMPLETE | 30 | Yes | Lab 12 | Yes |
| Modular source files | COMPLETE | 31 | Yes | Lab 13 | Yes |
| Structured Streaming comparison | COMPLETE | 32 | No | Lab 13 | Yes |
| dbt comparison | COMPLETE | 33 | No | Lab 13 | Yes |
| Apache Spark declarative pipelines awareness | COMPLETE | 34 | No | Lab 13 | Yes |
| Serverless performance/cost | COMPLETE | 35 | Conceptual | Lab 13 | Yes |
| Security/governance | COMPLETE | 36 | Conceptual | Capstone | Yes |
| Hands-on labs | COMPLETE | 37 | Yes | 13 labs | Yes |
| Break/fix incidents | COMPLETE | 38 | No | 12 incidents | Yes |
| Production runbooks | COMPLETE | 39 | No | Yes | Yes |
| Decision matrices | COMPLETE | 40 | No | Yes | Yes |
| ADRs | COMPLETE | 41 | No | Yes | Yes |
| Interview questions | COMPLETE | 43 | No | Yes | Yes |
| Practice questions | COMPLETE | 44 | No | Yes | Yes |
| Production capstone | COMPLETE | 45 | Yes | Yes | Yes |
| Final knowledge checkpoint | COMPLETE | 46 | No | Yes | Yes |
| Roadmap audit | COMPLETE | 47 | No | Yes | Yes |

### Audit result

**COMPLETE**

No required Topic 07 concept is intentionally omitted.

---

# 49. Completion Checklist

```text
[ ] Topic 07 scope matches the G4 roadmap.
[ ] Spark fundamentals are not unnecessarily re-taught.
[ ] Declarative model is explained from first principles.
[ ] Streaming tables are explained.
[ ] Materialized views are explained.
[ ] Temporary views are explained.
[ ] Expectations are treated as production quality policy.
[ ] WARN/DROP/FAIL are differentiated.
[ ] Expectation metrics are covered.
[ ] Event-log use is evidence-driven.
[ ] Lineage is covered.
[ ] CDC and SCD1/SCD2 are covered.
[ ] Sequencing and out-of-order changes are covered.
[ ] Delete semantics are covered.
[ ] Auto Loader and Kafka integration are covered.
[ ] Full/selective refresh are covered.
[ ] Flows are covered.
[ ] Backfills are covered.
[ ] Late data is covered.
[ ] Environment parameterization is covered.
[ ] Modular organization is covered.
[ ] Structured Streaming comparison is covered.
[ ] dbt comparison is covered.
[ ] Apache Spark declarative-pipeline awareness is covered.
[ ] Serverless performance/cost is covered.
[ ] Security/governance is covered.
[ ] 13 hands-on labs are included.
[ ] 12 break/fix incidents are included.
[ ] 12 production runbooks are included.
[ ] 6 decision matrices are included.
[ ] 5 ADRs are included.
[ ] 55 interview questions are included.
[ ] 40 practice questions are included.
[ ] Production capstone is included.
[ ] Final knowledge checkpoint is included.
[ ] Roadmap coverage audit is included.
[ ] Exact version-sensitive APIs are explicitly treated as verify-before-production.
[ ] No fabricated current API/schema/price claims are presented as stable facts.
```

## Final Operating Standard

For production Lakeflow Declarative Pipelines, think:

```text
SOURCE
  ↓
CONNECT
  ↓
DECLARE
  ↓
GRAPH
  ↓
INGEST
  ↓
VALIDATE
  ↓
APPLY CDC
  ↓
GOVERN
  ↓
OBSERVE
  ↓
RECONCILE
  ↓
OPTIMIZE
  ↓
RECOVER
  ↓
DOCUMENT
```

The central principle is:

> **Managed declarative pipelines reduce plumbing, not responsibility.**

You remain responsible for source semantics, correctness, quality, sequencing, governance, cost, recovery, and the business meaning of the resulting data products.
