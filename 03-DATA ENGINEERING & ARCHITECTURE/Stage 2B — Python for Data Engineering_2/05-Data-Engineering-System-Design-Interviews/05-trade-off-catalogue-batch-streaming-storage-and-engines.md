# Topic 05 — Trade-Off Catalogue: Batch, Streaming, Storage, and Engines

> **Stage:** G5 — Data Engineering System Design Interviews  
> **Progression:** Absolute Beginner → Foundation → Basic → Intermediate → Advanced → Senior → Staff → Interview Mastery → Production Thinking

## 1. Purpose

This module teaches a core Data Engineering system-design skill:

> **A trade-off is not a list of pros and cons. It is a requirement-driven decision between realistic alternatives.**

The reusable pattern is:

```text
Requirements
↓
Options
↓
Decision criteria
↓
Trade-off analysis
↓
Choice
↓
Why this choice fits these requirements
↓
Consequences
↓
Fallback / alternative
```

The target interview behavior is to replace:

> "It depends."

with:

> "It depends on X, Y, and Z. Given these requirements, I would choose A over B because..., accepting the following trade-off. If requirement Q changed, I would reconsider B."

This module uses technologies such as Kafka, Spark, Flink, DuckDB, Polars, warehouses, lakes, and lakehouses as **examples for architectural decisions**. It does not re-teach their internals.

---

# 2. Why Trade-Offs Matter

Every non-trivial architecture contains competing objectives.

```text
Lower latency
↔
Higher cost / complexity

Higher flexibility
↔
Higher operational burden

Stronger guarantees
↔
More implementation complexity

Faster delivery
↔
Less customization

Managed service
↔
Less operations / potentially more vendor dependence
```

A system-design interview tests whether you can identify the constraint that matters most and make a defensible decision.

### Weak

```text
Kafka:
Pros: scalable, fast
Cons: complex
```

### Strong

```text
Requirement:
100K events/sec, sub-minute freshness, replay, and multiple consumers.

Options:
Kafka-style durable event log
vs
simple task queue

Decision:
Use the event-log approach.

Why:
Replay and independent consumers are first-class requirements.

Trade-off:
Higher operational and platform complexity.

Alternative:
Use a queue if the requirement becomes task dispatch rather than
replayable event distribution.
```

The second answer demonstrates architecture reasoning.

---

# 3. Universal Trade-Off Framework

Use this nine-step process:

```text
1. Clarify the requirement.
2. Identify realistic options.
3. Define the decision criteria.
4. Compare only the dimensions that matter.
5. Select an option.
6. Explain why it fits the requirements.
7. State the trade-off you accept.
8. Explain consequences and risks.
9. Explain when the alternative would win.
```

## Decision template

```text
Requirement:
Options:
Decision criteria:

Option A:
Option B:

Chosen option:
Why:

Trade-off accepted:
Risks:
Mitigations:

Alternative would win when:
Future evolution:
```

## The five-line interview version

```text
Given requirement X,
I would choose A over B because Y.
The main benefit is Z.
The trade-off is W.
If requirement X changed to Q, I would reconsider B.
```

---

# 4. Trade-Off Dimensions

Possible dimensions include:

| Dimension | Core question |
|---|---|
| Latency | How quickly must a result be available? |
| Throughput | How much data/events must the system handle? |
| Freshness | How stale may data be? |
| Correctness | What errors are acceptable? |
| Availability | How much downtime is acceptable? |
| Durability | Must data survive failures? |
| Scalability | How does the system behave as load grows? |
| Complexity | How difficult is the architecture to build and operate? |
| Cost | What is the total economic impact? |
| Operational burden | Who owns incidents, upgrades, capacity, and security? |
| Development speed | How quickly can a useful system ship? |
| Flexibility | How many workloads can it support? |
| Query performance | How quickly can consumers retrieve data? |
| Write performance | How quickly can data be accepted? |
| Maintainability | How easy is the system to change safely? |
| Team expertise | Can the team operate it effectively? |
| Vendor lock-in | How costly is migration? |
| Portability | Can data/workloads move between environments? |
| Governance | Can ownership/access/lineage be controlled? |
| Security | What access and exposure risks exist? |
| Privacy | What happens to sensitive data? |
| Reliability | How does the system behave during failures? |
| Recovery | Can it replay, repair, and restore? |
| Time to market | How quickly can the business obtain value? |

**Do not optimize every dimension simultaneously.** The requirements determine which dimensions dominate.

---

# 5. Requirement → Criteria

The same options can produce different decisions under different requirements.

## Real-time clickstream

Prioritize:

- Freshness
- Throughput
- Latency
- Ordering
- Replay
- State
- Cost

## Financial reporting

Prioritize:

- Correctness
- Auditability
- Reconciliation
- Consistency
- Governance
- Reproducibility

## Internal analytics

Prioritize:

- Cost
- Simplicity
- Query performance
- Maintainability
- Time to market

## ML feature serving

Prioritize:

- Latency
- Freshness
- Point-in-time correctness
- Training/serving consistency
- Availability

## Compliance

Prioritize:

- Governance
- Lineage
- Privacy
- Deletion
- Auditability
- Correctness

> **Mental model:** Requirements choose the trade-off.

---

# 6. Processing Trade-Offs — Batch vs Micro-Batch vs Streaming

## 6.1 Batch

Batch processing handles bounded work periodically.

Examples:

```text
Daily financial reporting
Nightly customer aggregation
Hourly data quality reconciliation
```

### Strengths

- Simple mental model
- Often lower operational complexity
- Frequently economical
- Straightforward backfills
- Easy to reason about deterministic runs

### Weaknesses

- Higher latency
- Cannot satisfy strict real-time requirements
- Large periodic workloads can create resource spikes

### Choose batch when

```text
Freshness requirement is relaxed
AND
periodic processing is sufficient
AND
simplicity/cost matter
```

---

## 6.2 Micro-Batch

Micro-batch processes small batches frequently.

Examples:

```text
Every 30 minutes
Every 5 minutes
Every 1 minute
```

It occupies a useful middle ground.

### Strengths

- Better freshness than traditional batch
- Often simpler than continuous processing
- Can reuse batch-style transformations
- Frequently easier to operate than full streaming

### Weaknesses

- Some latency remains
- More scheduling/execution overhead
- Not suitable when continuous event-by-event processing is genuinely required

---

## 6.3 Streaming

Streaming processes continuously arriving events.

Useful when:

- Freshness is seconds or very low minutes
- Event-driven behavior matters
- Stateful processing is required
- Continuous outputs have material business value

Trade-offs include:

- Ordering
- Late events
- State growth
- Checkpoint/recovery behavior
- Backpressure
- Monitoring
- Higher operational complexity
- Potentially higher cost

### Choose streaming when

```text
Freshness/latency requirements
+
continuous event behavior
+
business value
justify the added complexity.
```

---

# 7. Batch vs Micro-Batch vs Streaming Matrix

| Dimension | Batch | Micro-batch | Streaming |
|---|---|---|---|
| Freshness | Low | Medium | Highest |
| Latency | High | Medium | Low |
| Complexity | Lower | Medium | Higher |
| Cost | Often lower | Medium | Potentially higher |
| Backfills | Usually straightforward | Usually manageable | Can be more complex |
| Stateful processing | Possible | Possible | Common |
| Late data | Less central | Relevant | Central concern |
| Operational burden | Lower | Medium | Higher |
| Best fit | Periodic analytics | Frequent refresh | Continuous/event-driven systems |

No column is universally superior.

---

# 8. Batch vs Micro-Batch vs Streaming Scenarios

### Scenario A

Requirement:

```text
Daily executive revenue report
```

**Decision:** Batch by default.

**Trade-off:** Accept daily latency to gain simplicity and lower operating burden.

### Scenario B

Requirement:

```text
Dashboard must normally be less than 10 minutes stale.
```

**Decision:** Micro-batch is a strong candidate.

**Trade-off:** Accept bounded latency instead of continuous processing.

### Scenario C

Requirement:

```text
Fraud signals must react within seconds.
```

**Decision:** Streaming becomes much more justified.

**Trade-off:** Accept state, operational, and monitoring complexity.

---

# 9. ETL vs ELT

## ETL

```text
Extract
↓
Transform
↓
Load
```

Transformation happens before loading into the destination.

Useful when:

- Data must be transformed before entering a downstream boundary.
- Sensitive information needs filtering/tokenization before loading.
- Destination compute is limited or inappropriate.
- The transformation step is naturally part of ingestion.

## ELT

```text
Extract
↓
Load
↓
Transform
```

Raw or minimally transformed data is loaded first and transformation occurs in the analytical platform.

Useful when:

- Raw data should be retained.
- The target platform has strong analytical compute.
- Teams need transformation flexibility.
- Reprocessing is valuable.

### Trade-off matrix

| Dimension | ETL | ELT |
|---|---|---|
| Raw retention | May require explicit raw path | Natural fit |
| Transformation location | Before target | In target |
| Flexibility | Lower after transformation | Higher |
| Target compute usage | Lower | Higher |
| Reprocessing | Depends on raw retention | Often strong |
| Governance | Can reduce exposure before load | Requires strong controls on raw data |
| Typical fit | Controlled ingestion | Analytical platforms |

**Decision rule:** Neither is universally better.

---

# 10. Storage Trade-Offs — Warehouse vs Lake vs Lakehouse

## 10.1 Warehouse

Optimized primarily for structured analytical workloads and SQL-oriented consumption.

Strengths:

- Strong analytical experience
- Managed operations in many platforms
- Good BI integration
- Predictable analytical workflows

Trade-offs:

- Potentially less flexible for arbitrary raw data
- Cost can depend heavily on compute/query patterns
- Platform-specific capabilities can increase lock-in

## 10.2 Data Lake

A low-level storage foundation commonly based on object storage and flexible file formats.

Strengths:

- Flexible formats
- Large-scale storage
- Good raw-data retention
- Useful foundation for many workloads

Trade-offs:

- More governance/data-management responsibility
- Raw flexibility can become data sprawl
- Query experience depends on surrounding engines/table management

## 10.3 Lakehouse

Combines lake-style storage with managed table semantics and analytical capabilities.

Potential capabilities:

- Transactional table behavior
- Schema management
- Versioning
- Analytical access
- Governance integrations

Trade-offs:

- More platform concepts
- Some platform/table-format dependence
- Requires disciplined governance and layout management

---

# 11. Warehouse vs Lake vs Lakehouse Matrix

| Dimension | Warehouse | Lake | Lakehouse |
|---|---|---|---|
| Structured analytics | Strong | Depends on engine | Strong |
| Raw data | Less natural | Strong | Strong |
| Semi/unstructured | Possible but not primary | Strong | Strong |
| SQL experience | Strong | Engine-dependent | Strong |
| Flexibility | Medium | High | High |
| Governance | Often mature | Must be designed | Strong when integrated |
| Transactional table semantics | Platform-dependent | Not inherent in raw files | Common capability |
| ML/AI data foundation | Possible | Strong | Strong |
| Operational simplicity | Often high | Lower at platform level | Medium |
| Main risk | Cost/lock-in | Governance/sprawl | Platform complexity |

---

# 12. Row vs Columnar

## Row-oriented

Stores fields belonging to a record together.

Good for:

- Point lookups
- Transactional access
- Frequent row-level updates
- Workloads that usually need most columns of a record

## Columnar

Stores values by column.

Good for:

- Analytical scans
- Aggregations
- Column pruning
- Compression
- Reading a subset of columns across many rows

The architectural question is:

```text
Do consumers usually need:
one/few complete rows?
or
selected columns across many rows?
```

### Trade-off

Columnar storage can reduce I/O for analytical scans, but row-oriented access may be more natural for transactional point operations.

---

# 13. Columnar Compression and I/O

Columnar data often compresses efficiently because values in the same column have similar types and distributions.

That can reduce:

- Storage
- Read I/O
- Network transfer

But compression is not magic.

> Better compression does not automatically solve poor data layout, inefficient queries, skew, or an unsuitable serving interface.

Connect this to Topic 03:

```text
Estimated raw volume
→
compression assumption
→
stored volume
→
I/O
→
cost
```

---

# 14. Table-Format Trade-Offs

Raw files provide storage, but analytical table formats can add semantics such as:

- Transactions
- Schema enforcement
- Schema evolution
- Versioning
- Time travel
- Metadata management

The trade-off is between:

```text
Raw-file simplicity/flexibility
vs
Managed table semantics
```

A table format is especially valuable when multiple writers/readers require stronger consistency and lifecycle semantics.

Do not equate a table format with a catalog:

```text
Table format
= how table state/data changes are represented

Catalog
= how assets are discovered, governed, owned, and accessed
```

---

# 15. Ingestion — Pull vs Push

## Pull

The consumer asks for data.

```text
Consumer → Source
```

Strengths:

- Consumer controls retrieval rate
- Simple for some APIs
- Can naturally accommodate polling

Trade-offs:

- Polling delay
- Source load
- Rate-limit management
- Consumer must know how to discover changes

## Push

The producer sends data.

```text
Producer → Consumer
```

Strengths:

- Lower latency
- Event-driven
- Producer can notify consumers immediately

Trade-offs:

- Consumer availability/backpressure must be handled
- Producer/consumer coupling can increase
- Retry semantics matter

### Decision criteria

- Latency
- Source capabilities
- Backpressure
- Failure handling
- Coupling
- Scale
- Operational model

---

# 16. Full vs Incremental vs CDC

## Full load

Extract everything.

Good when:

- Data volume is small
- Source supports efficient snapshots
- Simplicity matters
- Historical state must be periodically reconciled

Trade-off:

```text
Simple
↔
Potentially expensive and slow at scale
```

## Incremental

Extract only new/changed records using a reliable watermark/change field.

Good when:

- Source exposes a trustworthy change indicator
- Deletes are not the primary challenge
- Full scans are expensive

Trade-off:

```text
Lower volume
↔
More correctness logic around watermarks and missed changes
```

## CDC

Capture source changes, including inserts/updates/deletes as supported by the source mechanism.

Good when:

- Source is transactional
- Low latency is valuable
- Updates/deletes matter
- Full extraction is too expensive

Trade-off:

```text
Higher fidelity/freshness
↔
Higher ordering, schema, replay, and operational complexity
```

---

# 17. Managed Connectors vs Custom Ingestion

## Managed connector

Strengths:

- Faster delivery
- Less infrastructure ownership
- Standardized operational behavior
- Often integrated with governance/monitoring

Trade-offs:

- Connector limitations
- Pricing
- Vendor dependency
- Less custom behavior

## Custom code

Strengths:

- Full control
- Custom transformations/retries/protocols
- Can support unusual sources

Trade-offs:

- More testing
- More monitoring
- More maintenance
- More on-call ownership

### Decision

Choose managed ingestion when the source fits well and operational simplicity is valuable.

Choose custom ingestion when requirements genuinely exceed the connector's capabilities.

---

# 18. Processing Engines — DuckDB / Polars vs Spark vs Flink vs Warehouse SQL

## 18.1 DuckDB / Polars

Strong candidates for:

- Local analytics
- Small-to-medium workloads
- Prototyping
- Developer workflows
- Some production workloads that fit a single-node model

Key principle:

> **Distributed does not automatically mean better.**

A distributed engine introduces coordination and operational cost.

## 18.2 Spark

Attractive when:

- Data is large enough to justify distributed processing
- Batch transformations are complex
- Existing ecosystem/team capability matters
- Distributed joins/aggregations are required

Trade-offs:

- Cluster/compute overhead
- Shuffle
- Tuning
- Operational complexity
- Potentially unnecessary cost for smaller workloads

## 18.3 Flink

Attractive when:

- Continuous streaming is central
- Stateful/event-time processing is required
- Low latency matters

Trade-offs:

- Higher operational complexity
- State management
- Debugging and recovery complexity
- Specialized skills

## 18.4 Warehouse SQL

Attractive when:

- Workloads are primarily analytical
- Teams are SQL-heavy
- Managed compute is valuable
- Transformations fit the warehouse's execution model

Trade-offs:

- Platform dependence
- Query/compute pricing
- Specialized workloads may not fit
- Some processing patterns need another engine

---

# 19. Engine Decision Matrix

| Dimension | DuckDB / Polars | Spark | Flink | Warehouse SQL |
|---|---|---|---|---|
| Small data | Strong | Often unnecessary | Usually unnecessary | Strong |
| Huge batch | Limited by node/resources | Strong | Possible but not default | Strong where supported |
| Continuous streaming | Not primary | Possible depending on engine/mode | Strong | Platform-dependent |
| SQL-first | DuckDB strong | Supported | Supported | Strong |
| Local development | Excellent | Heavier | Heavier | Remote/platform dependent |
| Stateful streaming | Not primary | Possible | Strong | Usually not primary |
| Operational burden | Lower | Medium/high | High | Often lower for users |
| Best reason to choose | Simplicity/local speed | Distributed batch | Stateful low-latency streaming | Managed analytics |

This is a reasoning matrix, not a universal ranking.

---

# 20. Messaging — Kafka vs Managed Streams vs Queues

## Kafka-style event log

Strong when you need:

- Durable event history
- Replay
- Multiple independent consumers
- Partitioned high-throughput event processing
- Consumer groups

Trade-offs:

- Operational complexity
- Partition/capacity management
- More concepts for teams to operate

## Managed stream

Provides similar streaming-oriented capabilities while shifting infrastructure operations to a cloud/platform provider.

Trade-offs:

- Less operational work
- Cloud/platform dependence
- Pricing
- Service-specific semantics

## Queue

Strong when the primary need is:

- Work distribution
- Task dispatch
- Producer/consumer decoupling
- Acknowledgement/retry semantics

A queue and a durable event log are not interchangeable.

### Messaging matrix

| Requirement | Kafka-style log | Managed stream | Queue |
|---|---|---|---|
| Replayable event history | Strong | Often strong | Usually not the primary model |
| Independent consumers | Strong | Strong | Depends on queue model |
| Task dispatch | Possible but not primary | Possible | Strong |
| Ordering | Partition/key dependent | Service dependent | Queue dependent |
| Operational burden | Higher | Lower | Lower |
| Cloud integration | Depends | Strong | Strong |
| Main model | Event log | Managed event stream | Work distribution |

---

# 21. Data Modelling — Normalized vs Dimensional vs Wide

## Normalized

Characteristics:

- Lower duplication
- Strong entity integrity
- More joins

Good for:

- Operational systems
- Highly relational domains
- Update consistency

Trade-off:

```text
Less duplication
↔
More joins / analytical query complexity
```

## Dimensional

Characteristics:

- Facts
- Dimensions
- Star/snowflake-style analytical organization

Good for:

- BI
- Business reporting
- Stable analytical semantics

Trade-off:

```text
Analytical usability
↔
Some duplication and modelling effort
```

## Wide

Characteristics:

- Pre-joined consumer-oriented representation
- Fewer runtime joins

Good for:

- Repeated consumer access patterns
- Simple downstream consumption

Trade-offs:

- Duplication
- Larger storage
- More complex updates
- Less flexibility

### Modelling matrix

| Dimension | Normalized | Dimensional | Wide |
|---|---|---|---|
| BI usability | Medium | Strong | Strong |
| Runtime joins | More | Controlled | Fewer |
| Duplication | Lower | Medium | Higher |
| Flexibility | Strong | Strong | Lower |
| Query simplicity | Lower | Strong | Strong |
| Update complexity | Lower at entity level | Medium | Higher |
| Typical fit | Operational | Analytics | Consumer-specific serving |

---

# 22. Correctness — At-Least-Once + Idempotency vs Exactly-Once

## At-least-once

The system may process an event more than once but is designed to avoid silent loss under its stated failure model.

Duplicates are possible.

## Idempotency

```text
Same logical input processed repeatedly
→
same intended business outcome
```

Common mechanisms:

- Stable event IDs
- Deduplication keys
- Upserts
- Merge semantics
- Unique constraints where appropriate

## Exactly-once

"Exactly-once" must be scoped.

Distinguish:

```text
Exactly-once delivery
Exactly-once processing
Exactly-once business effect
```

A system can use at-least-once delivery and still produce an exactly-once **business effect** when the downstream operation is idempotent.

### Decision principle

Do not automatically choose the strongest guarantee.

Ask:

```text
What correctness guarantee does the business actually require?
```

If idempotent processing provides the required business outcome with less complexity, it may be preferable.

---

# 23. Deduplication Strategies

Common approaches:

- Stable event IDs
- Natural/business keys
- Hashes
- Watermarks
- State stores
- MERGE/upsert
- Database uniqueness constraints

Trade-offs involve:

```text
State size
Latency
Memory
Storage
Complexity
False-positive/false-negative risk
Recovery behavior
```

Example:

```text
Stable event_id
+
dedupe state
+
bounded retention
```

may be sufficient for one workload, while a financial ledger may need stronger transactional semantics.

---

# 24. Correctness Matrix

| Strategy | Complexity | Duplicate risk | Recovery | Performance | Typical fit |
|---|---|---|---|---|---|
| At-least-once | Lower | Higher | Strong with replay | Strong | Many pipelines |
| At-least-once + idempotency | Medium | Low business-effect risk | Strong | Strong | Most retry-heavy pipelines |
| Transactional exactly-once | Higher | Lower within guarantee boundary | Strong | Can cost more | Requirements justify it |
| Post-processing dedupe | Medium | Temporary duplicates possible | Good | Depends on state | Analytical correction workflows |

---

# 25. Serving — Direct Query vs Pre-Aggregation vs Cache vs Specialized Store

## Direct query

Use when:

- Queries are flexible
- Query volume is manageable
- Source engine can satisfy latency

Trade-offs:

- Repeated computation
- Potential latency
- Concurrency pressure
- Query cost

## Pre-aggregation

Use when:

- Query patterns are predictable
- Repeated aggregation is expensive
- Faster reads matter

Trade-offs:

- Additional storage
- Refresh complexity
- Staleness
- More pipelines

## Cache

Use when:

- Access is repetitive
- Low latency is important
- Some staleness is acceptable

Trade-offs:

- Invalidation
- Staleness
- Memory
- Additional operational behavior

## Specialized store

Useful when the access pattern itself is specialized:

- Search
- Time-series
- Key-value
- Vector retrieval
- Low-latency analytical access

> Choose the serving technology based on the access pattern, not the technology's popularity.

---

# 26. Serving Matrix

| Requirement | Direct query | Pre-aggregation | Cache | Specialized store |
|---|---|---|---|---|
| Lowest architecture complexity | Strong | Medium | Medium | Lower only when clearly justified |
| Flexible queries | Strong | Lower | Low | Depends |
| Lowest latency | Weak/medium | Strong | Strong | Strong |
| High repeated QPS | Medium | Strong | Strong | Strong |
| Freshness | Strong if source is fresh | Depends on refresh | Can be stale | Depends |
| Repeated computation reduction | Weak | Strong | Strong | Strong |
| Main risk | Query cost/latency | Refresh complexity | Invalidation | Specialized operations |

---

# 27. Managed vs Self-Hosted

## Managed

Strengths:

- Faster delivery
- Less infrastructure ownership
- Provider handles many upgrades/scaling responsibilities
- Potentially easier operations

Trade-offs:

- Vendor dependence
- Pricing
- Service constraints
- Migration cost

## Self-hosted

Strengths:

- Control
- Customization
- Potential portability
- Direct infrastructure control

Trade-offs:

- Staffing
- Upgrades
- Patching
- Monitoring
- Reliability engineering
- Capacity planning
- On-call

### Decision

Managed is often attractive when the service fits requirements and reducing operational burden has high value.

Self-hosting becomes more attractive when control, specialized behavior, economics at scale, or portability justify the additional responsibility.

---

# 28. Build vs Buy

Ask:

1. Is this a core competitive differentiator?
2. Is a mature solution available?
3. How much customization is actually required?
4. What is total cost of ownership?
5. What is the time-to-market requirement?
6. What operational expertise exists?
7. What are the lock-in risks?
8. What is the migration cost if the choice fails?

### Decision matrix

| Criterion | Build tends to win | Buy/managed tends to win |
|---|---|---|
| Differentiation | High | Low |
| Customization | High | Moderate |
| Time to market | Low priority | High priority |
| Team expertise | Strong | Limited |
| Operations | Willing to own | Want to reduce |
| Mature market solution | Poor fit | Strong fit |
| Long-term control | High priority | Lower priority |

---

# 29. One Engine vs Several

## One engine

Advantages:

- Standardization
- Smaller skill surface
- Easier monitoring
- Simpler deployment
- Lower organizational complexity

Trade-offs:

- Workload compromise
- Potential performance limitations
- Engine may be poor for some specialized workloads

## Multiple engines

Advantages:

- Workload specialization
- Better fit for distinct processing patterns

Trade-offs:

- More skills
- More infrastructure
- More observability
- More deployment complexity
- More governance
- More on-call surfaces

> **"Best tool for every workload" can become an organizational anti-pattern.**

The best architecture may intentionally standardize on a slightly less specialized tool because the total organizational cost is lower.

---

# 30. Cost vs Freshness vs Complexity

A common architecture triangle is:

```text
             Freshness
                /\
               /  \
              /    \
             /      \
            /________\
         Cost       Complexity
```

Increasing freshness often means:

```text
More frequent/continuous processing
→
More infrastructure activity
→
More monitoring/state/recovery concerns
→
Potentially higher cost
```

But this relationship is workload-dependent.

### Interview answer

> "The business wants one-minute freshness, but if fifteen-minute freshness is acceptable, I would consider micro-batch because it may deliver most of the business value with materially lower operational complexity."

---

# 31. Organizational Trade-Offs

## Team skills

A technically excellent technology is a poor choice if nobody can operate it safely.

```text
Technical fit
+
Team capability
=
Practical architecture fit
```

## Operational load

Compare:

```text
Managed service
vs
self-managed infrastructure
```

Account for:

- On-call
- Upgrades
- Scaling
- Monitoring
- Patching
- Incident response
- Security

## Vendor lock-in

Consider:

- Proprietary APIs
- Proprietary formats
- Query languages
- Control planes
- Metadata
- Operational dependencies
- Migration tooling

Lock-in can be acceptable when:

```text
Business value gained
>
Expected migration/lock-in cost
```

## Time to market

A custom platform may offer more control but delay business value.

A managed solution may ship faster but reduce customization.

---

# 32. Complexity Has a Cost

Complexity creates:

- Engineering effort
- On-call load
- Debugging time
- Upgrade work
- Security work
- Training requirements
- Documentation burden
- Incident-response cost
- Hiring constraints

A useful rule:

> **Every architectural capability should have a requirement that justifies its operational cost.**

---

# 33. Total Cost of Ownership

Conceptually:

```text
TCO =
Infrastructure
+
Engineering
+
Operations
+
Maintenance
+
Training
+
Incident cost
+
Migration cost
```

The cheapest cloud bill is not necessarily the cheapest architecture.

A system requiring three specialized teams to operate may cost more than a managed platform with a higher infrastructure bill.

---

# 34. Trade-Off Catalogue — 35 Core Decisions

## 1. Batch vs Streaming

**Option A:** Batch  
**Option B:** Streaming  
**Criteria:** Freshness, state, complexity, cost.  
**Choose A when:** Periodic freshness is sufficient.  
**Choose B when:** Continuous low-latency behavior is valuable.  
**Trade-off:** Simplicity/cost vs freshness.  
**Common mistake:** Assuming streaming is automatically more modern.  
**Interview answer:** "Given hourly freshness, I'd start with batch or micro-batch; streaming would be justified only if lower latency creates business value."  
**Production example:** Daily reporting vs fraud detection.

---

## 2. Batch vs Micro-Batch

**Criteria:** Required freshness, execution overhead, simplicity.  
**Choose batch when:** Hours/day are acceptable.  
**Choose micro-batch when:** Minutes matter.  
**Trade-off:** Simplicity vs freshness.  
**Common mistake:** Choosing continuous streaming when five-minute refresh is enough.  
**Interview answer:** "Five-minute freshness makes micro-batch attractive if continuous processing is not required."  
**Production example:** Frequent operational dashboards.

---

## 3. Micro-Batch vs Streaming

**Criteria:** Latency, event semantics, state, operational burden.  
**Choose micro-batch when:** Bounded delay is acceptable.  
**Choose streaming when:** Seconds-level continuous behavior matters.  
**Trade-off:** Operational simplicity vs latency.  
**Common mistake:** Ignoring business value of freshness.  
**Production example:** Alerting vs hourly KPI refresh.

---

## 4. ETL vs ELT

**Criteria:** Transformation location, raw retention, target compute, governance.  
**Choose ETL when:** Data must be transformed before the destination boundary.  
**Choose ELT when:** Target analytical compute and raw retention are valuable.  
**Trade-off:** Pre-load control vs post-load flexibility.  
**Common mistake:** Calling ELT universally modern.  
**Production example:** PII filtering before loading vs warehouse-native transformations.

---

## 5. Warehouse vs Lake

**Criteria:** Analytical serving, raw data, flexibility, governance.  
**Choose warehouse when:** Structured analytics dominate.  
**Choose lake when:** Flexible large-scale storage/raw data dominates.  
**Trade-off:** Analytical convenience vs raw flexibility.  
**Common mistake:** Treating a lake as a complete analytical platform by itself.  
**Production example:** BI warehouse vs raw object-storage foundation.

---

## 6. Lake vs Lakehouse

**Criteria:** Table semantics, transactions, governance, analytical access.  
**Choose lake when:** Raw/flexible storage is the primary need.  
**Choose lakehouse when:** Managed analytical table semantics are important.  
**Trade-off:** Simplicity of raw storage vs richer table capabilities.  
**Common mistake:** Assuming a lakehouse eliminates governance.  
**Production example:** Raw archive vs governed analytical tables.

---

## 7. Warehouse vs Lakehouse

**Criteria:** Workload diversity, governance, SQL experience, raw data, platform strategy.  
**Choose warehouse when:** SQL analytics and managed BI are dominant.  
**Choose lakehouse when:** Analytics, data engineering, ML/AI, and open-ish storage concerns overlap.  
**Trade-off:** Specialized analytical simplicity vs broader workload flexibility.  
**Common mistake:** Choosing based on branding.  
**Production example:** BI-first organization vs mixed analytics/ML platform.

---

## 8. Row vs Columnar

**Criteria:** Access pattern, scans, point lookups, compression.  
**Choose row when:** Complete records/point access dominate.  
**Choose columnar when:** Large analytical scans and selective columns dominate.  
**Trade-off:** Row access vs analytical scan efficiency.  
**Common mistake:** Choosing based on file popularity.  
**Production example:** Operational lookup vs analytical aggregation.

---

## 9. Pull vs Push

**Criteria:** Latency, source behavior, backpressure, coupling.  
**Choose pull when:** Consumers control retrieval and polling is acceptable.  
**Choose push when:** Producers can notify consumers and low latency matters.  
**Trade-off:** Consumer control vs event-driven freshness.  
**Common mistake:** Ignoring source API/rate limits.  
**Production example:** SaaS polling vs event webhook.

---

## 10. Full vs Incremental

**Criteria:** Data volume, change tracking, simplicity.  
**Choose full when:** Dataset is small or periodic reconciliation is valuable.  
**Choose incremental when:** Full extraction is expensive.  
**Trade-off:** Simplicity vs efficiency.  
**Common mistake:** Assuming incremental logic is free.  
**Production example:** Small reference table vs billion-row event table.

---

## 11. Incremental vs CDC

**Criteria:** Deletes, updates, latency, source capabilities.  
**Choose incremental when:** A reliable watermark is sufficient.  
**Choose CDC when:** Transaction-level change fidelity matters.  
**Trade-off:** Simpler ingestion vs richer change semantics.  
**Common mistake:** Ignoring deletes.  
**Production example:** Append-heavy table vs transactional order database.

---

## 12. Managed Connector vs Custom

**Criteria:** Source compatibility, customization, operations, speed.  
**Choose managed when:** Standard connector meets requirements.  
**Choose custom when:** Unique behavior is required.  
**Trade-off:** Speed/operations vs control.  
**Common mistake:** Rebuilding mature connectors.  
**Production example:** Standard SaaS ingestion vs proprietary protocol.

---

## 13. DuckDB/Polars vs Spark

**Criteria:** Data size, distribution need, local development, complexity.  
**Choose DuckDB/Polars when:** Work fits a node and simplicity matters.  
**Choose Spark when:** Distributed computation is genuinely required.  
**Trade-off:** Simplicity vs distributed scale.  
**Common mistake:** Using Spark because the data is called "big data" without estimating.  
**Production example:** Local 20 GB transformation vs multi-terabyte distributed join.

---

## 14. Spark vs Flink

**Criteria:** Batch vs continuous streaming, state, latency, ecosystem.  
**Choose Spark when:** Large-scale batch is central or existing Spark platform fit is strong.  
**Choose Flink when:** Low-latency stateful stream processing is central.  
**Trade-off:** Batch ecosystem vs streaming specialization.  
**Common mistake:** Treating the engines as interchangeable.  
**Production example:** Nightly transformation vs stateful event processing.

---

## 15. Spark vs Warehouse SQL

**Criteria:** Transformation type, data location, SQL skill, operational burden.  
**Choose warehouse SQL when:** Transformations fit analytical SQL and managed compute is valuable.  
**Choose Spark when:** Distributed/custom processing requires it.  
**Trade-off:** Managed simplicity vs processing flexibility.  
**Common mistake:** Moving every SQL transformation to Spark.  
**Production example:** ELT model vs custom distributed transformation.

---

## 16. Flink vs Managed Streaming

**Criteria:** Custom stateful processing, operational capacity, cloud dependence.  
**Choose Flink when:** Specialized streaming control is justified.  
**Choose managed streaming when:** Reducing operations has higher value.  
**Trade-off:** Control vs operational simplicity.  
**Common mistake:** Ignoring team skills.  
**Production example:** Specialized stream processing vs cloud-managed event pipeline.

---

## 17. Kafka vs Queue

**Criteria:** Replay, event history, consumer model, task dispatch.  
**Choose Kafka when:** Durable replayable events and independent consumers matter.  
**Choose queue when:** Work distribution is primary.  
**Trade-off:** Rich event-log semantics vs simpler task dispatch.  
**Common mistake:** Calling Kafka "better" universally.  
**Production example:** Clickstream fan-out vs background email jobs.

---

## 18. Kafka vs Managed Stream

**Criteria:** Operations, portability, cloud integration, pricing, control.  
**Choose Kafka when:** Ecosystem/control/portability requirements justify it.  
**Choose managed stream when:** Provider integration and lower operations dominate.  
**Trade-off:** Control vs operational simplicity.  
**Common mistake:** Ignoring cloud strategy.  
**Production example:** Cloud-native event pipeline vs multi-environment streaming platform.

---

## 19. Normalized vs Dimensional

**Criteria:** Update behavior, joins, BI usability, semantics.  
**Choose normalized when:** Entity integrity and transactional modeling dominate.  
**Choose dimensional when:** Analytical consumption dominates.  
**Trade-off:** Normalization vs analytical usability.  
**Common mistake:** Using operational normalization directly for every BI workload.  
**Production example:** Operational customer model vs analytics star schema.

---

## 20. Dimensional vs Wide

**Criteria:** Reuse, duplication, query simplicity, update patterns.  
**Choose dimensional when:** Shared reusable dimensions and measures matter.  
**Choose wide when:** Consumer-specific simplicity dominates.  
**Trade-off:** Reusability vs convenience.  
**Common mistake:** Creating huge wide tables for every consumer.  
**Production example:** Enterprise semantic model vs dashboard-specific dataset.

---

## 21. At-Least-Once vs Exactly-Once

**Criteria:** Business correctness, complexity, transactional boundaries.  
**Choose at-least-once + idempotency when:** Business effects can be made safely repeatable.  
**Choose stronger transactional semantics when:** The requirement truly demands them.  
**Trade-off:** Simplicity/performance vs stronger guarantees.  
**Common mistake:** Treating "exactly once" as a universal property.  
**Production example:** Idempotent analytical upsert vs financial state transition.

---

## 22. Idempotency vs Transactional Semantics

**Criteria:** Business effect, retry behavior, state boundaries.  
**Choose idempotency when:** Repeated operations can safely converge.  
**Choose transactions when:** multiple state changes must commit atomically.  
**Trade-off:** Simpler recovery vs stronger atomicity.  
**Common mistake:** Adding distributed transactions when deterministic idempotency is enough.  
**Production example:** Event upsert vs multi-table financial transfer.

---

## 23. Direct Query vs Pre-Aggregation

**Criteria:** Query flexibility, QPS, latency, refresh.  
**Choose direct query when:** Workloads are flexible and manageable.  
**Choose pre-aggregation when:** Repeated known aggregations dominate.  
**Trade-off:** Freshness/flexibility vs read speed.  
**Common mistake:** Precomputing everything.  
**Production example:** Ad hoc analyst queries vs executive KPI dashboard.

---

## 24. Pre-Aggregation vs Cache

**Criteria:** Query computation, freshness, access repetition.  
**Choose pre-aggregation when:** A durable derived dataset has value.  
**Choose cache when:** Repeated identical access benefits from transient acceleration.  
**Trade-off:** Durable computation vs invalidation complexity.  
**Common mistake:** Using cache to hide a bad data model.  
**Production example:** Daily sales aggregate vs hot API response.

---

## 25. Cache vs Specialized Store

**Criteria:** Access pattern, persistence, consistency, query capability.  
**Choose cache when:** Temporary acceleration is enough.  
**Choose specialized store when:** The access pattern requires persistent specialized indexing/query behavior.  
**Trade-off:** Simplicity vs capability.  
**Common mistake:** Treating a cache as the source of truth.  
**Production example:** Hot lookup cache vs vector/search index.

---

## 26. Managed vs Self-Hosted

**Criteria:** Team capability, control, cost, operations, portability.  
**Choose managed when:** Operational burden should be minimized.  
**Choose self-hosted when:** control/customization materially justifies ownership.  
**Trade-off:** Control vs operations.  
**Common mistake:** Ignoring on-call cost.  
**Production example:** Managed analytical platform vs internally operated processing cluster.

---

## 27. Build vs Buy

**Criteria:** Differentiation, customization, TCO, time to market.  
**Choose build when:** The capability is strategic and sufficiently unique.  
**Choose buy when:** Mature solutions exist and operations are not differentiating.  
**Trade-off:** Control vs delivery/maintenance burden.  
**Common mistake:** Building commodity infrastructure.  
**Production example:** Custom domain logic vs managed ingestion service.

---

## 28. One Engine vs Multiple

**Criteria:** Standardization, specialization, team skills, operational burden.  
**Choose one when:** Workloads are similar enough and platform simplicity matters.  
**Choose several when:** Distinct workload needs justify the complexity.  
**Trade-off:** Standardization vs specialization.  
**Common mistake:** Tool proliferation.  
**Production example:** Standard SQL engine vs separate streaming and batch engines.

---

## 29. Lower Cost vs Lower Latency

**Criteria:** Business value of freshness, user experience, budget.  
**Choose lower cost when:** Higher latency does not materially hurt the business.  
**Choose lower latency when:** Freshness has measurable business value.  
**Trade-off:** Economic efficiency vs responsiveness.  
**Common mistake:** Optimizing latency without measuring its value.  
**Production example:** Daily finance report vs fraud decisioning.

---

## 30. Faster Delivery vs Customization

**Criteria:** Time to market, strategic differentiation, requirements maturity.  
**Choose faster delivery when:** Standard functionality meets the requirement.  
**Choose customization when:** Unique requirements create material value.  
**Trade-off:** Speed vs control.  
**Common mistake:** Customizing before validating the requirement.  
**Production example:** Managed connector vs bespoke ingestion framework.

---

## 31. Replayability vs Minimal Storage

**Criteria:** Recovery requirements, retention, storage cost.  
**Choose replayability when:** Reprocessing and auditability matter.  
**Choose minimal retention when:** Data can be safely reconstructed elsewhere and policy allows.  
**Trade-off:** Recovery capability vs storage cost.  
**Common mistake:** Deleting raw data before proving downstream correctness.  
**Production example:** Immutable event archive vs short-lived intermediate data.

---

## 32. Strong Governance vs Maximum Data Access

**Criteria:** Sensitivity, compliance, collaboration needs.  
**Choose stronger governance when:** Data risk is high.  
**Choose broader access when:** Data is low-risk and collaboration value dominates.  
**Trade-off:** Control vs convenience.  
**Common mistake:** Treating governance as either zero or absolute.  
**Production example:** PII datasets vs public analytics.

---

## 33. Centralized Platform vs Team-Owned Pipelines

**Criteria:** Reuse, autonomy, governance, scale, ownership.  
**Choose centralized controls when:** Common requirements dominate.  
**Choose team ownership when:** Domains require high autonomy.  
**Trade-off:** Standardization vs local flexibility.  
**Common mistake:** Centralizing every implementation detail.  
**Production example:** Shared contracts/observability with domain-owned transformations.

---

## 34. Shared Infrastructure vs Isolation

**Criteria:** Cost, noisy-neighbor risk, security, reliability.  
**Choose sharing when:** Workloads are compatible and cost matters.  
**Choose isolation when:** Security, performance, or failure boundaries justify it.  
**Trade-off:** Utilization vs isolation.  
**Common mistake:** Assuming isolation is always safer or sharing is always cheaper.  
**Production example:** Shared analytics compute vs isolated regulated workload.

---

## 35. Open Portability vs Deep Platform Integration

**Criteria:** Vendor strategy, migration probability, productivity, ecosystem value.  
**Choose portability when:** Multi-platform migration is realistic and strategically important.  
**Choose deep integration when:** Platform productivity materially outweighs migration concerns.  
**Trade-off:** Portability vs platform leverage.  
**Common mistake:** Paying high complexity for hypothetical future migration.  
**Production example:** Standard open formats vs provider-native managed features.

---

# 35.1 One-Minute Trade-Off Examples

## Batch or streaming?

> "I would choose based primarily on freshness and whether continuous processing creates business value. If hourly or daily freshness is sufficient, batch reduces operational complexity and cost. If the business needs seconds-level reaction, streaming becomes justified. The trade-off is freshness versus complexity and cost."

## Kafka or queue?

> "I would choose Kafka-style event streaming when replayable event history and multiple independent consumers are important. I would choose a queue when the primary problem is distributing work to workers. The trade-off is richer event-log semantics versus simpler task dispatch."

## Spark or DuckDB?

> "I would first estimate the workload. If the data fits comfortably on one machine and the transformation is straightforward, DuckDB or Polars may be preferable because distributed infrastructure adds complexity. I would move to Spark when distributed compute is genuinely required."

## Spark or Flink?

> "I would choose based on the dominant execution model. Spark is attractive for large-scale batch and existing distributed data platforms; Flink is attractive when continuous, stateful, event-time processing is central. The trade-off is workload specialization versus platform fit and operational complexity."

## Lake or warehouse?

> "If the dominant requirement is governed SQL analytics, I would lean toward a warehouse. If retaining diverse raw data at scale and supporting varied processing workloads is central, a lake is attractive. The trade-off is analytical convenience versus storage and workload flexibility."

## Exactly-once or idempotency?

> "I would first define the required business guarantee. If repeated processing can safely converge through stable keys and idempotent writes, that may provide the required outcome with less complexity. I would use stronger transactional semantics when atomicity across the relevant state boundary is actually required."

---

# 36. "It Depends" Framework

When asked:

> "Would you use Kafka or a queue?"

Do not stop at "it depends."

Say:

```text
It depends primarily on:
1. Whether replay is required.
2. Whether multiple independent consumers exist.
3. Whether this is an event-log problem or task-dispatch problem.
4. Required ordering and throughput.
5. Operational constraints.

Given replay + multiple consumers, I would choose the event-log approach.
If the requirement is simple work distribution, I would choose a queue.
```

That is the target behavior.

---

# 37. Decision Tree

```text
What is the requirement?
        ↓
What are the realistic options?
        ↓
What dimensions matter?
        ↓
What is the dominant constraint?
        ↓
Which option satisfies it best?
        ↓
What trade-off am I accepting?
        ↓
What could fail?
        ↓
When would I choose the alternative?
        ↓
What changes at 10× scale?
```

---

# 38. Requirements → Trade-Offs → Decisions

## Analytics

```text
Requirement:
Daily reporting + moderate query volume.

Options:
Batch vs streaming.

Decision:
Batch.

Reason:
Freshness does not justify continuous processing.

Trade-off:
Higher latency for lower complexity/cost.
```

## Clickstream

```text
Requirement:
Seconds-to-minutes freshness.

Options:
Batch / micro-batch / streaming.

Decision:
Streaming or frequent micro-batch depending on exact SLA.

Trade-off:
Operational complexity for freshness.
```

## CDC

```text
Requirement:
Updates/deletes + low-latency replication.

Options:
Full / incremental / CDC.

Decision:
CDC.

Trade-off:
Higher operational complexity for richer change fidelity.
```

## ML

```text
Requirement:
Low-latency online features + historical training.

Decision:
Separate but consistent offline/online serving paths.

Trade-off:
More platform complexity for latency and correctness.
```

## RAG

```text
Requirement:
Permission-aware low-latency retrieval.

Decision:
Specialized retrieval index backed by governed source data.

Trade-off:
Index maintenance and consistency complexity.
```

## IoT

```text
Requirement:
High event rate + near-real-time monitoring.

Decision:
Streaming ingestion.

Trade-off:
State, observability, and operational burden.
```

## Logs

```text
Requirement:
Large volume + historical investigation.

Decision:
Low-cost durable storage plus fit-for-purpose analytical serving.

Trade-off:
Potentially higher query latency for lower storage cost.
```

## Compliance

```text
Requirement:
Provable deletion and auditability.

Decision:
Governed lineage-aware data architecture.

Trade-off:
More metadata and operational controls.
```

## Financial reporting

```text
Requirement:
Auditability and correctness.

Decision:
Favor deterministic/reconcilable processing over minimum latency.

Trade-off:
Potentially higher processing delay.
```

## E-commerce

```text
Requirement:
Operational transactions + analytical reporting.

Decision:
Separate operational and analytical serving responsibilities.

Trade-off:
Data movement/duplication for workload isolation.
```

---

# 39. Python — Weighted Decision Matrix

Python can make assumptions explicit.

```python
options = {
    "batch": {
        "freshness": 1,
        "complexity": 5,
        "cost": 5,
    },
    "streaming": {
        "freshness": 5,
        "complexity": 2,
        "cost": 2,
    },
}

weights = {
    "freshness": 0.6,
    "complexity": 0.2,
    "cost": 0.2,
}

def score(option):
    return sum(
        options[option][criterion] * weight
        for criterion, weight in weights.items()
    )

scores = {name: score(name) for name in options}
print(scores)
```

### Important

This is an educational decision aid.

A numeric score cannot fully model:

- Security boundaries
- Failure modes
- Organizational constraints
- Irreversible platform decisions
- Unknown unknowns

Use scoring to make assumptions visible, not to outsource engineering judgment.

---

# 40. Python — Processing Decision Helper

```python
def choose_processing_mode(
    freshness_minutes,
    complexity_tolerance="medium",
):
    if freshness_minutes <= 1:
        return "streaming"

    if freshness_minutes <= 30:
        return "micro-batch"

    return "batch"
```

This is intentionally simplified.

Real decisions also require:

- Volume
- State
- Source capability
- Correctness
- Cost
- Team capability
- Existing platform
- Recovery requirements

---

# 41. Python — Cost/Freshness Comparison

```python
options = {
    "batch": {
        "freshness_minutes": 1440,
        "monthly_cost": 1000,
        "complexity": 1,
    },
    "micro_batch": {
        "freshness_minutes": 10,
        "monthly_cost": 2200,
        "complexity": 2,
    },
    "streaming": {
        "freshness_minutes": 1,
        "monthly_cost": 5000,
        "complexity": 4,
    },
}

for name, values in options.items():
    print(
        name,
        "freshness=", values["freshness_minutes"],
        "cost=", values["monthly_cost"],
        "complexity=", values["complexity"],
    )
```

The point is to expose the trade-off:

```text
Freshness improves
→
cost/complexity may increase
```

The actual numbers must come from the real environment.

---

# 42. Python — Engine Matrix

```python
engines = {
    "DuckDB": {
        "local": 5,
        "distributed_batch": 1,
        "streaming": 1,
        "simplicity": 5,
    },
    "Spark": {
        "local": 2,
        "distributed_batch": 5,
        "streaming": 3,
        "simplicity": 2,
    },
    "Flink": {
        "local": 1,
        "distributed_batch": 2,
        "streaming": 5,
        "simplicity": 1,
    },
    "Warehouse SQL": {
        "local": 1,
        "distributed_batch": 4,
        "streaming": 2,
        "simplicity": 4,
    },
}
```

These scores are deliberately illustrative rather than universal.

---

# 43. Python — Trade-Off Catalogue

```python
tradeoffs = [
    {
        "name": "batch_vs_streaming",
        "criterion": "freshness",
        "alternative": "streaming",
        "default": "batch_when_latency_is_relaxed",
    },
    {
        "name": "spark_vs_duckdb",
        "criterion": "distributed_scale",
        "alternative": "duckdb",
        "default": "duckdb_when_one_node_is_sufficient",
    },
]

for tradeoff in tradeoffs:
    print(
        tradeoff["name"],
        "criterion:", tradeoff["criterion"],
        "alternative:", tradeoff["alternative"],
    )
```

The data structure encourages explicit decision criteria rather than technology preference.

---

# 44. Python — TCO Model

```python
def total_cost(
    infrastructure,
    engineering,
    operations,
    maintenance,
    training,
    incidents,
    migration,
):
    return sum([
        infrastructure,
        engineering,
        operations,
        maintenance,
        training,
        incidents,
        migration,
    ])

tco = total_cost(
    infrastructure=100_000,
    engineering=200_000,
    operations=80_000,
    maintenance=60_000,
    training=20_000,
    incidents=30_000,
    migration=40_000,
)

print(tco)
```

The model is conceptual. Real TCO should use measurable assumptions.

---

# 45. Hands-On Exercises

For every exercise use:

```text
Scenario
Requirements
Options
Decision criteria
Decision
Trade-off accepted
When alternative wins
Failure implications
Cost implications
Future evolution
```

## Exercise 1 — Batch vs Streaming

Daily revenue report, 24-hour freshness.

## Exercise 2 — Batch vs Micro-Batch

Operations dashboard, 10-minute freshness.

## Exercise 3 — Micro-Batch vs Streaming

Fraud alerts, 30-second freshness.

## Exercise 4 — Warehouse vs Lakehouse

BI-first company adding ML workloads.

## Exercise 5 — Kafka vs Queue

Customer event fan-out vs background task processing.

## Exercise 6 — Spark vs DuckDB

20 GB local transformation vs 20 TB distributed join.

## Exercise 7 — Spark vs Flink

Nightly aggregation vs stateful event processing.

## Exercise 8 — Full vs CDC

Small reference table vs mutable transactional orders.

## Exercise 9 — Managed Connector vs Custom

Standard SaaS source vs proprietary API with unusual authentication.

## Exercise 10 — Normalized vs Dimensional

Transactional customer system vs executive analytics.

## Exercise 11 — Dimensional vs Wide

Reusable enterprise semantic model vs one dashboard's fixed workload.

## Exercise 12 — Idempotency vs Stronger Transactions

Retryable analytical writes vs atomic financial transfer.

## Exercise 13 — Direct Query vs Pre-Aggregation

Ad-hoc analyst workload vs repeated KPI dashboard.

## Exercise 14 — Cache vs Specialized Store

Hot API lookup vs persistent vector retrieval.

## Exercise 15 — Managed vs Self-Hosted

Small team vs specialized high-control platform team.

---

# 46. Break/Fix Trade-Off Scenarios

## Scenario 1 — "Kafka is always better."

**Why wrong:** Tool choice is detached from workload.

**Better criteria:** Replay, consumer model, throughput, task dispatch, operations.

**Decision:** Use Kafka-style streaming only when event-log requirements justify it.

---

## Scenario 2 — Streaming for a daily report

**Why wrong:** Freshness does not justify complexity.

**Better decision:** Batch unless another requirement demands continuous processing.

---

## Scenario 3 — Spark for a 5 GB local workload

**Why wrong:** Distributed infrastructure may cost more than the workload requires.

**Better decision:** Evaluate DuckDB/Polars first.

---

## Scenario 4 — Specialized store without an access pattern

**Why wrong:** Technology is solving no demonstrated constraint.

**Better decision:** Define query/latency/access requirements first.

---

## Scenario 5 — Team preference decides architecture

**Why wrong:** Familiarity is one criterion, not the only criterion.

**Better decision:** Include team expertise alongside requirements, cost, reliability, and future operations.

---

## Scenario 6 — Pros/cons with no decision

**Why wrong:** The interviewer needs architectural judgment.

**Better decision:**

```text
Given X, choose A because Y,
accepting Z.
```

---

## Scenario 7 — Cost ignored

**Why wrong:** A technically excellent system can be economically infeasible.

**Better decision:** Include infrastructure, engineering, operations, and query/serving cost.

---

## Scenario 8 — Operational burden ignored

**Why wrong:** The architecture has hidden ownership cost.

**Better decision:** Ask who patches, upgrades, scales, monitors, and responds to incidents.

---

## Scenario 9 — Five engines for five workloads

**Why wrong:** Specialization may create more organizational cost than performance value.

**Better decision:** Standardize where workload fit is adequate; specialize only where the gain justifies complexity.

---

## Scenario 10 — Exactly-once selected automatically

**Why wrong:** Stronger guarantees may be unnecessary.

**Better decision:** Determine the required business guarantee and evaluate idempotency first.

---

# 47. Realistic System-Design Applications

| Case | Dominant trade-offs |
|---|---|
| Product analytics | Cost vs flexibility |
| Clickstream | Latency vs complexity |
| CDC | Correctness vs operational complexity |
| ML features | Freshness vs consistency |
| Log analytics | Cost vs query performance |
| Ad attribution | Correctness vs latency |
| IoT | Scale vs cost |
| GDPR | Governance vs operational complexity |
| RAG | Freshness vs retrieval/index cost |
| Financial reporting | Correctness/auditability vs latency |

For each case, ask:

```text
What are the 2–3 most important trade-offs?
Why do they dominate?
What would you choose?
What trade-off are you accepting?
When would the alternative win?
```

---

# 48. Senior-Level Trade-Off Thinking

### Junior

> "Spark is scalable."

### Senior

> "Given the dataset size and distributed transformation requirements, Spark is reasonable. The trade-off is cluster and shuffle overhead, which may be unnecessary for smaller workloads."

### Junior

> "Kafka is reliable."

### Senior

> "Kafka-style event streaming is attractive when durable replayable events and independent consumers matter. It introduces partition and operational complexity that would not be justified for simple task dispatch."

### Senior reasoning includes

- Requirement
- Estimate
- Decision criteria
- Trade-off
- Failure behavior
- Cost
- Operational ownership
- Future evolution

---

# 49. Staff-Level Trade-Off Thinking

Staff reasoning expands the boundary.

Consider:

- Multiple teams
- Shared infrastructure
- Platform standards
- Cost allocation
- Governance
- Vendor strategy
- Migration cost
- Skills
- Long-term maintainability
- Platform reuse

Example:

> "Engine X may perform better for one workload, but standardizing on Engine Y across six teams could reduce the total organizational cost of operations, training, observability, and hiring. I would choose X only if the performance difference materially affects the business requirement."

That is staff-level reasoning because the optimization target is the **system and organization**, not one benchmark.

---

# 50. Trade-Offs Change Over Time

A good decision today may become a poor decision at 10× scale.

```text
Today:
DuckDB

At 10×:
Distributed engine
```

```text
Today:
Direct queries

At high QPS:
Pre-aggregation/cache
```

```text
Today:
One pipeline

At organizational scale:
Platform standardization
```

Do not migrate because a technology is fashionable. Migrate because a requirement, bottleneck, cost curve, or operational constraint changed.

---

# 51. Changed-Requirement Scenarios

## Freshness: 24 hours → 30 seconds

Initial:

```text
Batch
```

New:

```text
Streaming or a suitable low-latency architecture
```

Reason: freshness became the dominant constraint.

---

## Volume: 1× → 10×

Re-evaluate:

- Compute
- Storage
- Network
- Metadata
- Partitioning
- Serving
- Cost

---

## Budget: normal → 50% reduction

Re-evaluate:

- Processing frequency
- Retention
- Serving
- Precomputation
- Managed/self-hosted choices
- Query patterns

Do not simply reduce compute until the SLA fails.

---

## Availability: normal → 99.99%

Re-evaluate:

- Redundancy
- Failure domains
- Recovery
- Deployment strategy
- Operational procedures

---

## Retention: 1 year → 7 years

Re-evaluate:

- Storage lifecycle
- Compression
- Archival
- Governance
- Retrieval requirements
- Cost

---

## New global regions

Re-evaluate:

- Data residency
- Network
- Replication
- Latency
- Disaster recovery
- Governance

---

## New sensitive PII

Re-evaluate:

- Access controls
- Minimization
- Encryption
- Retention
- Deletion
- Lineage

---

## New ML consumer

Re-evaluate:

- Data grain
- Historical correctness
- Point-in-time semantics
- Serving latency
- Feature contracts

---

# 52. Trade-Offs and Failure Modes

A trade-off is incomplete if failure behavior is ignored.

```text
Streaming
→ low latency
→ more state
→ more operational complexity
→ more state/recovery failure modes to monitor
```

For each major decision ask:

```text
What new failure mode does this option introduce?
How will we detect it?
How will we recover?
```

Examples:

| Choice | New concern |
|---|---|
| Streaming | Lag/state/replay |
| CDC | Ordering/deletes/schema |
| Pre-aggregation | Refresh correctness |
| Cache | Staleness/invalidation |
| Wide table | Duplication/update drift |
| Multiple engines | Cross-platform operations |
| Self-hosting | Patching/capacity/on-call |

---

# 53. Trade-Offs and Observability

Architecture choices determine what you must monitor.

## Streaming

Monitor:

- Lag
- Throughput
- Processing latency
- State size
- Checkpoint/recovery health

## Batch

Monitor:

- Runtime
- Freshness
- Row counts
- Failure rate
- Backlog

## Cache

Monitor:

- Hit rate
- Miss rate
- Staleness
- Evictions
- Backend load

Observability is therefore part of the trade-off, not an afterthought.

---

# 54. Trade-Offs and Data Quality

Architecture choices create different correctness risks.

```text
Streaming
→ late/out-of-order data

CDC
→ ordering/deletes/schema evolution

Pre-aggregation
→ refresh/reconciliation

Cache
→ staleness

Wide tables
→ duplication/update semantics

Multiple engines
→ semantic differences between implementations
```

Always ask:

> "What new way can this architecture produce incorrect data?"

---

# 55. Trade-Offs and Security/Privacy

Adding more systems can increase flexibility while expanding the security surface.

Example:

```text
Replicate sensitive data into more platforms
→
more consumer flexibility
+
more access-control, retention, lineage, and deletion obligations
```

Consider:

- Data exposure
- Access control
- Encryption
- Network boundaries
- PII replication
- Retention
- Deletion
- Auditability

A performance optimization that replicates PII into another system is not merely a performance decision.

---

# 56. Rapid-Fire Interview Questions

Use a 30–60 second answer.

1. Batch or streaming?
2. Batch or micro-batch?
3. ETL or ELT?
4. Lake or warehouse?
5. Lakehouse or warehouse?
6. Row or columnar?
7. Full load or incremental?
8. Incremental or CDC?
9. Pull or push?
10. Managed connector or custom?
11. DuckDB or Spark?
12. Spark or Flink?
13. Spark or warehouse SQL?
14. Kafka or queue?
15. Kafka or managed stream?
16. Normalized or dimensional?
17. Dimensional or wide?
18. At-least-once or exactly-once?
19. Idempotency or transaction?
20. Direct query or pre-aggregation?
21. Pre-aggregation or cache?
22. Cache or specialized store?
23. Managed or self-hosted?
24. Build or buy?
25. One engine or several?
26. Lower cost or lower latency?
27. Faster delivery or customization?
28. Shared platform or team-owned pipelines?
29. Portability or deep platform integration?
30. Replayability or minimum storage?

---

# 57. One-Minute Drills

## Drill 1

**Prompt:** Batch or streaming for daily reporting?

**Requirements:** Daily freshness.

**Expected decision:** Batch.

**30-second answer:** Batch is sufficient because the freshness requirement does not justify continuous processing.

**60-second answer:** Batch is the default because daily freshness is satisfied with lower operational complexity and likely lower cost. I would revisit streaming only if another consumer needs near-real-time data or if the business value of lower latency changes.

**Common mistake:** Choosing streaming because it sounds more scalable.

---

## Drill 2

**Prompt:** Kafka or queue?

**Requirements:** Multiple independent consumers and replay.

**Expected decision:** Event-log approach.

**Common mistake:** Selecting a queue because both move messages.

---

## Drill 3

**Prompt:** Spark or DuckDB?

**Requirements:** 10 GB, local workflow.

**Expected decision:** DuckDB/Polars is a strong first candidate.

**Common mistake:** Introducing distributed compute without need.

---

## Drill 4

**Prompt:** Warehouse or lakehouse?

**Requirements:** BI plus ML and governed analytical tables.

**Expected decision:** Lakehouse may be attractive.

**Common mistake:** Choosing based on product branding.

---

## Drill 5

**Prompt:** Direct query or pre-aggregation?

**Requirements:** Hundreds of thousands of repeated KPI queries.

**Expected decision:** Pre-aggregation is a strong candidate.

**Common mistake:** Recomputing the same expensive aggregation for every request.

---

## Drill 6

**Prompt:** Exactly-once or idempotency?

**Requirements:** Retryable analytical upserts.

**Expected decision:** Idempotency may be sufficient.

**Common mistake:** Paying complexity for a stronger guarantee than required.

---

## Drill 7

**Prompt:** Managed or self-hosted?

**Requirements:** Small team, no special infrastructure requirement.

**Expected decision:** Managed is likely preferable.

**Common mistake:** Ignoring on-call cost.

---

## Drill 8

**Prompt:** One engine or several?

**Requirements:** Five workloads but four fit one engine adequately.

**Expected decision:** Standardize unless the fifth workload's requirements materially justify another engine.

**Common mistake:** One engine per workload.

---

## Drill 9

**Prompt:** Full load or CDC?

**Requirements:** Small reference table.

**Expected decision:** Full load may be simpler.

**Common mistake:** Adding CDC because it is technically sophisticated.

---

## Drill 10

**Prompt:** Managed connector or custom?

**Requirements:** Standard source with ordinary schema behavior.

**Expected decision:** Managed connector.

**Common mistake:** Building commodity infrastructure.

---

# 58. Interviewer Follow-Up Drills

| Follow-up | What it tests |
|---|---|
| Why? | Decision clarity |
| What if traffic is 10×? | Scalability |
| What if budget is cut in half? | Cost |
| What if freshness changes from one hour to one minute? | Requirement sensitivity |
| What if the team cannot operate the technology? | Organizational fit |
| What if the vendor raises pricing? | Lock-in |
| What if replay is required? | Durability/recovery |
| What if data contains PII? | Security/privacy |
| What if consumers need different SLAs? | Serving/platform boundaries |
| What if the source starts producing deletes? | Data semantics |
| What if the system must support a second region? | Evolution |
| What if the job must be backfilled? | Recoverability |
| What if data arrives late? | Temporal correctness |
| What if the serving QPS grows 100×? | Serving scalability |
| What if the team doubles? | Organizational scaling |

---

# 59. Decision Record Template

```text
## Decision

### Requirement
...

### Options
A:
B:

### Decision Criteria
...

### Chosen Option
...

### Why
...

### Trade-offs Accepted
...

### Risks
...

### Mitigations
...

### When I Would Choose the Alternative
...

### Cost Implications
...

### Failure Implications
...

### Future Evolution
...
```

---

# 60. Master Trade-Off Matrix

| Category | Option A | Option B | Main criteria | Typical winner when | Main trade-off |
|---|---|---|---|---|---|
| Processing | Batch | Streaming | Freshness | Seconds matter | Complexity |
| Processing | Batch | Micro-batch | Freshness | Minutes matter | More execution overhead |
| Transformation | ETL | ELT | Compute location/raw retention | Analytical target is strong | Raw-data governance |
| Storage | Warehouse | Lake | Analytics vs raw flexibility | Structured BI dominates | Flexibility |
| Storage | Lake | Lakehouse | Table semantics | Governed analytical tables matter | Platform complexity |
| Storage | Row | Columnar | Access pattern | Large analytical scans | Point-access fit |
| Ingestion | Pull | Push | Latency/control | Event-driven freshness | Coupling/backpressure |
| Ingestion | Full | Incremental | Volume | Full scans expensive | Change correctness |
| Ingestion | Incremental | CDC | Deletes/updates | Transaction changes matter | Complexity |
| Engines | DuckDB | Spark | Scale | One node is sufficient | Distributed capability |
| Engines | Spark | Flink | Execution model | Streaming state matters | Specialized operations |
| Engines | Spark | Warehouse SQL | Workload | SQL transformations fit target | Specialized compute |
| Messaging | Kafka | Queue | Event log vs task | Replay/fan-out | Operational complexity |
| Messaging | Managed stream | Kafka | Operations/control | Managed integration matters | Lock-in |
| Modelling | Normalized | Dimensional | Workload | BI dominates | Duplication |
| Modelling | Dimensional | Wide | Reuse vs convenience | Fixed consumer wins | Duplication |
| Correctness | Idempotency | Transactions | Guarantee | Repeatable writes suffice | Atomicity |
| Serving | Direct | Pre-aggregate | QPS/latency | Repeated queries dominate | Refresh complexity |
| Serving | Cache | Specialized store | Access pattern | Persistent specialized access matters | Operational surface |
| Platform | Managed | Self-hosted | Operations/control | Small team | Vendor dependence |
| Platform | Build | Buy | Differentiation/TCO | Commodity capability exists | Less customization |
| Platform | One engine | Several | Standardization | Most workloads fit | Specialization |
| Economics | Low cost | Low latency | Business value | Freshness is critical | Spend |
| Organization | Fast delivery | Customization | Time/uniqueness | Standard solution fits | Control |
| Governance | Broad access | Strong controls | Data sensitivity | PII/compliance dominates | Convenience |
| Portability | Open | Deep integration | Migration probability | Platform leverage dominates | Lock-in |

---

# 61. "What Would You Choose?"

## 1. 10 GB/day, 24-hour freshness

Prefer a simple batch architecture unless another requirement changes the answer.

## 2. 10 TB/day, 5-minute freshness

Evaluate micro-batch and streaming; choose based on state/event semantics and business value.

## 3. 100 TB/day, sub-minute freshness

A distributed streaming architecture becomes much more justified.

## 4. 20 GB local transformation

Evaluate DuckDB/Polars before Spark.

## 5. 20 TB distributed join

Distributed processing becomes much more justified.

## 6. Daily financial close

Favor correctness, reconciliation, auditability, and deterministic recovery over minimum latency.

## 7. Millions of repeated dashboard queries

Consider pre-aggregation or caching.

## 8. Ad-hoc analyst queries

Direct analytical querying may be preferable to rigid precomputation.

## 9. Background task distribution

A queue may fit better than an event-log platform.

## 10. Event replay with many consumers

A durable event-log approach becomes more attractive.

## 11. Small team, mature managed service

Managed is often attractive.

## 12. Highly specialized differentiating capability

Build may be justified.

## 13. Five workloads, one adequate engine

Standardize unless specialization produces material value.

## 14. Five workloads with fundamentally different execution semantics

Multiple engines may be justified.

## 15. Sensitive PII across multiple consumers

Minimize replication and strengthen governance.

## 16. Seven-year retention

Revisit storage lifecycle and archival economics.

## 17. Global deployment

Consider residency, network, replication, and recovery boundaries.

## 18. 50% budget reduction

Identify the largest cost drivers before cutting arbitrary capacity.

## 19. Freshness changes from one hour to one minute

Re-evaluate batch, micro-batch, and streaming.

## 20. Vendor price increases

Evaluate actual migration cost before deciding that lock-in must be eliminated.

---

# 62. Common Mistakes

## 1. "It depends" without criteria

**Why it happens:** Fear of committing.

**Why weak:** Avoids architectural judgment.

**Better:** State 2–3 criteria and choose.

**Example:**

```text
It depends on freshness, replay, and consumer count.
Given replay + multiple consumers, choose the event-log approach.
```

---

## 2. Pros/cons without a decision

**Why weak:** The interviewer needs a recommendation.

**Better:**

```text
A wins because X.
We accept Y.
B would win if Z changes.
```

---

## 3. Technology preference

**Why weak:** Tool familiarity replaces reasoning.

**Better:** Requirement → criteria → choice.

---

## 4. Popularity-based selection

**Why weak:** Popular technologies still have operating costs.

**Better:** Evaluate fit.

---

## 5. Ignoring cost

**Why weak:** Production systems have budgets.

**Better:** Estimate major cost drivers.

---

## 6. Ignoring complexity

**Why weak:** Complexity becomes operational debt.

**Better:** Ask what new responsibilities the choice creates.

---

## 7. Ignoring team expertise

**Why weak:** An unoperable system is not production-ready.

**Better:** Include skills and hiring/on-call implications.

---

## 8. Ignoring failure modes

**Why weak:** The happy path is only half the architecture.

**Better:** Explain detection and recovery.

---

## 9. Ignoring future growth

**Why weak:** Today's optimal architecture can become tomorrow's bottleneck.

**Better:** Identify 10× consequences.

---

## 10. Overengineering

**Why weak:** Complexity has cost.

**Better:** Add capability only when requirements justify it.

---

## 11. Underengineering

**Why weak:** Simplification can violate reliability/correctness requirements.

**Better:** Protect hard requirements first.

---

## 12. Treating trade-offs as universal truths

**Why weak:** Architecture is context-dependent.

**Better:** State the conditions under which the choice wins.

---

# 63. Final Interview Playbook

```text
1. State the requirement.
2. Identify the actual architectural decision.
3. Name 2–3 realistic options.
4. Identify the deciding criteria.
5. Compare only the important dimensions.
6. Choose one.
7. Explain why.
8. State the trade-off.
9. Explain when the alternative wins.
10. Connect the decision to cost, reliability, operations, and evolution.
```

---

# 64. Mental Models

### Mental Model 1

> **Requirements choose the trade-off.**

### Mental Model 2

> **There is no universally best technology.**

### Mental Model 3

> **Optimize for the workload, not the tool.**

### Mental Model 4

> **Complexity is a cost.**

### Mental Model 5

> **A trade-off is useful only when it leads to a decision.**

### Mental Model 6

> **Every architecture choice creates operational responsibility.**

### Mental Model 7

> **Today's optimization may become tomorrow's bottleneck.**

---

# 65. Final Knowledge Checklist

```text
[ ] Explain what a trade-off is
[ ] Distinguish trade-offs from pros/cons
[ ] Identify decision criteria
[ ] Choose between batch and streaming
[ ] Choose between batch and micro-batch
[ ] Explain ETL vs ELT
[ ] Compare warehouse/lake/lakehouse
[ ] Compare row/columnar
[ ] Explain table-format trade-offs
[ ] Compare pull/push
[ ] Compare full/incremental/CDC
[ ] Compare managed/custom ingestion
[ ] Compare DuckDB/Polars/Spark/Flink/warehouse SQL
[ ] Compare Kafka/managed streams/queues
[ ] Compare normalized/dimensional/wide
[ ] Explain at-least-once/idempotency/exactly-once
[ ] Explain deduplication trade-offs
[ ] Compare direct query/pre-aggregation/cache/specialized store
[ ] Compare managed/self-hosted
[ ] Explain build vs buy
[ ] Explain one engine vs several
[ ] Explain cost/freshness/complexity
[ ] Explain team-skill trade-offs
[ ] Explain operational burden
[ ] Explain vendor lock-in
[ ] Explain time-to-market
[ ] Perform a one-minute trade-off answer
[ ] Handle interviewer follow-ups
[ ] Re-evaluate decisions when requirements change
[ ] Explain senior-level trade-offs
[ ] Explain staff-level organizational trade-offs
```

---

# 66. Roadmap Checkpoint

The learner must be able to:

1. Explain the main trade-offs across processing, storage, engines, ingestion, correctness, and serving.
2. Tie every choice back to stated requirements.
3. Make an explicit decision rather than listing alternatives.
4. Explain the accepted trade-off.
5. State when the alternative would win.

### Checkpoint exercise

Given:

```text
Requirement:
Sub-minute freshness
100K events/sec
Multiple independent consumers
Replay required
Small platform team
```

Answer:

```text
Options:
Decision criteria:
Choice:
Why:
Trade-off:
Operational mitigation:
Alternative:
When alternative wins:
```

A passing answer must consider both technical and organizational constraints.

---

# 67. Final Assessment

## Part A — Basic — 10 Questions

1. What is a trade-off?
2. Why are pros/cons insufficient?
3. What determines decision criteria?
4. When is batch preferable?
5. When is streaming preferable?
6. What is ETL?
7. What is ELT?
8. What is a data lake?
9. What is idempotency?
10. Why does cost matter?

For each answer, require an explicit example.

## Part B — Intermediate — 15 Questions

1. Batch vs micro-batch for a 10-minute SLA.
2. Incremental vs CDC for mutable data.
3. Pull vs push for an external API.
4. Managed connector vs custom ingestion.
5. DuckDB/Polars vs Spark.
6. Spark vs Flink.
7. Spark vs warehouse SQL.
8. Kafka vs queue.
9. Normalized vs dimensional.
10. Dimensional vs wide.
11. At-least-once + idempotency.
12. Direct query vs pre-aggregation.
13. Cache vs specialized store.
14. Managed vs self-hosted.
15. One engine vs several.

For each:

```text
Requirement
→
Criteria
→
Choice
→
Trade-off
```

## Part C — Advanced — 15 Questions

1. Cost vs freshness.
2. Build vs buy.
3. Vendor lock-in.
4. Replayability vs storage cost.
5. Streaming failure modes.
6. CDC correctness.
7. Serving at high QPS.
8. 10× scale.
9. Multi-region.
10. PII replication.
11. Governance vs convenience.
12. Platform standardization.
13. Multiple consumers with different SLAs.
14. Specialized engine vs standard platform.
15. Changing requirements during an interview.

## Part D — Senior/Staff — 10 Questions

1. Standardization vs specialization across six teams.
2. Managed platform vs self-hosted platform strategy.
3. Vendor lock-in versus productivity.
4. One engine versus multiple organizational skill surfaces.
5. Central platform versus domain ownership.
6. Cost allocation across shared infrastructure.
7. Migration cost versus present-day productivity.
8. How team size changes architecture choices.
9. How to justify complexity to leadership.
10. How to defend a decision while remaining willing to change it.

## Part E — Rapid-Fire Interview — 20 Questions

Answer each in 30–60 seconds:

1. Batch or streaming?
2. Batch or micro-batch?
3. ETL or ELT?
4. Lake or warehouse?
5. Lakehouse or warehouse?
6. Row or columnar?
7. Full or incremental?
8. Incremental or CDC?
9. Pull or push?
10. Managed or custom?
11. DuckDB or Spark?
12. Spark or Flink?
13. Spark or warehouse SQL?
14. Kafka or queue?
15. Normalized or dimensional?
16. Idempotency or exactly-once?
17. Direct query or pre-aggregation?
18. Cache or specialized store?
19. Managed or self-hosted?
20. One engine or several?

## Part F — Full System-Design Trade-Off Exercises

Complete at least five:

1. Batch analytics platform
2. Real-time clickstream
3. CDC lakehouse
4. ML feature platform
5. RAG/vector data platform

Every final scenario must contain:

```text
Requirements
↓
Options
↓
Decision criteria
↓
Trade-off analysis
↓
Decision
↓
Accepted trade-offs
↓
Alternative
↓
Failure implications
↓
Cost implications
↓
Future evolution
```

---

# 68. Completion Criteria

Do not consider this module complete until you can:

1. Explain trade-offs clearly.
2. Identify decision criteria.
3. Avoid generic "it depends."
4. Compare realistic alternatives.
5. Make explicit choices.
6. Defend choices.
7. Explain accepted trade-offs.
8. Explain when alternatives win.
9. Connect choices to requirements.
10. Connect choices to estimates.
11. Connect choices to cost.
12. Connect choices to operations.
13. Connect choices to failure handling.
14. Connect choices to future evolution.
15. Explain batch vs streaming.
16. Explain ETL vs ELT.
17. Explain warehouse/lake/lakehouse.
18. Explain row vs columnar.
19. Explain full/incremental/CDC.
20. Explain managed/custom ingestion.
21. Explain engine trade-offs.
22. Explain messaging trade-offs.
23. Explain modelling trade-offs.
24. Explain correctness trade-offs.
25. Explain serving trade-offs.
26. Explain platform trade-offs.
27. Explain organizational trade-offs.
28. Give one-minute answers.
29. Handle changed requirements.
30. Demonstrate senior/staff reasoning.

---

# 69. Connection to Previous Topics

## Topic 02 — Requirements

```text
Requirements
→
Trade-off criteria
```

Topic 02 tells you what the system must achieve.

## Topic 03 — Estimation

```text
Requirements
+
Estimates
→
Trade-off boundaries
```

Scale can eliminate otherwise reasonable choices.

## Topic 04 — Reusable Framework

```text
Requirements
→
Estimates
→
Framework
→
Trade-offs
```

Topic 04 structures the design.

Topic 05 teaches you to **defend the choices inside that structure**.

---

# 70. Connection to Topic 06

Topic 06 teaches diagramming and communication.

Trade-offs should become visible in the architecture:

```text
Requirement
↓
Choice
↓
Component
↓
Trade-off
```

For example:

```text
5-minute freshness
↓
Micro-batch
↓
Frequent processing job
↓
Higher execution frequency
```

Do not use this topic to re-teach diagramming; use it to prepare the learner to communicate architectural decisions visually.

---

# 71. Connection to Phase C Design Cases

The trade-off catalogue becomes the decision engine for the nine Phase C cases.

| Case | Likely dominant trade-offs |
|---|---|
| Batch analytics | Cost vs flexibility/freshness |
| Real-time clickstream | Latency vs complexity |
| CDC replication | Correctness vs operational complexity |
| ML feature platform | Freshness vs consistency |
| Log/metrics analytics | Cost vs query performance |
| Ad attribution | Correctness vs latency |
| IoT telemetry | Scale vs cost |
| GDPR deletion | Governance vs operational complexity |
| RAG/vector platform | Freshness vs retrieval/index cost |

The exact decision must still come from the case requirements.

---

# 72. Production Thinking

A production architecture is not simply the architecture with the highest benchmark performance.

It balances:

```text
Correctness
+
Performance
+
Reliability
+
Cost
+
Operational complexity
+
Security
+
Team capability
+
Time to market
+
Future evolution
```

A useful final question is:

> "What responsibility does this choice create for the team?"

For example:

```text
Streaming
→ state/recovery/lag ownership

Self-hosting
→ upgrades/capacity/security ownership

Multiple engines
→ multiple skill/observability/deployment surfaces

Cache
→ invalidation/staleness ownership

CDC
→ ordering/schema/delete/replay ownership
```

That is production architecture thinking.

---

# 73. Final Operating Standard

When an interviewer asks:

> "Which technology would you use?"

Think:

```text
1. What does the system need?
2. What are the realistic options?
3. What criteria matter?
4. What is the dominant constraint?
5. Which option fits best?
6. What trade-off am I accepting?
7. What new failure/operational burden does it create?
8. When would I choose the alternative?
9. What changes at 10×?
```

The target competency is:

```text
Understand
→
Compare
→
Choose
→
Defend
→
Operate
→
Re-evaluate
```

Not:

```text
Remember tool
→
Name tool
→
Declare it best
```

---

# 74. Roadmap Coverage Audit

| Roadmap Requirement | Covered? | Where |
|---|---|---|
| Trade-off method | Yes | Sections 2–3 |
| Option A vs B | Yes | Sections 3, 34 |
| Decision criteria | Yes | Sections 4–5 |
| Batch vs micro-batch vs streaming | Yes | Sections 6–8 |
| ETL vs ELT | Yes | Sections 9–10 |
| Warehouse vs lake vs lakehouse | Yes | Sections 11–12 |
| Row vs columnar | Yes | Sections 13–14 |
| Table formats | Yes | Section 14 |
| Pull vs push | Yes | Section 15 |
| Full vs incremental vs CDC | Yes | Section 16 |
| Managed connectors vs custom | Yes | Section 17 |
| DuckDB/Polars vs Spark | Yes | Sections 18–19 |
| Spark vs Flink | Yes | Sections 18–19 |
| Warehouse SQL | Yes | Sections 18–19 |
| Kafka vs managed streams vs queues | Yes | Section 20 |
| Normalized vs dimensional vs wide | Yes | Section 21 |
| At-least-once + idempotency | Yes | Sections 22–23 |
| Transactional exactly-once | Yes | Sections 22–24 |
| Deduplication strategies | Yes | Section 23 |
| Direct queries | Yes | Section 25 |
| Pre-aggregation | Yes | Section 25 |
| Caches | Yes | Section 25 |
| Specialized stores | Yes | Section 25 |
| Managed vs self-hosted | Yes | Section 27 |
| Build vs buy | Yes | Section 28 |
| One engine vs several | Yes | Section 29 |
| Cost vs freshness vs complexity | Yes | Section 30 |
| Team skills | Yes | Section 31 |
| Operational load | Yes | Section 31 |
| Vendor lock-in | Yes | Section 31 |
| Time to market | Yes | Section 31 |
| Interview trade-off communication | Yes | Sections 35.1, 36, 56–58 |
| Hands-on exercises | Yes | Section 45 |
| One-minute drills | Yes | Section 57 |
| Common mistakes | Yes | Section 62 |
| Roadmap checkpoint | Yes | Section 66 |
| Production application | Yes | Sections 47, 72 |

---

# 75. Final Quality Verification

```text
[✓] Target filename is correct.
[✓] Scope is limited to Data Engineering architecture trade-offs.
[✓] Topic 04 is used as the structural prerequisite.
[✓] Topic 03 estimation is integrated.
[✓] Topic 06 communication is prepared but not duplicated.
[✓] Phase C application is explicit.
[✓] Batch / micro-batch / streaming covered.
[✓] ETL / ELT covered.
[✓] Warehouse / lake / lakehouse covered.
[✓] Row / columnar covered.
[✓] Table-format trade-offs covered.
[✓] Pull / push covered.
[✓] Full / incremental / CDC covered.
[✓] Managed / custom ingestion covered.
[✓] DuckDB / Polars / Spark / Flink / warehouse SQL covered.
[✓] Kafka / managed streams / queues covered.
[✓] Normalized / dimensional / wide covered.
[✓] At-least-once / idempotency / exactly-once covered.
[✓] Deduplication covered.
[✓] Direct query / pre-aggregation / cache / specialized store covered.
[✓] Managed / self-hosted covered.
[✓] Build / buy covered.
[✓] One engine / several covered.
[✓] Cost / freshness / complexity covered.
[✓] Team skills covered.
[✓] Operational load covered.
[✓] Vendor lock-in covered.
[✓] Time to market covered.
[✓] Failure implications covered.
[✓] Security/privacy implications covered.
[✓] 10× evolution covered.
[✓] Senior/staff reasoning covered.
[✓] Python decision examples included.
[✓] Hands-on exercises included.
[✓] Break/fix scenarios included.
[✓] Rapid-fire questions included.
[✓] One-minute drills included.
[✓] Final assessment included.
[✓] Completion criteria included.
[✓] Roadmap coverage audit included.
```

---

# 76. Final Principle

> **There is no universally best Data Engineering architecture. There is only an architecture that is better or worse for a particular set of requirements, constraints, risks, and organizational realities.**

The learner's final answer should therefore sound like:

```text
Given these requirements,
I would choose X over Y because A, B, and C.

The trade-off I am accepting is D.

This creates risks E and F, which I would mitigate with G.

If requirement H changed,
I would reconsider Y.

At 10× scale,
I would revisit assumptions I and J.
```

That is the system-design trade-off competency this module is designed to build.
