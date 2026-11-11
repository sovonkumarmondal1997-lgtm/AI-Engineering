# AWS Data Architecture Reference Patterns

> **Stage:** 2D — Data Architecture  
> **Module:** 08 — Cloud, Hybrid and Multi-Cloud Data Architecture  
> **Lesson:** 02 — AWS Data Architecture Reference Patterns  
> **Learning progression:** Beginner → Intermediate → Advanced  
> **Recommended effort:** 6–8 hours  
> **Scenario:** Northbridge Bank, a fictional organisation  
> **Primary specification:** `roadmap-Cloud-Hybrid-and-Multi-Cloud-Data-Architecture.md`, Topic 5.2  
> **Scope note:** The module roadmap describes this lesson's recommended scope. The target lesson and neighboring lesson files were planned files, not evidence of previously written requirements. This document implements the roadmap recommendations; it does not claim that empty files contained additional instructions.

---

## 1. Purpose: map capabilities, not product names

The goal of this lesson is to translate the **logical enterprise data platform** developed earlier in Stage 2D into a plausible AWS implementation. A logical platform describes capabilities and responsibilities; a physical architecture chooses services, configurations, identities, data locations, and operational processes that realise those capabilities.

A service catalogue answers, “What products are available?” Architecture answers:

- Which business capability is needed, and what outcome must it deliver?
- Which component owns each responsibility?
- How does data flow between components?
- Which identity is used at each hop, and what permissions does it have?
- What network path is used, and what boundary protects it?
- Where are data and metadata stored?
- What happens when a component is throttled, unavailable, misconfigured, or too expensive?
- Which service-specific dependency is accepted, and how would it affect future change?

AWS is one implementation option, not a universal winner. The right choice depends on workload fit, data governance, recovery objectives, cost, team skills, and operational constraints.

### Learning outcomes

After completing the lesson, you should be able to:

1. Map the logical platform's capability families to candidate AWS services.
2. Explain the responsibilities and integration points of those services.
3. Trace data from a source through ingestion, storage, transformation, governance, and consumption.
4. Evaluate lake-centric, warehouse-centric, lakehouse, and streaming-first patterns.
5. Assess security, reliability, scalability, cost, and operational responsibilities.
6. Identify provider-specific dependencies and document verification gaps.
7. Compare a serverless lake-query pattern with a provisioned warehouse pattern.
8. Produce an AWS capability map, traced-flow diagram, pattern comparison, and ADR.

### Prerequisites

Before continuing, review these concepts from earlier Stage 2D modules:

- Logical platform capabilities, data zones, planes, ownership, and tenant boundaries.
- Object storage, file formats, table formats, partitioning, and data lifecycle.
- Ingestion, change data capture (CDC), data contracts, schema evolution, and failure handling.
- Requirements and quality attributes such as freshness, latency, throughput, availability, RTO, and RPO.
- Shared responsibility, regions, availability zones, and cloud cost drivers from Topic 01.
- Beginner-level VPC/VNet, subnet, IAM, and private-endpoint vocabulary from Topic 05.

Do not begin by memorising service names. Begin with the capability inventory and map each capability to one or more candidate services.

---

## 2. The reusable capability framework

Use the same capability families when studying AWS, Azure, and GCP. That common framework makes comparison possible without assuming that products with similar names have identical behaviour.

| Logical capability family | Business/technical responsibility | AWS candidates to investigate | Questions before choosing |
|---|---|---|---|
| Ingestion and integration | Move data from databases, applications, files, APIs, and events into the platform | AWS Database Migration Service (AWS DMS), Amazon Kinesis, Amazon MSK, AWS Glue connectors and jobs; other services may fit specific sources | Batch or streaming? CDC semantics? Replay? Ordering? Backpressure? |
| Lake storage | Store raw and curated data durably | Amazon S3; S3 storage features/classes; table-storage options may be relevant | Format, lifecycle, retention, request pattern, replication, access boundary? |
| Transformation and processing | Validate, clean, join, enrich, aggregate, and materialise data products | AWS Glue, Amazon EMR, SQL in Amazon Athena or Amazon Redshift; select based on workload | Batch/stream? Runtime control? Dependencies? Data volume? |
| Metadata and discovery | Record schemas, table locations, partitions, ownership metadata, and discoverability | AWS Glue Data Catalog, crawlers and catalog APIs | Who owns schema changes? What is authoritative? How is drift detected? |
| Governance and data-lake permissions | Enforce data-access policy and support governed sharing | AWS Lake Formation plus IAM, S3 policies, and service-specific controls | Are permissions enforced for every access path? Is direct S3 access possible? |
| Interactive lake query | Query data in S3 without maintaining a conventional always-on warehouse for every workload | Amazon Athena | Scan volume, file layout, concurrency, latency, query-results location, cost controls? |
| Data warehouse and BI analytics | Serve repeated SQL analytics with managed warehouse capabilities | Amazon Redshift; Athena or other serving options may also fit | Workload shape, concurrency, latency, isolation, loading strategy, cost? |
| Large-scale processing | Run distributed processing with runtime/framework control | Amazon EMR, AWS Glue, and service-specific serverless options | Does the team need cluster/runtime control? Who patches and tunes? |
| Workflow orchestration | Coordinate dependencies, retries, branches, and error handling | AWS Step Functions, Amazon MWAA, AWS Glue workflows and job triggers | State model, retry semantics, scheduling, backfills, observability? |
| Identity and access | Authenticate principals and authorise actions | AWS IAM, role assumption, service roles, resource policies | Least privilege? Human versus workload identities? Cross-account boundary? |
| Encryption and key control | Encrypt data and manage key-use permissions and lifecycle | AWS Key Management Service (AWS KMS), service-managed encryption features | Who can use/manage keys? What happens if a key is disabled? |
| Network access | Restrict reachability and define private paths | VPC, subnets, security groups, routing, VPC endpoints/PrivateLink where supported | What is public, private, reachable, or blocked? Which service supports the desired path? |
| Monitoring and audit | Detect failures, latency, access events, resource pressure, and spend | Amazon CloudWatch, AWS CloudTrail, service-specific logs/metrics; cost tools | What signal indicates user impact? Who responds? Are logs themselves protected? |
| Consumption | Deliver data to reports, applications, ML/AI pipelines, and analysts | Amazon Redshift, Athena, BI integrations, APIs and application-specific serving layers | Freshness, access controls, concurrency, lineage, and support ownership? |

This is a **candidate map**, not a mandated stack. A capability may require several services, and one service may support multiple capabilities. Verify current service support and constraints for the exact region, engine version, integration mode, and account setup.

---

## 3. AWS data-platform architecture at a glance

### 3.1 Capability-level reference architecture

```text
   Source systems / producer boundary
   +---------------------------------------------------+
   | Core databases | SaaS/API | files | event streams |
   +---------------------------------------------------+
               | batch / CDC / events / APIs
               v
   +---------------------------------------------------+
   | Ingestion boundary                                |
   | AWS DMS | Kinesis | MSK | Glue connectors/jobs    |
   +---------------------------------------------------+
               |
               v
   +---------------------------------------------------+
   | Amazon S3 lake storage                            |
   | Raw/landing -> validated -> curated data products |
   +---------------------------------------------------+
               |                    |
               v                    v
   +----------------------+  +-------------------------+
   | AWS Glue processing  |  | Amazon EMR processing   |
   | ETL / Spark jobs     |  | Spark / Hadoop options   |
   +----------------------+  +-------------------------+
               |                    |
               +----------+---------+
                          v
   +---------------------------------------------------+
   | Metadata and governance (consulted by supported  |
   | paths; not a mandatory physical data-flow stage) |
   | Glue Data Catalog + Lake Formation + IAM policies |
   +---------------------------------------------------+
               | metadata / authorization context
               v                    v
   +----------------------+  +-------------------------+
   | Athena lake queries  |  | Amazon Redshift         |
   | ad hoc / exploration |  | warehouse / BI workloads|
   +----------------------+  +-------------------------+
               |                    |
               +----------+---------+
                          v
            Analysts / BI / applications / ML data

   Cross-cutting: IAM | KMS | network boundaries | audit
   CloudWatch | CloudTrail | cost allocation | recovery
```

This diagram shows logical responsibilities, not an exact deployment or a strictly sequential data path. The catalog and governance components are metadata and authorization services that are consulted by supported workflows; they are not necessarily a physical processing stage through which data files pass. The correct service combination depends on workload requirements. For example, a small batch pipeline may need neither a streaming service nor a distributed cluster; a warehouse-centric workload may load curated data into Redshift and use S3 as an ingestion/retention layer.

### 3.2 Trust and network boundaries

```text
[On-premises / source trust boundary]
          |
          | approved private or controlled connection
          v
[AWS ingestion account or workload boundary]
  - source-specific roles
  - ingestion logs and failure queue/path
          |
          | role-authorised write path
          v
[Data producer account / S3 data boundary]
  - raw bucket/prefix
  - curated bucket/prefix
  - bucket policies and encryption
          |
          | catalog and governance permissions
          v
[Catalog / governance boundary]
  - Glue Data Catalog metadata
  - Lake Formation grants where configured
  - IAM permissions for APIs and roles
          |
          | authorised query/processing role
          v
[Consumer workload boundary]
  - Athena / Redshift / EMR / Glue
  - query results, outputs, audit and monitoring
```

A “boundary” is a design concept; it may be implemented with separate AWS accounts, resource policies, IAM roles, network controls, governance grants, or a combination. Do not assume every reference design requires one account per box. Choose boundaries to match data sensitivity, blast radius, ownership, and operational capacity.

**Security distinctions to preserve:**

- Network reachability answers whether a request can reach an endpoint.
- IAM answers whether a principal may call an AWS API or perform an authorised action.
- S3 bucket/access-point policies can add resource-side restrictions.
- Lake Formation can govern access to registered catalog resources and underlying data through supported integrations.
- KMS key policies and IAM permissions govern key operations.
- A query engine's permissions do not automatically make every direct path to the underlying objects safe. Review and test each access path.

---

## 4. Ingestion and integration

Ingestion is the controlled movement of source data into the platform. It includes batch file delivery, API pulls, database migration, CDC, and event streams. The ingestion mechanism must match the source, freshness requirement, replay needs, ordering semantics, and failure model.

### 4.1 Batch ingestion

Batch ingestion collects a bounded set of records over a time interval or source snapshot and processes them together.

Typical uses:

- Daily settlement or regulatory files.
- Periodic exports from SaaS applications.
- Historical backfills.
- Source systems that do not expose a suitable event stream.
- Workloads where minutes or hours of latency are acceptable.

A batch design should specify the batch identifier, expected arrival time, completeness criteria, schema version, idempotency strategy, and late-arriving-data policy.

**Example flow:**

```text
Daily source export
  -> controlled landing path
  -> manifest / arrival validation
  -> schema and quality checks
  -> raw S3 prefix
  -> transformation
  -> curated output
  -> catalog update / query validation
```

Do not mark a batch complete merely because a file exists. Verify size or manifest, record count where possible, checksum if provided, schema, duplicate handling, and successful downstream publication.

### 4.2 Database migration and change data capture

AWS DMS is a candidate for database migration and ongoing replication/CDC scenarios. It can move data from supported source endpoints to supported targets, but endpoint support, data types, limitations, and task behaviour vary. Validate the source/target combination in the current DMS documentation before design approval.

CDC captures changes after an initial load or from a source change log, depending on the configuration. It is useful when a downstream platform must remain reasonably current without repeatedly extracting the full source table.

```text
Source database
   | initial load (if required)
   | change log / CDC stream
   v
AWS DMS replication task
   |
   v
Target (e.g. S3 or supported database/warehouse target)
   |
   v
Validation, deduplication, transformation and publication
```

Questions to answer:

- How does the source expose changes, and what permissions are required?
- What is the initial-load strategy?
- Can the task resume after interruption? From which checkpoint?
- How are deletes, updates, schema changes, and ordering represented?
- What happens if the source log retention is insufficient during an outage?
- How are duplicate or replayed records handled downstream?
- Which lag metric indicates the freshness objective is at risk?

Do not assume CDC means exactly-once end-to-end processing. The source, replication task, destination, and downstream consumers can have different delivery semantics. Design idempotent writes or deduplication using stable keys and change metadata.

**AWS DMS-to-S3 ordering and bucket caveats:** with the S3 target's default CDC file layout, changes are written into table-specific folders/files and should not be assumed to preserve transaction order across tables. If downstream processing requires transaction ordering, verify and configure the documented transaction-preserving S3 target settings, then test the ordering contract for the actual source and workload. Also test how updates, deletes, schema changes, and full-load records are represented; the target files are not automatically a fully materialised current-state table. AWS's current S3-target guide also documents a limitation advising against enabling S3 versioning on the DMS target bucket because it can cause endpoint-test timeouts. Account for this before combining DMS S3 targets with a native S3 replication/versioning design; do not assume the two features can be enabled together without validation. See the [AWS DMS S3 target documentation](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.S3.html).

### 4.3 Streaming ingestion: Kinesis and MSK

**Amazon Kinesis Data Streams** and **Amazon MSK** are different options for streaming architectures.

- Kinesis Data Streams is an AWS-managed streaming data service with AWS-specific APIs and scaling/configuration concepts.
- Amazon MSK is a managed service for Apache Kafka, suitable when Kafka ecosystem compatibility and Kafka-specific capabilities are important.

These are not drop-in equivalents. Compare producer/consumer interfaces, partitioning and ordering, retention, throughput/scaling model, delivery semantics, operational model, integration ecosystem, and cost. Check current product documentation for current limits and options.

| Decision dimension | Kinesis Data Streams candidate | Amazon MSK candidate |
|---|---|---|
| Main reason to investigate | AWS-native streaming integration and managed stream primitives | Kafka compatibility, Kafka ecosystem, existing Kafka skills/workloads |
| Consumer model | Kinesis-specific APIs and supported integrations | Kafka producer/consumer protocols and Kafka ecosystem |
| Partitioning | Shards/partition-key behaviour and current scaling options must be understood | Kafka partitions, brokers, replication and partition placement |
| Operational considerations | Service configuration, retention, consumer scaling, quotas | Kafka cluster/broker configuration, partition strategy, client behaviour and version lifecycle |
| Lock-in/portability | AWS-specific API and operational model can create coupling | Kafka protocol can improve ecosystem portability, but managed configurations and integrations still create dependencies |
| Cost drivers | Stream capacity/throughput, retention, consumers and related requests/features | Broker/serverless mode where applicable, storage, throughput, network transfer, and operational choices |

### 4.4 Batch versus streaming

| Dimension | Batch | Streaming |
|---|---|---|
| Latency | Minutes/hours or scheduled intervals | Seconds or lower-latency event flow, depending on design |
| Complexity | Easier replay and bounded execution in many cases | More state, ordering, late events, backpressure, and continuous operations |
| Cost shape | Can schedule compute only when needed | Continuous ingestion/processing may incur ongoing cost |
| Failure recovery | Re-run a batch if inputs and outputs are controlled | Checkpoints, offsets, retention windows, replay and idempotency are essential |
| Fit | Regulatory batch, periodic extracts, backfills | Fraud signals, near-real-time operational analytics, event-driven systems |
| Common trap | Incomplete/duplicate files or reruns that duplicate output | Assuming ordering/exactly-once across all downstream systems |

Choose the simplest pattern that meets the freshness objective. Streaming is not inherently better if the business only needs a daily result.

---

## 5. Amazon S3 as a lake foundation

Amazon S3 is commonly used as durable object storage for data lakes. It stores objects in buckets and keys; the object store is not by itself a relational database, a schema registry, a query engine, or a complete governance system.

### 5.1 Logical zones and data contracts

A common logical layout is:

```text
s3://<approved-bucket>/raw/<domain>/<dataset>/...
s3://<approved-bucket>/validated/<domain>/<dataset>/...
s3://<approved-bucket>/curated/<domain>/<data-product>/...
s3://<approved-bucket>/quarantine/<domain>/<dataset>/...
```

These paths are illustrative. Do not copy them as production naming standards without a domain, account, region, security, and retention convention.

- **Raw/landing:** source-aligned data, with provenance and ingestion metadata.
- **Validated:** data that passed structural and basic quality checks.
- **Curated:** documented data products ready for approved consumers.
- **Quarantine:** invalid or suspicious records isolated from normal consumption.

Define each zone's owner, permitted writers/readers, retention, schema-evolution policy, encryption, quality gates, and recovery expectations. Folder names alone do not enforce access control.

### 5.2 File layout and query performance

For analytical workloads, format and layout affect scan volume, latency, and cost.

- Columnar formats such as Parquet can allow engines to read selected columns rather than entire row-oriented records.
- Partitioning can reduce scanned data when queries filter on partition keys, but excessive small partitions create metadata and file-management overhead.
- Too many tiny files increase scheduling and metadata overhead; overly large files may limit parallelism or create uneven work.
- Compression reduces stored/transferred bytes in many cases but costs CPU and can affect query behaviour.
- Table formats such as Apache Iceberg add table metadata and transactional/evolution capabilities over data files; support differs by engine and operation.

Do not choose a partition key only because it exists. Evaluate common predicates, cardinality, skew, update patterns, and the maintenance process. Detailed file/table-format design is covered in the earlier storage-architecture module.

### 5.3 Lifecycle, retention, and replication

Storage classes and lifecycle rules can reduce cost for data accessed less frequently, but retrieval charges, minimum-duration rules, access latency, and feature differences may apply. Check current S3 documentation and pricing for the exact storage class and use case.

Retention is a policy decision, not just a cost optimisation. Before deleting or tiering data, verify legal holds, audit needs, reproducibility, recovery objectives, and downstream dependencies.

Replication can support recovery or distribution, but introduces cost, lag/consistency considerations, permissions, and potential residency implications. For native S3 replication, source and destination buckets must have versioning enabled, and the replication role and KMS permissions (when applicable) must be correct. **Important integration caveat:** AWS DMS's S3-target guide currently advises against enabling versioning on the DMS target bucket because it can cause endpoint-test timeouts. Therefore, do not assume a DMS target bucket can also be used directly as the versioned source for native S3 replication; validate the exact current DMS/S3 design. One possible pattern to evaluate is a dedicated DMS landing bucket followed by a controlled, validated copy/publication into a separately versioned recovery or curated bucket, with the copy process's completeness, idempotency, cost, and RPO explicitly tested. Replication alone does not protect against every logical deletion or corruption scenario if the same change is replicated. Consider retention controls, protected backups, or a separately controlled recovery copy according to the threat model; test restoration rather than assuming replication is backup. See [S3 replication requirements](https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication-requirements.html), [S3 Versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html), and the [AWS DMS S3 target limitations](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.S3.html).

---

## 6. Processing and transformation

### 6.1 AWS Glue

AWS Glue is a managed data integration service with ETL capabilities. AWS Glue Data Catalog is its metadata component; these names are related but not interchangeable.

Use Glue as a candidate when the workload fits its supported integration and runtime model and the team values managed execution. Validate the required connector, runtime, table format, dependency, network path, and security configuration.

Typical responsibilities include:

- Extracting from supported sources or reading files in S3.
- Transforming records and writing outputs.
- Running Spark-based or other supported job types, depending on the chosen Glue capability.
- Crawling selected data to infer schema and populate catalog metadata.
- Integrating with orchestration and monitoring.

Do not assume a crawler is a complete data-quality system. Schema inference can be wrong or unstable when samples vary; critical schemas should have explicit ownership, validation, and controlled evolution.

### 6.2 Amazon EMR

Amazon EMR is a candidate for distributed data processing when teams need particular frameworks, runtime control, ecosystem compatibility, or cluster-level tuning. Exact deployment options and supported frameworks vary by EMR offering and version.

Trade-offs to consider:

- More runtime and cluster control can help specialised workloads.
- More control can mean more decisions about configuration, dependency compatibility, capacity, tuning, and operations.
- Persistent clusters may waste capacity when idle; ephemeral jobs or managed/serverless options may change that cost/operations balance.
- The team must plan upgrades, security patches, logs, failure recovery, and workload isolation according to the chosen deployment model.

Do not choose EMR solely because data volume sounds “big.” Compare it with Glue and other options using measured workload needs, team skills, runtime requirements, and total cost.

### 6.3 Processing contract

Every production transformation should define:

- Input data contract and schema version.
- Output contract and publication path.
- Deterministic or idempotent behaviour where feasible.
- Quality checks and rejected-record behaviour.
- Retry policy and the boundary of a retryable unit.
- Checkpoint/watermark handling for incremental processing.
- Logging and metrics without leaking sensitive values.
- Runtime and resource expectations.
- Owner and support escalation.

A job that exits with status zero but silently drops malformed records is not a reliable data product. Track rejected counts, expected counts, freshness, schema failures, and publication success.

---

## 7. Catalog, metadata, governance, and access

### 7.1 AWS Glue Data Catalog

The Data Catalog stores metadata about data assets—such as database/table definitions, schema and location information, and partitions—so integrated engines can discover data. It does not normally store the underlying S3 data itself.

The Data Catalog is regional: each AWS account has a Data Catalog in each AWS Region, so verify the region and account boundary in which catalog objects exist. Cross-account sharing and federation require explicit configuration and should not be assumed to happen automatically. A data lake recovery plan must explicitly recreate or recover the required catalog databases, tables, partitions, resource links, and related configuration in the recovery Region; do not assume S3 replication also replicates Glue Data Catalog metadata or Lake Formation grants. See [AWS Glue resource ARNs and regional catalog scope](https://docs.aws.amazon.com/glue/latest/dg/glue-specifying-resource-arns.html).

A catalog table is a metadata description, not proof that the underlying data are correct, current, authorised for every user, or physically available.

### 7.2 AWS Lake Formation

AWS Lake Formation provides data-lake governance capabilities that work with the Glue Data Catalog and supported analytics services. It can provide fine-grained permissions for registered data resources through supported integrations. It augments rather than replaces IAM.

**Critical limitation:** a governance grant protects access paths that are actually integrated with and governed by that model. Direct access to S3 objects or unregistered resources may be controlled by IAM, bucket policies, access points, and other policies instead. Do not assume a Lake Formation table grant automatically blocks every possible direct object access path.

Before enabling fine-grained governance:

1. Identify the data locations and register them as required by the chosen governance design.
2. Define who administers the lake and who grants access.
3. Decide whether access uses named-resource permissions, LF-tags, or another supported approach.
4. Align IAM, S3 resource policies, KMS key policies, and Lake Formation grants.
5. Test allowed and denied access through every intended engine and direct-storage path.
6. Audit changes and review permissions periodically.

### 7.3 IAM, resource policies, and KMS

IAM policies generally grant or deny API actions to identities; resource policies can constrain access to resources; service-specific governance systems can add further checks. A successful request may depend on several layers, and explicit denies or missing permissions can block it.

Use workload roles rather than embedding long-lived credentials in code. Scope permissions to the necessary resources and actions. Separate ingestion, transformation, administration, and consumer roles.

KMS controls key usage and administration according to the selected key type and policy model. Encryption at rest is not a substitute for least privilege. A role may need permissions both to access the data service and to use the relevant key. Test key permissions and recovery behaviour; accidental key disablement or loss of authorised access can make data unavailable.

---

## 8. Querying, warehousing, analytics, and serving

### 8.1 Amazon Athena

Athena is a managed serverless query service commonly used to query supported data formats in S3 with SQL. It integrates with the Glue Data Catalog for metadata and can integrate with Lake Formation for governed access on supported paths.

Typical fits:

- Ad hoc exploration of lake data.
- Infrequent or bursty SQL queries.
- Data validation and operational investigation.
- Some scheduled transformations or reporting queries, if performance and cost fit.

Important trade-offs:

- Query cost can depend on data scanned and the applicable pricing model.
- Poor file layout, unselective filters, or repeated full scans can increase cost.
- Concurrency, query execution behaviour, supported SQL features, and service limits must be checked for the actual workload.
- Query-result storage and its permissions/retention must be designed separately. Treat results as potentially sensitive data: an IAM principal with `s3:GetObject` access to the results location can retrieve result files directly even if `athena:GetQueryResults` is denied. Restrict the S3 results location independently, configure encryption and lifecycle/retention, and consider enforcing the result location through workgroup settings. See [Athena query-results access](https://docs.aws.amazon.com/athena/latest/ug/querying.html) and [workgroup result-location controls](https://docs.aws.amazon.com/athena/latest/ug/query-results-specify-location-workgroup.html).
- Serverless means the provider operates the underlying service; it does not mean unlimited concurrency, instant execution, or zero operational responsibility.

Cost controls include partitioning where appropriate, columnar formats, avoiding repeated scans, using workgroups and budgets/alerts where applicable, and measuring actual queries.

### 8.2 Amazon Redshift

Amazon Redshift is a data warehouse service for analytical SQL workloads. The exact architecture and operating model depend on the selected Redshift deployment/capability. Validate current features, scaling options, integrations, and limitations against the current documentation.

Consider Redshift when workload requirements favour warehouse-oriented serving, repeated analytical queries, controlled concurrency, data modelling, or a managed SQL analytics environment. It may coexist with an S3 lake; the architecture does not have to choose only one.

Trade-offs include capacity and workload management, data loading and refresh strategy, SQL/data-model compatibility, cost, and operational tuning. Do not assume a warehouse is automatically faster or cheaper than querying the lake; compare using representative query patterns and realistic data volumes.

### 8.3 Lake query versus warehouse

| Dimension | S3 + Athena-oriented pattern | Redshift-oriented pattern |
|---|---|---|
| Primary data location | Data files in S3, described by catalog metadata | Warehouse-managed storage and/or integrated access patterns depending on design |
| Typical fit | Ad hoc, exploratory, intermittent or lake-centric SQL | Repeated BI, managed warehouse analytics, workload/concurrency needs that fit Redshift |
| Cost drivers | Scanned data and applicable query/request/transfer charges | Capacity or consumption model, storage, data transfer, workload configuration and related charges |
| Performance levers | File format, partitioning, compression, data layout, query design | Data modelling, distribution/sort design where applicable, workload management, query design and capacity |
| Operational focus | Data layout, query guardrails, catalog and result location | Warehouse workload design, loading, concurrency, capacity and tuning |
| Governance | IAM, S3 controls, Glue Catalog and Lake Formation where configured | Warehouse permissions plus relevant lake/catalog permissions for integrated data |
| Risk | Repeated scans or poor layout create cost/latency surprises | Idle/overprovisioned capacity or poorly managed concurrency creates cost/performance issues |
| Decision evidence | Query volume, scan sizes, latency and concurrency tests | Representative benchmark, concurrency tests, refresh and cost model |

The comparison is intentionally high-level. Do not assume that one row describes every available deployment mode or feature. Verify service-specific pricing and functionality at decision time.

---

## 9. Orchestration and failure handling

Orchestration coordinates jobs and dependencies; it is not a replacement for the data-processing logic or a complete observability strategy.

### 9.1 AWS Step Functions

Step Functions is a candidate for explicit workflows with states, branches, waits, error handling, and service integrations. It can be useful when a workflow needs a clear state machine and operational visibility.

Use it when the workflow is well represented as a stateful sequence or graph of tasks. Verify current integration support, payload/state limits, retry/catch behaviour, execution mode, and pricing for the intended design.

### 9.2 Amazon MWAA

Amazon Managed Workflows for Apache Airflow (MWAA) is a managed Apache Airflow option for teams using DAG-based orchestration and the Airflow ecosystem. It can suit complex schedules, dependencies, and existing Airflow practices.

Managed Airflow still requires DAG engineering, dependency management, environment configuration, permissions, scheduling design, monitoring, and operational ownership. Check current version, networking, scaling, integration, and cost details.

### 9.3 Selecting an orchestrator

| Question | Step Functions candidate | MWAA candidate |
|---|---|---|
| Workflow model | Explicit state machine | Airflow DAGs and operators |
| Existing team skills | State-machine/service-integration skills | Airflow/Python and DAG operations skills |
| Service integrations | Verify the specific supported integration and semantics | Verify operators, hooks, provider packages and runtime compatibility |
| Operations | Workflow definition, retries, IAM, logs, execution behaviour | Environment, DAG parsing, dependencies, workers/scheduler, upgrades and logs |
| Common risk | Retrying a non-idempotent task can duplicate side effects | DAG/task retries and backfills can also duplicate side effects |
| Best decision input | Workflow shape, service integration, run cost and team familiarity | DAG complexity, ecosystem needs, existing skills and total operating cost |

Do not select an orchestrator solely based on popularity. Define the workflow contract, retries, timeout, idempotency, alerting, backfill, and recovery behaviour first.

### 9.4 Retry and idempotency

Retries are safe only when the operation can be repeated without creating unacceptable duplicate effects, or when duplicate effects are detected and reconciled.

A robust task design should specify:

- Which errors are retryable (for example transient throttling) and which require intervention (for example invalid schema or denied permissions).
- Backoff and maximum attempts appropriate to the failure type.
- A stable run/batch identifier.
- Atomic or staged publication where supported.
- Deduplication key and conflict policy.
- What state is recorded before and after success.
- How partial outputs are cleaned up or ignored.
- How alerts reach the owning team.

**Failure example:** a job writes half of a curated dataset and then fails. A blind retry appends the full dataset, doubling some records. Better options include writing to a run-specific staging location and publishing only after validation, using idempotent merge semantics where supported, or maintaining a deduplication key and reconciliation process.

---

## 10. Security, networking, and operational responsibility

This section establishes dependencies only; detailed network design belongs in `05-networking-identity-and-private-connectivity.md`, and hybrid integration belongs in Topic 06.

### 10.1 Minimum security review for a data flow

For every hop in a traced flow, record:

| Field | Example question |
|---|---|
| Source and destination | Which exact service/resource sends to which resource? |
| Principal | Which human or workload role performs the operation? |
| Required actions | Which API/resource operations are required? |
| Network path | Public endpoint, VPC path, service endpoint, or other supported path? |
| Data classification | What sensitivity level travels through this hop? |
| Encryption | What protects data in transit and at rest? Which key policy applies? |
| Audit | Which logs prove access and changes? |
| Failure signal | What metric/log/alert reveals failure or delay? |
| Owner | Who can diagnose and change the control? |

### 10.2 Example least-privilege policy shape

The following is a **deliberately incomplete teaching fragment**, not a deployable production policy. It demonstrates that permissions should be limited to a specific bucket/prefix and actions. It omits account-specific conditions, encryption requirements, explicit-deny strategy, and other policies that may be needed.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "WriteOnlyToIllustrativeRawPrefix",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::example-bank-raw/transactions/*"
    }
  ]
}
```

**Validation and safety notes:**

- Replace the example bucket and prefix with actual resources before use.
- This statement grants only the listed `PutObject` action on the specified object ARN pattern; it does not grant bucket listing or read access.
- A real ingestion role may need additional narrowly scoped actions depending on multipart upload, encryption, tagging, source integration, and the chosen service.
- KMS key use may require separate IAM and key-policy permissions.
- Bucket policy, service role trust policy, SCPs, permissions boundaries, VPC endpoint policies, and other controls can affect the final result.
- Do not attach a policy to production without testing both expected allow and deny cases in a non-production environment and reviewing it with the security owner.

### 10.3 Monitoring and incident handling

Use the appropriate service metrics and logs, CloudWatch for supported metrics/alarms/logs, and CloudTrail for supported API activity/audit events. Exact events, metric names, retention, and delivery behaviour vary by service and configuration.

Monitor outcomes, not just whether a service exists:

- Ingestion success, source lag, rejected records, and arrival delay.
- Job duration, failures, retries, resource pressure, and output row counts.
- Data freshness and quality at publication.
- Query latency, failed queries, scanned volume, and concurrency.
- Permission denials and unusual access patterns.
- Replication lag and backup/restore test results.
- Cost by domain, environment, workload, and unit of business outcome.

For each alert, specify severity, owner, runbook, escalation path, and the condition for closing the incident. Avoid logging secrets, raw credentials, or unnecessary sensitive record contents. Confirm which service events and metrics are actually emitted, their delivery/retention characteristics, and whether audit logging is enabled for the relevant account and Region; do not treat CloudTrail as a record of every data-plane event by default.

---

## 11. Reliability, scalability, and cost decisions

### 11.1 Reliability and disaster recovery

A managed service's own resilience features do not automatically make the whole data product resilient. The workflow may depend on a regional catalog, KMS key, role, network path, orchestration service, or an external source.

For every critical dataset, answer:

1. What are the required RTO and RPO?
2. What data and metadata must be restored?
3. Which identities, keys, network rules, catalog objects, workflow definitions, and secrets are required in the recovery environment?
4. Is the recovery location legally and contractually allowed?
5. Has recovery been tested with realistic data volume and dependencies?
6. What is the measured recovery point and elapsed recovery time?

Zone resilience and cross-region recovery are distinct. A region-level event can affect multiple zones. Cross-region replication and backups introduce cost, operational complexity, and potential residency constraints. A backup that has never been restored is an assumption, not demonstrated recovery capability.

**Region and residency decision:** document the approved Region for source ingestion, primary storage, processing, catalog/metadata, query results, logs, backups, and replicas—not just the main S3 bucket. Verify that every required service and feature is available in that Region, and check where service control-plane metadata, support logs, or integrated services may be processed or stored under the applicable AWS documentation and contract. A regional design is not, by itself, proof of legal compliance; confirm the applicable law, contract, data classification, and regulator interpretation with the responsible legal/compliance owner. Do not replicate sensitive data to a recovery Region until that location is approved.

### 11.2 Scalability and service limits

Scaling behaviour and quotas are service-specific and may vary by account, region, deployment type, or configuration. Do not design against an assumed unlimited service.

Record the expected workload envelope:

- Normal, peak, and growth volumes.
- Event rate or records per batch.
- Concurrent users and queries.
- File counts and average file sizes.
- Transformation duration and memory/compute requirements.
- Retention, replication, and recovery volume.
- Quotas/limits that could be reached and the process to request increases or redesign.

A scale test should reveal bottlenecks across the entire path. Increasing processing capacity may not fix a slow source, an undersized stream, poor file layout, throttled API, or a metadata bottleneck.

### 11.3 Cost model

Build estimates from measured or explicitly assumed quantities and current official prices for the chosen region and service. Record the pricing-check date, Region, currency, usage tier/commitment assumptions, included and excluded line items, and whether taxes/support are excluded. Use the [AWS Pricing Calculator](https://calculator.aws/) and the relevant service pricing page; recheck the assumptions before approval because pricing models and options change. Typical drivers include:

- S3 storage volume, storage class, requests, retrieval, lifecycle transitions, replication, and transfer.
- Athena query volume and bytes scanned under the applicable pricing model.
- Glue job execution, worker/runtime choice, catalog/crawler activity, and related requests.
- EMR deployment/capacity, storage, data transfer, and underlying resources.
- Redshift compute/capacity, storage, concurrency and workload configuration.
- Kinesis throughput/retention/consumers or MSK brokers/storage/transfer depending on the chosen mode.
- DMS replication capacity, source/target costs, and ongoing operational needs.
- Step Functions state transitions or workflow execution; MWAA environment and supporting resources.
- CloudWatch logs/metrics/alarms, CloudTrail storage/analysis, KMS requests where charged, support, and egress.

### 11.4 Worked cost sketch (illustrative quantities, not prices)

Assume the Northbridge analytics team runs 40 Athena queries per day. A sample month has 30 days, and the average query scans 18 GB. These are **illustrative assumptions**, not benchmark or billing facts.

1. Monthly query count: \(40 \times 30 = 1{,}200\) queries.
2. Monthly scanned volume: \(1{,}200 \times 18 = 21{,}600\) GB.
3. If a better file layout and partition pruning reduce average scan volume by 60%, new average scan is \(18 \times 0.40 = 7.2\) GB.
4. New monthly scanned volume: \(1{,}200 \times 7.2 = 8{,}640\) GB.
5. Reduction in scanned volume: \(21{,}600 - 8{,}640 = 12{,}960\) GB, or 60% under the assumptions.

This is a quantity comparison, not a bill. The actual cost depends on the current pricing model, billing units, rounding, region, query engine, and other charges. Validate performance and correctness after layout changes; do not infer that a 60% scan reduction yields exactly a 60% total-bill reduction. For a price-backed estimate, multiply the applicable billable quantity by the price applicable to the selected Region and pricing model, then add material non-query costs; cite the official price source and date in the ADR. Do not insert a remembered or undated per-GB rate.

Cost guardrails:

- Use workload/query metrics and alerts.
- Apply data layout and incremental processing thoughtfully.
- Set retention/lifecycle policy based on approved requirements.
- Tag resources and assign shared costs transparently.
- Monitor data transfer and replication.
- Evaluate idle capacity versus variable consumption.
- Model low, expected, and high usage rather than one false-precision number.

---

## 12. Common AWS reference patterns

### Pattern A — Lake-centric, serverless query

```text
Sources -> ingestion -> S3 raw -> transform/curate -> Glue Data Catalog
                                              |
                                              v
                                        Athena SQL
                                              |
                                              v
                                         BI / analyst
```

**Good fit:** exploratory and intermittent analytics, lake-centric datasets, workloads that benefit from querying data in S3 without operating a conventional warehouse for every query.

**Risks:** unbounded scans, poor partition/file layout, concurrency or latency that does not fit, weak governance, and forgotten query-result storage.

**Controls:** query-cost visibility, workgroups and limits where supported, format/layout optimisation, Lake Formation/IAM design, and freshness/quality monitoring.

### Pattern B — Warehouse-centric analytics

```text
Sources -> ingestion/ELT -> staging/curated data -> Redshift
                                                   |
                                                   v
                                               BI/reporting
```

**Good fit:** repeated BI and SQL workloads where warehouse capabilities, workload management, and serving behaviour fit the requirements.

**Risks:** idle/overprovisioned capacity, slow or fragile loads, data-model mismatch, concurrency issues, and additional data copies.

**Controls:** workload-based sizing, representative benchmarks, controlled refresh, workload monitoring, and a cost model that includes operations.

### Pattern C — Lakehouse-style storage and processing

```text
Sources -> S3 data files + table metadata
                    |
                    v
          Glue / EMR / supported engine
                    |
                    v
       Catalog + table format + governance
                    |
                    v
        Athena / EMR / other compatible engines
```

**Good fit:** teams seeking data-lake economics and multiple compute engines while needing table-level capabilities such as schema evolution or transactional semantics provided by a supported table format.

**Risks:** different engines may support different operations or versions; catalog, governance, compaction, and concurrency semantics need validation.

**Controls:** choose a table format and supported engine matrix deliberately; test reads, writes, schema evolution, maintenance, permissions, and recovery. Do not assume “open format” means all engines support all operations identically.

### Pattern D — Streaming-first event platform

```text
Applications / databases
       | events or CDC
       v
Kinesis Data Streams OR Amazon MSK
       |
       +--> stream consumers / near-real-time processing
       |
       +--> S3 archive / replayable history
       |
       v
Curated data products -> operational analytics / alerts / ML features
```

**Good fit:** event-driven systems with freshness requirements that justify continuous ingestion and processing.

**Risks:** partition/ordering issues, consumer lag, backpressure, retention limits, replay duplicates, schema evolution, and higher operational complexity.

**Controls:** event contracts, stable keys, lag alarms, idempotent consumers, retention/replay strategy, and clear ownership of poison messages and recovery.

### Pattern E — Cross-account governed data sharing

```text
Producer account                       Consumer account
+-------------------+                 +--------------------+
| S3 data + catalog | -- governed --> | Athena/EMR/Redshift |
| Lake Formation    |                 | consumer role       |
+-------------------+                 +--------------------+
                 Central or shared governance as designed
```

**Good fit:** a domain produces a trusted data product consumed by another team without creating unmanaged duplicate copies.

**Trade-offs:** governance configuration and cross-account policy design can be more complex than copying data. A copy may simplify consumer autonomy but creates duplicate storage, freshness, lineage, and revocation concerns.

**Controls:** explicit producer/consumer ownership, scoped cross-account grants, audited access, revocation tests, and documented data-product contracts. Validate current sharing capabilities and the exact services/regions involved.

---

## 13. Northbridge Bank: end-to-end traced flow

### 13.1 Scenario and assumptions

Northbridge Bank is fictional. For this lesson, assume:

- A core transaction database remains on premises during a phased migration.
- A daily batch is acceptable for regulatory reporting, while fraud analytics needs a lower-latency event path.
- Customer transaction records are sensitive and must remain in approved in-country locations under the scenario's internal policy. This is an illustrative policy assumption, not a statement of law.
- Raw data access is restricted to a small engineering group; analysts receive approved curated data.
- The platform team is small and prefers managed services where requirements fit.
- Current prices, regional service availability, quotas, and legal interpretations must be verified before production approval.

### 13.2 Batch reporting flow

```text
[On-prem core transaction database]
       |
       | source credentials / approved network path
       v
[AWS DMS task or approved batch export path]
       |
       | ingestion role; transfer status and lag monitored
       v
[S3 raw landing location]
       |
       | Glue job role reads raw, writes staging output
       v
[Validation + transformation]
       |
       +--> invalid records -> quarantine + alert
       |
       v
[S3 curated reporting dataset]
       |
       | metadata registered in Glue Data Catalog
       | Lake Formation grants (if selected/configured)
       v
[Athena query or Redshift warehouse]
       |
       | analyst/BI role with least privilege
       v
[Regulatory report / approved BI output]
```

For each hop, the design document must name the identity, network path, permission check, encryption/key dependencies, log/metric, and failure response. The diagram does not prove that a particular DMS source/target combination or network arrangement is supported; validate that configuration in current AWS documentation.

### 13.3 Streaming fraud flow

```text
[Transaction event producer]
          |
          v
[Kinesis Data Streams OR Amazon MSK]
          |
          v
[Consumer / streaming processing]
          |
          +--> low-latency fraud signal (approved serving path)
          |
          +--> S3 historical event archive
                     |
                     v
             curated analytics / replay
```

Select Kinesis or MSK based on source integration, event semantics, Kafka ecosystem requirements, operational skills, throughput model, retention, and cost—not by assuming the products are equivalent.

### 13.4 Trace worksheet

Complete one row for every transition.

| Hop | Responsibility | Identity | Network path | Failure signal | Recovery action |
|---|---|---|---|---|---|
| Source → ingestion | Extract/capture changes | Source-specific role/credential | Approved connection | Source lag/task status | Restore connectivity; resume/reconcile |
| Ingestion → S3 raw | Land source-aligned data | Ingestion role | Supported service path | Write failures/arrival delay | Retry safely; inspect partial objects |
| Raw → transform | Validate and transform | Job role | Service access to data/catalog | Job status, rejects, duration | Correct input/config; rerun idempotently |
| Transform → curated | Publish data product | Job role | S3 write path | Quality and publication checks | Stage output; publish after validation |
| Catalog/governance | Register metadata and grant access | Catalog/admin role | AWS API path | Permission/catalog errors | Correct scoped grant/config |
| Curated → query | Serve analytics | Consumer role | Approved service path | Query errors, freshness, cost | Correct access/layout/query |
| Query → report | Consume results | BI/app identity | Approved consumer path | Report failure/staleness | Re-run or use documented fallback |

---

## 14. Failure scenarios and responses

| Failure | Likely impact | Detection | Design response |
|---|---|---|---|
| DMS/ingestion task stops or lags | Stale downstream data | Task status, lag, expected-arrival alert | Diagnose source permissions/log retention/connectivity; resume and reconcile gaps |
| Batch arrives twice | Duplicate records | Batch ID, checksum, duplicate-key checks | Idempotent landing/publish logic; deduplicate and reconcile |
| Glue job fails midway | Partial output or missing partition | Job status, row counts, quality gates | Stage output, retry only safe units, publish after validation |
| Throttling or quota reached | Increased latency and retries | Service metrics and error classification | Bounded backoff, capacity/quota review, workload shaping |
| Schema changes unexpectedly | Parse failure or silent misinterpretation | Contract/schema validation | Quarantine, version contract, review backward compatibility |
| IAM or Lake Formation denial | Job/query fails despite network reachability | Access-denied logs and policy review | Identify exact principal/action/resource; grant minimum required access |
| Direct S3 access bypasses intended governance path | Data exposure | Access audit and access-path tests | Align bucket/IAM/key policies; restrict direct access where required |
| KMS key permission/configuration issue | Read/write or recovery failure | KMS/service errors and alarms | Restore authorised key policy/role access through change control |
| Zone or region event | Workload disruption or recovery delay | Service health, workload alarms | Follow tested recovery plan; validate data, metadata, keys, and identities |
| Query scans unexpectedly large data | Cost spike and latency | Query metrics, spend anomaly | Stop/limit harmful workload if safe; fix layout and add guardrails |
| Stream consumer falls behind | Late fraud signals and backlog | Consumer lag/age-of-data metrics | Scale within limits, resolve slow downstream, replay safely |
| Cross-account sharing fails | Consumer cannot access a data product | Access-denied logs and integration tests | Verify producer grants, consumer identity, catalog/resource policies, and supported integration |

Do not use retries to mask persistent configuration errors. Permission denial, schema incompatibility, and invalid data usually need correction rather than repeated execution.

---

## 15. Practical exercises

### Exercise A — Capability-to-service mapping

**Scenario:** Northbridge's logical platform needs an AWS option.

**Tasks**

1. Use the capability framework in Section 2.
2. Select a candidate service or mark a capability as a gap/decision pending.
3. Explain the service's responsibility in one sentence.
4. Name its upstream and downstream dependencies.
5. Record one assumption and one verification item per row.
6. Identify at least two AWS-specific dependencies the architecture accepts.

**Deliverable:** `northbridge-aws-capability-map.md`

**Validation:** every capability is mapped or explicitly marked as a gap; no unsupported service-equivalence claims; data owner, identity, network path, and failure signal are named for critical hops.

### Exercise B — Trace an end-to-end flow

Draw the batch reporting flow from Section 13.2. Annotate each hop with the identity, network path, data classification, encryption/key dependency, failure signal, and owner.

**Deliverable:** traced flow diagram and a table of unresolved questions.

### Exercise C — Serverless lake query versus warehouse

Compare two options for Northbridge's BI and ML workload mix:

- Option A: S3 curated datasets + Glue Data Catalog + Athena.
- Option B: S3 landing/curated layer + a Redshift-oriented serving warehouse.

Fix criteria before scoring: workload fit, latency, concurrency, governance, operations, cost, and recovery. Use illustrative usage assumptions first, then obtain current official prices for a dated estimate.

**Deliverable:** comparison table, cost sketch, and ADR.

**Validation:** include sensitivity analysis for query volume and scan volume. Explain which assumptions would change the decision.

### Exercise D — Batch versus streaming

Design a daily regulatory report and a lower-latency fraud signal. Decide which needs batch and which might justify streaming. Compare Kinesis and MSK only after documenting event rate, ordering, replay, retention, producer/consumer ecosystem, and team skills.

**Deliverable:** two diagrams and a decision note.

### Exercise E — Security review

Create a least-privilege review for ingestion, transformation, catalog administration, query, and analyst roles. Include S3, Glue, Lake Formation (if used), KMS, and audit paths.

Test both allowed and denied actions. Identify direct S3 access paths that could undermine intended table-level governance if left unrestricted.

**Deliverable:** role-permission matrix and test plan. Do not apply unreviewed policy changes to a production account.

---

## 16. Short ADR: choose a lake-query or warehouse-oriented pattern

The following is a **worked example using illustrative assumptions**, not a universal recommendation.

```markdown
# ADR-002: Initial serving pattern for Northbridge analytics

- Status: Proposed
- Context: A fictional bank needs governed analytics over curated data.
- Assumptions: Usage is initially spiky; analysts can tolerate the measured
  query latency; sensitive records remain in approved locations.
- Decision drivers: workload fit, governance, cost, latency, concurrency,
  operating skills, and recovery.

## Options
A. S3 + Glue Data Catalog + Athena.
B. S3 landing/curated layer + Amazon Redshift.
C. Hybrid serving: Athena for exploration, Redshift for selected BI products.

## Provisional decision
Evaluate Option A as the initial candidate for intermittent exploration,
but do not approve it until representative queries, scan volume, concurrency,
governance, and current pricing are measured. Consider Option C if recurring
BI workloads need different latency/concurrency behaviour.

## Rationale
Option A avoids requiring a warehouse for every exploratory query, but
its cost/performance depends on data layout and query behaviour. Option B
may better fit selected repeated analytical workloads but adds warehouse
capacity and data-refresh decisions. Option C separates workload classes
but increases operational and governance complexity.

## Consequences and risks
- Measure query scan volume, latency, concurrency, and cost.
- Enforce access and query-result controls.
- Maintain a documented owner for catalog, data layout, and permissions.
- Revisit if query volume, latency, concurrency, or cost crosses agreed
  thresholds.

## Validation plan
Run a representative workload in a non-production environment; document
data volume, query set, latency distribution, scanned volume, configuration,
current price sources, and assumptions. Review results with platform,
security, analytics, and finance stakeholders.
```

A sound ADR separates facts from assumptions, explains rejected options, and states the evidence that would trigger a review.

---

## 17. Review questions with answer guidance

Attempt each question before reading the answer guidance.

1. **Why should an AWS architecture begin with capabilities?**  
   *Guidance:* it preserves the business responsibility and makes comparison possible even when provider products differ.

2. **What is the difference between Amazon S3 and the Glue Data Catalog?**  
   *Guidance:* S3 stores objects/data; the catalog stores metadata that describes datasets and their locations/schemas.

3. **Does a Glue crawler guarantee schema correctness?**  
   *Guidance:* no. Inference can be unstable; critical schemas need contracts, validation, ownership, and controlled evolution.

4. **When would you investigate AWS DMS?**  
   *Guidance:* database migration or ongoing replication/CDC where the source/target and requirements are supported. Verify endpoint-specific limits and behaviour.

5. **How do Kinesis Data Streams and MSK differ architecturally?**  
   *Guidance:* Kinesis uses AWS-specific streaming APIs and service concepts; MSK provides managed Kafka. Compare protocol/ecosystem, partitioning, scaling, operations, and cost rather than treating them as equivalent.

6. **Why might Athena query cost increase suddenly?**  
   *Guidance:* larger scan volume, poor partition pruning/layout, repeated full scans, increased query volume, or other service-specific charges.

7. **When might Redshift be a better fit than lake-only querying?**  
   *Guidance:* when measured repeated BI/SQL workload, concurrency, latency, and serving requirements fit a warehouse model; validate rather than assume.

8. **What does Lake Formation add, and what does it not automatically guarantee?**  
   *Guidance:* it provides a governance/permissions model for supported integrated access paths; it does not automatically secure every direct or unregistered S3 access path.

9. **Why do IAM and KMS permissions need separate attention?**  
   *Guidance:* permission to call a data service and permission to use the encryption key are distinct checks; both identity and key policies may matter.

10. **Why is a retry not always safe?**  
    *Guidance:* a partially completed task may repeat side effects or duplicate records; use idempotency, staging, stable identifiers, and reconciliation.

11. **What must be included in a trace diagram?**  
    *Guidance:* responsibility, principal/identity, network path, data classification, failure signal, and recovery action for every critical hop.

12. **Why does cross-account data sharing require more than naming a consumer role?**  
    *Guidance:* producer grants, catalog/resource configuration, identity policies, supported service integrations, and audit/revocation behaviour must align.

13. **How do you make a cost comparison defensible?**  
    *Guidance:* date, region, usage quantities, current price sources, included/excluded charges, workload assumptions, uncertainty range, and measured workload evidence.

14. **What would you need to restore after a region failure besides data files?**  
    *Guidance:* catalog metadata, identities/policies, keys, network configuration, workflow definitions, secrets/configuration, monitoring, and tested access to recovery data.

15. **Name two AWS-specific dependencies you would record in an ADR.**  
    *Guidance:* examples include IAM policy structure, Lake Formation grants, Glue catalog semantics, a service-specific streaming API, or orchestration definitions. State the actual dependency used, not merely a service name.

---

## 18. Expected deliverables and mastery criteria

### Required deliverables

- [ ] AWS capability map with candidate service, rationale, assumptions, and verification items.
- [ ] End-to-end traced flow with identity and network path at every hop.
- [ ] AWS reference architecture diagram for one data domain, including account/data boundaries.
- [ ] Pattern comparison for lake-centric query versus warehouse-oriented serving.
- [ ] Cost sketch with assumptions, units, current price sources, and sensitivity analysis.
- [ ] Failure-handling notes for ingestion failure, retries, duplicates, permission errors, zone/region failure, and unexpected cost.
- [ ] ADR with options, rationale, trade-offs, risks, and revisit triggers.
- [ ] Inventory of at least two AWS-specific dependencies and their portability implications.

### Mastery criteria

You are ready to move to the Azure lesson when you can:

1. Map each logical platform capability to a candidate service and justify it.
2. Explain the responsibility and limitations of each major service used.
3. Trace a flow and name identity, network path, and failure signal at every critical hop.
4. Explain why direct S3 access and governed catalog access may follow different permission paths.
5. Compare two patterns using requirements, workload assumptions, cost, governance, and operational trade-offs.
6. State at least two AWS-specific dependencies without claiming unsupported equivalence with other clouds.
7. Explain what must be restored after a regional incident.
8. Find and verify service-specific details in official documentation instead of relying on memory.

### Completion gate

- [ ] Capability map, traced flow, and pattern ADR reviewed by another person.
- [ ] No “equivalent to X” claims without a verification note.
- [ ] Critical roles and data paths have named owners and access tests.
- [ ] Cost estimates show date, region, quantities, assumptions, and excluded charges.
- [ ] Weaknesses caused by memorising product names are addressed by remapping the logical platform from scratch.

---

## 19. Common mistakes and how to avoid them

| Mistake | Why it causes problems | Better practice |
|---|---|---|
| Memorising service names | Knowledge ages and does not explain architecture | Start from capability, responsibility, and requirements |
| Assuming a service does everything its name suggests | Hidden integration and operational limits remain undiscovered | Verify the exact feature, engine/version, region, and configuration |
| Ignoring account and permission structure | Creates excessive access and unclear ownership | Model identity and resource boundaries early |
| Assuming private networking means data is authorised | Reachability and permission are different controls | Test IAM, resource policies, governance grants, and key access |
| Assuming Lake Formation protects every S3 path | Direct/unregistered access may follow other policies | Test every intended and prohibited access path |
| Choosing serverless without cost guardrails | Query/usage spikes can produce surprise bills | Measure scans and use workload controls where available |
| Using retries without idempotency | Duplicate writes or partial outputs | Stage, validate, publish atomically where possible, and reconcile |
| Assuming CDC means exactly-once delivery | Duplicates, lag, and replay can occur across system boundaries | Define semantics and downstream deduplication |
| Treating a reference architecture as a mandate | Overfits one example to a different workload | State deviations and justify them against requirements |
| Assuming multi-zone means disaster recovery | Region-wide or shared-dependency failure may still stop the system | Define RTO/RPO and test recovery |
| Comparing prices without the same workload | Produces misleading provider/service conclusions | Use the same workload profile and include transfer and operations |
| Assuming an open table format means universal interoperability | Engine features and write semantics differ | Validate a supported engine/operation matrix |

---

## 20. Authoritative AWS documentation to consult

These official AWS sources support the concepts in this lesson. Service capabilities and constraints evolve; verify the current guide for the selected region, deployment mode, integration, and version before implementation.

1. [Amazon S3 User Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html) — object storage, access, lifecycle, and data protection.
2. [AWS Glue Developer Guide](https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html) — data integration and ETL responsibilities.
3. [AWS Glue Data Catalog documentation](https://docs.aws.amazon.com/glue/latest/dg/catalog-and-crawler.html) — catalog and crawler concepts.
4. [Amazon Athena User Guide](https://docs.aws.amazon.com/athena/latest/ug/what-is.html) — querying data with SQL and related controls.
5. [Amazon Redshift documentation](https://docs.aws.amazon.com/redshift/latest/mgmt/welcome.html) — warehouse capabilities and operating model.
6. [Amazon EMR documentation](https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-what-is-emr.html) — managed big-data processing options.
7. [Amazon Kinesis Data Streams Developer Guide](https://docs.aws.amazon.com/streams/latest/dev/introduction.html) — stream concepts and consumer models.
8. [Amazon MSK Developer Guide](https://docs.aws.amazon.com/msk/latest/developerguide/what-is-msk.html) — managed Apache Kafka.
9. [AWS DMS User Guide](https://docs.aws.amazon.com/dms/latest/userguide/Welcome.html) — database migration and replication/CDC.
10. [AWS Step Functions Developer Guide](https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html) — state machines and workflow orchestration.
11. [Amazon MWAA User Guide](https://docs.aws.amazon.com/mwaa/latest/userguide/what-is-mwaa.html) — managed Apache Airflow.
12. [AWS Lake Formation Developer Guide](https://docs.aws.amazon.com/lake-formation/latest/dg/what-is-lake-formation.html) — data-lake governance and supported fine-grained permissions.
13. [AWS IAM User Guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html) — identities and permissions.
14. [AWS KMS Developer Guide](https://docs.aws.amazon.com/kms/latest/developerguide/overview.html) — key management and key-use permissions.
15. [AWS CloudTrail User Guide](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html) — supported API activity and audit records.
16. [Amazon CloudWatch documentation](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html) — metrics, logs, alarms, and operational monitoring.
17. [AWS Prescriptive Guidance: Designing a data lake for growth and scale](https://docs.aws.amazon.com/prescriptive-guidance/latest/data-lake-for-growth-scale/introduction.html) — reference-architecture concepts for producer, consumer, catalog, and governance boundaries.

### Verification discipline

- The service list is a starting point, not a complete or permanently authoritative catalogue.
- Do not treat service names as proof of feature parity or interoperability.
- Verify current quotas, regional availability, pricing, supported integrations, security behaviour, and recovery semantics for the exact design.
- All Northbridge Bank details and numeric workload quantities are illustrative assumptions.
- Detailed provider networking, hybrid connectivity, portability/multi-cloud trade-offs, and infrastructure-as-code belong in the dedicated neighboring lessons.
- AWS should be selected only when its fit against the agreed requirements is supported by evidence.
