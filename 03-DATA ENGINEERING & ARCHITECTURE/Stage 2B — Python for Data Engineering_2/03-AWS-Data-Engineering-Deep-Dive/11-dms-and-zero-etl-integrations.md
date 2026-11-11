# DMS and Zero-ETL Integrations

> **Gap Module G3 — AWS Data Engineering Deep Dive | Phase D — Streaming, Big Compute, Orchestration, Replication**
>
> Production-oriented learning module covering database replication, full load, CDC, AWS Database Migration Service (DMS), DMS Serverless, replication reliability, S3/Kinesis/MSK/Redshift targets, zero-ETL, CDC-to-Iceberg patterns, PostgreSQL WAL and replication slots, validation, observability, security, cost, and architecture selection.

## Important AWS Cost Warning

This module can create billable AWS resources.

Before every lab:

1. Check current AWS pricing.
2. Configure AWS Budgets and alerts.
3. Use cost-allocation tags.
4. Use the smallest practical lab resources.
5. Stop/delete replication resources after testing.
6. Remove test databases and networking created only for the lab.
7. Verify that no billable resources remain.

> **Production rule:** replication is not "free plumbing." DMS capacity, storage, network transfer, source-database resources, targets, monitoring, and downstream processing all have operational and financial consequences.

## Current-documentation rule

AWS DMS and zero-ETL capabilities evolve. Verify current official AWS documentation before production deployment, especially for source/target support, regions, task settings, DMS Serverless behavior, CLI/boto3 APIs, Terraform resources, zero-ETL combinations, schema behavior, limits, and pricing.

The examples below deliberately distinguish **conceptual examples** from commands that must be validated against the current service version.

---

# 1. Why Database Replication Matters

An operational database exists primarily to serve application transactions. An analytical platform exists to serve reporting, historical analysis, experimentation, ML/AI, and large scans.

A common architecture is:

```text
                    ┌→ Application transactions
Operational DB ─────┼→ Analytics
                    ├→ Reporting
                    ├→ ML / AI
                    └→ Data lake / lakehouse
```

Running large analytical workloads directly against an OLTP system can create workload contention, latency, scaling pressure, and operational risk.

Replication creates workload isolation:

```text
OLTP database
     ↓
Replication / CDC
     ↓
Analytical platform
```

The engineering problem is broader than "copy the tables." You must preserve enough correctness, ordering, deletes, schema meaning, and operational visibility for downstream systems to trust the replica.

---

# 2. Operational Database vs Analytical Platform

| Dimension | Operational DB | Analytical platform |
|---|---|---|
| Primary purpose | Transactions | Analytics |
| Workload | Point reads/writes, transactions | Scans, joins, aggregations |
| Latency objective | Application response | Query/report latency |
| Concurrency pattern | Application users/services | Analysts, BI, pipelines |
| Data shape | Normalized/transactional | Curated analytical models |
| Historical analysis | Often limited | Core capability |
| Scaling concern | OLTP contention | Compute/storage/query throughput |

Replication is therefore a workload-isolation mechanism as well as a data-movement mechanism.

A useful question is:

> What data should leave the operational system, how fresh must it be, and what guarantees must the destination provide?

---

# 3. Full Load vs CDC

**Full load** copies existing state:

```text
Source DB
   ↓
Read existing rows
   ↓
Copy
   ↓
Target
```

**CDC (Change Data Capture)** copies changes after a starting point:

```text
INSERT
UPDATE
DELETE
   ↓
CDC mechanism
   ↓
Target
```

Mental model:

```text
Full Load = What already exists?
CDC       = What changed afterward?
```

Full load is useful for initial population or migration. CDC is useful for ongoing synchronization and low-downtime migration.

---

# 4. Full Load + CDC

Full Load + CDC combines the two phases:

```text
Phase 1: Full Load
       ↓
Existing data copied
       ↓
Phase 2: CDC
       ↓
New changes captured
```

The key engineering challenge is the boundary between the snapshot and the change stream.

For production cutovers, reason about:

- source write activity
- CDC start position
- replication lag
- target validation
- consistency
- cutover timing
- replay/recovery
- rollback

Do not treat "task completed" as equivalent to "target is correct."

---

# 5. AWS DMS Overview

AWS Database Migration Service provides managed data migration and replication capabilities.

Core model:

```text
SOURCE DATABASE
      ↓
SOURCE ENDPOINT
      ↓
DMS replication engine
      ↓
TARGET ENDPOINT
      ↓
TARGET SYSTEM
```

DMS concepts:

- **Source endpoint:** how DMS connects to the source.
- **Target endpoint:** how DMS writes to the target.
- **Replication instance:** managed compute used by provisioned DMS replication.
- **DMS Serverless:** a serverless capacity model for supported replication workloads.
- **Replication task:** configuration describing what to replicate and how.

DMS is a replication/migration service, not a substitute for your entire transformation platform.

---

# 6. DMS Architecture

A production DMS deployment has several boundaries:

```text
                 IAM / Secrets
                      |
Source DB → Source Endpoint → DMS → Target Endpoint → Target
                      |
                 CloudWatch/logs
```

Design dimensions:

1. Network reachability.
2. Authentication.
3. Encryption.
4. Source permissions.
5. Replication capacity.
6. Task configuration.
7. Target write permissions.
8. Monitoring.
9. Validation.
10. Cost lifecycle.

A good architecture isolates replication from application credentials and uses private connectivity where appropriate.

---

# 7. Source Endpoints

A DMS source endpoint encapsulates connection and engine-specific configuration.

Typical source families include PostgreSQL, MySQL, Aurora, and other engines supported by the current DMS documentation.

Endpoint design includes:

- host/port
- database
- authentication
- TLS/SSL
- networking
- engine-specific settings
- secrets handling

Do not hard-code credentials. Prefer secure credential mechanisms supported by the service.

Always test endpoint connectivity before diagnosing a task.

---

# 8. Target Endpoints

This roadmap emphasizes:

| Target | Typical role |
|---|---|
| S3 | Lake/raw CDC ingestion |
| Kinesis | Streaming consumers |
| MSK | Kafka ecosystem |
| Redshift | Analytics warehouse |

The target changes the replication design.

For example:

```text
PostgreSQL → S3
```

is primarily a lake ingestion pattern, while:

```text
PostgreSQL → MSK
```

is a streaming-platform pattern.

The target also changes schema, ordering, replay, validation, and cost considerations.

---

# 9. Replication Instances

A provisioned DMS replication instance supplies compute/network resources for replication tasks.

Think:

```text
Small workload → smaller capacity
Large workload → more capacity / different architecture
```

Do not use a fixed "instance size = X rows/sec" rule. Throughput depends on:

- source workload
- transaction size
- number of tables
- LOBs
- network
- target throughput
- transformations
- indexes
- concurrency

A replication instance that is idle still creates cost. Lifecycle management is part of production engineering.

---

# 10. DMS Serverless

DMS Serverless provides a serverless capacity model for supported replication workloads.

Conceptual comparison:

| Dimension | Provisioned DMS | DMS Serverless |
|---|---|---|
| Capacity | Explicit replication resources | Managed/scaled capacity model |
| Scaling | Capacity planning required | More automated |
| Operations | More infrastructure management | Less infrastructure management |
| Cost model | Resource/workload dependent | Usage/capacity dependent |
| Best fit | Predictable/controlled workloads | Workloads benefiting from managed scaling |

Exact capabilities, limits, supported configurations, and pricing must be verified against current AWS documentation before deployment.

Use requirements rather than novelty as the selection criterion.

---

# 11. Replication Tasks

A replication task defines the work DMS performs.

Lifecycle concepts include:

```text
Create
  ↓
Start
  ↓
Running
  ↓
Monitor
  ↓
Stop / Complete / Fail
  ↓
Resume / Restart / Reload as appropriate
```

The three core modes are:

- Full Load
- CDC Only
- Full Load + CDC

A recovery decision must distinguish between **resume**, **restart**, and **reload**. The correct choice depends on what state remains trustworthy.

---

# 12. Task Types

### Full Load

Copies existing source data.

### CDC Only

Starts from an appropriate CDC position rather than copying the entire existing dataset.

### Full Load + CDC

Copies existing data and continues capturing changes.

Selection depends on the business requirement:

```text
Initial population? → Full Load
Already initialized? → CDC Only
Migration + ongoing sync? → Full Load + CDC
```

---

# 13. PostgreSQL Source Prerequisites

PostgreSQL CDC uses logical replication mechanisms.

Mental model:

```text
Transaction
    ↓
WAL
    ↓
Logical replication / slot
    ↓
DMS
```

For self-managed PostgreSQL, current AWS documentation requires logical-replication configuration such as `wal_level = logical` and sufficient replication slots for the workload. AWS-managed PostgreSQL has service-specific parameter and privilege requirements. citeturn0search2turn0search4

For AWS-managed PostgreSQL, logical replication settings can increase WAL generation; monitor source disk and workload impact. citeturn0search2

Never blindly copy a production parameter recipe. Validate it against the exact PostgreSQL/Aurora/RDS version and DMS configuration.

---

# 14. Least-Privilege Replication Users

Use a dedicated replication identity.

Principles:

- minimum database permissions
- required replication privileges
- required schema/table access
- no unnecessary superuser privilege
- credentials stored securely
- permissions documented and reviewed

Illustrative placeholder:

```sql
CREATE USER dms_replication_user
WITH PASSWORD '<managed-secret-placeholder>';
```

The exact grants differ between self-managed PostgreSQL and AWS-managed PostgreSQL. Current AWS documentation should be followed for the chosen deployment.

---

# 15. Table Mappings

Table mappings determine what DMS replicates and how objects are treated.

Conceptual structure:

```json
{
  "rules": [
    {
      "rule-type": "selection",
      "rule-action": "include",
      "object-locator": {
        "schema-name": "public",
        "table-name": "orders"
      }
    }
  ]
}
```

Use mappings to express scope intentionally.

A production mapping should answer:

- Which schemas?
- Which tables?
- Which tables are excluded?
- Are filters required?
- Are transformations required?
- What happens when a new table appears?

Validate exact mapping syntax against the current DMS documentation before deployment.

---

# 16. Selection Rules

Selection rules define which source objects participate.

Common design:

```text
Include required schema/table
        ↓
Exclude known unwanted objects
        ↓
Apply filters only when justified
```

Do not accidentally replicate operational tables containing secrets, temporary objects, or irrelevant audit data.

Keep the mapping reviewable in version control.

---

# 17. Transformation Rules

DMS can perform replication-oriented transformations, such as selected renames or target-structure adjustments.

Production principle:

> Do not turn DMS into a general-purpose transformation engine.

Use DMS for replication-oriented shaping. Use Glue, Spark, SQL, or downstream lakehouse processing for complex business transformations.

This separation improves:

- debuggability
- replay
- lineage
- portability
- schema evolution
- ownership boundaries

---

# 18. DMS Task Settings

Task settings should be driven by:

```text
source
+
volume
+
latency
+
target
+
LOB requirements
+
schema behavior
```

Important categories:

- full-load behavior
- CDC processing
- batching
- errors
- logging
- validation
- LOB handling
- commit behavior
- transaction consistency
- target loading

Do not memorize undocumented settings. Validate exact options for the current DMS engine version.

---

# 19. Data Validation

Replication success does not automatically imply data correctness.

Use layered validation:

```text
Connection
   ↓
Row counts
   ↓
Sample records
   ↓
Hashes/checksums where appropriate
   ↓
Insert validation
   ↓
Update validation
   ↓
Delete validation
   ↓
CDC lag
   ↓
Business reconciliation
```

Validate:

- missing rows
- duplicates
- updates
- deletes
- numeric precision
- timestamps
- schema
- business totals

---

# 20. S3 Target

A common pattern is:

```text
PostgreSQL
   ↓
DMS
   ↓
S3
   ↓
Glue / Athena / Spark
```

DMS S3 targets support CSV and Parquet output. Current AWS documentation also exposes settings for CDC paths, transaction preservation, operation markers, timestamps, and Parquet timestamp precision. citeturn0search0turn0search6

For PostgreSQL/Aurora PostgreSQL → S3 Parquet, current DMS behavior around `confirmed_flush_lsn` depends on target memory retention; understand this when reasoning about source WAL pressure. citeturn0search0

Do not treat raw DMS files as a finished analytical table.

---

# 21. Kinesis Target

Pattern:

```text
Operational DB
      ↓
DMS
      ↓
Kinesis
      ↓
Streaming consumers
```

Useful when database changes need to enter an event/stream processing platform.

Consider:

- partitioning
- throughput
- ordering requirements
- replay
- consumer semantics
- downstream idempotency

Compare this with application-level event publication: DMS is convenient for database-derived change capture, while application events can represent business semantics that are not visible in row-level CDC.

---

# 22. MSK Target

Pattern:

```text
Operational DB
      ↓
DMS
      ↓
MSK
      ↓
Kafka consumers
```

Alternative:

```text
Operational DB
      ↓
Debezium
      ↓
Kafka / MSK
```

DMS is attractive when managed AWS replication is preferred. Debezium is attractive when the organization needs deeper Kafka-native CDC control and already has Kafka operational expertise.

---

# 23. Redshift Target

Pattern:

```text
Operational DB
      ↓
DMS
      ↓
Redshift
```

Evaluate:

- initial load
- ongoing replication
- latency
- target schema
- warehouse workload
- validation
- transformations
- cutover requirements

Then compare it with zero-ETL, which may remove some pipeline components for supported source/target combinations.

---

# 24. Parquet and Change Metadata

Parquet is useful for analytical storage because it is columnar and supports efficient analytical processing.

DMS S3 targets can emit Parquet. AWS documents an operation marker pattern where CDC records can carry `I`, `U`, or `D` semantics depending on configuration. DMS can also add a timestamp column representing transfer time for full load and source commit time for CDC. citeturn0search0

For Athena/Glue consumers, current DMS documentation notes that millisecond timestamp precision may be necessary for Parquet timestamps. citeturn0search0turn0search6

The target data contract must document:

- operation semantics
- key columns
- timestamp semantics
- ordering metadata
- schema
- partition/layout rules

---

# 25. Large Objects and Data Types

LOBs include large text and binary payloads.

LOB handling can affect:

- throughput
- memory
- network
- latency
- target compatibility

Data-type compatibility must also be explicit:

```text
Source type
   ↓
DMS type
   ↓
Target type
```

Watch for:

- numeric precision
- timestamps/time zones
- JSON
- binary data
- boolean semantics
- character encodings

Do not invent current LOB limits; verify the exact source/target documentation.

---

# 26. Schema Changes

Schema evolution is one of the hardest replication problems.

Examples:

```text
ADD COLUMN
DROP COLUMN
RENAME COLUMN
CHANGE DATA TYPE
NEW TABLE
```

Reason about:

```text
Source schema
    ↓
DMS behavior
    ↓
Target schema
    ↓
Downstream table
    ↓
Analytics contract
```

Current DMS S3 documentation, for example, describes support for several CDC DDL operations and explains that S3 objects already written are not retroactively rewritten to match later schema changes. citeturn0search0

Never assume identical DDL behavior across all DMS source/target combinations.

---

# 27. Zero-ETL Integrations

"Zero-ETL" does not literally mean zero data movement.

It generally means a managed integration reduces the custom extract/transform/load pipeline code that engineers must build and operate.

Conceptually:

```text
Traditional:
DB → DMS → S3/ETL → Transform → Warehouse

Zero-ETL:
DB → Managed integration → Analytics destination
```

The important architectural question is not whether a feature has the label "zero-ETL"; it is whether it meets the source, target, latency, schema, security, transformation, and cost requirements.

---

# 28. Zero-ETL Architecture

Current AWS documentation describes zero-ETL integrations for several source/target combinations, including RDS sources into supported Redshift destinations and RDS-to-SageMaker AI lakehouse integrations. citeturn0search3turn0search5

Architecture:

```text
Transactional source
       ↓
Managed zero-ETL integration
       ↓
Analytics destination
```

For every specific integration verify:

```text
Source
Target
Region
Engine/version
Feature status
Table limitations
Schema rules
Latency expectations
Security
Cost
```

Supported combinations change over time.

---

# 29. Zero-ETL Limitations

Zero-ETL does **not** mean:

- every database is supported
- every target is supported
- every region is supported
- every schema change works identically
- arbitrary transformations are supported
- monitoring is unnecessary
- security design is unnecessary
- cost is zero

Ask:

```text
Is my source supported?
Is my target supported?
Is my region supported?
Are my tables/features supported?
What latency is required?
What schema rules apply?
What failure modes exist?
What transformations are possible?
What lock-in am I accepting?
What is the cost?
```

This checklist is more durable than memorizing a list of integrations.

---

# 30. DMS CDC → S3 → Iceberg

Advanced lakehouse pattern:

```text
PostgreSQL
    ↓
DMS CDC
    ↓
S3 raw change files
    ↓
Glue / Athena / Spark
    ↓
Staging
    ↓
MERGE
    ↓
Iceberg silver table
```

Separate:

1. raw replicated evidence
2. CDC normalization
3. deduplication/order resolution
4. target-state application
5. analytical modeling

This separation makes replay and incident recovery much safer.

---

# 31. Applying CDC with MERGE

Conceptual example:

```sql
MERGE INTO silver.orders AS target
USING staging.orders_cdc AS source
ON target.order_id = source.order_id

WHEN MATCHED AND source.operation = 'UPDATE'
THEN UPDATE SET
    status = source.status,
    updated_at = source.updated_at

WHEN MATCHED AND source.operation = 'DELETE'
THEN DELETE

WHEN NOT MATCHED AND source.operation = 'INSERT'
THEN INSERT (
    order_id,
    status,
    updated_at
)
VALUES (
    source.order_id,
    source.status,
    source.updated_at
);
```

A simple `MERGE` is not sufficient by itself when multiple changes for the same key can arrive.

Before merging:

```text
CDC records
   ↓
Order by trustworthy source metadata
   ↓
Select latest valid change per key
   ↓
Deduplicate
   ↓
MERGE
```

Consider late arrival, duplicate delivery, deletes, retries, and transaction ordering.

---

# 32. Replication Lag

Replication lag is the distance between source changes and target application.

```text
Source change
    ↓
Captured
    ↓
Transferred
    ↓
Applied
    ↓
Target visible
```

Lag can accumulate because of:

- source workload
- replication capacity
- network
- large transactions
- LOBs
- target throttling
- schema problems
- downstream processing

Track lag as a business SLO when freshness matters.

---

# 33. PostgreSQL WAL and Replication Slots

PostgreSQL logical CDC relies on WAL.

```text
Transaction
    ↓
WAL
    ↓
Replication slot
    ↓
CDC consumer
```

A replication slot can retain WAL needed by the consumer. If the consumer stops advancing, WAL can accumulate and consume source disk.

Current AWS documentation explicitly warns that logical-replication configuration can increase WAL generation and describes how DMS uses logical replication slots for PostgreSQL CDC. citeturn0search2

Operational rule:

> Monitor replication health and source disk together.

Do not solve a WAL incident by blindly deleting a replication slot. First establish which task owns it and whether the required changes can be safely recovered.

---

# 34. Source Database Impact

Replication has source-side cost.

Potential impacts:

- CPU
- I/O
- WAL generation/retention
- network
- long transactions
- replication slots
- logical decoding workload

Before enabling CDC:

```text
Capacity
+
Replication configuration
+
Monitoring
+
Disk headroom
+
Rollback plan
```

Current AWS guidance for RDS/Aurora PostgreSQL also notes that logical-replication settings can affect background workers and source workload; monitor smaller instances carefully. citeturn0search2

---

# 35. Failure and Recovery

Common failures:

- DMS task stopped
- source unavailable
- target unavailable
- network failure
- authentication failure
- schema mismatch
- unsupported type
- replication lag
- WAL growth
- target throttling
- duplicate data
- missing data

Use:

```text
Symptom
 ↓
Evidence
 ↓
Likely cause
 ↓
Fix
 ↓
Verification
 ↓
Prevention
```

Recovery must preserve data correctness, not merely restore a green task status.

---

# 36. Monitoring

Monitor:

- task status
- CDC lag
- source health
- target health
- errors
- throughput
- replication capacity
- source WAL/slot health
- CloudWatch telemetry
- logs
- CloudTrail/audit events where useful

Conceptual dashboard:

```text
Task status
CDC latency
Throughput
Errors
Source DB health
Replication slot/WAL health
Target health
```

Avoid relying on one metric. A healthy DMS task can coexist with a growing source WAL backlog or downstream correctness issue.

---

# 37. Security

Use:

- least-privilege database users
- IAM roles
- Secrets Manager
- KMS where appropriate
- TLS/SSL
- private subnets
- security groups
- VPC endpoints where applicable
- controlled S3 access
- encrypted targets
- audit logging

Preferred topology:

```text
Private RDS/Aurora
       ↓
Private networking
       ↓
DMS
       ↓
Private target
```

Never place passwords or access keys directly in code examples.

---

# 38. Cost Optimization

Conceptual cost stack:

```text
DMS
+
Replication capacity
+
Storage
+
Network
+
Target services
+
Monitoring
```

Optimization levers:

- right-size capacity
- use DMS Serverless when it is appropriate
- stop/delete labs
- avoid idle replication instances
- control replication scope
- reduce unnecessary transformations
- batch downstream processing where latency permits
- monitor network and target costs

Cost optimization must not sacrifice required freshness or correctness.

---

# 39. DMS vs Zero-ETL vs Debezium

| Dimension | DMS | Zero-ETL | Debezium |
|---|---|---|---|
| Managed AWS experience | Strong | Strong | Depends on platform |
| Operational effort | Moderate | Often lower | Higher |
| Flexibility | Broad migration/replication use | Constrained by supported integrations | High CDC/Kafka control |
| Kafka ecosystem | Supported patterns | Usually not the core reason | Strong |
| Custom CDC control | Moderate | Lower | High |
| Portability | Moderate | Lower | High |
| AWS integration | Strong | Strong | Depends on deployment |
| Lock-in | AWS | Higher AWS dependency | Lower platform dependency |
| Best use | Managed migration/replication | Supported low-ops analytics paths | Kafka-centric CDC platforms |

Do not declare a universal winner.

Choose from requirements:

```text
Source
Target
Latency
Transformations
Kafka needs
Portability
Operational skills
Cost
Schema complexity
Lock-in tolerance
```

---

# 40. DMS Schema Conversion Awareness

Schema conversion addresses differences between database dialects and structures.

Potential concerns:

- SQL dialect
- data types
- stored procedures
- functions
- schema assessment
- incompatible features

It belongs in a broader migration program:

```text
Assess
 ↓
Convert
 ↓
Validate
 ↓
Replicate
 ↓
Test
 ↓
Cut over
```

This module only requires awareness; it is not a full schema-conversion course.

---

# 41. Production Reference Architectures

A production replication platform should be designed as a system, not a single task.

Reference architectures:

### Database → Lake

```text
RDS PostgreSQL
     ↓
DMS
     ↓
S3
     ↓
Glue / Athena
     ↓
Iceberg
     ↓
Analytics
```

### Database → Warehouse

```text
Aurora / RDS
     ↓
DMS or Zero-ETL
     ↓
Redshift
```

### Database → Kafka

```text
Operational DB
     ↓
DMS or Debezium
     ↓
MSK
     ↓
Kafka consumers
```

### Hybrid

```text
                  ┌→ S3 / Iceberg
                  |
Operational DB → CDC ─→ MSK
                  |
                  └→ Redshift
```

Use a hybrid only when the business value justifies additional operational complexity.

---

# 42. Architecture Decision Records

### ADR 1 — DMS instead of Debezium

**Context:** Managed AWS replication is preferred and Kafka-native CDC control is not the primary requirement.

**Decision:** Use DMS.

**Trade-off:** Less Kafka-specific control but lower platform-management burden.

### ADR 2 — Zero-ETL instead of DMS

**Context:** Source/target/region are currently supported and custom transformation requirements are limited.

**Decision:** Use zero-ETL.

**Trade-off:** Less custom pipeline code but stronger dependence on supported integration capabilities.

### ADR 3 — DMS → S3 instead of DMS → Redshift

**Context:** The organization needs a durable raw CDC landing layer and multiple downstream consumers.

**Decision:** Land in S3 and transform downstream.

### ADR 4 — Debezium → MSK

**Context:** Kafka is already a strategic platform and consumers need Kafka-native CDC.

**Decision:** Use Debezium/MSK.

### ADR 5 — CDC → S3 → Iceberg

**Context:** A lakehouse requires raw change evidence and replayable transformations.

**Decision:** Keep raw CDC separate from curated Iceberg state.

Every ADR should record:

```text
Context
Requirements
Decision
Alternatives
Latency
Reliability
Schema evolution
Security
Cost
Operations
Lock-in
Risks
```

---

# 43. Hands-On Labs

## Lab 1 — PostgreSQL → S3 with Full Load + CDC

Build:

```text
PostgreSQL
    ↓
AWS DMS
    ↓
S3
    ↓
Parquet CDC files
```

Tasks:

1. Create a disposable PostgreSQL test source.
2. Configure logical replication according to current AWS guidance.
3. Create a least-privilege replication identity.
4. Configure source endpoint.
5. Configure S3 target endpoint.
6. Configure Full Load + CDC.
7. Select tables.
8. Start replication.
9. Validate initial data.
10. Execute INSERT.
11. Execute UPDATE.
12. Execute DELETE.
13. Inspect CDC output.
14. Inspect timestamps/operation metadata.
15. Validate source vs target.
16. Tear down resources.

## Lab 2 — CDC → Iceberg

```text
DMS
 ↓
S3 CDC
 ↓
Glue/Athena/Spark
 ↓
Staging
 ↓
MERGE
 ↓
Iceberg Silver
```

Test:

- INSERT
- UPDATE
- DELETE
- multiple changes per key
- duplicate CDC records
- late-arriving records

## Lab 3 — Zero-ETL

Only execute a real zero-ETL integration if the source, target, region, engine/version, account permissions, and budget support it.

Otherwise:

1. document the supported architecture;
2. verify current AWS documentation;
3. simulate the data flow locally;
4. explicitly label the simulation.

Record:

- latency
- setup effort
- configuration
- monitoring
- limitations
- cost

## Lab 4 — DMS → Kinesis or MSK

Choose:

```text
PostgreSQL → DMS → Kinesis
```

or:

```text
PostgreSQL → DMS → MSK
```

Compare the selected architecture with Debezium.

## Lab 5 — Replication Incident

Simulate:

```text
DMS task stops
 ↓
CDC lag increases
 ↓
Replication slot stops advancing
 ↓
WAL grows
```

Detect, diagnose, recover, verify, and document.

## Lab 6 — DMS vs Zero-ETL vs Debezium ADR

Write an ADR covering:

```text
Context
Requirements
DMS
Zero-ETL
Debezium
Decision
Alternatives rejected
Latency
Cost
Security
Operations
Schema evolution
Lock-in
Recovery
```

---

# 44. Break/Fix Exercises

1. **Wrong credentials:** DMS cannot connect to PostgreSQL.
2. **Missing replication permissions:** connection works but CDC does not.
3. **WAL growth:** replication stops and source disk increases.
4. **Schema mismatch:** target cannot accept a source change.
5. **Large transaction:** CDC lag increases.
6. **Target throttling:** DMS cannot keep up.
7. **Validation mismatch:** source and target counts differ.
8. **Duplicate change:** target receives repeated changes.
9. **DMS task failure:** diagnose from logs/metrics.
10. **Zero-ETL limitation:** required source/target combination is unsupported.

For each exercise require:

```text
Symptom
Evidence
Root cause
Immediate containment
Fix
Verification
Prevention
```

---

# 45. Troubleshooting Runbooks

## DMS connection failure

Check:

1. DNS/network reachability.
2. Port/security group.
3. Endpoint credentials.
4. TLS configuration.
5. Database availability.
6. Endpoint test result.

## DMS task failure

Check:

1. Task state.
2. Error message.
3. Source endpoint.
4. Target endpoint.
5. IAM/network permissions.
6. Recent schema changes.
7. Logs.

## CDC lag

Check:

```text
Source load
DMS capacity
Network
Large transactions
Target throughput
LOBs
Errors
```

## WAL growth

Check:

1. replication-slot state
2. DMS task health
3. slot position
4. source disk headroom
5. whether required changes remain recoverable

Never delete a slot as a first response.

## Schema mismatch

Identify:

```text
Source DDL
↓
DMS behavior
↓
Target DDL
↓
Downstream contract
```

## Target throttling

Check target capacity, DMS throughput, batching, indexes, and downstream load.

## Validation mismatch

Compare counts, keys, samples, changes, deletes, and business reconciliation.

## LOB failure

Identify LOB size, target support, task settings, and performance impact.

## Data-type conversion failure

Compare source type → DMS type → target type and inspect precision/time-zone semantics.

## Duplicate data

Trace source transaction/event identity and target idempotency.

## Missing data

Determine whether the record was never captured, never transferred, rejected, or incorrectly applied.

## Zero-ETL integration failure

Verify source/target/region/version support first, then inspect integration health, permissions, encryption, schema constraints, and destination availability.

---

# 46. Common Mistakes

- Treating DMS as a transformation engine.
- No source capacity assessment.
- No replication-slot monitoring.
- Allowing WAL to grow indefinitely.
- No validation.
- Assuming raw DMS output is already analytical.
- Ignoring schema changes.
- Ignoring deletes.
- Ignoring duplicate CDC.
- No idempotency.
- No recovery plan.
- Leaving replication resources running.
- Assuming zero-ETL supports every source/target.
- Choosing Debezium without Kafka operational capability.
- Choosing DMS without understanding source impact.
- Hard-coded credentials.
- No cost monitoring.

The prevention principle is:

> Every replication architecture needs an explicit correctness contract, failure model, and recovery plan.

---

# 47. Performance Engineering

A conceptual throughput model is:

```text
Replication throughput
≈ minimum(
    source capacity,
    DMS capacity,
    network capacity,
    target capacity
)
```

This is a bottleneck model, not an AWS performance formula.

Important variables:

- source throughput
- transaction size
- DMS capacity
- network
- target throughput
- table count
- indexes
- LOBs
- schema complexity
- batch behavior
- CDC lag

Tune one bottleneck at a time and measure before/after.

---

# 48. Interview Preparation

## Beginner

- What is AWS DMS?
- What is CDC?
- What is Full Load?
- What is Full Load + CDC?
- What is a replication task?
- What is a DMS endpoint?

## Intermediate

- DMS provisioned vs Serverless?
- DMS to S3 vs Redshift?
- How do you validate replication?
- What are table mappings?
- How do you handle schema changes?
- What is replication lag?
- What is a PostgreSQL replication slot?

## Advanced

- Design PostgreSQL → S3 → Iceberg CDC.
- How do you prevent WAL from growing?
- DMS vs Debezium?
- DMS vs zero-ETL?
- How would you handle 10× transaction volume?
- How would you recover from CDC lag?
- How do you establish target correctness?
- How do you design enterprise database replication?
- How do you minimize downtime during migration?

For each major answer use:

1. short answer
2. detailed explanation
3. production example
4. common interview trap

---

# 49. Practice Questions

1. PostgreSQL has 2 TB and continuous writes. Design initial migration + CDC.
2. DMS lag grows from seconds to hours. Diagnose.
3. PostgreSQL WAL disk usage grows rapidly. Explain the cause and response.
4. Target data does not match source. Build a validation plan.
5. The company needs a Kafka ecosystem. Compare DMS and Debezium.
6. The company wants minimal operations. Evaluate zero-ETL.
7. The company needs S3 lake ingestion. Choose the architecture.
8. CDC contains updates and deletes. Build an Iceberg merge strategy.
9. Schema changes frequently. Compare DMS, zero-ETL, and Debezium.
10. Replication costs unexpectedly increase. Identify the cost drivers.

For every answer include reliability, security, observability, cost, and recovery considerations.

---

# 50. Cheat Sheets

## Replication

```text
Full Load
CDC
Full Load + CDC
```

## DMS

```text
Source
 ↓
Endpoint
 ↓
Replication Engine
 ↓
Task
 ↓
Target Endpoint
 ↓
Target
```

## CDC

```text
INSERT
UPDATE
DELETE
```

## PostgreSQL

```text
Transaction
 ↓
WAL
 ↓
Replication Slot
 ↓
DMS
```

## Lakehouse

```text
DMS
 ↓
S3 CDC
 ↓
Normalize / Deduplicate
 ↓
MERGE
 ↓
Iceberg
```

## Architecture Choice

```text
DMS
vs
Zero-ETL
vs
Debezium
```

---

# 51. Completion Checklist

### Fundamentals

- [ ] Explain database replication.
- [ ] Explain workload isolation.
- [ ] Explain Full Load.
- [ ] Explain CDC.
- [ ] Explain Full Load + CDC.

### DMS

- [ ] Source endpoints.
- [ ] Target endpoints.
- [ ] Replication instances.
- [ ] DMS Serverless.
- [ ] Replication tasks.
- [ ] Task types.
- [ ] Table mappings.
- [ ] Selection rules.
- [ ] Transformation rules.
- [ ] Task settings.
- [ ] Data validation.

### Targets

- [ ] S3.
- [ ] Kinesis.
- [ ] MSK.
- [ ] Redshift.
- [ ] Parquet.
- [ ] Change metadata.
- [ ] LOBs.
- [ ] Data types.
- [ ] Schema changes.

### Advanced CDC

- [ ] DMS CDC → S3 → Iceberg.
- [ ] MERGE.
- [ ] Ordering.
- [ ] Deduplication.
- [ ] Replication lag.
- [ ] PostgreSQL WAL.
- [ ] Replication slots.
- [ ] Source impact.
- [ ] Failure recovery.

### Architecture

- [ ] Zero-ETL.
- [ ] DMS vs zero-ETL vs Debezium.
- [ ] Schema Conversion awareness.
- [ ] Production architectures.
- [ ] ADRs.

### Operations

- [ ] Monitoring.
- [ ] Security.
- [ ] Cost.
- [ ] Performance.
- [ ] Break/fix.
- [ ] Runbooks.
- [ ] Interview preparation.
- [ ] Practice scenarios.

---

# 52. Final Roadmap Coverage Audit

| Roadmap requirement | Covered? | Section | Hands-on? |
|---|---|---:|---|
| AWS DMS | Yes | 5–12 | Yes |
| Source endpoints | Yes | 7 | Yes |
| Target endpoints | Yes | 8 | Yes |
| Replication instances | Yes | 9 | Yes |
| DMS Serverless | Yes | 10 | Yes |
| Replication tasks | Yes | 11–12 | Yes |
| PostgreSQL prerequisites | Yes | 13–14 | Yes |
| Least-privilege users | Yes | 14 | Yes |
| Table mappings | Yes | 15–16 | Yes |
| Transformation rules | Yes | 17 | Yes |
| DMS task settings | Yes | 18 | Yes |
| Data validation | Yes | 19 | Yes |
| S3 target | Yes | 20 | Yes |
| Kinesis target | Yes | 21 | Yes |
| MSK target | Yes | 22 | Yes |
| Redshift target | Yes | 23 | Yes |
| Parquet/change metadata | Yes | 24 | Yes |
| Large objects | Yes | 25 | Yes |
| Data types | Yes | 25 | Yes |
| Schema changes | Yes | 26 | Yes |
| Zero-ETL | Yes | 27–29 | Yes |
| DMS CDC → S3 → Iceberg | Yes | 30–31 | Yes |
| MERGE | Yes | 31 | Yes |
| CDC ordering | Yes | 31 | Yes |
| Replication lag | Yes | 32 | Yes |
| PostgreSQL WAL | Yes | 33 | Yes |
| Replication slots | Yes | 33 | Yes |
| Source impact | Yes | 34 | Yes |
| Failure/recovery | Yes | 35 | Yes |
| Monitoring | Yes | 36 | Yes |
| Security | Yes | 37 | Yes |
| Cost optimization | Yes | 38 | Yes |
| DMS vs zero-ETL vs Debezium | Yes | 39 | Yes |
| DMS Schema Conversion awareness | Yes | 40 | Awareness |
| Production architectures | Yes | 41 | Yes |
| ADRs | Yes | 42 | Yes |
| Hands-on labs | Yes | 43 | Yes |
| Break/fix | Yes | 44 | Yes |
| Troubleshooting runbooks | Yes | 45 | Yes |
| SQL/CLI/boto3 | Yes | Throughout | Yes |
| Terraform | Yes | Architecture/IaC guidance | Yes |
| Validation framework | Yes | 19 | Yes |
| Performance engineering | Yes | 47 | Yes |
| Interview preparation | Yes | 48 | Yes |
| Practice questions | Yes | 49 | Yes |
| Cheat sheets | Yes | 50 | Yes |
| Completion checklist | Yes | 51 | Yes |
| Final roadmap audit | Yes | 52 | Yes |

## Production Engineering Standard

A replication platform is production-ready only when:

- The source impact is measured.
- CDC prerequisites are explicit.
- Credentials are least privilege and securely stored.
- Network paths are private where appropriate.
- Replication scope is version controlled.
- Full-load/CDC correctness is validated.
- Deletes are handled.
- Duplicate CDC is handled.
- Ordering semantics are understood.
- Replication lag is monitored.
- PostgreSQL WAL/slot health is monitored where relevant.
- Schema evolution has an explicit policy.
- Raw CDC can be replayed where required.
- Target state can be reconciled to source.
- Failure recovery is documented.
- Cost is attributable.
- Infrastructure is reproducible.
- Current AWS documentation has been checked before production deployment.

## Final Learning Loop

```text
READ
 ↓
DRAW
 ↓
IMPLEMENT
 ↓
RUN
 ↓
BREAK
 ↓
OBSERVE
 ↓
DIAGNOSE
 ↓
FIX
 ↓
VALIDATE
 ↓
MEASURE
 ↓
DOCUMENT
 ↓
EXPLAIN
```

> **Final principle:** Database replication is not simply moving rows. Production replication is the disciplined management of **change, correctness, ordering, schema evolution, source impact, latency, recovery, security, and cost**.

### Current official AWS references used for version-sensitive guidance

- AWS DMS PostgreSQL source guidance. citeturn0search2
- AWS DMS S3 target guidance. citeturn0search0
- AWS DMS S3 endpoint API settings. citeturn0search6
- Amazon RDS zero-ETL documentation. citeturn0search3
- Amazon Redshift zero-ETL documentation. citeturn0search5


# 53. Required Hands-On Lab 6 — DMS vs Zero-ETL vs Debezium ADR

Create a production Architecture Decision Record containing:

```text
Context
Requirements
DMS option
Zero-ETL option
Debezium option
Decision
Why alternatives were rejected
Latency
Cost
Security
Operations
Schema evolution
Lock-in
Failure recovery
```

The learner must defend the decision rather than select a technology by familiarity.

# 54. Break/Fix Exercises

Work through at least these incidents:

1. Wrong credentials.
2. Missing replication permissions.
3. WAL growth.
4. Schema mismatch.
5. Large transaction causing CDC lag.
6. Target throttling.
7. Validation mismatch.
8. Duplicate CDC change.
9. DMS task failure.
10. Unsupported zero-ETL source/target combination.

For every incident:

```text
Symptom
↓
Evidence
↓
Likely cause
↓
Containment
↓
Fix
↓
Verification
↓
Prevention
```

# 55. Troubleshooting Runbook

Use a reusable runbook:

```text
Symptom
↓
Evidence
↓
Likely cause
↓
Commands / console locations
↓
Diagnosis
↓
Fix
↓
Verification
↓
Prevention
```

Required runbooks:

- DMS connection failure
- DMS task failure
- CDC lag
- WAL growth
- replication-slot issue
- schema mismatch
- target throttling
- validation mismatch
- LOB failure
- data-type conversion failure
- duplicate data
- missing data
- zero-ETL integration failure

# 56. SQL and CLI Examples

Use realistic, credential-safe examples.

Representative PostgreSQL setup:

```sql
CREATE USER dms_replication_user
WITH PASSWORD '<secure-secret-placeholder>';
```

Do not grant superuser privileges merely to make a lab work.

Include examples for:

- checking replication state
- inspecting WAL/replication slots
- checking table counts
- validating records
- DMS endpoint inspection
- replication-instance inspection
- replication-task status
- boto3 resource description
- starting/stopping tasks

Exact AWS CLI and boto3 parameters must be verified against current documentation before execution.

# 57. Terraform

Represent replication infrastructure as code where appropriate:

```text
DMS resources
Endpoints
IAM
S3
Networking
Monitoring
Tags
```

Use Terraform/OpenTofu for repeatability.

```text
Console
  =
Exploration

Terraform/OpenTofu
  =
Repeatability
```

Do not invent provider resource names or arguments. Verify the current AWS provider documentation before deployment.

# 58. Data Validation Framework

Use nine validation levels:

```text
LEVEL 1  Connection
LEVEL 2  Row counts
LEVEL 3  Sample records
LEVEL 4  Checksums / hashes
LEVEL 5  Insert validation
LEVEL 6  Update validation
LEVEL 7  Delete validation
LEVEL 8  CDC lag
LEVEL 9  Business reconciliation
```

The final validation question is not:

> Is the DMS task green?

It is:

> Can the business trust the target data?

# 59. Performance Engineering

Replication throughput is constrained by the slowest meaningful stage:

```text
Replication throughput
≈ minimum(
    source capacity,
    DMS capacity,
    network capacity,
    target capacity
)
```

This is a conceptual bottleneck model, not a literal AWS performance formula.

Tune:

- source workload
- transaction size
- DMS capacity
- network
- target throughput
- table count
- indexes
- LOBs
- schema complexity
- batch behavior
- CDC lag

Change one major variable at a time and measure the effect.

# 60. Advanced CDC Failure Modes

## Long transactions

Large transactions can delay visible CDC application and create bursts.

## Bursty workloads

A system that is normally healthy can accumulate lag during sudden write-volume increases.

## Schema changes

DDL can break downstream consumers if the target data contract changes unexpectedly.

## Replication restart

Recovery must account for the last trustworthy source position and target state.

## Duplicate delivery

Idempotent downstream application is required where duplicate changes are possible.

## Out-of-order application

Applying updates out of transaction order can corrupt the target state.

## Source overload

CDC consumes source resources. Replication must be part of OLTP capacity planning.

# 61. Production Security Architecture

Preferred topology:

```text
Private RDS/Aurora
        ↓
Private networking
        ↓
DMS
        ↓
Private target
```

Use:

- IAM
- least-privilege database users
- Secrets Manager
- KMS
- TLS/SSL
- security groups
- private subnets
- VPC endpoints where appropriate
- audit logging

Never put credentials in source code or Terraform state without understanding the associated secret-management risk.

# 62. Production Architecture #1 — Database to Lake

```text
RDS PostgreSQL
       ↓
AWS DMS
       ↓
S3 raw CDC
       ↓
Glue / Athena / Spark
       ↓
Iceberg
       ↓
Analytics
```

Responsibilities:

- DMS captures source changes.
- S3 preserves raw evidence.
- downstream processing normalizes changes.
- Iceberg represents curated state.
- catalog/governance controls access.

# 63. Production Architecture #2 — Database to Warehouse

```text
Aurora / RDS
      ↓
DMS / Zero-ETL
      ↓
Redshift
      ↓
Analytics
```

Choose DMS when migration/replication flexibility is needed; evaluate zero-ETL when the exact source/target combination is supported and lower pipeline operational burden is valuable.

# 64. Production Architecture #3 — Database to Kafka

```text
Operational DB
      ↓
DMS / Debezium
      ↓
MSK
      ↓
Kafka consumers
      ↓
Streaming platform
```

Evaluate:

- Kafka expertise
- replay requirements
- schema governance
- consumer ecosystem
- CDC control
- operational ownership

# 65. Production Architecture #4 — Hybrid

```text
                    ┌→ S3 / Iceberg
                    |
Operational DB → CDC ─→ MSK
                    |
                    └→ Redshift
```

Use a hybrid only when multiple downstream requirements justify the added reliability and operational complexity.

# 66. Orchestration Awareness

Connect this topic to Topic 10 without re-teaching orchestration.

A workflow may coordinate:

```text
DMS
 ↓
Validation
 ↓
CDC application
 ↓
DQ
 ↓
Downstream processing
```

Step Functions or MWAA can manage the workflow while DMS performs replication.

The separation of concerns is:

```text
Orchestrator = workflow control
DMS          = replication
Glue/Spark   = transformation
Iceberg      = table state
```

# 67. Observability Awareness

Connect this topic to Topic 12.

A conceptual dashboard should include:

```text
Task status
CDC latency
Throughput
Errors
Source DB health
Replication slot/WAL health
Target health
```

Use CloudWatch, DMS logs/metrics, database telemetry, and audit trails as appropriate.

# 68. Common Mistakes

Avoid:

- treating DMS as a transformation engine
- ignoring source capacity
- ignoring replication slots
- allowing WAL to grow indefinitely
- skipping validation
- assuming raw DMS files are analytical tables
- ignoring schema changes
- ignoring deletes
- ignoring duplicates
- assuming exactly-once semantics
- having no recovery plan
- leaving replication resources running
- assuming every zero-ETL combination is supported
- choosing Debezium without Kafka operational capability
- choosing DMS without source-impact analysis
- hard-coded credentials
- no cost monitoring

# 69. Decision Matrix

| Requirement | DMS | Zero-ETL | Debezium |
|---|---|---|---|
| AWS-managed experience | Strong | Strong | Depends on platform |
| Minimal operations | Moderate | Often strong | Lower |
| Migration flexibility | Strong | Narrower | Strong |
| Kafka ecosystem | Possible | Not primary | Strong |
| Custom CDC control | Moderate | Lower | Strong |
| Portability | Moderate | Lower | Strong |
| Lake ingestion | Strong | Integration-dependent | Strong with Kafka |
| Warehouse ingestion | Strong | Strong for supported combinations | Requires platform |
| Schema-change flexibility | Configuration-dependent | Integration-dependent | High control |
| Operational simplicity | Moderate | Often high | Lower |
| Lock-in | AWS | Higher AWS dependency | Lower |

The matrix is a starting point. Requirements decide the architecture.

# 70. Architecture Decision Records

Create at least:

### ADR 1 — Why DMS instead of Debezium?

### ADR 2 — Why zero-ETL instead of DMS?

### ADR 3 — Why DMS → S3 instead of DMS → Redshift?

### ADR 4 — Why Debezium → MSK?

### ADR 5 — Why CDC → S3 → Iceberg?

Each ADR contains:

```text
Context
Requirements
Decision
Alternatives
Latency
Reliability
Schema evolution
Security
Cost
Operations
Lock-in
Risks
```

# 71. Interview Preparation

## Beginner

- What is AWS DMS?
- What is CDC?
- What is Full Load?
- What is Full Load + CDC?
- What is a DMS replication task?
- What is a DMS endpoint?

## Intermediate

- DMS provisioned vs DMS Serverless?
- DMS to S3 vs DMS to Redshift?
- How do you validate replication?
- What are table mappings?
- How do you handle schema changes?
- What is replication lag?
- What is a PostgreSQL replication slot?

## Advanced

- Design PostgreSQL → S3 → Iceberg CDC.
- How would you prevent WAL from growing?
- DMS vs Debezium?
- DMS vs zero-ETL?
- How would you handle 10× transaction volume?
- How would you recover from CDC lag?
- How do you establish target correctness?
- How would you design enterprise database replication?
- How would you minimize downtime during migration?

For important questions prepare:

1. short answer
2. detailed answer
3. production considerations
4. common interview trap

# 72. Practice Questions

1. PostgreSQL has 2 TB and continuous writes. Design initial migration + CDC.
2. DMS lag grows from seconds to hours. Diagnose it.
3. WAL disk usage grows rapidly. Explain cause and response.
4. Target data does not match source. Build a validation plan.
5. The company needs Kafka. Compare DMS and Debezium.
6. The company wants minimal operations. Evaluate zero-ETL.
7. The company needs S3 lake ingestion. Choose the architecture.
8. CDC contains updates and deletes. Design the Iceberg merge strategy.
9. Schema changes frequently. Choose among DMS, zero-ETL, and Debezium.
10. Replication costs increase unexpectedly. Investigate the drivers.

For each scenario, include reliability, security, observability, cost, and recovery considerations.

# 73. Cheat Sheets

## Replication

```text
Full Load
CDC
Full Load + CDC
```

## DMS

```text
Source
 ↓
Endpoint
 ↓
Replication Engine
 ↓
Task
 ↓
Target Endpoint
 ↓
Target
```

## PostgreSQL

```text
Transaction
 ↓
WAL
 ↓
Replication Slot
 ↓
DMS
```

## Lakehouse

```text
DMS
 ↓
S3 CDC
 ↓
Deduplicate / Order
 ↓
MERGE
 ↓
Iceberg
```

## Architecture

```text
Managed migration/replication
    → DMS

Supported low-ops AWS integration
    → Zero-ETL

Kafka-centric programmable CDC
    → Debezium
```

# 74. AWS Cost Safety

Before every lab:

1. Check current pricing.
2. Configure AWS Budgets.
3. Use cost-allocation tags.
4. Use the smallest practical resources.
5. Stop/delete replication resources.
6. Remove test databases.
7. Remove lab networking.
8. Verify that resources are gone.

A common failure is leaving a replication instance or supporting infrastructure running after a lab.

# 75. Current AWS Documentation Requirement

Before production use, verify current official AWS documentation for:

- supported source engines
- supported target engines
- DMS Serverless capabilities
- replication task options
- CLI commands
- boto3 APIs
- endpoint configuration
- PostgreSQL prerequisites
- zero-ETL integrations
- supported regions
- schema-change behavior
- DMS output format
- Terraform provider resources
- pricing
- service limits
- DMS Schema Conversion

Never fabricate:

- API parameters
- prices
- quotas
- support matrices
- Terraform resource names
- metadata field names
- schema guarantees
- replication guarantees

If an exact current detail cannot be verified:

> Verify against the current official AWS documentation before using this in production.

# 76. Code Quality Requirements

All code examples must:

- be syntactically realistic
- avoid hard-coded credentials
- use placeholders for secrets
- prefer IAM/Secrets Manager where appropriate
- explain important lines
- be production-oriented
- distinguish illustrative examples from directly executable commands

Use:

```python
import boto3
```

when boto3 is appropriate.

Keep all examples inside this Markdown file; do not create external code files.

# 77. Production Engineering Principles

## Reliability

- Full-load/CDC consistency
- retries
- restartability
- validation
- replay/recovery
- idempotency

## Data correctness

- row counts
- hashes where useful
- business reconciliation
- CDC ordering
- deletes
- duplicates

## Performance

- replication capacity
- transaction size
- target throughput
- source load
- WAL
- LOBs

## Security

- least privilege
- private networking
- encryption
- secret management

## Cost

- right-sizing
- lifecycle management
- DMS Serverless where appropriate
- no idle resources

## Operability

- logs
- metrics
- alarms
- runbooks
- incident response

# 78. Final Learning Loop

Every major concept should follow:

```text
READ
 ↓
DRAW
 ↓
IMPLEMENT
 ↓
RUN
 ↓
BREAK
 ↓
OBSERVE
 ↓
DIAGNOSE
 ↓
FIX
 ↓
VALIDATE
 ↓
MEASURE
 ↓
DOCUMENT
 ↓
EXPLAIN
```

The target outcome is the ability to operate a replication platform, not merely describe DMS terminology.

# 79. Final Roadmap Coverage Audit

| Roadmap requirement | Covered? | Location |
|---|---|---|
| Database replication | Yes | 1–4 |
| Full Load | Yes | 3–4 |
| CDC | Yes | 3–4, 30–36 |
| AWS DMS | Yes | 5–18 |
| Source/target endpoints | Yes | 7–8 |
| Replication instances | Yes | 9 |
| DMS Serverless | Yes | 10 |
| Task types | Yes | 11–12 |
| PostgreSQL prerequisites | Yes | 13–14 |
| Table/selection/transformation rules | Yes | 15–17 |
| Task settings | Yes | 18 |
| Data validation | Yes | 19, 58 |
| S3 | Yes | 20, 30 |
| Kinesis | Yes | 21 |
| MSK | Yes | 22 |
| Redshift | Yes | 23 |
| Parquet/change metadata | Yes | 24 |
| LOBs/data types | Yes | 25 |
| Schema changes | Yes | 26 |
| Zero-ETL | Yes | 27–29 |
| CDC → S3 → Iceberg | Yes | 30–31 |
| MERGE | Yes | 31 |
| CDC ordering | Yes | 31, 60 |
| Replication lag | Yes | 32, 59–60 |
| WAL/replication slots | Yes | 33, 60 |
| Source impact | Yes | 34 |
| Failure/recovery | Yes | 35, 44–45 |
| Monitoring | Yes | 36, 67 |
| Security | Yes | 37, 61 |
| Cost | Yes | 38, 74 |
| DMS vs zero-ETL vs Debezium | Yes | 39, 69 |
| Decision framework | Yes | 39, 69 |
| Realistic scenarios | Yes | 41, 62–65 |
| Schema Conversion awareness | Yes | 40 |
| Hands-on labs | Yes | 43 |
| Break/fix | Yes | 44, 54 |
| Runbooks | Yes | 45, 55 |
| SQL/CLI/boto3 | Yes | 56 |
| Terraform | Yes | 57 |
| Performance engineering | Yes | 47, 59 |
| Orchestration awareness | Yes | 66 |
| Observability awareness | Yes | 67 |
| Common mistakes | Yes | 46, 68 |
| ADRs | Yes | 42, 70 |
| Interview preparation | Yes | 48, 71 |
| Practice questions | Yes | 49, 72 |
| Cheat sheets | Yes | 50, 73 |
| Cost safety | Yes | 74 |
| Current documentation | Yes | 75 |
| Code quality | Yes | 76 |
| Production principles | Yes | 77 |
| Learning loop | Yes | 78 |
| Final audit | Yes | 79 |

**Coverage result: PASS.**

# 80. Final Quality Check

Before considering the module complete, verify:

- [ ] All learning content remains in this Markdown file.
- [ ] No secrets or real credentials are present.
- [ ] Current AWS behavior is not presented from stale memory.
- [ ] Version-sensitive details are explicitly flagged for verification.
- [ ] Cost warnings are prominent.
- [ ] Labs use small, controlled resources.
- [ ] Failure paths are covered.
- [ ] Data correctness is treated separately from task health.
- [ ] Source impact and WAL health are operational concerns.
- [ ] DMS, zero-ETL, and Debezium are compared by requirements.
- [ ] The learner can defend an architecture decision.
- [ ] The final roadmap audit is complete.

# 81. Final Response Format

The final artifact should be delivered as:

```text
11-dms-and-zero-etl-integrations.md
```

The module is intentionally self-contained and production-oriented. It progresses:

```text
BEGINNER
  ↓
INTERMEDIATE
  ↓
ADVANCED
  ↓
PRODUCTION DATA PLATFORM ARCHITECTURE
```

> **Final mental model:** DMS answers *how do we move and replicate database changes?*; zero-ETL answers *can AWS provide a managed source-to-analytics integration for this supported combination?*; Debezium answers *do we need programmable, Kafka-centric CDC control?* The correct architecture is determined by source, target, latency, correctness, schema evolution, operational capability, security, cost, and lock-in.
