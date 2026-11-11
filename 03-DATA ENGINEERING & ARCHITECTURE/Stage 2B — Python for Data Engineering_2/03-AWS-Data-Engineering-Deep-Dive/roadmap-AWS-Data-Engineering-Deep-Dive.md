# Roadmap — Gap Module G3: AWS Data Engineering Deep Dive

This is the learning roadmap for the third gap module, **AWS Data
Engineering Deep Dive**. It tells you **what** to learn about building data
platforms on Amazon Web Services, **in what order**, **how** to learn each
topic, and **how to prove to yourself** that you have learned it before you
move on.

**When to take it:** after Stage 2 **Module 2.17** (Cloud Storage and Cloud
Data Platforms), ideally after Modules 2.18 and 2.20 as well. It is one of
two **alternative depth tracks** — choose this module **or** Gap Module G4
(Databricks), based on the jobs you are targeting. Employers usually expect
real depth in one platform.

**What this module is not:** it does **not** repeat Module 2.17's
cloud-neutral foundations (object storage concepts, basic S3 operations
with boto3, fsspec, IAM roles and least privilege, the warehouse
comparison, serverless basics with Lambda, managed Spark comparison,
storage classes and lifecycle rules), nor the engine internals from Modules
2.14–2.16 (Spark, Iceberg/Delta, Kafka). This module goes deep into the
**AWS-specific services** a data engineer uses every day, how they fit
together, and how to secure, operate, and pay for them.

> **Cost warning:** several services in this module bill by the hour
> whether you use them or not (Redshift provisioned clusters, EMR on EC2,
> MSK clusters, Kinesis shards, NAT gateways, interface VPC endpoints,
> Managed Workflows for Apache Airflow). Create everything with Terraform
> (Module 2.18), keep a teardown script, set budgets and alerts, and
> destroy resources after every study session. Check current pricing and
> free-tier terms before each topic.

> **Change warning:** AWS renames and extends services frequently (for
> example Amazon Data Firehose, Amazon Managed Service for Apache Flink,
> S3 Tables, and the next generation of Amazon SageMaker). Always confirm
> names, limits, and features in the current AWS documentation.

---

## 1. Module outcome

By the end of this module you will be able to:

- Map any data problem to the right AWS services and explain the trade-offs
  using reference architectures.
- Use advanced S3 capabilities for data lakes: **S3 Tables** (managed
  Iceberg), access points, and Batch Operations.
- Manage metadata with the **AWS Glue Data Catalog**, crawlers (and when to
  avoid them), and schema management.
- Build Spark and Python ETL with **AWS Glue**, including incremental
  processing and **Glue Data Quality**.
- Run fast, cheap SQL on the lake with **Amazon Athena**: partition
  projection, CTAS/UNLOAD, and Iceberg tables.
- Govern the lake with **AWS Lake Formation**: fine-grained and tag-based
  permissions and cross-account sharing.
- Design and operate **Amazon Redshift** (provisioned and Serverless),
  including Spectrum, data sharing, and workload management.
- Build streaming ingestion with **Kinesis Data Streams**, **Amazon Data
  Firehose**, and **Amazon MSK**.
- Choose and run **Amazon EMR** on EC2, on EKS, or Serverless.
- Orchestrate with **Step Functions**, **EventBridge**, and **MWAA**.
- Replicate operational databases with **AWS DMS** and **zero-ETL
  integrations**.
- Monitor, audit, and control cost with **CloudWatch**, **CloudTrail**, and
  AWS cost tools.
- Secure data with **KMS**, **VPC endpoints**, and private networking.
- Explain the **SageMaker Unified Studio** and **Amazon DataZone**
  direction for unified analytics and governance.
- Prepare for the **AWS Certified Data Engineer – Associate** exam.

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Remote servers, tunnels, command-line data tools | Gap Module G2 | Working with private resources and inspecting data |
| Containers | Gap Module G1, Module 2.18 | Local Glue development images, EMR on EKS awareness |
| SQL, `MERGE`, `EXPLAIN` | Module 2.6 | Athena and Redshift SQL |
| Data modelling | Module 2.8 | Redshift table design, lake layers |
| Ingestion patterns, CDC concepts | Module 2.9 | DMS, zero-ETL, Firehose |
| Data quality and contracts | Module 2.11 | Glue Data Quality |
| Orchestration | Module 2.13 | Step Functions and MWAA |
| **Spark** | Module 2.14 | Glue and EMR run Spark; tuning **not** re-taught |
| **Iceberg, catalogs, maintenance** | Module 2.15 | S3 Tables, Athena Iceberg, Glue as Iceberg catalog |
| **Kafka and streaming concepts** | Module 2.16 | MSK, Kinesis, Managed Flink |
| **S3, IAM, warehouses, Lambda, managed Spark, storage classes** | Module 2.17 | Foundations **not** re-taught |
| **Terraform, CI/CD, secrets managers** | Module 2.18 | Every resource here is created as code |
| Observability, governance, PII | Module 2.20 | CloudWatch, CloudTrail, Lake Formation |
| Performance and cost | Module 2.21 | Athena scan costs, EMR and Redshift sizing |

**Tools and accounts needed:**

- An AWS account used only for learning, with **MFA**, **IAM Identity
  Center (single sign-on)** or assumed roles (no long-lived access keys),
  **AWS Budgets** with email alerts, and cost allocation tags enabled.
- AWS CLI v2, Terraform (or OpenTofu), Python 3.12+ with `boto3`,
  `awswrangler` (AWS SDK for pandas — optional), `pyiceberg`, and `duckdb`.
- The AWS Glue local development container image (optional) for testing
  Glue jobs without paying for job runs.
- Your platform datasets from earlier Stage 2 modules (orders, customers,
  events) as sample data.

---

## 3. How the module is organised

The fourteen topics are grouped into five phases. Work through them **in
order**.

```text
Phase A — Landscape and Storage                       (Basics → Intermediate)
  01 AWS data services landscape and reference architectures
  02 S3 Tables, access points, and Batch Operations

Phase B — Catalog, Processing, and Query              (Intermediate)
  03 Glue Data Catalog, crawlers, and schema management
  04 Glue ETL jobs and Glue Data Quality
  05 Athena advanced: partition projection, CTAS, and Iceberg

Phase C — Governance and Warehousing                  (Intermediate → Advanced)
  06 Lake Formation permissions and governance
  07 Redshift deep dive: Serverless, Spectrum, and data sharing

Phase D — Streaming, Big Compute, Orchestration, Replication   (Advanced)
  08 Kinesis Data Streams, Firehose, and MSK
  09 EMR on EC2, EKS, and Serverless
  10 Step Functions, EventBridge, and MWAA orchestration
  11 DMS and zero-ETL integrations

Phase E — Operating, Securing, and Unifying           (Advanced)
  12 CloudWatch, CloudTrail, and Cost Explorer for data
  13 KMS, VPC endpoints, and private networking for data
  14 SageMaker Unified Studio and DataZone overview

Consolidate
  practice-questions.md
  interview-practice.md
  certification-prep-aws-data-engineer-associate.md
  Module mini-project: an AWS serverless lakehouse (→ Projects/03-aws-serverless-lakehouse.md)
```

The dependency chain:

```text
01 ► 02 ► 03 ► 04 ► 05 ► 06 ► 07 ► 08 ► 09 ► 10 ► 11 ► 12 ► 13 ► 14
map  store catalog process query govern warehouse stream compute orchestrate
                                                                replicate observe secure unify
```

Why this order:

- The landscape (01) prevents "service soup"; storage (02) and the catalog
  (03) are the foundation every other service reads from.
- Glue ETL (04) writes tables that Athena (05) queries; Lake Formation (06)
  then governs both — and Redshift (07) consumes the same catalog.
- Streaming (08), EMR (09), orchestration (10), and replication (11) are
  the advanced building blocks you connect to that foundation.
- Monitoring and cost (12), security networking (13), and the unified
  studio (14) apply across everything before them.

---

## 4. Suggested schedule

About **5–6 weeks at 8–10 hours per week**, plus 1–2 weeks of exam
preparation if you take the certification.

| Week | Work |
| --- | --- |
| 1 | Account safety and Terraform baseline · Topic 01 — landscape · Topic 02 — S3 Tables and access points |
| 2 | Topic 03 — Glue Data Catalog · Topic 04 — Glue ETL and Data Quality |
| 3 | Topic 05 — Athena advanced · Topic 06 — Lake Formation |
| 4 | Topic 07 — Redshift · Topic 08 — Kinesis, Firehose, MSK |
| 5 | Topic 09 — EMR · Topic 10 — orchestration · Topic 11 — DMS and zero-ETL |
| 6 | Topic 12 — monitoring and cost · Topic 13 — KMS and private networking · Topic 14 — unified studio · practice · mini-project |
| 7–8 (optional) | Interview practice · certification preparation |

---

## 5. How to study every topic (the AWS build loop)

```text
Read → Draw the architecture → Estimate the cost → Write it in Terraform
→ Deploy with least privilege → Run a realistic workload → Break it
→ Observe (metrics, logs, trail) → Measure cost → Tear down → Write it down
```

1. **Read** the topic file and the service's current AWS documentation
   ("what is", quotas, pricing).
2. **Draw** where the service sits in your platform and which services it
   talks to.
3. **Estimate the cost** of your exercise before creating anything.
4. **Write it in Terraform** (no console-only resources, except for
   exploring).
5. **Deploy with least privilege**: one role per workload (Module 2.17).
6. **Run a realistic workload** using your Stage 2 datasets.
7. **Break it**: missing permission, bad data, schema change, throttling,
   a failed job.
8. **Observe** it in CloudWatch metrics and logs and CloudTrail events.
9. **Measure cost** with cost allocation tags and compare with your
   estimate.
10. **Tear down** and verify nothing billable remains.
11. **Write down** lessons, costs, and exam-relevant facts in
    `module-g3-notes.md`.

Keep one `aws_lab/` repository:

```text
aws_lab/
├── infra/                 # Terraform: one module per topic, shared baseline (budgets, tags, roles)
├── jobs/                  # Glue scripts, EMR jobs, Lambda functions
├── sql/                   # Athena and Redshift SQL
├── statemachines/         # Step Functions definitions
├── docs/                  # architecture diagrams, cost log, service map, exam notes
└── tests/                 # moto-based unit tests and integration scripts
```

---

## 6. Phase A — Landscape and Storage (Basics → Intermediate)

### Topic 01 — [AWS data services landscape and reference architectures](01-aws-data-services-landscape-and-reference-architectures.md)

**Why it comes first:** AWS offers many overlapping data services. Without a
map, teams pick services by habit and end up with expensive, fragmented
platforms.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The AWS data service families: **storage** (S3, S3 Tables), **catalog and governance** (Glue Data Catalog, Lake Formation, DataZone), **ingestion** (DMS, zero-ETL, Kinesis, Firehose, MSK, AppFlow, Transfer Family), **processing** (Glue, EMR, Lambda, Managed Service for Apache Flink), **query and warehouse** (Athena, Redshift), **orchestration** (Step Functions, EventBridge, MWAA), **operations and security** (CloudWatch, CloudTrail, KMS, VPC) |
| Basics | Mapping the Stage 2 concepts to AWS services (a service map from Module 2.17's table, now in depth) |
| Intermediate | **Reference architectures**: serverless lakehouse (S3 + Glue + Athena + Lake Formation), warehouse-centric (Redshift + zero-ETL + Spectrum), streaming (Kinesis/MSK + Flink + Firehose + S3/Redshift), big-data processing (EMR + S3 + Iceberg) |
| Intermediate | **Choosing between overlapping services**: Glue vs EMR vs Lambda for processing; Athena vs Redshift for SQL; Kinesis vs MSK for streaming; Step Functions vs MWAA for orchestration; DMS vs zero-ETL vs Debezium for replication |
| Intermediate | Service **quotas** and regional availability — checking them before designing |
| Advanced | Multi-account set-ups for data platforms (separate accounts for ingestion, lake, analytics, and environments), and AWS Organizations guardrails — awareness |
| Advanced | The AWS Well-Architected Framework and its data analytics lens as a review checklist |

**How to learn it**

1. Read the topic file.
2. Draw each reference architecture from memory, then compare with AWS's
   published diagrams.
3. For five workloads from earlier modules, choose services and write a
   one-line justification each.

**Hands-on exercise — `docs/`**

1. Build a **service decision table** (rows: workloads; columns: chosen
   service, alternative, reason, cost driver).
2. Create a Terraform **baseline**: budgets and alerts, cost allocation tags,
   a lab S3 bucket with encryption and blocked public access, and an
   `aws-lab` role for your own work.
3. Record the quotas that matter for this module (Glue concurrent runs,
   Athena concurrent queries, Kinesis shard limits) in your notes.

**Checkpoint — you are ready to move on when you can:**

- [ ] Name the main AWS data services by family and purpose.
- [ ] Draw four reference architectures.
- [ ] Choose between overlapping services with reasons.

**Common mistakes:** choosing services before requirements; running
several overlapping tools for the same job; ignoring quotas and regional
availability.

---

### Topic 02 — [S3 Tables, access points, and Batch Operations](02-s3-tables-access-points-and-batch-operations.md)

**Why here:** Module 2.17 covered S3 fundamentals. Data lakes on AWS also
use S3 capabilities built specifically for analytics, per-application
access, and operations on billions of objects.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **S3 Tables**: table buckets that store Apache Iceberg tables as a managed resource, with namespaces and tables |
| Basics | Automatic table maintenance in S3 Tables (compaction, snapshot management, unreferenced file removal) vs doing it yourself (Module 2.15) |
| Intermediate | Accessing S3 Tables from Athena, Glue, EMR, Redshift, and open-source engines through AWS catalog integrations and the Iceberg REST interface; permissions on table buckets |
| Intermediate | When to use S3 Tables vs your own Iceberg tables in general-purpose buckets (control, cost, engine compatibility) |
| Intermediate | **Access points**: separate access policies per application or team on a shared bucket; restricting access points to a VPC; delegating bucket access control to access points |
| Intermediate | **S3 Batch Operations**: running copy, tagging, restore, ACL/ownership fixes, object deletion or Lambda functions across millions of objects from a manifest (e.g. S3 Inventory) |
| Advanced | S3 Inventory as a source of truth for audits and batch jobs (building on Module 2.17's storage reports) |
| Advanced | Object metadata tables for S3 (queryable metadata of objects) — awareness |
| Advanced | Multi-Region Access Points and replication for resilience — awareness |
| Advanced | Cost considerations: table bucket storage and maintenance pricing, Batch Operations per-job and per-object costs |

**How to learn it**

1. Read the topic file.
2. Create a table bucket and one Iceberg table, load data, and query it from
   Athena; inspect the automatic maintenance settings.
3. Design access points for three consumers of one bucket.

**Hands-on exercise — `infra/s3_advanced/`**

1. Create an S3 table bucket, a namespace, and a `orders` Iceberg table;
   write data with PyIceberg or a Glue/EMR job; query from Athena.
2. Compare behaviour and cost with an Iceberg table in a general-purpose
   bucket that you maintain yourself.
3. Create access points for `ingestion` (write to `landing/`), `analytics`
   (read `gold/`), and a VPC-only access point for a private job.
4. Generate an S3 Inventory report and run a Batch Operations job that tags
   all objects older than 90 days in `landing/`; review the completion
   report.
5. Record costs of each experiment.

**Checkpoint:**

- [ ] Explain S3 Tables and when to use them.
- [ ] Use access points to separate application permissions.
- [ ] Run Batch Operations from an inventory manifest.

**Common mistakes:** one bucket policy trying to serve every team; scripts
looping over millions of objects instead of Batch Operations; enabling
features without checking cost and engine support.

---

## 7. Phase B — Catalog, Processing, and Query (Intermediate)

### Topic 03 — [Glue Data Catalog, crawlers, and schema management](03-glue-data-catalog-crawlers-and-schema-management.md)

**Why here:** The Glue Data Catalog is the metadata backbone of AWS
analytics: Athena, Glue, EMR, Redshift Spectrum, and Lake Formation all use
it. Poor catalog hygiene breaks queries and governance everywhere.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Catalog objects: databases, tables, partitions, columns, table properties, and storage descriptors |
| Basics | Creating tables through Athena DDL, Terraform, the API (boto3), and Iceberg writers |
| Basics | **Crawlers**: how they infer schemas and partitions from S3 (classifiers, include/exclude patterns, schedules) |
| Intermediate | **Crawler schema-change policies**: update, ignore, or log; incremental crawls; and why crawlers can silently create wrong tables or partitions |
| Intermediate | **When not to use crawlers**: defining schemas as code for stable, contracted datasets (Module 2.11), and registering partitions deliberately or using partition projection (Topic 05) |
| Intermediate | **Partition management**: adding partitions (API, `MSCK REPAIR`, crawlers), **partition indexes** for tables with many partitions, and their effect on query planning |
| Intermediate | Glue as an **Iceberg catalog** (including its Iceberg REST endpoint) for Spark, PyIceberg, and other engines (Module 2.15) |
| Advanced | **Glue Schema Registry** for streaming data (Avro, JSON Schema, Protobuf) with Kinesis and MSK, compared with Confluent-style registries (Module 2.16) |
| Advanced | Column statistics in the catalog and their use by query engines |
| Advanced | Catalog permissions (IAM and Lake Formation — Topic 06), cross-account catalog access, and catalog federation to external catalogs — awareness |
| Advanced | Catalog costs and limits (objects stored, requests) |

**How to learn it**

1. Read the topic file.
2. Crawl a messy prefix (mixed schemas, a stray file) and observe the
   tables the crawler creates; then define the same tables as code.
3. Create a table with 50,000 partitions and compare query planning with
   and without partition indexes.

**Hands-on exercise — `infra/catalog/`**

1. Define `bronze`, `silver`, and `gold` databases and core tables in
   Terraform with explicit schemas and table properties.
2. Run a crawler on a landing prefix with deliberately inconsistent files;
   document every surprising result and the schema-change policy you would
   choose.
3. Register partitions for a date-partitioned table using the API from a
   Python job (the pattern pipelines use after writing new partitions).
4. Add a partition index and measure the effect on an Athena query's
   planning time.
5. Use Glue as the Iceberg catalog from PyIceberg or Spark and create an
   Iceberg table.
6. Register a Protobuf or Avro schema in the Glue Schema Registry (used in
   Topic 08).

**Checkpoint:**

- [ ] Manage catalog databases, tables, and partitions as code.
- [ ] Explain the risks of crawlers and when to use them.
- [ ] Use partition indexes and Glue as an Iceberg catalog.
- [ ] Use the Glue Schema Registry for streaming schemas.

**Common mistakes:** crawlers on production prefixes with default policies;
thousands of accidental tables from a bad crawl; schemas nobody owns;
forgetting to register partitions after writes.

---

### Topic 04 — [Glue ETL jobs and Glue Data Quality](04-glue-etl-jobs-and-glue-data-quality.md)

**Why here:** AWS Glue is AWS's serverless ETL service: managed Spark (and
Python) without clusters. It is the default batch-processing choice on many
AWS data teams.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Glue job types: **Spark** jobs, **Python shell** jobs (small, single-node work), and **streaming** jobs; Glue versions and their Spark and Python versions |
| Basics | Job parameters, IAM job roles, script locations, and running jobs from the CLI and boto3 |
| Basics | **DynamicFrames** vs Spark DataFrames — what DynamicFrames add (schema flexibility, catalog integration) and why most teams use DataFrames for transformations |
| Intermediate | **Worker types and capacity (DPUs)**, auto scaling, and the **Flex** execution class for non-urgent jobs at lower cost |
| Intermediate | **Job bookmarks** for incremental processing of new S3 files or JDBC rows — and their limitations compared with your own state management (Module 2.12) |
| Intermediate | Writing Iceberg, Delta, or Hudi tables from Glue; partitioned Parquet output; updating the catalog from jobs |
| Intermediate | Glue **connections** for JDBC sources in VPCs (links to Topic 13) |
| Intermediate | Development workflow: local development with the Glue container image, interactive sessions/notebooks, and packaging extra Python libraries |
| Intermediate | **Glue Data Quality**: rules in the Data Quality Definition Language (DQDL), rule recommendations, rulesets on catalog tables and inside jobs, outcomes, and failing or quarantining data (Module 2.11) |
| Advanced | Data-quality anomaly detection and rules over statistics |
| Advanced | Tuning Glue Spark jobs (applying Module 2.14): partitions, skew, broadcast joins, and reading the Spark UI for Glue runs |
| Advanced | Glue Studio (visual ETL) and Glue workflows/triggers — awareness, and why teams usually orchestrate with Step Functions or MWAA (Topic 10) |
| Advanced | Cost model: DPU-hours, minimum billing, Flex, and right-sizing |

**How to learn it**

1. Read the topic file.
2. Port one PySpark job from Module 2.14 to Glue, first locally with the
   Glue container, then as a real job.
3. Run it with different worker types and Flex; record time and cost.

**Hands-on exercise — `jobs/glue/`**

1. Write a Glue Spark job that reads bronze JSON orders from S3, cleans and
   deduplicates them, and writes a partitioned Iceberg `silver.orders`
   table registered in the catalog.
2. Make it incremental with job bookmarks; then implement the same with
   your own watermark (Module 2.12) and compare behaviour on reruns and
   backfills.
3. Add a Glue Data Quality ruleset (completeness, uniqueness, value ranges,
   referential checks) that fails the job on critical rules and writes
   failing rows to a quarantine prefix.
4. Run a Python shell job for a small reference-data load.
5. Compare cost and time: standard vs Flex execution; two worker sizes.
6. Test transformation functions locally with pytest (Module 2.19) before
   deploying.

**Checkpoint:**

- [ ] Build and deploy Glue Spark and Python shell jobs as code.
- [ ] Choose worker types and execution classes by cost and urgency.
- [ ] Use bookmarks or your own state for incremental processing.
- [ ] Enforce data quality with Glue Data Quality.

**Common mistakes:** developing only in the console; oversized workers for
small data; relying on bookmarks for complex incremental logic; running
every job with standard execution when Flex would do.

---

### Topic 05 — [Athena advanced: partition projection, CTAS, and Iceberg](05-athena-advanced-partition-projection-ctas-and-iceberg.md)

**Why here:** Athena is serverless SQL over the lake, billed mainly by data
scanned. Used well, it is fast and cheap; used carelessly, it scans
terabytes for every dashboard refresh.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Athena's engine (Trino-based), query results location, and pricing by bytes scanned (Module 2.17) |
| Basics | **Workgroups**: separating teams and workloads, enforcing result locations and encryption, and **per-query and per-workgroup data limits** |
| Intermediate | **Partition projection**: computing partitions from table properties instead of storing millions of partitions in the catalog — configuration for dates, integers, and enums |
| Intermediate | **CTAS** (`CREATE TABLE AS SELECT`) and `INSERT INTO` to produce optimised Parquet or Iceberg tables; `UNLOAD` to export query results as Parquet |
| Intermediate | **Iceberg tables in Athena**: creating, `MERGE`, `UPDATE`, `DELETE`, time travel, and maintenance (`OPTIMIZE`, `VACUUM`) — applying Module 2.15 on AWS |
| Intermediate | Reducing cost and time (applying Modules 2.5 and 2.21): columnar formats, compression, partitioning and sorting, file sizes, selecting only needed columns |
| Intermediate | **Parameterised queries** and prepared statements from Python (no string formatting — Module 2.7) |
| Advanced | **Query result reuse** and when cached results are acceptable |
| Advanced | **Federated queries** through data source connectors (e.g. querying a database from Athena) — use cases and costs |
| Advanced | Capacity reservations for predictable workloads, and Athena for Apache Spark — awareness |
| Advanced | Reading `EXPLAIN` and query statistics to see scanned bytes and bottlenecks |
| Advanced | Athena as a query engine for dbt (Module 2.12) — awareness |

**How to learn it**

1. Read the topic file.
2. Run the same analytical query on raw CSV, partitioned Parquet, and an
   Iceberg table; compare scanned bytes and cost.
3. Configure partition projection on a table with years of hourly partitions.

**Hands-on exercise — `sql/athena/`**

1. Create workgroups `analytics` and `etl` with enforced result locations,
   encryption, and per-query scan limits; show a query blocked by the limit.
2. Configure partition projection for a date-and-hour partitioned events
   table; remove the catalog partitions and show queries still prune.
3. Use CTAS to convert raw CSV into partitioned, compressed Parquet; use
   `UNLOAD` to export a report.
4. Create an Iceberg `silver.customers` table in Athena; apply a CDC batch
   with `MERGE`; query an older snapshot; run `OPTIMIZE` and `VACUUM`.
5. Run a parameterised query from Python (boto3 or AWS SDK for pandas) and
   fetch results.
6. Build a cost comparison table for all experiments.

**Checkpoint:**

- [ ] Control cost and access with workgroups and scan limits.
- [ ] Use partition projection for large partitioned tables.
- [ ] Use CTAS, `INSERT INTO`, and `UNLOAD` effectively.
- [ ] Run and maintain Iceberg tables with Athena.
- [ ] Reduce scanned bytes with layout and query design.

**Common mistakes:** querying raw CSV/JSON repeatedly; millions of catalog
partitions; no workgroup limits; `SELECT *` on wide tables; forgetting
Iceberg maintenance.

---

## 8. Phase C — Governance and Warehousing (Intermediate → Advanced)

### Topic 06 — [Lake Formation permissions and governance](06-lake-formation-permissions-and-governance.md)

**Why here:** IAM policies on S3 prefixes cannot express "analysts may see
these columns and only their region's rows". Lake Formation adds
database-style, fine-grained permissions to the lake — for every engine
that reads the catalog.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why Lake Formation: central, fine-grained permissions on catalog resources instead of per-bucket IAM policies |
| Basics | **Data lake administrators**, **registered S3 locations**, and the Lake Formation permission model (grants on databases, tables, columns) |
| Basics | How engines (Athena, Glue, EMR, Redshift Spectrum) obtain temporary, scoped credentials from Lake Formation (**credential vending**) |
| Intermediate | **Column-level** permissions and **data filters** for **row-level** and cell-level security |
| Intermediate | **LF-Tags** and **tag-based access control** (TBAC): tagging databases, tables, and columns (e.g. `classification=pii`, `domain=finance`) and granting by tag — scaling governance (Module 2.20) |
| Intermediate | **Hybrid access mode** and the transition from IAM-only access; the default permissions for newly created resources and why to review them |
| Intermediate | Auditing access with CloudTrail (Topic 12) |
| Advanced | **Cross-account sharing** of tables and databases (resource links, AWS RAM) for multi-account platforms (Topic 01) |
| Advanced | Governing S3 Tables and Iceberg tables with Lake Formation |
| Advanced | Common pitfalls: permissions granted in IAM and Lake Formation at once, super-user principals left in place, and engines that do not enforce fine-grained controls |
| Advanced | The relationship between Lake Formation and business catalogs (Topic 14) |

**How to learn it**

1. Read the topic file.
2. Write an access matrix for three personas (data engineer, finance
   analyst, marketing analyst) across bronze, silver, and gold tables and
   columns.
3. Implement it with LF-Tags and test it with each persona in Athena.

**Hands-on exercise — `infra/lakeformation/`**

1. Register the lake location with Lake Formation and move catalog
   permissions from IAM-only to Lake Formation deliberately.
2. Create LF-Tags (`domain`, `classification`, `layer`), tag databases,
   tables, and PII columns, and grant access by tags to three roles.
3. Create a row-level data filter so a regional analyst sees only their
   region's orders; hide PII columns from marketing.
4. Verify permissions with automated tests (Module 2.20): run queries as
   each role and assert which rows and columns are visible.
5. Share a gold database with a second account (or simulate with a
   separate role) using cross-account grants.
6. Find each role's access in CloudTrail.

**Checkpoint:**

- [ ] Explain credential vending and the Lake Formation permission model.
- [ ] Implement column-, row-, and tag-based access control.
- [ ] Share data across accounts.
- [ ] Test and audit permissions.

**Common mistakes:** managing the same access in IAM and Lake Formation;
leaving broad default grants on new resources; manual per-table grants that
do not scale; assuming every engine enforces fine-grained permissions.

---

### Topic 07 — [Redshift deep dive: Serverless, Spectrum, and data sharing](07-redshift-deep-dive-serverless-spectrum-and-data-sharing.md)

**Why here:** Amazon Redshift is AWS's data warehouse. Module 2.17 compared
it with other warehouses; this topic makes you able to design, load, tune,
and govern it.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Architecture: leader and compute nodes, **RA3** nodes with managed storage, and **Redshift Serverless** (workgroups, namespaces, base and maximum capacity in RPUs) |
| Basics | Choosing provisioned vs Serverless (steady vs spiky workloads, cost control) |
| Basics | **Loading**: `COPY` from S3 (many files, Parquet, manifests, IAM roles), and `UNLOAD` back to S3 |
| Intermediate | **Table design**: distribution styles (`AUTO`, `KEY`, `EVEN`, `ALL`), sort keys, automatic table optimisation and compression — designing a star schema (Module 2.8) for Redshift |
| Intermediate | `MERGE` and staging tables for incremental loads (Module 2.12) |
| Intermediate | **Materialised views** with automatic refresh; result caching |
| Intermediate | **Redshift Spectrum** / external tables on the Glue Catalog: querying the lake from Redshift and joining with warehouse tables |
| Intermediate | **Workload management**: queues, query priorities, concurrency scaling, and query monitoring rules to stop runaway queries |
| Advanced | **Data sharing**: sharing live data across clusters, workgroups, and accounts without copying (including multi-warehouse writes where supported) |
| Advanced | Semi-structured data with the `SUPER` type and PartiQL |
| Advanced | **Streaming ingestion** from Kinesis or MSK into materialised views |
| Advanced | Automatic maintenance (vacuum, analyze) and reading system tables and views for performance and cost |
| Advanced | Security: IAM roles for `COPY`, database roles, row-level security and dynamic data masking in Redshift, and Lake Formation for Spectrum |
| Advanced | Running dbt on Redshift (Module 2.12) — awareness |

**How to learn it**

1. Read the topic file.
2. Load the same star schema with two different distribution designs and
   compare query plans and run times.
3. Query lake tables through Spectrum and join them with warehouse tables.

**Hands-on exercise — `sql/redshift/`**

1. Create a Redshift Serverless workgroup with a low base capacity and a
   maximum capacity limit (Terraform).
2. Load dimensions and facts with `COPY` from Parquet in S3; design
   distribution and sort keys; verify with `EXPLAIN` and system views.
3. Implement an incremental load of orders with a staging table and
   `MERGE`.
4. Create external tables over the lake (Spectrum) and a materialised view
   joining lake events with warehouse orders.
5. Set up workload management rules that abort queries scanning too much.
6. Share a gold schema with another workgroup through data sharing.
7. Record the cost per query and per load; pause or delete resources after
   the exercise.

**Checkpoint:**

- [ ] Choose provisioned vs Serverless and size them.
- [ ] Design distribution and sort keys for a star schema.
- [ ] Load, merge, and unload data efficiently.
- [ ] Query the lake with Spectrum and share data without copies.
- [ ] Protect the warehouse with workload management.

**Common mistakes:** single-row inserts; `KEY` distribution on skewed
columns; no maximum capacity on Serverless; copying data between
warehouses instead of sharing it.

---

## 9. Phase D — Streaming, Big Compute, Orchestration, Replication (Advanced)

### Topic 08 — [Kinesis Data Streams, Firehose, and MSK](08-kinesis-data-streams-firehose-and-msk.md)

**Why here:** Module 2.16 taught streaming with Kafka. On AWS you choose
between **Kinesis** (AWS-native) and **MSK** (managed Kafka) — and use
**Firehose** to land streams in the lake and warehouse with little code.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Kinesis Data Streams**: streams, shards (provisioned) vs on-demand capacity, partition keys, sequence numbers, retention |
| Basics | Producing with boto3 (`PutRecords`) and handling **partial batch failures** |
| Basics | **Amazon Data Firehose**: fully managed delivery of streams to S3, Redshift, OpenSearch, and other destinations with buffering |
| Intermediate | Consuming Kinesis: shared vs **enhanced fan-out** consumers, the Kinesis Client Library and checkpoints (DynamoDB leases), and Lambda consumers with batching and bisecting on errors |
| Intermediate | **Hot shards** from skewed partition keys and resharding (Module 2.16 skew ideas on Kinesis) |
| Intermediate | Firehose features: **dynamic partitioning** of S3 output, **format conversion** to Parquet using a Glue schema, record transformation with Lambda, and delivery to **Iceberg tables** |
| Intermediate | Monitoring consumer lag with **iterator age** (Topic 12) |
| Intermediate | **Amazon MSK**: provisioned clusters vs MSK Serverless, IAM authentication, and running your Module 2.16 Kafka clients against MSK |
| Advanced | **MSK Connect** for connectors (e.g. Debezium from Module 2.16 or S3 sink connectors) |
| Advanced | **Amazon Managed Service for Apache Flink** for stateful stream processing (Module 2.16's Flink, managed) |
| Advanced | Schema governance with the Glue Schema Registry (Topic 03) |
| Advanced | **Choosing Kinesis vs MSK**: ecosystem, throughput and partition limits, retention, operational effort, cost model, and portability |

**How to learn it**

1. Read the topic file.
2. Re-run a Module 2.16 producer and consumer against MSK with IAM auth,
   then implement the same flow with Kinesis.
3. Build a Firehose delivery to partitioned Parquet in S3 and query it with
   Athena.

**Hands-on exercise — `jobs/streaming/`**

1. Create an on-demand Kinesis stream; write a Python producer with
   `PutRecords`, retrying only failed records; send click events keyed by
   user.
2. Consume with a Lambda function (batch size, error bisecting, a failure
   destination) and with an enhanced fan-out consumer; compare latency.
3. Create a Firehose stream from Kinesis to S3 with dynamic partitioning by
   event date and type, Parquet conversion using a Glue table schema, and a
   delivery error prefix; query the output with Athena.
4. Create a skewed key workload, find the hot shard in metrics, and fix the
   key design.
5. Run your Kafka producer and consumer against MSK Serverless with IAM
   authentication.
6. Write a Kinesis vs MSK decision record for your platform, including
   costs.

**Checkpoint:**

- [ ] Produce to and consume from Kinesis reliably.
- [ ] Deliver streams to the lake with Firehose (partitioning and Parquet).
- [ ] Monitor iterator age and fix hot shards.
- [ ] Run Kafka workloads on MSK and choose between Kinesis and MSK.

**Common mistakes:** ignoring partial `PutRecords` failures; skewed
partition keys; no failure destinations for Lambda consumers; small Firehose
buffers producing tiny files; provisioned clusters left running.

---

### Topic 09 — [EMR on EC2, EKS, and Serverless](09-emr-on-ec2-eks-and-serverless.md)

**Why here:** When Glue is not enough — very large or long-running Spark,
custom configurations, other big-data engines, or cost optimisation at
scale — teams use Amazon EMR. It comes in three deployment options.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | EMR's purpose: managed Spark (and other open-source engines) with AWS-optimised runtimes |
| Basics | **EMR on EC2**: primary, core, and task nodes; steps; transient (per-job) vs long-running clusters |
| Basics | **EMR Serverless**: applications, job runs, automatic scaling, pre-initialised capacity, and maximum capacity limits |
| Intermediate | **EMR on EKS**: running Spark jobs on an existing Kubernetes cluster through virtual clusters (Module 2.18) |
| Intermediate | **Cost optimisation on EC2**: Spot for task nodes, instance fleets with several instance types, managed scaling, and auto-termination |
| Intermediate | Configuration: Spark settings, bootstrap actions, custom images (Serverless/EKS), and packaging Python dependencies |
| Intermediate | Reading and writing Iceberg, Delta, or Hudi tables with the Glue Catalog and Lake Formation |
| Intermediate | Accessing logs and the Spark UI for EMR jobs (Module 2.14 debugging) |
| Advanced | Choosing **Glue vs EMR on EC2 vs EMR Serverless vs EMR on EKS**: control, start-up time, cost, operations, and team skills |
| Advanced | Submitting and monitoring jobs from Step Functions or Airflow (Topic 10) |
| Advanced | EMR Studio and notebooks — awareness |
| Advanced | Security: job execution roles, encryption configurations, and running in private subnets (Topic 13) |

**How to learn it**

1. Read the topic file.
2. Run the same Module 2.14 job on Glue, EMR Serverless, and a transient EMR
   on EC2 cluster with Spot task nodes.
3. Record start-up time, run time, and cost for each.

**Hands-on exercise — `jobs/emr/`**

1. Create an EMR Serverless application with a maximum capacity and submit
   your silver-to-gold Spark job reading Iceberg tables via the Glue
   Catalog.
2. Run the same job on a transient EMR on EC2 cluster with Spot task nodes,
   managed scaling, and auto-termination.
3. Find the Spark UI and logs for both runs; diagnose one deliberately
   skewed stage.
4. Build a comparison table (Glue, EMR Serverless, EMR on EC2): start-up
   time, run time, cost, effort — and write a recommendation.
5. Tear down all clusters and applications.

**Checkpoint:**

- [ ] Run Spark jobs on EMR Serverless and EMR on EC2.
- [ ] Use Spot, fleets, managed scaling, and auto-termination safely.
- [ ] Choose between Glue and the EMR options with evidence.

**Common mistakes:** long-running clusters that sit idle; Spot for core
nodes holding data; no maximum capacity on Serverless; debugging without
the Spark UI.

---

### Topic 10 — [Step Functions, EventBridge, and MWAA orchestration](10-step-functions-eventbridge-and-mwaa-orchestration.md)

**Why here:** AWS pipelines combine many services. You need to coordinate
Glue, EMR, Athena, Lambda, and Redshift steps — on schedules and on events —
with retries and error handling.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Step Functions**: state machines, states (`Task`, `Choice`, `Parallel`, `Map`, `Wait`, `Pass`, `Fail`), inputs and outputs |
| Basics | **Standard vs Express** workflows: duration, pricing, and delivery semantics |
| Basics | **Service integrations**: starting Glue jobs, EMR Serverless jobs, Athena queries, Lambda functions, and Redshift statements — and waiting for completion ("run a job and wait" patterns) |
| Intermediate | **Retries and catchers** per state: backoff, jitter, and routing errors to alerting or compensation steps (Module 2.13 ideas on AWS) |
| Intermediate | **Distributed Map** for processing millions of S3 objects in parallel |
| Intermediate | **EventBridge**: event buses, rules, S3 object events via EventBridge, and targets (Step Functions, Lambda) — event-driven pipelines |
| Intermediate | **EventBridge Scheduler** for cron-like and one-time schedules |
| Intermediate | **MWAA** (Amazon Managed Workflows for Apache Airflow): environments, DAG deployment from S3, requirements, AWS provider operators, and supported Airflow versions |
| Advanced | Choosing **Step Functions vs MWAA vs EventBridge-only**: complexity, team skills, backfills, observability, and cost (MWAA environments bill continuously) |
| Advanced | Callback patterns with task tokens for human approval or external systems |
| Advanced | EventBridge Pipes for connecting sources to targets with filtering and enrichment — awareness |
| Advanced | Defining state machines and schedules as code and testing them (Module 2.18) |

**How to learn it**

1. Read the topic file.
2. Orchestrate your Topic 04 and Topic 05 work (Glue job → data quality →
   Athena CTAS → notification) as a state machine.
3. Rebuild the same flow as an MWAA DAG and compare.

**Hands-on exercise — `statemachines/`**

1. Build a Standard workflow: Glue job (wait for completion) → Data Quality
   evaluation → `Choice` (fail or continue) → Athena CTAS for gold →
   notification; with retries and a catcher routing failures to an alert.
2. Trigger it from an EventBridge rule when a partner file lands in S3, and
   separately on a daily EventBridge Scheduler schedule.
3. Use Distributed Map to validate 100,000 small S3 objects in parallel with
   a Lambda function and summarise results.
4. Deploy a small MWAA environment (briefly, due to cost) and run an
   equivalent DAG using AWS operators; then delete the environment.
5. Write a decision record: Step Functions vs MWAA for your platform.

**Checkpoint:**

- [ ] Build state machines that orchestrate AWS data services with error
      handling.
- [ ] Trigger pipelines from events and schedules with EventBridge.
- [ ] Explain MWAA and when to prefer it.

**Common mistakes:** polling loops in Lambda instead of built-in wait
integrations; no catchers, so failures are silent; MWAA environments left
running; event-driven pipelines without deduplication of repeated events.

---

### Topic 11 — [DMS and zero-ETL integrations](11-dms-and-zero-etl-integrations.md)

**Why here:** Replicating operational databases into the lake and warehouse
is a core need (Module 2.9, Project 02). AWS offers managed options that
may replace self-managed CDC — with different trade-offs.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **AWS DMS**: source and target endpoints, replication instances or DMS Serverless, and replication tasks |
| Basics | Task types: **full load**, **CDC only**, and **full load + CDC** |
| Basics | Source prerequisites (e.g. logical replication settings on PostgreSQL — Module 2.9) and least-privilege source users |
| Intermediate | Table mappings (selection and transformation rules), task settings, and **data validation** |
| Intermediate | Targets for data engineering: **S3** (Parquet, with change columns), Kinesis or MSK, and Redshift |
| Intermediate | Handling large objects, data types, and schema changes in DMS |
| Intermediate | **Zero-ETL integrations**: near-real-time replication from supported AWS databases (e.g. Aurora, RDS, DynamoDB) into Redshift or the lakehouse without building pipelines |
| Intermediate | Zero-ETL from supported SaaS applications via Glue — awareness |
| Advanced | Applying DMS CDC files in S3 to Iceberg tables with `MERGE` (Topics 04–05, Module 2.15) |
| Advanced | Monitoring replication lag, task errors, and source impact (replication slots and WAL — Module 2.9 risk) |
| Advanced | **Choosing** DMS vs zero-ETL vs Debezium on MSK (Project 02): latency, flexibility, schema-change handling, supported sources and targets, cost, and lock-in |
| Advanced | DMS Schema Conversion for database migrations — awareness |

**How to learn it**

1. Read the topic file.
2. Replicate a small PostgreSQL (RDS) database to S3 with DMS full load +
   CDC; make changes and inspect the change files.
3. If available in your region and budget, set up a zero-ETL integration
   into Redshift Serverless and compare latency and effort.

**Hands-on exercise — `infra/replication/`**

1. Create an RDS PostgreSQL instance with logical replication enabled and a
   least-privilege replication user.
2. Run a DMS full load + CDC task to S3 in Parquet with transaction
   timestamps; enable validation.
3. Build a Glue or Athena job that merges the change files into Iceberg
   `silver` tables, handling inserts, updates, and deletes.
4. Monitor task lag and source replication-slot health; stop the task and
   observe the effect on the source.
5. Write a comparison of DMS, zero-ETL, and your Project 02 Debezium
   pipeline.
6. Tear down the database, task, and replication resources.

**Checkpoint:**

- [ ] Configure DMS endpoints, tasks, mappings, and validation.
- [ ] Merge DMS CDC output into lakehouse tables.
- [ ] Explain zero-ETL integrations and their limits.
- [ ] Choose a replication approach with evidence.

**Common mistakes:** replication instances left running; unmonitored
source replication slots; treating DMS output as ready-to-query tables
without merging; assuming zero-ETL covers every source and schema change.

---

## 10. Phase E — Operating, Securing, and Unifying (Advanced)

### Topic 12 — [CloudWatch, CloudTrail, and Cost Explorer for data](12-cloudwatch-cloudtrail-and-cost-explorer-for-data.md)

**Why here:** Module 2.20 taught observability in general. On AWS, you must
know exactly where each service publishes metrics and logs, how to audit
data access, and how to see what each pipeline costs.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **CloudWatch metrics** for data services: Glue job metrics, EMR, Kinesis (`IteratorAgeMilliseconds`, throttling), Firehose delivery, Redshift, Athena workgroup metrics, Step Functions executions |
| Basics | **CloudWatch Logs** for Glue, Lambda, Step Functions, and EMR; log retention settings |
| Basics | **Alarms** and notifications (e.g. SNS or chat integrations) |
| Intermediate | **CloudWatch Logs Insights** queries for investigating failures across runs |
| Intermediate | **Dashboards** per pipeline and per platform |
| Intermediate | **EventBridge events** for job state changes (e.g. Glue job failed) routed to alerting (Module 2.20 routing) |
| Intermediate | **CloudTrail**: management events vs **data events** (e.g. S3 object-level access, which costs extra), trails to S3, and querying trails with Athena for audits |
| Intermediate | **Cost Explorer**, **AWS Budgets**, and **cost allocation tags** (activated) for cost per pipeline, team, and environment |
| Advanced | Detailed billing data exports queried with Athena for unit economics (Module 2.21) |
| Advanced | Cost anomaly detection — awareness |
| Advanced | Log and metric cost control: retention, sampling, and avoiding high-cardinality custom metrics |
| Advanced | CloudTrail Lake and organisation-wide trails — awareness |

**How to learn it**

1. Read the topic file.
2. For every service used in this module, list its key health metric and
   the alarm you would set.
3. Answer "who read the finance gold table last week?" and "what did the
   orders pipeline cost last month?" from AWS data alone.

**Hands-on exercise — `infra/observability/`**

1. Create alarms for Glue job failures (via EventBridge), Kinesis iterator
   age, Firehose delivery errors, Redshift query queue time, and Step
   Functions failed executions — routed to one notification channel.
2. Build a CloudWatch dashboard for the platform.
3. Write three Logs Insights queries you would use during an incident.
4. Enable CloudTrail data events for the gold prefix only; query the trail
   with Athena to list who accessed gold data.
5. Build a monthly cost report per pipeline from cost allocation tags (Cost
   Explorer or billing exports + Athena) and set per-pipeline budgets.

**Checkpoint:**

- [ ] Monitor every AWS data service with the right metrics and alarms.
- [ ] Investigate failures with Logs Insights.
- [ ] Audit data access with CloudTrail.
- [ ] Attribute cost to pipelines with tags and budgets.

**Common mistakes:** logs kept forever; untagged resources; CloudTrail data
events enabled for every bucket (expensive); alarms nobody receives.

---

### Topic 13 — [KMS, VPC endpoints, and private networking for data](13-kms-vpc-endpoints-and-private-networking-for-data.md)

**Why here:** Production AWS data platforms keep data encrypted with
controlled keys and traffic off the public internet. These topics are also
central to the certification's security domain.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **KMS keys**: AWS-managed vs customer-managed keys; key policies, grants, and rotation (Module 2.20 envelope encryption, on AWS) |
| Basics | S3 encryption options: SSE-S3 vs SSE-KMS; **S3 Bucket Keys** to reduce KMS request costs |
| Basics | Encryption settings for Glue (security configurations), Athena (results), Redshift, Kinesis, Firehose, EMR, and MSK |
| Intermediate | **VPC basics for data**: private subnets, security groups, and why NAT gateways are both a data path and a significant cost |
| Intermediate | **Gateway endpoints** (S3, DynamoDB — no hourly charge) vs **interface endpoints** (PrivateLink — hourly and per-GB charges) for Glue, Athena, STS, Secrets Manager, Kinesis, and more |
| Intermediate | **Bucket policies restricted to VPC endpoints** or VPCs, and denying non-TLS access |
| Intermediate | Running Glue jobs, EMR, Redshift, and Lambda inside private subnets with the endpoints they need |
| Intermediate | Database credentials from **Secrets Manager** with rotation (Module 2.18) for Glue connections, DMS, and Redshift |
| Advanced | **Cross-account encryption**: sharing KMS keys and encrypted data between accounts |
| Advanced | **Data perimeter** concepts: ensuring only trusted identities access trusted resources from expected networks — awareness |
| Advanced | Private connectivity to other networks (VPN, Direct Connect) — awareness |
| Advanced | Troubleshooting "access denied" and "timeout" errors caused by key policies, endpoint policies, and security groups |

**How to learn it**

1. Read the topic file.
2. Draw your platform's network: VPC, subnets, endpoints, and which services
   run where.
3. Create an access-denied error through a KMS key policy and a timeout
   through a missing endpoint, and diagnose both.

**Hands-on exercise — `infra/network_security/`**

1. Create customer-managed KMS keys for `silver` and `gold` data with key
   policies allowing only the relevant roles; enable S3 Bucket Keys.
2. Build a VPC with private subnets, an S3 gateway endpoint, and the
   interface endpoints your Glue job needs; run the Topic 04 job inside it
   **without** a NAT gateway.
3. Restrict the gold bucket to requests from your VPC endpoint and to TLS
   only; prove access from outside is denied.
4. Move the Glue JDBC connection credentials to Secrets Manager.
5. Estimate the monthly cost of endpoints vs a NAT gateway for your traffic.
6. Tear down endpoints (they bill hourly).

**Checkpoint:**

- [ ] Encrypt data with customer-managed keys and control them with key
      policies.
- [ ] Run data workloads privately using VPC endpoints.
- [ ] Restrict buckets to VPC endpoints and TLS.
- [ ] Diagnose KMS and networking access problems.

**Common mistakes:** everything through a NAT gateway (expensive); keys
shared by every workload; forgetting KMS permissions in job roles; interface
endpoints left running in labs.

---

### Topic 14 — [SageMaker Unified Studio and DataZone overview](14-sagemaker-unified-studio-and-datazone-overview.md)

**Why last:** AWS is converging data, analytics, and AI tooling into a
unified experience with a business data catalog and governed data sharing.
You should understand where it fits relative to everything you built in
this module.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The goal: one environment where data engineers, analysts, and ML/AI builders find, access, and use governed data |
| Basics | **Amazon DataZone** concepts: domains, projects, business data catalog, glossaries, metadata forms, data products, publishing, and **subscription requests** with approval |
| Basics | **SageMaker Unified Studio** (part of the next generation of Amazon SageMaker) and its catalog and lakehouse capabilities — how they build on the Glue Data Catalog, Lake Formation, Athena, Redshift, and EMR |
| Intermediate | Publishing a gold dataset as a data product with business metadata, and approving a consumer's subscription |
| Intermediate | How governed access is granted underneath (Lake Formation and Redshift permissions) |
| Intermediate | Relationship to open-source and third-party catalogs from Module 2.20 (OpenMetadata, DataHub) and to Unity Catalog (Gap Module G4) |
| Advanced | When to adopt the unified studio vs composing individual services yourself — team size, governance needs, and lock-in |
| Advanced | Tracking product changes: this area evolves quickly; check current capabilities and naming |

**How to learn it**

1. Read the topic file.
2. Create a small domain and project; publish your `gold.daily_revenue`
   table as a data product with a description and glossary terms.
3. Subscribe to it from a second project and inspect the permissions created
   underneath.

**Hands-on exercise — `docs/unified_catalog.md`**

1. Publish two gold datasets with business metadata, owners, and glossary
   terms.
2. Request access from an analyst project and approve it; verify the
   analyst can query the data in Athena.
3. Compare the experience with the self-built catalog and governance from
   Module 2.20 and Topic 06; write a short adoption recommendation.
4. Clean up the domain and projects.

**Checkpoint:**

- [ ] Explain DataZone and SageMaker Unified Studio concepts.
- [ ] Publish and subscribe to a governed data product.
- [ ] Explain how it relates to Lake Formation and the Glue Catalog.

**Common mistakes:** treating the business catalog as a replacement for
technical permissions design; adopting a unified platform without checking
current feature coverage for your engines and regions.

---

## 11. Consolidate — practice, interviews, and certification

### [`practice-questions.md`](practice-questions.md)

For every question:

1. Identify the requirements (latency, volume, cost, security, operations).
2. Choose services and justify each against alternatives.
3. Define IAM roles, Lake Formation permissions, encryption, and networking.
4. Estimate the monthly cost.
5. Implement the core in Terraform if the question asks for it, then tear
   it down.

### [`interview-practice.md`](interview-practice.md)

AWS data interviews mix architecture, service trade-offs, and incident
scenarios. Practise out loud with a **30-minute timer**:

- design a serverless lakehouse for clickstream and orders;
- replicate an Aurora or RDS database into analytics with minimal latency;
- secure a multi-account data lake with fine-grained access;
- reduce an Athena bill that tripled;
- choose Kinesis or MSK for a new streaming platform;
- a Glue job got 5× slower after a data spike — walk through your
  diagnosis;
- choose Glue, EMR Serverless, or Redshift for a nightly transformation.

For each, cover requirements, services, data flow, security, operations,
cost, and trade-offs.

### [`certification-prep-aws-data-engineer-associate.md`](certification-prep-aws-data-engineer-associate.md)

The **AWS Certified Data Engineer – Associate** exam covers data ingestion
and transformation, data store management, data operations and support,
and data security and governance. Preparation plan:

1. Download the **current exam guide** and map every task statement to a
   topic in this module (and to Stage 2 modules for general concepts).
2. Fill gaps with AWS Skill Builder resources and the official
   documentation's service FAQs.
3. Take practice exams; for every wrong answer, write why the correct
   answer is right **and** why each distractor is wrong.
4. Focus on service limits, cost-optimised choices, security defaults, and
   "most operationally efficient" answers — typical exam patterns.
5. Revisit hands-on labs for services you have not used in real exercises.

---

## 12. Module mini-project — an AWS serverless lakehouse

This mini-project is expanded in
[`../00-Gap-Modules-Overview/Projects/03-aws-serverless-lakehouse.md`](../00-Gap-Modules-Overview/Projects/03-aws-serverless-lakehouse.md).
The short version:

**Goal:** Rebuild the core of your Stage 2 orders platform on AWS with
serverless and managed services, entirely as code, secured, observed, and
within a small budget.

1. **Infrastructure:** Terraform for all resources, per-environment
   variables, budgets, and a teardown script.
2. **Ingestion:** partner files via S3 events and Step Functions; orders
   database replicated with DMS (or zero-ETL where available); click events
   through Kinesis and Firehose into partitioned Parquet or Iceberg.
3. **Catalog and storage:** Glue Data Catalog as code, Iceberg tables (in
   S3 Tables or general-purpose buckets), partition projection where useful.
4. **Processing:** Glue Spark jobs for bronze → silver → gold with Glue Data
   Quality gates; one heavier job on EMR Serverless for comparison.
5. **Query and warehouse:** Athena workgroups with scan limits for
   analysts; gold facts and dimensions loaded into Redshift Serverless (or
   queried via Spectrum).
6. **Governance and security:** Lake Formation with LF-Tags, row filters,
   and PII column restrictions; customer-managed KMS keys; private
   subnets with VPC endpoints; secrets in Secrets Manager.
7. **Orchestration and operations:** Step Functions (or MWAA) pipelines
   with retries and alerts; CloudWatch dashboards and alarms; CloudTrail
   audit queries; cost per pipeline from tags.
8. **Evidence:** an architecture diagram, a service decision record, a cost
   report, and a teardown log.

**Grading yourself:** the platform is created and destroyed entirely from
code; an analyst role sees only permitted rows and columns; a bad file is
blocked by a quality gate and alerted; costs are attributed per pipeline and
stay within budget; and nothing billable remains after teardown.

---

## 13. Module self-assessment — exit criteria

Tick every box without looking at your notes:

- [ ] I can map data problems to AWS services and justify trade-offs.
- [ ] I can use S3 Tables, access points, and Batch Operations.
- [ ] I can manage the Glue Data Catalog as code and use crawlers safely.
- [ ] I can build and cost-optimise Glue jobs with Data Quality gates.
- [ ] I can run cheap, fast Athena queries, including on Iceberg tables.
- [ ] I can implement fine-grained, tag-based governance with Lake
      Formation.
- [ ] I can design, load, tune, and share data in Redshift.
- [ ] I can build streaming ingestion with Kinesis, Firehose, or MSK.
- [ ] I can choose and run EMR deployment options.
- [ ] I can orchestrate AWS pipelines with Step Functions, EventBridge, or
      MWAA.
- [ ] I can replicate databases with DMS or zero-ETL and choose between
      approaches.
- [ ] I can monitor, audit, and cost-attribute AWS data workloads.
- [ ] I can secure data with KMS, VPC endpoints, and private networking.
- [ ] I can explain the unified studio and business catalog direction.
- [ ] I have finished the practice questions, interview practice, and the
      mini-project (and, optionally, passed the certification).

---

## 14. Recommended reading and references

| Resource | Relevant topics |
| --- | --- |
| AWS documentation and service FAQs for S3, S3 Tables, Glue, Athena, Lake Formation, Redshift, Kinesis, Firehose, MSK, EMR, Step Functions, EventBridge, MWAA, DMS, CloudWatch, CloudTrail, KMS, VPC, DataZone, and SageMaker Unified Studio | All topics |
| AWS Well-Architected Framework — Data Analytics Lens | 01, 12, 13 |
| AWS Prescriptive Guidance and AWS Architecture Center — data lake, lakehouse, and streaming reference architectures | 01, 08 |
| AWS Big Data Blog — deep dives on Iceberg on AWS, Lake Formation, Redshift, Glue performance | 02–09 |
| Official exam guide for AWS Certified Data Engineer – Associate; AWS Skill Builder exam preparation | Certification prep |
| Terraform AWS provider documentation | All topics |
| AWS SDK for pandas (awswrangler) documentation | 03, 05, 07 |

---

## 15. Where this module leads

| This module's skill | Where you use it next |
| --- | --- |
| Complete AWS data platform | Stage 2 **Capstone** (Project 07) — Option B, real cloud deployment on AWS |
| Service trade-offs and reference architectures | Gap Module G5 — Data Engineering System Design Interviews |
| Lake Formation, KMS, and private networking | Governance evidence for the capstone and any AWS production role |
| SageMaker Unified Studio, streaming, and feature data on AWS | Applied AI and Agentic AI stages built on AWS |

Depth in one cloud turns general data engineering knowledge into
deliverable systems. The habits you build here — pick services from
requirements, build everything as code, grant access through tags and
least privilege, keep traffic private and data encrypted, watch iterator
age and scanned bytes, tag every resource, and tear down what you do not
use — are exactly what AWS data engineering roles expect.
