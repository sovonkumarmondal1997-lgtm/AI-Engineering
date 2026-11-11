# Roadmap — Module 2C.4: Google Cloud BigQuery and GCP Data Engineering

This is the learning roadmap for the fourth module of Stage 2C, **Data
Engineering_3**. It tells you **what** to learn about BigQuery and the
Google Cloud data platform, **in what order**, **how** to learn each topic,
and **how to prove to yourself** that you have learned it before you move
on.

Stage 2B covered AWS and Databricks in depth. Google Cloud is the third
major platform, and BigQuery is one of the most popular analytics engines
in the world. Its design differs from Snowflake and Redshift: it is
**serverless**, separates storage from compute completely, bills by data
scanned or by reserved **slots**, and is deeply integrated with Pub/Sub,
Dataflow, and Vertex AI.

This module teaches BigQuery in depth, then the GCP services a data
engineer combines with it for streaming, batch processing, Spark,
orchestration, and governance. Most work is SQL plus Python (client
libraries, Apache Beam, PySpark).

---

## 1. Module outcome

By the end of this module you will be able to:

- Map GCP data services to the AWS/Azure equivalents and choose between
  them.
- Explain BigQuery's architecture (Dremel, Colossus, Capacitor, Jupiter)
  and its slot-based execution.
- Partition, cluster, and tune BigQuery tables and **control query cost**.
- Load batch data, stream data, and query external data in BigQuery.
- Use scheduled queries, **BigQuery ML**, and routines.
- Build batch and streaming pipelines with **Pub/Sub** and **Dataflow
  (Apache Beam)**.
- Run Spark with **Dataproc** and **Dataproc Serverless**.
- Orchestrate with **Cloud Composer (Airflow)** and **Workflows**.
- Govern data with **IAM**, policy tags, row-level security, **Dataplex**,
  and Data Catalog capabilities.

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| SQL, window functions, partitions | Stage 2 — Module 2.6 | BigQuery Standard SQL |
| Columnar formats, partitioning | Stage 2 — Module 2.5 | Capacitor, external tables |
| Dimensional modelling | Stage 2 — Module 2.8 | BigQuery nested/repeated and star schemas |
| Streaming, windows, watermarks | Stage 2 — Module 2.16 | Pub/Sub and Dataflow |
| Spark | Stage 2 — Module 2.14 | Dataproc |
| Airflow | Stage 2 — Module 2.13 | Cloud Composer |
| Cloud storage and IAM concepts | Stage 2 — Module 2.17; Stage 2B — 2B.3 | GCS, service accounts |
| Terraform, CI/CD | Stage 2 — Module 2.18 | Deploying GCP resources |
| Snowflake warehouses and cost | Module 2C.3 | A useful contrast for slots vs credits |

**Tools needed:**

- A **Google Cloud account** with the free tier or sandbox; **set a
  budget alert and quota limits** first. BigQuery's sandbox needs no
  billing but has limits.
- `gcloud` CLI, `bq` CLI, and Python 3.12+ in a `uv` project: `uv add
  google-cloud-bigquery google-cloud-storage google-cloud-pubsub
  apache-beam[gcp] db-dtypes pandas pytest`.
- Optional: BigQuery emulators and the Pub/Sub emulator for local tests.

**A note on cost:** an unbounded query on a large table can cost real
money. Always preview with a **dry run**, set `maximum_bytes_billed`, and
use partition filters.

---

## 3. How the module is organised

The nine topics are grouped into five phases. Work through them **in order**.

```text
Phase A — The Platform                               (Basics)
  01 GCP data services landscape

Phase B — BigQuery Core                              (Intermediate → Advanced)
  02 BigQuery architecture, slots, and storage
  03 Partitioning, clustering, and query cost control
  04 Loading, streaming, and external tables
  05 BigQuery ML and scheduled queries

Phase C — Processing Services                        (Intermediate → Advanced)
  06 Pub/Sub and Dataflow (Apache Beam)
  07 Dataproc and Dataproc Serverless

Phase D — Orchestration                              (Intermediate)
  08 Cloud Composer and Workflows

Phase E — Governance                                 (Advanced)
  09 Dataplex, IAM, and governance

Consolidate
  Module mini-project: a serverless GCP data platform
```

The dependency chain:

```text
01 ► 02 ► 03 ► 04 ► 05 ► 06 ► 07 ► 08 ► 09
map  how  cut  get  SQL  stream spark orch- govern
     it   cost data +ML  & batch      est-
     works      in            engines  ration
```

Why this order:

- The landscape (01) gives context; BigQuery internals (02) explain cost
  and performance.
- Cost control (03) and loading (04) are the practical daily skills; ML and
  scheduled queries (05) extend SQL.
- Pub/Sub, Dataflow, and Dataproc (06–07) feed and transform BigQuery;
  orchestration (08) schedules everything; governance (09) secures it.

---

## 4. Suggested schedule

About **5 weeks at 8 hours per week**.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — landscape · Topic 02 — BigQuery architecture |
| 2 | Topic 03 — partitioning, clustering, cost · Topic 04 — loading |
| 3 | Topic 05 — BQML and scheduled queries · Topic 06 — Pub/Sub and Dataflow |
| 4 | Topic 07 — Dataproc · Topic 08 — Composer and Workflows |
| 5 | Topic 09 — governance · mini-project |

---

## 5. How to study every topic (the serverless-cloud loop)

```text
Read → Draw the architecture → Dry-run for cost → Build → Check bytes
billed and slots used → Break it → Clean up → Write it down → Explain aloud
```

1. **Read** the topic file once, fully.
2. **Draw** the services, identities, and data flow.
3. **Dry-run** every query and estimate cost before running.
4. **Build** with Terraform or `gcloud`/`bq` scripts, not only the console.
5. **Check** `INFORMATION_SCHEMA.JOBS` for bytes billed and slot time.
6. **Break it**: bad schema, duplicate messages, missing permission.
7. **Clean up** every resource (delete datasets, topics, clusters).
8. **Write it down** in `module-2c4-notes.md`.
9. **Explain aloud** why you chose each service.

Keep one `gcp_lab/` project:

```text
gcp_lab/
├── terraform/            # datasets, buckets, topics, service accounts, Composer
├── sql/                  # BigQuery DDL, queries, scheduled queries, BQML
├── beam/                 # Dataflow pipelines
├── dataproc/             # PySpark jobs
├── dags/                 # Composer DAGs
├── governance/           # policy tags, IAM bindings, data quality rules
└── tests/
```

---

## 6. Phase A — The Platform (Basics)

### Topic 01 — [GCP data services landscape](01-gcp-data-services-landscape.md)

**Why it comes first:** GCP has many overlapping products. A map prevents
choosing by name recognition instead of by fit.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Projects, folders, organisations, billing accounts; regions and multi-regions |
| Basics | Service accounts, IAM roles, and Application Default Credentials; the `gcloud` workflow |
| Basics | The data service families: **storage** (GCS, Bigtable, Spanner, Cloud SQL, AlloyDB, Firestore), **analytics** (BigQuery), **streaming** (Pub/Sub, Dataflow), **batch** (Dataproc), **orchestration** (Composer, Workflows), **governance** (Dataplex), **BI/ML** (Looker, Vertex AI) |
| Intermediate | Mapping to AWS/Azure: S3↔GCS, Redshift/Athena↔BigQuery, Kinesis/MSK↔Pub/Sub, Glue/EMR↔Dataflow/Dataproc, MWAA↔Composer, Lake Formation↔Dataplex |
| Intermediate | Reference architectures: batch lake→warehouse, streaming analytics, CDC replication (Datastream), ML feature pipelines |
| Intermediate | **Datastream** (serverless CDC), **Data Fusion**, **Dataform** (SQL transformations), and **BigLake** — what each is for |
| Advanced | Networking basics: VPC, Private Google Access, VPC Service Controls (data exfiltration perimeters) |
| Advanced | Organisation policy, labels, and billing export to BigQuery |
| Advanced | Choosing between serverless and managed-cluster services; open-source portability (Beam, Spark, Iceberg) |
| Advanced | Pricing models overview: on-demand vs capacity (slots), streaming, storage tiers |

**How to learn it**

1. Read the topic file.
2. Build a one-page map: for each task (store files, query SQL, stream,
   transform, orchestrate, govern) name the GCP service and its AWS/Azure
   twin.
3. Design a reference architecture for "daily sales files plus real-time
   clickstream".

**Hands-on exercise — `experiments/01_landscape/`**

1. Create a project, a budget alert, and a least-privilege service account
   with Terraform.
2. Create a GCS bucket and a BigQuery dataset; load a CSV with `bq`.
3. Enable billing export to BigQuery (or inspect the sandbox equivalent).
4. Write the service-map document.

**Checkpoint:**

- [ ] Map GCP services to AWS/Azure equivalents.
- [ ] Explain projects, IAM, and service accounts.
- [ ] Choose services for a reference architecture.

**Common mistakes:** using primitive owner roles; one project for
everything; no budget alerts; choosing Dataproc where BigQuery SQL would
do.

---

## 7. Phase B — BigQuery Core (Intermediate → Advanced)

### Topic 02 — [BigQuery architecture, slots, and storage](02-bigquery-architecture-slots-and-storage.md)

**Why here:** BigQuery's cost and speed make sense only when you know how
it executes queries and stores data.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Serverless analytics: no cluster to manage; datasets, tables, views, and jobs |
| Basics | Standard SQL, the console, `bq`, and the Python client (`client.query().result()`) |
| Basics | **On-demand pricing** (per TB scanned) vs **capacity pricing** (slots) |
| Intermediate | The architecture: **Dremel** execution trees, **Colossus** storage, **Capacitor** columnar format, **Jupiter** network, and the in-memory **shuffle** service |
| Intermediate | **Slots**: units of compute; reservations, assignments, and autoscaling editions (Standard, Enterprise, Enterprise Plus) |
| Intermediate | Reading the **execution graph** and stage statistics; slot milliseconds; shuffle spills |
| Intermediate | Nested and repeated fields (`STRUCT`, `ARRAY`), `UNNEST`, and why denormalisation works well in BigQuery |
| Intermediate | Storage: logical vs physical billing, long-term storage discount, time travel (up to 7 days) and fail-safe |
| Advanced | Table types: native, external, **BigLake**, **BigQuery tables for Apache Iceberg**, materialised views, snapshots, and clones |
| Advanced | Query optimiser behaviour: join strategies (broadcast vs hash), `APPROX_` functions, and the BI Engine in-memory cache |
| Advanced | Multi-tenant concerns: reservations per team, concurrency, and queueing |
| Advanced | Comparison with Snowflake and Redshift (links to Module 2C.3) |

**How to learn it**

1. Read the topic file.
2. Draw a query's path from SQL → stages → slots → shuffle → result.
3. Compare the cost of on-demand and 100 slots for a workload.

**Hands-on exercise — `experiments/02_bigquery_architecture/`**

1. Query a public dataset; read the execution graph and slot usage.
2. Run the same query on a nested table and a flattened table; compare
   bytes processed.
3. Query `INFORMATION_SCHEMA.JOBS` for bytes billed, slot-ms, and runtime
   per job.
4. Use time travel to query yesterday's table state.
5. Estimate break-even between on-demand and capacity for your workload.

**Checkpoint:**

- [ ] Explain Dremel, Colossus, slots, and shuffle in plain language.
- [ ] Choose on-demand vs capacity pricing.
- [ ] Use nested and repeated fields.
- [ ] Read a query execution graph.

**Common mistakes:** copying star schemas blindly instead of using nested
data; `SELECT *` on wide tables; ignoring slot contention on shared
reservations.

---

### Topic 03 — [Partitioning, clustering, and query cost control](03-partitioning-clustering-and-query-cost-control.md)

**Why here:** BigQuery cost scales with bytes read. Partitioning and
clustering are the main way to read less.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Partitioned tables**: by ingestion time, date/timestamp column, or integer range; partition pruning |
| Basics | `require_partition_filter` and partition expiration |
| Basics | Dry runs and `maximum_bytes_billed`; the "bytes processed" estimate |
| Intermediate | **Clustered tables**: up to four columns, order matters, block pruning; combining partitioning and clustering |
| Intermediate | Choosing keys: filter columns, cardinality, and partition size (avoid too many tiny partitions) |
| Intermediate | Cost levers: select only needed columns, avoid `SELECT *`, filter early, use `LIMIT` carefully (it does not cut bytes billed on its own), approximate aggregates |
| Intermediate | **Materialised views**, BI Engine, and result caching (24-hour cache) |
| Intermediate | Table design for update patterns: append-only, `MERGE`, and the cost of DML |
| Advanced | Query optimisation: join order, pre-aggregation, avoiding cross joins and skew, `QUALIFY`, window function cost |
| Advanced | Cost governance: custom quotas, per-user and per-project limits, reservations, labels, and billing export analysis |
| Advanced | Finding expensive queries with `INFORMATION_SCHEMA.JOBS_BY_PROJECT` and `JOBS_TIMELINE` |
| Advanced | Search indexes, vector indexes — awareness; table snapshots for cheap backups |

**How to learn it**

1. Read the topic file.
2. Take a 2 TB event table: design partitioning and clustering for five
   typical queries and estimate bytes scanned.
3. List the quickest five ways to cut the bill.

**Hands-on exercise — `experiments/03_partition_cluster/`**

1. Create the same table unpartitioned, partitioned by day, and
   partitioned + clustered; run identical queries and compare bytes
   processed.
2. Enable `require_partition_filter` and confirm unfiltered queries fail.
3. Set `maximum_bytes_billed` on a client and trigger the guard.
4. Build a materialised view and show the cost of repeated aggregates drop.
5. Write a "top 20 costly queries this month" report from `INFORMATION_SCHEMA`.

**Checkpoint:**

- [ ] Choose partitioning and clustering for a workload.
- [ ] Estimate cost with a dry run.
- [ ] Apply guardrails (`maximum_bytes_billed`, partition filters).
- [ ] Find and fix expensive queries.

**Common mistakes:** over-partitioning; partitioning on a column nobody
filters; believing `LIMIT` reduces cost; no cost guardrails for analysts.

---

### Topic 04 — [BigQuery loading, streaming, and external tables](04-bigquery-loading-streaming-and-external-tables.md)

**Why here:** getting data in reliably is the central engineering task.
BigQuery offers several paths with different cost, latency, and
guarantees.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Batch load jobs** from GCS (free ingestion): CSV, JSON, Avro, Parquet, ORC; schema autodetect vs explicit schema |
| Basics | Write dispositions: `WRITE_APPEND`, `WRITE_TRUNCATE`, `WRITE_EMPTY`; load job idempotency using job IDs |
| Basics | Python client: `load_table_from_uri`, `load_table_from_dataframe`, `load_table_from_file` |
| Intermediate | **External tables** and **BigLake tables** over GCS (Hive-style partitioning, metadata caching); trade-offs vs native tables |
| Intermediate | **Storage Write API** (recommended for streaming; exactly-once with committed streams) vs legacy `insertAll` |
| Intermediate | Streaming buffer behaviour, DML limits on recently streamed data, and cost of streaming |
| Intermediate | Schema evolution: adding columns, relaxing modes, `ALLOW_FIELD_ADDITION`, and handling type changes |
| Intermediate | `MERGE`-based upserts for CDC; deduplicating with `QUALIFY ROW_NUMBER()` |
| Advanced | **Datastream** for CDC from MySQL/Postgres/Oracle into BigQuery; **Pub/Sub BigQuery subscriptions** (direct writes) |
| Advanced | Federated queries to Cloud SQL, Spanner, and Bigtable; when federation is a trap |
| Advanced | Data transfer service for SaaS and cross-cloud sources (S3, Azure) |
| Advanced | Load error handling: `max_bad_records`, error tables, quarantine patterns, and monitoring `INFORMATION_SCHEMA.LOAD_JOBS` |
| Advanced | Landing-zone → raw → curated layering inside BigQuery (medallion on BigQuery) |

**How to learn it**

1. Read the topic file.
2. For a daily 50 GB file drop, a 5k events/s stream, and a Postgres CDC
   source, choose the ingestion path and justify.
3. Draw how you would make each load idempotent.

**Hands-on exercise — `experiments/04_loading/`**

1. Load Parquet from GCS with a deterministic job ID; re-run and confirm
   no duplicate load.
2. Create an external table over Hive-partitioned Parquet; compare query
   cost and speed with a native copy.
3. Stream 1 million events with the Storage Write API client; observe
   latency and the streaming buffer.
4. Apply CDC records to a target with `MERGE`; handle deletes.
5. Load a file with bad rows and route them to a quarantine table.

**Checkpoint:**

- [ ] Choose batch load, Storage Write API, Pub/Sub subscription, or
      Datastream.
- [ ] Make loads idempotent.
- [ ] Evolve schemas safely.
- [ ] Explain external vs native table trade-offs.

**Common mistakes:** streaming when batch is free and sufficient; no
deduplication on at-least-once streams; autodetecting schemas in
production; heavy use of federated queries as a pipeline.

---

### Topic 05 — [BigQuery ML and scheduled queries](05-bigquery-ml-and-scheduled-queries.md)

**Why here:** two features that turn BigQuery from a store into a small
platform: SQL-based machine learning and built-in scheduling.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Scheduled queries** through the Data Transfer Service: schedule, destination table, parameters (`@run_date`), and notifications |
| Basics | **Routines**: SQL UDFs, JavaScript UDFs, stored procedures, and table functions |
| Basics | Scripting: variables, `IF`, loops, `EXECUTE IMMEDIATE`, and temporary tables |
| Intermediate | **BigQuery ML**: `CREATE MODEL` for linear/logistic regression, boosted trees, k-means, matrix factorisation, ARIMA_PLUS time series |
| Intermediate | Training, evaluation (`ML.EVALUATE`), prediction (`ML.PREDICT`), feature preprocessing (`TRANSFORM`), and explainability |
| Intermediate | Importing/serving external models (TensorFlow, ONNX) and remote models calling Vertex AI |
| Intermediate | Backfilling scheduled queries and idempotent date-parameterised loads |
| Advanced | **Dataform** for SQL pipelines: dependencies, assertions, incremental tables (alternative to dbt, Module 2C.6) |
| Advanced | Generative AI functions in SQL (`ML.GENERATE_TEXT`, embeddings, vector search) — awareness |
| Advanced | Limits of BQML: when to move to Vertex AI pipelines (links to Module 2C.10) |
| Advanced | Governance of models: versioning, evaluation tables, and access control |

**How to learn it**

1. Read the topic file.
2. Define a churn problem and decide which parts stay in SQL and which
   need Vertex AI.
3. Write a parameterised daily aggregation as a scheduled query.

**Hands-on exercise — `experiments/05_bqml_scheduling/`**

1. Create a scheduled query that builds a daily summary table from a
   partition parameter; backfill 7 days.
2. Train a logistic-regression model with `CREATE MODEL`; evaluate and
   predict.
3. Train an `ARIMA_PLUS` forecast on a time series and read the results.
4. Wrap steps in a stored procedure and call it from a schedule.
5. Recreate the same pipeline in Dataform with assertions.

**Checkpoint:**

- [ ] Schedule, parameterise, and backfill queries.
- [ ] Train, evaluate, and use a BQML model.
- [ ] Write routines and scripts.
- [ ] Decide when BQML is enough.

**Common mistakes:** scheduled queries without idempotency; treating BQML
as a full MLOps solution; no evaluation tracking.

---

## 8. Phase C — Processing Services (Intermediate → Advanced)

### Topic 06 — [Pub/Sub and Dataflow (Apache Beam)](06-pubsub-and-dataflow-apache-beam.md)

**Why here:** Pub/Sub carries events; Dataflow processes them with Beam.
Together they are GCP's streaming core, and Beam is the portable model
behind it (the concepts from Module 2.16 appear again).

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Pub/Sub**: topics, subscriptions (pull/push/BigQuery/Cloud Storage), acknowledgement, retention, and replay |
| Basics | Ordering keys, dead-letter topics, retry policies, and message attributes |
| Basics | Pub/Sub vs Kafka: managed, no partitions to size, per-message ack |
| Intermediate | **Apache Beam model**: `PCollection`, `PTransform`, `ParDo`, `GroupByKey`, `CoGroupByKey`, `Combine`, side inputs |
| Intermediate | Beam Python SDK; batch pipelines reading GCS and writing BigQuery; testing with `TestPipeline` and `assert_that` |
| Intermediate | Event time, **windowing** (fixed, sliding, session, global), **triggers**, watermarks, and allowed lateness |
| Intermediate | Streaming from Pub/Sub to BigQuery with dead-letter handling and deduplication by message ID |
| Advanced | Dataflow runner: autoscaling, Streaming Engine, Shuffle service, Flex Templates, and Dataflow SQL / templates |
| Advanced | Exactly-once semantics in Dataflow, stateful DoFns, timers, and the cost of state |
| Advanced | Observability: job graph, watermark lag, system lag, throughput, and worker logs |
| Advanced | Performance: fusion, hot keys, `Reshuffle`, batching writes, and worker sizing |
| Advanced | Beam vs Spark Structured Streaming vs Flink (links to Module 2.16) and when Beam portability matters |

**How to learn it**

1. Read the topic file.
2. Map concepts from Module 2.16 (watermarks, windows, state) onto Beam's
   names.
3. Draw a streaming pipeline with a dead-letter path.

**Hands-on exercise — `experiments/06_pubsub_dataflow/`**

1. Publish synthetic events to Pub/Sub, including duplicates and late data.
2. Write a Beam pipeline: parse → validate (bad records to dead-letter) →
   fixed windows → aggregate → BigQuery.
3. Run it locally with the DirectRunner and tests, then on Dataflow with a
   small worker pool.
4. Introduce a hot key and observe the effect; fix it with key salting.
5. Package the pipeline as a Flex Template and launch it.

**Checkpoint:**

- [ ] Explain Pub/Sub acknowledgement, replay, and dead-letter handling.
- [ ] Write and test a Beam pipeline with windows.
- [ ] Explain watermarks and triggers in Beam.
- [ ] Monitor and tune a Dataflow job.

**Common mistakes:** assuming Pub/Sub delivers once and in order; no
dead-letter topic; global windows on unbounded data; ignoring costs of
idle streaming jobs.

---

### Topic 07 — [Dataproc and Dataproc Serverless](07-dataproc-and-dataproc-serverless.md)

**Why here:** when you need Spark, Hive, or existing Hadoop-ecosystem
code on GCP, Dataproc is the managed answer (and a migration target from
Module 2C.2).

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Dataproc clusters**: master/worker nodes, image versions, and managed Spark/Hadoop/Hive |
| Basics | Submitting PySpark jobs with `gcloud dataproc jobs submit pyspark`; reading GCS (`gs://`) via the connector |
| Basics | Ephemeral clusters: create → run → delete; why storage lives in GCS, not HDFS |
| Intermediate | **Dataproc Serverless for Spark**: batches, no cluster management, autoscaling, and per-run configuration |
| Intermediate | **Workflow templates** and autoscaling policies; preemptible/Spot secondary workers |
| Intermediate | The **BigQuery connector for Spark**: reading and writing BigQuery from PySpark |
| Intermediate | Initialisation actions, custom images, and dependency management (Conda/pip) |
| Advanced | Cost optimisation: ephemeral vs long-running, right-sizing, Spot, and disk choices (links to Module 2.21) |
| Advanced | Dataproc on GKE and Metastore (Dataproc Metastore / BigLake Metastore) for shared catalogs |
| Advanced | Security: service accounts, Kerberos, VPC-SC, and CMEK — awareness |
| Advanced | Choosing between Dataproc, Dataflow, and BigQuery SQL for a workload |
| Advanced | Migrating on-prem Hadoop and Spark jobs to Dataproc |

**How to learn it**

1. Read the topic file.
2. Compare three jobs (SQL aggregation, streaming enrichment, legacy
   PySpark ETL) and choose BigQuery, Dataflow, or Dataproc for each.
3. Draw an ephemeral-cluster workflow.

**Hands-on exercise — `experiments/07_dataproc/`**

1. Run a PySpark ETL on an ephemeral cluster (GCS in, BigQuery out); delete
   the cluster at the end.
2. Run the same job on Dataproc Serverless; compare startup time and cost.
3. Use Spot secondary workers and observe behaviour on preemption.
4. Wrap the run in a workflow template.

**Checkpoint:**

- [ ] Run Spark jobs on clusters and serverless batches.
- [ ] Use ephemeral clusters correctly.
- [ ] Read and write BigQuery from Spark.
- [ ] Choose among Dataproc, Dataflow, and BigQuery.

**Common mistakes:** long-lived idle clusters; storing data in HDFS on
the cluster; Spark for work BigQuery SQL does cheaper.

---

## 9. Phase D — Orchestration (Intermediate)

### Topic 08 — [Cloud Composer and Workflows](08-cloud-composer-and-workflows.md)

**Why here:** pipelines need scheduling, dependencies, retries, and
visibility. Composer (managed Airflow) is the standard; Workflows is the
lightweight alternative.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Cloud Composer**: managed Airflow; environments, the DAGs bucket, and the Airflow UI |
| Basics | Google provider operators: `BigQueryInsertJobOperator`, `GCSToBigQueryOperator`, `DataprocSubmitJobOperator`, `DataflowTemplatedJobStartOperator` |
| Basics | Connections and service accounts instead of key files |
| Intermediate | Environment sizing, Composer 2/3 autoscaling, and cost (environments run continuously) |
| Intermediate | Deferrable operators and sensors for long GCP jobs; idempotent, templated tasks (`{{ ds }}`) |
| Intermediate | Dependency management (PyPI packages), environment variables, and Secret Manager integration |
| Intermediate | **Workflows**: YAML/JSON orchestration of GCP APIs and HTTP calls; **Cloud Scheduler** and **Eventarc** triggers |
| Advanced | Choosing Composer vs Workflows vs Cloud Scheduler + Cloud Run Jobs vs Dagster/Prefect |
| Advanced | CI/CD for DAGs: tests, linting, deployment to the bucket, and environment promotion (Module 2.18) |
| Advanced | Monitoring and alerting with Cloud Monitoring; SLAs and failure callbacks (Module 2.13) |
| Advanced | Cost and operations: private IP environments, upgrades, and scaling workers |

**How to learn it**

1. Read the topic file.
2. Convert your batch pipeline (load → transform → quality check →
   notify) into a DAG outline.
3. Decide which parts belong in Workflows instead.

**Hands-on exercise — `experiments/08_composer/`**

1. Deploy a small Composer environment with Terraform.
2. Write a DAG: GCS sensor → load to BigQuery → run a transform query →
   data-quality check → alert on failure.
3. Test the DAG locally with `pytest` (import and structure tests).
4. Re-implement a simple chain in Workflows and compare effort and cost.
5. Delete the environment when finished.

**Checkpoint:**

- [ ] Build and deploy a DAG with Google operators.
- [ ] Use connections and secrets safely.
- [ ] Choose among Composer, Workflows, and Scheduler.
- [ ] Estimate Composer cost.

**Common mistakes:** leaving Composer running idle; heavy compute inside
Airflow workers; hard-coded credentials; non-idempotent tasks.

---

## 10. Phase E — Governance (Advanced)

### Topic 09 — [Dataplex, IAM, and governance](09-dataplex-iam-and-governance.md)

**Why it comes last:** governance spans every service above and mirrors
Lake Formation (Stage 2B) and Unity Catalog (Databricks).

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | IAM at project, dataset, table, and column level; predefined vs custom roles; service-account hygiene |
| Basics | BigQuery access: dataset ACLs, authorised views/datasets/routines |
| Basics | Audit logs (Admin Activity, Data Access) and how to query them in BigQuery |
| Intermediate | **Column-level security** with policy tags and **dynamic data masking**; **row-level security** with row access policies |
| Intermediate | **Dataplex Universal Catalog**: lakes/zones/assets, automatic discovery, metadata, and search; business glossary |
| Intermediate | **Dataplex data quality**: rules, scans, scores, and alerts (links to Module 2.11) |
| Intermediate | Data profiling and lineage (Data Lineage API; BigQuery, Dataflow, Composer integrations; OpenLineage) |
| Advanced | Data products, domains, and mesh-style governance with Dataplex (links to Module 2C.8) |
| Advanced | VPC Service Controls, CMEK, DLP API for PII discovery and de-identification |
| Advanced | Policy-as-code: Terraform for IAM, tags, and policies; access reviews |
| Advanced | Cross-cloud governance and BigQuery Omni — awareness |
| Advanced | Compliance: retention, deletion, data residency |

**How to learn it**

1. Read the topic file.
2. Design access for analysts, engineers, and a finance team with PII.
3. Map each control to Lake Formation or Unity Catalog equivalents.

**Hands-on exercise — `experiments/09_governance/`**

1. Create a policy-tag taxonomy; apply it to PII columns; verify masked
   and denied access for two identities.
2. Add a row access policy by region.
3. Publish an authorised view to expose a subset across projects.
4. Create a Dataplex data quality scan with three rules and view results.
5. Run a DLP inspection on a table and report findings.

**Checkpoint:**

- [ ] Design least-privilege access across datasets.
- [ ] Apply column and row-level security.
- [ ] Set up catalog, quality scans, and lineage.
- [ ] Explain VPC-SC and CMEK at a high level.

**Common mistakes:** project-level Editor roles for analysts; masking
without testing; governance scripted by hand and not in Terraform.

---

## 11. Module mini-project — a serverless GCP data platform

**Goal:** build a small, governed platform with batch and streaming paths
into BigQuery.

**Requirements**

1. **Batch:** daily files land in GCS → load to BigQuery → transformed by
   Dataform or scheduled queries into curated tables.
2. **Streaming:** events to Pub/Sub → Dataflow (Beam) with dead-letter →
   partitioned, clustered BigQuery tables.
3. **Spark:** one Dataproc Serverless job for a heavy enrichment step.
4. **Orchestration:** a Composer DAG running the batch path with quality
   gates.
5. **Governance:** policy tags, row access, a Dataplex quality scan, and
   lineage.
6. **Cost:** dry-run guardrails, `maximum_bytes_billed`, a budget alert,
   and a report of top queries.
7. All infrastructure in Terraform; a README with an architecture diagram.

**Done when** the platform runs from scratch with one command, bad data is
quarantined, PII is masked for analysts, and the bill is explained.

---

## 12. Module self-assessment — exit criteria

You have completed this module when you can do all of the following
**without notes**:

- [ ] Map GCP data services and choose among them.
- [ ] Explain BigQuery's architecture and slots.
- [ ] Partition, cluster, and control query cost.
- [ ] Load batch and streaming data idempotently.
- [ ] Use scheduled queries, routines, and BQML.
- [ ] Build and monitor a Beam pipeline on Dataflow.
- [ ] Run Spark on Dataproc and Dataproc Serverless.
- [ ] Orchestrate with Composer.
- [ ] Secure and govern data with IAM, policy tags, and Dataplex.

---

## 13. Recommended reading and references

- Google Cloud documentation: BigQuery, Pub/Sub, Dataflow, Dataproc,
  Composer, Dataplex.
- *Google BigQuery: The Definitive Guide* — Lakshmanan and Tigani.
- Apache Beam Programming Guide.
- The Dremel paper and Google Cloud Architecture Center data analytics
  blueprints.
- Professional Data Engineer exam guide (as a study outline).

---

## 14. Where this module leads

- **Module 2C.5** covers the Azure equivalents.
- **Module 2C.6** (dbt) works on BigQuery as well as Snowflake.
- **Module 2C.8** covers platform architecture and vendor selection across
  clouds.
- **Module 2C.10** continues BQML/Vertex AI into ML handoff.
