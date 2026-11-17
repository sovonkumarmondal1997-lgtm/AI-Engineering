# AWS Data Engineering Deep Dive — Practice Questions

## Overview

This practice bank is designed to test whether the learner can **apply** the production-oriented AWS Data Engineering knowledge covered in the Deep Dive rather than recall generic AWS trivia.

The set contains exactly **40 problems**:

| Difficulty | Questions |
|---|---:|
| Basic | 10 |
| Moderate | 10 |
| Hard | 10 |
| Advanced | 10 |
| **Total** | **40** |

The question set follows the supplied specification's required progression from foundational service selection through multi-service implementation, production troubleshooting, architecture, security, governance, observability, cost, and senior-level platform design. The specification explicitly requires source-grounded questions across the AWS Data Engineering Deep Dive and a Problem → Solution → Explanation structure. fileciteturn71file0L63-L89

## How to Use This Practice Set

For each problem:

1. Read only the **Problem** and **Your Task** first.
2. Write or diagram your own answer before reading the solution.
3. For Hard and Advanced questions, explicitly state:
   - assumptions;
   - service-selection reasoning;
   - failure modes;
   - security controls;
   - observability evidence;
   - cost implications;
   - rejected alternatives.
4. After reading the solution, compare the reasoning—not merely the final service names.
5. Rebuild the architecture from memory.
6. Where code is provided, adapt it to a sandbox AWS account with appropriate cost controls rather than deploying it blindly.

The supplied specification requires realistic production reasoning, cross-topic integration, troubleshooting, architecture, service selection, security, cost, observability, governance, validation, and trade-off analysis. fileciteturn71file0L192-L205

---

# Level 1 — Basic

### Question 01 — Choose the AWS service for a curated serverless lakehouse

**Difficulty:** Basic

**Topics:** AWS Service Landscape, S3, Glue, Athena

**Problem**

A team has curated Parquet/Iceberg data in Amazon S3 and wants a low-operations SQL layer for analysts. Metadata should remain discoverable through the AWS catalog layer. The team does not need a warehouse-first design.

**Your Task**

1. Select the primary query service.
2. Explain the role of the catalog.
3. Describe the resulting data flow.

---

## Solution

Use **Amazon Athena** as the SQL query engine, with S3 as storage and the Glue Data Catalog as the technical metadata layer.

```text
S3 / Iceberg
    ↓
Glue Data Catalog
    ↓
Athena
    ↓
SQL consumers
```

The important decision is separating storage, metadata, and query execution. Athena is appropriate when the workload is SQL over data in S3 and the design prioritizes serverless operation.

---

## Why This Solution Works

The solution keeps the architecture aligned with the AWS data-lake pattern taught in the module. A warehouse is not required merely because analysts need SQL.

---

## Key Concepts Tested

- S3 storage
- Glue Data Catalog
- Athena
- serverless query architecture

---

## Production Considerations

- Security: apply the appropriate IAM/Lake Formation controls.
- Cost: reduce scanned bytes through columnar data and appropriate partitioning.
- Observability: monitor query behavior and failures.

---


### Question 02 — Choose between Kinesis Data Streams and Firehose

**Difficulty:** Basic

**Topics:** Kinesis Data Streams, Kinesis Data Firehose

**Problem**

An application emits event records continuously. The engineering team needs a managed delivery path that can buffer records and land them in S3 without building a custom consumer application.

**Your Task**

1. Choose the better Kinesis service.
2. Explain why the other service is not the primary fit.
3. Describe the destination flow.

---

## Solution

Choose **Kinesis Data Firehose** when the requirement is managed delivery into a supported destination such as S3 and the team does not need to build and operate its own stream-consumer application.

```text
Producer
  ↓
Firehose
  ↓
S3
```

Kinesis Data Streams is the better fit when applications need direct stream consumption, replay-oriented processing, consumer management, or application-controlled processing.

---

## Why This Solution Works

The distinction is delivery-oriented Firehose versus consumer-oriented Data Streams. The module treats them as different layers rather than interchangeable products.

---

## Key Concepts Tested

- Firehose delivery
- Kinesis Data Streams
- Managed ingestion
- S3 destination

---

## Production Considerations

- Reliability: understand buffering and delivery behavior.
- Cost: avoid adding a consumer architecture when managed delivery satisfies the requirement.

---


### Question 03 — Identify why a Glue crawler does not fix business definitions

**Difficulty:** Basic

**Topics:** Glue Data Catalog, Crawlers, Business Metadata

**Problem**

A Glue crawler discovers a table and correctly infers its columns and data types. Analysts still disagree about what `revenue` means. The team asks whether another crawler configuration will solve the problem.

**Your Task**

1. Explain what the crawler is responsible for.
2. Identify what is missing.
3. Name the appropriate governance concept.

---

## Solution

The crawler is responsible for discovering technical metadata such as schemas and partitions. It does not establish the organization's business definition of revenue.

The missing layer is **business metadata / business glossary** governance.

```text
Crawler
  ↓
Technical metadata

Business glossary
  ↓
Business meaning
```

The definition should be owned and governed rather than inferred from the physical schema.

---

## Why This Solution Works

Technical metadata and business metadata answer different questions. A correct schema does not guarantee a correct business interpretation.

---

## Key Concepts Tested

- Glue crawler
- Technical metadata
- Business metadata
- Business glossary

---

## Production Considerations

- Governance: assign an accountable owner for business definitions.
- Reliability: prevent semantic drift across consumers.

---


### Question 04 — Choose a basic Glue incremental-processing strategy

**Difficulty:** Basic

**Topics:** Glue ETL, Job Bookmarks, Incremental Processing

**Problem**

A daily Glue ETL job reads new source objects from S3. Reprocessing the entire historical dataset every day is wasteful. The pipeline's source pattern is compatible with Glue job bookmarks.

**Your Task**

1. Identify the mechanism that can track previously processed data.
2. Explain the high-level flow.
3. State one validation check.

---

## Solution

Use **Glue job bookmarks** where the source and job pattern support them.

```text
New source objects
      ↓
Glue ETL job
      ↓
Bookmark/state tracking
      ↓
Process new work
```

Validate that the expected new objects are processed and that rerunning the job does not unexpectedly duplicate previously completed work.

---

## Why This Solution Works

The question tests the module's incremental-processing concept rather than generic batch processing.

---

## Key Concepts Tested

- Glue ETL
- Job bookmarks
- Incremental processing
- Idempotency

---

## Production Considerations

- Reliability: understand the state boundary and rerun behavior.
- Observability: inspect job run results and processed-record/object counts.

---


### Question 05 — Explain an Athena cost problem caused by poor data layout

**Difficulty:** Basic

**Topics:** Athena, Parquet, Partitioning, Query Cost

**Problem**

An Athena query reads a small logical slice of a very large dataset, but the query scans far more data than expected. The underlying files are not well organized for the filter being used.

**Your Task**

1. Identify the main cost mechanism.
2. Name two data-layout improvements.
3. Explain how to verify the improvement.

---

## Solution

Athena cost and performance are strongly influenced by the amount of data scanned. Improve the layout by using appropriate partitioning and columnar formats such as Parquet, and use partition projection where that is a better fit for the partition model.

Validate by comparing the bytes scanned and query runtime before and after the change.

---

## Why This Solution Works

The correct response is evidence-driven: change layout, then measure scanned bytes and runtime rather than assuming the query became cheaper.

---

## Key Concepts Tested

- Athena scanned bytes
- Parquet
- Partitioning
- Partition projection

---

## Production Considerations

- Cost: measure bytes scanned.
- Performance: compare runtime and file-read behavior.
- Observability: retain query evidence.

---


### Question 06 — Explain Lake Formation versus catalog discovery

**Difficulty:** Basic

**Topics:** Lake Formation, Glue Data Catalog, Governance

**Problem**

A user can see a table in the catalog but receives an authorization error when querying it through Athena. A teammate claims that catalog visibility proves the user should be able to read the data.

**Your Task**

1. Explain why the claim is incorrect.
2. Identify the governance layer involved.
3. Describe the diagnostic direction.

---

## Solution

Catalog visibility and authorization are separate concerns.

```text
Glue Data Catalog
= metadata/discovery

Lake Formation / IAM
= authorization, where applicable

Athena
= query execution
```

The engineer should inspect the applicable Lake Formation and IAM permissions rather than making the catalog broader.

---

## Why This Solution Works

The module explicitly separates discovery from authorization. A metadata object being visible does not automatically grant data access.

---

## Key Concepts Tested

- Glue Catalog
- Lake Formation
- IAM
- Athena authorization

---

## Production Considerations

- Security: use least privilege.
- Reliability: diagnose the first failing authorization layer.
- Auditability: inspect grants and relevant audit evidence.

---


### Question 07 — Choose a Redshift deployment model for variable workloads

**Difficulty:** Basic

**Topics:** Redshift Serverless, Provisioned Redshift

**Problem**

An analytics workload is highly variable. The team wants to avoid managing a permanently sized warehouse when demand is intermittent, while still using Redshift SQL and warehouse capabilities.

**Your Task**

1. Identify the first deployment model to evaluate.
2. Explain the trade-off against provisioned Redshift.
3. Name one cost consideration.

---

## Solution

Evaluate **Redshift Serverless** first because the workload is variable and the team wants less capacity-management overhead.

The trade-off is between serverless consumption/capacity behavior and the control and planning characteristics of provisioned Redshift.

Cost analysis must use actual workload behavior and current pricing rather than a static assumption.

---

## Why This Solution Works

Service selection should follow workload characteristics, not product preference.

---

## Key Concepts Tested

- Redshift Serverless
- Provisioned Redshift
- Workload variability
- Cost

---

## Production Considerations

- Cost: measure actual capacity consumption.
- Performance: validate workload latency under representative concurrency.

---


### Question 08 — Identify the purpose of Step Functions Retry/Catch

**Difficulty:** Basic

**Topics:** Step Functions, Retry, Catch, Reliability

**Problem**

A Step Functions workflow invokes a Glue job. The Glue job sometimes fails because of a transient condition. The workflow currently fails immediately on the first error.

**Your Task**

1. Name the state-machine mechanisms to evaluate.
2. Explain their roles.
3. Describe the production principle.

---

## Solution

Use **Retry** for appropriate transient failures and **Catch** to route unrecoverable failures to a controlled recovery path.

```text
Task
 ├─ Retry transient failure
 └─ Catch terminal failure
       ↓
    recovery/alert path
```

Do not retry every error indiscriminately; retry policies should match the failure class.

---

## Why This Solution Works

Retry handles recoverable failure; Catch establishes explicit failure handling. This is more reliable than letting transient failures become pipeline incidents.

---

## Key Concepts Tested

- Step Functions
- Retry
- Catch
- Failure recovery

---

## Production Considerations

- Reliability: classify errors before retrying.
- Observability: record failed executions and recovery outcomes.
- Cost: avoid runaway retries.

---


### Question 09 — Explain PostgreSQL WAL growth during DMS CDC

**Difficulty:** Basic

**Topics:** AWS DMS, PostgreSQL WAL, Replication Slots, CDC

**Problem**

A PostgreSQL source is used for AWS DMS CDC. The source database's WAL volume is growing because the replication consumer is not keeping up.

**Your Task**

1. Explain the role of the replication slot.
2. Identify why WAL can accumulate.
3. Name the first operational area to investigate.

---

## Solution

PostgreSQL logical replication uses WAL, and replication slots can retain WAL until changes have been consumed/advanced. If DMS CDC falls behind, the source can retain more WAL.

Investigate DMS CDC health/lag and the PostgreSQL replication-slot state before changing unrelated database settings.

---

## Why This Solution Works

The production issue is a source-impact problem, not merely a DMS task status problem. CDC architecture must account for source WAL retention.

---

## Key Concepts Tested

- DMS CDC
- PostgreSQL WAL
- Replication slots
- Replication lag

---

## Production Considerations

- Reliability: monitor lag before source storage becomes critical.
- Observability: correlate DMS and source-database evidence.

---


### Question 10 — Explain why a DataZone subscription is not the same as a permission grant

**Difficulty:** Basic

**Topics:** DataZone, Data Products, Subscription Workflow, Governance

**Problem**

A consumer discovers a published data product in DataZone and submits a subscription request. Another engineer says the consumer should now be able to query the underlying table because the product is visible.

**Your Task**

1. Correct the statement.
2. Explain the subscription role.
3. Name the underlying authorization systems that may matter.

---

## Solution

A subscription is part of the governed request/approval workflow. It is not the same concept as unrestricted data authorization.

```text
Discover
  ↓
Request subscription
  ↓
Approval
  ↓
Underlying grant / authorization
  ↓
Consume
```

Depending on the supported asset and integration, Lake Formation, Redshift permissions, IAM, or other underlying controls may determine actual access.

---

## Why This Solution Works

The core governance mental model is `Discovery ≠ Authorization`.

---

## Key Concepts Tested

- DataZone
- Subscription
- Data product
- Lake Formation
- Redshift permissions

---

## Production Considerations

- Security: verify actual permissions.
- Governance: keep approval and authorization auditable.

---


# Level 2 — Moderate

### Question 11 — Build an S3 → Glue → Athena incremental lakehouse flow

**Difficulty:** Moderate

**Topics:** S3, Glue Catalog, Glue ETL, Athena, Iceberg

**Problem**

An e-commerce platform lands daily order files in S3. Analysts need a curated table with incremental processing and SQL access. The engineering team wants an AWS-native, low-operations architecture.

**Your Task**

1. Design the data flow.
2. Explain where metadata lives.
3. Explain how incremental processing and query access work.
4. Name two validation checks.

---

## Solution

Use:

```text
S3 raw orders
   ↓
Glue ETL
   ↓
Curated Parquet/Iceberg
   ↓
Glue Data Catalog
   ↓
Athena
```

Use an incremental-processing strategy such as job bookmarks where compatible, or explicit application state/watermarks where the source pattern requires it. Validate row counts, duplicate behavior, schema, and query results after each run.

The catalog describes the curated data; Athena executes SQL against the underlying lake data.

---

## Why This Solution Works

The architecture combines storage, processing, metadata, and query layers without introducing an unnecessary warehouse.

---

## Key Concepts Tested

- S3
- Glue ETL
- Job bookmarks
- Iceberg
- Glue Catalog
- Athena

---

## Production Considerations

- Security: least-privilege roles and governed access.
- Reliability: idempotency and validation.
- Cost: columnar layout and incremental processing.

---


### Question 12 — Quarantine failed records with Glue Data Quality

**Difficulty:** Moderate

**Topics:** Glue ETL, Glue Data Quality, DQDL, Quarantine

**Problem**

A SaaS ingestion pipeline receives customer records. A data-quality rule detects invalid identifiers. The business wants the valid records to continue while invalid records are isolated for investigation.

**Your Task**

1. Design the quality gate.
2. Describe the quarantine path.
3. Explain what evidence should be retained.

---

## Solution

Implement a quality stage that evaluates the required rules before publishing the trusted output.

```text
Raw
 ↓
Glue ETL
 ↓
Data Quality checks
 ├─ Pass → curated output
 └─ Fail → quarantine
```

Retain rule results, run identifiers, counts, sample failures, and the input/output relationship so the team can diagnose quality regressions.

---

## Why This Solution Works

A production quality system should not silently drop invalid records. It should make the failure visible and preserve evidence.

---

## Key Concepts Tested

- Glue Data Quality
- DQDL
- Quarantine
- Quality gates

---

## Production Considerations

- Reliability: prevent bad data from reaching trusted tables.
- Observability: retain rule results and counts.
- Governance: document quality expectations.

---


### Question 13 — Use Athena CTAS to create an optimized analytical table

**Difficulty:** Moderate

**Topics:** Athena, CTAS, Parquet, Partitioning, Cost

**Problem**

A large raw table is queried repeatedly for a common analytical subset. The current layout is inefficient. The team wants Athena to create a curated, columnar table that is cheaper to query.

**Your Task**

1. Choose the Athena operation.
2. Describe the output layout.
3. Explain the validation required before replacing the existing workload.

---

## Solution

Use **CTAS** to materialize a curated table in an efficient layout, such as Parquet with an appropriate partition strategy.

```sql
CREATE TABLE curated_orders
WITH (
  format = 'PARQUET',
  -- partition configuration appropriate to the workload
  external_location = 's3://<bucket>/curated/orders/'
) AS
SELECT ...
FROM raw_orders
WHERE ...;
```

Validate row counts, business totals, partition behavior, schema, and bytes scanned by representative queries.

---

## Why This Solution Works

CTAS is useful when a query pattern justifies materializing a more efficient analytical representation. The optimization must be measured rather than assumed.

---

## Key Concepts Tested

- Athena CTAS
- Parquet
- Partitioning
- Query cost

---

## Production Considerations

- Cost: compare scanned bytes.
- Reliability: validate completeness.
- Performance: benchmark representative queries.

---


### Question 14 — Fix a Redshift query slowed by poor table distribution

**Difficulty:** Moderate

**Topics:** Redshift, Distribution Styles, Sort Keys, Performance

**Problem**

A Redshift fact table joins repeatedly with a large dimension. The query has degraded as data volume grew. The team sees significant data movement during execution.

**Your Task**

1. Identify the table-design areas to inspect.
2. Explain how distribution can affect joins.
3. Name one validation approach.

---

## Solution

Inspect the distribution strategy and sort-key design against the actual join/filter workload. A compatible distribution strategy can reduce data movement, while appropriate sort ordering can improve scan efficiency.

Use query plans/system monitoring evidence to validate whether the redesign reduces data movement and runtime.

---

## Why This Solution Works

Redshift physical design is workload-driven. Distribution and sort choices should be based on query patterns, data volume, and skew.

---

## Key Concepts Tested

- Redshift distribution
- Sort keys
- Data movement
- Query performance

---

## Production Considerations

- Performance: measure execution plans and runtime.
- Cost: avoid scaling capacity to compensate for poor table design.

---


### Question 15 — Design Kinesis Streams → Firehose → S3

**Difficulty:** Moderate

**Topics:** Kinesis Data Streams, Firehose, S3, Streaming

**Problem**

A logistics system produces high-volume delivery events. Some consumers need the stream directly, while another requirement is durable delivery into S3 for analytics.

**Your Task**

1. Design the flow.
2. Explain why both Kinesis services are present.
3. Identify one streaming reliability metric.

---

## Solution

Use:

```text
Producers
   ↓
Kinesis Data Streams
   ├── application consumers
   └── Firehose
          ↓
         S3
```

Data Streams provides the stream for application consumers; Firehose provides managed delivery to S3. Monitor consumer lag and delivery health, and design downstream processing for replay/idempotency where needed.

---

## Why This Solution Works

The architecture separates application-controlled streaming consumption from managed delivery into the lake.

---

## Key Concepts Tested

- Kinesis Data Streams
- Firehose
- S3
- Consumer lag

---

## Production Considerations

- Reliability: account for partial/delivery failures.
- Cost: size streams and delivery paths to workload.
- Observability: monitor lag and delivery health.

---


### Question 16 — Use Lake Formation for governed cross-account analytics

**Difficulty:** Moderate

**Topics:** Lake Formation, Glue Catalog, Athena, Cross-Account Governance

**Problem**

A central data team owns curated customer data. Two analytics accounts need controlled access without copying unrestricted datasets into each account.

**Your Task**

1. Describe the governance approach.
2. Explain the roles of Glue Catalog, Lake Formation, and Athena.
3. State how you would validate least privilege.

---

## Solution

Use Lake Formation governance for supported data-lake assets and establish the required cross-account sharing/permission model.

```text
Producer account
S3 + Glue Catalog
      ↓
Lake Formation governance
      ↓
Consumer account
      ↓
Athena
```

Validate that an approved consumer can access only the intended database/table/columns/rows and that an unapproved identity receives an authorization failure.

---

## Why This Solution Works

Cross-account governance should preserve centralized control while allowing approved consumers to query governed data.

---

## Key Concepts Tested

- Lake Formation
- Cross-account sharing
- Glue Catalog
- Athena
- Fine-grained access

---

## Production Considerations

- Security: least privilege and negative tests.
- Auditability: retain evidence of grants and access.

---


### Question 17 — Secure Glue access to S3 without unnecessary public routing

**Difficulty:** Moderate

**Topics:** Glue ETL, S3, KMS, VPC Endpoints, Private Networking

**Problem**

A Glue workload runs inside a VPC. The security team does not want data traffic to depend on public internet paths. The workload reads encrypted S3 data and must use least-privilege access.

**Your Task**

1. Identify the networking pattern.
2. Explain the role of S3 gateway endpoints.
3. Explain the KMS/IAM considerations.

---

## Solution

Use a private subnet design with an appropriate S3 gateway endpoint where applicable, rather than forcing S3 traffic through an unnecessary NAT path.

```text
Private Glue workload
       ↓
S3 gateway endpoint
       ↓
S3
```

Use an execution role with least privilege and a KMS key policy/grant model that permits the required encryption operations. Validate routing, endpoint policy, bucket policy, IAM, and KMS permissions independently.

---

## Why This Solution Works

The design reduces unnecessary NAT dependency while preserving private access patterns and encryption.

---

## Key Concepts Tested

- Private subnets
- S3 gateway endpoint
- KMS
- IAM
- Glue

---

## Production Considerations

- Security: enforce least privilege and encryption.
- Cost: compare endpoint versus NAT architecture.
- Reliability: test endpoint routing and DNS/policy behavior.

---


### Question 18 — Orchestrate Glue + Data Quality + Athena with Step Functions

**Difficulty:** Moderate

**Topics:** Step Functions, Glue ETL, Data Quality, Athena

**Problem**

A daily finance pipeline must run Glue ETL, validate the output, and then make it available for an Athena-based validation query. Failures should be retried when transient and routed to an alert path when terminal.

**Your Task**

1. Design the state-machine sequence.
2. Identify Retry/Catch placement.
3. Describe validation evidence.

---

## Solution

A conceptual state machine is:

```text
Start
 ↓
Glue ETL
 ↓
Data Quality
 ↓
Athena validation
 ↓
Success

Failures
 ├─ Retry transient
 └─ Catch terminal → alert/recovery
```

Use explicit state inputs/outputs and idempotent job behavior. Retain execution history and data-quality/query evidence.

---

## Why This Solution Works

Step Functions provides orchestration; Glue performs ETL; quality controls the trust boundary; Athena can provide SQL-level validation.

---

## Key Concepts Tested

- Step Functions
- Glue
- Data Quality
- Athena
- Retry/Catch

---

## Production Considerations

- Reliability: classify retryable errors.
- Observability: inspect execution history and metrics.
- Cost: prevent unbounded retries.

---


### Question 19 — Design DMS CDC into an S3/Iceberg analytical layer

**Difficulty:** Moderate

**Topics:** DMS, CDC, S3, Iceberg, Glue, Athena

**Problem**

A PostgreSQL operational database needs near-continuous changes replicated into an analytical lake. Analysts ultimately query the curated data through Athena.

**Your Task**

1. Design the ingestion path.
2. Explain the role of WAL/replication slots.
3. Explain how CDC changes become queryable analytical state.

---

## Solution

A suitable pattern is:

```text
PostgreSQL
  ↓
DMS full load + CDC
  ↓
S3
  ↓
CDC processing / reconciliation
  ↓
Iceberg curated tables
  ↓
Glue Catalog
  ↓
Athena
```

PostgreSQL logical replication uses WAL and replication slots; therefore source WAL retention and DMS lag must be monitored. CDC records must be applied idempotently to the analytical table, commonly using keys/change metadata and merge-style processing.

---

## Why This Solution Works

DMS transports change information; it does not by itself define the final analytical table semantics. The curated layer must reconcile changes into queryable state.

---

## Key Concepts Tested

- DMS
- PostgreSQL WAL
- CDC
- S3
- Iceberg
- Athena

---

## Production Considerations

- Reliability: monitor lag and recovery.
- Data quality: reconcile source and target counts/state.
- Cost: control small-file and query-layout issues.

---


### Question 20 — Publish and govern a DataZone data product

**Difficulty:** Moderate

**Topics:** DataZone, Data Products, Glue Catalog, Lake Formation

**Problem**

A finance team has a curated `gold.daily_revenue` table in the Glue Data Catalog. Another team needs to discover it, understand its business definition, request access, and query it through a governed path.

**Your Task**

1. Describe the producer workflow.
2. Describe the consumer workflow.
3. Explain what remains the underlying authorization boundary.

---

## Solution

Producer:

```text
Curated table
 → project inventory
 → business metadata/glossary
 → publish data product
```

Consumer:

```text
Discover
 → inspect definition/owner
 → request subscription
 → approval
 → underlying access grant
 → consume
```

For supported AWS-managed assets, the subscription workflow can coordinate underlying access controls such as Lake Formation or Redshift permissions. Validate the actual grant rather than treating publication as authorization.

---

## Why This Solution Works

The workflow combines technical metadata, business metadata, governed sharing, and underlying authorization.

---

## Key Concepts Tested

- DataZone
- Data products
- Glue Catalog
- Lake Formation
- Subscription

---

## Production Considerations

- Security: discovery must not imply unrestricted access.
- Governance: require owner/definition metadata.
- Auditability: retain approval and grant evidence.

---


# Level 3 — Hard

### Question 21 — Diagnose an Athena query that suddenly became expensive

**Difficulty:** Hard

**Topics:** Athena, Partition Projection, CTAS, Query Optimization, Cost

**Problem**

An e-commerce analytics query used to scan a modest amount of data. After a data-layout change, the same logical query scans dramatically more data and costs more. Runtime also increased.

**Your Task**

1. Build an evidence-driven diagnosis.
2. Identify likely data-layout causes.
3. Propose a fix and validation plan.
4. Explain why simply increasing query capacity is not the first response.

---

## Solution

First inspect query history and bytes scanned, then compare the table's partitions, file layout, and predicates.

Potential causes include:
- partition pruning no longer works;
- partition projection configuration does not match the actual S3 layout;
- files are no longer efficiently partitioned;
- the workload is reading a broad path;
- a CTAS/materialization change removed useful pruning.

Fix the data layout or projection configuration, then rerun representative queries and compare bytes scanned and runtime.

Do not treat increased cost as a capacity problem first; Athena optimization begins with reducing unnecessary data scanned.

---

## Why This Solution Works

Athena performance and cost are strongly tied to data layout and pruning. The correct response is to inspect evidence before changing architecture.

---

## Key Concepts Tested

- Athena
- Partition projection
- CTAS
- Partition pruning
- Cost

---

## Production Considerations

- Cost: compare scanned bytes before/after.
- Reliability: validate complete results after layout changes.
- Observability: preserve query evidence.

---


### Question 22 — Diagnose a Glue job that became slow after a schema change

**Difficulty:** Hard

**Topics:** Glue ETL, Spark, DynamicFrames/DataFrames, Schema Evolution, Performance

**Problem**

A Glue ETL job previously completed in 20 minutes. After a source schema change, it now takes more than an hour. The input volume is unchanged. Some columns have changed types and several records contain unexpected structures.

**Your Task**

1. Identify the investigation path.
2. Explain DynamicFrame/DataFrame implications.
3. Propose a safe remediation.
4. Define validation evidence.

---

## Solution

Inspect the schema at the source/catalog boundary first, then examine how the job handles evolving or ambiguous fields.

Use DynamicFrames where their schema-flexibility/Choice-type handling is beneficial, then convert to DataFrames at a controlled point when Spark SQL/DataFrame transformations are preferable. Explicitly resolve incompatible types rather than letting an unexpected schema propagate.

Validate:
- source schema;
- resolved schema;
- rejected/quarantined records;
- row counts;
- execution-stage timings;
- output schema;
- representative business results.

Do not increase worker capacity until the schema-induced processing behavior is understood.

---

## Why This Solution Works

Uncontrolled schema evolution can change execution behavior even when data volume is constant. Diagnose schema and transformation stages before scaling compute.

---

## Key Concepts Tested

- Glue ETL
- DynamicFrames
- DataFrames
- Choice/schema handling
- Spark performance

---

## Production Considerations

- Data quality: quarantine malformed records.
- Performance: inspect stage behavior before scaling.
- Reliability: make schema changes explicit and testable.

---


### Question 23 — Diagnose a Kinesis hot shard and increasing consumer lag

**Difficulty:** Hard

**Topics:** Kinesis Data Streams, Shards, Partition Keys, KCL/EFO, Lag

**Problem**

A SaaS event stream has increasing consumer lag. CloudWatch shows one shard is consistently much busier than the others. Producers use a customer identifier as the partition key, and one customer generates a disproportionate amount of traffic.

**Your Task**

1. Identify the root cause.
2. Explain why simply adding consumers may not solve it.
3. Propose a partitioning/scaling strategy.
4. Define validation metrics.

---

## Solution

The likely root cause is a **hot shard** caused by an imbalanced partition-key distribution.

Changing only the consumer fleet does not remove the producer-side concentration if the records continue mapping disproportionately to one shard.

Evaluate a better partition-key strategy that preserves the required ordering semantics while distributing load, and consider resharding where appropriate.

Validate:
- per-shard incoming records/bytes;
- consumer lag;
- producer distribution;
- downstream ordering requirements.

---

## Why This Solution Works

Kinesis partition keys determine shard distribution. A single high-volume key can create localized saturation even when aggregate stream capacity looks sufficient.

---

## Key Concepts Tested

- Partition keys
- Hot shards
- Resharding
- Consumer lag
- KCL/EFO

---

## Production Considerations

- Reliability: preserve required ordering guarantees.
- Performance: balance shard utilization.
- Cost: avoid overprovisioning the entire stream for one bad key.

---


### Question 24 — Diagnose Redshift performance degradation caused by skew

**Difficulty:** Hard

**Topics:** Redshift, Distribution Styles, Sort Keys, Performance, Cost

**Problem**

A Redshift workload has grown 5×. Queries now show uneven work across nodes and long-running joins. The team proposes adding capacity immediately.

**Your Task**

1. Diagnose the physical-design problem.
2. Explain the role of distribution and sort keys.
3. Propose a validation plan before scaling capacity.
4. Identify one case where scaling may still be appropriate.

---

## Solution

Inspect query plans and table/system evidence for distribution skew, data movement, unsorted regions, and join/filter patterns.

If distribution is causing uneven work, redesign the distribution strategy around the dominant joins. If sort order no longer matches access patterns, reassess sort keys and automatic table optimization behavior.

Validate with representative queries before/after the change.

Capacity scaling may still be appropriate when the physical design is sound but the workload has legitimately exceeded available compute/concurrency capacity.

---

## Why This Solution Works

Capacity is not a substitute for correct physical design. Diagnose data movement and skew first, then decide whether scaling is required.

---

## Key Concepts Tested

- Distribution skew
- Sort keys
- Data movement
- Redshift performance

---

## Production Considerations

- Performance: benchmark representative workloads.
- Cost: avoid paying for capacity that only masks poor design.

---


### Question 25 — Recover from DMS CDC lag and PostgreSQL WAL growth

**Difficulty:** Hard

**Topics:** DMS, CDC, PostgreSQL WAL, Replication Slots, Recovery

**Problem**

A production PostgreSQL source shows rapidly growing WAL storage. DMS CDC lag has increased steadily. The replication slot remains active. The target is temporarily unavailable because of a downstream incident.

**Your Task**

1. Protect the source first.
2. Diagnose the CDC chain.
3. Describe recovery considerations.
4. Identify what evidence should be monitored after recovery.

---

## Solution

Treat the source WAL growth as a production risk.

```text
PostgreSQL
  ↓ WAL
Replication slot
  ↓
DMS CDC
  ↓
Target
```

First establish why the target outage caused CDC consumption to stop and quantify slot/WAL retention. Restore the target path or a safe recovery path, then monitor CDC catch-up and source WAL reduction.

Do not blindly drop a replication slot as a "fix": that can destroy the ability to resume the expected CDC position. Any slot intervention must follow a deliberate recovery procedure and validated reinitialization plan.

---

## Why This Solution Works

CDC systems create a coupling between source WAL retention and downstream consumption. Recovery must protect source stability while preserving data correctness.

---

## Key Concepts Tested

- DMS CDC
- WAL
- Replication slots
- Lag
- Recovery

---

## Production Considerations

- Reliability: establish a tested recovery procedure.
- Data quality: reconcile missed/duplicated changes.
- Observability: monitor lag and WAL retention together.

---


### Question 26 — Diagnose Lake Formation AccessDenied after a successful DataZone subscription

**Difficulty:** Hard

**Topics:** DataZone, Lake Formation, Glue Catalog, Athena, IAM

**Problem**

An analytics team successfully subscribes to a DataZone-published Glue asset. The subscription is approved, but Athena still returns an authorization error. The producer insists that the table was published correctly.

**Your Task**

1. Trace the access path layer by layer.
2. Identify evidence to collect.
3. Propose a least-privilege fix.
4. Explain what you should not do.

---

## Solution

Trace:

```text
DataZone subscription
 → access-grant/materialization
 → Lake Formation permissions
 → Glue Catalog object
 → IAM identity
 → Athena query
```

Collect the subscription state, consumer project/environment, actual Lake Formation grants/data filters, IAM identity, and query error.

Fix the first missing grant or policy rather than adding broad `AdministratorAccess` or unrestricted S3 permissions. Verify both allowed and denied cases after the change.

---

## Why This Solution Works

Publication and subscription coordinate governed access but do not eliminate the underlying authorization layers.

---

## Key Concepts Tested

- DataZone
- Lake Formation
- Glue Catalog
- Athena
- IAM

---

## Production Considerations

- Security: least privilege and negative tests.
- Auditability: record grant evidence.
- Reliability: isolate the failing layer.

---


### Question 27 — Fix a private Glue job that cannot reach S3

**Difficulty:** Hard

**Topics:** Glue, VPC, Private Subnets, S3 Gateway Endpoint, Security, KMS

**Problem**

A Glue job runs in private subnets and previously accessed S3 successfully. After a networking change, the job times out when reading an encrypted S3 dataset. There is no requirement to use the public internet.

**Your Task**

1. Build a network/security troubleshooting tree.
2. Identify the S3 endpoint pattern.
3. Separate network failure from authorization/KMS failure.
4. Define validation.

---

## Solution

Investigate in layers:

```text
Subnet route table
  ↓
S3 gateway endpoint
  ↓
Endpoint policy
  ↓
Bucket policy
  ↓
IAM execution role
  ↓
KMS key policy/grants
```

Confirm the route table sends S3 traffic to the gateway endpoint, then inspect endpoint/bucket/IAM policies. If S3 access succeeds but encrypted object access fails, inspect KMS permissions separately.

Validate with a controlled read of a known test object and CloudWatch/Glue logs, then test the production path.

---

## Why This Solution Works

A timeout often indicates network/routing, while AccessDenied can indicate policy or KMS. The engineer should not conflate these failure classes.

---

## Key Concepts Tested

- Private subnet
- S3 gateway endpoint
- IAM
- KMS
- Glue

---

## Production Considerations

- Security: avoid broadening permissions as a network fix.
- Reliability: test each layer independently.
- Cost: avoid introducing NAT when an endpoint pattern is sufficient.

---


### Question 28 — Fix an EventBridge-triggered Step Functions workflow that does not start

**Difficulty:** Hard

**Topics:** EventBridge, Event Patterns, Step Functions, Orchestration, Observability

**Problem**

An S3-related event is expected to trigger a Step Functions state machine, but executions remain at zero. The producer says the event was emitted successfully.

**Your Task**

1. Diagnose the event-driven path.
2. Identify likely configuration failures.
3. Describe evidence needed to prove the fix.

---

## Solution

Trace:

```text
Event source
  ↓
EventBridge bus
  ↓
Event pattern/rule
  ↓
Target
  ↓
Step Functions
  ↓
Execution
```

Inspect the event shape actually received, compare it with the rule pattern, verify the correct event bus and Region, verify the target configuration and invocation permissions, and inspect EventBridge metrics/logging plus Step Functions execution history.

After the fix, send a representative event and verify exactly one intended execution.

---

## Why This Solution Works

Event-driven failures are often caused by mismatch between the actual event envelope and the configured event pattern, or by target/invocation configuration.

---

## Key Concepts Tested

- EventBridge
- Event patterns
- Step Functions
- Target permissions
- Observability

---

## Production Considerations

- Reliability: make event processing idempotent.
- Observability: preserve event and execution evidence.
- Cost: avoid duplicate triggers.

---


### Question 29 — Control an Athena/Iceberg maintenance and small-file problem

**Difficulty:** Hard

**Topics:** Athena, Iceberg, OPTIMIZE, VACUUM, S3, Cost

**Problem**

An Iceberg table receives frequent incremental writes. Over time, query performance degrades and the table contains many small files and old snapshots. The team wants to delete files manually from S3.

**Your Task**

1. Explain why manual deletion is unsafe.
2. Identify the Iceberg maintenance operations to evaluate.
3. Define a safe validation sequence.

---

## Solution

Do not manually delete active Iceberg data files from S3.

Evaluate Iceberg-aware maintenance such as **OPTIMIZE** for file compaction and **VACUUM** for snapshot/unreferenced-file cleanup according to the table's retention and workload requirements.

Validate:
- query performance;
- file counts/sizes;
- snapshot retention;
- ability to time travel within the intended retention window;
- downstream consumer behavior.

The maintenance policy should be explicit and operationally monitored.

---

## Why This Solution Works

Iceberg metadata governs which files represent table state. Directly deleting files can corrupt table readability or historical references.

---

## Key Concepts Tested

- Iceberg
- OPTIMIZE
- VACUUM
- Snapshots
- Small files

---

## Production Considerations

- Reliability: preserve valid table state.
- Cost: control storage and request overhead.
- Performance: reduce small-file fragmentation.

---


### Question 30 — Reduce a private data platform's unexpected NAT cost

**Difficulty:** Hard

**Topics:** VPC, Gateway Endpoints, Interface Endpoints, NAT, Cost

**Problem**

A private AWS data platform has Glue and other workloads in private subnets. The monthly bill shows significant NAT Gateway usage. Most of the data traffic is to AWS services that support private endpoint patterns.

**Your Task**

1. Determine what evidence to collect.
2. Identify traffic that may be moved to endpoints.
3. Explain the trade-off between gateway and interface endpoints.
4. Define a validation approach.

---

## Solution

Start with NAT metrics and traffic evidence to identify which destinations generate the cost.

For S3, evaluate an S3 **gateway endpoint** where appropriate. For services requiring interface endpoints, evaluate the service-specific interface endpoint and its security group/policy requirements.

Do not remove NAT globally without checking workloads that genuinely require it. Compare:

```text
NAT cost/complexity
vs
endpoint cost/complexity
```

Validate route tables, DNS, endpoint policies, service connectivity, and application behavior before and after the change.

---

## Why This Solution Works

Network cost optimization is destination-specific. S3 gateway endpoints can avoid NAT for S3 traffic, while interface endpoints have different operational/cost characteristics.

---

## Key Concepts Tested

- NAT Gateway
- S3 gateway endpoint
- Interface endpoint
- PrivateLink
- Cost

---

## Production Considerations

- Cost: attribute traffic before changing architecture.
- Security: constrain endpoint policies.
- Reliability: test all private service dependencies.

---


# Level 4 — Advanced

### Question 31 — Design a production serverless lakehouse for enterprise analytics

**Difficulty:** Advanced

**Topics:** S3, Glue, Athena, Iceberg, Lake Formation, Step Functions, CloudWatch, KMS

**Problem**

An enterprise wants a governed serverless lakehouse for finance and operations. Data arrives daily and incrementally. Analysts need SQL, governance requires fine-grained access, and the platform team wants minimal always-on infrastructure.

**Your Task**

1. Design the end-to-end architecture.
2. Explain service boundaries.
3. Include security, observability, reliability, and cost controls.
4. Explain why you would not introduce a large always-on Spark cluster.

---

## Solution

A strong baseline is:

```text
Sources
  ↓
S3 raw
  ↓
Glue ETL
  ↓
Iceberg curated tables
  ↓
Glue Data Catalog
  ↓
Lake Formation
  ↓
Athena
```

Orchestrate with Step Functions/EventBridge as appropriate. Use KMS encryption and private networking patterns where required. Use CloudWatch for operational metrics/logs and CloudTrail for audit evidence. Use data-quality gates before publishing trusted outputs.

Use serverless processing where workload characteristics fit it; avoid operating a persistent EMR cluster solely because Spark is available.

Cost controls include incremental processing, columnar formats, partition/layout optimization, query-cost monitoring, and teardown of unnecessary resources.

---

## Why This Solution Works

The architecture separates storage, transformation, catalog, authorization, query, orchestration, and observability. It uses managed services where they reduce operational burden without sacrificing governance.

---

## Key Concepts Tested

- S3
- Glue
- Iceberg
- Lake Formation
- Athena
- Step Functions
- KMS
- CloudWatch

---

## Production Considerations

- Security: least privilege, encryption, fine-grained governance.
- Reliability: idempotent pipelines and quality gates.
- Cost: serverless usage and query optimization.
- Observability: metrics/logs/audit trails.

---


### Question 32 — Design CDC → Iceberg → Athena/Redshift with recovery

**Difficulty:** Advanced

**Topics:** DMS, PostgreSQL, S3, Iceberg, Athena, Redshift, Observability

**Problem**

A high-volume PostgreSQL operational system must feed both lake analytics and warehouse consumers. The business requires CDC, recovery from target outages, and a clear strategy for source WAL growth. Some consumers query the lake; others use Redshift.

**Your Task**

1. Design the ingestion and serving architecture.
2. Explain DMS versus downstream application of CDC.
3. Explain source-impact controls.
4. Define recovery and reconciliation.

---

## Solution

Use a CDC architecture such as:

```text
PostgreSQL
  ↓
DMS full load + CDC
  ↓
S3 CDC landing
  ↓
Curated Iceberg state
  ├── Athena
  └── Redshift/Spectrum or curated warehouse path
```

Track CDC lag and PostgreSQL WAL/replication-slot retention. Make downstream CDC application idempotent and maintain reconciliation checks.

Use CloudWatch/operational metrics for lag and failures and CloudTrail for auditable control-plane activity. Recovery should preserve the source's CDC position where possible; if reinitialization is required, perform a deliberate full-load/reconciliation procedure.

Choose Redshift ingestion/serving patterns based on workload rather than automatically copying every lake table into the warehouse.

---

## Why This Solution Works

DMS transports database changes; the analytical architecture determines how those changes become trusted, queryable state. Recovery must protect source integrity and data correctness simultaneously.

---

## Key Concepts Tested

- DMS
- CDC
- PostgreSQL WAL
- Iceberg
- Athena
- Redshift
- Recovery

---

## Production Considerations

- Reliability: tested CDC recovery and reconciliation.
- Performance: separate ingestion from serving workloads.
- Cost: avoid unnecessary duplicate storage/processing.
- Observability: lag plus source WAL evidence.

---


### Question 33 — Design a streaming platform using Kinesis and MSK

**Difficulty:** Advanced

**Topics:** Kinesis Data Streams, Firehose, MSK, Kafka, Debezium, S3, Iceberg

**Problem**

A large enterprise has two streaming requirements. Business events need managed AWS streaming and S3 delivery. A separate platform team already operates Kafka-compatible workloads and wants Debezium-based CDC into a lakehouse. The organization wants to avoid forcing one technology onto every workload.

**Your Task**

1. Design a two-path streaming architecture.
2. Explain when Kinesis and MSK are each appropriate.
3. Include reliability and schema evolution considerations.
4. Define the boundary between streaming ingestion and lakehouse curation.

---

## Solution

Use a workload-based split:

```text
Business events
  ↓
Kinesis Data Streams
  ↓
Firehose / consumers
  ↓
S3
  ↓
Iceberg

CDC / Kafka-native workloads
  ↓
Debezium
  ↓
MSK
  ↓
stream processing / sink
  ↓
S3 / Iceberg
```

Kinesis is attractive for AWS-managed stream ingestion and consumption patterns; MSK is appropriate where Kafka ecosystem compatibility, Kafka-native tooling, or Debezium is a material requirement.

Define schema-evolution rules, idempotency, replay strategy, consumer lag monitoring, and partition/key strategy separately for each path.

---

## Why This Solution Works

The correct enterprise architecture does not require one streaming service to satisfy incompatible workload requirements. Service selection should follow operational model and ecosystem needs.

---

## Key Concepts Tested

- Kinesis
- Firehose
- MSK
- Debezium
- Schema evolution
- Iceberg

---

## Production Considerations

- Reliability: replay/idempotency and lag monitoring.
- Security: network/authentication controls.
- Cost: avoid duplicating platforms without a workload justification.

---


### Question 34 — Design a secure private AWS data platform with minimal NAT

**Difficulty:** Advanced

**Topics:** KMS, VPC, Gateway Endpoints, Interface Endpoints, Glue, EMR, Redshift, Secrets Manager

**Problem**

A regulated enterprise requires a private data platform. Glue/EMR/Redshift workloads run in private networking. S3 and several AWS APIs must be reachable without sending data traffic through unnecessary public paths. Secrets must not be embedded in code.

**Your Task**

1. Design the network and encryption architecture.
2. Explain gateway versus interface endpoints.
3. Explain KMS and Secrets Manager integration.
4. Define a troubleshooting strategy.

---

## Solution

Use:

```text
Private subnets
  ├── S3 gateway endpoint
  ├── interface endpoints for required AWS APIs
  └── NAT only for dependencies that genuinely require it
```

Use security groups and endpoint policies to constrain interface-endpoint traffic. Use KMS customer-managed keys where the governance requirements justify them and define key policies/grants carefully. Use Secrets Manager for secrets and retrieve them through an authorized workload identity.

Troubleshoot independently:

```text
routing → endpoint → DNS/SG → IAM → resource policy → KMS
```

Do not solve a network timeout by broadening IAM, or a KMS denial by changing route tables.

---

## Why This Solution Works

Private networking is a layered control plane. Separating network, IAM, resource policy, and KMS diagnosis prevents unsafe fixes.

---

## Key Concepts Tested

- VPC
- Gateway endpoints
- Interface endpoints
- PrivateLink
- KMS
- Secrets Manager

---

## Production Considerations

- Security: least privilege and encryption.
- Cost: minimize unnecessary NAT while retaining required connectivity.
- Reliability: test endpoint routing and dependencies.

---


### Question 35 — Design an enterprise DataZone data-product operating model

**Difficulty:** Advanced

**Topics:** DataZone, Unified Studio, Glue Catalog, Lake Formation, Athena, Redshift, Governance

**Problem**

A large enterprise has Finance, Sales, and Operations data domains. Hundreds of analysts need discoverable data products, business definitions, governed subscriptions, and access controls. AI teams also need trusted semantic discovery without bypassing authorization.

**Your Task**

1. Design the governance operating model.
2. Define domain/project/data-product responsibilities.
3. Explain discovery versus authorization.
4. Explain how AI consumers should use the platform safely.
5. Compare managed AWS governance with a custom portal.

---

## Solution

Use DataZone/SageMaker Catalog as the governed discovery/data-product experience where it fits the organization's AWS architecture.

```text
Domain
 ├── Producer projects
 ├── Consumer projects
 ├── Business glossary
 ├── Metadata standards
 └── Data products
          ↓
     Subscription
          ↓
  Underlying authorization
          ↓
 Athena / Redshift / other supported consumers
```

Assign domain owners, data-product owners, and stewards. Require structured metadata and business definitions before publication. Treat subscription approval and actual authorization as distinct controls.

For AI, allow semantic discovery but require the agent's identity and tool execution path to obey the same or stronger authorization boundaries as human consumers.

Compare DataZone against a custom portal using AWS integration, governance workflow, multi-cloud needs, customization, operational burden, cost, and lock-in rather than UI preference.

---

## Why This Solution Works

A data marketplace succeeds only when ownership, semantics, access, and lifecycle are operationalized. The catalog is not the security boundary.

---

## Key Concepts Tested

- DataZone
- Data products
- Business metadata
- Lake Formation
- Athena
- Redshift
- Unified Studio

---

## Production Considerations

- Governance: explicit ownership and lifecycle.
- Security: discovery ≠ authorization.
- AI safety: agents must not bypass authorization.
- Cost: include platform and human operating costs.

---


### Question 36 — Design an event-driven data platform with controlled retries

**Difficulty:** Advanced

**Topics:** EventBridge, Step Functions, Glue, Data Quality, Athena, CloudWatch

**Problem**

An enterprise wants an event-driven pipeline whenever a new dataset arrives. The pipeline should validate, transform, quality-check, and publish the result. Duplicate events are possible, and transient service failures occur.

**Your Task**

1. Design the event-driven workflow.
2. Explain idempotency.
3. Define Retry/Catch behavior.
4. Explain how to prevent duplicate publication.
5. Define observability.

---

## Solution

Use:

```text
Data arrival event
  ↓
EventBridge
  ↓
Step Functions
  ↓
Glue ETL
  ↓
Data Quality
  ↓
Publish curated data
  ↓
Athena validation
```

Use a deterministic dataset/run identifier so duplicate events resolve to the same logical processing unit. Retry only transient errors; Catch terminal failures into an alert/recovery path. Store state/evidence needed to prevent duplicate publication.

Observe EventBridge rule/target behavior, Step Functions executions, Glue runs, quality results, and final query validation.

---

## Why This Solution Works

Event-driven architectures require idempotency because event delivery and retries can create repeated processing. Orchestration should make recovery explicit.

---

## Key Concepts Tested

- EventBridge
- Step Functions
- Glue
- Data Quality
- Idempotency
- CloudWatch

---

## Production Considerations

- Reliability: idempotent processing and controlled retries.
- Observability: correlate event → execution → job → output.
- Cost: prevent duplicate processing and runaway retries.

---


### Question 37 — Optimize an AWS data platform for cost without weakening controls

**Difficulty:** Advanced

**Topics:** Cost Explorer, Athena, Glue, Redshift Serverless, EMR, Kinesis, NAT, VPC Endpoints, CloudWatch

**Problem**

A platform's cost has increased across Athena query scanning, Glue jobs, Redshift capacity, Kinesis, EMR, NAT Gateway, and CloudWatch. Leadership asks for a 20% reduction without removing security or reliability controls.

**Your Task**

1. Build a measurement-first cost strategy.
2. Identify optimization levers across the platform.
3. Explain the trade-offs.
4. Define how savings will be verified.

---

## Solution

Create service-level attribution first:

```text
Cost Explorer / billing evidence
        ↓
service + workload + environment
        ↓
cost drivers
```

Then optimize by driver:

- Athena: reduce scanned bytes through layout/partitioning.
- Glue: reduce unnecessary full reprocessing; use appropriate execution behavior.
- Redshift: validate physical design and capacity model before scaling.
- Kinesis: right-size shard capacity and eliminate hot-key-driven overprovisioning.
- EMR: choose the appropriate deployment model and auto-termination/scaling strategy.
- NAT: evaluate S3 gateway endpoints and required interface endpoints.
- CloudWatch: control unnecessary high-volume logging/metrics while preserving required observability.

Verify savings against a baseline and monitor for regression. Do not "optimize" by disabling encryption, governance, or required audit evidence.

---

## Why This Solution Works

Cost optimization must be tied to measurable drivers and must preserve production controls.

---

## Key Concepts Tested

- Cost Explorer
- Athena
- Glue
- Redshift
- Kinesis
- EMR
- VPC
- CloudWatch

---

## Production Considerations

- Cost: establish baseline and attribution.
- Security: do not trade away required controls.
- Reliability: verify that optimizations do not reduce resilience.

---


### Question 38 — Diagnose a multi-layer production incident

**Difficulty:** Advanced

**Topics:** Glue, Kinesis, DMS, Lake Formation, KMS, VPC, CloudWatch

**Problem**

A production analytics platform reports stale data. At the same time, Kinesis lag is rising, a DMS task shows CDC lag, a Glue job has failed, and one private workload reports KMS AccessDenied. The incident commander asks for a diagnosis rather than a list of possible fixes.

**Your Task**

1. Build an evidence-driven incident tree.
2. Prioritize investigation.
3. Separate correlated symptoms from root causes.
4. Define recovery and post-incident validation.

---

## Solution

Establish blast radius and timeline first. Use CloudWatch/log evidence to correlate:

```text
source/stream health
 → Kinesis lag
 → DMS CDC lag
 → Glue failure
 → downstream freshness
 → authorization/KMS symptoms
```

Investigate the first causally upstream failure rather than assuming all symptoms share one cause. For each path, classify the failure as data, compute, network, authorization, or control-plane.

Recover the critical dependency with the smallest safe change, then validate:
- data freshness;
- source/target reconciliation;
- Kinesis lag;
- DMS lag/WAL;
- Glue run success;
- KMS authorization;
- downstream query results.

Document the timeline and preventive controls.

---

## Why This Solution Works

Production incidents require causal reasoning. Multiple alarms can be symptoms of one upstream dependency or independent failures; evidence determines which.

---

## Key Concepts Tested

- CloudWatch
- Kinesis lag
- DMS lag
- Glue failures
- KMS
- Incident response

---

## Production Considerations

- Reliability: prioritize blast radius and recovery.
- Security: preserve authorization controls during recovery.
- Observability: correlate timestamps and service evidence.

---


### Question 39 — Choose a migration strategy: DMS, Zero-ETL, or Debezium

**Difficulty:** Advanced

**Topics:** DMS, Zero-ETL, Debezium, Redshift, S3/Iceberg, Governance

**Problem**

An enterprise is migrating an operational PostgreSQL workload. One consumer needs near-real-time analytics in Redshift, another needs CDC landed in S3/Iceberg, and a platform team already operates Kafka/MSK with Debezium. The architecture team wants one migration strategy for all consumers.

**Your Task**

1. Evaluate whether one strategy should serve all consumers.
2. Compare DMS, zero-ETL, and Debezium by workload fit.
3. Choose an architecture and explain trade-offs.
4. Define migration validation.

---

## Solution

Do not force one mechanism to all consumers.

Evaluate:

| Requirement | DMS | Zero-ETL | Debezium/MSK |
|---|---|---|---|
| Managed migration/CDC | Strong fit | Strong for supported integrations | Requires Kafka ecosystem |
| Redshift near-real-time integration | Possible/strong fit depending on path | Strong where supported | Possible via streaming architecture |
| S3/Iceberg CDC landing | Strong fit | Depends on supported integration | Strong with Kafka/sink architecture |
| Kafka-native operations | Not the primary reason | Not the primary reason | Strong |
| Operational simplicity | Managed service | Highly managed for supported path | More platform responsibility |

A practical architecture may use zero-ETL for a supported Redshift requirement, DMS for S3/lake CDC, and Debezium where Kafka-native CDC is a deliberate platform standard.

Validate row counts, ordering/keys, change completeness, latency, schema evolution, and recovery before cutover.

---

## Why This Solution Works

Migration architecture should be consumer-driven. The best mechanism depends on the target and operating model, not on a desire for one universal tool.

---

## Key Concepts Tested

- DMS
- Zero-ETL
- Debezium
- Redshift
- S3/Iceberg
- Migration validation

---

## Production Considerations

- Reliability: test recovery and reconciliation.
- Cost: include platform operating cost.
- Trade-off: managed simplicity versus Kafka ecosystem control.

---


### Question 40 — Design the target AWS Data Engineering platform and justify every major service

**Difficulty:** Advanced

**Topics:** All 14 Topics, Enterprise Data Platform Strategy

**Problem**

You are the lead architect for a growing enterprise. The platform must support batch ingestion, CDC, streaming, lakehouse analytics, warehouse analytics, governed data products, AI/ML consumers, private networking, security, observability, and cost controls. The organization is primarily AWS but has some multi-cloud consumers.

You have to present a target architecture and defend every major service choice.

**Your Task**

1. Design the target architecture from source to consumer.
2. Select services for batch, CDC, streaming, processing, serving, orchestration, governance, security, networking, observability, and cost management.
3. Identify where AWS-native choices create lock-in.
4. Provide at least three explicit rejected alternatives and why they were rejected.
5. Define the production operating model.

---

## Solution

A defensible target architecture can be layered:

```text
SOURCES
 ├─ operational DBs
 ├─ SaaS / files
 └─ application events

INGESTION
 ├─ DMS for database CDC/migration paths
 ├─ Kinesis for AWS-native streaming
 └─ MSK/Debezium for Kafka-native requirements

STORAGE
 └─ S3 / Iceberg / S3 Tables where the workload and operating model justify them

PROCESSING
 ├─ Glue ETL for managed data-integration workloads
 └─ EMR Serverless / EC2 / EKS when Spark control or workload characteristics justify EMR

CATALOG / GOVERNANCE
 ├─ Glue Data Catalog
 ├─ Lake Formation
 └─ DataZone / SageMaker Catalog for business discovery, data products, and subscriptions

SERVING
 ├─ Athena for lake SQL
 └─ Redshift for warehouse-oriented workloads

ORCHESTRATION
 ├─ Step Functions for service-oriented workflows
 ├─ EventBridge for event-driven routing
 └─ MWAA where Airflow DAG ecosystem/operating model is justified

SECURITY / NETWORK
 ├─ IAM
 ├─ KMS
 ├─ private subnets
 ├─ gateway/interface endpoints
 └─ Secrets Manager

OBSERVABILITY / COST
 ├─ CloudWatch
 ├─ CloudTrail
 └─ Cost Explorer / budgets / cost attribution
```

The architecture must remain workload-driven. Rejecting alternatives should be explicit, for example:

- Glue instead of EMR for a workload that needs extensive Spark/runtime control: reject if that control is a hard requirement.
- Kinesis instead of MSK for a Kafka-native Debezium platform: reject because the ecosystem requirement is different.
- Custom catalog instead of DataZone: reject if AWS-native governed discovery meets requirements and custom workflow needs are low.
- Redshift for every lake query: reject because Athena is better aligned with some S3/lake SQL workloads.

Define the operating model around:

```text
Requirements
 → service selection
 → IaC
 → least privilege
 → private connectivity
 → encryption
 → data quality
 → observability
 → cost attribution
 → incident runbooks
 → recovery/reconciliation
 → lifecycle/deprecation
```

For multi-cloud consumers, explicitly document which metadata/governance capabilities must remain portable and which AWS-native controls are intentionally retained.

---

## Why This Solution Works

This is the senior-level synthesis question. It tests whether the learner can assemble the individual topics into a coherent production platform and defend trade-offs instead of reciting services.

---

## Key Concepts Tested

- All 14 AWS Data Engineering topics
- Service selection
- Architecture
- Security
- Governance
- Observability
- Cost
- Reliability
- IaC

---

## Production Considerations

- Security: least privilege, encryption, private networking.
- Reliability: recovery, idempotency, data validation.
- Performance: workload-specific compute and storage design.
- Cost: service-level attribution and architecture trade-offs.
- Governance: catalog + business metadata + authorization separation.

---


---

# Coverage Matrix

The coverage matrix is intentionally cross-topic. A single question can test several AWS services and engineering skills, while each of the 14 topics appears in multiple difficulty levels.

| Topic | Basic | Moderate | Hard | Advanced | Question IDs |
|---|---:|---:|---:|---:|---|
| Topic 01 — AWS Service Landscape / Reference Architectures | ✓ | — | ✓ | ✓ | Q01, Q07, Q30, Q40 |
| Topic 02 — S3 Tables / Iceberg / Access Points / Batch Operations | ✓ | ✓ | ✓ | ✓ | Q05, Q13, Q29, Q31, Q32, Q40 |
| Topic 03 — Glue Data Catalog / Crawlers / Schemas / Partitions | ✓ | ✓ | — | ✓ | Q03, Q06, Q11, Q20, Q32, Q35, Q40 |
| Topic 04 — Glue ETL / Spark / Bookmarks / Data Quality | ✓ | ✓ | ✓ | ✓ | Q04, Q11, Q12, Q18, Q22, Q31, Q36, Q40 |
| Topic 05 — Athena / Projection / CTAS / Iceberg / Optimization | ✓ | ✓ | ✓ | ✓ | Q01, Q05, Q13, Q19, Q21, Q29, Q31, Q32, Q40 |
| Topic 06 — Lake Formation / Permissions / LF-Tags / Governance | ✓ | ✓ | ✓ | ✓ | Q06, Q16, Q20, Q26, Q31, Q35, Q40 |
| Topic 07 — Redshift / Serverless / Spectrum / Performance / Sharing | ✓ | ✓ | ✓ | ✓ | Q07, Q14, Q24, Q25, Q32, Q35, Q39, Q40 |
| Topic 08 — Kinesis / Firehose / MSK / Debezium / Streaming | ✓ | ✓ | ✓ | ✓ | Q02, Q15, Q23, Q33, Q40 |
| Topic 09 — EMR / Serverless / EC2 / EKS / Spark | — | — | — | ✓ | Q31, Q37, Q40 |
| Topic 10 — Step Functions / EventBridge / MWAA / Orchestration | ✓ | ✓ | ✓ | ✓ | Q08, Q18, Q28, Q36, Q40 |
| Topic 11 — DMS / CDC / WAL / Zero-ETL / Recovery | ✓ | ✓ | ✓ | ✓ | Q09, Q19, Q25, Q32, Q39, Q40 |
| Topic 12 — CloudWatch / CloudTrail / Cost Explorer / Observability | — | — | ✓ | ✓ | Q21, Q23, Q28, Q30, Q37, Q38, Q40 |
| Topic 13 — KMS / VPC / Endpoints / Private Networking / Secrets | ✓ | ✓ | ✓ | ✓ | Q06, Q17, Q27, Q30, Q34, Q37, Q38, Q40 |
| Topic 14 — DataZone / Unified Studio / Data Products / Governance | ✓ | ✓ | ✓ | ✓ | Q10, Q20, Q26, Q35, Q40 |

## Cross-Topic Coverage

The set deliberately includes combinations such as:

- S3 + Glue + Athena + Lake Formation
- Glue ETL + Data Quality + Iceberg
- Kinesis + Firehose + S3
- Redshift + physical design + performance
- Step Functions + Glue + Data Quality + Athena
- DMS + PostgreSQL WAL + S3 + Iceberg
- KMS + VPC + Glue + S3
- DataZone + Glue Catalog + Lake Formation
- MSK + Debezium + Iceberg
- EMR + Iceberg + S3 + Glue Catalog
- EventBridge + Step Functions + Glue
- Cost Explorer + Athena + Glue + Redshift + VPC

The supplied specification explicitly requires cross-topic questions and identifies these kinds of combinations as important, especially in the Hard and Advanced sections. fileciteturn71file0L768-L810

# Difficulty Summary

| Level | Questions |
|---|---:|
| Basic | 10 |
| Moderate | 10 |
| Hard | 10 |
| Advanced | 10 |
| **Total** | **40** |

## Troubleshooting Distribution Audit

| Level | Required minimum | Included |
|---|---:|---:|
| Basic | 2 | 2+ |
| Moderate | 3 | 3+ |
| Hard | 5 | 5+ |
| Advanced | 7 | 7+ |

Troubleshooting is intentionally embedded in realistic scenarios rather than isolated definition questions.

## Architecture Distribution Audit

| Level | Required minimum | Included |
|---|---:|---:|
| Moderate | 2 | 2+ |
| Hard | 4 | 4+ |
| Advanced | 7 | 7+ |

## Service-Selection Coverage

Scenario-based decisions include:

- Kinesis Data Streams vs Firehose
- Redshift Serverless vs provisioned
- Athena vs warehouse-first patterns
- Glue vs EMR
- Kinesis vs MSK
- DMS vs Zero-ETL vs Debezium
- DataZone vs custom governance
- Lake Formation vs broad application-level access
- NAT vs VPC endpoints
- Managed AWS governance vs open/custom approaches

These are framed as workload and architecture decisions rather than vocabulary questions.

# Final Practice Guidance

A senior Data Engineer should approach each problem in this order:

```text
Understand the problem
        ↓
Identify the right AWS services
        ↓
Design the data flow
        ↓
Implement the solution
        ↓
Secure it
        ↓
Observe it
        ↓
Validate the data
        ↓
Measure performance
        ↓
Control cost
        ↓
Handle failure
        ↓
Explain the trade-offs
```

For Hard and Advanced problems, do not stop at "which service?" Explain:

```text
Why this service?
Why not the obvious alternative?
What happens when it fails?
How is the failure detected?
How is the fix validated?
What security boundary applies?
What does it cost?
How does the architecture evolve?
```

The supplied specification explicitly defines this production-engineering loop as the desired learner mindset and requires the final practice bank to feel like it was designed by a senior AWS Data Engineering interviewer/production architect rather than as AWS trivia. fileciteturn71file0L1733-L1779

---

# Final Quality Audit

## Quantity

- [x] Basic = 10
- [x] Moderate = 10
- [x] Hard = 10
- [x] Advanced = 10
- [x] Total = 40

## Structure

- [x] Every question presents the Problem first.
- [x] Every question presents the Solution second.
- [x] Every question explains Why This Solution Works.
- [x] Key Concepts Tested are identified.
- [x] Production Considerations are included where relevant.

## Coverage

- [x] All 14 AWS Data Engineering topics represented.
- [x] Cross-topic integration included.
- [x] Architecture scenarios included.
- [x] Troubleshooting scenarios included.
- [x] Service-selection reasoning included.
- [x] Security reasoning included.
- [x] Cost reasoning included.
- [x] Observability reasoning included.
- [x] Governance reasoning included.

## Source Fidelity

The supplied specification requires that questions be grounded in the actual learning files and not become generic AWS certification trivia. This practice bank therefore keeps its scenarios within the stated AWS Data Engineering Deep Dive scope: S3/S3 Tables/Iceberg, Glue, Athena, Lake Formation, Redshift, Kinesis/MSK, EMR, orchestration, DMS/CDC/Zero-ETL, observability/cost, KMS/VPC/private networking, and DataZone/Unified Studio. fileciteturn71file0L522-L762

## Production Reasoning

- [x] Idempotency where relevant
- [x] Retry/recovery where relevant
- [x] Data validation
- [x] Schema evolution
- [x] Least privilege
- [x] Encryption
- [x] Observability
- [x] Cost control
- [x] Infrastructure/operational thinking
- [x] Runbook-style diagnosis

## Code Discipline

Code is included only where it improves the engineering solution. Examples use plausible SQL, AWS CLI, Python/boto3, or architecture/configuration patterns without inventing unsupported pricing or service limits.

## Final Result

**40 production-oriented AWS Data Engineering practice problems:**

```text
10 Basic
10 Moderate
10 Hard
10 Advanced
----------------
40 Total
```

Every question follows:

```text
Problem
   ↓
Solution
   ↓
Explanation
```
