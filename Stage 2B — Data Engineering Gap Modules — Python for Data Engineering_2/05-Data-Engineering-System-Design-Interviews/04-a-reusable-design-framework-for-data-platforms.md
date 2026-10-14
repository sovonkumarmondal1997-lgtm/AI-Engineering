# Topic 04 — A Reusable Design Framework for Data Platforms

> **Stage:** G5 — Data Engineering System Design Interviews  
> **Purpose:** Learn a repeatable framework for structuring Data Engineering system-design problems under interview pressure.  
> **Progression:** Absolute Beginner → Foundation → Basic → Intermediate → Advanced → Senior → Staff → Interview Mastery → Production Thinking

---

## 1. What This Module Teaches

A system-design interview is not primarily a technology-recall exercise. The difficult part is remembering **what to consider**, in what order, while requirements are ambiguous and time is limited.

This module teaches a reusable thinking framework:

```text
Requirements
    ↓
Estimates
    ↓
High-Level Data Flow
    ↓
Data Model & Storage
    ↓
Processing
    ↓
Serving
    ↓
Cross-Cutting Concerns
    ↓
Failure Handling
    ↓
Evolution
```

The framework is a **map, not a script**.

The learner should finish this module able to take a prompt such as:

> "Design a data platform for a rapidly growing application."

and systematically ask:

```text
What are the requirements?
        ↓
What is the scale?
        ↓
What does the data flow look like?
        ↓
What is the data model and grain?
        ↓
Where is data stored?
        ↓
How is it processed?
        ↓
How is it served?
        ↓
How do we protect correctness and reliability?
        ↓
What can fail and how do we recover?
        ↓
What changes at 10× scale?
        ↓
What trade-offs are we making?
```

### Scope boundary

This module teaches **how to structure and reason about Data Engineering system design**. It does not become a full Kafka, Spark, Airflow, Databricks, AWS, ML, RAG, or security course. Those technologies are building blocks from elsewhere in the roadmap.

---

# 2. Why a Reusable Framework Is Necessary

Without a framework, candidates commonly jump directly to:

```text
Kafka → Spark → S3 → Snowflake
```

That can sound impressive while still being a poor design.

The better sequence is:

```text
Requirements
→ Scale
→ Data flow
→ Storage
→ Processing
→ Serving
→ Reliability
→ Security
→ Cost
→ Evolution
```

The framework reduces:

- **Cognitive load** — fewer important dimensions are forgotten.
- **Time pressure** — the candidate always knows the next design layer.
- **Ambiguity** — requirements are converted into explicit assumptions.
- **Architecture drift** — choices remain connected to requirements.
- **Failure blindness** — failure and recovery become mandatory.
- **Communication problems** — the interviewer can follow the design.
- **Interview risk** — the candidate reaches reliability, cost, and evolution instead of spending the entire interview on the happy path.

> **Framework principle:** The framework determines what questions to ask; requirements determine what technologies to choose.

---

# 3. The Master Framework

```text
┌─────────────────────────────┐
│ 1. Requirements             │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ 2. Estimates                │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ 3. High-Level Data Flow     │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ 4. Data Model & Storage     │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ 5. Processing               │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ 6. Serving                  │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ 7. Cross-Cutting Concerns   │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ 8. Failure Handling         │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ 9. Evolution                │
└─────────────────────────────┘
```

A useful high-level Data Engineering flow is:

```text
Sources
  ↓
Ingestion
  ↓
Raw / Bronze
  ↓
Transformation
  ↓
Silver
  ↓
Business Aggregation
  ↓
Gold
  ↓
Serving
  ↓
Consumers
```

Bronze/Silver/Gold are **conceptual data layers**, not mandatory physical databases.

---

# 4. Stage 1 — Requirements

## 4.1 What is it?

Requirements define what the system must accomplish and the constraints within which it must operate.

This module builds on Topic 02 rather than repeating it.

### Functional requirements

Ask:

- What data enters the system?
- What capabilities must the platform provide?
- What products or workflows consume the data?
- What questions must the data answer?
- What transformations or derived products are required?

### Non-functional requirements

Clarify:

- Freshness
- Latency
- Volume
- Growth
- Correctness
- Availability
- Retention
- Security
- Privacy
- Cost

The design chain is:

```text
Requirements
    ↓
Constraints
    ↓
Architecture boundaries
```

### Example

```text
Requirement:
Dashboard must be less than 5 minutes stale.

Likely consequence:
Near-real-time or frequent micro-batch processing may be required.
```

The requirement does not automatically dictate one technology. It creates an architectural constraint.

## 4.2 Requirements → Design Consequences

| Requirement | Likely design consequence |
|---|---|
| Sub-second latency | Low-latency serving path |
| 24-hour freshness | Batch may be sufficient |
| Exactly-once business effect | Strong idempotency/deduplication |
| Seven-year retention | Lifecycle/tiered storage |
| 100 TB/day | Distributed infrastructure |
| EU personal data | Privacy and governance controls |
| Financial reporting | Auditability and reconciliation |
| 99.99% availability | Redundancy and recovery strategy |

### Interview communication

> "Before selecting technologies, I want to clarify freshness, scale, correctness, consumers, retention, availability, security, and cost. Those constraints will drive the architecture."

## 4.3 Requirement Questions

| Question | Why it matters |
|---|---|
| How fresh must the data be? | Determines batch vs frequent vs streaming possibilities |
| How much data arrives? | Establishes capacity boundaries |
| Is the source mutable? | May require CDC/history semantics |
| Can data be replayed? | Determines recovery and backfill options |
| Who consumes the output? | Determines serving interface |
| What is the retention period? | Drives storage and lifecycle |
| What does correctness mean? | Defines quality and reconciliation requirements |
| What availability is required? | Defines resilience expectations |
| Is data sensitive? | Drives privacy/security/governance |
| What cost boundary exists? | Prevents technically elegant but uneconomic designs |

---

# 5. Stage 2 — Estimates

Topic 03 teaches estimation in depth. Topic 04 uses those estimates to set architecture boundaries.

Estimate enough to understand:

- Daily volume
- Average throughput
- Peak throughput
- Storage
- Retention
- Compute
- Serving QPS
- Cost
- Growth

The integration is:

```text
Requirements
    ↓
Estimates
    ↓
Capacity boundaries
    ↓
Architecture choices
```

### Example

Suppose:

```text
500 GB/day
5-minute freshness
1-year retention
```

You now know that storage, processing frequency, retention strategy, and serving design cannot be chosen blindly.

> **Interview rule:** Estimate before making expensive architecture commitments.

Do not repeat every formula from Topic 03 here. The purpose is to **use estimates to drive design**.

---

# 6. Stage 3 — High-Level Data Flow

Start with the simplest useful architecture:

```text
Sources
   ↓
Ingestion
   ↓
Raw / Bronze
   ↓
Transformation
   ↓
Silver
   ↓
Business Aggregation
   ↓
Gold
   ↓
Serving
   ↓
Consumers
```

Each block answers a different question:

| Layer | Core question |
|---|---|
| Sources | Where does data originate? |
| Ingestion | How does data enter the platform? |
| Bronze | How do we preserve source fidelity and replayability? |
| Silver | How do we clean, validate, deduplicate, and standardize? |
| Gold | What business-ready products do consumers need? |
| Serving | How is the output exposed efficiently? |
| Consumers | Who uses the result and with what latency? |

Do not add components merely to make the diagram look sophisticated.

---

# 7. Sources

Common source categories:

- Application databases
- APIs
- SaaS systems
- Files
- Event streams
- CDC feeds
- IoT devices
- Logs
- External partners

For every source, ask:

1. What is its arrival pattern?
2. Is it append-only or mutable?
3. Is it transactional?
4. What is its schema behavior?
5. Can it replay?
6. What happens when it is unavailable?
7. Who owns the source?
8. What correctness guarantees exist?

| Source | Typical pattern | Important design concern |
|---|---|---|
| Application DB | Mutable transactional records | CDC, consistency, source load |
| API | Request/response | Rate limits, pagination, retries |
| SaaS | Managed external source | API limits, schema changes |
| Files | Batch objects | Arrival detection, partial files |
| Event stream | Continuous events | Ordering, duplicates, lag |
| CDC | Database changes | Ordering, deletes, schema evolution |
| IoT | High-rate telemetry | Volume, connectivity, burstiness |
| Logs | Append-heavy | Volume, parsing, retention |
| Partner feed | External contract | Contract stability, reconciliation |

---

# 8. Ingestion

Ingestion is a design decision, not simply a product choice.

## 8.1 Batch

Appropriate when:

- Freshness requirements are measured in hours or days.
- The source naturally produces files or snapshots.
- Operational simplicity is valuable.
- Streaming would provide little business value.

## 8.2 Streaming

Appropriate when:

- Freshness is seconds or very low minutes.
- Events arrive continuously.
- Consumers benefit materially from rapid updates.

## 8.3 CDC

Appropriate when:

- The source is a transactional database.
- Incremental changes matter.
- Full snapshots are too expensive or too slow.
- Deletes and updates must be represented.

## 8.4 API/file ingestion

Consider:

- Pagination
- Rate limits
- Retries
- Partial delivery
- Idempotency
- Checkpointing
- File arrival semantics
- Schema changes

Ask:

```text
Is the source:
- batch?
- streaming?
- transactional?
- append-only?
- mutable?
- replayable?
```

Do not turn this section into a Kafka or CDC tutorial. The interview goal is choosing the **right ingestion behavior**.

## 8.5 Ingestion Decision Tree

```text
How fresh must data be?
        |
        +-- Hours/days
        |      ↓
        |    Batch
        |
        +-- Minutes
        |      ↓
        |   Micro-batch / frequent ingestion
        |
        +-- Seconds/sub-seconds
               ↓
             Streaming
```

Then validate against:

```text
Source capability
+ Volume
+ Correctness
+ Operational complexity
+ Cost
```

Freshness alone does not determine the architecture.

---

# 9. Storage Layers

## Bronze

Purpose:

- Raw or near-raw source representation
- Replay
- Auditability
- Source fidelity

Typical questions:

- Can I reconstruct the source record?
- Can I replay after a downstream bug?
- Can I prove what arrived?

## Silver

Purpose:

- Clean
- Validate
- Deduplicate
- Standardize
- Conform

Typical questions:

- Is the data usable by downstream systems?
- Are keys consistent?
- Are duplicates controlled?
- Are invalid records quarantined?

## Gold

Purpose:

- Business-ready
- Aggregated
- Consumer-oriented
- Analytics-ready

Typical questions:

- What business entity or metric is represented?
- Who owns the semantic definition?
- Is the serving workload supported?

### Important

Bronze/Silver/Gold are **logical responsibilities**, not a requirement to deploy three separate databases.

---

# 10. Data Model and Grain

A strong system-design answer makes the data grain explicit.

Ask:

- What are the entities?
- What are the events?
- What are the relationships?
- What are the keys?
- What is the grain?
- What is immutable?
- What is mutable?
- What needs history?
- What needs aggregation?

Examples:

```text
One row per order
One row per order item
One row per customer
One event per click
One record per device reading
```

### Why grain matters

Suppose a dashboard needs revenue per order, but the underlying table is actually one row per order item. A naïve aggregation can double-count or misinterpret the metric.

A useful interview sentence is:

> "The grain of this table is one row per order item; therefore revenue calculations must account for item-level multiplicity."

Wrong grain creates downstream problems in:

- Aggregations
- Joins
- Deduplication
- Historical modeling
- Feature generation
- Serving
- Cost

---

# 11. Storage Format

Reason about:

- Row-oriented vs column-oriented storage
- Parquet/columnar formats
- JSON/raw formats
- Table formats
- Compression
- Partitioning
- Clustering/layout

Do not ask:

> "Which format is popular?"

Ask:

> "What storage characteristics fit the access pattern, update model, scale, and consumer workload?"

### Example

Analytical workloads that scan selected columns often benefit from columnar storage because they can avoid reading unrelated columns.

Raw source payloads may still need preservation in a source-faithful representation for replay or audit.

---

# 12. Table Format vs Catalog

These are related but different concepts.

## Table format

May provide:

- Transactions
- Schema management
- Versioning
- Metadata
- Time travel
- Reliable table semantics

## Catalog

May provide:

- Discovery
- Governance
- Ownership
- Access control
- Metadata

A useful mental model:

```text
Table format
= How table state is represented and managed

Catalog
= How data assets are discovered, governed, owned, and accessed
```

Do not assume one automatically replaces the other.

---

# 13. Storage Layout

Reason about:

- Partitioning
- Clustering
- Sort order
- File sizing
- Data locality
- Retention

> **Storage layout should follow access patterns and workload, not personal preference.**

Example:

```sql
SELECT *
FROM events
WHERE event_date BETWEEN '2026-10-01' AND '2026-10-07';
```

A date-oriented layout may be useful because the access pattern repeatedly filters on `event_date`.

But partitioning has costs.

### Over-partitioning risks

- Too many small files
- Metadata overhead
- Slow planning
- Operational complexity
- Uneven partition sizes

A strong candidate can say:

> "I would choose a layout based on dominant access patterns and validate it against data distribution; I would avoid partitioning on high-cardinality columns merely because they appear in queries."

---

# 14. Processing

Processing can be:

- Batch
- Streaming
- Incremental
- Stateful
- Stateless
- Distributed

Choose based on:

```text
Volume
Latency
Complexity
State
Correctness
Cost
Operational requirements
```

### Batch

Good when the system can tolerate bounded delay and benefits from simpler processing.

### Streaming

Good when continuously arriving data must produce results quickly.

### Incremental

Good when recomputing all historical data is unnecessary or too expensive.

### Stateful

Required when results depend on prior events or retained state.

### Stateless

Useful when each input can be processed independently.

### Distributed

Useful when the workload exceeds the practical capacity of a single process or machine.

---

# 15. Processing Engine Selection

Do not start with a vendor.

Use:

```text
Workload
   ↓
Latency
   ↓
Scale
   ↓
State
   ↓
Operational model
   ↓
Engine choice
```

Possible categories include:

- SQL engines
- Distributed processing engines
- Stream processing engines
- Warehouse engines
- Serverless query engines

The question is not:

> "Is Spark better than X?"

The question is:

> "What processing characteristics does this workload require, and which engine satisfies them with acceptable complexity and cost?"

---

# 16. Processing vs Orchestration

These are different responsibilities.

### Processing

Answers:

> "How is the data transformed?"

Examples:

- Join
- Aggregate
- Filter
- Enrich
- Deduplicate
- Compute a feature

### Orchestration

Answers:

> "When, in what order, under what retry policy, and with what operational state does the workflow execute?"

Orchestration provides:

- Dependencies
- Scheduling
- Retries
- Backfills
- Monitoring
- SLAs
- Workflow state

A processing engine does not automatically become an orchestration strategy.

---

# 17. Serving

Serving means making processed data available in a form appropriate for its consumers.

```text
Processing output
       ↓
Serving interface
       ↓
Consumer
```

Common serving patterns:

- Analytics serving
- BI/query interfaces
- Application APIs
- Feature serving
- Search
- Vector retrieval
- Operational consumers

> **The consumer determines the serving interface.**

### Examples

| Consumer | Serving interface |
|---|---|
| BI | Warehouse/query interface |
| Application API | Low-latency database/API |
| ML | Feature store or feature-serving interface |
| RAG | Vector search/retrieval interface |
| Compliance | Auditable query/reporting interface |

Do not build a serving layer without identifying the consumer's latency, consistency, and query needs.

---

# 18. Cross-Cutting Concerns

A production Data Engineering design is incomplete without these:

1. Data quality
2. Data contracts
3. Idempotency
4. Backfills
5. Late data
6. Schema evolution
7. Orchestration
8. SLAs
9. Observability
10. Alerting
11. Security
12. Privacy
13. Governance
14. Cost

These are not a final checklist to mention only if time remains. They are architectural concerns.

---

# 19. Data Quality

Ask:

> "What does good data mean for this system?"

Dimensions include:

- Completeness
- Accuracy
- Validity
- Uniqueness
- Timeliness
- Referential integrity
- Distribution anomalies

Examples:

```text
Completeness:
Expected 10M events; only 7M arrived.

Uniqueness:
Same transaction_id appears multiple times.

Validity:
Country code is outside the supported domain.

Timeliness:
Latest partition is 90 minutes old when SLA is 10 minutes.

Distribution:
Order amount suddenly becomes 100× higher than normal.
```

### Pipeline health vs data health

A pipeline can be technically green while producing bad data.

```text
Pipeline health:
Job completed successfully.

Data health:
Rows are complete, valid, unique, timely, and semantically correct.
```

Both must be monitored.

---

# 20. Data Contracts

A data contract establishes expectations between producers and consumers.

Cover:

- Producer expectations
- Consumer expectations
- Schema
- Semantics
- Ownership
- Compatibility
- Change management

A useful contract asks:

```text
Who owns this dataset?
What does each field mean?
What is the grain?
What changes are allowed?
What constitutes a breaking change?
Who is notified?
How is compatibility tested?
```

Contracts reduce accidental breaking changes by making producer/consumer expectations explicit.

---

# 21. Idempotency

The core question is:

> **If the same input is processed twice, can the result remain correct?**

Useful mechanisms include:

```text
event_id
transaction_id
deduplication key
upsert
merge
```

Idempotency matters for:

- Retries
- Reprocessing
- Exactly-once business outcomes
- Backfills
- Recovery

Example:

```text
Input:
transaction_id = T123

First attempt:
write T123

Retry:
write T123 again

If the operation is idempotent:
final business state remains correct.
```

Do not confuse idempotency with exactly-once processing. A system can process a message multiple times while still producing one correct business effect.

---

# 22. Backfills

Backfills happen because:

- Historical data needs correction.
- A pipeline bug was fixed.
- A new derived field is introduced.
- A source corrects historical records.
- A schema or transformation changes.

Ask:

1. Can the system replay?
2. Is raw data retained?
3. Can historical and live processing coexist safely?
4. Will backfill compete with production workloads?
5. Is processing idempotent?
6. How is correctness verified?
7. How is the serving layer updated?

A mature design treats backfill as an expected operating mode, not an emergency improvisation.

---

# 23. Late Data

Distinguish:

- **Event time** — when the event actually occurred.
- **Processing time** — when the platform processed it.
- **Arrival time** — when the platform received it.

Events may arrive out of order.

Conceptually:

```text
Event time:       10:01
Event arrives:    10:08
```

Questions:

- When is a window considered complete?
- How are late events incorporated?
- Are corrections emitted?
- Is reprocessing required?
- What is the acceptable lateness?
- How is state bounded?

Watermarks are one conceptual mechanism for deciding how much out-of-order data the system expects, but this module intentionally does not become a stream-processing tutorial.

---

# 24. Schema Evolution

Changes include:

- Adding fields
- Removing fields
- Renaming fields
- Type changes
- Semantic changes
- Versioning

Think:

```text
Schema change
    ↓
Producer impact
    ↓
Pipeline impact
    ↓
Consumer impact
```

Important concepts:

- Backward compatibility
- Forward compatibility
- Versioning
- Deprecation
- Ownership
- Migration windows

A field rename may be more disruptive than adding a nullable field because downstream consumers may depend on the old name.

---

# 25. Orchestration and SLAs

The design should explain:

- Schedule
- Dependencies
- Retry policy
- Timeout
- Failure handling
- Freshness SLA
- Recovery expectations
- Backfill execution

Example:

```text
Raw ingestion
   ↓
Quality gate
   ↓
Silver transformation
   ↓
Gold aggregation
   ↓
Serving refresh
```

If Silver fails:

```text
Do not publish an invalid Gold result.
Retry or repair Silver.
Verify correctness.
Then resume downstream work.
```

An SLA should be measurable.

```text
Bad:
"The dashboard should be fresh."

Better:
"95% of daily dashboard data is available within 10 minutes
of the source cutoff, with an escalation when freshness exceeds
15 minutes."
```

---

# 26. Observability

Observe three layers.

## Infrastructure

- CPU
- Memory
- Network
- Disk

## Pipeline

- Throughput
- Lag
- Runtime
- Failure rate
- Retry count

## Data

- Row counts
- Null rates
- Duplicates
- Freshness
- Distribution

A strong design distinguishes:

```text
System is running
```

from:

```text
System is producing trustworthy data
```

---

# 27. Alerting

Ask:

> "What should page an engineer?"

Examples:

- Pipeline failed
- Freshness SLA violated
- Consumer lag grows continuously
- Unexpected volume drop
- Schema-breaking change
- Cost anomaly

Avoid alerting on every metric.

A useful alert should generally have:

```text
Signal
→
Threshold / condition
→
Business or operational impact
→
Owner
→
Action
```

A dashboard metric that requires no action should not necessarily page someone at 3 a.m.

---

# 28. Security

Architecture-level questions:

- Who can access the data?
- What data is sensitive?
- How is data encrypted?
- How are users/services authenticated?
- How is authorization enforced?
- Are privileges least-privilege?
- Where are secrets stored?
- What are the network boundaries?
- What is audited?

Keep security connected to the data platform rather than turning this module into a security course.

---

# 29. Privacy

Consider:

- PII
- Sensitive data
- Data minimization
- Retention
- Deletion
- Masking
- Tokenization
- Access controls

A privacy requirement can change architecture.

For example:

```text
Requirement:
Delete a user's personal data.

Architecture implication:
Need identity mapping + lineage + deletion propagation
+ verification + auditability.
```

Privacy is therefore a design constraint, not paperwork added after deployment.

---

# 30. Governance

Governance includes:

- Data ownership
- Catalog
- Lineage
- Classification
- Access policies
- Auditability
- Retention
- Compliance

A useful mental model:

```text
Discover
→
Classify
→
Own
→
Control access
→
Trace lineage
→
Audit
→
Retain/delete according to policy
```

Governance should be designed into the platform.

---

# 31. Cost

Include:

- Storage
- Compute
- Query/scan
- Network
- Serving
- Operational complexity

A technically correct design can still be a poor production design if it is economically unreasonable.

A senior candidate should be able to say:

> "This design satisfies the freshness requirement, but it introduces continuous compute and higher operational complexity. If the business can tolerate 15-minute freshness, micro-batch would materially reduce cost."

---

# 32. Failure Handling

A complete design does not stop at the happy path.

Use:

```text
Component
   ↓
Failure mode
   ↓
Impact
   ↓
Detection
   ↓
Recovery
   ↓
Prevention
```

Apply it to:

- Source unavailable
- Ingestion failure
- Duplicate data
- Late data
- Processing failure
- Storage failure
- Serving failure
- Schema change
- Orchestrator failure

## Reusable failure matrix

| Component | Failure | Impact | Detection | Recovery | Prevention |
|---|---|---|---|---|---|
| Source | Source unavailable | Freshness delay | Availability check / freshness metric | Retry later; replay missed range | Source SLA, buffering |
| Ingestion | Consumer/job failure | Missing or delayed data | Job health + lag | Restart from checkpoint | Checkpointing, idempotency |
| Data | Duplicates | Incorrect aggregates | Uniqueness checks | Deduplicate/recompute | Stable event keys |
| Streaming | Late events | Incorrect windows | Late-data metrics | Reprocess/correct | Event-time policy |
| Processing | Transformation failure | Downstream blocked | Job failure | Retry/repair | Tests, validation |
| Storage | Write failure | Missing output | Write errors | Retry/restore | Durable storage, transactional writes |
| Serving | Query/API failure | Consumer outage | Latency/error rate | Failover/retry | Redundancy, caching where appropriate |
| Schema | Breaking change | Pipeline/consumer break | Contract validation | Roll back/adapt/migrate | Compatibility policy |
| Orchestrator | Scheduler outage | Workflow delay | Control-plane monitoring | Resume/repair | HA and recovery procedures |

---

# 33. Delivery Semantics: At-Most, At-Least, Exactly Once

These terms must not be used casually.

### At-most-once

An item is delivered zero or one time.

Potential consequence:

```text
No duplicate, but data may be lost.
```

### At-least-once

An item is delivered one or more times.

Potential consequence:

```text
No intentional loss, but duplicates are possible.
```

### Exactly-once processing

The processing system attempts to ensure one processing outcome under its defined execution semantics.

### Exactly-once business effect

The business state changes as though each logical event affected the result once.

These are not automatically equivalent.

For example:

```text
At-least-once delivery
+
Stable event_id
+
Idempotent upsert
=
Potentially exactly-once business effect
```

The exact guarantee depends on the boundaries of the system.

> **Interview rule:** Always ask, "Exactly once at which layer?"

---

# 34. Recovery and Replay

A production architecture should make recovery explainable.

Useful mechanisms:

- Checkpoints
- Reprocessing
- Replayable raw data
- Dead-letter/quarantine paths
- Backfills
- Recovery windows

A powerful architectural property is **replayability**.

```text
Raw immutable/recoverable data
        ↓
Re-run transformation
        ↓
Rebuild corrected output
```

Without replayability, a transient or transformation failure may become a permanent data-loss problem.

---

# 35. Stage 9 — Design for Evolution

Every complete design should answer:

- What happens at 10× scale?
- What if a new source arrives?
- What if a new consumer arrives?
- What if latency becomes stricter?
- What if retention increases?
- What if cost must fall?
- What if another region is added?
- What if the schema changes?

Evolution is not an optional final paragraph. It tests whether the architecture has sensible boundaries.

---

# 36. 10× Scale

Example:

```text
Current: 10 TB/day
Future:  100 TB/day
```

Ask:

- What becomes the bottleneck?
- Storage?
- Network?
- Compute?
- Metadata?
- Partitioning?
- Orchestration?
- Serving?
- Cost?

Then revisit the estimates.

> Scaling is not simply "add more machines."

At 10× scale, a metadata bottleneck, small-file problem, partitioning strategy, network transfer, query pattern, or cost model may dominate before raw compute does.

---

# 37. New Sources

Suppose the platform evolves from:

```text
Source A
```

to:

```text
Source A
Source B
Source C
Source D
```

Ask:

- Is ingestion standardized?
- Are source-specific adapters isolated?
- Are contracts explicit?
- Is schema management centralized?
- Is governance consistent?
- Who owns operational failures?

A reusable platform boundary might look like:

```text
Source-specific adapters
        ↓
Standard ingestion contract
        ↓
Common raw representation
        ↓
Shared governance / observability
```

---

# 38. New Consumers

Suppose the original consumer was analytics:

```text
Analytics
```

and becomes:

```text
Analytics
ML
AI
Operational API
Compliance
External partners
```

The serving architecture may need to evolve.

Do not assume one storage interface is ideal for every consumer.

Ask:

- Which consumers require low latency?
- Which require interactive analytics?
- Which need point-in-time features?
- Which need vector retrieval?
- Which need auditability?
- Which need external sharing?
- Which data contract protects each consumer?

---

# 39. Interview Time Allocation

A 45–60 minute interview needs deliberate pacing.

One flexible example:

```text
0–5 min
Requirements

5–10 min
Estimates

10–20 min
High-level architecture

20–35 min
Deep dive

35–45 min
Reliability / quality / security / cost

45–50 min
Trade-offs / evolution / wrap-up
```

This is **not a rigid script**.

If the interviewer spends 10 minutes probing requirements, compress later sections intelligently.

### Time-management rule

Do not spend:

```text
20 minutes on ingestion
0 minutes on failures
0 minutes on cost
0 minutes on evolution
```

A good candidate protects time for the concerns that distinguish production thinking.

---

# 40. Choosing Where to Go Deep

> **Do not deep-dive everything.**

Identify the one or two genuinely difficult parts.

| Problem | Likely deep-dive |
|---|---|
| Clickstream | Partitioning, ordering, late data, streaming |
| CDC | Ordering, deletes, schema evolution, replay |
| ML feature platform | Online/offline consistency, freshness, serving latency |
| GDPR | Deletion propagation, derived data, backups, auditability |
| Analytics | Data model, query patterns, cost, freshness |
| RAG | Access control, re-indexing, deletes, retrieval latency |

A useful interview move:

> "The broad architecture is straightforward. The highest-risk area is late-arriving clickstream data, so I'd like to spend the next few minutes there."

That demonstrates judgment.

---

# 41. Framework Adaptation — Analytics

```text
Sources
   ↓
Batch ingestion
   ↓
Lakehouse
   ↓
Transformation
   ↓
Warehouse / analytical serving
   ↓
BI
```

Priorities:

- Freshness
- Data modeling
- Cost
- Quality
- Governance

Likely deep dive:

```text
Grain
→
Dimensions/facts or equivalent semantic model
→
Query patterns
→
Incremental refresh
→
Cost
```

---

# 42. Framework Adaptation — Streaming

```text
Producers
   ↓
Streaming ingestion
   ↓
Stream processing
   ↓
State / storage
   ↓
Serving
   ↓
Consumers
```

Priorities:

- Throughput
- Latency
- Ordering
- Duplicates
- Late data
- Replay
- Backpressure

Likely deep dive:

```text
Partitioning
→
Ordering
→
State
→
Late data
→
Recovery
```

---

# 43. Framework Adaptation — ML Data / Feature Platform

```text
Sources
   ↓
Feature computation
   ↓
Offline store
   ↓
Online serving
   ↓
ML consumers
```

Priorities:

- Feature freshness
- Training/serving consistency
- Point-in-time correctness
- Latency
- Backfills
- Monitoring

Likely deep dive:

```text
Offline correctness
↔
Online correctness
↔
Feature freshness
↔
Serving latency
```

---

# 44. Framework Adaptation — AI / RAG Data Platform

```text
Documents
   ↓
Ingestion
   ↓
Parsing
   ↓
Chunking
   ↓
Embedding
   ↓
Vector storage
   ↓
Retrieval
   ↓
AI application
```

Priorities:

- Document freshness
- Metadata
- Access control
- Re-indexing
- Deletes
- Retrieval latency
- Cost
- Versioning

This is not a RAG tutorial. The goal is applying the Data Engineering framework.

A likely deep dive:

```text
Access control
→
Document versioning
→
Incremental re-indexing
→
Deletion propagation
→
Retrieval latency/cost
```

---

# 45. Framework Adaptation — Compliance / GDPR

```text
Sources
   ↓
Data discovery
   ↓
Identity mapping
   ↓
Deletion propagation
   ↓
Verification
   ↓
Audit
```

Priorities:

- Data lineage
- PII
- Retention
- Deletion
- Derived data
- Backups
- Auditability

The central design question becomes:

> "Can I prove that a subject's data was deleted everywhere required by policy?"

---

# 46. One Framework, Many Systems

| Framework stage | Analytics | Streaming | ML | AI/RAG | Compliance |
|---|---|---|---|---|---|
| Requirements | Freshness + BI needs | Latency + event guarantees | Feature correctness | Retrieval requirements | Deletion obligations |
| Estimates | Scan volume | Events/sec + state | Feature volume/QPS | Documents + retrieval QPS | Subject/request volume |
| Flow | Batch lakehouse | Event stream | Feature pipeline | Document pipeline | Discovery → deletion |
| Storage | Columnar analytical tables | Event/state stores | Offline + online | Object + vector stores | Governed source/derived data |
| Processing | Batch/incremental | Stateful streaming | Feature computation | Parsing/embedding/indexing | Propagation/verification |
| Serving | BI/query | Low-latency consumers | Feature serving | Retrieval | Audit/reporting |
| Cross-cutting | Quality/cost | Ordering/late data | PIT correctness | ACL/versioning | Governance/lineage |
| Failure | Job/data failures | Lag/state/replay | Feature skew | Index drift | Incomplete deletion |
| Evolution | More data/users | 10× events | More features/models | More sources/tenants | New regulations/regions |

> **The framework remains stable; the depth and decisions change.**

---

# 47. Data Engineering System Design vs Generic Software Design

Data Engineering system design has first-class concerns that are often less central in generic backend discussions:

- Data correctness
- Data lineage
- Backfills
- Reprocessing
- Late data
- Schema evolution
- Data quality
- Storage layout
- Batch/streaming behavior
- Retention
- Cost
- Governance

A backend service can be healthy while returning the wrong record only occasionally; a data platform can be operationally green while silently corrupting millions of analytical rows.

Therefore:

```text
Availability
+
Correctness
+
Recoverability
+
Traceability
+
Cost
```

must all be considered.

---

# 48. Decision Record Format

For any major architectural choice, use:

```text
Decision:
Why:
Alternatives:
Trade-off:
Assumption:
Failure mode:
Cost implication:
Future evolution:
```

Example:

```text
Decision:
Use micro-batch rather than continuous streaming.

Why:
The business requires five-minute freshness, not sub-minute freshness.

Alternatives:
Continuous streaming; hourly batch.

Trade-off:
Less operational complexity than continuous streaming,
but more latency than true streaming.

Assumption:
Five-minute freshness remains sufficient.

Failure mode:
Processing delay can violate freshness SLA.

Cost implication:
Lower continuous compute and operational overhead.

Future evolution:
Can move toward continuous processing if the SLA tightens.
```

Use the record format for:

- Batch vs streaming
- Storage format
- Processing engine
- Serving layer
- Partitioning
- Orchestration

---

# 49. Technology Selection

Use:

```text
Requirement
   ↓
Scale
   ↓
Latency
   ↓
Correctness
   ↓
Operational constraints
   ↓
Cost
   ↓
Existing platform
   ↓
Technology choice
```

Naming technologies too early is a common interview failure.

Weak:

> "I'll use Kafka because it is scalable."

Strong:

> "The requirement is continuous ingestion at high event volume with replay and low-latency downstream processing. That makes a durable streaming ingestion pattern appropriate; the exact technology depends on the existing platform and operational constraints."

The second answer demonstrates reasoning rather than brand recognition.

---

# 50. Reusable High-Level Architecture Template

```text
1. Sources
2. Ingestion
3. Raw storage
4. Transformation
5. Curated storage
6. Serving
7. Consumers
8. Observability
9. Governance
10. Failure / recovery
11. Evolution
```

Use it as a starting point, then remove components that are unnecessary.

---

# 51. Whiteboard Template

```text
                 ┌───────────────┐
                 │    Sources    │
                 └───────┬───────┘
                         ↓
                 ┌───────────────┐
                 │   Ingestion   │
                 └───────┬───────┘
                         ↓
                 ┌───────────────┐
                 │ Bronze / Raw  │
                 └───────┬───────┘
                         ↓
                 ┌───────────────┐
                 │  Processing   │
                 └───────┬───────┘
                         ↓
                 ┌───────────────┐
                 │ Silver / Gold │
                 └───────┬───────┘
                         ↓
                 ┌───────────────┐
                 │   Serving     │
                 └───────┬───────┘
                         ↓
                 ┌───────────────┐
                 │   Consumers   │
                 └───────────────┘

 Side concerns:
 Quality | Security | Governance
 Observability | Cost | Failure Recovery
```

Draw only what helps explain the design.

---

# 52. Five Complete Framework Walkthroughs

These are framework demonstrations, not replacements for the Phase C case files.

## 52.1 Walkthrough 1 — Batch Analytics Platform

### Prompt

> Design a platform that ingests application data and provides daily business analytics.

### 1. Requirements

Assume:

- Daily analytics is sufficient.
- Data must be available by 7:00 AM.
- Historical data is retained for several years.
- BI users need consistent business definitions.

### 2. Estimates

Suppose:

```text
500 GB/day
3-year retention
Daily processing
Hundreds of BI users
```

### 3. High-level flow

```text
Application DBs / SaaS
        ↓
Batch ingestion
        ↓
Bronze
        ↓
Transformations
        ↓
Silver
        ↓
Business aggregates
        ↓
Gold
        ↓
Analytical serving
        ↓
BI
```

### 4. Data model / storage

Define grain explicitly:

```text
orders: one row per order
order_items: one row per order item
customer_daily_metrics: one row per customer per day
```

Use analytical/columnar storage characteristics where appropriate.

### 5. Processing

Use incremental batch transformations where full recomputation is unnecessary.

### 6. Serving

Provide an analytical query interface suitable for BI.

### 7. Cross-cutting

Address:

- Data quality
- Contracts
- Idempotency
- Backfills
- Schema evolution
- Freshness SLA
- Governance
- Cost

### 8. Failure handling

If a source is delayed:

```text
Detect freshness violation
→ Retry
→ Reconcile
→ Delay publication if correctness would be compromised
→ Alert owner
```

### 9. Evolution

At 10× scale:

- Revisit partitioning/layout.
- Revisit compute.
- Reduce unnecessary scans.
- Reassess retention cost.
- Separate workloads if contention grows.

### 10. Trade-off

Daily batch is operationally simpler and cheaper than continuous streaming because the requirement does not justify lower latency.

### 11. Interview communication

> "Because the business needs daily analytics rather than sub-minute freshness, I would start with batch ingestion and incremental transformations. I would preserve raw data for replay, define clear table grain, publish only quality-validated Gold outputs, and reserve streaming complexity for a requirement that actually needs it."

---

## 52.2 Walkthrough 2 — Real-Time Clickstream Platform

### Prompt

> Design a clickstream platform that supports near-real-time product analytics.

### 1. Requirements

Assume:

- Seconds-to-minutes freshness.
- High event volume.
- Events can arrive out of order.
- Analysts need recent metrics.
- Raw events must be replayable.

### 2. Estimates

Estimate:

```text
Events/sec
Peak events/sec
Event size
Daily storage
Retention
Serving QPS
```

### 3. Flow

```text
Producers
   ↓
Streaming ingestion
   ↓
Raw event storage
   ↓
Stream processing
   ↓
Curated/stateful outputs
   ↓
Serving
   ↓
Analytics consumers
```

### 4. Data model

```text
event_id
event_time
user_id
session_id
event_type
attributes
```

### 5. Processing

Focus on:

- Partitioning
- Ordering
- Stateful operations
- Late events
- Deduplication

### 6. Serving

Choose a low-latency analytical or operational interface according to consumer needs.

### 7. Cross-cutting

Especially:

- Event contracts
- Idempotency
- Late data
- Replay
- Lag
- Freshness
- Cost

### 8. Failure

If processing stops:

```text
Detect lag
→ Stop bad publication if necessary
→ Recover from checkpoint
→ Replay safely
→ Reconcile
→ Resume
```

### 9. Evolution

At 10×:

- Partition capacity
- State size
- Network throughput
- Serving load
- Storage cost
- Backpressure

### 10. Trade-off

Streaming provides freshness but increases operational complexity.

### 11. Interview communication

> "The difficult part is not the event ingestion box. It is preserving correctness while handling duplicates, ordering, late events, replay, and state growth."

---

## 52.3 Walkthrough 3 — CDC to Lakehouse

### Prompt

> Replicate operational database changes into an analytical lakehouse.

### 1. Requirements

- Incremental updates
- Inserts, updates, deletes
- Historical analytical access
- Minimal impact on source database
- Recoverability

### 2. Estimates

Estimate:

- Change events/sec
- Peak changes/sec
- Average event size
- Daily change volume
- Retention
- Downstream processing volume

### 3. Flow

```text
Operational DB
      ↓
CDC
      ↓
Raw change records
      ↓
Dedup/order/validation
      ↓
Curated tables
      ↓
Analytical serving
```

### 4. Data model

Preserve:

```text
primary key
operation type
change timestamp
source position / sequence
before/after or equivalent payload
```

### 5. Processing

Need to reason about:

- Ordering
- Deletes
- Upserts
- Idempotency
- Replay

### 6. Serving

Analytical tables optimized for consumer access patterns.

### 7. Cross-cutting

Contracts, schema evolution, lineage, auditability, freshness, reconciliation.

### 8. Failure

If a change range is missing:

```text
Identify source position gap
→ Recover/replay
→ Reconcile counts/checksums
→ Rebuild affected outputs
```

### 9. Evolution

More tables and higher change rates may require standardized connectors, partitioning, source isolation, and stronger operational controls.

### 10. Trade-off

CDC is more operationally complex than periodic snapshots but can dramatically reduce source-to-analytics latency and transferred data.

### 11. Interview communication

> "I would make source position and idempotency explicit because replay and ordering are central to CDC correctness."

---

## 52.4 Walkthrough 4 — ML Feature Platform

### Prompt

> Design a platform that computes features for training and online inference.

### 1. Requirements

- Historical training data
- Low-latency online features
- Freshness requirements
- Point-in-time correctness
- Reproducible feature definitions

### 2. Estimates

Estimate:

- Entities
- Feature count
- Update rate
- Online QPS
- Storage
- Feature freshness

### 3. Flow

```text
Sources
   ↓
Feature computation
   ├──────────────→ Offline store
   ↓
Online feature update
   ↓
Online serving
   ↓
ML inference
```

### 4. Data model

Explicitly define:

```text
entity_id
feature_name
feature_value
event_time / effective_time
```

### 5. Processing

Separate:

- Historical computation
- Incremental updates
- Online updates

### 6. Serving

Online consumers need low-latency access; training needs point-in-time-correct historical data.

### 7. Cross-cutting

Focus on:

- Training/serving consistency
- Point-in-time correctness
- Backfills
- Freshness
- Monitoring
- Data quality

### 8. Failure

If online feature updates stop:

```text
Detect freshness violation
→ Determine stale-feature policy
→ Recover/replay
→ Validate
→ Resume
```

### 9. Evolution

More models and features require stronger ownership, contracts, lineage, cost controls, and platform reuse.

### 10. Trade-off

Keeping offline and online representations consistent increases engineering complexity but protects model correctness.

### 11. Interview communication

> "The key architectural risk is not merely serving latency; it is whether training and online inference observe semantically consistent features."

---

## 52.5 Walkthrough 5 — RAG / Vector Data Platform

### Prompt

> Design a platform that ingests enterprise documents and supports permission-aware retrieval for an AI application.

### 1. Requirements

- Document freshness
- Access control
- Incremental updates
- Deletes
- Retrieval latency
- Versioning

### 2. Estimates

Estimate:

- Documents/day
- Average document size
- Chunk count
- Embedding volume
- Retrieval QPS
- Re-indexing workload

### 3. Flow

```text
Documents
   ↓
Ingestion
   ↓
Parsing
   ↓
Chunking
   ↓
Embedding
   ↓
Vector storage
   ↓
Retrieval
   ↓
AI application
```

### 4. Data model

Keep metadata such as:

```text
document_id
document_version
chunk_id
source
owner
permissions
effective_time
embedding_version
```

### 5. Processing

Incremental processing should distinguish:

- New documents
- Changed documents
- Deleted documents

### 6. Serving

The retrieval interface must support the consumer's latency and authorization requirements.

### 7. Cross-cutting

Especially:

- Access control
- Metadata quality
- Versioning
- Deletes
- Cost
- Observability

### 8. Failure

If an indexing job fails halfway:

```text
Identify incomplete batch
→ Avoid publishing incomplete state
→ Retry/reprocess
→ Validate index coverage
→ Resume
```

### 9. Evolution

10× growth may require:

- Index sharding/partitioning
- Incremental re-indexing
- Tenant isolation
- Cost controls
- Better metadata governance

### 10. Trade-off

A richer retrieval index may improve recall or filtering while increasing storage, indexing, and serving cost.

### 11. Interview communication

> "The highest-risk area is permission-aware retrieval and deletion propagation, because serving stale or unauthorized content is a correctness and security failure."

---

# 53. Python Examples

Python is used only to reinforce framework thinking.

## 53.1 Requirements Object

```python
requirements = {
    "freshness_minutes": 5,
    "daily_events": 100_000_000,
    "retention_days": 365,
    "availability": 0.999,
}
```

This converts ambiguous discussion into explicit architecture inputs.

---

## 53.2 Teaching Decision Helper

```python
def choose_processing_mode(freshness_minutes):
    if freshness_minutes < 1:
        return "streaming"
    elif freshness_minutes < 60:
        return "micro-batch"
    return "batch"
```

This is intentionally simplified.

Real architecture decisions also require:

- Source capabilities
- Volume
- State
- Correctness
- Operational constraints
- Cost
- Existing platform

Never use one threshold as a production architecture rule.

---

## 53.3 Requirement-to-Decision Mapping

```python
requirements = {
    "freshness_minutes": 5,
    "daily_volume_gb": 500,
    "consumers": ["bi", "ml"],
}

decisions = {
    "processing": "frequent incremental processing",
    "storage": "columnar lakehouse",
    "serving": ["analytics", "feature-serving"],
}
```

The important learning is not the dictionary. It is the reasoning chain:

```text
Requirements
→
Constraints
→
Design decisions
```

---

## 53.4 Failure Matrix

```python
failure_matrix = [
    {
        "component": "ingestion",
        "failure": "source unavailable",
        "impact": "data freshness delay",
        "recovery": "retry and replay",
    }
]
```

This structure makes failure handling explicit during a design review.

---

## 53.5 Framework Completeness Checker

```python
required_stages = [
    "requirements",
    "estimates",
    "flow",
    "storage",
    "processing",
    "serving",
    "cross_cutting",
    "failure",
    "evolution",
]

def missing_stages(design):
    return [stage for stage in required_stages if not design.get(stage)]

design = {
    "requirements": True,
    "estimates": True,
    "flow": True,
    "storage": True,
    "processing": True,
    "serving": True,
    "cross_cutting": True,
    "failure": False,
    "evolution": False,
}

print(missing_stages(design))
```

Expected output:

```text
['failure', 'evolution']
```

The lesson is simple: a design can look complete while still missing critical production stages.

---

# 54. Hands-On Exercises

## Exercise 1 — Basic Batch Analytics

**Prompt:** Design a platform for daily sales analytics.

**Time limit:** 20 minutes.

### Requirements checklist

- [ ] Consumers identified
- [ ] Freshness clarified
- [ ] Volume estimated
- [ ] Retention clarified
- [ ] Correctness expectations stated

### Framework checklist

- [ ] Sources
- [ ] Ingestion
- [ ] Bronze/Silver/Gold
- [ ] Data grain
- [ ] Processing
- [ ] Serving
- [ ] Quality
- [ ] Failure recovery
- [ ] Evolution

### Expected output

One architecture diagram, five assumptions, one decision record, one failure matrix.

### Self-review

Can you explain why batch is sufficient rather than merely saying it is simpler?

---

## Exercise 2 — Real-Time Event Platform

**Prompt:** Design a platform for near-real-time application events.

**Time limit:** 25 minutes.

Focus on:

- Throughput
- Latency
- Partitioning
- Ordering
- Duplicates
- Late data
- Replay
- Serving

### Self-review

Can you explain what happens when events arrive 10 minutes late?

---

## Exercise 3 — CDC Platform

**Prompt:** Replicate a transactional database into an analytical platform.

**Time limit:** 25 minutes.

Focus on:

- Inserts
- Updates
- Deletes
- Ordering
- Source position
- Idempotency
- Schema evolution
- Replay
- Reconciliation

### Self-review

Can you recover from a missing change range?

---

## Exercise 4 — ML Feature Platform

**Prompt:** Build a feature platform for training and online inference.

**Time limit:** 30 minutes.

Focus on:

- Feature freshness
- Point-in-time correctness
- Offline/online consistency
- Serving latency
- Backfills
- Monitoring

### Self-review

Can you explain how training avoids future-data leakage?

---

## Exercise 5 — Compliance Platform

**Prompt:** Design a platform that supports verified deletion of personal data.

**Time limit:** 30 minutes.

Focus on:

- Identity mapping
- Discovery
- Lineage
- Derived data
- Deletion
- Backups
- Verification
- Auditability

### Self-review

Can you prove deletion rather than merely say "we deleted it"?

---

# 55. One-Page Framework

```text
1. Requirements
   What must the system do?

2. Estimates
   How big / fast is it?

3. Data Flow
   Where does data come from and where does it go?

4. Data Model & Storage
   What is the grain, format, layout, and retention?

5. Processing
   Batch, streaming, incremental, stateful?

6. Serving
   Who consumes the data and how?

7. Cross-Cutting
   Quality, contracts, idempotency, backfills,
   late data, schema evolution, observability,
   security, privacy, governance, cost.

8. Failure Handling
   What breaks? How do we detect and recover?

9. Evolution
   What happens at 10× scale or with new sources/consumers?
```

---

# 56. Interview Communication Script

Use transitions to make the reasoning easy to follow.

> "Let me first clarify the requirements."

> "Given those requirements, I'll estimate the scale."

> "Now I'll sketch the high-level data flow."

> "I'll zoom into the storage and data model."

> "Next I'll explain the processing path."

> "For serving, the key question is who consumes this data."

> "Let me cover cross-cutting concerns such as data quality, reliability, security, and cost."

> "Finally, I'll discuss failure handling and how this evolves at 10× scale."

These transitions are not memorized speeches. They are navigation markers for the interviewer.

---

# 57. Common Failure Patterns

| Mistake | Why it happens | Why it hurts | Better approach |
|---|---|---|---|
| Framework memorization without reasoning | Candidate learned a checklist | Sounds mechanical | Connect every step to requirements |
| Jumping to tools | Technology familiarity dominates | Choices appear arbitrary | State constraints first |
| Huge diagram | Candidate wants to show knowledge | No time for depth | Draw only decision-relevant components |
| Spending 20 minutes on ingestion | Comfortable topic | Reliability/evolution are skipped | Time-box the happy path |
| Ignoring quality | Infrastructure-centric thinking | Correct-looking data can be wrong | Define data-quality signals |
| Ignoring backfills | Only happy path considered | Real pipelines require correction | Design replayability |
| Ignoring late data | Batch mindset applied to streams | Metrics can be wrong | Define event-time behavior |
| Ignoring recovery | Architecture stops at success | Production outages become unexplained | Use failure matrix |
| Ignoring security | Treated as someone else's problem | Sensitive data is exposed | Identify access boundaries |
| Ignoring cost | "Scale" becomes infinite spend | Design is uneconomic | Estimate major cost drivers |
| No evolution | Optimizes today's snapshot | Architecture becomes brittle | Discuss 10× and new consumers |
| Deep-diving everything | Fear of missing detail | Interview loses structure | Pick 1–2 high-risk areas |
| Same architecture everywhere | Memorized solution | Does not match workload | Adapt depth to problem type |
| Technology-first design | Vendor familiarity | Requirements become post-hoc | Choose tools after constraints |

---

# 58. Senior-Level Framework Usage

Weak:

> "I'll use Kafka, Spark, and S3."

Stronger:

> "The freshness requirement is sub-minute and peak throughput is approximately X, so I'll use a streaming ingestion path. I'll retain raw events for replay, process them incrementally, and expose a low-latency serving path. The main risks are late events, duplicates, and state growth."

The difference is:

- Reasoning
- Assumptions
- Trade-offs
- Failure handling
- Operational ownership
- Cost
- Evolution

A senior answer explains **why**.

---

# 59. Staff-Level Framework Usage

Staff-level framework usage adds:

- Platform reuse
- Multiple teams
- Multiple domains
- Governance
- Standard interfaces
- Evolution
- Organizational-scale cost
- Reliability boundaries
- Ownership
- Migration strategy
- Cross-team dependencies

Example:

> "Rather than creating a custom ingestion pattern for every team, I would standardize the source contract, ingestion interface, ownership model, quality gates, and observability. Individual adapters can remain source-specific while the platform enforces common controls."

This is still system-design thinking, not a generic Staff Engineer course.

---

# 60. Adaptive Depth

> **The framework is constant; the depth is variable.**

```text
Analytics
→ More time on data model, query patterns, serving, cost.

Streaming
→ More time on partitioning, ordering, state, late data, replay.

ML
→ More time on feature correctness and serving consistency.

Compliance
→ More time on lineage, deletion, governance, auditability.

RAG
→ More time on permissions, re-indexing, deletion, metadata.
```

A strong candidate can say:

> "I have the broad architecture. The risk I want to explore is X, because it is the component most likely to violate the stated requirement."

---

# 61. Estimation + Framework Integration

Topic 03 and Topic 04 are not separate mental exercises.

```text
Requirements
    ↓
Estimates
    ↓
Architecture
```

Example:

```text
500 GB/day
+
5-minute freshness
+
1-year retention
```

should affect:

- Storage capacity
- Processing frequency
- Retention/lifecycle strategy
- Query architecture
- Cost

If the architecture does not change after estimation, ask whether the estimates were actually used.

---

# 62. Framework + Trade-Offs

Prepare for Topic 05:

```text
Requirement
    ↓
Possible choices
    ↓
Trade-off
    ↓
Decision
```

Example:

```text
Requirement:
<1 minute freshness

Choices:
Batch / micro-batch / streaming

Decision:
Streaming

Why:
Freshness

Trade-off:
Higher operational complexity and cost
```

Do not turn this section into the Topic 05 trade-off catalogue. The goal is learning how the framework creates a place for trade-off reasoning.

---

# 63. Framework + Diagramming

Prepare for Topic 06 by remembering:

- Draw only necessary components.
- Use arrows to show data flow.
- Label important interfaces.
- Show storage boundaries.
- Show serving boundaries.
- Mark critical failure points.
- Avoid diagram clutter.

Topic 06 will develop diagramming and communication in greater depth.

---

# 64. Self-Review Scorecard

Score each area from 1 to 5 after every practice design.

| Area | Score 1–5 |
|---|---:|
| Requirements | |
| Estimates | |
| Data flow | |
| Data model / storage | |
| Processing | |
| Serving | |
| Quality / contracts | |
| Reliability | |
| Security / privacy | |
| Observability | |
| Cost | |
| Failure handling | |
| Evolution | |
| Communication | |

### Scoring interpretation

| Score | Meaning |
|---:|---|
| 1 | Missing or incorrect |
| 2 | Mentioned but shallow |
| 3 | Competent |
| 4 | Strong and reasoned |
| 5 | Clear, quantified, trade-off-aware, production-oriented |

Track the lowest three scores. Those become the next practice targets.

---

# 65. Practice Questions

## Basic — 8

### 1. What is the purpose of a reusable system-design framework?

**What to identify:** Cognitive load, time pressure, completeness.

**Expected framework path:** Explain the nine stages.

**Strong-answer characteristics:** Framework as thinking tool, not script.

**Common mistake:** Treating the framework as a fixed architecture.

**Production takeaway:** Consistent reasoning reduces omissions.

---

### 2. Why should requirements come before technology selection?

**What to identify:** Requirements create constraints.

**Expected framework path:** Requirements → estimates → choices.

**Strong-answer characteristics:** Technology follows workload.

**Common mistake:** Naming a preferred stack immediately.

**Production takeaway:** Avoid architecture by habit.

---

### 3. What is the difference between Bronze, Silver, and Gold?

**What to identify:** Raw/source-fidelity, curated/conformed, business-ready responsibilities.

**Expected framework path:** Flow → storage responsibilities.

**Strong-answer characteristics:** Recognizes these as conceptual layers.

**Common mistake:** Assuming three mandatory physical databases.

**Production takeaway:** Separate data responsibilities clearly.

---

### 4. Why does data grain matter?

**What to identify:** One-row meaning.

**Expected framework path:** Data model → joins → aggregations.

**Strong-answer characteristics:** Gives an order/order-item example.

**Common mistake:** Describing tables without grain.

**Production takeaway:** Explicit grain prevents semantic errors.

---

### 5. What determines the serving interface?

**What to identify:** Consumer requirements.

**Expected framework path:** Processing → serving → consumer.

**Strong-answer characteristics:** BI/API/ML/RAG examples.

**Common mistake:** Picking a serving technology before knowing consumers.

**Production takeaway:** Serving follows access pattern.

---

### 6. What is idempotency?

**What to identify:** Safe repeated processing.

**Expected framework path:** Input identity → write semantics → retry/replay.

**Strong-answer characteristics:** Uses event ID or merge.

**Common mistake:** Equating idempotency with exactly-once delivery.

**Production takeaway:** Retries become safer.

---

### 7. Why are backfills important?

**What to identify:** Historical correction/reprocessing.

**Expected framework path:** Raw retention → replay → corrected outputs.

**Strong-answer characteristics:** Mentions production isolation and verification.

**Common mistake:** Treating backfills as rare emergencies.

**Production takeaway:** Design for correction.

---

### 8. What must a complete design say about failure?

**What to identify:** Failure, detection, recovery, prevention.

**Expected framework path:** Component → failure matrix.

**Strong-answer characteristics:** Gives a concrete example.

**Common mistake:** Only describing happy path.

**Production takeaway:** Recoverability is architectural.

---

## Intermediate — 10

### 9. A dashboard needs 24-hour freshness. Should you stream?

**What to identify:** Requirement-to-architecture reasoning.

**Expected framework path:** Requirements → estimates → batch/micro-batch.

**Strong-answer characteristics:** Says streaming may be unnecessary.

**Common mistake:** Choosing streaming because it is "real time."

**Production takeaway:** Complexity needs justification.

---

### 10. A source database is mutable and downstream consumers need deletes. What should you consider?

**What to identify:** CDC, ordering, deletes, replay.

**Expected framework path:** Source → ingestion → raw → curated.

**Strong-answer characteristics:** Explicitly handles deletes and idempotency.

**Common mistake:** Treating updates as append-only.

**Production takeaway:** Source mutation affects ingestion semantics.

---

### 11. How do you decide partitioning?

**What to identify:** Access patterns and distribution.

**Expected framework path:** Estimates → workload → storage layout.

**Strong-answer characteristics:** Avoids high-cardinality over-partitioning.

**Common mistake:** Partitioning every queried column.

**Production takeaway:** Layout follows workload.

---

### 12. How do pipeline health and data health differ?

**What to identify:** Execution vs correctness.

**Expected framework path:** Observability → data quality.

**Strong-answer characteristics:** Gives row-count/freshness example.

**Common mistake:** Assuming successful jobs imply correct data.

**Production takeaway:** Operational green is not data green.

---

### 13. What should happen when a producer adds a breaking field change?

**What to identify:** Contract and compatibility process.

**Expected framework path:** Schema evolution → producer → pipeline → consumer.

**Strong-answer characteristics:** Compatibility/versioning/migration.

**Common mistake:** Hoping downstream code does not break.

**Production takeaway:** Schema changes are system changes.

---

### 14. What makes a system backfill-friendly?

**What to identify:** Replayable raw data, deterministic/idempotent processing, isolation.

**Expected framework path:** Storage → processing → recovery.

**Strong-answer characteristics:** Verification and production protection.

**Common mistake:** Only increasing compute.

**Production takeaway:** Backfill is a first-class workflow.

---

### 15. What should trigger an alert?

**What to identify:** Actionable, impact-oriented conditions.

**Expected framework path:** SLA/observability → alert.

**Strong-answer characteristics:** Freshness violation, pipeline failure, sustained lag.

**Common mistake:** Alerting on every metric.

**Production takeaway:** Alerts need owners and actions.

---

### 16. What changes when a platform gets a new consumer?

**What to identify:** Serving contract, latency, data shape, governance.

**Expected framework path:** Consumer → serving → contracts.

**Strong-answer characteristics:** Does not blindly reuse existing serving.

**Common mistake:** Assuming the same query path works.

**Production takeaway:** Consumers drive interface design.

---

### 17. When should you deep-dive?

**What to identify:** Highest-risk/highest-complexity component.

**Expected framework path:** Requirements → identify architectural risk → deep dive.

**Strong-answer characteristics:** Names one or two areas.

**Common mistake:** Deep-diving every component.

**Production takeaway:** Depth is a scarce interview resource.

---

### 18. What does 10× scale analysis require?

**What to identify:** Bottlenecks, not just machines.

**Expected framework path:** Estimates → bottleneck analysis → architecture evolution.

**Strong-answer characteristics:** Storage/network/metadata/serving/cost.

**Common mistake:** "Add more workers."

**Production takeaway:** Scaling changes system bottlenecks.

---

## Advanced — 7

### 19. A streaming system has correct throughput but wrong aggregates because events arrive late. Where does the framework take you?

**What to identify:** Event time, state, late data, correction.

**Expected framework path:** Processing → cross-cutting → failure/recovery.

**Strong-answer characteristics:** Defines lateness policy and replay/correction.

**Common mistake:** Looking only at infrastructure metrics.

**Production takeaway:** Correctness is temporal.

---

### 20. A Gold table is correct today but full recomputation becomes impossible at 10× scale. What evolves?

**What to identify:** Incremental processing, storage layout, partitioning, compute.

**Expected framework path:** Estimates → processing → storage → evolution.

**Strong-answer characteristics:** Identifies the bottleneck first.

**Common mistake:** Replacing everything with a new tool immediately.

**Production takeaway:** Evolution should be evidence-driven.

---

### 21. A platform must support BI, ML, and AI consumers from the same curated data. How should you reason?

**What to identify:** Shared governed data vs consumer-specific serving.

**Expected framework path:** Data model → serving → contracts/governance.

**Strong-answer characteristics:** Shared semantic foundations with fit-for-purpose serving.

**Common mistake:** One universal serving store.

**Production takeaway:** Reuse data, not necessarily interfaces.

---

### 22. A CDC source changes a field type while downstream consumers cannot migrate immediately. What should you design?

**What to identify:** Compatibility, versioning, migration.

**Expected framework path:** Data contract → schema evolution → consumer impact.

**Strong-answer characteristics:** Compatibility layer or staged migration.

**Common mistake:** Silently coercing values.

**Production takeaway:** Evolution requires coordination.

---

### 23. A compliance request requires deleting a user's data from raw, curated, and derived outputs. How do you structure the design?

**What to identify:** Identity mapping, lineage, deletion propagation, verification.

**Expected framework path:** Requirements → governance → processing → serving → audit.

**Strong-answer characteristics:** Proves completion.

**Common mistake:** Deleting only the source row.

**Production takeaway:** Derived data creates deletion complexity.

---

### 24. The system is technically correct but costs 5× the target budget. What should happen?

**What to identify:** Cost as a design constraint.

**Expected framework path:** Estimates → architecture → trade-offs.

**Strong-answer characteristics:** Quantifies major drivers and evaluates requirement relaxation.

**Common mistake:** Treating cost as finance's problem.

**Production takeaway:** Economic sustainability is architecture.

---

### 25. An RAG platform adds a new tenant with different permissions and document retention. What changes?

**What to identify:** Tenant isolation, access control, lifecycle, indexing.

**Expected framework path:** Requirements → storage → serving → governance → evolution.

**Strong-answer characteristics:** Treats authorization and deletion as architecture.

**Common mistake:** Adding a tenant ID without isolation analysis.

**Production takeaway:** Multi-tenancy changes failure and governance boundaries.

---

## Senior / Staff — 5

### 26. How would you design a reusable platform for ten teams with different source systems?

**What to identify:** Standard interfaces, contracts, ownership, governance.

**Expected framework path:** Sources → ingestion contract → shared platform controls → team-specific adapters.

**Strong-answer characteristics:** Balances standardization with domain autonomy.

**Common mistake:** One rigid pipeline for everyone.

**Production takeaway:** Platform design is boundary design.

---

### 27. How do you choose between a centralized platform and team-owned pipelines?

**What to identify:** Reuse, ownership, governance, cost, organizational dependencies.

**Expected framework path:** Requirements → operating model → reliability/cost → evolution.

**Strong-answer characteristics:** Uses workload and organizational context.

**Common mistake:** Declaring one model universally superior.

**Production takeaway:** Architecture includes ownership.

---

### 28. A platform is growing 10× while the team size remains constant. What do you prioritize?

**What to identify:** Automation, standardization, observability, cost, managed services where appropriate.

**Expected framework path:** Evolution → operational model → cost → reliability.

**Strong-answer characteristics:** Reduces per-pipeline operational burden.

**Common mistake:** Scaling people linearly with workload.

**Production takeaway:** Staff-level design considers operational leverage.

---

### 29. Multiple teams want different technologies for the same ingestion problem. How should a platform architect respond?

**What to identify:** Standard interface vs implementation choice.

**Expected framework path:** Requirements → platform contract → technology decision → governance.

**Strong-answer characteristics:** Standardizes outcomes/interfaces where valuable, not necessarily every implementation detail.

**Common mistake:** Technology standardization for its own sake.

**Production takeaway:** Standardize the right abstraction.

---

### 30. How would you defend a design when the interviewer proposes a simpler architecture?

**What to identify:** Requirement impact and trade-off.

**Expected framework path:** Revisit requirement → quantify difference → compare choices.

**Strong-answer characteristics:** Willingness to change the design if the simpler option satisfies requirements.

**Common mistake:** Defending personal architecture preferences.

**Production takeaway:** Good architects optimize for requirements, not ego.

---

# 66. Interview Follow-Up Questions

| Follow-up | What the interviewer is testing |
|---|---|
| Why batch instead of streaming? | Requirement-driven architecture |
| What happens if the source is down? | Resilience and recovery |
| What happens if events arrive late? | Temporal correctness |
| How do you backfill? | Replayability and operational maturity |
| What if volume increases 10×? | Scalability reasoning |
| How do you detect bad data? | Data-quality thinking |
| What happens if schema changes? | Contracts and evolution |
| How do you secure PII? | Security/privacy architecture |
| How do you control cost? | Economic reasoning |
| How do you support a new consumer? | Extensibility |
| What is the table grain? | Data modeling |
| What happens on retry? | Idempotency |
| Where is the source of truth? | Data ownership/model |
| How do you reconcile source and target? | Correctness |
| What is your freshness SLA? | Measurable operations |
| What pages an engineer? | Alert quality |
| How do you recover after corruption? | Recovery/replay |
| How do you migrate schema? | Compatibility |
| What is your biggest bottleneck? | Estimation |
| Where would you spend the next ten minutes? | Deep-dive judgment |

---

# 67. Break / Fix Scenarios

## Scenario 1 — Technology First

**Broken design:** Candidate immediately chooses Kafka, Spark, and a lakehouse.

**Diagnosis:** Requirements and estimates are missing.

**Corrected framework path:**

```text
Requirements
→ Estimates
→ Architecture
→ Technology
```

**Improved design:** Choose components only after constraints are established.

---

## Scenario 2 — Ingestion Without Serving

**Broken design:** Candidate spends the interview designing ingestion and storage.

**Diagnosis:** No consumer contract.

**Corrected path:**

```text
Consumers
→ Serving requirements
→ Work backward into data products
```

**Improved design:** Define how consumers actually use the output.

---

## Scenario 3 — Storage Without Retention

**Broken design:** "Store everything forever."

**Diagnosis:** No retention/cost requirement.

**Corrected path:**

```text
Retention requirement
→ Storage estimate
→ Lifecycle strategy
→ Cost
```

**Improved design:** Retain what is required and define lifecycle policy.

---

## Scenario 4 — No Backfills

**Broken design:** Pipeline assumes data is never wrong.

**Diagnosis:** No replay/correction strategy.

**Corrected path:**

```text
Raw retention
→ Idempotent processing
→ Backfill workflow
→ Verification
```

**Improved design:** Make correction a supported operating mode.

---

## Scenario 5 — No Late Data

**Broken design:** Streaming windows close permanently when the first result is produced.

**Diagnosis:** Event-time behavior is undefined.

**Corrected path:**

```text
Event time
→ Lateness policy
→ State/reprocessing
→ Correction
```

**Improved design:** Define late-event handling explicitly.

---

## Scenario 6 — No Data Quality

**Broken design:** Dashboard is considered healthy because jobs are green.

**Diagnosis:** Pipeline health confused with data health.

**Corrected path:**

```text
Execution monitoring
+
Data-quality monitoring
```

**Improved design:** Add completeness, freshness, uniqueness, validity, and distribution checks where relevant.

---

## Scenario 7 — No Failure Recovery

**Broken design:** Diagram stops at "Gold table."

**Diagnosis:** Happy path only.

**Corrected path:**

```text
Failure
→ Detection
→ Recovery
→ Replay
→ Prevention
```

**Improved design:** Failure matrix for critical components.

---

## Scenario 8 — No Cost

**Broken design:** Continuous high-capacity infrastructure is selected for a relaxed freshness requirement.

**Diagnosis:** Cost never entered the requirements.

**Corrected path:**

```text
Freshness requirement
→ Capacity estimate
→ Cost estimate
→ Compare alternatives
```

**Improved design:** Choose the cheapest architecture that satisfies requirements with acceptable risk.

---

## Scenario 9 — Today's Scale Only

**Broken design:** Architecture is sized for 10 TB/day forever.

**Diagnosis:** No growth model.

**Corrected path:**

```text
Current estimate
→ Growth
→ 10× bottleneck analysis
→ Evolution
```

**Improved design:** Identify likely future bottlenecks and migration boundaries.

---

## Scenario 10 — Same Architecture Everywhere

**Broken design:** Analytics, streaming, ML, and compliance all receive the same architecture.

**Diagnosis:** Framework has become a script.

**Corrected path:**

```text
Stable framework
+
Problem-specific depth
```

**Improved design:** Spend time on the dimensions that are unique to the workload.

---

# 68. Three Complete Mock Interviews

## Mock 1 — Analytics

### Prompt

> Design a multi-source analytics platform for a rapidly growing retail business.

### Requirements information

- Hundreds of stores
- Daily operational data
- BI users
- Historical reporting
- Business-critical revenue metrics

### Estimation areas

- Events/records per day
- Daily storage
- Retention
- Query volume
- Freshness

### Framework checklist

- [ ] Requirements
- [ ] Estimates
- [ ] Sources
- [ ] Ingestion
- [ ] Storage layers
- [ ] Data grain
- [ ] Processing
- [ ] Serving
- [ ] Quality
- [ ] Governance
- [ ] Cost
- [ ] Failure
- [ ] Evolution

### Deep-dive area

Data model and incremental processing.

### Failure scenarios

- Source delayed
- Duplicate records
- Incorrect business metric
- Failed daily job

### Evolution question

> What changes when data volume becomes 10× larger and hourly dashboards are added?

### Self-score

Use the 14-area scorecard. Target average: **4+** before considering the mock strong.

---

## Mock 2 — Streaming

### Prompt

> Design a near-real-time clickstream platform for a large consumer application.

### Requirements information

- Continuous events
- Seconds-to-minutes freshness
- High peak volume
- Late events possible
- Analytics and operational consumers

### Estimation areas

- Events/sec
- Peak events/sec
- Event size
- Storage
- Consumer QPS
- State size

### Deep-dive area

Ordering, partitioning, late data, and recovery.

### Failure scenarios

- Consumer lag
- Duplicate events
- Processing restart
- Hot partition
- Late events

### Evolution question

> What breaks first at 10× traffic?

### Self-score

Explicitly score streaming correctness, replay, and failure handling.

---

## Mock 3 — AI/RAG

### Prompt

> Design an enterprise document data platform for permission-aware RAG.

### Requirements information

- Multiple business units
- Document updates and deletes
- Permission-sensitive retrieval
- Low retrieval latency
- Audit requirements

### Estimation areas

- Documents
- Average document size
- Chunks
- Embeddings
- Retrieval QPS
- Re-indexing volume

### Deep-dive area

Permissions, incremental indexing, deletion, and versioning.

### Failure scenarios

- Index partially updated
- Permission changed
- Document deleted
- Embedding version changed
- Source unavailable

### Evolution question

> How does the design change for 10× documents and multiple regions?

### Self-score

Pay special attention to privacy, governance, deletion, and serving.

---

# 69. Python Mini-Projects

## Mini Project 1 — Requirements → Checklist

Create a dictionary of requirements and generate the framework questions you need to answer.

Minimum fields:

```text
freshness
daily_volume
peak_rate
retention
consumers
availability
security
cost
```

## Mini Project 2 — Requirements → Architecture Mapping

Given:

```text
freshness_minutes
volume_gb_day
consumer_type
```

produce a human-readable design recommendation.

Keep it heuristic and explain its assumptions.

## Mini Project 3 — Failure Matrix

Create a list of dictionaries containing:

```text
component
failure
impact
detection
recovery
prevention
```

Then print a readable table.

## Mini Project 4 — Framework Completeness Checker

Reuse the completeness checker from Section 53 and extend it with:

```text
quality
contracts
idempotency
backfills
late_data
schema_evolution
security
privacy
governance
cost
```

## Mini Project 5 — Architecture Decision Record

Represent:

```python
adr = {
    "decision": "micro-batch",
    "why": "five-minute freshness requirement",
    "alternatives": ["batch", "streaming"],
    "tradeoff": "lower complexity than streaming",
    "assumption": "five-minute freshness remains sufficient",
    "failure_mode": "processing delay",
    "cost_implication": "lower continuous compute",
    "future_evolution": "move toward streaming if SLA tightens",
}
```

The objective is structured reasoning, not application development.

---

# 70. Final Master Checklist

## Data Engineering System Design Framework Checklist

```text
[ ] Requirements clarified
[ ] Functional requirements identified
[ ] Non-functional requirements identified
[ ] Assumptions stated
[ ] Estimates completed
[ ] Sources identified
[ ] Ingestion mode selected
[ ] Raw/Bronze layer considered
[ ] Data model defined
[ ] Storage format considered
[ ] Storage layout considered
[ ] Table format considered
[ ] Catalog/governance considered
[ ] Processing model selected
[ ] Processing engine justified
[ ] Orchestration addressed
[ ] Serving interface defined
[ ] Consumers identified
[ ] Data quality addressed
[ ] Data contracts addressed
[ ] Idempotency addressed
[ ] Backfills addressed
[ ] Late data addressed
[ ] Schema evolution addressed
[ ] SLAs addressed
[ ] Observability addressed
[ ] Alerting addressed
[ ] Security addressed
[ ] Privacy addressed
[ ] Governance addressed
[ ] Cost addressed
[ ] Failure scenarios addressed
[ ] Recovery/replay addressed
[ ] 10× scale addressed
[ ] New sources addressed
[ ] New consumers addressed
[ ] Trade-offs explained
[ ] Deep-dive area selected
[ ] Design communicated clearly
```

---

# 71. Final Framework Cheat Sheet

A compact mnemonic created specifically for this learning file is:

```text
R — Requirements
E — Estimates
F — Flow
S — Storage
P — Processing
V — Serving
C — Cross-cutting
F — Failure
E — Evolution
```

## R-E-F-S-P-V-C-F-E

| Letter | Meaning | Core question |
|---|---|---|
| R | Requirements | What must the system do? |
| E | Estimates | How big/fast is it? |
| F | Flow | Where does data come from and go? |
| S | Storage | What is the grain, format, layout, retention? |
| P | Processing | How is data transformed? |
| V | Serving | Who consumes it and how? |
| C | Cross-cutting | Is it correct, reliable, secure, governed, observable, affordable? |
| F | Failure | What breaks and how do we recover? |
| E | Evolution | What happens at 10× or with new sources/consumers? |

> This acronym is a learning mnemonic, not a claim about the authoritative roadmap's terminology.

---

# 72. Roadmap Checkpoint

The learner must demonstrate all three capabilities:

### 1. Apply a structured framework

```text
Requirements
→ Estimates
→ Architecture
→ Cross-cutting
→ Failures
→ Evolution
```

### 2. Cover cross-cutting concerns without prompting

Without a checklist, the learner should naturally discuss:

- Quality
- Contracts
- Idempotency
- Backfills
- Late data
- Schema evolution
- SLAs
- Observability
- Security
- Privacy
- Governance
- Cost

### 3. Choose where to go deep

The learner should be able to say:

> "The highest-risk part of this design is X because it directly threatens requirement Y, so I will spend the next several minutes there."

If the learner can do all three under time pressure, Topic 04 is functioning as intended.

---

# 73. Final Assessment

## Part A — Framework Fundamentals — 10 Questions

1. Why is a reusable framework needed?
2. Why should requirements precede technology selection?
3. What are the nine framework stages?
4. Why do estimates influence architecture?
5. Why is data grain important?
6. What is the purpose of Bronze?
7. What determines a serving interface?
8. Why is idempotency important?
9. Why must failure handling be explicit?
10. Why is evolution mandatory?

### Passing expectation

The learner answers without relying on technology names as substitutes for reasoning.

---

## Part B — Architecture Application — 10 Problems

1. Daily sales analytics
2. Near-real-time clickstream
3. CDC-to-lakehouse
4. IoT telemetry
5. Multi-source customer analytics
6. ML feature platform
7. Enterprise document platform
8. Partner data ingestion
9. Financial reporting platform
10. Multi-region analytics platform

For each:

```text
Requirements
Estimates
Flow
Data model
Storage
Processing
Serving
Cross-cutting
Failure
Evolution
Trade-offs
```

---

## Part C — Cross-Cutting Concerns — 10 Scenarios

1. Duplicate transactions
2. Missing daily partition
3. Freshness SLA violation
4. Breaking schema change
5. PII access request
6. Cost anomaly
7. Unexpected data-volume spike
8. New consumer requiring lower latency
9. Backfill during peak production
10. Data-quality distribution anomaly

For each, identify the affected framework stage and the design response.

---

## Part D — Failure Handling — 10 Scenarios

1. Source unavailable
2. Ingestion job crashes
3. Consumer lag increases
4. Processing produces corrupted output
5. Storage write fails
6. Serving layer becomes unavailable
7. Schema breaks downstream
8. Checkpoint becomes unusable
9. Late data changes published results
10. Backfill produces a conflicting result

For each:

```text
Failure
→ Detection
→ Containment
→ Recovery
→ Replay
→ Prevention
```

---

## Part E — Evolution — 10 Scenarios

1. 2× data
2. 10× data
3. New source
4. New consumer
5. Lower latency SLA
6. Longer retention
7. New region
8. New privacy requirement
9. Cost reduction target
10. New schema version

The learner must identify the architecture boundary affected and explain the likely evolution.

---

## Part F — Full System Design

Complete at least three timed designs:

### Design 1 — Analytics

45–50 minutes.

### Design 2 — Streaming

45–50 minutes.

### Design 3 — AI/RAG or ML

45–50 minutes.

Every design must include:

```text
Requirements
Estimates
High-level flow
Data model
Storage
Processing
Serving
Cross-cutting concerns
Failure handling
Evolution
Trade-offs
```

---

# 74. Completion Criteria

Do not consider this module complete until you can:

1. Explain why a reusable framework is needed.
2. Use the framework without mechanically reciting it.
3. Clarify requirements.
4. Estimate scale.
5. Draw the high-level flow.
6. Define data model and grain.
7. Choose storage characteristics.
8. Choose processing strategy.
9. Define serving interfaces.
10. Address data quality.
11. Address data contracts.
12. Address idempotency.
13. Address backfills.
14. Address late data.
15. Address schema evolution.
16. Address SLAs.
17. Address observability.
18. Address alerting.
19. Address security.
20. Address privacy.
21. Address governance.
22. Address cost.
23. Analyze failures.
24. Explain recovery and replay.
25. Explain evolution.
26. Adapt the framework to analytics.
27. Adapt it to streaming.
28. Adapt it to ML.
29. Adapt it to AI/RAG.
30. Adapt it to compliance.
31. Know where to deep-dive.
32. Communicate clearly under time pressure.
33. Explain major decisions with trade-offs.
34. Handle interviewer follow-ups.
35. Design without blindly selecting technologies first.

---

# 75. Final Operating Standard

A production-ready Data Engineering system-design answer should follow this mental sequence:

```text
1. Clarify what success means.
2. Quantify the workload.
3. Draw the smallest useful data flow.
4. Define data grain and storage responsibilities.
5. Choose processing behavior.
6. Define serving based on consumers.
7. Make correctness, quality, contracts, and operations explicit.
8. Design for failure, recovery, replay, and backfill.
9. Explain cost.
10. Explain 10× scale and new sources/consumers.
11. State the most important trade-offs.
12. Deep-dive only where the requirements make the design difficult.
```

The strongest candidate does not sound like a technology catalogue.

They sound like an engineer who can:

```text
Understand
→
Quantify
→
Structure
→
Choose
→
Defend
→
Operate
→
Recover
→
Evolve
```

---

# 76. Next-Topic Bridge

The dependency chain is:

```text
Topic 02
Requirements
        ↓
Topic 03
Estimates
        ↓
Topic 04
Reusable Framework
        ↓
Topic 05
Trade-offs
        ↓
Topic 06
Diagramming
        ↓
Phase C
Full Design Cases
```

Topic 04 teaches the learner **how to structure the design**.

Topic 05 will teach the learner **how to defend the choices inside that structure**.

Topic 06 will teach the learner **how to communicate the design visually and verbally**.

Phase C will require applying the complete method to realistic end-to-end system-design cases.

---

# 77. Roadmap Coverage Audit

| Roadmap Requirement | Covered? | Where |
|---|---|---|
| Requirements | Yes | Section 4 |
| Estimates | Yes | Section 5 |
| High-level data flow | Yes | Section 6 |
| Sources | Yes | Section 7 |
| Ingestion | Yes | Section 8 |
| Bronze/Silver/Gold | Yes | Section 9 |
| Batch/streaming | Yes | Sections 8, 14 |
| Data model | Yes | Section 10 |
| Storage | Yes | Sections 11–13 |
| Processing | Yes | Sections 14–15 |
| Serving | Yes | Sections 16–17 |
| Consumers | Yes | Section 17 |
| Ingestion mode | Yes | Section 8 |
| Storage format/layout | Yes | Sections 11–13 |
| Table format | Yes | Section 12 |
| Catalog | Yes | Section 12 |
| Processing engine | Yes | Section 15 |
| Orchestration | Yes | Section 16 |
| Data quality | Yes | Section 19 |
| Data contracts | Yes | Section 20 |
| Idempotency | Yes | Section 21 |
| Backfills | Yes | Section 22 |
| Late data | Yes | Section 23 |
| Schema evolution | Yes | Section 24 |
| SLAs | Yes | Section 25 |
| Observability | Yes | Section 26 |
| Alerting | Yes | Section 27 |
| Security | Yes | Section 28 |
| Privacy | Yes | Section 29 |
| Governance | Yes | Section 30 |
| Cost | Yes | Section 31 |
| Time allocation | Yes | Section 39 |
| Deep-dive selection | Yes | Section 40 |
| Analytics adaptation | Yes | Section 41 |
| Streaming adaptation | Yes | Section 42 |
| ML adaptation | Yes | Section 43 |
| AI adaptation | Yes | Section 44 |
| Compliance adaptation | Yes | Section 45 |
| 10× scale evolution | Yes | Section 36 |
| New sources | Yes | Section 37 |
| New consumers | Yes | Section 38 |
| Failure handling | Yes | Sections 32–34 |
| Evolution | Yes | Section 35 |
| Roadmap checkpoint | Yes | Section 72 |

---

# 78. Final Safety and Quality Verification

- **Target filename:** `04-a-reusable-design-framework-for-data-platforms.md`
- **Additional Markdown files:** None created by this deliverable.
- **Additional folders:** None created by this deliverable.
- **Roadmap modification:** None.
- **Scope:** Data Engineering system-design framework, not a replacement for technology-specific modules.
- **Progression:** Beginner → Intermediate → Advanced → Senior → Staff → Interview Application → Production Thinking.
- **Cross-cutting concerns:** First-class.
- **Failure handling:** Mandatory.
- **Evolution:** Mandatory.
- **10× scale:** Explicit.
- **New sources/consumers:** Explicit.
- **Problem adaptation:** Analytics, streaming, ML, AI/RAG, compliance.
- **Topic 03 integration:** Explicit.
- **Topic 05 integration:** Explicit.
- **Topic 06 integration:** Explicit.
- **Phase C bridge:** Explicit.
- **Python examples:** Included as small educational examples.
- **Practice:** 30 framework questions, follow-ups, break/fix scenarios, and three mocks.
- **Final assessment:** Included.
- **Roadmap coverage audit:** Included.

> **Final principle:** The ultimate goal is not memorizing an architecture. The goal is developing the ability to systematically reason about any Data Engineering platform under interview pressure.
