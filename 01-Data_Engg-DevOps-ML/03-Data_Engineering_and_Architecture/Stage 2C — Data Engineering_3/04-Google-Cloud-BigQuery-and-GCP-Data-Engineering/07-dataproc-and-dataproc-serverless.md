# Dataproc and Dataproc Serverless

> **Stage 2C — Data Engineering_3 · 04-Google-Cloud-BigQuery-and-GCP-Data-Engineering · Topic 07**
>
> Target file: `07-dataproc-and-dataproc-serverless.md`  
> Hands-on workspace: `experiments/07_dataproc/`

## 1. Learning objectives and prerequisites

By the end of this lesson, you should be able to:

- Explain Spark's driver/executor model, partitions, shuffles, and why distributed processing can help—or make a workload slower and more expensive.
- Choose a managed Dataproc cluster or Dataproc Serverless for Spark, submit PySpark jobs, and retrieve logs.
- Read durable source data from Cloud Storage (`gs://`) and write curated data to BigQuery with the Spark BigQuery connector.
- Design an ephemeral create → submit → validate → delete lifecycle without treating cluster HDFS as durable storage.
- Package dependencies, select compatible Dataproc image/runtime and connector versions, and use workflow templates.
- Reason about autoscaling, Spot/preemptible secondary workers, disks, IAM, network boundaries, encryption, and retries.
- Decide when BigQuery SQL or Dataflow is a better fit than Spark, and plan migration of existing Hadoop/Spark jobs.
- Record actual startup/runtime/cost observations without presenting invented benchmarks as facts.

### Prerequisites

You should already be comfortable with:

- Python and PySpark basics: DataFrames, schemas, transformations, actions, joins, aggregations.
- SQL, BigQuery datasets/tables, partitioning, and basic query-cost control (Topics 02–05).
- Cloud Storage, IAM service accounts, `gcloud`, and basic networking concepts (Topic 01 and earlier data-engineering modules).
- Streaming concepts and Dataflow's Beam model (Topic 06), so you can distinguish batch/distributed ETL from event-time streaming.
- Airflow/Composer fundamentals at a conceptual level; Topic 08 will orchestrate these jobs.

### Lab safety

This lab provisions billable resources. Use a dedicated project, one region, a small cluster, a short-lived batch, a budget alert, and a clearly named lab bucket/dataset. Replace all placeholders. Do not paste credentials into code. Do not run cleanup commands until you have verified that resource names point only to lab resources.

---

## 2. Spark and Hadoop workload fundamentals

### 2.1 What Spark is good at

Apache Spark is a distributed processing engine. A Spark application can read data, build a logical plan, optimize the plan, and execute tasks across multiple executors. It is useful when a workload needs distributed transformations, joins, complex Python/Scala libraries, or compatibility with existing Spark/Hadoop code.

Common workloads:

- Large batch ETL across files in Cloud Storage.
- Complex joins or transformations that do not fit comfortably into a single SQL transformation.
- Existing PySpark jobs being moved from on-premises Hadoop/Spark to Google Cloud.
- Spark ML or other Spark ecosystem workloads where that ecosystem is a requirement.
- Data preparation that feeds BigQuery or another analytical platform.

**Spark is not automatically faster than SQL.** If data already resides in BigQuery and the work is relational aggregation, filtering, or joins expressible in Standard SQL, BigQuery often avoids moving data into a second compute system. Spark introduces startup, serialization, shuffle, network, and output-write costs.

### 2.2 Driver, executors, tasks, and partitions

- **Driver:** creates the Spark session, builds the execution plan, schedules tasks, tracks application state, and coordinates executors.
- **Executor:** worker-side process that runs tasks, caches data, and stores shuffle blocks.
- **Partition:** a logical chunk of a dataset. Spark normally schedules one task per partition per stage.
- **Stage:** a group of tasks separated by shuffle boundaries.
- **Shuffle:** redistribution of records between executors, commonly required by `groupBy`, large joins, `distinct`, and repartitioning.
- **Action:** an operation such as `count`, `collect`, or a write that causes Spark to execute a plan.

More workers do not guarantee linear speed-up. A single hot key, too few partitions, too many tiny files, insufficient executor memory, or a large shuffle can dominate the job.

```text
Cloud Storage objects
        |
        v
  Spark driver ---- plans stages / schedules tasks
        |
        +-----------------------------+
        |                             |
        v                             v
  Executor A                     Executor B
  partitions 0..n                partitions n+1..m
        |                             |
        +---------- shuffle ----------+
                      |
                      v
             output partitions
                      |
                      v
             BigQuery staging table
                      |
                      v
            idempotent MERGE to target
```

### 2.3 Hadoop ecosystem and HDFS

Dataproc can run Spark and Hadoop components, and some workloads also use Hive-compatible catalogs or Hadoop libraries. A Dataproc cluster's HDFS is local to that cluster's lifecycle and is not the correct place for durable pipeline output. If a cluster is deleted, its local disks and HDFS data can disappear.

Use Cloud Storage for durable object storage and checkpoints/artifacts where supported; use BigQuery for curated analytics tables; use a managed metastore when multiple jobs need a shared catalog. Treat HDFS as temporary distributed scratch unless you have explicitly designed and operated a different persistence strategy.

### 2.4 Cloud Storage integration

Use `gs://bucket/path/file` URIs. Dataproc's Cloud Storage connector allows Hadoop/Spark filesystem APIs to access objects through Google Cloud Storage. It is not the same as mounting a POSIX disk: object listing, rename, consistency patterns, permissions, and request costs differ from a local filesystem.

Prefer Parquet or Avro for typed analytical data when appropriate. Avoid generating thousands of tiny files; use a deliberate partitioning strategy and compact outputs if downstream consumers need fewer, larger files.

---

## 3. Dataproc architecture and cluster lifecycle

### 3.1 Managed cluster components

A standard Dataproc cluster is a managed set of Compute Engine VMs with configured data-processing software.

- **Primary/master node(s):** host cluster control services and, depending on configuration, may host the Spark driver and YARN ResourceManager.
- **Primary workers:** provide dependable worker capacity and run executors / YARN NodeManagers.
- **Secondary workers:** additional capacity commonly backed by preemptible/Spot VMs; these can disappear and must not be the only place where irreplaceable state exists.
- **Image version:** defines a tested bundle of OS, Java, Hadoop, Spark, and related components. Choose an image supported for your workload and check its component matrix before pinning it.
- **Autoscaling policy:** adjusts eligible worker groups according to YARN resource demand and configured bounds. It does not make a badly partitioned job efficient.

Terminology differs by product generation. “Master” remains in some Dataproc API and CLI fields; “primary node” is often used in product explanations.

### 3.2 Cluster lifecycle

For intermittent batch workloads, prefer an ephemeral cluster:

1. Create the cluster with explicit region, image version, machine types, disk settings, network, service account, and labels.
2. Upload/verify the script and input objects.
3. Submit the PySpark job.
4. Monitor job state and logs; fail the pipeline if the job fails.
5. Validate the output in BigQuery and record metrics.
6. Delete the cluster in a `finally`-style cleanup path or an operational runbook, after confirming that the output is durable.

Cluster startup is a real cost and latency component. For many short jobs, Dataproc Serverless can reduce cluster-management work; for repeated jobs, a long-running cluster may amortize startup overhead but incurs idle VM and disk costs. Compare total cost and operational burden, not only Spark execution time.

### 3.3 Choose an image version deliberately

Do not blindly copy a version number from an old tutorial. Before provisioning:

```bash
gcloud dataproc image-versions list --region="${REGION}"
gcloud dataproc clusters create --help
gcloud dataproc batches submit pyspark --help
```

Choose a currently supported image/runtime that matches the required Spark, Java, Python, connector, and dependency versions. The exact default image/runtime can change. Pin an explicit image version for reproducibility and record it in run metadata; periodically test upgrades in a non-production environment.

**Compatibility rule:** the Spark BigQuery connector is version-sensitive. Dataproc image 2.1+ and Dataproc Serverless commonly provide a built-in connector; when overriding it, use the documented Dataproc metadata or Serverless property rather than assuming a `--jars` flag overrides the built-in connector.

### 3.4 Create a small lab cluster

Set variables first. Use a region supported by all services and close to the dataset.

```bash
export PROJECT_ID="YOUR_PROJECT_ID"
export REGION="us-central1"                 # choose a supported region
export ZONE="us-central1-a"                  # optional; must match region
export CLUSTER="dp-lab-$(date +%Y%m%d%H%M%S)"
export BUCKET="YOUR_UNIQUE_GCS_BUCKET"
export DATASET="dataproc_lab"
export TARGET_TABLE="orders_curated"
export STAGING_PREFIX="dataproc_staging"
export RUNTIME_SA="YOUR_RUNTIME_SERVICE_ACCOUNT"

gcloud config set project "${PROJECT_ID}"
gcloud services enable \
  dataproc.googleapis.com \
  compute.googleapis.com \
  storage.googleapis.com \
  bigquery.googleapis.com \
  logging.googleapis.com
```

Create the bucket and dataset if they do not already exist. Bucket names are globally unique; dataset location should align with the region strategy. Avoid deleting shared or pre-existing resources.

```bash
gcloud storage buckets create "gs://${BUCKET}" \
  --location="${REGION}" \
  --uniform-bucket-level-access

bq --location="${REGION}" mk --dataset "${PROJECT_ID}:${DATASET}"
```

Create a small cluster with an explicit image version chosen from the current supported list. Replace `2.x` with the exact version you verified; do not run this literal placeholder.

```bash
# Example shape only: substitute a currently supported image version.
gcloud dataproc clusters create "${CLUSTER}" \
  --region="${REGION}" \
  --zone="${ZONE}" \
  --image-version="2.x-debian12" \
  --master-machine-type="e2-standard-2" \
  --worker-machine-type="e2-standard-2" \
  --num-workers=2 \
  --master-boot-disk-size=100GB \
  --worker-boot-disk-size=100GB \
  --bucket="${BUCKET}" \
  --service-account="${RUNTIME_SA}" \
  --enable-component-gateway \
  --labels=purpose=learning,owner=dataproc-lab
```

The image string is intentionally a placeholder because available image versions change. Use `gcloud dataproc image-versions list` and the official compatibility documentation to choose a valid current value. For a constrained lab, consider a smaller worker count only if the selected configuration supports it; some cluster configurations require minimum topology constraints.

### 3.5 Ephemeral HDFS and durable storage

Do not use a path such as `/user/hadoop/output` as the only final output location. That path is on cluster HDFS. Prefer:

- Source: `gs://BUCKET/raw/...`
- Temporary job artifacts: a dedicated staging prefix/bucket with lifecycle rules
- Curated analytical output: BigQuery
- Durable file output, if required: `gs://BUCKET/curated/...`

Never delete a bucket or dataset as a casual substitute for cleaning up the cluster. Resource cleanup should be scoped and explicit.

---

## 4. PySpark submission and Cloud Storage integration

### 4.1 Job submission syntax

The standard command is:

```bash
gcloud dataproc jobs submit pyspark \
  --cluster="${CLUSTER}" \
  --region="${REGION}" \
  gs://BUCKET/path/to/main.py \
  -- --input="gs://BUCKET/raw/orders.jsonl"
```

The `--` separates `gcloud` flags from arguments passed to the Python driver. `--py-files` distributes `.py`, `.zip`, or `.egg` files to driver/executors; `--jars` supplies JARs. `--properties` sets Spark properties. Use `--max-failures-total` / `--max-failures-per-hour` only after considering whether reruns can duplicate external side effects.

### 4.2 Read Cloud Storage

For Spark DataFrames:

```python
orders = (
    spark.read
    .schema(order_schema)
    .json("gs://YOUR_BUCKET/raw/orders.jsonl")
)
```

Do not assume a local file on the submitter is visible to every worker. Stage scripts and input data in Cloud Storage or distribute supporting files using documented job flags. The cluster's attached service account needs the appropriate Cloud Storage permissions.

### 4.3 Job monitoring

Useful commands:

```bash
gcloud dataproc jobs list --region="${REGION}" --cluster="${CLUSTER}"
gcloud dataproc jobs describe JOB_ID --region="${REGION}"
gcloud dataproc jobs wait JOB_ID --region="${REGION}"
gcloud dataproc jobs get-iam-policy JOB_ID --region="${REGION}"  # inspect only if needed
```

Check driver output and Cloud Logging. Correlate the Dataproc job ID with the BigQuery staging/target changes. Capture actual start/end times, input rows/bytes, output rows, shuffle spill, failed tasks, and cost data where available.

---

## 5. Dataproc Serverless for Spark and batch lifecycle

### 5.1 Mental model

Dataproc Serverless for Spark submits a **batch** rather than asking you to create and manage a cluster. Google provisions the runtime environment for the workload, scales compute according to service behavior and configuration, and tears down the workload resources after completion. You still own the code, dependency compatibility, IAM, network, input/output design, observability, and cost control.

Typical advantages:

- No long-lived cluster to maintain for each batch.
- Per-run runtime version, service account, network, dependency, and Spark property choices.
- Less cluster provisioning and teardown code in a small batch pipeline.

Trade-offs:

- Batch startup/provisioning latency still exists; serverless does not mean instantaneous.
- Supported Spark versions, configuration properties, libraries, network modes, and integrations are runtime-dependent.
- Some cluster-specific features and customizations do not map directly to Serverless.
- Repeated tiny jobs may still be dominated by startup and dependency-fetching overhead.

### 5.2 Submit the same PySpark script

```bash
export BATCH="orders-etl-$(date +%Y%m%d%H%M%S)"

gcloud dataproc batches submit pyspark \
  gs://"${BUCKET}"/code/main.py \
  --batch="${BATCH}" \
  --region="${REGION}" \
  --deps-bucket="gs://${BUCKET}" \
  --service-account="YOUR_RUNTIME_SERVICE_ACCOUNT" \
  --version="2.x" \
  -- \
  --input="gs://${BUCKET}/raw/orders.jsonl" \
  --staging-table="${PROJECT_ID}.${DATASET}.orders_stage"
```

Replace `2.x` with a supported Serverless runtime version from the current version documentation. `--deps-bucket` is for workload dependencies; `--staging-bucket` is the Cloud Storage bucket used for staging/configuration/output artifacts when specified. Use a dedicated bucket or prefix with retention/lifecycle controls.

To inspect the batch:

```bash
gcloud dataproc batches describe "${BATCH}" --region="${REGION}"
gcloud dataproc batches list --region="${REGION}"
```

Serverless dependency and runtime flags evolve with `gcloud` SDK releases. Confirm your installed command's help and the current documentation before using optional flags in production.

### 5.3 Resource and runtime configuration

The batch command accepts runtime-specific configuration through `--properties`. Do not copy arbitrary cluster properties into Serverless; consult the Serverless-supported property list. For example, when the built-in BigQuery connector must be overridden, documented properties include:

```bash
--properties="dataproc.sparkBqConnector.version=VERSION"
```

or a connector URI property where supported. Match the connector to the selected runtime's Spark version. Do not set a connector override unless you have verified the exact compatible artifact.

---

## 6. BigQuery connector for Spark

### 6.1 Why use the connector?

The Spark BigQuery connector reads BigQuery tables into Spark DataFrames and writes Spark DataFrames to BigQuery. It is a data source connector, not a reason to move every SQL transformation out of BigQuery.

Read:

```python
source_df = (
    spark.read
    .format("bigquery")
    .load("PROJECT_ID.DATASET.SOURCE_TABLE")
)
```

Write to a staging table:

```python
(
    output_df.write
    .format("bigquery")
    .option("temporaryGcsBucket", "YOUR_BUCKET")
    .mode("overwrite")
    .save("PROJECT_ID.DATASET.STAGING_TABLE")
)
```

The connector supports different write paths and may use Cloud Storage as temporary storage for indirect writes. The runtime service account must be able to access BigQuery and any temporary bucket required by the chosen write method. The connector's built-in version depends on Dataproc image or Serverless runtime. Verify connector compatibility, write method, location, and permissions before a production deployment.

### 6.2 A safe output pattern

A Spark write with `append` is not automatically idempotent. If a job retries after the write but before orchestration records success, rows may be duplicated.

For this lab, use this pattern:

1. Build a deterministic staging table name for the logical run (or a dedicated staging table with `overwrite` semantics).
2. Deduplicate input by a stable business key (`event_id` in the example).
3. Write the staging result.
4. Execute a BigQuery `MERGE` keyed by `event_id` into the curated target.
5. Validate row counts and duplicate keys.
6. Delete the lab staging table only after validation and only if it is not needed for diagnosis.

A `MERGE` can be made idempotent when its source and match key are deterministic. It does not magically solve concurrent writers or conflicting updates; define conflict resolution and partition boundaries for real pipelines.

---

## 7. Dependency, image, and environment management

### 7.1 Choose the simplest dependency mechanism that works

| Mechanism | Use it when | Main risks |
|---|---|---|
| Built-in runtime libraries | Dependencies are already included and compatible | Hidden version assumptions; runtime upgrades change them |
| `--py-files` | Small internal Python modules/packages (`.py`, `.zip`, `.egg`) | Native wheels and complex dependency trees may not distribute correctly |
| `--archives` | A supported archive should be unpacked into the working directory | Path/activation assumptions; native libraries must match OS/Python |
| pip/requirements | Python dependencies need repeatable installation using supported job/runtime mechanisms | Network access, resolver drift, native build dependencies, install time |
| Conda environment archive | A prebuilt environment is needed and the selected execution mode supports it | Archive size, ABI compatibility, environment activation and platform differences |
| Initialization action | Cluster-level setup must run when cluster VMs are created | Startup latency, mutable external downloads, privilege/supply-chain risk |
| Custom image/container | A controlled, reusable runtime is required and the target mode supports it | Image lifecycle, vulnerability patching, reproducibility, unsupported customization |

**Important:** initialization actions apply to Dataproc clusters; they are not a universal way to configure Dataproc Serverless. Serverless has its own dependency/runtime mechanisms and optional custom container image support where documented.

### 7.2 Reproducibility practices

- Pin package versions and record Python, Java, Spark, Dataproc image/runtime, connector, and package-lock information.
- Prefer immutable artifacts and checksums over downloading `latest` during cluster startup.
- Build dependencies in CI, test them against the target image/runtime, and promote the same artifact to production.
- Avoid installing large dependencies on every job if it makes startup expensive; use an approved prebuilt image/environment where supported.
- Avoid dependency collisions with Spark's bundled libraries.
- Test both driver and executor imports; an import working on the driver does not prove that executors have the package.

### 7.3 Custom images and initialization actions

Use initialization actions only for cluster deployments that support them. Keep scripts idempotent, version-controlled, auditable, and safe to retry. Pin downloaded artifacts and fail fast if a dependency cannot be installed. A custom image is useful for repeated stable cluster workloads, but it introduces image build, patching, scanning, and rollout responsibilities.

For Serverless, inspect the current `gcloud dataproc batches submit pyspark --help` and runtime docs for `--container-image`, `--archives`, `--py-files`, `--deps-bucket`, and supported properties. Do not assume every cluster option exists for batches.

---

## 8. Reliability, security, and networking

### 8.1 IAM: separate deployer from runtime identity

Use separate identities where practical:

- **Human/deployer identity:** can create/update/delete the lab resources and submit jobs.
- **Dataproc service agent:** Google-managed service identity needed by the service; do not remove its required roles.
- **Runtime service account:** used by the cluster or batch to access only the required input bucket, staging bucket, BigQuery dataset/tables, KMS key, and logging APIs.

Typical least-privilege permission categories (exact predefined/custom roles depend on how resources are provisioned):

- Dataproc API permissions to create clusters or submit batches.
- Compute permissions for cluster VM lifecycle, often via the documented service-agent setup.
- Cloud Storage object read on input prefixes and object create/list/delete only where required on staging paths.
- BigQuery job creation in the target project plus table read/write permissions on the relevant dataset.
- Cloud KMS encrypt/decrypt permissions for the runtime/service identities if CMEK is used.
- Logging write permissions needed to emit logs.

Do not grant Project Owner or Editor to the runtime account just to get the lab running. Use IAM Policy Troubleshooter or audit logs to identify missing permissions instead of broadening access blindly. Use attached service accounts and Application Default Credentials; do not distribute service-account key JSON files to workers.

### 8.2 Network boundaries

- Prefer private IP / controlled egress designs where required by the organization's policy.
- Confirm the chosen subnet has the required routes, firewall rules, DNS, and Private Google Access or other approved path to Google APIs.
- Restrict outbound access for package installation; mirror approved packages/artifacts when public internet egress is not allowed.
- VPC Service Controls (VPC-SC) can reduce data exfiltration risk for supported Google APIs, but it is not a replacement for IAM, firewall rules, or workload-level controls. Validate Dataproc, BigQuery, Cloud Storage, and KMS access patterns against the perimeter design.
- Use labels, audit logs, and resource-level IAM to support investigation and cost allocation.

### 8.3 Encryption and sensitive workloads

Google Cloud services encrypt data at rest by default; CMEK adds customer control over key policy and lifecycle for supported resources. For CMEK, confirm service support, key location, key IAM, and failure behavior if the key is disabled or inaccessible. Batch commands expose `--kms-key` for supported Serverless resources; cluster and workflow resources have their own encryption configuration paths.

Kerberos is relevant to some Hadoop-compatible secure cluster deployments, especially when integrating with existing Hadoop identity/security requirements. It is not a default prerequisite for a typical managed Dataproc learning lab.

**Dataproc on GKE** runs supported Dataproc workloads using Google Kubernetes Engine infrastructure and is relevant when Kubernetes integration or an existing GKE operating model is a requirement. It is not identical to a standard VM-based Dataproc cluster or Dataproc Serverless: verify current product availability, supported Spark/runtime versions, networking, identity, and operational requirements before selecting it.

**Dataproc Metastore** is a managed Hive metastore service for compatible Spark/Hive workloads that need a shared catalog. **BigLake Metastore** is a catalog service oriented to lakehouse/open table formats and interoperable analytics engines; it is not simply a drop-in synonym for every Hive metastore deployment. Choose based on table formats, engines, interoperability, region, and service support. Treat Kerberos, VPC-SC, CMEK, Dataproc on GKE, and shared metastore configuration as architecture-awareness topics until a specific workload requires them.

### 8.4 Reliability and partial failure

Spark retries failed tasks/stages according to Spark settings and runtime behavior, but external side effects can still be duplicated if the application writes to an external system before the job fails. Therefore:

- Prefer transformations with deterministic outputs.
- Use stable business keys and idempotent `MERGE`/overwrite staging patterns.
- Write to a run-scoped staging table, validate, then promote.
- Make cleanup separate from correctness; never delete the only valid output during a retry.
- Set batch timeouts where supported, and use bounded retry policies.
- Capture the job ID, input manifest, code version, runtime version, run date, and output counts.
- For concurrent runs, isolate staging resources and define how overlapping date partitions are handled.
- Test malformed input, empty input, permission failures, unavailable Spot capacity, and failed BigQuery writes.

---

## 9. Cost optimization and operational trade-offs

### 9.1 Cost model

Actual costs depend on region, VM family, disk size/type, cluster uptime, Dataproc pricing, Serverless usage, Cloud Storage requests/storage, BigQuery processing/storage, network egress, and any auxiliary resources. This lesson does not supply benchmark numbers or a price estimate; calculate them for your project and region using current pricing.

Record at least:

- Resource provisioning/startup time.
- Spark application runtime.
- End-to-end wall-clock time.
- Input bytes and rows; output rows/bytes.
- VM/core/memory/disk configuration or Serverless runtime configuration.
- Shuffle read/write, spill, executor failures, and retries.
- BigQuery bytes processed by validation/merge queries.
- Actual billing data after it becomes available; label resources consistently.

### 9.2 Ephemeral versus long-running clusters

| Pattern | Advantages | Costs/risks | Good fit |
|---|---|---|---|
| Ephemeral cluster per workload/window | Strong isolation; no idle compute after deletion; repeatable config | Startup overhead; cluster creation quota/API limits; repeated dependency setup | Scheduled batch jobs with gaps |
| Long-running cluster | Amortizes startup; shared environment can serve frequent jobs | Idle VM/disk cost; drift; noisy-neighbor and dependency conflicts; patching burden | Frequent workloads with stable demand |
| Dataproc Serverless batch | No cluster lifecycle management; per-batch runtime configuration | Startup still exists; runtime feature limits; dependency/setup overhead | Intermittent Spark batch jobs with supported requirements |

### 9.3 Right-sizing and disks

- Start with a small representative sample and measure CPU, memory, shuffle, disk spill, and throughput.
- Use enough partitions to keep executors busy without creating excessive scheduling overhead.
- Avoid oversizing the driver: `collect()` or large local objects can exhaust driver memory regardless of worker count.
- Increase executor memory or disk only when metrics identify the bottleneck; larger machines can cost more without improving skew or serial stages.
- Choose boot disk size/type based on dependency/runtime needs and shuffle spill. Local SSD can improve scratch performance for suitable I/O-heavy workloads, but costs, durability, and supported configuration must be checked.
- Prefer columnar formats, filter early, project only required columns, and avoid unnecessary shuffles.
- Compact small files and tune output partition count before adding more workers.

### 9.4 Spot / preemptible secondary workers

Secondary workers can add cheaper, interruptible capacity for workloads that tolerate loss of some workers. Their availability is not guaranteed and they can be reclaimed. Keep primary capacity sufficient for critical work, and test recovery under worker loss.

Use Spot/preemptible capacity for elastic, retryable batch workloads—not for unique state or as a guarantee of capacity. Dataproc uses different API/CLI terminology across versions and worker configuration options; check current docs for the selected cluster image and command. Do not assume that adding secondary workers automatically makes every Spark shuffle resilient. Dataproc Enhanced Flexibility Mode (EFM) can change shuffle behavior for supported Spark/image combinations; it has version and workload limitations and should be tested rather than enabled by habit.

### 9.5 Autoscaling and workflow templates

- **Autoscaling policy** controls cluster worker scaling based on resource demand and configured bounds; it is associated with cluster configurations and is not the same as Serverless autoscaling.
- **Workflow template** defines a repeatable dependency graph of Dataproc jobs and can create a managed cluster for the workflow. It is useful for cluster-based multi-step Spark/Hadoop jobs.
- **Dataproc Serverless batch** is a separate execution model and does not need a cluster workflow template to run one batch. Use Composer/Workflows (Topic 08) for cross-service orchestration and dependencies beyond a Dataproc workflow.

---

## 10. Dataproc versus Dataflow versus BigQuery SQL

Use the simplest engine that satisfies correctness, latency, scale, operational, and governance requirements.

| Requirement | Strong starting choice | Why / caveats |
|---|---|---|
| Filter, join, aggregate, deduplicate, and transform data already in BigQuery | **BigQuery SQL** | Avoids moving data to another engine; inspect bytes processed, slots, and query plan |
| Streaming events with event time, windows, watermarks, timers, state, and late-data policy | **Dataflow / Apache Beam** | Beam model is designed for bounded/unbounded pipelines; streaming guarantees depend on source, runner, and sink |
| Existing PySpark/Hadoop code, Spark-specific libraries, complex distributed Python transformations | **Dataproc or Dataproc Serverless** | Preserves Spark ecosystem and migration path; manage shuffle, dependencies, output idempotency |
| Batch processing of GCS files where a Spark ecosystem is not required | **BigQuery load + SQL** or **Dataflow batch** | Compare operational burden and data movement before choosing Spark |
| Shared transformation logic across multiple big-data platforms | **Spark/Dataproc may fit** | Portability can be useful but does not eliminate runtime-specific behavior |
| Low-latency, event-driven transformations with stateful event-time semantics | **Dataflow** | Do not force a batch Spark job into a streaming role without a clear latency/semantics reason |
| SQL-centric warehouse transformations and dimensional models | **BigQuery SQL / Dataform** | Better fit for warehouse-centric transformations and dependency-aware SQL pipelines |

### Decision checklist

1. Is the data already in BigQuery and the work relational? Try SQL first.
2. Is the workload a true event-time streaming pipeline? Evaluate Dataflow.
3. Does it require Spark/Hadoop libraries or compatibility with an existing PySpark job? Evaluate Dataproc.
4. Does the job run infrequently? Compare Serverless or ephemeral clusters.
5. Does it run continuously? Model the cost and operational overhead of a long-lived cluster.
6. Can the output be written idempotently and validated? If not, fix that before scaling.
7. Are there organization-specific network, encryption, metastore, or runtime constraints? Validate those before selecting the service.

---

## 11. Migration considerations

Treat migration as an application and data-contract migration, not just a change to the cluster manager.

### 11.1 Inventory

For each existing Hadoop/Spark job, record:

- Spark/Hadoop version, Java/Python version, package/JAR dependencies, and native libraries.
- HDFS paths, Hive tables/metastore dependencies, YARN assumptions, custom scripts, credentials, and scheduler integration.
- Input/output formats, partitioning, file counts, schema evolution, business keys, and data-quality checks.
- SLA, data volume, shuffle footprint, driver/executor sizing, failure/retry behavior, and downstream consumers.
- Required security model: Kerberos, service accounts, network boundaries, encryption, and audit needs.

### 11.2 Refactor for cloud

- Replace hard-coded HDFS paths with configuration-driven `gs://` or appropriate cloud storage locations.
- Move durable state out of cluster HDFS.
- Replace long-lived credentials with service-account identity and least privilege.
- Revisit Hive Metastore requirements and choose a supported shared catalog, such as Dataproc Metastore or BigLake Metastore, only where needed.
- Remove obsolete Hadoop tools or isolate them behind migration adapters if no longer required.
- Convert implicit assumptions about local files, rename atomicity, and shared disks into explicit object-storage-safe logic.
- Make outputs idempotent, add data-quality checks, and define a replay/backfill strategy.

### 11.3 Validate before cutover

Run representative historical inputs through old and new paths. Compare:

- Row counts and distinct business keys.
- Schema and nullability.
- Aggregates, checksums, and business-level invariants.
- Duplicate and late-record behavior.
- Runtime, shuffle, failures, and actual costs.
- Security/audit behavior and recovery from partial failure.

Use shadow runs or controlled backfills where practical. Cut over only when correctness, operational readiness, rollback, and cost are accepted by the owning team.

---

## 12. Hands-on exercises and troubleshooting

### 12.1 Lab workspace

Create this directory:

```text
experiments/07_dataproc/
├── README.md
├── main.py
├── sample_orders.jsonl
├── requirements.txt
├── run_cluster.sh
├── run_serverless.sh
├── validate.sql
├── workflow-template.yaml
└── observations.md
```

The files below are complete lab examples. Replace project, bucket, region, dataset, service account, and runtime/image placeholders. The script deliberately writes to a run-scoped staging table. A separate `MERGE` promotes staging rows into the curated table.

### 12.2 Sample input: `sample_orders.jsonl`

```json
{"event_id":"evt-001","customer_id":"cust-01","event_ts":"2026-01-01T10:15:00Z","amount_usd":12.5}
{"event_id":"evt-002","customer_id":"cust-02","event_ts":"2026-01-01T10:17:00Z","amount_usd":44.0}
{"event_id":"evt-003","customer_id":"cust-01","event_ts":"2026-01-02T08:01:00Z","amount_usd":9.99}
{"event_id":"evt-002","customer_id":"cust-02","event_ts":"2026-01-01T10:17:00Z","amount_usd":44.0}
{"event_id":"evt-004","customer_id":"cust-03","event_ts":"2026-01-02T09:30:00Z","amount_usd":105.0}
```

Expected behavior: `evt-002` is a deliberate duplicate. The job deduplicates on `event_id`, producing four unique events. In a real system, define which version wins when duplicate keys contain conflicting payloads; `dropDuplicates` is appropriate only when duplicate rows are equivalent for the business contract.

### 12.3 PySpark ETL: `main.py`

```python
"""GCS JSONL -> validated/deduplicated PySpark DataFrame -> BigQuery staging.

The curated target is updated by a separate idempotent BigQuery MERGE.
Run this same script on a Dataproc cluster or Dataproc Serverless for Spark.
"""
from __future__ import annotations

import argparse
from pyspark.sql import SparkSession, functions as F, types as T


ORDER_SCHEMA = T.StructType(
    [
        T.StructField("event_id", T.StringType(), True),
        T.StructField("customer_id", T.StringType(), True),
        T.StructField("event_ts", T.StringType(), True),
        T.StructField("amount_usd", T.DoubleType(), True),
    ]
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="gs://... JSONL input path")
    parser.add_argument(
        "--staging-table",
        required=True,
        help="project.dataset.table staging table in BigQuery",
    )
    parser.add_argument(
        "--temp-gcs-bucket",
        required=True,
        help="bucket name (without gs://) for connector temporary files",
    )
    parser.add_argument("--tax-rate", type=float, default=0.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.input.startswith("gs://"):
        raise ValueError("--input must be a Cloud Storage gs:// URI")
    if not (0 <= args.tax_rate <= 1):
        raise ValueError("--tax-rate must be between 0 and 1")

    spark = (
        SparkSession.builder
        .appName("dataproc-orders-etl")
        .getOrCreate()
    )

    try:
        raw = (
            spark.read
            .schema(ORDER_SCHEMA)
            .option("mode", "PERMISSIVE")
            .json(args.input)
        )

        # Explicit validation. Invalid rows are excluded from curated output;
        # production pipelines should persist rejects to a quarantine location.
        parsed = (
            raw
            .withColumn("event_ts_parsed", F.to_timestamp("event_ts"))
            .filter(F.col("event_id").isNotNull() & (F.length(F.trim("event_id")) > 0))
            .filter(F.col("customer_id").isNotNull())
            .filter(F.col("event_ts_parsed").isNotNull())
            .filter(F.col("amount_usd").isNotNull() & (F.col("amount_usd") >= 0))
        )

        # The sample's duplicate event is identical. For conflicting versions,
        # use a deterministic ordering (e.g., source_updated_at + source sequence).
        deduplicated = parsed.dropDuplicates(["event_id"])

        output = (
            deduplicated
            .withColumn("event_ts", F.col("event_ts_parsed"))
            .drop("event_ts_parsed")
            .withColumn("event_date", F.to_date("event_ts"))
            .withColumn(
                "amount_with_tax",
                F.round(F.col("amount_usd") * (F.lit(1.0) + F.lit(args.tax_rate)), 2),
            )
            .withColumn("processed_at", F.current_timestamp())
            .select(
                "event_id",
                "customer_id",
                "event_ts",
                "event_date",
                "amount_usd",
                "amount_with_tax",
                "processed_at",
            )
        )

        # This is a deterministic staging-table write. Use a run-scoped table
        # in concurrent/production workloads; overwrite is not a safe shared
        # staging strategy when two runs can write to the same table at once.
        (
            output.write
            .format("bigquery")
            .option("temporaryGcsBucket", args.temp_gcs_bucket)
            .mode("overwrite")
            .save(args.staging_table)
        )

        print(f"staging_table={args.staging_table}")
        print(f"input_rows={raw.count()}")
        print(f"valid_deduplicated_rows={output.count()}")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
```

**Production caveats:** this sample excludes invalid rows but does not persist them to a quarantine table; add a reject branch before production. `dropDuplicates` does not define which conflicting row wins. `current_timestamp()` changes on rerun, so the final `MERGE` below deliberately does not update rows when the business fields are unchanged. For a production table, use deterministic source metadata and an explicit update policy. For a very large dataset, avoid repeated full actions such as `count()` unless you intend to pay for them; this teaching script includes counts to make the lab observable.

### 12.4 Dependencies: `requirements.txt`

```text
# The Spark runtime provides PySpark. Do not pip-install a conflicting pyspark
# version into a managed Dataproc runtime without a tested compatibility plan.
# Add only Python libraries that are not included in the selected runtime.
# Example for an application dependency:
# python-dateutil==2.9.0.post0
```

The sample intentionally has no third-party Python dependency. The BigQuery connector is a JVM connector, not a pip package; use the connector bundled with the selected image/runtime unless a documented compatibility reason requires overriding it.

### 12.5 Stage sample data and script

```bash
export PROJECT_ID="YOUR_PROJECT_ID"
export REGION="us-central1"
export BUCKET="YOUR_UNIQUE_GCS_BUCKET"
export DATASET="dataproc_lab"
export TARGET_TABLE="orders_curated"
export RUNTIME_SA="YOUR_RUNTIME_SERVICE_ACCOUNT"
export INPUT_URI="gs://${BUCKET}/raw/sample_orders.jsonl"
export SCRIPT_URI="gs://${BUCKET}/code/main.py"
export STAGING_TABLE="${PROJECT_ID}.${DATASET}.orders_stage"
export TAX_RATE="0.00"

gcloud storage cp sample_orders.jsonl "${INPUT_URI}"
gcloud storage cp main.py "${SCRIPT_URI}"
```

Create the curated target table once. Set dataset location to match the chosen design:

```sql
CREATE TABLE IF NOT EXISTS `YOUR_PROJECT_ID.dataproc_lab.orders_curated` (
  event_id STRING NOT NULL,
  customer_id STRING,
  event_ts TIMESTAMP,
  event_date DATE,
  amount_usd FLOAT64,
  amount_with_tax FLOAT64,
  processed_at TIMESTAMP
)
PARTITION BY event_date
CLUSTER BY customer_id;
```

### 12.6 Submit to a Dataproc cluster: `run_cluster.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

: "${PROJECT_ID:?set PROJECT_ID}"
: "${REGION:?set REGION}"
: "${CLUSTER:?set CLUSTER}"
: "${BUCKET:?set BUCKET}"
: "${INPUT_URI:?set INPUT_URI}"
: "${SCRIPT_URI:?set SCRIPT_URI}"
: "${STAGING_TABLE:?set STAGING_TABLE}"
: "${TAX_RATE:=0.00}"

gcloud dataproc jobs submit pyspark "${SCRIPT_URI}" \
  --cluster="${CLUSTER}" \
  --region="${REGION}" \
  --labels=purpose=learning,workload=orders-etl \
  --max-failures-total=1 \
  -- \
  --input="${INPUT_URI}" \
  --staging-table="${STAGING_TABLE}" \
  --temp-gcs-bucket="${BUCKET}" \
  --tax-rate="${TAX_RATE}"
```

Run it from a shell where the variables are set. The job's runtime identity must be able to read the input object, write temporary objects if the connector needs them, and write the staging table.

### 12.7 Submit to Dataproc Serverless: `run_serverless.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

: "${PROJECT_ID:?set PROJECT_ID}"
: "${REGION:?set REGION}"
: "${BUCKET:?set BUCKET}"
: "${RUNTIME_SA:?set RUNTIME_SA}"
: "${INPUT_URI:?set INPUT_URI}"
: "${SCRIPT_URI:?set SCRIPT_URI}"
: "${STAGING_TABLE:?set STAGING_TABLE}"
: "${SERVERLESS_VERSION:?set SERVERLESS_VERSION to a supported runtime}"
: "${TAX_RATE:=0.00}"

BATCH="orders-etl-$(date +%Y%m%d%H%M%S)"

gcloud dataproc batches submit pyspark "${SCRIPT_URI}" \
  --batch="${BATCH}" \
  --region="${REGION}" \
  --deps-bucket="gs://${BUCKET}" \
  --service-account="${RUNTIME_SA}" \
  --version="${SERVERLESS_VERSION}" \
  --ttl=1h \
  -- \
  --input="${INPUT_URI}" \
  --staging-table="${STAGING_TABLE}" \
  --temp-gcs-bucket="${BUCKET}" \
  --tax-rate="${TAX_RATE}"

gcloud dataproc batches describe "${BATCH}" --region="${REGION}"
```

Use a supported runtime version verified from the current documentation. This example's `--ttl` is a guardrail; it can terminate a job that runs longer than expected, so choose a value consistent with the workload and SLA. The staging table is shared in this minimal lab; for concurrent runs, make the staging table run-scoped and pass that name into the script.

### 12.8 Promote staging to curated output: `validate.sql`

Run the following with `bq query --use_legacy_sql=false` after the staging write succeeds. Replace project/dataset/table names. The target table must exist.

```sql
MERGE `YOUR_PROJECT_ID.dataproc_lab.orders_curated` AS T
USING (
  SELECT
    event_id,
    customer_id,
    event_ts,
    event_date,
    amount_usd,
    amount_with_tax,
    processed_at
  FROM `YOUR_PROJECT_ID.dataproc_lab.orders_stage`
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY event_id
    ORDER BY event_ts DESC, customer_id DESC
  ) = 1
) AS S
ON T.event_id = S.event_id
WHEN MATCHED AND (
  T.customer_id IS DISTINCT FROM S.customer_id OR
  T.event_ts IS DISTINCT FROM S.event_ts OR
  T.event_date IS DISTINCT FROM S.event_date OR
  T.amount_usd IS DISTINCT FROM S.amount_usd OR
  T.amount_with_tax IS DISTINCT FROM S.amount_with_tax
) THEN UPDATE SET
  customer_id = S.customer_id,
  event_ts = S.event_ts,
  event_date = S.event_date,
  amount_usd = S.amount_usd,
  amount_with_tax = S.amount_with_tax,
  processed_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN INSERT (
  event_id, customer_id, event_ts, event_date,
  amount_usd, amount_with_tax, processed_at
) VALUES (
  S.event_id, S.customer_id, S.event_ts, S.event_date,
  S.amount_usd, S.amount_with_tax, CURRENT_TIMESTAMP()
);
```

The `QUALIFY` tie-breaker here is only deterministic for the sample's equivalent duplicate rows; it is not a general conflict-resolution policy. A production source should carry a reliable update timestamp or monotonic source sequence.

Validation queries:

```sql
-- Expected for the sample: 4 unique event IDs in staging.
SELECT COUNT(*) AS row_count,
       COUNT(DISTINCT event_id) AS distinct_event_ids
FROM `YOUR_PROJECT_ID.dataproc_lab.orders_stage`;

-- Should return no rows.
SELECT event_id, COUNT(*) AS n
FROM `YOUR_PROJECT_ID.dataproc_lab.orders_curated`
GROUP BY event_id
HAVING COUNT(*) > 1;

-- Inspect date partitioning and result values.
SELECT event_id, customer_id, event_date, amount_usd, amount_with_tax
FROM `YOUR_PROJECT_ID.dataproc_lab.orders_curated`
ORDER BY event_id;
```

For the sample, expect four unique IDs (`evt-001` through `evt-004`). Exact timestamps and `processed_at` values depend on execution time. The target is updated through `MERGE`, so rerunning the same input should not create duplicate `event_id` rows.

### 12.9 Service account and permissions checklist

Before running, verify the runtime service account has the minimum permissions required by the selected setup:

- Read objects from `gs://${BUCKET}/raw/` and `gs://${BUCKET}/code/`.
- Create/read/delete temporary objects in the connector staging bucket or prefix, as required by the write method.
- Create BigQuery jobs in the project where the `MERGE` runs.
- Read/write the staging table and read/write the curated target table.
- Write logs and metrics.
- Use the CMEK key, if configured, and access the required APIs through the chosen network.

The identity that creates the cluster/batch may differ from the runtime identity. Confirm the documented Dataproc service-agent and VM service-account requirements for the selected configuration. Do not grant broad project roles to the runtime service account as a shortcut.

### 12.10 Monitoring and troubleshooting

| Symptom | Likely cause | Investigation / correction |
|---|---|---|
| `PERMISSION_DENIED` on GCS | Runtime identity lacks object access, bucket policy or perimeter denies access | Inspect the exact object/API in logs; grant least-privilege object permissions |
| BigQuery `Access Denied` | Missing job creation or dataset/table access; wrong project/location | Verify runtime SA, dataset location, target project, connector and query identity |
| Connector class/provider not found | Connector absent or incompatible with Spark runtime | Check image/runtime connector support and official compatibility matrix |
| Python module import fails only on executors | Dependency was installed only on driver or not distributed | Use supported `--py-files`/archives/environment mechanism and test executor imports |
| Driver OOM | Large `collect()`, oversized plan, too much driver-side state | Remove driver-side collection, increase driver only if evidence supports it |
| Executor OOM or spill | Oversized partitions, skew, insufficient memory/disk | Inspect Spark UI/stage metrics; tune partitions, skew, memory/disk based on evidence |
| Job slow despite many workers | Shuffle, skew, tiny files, low parallelism, serial stage, remote I/O | Inspect stage/task distribution, shuffle, spill and file layout before scaling |
| Duplicate target rows after retry | Append writes or non-idempotent side effects | Use run-scoped staging, stable keys, deterministic dedupe, `MERGE`, and uniqueness checks |
| Serverless batch remains pending/fails at startup | Quota, service account, subnet, dependency fetch, unsupported runtime/property | Inspect batch details/logs, quotas, IAM, region and runtime support |
| Cluster remains billable after failure | Cleanup path did not run or cluster deletion failed | Check cluster state and delete only the explicitly named lab cluster |

### 12.11 Spot/preemptible worker experiment

Perform only after the baseline job works:

1. Create a test cluster with a supported secondary-worker configuration and a current autoscaling policy, if applicable.
2. Run a sufficiently long, retryable batch workload and capture task retries, shuffle behavior, completion time, and job logs.
3. Compare with a primary-worker-only baseline using the same input and output validation.
4. Do not manually interrupt production workers to simulate failure. Use a controlled lab and follow current documentation for the selected feature.
5. Record whether capacity was available and whether the job completed; do not assume the cloud will reclaim a worker during the experiment.

Spot/preemptible capacity is an optimization, not a correctness mechanism. Use supported EFM configuration only after confirming image/version support and understanding its limitations.

### 12.12 Workflow template experiment

This exercise creates a **managed-cluster workflow template**, attaches the same PySpark job, inspects the resolved template, instantiates it, waits for the workflow to finish, validates the output, and deletes the template. It is cluster-based Dataproc (not a Serverless batch). The workflow-managed cluster is created for the workflow and deleted when the workflow completes; the GCS and BigQuery outputs remain durable.

Prerequisites: the APIs and lab bucket/dataset from Sections 3 and 12.5 exist; `SCRIPT_URI`, `INPUT_URI`, `STAGING_TABLE`, `BUCKET`, `REGION`, `PROJECT_ID`, `RUNTIME_SA`, `DATAPROC_IMAGE_VERSION`, and `TAX_RATE` are set; the deployer can create/update/instantiate workflow templates and create Dataproc clusters/jobs; the runtime identity has the permissions in Section 12.9. Use a supported image version returned by `gcloud dataproc image-versions list --region="${REGION}"`.

```bash
set -euo pipefail
: "${PROJECT_ID:?set PROJECT_ID}"
: "${REGION:?set REGION}"
: "${BUCKET:?set BUCKET}"
: "${RUNTIME_SA:?set RUNTIME_SA}"
: "${SCRIPT_URI:?set SCRIPT_URI}"
: "${INPUT_URI:?set INPUT_URI}"
: "${STAGING_TABLE:?set STAGING_TABLE}"
: "${DATAPROC_IMAGE_VERSION:?set a supported image version}"
: "${TAX_RATE:=0.00}"

TEMPLATE="orders-etl-$(date +%Y%m%d%H%M%S)"

gcloud dataproc workflow-templates create "${TEMPLATE}" \
  --region="${REGION}" \
  --labels=purpose=learning,workload=orders-etl

gcloud dataproc workflow-templates set-managed-cluster "${TEMPLATE}" \
  --region="${REGION}" \
  --cluster-name="${TEMPLATE}-cluster" \
  --image-version="${DATAPROC_IMAGE_VERSION}" \
  --num-workers=2 \
  --master-machine-type=e2-standard-2 \
  --worker-machine-type=e2-standard-2 \
  --bucket="${BUCKET}" \
  --service-account="${RUNTIME_SA}" \
  --labels=purpose=learning,workload=orders-etl

gcloud dataproc workflow-templates add-job pyspark "${SCRIPT_URI}" \
  --workflow-template="${TEMPLATE}" \
  --region="${REGION}" \
  --step-id=orders-etl \
  --labels=purpose=learning,workload=orders-etl \
  -- \
  --input="${INPUT_URI}" \
  --staging-table="${STAGING_TABLE}" \
  --temp-gcs-bucket="${BUCKET}" \
  --tax-rate="${TAX_RATE}"

gcloud dataproc workflow-templates describe "${TEMPLATE}" --region="${REGION}"
gcloud dataproc workflow-templates instantiate "${TEMPLATE}" --region="${REGION}"
```

Instantiation is synchronous by default in the documented CLI flow; if your SDK/version or wrapper returns before completion, inspect the workflow operation/job state and wait for a terminal success state before validating. Run the validation SQL in Section 12.8 and confirm four unique event IDs for the supplied sample. If the workflow fails, inspect the workflow/job logs before cleanup. Delete the template only after recording the result:

```bash
gcloud dataproc workflow-templates delete "${TEMPLATE}" --region="${REGION}"
```

The template and workflow-managed cluster are billable resources while active. Keep the worker count small, use a timeout/operational deadline appropriate to the lab, and verify the managed cluster was deleted after completion. For cross-service orchestration, dependencies, alerts, and backfills, Topic 08 covers Cloud Composer and Workflows. Avoid running heavy Spark work inside Airflow workers; submit a Dataproc job/batch and monitor its lifecycle.

### 12.13 Cleanup

First inspect names and outputs. Delete only the cluster created for this lab:

```bash
gcloud dataproc clusters describe "${CLUSTER}" --region="${REGION}"
gcloud dataproc clusters delete "${CLUSTER}" --region="${REGION}"
```

If a workflow fails, inspect its status and logs first; then verify whether its managed cluster was deleted. Delete any remaining cluster only after confirming its exact lab name and ownership. Delete the workflow template created in Section 12.12 after recording results.

Delete staging tables only after validation and only if they are lab-owned:

```bash
bq rm -f "${PROJECT_ID}:${DATASET}.orders_stage"
```

Optional bucket cleanup is intentionally not automated here because a bucket may contain other files. If and only if the bucket is dedicated to this lab and you have checked its contents, delete its objects and then the bucket using explicit commands. Remove workflow templates created by the lab when no longer needed. Verify no cluster, batch, idle VM, staging object, or temporary bucket remains.

### 12.14 Compare cluster and Serverless: `observations.md`

Record measured results from your own environment. Do not copy another learner's runtime as a benchmark.

| Metric | Cluster | Serverless batch |
|---|---:|---:|
| Image/runtime version | | |
| Machine types / runtime configuration | | |
| Provisioning/startup duration | | |
| Spark application runtime | | |
| End-to-end wall-clock duration | | |
| Input rows / bytes | | |
| Output rows | | |
| Shuffle read/write and spill | | |
| Retries / failed tasks | | |
| BigQuery validation bytes processed | | |
| Actual billed cost and time window | | |
| Configuration/operations effort (notes) | | |

Compare only runs with the same input, code version, output contract, and similar region/permission setup. Billing export data may arrive later than job completion; distinguish estimated cost from actual billed cost. If cost cannot be isolated from shared project usage, state that limitation instead of manufacturing a figure.

For a defensible comparison, run each mode at least three times on the same immutable input and code version, after one clearly labelled warm-up run if dependency caching is part of the intended scenario. Report every run plus the median end-to-end duration; do not discard slow runs without documenting why. Compare **total workload cost**, not only Spark executor runtime: include cluster VM and disk time from creation to deletion, Dataproc charges where applicable, Serverless usage, GCS temporary objects/requests, BigQuery staging/validation/MERGE work, and relevant network costs. Use the pricing calculator for a planning estimate, then reconcile with billing export after usage has posted. Keep resources labelled and isolate the lab project or billing window where possible. If usage cannot be attributed reliably, report a cost range or mark actual cost as unavailable rather than claiming a precise comparison.

### 12.15 Additional exercises

1. **Partitioning:** compare the default partition layout with a deliberately repartitioned dataset. Explain the shuffle cost and task count.
2. **Skew:** introduce a dominant customer key and inspect task-duration skew. Propose salting or a different aggregation strategy only if semantics permit.
3. **Failure handling:** remove a required input object or deny one permission; verify that the job fails visibly and no partial output is promoted.
4. **Idempotency:** run the same input twice. Prove target key uniqueness and compare business columns, not only row count.
5. **Engine selection:** implement one relational aggregate in BigQuery SQL and one Spark version; compare bytes processed, elapsed time, operational steps, and actual cost.
6. **Migration design:** choose an existing Hadoop/Spark job and write a path, dependency, catalog, identity, and rollback migration checklist.

---

## 13. Knowledge checks with answers

### Questions

1. What is the difference between the Spark driver and executors?
2. Why can a `groupBy` or large join be expensive?
3. Why should durable outputs not live only in cluster HDFS?
4. What does `--` do in a `gcloud dataproc jobs submit pyspark` command?
5. Does Serverless mean there is no startup time or runtime compatibility concern?
6. Why is a plain BigQuery append not necessarily safe under retries?
7. What is the purpose of a staging table plus `MERGE`?
8. When would BigQuery SQL be preferable to Dataproc?
9. What risks accompany Spot/preemptible secondary workers?
10. Why should initialization actions not be assumed to work for Serverless?
11. What should be checked before overriding the BigQuery connector?
12. What does a Dataproc workflow template do, and how is it different from Composer?
13. Name three useful signals to inspect before adding workers.
14. What is the role of IAM on the runtime service account?
15. How should you compare Serverless and cluster cost?

### Answers

1. The driver plans and coordinates execution; executors run tasks and hold/cache data and shuffle blocks.
2. They redistribute records across partitions (shuffle), potentially moving large amounts of data over the network and spilling to disk; skew can leave a few tasks much slower than others.
3. Cluster deletion can remove HDFS and local disks. Durable storage must be external to the cluster lifecycle, such as Cloud Storage or BigQuery.
4. It separates `gcloud` options from arguments passed to the PySpark driver.
5. No. Serverless removes cluster management but still has provisioning/startup, supported runtime versions, dependency constraints, quotas, and costs.
6. A retry after a successful append but before orchestration records success can append the same records again.
7. It isolates a run's output, validates it, and merges by stable key so reruns can be idempotent under a defined conflict policy.
8. When data is already in BigQuery and transformations are relational SQL operations; SQL avoids data movement and a separate Spark runtime.
9. Capacity may be reclaimed or unavailable, causing task retries, delays, or failures. Workloads must tolerate interruptions; never store unique durable state only on those workers.
10. Initialization actions configure cluster VMs. Serverless uses its own runtime/dependency mechanisms.
11. Spark/runtime compatibility, current built-in connector, exact supported override property, and the connector's documented compatibility matrix.
12. It defines a repeatable dependency graph of Dataproc jobs and cluster configuration; Composer orchestrates broader pipelines across services with Airflow scheduling, sensors, retries, and alerting.
13. Shuffle read/write, spill, task-duration skew, executor CPU/memory, failed tasks, input file count/size, and driver memory.
14. It grants the job the minimum permissions to access its input, staging output, BigQuery tables/jobs, logs, and optional encryption keys without embedding credentials.
15. Run equivalent jobs in the same region with identical input/output contracts; record startup, application and end-to-end times, resource configuration, metrics, and actual billing data after it is available.

---

## 14. Syllabus checkpoint

Mark each item only after you can explain or demonstrate it.

- [ ] Explain Dataproc cluster nodes, image versions, Spark, Hadoop, and Hive.
- [ ] Submit PySpark with `gcloud dataproc jobs submit pyspark`.
- [ ] Read Cloud Storage data via `gs://` and explain why cluster HDFS is ephemeral.
- [ ] Create, run, validate, and delete an ephemeral cluster.
- [ ] Submit the equivalent supported PySpark batch to Dataproc Serverless.
- [ ] Read/write BigQuery using the Spark BigQuery connector.
- [ ] Select a compatible image/runtime and manage Python/JVM dependencies.
- [ ] Explain workflow templates, autoscaling policies, and Spot/preemptible secondary workers.
- [ ] Discuss cost trade-offs across ephemeral/long-running clusters, Serverless, worker sizing, and disks.
- [ ] Explain Dataproc on GKE, shared metastore choices, Kerberos, VPC-SC, and CMEK at awareness level.
- [ ] Choose among Dataproc, Dataflow, and BigQuery SQL for a workload.
- [ ] Explain migration and idempotent retry behavior.
- [ ] Record actual lab observations and clean up resources.

**Exit criterion:** complete one GCS → PySpark → BigQuery pipeline on a cluster and one on Serverless, validate target key uniqueness, clean up lab resources, and write a short evidence-based comparison. If you cannot provision GCP resources, complete the code review and command dry-run, but mark cloud execution as **not performed**.

---

## 15. Summary and transition to Topic 08

Dataproc is the managed route for Spark/Hadoop workloads when Spark compatibility or its ecosystem justifies a separate distributed engine. Dataproc clusters provide control over nodes, images, initialization, and cluster-specific configuration; Serverless batches reduce cluster lifecycle management for supported workloads. Neither removes the need for dependency control, least-privilege IAM, reliable output semantics, monitoring, and cost measurement.

Default decision order:

1. **BigQuery SQL first** for warehouse-native relational transformations.
2. **Dataflow** for event-time streaming or Beam-based batch/stream processing requirements.
3. **Dataproc / Dataproc Serverless** when Spark/Hadoop libraries, existing code, or distributed Spark processing are justified.

Topic 08 — Cloud Composer and Workflows — adds scheduling, dependencies, retries, backfills, alerts, and cross-service orchestration. Keep compute execution inside Dataproc/Dataflow/BigQuery and let the orchestrator coordinate lifecycle and quality gates.

---

## 16. Official documentation references

Use the current official docs before deployment because image versions, runtime defaults, supported properties, and connector compatibility change.

1. [Dataproc overview](https://cloud.google.com/dataproc/docs/concepts/overview)
2. [Dataproc image versions](https://cloud.google.com/dataproc/docs/concepts/versioning/dataproc-versions)
3. [`gcloud dataproc jobs submit pyspark` reference](https://cloud.google.com/sdk/gcloud/reference/dataproc/jobs/submit/pyspark)
4. [Dataproc Serverless for Spark overview](https://cloud.google.com/dataproc-serverless/docs/concepts/overview)
5. [`gcloud dataproc batches submit pyspark` reference](https://cloud.google.com/sdk/gcloud/reference/dataproc/batches/submit/pyspark)
6. [Dataproc Serverless runtime versions](https://cloud.google.com/dataproc-serverless/docs/concepts/versions)
7. [Spark BigQuery connector source and compatibility matrix](https://github.com/GoogleCloudDataproc/spark-bigquery-connector)
8. [Dataproc autoscaling](https://cloud.google.com/dataproc/docs/concepts/configuring-clusters/autoscaling)
9. [Dataproc workflow templates](https://cloud.google.com/dataproc/docs/concepts/workflows/overview)
10. [Dataproc initialization actions](https://cloud.google.com/dataproc/docs/concepts/configuring-clusters/init-actions)
11. [Dataproc enhanced flexibility mode](https://cloud.google.com/dataproc/docs/concepts/configuring-clusters/enhanced-flexibility-mode)
12. [Dataproc security best practices](https://cloud.google.com/dataproc/docs/concepts/security)
13. [Cloud Storage connector for Hadoop](https://cloud.google.com/dataproc/docs/concepts/connectors/cloud-storage)
14. [BigQuery IAM roles and permissions](https://cloud.google.com/bigquery/docs/access-control)
15. [Dataproc pricing](https://cloud.google.com/dataproc/pricing)
16. [Dataproc Serverless pricing](https://cloud.google.com/dataproc-serverless/pricing)
17. [Cloud Composer overview — Topic 08 dependency](https://cloud.google.com/composer/docs/composer-3/composer-overview)
18. [Dataflow overview — Topic 06 comparison](https://cloud.google.com/dataflow/docs/concepts/overview)
19. [Dataproc on GKE](https://cloud.google.com/dataproc/docs/guides/dpgke/overview)
20. [BigLake metastore overview](https://cloud.google.com/biglake/docs/metastore-intro)
21. [`workflow-templates set-managed-cluster` CLI reference](https://cloud.google.com/sdk/gcloud/reference/dataproc/workflow-templates/set-managed-cluster)
22. [`workflow-templates add-job pyspark` CLI reference](https://cloud.google.com/sdk/gcloud/reference/dataproc/workflow-templates/add-job/pyspark)

---

## Verification and execution status

This lesson was reviewed against Topic 07 in `roadmap-Google-Cloud-BigQuery-and-GCP-Data-Engineering.md`, its location in `Roadmap_ptree.md`, and Topic 06 processing-service context. Topic 08 is used only as a downstream orchestration dependency. The audit covered all sections, commands, PySpark examples, SQL, diagrams, cost guidance, and practical exercises. The workflow-template exercise was completed with explicit managed-cluster configuration and cleanup; the cluster-versus-Serverless exercise now specifies a repeatable comparison method without inventing results.

**Static-review status:** PASS for syllabus coverage and reviewed command/code structure. Current official Google Cloud CLI references were consulted for workflow-template managed-cluster setup, PySpark job attachment, and Serverless batch flags. Python syntax and SQL logic were manually inspected; no live cloud integration test was performed.

**Execution status:** No Google Cloud cluster, Serverless batch, workflow template, BigQuery write, benchmark, or billing comparison was executed as part of preparing this lesson. The reader must verify the selected region, current image/runtime version, IAM, network/perimeter setup, connector compatibility, and current pricing in their own project before execution.
