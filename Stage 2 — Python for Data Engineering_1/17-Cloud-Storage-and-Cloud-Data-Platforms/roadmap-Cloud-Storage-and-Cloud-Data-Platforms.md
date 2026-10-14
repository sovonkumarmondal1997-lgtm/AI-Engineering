# Roadmap — Module 2.17: Cloud Storage and Cloud Data Platforms

This is the learning roadmap for the seventeenth module of Stage 2,
**Python for Data Engineering**. It tells you **what** to learn about cloud
storage and cloud data platforms, **in what order**, **how** to learn each
topic, and **how to prove to yourself** that you have learned it before you
move on.

Everything you have built so far ran on your laptop: MinIO standing in for
S3, PostgreSQL in Docker standing in for a warehouse, a Docker Spark
cluster standing in for a managed one. That was deliberate — the concepts
are the same everywhere. But real data platforms run in the cloud, and the
cloud adds three things your laptop never taught you: **identity and
permissions** (who may touch what), **managed services** (warehouses,
serverless functions, managed Spark) with their own trade-offs, and
**money** (every byte stored, scanned, moved, and every second of compute
has a price).

This module teaches the cloud from a data engineer's point of view: object
storage in depth, Python access to it, secure identity for pipelines, the
three major cloud warehouses, fast loading, serverless processing, managed
Spark, and storage cost control. **AWS is used as the primary example**,
with equivalent services on Google Cloud and Azure mapped throughout,
because the skills transfer across providers.

---

## 1. Module outcome

By the end of this module you will be able to:

- Explain object storage (S3, GCS, ADLS) — buckets, keys, prefixes,
  consistency, versioning, encryption, request costs — and how it differs
  from a filesystem.
- Use **boto3** for every common S3 operation efficiently and safely,
  including multipart transfers, pagination, retries, and presigned URLs.
- Write **cloud-agnostic** file code with **fsspec** that works on S3, GCS,
  ADLS, and local disk — and plugs into pandas, Polars, PyArrow, and
  DuckDB.
- Design **IAM** for pipelines: roles instead of keys, temporary
  credentials, workload identity federation, and least-privilege policies.
- Compare **Snowflake, BigQuery, and Redshift** — architecture, pricing,
  performance features — and choose between them.
- Load and extract data to and from warehouses from Python with the
  **fastest, cheapest** patterns.
- Build **serverless** data processing with functions, event triggers, and
  serverless query engines — and know their limits.
- Run Spark on **Databricks, EMR, and Dataproc**, control its cost, and
  deploy jobs to it.
- Reduce storage cost with **storage classes and lifecycle policies**
  without breaking tables or compliance.

---

## 2. Prerequisites

This module builds on earlier stages and Modules 2.1–2.16. It does **not**
re-teach them.

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Networking, environment variables, command line | Stage 0 | Cloud CLIs, endpoints, and credentials |
| Secrets and local security hygiene | Stage 0 — Developer Environment | Never putting cloud keys in code or Git |
| HTTP, retries, rate limits, pagination | Stage 2 — Module 2.9 | Cloud APIs are HTTP APIs with the same rules |
| Warehouse vs lake vs lakehouse | Stage 2 — Module 2.1 | Now built on real cloud services |
| Arrow, DuckDB, Polars over object storage (MinIO) | Stage 2 — Module 2.4 | The same code, now against real clouds |
| Parquet layout, partitioning, small files, compression | Stage 2 — Module 2.5 | Decides query cost in cloud warehouses and engines; **not** re-taught |
| SQL, `MERGE`, indexes vs zone maps | Stage 2 — Module 2.6 | Warehouse SQL dialects build on it |
| DB-API, SQLAlchemy, `COPY`, streaming extraction | Stage 2 — Module 2.7 | Warehouse connectors follow the same patterns |
| Dimensional models | Stage 2 — Module 2.8 | Physical design in warehouses |
| Concurrency | Stage 2 — Module 2.10 | Parallel transfers and serverless fan-out |
| dbt and pipeline patterns | Stage 2 — Module 2.12 | Running transformations in warehouses |
| Orchestration | Stage 2 — Module 2.13 | Submitting cloud jobs from Airflow or Dagster |
| Spark, tuning, and the Spark UI | Stage 2 — Module 2.14 | Managed Spark is still Spark |
| Table formats and catalogs | Stage 2 — Module 2.15 | Lakehouse tables on real cloud storage and catalogs |
| Kafka and streaming | Stage 2 — Module 2.16 | Managed streaming services are mapped here |

**Tools and accounts needed:**

- A cloud account on at least one provider (AWS recommended to follow the
  examples), plus free or trial access where available for a warehouse
  (for example a BigQuery sandbox, a Snowflake trial, or a free Databricks
  edition). Check current free-tier and trial terms before starting.
- **Before creating anything: set a budget with email alerts, enable
  multi-factor authentication on the root/owner account, and never use the
  root account for work.**
- Cloud CLIs (`aws`, and optionally `gcloud` / `az`) authenticated with
  short-lived credentials (single sign-on or role assumption), not
  long-lived access keys where avoidable.
- Python 3.12+ in a `uv` project: `uv add boto3 s3fs gcsfs adlfs fsspec
  universal-pathlib pyarrow polars pandas duckdb snowflake-connector-python
  google-cloud-bigquery redshift-connector moto pytest` (install only what
  your chosen providers need).
- **Local stand-ins** for most experiments: MinIO (S3 API), `moto` (mocked
  AWS APIs in tests), and optionally a local AWS emulator.
- A **teardown script** for every exercise — resources left running are the
  most common source of surprise bills.

**A note on change:** cloud services, names, limits, and prices change
often. Treat every number in this roadmap as an example; always confirm
limits and pricing in the provider's current documentation and pricing
pages. Infrastructure as code (Terraform) comes in Module 2.18; in this
module use the CLI and SDKs, and record every resource you create.

---

## 3. How the module is organised

The nine topics are grouped into five phases. Work through them **in
order**.

```text
Phase A — Object Storage from Python                 (Basics → Intermediate)
  01 Object storage: S3, GCS, and ADLS
  02 boto3 and S3 operations
  03 fsspec and cloud-agnostic file access

Phase B — Identity and Access                        (Intermediate → Advanced)
  04 IAM roles and least privilege for pipelines

Phase C — Cloud Warehouses                           (Intermediate → Advanced)
  05 Cloud warehouses: Snowflake, BigQuery, and Redshift
  06 Python warehouse connectors and bulk loads

Phase D — Cloud Compute for Data                     (Intermediate → Advanced)
  07 Serverless data processing
  08 Managed Spark: Databricks, EMR, and Dataproc

Phase E — Cost Control                               (Advanced)
  09 Storage classes and lifecycle policies

Consolidate
  practice-questions.md
  Module mini-project: the orders platform, cloud-native
```

The dependency chain:

```text
01 ──► 02 ──► 03 ──► 04 ──► 05 ──► 06 ──► 07 ──► 08 ──► 09
where   AWS SDK portable who may  which    load    event-   big      pay
data    access  access   access   warehouse fast   driven   compute  less
lives                    what                      compute           to keep it
```

Why this order:

- Object storage (01) is the foundation of every cloud data platform; you
  access it natively (02) before abstracting it (03).
- Identity (04) comes before warehouses and compute because every service
  after it needs roles and permissions — and security is much harder to
  add later.
- You understand warehouses (05) before loading them efficiently (06).
- Serverless (07) is the smallest unit of cloud compute; managed Spark (08)
  the largest.
- Storage cost control (09) comes last because it requires knowing how
  every other service reads and writes your data.

---

## 4. Suggested schedule

About **5 weeks at 8–10 hours per week**.

| Week | Work |
| --- | --- |
| 1 | Account safety set-up · Topic 01 — object storage · Topic 02 — boto3 |
| 2 | Topic 03 — fsspec · Topic 04 — IAM and least privilege |
| 3 | Topic 05 — cloud warehouses · Topic 06 — connectors and bulk loads |
| 4 | Topic 07 — serverless · Topic 08 — managed Spark |
| 5 | Topic 09 — storage classes and lifecycle · practice questions · mini-project · full teardown |

---

## 5. How to study every topic (the cloud loop)

```text
Read → Map the service across clouds → Estimate the cost → Build it locally
→ Build it in the cloud with least privilege → Break it (permissions,
throttling, failures) → Measure time and cost → Tear it down
→ Write it down → Explain aloud
```

1. **Read** the topic file once, fully.
2. **Map the service** to its equivalents on AWS, Google Cloud, and Azure
   in a table you keep throughout the module.
3. **Estimate the cost** of your exercise before running it (storage,
   requests, scans, compute seconds, data transfer).
4. **Build it locally first** with MinIO, `moto`, DuckDB, or Docker Spark
   whenever possible.
5. **Build it in the cloud** with a dedicated role that has only the
   permissions the exercise needs.
6. **Break it**: remove a permission, throttle requests, kill a job, send a
   duplicate event.
7. **Measure** time, bytes, and the actual cost (billing console or cost
   tags) and compare with your estimate.
8. **Tear it down** with your script and verify nothing billable remains.
9. **Write down** what you learned in `module-2.17-notes.md`.
10. **Explain aloud** who can access what, and what the exercise cost and
    why.

Keep one `cloud_lab/` project:

```text
cloud_lab/
├── docs/
│   ├── service-map.md       # AWS ↔ GCP ↔ Azure equivalents
│   ├── resources.md         # every resource created, with teardown status
│   └── cost-log.md          # estimated vs actual cost per exercise
├── policies/                # IAM policy documents (JSON)
├── src/cloud_lab/           # storage, warehouse, serverless, and Spark code
├── scripts/                 # setup and teardown scripts
└── tests/                   # moto/MinIO-based tests
```

---

## 6. Phase A — Object Storage from Python (Basics → Intermediate)

### Topic 01 — [Object storage: S3, GCS, and ADLS](01-object-storage-s3-gcs-and-adls.md)

**Why it comes first:** Object storage is where data lakes, lakehouse
tables, warehouse stages, logs, and backups live. Its behaviour decides
how every tool above it performs and what it costs.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Buckets (containers), objects, keys, and metadata; URIs (`s3://`, `gs://`, `abfss://`) |
| Basics | Objects vs files: no real directories (prefixes and delimiters), whole-object writes, no in-place edits |
| Basics | The three main services: Amazon S3, Google Cloud Storage, Azure Data Lake Storage Gen2 (Blob Storage with a hierarchical namespace) |
| Intermediate | **Consistency**: strong read-after-write consistency on the major providers today, and what that does and does not guarantee (e.g. no multi-object transactions — the reason for table formats in Module 2.15) |
| Intermediate | Hierarchical namespaces (ADLS Gen2) with real directories and atomic renames vs flat namespaces with prefix simulation |
| Intermediate | **Multipart uploads**, ETags and checksums, conditional requests (e.g. only write if the object does not exist) |
| Intermediate | **Versioning**, object lock / immutability (write once, read many), and replication |
| Intermediate | **Encryption**: provider-managed keys vs customer-managed keys (KMS), encryption in transit |
| Advanced | **Performance**: request rate limits per prefix, parallel range reads (how Parquet readers fetch only footers and column chunks), throughput from compute in the same region |
| Advanced | **Pricing model**: storage per GB-month, requests per operation, retrieval fees, and **data transfer (egress)** between regions and out to the internet |
| Advanced | Event notifications on object creation (feeding serverless processing in Topic 07) |
| Advanced | S3-compatible storage (MinIO and others) and low-latency storage classes for specific workloads — awareness |

**How to learn it**

1. Read the topic file.
2. Build a service-map table for storage concepts across AWS, Google
   Cloud, and Azure.
3. Estimate the monthly cost of a 10 TB lake with 50 million objects and 20
   million GET requests per day in one region, then with cross-region
   reads.

**Hands-on exercise — `experiments/01_object_storage/`**

1. Create a bucket (in your cloud account and in MinIO) with versioning and
   default encryption enabled and public access blocked.
2. Upload, overwrite, and delete objects; recover a deleted object from its
   previous version.
3. Upload a 5 GB file with multipart upload and compare with a single-part
   upload.
4. Read one column of a large Parquet file from S3 with DuckDB and count
   the bytes actually transferred (range requests).
5. Configure an event notification on a prefix (you will consume it in
   Topic 07).
6. Record the cost of the exercise.

**Checkpoint — you are ready to move on when you can:**

- [ ] Explain objects, keys, prefixes, and why there are no real
      directories.
- [ ] Explain consistency guarantees and what object storage cannot do
      atomically.
- [ ] Explain versioning, encryption options, and object lock.
- [ ] Explain the pricing model, including egress.
- [ ] Map S3 concepts to GCS and ADLS.

**Common mistakes:** public buckets; storage and compute in different
regions (slow and expensive); treating prefixes like directories that can
be renamed cheaply; millions of tiny objects (Module 2.5).

---

### Topic 02 — [boto3 and S3 operations](02-boto3-and-s3-operations.md)

**Why here:** boto3 is the AWS SDK for Python. Even when higher-level tools
hide it, you will use it for transfers, listings, metadata, presigned URLs,
and automation — and debug its errors.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Sessions and clients (`boto3.Session`, `session.client("s3")`); the resource API and why most new code uses clients |
| Basics | The **credential chain**: environment, shared config and SSO profiles, assumed roles, instance or container roles — and why code should never contain keys |
| Basics | Core operations: `put_object`, `get_object` (streaming bodies), `head_object`, `copy_object`, `delete_object`, `list_objects_v2` |
| Intermediate | **Paginators** for listings with millions of keys; filtering by prefix and delimiter |
| Intermediate | **Managed transfers**: `upload_file` / `download_file` with `TransferConfig` (multipart thresholds, chunk sizes, concurrency) |
| Intermediate | Batch deletes (`delete_objects`), server-side copies, and object metadata and tags |
| Intermediate | **Errors and retries**: `ClientError` codes (`NoSuchKey`, `AccessDenied`, `SlowDown`), botocore retry modes and configuration, timeouts |
| Intermediate | **Presigned URLs** for temporary, scoped access without sharing credentials |
| Advanced | Thread safety: sharing clients across threads, not sessions; parallel transfers (Module 2.10) |
| Advanced | Conditional writes and ETag checks for safe concurrent updates |
| Advanced | Testing with **moto** (mocked AWS) and MinIO (real S3 API); avoiding real cloud calls in unit tests |
| Advanced | Async access (e.g. aiobotocore-based libraries) and other SDKs: `google-cloud-storage`, `azure-storage-blob` — same ideas, different APIs |

**How to learn it**

1. Read the topic file.
2. Write each core operation against MinIO, then against real S3 with an
   SSO or assumed-role profile.
3. List a bucket with 1 million keys with and without paginators; measure
   time and memory.

**Hands-on exercise — `src/cloud_lab/s3_ops.py`**

1. Build an `S3Store` class with `put`, `get` (streaming), `exists`,
   `list(prefix)` (paginated generator), `copy`, `delete_prefix` (batched),
   and `presign`.
2. Upload 2,000 files in parallel with a shared client and tuned
   `TransferConfig`; measure throughput.
3. Handle `NoSuchKey`, `AccessDenied`, and throttling explicitly, with
   botocore retry configuration.
4. Write an atomic "publish" using a conditional write or a manifest object
   (building on Module 2.5's atomic outputs).
5. Test everything with `moto`, then run an integration test against MinIO.

**Checkpoint:**

- [ ] Use boto3 clients with the credential chain (no keys in code).
- [ ] List, transfer, copy, and delete at scale efficiently.
- [ ] Configure retries and handle common errors.
- [ ] Generate presigned URLs.
- [ ] Test S3 code without touching the cloud.

**Common mistakes:** hard-coded access keys; listing without pagination;
downloading whole objects to read a few bytes; one session shared across
threads; unit tests that call real AWS.

---

### Topic 03 — [fsspec and cloud-agnostic file access](03-fsspec-and-cloud-agnostic-file-access.md)

**Why here:** Most data code should not care whether a file is on S3, GCS,
ADLS, or local disk. fsspec provides one filesystem interface used by
pandas, Polars, PyArrow, Dask, and many other libraries.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **fsspec** filesystems and protocols (`s3`, `gcs`, `abfs`, `file`, `memory`); implementations `s3fs`, `gcsfs`, `adlfs` |
| Basics | `fsspec.open(url)`, `fsspec.url_to_fs(url)`, and filesystem methods (`ls`, `glob`, `exists`, `put`, `get`, `rm`) |
| Basics | Passing credentials and options (`storage_options`) instead of global state |
| Intermediate | Library integration: pandas `read_parquet(..., storage_options=...)`, Polars `scan_parquet`, PyArrow datasets with fsspec or `pyarrow.fs`, DuckDB with its own cloud extensions |
| Intermediate | **Caching layers**: whole-file caches and block caches for repeated reads |
| Intermediate | `universal-pathlib` (`UPath`) for a `pathlib`-style API across storage backends |
| Intermediate | The `memory` filesystem for fast unit tests |
| Advanced | Performance: block sizes, range requests, many small files vs few large ones, listing caches and when they go stale |
| Advanced | Alternatives and complements: PyArrow's native filesystems and newer high-performance object-store libraries — awareness and when they are faster |
| Advanced | Designing storage-agnostic pipeline code: one `storage_url` in configuration (Module 2.12), no provider-specific calls in business logic |

**How to learn it**

1. Read the topic file.
2. Take your Module 2.12 readers and writers and make them work
   unchanged on local disk, MinIO, and real S3 (and GCS or ADLS if
   available) by changing only a URL.
3. Compare read times of the same Parquet dataset via fsspec, PyArrow's
   native filesystem, and DuckDB.

**Hands-on exercise — `src/cloud_lab/storage.py`**

1. Build `read_dataset(url)` and `write_dataset(df, url)` helpers using
   fsspec/PyArrow that accept `file://`, `s3://`, `gs://`, or `abfs://`
   URLs from configuration.
2. Use `UPath` to walk a partitioned dataset on S3 like a local directory.
3. Add a block cache for repeated reads of a remote file and measure the
   speed-up.
4. Unit-test the helpers with the `memory` filesystem; integration-test
   with MinIO.
5. Refactor one earlier pipeline so its only storage-specific input is the
   base URL.

**Checkpoint:**

- [ ] Use fsspec to read and write across storage backends.
- [ ] Pass storage options to pandas, Polars, PyArrow, and DuckDB.
- [ ] Use caching and `UPath` appropriately.
- [ ] Design storage-agnostic pipeline code.

**Common mistakes:** provider-specific code scattered through pipelines;
stale listing caches after writes; credentials in URLs; ignoring
performance differences between access libraries.

---

## 7. Phase B — Identity and Access (Intermediate → Advanced)

### Topic 04 — [IAM roles and least privilege for pipelines](04-iam-roles-and-least-privilege-for-pipelines.md)

**Why here:** In the cloud, **identity is the security perimeter**. A
leaked access key or an over-privileged pipeline role is one of the most
common and damaging data incidents. Every service in the rest of this
module depends on getting this right.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Identities: human users, groups, **roles**, and service identities (service accounts, managed identities) |
| Basics | Policies: identity-based policies, resource-based policies (e.g. bucket policies), and the evaluation logic (explicit deny wins) |
| Basics | **Why roles and temporary credentials beat long-lived access keys** |
| Intermediate | Assuming roles (e.g. AWS STS `AssumeRole`) and short-lived credentials; single sign-on for humans |
| Intermediate | **Workload identity**: roles attached to compute (instance profiles, task/pod roles on containers and Kubernetes, function execution roles) so code never holds keys |
| Intermediate | **Workload identity federation** for CI/CD (e.g. OIDC from GitHub Actions to AWS, GCP, or Azure) — no stored cloud secrets (CI details in Module 2.18) |
| Intermediate | Writing **least-privilege policies**: specific actions, specific resources (bucket and prefix ARNs), and conditions |
| Intermediate | Equivalents across clouds: GCP IAM with service accounts and Workload Identity Federation; Azure RBAC with managed identities |
| Advanced | Separation of duties: separate roles per pipeline and per environment; read-only roles for analysts; break-glass access |
| Advanced | Encryption key permissions (KMS key policies) as a second layer of access control |
| Advanced | Guardrails: permission boundaries and organisation-level policies — awareness |
| Advanced | Auditing and analysis: access logs and audit trails (e.g. CloudTrail), access analysers for unused or public access |
| Advanced | Catalog-level governance and credential vending (Module 2.15) and how it complements IAM |

**How to learn it**

1. Read the topic file.
2. List every pipeline in your platform and the exact storage prefixes,
   services, and actions each needs.
3. Write policies for them, then use the provider's policy simulator (or
   trial and error in a sandbox) to prove what is allowed and denied.

**Hands-on exercise — `policies/` and `experiments/04_iam/`**

1. Create three roles: `ingest-orders` (write only to
   `s3://<lake>/bronze/orders/`), `transform-silver` (read bronze, write
   silver), and `analyst-readonly` (read gold only); write their policies.
2. Run your pipelines using assumed-role credentials only; show an
   `AccessDenied` when a pipeline touches another layer.
3. Encrypt the gold prefix with a customer-managed key and grant decrypt
   only to the analyst and transform roles.
4. Configure OIDC federation from GitHub Actions to a deploy role (or
   document the exact steps if you cannot yet).
5. Find every action in the audit trail performed by your pipelines during
   the exercise.
6. Delete any long-lived access keys you created.

**Checkpoint:**

- [ ] Explain roles, policies, and policy evaluation.
- [ ] Run pipelines with temporary credentials only.
- [ ] Write least-privilege policies scoped to prefixes.
- [ ] Explain workload identity and OIDC federation.
- [ ] Audit who accessed what.

**Common mistakes:** `"Action": "*"` / `"Resource": "*"`; one shared admin
role for every pipeline; access keys in `.env` files that get committed;
forgetting KMS permissions; never reviewing unused permissions.

---

## 8. Phase C — Cloud Warehouses (Intermediate → Advanced)

### Topic 05 — [Cloud warehouses: Snowflake, BigQuery, and Redshift](05-cloud-warehouses-snowflake-bigquery-and-redshift.md)

**Why here:** Cloud warehouses run a large share of analytics. Each has a
different architecture and pricing model, and the same query can cost ten
times more in the wrong design.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What cloud warehouses share: columnar storage, separation of storage and compute, massively parallel processing, SQL, and managed operations |
| Basics | **Snowflake**: virtual warehouses (compute clusters) billed per second of use, databases and schemas, stages |
| Basics | **BigQuery**: serverless; datasets and tables; pricing by bytes scanned (on-demand) or by reserved capacity (slots) |
| Basics | **Redshift**: provisioned clusters and a serverless option; tables stored in managed storage |
| Intermediate | Performance features: Snowflake micro-partitions and clustering keys; BigQuery partitioning and clustering; Redshift distribution styles and sort keys — and how each relates to Parquet layout ideas from Module 2.5 |
| Intermediate | **Cost models** in depth: what you pay for (compute time, bytes scanned, storage, data transfer); auto-suspend, query limits, and budgets |
| Intermediate | Loading paths: stages and `COPY INTO` (Snowflake), load jobs and the Storage Write API (BigQuery), `COPY` from S3 (Redshift) |
| Intermediate | Useful platform features: time travel and zero-copy cloning (Snowflake), materialised views, result caching, and query history for cost analysis |
| Advanced | Lakehouse integration: querying Iceberg tables and external data in object storage from each warehouse (Module 2.15) |
| Advanced | Continuous and in-warehouse processing: e.g. Snowflake Snowpipe, streams, tasks, and dynamic tables; BigQuery scheduled queries — awareness |
| Advanced | Running dbt on each warehouse (Module 2.12) and dialect differences |
| Advanced | Other platforms: Databricks SQL, Azure's analytics services, and managed Postgres-compatible analytics — awareness |
| Advanced | **Choosing a warehouse**: workload shape (steady vs spiky), team skills, existing cloud, lakehouse strategy, governance, and cost predictability |

**How to learn it**

1. Read the topic file.
2. Build a comparison table (architecture, pricing, scaling, performance
   features, loading, lakehouse support) for the three warehouses.
3. Load the same gold dataset into at least one warehouse (two if you
   can) and run the same ten queries; record time and cost per query.

**Hands-on exercise — `experiments/05_warehouses/`**

1. Load your orders star schema (Module 2.8) into your chosen warehouse
   from Parquet in object storage.
2. Run ten analytical queries; record bytes scanned, duration, and cost
   from the warehouse's query history.
3. Apply partitioning/clustering (or sort/distribution keys) and repeat;
   quantify the saving.
4. Show one expensive anti-pattern (e.g. `SELECT *` on a huge BigQuery
   table, or an always-on Snowflake warehouse) and its fix.
5. Configure cost controls: auto-suspend, query byte limits, or budget
   alerts.
6. Write a warehouse recommendation for a fictional company.

**Checkpoint:**

- [ ] Explain the architecture and pricing of Snowflake, BigQuery, and
      Redshift.
- [ ] Use each platform's layout features to reduce cost.
- [ ] Read query history to find expensive queries.
- [ ] Recommend a warehouse for a scenario.

**Common mistakes:** `SELECT *` on scan-priced warehouses; compute left
running; no partitioning on large time-series tables; copying on-premises
indexing habits into columnar warehouses.

---

### Topic 06 — [Python warehouse connectors and bulk loads](06-python-warehouse-connectors-and-bulk-loads.md)

**Why here:** Pipelines load data into warehouses and pull results out.
Row-by-row inserts that were slow in PostgreSQL (Module 2.7) are
catastrophically slow and expensive in cloud warehouses.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Python connectors: `snowflake-connector-python`, `google-cloud-bigquery`, `redshift_connector` (and PostgreSQL drivers); DB-API patterns from Module 2.7 |
| Basics | Authentication without passwords where possible: key-pair auth (Snowflake), application default credentials and service accounts (BigQuery), IAM-based auth (Redshift) |
| Basics | Parameterised queries and query labels/tags for cost attribution |
| Intermediate | **The bulk-load pattern**: write Parquet to object storage → load with `COPY INTO` / load jobs / `COPY` → merge from a staging table (Modules 2.6 and 2.12) |
| Intermediate | Library helpers: loading DataFrames (e.g. Snowflake's pandas write helpers, BigQuery's DataFrame and URI loads), and when helpers stage files for you |
| Intermediate | **Fast extraction**: Arrow-based result fetching (e.g. Snowflake's Arrow/pandas fetches, the BigQuery Storage Read API) instead of row-by-row fetching; unloading large results to object storage |
| Intermediate | Load options and errors: file formats, schema matching, error thresholds, and rejected-row handling (quarantine from Module 2.11) |
| Advanced | Arrow-native connectivity with **ADBC** drivers for warehouses (Module 2.4) |
| Advanced | Streaming or micro-batch ingestion options (e.g. Snowpipe, BigQuery Storage Write API) vs batch loads — cost and latency |
| Advanced | Idempotent loads: load ids, staging tables per run, `MERGE`, and never double-loading a file (file registries from Module 2.9) |
| Advanced | Higher-level tools: SQLAlchemy dialects, dlt destinations (Module 2.9), AWS SDK for pandas — awareness |
| Advanced | Cost awareness in code: dry runs and byte estimates (BigQuery), warehouse sizes and auto-suspend (Snowflake), and query tagging |

**How to learn it**

1. Read the topic file.
2. Load 10 million rows into your warehouse three ways — row inserts in
   batches, a DataFrame helper, and stage-then-`COPY` — and record time
   and cost.
3. Extract 10 million rows with regular fetching and Arrow-based fetching.

**Hands-on exercise — `src/cloud_lab/warehouse_loader.py`**

1. Build `load_parquet_to_warehouse(uri, table, keys)`: `COPY`/load into a
   run-specific staging table, validate with Module 2.11 checks, `MERGE`
   into the target, and drop staging — idempotently.
2. Build `extract_query_to_parquet(sql, uri)` using Arrow-based fetching or
   an unload, with bounded memory.
3. Authenticate with key pairs, service accounts, or IAM — no passwords in
   code or config.
4. Tag every query with the pipeline name and run id; produce a cost report
   per pipeline from the query history.
5. Load the same file twice and prove no duplicates; load a file with bad
   rows and quarantine them.

**Checkpoint:**

- [ ] Use Python connectors with secure authentication.
- [ ] Implement stage → load → merge bulk loads.
- [ ] Extract large results with Arrow or unloads.
- [ ] Make warehouse loads idempotent and cost-attributed.

**Common mistakes:** `INSERT` loops into warehouses; fetching millions of
rows through slow row fetches; passwords in connection strings; untagged
queries that make cost impossible to attribute.

---

## 9. Phase D — Cloud Compute for Data (Intermediate → Advanced)

### Topic 07 — [Serverless data processing](07-serverless-data-processing.md)

**Why here:** Many data tasks are small, event-driven, or spiky: process a
file when it lands, call an API every 15 minutes, run a query on demand.
Serverless compute runs them without servers — and without paying when
idle.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Serverless functions: AWS Lambda, Google Cloud Run functions / Cloud Run jobs, Azure Functions — code that runs on events, billed per invocation and duration |
| Basics | Triggers: object-storage events, schedules (e.g. EventBridge Scheduler / Cloud Scheduler), queues and streams, HTTP |
| Basics | Packaging Python: dependency layers, container images, and keeping cold starts small |
| Intermediate | **Limits** that shape designs: maximum run time, memory and CPU, temporary disk, payload sizes, and concurrency limits |
| Intermediate | **Event-driven file processing**: an object lands → a function validates and converts it (e.g. with DuckDB or Polars) → writes Parquet to bronze/silver |
| Intermediate | **Idempotency**: events can be delivered more than once or out of order — deduplicate by object key and version (Module 2.9 file registries) |
| Intermediate | Serverless query engines: Amazon Athena and BigQuery (pay per data scanned) over lake data; serverless Spark options (Topic 08) |
| Advanced | Orchestrating serverless steps: state machines (e.g. AWS Step Functions, Google Workflows) vs orchestrators like Airflow (Module 2.13) |
| Advanced | Fan-out and backpressure: thousands of concurrent functions overwhelming a database or API — reserved concurrency, queues, and batching (Modules 2.10 and 2.16) |
| Advanced | Failure handling: retries, dead-letter queues, and partial batch failures |
| Advanced | Observability: structured logs, metrics, and tracing for functions (Module 2.20) |
| Advanced | When serverless is the wrong choice: long-running, heavy, or steady workloads where containers or clusters are cheaper |

**How to learn it**

1. Read the topic file.
2. Sketch three event-driven designs from your platform (partner file
   arrives, API poll every 15 minutes, nightly compaction) and decide
   serverless function, serverless query engine, container job, or Spark.
3. Estimate the monthly cost of each design.

**Hands-on exercise — `serverless/`**

1. Build a function triggered when a CSV lands in `landing/`: validate it
   (Pydantic/Pandera from Module 2.11), convert it to Parquet with DuckDB or
   Polars, write to `bronze/`, and record the file in a registry table.
2. Make it idempotent under duplicate events and test by sending the same
   event twice.
3. Send malformed files and route failures to a dead-letter queue.
4. Upload 1,000 files at once; observe concurrency and protect a database
   sink with reserved concurrency or a queue.
5. Query bronze with a serverless query engine (e.g. Athena over Iceberg
   or Parquet) and compare its per-query cost with your warehouse.
6. Tear everything down.

**Checkpoint:**

- [ ] Build event-driven functions with storage triggers and schedules.
- [ ] Design around serverless limits.
- [ ] Make functions idempotent and handle failures with dead-letter
      queues.
- [ ] Choose between functions, serverless SQL, containers, and clusters.

**Common mistakes:** functions that time out on large files; unbounded
fan-out overwhelming downstream systems; assuming each event arrives
exactly once; huge deployment packages causing slow cold starts.

---

### Topic 08 — [Managed Spark: Databricks, EMR, and Dataproc](08-managed-spark-databricks-emr-and-dataproc.md)

**Why here:** Your Docker Spark cluster from Module 2.14 was for learning.
In production, Spark runs on managed platforms that provision clusters,
integrate storage and catalogs, and bill by the second — and can become
the biggest line in the data budget.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Managed Spark options: **Databricks** (on all major clouds), **Amazon EMR** (on EC2, on EKS, and serverless), **Google Dataproc** (clusters and serverless), and cloud-native serverless Spark/ETL services (e.g. AWS Glue) |
| Basics | Clusters vs serverless Spark; job clusters (created per job) vs long-running interactive clusters |
| Basics | Submitting PySpark jobs: packaged code, entry points, arguments (the run context from Module 2.12) |
| Intermediate | **Databricks** essentials: workspaces, compute, jobs, notebooks vs Git-based projects, Unity Catalog (Module 2.15), Delta Lake, and its declarative pipeline and bundle-based deployment tooling (awareness) |
| Intermediate | **EMR** and **Dataproc** essentials: cluster configuration, steps/jobs, serverless applications, and integration with each cloud's catalog and storage |
| Intermediate | Dependencies: Python packages, JARs, and container images on managed platforms |
| Intermediate | Accessing the Spark UI and logs for managed jobs (Module 2.14 debugging skills) |
| Advanced | **Cost control**: right-sizing, autoscaling, spot/preemptible workers, auto-termination, job vs all-purpose compute pricing, and cost tags |
| Advanced | Orchestrating managed Spark from Airflow or Dagster (provider operators and integrations — Module 2.13) |
| Advanced | Security: job roles with least privilege (Topic 04), network isolation, and secrets |
| Advanced | Choosing a platform: managed Spark vs warehouse SQL vs single-node engines on containers (Module 2.4) for a given workload |

**How to learn it**

1. Read the topic file.
2. Run your Module 2.14 Spark job unchanged (except configuration) on at
   least one managed platform (a free or trial edition is fine).
3. Compare run time and cost with job compute, autoscaling, and spot
   workers.

**Hands-on exercise — `managed_spark/`**

1. Package your Spark pipeline and submit it as a job on your chosen
   platform (e.g. Databricks job, EMR Serverless application, or Dataproc
   Serverless batch), reading and writing Iceberg or Delta tables in cloud
   storage.
2. Run it with a least-privilege job role; show access denied outside its
   prefixes.
3. Compare three compute configurations for cost and time; tag every run.
4. Trigger the job from an Airflow DAG (Module 2.13) with the data interval
   as an argument.
5. Diagnose one deliberately slow run using the platform's Spark UI and
   logs.
6. Tear down clusters and applications.

**Checkpoint:**

- [ ] Explain the managed Spark options and their trade-offs.
- [ ] Deploy and run PySpark jobs on a managed platform.
- [ ] Control cost with job compute, autoscaling, spot, and
      auto-termination.
- [ ] Orchestrate and secure managed Spark jobs.

**Common mistakes:** interactive clusters running all weekend; running
production jobs from notebooks; over-sized clusters for small data; no cost
tags, so nobody knows which pipeline spends what.

---

## 10. Phase E — Cost Control (Advanced)

### Topic 09 — [Storage classes and lifecycle policies](09-storage-classes-and-lifecycle-policies.md)

**Why last:** Data only grows. Storage classes and lifecycle policies are
the simplest large cost saving in most data platforms — if applied with an
understanding of how every tool in this module reads and writes data.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Storage classes by access frequency: frequent access (standard), infrequent access, archive tiers, and automatic tiering — on S3, GCS, and Azure |
| Basics | Trade-offs: cheaper storage vs retrieval fees, retrieval delays for deep archives, and **minimum storage durations** |
| Basics | **Lifecycle policies**: transition objects to cheaper classes after N days; expire objects; clean up old versions |
| Intermediate | Housekeeping rules: aborting incomplete multipart uploads, expiring noncurrent versions, deleting temporary and staging prefixes |
| Intermediate | Designing prefixes for lifecycle rules: separating landing, bronze, silver, gold, temp, and logs so rules can target them |
| Intermediate | **Per-object charges**: small objects in infrequent-access classes can cost more than they save (minimum billable object sizes, per-request fees) — another reason to avoid small files |
| Advanced | **Lifecycle and table formats**: never transitioning or expiring files that live table snapshots reference; rely on vacuum and snapshot expiry (Module 2.15) for table data, and lifecycle rules for raw landing data and logs |
| Advanced | Compliance: retention requirements, object lock, legal holds, and deletion deadlines (links to GDPR deletes in Module 2.15 and governance in Module 2.20) |
| Advanced | Analysing storage: inventory reports and storage analytics to find what is large, old, and unused |
| Advanced | A **storage cost model** for a lake: growth rate, tiering schedule, retrieval patterns, and projected savings |
| Advanced | Other cost levers: compression (Module 2.5), deleting duplicates, and avoiding cross-region transfer |

**How to learn it**

1. Read the topic file.
2. Build a cost model for your lake: 1 TB per month growth, 3 years of
   history, typical access patterns per layer; compare "everything standard"
   with a tiered plan.
3. Inspect an inventory report (or a full listing) of your lab bucket and
   classify objects by prefix, age, and size.

**Hands-on exercise — `policies/lifecycle/` and `src/cloud_lab/storage_report.py`**

1. Write lifecycle rules for your lab bucket: landing files to infrequent
   access after 30 days and archive after 180; delete `tmp/` after 7 days;
   expire noncurrent versions after 30 days; abort incomplete multipart
   uploads after 7 days.
2. Exclude table-format data prefixes from transitions and document why.
3. Build a storage report from a listing or inventory: size and object
   count by prefix, class, and age; small-object counts.
4. Calculate projected monthly savings, including retrieval and per-object
   costs.
5. Apply the rules (to a test bucket first) and verify them after the
   provider applies them.

**Checkpoint:**

- [ ] Compare storage classes, including minimum durations and retrieval
      costs.
- [ ] Write lifecycle rules for transitions, expiry, versions, and
      multipart cleanup.
- [ ] Explain why lifecycle rules must not touch live table files.
- [ ] Model and verify storage savings.

**Common mistakes:** archiving data that is still queried; lifecycle
expiry deleting files a Delta or Iceberg table still references; tiering
millions of tiny files; forgetting noncurrent versions keep costing money.

---

## 11. Consolidate — practice questions

When all nine topics are done, open
[`practice-questions.md`](practice-questions.md). For every question:

1. Map the design to services on AWS, and name the Google Cloud and Azure
   equivalents.
2. Define the identities and least-privilege permissions involved.
3. Estimate the monthly cost (storage, requests, compute, scans, transfer).
4. Implement it locally first where possible, then in the cloud.
5. Measure time and actual cost, and compare with your estimate.
6. Tear it down and confirm nothing billable remains.

---

## 12. Module mini-project — the orders platform, cloud-native

This is the proof that you have finished the module.

**Scenario:** Your company is moving the orders platform (Modules 2.9–2.16)
from on-premises servers to the cloud. Leadership asks for a secure,
cost-controlled design with a working proof of concept on one provider and
a documented mapping to the other two.

Build `cloud_platform/` on one cloud (AWS recommended) with:

1. **Account safety** — budget alerts, MFA, single sign-on or assumed roles
   for your own access, and no long-lived access keys.
2. **Storage** — a lake bucket with versioning, encryption (with a
   customer-managed key for gold), blocked public access, and prefixes per
   layer and purpose.
3. **Identity** — one least-privilege role per pipeline and an analyst
   read-only role; OIDC federation for CI (or a documented plan).
4. **Ingestion** — an event-driven function converting landed partner files
   to bronze Parquet, idempotent and with a dead-letter queue.
5. **Processing** — the silver/gold Spark job from Module 2.14 on a managed
   Spark platform, reading and writing Iceberg or Delta tables through a
   catalog, with cost tags and auto-termination.
6. **Warehouse** — gold tables loaded into a cloud warehouse with the
   stage → load → merge pattern, Arrow-based extraction for a report, and
   query tagging for cost attribution.
7. **Portable code** — all storage access through fsspec/PyArrow URLs from
   configuration; the same pipeline code runs against MinIO locally.
8. **Cost control** — lifecycle policies for landing, temp, and logs; a
   storage report; a monthly cost estimate compared with the actual bill of
   your proof of concept.
9. **Documentation** — architecture diagram, service mapping to the other
   two clouds, IAM matrix (role → resources → actions), runbook, and a
   **teardown script** that removes everything.

**Grading yourself:** no credential exists in code, config, or Git; every
pipeline is denied access outside its prefixes; re-delivered events and
re-run loads create no duplicates; the proof of concept stays within its
budget; and the teardown script leaves nothing billable behind.

---

## 13. Module self-assessment — exit criteria

Only move to Module 2.18 when you can tick every box without looking at your
notes:

- [ ] I can explain object storage behaviour and pricing on S3, GCS, and
      ADLS.
- [ ] I can use boto3 efficiently, safely, and testably.
- [ ] I can write storage-agnostic data code with fsspec.
- [ ] I can design least-privilege IAM with roles and temporary
      credentials, and no long-lived keys.
- [ ] I can compare Snowflake, BigQuery, and Redshift and reduce their
      costs.
- [ ] I can load and extract warehouse data with bulk and Arrow-based
      patterns.
- [ ] I can build idempotent, event-driven serverless processing.
- [ ] I can run, orchestrate, and cost-control managed Spark jobs.
- [ ] I can apply storage classes and lifecycle policies safely.
- [ ] I have finished all practice questions and the mini-project, and
      torn everything down.

---

## 14. Recommended reading and references

| Resource | Relevant topics |
| --- | --- |
| Amazon S3 User Guide (consistency, performance guidelines, storage classes, lifecycle, security best practices); Google Cloud Storage and Azure Data Lake Storage Gen2 documentation | 01, 09 |
| boto3 documentation (S3 client, paginators, transfer configuration, credentials) and `moto` documentation | 02 |
| fsspec, s3fs, gcsfs, adlfs, and universal-pathlib documentation | 03 |
| AWS IAM User Guide (policies, roles, security best practices); Google Cloud IAM and Workload Identity Federation; Azure RBAC and managed identities | 04 |
| Snowflake, BigQuery, and Redshift documentation — architecture, loading data, performance, cost optimisation | 05, 06 |
| Snowflake Python connector, BigQuery Python client and Storage Read API, Redshift Python connector documentation | 06 |
| AWS Lambda, Step Functions, and Athena; Google Cloud Run; Azure Functions documentation | 07 |
| Databricks, Amazon EMR, and Google Dataproc documentation (jobs, serverless, cost management) | 08 |
| Cloud provider well-architected guidance for data analytics and cost optimisation | All topics |
| *Fundamentals of Data Engineering* — Joe Reis and Matt Housley, chapters on storage and cloud economics | 01, 05, 09 |

---

## 15. Where this module leads

| This module's idea | Where it goes deeper |
| --- | --- |
| Creating every resource in this module as code (Terraform), container images, Kubernetes, secrets managers, OIDC in CI | 2.18 Containers, Infrastructure, and CI/CD for Data |
| Testing cloud code with mocks, MinIO, and containers | 2.19 Testing Data Pipelines |
| Audit logs, access control, encryption, PII, and data retention | 2.20 Observability, Lineage, Governance, and Security |
| Compute and warehouse cost optimisation; Dask and Ray on cloud compute | 2.21 Performance, Scaling, and Cost Optimization |
| Serving warehouse and lakehouse data to BI, ML, and AI applications | 2.22 Serving Data for Analytics, ML, and AI |

The cloud turns infrastructure into an API and a bill. The habits you build
here — roles instead of keys, least privilege by prefix, estimate before
you run, tag everything, load in bulk, keep code storage-agnostic, and tear
down what you do not use — are what make a cloud data platform secure,
portable, and affordable.
