# 04 — Glue ETL Jobs and Glue Data Quality

> **G3 — AWS Data Engineering Deep Dive**
>
> **Progression:** ETL fundamentals → Glue architecture → job types → Spark → DynamicFrames/DataFrames → configuration → workers/DPUs → incremental processing → bookmarks/state → idempotency → Parquet → Iceberg → JDBC/VPC → dependencies → performance → Data Quality → DQDL → quality gates → quarantine → anomaly detection → testing → observability → security → cost → production architecture

---

## 1. Module Overview

AWS Glue is a managed data-integration service that can run Spark-based ETL without requiring you to operate a Spark cluster yourself. It also provides Python shell and streaming job capabilities, integrations with the Glue Data Catalog, and AWS Glue Data Quality.

This module is not about memorizing console fields. It is about learning how to design a **production ETL system** that can:

- ingest data incrementally,
- transform it with Spark,
- handle schema irregularities,
- write efficient lakehouse formats,
- validate data quality,
- quarantine bad records,
- recover from failure,
- avoid duplicate output,
- run inside controlled network boundaries,
- use least-privilege IAM,
- manage dependencies reproducibly,
- expose useful logs and metrics,
- control compute cost.

AWS Glue Data Quality provides managed, serverless data-quality capabilities using the Data Quality Definition Language (DQDL), rulesets, recommendations, scores, and ML-based anomaly detection. citeturn0search1turn0search0

### The simplest mental model

```text
Source
  ↓
Extract
  ↓
Transform
  ↓
Validate
  ↓
Publish
  ↓
Observe
```

In AWS Glue:

```text
S3 / JDBC / Streaming Source
             ↓
        Glue Job
             ↓
      Spark / PySpark
             ↓
      Transformations
             ↓
      Data Quality
        /         \
     PASS          FAIL
      ↓             ↓
 Curated        Quarantine
      ↓
 Parquet / Iceberg
      ↓
 Data Catalog
      ↓
 Analytics
```

### Relationship to earlier roadmap modules

You already learned the fundamentals of:

- Python
- SQL
- data engineering
- Spark/PySpark
- S3
- Data Catalog
- Iceberg
- data quality concepts
- orchestration concepts
- Terraform
- AWS fundamentals

This module **applies those concepts inside AWS Glue**.

### Scope boundary

This module goes deep on:

- Glue jobs
- Glue Spark execution
- Python shell jobs
- streaming jobs
- job configuration
- DynamicFrames and DataFrames
- incremental processing
- bookmarks and custom state
- watermarks
- idempotency
- Parquet
- Iceberg
- JDBC/VPC connectivity
- dependencies
- Glue local development
- interactive sessions
- Glue Studio/workflows awareness
- Spark tuning in Glue
- Glue Data Quality
- DQDL
- quality gates
- quarantine
- recommendations
- anomaly detection
- testing
- observability
- security
- cost
- production operations

It only **connects to**, rather than re-teaches:

- Glue Data Catalog internals
- advanced Athena
- Lake Formation
- Redshift
- Kinesis/MSK
- EMR
- Step Functions/MWAA
- DMS
- DataZone

---

# 2. Why AWS Glue ETL Exists

Traditional ETL:

```text
Source
  ↓
Extract
  ↓
Transform
  ↓
Load
```

In a production data lake:

```text
Operational DB ─────┐
API ────────────────┤
Files ──────────────┤
Events ─────────────┘
          ↓
       Landing
          ↓
       Transform
          ↓
       Validate
          ↓
       Publish
```

The infrastructure needed to operate a distributed processing engine can become substantial:

```text
Compute
Networking
Cluster lifecycle
Runtime
Scaling
Logging
Monitoring
Dependencies
Security
```

Glue removes much of the cluster-management burden.

The engineer still owns:

```text
Data logic
Schema
Incremental strategy
Quality
Idempotency
Security
Performance
Cost
Operations
```

That distinction is critical.

> **Managed compute does not mean managed engineering decisions.**

---

# 3. Glue ETL Mental Model

A Glue job can be understood as:

```text
Glue Job
│
├── Runtime / Glue version
│
├── Command
│     ├── Spark ETL
│     ├── Python shell
│     └── Streaming
│
├── Script
│
├── IAM execution role
│
├── Parameters
│
├── Workers
│
├── Input
│
├── Transformation
│
├── Output
│
├── State / bookmarks
│
├── Logs / metrics
│
└── Data quality
```

### What AWS manages

Depending on the job type and configuration, Glue manages much of:

- infrastructure provisioning,
- Spark runtime setup,
- worker lifecycle,
- execution environment,
- integration with AWS services,
- logging/metrics integration.

### What the data engineer manages

You still manage:

- code,
- schema,
- data contracts,
- transformations,
- partitioning,
- incremental semantics,
- state,
- retries,
- quality thresholds,
- output correctness,
- dependencies,
- IAM requirements,
- networking,
- testing,
- cost.

---

# 4. Glue Job Types

AWS Glue supports several job patterns. Select the smallest execution model that matches the workload.

| Job type | Best fit | Avoid when |
|---|---|---|
| Spark | Distributed ETL | Tiny utility task |
| Python shell | Lightweight Python work | Large distributed transformations |
| Streaming | Continuous/near-real-time processing | Simple daily batch |
| Interactive session | Development/exploration | Production scheduler by itself |
| Glue Studio visual job | Visual development / generated ETL | Complex code-heavy engineering where code review is primary |

---

# 5. Spark Jobs

A Glue Spark job uses a managed Spark runtime.

Conceptually:

```text
Driver
  |
  +── Executor
  +── Executor
  +── Executor
  +── Executor
```

The driver coordinates work.

Executors process partitions.

You should already know the underlying Spark concepts from the PySpark module. Here the important question is:

> **How does Spark knowledge translate into an AWS Glue production job?**

Example:

```python
from pyspark.sql import functions as F

df = spark.read.parquet("s3://example/raw/orders/")

clean = (
    df
    .filter(F.col("order_id").isNotNull())
    .withColumn("amount", F.col("amount").cast("decimal(18,2)"))
)

clean.write.mode("append").parquet(
    "s3://example/silver/orders/"
)
```

The transformation is Spark.

Glue provides the managed execution environment.

---

# 6. Python Shell Jobs

Python shell jobs are appropriate for smaller, single-node tasks.

Examples:

```text
Small API extraction
Metadata update
Small reference-data transformation
File validation
Control-plane automation
Lightweight notification
```

They are not a replacement for Spark when the data requires distributed processing.

### Decision rule

Ask:

```text
Does the workload require distributed computation?
          |
       +--+--+
       |     |
      YES    NO
       |     |
    Spark   Python Shell
```

Do not choose Spark merely because the data is stored in S3.

---

# 7. Streaming Jobs

Glue can run streaming workloads using managed Spark streaming capabilities.

Mental model:

```text
Streaming Source
      ↓
Micro-batches / streaming execution
      ↓
Transform
      ↓
Validate
      ↓
Sink
```

Use cases:

- event processing,
- continuous ingestion,
- near-real-time transformations,
- streaming quality checks.

Streaming jobs introduce additional concerns:

- checkpoints/state,
- late data,
- duplicate events,
- watermarking,
- restart behavior,
- maintenance/restart windows,
- source offsets.

Kinesis and MSK are covered later in G3. This module focuses on the Glue execution side.

---

# 8. Glue Versions and Runtime Selection

Glue jobs run against a managed Glue runtime.

The runtime determines important compatibility characteristics such as:

- Spark version,
- Python version,
- available libraries,
- supported features,
- runtime behavior.

AWS currently documents Glue job APIs with runtime/version configuration and notes that jobs created without an explicit Glue version can receive the current service default. Verify the current Glue runtime matrix before production deployment. citeturn1search4

### Production rule

Never say:

> "Glue 5.x always behaves exactly like Glue 4.x."

Instead:

```text
Glue Version
     ↓
Spark Version
     ↓
Python Version
     ↓
Library Compatibility
     ↓
Application Behavior
```

### Upgrade process

```text
Current runtime
      ↓
Dependency inventory
      ↓
Local test
      ↓
Integration test
      ↓
Performance test
      ↓
Canary
      ↓
Production rollout
```

---

# 9. Job Parameters

Do not hardcode environment-specific values:

```python
SOURCE = "s3://prod-bucket/orders/"
```

Prefer parameters:

```text
--SOURCE_PATH
--TARGET_PATH
--RUN_DATE
--ENV
--WATERMARK
```

AWS Glue supports job-level default arguments and run-level arguments. AWS currently documents a maximum size for the total job argument payload; verify current limits before designing large configuration payloads. citeturn0search8turn1search7

### Example script

```python
import sys
from awsglue.utils import getResolvedOptions

args = getResolvedOptions(
    sys.argv,
    [
        "JOB_NAME",
        "SOURCE_PATH",
        "TARGET_PATH",
    ],
)

source_path = args["SOURCE_PATH"]
target_path = args["TARGET_PATH"]
```

### Good parameters

```text
paths
dates
environment
mode
watermark
feature flags
quality policy
```

### Bad parameters

Avoid using job arguments as a database for:

- huge configuration documents,
- secrets,
- rapidly changing state,
- large datasets.

Secrets belong in a secret-management system.

---

# 10. IAM Execution Roles

A Glue job executes using an IAM role.

The role should provide only the permissions required by the job.

Example logical permissions:

```text
S3:
  read raw
  write curated
  write quarantine

Glue:
  read/update catalog where required

CloudWatch:
  logs/metrics where required

KMS:
  encrypt/decrypt where required

Secrets Manager:
  retrieve only the required secret
```

Avoid:

```json
{
  "Effect": "Allow",
  "Action": "*",
  "Resource": "*"
}
```

as the default.

### Least privilege lifecycle

```text
Prototype
  ↓
Observe actual permissions
  ↓
Remove unused permissions
  ↓
Restrict resources
  ↓
Review
  ↓
Production
```

---

# 11. Glue Script Locations and Deployment

A production script should be version controlled.

Conceptually:

```text
Git
 ↓
Build / validate
 ↓
Artifact
 ↓
S3 or supported source-control integration
 ↓
Glue Job
```

Do not make the AWS console the only copy of production code.

### Recommended repository organization

```text
jobs/
  glue/
    orders/
      main.py
      tests/
      requirements.txt
      README.md
```

The roadmap's lab repository can use:

```text
jobs/glue/
```

without creating those files as part of this Markdown module.

---

# 12. AWS CLI — Job Operations

Typical operational commands include:

```bash
aws glue get-job \
  --job-name orders-etl
```

```bash
aws glue start-job-run \
  --job-name orders-etl
```

```bash
aws glue get-job-run \
  --job-name orders-etl \
  --run-id jr_123456
```

```bash
aws glue get-job-runs \
  --job-name orders-etl
```

Create/update operations depend on the complete Job API structure.

### Production rule

For complex nested CLI payloads:

```text
AWS CLI help
+
current AWS API reference
+
small dry-run/plan
```

Do not rely on memory for deeply nested Glue job JSON.

---

# 13. boto3 — Job Operations

```python
import boto3

glue = boto3.client("glue")

run = glue.start_job_run(
    JobName="orders-etl",
    Arguments={
        "--SOURCE_PATH": "s3://example/raw/orders/",
        "--TARGET_PATH": "s3://example/silver/orders/",
    },
)

print(run["JobRunId"])
```

Inspect:

```python
run = glue.get_job_run(
    JobName="orders-etl",
    RunId=run["JobRunId"],
    PredecessorsIncluded=False,
)

print(run["JobRun"]["JobRunState"])
```

### Production automation

Wrap API calls with:

- retry strategy,
- structured logging,
- request identifiers,
- exception classification,
- timeouts where applicable,
- idempotent orchestration.

---

# 14. DynamicFrames

A DynamicFrame is an AWS Glue-specific distributed data abstraction designed for ETL workloads with schema irregularities.

AWS documents interoperability between DynamicFrames and Spark DataFrames through conversion methods such as `toDF()` and `fromDF()`. DynamicFrames also support `Choice` types for fields with inconsistent types across records. citeturn1search0turn1search2

### Why DynamicFrames exist

Suppose records contain:

```text
row 1: amount = 100
row 2: amount = "100.50"
row 3: amount = null
```

A conventional schema can struggle with this inconsistency.

DynamicFrames can represent ambiguous fields using a Choice-type model.

---

# 15. DataFrames

Spark DataFrames are the standard abstraction for most transformations.

Example:

```python
df = spark.read.parquet(
    "s3://example/raw/orders/"
)

result = (
    df
    .filter("order_id IS NOT NULL")
    .withColumnRenamed("customer", "customer_id")
)
```

DataFrames give you access to Spark's familiar:

- SQL expressions,
- joins,
- aggregations,
- window functions,
- partitioning,
- optimization,
- explain plans.

### Practical production pattern

```text
DynamicFrame
      ↓
Normalize / resolve schema issues
      ↓
DataFrame
      ↓
Spark transformations
      ↓
DataFrame
      ↓
Output
```

Most teams should not use DynamicFrames merely because the job is called "Glue."

---

# 16. DynamicFrame vs DataFrame

| Dimension | DynamicFrame | DataFrame |
|---|---|---|
| Glue integration | Strong | Strong |
| Schema irregularity | Excellent | Requires explicit handling |
| Choice types | Native | Standard Spark types |
| Spark ecosystem | Moderate | Excellent |
| Complex transformations | Possible | Usually preferred |
| Catalog integration | Convenient | Excellent through Spark/Glue |
| Learning priority | Understand deeply | Use heavily |

### Decision rule

Use DynamicFrames when:

```text
Glue-specific schema flexibility
or
Glue-native transforms
```

are useful.

Use DataFrames when:

```text
Spark-native transformations
performance
clarity
SQL/functions
```

are the priority.

---

# 17. Resolving Choice Types

Example:

```python
dyf = glueContext.create_dynamic_frame.from_catalog(
    database="raw",
    table_name="orders",
)

dyf = dyf.resolveChoice(
    specs=[
        ("amount", "cast:double")
    ]
)
```

AWS supports resolution actions such as casting, projecting a type, creating structs/columns, and matching a catalog schema. citeturn1search5

A useful pattern:

```text
Detect ambiguous field
       ↓
Understand why it is ambiguous
       ↓
Choose business-correct resolution
       ↓
Validate
       ↓
Write
```

Do not cast blindly.

If a producer sends:

```text
"$100.50"
```

casting to `double` may fail or produce incorrect handling unless the currency symbol is normalized first.

---

# 18. Converting Between DynamicFrames and DataFrames

```python
df = dyf.toDF()
```

Then:

```python
from awsglue.dynamicframe import DynamicFrame

dyf = DynamicFrame.fromDF(
    df,
    glueContext,
    "orders_dyf",
)
```

### Important

The `toDF()` options are for resolving DynamicFrame choice types, not for arbitrary CSV parsing configuration. AWS explicitly distinguishes these concerns. citeturn1search2

---

# 19. Reading from S3

DataFrame:

```python
df = spark.read.parquet(
    "s3://example/raw/orders/"
)
```

JSON:

```python
df = spark.read.json(
    "s3://example/raw/orders/"
)
```

CSV:

```python
df = (
    spark.read
    .option("header", True)
    .csv("s3://example/raw/orders/")
)
```

DynamicFrame:

```python
dyf = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={
        "paths": ["s3://example/raw/orders/"]
    },
    format="json",
)
```

### Production considerations

Ask:

- Is the source compressed?
- Is it columnar?
- Are files too small?
- Are schemas consistent?
- Is partition pruning possible?
- Are we reading unnecessary columns?
- Are we repeatedly scanning historical data?

---

# 20. Writing Partitioned Parquet

A common lake pattern:

```python
(
    df.write
      .mode("append")
      .partitionBy("year", "month", "day")
      .parquet("s3://example/silver/orders/")
)
```

Result:

```text
orders/
  year=2026/
    month=10/
      day=05/
      day=06/
```

### Why Parquet

Parquet is columnar and supports efficient analytical access.

Benefits:

- column pruning,
- compression,
- predicate pushdown,
- broad ecosystem support.

### But partitioning is not free

Bad partition design can create:

- huge partition counts,
- tiny files,
- metadata overhead,
- slow planning,
- difficult operations.

---

# 21. Small Files

Suppose a job creates:

```text
10,000 files × 5 MB
```

instead of:

```text
100 files × 500 MB
```

The total bytes may be similar, but the operational behavior is not.

Small files can increase:

- object metadata overhead,
- task scheduling overhead,
- query planning,
- S3 request volume,
- downstream processing overhead.

### Spark-side mitigation

Use appropriate repartition/coalesce strategies before writing.

But do not blindly:

```python
df.coalesce(1)
```

This creates a single-file bottleneck.

---

# 22. Iceberg Output

Glue can write to Iceberg-compatible tables.

Conceptually:

```text
Spark
 ↓
Iceberg writer
 ↓
S3 data files
+
Iceberg metadata
 ↓
Glue Catalog
 ↓
Query engines
```

The exact configuration depends on Glue runtime and Iceberg integration.

Production principle:

> Use table-format-aware writers and supported catalog integrations; do not manually manipulate Iceberg metadata files.

### Why Iceberg

Iceberg provides table semantics around:

- snapshots,
- schema evolution,
- partition evolution,
- metadata,
- atomic table operations,
- table-aware writes.

This is why Iceberg is different from simply writing Parquet folders.

---

# 23. Delta Lake and Hudi Awareness

Glue can interact with multiple transactional/table formats depending on runtime and configuration.

For this roadmap:

```text
Iceberg
=
Core
```

```text
Delta/Hudi
=
Awareness
```

The important engineering skill is recognizing that:

```text
Parquet files
≠
transactional lakehouse table
```

Table formats add metadata and transactional semantics on top of object storage.

---

# 24. Glue Data Catalog Integration from Jobs

A Glue job may consume catalog metadata:

```python
dyf = glueContext.create_dynamic_frame.from_catalog(
    database="bronze",
    table_name="orders",
)
```

This creates a convenient relationship:

```text
Data Catalog
      ↓
Glue Job
      ↓
DataFrame / DynamicFrame
      ↓
Transform
      ↓
Output
```

But do not let the catalog become an uncontrolled source of truth.

Production ownership should be clear:

```text
Who owns schema?
Who owns table location?
Who approves changes?
Who owns data quality?
```

---

# 25. Incremental Processing

A production pipeline should rarely process all historical data every time.

Full load:

```text
Day 1 → 1 TB
Day 2 → 1 TB
Day 3 → 1 TB
```

Every day scans:

```text
1 TB
1 TB
1 TB
```

Incremental:

```text
Day 1 → 1 TB
Day 2 → 50 GB new/changed
Day 3 → 45 GB new/changed
```

The goal:

```text
Process only what changed
```

Benefits:

- lower cost,
- lower runtime,
- smaller failure domain,
- faster recovery.

---

# 26. Job Bookmarks

AWS Glue job bookmarks track state so supported sources can avoid reprocessing previously handled data. AWS documents bookmark behavior for sources including S3 and JDBC and requires `job.init()` at the beginning and `job.commit()` at the end for bookmark state to be initialized/updated correctly. citeturn1search11

Basic lifecycle:

```text
Job Start
   ↓
job.init()
   ↓
Read eligible new data
   ↓
Transform
   ↓
Write
   ↓
job.commit()
```

Example:

```python
from awsglue.job import Job

job = Job(glueContext)

job.init(args["JOB_NAME"], args)

# processing...

job.commit()
```

### Important

A bookmark is not the same thing as business-level incremental state.

---

# 27. Bookmark Limitations

Bookmarks are useful but not universal.

They do not automatically solve:

- complex CDC semantics,
- late-arriving corrections,
- arbitrary backfills,
- cross-source synchronization,
- business watermark logic,
- idempotent target writes,
- deduplication,
- exactly-once business semantics.

Use:

```text
Bookmark
+
idempotent target
+
validation
+
recovery strategy
```

rather than:

```text
Bookmark = guaranteed correctness
```

---

# 28. Custom Incremental State

Sometimes you need explicit state.

Example:

```text
watermark = 2026-10-06T12:00:00Z
```

Store it in an appropriate state store, depending on the architecture.

Conceptually:

```text
Read current state
      ↓
Read data > watermark
      ↓
Transform
      ↓
Publish successfully
      ↓
Advance watermark
```

### Critical ordering rule

Do not update state before the output is durable.

Bad:

```text
Advance watermark
   ↓
Write output
   ↓
Write fails
```

Now the next run may skip data.

Better:

```text
Read watermark
   ↓
Process
   ↓
Validate
   ↓
Publish
   ↓
Commit state
```

---

# 29. Watermarking

A watermark identifies the progress boundary.

Example:

```text
last_processed_updated_at
```

Query:

```sql
SELECT *
FROM source
WHERE updated_at > :watermark;
```

### Problems

What if:

```text
record updated_at = 10:00
```

arrives at:

```text
10:05
```

after the watermark has already advanced?

You need a late-arrival strategy.

Common patterns:

```text
Lookback window
Deduplication
Versioned writes
CDC log position
Event-time watermark
```

Example:

```text
current watermark = 10:00

read:
updated_at > 09:55
```

Then deduplicate.

---

# 30. Bookmark vs Watermark

| Feature | Bookmark | Custom watermark |
|---|---|---|
| Managed by Glue | Yes | No |
| Simple S3/JDBC incremental | Strong | Strong |
| Business semantics | Limited | Strong |
| Backfill control | Limited | Strong |
| Custom late-data logic | Limited | Strong |
| Engineering effort | Low | Higher |
| Visibility/control | Moderate | High |

### Senior-engineer rule

Use the simplest state mechanism that correctly represents the business semantics.

---

# 31. Idempotency

A pipeline is idempotent when retrying the same logical input does not create an incorrect additional result.

Bad:

```text
Input batch
 ↓
append
 ↓
retry
 ↓
append again
```

Result:

```text
duplicate records
```

Better:

```text
Input batch
 ↓
deterministic transformation
 ↓
idempotent write
```

For lakehouse tables, table-aware merge/upsert semantics can be used where appropriate.

---

# 32. Retry Semantics

Retries are normal.

Failures include:

- transient network error,
- temporary AWS service error,
- executor failure,
- database timeout,
- dependency installation failure,
- malformed input,
- quality failure.

Not all failures should be retried.

### Retry classification

```text
Transient infrastructure
→ retry

Rate limiting
→ retry with backoff

Bad data
→ quarantine/fail

Schema contract violation
→ fail / investigate

Permission denied
→ fail / fix configuration

Code bug
→ fail / deploy fix
```

A retry policy without failure classification can amplify incidents.

---

# 33. Production Incremental Pattern

```text
                 SOURCE
                   |
                   v
             Read State
                   |
                   v
          Identify Increment
                   |
                   v
              Transform
                   |
                   v
              Validate
                   |
              +----+----+
              |         |
             FAIL      PASS
              |         |
              v         v
        Quarantine   Publish
                        |
                        v
                  Commit State
```

This pattern is more robust than:

```text
read → transform → append → hope
```

---

# 34. JDBC Sources

Glue can connect to JDBC-compatible data sources.

Examples:

```text
PostgreSQL
MySQL
SQL Server
Oracle
other supported JDBC sources
```

A common architecture:

```text
Private Database
      ↓
VPC
      ↓
Glue Connection
      ↓
Glue Job
      ↓
S3 / Iceberg
```

---

# 35. VPC JDBC Networking

When a Glue job needs a private JDBC source, networking becomes part of the ETL system.

Check:

```text
VPC
 ↓
Subnet
 ↓
Route table
 ↓
Security group
 ↓
DNS
 ↓
Database endpoint
 ↓
Database listener
```

AWS documents Glue connection properties for VPC JDBC connections, including VPC, subnet and security-group configuration. citeturn1search12

### Security group reasoning

The database must allow the Glue job's network identity to connect.

Do not solve:

```text
connection timeout
```

by opening:

```text
0.0.0.0/0
```

unless there is an extraordinary, explicitly justified requirement.

---

# 36. Secrets

Never write:

```python
password = "SuperSecret123"
```

Use a secret-management mechanism such as AWS Secrets Manager.

Conceptual flow:

```text
Glue Job
   ↓
IAM permission
   ↓
Secrets Manager
   ↓
Credential
   ↓
JDBC connection
```

The IAM role should only be allowed to retrieve the specific secret required.

---

# 37. Glue Connections

A Glue connection can hold connection metadata needed to connect to data sources.

Typical concerns:

- JDBC URL
- network configuration
- authentication mechanism
- Secrets Manager integration
- SSL
- security groups

Treat connection definitions as infrastructure.

Prefer:

```text
Terraform / CloudFormation / controlled IaC
```

over undocumented console-only configuration.

---

# 38. Local Glue Development

AWS provides local development options for Glue Spark jobs, including Glue Docker images and interactive development workflows. The Glue documentation explicitly supports local/remote development using Docker and notes that this can help test scripts without incurring Glue job-run cost. citeturn0search5

A productive loop:

```text
Edit
 ↓
Local test
 ↓
Unit test
 ↓
Package
 ↓
Deploy
 ↓
Small AWS run
 ↓
Observe
```

Do not make every debugging iteration a paid cloud run.

---

# 39. Interactive Sessions and Notebooks

Interactive sessions are useful for:

- exploration,
- prototyping,
- schema inspection,
- testing transformations,
- learning Glue APIs.

They are not a substitute for:

- version control,
- automated testing,
- deployment,
- production orchestration.

A production workflow should eventually become:

```text
Code
 ↓
Test
 ↓
Review
 ↓
Deploy
 ↓
Run
```

---

# 40. External Python Libraries

Glue supports additional Python dependencies.

AWS documents `--additional-python-modules` and additional packaging approaches; current Glue versions also support requirements-file and bundled-wheel approaches. AWS warns that unpinned runtime package installation is risky for production and recommends frozen artifacts for stronger reproducibility. citeturn1search3turn1search10

Example:

```text
--additional-python-modules
awswrangler==<pinned-version>
```

### Production hierarchy

Prefer:

```text
Frozen artifacts
>
Pinned dependencies
>
Unpinned runtime installation
```

### Why

Uncontrolled dependencies can cause:

```text
Yesterday:
job works

Today:
dependency resolver selects new version

Result:
job fails
```

---

# 41. Dependency Strategy

Maintain:

```text
requirements.txt
```

or a controlled artifact bundle.

Document:

```text
Python version
Glue runtime
Spark version
Package versions
Native dependencies
```

Test the exact combination.

### Dependency incident

```text
Job failed after deployment
 ↓
Compare runtime
 ↓
Compare dependency versions
 ↓
Compare packaging
 ↓
Check native library compatibility
 ↓
Reproduce locally
```

---

# 42. Glue Studio

Glue Studio provides a visual interface for developing and monitoring ETL jobs. AWS also supports script-based and notebook workflows. citeturn0search5

Use it for:

- learning,
- visual prototyping,
- simple transformations,
- understanding generated ETL patterns.

Do not assume:

```text
Visual = production-ready
```

Production requirements still include:

- code review,
- tests,
- deployment control,
- observability,
- security,
- reproducibility.

---

# 43. Glue Workflows and Triggers

Glue provides workflows/triggers for coordinating Glue-related processes.

This module only teaches awareness.

For larger production orchestration, the roadmap later covers:

```text
Step Functions
MWAA
EventBridge
```

A useful distinction:

```text
Glue Job
=
processing

Orchestrator
=
coordination
```

Do not place complex business orchestration inside a single ETL script.

---

# 44. Spark Tuning in Glue

Your Spark knowledge from Module 2.14 transfers directly.

Key dimensions:

```text
Input partitions
Shuffle
Join strategy
Data skew
Broadcast
Caching
Output partitions
File sizes
```

### First rule

Do not tune by guessing.

Use evidence:

```text
Job duration
Spark UI
Stage metrics
Shuffle volume
Task distribution
Input/output sizes
Executor memory
```

---

# 45. Partitioning and Repartitioning

Bad:

```python
df.repartition(5000)
```

without evidence.

Also bad:

```python
df.coalesce(1)
```

for a large production dataset.

Better:

```text
Estimate data volume
 ↓
Understand parallelism
 ↓
Observe stage behavior
 ↓
Tune partition count
```

The correct value depends on workload characteristics and Glue runtime.

---

# 46. Data Skew

Suppose:

```text
customer_id = 1
```

contains:

```text
70% of all rows
```

A join can become skewed.

Symptoms:

```text
Most tasks finish
One/few tasks remain
```

Potential strategies:

- salting,
- broadcast where appropriate,
- repartitioning,
- pre-aggregation,
- skew-aware design.

Do not automatically increase worker count.

If one task has 100× the data, more workers may not solve the fundamental imbalance.

---

# 47. Broadcast Joins

If a dimension table is small enough:

```python
from pyspark.sql.functions import broadcast

result = fact.join(
    broadcast(dim),
    "customer_id",
)
```

Potential benefit:

```text
Avoid large shuffle of dimension table
```

But broadcasting a table that is not actually small can cause memory failures.

Always validate:

```text
dimension size
executor memory
actual Spark plan
```

---

# 48. Reading the Spark UI

For a slow Glue job, inspect:

```text
Jobs
 ↓
Stages
 ↓
Tasks
 ↓
Input
 ↓
Shuffle
 ↓
Task duration
 ↓
Executor behavior
```

Look for:

- one stage dominating runtime,
- high shuffle,
- skew,
- spills,
- long-tail tasks,
- excessive input,
- too many small files.

### Senior-engineer habit

Do not say:

> "The job needs more workers."

Say:

> "Stage 4 has a long-tail task distribution caused by skew on `customer_id`; increasing workers alone will not remove the skew."

---

# 49. Glue Auto Scaling

AWS Glue Auto Scaling can add/remove workers based on workload parallelism for supported Glue versions and job types. AWS currently documents Auto Scaling for Glue ETL, interactive sessions and streaming jobs on Glue 3.0 and later. citeturn1search9

Mental model:

```text
Workload grows
 ↓
Workers increase

Workload shrinks
 ↓
Workers decrease
```

Benefits:

- less manual sizing,
- better resource utilization,
- potentially lower cost.

But Auto Scaling does not eliminate the need for:

- good partitioning,
- good joins,
- skew handling,
- efficient input/output,
- reasonable maximum workers.

---

# 50. Flex Execution Class

AWS Glue supports `STANDARD` and `FLEX` execution classes for applicable Spark jobs. FLEX is intended for workloads where startup/completion timing can vary. citeturn1search4turn1search8

Use FLEX for:

- non-urgent batch,
- development,
- backfills,
- maintenance,
- workloads where latency is less important.

Prefer STANDARD for:

- strict SLAs,
- latency-sensitive production workloads.

### Decision

```text
Urgent?
 |
 +-- YES → STANDARD
 |
 +-- NO
      ↓
Can completion time vary?
      |
     YES → FLEX candidate
```

Always verify current pricing and availability before cost modeling.

---

# 51. Cost Model

Conceptually:

```text
Glue Cost
=
Compute
+
Runtime
+
Worker Capacity
+
Additional Services
```

The exact pricing model depends on job type, runtime and region.

Never hardcode remembered prices into architecture documents.

Verify current AWS pricing before deployment.

### Cost drivers

- oversized workers,
- excessive runtime,
- full reloads,
- unnecessary retries,
- inefficient joins,
- repeated scans,
- small files,
- excessive data movement,
- unnecessary DQ runs,
- unnecessary development runs.

---

# 52. Cost Optimization

Use:

```text
Right-size
+
Incremental processing
+
Efficient Spark
+
Appropriate execution class
+
Auto Scaling
+
Small development datasets
+
Local testing
```

### Measure before optimizing

Track:

```text
Input GB
Output GB
Duration
Worker count
Execution class
Retry count
Quality-check overhead
```

Then compare.

---

# 53. AWS Glue Data Quality

AWS Glue Data Quality provides managed data-quality evaluation using DQDL. It supports rules, rulesets, scores, recommendations, anomaly detection and integrations with Glue ETL and the Data Catalog. citeturn0search1turn0search4

Mental model:

```text
Dataset
   ↓
Rules
   ↓
Evaluation
   ↓
Results
   ↓
Quality Gate
   ↓
PASS / FAIL / QUARANTINE
```

Data quality is not just:

```text
"Is the pipeline running?"
```

It asks:

```text
"Is the data trustworthy?"
```

---

# 54. Data Quality Dimensions

Common dimensions:

```text
Completeness
Uniqueness
Validity
Consistency
Accuracy
Timeliness
Integrity
```

Examples:

```text
order_id cannot be null
order_id must be unique
amount >= 0
status ∈ {PENDING, PAID, CANCELLED}
order_date cannot be in impossible future range
customer_id must reference known customer
```

---

# 55. DQDL

DQDL is the Data Quality Definition Language used to define rules.

Example:

```text
Rules = [
    IsComplete "order_id",
    IsUnique "order_id",
    ColumnValues "amount" >= 0,
    ColumnValues "status" in ["PENDING", "PAID", "CANCELLED"]
]
```

Treat examples as patterns and verify exact supported syntax against the current DQDL reference before deployment.

AWS currently documents a broad built-in rule set and a DQDL rule builder. citeturn0search10

---

# 56. Rule Categories

Think in categories.

### Completeness

```text
IsComplete
```

### Uniqueness

```text
IsUnique
```

### Range

```text
ColumnValues
```

### Referential checks

```text
CustomSQL
```

### Row-level logic

```text
RowCount
```

### Distribution/statistics

```text
Mean
Sum
StandardDeviation
DistinctValuesCount
```

The exact supported rule/analyzer vocabulary should be verified against the current AWS DQDL documentation.

---

# 57. Rulesets

A ruleset is a collection of quality rules.

Conceptually:

```text
orders_quality
│
├── completeness
├── uniqueness
├── validity
├── range
└── referential integrity
```

Separate rulesets when ownership or operational policy differs.

For example:

```text
critical_orders_quality
```

versus:

```text
analytics_orders_observability
```

Do not create one giant ruleset containing every conceivable check.

---

# 58. Data Quality Evaluation

Evaluation:

```text
Dataset
 ↓
Ruleset
 ↓
Execution
 ↓
Rule results
 ↓
Quality score
```

AWS documents data quality scores as the percentage of evaluated rules that pass. citeturn0search1

### Important

A score alone is not enough.

For example:

```text
99% quality
```

could still hide:

```text
1 failed critical rule
```

Therefore define severity.

---

# 59. Quality Gates

A quality gate decides whether downstream processing may continue.

Example:

```text
Critical rules
   ↓
Must pass
```

```text
Warning rules
   ↓
Can continue
```

Conceptual:

```text
DQ
 |
 +── Critical FAIL → STOP / QUARANTINE
 |
 +── Warning FAIL → ALERT + CONTINUE
 |
 └── PASS → PUBLISH
```

### Why severity matters

Not all data-quality failures have equal business impact.

Example:

```text
currency missing
```

may be critical.

While:

```text
optional marketing_source missing
```

may be warning-level.

---

# 60. Quarantine

Quarantine means isolating data that fails validation.

```text
Input
 ↓
Transform
 ↓
DQ
 ├── PASS → curated
 └── FAIL → quarantine
```

A useful quarantine record contains:

```text
original data
failure reason
rule name
pipeline run ID
ingestion timestamp
source identifier
schema version
```

### Quarantine is not trash

It is an operational recovery mechanism.

```text
Quarantine
 ↓
Investigate
 ↓
Correct
 ↓
Reprocess
```

---

# 61. Bad-Record Handling

There are two broad categories.

### Row-level failure

Example:

```text
amount = -500
```

You may isolate the row.

### Dataset-level failure

Example:

```text
90% of rows have invalid schema
```

Do not quietly quarantine individual rows and continue.

Fail the dataset.

### Production principle

```text
Small, understood bad-record rate
→ quarantine

Structural/systemic failure
→ stop pipeline
```

---

# 62. Data Quality Recommendations

AWS Glue Data Quality can generate rule recommendations from data. AWS documents BASIC and ADVANCED recommendation modes; current documentation notes that ADVANCED recommendations use sampled table data and Amazon Bedrock, and AWS recommends reviewing generated rules before using them. citeturn0search7turn0search6

Use recommendations as:

```text
Discovery
 ↓
Candidate rules
 ↓
Human review
 ↓
Approved rules
 ↓
Production ruleset
```

Never treat automatically generated recommendations as authoritative business contracts.

---

# 63. Anomaly Detection

Traditional rule:

```text
RowCount > 1,000,000
```

can become stale.

Anomaly detection asks:

```text
What does normal look like historically?
```

AWS Glue Data Quality anomaly detection uses historical statistics and machine-learning-based detection. AWS documents that anomaly detection requires historical observations and supports multiple statistics/rule types. citeturn0search0turn0search3

Conceptual flow:

```text
Historical statistics
       ↓
Baseline
       ↓
New observation
       ↓
Expected range
       ↓
Anomaly?
```

---

# 64. Historical Baselines

Example:

```text
Daily order count:

Monday    1.0M
Tuesday   1.1M
Wednesday 1.05M
Thursday  1.08M
Friday    1.2M
```

A new value:

```text
120K
```

may be suspicious.

A static rule:

```text
RowCount > 100K
```

would miss the business context.

Anomaly detection can reason from historical behavior.

AWS currently notes that anomaly detection requires a minimum number of historical data points and that detected anomalies can influence subsequent model behavior unless explicitly handled. citeturn0search0

---

# 65. Anomaly Detection Is Not a Quality Gate by Itself

Anomaly:

```text
unusual
```

does not necessarily mean:

```text
invalid
```

Example:

```text
Black Friday
```

may produce an enormous traffic spike.

Therefore:

```text
Anomaly
 ↓
Investigate
 ↓
Classify
 ├── expected event
 └── actual incident
```

Do not automatically reject every anomaly.

---

# 66. Glue Data Quality in ETL

Data quality can be applied inside an ETL pipeline.

Conceptual:

```text
Read
 ↓
Transform
 ↓
Evaluate Data Quality
 ↓
Quality result
 ↓
Conditional publish
```

AWS documents Data Quality integration with Glue ETL and supports identifying failing records in ETL workflows. citeturn0search4turn0search9

### Example architecture

```text
DynamicFrame
     ↓
EvaluateDataQuality
     ↓
+----+----+
|         |
PASS     FAIL
|         |
v         v
Curated  Quarantine
```

---

# 67. Quality Gates in Code

A conceptual pattern:

```python
quality_result = evaluate_quality(df)

if quality_result.is_critical_failure:
    write_quarantine(df)
    raise RuntimeError("Critical data-quality failure")

write_curated(df)
```

The implementation can use AWS Glue Data Quality transforms or catalog evaluation APIs depending on the pipeline.

The key engineering concept is:

> **Validation must occur before publication, not after consumers discover the problem.**

---

# 68. Testing Glue Jobs

Testing should happen at several layers.

```text
Unit
 ↓
Transformation
 ↓
Data contract
 ↓
Integration
 ↓
AWS execution
 ↓
Production monitoring
```

### Unit test

Test pure transformation functions.

```python
def normalize_status(value: str) -> str:
    return value.strip().upper()
```

Test:

```python
assert normalize_status(" paid ") == "PAID"
```

### DataFrame test

Create a small local DataFrame and verify:

- columns,
- types,
- transformations,
- duplicates,
- null behavior.

---

# 69. Data Quality Testing

Test the rules themselves.

Example:

```text
Valid dataset
 → expected PASS

Null order_id
 → expected FAIL

Duplicate order_id
 → expected FAIL

Negative amount
 → expected FAIL

Unknown customer
 → expected FAIL
```

A rule that has never been tested against bad data is not production-ready.

---

# 70. Integration Testing

An integration test should verify:

```text
S3 input
 ↓
Glue job
 ↓
Catalog/output
 ↓
Quality result
```

Keep test data small.

Validate:

- output schema,
- partition layout,
- record counts,
- quality outcomes,
- quarantine behavior.

---

# 71. Failure Injection

Production readiness requires intentionally breaking things.

Test:

```text
Missing input
Malformed JSON
Schema drift
Duplicate records
Invalid numeric value
Permission denied
JDBC timeout
Dependency mismatch
Worker memory pressure
Quality-rule failure
```

For every failure:

```text
Expected behavior
Actual behavior
Detection
Recovery
```

---

# 72. Observability

A production Glue job should expose:

```text
Logs
Metrics
Run status
Input volume
Output volume
Quality score
Failed-record count
Duration
Retries
```

Structured log example:

```json
{
  "job": "orders-etl",
  "run_id": "example",
  "source": "orders",
  "input_rows": 1200000,
  "output_rows": 1185000,
  "quarantine_rows": 15000,
  "quality_score": 0.96,
  "status": "SUCCESS_WITH_QUARANTINE"
}
```

Do not log:

```text
password
secret
access token
full sensitive record
```

---

# 73. Operational Metrics

Useful metrics:

```text
job_duration
input_bytes
input_rows
output_rows
quarantine_rows
dq_score
dq_failed_rules
retry_count
records_per_second
shuffle_bytes
executor_memory_pressure
```

Business metrics can include:

```text
orders_processed
payments_processed
customers_processed
```

Technical metrics and business metrics should be distinguishable.

---

# 74. Logging Strategy

Good logs answer:

```text
What happened?
When?
Which job?
Which run?
Which input?
Which partition?
What state?
What failed?
Why?
```

Example:

```text
run_id=abc123
dataset=orders
partition=2026-10-06
input_rows=1,200,000
quality_failed=15,000
action=quarantine
```

Avoid noisy per-record logs for millions of records.

---

# 75. Error Handling

Classify errors.

```text
INPUT_ERROR
SCHEMA_ERROR
QUALITY_ERROR
NETWORK_ERROR
AUTHORIZATION_ERROR
DEPENDENCY_ERROR
COMPUTE_ERROR
UNKNOWN_ERROR
```

Then map:

```text
INPUT_ERROR
→ quarantine / fail

SCHEMA_ERROR
→ fail + alert

QUALITY_ERROR
→ quality gate

NETWORK_ERROR
→ retry

AUTHORIZATION_ERROR
→ fail + operator action

COMPUTE_ERROR
→ retry / tune

DEPENDENCY_ERROR
→ rollback package
```

---

# 76. Production Retry Policy

Do not retry everything.

A retry loop can turn:

```text
one failure
```

into:

```text
ten failures
```

and create:

- cost,
- duplicate output,
- downstream pressure.

Use:

```text
bounded retries
+
exponential backoff
+
jitter
+
failure classification
```

---

# 77. Idempotent Output Design

Example:

```text
Input batch ID = 20261006-001
```

Before writing:

```text
Does this batch already exist?
```

For table-aware systems:

```text
MERGE / upsert / transactional commit
```

may be appropriate.

For append-only data:

```text
deterministic partition
+
deduplication key
+
batch identity
```

can help.

The exact strategy depends on the table format and business semantics.

---

# 78. Production Orders Pipeline

The required capstone architecture:

```text
              RAW DATA

        orders JSON
        customers CSV
             |
             v
        S3 Landing
             |
             v
        Glue Spark Job
             |
      +------+------+ 
      |             |
    Clean         Normalize
      |             |
      +------+------+
             |
          Join
             |
        Deduplicate
             |
             v
       Data Quality
        /        \
      PASS        FAIL
       |           |
       v           v
   Iceberg     Quarantine
       |
       v
 Glue Catalog
       |
       v
 Analytics
```

---

# 79. Capstone Requirements

Build a conceptual production pipeline that includes:

```text
[ ] Glue Spark job
[ ] Parameters
[ ] IAM role
[ ] S3 input
[ ] DynamicFrame awareness
[ ] DataFrame transformations
[ ] Incremental processing
[ ] Bookmark or custom watermark
[ ] Idempotent output
[ ] Partitioned Parquet or Iceberg
[ ] Data Catalog integration
[ ] DQDL rules
[ ] Quality gate
[ ] Quarantine
[ ] Logging
[ ] Metrics
[ ] Failure handling
[ ] Retry strategy
[ ] Tests
[ ] Dependency strategy
[ ] Security
[ ] Cost model
```

---

# 80. Lab 1 — Simple Glue Spark Transformation

## Objective

Run a simple Spark transformation in Glue.

## Input

```text
s3://example/raw/orders/
```

## Transform

```python
df = spark.read.json(source)

clean = (
    df
    .filter("order_id IS NOT NULL")
    .withColumn("amount", F.col("amount").cast("double"))
)
```

## Expected result

Rows without `order_id` are removed.

## Failure scenario

Make `amount` contain invalid strings.

## Verification

Check:

```text
row count
schema
invalid records
```

## Cleanup

Delete temporary AWS resources and verify no billable job remains.

## Production lesson

Start with deterministic transformations before adding optimization.

---

# 81. Lab 2 — DynamicFrame to DataFrame

## Objective

Understand schema flexibility.

Create inconsistent data:

```json
{"order_id": 1, "amount": 10}
{"order_id": 2, "amount": "20"}
```

Read as a DynamicFrame.

Inspect:

```python
dyf.printSchema()
```

Resolve the ambiguity.

Convert:

```python
df = dyf.toDF()
```

Compare:

```text
DynamicFrame
vs
DataFrame
```

---

# 82. Lab 3 — Parameterized Job

Pass:

```text
--SOURCE_PATH
--TARGET_PATH
--RUN_DATE
```

Verify the job does not contain environment-specific paths in the code.

Failure injection:

```text
omit TARGET_PATH
```

Expected:

```text
clear startup failure
```

---

# 83. Lab 4 — Partitioned Parquet

Write:

```text
year
month
day
```

Then inspect the S3 layout.

Measure:

```text
file count
file sizes
partition count
```

Do not optimize based solely on file count. Relate it to data volume and downstream access.

---

# 84. Lab 5 — Incremental Processing

Run:

```text
Batch A
Batch B
Batch C
```

Process only new data.

Then rerun:

```text
Batch B
```

The output should remain correct.

This is where you validate idempotency rather than simply validating bookmark behavior.

---

# 85. Lab 6 — Bookmark Investigation

Test:

```text
Run 1
Run 2
Run 3
```

Record:

```text
input discovered
input processed
bookmark state
output
```

Then intentionally reset/alter the test state according to current Glue bookmark controls.

Document:

```text
What changed?
What data was reprocessed?
Was output still correct?
```

---

# 86. Lab 7 — Iceberg Output

Create a small Iceberg table using a supported Glue runtime/configuration.

Verify:

```text
table identity
schema
data
snapshot behavior
catalog visibility
```

Compare:

```text
Parquet folder
vs
Iceberg table
```

---

# 87. Lab 8 — Basic Data Quality

Create rules:

```text
order_id complete
order_id unique
amount >= 0
status valid
```

Inject bad data.

Observe:

```text
rule result
quality score
failed records
```

---

# 88. Lab 9 — Quality Gate

Define:

```text
Critical:
order_id completeness
order_id uniqueness

Warning:
optional field completeness
```

Expected:

```text
Critical fail → stop publish
Warning fail → alert but continue
```

Document the business rationale.

---

# 89. Lab 10 — Quarantine

Create:

```text
curated/
quarantine/
```

Route invalid records to:

```text
quarantine/
```

Attach failure metadata.

Verify:

```text
PASS → curated
FAIL → quarantine
```

---

# 90. Lab 11 — Anomaly Detection

Collect historical observations.

Choose a statistic such as:

```text
RowCount
Completeness
Mean
```

Inject an abnormal value.

Observe the anomaly.

Then ask:

```text
Is it actually a data defect?
```

Test a legitimate business spike.

---

# 91. Lab 12 — JDBC

Connect to a controlled test database.

Architecture:

```text
JDBC
 ↓
VPC
 ↓
Glue
 ↓
S3
```

Test:

```text
valid connection
invalid security group
invalid credentials
DNS failure
database unavailable
```

Do not expose the database publicly simply to make the lab easier.

---

# 92. Lab 13 — Failure Injection

Inject:

```text
missing input
bad schema
invalid credentials
quality failure
network failure
dependency failure
```

For each:

```text
Detect
 ↓
Classify
 ↓
Retry or fail
 ↓
Alert
 ↓
Recover
```

---

# 93. Lab 14 — Performance Optimization

Create a deliberately inefficient job.

Baseline:

```text
duration
worker count
input size
shuffle
output size
```

Then test one change at a time:

```text
partitioning
projection
broadcast
repartition
worker size
auto scaling
```

Do not change five variables at once.

---

# 94. Lab 15 — Production Pipeline

Combine:

```text
S3
 ↓
Glue Spark
 ↓
Incremental state
 ↓
Transform
 ↓
DQ
 ├── PASS → Iceberg
 └── FAIL → quarantine
 ↓
Catalog
 ↓
Observability
```

Produce a runbook describing:

- normal run,
- failed run,
- replay,
- backfill,
- quality failure,
- schema change,
- rollback.

---

# 95. Break/Fix Incident 1 — Out of Memory

## Symptom

```text
Executor lost
OutOfMemoryError
```

Investigate:

```text
data volume
skew
collect()
large joins
broadcast size
partitioning
worker type
```

### Common bad fix

```text
Add more workers
```

without understanding the memory pattern.

### Better approach

```text
Identify stage
 ↓
Identify memory-heavy operation
 ↓
Remove collect()
 ↓
Fix skew/join
 ↓
Adjust partitions
 ↓
Right-size workers
```

---

# 96. Break/Fix Incident 2 — Job 5× Slower

Trace:

```text
Input
 ↓
Read
 ↓
Transform
 ↓
Join
 ↓
Shuffle
 ↓
Output
```

Use Spark UI evidence.

Questions:

- Did input volume change?
- Did partition count change?
- Did a join become skewed?
- Did broadcast stop working?
- Did files become tiny?
- Did a source become slower?

---

# 97. Break/Fix Incident 3 — Data Reprocessed

Investigate:

```text
bookmark
 ↓
job initialization
 ↓
job commit
 ↓
input path
 ↓
source semantics
 ↓
state reset
```

Then inspect target idempotency.

Even if the source state is correct, the target should not become corrupt after a legitimate retry.

---

# 98. Break/Fix Incident 4 — Duplicate Records

Possible causes:

```text
append retry
duplicate input
bookmark reset
late data
parallel writers
non-idempotent logic
```

Remediation:

```text
identify business key
deduplicate
make output idempotent
control retries
```

---

# 99. Break/Fix Incident 5 — Data Quality Failure

Investigate:

```text
failed rule
actual value
expected value
source change
threshold
upstream incident
```

Do not simply disable the rule.

Ask:

> Is the rule wrong, or is the data wrong?

---

# 100. Break/Fix Incident 6 — Schema Drift

Trace:

```text
Source
 ↓
Raw
 ↓
Glue read
 ↓
Transformation
 ↓
DQ
 ↓
Output
```

Identify the first point where the schema became incompatible.

---

# 101. Break/Fix Incident 7 — JDBC Timeout

Check:

```text
VPC
Subnet
Route
Security Group
DNS
Database
Credentials
SSL
```

Classify:

```text
network
authentication
database capacity
configuration
```

Do not immediately increase Glue workers.

---

# 102. Production Security Architecture

```text
IAM Identity Center / assumed role
              ↓
         Glue Job Role
              ↓
      +-------+-------+
      |       |       |
     S3     Glue     KMS
      |       |       |
      +-------+-------+
              |
       Secrets Manager
              |
          JDBC Source
```

Security principles:

```text
Least privilege
Private access
Encryption
Secret isolation
Auditability
No hardcoded credentials
```

---

# 103. Networking Checklist

For private JDBC:

```text
[ ] Correct VPC
[ ] Correct subnet
[ ] Route exists
[ ] DNS works
[ ] Security group permits traffic
[ ] Database accepts source
[ ] SSL configured
[ ] Credentials valid
[ ] Secrets Manager accessible
[ ] Required AWS endpoints/routes available
```

For S3 access from restricted networking, also reason about appropriate VPC endpoints/private connectivity and IAM.

---

# 104. Secrets Checklist

```text
[ ] Secret in Secrets Manager
[ ] Job role can retrieve only required secret
[ ] Secret not in source code
[ ] Secret not in Git
[ ] Secret not in logs
[ ] Rotation strategy considered
[ ] Database user least privilege
```

---

# 105. Deployment Strategy

A production Glue deployment should resemble:

```text
Developer
   ↓
Git
   ↓
Unit tests
   ↓
Static checks
   ↓
Package
   ↓
Infrastructure plan
   ↓
Review
   ↓
Deploy
   ↓
Integration test
   ↓
Canary
   ↓
Production
```

Avoid:

```text
Edit console
 ↓
Run production
 ↓
Hope
```

---

# 106. Runbook Template

## Job

```text
orders-etl
```

## Purpose

```text
Transform raw orders into curated Iceberg orders.
```

## Inputs

```text
s3://.../raw/orders/
```

## Outputs

```text
silver.orders
```

## State

```text
bookmark / watermark
```

## Quality gates

```text
order_id complete
order_id unique
amount >= 0
status valid
```

## Failure actions

```text
quality failure → quarantine
network failure → retry
schema failure → stop
permission failure → operator
```

## Recovery

```text
Identify failed input
Validate corrected data
Replay
Verify idempotency
```

---

# 107. Production Decision Matrix

| Decision | Prefer A | Prefer B |
|---|---|---|
| Large distributed ETL | Spark | Python shell |
| Tiny utility | Python shell | Spark |
| Stable schema | DataFrame | DynamicFrame |
| Irregular source schema | DynamicFrame first | DataFrame after resolution |
| Simple incremental S3 | Bookmark | Custom state |
| Complex business watermark | Custom state | Bookmark |
| Urgent job | STANDARD | FLEX |
| Non-urgent batch | FLEX candidate | STANDARD |
| Exploratory development | Interactive session | Production job |
| Production code | Git/IaC | Console-only |
| Critical DQ failure | Stop/quarantine | Continue |
| Expected anomaly | Investigate | Automatically reject |
| Repeated duplicate failures | Idempotent write | Append-only retry |

---

# 108. Common Beginner Mistakes

1. Treating Glue as magic.
2. Assuming Spark knowledge is unnecessary.
3. Using DynamicFrames everywhere without understanding DataFrames.
4. Hardcoding paths.
5. Hardcoding credentials.
6. Ignoring job parameters.
7. Running full loads every day.
8. Treating bookmarks as exactly-once guarantees.
9. Updating watermark state before publishing output.
10. Appending on every retry.
11. Creating millions of tiny files.
12. Broadcasting large tables.
13. Increasing worker count without investigating skew.
14. Installing unpinned libraries in production.
15. Running production code only from the console.
16. Treating DQ scores as business truth.
17. Automatically rejecting every anomaly.
18. Sending every bad record to quarantine.
19. Quarantining systemic schema failures instead of stopping.
20. Opening databases publicly to fix networking.
21. Giving Glue AdministratorAccess.
22. Ignoring retry-induced duplicates.
23. Failing to test backfills.
24. Ignoring late-arriving data.
25. Disabling quality rules when they fail.

---

# 109. Senior Data Engineer Mental Model

When designing a Glue pipeline, ask in this order:

```text
1. What is the business output?
        ↓
2. What is the source contract?
        ↓
3. What changes incrementally?
        ↓
4. What state is required?
        ↓
5. What transformations are needed?
        ↓
6. What table format should be used?
        ↓
7. What quality rules define "good"?
        ↓
8. What happens to bad data?
        ↓
9. What happens on retry?
        ↓
10. How is it observed?
        ↓
11. How is it secured?
        ↓
12. What does it cost?
```

This sequence prevents engineers from jumping directly to:

> "Which Glue worker type should I choose?"

---

# 110. End-to-End Architecture

```text
                  DATA SOURCES
                       |
          +------------+------------+
          |            |            |
         S3          JDBC        Stream
          |            |            |
          +------------+------------+
                       |
                    Landing
                       |
                       v
                +-------------+
                | Glue Spark  |
                |    Job      |
                +-------------+
                       |
              Incremental State
                       |
                       v
                 Transform
                       |
                  Validate
                       |
                 Data Quality
                  /        \
               PASS        FAIL
                |            |
                v            v
             Iceberg     Quarantine
                |
                v
          Glue Data Catalog
                |
       +--------+--------+
       |        |        |
    Athena    EMR    Other Engines
```

---

# 111. Architecture Principles

## Principle 1 — Separate compute from data

```text
Glue
=
compute

S3/Iceberg
=
data
```

## Principle 2 — Make state explicit

```text
bookmark
or
watermark
```

## Principle 3 — Make output idempotent

Retries are expected.

## Principle 4 — Validate before publish

```text
bad data
≠
curated data
```

## Principle 5 — Observe before tuning

Use evidence.

## Principle 6 — Secure by default

No public database.

No hardcoded secret.

No wildcard role by default.

## Principle 7 — Treat dependencies as artifacts

Pin and test.

---

# 112. Advanced Production Scenario — Backfill

Suppose:

```text
2026-09-01 → 2026-09-30
```

must be recomputed.

Do not simply disable all incremental state and run the production job blindly.

Design:

```text
Backfill mode
 ↓
Explicit date range
 ↓
Isolated run
 ↓
Quality validation
 ↓
Idempotent publish
 ↓
Reconciliation
```

Parameter:

```text
--RUN_MODE=BACKFILL
--START_DATE=2026-09-01
--END_DATE=2026-09-30
```

Backfills should be first-class engineering workflows.

---

# 113. Advanced Production Scenario — Late Data

Suppose:

```text
event_time = 09:58
arrival_time = 10:07
```

If the job at 10:00 already advanced its watermark, the record may be missed.

Possible strategy:

```text
watermark
+
lookback window
+
deduplication
```

Example:

```text
watermark = 10:00
lookback = 10 minutes

read > 09:50
```

Then deduplicate by business/event key.

---

# 114. Advanced Production Scenario — Source Schema Change

Producer changes:

```text
amount DECIMAL
```

to:

```text
amount STRING
```

Response:

```text
Detect
 ↓
Classify as breaking
 ↓
Stop production publish
 ↓
Alert owner
 ↓
Assess consumer impact
 ↓
Correct producer or transform
 ↓
Replay affected input
```

Do not silently cast all values without checking semantics.

---

# 115. Advanced Production Scenario — Quality Degradation

Historical:

```text
DQ score ≈ 99.8%
```

Today:

```text
DQ score = 94%
```

Do not immediately disable the rules.

Investigate:

```text
Which rules failed?
Which partitions?
Which producer?
What changed?
Is the shift statistically unusual?
```

Then decide:

```text
incident
expected business change
bad rule
```

---

# 116. Data Quality Strategy

A mature quality strategy has layers.

```text
Layer 1 — Schema
Layer 2 — Structural validation
Layer 3 — Field validation
Layer 4 — Referential checks
Layer 5 — Business rules
Layer 6 — Historical anomaly detection
Layer 7 — Consumer monitoring
```

No single layer is enough.

---

# 117. Quality Rule Severity

Example:

| Rule | Severity | Action |
|---|---|---|
| order_id complete | Critical | Stop |
| order_id unique | Critical | Stop |
| amount >= 0 | Critical | Quarantine |
| status valid | Critical | Quarantine |
| currency present | Warning | Alert |
| optional marketing field | Info | Observe |

This turns Data Quality into an operational control system.

---

# 118. DQDL Rule Design Principles

Rules should be:

```text
Specific
Testable
Business-relevant
Version-controlled
Owned
Observable
```

Avoid:

```text
Rules nobody understands
Rules with arbitrary thresholds
Rules that always fail
Rules that nobody acts upon
```

A rule without an operational response is often just noise.

---

# 119. Data Quality Recommendation Workflow

```text
Sample data
 ↓
Recommendation
 ↓
Review
 ↓
Remove irrelevant rules
 ↓
Add business rules
 ↓
Set severity
 ↓
Test
 ↓
Version
 ↓
Deploy
```

For ADVANCED recommendations, understand that sampled table data and metadata can be sent to Amazon Bedrock as part of recommendation processing; this creates an additional data-protection consideration for sensitive datasets. AWS documents the current behavior and protections. citeturn0search6

---

# 120. Anomaly Detection Workflow

```text
Collect statistics
       ↓
Historical baseline
       ↓
New observation
       ↓
Detect anomaly
       ↓
Observation
       ↓
Human/business interpretation
       ↓
Accept / reject / adjust
```

The model should not be treated as an autonomous business decision-maker.

---

# 121. Production DQ Operating Model

Define:

```text
Rule owner
Data owner
Pipeline owner
On-call owner
Threshold owner
```

Track:

```text
rule failure frequency
false positives
false negatives
time to recovery
quarantine volume
data freshness
```

This transforms Data Quality from a feature into a discipline.

---

# 122. Performance Checklist

Before adding workers:

```text
[ ] Read only needed columns
[ ] Read only needed partitions
[ ] Avoid unnecessary full scans
[ ] Check file sizes
[ ] Check input partitions
[ ] Check shuffle
[ ] Check skew
[ ] Check joins
[ ] Check broadcast
[ ] Check output partitioning
[ ] Check Spark UI
```

Then consider:

```text
worker type
worker count
auto scaling
execution class
```

---

# 123. Cost Checklist

```text
[ ] Incremental instead of full load
[ ] Right-size workers
[ ] Use Auto Scaling where appropriate
[ ] Use FLEX for eligible non-urgent jobs
[ ] Reduce retries
[ ] Reduce runtime
[ ] Avoid tiny files
[ ] Test locally
[ ] Use small AWS test data
[ ] Clean up resources
[ ] Monitor spend
[ ] Verify current pricing
```

---

# 124. Security Checklist

```text
[ ] Least-privilege IAM
[ ] No hardcoded secrets
[ ] Secrets Manager
[ ] Encryption
[ ] KMS where required
[ ] Private JDBC networking
[ ] Restricted S3 paths
[ ] Restricted Glue permissions
[ ] Restricted secret access
[ ] Logs do not contain secrets
[ ] Auditability
```

---

# 125. Production Readiness Checklist

A job is not production-ready because it runs once.

It should have:

```text
Code
Tests
Schema
Incremental strategy
Idempotency
DQ
Quarantine
Retries
Observability
Security
Dependencies
Cost model
Runbook
Deployment process
Rollback strategy
Backfill strategy
```

---

# 126. Interview Preparation

## Basic

1. What is AWS Glue?
2. What is a Glue Spark job?
3. What is a Python shell job?
4. What is a streaming Glue job?
5. What is a DynamicFrame?
6. What is a DataFrame?
7. Why would you convert a DynamicFrame to a DataFrame?
8. What is a job bookmark?
9. What is a DQDL ruleset?
10. What is quarantine?

## Intermediate

1. How do Glue bookmarks work?
2. When would you use a custom watermark?
3. Why is idempotency important?
4. How do you handle schema drift?
5. How do you size Glue workers?
6. What is Auto Scaling?
7. What is FLEX?
8. How do you connect Glue to a private JDBC database?
9. How do you package Python dependencies?
10. How do you implement a quality gate?

## Advanced

1. Design an incremental Glue pipeline with late-arriving data.
2. Explain bookmark limitations.
3. Compare bookmark and watermark architectures.
4. Design an idempotent Iceberg pipeline.
5. Diagnose a Glue Spark job that is five times slower.
6. Design a quality system with critical and warning rules.
7. Design quarantine and replay.
8. Design Glue networking for a private database.
9. Design dependency management for multiple Glue runtimes.
10. Design a production cost-optimization strategy.

---

# 127. Practice Questions — Basic

1. What is Glue ETL?
2. Why is Glue called managed ETL?
3. What does a Spark job do?
4. What does a Python shell job do?
5. What is a streaming job?
6. What is a Glue runtime?
7. What is a Glue execution role?
8. What is a job parameter?
9. What is a DynamicFrame?
10. What is a DataFrame?
11. Why are DataFrames commonly used for transformations?
12. What is a DPU?
13. What is Auto Scaling?
14. What is FLEX?
15. What is a bookmark?
16. What is a watermark?
17. What is idempotency?
18. What is Parquet?
19. What is Iceberg?
20. What is Data Quality?

---

# 128. Practice Questions — Incremental Processing

1. Why avoid full loads?
2. How does a bookmark help?
3. What does `job.commit()` do conceptually?
4. Why can bookmark state be insufficient?
5. What is a watermark?
6. How do late-arriving records affect watermarks?
7. What is a lookback window?
8. Why is deduplication needed with lookback windows?
9. What happens if state advances before output succeeds?
10. How do you make a replay safe?
11. How do you backfill a date range?
12. How do you handle duplicate source records?
13. How do you handle corrections to old data?
14. How do you compare bookmark and watermark approaches?
15. How do you design state for CDC?

---

# 129. Practice Questions — Data Quality

1. What is DQDL?
2. What is a ruleset?
3. What is a quality score?
4. What is a quality gate?
5. What is quarantine?
6. What is a critical rule?
7. What is a warning rule?
8. What is anomaly detection?
9. Why are historical baselines useful?
10. Why can an anomaly be legitimate?
11. What is rule recommendation?
12. Why review generated rules?
13. How do you test DQ rules?
14. How do you handle systemic schema failure?
15. How do you design DQ for a financial dataset?

---

# 130. Practice Questions — Troubleshooting

1. Job OOM.
2. Job suddenly 5× slower.
3. Duplicate output after retry.
4. Bookmark does not behave as expected.
5. New data is skipped.
6. JDBC connection timeout.
7. DQ rule fails unexpectedly.
8. Quarantine volume spikes.
9. Dependency installation fails.
10. Iceberg write fails.
11. S3 access denied.
12. KMS access denied.
13. Job cannot retrieve secret.
14. Worker count grows unexpectedly.
15. Runtime upgrade breaks the job.

For each answer:

```text
Symptom
Evidence
Hypotheses
Tests
Root Cause
Fix
Verification
Prevention
```

---

# 131. Practice Questions — Architecture

1. Design a Glue ETL platform for 10 TB/day.
2. Design incremental processing for an orders database.
3. Design a private JDBC ingestion pipeline.
4. Design DQ with quarantine and replay.
5. Design a multi-environment Glue deployment.
6. Design a Glue + Iceberg lakehouse.
7. Design a cost-controlled backfill system.
8. Design schema evolution handling.
9. Design a production observability strategy.
10. Design a complete orders pipeline.

---

# 132. Practice Questions — Production Decisions

1. DynamicFrame or DataFrame?
2. Bookmark or watermark?
3. Parquet or Iceberg?
4. STANDARD or FLEX?
5. Fixed workers or Auto Scaling?
6. Crawler or explicit schema?
7. Row quarantine or dataset failure?
8. Static threshold or anomaly detection?
9. Runtime package installation or frozen artifacts?
10. Glue workflow or external orchestrator?

Every answer should state:

```text
Decision
Reason
Trade-offs
Failure mode
Cost
Security
Operational impact
```

---

# 133. Cheat Sheet — Glue Jobs

```text
Spark
=
Distributed ETL

Python Shell
=
Small single-node tasks

Streaming
=
Continuous processing

Interactive Session
=
Development / exploration

Glue Studio
=
Visual development
```

---

# 134. Cheat Sheet — State

```text
Bookmark
=
Glue-managed incremental state

Watermark
=
Application-defined progress boundary

Idempotency
=
Safe replay

Lookback
=
Re-read recent history

Deduplication
=
Remove replay/late-data duplicates
```

---

# 135. Cheat Sheet — Data Quality

```text
Rule
 ↓
Ruleset
 ↓
Evaluation
 ↓
Result
 ↓
Quality Gate
 ├── PASS
 ├── WARNING
 └── FAIL
        ↓
    Quarantine
```

---

# 136. Cheat Sheet — Performance

```text
Slow Job
 ↓
Input
 ↓
Partitions
 ↓
Shuffle
 ↓
Join
 ↓
Skew
 ↓
Memory
 ↓
Output
```

Do not begin with:

```text
Add workers
```

Begin with:

```text
Find the bottleneck
```

---

# 137. Cheat Sheet — Production

```text
Code
 ↓
Test
 ↓
Deploy
 ↓
Incremental
 ↓
Transform
 ↓
Validate
 ↓
Publish
 ↓
Observe
 ↓
Recover
```

---

# 138. Final Knowledge Check — 20 Concepts

1. Why does Glue exist?
2. What is the difference between Spark and Python shell jobs?
3. What is a DynamicFrame?
4. Why use a DataFrame?
5. What is a Choice type?
6. Why use job parameters?
7. What is a worker?
8. What is Auto Scaling?
9. What is FLEX?
10. What is a bookmark?
11. What is a watermark?
12. Why is idempotency required?
13. Why use Parquet?
14. Why use Iceberg?
15. What is DQDL?
16. What is a quality gate?
17. What is quarantine?
18. What is anomaly detection?
19. Why is observability important?
20. Why is cost optimization part of ETL engineering?

---

# 139. Final Knowledge Check — 10 PySpark/Glue Questions

1. Convert a DynamicFrame to a DataFrame and explain why.
2. Resolve a Choice type.
3. Read partitioned Parquet.
4. Write partitioned Parquet.
5. Broadcast a small dimension table.
6. Explain a skewed join.
7. Identify a Spark UI bottleneck.
8. Explain why `coalesce(1)` can be dangerous.
9. Explain why adding workers may not fix skew.
10. Design a Spark transformation for idempotent replay.

---

# 140. Final Knowledge Check — 10 Incremental Questions

1. Explain bookmark state.
2. Explain watermark state.
3. Explain late-arriving data.
4. Explain a lookback window.
5. Explain deduplication.
6. Explain retry behavior.
7. Explain state-commit ordering.
8. Explain backfill mode.
9. Explain correction handling.
10. Design a production incremental strategy.

---

# 141. Final Knowledge Check — 10 Data Quality Questions

1. Write a completeness rule.
2. Write a uniqueness rule.
3. Write a range rule.
4. Explain a critical rule.
5. Explain a warning rule.
6. Explain quarantine.
7. Explain rule recommendations.
8. Explain anomaly detection.
9. Explain historical baselines.
10. Design a DQ operating model.

---

# 142. Final Knowledge Check — 10 Troubleshooting Questions

1. Why did the job run out of memory?
2. Why did it become slower?
3. Why did it duplicate output?
4. Why did it skip data?
5. Why did the JDBC connection fail?
6. Why did a DQ rule fail?
7. Why did quarantine volume increase?
8. Why did dependencies fail?
9. Why did an Iceberg write fail?
10. Why did an IAM/KMS call fail?

---

# 143. Final Knowledge Check — 5 Architecture Questions

1. Design an incremental orders pipeline.
2. Design a quality-gated Iceberg pipeline.
3. Design private JDBC ingestion.
4. Design a production backfill mechanism.
5. Design Glue ETL across development, staging and production.

---

# 144. Final Knowledge Check — 5 Production Decision Questions

1. When should you choose DynamicFrame over DataFrame?
2. When should you choose bookmark over custom state?
3. When should a DQ failure stop the pipeline?
4. When should an anomaly be treated as informational?
5. When should FLEX be used?

---

# 145. Module Completion Checklist

## Glue ETL

- [ ] I understand Glue ETL.
- [ ] I understand Spark jobs.
- [ ] I understand Python shell jobs.
- [ ] I understand streaming jobs.
- [ ] I understand Glue runtimes.
- [ ] I understand job parameters.
- [ ] I understand IAM roles.
- [ ] I can create and operate Glue jobs.
- [ ] I can use AWS CLI.
- [ ] I can use boto3.

## Data Processing

- [ ] I understand DynamicFrames.
- [ ] I understand DataFrames.
- [ ] I can convert between them.
- [ ] I understand Choice types.
- [ ] I can perform Spark transformations.
- [ ] I understand worker sizing.
- [ ] I understand DPUs.
- [ ] I understand Auto Scaling.
- [ ] I understand FLEX.
- [ ] I can inspect Spark execution.

## Incremental Processing

- [ ] I understand bookmarks.
- [ ] I understand custom state.
- [ ] I understand watermarks.
- [ ] I understand late-arriving data.
- [ ] I understand lookback windows.
- [ ] I understand deduplication.
- [ ] I understand idempotency.
- [ ] I can design safe retries.
- [ ] I can design backfills.

## Storage

- [ ] I can write partitioned Parquet.
- [ ] I understand small files.
- [ ] I understand Iceberg integration.
- [ ] I understand table-aware writes.
- [ ] I understand Delta/Hudi at awareness level.

## Networking

- [ ] I understand Glue JDBC connections.
- [ ] I understand VPC/subnet/security-group relationships.
- [ ] I understand Secrets Manager integration.
- [ ] I can troubleshoot JDBC connectivity.

## Dependencies

- [ ] I understand additional Python modules.
- [ ] I understand pinning.
- [ ] I understand frozen artifacts.
- [ ] I understand runtime compatibility.
- [ ] I can test dependency changes.

## Data Quality

- [ ] I understand Glue Data Quality.
- [ ] I understand DQDL.
- [ ] I can design rules.
- [ ] I can design rulesets.
- [ ] I understand quality scores.
- [ ] I understand quality gates.
- [ ] I understand quarantine.
- [ ] I understand rule recommendations.
- [ ] I understand anomaly detection.
- [ ] I understand historical baselines.

## Production

- [ ] I can troubleshoot Glue jobs.
- [ ] I understand retries.
- [ ] I understand idempotency.
- [ ] I understand observability.
- [ ] I understand security.
- [ ] I understand cost optimization.
- [ ] I can test ETL transformations.
- [ ] I can design a production Glue pipeline.
- [ ] I can write an operational runbook.

---

# 146. Roadmap Coverage Audit

The authoritative Topic 04 requirements are explicitly checked below.

| Requirement | Covered | Evidence in this module |
|---|---|---|
| Glue ETL overview | Yes | Sections 1–3 |
| Spark jobs | Yes | Sections 5, 44–48 |
| Python Shell jobs | Yes | Section 6 |
| Streaming jobs | Yes | Section 7 |
| Glue versions | Yes | Section 8 |
| Job parameters | Yes | Section 9 |
| IAM roles | Yes | Section 10 |
| Scripts | Yes | Section 11 |
| AWS CLI | Yes | Sections 12, 133 |
| boto3 | Yes | Section 13 |
| DynamicFrames | Yes | Sections 14–18 |
| DataFrames | Yes | Sections 15–18 |
| Worker types | Yes | Sections 44–50 |
| DPUs | Yes | Sections 44–51 |
| Auto Scaling | Yes | Section 49 |
| Flex | Yes | Section 50 |
| Job bookmarks | Yes | Sections 26–30 |
| Custom incremental state | Yes | Sections 28–30 |
| Watermarking | Yes | Sections 29–30, 113–114 |
| Incremental processing | Yes | Sections 25–30 |
| Idempotency | Yes | Sections 31, 77, 114 |
| S3 input/output | Yes | Sections 19–20 |
| Partitioned Parquet | Yes | Sections 20–21 |
| Iceberg | Yes | Sections 22–23, 86 |
| Delta/Hudi awareness | Yes | Section 23 |
| Glue Data Catalog integration | Yes | Section 24 |
| VPC JDBC connections | Yes | Sections 34–38, 91 |
| Glue local container | Yes | Section 38 |
| Interactive sessions/notebooks | Yes | Section 39 |
| External libraries | Yes | Sections 40–41 |
| Dependencies | Yes | Sections 40–41 |
| Glue Studio/workflows awareness | Yes | Sections 42–43 |
| Spark tuning | Yes | Sections 44–48, 94 |
| Cost model | Yes | Sections 51–52, 123 |
| Glue Data Quality | Yes | Sections 53–67 |
| DQDL | Yes | Sections 55–57, 118 |
| Rules | Yes | Sections 56–57 |
| Rulesets | Yes | Section 57 |
| Data quality evaluation | Yes | Sections 58, 66 |
| Data quality outcomes | Yes | Sections 58–60 |
| Quality gates | Yes | Sections 59, 67, 117 |
| Quarantine | Yes | Sections 60–61 |
| Bad-record handling | Yes | Section 61 |
| Data quality alerts | Yes | Sections 59, 72–74, 117 |
| Recommendations | Yes | Sections 62, 119 |
| Anomaly detection | Yes | Sections 63–65, 120 |
| Historical baselines | Yes | Sections 64, 120 |
| Production DQ strategy | Yes | Sections 116–121 |
| Testing | Yes | Sections 68–70 |
| Observability | Yes | Sections 72–75 |
| Logging | Yes | Section 74 |
| Metrics | Yes | Sections 72–73 |
| Security | Yes | Sections 102–104, 124 |
| Secrets | Yes | Sections 36, 104 |
| Networking | Yes | Sections 35, 103 |
| Performance | Yes | Sections 44–50, 122 |
| Cost | Yes | Sections 51–52, 123 |
| Failure handling | Yes | Sections 75, 95–100 |
| Deployment | Yes | Section 105 |
| Operational runbooks | Yes | Section 106 |

**Roadmap coverage: COMPLETE**

---

# 147. Technical Accuracy Audit

The module follows these accuracy rules:

- No invented AWS prices.
- No invented service quotas.
- Runtime-sensitive details are explicitly marked for current documentation verification.
- CLI/API examples use documented Glue operations.
- DynamicFrame/DataFrame behavior is aligned with current AWS Glue documentation.
- Bookmark guidance reflects the documented `job.init()` / `job.commit()` lifecycle.
- Auto Scaling and FLEX are described with current documented applicability.
- Python dependency guidance reflects current AWS Glue packaging guidance.
- Data Quality capabilities are described using current AWS documentation.
- Anomaly detection is not presented as a deterministic business decision engine.
- ADVANCED DQ recommendations are treated as a data-protection consideration because current AWS documentation states that sampled table data and metadata are used with Amazon Bedrock for the recommendation process.
- Terraform examples are intentionally described as patterns where provider schemas can vary.
- No secrets or credential material is embedded.
- No unsupported exactly-once guarantee is claimed for bookmarks.

Current AWS documentation used to validate the module includes Glue Data Quality, DQDL/recommendations/anomaly detection, Glue job parameters, DynamicFrames, bookmarks, Auto Scaling, worker/execution classes, VPC connection properties, local development and Python dependency packaging. citeturn0search1turn0search0turn0search7turn0search8turn1search0turn1search11turn1search9turn1search4turn1search12turn0search5turn1search3

**Technical accuracy audit: PASSED**

---

# 148. Security Audit

The module explicitly avoids:

```text
Hardcoded AWS credentials
Hardcoded database passwords
Root-user execution
Wildcard IAM as a default
Public database exposure
Secrets in logs
Secrets in source control
```

It promotes:

```text
IAM roles
IAM Identity Center / assumed roles
Secrets Manager
KMS
Private networking
Least privilege
Restricted S3 access
Auditability
```

**Security audit: PASSED**

---

# 149. Cost Safety Audit

The module:

- avoids fabricated prices,
- recommends current AWS pricing verification,
- teaches right-sizing,
- covers Auto Scaling,
- covers FLEX,
- emphasizes incremental processing,
- encourages local testing,
- warns about retries,
- discusses small files and inefficient Spark,
- requires cleanup after labs.

**Cost-safety audit: PASSED**

---

# 150. File-Scope Audit

Target requested by the learner:

```text
04-glue-etl-jobs-and-glue-data-quality.md
```

This deliverable is self-contained and does not require creation of:

```text
Python files
Terraform files
Test files
Project files
README files
Other topic files
```

**Other files required by this module: NONE**

**File-scope audit: PASSED**

---

# 151. Final Operating Standard

The module is complete when you can independently execute this loop:

```text
Understand requirement
       ↓
Select Glue job type
       ↓
Define input/output contract
       ↓
Choose state strategy
       ↓
Build transformation
       ↓
Validate schema
       ↓
Apply data quality
       ↓
Quarantine bad data
       ↓
Publish idempotently
       ↓
Observe
       ↓
Measure cost
       ↓
Recover from failure
       ↓
Document
```

The target skill is not:

> "I know how to run an AWS Glue job."

The target skill is:

> **"I can design and operate an incremental, idempotent, observable, secure, cost-efficient, quality-controlled AWS data pipeline using Glue."**

---

# 152. Final Execution Summary

```text
Target file updated:
03-AWS-Data-Engineering-Deep-Dive/04-glue-etl-jobs-and-glue-data-quality.md

Other files modified:
NONE

Roadmap coverage:
COMPLETE

Topic 04 audit:
PASSED

Technical accuracy audit:
PASSED

Security audit:
PASSED

Cost-safety audit:
PASSED

File-scope audit:
PASSED
```
